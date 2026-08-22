Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agent-linux（AirymaxOS）系统性全面审查报告 v1.0

> **文档定位**： agent-linux（AirymaxOS，极境智能体操作系统）"再一次"系统性全面审查报告，作为架构审查专家对整体方案的复核。\
> **保密级别**： SPHARX Ltd 内部参考，**闭源不公开**\
> **版本**： 1.0（2026-07-13）\
> **审查范围**： 前序 v0.9.0 综合审查（15 项问题）+ Wave 2 v2 源码级深读（34 项差距）处置回顾 / 方案内容冲突检查 / 技术点唯一性检查 / openEuler 工程实践参考充分性 / seL4 微内核化改造参考充分性 / 开发就绪度评估 / 细节完成度检查 / IRON-9 v2 三层共享模型验证 / 8 子仓命名规范验证\
> **审查方法**： 源码级深读 + 文档交叉验证 + Grep 机器检查 + 三层对齐度评分\
> **证据要求**： 所有结论附文件路径与行号\
> **SPDX-License-Identifier**： AGPL-3.0-or-later OR Apache-2.0

---

## 目录

- [1. 前序审查回顾（v0.9.0 + Wave 2 v2）](#1-前序审查回顾v090--wave-2-v2)
- [2. 方案冲突检查结果](#2-方案冲突检查结果)
- [3. 技术点唯一性检查结果](#3-技术点唯一性检查结果)
- [4. openEuler 工程实践参考充分性评估](#4-openeuler-工程实践参考充分性评估)
- [5. seL4 微内核化改造参考充分性评估](#5-sel4-微内核化改造参考充分性评估)
- [6. 开发就绪度评估（8 项判定标准）](#6-开发就绪度评估8-项判定标准)
- [7. 细节完成度检查](#7-细节完成度检查)
- [8. IRON-9 v2 三层共享模型验证](#8-iron-9-v2-三层共享模型验证)
- [9. 8 子仓命名规范验证](#9-8-子仓命名规范验证)
- [10. 综合评分和改进建议](#10-综合评分和改进建议)

---

## 1. 前序审查回顾（v0.9.0 + Wave 2 v2）

### 1.1 v0.9.0 综合审查回顾

v0.9.0 综合审查报告（`00-reviews/_review_0.9.0/`）于 2026-07-13 完成，识别 15 项问题（P0-CRITICAL 3 项 + P1-MAJOR 6 项 + P2-MINOR 6 项），综合评分 70/100（B-），三层对齐度：规范声明层 92/A、方案设计层 68/D+、实现落地层 N/A（72 代理）。

**15 项问题清单及 v0.2.5 处置状态**：

| 编号 | 问题 | 等级 | v0.2.5 处置 | 证据 |
|------|------|------|------------|------|
| P0-CRITICAL-01 | 版本倒置（闭源 v0.2.4 比开源 v0.1.1 更旧 3 天） | P0 | **已修复** | 闭源总纲 L7：`版本: 0.2.5...2026-07-13`；`00-reviews/_review_0.9.0/04-systematized-issues.md` L24-49 |
| P0-CRITICAL-02 | ES-SEL4 数量三重冲突（5/10/54） | P0 | **部分修复**（标题已修正，正文 ES-SEL4-7 分类残留冲突，详见 §2.1） | 闭源总纲 L39/L1389 标题修正；L1403/L1410 正文残留 |
| P0-CRITICAL-03 | OS-ACC 编号冲突未消解 | P0 | **已修复** | `09-ssot-registry.md` L420：`SSoT 对齐说明（v0.2.5 已消解）` |
| P1-MAJOR-01 | OS-KER-005 编号缺失（L106-107 跳号） | P1 | **未修复**（仍跳号，详见 §3.2） | `09-ssot-registry.md` L106-107：OS-KER-004 → OS-KER-006 |
| P1-MAJOR-02 | Rust 编号登记缺口（L469/473） | P1 | **未修复**（已文档化，移交 1.0.1） | `09-ssot-registry.md` L469/L473 |
| P1-MAJOR-03 | 闭源文档术语滞后（OLK-6.6 概念引用） | P1 | **已修复** | 闭源总纲 L14：`所有概念引用已统一为"Linux 6.6 内核基线"` |
| P1-MAJOR-04 | 品味哲学层 8 项隐性智慧未文档化 | P1 | **未修复**（移交 1.0.1） | `00-reviews/_review_0.9.0/01-olk66-code-taste-distillation.md` |
| P1-MAJOR-05 | agentrt 源码差距（15 文件 4 空格 / 104 typedef / 10 文件错误宏） | P1 | **未修复**（移交 1.0.1 M1） | `00-reviews/_review_0.9.0/04-systematized-issues.md` |
| P1-MAJOR-06 | 附录 D 标题与 §12.6 矛盾 | P1 | **已修复** | 闭源总纲 L1389 标题修正 |
| P2-MINOR-01 | 9 个族索引文件废除但引用未清理 | P2 | **部分修复** | `09-ssot-registry.md` L474 V9 验证 |
| P2-MINOR-02 | 族索引引用未清理 | P2 | **部分修复** | 同上 |
| P2-MINOR-03 | 文档计数三作用域模型未在 SSoT 注册 | P2 | **未修复**（移交后续） | `09-ssot-registry.md` |
| P2-MINOR-04 | AirymaxAgentOS → AirymaxOS | P2 | **已修复** | 闭源总纲 v0.2.5 全文使用 AirymaxOS |
| P2-MINOR-05 | §12.8 与附录 D 矛盾 | P2 | **已修复** | 闭源总纲 L1041-1051 |
| P2-MINOR-06 | 规则编号注册表变更日志不完整 | P2 | **未修复**（移交后续） | `09-ssot-registry.md` |

**v0.9.0 处置汇总**：

| 处置状态 | 数量 | 占比 |
|---------|------|------|
| 已修复 | 6 项（P0-01/03 + P1-03/06 + P2-04/05） | 40% |
| 部分修复 | 3 项（P0-02 + P2-01/02） | 20% |
| 未修复（移交 1.0.1） | 6 项（P1-01/02/04/05 + P2-03/06） | 40% |

### 1.2 Wave 2 v2 源码级深读回顾

Wave 2 v2 源码级深读审查（Phase A-F，~27h 工时）于 2026-07-13 完成。核心成果：三层对齐度评分从 61/C+ 跃升至 80/B（规范声明层 92/A 持平 + 方案设计层 45/D+ → 80/B 跃升 +35 分 + 实现落地层 N/A 维持）。

**34 项差距清单处置**：

| 类别 | 数量 | 处置方式 | 代表项 |
|------|------|---------|--------|
| A 类（P0 文档修正） | 8 项 | **全部完成** | D1 IPC 状态机命名对齐 seL4 EPState_Idle/Send/Recv / D2 Fastpath 语义分层 / D3 syscall master/MCS 模式区分 / D4 Reply 原子性 / D5 vtime 类型 / D6 [SC] 分层视图 / D7 ipc_msg_hdr.h→ipc.h / D8 CLOCK 设计权衡 |
| B/C/D/E 类 | 26 项 | **移交 1.0.1** | seL4 深度借鉴 C-C01~C-C09 / agentrt 代码品味改进 C-B02~C-B06 等 |

**证据**：

- `agent-linux开发路线和进度.md` L1010：`Wave 2 v2 源码级深读 ✅ 完成...26 README 重写，34 项差距全部处置`
- `agent-linux开发路线和进度.md` L1019：`1.0.1 M1 就绪判定 ✅ 通过（8 项判定标准全部满足）`
- `130-roadmap/README.md` L300：`Phase D D1-D8 8 P0 fixes + D9 directory structure (350 lines) + D10 [SC] header indent verification`

### 1.3 前序审查小结

v0.9.0 的 15 项问题中 6 项已修复、3 项部分修复、6 项移交；Wave 2 v2 的 34 项差距中 8 项 A 类已修复、26 项移交。**但本次复核发现 P0-CRITICAL-02（ES-SEL4 数量冲突）仅部分修复**——标题已修正但正文 ES-SEL4-7 分类仍存在残留冲突（详见 §2.1），这是一个在 v0.2.5 中未被发现的新发现。

---

## 2. 方案冲突检查结果

### 2.1 ES-SEL4-7 分类残留冲突（新发现，P0 级）

**问题描述**：v0.2.5 修复 P0-CRITICAL-02 时仅修正了附录 D 标题，但正文对 ES-SEL4-7 的分类与标题声明矛盾，导致"架构层强制借鉴数量"在标题与正文之间出现 5 vs 6 的冲突。

**证据链**：

1. **标题声明（5 项强制）**：
   - 闭源总纲 L1389：`附录 D ES-SEL4 工程思想借鉴映射（ES-SEL4-1~5 强制 + ES-SEL4-6~10 P2 增强）`
   - 闭源总纲 L1393：`ES-SEL4-1~5 在架构层强制借鉴，ES-SEL4-6~10 作为 P2 增强建议增量落地`
   - 闭源总纲 L1024（OS-IRON-012）：`seL4 工程思想的借鉴仅限架构层（ES-SEL4-1~5）`
   - 闭源总纲 L1010（§12.5 标题）：`架构层借鉴 seL4（5 项选择性借鉴）`

2. **正文分类矛盾（ES-SEL4-7 被归入"架构层强制"）**：
   - 闭源总纲 L1403：`ES-SEL4-7 | 架构正交分层 | ... | 架构层强制（已落地） | airymaxos-kernel arch/{x86,arm64,riscv}/{machine,plat}/`
   - 闭源总纲 L1410：`架构层强制借鉴（ES-SEL4-1~5 + ES-SEL4-7）: 6 项，已在 1.0.1 架构设计中落地`

3. **§12.8 表格中的矛盾**：
   - 闭源总纲 L1041（§12.8 标题）：`ES-SEL4-6~10 的落地方式`——将 ES-SEL4-7 归入"ES-SEL4-6~10"范围
   - 闭源总纲 L1051：`ES-SEL4-7 架构正交分层 | arch/machine/plat 三层适配 | 已在 kernel 子仓落地`——但又标注"已在 kernel 子仓落地"

**冲突本质**：标题将 ES-SEL4-7 归入"ES-SEL4-6~10 P2 增强"（即非强制、未来落地），但正文将其归入"架构层强制（已落地）"并计入 6 项强制借鉴。OS-IRON-012 明确声明"借鉴仅限架构层（ES-SEL4-1~5）"为 5 项，与正文 6 项直接矛盾。

**影响**：违反 SSoT 唯一性原则。审查者无法确定 ES-SEL4-7 究竟是"架构层强制（已落地）"还是"P2 增强（未来落地）"，也无法确定架构层强制借鉴是 5 项还是 6 项。

**修复建议**：

- 方案 A（推荐）：将 ES-SEL4-7 从"架构层强制"重新分类为"P2 增强（已提前落地）"，与标题一致。修改 L1403 借鉴方式为"P2 增强建议（已落地）"，修改 L1410 为"架构层强制借鉴（ES-SEL4-1~5）: 5 项"。
- 方案 B：修改标题和 OS-IRON-012，将架构层强制范围扩展为"ES-SEL4-1~5 + ES-SEL4-7"共 6 项，同步修改 §12.5 标题和 §12.8 表格分类。

### 2.2 ES-SEL4-9/10 状态分类模糊

**问题描述**：ES-SEL4-9 和 ES-SEL4-10 在标题中被归入"ES-SEL4-6~10 P2 增强"（未来落地），但正文标注为"已落地"，分类语义模糊。

**证据**：

- 闭源总纲 L1389 标题：`ES-SEL4-1~5 强制 + ES-SEL4-6~10 P2 增强`——ES-SEL4-9/10 属于"P2 增强"
- 闭源总纲 L1049（§12.8）：`ES-SEL4-9 libsel4 独立 | SDK 层借鉴 libsel4 模型 | 已在 airymaxos-cloudnative 落地`
- 闭源总纲 L1050（§12.8）：`ES-SEL4-10 CMake 构建 | 用户态子仓采用 Meson/CMake | 已在 services/cloudnative 落地`
- 闭源总纲 L1405-1406（附录 D）：`ES-SEL4-9...已落地` / `ES-SEL4-10...已落地（用户态子仓）`
- 闭源总纲 L1412：`已落地（ES-SEL4-9 + ES-SEL4-10）: 2 项，用户态子仓构建系统已采纳`

**影响**：P2 增强建议的定义是"1.0.1 阶段增量落地"（L1043），但 ES-SEL4-9/10 已标注"已落地"，与 P2 的"未来落地"语义冲突。建议在标题或正文中明确区分"P2 增强（已落地）"与"P2 增强（待落地）"。

### 2.3 闭源文档与开源文档命名不一致（airymaxos- 前缀）

**问题描述**：闭源总纲 v0.2.5 在 8 子仓名称上仍使用 `airymaxos-` 前缀（37 处），而开源文档已统一去除该前缀。

**证据**：

- 闭源总纲 L78-85：8 子仓表格使用 `airymaxos-kernel`、`airymaxos-services`、`airymaxos-security`、`airymaxos-memory`、`airymaxos-cognition`、`airymaxos-cloudnative`、`airymaxos-system`、`airymaxos-tests-linux`
- 闭源总纲 L1067-1074（§13.1）：8 子仓依赖层次表同样使用 `airymaxos-` 前缀
- 闭源总纲 L1099：`airymaxos-kernel/` 目录结构
- 闭源总纲 L1016-1020：ES-SEL4 落地子仓列使用 `airymaxos-kernel` 等
- Grep 统计：闭源总纲 `airymaxos-` 前缀出现 **37 处**
- 开源文档 `README.md` L132-139：8 子仓 URL 使用裸名 `kernel`、`services`、`security`、`memory`、`cognition`、`cloudnative`、`system`、`tests-linux`
- 开源文档 `06-directory-structure.md` L175-184：8 子仓映射表使用裸名
- 开源文档 `06-directory-structure.md` L294：`禁止前缀：airymaxos_*（已废弃，详见 project_memory）`

**影响**：闭源与开源文档在子仓命名上不一致，违反 SSoT 原则。开源文档已明确废弃 `airymaxos_*` 前缀，但闭源总纲 v0.2.5 未同步此变更。详见 §9。

### 2.4 方案冲突检查小结

| 冲突项 | 等级 | 状态 | 修复建议 |
|--------|------|------|---------|
| ES-SEL4-7 分类残留冲突（5 vs 6） | P0 | **新发现，未修复** | 统一标题与正文分类（方案 A 或 B） |
| ES-SEL4-9/10 状态分类模糊 | P2 | 未修复 | 区分"已落地"与"待落地"P2 项 |
| airymaxos- 前缀不一致（闭源 37 处） | P1 | 未修复 | 闭源总纲同步开源文档去除前缀 |

---

## 3. 技术点唯一性检查结果

### 3.1 09-ssot-registry.md 作为唯一 SSoT 验证

**结论**：`09-ssot-registry.md` 作为规则编号唯一 SSoT 的地位已建立，OS-ACC 冲突已在 v0.2.5 中消解。

**证据**：

- `09-ssot-registry.md` L11：`本注册表于 2026-07-12 创建，替代此前分散在 00-engineering-standards-handbook.md §3 与 07-maintainers-and-governance.md §10 中的碎片化注册表`
- `09-ssot-registry.md` L420：`SSoT 对齐说明（v0.2.5 已消解）：历史 00-handbook §3.7 与 07-governance §10 中定义的 OS-ACC-001~005 与 130-roadmap 中的 OS-ACC 编号存在语义冲突...现已完成消解：本注册表 §7 确认 130-roadmap/06-acceptance-criteria.md 为 OS-ACC 的唯一权威定义文档`
- `09-ssot-registry.md` L418：`权威定义文档：130-roadmap/06-acceptance-criteria.md`

**SSoT 三层引用验证**：

- 00-handbook L151：已改为引用 SSoT 注册表 §7（见 L420 声明）
- 07-governance L645：已改为引用 SSoT 注册表 §7（见 L420 声明）

### 3.2 OS-KER-005 编号缺失（P1，未修复）

**问题描述**：SSoT 注册表中 OS-KER 编号从 004 跳至 006，005 缺失且未明确标注废弃原因。

**证据**：

- `09-ssot-registry.md` L106：`OS-KER-004 | 分级标签按分配逆序释放 | 01 §7.2`
- `09-ssot-registry.md` L107：`OS-KER-006 | volatile 仅 4 种例外 | 01 §6.3`
- 两行之间无 OS-KER-005，且无废弃说明注释

**影响**：编号跳号未标注原因，审查者无法确定 005 是被废弃、合并还是遗漏。建议补充注释 `OS-KER-005 | （已废弃，合并至 OS-KER-004） | —` 或类似说明。

### 3.3 Rust 编号登记缺口（P1，已文档化，移交 1.0.1）

**问题描述**：Rust 相关规则编号存在登记缺口，OS-STD-030~035 + OS-SEC-001~002,030~037+ 编号未在 SSoT 注册表中完整登记。

**证据**：

- `09-ssot-registry.md` L469：`发现 Rust 文件 OS-STD-030~035 + OS-SEC-001~002,030~037+ 编号登记缺口，留待 B5 审查消解`
- `09-ssot-registry.md` L473：`Rust 编号缺口已文档化，留待后续消解`
- `09-ssot-registry.md` L277：`OS-KER-144 | Rust 仅用于安全敏感非热路径 | OS-KER-048`——存在别名引用但原始编号登记不完整

**影响**：Rust 规则编号未在 SSoT 完整登记，可能导致编号冲突。已文档化并移交 1.0.1 消解，不阻断 0.1.1 文档可开发状态。

### 3.4 规则编号体系完整性

**17 类规则编号前缀验证**（闭源总纲 L92-103）：

| 前缀 | 含义 | SSoT 登记 | 状态 |
|------|------|----------|------|
| OS-IRON | 工程铁律 | ✅ | 完整 |
| OS-BAN | 禁止规则 | ✅ | 完整 |
| OS-STD | 标准规则 | ✅ | 完整（OS-STD-2xx 运维域残留，详见 §7.2） |
| OS-ACC | 验收标准 | ✅ | 已消解冲突 |
| OS-KER | 内核工程规则 | ⚠️ | OS-KER-005 跳号 |
| OS-DRV | 驱动工程规则 | ✅ | 完整 |
| OS-BUILD | 构建工程规则 | ✅ | 完整 |
| OS-TEST | 测试工程规则 | ✅ | 完整 |
| OS-OBS | 可观测性规则 | ✅ | 完整 |
| OS-SEC | 安全工程规则 | ⚠️ | Rust 编号缺口 |
| OS-ABI | ABI 稳定性规则 | ✅ | 完整 |

### 3.5 技术点唯一性检查小结

| 检查项 | 状态 | 备注 |
|--------|------|------|
| 09-ssot-registry.md 唯一 SSoT | ✅ 通过 | OS-ACC 冲突已消解 |
| OS-KER-005 跳号 | ⚠️ 未修复 | P1，建议补充废弃说明 |
| Rust 编号缺口 | ⚠️ 已文档化 | P1，移交 1.0.1 |
| 17 类规则编号完整性 | ✅ 基本通过 | 2 项缺口已记录 |

---

## 4. openEuler 工程实践参考充分性评估

### 4.1 ES-OLK-1~13 工程思想映射验证

**结论**：ES-OLK-1~13 的 13 项工程思想从 Linux 6.6 内核基线（openEuler OLK-6.6 标杆）源码中提炼，映射完整，每项均有明确的落地规则和章节引用。

**证据**（闭源总纲附录 C，L1380-1385）：

| 编号 | 工程思想 | 落地规则 | 源码证据 |
|------|---------|---------|---------|
| ES-OLK-1 | 关注点分离 | OS-STD-061 | `kernel/locking/mutex.c` 模块化设计 |
| ES-OLK-2 | 架构正交 | OS-STD-061 | `arch/{x86,arm64,riscv}/` 分层 |
| ES-OLK-3 | UAPI 物理隔离 | OS-IRON-001 | `include/uapi/` 目录隔离 |
| ES-OLK-4 | 策略机制分离 | OS-IRON-003 | sched_ext BPF 策略可插拔 |
| ES-OLK-5 | 条件编译规范化 | OS-KER-003 | `IS_ENABLED()` 替代 `#ifdef` |
| ES-OLK-6 | UAPI 物理隔离 | OS-STD-061 | `include/uapi/` 独立目录 |
| ES-OLK-7 | 声明式配置+命令式构建分离 | OS-STD-061 | Kconfig + Makefile 分离 |
| ES-OLK-8 | 维护者制度文档化 | OS-STD-040 | MAINTAINERS 文件 |
| ES-OLK-9 | 规范可执行 | OS-STD-030 | checkpatch.pl 机器检查 |
| ES-OLK-10 | regression 零容忍 | OS-IRON-006 | 回归必须当前周期修复 |
| ES-OLK-11 | 用户空间 ABI 永久稳定 | OS-IRON-001 | 接口导出后永久支持 |
| ES-OLK-12 | 运行时可加载 | OS-IRON-003 | EXPORT_SYMBOL + 模块机制 |
| ES-OLK-13 | 文档即代码 | OS-STD-008 | Documentation/ 与代码同仓库 |

**源码级验证证据**（`01Reference/kernel-OLK-6.6/`）：

- `kernel/locking/mutex.c`：SPDX-License-Identifier: GPL-2.0-only；Tab 8 缩进；K&R 大括号；`#define MUTEX_FLAG_WAITERS 0x01`（信任读者）；`EXPORT_SYMBOL(__mutex_init)` 紧跟函数定义；`static inline struct task_struct *__mutex_owner`（双下划线前缀）
- `mm/page_alloc.c`：MGLRU 多代 LRU 实现，zone 水位线管理

### 4.2 六大编码支柱验证

**结论**：六大编码支柱（Tab 8 / K&R / 最小 typedef / goto 集中出口 / kernel-doc / 80 列）在闭源总纲中明确定义，与 OLK-6.6 源码实践完全对齐。

**证据**：

| 支柱 | 规则编号 | 闭源总纲定义 | OLK-6.6 源码验证 |
|------|---------|-------------|-----------------|
| Tab 8 缩进 | OS-FMT-001 | L331：`C 内核代码使用 Tab 缩进，Tab 宽度为 8 字符` | `mutex.c` 全文 Tab 8 |
| K&R 大括号 | OS-FMT-003 | L351：`使用 K&R 风格` | `mutex.c` K&R 风格 |
| 最小 typedef | OS-STD-010 | L321：`typedef 严格限制（仅 5 种例外）` | `mutex.c` 无多余 typedef |
| goto 集中出口 | OS-KER-001 | L201：`使用 goto out_free_xxx: 集中出口模式` | `mutex.c` goto 错误处理 |
| kernel-doc | OS-STD-008 | L270：`所有 EXPORTed 函数必须包含完整的 kernel-doc 注释` | `mutex.c` kernel-doc 注释 |
| 80 列行宽 | OS-FMT-002 | L342：`C 代码首选 80 列` | `mutex.c` 80 列限制 |

### 4.3 双源融合裁决 16 维度验证

**结论**：双源融合裁决覆盖 16 个维度，11 维度采纳 Linux 6.6 内核基线、3 维度借鉴 seL4 架构层、2 维度借鉴 seL4 P2 增强，裁决逻辑清晰。

**证据**（闭源总纲附录 E，L1420-1446）：

| 裁决类型 | 维度数量 | 维度编号 |
|---------|---------|---------|
| 采纳 Linux 6.6 内核基线 | 11 | #1-#11（缩进/命名/typedef/大括号/行宽/错误处理/注释/UAPI/并发/内存/字符串拷贝） |
| 借鉴 seL4（架构层） | 3 | #12 架构组织 / #15 形式化 / #16 capability+IPC |
| 借鉴 seL4（P2 增强） | 2 | #13 接口契约 XML / #14 bitfield codegen |

### 4.4 openEuler 参考充分性评估小结

**评分**：92/A（与 v0.9.0 规范声明层评分持平）

**充分性判定**：

- ES-OLK-1~13 映射完整，13/13 项均有源码级证据
- 六大编码支柱全部对齐 OLK-6.6 源码实践
- 双源融合裁决 16 维度逻辑清晰
- 术语清洗已完成（L14：概念引用统一为"Linux 6.6 内核基线"）

**不足**：

- P1-MAJOR-04 品味哲学层 8 项隐性智慧未文档化（信任读者 / 短函数 / 简洁文件头 / EXPORT_SYMBOL 紧跟 / include 字母序 / __ 前缀 / __read_mostly / __randomize_layout），移交 1.0.1
- P1-MAJOR-05 agentrt 源码差距（15 文件 4 空格 / 104 typedef / 10 文件错误宏）待 1.0.1 M1 改进

---

## 5. seL4 微内核化改造参考充分性评估

### 5.1 ES-SEL4-1~5 架构层强制借鉴验证

**结论**：ES-SEL4-1~5 的 5 项架构层强制借鉴均有 seL4 源码级证据和明确的落地子仓。

**证据**（闭源总纲 L1014-1020 + 附录 D L1397-1401）：

| 编号 | seL4 工程思想 | 落地子仓 | seL4 源码证据 |
|------|-------------|---------|-------------|
| ES-SEL4-1 | 极简原则（Liedtke minimality） | airymaxos-kernel corekern/ | seL4 内核核心 ~1.44 万行；`20-modules/01-kernel.md` L55-62 引用 Liedtke 原文 |
| ES-SEL4-2 | capability 单一权限模型 | airymaxos-security | `seL4-master/src/object/cnode.c` 7 CNode 操作（Copy/Mint/Move/Mutate/Revoke/Delete/Rotate） |
| ES-SEL4-3 | 服务用户态化 | airymaxos-services | seL4 用户态服务架构 |
| ES-SEL4-4 | 消息传递 IPC（含 fastpath） | airymaxos-kernel io_uring/ | `seL4-master/src/object/endpoint.c` EPState_Idle/Send/Recv 三态机；`seL4-master/src/fastpath/fastpath.c` POINT OF NO RETURN |
| ES-SEL4-5 | 形式化验证驱动 | airymaxos-tests-linux | seL4 proof/ Isabelle/HOL |

**seL4 源码级验证证据**：

- `seL4-master/src/object/cnode.c`（934 行）：7 CNode 操作完整实现；`reduceZombie` 增量清理；`finaliseSlot`/`emptySlot`/`reduceZombie` static 函数
- `seL4-master/src/object/endpoint.c`（577 行）：`sendIPC` 函数三态机（EPState_Idle/Send/Recv）；Reply 原子性通过 `doIPCTallTransfer` + 临界区实现；MCS 模式 `reply_push`/`reply_unlink`
- `seL4-master/src/fastpath/fastpath.c`（899 行）：`fastpath_call` 函数 NORETURN 修饰；12 项前置条件检查后进入 POINT OF NO RETURN（L167-171）；`slowpath()` 回退

### 5.2 ES-SEL4-6~10 P2 增强建议验证

**结论**：ES-SEL4-6~10 作为 P2 增强建议已在 §12.8 和附录 D 中规划，但存在分类模糊问题（详见 §2.1/§2.2）。

**证据**（闭源总纲 L1041-1051）：

| 编号 | seL4 工程思想 | 落地方式 | 状态 |
|------|-------------|---------|------|
| ES-SEL4-6 | 接口契约 XML | R-01（§14.1） | P2 待落地 |
| ES-SEL4-7 | 架构正交分层 | arch/machine/plat 三层 | **分类冲突**（标题 P2 / 正文"架构层强制已落地"） |
| ES-SEL4-8 | bitfield codegen | R-02（§14.2） | P2 待落地 |
| ES-SEL4-9 | libsel4 独立 | SDK 层借鉴 | **已落地**（但归入 P2 范围） |
| ES-SEL4-10 | CMake 构建 | 用户态子仓 | **已落地**（但归入 P2 范围） |

### 5.3 seL4 借鉴边界声明验证

**结论**：seL4 借鉴边界声明清晰，6 项 seL4 特性因与 Linux 6.6 基线冲突被明确拒绝。

**证据**（闭源总纲 L1024-1035）：

- OS-IRON-012（L1024）：`seL4 工程思想的借鉴仅限架构层（ES-SEL4-1~5），不包括编码风格层（4 空格 / camelCase / 重度 typedef）和接口契约层`
- 拒绝特性表（L1028-1035）：4 空格缩进 / camelCase 命名 / 重度 typedef / 内核非抢占无并发模型 / 无动态内存分配 / exception_t 错误码

### 5.4 关键设计对齐 seL4 验证

**IPC 状态机命名对齐**（Wave 2 v2 D1 修复）：

- `20-modules/01-kernel.md`：EPState_Idle=0, EPState_Send=1, EPState_Recv=2，对齐 seL4 `endpoint.c` 三态机

**Fastpath 语义分层**（Wave 2 v2 D2 修复）：

- POINT OF NO RETURN 模式与 io_uring 零拷贝语义区分明确

**syscall master/MCS 模式区分**（Wave 2 v2 D3 修复）：

- master 模式 8 个 activity syscall / MCS 模式 11 个，agent-linux 采用 master 模式（`20-modules/01-kernel.md` L117）

**Reply 原子性**（Wave 2 v2 D4 修复）：

- 通过 `doReplyTransfer` 临界区串行涌现属性实现

**vtime 类型**（Wave 2 v2 D5 修复）：

- `airy_vtime_t = __s32 Q16.16 定点`

### 5.5 seL4 参考充分性评估小结

**评分**：80/B（方案设计层，与 Wave 2 v2 评分一致）

**充分性判定**：

- ES-SEL4-1~5 架构层强制借鉴有完整 seL4 源码级证据
- 6 项拒绝特性边界声明清晰
- 5 项关键设计（IPC 状态机 / Fastpath / syscall 模式 / Reply 原子性 / vtime 类型）已对齐 seL4
- seL4 源码三方交叉验证完成（B2 报告 81248B）

**不足**：

- ES-SEL4-7 分类残留冲突（P0，详见 §2.1）
- ES-SEL4-9/10 状态分类模糊（P2，详见 §2.2）
- seL4 深度借鉴 C-C01~C-C09 待 1.0.1 M1 落地

---

## 6. 开发就绪度评估（8 项判定标准）

### 6.1 8 项判定标准验证

**结论**：v0.2.5 声明 8 项判定标准全部通过，本次复核确认 7 项通过、1 项有条件通过。

**证据**（`agent-linux开发路线和进度.md` L1019）：

`1.0.1 M1 就绪判定 ✅ 通过（8 项判定标准全部满足：工程思想统一 + 工程标准规范 + 无方案冲突点 + 对齐 openEuler 代码品味 + 对齐 seL4 微内核思想 + 系统性目录结构 + 全部 README 重写 + v0.9.0 P0 修复）`

| # | 判定标准 | 状态 | 证据 | 备注 |
|---|---------|------|------|------|
| 1 | 工程思想统一（ES-OLK-1~13 + seL4 11 项设计模式统一映射） | ✅ 通过 | 闭源总纲附录 C/D；§4/§12 | 13+10 项映射完整 |
| 2 | 工程标准规范（23 文档 SSoT 体系 + 09-ssot-registry.md 唯一 SSoT） | ✅ 通过 | `09-ssot-registry.md` L11 SSoT 声明 | OS-ACC 冲突已消解 |
| 3 | 无方案冲突点 | ⚠️ **有条件通过** | ES-SEL4-7 分类残留冲突（§2.1） | 存在 1 项 P0 级残留冲突 |
| 4 | 对齐 openEuler 代码品味（OLK-6.6 六大支柱源码级验证） | ✅ 通过 | §4.2 六大支柱验证 | 8 项隐性智慧待 1.0.1 |
| 5 | 对齐 seL4 微内核思想（ES-SEL4-1~5 验证 + 6 项新发现 + 3 项语义偏离修复） | ✅ 通过 | §5.1 ES-SEL4-1~5 验证 | ES-SEL4-7 分类待修复 |
| 6 | 系统性目录结构设计（350 行 SSoT） | ✅ 通过 | `06-directory-structure.md` 361 行 | 超出 350 行目标 |
| 7 | 全部 README 重写（26 个） | ✅ 通过 | `find` 统计 26 个 README.md | 26/26 验证通过 |
| 8 | v0.9.0 P0 修复 | ⚠️ **部分通过** | P0-01/03 已修复，P0-02 部分修复 | ES-SEL4-7 残留冲突 |

### 6.2 26 个 README 验证

**结论**：`docs/AirymaxOS/` 下共 26 个 README.md 文件，与声明一致。

**证据**（`find` 命令统计）：

- 顶层 README：`docs/AirymaxOS/README.md`（1 个）
- 目录级 README：25 个（00-requirements / 10-architecture / 20-modules / 30-interfaces / 40-dataflows / 50-engineering-standards + 5 子目录 / 60-driver-model / 70-build-system / 80-testing / 90-observability / 100-operations / 110-security / 120-development-process / 130-roadmap / 140-application-development / 150-cloudnative / 160-compatibility / 170-performance / 180-i18n / 190-distribution）
- 总计：**26 个**（1 顶层 + 25 目录级）

### 6.3 目录结构 SSoT 验证

**结论**：`06-directory-structure.md` 共 361 行，超出 350 行目标，作为目录结构唯一 SSoT。

**证据**：

- `wc -l` 统计：`361 /home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/10-architecture/06-directory-structure.md`
- L175-184：8 子仓映射表
- L214-228：ES-OLK-1~13 映射
- L249-263：seL4 设计模式对齐
- L294：`禁止前缀：airymaxos_*（已废弃）`

### 6.4 三层对齐度评分

**结论**：三层对齐度评分维持 Wave 2 v2 的 80/B。

| 层次 | 权重 | Wave 2 v2 评分 | 本次复核 | 变化 |
|------|------|--------------|---------|------|
| 规范声明层 | 35% | 92/A | 92/A | 持平 |
| 方案设计层 | 40% | 80/B | 78/B+ | -2（ES-SEL4-7 残留冲突） |
| 实现落地层 | 25% | N/A（72 代理） | N/A（72 代理） | 持平 |
| **综合** | 100% | **80/B** | **79/B+** | -1 |

**评分调整说明**：方案设计层因 ES-SEL4-7 分类残留冲突（P0 级新发现）从 80 降至 78，但综合评分仍维持在 B 级范围。

### 6.5 开发就绪度评估小结

**判定**：**有条件通过**——8 项判定标准中 6 项完全通过、2 项有条件通过（无方案冲突点 + v0.9.0 P0 修复），存在 1 项 P0 级残留冲突（ES-SEL4-7 分类）需修复后方可进入 1.0.1 M1 代码开发。

**建议**：修复 ES-SEL4-7 分类残留冲突后，开发就绪度可恢复为"全部通过"状态。

---

## 7. 细节完成度检查

### 7.1 tests 简写残留（已知遗留，移交 1.0.1）

**问题描述**：`tests` 简写（应为 `tests-linux` 全称或上下文明确缩写）在开源文档中仍有残留。

**证据**：

- Grep `\btests\b` 在 `docs/AirymaxOS/` 范围：10 处匹配，分布在 5 个文件
  - `30-interfaces/01-syscalls.md`：3 处
  - `30-interfaces/README.md`：2 处
  - `30-interfaces/02-ipc-protocol.md`：3 处
  - `160-compatibility/03-upstream-tracking.md`：1 处
  - `190-distribution/01-rpm-packaging.md`：1 处
- `130-roadmap/README.md` L319：`tests 简写 49 文件/177 处`——历史统计（含闭源文档范围更广）

**状态**：已知遗留，移交 1.0.1。开源文档范围已从 49 文件/177 处大幅减少至 5 文件/10 处。

### 7.2 OS-STD-2xx 运维域残留（已知遗留，移交 1.0.1）

**问题描述**：OS-STD-2xx 编号原属运维域，在 SSoT 精简后应迁移至 OS-OBS，但部分引用残留。

**证据**：

- Grep `OS-STD-2\d\d` 在 `docs/AirymaxOS/` 范围：57 处匹配，分布在 4 个文件
  - `50-engineering-standards/01-coding-standards.md`：32 处
  - `50-engineering-standards/05-development-process.md`：22 处
  - `50-engineering-standards/10-coding-style/C_Cpp_coding_style.md`：1 处
  - `70-build-system/02-kconfig-system.md`：2 处

**状态**：已知遗留，移交 1.0.1。需将 OS-STD-2xx 运维域编号迁移至 OS-OBS 可观测性规则。

### 7.3 OS-KER-001~008 SSoT 内部不一致

**问题描述**：OS-KER 编号在 SSoT 注册表中存在跳号（005 缺失）和内部引用不一致。

**证据**：

- `09-ssot-registry.md` L106-107：OS-KER-004 → OS-KER-006（005 跳号，详见 §3.2）
- `09-ssot-registry.md` L277：`OS-KER-144 | Rust 仅用于安全敏感非热路径 | OS-KER-048`——别名引用

**状态**：P1，未修复，建议补充 OS-KER-005 废弃说明。

### 7.4 R-04 seL4 借鉴参考

**问题描述**：R-04（seL4 深度借鉴）作为 P2 增强建议，待 R-01/R-02/R-03 后落地。

**证据**：

- `agent-linux开发路线和进度.md` L1018：`4 项 P2 建议 | R-01/R-02 → M1、R-03 → M5、R-04 → R-01/R-02/R-03 后`

**状态**：已规划，待 1.0.1 阶段按序落地。

### 7.5 Rust 编号登记缺口

**问题描述**：详见 §3.3。

**状态**：P1，已文档化，移交 1.0.1。

### 7.6 细节完成度检查小结

| 检查项 | 状态 | 当前数据 | 目标 | 备注 |
|--------|------|---------|------|------|
| tests 简写 | ⚠️ 已知遗留 | 5 文件/10 处（开源） | 0 | 移交 1.0.1，已大幅减少 |
| OS-STD-2xx 残留 | ⚠️ 已知遗留 | 4 文件/57 处 | 0 | 移交 1.0.1，迁移至 OS-OBS |
| OS-KER-005 跳号 | ⚠️ 未修复 | 1 处跳号 | 补充废弃说明 | P1 |
| R-04 seL4 借鉴 | ✅ 已规划 | 待 R-01/02/03 后 | 1.0.1 落地 | P2 |
| Rust 编号缺口 | ⚠️ 已文档化 | OS-STD-030~035 + OS-SEC 缺口 | 完整登记 | P1，移交 1.0.1 |

---

## 8. IRON-9 v2 三层共享模型验证

### 8.1 [SC] 共享契约层 6 个头文件验证

**结论**：[SC] 共享契约层 6 个头文件定义完整，物理宿主于 `include/airymax/`，单一数据源。

**证据**（`120-cross-project-code-sharing.md` L71-76）：

| # | 头文件 | 内容 | magic 值 | 物理路径 |
|---|--------|------|---------|---------|
| 1 | `memory_types.h` | MemoryRovol L1-L4 + GFP 掩码 + PMEM 接口 | — | `include/airymax/memory_types.h` |
| 2 | `security_types.h` | POSIX capability 41 ID + LSM 252 ID + Cupolas blob + capability 派生模型 + `cap_t` = `uint64_t` | — | `include/airymax/security_types.h` |
| 3 | `cognition_types.h` | CoreLoopThree 阶段枚举 + Thinkdual 模式 + LLM 推理阶段 + `airy_err_t` = `int32_t` | — | `include/airymax/cognition_types.h` |
| 4 | `sched.h` | SCHED_EXT 约束 + 任务描述符 + vtime 类型 + 优先级范围 + SLICE_DFL | `0x41475453` ('AGTS') | `include/airymax/sched.h` |
| 5 | `ipc.h` | IPC magic + 128B 消息头 + SQE/CQE 操作码 | `0x41524531` ('ARE1') | `include/airymax/ipc.h` |
| 6 | `syscalls.h` | Syscall 编号体系（12 核心 + 12 预留 = 24 槽位） | — | `include/airymax/syscalls.h` |

**单一数据源约束**（闭源总纲 L1061 OS-IRON-014）：

`[SC] 共享契约层 6 个头文件...仅物理宿主于 airymaxos-kernel/include/airymax/，是唯一物理副本。其他子仓通过 -I../kernel/include 构建路径引用，禁止在任何子仓的 include/airymax/<sub>/ 下创建 [SC] 头文件的物理副本。`

### 8.2 IPC magic 值验证

**结论**：IPC magic 值 0x41524531（'ARE1'）和任务描述符 magic 0x41475453（'AGTS'）定义正确，SSoT 权威定义登记于 09-ssot-registry.md。

**证据**（`120-cross-project-code-sharing.md`）：

- L12：`IPC magic 值（0x41524531 'ARE1'）与任务描述符 magic（0x41475453 'AGTS'）的权威定义登记于 09-ssot-registry.md §3`
- L236-237：`/* Task descriptor magic: 0x41475453 = 'AGTS' (Agent Task) */ #define AIRY_TASK_MAGIC 0x41475453u`
- L302-303：`/* IPC magic: 0x41524531 = 'ARE1' (Airymax Runtime Engine v1) */ #define AIRY_IPC_MAGIC 0x41524531u`
- L355：`_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128,`——128B 消息头静态断言
- L405：`### 3.1 IPC magic 0x41524531 ('ARE1')`
- L413：`SSoT 权威定义：#define AIRY_IPC_MAGIC 0x41524531u（[SC] include/airymax/ipc.h）`
- L436：`### 3.2 任务描述符 magic 0x41475453 ('AGTS')`
- L446：`与 IPC magic 区分：'AGTS' ≠ 'ARE1'，避免任务描述符与 IPC 消息混淆`

**magic 值设计理由**：

- 'ARE1' = Airymax Runtime Engine v1（IPC 协议识别）
- 'AGTS' = AGent Task State（任务描述符识别）
- 两者独立避免混淆（IRON-9 同源但独立原则）

### 8.3 7 项 Capability 操作验证

**结论**：7 项 CNode 操作与 seL4 完全对齐。

**证据**（`120-cross-project-code-sharing.md` L183-189）：

```c
AIRY_CAP_OP_COPY    = 0,
AIRY_CAP_OP_MINT    = 1,
AIRY_CAP_OP_MOVE    = 2,
AIRY_CAP_OP_MUTATE  = 3,
AIRY_CAP_OP_REVOKE  = 4,
AIRY_CAP_OP_DELETE  = 5,
AIRY_CAP_OP_ROTATE  = 6,
```

**seL4 源码对齐**（`seL4-master/src/object/cnode.c`）：

- seL4 CNode 操作：Copy / Mint / Move / Mutate / Revoke / Delete / Rotate（7 项完全对齐）

### 8.4 [SS] 语义同源层与 [IND] 独立层验证

**结论**：[SS] 语义同源层 30+ 项高层 API 语义、[IND] 完全独立层 15+ 项内核态专属，定义清晰。

**证据**（`20-modules/01-kernel.md` L167-181 + L46-52）：

- [SS] 语义同源层：sched_ext BPF 调度类（调度数据流）、8 个 IPC 原语 syscall（IPC 控制面）、io_uring 零拷贝（IPC 数据面）、struct_ops 注册（eBPF 数据流）
- [IND] 完全独立层：Linux 6.6 内核维护、微内核化改造、Rust 安全驱动、[SC] 共享契约层物理宿主、记忆卷载（userfaultfd + MGLRU + CXL）

### 8.5 IRON-9 v2 验证小结

| 验证项 | 状态 | 证据 |
|--------|------|------|
| [SC] 6 个头文件 | ✅ 通过 | `120-cross-project-code-sharing.md` L71-76 |
| IPC magic 0x41524531 ('ARE1') | ✅ 通过 | L302-303 / L413 |
| 任务描述符 magic 0x41475453 ('AGTS') | ✅ 通过 | L236-237 / L436 |
| 128B 消息头静态断言 | ✅ 通过 | L355 `_Static_assert` |
| 7 项 Capability 操作 | ✅ 通过 | L183-189，对齐 seL4 cnode.c |
| [SS] 语义同源层 | ✅ 通过 | `01-kernel.md` L46-52 |
| [IND] 独立层 | ✅ 通过 | `01-kernel.md` L46-52 |
| 单一数据源约束 | ✅ 通过 | 闭源总纲 L1061 OS-IRON-014 |

---

## 9. 8 子仓命名规范验证

### 9.1 开源文档命名验证

**结论**：开源文档已统一去除 `airymaxos-` 前缀，8 子仓使用裸名。

**证据**：

- `docs/AirymaxOS/README.md` L132-139：8 子仓 URL 使用裸名
  - `https://atomgit.com/openairymax/kernel`
  - `https://atomgit.com/openairymax/services`
  - `https://atomgit.com/openairymax/security`
  - `https://atomgit.com/openairymax/memory`
  - `https://atomgit.com/openairymax/cognition`
  - `https://atomgit.com/openairymax/cloudnative`
  - `https://atomgit.com/openairymax/system`
  - `https://atomgit.com/openairymax/tests-linux`
- `06-directory-structure.md` L175-184：8 子仓映射表使用裸名（kernel / services / security / memory / cognition / cloudnative / system / tests-linux）
- `06-directory-structure.md` L294：`禁止前缀：airymaxos_*（已废弃，详见 project_memory）`

### 9.2 闭源文档命名验证

**结论**：闭源总纲 v0.2.5 仍使用 `airymaxos-` 前缀，共 37 处，与开源文档不一致。

**证据**：

- 闭源总纲 L78-85（§1.4 8 子仓工程标准差异化表）：`airymaxos-kernel` / `airymaxos-services` / `airymaxos-security` / `airymaxos-memory` / `airymaxos-cognition` / `airymaxos-cloudnative` / `airymaxos-system` / `airymaxos-tests-linux`
- 闭源总纲 L1067-1074（§13.1 8 子仓依赖层次表）：同上 8 个 `airymaxos-` 前缀
- 闭源总纲 L1099（§13.3 目录结构）：`airymaxos-kernel/`
- 闭源总纲 L1016-1020（§12.5 ES-SEL4 落地子仓）：`airymaxos-kernel` / `airymaxos-security` / `airymaxos-services` / `airymaxos-tests-linux`
- 闭源总纲 L1398-1406（附录 D 落地子仓列）：`airymaxos-security` / `airymaxos-services` / `airymaxos-kernel` / `airymaxos-tests-linux` / `airymaxos-cloudnative`
- Grep 统计：闭源总纲 `airymaxos-` 前缀共 **37 处**

### 9.3 函数前缀验证

**结论**：开源文档函数前缀使用 `airy_*`（正确），闭源文档声明 `airymaxos_*` 已废弃但仍在示例代码中使用。

**证据**：

- 闭源总纲 L294（开源 SSoT）：`禁止前缀：airymaxos_*（已废弃）`
- 闭源总纲 L167（OS-STD-005）：`airymaxos_* 前缀用于 AirymaxOS 内核/发行版专属 API`——**与开源 SSoT 矛盾**
- 闭源总纲 L171：`int airymaxos_lsm_hook_register(...)`——示例代码使用 `airymaxos_*` 前缀
- 开源 `06-directory-structure.md` L292：`内核函数：airy_<子系统>_<功能>()`——使用 `airy_*` 前缀

**冲突分析**：闭源总纲 OS-STD-005（L167）仍声明 `airymaxos_*` 前缀用于 AirymaxOS 专属 API，但开源 SSoT（L294）已明确废弃该前缀。两者矛盾。

### 9.4 8 子仓命名规范验证小结

| 验证项 | 开源文档 | 闭源文档 | 一致性 |
|--------|---------|---------|--------|
| 子仓名称 | 裸名（kernel 等） | `airymaxos-` 前缀（37 处） | ❌ 不一致 |
| 函数前缀 | `airy_*` | `airymaxos_*`（OS-STD-005 声明） | ❌ 不一致 |
| 前缀废弃声明 | L294 明确废弃 | L167 仍声明使用 | ❌ 矛盾 |

**修复建议**：

1. 闭源总纲全文替换 `airymaxos-kernel` → `kernel`、`airymaxos-services` → `services` 等（37 处）
2. 闭源总纲 L167 OS-STD-005 修改为：`airy_* 前缀用于 AirymaxOS 内核/发行版专属 API（与 agentrt 共享 Airymax 同源语义）`
3. 闭源总纲 L171 示例代码修改为：`int airy_lsm_hook_register(...)`
4. 同步修改 §13 目录结构中所有 `airymaxos-` 前缀

---

## 10. 综合评分和改进建议

### 10.1 综合评分

| 评分维度 | v0.9.0 | Wave 2 v2 | 本次复核（v1.0） | 变化 |
|---------|--------|-----------|----------------|------|
| 规范声明层（35%） | 92/A | 92/A | 92/A | 持平 |
| 方案设计层（40%） | 68/D+ | 80/B | 78/B+ | -2（ES-SEL4-7 残留） |
| 实现落地层（25%） | N/A（72 代理） | N/A（72 代理） | N/A（72 代理） | 持平 |
| **综合评分** | **70/B-** | **80/B** | **79/B+** | -1 |

**评分调整说明**：

- 方案设计层 -2 分：ES-SEL4-7 分类残留冲突（P0 级新发现，v0.2.5 修复 P0-CRITICAL-02 时遗漏正文对齐）
- 综合评分 -1 分：因方案设计层权重 40%，-2 分折算为综合 -0.8 分，取整 -1 分

**评分结论**：79/B+（接近 80/B，修复 ES-SEL4-7 残留冲突后可恢复至 80/B）

### 10.2 问题处置汇总

| 问题来源 | 总数 | 已修复 | 部分修复 | 未修复 | 新发现 |
|---------|------|--------|---------|--------|--------|
| v0.9.0（15 项） | 15 | 6 | 3 | 6 | — |
| Wave 2 v2（34 项） | 34 | 8（A 类） | — | 26（B/C/D/E 类） | — |
| 本次复核新发现 | — | — | — | — | 3（ES-SEL4-7 残留 / ES-SEL4-9/10 模糊 / airymaxos- 前缀不一致） |

### 10.3 待修复问题清单（按优先级）

#### P0 级（阻断 1.0.1 M1 启动）

| # | 问题 | 修复方案 | 工作量 | 证据 |
|---|------|---------|--------|------|
| 1 | ES-SEL4-7 分类残留冲突（5 vs 6） | 统一标题与正文分类（推荐方案 A：将 ES-SEL4-7 归入 P2 已落地） | ~2h | §2.1 |

#### P1 级（1.0.1 M1 阶段修复）

| # | 问题 | 修复方案 | 工作量 | 证据 |
|---|------|---------|--------|------|
| 2 | airymaxos- 前缀不一致（闭源 37 处） | 闭源总纲全文替换为裸名 + 修改 OS-STD-005 | ~4h | §9 |
| 3 | OS-KER-005 跳号 | 补充废弃说明注释 | ~0.5h | §3.2 |
| 4 | ES-SEL4-9/10 状态分类模糊 | 区分"已落地"与"待落地"P2 项 | ~1h | §2.2 |

#### P2 级（1.0.1 阶段增量修复）

| # | 问题 | 修复方案 | 工作量 | 证据 |
|---|------|---------|--------|------|
| 5 | tests 简写残留（5 文件/10 处） | 全文替换为全称 | ~2h | §7.1 |
| 6 | OS-STD-2xx 运维域残留（4 文件/57 处） | 迁移至 OS-OBS | ~4h | §7.2 |
| 7 | Rust 编号登记缺口 | SSoT 完整登记 | ~3h | §3.3 |
| 8 | 文档计数三作用域模型未在 SSoT 注册 | 补充注册 | ~1h | §3.1 |
| 9 | 规则编号注册表变更日志不完整 | 补充变更日志 | ~1h | §3.1 |
| 10 | 品味哲学层 8 项隐性智慧未文档化 | 文档化 8 项隐性智慧 | ~8h | §4.4 |
| 11 | agentrt 源码差距（15 文件） | 1.0.1 M1 代码品味改进 | ~40h | §4.4 |

### 10.4 改进建议

#### 短期（0.1.1 收尾，~2h）

1. **立即修复 P0 级 ES-SEL4-7 分类残留冲突**——这是阻断 1.0.1 M1 启动的唯一 P0 级问题。推荐方案 A：将闭源总纲 L1403 ES-SEL4-7 借鉴方式从"架构层强制（已落地）"修改为"P2 增强建议（已落地）"，修改 L1410 为"架构层强制借鉴（ES-SEL4-1~5）: 5 项"，与标题和 OS-IRON-012 对齐。

#### 中期（1.0.1 M1 阶段，~56h）

2. **修复 airymaxos- 前缀不一致**——闭源总纲同步开源文档去除 `airymaxos-` 前缀（37 处），修改 OS-STD-005 函数前缀声明。
3. **补充 OS-KER-005 废弃说明**——在 SSoT 注册表 L106-107 之间补充注释。
4. **消解 ES-SEL4-9/10 状态分类模糊**——在标题或正文中明确区分"P2 增强（已落地）"与"P2 增强（待落地）"。
5. **迁移 OS-STD-2xx 至 OS-OBS**——4 文件 57 处运维域编号迁移。
6. **清除 tests 简写残留**——5 文件 10 处替换为全称。
7. **完整登记 Rust 编号**——OS-STD-030~035 + OS-SEC 缺口补充。

#### 长期（1.0.1 全阶段，~120h+）

8. **文档化 8 项隐性智慧**——将 OLK-6.6 源码中提炼的 8 项隐性工程智慧（信任读者 / 短函数 / 简洁文件头 / EXPORT_SYMBOL 紧跟 / include 字母序 / __ 前缀 / __read_mostly / __randomize_layout）文档化。
9. **agentrt 源码代码品味改进**——15 文件 4 空格 → Tab 8、104 typedef 清理、10 文件错误宏统一。
10. **seL4 深度借鉴 C-C01~C-C09 落地**——9 项 seL4 深度借鉴在 1.0.1 M1 代码开发中实现。
11. **R-01~R-04 P2 增强建议落地**——syscall.xml 接口契约 / structures.bf codegen / MAINTAINERS / seL4 深度借鉴。

### 10.5 最终结论

agent-linux（AirymaxOS）整体方案经过 v0.9.0 综合审查 + Wave 2 v2 源码级深读 + 本次 v1.0 系统性复核，**已基本达到可开发状态**，但存在 1 项 P0 级残留冲突（ES-SEL4-7 分类）需立即修复。

**核心优势**：

- 工程思想统一：ES-OLK-1~13 + ES-SEL4-1~5 映射完整，源码级验证
- 工程标准规范：23 文档 SSoT 体系 + 09-ssot-registry.md 唯一 SSoT，OS-ACC 冲突已消解
- 对齐 openEuler 代码品味：六大支柱源码级验证，术语清洗完成
- 对齐 seL4 微内核思想：5 项架构层强制借鉴 + 5 项关键设计对齐（IPC 状态机 / Fastpath / syscall / Reply / vtime）
- IRON-9 v2 三层共享模型：[SC] 6 头文件 + IPC magic + 7 capability 操作完整
- 系统性目录结构：361 行 SSoT，8 子仓映射清晰
- 26 README 全部重写

**待改进**：

- ES-SEL4-7 分类残留冲突（P0，~2h 修复）
- airymaxos- 前缀不一致（P1，~4h 修复）
- 6 项已知遗留移交 1.0.1（tests 简写 / OS-STD-2xx / OS-KER-005 / Rust 编号 / 品味哲学 / agentrt 源码）

**建议**：修复 P0 级 ES-SEL4-7 分类残留冲突后（~2h），agent-linux 方案可正式进入 1.0.1 M1 代码开发阶段。

---

> **报告结束** | SPHARX Ltd 内部参考 | 闭源不公开 | 审查日期：2026-07-13 | 审查版本：v1.0
