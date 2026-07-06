# Airymax 0.1.1 Project Management Documentation Center (DocsClosed)

**Language:** English | [简体中文](README_zh.md)

> Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
> **Last Updated**: 2026-07-06
> **Current Version**: Airymax 0.1.1 (the sole foundational version)
> **Documentation System**: v4.0 (Foundation + 38-repo split + Production-readiness — three pillars)

---

## 📌 Version Positioning

**Airymax 0.1.1 is the sole foundational version** (no 0.1.2 / 0.2.0 / 0.3.0 plans; it transitions directly to 1.0.1). All architecture, standards, licensing, quality, and ecosystem work must be completed within 0.1.1.

**Three Pillars**:
1. **Foundation W01-W30** (~1,620h) — atoms decoupling, CoreKern simplification, taskflow fixes, SDK for 4 languages
2. **38-repo split SP01-SP31** (~572h) — 1 umbrella repo + 5 management repos + 29 leaf repos + 3 top-level repos
3. **Production readiness SP32-SP37** (~240h) — CI/CD, release, monitoring, security, documentation, community

**Total effort**: ~3,396.5h | **Total acceptance criteria**: 149 items | **Roadmap**: ~36 days

---

## 📚 Core Documents (7)

### 1. [0.1.1技术全面改进方案v3.0.md](./0.1.1技术全面改进方案v3.0.md) — v4.0

Master technical improvement plan for version 0.1.1 (1796 lines, 133KB). Includes:
- Chapter 20: Complete list of 38 confirmed defects (categories A-H)
- Chapter 25: W01-W30 foundation work list (~1,620h)
- Chapter 26: 38-repo split plan (SP01-SP31)
- Chapter 27: Production-readiness plan (SP32-SP37)
- Appendix A: 79-task master table (~964.5h)

### 2. [0.1.1详细任务清单.md](./0.1.1详细任务清单.md) — v2.0

Detailed task list for version 0.1.1 (3712 lines, 146 main tasks). Includes:
- Part 1: W01-W30 foundation tasks
- Part 2: Phase 0-4 fix tasks (79 items)
- Parts 3-6: 38 defect fix tasks
- Part 7: SP01-SP31 38-repo split tasks
- Part 8: SP32-SP37 production-readiness tasks

### 3. [0.1.1工程标准规范手册.md](./0.1.1工程标准规范手册.md) — v26.0

Engineering standards & specifications for version 0.1.1 (4333 lines, 232KB, 356 BAN rules). Includes:
- §11.5 Independent sub-repository path reference safety specification
- §11.6 agentos_ → agentrt_ thorough rename specification (seven-layer rename matrix)
- §11.7 38-repo git submodule split specification
- §11.8 build directory must reside outside the source tree specification
- Chapter 36 SPLIT-01~08 (8 split specifications)
- Chapter 37 PROD-01~06 (6 production-readiness specifications)
- IRON-1~8 (8 engineering iron laws)

### 4. [0.1.1AgentRT仓库拆分方案.md](./0.1.1AgentRT仓库拆分方案.md)

Detailed 38-repo split plan. 1 umbrella repo (airymaxhub) + 5 management repos (agentrt/sdk/ecosystem/products/agentrt-linux) + 29 leaf repos + 3 top-level repos (devtools/docs/docs-closed).

### 5. [0.1.1AgentRT仓库拆分方案可行性分析报告.md](./0.1.1AgentRT仓库拆分方案可行性分析报告.md)

Feasibility analysis report for the 38-repo split plan.

### 6. [0.1.1_taskflow_vs_corekern_scheduler_对比报告.md](./0.1.1_taskflow_vs_corekern_scheduler_对比报告.md)

Comparative report on the taskflow vs. corekern scheduler dual-engine design, which finalizes the dual-engine collaboration scheme (graph_engine retains A-class microkernel primitives + taskflow_advanced serves as B-class DAG workflow orchestration + pregel_engine is forced to max_workers=1 downgrade in 0.1.1).

### 7. [0.1.1许可证全面审计报告.md](./0.1.1许可证全面审计报告.md)

Comprehensive license audit report for version 0.1.1. All 5 LICENSE files + 3 NOTICE files within OpenAirymax are unified under the AGPL v3 + Apache 2.0 dual license; MemoryRovol remains independently closed-source (SPHARX Ltd. Commercial EULA v1.0).

---

## 📂 Directory Structure

```
docs-closed/
├── README.md                                    # This document
├── 0.1.1技术全面改进方案v3.0.md                  # v4.0 core plan
├── 0.1.1详细任务清单.md                          # v2.0 task list
├── 0.1.1工程标准规范手册.md                      # v26.0 engineering specs
├── 0.1.1AgentRT仓库拆分方案.md                  # 38-repo split plan
├── 0.1.1AgentRT仓库拆分方案可行性分析报告.md     # Split feasibility analysis
├── 0.1.1_taskflow_vs_corekern_scheduler_对比报告.md  # Dual-engine comparison
├── 0.1.1许可证全面审计报告.md                    # License audit
├── contracts/                                   # Separation-of-powers contracts
│   ├── README.md
│   ├── CMakeLists.txt
│   ├── contract_A_B.h                           # A-B team contract
│   ├── contract_A_C.h                           # A-C team contract
│   ├── contract_B_C.h                           # B-C team contract
│   └── contract_test.c                          # Contract tests
├── subsystems/                                  # Subsystem design documents
│   ├── SUBSYSTEM_corekern.md                    # MicroCoreRT microkernel
│   ├── SUBSYSTEM_coreloopthree.md               # Three-layer cognitive loop
│   ├── SUBSYSTEM_cupolas.md                     # Security cupola
│   ├── SUBSYSTEM_memory.md                      # Memory volume loading
│   ├── SUBSYSTEM_checkpoint.md                  # Checkpoint
│   ├── SUBSYSTEM_gateway_d.md                   # Gateway daemon
│   ├── SUBSYSTEM_llm_d.md                       # LLM daemon
│   ├── SUBSYSTEM_tool_d.md                      # Tool daemon
│   ├── SUBSYSTEM_market_d.md                    # Market daemon
│   ├── SUBSYSTEM_manager.md                     # Manager
│   ├── SUBSYSTEM_orchestrator.md                # Orchestrator
│   └── SUBSYSTEM_openlab.md                     # Open laboratory
├── TOC材料/                                     # Technical Oversight Committee materials
│   ├── 01_SystemicLLM.html
│   ├── 02_Foundation.html
│   ├── 03_Intelligence.html
│   ├── 04_LongEngineering.html
│   ├── docs/
│   └── 《AgentOS开源项目准入申请》2(1).pptx
├── 修复工作历史档案/                            # Historical archive
│   ├── 各轮次归档/                              # Per-round document archive
│   ├── 改进计划/                                # 14 historical improvement plans
│   ├── 方案归档/                                # Proposal archive
│   ├── 旧版文档/                                # 3 early-version documents
│   └── 检查报告/                                # 18 audit inspection reports
├── 历史对话/                                    # Long-task historical conversation records
└── 技术借鉴与改进/                              # Technical analysis & prototype design
    ├── 分析报告/                                # 6 technical analysis reports
    ├── 历史原型设计/                            # 4 early prototype designs
    └── 核心模块设计方案/                        # 5 module implementation plans
```

---

## 🔑 Engineering Iron Laws IRON-1~8

| ID | Iron Law | Description |
|------|------|------|
| IRON-1 | Sole foundational version | 0.1.1 is the sole foundational version, with no intermediate transition |
| IRON-2 | No stubs | Unimplemented feature designs, stub functions/files, and simplified features are strictly forbidden |
| IRON-3 | No bypassing functional limits | Completing compilation and integration by bypassing functional limits is strictly forbidden |
| IRON-4 | No new features | No new features are introduced within 0.1.1 |
| IRON-5 | No simplifying features | Simplifying features to evade implementation is strictly forbidden |
| IRON-6 | No cross-layer coupling residue | The atoms kernel layer must remain absolutely safe, with no technical debt |
| IRON-7 | No version transitions | After 0.1.1 it goes directly to 1.0.1; 0.1.2/0.2.0/0.3.0/1.0.0 are forbidden |
| IRON-8 | No production-readiness downgrade | No compatibility alias headers / compatibility layers / dual-track schemes |

---

## 📊 Key Data

| Item | Value |
|------|------|
| Core documents | 7 |
| BAN rules | 356 |
| Engineering iron laws | 8 (IRON-1~8) |
| Split specifications | 8 (SPLIT-01~08) |
| Production-readiness specifications | 6 (PROD-01~06) |
| Foundation work | W01-W30 (~1,620h) |
| Split tasks | SP01-SP31 (~572h) |
| Production-readiness tasks | SP32-SP37 (~240h) |
| Total effort | ~3,396.5h |
| Total acceptance criteria | 149 items |
| Roadmap | ~36 days |
| Repository count | 38 (1+5+29+3) |

---

## 📜 Archiving Principles

1. **Current-version documents** (0.1.1) remain in the docs-closed root directory
2. **Per-round historical documents** are archived under `修复工作历史档案/各轮次归档/`
3. **Plans/proposals/reports** are archived under their respective typed subdirectories
4. **Historical conversations** are stored separately and consulted on demand
5. **After 0.1.1 is released**, this documentation center will be archived under `修复工作历史档案/各轮次归档/第10轮/`

---

## 🔄 Version Evolution

| Round | Time | Document Version | Status |
|------|------|---------|------|
| Round 09 | 2026-04 ~ 2026-06 | v11.14 → v11.21 | Archived |
| **0.1.1** | **2026-07 ~ present** | **v4.0** | **In progress** |
| 1.0.1 | TBD | — | Pending start |

---

## 📞 Contact

- **Organization**: openairymax (atomgit.com)
- **Umbrella repo**: `git@atomgit.com:openairymax/airymaxhub.git`
- **docs-closed repo**: `git@atomgit.com:openairymax/docs-closed.git`

---

**© 2025-2026 SPHARX Ltd. All Rights Reserved.**
"From data intelligence emerges."
