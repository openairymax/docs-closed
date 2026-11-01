Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 第二部分：seL4 工程思想分析

> **文档定位**： v0.9.0 综合审查报告第二部分。基于 seL4 `seL4-master`（src/ + include/ + libsel4/ + tools/ + proof/ + spec/ 全量源码）的深度研究，分析 seL4 在架构层被选择性借鉴的 5 项工程思想（ES-SEL4-1~5）、被 OS-IRON-012 明确禁止借鉴的编码风格层，以及研究范围与借鉴范围之间的差异。本部分揭示 agent-linux 在 seL4 借鉴范围声明上存在 P0-CRITICAL 级别的数量三重冲突。\
> **版本**： 0.9.0\
> **审查对象**： `01Reference/seL4-master/`（全量源码）\
> **审查方法**： 源码级证据 + 闭源总纲 §12 / 附录 D 对照 + 开源手册 OS-IRON-012 对照\
> **SPDX-License-Identifier**： AGPL-3.0-or-later OR Apache-2.0

---

## 1. seL4 架构层借鉴：ES-SEL4-1~5 源码级验证

agent-linux 在架构层选择性借鉴 seL4 的 5 项工程思想。以下对每项进行源码级验证，确认 seL4 源码中真实存在且借鉴方式合理。

### 1.1 ES-SEL4-1：极简原则（Liedtke minimality）

**理论来源**： Liedtke minimality principle——微内核应只包含不可由用户态实现的最小机制集。

**seL4 源码级证据**：

seL4 内核极小，核心机制仅 4 类：

```
seL4-master/src/
├── object/
│   ├── tcb.c          # 线程控制块
│   ├── endpoint.c     # IPC 端点
│   ├── cnode.c        # capability 节点
│   ├── notification.c # 异步通知
│   ├── untyped.c      # 未类型化内存
│   └── frame.c        # 页帧
├── api/
│   └── syscall.c      # 系统调用入口
├── kernel/
│   ├── boot.c         # 启动
│   ├── thread.c       # 线程调度
│   └── ...
└── fastpath/
    └── fastpath.c     # IPC fastpath 优化
```

seL4 内核不包含文件系统、网络栈、设备驱动——这些全部在用户态实现。内核只提供：线程（TCB）、IPC（Endpoint）、capability（CNode）、内存（Untyped + Frame）、通知（Notification）。

**agent-linux 借鉴方式**： 影响 `airymaxos-kernel` 子仓的内核机制最小化取向——corekern 仅保留 4 原子机制（task/memory/ipc/time），不将文件系统/网络栈/驱动放入内核态。

**品味评价**： 极简原则的借鉴是合理的——它让内核保持小而美，复杂功能移至用户态，便于形式化验证和安全性论证。

### 1.2 ES-SEL4-2：capability 单一权限模型

**理论来源**： seL4 使用 capability 作为唯一的权限表达机制，不使用 ACL/RBAC 等其他模型。

**seL4 源码级证据**：

```c
/* seL4-master/src/object/cnode.c —— capability 操作全量实现 */
/* 7 种 capability 操作：mint/mintcopy/derive/revoke/copy/mutate/delete */
```

seL4 的 capability 模型：
- 所有权限通过 capability 表达（不是 UID/GID/ACL）
- capability 存储在 CNode（capability node tree）中
- 7 种操作：Copy / Mint / Move / Mutate / Revoke / Delete / Rotate
- capability 可派生（derive），形成权限树
- 撤销（revoke）会递归撤销所有派生 capability

**agent-linux 借鉴方式**： 影响 `airymaxos-security` 子仓的 capability 设计——`security_types.h` 定义 `enum airy_cap_op` 包含 7 种操作（AIRY_CAP_OP_COPY/MINT/MOVE/MUTATE/REVOKE/DELETE/ROTATE），与 seL4 同源。

```c
/* include/airymax/security_types.h —— [SC] 共享契约层 */
enum airy_cap_op {
    AIRY_CAP_OP_COPY    = 0,
    AIRY_CAP_OP_MINT    = 1,
    AIRY_CAP_OP_MOVE    = 2,
    AIRY_CAP_OP_MUTATE  = 3,
    AIRY_CAP_OP_REVOKE  = 4,
    AIRY_CAP_OP_DELETE  = 5,
    AIRY_CAP_OP_ROTATE  = 6,
};
```

**品味评价**： capability 单一模型的借鉴是合理的——它统一了权限表达，避免了 ACL/RBAC/capability 三套并存的复杂性。但 agent-linux 同时保留了 LSM 钩子（252 ID），这是与 seL4 的关键差异——seL4 纯 capability，agent-linux 是 capability + LSM 融合模型。这种融合的合理性需要在 1.0.1 阶段进一步论证。

### 1.3 ES-SEL4-3：服务用户态化

**理论来源**： seL4 将所有非核心服务（文件系统、网络栈、设备驱动）移至用户态，内核仅提供最小机制。

**seL4 源码级证据**：

seL4 内核源码中不包含：
- 文件系统（VFS/ext4/FAT 等）
- 网络栈（TCP/IP/socket 等）
- 设备驱动（除启动必需的最小驱动）

这些服务在用户态实现，通过 IPC 与内核通信。seL4 的 `libsel4/` 是用户态库，不是内核的一部分。

**agent-linux 借鉴方式**： 影响 `airymaxos-services` 子仓——VFS/网络栈/部分驱动移至用户态。闭源总纲 §13.4 声明"用户态服务架构"。

**品味评价**： 服务用户态化的借鉴需要审慎——seL4 是从零设计的微内核，服务用户态化是其基本架构；而 agent-linux 基于 Linux 6.6 fork，将 VFS/网络栈移至用户态是重大改造，需评估性能影响和工程复杂度。这一借鉴的落地难度远高于其他 4 项，是 1.0.1 阶段的最大技术风险。

### 1.4 ES-SEL4-4：消息传递 IPC（含 fastpath）

**理论来源**： seL4 使用消息传递（message passing）作为唯一 IPC 机制，并提供 fastpath 优化减少 syscall 开销。

**seL4 源码级证据**：

```c
/* seL4-master/src/object/endpoint.c —— IPC 端点实现 */
/* sendIPC / recvIPC 是核心 IPC 函数 */

/* seL4-master/src/fastpath/fastpath.c —— IPC fastpath 优化 */
/* fastpath 是 IPC 的最短路径，绕过完整调度路径 */
```

seL4 IPC 模型：
- Endpoint 是 IPC 端点，发送方/接收方在此 rendezvous
- Message Register（MR）+ IPC Buffer 双通道传输消息
- MessageInfo 编码（label + caps + length + unwrap）
- fastpath 优化：常见 IPC 路径绕过完整调度，直接切换线程

**agent-linux 借鉴方式**： 影响 `airymaxos-kernel` 子仓的 IPC 子系统——采用 io_uring 消息传递模型，[SC] 共享 `ipc.h` 定义 128 字节消息头 + magic 0x41524531 ('ARE1')。

```c
/* include/airymax/ipc.h —— [SC] 共享契约层 */
struct airy_ipc_msg_hdr {
    __u32   magic;          /* 0x41524531 'ARE1' */
    __u16   opcode;
    __u16   flags;
    __u64   trace_id;
    __u64   timestamp_ns;
    __u64   src_task;
    __u64   dst_task;
    __u32   payload_len;
    __u8    reserved[84];
} __attribute__((packed));

_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128,
        "IPC message header must be exactly 128 bytes");
```

**品味评价**： 消息传递 IPC 的借鉴是合理的，但 agent-linux 选择 io_uring 而非 seL4 的 Endpoint 模型，这是基于 Linux 6.6 基线的务实选择——io_uring 是 Linux 6.6 原生的高性能异步 I/O 框架，复用它比重新实现 Endpoint 模型更符合"Linux 6.6 为基"的工程取向。

### 1.5 ES-SEL4-5：形式化验证驱动

**理论来源**： seL4 是世界上第一个功能正确性经过形式化验证的操作系统内核。

**seL4 源码级证据**：

```
seL4-master/
├── proof/        # Isabelle/HOL 形式化证明
├── spec/         # 形式化规约（haskell/executable/C）
├── capDL/        # capability 描述语言
└── tools/        # bitfield_gen.py 等代码生成工具
```

seL4 的形式化验证三段式：
1. **抽象规约**（Abstract Spec）—— Haskell 描述内核行为
2. **设计规约**（Design Spec）—— 可执行规约
3. **C 代码验证**（C Verification）—— 证明 C 实现符合设计规约

**agent-linux 借鉴方式**： 影响 `airymaxos-tests-linux` 子仓——`formal-verification` 三段式框架。但 0.1.1 阶段仅文档框架，1.0.1 阶段才填充实际验证代码。

**品味评价**： 形式化验证的借鉴是雄心勃勃的——seL4 的形式化验证耗费数年，agent-linux 基于 Linux 6.6 fork（数百万行代码），全量形式化验证不现实。建议借鉴的是形式化验证的"思想"（关键路径不变量检查），而非"全套方法"（Isabelle/HOL 全量证明）。

---

## 2. seL4 编码风格层：被 OS-IRON-012 明确禁止借鉴

seL4 的编码风格与 Linux 6.6 基线冲突，被 OS-IRON-012 明确禁止借鉴。本节通过源码级证据说明禁止的合理性。

### 2.1 禁止借鉴一：4 空格缩进

**seL4 源码级证据**：

```c
/* seL4-master/src/object/tcb.c */
bool_t
checkPrio(prio_t prio, tcb_t *tcb) {
    /* ^ 4 空格缩进，非 Tab 8 */
    u32 dom = ksCurDomain;
    if (isRunnable(tcb)) {
        /* ^ 8 空格 = 2 级缩进 */
```

**禁止理由**： 与 OLK-6.6 Tab 8 冲突。Tab 8 让深嵌套在视觉上不可忽视，4 空格则让深嵌套"看起来还行"。

### 2.2 禁止借鉴二：camelCase 命名

**seL4 源码级证据**：

```c
/* seL4-master/src/object/tcb.c */
bool_t checkPrio(prio_t prio, tcb_t *tcb);  /* camelCase 函数名 */
void addToBitmap(u32 dom, u32 prio);          /* camelCase 函数名 */
void removeFromBitmap(u32 dom, u32 prio);     /* camelCase 函数名 */

/* seL4-master/include/api/types.h */
typedef word_t prio_t;           /* camelCase 类型名（prio） */
typedef uint64_t ticks_t;        /* camelCase 类型名（ticks） */
```

**禁止理由**： 与 OLK-6.6 snake_case 冲突。seL4 的 camelCase 源于 Haskell 形式化传统（Haskell 函数名是 camelCase），但 C/Unix 生态主流是 snake_case。

### 2.3 禁止借鉴三：重度 typedef

**seL4 源码级证据**：

```c
/* seL4-master/include/api/types.h —— 重度 typedef */
typedef word_t prio_t;                        /* typedef 基本类型 */
typedef uint64_t ticks_t;                     /* typedef 基本类型 */
typedef struct cap_transfer cap_transfer_t;   /* typedef 结构体 */
typedef word_t exception_t;                   /* typedef 枚举为 word_t */
typedef struct syscall_error syscall_error_t; /* typedef 结构体 */
typedef word_t syscall_error_type_t;          /* typedef 基本类型 */

/* seL4-master/include/api/failures.h —— 枚举 typedef */
enum exception {
    EXCEPTION_NONE,
    EXCEPTION_FAULT,
    EXCEPTION_LOOKUP_FAULT,
    EXCEPTION_SYSCALL_ERROR,
    EXCEPTION_PREEMPTED
};
typedef word_t exception_t;  /* 枚举被 typedef 为 word_t，隐藏类型信息 */
```

**禁止理由**： 与 OLK-6.6 最小 typedef（5 种例外）冲突。seL4 的重度 typedef 隐藏类型信息——`exception_t` 实际是 `word_t`（即 unsigned long），但读者无法从类型名得知这一点。OLK-6.6 要求 `enum exception` 直接使用，不 typedef。

### 2.4 禁止借鉴四：`#pragma once`

**seL4 源码级证据**：

```c
/* seL4-master/include/api/types.h */
#pragma once    /* 非 #ifndef guard */

/* seL4-master/include/api/failures.h */
#pragma once    /* 非 #ifndef guard */

/* seL4-master/libsel4/include/sel4/errors.h */
#pragma once    /* 非 #ifndef guard */
```

**禁止理由**： `#pragma once` 是编译器扩展，非 C 标准。OLK-6.6 使用 `#ifndef _XXX_H` / `#define _XXX_H` / `#endif` 标准头文件保护，兼容所有编译器。

### 2.5 禁止借鉴五：enum 错误处理

**seL4 源码级证据**：

```c
/* seL4-master/libsel4/include/sel4/errors.h —— 枚举错误码 */
typedef enum {
    seL4_NoError = 0,
    seL4_InvalidArgument,
    seL4_InvalidCapability,
    seL4_IllegalOperation,
    seL4_RangeError,
    seL4_AlignmentError,
    seL4_FailedLookup,
    seL4_TruncatedMessage,
    seL4_DeleteFirst,
    seL4_RevokeFirst,
    seL4_NotEnoughMemory,
    seL4_NumErrors
} seL4_Error;

/* seL4-master/include/api/failures.h —— exception_t 枚举 + 全局错误状态 */
typedef word_t exception_t;
extern syscall_error_t current_syscall_error;  /* 全局错误状态 */
extern seL4_Fault_t current_fault;              /* 全局错误状态 */
extern lookup_fault_t current_lookup_fault;     /* 全局错误状态 */
```

**禁止理由**： 与 OLK-6.6 负 errno + goto 集中出口冲突。seL4 的错误处理：
- 使用枚举错误码（`seL4_Error` / `exception_t`）而非负 errno
- 使用全局变量（`current_syscall_error`）传递错误细节，而非函数返回值
- 使用 `EXCEPTION_SYSCALL_ERROR` 等枚举返回，而非 `return -EINVAL`

OLK-6.6 的错误处理：
- 使用负 errno（`-EINVAL` / `-ENOMEM` / `-EBUSY`）
- 错误细节通过函数返回值传递，而非全局变量
- 使用 `goto out_free_xxx:` 集中出口释放资源

seL4 的全局错误状态模型在 SMP 场景下需要 per-CPU 变量，增加复杂度；OLK-6.6 的返回值模型天然无此问题。

---

## 3. P0-CRITICAL：ES-SEL4 数量三重冲突

本次审查发现 agent-linux 在 seL4 借鉴范围声明上存在 **P0-CRITICAL 级别的数量三重冲突**——同一项目内的不同文档对"借鉴了多少项 seL4 工程思想"给出三个不同的数字。

### 3.1 冲突三源

| 来源文档 | 声明数量 | 借鉴范围 | 文档位置 |
|---------|---------|---------|---------|
| **开源手册 + SSoT 注册表** | **5 项** | ES-SEL4-1~5（仅架构层） | `00-engineering-standards-handbook.md` OS-IRON-012 + `09-ssot-registry.md` 第 89 行 + `04-engineering-philosophy.md` 第 591 行 + `05-development-process.md` 第 1831/1837/1839/1864/1869/2098 行 |
| **闭源总纲正文 + 附录 D 标题** | **10 项** | ES-SEL4-1~10（架构层 + P2 增强） | `agent-linux基本工程标准规范.md` 目录第 37 行"附录 D ES-SEL4-1~10 工程思想借鉴映射" + §12.5/§12.6/§12.8 |
| **闭源研究文档** | **54 项** | ES-SEL4-01~54（全量研究范围） | `20-archive/reviews/_research_0.2.5/01-sel4-deep-analysis.md` 第 10/32/95-105/235-259 行 |

### 3.2 冲突本质分析

这三个数字并非简单的矛盾，而是**三个不同作用域的混淆**：

1. **5 项（ES-SEL4-1~5）**——架构层**强制借鉴**范围。这是 OS-IRON-012 铁律定义的、agent-linux 在 0.1.1 阶段必须落地的 seL4 工程思想。

2. **10 项（ES-SEL4-1~10）**——架构层 + P2 增强建议范围。闭源总纲 §12.8 明确说明 ES-SEL4-6~10（接口契约 XML / bitfield codegen / libsel4 独立 / CMake 构建 / 现代构建系统）"不作为架构层强制借鉴，而是作为 P2 增强建议在 1.0.1 阶段增量落地"。

3. **54 项（ES-SEL4-01~54）**——研究文档的全量提炼范围。`20-archive/reviews/_research_0.2.5/01-sel4-deep-analysis.md` 对 seL4 进行 12 维度深度分析，提炼 54 项工程思想，这是**研究产出**，不是**借鉴范围**。

### 3.3 冲突的危害

尽管三个数字有合理的解释（5 = 强制 / 10 = 强制 + P2 / 54 = 研究），但文档没有显式说明这一作用域差异，导致：

1. **审查者困惑**——阅读开源手册的人认为"只借鉴 5 项"，阅读闭源总纲附录 D 标题的人认为"借鉴 10 项"，阅读研究文档的人认为"借鉴 54 项"。三个数字在同一项目内并存，且无统一说明。

2. **SSoT 破坏**——OS-IRON-012 是 SSoT 注册表登记的铁律，声明"ES-SEL4-1~5"；但闭源总纲附录 D 标题是"ES-SEL4-1~10"。两者都是"权威文档"，但数字不一致，破坏 SSoT 原则。

3. **CI 校验困惑**——`05-development-process.md` 第 1837-1864 行的 `check-sel4-scope.sh` 脚本检查"代码中 seL4 借鉴是否仅限 ES-SEL4-1~5 架构层"。如果开发者参考闭源总纲附录 D 认为可以借鉴 ES-SEL4-6~10，CI 脚本将拒绝，但开发者不理解为何被拒。

### 3.4 修复建议

**P0-CRITICAL 修复方案**（0.1.1 立即修复）：

1. **闭源总纲附录 D 标题修正**——将"附录 D ES-SEL4-1~10 工程思想借鉴映射"改为"附录 D seL4 工程思想借鉴映射（ES-SEL4-1~5 强制 + ES-SEL4-6~10 P2 增强）"，显式标注作用域差异。

2. **闭源总纲 §12.5 标题修正**——将"架构层借鉴 seL4（5 项选择性借鉴）"保留，但在表格后增加显式说明："ES-SEL4-6~10 见 §12.8，作为 P2 增强建议在 1.0.1 阶段增量落地，不属于 0.1.1 强制借鉴范围。"

3. **开源手册 OS-IRON-012 补充说明**——在"seL4 借鉴仅限架构层（ES-SEL4-1~5）"后增加注释："ES-SEL4-6~10 作为 P2 增强建议在 1.0.1 阶段增量落地，详见闭源总纲 §12.8。研究文档 `20-archive/reviews/_research_0.2.5/01-sel4-deep-analysis.md` 提炼的 54 项工程思想是研究产出，不是借鉴范围。"

4. **SSoT 注册表补充登记**——在 `09-ssot-registry.md` 中显式登记三个作用域：ES-SEL4-1~5（强制）/ ES-SEL4-6~10（P2 增强）/ ES-SEL4-01~54（研究产出），消除数字歧义。

---

## 4. seL4 工程思想综合评分

基于上述源码级证据，对 seL4 工程思想进行评分：

| 维度 | 评分 | 证据 |
|------|------|------|
| 架构层借鉴合理性（ES-SEL4-1~5） | 88/100 | 5 项借鉴均有源码支撑，但服务用户态化（ES-SEL4-3）落地风险高 |
| 编码风格层禁止合理性 | 95/100 | 5 项禁止均有源码支撑，与 OLK-6.6 冲突明确 |
| 借鉴范围声明一致性 | 35/100 | 三重冲突（5/10/54），P0-CRITICAL |
| 形式化验证可行性 | 60/100 | 全量形式化验证不现实，建议仅关键路径 |
| **综合** | **70/100** | **B-**（被 P0-CRITICAL 拖累） |

---

## 5. 对 agent-linux 的启示

### 5.1 应保持的对齐

agent-linux 在以下方面已正确对齐 seL4 借鉴：

- ES-SEL4-1~5 架构层借鉴选择合理（极简原则 / capability / 服务用户态化 / 消息传递 IPC / 形式化验证）
- 编码风格层 5 项禁止借鉴正确（4 空格 / camelCase / 重度 typedef / #pragma once / enum 错误处理）
- [SC] 共享契约层的 capability 操作（7 种）与 seL4 同源

### 5.2 应修复的冲突

- **P0-CRITICAL：ES-SEL4 数量三重冲突**——5/10/54 三个数字必须显式标注作用域，消除歧义（详见 §3.4 修复方案）。
- **P1-MAJOR：附录 D 标题与正文矛盾**——附录 D 标题说"ES-SEL4-1~10"，但 §12.6 OS-IRON-012 说"ES-SEL4-1~5"。

### 5.3 建议的长期演进

- **形式化验证范围明确化**——1.0.1 阶段应明确形式化验证的范围（全量 / 关键路径 / 仅 corekern），而非笼统说"形式化验证驱动"。
- **capability + LSM 融合模型论证**——agent-linux 同时使用 capability（seL4 借鉴）和 LSM（Linux 6.6 原生），两者的交互模型需要在 1.0.1 阶段论证，避免权限检查双重化。

---

> **下一步**：阅读 [03-six-dimension-problem-check.md](./03-six-dimension-problem-check.md) 了解六维度问题检查。
