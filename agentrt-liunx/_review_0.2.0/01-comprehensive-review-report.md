Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agentrt-liunx（AirymaxOS）技术方案全面审查与完善报告 v0.2.0

> **审查日期**: 2026-07-09
> **审查版本**: v0.2.0（在 v0.1.1 基础上的二次完善审查）
> **审查范围**: OpenAirymax/docs/AirymaxAgentOS/（125 篇开源文档）+ docs-closed/agentrt-liunx/（闭源审查文档）
> **参考基线**:
> - seL4 源码：/home/spharx/SpharxWorks/01Reference/seL4-master
> - openEuler 内核源码：/home/spharx/SpharxWorks/01Reference/kernel-OLK-6.6
> **审查维度**: 合规性 / 文档完整性 / 工程标准 / 技术正确性 / 交付就绪度
> **目标**: 成熟度 100%

---

## 目录

1. [审查概述](#1-审查概述)
2. [v0.1.1 → v0.2.0 变更总览](#2-v011--v020-变更总览)
3. [本轮修复工作详述](#3-本轮修复工作详述)
4. [二次问题检查结果](#4-二次问题检查结果)
5. [阶段 H 验证清单（18 项）](#5-阶段-h-验证清单18-项)
6. [成熟度评估](#6-成熟度评估)
7. [剩余事项与建议](#7-剩余事项与建议)
8. [最终结论](#8-最终结论)

---

## 1. 审查概述

### 1.1 审查目标

本报告记录 agentrt-liunx（AirymaxOS，极境智能体操作系统）技术设计方案在 v0.1.1 文档体系完成后的**第二轮全面审查与完善**工作。本轮审查在 v0.1.1 首轮审查（v0.1.1 综合评分 93/100，"有条件 Go"）的基础上，执行用户提出的 **8 项注意点 + 6 项执行任务**，目标为**成熟度 100%**。

### 1.2 8 项注意点（硬约束）

| 编号 | 注意点 | 执行状态 |
|------|--------|----------|
| 1 | agentrt（用户态）使用"微核心"（micro-core）；agentrt-liunx（OS 发行版）使用"微内核"（micro-kernel），不能混淆 | ✅ 已验证 |
| 2 | `_review_0.1.1` 不在开源公开仓库中，移到 `docs-closed/agentrt-liunx` | ✅ 已迁移 |
| 3 | openEuler 相关描述只能在管理仓或大纲性质的非核心文档中 | ✅ 已验证（12 处合法引用） |
| 4 | Capital_Specifications 整合到 50-engineering-standards，然后删除 | ✅ 内容已迁移，交叉引用已更新 |
| 5 | 开源商业化"开发标准"整理到 `docs/AirymaxStandards` | ✅ 7 文件 3718 行已完成 |
| 6 | agentrt 和 agentrt-liunx 代码共享最大化 | ✅ IRON-9 v2 [SC] 6 个头文件 |
| 7 | 内核是严肃工程，不能为创新忽视风险 | ✅ seL4 形式化验证方案 |
| 8 | C 语言代码编写规范额外注重 | ✅ 8 文件 4684 行工程标准 |

### 1.3 6 项执行任务

| 编号 | 执行任务 | 执行状态 |
|------|---------|----------|
| 1 | 基于已有 docs/AirymaxAgentOS 全部设计方案进行问题检查 | ✅ 完成（二次问题检查） |
| 2 | 研究 01Reference/kernel-OLK-6.6 源代码，对比 agentrt-liunx 弱点加强 | ✅ 完成（02-olk66-source-mapping） |
| 3 | 所有方案文档不能有占位文档，编写实施示例和示例代码 | ✅ 完成（140-190 目录 27 文件） |
| 4 | seL4 源码参考，制定详尽方案 | ✅ 完成（03-microkernel-design-ref） |
| 5 | 遵循乔布斯设计思想，简约又极致的细节 | ✅ 贯穿全部文档 |
| 6 | 交付成果：审查报告 + 修订文档集 + 工程标准规范手册 | ✅ 本报告即交付成果 |

### 1.4 审查范围统计

| 文档类别 | 文件数 | 总行数 | 覆盖率 |
|---------|--------|--------|--------|
| 开源文档（docs/AirymaxAgentOS/） | 125 | ~80,000+ | 100% |
| 开放标准（docs/AirymaxStandards/） | 7 | ~3,718 | 100% |
| 闭源审查文档（docs-closed/agentrt-liunx/） | ~35 | ~20,000+ | 100% |
| seL4 源码验证路径 | — | — | 关键路径全覆盖 |
| OLK-6.6 源码验证路径 | 12 | — | 关键路径全覆盖 |

---

## 2. v0.1.1 → v0.2.0 变更总览

### 2.1 阶段 A-F 完成情况

| 阶段 | 内容 | 产出 | 状态 |
|------|------|------|------|
| A | 文件迁移与目录重组 | _review_0.1.1 迁移至 docs-closed | ✅ |
| B | 140-160 目录充实 | 9 文件 5,520 行 | ✅ |
| C | seL4 改造方案 | 700 行微内核设计参考 | ✅ |
| D | 170-190 目录充实 | 18 文件 ~12,500 行 | ✅ |
| E | 工程标准 8 文件 | 4,684 行 | ✅ |
| F | AirymaxStandards 7 文件 | 3,718 行 | ✅ |

### 2.2 本轮专项修复

| 修复项 | 文件数 | 修改处数 | 状态 |
|--------|--------|---------|------|
| Task #114: SCHED_AGENT 宏违规 | 1 | 1 处 | ✅ |
| Task #115: [SC] 头文件 4→6 统一 | 12 | 20+ 处 | ✅ |
| 150-cloud-native → 150-cloudnative | 7 | 14 处 | ✅ |
| Capital_Specifications 交叉引用更新 | 5 | 5 处 | ✅ |
| SCHED_AGENT 宏（02-posix-compat.md） | 1 | 2 处 | ✅ |
| Copyright 头补全 | 2 | 2 处 | ✅ |

---

## 3. 本轮修复工作详述

### 3.1 Task #114: SCHED_AGENT 调度类编号违规修复

**问题**：`#define SCHED_AGENT 7` 与 OLK-6.6 已有的 `SCHED_EXT=7`（`include/uapi/linux/sched.h:121`）编号冲突。

**修复**：
- 删除 `#define SCHED_AGENT 7` 宏定义
- 改为 `#define SCHED_AGENT_NAME "sched_agent"`（BPF 策略名称字符串）
- 添加注释说明复用内核 SCHED_EXT=7

**影响文件**：`40-dataflows/04-scheduling-flow.md`（前轮修复）、`160-compatibility/02-posix-compat.md`（本轮修复）

### 3.2 Task #115: [SC] 头文件数量 4→6 统一

**问题**：IRON-9 v2 [SC] 共享契约层头文件从基础 4 个扩展至 6 个（新增 `sched.h` 和 `ipc.h`），但 12 个文件仍引用旧的"4 个头文件"。

**6 个 [SC] 头文件清单**：

| 头文件 | 内容 |
|--------|------|
| `bpf_struct_ops.h` | sched_ext BPF 调度器 struct_ops 状态机 + common_value |
| `memory_types.h` | MemoryRovol L1-L4 数据结构 + GFP 掩码语义 + PMEM 持久化接口 |
| `security_types.h` | Cupolas capability 令牌 + POSIX cap 38 ID + LSM 254 ID + 派生模型 + Vault backend |
| `cognition_types.h` | CoreLoopThree 阶段枚举 + Thinkdual 模式 + LLM 推理阶段 + Token 能效 |
| `sched.h` | SCHED_EXT 约束 + 任务描述符（magic 0x41475453）+ vtime 衰减 + 优先级 0-139 |
| `ipc.h` | IPC magic（0x41524531）+ 128B 消息头结构 + SQE/CQE 操作码 |

**修复规模**：
- 15 处简单数量修复（"4 个" → "6 个"）
- 1 处整章重写（`agentrt_integration.md` 第 2.2 节，~235 行）
- 3 处 Mermaid 图修复
- 4 处 `error_code_reference.md` 概念性调整
- 1 处错误码 [SC]→[SS] 层级修正（错误码属于 [SS] 语义同源层）
- 2 处错误头文件名表格替换

**影响文件（12 个）**：
1. `20-modules/README.md`
2. `40-dataflows/README.md`
3. `TERMINOLOGY.md`
4. `50-engineering-standards/10-coding-style/README.md`
5. `50-engineering-standards/10-coding-style/C_coding_style_standard.md`
6. `50-engineering-standards/10-coding-style/Rust_coding_style_standard.md`
7. `50-engineering-standards/20-contracts/README.md`
8. `50-engineering-standards/20-contracts/syscall_api_contract.md`
9. `50-engineering-standards/40-integration/agentrt_integration.md`
10. `50-engineering-standards/40-integration/README.md`
11. `50-engineering-standards/08-compliance-checklist.md`
12. `50-engineering-standards/50-project-erp/error_code_reference.md`

### 3.3 150-cloud-native → 150-cloudnative 目录名统一

**问题**：实际目录名为 `150-cloudnative`（无连字符），但 14 处文档引用为 `150-cloud-native`（有连字符）。

**修复**：7 个文件 14 处全部替换为 `150-cloudnative`。

**影响文件（7 个）**：
1. `150-cloudnative/README.md`（1 处）
2. `130-roadmap/01-development-strategy.md`（1 处）
3. `130-roadmap/06-acceptance-criteria.md`（6 处）
4. `130-roadmap/02-milestones-and-timeline.md`（3 处）
5. `130-roadmap/03-resource-estimation.md`（1 处）
6. `20-modules/README.md`（1 处）
7. `README.md`（1 处，含链接文本和路径）

### 3.4 Capital_Specifications 交叉引用更新

**问题**：`Capital_Specifications` 内容已迁移至 `50-engineering-standards/`（2026-07-08 完成），但 5 处 AirymaxAgentOS 文档仍引用旧路径。

**修复**：更新为 `50-engineering-standards/10-coding-style/` 等新路径。

**影响文件（5 个）**：
1. `30-interfaces/04-coding-standard.md`（2 处）
2. `10-architecture/04-engineering-baseline.md`（1 处）
3. `10-architecture/02-five-dimensional-principles.md`（1 处）
4. `TERMINOLOGY.md`（1 处路径修正）

**保留引用**：`50-engineering-standards/README.md` 中 6 处历史迁移说明（`原 Capital_Specifications/...`）为合法追溯记录，保留不动。

### 3.5 SCHED_AGENT 宏违规（02-posix-compat.md）

**问题**：`160-compatibility/02-posix-compat.md:252` 定义了 `#define SCHED_AGENT 7`，与 OLK-6.6 SCHED_EXT=7 冲突。

**修复**：
- 替换为 `#define SCHED_AGENT_NAME "sched_agent"`（BPF 策略名称）
- 添加注释说明复用内核 SCHED_EXT=7，禁止定义 SCHED_AGENT 调度类编号宏
- 更新兼容性表格 `SCHED_AGENT` → `SCHED_EXT`

### 3.6 Copyright 头补全

**问题**：2 个文件缺少 Copyright 头。

**修复**：
1. `00-requirements/README.md` — 添加 Copyright
2. `10-architecture/04-engineering-baseline.md` — 添加 Copyright

---

## 4. 二次问题检查结果

在阶段 A-F 全部完成后，执行了系统化的二次问题检查（Grep 全文档扫描），检查 4 类禁词/违规表述：

### 4.1 "微内核原语" 检查（5 处）

| 文件 | 行号 | 上下文 | 判定 |
|------|------|--------|------|
| `180-i18n/03-doc-i18n.md` | 318 | `"微内核原语": "微核心原语"` 术语对照表左侧 | ✅ 合法引用 |
| `180-i18n/03-doc-i18n.md` | 617 | `"微内核原语" → 应使用 "微核心原语"` 禁词清单说明 | ✅ 合法引用 |
| `120-cross-project-code-sharing.md` | 21 | `禁止用"微内核原语"描述 agentrt` 禁止声明 | ✅ 合法引用 |
| `70-kernel-doc-standard.md` | 22 | `不称"微内核原语"` 术语规范声明 | ✅ 合法引用 |
| `170-performance/01-scheduling-performance.md` | 32 | `禁止使用"微内核原语"描述 agentrt` 禁止声明 | ✅ 合法引用 |

**结论**：5 处全部为合法引用（禁词清单/术语对照表/禁止声明），符合"仅允许在审查报告、变更日志和修复计划中作为合法引用保留"规则。**无需修改**。

### 4.2 "MGLRU 2.0" 检查（3 处）

| 文件 | 行号 | 上下文 | 判定 |
|------|------|--------|------|
| `00-engineering-standards-handbook.md` | 300 | `MGLRU 2.0 \| MGLRU 多代 LRU` 禁词对照表 | ✅ 合法引用 |
| `00-engineering-standards-handbook.md` | 386 | `grep -rE "MGLRU 2.0\|..."` 检查脚本 | ✅ 合法引用 |
| `00-engineering-standards-handbook.md` | 433 | `MGLRU 2.0 清零 ✅ 已完成` 修复记录 | ✅ 合法引用 |

**结论**：3 处全部为合法引用（禁词对照表/检查脚本/修复记录）。**无需修改**。

### 4.3 "openEuler|Euler" 检查（12 处）

| 文件 | 行号 | 上下文 | 判定 |
|------|------|--------|------|
| `180-i18n/03-cjk-support.md` | 33 | `禁止使用 openEuler/Euler 字样` 禁止声明 | ✅ 合法引用 |
| `180-i18n/02-error-message-i18n.md` | 38 | `不使用 openEuler/Euler 字样` 声明 | ✅ 合法引用 |
| `180-i18n/03-doc-i18n.md` | 38,316,317,616 | 禁止声明 + 术语对照表 + 禁词清单 | ✅ 合法引用 |
| `180-i18n/01-locale-design.md` | 33 | `禁止使用 openEuler/Euler 字样` | ✅ 合法引用 |
| `190-distribution/01-rpm-packaging.md` | 33 | `禁止使用 openEuler/Euler 字样` | ✅ 合法引用 |
| `190-distribution/03-installer-design.md` | 38 | `不使用 openEuler/Euler 字样` | ✅ 合法引用 |
| `190-distribution/02-installer-design.md` | 33 | `禁止使用 openEuler/Euler 字样` | ✅ 合法引用 |
| `190-distribution/02-dnf-repo-design.md` | 38 | `不使用 openEuler/Euler 字样` | ✅ 合法引用 |
| `190-distribution/03-update-mechanism.md` | 33 | `禁止使用 openEuler/Euler 字样` | ✅ 合法引用 |

**结论**：12 处全部为合法引用（禁止声明/术语对照表/禁词清单说明）。所有文档均明确声明"禁止使用 openEuler/Euler 字样"并将外部 Linux 发行版统一表述为"主流 Linux 发行版"。**无需修改**。

### 4.4 "150-cloud-native" 检查（14 处）

**结论**：14 处全部为实际目录名引用错误，**已全部修复**为 `150-cloudnative`。修复后验证残留 0。

---

## 5. 阶段 H 验证清单（18 项）

| 编号 | 验证项 |