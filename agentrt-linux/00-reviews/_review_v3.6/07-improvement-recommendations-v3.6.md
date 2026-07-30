SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 07 — 改进建议汇总与实施路线图

> **文档定位**：v3.6 深度对比研究 · 改进建议汇总
> **数据来源**：报告 01-06 全部发现，经去重与优先级评定
> **最后更新**：2026-07-30
> **方法论**：交叉比对六份子域报告，合并重复项，按严重性/紧急度/工作量三维评定

---

## 1. 改进点优先级矩阵

### 1.1 P0 — 阻断项（0.1.1 冻结前必须修复）

| 编号 | 标题 | 来源报告 | 现状位置 | 工作量 |
|------|------|----------|----------|--------|
| P0-1 | 552-571 预留 syscall 槽位未在 syscall_64.tbl 显式登记 | 04 | [syscall_64.tbl](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/arch/x86/entry/syscalls/syscall_64.tbl) L384-387（仅 548-551 登记，552-571 缺失） | 1h |

### 1.2 P1 — 高优先级（M2 前收敛）

| 编号 | 标题 | 来源报告 | 现状位置 | 工作量 |
|------|------|----------|----------|--------|
| P1-1 | stc_dispatch.c 用 pr_info 影响性能 | 01 | [stc_dispatch.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_dispatch.c) L73-75 | 2h |
| P1-2 | stc_stats 未通过 debugfs/sysfs 暴露 | 01 | [stc_stats.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_stats.c) L20-39 | 3h |
| P1-3 | airy_vtime_decay 语义偏差（注释声称 EEVDF，实为旧 CFS） | 01 | [sched.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/sched.h) L42-50 | 1h(注释)/8h(算法) |
| P1-4 | task_kill/file_open 仅检查 agent_state，缺完整 Badge 校验 | 02 | [airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_lsm.c) L67-109 | 4h |
| P1-5 | airy_ipc_capability.c 用 __aligned(64) 违反 OS-IRON-016 | 02/06 | [airy_ipc_capability.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/ipc/airy_ipc_capability.c) L29-30 | 0.5h |
| P1-6 | airy_inode_sec 未接线到 VFS，file_open 无法 per-inode 检查 | 02 | [lsm_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/lsm_types.h) L40-43 | 8h |
| P1-7 | fastpath_send 不含 Badge 校验的决策未文档化 | 03 | [airy_ipc_fastpath.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_fastpath.c) L31-34 | 1h |
| P1-8 | 缺少 cancelBadgedSends 等价机制 | 03/05 | seL4 [endpoint.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/endpoint.c) L476-489 | 6h |
| P1-9 | REVOKE 无级联撤销，派生 cap 不受影响 | 05 | [airy_cap_derive.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_derive.c) L190-206 | 2h(文档)/16h(实现) |
| P1-10 | COPY 不支持权限子集降级 | 05 | [airy_cap_derive.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_derive.c) L79-104 | 3h |
| P1-11 | 全局单一 spinlock 可扩展性瓶颈 | 05 | [airy_cap_derive.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_derive.c) L27 | 8h |

### 1.3 P2 — 中优先级（M3-M5 渐进收敛）

| 编号 | 标题 | 来源报告 | 现状位置 | 工作量 |
|------|------|----------|----------|--------|
| P2-1 | 缺少 CBS 带宽准入（dl_bw 等价） | 01 | [stc_dispatch.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_dispatch.c) L87 | 4h |
| P2-2 | syscall 入口无 budget 检查 | 01/04 | [airy_syscalls.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/syscalls/airy_syscalls.c) L78-198 | M2 |
| P2-3 | 缺少 SC 捐赠与 consumed time 上报 | 01/03 | seL4 [endpoint.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/endpoint.c) L101-103 | M5 |
| P2-4 | 缺少 lockdown 机制 | 02 | openEuler [security.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/security/security.c) L43-75 | 6h |
| P2-5 | security_hook_heads 注册阶段未明确 | 02 | [airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_lsm.c) L150-154 | 1h(文档) |
| P2-6 | 5 hook 可观测性不足，扩展计划未文档化 | 02 | [lsm_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/lsm_types.h) L23 | 2h(文档) |
| P2-7 | ring_post magic check 冗余性评估 | 03 | [airy_ipc_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_ring.c) L71 | 2h |
| P2-8 | 借鉴 xsched sched_attr 扩展属性 | 04 | openEuler [syscall_64.tbl](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/arch/x86/entry/syscalls/syscall_64.tbl) L391-392 | M3 |
| P2-9 | syscall_gen.py SSoT 流程文档化 | 04 | [syscall_gen.py](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/tools/codegen/syscall_gen.py) L310-364 | 2h |
| P2-10 | 缺少 derive_tree 派生关系追踪 | 05 | [airy_ipc_capability.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/ipc/airy_ipc_capability.c) L29-32 | M3 |
| P2-11 | CNodeSaveCaller 不实现的决策未文档化 | 05 | seL4 [cnode.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c) L36-40 | 1h |
| P2-12 | ALK vs KABI 权衡决策未文档化 | 06 | openEuler [sched.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/sched.h) L722 | 2h |
| P2-13 | _reserved 字段命名不统一 | 06 | [lsm_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/lsm_types.h) L53 vs [sched.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/sched.h) L70 | 1h |
| P2-14 | MemoryRovol（549）M5 实现规划 | 06 | [airy_syscalls.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/syscalls/airy_syscalls.c) L143-151 | M5 |

---

## 2. 改进点分类统计

| 类别 | P0 | P1 | P2 | 合计 |
|------|----|----|----|----|
| 调度器 | 0 | 3 | 3 | 6 |
| 安全 LSM | 0 | 3 | 3 | 6 |
| IPC | 0 | 2 | 2 | 4 |
| Syscall/Codegen | 1 | 0 | 3 | 4 |
| Capability/CNode | 0 | 3 | 2 | 5 |
| 内存/版本治理 | 0 | 0 | 4 | 4 |
| **合计** | **1** | **11** | **17** | **29** |

---

## 3. 实施路线图

### 3.1 阶段一：0.1.1 冻结前（立即）

目标：修复 P0 + 低工作量 P1，确保基线自洽。

| 编号 | 工作量 | 说明 |
|------|--------|------|
| P0-1 | 1h | syscall_64.tbl 增加 552-571 显式 `sys_ni_syscall` 占位 |
| P1-5 | 0.5h | `__aligned(64)` → `AIRY_ALIGNED(64)` 一字符修复 |
| P1-1 | 2h | `pr_info` → tracepoint |
| P1-3(注释) | 1h | 修正 `airy_vtime_decay` 注释为"用户态 vtime 近似" |
| P1-7 | 1h | 文档化 fastpath_send Badge 校验在 LSM hook 完成的决策 |
| P2-5 | 1h | 文档化 hook 注册阶段（boot-only） |
| P2-11 | 1h | 文档化不实现 CNodeSaveCaller 的决策 |
| P2-13 | 1h | 统一 `_reserved` 命名 |

小计：约 8.5h，全部为低风险文档/单行修复。

### 3.2 阶段二：M2 前（io_uring IPC 集成）

目标：安全入口完整化 + 可观测性。

| 编号 | 工作量 | 说明 |
|------|--------|------|
| P1-2 | 3h | stc_stats → debugfs 暴露 |
| P1-4 | 4h | task_kill/file_open 增加 Badge 校验 |
| P1-10 | 3h | COPY 增加可选权限降级 |
| P1-8 | 6h | 实现 cancelBadgedSends |
| P2-2 | M2 | syscall 入口 budget guard |
| P2-7 | 2h | magic check 冗余性评估 |

小计：约 18h + M2 集成。

### 3.3 阶段三：M3-M5（sched_tac / cognition / memory）

目标：运行时治理完善。

| 编号 | 工作量 | 说明 |
|------|--------|------|
| P1-6 | 8h | airy_inode_sec 接线 VFS |
| P1-9 | 16h | derive_tree 或级联撤销文档化 |
| P1-11 | 8h | per-bucket 锁替代全局 spinlock |
| P2-1 | 4h | CBS 带宽准入 |
| P2-4 | 6h | lockdown 机制 |
| P2-10 | M3 | derive_tree 实现 |
| P2-3 | M5 | SC 捐赠 |
| P2-14 | M5 | MemoryRovol 实现 |

小计：约 42h + M3/M5 集成。

---

## 4. 风险评估总览

### 4.1 高风险项

- **P1-9（REVOKE 级联撤销）**：若选择实现 derive_tree，需修改 `airy_cap_slot` 结构体（[lsm_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/lsm_types.h) L46-54），影响 UAPI 兼容性。建议优先文档化"非级联"语义，待 M3 评估实际需求。
- **P1-11（全局 spinlock）**：改为 per-bucket 锁涉及并发正确性验证，需配合 KCSAN/KASAN 压测。
- **P2-3（SC 捐赠）**：涉及优先级反转防护和 refill 链，复杂度高，仅确有需求时实施。

### 4.2 低风险项

- P0-1、P1-5、P1-1、P1-3(注释)、P1-7、P2-5、P2-11、P2-13 均为单行修复或文档补充，无功能变更风险。

---

## 5. 与 v3.5 审计的关系

v3.5 审计（[27-systematic-audit-v9.0.md](file:///home/spharx/SpharxWorks/airymaxhub/docs-closed/agentrt-linux/00-reviews/_review_v3.5/27-systematic-audit-v9.0.md)）已修复的项不再重复。本报告聚焦 v3.5 未覆盖的**跨项目深度对比**维度：

- v3.5 侧重的 SSoT/IRON 合规性、Kbuild/Makefile 正确性、桩函数合规性已收敛
- v3.6 新增的对比维度：seL4 CNode 语义对齐、openEuler KABI/sched_class/dl_bw 参考、CBS/MCS budget 运行时治理

两者互补：v3.5 保证"做对了"，v3.6 追问"做得够不够好"。
