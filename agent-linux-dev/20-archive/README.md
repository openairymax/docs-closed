Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 20-archive — 历史归档

> **文档定位**: agent-linux 逐版本评审与目录结构设计的历史归档（只读）
> **版本**: 1.0.0
> **最后更新**: 2026-11-01
> **主要读者**: agent-linux 架构委员会 + 质量组

---

## 1. 本目录定位

本目录收纳 AirymaxOS 演进过程中产生的**历史记录**，用途是**追溯**而非**依据**：

- 某个设计决定是在哪一轮评审中被提出、被推翻、被改写的；
- 某个工程规范条目（OS-STD / TD-* / IRON-*）的由来与演进；
- 目录结构在 0.2.x 期间的四次调整过程。

**归档不等于现行规范。** 现行规范以
`../agentrt-linux基本工程标准规范.md`、`../agentrt-linux开发路线和进度.md` 与
`docs/docs-linux/` 正式设计文档为准。

> 归档文档保持原文表述（含当时的版本口径、目录名与结论），
> 仅将失效的**路径引用**改写为当前布局，以便链接可达；历史结论本身不作修订。

---

## 2. 目录结构

```
20-archive/
├── README.md                # 本文件
├── reviews/                 # 逐版本评审（36 个轮次，157 篇）
└── designs/                 # 目录结构设计（4 篇）
```

---

## 3. reviews — 逐版本评审

### 3.1 轮次清单

| 轮次 | 篇数 | 性质 |
|------|------|------|
| `_review_0.1.1` | 5 | 文档体系首轮综合评审 |
| `_review_0.2.0` | 5 | 综合评审 + 成熟度评估 |
| `_review_0.2.1` / `_review_0.2.3` / `_review_0.2.4` / `_review_0.2.5` / `_review_0.2.6` | 1 / 1 / 3 / 1 / 1 | 目录结构与文档一致性评审 |
| `_review_0.3.0` / `_review_0.4.0` | 4 / 1 | 源码证据与修订报告 |
| `_review_0.6.0` | 3 | OLK-6.6 / agentrt / Euler 三方对齐 |
| `_review_0.7.0` / `_review_0.8.0` | 1 / 1 | 增量评审 |
| `_review_0.9.0` | 7 | seL4 工程思想与六维问题检出 |
| `_review_v1.0` / `_review_v1.9` | 1 / 2 | 系统性复核 |
| `_review_v2.0` / `_review_v2.1` | 1 / 2 | 系统性复核 v2 |
| `_review_v2.2` | 43 | IPC / AIPc / capability folding 专题深审 |
| `_review_v2.3` ~ `_review_v2.9` | 各 1 | 逐版增量评审 |
| `_review_v3.0` | 4 | 回归测试计划与评审 |
| `_review_v3.1` / `_review_v3.2` / `_review_v3.3` / `_review_v3.4` | 各 1 | 深度一致性审计 |
| `_review_v3.5` | 28 | 终审系列与修复实现报告 |
| `_review_v3.6` | 13 | 三轮审查（安全 / syscall-codegen / 故障处理等域） |
| `_research_0.2.1` / `_research_0.2.5` / `_research_0.3.1` | 2 / 2 / 3 | 专项研究（含 seL4 源码全量提炼） |
| `_analysis_0.3.0` | 11 | 阶段性结论分析（经验教训 / 版本决策 / 微内核源选择） |

合计 **36 个轮次、157 篇**。

### 3.2 使用建议

- 查「某个结论是怎么来的」→ 按版本号定位到对应 `_review_*` 轮次；
- 查「微内核路线为何只保留 seL4」→ `_analysis_0.3.0/04-microkernel-source-sel4-only.md`；
- 查「v3.6 审查提出了哪些改进项」→ `_review_v3.6/07-improvement-recommendations-v3.6.md`；
- 查「IPC 生产就绪度的判定依据」→ `_review_v2.2/21-ipc-production-readiness.md`。

---

## 4. designs — 目录结构设计

| 文档 | 主题 |
|------|------|
| `_design_0.2.1/01-agent-linux-directory-structure.md` | 首次目录结构设计 |
| `_design_0.2.2/01-directory-structure-optimization.md` | 结构优化（合并散目录） |
| `_design_0.2.3/01-agent-linux-directory-structure.md` | 结构再调整 |
| `_design_0.2.4/01-agent-linux-directory-structure.md` | 结构定稿（现行骨架的直接来源） |

四篇文档记录了仓库从「扁平多目录」收敛为「分层骨架」的完整过程。
**2026-11-01 的 7 → 2 目录整合**（`10-references/` + `20-archive/`）沿用同一思路，
可视为该系列的延续。

---

## 5. 与其他目录的关系

| 目录 | 关系 |
|------|------|
| `../10-references/` | 归档评审所引用的外部依据均在该目录 |
| `../0.0.x-极境OS任务方案.md` | 逐版本施工账本；归档评审中的问题项多在后续版本账本中被登记为 TD-* |
| `../agentrt-linux基本工程标准规范.md` | 归档评审中的工程标准结论已收敛为该规范的 OS-STD 编号条目 |
| `docs/docs-linux/` | 对外正式设计文档，不引用归档内容 |

---

> **文档结束** | AgentRT 开源维护团队
