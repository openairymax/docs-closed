Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agentrt（Airymax 运行时）闭源工程文档

> **文档定位**: AgentRT 的架构演进方案、设计与契约、评审与归档
> **目录状态**: 2026-11-01 重组（七个专题目录归并为两个，专题稿并入版本方案）
> **主要读者**: Airymax 核心开发组

---

## 1. 定位

本目录存放 AgentRT（Airymax 运行时）的**闭源工程文档**，与公开文档仓
（`docs/`）互补：`docs/docs-workload/` 承载对外可公开的架构与工程标准，
本目录承载**版本演进方案、内部设计稿、团队合约、历史评审**。

两个目录承载全部内容，按「是否仍在服役」二分：

- `10-designs-and-contracts/` —— **活文档**：被实现、被门禁、被引用的
  设计、规格、合约与工程计划。改动即改动工程事实。
- `90-reviews-and-archive/` —— **只读封存**：评审记录、技术参考与快照。
  按快照语义保存，不回溯纠错（见 §4）。

---

## 2. 目录结构

```
agent-workload-dev/
├── README.md                          # 本文件 — 目录索引
├── repo-topology.md                   # 仓库层级与 Git 约定（全局性）
│
├── 10-designs-and-contracts/          # 活文档（设计·规格·合约·计划）
│   ├── designs/                       #   设计稿（方法论与专题，16 篇）
│   │   └── _design_0.1.1/             #     0.1.1 期设计（版本化快照子集）
│   ├── subsystem-specs/               #   子系统规格 01–13（13 篇）
│   ├── contracts/                     #   跨团队接口合约（Gate 4/5 的 SSoT 宿主）
│   └── engineering-plans/             #   工程治理计划（日志收敛、错误码迁移）
│
├── 90-reviews-and-archive/            # 只读封存
│   ├── reviews/                       #   各轮评审与修复历史
│   │   ├── _review_v1.0 … _review_v4.4/   # 版本化评审轮次
│   │   ├── _review_0.1.1/ _analysis_0.1.1/ # 0.1.1 期审计与分析
│   │   ├── _archive_0.1.6/            #   0.1.6 期封存
│   │   ├── _archive_conversations/    #   总线开发长任务对话记录
│   │   └── _archive_fix_history/      #   修复工作历史档案
│   ├── tech-reference/                #   技术借鉴与改进参考（早期归档）
│   └── snapshots/                     #   单文件快照（r63 超大方案快照）
│
├── 0.1.9 … 0.2.x 架构改进方案.md       # 版本演进方案（各版本单一入口）
└── 0.1.20-*.md / agentrt*.md          # 0.1.20 期方案、台账与规范手册
```

### 2.1 版本演进方案（顶层）

每个版本**只有一个入口**：`0.1.N-架构改进方案.md`。该版本期的审查报告、
收口设计、收敛问题点、专题研究一律并入其中作为章节，不再单列平级文件——
避免「方案说 A、审查说非 A」的双份事实源漂移。

| 文档 | 内容 |
|---|---|
| `0.1.9` / `0.1.11` / `0.1.12` / `0.1.13` / `0.1.15` / `0.1.16` / `0.1.17` / `0.1.18` | 历史版本方案（含并入的审查/收口/问题点章节） |
| `0.1.19-架构改进方案.md` | 0.1.19 期方案（并入架构文档、TUI 建设、100k 可行性、机制核减重、低算力稳定性、L1-SSoT 台账、三目标审查七篇专题） |
| `0.1.20-架构改进完善和自演化方案.md` | **现行 SSoT**：0.1.20 期判据、任务清单与自演化机制 |
| `0.1.20-架构文档.md` | 0.1.20 期架构文档 |
| `0.2.x-架构改进方案.md` | 0.2.x 期前瞻方案 |

`0.1.20-架构改进完善和自演化方案.md` 与 `0.1.20-架构文档.md` 是 CI
Gate 45（自指门禁）的**受辖文档**，审计 `<file>:<line>` 引用的有效性。

---

## 3. 命名约定

- **内容目录**：`NN-kebab-case-topic/`（十位编号 + kebab-case 主题；
  与 `agent-linux-dev/10-references`、`20-archive` 同惯例）
- **版本化目录**：`_phase_version/`（下划线 + 阶段 + 版本号）
  - 阶段类型：`review`（评审）、`design`（设计）、`analysis`（分析）、
    `research`（研究）
- **归档目录**：`_archive_xxx/`（下划线 + archive + 主题）
- **文件命名**：`NN-kebab-case-name.md`（编号 + kebab-case 名称）
- **顶级文档**：允许中文名（同 `agent-linux-dev/` 模式）

---

## 4. 快照语义（`90-reviews-and-archive/` 不纠错）

`90-reviews-and-archive/` 内的评审、分析、参考与快照文档按**快照语义**
保存：其正文中出现的路径、文件名与版本号，反映的是**撰写当时**的仓形，
不随之后的目录重组而回改。这是刻意的——历史评审的价值在于其原始判断，
若按当前路径回改，记录与被评审对象之间的对应关系就被抹去了。

因此若在其中读到 `docs-closed/agentrt/00-reviews/…` 一类路径，请按
2026-11-01 的重组映射换算：

| 旧路径 | 现路径 |
|---|---|
| `00-reviews/` | `90-reviews-and-archive/reviews/` |
| `01-designs/` | `10-designs-and-contracts/designs/` |
| `05-tech-reference-and-improvement/` | `90-reviews-and-archive/tech-reference/` |
| `06-contracts/` | `10-designs-and-contracts/contracts/` |
| `07-subsystem-specs/` | `10-designs-and-contracts/subsystem-specs/` |
| `50-engineering-standards/` | `10-designs-and-contracts/engineering-plans/` |
| `archive/` | `90-reviews-and-archive/snapshots/` |
| `docs-closed/agentrt/`（早期根名） | `docs-closed/agent-workload-dev/` |

`10-designs-and-contracts/` 是活文档，**不适用**本节的免纠错豁免：
其中的路径错误一律就地订正。唯一例外是 `designs/_design_0.1.1/` ——
它是 0.1.1 期设计的版本化快照，按快照语义保留原路径。

---

## 5. 维护规则

1. 新增设计或规格 → `10-designs-and-contracts/` 对应子目录，按 `NN-` 编号。
2. 新增评审或分析 → `90-reviews-and-archive/reviews/_review_<version>/`。
3. 版本方案定稿后，其配套的审查/收口/问题点文档并入方案正文，不留平级副本。
4. 移动 `contracts/` 目录或更名，必须同步
   `tools/scripts/ci/quality/gates/lib/contract-sso.sh` 的 `csso_root()`
   候选集，否则 Gate 4/5 转为「未判定」而静默放行。

---

**文档版本**: 0.1.20
**最后更新**: 2026-11-01
**维护者**: AgentRT 开源维护团队
