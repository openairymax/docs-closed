Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agentrt（Airymax 运行时）闭源文档

> **文档定位**: agentrt 内部技术文档索引，**闭源不公开**
> **保密级别**: SPHARX Ltd 内部参考
> **版本**: 0.1.1
> **最后更新**: 2026-07-10
> **适用范围**: Airymax 核心开发组

---

## 1. 文档定位与保密声明

本目录存放 AgentRT（Airymax 运行时）的**内部技术文档**，这些文档：

1. **闭源不公开**：本目录所有文档归 SPHARX Ltd 所有，仅供内部使用
2. **与 agentrt-linux 互补**：agentrt-linux 侧重 Linux 内核技术参考，本目录侧重 Airymax 运行时本身的设计与工程文档

---

## 2. 目录结构

```
docs-closed/agentrt/
├── README.md                              # 本文件 — 闭源文档索引
├── agentrt工程标准规范手册.md               # 工程标准规范手册（顶级规范文档）
│
├── 05-tech-reference-and-improvement/     # 技术借鉴与改进参考
│   ├── 01-cicd-restructure-v11.14.md      #   CI/CD 系统化重构方案
│   ├── analysis-reports/                  #   分析报告
│   ├── historical-prototypes/             #   历史原型设计
│   └── core-module-designs/              #   核心模块设计方案
│
├── 06-contracts/                          # 模块间契约定义
│   ├── CMakeLists.txt                     #   契约构建配置
│   ├── README.md                          #   契约说明
│   ├── contract_A_B.h                     #   A↔B 契约头文件
│   ├── contract_A_C.h                     #   A↔C 契约头文件
│   ├── contract_B_C.h                     #   B↔C 契约头文件
│   └── contract_test.c                    #   契约测试
│
├── 07-subsystem-specs/                    # 子系统规格文档
│   ├── 01-checkpoint.md                   #   检查点子系统
│   ├── 02-corekern.md                     #   原子核心 (CoreKern)
│   ├── 03-coreloopthree.md               #   三层认知循环 (CoreLoopThree)
│   ├── 04-cupolas.md                      #   安全穹顶 (Cupolas)
│   ├── 05-gateway-d.md                    #   网关服务 (gateway_d)
│   ├── 06-llm-d.md                        #   LLM 服务 (llm_d)
│   ├── 07-manager.md                      #   管理器
│   ├── 08-market-d.md                     #   市场服务 (market_d)
│   ├── 09-memory.md                       #   记忆系统
│   ├── 10-openlab.md                      #   开放实验室 (OpenLab)
│   ├── 11-orchestrator.md                 #   编排器
│   └── 12-tool-d.md                       #   工具服务 (tool_d)
│
├── _analysis_0.1.1/                       # 0.1.1 分析报告
│   ├── 01-taskflow-vs-corekern-scheduler-comparison.md  # TaskFlow vs CoreKern 调度器对比
│   └── 02-repo-split-feasibility-analysis.md             # 仓库拆分可行性分析
│
├── _review_0.1.1/                         # 0.1.1 审计报告
│   └── 01-license-audit-report.md         #   许可证全面审计报告
│
├── _design_0.1.1/                         # 0.1.1 设计方案
│   ├── 01-repo-split-proposal.md          #   仓库拆分方案
│   ├── 02-tech-improvement-plan-v3.0.md   #   技术全面改进方案 v3.0
│   └── 03-detailed-task-list.md           #   详细任务清单
│
├── _archive_conversations/                # 历史对话归档
│   ├── 总线开发-长任务.md                    #   总线开发对话记录 1
│   └── 总线开发-长任务2.md                   #   总线开发对话记录 2
│
└── _archive_fix_history/                  # 修复工作历史档案
    ├── round-archives/                    #   各轮次归档
    ├── improvement-plans/                 #   改进计划
    ├── proposal-archives/                 #   方案归档
    ├── legacy-docs/                       #   旧版文档
    └── inspection-reports/                #   检查报告
```

---

## 3. 命名约定

遵循 `agentrt-linux/` 的命名规范：

- **内容目录**：`NN-kebab-case-topic/`（两位编号 + kebab-case 主题）
- **版本化目录**：`_phase_version/`（下划线 + 阶段 + 版本号）
  - 阶段类型：`review`（审计/评审）、`design`（设计/方案）、`analysis`（分析）、`research`（研究）
- **归档目录**：`_archive_xxx/`（下划线 + archive + 主题）
- **文件命名**：`NN-kebab-case-name.md`（编号 + kebab-case 名称）
- **顶级文档**：允许中文名（同 `agentrt-linux/` 模式）

---

**文档版本**: v1.0
**生成时间**: 2026-07-10
**维护者**: SPHARX Ltd. - Airymax Team
