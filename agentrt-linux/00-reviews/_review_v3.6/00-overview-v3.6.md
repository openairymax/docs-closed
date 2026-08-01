SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 00 — v3.6 深度对比研究主索引

> **文档定位**：agentrt-linux 内核设计深度对比研究 · 主索引
> **对比基准**：openEuler kernel-OLK-6.6 · seL4-master · Airymax agentrt-linux
> **最后更新**：2026-07-30
> **方法论**：逐字节阅读三项目源码，所有引用标注文件路径+行号，严禁编造

---

## 1. 研究范围

本研究对 Airymax agentrt-linux 内核设计与两个参考项目（openEuler OLK-6.6、seL4-master）进行 6 子域深度对比，产出 9 份报告（本索引 + 6 子域对比 + 改进汇总 + 闭环总结）。

### 1.1 三个项目根目录

| 项目 | 路径 | 角色 |
|------|------|------|
| openEuler | `/home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/` | 通用服务器内核参考（KABI/sched_class/dl_bw/LSM） |
| seL4 | `/home/spharx/SpharxWorks/.engineer-reference/seL4-master/` | 形式化微内核参考（CNode/MCS/endpoint/badge） |
| Airymax | `/home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/` | 被评估对象（ALK/sched_tac/airy_lsm/Badge folding） |

### 1.2 Airymax 设计文档

`/home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/` 下 IRON/SSoT/工程标准文档作为约束基线。

---

## 2. 报告清单

| 编号 | 文件 | 主题 | 关键发现数 |
|------|------|------|-----------|
| 00 | [本文件](00-overview-v3.6.md) | 主索引：研究范围/方法论/优先级矩阵 | — |
| 01 | [01-scheduler-comparison](01-scheduler-comparison-v3.6.md) | 调度器：EEVDF/CBS/dl_bw/sched_class vs sched_tac | 6 |
| 02 | [02-security-comparison](02-security-comparison-v3.6.md) | 安全：security_hook_heads/kmem_cache vs airy_lsm 5 钩子 | 6 |
| 03 | [03-ipc-comparison](03-ipc-comparison-v3.6.md) | IPC：endpoint+badge+doIPCTransfer vs io_uring+SPSC ring | 4 |
| 04 | [04-syscall-codegen-comparison](04-syscall-codegen-comparison-v3.6.md) | syscall：syscall_64.tbl/kabi_reserved/xsched vs syscall_gen.py | 4 |
| 05 | [05-capability-cnode-comparison](05-capability-cnode-comparison-v3.6.md) | capability：cap_t/decodeCNodeInvocation/cteRevoke vs Badge/7 操作 | 6 |
| 06 | [06-memory-version-governance](06-memory-version-governance-v3.6.md) | 内存+版本：Untyped/Frame/KABI vs MemoryRovol/ALK/IRON | 4 |
| 07 | [07-improvement-recommendations](07-improvement-recommendations-v3.6.md) | 改进建议汇总：29 项 + 优先级矩阵 + 路线图 | 29 |
| 08 | [08-closure-summary](08-closure-summary-v3.6.md) | 闭环：Go/No-Go 判断 + 成熟度评分 | — |

---

## 3. 关键发现摘要

### 3.1 设计优势（Airymax 领先项）

1. **Badge folding**：64-bit Badge 三段式布局（[ipc.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/ipc.h) L47-63）实现 O(1) 定向撤销 + ~10ns fastpath（已由微基准实测 2-10ns，见 [08-closure-summary](08-closure-summary-v3.6.md) L109 实测标注），优于 seL4 TCB badge 和 POSIX bitmap。
2. **SSoT + codegen CI**：[syscall_gen.py](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/tools/codegen/syscall_gen.py) L310-364 的 check_mode/check_tbl_mode 保证 syscall.xml → syscall.h → syscall_64.tbl 三方一致性，工程严谨性领先。
3. **ALK 策略**：只新增文件不改主线，天然规避 KABI 债务，优于 openEuler KABI_REPLACE/KABI_USE2 宏补丁。
4. **5-phase slowpath**：[airy_cap_check.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_check.c) L191-260 的 ring frozen → CAP_REQUEST → DSL → recheck → enforce 分层校验，防御纵深优于参考项目。

### 3.2 主要差距（需收敛项）

1. **[P0] 预留 syscall 槽未显式登记**：syscall_64.tbl 中 552-571 未登记为 sys_ni_syscall，存在被误占用风险（[报告04](04-syscall-codegen-comparison-v3.6.md)）。
2. **安全入口不对称**：task_kill/file_open 仅检查 agent_state（[airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_lsm.c) L67-109），io_uring_cmd 路径有完整校验。
3. **REVOKE 无级联撤销**：[airy_cap_derive.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_derive.c) L190-206 仅 per-agent epoch+1，已派生 cap 不受影响，seL4 通过 MDB 链递归撤销。
4. **运行时治理缺失**：CBS 带宽准入、budget 入口检查、SC 捐赠、lockdown 均未实现（M2-M5 项）。
5. **可观测性不足**：stc_dispatch.c L73 用 pr_info、stc_stats 未暴露 debugfs（[报告01](01-scheduler-comparison-v3.6.md)）。

---

## 4. 改进点优先级矩阵

### 4.1 P0 — 阻断项（0.1.1 冻结前）

| 编号 | 标题 | 来源 | 工作量 |
|------|------|------|--------|
| P0-1 | 552-571 预留 syscall 槽未显式登记 | 04 | 1h |

### 4.2 P1 — 高优先级（M2 前收敛）

| 编号 | 标题 | 来源 | 工作量 |
|------|------|------|--------|
| P1-1 | stc_dispatch.c pr_info → tracepoint | 01 | 2h |
| P1-2 | stc_stats → debugfs 暴露 | 01 | 3h |
| P1-3 | airy_vtime_decay 语义偏差 | 01 | 1h(注释) |
| P1-4 | task_kill/file_open Badge 校验 | 02 | 4h |
| P1-5 | __aligned(64) → AIRY_ALIGNED(64) | 02/06 | 0.5h |
| P1-6 | airy_inode_sec 接线 VFS | 02 | 8h |
| P1-7 | fastpath_send Badge 决策文档化 | 03 | 1h |
| P1-8 | cancelBadgedSends 等价机制 | 03/05 | 6h |
| P1-9 | REVOKE 级联撤销语义 | 05 | 2h(文档) |
| P1-10 | COPY 权限子集降级 | 05 | 3h |
| P1-11 | 全局 spinlock 可扩展性 | 05 | 8h |

### 4.3 P2 — 中优先级（M3-M5）

17 项，详见 [07-improvement-recommendations](07-improvement-recommendations-v3.6.md) §1.3。

---

## 5. Go/No-Go 判断

| 阶段 | 判断 | 条件 |
|------|------|------|
| M0 设计 | ✅ GO | 修复 P0-1（1h） |
| M1 脚手架 | ✅ GO | -ENOSYS 合规（OS-IRON-004） |
| M2 IPC 集成 | ⚠️ 条件 GO | 收敛 P1-1/P1-4/P1-5 |

**综合成熟度评分：89.5（A-）**——详见 [08-closure-summary](08-closure-summary-v3.6.md)。

---

## 6. 研究方法说明

### 6.1 证据收集

- openEuler：逐行阅读 sched.h（2700+ 行）、security.c、syscall_64.tbl、syscalls.h、sys_ni.c
- seL4：逐行阅读 syscall.c、syscall.h、cnode.c（390+ 行）、endpoint.c、schedcontext.c
- Airymax：逐行阅读 20 个核心源文件（airy_cap.h/airy_lsm.c/airy_cap_check.c/airy_cap_derive.c/airy_ipc_capability.c/airy_ipc_fastpath.c/airy_ipc_ring.c/airy_syscalls.c/stc_dispatch.c/stc_mcs_map.c/stc_stats.c/stc_policy.h/ipc.h/syscalls.h/lsm_types.h/security_types.h/sched.h/airy_ipc_internal.h/syscall_gen.py + syscall_64.tbl Airymax 段）

### 6.2 引用规范

- 所有代码位置使用 `[文件名](file:///绝对路径#L行号)` markdown 链接
- 行号来自实际 Read 工具读取或 grep 确认，严禁编造
- 改进建议每条包含：现状（带行号）+ 参考（带行号）+ 建议 + 风险评估

### 6.3 与 v3.5 审计的关系

v3.5 审计（[27-systematic-audit-v9.0.md](file:///home/spharx/SpharxWorks/airymaxhub/docs-closed/agentrt-linux/00-reviews/_review_v3.5/27-systematic-audit-v9.0.md)）侧重 SSoT/IRON 合规性；v3.6 新增跨项目深度对比维度。两者互补：v3.5 保证"做对了"，v3.6 追问"做得够不够好"。
