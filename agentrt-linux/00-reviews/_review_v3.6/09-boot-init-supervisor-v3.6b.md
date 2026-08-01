SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 09 — 启动初始化与 Micro-Supervisor 接线（v3.6b 深度对比）

> **文档定位**：agentrt-linux 内核设计深度对比研究 · 第二轮 · 维度 1
> **对比基准**：openEuler kernel-OLK-6.6 · seL4-master · Airymax agentrt-linux
> **最后更新**：2026-07-31
> **方法论**：逐字节阅读三项目源码，所有引用标注文件路径+行号，严禁编造

---

## 0. 摘要

本报告对比三项目的启动初始化序列与 Micro-Supervisor 接线方式。openEuler 采用集中式 `start_kernel` 串行调用 ~60 个 init 函数；seL4 采用 `init_kernel` + `create_root_cnode` + `create_initial_thread` 三阶段显式 boot；Airymax 复用 Linux initcall 机制，通过分散的 `late_initcall` / `security_initcall` 拼装子系统。核心发现：Airymax 的 `airy_kern_api_init` 仅串联 `airy_locking_init()`，其余 7 个 corekern 子系统 init 未统一调度（N1）；补充 LSM 钩子缺 Badge 校验（N2）；`mmap_addr`/`file_mprotect` 未对接 cap_array 白名单（N20/N21）。

---

## 1. 对比基准

### 1.1 openEuler OLK-6.6 启动序列

openEuler 沿用 Linux 标准启动模型，[init/main.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/init/main.c) L888-889 定义 `start_kernel(void)`，该函数串行调用约 60 个初始化函数，关键节点：

| 调用 | 位置 | 作用 |
|------|------|------|
| `setup_arch` | L912 | 架构相关初始化 |
| `mm_init` | — | 内存子系统初始化 |
| `sched_init` | L959 | 调度器初始化 |
| `security_init` | L1071 | LSM 框架初始化 |
| `rest_init` | L1090 | 创建 init 线程，进入 `cpu_startup_entry` |

LSM 初始化在 [security/security.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/security/security.c) L436 `security_init(void)` 中完成，L456 调用 `ordered_lsm_init()` 按 `CONFIG_LSM` 顺序加载各 LSM 模块。各 LSM 通过 [include/linux/lsm_hooks.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/lsm_hooks.h) L131 的 `DEFINE_LSM(lsm)` 宏将 `lsm_info` 结构放入 `.lsm_info.init` section，由 `ordered_lsm_init` 统一遍历。

**特征**：集中式、显式顺序、单一入口 `start_kernel`，所有子系统初始化在同一函数内可见，便于审计启动依赖。

### 1.2 seL4 启动序列

seL4 采用微内核显式 boot，[src/kernel/boot.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/boot.c) 关键阶段：

| 函数 | 行号 | 作用 |
|------|------|------|
| `init_kernel` | L300 | 内核状态归零、初始化全局 |
| `create_root_cnode` | L278 | 创建根 CNode（L288 `write_slot` 写入 root cap） |
| `create_initial_thread` | L496 | 创建初始线程（root task），设置 PC/SP |

**特征**：boot 代码用 `BOOT_CODE` 宏标记，编译期保证仅在启动阶段链接；无 initcall 机制，所有 boot 步骤在同一 `try_init_kernel` 调用链中显式完成；root CNode 与 initial thread 在 boot 阶段就绑定 capability，无运行时再注册。

### 1.3 Airymax 启动序列

Airymax 复用 Linux initcall 机制，启动入口分散在三个 `late_initcall` + 一个 `security_initcall`：

| 文件 | 入口函数 | 行号 | initcall 级别 | 作用 |
|------|----------|------|--------------|------|
| [airy_core.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/init/airy_core.c) | `airy_core_init` | L18/L28 | late | 打印 boot banner |
| [airy_kern_api.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/api/airy_kern_api.c) | `airy_kern_api_init` | L24/L48 | late | corekern API 初始化 |
| [airy_superv_init.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/superv/airy_superv_init.c) | `airy_superv_init` | L31/L57 | late | Micro-Supervisor 接线 |
| airy_die_notify.c | `airy_die_notify_init` | — | security | die_notifier 注册 |

**LSM 初始化路径**：airy_lsm.c 通过 `DEFINE_LSM(airy)` 注册 5 个核心钩子（task_kill/file_open/io_uring_cmd 等，第一轮报告 02 已覆盖）；airy_superv_lsm.c L121 `airy_superv_register_hooks()` 通过 `security_add_hooks()` 将 5 个补充钩子追加到同一 "airy" LSM blob。

---

## 2. Micro-Supervisor 接线深度分析

### 2.1 接线时序

```
security_initcall:
  airy_die_notify_init() → register_die_notifier(airy_die_notify_block)

late_initcall (顺序由链接决定，非显式):
  airy_core_init()         → pr_info banner
  airy_kern_api_init()     → airy_locking_init()  [仅此一个]
  airy_superv_init()       → airy_superv_register_hooks() → security_add_hooks(5 hooks)
```

[airy_superv_init.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/superv/airy_superv_init.c) L39 调用 `airy_superv_register_hooks()`，该函数在 [airy_superv_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_superv_lsm.c) L121-128 定义，L123 调用 `security_add_hooks()` 将 `airy_superv_hooks[]`（L105-111，5 个钩子）注册到 "airy" LSM。

### 2.2 五个补充 LSM 钩子

| 钩子 | 函数 | 行号 | 校验逻辑 |
|------|------|------|----------|
| `task_fix_setuid` | `airy_superv_task_fix_setuid` | L35-45 | L41 `agent_state==STOPPED→-EPERM` |
| `mmap_addr` | `airy_superv_mmap_addr` | L48-58 | L54 `addr>=TASK_SIZE→-EACCES` |
| `file_mprotect` | `airy_superv_file_mprotect` | L61-73 | L69 `W^X→-EACCES` |
| `capset` | `airy_superv_capset` | L76-88 | L84 `agent_state==STOPPED→-EPERM` |
| `capable` | `airy_superv_capable` | L91-102 | L98 `agent_state==STOPPED→-EPERM` |

### 2.3 与 seL4 handleFault 的对比

seL4 的故障隔离通过 `sendFaultIPC` 将 fault 发送到线程的 faultEP，由 supervisor 接收处理（详见报告 16）。Airymax 的 Micro-Supervisor 模型借鉴此语义：内核侧（Micro）冷酷执法——`agent_state==STOPPED` 即拒绝；用户侧（Macro）温情裁决——通过 eventfd 通知 Macro-Supervisor 做策略决策。

但当前实现存在不对称：`task_fix_setuid`/`capset`/`capable` 三个钩子仅检查 `agent_state`，不校验 Badge epoch/random tag，与第一轮 P1-4（task_kill/file_open 缺 Badge 校验）同源。`mmap_addr`/`file_mprotect` 则完全未查 `agent_state`，仅做地址/W^X 检查，未对接 cap_array 的 agent 地址范围白名单。

---

## 3. 关键发现

### 3.1 【发现 1】启动初始化分散，corekern 7 子系统 init 未串联

**现状**：[airy_kern_api.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/api/airy_kern_api.c) L24-45 `airy_kern_api_init()` 注释声称"Aggregates initialisation of the corekern subdirectories (api, sched, ipc, taskflow, memory, time, object, locking, irq, bpf)"，但函数体 L37 仅调用 `airy_locking_init()`，其余 9 个子系统的 init 函数均未调用。

**参考**：openEuler [init/main.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/init/main.c) L889 `start_kernel` 在单一函数内显式串联所有子系统 init，依赖关系一目了然。seL4 [boot.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/boot.c) L278/L300/L496 三阶段 boot 同样显式。

**风险**：当前各子系统 init 多为自测占位（如 airy_locking_init 仅 self-test），缺失串联暂不致命。但 M2 起 ipc/taskflow/memory 真正实现后，若仍依赖 initcall 链接顺序而非显式调用，将产生难以排查的初始化顺序 bug。

**建议**：在 `airy_kern_api_init` 中显式调用各子系统 init，按依赖排序：locking → memory → object → time → irq → taskflow → ipc → bpf。对应 N1。

**优先级**：P1 · 工作量 4h · 风险低

### 3.2 【发现 2】补充 LSM 钩子 Badge 校验不对称

**现状**：[airy_superv_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_superv_lsm.c) 中三个钩子（L41 `task_fix_setuid`、L84 `capset`、L98 `capable`）仅检查 `sec->agent_state == AIRY_AGENT_STOPPED`，不校验 Badge epoch/random tag。另两个钩子（L48 `mmap_addr`、L61 `file_mprotect`）连 `agent_state` 都不查。

**参考**：第一轮报告 02 已发现 airy_lsm.c 的 task_kill/file_open 同样缺 Badge 校验（P1-4）。io_uring_cmd 路径有完整 5-phase slowpath（airy_cap_check.c L191-260）。补充钩子应与核心钩子保持一致的校验深度。

**风险**：一个 `STOPPED` 但 Badge 已 rotate 的 agent 仍可通过 `capset`/`capable` 提权；`mmap_addr` 仅挡 kernel-space 地址，未挡 cap_array 未授权的用户空间范围。

**建议**：三钩子增加 `airy_cap_has_perm()` 调用（已存在于 airy_cap_check_superv.c）；`mmap_addr`/`file_mprotect` 对接 cap_array 的 agent 地址白名单与 PROT_EXEC 权限。对应 N2/N20/N21。

**优先级**：P1 · 工作量 4h+3h+3h · 风险中（需避免 fastpath 性能回归）

### 3.3 【发现 3】late_initcall 时机晚于 fs/sched 等

**现状**：`airy_core_init`/`airy_kern_api_init`/`airy_superv_init` 均为 `late_initcall`，在 fs/sched/etc 之后执行。

**参考**：openEuler LSM 通过 `security_init`（init/main.c L1071，早于 late_initcall）加载；seL4 boot 在内核启动前完成全部初始化。

**风险**：若 agent 在 late_initcall 之前触发（如早期 syscall），airy_lsm 钩子已注册但 airy_superv 补充钩子未注册，导致安全检查不完整。

**建议**：评估将 `airy_superv_register_hooks` 移至 `security_initcall` 或并入 airy_lsm.c 的 `DEFINE_LSM(airy).init`，使 10 个钩子原子注册。对应 N22。

**优先级**：P2 · 工作量 1h(文档评估) · 风险低

---

## 4. 改进点清单

| 编号 | 标题 | 优先级 | 现状行号 | 工作量 |
|------|------|--------|----------|--------|
| N1 | airy_kern_api_init 仅串联 locking_init，7 子系统 init 未统一调度 | P1 | [airy_kern_api.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/api/airy_kern_api.c) L37 | 4h |
| N2 | airy_superv_lsm.c 5 补充钩子缺 Badge 校验 | P1 | [airy_superv_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_superv_lsm.c) L41/L84/L98 | 4h |
| N20 | mmap_addr 未对接 cap_array 地址白名单 | P2 | [airy_superv_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_superv_lsm.c) L54 | 3h |
| N21 | file_mprotect 仅 W^X 检查，未对接 cap_array PROT_EXEC | P2 | [airy_superv_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_superv_lsm.c) L69 | 3h |
| N22 | late_initcall 时机晚于 fs/sched/etc | P2 | [airy_kern_api.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/api/airy_kern_api.c) L48 | 1h(文档) |

---

## 5. 与第一轮的关系

第一轮报告 02 覆盖 airy_lsm.c 的 5 个核心钩子（task_kill/file_open/io_uring_cmd 等）。本报告覆盖 airy_superv_lsm.c 的 5 个补充钩子（task_fix_setuid/mmap_addr/file_mprotect/capset/capable），两者共同构成 Micro-Supervisor 的 10 钩子安全面。N2 与第一轮 P1-4 同源（Badge 校验不对称），建议合并修复。

## 6. 小结

Airymax 复用 Linux initcall 机制是合理的工程选择（避免改主线 boot 序列，符合 ALK 策略），但 `airy_kern_api_init` 的"占位串联"在 M2 后必须补齐。Micro-Supervisor 的 5+5 钩子分工设计清晰，但 Badge 校验不对称是跨两轮的系统性问题，应在 M2 前统一收敛。
