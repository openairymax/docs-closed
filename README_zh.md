# docs-closed — 技术参考与评审归档

**语言:** [English](README.md) | 简体中文

> Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
> **最后更新**: 2026-09-19
> **当前版本**: Airymax 0.1.1（唯一奠基版本）
> **文档体系**: v4.0（奠基 + 38 仓拆分 + 生产就绪三大支柱）

---

## 📌 版本定位

**Airymax 0.1.1 是唯一的奠基版本**（无 0.1.2 / 0.2.0 / 0.3.0 计划，直接过渡到 1.0.1）。所有架构、标准、许可证、质量和生态工作必须在 0.1.1 内完成。

**三大支柱**：
1. **奠基 W01-W30**（~1,620h）— atoms 解耦、CoreKern 精简、taskflow 修复、SDK 4 语言
2. **38 仓拆分 SP01-SP31**（~572h）— 1 伞仓 + 5 管理仓 + 29 叶子仓 + 3 顶层仓
3. **生产就绪 SP32-SP37**（~240h）— CI/CD、发布、监控、安全、文档、社区

**总工时**：~3,396.5h | **总验收标准**：149 项 | **路线图**：~36 天

---

## 📚 核心文档（7 篇）

### 1. [技术全面改进方案 v3.0](./agent-workload-dev/10-designs-and-contracts/designs/_design_0.1.1/02-tech-improvement-plan-v3.0.md) — v4.0

0.1.1 版本技术改进总方案（约 1,989 行）。包含：
- 第二十章：38 项已确认缺陷完整清单（A-H 类）
- 第二十五章：W01-W30 奠基工作清单（~1,620h）
- 第二十六章：38 仓拆分方案（SP01-SP31）
- 第二十七章：生产就绪方案（SP32-SP37）
- 附录 A：79 项任务总表（~964.5h）

### 2. [详细任务清单](./agent-workload-dev/10-designs-and-contracts/designs/_design_0.1.1/03-detailed-task-list.md) — v2.0

0.1.1 版本详细任务清单（3,811 行，146 项主任务）。包含：
- 第一部分：W01-W30 奠基任务
- 第二部分：Phase 0-4 修复任务（79 项）
- 第三~六部分：38 项缺陷修复任务
- 第七部分：SP01-SP31 38 仓拆分任务
- 第八部分：SP32-SP37 生产就绪任务

### 3. [agentrt 工程标准规范手册](./agent-workload-dev/agentrt工程标准规范手册.md) — v26.0

0.1.1 版本工程标准规范（4,584 行，356 项 BAN 规则）。包含：
- §11.5 独立子仓库路径引用安全规范
- §11.6 agentos_ → agentrt_ 彻底改名规范（七层面改名矩阵）
- §11.7 38 仓 git submodule 拆分规范
- §11.8 build 目录必须在源树外规范
- 第三十六章 SPLIT-01~08（8 项拆分规范）
- 第三十七章 PROD-01~06（6 项生产就绪规范）
- IRON-1~8（8 项工程铁律）

### 4. [AgentRT 仓库拆分方案](./agent-workload-dev/10-designs-and-contracts/designs/_design_0.1.1/01-repo-split-proposal.md)

38 仓拆分方案详述。1 伞仓(airymaxhub) + 5 管理仓(agentrt/sdk/ecosystem/products/agent-linux) + 29 叶子仓 + 3 顶层仓。

### 5. [仓库拆分方案可行性分析报告](./agent-workload-dev/90-reviews-and-archive/reviews/_analysis_0.1.1/02-repo-split-feasibility-analysis.md)

38 仓拆分方案可行性分析报告。

### 6. [taskflow 与 corekern 调度器对比报告](./agent-workload-dev/90-reviews-and-archive/reviews/_analysis_0.1.1/01-taskflow-vs-corekern-scheduler-comparison.md)

taskflow 与 corekern scheduler 双引擎对比报告，确定双引擎协同方案（graph_engine 留 A 类微核心原语 + taskflow_advanced 作为 B 类 DAG 工作流编排 + pregel_engine 0.1.1 强制 max_workers=1 降级）。

### 7. [许可证全面审计报告](./agent-workload-dev/90-reviews-and-archive/reviews/_review_0.1.1/01-license-audit-report.md)

0.1.1 版本许可证全面审计报告。OpenAirymax 内所有 5 个 LICENSE 文件 + 3 个 NOTICE 文件统一为 AGPL v3 + Apache 2.0 双许可证；MemoryRovol 的独立许可策略详见审计报告原文。

---

## 📂 目录结构

```
docs-closed/
├── README.md                                    # 英文版
├── README_zh.md                                 # 本文档（中文版）
├── agent-workload-dev/                          # AgentRT 运行时技术文档（索引：agent-workload-dev/README.md）
│   ├── agentrt工程标准规范手册.md               # 工程标准规范手册（4,584 行）
│   ├── agentrt开发路线和进度1.0.1版本.md        # 开发路线与进度跟踪
│   ├── repo-topology.md                         # 仓库拓扑
│   ├── 0.1.9 … 0.2.x 架构改进方案.md            # 各版本方案（每版单一入口）
│   ├── 10-designs-and-contracts/                # 活文档：设计·规格·合约·计划
│   │   ├── designs/                             #   设计稿（+ _design_0.1.1/ 版本化快照）
│   │   ├── subsystem-specs/                     #   13 篇子系统规格（01 … 13-module-boundaries）
│   │   ├── contracts/                           #   合约头文件（A/B/C）+ 契约测试；Gate 4/5 的 SSoT 宿主
│   │   └── engineering-plans/                   #   日志收敛、错误码迁移专项计划
│   └── 90-reviews-and-archive/                  # 只读封存：评审·参考·快照
│       ├── reviews/                             #   _review_v1.0 … _review_v4.4、_analysis_0.1.1、
│       │                                        #   _review_0.1.1、_archive_0.1.6、
│       │                                        #   _archive_conversations、_archive_fix_history
│       ├── tech-reference/                      #   技术借鉴与改进（历史归档）
│       └── snapshots/                           #   单文件快照（0.1.20 r63）
├── agent-linux-dev/                             # AirymaxOS 技术参考与历史归档（索引：agent-linux-dev/README.md）
│   ├── 10-references/                           # 设计依据（参考来源 + 任务账本生成器）
│   │   ├── openeuler-tech-reference/            #   openEuler 技术规范参考（14 篇）
│   │   ├── olk66-source-mapping/                #   OLK-6.6 源码映射（8 篇）
│   │   ├── microkernel-design-ref/              #   seL4 / Zircon / Minix3 微内核设计参考（6 篇）
│   │   ├── industry-best-practices/             #   行业最新理论与最佳实践（4 篇）
│   │   └── generators/                          #   任务账本生成器（5 个 Python 脚本）
│   ├── 20-archive/                              # 历史归档（只读）
│   │   ├── reviews/                             #   版本审查/研究系列（36 轮次，157 篇）
│   │   └── designs/                             #   目录结构设计（_design_0.2.1 … _design_0.2.4）
│   ├── 0.0.x-极境OS任务方案.md                  # 逐版本施工账本（0.0.2 / 0.0.3 / 0.0.4）
│   ├── 0.0.4-*.md                               # 0.0.4 输入清单 / 固件与硬件使能 / 构建提速 / 流水线治理
│   ├── AirymaxOS-终端验证命令墙.md              # 终端验证命令速查
│   ├── agentrt-linux基本工程标准规范.md         # agentrt-linux 工程标准规范
│   ├── agentrt-linux开发路线和进度.md           # agentrt-linux 开发路线与进度
│   └── agentrt-linux验收实验任务卡草案.md       # 验收实验任务卡
├── openstandards/                               # 开放标准研究稿
│   ├── _research_v1.0/                          #   重构建议书
│   ├── _research_v2.0/                          #   优化稿 v2
│   └── _research_v2.1/                          #   评审稿 v2.1
├── paper/                                       # 学术论文材料
│   ├── 01-hot-os-2027-*.md … 16-*.md            #   HotOS 2027、IPC 与 capability-folding 研究
│   ├── budget-aware-ttc/                        #   预算感知 TTC 研究
│   └── edge-cloud-agent-measurement/            #   端云智能体测量研究
└── TOC材料/                                     # 技术 Oversight 委员会材料
    ├── 00_…07_*.html                            #   演示页（HTML）
    ├── PNG_HD/  docs/                           #   高清图导出与支撑文档
    └── 《AgentOS开源项目准入申请》2(1).pptx      #   开源项目准入申请材料
```

---

## 🔑 工程铁律 IRON-1~8

| 编号 | 铁律 | 说明 |
|------|------|------|
| IRON-1 | 唯一奠基版本 | 0.1.1 是唯一奠基版本，无中间过渡 |
| IRON-2 | 禁止桩函数桩文件 | 严禁未实现的功能设计、桩函数/桩文件、简化功能 |
| IRON-3 | 禁止绕开功能限制 | 严禁绕开功能限制的方式完成编译和集成 |
| IRON-4 | 禁止新特性 | 0.1.1 内不引入新特性 |
| IRON-5 | 禁止简化功能 | 严禁简化功能以逃避实现 |
| IRON-6 | 禁止跨层耦合残留 | atoms 内核层必须保持绝对安全，无技术债务 |
| IRON-7 | 禁止版本过渡 | 0.1.1 后直接 1.0.1，禁止 0.1.2/0.2.0/0.3.0/1.0.0 |
| IRON-8 | 禁止生产就绪降级 | 不留兼容别名头/兼容层/双轨制 |

---

## 📊 关键数据

| 项目 | 数值 |
|------|------|
| 核心文档 | 7 篇 |
| BAN 规则 | 356 项 |
| 工程铁律 | 8 项（IRON-1~8） |
| 拆分规范 | 8 项（SPLIT-01~08） |
| 生产就绪规范 | 6 项（PROD-01~06） |
| 奠基工作 | W01-W30（~1,620h） |
| 拆分任务 | SP01-SP31（~572h） |
| 生产就绪任务 | SP32-SP37（~240h） |
| 总工时 | ~3,396.5h |
| 总验收标准 | 149 项 |
| 路线图 | ~36 天 |
| 仓库数量 | 38 个（1+5+29+3） |

---

## 📜 归档原则

1. **当前版本文档**（0.1.1）存放于 `agent-workload-dev/10-designs-and-contracts/designs/_design_0.1.1/`、`agent-workload-dev/90-reviews-and-archive/reviews/_analysis_0.1.1/` 与 `agent-workload-dev/90-reviews-and-archive/reviews/_review_0.1.1/`
2. **历史轮次文档**归档至 `agent-workload-dev/90-reviews-and-archive/reviews/_archive_fix_history/round-archives/`
3. **方案/计划/报告**归档至 `_archive_fix_history/` 下对应的类型子目录
4. **历史对话**独立存放于 `agent-workload-dev/90-reviews-and-archive/reviews/_archive_conversations/`，按需查阅
5. **归档材料只追加不改写**：历史结论原样保留以便溯源，不在原地修订

---

## 🔄 版本演进

| 轮次 | 时间 | 文档版本 | 状态 |
|------|------|---------|------|
| 第09轮 | 2026-04 ~ 2026-06 | v11.14 → v11.21 | 已归档 |
| **0.1.1** | **2026-07 ~ 至今** | **v4.0** | **进行中** |
| 1.0.1 | 待定 | — | 待启动 |

---

## 📞 联系方式

- **组织**: openairymax（atomgit.com）
- **伞仓**: `git@atomgit.com:openairymax/airymaxhub.git`
- **docs-closed 仓**: `git@atomgit.com:openairymax/docs-closed.git`

---

**© 2025-2026 SPHARX Ltd. All Rights Reserved.**
"From data intelligence emerges."
