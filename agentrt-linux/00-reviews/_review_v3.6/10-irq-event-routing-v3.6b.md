SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 10 — IRQ/事件路由（v3.6b 深度对比）

> **文档定位**：agentrt-linux 内核设计深度对比研究 · 第二轮 · 维度 2
> **对比基准**：openEuler kernel-OLK-6.6 · seL4-master · Airymax agentrt-linux
> **最后更新**：2026-07-31
> **方法论**：逐字节阅读三项目源码，所有引用标注文件路径+行号，严禁编造

---

## 0. 摘要

本报告对比三项目的 IRQ/事件路由机制。openEuler 提供 `request_threaded_irq` + IRQF_* 标志体系，支持共享/线程化/定时器中断；seL4 通过 `IRQControl` capability 将 IRQ 绑定到 Notification cap，实现 per-agent 能力中介的 IRQ 投递；Airymax 的 [airy_irq.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/irq/airy_irq.c) 仅是 `request_irq`/`free_irq` 的薄包装，`dev_id=NULL`、`flags=0`，无 agent 路由、无 capability 中介，与 seL4 IRQControl 不可比。核心发现：N6（无 agent IRQ 路由，无 IRQControl 等价物）。

---

## 1. 对比基准

### 1.1 openEuler OLK-6.6 IRQ 管理

openEuler 沿用 Linux IRQ 框架。注册入口 [include/linux/interrupt.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/interrupt.h) L167 `request_irq()`，核心实现在 [kernel/irq/manage.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/irq/manage.c) L2142 `request_threaded_irq()`。

| 标志 | 行号 | 含义 |
|------|------|------|
| `IRQF_SHARED` | L73 | 允许多设备共享 IRQ 线 |
| `IRQF_NO_THREAD` | L82 | 禁止线程化（硬中断上下文） |
| `IRQF_TIMER` | L88 | 定时器中断（NO_SUSPEND\|NO_THREAD） |

**特征**：`dev_id` 用于区分共享 IRQ 上的不同 handler；`flags` 控制线程化/共享/唤醒等行为；handler 通过 `irqreturn_t` 返回 `IRQ_HANDLED`/`IRQ_NONE` 决定是否唤醒线程化处理。

### 1.2 seL4 IRQControl

seL4 将 IRQ 抽象为 capability。[src/object/interrupt.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/interrupt.c) 关键路径：

| 函数 | 行号 | 作用 |
|------|------|------|
| `decodeIRQControlInvocation` | L23 | 解码 IRQControl 调用 |
| `invokeIRQControl` | L78 | 将 IRQ 绑定到 handlerSlot（L80 `setIRQState(IRQSignal, irq)`，L81 `cteInsert` 插入 IRQ handler cap） |
| `decodeIRQHandlerInvocation` | L86 | 解码 IRQHandler 调用（L94 `IRQSetIRQHandler` 将 Notification cap 绑定到 IRQ） |

**机制**：`invokeIRQControl` 在 controlSlot（父 cap）与 handlerSlot 之间建立能力关系，`cteInsert` 生成 `cap_irq_handler_cap`。用户态拿到 IRQHandler cap 后，通过 `IRQSetIRQHandler`（L94）将其绑定到一个 Notification cap（L102 `ntfnCap`）。IRQ 触发时，内核 `sendSignal` 到该 Notification，等待者被唤醒。这实现了**能力中介的 per-agent IRQ 投递**：只有持有 IRQHandler cap 的 agent 才能接收对应 IRQ。

### 1.3 Airymax IRQ 管理

[airy_irq.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/irq/airy_irq.c) 全文 43 行，两个函数：

| 函数 | 行号 | 实现要点 |
|------|------|----------|
| `airy_irq_register_handler` | L18 | L25 `request_irq(irq, fn, 0, "airy_irq", NULL)` — flags 恒为 0，dev_id 恒为 NULL |
| `airy_irq_unregister_handler` | L36 | L41 `free_irq(irq, NULL)` |

**特征**：固定 name="airy_irq"（L25），无法区分多个 agent 的 handler；`flags=0` 意味着不支持 `IRQF_SHARED`，同一 IRQ 只能注册一个 airy handler；`dev_id=NULL` 在共享 IRQ 场景下会导致 `free_irq` 无法定位正确 handler（但当前不支持共享，暂不致命）。

---

## 2. 三方对比

| 维度 | openEuler | seL4 | Airymax |
|------|-----------|------|---------|
| IRQ 注册入口 | `request_threaded_irq` (manage.c L2142) | `invokeIRQControl` (interrupt.c L78) | `airy_irq_register_handler` (airy_irq.c L18) |
| 中介模型 | 全局 irq_desc 数组 + handler 链 | capability（IRQControl→IRQHandler→Notification） | 无中介，直接 request_irq |
| per-agent 路由 | 无（handler 不区分 agent） | 有（cap 持有者即接收者） | 无 |
| 共享 IRQ | `IRQF_SHARED` (interrupt.h L73) | 不适用（每 IRQ 一个 handler cap） | 不支持（flags=0） |
| 线程化 | `IRQF_NO_THREAD` 可控 (L82) | 不适用 | 不可控（flags=0） |
| 投递机制 | handle_irq_event → handler 链 | setIRQState + sendSignal 到 Notification | Linux 默认 handle_irq_event |
| 能力撤销 | 无 | cap revoke 即撤销 IRQ 接收权 | 无 |

---

## 3. 关键发现

### 3.1 【发现 1】无 agent IRQ 路由，无 IRQControl 等价物

**现状**：[airy_irq.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/irq/airy_irq.c) L25 `request_irq` 调用未携带任何 agent 标识，handler 注册后 IRQ 触发直接进入 `fn` 回调，无法将 IRQ 事件路由到特定 agent 或 Macro-Supervisor。

**参考**：seL4 [interrupt.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/interrupt.c) L78 `invokeIRQControl` 通过 `cteInsert` 建立 IRQ→cap→Notification→agent 的完整链路，IRQ 触发即 `sendSignal` 到目标 agent 的 Notification。openEuler 虽无 per-agent 路由，但其 `request_threaded_irq` 支持 `IRQF_SHARED` + `dev_id` 区分多设备。

**风险**：Airymax 的 agent 模型需要将硬件 IRQ 转化为 agent 可感知的事件（设计文档 09-kernel-agent-supervisor.md 提到 eventfd 借鉴 seL4 Notification 位图语义），但当前 airy_irq.c 与 eventfd 路径完全断开，IRQ 无法触发 agent 唤醒。

**建议**：M3 实现 `airy_irq_route_to_agent(irq, agent_id, ntfn_cap)`，在 handler 中调用 `airy_eventfd_signal_fault` 或等价的 Notification 机制将 IRQ 事件投递给目标 agent。短期文档化"当前 IRQ 不支持 agent 路由，M3 实现"。对应 N6。

**优先级**：P1 · 工作量 M3 · 风险中（需与 eventfd/Notification 路径协同设计）

### 3.2 【发现 2】flags=0 + dev_id=NULL 限制扩展性

**现状**：[airy_irq.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/irq/airy_irq.c) L25 `request_irq((unsigned int)irq, fn, 0, "airy_irq", NULL)` 硬编码 flags=0。

**参考**：openEuler [interrupt.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/interrupt.h) L73 `IRQF_SHARED`、L82 `IRQF_NO_THREAD`、L88 `IRQF_TIMER` 提供丰富标志。

**风险**：定时器中断需 `IRQF_TIMER`（含 NO_SUSPEND\|NO_THREAD），当前 flags=0 会导致定时器 IRQ 在 suspend 时被禁用、可能被强制线程化；多 agent 共享 IRQ 场景无法支持。

**建议**：将 `flags` 作为参数传入 `airy_irq_register_handler`，调用方按需指定 `IRQF_TIMER`/`IRQF_SHARED`；`dev_id` 改为传递 `agent_id` 或 handler 私有数据。

**优先级**：P2 · 工作量 1h · 风险低

---

## 4. 改进点清单

| 编号 | 标题 | 优先级 | 现状行号 | 工作量 |
|------|------|--------|----------|--------|
| N6 | 无 agent IRQ 路由，无 IRQControl 等价物 | P1 | [airy_irq.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/irq/airy_irq.c) L18-33 | M3 |
| — | flags=0 + dev_id=NULL 限制扩展性 | P2 | [airy_irq.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/irq/airy_irq.c) L25 | 1h |

---

## 5. 小结

airy_irq.c 是本轮最薄的子系统（43 行），作为 M0 占位 wrapper 自洽（-EINVAL 校验 + pr_info 日志合理）。但 agent RT 系统的核心需求——将硬件 IRQ 转化为 agent 事件——完全未实现。seL4 的 IRQControl→Notification 链路是 Airymax agent 模型的目标形态，M3 应将 airy_irq 与 airy_eventfd/airy_log_ring 的 Notification 路径打通。
