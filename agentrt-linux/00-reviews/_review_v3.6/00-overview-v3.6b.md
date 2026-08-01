SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 00 — v3.6b 深度对比研究主索引（第二轮）

> **文档定位**：agentrt-linux 内核设计深度对比研究 · 第二轮主索引
> **对比基准**：openEuler kernel-OLK-6.6 · seL4-master · Airymax agentrt-linux
> **最后更新**：2026-07-31
> **方法论**：逐字节阅读三项目源码，所有引用标注文件路径+行号，严禁编造
> **与前序关系**：本轮（v3.6b）在第一轮（v3.6）6 子域基础上发掘 8 个新维度，两轮互补不重复

---

## 1. 研究范围

### 1.1 第二轮定位

第一轮（v3.6）覆盖 6 子域：调度器 / 安全 LSM / IPC / syscall-codegen / capability-CNode / 内存版本治理，产出 29 项改进点（1 P0 + 11 P1 + 17 P2）。

第二轮（v3.6b）要求"超越第一轮 6 子域，发掘新维度"，对 openEuler OLK-6.6 + seL4-master + Airymax 三项目做字节级对比。本轮选定 8 个新维度，均为第一轮未触及的子系统。

### 1.2 三个项目根目录

| 项目 | 路径 | 角色 |
|------|------|------|
| openEuler | `/home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/` | 通用服务器内核参考（start_kernel/hrtimer/printk ringbuffer/die_chain） |
| seL4 | `/home/spharx/SpharxWorks/.engineer-reference/seL4-master/` | 形式化微内核参考（boot.c/TCB suspend-resume/handleFault/IRQControl/Untyped） |
| Airymax | `/home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/` | 被评估对象（airy_core/airy_superv_*/airy_log_*/airy_die_notify） |

### 1.3 八个新维度

| 序号 | 维度 | Airymax 主文件 | 参考对比点 |
|------|------|----------------|-----------|
| 1 | 启动初始化 + supervisor 接线 | init/airy_core.c、kernel/superv/airy_superv_init.c | openEuler start_kernel 序列、seL4 boot.c |
| 2 | IRQ/事件路由 | kernel/corekern/irq/airy_irq.c | openEuler request_irq、seL4 IRQControl |
| 3 | 时间/定时器 | kernel/corekern/time/airy_time.c | openEuler hrtimer、seL4 timer.c |
| 4 | 同步原语 + 并发正确性 | kernel/corekern/locking/airy_locking.c | openEuler spinlock/RCU、seL4 NODE_LOCK |
| 5 | 内存分配 + 分层治理 | kernel/corekern/memory/airy_mem_alloc.c、airy_mem_tier.c | openEuler alloc_pages/memcg、seL4 Untyped |
| 6 | 任务生命周期 + TCB 等价物 | kernel/corekern/taskflow/airy_task_lifecycle.c | openEuler task_struct、seL4 TCB |
| 7 | 日志可观测性基础设施 | kernel/log/airy_log_ring.c | openEuler printk ringbuffer |
| 8 | 故障处理与隔离 | security/airy/airy_die_notify.c | openEuler die_chain、seL4 handleFault |

---

## 2. 报告清单

| 编号 | 文件 | 主题 | 关键发现数 |
|------|------|------|-----------|
| 00 | [本文件](00-overview-v3.6b.md) | 主索引：研究范围/方法论/优先级矩阵 | — |
| 09 | [09-boot-init-supervisor](09-boot-init-supervisor-v3.6b.md) | 启动初始化与 Micro-Supervisor 接线 | 3 |
| 10 | [10-irq-event-routing](10-irq-event-routing-v3.6b.md) | IRQ/事件路由 | 2 |
| 11 | [11-time-timer](11-time-timer-v3.6b.md) | 时间/定时器 | 2 |
| 12 | [12-synchronization-concurrency](12-synchronization-concurrency-v3.6b.md) | 同步原语与并发正确性 | 3 |
| 13 | [13-memory-allocation-tiering](13-memory-allocation-tiering-v3.6b.md) | 内存分配与分层治理 | 3 |
| 14 | [14-task-lifecycle-tcb](14-task-lifecycle-tcb-v3.6b.md) | 任务生命周期与 TCB 等价物 | 2 |
| 15 | [15-logging-observability](15-logging-observability-v3.6b.md) | 日志可观测性基础设施 | 3 |
| 16 | [16-fault-handling-isolation](16-fault-handling-isolation-v3.6b.md) | 故障处理与隔离 | 2 |
| 17 | [17-improvement-recommendations](17-improvement-recommendations-v3.6b.md) | 改进建议汇总：22 项 + 优先级矩阵 + 路线图 | 22 |
| 18 | [18-closure-summary](18-closure-summary-v3.6b.md) | 闭环：Go/No-Go 判断 + 成熟度评分 | — |

---

## 3. 关键发现摘要

### 3.1 设计亮点（Airymax 领先或自洽项）

1. **双 Supervisor 模型**：Micro-Supervisor（内核冷酷执法）+ Macro-Supervisor（用户态温情裁决），airy_lsm.c 5 核心 + airy_superv_lsm.c 5 补充钩子分工清晰，借鉴 seL4 handleFault 的 fault IPC 语义。
2. **lock-free 日志 ring**：[airy_log_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_ring.c) L52-60 三索引（head/committed_head/tail）+ cmpxchg reserve + smp_store_release commit + smp_load_acquire 消费，内存序正确，质量高于第一轮多数子系统。
3. **die_notifier 独立链**：[airy_die_notify.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_die_notify.c) L29 自建 `ATOMIC_NOTIFIER_HEAD(airy_die_chain)`，与内核 die_chain 解耦，避免污染主线 panic 路径。
4. **per-bucket cap 锁**：[airy_cap_array.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_array.c) L27-30 静态初始化 `airy_cap_bucket_locks[AIRY_CAP_BUCKET_NR]`，已收敛第一轮 P1-11 的全局锁子问题。
5. **8 态任务状态机**：[airy_task_lifecycle.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/taskflow/airy_task_lifecycle.c) L68-140 显式 legal transition 表，比 openEuler 隐式 state 位图更易审计。

### 3.2 主要差距（需收敛项）

1. **初始化串联缺失**：[airy_kern_api.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/api/airy_kern_api.c) late_initcall 仅调 `airy_locking_init()`，其余 7 个子系统 init 未统一调度。
2. **die_notifier freeze 死代码**：[airy_ipc_freeze.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_ipc_freeze.c) L110-124 `airy_ipc_ring_for_task()` 在 M0 阶段 sec->ipc_ring 恒为 NULL，die_notifier 无法实际冻结任何 ring。
3. **补充 LSM 钩子 Badge 不对称**：[airy_superv_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_superv_lsm.c) L41/L84/L98 仅检查 agent_state==STOPPED→-EPERM，无 Badge 校验，与第一轮 P1-4 同源。
4. **无 hrtimer 封装**：[airy_time.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/time/airy_time.c) 仅 ktime_get_ns wrapper，agent 超时唤醒机制缺失。
5. **无 agent IRQ 路由**：[airy_irq.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/irq/airy_irq.c) request_irq wrapper dev_id=NULL、flags=0，无 seL4 IRQControl 等价物。
6. **BPF 占位未接入**：[airy_bpf_probe.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/bpf/airy_bpf_probe.c) + [airy_struct_ops.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/bpf/airy_struct_ops.c) 未真正调用 bpf_struct_ops_register。
7. **tier 分类仅靠 GFP 低 4 位**：[airy_mem_tier.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/memory/airy_mem_tier.c) tier_of() 无实际 NUMA/CXL 路由实现。

---

## 4. 改进点优先级矩阵

### 4.1 P0 — 阻断项

本轮无新增 P0。第一轮 P0-1（552-571 预留 syscall 槽）仍是唯一阻断项，见 [07-improvement-recommendations](07-improvement-recommendations-v3.6.md) §1.1。

### 4.2 P1 — 高优先级（M2 前收敛）

| 编号 | 标题 | 来源报告 | 现状位置 | 工作量 |
|------|------|----------|----------|--------|
| N1 | airy_kern_api_init 仅串联 locking_init，7 子系统 init 未统一调度 | 09 | [airy_kern_api.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/api/airy_kern_api.c) L1-48 | 4h |
| N2 | airy_superv_lsm.c 5 补充钩子缺 Badge 校验 | 09/16 | [airy_superv_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_superv_lsm.c) L41/L84/L98 | 4h |
| N3 | airy_ipc_ring_for_task() M0 恒返回 NULL，die_notifier freeze 死代码 | 16 | [airy_ipc_freeze.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_ipc_freeze.c) L110-124 | 2h(文档)/M2(实现) |
| N4 | airy_object.c 全局单 spinlock + O(N) lookup | 12 | [airy_object.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/object/airy_object.c) L1-90 | 8h |
| N5 | airy_time.c 无 hrtimer 封装，agent 超时唤醒缺失 | 11 | [airy_time.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/time/airy_time.c) L1-33 | 6h |
| N6 | airy_irq.c 无 agent IRQ 路由，无 IRQControl 等价物 | 10 | [airy_irq.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/irq/airy_irq.c) L1-43 | M3 |
| N7 | airy_mem_alloc.c 无 memcg 集成，无 per-agent 内存账户 | 13 | [airy_mem_alloc.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/memory/airy_mem_alloc.c) L1-46 | 8h |
| N8 | airy_mem_tier.c tier 分类仅靠 GFP 低 4 位，无 NUMA/CXL 路由 | 13 | [airy_mem_tier.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/memory/airy_mem_tier.c) L1-52 | M4 |
| N9 | airy_bpf_probe.c + airy_struct_ops.c 未真正接入 BPF | 12 | [airy_struct_ops.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/bpf/airy_struct_ops.c) L1-61 | M3 |
| N10 | airy_locking.c 无 RCU wrapper，cap_array 高频读未利用 RCU | 12 | [airy_locking.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/locking/airy_locking.c) L1-47 | 6h |

### 4.3 P2 — 中优先级（M3-M5）

| 编号 | 标题 | 来源报告 | 现状位置 | 工作量 |
|------|------|----------|----------|--------|
| N11 | airy_task_lifecycle.c 无显式 suspend/resume | 14 | [airy_task_lifecycle.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/taskflow/airy_task_lifecycle.c) L68-140 | 4h |
| N12 | airy_log_ring.c 满时 overwrite 无溢出计数器/告警 | 15 | [airy_log_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_ring.c) L153-154 | 2h |
| N13 | airy_die_notify.c 仅映射 4 种 die reason | 16 | [airy_die_notify.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_die_notify.c) L64-80 | 2h |
| N14 | airy_eventfd.c 单全局 ctx，多 Macro-Supervisor 无法区分 | 16 | [airy_eventfd.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_eventfd.c) L1-144 | 4h |
| N15 | airy_ipc_zero_copy.c 注册表全局链表+单 spinlock | 13 | [airy_ipc_zero_copy.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_zero_copy.c) L1-168 | 6h |
| N16 | airy_mem_tier_shift 静态表无 sysfs 暴露 | 13 | [airy_mem_tier.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/memory/airy_mem_tier.c) | 2h |
| N17 | airy_log_persist.c 同步 kernel_write，无异步刷盘线程 | 15 | [airy_log_persist.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_persist.c) L1-102 | 4h |
| N18 | airy_cap_rotate.c 单行委托可内联到 airy_cap.h | 14 | [airy_cap_rotate.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_rotate.c) L1-38 | 0.5h |
| N19 | airy_log_kern.c 8→5 级别映射丢失 ALERT/CRIT/NOTICE 粒度 | 15 | [airy_log_kern.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_kern.c) L1-103 | 1h |
| N20 | airy_superv_lsm.c mmap_addr 未对接 cap_array 地址白名单 | 09 | [airy_superv_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_superv_lsm.c) | 3h |
| N21 | airy_superv_lsm.c file_mprotect 仅 W^X 检查，未对接 cap_array PROT_EXEC | 09 | [airy_superv_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_superv_lsm.c) | 3h |
| N22 | airy_kern_api.c late_initcall 时机晚于 fs/sched/etc | 09 | [airy_kern_api.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/api/airy_kern_api.c) | 1h(文档) |

---

## 5. Go/No-Go 判断

| 阶段 | 判断 | 条件 |
|------|------|------|
| M0 设计 | ✅ GO | 本轮无新增 P0；N1/N2 文档化接线顺序与 Badge 校验计划 |
| M1 脚手架 | ✅ GO | 多数子系统为 wrapper 占位，符合 M0 自洽 |
| M2 IPC 集成 | ⚠️ 条件 GO | 收敛 N3（freeze 死代码）/N5（hrtimer）/N10（RCU） |

**综合成熟度评分：86.0（B+）**——详见 [18-closure-summary](18-closure-summary-v3.6b.md)。

> 说明：本轮评分低于第一轮（89.5），因本轮刻意选择第一轮未触及的"基础设施"维度，这些维度多为 M0/M1 占位实现，成熟度天然偏低。两轮加权后整体成熟度见报告 18。

---

## 6. 研究方法说明

### 6.1 证据收集

- **openEuler**：Read 工具逐行核验 init/main.c（start_kernel L888）、security/security.c（security_init L438-504）、include/linux/sched.h（task_struct L805）、kernel/printk/printk.c（vprintk_emit L2316）、kernel/printk/printk_ringbuffer.c（prb_reserve L1485）
- **seL4**：Read 工具逐行核验 src/kernel/boot.c（create_root_cnode L278、create_initial_thread L496）、src/object/tcb.c（invokeTCB_Suspend L1690、decodeTCBInvocation L848）、src/object/untyped.c、src/object/interrupt.c
- **Airymax**：主上下文逐文件 Read 核验 25 个新源文件（init/airy_core.c、kernel/superv/*、security/airy/airy_superv_lsm.c、airy_die_notify.c、airy_ipc_freeze.c、airy_eventfd.c、airy_cap_array.c、kernel/corekern/* 全部子目录、kernel/log/*），所有行号经 Read 工具确认

### 6.2 引用规范

- 所有代码位置使用 `[文件名](file:///绝对路径#L行号)` markdown 链接
- 行号来自实际 Read 工具读取或 grep 确认，严禁编造
- 改进建议每条包含：现状（带行号）+ 参考（带行号）+ 建议 + 风险评估
- openEuler/seL4 关键行号经子代理调研后由主上下文二次 Read 核验，杜绝幻觉

### 6.3 与第一轮（v3.6）的关系

| 维度 | 第一轮 v3.6 | 第二轮 v3.6b |
|------|------------|-------------|
| 子域数 | 6 | 8（全新） |
| 报告数 | 9 | 11 |
| 改进点 | 29（1 P0 + 11 P1 + 17 P2） | 22（0 P0 + 10 P1 + 12 P2） |
| 累计改进点 | — | 51（去重后） |
| 视角 | 核心机制（sched/security/IPC/cap/syscall/mem-version） | 基础设施（boot/irq/time/sync/mem-alloc/task/log/fault） |

两轮互补：第一轮保证"核心机制设计对"，第二轮追问"基础设施撑不撑得住"。
