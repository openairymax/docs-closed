SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 08 — 闭环总结与 Go/No-Go 判断

> **文档定位**：v3.6 深度对比研究 · 闭环总结
> **研究范围**：openEuler kernel-OLK-6.6 · seL4-master · Airymax agent-linux 全量对比
> **最后更新**：2026-07-30
> **前置文档**：[00-overview](00-overview-v3.6.md) · [01-06 子域报告](01-scheduler-comparison-v3.6.md) · [07 改进建议](07-improvement-recommendations-v3.6.md)

---

## 1. 研究结论

### 1.1 核心发现

本次深度对比研究覆盖 6 个子域（调度器/安全/IPC/syscall/capability/内存版本治理），产出 29 项改进建议（1 P0 + 11 P1 + 17 P2）。核心发现如下：

1. **Airymax 的工程基线自洽性良好**：ALK"只新增文件"策略天然规避了 openEuler KABI 兼容性债务，SSoT + codegen CI 校验（[syscall_gen.py](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/tools/codegen/syscall_gen.py) L310-364）在工程严谨性上领先参考项目。

2. **Badge folding 设计优于参考项目**：64-bit Badge（[ipc.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/ipc.h) L47-63）的 epoch+randtag+perms 三段式布局，实现了 O(1) 定向撤销（[airy_ipc_capability.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/ipc/airy_ipc_capability.c) L61-71）和 ~10ns fastpath 校验（[airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap.h) L50-77），在防重放和性能上优于 seL4 的 TCB badge 存储和 POSIX bitmap。

3. **主要差距集中在运行时治理层**：调度带宽准入、budget 入口检查、SC 捐赠、lockdown 机制等"动态治理"能力缺失。这些是 M2-M5 阶段的功能实现项，不影响 M0/M1 基线自洽性。

4. **安全入口存在不对称**：io_uring_cmd 路径有完整 5-phase 校验（[airy_cap_check.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_check.c) L191-260），但 task_kill/file_open 仅检查 agent_state（[airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_lsm.c) L67-109）。这是 M2 前需收敛的 P1 安全项。

### 1.2 与参考项目的定位差异

| 维度 | openEuler | seL4 | Airymax |
|------|-----------|------|---------|
| 设计目标 | 通用服务器内核 | 形式化验证微内核 | Agent RT 内核 |
| 兼容性策略 | KABI 宏保持二进制兼容 | 无兼容性债务（全新 ABI） | ALK 只新增文件 + IRON-001 UAPI 永不破坏 |
| 调度可扩展性 | BPF_SCHED 动态注入 | 无（编译期固定） | 纯 C 静态映射（禁 sched_ext） |
| 安全模型 | LSM hook 头表 + POSIX cap | cap_t 联合体 + CNode 派生 | 64-bit Badge + capability folding |
| IPC 模型 | System V / io_uring | endpoint 阻塞式 | io_uring + SPSC 无锁 ring |

Airymax 的定位是**在 Linux 6.6 成熟基础设施之上叠加 Agent 运行时能力**，而非重写内核。这决定了其"映射而非新增"的工程哲学是正确的。

---

## 2. Go/No-Go 判断

### 2.1 M0 设计阶段：✅ GO（附带 1 项 P0 修复）

M0 设计基线基本自洽，仅 1 项 P0 需在 0.1.1 冻结前修复：

- **P0-1**：syscall_64.tbl 中 552-571 预留槽位未显式登记为 `sys_ni_syscall`，存在被误占用风险。修复工作量 1h。

其余 P1 项均为 M2 前收敛项，不阻断 M0 完成。

### 2.2 M1 脚手架阶段：✅ GO

M1 的 4 个 syscall（[airy_syscalls.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/syscalls/airy_syscalls.c) L78-198）返回 -ENOSYS 是合规的 OS-IRON-004 渐进式开发，不是 IRON-2 桩函数违规。SYSCALL_DEFINE 宏使用规范，参数校验充分。

### 2.3 M2 io_uring IPC 集成：⚠️ 条件 GO

M2 启动前需完成以下 P1 收敛：

1. P1-4：task_kill/file_open 增加 Badge 校验（安全入口对称性）
2. P1-1：pr_info → tracepoint（fastpath 性能）
3. P1-5：__aligned → AIRY_ALIGNED（IRON-016 合规）

---

## 3. 成熟度评分

| 维度 | v3.5 评分 | v3.6 评分 | 变化 | 说明 |
|------|-----------|-----------|------|------|
| 工程标准合规 | 90 (A-) | 92 (A) | +2 | P0-1 修复后达 93 |
| 架构自洽性 | 90 (A-) | 91 (A-) | +1 | ALK 策略验证充分 |
| 安全完整性 | 85 (B+) | 86 (B+) | +1 | 发现入口不对称，M2 收敛 |
| 调度器成熟度 | 85 (B+) | 85 (B+) | 0 | 运行时治理为 M2-M5 项 |
| IPC 性能 | 88 (B+) | 88 (B+) | 0 | fastpath 设计优秀，缺 cancelBadgedSends |
| 对比研究覆盖 | N/A | 95 (A) | NEW | 6 子域全量对比 |

**综合评分：89.5（A-）**——M0 设计阶段就绪，M2 前需收敛 3 项 P1。

---

## 4. 后续工作

### 4.1 立即执行（0.1.1 冻结前）

- [ ] P0-1：syscall_64.tbl 增加 552-571 显式占位
- [ ] P1-5：__aligned → AIRY_ALIGNED
- [ ] P1-1：pr_info → tracepoint
- [ ] P1-3(注释)：airy_vtime_decay 注释修正
- [ ] P1-7/P2-5/P2-11/P2-13：4 项文档化决策

### 4.2 M2 前收敛

- [ ] P1-2：stc_stats → debugfs
- [ ] P1-4：task_kill/file_open Badge 校验
- [ ] P1-8：cancelBadgedSends 实现
- [ ] P1-10：COPY 权限降级
- [ ] P2-2：syscall 入口 budget guard

### 4.3 M3-M5 渐进

- [ ] P1-6/P1-9/P1-11：VFS 接线 / derive_tree / per-bucket 锁
- [ ] P2-1/P2-3/P2-4/P2-14：CBS 准入 / SC 捐赠 / lockdown / MemoryRovol

---

## 5. 研究局限性

1. **openEuler 证据来自 OLK-6.6 单一版本**：未对比 RHEL/Ubuntu 等其他发行版的调度/安全扩展。
2. **seL4 证据来自 master 分支**：未区分 MCS 与非 MCS 配置的编译时差异（cnode.c L36-40）。
3. **性能数据为设计估算**：~10ns Badge 校验、~158ns fastpath 等数据来自设计文档，未在本轮实测验证。
4. **Airymax 代码为 M1 脚手架状态**：syscall 返回 -ENOSYS，部分建议需待 M2-M5 真实实现后重新评估。

---

## 6. 结论

Airymax agent-linux 的内核设计在 ALK 约束下做出了合理的工程权衡。通过 seL4 CNode 语义对齐和 openEuler KABI/sched_class 参考，本次研究确认了 Airymax 的 capability folding 和"映射而非新增"策略的正确性，同时识别出 29 项可执行的改进建议。

**Go 判断成立**：M0 设计阶段就绪，0.1.1 冻结前修复 1 项 P0 + 4 项低工作量 P1/P2 即可进入 M2。
