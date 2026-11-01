Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# seL4 微内核拓展型改造方案 → agent-linux 微内核化

> **文档定位**: 闭源内部参考，深度研究 seL4 源码（src/、libsel4/、include/、tools/、manual/），提炼 seL4 四大工程思想与工程标准，制定 agent-linux（AirymaxOS，极境智能体操作系统）基于 seL4 思想 + Linux 6.6 基线的微内核化拓展型改造方案
> **版本**: 0.1.1（文档体系完成）/ 1.0.1（开发）
> **最后更新**: 2026-07-09
> **理论根基**: Linux 6.6 内核基线工程思想 + seL4 微内核设计思想 + Airymax 体系并行论
> **密级**: 闭源内部参考（docs-closed）

---

## 1. 文档说明

### 1.1 目的

本文档不是让 agent-linux 重写一个 seL4，而是把 seL4 的工程思想"叠加"到 Linux 6.6 基线上，形成 agent-linux 自己的微内核化拓展型改造方案。回答四个问题：

1. **seL4 工程思想是什么**：最小化原则、capability 安全、快速 IPC、形式化验证
2. **seL4 工程标准是什么**：CMake 构建、DCO 贡献、SECURITY 漏洞治理、LICENSES 许可证治理
3. **agent-linux 如何叠加 seL4 思想**：通过 sched_ext + eBPF kfunc + io_uring（用户态-内核态）+ kfifo（kthread 间）叠加 seL4 思想
4. **改造路线与风险**：分阶段实施计划与风险评估

> **术语澄清**：agentrt（用户态运行时）= 微核心（micro-core），基于 seL4 微内核思想抽象；agent-linux（OS 发行版）= 微内核（micro-kernel），真正的微内核。本文档严禁使用"微内核原语"描述 agentrt，统一使用"微核心原语"。

### 1.2 seL4 源码定位

| 路径 | 说明 | 规模 |
|------|------|------|
| `src/fastpath/fastpath.c` | 快速 IPC 路径实现 | 31,252 字节 |
| `include/fastpath/fastpath.h` | 快速路径头文件（lookup_fp 等） | 5,484 字节 |
| `src/object/cnode.c` | CNode capability 操作（Mint/Copy/Move/Revoke） | 27,944 字节 |
| `include/object/cap.h` / `structures.h` | capability 类型与结构定义 | — |
| `src/api/syscall.c` | 系统调用入口（handleSyscall） | 21,321 字节 |
| `src/kernel/thread.c` | 线程管理（TCB） | 23,899 字节 |
| `src/kernel/cspace.c` | CSpace 核心 | 5,810 字节 |
| `src/kernel/boot.c` | 内核引导 | 41,275 字节 |
| `libsel4/` | 用户态 API 库（seL4_Call 等） | 大型 |
| `tools/bitfield_gen.py` | 位字段代码生成器 | 123,002 字节 |
| `gcc.cmake` / `llvm.cmake` | GCC / LLVM 工具链配置 | 6,873 / 1,162 字节 |
| `CMakeLists.txt` | 顶层 CMake 构建 | 27,248 字节 |
| `CONTRIBUTING.md` / `SECURITY.md` | 贡献与安全策略 | — |
| `LICENSES/` | 许可证文本（GPL-2.0/BSD/MIT/CC-BY-SA/Apache） | 10 文件 |
| `manual/` | 形式化验证手册（Doxyfile + LaTeX） | 大型 |

### 1.3 IRON-9 v2 代码共享边界

| 标注 | 含义 | 本文档适用 |
|------|------|------------|
| **[SC]** | 共享契约层（agentrt ↔ agent-linux 共享 4 头文件） | Cupolas/AgentsIPC 契约 |
| **[SS]** | 语义同源层（API 签名同源，实现独立） | capability/IPC 语义同源 |
| **[IND]** | 完全独立层 | seL4 思想叠加实现独立 |

**关键声明**：agent-linux 不复制 seL4 源码，而是把 seL4 工程思想（capability 派生、快速 IPC、最小化内核职责、形式化验证目标）叠加到 Linux 6.6 基线（sched_ext + eBPF + io_uring + kfifo）之上，形成 [IND] 独立实现。

---

## 2. seL4 工程思想提炼

### 2.1 Liedtke 最小化原则（Minimality Principle）

**源码体现**: seL4 内核仅 ~10,000–16,000 SLOC，严格遵循 Liedtke 1995 最小化原则：

> "A concept is tolerated inside the microkernel only if moving it outside the kernel would prevent the implementation of the system's required functionality." — Jochen Liedtke

seL4 内核仅提供 4 个原子机制，源码组织精简：

| 机制 | seL4 源码 | 说明 | agent-linux 对应 |
|------|-----------|------|---------------------|
| 线程（TCB） | `src/kernel/thread.c:1` / `include/object/tcb.h:1` | 执行单元 + 调度上下文 | sched_ext 调度类（SCHED_AGENT BPF 策略） |
| 地址空间（VSpace） | `include/object/structures.h` | 页表薄封装 | Linux mm（MemoryRovol） |
| IPC（Endpoint） | `src/object/endpoint.c:1` | 同步消息传递 | AgentsIPC（io_uring + 128B 头） |
| 通知（Notification） | `src/object/notification.c:1` | 二进制信号量 | taskflow 事件（kfifo + wait_event） |

**最小化证据**：seL4 把文件系统、网络、设备驱动、用户态进程管理全部移出内核，由用户态服务承担。`src/kernel/boot.c` 仅做内核初始化，不包含任何策略。

#### 2.1.1 agent-linux 复用方式 [IND]

agent-linux 不重写内核，而是用 Linux 6.6 机制叠加 seL4 最小化思想：

- **内核职责最小化**：通过 sched_ext（BPF 调度策略）+ eBPF kfunc（可编程扩展）把策略移出内核硬编码
- **机制/策略分离**：内核保留机制（调度类、IPC 通道、capability 框架），策略移到用户态（BPF 程序、daemon）
- **[IND] 独立**：不复制 seL4 TCB/Endpoint 源码，用 Linux `task_struct` + io_uring 等价实现

### 2.2 Capability 安全模型

**源码路径**: `seL4: src/object/cnode.c:1-719` / `include/object/cap.h` / `include/object/structures.h`

seL4 capability 是不可伪造的权限令牌，所有内核对象访问都经 capability 校验。`src/object/cnode.c` 实现 5 类核心操作（行号精确引用）：

| 操作 | seL4 函数 | 源码行号 | 语义 | agent-linux Cupolas 对应 |
|------|-----------|----------|------|----------------------------|
| Revoke | `invokeCNodeRevoke()` | `cnode.c:315-318` | 递归撤销所有派生 cap | `airymax_cap_revoke()` |
| Delete | `invokeCNodeDelete()` | `cnode.c:320-323` | 删除单个 cap | `airymax_cap_delete()` |
| Insert | `invokeCNodeInsert()` | `cnode.c:336-341` | 插入 cap（不降权） | `airymax_cap_mintcopy()` |
| Move | `invokeCNodeMove()` | `cnode.c:343-348` | 移动 cap | `airymax_cap_move()` |
| Rotate | `invokeCNodeRotate()` | `cnode.c:350-361` | 三槽位旋转交换 | `airymax_cap_rotate()` |

**关键源码摘录**（`src/object/cnode.c:315-348`）：

```c
/* seL4: src/object/cnode.c:315-348 — capability 核心操作 */
exception_t invokeCNodeRevoke(cte_t *destSlot)
{
        return cteRevoke(destSlot);
}

exception_t invokeCNodeDelete(cte_t *destSlot)
{
        return cteDelete(destSlot, true);
}

exception_t invokeCNodeInsert(cap_t cap, cte_t *srcSlot, cte_t *destSlot)
{
        cteInsert(cap, srcSlot, destSlot);
        return EXCEPTION_NONE;
}

exception_t invokeCNodeMove(cap_t cap, cte_t *srcSlot, cte_t *destSlot)
{
        cteMove(cap, srcSlot, destSlot);
        return EXCEPTION_NONE;
}
```

**capability 不可伪造性**：seL4 的 cap 是内核对象，用户态无法直接构造，只能通过现有 cap 派生（Mint/Copy）。这是 Cupolas 安全模型的根基。

#### 2.2.1 agent-linux Cupolas capability 迁移 [IND]

agent-linux 把 seL4 capability 思想叠加到 Linux 6.6 基线，形成 Cupolas 派生模型：

```c
/* agent-linux: include/airymax/cupolas_types.h — Cupolas capability（[SC] 共享契约层） */
#ifndef _AIRYMAX_CUPOLAS_TYPES_H
#define _AIRYMAX_CUPOLAS_TYPES_H

#include <linux/types.h>

/* capability 节点（参考 seL4 cte_t，[IND] 独立实现） */
struct airymax_cap_node {
        uint32_t magic;                 /* 防伪魔数（等价 seL4 cap 不可伪造性） */
        uint32_t obj_type;              /* 对象类型（TCB/EP/VSpace/...） */
        uint32_t perms;                 /* 权限位（读/写/执行/Grant） */
        uint32_t depth;                 /* 派生深度（Revoke 用） */
        void *obj;                      /* 指向内核对象 */
        struct airymax_cap_node *parent; /* 父 cap（派生链） */
        struct airymax_cap_node *child;  /* 子 cap 链表 */
        struct list_head siblings;       /* 兄弟链表 */
};

/* 权限位（参考 seL4 cap_endpoint_cap_get_capCanSend 等） */
#define AIRYMAX_CAP_READ    (1u << 0)
#define AIRYMAX_CAP_WRITE   (1u << 1)
#define AIRYMAX_CAP_EXEC    (1u << 2)
#define AIRYMAX_CAP_GRANT   (1u << 3)   /* 可派生（等价 seL4 CanGrant） */

#endif /* _AIRYMAX_CUPOLAS_TYPES_H */
```

```c
/* agent-linux: security/airymax/cupolas.c — Cupolas 操作（[IND] 独立实现） */
/* 等价 seL4 invokeCNodeRevoke（cnode.c:315）—— 递归撤销派生链 */
int airymax_cap_revoke(struct airymax_cap_node *parent)
{
        struct airymax_cap_node *child, *tmp;

        list_for_each_entry_safe(child, tmp, &parent->siblings, siblings) {
                airymax_cap_revoke(child);     /* 递归撤销子链 */
                airymax_cap_delete(child);
        }
        return 0;
}

/* 等价 seL4 invokeCNodeMove（cnode.c:343）—— 移动 cap */
int airymax_cap_move(struct airymax_cap_node *src, struct airymax_cap_node *dst)
{
        dst->obj_type = src->obj_type;
        dst->perms = src->perms;
        dst->obj = src->obj;
        /* 源 cap 清零（不可伪造性保证） */
        memset(src, 0, sizeof(*src));
        src->magic = 0;
        return 0;
}
```

### 2.3 快速 IPC（Fast IPC）

**源码路径**: `seL4: src/fastpath/fastpath.c:19-300` / `include/fastpath/fastpath.h:1-172`

seL4 的 fast IPC 是其性能领先的关键。`fastpath_call()` 是核心快路径（`src/fastpath/fastpath.c:19`）：

```c
/* seL4: src/fastpath/fastpath.c:19-100 — 快速 IPC 调用路径 */
void NORETURN fastpath_call(word_t cptr, word_t msgInfo)
{
        seL4_MessageInfo_t info;
        cap_t ep_cap;
        endpoint_t *ep_ptr;
        word_t length;
        tcb_t *dest;
        ...
        /* 1. 解析消息信息 */
        info = messageInfoFromWord_raw(msgInfo);
        length = seL4_MessageInfo_get_length(info);

        /* 2. 快路径预检查：无额外 cap、长度合法、无 fault */
        if (unlikely(fastpath_mi_check(msgInfo) ||
                     fault_type != seL4_Fault_NullFault)) {
                slowpath(SysCall);        /* 退化到慢路径 */
        }

        /* 3. capability 查找（lookup_fp） */
        ep_cap = lookup_fp(TCB_PTR_CTE_PTR(NODE_STATE(ksCurThread), tcbCTable)->cap,
                           cptr);

        /* 4. 校验 endpoint cap */
        if (unlikely(!cap_capType_equals(ep_cap, cap_endpoint_cap) ||
                     !cap_endpoint_cap_get_capCanSend(ep_cap))) {
                slowpath(SysCall);
        }

        /* 5. 取目标线程 + 检查接收方在等待 */
        ep_ptr = EP_PTR(cap_endpoint_cap_get_capEPPtr(ep_cap));
        dest = TCB_PTR(endpoint_ptr_get_epQueue_head(ep_ptr));
        if (unlikely(endpoint_ptr_get_state(ep_ptr) != EPState_Recv)) {
                slowpath(SysCall);
        }
        /* 6. 直接切换到目标线程（避免完整调度） */
        ...
}
```

**快路径设计精髓**（`include/fastpath/fastpath.h:64-108`）：

- `lookup_fp()` 是内联 cap 查找（`fastpath.h:65`），radix 树遍历
- `maybeDonateSchedContext_fp()` 调度上下文捐赠（`fastpath.h:16`）
- 快路径直接线程切换，不经完整调度器
- 任何不满足快路径条件即 `slowpath()` 退化

#### 2.3.1 agent-linux IPC 快路径设计 [IND]

agent-linux 用 io_uring（用户态-内核态）+ kfifo（kthread 间）叠加 seL4 fast IPC 思想，形成 AgentsIPC 128B 消息头：

```c
/* agent-linux: include/airymax/agents_ipc.h — AgentsIPC 128B 消息头（[SC] 共享契约层） */
#ifndef _AIRYMAX_AGENTS_IPC_H
#define _AIRYMAX_AGENTS_IPC_H

#include <linux/types.h>
#include <airymax/cupolas_types.h>

/* AgentsIPC 128B 消息头（参考 seL4_MessageInfo，[IND] 独立实现） */
struct airymax_ipc_hdr {
        uint32_t magic;                 /* 0x AIRYMAX_IPC_MAGIC */
        uint16_t op;                    /* 操作码（等价 seL4 syscall 号） */
        uint16_t msg_len;               /* 消息体长度（等价 seL4 length） */
        uint32_t cap_idx;               /* capability 索引（等价 seL4 cptr） */
        uint32_t badge;                 /* 发送方标识（等价 seL4 badge） */
        uint32_t label;                 /* 消息标签（等价 seL4 label） */
        uint32_t flags;                 /* 标志位 */
        uint32_t seq;                   /* 序列号（防重放） */
        uint32_t reserved[8];           /* 预留（凑齐 128B） */
        /* 消息体紧跟其后，最长 4KB */
} __packed;

#define AIRYMAX_IPC_MAGIC         0x41495043  /* "AIPC" */
#define AIRYMAX_IPC_HDR_SIZE      128
#define AIRYMAX_IPC_BODY_MAX      4096

#endif /* _AIRYMAX_AGENTS_IPC_H */
```

```c
/* agent-linux: ipc/airymax/fastpath.c — AgentsIPC 快路径（[IND] 独立实现） */
/* 等价 seL4 fastpath_call（fastpath.c:19）—— 快速 IPC 派发 */
int airymax_ipc_fastpath(struct airymax_ipc_hdr *hdr)
{
        struct airymax_cap_node *cap;
        int ret;

        /* 1. 快路径预检查（等价 fastpath_mi_check） */
        if (unlikely(hdr->magic != AIRYMAX_IPC_MAGIC))
                return -EINVAL;
        if (unlikely(hdr->msg_len > AIRYMAX_IPC_BODY_MAX))
                return -EMSGSIZE;

        /* 2. capability 查找（等价 lookup_fp，fastpath.h:65） */
        cap = airymax_cap_lookup_fast(hdr->cap_idx);
        if (unlikely(!cap || !(cap->perms & AIRYMAX_CAP_WRITE)))
                return -EACCES;

        /* 3. 校验目标端点（等价 EPState_Recv 检查） */
        if (unlikely(!airymax_ep_can_recv(cap->obj)))
                return -EAGAIN;

        /* 4. 快路径直接派发（不经完整调度） */
        ret = airymax_ep_deliver(cap->obj, hdr);
        return ret;
}
```

### 2.4 形式化验证（Verification）

**源码体现**: `manual/`（Doxyfile 99,890 字节 + LaTeX 手册）+ 外部 `l4v` 仓库（Isabelle/HOL 证明）

seL4 验证栈四层：

| 层 | 内容 | 工具 |
|----|------|------|
| 二进制 | 二进制验证（编译器正确性） | SMT 求解器 |
| C 实现 | 功能正确性证明 | Isabelle/HOL |
| 可执行规范 | Haskell 参考实现 | — |
| 抽象规范 | 数学抽象 | Isabelle/HOL |

**`CONTRIBUTING.md:25-29`** 明确贡献要求：

> Contributions to `master` should additionally either be invisible to the proof in l4v, such as comments, documentation, style, unverified platform, etc, or they should come with proof updates to `l4v`.

#### 2.4.1 agent-linux 复用方式 [IND]

agent-linux 无法达到 seL4 完整形式化验证（基于 Linux 6.6，规模差异巨大），但采纳分阶段验证目标：

- **1.0.1**：关键路径（Cupolas capability 派生、AgentsIPC 128B 头）用 KUnit 单元测试 + TLA+ 模型检查
- **2.0+**：Cupolas 核心操作（revoke/move/mintcopy）尝试 Isabelle/HOL 部分证明

---

## 3. seL4 工程标准提炼

### 3.1 `CMakeLists.txt` —— 构建标准

**源码路径**: `seL4: CMakeLists.txt:1-27,248`

seL4 用 CMake 替代 Kbuild，关键设计：

| 行段 | 内容 | 源码行号 |
|------|------|----------|
| 最低版本 | `cmake_minimum_required(VERSION 3.16.0)` | L7 |
| 工具查找 | `find_file(KERNEL_HELPERS_PATH helpers.cmake ...)` | L14-16 |
| 必需工具 | `RequireTool(...)` 声明 | L22-40 |
| Python 工具 | bitfield_gen / config_gen / hardware_gen / invocation_header_gen | L31-39 |
| 项目声明 | `project(seL4 C ASM)` | L11 |
| 通用标志 | `-D__KERNEL_${KernelWordSize}__` | L48 |
| 架构标志 | x86/ARM/RISC-V 分支 | L50-100 |

**关键工具集**（`CMakeLists.txt:31-40`）：

```
set(PYTHON3 "python3" CACHE INTERNAL "")
RequireTool(CPP_GEN_PATH cpp_gen.sh)
RequireTool(CIRCULAR_INCLUDE circular_includes.py)
RequireTool(CONFIG_GEN_PATH config_gen.py)
RequireTool(BF_GEN_PATH bitfield_gen.py)
RequireTool(HARDWARE_GEN_PATH hardware_gen.py)
RequireTool(INVOCATION_ID_GEN_PATH invocation_header_gen.py)
RequireTool(INVOCATION_JSON_GEN_PATH invocation_json_gen.py)
RequireTool(SYSCALL_ID_GEN_PATH syscall_header_gen.py)
RequireTool(XMLLINT_PATH xmllint.sh)
```

### 3.2 `gcc.cmake` / `llvm.cmake` —— 工具链配置

**源码路径**: `seL4: gcc.cmake:1-183` / `llvm.cmake:1-44`

| 工具链 | 文件 | 关键设计 |
|--------|------|----------|
| GCC | `gcc.cmake:37-53` | `FindPrefixedGCC()` 自动查找交叉编译器前缀 |
| LLVM | `llvm.cmake:14-28` | `LLVM_TOOLCHAIN ON` + `clang` + triple |
| ccache | 两文件均启用 | `find_program(CCACHE ccache)` 缓存加速 |
| 彩色输出 | `gcc.cmake:168-183` | `FORCE_COLORED_OUTPUT` 选项 |

#### 3.2.1 agent-linux 复用方式 [IND]

agent-linux 基于 Linux 6.6 用 Kbuild（非 CMake），但采纳工具链思想：

- **[SS] 同源**：双编译器（GCC/Clang）、ccache 加速、交叉编译器自动查找
- **[IND] 独立**：用 Kbuild 而非 CMake；Q16.16 定点数约束（seL4 无此约束）

### 3.3 `CONTRIBUTING.md` —— 贡献标准

**源码路径**: `seL4: CONTRIBUTING.md:1-57`

| 规则 | 源码行号 | agent-linux 复用 |
|------|----------|---------------------|
| 提交可二分（bisectable） | L15 | [SS] 采纳 |
| 提交保持小 | L17 | [SS] 采纳 |
| 必须通过 sel4test | L23-25 | [SS] 采纳（airymax-kunit + kselftest） |
| proof 不可见变更需附 proof 更新 | L27-29 | [IND] 形式化目标阶段化 |
| DCO sign-off（`git commit -s`） | L43-56 | [SS] 完全采纳 |

### 3.4 `SECURITY.md` —— 漏洞治理标准

**源码路径**: `seL4: SECURITY.md:1-99`

| 承诺 | 源码行号 | agent-linux 复用 |
|------|----------|---------------------|
| 14 天内响应 | L50 | [SS] 采纳 |
| 90 天修复目标（proof 可能更长） | L53 | [SS] 采纳 |
| 公开致谢 | L58 | [SS] 采纳 |
| 漏洞邮箱 security@seL4.systems | L70 | [IND] 独立邮箱 security@spharx.com |
| 验证配置外的漏洞也受理 | L77-98 | [SS] 采纳 |

**`SECURITY.md:77-89` 关键澄清**（验证与漏洞关系）：

> Even verified configurations contain some code that is assumed to do the right thing, including boot code, assembly stubs, and cache management. If that code does the wrong thing, there might be a security vulnerability.

### 3.5 `LICENSES/` —— 许可证治理

**源码路径**: `seL4: LICENSES/`（10 文件）

| 许可证 | 文件 | 用途 |
|--------|------|------|
| GPL-2.0-only | `GPL-2.0-only.txt` | 内核主体 |
| BSD-2/3-Clause | `BSD-*.txt` | 部分组件 |
| MIT | `MIT.txt` | 部分工具 |
| CC-BY-SA-4.0 | `CC-BY-SA-4.0.txt` | 文档 |
| Apache-2.0 | `Apache-2.0.txt` | 部分组件 |
| LPPL-1.3c | `LPPL-1.3c.txt` | LaTeX 手册 |
| SHL-0.51 | `SHL-0.51.txt` | 部分硬件描述 |
| LicenseRef-Trademark | `LicenseRef-Trademark.txt` | 商标 |

OLK-6.6 也用同样结构（`LICENSES/preferred/`、`dual/`、`exceptions/`、`deprecated/`）。

#### 3.5.1 agent-linux 复用方式 [IND]

agent-linux 采纳 SPDX-License-Identifier + LICENSES 目录治理（[SS] 同源），许可证策略独立：

- **开源部分**（`docs/docs-linux/`）：AGPL v3 + Apache 2.0
- **闭源部分**（`docs-closed/`）：SPHARX Ltd 内部参考，不对外发布
- **内核代码**：GPL-2.0（与 Linux 6.6 基线一致）

---

## 4. agent-linux 微内核化改造策略

### 4.1 改造哲学：叠加而非重写

| seL4 思想 | seL4 实现方式 | agent-linux 叠加方式 | 边界 |
|-----------|--------------|------------------------|------|
| 最小化内核 | 仅 4 机制，~10K SLOC | sched_ext + eBPF 把策略移出内核 | [IND] |
| capability 安全 | seL4 CNode + cap_t | Cupolas 派生链（叠加 LSM/eBPF） | [IND] |
| 快速 IPC | fastpath_call() | AgentsIPC 128B 头 + io_uring | [IND] |
| 服务用户态化 | seL4 用户态服务 | agent-linux 12 daemons | [IND] |
| 形式化验证 | Isabelle/HOL 完整证明 | KUnit + TLA+ 阶段化目标 | [IND] |

### 4.2 capability 安全模型迁移（seL4 cap → Cupolas）

**迁移映射表**：

| seL4 概念 | seL4 源码 | agent-linux Cupolas | 实现机制 |
|-----------|-----------|------------------------|----------|
| CNode（cap 表） | `include/object/cnode.h` | `struct airymax_cap_node` | LSM blob（cred/inode/file/task） |
| cap_t（cap 令牌） | `include/object/structures.h` | `airymax_cap_node` + magic 防伪 | eBPF kfunc 校验 |
| CSpace（cap 空间） | `src/kernel/cspace.c` | Cupolas blob 树 | radix 树 |
| Mint（派生降权） | `cnode.c` | `airymax_cap_mint()` | LSM hook |
| Copy（复制不降权） | `cnode.c` | `airymax_cap_mintcopy()` | LSM hook |
| Move（移动） | `cnode.c:343` | `airymax_cap_move()` | LSM hook |
| Revoke（递归撤销） | `cnode.c:315` | `airymax_cap_revoke()` | LSM hook + 派生链遍历 |
| CanGrant（可派生） | `cap_endpoint_cap_get_capCanGrant` | `AIRYMAX_CAP_GRANT` 权限位 | 位校验 |

**不可伪造性实现差异**：
- seL4：cap 是内核对象，用户态无法直接构造（硬件 MMU 隔离）
- agent-linux：cap 通过 magic + eBPF kfunc 校验（叠加在 Linux cred 上），无法达到 seL4 硬件级不可伪造，但满足智能体场景

```c
/* agent-linux: security/airymax/cupolas_bpf.c — eBPF kfunc 校验 cap（[IND]） */
/* BPF_PROG_TYPE_LSM 程序：校验 cap 不可伪造性 */
SEC("lsm/airymax_cap_verify")
int BPF_PROG(airymax_cap_verify, struct airymax_cap_node *cap, int ret)
{
        if (cap->magic != AIRYMAX_CAP_MAGIC)
                return -EACCES;          /* 防伪校验失败 */
        if (!(cap->perms & AIRYMAX_CAP_GRANT))
                return -EPERM;          /* 无派生权限 */
        return 0;
}
```

### 4.3 IPC 快路径设计（seL4 fast IPC → AgentsIPC 128B）

**设计对照**：

| seL4 fast IPC | agent-linux AgentsIPC |
|----------------|-------------------------|
| `fastpath_call()` 同步调用 | io_uring SQE 提交 + CQE 完成 |
| `MessageInfo`（word 编码） | 128B 固定消息头 |
| `lookup_fp()` cap 查找 | `airymax_cap_lookup_fast()` radix 树 |
| `EPState_Recv` 接收检查 | `airymax_ep_can_recv()` |
| 直接线程切换 | io_uring task_work 回调 |
| kthread 间不适用 | kfifo + wait_event_interruptible |

**用户态-内核态 IPC**：io_uring（零拷贝、批量提交）
**kthread 间 IPC**：kfifo + `wait_event_interruptible`（禁用 io_uring，避免用户态机制滥用）

```c
/* agent-linux: ipc/airymax/kfifo_ipc.c — kthread 间快路径（[IND]） */
/* kthread 间通信用 kfifo + wait_event_interruptible（不用 io_uring） */
int airymax_kthread_send(struct airymax_kfifo_chan *ch, void *msg, size_t len)
{
        int ret;

        ret = kfifo_in(&ch->fifo, msg, len);
        if (ret == len) {
                wake_up_interruptible(&ch->rx_wait);
                return 0;
        }
        /* 队列满，等待发送方处理 */
        ret = wait_event_interruptible(ch->tx_wait,
                                       kfifo_avail(&ch->fifo) >= len);
        if (ret)
                return -EINTR;
        kfifo_in(&ch->fifo, msg, len);
        wake_up_interruptible(&ch->rx_wait);
        return 0;
}

int airymax_kthread_recv(struct airymax_kfifo_chan *ch, void *buf, size_t len)
{
        int ret;

        ret = kfifo_out(&ch->fifo, buf, len);
        if (ret == len) {
                wake_up_interruptible(&ch->tx_wait);
                return 0;
        }
        /* 无数据，等待 */
        ret = wait_event_interruptible(ch->rx_wait,
                                       kfifo_len(&ch->fifo) >= len);
        if (ret)
                return -EINTR;
        kfifo_out(&ch->fifo, buf, len);
        wake_up_interruptible(&ch->tx_wait);
        return 0;
}
```

### 4.4 服务用户态化（seL4 用户态服务 → agent-linux 12 daemons）

seL4 把 FS/网络/驱动等移到用户态服务。agent-linux 在 Linux 6.6 基线上，把智能体操作系统服务拆分为 12 个用户态 daemon：

| # | daemon | seL4 对应用户态服务 | 边界 |
|---|--------|---------------------|------|
| 1 | cognition-daemon | seL4 无（智能体专属） | [IND] |
| 2 | memory-daemon | seL4 VM 模型 | [IND] |
| 3 | ipc-router-daemon | seL4 IPC 中继 | [IND] |
| 4 | cap-broker-daemon | seL4 cap 分配器 | [IND] |
| 5 | sched-policy-daemon | seL4 调度策略 | [IND] |
| 6 | bpf-loader-daemon | seL4 无 | [IND] |
| 7 | fs-proxy-daemon | seL4 用户态 FS | [IND] |
| 8 | net-proxy-daemon | seL4 用户态网络栈 | [IND] |
| 9 | device-mgr-daemon | seL4 用户态驱动 | [IND] |
| 10 | security-daemon | seL4 安全监控 | [IND] |
| 11 | observ-daemon | seL4 无 | [IND] |
| 12 | lifecycle-daemon | seL4 资源管理 | [IND] |

### 4.5 最小化内核职责清单

| 内核职责 | seL4 | agent-linux | 机制 |
|----------|------|----------------|------|
| 调度机制 | 调度器（内核内） | sched_ext 调度类 | BPF 策略在外 |
| IPC 机制 | Endpoint（内核内） | io_uring + kfifo | 策略在 daemon |
| capability | CNode（内核内） | Cupolas blob | 校验在 eBPF |
| 地址空间 | VSpace（内核内） | Linux mm | 策略在 MemoryRovol |
| 中断 | IRQ（内核内） | Linux IRQ | — |
| FS | 用户态 | 用户态 daemon | [IND] |
| 网络 | 用户态 | 用户态 daemon | [IND] |
| 驱动 | 用户态 | 1.0.1 保留内核态 | 后续阶段移出 |

---

## 5. 改造路线图

### 5.1 阶段总图

```
0.1.1 文档体系完成（已完成 2026-07-07）
        ↓ seL4 思想提炼 + 映射文档（本文档）
1.0.1 开发阶段一：内核机制叠加
        ↓ sched_ext + AgentsIPC + Cupolas 框架
1.0.2-1.1.x 开发阶段二：用户态服务化
        ↓ 12 daemons 上线
1.2.x-2.0 开发阶段三：驱动用户态化
        ↓ 最小微内核（~80K LOC 目标）
2.0+ 开发阶段四：形式化验证
        ↓ Cupolas + AgentsIPC 关键路径验证
```

### 5.2 阶段交付物

| 阶段 | 版本 | 关键交付物 | seL4 思想体现 |
|------|------|------------|----------------|
| 文档 | 0.1.1 | 26 闭源参考文档（含本文档） | 思想提炼完成 |
| 开发一 | 1.0.1 | sched_ext 调度类 + AgentsIPC 128B + Cupolas 框架 + Q16.16 库 | capability + fast IPC + 最小化 |
| 开发二 | 1.0.2-1.1.x | 12 daemons 用户态化 | 服务用户态化 |
| 开发三 | 1.2.x-2.0 | 驱动用户态化 + 内核 ~80K LOC | 最小化内核 |
| 开发四 | 2.0+ | Cupolas/AgentsIPC Isabelle 证明 | 形式化验证 |

### 5.3 1.0.1 阶段详细任务

| # | 任务 | seL4 参考 | 交付物 |
|---|------|-----------|--------|
| 1 | `include/airymax/cupolas_types.h` | `include/object/cap.h` | capability 类型 [SC] |
| 2 | `include/airymax/agents_ipc.h` | `libsel4` MessageInfo | 128B 头 [SC] |
| 3 | `security/airymax/cupolas.c` | `src/object/cnode.c:315-348` | cap 操作 [IND] |
| 4 | `ipc/airymax/fastpath.c` | `src/fastpath/fastpath.c:19` | IPC 快路径 [IND] |
| 5 | `ipc/airymax/kfifo_ipc.c` | seL4 无 | kthread 间 IPC [IND] |
| 6 | `include/airymax/airymax_q16.h` | seL4 无 | Q16.16 定点数 [IND] |
| 7 | `lib/airymax/airymax_q16_test.c` | — | KUnit 测试 [IND] |
| 8 | sched_ext BPF 调度策略 | seL4 调度器 | 调度策略外置 [IND] |

---

## 6. 风险评估

### 6.1 本质差异风险

seL4 是形式化验证的微内核，agent-linux 基于 Linux 6.6 改造，两者本质差异带来风险：

| 风险 | seL4 | agent-linux | 影响 | 缓解 |
|------|------|----------------|------|------|
| 不可伪造性 | 硬件级（MMU 隔离） | 软件级（magic + eBPF） | cap 可被绕过 | Cupolas + LSM + seccomp 多层 |
| 形式化验证 | 完整证明 | 阶段化目标 | 关键路径有缺陷 | KUnit + TLA+ 模型检查 |
| 内核规模 | ~10K SLOC | ~80K LOC 目标（Linux 基线） | 攻击面大 | 攻击面审计 + eBPF 监控 |
| IPC 性能 | 快路径硬件优化 | io_uring + 内核切换 | 性能不及 seL4 | io_uring 零拷贝 + 128B 头 |
| 时间隔离 | MCS 验证 | sched_ext 时间片 | 隔离不彻底 | SCHED_AGENT 时间预算 |

### 6.2 工程风险

| 风险 | 影响 | 概率 | 缓解 |
|------|------|------|------|
| sched_ext 稳定性 | 调度类崩溃 | 中 | OLK-6.6 内置 SCHED_EXT=7 已验证 |
| eBPF kfunc 兼容 | 内核升级断裂 | 中 | kfunc 版本化 + KABI 管理 |
| io_uring 滥用 | 安全风险 | 中 | kthread 间强制 kfifo |
| Q16.16 精度不足 | 智能体决策偏差 | 低 | Q16.16 够用（16 位小数） |
| 12 daemons 复杂度 | 系统难维护 | 高 | 渐进交付，每阶段可用 |

### 6.3 安全风险

| 风险 | seL4 状态 | agent-linux 风险 | 缓解 |
|------|-----------|---------------------|------|
| cap 伪造 | 不可能（硬件） | 可能（软件校验绕过） | eBPF + LSM + 魔数三重 |
| Rowhammer | seL4 假设内存不可破坏 | 同假设失效 | 同 seL4，无解 |
| 旁路攻击 | seL4 未完全证明 | 同 | 常规缓解 |
| daemon 提权 | seL4 服务隔离 | daemon 漏洞提权 | Cupolas 最小权限 + seccomp |

### 6.4 缓解优先级

1. **P0**：Cupolas 不可伪造性（eBPF + LSM + 魔数）
2. **P0**：AgentsIPC 128B 头一致性（KUnit 全覆盖）
3. **P1**：sched_ext 稳定性（kselftest）
4. **P1**：Q16.16 精度（边界测试）
5. **P2**：12 daemons 隔离（seccomp + Cupolas）

---

## 7. 与开源文档的关系

- 本改造方案是**闭源参考**，不对外发布
- 开源设计文档（`docs/docs-linux/`）引用本方案时，必须用 agent-linux 自身语言表述
- 开源文档中**严禁**出现 seL4 源码路径、行号、函数名等直接引用
- 开源文档中**严禁**出现任何主流 Linux 发行版的名称

---

## 8. 相关文档

| 文档 | 关系 |
|------|------|
| `10-references/microkernel-design-ref/01-sel4-reference.md` | seL4 设计参考（思想层） |
| `10-references/microkernel-design-ref/04-microkernel-strategy.md` | 改造策略对照（seL4+Zircon+Minix3） |
| `10-references/olk66-source-mapping/01-sched-ext-mapping.md` | sched_ext 源码映射（SCHED_AGENT） |
| `10-references/olk66-source-mapping/02-io-uring-mapping.md` | io_uring 源码映射（AgentsIPC） |
| `10-references/olk66-source-mapping/07-engineering-toolchain-mapping.md` | 工程工具链映射 |
| `agent-linux基本工程标准规范.md` | 工程标准规范 |

---

## 9. 附录：seL4 关键源码引用清单

| 引用 | 源码位置 | 用途 |
|------|----------|------|
| `fastpath_call()` | `src/fastpath/fastpath.c:19` | 快速 IPC 入口 |
| `lookup_fp()` | `include/fastpath/fastpath.h:65` | cap 快查找 |
| `maybeDonateSchedContext_fp()` | `include/fastpath/fastpath.h:16` | 调度上下文捐赠 |
| `invokeCNodeRevoke()` | `src/object/cnode.c:315` | cap 递归撤销 |
| `invokeCNodeDelete()` | `src/object/cnode.c:320` | cap 删除 |
| `invokeCNodeInsert()` | `src/object/cnode.c:336` | cap 插入 |
| `invokeCNodeMove()` | `src/object/cnode.c:343` | cap 移动 |
| `invokeCNodeRotate()` | `src/object/cnode.c:350` | cap 旋转 |
| `handleSyscall()` | `src/api/syscall.c` | 系统调用派发 |
| `CMakeLists.txt` | `CMakeLists.txt:1` | 顶层构建 |
| `FindPrefixedGCC()` | `gcc.cmake:37` | GCC 工具链查找 |
| DCO sign-off | `CONTRIBUTING.md:43` | 贡献签署 |
| 漏洞响应承诺 | `SECURITY.md:50` | 安全治理 |
| LICENSES 治理 | `LICENSES/` | 许可证 |

---

> **文档结束** | Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved. | 闭源内部参考（docs-closed）
