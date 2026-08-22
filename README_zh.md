# Airymax 0.1.1 项目管理文档中心 (DocsClosed)

**语言:** [English](README.md) | 简体中文

> Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
> **最后更新**: 2026-07-06
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

### 1. [0.1.1技术全面改进方案v3.0.md](./0.1.1技术全面改进方案v3.0.md) — v4.0

0.1.1 版本技术改进总方案（1796 行，133KB）。包含：
- 第二十章：38 项已确认缺陷完整清单（A-H 类）
- 第二十五章：W01-W30 奠基工作清单（~1,620h）
- 第二十六章：38 仓拆分方案（SP01-SP31）
- 第二十七章：生产就绪方案（SP32-SP37）
- 附录 A：79 项任务总表（~964.5h）

### 2. [0.1.1详细任务清单.md](./0.1.1详细任务清单.md) — v2.0

0.1.1 版本详细任务清单（3712 行，146 项主任务）。包含：
- 第一部分：W01-W30 奠基任务
- 第二部分：Phase 0-4 修复任务（79 项）
- 第三~六部分：38 项缺陷修复任务
- 第七部分：SP01-SP31 38 仓拆分任务
- 第八部分：SP32-SP37 生产就绪任务

### 3. [0.1.1工程标准规范手册.md](./0.1.1工程标准规范手册.md) — v26.0

0.1.1 版本工程标准规范（4333 行，232KB，356 项 BAN 规则）。包含：
- §11.5 独立子仓库路径引用安全规范
- §11.6 agentos_ → agentrt_ 彻底改名规范（七层面改名矩阵）
- §11.7 38 仓 git submodule 拆分规范
- §11.8 build 目录必须在源树外规范
- 第三十六章 SPLIT-01~08（8 项拆分规范）
- 第三十七章 PROD-01~06（6 项生产就绪规范）
- IRON-1~8（8 项工程铁律）

### 4. [0.1.1AgentRT仓库拆分方案.md](./0.1.1AgentRT仓库拆分方案.md)

38 仓拆分方案详述。1 伞仓(airymaxhub) + 5 管理仓(agentrt/sdk/ecosystem/products/agent-linux) + 29 叶子仓 + 3 顶层仓(devtools/docs/docs-closed)。

### 5. [0.1.1AgentRT仓库拆分方案可行性分析报告.md](./0.1.1AgentRT仓库拆分方案可行性分析报告.md)

38 仓拆分方案可行性分析报告。

### 6. [0.1.1_taskflow_vs_corekern_scheduler_对比报告.md](./0.1.1_taskflow_vs_corekern_scheduler_对比报告.md)

taskflow 与 corekern scheduler 双引擎对比报告，确定双引擎协同方案（graph_engine 留 A 类微核心原语 + taskflow_advanced 作为 B 类 DAG 工作流编排 + pregel_engine 0.1.1 强制 max_workers=1 降级）。

### 7. [0.1.1许可证全面审计报告.md](./0.1.1许可证全面审计报告.md)

0.1.1 版本许可证全面审计报告。OpenAirymax 内所有 5 个 LICENSE 文件 + 3 个 NOTICE 文件统一为 AGPL v3 + Apache 2.0 双许可证；MemoryRovol 独立闭源（SPHARX Ltd. 商业 EULA v1.0）。

---

## 📂 目录结构

```
docs-closed/
├── README.md                                    # 英文版
├── README_zh.md                                 # 本文档（中文版）
├── 0.1.1技术全面改进方案v3.0.md                  # v4.0 核心方案
├── 0.1.1详细任务清单.md                          # v2.0 任务清单
├── 0.1.1工程标准规范手册.md                      # v26.0 工程规范
├── 0.1.1AgentRT仓库拆分方案.md                  # 38 仓拆分方案
├── 0.1.1AgentRT仓库拆分方案可行性分析报告.md     # 拆分可行性分析
├── 0.1.1_taskflow_vs_corekern_scheduler_对比报告.md  # 双引擎对比
├── 0.1.1许可证全面审计报告.md                    # 许可证审计
├── contracts/                                   # 三权分立契约
│   ├── README.md
│   ├── CMakeLists.txt
│   ├── contract_A_B.h                           # A-B 团队契约
│   ├── contract_A_C.h                           # A-C 团队契约
│   ├── contract_B_C.h                           # B-C 团队契约
│   └── contract_test.c                          # 契约测试
├── subsystems/                                  # 子系统设计文档
│   ├── SUBSYSTEM_corekern.md                    # 微核心 MicroCoreRT
│   ├── SUBSYSTEM_coreloopthree.md               # 三层认知循环
│   ├── SUBSYSTEM_cupolas.md                     # 安全穹顶
│   ├── SUBSYSTEM_memory.md                      # 记忆卷载
│   ├── SUBSYSTEM_checkpoint.md                  # 检查点
│   ├── SUBSYSTEM_gateway_d.md                   # 网关 daemon
│   ├── SUBSYSTEM_llm_d.md                       # LLM daemon
│   ├── SUBSYSTEM_tool_d.md                      # 工具 daemon
│   ├── SUBSYSTEM_market_d.md                    # 市场 daemon
│   ├── SUBSYSTEM_manager.md                     # 管理器
│   ├── SUBSYSTEM_orchestrator.md                # 编排器
│   └── SUBSYSTEM_openlab.md                     # 开放实验室
├── TOC材料/                                     # 技术 Oversight 委员会材料
│   ├── 01_SystemicLLM.html
│   ├── 02_Foundation.html
│   ├── 03_Intelligence.html
│   ├── 04_LongEngineering.html
│   ├── docs/
│   └── 《AgentOS开源项目准入申请》2(1).pptx
├── 修复工作历史档案/                            # 历史归档
│   ├── 各轮次归档/                              # 各轮次文档归档
│   ├── 改进计划/                                # 14 份历史改进计划
│   ├── 方案归档/                                # 方案归档
│   ├── 旧版文档/                                # 3 份早期版本文档
│   └── 检查报告/                                # 18 份审计检查报告
├── 历史对话/                                    # 长任务历史对话记录
└── 技术借鉴与改进/                              # 技术分析与原型设计
    ├── 分析报告/                                # 6 份技术分析报告
    ├── 历史原型设计/                            # 4 份早期原型设计
    └── 核心模块设计方案/                        # 5 份模块实现方案
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

1. **当前版本文档**（0.1.1）保留在 docs-closed 根目录
2. **历史轮次文档**归档至 `修复工作历史档案/各轮次归档/`
3. **方案/计划/报告**归档至对应的类型子目录
4. **历史对话**独立存放，按需查阅
5. **0.1.1 发布后**，本文档中心将归档至 `修复工作历史档案/各轮次归档/第10轮/`

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
