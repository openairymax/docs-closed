Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# docs-closed — Technical Reference & Review Archive

**Language:** English | [简体中文](README_zh.md)

> **Last updated**: 2026-09-19
> **Version context**: Airymax 0.1.1 (the single founding release)
> **Document system**: v4.0 (foundation + 38-repo split + production readiness)

---

## 📌 Purpose

`docs-closed/` is the **technical reference & review archive** of the Airymax
documentation center. It is published together with the open-source repositories
and provides, in the spirit of open development:

1. **Upstream traceability** — the reference material behind Airymax designs:
   openEuler / OLK-6.6 source mapping, microkernel design studies (seL4,
   Zircon, Minix3) and industry best-practice surveys.
2. **Design review records** — architecture improvement plans, audits and
   convergence-issue reviews produced across the 0.1.x development rounds.
3. **Historical archive** — early technology-evaluation analyses, prototype
   designs and long-task conversation records, preserved for project-history
   research.

Formal, user-facing design documents live in the sibling leaf repositories
`docs/docs-workload/` (AirymaxRT runtime) and `docs/docs-linux/` (AirymaxOS).
Per the BAN-INTERNAL-001~005 layering rules, those formal documents express
the absorbed conclusions in Airymax's own language and do not copy the
reference wording maintained in this archive.

---

## 📌 Version Positioning

**Airymax 0.1.1 is the single founding release** (no 0.1.2 / 0.2.0 / 0.3.0
plans — the next milestone is 1.0.1). All architecture, standards, licensing,
quality and ecosystem work is anchored inside 0.1.1.

**Three pillars**:

1. **Foundation W01–W30** (~1,620 h) — atoms decoupling, CoreKern slimming,
   taskflow fixes, 4-language SDK
2. **38-repo split SP01–SP31** (~572 h) — 1 umbrella + 5 management +
   29 leaf + 3 top-level repos
3. **Production readiness SP32–SP37** (~240 h) — CI/CD, release, monitoring,
   security, documentation, community

**Total effort**: ~3,396.5 h | **Acceptance criteria**: 149 | **Roadmap**: ~36 days

---

## 📚 Key 0.1.1 Documents (7)

### 1. [Comprehensive Technical Improvement Plan v3.0](agentrt/01-designs/_design_0.1.1/02-tech-improvement-plan-v3.0.md) — v4.0

Master technical improvement plan for 0.1.1 (~1,989 lines):

- Chapter 20: full list of 38 confirmed defects (classes A–H)
- Chapter 25: foundation work plan W01–W30 (~1,620 h)
- Chapter 26: 38-repo split plan (SP01–SP31)
- Chapter 27: production-readiness plan (SP32–SP37)
- Appendix A: 79-task master table (~964.5 h)

### 2. [Detailed Task List](agentrt/01-designs/_design_0.1.1/03-detailed-task-list.md) — v2.0

Detailed task breakdown for 0.1.1 (3,811 lines, 146 main tasks):

- Part 1: W01–W30 foundation tasks
- Part 2: Phase 0–4 fix tasks (79 items)
- Parts 3–6: 38 defect-fix tasks
- Part 7: SP01–SP31 repo-split tasks
- Part 8: SP32–SP37 production-readiness tasks

### 3. [Engineering Standards Handbook](agentrt/agentrt工程标准规范手册.md) — v26.0

Engineering standards for 0.1.1 (4,584 lines, 356 BAN rules):

- §11.5 independent-submodule path-reference safety
- §11.6 `agentos_` → `agentrt_` full rename matrix (seven layers)
- §11.7 38-repo git-submodule split rules
- §11.8 out-of-source build-tree rule
- Chapter 36: SPLIT-01~08 (8 split rules)
- Chapter 37: PROD-01~06 (6 production-readiness rules)
- IRON-1~8 (8 engineering iron rules)

### 4. [Repository Split Proposal](agentrt/01-designs/_design_0.1.1/01-repo-split-proposal.md)

The 38-repo split plan in detail: 1 umbrella repo (airymaxhub) + 5 management
repos (agentrt/sdk/ecosystem/products/agent-linux) + 29 leaf repos +
3 top-level repos.

### 5. [Split Feasibility Analysis](agentrt/00-reviews/_analysis_0.1.1/02-repo-split-feasibility-analysis.md)

Feasibility analysis report for the 38-repo split plan.

### 6. [TaskFlow vs CoreKern Scheduler Comparison](agentrt/00-reviews/_analysis_0.1.1/01-taskflow-vs-corekern-scheduler-comparison.md)

Dual-engine comparison report that settled the co-existence design:
`graph_engine` keeps Class-A micro-core primitives, `taskflow_advanced`
serves as the Class-B DAG workflow orchestrator, and `pregel_engine` is
force-degraded to `max_workers=1` in 0.1.1.

### 7. [License Audit Report](agentrt/00-reviews/_review_0.1.1/01-license-audit-report.md)

Comprehensive license audit for 0.1.1: all 5 LICENSE and 3 NOTICE files in
OpenAirymax unified under the AGPL-3.0-or-later + Apache-2.0 dual license;
MemoryRovol's separate licensing policy is covered in the audit report itself.

---

## 📂 Repository Layout

```
docs-closed/
├── README.md                 # This file (English)
├── README_zh.md              # Chinese version
├── agentrt/                  # AgentRT runtime technical docs (index: agentrt/README.md)
│   ├── agentrt工程标准规范手册.md            # Engineering standards handbook
│   ├── agentrt开发路线和进度1.0.1版本.md       # Roadmap & progress tracking (1.0.1)
│   ├── repo-topology.md                      # Repository topology
│   ├── 0.1.x / 0.2.x 改进方案与审查系列.md    # 0.1.1–0.2.x improvement & review series
│   ├── 00-reviews/                           # Reviews, analyses and archives
│   │   ├── _analysis_0.1.1/                  #   Dual-engine comparison, split feasibility
│   │   ├── _review_0.1.1/                    #   License audit report
│   │   ├── _review_v1.0 … _review_v4.4/      #   Historical review rounds
│   │   ├── _archive_0.1.6/                   #   0.1.6 snapshot archive
│   │   ├── _archive_conversations/           #   Long-task conversation records
│   │   └── _archive_fix_history/             #   Fix-work history (rounds/plans/proposals/
│   │                                         #   legacy docs/inspection reports)
│   ├── 01-designs/                           # Design proposals
│   │   └── _design_0.1.1/                    #   0.1.1 founding documents
│   ├── 05-tech-reference-and-improvement/    # Early tech-reference & prototype archive
│   ├── 06-contracts/                         # Inter-module contract headers (A/B/C) + tests
│   ├── 07-subsystem-specs/                   # 13 subsystem specs (checkpoint … module-boundaries)
│   └── 50-engineering-standards/             # Log & error-code convergence plans
├── agent-linux-dev/          # AirymaxOS technical reference & archive (index: agent-linux-dev/README.md)
│   ├── 10-references/                        # Design sources (references + task-ledger generators)
│   │   ├── openeuler-tech-reference/         #   openEuler technical-spec references (14 docs)
│   │   ├── olk66-source-mapping/             #   OLK-6.6 source-to-design mapping (8 docs)
│   │   ├── microkernel-design-ref/           #   seL4 / Zircon / Minix3 references (6 docs)
│   │   ├── industry-best-practices/          #   Industry theory & AirymaxOS synthesis (4 docs)
│   │   └── generators/                       #   Task-ledger generators (5 Python scripts)
│   ├── 20-archive/                           # Historical archive (read-only)
│   │   ├── reviews/                          #   Version review & research series (36 rounds, 157 docs)
│   │   └── designs/                          #   Directory-structure designs (_design_0.2.1 … _design_0.2.4)
│   ├── 0.0.x-极境OS任务方案.md               # Per-version task ledgers (0.0.2 / 0.0.3 / 0.0.4)
│   ├── 0.0.4-*.md                            # 0.0.4 input list / firmware / build / pipeline plans
│   ├── AirymaxOS-终端验证命令墙.md           # Terminal verification command wall
│   ├── agentrt-linux基本工程标准规范.md       # agentrt-linux engineering standards
│   ├── agentrt-linux开发路线和进度.md         # agentrt-linux roadmap & progress
│   └── agentrt-linux验收实验任务卡草案.md     # Acceptance experiment task cards
├── openstandards/            # Open-standard research drafts
│   ├── _research_v1.0/                       #   Rebuild proposal
│   ├── _research_v2.0/                       #   Optimization v2
│   └── _research_v2.1/                       #   Review v2.1
├── paper/                    # Academic publication material
│   ├── 01-hot-os-2027-*.md … 16-*.md         # HotOS 2027 papers, IPC & capability-folding studies
│   ├── budget-aware-ttc/                     # Budget-aware TTC study
│   └── edge-cloud-agent-measurement/         # Edge-cloud agent measurement study
└── TOC材料/                  # Technical Oversight Committee deck
    ├── 00_…07_*.html                         # Slide material (HTML)
    ├── PNG_HD/  docs/                        # HD exports and supporting docs
    └── 《AgentOS开源项目准入申请》2(1).pptx    # Open-source project admission deck
```

Directory-level indexes: [agentrt/README.md](agentrt/README.md) ·
[agent-linux-dev/README.md](agent-linux-dev/README.md)

---

## 🔑 Engineering Iron Rules IRON-1~8

| Rule | Name | Description |
|------|------|-------------|
| IRON-1 | Single founding release | 0.1.1 is the only founding version; no intermediate transitions |
| IRON-2 | No stub functions/files | Unimplemented designs, stubs and placeholder features are prohibited |
| IRON-3 | No workaround integration | Builds/integration must not bypass functional gates |
| IRON-4 | No new features | 0.1.1 introduces no new features |
| IRON-5 | No simplification | Features must not be simplified to dodge implementation |
| IRON-6 | No cross-layer residue | The atoms kernel layer stays absolutely safe, zero technical debt |
| IRON-7 | No transition versions | Straight from 0.1.1 to 1.0.1; 0.1.2/0.2.0/0.3.0/1.0.0 are prohibited |
| IRON-8 | No readiness downgrade | No compat alias headers, compat layers or dual-track systems |

---

## 📊 Key Figures

| Item | Value |
|------|-------|
| Key documents | 7 |
| BAN rules | 356 |
| Iron rules | 8 (IRON-1~8) |
| Split rules | 8 (SPLIT-01~08) |
| Production-readiness rules | 6 (PROD-01~06) |
| Foundation work | W01–W30 (~1,620 h) |
| Split tasks | SP01–SP31 (~572 h) |
| Readiness tasks | SP32–SP37 (~240 h) |
| Total effort | ~3,396.5 h |
| Acceptance criteria | 149 |
| Roadmap | ~36 days |
| Repositories | 38 (1 + 5 + 29 + 3) |

---

## 📜 Archive Principles

1. **Current (0.1.1) founding documents** live under
   `agentrt/01-designs/_design_0.1.1/`, `agentrt/00-reviews/_analysis_0.1.1/`
   and `agentrt/00-reviews/_review_0.1.1/`
2. **Historical round documents** are archived under
   `agentrt/00-reviews/_archive_fix_history/round-archives/`
3. **Proposals / improvement plans / inspection reports** go to the matching
   type-specific subdirectory under `_archive_fix_history/`
4. **Long-task conversation records** are kept separately in
   `agentrt/00-reviews/_archive_conversations/`
5. Archive material is **append-only**: historical conclusions are preserved
   as-is for traceability and are not rewritten in place

---

## 🔄 Version History

| Round | Period | Document system | Status |
|-------|--------|-----------------|--------|
| Round 09 | 2026-04 ~ 2026-06 | v11.14 → v11.21 | Archived |
| **0.1.1** | **2026-07 ~ present** | **v4.0** | **In progress** |
| 1.0.1 | TBD | — | Planned |

---

## 📞 Contact

- **Organization**: openairymax (official primary platform: AtomGit; GitHub mirrors are convenience copies only)
- **Umbrella repo**: `git@atomgit.com:openairymax/airymaxhub.git`
- **docs-closed repo**: `git@atomgit.com:openairymax/docs-closed.git`
- **License**: dual-licensed under AGPL-3.0-or-later OR Apache-2.0 (see `../LICENSE` and `../NOTICE`)
- **Maintainer**: AgentRT open-source maintainer team

---

**© 2025-2026 SPHARX Ltd. All Rights Reserved.**
"From data intelligence emerges."
