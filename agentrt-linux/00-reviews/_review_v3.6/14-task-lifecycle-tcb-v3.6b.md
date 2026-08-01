SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 14 — 任务生命周期与 TCB 等价物（v3.6b 深度对比）

> **文档定位**：agentrt-linux 内核设计深度对比研究 · 第二轮 · 维度 6
> **对比基准**：openEuler kernel-OLK-6.6 · seL4-master · Airymax agentrt-linux
> **最后更新**：2026-07-31
> **方法论**：逐字节阅读三项目源码，所有引用标注文件路径+行号，严禁编造

---

## 0. 摘要

本报告对比三项目的任务生命周期与 TCB 等价物。openEuler 以 `struct task_struct` 的 `__state` 位图（[sched.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/sched.h) L813）+ `copy_process`/`do_exit` 隐式驱动生命周期；seL4 以显式 `invokeTCB_Suspend`/`invokeTCB_Resume`/`invokeTCB_ThreadControl` cap 操作管理 TCB；Airymax 以 [airy_task_lifecycle.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/taskflow/airy_task_lifecycle.c) L68-140 的 8 态显式状态机 + 合法转移表驱动生命周期。核心发现：N11（无显式 suspend/resume API，`STOPPED→READY` 借用 SIGCONT 路径）、N18（[airy_cap_rotate.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_rotate.c) 单行委托可内联）。正面发现：8 态显式状态机比 openEuler 隐式位图更易审计。

---

## 1. 对比基准

### 1.1 openEuler OLK-6.6 task_struct 隐式 state 位图

openEuler 沿用 Linux 进程模型，`struct task_struct` 承载全部任务状态：

| 要素 | 位置 | 行号 | 说明 |
|------|------|------|------|
| `struct task_struct` | [sched.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/sched.h) | L805 | 进程描述符起点 |
| `__state` | sched.h | L813 | `unsigned int`，TASK_RUNNING/INTERRUPTIBLE/UNINTERRUPTIBLE 等位图 |
| `prio` | sched.h | L846 | 调度优先级 |
| `policy` | sched.h | L890 | SCHED_NORMAL/FIFO/RR/BATCH/IDLE/DEADLINE |
| `exit_state` | sched.h | L938 | EXIT_ZOMBIE/EXIT_DEAD，退出阶段标志 |
| `TASK_RUNNING` | sched.h | L94 | 0x00000000（就绪/运行共用） |
| `TASK_INTERRUPTIBLE` | sched.h | L95 | 0x00000001 |
| `TASK_UNINTERRUPTIBLE` | sched.h | L96 | 0x00000002 |
| `EXIT_DEAD` | sched.h | L100 | 0x00000010 |
| `EXIT_ZOMBIE` | sched.h | L101 | 0x00000020 |
| `wake_up_process` 声明 | sched.h | L2137 | `extern int wake_up_process(struct task_struct *)` |

生命周期驱动点：

| 阶段 | 位置 | 行号 | 说明 |
|------|------|------|------|
| fork | [fork.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/fork.c) | L2365 | `copy_process` 复制 task_struct |
| clone 入口 | fork.c | L3020 | `kernel_clone`（OLK-6.6 无 `_do_fork`） |
| exit | [exit.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/exit.c) | L809 | `do_exit` 主退出流程 |
| exit_state=ZOMBIE | exit.c | L739 | `tsk->exit_state = EXIT_ZOMBIE` |
| EXIT_DEAD | exit.c | L274 | `leader->exit_state = EXIT_DEAD`（de-thread） |
| do_task_dead | exit.c | L924 | 调度切走后永不返回 |
| 唤醒 | [core.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/core.c) | L4082/L4363 | `try_to_wake_up`/`wake_up_process` |

**特征**：`__state` 是位图，`TASK_RUNNING` 同时表示"就绪"和"运行"两种语义（由 `on_rq` 区分）；suspend/resume 没有显式 API，而是通过 `SIGSTOP`/`SIGCONT` 信号路径间接实现（`do_signal_stop` 改 `__state`，`SIGCONT` 经 `try_to_wake_up` 回到 `TASK_RUNNING`）。状态空间是隐式的——合法转移由各调用点的 `if` 散落约束，无集中表。

### 1.2 seL4 TCB 显式 cap 操作

seL4 的 TCB 是内核对象，生命周期由 cap invocation 显式驱动：

| 函数 | 位置 | 行号 | 说明 |
|------|------|------|------|
| `decodeTCBInvocation` | [tcb.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/tcb.c) | L848 | 解码 TCB 调用入口 |
| `TCBSuspend` case | tcb.c | L865-869 | 转入 `invokeTCB_Suspend` |
| `TCBResume` case | tcb.c | L871-874 | 转入 `invokeTCB_Resume` |
| `invokeTCB_Suspend` | tcb.c | L1690 | 调用 `suspend()`（置 Blocked） |
| `invokeTCB_Resume` | tcb.c | L1696 | 调用 `restart()`（置 Runnable） |
| `invokeTCB_ThreadControlCaps` | tcb.c | L1724 | cap 字段控制（fault handler 等） |
| `invokeTCB_ThreadControl` | tcb.c | L1786 | 参数/优先级/栈基址控制 |
| `invokeTCB_ThreadControlSched` | tcb.c | L1862 | 调度上下文（SC）绑定/解绑 |

**机制**：seL4 不用位图，而是显式 `ThreadState` 枚举（Runnable/Blocked/Restarted 等）。suspend/resume 是一等公民 cap 操作——`invokeTCB_Suspend`（[tcb.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/tcb.c) L1690）直接调 `suspend()`，`invokeTCB_Resume`（L1696）直接调 `restart()`，无信号中介。TCB 的删除通过 cap revocation（CNode Revoke/Delete）实现，不存在"zombie 再 reap"的两阶段退出。

### 1.3 Airymax 8 态显式状态机

**任务描述符** — [airy_task_desc.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/taskflow/airy_task_desc.c)：

| 要素 | 行号 | 说明 |
|------|------|------|
| `airy_task_desc_init` | L19 | 描述符初始化入口 |
| magic 校验 | L29-33 | `desc->magic != 0 && != AIRY_TASK_MAGIC` → 拒绝（腐化检测） |
| `magic = AIRY_TASK_MAGIC` | L37 | 0x41475453（'AGTS'） |
| `prio = AIRY_PRIO_MAX/2` | L38 | 默认中位优先级 |
| `sched_policy = AIRY_SCHED_POLICY_EEVDF` | L40 | 默认 EEVDF |
| `state = AIRY_AGENT_INACTIVE` | L42 | 初始态 |
| `airy_task_desc_valid` | L48 | magic 校验接口 |

**状态机** — [airy_task_lifecycle.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/taskflow/airy_task_lifecycle.c)：

| 要素 | 行号 | 说明 |
|------|------|------|
| `airy_task_state_names[]` | L27-36 | 8 态名表：INACTIVE/SPAWNING/READY/RUNNING/BLOCKED/STOPPING/STOPPED/DEAD |
| `airy_task_state_name` | L39 | 状态名查询（越界返回 "UNKNOWN"） |
| `airy_task_state_transition` | L68 | 状态转移校验入口 |
| DEAD 守卫 | L79-80 | DEAD 仅可转 INACTIVE（reap 回收） |
| 合法转移表 | L82-136 | 集中 switch，逐 next-state 列出合法 cur-state |
| `*state = next` | L138 | 校验通过后提交 |

合法转移表（[airy_task_lifecycle.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/taskflow/airy_task_lifecycle.c) L82-136 注释 L50-63 文档化）：

```
INACTIVE → SPAWNING   (fork)
SPAWNING → READY      (exec complete)
READY    → RUNNING    (scheduler picks)
RUNNING  → BLOCKED    (IPC/IO wait)
BLOCKED  → READY      (wakeup)
RUNNING  → STOPPING   (Micro-Supervisor SIGSTOP, abnormal)
BLOCKED  → STOPPING   (Micro-Supervisor SIGSTOP, abnormal)
STOPPING → STOPPED    (SIGSTOP takes effect)
STOPPED  → READY      (SIGCONT, adjudicated recovery)
STOPPED  → DEAD       (adjudicated termination)
RUNNING  → DEAD       (kill SIGKILL, fatal)
DEAD     → INACTIVE   (waitpid, recycling)
```

---

## 2. 关键发现

### 2.1 【发现 1】无显式 suspend/resume API，STOPPED→READY 借用 SIGCONT 路径

**现状**：[airy_task_lifecycle.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/taskflow/airy_task_lifecycle.c) L68-140 的状态机定义了 `RUNNING/BLOCKED → STOPPING → STOPPED → READY` 这条"冻结-恢复"路径，但仓库内**无 `airy_task_suspend`/`airy_task_resume` 显式 API**——`STOPPED → READY` 的转移（L94 注释 "SIGCONT, adjudicated recovery"）依赖信号路径驱动，而非 seL4 风格的一等公民 cap 操作。Micro-Supervisor 若要冻结 agent，需通过 `SIGSTOP` 信号间接触发 `RUNNING → STOPPING`，恢复时再经 `SIGCONT` 间接触发 `STOPPED → READY`。

**参考**：seL4 [tcb.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/tcb.c) L1690 `invokeTCB_Suspend`/L1696 `invokeTCB_Resume` 是显式 cap invocation——用户态 supervisor 直接发 `TCBSuspend`/`TCBResume` 调用即可冻结/恢复线程，无信号中介，权限由 endpoint cap 的 `canSend`/badge 精确控制。openEuler 同样无 `suspend` 系统调用，但 openEuler 的目标是通用服务器，进程冻结不是核心场景；Airymax 作为 agent RT 内核，agent 冻结是 Micro-Supervisor 的核心执法手段，借用信号路径会带来两个问题：(1) 信号递送有延迟窗口，agent 可能在 `STOPPING → STOPPED` 之间继续执行 IPC；(2) `SIGSTOP`/`SIGCONT` 的权限模型是 UID/CAP_KILL，与 Airymax 的 capability/Badge 模型不对齐。

**风险**：M2 IPC 集成时，Micro-Supervisor 需在检测到 agent 异常后"立即冻结其 IPC ring"。当前路径需先发 `SIGSTOP`、等调度器切入信号处理，时序窗口内 agent 仍可发 IPC，与 [airy_ipc_freeze.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_ipc_freeze.c) L37-50 的 ring freeze（smp_store_release 立即生效）不同步。

**建议**：M2 增加 `airy_task_suspend(agent_id)`/`airy_task_resume(agent_id)` 显式 API，内部直接调 `airy_task_state_transition` 推进状态机 + 同步触发 `airy_ipc_freeze_ring`，使状态转移与 ring freeze 在同一临界区原子完成。短期（M0/M1）可文档化"借用 SIGSTOP/SIGCONT 路径"的临时决策。对应 N11。

**优先级**：P2 · 工作量 4h · 风险中（涉及与信号路径的协调）

### 2.2 【发现 2】airy_cap_rotate.c 单行委托可内联

**现状**：[airy_cap_rotate.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_rotate.c) 全文件 38 行，唯一函数 `airy_cap_rotate`（L33-37）除一句 `pr_debug_ratelimited`（L35-36）外，仅 L37 `return airy_cap_derive(agent_id, agent_id, AIRY_CAP_OP_ROTATE, 0);` 单行委托。整个 `.c` 文件 + 编译单元 + EXPORT_SYMBOL 的开销，相对一个内联函数收益偏低。

**参考**：seL4 的 badge rotation 同样是 `airy_cap_derive` 的子情况，但 seL4 直接在 `decodeTCBInvocation`（[tcb.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/tcb.c) L848）的 switch 内联处理，无独立翻译单元。openEuler 的 capability 类操作（`cap_set` 等）也是 `static inline` 头文件内联。

**建议**：将 `airy_cap_rotate` 移至 [airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap.h) 作为 `static inline`，保留 `airy_cap_rotate.c` 的 `pr_debug_ratelimited` 作为可选日志层（或一并内联）。这减少一个编译单元、缩短调用链（消除一次函数调用 + EXPORT_SYMBOL 查找）。`pr_debug_ratelimited` 在内联函数中同样可用。对应 N18。

**优先级**：P2 · 工作量 0.5h · 风险低（纯重构，无语义变更）

### 2.3 正面发现：8 态显式状态机比 openEuler 隐式位图更易审计

**现状**：[airy_task_lifecycle.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/taskflow/airy_task_lifecycle.c) L82-136 的 `airy_task_state_transition` 用集中 switch 列出全部 12 条合法转移，非法转移统一返回 `-EINVAL`。注释 L50-63 同步文档化转移语义（fork/exec/wakeup/SIGSTOP/SIGCONT/kill/reap）。

**对比**：openEuler 的 `__state` 位图（[sched.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/sched.h) L813）合法转移由 `try_to_wake_up`（[core.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/core.c) L4082）、`do_signal_stop`、`do_exit`（[exit.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/exit.c) L809）等十余处散落约束，无集中表，审计需交叉比对多文件。

**价值**：对 agent RT 内核，"哪些状态转移合法"是安全审计的核心问题。集中表使审计可在一屏内完成（L82-136 共 55 行），且 `airy_task_state_name`（L39）为可观测性提供字符串接口——openEuler 需用 `task_state_to_char`（'R/S/D/T/Z/X'）单字符表示，可读性差。这是 Airymax 在可审计性上**优于** openEuler 的设计点，值得保留并向其他子系统推广（如 capability 状态、IPC ring freeze 状态也可考虑集中转移表）。

### 2.4 正面发现：magic 腐化检测

[airy_task_desc.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/taskflow/airy_task_desc.c) L29-33 的 magic 校验（`desc->magic != 0 && != AIRY_TASK_MAGIC` → `-EINVAL`）能检测两类问题：(1) 未初始化内存（magic=0 允许 re-init，是宽容设计）；(2) 内存腐化（其他值直接拒绝）。`AIRY_TASK_MAGIC = 0x41475453`（'AGTS'，L37 注释）选 ASCII 可读 magic，便于内存转储人工识别。这是 openEuler task_struct 和 seL4 tcb_t 都没有的运行时自检机制。

---

## 3. 改进点清单

| 编号 | 标题 | 优先级 | 现状行号 | 工作量 |
|------|------|--------|----------|--------|
| N11 | 无显式 suspend/resume API，STOPPED→READY 借用 SIGCONT 路径 | P2 | [airy_task_lifecycle.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/taskflow/airy_task_lifecycle.c) L68-140 | 4h |
| N18 | airy_cap_rotate.c 单行委托可内联到 airy_cap.h | P2 | [airy_cap_rotate.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_rotate.c) L33-37 | 0.5h |
| — | 8 态显式状态机集中转移表，易审计（正面） | — | [airy_task_lifecycle.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/taskflow/airy_task_lifecycle.c) L82-136 | — |
| — | magic 腐化检测 + ASCII 可读 magic（正面） | — | [airy_task_desc.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/taskflow/airy_task_desc.c) L29-37 | — |

---

## 4. 小结

Airymax 的 8 态显式状态机（[airy_task_lifecycle.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/taskflow/airy_task_lifecycle.c) L68-140）在可审计性上明显优于 openEuler 的隐式 `__state` 位图，也优于 seL4 的"状态枚举 + 散落转移约束"——集中合法转移表让安全审计可一屏完成。magic 腐化检测（[airy_task_desc.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/taskflow/airy_task_desc.c) L29-33）是额外自检亮点。主要差距是 N11：suspend/resume 缺显式 API，M2 IPC 集成时需补齐以与 ring freeze 原子协同；N18 是低收益单行委托文件，内联即可。两发现均为 P2，不阻断 M0/M1。
