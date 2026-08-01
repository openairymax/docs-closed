SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 17 — 改进建议汇总与实施路线图（v3.6b）

> **文档定位**：agentrt-linux 内核设计深度对比研究 · 第二轮 · 改进建议汇总
> **数据来源**：报告 09-16 全部发现，经去重与优先级评定
> **最后更新**：2026-07-31
> **方法论**：交叉比对八份子域报告，合并重复项，按严重性/紧急度/工作量三维评定

---

## 1. 改进点优先级矩阵

### 1.1 P0 — 阻断项

**本轮无新增 P0**。第一轮 P0-1（[syscall_64.tbl](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/arch/x86/entry/syscalls/syscall_64.tbl) L384-387，552-571 预留槽未显式登记）仍是唯一阻断项，详见 [07-improvement-recommendations](07-improvement-recommendations-v3.6.md) §1.1。

### 1.2 P1 — 高优先级（M2 前收敛）

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

### 1.3 P2 — 中优先级（M3-M5 渐进收敛）

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

## 2. 改进点分类统计

### 2.1 按优先级

| 优先级 | 数量 | 说明 |
|--------|------|------|
| P0 | 0 | 本轮无新增阻断项 |
| P1 | 10 | M2 前收敛（含 3 项文档化决策） |
| P2 | 12 | M3-M5 渐进收敛 |
| **合计** | **22** | — |

### 2.2 按来源维度

| 维度 | 报告 | P1 | P2 | 合计 |
|------|------|----|----|----|
| 启动初始化 + supervisor | 09 | 2（N1/N2） | 3（N20/N21/N22） | 5 |
| IRQ/事件路由 | 10 | 1（N6） | 0 | 1 |
| 时间/定时器 | 11 | 1（N5） | 0 | 1 |
| 同步原语 + 并发 | 12 | 3（N4/N9/N10） | 0 | 3 |
| 内存分配 + 分层 | 13 | 2（N7/N8） | 2（N15/N16） | 4 |
| 任务生命周期 + TCB | 14 | 0 | 2（N11/N18） | 2 |
| 日志可观测性 | 15 | 0 | 3（N12/N17/N19） | 3 |
| 故障处理与隔离 | 16 | 1（N3） | 2（N13/N14） | 3 |
| **合计** | — | **10** | **12** | **22** |

> 注：N2 来源标记为 09/16（启动与故障两维度交叉），上表按主来源归入 09。

### 2.3 按工作量分布

| 工作量区间 | 编号 | 数量 |
|-----------|------|------|
| ≤1h（文档/单行） | N18(0.5h)/N19(1h)/N22(1h文档) | 3 |
| 2-4h（低风险改进） | N3(2h文档)/N12(2h)/N13(2h)/N16(2h)/N1(4h)/N2(4h)/N11(4h)/N14(4h)/N17(4h)/N20(3h)/N21(3h) | 11 |
| 6-8h（中风险改进） | N5(6h)/N10(6h)/N15(6h)/N4(8h)/N7(8h) | 5 |
| 里程碑级（M3-M5） | N6(M3)/N8(M4)/N9(M3) | 3 |

---

## 3. 实施路线图

### 3.1 阶段一：M0 文档化（立即）

目标：补齐文档化决策与低工作量修复，确保 M0 设计基线自洽。

| 编号 | 工作量 | 说明 |
|------|--------|------|
| N3(文档) | 2h | airy_ipc_freeze.c L104-108 + airy_die_notify.c L133-135 补注释，明示 M0 freeze 死代码占位 |
| N18 | 0.5h | airy_cap_rotate.c 单行委托内联到 airy_cap.h |
| N19 | 1h | airy_log_kern.c 8→5 映射粒度损失文档化（或扩展 7 级） |
| N22 | 1h | airy_kern_api.c late_initcall 时机文档化（晚于 fs/sched/etc 的取舍） |

小计：约 4.5h，全部为低风险文档/单行修复，不改变功能。

### 3.2 阶段二：M2 前收敛（P1 高优先级）

目标：安全入口完整化 + 可观测性 + IPC 集成就绪。

| 编号 | 工作量 | 说明 |
|------|--------|------|
| N1 | 4h | airy_kern_api_init 统一调度 8 子系统 init |
| N2 | 4h | airy_superv_lsm 5 钩子补 Badge 校验（与第一轮 P1-4 同源） |
| N4 | 8h | airy_object.c 全局锁 → per-bucket 锁 + idr |
| N5 | 6h | airy_time.c 增加 hrtimer 封装，agent 超时唤醒 |
| N7 | 8h | airy_mem_alloc.c 集成 memcg/per-agent 账户 |
| N10 | 6h | airy_locking.c 增加 RCU wrapper，cap_array 高频读 RCU 化 |
| N3(实现) | M2 | airy_ipc_freeze.c sec->ipc_ring 接线（OS-IRON-004） |

小计：约 36h + M2 集成。N6/N8/N9 为 M3/M4 里程碑项，不在 M2 前。

### 3.3 阶段三：M3-M5 渐进收敛（P2 + 里程碑级 P1）

目标：运行时治理完善 + 扩展性。

| 编号 | 工作量 | 说明 |
|------|--------|------|
| N6 | M3 | airy_irq.c 实现 agent IRQ 路由（IRQControl 等价物） |
| N8 | M4 | airy_mem_tier.c 实现 tier→NUMA/CXL 路由 |
| N9 | M3 | airy_bpf_probe/struct_ops 真正接入 BPF |
| N11 | 4h | airy_task_lifecycle 增加 suspend/resume 显式 API |
| N12 | 2h | airy_log_ring_header 增 dropped 计数器 |
| N13 | 2h | airy_die_map_fault 补齐 DIE_GPF/DIE_PANIC 等 8 种映射 |
| N14 | 4h | airy_eventfd 改 per-agent/per-domain ctx 表 |
| N15 | 6h | airy_ipc_zero_copy 注册表 per-agent 命名空间 |
| N16 | 2h | airy_mem_tier_shift sysfs 暴露 |
| N17 | 4h | airy_log_persist 引入 airy_log_flushd 异步刷盘 |
| N20 | 3h | airy_superv_lsm mmap_addr 对接 cap_array 地址白名单 |
| N21 | 3h | airy_superv_lsm file_mprotect 对接 cap_array PROT_EXEC |

小计：约 30h + M3/M4/M5 集成。

---

## 4. 风险评估总览

### 4.1 高风险项

- **N4（airy_object.c 全局锁 + O(N) lookup）**：改 per-bucket 锁 + idr 涉及并发正确性验证，需配合 KCSAN/KASAN 压测。与第一轮 P1-11（cap_derive 全局锁）同源问题，建议一并设计 per-bucket 锁体系。
- **N3（freeze 死代码）**：M2 实现 `sec->ipc_ring` 接线需协调 agent 注册路径与 die_notifier，时序敏感（接线前 die_notifier 无法兑现 freeze 承诺）。
- **N7（per-agent 内存账户）**：memcg 集成涉及 cgroup 子系统交互，复杂度高，是第一轮 MemoryRovol（syscall 549，M5）的底层支撑。
- **N14（eventfd 多 ctx）**：改 per-agent ctx 表涉及 fault 路由语义变更，需重新评估 die_notifier 链路的并发安全。

### 4.2 低风险项

- N18/N19/N22 为单行修复或文档补充，无功能变更风险。
- N12/N13/N16 为增量字段/映射补齐，不破坏现有路径。
- N11/N17 为新增 API/线程，不改现有语义。

---

## 5. 与第一轮（v3.6）的关系

### 5.1 两轮改进点汇总

| 维度 | 第一轮 v3.6 | 第二轮 v3.6b | 累计（去重） |
|------|------------|-------------|-------------|
| 子域数 | 6 | 8（全新） | 14 |
| 报告数 | 9 | 11 | 20 |
| P0 | 1 | 0 | 1 |
| P1 | 11 | 10 | 21（去重后） |
| P2 | 17 | 12 | 29（去重后） |
| 合计 | 29 | 22 | 51（去重后） |

### 5.2 交叉项（去重）

- **N2 ↔ 第一轮 P1-4**：均关于 Airymax LSM 钩子缺 Badge 校验。第一轮 P1-4 针对 [airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_lsm.c) L67-109 的 task_kill/file_open；第二轮 N2 针对补充钩子 [airy_superv_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_superv_lsm.c) L41/L84/L98。两者同源（安全入口不对称），建议 M2 前一并收敛。
- **N4 ↔ 第一轮 P1-11**：均关于全局 spinlock 可扩展性。第一轮 P1-11 针对 cap_derive 全局锁（已由 [airy_cap_array.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_array.c) L27-30 per-bucket 锁收敛）；第二轮 N4 针对 airy_object.c 全局锁。建议统一 per-bucket 锁设计模式。

### 5.3 互补关系

第一轮保证"核心机制设计对"（调度器/安全/IPC/syscall/capability/内存版本治理），第二轮追问"基础设施撑不撑得住"（boot/irq/time/sync/mem-alloc/task/log/fault）。两轮覆盖 14 个子域，改进点去重后 51 项，无遗漏核心维度。第一轮的 P0-1 仍是唯一阻断项，第二轮无新增阻断，故 M0 设计阶段 Go 判断成立（详见报告 18）。
