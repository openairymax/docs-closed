Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# C-2.6 工程标准合并决策执行完成报告

> **报告编号**: C-2.6-EXEC（D-01~D-09 执行完成报告）
> **报告日期**: 2026-07-09
> **报告版本**: v0.3.0（系统性分析与决策阶段）
> **执行范围**: `docs/AirymaxOS/50-engineering-standards/` 下 10 个文件的 SSoT 对齐修复
> **机密级别**: 闭源不公开（SPHARX Ltd 内部参考）
> **核心结论**: 9 项合并决策（D-01~D-09）全部执行完毕，采用**非破坏性 SSoT 对齐模式**——不删除文件、不破坏交叉引用，通过添加 SSoT 声明头 + §0 编号映射表消除编号歧义。

---

## 1. 执行概述

### 1.1 执行方法：非破坏性 SSoT 对齐模式

本次执行采用统一的**非破坏性 SSoT 对齐模式**，该方法论的核心原则：

1. **不删除文件**：即使文件内容与 SSoT 重叠，也保留物理文件（避免破坏 21+ 处交叉引用）
2. **不大幅度删改**：遵循用户约束"设计文档很重要，不能随意大幅度删改"
3. **添加 SSoT 声明头**：在文档头部 blockquote 声明权威来源（SSoT）与本文档的从属关系
4. **添加 §0 编号映射表**：在文档正文前插入编号对齐映射表，消除编号歧义
5. **保留独特内容**：识别并保留每份文档的独特价值（如 OLK-6.6 源码行号、CI 门禁流程、完整 YAML 配置等）

### 1.2 执行统计

| 决策 | 优先级 | 涉及文件数 | 执行状态 | 执行方式 |
|------|--------|-----------|---------|---------|
| D-01 | P0 | 1 | ✅ 完成 | SSoT 声明 + §0 IRON 编号对齐映射表 |
| D-02 | P0 | 1 | ✅ 完成 | SSoT 声明 + §6 速查表交叉引用注 |
| D-03 | P0 | 2 | ✅ 完成 | SSoT 声明 + §0 编号映射表（2 文件） |
| D-04 | P0 | 1 | ✅ 完成 | SSoT 声明 + §0.2 OS-KER→OS-FMT 迁移映射表 |
| D-05 | P0 | 1 | ✅ 完成 | SSoT 声明 + §0.1 OS-STD→OS-STD-CODE 迁移映射表 |
| D-06 | P0 | 2 | ✅ 完成 | SSoT 声明 + §0.2 编号段隔离对照表（2 文件） |
| D-07 | P1 | 1 | ✅ 完成 | SSoT 声明 + §0 前缀迁移映射表 |
| D-08 | P2 | 0 | ✅ 已确认 | 先前会话已执行（废弃标记） |
| D-09 | P2 | 1 | ✅ 完成 | D-09 子域校验声明（60） |
| **合计** | | **10** | **9/9** | |

---

## 2. 逐项执行详情

### 2.1 D-01：IRON 铁律编号对齐

- **文件**: `04-engineering-philosophy.md`
- **问题**: OS-IRON-003~006 标签与闭源 SSoT（附录 A 14 条铁律）存在 2-3 位语义偏移
- **执行**:
  - 头部添加 SSoT 声明行（指向闭源附录 A 14 条铁律为 SSoT）
  - 新增 §0 章节"IRON 铁律编号 SSoT 对齐映射表"
    - §0.1 编号对齐映射表（9 行：SSoT IRON-001~014 → 本文档章节 → 历史标签 → 对齐状态）
    - §0.2 历史标签处置表（4 行：§5 IRON-003 降级、§6 IRON-004 补标为 005、§9 IRON-005 补标为 006、§10 IRON-006 降级）
    - §0.3 完整 IRON 铁律索引说明
  - 目录新增 §0 条目

### 2.2 D-02：02 + 80 合并

- **文件**: `80-clang-format-enforcement.md`
- **问题**: §1（关键配置项详解）与 02-code-format.md §9 100% 重叠
- **执行**:
  - 头部添加 SSoT 声明行（02 §1-§8 为格式规则 SSoT，§9 为配置项速查表 SSoT）
  - 明确 §1/§2/§6 为"补充详述"（附 OLK-6.6 源码行号 + 详细理由 + 完整 YAML）
  - 明确 §3/§4/§5 为"独立权威内容"（CI 门禁、troubleshooting、checkpatch 协作）
  - §6 速查表头部添加 SSoT 注（编号冲突时以 02 为准，本表编号仅作历史导航）

### 2.3 D-03：10-coding-style/C* SSoT 对齐

- **文件**: `C_coding_style_standard.md` + `C_coding_style_standard_supplement.md`
- **问题**: §2 格式规则使用 OS-KER-011~014 与 02 冲突；§3-§6 语义规则与 01 重叠
- **C-2.6 原始判断修正**: 报告声称"100% 被 01+02+03 覆盖"，实际审查发现 §7-§10（goto/GFP/锁/RCU/[SC][SS]）为内核态专属权威内容，不在 01/02/03 中
- **执行**:
  - `C_coding_style_standard.md` 头部添加 SSoT 声明 + §0 映射表
    - §0.1 格式规则映射表（OS-KER-011~014 → 02 OS-KER-005/004/008/010~014）
    - §0.2 语义规则映射表（OS-STD-005/028/029/004/006~017 → 01 对应位置）
    - §0.3 本文件保留的权威内容表（§7 goto/§8 GFP/§9 锁/§10 [SC][SS] 为内核态专属）
  - `C_coding_style_standard_supplement.md` 头部添加 SSoT 声明（OLK-6.6 行号索引为独特价值）

### 2.4 D-04：格式规则迁移 OS-FMT

- **文件**: `02-code-format.md`
- **问题**: OS-KER-005 双义（Tab 8 字符 vs 字符串禁止断行）、K&R 大括号双编号、空格规则 5 拆 1
- **执行**:
  - 头部添加 SSoT 声明行（OS-FMT-NNN 为目标前缀，历史编号并存等价）
  - 新增 §0.2 "OS-KER → OS-FMT 编号迁移映射"
    - §0.2.1 格式规则迁移映射表（17 行映射，含迁移说明）
    - §0.2.2 迁移状态（编号并存阶段，1.0.1 触发统一替换）
    - §0.2.3 迁移后保留的内核态专属 OS-KER 编号（goto/typedef/float/IS_ENABLED/bug 修复）
  - 采纳 OLK-6.6 §3 立场（单语句可不加大括号），弃闭源 OS-FMT-004

### 2.5 D-05：编码规则迁移 OS-STD-CODE

- **文件**: `01-coding-standards.md`
- **问题**: 首条 OS-STD-CODE-001（4 段）与后续 OS-STD-002~027（3 段）不一致
- **执行**:
  - 头部添加 SSoT 声明行（OS-STD-CODE-NNN 为目标前缀，历史编号并存等价）
  - 新增 §0.1 "OS-STD → OS-STD-CODE 编号迁移映射"
    - §0.1.1 编码规则迁移映射表（27 行映射，OS-STD-001~027 → OS-STD-CODE-001~027）
    - §0.1.2 迁移状态（编号并存阶段，1.0.1 触发统一替换）
  - 闭源冲突消解说明：闭源 §2.5 OS-STD-011（bool 边界）与本卷 OS-STD-011（通用风格）冲突，最终裁决以本卷为准

### 2.6 D-06：05/06 编号段隔离 PROD/TOOL

- **文件**: `05-development-process.md` + `06-toolchain-and-automation.md`
- **问题**: 两卷共用 OS-STD-101~158 段导致 30+ 项语义冲突（如 OS-STD-101 在 05 = "RFC"、在 06 = "checkpatch"）
- **执行**:
  - `05-development-process.md` 头部添加 SSoT 声明（OS-STD-PROD-NNN 为目标前缀）+ §0.2 编号段隔离对照表（6 行示例）
  - `06-toolchain-and-automation.md` 头部添加 SSoT 声明（OS-STD-TOOL-NNN 为目标前缀）+ §0.2 编号段隔离对照表（6 行示例）
  - 对照表展示同一编号在两卷的不同定义，明确隔离方案

### 2.7 D-07：08 前缀统一 OS-STD-CHECK

- **文件**: `08-compliance-checklist.md`
- **问题**: STD-DOC/CODE/IRON/CI 自创独立前缀与全项目 OS-* 体系并行
- **执行**:
  - 头部添加 SSoT 声明行（OS-STD-CHECK-{DOC|CODE|IRON|CI}-NNN 为目标前缀）
  - 新增 §0 "检查规则前缀统一映射"
    - §0.1 前缀迁移映射表（4 类前缀迁移：STD-DOC→OS-STD-CHECK-DOC 等）
    - §0.2 迁移状态（编号并存阶段，1.0.1 触发统一替换）
    - 体系融合说明（被检查规则 vs 检查规则前缀清晰区分）
    - 脚本命名影响说明（脚本名不受迁移影响）

### 2.8 D-08：09 废弃标记

- **状态**: ✅ 先前会话已执行
- **验证**: 09-license-strategy.md 第 5 行已有废弃头部声明，README + 110 合并文档 + 08 引用均已更新

### 2.9 D-09：60/70/110 子域校验

- **文件**: `60-checkpatch-rule-map.md`
- **校验结果**:
  - 60 使用 OS-STD-CODE-NNN（4 段）✅ — 引用 01 的 010-027 + 新增 028-036+ checkpatch 专属规则
  - 70 使用 OS-STD-DOC-NNN（4 段）✅ — 独立子域（DOC = Documentation）
  - 110 使用 OS-STD-SPDX-NNN（4 段）✅ — 独立子域（SPDX = License）
- **执行**: 为 60 添加 D-09 子域校验声明（澄清与 01 的"引用+扩展"关系，无冲突）

---

## 3. 修复模式总结

### 3.1 SSoT 对齐模式的三层结构

本次执行的 10 个文件均采用统一的三层结构：

```
┌─────────────────────────────────────────────────────┐
│ 第 1 层：SSoT 声明行（头部 blockquote）              │
│ - 声明目标前缀（OS-FMT / OS-STD-CODE / OS-STD-PROD │
│   / OS-STD-TOOL / OS-STD-CHECK-* 等）              │
│ - 声明历史编号并存等价                              │
│ - 声明规则效力以本卷正文为准                         │
│ - 声明与闭源总纲的冲突以闭源总纲为准                 │
├─────────────────────────────────────────────────────┤
│ 第 2 层：§0 编号映射表（正文前插入）                 │
│ - 编号对齐映射表（历史编号 → 目标编号）              │
│ - 迁移状态说明（并存阶段 / 触发条件）                │
│ - 保留的独立权威内容表（如有）                       │
├─────────────────────────────────────────────────────┤
│ 第 3 层：原始正文（保留不变）                        │
│ - 所有历史编号保留                                  │
│ - 所有章节内容保留                                  │
│ - 所有交叉引用保留                                  │
└─────────────────────────────────────────────────────┘
```

### 3.2 与 C-2.6 原始报告的差异

C-2.6 原始报告建议的执行方式（删除文件、重写章节）与用户约束冲突：

| C-2.6 原始建议 | 实际执行方式 | 理由 |
|---------------|------------|------|
| D-03 删除 2 份 C* 文档 | SSoT 对齐（保留文件 + 添加映射表） | §7-§10 为内核态专属权威内容，不在 01/02/03 中 |
| D-02 删除 80 §1-§4 | SSoT 对齐（保留 + 声明从属关系） | 80 有 OLK-6.6 行号索引独特价值 |
| D-04/D-05 全量替换编号 | SSoT 对齐（并存 + 映射表） | 1.0.1 开发阶段触发统一替换 |
| D-06 重写 05/06 编号 | SSoT 对齐（并存 + 隔离声明） | 避免破坏 30+ 处引用 |
| D-07 全量替换 08 前缀 | SSoT 对齐（并存 + 映射表） | 避免破坏检查脚本输出引用 |

---

## 4. 编号体系最终状态

### 4.1 14 种前缀的最终归类

| 前缀 | 含义 | 归属文档 | 状态 |
|------|------|---------|------|
| OS-IRON-NNN | 工程铁律 | 闭源附录 A（SSoT）+ 04-philosophy（哲学阐述） | ✅ D-01 对齐 |
| OS-BAN-NNN | 禁止规则 | 01-coding-standards + 10-coding-style/C* | 活跃 |
| OS-FMT-NNN | 格式规则 | 02-code-format（SSoT） | ✅ D-04 迁移目标 |
| OS-STD-CODE-NNN | 编码规则 | 01-coding-standards（SSoT）+ 60-checkpatch（映射+扩展） | ✅ D-05 迁移目标 |
| OS-STD-PROD-NNN | 开发流程规则 | 05-development-process（SSoT） | ✅ D-06 迁移目标 |
| OS-STD-TOOL-NNN | 工具链规则 | 06-toolchain-and-automation（SSoT） | ✅ D-06 迁移目标 |
| OS-STD-CHECK-* | 检查规则 | 08-compliance-checklist（SSoT） | ✅ D-07 迁移目标 |
| OS-STD-DOC-NNN | 文档规范 | 70-kernel-doc-standard（SSoT） | ✅ D-09 校验通过 |
| OS-STD-SPDX-NNN | 许可证规范 | 110-spdx-license-compliance（SSoT） | ✅ D-09 校验通过 |
| OS-KER-NNN | 内核工程规则 | 02-code-format（格式部分迁移至 OS-FMT）+ 01/03/04（内核态专属保留） | ✅ D-04 部分迁移 |
| OS-STD-GOV-NNN | 治理规则 | 07-maintainers-and-governance | 活跃 |
| OS-ACC-NNN | 验收标准 | 00-handbook + 130-roadmap | 活跃 |
| OS-ABI-NNN | ABI 规则 | 30-interfaces + 30-runtime-interfaces | 活跃 |
| OS-SEC-NNN | 安全规则 | 10-coding-style/secure | 活跃 |

### 4.2 编号冲突消除状态

| 冲突类型 | 冲突前 | 冲突后 | 消除方式 |
|---------|--------|--------|---------|
| IRON 编号偏移 | 04-philosophy OS-IRON-003~006 偏移 | §0 映射表明确对齐关系 | D-01 |
| 配置项重复 | 80 §1 与 02 §9 重叠 | SSoT 声明 + 交叉引用 | D-02 |
| C* 格式编号冲突 | OS-KER-011~014 双重定义 | §0 映射表指向 02 为 SSoT | D-03 |
| OS-KER-005 双义 | Tab vs 字符串禁止断行 | 拆分为 OS-FMT-001 + OS-FMT-008 | D-04 |
| OS-STD 3/4 段混用 | OS-STD-CODE-001 + OS-STD-002~027 | 统一为 OS-STD-CODE-001~027 | D-05 |
| 05/06 编号段冲突 | OS-STD-101~158 双重定义 | 隔离为 PROD / TOOL | D-06 |
| 08 前缀独立 | STD-DOC/CODE/IRON/CI 自创 | 迁移至 OS-STD-CHECK-* | D-07 |
| 09 废弃 | 与 110 重叠 | 废弃标记 + 指向 110 | D-08 |
| 60/70/110 子域 | 校验是否冲突 | 独立子域，无冲突 | D-09 |

---

## 5. 后续工作

### 5.1 1.0.1 开发阶段触发项

以下迁移工作在 1.0.1 开发阶段触发执行（当前为编号并存阶段）：

| 触发条件 | 执行内容 | 涉及文件 |
|---------|---------|---------|
| `.clang-format` 实施时 | OS-KER → OS-FMT 全量替换 | 02-code-format.md |
| checkpatch 脚本实施时 | OS-STD → OS-STD-CODE 全量替换 | 01-coding-standards.md + 60-checkpatch-rule-map.md |
| CI/CD 流水线实施时 | OS-STD → OS-STD-PROD / OS-STD-TOOL 全量替换 | 05 + 06 |
| CI 检查脚本实施时 | STD-* → OS-STD-CHECK-* 全量替换 | 08-compliance-checklist.md |

### 5.2 与 C-2.7 深层次问题排查的协同

C-2.7 后台 Agent 正在审查 20-modules/01-08 模块文档。当 C-2.7 完成后，其发现的问题可能与本次 C-2.6 合并决策执行产生协同：

- 若 C-2.7 发现模块文档引用了冲突编号 → 使用本次建立的 §0 映射表消解
- 若 C-2.7 发现模块文档需要新增规则编号 → 遵循本次确立的 4 段前缀体系（OS-FMT / OS-STD-CODE / OS-STD-PROD / OS-STD-TOOL / OS-STD-CHECK-* 等）

---

## 6. 相关文档

### 6.1 本报告引用的执行对象

- `docs/AirymaxOS/50-engineering-standards/04-engineering-philosophy.md`（D-01）
- `docs/AirymaxOS/50-engineering-standards/80-clang-format-enforcement.md`（D-02）
- `docs/AirymaxOS/50-engineering-standards/10-coding-style/C_coding_style_standard.md`（D-03）
- `docs/AirymaxOS/50-engineering-standards/10-coding-style/C_coding_style_standard_supplement.md`（D-03）
- `docs/AirymaxOS/50-engineering-standards/02-code-format.md`（D-04）
- `docs/AirymaxOS/50-engineering-standards/01-coding-standards.md`（D-05）
- `docs/AirymaxOS/50-engineering-standards/05-development-process.md`（D-06）
- `docs/AirymaxOS/50-engineering-standards/06-toolchain-and-automation.md`（D-06）
- `docs/AirymaxOS/50-engineering-standards/08-compliance-checklist.md`（D-07）
- `docs/AirymaxOS/50-engineering-standards/60-checkpatch-rule-map.md`（D-09）

### 6.2 同批分析报告

- `docs-closed/agent-linux-dev/_analysis_0.3.0/06-engineering-standards-consolidation.md`（C-2.6 原始合并报告，942 行）
- `docs-closed/agent-linux-dev/_analysis_0.3.0/07-engineering-standards-review.md`（C-2 审查报告，756 行）
- `docs-closed/agent-linux-dev/agent-linux基本工程标准规范.md`（闭源 SSoT，1444 行）

---

> **报告结束** | C-2.6 合并决策执行完成 | v0.3.0 | 2026-07-09 | 闭源不公开
