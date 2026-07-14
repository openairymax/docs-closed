# AgentRT v0.1.1 工程标准规范手册

> **文档版本**: v28.0
> **适用版本**: AgentRT v0.1.1（三大支柱：奠基 + 38 仓拆分 + 生产就绪）
> **适用范围**: Airymax 全项目 38 个 git 仓库（伞仓 airymaxhub + 5 管理仓 agentrt/agentrt-linux/sdk/ecosystem/products + 29 叶子仓 + 3 顶层仓 devtools/docs/docs-closed）
> **最后更新**: 2026-07-06
> **前版**: v25.0 (2026-07-04, 唯一奠基版本工程规范)
>
> **v26.0 变动说明**: v4.0 用户确立 0.1.1 目标扩展为**"奠基 + 29 仓拆分 + 生产就绪"三大支柱**（0.1.1 后直接过渡到 1.0.1，无中间版本，一切以生产就绪为目标）。新增 **第三十六章：29 仓 git 拆分工程规范（SPLIT-01~SPLIT-08）** 和 **第三十七章：生产就绪工程规范（PROD-01~PROD-06）**。关键决策落实：(1) **29 仓 git 拆分**：1 伞仓 + 4 管理仓 + 21 叶子仓 + 3 顶层仓；伞仓 airymaxhub.git 地址 `git@atomgit.com:openairymax/airymaxhub.git`；agentrt 管理仓继承原 AgentRT 仓库 `git@atomgit.com:openairymax/agentos.git` 保留全部 git 历史；sdk 模块下子仓采用 `sdk-xx` 命名；全部目录名小写。(2) **airy_ → agentrt_ 改名彻底**：不留兼容别名头（不生成 `airy_compat_aliases.h`），7 个层面全部直接改（源码目录/CMake target/运行时路径/安装路径/C ABI/C 宏/SDK 包名），涉及 472 个 .c/.h 文件、13037 次 airy_ 前缀。(3) **daemon → daemons 改名**：模块名、目录、CMake target、仓库名统一改名；进程二进制名 `*_d` 保持不变。(4) **5 处跨层耦合解耦**：coreloopthree←daemons/common/checkpoint+orchestrator + coreloopthree←cupolas/yaml_minimal.c + coreloopthree←daemons/hook_d/9 文件 + protocols←daemons/common/safe_string_utils.c + cupolas←gateway。(5) **生产就绪**：CI/CD 全仓 + SBOM + 跨平台打包 + 性能 Soak 72h + 安全审计 + 发布验收。新增 BAN-341~BAN-356 共 16 项 v4.0 BAN 规则（改名彻底 4 项 + 拆分顺序 4 项 + 拆分构建 2 项 + 生产就绪 6 项）。BAN 规则从 340 项扩展为 356 项（+16）。配套：详细任务清单 v2.0 + 技术改进方案 v4.0 + taskflow 对比报告 v1.0。（注：v27.0 已迁移至 38 仓，详见 line 19；本条为 v26.0 历史记录）

### v28.0 变动说明（AirymaxOS Linux 6.6 兼容性规范，v4.2 对应）

- **v28.0 变动**: v4.2 用户确立 AirymaxOS 基于 **Linux 6.6（openEuler 24.03 LTS 内核版本）**，同步 openEuler 内核版本以确保兼容性与稳定性。新增 **IRON-10**（禁止引用 Linux 7.0 专属特性作为 6.6 原生能力）+ **BAN-361**（禁止引用 Linux 7.0 专属特性作为 Linux 6.6 原生能力）+ **ACC-OS04**（Linux 6.6 内核兼容性验证）。IRON 规则从 27 项扩展为 28 项。BAN 规则从 356 项扩展为 357 项。ACC 验收标准从 137 项扩展为 138 项。配套：技术改进方案 v4.2 + 详细任务清单 v2.2。

### v27.0 变动说明（AirymaxOS 前瞻，v4.1 对应）

- **AirymaxOS（agentrt-linux）决策（用户决策 2026-07-06）**: agentrt-linux 正式全称 "AirymaxOS"（极境智能体操作系统），与 agentrt（AirymaxAgentRT / 极境智能体运行底座平台工程）同级的**管理仓**，伞仓直属。基于 Linux 内核的发行版级别研究项目，全面采用**微内核设计思想**（参考 seL4 / Zircon / Minix3），全面参考 openEuler 模块设计、技术规格、标准和规范，兼容 Euler 标准。agentrt 和 AirymaxOS **同源**（共享 Airymax 设计理念），agentrt 在 AirymaxOS 上运行**天然更稳健和适配**（架构同源，无适配层）。天然云原生亲和力（对标 Ubuntu/openEuler）。
- **8 子仓设计（基于微内核设计思想 + openEuler 标准 + Airymax 同源）**: 每个子仓明确对应 agentrt 模块：(1) airymaxos-kernel 复用 atoms/corekern (2) airymaxos-services 复用 daemons (3) airymaxos-security 复用 cupolas (4) airymaxos-memory 复用 heapstore+memoryrovol (5) airymaxos-cognition 复用 coreloopthree+frameworks (6) airymaxos-cloudnative 复用 gateway+sdk (7) airymaxos-system 复用 commons (8) airymaxos-tests-linux 复用全模块测试。基于 2026-07-06 CS 最新理论。
- **仓库总数变更**: 29 仓 → **38 仓**（+9）。1 伞仓 + 5 管理仓 + 29 叶子仓 + 3 顶层仓。
- **OS 文档位置决策**: OS 设计文档全部在 `docs/AirymaxOS/` 模块内（含 12 个设计文档），RT 文档继续在 `docs-closed/`，物理分开。
- **新增 IRON-9 v2 工程铁律**（2026-07-07 变更）: agentrt 和 AirymaxOS **同源且部分代码共享**。三层共享模型：[SC] 共享契约层（`include/airymax/` 6 个头文件完全共享：memory_types.h / security_types.h / cognition_types.h / sched.h / ipc.h / syscalls.h；另含补充共享文件 bpf_struct_ops.h，非 [SC] 核心头文件）+ [SS] 语义同源层（API 签名同源，实现独立）+ [IND] 完全独立层。agentrt 保持跨平台用户态纯净，AirymaxOS 是完整发行版。代码共享边界澄清：代码共享仅限于 agentrt 与 agentrt-linux 之间，与 Euler 项目仅技术参考，不共享代码。AirymaxOS 工程思想与 Euler 保持一致性（协议层 + 接入层 + 模块化 + 工具链兼容），以便未来兼容 Euler 标准的发行版工具链。
- **新增第三十八章：AirymaxOS（agentrt-linux）工程规范**。
- **新增 BAN-357~BAN-360（4 项）**: AirymaxOS 仓库占位/OS 文档分离/内核态污染/子仓命名。BAN 规则从 356 项扩展为 360 项。
> **v25.0 变动说明**: v3.5 用户确立 **0.1.1 是唯一奠基版本**（无 0.1.2/0.2.0/0.3.0 计划，直接过渡到 1.0.1），所有架构、标准、许可证、质量和生态工作必须在 0.1.1 内完成。新增**第三十五章：奠基性版本工程规范（FOUND-01~FOUND-10）**，含 5 大核心决策的工程规范落实：(1) **CoreKern 精简方案 C**（FOUND-01/02）：从 7,522 行精简至 ~4,000 行的硬性行数约束 + 5 类移出范围清单 + ops 钩子保留原则；(2) **taskflow 双引擎协同方案**（FOUND-03/04）：A/B 类语义重新分类规范 + 6 类 BUG 修复规范 + 0.1.1 强制 max_workers=1 降级约束；(3) **SDK 双层 API 4 语言**（FOUND-05/06）：4×4 嵌套客户端矩阵规范 + L1 C ABI + L2 语言原生包装双层架构；(4) **AGPL v3 + Apache 2.0 双许可证**（FOUND-07）：SPDX 表达式 `AGPL-3.0-or-later OR Apache-2.0` 强制规范 + 版权人 SPHARX Ltd. 统一；(5) **静态分析基线**（FOUND-08/09）：lizard v1.23.0 CCN 阈值 + 重复检测器阈值 + 拆分操作规范；(6) **唯一奠基版本工程铁律**（FOUND-10）：禁止新特性、禁止桩函数、禁止绕开功能限制、禁止简化功能。新增 BAN-328~BAN-340 共 13 项 v3.5 BAN 规则。BAN 规则从 327 项扩展为 340 项（+13）。配套：详细任务清单 v1.7.0 + 技术改进方案 v3.5 + taskflow 对比报告 v1.0。
> **v24.7 变动说明**: v3.4 用户 7 项关键决策落实。(1) **第三十三章 ARC-01~ARC-08 方案 A 修正**：原方案 B（物理迁移 coreloopthree/frameworks/taskflow 到 daemons 层）已否决，改为方案 A（接口反转）——引入 ops 抽象表（`airy_checkpoint_ops_t`/`airy_hook_ops_t`/`airy_orch_ops_t`），daemons init 时注入，atoms 文件物理位置不变，消除全部 17 处反向依赖。taskflow 保留在 atoms（是通用 Pregel/DAG 核心原语）。BAN-313/315 撤销，新增 BAN-319（ops 注入点为空时优雅降级）。(2) **新增第三十四章（开放标准规范 STD-01~STD-08）**：覆盖 SDK 双层 API、IPC 128 字节消息头、服务发现多后端适配器、JSON-RPC 命名空间、统一错误码、ARE Standards 三层标准、独立仓库可行性、开放标准 BAN 规则（BAN-320~BAN-327）。(3) **新增 LOG-26 全功能统一打印/日志系统定义**。BAN 规则从 318 项扩展为 327 项（+9）。
> **v24.6 变动说明**: v3.3 综合审计。新增第三十二章（开源许可证规范 LC-01~LC-08，覆盖 ~~AGPL v3 + Apache 2.0 + SPHARX-Proprietary 三许可证体系~~ → **v25.0 已修正为 AGPL-3.0-or-later OR Apache-2.0 双许可证**）和第三十三章（微内核架构规范 ARC-01~ARC-08，覆盖 atoms 边界、反向依赖禁止、层级倒置修复）。许可证变更由用户明确决策（版权归属人 SPHARX Ltd.），为 v0.1.1 发行前阻断性最高优先级任务。架构规范源自 v3.3 三轮审计发现 atoms 层非真正微内核（corekern 仅 15K LOC 而 atoms 总计 84K LOC，coreloopthree 50K LOC 应上移）。
> **v24.5 变动说明**: v3.2 二次验证修正。更新统一打印/日志系统实际数据（统一率 98.2%，~3150 统一调用 vs ~58 裸调用，打印完整度 82%，日志完整度 62%）。5 项缺陷已修复降级（A1/A5/F1/F2/G1 REFUTED），新增 PRT-16~PRT-18（protocols 模块迁移、atoms/memory 迁移、heapstore_migration 迁移）和 LOG-21~LOG-25（异步日志连通、JSON 格式化、syslog 后端、时间轮转、监控数据采集）。
> **v24.3 变动说明**: 新增 5 条工程教训 L-49~L-53（源自 .gitignore 系统性更新、AgentOS→AgentRT 改名方案执行核查、任务状态一致性审查）。涵盖 IDE 配置排除规范、跨子仓库改名同步、TypeScript SDK 包名遗漏、任务状态三文档一致性、配置文件标题品牌统一五项新教训。
> **v24.2 变动说明**: 适配三智能体团队并行执行模型。新增第二十一章（智能体协作规范：合约文件规范、@owner 注解、BAN 规则自动修复策略、防冲突机制）；新增第二十二章（SLO/Error Budget 定义 + Soak Test 分层执行 L1/L2/L3）；新增第二十三章（负载测试规范：5 种场景）；BAN-254 从单一 24h soak test 改为分层执行（4h PR / 24h 每周 / 72h 发布前）。

---

## 第一章：总则

### 1.1 核心哲学

> **每一条写在规范文档里的规则，都必须有对应的自动化工具来强制执行。**
> 违反规则 = 编译失败 或 CI 红灯。不存在"建议遵守"这种灰色地带。

> **连接即功能。** v0.1.1 的核心任务不是"新建模块"，而是将已有 12 个 daemon 和 atoms 子系统完成端到端连接。每条连接线必须有集成测试证明其功能正确。

> **先连接已有资产，再补齐缺失能力。** 源代码审计揭示了 18 项参考项目资产中 12 项（67%）已实现。0.1.1 的战略重心是"连接"，而非"重建"。

> **规范的目的不是限制，是防止已知错误重演。** 每一条 BAN 规则背后都有至少一次实际发生的生产事故或审计发现。

v0.1.0 的核心哲学全数继承：
- **内存安全不是功能，是地基。**
- **每一个核心创新必须有对应的编码契约。**
- **术语不一致是系统性风险的温床。**
- **宣称完成 = CI 绿灯 + 集成测试通过 + 验收标准达标。**

### 1.2 v0.1.0 四层自动化铁律体系（全数继承）

```
Layer 1: 编译期      -Werror + banned_functions.h  → 违规代码不可编译
Layer 2: 静态分析    clang-tidy + cppcheck + eslint → 违规被扫描发现
Layer 3: 预提交检查  pre-commit hooks              → 违规阻止 git commit
Layer 4: CI 门禁     quality-gate.sh + BAN rules   → 违规阻止 PR 合并
```

### 1.3 v0.1.1 新增：三层集成验证体系

```
Layer 5: 连接验证    12 条连接线集成测试           → 端到端数据流验证
Layer 6: 协议验证    A2A/MCP/OpenAI 端到端测试     → 协议互操作验证
Layer 7: 发布验证    67 项 ACC 验收标准             → 全量发布就绪检查
```

### 1.4 版本路线图

| 版本 | 里程碑 | 规范等级 |
|------|--------|---------|
| v0.1.0 | 代码质量加固完成（beta） | 四层自动化铁律体系 |
| **v0.1.1** | **唯一奠基版本（行业底层可投产平台）** | **四层 + 三层集成验证 + ACC 137项 + W01-W30 + FOUND-01~FOUND-10** |
| **v1.0.1** | **正式生产（直接过渡，无 0.2.0/0.3.0）** | **零例外、零豁免 + 全部 BAN 规则 strict 模式** |

> **v25.0 路线图修正**（用户决策）: 0.1.1 是唯一的奠基版本，所有架构、标准、许可证、质量和生态工作必须在 0.1.1 内完成。无 0.1.2/0.2.0/0.3.0 计划，0.1.1 完成后直接过渡到 1.0.1 正式生产版本。原 v0.2.0/v1.0.0 路线图废止。

### 1.5 团队三权分立（v0.1.1 新增）

| 团队 | 位置 | 职责 | 代码范围 |
|------|------|------|---------|
| **团队A（核心引擎）** | C 核心层 | atoms/、cupolas/、daemons/、MemoryRovol 桥接 | `agentos/atoms/`、`agentos/cupolas/`、`agentos/daemons/`、`MemoryRovol/` |
| **团队B（生态+SDK）** | 生态层 + 网关 | ecosystem/、sdk/、gateway/、heapstore/ | `ecosystem/`、`sdk/`、`agentos/gateway/`、`agentos/heapstore/`、`agentos/protocols/` |
| **团队C（基础设施）** | CI/CD + 部署 + 质量 | deploy/、scripts/、tests/、文档 | `deploy/`、`scripts/`、`tests/`、`Docs/` |

**非交叉原则**：
- 同一文件只属于一个团队。不得出现"团队A和团队B同时修改同一个.c文件"。
- 交叉点通过"接口契约"解耦：团队A定义头文件接口 → 团队B实现调用方 → 团队C编写集成测试。
- 每个团队有独立的 CI job，互不依赖对方的构建结果。

### 1.6 术语强制规范

本手册所有术语以 [10-terminology.md](../Docs/10-terminology.md) v4.0 为唯一权威源。以下为高频易错术语的强制对照：

| 标准名称 | 标准英文 | 代码前缀 | 禁止使用的旧称 |
|---------|---------|---------|---------------|
| 原子核心 | CoreKern | `airy_*` | "原子内核" |
| 三层认知循环 | CoreLoopThree | `airy_*` | "第三循环内核"、"三层循环运行时"、"三层一体架构" |
| 记忆卷载 | MemoryRovol | `airy_*` | "记忆漩涡引擎" |
| 安全穹顶 | Cupolas | `cupolas_*` | "Cupolas安全模块" |
| 用户态服务层 | Daemon | `*_d` 进程 | "守护进程"、"后端服务层"、"daemon进程" |
| 微核心 | MicroCoreRT | `airy_*` | "微内核"、"Microkernel" |
| 双思考系统 | Thinkdual | `tc_*`/`mc_*`/`sc_*` | "认知双思系统"、"双系统认知模型" |
| 任务流引擎 | TaskFlow | `airy_*` | — |
| 系统调用层 | AirymaxSyscall | `airy_sys_*` | "Syscall Layer" |
| 多智能体协作框架 | MAC | `mac_*` | "Multi-Agent System" |
| 分时推理框架 | TimeSliceInfer | `ts_*` | "时间切片推理" |
| 记忆交换算法 | MemorySwap | `airy_*` | — |
| 协议适配层 | Protocols | — | — |
| 统一错误码体系 | ErrorCodeSystem | `AIRY_E*` | — |

### 1.7 架构原则→章节映射

本手册每条规范均可追溯到 [00-architectural-principles.md](../Docs/00-architectural-principles.md) 的 24 条核心原则：

| 原则 | 编号 | 本手册对应章节 |
|------|------|-------------|
| 反馈闭环 | S-1 | §4.8 错误链、§16 可观测性 |
| 层次分解 | S-2 | §4.9 目录模板、§11 目录重组 |
| 总体设计部 | S-3 | §1.5 团队三权分立 |
| 涌现性管理 | S-4 | §2 历史教训 |
| 内核极简 | K-1 | §4.1 内存管理 |
| 接口契约化 | K-2 | §4.10 API/ABI 管理、§4.11 函数设计 |
| 服务隔离 | K-3 | §1.5 团队三权分立 |
| 可插拔策略 | K-4 | §4.12 策略模式 |
| 认知层双思考 | C-1 | §9 LLM 路由（Smart Model Routing） |
| 增量演化 | C-2 | §4.13 增量规划 |
| 记忆卷载 | C-3 | §13 MemoryRovol |
| 遗忘机制 | C-4 | §13.6 遗忘机制 |
| 安全内生 | E-1 | §4.5 安全编码、§15 安全规范 |
| 可观测性 | E-2 | §16 可观测性 |
| 资源确定性 | E-3 | §4.1 内存管理、§4.7 AgentRT 安全宏 |
| 跨平台一致性 | E-4 | §4.6 CROSS 跨平台规范 |
| 命名语义化 | E-5 | §11.3 命名规范 |
| 错误可追溯 | E-6 | §4.2 错误处理、§4.8 错误链、§4.14 错误消息模板 |
| 文档即代码 | E-7 | §4.11 函数设计（Doxygen） |
| 可测试性 | E-8 | §12 测试规范 |
| 简约至上 | A-1 | §4.15 复杂度度量 |
| 极致细节 | A-2 | §4.14 错误消息模板 |
| 人文关怀 | A-3 | §6.5 TUI 架构 |
| 完美主义 | A-4 | §4.6 编译硬化、§12 测试规范 |

---

## 第二章：历史教训全面回顾

### 2.1 v0.1.0 教训继承（L-01 ~ L-38，190 条 BAN 规则全数保留）

| 编号 | 教训 | 0.1.1 关联 |
|------|------|----------|
| L-01 | "宣称完成但实际未完成" | → ACC 67 项硬性验收标准 |
| L-15 | "CI 全绿的假象"（`|| true` 质量欺诈） | → ACC-OP51 CI/CD 7 教训 |
| L-17 | "集成是最大的谎言"（代码存在 ≠ 连接正常） | → 12 条连接线集成测试 |
| L-20 | "IDE 错误是编译错误的预告" | → clang-tidy 增量检查保留 |
| L-24 | "日志系统三重混乱" | → daemons 统一 SVC_LOG_* 保留 |
| L-25 | "错误处理无上下文" | → BAN-073/074 错误上下文保留 |
| L-26 | "桩函数与简化实现是生产的定时炸弹" | → BAN-01~13 桩函数禁止保留 |
| L-27 | "核心创新已实现，但缺乏集成验证" | → 12 条连接线专为此设计 |
| L-29 | "外部参考项目吸收缺乏规范指导" | → 命名隔离策略（v2.3 Ch2.3） |
| L-30 | "内存安全审计揭示系统性风险" | → BAN-151~BAN-162 内存安全保留 |
| L-31~L-38 | CI/CD 7 教训 | → §3.1 CI/CD 规范 |

### 2.2 v0.1.1 新增教训（L-39 ~ L-53）

| 编号 | 教训 | 来源 | 0.1.1 应用 |
|------|------|------|----------|
| **L-39** | "方案制定阶段必须进行源代码审计" | v2.1→v2.2 修正 | 任何设计方案前必须审计实际代码状态 |
| **L-40** | "阶段间依赖必须先于开发验证" | v2.2→v2.3 修正 | Phase 1 的 C-L05 依赖 Phase 2 的 Hook 系统 → 重新排序 |
| **L-41** | "验收标准必须覆盖全部任务，无遗漏" | v2.2 评估 | 发现 TUI/CI/CD/设计哲学/MemoryRovol 验收缺失 → 补至 63 项 |
| **L-42** | "非交叉原则防止团队责任模糊" | 09 看板经验 | 三团队三权分立，同一文件只属一个团队 |
| **L-43** | "Hook 系统必须 fail-open" | atomcode 审计 | Hook 超时/崩溃时默认放行，记录审计日志 |
| **L-44** | "LLM 错误必须结构化分类" | hermes-agent 审计 | 错误分类器 14 类 + 恢复提示 |
| **L-45** | "配置中的敏感信息必须 SecretRef" | openclaw 审计 | SecretRef 三种提供者：env/file/exec |
| **L-46** | "Plugin 权限声明必须与运行时行为一致" | claude-code + atomcode 审计 | Plugin manifest permissions 与 Cupolas SafetyGuard 守卫类型对应 |
| **L-47** | "记忆提取必须遵守原子性规则" | agent-memory-demo 审计 | 7 条记忆提取规则写入 Prompt 模板 |
| **L-48** | "SSE 流式传输必须支持背压和取消" | openJiuwen 审计 | AsyncStreamQueue + StreamEmitter + 取消信号 |
| **L-49** | ".gitignore 必须排除所有 IDE 配置目录" | .gitignore 系统性更新审查 | 所有仓库（开源+闭源）的 .gitignore 必须包含 `.trae/`、`.vscode/`、`.idea/` 等 IDE 配置排除；新增子仓库时必须同步配置 |
| **L-50** | "改名方案的跨子仓库同步最易遗漏" | AgentOS→AgentRT 改名执行核查 | 改名方案必须包含跨子仓库同步检查清单（Desktop/Docker/Docs/MemoryRovol/DocsClosed），每子仓库逐一验证品牌引用 |
| **L-51** | "多语言 SDK 改名必须覆盖所有包管理配置" | TypeScript SDK 包名遗漏 | 改名方案必须显式列出所有语言的包配置文件：pyproject.toml/Cargo.toml/go.mod/package.json，TypeScript npm 包名易被忽略 |
| **L-52** | "任务状态必须在三文档中保持一致" | P3.6~P3.10 状态标记矛盾 | 任务看板、详细任务清单、验收标准三文档的状态标记必须一致；子任务全 [x] 但总体 ⚠️ 属于逻辑矛盾，必须修正 |
| **L-53** | "配置文件标题必须与项目品牌统一" | Docker/.gitignore 标题未统一 | 所有配置文件（.gitignore、Dockerfile、docker-compose.yml 等）的标题注释必须与当前项目品牌一致，改名后必须同步更新 |

---

## 第三章：CI/CD 流水线规范

### 3.1 v0.1.0 7 个 CI/CD 关键教训的标准化应用

#### 教训1：Shell 脚本便携性 — `head -z` 全面消除

**BAN-191**：禁止使用 `head -z` 管道。替代为 `while IFS= read -r -d ''` 循环。

```bash
# ❌ 禁止 — macOS 的 head 不支持 -z
find . -name "*.c" -print0 | head -z -100

# ✅ 正确 — POSIX 兼容
local count=0
while IFS= read -r -d '' file; do
    [[ $count -ge 100 ]] && break
    ((count++)) || true
done < <(find . -name "*.c" -print0)
```

**检测方式**：`quality-gate.sh` 中 `grep -qP "head\s+-z" "$file"` 扫描。

#### 教训2：安全扫描正则精准化

**BAN-192**：安全扫描中禁止使用未经充分测试的宽泛正则。所有正则必须经过误报测试。

禁止模式：`[A-Za-z0-9+/]{40,}={0,2}`（Base64 超敏感匹配）
保留模式：`AKIA[0-9A-Z]{16}`、`password\s*=...`、`api_key\s*=...`

**检测方式**：`security_check.py` 中内置误报测试用例，每次运行先执行误报测试。

#### 教训3：危险函数扫描使用词边界

**BAN-193**：危险函数扫描必须使用 Perl 正则 `\b` 词边界，禁止直接 `grep "strcpy("`。

```bash
# ❌ 禁止 — 误匹配 safe_strcpy
grep -q "strcpy(" "$file"

# ✅ 正确 — 词边界精确匹配
grep -qP "\bstrcpy\s*\(" "$file"
```

**检测方式**：`ban_scan.sh` 使用 `grep -P "\b(banned_func)\s*\("` 模式。

#### 教训4：CI 质量门禁统一入口

**规范**：`quality-gate.sh` 作为唯一质量门禁入口。CI 中 `quality-gate` job 的失败直接导致 `result` job 失败。

**检测方式**：CI yaml 审计 — `quality-gate` job 必须出现在 `result` job 的 `needs` 列表中。

#### 教训5：`continue-on-error` 零容忍

**BAN-194**：任何构建依赖步骤（`npm ci`、`pip install`、`cmake`、`make`）不得使用 `continue-on-error: true`。仅可选步骤（如 coverage 上报）允许使用，且必须注释说明原因。

**检测方式**：CI yaml 审计脚本 `check_ci_yaml.py`。

#### 教训6：Feature Test Macros 必须 CMake 级定义

**BAN-195**：`_GNU_SOURCE`、`_POSIX_C_SOURCE`、`_XOPEN_SOURCE` 必须在 `CMakeLists.txt` 中通过 `add_compile_definitions()` 定义，禁止在源文件中 `#define`。

**检测方式**：`check_feature_macros.sh` 扫描源文件中的 `#define _GNU_SOURCE` 等。

#### 教训7：错误码统一注册

**BAN-196**：所有错误码必须在 `airy_types.h` 的 `airy_err_t` 中注册，禁止局部 `#define`。

**检测方式**：`check_error_codes.sh` 扫描 `#define AIRY_E` 并与 `airy_types.h` 交叉校验。

### 3.2 v0.1.1 团队专用 CI Job

```
ci.yml
├── team-a-build          (团队A: atoms/ + cupolas/ + daemons/ + memoryrovol/)
├── team-b-build          (团队B: ecosystem/ + sdk/ + gateway/ + protocols/)
├── team-c-build          (团队C: tests/ + deploy/ + scripts/)
├── connection-tests      (12 条连接线集成测试，依赖 team-a-build + team-b-build)
├── protocol-tests        (A2A/MCP/OpenAI 端到端测试)
├── ban-scan-all          (BAN-001~BAN-256 全量扫描)
├── clang-tidy-incremental(增量静态分析)
├── quality-gate          (quality-gate.sh --strict)
├── python-checks         (ecosystem/ Python 规范)
├── rust-checks           (sdk/cli/ + sdk/tui/ Rust 规范)
├── go-checks             (sdk/go/ Go 规范)
├── principles-compliance (架构原则合规性检查)
└── result                (汇总全部 job，任一失败则 CI 失败)
```

### 3.3 CI Job 依赖关系

```
team-a-build ─────────────────┐
team-b-build ─────────────────┼── connection-tests ──┐
team-c-build ─────────────────┤                      │
                              │                      ▼
ban-scan-all ─────────────────┼── quality-gate ──────┼── result
clang-tidy-incremental ───────┤                      │
python-checks ────────────────┤                      │
rust-checks ──────────────────┤                      │
go-checks ────────────────────┤                      │
principles-compliance ────────┘                      │
protocol-tests ──────────────────────────────────────┘
```

### 3.4 Pre-commit 钩子规范（源自 C 编码标准）

**规范**：必须配置以下 pre-commit 钩子：

| 钩子 | 功能 | 阻断条件 |
|------|------|---------|
| `clang-format` | C/C++ 代码格式化 | 格式不一致 |
| `license-header-check` | 版权头检查 | 缺少版权头 |
| `shellcheck` | Shell 脚本检查 | shellcheck 警告 |
| `commit-msg` | Conventional Commits 格式 | 格式不合规 |
| `ruff format` | Python 代码格式化 | 格式不一致 |
| `cargo fmt --check` | Rust 代码格式化 | 格式不一致 |

### 3.5 Conventional Commits 规范

**规范**：所有提交必须遵循 Conventional Commits 格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

| type | 含义 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复 |
| `refactor` | 重构 |
| `docs` | 文档 |
| `test` | 测试 |
| `chore` | 构建/工具 |
| `perf` | 性能 |
| `style` | 格式化（不影响功能） |

**规范**：格式化提交与功能提交必须分离（L-38 教训）。

### 3.6 发布流程规范

| 阶段 | 触发条件 | 执行内容 |
|------|---------|---------|
| 开发验证 | 每次 push | team-a/b/c-build + ban-scan + clang-tidy |
| PR 合并 | PR 创建/更新 | 全量 CI + connection-tests + protocol-tests |
| 候选发布 | tag `v0.1.1-rc.*` | 全量 CI + 67 项 ACC 验收 + 性能基准 |
| 正式发布 | tag `v0.1.1` | 全量 CI + 67 项 ACC 验收 + SBOM 生成 + 签名 + Docker 镜像发布 |

### 3.7 硬编码路径预防规则（v24.1 新增，源自 v2.5 §3.5）

> **背景**: 对 AgentRT 子仓库全量源代码进行硬编码路径审计后，发现 5 处轻度泄露（SpharxWorks 标识符），无严重本地开发路径泄露。为防止未来引入，新增以下强制规则。

#### PATH-BAN-1~PATH-BAN-5 硬编码禁止规则

| 规则 | 内容 | 检测方式 |
|------|------|---------|
| **PATH-BAN-1** | 禁止在源代码中硬编码形如 `/home/<user>/`、`C:\Users\<user>\`、`D:\SPHARX-CN\` 的绝对路径 | CI grep 扫描（`quality-gate.sh` 的 `[PATH-SCAN]` 步骤） |
| **PATH-BAN-2** | 所有运行时路径必须通过 `agentrt.yaml` 配置或 `commons/path_manager.h` 获取，禁止硬编码 | Code review |
| **PATH-BAN-3** | CMake 跨子仓库引用必须使用 `get_filename_component` 相对推导，不得硬编码 `../agentrt/` 等 | CI CMake 审计 |
| **PATH-BAN-4** | 禁止在 git commit 中包含本机用户名或主机名 | pre-commit hook |
| **PATH-BAN-5** | `.env` 和 `.env.example` 中的路径必须使用相对路径或环境变量占位符 | pre-commit hook |

**检测方式**：`quality-gate.sh` 中的 `[PATH-SCAN]` 步骤扫描以下禁止模式：

```bash
# 硬编码路径泄露扫描（集成在 quality-gate.sh 中）
echo "[PATH-SCAN] Scanning for hardcoded dev paths..."
FORBIDDEN_PATTERNS=(
    '/home/[a-z]+/project'     # Linux home dirs
    '/Users/[a-z]+/project'    # macOS home dirs
    'C:\\\\Users\\\\'           # Windows user dirs
    'D:\\\\SPHARX'             # Dev machine specific
    'SpharxWorks'              # Dev workspace name
)
for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
    matches=$(grep -rn "$pattern" --include="*.c" --include="*.h" --include="*.py" \
              --include="*.sh" --include="*.rs" --include="*.go" agentos/ 2>/dev/null | \
              grep -v "path_manager\|path_scan\|FORBIDDEN_PATTERNS" || true)
    if [ -n "$matches" ]; then
        echo "[PATH-SCAN] FAIL: Hardcoded path detected:"
        echo "$matches"
        exit 1
    fi
done
echo "[PATH-SCAN] PASS: No hardcoded dev paths found"
```

**审计结果（2026-06-14）**：

| 类别 | 发现数 | 示例 | 风险 | 处理 |
|------|:---:|------|:---:|------|
| A: 本地开发路径泄露 | 5 | Rust `AUTHOR = "SpharxWorks"`、Python `author="SpharxWorks"`、Go `Author = "SpharxWorks"` | 极低（仅为作者/元数据字段） | 改为 `"SPHARX Ltd."` |
| B: Unix 运行时路径 | 8 | `/var/lib/agentos/`、`/var/log/agentos/`、`/opt/` | 正常（运行时标准路径） | 保留，Windows 通过 `path_manager.h` 映射 |
| C: CMake 相对路径 | 全部 | `get_filename_component`、`${CMAKE_CURRENT_SOURCE_DIR}` | 正常（构建系统标准） | 保留 |
| D: `#include` 内部路径 | 全部 | `#include "agentos/commons/..."` | 正常（项目内相对路径） | 保留 |

**规范**：CI 中 `quality-gate` job 必须包含 `[PATH-SCAN]` 步骤，任何硬编码路径匹配均视为 CI 失败。

---

## 第四章：C 语言核心代码规范

> **说明**：本章整合 [C_coding_style_standard.md](../Docs/50-specifications/30-coding-standard/01-c-coding-style.md) 和 [C_Cpp_secure_coding_standard.md](../Docs/50-specifications/30-coding-standard/02-c-cpp-secure-coding.md) 的全部规范。BAN-001~BAN-074、CROSS-01~CROSS-06、REQ-01~REQ-08 全数纳入。

### 4.1 内存管理（BAN-001~BAN-030 + BAN-246~BAN-255）

> **设计哲学**：内存安全不是功能，是地基。借鉴 Linux 内核（slab/mempool）、seL4（能力模型）、OpenBSD（guard page/零化释放）、Fuchsia/Zircon（VMO 句柄模型）的最佳实践，建立 AgentRT 五层内存管理体系。

#### 4.1.1 核心分配规则（BAN-001~BAN-006）

- **BAN-001**：禁止裸 `malloc`，统一使用 `AIRY_MALLOC`
- **BAN-002**：禁止裸 `free`，统一使用 `AIRY_FREE`
- **BAN-003**：`AIRY_MALLOC(count * sizeof(...))` 必须有溢出检查（BAN-151）
- **BAN-004**：`strncpy` 必须后置 null 终止（BAN-152）
- **BAN-005**：`memcpy` 动态长度必须有前置校验（BAN-153）
- **BAN-006**：错误路径必须释放已分配内存（BAN-154）

#### 4.1.2 内存分配器体系（三层架构）

AgentRT 采用三层分配器架构，各层职责明确：

```
┌─────────────────────────────────────────────────────────┐
│ Layer 3: 应用层分配器                                     │
│  • arena_alloc/arena_reset  — 请求作用域零碎片分配        │
│  • airy_mem_pool_alloc   — 固定大小块池分配            │
│  • airy_slab_alloc       — 对象缓存（构造/析构复用）    │
│  • AIRY_MALLOC/FREE      — 通用分配（回退到 Layer 2）  │
├─────────────────────────────────────────────────────────┤
│ Layer 2: 中间层（memory_compat.h + memory_pool.h）        │
│  • 安全宏封装 + 统计追踪 + 调试标记                       │
│  • 内存池管理（8 字节对齐、双重释放检测、指针归属验证）     │
│  • OOM 水位监控 + 预分配紧急缓冲区                        │
├─────────────────────────────────────────────────────────┤
│ Layer 1: 底层分配器（airy_memory.h + memory.c）        │
│  • 封装标准 C 库 malloc/free/posix_memalign              │
│  • 线程安全锁 + 标签追踪 + 统计上报                       │
│  • memory_stats_reporter 后台线程每 60s 上报              │
└─────────────────────────────────────────────────────────┘
```

**分配器选择规则**：

| 场景 | 推荐分配器 | 理由 |
|------|-----------|------|
| IPC 消息块（高频固定大小） | `airy_slab_alloc` | 对象复用，避免重复构造/析构 |
| 请求作用域临时内存 | `arena_alloc` + `arena_reset` | O(1) 分配/释放，零碎片 |
| 固定大小对象池 | `airy_mem_pool_alloc` | 双重释放检测、指针归属验证 |
| 通用分配 | `AIRY_MALLOC` | 带统计追踪的安全分配 |
| 大块内存（>1MB） | `airy_mem_aligned_alloc` 或 mmap | 避免堆碎片，对齐保证 |
| 敏感数据（密钥/令牌） | `AIRY_MALLOC` + `AIRY_SECURE_ZERO` | 释放前安全清零 |

#### 4.1.3 所有权模型

**规范**：每个内存分配必须有明确的所有权归属，通过 `@ownership` Doxygen 注解标注。

```c
/**
 * @brief 创建 IPC 消息
 * @ownership 返回的指针由调用者拥有，需通过 airy_mem_free() 释放
 */
ipc_message_t *ipc_msg_create(msg_type_t type);

/**
 * @brief 获取代理名称
 * @ownership 返回的指针为借用引用，调用者不可释放
 */
const char *agent_get_name(const agent_t *agent);
```

**所有权传递规则**：

| 模式 | 语义 | 释放责任 |
|------|------|---------|
| `@ownership caller` | 调用者拥有 | 调用者负责释放 |
| `@ownership borrowed` | 借用引用 | 不可释放，所有者负责 |
| `@ownership transfer` | 所有权转移 | 新持有者负责释放 |
| `@ownership shared` | 共享所有权 | 引用计数归零时释放 |

**BAN-246**：函数返回指针必须标注 `@ownership`，未标注视为编译警告。

#### 4.1.4 引用计数规范

**规范**：共享所有权对象必须使用原子引用计数，引用计数结构体置于对象首部。

```c
/* 引用计数对象 — rc 必须在结构体首部 */
typedef struct {
    _Atomic uint32_t refcount;   /* C11 原子引用计数 */
    void (*deleter)(void *);     /* 自定义析构函数 */
} refcounted_t;

/* 使用模式 */
typedef struct {
    refcounted_t rc;             /* 首部 */
    size_t       payload_size;
    uint8_t      data[];
} ipc_shared_buffer_t;

/* retain/release 必须成对 */
ipc_shared_buffer_t *buf = refcount_alloc(sizeof(*buf) + size, free);
refcount_retain(buf);   /* 发送方 +1 */
refcount_retain(buf);   /* 接收方 +1 */
refcount_release(buf);  /* 发送方 -1 */
refcount_release(buf);  /* 接收方 -1 → 触发 free */
```

**BAN-247**：共享内存对象禁止裸 `airy_mem_free`，必须通过 `refcount_release` 释放。

**BAN-248**：引用计数操作必须使用 `_Atomic` + `memory_order_acq_rel`，禁止裸 `++`/`--`。

#### 4.1.5 RAII 模式与资源清理

**规范**：所有函数内分配的资源必须使用 `goto cleanup` 模式或 `__attribute__((cleanup))` 自动清理。

**模式一：goto cleanup（Linux 内核标准，跨平台兼容）**

```c
airy_err_t process_task(task_t *task) {
    char *buffer = NULL;
    ipc_msg_t *msg = NULL;

    buffer = AIRY_MALLOC(BUF_SIZE);
    if (!buffer) goto fail_buffer;

    msg = ipc_msg_create(task->type);
    if (!msg) goto fail_msg;

    /* 正常处理 */
    process(buffer, msg);
    AIRY_FREE(buffer);
    return AIRY_SUCCESS;

fail_msg:
    AIRY_FREE(buffer);
fail_buffer:
    return AIRY_ENOMEM;
}
```

**模式二：AUTO_FREE（GCC/Clang 扩展，编译期自动清理）**

```c
/* 定义在 memory_compat.h 中 */
#define AUTO_FREE __attribute__((cleanup(auto_free_fn)))

airy_err_t safe_handler(void) {
    AUTO_FREE char *buf = AIRY_MALLOC(1024);
    AUTO_FREE char *name = AIRY_STRDUP("agent");

    if (!buf || !name) return AIRY_ENOMEM;

    /* 函数返回时 buf 和 name 自动释放 */
    return process(buf, name);
}
```

**BAN-249**：禁止超过 3 层嵌套的资源分配而不使用 `goto cleanup` 或 `AUTO_FREE`。

#### 4.1.6 OOM 处理规范

**规范**：AgentRT 采用五级内存压力框架（`oom_handler.h`），所有 daemon 必须注册 OOM 降级回调。

| 压力级别 | 内存水位 | 系统行为 |
|---------|---------|---------|
| NORMAL | < 70% | 正常运行 |
| WARNING | 70%~80% | 丢弃非必要缓存，缩减内存池 |
| DEGRADED | 80%~90% | 延迟非关键操作，拒绝低优先级分配 |
| CRITICAL | 90%~95% | 拒绝新请求，紧急 GC，同步 IO |
| FATAL | > 95% | 优雅关机，保存关键状态 |

**OOM 降级回调注册**：

```c
/* 每个 daemon 启动时注册 */
airy_oom_register_callback(WATERMARK_WARNING,  my_daemons_drop_cache);
airy_oom_register_callback(WATERMARK_DEGRADED, my_daemons_defer_ops);
airy_oom_register_callback(WATERMARK_CRITICAL, my_daemons_reject_requests);
airy_oom_register_callback(WATERMARK_FATAL,    my_daemons_graceful_shutdown);
```

**分配失败重试策略**：

```c
/* 带重试的分配 — 关键路径使用 */
void *airy_mem_alloc_with_retry(size_t size, int max_retries) {
    for (int i = 0; i < max_retries; i++) {
        void *ptr = airy_mem_alloc(size);
        if (ptr) return ptr;
        /* 触发 OOM 降级后重试 */
        airy_oom_trigger_recovery(i);
        airy_sleep_ms(10 * (i + 1));  /* 指数退避 */
    }
    return NULL;
}
```

**BAN-250**：daemon 启动时必须注册至少 WARNING 和 CRITICAL 两级 OOM 回调。

**BAN-251**：关键路径（IPC 消息分配）必须使用 `airy_mem_alloc_with_retry` 或预分配缓冲区，不得在 OOM 时直接崩溃。

#### 4.1.7 安全释放与敏感数据清零

**规范**：敏感数据（密钥、令牌、密码）释放前必须安全清零，防止内存残留泄露。

```c
/* 安全释放宏 — 定义在 memory_compat.h */
#define AIRY_SECURE_FREE(ptr, size) do {                    \
    if (ptr) {                                                  \
        __builtin_memset((ptr), 0xFF, (size));                 \
        __builtin_memset((ptr), 0x00, (size));                 \
        __builtin_memset((ptr), 0xFF, (size));                 \
        airy_mem_free(ptr);                                  \
        (ptr) = NULL;                                           \
    }                                                           \
} while (0)
```

**延迟释放检测（use-after-free 防护）**：

```c
/* 调试模式下：释放后填充 0xDA 标记，延迟真正释放 */
#ifdef AIRY_DEBUG
void airy_debug_free(void *ptr, size_t size) {
    __builtin_memset(ptr, 0xDA, size);  /* "Dead Access" 标记 */
    deferred_free_enqueue(ptr, size);    /* 延迟释放队列 */
}
#endif
```

**BAN-252**：敏感数据释放禁止使用 `AIRY_FREE`，必须使用 `AIRY_SECURE_FREE` 或 `AIRY_SECURE_ZERO` + `AIRY_FREE`。

#### 4.1.8 内存对齐与缓存行优化

**规范**：频繁并发访问的数据结构必须按缓存行对齐，避免伪共享（false sharing）。

```c
/* 缓存行对齐 — 避免伪共享 */
typedef struct {
    _Alignas(64) _Atomic uint64_t tx_count;   /* CPU 0 写 */
    _Alignas(64) _Atomic uint64_t rx_count;   /* CPU 1 写 */
} per_cpu_counters_t;

/* 大块内存对齐分配 */
void *ptr = airy_mem_aligned_alloc(size, 64);  /* 64 字节缓存行对齐 */
```

**BAN-253**：并发计数器结构体中，不同线程写入的字段必须 `_Alignas(64)` 分离到不同缓存行。

#### 4.1.9 内存泄漏检测与长时间运行保障

**规范**：所有 daemon 必须通过 24 小时内存泄漏测试（soak test），RSS 增长 < 5%。

**检测工具矩阵**：

| 工具 | 检测能力 | CI 集成 |
|------|---------|---------|
| AddressSanitizer (ASan) | 越界、use-after-free、双重释放 | 每次 PR（已集成） |
| LeakSanitizer (LSan) | 内存泄漏 | 每次 PR（已集成） |
| MemorySanitizer (MSan) | 未初始化内存读取 | CI 独立构建 |
| Valgrind memcheck | 内存泄漏、越界、未初始化 | 每周全量 |
| `airy_mem_check_leaks()` | 运行时泄漏扫描 | 后台每 60s |
| `memory_debug.h` 边界检查 | canary 越界、释放后使用 | Debug 构建 |

**BAN-254**：daemon 24 小时 soak test RSS 增长超过 5% 视为内存泄漏，禁止合并。

**BAN-255**：所有 `AIRY_MALLOC`/`AIRY_FREE` 必须在 `memory_stats_reporter` 统计覆盖内，禁止绕过统计的分配。

### 4.2 错误处理（保留 BAN-073~BAN-085）

- **BAN-073**：禁止 `return -1`，必须使用 `AIRY_E_*` 错误码
- **BAN-074**：错误必须通过 `airy_error_push_ex()` 传播上下文
- **BAN-075**：每个函数必须显式声明和检查返回值

### 4.3 日志系统（保留 BAN-060~BAN-072）

- daemons 层统一使用 `SVC_LOG_*` 宏
- atoms/gateway/protocols 统一使用 `AIRY_LOG_*` 宏
- 全面禁止 `printf`/`fprintf`

### 4.4 禁止模式清单（BAN-01~BAN-13 + BAN-70~BAN-74）

源自 [C_coding_style_standard.md §18](../Docs/50-specifications/30-coding-standard/01-c-coding-style.md)：

| 编号 | 禁止模式 | 检测命令 |
|------|---------|----------|
| BAN-01 | `return AIRY_SUCCESS` 占位返回 | `grep -rn "return AIRY_SUCCESS" --include="*.c"` |
| BAN-02 | `(void)param` 忽略参数 | `grep -rn "(void)" --include="*.c"` |
| BAN-03 | 空函数体 `{}` | 代码审查 |
| BAN-04 | TODO/FIXME 无关联 Issue | `grep -rn "TODO\|FIXME" --include="*.c"` |
| BAN-05 | simplified/placeholder/stub 注释 | `grep -rn "simplified\|placeholder\|stub" --include="*.c"` |
| BAN-06 | `return STRDUP(input)` 回显 | 代码审查 |
| BAN-07 | `(void*)1` 假指针 | 代码审查 |
| BAN-08 | `while(cond){break;}` 假循环 | 代码审查 |
| BAN-09 | `free("literal")` 释放字符串字面量 | `grep -rn 'free("' --include="*.c"` |
| BAN-10 | `*(ptr)=val` 假原子操作 | 代码审查 + TSan |
| BAN-11 | `*_stub.h` 桩头文件 | `find . -name "*_stub.h"` |
| BAN-12 | 降级模式返回假成功 | `grep -rn "degraded\|fallback.*SUCCESS" --include="*.c"` |
| BAN-13 | DUMMY 假数据 | `grep -rn "DUMMY\|dummy" --include="*.c" --include="*.h"` |
| BAN-70 | 直接使用 `printf` 系列输出 | `grep -rn "printf(" --include="*.c" --include="*.h"` |
| BAN-71 | 直接使用 `malloc`/`free` | `grep -rn "\bmalloc\b\|\bfree\b" --include="*.c" --include="*.h"` |
| BAN-72 | 直接使用 `realloc` | `grep -rn "\brealloc\b" --include="*.c" --include="*.h"` |
| BAN-73 | 使用 `strcpy`/`strcat`/`sprintf` | `grep -rn "\bstrcpy\b\|\bstrcat\b\|\bsprintf\b" --include="*.c" --include="*.h"` |
| BAN-74 | 使用 `memset` 清零敏感数据 | `grep -rn "memset.*key\|memset.*password\|memset.*secret\|memset.*token" --include="*.c"` |

### 4.5 AgentRT 安全宏完整列表（源自 memory_compat.h）

所有 C 代码必须优先使用以下安全宏（定义在 `memory_compat.h`）：

| 宏名称 | 功能 | 替代的不安全函数 |
|--------|------|----------------|
| `AIRY_MALLOC(size)` | 带返回值检查的 malloc | `malloc` |
| `AIRY_CALLOC(nmemb, size)` | 带返回值检查的 calloc（零初始化） | `calloc` |
| `AIRY_REALLOC(ptr, size)` | 安全 realloc（使用临时指针，避免原指针丢失） | `realloc` |
| `AIRY_FREE(ptr)` | 安全释放（释放后置 NULL） | `free` |
| `AIRY_STRDUP(s)` | 带返回值检查的 strdup | `strdup` |
| `AIRY_STRNDUP(s, n)` | 带返回值检查的 strndup | `strndup` |
| `AIRY_STRNCPY_TERM(dst, src, dst_size)` | 安全字符串拷贝（保证 null 终止） | `strncpy` |
| `AIRY_MEMCPY_SAFE(dst, dst_size, src, src_size)` | 安全内存拷贝（带边界检查） | `memcpy` |
| `SAFE_MALLOC_ARRAY(type, count)` | 安全数组分配（带整数溢出检查） | `malloc(count * sizeof(type))` |
| `AIRY_SECURE_ZERO(ptr, size)` | 安全内存清零（防止编译器优化，跨平台替代 `explicit_bzero`） | `memset`（用于敏感数据） |

**安全释放宏**（定义在 `airy_memory.h`）：

| 宏名称 | 功能 | 用法 |
|--------|------|------|
| `MEMORY_FREE_SAFE(pptr)` | 安全释放宏，接受**指针的指针**，释放后自动将原指针置 NULL | `MEMORY_FREE_SAFE(&buf)` |

```c
char* buf = AIRY_MALLOC(1024);
// ... 使用 buf ...
MEMORY_FREE_SAFE(&buf);  // 释放并置 buf = NULL
// 此时 buf 一定为 NULL，不会误用
```

### 4.6 跨平台编译规范（CROSS-01~CROSS-06）

源自 [C_coding_style_standard.md §17](../Docs/50-specifications/30-coding-standard/01-c-coding-style.md)：

#### CROSS-01：禁止直接使用 POSIX 线程 API

**违规示例**: `pthread_create()`, `pthread_mutex_lock()`, `pthread_cond_wait()`
**正确做法**: 全部替换为 `platform.h` 提供的 `airy_thread_create()`, `airy_mutex_lock()`, `airy_cond_wait()`

#### CROSS-02：禁止使用 C99 VLA 变长数组

**违规示例**: `int arr[n]`
**正确做法**: `int* arr = AIRY_MALLOC(n * sizeof(int))` + 对应 `AIRY_FREE`

#### CROSS-03：禁止直接使用 POSIX 时间函数

**违规示例**: `clock_gettime(CLOCK_MONOTONIC, &ts)`
**正确做法**: 使用 `airy_time_ns()`, `airy_time_ms()`

#### CROSS-04：禁止使用 GCC 扩展语法

**违规示例**: 嵌套函数指针、语句表达式
**正确做法**: 使用 ANSI C 标准语法

#### CROSS-05：Windows 头文件保护

**违规示例**: `#define NOMINMAX` 缺少 `#ifndef`
**正确做法**: 使用 `#ifndef NOMINMAX` / `#define NOMINMAX` / `#endif` 三行保护

#### CROSS-06：MSVC /WX 级别零警告

**要求**: MSVC 编译必须 `/WX` 标志零警告通过，应移除所有未使用变量和隐式类型转换

### 4.7 强制规范（REQ-01~REQ-08）

源自 [C_coding_style_standard.md §1.2](../Docs/50-specifications/30-coding-standard/01-c-coding-style.md)：

| 编号 | 规范 |
|------|------|
| REQ-01 | 所有公共 API 必须使用 Doxygen 风格注释，明确 ownership、线程语义、错误语义 |
| REQ-02 | 返回值优先使用 `airy_err_t`（int32_t），或返回指针（失败返回 NULL 并记录日志） |
| REQ-03 | 所有资源按 create/destroy 成对管理，API 文档中明确释放责任 |
| REQ-04 | 优先使用 C11 atomics（`stdatomic.h`），避免遗留 `_sync*` |
| REQ-05 | 热路径优先无锁/原子实现，并提供锁保护的安全回退（System 2） |
| REQ-06 | 日志格式使用结构化 JSON，最小字段：`timestamp`、`level`、`module`、`function`、`trace_id`、`request_id`、`message`、`err_code` |
| REQ-07 | 追踪采用 W3C Trace Context（`traceparent`），请求入口生成 `trace_id` |
| REQ-08 | 指标采用 Prometheus exposition 格式，提供 `/metrics`、`/healthz`、`/readyz` 端点 |

### 4.8 错误链规范（源自 ARCHITECTURAL_PRINCIPLES E-6）

**规范**：错误传播必须使用 `airy_error_wrap()` 形成错误链，包含模块名、函数名、行号和附加消息。

```c
/**
 * @brief 包装错误，添加上下文信息形成错误链
 * @param err 原始错误码
 * @param module 模块名
 * @param function 函数名
 * @param line 行号
 * @param message 附加消息
 * @return 包装后的错误链句柄
 */
airy_err_chain_t airy_err_wrap(
    airy_err_t err,
    const char* module,
    const char* function,
    int line,
    const char* message
);
```

**规范**：错误链最终输出时必须格式化显示完整调用栈，便于定位根因。

### 4.9 错误码分段表（源自 10-terminology.md ErrorCodeSystem）

> **SSoT 对齐说明（v4.0 修正）**：本分段表已对齐 SSoT 方案 A（POSIX errno 负值 + 扩展码迁移），权威源为 `agentrt/commons/utils/error/include/error.h`。原 v3.0 的 -1001~-9099 千位分段方案已废止，统一采用百位分段（-1~-99/-100~-199/.../-900~-909）。`AIRY_E*` POSIX 风格码（如 `AIRY_EINVAL=-22`/`AIRY_ENOMEM=-12`/`AIRY_ETIMEDOUT=-110`）权威定义位于 `airy_types.h`（硬定义，无 `#ifndef` 保护）；`AIRY_ERR_*` 扩展码定义位于 `error.h`。v3.0 SSoT 统一收敛将原与 POSIX errno 冲突的扩展码迁移至 -40~-48 区间，将原与 `ECONNRESET`/`ENOTCONN`/`ETIMEDOUT`/`ECONNREFUSED` 冲突的系统码迁移至 -120~-123。

| 段 | 范围 | 用途 | 关键示例 |
|----|------|------|---------|
| 成功 | 0 | `AIRY_EOK`/`AIRY_OK`/`AIRY_SUCCESS`（等价，均定义于 `airy_types.h`） | `AIRY_EOK=0` |
| 通用基础 | -1 ~ -99 | 基础错误（参数/内存/超时等）+ POSIX errno 负值 + -40~-48 扩展迁移码 | `AIRY_EPERM=-1`、`AIRY_ERR_NULL_POINTER=-3`、`AIRY_ERR_INVALID_PARAM=-40`、`AIRY_ERR_BUSY=-48`、`AIRY_ERR_UNKNOWN=-99` |
| 系统与平台 | -100 ~ -199 | 系统与平台错误（含 -120~-123 迁移系统码） | `AIRY_ERR_SYS_BASE=-100`、`AIRY_ERR_SYS_THREAD=-120`、`AIRY_ERR_SYS_CONDITION=-121`、`AIRY_ERR_SYS_PIPE=-122`、`AIRY_ERR_SYS_PROCESS=-123` |
| 内核层 | -200 ~ -299 | 内核层错误（IPC/任务/同步/锁/内存/调度/定时器/中断） | `AIRY_ERR_KERN_BASE=-200`、`AIRY_ERR_KERN_IPC=-201` |
| 服务层 | -300 ~ -399 | 服务层错误（未就绪/忙/停止/配置/依赖/健康/负载均衡） | `AIRY_ERR_SVC_BASE=-300`、`AIRY_ERR_SVC_NOT_READY=-301` |
| LLM/AI 服务 | -400 ~ -499 | LLM/AI 服务错误（无 Provider/Provider 失败/限流/上下文/模型/鉴权/Token/解析/空响应/成本） | `AIRY_ERR_LLM_BASE=-400`、`AIRY_ERR_LLM_NO_PROVIDER=-401` |
| 执行/工具 | -500 ~ -599 | 执行/工具错误（未找到/失败/超时/校验/沙箱/权限/参数/环境） | `AIRY_ERR_EXEC_BASE=-500`、`AIRY_ERR_EXEC_NOT_FOUND=-501` |
| 记忆/存储 | -600 ~ -699 | 记忆/存储错误（写/读/查询/演化/满/损坏/未初始化） | `AIRY_ERR_MEM_BASE=-600`、`AIRY_ERR_MEM_WRITE=-601` |
| 安全/沙箱 | -700 ~ -799 | 安全/沙箱错误（含 Cupolas 安全穹顶 -712~-799 专属段） | `AIRY_ERR_SEC_BASE=-700`、`AIRY_ERR_CUPOLAS_BASE=-712`、`AIRY_ERR_CUPOLAS_DENIED=-713` |
| 协调/规划 | -800 ~ -899 | 协调/规划错误（计划失败/同步失败/调度/意图/补偿/重试超限） | `AIRY_ERR_COORD_BASE=-800`、`AIRY_ERR_COORD_PLAN_FAIL=-801` |
| 协议/校验 | -900 ~ -909 | 协议/校验错误（IPC 消息头校验/CRC32 校验和，消息必须丢弃） | `AIRY_ERR_PROTOCOL=-900`、`AIRY_ERR_CHECKSUM=-901` |

**BAN-231**：新增错误码必须在其所属分段范围内注册，禁止跨段分配。

**检测方式**：`check_error_codes.sh` 验证错误码在正确分段内。

### 4.10 API/ABI 管理规范（源自 C 编码标准 §5）

**规范**：公共头文件顶部必须声明 API 版本宏：`#define MODULE_API_VERSION 1`

**规范**：相同 MAJOR 版本内保证 ABI 兼容；破坏性更改需递增 MAJOR 并发布迁移说明。

**规范**：优先使用不透明指针（opaque types）作为导出类型，避免直接暴露结构字段。

**规范**：Release 构建必须启用 `-fvisibility=hidden` 并显式导出公共符号。

**规范**：每个公共 API 注释必须包含 `@since`（引入版本）和 `@deprecated`（弃用版本及替代方案）。

**规范**：弃用接口需保留至少两个次要版本，并在编译时产生警告。

### 4.11 函数设计规范（源自 C 编码标准 §6）

**规范**：函数必须 ≤80 行；推荐 ≤50 行。若 >80 行必须重构并添加单元测试。

**规范**：参数数量不超过 5 个，若超过请封装成结构体。

**规范**：公共 API 必须使用 Doxygen 风格注释，且明确 ownership（谁释放）、线程语义与错误语义。

```c
/**
 * @brief 提交计划并返回任务 ID。
 * @param engine [in] 引擎句柄（非 NULL）。
 * @param plan   [in] 待调度计划（只读）。
 * @param out_id [out] 输出任务 ID（调用者负责 free）。
 * @ownership out_id 由调用者释放
 * @threadsafe 否
 * @return AIRY_EOK (0) 成功；其他值为错误码。
 * @since v0.1.0
 */
int cognition_schedule(cognition_engine_t* engine,
                       const task_plan_t* plan,
                       char** out_id);
```

### 4.12 策略模式规范（源自 ARCHITECTURAL_PRINCIPLES K-4）

**规范**：所有可插拔策略必须实现统一的三函数模式：

```c
struct airy_plan_strategy {
    airy_plan_func_t plan;       /* 核心算法函数 */
    airy_plan_destroy_t destroy; /* 资源释放函数 */
    void* data;                     /* 私有数据指针 */
};
```

**规范**：策略切换不能影响正在运行的任务。

**规范**：社区贡献的策略必须通过契约验证（`tests/contract/`）。

### 4.13 增量规划规范（源自 ARCHITECTURAL_PRINCIPLES C-2）

**规范**：规划器必须支持增量扩展（不能一次性生成所有节点）。

**规范**：规划深度默认限制为 10 层，可通过配置文件调整。

**规范**：任务回退时必须保留已成功节点的结果，仅重新规划失败节点及其下游。

**规范**：回退次数超过阈值（默认 3 次）必须终止任务，记录不可恢复错误。

### 4.14 错误消息模板规范（源自 ARCHITECTURAL_PRINCIPLES A-2）

**规范**：所有错误消息必须遵循统一模板：

```
[ERROR] <error_code>: <human_readable> (context: <key=value>). Suggestion: <action>
```

**示例**：
```
[ERROR] AIRY_ENOMEM: 内存分配失败 (context: requested=256MB, available=128MB, process=airy_llm_d, pid=1234, used=2.1GB). Suggestion: 1) 减少批量大小 2) 启用内存压缩 3) 增加系统内存
```

**BAN-232**：错误消息禁止仅包含错误码，必须包含上下文和修复建议。

**检测方式**：`check_error_message_format.py --regex '^\[ERROR\] .*: .* \(context: .*\)\. Suggestion: .*$'`

### 4.15 复杂度度量规范（源自 ARCHITECTURAL_PRINCIPLES A-1）

**规范**：每个模块的公共 API 数量、平均参数个数、圈复杂度需在代码审查时记录，并纳入技术债务看板。

**规范**：每季度进行一次接口复杂度审查，对超标模块提出简化计划。

**规范**：新增 API 必须提供充分理由（如 ADR），并评估是否可通过现有 API 组合实现。

**规范**：CI 中运行 `scripts/check_api_complexity.sh --trend --report`，输出各模块复杂度趋势报告。

### 4.16 连接验证规范（v0.1.1 新增）

**BAN-197**：每条连接线必须有独立的集成测试文件（命名：`test_c_link_XX_*.c`）。

**BAN-198**：连接线接口变更必须同步更新对应的集成测试。

**BAN-199**：连接线集成测试必须覆盖：正常路径 + 错误路径 + 超时路径 + 并发路径。

### 4.17 安全编码规范（v0.1.1 强化）

**BAN-211**：所有外部输入（HTTP 请求、IPC 消息、CLI 参数）必须经过 Cupolas Sanitizer 四阶段净化管道后才可使用，禁止直接使用原始输入。

**BAN-212**：文件路径操作必须验证工作区边界，禁止路径穿越（`../`、符号链接逃逸）。

**BAN-213**：API Key 和 OAuth Token 必须在日志中脱敏，禁止完整输出。

#### TOCTOU 竞态条件防护（源自 C 安全编码标准 §3.4）

**BAN-233**：禁止先检查后使用的模式（`access()` + `open()`、`stat()` + `open()`），必须直接尝试操作。

```c
// ❌ 禁止 — TOCTOU 竞态
if (access(filepath, R_OK) == 0) {
    FILE* f = fopen(filepath, "r");  // 攻击者可能在此窗口替换文件
}

// ✅ 正确 — 直接操作 + O_NOFOLLOW
int fd = open(filepath, O_RDONLY | O_NOFOLLOW);
if (fd < 0) return AIRY_EINVAL;
```

**检测方式**：`ban_scan.sh` 检测 `access()` + `open()` 组合模式。

#### 信号处理器安全（源自 C 安全编码标准 §3.5）

**BAN-234**：信号处理器中禁止调用非异步信号安全函数（`printf`、`malloc`、`free`、`syslog`、`pthread_mutex_lock` 等）。仅允许设置 `volatile sig_atomic_t` 标志和调用 `write()`/`_exit()` 等异步信号安全函数。

**检测方式**：代码审查 + `ban_scan.sh` 检测信号处理器中的禁止函数调用。

#### 格式化字符串安全（源自 C 安全编码标准 §5.2）

**BAN-235**：禁止将用户输入直接作为格式化字符串。所有 `printf` 族、`syslog`、`fprintf`、`snprintf`、`errx` 必须使用固定格式字符串。

```c
// ❌ 禁止 — 格式化字符串注入
printf(user_input);
syslog(LOG_ERR, user_msg);

// ✅ 正确 — 固定格式字符串
printf("%s", user_input);
syslog(LOG_ERR, "%s", user_msg);
```

**BAN-236**：所有格式化字符串中禁止使用 `%n`（可写入任意内存地址）。

**检测方式**：编译选项 `-Wformat=2 -Wno-format-extra-args`。

#### 编译硬化选项（源自 C 安全编码标准 §8 + C 编码标准 §12.1）

**规范**：Release 构建必须启用以下编译/链接硬化选项：

| 选项 | 作用 | 平台 |
|------|------|------|
| `-fstack-protector-strong` | 栈溢出检测 | GCC/Clang |
| `-D_FORTIFY_SOURCE=2` | 运行时缓冲区检查 | GCC/Clang |
| `-fPIE -pie` | 位置无关可执行 | GCC/Clang |
| `-Wl,-z,relro -Wl,-z,now` | 只读重定位 | GCC/Clang |
| `-fvisibility=hidden` | 符号隐藏 | GCC/Clang |
| `/GS-` 或 `/guard:cf` | 控制流防护 | MSVC |

**规范**：CI 矩阵中运行 Sanitizers：ASAN、UBSAN、TSAN、MSAN。

**规范**：对解析器与外部输入持续做模糊测试（libFuzzer/AFL++），并保留回归 corpus。

#### 动态库加载安全（源自 C 安全编码标准 §6.3）

**BAN-237**：`dlopen()` 必须使用绝对路径，禁止依赖 `LD_LIBRARY_PATH`、`LD_PRELOAD`、`DYLD_INSERT_LIBRARIES` 等环境变量。

**规范**：程序启动时必须清理上述危险环境变量。使用 `RPATH`/`RUNPATH` 替代 `LD_LIBRARY_PATH`。

**规范**：禁止加载来自可写目录（如 `/tmp`、用户 home 目录）的动态库。

#### 有符号/无符号整数混用防护（源自 C 安全编码标准 §4.4）

**BAN-238**：禁止有符号/无符号整数之间的隐式转换，必须显式转换并添加范围检查。

**规范**：比较操作中两操作数类型必须一致。使用 `-Wsign-compare -Wsign-conversion` 编译选项检测。

**规范**：循环变量与数组索引统一使用 `size_t`。

### 4.18 目录模板强制规范（源自 C 编码标准 §3）

**规范**：每个模块必须且仅包含以下五项顶级内容：

```
module/
├── include/           ← 稳定公共头（导出 API）
├── src/               ← 实现（可含 src/internal/）
├── tests/             ← 单元与集成测试
├── CMakeLists.txt     ← 构建、导出与安装规则
└── README.md          ← 模块概述、API 兼容级别、配置与示例
```

**规范**：`include/` 仅放对外接口；实现细节保留在 `src/`。

**规范**：`README.md` 须声明 API 版本（MAJOR.MINOR）、支持平台与快速上手示例。

**规范**：`tests/` 至少包含一个单元测试与一个可在 CI 中重复运行的集成测试用例。

### 4.19 代码审查规范（源自 C 编码标准 §16）

**规范**：仓库中设置 CODEOWNERS，关键模块由指定人员审查；关键模块 PR 至少需要两位 reviewer。

**Review 清单（必检项）**：

| 检查项 | 说明 |
|--------|------|
| API/ABI 影响 | 是否破坏现有接口 |
| 测试覆盖 | 是否包含相应测试 |
| 格式/静态分析/sanitizer 结果 | 是否全部通过 |
| SBOM/第三方许可影响 | 是否引入新依赖 |
| 安全考虑 | 是否引入安全风险 |
| BAN 检查 | 是否通过 BAN-01~13 自动扫描 |
| CROSS 检查 | 是否通过 CROSS-01~06 跨平台规范检查 |

### 4.20 供应链安全规范（源自 C 编码标准 §12.4 + §15）

**规范**：CI 生成 SBOM（SPDX/CycloneDX格式）。

**规范**：定期依赖漏洞扫描。依赖漏洞超过高危阈值时阻断发布。

**规范**：发布时用 Sigstore/Cosign 签名制品。

**规范**：每次发布应保留可重现构建元数据（构建日志、编译标志、SBOM、签名）。

---

## 第五章：Python 生态层代码规范

> **说明**：本章整合 [Python_coding_style_standard.md](../Docs/50-specifications/30-coding-standard/12-python-coding-style.md) 的全部规范。

### 5.1 继承规范（BAN-080~BAN-099 保留）

- BAN-080：禁止 `print()`，统一使用 `logging.getLogger()`
- BAN-081：禁止裸 `except:`，必须指定异常类型
- BAN-082：禁止 `assert` 用于生产逻辑

### 5.2 Python 专项 BAN 规则（整合 Python 编码标准 BAN-180~187）

| 编号 | 规则 | 检测方式 | 替代方案 |
|------|------|---------|---------|
| BAN-214 | Python 库代码禁止 `print()` | `ruff T201` / pylint | 使用 `logging`：`logger.info()` |
| BAN-215 | API 边界必须校验输入 | pylint + 代码审查 | 使用 Pydantic BaseModel |
| BAN-216 | 错误处理必须使用结构化异常 | ruff + 代码审查 | 继承 `AgentRTError` 基类 |
| BAN-239 | 禁止裸 `except:` | `ruff E722` | 使用 `except Exception:` 并记录日志 |
| BAN-240 | 禁止 `except` 块中 `pass` 且无日志 | 代码审查 / 自定义 ruff 规则 | 至少记录 `logger.warning()` |
| BAN-241 | 禁止生产代码中使用 `assert` | `ruff S101` | 使用显式条件检查 + 异常 |

### 5.3 生态层迁移规范

**BAN-200**：`manager/` 和 `openlab/` 从 `agentos/` 迁移到 `ecosystem/` 后，所有 `import` 路径必须更新并通过 `python -m pytest` 验证。

**BAN-201**：`manager/` 的 11 Schema 必须与 `agentrt.yaml` 统一配置中心的 Schema 保持一致，新增字段需要双向同步。

**BAN-202**：OpenLab Markets 的 `market_client.py` 必须实现与 `market_d` C 服务的一致性契约。

### 5.4 Python 编码标准

**规范**：Python 版本要求 3.11+。

**规范**：代码格式化使用 Ruff，行长度上限 120。

**规范**：静态分析使用 pylint + mypy，CI 中必须通过。

**规范**：异步优先（async-first）。所有 I/O 操作必须使用 `async def`，禁止在异步上下文中调用同步阻塞函数。

**规范**：测试覆盖率目标 ≥ 70%。

**规范**：一个 PR = 一个 issue ≤ 5000 行变更。

**规范**：所有外部依赖在测试中必须使用 mock 或 fake 实现。

### 5.5 C FFI 绑定规范（源自 Python 编码标准 §10-A）

**规范**：FFI 框架选择：简单绑定用 `ctypes`，复杂绑定用 `cffi`。

**规范**：绑定文件命名：`airy_<module>_ffi.py`。

**规范**：FFI 模块仅暴露 Pythonic 接口，不暴露原始 C 指针。

**规范**：所有 `AIRY_E*` C 错误码必须转换为 Python 异常。

**FFI 内存所有权规则**：

| 所有权 | 规则 |
|--------|------|
| C → Python（C 分配） | Python 使用后必须调用 C 侧释放函数 |
| Python → C（Python 分配） | Python 保持引用，C 侧不得释放 |
| 共享缓冲区 | 明确文档化生命周期，使用 `memoryview` 避免拷贝 |

---

## 第六章：Rust SDK/CLI/TUI 规范

> **说明**：本章整合 [Rust_coding_style_standard.md](../Docs/50-specifications/30-coding-standard/13-rust-coding-style.md) 和 [Rust_secure_coding_standard.md](../Docs/50-specifications/30-coding-standard/14-rust-secure-coding.md) 的核心规范。

### 6.1 基础规范

**BAN-203**：CLI 工具必须使用 `clap` crate 构建参数解析。

**BAN-204**：TUI 工具必须使用 `ratatui` crate。

**BAN-205**：所有 `unwrap()` 和 `expect()` 必须有对应的错误消息，生产代码中禁止裸 panic。

**检测方式**：`cargo clippy -- -W clippy::panic -W clippy::unwrap_used`

**BAN-206**：Rust SDK 的 FFI 调用必须通过 `unsafe` 块封装，并在块内进行参数校验。

**检测方式**：`cargo clippy -- -W clippy::undocumented_unsafe_blocks`

### 6.2 Plugin SDK 规范

**BAN-207**：Plugin manifest 的 `permissions` 声明必须与 Cupolas `safety_guard.h` 的 8 种守卫类型对应。

| Plugin manifest 权限 | Cupolas SafetyGuard 守卫 |
|---------------------|------------------------|
| `permission` | `SAFETY_GUARD_PERMISSION` |
| `input` | `SAFETY_GUARD_INPUT` |
| `resource` | `SAFETY_GUARD_RESOURCE` |
| `audit` | `SAFETY_GUARD_AUDIT` |
| `rate_limit` | `SAFETY_GUARD_RATE_LIMIT` |
| `content_filter` | `SAFETY_GUARD_CONTENT_FILTER` |
| `network` | `SAFETY_GUARD_NETWORK` |
| `sandbox` | `SAFETY_GUARD_SANDBOX` |

**BAN-208**：Plugin 生命周期方法（`init`/`start`/`stop`/`destroy`）必须实现超时保护（默认 30s）。

### 6.3 CLI 通信规范

**规范**：CLI 工具通过 `gateway` 的 HTTP API 与 C 核心通信，不直接调用 syscall 或 IPC Bus。

| CLI 命令 | HTTP 请求 | 目标 daemon |
|---------|----------|------------|
| `agentrt run` | `POST /api/v1/agent/run` | CoreLoopThree |
| `agentrt config reload` | `POST /api/v1/config/reload` | config_manager |
| `agentrt llm list` | `GET /api/v1/llm/providers` | llm_d |
| `agentrt status` | `GET /api/v1/health` | monit_d |

**例外**：`agentrt init` 和 `agentrt create` 是纯本地文件操作，不经过 gateway。

### 6.4 Release 优化规范

**规范**：Release 构建必须启用以下优化：

```toml
[profile.release]
opt-level = "z"
lto = true
codegen-units = 1
strip = true
panic = "abort"
```

**BAN-217**：Release 构建禁止使用 `panic = "unwind"`。

### 6.5 TUI 架构规范

**规范**：TUI 采用保留模式（retained-mode）架构，应用状态与渲染分离。

**规范**：TUI 与 Agent 运行时通过异步 channel 通信，TUI 不直接调用任何 Agent API。

---

## 第七章：Hook 系统规范

> **来源**：综合 atomcode、openclaw、claude-code 的工程实践。详见 v22.0 第七章，内容不变。

### 7.1 Hook 生命周期事件

AgentRT 定义以下 Hook 事件，覆盖 Agent、LLM、MemoryRovol 三大生命周期：

```
Agent 生命周期:
├── on_agent_init        ← Agent 初始化
├── on_agent_start       ← Agent 开始执行
├── ┌─── 循环 ───┐
│   │ on_cognition_start  ← 认知阶段开始
│   │ on_tool_call        ← 工具调用前（可拦截，连接 Cupolas SafetyGuard）
│   │ on_tool_result      ← 工具调用后
│   │ on_cognition_end    ← 认知阶段结束
│   └────────┘
├── on_agent_stop        ← Agent 停止
└── on_agent_destroy     ← Agent 销毁

LLM 生命周期:
├── on_llm_request       ← LLM 请求发送前
├── on_llm_response      ← LLM 响应接收后
└── on_llm_error         ← LLM 调用失败

MemoryRovol 生命周期:
├── on_l1_write          ← L1 原始数据写入前
├── on_l2_embed          ← L2 嵌入生成后
├── on_l3_bind           ← L3 实体绑定后
└── on_l4_rule           ← L4 规则发现后

会话生命周期:
├── on_session_start     ← 会话创建
├── on_session_end       ← 会话结束
└── on_session_compact   ← 会话上下文压缩
```

### 7.2 Hook 注册接口规范

**BAN-209**：Hook 注册必须通过 `airy_hook_register()` 统一接口，禁止直接操作内部注册表。

```c
typedef struct {
    const char *name;              // 唯一标识符，格式: [a-z][a-z0-9_]*  最长64字符
    airy_hook_type_t type;      // Hook 类型: SHELL/PYTHON/WEBHOOK
    const char *entrypoint;        // 脚本路径 / URL / Python 模块路径
    const char **events;           // 监听的事件列表，1~16
    size_t event_count;
    int priority;                  // 0-100，越高越先执行，默认50
    bool blocking;                 // true=可拦截操作，false=仅观察
    uint32_t timeout_ms;           // 超时时间，默认5000ms
    bool enabled;                  // 启用/禁用状态，默认true
} airy_hook_descriptor_t;

int airy_hook_register(airy_hook_descriptor_t *desc);
int airy_hook_unregister(const char *name);
int airy_hook_trigger(const char *event, const char *context_json,
                         bool *blocked, char **result_json);
```

### 7.3 Hook 执行规范

**BAN-210**：Hook 执行必须受超时保护（默认 5s），超时 Hook 将被强制终止并记录审计日志。

**BAN-218**：Hook 系统必须采用 fail-open 策略：Hook 超时或崩溃时默认放行主操作，仅记录审计日志。

### 7.4 三种 Hook 实现模式

| 模式 | 通信方式 | 超时 | 重试 | 适用场景 |
|------|---------|------|------|---------|
| Shell Hook | stdin JSON + exit code | 5s（可配置） | 无 | 简单脚本、CI/CD 集成 |
| Python Hook | HookPlugin 基类 | 5s（可配置） | 无 | 复杂逻辑、需要 SDK 访问 |
| Webhook | HTTP POST + HMAC-SHA256 签名 | 30s | 3 次指数退避 | 外部服务集成 |

### 7.5 Hook 来源与优先级

| 优先级 | 来源 | 目录 |
|:---:|------|------|
| 1 | config | `agentrt.yaml` 中声明 |
| 2 | global | `~/.agentos/hooks/` |
| 3 | bundled | `ecosystem/hooks/` |
| 4 | workspace | `.agentos/hooks/` |

### 7.6 Hook 与 SafetyGuard 集成

**接口**：`hook_interceptor.c` 必须通过 `safety_guard_check_chain()` 拦截工具调用。

**连接线**：C-L05-HOOK — Cupolas SafetyGuard → Hook 系统，Phase 2 完成连接。

### 7.7 官方 Hook 集合

| Hook | 事件 | 功能 |
|------|------|------|
| `audit_hook.py` | on_tool_call | 记录所有工具调用到审计日志 |
| `cost_tracker.py` | on_llm_response | 追踪 Token 消耗和费用 |
| `security_reminder.py` | on_agent_start | 注入安全提醒到 System Prompt |
| `prompt_injector.py` | on_llm_request | 注入自定义 Prompt 片段 |
| `session_memory.py` | on_session_start | 加载历史会话记忆 |

### 7.8 Hook 配置格式

Hook 支持 3 种配置格式：TOML ScriptHook、TOML Webhook、agentrt.yaml 内联。详见 v22.0 §7.8。

---

## 第八章：Plugin 系统规范

> **来源**：综合 openclaw、claude-code、atomcode 的工程实践。详见 v22.0 第八章，内容不变。

### 8.1 四型插件模型

| 类型 | 功能 | 生命周期 | 示例 |
|------|------|---------|------|
| **Command** | 斜杠命令扩展 | 按需加载 | `/review`、`/deploy` |
| **Agent** | 子智能体 | 按需创建 | 代码审查 Agent、研究 Agent |
| **Hook** | 事件驱动拦截 | 注册时加载 | 安全审计 Hook、成本追踪 Hook |
| **Skill** | 知识注入 | 会话级加载 | 代码规范 Skill、领域知识 Skill |

### 8.2 Plugin Manifest 规范

**BAN-219**：每个 Plugin 必须包含 `plugin.json` manifest 文件。

**规范**：`permissions` 数组中的每个值必须与 Cupolas SafetyGuard 的守卫类型精确对应（见 §6.2 对照表）。

**规范**：Plugin 运行时通过 `${AGENTRT_PLUGIN_ROOT}` 环境变量获取自身根目录，禁止硬编码路径。

### 8.3 Plugin 自动发现

```
1. 扫描 agentrt.yaml 中 plugins.plugin_dirs 列出的目录
2. 每个目录下查找 plugin.json
3. 解析 plugin.json → 注册 Command/Agent/Hook/Skill 入口
4. 扫描 commands/ → 注册斜杠命令
5. 扫描 agents/ → 注册子智能体
6. 扫描 skills/ → 注册知识注入
7. 扫描 hooks/ → 注册事件 Hook
8. 扫描 .mcp.json → 注册 MCP 工具服务器
```

### 8.4 Plugin 生命周期

```
discovered → validated → installed → initialized → running → stopped → destroyed
```

**BAN-220**：Plugin 安装包必须提供 SHA-256 校验和，安装时必须验证完整性。

### 8.5 Plugin 安全审查

| 层级 | 审查方式 | 检查内容 |
|------|---------|---------|
| Layer 1 | 正则模式匹配 | 已知危险模式（`eval()`、`exec()`、`subprocess.call()`、`os.system()`） |
| Layer 2 | LLM diff 审查 | AI 审查 Plugin 代码差异 |
| Layer 3 | Agentic 审查 | 独立 Agent 执行深度安全审查 |

**BAN-221**：Layer 1 正则匹配命中的 Plugin 必须标记为"需人工审批"，禁止自动安装。

---

## 第九章：LLM 路由与错误处理规范

> **来源**：综合 hermes-agent、atomcode 的工程实践。详见 v22.0 第九章，内容不变。

### 9.1 三层成本感知路由

```
Layer 1: Provider 路由    → cost_aware/round_robin/least_latency/quality_first
Layer 2: Smart Model Routing → 简单消息启发式 → 便宜模型
Layer 3: Auxiliary Client Routing → 降级到 fallback_chain
```

### 9.2 错误分类器

**规范**：所有 LLM 错误必须通过结构化错误分类器处理（14 类）。

**BAN-230**：错误分类器必须覆盖全部 LLM 错误类型，不得有未分类的错误。

### 9.3 重试策略规范

**BAN-222**：LLM 重试禁止使用固定间隔，必须使用抖动指数退避。

### 9.4 降级链规范

**规范**：每个 LLM 请求必须配置降级链（fallback_chain）。

### 9.5 Prompt 缓存不可变性

**BAN-223**：Prompt 缓存上下文在构建后必须不可变。

---

## 第十章：配置管理规范

> **来源**：综合 openclaw、hermes-agent 的工程实践。详见 v22.0 第十章，内容不变。

### 10.1 统一配置中心

**规范**：所有子系统配置通过一个 `agentrt.yaml` 文件管理。

### 10.2 配置优先级

```
1. 环境变量覆盖        AIRY_LLM_PROVIDERS_OPENAI_API_KEY=sk-xxx
2. 命令行参数覆盖      agentrt config set llm.default_provider anthropic
3. agentrt.yaml 配置   llm.default_provider: "openai"
4. Plugin 默认值       Plugin manifest 中的默认配置
5. 系统内置默认值      代码中的 AIRY_DEFAULT_* 常量
```

**规范**：环境变量覆盖格式为 `AIRY_` + 配置路径（`_` 分隔，全大写）。

### 10.3 SecretRef 机制

**BAN-224**：配置中的敏感信息必须通过 SecretRef 机制引用，禁止明文写入 `agentrt.yaml`。

SecretRef 支持三种提供者：`${env:VAR}`、`${file:/path}`、`${exec:command}`

**规范**：SecretRef 解析顺序：`env` → `file` → `exec`。`exec` 提供者必须设置超时（默认 5s）。

**规范**：配置加载时自动检测敏感字段（包含 `key`、`secret`、`password`、`token` 关键词），对未使用 SecretRef 的敏感字段发出警告。

### 10.4 配置热重载

**BAN-225**：配置热重载期间，正在进行的操作必须使用旧配置完成，新操作使用新配置。

### 10.5 原子文件写入

**规范**：配置文件写入必须使用原子操作：写入临时文件 → fsync → rename。

### 10.6 Profile 隔离

**规范**：AgentRT 支持通过 `AGENTRT_HOME` 环境变量覆盖配置和数据目录。

**规范**：代码中必须使用 `get_agentrt_home()` 获取配置目录，禁止硬编码 `~/.agentos/`。

---

## 第十一章：目录结构重组规范

### 11.1 Git 操作规范

**规范**：所有目录移动必须使用 `git mv` 而非普通文件系统 `mv`，以保留 git 历史。

**规范**：每次目录移动后立即提交，避免混合功能性变更。

**规范**：若文件未被 git 跟踪（untracked），`git mv` 会失败。此时使用 PowerShell `Move-Item` 移动，并在提交信息中注明"untracked file move"。

### 11.2 构建系统一致性

**BAN-226**：目录移动后必须验证 4 个构建系统全部通过：CMake 构建 + Python 模块导入 + Rust SDK 编译 + Go SDK 编译。

### 11.3 命名规范（全项目统一）

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| 目录名 | kebab-case | `coreloopthree/` |
| C 文件名 | snake_case | `hook_registry.c` |
| C 函数名 | snake_case + 模块前缀 | `airy_hook_register()` |
| C 类型名 | snake_case + `_t` | `airy_hook_descriptor_t` |
| C 枚举值 | UPPER_SNAKE_CASE | `AIRY_TASK_STATE_READY` |
| Python 文件名 | snake_case | `audit_hook.py` |
| Python 类名 | PascalCase | `PromptEvaluator` |
| Python 函数名 | snake_case | `select_provider` |
| Rust 类型名 | PascalCase | `PluginManifest` |
| Rust 函数名 | snake_case | `register_hook` |
| Go 导出函数 | PascalCase | `RegisterHook` |
| Go 未导出函数 | camelCase | `selectProvider` |
| Go 包名 | lowercase | `hookd` |
| YAML 键名 | snake_case | `default_provider` |
| 环境变量 | UPPER_SNAKE_CASE | `AGENTRT_HOME` |
| Hook 事件名 | snake_case | `on_tool_call` |
| BAN 规则编号 | `BAN-NNN` | `BAN-191` |

### 11.4 其他语言编码标准引用

| 语言 | 规范文档 | 关键规则 |
|------|---------|---------|
| Go | [Go_coding_style_standard.md](../Docs/50-specifications/30-coding-standard/06-go-coding-style.md) | gofmt、golint、go vet、error 作为返回值 |
| C++ | [Cpp_coding_style_standard.md](../Docs/50-specifications/30-coding-standard/05-cpp-coding-style.md) | clang-format、RAII、智能指针、禁止裸 new/delete |
| TypeScript | [JavaScript_coding_style_standard.md](../Docs/50-specifications/30-coding-standard/08-javascript-coding-style.md) | ESLint + Oxlint、Zod 校验、discriminated unions |
| Java | [Java_secure_coding_standard.md](../Docs/50-specifications/30-coding-standard/09-java-secure-coding.md) | 输入验证、SQL 参数化、安全反序列化 |

### 11.5 独立子仓库路径引用安全规范（v24.1 新增）

> **背景**: `OpenAirymax/` 下的 `AgentRT`、`Desktop`、`Docker`、`Docs`、`MemoryRovol`、`DocsClosed` 均为**独立的 Git 子仓库**，各自拥有独立的 `.git/`、commit 历史、CI/CD 流程。跨子仓库的路径引用必须使用相对推导机制。

#### 11.5.1 子仓库清单与职责边界

| 子仓库 | Git 远程 | 职责 | 改名后路径 |
|--------|---------|------|----------|
| **AgentRT** | `origin` (独立) | C 核心引擎 + 所有源代码 | `OpenAirymax/agentrt/` |
| **Desktop** | `origin` (独立) | Tauri 桌面应用（前端） | 不变 |
| **Docker** | `origin` (独立) | 生产 Docker 部署配置 | 不变 |
| **Docs** | `origin` (独立) | 公开文档 | 不变 |
| **MemoryRovol** | `origin` (独立) | MemoryRovol 商业化库 | 不变 |
| **DocsClosed** | `origin` (独立) | 内部文档 | 不变 |

#### 11.5.2 跨子仓库引用安全规则

**规范**：CMake 跨子仓库引用必须使用 `get_filename_component` 进行相对路径推导，禁止硬编码同级目录名。

```cmake
# ✅ 正确 — 相对推导（不受父目录改名影响）
get_filename_component(_airy_root "${CMAKE_CURRENT_SOURCE_DIR}/../../.." ABSOLUTE)
get_filename_component(_workspace_root "${_airy_root}/.." ABSOLUTE)
set(_mr_candidate "${_workspace_root}/MemoryRovol")

# ❌ 禁止 — 硬编码同级目录名
set(_mr_candidate "${CMAKE_SOURCE_DIR}/../MemoryRovol")  # NA-4 违反
```

**验证（v2.5 已验证通过）**：AgentOS 改名后 `CMAKE_CURRENT_SOURCE_DIR` 从 `...AgentOS/agentos/...` 变为 `...agentrt/agentrt/...`，但 `get_filename_component(.../../../..)` 的相对层级不变，推导出的 `MemoryRovol/` 子仓库路径解析**不受改名影响**。

**规范**：Desktop 和 Docker 子仓库中的 AgentRT 交叉引用必须分别在其自有 CI 中验证，确保独立子仓库更新后跨库集成仍然正常。

#### 11.5.3 子仓库间改名协调时序

```
步骤 1: AgentOS 子仓库完成 P0.1 改名 + P0.10 编译验证
步骤 2: Desktop 子仓库更新 productName + UI 文案（并行）
步骤 3: Docker 子仓库更新 Dockerfile COPY 路径 + 文档
步骤 4: Docs 子仓库更新品牌引用
步骤 5: MemoryRovol 子仓库更新日志前缀
步骤 6: DocsClosed 子仓库更新
步骤 7: 全子仓库交叉验证 — docker-compose up + Desktop 连接 AgentRT 后端
```

### 11.6 airy_ → agentrt_ 彻底改名规范（v26.0 重写）

> ⚠️ **历史决策记录（未执行）**：本节记录的是 v26.0 阶段的一项历史改名决策，**该决策未实际执行**。
>
> **当前前缀规范**以 SSoT `docs/AirymaxRT/10-architecture/06-iron9-shared-model.md` §3.12 为准：
> - `airy_*` 是 [SC] 共享契约层 + 应用层的**正确前缀**（源码 1788 处使用）
> - `agentrt_*` **不使用**（源码 0 处使用）
> - `agentos_*` **已废弃**（源码 0 处使用）
>
> 本节保留作为历史决策记录，BAN-341~BAN-344 规则中关于 `daemon/` → `daemons/` 改名部分仍然有效，但关于 `airy_` → `agentrt_` 改名部分**已废止**。
>
> **附加说明**：本节 L5 改名矩阵中出现的 `airy_error_t` 本身为错误命名，正确的错误码类型名应为 `airy_err_t`（定义于 `agentrt/commons/include/airy_types.h`），参见 SSoT `docs/AirymaxRT/10-architecture/00-architectural-principles.md`。本节中 `airy_error_t` → `agentrt_error_t` 的改名建议同样已废止，正确的类型名维持 `airy_err_t`。

> **核心决策 §v4.0**: `airy_` → **`agentrt_`** 彻底改名，**不留兼容别名头**（不生成 `airy_compat_aliases.h`）。0.1.1 是唯一奠基版本（无 0.2.0/0.3.0/1.0.0 过渡，直接到 1.0.1），兼容别名头无价值。同时 `daemon` → **`daemons`** 改名（模块名、目录、CMake target、仓库名统一改）。进程二进制名 `*_d`（gateway_d/llm_d/tool_d/sched_d/market_d/monit_d/channel_d/info_d/notify_d/observe_d/hook_d/plugin_d）保持不变。

#### 11.6.1 七层面彻底改名矩阵

| 层面 | 旧名 | 新名 | 影响范围 | 必改 |
|------|------|------|---------|:---:|
| **L1 源码目录** | `agentos/` | `agentrt/` | 顶层目录 | ✅ |
| **L2 CMake target** | `airy_common`、`airy_atoms`、`airy_daemon` 等 15+ 个 | `agentrt_common`、`agentrt_atoms`、`agentrt_daemons` 等 | 全部 CMakeLists.txt | ✅ |
| **L3 运行时路径** | `/etc/agentos`、`AIRY_CONFIG_DIR` | `/etc/agentrt`、`AGENTRT_CONFIG_DIR` | 全部配置文件 + 环境变量 | ✅ |
| **L4 安装路径** | `include/agentos/` | `include/agentrt/` | 全部 CMake install() + #include | ✅ |
| **L5 C 公开 ABI** | `airy_error_t`、`airy_syscalls_init()` 等数千处 | `agentrt_error_t`、`agentrt_syscalls_init()` | 472 个 .c/.h 文件、13037 处前缀 | ✅ |
| **L6 C 宏** | `AIRY_API`、`AIRY_VERSION` | `AGENTRT_API`、`AGENTRT_VERSION` | 全部公开头文件 | ✅ |
| **L7 SDK 包名** | `agentos`(PyPI)、`@agentos/sdk`(npm)、`agentrt-rs`(crate)、`github.com/spharx/agentos/sdk/go` | `agentrt`(PyPI)、`@agentrt/sdk`(npm)、`agentrt-rs`(保持)、`github.com/spharx/agentrt/sdk/go` | 4 个 SDK 包配置 | ✅ |
| **L8 daemon 模块** | `agentos/daemon/`、`agentrt_daemon`、`daemon.git` | `agentrt/daemons/`、`agentrt_daemons`、`daemons.git` | 目录 + CMake + 仓库名 | ✅ |
| **L9 进程二进制名** | `gateway_d`、`llm_d`、`tool_d` 等 12 个 `*_d` | **保持不变** | — | ❌ |

#### 11.6.2 改名验证标准（ACC-SP01 + ACC-SP02）

| 验证项 | 验证命令 | 期望 |
|--------|---------|:---:|
| L1-L6 airy_ 零残留 | `grep -rn '\bairy_' --include='*.c' --include='*.h' --include='*.py' --include='*.go' --include='*.rs' --include='*.ts' . | wc -l` | **0** |
| L6 AIRY_ 宏零残留 | `grep -rn 'AIRY_' --include='*.h' . | wc -l` | **0** |
| L7 SDK 包名零残留 | `grep -rn 'agentos' sdk/*/pyproject.toml sdk/*/package.json sdk/*/Cargo.toml sdk/*/go.mod` | **0** |
| L8 daemon/零残留 | `grep -rn '\bdaemon/' --include='CMakeLists.txt' . | wc -l` | **0** |
| L9 进程二进制名保持 | `find . -name '*_d' -type f` | **12 个** |

#### 11.6.3 改名操作规范（BAN-341~BAN-344）

| BAN | 规则 | 检测方式 |
|-----|------|---------|
| **BAN-341** | **禁止保留 `airy_compat_aliases.h` 兼容别名头**——0.1.1 是唯一奠基版本，无过渡版本，兼容别名头无价值 | `[SPLIT-SCAN]` grep `airy_compat_aliases.h` 期望 0 |
| **BAN-342** | **禁止改名后留有 airy_ 前缀残留**——任何残留即编译失败。**【v4.0 废止】本规则中关于 airy_ 前缀清零的要求已废止。airy_* 是 SSoT 规定的 [SC] + 应用层正确前缀（见 §1.6 术语表 + 06-iron9 §3.12）。BAN-342 仅保留 agentos_* 废弃前缀清零部分。** | `[SPLIT-SCAN]` grep `airy_` 期望 0（**注：本检测已废止，airy_* 为正确前缀，源码 1788 处使用；仅 agentos_* 废弃前缀清零检测保留**） |
| **BAN-343** | **禁止 daemon 模块名残留**（应为 daemons）——目录、CMake target、仓库名必须统一 | `[SPLIT-SCAN]` grep `daemon/` 在 CMakeLists.txt 期望 0 |
| **BAN-344** | **禁止进程二进制名 `*_d` 改名**——gateway_d/llm_d 等 12 个进程二进制名是用户接口契约，必须保持 | `[SPLIT-SCAN]` `find . -name '*_d'` 期望 12 |

#### 11.6.4 改名操作步骤（SP01 详细）

```bash
# 1. 改名前完整符号清单导出
nm -g build/lib/*.a | grep airy_ > /tmp/airy_symbols_before.txt

# 2. 源码目录改名
git mv agentos agentrt

# 3. CMake target 改名（全部 CMakeLists.txt）
find . -name CMakeLists.txt -exec sed -i 's/airy_/agentrt_/g' {} +

# 4. 运行时路径改名
find . -type f -exec sed -i 's|/etc/agentos|/etc/agentrt|g; s|AIRY_CONFIG_DIR|AGENTRT_CONFIG_DIR|g' {} +

# 5. 安装路径改名
find . -type f -exec sed -i 's|include/agentos/|include/agentrt/|g' {} +

# 6. C 公开 ABI 改名（472 文件 13037 处）
find . -name '*.c' -o -name '*.h' | xargs sed -i 's/\bairy_/agentrt_/g'

# 7. C 宏改名
find . -name '*.h' -exec sed -i 's/AIRY_/AGENTRT_/g' {} +

# 8. SDK 包名改名（4 个 SDK）
# sdk/python/pyproject.toml: name = "agentrt"
# sdk/typescript/package.json: "@agentrt/sdk"
# sdk/rust/Cargo.toml: agentrt-rs（保持）
# sdk/go/go.mod: github.com/spharx/agentrt/sdk/go

# 9. daemon → daemons 改名
git mv agentrt/daemon agentrt/daemons
find . -name CMakeLists.txt -exec sed -i 's/agentrt_daemon\b/agentrt_daemons/g' {} +

# 10. 全量重编译 + ctest 验证
cmake -B build && cmake --build build -j$(nproc) && ctest --test-dir build

# 11. 改名后符号清单对比
nm -g build/lib/*.a | grep agentrt_ > /tmp/agentrt_symbols_after.txt
diff /tmp/airy_symbols_before.txt /tmp/agentrt_symbols_after.txt
# 期望：仅前缀变化，符号数量一致

# 12. 零残留验证
grep -rn '\bairy_' --include='*.c' --include='*.h' --include='*.py' --include='*.go' --include='*.rs' --include='*.ts' . | wc -l  # 期望 0
grep -rn 'AIRY_' --include='*.h' . | wc -l  # 期望 0
grep -rn '\bdaemon/' --include='CMakeLists.txt' . | wc -l  # 期望 0
find . -name '*_d' -type f | wc -l  # 期望 12（进程二进制名保持）
```

**规范**：改名操作必须使用 `git mv`（目录改名）+ `sed -i`（文件内容改名），确保 `git log --follow` 可追踪历史。改名后必须跑全量重编译 + ctest 验证 + 符号清单对比。

---

### 11.7 38 仓 git submodule 拆分规范（v26.0 新增）

> **核心决策 §v4.0**: OpenAirymax 拆分为 **38 个 git 仓库**（1 伞仓 + 5 管理仓 + 29 叶子仓 + 3 顶层仓）。伞仓 airymaxhub.git 地址 `git@atomgit.com:openairymax/airymaxhub.git`；agentrt 管理仓继承原 AgentRT 仓库 `git@atomgit.com:openairymax/agentos.git` 保留全部 git 历史；sdk 模块下子仓采用 `sdk-xx` 命名；全部目录名小写。

#### 11.7.1 38 仓目录结构规范（SPLIT-01）

```
airymaxhub/                                  # 伞仓（1）
│   url: git@atomgit.com:openairymax/airymaxhub.git
│
├── .gitmodules                              # 伞仓 submodule 声明（7 条）
├── cmake/                                   # 伞仓直属，非 submodule
│   ├── compilerflags.cmake
│   ├── sanitizers.cmake
│   ├── dependencies.cmake
│   ├── platform.cmake
│   └── utils.cmake
│
├── agentrt/                    # 管理仓库 submodule（继承原 AgentRT 历史）
│   │   url: git@atomgit.com:openairymax/agentos.git  ← 继承，保留全部 git 历史
│   │
│   ├── .gitmodules                            # agentrt 管理仓 submodule 声明（7 条）
│   ├── atoms/                    # submodule  git@atomgit.com:openairymax/atoms.git
│   ├── commons/                  # submodule  git@atomgit.com:openairymax/commons.git
│   ├── cupolas/                  # submodule  git@atomgit.com:openairymax/cupolas.git
│   ├── heapstore/                # submodule  git@atomgit.com:openairymax/heapstore.git
│   ├── protocols/                # submodule  git@atomgit.com:openairymax/protocols.git
│   ├── gateway/                  # submodule  git@atomgit.com:openairymax/gateway.git
│   └── daemons/                  # submodule  git@atomgit.com:openairymax/daemons.git
│
├── sdk/                         # 管理仓库 submodule
│   │   url: git@atomgit.com:openairymax/sdk.git
│   │
│   ├── .gitmodules                            # sdk 管理仓 submodule 声明（6 条）
│   ├── sdk-python/               # submodule  git@atomgit.com:openairymax/sdk-python.git
│   ├── sdk-go/                   # submodule  git@atomgit.com:openairymax/sdk-go.git
│   ├── sdk-rust/                 # submodule  git@atomgit.com:openairymax/sdk-rust.git
│   ├── sdk-typescript/           # submodule  git@atomgit.com:openairymax/sdk-typescript.git
│   ├── sdk-cli/                  # submodule  git@atomgit.com:openairymax/sdk-cli.git
│   └── sdk-tui/                  # submodule  git@atomgit.com:openairymax/sdk-tui.git
│
├── ecosystem/                   # 管理仓库 submodule
│   │   url: git@atomgit.com:openairymax/ecosystem.git
│   │
│   ├── .gitmodules                            # ecosystem 管理仓 submodule 声明（5 条）
│   ├── manager/                  # submodule  git@atomgit.com:openairymax/manager.git
│   ├── prompts/                  # submodule  git@atomgit.com:openairymax/prompts.git
│   ├── examples/                 # submodule  git@atomgit.com:openairymax/examples.git
│   ├── openlab/                  # submodule  git@atomgit.com:openairymax/openlab.git
│   └── skills/                   # submodule  git@atomgit.com:openairymax/skills.git
│
├── products/                    # 管理仓库 submodule
│   │   url: git@atomgit.com:openairymax/products.git
│   │
│   ├── .gitmodules                            # products 管理仓 submodule 声明（3 条）
│   ├── desktop/                  # submodule  git@atomgit.com:openairymax/desktop.git
│   ├── docker/                   # submodule  git@atomgit.com:openairymax/docker.git
│   └── memoryrovol/              # submodule  git@atomgit.com:spharx/memoryrovol.git  ← 闭源 EULA
│
├── devtools/                    # 顶层 submodule
│       url: git@atomgit.com:openairymax/devtools.git
│
├── docs/                        # 顶层 submodule
│       url: git@atomgit.com:openairymax/docs.git
│
└── docs-closed/                 # 顶层 submodule
        url: git@atomgit.com:openairymax/docs-closed.git
```

#### 11.7.2 仓库命名规范（SPLIT-02）

| 规则 | 说明 | 示例 |
|------|------|------|
| **裸名规则** | 仓库名不带 `agentrt-` 前缀，归属 `openairymax` 组织 | `openairymax/atoms` 而非 `openairymax/agentrt-atoms` |
| **sdk-xx 前缀规则** | sdk 模块下子仓必须使用 `sdk-` 前缀 | `sdk-python`、`sdk-go`、`sdk-rust`、`sdk-typescript`、`sdk-cli`、`sdk-tui` |
| **小写规则** | 全部目录名 + 仓库名小写 | `agentrt/daemons/` 而非 `agentrt/Daemon/` |
| **memoryrovol 例外** | memoryrovol 归属 `spharx` 组织（闭源 EULA） | `git@atomgit.com:spharx/memoryrovol.git` |
| **伞仓名规则** | 伞仓名为 `airymaxhub`（产品品牌） | `git@atomgit.com:openairymax/airymaxhub.git` |
| **agentrt 管理仓继承规则** | agentrt 管理仓 url 必须是原 AgentRT 仓库 url | `git@atomgit.com:openairymax/agentos.git`（保留全部 git 历史） |

#### 11.7.3 git 历史保留规范（SPLIT-03）

| 仓库类型 | 历史保留方式 | 操作命令 |
|---------|------------|---------|
| **伞仓** | 全新创建（无历史继承） | `git init && git remote add origin git@atomgit.com:openairymax/airymaxhub.git` |
| **agentrt 管理仓** | 直接继承原 AgentRT url（不 clone 不 subtree） | `git remote set-url origin git@atomgit.com:openairymax/agentos.git`（url 保持不变，agentrt 管理仓继续使用原 AgentRT 仓库） |
| **sdk/ecosystem/products 管理仓** | 全新创建 | `git init && git remote add origin <url>` |
| **叶子仓（拆分自 AgentRT）** | 使用 `git subtree split` 保留子目录历史 | `git subtree split --prefix=agentrt/agentrt/atoms/ -b atoms-branch` |
| **memoryrovol 仓** | 已是独立仓库，无操作 | — |

#### 11.7.4 7 阶段拆分顺序规范（SPLIT-04）

| 阶段 | 内容 | SP 编号 | 工时 | 阻塞条件 |
|------|------|:---:|:---:|---------|
| **阶段 1** | 奠基（W01-W30 全部完成） | W01-W30 | ~1,620h | — |
| **阶段 2** | 改名（airy_→agentrt_ 彻底 + daemon→daemons） | SP01 | 70h | 阶段 1 完成 |
| **阶段 3** | 解耦 5 处跨层耦合 | SP02-SP06 | 200h | 阶段 2 完成 |
| **阶段 4** | 立即可拆 10 仓（零跨层耦合） | SP07-SP16 | 80h | 阶段 2 完成 |
| **阶段 5** | C 层拆分 7 仓（解耦后） | SP17-SP23 | 112h | 阶段 3 完成 |
| **阶段 6** | 配套拆分 7 仓 + 伞仓组装 | SP24-SP31 | 100h | 阶段 4+5 完成 |
| **阶段 7** | 生产就绪 | SP32-SP37 | 240h | 阶段 6 完成 |

#### 11.7.5 5 处跨层耦合解耦规范（SPLIT-05）

| # | 耦合点 | 源文件归属 | 被编译进 | 修复方案 | LOC |
|---|--------|-----------|---------|---------|:---:|
| 1 | coreloopthree 编译 daemons/common/src/checkpoint.c + orchestrator.c | daemons 层 | atoms 层 | 移至 commons/utils/execution/ | 3,179 |
| 2 | coreloopthree 编译 cupolas/src/yaml_minimal.c | cupolas 层 | atoms 层 | 移至 commons/utils/config_unified/ | 1,554 |
| 3 | coreloopthree 编译 daemons/hook_d/src/{service,hook_executor,hook_registry,hook_interceptor,hook_timeout}.c | daemons 层 | atoms 层 | 提取为 atoms/coreloopthree/src/hooks/，daemons/hook_d 仅保留生命周期 | 1,872 |
| 4 | protocols 编译 daemons/common/src/safe_string_utils.c | daemons 层 | protocols 层 | 移至 commons/utils/string/ | 225 |
| 5 | cupolas 私有 include gateway/include，调用 gateway_register_endpoint() | gateway 层 | cupolas 层（反向） | 改为回调函数指针注入 | 3 处调用 |

#### 11.7.6 拆分验证规范（SPLIT-06）

| 验证项 | 验证命令 | 期望 |
|--------|---------|:---:|
| 38 仓独立 clone+构建 | 38 仓逐一 `git clone + cmake -B build + cmake --build build + ctest` | 全部成功 |
| agentrt 管理仓历史保留 | `git -C agentrt log --oneline | wc -l` 与原 AgentRT 一致 | 一致 |
| agentrt 管理仓 url | `git -C agentrt remote -v` | `git@atomgit.com:openairymax/agentos.git` |
| 伞仓一次性拉取 | `git clone --recursive git@atomgit.com:openairymax/airymaxhub.git` | 无失败 submodule |
| 5 管理仓 .gitmodules 条目数 | agentrt(7) + sdk(6) + ecosystem(5) + products(3) + agentrt-linux(8) | 29 |
| cmake/ 伞仓直属 | `ls cmake/*.cmake | wc -l` | 5 |
| memoryrovol EULA | `git -C products/memoryrovol remote -v` + `head LICENSE` | spharx 组织 + EULA |
| sdk-xx 命名 | `ls sdk/` | 全部 sdk-* 模式 |
| 目录名小写 | `find . -type d -name '[A-Z]*'` | 空 |

#### 11.7.7 拆分 BAN 规则（BAN-345~BAN-348）

| BAN | 规则 | 检测方式 |
|-----|------|---------|
| **BAN-345** | **禁止不按 7 阶段顺序拆分**——拆仓顺序错误会导致子仓依赖未就绪的父仓，触发递归 submodule 失败 | `[SPLIT-SCAN]` 检查 SP 编号顺序执行 |
| **BAN-346** | **禁止 agentrt 管理仓不继承原 AgentRT url**——必须使用 `git@atomgit.com:openairymax/agentos.git` 保留全部 git 历史 | `[SPLIT-SCAN]` `git -C agentrt remote -v` 验证 |
| **BAN-347** | **禁止 sdk 子仓不使用 sdk-xx 命名**——sdk/python 等裸名违反命名规范 | `[SPLIT-SCAN]` `ls sdk/` 全部 sdk-* |
| **BAN-348** | **禁止目录名包含大写字母**——全部目录名小写 | `[SPLIT-SCAN]` `find . -type d -name '[A-Z]*'` 期望空 |

---

### 11.8 AgentOS→AgentRT 历史改名（v24.1 已完成，仅保留历史记录）

> **历史记录**: v24.1 已完成的 `AgentOS/` → `agentrt/` 外层改名，属于早期决策。当前 v26.0 的 §11.6 是更深入的 `airy_` → `agentrt_` 内层彻底改名。

原 §11.6 的内容已归档至历史记录，详见 v24.1 版本的手册归档。当前 v26.0 的 §11.6 是彻底改名规范（airy_→agentrt_ + daemon→daemons）。

---

## 第十二章：测试规范

### 12.1 测试金字塔

```
Layer 3: 端到端 (E2E)  — 12 条连接线 + A2A/MCP/OpenAI 完整数据流
Layer 2: 集成 (INT)     — 跨模块接口验证
Layer 1: 单元 (UT)      — 纯粹函数无副作用
```

### 12.2 集成测试强制要求

| 测试类型 | 命名规范 | 最少覆盖路径 | CI 要求 |
|---------|---------|-------------|--------|
| 连接线测试 | `test_c_link_XX_desc.c` | 正常 ×1 + 错误 ×1 + 超时 ×1 + 并发 ×1 | 必须全部通过 |
| 协议测试 | `test_proto_XXX.c` | A2A/MCP/OpenAI 各 1 个测试 | 必须全部通过 |
| Hook 测试 | `test_hook_*.c` | 注册/触发/拦截/超时/fail-open 各 1 个 | 必须全部通过 |
| 配置测试 | `test_config_*.c` | 加载/热重载/环境变量覆盖/SecretRef/校验 各 1 个 | 必须全部通过 |
| Plugin 测试 | `test_plugin_*.c` | 发现/安装/初始化/权限/卸载 各 1 个 | 必须全部通过 |
| 路由测试 | `test_router_*.c` | 成本感知/降级链/重试/缓存 各 1 个 | 必须全部通过 |
| 契约测试 | `tests/contract/` | 每个 API 契约条款验证 | 必须全部通过 |

### 12.3 测试覆盖率要求

| 模块 | 行覆盖率 | 分支覆盖率 |
|------|:---:|:---:|
| atoms/ | ≥ 60% | ≥ 40% |
| daemon/ | ≥ 50% | ≥ 30% |
| 12 条连接线 | 100% | 100% |
| Hook 系统 | ≥ 70% | ≥ 50% |
| LLM 路由 | ≥ 70% | ≥ 50% |
| ecosystem/ (Python) | ≥ 70% | — |
| 关键模块（corekern/coreloopthree/cupolas） | ≥ 85% | ≥ 60% |

### 12.4 测试环境隔离

**规范**：所有测试用例必须在隔离的沙箱环境中运行，不依赖外部网络、文件系统或真实 LLM 服务。

**规范**：外部依赖必须使用 mock 或 fake 实现，确保测试可重复、无副作用。

**规范**：CI 中必须包含"干净环境"测试（如 Docker 容器中运行），避免环境污染导致的假阳性。

**BAN-227**：集成测试中禁止发起真实 LLM API 调用。

**检测方式**：CI 中启用 `--no-network` 模式运行测试。

### 12.5 模糊测试规范

**规范**：对解析器与外部输入持续做模糊测试（libFuzzer/AFL++），并保留回归 corpus。

**规范**：对关键路径提供 microbenchmarks，并对比回归。

### 12.6 内存安全测试规范

**规范**：CI 中必须运行 ASan + LSan 构建，任何内存安全违规（越界、use-after-free、泄漏）视为构建失败。

**规范**：每周运行 Valgrind memcheck 全量扫描，零泄漏零错误为目标。

**规范**：MemorySanitizer (MSan) 构建作为独立 CI job，检测未初始化内存读取。

**内存压力测试**：

| 测试场景 | 方法 | 通过标准 |
|---------|------|---------|
| OOM 触发 | 限制容器内存至 `max_alloc_mb` 的 90% | OOM 回调正确触发，系统优雅降级 |
| OOM 恢复 | 触发 OOM 后释放内存 | 系统恢复正常服务 |
| 长时间运行 | daemon 运行 24 小时 | RSS 增长 < 5% |
| 内存碎片 | 随机大小分配/释放 100 万次 | 碎片率 < 15% |
| IPC 共享内存竞争 | 16 daemon 并发 IPC | 无死锁、无泄漏 |

**BAN-256**：CI 中 ASan/LSan 违规禁止合并，零容忍。

---

## 第十三章：MemoryRovol 独立库规范

### 13.1 独立性原则

**规范**：MemoryRovol 拥有独立的 `CMakeLists.txt`、独立的 CI workflow、独立的版本号、独立的构建产物。

**规范**：`agentos/atoms/memoryrovol/` 仅保留桥接层（`memoryrovol_bridge.c/h`），不包含任何 MemoryRovol 核心实现。

### 13.2 提供商接口规范

**规范**：MemoryRovol 提供的 `libmemoryrovol.a` 必须实现 `memory_provider.h` 中定义的全部接口。版本不匹配时编译报错。

### 13.3 记忆提取规则（源自 agent-memory-demo 7 规则）

| 规则 | 内容 | 违规后果 |
|------|------|---------|
| R1 原子性 | 每条事实必须是单一不可分的信息单元 | 非原子事实导致检索噪声 |
| R2 第三人称 | 始终使用第三人称视角 | 第一人称导致记忆归属混乱 |
| R3 上下文丰富 | 包含所有必要的上下文信息 | 缺失上下文导致记忆不可用 |
| R4 噪声过滤 | 忽略问候语和重复信息 | 噪声记忆浪费存储和检索资源 |
| R5 结构化输出 | 仅输出有效的 JSON 数组 | 非结构化输出无法自动处理 |
| R6 分类 | 每条事实归属 6 类之一：personal/work/preference/technical/project/decision | 未分类事实无法有效检索 |
| R7 空结果处理 | 无新事实时返回空数组 `[]` | 无空结果处理导致解析错误 |

### 13.4 限流规范

**规范**：记忆写入操作必须通过 RateLimiter 限流（默认 50 次/分钟），防止高频写入导致存储过载。

### 13.5 优雅降级

**规范**：所有 MemoryRovol 外部依赖失败时降级到无记忆模式，禁止崩溃。

### 13.6 遗忘机制规范（源自 ARCHITECTURAL_PRINCIPLES C-4）

**规范**：遗忘策略必须是可配置的，支持 NONE/EBBINGHAUS/LINEAR/ACCESS_BASED 四种策略。

**规范**：遗忘阈值必须可调（默认 0.3，低于此值归档）。

**规范**：归档数据必须可复活（通过检索重新激活）。

**遗忘公式**：`R(t) = e^(-t/τ)`，τ 默认 7 天。

### 13.7 MemoryRovol 内存预算规范

**规范**：MemoryRovol 各层必须设置内存预算上限，超限时触发降级。

| 层级 | 默认内存预算 | 超限行为 |
|------|------------|---------|
| L1 原始卷 | 512 MB | 拒绝新写入，触发压缩 |
| L2 特征层 | 1024 MB | 驱逐低频向量索引 |
| L3 结构层 | 256 MB | 暂停实体绑定，降级到 L2 检索 |
| L4 模式层 | 128 MB | 暂停聚类分析，保留已有模式 |
| 检索缓存 | 64 MB | LRU 驱逐 |

**规范**：MemoryRovol 总内存占用不得超过 `agentrt.yaml` 中 `kernel.memory.max_alloc_mb` 的 40%。

### 13.8 MemoryRovol 内存压力处理

**规范**：嵌入计算内存不足时，降级到更小的嵌入模型（如从 1536 维降至 768 维）。

**规范**：向量索引缓存内存不足时，按 LRU 策略驱逐，驱逐后查询降级到精确扫描。

**规范**：L1 存储写入超出预算时，触发压缩（zstd）和遗忘引擎（prune），释放空间后重试。

---

## 第十四章：Prompt 工程规范

> **来源**：综合 openJiuwen、agent-memory-demo、hermes-agent 的工程实践。详见 v22.0 第十四章，内容不变。

### 14.1 Prompt 模板格式规范

**规范**：所有 Prompt 模板必须使用 YAML 格式，遵循 `PromptSpec` Schema。

**规范**：每个 Prompt 模板必须包含 `metrics` 字段，声明目标 precision/recall/hallucination_rate。

**BAN-228**：Prompt 模板禁止硬编码 API Key 或敏感信息。

### 14.2 Prompt 调优规范

**规范**：调优必须基于标注数据集（`JSONL` 格式）。

**规范**：A/B 对比测试必须记录 statistical significance（p < 0.05）。

**规范**：调优后必须产生调优报告（`tune_report.yaml`）。

**调优参数**：`max_iterations`（默认10）、`parallel_candidates`（默认5）、`early_stop_patience`（默认3）、`significance_level`（默认0.05）。

### 14.3 Prompt 版本管理

**规范**：每个 Prompt 模板有独立的语义版本号。

**规范**：Prompt 版本注册表 `registry.yaml` 记录所有模板的版本历史和评测结果。

**规范**：Prompt 变更必须通过 A/B 测试验证，禁止未经验证直接替换生产 Prompt。

---

## 第十五章：安全规范

> **来源**：综合 atomcode、openclaw、claude-code、Cupolas 的工程实践。详见 v22.0 第十五章，内容不变。

### 15.1 工具调用审批链

**三级审批模型**：AutoApprove / RequireApproval / RequireApprovalAlways

**路径安全检查**：工作区边界 + 敏感路径 + 符号链接逃逸检测

### 15.2 沙箱隔离规范

| 后端 | 隔离级别 | 适用场景 |
|------|---------|---------|
| Docker 容器 | 强隔离 | 生产环境、不可信 Plugin |
| SSH 远程 | 网络隔离 | 远程执行 |
| 本地进程 | 弱隔离 | 开发环境 |

### 15.3 安全审计

**规范**：`agentrt security audit` 命令必须执行 10 项检查（API Key 泄露、SecretRef 合规、权限过度声明、路径穿越、依赖漏洞、网络暴露、审计日志完整性、配置默认值安全、Hook 安全、Plugin 完整性）。

### 15.4 Cupolas 纵深防御集成

**规范**：所有外部请求必须经过 Cupolas 四阶段防护链：

```
输入净化 (Sanitizer) → 权限裁决 (Permission) → 网络过滤 (Network Security) → 审计记录 (Audit)
```

**规范**：审计日志使用 SHA-256 哈希链，确保不可篡改。

---

## 第十六章：可观测性规范

### 16.1 必需指标

| 指标名 | 类型 | 标签 | 说明 |
|--------|------|------|------|
| `airy_cognition_latency_ms` | Histogram | `agent_id` | 认知阶段延迟 |
| `airy_llm_request_duration_ms` | Histogram | `provider`, `model` | LLM 请求延迟 |
| `airy_llm_cost_usd_total` | Counter | `provider` | LLM 累计费用 |
| `airy_tool_call_total` | Counter | `tool_name`, `status` | 工具调用次数 |
| `airy_memory_operations_total` | Counter | `layer`, `operation` | 记忆操作次数 |
| `airy_hook_execution_ms` | Histogram | `hook_name`, `event` | Hook 执行延迟 |
| `airy_connection_health` | Gauge | `connection_id` | 连接线健康状态 |
| `airy_plugin_lifecycle_total` | Counter | `plugin_name`, `event` | Plugin 生命周期事件 |
| `airy_llm_retry_total` | Counter | `provider`, `error_category` | LLM 重试次数 |
| `airy_config_reload_total` | Counter | `status` | 配置重载次数 |

### 16.2 日志格式规范

**规范**：所有服务日志必须为 JSON 格式，包含以下字段：

| 字段 | 类型 | 必须 | 说明 |
|------|------|:---:|------|
| `timestamp` | string | 是 | ISO 8601 格式，精确到毫秒 |
| `level` | string | 是 | DEBUG/INFO/WARN/ERROR/FATAL |
| `service` | string | 是 | 服务名（如 `llm_d`、`hook_d`） |
| `module` | string | 否 | 模块名（如 `coreloopthree.cognition`） |
| `function` | string | 否 | 函数名 |
| `message` | string | 是 | 人类可读消息 |
| `trace_id` | string | 是 | 全链路追踪 ID（W3C Trace Context） |
| `span_id` | string | 否 | 当前 span ID |
| `request_id` | string | 否 | 请求 ID |
| `err_code` | string | 否 | 错误码 |
| `context` | object | 否 | 结构化上下文信息 |

**规范**：跨 daemon 请求必须在 IPC Bus 层注入 `trace_id`，确保全链路追踪。

**规范**：高吞吐场景需实现日志采样或汇总策略以防日志风暴，但错误日志应保持完整。

### 16.3 SSE 流式传输规范

**规范**：SSE 流式传输使用 AsyncStreamQueue + StreamEmitter 架构。

**BAN-229**：SSE 流式传输必须实现取消信号传播。

### 16.4 健康检查规范

**规范**：每个 daemon 必须实现 `/healthz`（liveness）和 `/readyz`（readiness）端点。

**规范**：健康检查必须包含依赖项状态，不能只报告自己健康。

**规范**：指标采用 Prometheus exposition 格式，提供 `/metrics` 端点。

**内存可观测性必需指标**：

| 指标名 | 类型 | 说明 |
|--------|------|------|
| `airy_memory_rss_bytes` | Gauge | 各 daemon 常驻内存 |
| `airy_memory_heap_bytes` | Gauge | 堆内存使用量 |
| `airy_memory_pool_utilization` | Gauge | 内存池使用率（0~1） |
| `airy_oom_events_total` | Counter | OOM 事件计数（按级别标签） |
| `airy_memory_alloc_bytes_total` | Counter | 累计分配字节数 |
| `airy_memory_free_bytes_total` | Counter | 累计释放字节数 |
| `airy_memory_gc_pause_ms` | Histogram | GC 暂停时间（MemoryRovol） |
| `airy_memory_pressure_level` | Gauge | 当前内存压力级别（0~4） |

---

## 第十七章：外部技术吸收规范

### 17.1 吸收原则

1. **命名隔离**：所有融入技术必须赋予 AgentRT 体系的新名称
2. **接口重设计**：不复制参考项目的接口定义、类型结构、文件结构
3. **设计哲学归属**：新技术必须映射到五维正交设计体系
4. **吸收记录**：所有吸收必须有对应的命名映射表

### 17.2 18 项参考资产映射表

| 参考技术 | AgentRT 名称 | 融入位置 | 吸收状态 |
|---------|-------------|---------|:---:|
| openclaw Plugin System | AgentRT 四型插件 | Rust SDK `plugin.rs` | 已实现 |
| openclaw Hook System | AgentRT Hook 系统 | `hook_d/` | 0.1.1 新建 |
| openclaw YAML Schema | Manager Schema 体系 | `manager/schema/` | 已实现 |
| openclaw Agent Lanes | AgentRT 执行通道 | `corekern/scheduler` | 已实现 |
| openclaw Boot | AgentRT 启动引导 | `daemons/common/` | 已实现 |
| openclaw Soul | AgentRT 设计哲学 | `Docs/DESIGN_PHILOSOPHY.md` | 0.1.1 新建 |
| claude-code Plugin | AgentRT 四型插件 | Rust SDK | 已实现 |
| openJiuwen Pregel | TaskFlow | `atoms/taskflow/` | 已实现 |
| openJiuwen Agent Store | OpenLab Markets | `openlab/markets/` | 已实现 |
| openJiuwen A2A | AgentRT A2A | `gateway_d/protocol/` | 已实现 |
| openJiuwen Checkpointer | AgentRT 会话恢复 | `daemons/common/checkpoint` | 已实现 |
| openJiuwen SSE | LLM 流式 | `llm_d/providers/` | 已实现 |
| openJiuwen Prompt 调优 | Prompt 评测框架 | `ecosystem/prompts/tuner/` | 0.1.1 新建 |
| openJiuwen MCP | AgentRT MCP | `gateway_d/protocol/` | 已实现 |
| atomcode LlmProvider | LLM Provider ops_t | `llm_d/providers/provider.h` | 已实现 |
| atomcode TurnRunner | 工具审批链 | Cupolas SafetyGuard | 0.1.1 连接 |
| atomcode CLI/TUI | AgentRT CLI + TUI | `sdk/cli/` + `sdk/tui/` | 0.1.1 新建 |
| hermes-agent 成本路由 | AgentRT 成本路由 | `llm_d/router/` | 0.1.1 新建 |

---

## 第十八章：团队非交叉任务规范

### 18.1 三权分立边界

| 团队 | 唯一拥有的代码目录 | 不得修改的目录 |
|------|------------------|--------------|
| 团队A | `agentos/atoms/`、`agentos/cupolas/`、`agentos/daemons/`、`MemoryRovol/` | `ecosystem/`、`sdk/` |
| 团队B | `ecosystem/`、`sdk/`、`agentos/gateway/`、`agentos/heapstore/`、`agentos/protocols/` | `agentos/atoms/`、`agentos/cupolas/` |
| 团队C | `deploy/`、`scripts/`、`tests/`、`Docs/` | `agentos/`（除 tests/）、`ecosystem/`、`sdk/` |

### 18.2 接口契约机制

1. 接口需求方提出接口需求文档
2. 接口提供方定义头文件接口
3. 接口文档冻结后，供需双方各自独立开发
4. 团队C 编写集成测试验证接口契约
5. 接口变更需要双方 team lead 审批

### 18.3 每日交叉检查点

| 检查点 | 负责人 | 频率 |
|--------|-------|------|
| 团队A 编译（C 全量 + MemoryRovol 桥接） | 团队A | 每日 |
| 团队B 编译（Python + Rust + Go + TypeScript） | 团队B | 每日 |
| 团队C CI 全量流水线 | 团队C | 每次 PR |
| 12 条连接线集成测试 | 团队C | 每次 PR |
| BAN 规则全量扫描 | 团队C | 每次 PR |
| 架构原则合规性检查 | 团队C | 每周 |
| 67 项 ACC 验收标准 | 团队C | 阶段结束后 |

---

## 第十九章：契约规范引用

> **说明**：本节汇总 [50-specifications/10-contracts/](../Docs/50-specifications/10-contracts/) 下的契约规范，工程标准手册不重复内容，但强制引用。

| 契约文档 | 内容 | 工程标准关联 |
|---------|------|------------|
| [agent_contract.md](../Docs/50-specifications/10-contracts/01-agent-contract.md) | Agent 能力描述文件格式（JSON Schema） | §8 Plugin 系统 |
| [skill_contract.md](../Docs/50-specifications/10-contracts/02-skill-contract.md) | Skill 接口、能力、权限元数据格式 | §8 Plugin 系统 |
| [protocol_contract.md](../Docs/50-specifications/10-contracts/03-protocol-contract.md) | 协议适配层接口契约 | §3.6 发布流程 |
| [syscall_api_contract.md](../Docs/50-specifications/10-contracts/04-syscall-api-contract.md) | 系统调用接口契约 | §4.10 API/ABI 管理 |
| [logging_format.md](../Docs/50-specifications/10-contracts/05-logging-format.md) | 统一日志格式契约 | §16.2 日志格式 |
| [glossary_index.md](../Docs/50-specifications/10-contracts/06-glossary-index.md) | 术语索引 | §1.6 术语规范 |

---

## 第二十章：BAN 规则完整汇总

### 20.1 v0.1.0 继承规则（BAN-001 ~ BAN-190）

v0.1.0 的 190 条 BAN 规则全数保留，详见 v0.1.0 工程标准规范手册。以下按类别汇总：

| 类别 | 编号范围 | 数量 | 关键规则 |
|------|---------|------|---------|
| 禁止模式 | BAN-01~BAN-13 | 13 | 占位返回、假指针、桩函数、假数据 |
| 内存管理 | BAN-001~BAN-030 | 30 | 禁止裸 malloc/free、溢出检查、null 终止 |
| 日志系统 | BAN-060~BAN-072 | 13 | 统一 SVC_LOG_*/AIRY_LOG_*、禁止 printf |
| 错误处理 | BAN-073~BAN-085 | 13 | 禁止 return -1、错误上下文传播 |
| Python 规范 | BAN-080~BAN-099 | 20 | 禁止 print()、裸 except、assert |
| 桩函数 | BAN-100~BAN-110 | 11 | 禁止桩函数和简化实现 |
| 内存安全 | BAN-151~BAN-162 | 12 | 溢出检查、strncpy null 终止、memcpy 前置校验 |
| 其他 | BAN-031~BAN-059, BAN-111~BAN-150, BAN-163~BAN-190 | 91 | 编码规范、命名规范、文档规范等 |

### 20.2 v0.1.1 新增规则（BAN-191 ~ BAN-245）

| 编号 | 规则 | 类别 | 检测方式 | 来源 |
|------|------|------|---------|------|
| BAN-191 | 禁止 `head -z` 管道 | CI/CD | `quality-gate.sh` | v0.1.0 L-31 |
| BAN-192 | 安全扫描禁止宽泛正则 | 安全 | `security_check.py` | v0.1.0 L-32 |
| BAN-193 | 危险函数扫描必须用 `\b` 词边界 | 安全 | `ban_scan.sh` | v0.1.0 L-33 |
| BAN-194 | 构建依赖步骤禁止 `continue-on-error` | CI/CD | CI yaml 审计 | v0.1.0 L-35 |
| BAN-195 | Feature Test Macros 必须在 CMake 级定义 | 编译 | CMake 检查 | v0.1.0 L-36 |
| BAN-196 | 错误码禁止局部 `#define` | 错误处理 | `check_error_codes.sh` | v0.1.0 L-37 |
| BAN-197 | 连接线必须有集成测试 | 测试 | `check_connection_tests.sh` | v0.1.1 L-17 |
| BAN-198 | 连接线接口变更必须同步测试 | 测试 | CI | v0.1.1 L-17 |
| BAN-199 | 连接线测试必须 4 路径覆盖 | 测试 | 测试文件审计 | v0.1.1 L-17 |
| BAN-200 | manager/openlab 迁移必须通过 pytest | Python | CI | v0.1.1 L-39 |
| BAN-201 | Manager Schema 与 agentrt.yaml 双向同步 | 配置 | `schema_diff.py` | v0.1.1 L-39 |
| BAN-202 | OpenLab 与 market_d 契约一致性 | 协议 | 集成测试 | v0.1.1 L-39 |
| BAN-203 | CLI 必须用 clap crate | Rust | `cargo check` | atomcode |
| BAN-204 | TUI 必须用 ratatui crate | Rust | `cargo check` | atomcode |
| BAN-205 | Rust 生产代码禁止裸 panic | Rust | `clippy::panic` | atomcode |
| BAN-206 | FFI unsafe 块必须参数校验 | Rust | `clippy::undocumented_unsafe_blocks` | atomcode |
| BAN-207 | Plugin permissions 与 SafetyGuard 守卫对应 | 安全 | 集成测试 | atomcode |
| BAN-208 | Plugin 生命周期超时保护 | 安全 | 集成测试 | atomcode |
| BAN-209 | Hook 注册必须统一接口 | Hook | 代码审查 | atomcode+openclaw |
| BAN-210 | Hook 执行超时保护 | Hook | 集成测试 | atomcode |
| BAN-211 | 外部输入必须经过 Sanitizer 净化 | 安全 | `ban_scan.sh` | atomcode |
| BAN-212 | 文件路径必须验证工作区边界 | 安全 | `ban_scan.sh` | atomcode |
| BAN-213 | API Key/OAuth Token 日志脱敏 | 安全 | `security_check.py` | atomcode |
| BAN-214 | Python 库代码禁止 print() | Python | `ruff T201` / pylint | Python编码标准 |
| BAN-215 | API 边界必须校验输入 | Python | pylint + 代码审查 | Python编码标准 |
| BAN-216 | 错误处理必须使用结构化异常 | Python | ruff + 代码审查 | Python编码标准 |
| BAN-217 | Release 构建禁止 panic=unwind | Rust | CI Cargo.toml 检查 | atomcode |
| BAN-218 | Hook 必须 fail-open | Hook | 集成测试 | atomcode |
| BAN-219 | Plugin 必须包含 manifest | Plugin | CI 文件检查 | claude-code |
| BAN-220 | Plugin 安装必须 SHA-256 校验 | 安全 | 集成测试 | openclaw |
| BAN-221 | 危险模式 Plugin 需人工审批 | 安全 | 集成测试 | claude-code |
| BAN-222 | LLM 重试禁止固定间隔 | 路由 | `ban_scan.sh` | hermes-agent |
| BAN-223 | Prompt 缓存上下文不可变 | 路由 | 代码审查 | hermes-agent |
| BAN-224 | 敏感配置必须 SecretRef | 配置 | `config_validator.py` | openclaw |
| BAN-225 | 配置热重载不得中断进行中操作 | 配置 | 集成测试 | openclaw |
| BAN-226 | 目录移动后必须验证 4 构建系统 | 构建 | CI | v0.1.1 L-39 |
| BAN-227 | 集成测试禁止真实 LLM 调用 | 测试 | CI --no-network | ARCHITECTURE E-8 |
| BAN-228 | Prompt 模板禁止硬编码敏感信息 | Prompt | `security_check.py` | hermes-agent |
| BAN-229 | SSE 流必须支持取消信号传播 | 可观测性 | 集成测试 | openJiuwen |
| BAN-230 | 错误分类器必须覆盖全部 LLM 错误 | 路由 | 代码审查 | hermes-agent |
| **BAN-231** | 错误码必须在正确分段范围内注册 | 错误处理 | `check_error_codes.sh` | TERMINOLOGY |
| **BAN-232** | 错误消息禁止仅含错误码，必须有上下文和修复建议 | 错误处理 | `check_error_message_format.py` | ARCH A-2 |
| **BAN-233** | 禁止 TOCTOU 竞态（access+open/stat+open） | 安全 | `ban_scan.sh` | C安全编码标准 |
| **BAN-234** | 信号处理器禁止调用非异步信号安全函数 | 安全 | 代码审查 + `ban_scan.sh` | C安全编码标准 |
| **BAN-235** | 禁止用户输入作为格式化字符串 | 安全 | `-Wformat=2` | C安全编码标准 |
| **BAN-236** | 禁止格式化字符串中使用 %n | 安全 | `-Wformat=2` | C安全编码标准 |
| **BAN-237** | dlopen 必须使用绝对路径，禁止依赖 LD_LIBRARY_PATH | 安全 | `ban_scan.sh` | C安全编码标准 |
| **BAN-238** | 禁止有符号/无符号整数隐式转换 | 安全 | `-Wsign-compare -Wsign-conversion` | C安全编码标准 |
| **BAN-239** | Python 禁止裸 except: | Python | `ruff E722` | Python编码标准 |
| **BAN-240** | Python 禁止 except 块中 pass 且无日志 | Python | 代码审查 | Python编码标准 |
| **BAN-241** | Python 禁止生产代码中使用 assert | Python | `ruff S101` | Python编码标准 |
| **BAN-242** | 禁止使用 C99 VLA 变长数组 | 编译 | `ban_scan.sh` | CROSS-02 |
| **BAN-243** | 禁止直接使用 POSIX 线程 API | 编译 | `ban_scan.sh` | CROSS-01 |
| **BAN-244** | 禁止直接使用 POSIX 时间函数 | 编译 | `ban_scan.sh` | CROSS-03 |
| **BAN-245** | 禁止使用 GCC 扩展语法 | 编译 | 代码审查 | CROSS-04 |
| **BAN-246** | 函数返回指针必须标注 @ownership | 内存管理 | Doxygen 检查 | 内存所有权模型 |
| **BAN-247** | 共享内存对象禁止裸 free，必须 refcount_release | 内存管理 | `ban_scan.sh` | 引用计数规范 |
| **BAN-248** | 引用计数操作必须使用 _Atomic + acq_rel | 内存管理 | 代码审查 | 引用计数规范 |
| **BAN-249** | 超过 3 层嵌套资源分配必须使用 goto cleanup 或 AUTO_FREE | 内存管理 | 代码审查 | RAII 模式 |
| **BAN-250** | daemon 启动必须注册至少 WARNING + CRITICAL 两级 OOM 回调 | 内存管理 | CI 启动检查 | OOM 处理规范 |
| **BAN-251** | 关键路径分配必须使用重试或预分配，不得 OOM 直接崩溃 | 内存管理 | 代码审查 | OOM 处理规范 |
| **BAN-252** | 敏感数据释放禁止 AIRY_FREE，必须 AIRY_SECURE_FREE | 内存管理 | `security_check.py` | 安全释放 |
| **BAN-253** | 并发计数器不同线程写字段必须 _Alignas(64) 分离 | 内存管理 | 代码审查 | 缓存行优化 |
| **BAN-254** | daemon 24h soak test RSS 增长 > 5% 视为内存泄漏 | 内存管理 | CI soak test | 泄漏检测 |
| **BAN-255** | 所有分配必须在 memory_stats_reporter 统计覆盖内 | 内存管理 | `ban_scan.sh` | 统计追踪 |
| **BAN-256** | CI 中 ASan/LSan 违规禁止合并 | 测试 | CI | 内存安全测试 |

### 20.3 v3.0~v3.5 新增规则（BAN-257~BAN-340，跨章节汇总）

v3.0~v3.5 期间新增的 BAN-257~BAN-340 共 84 项规则分散在第二十八/三十一/三十三/三十四/三十五章中定义，本节汇总索引:

| 编号范围 | 数量 | 定义位置 | 主题 |
|---------|:---:|---------|------|
| BAN-257~BAN-290 | 34 | 第二十八章 §28 | v3.0 双思考系统/内核安全/部署/最佳实践 |
| BAN-291~BAN-310 | 20 | 第三十一章 §31 | v24.4 统一打印/日志系统 |
| BAN-311~BAN-319 | 9 | 第三十三章 §33 | v24.7 微内核架构方案 A |
| BAN-320~BAN-327 | 8 | 第三十四章 §34 | v24.7 开放标准规范 |
| BAN-328~BAN-340 | 13 | 第三十五章 §35.11 | v25.0 v3.5 唯一奠基版本（CoreKern 精简 + taskflow + SDK + SPDX + 行数 + CCN） |

### 20.4 v4.0/v4.1/v4.2 新增规则（BAN-341~BAN-361，跨章节汇总）

v4.0/v4.1/v4.2 新增的 BAN-341~BAN-361 共 21 项规则分散在 §11.6/§11.7/第三十六/三十七/三十八章中定义，本节汇总索引:

| 编号范围 | 数量 | 定义位置 | 主题 |
|---------|:---:|---------|------|
| **BAN-341~BAN-344** | 4 | §11.6.3 | **改名彻底约束**（兼容别名头/airy_ 残留/daemon 残留/`*_d` 改名） |
| **BAN-345~BAN-348** | 4 | §11.7.7 | **38 仓拆分约束**（顺序/agentrt 继承/sdk-xx 命名/小写） |
| **BAN-349~BAN-350** | 2 | §36.10 | **38 仓构建约束**（独立构建失败/跨平台降级） |
| **BAN-351~BAN-356** | 6 | §37.7 | **生产就绪约束**（无 SBOM/单平台/Soak 跳过/安全降级/149 验收/cosign 跳过） |
| **BAN-357~BAN-361** | 5 | §38.9/§38.10 | **AirymaxOS 工程约束**（README/文档分离/同源独立/子仓命名/Linux 6.6 兼容性） |

**v4.0/v4.1/v4.2 BAN 规则完整清单**:

| 编号 | 规则 | 定义位置 |
|------|------|---------|
| BAN-341 | 禁止保留 `airy_compat_aliases.h` 兼容别名头 | §11.6.3 |
| BAN-342 | 禁止改名后留有 airy_ 前缀残留 [已部分废止：airy_ 部分废止，agentos_* 清零保留] | §11.6.3 |
| BAN-343 | 禁止 daemon 模块名残留（应为 daemons） | §11.6.3 |
| BAN-344 | 禁止进程二进制名 `*_d` 改名 | §11.6.3 |
| BAN-345 | 禁止不按 7 阶段顺序拆分 | §11.7.7 |
| BAN-346 | 禁止 agentrt 管理仓不继承原 AgentRT url | §11.7.7 |
| BAN-347 | 禁止 sdk 子仓不使用 sdk-xx 命名 | §11.7.7 |
| BAN-348 | 禁止目录名包含大写字母 | §11.7.7 |
| BAN-349 | 禁止 38 仓中任何一仓构建失败 | §36.10 |
| BAN-350 | 禁止跨平台编译降级 | §36.10 |
| BAN-351 | 禁止无 SBOM 发布 | §37.7 |
| BAN-352 | 禁止单平台发布 | §37.7 |
| BAN-353 | 禁止 Soak Test 跳过 | §37.7 |
| BAN-354 | 禁止安全审计降级 | §37.7 |
| BAN-355 | 禁止 149 项验收有 1 项 FAIL | §37.7 |
| BAN-356 | 禁止跳过 cosign 签名 | §37.7 |
| BAN-357 | 禁止 0.1.1 中 agentrt-linux 仓库无 README.md 或 README 未声明 openEuler 参考规范 + 微内核设计思想 | §38.9 |
| BAN-358 | 禁止 OS 设计文档放置在 docs-closed/（必须放置在 docs/AirymaxOS/） | §38.9 |
| BAN-359 | 禁止 AirymaxOS 内核态代码污染 agentrt 用户态跨平台路径（IRON-9） | §38.9 |
| BAN-360 | 禁止 AirymaxOS 子仓名不使用 airymaxos- 前缀 | §38.9 |
| BAN-361 | 禁止引用 Linux 7.0 专属特性作为 Linux 6.6 原生能力（PREEMPT_LAZY / Rust 正式转正 / MGLRU 2.0 / XFS 自修复 / eBPF 签名验证 / sched_ext（Linux 6.15+）等） | §38.10 |

### 20.5 BAN 规则检测方式汇总

| 检测方式 | 覆盖规则 | 执行时机 |
|---------|---------|---------|
| `quality-gate.sh` | BAN-191, BAN-193, BAN-211, BAN-212, BAN-222, BAN-233, BAN-237, BAN-242~244 | 每次 PR |
| `security_check.py` | BAN-192, BAN-213, BAN-228 | 每次 PR |
| `ban_scan.sh` | BAN-193, BAN-211, BAN-212, BAN-222, BAN-233, BAN-234, BAN-237, BAN-242~244 | 每次 PR |
| `check_error_codes.sh` | BAN-196, BAN-231 | 每次 PR |
| `check_connection_tests.sh` | BAN-197 | 每次 PR |
| `check_error_message_format.py` | BAN-232 | 每次 PR |
| `config_validator.py` | BAN-224 | 每次 PR |
| `cargo clippy` | BAN-205, BAN-206 | 每次 PR |
| `cargo check` | BAN-203, BAN-204 | 每次 PR |
| CI yaml 审计 | BAN-194 | 每次 PR |
| CMake 检查 | BAN-195 | 每次 PR |
| CI Cargo.toml 检查 | BAN-217 | 每次 PR |
| CI 文件检查 | BAN-219 | 每次 PR |
| 编译选项 `-Wformat=2` | BAN-235, BAN-236 | 每次构建 |
| 编译选项 `-Wsign-compare` | BAN-238 | 每次构建 |
| 集成测试 | BAN-207, BAN-208, BAN-210, BAN-218, BAN-220, BAN-221, BAN-225, BAN-229 | 每次 PR |
| 代码审查 | BAN-209, BAN-223, BAN-230, BAN-234, BAN-240, BAN-245 | PR 审查时 |
| pylint/ruff | BAN-214, BAN-215, BAN-216, BAN-239, BAN-240, BAN-241 | 每次 PR |
| CI --no-network | BAN-227 | 每次 PR |
| `schema_diff.py` | BAN-201 | 每次 PR |
| pytest | BAN-200 | 每次 PR |
| `scripts/check_principles_compliance.py` | 架构原则合规性 | 每周 |
| `scripts/check_api_complexity.sh` | 复杂度度量 | 每次 PR |
| `security_check.py` (扩展) | BAN-252 | 每次 PR |
| Doxygen @ownership 检查 | BAN-246 | 每次 PR |
| CI 启动检查 | BAN-250 | 每次部署 |
| CI soak test (分层: 4h PR / 24h 每周 / 72h 发布前) | BAN-254 | 分层执行 |
| ASan/LSan CI job | BAN-256 | 每次 PR |

---

## 第二十一章：智能体协作规范（v24.2 新增）

### 21.1 跨团队合约文件规范

所有跨团队接口必须通过合约文件（`contracts/`）定义，优先于任何代码实现。合约文件是团队间唯一的接口真理来源。

**文件命名**：`contracts/contract_<TEAM1>_<TEAM2>.h`

```
contracts/
├── contract_A_B.h    # 团队A ↔ 团队B 接口合约
├── contract_A_C.h    # 团队A ↔ 团队C 接口合约
└── contract_B_C.h    # 团队B ↔ 团队C 接口合约
```

**每份合约文件必须包含**：
1. **函数签名**（精确到参数类型、const 修饰、错误码）
2. **数据结构内存布局**（`static_assert` 验证 `sizeof`）
3. **时序图约束**（消息流的先后顺序，用 Doxygen 注释描述）
4. **错误码映射表**（源错误码 → 目标错误码的完整映射）
5. **版本号**（`#define CONTRACT_A_B_VERSION 0x00010000`）

**合约验证**：每合约附带 `contract_test.c` — 可独立编译运行的接口验证代码：

```c
// contracts/contract_test.c
#include "contract_A_B.h"
// 编译此文件即验证合约中所有符号可用
// CI: cmake --build build --target contract_tests
```

**合约版本变更规则**：
- 任何修改必须 bump 版本号（遵循 semver）
- CI 自动检测版本变更 → 在所有受影响团队的待合并 PR 上标记 "⚠️ Contract Changed"
- 不兼容的接口变更（MAJOR bump）需要所有受影响团队的 PR 同步合入

### 21.2 文件所有权锁（@owner 注解）

每个 `.c`/`.h` 文件必须在顶部添加所有权标记：

```c
// @owner: team-A
// @cross_team_deps: team-B(contract_A_B.h#L42), team-C(contract_A_C.h#L18)
```

**CI 强制执行**：
- 非拥有团队的 PR 修改 `@owner: team-X` 文件 → 自动拒绝
- 例外：`@cross_team_deps` 中声明的合约接口部分
- 例外：团队C 修改 `tests/`、`scripts/`、`Docs/`、根 `CMakeLists.txt`

### 21.3 智能体团队 BAN 规则策略

智能体团队不会产生"红灯疲劳"，因此 256 条 BAN 规则在 Phase 0 首日全量启用（不采用人类团队的三梯队渐进式策略）。

**BAN 规则分类**：
- **🤖 auto-fixable**（自动修复）：约 120 条 — 由 `scripts/dev/fix/run_all_fixes.sh` 批量修复
- **👤 manual-review**（人工审查）：约 136 条 — 需智能体理解业务语义后修复

**BAN 增量检测**：每个 PR 的 BAN 违规数不允许超过基线（`ban_baseline.json`）。增加违规 → 直接拒绝合并。

**自动修复脚本集**（位于 `scripts/dev/fix/`）：

| 脚本 | 修复范围 |
|------|---------|
| `fix_ban_printf.py` | printf/fprintf → SVC_LOG_*/AIRY_LOG_* |
| `fix_ban_return_neg1.py` | return -1 → AIRY_E* |
| `fix_ban_strcpy.py` | strcpy/strcat/sprintf → AIRY_STRNCPY |
| `fix_ban_malloc.py` |裸 malloc/free → AIRY_MALLOC/FREE |
| `fix_ban_sec22.py` | AIRY_FREE 后添加 ptr = NULL |
| `fix_ban_nested_if.py` | 深度嵌套 if → 辅助函数提取 |
| `fix_ban_missing_null.py` | 分配后添加 NULL 检查 |
| `run_all_fixes.sh` | 一键运行所有修复 |

### 21.4 智能体团队防冲突机制

| 机制 | 说明 | CI 阶段 |
|------|------|------|
| **文件所有权检查** | `check_ownership.sh` — 验证跨团队修改合规性 | 每次 PR |
| **合约版本 bump 通知** | 检测合约文件变更 → 自动标记受影响 PR | 每次 PR |
| **语义冲突检测** | `nm -g` 符号表比对合约期望符号 | 每次 PR |
| **修复循环检测** | 同一 PR 超过 3 轮 CI 修复 → 标记需人工介入 | 每次 PR |
| **风格一致性扫描** | clang-format 锁定 + clang-tidy 全量检查 | 每 Phase 结束 |
| **合约编译验证** | `cmake --build build --target contract_tests` | 每次 PR |

---

## 第二十二章：服务等级目标 (SLO) 与 Error Budget（v24.2 新增）

### 22.1 SLO 定义

| SLO | 目标值 | 测量窗口 | 测量方式 |
|-----|:---:|------|------|
| Agent 认知循环 P99 延迟 | < 2s | 24h 滑动窗口 | CoreLoopThree 内置计时 + Prometheus histogram |
| LLM 路由选择 P99 延迟 | < 100ms | 24h 滑动窗口 | llm_d router 计时 |
| 服务发现健康检查超时率 | < 0.1% | 24h 滑动窗口 | service_discovery 日志聚合 |
| daemon 崩溃率（每个） | < 0.01% | 每周 | Prometheus `airy_daemon_restart_total` |
| IPC Bus 消息丢失率 | < 0.001% | 每周 | IPC Bus 发送/接收计数器差值 |
| MemoryRovol 缓存命中率 | > 85% | 24h 滑动窗口 | MemoryRovol 内置计数器 |
| 端到端请求成功率 | > 99.9% | 24h 滑动窗口 | gateway Prometheus `http_requests_total{status!~"5.."}` |

### 22.2 Error Budget 策略

- **计算公式**：`Error Budget = (1 - SLO目标) × 总请求数`
- **耗尽条件**：Error Budget 降至 0%
- **耗尽策略**：冻结所有新功能发布 → 仅接受稳定性修复 PR → Error Budget 恢复 > 50% 后解除冻结
- **监控**：Prometheus `airy_error_budget_remaining` gauge

### 22.3 Soak Test 分层执行（替代 BAN-254 单一层级）

| 层级 | 触发时机 | 时长 | 通过标准 | CI 环境 |
|------|---------|:---:|------|------|
| **L1: PR 级** | 每次 PR | 4h | RSS 增长 < 2%（快速信号） | CI runner |
| **L2: 周级** | 每周定时 | 24h | RSS 增长 < 5%（正式门禁） | 专用 soak runner |
| **L3: 发布前** | M4 准出前 | 72h | RSS 增长 < 3%（最终确认） | 生产镜像环境 |

---

## 第二十三章：负载测试规范（v24.2 新增）

### 23.1 负载测试场景

| 场景 | 配置 | 时长 | 通过标准 |
|------|------|:---:|------|
| **稳态负载** | 100 QPS 持续 | 24h | 无 OOM、无进程崩溃、RSS 增长 < 5% |
| **突发负载** | 500 QPS 持续 5min → 恢复 | 30min | 恢复时间 < 30s、无请求丢失 |
| **级联故障** | 随机 kill 25% daemon | 1h | 服务发现 < 10s 摘除故障节点、请求路由 < 5s 切换 |
| **内存压力** | 逐步增加并发：10→50→100→200 QPS | 4h | Arena 不超过预算、tcache 不触发强制回收 |
| **长连接** | 100 并发 WebSocket 连接 × 2h | 2h | 无连接泄漏、无 websocketd OOM |

### 23.2 负载测试工具

- **推荐**：`k6`（脚本化负载生成）+ `vegeta`（HTTP 压测）
- **集成**：Phase 3 CI 中 `load-test` job — 自动执行稳态负载场景
- **报告**：每次负载测试输出 `load_test_report.json`（P50/P95/P99 延迟 + 吞吐量 + 错误率）

---

## 第二十四章：双思考系统工程规范（v3.0 新增）

> **来源**: 2025-2026 年双思考系统（Thinkdual）最新理论研究 + v3.0 穷尽审查发现
> **目标**: 确保双思考系统在超长工程任务中正确思考、输出正确方案

### 24.1 认知管线可达性规范（DT-01~DT-05）

| 规则 | 内容 | 检测方式 |
|------|------|---------|
| DT-01 | **plan_strategy 必须注入**：cognition engine 创建后必须调用 `airy_cognition_set_plan_strategy` 注入非 NULL 的规划策略 | 启动时断言 `engine->plan_strat != NULL` |
| DT-02 | **Phase 0-4 不可跳过**：认知管线的 5 个阶段必须顺序执行，任何阶段不得被 `goto process_fail` 跳过 | 集成测试：验证每阶段 step_complete 被调用 |
| DT-03 | **B6 输出必须打通**：Phase 2 的 `phase2_output` 必须写入 `task_node_output`，不得仅写入 ctx_window 后 FREE | 代码审查：grep `task_node_output` 赋值点 |
| DT-04 | **fallback 策略必须注入**：cognition engine 必须同时注入主策略和 fallback 策略 | 启动时断言 `engine->fallback_plan_strat != NULL` |
| DT-05 | **配置可覆盖**：plan_strategy 类型必须可通过 agentrt.yaml 的 `cognition.plan_strategy` 配置项覆盖 | 配置测试：修改 YAML 后验证策略切换 |

### 24.2 多模型验证规范（DT-06~DT-10）

> **理论依据**: MIT/ICLR 2026 Cross-Model Disagreement (TU=AU+EU)；AdversaBench 三法官面板

| 规则 | 内容 | 检测方式 |
|------|------|---------|
| DT-06 | **三模型独立**：S2/S1-verify/S1-expert 必须使用不同的 LLM 模型（`s2_model ≠ s1_verify_model ≠ s1_expert_model`） | 单元测试：断言三模型字段互不相同 |
| DT-07 | **跨模型分歧检测**：disagreement ≥ threshold 时必须触发 `coordinate()` 交叉验证 | 集成测试：构造分歧场景验证 coordinate 调用 |
| DT-08 | **温度差异化**：S2 temp=0.7（创造性）/ S1-verify temp=0.3（确定性）/ S1-expert temp=0.5（平衡） | 配置审查：验证温度设置 |
| DT-09 | **成本感知路由**：S1-verify 优先使用轻量模型（通过 llm_router 成本感知路由选择） | 集成测试：验证 router 选择便宜模型 |
| DT-10 | **日预算上限**：三模型调用的总 Token 成本不得超过日预算上限，超限自动降级为单模型 | 压力测试：模拟超预算场景验证降级 |

### 24.3 对抗式验证规范（DT-11~DT-15）

> **理论依据**: ICML 2026 Agentic Overconfidence（"find bugs" 比 "verify correctness" 降低过度自信 15pp）

| 规则 | 内容 | 检测方式 |
|------|------|---------|
| DT-11 | **对抗式 prompt**：S1 验证 prompt 必须使用 "find bugs/flaws" 对抗式框架，禁止 "verify correctness" 确认式 | 代码审查：grep `find.bug|find.flaw|critique` |
| DT-12 | **禁止字数打分**：LLM 不可用时禁止使用字数打分回退（content_len > N = acceptable），必须返回 ENOTSUP | 代码审查：grep `content_len` 在评分逻辑中 |
| DT-13 | **大声失败**：REJECT 不得静默丢弃，必须返回错误码 + 触发重试 | 集成测试：构造 REJECT 场景验证重试 |
| DT-14 | **最大修正轮数**：修正轮数上限 3 轮，超过后强制接受最佳方案（避免无限循环） | 单元测试：验证 3 轮后强制接受 |
| DT-15 | **置信度弃权**：置信度低于阈值（0.3）时弃权而非猜测（共形预测弃权） | 单元测试：低置信度场景验证弃权 |

### 24.4 循环检测规范（DT-16~DT-18）

> **理论依据**: Authon 循环防护（计数器循环检测无效，需语义级检测）

| 规则 | 内容 | 检测方式 |
|------|------|---------|
| DT-16 | **语义循环检测**：循环检测必须使用语义相似度（embedding 余弦相似度），不得仅依赖计数器 | 单元测试：构造语义重复验证检测 |
| DT-17 | **循环阈值**：语义相似度 ≥ 0.95 且连续出现 ≥ 2 次时判定为循环 | 配置审查：验证阈值设置 |
| DT-18 | **循环中断**：检测到循环后必须中断当前批判轮次，触发重规划或降级 | 集成测试：构造循环场景验证中断 |

### 24.5 桩函数零容忍规范（DT-19~DT-20）

| 规则 | 内容 | 检测方式 |
|------|------|---------|
| DT-19 | **禁止桩函数**：所有协调器（weighted/arbiter/majority）必须实现真实算法，禁止"返回原文"/"返回 inputs[0]"等桩逻辑 | 代码审查 + 单元测试：验证非桩逻辑 |
| DT-20 | **死代码零容忍**：所有定义的函数必须有至少一个生产代码调用点（非仅测试），`__attribute__((unused))` 标记的函数必须在 P4.8 中消除 | CI 检查：grep `__attribute__((unused))` 零命中 |

---

## 第二十五章：内核安全规范（v3.0 新增）

> **来源**: v3.0 atoms 内核层审查发现（F1-F5）+ 2025-2026 内核安全最佳实践
> **原则**: agentos/atoms 内核层必须绝对安全，零技术债务

### 25.1 OOM 处理规范（KER-01~KER-04）

| 规则 | 内容 | 检测方式 |
|------|------|---------|
| KER-01 | **OOM handler 必须激活**：kernel init 中必须调用 `airy_oom_init` + `airy_oom_config_apply`，生产代码不得跳过 | 启动日志验证：grep `OOM handler initialized` |
| KER-02 | **水位线必须 apply**：`oom_watermark_percent`（默认 85）必须通过 `airy_oom_config_apply` 应用到 handler，不得仅用于日志 | 代码审查：验证 apply 调用 |
| KER-03 | **分配器接入**：mempool/slab 分配器必须调用 `airy_oom_check_allocation`，不得绕过 OOM 检查 | 代码审查：grep `oom_check_allocation` 在分配路径 |
| KER-04 | **降级回调链**：所有 daemon 必须通过 `airy_register_degradation` 注册降级回调，OOM 触发时执行降级而非崩溃 | 集成测试：内存压力测试验证降级 |

### 25.2 heapstore 持久化规范（KER-05~KER-07）

| 规则 | 内容 | 检测方式 |
|------|------|---------|
| KER-05 | **BUILD_HEAPSTORE 必须定义**：CMake 必须通过 `target_compile_definitions` 定义 `BUILD_HEAPSTORE` 宏 | CMake 审查：验证宏定义 |
| KER-06 | **heapstore 必须链接**：`airy_syscall` 必须链接 `airy_heapstore` 库 | CMake 审查：验证 target_link_libraries |
| KER-07 | **integration_init 必须调用**：系统初始化时必须调用 `heapstore_integration_init`，session 等状态必须持久化 | 持久化测试：重启后 session 存在 |

### 25.3 ODR 违规防护规范（KER-08~KER-10）

> **理论依据**: C++ One Definition Rule + GCC -Wodr 检测

| 规则 | 内容 | 检测方式 |
|------|------|---------|
| KER-08 | **结构体单一定义**：同一结构体不得在多个翻译单元中有不兼容定义（如 taskflow_engine_s 双重定义） | CI 编译：`-Wodr` 零警告 |
| KER-09 | **函数签名一致**：函数声明与定义的参数数量/类型必须完全一致 | CI 编译：`-Wstrict-prototypes` 零警告 |
| KER-10 | **返回码不碰撞**：成功码（0）与错误码不得取相同值（如 `TASKFLOW_ERROR_RETRY == 0 == TASKFLOW_SUCCESS`） | 单元测试：断言 `ERROR_RETRY != SUCCESS` |

### 25.4 层级依赖规范（KER-11~KER-13）

| 规则 | 内容 | 检测方式 |
|------|------|---------|
| KER-11 | **内核不依赖上层**：atoms 内核层不得 `#include` daemon/cupolas 层头文件，不得链接上层服务库 | CMake 审查：atoms-core 无上层依赖 |
| KER-12 | **适配器接口**：atoms 需要上层功能时必须定义抽象接口（如 `cognition_llm_iface_t`），由 daemon 实现并注入 | 代码审查：验证接口抽象 |
| KER-13 | **CMake 分层**：atoms CMake 必须拆分为 `atoms-core`（无上层依赖）和 `atoms-bridge`（含适配器） | CMake 审查：验证分层 |

### 25.5 返回码语义规范（KER-14~KER-15）

| 规则 | 内容 | 检测方式 |
|------|------|---------|
| KER-14 | **失败必须返回非 0**：函数失败时必须返回非 0 错误码，禁止恒返回 SUCCESS（如 `taskflow_unit_execute_impl`） | 单元测试：构造失败场景验证返回码 |
| KER-15 | **返回码语义一致**：0=成功、非 0=错误的约定必须全项目一致，禁止逻辑反转（如 `if (!perm_ret)` 将授权误判为拒绝） | 代码审查：grep `if (!.*ret)` 模式审查 |

---

## 第二十六章：部署工程规范（v3.0 新增）

> **来源**: v3.0 Docker 部署审查发现（G1/G2/G4）+ 2025-2026 容器化最佳实践

### 26.1 Docker 构建规范（DEP-01~DEP-05）

| 规则 | 内容 | 检测方式 |
|------|------|---------|
| DEP-01 | **路径必须正确**：Dockerfile 中的 COPY 源路径必须与实际仓库结构一致（`agentrt/` 非 `AgentOS/`） | docker build 验证 |
| DEP-02 | **二进制必须存在**：Dockerfile CMD 引用的二进制必须在 CMake 中有对应 `add_executable` target | CI 检查：Dockerfile 二进制名 vs CMake target |
| DEP-03 | **多阶段构建**：Dockerfile 必须使用多阶段构建（builder + runtime），runtime 镜像不含编译工具链 | Dockerfile 审查 |
| DEP-04 | **镜像最小化**：runtime 镜像基于 `alpine` 或 `distroless`，不含 shell/包管理器（减少攻击面） | 镜像扫描：Trivy 零 HIGH/CRITICAL 漏洞 |
| DEP-05 | **.dockerignore**：必须配置 `.dockerignore` 排除 `build/`、`.git/`、`DocsClosed/` 等 | 文件检查 |

### 26.2 二进制命名规范（DEP-06~DEP-07）

| 规则 | 内容 | 检测方式 |
|------|------|---------|
| DEP-06 | **命名统一**：所有 daemon 二进制必须使用 `agentos-<name>-d` 命名（通过 `set_target_properties OUTPUT_NAME`） | CMake 审查：验证 OUTPUT_NAME |
| DEP-07 | **supervisor 引用一致**：supervisord.conf 中的二进制路径必须与 CMake 编译产物名完全一致 | 部署验证：supervisor 启动成功 |

### 26.3 端口分配规范（DEP-08~DEP-10）

| 规则 | 内容 | 检测方式 |
|------|------|---------|
| DEP-08 | **端口分配表**：项目必须维护统一的端口分配表（配置中心管理），各 daemon 监听端口互不冲突 | 配置审查：端口表无重复 |
| DEP-09 | **EXPOSE 一致**：Dockerfile EXPOSE 的端口必须与 daemon 实际监听端口一致 | Dockerfile 审查 |
| DEP-10 | **healthcheck 端口正确**：docker-compose healthcheck 中的端口必须与 daemon 实际监听端口一致 | 部署验证：healthcheck 通过 |

**v3.0 端口分配表**：

| daemons | 端口 | 用途 |
|--------|:----:|------|
| llm_d | 8080 | LLM 服务 TCP |
| tool_d | 8090 | 工具服务 TCP（避免与 gateway 冲突） |
| market_d | 8082 | 市场服务 TCP |
| sched_d | 8083 | 调度服务 TCP |
| info_d | 8086 | 信息服务 TCP（避免与 sched_d 冲突） |
| notify_d | 8084 | 通知服务 TCP |
| observe_d | 8085/metrics 9092 | 观测服务 TCP + metrics |
| monit_d | 9091 | 监控服务 TCP（避免与 observe_d metrics 冲突） |
| gateway_d | HTTP 9080/WS 9081 | 网关 HTTP + WebSocket（避免与 llm_d/tool_d 冲突） |

### 26.4 进程管理规范（DEP-11~DEP-12）

| 规则 | 内容 | 检测方式 |
|------|------|---------|
| DEP-11 | **supervisord 配置**：所有需要常驻的 daemon 必须在 supervisord.conf 中配置，含 autorestart/max_retries/startsecs | supervisord 审查 |
| DEP-12 | **就绪等待**：daemon 启动必须等待依赖就绪（如 llm_d 等待 config 加载），不得盲目并行启动 | 启动脚本审查 |

---

## 第二十七章：2025-2026 行业最佳实践对照（v3.0 新增）

> **来源**: 2025-2026 年软件工程行业最佳实践调研 + v3.0 穷尽审查对照

### 27.1 内存安全最佳实践

| 实践 | 行业标准（2025-2026） | Airymax 现状 | v3.0 要求 |
|------|----------------------|:----------:|---------|
| ASan/LSan CI | Google/Meta 全量 ASan CI | ✅ 已有 BAN-151~162 | 保持 |
| OOM handler 激活 | Linux kernel OOM killer 思想 | ❌ F1 从未 init | P3.19 修复 |
| 持久化 fsync | PostgreSQL WAL fsync 模式 | ❌ C4 无 fsync | P3.12 修复 |
| 内存数据库持久化 | SQLite WAL 模式 | ❌ C8 :memory: | P3.12 修复 |
| Arena 分配器 | jemalloc/tcmalloc arena | ✅ P1.19 已规划 | 保持 |

### 27.2 并发安全最佳实践

| 实践 | 行业标准（2025-2026） | Airymax 现状 | v3.0 要求 |
|------|----------------------|:----------:|---------|
| 原子操作 | C11 atomics / C++20 atomic_ref | ✅ atomic_compat.h | 保持 |
| 互斥锁粒度 | 细粒度锁 + 无锁数据结构 | ⚠️ 部分粗粒度 | 优化 |
| ThreadSanitizer | TSan CI 检测数据竞争 | ❌ 未集成 | 新增 TSan CI job |
| 死锁检测 | lockdep / ThreadSanitizer | ❌ 无 | 新增 |

### 27.3 错误处理最佳实践

| 实践 | 行业标准（2025-2026） | Airymax 现状 | v3.0 要求 |
|------|----------------------|:----------:|---------|
| 错误码分段 | HTTP 状态码分段思想 | ✅ §4.9 错误码分段表 | 保持 |
| 返回码语义一致 | 0=成功/非 0=错误 | ❌ F4 返回码颠倒 | P3.21 修复 |
| 大声失败 | Fail-fast (Erlang let-it-crash) | ❌ B5 REJECT 静默丢弃 | P3.11 修复 |
| 错误链 | Go errors.Is/As / Rust ? | ✅ §4.8 错误链规范 | 保持 |

### 27.4 日志规范最佳实践

| 实践 | 行业标准（2025-2026） | Airymax 现状 | v3.0 要求 |
|------|----------------------|:----------:|---------|
| 结构化日志 | JSON structured logging | ✅ §4.3 日志系统 | 保持 |
| CLOCK_REALTIME | 日志时间戳用 REALTIME | ✅ project_memory 约束 | 保持 |
| 彩色日志 | ANSI escape codes | ✅ project_memory 约束 | 保持 |
| 日志级别动态 | runtime log level | ✅ AGENTRT_LOG_COLOR | 保持 |
| 关键环节覆盖 | 所有关键操作有日志 | ❅ 部分缺失 | P3.14-P3.18 补充 |

### 27.5 测试最佳实践

| 实践 | 行业标准（2025-2026） | Airymax 现状 | v3.0 要求 |
|------|----------------------|:----------:|---------|
| 单元测试覆盖 | ≥80% line coverage | ⚠️ 未达标 | P3 阶段补充 |
| Fuzz 测试 | OSS-Fuzz / libFuzzer | ✅ H2 REFUTED: 已有 fuzz | 保持 |
| 集成测试 | 端到端冒烟测试 | ❅ 缺失 DT00 | P1.14 新增 |
| 属性测试 | QuickCheck / proptest | ❌ 无 | 新增 |
| 突变测试 | mutation testing | ❌ 无 | 评估引入 |

### 27.6 供应链安全最佳实践

| 实践 | 行业标准（2025-2026） | Airymax 现状 | v3.0 要求 |
|------|----------------------|:----------:|---------|
| SBOM | SPDX / CycloneDX | ✅ P4.5 SBOM 生成 | 保持 |
| 依赖锁定 | lockfile (Cargo.lock / pip freeze) | ⚠️ 部分 | 补全 |
| 签名发布 | Sigstore / cosign | ✅ P4.6 发布签名 | 保持 |
| 镜像扫描 | Trivy / Grype | ❅ 未集成 | 新增 CI job |

### 27.7 可观测性最佳实践

| 实践 | 行业标准（2025-2026） | Airymax 现状 | v3.0 要求 |
|------|----------------------|:----------:|---------|
| Metrics | Prometheus + OpenMetrics | ✅ P1.10 C-L10 | 保持 |
| Tracing | OpenTelemetry distributed tracing | ⚠️ 部分 | 补全 |
| Logging | Loki / ELK | ✅ §4.3 | 保持 |
| 分布式追踪 | OpenTelemetry + Jaeger | ❅ 缺失 | 新增 |
| 思考链追踪 | Agent-specific trace | ✅ thinking_chain | 保持 |

### 27.8 跨平台最佳实践

| 实践 | 行业标准（2025-2026） | Airymax 现状 | v3.0 要求 |
|------|----------------------|:----------:|---------|
| 平台抽象层 | platform.h 兼容层 | ✅ §4.6 CROSS-01~06 | 保持 |
| CI 多平台 | Linux/Windows/macOS CI | ⚠️ 仅 Linux | 补全 |
| 编译器兼容 | GCC/Clang/MSVC | ⚠️ 仅 GCC/Clang | 补全 MSVC |
| 路径处理 | 跨平台路径分隔符 | ✅ hardcode 路径清理 | 保持 |

---

## 第二十八章：v3.0 新增 BAN 规则（BAN-257~BAN-290）

> **来源**: v3.0 穷尽审查发现 + 第二十四至二十七章规范

### 28.1 双思考系统 BAN 规则（BAN-257~BAN-276）

| 编号 | 规则 | 检测方式 | 对应规范 |
|------|------|---------|---------|
| BAN-257 | 禁止 plan_strategy 为 NULL 时进入认知管线 | 启动断言 | DT-01 |
| BAN-258 | 禁止 Phase 2 输出不写入 task_node_output | 代码审查 | DT-03 |
| BAN-259 | 禁止 S2/S1-verify/S1-expert 使用同一模型 | 单元测试 | DT-06 |
| BAN-260 | 禁止 S1 验证 prompt 使用 "verify correctness" | 代码审查 | DT-11 |
| BAN-261 | 禁止 LLM 不可用时使用字数打分回退 | 代码审查 | DT-12 |
| BAN-262 | 禁止 REJECT 静默丢弃 | 集成测试 | DT-13 |
| BAN-263 | 禁止循环检测仅依赖计数器 | 单元测试 | DT-16 |
| BAN-264 | 禁止 weighted/arbiter 返回原文桩逻辑 | 代码审查 | DT-19 |
| BAN-265 | 禁止 `__attribute__((unused))` 死代码 | CI 检查 | DT-20 |
| BAN-266 | 禁止 fallback_plan_strat 为 NULL | 启动断言 | DT-04 |
| BAN-267~276 | 详见双思考系统报告 §6.2 验收标准 | — | DT-05~DT-18 |

### 28.2 内核安全 BAN 规则（BAN-277~BAN-285）

| 编号 | 规则 | 检测方式 | 对应规范 |
|------|------|---------|---------|
| BAN-277 | 禁止 OOM handler 未 init 即使用 | 启动日志验证 | KER-01 |
| BAN-278 | 禁止分配器绕过 OOM 检查 | 代码审查 | KER-03 |
| BAN-279 | 禁止 BUILD_HEAPSTORE 未定义 | CMake 审查 | KER-05 |
| BAN-280 | 禁止结构体跨 TU 不兼容定义 | -Wodr 编译 | KER-08 |
| BAN-281 | 禁止函数签名声明/定义不一致 | -Wstrict-prototypes | KER-09 |
| BAN-282 | 禁止成功码与错误码取相同值 | 单元测试 | KER-10 |
| BAN-283 | 禁止 atoms 内核 #include daemons 层 | CMake 审查 | KER-11 |
| BAN-284 | 禁止函数恒返回 SUCCESS（无视失败） | 单元测试 | KER-14 |
| BAN-285 | 禁止返回码逻辑反转（`if (!ret)`） | 代码审查 | KER-15 |

### 28.3 部署工程 BAN 规则（BAN-286~BAN-290）

| 编号 | 规则 | 检测方式 | 对应规范 |
|------|------|---------|---------|
| BAN-286 | 禁止 Dockerfile COPY 路径与仓库结构不一致 | docker build | DEP-01 |
| BAN-287 | 禁止 CMD 引用不存在的二进制 | CI 检查 | DEP-02 |
| BAN-288 | 禁止 daemon 二进制名不统一（无 agentos- 前缀） | CMake 审查 | DEP-06 |
| BAN-289 | 禁止 EXPOSE 端口与实际监听不一致 | Dockerfile 审查 | DEP-09 |
| BAN-290 | 禁止 healthcheck 端口与实际监听不一致 | 部署验证 | DEP-10 |

---

## 第二十九章：统一打印系统规范（v24.4 新增）

> **背景**: v3.0 二次验证发现项目存在"两头有、中间缺"的打印系统割裂：构建期（CMake `airy_print.cmake`）已实现统一打印（8 函数 + ANSI 彩色 + 时间戳），但运行时（C 层）**无统一打印 API**——`airy_print_ok`/`airy_print_no` 不存在，NO=红色状态打印完全缺失；大量生产代码直接 `fprintf(stderr,...)` 绕过日志系统（heapstore_log.c 自建日志系统、memory.c 泄漏报告、compat.c 诊断输出等）。本章建立运行时统一打印系统的强制规范。

### 29.1 设计原则

| 原则 | 内容 |
|------|------|
| **单一管线** | 所有运行时打印（含状态打印、诊断输出、启动 banner）最终必须委托 `log_write_va()`，禁止再造独立输出管线 |
| **双层统一** | 构建期（CMake `airy_print_*`）与运行时（C `airy_print_*`）API 命名对齐、色彩语义对齐、时间戳源对齐 |
| **状态显式化** | OK=绿色、NO=红色必须通过专用函数（`airy_print_ok`/`airy_print_no`）输出，禁止用 `printf("[OK]")` 拼接 |
| **时间戳权威** | 运行时打印时间戳唯一来源为 `logging.c:get_current_timestamp()`（`CLOCK_REALTIME`），禁止使用 `airy_time_ns()`（`CLOCK_MONOTONIC`） |
| **色彩统一控制** | 运行时色彩由 `AGENTRT_LOG_COLOR=1/0` 控制；构建期由 `AGENTRT_BUILD_COLOR=1/0` 控制；两者自动检测逻辑一致（`isatty` → 终端启用/管道禁用） |

### 29.2 运行时统一打印 API（PRT-01~PRT-08）

**规范 PRT-01**：新增 `agentos/commons/utils/print/include/airy_print.h` 头文件，提供以下 8 个函数式宏，命名与 CMake 层完全对齐：

| 函数 | 级别映射 | 颜色 | 用途 |
|------|---------|------|------|
| `airy_print_ok(fmt, ...)` | INFO | 绿色 `\033[32m` | 成功/确认状态（对应 `[OK]`） |
| `airy_print_no(fmt, ...)` | ERROR | 红色 `\033[31m` | 失败/拒绝状态（对应 `[NO]`，**v3.0 前完全缺失**） |
| `airy_print_info(fmt, ...)` | INFO | 蓝色 `\033[34m` | 信息性输出 |
| `airy_print_warn(fmt, ...)` | WARN | 黄色 `\033[33m` | 警告 |
| `airy_print_error(fmt, ...)` | ERROR | 红色 `\033[31m` | 错误（不终止） |
| `airy_print_fatal(fmt, ...)` | FATAL | 品红 `\033[35m` | 致命错误 |
| `airy_print_debug(fmt, ...)` | DEBUG | 灰色 `\033[90m` | 调试信息 |
| `airy_print_section(fmt, ...)` | INFO | 青色加粗 `\033[1;36m` | 章节标题 |

**规范 PRT-02**：所有 `airy_print_*` 函数底层委托 `log_write_va(level, __FILE__, __LINE__, fmt, args)`，复用核心日志系统的色彩检测（`AGENTRT_LOG_COLOR`）、时间戳（`CLOCK_REALTIME`）、节流（`log_set_throttle`）、采样（`log_should_sample`），禁止独立实现输出管线。

**规范 PRT-03**：统一输出格式为 `[YYYY-MM-DD HH:MM:SS.sss] [LEVEL] [filename.c:line] message`，与 `logging.c:330-335` 格式完全一致。状态打印（OK/NO）在 message 前自动添加 `[OK]`/`[NO]` 标签。

**规范 PRT-04**：`airy_print_ok` 和 `airy_print_no` 必须成对存在，禁止只实现 OK 不实现 NO（v3.0 前的缺陷）。

**规范 PRT-05**：`airy_print.h` 必须在 `agentos/CMakeLists.txt` 中通过 `target_include_directories()` 暴露给所有 daemon 和 atoms 子系统，确保全项目可 `#include <airy_print.h>`。

**规范 PRT-06**：CMake 构建期打印（`airy_print.cmake`）的环境变量从 `AGENTRT_BUILD_COLOR` 保持不变（构建期与运行时分离），但在 `airy_print.h` 文档注释中明确标注两者的关系和使用场景。

**规范 PRT-07**：daemon 启动 banner（如 `gateway_d/main.c` 的帮助文本）属于 CLI 输出而非日志，可保留 `fputs(stdout)` 但必须通过 `airy_print_section` 输出标题行，帮助文本体可豁免（标记 `/* CLI_HELP: exempt from log_write */`）。

**规范 PRT-08**：所有 `airy_print_*` 函数必须线程安全（底层 `log_write_va` 已持锁），禁止在信号处理函数中调用（信号处理中仅允许 `write(STDERR_FILENO, ...)` 原子写入）。

### 29.3 违规打印整改清单（PRT-09~PRT-15）

**规范 PRT-09**：`heapstore/src/heapstore_log.c` 的自建日志系统（`fputs("[heapstore_LOG WARN]...", stderr/stdout)"`）必须整体替换为 `airy_print_warn`/`airy_print_error`/`airy_print_debug`，禁止 heapstore 模块维护独立日志输出管线。

**规范 PRT-10**：`commons/utils/memory/src/memory.c:695-729` 的内存泄漏报告（10 处 `fprintf(stderr,...)`）必须改为 `airy_print_error`，确保泄漏报告包含时间戳和文件行号。

**规范 PRT-11**：`commons/utils/memory/src/memory_debug.c` 的诊断转储（44 处 `fprintf`）改为 `airy_print_debug`，并受 `log_set_module_level("memory_debug", LOG_DEBUG)` 控制。

**规范 PRT-12**：`commons/utils/compat/src/compat.c` 和 `compat2.c` 的 stderr 诊断输出（10 处 `fputs`）改为 `airy_print_warn`/`airy_print_error`。

**规范 PRT-13**：`logging_compat.c:168` 的调试输出（`fprintf(stderr,"[LOGGING_COMPAT] API call: %s\n")`）改为 `airy_print_debug`，受模块级别控制。

**规范 PRT-14**：合法文件 I/O（如 `checkpoint.c` 写 JSON 文件、`heapstore_core.c` 写数据文件、`audit_overflow.c` 写审计文件）不属违规，但必须使用 `FILE*` 参数化写入，禁止硬编码 `stderr`/`stdout`。

**规范 PRT-15**：CI 中 `quality-gate.sh` 新增 `[PRINT-SCAN]` 步骤，扫描生产代码（排除 tests/examples/bench/日志系统内部）中的 `fprintf(stderr`/`fprintf(stdout`/`fputs(.*stderr`/`fputs(.*stdout` 调用，违规即 CI 失败。豁免清单：`logging.c`（`__builtin_fprintf`）、`logging_compat.c`（迁移报告文件 I/O）、`service_logging.c`、`memory.c`/`memory_debug.c`（BAN-70 EXEMPT 诊断转储，待 PRT-10/11 修复后移除豁免）。

### 29.4 v3.2 新增：遗留模块迁移规范（PRT-16~PRT-18）

> **背景**: v3.2 二次验证统计统一打印率 98.2%（~3150 统一调用 vs ~58 裸调用），但仍有 3 个模块存在大量裸调用需迁移。

**规范 PRT-16**：`protocols/` 模块（MCP/A2A/OpenJiuWen 等协议适配器）约 80 处裸 `printf`/`fprintf` 必须替换为 `AIRY_LOG_*` 宏。协议适配器的调试输出应使用 `LOG_DEBUG`，连接错误使用 `LOG_ERROR`，协议协商使用 `LOG_INFO`。迁移时需在每个协议文件头部添加 `#include <logging_compat.h>`。

**规范 PRT-17**：`atoms/memory/` 模块的裸调用（当前仅 2 处 `AIRY_LOG` + 若干裸调用）必须统一为 `AIRY_LOG_*` 宏。`builtin_provider.c` 等内存提供者实现的调试输出使用 `LOG_DEBUG`，内存分配失败使用 `LOG_ERROR`。

**规范 PRT-18**：`heapstore/src/heapstore_migration.c` 的 5 处裸 `fprintf` 必须替换为 `airy_print_info`/`warn`/`error`。数据库迁移是关键操作，迁移进度必须通过 `airy_print_info` 输出（含时间戳+信息头），迁移失败必须通过 `airy_print_error` 输出。

---

## 第三十章：统一日志系统规范（v24.4 新增）

> **背景**: v3.0 二次验证确认核心日志系统（`log_write`/`log_write_va`）已完整实现，8 个协议文件 `error.h` 本地 `#define` 已迁移至 `logging_compat.h`，时间戳正确使用 `CLOCK_REALTIME`，`AGENTRT_LOG_COLOR` 已实现。但存在以下待加固项：`svc_logger.h` 未包含 `logging_compat.h`（改为直接 `logging.h`）、13 个协议文件含 `error.h` 但无日志宏、关键系统操作环节日志覆盖不足。本章建立统一日志系统的完整规范。

### 30.1 核心 API 规范（LOG-01~LOG-05）

**规范 LOG-01**：所有日志输出必须通过核心日志系统 API（`log_write()`/`log_write_va()`/`LOG_*` 宏/`AIRY_LOG_*` 宏/`SVC_LOG_*` 宏），禁止直接 `fprintf`/`printf`/`fputs`/`puts` 用于日志输出。合法文件 I/O 除外（见 PRT-14）。

**规范 LOG-02**：日志级别枚举严格为 5 级（DEBUG=0, INFO=1, WARN=2, ERROR=3, FATAL=4），禁止新增级别。颜色映射固定：DEBUG=灰(`\033[90m`)、INFO=蓝(`\033[34m`)、WARN=黄(`\033[33m`)、ERROR=红(`\033[31m`)、FATAL=品红(`\033[35m`)。

**规范 LOG-03**：日志格式严格为 `[YYYY-MM-DD HH:MM:SS.sss] [LEVEL] [filename.c:line] message`，LEVEL 部分用对应颜色 ANSI 码包裹（含 RESET）。文件输出（`log_file_write`）始终不带 ANSI 色彩。

**规范 LOG-04**：时间戳唯一来源为 `logging.c:get_current_timestamp()`（`clock_gettime(CLOCK_REALTIME, &ts)`），禁止使用 `airy_time_ns()`（`CLOCK_MONOTONIC`）或 `time()`/`localtime()` 作为日志时间戳。`airy_time_ns()` 仅用于子系统计时（超时、调度、性能测量）。

**规范 LOG-05**：色彩控制通过 `AGENTRT_LOG_COLOR` 环境变量：识别 `0/no/false/off/never` 关闭，其余值启用；未设置时通过 `isatty(STDOUT_FILENO) || isatty(STDERR_FILENO)` 自动检测（终端启用、管道/文件禁用）。禁止其他模块独立实现色彩检测逻辑。

### 30.2 兼容层规范（LOG-06~LOG-10）

**规范 LOG-06**：`logging_compat.h` 是 `AIRY_LOG_*` 宏的唯一定义源，通过 `#ifndef AIRY_LOG_ERROR` 保护避免冲突。所有使用 `AIRY_LOG_ERROR/WARN/INFO/DEBUG/FATAL` 的代码必须 `#include <logging_compat.h>` 或 `#include <error.h>`（corekern 版本已包含 logging_compat.h）。

**规范 LOG-07**：`svc_logger.h` 必须在文件顶部 `#include <logging_compat.h>`，确保仅包含 `svc_logger.h` 的代码也能使用 `AIRY_LOG_*` 宏。当前 `svc_logger.h` 仅包含 `logging.h` 提供的 `LOG_*`/`SVC_LOG_*` 宏，需补充 `logging_compat.h` 以提供 `AIRY_LOG_*` 宏。

**规范 LOG-08**：8 个协议文件（`openjiuwen_adapter.c`、`airy_protocol_interface.c`、`mcp_transport.c`、`mcp_v1_adapter.c`、`a2a_v03_adapter.c`、`test_agntcy_acp.c`、`test_openclaw_adapter.c`、`test_china_eco_crypto.c`）已包含 `logging_compat.h`，此为合规范例。其余 13 个协议文件（`claude_adapter.c`、`china_eco_adapter.c`、`openai_enterprise_adapter.c` 等）若需日志输出，必须补充 `#include <logging_compat.h>`。

**规范 LOG-09**：`error.h` 三层定义关系固定：
- `commons/utils/error/include/error.h`（权威源，定义 `AIRY_ERR_*` 扩展错误码（`AIRY_OK`/`AIRY_EOK`/`AIRY_SUCCESS` 成功码定义于 `airy_types.h`））
- `atoms/corekern/include/error.h`（`#include` 权威 error.h + `logging_compat.h`，内核层统一日志入口）
- `daemons/common/include/error.h`（`#include` 权威 error.h，daemons 层兼容别名 `AIRY_ERROR_*` → `AIRY_ERR_*`）
禁止在其他位置新增 `error.h` 或本地 `#define AIRY_ERR_*`/`#define AIRY_LOG_*`。

**规范 LOG-10**：`logging_compat.c` 中的 19 处 `fprintf` 用于迁移报告文件 I/O（写 JSON 文件），属合法文件 I/O（见 PRT-14），但 `:168` 的调试输出 `fprintf(stderr,"[LOGGING_COMPAT] API call: %s\n")` 必须改为 `airy_print_debug`（见 PRT-13）。

### 30.3 关键环节增强日志覆盖（LOG-11~LOG-18）

**规范 LOG-11**：daemon 启停环节必须记录以下日志：
- 启动：`LOG_INFO("daemon %s starting, pid=%d, config=%s", daemon_name, getpid(), config_path)`
- 启动完成：`airy_print_ok("daemon %s started, listening on %s:%d", daemon_name, host, port)`
- 启动失败：`airy_print_fatal("daemon %s startup failed: %s (code=%d)", daemon_name, error_msg, err)`
- 停止：`LOG_INFO("daemon %s stopping, pid=%d", daemon_name, getpid())`
- 停止完成：`LOG_INFO("daemon %s stopped", daemon_name)`

**规范 LOG-12**：IPC 握手环节必须记录：
- 连接建立：`LOG_DEBUG("ipc connection accepted: %s -> %s", src, dst)`
- 握手成功：`airy_print_ok("ipc handshake ok: %s <-> %s", src, dst)`
- 握手失败：`airy_print_no("ipc handshake failed: %s -> %s, reason=%s", src, dst, reason)`
- 连接断开：`LOG_WARN("ipc connection closed: %s -> %s", src, dst)`

**规范 LOG-13**：LLM 调用环节必须记录：
- 请求发起：`LOG_INFO("llm request: model=%s, provider=%s, tokens_in=%zu", model, provider, input_tokens)`
- 响应成功：`LOG_INFO("llm response: model=%s, tokens_out=%zu, latency=%zums", model, output_tokens, latency_ms)`
- 响应失败：`airy_print_no("llm error: model=%s, provider=%s, code=%d, msg=%s", model, provider, err, msg)`
- 降级触发：`LOG_WARN("llm fallback: %s -> %s, reason=%s", primary_model, fallback_model, reason)`

**规范 LOG-14**：checkpoint 读写环节必须记录：
- 保存：`LOG_DEBUG("checkpoint save: task=%s, step=%d, size=%zu bytes", task_id, step, size)`
- 恢复：`LOG_INFO("checkpoint restore: task=%s, step=%d", task_id, step)`
- 保存失败：`airy_print_no("checkpoint save failed: task=%s, code=%d", task_id, err)`

**规范 LOG-15**：cupolas 审计环节必须记录：
- 审批通过：`airy_print_ok("cupolas allow: agent=%s, tool=%s, guard=%s", agent, tool, guard_type)`
- 审批拒绝：`airy_print_no("cupolas deny: agent=%s, tool=%s, guard=%s, reason=%s", agent, tool, guard_type, reason)`
- 审计溢出：`LOG_WARN("cupolas audit overflow: %zu events dropped", dropped_count)`

**规范 LOG-16**：OOM 压力环节必须记录：
- 水位线升级：`LOG_WARN("oom watermark: %s -> %s, usage=%.1f%%", prev_level, new_level, usage_pct)`
- 降级触发：`LOG_ERROR("oom degraded: level=%s, action=%s", level, action)`
- 致命水位：`airy_print_fatal("oom fatal: usage=%.1f%%, initiating emergency shutdown", usage_pct)`

**规范 LOG-17**：heapstore 持久化环节必须记录：
- 写入成功：`LOG_DEBUG("heapstore write: key=%s, size=%zu, durable=%s", key, size, durable ? "yes" : "no")`
- 写入失败：`airy_print_no("heapstore write failed: key=%s, code=%d", key, err)`
- fsync 完成：`LOG_DEBUG("heapstore fsync: %zu bytes flushed", bytes)`

**规范 LOG-18**：双思考系统环节必须记录：
- Phase 2 启动：`LOG_INFO("thinkdual phase2 start: task=%s, model=%s", task_id, model)`
- Phase 2 结果：`airy_print_ok("thinkdual phase2 done: task=%s, score=%.2f, verdict=%s", task_id, score, verdict)`
- Phase 2 拒绝：`airy_print_no("thinkdual phase2 reject: task=%s, reason=%s", task_id, reason)`
- 循环检测：`LOG_WARN("thinkdual loop detected: task=%s, count=%d, action=%s", task_id, loop_count, action)`

### 30.4 日志配置与运维规范（LOG-19~LOG-20）

**规范 LOG-19**：`agentrt.yaml` 的 `logging` 配置段必须支持以下字段：
```yaml
logging:
  level: "INFO"                    # 全局默认级别
  color: "auto"                    # auto/on/off（对应 AGENTRT_LOG_COLOR 未设置/1/0）
  module_levels:                   # 模块级覆盖（支持通配符）
    "memory_debug": "WARN"
    "ipc.*": "DEBUG"
  throttle:
    enabled: true
    max_per_sec: 100
  sampling:
    ERROR: 1.0    # 100%
    WARN: 0.1     # 10%
    INFO: 0.01    # 1%
    DEBUG: 0.001  # 0.1%
  file:
    enabled: false
    path: "/var/log/agentos/agentos.log"
    max_size_mb: 100
    max_files: 10
    flush_interval_sec: 5
  trace_id: "${AIRY_TRACE_ID}"  # 分布式追踪 ID 注入
```

**规范 LOG-20**：`log_reload_config(path)` 必须支持运行时热重载（SIGHUP 触发或 `agentrt config reload` 命令），重载后立即生效新级别/色彩/节流/采样配置，无需重启 daemon。热重载必须记录 `LOG_INFO("logging config reloaded: %s", path)`。

### 30.5 v3.2 新增：日志系统加固规范（LOG-21~LOG-25）

> **背景**: v3.2 二次验证发现日志系统完整度仅 62%，主要缺失在异步路径断开、JSON 格式化未实现、syslog 后端未实现、时间轮转未实现、监控数据未采集。

**规范 LOG-21**：异步写入路径必须连通。当前 `atomic_logging.c` 的环形队列+异步刷盘线程已实现，但 `logging.c` 的 `log_write()` 未提交到 `atomic_logging_submit()`，导致 `log_config_t.async_mode` 字段无实际作用。修复后 `log_write()` 在 `async_mode=true` 时应将日志记录提交到环形队列，由后台线程刷盘；`async_mode=false` 时保持同步写入。

**规范 LOG-22**：JSON 格式化必须实现。`logging.h` 中 `LOG_FORMAT_JSON` 已在 `log_config_t.format` 枚举中定义，但 `format_log_message()` 仅实现了 `LOG_FORMAT_TEXT`。JSON 格式必须输出 `{"timestamp":"...","level":"...","module":"...","line":...,"message":"...","trace_id":"...","span_id":"..."}` 结构，用于日志聚合系统（ELK/Loki）消费。

**规范 LOG-23**：syslog 输出后端必须实现。`LOG_OUTPUT_SYSLOG` 枚举已定义但无实现代码。实现需调用 `openlog()`/`syslog()`/`closelog()`，支持 `log_config_t.syslog_facility` 配置，映射 LOG_DEBUG→LOG_DEBUG, LOG_INFO→LOG_INFO, LOG_WARN→LOG_WARNING, LOG_ERROR→LOG_ERR, LOG_FATAL→LOG_CRIT。

**规范 LOG-24**：基于时间的日志轮转必须实现。服务层定义了 `ROTATION_STRATEGY_TIME`/`ROTATION_STRATEGY_BOTH` 及 `rotation_interval_t`，但无实现。时间轮转应支持按小时/天/周切换日志文件，配合大小轮转（已有）实现双重保护。

**规范 LOG-25**：监控数据采集必须实现。`log_monitoring_stats_t` 结构完整但无实际采集逻辑。必须采集：总写入数/级别分布/节流丢弃数/采样跳过数/各输出后端延迟/队列深度（异步模式），并通过 `log_get_monitoring_stats()` API 暴露。

### 30.6 v3.4 新增：全功能统一打印/日志系统定义（LOG-26）

**规范 LOG-26**：v0.1.1 必须实现"全功能"统一打印/日志系统，定义如下七项必备能力（用户关键决策 4 明确要求）：

| 能力 | 定义 | 验收标准 |
|------|------|---------|
| **1. 流式日志（Streaming）** | 支持日志流式输出（`log_stream_open/write/flush/close`），适配 SSE/WebSocket 实时推送场景 | `log_stream_write()` 可边产生边消费，无需等待缓冲区满 |
| **2. 结构化字段（Structured Fields）** | 日志支持结构化键值对字段（`log_write_kv(level, file, line, fmt, kv_pairs[], n)`），可输出 JSON Lines 格式 | `log_write_kv(LOG_INFO, __FILE__, __LINE__, "cognition", kv, 2)` 输出 `{"ts":"...","level":"INFO","msg":"cognition","task_id":"t123","phase":2}` |
| **3. 采样与节流（Sampling/Throttle）** | 高频日志支持采样率配置（`log_set_sample_rate(category, rate)`）和节流（`log_set_throttle(category, max_per_sec)`），防止日志风暴 | DEBUG 级别采样率 0.1 时，1000 次/秒调用仅输出 100 次；节流 100/s 时超限丢弃并计数 |
| **4. 29 事件全覆盖** | 关键环节 29 个事件全部必须有增强日志（启动/初始化/连接/断开/错误/恢复/调度/认知阶段/双思考/记忆读写/工具执行/安全检查/审计） | `grep -rn 'log_write\|LOG_\|AIRY_LOG_' agentrt/agentrt/ | grep -E "29 事件清单" ` 全覆盖 |
| **5. 日志分级动态调整** | 运行时可通过 API（`log_set_level(category, level)`）和配置（`log.level.cognition=DEBUG`）动态调整日志级别，无需重启 | `agentrt log level cognition DEBUG` → 后续 cognition 日志输出 DEBUG 级别 |
| **6. 异步落盘（Async Flush）** | 日志写入异步队列，独立线程落盘，不阻塞业务线程；队列满时按策略丢弃（最低级别优先丢）或阻塞 | 业务线程日志调用 < 1μs，落盘线程独立；队列满时丢弃 DEBUG/WARN，保留 ERROR/FATAL |
| **7. trace_id 跨进程贯穿** | trace_id 通过 IPC 消息头（`airy_ipc_msg_hdr.trace_id`）跨进程传递，所有日志输出包含 trace_id 字段 | 跨 3 个 daemon 的请求 → 三份日志 trace_id 一致 |

**29 事件清单（关键环节增强日志，必须全覆盖）**：

| 类别 | 事件 | 日志级别 | 触发点 |
|------|------|---------|--------|
| 启动 | atoms_init_start/complete | INFO/FATAL | `airy_core_init()` 入口/出口 |
| 启动 | daemon_init_start/complete | INFO/FATAL | 各 daemon `main()` 入口/出口 |
| 启动 | ops_injected | INFO | daemon ops 注入 atoms 时 |
| 连接 | ipc_connect/disconnect | INFO/WARN | IPC Bus 连接建立/断开 |
| 连接 | service_register/discover | INFO | 服务注册/发现 |
| 调度 | task_schedule/complete | DEBUG/INFO | 任务调度/完成 |
| 认知 | phase0_decompose/phase1_plan/phase2_execute/phase3_audit/phase4_replan | INFO | CoreLoopThree 五阶段 |
| 双思考 | s2_generate/s1_verify/s1_expert/major_fix_triggered | INFO/WARN | 双思考系统 |
| 记忆 | mem_l1_write/l2_retrieve/l3_bind/l4_pattern | DEBUG | MemoryRovol 四层 |
| 工具 | tool_execute_start/complete/fail | INFO/ERROR | 工具执行 |
| 安全 | permission_check/quarantine | WARN/ERROR | Cupolas |
| 审计 | audit_log_write | INFO | 审计日志 |
| 错误 | error_recover/fatal | WARN/FATAL | 错误恢复/致命错误 |
| 恢复 | service_recover/health_restore | INFO | 服务恢复 |

**强制要求**：
- 七项能力必须全部实现，缺一不可（用户明确要求"全功能"）
- 29 事件清单必须全覆盖，CI 检查 `[LOG-EVENT-SCAN]` 验证每个事件有对应日志点
- 关键环节（启动/认知/双思考/安全/错误）日志必须增强（含上下文字段 + trace_id）
- 异步落盘必须保证 ERROR/FATAL 不丢弃（仅丢弃 DEBUG/WARN）

**验收标准**：ACC-LOG26（七项能力全部实现 + 29 事件全覆盖 + 异步落盘 ERROR/FATAL 不丢弃）。

---

## 第三十一章：统一打印/日志 BAN 规则（BAN-291~BAN-310，v24.4 新增）

> **来源**: v3.0 二次验证 + 第二十九/三十章规范

### 31.1 违规打印 BAN 规则（BAN-291~BAN-300）

| 编号 | 规则 | 检测方式 | 对应规范 |
|------|------|---------|---------|
| BAN-291 | 禁止生产代码中 `fprintf(stderr,...)`/`fprintf(stdout,...)` 用于日志输出 | `[PRINT-SCAN]` CI 步骤 | PRT-15 |
| BAN-292 | 禁止 `fputs(msg, stderr)`/`fputs(msg, stdout)` 用于日志输出 | `[PRINT-SCAN]` CI 步骤 | PRT-15 |
| BAN-293 | 禁止 `puts()`/`printf()` 用于日志输出 | `[PRINT-SCAN]` CI 步骤 | PRT-15 |
| BAN-294 | 禁止 heapstore 模块维护独立日志输出管线（`heapstore_log.c` 自建系统） | 代码审查 | PRT-09 |
| BAN-295 | 禁止用 `printf("[OK]")`/`printf("[NO]")` 拼接状态打印 | `[PRINT-SCAN]` 检测 `[OK]`/`[NO]` 字面量 | PRT-01 |
| BAN-296 | 禁止 `airy_print_no` 未实现（必须与 `airy_print_ok` 成对存在） | 编译检查头文件 | PRT-04 |
| BAN-297 | 禁止在信号处理函数中调用 `airy_print_*`/`log_write` | 代码审查 | PRT-08 |
| BAN-298 | 禁止 daemon banner 不使用 `airy_print_section` 输出标题行 | 代码审查 | PRT-07 |
| BAN-299 | 禁止 `memory.c`/`memory_debug.c` 泄漏报告使用 `fprintf` | `[PRINT-SCAN]` | PRT-10/11 |
| BAN-300 | 禁止 `compat.c`/`compat2.c` 诊断输出使用 `fputs(stderr)` | `[PRINT-SCAN]` | PRT-12 |

### 31.2 日志系统 BAN 规则（BAN-301~BAN-310）

| 编号 | 规则 | 检测方式 | 对应规范 |
|------|------|---------|---------|
| BAN-301 | 禁止使用 `airy_time_ns()`（CLOCK_MONOTONIC）作为日志时间戳 | 代码审查 | LOG-04 |
| BAN-302 | 禁止使用 `time()`/`localtime()` 作为日志时间戳 | 代码审查 | LOG-04 |
| BAN-303 | 禁止在 `error.h` 之外的位置新增 `#define AIRY_ERR_*` | `check_error_codes.sh` | LOG-09 |
| BAN-304 | 禁止本地 `#define AIRY_LOG_ERROR`/`AIRY_LOG_WARN` 等日志宏 | `ban_scan.sh` | LOG-06 |
| BAN-305 | 禁止 `svc_logger.h` 不包含 `logging_compat.h` | 头文件审查 | LOG-07 |
| BAN-306 | 禁止新增日志级别（超出 DEBUG/INFO/WARN/ERROR/FATAL 5 级） | 枚举审查 | LOG-02 |
| BAN-307 | 禁止其他模块独立实现色彩检测逻辑（必须复用 `AGENTRT_LOG_COLOR`） | 代码审查 | LOG-05 |
| BAN-308 | 禁止 daemon 启停无日志覆盖（启动/完成/失败/停止 5 事件） | 集成测试 | LOG-11 |
| BAN-309 | 禁止 LLM 调用无日志覆盖（请求/响应/失败/降级 4 事件） | 集成测试 | LOG-13 |
| BAN-310 | 禁止 cupolas 审批无日志覆盖（允许/拒绝/溢出 3 事件） | 集成测试 | LOG-15 |

---

## 第三十二章：开源许可证规范（v24.6 新增 / v25.0 双许可证修正）

> **来源**: v3.3 综合审计 → v3.5 用户最终决定全项目许可证统一为 AGPL v3 + Apache 2.0 双许可证
> **版权归属人**: SPHARX Ltd.
> **战略定位**: 成为"行业底座"需要兼顾"防云厂商白嫖"与"零门槛采纳"。AGPL-3.0-or-later OR Apache-2.0 双许可证统一覆盖运行时核心 + 工具链/SDK + 文档（接收方可任选其一遵循：AGPL 路径防云厂商闭源分发；Apache 路径零门槛采纳）。MemoryRovol 作为独立闭源仓库不在此双许可证体系内，由其自有商业 EULA 治理。
> **v3.5 修正**: 取消 v3.3 提出的"三许可证体系（AGPL v3 + Apache 2.0 + SPHARX-Proprietary）+ CC-BY-SA-4.0"路径，禁止 SPHARX-Proprietary 与 CC-BY-SA-4.0 作为项目内许可证。

### 32.1 双许可证体系总览（LC-01）

| 许可证 | 适用范围 | SPDX 标识符 | 文件位置 |
|--------|---------|------------|---------|
| AGPL-3.0-or-later OR Apache-2.0 | 全项目源代码、构建脚本、SDK、文档（含 atoms/cupolas/daemons/gateway/heapstore/protocols/commons/sdk/ecosystem/scripts/deploy/tests） | `AGPL-3.0-or-later OR Apache-2.0` | `OpenAirymax/LICENSE`（双许可证全文） |
| MemoryRovol 独立 EULA | 仅 MemoryRovol 独立闭源仓库（不在 OpenAirymax 主仓库内） | 由 MemoryRovol 仓库自行声明 | MemoryRovol 仓库内 LICENSE 文件 |

**强制规则 LC-01**: OpenAirymax 主仓库内所有源代码、构建脚本、文档统一使用 `AGPL-3.0-or-later OR Apache-2.0` 双许可证，禁止引入第三种许可证（MIT/BSD/GPL/CC-BY-SA-4.0/SPHARX-Proprietary 等不得新增）。MemoryRovol 作为独立闭源仓库不在本规则约束范围内。

### 32.2 SPDX 标识符强制规范（LC-02）

**强制规则 LC-02**: 所有 `.c`/`.h`/`.go`/`.rs`/`.py`/`.ts`/`.js`/`.sh`/`.ps1`/`.json`/`.toml`/`.yaml`/`.clangd`/`CMakeLists.txt` 文件头部必须包含 SPDX 标识符，格式统一如下：

```c
// SPDX-FileCopyrightText: 2025-2026 SPHARX Ltd.
// SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0
```

或（脚本类文件 `#` 注释）：

```bash
# SPDX-FileCopyrightText: 2025-2026 SPHARX Ltd.
# SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0
```

或（块注释 `/* */`）：

```c
/* SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0 */
```

**禁止行为**：
- 禁止使用单一 `Apache-2.0` 或单一 `AGPL-3.0-or-later` 作为 SPDX 标识符（必须为双许可证）
- 禁止使用 `All Rights Reserved` 作为唯一许可证声明（必须配合 SPDX 标识符）
- 禁止在源码头部放置完整许可证文本（SPDX 标识符已足够，完整文本位于 `LICENSE` 文件）
- 禁止省略 `SPDX-FileCopyrightText` 字段
- 禁止使用 `SPHARX-Proprietary` / `Proprietary` / `CC-BY-SA-4.0` 作为 OpenAirymax 主仓库内文件的 SPDX 标识符

### 32.3 子目录许可证路由（LC-03）

**强制规则 LC-03**: OpenAirymax 主仓库内所有子目录统一使用双许可证（不再区分运行时核心与工具链）：

| 子目录 | 许可证 | 理由 |
|--------|--------|------|
| `agentrt/agentrt/atoms/` | AGPL-3.0-or-later OR Apache-2.0 | 双许可证统一 |
| `agentrt/agentrt/cupolas/` | AGPL-3.0-or-later OR Apache-2.0 | 双许可证统一 |
| `agentrt/agentrt/daemons/` | AGPL-3.0-or-later OR Apache-2.0 | 双许可证统一 |
| `agentrt/agentrt/gateway/` | AGPL-3.0-or-later OR Apache-2.0 | 双许可证统一 |
| `agentrt/agentrt/heapstore/` | AGPL-3.0-or-later OR Apache-2.0 | 双许可证统一 |
| `agentrt/agentrt/protocols/` | AGPL-3.0-or-later OR Apache-2.0 | 双许可证统一 |
| `agentrt/agentrt/commons/` | AGPL-3.0-or-later OR Apache-2.0 | 双许可证统一 |
| `agentrt/sdk/rust/`、`sdk/python/`、`sdk/go/`、`sdk/typescript/` | AGPL-3.0-or-later OR Apache-2.0 | 双许可证统一 |
| `agentrt/ecosystem/` | AGPL-3.0-or-later OR Apache-2.0 | 双许可证统一 |
| `agentrt/scripts/`、`deploy/`、`tests/` | AGPL-3.0-or-later OR Apache-2.0 | 双许可证统一 |
| `Desktop/` | AGPL-3.0-or-later OR Apache-2.0 | 双许可证统一 |
| `Docker/` | AGPL-3.0-or-later OR Apache-2.0 | 双许可证统一 |
| `Docs/` | AGPL-3.0-or-later OR Apache-2.0 | 双许可证统一 |
| `MemoryRovol/` | 独立闭源 EULA | 独立仓库，不在 OpenAirymax 主仓库内 |

**禁止行为**：
- 禁止 OpenAirymax 主仓库内任何子目录使用单一 `Apache-2.0` 或单一 `AGPL-3.0-or-later` SPDX 标识符
- 禁止 OpenAirymax 主仓库内任何子目录使用 `SPHARX-Proprietary` / `Proprietary` / `CC-BY-SA-4.0` / `MIT` / `BSD-3-Clause` 等其他许可证
- 禁止 `MemoryRovol/`（独立闭源仓库）使用 AGPL 或 Apache 许可证

### 32.4 许可证矛盾消除规范（LC-04）

**强制规则 LC-04**: 禁止出现"LICENSE 文件 + 源码头部 + CMake 字段 + package.json/Cargo.toml"四重许可证矛盾。

**已知矛盾（v3.3 发现，已修复）**：
- ~~`MemoryRovol/LICENSE` = Apache 2.0 全文~~ → 已修正：MemoryRovol 作为独立闭源仓库已迁出 OpenAirymax 主仓库
- ~~`MemoryRovol/src/memoryrovol.c:4` = `All Rights Reserved`~~ → 已修正
- ~~`MemoryRovol/CMakeLists.txt:224` = `set(CPACK_RPM_PACKAGE_LICENSE "Proprietary")`~~ → 已修正

**修复方式（v3.5 实施）**：
- OpenAirymax 内 5 个 `LICENSE` 文件（`agentrt/`、`Desktop/`、`Docker/`、`Docs/`、`MemoryRovol/`）统一为双许可证全文（AGPL v3 + Apache 2.0）
- 3 个 `NOTICE` 文件（`agentrt/`、`Desktop/`、`Docker/`）统一声明版权人 SPHARX Ltd.
- 所有源码头部统一为 `SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0`
- 所有 CMake 字段统一为 `set(CPACK_RPM_PACKAGE_LICENSE "AGPL-3.0-or-later OR Apache-2.0")`
- 所有 Cargo.toml 字段统一为 `license = "AGPL-3.0-or-later OR Apache-2.0"`

### 32.5 非源码文件许可证字段（LC-05）

**强制规则 LC-05**: 所有非源码文件必须声明许可证字段：

| 文件类型 | 字段 | 示例 |
|---------|------|------|
| `Cargo.toml` | `license = "..."` | `license = "AGPL-3.0-or-later OR Apache-2.0"` |
| `package.json` | `"license": "..."` | `"license": "AGPL-3.0-or-later OR Apache-2.0"` |
| `go.mod` | 头部 SPDX 注释 | `// SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0` |
| `setup.py`/`pyproject.toml` | `license = "..."` | `license = "AGPL-3.0-or-later OR Apache-2.0"` |
| `CMakeLists.txt` | 顶部 SPDX 注释 | `# SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0` |
| `vcpkg.json` | `"license": "..."` | `"license": "AGPL-3.0-or-later OR Apache-2.0"` |

**禁止行为**：
- 禁止 `Cargo.toml`/`package.json`/`vcpkg.json` 缺少 `license` 字段
- 禁止许可证字段为空字符串或 `UNLICENSED`（除非明确为内部工具）
- 禁止使用单一许可证字段（必须为双许可证 `AGPL-3.0-or-later OR Apache-2.0`）

### 32.6 CI 许可证合规扫描（LC-06）

**强制规则 LC-06**: CI 流水线必须集成许可证合规扫描，作为 Gate 0（编译前阻断）。

**扫描脚本**: `scripts/ci/license-check.sh`
**扫描工具**: `licensecheck` 或 `reuse`（FSFE 推荐）
**扫描规则**:
1. 所有 `.c`/`.h`/`.go`/`.rs`/`.py`/`.ts`/`.js`/`.sh`/`.ps1`/`.json`/`.toml`/`.yaml`/`.clangd`/`CMakeLists.txt` 必须有 SPDX 标识符
2. OpenAirymax 主仓库内所有源码必须是 `AGPL-3.0-or-later OR Apache-2.0`（双许可证）
3. 5 个 `LICENSE` 文件（`agentrt/`、`Desktop/`、`Docker/`、`Docs/`、`MemoryRovol/`）必须为双许可证全文
4. 3 个 `NOTICE` 文件（`agentrt/`、`Desktop/`、`Docker/`）必须声明版权人 SPHARX Ltd.

**违规处理**：
- 缺少 SPDX 标识符 → REJECT
- SPDX 标识符为单一许可证（非双许可证）→ REJECT
- 许可证类型不匹配路由表 → REJECT
- 许可证矛盾（LICENSE 文件 vs 源码头部 vs CMake 字段 vs package.json）→ REJECT

### 32.7 贡献者许可协议 CLA（LC-07）

**强制规则 LC-07**: 所有外部贡献者必须签署贡献者许可协议（CLA）。

**CLA 内容**：
- 贡献者授予 SPHARX Ltd. 在 AGPL-3.0-or-later OR Apache-2.0 双许可证下使用贡献代码的权利
- 贡献者保证拥有贡献代码的版权或已获得授权
- 贡献者保证贡献代码不侵犯第三方知识产权
- 贡献者同意贡献代码将统一以 `AGPL-3.0-or-later OR Apache-2.0` 双许可证发布

**CLA 文件位置**: `OpenAirymax/CONTRIBUTING.md` 中的 CLA 章节
**签署方式**: 首次 PR 时在 CONTRIBUTING.md 末尾添加签署信息

### 32.8 MemoryRovol 独立闭源仓库隔离规范（LC-08）

**强制规则 LC-08**: MemoryRovol 作为独立闭源仓库（独立 git submodule），不纳入 OpenAirymax 主仓库的双许可证体系，由其自有商业 EULA 治理。

**隔离措施**：
1. MemoryRovol 不与 AgentRT 主仓库共享 Git 历史（独立 git submodule）
2. MemoryRovol 的构建产物不包含 AGPL v3 代码
3. MemoryRovol 与 AgentRT 的接口必须通过运行时 ABI（动态链接）而非编译期头文件包含
4. MemoryRovol 的 LICENSE 文件由其独立仓库自行维护（独立商业 EULA）
5. MemoryRovol 的源码头部 SPDX 标识符由其独立仓库自行决定
6. CI 扫描时 MemoryRovol 必须作为独立检查单元（与 OpenAirymax 主仓库隔离）

**OpenAirymax 主仓库内对 MemoryRovol 的引用**：
- `OpenAirymax/MemoryRovol/` 目录仅作为 git submodule 挂载点，不视为 OpenAirymax 主仓库的一部分
- OpenAirymax 主仓库内的 `LICENSE` 文件不约束 MemoryRovol 独立仓库
- OpenAirymax 主仓库内的 SPDX 扫描应排除 `MemoryRovol/` 目录

**合规验证**：
- `grep -rn "AGPL-3.0-or-later OR Apache-2.0" OpenAirymax/ --include="*.c" --include="*.h" --include="*.go" --include="*.rs" --include="*.py" --include="*.ts" --include="*.js" --include="*.sh" | grep -v "/.git/" | grep -v "MemoryRovol/"` → 应覆盖所有 OpenAirymax 主仓库源码
- `grep -rn "SPHARX-Proprietary\|Proprietary\|CC-BY-SA-4.0" OpenAirymax/ --include="*.c" --include="*.h" --include="*.go" --include="*.rs" --include="*.py" --include="*.ts" --include="*.js" --include="*.sh" | grep -v "/.git/" | grep -v "MemoryRovol/"` → 0（OpenAirymax 主仓库内不得出现 SPHARX-Proprietary / Proprietary / CC-BY-SA-4.0）

---

## 第三十三章：微内核架构规范（v24.7 方案 A 修正）

> **来源**: v3.3 综合审计 + v3.4 用户关键决策 7 — atoms 内的模块不能随意物理移动
> **核心原则**: atoms 层必须满足"无反向依赖、可独立编译、仅暴露接口"三大特征。**采用方案 A（接口反转）**：atoms 文件物理位置不变，通过 ops 抽象表 + daemons init 时注入消除反向依赖。
> **方案选择依据**: 用户明确约束"atoms 内的模块不能随意移动"；taskflow 是通用 Pregel/DAG 核心原语不应移动；coreloopthree 虽语义上是应用层但已深度集成（43.9K LOC），物理迁移工程代价过高。

### 33.1 atoms 层语义边界定义（ARC-01，方案 A 修正）

**强制规则 ARC-01**: atoms 层包含三类模块，物理位置不变，通过语义边界文档 + ops 接口隔离定义边界：

| 类别 | 子模块 | 语义角色 | LOC |
|------|--------|---------|-----|
| **真正微核心原语**（不可移动） | `corekern/` | IPC/Task/Sync/Mem/Timer/Interrupt | ~12.2K |
| **真正微核心原语**（不可移动） | `syscall/` | 系统调用层：telemetry/skill/session/sandbox | ~6.2K |
| **真正微核心原语**（不可移动） | `memory/` | 内置记忆 L1/L2 | ~1.5K |
| **真正微核心原语**（不可移动） | `taskflow/` | 通用 Pregel/DAG 图引擎（核心原语，非业务） | ~6.5K |
| **应用语义层**（物理保留，接口隔离） | `coreloopthree/` | 三层认知循环（反向依赖通过 ops 注入消除） | ~43.9K |
| **应用语义层**（物理保留，接口隔离） | `frameworks/` | 外部 AI 框架适配器注册表 | ~0.6K |
| **商业隔离层** | `memoryrovol/` | 商业记忆桥接（仅头文件，独立闭源仓库） | ~0.012K |

**强制要求**：
- 必须新增 `agentrt/agentrt/atoms/BOUNDARY.md` 文档化三类模块分类
- coreloopthree/frameworks 的反向依赖必须通过 ops 抽象表消除（见 ARC-04）
- taskflow 保留在 atoms（是核心原语），仅解耦对 coreloopthree 的链接依赖

**禁止行为**：
- 禁止 atoms 层 `#include` daemons 头文件（通过 ops 注入替代）
- 禁止 atoms 层 CMakeLists.txt 编译 daemons 源文件
- 禁止 atoms 层出现对 daemons 的编译期绑定

### 33.2 反向依赖禁止（ARC-02）

**强制规则 ARC-02**: atoms 层禁止依赖任何上层模块（daemons/cognition_engine/framework_registry/taskflow/gateway/heapstore）。

**检测方法**：
```bash
grep -rn '#include.*daemons/' agentrt/agentrt/atoms/ | grep -v ".git/"
grep -rn '#include.*gateway/' agentrt/agentrt/atoms/ | grep -v ".git/"
grep -rn '#include.*heapstore/' agentrt/agentrt/atoms/ | grep -v ".git/"
grep -rn 'daemons/' agentrt/agentrt/atoms/*/CMakeLists.txt
```

上述命令必须全部返回 0。

**已知违规（v3.3 发现，必须修复）**：
- `atoms/coreloopthree/CMakeLists.txt:46-54` 直接编译 5 个 daemons 源文件进 atoms 库
- `atoms/coreloopthree/CMakeLists.txt:149-150` 反向 include `daemons/common/include`、`daemons/llm_d/include`

**修复方式**：
- 引入适配器接口层：atoms 定义抽象接口（`agentrt_daemons_adapter.h`），daemons 实现并注入
- atoms 不再直接编译 daemons 源文件，而是通过适配器调用

### 33.3 atoms 可独立编译（ARC-03）

**强制规则 ARC-03**: atoms 层必须可独立编译，不依赖外部 daemons 源文件。

**验证命令**：
```bash
cmake --build build --target agentrt_atoms_standalone
```

此命令必须成功，且构建产物不包含任何 daemons 符号。

**当前状态**：atoms 不可独立编译（依赖 daemons 源文件），必须在 P0.17.4 修复后达到此标准。

### 33.4 层级倒置修复 — 接口反转（ARC-04，方案 A 修正）

**强制规则 ARC-04**: 禁止 atoms 层编译 daemons 源文件，禁止 atoms 层 include daemons 头文件。**通过 ops 抽象表 + daemons init 时注入消除反向依赖，atoms 文件物理位置不变**。

**修复路径（方案 A 接口反转）**：
1. 在 `atoms/coreloopthree/include/` 新增三个 ops 抽象表头文件（不依赖 daemons 头）：
   - `agentrt_checkpoint_ops_t`（save/restore/list/delete）
   - `agentrt_hook_ops_t`（trigger/register/unregister/list）
   - `agentrt_orch_ops_t`（dispatch/coordinate/audit/replan）
2. coreloopthree 内部新增全局注入点 + setter：`agentrt_loop_set_checkpoint_ops(loop, &ops)`
3. daemons 层实现 ops 实例并在 init 时注入：
   - `daemons/common/src/checkpoint.c` → `g_daemons_checkpoint_ops`
   - `daemons/hook_d/src/hook_service.c` → `g_daemons_hook_ops`
   - `daemons/common/src/orchestrator.c` → `g_daemons_orch_ops`
4. coreloopthree 内部调用改为 ops 表分发：
   ```c
   if (g_checkpoint_ops && g_checkpoint_ops->save) {
       g_checkpoint_ops->save(...);
   } else {
       return AIRY_ERR_NOT_INITIALIZED;  // 优雅降级
   }
   ```
5. CMakeLists.txt 删除 17 处反向依赖（7 处 daemons 源文件编译 + 10 处 daemons include path）
6. taskflow 保留在 atoms，仅解耦 `target_link_libraries(agentrt_taskflow PUBLIC agentrt_coreloopthree)` → `PUBLIC agentrt_corekern`

**不移动文件的理由**：
- 用户明确约束"atoms 内的模块不能随意移动"
- taskflow 是通用 Pregel/DAG 核心原语（非业务），不应移到 daemons
- coreloopthree 虽语义上是应用层，但 43.9K LOC 物理迁移工程代价过高且历史断裂
- 方案 A 通过接口隔离达到与物理迁移相同的"无反向依赖"目标

**验证**：
- `grep -rn '#include.*daemons/' agentrt/agentrt/atoms/ | grep -v ".git/"` → 0
- `grep -rn 'daemons/' agentrt/agentrt/atoms/*/CMakeLists.txt agentrt/agentrt/atoms/*/src/*/CMakeLists.txt` → 0
- `cmake --build build --target agentrt_atoms_standalone` → 成功
- 启动 daemons 但不注入 ops → cognition 返回 `AIRY_ERR_NOT_INITIALIZED` 而非崩溃

### 33.5 airy_core_init() 初始化链完整（ARC-05）

**强制规则 ARC-05**: `airy_core_init()` 必须初始化所有必要的 atoms 子系统，并通过适配器注入点接受 daemons 层初始化。

**当前问题**：`core_init.c:25-113` 仅初始化 6 个子系统（mem→oom→task→ipc→time_eventloop→heapstore），缺失 cognition/memory/cupolas/frameworks_registry。

**修复后初始化链**：
1. atoms 层初始化（core_init 内）：mem → oom → task → ipc → time_eventloop → heapstore
2. daemons 层注入初始化（通过适配器）：cognition_engine → framework_registry → taskflow → cupolas → memory_engine

**验证**：启动日志显示完整初始化链，所有子系统均报告 INIT OK。

### 33.6 微内核遵循性验证（ARC-06，方案 A 修正）

**强制规则 ARC-06**: atoms 层必须满足以下 5 项验证标准（方案 A 版本，文件不移动）：

| 验证项 | 标准 | 验证命令 |
|--------|------|---------|
| 无反向依赖 | atoms 不依赖 daemon/gateway/heapstore（通过 ops 注入） | `grep -rn '#include.*daemon/' atoms/` → 0 |
| 无编译期绑定 | atoms CMakeLists 不编译 daemon 源文件 | `grep -rn 'daemon/' atoms/*/CMakeLists.txt atoms/*/src/*/CMakeLists.txt` → 0 |
| ops 注入隔离 | coreloopthree/frameworks 通过 ops 抽象表调用 daemon，无直接 include | `grep -rn '#include.*"checkpoint.h"\|"orchestrator.h"' atoms/coreloopthree/` → 0 |
| 优雅降级 | ops 未注入时返回 `AIRY_ERR_NOT_INITIALIZED` 而非崩溃 | 集成测试：启动 daemon 不注入 ops → cognition 优雅失败 |
| 独立编译 | atoms 可独立编译（不依赖外部 daemon 源文件） | `cmake --build build --target airy_atoms_standalone` → 成功 |

**CI 集成**：上述 5 项验证必须集成到 `quality-gate.sh` Gate 1（编译期）。

**说明（方案 A 与方案 B 的差异）**：
- 方案 A 不强制 atoms 总 LOC ≤ 30K（维持现状 ~84K LOC，含 coreloopthree 43.9K）
- 方案 A 不强制 coreloopthree/frameworks/taskflow 物理移出 atoms
- 方案 A 通过 ops 注入实现"无反向依赖"语义等价于物理迁移

### 33.7 三权分立与合约文件强化（ARC-07）

**强制规则 ARC-07**: 三权分立（团队 A/B/C）+ contract_*.h 合约文件机制必须强化为 atoms→daemon 的合约载体。

**当前合约文件**：
- `contracts/contract_A_B.h`（团队 A+B 接口合约）
- `contracts/contract_A_C.h`（团队 A+C 接口合约）
- `contracts/contract_B_C.h`（团队 B+C 接口合约）

**新增合约文件**（v3.3 强化）：
- `contracts/contract_atoms_daemon.h`（atoms→daemon 适配器接口合约）
- `contracts/contract_atoms_cupolas.h`（atoms→cupolas 安全合约）

**价值评估（用户问题 3 答复）**：
- 价值 1：跨团队并行开发，接口冻结后互不阻塞
- 价值 2：编译期合约验证（`contract_test.c` 编译通过即接口兼容）
- 价值 3：CI 合约版本变更检测，防止隐式接口漂移
- 价值 4：为 atoms 上移后的适配器接口层提供天然合约载体

**强制规则**：
- 所有跨团队接口必须通过合约文件定义
- 合约文件版本号变更必须触发 CI 告警
- 合约文件必须包含编译验证代码（`contract_test.c`）

### 33.8 架构规范 BAN 规则（ARC-08）

**强制规则 ARC-08**: 新增以下架构相关 BAN 规则：

| 编号 | 规则 | 检测方式 |
|------|------|---------|
| BAN-311 | 禁止 atoms 层 include daemon/ 头文件（通过 ops 注入替代） | `[ARCH-SCAN]` CI 步骤 |
| BAN-312 | 禁止 atoms 层 CMakeLists.txt 编译 daemon 源文件 | CMakeLists.txt 审查 |
| BAN-313 | 禁止 atoms 层 coreloopthree/frameworks 出现编译期 daemon 绑定（必须通过 ops 抽象表运行时注入） | `[ARCH-SCAN]` + 代码审查 |
| BAN-314 | 禁止 atoms 层业务模块（coreloopthree/frameworks）直接调用 daemon 函数（必须经 ops 表分发） | 代码审查 |
| BAN-315 | 禁止 taskflow 反向链接 coreloopthree（taskflow 仅依赖 corekern） | `grep 'airy_coreloopthree' atoms/taskflow/CMakeLists.txt` → 0 |
| BAN-316 | 禁止跨团队直接修改对方代码（必须通过合约文件） | git blame 审查 |
| BAN-317 | 禁止合约文件无版本号 | 头文件审查 |
| BAN-318 | 禁止合约文件无编译验证代码 | `contract_test.c` 存在性检查 |
| BAN-319 | 禁止 ops 注入点为空时崩溃（必须返回 `AIRY_ERR_NOT_INITIALIZED` 优雅降级） | 集成测试 |

**方案 A 修正说明**：原 BAN-313（atoms 总 LOC ≤ 30K）和原 BAN-315（atoms 禁止出现 cognition/taskflow/framework 关键字）已撤销——方案 A 下 atoms 文件物理位置不变，coreloopthree/frameworks/taskflow 保留在 atoms，通过 ops 注入实现"无反向依赖"语义等价。

---

## 第三十四章：开放标准规范（v24.7 新增）

> **来源**: v3.4 用户关键决策 2/3/5 — 正式化"开发标准"，将可外部采纳部分抽象为独立 ARE Standards 体系
> **核心原则**: Airymax 推动的"行业底座"开放标准体系（ARE Standards），目标是定义 Agent Runtime Environment 的三层标准接口，使第三方可独立实现兼容的 Agent 运行时。
> **配套文档**: `Docs/50-specifications/20-are-standards/`（L1/L2/L3 三层标准草案）

### 34.1 SDK 双层 API 规范（STD-01）

**强制规则 STD-01**: SDK 必须提供双层 API，对齐 OpenAI 生态并显式覆盖四个领域客户端。

**双层 API 设计**：
- **Manager 层**（向后兼容）：`Manager.cognition().process()` / `Manager.safety().check()`
- **嵌套资源 API 层**（对齐 OpenAI）：`/v1/cognition/process`、`/v1/safety/check`、`/v1/tools/execute`、`/v1/chat/completions`、`/v1/embeddings`

**显式客户端覆盖**（四语言 SDK 同步实现）：
| 客户端 | 方法 | 对齐 |
|--------|------|------|
| CognitionClient | `cognition.process/get_status/cancel` | Airymax 原生 |
| SafetyClient | `safety.check/scan/quarantine` | Airymax 原生 |
| ToolClient | `tool.execute/list/cancel` | Airymax 原生 |
| ChatClient | `chat.create/stream/function_call/tool_call` | OpenAI `/v1/chat/completions` |

**验证**：四语言 SDK（Rust/Python/Go/TypeScript）均有四个客户端实现。

### 34.2 IPC Bus 统一消息头规范（STD-02）

> **SSoT 声明**：IPC 消息头结构体权威定义位于 `include/airymax/ipc.h`（[SC] 共享契约层，agentrt 与 agentrt-linux 共享同一物理头文件，逐字节相同）。本节代码必须与 `docs/AirymaxRT/30-interfaces/06-ipc/README.md` §2.1（`struct airy_ipc_msg_hdr`，128 字节，8 字段，`__attribute__((packed))`，`_Static_assert(sizeof(...) == 128)`）以及源码 `agentrt/commons/include/airymax/ipc.h` 逐字节一致。

**强制规则 STD-02**: 所有 IPC 消息必须使用 128 字节统一消息头 `struct airy_ipc_msg_hdr`。

**消息头结构**（128 字节，[SC] 共享契约层）：
```c
/* include/airymax/ipc.h —— [SC] 共享契约层，agentrt 与 agentrt-linux 逐字节共享 */
#include <airymax/uapi_compat.h>  /* __u32/__u16/__u64/__u8 跨平台 UAPI 类型 */

#define AIRY_IPC_MAGIC    0x41524531u   /* 'ARE1' —— IPC 消息头 magic */
#define AIRY_IPC_HDR_SZ   128           /* 固定 128 字节消息头 */

/**
 * struct airy_ipc_msg_hdr - IPC message header (128 bytes, [SC] shared)
 * @magic: Must be AIRY_IPC_MAGIC (0x41524531 'ARE1').
 * @opcode: Operation code; see enum airy_ipc_op.
 * @flags: Message flags (AIRY_IPC_F_*).
 * @trace_id: Distributed trace identifier for cross-daemon tracing.
 * @timestamp_ns: Timestamp in nanoseconds (CLOCK_REALTIME).
 * @src_task: Source task identifier.
 * @dst_task: Destination task identifier.
 * @payload_len: Payload length in bytes (excludes this 128B header).
 * @reserved: 84 bytes padding, must be zero.
 *
 * Fixed 128-byte header, layout never changes. Shared between
 * agentrt (user-space) and agentrt-linux (kernel) via [SC] contract layer.
 * Recipients MUST validate magic before processing.
 */
struct airy_ipc_msg_hdr {
    __u32   magic;          /* offset 0,  'ARE1' (0x41524531) */
    __u16   opcode;         /* offset 4,  操作码（见 enum airy_ipc_op） */
    __u16   flags;          /* offset 6,  消息标志（AIRY_IPC_F_*） */
    __u64   trace_id;       /* offset 8,  分布式追踪 ID（贯穿全链路） */
    __u64   timestamp_ns;   /* offset 16, 纳秒时间戳（CLOCK_REALTIME） */
    __u64   src_task;       /* offset 24, 源任务 ID（整型 task ID，非字符串） */
    __u64   dst_task;       /* offset 32, 目标任务 ID（整型 task ID，非字符串） */
    __u32   payload_len;    /* offset 40, 负载长度（不含本 128B 头） */
    __u8    reserved[84];   /* offset 44, 84 字节保留，必须为零 */
} __attribute__((packed));

_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128,
    "IPC message header must be exactly 128 bytes");
```

**强制要求**：
- `sizeof(struct airy_ipc_msg_hdr) == 128`（编译期 `_Static_assert` 强制验证）
- magic 不匹配则拒绝连接并返回 `AIRY_EPROTO`
- trace_id 字段强制填充（跨进程贯穿）
- 开放标准推动路径：v0.1.1 文档发布 → v0.2.0 参考实现 → v0.3.0 IETF 草案 → v1.0.0 正式发布

**与早期草案的对应关系**（仅供迁移参考）：

| 早期草案字段（已废弃 `are_ipc_message_header_t`） | SSoT 字段（`struct airy_ipc_msg_hdr`） | 说明 |
|--------------------------------------------------|--------------------------------------|------|
| `uint32_t magic` | `__u32 magic` | 类型改为 UAPI `__u32` |
| `uint16_t version` | — | 移除（version 由 `opcode`/`flags` 承载） |
| `uint16_t msg_type` | `__u16 opcode` | 重命名为 `opcode`，对齐 `enum airy_ipc_op` |
| `uint32_t protocol` | — | 移除（protocol 由上层协议层处理） |
| `uint64_t msg_id` | — | 移除（msg_id 由 `trace_id` + `src_task` 推导） |
| `uint64_t trace_id` | `__u64 trace_id` | 保留，类型改为 UAPI `__u64` |
| `uint64_t correlation_id` | — | 移除（correlation 由 `trace_id` 复用） |
| `char source[32]` | `__u64 src_task` | 改为整型 task ID |
| `char target[32]` | `__u64 dst_task` | 改为整型 task ID |
| `uint32_t payload_len` | `__u32 payload_len` | 保留，类型改为 UAPI `__u32` |
| `uint32_t flags` | `__u16 flags` | 类型改为 UAPI `__u16` |
| `uint64_t timestamp_ns` | `__u64 timestamp_ns` | 保留，类型改为 UAPI `__u64` |
| `uint32_t checksum` | — | 移除（CRC32 由传输层处理） |
| `uint32_t reserved` | `__u8 reserved[84]` | 扩展为 84 字节保留区 |

### 34.3 服务发现多后端适配器规范（STD-03）

**强制规则 STD-03**: 服务发现必须通过统一适配器接口 `are_svc_discovery_adapter_t` 支持五种后端。

**五种后端**：
| 后端 | 适用场景 | 实现 |
|------|---------|------|
| shm | 高性能本地（单机/单容器） | 现有 SHM 重构为 `shm_adapter.c` |
| dns-sd | 局域网多机部署 | 基于 avahi/mDNS |
| consul | 云上生产部署 | HTTP API 调用 Consul |
| etcd | K8s 环境非原生 service | gRPC 调用 etcd v3 |
| k8s | K8s 原生部署 | K8s API server watch EndpointSlice |

**配置选择**：`agentrt.yaml` 的 `service_discovery.backend: shm|dns-sd|consul|etcd|k8s`

### 34.4 JSON-RPC 方法命名空间规范（STD-04）

**强制规则 STD-04**: 所有 JSON-RPC 方法名必须为 `<daemon>.<method>` 格式，禁止扁平方法名。

**12 个 daemons 命名空间**：
`llm.`/`tool.`/`sched.`/`mem.`/`agent.`/`a2a.`/`mcp.`/`hook.`/`plugin.`/`cupolas.`/`monit.`/`market.`

**已知冲突（必须修复）**：
- `register_agent` @ market_d/sched_d → `market.register_agent`/`sched.register_agent`
- `health_check` @ monit_d/market_d/sched_d → `monit.health_check`/`market.health_check`/`sched.health_check`

**验证**：`grep -rn 'json_rpc_register_method.*"[a-z]_' agentrt/agentrt/daemons/` → 0（无下划线开头的扁平名）

### 34.5 统一错误码规范（STD-05）

**强制规则 STD-05**: 全项目错误码必须由唯一权威源定义，禁止多套并行系统。

**权威源**：`agentrt/commons/utils/error/include/error.h` 为唯一定义源（v4.0 修正：原 `agentos/` 路径已对齐 SSoT 方案 A 改为 `agentrt/`）。

**分段规范（v4.0 修正：对齐 SSoT 11 段方案 A，与 §4.9 一致）**：
| 段 | 范围 | 用途 |
|----|------|------|
| 成功 | 0 | `AIRY_EOK`/`AIRY_OK`/`AIRY_SUCCESS`（等价，定义于 `airy_types.h`） |
| 通用基础 | -1~-99 | 基础错误（参数/内存/超时等）+ POSIX errno 负值 + -40~-48 扩展迁移码 |
| 系统与平台 | -100~-199 | 系统与平台错误（含 -120~-123 迁移系统码） |
| 内核层 | -200~-299 | 内核层错误（IPC/任务/同步/锁/内存/调度/定时器/中断） |
| 服务层 | -300~-399 | 服务层错误（未就绪/忙/停止/配置/依赖/健康/负载均衡） |
| LLM/AI 服务 | -400~-499 | LLM/AI 服务错误（无 Provider/Provider 失败/限流/上下文/模型/鉴权/Token/解析/空响应/成本） |
| 执行/工具 | -500~-599 | 执行/工具错误（未找到/失败/超时/校验/沙箱/权限/参数/环境） |
| 记忆/存储 | -600~-699 | 记忆/存储错误（写/读/查询/演化/满/损坏/未初始化） |
| 安全/沙箱 | -700~-799 | 安全/沙箱错误（含 Cupolas 安全穹顶 -712~-799 专属段） |
| 协调/规划 | -800~-899 | 协调/规划错误（计划失败/同步失败/调度/意图/补偿/重试超限） |
| 协议/校验 | -900~-909 | 协议/校验错误（IPC 消息头校验/CRC32 校验和，消息必须丢弃） |

> **v4.0 SSoT 对齐说明**：原 §34.5 为 9 段（缺"成功"+"协调/规划"，且将 -800~-899 误标为"协议"），已对齐 SSoT 方案 A 11 段。`AIRY_E*` POSIX 风格码权威定义位于 `airy_types.h`；`AIRY_ERR_*` 扩展码定义位于 `error.h`。详见 §4.9 错误码分段表。

**已知冲突（必须修复）**：Cupolas 三套并行错误码系统（commons / cupolas enum / cupolas 本地 #define）数值冲突，必须统一到 commons 权威源。

### 34.6 ARE Standards 三层标准（STD-06）

**强制规则 STD-06**: ARE Standards 必须包含三层标准文档，标注 draft 状态，v0.1.1 发行前冻结。

**三层标准**：
| 层级 | 标准 | 文档 |
|------|------|------|
| L1 | 核心运行时接口 | `are_standards/L1_runtime_interface.md` |
| L2 | 服务通信协议 | `are_standards/L2_service_protocol.md` |
| L3 | 安全与治理 | `are_standards/L3_security_governance.md` |

**标准化路线图**：草案（v0.1.1）→ 试用（v0.2.0）→ 候选（v0.3.0）→ 正式（v1.0.0）

### 34.7 独立仓库可行性（STD-07）

**强制规则 STD-07**: ARE Standards 可独立发布为 `are-standards` 仓库，与 Airymax 主仓库分离。

**可行性依据**：
- `Docs/` 已是独立 git submodule（`git@atomgit.com:openairymax/docs.git`）
- `50-specifications/20-are-standards/` 作为标准容器
- 参考实现保留在 Airymax 主仓库，标准文档独立发布
- 治理模型：SPHARX Ltd. 主导标准制定 + 社区贡献流程

### 34.8 开放标准 BAN 规则（STD-08）

**强制规则 STD-08**: 新增以下开放标准相关 BAN 规则：

| 编号 | 规则 | 检测方式 |
|------|------|---------|
| BAN-320 | 禁止 SDK 使用扁平方法名调用（必须用嵌套资源 API 或 Manager 模式） | 代码审查 |
| BAN-321 | 禁止 IPC 消息不填充 trace_id 字段 | `[IPC-SCAN]` CI 步骤 |
| BAN-322 | 禁止 IPC 消息 magic 字段不校验 | 集成测试 |
| BAN-323 | 禁止 service_discovery 硬编码 SHM 后端（必须可通过配置切换） | 配置审查 |
| BAN-324 | 禁止 JSON-RPC 注册扁平方法名（必须 `<daemon>.<method>`） | `[RPC-SCAN]` CI 步骤 |
| BAN-325 | 禁止 cupolas 本地 `#define` 错误码（必须引用 commons 权威源） | `[ERROR-SCAN]` CI 步骤 |
| BAN-326 | 禁止 ARE Standards 文档无版本号 | 文档审查 |
| BAN-327 | 禁止标准文档无一致性测试套件 | v0.3.0 候选阶段强制 |

---

## 第三十五章：奠基性版本工程规范（FOUND-01~FOUND-10）

> **章节定位**: 0.1.1 是 Airymax 唯一的奠基版本（无 0.1.2/0.2.0/0.3.0 计划，直接过渡到 1.0.1）。所有架构、标准、许可证、质量和生态工作必须在 0.1.1 内完成。本章落实 v3.5 第二十五章的 5 大核心决策为可执行的工程规范，配套 W01-W30 工作清单（详见详细任务清单 v1.7.0 第六部分）。
>
> **规范来源**: 用户 2026-07-04 关键决策 + taskflow vs corekern scheduler 对比报告 v1.0 + lizard v1.23.0 + 自定义重复检测器基线扫描。

### 35.1 CoreKern 精简方案 C 工程规范（FOUND-01）

**强制规则 FOUND-01**: CoreKern 必须从 7,522 行精简至 ~4,000 行（±200 容差），0.1.1 内完成。

**精简范围（5 类必移出）**:

| 类别 | 行数 | 移出策略 | 目标位置 |
|------|:----:|---------|---------|
| Observability | 682 | ops 钩子保留，实现移出 | `agentos/daemons/observability_d/` |
| OOM Handler | 1033 | 5 级压力框架骨架保留，逻辑移出 | `agentos/daemons/oom_d/` |
| Kahn 拓扑排序 | 300 | 接口声明保留，算法实现移出 | `agentos/frameworks/scheduler/` |
| 冗余分配器（9→3） | ~600 | 合并为 slab+buddy+region 三种 | 仅保留 3 种 |
| syscall 业务逻辑 | ~400 | 纯 POSIX 封装保留，业务移出 | `agentos/daemons/` 对应模块 |
| **合计** | **~3015** | — | — |

**保留原则**:
- atoms/corekern/ 必须保持纯原语（A 类微核心原语）
- 所有移出功能通过 ops 抽象接口暴露（atoms 调用，daemon 注入实现）
- atoms 文件物理位置不变（方案 A 接口反转，非方案 B 物理迁移）

**检测方式**: CI 行数检查 `wc -l atoms/corekern/src/**/*.c` ≤ 4200；`[FOUND-SCAN]` 静态扫描禁止业务代码。

### 35.2 CoreKern 6 类 BUG 修复规范（FOUND-02）

**强制规则 FOUND-02**: CoreKern 6 类 BUG 必须在 0.1.1 内全部修复，ASan/LSan 全量验证。

| BUG 编号 | 类别 | 修复规范 |
|---------|------|---------|
| BUG-1 | 内存泄漏 | scheduler_core.c 退出路径必须 `free(task_node)`，使用 `goto cleanup` 模式 |
| BUG-2 | 锁顺序倒置 | 定义全局锁顺序：scheduler_core → scheduler_posix → task_node，禁止倒序获取 |
| BUG-3 | 条件变量虚假唤醒 | 必须 `while (condition) pthread_cond_wait()`，禁止 `if (condition)` |
| BUG-4 | 原子操作误用 | 32 位平台必须用 `_Atomic` 或 `__atomic_*` 内建，禁止非对齐访问 |
| BUG-5 | 栈溢出 | 递归深度必须限制（`max_depth = 32`），超限改为迭代 |
| BUG-6 | 信号处理器非异步信号安全 | signal handler 中禁止 `printf`，必须用 `write()` + 异步信号安全函数 |

**检测方式**: ASan/LSan CI 全绿；`[FOUND-SCAN]` 检查 cond_wait 模式；fuzz 测试覆盖。

### 35.3 taskflow 双引擎协同规范（FOUND-03）

**强制规则 FOUND-03**: taskflow 模块保留在 atoms，按 A/B 类语义重新分类，0.1.1 内采用双引擎协同方案。

**A/B 类语义分类规范**:

| 模块 | 类别 | 定位 | 0.1.1 处置 |
|------|:---:|------|---------|
| graph_engine | A 类 | 真正微核心原语（DAG 构建+拓扑排序+并行执行） | 保留 A 类，无需 ops 适配 |
| pregel_engine | B 类 | 应用语义层（BSP 模型） | **0.1.1 强制 max_workers=1 降级** |
| taskflow_advanced | B 类 | 应用语义层（task 生命周期管理） | 作为 B 类 DAG 工作流编排引擎 |
| workflow_patterns | B 类 | 应用语义层（5 种工作流模式） | 与 taskflow_advanced 协同 |
| taskflow_execution_unit | B 类 | 应用语义层（执行单元） | 与 taskflow_advanced 协同 |

**双引擎协同方案**:
- **scheduler（A 类）**: 保持纯原语，不感知业务语义
- **taskflow_advanced（B 类）**: 作为 coreloopthree 的 DAG 编排引擎
- **pregel_engine（B 类）**: 0.1.1 内 max_workers=1 串行降级，1.0.1 再启用多 worker

**检测方式**: 编译期静态断言 `static_assert(MAX_WORKERS == 1)`；`[FOUND-SCAN]` 检查 B 类模块不直接调用 daemon 源。

### 35.4 taskflow 6 类 BUG 修复规范（FOUND-04）

**强制规则 FOUND-04**: taskflow 6 类 BUG 必须在 0.1.1 内全部修复，5 个测试文件 ctest 全绿。

| BUG 编号 | 类别 | 修复规范 |
|---------|------|---------|
| #1 ODR 违规 | 符号冲突 | 同名结构体必须重命名（`taskflow_task_node_t` vs `daemon_task_node_t`），增加 `-Wodr` 编译期检测 |
| #2 类型混淆 | 类型安全 | `task_handle_t` 禁止强转，必须用 union 或泛型接口 |
| #3 返回码恒 SUCCESS | 错误处理 | 所有 taskflow_* 函数必须返回 `taskflow_status_t`，调用方必须检查 |
| #4 pause-resume 不更新状态 | 状态管理 | pause 后立即 `task->state = TASK_PAUSED`，resume 后 `TASK_RUNNING` |
| #5 错误宏放置错误 | 代码规范 | `TASKFLOW_ERROR()` 宏必须在 return 之前，禁止在 return 之后 |
| #6 partition 桩函数 | 功能完整 | 必须实现真实 partition 算法（hash + 取模），禁止 no-op |

**检测方式**: `[FOUND-SCAN]` 检查返回码检查模式；5 个测试文件 ctest 全绿。

### 35.5 SDK 双层 API 4 语言规范（FOUND-05）

**强制规则 FOUND-05**: SDK 必须在 0.1.1 内完成 Python + Rust + Go + TypeScript 4 语言 × 4 嵌套资源 API，共 16 个嵌套客户端。

**4×4 嵌套客户端矩阵**:

| 语言 | CognitionClient | SafetyClient | ToolClient | ChatClient |
|------|:---:|:---:|:---:|:---:|
| Python | ✅ | ✅ | ✅ | ✅ |
| Rust | ✅ | ✅ | ✅ | ✅ |
| Go | ✅ | ✅ | ✅ | ✅ |
| TypeScript | ✅ | ✅ | ✅ | ✅ |

**双层 API 架构**:
- **Layer 1（C ABI）**: 统一 C 接口，4 语言通过 FFI/ctypes/cgo/N-API 调用
- **Layer 2（语言原生包装）**: 各语言 idiomatic 风格（Python: Pythonic；Rust: async/await + trait；Go: context.Context + goroutine；TypeScript: Promise + .d.ts）

**API 命名规范**:
- CognitionClient: `cognition.process()` / `cognition.reflect()` / `cognition.evolve()`
- SafetyClient: `safety.validate()` / `safety.sanitize()` / `safety.audit()`
- ToolClient: `tool.invoke()` / `tool.list()` / `tool.register()`
- ChatClient: `chat.send()` / `chat.stream()` / `chat.history()`

**检测方式**: `[SDK-SCAN]` 检查禁止扁平方法名；4 语言各自 e2e 测试通过（非 mock）。

### 35.6 SDK L1 C ABI 接口规范（FOUND-06）

**强制规则 FOUND-06**: 4 语言 SDK 必须严格遵循 L1 C ABI 接口规范，CTS 一致性测试套件全绿。

**L1 C ABI 接口定义**（参考 ARE Standards L1）:
- 函数命名: `airy_<resource>_<action>`（如 `airy_cognition_process`）
- 参数顺序: `(handle, request, response, error_info)` 固定四参数
- 返回值: `airy_status_t`（枚举：SUCCESS/INVALID_PARAM/NOT_FOUND/INTERNAL/UNAVAILABLE）
- 错误处理: `error_info` 结构体含 code + message + trace_id
- 内存所有权: 调用方分配 request，被调方分配 response，调用方负责释放

**CTS 一致性测试**:
- 4 语言各自实现相同的 100 个测试用例
- 覆盖 4 个资源 API × 25 个场景
- 跨语言行为一致性验证

**检测方式**: CTS 测试套件全绿；`[SDK-SCAN]` 检查 L1 接口签名一致性。

### 35.7 AGPL v3 + Apache 2.0 双许可证规范（FOUND-07）

**强制规则 FOUND-07**: 全项目必须采用 `AGPL-3.0-or-later OR Apache-2.0` 双许可证，版权人 SPHARX Ltd.。

**许可证统一范围**:

| 范围 | 数量 | 强制规范 |
|------|:----:|---------|
| 源代码 SPDX 标签 | 316 | `SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0` |
| Cargo.toml license 字段 | 4 | `license = "AGPL-3.0-or-later OR Apache-2.0"` |
| package.json license 字段 | 1 | `"license": "AGPL-3.0-or-later OR Apache-2.0"` |
| vcpkg.json license 字段 | 1 | `"license": "AGPL-3.0-or-later OR Apache-2.0"` |
| pyproject.toml license 字段 | 1 | `license = "AGPL-3.0-or-later OR Apache-2.0"` |
| contract.json license 字段 | 7 | `"license": "AGPL-3.0-or-later OR Apache-2.0"` |
| README 许可证声明 | 4 | 必须含 `AGPL v3 + Apache 2.0 双许可证` + `版权人 SPHARX Ltd.` |
| ARE standards 文档 | 4 | 头部 + 尾部双许可证声明 |
| coding_standard 文档 | 5 | SPDX 示例必须为双许可证 |

**禁止事项**:
- 禁止单一 Apache-2.0 标签（BAN-338）
- 禁止 GPL-3.0-or-later（与 AGPL 不兼容）
- 禁止 MIT（不符合商业策略）
- 禁止 SPHARX-Proprietary（已废止，由双许可证取代）

**检测方式**: `[LICENSE-SCAN]` CI 步骤；`grep -r "Apache-2.0$" --include="*.c"` 返回 0。

### 35.8 静态分析基线规范（FOUND-08）

**强制规则 FOUND-08**: lizard v1.23.0 + 自定义重复检测器必须达到基线阈值，0.1.1 发布前 CCN>100 函数数 ≤ 5，重复率 < 15%。

**lizard v1.23.0 基线（全项目扫描）**:

| 维度 | 基线值（v3.5 扫描） | 0.1.1 目标 | 1.0.1 目标 |
|------|:---:|:---:|:---:|
| 总函数数 | 18,716 | — | — |
| CCN > 15 函数数 | 1,603 | ≤ 800 | ≤ 200 |
| CCN > 30 函数数 | 311 | ≤ 150 | ≤ 50 |
| CCN > 50 函数数 | 74 | ≤ 30 | ≤ 10 |
| CCN > 100 函数数 | 10 | ≤ 5 | ≤ 2 |
| 最高 CCN | 252（browser_execute） | ≤ 100 | ≤ 50 |

**Top 5 极端函数（必须拆分）**:

| 函数名 | CCN | 拆分目标 |
|--------|:---:|---------|
| browser_execute | 252 | 5 个子函数 + 1 个调度器 |
| airy_cognition_process | 243 | Phase 1/2/3 三个独立函数 |
| execute_single_phase | 218 | 按 phase type 分派表 |
| parse_value | 132 | 按 type 分派表 |
| yaml_parse_value | 124 | 同上 |

**自定义重复检测器基线**:

| 维度 | 基线值 | 0.1.1 目标 |
|------|:---:|:---:|
| 扫描文件数 | 1,686 | — |
| 跨文件重复块 | 2,314 | ≤ 1,500 |
| 重复行 | 25,512 | ≤ 18,000 |
| 显著重复文件 | 316 | ≤ 200 |
| 重复率 | ~17% | < 15% |
| 最高重复文件 | ToolManager.tsx (1,404 行) | ≤ 500 行 |

**拆分操作规范**:
1. 每次拆分前后必须跑 lizard + 重复检测器对比
2. 保留原函数作为 fallback（R45 缓解）
3. 拆分后单元测试覆盖率不得下降
4. 性能基准测试对比（拆分前后吞吐率不低于 95%）

**检测方式**: lizard CI 门禁（BAN-340）；`[DUP-SCAN]` 重复检测 CI 步骤。

### 35.9 静态分析操作规范（FOUND-09）

**强制规则 FOUND-09**: 静态分析优化必须遵循"先基线后优化"原则，禁止无基线的盲目拆分。

**操作流程**:
1. **基线扫描**: `lizard --CCN 15 --length 100 --arguments 5 --working_threads 4 <path>` 输出 JSON 报告
2. **重复检测**: 自定义检测器输出跨文件重复块 + 重复行统计
3. **优先级排序**: CCN > 100 优先（P0）→ CCN 50-99 次（P1）→ CCN 30-49 后（P2）
4. **拆分执行**: 每次只拆分 1 个函数，立即跑测试验证
5. **回归验证**: lizard 对比 + 重复检测对比 + 单元测试全绿
6. **文档更新**: 更新基线报告，记录拆分前后数据

**禁止事项**:
- 禁止无基线的盲目拆分（可能引入回归）
- 禁止拆分良好设计的函数（CCN 高但逻辑清晰）
- 禁止为降 CCN 而拆分（必须基于可读性 + 可维护性）
- 禁止拆分后不跑测试（必须 lizard + 重复检测 + 单元测试三重验证）

**检测方式**: PR 必须附 lizard 前后对比报告；代码审查检查拆分合理性。

### 35.10 唯一奠基版本工程铁律（FOUND-10）

**强制规则 FOUND-10**: 0.1.1 是唯一奠基版本，必须遵循以下工程铁律，禁止任何例外。0.1.1 之后直接 1.0.1，无 0.1.2/0.2.0/0.3.0/1.0.0 中间过渡版本。

**9 大工程铁律**:

| 铁律编号 | 内容 | 理由 | 定义章节 |
|---------|------|------|---------|
| IRON-1 | **禁止新特性**: 0.1.1 不引入任何新功能，仅修复 + 集成 + 标准化 | 唯一奠基版本无回退窗口（R44） | §35.10 |
| IRON-2 | **禁止桩函数/桩文件**: 所有功能必须真实实现，禁止 no-op / TODO / FIXME | 用户硬约束 | §35.10 |
| IRON-3 | **禁止绕开功能限制的编译/集成**: 禁止 `#ifdef DISABLE_*` 绕过检查 | 用户硬约束 | §35.10 |
| IRON-4 | **禁止简化功能**: 不允许"为了 0.1.1 先简化，1.0.1 再完善" | 用户硬约束 | §35.10 |
| IRON-5 | **禁止未实现的功能设计**: 文档中的设计必须有对应实现 | 用户硬约束 | §35.10 |
| IRON-6 | **禁止跨层耦合残留**: 0.1.1 拆仓前必须完成 5 处跨层耦合解耦（SP02-SP06），任何残留即拆仓失败 | 38 仓独立构建硬约束 | §36.1 |
| IRON-7 | **禁止版本过渡**: 0.1.1 之后直接 1.0.1，禁止 0.1.2/0.2.0/0.3.0/1.0.0 中间版本，禁止兼容别名头/兼容层/双轨制 | 用户硬约束（2026-07-05） | §36.1 |
| IRON-8 | **禁止生产就绪降级**: SP32-SP37 生产就绪 6 项全部必须达标，未达标禁止发布 0.1.1 | 一切以生产就绪为目标 | §36.1 |
| IRON-9 | **agentrt 和 AirymaxOS 同源且部分代码共享**（IRON-9 v2，2026-07-07 变更）: 三层共享模型：[SC] 共享契约层（`include/airymax/` 6 个头文件完全共享：memory_types.h / security_types.h / cognition_types.h / sched.h / ipc.h / syscalls.h；另含补充共享文件 bpf_struct_ops.h，非 [SC] 核心头文件）+ [SS] 语义同源层（API 签名同源，实现独立）+ [IND] 完全独立层。agentrt 保持跨平台用户态纯净（不依赖任何特定 OS），AirymaxOS 是完整发行版（基于 Linux 内核 + 微内核化改造）。代码共享边界：代码共享仅限于 agentrt 与 agentrt-linux 之间，与 Euler 项目仅技术参考，不共享代码。AirymaxOS 工程思想与 Euler 保持一致性（协议层 + 接入层 + 模块化 + 工具链兼容） | AirymaxOS 与 AirymaxAgentRT 架构分离硬约束（2026-07-06，2026-07-07 IRON-9 v2 变更） | §38.1 |
| IRON-10 | **禁止引用 Linux 7.0 专属特性作为 6.6 原生能力**: AirymaxOS 基于 Linux 6.6（openEuler 24.03 LTS 内核版本），禁止引用 Linux 7.0 专属特性（PREEMPT_LAZY / Rust 正式转正 / MGLRU 2.0 / XFS 自修复 / eBPF 签名验证等）作为 Linux 6.6 原生能力。正确表述：EEVDF 调度器 / Rust 实验性支持 / MGLRU 多代 LRU / sched_ext（openEuler backport，主线 6.12+）/ eBPF kfunc + dynamic pointer / XFS 在线 fsck | Linux 6.6 内核版本兼容性硬约束（2026-07-06） | §38.10 |

**例外审批流程**:
- 任何铁律例外必须经用户书面批准
- 例外必须记录在 `DocsClosed/exceptions.md` 中
- 例外必须有明确的修复计划和时间表

**检测方式**: `[FOUND-SCAN]` 检查 TODO/FIXME/no-op/stub；`[SPLIT-SCAN]` 5 处耦合扫描 + `[PROD-SCAN]` 生产就绪 6 项检查；版本号静态断言；代码审查检查"绕开"模式；集成测试检查功能完整度。

### 35.11 v3.5 新增 BAN 规则（BAN-328~BAN-340）

**强制规则**: 新增以下 v3.5 唯一奠基版本相关 BAN 规则：

| 编号 | 规则 | 检测方式 |
|------|------|---------|
| BAN-328 | 禁止 atoms/corekern/ 包含 Observability 实现代码（仅保留 ops 钩子声明） | `[FOUND-SCAN]` |
| BAN-329 | 禁止 atoms/corekern/ 包含 OOM Handler 实现代码（仅保留 5 级压力框架骨架） | `[FOUND-SCAN]` |
| BAN-330 | 禁止 atoms/corekern/scheduler/ 包含 Kahn 拓扑排序算法实现 | `[FOUND-SCAN]` |
| BAN-331 | 禁止 atoms/corekern/memory/ 中分配器种类 > 3（仅 slab/buddy/region） | `[FOUND-SCAN]` |
| BAN-332 | 禁止 atoms/syscall/ 包含业务逻辑代码（仅保留纯 POSIX 跨平台封装） | `[FOUND-SCAN]` |
| BAN-333 | 禁止 taskflow pregel_engine max_workers > 1（0.1.1 强制串行降级） | 编译期静态断言 |
| BAN-334 | 禁止 taskflow_advanced 调用方未检查返回码（必须 `if (rc != TASKFLOW_SUCCESS)`） | `[FOUND-SCAN]` |
| BAN-335 | 禁止 taskflow_advanced.c 的 `TASKFLOW_ERROR()` 宏放置在 return 之后 | `[FOUND-SCAN]` |
| BAN-336 | 禁止 taskflow pause/resume 后未更新 task 状态字段 | 集成测试 |
| BAN-337 | 禁止 SDK 4 语言客户端使用扁平方法名（必须 CognitionClient/SafetyClient/ToolClient/ChatClient 嵌套） | `[SDK-SCAN]` |
| BAN-338 | 禁止源代码 SPDX 标签为单一 Apache-2.0（必须 `AGPL-3.0-or-later OR Apache-2.0`） | `[LICENSE-SCAN]` |
| BAN-339 | 禁止 CoreKern 总行数 > 4200（±200 容差，目标 ~4000） | CI 行数检查 |
| BAN-340 | 禁止高 CCN 函数（CCN > 100）未经审查直接合入主分支 | lizard CI 门禁 |

> **v4.0 扩展铁律 IRON-6~IRON-8**（追加于第三十六章 §36.2，详见该章节）

---

## 第三十六章：38 仓 git 拆分工程规范（SPLIT-01~SPLIT-08，v26.0 v4.0 新增）

> **章节定位**: 本章是 §11.7「38 仓 git submodule 拆分规范」的工程实践详尽版，提供从目录结构到 git subtree split、submodule 同步、CI 集成的完整工程规范。所有 SPLIT 编号与 §11.7 一致并扩展。0.1.1 是唯一奠基版本（无 0.2.0/0.3.0/1.0.0 过渡，直接到 1.0.1），一切以生产就绪为目标。
>
> **目标读者**: 平台工程师、构建工程师、DevOps 工程师、仓库管理员。

### 36.1 v4.0 新增工程铁律（IRON-6~IRON-8）

**强制规则**: 在 IRON-1~IRON-5 基础上追加以下 v4.0 工程铁律，禁止任何例外。

| 铁律编号 | 内容 | 理由 |
|---------|------|------|
| IRON-6 | **禁止跨层耦合残留**: 0.1.1 拆仓前必须完成 5 处跨层耦合解耦（SP02-SP06），任何残留即拆仓失败 | 38 仓独立构建硬约束 |
| IRON-7 | **禁止版本过渡**: 0.1.1 之后直接 1.0.1，禁止 0.1.2/0.2.0/0.3.0/1.0.0 中间版本，禁止兼容别名头/兼容层/双轨制 | 用户硬约束（2026-07-05） |
| IRON-8 | **禁止生产就绪降级**: SP32-SP37 生产就绪 6 项全部必须达标，未达标禁止发布 0.1.1 | 一切以生产就绪为目标 |

**例外审批流程**: 同 §35.10。

**检测方式**: `[SPLIT-SCAN]` 5 处耦合扫描 + `[PROD-SCAN]` 生产就绪 6 项检查 + 版本号静态断言。

### 36.2 SPLIT-01：38 仓目录结构工程规范

**强制规则 SPLIT-01**: OpenAirymax 必须拆分为 **38 个 git 仓库**（1 伞仓 + 5 管理仓 + 29 叶子仓 + 3 顶层仓），结构必须与 §11.7.1 完全一致。

**38 仓清单**（与 §11.7.1 互引）:

| 类别 | 数量 | 仓库列表 |
|------|:---:|---------|
| 伞仓 | 1 | `airymaxhub` |
| 管理仓 | 5 | `agentrt`、`agentrt-linux`（AirymaxOS 管理仓）、`sdk`、`ecosystem`、`products` |
| C 层叶子仓 | 7 | `atoms`、`commons`、`cupolas`、`heapstore`、`protocols`、`gateway`、`daemons`（agentrt 管理仓的子仓） |
| AirymaxOS 叶子仓 | 8 | `airymaxos-kernel`、`airymaxos-services`、`airymaxos-security`、`airymaxos-memory`、`airymaxos-cognition`、`airymaxos-cloudnative`、`airymaxos-system`、`airymaxos-tests-linux`（agentrt-linux 管理仓的子仓） |
| SDK 叶子仓 | 6 | `sdk-python`、`sdk-go`、`sdk-rust`、`sdk-typescript`、`sdk-cli`、`sdk-tui` |
| 生态叶子仓 | 5 | `manager`、`prompts`、`examples`、`openlab`、`skills` |
| 产品叶子仓 | 3 | `desktop`、`docker`、`memoryrovol`（闭源 EULA） |
| 顶层仓 | 3 | `devtools`、`docs`、`docs-closed` |
| **合计** | **38** | — |

**submodule 嵌套层级**:

```
airymaxhub（L0）
├── agentrt（L1 管理仓）→ 7 个 L2 叶子仓
├── agentrt-linux（L1 管理仓，1.0.1）→ 6 个 L2 叶子仓
├── sdk（L1 管理仓）→ 6 个 L2 叶子仓
├── ecosystem（L1 管理仓）→ 5 个 L2 叶子仓
├── products（L1 管理仓）→ 3 个 L2 叶子仓
├── devtools（L1 顶层仓）
├── docs（L1 顶层仓）
└── docs-closed（L1 顶层仓）
```

**伞仓直属文件**（非 submodule，伞仓 git 直接管理）:
- `.gitmodules`（伞仓 submodule 声明，7 条）
- `cmake/`（5 个 CMake 模块：`compilerflags.cmake`、`sanitizers.cmake`、`dependencies.cmake`、`platform.cmake`、`utils.cmake`）
- `README.md`、`LICENSE`（AGPL v3 + Apache 2.0 双许可证）、`NOTICE`

### 36.3 SPLIT-02：仓库命名工程规范

**强制规则 SPLIT-02**: 全部仓库名 + 目录名小写；sdk 模块下子仓必须 `sdk-xx` 前缀；agentrt 管理仓 url 必须继承原 AgentRT 仓库。

**命名矩阵**（与 §11.7.2 一致并扩展）:

| 命名规则 | 强制 | 反例（禁止） | 正例（必须） |
|---------|:---:|------------|------------|
| 仓库名小写 | ✅ | `AgentRT`、`SDK-Python` | `agentrt`、`sdk-python` |
| 目录名小写 | ✅ | `agentrt/Daemon/` | `agentrt/daemons/` |
| sdk-xx 前缀 | ✅ | `sdk/python`、`sdkpython` | `sdk-python` |
| 裸名（无 agentrt- 前缀） | ✅ | `agentrt-atoms` | `atoms` |
| 伞仓 = airymaxhub | ✅ | `openairymax`、`airymax-hub` | `airymaxhub` |
| agentrt 继承 url | ✅ | `git@atomgit.com:openairymax/agentrt.git` | `git@atomgit.com:openairymax/agentos.git` |
| memoryrovol 归属 spharx | ✅ | `openairymax/memoryrovol.git` | `spharx/memoryrovol.git` |
| 进程二进制名 `*_d` | ✅ | `daemons/gateway` | `daemons/gateway_d`（保持不变） |

### 36.4 SPLIT-03：git 历史保留工程规范

**强制规则 SPLIT-03**: 不同仓库类型必须采用对应的 git 历史保留方式，详见 §11.7.3。

**git subtree split 详细操作规范**（适用于从 agentrt 管理仓拆分叶子仓）:

```bash
# 以 atoms 仓为例（其他 C 层叶子仓同理）
cd agentrt  # agentrt 管理仓工作目录

# 1. 创建临时分支保留 atoms 子目录历史
git subtree split --prefix=agentrt/atoms/ -b atoms-split-branch

# 2. 推送到独立仓库
git push git@atomgit.com:openairymax/atoms.git atoms-split-branch:main

# 3. 验证历史保留
git log --oneline atoms-split-branch | wc -l  # 应与原 agentrt/atoms/ 提交数一致

# 4. 清理临时分支
git branch -D atoms-split-branch

# 5. 在 agentrt 管理仓中删除子目录，添加 submodule
git rm -rf agentrt/atoms
git submodule add git@atomgit.com:openairymax/atoms.git agentrt/atoms
git commit -m "SP17: split atoms into independent submodule"
```

**agentrt 管理仓继承详细操作规范**:

```bash
# agentrt 管理仓直接继承原 AgentRT 仓库（不 clone 不 subtree）
cd AgentRT  # 原 AgentRT 仓库工作目录
git remote set-url origin git@atomgit.com:openairymax/agentos.git
# url 保持 git@atomgit.com:openairymax/agentos.git，仓库历史完整保留
git remote -v  # 验证 origin = git@atomgit.com:openairymax/agentos.git
git log --oneline | wc -l  # 与原 AgentRT 一致
```

### 36.5 SPLIT-04：7 阶段拆分顺序工程规范

**强制规则 SPLIT-04**: 7 阶段顺序必须严格遵循，详见 §11.7.4。

**阶段依赖关系图**:

```
阶段 1（W01-W30 奠基）
    │
    ├──→ 阶段 2（SP01 改名）
    │        │
    │        ├──→ 阶段 3（SP02-SP06 解耦）──→ 阶段 5（SP17-SP23 C 层拆分）
    │        │
    │        └──→ 阶段 4（SP07-SP16 立即可拆 10 仓）
    │                                          │
    │                                          ↓
    │                                    阶段 6（SP24-SP31 配套拆分 + 伞仓组装）
    │                                          │
    │                                          ↓
    │                                    阶段 7（SP32-SP37 生产就绪）
    │
    └──→ 阶段 6 阻塞条件：阶段 4+5 全部完成
```

**关键阻塞点**:
- 阶段 5（C 层拆分）必须等待阶段 3（解耦）完成，否则原子仓会触发跨层依赖未就绪
- 阶段 6（伞仓组装）必须等待阶段 4+5 全部完成
- 阶段 7（生产就绪）必须等待阶段 6 完成，且 38 仓独立构建全部通过

### 36.6 SPLIT-05：5 处跨层耦合解耦工程规范

**强制规则 SPLIT-05**: 5 处跨层耦合必须在 SP02-SP06 阶段全部解耦，详见 §11.7.5。

**解耦操作详细规范**:

```bash
# 解耦 #1：daemons/common/src/checkpoint.c + orchestrator.c → commons/utils/execution/
mkdir -p commons/utils/execution/
git mv daemons/common/src/checkpoint.c commons/utils/execution/
git mv daemons/common/src/orchestrator.c commons/utils/execution/
# 更新 CMakeLists.txt 引用
find . -name CMakeLists.txt -exec sed -i 's|daemons/common/src/checkpoint|commons/utils/execution/checkpoint|g' {} +
find . -name CMakeLists.txt -exec sed -i 's|daemons/common/src/orchestrator|commons/utils/execution/orchestrator|g' {} +

# 解耦 #2：cupolas/src/yaml_minimal.c → commons/utils/config_unified/
mkdir -p commons/utils/config_unified/
git mv cupolas/src/yaml_minimal.c commons/utils/config_unified/yaml_minimal.c

# 解耦 #3：daemons/hook_d/src/{5 个文件} → atoms/coreloopthree/src/hooks/
mkdir -p atoms/coreloopthree/src/hooks/
git mv daemons/hook_d/src/service.c atoms/coreloopthree/src/hooks/
git mv daemons/hook_d/src/hook_executor.c atoms/coreloopthree/src/hooks/
git mv daemons/hook_d/src/hook_registry.c atoms/coreloopthree/src/hooks/
git mv daemons/hook_d/src/hook_interceptor.c atoms/coreloopthree/src/hooks/
git mv daemons/hook_d/src/hook_timeout.c atoms/coreloopthree/src/hooks/
# daemons/hook_d 仅保留生命周期管理

# 解耦 #4：daemons/common/src/safe_string_utils.c → commons/utils/string/
mkdir -p commons/utils/string/
git mv daemons/common/src/safe_string_utils.c commons/utils/string/safe_string_utils.c

# 解耦 #5：cupolas 反向调用 gateway（改为回调函数指针注入）
# 在 cupolas 中定义回调函数指针类型，gateway 在初始化时注入实现
```

### 36.7 SPLIT-06：拆分验证工程规范

**强制规则 SPLIT-06**: 拆分完成后必须通过 §11.7.6 全部 9 项验证。

**自动化验证脚本**:

```bash
#!/bin/bash
# scripts/verify_split.sh - 38 仓拆分验证
set -euo pipefail

FAIL=0

# 1. 38 仓独立 clone + 构建
REPOS=(
  "airymaxhub" "agentrt" "sdk" "ecosystem" "products"
  "atoms" "commons" "cupolas" "heapstore" "protocols" "gateway" "daemons"
  "sdk-python" "sdk-go" "sdk-rust" "sdk-typescript" "sdk-cli" "sdk-tui"
  "manager" "prompts" "examples" "openlab" "skills"
  "desktop" "docker" "memoryrovol"
  "devtools" "docs" "docs-closed"
)

for repo in "${REPOS[@]}"; do
  echo "[SPLIT-SCAN] $repo ..."
  rm -rf /tmp/verify_$repo
  if git clone --depth=1 "git@atomgit.com:openairymax/$repo.git" /tmp/verify_$repo 2>/dev/null; then
    # memoryrovol 归属 spharx 组织
    if [ "$repo" = "memoryrovol" ]; then
      rm -rf /tmp/verify_$repo
      git clone --depth=1 "git@atomgit.com:spharx/memoryrovol.git" /tmp/verify_$repo
    fi
  else
    echo "[FAIL] $repo clone failed"
    FAIL=$((FAIL+1))
  fi
done

# 2. agentrt 管理仓历史保留
cd /tmp/verify_agentrt
HIST_COUNT=$(git log --oneline | wc -l)
echo "[SPLIT-SCAN] agentrt history: $HIST_COUNT commits"

# 3. agentrt 管理仓 url 验证
URL=$(git remote get-url origin)
[ "$URL" = "git@atomgit.com:openairymax/agentos.git" ] || { echo "[FAIL] agentrt url: $URL"; FAIL=$((FAIL+1)); }

# 4. 伞仓一次性拉取
cd /tmp && rm -rf airymaxhub_verify
git clone --recursive git@atomgit.com:openairymax/airymaxhub.git airymaxhub_verify
[ -f airymaxhub_verify/.gitmodules ] || { echo "[FAIL] airymaxhub .gitmodules missing"; FAIL=$((FAIL+1)); }

# 5. 目录名小写验证
CAP_DIRS=$(find /tmp/airymaxhub_verify -type d -name '[A-Z]*' 2>/dev/null | head -1)
[ -z "$CAP_DIRS" ] || { echo "[FAIL] uppercase dir: $CAP_DIRS"; FAIL=$((FAIL+1)); }

echo "===================="
[ $FAIL -eq 0 ] && echo "✅ SPLIT-06 ALL PASS" || echo "❌ SPLIT-06 FAIL: $FAIL"
exit $FAIL
```

### 36.8 SPLIT-07：submodule 同步与 CI 集成工程规范

**强制规则 SPLIT-07**: 所有 5 个管理仓必须维护 `.gitmodules`，所有 submodule 必须与父仓 main 分支同步；CI 流水线必须支持 `--recursive` 拉取。

**5 管理仓 .gitmodules 模板**:

**agentrt/.gitmodules**（7 条）:
```ini
[submodule "atoms"]
    path = atoms
    url = git@atomgit.com:openairymax/atoms.git
    branch = main
[submodule "commons"]
    path = commons
    url = git@atomgit.com:openairymax/commons.git
    branch = main
[submodule "cupolas"]
    path = cupolas
    url = git@atomgit.com:openairymax/cupolas.git
    branch = main
[submodule "heapstore"]
    path = heapstore
    url = git@atomgit.com:openairymax/heapstore.git
    branch = main
[submodule "protocols"]
    path = protocols
    url = git@atomgit.com:openairymax/protocols.git
    branch = main
[submodule "gateway"]
    path = gateway
    url = git@atomgit.com:openairymax/gateway.git
    branch = main
[submodule "daemons"]
    path = daemons
    url = git@atomgit.com:openairymax/daemons.git
    branch = main
```

**sdk/.gitmodules**（6 条）、**ecosystem/.gitmodules**（5 条）、**products/.gitmodules**（3 条）按 §11.7.1 推导。

**伞仓 .gitmodules**（7 条）:
```ini
[submodule "agentrt"]
    path = agentrt
    url = git@atomgit.com:openairymax/agentos.git
    branch = main
[submodule "sdk"]
    path = sdk
    url = git@atomgit.com:openairymax/sdk.git
    branch = main
[submodule "ecosystem"]
    path = ecosystem
    url = git@atomgit.com:openairymax/ecosystem.git
    branch = main
[submodule "products"]
    path = products
    url = git@atomgit.com:openairymax/products.git
    branch = main
[submodule "devtools"]
    path = devtools
    url = git@atomgit.com:openairymax/devtools.git
    branch = main
[submodule "docs"]
    path = docs
    url = git@atomgit.com:openairymax/docs.git
    branch = main
[submodule "docs-closed"]
    path = docs-closed
    url = git@atomgit.com:openairymax/docs-closed.git
    branch = main
```

**CI 集成规范**（GitHub Actions / GitLab CI）:

```yaml
# .github/workflows/build.yml（伞仓）
jobs:
  build:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive  # 必须 recursive，递归拉取所有嵌套 submodule
          ssh-key: ${{ secrets.DEPLOY_KEY }}
      - name: Build
        run: |
          cmake -B build -DCMAKE_BUILD_TYPE=Release
          cmake --build build -j$(nproc)
          ctest --test-dir build --output-on-failure
```

**submodule 同步操作规范**:

```bash
# 父仓更新 submodule commit 引用
cd airymaxhub
git submodule update --remote --merge  # 拉取子仓最新 main
git add .
git commit -m "chore: sync submodules to latest main"
git push

# 子仓变更后，父仓必须同步
cd agentrt
# ... 修改 atoms submodule 后
cd ..
git add agentrt
git commit -m "chore: bump agentrt submodule (atoms update)"
git push
```

### 36.9 SPLIT-08：跨平台构建工程规范

**强制规则 SPLIT-08**: 38 仓必须全部支持 Linux（Ubuntu 22.04+）/macOS（13+）/Windows（10+）三平台构建，禁止平台特定 hack。

**跨平台构建矩阵**:

| 平台 | 编译器 | CMake 生成器 | 构建命令 |
|------|--------|------------|---------|
| Linux | gcc 11+ / clang 14+ | Ninja | `cmake -B build -G Ninja && cmake --build build` |
| macOS | Apple clang 14+ | Ninja | 同上 |
| Windows | MSVC 19.30+ / MinGW | Ninja / VS2022 | 同上（Ninja）或 `cmake --build build --config Release`（VS） |

**跨平台约束**:
- 禁止 `#ifdef _WIN32` 业务逻辑分支（仅允许平台特定的 POSIX 封装层 `atoms/syscall/`）
- 禁止硬编码路径分隔符（必须使用 `cmake/path.cmake` 提供的 `path_join()`）
- 禁止使用 `popen`、`system` 等非跨平台 API（必须使用 `atoms/syscall/process.h` 抽象层）
- 禁止使用 `dlopen` 等平台特定符号（必须使用 `atoms/syscall/dynamic_load.h` 抽象层）

### 36.10 第三十六章 BAN 规则（BAN-349~BAN-350）

**强制规则**: 新增以下 v4.0 仓库拆分工程 BAN 规则（在 §11.7.7 的 BAN-345~BAN-348 基础上追加）:

| BAN | 规则 | 检测方式 |
|-----|------|---------|
| **BAN-349** | **禁止 38 仓中任何一仓构建失败**——38 仓独立 `git clone + cmake + ctest` 必须全部通过 | CI 全仓矩阵构建 |
| **BAN-350** | **禁止跨平台编译降级**——三平台（Linux/macOS/Windows）必须全部通过，禁止"先 Linux，1.0.1 再补其他平台" | CI 三平台矩阵 |

---

## 第三十七章：生产就绪工程规范（PROD-01~PROD-06，v26.0 v4.0 新增）

> **章节定位**: 本章对应详细任务清单第八部分（SP32-SP37）的工程规范详尽版，定义 0.1.1 发布前的生产就绪 6 项硬门禁。一切以生产就绪为目标（IRON-8）。
>
> **目标读者**: DevOps 工程师、SRE、安全工程师、发布经理。

### 37.1 PROD-01：CI/CD 全仓流水线规范

**强制规则 PROD-01**: 38 仓全部必须配置独立 CI 流水线，伞仓必须配置递归流水线。

**38 仓 CI 矩阵**:

| 仓库类型 | CI 流水线数 | 触发条件 | 必跑步骤 |
|---------|:---------:|---------|---------|
| 伞仓 airymaxhub | 1 | push to main / PR | 递归 submodule 拉取 + 全量构建 + 全量测试 |
| 管理仓 ×4 | 4 | push to main / PR | 递归 submodule 拉取 + 子仓构建 + 子仓测试 |
| C 层叶子仓 ×7 | 7 | push to main / PR | cmake 构建 + ctest + ASan/LSan/UBSan + lizard |
| SDK 叶子仓 ×6 | 6 | push to main / PR | 语言原生测试（pytest/go test/cargo test/jest） |
| 生态叶子仓 ×5 | 5 | push to main / PR | 仓库特定测试 |
| 产品叶子仓 ×3 | 3 | push to main / PR | 产品构建（docker build / tauri build / EULA 验证） |
| 顶层仓 ×3 | 3 | push to main / PR | 文档校验 / devtools 测试 |
| **合计** | **29** | — | — |

**CI 必跑步骤**（所有仓）:
1. `cmake -B build -DCMAKE_BUILD_TYPE=Debug` 或语言原生构建
2. `cmake --build build` 或语言原生编译
3. `ctest --test-dir build --output-on-failure` 或语言原生测试
4. `clang-format --dry-run --Werror`（C 仓）/ `gofmt -l`（Go）/ `rustfmt --check`（Rust）/ `prettier --check`（TypeScript）
5. `clang-tidy`（C 仓）/ `golangci-lint`（Go）/ `clippy`（Rust）/ `eslint`（TypeScript）
6. SPDX 标签检查（C 仓）
7. 行数检查（仅 atoms/corekern，BAN-339）

### 37.2 PROD-02：SBOM 供应链安全规范

**强制规则 PROD-02**: 0.1.1 发布必须生成 SBOM（Software Bill of Materials），格式 CycloneDX v1.5，签名 Sigstore cosign。

**SBOM 生成规范**:

```bash
# 1. 生成 CycloneDX SBOM（每仓一份，伞仓聚合）
cyclonedx-bom -o sbom.json --schema-version 1.5

# 2. 38 仓 SBOM 聚合到伞仓
cd airymaxhub
for repo in agentrt sdk ecosystem products devtools docs docs-closed; do
  cyclonedx-bom -o sbom-$repo.json --schema-version 1.5
done
cyclonedx merge -o sbom-airymaxhub.json sbom-*.json

# 3. cosign 签名
cosign sign-blob --key cosign.key sbom-airymaxhub.json
# 输出 sbom-airymaxhub.json.sig + sbom-airymaxhub.json.pem

# 4. 发布到 release
gh release create v0.1.1 sbom-airymaxhub.json sbom-airymaxhub.json.sig sbom-airymaxhub.json.pem
```

**SBOM 必含字段**:
- `bomFormat`: `CycloneDX`
- `specVersion`: `1.5`
- `components`: 38 仓 + 所有第三方依赖（含版本号 + License）
- `dependencies`: 仓间依赖关系
- `metadata.tools`: 生成工具链版本
- `signatures`: cosign 签名

**供应链安全扫描**（Trivy）:
```bash
trivy fs --severity HIGH,CRITICAL --exit-code 1 .
trivy sbom sbom-airymaxhub.json --severity HIGH,CRITICAL --exit-code 1
```

### 37.3 PROD-03：跨平台二进制打包规范

**强制规则 PROD-03**: 0.1.1 必须发布三平台二进制包，格式 .tar.gz（Linux/macOS）+ .zip（Windows）。

**三平台发布矩阵**:

| 平台 | 架构 | 包格式 | 包名 | 内含 |
|------|------|--------|------|------|
| Linux | x86_64 | .tar.gz | `airymax-0.1.1-linux-x86_64.tar.gz` | `bin/`、`lib/`、`include/`、`share/` |
| Linux | aarch64 | .tar.gz | `airymax-0.1.1-linux-aarch64.tar.gz` | 同上 |
| macOS | x86_64 | .tar.gz | `airymax-0.1.1-darwin-x86_64.tar.gz` | 同上 |
| macOS | arm64 | .tar.gz | `airymax-0.1.1-darwin-arm64.tar.gz` | 同上（Apple Silicon） |
| Windows | x86_64 | .zip | `airymax-0.1.1-windows-x86_64.zip` | `bin/`、`lib/`、`include/`、`share/`（含 .dll） |

**包内必含**:
- `bin/`: 12 个 daemon 进程二进制（gateway_d、llm_d、tool_d、sched_d、market_d、monit_d、channel_d、info_d、notify_d、observe_d、hook_d、plugin_d）
- `lib/`: 共享库 + 静态库
- `include/`: C 公开 ABI 头文件（airy_ 前缀）
- `share/`: 默认配置 + 文档
- `LICENSE`、`NOTICE`、`sbom.json`、`sbom.json.sig`

**校验文件**:
- `airymax-0.1.1-linux-x86_64.tar.gz.sha256`
- `airymax-0.1.1-linux-x86_64.tar.gz.sha256.sig`（cosign 签名）

### 37.4 PROD-04：性能 Soak Test 规范

**强制规则 PROD-04**: 0.1.1 发布前必须通过 72 小时持续运行 Soak Test，禁止内存泄漏、禁止性能衰减 > 10%。

**Soak Test 矩阵**:

| 测试项 | 持续时间 | 通过标准 | 监控指标 |
|-------|---------|---------|---------|
| **atoms/corekern** | 72h | RSS 增长 < 50MB | RSS、CPU、fd 数、线程数 |
| **atoms/memory** | 72h | 分配器无碎片化 | 碎片率 < 5% |
| **atoms/taskflow** | 72h | 任务调度延迟 P99 < 10ms | 调度延迟、队列长度 |
| **daemons 全栈** | 72h | 12 daemon 全部存活 | 进程存活、心跳、内存 |
| **gateway HTTP** | 72h | QPS 无衰减 | QPS、延迟、错误率 |
| **MemoryRovol** | 72h | 卷载延迟无衰减 | 卷载延迟、内存占用 |

**Soak Test 自动化脚本**:

```bash
#!/bin/bash
# scripts/soak_test.sh - 72h 持续运行测试
DURATION=259200  # 72h = 259200s
START=$(date +%s)
END=$((START + DURATION))

while [ $(date +%s) -lt $END ]; do
  # 1. 启动 12 daemon
  for d in gateway_d llm_d tool_d sched_d market_d monit_d channel_d info_d notify_d observe_d hook_d plugin_d; do
    pgrep -x $d > /dev/null || ./$d &
  done

  # 2. 持续注入负载
  for i in $(seq 1 1000); do
    curl -s http://localhost:8080/health > /dev/null
  done

  # 3. 采集指标
  for d in gateway_d llm_d tool_d sched_d market_d monit_d channel_d info_d notify_d observe_d hook_d plugin_d; do
    echo "$(date +%Y-%m-%dT%H:%M:%S) $d RSS=$(ps -o rss= -p $(pgrep -x $d)) CPU=$(ps -o %cpu= -p $(pgrep -x $d))" >> /tmp/soak_metrics.log
  done

  sleep 60  # 每分钟采集一次
done

# 4. 检查通过标准
python3 scripts/analyze_soak.py /tmp/soak_metrics.log
# 输出: PASS / FAIL + 详细报告
```

### 37.5 PROD-05：安全审计规范

**强制规则 PROD-05**: 0.1.1 发布前必须通过完整安全审计，含静态扫描 + 渗透测试 + 第三方审计。

**安全审计矩阵**:

| 审计项 | 工具 | 通过标准 |
|-------|------|---------|
| 静态扫描 | Semgrep + CodeQL + clang-tidy security | 0 CRITICAL / 0 HIGH |
| 依赖漏洞 | Trivy + OSV-Scanner | 0 CRITICAL / 0 HIGH |
| 内存安全 | ASan + LSan + UBSan 全量测试 | 0 error |
| 密钥泄漏 | gitleaks + trufflehog | 0 leak |
| 渗透测试 | OWASP ZAP + Burp Suite | 0 CRITICAL |
| 第三方审计 | 外部安全公司 | 出具审计报告 |

**密钥安全**:
- 所有 secrets 必须使用 GitHub Actions secrets / GitLab CI variables
- 禁止硬编码 API key / token / password
- cosign 签名密钥必须使用 KMS（HSM 保护）

**许可证合规审计**:
```bash
# 1. SPDX 标签全量扫描
grep -r "SPDX-License-Identifier" --include="*.c" --include="*.h" | \
  grep -v "AGPL-3.0-or-later OR Apache-2.0" | \
  grep -v "LicenseRef-SPHARX-MemoryRovol-EULA-1.0"
# 期望: 0 行（除 memoryrovol 外必须全部双许可证）

# 2. License 文件校验
for repo in atoms commons cupolas heapstore protocols gateway daemons; do
  head -1 $repo/LICENSE | grep -q "GNU AFFERO GENERAL PUBLIC LICENSE" || echo "[FAIL] $repo"
done
head -1 products/memoryrovol/LICENSE | grep -q "SPHARX" || echo "[FAIL] memoryrovol"
```

### 37.6 PROD-06：发布验收规范

**强制规则 PROD-06**: 0.1.1 发布必须通过 149 项验收标准（ACC-FOUND01~08 + ACC-FOUND-SP01~SP12 + 其他 129 项），全部达标后方可发布。

**发布验收清单**:

| 验收类别 | 项数 | 通过标准 |
|---------|:---:|---------|
| 奠基验收 ACC-FOUND01~08 | 8 | 全部 PASS |
| 仓库拆分验收 ACC-SP01~SP12 | 12 | 全部 PASS |
| 工程规范 FOUND-01~10 | 10 | 全部 PASS |
| 仓库拆分 SPLIT-01~08 | 8 | 全部 PASS |
| 生产就绪 PROD-01~06 | 6 | 全部 PASS |
| 历史验收（架构/内核/打印/日志/许可证/标准化） | 105 | 全部 PASS |
| **合计** | **149** | **全部 PASS** |

**发布流程**:

```bash
# 1. 全量验收脚本
python3 scripts/release_checklist.py --version 0.1.1
# 输出: 149/149 PASS 或 FAIL 详情

# 2. 创建 release tag
git tag -a v0.1.1 -m "Airymax 0.1.1 - Foundation + 29-repo split + Production ready"
git push origin v0.1.1

# 3. 生成 release notes
gh release create v0.1.1 \
  --title "Airymax 0.1.1 - Foundation + 29-repo split + Production ready" \
  --notes-file DocsClosed/release-notes-0.1.1.md \
  airymax-0.1.1-linux-x86_64.tar.gz \
  airymax-0.1.1-linux-x86_64.tar.gz.sha256 \
  airymax-0.1.1-linux-x86_64.tar.gz.sha256.sig \
  airymax-0.1.1-darwin-arm64.tar.gz \
  airymax-0.1.1-windows-x86_64.zip \
  sbom-airymaxhub.json \
  sbom-airymaxhub.json.sig

# 4. 发布后验证
gh release view v0.1.1
# 期望: 7 个 assets 全部上传成功
```

### 37.7 第三十七章 BAN 规则（BAN-351~BAN-356）

**强制规则**: 新增以下 v4.0 生产就绪 BAN 规则:

| BAN | 规则 | 检测方式 |
|-----|------|---------|
| **BAN-351** | **禁止无 SBOM 发布**——0.1.1 release 必须包含 CycloneDX v1.5 SBOM + cosign 签名 | release assets 检查 |
| **BAN-352** | **禁止单平台发布**——必须三平台（Linux/macOS/Windows）全部通过 | CI 三平台矩阵 |
| **BAN-353** | **禁止 Soak Test 跳过**——72h 持续运行必须执行，禁止"先发布后补 Soak" | Soak Test 报告归档 |
| **BAN-354** | **禁止安全审计降级**——6 项安全审计必须全部通过，0 CRITICAL / 0 HIGH | 安全审计报告 |
| **BAN-355** | **禁止 149 项验收有 1 项 FAIL**——发布前必须 149/149 全部 PASS | `release_checklist.py` |
| **BAN-356** | **禁止跳过 cosign 签名**——所有二进制包 + SBOM 必须有 cosign 签名 | 签名校验脚本 |

---

## 第三十八章：AirymaxOS（agentrt-linux）工程规范（v27.0 v4.1 新增）

> **章节定位**: 本章是 AirymaxOS（agentrt-linux）的工程规范。AirymaxOS 是与 agentrt（AirymaxAgentRT）同级的**管理仓**，伞仓直属。基于 Linux 内核的发行版级别研究项目，全面采用**微内核设计思想**（参考 seL4 / Zircon / Minix3），全面参考 openEuler 模块设计、技术规格、标准和规范。0.1.1 中仅创建仓库占位，实际开发在 1.0.1。OS 详细设计文档全部在 `docs/AirymaxOS/` 模块内。

### 38.1 AirymaxOS 架构分离工程规范（IRON-9）

**强制规则**: AirymaxOS（agentrt-linux）与 AirymaxAgentRT（agentrt）必须保持架构分离，但**同源**。

| 维度 | AirymaxAgentRT（agentrt） | AirymaxOS（agentrt-linux） |
|------|---------------------------|----------------------------|
| 运行层级 | 用户态（跨 Linux/macOS/Windows） | 内核态 + 用户态（Linux 发行版） |
| 跨平台 | ✅ 三平台 | ❌ Linux only |
| 内核态 | ❌ 禁止（IRON-1~5） | ✅ 基于 Linux 内核 + 微内核化改造 |
| 设计思想 | 用户态运行时平台 | **微内核设计思想**（seL4 / Zircon / Minix3） |
| 接入方式 | 直接编译 | 同源天然适配（无适配层） |
| 版本 | 0.1.1 | 1.0.1 |
| 文档位置 | docs-closed/ | docs/AirymaxOS/ |

**IRON-9 v2 强制规则**（2026-07-07 变更）: agentrt 和 AirymaxOS **同源且部分代码共享**。三层共享模型：[SC] 共享契约层（`include/airymax/` 6 个头文件完全共享：memory_types.h / security_types.h / cognition_types.h / sched.h / ipc.h / syscalls.h；另含补充共享文件 bpf_struct_ops.h，非 [SC] 核心头文件）+ [SS] 语义同源层（API 签名同源，实现独立）+ [IND] 完全独立层。agentrt 保持跨平台用户态纯净（不依赖任何特定 OS），AirymaxOS 是完整发行版。代码共享边界：代码共享仅限于 agentrt 与 agentrt-linux 之间，与 Euler 项目仅技术参考，不共享代码。AirymaxOS 工程思想与 Euler 保持一致性（协议层 + 接入层 + 模块化 + 工具链兼容），以便未来兼容 Euler 标准。

### 38.2 AirymaxOS 微内核设计思想工程规范

**强制规则**: AirymaxOS 必须全面采用微内核设计思想。

| 微内核原则 | 来源 | AirymaxOS 落地 |
|---|---|---|
| Liedtke minimality | seL4 | airymaxos-kernel 最小化特权态代码 |
| 服务用户态化 | Minix3 | airymaxos-services 用户态系统服务 |
| 消息传递通信 | Zircon | 基于 io_uring 的高性能 IPC |
| capability-based security | seL4 + Zircon | airymaxos-security capability 系统 |
| 形式化验证 | seL4 | airymaxos-tests-linux 形式化验证框架 |

### 38.3 AirymaxOS 8 子仓工程规范（基于微内核设计思想 + openEuler 标准 + Airymax 同源）

**强制规则**: AirymaxOS 必须拆分为 8 个子仓，每个子仓明确对应 agentrt 的模块，体现"同源天然适配"。

| # | 子仓 | 中文 | 核心职责 | 同源 agentrt | 微内核思想体现 |
|---|------|------|---------|---|---|
| 1 | `airymaxos-kernel` | 极境内核 | Linux 6.6 + 微内核化改造（EEVDF + sched_ext + eBPF kfunc + io_uring + Rust 实验性） | atoms/corekern | 最小化特权态 |
| 2 | `airymaxos-services` | 极境服务 | 用户态系统服务（VFS + 网络 + 驱动 + 12 daemons + systemd） | daemons | 服务用户态化 |
| 3 | `airymaxos-security` | 极境安全 | capability + LSM + 机密计算 + 国密 | cupolas | capability security |
| 4 | `airymaxos-memory` | 极境记忆 | MemoryRovol 内核态 + CXL + PMEM + MGLRU 多代 LRU | heapstore + memoryrovol | 记忆独立服务 |
| 5 | `airymaxos-cognition` | 极境认知 | CoreLoopThree kthread + Wasm + LLM 调度 | coreloopthree + frameworks | 认知独立服务 |
| 6 | `airymaxos-cloudnative` | 极境云原生 | K8s + containerd + OCI + agentctl + 超节点 OS | gateway + sdk | 云原生模块 |
| 7 | `airymaxos-system` | 极境系统 | RPM + dnf + 配置 + shell + DevStation | commons | 发行版工具 |
| 8 | `airymaxos-tests-linux` | 极境测试 | 单元 + 集成 + 形式化验证 + Soak + 混沌 | 全模块测试 | 形式化验证 |

### 38.4 AirymaxOS 同源天然适配工程规范

**强制规则**: agentrt 全部能力在 AirymaxOS 上同源天然适配，无适配层。

| AirymaxAgentRT（用户态） | AirymaxOS（OS 化） | 同源语义 | 天然适配优势 |
|---------------------------|-------------------|----------|--------------|
| MicroCoreRT taskflow | airymaxos-kernel SCHED_AGENT | 调度语义一致 | agentrt 调度天然契合 |
| AgentsIPC 128B 消息头 | airymaxos-services io_uring IPC | IPC 协议语义一致 | 无协议转换 |
| Cupolas 用户态沙箱 | airymaxos-security capability + LSM | 安全模型一致 | 沙箱边界天然对齐 |
| MemoryRovol 用户态引擎 | airymaxos-memory 内核态 mmap | 记忆模型一致 | 记忆卷载原生支持 |
| CoreLoopThree 应用层循环 | airymaxos-cognition kthread | 认知模型一致 | 循环上下文天然契合 |
| 12 daemons 用户态进程 | airymaxos-services systemd 集成 | 服务模型一致 | OS 级守护天然适配 |
| gateway + sdk | airymaxos-cloudnative K8s+OCI | 网关语义一致 | 容器化原生支持 |

### 38.5 AirymaxOS openEuler 参考规范

**强制规则**: AirymaxOS 必须全面参考 openEuler 的技术规格、标准和规范。

| 维度 | openEuler 参考 | AirymaxOS 落地 |
|------|----------------|----------------|
| 内核 | Linux 6.6+ (openEuler 24.03 LTS) | airymaxos-kernel 基于 Linux 6.6（openEuler 24.03 LTS 内核） |
| 包管理 | RPM + dnf | airymaxos-system RPM + dnf（兼容） |
| 初始化 | systemd | airymaxos-services systemd 集成 |
| 安全 | SELinux + 国密 | airymaxos-security + 国密 |
| 测试 | mugen | airymaxos-tests-linux mugen 类框架 |
| AI 原生 | 智慧中枢 + 超节点 OS | airymaxos-cognition + cloudnative |
| 文档 | docs.openeuler.org | docs/AirymaxOS/ |

### 38.6 AirymaxOS 云原生亲和力工程规范

**强制规则**: AirymaxOS 必须具备天然云原生亲和力，对标 Ubuntu/openEuler。

| 云原生能力 | 实现规范 |
|-----------|---------|
| K8s 原生 | Agent 作为 K8s CRD，agentctl 对标 kubectl |
| 容器化 | containerd shim，OCI image 规范 |
| 服务网格 | CNI 插件，零信任网络 |
| 可观测性 | OpenTelemetry-native，eBPF 内核态观测 |
| 弹性伸缩 | GPU/NPU 池化，LLM 推理感知调度 |
| 机密计算 | TEE/SGX/SEV-SNP 支持 Agent 机密执行 |
| 超节点 OS | 参考 openEuler 超节点 OS |

### 38.7 AirymaxOS 文档位置工程规范

**强制规则**: OS 设计文档与 RT 文档物理分开。

| 文档类型 | 位置 | 强制 |
|---------|------|:---:|
| RT 设计文档 | `docs-closed/`（顶层仓） | ✅ |
| **OS 设计文档** | `docs/AirymaxOS/`（docs 顶层仓下子目录，12 个文档） | ✅ |

### 38.8 AirymaxOS 仓库地址工程规范

| 仓库 | URL |
|------|-----|
| 管理仓 | `git@atomgit.com:openairymax/agentrt-linux.git` |
| 子仓 1 | `git@atomgit.com:openairymax/airymaxos-kernel.git` |
| 子仓 2 | `git@atomgit.com:openairymax/airymaxos-services.git` |
| 子仓 3 | `git@atomgit.com:openairymax/airymaxos-security.git` |
| 子仓 4 | `git@atomgit.com:openairymax/airymaxos-memory.git` |
| 子仓 5 | `git@atomgit.com:openairymax/airymaxos-cognition.git` |
| 子仓 6 | `git@atomgit.com:openairymax/airymaxos-cloudnative.git` |
| 子仓 7 | `git@atomgit.com:openairymax/airymaxos-system.git` |
| 子仓 8 | `git@atomgit.com:openairymax/tests-linux.git` |

### 38.9 第三十八章 BAN 规则（BAN-357~BAN-361）

| 编号 | 规则 | 检测方式 |
|------|------|---------|
| BAN-357 | 禁止 0.1.1 中 agentrt-linux 仓库无 README.md 或 README 未声明 openEuler 参考规范 + 微内核设计思想 | `[OS-SCAN]` |
| BAN-358 | 禁止 OS 设计文档放置在 docs-closed/（必须放置在 docs/AirymaxOS/） | `[OS-SCAN]` |
| BAN-359 | 禁止 AirymaxOS 内核态代码污染 agentrt 用户态跨平台路径（IRON-9） | `[OS-SCAN]` + `[FOUND-SCAN]` |
| BAN-360 | 禁止 AirymaxOS 子仓名不使用 airymaxos- 前缀 | `[OS-SCAN]` |
| BAN-361 | 禁止引用 Linux 7.0 专属特性作为 Linux 6.6 原生能力（PREEMPT_LAZY / Rust 正式转正 / MGLRU 2.0 / XFS 自修复 / eBPF 签名验证 / sched_ext（Linux 6.15+）等） | `[OS-SCAN]` + Grep 全文档扫描 |

### 38.10 AirymaxOS Linux 6.6 兼容性工程规范（v4.2 新增，IRON-10 + BAN-361 + ACC-OS04）

**强制规则**: AirymaxOS 基于 Linux 6.6（openEuler 24.03 LTS 内核版本），禁止引用 Linux 7.0 专属特性作为 Linux 6.6 原生能力。

#### IRON-10：禁止引用 Linux 7.0 专属特性作为 6.6 原生能力

AirymaxOS 基于 Linux 6.6（openEuler 24.03 LTS 内核版本）。禁止在文档、代码、注释中引用 Linux 7.0 专属特性（PREEMPT_LAZY / Rust 正式转正 / MGLRU 2.0 / XFS 自修复 / eBPF 签名验证等）作为 Linux 6.6 原生能力。

**正确表述**：
- Linux 6.6（openEuler 24.03 LTS 内核）
- EEVDF 调度器（Linux 6.6 原生，替代 CFS）
- Rust 实验性支持（Linux 6.6，非"正式转正"）
- MGLRU 多代 LRU（Linux 6.6 基础版本，非"2.0"）
- sched_ext（openEuler backport，主线 6.12+）
- eBPF kfunc + dynamic pointer（Linux 6.6 原生，非"签名验证"）
- XFS 在线 fsck（Linux 6.6，非"自修复"）

**违反此规则的文档/代码必须在评审中被打回。**

#### BAN-361：禁止引用 Linux 7.0 专属特性作为 Linux 6.6 原生能力

禁止在 AirymaxOS 设计文档、源代码、注释、提交信息中引用以下 Linux 7.0 专属特性作为 Linux 6.6 原生能力：

- `PREEMPT_LAZY`（应为 `EEVDF 调度器`）
- `Rust 正式转正`（应为 `Rust 实验性支持`）
- `MGLRU 2.0`（应为 `MGLRU 多代 LRU`）
- `XFS 自修复`（应为 `XFS 在线 fsck`）
- `eBPF 签名验证`（应为 `eBPF kfunc + dynamic pointer`）
- `sched_ext（Linux 6.15+）`（应为 `sched_ext（openEuler backport，主线 6.12+）`）
- `Linux 7.0`（应为 `Linux 6.6（openEuler 24.03 LTS 内核）`）

**违反此规则的文档/代码必须在评审中被打回。**

#### ACC-OS04：Linux 6.6 内核兼容性验收标准

| 编号 | 验收标准 | 验证方法 |
|------|---------|---------|
| ACC-OS04 | Linux 6.6 内核兼容性验证（无 Linux 7.0 专属特性误引） | Grep 全文档扫描 `Linux 7.0\|PREEMPT_LAZY\|Rust 正式转正\|MGLRU 2.0\|XFS 自修复\|eBPF 签名验证`，结果为 0 |

---

## 附录C：v3.0 规范变更摘要

| 章节 | 新增规则数 | 来源 |
|------|:--------:|------|
| 第二十四章：双思考系统工程规范 | 20（DT-01~DT-20） | v3.0 穷尽审查 |
| 第二十五章：内核安全规范 | 15（KER-01~KER-15） | F1-F5 修复 |
| 第二十六章：部署工程规范 | 12（DEP-01~DEP-12） | G1/G2/G4 修复 |
| 第二十七章：行业最佳实践对照 | 8 类 40+ 项 | 2025-2026 调研 |
| 第二十八章：v3.0 新增 BAN 规则 | 34（BAN-257~BAN-290） | v3.0 全部 |
| 第二十九章：统一打印系统规范 | 18（PRT-01~PRT-18） | v24.5 二次验证 |
| 第三十章：统一日志系统规范 | 26（LOG-01~LOG-26，含 LOG-26 全功能定义） | v24.7 v3.4 全功能 |
| 第三十一章：统一打印/日志 BAN 规则 | 20（BAN-291~BAN-310） | v24.4 全部 |
| 第三十二章：开源许可证规范 | 8（LC-01~LC-08） | v24.6 v3.3 综合审计 |
| 第三十三章：微内核架构规范 | 8（ARC-01~ARC-08，方案 A 修正）+ 9 BAN（BAN-311~BAN-319） | v24.7 v3.4 方案 A |
| 第三十四章：开放标准规范 | 8（STD-01~STD-08）+ 8 BAN（BAN-320~BAN-327） | v24.7 v3.4 开放标准化 |
| **第三十五章：奠基性版本工程规范** | **10（FOUND-01~FOUND-10）+ 13 BAN（BAN-328~BAN-340）** | **v25.0 v3.5 唯一奠基版本** |
| **第三十六章：38 仓 git 拆分工程规范（v4.0 新增）** | **8（SPLIT-01~SPLIT-08）+ 3 IRON（IRON-6~8）+ 6 BAN（BAN-345~BAN-350）** | **v26.0 v4.0 38 仓拆分** |
| **第三十七章：生产就绪工程规范（v4.0 新增）** | **6（PROD-01~PROD-06）+ 6 BAN（BAN-351~BAN-356）** | **v26.0 v4.0 生产就绪** |
| **第三十八章：AirymaxOS（agentrt-linux）工程规范（v4.1 新增，v4.2 扩展）** | **10（§38.1~§38.10 工程规范）+ 2 IRON（IRON-9/IRON-10）+ 5 BAN（BAN-357~BAN-361）+ 1 ACC（ACC-OS04）** | **v27.0 v4.1 AirymaxOS 工程规范 + v28.0 v4.2 Linux 6.6 兼容性** |
| **§11.6：airy_→agentrt_ 改名规范（v4.0：airy_ 部分已废止，agentos_* 清零部分保留）** | **7 层面矩阵 + 4 BAN（BAN-341~BAN-344）** | **v26.0 v4.0 改名彻底** |
| **§11.7：38 仓 git submodule 拆分规范（v4.0 新增）** | **6（SPLIT-01~SPLIT-06 简略版）+ 4 BAN（BAN-345~BAN-348）** | **v26.0 v4.0 38 仓拆分** |
| **合计** | **189+ 项历史 + 35 项 v4.0 新增规则 = 224+ 项** | — |

> **v28.0 规范手册总计**: 38 章 + 3 附录，BAN 规则 361 项（新增 BAN-341~BAN-361 共 21 项 v4.0/v4.1/v4.2 规则，含改名 4 项 + 拆分 6 项 + 生产就绪 6 项 + AirymaxOS 5 项）。新增 IRON-6~10（5 项工程铁律）+ SPLIT-01~08（8 项 38 仓拆分工程规范）+ PROD-01~06（6 项生产就绪工程规范）+ §11.6 改名七层面矩阵 + §11.7 38 仓拆分简略版 + 第三十八章 AirymaxOS 工程规范（§38.1~§38.10，含 IRON-10 + BAN-361 + ACC-OS04 Linux 6.6 兼容性规范）。三大支柱：(1) 奠基 W01-W30（~1,620h）(2) 38 仓拆分 SP01-SP31（~572h）(3) 生产就绪 SP32-SP37（~240h）。总工时 ~3,396.5h，路线图 36 天。配套：详细任务清单 v2.2 + 技术改进方案 v4.2。0.1.1 之后直接 1.0.1，无中间过渡版本。

---

<div align="center">

**© 2025-2026 SPHARX Ltd. All Rights Reserved.**

*From data intelligence emerges*

</div>
