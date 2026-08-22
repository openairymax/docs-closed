Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agent-linux（AirymaxOS）工程标准合并审查报告

> **报告编号**: C-2.6（工程标准合并审查）
> **报告日期**: 2026-07-09
> **报告版本**: v0.3.0（系统性分析与决策阶段）
> **审查范围**: `docs/AirymaxOS/50-engineering-standards/` 全部 22 份 Markdown 文件 + 5 个子目录 + 闭源总纲 `docs-closed/agent-linux/agent-linux基本工程标准规范.md`（1444 行）+ OLK-6.6 参考基线 `01Reference/kernel-OLK-6.6/Documentation/process/coding-style.rst`
> **机密级别**: 闭源不公开（SPHARX Ltd 内部参考）
> **核心结论**: 当前工程标准体系存在 **3 类结构性问题**——(1) 同一规则被分配 2-4 个不同编号（编号混乱）；(2) 同一编号在不同文件被赋予 2-3 个不同含义（语义冲突）；(3) 公开 OS-* 与闭源 OS-IRON/OS-BAN/OS-STD/OS-KER/OS-FMT 编号体系未对齐。本报告给出 9 项合并决策与 4 阶段执行计划。

---

## 1. 审查概述

### 1.1 背景与问题触发

agent-linux（AirymaxOS）的工程标准体系自 0.1.1 版本奠基以来，经历了三轮增量扩展：

1. **0.1.1 奠基期**：建立 7 主题文档（01-07）+ 1 合规检查（08）+ 1 许可证（09）+ 6 扩展专题（60/70/80/100/110/120）的初步架构。
2. **0.2.x 演进期**：新增 `10-coding-style/` 子目录承载 C/Rust 多语言风格与安全编码规范，与 01-03 主题卷形成职责重叠。
3. **0.2.4-0.3.0 闭源总纲期**：撰写 1444 行闭源工程标准规范总纲，引入 OS-FMT/OS-DRV/OS-BUILD/OS-TEST/OS-OBS/OS-SEC/OS-ABI 等 7 个新前缀与公开编号体系并行。

三轮扩展未做集中校验，导致规则编号在多份文档中**重复定义、语义冲突、引用断裂**。本审查即针对此问题展开。

### 1.2 审查方法

本审查采用"四步证据法"：

| 步骤 | 工具 | 目的 |
|------|------|------|
| 1. 文件清查 | `Glob` + `ls` | 列出 50-engineering-standards/ 全部 .md 文件与子目录 |
| 2. 职责采样 | `Read`（每文件前 100-200 行） | 提取每份文档的"章节定位"声明与权威声明 |
| 3. 编号枚举 | `Grep` 全目录正则 `OS-(KER\|STD-CODE\|STD-FMT\|...)-[A-Z0-9-]+` | 抓取所有规则编号及其上下文文本 |
| 4. 交叉比对 | 人工 + 表格 | 对同一编号在不同文件的定义、同一规则在不同文件的编号做矩阵化比对 |

参考基线为 OLK-6.6 `Documentation/process/coding-style.rst`（Linux 6.6 内核编码风格权威来源）。

### 1.3 审查范围

**公开文档（22 份 + 5 子目录）**：

```
docs/AirymaxOS/50-engineering-standards/
├── README.md                              (40KB,  主索引)
├── 00-engineering-standards-handbook.md   (27KB,  SSoT 索引)
├── 01-coding-standards.md                 (27KB,  代码规范)
├── 02-code-format.md                      (19KB,  代码格式)
├── 03-code-style.md                       (24KB,  代码风格)
├── 04-engineering-philosophy.md           (41KB,  工程思想)
├── 05-development-process.md              (35KB,  开发流程)
├── 06-toolchain-and-automation.md         (34KB,  工具链)
├── 07-maintainers-and-governance.md       (50KB,  维护者治理)
├── 08-compliance-checklist.md             (21KB,  合规检查)
├── 09-license-strategy.md                 (8KB,   已废弃→110)
├── 60-checkpatch-rule-map.md              (31KB,  checkpatch 映射)
├── 70-kernel-doc-standard.md              (18KB,  kernel-doc 规范)
├── 80-clang-format-enforcement.md        (17KB,  clang-format 配置)
├── 100-deprecated-api-registry.md        (21KB,  弃用 API 清单)
├── 110-spdx-license-compliance.md         (18KB,  SPDX 合规)
├── 120-cross-project-code-sharing.md      (19KB,  跨项目代码共享)
└── 10-coding-style/                       (子目录)
    ├── README.md                           (22KB,  子目录索引)
    ├── C_coding_style_standard.md          (27KB,  C 风格)
    ├── C_coding_style_standard_supplement.md (23KB,  C 风格补充)
    ├── C_Cpp_secure_coding_standard.md     (19KB,  C/C++ 安全)
    ├── Rust_coding_style_standard.md        (19KB,  Rust 风格)
    └── Rust_secure_coding_standard.md      (19KB,  Rust 安全)
```

**闭源参考（1 份）**：`docs-closed/agent-linux/agent-linux基本工程标准规范.md`（80KB / 1444 行）。

**OLK-6.6 基线（1 份）**：`01Reference/kernel-OLK-6.6/Documentation/process/coding-style.rst`（44KB）。

---

## 2. 文件清单与职责矩阵

### 2.1 公开 22 份文档职责矩阵

| # | 文件 | 职责定位 | 行数级 | 规则编号体系 | 状态 |
|---|------|---------|--------|-------------|------|
| 0 | README.md | 主索引与总纲 | ~1200 | 引用 | 活跃 |
| 1 | 00-engineering-standards-handbook.md | SSoT 索引 + IRON 铁律 + SSoT 注册表 | ~900 | OS-IRON/STD/KER/BAN/ABI/ACC + OS-STD-CODE/FMT/STY/GOV | 活跃 |
| 2 | 01-coding-standards.md | 语义层代码规则（命名/函数/注释/类型/错误/内存/锁） | ~900 | OS-STD-001~020 + OS-KER-002 + OS-STD-CODE-001（首条混用） | 活跃 |
| 3 | 02-code-format.md | 机械格式规则（缩进/行宽/大括号/空格/clang-format） | ~600 | OS-KER-002~019 + OS-STD-047/202~206 | 活跃 |
| 4 | 03-code-style.md | 工程风格决策（模块化/抽象/策略机制/防御性） | ~750 | OS-KER-022~032 + OS-STD-212~213 | 活跃 |
| 5 | 04-engineering-philosophy.md | 工程思想（双层稳定性/渐进式/审查优先） | ~1300 | OS-IRON-001~006 + OS-KER-002/003/006/010/020~022/030~031/040~041/050 | 活跃 |
| 6 | 05-development-process.md | 补丁生命周期/维护者层级/补丁格式 | ~1100 | OS-STD-101~234（与 06 重叠） | 活跃 |
| 7 | 06-toolchain-and-automation.md | 7 层验证/checkpatch/CI/CD | ~1100 | OS-STD-002~158（与 05 重叠） | 活跃 |
| 8 | 07-maintainers-and-governance.md | MAINTAINERS/层级/DCO/SSoT 注册表 | ~1600 | OS-STD-GOV-001~007 + OS-STD-061~072 | 活跃 |
| 9 | 08-compliance-checklist.md | 17 项检查规则 + 检查脚本 | ~558 | STD-DOC-01~08/STD-CODE-01~05/STD-IRON-01~04/STD-CI-01 | 活跃 |
| 10 | 09-license-strategy.md | SPDX 许可证策略矩阵（已废弃） | ~280 | 引用 110 | **已废弃** |
| 11 | 60-checkpatch-rule-map.md | checkpatch 规则→OS-STD-CODE-NNN 映射 | ~950 | OS-STD-CODE-001~999 | 活跃 |
| 12 | 70-kernel-doc-standard.md | kernel-doc 注释规范 | ~580 | OS-STD-DOC-001~NNN | 活跃 |
| 13 | 80-clang-format-enforcement.md | .clang-format 配置 + CI 门禁 | ~560 | OS-KER-011/012（与 02 冲突） | 活跃 |
| 14 | 100-deprecated-api-registry.md | 弃用 API 清单（strcpy/BUG/typedef 等） | ~660 | 引用 OS-BAN | 活跃 |
| 15 | 110-spdx-license-compliance.md | SPDX 合规 5 类文件分类检查 | ~580 | OS-STD-SPDX-001~003 | 活跃 |
| 16 | 120-cross-project-code-sharing.md | IRON-9 v2 三层模型 + 6 个 [SC] 头文件 | ~580 | OS-IRON-008~014 引用 | 活跃 |
| 17 | 10-coding-style/README.md | 子目录总索引 | ~680 | 引用 | 活跃 |
| 18 | 10-coding-style/C_coding_style_standard.md | C 语言编码风格规范 | ~840 | OS-KER-011~015 + OS-STD-005/028/029（与 02 重叠） | 活跃 |
| 19 | 10-coding-style/C_coding_style_standard_supplement.md | C 风格补充（OLK-6.6 源码行号映射） | ~720 | OS-KER-007~015 + OS-STD-CODE-010/012/014/015（与 02 重叠且与 18 冲突） | 活跃 |
| 20 | 10-coding-style/C_Cpp_secure_coding_standard.md | C/C++ 安全编码规范 | ~600 | OS-SEC-010~020 + OS-BAN-006/007 + OS-KER-033 | 活跃 |
| 21 | 10-coding-style/Rust_coding_style_standard.md | Rust 编码风格规范 | ~610 | OS-STD-030~038 + OS-SEC-001~003 | 活跃 |
| 22 | 10-coding-style/Rust_secure_coding_standard.md | Rust 安全编码规范 | ~610 | OS-SEC-NNN | 活跃 |

### 2.2 闭源总纲职责

`agent-linux基本工程标准规范.md`（1444 行）是**闭源工程标准的总纲**，与公开 22 份文档构成"闭源总纲 + 开源子文档"双层结构。其规则编号体系如下：

| 前缀 | 含义 | 数量 | 与公开文档关系 |
|------|------|------|---------------|
| OS-IRON-001~014 | 工程铁律 | 14 | 与公开 00-handbook（10 条）+ 04-philosophy（重定义 6 条）冲突 |
| OS-BAN-001~011 | 禁止规则 | 7（间断） | 与公开 01/10-coding-style 部分冲突 |
| OS-STD-001~052 | 标准规则 | 19（间断） | 与公开 01（OS-STD-001~020）大量语义错位 |
| OS-ACC-001 | 验收标准 | 1 | 与公开 00-handbook OS-ACC-001~005 冲突 |
| OS-KER-001~003 | 内核工程规则 | 3 | 与公开 02（OS-KER-002~019）大量冲突 |
| OS-FMT-001~007 | 格式规则 | 7 | **公开文档无此前缀**，与 OS-KER-005/004/008 等冲突 |
| OS-DRV/BUILD/TEST/OBS/SEC/ABI | 子域规则 | 引用 | 公开文档部分覆盖但未集中注册 |

---

## 3. 重复问题清单

### 3.1 重复对 R-1：01-coding-standards.md vs 02-code-format.md（命名边界模糊）

| 维度 | 01-coding-standards.md | 02-code-format.md |
|------|------------------------|---------------------|
| 自我定位 | "语义层代码规则（命名/函数/注释/类型/错误/内存/锁）" | "纯机械格式规则（缩进/行宽/大括号/空格）" |
| 实际重叠 | §6 类型规范（typedef 5 种例外、bool 边界、u8/u16/u32） | §1-§7 也涉及类型相关格式（如指针声明 `*` 贴名字） |
| 重叠内容 | typedef 限制、bool 使用边界、kernel-doc 注释 | 缩进/行宽/大括号/空格、指针声明格式 |
| 重叠度 | 中等 | 中等 |
| 严重度 | **P1-MAJOR** | 命名边界虽声明清晰，但 01 §6 类型规范与 02 §4.3 指针声明存在概念交叉，且都使用 OS-KER-002 编号（**编号冲突**，见 §4.1） |

**示例**：01 §6.2 用 `OS-KER-002` 定义"内核内部用 u8/u16/u32/u64，UAPI 用 __u32"；02 §1.5 也用 `OS-KER-002` 定义"Kconfig 中允许混用 Tab 与空格"。**同一编号两种含义**。

### 3.2 重复对 R-2：02-code-format.md vs 80-clang-format-enforcement.md（强烈重叠）

| 维度 | 02-code-format.md | 80-clang-format-enforcement.md |
|------|-------------------|-------------------------------|
| 自我定位 | "格式规则定义层（OS-KER-004~021）" | ".clang-format 工具配置层（YAML + OLK-6.6 源码行号 + CI 门禁）" |
| 实际重叠 | §9 clang-format 关键配置项表（已在 02 内嵌） | §1 关键配置项详解（IndentWidth/TabWidth/ColumnLimit 等） |
| 重叠内容 | 缩进/行宽/大括号/指针对齐/空格的全部配置项 | 同一组配置项的详细解释（OLK-6.6 行号 + 理由） |
| 重叠度 | **高（>70%）** | 高 |
| 严重度 | **P0-CRITICAL** | 80 §0.1 已用"交叉引用"声明职责分离，但实际两份文档都包含完整 YAML 配置项与配置理由。编号冲突：02 用 OS-KER-005（Tab），80 用 OS-KER-011（缩进配置）；02 用 OS-KER-004（80 列），80 用 OS-KER-012（行宽） |

**示例 YAML 重叠**：

```yaml
# 02-code-format.md §9 与 80-clang-format-enforcement.md §1.1 都给出：
IndentWidth: 8
TabWidth: 8
UseTab: Always
ColumnLimit: 80
```

两份文档对同一份 `.clang-format` 配置做了解释，仅 80 附加了 OLK-6.6 源码行号。

### 3.3 重复对 R-3：02-code-format.md vs 10-coding-style/C_coding_style_standard.md（严重重叠）

| 维度 | 02-code-format.md | 10-coding-style/C_coding_style_standard.md |
|------|-------------------|-------------------------------------------|
| 自我定位 | "agent-linux 代码格式规则唯一权威来源（SSoT）" | "C 语言编码风格规范（基于 Linux 6.6 内核 coding-style.rst）" |
| 实际重叠 | §1 缩进 / §2 行宽 / §3 大括号 / §4 空格 / §5 switch-case | §2.1 缩进 / §2.2 行宽 / §2.3 大括号 / §2.4 空格（完全相同主题） |
| 重叠内容 | Tab 8 字符 / 80 列 / K&R / 关键字后空格 / 指针 `*` 贴名字 | 同一组规则，但**编号完全不同** |
| 重叠度 | **高（>80%）** | 高 |
| 严重度 | **P0-CRITICAL** | 02 §0 已声明"`10-coding-style/C_coding_style_standard.md` 中的格式规则均引用本卷，不得重新定义"，但 C_coding_style_standard.md §2.1 实际**重新定义**了 OS-KER-011（Tab 8 字符），与 02 §1.1 的 OS-KER-005（Tab 8 字符）冲突 |

**编号冲突示例**：

| 规则 | 02-code-format.md | 10-coding-style/C_coding_style_standard.md |
|------|---------------------|---------------------------------------------|
| Tab 8 字符 | OS-KER-005 | OS-KER-011 |
| 80 列行宽 | OS-KER-004 | OS-KER-012 |
| K&R 大括号 | OS-STD-047 + OS-KER-008 | OS-KER-013 |
| 关键字后空格 | OS-KER-010 | OS-KER-014 |
| 函数长度 | OS-STD-006（在 01 卷） | OS-KER-015 |

### 3.4 重复对 R-4：10-coding-style/C_coding_style_standard.md vs C_coding_style_standard_supplement.md（编号完全冲突）

| 维度 | C_coding_style_standard.md | C_coding_style_standard_supplement.md |
|------|---------------------------|----------------------------------------|
| 自我定位 | "C 语言编码风格规范" | "C 风格补充（OLK-6.6 源码行号映射）" |
| 实际重叠 | §2.1 OS-KER-011 Tab 8 字符 | §1 OS-KER-011 Tab-8 缩进强制（同义，重复） |
| 编号冲突 | §2.3 OS-KER-013 = K&R 大括号 | §8 OS-KER-013 = 禁止结构体 typedef（**完全不同**） |
| 编号冲突 | §2.4 OS-KER-014 = 空格规则 | §9 OS-KER-014 = 零警告门禁（**完全不同**） |
| 编号冲突 | §4.1 OS-KER-015 = 函数长度 | §11 OS-KER-015 = 禁止 BUG()/BUG_ON()（**完全不同**） |
| 重叠度 | 中（同义部分）+ 严重（编号冲突） | 同 |
| 严重度 | **P0-CRITICAL** | 同一份子目录下两份文档对 OS-KER-013/014/015 给出**完全不同的定义**，是当前体系最严重的内部冲突 |

### 3.5 重复对 R-5：04-engineering-philosophy.md vs 00-engineering-standards-handbook.md（IRON 编号冲突）

| 维度 | 04-engineering-philosophy.md | 00-engineering-standards-handbook.md |
|------|------------------------------|--------------------------------------|
| 自我定位 | "工程思想五大主题章节" | "SSoT 索引 + IRON 铁律汇总" |
| IRON-003 含义 | "regression 必须在当前 stabilization 阶段修复" | "补丁序列中点必须可编译可运行，git bisect 友好" |
| IRON-005 含义 | "已导出至用户空间的接口不允许破坏向后兼容" | "DCO Signed-off-by 链强制" |
| IRON-006 含义 | "决策者必须提前声明决策是初步的、可能是错的" | "信任链分层不可越级提交" |
| 重叠度 | 中 | 中 |
| 严重度 | **P0-CRITICAL** | 00-handbook 是 SSoT 索引并自我声明"以本手册为准"，但 04 实际重新定义了 6 条 IRON 铁律的语义。3 条 IRON 编号出现 2 种不同定义 |

### 3.6 重复对 R-6：04-engineering-philosophy.md vs 闭源总纲（IRON 编号冲突）

| IRON 编号 | 04-engineering-philosophy.md（公开） | 闭源总纲 §4 |
|----------|------------------------------------|-------------|
| OS-IRON-001 | "用户空间 ABI 永不破坏" | "用户空间 ABI 永不破坏"（一致） |
| OS-IRON-002 | "内核内部 API 不保证稳定" | "内核内部 API 不保证稳定"（一致） |
| OS-IRON-003 | "regression 必须修复" | "策略与机制分离"（**完全不同**） |
| OS-IRON-004 | （04 未定义） | "渐进式开发" |
| OS-IRON-005 | "已导出接口不允许破坏兼容" | "审查优先文化"（**完全不同**） |
| OS-IRON-006 | "决策者提前声明" | "不破坏用户空间原则"（**完全不同**） |

**严重度 P0-CRITICAL**：闭源总纲附录 A 给出 OS-IRON-001~014 完整注册表，与公开 00-handbook 的 OS-IRON-001~010 在 003/005/006 三条上完全冲突。

### 3.7 重复对 R-7：05-development-process.md vs 06-toolchain-and-automation.md（OS-STD 编号段冲突）

| OS-STD 编号 | 05-development-process.md §12 | 06-toolchain-and-automation.md §11 |
|------------|------------------------------|------------------------------------|
| OS-STD-101 | "L1/L2 接口设计需 RFC + 顶级维护者 ACK" | "checkpatch --strict 无 ERROR" |
| OS-STD-102 | "设计文档含五维原则映射小节" | "WARNING/CHECK 可被辩护" |
| OS-STD-103 | "早期审查 PR 含完整补丁描述" | "C/C++ 通过 clang-format" |
| OS-STD-131 | "develop nightly build 三架构三配置" | "子仓维护 ci/nightly/release workflow" |
| OS-STD-132 | "develop 连续 3 天失败冻结补丁" | "CI 矩阵覆盖 9 组合" |
| OS-STD-133 | "airymax-mm 补丁说明无子系统归属理由" | "PR 必须过全部检查（同 031/233）" |

**严重度 P0-CRITICAL**：05 与 06 在 OS-STD-101~158 段共有 30+ 条编号语义冲突。05 §12 自我声明"与 07 卷规则编号注册表对齐"，但 06 §11 也作同样声明，二者实际互不对齐。

### 3.8 重复对 R-8：09-license-strategy.md vs 110-spdx-license-compliance.md（已识别废弃）

09 §0 已明确废弃声明（2026-07-09）：

```markdown
> **⚠️ 本文档已废弃（2026-07-09）**：本卷的许可证策略矩阵与合规执行
> 内容已合并至 110-spdx-license-compliance.md。请以 110 卷为权威来源。
> 本卷保留仅作为历史参考，不再维护更新。
```

**严重度 P2-MINOR**：废弃声明已就位，仅需在 README 与 00-handbook 中标注"已废弃，参见 110"链接，并考虑物理移除。

### 3.9 重复对 R-9：08-compliance-checklist.md vs 闭源总纲 §8（检查规则命名体系冲突）

| 维度 | 08-compliance-checklist.md | 闭源总纲 §8 |
|------|---------------------------|-------------|
| 检查规则前缀 | STD-DOC-* / STD-CODE-* / STD-IRON-* / STD-CI-* | OS-STD-050~052（仅脚本规范） |
| 检查项数量 | 17 项（STD-DOC-01~08 + STD-CODE-01~05 + STD-IRON-01~04） | 4 类，OS-STD-050/051/052 + STD-IRON-01~04 |
| 编号体系 | 4 段独立编号（与 OS-* 体系并行） | 沿用 OS-* 体系 |
| 严重度 | **P1-MAJOR** | 08 自创 STD-DOC/STD-CODE/STD-IRON/STD-CI 四个独立前缀，与全项目 OS-* 编号体系并行存在，未对齐 |

### 3.10 重复对 R-10：100-deprecated-api-registry.md vs 01-coding-standards.md vs 10-coding-style/C_Cpp_secure_coding_standard.md（strscpy 规则三处定义）

`strscpy` 强制替代 `strcpy/strncpy/strlcpy` 在 4 份文档中以 4 种不同编号出现：

| 文档 | 编号 | 规则文本 |
|------|------|---------|
| 00-engineering-standards-handbook.md §3.2.1 | OS-STD-CODE-003 | "禁止 strcpy/strncpy/strlcpy，强制 strscpy" |
| 01-coding-standards.md（引用 handbook） | OS-STD-CODE-003 | 同上 |
| 闭源总纲 §2.2.4 | OS-BAN-004 | "禁止 strcpy/strncpy/strlcpy，强制 strscpy" |
| 10-coding-style/C_coding_style_standard_supplement.md §1 | OS-STD-CODE-010 | "strscpy 强制替代 strcpy/strncpy/strlcpy" |
| 60-checkpatch-rule-map.md §1 | OS-STD-CODE-010 | 映射到 checkpatch STRCPY/STRLCPY/STRNCPY 规则 |
| 10-coding-style/C_Cpp_secure_coding_standard.md §1.2 | OS-BAN-006 | "禁止 strcpy/strncpy/strlcpy，强制 strscpy" |

**严重度 P0-CRITICAL**：同一规则在 6 处出现，使用 4 种不同编号（OS-STD-CODE-003 / OS-BAN-004 / OS-STD-CODE-010 / OS-BAN-006）。

### 3.11 重复对 R-11：goto 集中出口模式（3 处定义）

| 文档 | 编号 |
|------|------|
| 00-handbook §3.2.1 | OS-STD-CODE-002 |
| 闭源总纲 §2.2.4 | OS-KER-001 |
| 10-coding-style/C_coding_style_standard_supplement.md §2 | OS-KER-009 |

**严重度 P0-CRITICAL**：goto 集中出口这一最基础的内核工程范式在 3 份文档中以 3 种不同编号定义。

### 3.12 重复对 R-12：禁止 BUG()/BUG_ON()（3 处定义）

| 文档 | 编号 |
|------|------|
| 00-handbook §3.3 | OS-KER-004 |
| 闭源总纲 §2.2.4 | OS-BAN-002 |
| 10-coding-style/C_coding_style_standard_supplement.md §11 | OS-KER-015 |

**严重度 P0-CRITICAL**。

### 3.13 重复对 R-13：禁止 %p 默认输出（3 处定义）

| 文档 | 编号 |
|------|------|
| 00-handbook §3.4 | OS-BAN-003 |
| 闭源总纲 §2.2.4 | OS-BAN-005 |
| 10-coding-style/C_Cpp_secure_coding_standard.md §4.3 | OS-BAN-007 |

**严重度 P0-CRITICAL**。

### 3.14 重复对 R-14：bool 仅用于返回值与栈变量（3 处定义）

| 文档 | 编号 |
|------|------|
| 01-coding-standards.md §6.3 | OS-KER-002（**与同文件 §6.2 的"u8/u16/u32"共用编号**） |
| 00-handbook §3.3 | OS-KER-008 |
| 10-coding-style/C_coding_style_standard_supplement.md §3 | OS-KER-008 |
| 闭源总纲 §2.5 | OS-STD-011 |

**严重度 P0-CRITICAL**：01-coding-standards.md 内部还出现 OS-KER-002 双义（types 与 bool），是文件级内部冲突。

### 3.15 重复对汇总

| 严重度 | 数量 | 重复对编号 |
|--------|------|-----------|
| P0-CRITICAL | 10 | R-2、R-3、R-4、R-5、R-6、R-7、R-10、R-11、R-12、R-13、R-14 |
| P1-MAJOR | 3 | R-1、R-9 |
| P2-MINOR | 1 | R-8 |

---

## 4. 不一致问题清单

### 4.1 同编号双义冲突（OS-KER 系列）

下表枚举所有 OS-KER 编号在不同文件的语义冲突：

| 编号 | 01-coding-standards | 02-code-format | 03-code-style | 04-engineering-philosophy | 10-coding-style/C | 10-coding-style/C-supplement | 10-coding-style/C-secure | 80-clang-format |
|------|---------------------|----------------|---------------|---------------------------|--------------------|------------------------------|--------------------------|------------------|
| OS-KER-001 | — | — | — | — | — | — | — | — |
| OS-KER-002 | u8/u16/u32 + bool（**双义**） | Kconfig 混用 | — | you broke it, you fix it | — | — | — | — |
| OS-KER-003 | — | 行尾禁止空白 | — | 补丁中点可编译 | — | goto 集中错误处理 | — | — |
| OS-KER-004 | — | 80 列 | — | — | — | — | — | — |
| OS-KER-005 | — | Tab 8 字符 + 字符串禁止断行（**双义**） | — | — | — | — | — | — |
| OS-KER-006 | — | 后继行短于父行 | — | 内核内部 API 可变 | — | — | — | — |
| OS-KER-007 | — | — | — | — | — | 内核态禁 float | — | — |
| OS-KER-008 | — | 函数开括号独占一行 | — | — | — | bool 仅返回值 | — | — |
| OS-KER-009 | — | 单语句大括号规则 | — | — | — | goto 集中错误处理 | — | — |
| OS-KER-010 | — | 关键字后空格 | — | 内核不内置策略 | — | — | — | — |
| OS-KER-011 | — | sizeof/typeof 不加空格 | — | — | Tab 8 字符 | Tab-8 缩进强制 | — | 缩进配置 |
| OS-KER-012 | — | 指针声明 `*` 贴名字 | — | — | 80 列行宽 | 80 列 | — | 行宽配置 |
| OS-KER-013 | — | 二元/三元运算符 | — | — | K&R 大括号 | 禁止 typedef 结构体 | — | — |
| OS-KER-014 | — | 括号内禁止空格 | — | — | 空格规则 | 零警告门禁 | — | — |
| OS-KER-015 | — | case 与 switch 对齐 | — | — | 函数长度 | 禁止 BUG()/BUG_ON() | — | — |
| OS-KER-022 | — | — | 反过度抽象 | 补丁顺序 | — | — | — | — |
| OS-KER-030 | — | — | IS_ENABLED | bug 修复附回归测试 | — | — | — | — |
| OS-KER-031 | — | — | 引用计数强制 | bug 修复复杂度匹配 | — | — | — | — |
| OS-KER-033 | — | — | — | — | — | — | 柔性数组成员 | — |

**冲突统计**：

- OS-KER-002：4 种不同含义（最严重）
- OS-KER-003、OS-KER-011、OS-KER-012、OS-KER-013、OS-KER-014、OS-KER-015：3 种不同含义
- OS-KER-005、OS-KER-006、OS-KER-008、OS-KER-009、OS-KER-010、OS-KER-022、OS-KER-030、OS-KER-031：2 种不同含义

### 4.2 同编号双义冲突（OS-STD 系列）

| 编号 | 01-coding-standards | 00-handbook | 闭源总纲 |
|------|---------------------|-------------|---------|
| OS-STD-001 | 全局符号描述性命名（与 OS-STD-CODE-001 混用） | OS-STD-CODE-001（4 段） | 全局符号描述性命名 |
| OS-STD-008 | 原型必须含参数名 | — | kernel-doc 强制 |
| OS-STD-009 | EXPORT_SYMBOL 紧跟函数定义 | — | 注释解释"为什么" |
| OS-STD-010 | 注释说明 WHAT 与 WHY | — | 类型规范（u8/u16/u32） |
| OS-STD-011 | 通用代码用通用风格 | — | bool 仅返回值与栈变量 |
| OS-STD-020 | typedef 严格限制 | — | 补丁格式规范 |
| OS-STD-021 | — | — | 稳定版维护规则 |
| OS-STD-030 | — | — | checkpatch 强制 |
| OS-STD-040 | — | — | MAINTAINERS 文件规范 |
| OS-STD-101~158 | — | — | — （与 05/06 冲突，见 §3.7） |

**编号格式冲突**：

- 00-handbook 使用 **4 段**编号：`OS-STD-CODE-NNN` / `OS-STD-FMT-NNN` / `OS-STD-STY-NNN` / `OS-STD-GOV-NNN`
- 01-coding-standards.md **首条使用 4 段**（OS-STD-CODE-001），**第二条起退化为 3 段**（OS-STD-002）——同文件内部不一致
- 闭源总纲与 05/06/07 使用 **3 段**编号：`OS-STD-NNN`

### 4.3 同编号双义冲突（OS-IRON 系列）

| OS-IRON 编号 | 00-handbook §2.1 | 04-engineering-philosophy | 闭源总纲 §4 + 附录 A |
|--------------|------------------|---------------------------|----------------------|
| OS-IRON-001 | 不破坏用户空间 ABI | 不破坏用户空间 ABI | 用户空间 ABI 永不破坏（一致） |
| OS-IRON-002 | 内核内部 API 不保证稳定 | 内核内部 API 不保证稳定 | 内核内部 API 不保证稳定（一致） |
| OS-IRON-003 | 补丁中点可编译可运行 | **regression 必须修复** | **策略与机制分离** |
| OS-IRON-004 | 7 层验证强制 | — | 渐进式开发 |
| OS-IRON-005 | DCO Signed-off-by 强制 | **已导出接口不允许破坏** | **审查优先文化** |
| OS-IRON-006 | 信任链分层不可越级提交 | **决策者必须提前声明** | **不破坏用户空间原则** |
| OS-IRON-007 | Reviewed-by 不可替代 Signed-off-by | — | DCO 强制 |
| OS-IRON-008 | regression 不可接受 | — | 共享契约层 6 个头文件双向 CI |
| OS-IRON-009 | IRON-9 v2 同源 | — | 代码共享边界声明 |
| OS-IRON-010 | 组织 6 级成熟度 Level 2 | — | "Linux 6.6 为基、seL4 为鉴"工程取向 |
| OS-IRON-011~014 | — | — | 闭源新增 4 条（双源边界、seL4 借鉴、8 子仓、[SC] 单一数据源） |

**严重度 P0-CRITICAL**：3 条 IRON 铁律（003/005/006）在三份文档中有 3 种完全不同的定义。这是工程标准体系**最严重的语义冲突**，因为 IRON 铁律是"不可妥协"级别。

### 4.4 同编号双义冲突（OS-BAN 系列）

| OS-BAN 编号 | 00-handbook §3.4 | 01-coding-standards | 10-coding-style/C-secure | 闭源总纲 §2.2.4 |
|--------------|------------------|---------------------|---------------------------|-----------------|
| OS-BAN-001 | — | 敏感术语禁用 | — | 敏感术语禁用 |
| OS-BAN-002 | — | 函数声明禁止 extern | — | 禁止 BUG()/BUG_ON() |
| OS-BAN-003 | 禁止 %p 默认输出 | 禁止 IDE 自动排序 include | — | — |
| OS-BAN-004 | — | 禁止五类宏 | — | 禁止 strcpy/strncpy/strlcpy |
| OS-BAN-005 | — | — | — | 禁用 %p 默认输出 |
| OS-BAN-006 | — | — | 禁止 strcpy/strncpy/strlcpy | — |
| OS-BAN-007 | — | — | 禁止 %p 默认输出 | — |

**冲突示例**：`strcpy/strncpy/strlcpy 禁令`在 4 处以 4 种不同编号出现（OS-STD-CODE-003 / OS-BAN-004 / OS-STD-CODE-010 / OS-BAN-006）。

### 4.5 同规则不同编号汇总

| 规则内容 | 出现位置数 | 出现的编号 |
|---------|-----------|-----------|
| strscpy 强制替代 strcpy/strncpy/strlcpy | 6 | OS-STD-CODE-003 / OS-BAN-004 / OS-STD-CODE-010 / OS-BAN-006 |
| Tab 8 字符缩进 | 5 | OS-KER-005 / OS-KER-011 / OS-FMT-001 / OS-STD-FMT-001（handbook） |
| 80 列行宽 | 5 | OS-KER-004 / OS-KER-012 / OS-FMT-002 / OS-STD-FMT-002（隐含） |
| K&R 大括号 | 4 | OS-STD-047+OS-KER-008 / OS-KER-013 / OS-FMT-003 |
| goto 集中出口 | 3 | OS-STD-CODE-002 / OS-KER-001 / OS-KER-009 |
| 禁止 BUG()/BUG_ON() | 3 | OS-KER-004 / OS-BAN-002 / OS-KER-015 |
| 禁止 %p 默认输出 | 3 | OS-BAN-003 / OS-BAN-005 / OS-BAN-007 |
| bool 仅返回值与栈变量 | 4 | OS-KER-002（01 双义）/ OS-KER-008 / OS-STD-011 |
| 关键字后空格 | 3 | OS-KER-010 / OS-KER-014 / OS-FMT-005 |
| 函数长度一屏可读 | 3 | OS-STD-006 / OS-KER-027 / OS-KER-015 |

### 4.6 编号格式不统一（3 段 vs 4 段）

| 文档 | 编号格式 | 示例 |
|------|---------|------|
| 00-engineering-standards-handbook.md | 4 段 | OS-STD-CODE-001、OS-STD-FMT-001、OS-STD-STY-001、OS-STD-GOV-001 |
| 01-coding-standards.md | 混用（首条 4 段，余 3 段） | OS-STD-CODE-001、OS-STD-002 |
| 02-code-format.md | 3 段 | OS-KER-005、OS-STD-047、OS-STD-202 |
| 03-code-style.md | 3 段 | OS-KER-022、OS-STD-212 |
| 04-engineering-philosophy.md | 3 段 | OS-IRON-001、OS-KER-002 |
| 05-development-process.md | 3 段 | OS-STD-101 |
| 06-toolchain-and-automation.md | 混用（首条 4 段，余 3 段） | OS-STD-CODE-004、OS-STD-002 |
| 07-maintainers-and-governance.md | 4 段（GOV 子域） | OS-STD-GOV-001 |
| 08-compliance-checklist.md | 独立前缀 | STD-DOC-01、STD-CODE-01、STD-IRON-01、STD-CI-01 |
| 60-checkpatch-rule-map.md | 4 段 | OS-STD-CODE-010 |
| 70-kernel-doc-standard.md | 4 段 | OS-STD-DOC-001 |
| 80-clang-format-enforcement.md | 3 段 | OS-KER-011 |
| 110-spdx-license-compliance.md | 4 段 | OS-STD-SPDX-001 |
| 10-coding-style/C_coding_style_standard.md | 3 段 | OS-KER-011、OS-STD-005 |
| 10-coding-style/C_coding_style_standard_supplement.md | 混用 | OS-KER-011、OS-STD-CODE-010 |
| 闭源总纲 | 3 段 + 4 段（FMT/SPDX 子域） | OS-STD-001、OS-FMT-001 |

---

## 5. 编号体系分析

### 5.1 公开 OS-* 体系现状

公开文档使用的编号前缀统计：

| 前缀 | 含义 | 文档使用情况 |
|------|------|-------------|
| OS-IRON | 工程铁律 | 00-handbook + 04-philosophy + 120-cross-project |
| OS-BAN | 禁止规则 | 00-handbook + 01-coding + 10-coding-style/C-secure |
| OS-STD | 标准规则 | 01/02/03/04/05/06/07（混用 3 段与 4 段） |
| OS-STD-CODE | 4 段编码子域 | 00-handbook + 60-checkpatch + 10-coding-style/C-supplement |
| OS-STD-FMT | 4 段格式子域 | 00-handbook（仅 2 条） |
| OS-STD-STY | 4 段风格子域 | 00-handbook（仅 2 条） |
| OS-STD-GOV | 4 段治理子域 | 00-handbook + 07-maintainers |
| OS-STD-DOC | 4 段文档子域 | 70-kernel-doc |
| OS-STD-SPDX | 4 段 SPDX 子域 | 110-spdx-license |
| OS-KER | 内核工程规则 | 01/02/03/04/10-coding-style/80-clang-format |
| OS-ACC | 验收标准 | 00-handbook |
| OS-ABI | 接口稳定性 | 00-handbook |
| OS-SEC | 安全工程规则 | 10-coding-style/Rust + 10-coding-style/C-secure |
| OS-DRV/BUILD/TEST/OBS | 子域规则 | 闭源引用，公开未集中定义 |
| STD-DOC/CODE/IRON/CI | 独立前缀 | 08-compliance-checklist |

**问题**：14 种前缀并存，3 段与 4 段格式混用，子域前缀（CODE/FMT/STY/GOV/DOC/SPDX）仅 00-handbook 与个别专题文档使用，01-07 主题文档均使用 3 段。

### 5.2 闭源 OS-IRON/OS-BAN/OS-STD/OS-KER/OS-FMT 体系

闭源总纲附录 A 给出完整注册表：

| 前缀 | 闭源数量 | 公开对应前缀 | 冲突 |
|------|---------|-------------|------|
| OS-IRON-001~014 | 14 | OS-IRON-001~010（00-handbook） | 003/005/006 三条语义不同 |
| OS-BAN-001~011 | 7（间断） | OS-BAN-001~006（公开） | 002/003/004/005 语义不同 |
| OS-STD-001~052 | 19（间断） | OS-STD-001~020（01） | 008~011/020/030/040/041/050~052 语义不同 |
| OS-KER-001~003 | 3 | OS-KER-002~050（公开分散） | 001/002/003 完全不同 |
| OS-FMT-001~007 | 7 | **公开无此前缀** | 与 OS-KER-005/004/008 等冲突 |
| OS-ACC-001 | 1 | OS-ACC-001~005（00-handbook） | 001 语义不同（公开=DCO，闭源=覆盖率） |

### 5.3 公开 vs 闭源编号体系冲突矩阵

| 维度 | 公开体系 | 闭源体系 | 是否需要统一 |
|------|---------|---------|-------------|
| IRON 铁律数量 | 10 条 | 14 条 | **是**——以闭源 14 条为准，公开补齐 4 条 |
| IRON-003/005/006 含义 | 与闭源不同 | 闭源为准 | **是**——以闭源语义为准 |
| 格式规则前缀 | OS-KER-005（Tab）/ OS-KER-004（80 列） | OS-FMT-001/002 | **是**——统一为 OS-FMT-* |
| 内核工程前缀 | OS-KER-002~050 | OS-KER-001~003 | **是**——OS-KER 仅保留内核态专属规则（goto/IS_ENABLED/条件编译等） |
| OS-STD 子域前缀 | 4 段（CODE/FMT/STY/GOV/DOC/SPDX） | 3 段 + 4 段 FMT/SPDX | **是**——统一为 4 段 |
| OS-ACC 编号 | 5 条（DCO/7 层验证/补丁中点/regression 72h/状态字段） | 1 条（覆盖率） | **是**——以闭源覆盖率扩展，合并公开 5 条 |
| 检查规则前缀 | STD-DOC/CODE/IRON/CI（08 卷自创） | OS-STD-050~052 | **是**——08 卷应改为 OS-STD-CHECK-NNN |
| OS-DRV/BUILD/TEST/OBS/SEC/ABI | 公开仅 OS-SEC + OS-ABI（少量） | 闭源引用未定义 | **是**——公开应补齐注册 |

### 5.4 编号体系统一建议

**建议方案 A（推荐）：闭源总纲为权威，公开对齐**

- 闭源总纲附录 A 为 SSoT，公开 00-handbook §3 改为闭源附录 A 的镜像
- 公开补齐 OS-IRON-011~014 / OS-FMT-001~007 / OS-DRV/BUILD/TEST/OBS/SEC/ABI 完整定义
- 公开 OS-KER 仅保留内核态专属规则（goto/IS_ENABLED/条件编译），格式规则迁移至 OS-FMT-*

**建议方案 B（不推荐）：公开为权威，闭源对齐**

- 工作量大，闭源总纲已包含更完整体系（OS-FMT 7 条、OS-IRON 14 条）

**本报告采纳方案 A**。

---

## 6. 合并方案

### 6.1 决策矩阵

| 决策编号 | 涉及文件 | 决策类型 | 决策内容 | 理由 | 优先级 |
|---------|---------|---------|---------|------|--------|
| D-01 | 00-handbook + 04-philosophy + 闭源总纲 | 重新对齐 | IRON-001~014 以闭源总纲附录 A 为 SSoT；04-philosophy 重写 §2-§7 使其 OS-IRON 编号与闭源一致；00-handbook §2 同步更新 | 闭源总纲体系更完整（14 条 vs 10 条），且附录 A 已建立完整注册表 | P0 |
| D-02 | 02-code-format + 80-clang-format-enforcement | 合并 | 80-clang-format 的"配置项详解"合并至 02-code-format §9（已有该表）；80-clang-format 仅保留 OLK-6.6 源码行号索引 + CI 门禁脚本流程；02 为格式规则 SSoT，80 为工具配置 SSoT | 80 §0.1 已声明交叉引用，实际重叠 70%+；合并后职责清晰 | P0 |
| D-03 | 02-code-format + 10-coding-style/C_coding_style_standard.md + C_coding_style_standard_supplement.md | 删除 + 合并 | 删除 10-coding-style/C_coding_style_standard.md 与 C_coding_style_standard_supplement.md，其内容已 100% 被 01+02+03 覆盖；10-coding-style/ 仅保留 README + 安全编码两份（C_Cpp_secure + Rust_secure） | 10-coding-style/C* 与 02 严重重叠（>80%）且编号完全冲突；保留只会加剧混乱 | P0 |
| D-04 | 02-code-format + 闭源总纲 §3 | 编号迁移 | 格式规则统一使用 OS-FMT-001~007（闭源前缀）；02 中 OS-KER-005（Tab）迁移为 OS-FMT-001，OS-KER-004（80 列）迁移为 OS-FMT-002，OS-KER-008（函数开括号）迁移为 OS-FMT-003，等等；02 §0.1 关键术语保留 | OS-FMT 是闭源已确立的格式子域前缀，且语义更准确（FMT = Format） | P0 |
| D-05 | 01-coding-standards + 闭源总纲 §2 | 编号迁移 | 编码规则统一使用 OS-STD-CODE-NNN（4 段）；01 中 OS-STD-001~020 全部迁移为 OS-STD-CODE-001~020；首条 OS-STD-CODE-001 与后续 OS-STD-002 不一致问题修复 | 4 段编号带子域语义，便于跨文档检索；00-handbook 已使用此格式 | P0 |
| D-06 | 05-development-process + 06-toolchain-and-automation | 编号段重新分配 | 05 使用 OS-STD-PROD-NNN（4 段，PROD = Process/Development）；06 使用 OS-STD-TOOL-NNN（4 段，TOOL = Toolchain）；OS-STD-101~158 段冲突消除 | 05/06 共用 OS-STD-101~158 段导致 30+ 条语义冲突；4 段子域前缀彻底隔离 | P0 |
| D-07 | 08-compliance-checklist | 前缀统一 | STD-DOC/CODE/IRON/CI 改为 OS-STD-CHECK-DOC-NNN / OS-STD-CHECK-CODE-NNN / OS-STD-CHECK-IRON-NNN / OS-STD-CHECK-CI-NNN；或简化为 OS-CHECK-DOC-NNN 等 | 08 自创独立前缀与全项目 OS-* 体系并行；改为 OS-* 子域统一 | P1 |
| D-08 | 09-license-strategy | 物理移除 | README + 00-handbook 标注"已废弃，参见 110"链接；保留物理文件但加 `DEPRECATED` 标记头部 | 09 §0 已声明废弃，仅需完成引用清理 | P2 |
| D-09 | 60-checkpatch-rule-map + 70-kernel-doc + 110-spdx | 子域前缀统一 | 三份专题文档已使用 4 段编号（OS-STD-CODE/DOC/SPDX）；保留现状，仅校验其编号不与 01-07 主题卷冲突 | 已是良好实践，仅需集中校验 | P2 |

### 6.2 决策详细理由

#### D-01：IRON 铁律对齐

闭源总纲附录 A 的 14 条 IRON 铁律已包含：

```
OS-IRON-001  用户空间 ABI 永不破坏
OS-IRON-002  内核内部 API 不保证稳定
OS-IRON-003  策略与机制分离
OS-IRON-004  渐进式开发，补丁自包含
OS-IRON-005  审查优先文化
OS-IRON-006  不破坏用户空间原则
OS-IRON-007  DCO 强制
OS-IRON-008  共享契约层 6 个头文件双向 CI 验证
OS-IRON-009  代码共享边界：仅 agentrt ↔ AirymaxOS
OS-IRON-010  "Linux 6.6 为基、seL4 为鉴"工程取向
OS-IRON-011  双源边界声明（技术参考非代码共享）
OS-IRON-012  seL4 借鉴仅限架构层（ES-SEL4-1~5）
OS-IRON-013  8 子仓独立 git 仓库 + submodule 管理
OS-IRON-014  [SC] 共享契约层 6 头文件单一数据源（禁止物理副本）
```

而公开 00-handbook 仅 10 条，且 003/005/006 与闭源语义不同。**对齐策略**：

1. 公开 00-handbook §2.1 直接引用闭源附录 A 的 14 条
2. 04-engineering-philosophy §2-§7 重写，所有 IRON 引用改为闭源语义
3. 公开 README §1.2 "三大支柱"中"17 类规则编号体系"统一为闭源 11 类前缀

#### D-02：02 + 80 合并

80-clang-format-enforcement.md 的实际价值仅在两点：

1. **OLK-6.6 源码行号索引**（如 `.clang-format:645` → `IndentWidth: 8`）
2. **CI 门禁脚本流程**（`make format-check` 流水线）

其余 §1（关键配置项详解）与 02 §9（clang-format 关键配置项表）100% 重叠。**合并策略**：

- 02 §9 扩展为"clang-format 配置项表 + OLK-6.6 源码行号"二合一表格
- 80 仅保留 §0（文档说明）+ §5（CI 门禁流程）+ §6（与 checkpatch 协作流水线）
- 80 §1-§4 全部删除（已合并入 02）

#### D-03：删除 10-coding-style/C*

`10-coding-style/C_coding_style_standard.md` 与 `C_coding_style_standard_supplement.md` 的实际内容：

- C_coding_style_standard.md §2.1-§2.4（缩进/行宽/大括号/空格）= 02 §1-§4 完全覆盖
- C_coding_style_standard.md §3-§9（命名/函数/注释/头文件/错误处理/内存/锁）= 01 §1-§9 完全覆盖
- C_coding_style_standard_supplement.md §1-§12 = 02 + 01 的部分规则加上 OLK-6.6 行号索引

两份文档的存在**只增加编号冲突，不增加规则覆盖**。**合并策略**：

- 删除两份文档（共 50KB）
- 10-coding-style/README.md 更新，仅保留 C_Cpp_secure_coding_standard.md + Rust_coding_style_standard.md + Rust_secure_coding_standard.md 三份
- 02 §0.1 关键术语表新增"OLK-6.6 源码行号"列（吸收 supplement 的核心价值）

#### D-04：格式规则迁移 OS-FMT

迁移映射表：

| 当前编号（02） | 新编号 | 规则 |
|---------------|--------|------|
| OS-KER-005（Tab 8 字符） | OS-FMT-001 | Tab 缩进，8 字符宽 |
| OS-KER-004（80 列） | OS-FMT-002 | C 代码首选 80 列 |
| OS-KER-005（字符串禁止断行） | OS-FMT-008 | 用户可见字符串禁止断行（消除 02 内部双义） |
| OS-STD-047 + OS-KER-008（大括号） | OS-FMT-003 + OS-FMT-009 | K&R 大括号 + 函数开括号独占一行 |
| OS-KER-009（单语句大括号） | OS-FMT-004 | 单语句与多语句大括号规则 |
| OS-KER-010~014（空格） | OS-FMT-005 | 空格规则（合并 5 条为 1 条） |
| OS-KER-012（指针声明 `*` 贴名字） | OS-FMT-006 | 指针对齐 |
| OS-KER-015~019（switch/空行/多语句） | OS-FMT-010~014 | 其他格式规则 |

迁移后 OS-KER 仅保留内核态专属规则（goto/IS_ENABLED/条件编译/bool/types）。

#### D-05：编码规则迁移 OS-STD-CODE

迁移映射表（部分示例）：

| 当前编号（01） | 新编号 | 规则 |
|---------------|--------|------|
| OS-STD-CODE-001（首条 4 段） | OS-STD-CODE-001 | 全局符号描述性命名（保留） |
| OS-STD-002 | OS-STD-CODE-002 | 局部变量短小切题 |
| OS-STD-003 | OS-STD-CODE-003 | 宏与枚举命名 |
| OS-STD-004 | OS-STD-CODE-004 | 函数返回值约定 |
| OS-STD-005 | OS-STD-CODE-005 | agent-linux 专属前缀 |
| OS-STD-006 | OS-STD-CODE-006 | 函数长度 |
| OS-STD-007 | OS-STD-CODE-007 | 函数原型元素顺序 |
| OS-STD-008 | OS-STD-CODE-008 | 原型必须含参数名 |
| OS-STD-009 | OS-STD-CODE-009 | EXPORT_SYMBOL 紧跟 |
| OS-STD-010 | OS-STD-CODE-010 | 注释说明 WHAT 与 WHY |
| ... | ... | ... |
| OS-STD-020 | OS-STD-CODE-020 | typedef 严格限制 |

迁移后 01 全部使用 4 段编号，与 60-checkpatch-rule-map.md（已使用 OS-STD-CODE-NNN）对齐。

#### D-06：05/06 编号段隔离

**重新分配**：

- 05-development-process 使用 `OS-STD-PROD-NNN`（PROD = Process/Development）
- 06-toolchain-and-automation 使用 `OS-STD-TOOL-NNN`（TOOL = Toolchain）

**示例迁移**：

| 当前编号 | 新编号 | 文档 | 规则 |
|---------|--------|------|------|
| OS-STD-101（05） | OS-STD-PROD-101 | 05 | L1/L2 接口设计需 RFC |
| OS-STD-101（06） | OS-STD-TOOL-101 | 06 | checkpatch --strict 无 ERROR |
| OS-STD-131（05） | OS-STD-PROD-131 | 05 | develop nightly build |
| OS-STD-131（06） | OS-STD-TOOL-131 | 06 | 子仓维护 ci/nightly/release |

迁移后 05/06 共用 OS-STD-101~158 段冲突消除。

#### D-07：08-compliance-checklist 前缀统一

**迁移方案**：

| 当前前缀 | 新前缀 | 示例 |
|---------|--------|------|
| STD-DOC-01~08 | OS-STD-CHECK-DOC-01~08 | OS-STD-CHECK-DOC-01（Copyright 检查） |
| STD-CODE-01~05 | OS-STD-CHECK-CODE-01~05 | OS-STD-CHECK-CODE-01（SPDX 检查） |
| STD-IRON-01~04 | OS-STD-CHECK-IRON-01~04 | OS-STD-CHECK-IRON-01（[SC] 一致性） |
| STD-CI-01 | OS-STD-CHECK-CI-01 | CI/CD 流水线集成 |

迁移后 08 完全融入 OS-* 体系。

### 6.3 缺失标准识别

审查发现以下标准缺失，需新建：

| 缺失项 | 缺失原因 | 建议位置 | 优先级 |
|--------|---------|---------|--------|
| OS-DRV-001~NNN 驱动工程规则 | 闭源总纲引用但未定义 | 新建 90-driver-engineering.md 或合并入 04-philosophy §K-3 | P1 |
| OS-BUILD-001~NNN 构建工程规则 | 闭源总纲引用但未定义 | 新建 75-build-engineering.md 或合并入 06-toolchain | P1 |
| OS-TEST-001~NNN 测试工程规则 | 闭源总纲引用但未定义 | 新建 85-test-engineering.md 或合并入 06-toolchain §6 | P1 |
| OS-OBS-001~NNN 可观测性规则 | 闭源总纲引用但未定义 | 新建 95-observability-rules.md | P2 |
| OS-SEC-001~NNN 安全工程规则 | 公开仅 10-coding-style/secure 部分覆盖 | 合并 10-coding-style/Rust_secure + C_Cpp_secure 至 65-security-engineering.md | P1 |
| 公开 IRON-011~014 | 闭源已定义但公开未补齐 | 00-handbook §2.1 补齐 4 条 | P0 |
| 8 子仓差异化标准矩阵 | 闭源 §1.4 已有，公开未镜像 | 00-handbook 新增 §2.2 子仓差异化 | P1 |
| 微核心 vs 微内核术语规范 | 00-handbook §7 已有但未强制 | 00-handbook §7 升级为 OS-STD-TERM-001 | P2 |

---

## 7. OLK-6.6 对标分析

### 7.1 OLK-6.6 coding-style.rst 核心规则

OLK-6.6 `Documentation/process/coding-style.rst` 是 Linux 6.6 内核编码风格权威来源，共 19 章。其核心规则如下：

| 章节 | 主题 | agent-linux 对应规则 |
|------|------|----------------------|
| 1 | Indentation（Tab 8 字符） | OS-KER-005 / OS-KER-011 / OS-FMT-001（**3 编号冲突**） |
| 2 | Breaking long lines and strings | OS-KER-005（字符串）/ OS-KER-006（后继行） |
| 3 | Placing Braces and Spaces | OS-STD-047 / OS-KER-008~014 |
| 4 | Naming | OS-STD-001 / OS-STD-005 |
| 5 | Typedef | OS-STD-020 / OS-KER-002 |
| 6 | Functions | OS-STD-006~009 |
| 7 | Centralized exiting of functions | OS-STD-CODE-002 / OS-KER-001 / OS-KER-009（**3 编号冲突**） |
| 8 | Commenting | OS-STD-010~014 |
| 9 | Macros, Enums and RTL | OS-STD-003 / OS-STD-018~019 / OS-BAN-004 |
| 10 | The inline disease | OS-STD-019 |
| 11 | Function return values and names | OS-STD-004 |
| 12 | Kernel messages | OS-KER-005（字符串禁止断行） |
| 13 | Printing kernel messages | （分散） |
| 14 | Conditional Compilation | OS-KER-003 / OS-KER-030（**2 编号冲突**） |
| 15 | Idiomatic C | （分散） |
| 16 | Rationale | （背景） |
| 17 | References | （背景） |
| 18 | Breaking long lines and strings | （同 §2） |
| 19 | I/O | （未覆盖） |

### 7.2 OLK-6.6 与 agent-linux 差距

| 差距项 | OLK-6.6 现状 | agent-linux 现状 | 建议修复 |
|--------|------------|-------------------|---------|
| 编号一致性 | OLK-6.6 无编号（章节即规则） | 同一规则 3-4 个编号 | 统一为 OS-FMT / OS-STD-CODE 4 段 |
| 字符串拷贝 | strscpy 强制（kernel 内已强制） | 4 个不同编号 | 统一为 OS-STD-CODE-010 |
| goto 集中出口 | 第 7 章明确 | 3 个不同编号 | 统一为 OS-KER-001 |
| bool 边界 | 第 5 章明确 | 4 个不同编号 | 统一为 OS-STD-CODE-011 |
| typedef 5 种例外 | 第 5 章明确 | OS-STD-020（01）+ OS-STD-010（闭源）冲突 | 统一为 OS-STD-CODE-020 |
| 条件编译 IS_ENABLED | 第 14 章明确 | OS-KER-003（02 行尾）/ OS-KER-030（03 IS_ENABLED）冲突 | 统一为 OS-KER-003 = IS_ENABLED |
| 单语句大括号 | 第 3 章明确"任一分支多语句则两分支都加" | 02 OS-KER-009 与闭源 OS-FMT-004 冲突（02 不要求单语句加，闭源要求加） | **采纳 OLK-6.6 立场**：单语句可不加（02 正确） |
| 行宽 80 列 | 第 2 章明确 | OS-KER-004 / OS-KER-012 / OS-FMT-002 冲突 | 统一为 OS-FMT-002 |
| 后继行短于父行 | 第 2 章明确 | OS-KER-006（02） | 保留 |

### 7.3 单语句大括号规则冲突解决

**OLK-6.6 §3 原文**：

```c
Don't put multiple statements on a single line unless you have
something to hide:

.. code-block:: c

        if (condition) do_this;
          do_something_everytime;

Don't use commas to avoid using braces:

.. code-block:: c

        if (condition)
                do_this(), do_that();

Always uses braces for multiple statements:

.. code-block:: c

        if (condition) {
                do_this();
                do_that();
        }
```

OLK-6.6 立场：**单语句可不加大括号，但多语句必须加**。

- 02-code-format.md OS-KER-009：单语句不需要大括号；任一分支多语句则两分支都加 —— **与 OLK-6.6 一致**
- 闭源总纲 OS-FMT-004：即使单条语句也使用大括号 —— **与 OLK-6.6 不一致**

**决策**：采纳 OLK-6.6 立场，删除闭源 OS-FMT-004，统一为 02 的 OS-KER-009（迁移后为 OS-FMT-004）。

### 7.4 OLK-6.6 §19 I/O 缺失

OLK-6.6 §19 涉及 I/O 操作规范（`ioremap` / `readl` / `writel` 等），agent-linux 当前未覆盖。**建议**：在 03-code-style.md 新增 §10 I/O 风格规范，或新建 90-driver-engineering.md。

---

## 8. 执行计划

### 8.1 优先级排序

| 阶段 | 优先级 | 决策 | 工作量估计 | 责任 |
|------|--------|------|-----------|------|
| **阶段 1：编号体系对齐** | P0 | D-01、D-04、D-05、D-06 | 2 周 | 架构委员会 + 工程标准组 |
| **阶段 2：重复文件合并** | P0 | D-02、D-03 | 1 周 | 工程标准组 |
| **阶段 3：检查规则前缀统一** | P1 | D-07、缺失项补齐（OS-DRV/BUILD/TEST/SEC） | 2 周 | 工程标准组 + 安全组 |
| **阶段 4：废弃文件清理** | P2 | D-08、D-09、缺失项补齐（OS-OBS/TERM） | 1 周 | 工程标准组 |

### 8.2 阶段 1 详细任务（P0，2 周）

**第 1 周：编号体系对齐设计**

1. 闭源总纲附录 A 升级为唯一 SSoT 注册表（确认 OS-IRON-001~014 / OS-FMT-001~007 / OS-KER-001~003）
2. 公开 00-handbook §3 重写，对齐闭源附录 A（含 14 条 IRON + 7 条 FMT + 3 条 KER）
3. 04-engineering-philosophy §2-§7 重写，所有 IRON 引用对齐闭源语义
4. 设计 OS-STD-CODE / OS-STD-PROD / OS-STD-TOOL / OS-STD-GOV / OS-STD-CHECK 完整 4 段编号空间分配表

**第 2 周：编号迁移执行**

5. 01-coding-standards.md OS-STD-001~020 → OS-STD-CODE-001~020（全局替换）
6. 02-code-format.md OS-KER-005/004/008/009/010~019 → OS-FMT-001~014
7. 03-code-style.md OS-KER-022~032 → 重新分配至 OS-KER-101~111（避开 02 段）
8. 05-development-process.md OS-STD-101~234 → OS-STD-PROD-101~234
9. 06-toolchain-and-automation.md OS-STD-002~158 → OS-STD-TOOL-001~158
10. 07-maintainers-and-governance.md OS-STD-GOV-001~007 保留

### 8.3 阶段 2 详细任务（P0，1 周）

1. 80-clang-format-enforcement.md §1-§4 内容合并至 02-code-format.md §9（扩展为含 OLK-6.6 行号的二合一表）
2. 80-clang-format-enforcement.md 仅保留 §0 + §5 + §6
3. 删除 10-coding-style/C_coding_style_standard.md（27KB）
4. 删除 10-coding-style/C_coding_style_standard_supplement.md（23KB）
5. 10-coding-style/README.md 更新，移除 C_coding_style 与 supplement 引用
6. 02-code-format.md §0.1 关键术语表新增"OLK-6.6 源码行号"列

### 8.4 阶段 3 详细任务（P1，2 周）

1. 08-compliance-checklist.md STD-DOC/CODE/IRON/CI → OS-STD-CHECK-DOC/CODE/IRON/CI
2. 新建 90-driver-engineering.md（OS-DRV-001~NNN）或合并入 03-code-style §K-3
3. 新建 75-build-engineering.md（OS-BUILD-001~NNN）或合并入 06-toolchain §643+
4. 新建 85-test-engineering.md（OS-TEST-001~NNN）或合并入 06-toolchain §6
5. 合并 10-coding-style/Rust_secure + C_Cpp_secure 至 65-security-engineering.md（OS-SEC-001~NNN）

### 8.5 阶段 4 详细任务（P2，1 周）

1. 09-license-strategy.md 物理文件加 `DEPRECATED` 标记，README + 00-handbook 标注"已废弃"
2. 新建 95-observability-rules.md（OS-OBS-001~NNN）
3. 00-handbook §7 微核心 vs 微内核术语规范升级为 OS-STD-TERM-001
4. 00-handbook §2.2 新增 8 子仓差异化矩阵（镜像闭源 §1.4）
5. 00-handbook §2.1 补齐 OS-IRON-011~014（4 条新增）

### 8.6 验证机制

每阶段完成后，运行以下验证脚本（建议落地为 `scripts/check-rule-numbering.sh`）：

```bash
#!/bin/bash
# check-rule-numbering.sh
# 验证所有规则编号在所有文档中语义一致

# 1. 提取所有 OS-* 编号及其上下文
grep -rnE '\*\*OS-[A-Z]+(-[A-Z]+)*-[0-9]+\*\*' \
    docs/AirymaxOS/50-engineering-standards/ \
    docs-closed/agent-linux/agent-linux基本工程标准规范.md \
    > /tmp/all-rules.txt

# 2. 检查同编号双义
awk -F: '{print $3}' /tmp/all-rules.txt | sort | uniq -d
# 期望输出：空（无重复编号）

# 3. 检查同规则不同编号
# （需要语义对齐表，手动审核）

# 4. 检查 IRON 铁律 14 条完整性
IRON_COUNT=$(grep -cE 'OS-IRON-0[01][0-9]' \
    docs-closed/agent-linux/agent-linux基本工程标准规范.md)
if [ "$IRON_COUNT" -lt 14 ]; then
    echo "ERROR: IRON 铁律不足 14 条（当前 $IRON_COUNT）"
    exit 1
fi
```

### 8.7 时间线

| 阶段 | 起止时间 | 里程碑 |
|------|---------|--------|
| 阶段 1 | 2026-07-10 ~ 2026-07-23 | 编号体系对齐完成，所有 P0 编号冲突消除 |
| 阶段 2 | 2026-07-24 ~ 2026-07-30 | 重复文件合并完成，10-coding-style/C* 删除 |
| 阶段 3 | 2026-07-31 ~ 2026-08-13 | 检查规则前缀统一，缺失标准补齐（OS-DRV/BUILD/TEST/SEC） |
| 阶段 4 | 2026-08-14 ~ 2026-08-20 | 废弃清理完成，OS-OBS/TERM 补齐 |

---

## 9. 相关文档

### 9.1 直接相关

| 文档 | 路径 | 关系 |
|------|------|------|
| 公开工程标准 README | `docs/AirymaxOS/50-engineering-standards/README.md` | 主索引 |
| 公开 SSoT 手册 | `docs/AirymaxOS/50-engineering-standards/00-engineering-standards-handbook.md` | SSoT 索引（需重写） |
| 闭源工程标准总纲 | `docs-closed/agent-linux/agent-linux基本工程标准规范.md` | 闭源 SSoT（附录 A 为权威） |
| OLK-6.6 编码风格 | `01Reference/kernel-OLK-6.6/Documentation/process/coding-style.rst` | 参考基线 |
| 经验总结报告 | `docs-closed/agent-linux/_analysis_0.3.0/01-lessons-learned.md` | 同期分析报告 |

### 9.2 编号体系参考

| 文档 | 路径 | 用途 |
|------|------|------|
| OLK-6.6 .clang-format | `01Reference/kernel-OLK-6.6/.clang-format`（689 行） | 格式规则源 |
| OLK-6.6 checkpatch.pl | `01Reference/kernel-OLK-6.6/scripts/checkpatch.pl` | 规则映射源 |
| OLK-6.6 kernel-doc | `01Reference/kernel-OLK-6.6/scripts/kernel-doc` | 注释规范源 |

### 9.3 重复对涉及文件清单

| 重复对 | 涉及文件 |
|--------|---------|
| R-1 | `01-coding-standards.md` + `02-code-format.md` |
| R-2 | `02-code-format.md` + `80-clang-format-enforcement.md` |
| R-3 | `02-code-format.md` + `10-coding-style/C_coding_style_standard.md` |
| R-4 | `10-coding-style/C_coding_style_standard.md` + `C_coding_style_standard_supplement.md` |
| R-5 | `04-engineering-philosophy.md` + `00-engineering-standards-handbook.md` |
| R-6 | `04-engineering-philosophy.md` + 闭源总纲 |
| R-7 | `05-development-process.md` + `06-toolchain-and-automation.md` |
| R-8 | `09-license-strategy.md` + `110-spdx-license-compliance.md` |
| R-9 | `08-compliance-checklist.md` + 闭源总纲 §8 |
| R-10~R-14 | 跨 4-6 份文档的同一规则多编号 |

---

## 附录 A：合并决策速查表

| 决策 | 涉及文件 | 类型 | 优先级 |
|------|---------|------|--------|
| D-01 | 00-handbook + 04-philosophy + 闭源 | 重新对齐 IRON | P0 |
| D-02 | 02 + 80 | 合并（80 保留 CI 部分） | P0 |
| D-03 | 10-coding-style/C* | 删除 2 份 | P0 |
| D-04 | 02 + 闭源 §3 | 编号迁移 OS-FMT | P0 |
| D-05 | 01 + 闭源 §2 | 编号迁移 OS-STD-CODE | P0 |
| D-06 | 05 + 06 | 编号段隔离 PROD/TOOL | P0 |
| D-07 | 08 | 前缀统一 OS-STD-CHECK | P1 |
| D-08 | 09 | 物理移除标记 | P2 |
| D-09 | 60 + 70 + 110 | 子域前缀校验 | P2 |

## 附录 B：编号体系目标状态

合并完成后的目标编号体系：

| 前缀 | 含义 | 数量 | 文档分布 |
|------|------|------|---------|
| OS-IRON-001~014 | 工程铁律 | 14 | 闭源附录 A + 公开 00-handbook §2.1 |
| OS-BAN-001~011 | 禁止规则 | 7（间断） | 闭源 §2.2.4 + 公开 01 §OS-BAN |
| OS-STD-CODE-001~020 | 编码标准 | 20 | 01-coding-standards |
| OS-STD-FMT-001~014 | 格式标准 | 14 | 02-code-format（迁移自 OS-KER-005~019） |
| OS-STD-STY-001~NNN | 风格标准 | 待定 | 03-code-style |
| OS-STD-PROD-101~234 | 流程标准 | 50+ | 05-development-process |
| OS-STD-TOOL-001~158 | 工具标准 | 50+ | 06-toolchain-and-automation |
| OS-STD-GOV-001~007 | 治理标准 | 7 | 07-maintainers-and-governance |
| OS-STD-CHECK-DOC/CODE/IRON/CI | 检查标准 | 17 | 08-compliance-checklist |
| OS-STD-CODE-001~999 | checkpatch 映射 | 30+ | 60-checkpatch-rule-map |
| OS-STD-DOC-001~NNN | kernel-doc | 待定 | 70-kernel-doc-standard |
| OS-STD-SPDX-001~003 | SPDX 合规 | 3 | 110-spdx-license-compliance |
| OS-KER-001~003 + 101~111 | 内核工程（仅内核态专属） | 3 + 11 | 01 + 03（迁移后） |
| OS-ACC-001~NNN | 验收标准 | 待扩展 | 00-handbook §3.6 |
| OS-ABI-001 | 接口稳定性 | 1 | 00-handbook §3.5 |
| OS-DRV-001~NNN | 驱动工程 | 待新建 | 90-driver-engineering（新建） |
| OS-BUILD-001~NNN | 构建工程 | 待新建 | 75-build-engineering（新建） |
| OS-TEST-001~NNN | 测试工程 | 待新建 | 85-test-engineering（新建） |
| OS-OBS-001~NNN | 可观测性 | 待新建 | 95-observability-rules（新建） |
| OS-SEC-001~020 | 安全工程 | 20 | 65-security-engineering（合并自 10-coding-style/*_secure） |

## 附录 C：关键术语

| 术语 | 定义 |
|------|------|
| SSoT | Single Source of Truth，单一事实源 |
| IRON-9 v2 | agentrt 与 agent-linux 的同源且部分代码共享模型 |
| [SC] | Shared-Contract，共享契约层 |
| [SS] | Shared-Semantics，语义同源层 |
| [IND] | Independent，完全独立层 |
| OLK-6.6 | OpenLinux Kernel 6.6，agent-linux 内核基线 |
| 双层稳定性 | 用户空间 ABI 永久稳定 + 内核内部 API 可变 |
| 策略机制分离 | 机制留内核，策略外移至用户空间或可插拔模块 |

---

> **文档结束** | SPHARX Ltd 内部参考 | 闭源不公开
> **报告版本**: v0.3.0
> **下次审查触发条件**: 阶段 1 完成后（2026-07-23）启动验证审查
