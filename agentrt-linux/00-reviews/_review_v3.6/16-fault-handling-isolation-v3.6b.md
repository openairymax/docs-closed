SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 16 — 故障处理与隔离（v3.6b 深度对比）

> **文档定位**：agentrt-linux 内核设计深度对比研究 · 第二轮 · 维度 8
> **对比基准**：openEuler kernel-OLK-6.6 · seL4-master · Airymax agentrt-linux
> **最后更新**：2026-07-31
> **方法论**：逐字节阅读三项目源码，所有引用标注文件路径+行号，严禁编造

---

## 0. 摘要

本报告对比三项目的故障处理与隔离机制。openEuler 用 `die_chain` + `panic_notifier_list` 双 atomic notifier 链（[notifier.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/notifier.c) L581/L149）+ `oops_begin/oops_end`（[dumpstack.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/arch/x86/kernel/dumpstack.c) L351/L377）驱动 OOPS/panic 路径；seL4 用 `handleFault` + `sendFaultIPC`（[faulthandler.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/faulthandler.c) L15/L31）把故障经 endpoint cap 投递给用户态 fault handler，无 handler 则置 Inactive；Airymax 用 [airy_die_notify.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_die_notify.c) 独立 `airy_die_chain`（L29）+ INT_MAX 优先级 die_notifier（L152-155）+ [airy_ipc_freeze.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_ipc_freeze.c) ring 冻结 + [airy_eventfd.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_eventfd.c) 上报 Macro-Supervisor。核心发现：N3（`airy_ipc_ring_for_task` M0 恒返回 NULL，die_notifier freeze 死代码）、N13（die reason 仅映射 4 种）、N14（eventfd 单全局 ctx）。N2（superv_lsm 5 钩子缺 Badge 校验）与报告 09 交叉引用。正面发现：die_notifier 独立链避免污染主线 panic。

---

## 1. 对比基准

### 1.1 openEuler OLK-6.6 die_chain + panic_notifier_list

openEuler 沿用 Linux 双链故障通知：

**die_chain（OOPS/硬件异常）**：

| 要素 | 位置 | 行号 | 说明 |
|------|------|------|------|
| `die_chain` 定义 | [notifier.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/notifier.c) | L581 | `static ATOMIC_NOTIFIER_HEAD(die_chain)` |
| `notify_die` | notifier.c | L583 | L596 `atomic_notifier_call_chain(&die_chain, val, &args)` |
| `register_die_notifier` | notifier.c | L600 | 委托 `atomic_notifier_chain_register`（L149） |
| `enum die_val` | [kdebug.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/arch/x86/include/asm/kdebug.h) | L10-23 | DIE_OOPS/DIE_INT3/DIE_DEBUG/DIE_PANIC/DIE_NMI/DIE_DIE/DIE_KERNELDEBUG/DIE_TRAP/DIE_GPF/DIE_CALL/DIE_PAGE_FAULT/DIE_NMIUNKNOWN（12 种） |
| `notify_die` 声明 | [kdebug.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/kdebug.h) | L20 | 跨架构接口 |
| `register_die_notifier` 声明 | kdebug.h | L17 | — |
| `die()` | [dumpstack.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/arch/x86/kernel/dumpstack.c) | L460 | OOPS 入口 |
| `oops_begin` | dumpstack.c | L351 | L362 自旋 `die_owner`，关中断 |
| `oops_end` | dumpstack.c | L377 | L383 释放 `die_owner`，判 panic |
| `notify_die(DIE_OOPS)` | dumpstack.c | L441 | die() 内调用 |

**panic_notifier_list（panic 阶段）**：

| 要素 | 位置 | 行号 | 说明 |
|------|------|------|------|
| `panic_notifier_list` | [panic.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/panic.c) | L79 | `ATOMIC_NOTIFIER_HEAD(panic_notifier_list)` |
| `panic_early_notifier_list` | panic.c | L80 | 早期通知链 |
| `panic()` | panic.c | L279 | panic 入口 |
| 通知调用 | panic.c | L373 | `atomic_notifier_call_chain(&panic_notifier_list, 0, buf)` |
| `panic_timeout` | panic.c | L67 | 重启超时（CONFIG_PANIC_TIMEOUT） |

**机制**：`die()`（dumpstack.c L460）调 `oops_begin`（L351）抢 `die_owner` + 关中断，`__die` 打印寄存器，`notify_die(DIE_OOPS)` 遍历 `die_chain`；`oops_end`（L377）释放 + 判 `panic_on_oops` 决定是否进 `panic()`。`panic()`（panic.c L279）打印栈 + L373 通知 `panic_notifier_list` + L409 按 `panic_timeout` 重启或 hang。两条链分工：`die_chain` 处理"可恢复 OOPS"，`panic_notifier_list` 处理"不可恢复 panic"。

### 1.2 seL4 handleFault + sendFaultIPC（fault IPC 投递）

seL4 把故障作为一等公民 IPC 事件投递给用户态 fault handler：

| 要素 | 位置 | 行号 | 说明 |
|------|------|------|------|
| `handleFault`（MCS） | [faulthandler.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/faulthandler.c) | L15-22 | 读 `tcbFaultHandler` cap → `sendFaultIPC` → 无 handler 则 `handleNoFaultHandler` |
| `sendFaultIPC`（MCS） | faulthandler.c | L31-52 | cap 为 endpoint_cap → `sendIPC` 带 badge 投递；null_cap → 返回 false |
| `handleFault`（非 MCS） | faulthandler.c | L55-64 | `sendFaultIPC` 失败 → `handleDoubleFault` |
| `sendFaultIPC`（非 MCS） | faulthandler.c | L66-103 | `lookupCap` → endpoint_cap 且 canSend+canGrant → `sendIPC`；否则 EXCEPTION_FAULT |
| `handleNoFaultHandler`/`handleDoubleFault` | faulthandler.c | L146/L149 | 打印故障 + L172 `setThreadState(Inactive)` |
| `handleFaultReply` | [faults.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/api/faults.c) | L114 | 回复处理（CapFault/UnknownSyscall/UserException/Timeout/DebugException） |
| `setMRs_fault` | faults.c | L191 | 故障信息编码进 MR（Message Registers） |
| `print_fault` | faulthandler.c | L107-142 | `CONFIG_PRINTING` 下打印故障类型 |

**机制**：seL4 故障类型有 CapFault/VMFault/UnknownSyscall/UserException/Timeout/DebugException（[faults.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/api/faults.c) L122-188 switch）。`handleFault`（faulthandler.c L15）从 TCB 的 `tcbFaultHandler` 槽取 endpoint cap，`sendFaultIPC`（L31）校验 cap 类型 + badge + canGrant，调 `sendIPC` 把故障信息（编码在 MR）投递到 fault handler endpoint，用户态 supervisor 阻塞接收并裁决。无 handler（null cap）则 `handleNoFaultHandler`（L146）置线程 Inactive——这是"内核不裁决故障，只投递"的微内核哲学。

### 1.3 Airymax die_notify + ipc_freeze + eventfd 三段式

**die 通知** — [airy_die_notify.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_die_notify.c)（166 行）：

| 要素 | 行号 | 说明 |
|------|------|------|
| `airy_die_chain` | L29 | `ATOMIC_NOTIFIER_HEAD`，独立于内核 die_chain |
| `airy_die_map_fault` | L64-80 | L67 DIE_OOPS→VM_FAULT；L69-76 `IS_ENABLED(CONFIG_X86)` 守卫 DIE_PAGE_FAULT/DIE_TRAP/DIE_NMI |
| `airy_die_notifier` | L98-144 | 回调主体 |
| agent_id 取值 | L114-125 | L114 默认 0；L115-125 从 `task->security` 取 `sec->agent_id` + cmpxchg 递增 `fault_count` |
| ring 冻结 | L133-135 | `airy_ipc_ring_for_task(task)` → 非空才 freeze |
| eventfd 上报 | L141 | `airy_eventfd_signal_fault(fault_code, agent_id, timestamp)` |
| `airy_die_nb` | L152-155 | notifier_block，`priority = INT_MAX` |
| `airy_die_notify_init` | L163-165 | `register_die_notifier(&airy_die_nb)` 注册到内核 die_chain |

**ring 冻结** — [airy_ipc_freeze.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_ipc_freeze.c)（125 行）：

| 要素 | 行号 | 说明 |
|------|------|------|
| `airy_ipc_freeze_ring` | L37-50 | L42-43 记 reason/timestamp；L49 `smp_store_release(&ring->frozen, true)` |
| `airy_ipc_thaw_ring` | L58-71 | L70 `smp_store_release(&ring->frozen, false)` |
| `airy_ipc_fastpath_check` | L85-91 | L87 `READ_ONCE + unlikely` fastpath |
| `airy_ipc_ring_for_task` | L110-124 | L114 `!task/!security` → NULL；L124 返回 `sec->ipc_ring`（M0 恒 NULL） |
| M0 占位注释 | L104-108 | 明示 M0 `ipc_ring` 未接线，OS-IRON-004 后填充 |

**eventfd 上报** — [airy_eventfd.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_eventfd.c)（144 行）：

| 要素 | 行号 | 说明 |
|------|------|------|
| `fault_eventfd_ctx` | L39 | 单全局 ctx |
| `fault_eventfd_lock` | L40 | `DEFINE_SPINLOCK` |
| `airy_eventfd_register` | L64-94 | L83 指针所有权转移（steal reference，Linux 6.6 无 `eventfd_ctx_get` 导出） |
| `airy_eventfd_signal_fault` | L122-143 | L137 pack fault_code+agent_id 进 `__u64`；L139-143 持锁调 `eventfd_signal` |

---

## 2. 关键发现

### 2.1 【发现 1】airy_ipc_ring_for_task M0 恒返回 NULL，die_notifier freeze 死代码

**现状**：[airy_die_notify.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_die_notify.c) L133 `airy_ipc_ring_for_task(task)` 在 M0 阶段恒返回 NULL（[airy_ipc_freeze.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_ipc_freeze.c) L110-124：L124 返回 `sec->ipc_ring`，而 L104-108 注释明示 M0 该字段未接线）。因此 L134-135 的 `if (ring) airy_ipc_freeze_ring(ring, fault_code)` 分支在 M0 **永不执行**——die_notifier 的 ring freeze 步骤是死代码。

**参考**：seL4 [faulthandler.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/faulthandler.c) L31-52 `sendFaultIPC` 的 fault handler cap 来自 TCB 的 `tcbFaultHandler` 槽，boot 阶段由 root task 配置（[boot.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/boot.c) create_initial_thread），运行时 cap 一定有效或为 null（null 则 `handleNoFaultHandler` 置 Inactive，语义明确）。seL4 没有"cap 字段未接线"的中间状态——要么有效要么 null，且 null 路径有明确处理（L172 setThreadState Inactive）。Airymax 的 M0 占位导致 die_notifier 的"冻结隔离"承诺无法兑现。

**风险**：die_notifier 的设计意图（[airy_die_notify.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_die_notify.c) L8-10 注释"freeze all active IPC rings to prevent cascading failures"）在 M0 落空。若 M0 期间发生 OOPS，agent 的 IPC ring 不会被冻结，级联故障风险存在。虽 M0 无真实 agent 运行（影响有限），但文档与实现不一致会误导审计。

**建议**：(1) 短期（M0/M1）：在 [airy_ipc_freeze.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_ipc_freeze.c) L104-108 注释基础上，于 [airy_die_notify.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_die_notify.c) L133-135 补 `/* M0: ring_for_task returns NULL, freeze is no-op until OS-IRON-004 */` 注释，明示死代码是临时占位；(2) M2（OS-IRON-004 落地时）：`airy_task_alloc` 或 agent 注册路径填充 `sec->ipc_ring`，使 die_notifier freeze 真正生效。对应 N3。

**优先级**：P1 · 工作量 2h（文档）/ M2（实现） · 风险低（M0 占位可控，但需文档化）

### 2.2 【发现 2】die_notify 仅映射 4 种 die reason，覆盖面窄

**现状**：[airy_die_notify.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_die_notify.c) L64-80 `airy_die_map_fault` 仅映射：

- L67 `DIE_OOPS` → `AIRY_FAULT_VM_FAULT`（跨架构，always）
- L70 `DIE_PAGE_FAULT` → `AIRY_FAULT_VM_FAULT`（x86 only，`IS_ENABLED(CONFIG_X86)`）
- L72 `DIE_TRAP` → `AIRY_FAULT_ABNORMAL_CAP`（x86 only）
- L74 `DIE_NMI` → `AIRY_FAULT_TIMEOUT`（x86 only）

openEuler x86 定义 12 种 die reason（[kdebug.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/arch/x86/include/asm/kdebug.h) L10-23：DIE_OOPS/DIE_INT3/DIE_DEBUG/DIE_PANIC/DIE_NMI/DIE_DIE/DIE_KERNELDEBUG/DIE_TRAP/DIE_GPF/DIE_CALL/DIE_PAGE_FAULT/DIE_NMIUNKNOWN）。Airymax 漏掉 8 种：DIE_INT3（断点）/DIE_DEBUG（调试异常）/DIE_PANIC（panic 前通知）/DIE_DIE（die 链终止）/DIE_KERNELDEBUG（kgdb）/DIE_GPF（一般保护故障 #GP）/DIE_CALL（调用通知）/DIE_NMIUNKNOWN（未知 NMI）。漏掉的 `DIE_GPF`（#GP）和 `DIE_PANIC` 尤其重要——#GP 常指示内核态错误，panic 前通知是最后机会。

**参考**：seL4 故障类型粒度更细（[faults.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/api/faults.c) L122-188：CapFault/VMFault/UnknownSyscall/UserException/Timeout/DebugException），且全部经 `sendFaultIPC` 投递，无"漏映射"问题。

**风险**：漏映射的 die reason 走 L77-78 `default: return 0`，die_notifier L108-109 `if (fault_code == 0) return NOTIFY_DONE` 提前返回——即这些故障**不触发 ring freeze、不触发 eventfd 上报**。Macro-Supervisor 对 #GP/panic 前通知等"看不到"，故障归因信息缺失。

**建议**：(1) 补齐映射：DIE_GPF→`AIRY_FAULT_ABNORMAL_CAP`、DIE_PANIC→`AIRY_FAULT_VM_FAULT`（或新增 `AIRY_FAULT_PANIC`）、DIE_NMIUNKNOWN→`AIRY_FAULT_TIMEOUT`、DIE_DEBUG/DIE_INT3→`AIRY_FAULT_ABNORMAL_CAP`（debug trap 视情况）；(2) arm64/sw_64 架构补 `IS_ENABLED(CONFIG_ARM64)`/`CONFIG_SW64` 守卫的对应 die reason；(3) 在 `airy_fault_code` 枚举补充 `AIRY_FAULT_PANIC`/`AIRY_FAULT_GP` 细分。对应 N13。

**优先级**：P2 · 工作量 2h · 风险低（补映射不破坏现有路径）

### 2.3 【发现 3】eventfd 单全局 ctx，多 Macro-Supervisor 无法区分

**现状**：[airy_eventfd.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_eventfd.c) L39 `static struct eventfd_ctx *fault_eventfd_ctx` 是单全局变量，L40 单 spinlock。L64-94 `airy_eventfd_register` 仅允许一个 ctx：L77 `fault_eventfd_ctx == NULL` 才注册，L88 不同 ctx 返回 `-AIRY_EBUSY`。L122-143 `airy_eventfd_signal_fault` 向这唯一 ctx 发信号。

**参考**：openEuler printk 无此问题（ringbuffer 是全局共享，消费者轮询）。seL4 的 fault handler 是 per-TCB 的（[faulthandler.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/faulthandler.c) L17 `TCB_PTR_CTE_PTR(tptr, tcbFaultHandler)->cap`），每个线程可有自己的 fault handler endpoint——天然支持多 supervisor。

**风险**：(1) 单 Macro-Supervisor 是 M0/M1 的合理简化，但 M3+ 若引入多 supervisor（如按 agent 域划分），单 ctx 成为瓶颈；(2) 单 ctx 无故障过滤——所有 fault_code 都发给同一 supervisor，无法按 agent_id/fault_code 路由到不同处理者；(3) L122-143 `airy_eventfd_signal_fault` 持 spinlock 调 `eventfd_signal`（L139-143），虽注释 L114-120 论证"eventfd_signal 不睡眠故可持锁"，但高并发 fault 风暴时 spinlock 争用会延长 die_notifier 链路时延。

**建议**：(1) 短期：文档化"单 ctx 是 M0/M1 简化，M3+ 评估多 supervisor 需求"；(2) 中期：改 per-agent 或 per-domain eventfd 表（如 idr 映射 agent_id→ctx），`airy_eventfd_signal_fault` 按 agent_id 查表分发；(3) 评估将 `eventfd_signal` 移出 spinlock（需解决 Linux 6.6 无 `eventfd_ctx_get` 导出的引用计数问题，可借鉴 L52-59 注释的 ownership transfer 思路）。对应 N14。

**优先级**：P2 · 工作量 4h · 风险中（多 supervisor 涉及 fault 路由语义变更）

### 2.4 正面发现：die_notifier 独立链避免污染主线 panic

[airy_die_notify.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_die_notify.c) L29 `ATOMIC_NOTIFIER_HEAD(airy_die_chain)` 是**独立于内核 die_chain 的第二条链**——L23-27 注释明示"kernel die_chain handles hardware/kernel faults (OOPS, NMI); airy_die_chain handles Airy capability-space faults"。airy_die_notifier（L98）通过 `register_die_notifier`（L165）注册到**内核 die_chain** 以拦截 OOPS，同时 `airy_die_chain` 保留给"airy capability-space 故障"（如 badge 伪造）单独通知。

这避免了一个常见反模式：把所有故障都塞进内核 die_chain 导致 panic 路径臃肿。openEuler 的 die_chain 注册者众多（kprobes/kgdb/mce/edac...），airy 单独成链让 capability 故障的通知不与硬件故障竞争 INT_MAX 优先级。L152-155 `priority = INT_MAX` 保证 airy 在 die_chain 上最先执行（抢在其他 notifier 前 freeze ring + 上报），是合理的优先级选择。

### 2.5 正面发现：fault_count cmpxchg + ring freeze 内存序

[airy_die_notify.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_die_notify.c) L121-124 的 `fault_count` 递增用 `cmpxchg` 循环（无锁），正确处理并发 fault。[airy_ipc_freeze.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_ipc_freeze.c) L37-50 `airy_ipc_freeze_ring` 的 L42-43 写 reason/timestamp + L49 `smp_store_release(&ring->frozen, true)` 保证 metadata 先于 frozen 可见；L58-71 `airy_ipc_thaw_ring` 的 L63-64 清 metadata + L70 `smp_store_release(&ring->frozen, false)` 同理。L85-91 `airy_ipc_fastpath_check` 的 `READ_ONCE + unlikely` fastpath 与 freeze 的 `smp_store_release` 正确配对。这套内存序设计与报告 15 的 log_ring（正面发现）质量一致，是本轮 lock-free 设计的又一正确实现。

### 2.6 交叉引用：N2（superv_lsm 5 钩子缺 Badge 校验）

[airy_superv_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_superv_lsm.c) L41/L84/L98 的 5 个补充 LSM 钩子（task_kill/file_open/mmap_addr/file_mprotect/...）仅检查 `agent_state == STOPPED → -EPERM`，无 Badge 校验。这与故障处理相关——agent 处于 STOPPED 态时仍可能尝试触发 fault 路径，缺 Badge 校验意味着被冻结 agent 的故障事件无法按身份过滤。N2 的详细分析与改进建议见报告 09（启动初始化与 supervisor 接线），本报告交叉引用以保持故障隔离视角的完整性。对应 N2。

---

## 3. 改进点清单

| 编号 | 标题 | 优先级 | 现状行号 | 工作量 |
|------|------|--------|----------|--------|
| N2 | airy_superv_lsm 5 钩子缺 Badge 校验（详见报告 09） | P1 | [airy_superv_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_superv_lsm.c) L41/L84/L98 | 4h |
| N3 | airy_ipc_ring_for_task M0 恒返回 NULL，die_notifier freeze 死代码 | P1 | [airy_ipc_freeze.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_ipc_freeze.c) L110-124 | 2h(文档)/M2(实现) |
| N13 | die_notify 仅映射 4 种 die reason（漏 DIE_GPF/DIE_PANIC 等 8 种） | P2 | [airy_die_notify.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_die_notify.c) L64-80 | 2h |
| N14 | eventfd 单全局 ctx，多 Macro-Supervisor 无法区分 | P2 | [airy_eventfd.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_eventfd.c) L39/L64-94 | 4h |
| — | die_notifier 独立链避免污染主线 panic（正面） | — | [airy_die_notify.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_die_notify.c) L29 | — |
| — | fault_count cmpxchg + ring freeze 内存序正确（正面） | — | [airy_die_notify.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_die_notify.c) L121-124 / [airy_ipc_freeze.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_ipc_freeze.c) L37-50 | — |

---

## 4. 小结

Airymax 的故障处理三段式（die_notify → ipc_freeze → eventfd）在结构上借鉴了 seL4 的"fault 投递给 supervisor"哲学，同时保留 openEuler 的 die_chain 机制作为底层。正面发现是 [airy_die_notify.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_die_notify.c) L29 的独立 `airy_die_chain`——避免污染主线 panic 路径，以及 ring freeze/eventfd 的内存序正确性。主要差距是 N3：M0 阶段 `airy_ipc_ring_for_task` 恒返回 NULL 使 die_notifier 的 freeze 步骤成为死代码，需在 M2（OS-IRON-004）补齐 `sec->ipc_ring` 接线；N13 的 die reason 映射覆盖面窄（4/12 种）需补齐；N14 的单 eventfd ctx 是 M3+ 多 supervisor 的扩展隐患。N2（Badge 校验）与报告 09 共享，是 M2 前需收敛的安全入口对称性问题。整体故障隔离设计方向正确，M2 需收敛 N3 以兑现"freeze 隔离"承诺。
