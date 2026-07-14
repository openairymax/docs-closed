Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# Airymax 文档规范与质量控制 v2.1 复审报告

> **文档定位**：v2.1 文档侧复审收敛报告，覆盖 `docs/`（开源）与 `docs-closed/`（闭源）两个仓库的文档规范与质量控制，作为 1.0.1 M1 启动前文档侧阻断项的判定基线之一。
> **保密级别**：SPHARX Ltd 内部参考，**闭源不公开**。
> **版本**：2.1（2026-07-13）。
> **审查范围**：开源 `docs/AirymaxOS/`（123 .md）+ `docs/AirymaxRT/`（88 .md + 3 .drawio）+ `docs/OpenStandards/`（8 主标准 + 3 _research 目录）+ `docs/Publications/` + 闭源 `docs-closed/agentrt/` + `docs-closed/agentrt-linux/`，共 5 个文档子仓库；228 个开源 .md + 225 个闭源 .md。
> **审查方法**：13 关键词 Grep 机器检查 + URL 格式 Grep 验证 + 路径有效性实测（`ls`/`find`）+ 内部引用解析性抽样（20 文件）+ 跨仓库前缀迁移统计 + 上下游关系交叉对照 + 与 v1.0 综合分析（`docs-closed/agentrt/_review_v1.0/00-comprehensive-analysis.md`）和 v2.0 文档质量控制（`docs-closed/_review_v2.0/01-document-quality-control.md`）结论对照。
> **证据要求**：所有结论附文件路径与行号（格式：`文件路径:L行号`），可通过 Grep/Read 工具复核。
> **SPDX-License-Identifier**：AGPL-3.0-or-later OR Apache-2.0。

---

## 目录

- [1. 执行摘要](#1-执行摘要)
- [2. 内部审查描述清理验证](#2-内部审查描述清理验证)
- [3. URL 格式验证](#3-url-格式验证)
- [4. 开源/闭源边界确认](#4-开源闭源边界确认)
- [5. 断裂引用修复验证](#5-断裂引用修复验证)
- [6. 反抄袭检查](#6-反抄袭检查)
- [7. 闭源文档准确性](#7-闭源文档准确性)
- [8. 上下游关系描述准确性](#8-上下游关系描述准确性)
- [9. 模板文件和占位符检查](#9-模板文件和占位符检查)
- [10. 综合评分与改进建议](#10-综合评分与改进建议)

---

## 1. 执行摘要

### 1.1 审查目标与边界

本报告是 v2.1 文档规范与质量控制维度的复审，**聚焦于验证 v1.0 提出的 7 项背景问题在 v2.1 阶段的修复状态**，并新增 v1.0 未覆盖的内部研究文档越界、跨边界引用、邮箱域名标准化等 3 类问题。本报告不重复 v1.0 综合分析已覆盖的源码正确性、IPC 头三重违规、ES-SEL4-7 分类冲突等源码/方案侧问题。

### 1.2 v1.0 vs v2.1 评分对比表

| 评分维度 | v1.0 评分 | v2.1 评分 | 趋势 | 关键变化 |
|---------|---------|---------|------|---------|
| 内部审查描述清理 | 60/D（30 文件 50 处编辑清理完成） | **78/B+** | ↑ +18 | 13 关键词中 12 项零残留；但 `docs/OpenStandards/_research_v1.0/v2.0/v2.1/` 3 目录越界存放内部审查报告（未跟踪文件） |
| URL 格式一致性 | 75/B（部分 SSH 残留） | **100/A+** | ↑ +25 | `git@atomgit.com` / `git@` 零匹配；49 处 atomgit.com 全部 https 格式 |
| 开源/闭源边界 | 65/C+（边界基本清晰） | **55/C**（**倒退**） | ↓ -10 | 4 处开源文档跨引用闭源 `../../../DocsClosed/0.1.1详细任务清单.md`；3 个 _research 内部审查目录误入开源 |
| 断裂引用修复 | 35/D-（5 仓库全部存在引用错误） | **30/D-**（**倒退**） | ↓ -5 | v1.0 标记的 `docs/AirymaxOS/TERMINOLOGY.md` 断裂引用**未修复**；新增 8+ 处 `08-compliance-checklist.md` 断裂、25 处 `00-basic-theories/` 断裂、23 处 `30-coding-standard/` 断裂、4 处 `PROTOCOL_GUIDE.md` 断裂 |
| 反抄袭合规 | 80/B+ | **85/B+** | ↑ +5 | seL4/Linux/openEuler/OCI/CNCF 引用全部附 URL；"参考声明"明确"借鉴非移植"；未发现直接复制 |
| 闭源文档准确性 | 70/B-（agentos_* 前缀背离） | **65/C+**（**倒退**） | ↓ -5 | 子系统规范层 `airy_*` 已对齐；但工程标准手册 `agentrt_*` 仍 22 处（agentrt-linux）+ 218 处（agentrt）残留；版本号 v0.2.5（闭源）vs v0.1.1（开源）差距 4 个小版本 |
| 上下游关系描述 | 65/C+ | **78/B+** | ↑ +13 | agentrt（微核心）↔ agentrt-linux（微内核）5 维同源映射准确；OpenStandards 公开标准 vs 工程标准内部规范的边界清晰；2 个符号链接全部正确 |
| 模板与占位符 | —（v1.0 未覆盖） | **80/B**（新增） | — | 未发现 `@spharx.ai` 虚构邮箱；TBD 仅用于 1.0.1 未启动版本日期（合理）；`your-team@spharx.cn` 1 处占位需替换；4 个邮箱域名（.cn/.com/.io/.dev）未统一 |
| **总评** | **58/D+** | **68/C+** | **↑ +10** | URL 与上下游关系显著改善；但断裂引用系统性扩散（v1.0 标记项未修复 + 新增 60+ 处）、开源/闭源边界出现新违规、闭源前缀迁移停滞 |

### 1.3 核心结论

> **5 个文档仓库当前仍未达到"文档侧可开发"状态**：v1.0 标记的 1 处断裂引用（`docs/AirymaxOS/TERMINOLOGY.md`）**在 v2.1 中仍未修复**，且由于 2026-07-12/13 的两次文件迁移（TERMINOLOGY.md → 90-terminology.md、08-compliance-checklist.md → 05-development-process.md Part III）未同步更新引用方，**断裂引用数量从 v1.0 的"5 仓库全部存在"恶化为 v2.1 的"60+ 处跨 30+ 文件"**。同时 `docs/OpenStandards/_research_v1.0/v2.0/v2.1/` 3 个内部审查报告目录误入开源工作树（虽未跟踪但已违反边界原则），4 处开源文档跨引用闭源 `DocsClosed/0.1.1详细任务清单.md`，构成新的边界违规。闭源 `agentrt_` → `airy_` 前缀迁移在子系统规范层已完成但工程标准手册层停滞（606 处残留）。

### 1.4 与 v1.0 / v2.0 的关系

本报告**沿用 v1.0 综合分析（`docs-closed/agentrt/_review_v1.0/00-comprehensive-analysis.md`）**关于 P0-9（文件路径引用错误）的判定，并经本次实测**确认问题不仅未修复反而扩散**；同时**沿用 v2.0 文档质量控制（`docs-closed/_review_v2.0/01-document-quality-control.md`）**关于引用路径体系系统性失效的判定，并新增**内部研究文档越界、跨边界引用、闭源前缀迁移停滞、邮箱域名未标准化** 4 类 v1.0/v2.0 未覆盖的问题。

---

## 2. 内部审查描述清理验证

### 2.1 13 关键词 Grep 机器检查结果

对 `docs/` 全量执行 13 个关键词 Grep 检查，结果如下：

| # | 关键词 | 匹配文件数 | 匹配行数 | 评估 |
|---|--------|----------|---------|------|
| 1 | `Wave 2 v2` | 0 | 0 | ✅ 清理彻底 |
| 2 | `审查状态` | 1 | 2 | ⚠️ 合法技术内容（见 §2.2） |
| 3 | `Phase D 修复说明` | 0 | 0 | ✅ 清理彻底 |
| 4 | `Phase A/B/C/D` | 0 | 0 | ✅ 清理彻底 |
| 5 | `源码级深读审查` | 0 | 0 | ✅ 清理彻底 |
| 6 | `审查里程碑` | 0 | 0 | ✅ 清理彻底 |
| 7 | `Phase D 审查状态声明` | 0 | 0 | ✅ 清理彻底 |
| 8 | `D7 修复说明` | 0 | 0 | ✅ 清理彻底 |
| 9 | `D9`（上下文相关） | 0 | 0 | ✅ 清理彻底 |
| 10 | `D10`（上下文相关） | 0 | 0 | ✅ 清理彻底 |
| 11 | `_review_0.7.0` | 0 | 0 | ✅ 清理彻底 |
| 12 | `_review_0.9.0` | 0 | 0 | ✅ 清理彻底 |
| 13 | `_review_v1.0` | 0 | 0 | ✅ 清理彻底 |

**结论**：13 个关键词中 12 个零残留，v1.0 阶段的 30 文件 50 处编辑清理**对文件内容而言是彻底的**。Git 历史中仍可见提交消息 `668a56f docs: 完成Wave 2 v2源码级深读审查全流程落地`，但提交元数据不属于文件内容审查范围。

### 2.2 "审查状态" 2 处匹配的合法性判定

| 文件路径:行号 | 上下文 | 判定 |
|--------------|--------|------|
| `docs/AirymaxOS/120-development-process/01-patch-lifecycle.md:219` | PR 模板字段 `### 审查状态`（含 Reviewed-by 复选框、CI 状态、签字状态） | ✅ 合法技术内容（开发流程文档中的 PR 模板字段） |
| `docs/AirymaxOS/120-development-process/01-patch-lifecycle.md:817` | C 结构体字段注释 `/* 审查状态 */`（含 `subsystem_reviewed`、`develop_nightly_pass`、`ci_all_green`、`protocol_signed`、`airy_compat_test` 5 个 bool 字段） | ✅ 合法技术内容（补丁数据结构定义） |

**结论**：2 处"审查状态"匹配均为合法技术内容，**不属于内部审查描述残留**。

### 2.3 新发现：`docs/OpenStandards/_research_v1.0/v2.0/v2.1/` 3 目录越界存放内部审查报告

虽然 13 关键词在已跟踪文件中零残留，但本次 Grep 在 **未跟踪文件** 中发现 3 个内部审查报告目录误入开源工作树：

| 目录路径 | 文件 | 文档定位声明 | 状态声明 | Git 跟踪状态 |
|---------|------|------------|---------|-------------|
| `docs/OpenStandards/_research_v1.0/` | `01-open-standards-rebuild-proposal.md`（1147 行） | "OpenStandards 内部研究文档（_research_v1.0 系列）" | "待标准委员会评审" | **未跟踪**（`git status` 显示 `OpenStandards/_research_v1.0/`） |
| `docs/OpenStandards/_research_v2.0/` | `01-open-standards-optimization-v2.md`（1088 行） | "OpenStandards 内部研究文档（_research_v2.0 系列）" | "待标准委员会评审" | **未跟踪** |
| `docs/OpenStandards/_research_v2.1/` | `01-open-standards-review-v2.1.md`（1011 行） | "OpenStandards 内部研究文档（_research_v2.1 系列）" | "待标准委员会评审" | **未跟踪** |

**证据**（`docs/OpenStandards/_research_v2.1/01-open-standards-review-v2.1.md:5-10`）：

```
> **文档定位**: OpenStandards 内部研究文档（_research_v2.1 系列）
> **版本**: 1.0（复审报告草案）
> **最后更新**: 2026-07-13
> **SPDX-License-Identifier**: CC-BY-4.0
> **作者**: OpenStandards 复审小组
> **状态**: 待标准委员会评审
```

**问题严重性**：
1. 文档自身明确标注"内部研究文档"和"待标准委员会评审"，与开源 `docs/` 的"可公开设计文档"定位冲突。
2. 文档包含内部评分表（如 v2.0 vs v2.1 评分对比表）、内部审查方法（"静态审查"、"基线比对"）、内部决策建议（"建议在第 1 阶段交付物中追加 `PATENTS-LEGAL-REVIEW.md`"），属于内部审查报告性质。
3. 文档头部 `Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.` 与开源 `docs/` 的双许可证（AGPL-3.0-or-later OR Apache-2.0）声明不一致。
4. 虽然当前未跟踪（不会随 `git push` 进入开源仓库），但物理路径已在开源工作树中，存在误提交风险。

**建议**：将 3 个 `_research_v*` 目录整体迁移至 `docs-closed/agentrt/_research_open-standards/` 或 `docs-closed/_research_open-standards/`，并在 `docs/.gitignore` 中追加 `OpenStandards/_research_*/` 排除规则作为双保险。

### 2.4 补充搜索：`审查报告` 关键词在 docs/ 下的匹配

对 `审查报告` 关键词执行补充 Grep，结果 3 处匹配：

| 文件路径:行号 | 上下文 | 判定 |
|--------------|--------|------|
| `docs/OpenStandards/_research_v2.0/01-open-standards-optimization-v2.md:3` | 标题 `# Airymax 开放标准第二轮优化审查报告（v2.0）` | ❌ 内部审查报告（同 §2.3） |
| `docs/OpenStandards/_research_v2.0/01-open-standards-optimization-v2.md:990` | `本 v2.0 优化审查报告基于对 v1.0 重建方案的逐项验证...` | ❌ 内部审查报告（同 §2.3） |
| `docs/AirymaxOS/50-engineering-standards/00-engineering-standards-handbook.md:351` | `开源品牌清零 | grep -riE "主流 Linux 发行版" docs/AirymaxOS/ | 0 结果（排除审查报告）` | ✅ 合法技术内容（合规检查脚本的注释，描述 grep 命令的排除规则） |

**结论**：3 处匹配中 2 处属于 §2.3 已识别的内部审查报告越界问题，1 处为合法技术内容。

---

## 3. URL 格式验证

### 3.1 `git@atomgit.com` SSH 格式验证

| 关键词 | 匹配文件数 | 匹配行数 | 评估 |
|--------|----------|---------|------|
| `git@atomgit.com` | 0 | 0 | ✅ 清理彻底 |
| `git@` | 0 | 0 | ✅ 清理彻底 |

### 3.2 `atomgit.com` 全量匹配验证

对 `atomgit.com` 执行 Grep，共 49 处匹配，**全部为 https:// 格式**：

| 文件路径:行号 | URL 格式 | 用途 |
|--------------|---------|------|
| `docs/AirymaxRT/140-application-development/01-getting-started.md:38` | `https://atomgit.com/openairymax/agentrt.git` | git clone 主仓库 |
| `docs/AirymaxRT/140-application-development/01-getting-started.md:243-246` | `https://atomgit.com/openairymax/docs/blob/main/*.md` | 文档链接 |
| `docs/AirymaxRT/140-application-development/02-build-guide.md:389-401` | `https://atomgit.com/openairymax/{agentrt,docs,docker,desktop}` + `https://atomgit.com/spharx/{workshop,deepness,benchmark}` | 仓库清单 |
| `docs/AirymaxOS/30-interfaces/03-sdk-api.md:18-21` | `https://atomgit.com/openairymax/agentrt-{py,rs,go,ts}.git` | 4 语言 SDK 仓库 |
| `docs/AirymaxOS/README.md:131-139` | `https://atomgit.com/openairymax/{kernel,services,security,memory,cognition,cloudnative,system,tests-linux}` | 8 子仓清单 |
| `docs/AirymaxOS/50-engineering-standards/07-maintainers-and-governance.md:170-254` | `git https://atomgit.com/openairymax/*.git`（MAINTAINERS 文件 T: 字段） | 8 子仓 MAINTAINERS |
| `docs/AirymaxOS/20-modules/README.md:19-26` | `https://atomgit.com/openairymax/*.git` | 8 子仓模块表 |
| `docs/NOTICE:4` | `https://atomgit.com/openairymax/airymaxhub` | NOTICE 文件仓库声明 |
| `docs/AirymaxRT/30-interfaces/05-runtime-interfaces/README.md:29, 31` | `https://atomgit.com/openairymax/{docs,are-standards}.git` | 文档仓与未来标准仓 |
| `docs/AirymaxOS/50-engineering-standards/50-project-erp/README.md:199, 335` | `git + atomgit.com`（描述性文字） | 工具链描述 |
| `docs/OpenStandards/_research_v1.0/01-open-standards-rebuild-proposal.md:490-491` | `https://atomgit.com/openeuler/community/...` | openEuler 社区参考链接 |

### 3.3 结论

**URL 格式验证 100% 通过**：
- `git@atomgit.com` SSH 格式零残留（v1.0 阶段清理彻底）；
- `git@` 通用 SSH 格式零残留；
- 49 处 atomgit.com 匹配全部为 https:// 格式；
- 无任何非 http/https 格式的 URL 残留。

---

## 4. 开源/闭源边界确认

### 4.1 `docs/` 开源性质确认

| 检查项 | 结果 | 评估 |
|--------|------|------|
| 文件内容是否包含"SPHARX Ltd 内部参考" | 0 匹配 | ✅ 无闭源标记 |
| 文件内容是否包含"闭源不公开" | 0 匹配 | ✅ 无闭源标记 |
| 文件内容是否包含"保密级别" | 0 匹配 | ✅ 无闭源标记 |
| SPHARX Ltd. 出现是否合理 | 100+ 处匹配，全部为版权声明（`Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.`）或许可证归属人声明 | ✅ 合法（开源项目版权人声明） |
| 文件内容是否包含 BAN-INTERNAL-002 等内部规则编号 | 0 匹配（仅闭源 `docs-closed/` 中存在） | ✅ 无内部规则泄露 |

### 4.2 `docs-closed/` 闭源性质确认

| 检查项 | 结果 | 评估 |
|--------|------|------|
| `docs-closed/agentrt/agentrt工程标准规范手册.md` 头部 | `保密级别: SPHARX Ltd 内部参考，闭源不公开` | ✅ 闭源标记正确 |
| `docs-closed/agentrt-linux/agentrt-linux基本工程标准规范.md` 头部 | `保密级别: SPHARX Ltd 内部参考，闭源不公开` | ✅ 闭源标记正确 |
| 闭源文档是否包含内部决策记录 | 是（如 Wave 2 v2 Phase A-F 审查结论、P0-CRITICAL 修复状态等） | ✅ 符合闭源定位 |

### 4.3 边界违规问题

#### 4.3.1 3 个内部审查报告目录误入开源工作树（严重）

详见 §2.3。`docs/OpenStandards/_research_v1.0/`、`_research_v2.0/`、`_research_v2.1/` 3 个目录物理路径在开源 `docs/` 工作树中，虽然当前 `git status` 显示为未跟踪，但：

1. 文档内容明确标注"内部研究文档"和"待标准委员会评审"；
2. 包含内部评分表、审查方法、决策建议等内部审查报告性质内容；
3. 存在被误 `git add` 提交到开源仓库的风险。

#### 4.3.2 4 处开源文档跨引用闭源 `DocsClosed/`（严重）

Grep 搜索 `DocsClosed/` 在 `docs/` 下的匹配，发现 **4 处开源文档跨引用闭源文件**：

| 文件路径:行号 | 引用内容 | 问题 |
|--------------|---------|------|
| `docs/AirymaxRT/30-interfaces/06-ipc/README.md:61` | `详见 [0.1.1详细任务清单.md](../../../DocsClosed/0.1.1详细任务清单.md) P0.22（IPC Bus 规范化，16h）` | ❌ 开源文档引用闭源任务清单 |
| `docs/AirymaxRT/30-interfaces/07-rpc-api/README.md:82` | `详见 [0.1.1详细任务清单.md](../../../DocsClosed/0.1.1详细任务清单.md) P0.24（JSON-RPC 命名空间规范，16h）` | ❌ 开源文档引用闭源任务清单 |
| `docs/AirymaxRT/30-interfaces/08-service-discovery/README.md:68` | `详见 [0.1.1详细任务清单.md](../../../DocsClosed/0.1.1详细任务清单.md) P0.23（服务发现标准协议适配器，20h）` | ❌ 开源文档引用闭源任务清单 |
| `docs/AirymaxRT/140-application-development/01-sdk/README.md:72` | `详见 [0.1.1详细任务清单.md](../../../DocsClosed/0.1.1详细任务清单.md) P0.21（SDK 标准化，32h）` | ❌ 开源文档引用闭源任务清单 |

**问题严重性**：
1. 4 处引用均指向 `../../../DocsClosed/0.1.1详细任务清单.md`，即从 `docs/AirymaxRT/30-interfaces/06-ipc/` 等目录出发，相对路径解析为 `docs-closed/0.1.1详细任务清单.md`（实际闭源仓库路径为 `docs-closed/`，相对路径还差一层）—— **路径本身也是断裂的**。
2. 开源文档不应包含对闭源任务清单的引用，这违反了"开源文档仅包含可公开设计文档"的边界原则。
3. 任务编号（P0.21/22/23/24）和工时（16h/20h/32h）属于内部项目规划信息，不应暴露给开源用户。

**建议**：删除这 4 处跨边界引用，或替换为开源文档内部的"详见 IPC Bus 规范化设计"等无内部任务编号的描述。

### 4.4 开源 `docs/` 内部参考文献的合法性

`docs/AirymaxOS/10-architecture/03-microkernel-strategy.md:696` 包含 `### 12.3 agentrt-linux 内部参考文献` 章节，列出：

- `50-engineering-standards/README.md`（存在）
- `include/airymax/{sched,ipc,bpf_struct_ops,memory_types,security_types,cognition_types}.h`（[SC] 共享契约层头文件清单）
- `50-engineering-standards/08-compliance-checklist.md`（**不存在，详见 §5.3**）

**判定**：章节标题"内部参考文献"属于命名不当（应改为"参考文献"或"内部交叉引用"），但内容本身是开源工程标准的合法引用；唯一问题是 `08-compliance-checklist.md` 断裂引用（详见 §5.3）。

---

## 5. 断裂引用修复验证

### 5.1 v1.0 标记的断裂引用修复状态

v1.0 报告标记的 1 处断裂引用：

> `docs/OpenStandards/README.md` 引用 `docs/AirymaxOS/TERMINOLOGY.md`（不存在）

**v2.1 实测**（`docs/OpenStandards/README.md:231`）：

```
- agentrt-linux（AirymaxOS）统一术语表：`docs/AirymaxOS/TERMINOLOGY.md`
```

**实测 `docs/AirymaxOS/TERMINOLOGY.md` 存在性**：

```
$ ls -la /home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/TERMINOLOGY.md
ls: cannot access '.../docs/AirymaxOS/TERMINOLOGY.md': No such file or directory
```

**结论**：**v1.0 标记的断裂引用在 v2.1 中仍未修复**。该文件已于 2026-07-12 从 `docs/AirymaxOS/TERMINOLOGY.md` 移至 `docs/AirymaxOS/50-engineering-standards/90-terminology.md`（见 `docs/AirymaxOS/50-engineering-standards/README.md:456` 的迁移说明），但 `docs/OpenStandards/README.md:231` 的引用未同步更新。

**正确修复路径**：`docs/AirymaxOS/TERMINOLOGY.md` → `docs/AirymaxOS/50-engineering-standards/90-terminology.md`（而非 v1.0 任务描述中建议的 `docs/AirymaxRT/TERMINOLOGY.md`，因为引用上下文明确为"agentrt-linux（AirymaxOS）统一术语表"，应指向 OS 侧而非 RT 侧）。

### 5.2 新发现：`docs/AirymaxOS/TERMINOLOGY.md` 断裂引用扩散至 3 处

Grep 搜索 `AirymaxOS/TERMINOLOGY.md` 在 `docs/` 下的匹配，发现 **3 处断裂引用**：

| 文件路径:行号 | 引用内容 | 状态 |
|--------------|---------|------|
| `docs/OpenStandards/README.md:231` | `docs/AirymaxOS/TERMINOLOGY.md` | ❌ 断裂（v1.0 已标记，未修复） |
| `docs/OpenStandards/_research_v1.0/01-open-standards-rebuild-proposal.md:1132` | `docs/AirymaxOS/TERMINOLOGY.md`（表格条目） | ❌ 断裂（同属 §2.3 越界内部研究文档） |
| `docs/AirymaxRT/10-architecture/00-architectural-principles.md:1528` | `[统一术语表](../../AirymaxOS/TERMINOLOGY.md)` | ❌ 断裂（相对路径解析为 `docs/AirymaxOS/TERMINOLOGY.md`） |

### 5.3 新发现：`08-compliance-checklist.md` 断裂引用 8+ 处

`docs/AirymaxOS/50-engineering-standards/08-compliance-checklist.md` 已于 2026-07-13 物理删除并合并入 `05-development-process.md` Part III（见 `docs/AirymaxOS/50-engineering-standards/05-development-process.md:12` 合并说明），但 **8+ 处引用未更新**：

| 文件路径:行号 | 引用内容 | 状态 |
|--------------|---------|------|
| `docs/AirymaxRT/README.md:62` | `[**合规检查**](50-engineering-standards/08-compliance-checklist.md)` | ❌ 断裂 |
| `docs/AirymaxRT/README_zh.md:87` | `[**合规检查**](50-engineering-standards/08-compliance-checklist.md)` | ❌ 断裂 |
| `docs/AirymaxOS/150-cloudnative/04-supernode-os.md:830` | `[50-engineering-standards/08-compliance-checklist.md](../50-engineering-standards/08-compliance-checklist.md)` | ❌ 断裂 |
| `docs/AirymaxOS/160-compatibility/05-cross-distro.md:723` | `50-engineering-standards/08-compliance-checklist.md`（合规检查清单） | ❌ 断裂 |
| `docs/AirymaxOS/160-compatibility/04-ipc-versioning.md:877` | `50-engineering-standards/08-compliance-checklist.md`（合规检查清单） | ❌ 断裂 |
| `docs/AirymaxOS/10-architecture/03-microkernel-strategy.md:700` | `50-engineering-standards/08-compliance-checklist.md` | ❌ 断裂 |
| `docs/AirymaxOS/20-modules/02-services.md:534` | `[合规检查清单](../50-engineering-standards/08-compliance-checklist.md)` | ❌ 断裂 |
| `docs/AirymaxOS/190-distribution/05-reproducible-build.md:1589` | `50-engineering-standards/08-compliance-checklist.md`（合规检查清单） | ❌ 断裂 |

**正确修复路径**：`08-compliance-checklist.md` → `05-development-process.md` Part III（`# Part III: 规范符合性检查（原 08-compliance-checklist.md）`，见 `05-development-process.md:1422`）。

### 5.4 新发现：`00-basic-theories/` 目录断裂引用 25 处

Grep 搜索 `00-basic-theories/` 在 `docs/` 下的匹配，发现 **25 处断裂引用，跨 9 个文件**：

| 文件路径 | 匹配数 | 实际应指向 |
|---------|-------|----------|
| `docs/AirymaxRT/TERMINOLOGY.md` | 4（行 604-607） | `docs/AirymaxRT/00-requirements/01-mcis-cn.md` 等（实际文件存在于 `00-requirements/`） |
| `docs/AirymaxRT/10-architecture/00-architectural-principles.md` | 4（行 1519-1522） | 同上 |
| `docs/AirymaxRT/20-modules/10-contracts/01-agent-contract.md` | 4 | 同上 |
| `docs/AirymaxRT/20-modules/10-contracts/02-skill-contract.md` | 4 | 同上 |
| `docs/AirymaxRT/20-modules/10-contracts/03-protocol-contract.md` | 1 | 同上 |
| `docs/AirymaxRT/20-modules/10-contracts/04-syscall-api-contract.md` | 1 | 同上 |
| `docs/AirymaxRT/20-modules/10-contracts/05-logging-format.md` | 1 | 同上 |
| `docs/AirymaxOS/50-engineering-standards/30-runtime-interfaces/README.md` | 2（行 505-506） | 同上 |
| `docs/AirymaxOS/50-engineering-standards/90-terminology.md` | 4（行 847-850） | 同上 |

**实测 `docs/AirymaxRT/00-basic-theories/` 存在性**：

```
$ ls -d /home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxRT/00-basic-theories/
ls: cannot access '.../AirymaxRT/00-basic-theories/': No such file or directory
```

**实测正确路径**：`docs/AirymaxRT/00-requirements/` 目录下存在 `01-mcis-cn.md`、`02-cognition-design-cn.md`、`03-memory-design-cn.md`、`04-design-principles-cn.md` 等被引用的文件。

**结论**：25 处引用全部断裂，正确路径应为 `00-requirements/` 而非 `00-basic-theories/`。此问题在 v2.0 报告 §4.1 中已被标记（"开源 AirymaxRT 引用 `00-basic-theories/`（应为 `00-requirements/`）"），但 v2.1 实测**仍未修复**。

### 5.5 新发现：`30-coding-standard/` 目录断裂引用 23 处

Grep 搜索 `30-coding-standard/` 在 `docs/` 下的匹配，发现 **23 处断裂引用，跨 9 个文件**：

| 文件路径 | 匹配数 | 实际应指向 |
|---------|-------|----------|
| `docs/AirymaxOS/50-engineering-standards/10-coding-style/README.md` | 1 | `docs/AirymaxOS/50-engineering-standards/10-coding-style/`（目录存在但文件命名不同） |
| `docs/AirymaxRT/50-specifications/10-contracts/06-glossary-index.md` | 6 | `docs/AirymaxRT/50-engineering-standards/10-coding-style/` |
| `docs/AirymaxRT/20-modules/10-contracts/04-syscall-api-contract.md` | 2 | 同上 |
| `docs/AirymaxRT/20-modules/10-contracts/06-glossary-index.md` | 6 | 同上 |
| `docs/AirymaxRT/20-modules/10-contracts/02-skill-contract.md` | 2 | 同上 |
| `docs/AirymaxRT/20-modules/10-contracts/05-logging-format.md` | 1 | 同上 |
| `docs/AirymaxRT/140-application-development/05-config-change-process.md` | 1 | 同上 |
| `docs/AirymaxRT/20-modules/10-contracts/01-agent-contract.md` | 2 | 同上 |
| `docs/AirymaxRT/20-modules/10-contracts/03-protocol-contract.md` | 2 | 同上 |

**实测 `docs/AirymaxRT/30-coding-standard/` 存在性**：

```
$ ls -d /home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxRT/30-coding-standard/
ls: cannot access '.../AirymaxRT/30-coding-standard/': No such file or directory
```

**问题复杂性**：不仅目录路径错误（应为 `50-engineering-standards/10-coding-style/`），且引用的文件名（如 `01-c-coding-style.md`、`02-c-cpp-secure-coding.md`、`06-go-coding-style.md`、`10-log-standard.md`、`13-rust-coding-style.md`、`14-rust-secure-coding.md`、`15-security-design.md`）与实际文件名（`C_Cpp_coding_style.md`、`Go_coding_style.md`、`Rust_coding_style.md`、`coding_conventions.md`、`scripting_coding_style.md`）**完全不匹配**。这表明这批引用可能指向一个**已废弃的目录结构**，需要重新映射到当前的 `10-coding-style/` 目录。

### 5.6 新发现：`PROTOCOL_GUIDE.md` 断裂引用 4 处

Grep 搜索 `PROTOCOL_GUIDE.md` 在 `docs/` 下的匹配，发现 **4 处断裂引用，集中在 1 个文件**：

| 文件路径:行号 | 引用内容 | 状态 |
|--------------|---------|------|
| `docs/AirymaxRT/30-interfaces/70-toolkit/02-protocol-quickstart.md:298` | `[PROTOCOL_GUIDE.md](./PROTOCOL_GUIDE.md)` | ❌ 断裂 |
| `docs/AirymaxRT/30-interfaces/70-toolkit/02-protocol-quickstart.md:323` | `[PROTOCOL_GUIDE.md](./PROTOCOL_GUIDE.md)` | ❌ 断裂 |

**实测正确文件**：`docs/AirymaxRT/30-interfaces/70-toolkit/01-protocol-guide.md`（同目录下存在）。

**正确修复路径**：`./PROTOCOL_GUIDE.md` → `./01-protocol-guide.md`。

### 5.7 断裂引用汇总

| 断裂引用类型 | 断裂处数 | 涉及文件数 | v1.0 是否标记 | v2.1 修复状态 |
|------------|---------|----------|-------------|-------------|
| `docs/AirymaxOS/TERMINOLOGY.md`（已迁移） | 3 | 3 | ✅ 标记 1 处 | ❌ 未修复，扩散至 3 处 |
| `08-compliance-checklist.md`（已合并） | 8+ | 8 | ❌ 未标记 | ❌ 新增 |
| `00-basic-theories/`（目录不存在） | 25 | 9 | ❌ 未标记（v2.0 标记） | ❌ 未修复 |
| `30-coding-standard/`（目录不存在） | 23 | 9 | ❌ 未标记 | ❌ 新增 |
| `PROTOCOL_GUIDE.md`（文件名错误） | 4 | 1 | ❌ 未标记 | ❌ 新增 |
| `../../../DocsClosed/0.1.1详细任务清单.md`（跨边界） | 4 | 4 | ❌ 未标记 | ❌ 新增 |
| **合计** | **67+** | **34** | — | **全部未修复** |

### 5.8 抽样检查 20 个文件的内部引用解析性

按 v2.1 任务要求，抽样检查 20 个文件的内部引用解析性，结果如下（节选关键样本）：

| # | 文件路径 | 抽样引用 | 解析状态 |
|---|---------|---------|---------|
| 1 | `docs/OpenStandards/README.md` | `docs/AirymaxOS/TERMINOLOGY.md`（行 231） | ❌ 断裂 |
| 2 | `docs/OpenStandards/01-airy-agent-runtime-standard.md` | `./README.md`、`./02-airy-ipc-protocol-standard.md` | ✅ 解析 |
| 3 | `docs/OpenStandards/03-airy-security-model-standard.md` | `./README.md`、`./01-airy-agent-runtime-standard.md`、`./02-airy-ipc-protocol-standard.md` | ✅ 解析 |
| 4 | `docs/OpenStandards/05-airy-cognition-loop-standard.md` | `./README.md`、`./04-airy-memory-rovol-standard.md`、`./06-airy-scheduling-standard.md` | ✅ 解析 |
| 5 | `docs/AirymaxOS/README.md` | `https://atomgit.com/openairymax/kernel` 等 8 子仓 | ✅ 解析（外部 URL） |
| 6 | `docs/AirymaxOS/10-architecture/03-microkernel-strategy.md` | `50-engineering-standards/08-compliance-checklist.md`（行 700） | ❌ 断裂 |
| 7 | `docs/AirymaxOS/20-modules/02-services.md` | `../50-engineering-standards/08-compliance-checklist.md`（行 534） | ❌ 断裂 |
| 8 | `docs/AirymaxOS/50-engineering-standards/README.md` | `90-terminology.md`、`09-ssot-registry.md`、`05-development-process.md` | ✅ 解析 |
| 9 | `docs/AirymaxOS/120-development-process/01-patch-lifecycle.md` | `50-engineering-standards/05-development-process.md`、`07-maintainers-and-governance.md` | ✅ 解析 |
| 10 | `docs/AirymaxOS/160-compatibility/03-upstream-tracking.md` | `https://git.kernel.org/...` | ✅ 解析（外部 URL） |
| 11 | `docs/AirymaxRT/README.md` | `50-engineering-standards/08-compliance-checklist.md`（行 62） | ❌ 断裂 |
| 12 | `docs/AirymaxRT/TERMINOLOGY.md` | `00-basic-theories/01-mcis-cn.md` 等 4 处（行 604-607） | ❌ 断裂 |
| 13 | `docs/AirymaxRT/10-architecture/00-architectural-principles.md` | `00-basic-theories/01-mcis-cn.md` 等 4 处（行 1519-1522） | ❌ 断裂 |
| 14 | `docs/AirymaxRT/10-architecture/00-architectural-principles.md` | `../../AirymaxOS/TERMINOLOGY.md`（行 1528） | ❌ 断裂 |
| 15 | `docs/AirymaxRT/20-modules/10-contracts/01-agent-contract.md` | `../30-coding-standard/02-c-cpp-secure-coding.md` 等 2 处 | ❌ 断裂 |
| 16 | `docs/AirymaxRT/20-modules/10-contracts/02-skill-contract.md` | `../../00-basic-theories/04-design-principles-cn.md` 等 4 处 | ❌ 断裂 |
| 17 | `docs/AirymaxRT/30-interfaces/06-ipc/README.md` | `../../../DocsClosed/0.1.1详细任务清单.md`（行 61） | ❌ 断裂 + 跨边界 |
| 18 | `docs/AirymaxRT/30-interfaces/70-toolkit/02-protocol-quickstart.md` | `./PROTOCOL_GUIDE.md`（行 298、323） | ❌ 断裂 |
| 19 | `docs/AirymaxRT/30-interfaces/70-toolkit/10-go/README.md` | `../../../../140-application-development/24-create-agent.md` | ✅ 解析 |
| 20 | `docs/AirymaxRT/140-application-development/01-sdk/README.md` | `../../../DocsClosed/0.1.1详细任务清单.md`（行 72） | ❌ 断裂 + 跨边界 |

**抽样结论**：20 个文件中 **9 个存在断裂引用**（45% 断裂率），其中 2 个还涉及跨边界违规。开源 `docs/` 的内部引用体系**系统性失效**。

---

## 6. 反抄袭检查

### 6.1 seL4 引用规范性

Grep 搜索 `seL4` 在 `docs/` 下的匹配，30+ 处，全部规范引用：

| 引用类型 | 示例 | 评估 |
|---------|------|------|
| URL 附源 | `seL4 capability 安全模型：https://sel4.systems/`（`docs/OpenStandards/03-airy-security-model-standard.md:615`） | ✅ 规范 |
| URL 附源 | `seL4 Licensing: https://www.sel4.org/Legal/license.html`（`docs/OpenStandards/_research_v2.1/01-open-standards-review-v2.1.md:1089`） | ✅ 规范 |
| 借鉴声明 | `agentrt-linux 的微内核设计思想**唯一来源为 seL4**（参考 01Reference/seL4-master）`（`docs/AirymaxOS/README.md:163`） | ✅ 规范（明确"借鉴非移植"） |
| 借鉴声明 | `微内核思想来源：seL4（唯一来源，ADR-014）| 技术路线：基于 Linux 改造（ADR-012）`（`docs/AirymaxOS/10-architecture/03-microkernel-strategy.md:705`） | ✅ 规范 |

### 6.2 Linux 6.6 / kernel.org 引用规范性

Grep 搜索 `Linux 6.6`、`kernel.org` 在 `docs/` 下的匹配，全部规范引用：

| 引用类型 | 示例 | 评估 |
|---------|------|------|
| URL 附源 | `Linux LSM 框架：https://docs.kernel.org/admin-guide/LSM/index.html`（`docs/OpenStandards/03-airy-security-model-standard.md:617`） | ✅ 规范 |
| URL 附源 | `Linux sched_ext 文档：https://docs.kernel.org/scheduler/sched-ext.html`（`docs/OpenStandards/06-airy-scheduling-standard.md:542`） | ✅ 规范 |
| URL 附源 | `Linux io_uring：https://docs.kernel.org/filesystems/io_uring.html`（`docs/OpenStandards/07-airy-syscall-standard.md:661`） | ✅ 规范 |
| 参考来源声明 | `参考来源：基于 kernel.org 官方发布表 + kernelnewbies.org + LWN + Phoronix 多方交叉验证`（`docs/AirymaxOS/10-architecture/04-engineering-baseline.md:332`） | ✅ 规范 |
| GPL 许可证声明 | `// SPDX-License-Identifier: GPL-2.0-only WITH Linux-syscall-note`（`docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md:653`） | ✅ 规范（内核代码示例正确许可证） |

### 6.3 openEuler 引用规范性

Grep 搜索 `openEuler` 在 `docs/` 下的匹配，30+ 处，全部规范引用：

| 引用类型 | 示例 | 评估 |
|---------|------|------|
| URL 附源 | `openEuler 贡献攻略：https://www.openeuler.org/zh/community/contribution/detail.html`（`docs/OpenStandards/_research_v1.0/01-open-standards-rebuild-proposal.md:495`） | ✅ 规范 |
| URL 附源 | `openEuler 社区组织：https://www.openeuler.org/zh/community/organization/`（同上:496） | ✅ 规范 |
| 不共享代码声明 | `agentrt-linux 不移植 openEuler 特有特性，与 openEuler 的关系仅限于技术参考，不共享代码`（`docs/AirymaxOS/README.md:163`） | ✅ 规范（明确"参考非移植"） |

**注意**：v2.0 报告 §2.1.1 指出开源 `docs/AirymaxOS/` 中 openEuler 提及与闭源 `docs-closed/agentrt-linux/README.md` BAN-INTERNAL-002 规则冲突。本次实测确认 openEuler 在开源文档中的提及仍然存在（`docs/AirymaxOS/README.md:30, 163`、`docs/AirymaxOS/10-architecture/06-directory-structure.md:32, 118, 222` 等），但 BAN-INTERNAL-002 规则本身位于闭源文档，开源文档不受其约束。从反抄袭角度，openEuler 引用全部附 URL 且明确"不共享代码"，**未构成抄袭**。

### 6.4 OCI / CNCF / openEuler 治理模式引用

`docs/OpenStandards/_research_v1.0/01-open-standards-rebuild-proposal.md` 第 4 章对 OCI / CNCF / seL4 Foundation / openEuler 四大治理模式的对比，全部基于公开规范与官方文档，且第 22 行明确声明：

> 本报告对外部协议与治理模式（MCP / A2A / AG-UI / ANP / OCI / CNCF / seL4 Foundation / openEuler 等）的描述均基于公开规范与官方文档，**所有外部引用必须附 URL**，不得转述为 Airymax 自有观点。

**评估**：✅ 反抄袭合规。

### 6.5 代码片段原创性

抽样检查 `docs/` 下的代码块，全部包含正确的 SPDX-License-Identifier 头部，未发现直接复制粘贴的代码片段：

- `docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md:653` — `// SPDX-License-Identifier: GPL-2.0-only WITH Linux-syscall-note`（内核代码示例）
- `docs/AirymaxRT/30-interfaces/05-runtime-interfaces/03-l3-security-governance.md:536` — `// SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0`（用户态代码示例）
- `docs/AirymaxOS/190-distribution/01-rpm-packaging.md:152` — `License: GPL-2.0-only OR AGPL-3.0-or-later`（RPM Spec 文件）

### 6.6 反抄袭检查结论

**反抄袭合规性评分：85/B+**（v1.0: 80/B+，提升 +5）。

- seL4 / Linux / openEuler / OCI / CNCF 引用全部附 URL，符合"所有外部引用必须附 URL"的内部规则；
- "参考声明" / "唯一来源" / "不共享代码"等声明明确"借鉴非移植"；
- 代码片段全部包含正确的 SPDX-License-Identifier 头部；
- Linus Torvalds 引用为理念引用（regression 不可接受原则），非代码复制；
- 未发现直接复制粘贴的代码片段或未标注来源的内容。

---

## 7. 闭源文档准确性

### 7.1 `docs-closed/agentrt/` 工程准确性与实施指导性

#### 7.1.1 子系统规范层（07-subsystem-specs/）— 工程准确性良好

抽样 `docs-closed/agentrt/07-subsystem-specs/02-corekern.md`（CoreKern 子系统边界文档，v1.0.0，2026-06-17）：

| 维度 | 评估 |
|------|------|
| 职责边界清晰度 | ✅ 明确列出 9 大核心职责（内存/OOM/任务/线程/IPC/时间/可观测性/错误处理/初始化）+ 6 项非职责（AI/LLM、安全守卫、网络协议、工具调用、持久化、配置管理） |
| 头文件清单完整性 | ✅ 14 个头文件全部列出（`airy_rt.h`、`mem.h`、`oom_handler.h`、`task.h`、`ipc.h`、`airy_time.h`、`error.h`、`arena.h`、`tcache.h`、`refcount.h`、`observability.h`、`platform_core.h`、`stdatomic.h`、`export.h`） |
| API 签名规范性 | ✅ 全部使用 `airy_*` 前缀（`airy_core_init`、`airy_mem_alloc`、`airy_oom_init`、`airy_task_create`、`airy_ipc_channel_create`、`airy_clock_monotonic_ms` 等） |
| 错误码定义 | ✅ 8 个错误码全部 `AIRY_*` 前缀（`AIRY_OK`、`AIRY_EINVAL`、`AIRY_ENOMEM`、`AIRY_ENOTINIT`、`AIRY_EEXIST`、`AIRY_EBUSY`、`AIRY_ENOENT`、`AIRY_ERR_ALREADY_EXISTS`） |
| 依赖关系图 | ✅ 内部依赖（`airy_atoms`、`airy_common`）+ 运行时依赖（POSIX 线程、系统时钟）+ 被依赖方（CoreLoopThree、Cupolas、所有 daemon、gateway_d、llm_d、tool_d）完整列出 |

**结论**：子系统规范层工程准确性良好，已完整迁移至 `airy_*` 前缀。

#### 7.1.2 工程标准手册层（agentrt工程标准规范手册.md）— 前缀迁移停滞

`docs-closed/agentrt/agentrt工程标准规范手册.md` 中 `agentrt_*` 前缀残留统计：

| 维度 | 数量 | 评估 |
|------|------|------|
| `agentrt_[a-z]` 匹配数 | 22 处 | ❌ 前缀迁移停滞 |
| `airy_[a-z]` 匹配数 | 163 处 | ✅ 新前缀已广泛使用 |
| 比例 | 22 : 163（12% : 88%） | ⚠️ 12% 残留 |

**关键残留位置**（节选）：

| 行号 | 内容 | 问题 |
|------|------|------|
| 1415 | `代码中必须使用 get_agentrt_home() 获取配置目录` | ❌ 应为 `get_airy_home()` |
| 1518 | CMake target 表格 `agentrt_common、agentrt_atoms、agentrt_daemon 等` 列为"已废弃" | ✅ 表格中标注为废弃（但表格仍保留旧前缀） |
| 1521 | `agentrt_error_t、agentrt_syscalls_init() 等` 列为"已废弃" | ✅ 同上 |
| 1524 | `agentos/daemon/、agentrt_daemon、daemon.git` 列为"已废弃" | ✅ 同上 |
| 1578 | `find . -name CMakeLists.txt -exec sed -i 's/agentrt_daemon\b/agentrt_daemons/g' {} +` | ❌ 迁移脚本本身使用旧前缀（应为 `airy_daemons`） |
| 3176-3226 | 适配器接口层示例代码 `agentrt_daemons_adapter.h`、`agentrt_atoms_standalone` 等 | ❌ 示例代码使用旧前缀 |
| 3198-3201 | `agentrt_checkpoint_ops_t`、`agentrt_hook_ops_t`、`agentrt_orch_ops_t`、`agentrt_loop_set_checkpoint_ops` | ❌ 接口定义使用旧前缀 |

**矛盾点**：手册 §1518-1524 的表格明确标注 `agentrt_*` 为"已废弃"，但手册自身的代码示例（§1578、§3176-3226）仍在使用 `agentrt_*` 前缀，**手册内容自相矛盾**。

#### 7.1.3 `docs-closed/agentrt/` 全量前缀统计

| 目录 | `agentrt_[a-z]` 匹配数 | `airy_[a-z]` 匹配数 | 评估 |
|------|----------------------|---------------------|------|
| `docs-closed/agentrt/`（全量） | 218 处 / 12 文件 | — | ❌ 前缀迁移未完成 |
| `docs-closed/agentrt/agentrt工程标准规范手册.md` | 22 处 | 163 处 | ⚠️ 12% 残留 |
| `docs-closed/agentrt/07-subsystem-specs/02-corekern.md` | 0 处 | 50 处 | ✅ 完全迁移 |
| `docs-closed/agentrt/_design_0.1.1/01-repo-split-proposal.md` | 24 处 | — | ❌ 设计文档未迁移 |
| `docs-closed/agentrt/_design_0.1.1/04-release-full-remediation-plan.md` | 19 处 | — | ❌ 设计文档未迁移 |
| `docs-closed/agentrt/_archive_conversations/总线开发-长任务.md` | 48 处 | — | ⚠️ 历史归档（可不迁移） |
| `docs-closed/agentrt/_archive_conversations/总线开发-长任务2.md` | 48 处 | — | ⚠️ 历史归档（可不迁移） |

**结论**：子系统规范层已完全迁移，工程标准手册层 12% 残留且自相矛盾，设计文档与归档未迁移。

### 7.2 `docs-closed/agentrt-linux/` 工程准确性与实施指导性

#### 7.2.1 工程标准手册层（agentrt-linux基本工程标准规范.md）— 前缀迁移严重滞后

`docs-closed/agentrt-linux/agentrt-linux基本工程标准规范.md` 前缀统计：

| 维度 | 数量 | 评估 |
|------|------|------|
| `agentrt_[a-z]` 匹配数 | 22 处 | ❌ 前缀迁移严重滞后 |
| `airy_[a-z]` 匹配数 | **0 处** | ❌ **完全未迁移** |

**关键问题**：

1. 手册头部（行 7）声明版本为 `0.2.5（同步开源手册 v0.1.1 全部变更 + 融入 Wave 2 v2 源码级深读审查结论 + 术语清洗 OLK-6.6 → Linux 6.6 内核基线 + ES-SEL4 数量冲突消解 + 附录 D 标题修正）`，但**完全未提及 `agentrt_` → `airy_` 前缀迁移**。

2. 手册代码示例（行 131-400+）全部使用 `agentrt_*` 前缀：
   - `agentrt_sched_ready_queue()`（行 131）
   - `struct agentrt_task *task;`（行 141）
   - `enum agentrt_task_state`（行 151）
   - `int agentrt_ipc_send(u32 ch, const void *msg, size_t len);`（行 170）
   - `agentrt_get_private()`（行 187）
   - `agentrt_task_submit()`、`agentrt_task_is_pending()`（行 195-196）
   - `agentrt_alloc_and_init()`、`agentrt_buffer`（行 204-206）
   - `agentrt_sched_init()`（行 244-250）
   - `agentrt_sched_submit_task()`（行 274-284）
   - `agentrt_task_create()`（行 355）
   - `agentrt_for_each_task`（行 400）

3. 手册行 815 提到 `agentrt_ipc_msg_hdr_t`（IPC 消息头类型），但开源 `docs/AirymaxOS/50-engineering-standards/20-contracts/` 与实际源码已统一使用 `airy_ipc_msg_hdr_t`。

#### 7.2.2 `docs-closed/agentrt-linux/` 全量前缀统计

| 目录 | `agentrt_[a-z]` 匹配数 | 文件数 | 评估 |
|------|----------------------|------|------|
| `docs-closed/agentrt-linux/`（全量） | 388 处 | 34 文件 | ❌ 前缀迁移严重滞后 |
| `docs-closed/agentrt-linux/02-olk66-source-mapping/05-security-mapping.md` | 62 处 | 1 文件 | ❌ 安全映射未迁移 |
| `docs-closed/agentrt-linux/02-olk66-source-mapping/04-mm-mapping.md` | 41 处 | 1 文件 | ❌ 内存映射未迁移 |
| `docs-closed/agentrt-linux/02-olk66-source-mapping/02-io-uring-mapping.md` | 32 处 | 1 文件 | ❌ io_uring 映射未迁移 |
| `docs-closed/agentrt-linux/agentrt-linux基本工程标准规范.md` | 22 处 | 1 文件 | ❌ 工程标准手册未迁移 |
| `docs-closed/agentrt-linux/_review_0.7.0/01-syscall-minimization-and-ssot-conflict-analysis.md` | 34 处 | 1 文件 | ⚠️ 审查报告（可不迁移） |
| `docs-closed/agentrt-linux/_research_0.3.1/01-comprehensive-issue-list.md` | 17 处 | 1 文件 | ⚠️ 研究报告（可不迁移） |

#### 7.2.3 闭源文档内部审查描述残留（合法）

闭源 `docs-closed/agentrt-linux/agentrt-linux基本工程标准规范.md` 头部（行 7-16）包含：

- `Wave 2 v2 源码级深读审查结论`
- `Wave 2 v2 源码级深读审查完成（Phase A/B/C/D/E/F，2026-07-13）`
- `Wave 2 v2 源码级深读报告（_review_0.9.0/ 7 份报告）`

**判定**：✅ 合法。闭源文档包含内部审查描述符合其"内部工程实现指南"定位，无需清理。

### 7.3 闭源 v0.2.5 与开源 v0.1.1 版本同步情况

| 维度 | 开源版本 | 闭源版本 | 同步状态 |
|------|---------|---------|---------|
| `docs/AirymaxOS/50-engineering-standards/00-engineering-standards-handbook.md` | v0.1.1（行 6） | — | — |
| `docs/AirymaxOS/README.md` | v0.1.1（行 8） | — | — |
| `docs-closed/agentrt-linux/agentrt-linux基本工程标准规范.md` | — | v0.2.5（行 7，"同步开源手册 v0.1.1 全部变更"） | ⚠️ 版本号差距 4 个小版本 |
| `docs-closed/agentrt/agentrt工程标准规范手册.md` | — | v28.0（v2.0 报告标记，本次未实测） | ⚠️ 版本号差距更大 |

**问题分析**：

1. 闭源 v0.2.5 声明"同步开源手册 v0.1.1 全部变更"，但版本号本身差距 4 个小版本（0.1.1 → 0.2.5），表明闭源侧独立演进。
2. 闭源 v0.2.5 头部包含"融入 Wave 2 v2 源码级深读审查结论"、"术语清洗 OLK-6.6 → Linux 6.6 内核基线"、"ES-SEL4 数量冲突消解"、"附录 D 标题修正"等开源 v0.1.1 未包含的内部修复。
3. 闭源 v0.2.5 头部声明"1.0.1（开发）"，表明已进入 1.0.1 开发阶段，而开源 v0.1.1 仍为设计文档阶段。

**结论**：闭源 v0.2.5 与开源 v0.1.1 **版本号不同步但内容部分同步**。闭源侧通过头部声明"同步开源手册 v0.1.1 全部变更"建立单向同步关系，但闭源侧的内部修复（Wave 2 v2、ES-SEL4 消解等）未回流开源。

### 7.4 闭源文档工程准确性总评

**评分：65/C+**（v1.0: 70/B-，下降 -5）。

- 子系统规范层（`07-subsystem-specs/`）工程准确性良好，已完整迁移至 `airy_*` 前缀；
- 工程标准手册层（`agentrt工程标准规范手册.md`、`agentrt-linux基本工程标准规范.md`）前缀迁移严重滞后，22 + 22 = 44 处 `agentrt_*` 残留，且 agentrt-linux 手册**完全未迁移**（`airy_*` 0 处）；
- 工程标准手册内容自相矛盾（标注 `agentrt_*` 为"已废弃"但自身代码示例仍使用 `agentrt_*`）；
- 版本同步为单向（闭源 ← 开源），闭源侧内部修复未回流开源。

---

## 8. 上下游关系描述准确性

### 8.1 agentrt（用户态运行时）vs agentrt-linux（智能体操作系统）的关系

`docs/AirymaxOS/README.md:165-179` 明确描述 agentrt 与 agentrt-linux 的关系：

```
agentrt（AirymaxAgentRT，跨平台用户态运行时）
   │
   └── 运行在 agentrt-linux 上: 天然更稳健和适配（同源）
       │
       ├── agentrt 的 MicroCoreRT 调度 ←→ agentrt-linux 的 Agent 调度策略（语义同源）
       ├── agentrt 的 AgentsIPC 协议 ←→ agentrt-linux 的 IPC 子系统（128B 消息头同源）
       ├── agentrt 的 Cupolas 安全 ←→ agentrt-linux 的 capability + LSM（模型同源）
       ├── agentrt 的 MemoryRovol ←→ agentrt-linux 的 记忆子系统（记忆模型同源）
       └── agentrt 的 CoreLoopThree ←→ agentrt-linux 的 认知 kthread（循环模型同源）
```

**评估**：✅ 准确。5 维同源映射（调度、IPC、安全、记忆、认知）与 IRON-9 v2 三层共享模型一致，"同源红利"声明（"agentrt 在 agentrt-linux 上运行无适配层"）与微核心/微内核分工一致。

### 8.2 微核心（MicroCore）vs 微内核（Microkernel）术语区分

`docs/OpenStandards/README.md:33-39, 216-217`：

| 术语 | 定位 | 说明 |
|------|------|------|
| **agentrt** | AirymaxAgentRT 极境智能体运行底座平台工程 | 用户态 AI Agent 运行时平台工程，定位为**微核心**（micro-core） |
| **agentrt-linux** | agentrt-linux（AirymaxOS）极境智能体操作系统 | 智能体操作系统发行版，定位为**微内核**（micro-kernel） |

明确约束：
- **agentrt = 微核心**：agentrt 的 MicroCoreRT 是用户态微核心运行时，**不得**用"微内核"描述 agentrt。
- **agentrt-linux = 微内核**：agentrt-linux 基于 Linux 6.6 内核基线进行微内核化改造（sched_ext + eBPF + io_uring），将 VFS、网络栈、部分驱动移到用户态。

**评估**：✅ 准确。微核心（用户态运行时）与微内核（OS 发行版）的术语区分清晰，与 ADR-014（seL4 唯一来源）、ADR-012（基于 Linux 改造）一致。

### 8.3 AirymaxRT vs AirymaxOS 目录结构对应

| 开源目录 | 闭源对应 | 用途 |
|---------|---------|------|
| `docs/AirymaxRT/` | `docs-closed/agentrt/` | agentrt（用户态运行时）设计文档 / 内部工程实现指南 |
| `docs/AirymaxOS/` | `docs-closed/agentrt-linux/` | agentrt-linux（智能体操作系统）设计文档 / 内部工程实现指南 |
| `docs/OpenStandards/` | （无闭源对应） | Airymax 开放标准体系（公开标准） |
| `docs/Publications/` | （无闭源对应） | 学术论文与报告（公开） |

**评估**：✅ 准确。开源 `docs/AirymaxRT/` 对应闭源 `docs-closed/agentrt/`，开源 `docs/AirymaxOS/` 对应闭源 `docs-closed/agentrt-linux/`，命名映射清晰（RT = Runtime = agentrt，OS = Operating System = agentrt-linux）。

### 8.4 OpenStandards 与内部设计文档的关系

`docs/OpenStandards/README.md:46-52`：

| 维度 | 开放标准 | 工程标准 |
|------|---------|---------|
| **可见性** | 公开、可被第三方实现 | 内部实现规范 |
| **内容** | 接口契约、协议格式、兼容性要求 | 编码规范、目录结构、CI/CD 流程 |
| **目标读者** | 第三方实现者、生态伙伴 | 内部开发者、维护者 |
| **许可** | CC-BY-4.0（规范文档）+ OWFa 1.0（专利） | AGPL-3.0-or-later OR Apache-2.0 |

明确陈述：**开放标准是公开的生态接口，工程标准是内部实现规范**。一个第三方实现只要符合开放标准即可纳入 Airymax 生态；其内部如何编码、如何组织代码，由该实现自行决定。

**评估**：✅ 准确。OpenStandards 定位为"公开生态接口"，与内部工程标准（`docs/AirymaxOS/50-engineering-standards/`、`docs-closed/agentrt/`）形成清晰的"接口 vs 实现"分层。

### 8.5 50-engineering-standards 符号链接正确性

实测 `docs/` 下的符号链接：

| 符号链接路径 | 目标路径 | 实测结果 |
|------------|---------|---------|
| `docs/AirymaxRT/50-engineering-standards` | `../AirymaxOS/50-engineering-standards` | ✅ 正确（解析为 `docs/AirymaxOS/50-engineering-standards`，存在） |
| `docs/AirymaxRT/00-requirements/10-terminology.md` | `../TERMINOLOGY.md` | ✅ 正确（解析为 `docs/AirymaxRT/TERMINOLOGY.md`，存在） |

**评估**：✅ 2 个符号链接全部正确。`docs/AirymaxRT/50-engineering-standards` 指向 `docs/AirymaxOS/50-engineering-standards`，实现 IRON-9 v2 三层共享模型中的"工程标准两端共享"；`docs/AirymaxRT/00-requirements/10-terminology.md` 指向 `docs/AirymaxRT/TERMINOLOGY.md`，实现术语表单一权威来源。

### 8.6 上下游关系描述总评

**评分：78/B+**（v1.0: 65/C+，提升 +13）。

- agentrt ↔ agentrt-linux 5 维同源映射准确；
- 微核心/微内核术语区分清晰；
- 开源/闭源目录结构对应关系明确；
- OpenStandards 与内部工程标准的"接口 vs 实现"分层清晰；
- 2 个符号链接全部正确；
- 唯一扣分点：`docs/AirymaxOS/10-architecture/03-microkernel-strategy.md:696` 的"agentrt-linux 内部参考文献"章节标题命名不当（应改为"参考文献"），且其中 `08-compliance-checklist.md` 引用断裂（详见 §5.3）。

---

## 9. 模板文件和占位符检查

### 9.1 虚构邮箱地址检查

#### 9.1.1 `@spharx.ai` 虚构邮箱（v2.1 任务重点关注）

Grep 搜索 `@spharx.ai` 在 `docs/` 下的匹配：**0 处**。

**结论**：✅ 未发现 `@spharx.ai` 虚构邮箱。

#### 9.1.2 实际使用的邮箱域名统计

Grep 搜索 `@spharx\.` 在 `docs/` 下的匹配，共 14 处，涉及 4 个域名：

| 域名 | 匹配数 | 用途 | 评估 |
|------|-------|------|------|
| `@spharx.cn` | 8 处 | `cupolas-team@spharx.cn`、`support@spharx.cn`、`team@spharx.cn`、`alerts@spharx.cn`、`ops-team@spharx.cn`、`oncall@spharx.cn`、`your-team@spharx.cn` | ⚠️ 主域名，但部分为占位（`your-team@spharx.cn`） |
| `@spharx.com` | 3 处 | `dev@spharx.com`（Dockerfile maintainer + RPM changelog）、`SPHARX <dev@spharx.com>` | ⚠️ 第二域名 |
| `@spharx.io` | 2 处 | `security@spharx.io`（安全漏洞报告） | ⚠️ 第三域名 |
| `@spharx.dev` | 1 处 | `airymax-kernel-maintainers@spharx.dev`（内核维护者邮件列表） | ⚠️ 第四域名 |

**问题**：
1. **4 个邮箱域名未统一**：`spharx.cn`、`spharx.com`、`spharx.io`、`spharx.dev` 同时使用，缺乏统一的域名策略。
2. **`your-team@spharx.cn` 占位邮箱**（`docs/AirymaxRT/140-application-development/20-manager-development.md:284`）：示例配置中使用 `your-team` 作为占位符，应替换为具体团队邮箱或明确的占位符标记（如 `<your-team>@spharx.cn`）。
3. **`user@example.com` 标准占位**（4 处）：属于 RFC 2606 标准占位域名，合法。

**建议**：统一邮箱域名为单一域名（建议 `@spharx.com` 作为主域名），并将 `your-team@spharx.cn` 替换为 `<team-name>@spharx.com` 明确占位。

### 9.2 TBD/TODO 占位符检查

#### 9.2.1 TBD 占位符

Grep 搜索 `\bTBD\b` 在 `docs/` 下的匹配，4 处：

| 文件路径:行号 | 上下文 | 评估 |
|--------------|--------|------|
| `docs/AirymaxOS/50-engineering-standards/10-coding-style/Rust_coding_style.md:581` | `| 1.0.1 | TBD | 首个开发版本：与代码实现同步验证 |` | ✅ 合理（1.0.1 未启动，日期待定） |
| `docs/AirymaxOS/50-engineering-standards/10-coding-style/Rust_coding_style.md:1089` | `| 1.0.1 | TBD | 首个开发版本：与代码实现同步验证，形式化验证覆盖全部安全关键模块 |` | ✅ 合理 |
| `docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md:796` | `| 1.0.1 | TBD | 首个开发版本：与代码实现同步验证 |` | ✅ 合理 |
| `docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md:3439` | `| 1.0.1 | TBD | 首个开发版本：与代码实现同步验证，CVE 案例扩展至 10+ |` | ✅ 合理 |

**结论**：✅ 4 处 TBD 全部用于 1.0.1 版本日期占位，合理且明确标注。

#### 9.2.2 TODO/FIXME 占位符

Grep 搜索 `\bTODO\b|\bFIXME\b` 在 `docs/` 下的匹配，20+ 处，全部为代码示例中的合法用法：

| 类型 | 文件路径 | 用途 | 评估 |
|------|---------|------|------|
| 代码示例 | `docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md:2384-2391` | `// TODO(author): 添加缓存淘汰策略 [P1] [#1234]` 等 | ✅ 合法（编码规范中的 TODO/FIXME 格式示例） |
| 代码示例 | `docs/AirymaxOS/50-engineering-standards/10-coding-style/coding_conventions.md:798-819` | `// TODO(zhangsan): 添加任务取消功能 #1234 [优先级: P1]` 等 | ✅ 合法 |
| 流程描述 | `docs/AirymaxRT/140-application-development/15-testing-standards.md:465` | `无跳过测试（除非有明确原因和 TODO）` | ✅ 合法（测试清单检查项） |

**结论**：✅ TODO/FIXME 全部为代码示例或流程检查项，无未完成的占位符。

### 9.3 XXX 占位符检查

Grep 搜索 `\bXXX\b` 在 `docs/` 下的匹配，15 处：

| 类型 | 匹配数 | 评估 |
|------|-------|------|
| 规则编号模板（`OS-STD-XXX`、`OS-DEV-XXX`、`OS-KER-XXX`、`OS-DRV-XXX`、`OS-ACC-XXX`、`OS-TEST-XXX`、`NFR-XXX`、`CWE-XXX`） | 12 处 | ✅ 合法（规则编号占位模板） |
| Doxygen 错误消息模板（`documented symbol XXX was not declared or defined` 等） | 3 处 | ✅ 合法（Doxygen 警告消息示例） |
| Go 代码示例占位（`XXX 管理模块`、`XXX 资源`） | 2 处 | ⚠️ 次要问题（应替换为具体示例） |

**问题位置**：

| 文件路径:行号 | 内容 | 建议 |
|--------------|------|------|
| `docs/AirymaxOS/50-engineering-standards/10-coding-style/Go_coding_style.md:1521` | `// Airymax Go SDK - XXX 管理模块` | 替换为具体模块名（如 `Agent 管理模块`） |
| `docs/AirymaxOS/50-engineering-standards/10-coding-style/Go_coding_style.md:1525` | `// 提供 XXX 资源的创建、查询、更新、删除等生命周期管理功能` | 替换为具体资源名（如 `Agent 资源`） |

### 9.4 提前创建的不属于当前阶段的文件

实测 `docs/AirymaxOS/` 下的阶段目录：

| 目录 | 文件数 | 阶段 | 评估 |
|------|-------|------|------|
| `150-cloudnative/` | 6 .md | 1.0.1+（云原生） | ✅ 合理（0.1.1 阶段已包含设计草案） |
| `180-i18n/` | 6 .md | 1.0.1+（国际化） | ✅ 合理 |
| `190-distribution/` | 6 .md | 1.0.1+（发行版） | ✅ 合理 |

**评估**：✅ 未发现提前创建的不属于当前阶段的文件。0.1.1 阶段为"设计文档体系"，150-cloudnative、180-i18n、190-distribution 目录下的文件均为设计草案，符合 0.1.1 范围。

### 9.5 模板与占位符检查总评

**评分：80/B**（v1.0 未覆盖，新增）。

- 未发现 `@spharx.ai` 虚构邮箱；
- TBD 4 处全部用于 1.0.1 版本日期占位，合理；
- TODO/FIXME 全部为代码示例，合法；
- XXX 占位符 15 处中 13 处合法、2 处为次要问题（Go 代码示例）；
- 未发现提前创建的不属于当前阶段的文件；
- 主要扣分点：4 个邮箱域名未统一、`your-team@spharx.cn` 占位邮箱未明确标记。

---

## 10. 综合评分与改进建议

### 10.1 综合评分

| 评分维度 | v1.0 评分 | v2.1 评分 | 趋势 | 权重 | 加权分 |
|---------|---------|---------|------|------|-------|
| 内部审查描述清理 | 60/D | 78/B+ | ↑ +18 | 15% | 11.7 |
| URL 格式一致性 | 75/B | 100/A+ | ↑ +25 | 10% | 10.0 |
| 开源/闭源边界 | 65/C+ | 55/C | ↓ -10 | 15% | 8.25 |
| 断裂引用修复 | 35/D- | 30/D- | ↓ -5 | 20% | 6.0 |
| 反抄袭合规 | 80/B+ | 85/B+ | ↑ +5 | 10% | 8.5 |
| 闭源文档准确性 | 70/B- | 65/C+ | ↓ -5 | 10% | 6.5 |
| 上下游关系描述 | 65/C+ | 78/B+ | ↑ +13 | 10% | 7.8 |
| 模板与占位符 | — | 80/B | 新增 | 10% | 8.0 |
| **总评** | **58/D+** | **68/C+** | **↑ +10** | 100% | **66.85** |

**总评**：**68/C+**（v1.0: 58/D+，提升 +10）。

### 10.2 v2.1 vs v1.0 改善项

| 改善项 | v1.0 状态 | v2.1 状态 | 改善幅度 |
|--------|----------|----------|---------|
| 内部审查描述清理（13 关键词） | 30 文件 50 处编辑 | 12/13 关键词零残留 | 显著 |
| URL 格式（git@ SSH 残留） | 部分残留 | 零残留 | 完全 |
| 反抄袭合规 | 80/B+ | 85/B+ | +5 |
| 上下游关系描述 | 65/C+ | 78/B+ | +13 |
| 微核心/微内核术语区分 | 部分模糊 | 清晰 | 显著 |
| 符号链接正确性 | 未验证 | 2/2 正确 | 新增验证 |

### 10.3 v2.1 vs v1.0 恶化项

| 恶化项 | v1.0 状态 | v2.1 状态 | 恶化幅度 |
|--------|----------|----------|---------|
| 断裂引用数量 | 5 仓库全部存在（约 10 处） | 67+ 处跨 34 文件 | **6.7 倍** |
| 开源/闭源边界违规 | 边界基本清晰 | 3 个内部审查目录越界 + 4 处跨边界引用 | 新增违规 |
| 闭源前缀迁移 | agentos_* 背离 | agentrt_* 606 处残留（agentrt 218 + agentrt-linux 388） | 停滞 |
| 闭源版本同步 | v0.2.5 vs v0.1.1 | 同 | 持平（未改善） |

### 10.4 P0 级阻断问题（必须修复后方可进入 1.0.1 M1）

#### P0-1：断裂引用系统性扩散（67+ 处跨 34 文件）

**问题描述**：v1.0 标记的 1 处断裂引用（`docs/AirymaxOS/TERMINOLOGY.md`）未修复，且因 2026-07-12/13 的两次文件迁移未同步更新引用方，扩散至 67+ 处跨 34 文件。

**影响**：开源 `docs/` 的内部引用体系系统性失效，第三方实现者无法通过引用路径找到目标文档，严重影响开源文档的可用性。

**修复方案**：

| 断裂类型 | 处数 | 修复路径 |
|---------|-----|---------|
| `docs/AirymaxOS/TERMINOLOGY.md` | 3 | → `docs/AirymaxOS/50-engineering-standards/90-terminology.md` |
| `08-compliance-checklist.md` | 8+ | → `05-development-process.md` Part III（使用锚点 `#part-iii-规范符合性检查原-08-compliance-checklistmd`） |
| `00-basic-theories/` | 25 | → `00-requirements/`（路径替换） |
| `30-coding-standard/` | 23 | → `50-engineering-standards/10-coding-style/`（路径替换 + 文件名重映射） |
| `PROTOCOL_GUIDE.md` | 4 | → `01-protocol-guide.md` |
| `../../../DocsClosed/0.1.1详细任务清单.md` | 4 | 删除引用或替换为开源内部描述 |

**工作量估算**：8 小时（含路径重映射表编写 + 批量 sed 替换 + 验证）。

#### P0-2：开源/闭源边界违规（3 目录 + 4 跨引用）

**问题描述**：

1. `docs/OpenStandards/_research_v1.0/`、`_research_v2.0/`、`_research_v2.1/` 3 个内部审查报告目录误入开源工作树（虽未跟踪但物理路径已越界）；
2. 4 处开源文档跨引用闭源 `../../../DocsClosed/0.1.1详细任务清单.md`。

**影响**：违反"开源文档仅包含可公开设计文档"原则，存在内部审查报告误提交到开源仓库的风险；跨边界引用导致开源文档引用路径断裂（闭源文件不在开源仓库中）。

**修复方案**：

| 违规类型 | 修复方案 |
|---------|---------|
| 3 个 `_research_v*` 目录 | 整体迁移至 `docs-closed/_research_open-standards/` 或 `docs-closed/agentrt/_research_open-standards/`；在 `docs/.gitignore` 追加 `OpenStandards/_research_*/` 排除规则 |
| 4 处 `DocsClosed/` 跨引用 | 删除跨边界引用，替换为开源内部描述（如"详见 IPC Bus 规范化设计章节"） |

**工作量估算**：2 小时（目录迁移 + .gitignore 更新 + 4 处引用替换）。

### 10.5 P1 级重要问题（建议修复）

#### P1-1：闭源 `agentrt_` → `airy_` 前缀迁移停滞（606 处）

**问题描述**：闭源 `docs-closed/agentrt/` 218 处 + `docs-closed/agentrt-linux/` 388 处 = 606 处 `agentrt_*` 前缀残留，其中 `agentrt-linux基本工程标准规范.md` 完全未迁移（`airy_*` 0 处）。

**影响**：闭源工程标准手册与实际源码（已迁移至 `airy_*`）严重背离，误导开发者使用错误前缀；工程标准手册内容自相矛盾（标注 `agentrt_*` 为"已废弃"但自身代码示例仍使用 `agentrt_*`）。

**修复方案**：

1. 工程标准手册层（`agentrt工程标准规范手册.md`、`agentrt-linux基本工程标准规范.md`）：批量替换代码示例中的 `agentrt_*` → `airy_*`，保留迁移说明表格中的旧前缀作为"已废弃"对照；
2. 设计文档层（`_design_0.1.1/`）：评估是否需要迁移（历史设计文档可保留旧前缀，但需在文档头部声明"前缀已废弃，仅作历史参考"）；
3. 审查报告与归档（`_review_*`、`_archive_*`）：可不迁移，但需在目录 README 中声明"历史文档，前缀未迁移"。

**工作量估算**：12 小时（手册替换 4h + 设计文档评估 4h + 验证 4h）。

#### P1-2：邮箱域名未统一（4 个域名并存）

**问题描述**：`@spharx.cn`、`@spharx.com`、`@spharx.io`、`@spharx.dev` 4 个域名并存，缺乏统一策略。

**修复方案**：统一为单一域名（建议 `@spharx.com` 作为主域名），或明确各域名用途（如 `@spharx.com` 对外、`@spharx.cn` 内部、`@spharx.io` 安全报告、`@spharx.dev` 邮件列表）。

**工作量估算**：2 小时（域名策略制定 + 批量替换 + 验证）。

### 10.6 P2 级次要问题（可选修复）

#### P2-1：Go 代码示例 XXX 占位符（2 处）

`docs/AirymaxOS/50-engineering-standards/10-coding-style/Go_coding_style.md:1521, 1525` 使用 `XXX` 作为模块名/资源名占位符，应替换为具体示例（如 `Agent 管理模块`、`Agent 资源`）。

**工作量估算**：15 分钟。

#### P2-2：`your-team@spharx.cn` 占位邮箱未明确标记（1 处）

`docs/AirymaxRT/140-application-development/20-manager-development.md:284` 的 `your-team@spharx.cn` 应替换为 `<your-team>@spharx.com` 明确占位标记。

**工作量估算**：5 分钟。

#### P2-3：闭源版本号差距（v0.2.5 vs v0.1.1）

闭源 v0.2.5 与开源 v0.1.1 版本号差距 4 个小版本，建议在闭源手册头部明确"版本号差异说明"（如"闭源 v0.2.5 对应开源 v0.1.1 + 内部修复 Wave 2 v2 / ES-SEL4 消解 / 附录 D 修正"）。

**工作量估算**：30 分钟（头部说明修订）。

### 10.7 修复优先级与工作量汇总

| 优先级 | 问题编号 | 问题描述 | 工作量 | 阻断 M1 |
|-------|---------|---------|-------|--------|
| P0 | P0-1 | 断裂引用系统性扩散（67+ 处） | 8h | ✅ 阻断 |
| P0 | P0-2 | 开源/闭源边界违规（3 目录 + 4 跨引用） | 2h | ✅ 阻断 |
| P1 | P1-1 | 闭源前缀迁移停滞（606 处） | 12h | ❌ 不阻断（但影响工程标准手册可用性） |
| P1 | P1-2 | 邮箱域名未统一（4 域名） | 2h | ❌ 不阻断 |
| P2 | P2-1 | Go 代码 XXX 占位符（2 处） | 0.25h | ❌ 不阻断 |
| P2 | P2-2 | your-team 邮箱未标记（1 处） | 0.08h | ❌ 不阻断 |
| P2 | P2-3 | 闭源版本号差距说明 | 0.5h | ❌ 不阻断 |
| **合计** | — | — | **24.83h** | — |

### 10.8 行动建议

1. **立即执行（M1 启动前阻断项）**：
   - 修复 P0-1（断裂引用 67+ 处，8h）：建立路径重映射表，批量 sed 替换，验证全部 67+ 处引用解析通过；
   - 修复 P0-2（边界违规，2h）：迁移 3 个 `_research_v*` 目录至闭源仓库，删除 4 处跨边界引用。

2. **M1 期间执行**：
   - 修复 P1-1（闭源前缀迁移，12h）：优先修复两本工程标准手册，子系统规范层已对齐无需修复；
   - 修复 P1-2（邮箱域名统一，2h）：制定域名策略并批量替换。

3. **M1 后执行**：
   - 修复 P2-1/P2-2/P2-3（次要问题，0.83h）：作为文档质量持续改进的一部分。

4. **建立机制（防止问题复发）**：
   - 在 CI/CD 中引入引用解析检查脚本（`check-broken-references.sh`），对每次 PR 自动验证所有 .md 文件的内部引用解析性；
   - 在 `docs/.gitignore` 追加 `OpenStandards/_research_*/` 排除规则，防止内部研究文档误提交；
   - 在文件迁移流程中追加"引用方同步更新"检查项，防止再次出现因文件迁移导致的断裂引用扩散。

### 10.9 最终判定

**5 个文档仓库当前未达到"文档侧可开发"状态**。技术内核（微核心/微内核术语区分、5 维同源映射、IRON-9 v2 三层共享模型、URL 格式一致性、反抄袭合规）已达到可发布水平，但**断裂引用系统性扩散**（67+ 处跨 34 文件）和**开源/闭源边界违规**（3 目录 + 4 跨引用）两项 P0 级问题必须在进入 1.0.1 M1 代码开发前完成修复。

**预计修复工作量**：P0 阻断项 10h（P0-1 8h + P0-2 2h），P1/P2 重要/次要问题 14.83h，合计 24.83h。

---

> **报告结束** | Airymax 文档规范与质量控制 v2.1 复审报告 | 2026-07-13
> **审查员**：Airymax 文档质量审查专家（agentrt 子代理）
> **保密级别**：SPHARX Ltd 内部参考，**闭源不公开**
> **SPDX-License-Identifier**：AGPL-3.0-or-later OR Apache-2.0
