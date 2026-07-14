Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# Airymax 开放标准重建方案研究报告（v1.0）

> **文档定位**: OpenStandards 内部研究文档（_research_v1.0 系列）
> **版本**: 1.0（研究报告草案）
> **最后更新**: 2026-07-13
> **SPDX-License-Identifier**: CC-BY-4.0
> **作者**: OpenStandards 重建小组
> **状态**: 待标准委员会评审

***

## 0. 文档元信息与读者指南

### 0.1 文档定位

本报告是 Airymax 开放标准体系（OpenStandards，下文简称"本体系"）从 v1.1 升级到 v2.x 的**重建方案研究报告**，落盘于 `docs/OpenStandards/_research_v1.0/`，与现行 7 份主题标准（`01-` ~ `07-`）并存。报告本身不是规范条款，仅作为重建决策的事实与逻辑依据，最终迁移到 v2.x 的所有正式条款仍以 `AOS-STD-<域>-<NNN>` 编号在主标准文档中固化。

### 0.2 引用与版权声明

- 本报告对外部协议与治理模式（MCP / A2A / AG-UI / ANP / OCI / CNCF / seL4 Foundation / openEuler 等）的描述均基于公开规范与官方文档，**所有外部引用必须附 URL**，不得转述为 Airymax 自有观点。
- 报告本身以 [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) 发布，与 v2.x 计划采纳的"规范文档 CC-BY-4.0 + OWFa 1.0"双许可保持一致，便于社区引用与传播。
- 凡涉及 Airymax 自有标准条目（如 `AOS-STD-RT-001`）的引用，应回到 `docs/OpenStandards/0X-*.md` 主文档核对权威定义；本报告中的转述仅用于研究论证。

### 0.3 阅读路径建议

- **决策者**：阅读第 1、5、6、8 节，重点关注四阶段路径与关键决策点。
- **协议对接工程师**：阅读第 3、5.3、5.5 节，理解 MCP/A2A/AG-UI/ANP 与 7 域的映射。
- **治理与法务**：阅读第 4、5.1、5.2 节，理解 OWFa 1.0 与 CNCF 三级孵化机制。
- **agentrt/agentrt-linux 实现者**：阅读第 2、7 节，理解迁移路径与实现同步风险。

***

## 1. 执行摘要

### 1.1 当前 OpenStandards 现状评估（一句话）

当前 OpenStandards v1.1 已建立 8 文件 / 7 域 / 4409 行的扎实内核契约（RT/IPC/SEC/MEM/COG/SCHED/SYS），具备 L1~L4 稳定性分级与 RFC 公示流程雏形，但**完全置身于 2026 年 AI Agent 协议生态之外**，且**缺少 OCI 级专利授权与 CNCF 级孵化治理机制**，难以承担"生态繁荣"的对外承诺。

### 1.2 重建核心诉求（一句话）

在不破坏既有 7 域 L1 永久稳定契约的前提下，**补齐专利授权、对接 MCP/A2A/AG-UI/ANP 协议生态、引入 CNCF 风格三级孵化治理、与 OpenChain ISO/IEC 5230 供应链合规对齐**，使本体系从"自洽草案"演进为"可被第三方独立实现并受法律与社区双重保护的开放标准"。

### 1.3 重建方案概述（四阶段路径）

| 阶段 | 版本跃迁 | 工期 | 核心交付 | 风险等级 |
|------|---------|------|---------|---------|
| **阶段 1：专利授权补全** | 1.1 → 1.2 | ~2 周 | OWFa 1.0 专利授权 + CC-BY-4.0 规范文档双许可 + OpenChain 合规基线 | 低 |
| **阶段 2：协议对接** | 1.2 → 2.0 | ~4 周 | 新增 PROTO/INTEROP 两域，08/09 标准文档，修订 02 IPC 桥接 MCP JSON-RPC 2.0 | 中 |
| **阶段 3：治理升级** | 2.0 → 2.1 | ~6 周 | CNCF 风格 Draft→Proposed→Stable 三级孵化 + 公开 RFC + Apache-2.0 测试套件 | 中 |
| **阶段 4：生态扩展** | 2.1 → 2.2 | ~8 周 | Airymax Certified 认证体系 + OCI 标准格式对接 + seL4 风格形式化验证基线 | 高 |

四阶段合计 ~20 周（约 5 个月），最终在 2026 年底完成从 v1.1 到 v2.2 的整体跃迁。每一阶段均以可独立发布、可独立采纳为原则，不强制下游实现一次性升级。

***

## 2. 当前 OpenStandards 现状深度分析

### 2.1 文件清单与覆盖度评估

当前体系由 1 个总索引 + 7 个主题标准构成，总计 4409 行（按 `wc -l` 口径）：

| 编号 | 文件 | 主题 | 行数 | 域代号 | 标准条目数 | L1 条目占比 |
|------|------|------|------|--------|-----------|-----------|
| 总索引 | `README.md` | 总览与导航 | 250 | — | — | — |
| 01 | `01-airy-agent-runtime-standard.md` | Agent 运行时 | 610 | RT | 24 | 87.5% |
| 02 | `02-airy-ipc-protocol-standard.md` | IPC 协议 | 551 | IPC | 23 | 78.3% |
| 03 | `03-airy-security-model-standard.md` | 安全模型 | 622 | SEC | 27 | 81.5% |
| 04 | `04-airy-memory-rovol-standard.md` | 记忆卷载 | 617 | MEM | 21 | 100% |
| 05 | `05-airy-cognition-loop-standard.md` | 认知循环 | 543 | COG | 16 | 87.5% |
| 06 | `06-airy-scheduling-standard.md` | 调度 | 549 | SCHED | 31 | 77.4% |
| 07 | `07-airy-syscall-standard.md` | 系统调用 | 667 | SYS | 32 | 81.3% |
| **合计** | **8 文件** | **7 域** | **4409** | — | **174** | **~84.5%** |

**覆盖度评估结论**：

1. **运行时内核契约扎实**：生命周期状态机（AOS-STD-RT-001）、IPC 128B 消息头（AOS-STD-IPC-001）、capability 64B 令牌（AOS-STD-SEC-001）、MemoryRovol L1-L4（AOS-STD-MEM-001）、CoreLoopThree 三阶段（AOS-STD-COG-001）、SCHED_EXT=7（AOS-STD-SCHED-001）、12 核心 syscall（AOS-STD-SYS-001）已构成自洽的微核心 / 微内核运行时基线。
2. **L1 永久稳定比例高**：约 84.5% 的条目声明 L1 永久稳定，意味着本体系已对社区做出强承诺，重建不得破坏既有 L1 契约。
3. **缺失维度明显**：无协议对接域、无互操作域、无治理章程、无贡献指南、无行为准则、无独立兼容性测试套件仓库。

### 2.2 治理模式成熟度评估

将当前体系与 OCI / CNCF / seL4 Foundation / openEuler 四大成熟治理模式对比：

| 维度 | OpenStandards v1.1 | OCI | CNCF | seL4 Foundation | openEuler |
|------|-------------------|-----|------|-----------------|-----------|
| **法律实体** | SPHARX Ltd.（单一公司） | Linux Foundation | Linux Foundation | LF Projects, LLC + 瑞士协会 seL4 International | OpenAtom 开放原子开源基金会 |
| **专利授权** | 无 | OWFa 1.0（Patent + Copyright） | Apache-2.0 内置专利授权 | GPL-2.0 + BSD-2-Clause（无独立 OWFa） | CLA 中含专利授权 |
| **规范文档许可** | AGPL-3.0-or-later OR Apache-2.0 | CC-BY-4.0 | CC-BY-4.0 | CC-BY-SA-4.0 | 各项目独立 |
| **参考实现许可** | AGPL-3.0-or-later OR Apache-2.0 | Apache-2.0 | Apache-2.0（多数） | GPL-2.0 / BSD-2-Clause | MulanPSL-2.0 / Apache-2.0 |
| **测试套件许可** | 文档内嵌，无独立仓库 | Apache-2.0 | Apache-2.0 | BSD-2-Clause | MulanPSL-2.0 |
| **分级孵化** | 无 | 无（单一规范集） | Sandbox→Incubation→Graduation | 无（单一 kernel 项目） | SIG 孵化机制 |
| **公开 RFC** | 30 天公示 | TOB 公开评审 | TOC 公开评审 | TSC 公开会议 | TC + SIG 公开评审 |
| **CLA 机制** | 无 | 无（OWFa 替代） | 有（DCO + CLA） | 有 | 三类 CLA（个人/企业/员工） |
| **行为准则** | 无 | LF 行为准则 | CNCF CoC | LF 行为准则 | openEuler CoC |
| **供应链合规** | 无 | 无 | CII Best Practices Badge | 无 | OpenChain ISO/IEC 5230 + ISO/IEC 18974 |
| **形式化验证** | 无（仅 AOS-STD-SYS 设计借鉴 seL4） | 无 | 无 | Isabelle/HOL（~50 万行证明） | 无 |
| **商标体系** | Certified / Compatible / Inspired（未注册） | OCI Trademark Board | CNCF 商标管理 | seL4 商标政策 | openEuler 商标 |
| **会议透明度** | 季度例会，纪要公开（承诺但未实施） | TOB 公开 | TOC 公开 | TSC 公开 | TC 公开 |

**成熟度评估结论**：当前体系处于"自洽草案"阶段，治理结构停留在 SPHARX 单一公司主导，与四大成熟模式在**专利授权、规范与实现许可分离、CLA、行为准则、供应链合规、商标注册**六个维度均存在显著差距。

### 2.3 五项关键缺失的详细分析

#### 2.3.1 缺失一：零提及 MCP/A2A/AG-UI/ANP 等 2026 AI Agent 协议

**问题**：8 份文档总计 4409 行中，`MCP`、`A2A`、`AG-UI`、`ANP`、`Model Context Protocol`、`Agent-to-Agent` 字样出现次数为 **0**。当前体系的对外通信协议（02 IPC 标准）仅定义内部 128B 消息头与 5 种 payload 类型，未提供任何与外部 Agent 生态对接的契约。

**风险**：

1. **生态孤岛化**：任何遵循 MCP 的工具服务器（filesystem、PostgreSQL、GitHub、Slack 等已存在大量参考实现）、遵循 A2A 的远程 Agent（Google、Salesforce、ServiceNow 等已部署）、遵循 AG-UI 的前端应用（CopilotKit、Microsoft Agent Framework 等已广泛采用）均无法直接接入 Airymax 生态，必须由 SPHARX 单独编写适配代码。
2. **被行业标准边缘化**：MCP 已于 2025 年 12 月捐赠给 Linux Foundation 旗下 AI Alliance，A2A 已于 2025 年 6 月捐赠给 Linux Foundation，二者已成为事实标准；本体系如不主动对接，将丧失与主流生态互操作的机会窗口。
3. **N×M 集成成本**：参考 MCP 解决的 N×M 工具集成问题，若 N=5 个 AI 客户端、M=5 个外部系统，本体系需自研 25 套集成代码，而对接 MCP 后仅需 5 套 MCP Server。

**严重等级**：高。这是触发本次重建的直接原因。

#### 2.3.2 缺失二：无 OWFa 1.0 专利授权

**问题**：当前体系仅有 AGPL-3.0-or-later + Apache-2.0 双许可证，二者均包含**有限的**专利授权条款（Apache-2.0 第 3 条），但缺少独立的专利不主张承诺（Patent Non-Assert Promise）。任何第三方在实现本标准时，仍面临被 SPHARX 或其他贡献者以专利侵权起诉的法律风险。

**对比**：OCI 标准的成熟做法是采用 [OWFa 1.0](https://www.openwebfoundation.org/the-agreements/the-owf-1-0-agreements-granted-claims/owfa-1-0-patent-only)（Open Web Foundation Final Specification Agreement），其核心机制为：

- **Patent Non-Assert Promise**：贡献者以个人名义不可撤销地承诺不对其 Granted Claims 主张专利侵权，针对 Permitted Uses 范围内的实现者。
- **Patent License Commitment**：在 Non-Assert 之外，额外授予免版税、非歧视的专利许可。
- **Defensive Termination**：若被授权方主动起诉贡献者专利侵权，则其获得的承诺终止（防御性条款）。
- **Bankruptcy Protection**：参考美国破产法第 365(n) 条，确保贡献者破产时承诺仍可保留。

**风险**：

1. **企业采纳阻力**：大型企业在采纳开放标准前，法务部门通常要求明确的专利授权条款。缺少 OWFa 级承诺将使企业级采纳被合规审查卡住。
2. **贡献者风险**：未来若有第三方贡献者贡献包含其专利的标准条款，缺少 OWFa 将导致后续贡献者的专利主张权属不清。
3. **与 OCI 治理不对齐**：本体系若希望未来被 Linux Foundation 或类似中立组织托管，OWFa 是基本门槛。

**严重等级**：高。这是法律层面的根本性缺失。

#### 2.3.3 缺失三：无 OpenChain ISO/IEC 5230 认证

**问题**：当前体系没有任何供应链合规认证。参考 [ISO/IEC 5230:2020](https://www.iso.org/standard/81039.html)（OpenChain License Compliance）与 [ISO/IEC 18974:2023](https://www.iso.org/standard/86450.html)（OpenChain Security Assurance），成熟开源项目均已建立供应链合规体系，每项标准要求 25 项验证材料（合计 50 项）。

**对比**：openEuler 作为 OpenAtom 基金会托管项目，已完整采纳 OpenChain ISO/IEC 5230，其社区贡献攻略明确要求签署三类 CLA（个人 / 企业 / 员工），并通过 SIG 组机制管理 100+ 兴趣小组。

**风险**：

1. **供应链不透明**：第三方实现本标准时，无法验证其所用开源组件的许可证合规性。
2. **SBOM 缺失**：当前体系未要求实现者提供 Software Bill of Materials，与 EU Cyber Resilience Act、NTIA SBOM 最低要素等 2026 年合规要求不符。
3. **企业采购障碍**：政府与大型企业采购 AI Agent 平台时，OpenChain 认证已成为常见的预筛选条件。

**严重等级**：中。影响中长期生态扩展，但不阻塞短期重建。

#### 2.3.4 缺失四：与 CNCF/seL4 Foundation 等成熟治理模式不对齐

**问题**：当前体系缺少分级孵化机制（参考 CNCF Sandbox→Incubation→Graduation），缺少技术监督委员会（参考 OCI TOB / CNCF TOC / seL4 TSC），缺少形式化验证基线（参考 seL4 Foundation 的 Isabelle/HOL 证明）。

**对比**：

- **CNCF 三级孵化**：Sandbox（实验性，15-20% 三年内归档）→ Incubation（3+ 组织生产部署，commiter 多样性，安全审计）→ Graduated（多组织 maintainer、第三方安全审计、超多数 TOC 投票，仅 4% 项目达到）。详见 [CNCF Project Lifecycle](https://contribute.cncf.io/projects/lifecycle/)。
- **seL4 Foundation**：以 GPL-2.0（kernel）+ BSD-2-Clause（userland）+ CC-BY-SA-4.0（docs）三段式许可，配合 Isabelle/HOL 形式化证明（约 50 万行），建立"功能正确性 + 完整性 + 机密性"三大定理。详见 [seL4 Licensing](https://www.sel4.org/Legal/license.html)。
- **OCI 治理**：三层结构——Trademark Board（商标管理）、Technical Leadership（技术领导）、Technical Oversight Board（技术监督委员会）。详见 [OCI FAQ](https://opencontainers.org/faq/)。

**风险**：

1. **无项目分级**：本体系内的标准条目无"实验→稳定→毕业"的生命周期管理，新提案与已稳定条目混在一起，社区无法判断哪些可放心采纳。
2. **无形式化验证基线**：03 安全模型标准与 07 系统调用标准明确声明"借鉴 seL4"，但缺少任何形式化验证实践，无法支撑"高保证"宣传。
3. **决策机制单一**：当前所有决策由 SPHARX 标准委员会裁决，缺少社区代表投票机制。

**严重等级**：中。影响社区信任度与长期可持续性。

#### 2.3.5 缺失五：许可证分离原则缺失

**问题**：当前体系所有文档与配套测试套件统一采用 AGPL-3.0-or-later OR Apache-2.0 双许可证，未区分规范文档、参考实现、测试套件、示例代码的许可差异。

**对比**：OCI 标准做法为——

| 产物 | 许可证 | 理由 |
|------|--------|------|
| 规范文档 | CC-BY-4.0 | 鼓励最广泛引用与传播 |
| 参考实现 | Apache-2.0 | 允许商业闭源派生 |
| 测试套件 | Apache-2.0 | 鼓励社区贡献测试用例 |
| 示例代码 | MIT 或 Apache-2.0 | 允许直接复制到商业项目 |

seL4 Foundation 的做法更细致——kernel 用 GPL-2.0（强 copyleft 保障回馈）、userland 用 BSD-2-Clause（宽松允许商业）、文档用 CC-BY-SA-4.0（copyleft 保护文档衍生）。

**风险**：

1. **AGPL 网络服务条款过严**：将规范文档以 AGPL 发布会限制企业引用与转述，与"开放标准鼓励最广泛采纳"的初衷相悖。
2. **测试套件被闭源风险**：当前测试用例内嵌于标准文档，第三方实现者无法在不接受 AGPL 的情况下贡献新用例。
3. **示例代码被污染**：示例代码以 AGPL 发布意味着用户复制示例代码后必须开源整个应用，严重阻碍采纳。

**严重等级**：中。可通过阶段 1 快速修复。

***

## 3. 2026 AI Agent 协议生态分析

### 3.1 五大协议的最新状态（2026 年）

#### 3.1.1 MCP（Model Context Protocol）

| 属性 | 值 |
|------|---|
| **创建方** | Anthropic（2024 年 11 月） |
| **当前治理** | Linux Foundation AI Alliance（2025 年 12 月捐赠） |
| **当前规范版本** | 2025-11-25（最新稳定版） |
| **下一版本** | 2026-07-28 Release Candidate（2026 年 7 月 28 日正式发布） |
| **协议格式** | JSON-RPC 2.0 |
| **架构** | Host-Client-Server（借鉴 LSP） |
| **传输** | stdio + Streamable HTTP（取代 HTTP+SSE） |
| **认证** | OAuth 2.1 with PKCE（远程服务器） |
| **核心原语** | Resources（数据）、Tools（函数）、Prompts（模板） |
| **客户端能力** | Elicitation（向用户索取信息） |
| **2026-07-28 主要变更** | 协议层无状态化、Extensions 一等公民、Tasks 与 MCP Apps 转正、授权硬化、形式化弃用政策 |
| **官方规范 URL** | https://modelcontextprotocol.io/specification/latest/index |
| **官方博客 URL** | https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/ |

**关键认知**：MCP 锚定"上下文接入层"，定义 LLM 周围的可插拔生态环境，而非 LLM 内部推理逻辑。这与本体系的 02 IPC 标准（Agent 间通信）在层次上互补——MCP 是 Agent↔Tool，本体系 IPC 是 Agent↔Agent。

#### 3.1.2 A2A（Agent-to-Agent Protocol）

| 属性 | 值 |
|------|---|
| **创建方** | Google（2025 年 4 月） |
| **当前治理** | Linux Foundation（2025 年 6 月捐赠） |
| **当前规范版本** | 1.0.0（已发布稳定版） |
| **历史版本** | 0.1.0 / 0.2.5 / 0.2.6 / 0.3.0 |
| **协议格式** | JSON-RPC 2.0 over HTTPS + SSE 流式 |
| **三层架构** | Data Model / Operations / Protocol Bindings（JSON-RPC / gRPC / HTTP-REST） |
| **核心数据对象** | Task、Message、AgentCard、Part、Artifact、Extension |
| **核心操作** | Send Message / Send Streaming Message / Get Task / List Tasks / Cancel Task / Get Agent Card |
| **设计原则** | Simple、Enterprise Ready、Async First、Modality Agnostic、Opaque Execution |
| **许可证** | Apache-2.0 |
| **官方规范 URL** | https://a2a-protocol.org/v1.0.0/specification |
| **GitHub 仓库** | https://github.com/a2aproject/A2A |

**关键认知**：A2A 是"Agent 互联网时代的 HTTP"，定义不透明 Agent 之间的任务委托与能力发现。AgentCard（位于 `/.well-known/agent.json`）是其服务发现机制。与本体系的 01 运行时标准（Agent 元数据）和 02 IPC 标准（Agent 间通信）存在直接的功能映射关系。

#### 3.1.3 AG-UI（Agent-User Interaction Protocol）

| 属性 | 值 |
|------|---|
| **创建方** | CopilotKit 团队 + 多家 Agent 框架合作伙伴 |
| **治理** | 开放标准（社区驱动） |
| **协议格式** | 事件驱动，16 种标准化事件类型 |
| **传输** | SSE / WebSocket / Webhook（传输无关） |
| **核心事件** | RUN_STARTED / RUN_FINISHED / RUN_ERROR / STEP_STARTED / STEP_FINISHED / TEXT_MESSAGE_START / TEXT_MESSAGE_CONTENT / TEXT_MESSAGE_END / TOOL_CALL_START / TOOL_CALL_ARGS / TOOL_CALL_END / TOOL_CALL_RESULT / CUSTOM 等 |
| **支持的 7 大特性** | Agentic Chat / Backend Tool Rendering / Human in the Loop / Agentic Generative UI / Tool-based Generative UI / Shared State / Predictive State Updates |
| **官方文档 URL** | https://docs.ag-ui.com/introduction |
| **官网 URL** | https://ag-ui.com/ |
| **Microsoft 集成** | https://learn.microsoft.com/agent-framework/integrations/ag-ui/ |

**关键认知**：AG-UI 锚定"Agent↔用户"交互层，是连接 CopilotKit、Microsoft Agent Framework、LangChain、Mastra、CrewAI、Pydantic AI 等前后端的统一协议。与本体系的 05 认知循环标准（CoreLoopThree 三阶段）存在天然映射——AG-UI 的 RUN/STEP 事件可直接对应 PERCEPTION/THINKING/ACTION 三阶段。

#### 3.1.4 ANP（Agent Network Protocol）

| 属性 | 值 |
|------|---|
| **创建方** | Gaowei Chang（常高伟，2024 年） |
| **治理** | 开放社区 |
| **许可证** | MIT |
| **身份层** | W3C DID + 自定义 did:wba（Web-Based Agent）方法 |
| **三层架构** | 身份与加密通信层 / 元协议层 / 应用协议层 |
| **设计原则** | AI 原生设计、兼容与复用、可组合性、简单可扩展、基于现有基础设施可实施性、最小信任原则 |
| **核心特性** | 去中心化身份、跨平台认证、Agent 描述发现、自然语言元协议协商 |
| **官方白皮书 URL** | https://www.agent-network-protocol.com/zh/specs/white-paper.html |
| **DID:WBA 规范 URL** | https://agentnetworkprotocol.com/en/specs/03-did-wba-method-specification/ |

**关键认知**：ANP 锚定"开放互联网 Agent 互联"，与 A2A（企业内 Agent 协作）形成互补。其 did:wba 方法基于 W3C DID 规范，将 Agent 身份文档托管在自有域名下，实现无区块链的去中心化身份。与本体系的 03 安全模型标准（Cupolas capability）存在身份与权限模型的映射关系。

#### 3.1.5 OSI / OSINT（Open Source Intelligence）

| 属性 | 值 |
|------|---|
| **领域定位** | 情报学科（非单一协议规范） |
| **2026 年进展** | 美国 FY27 NDAA 修正案将 OSI（Open source intelligence Layer for Integration）正式立法化，授权 1000 万美元用于陆军 OSINT/PAI/CAI 整合 |
| **生态状态** | 工具碎片化（PhoneInfoga、OSINT Framework、NEXUS OSINT 等），无统一协议 |
| **与 AI Agent 关系** | OSINT 工具正通过 MCP Server 化接入 Agent 生态（如 ai-dataset-radar 0.1.1 已提供 MCP Server 集成） |
| **参考资料 URL** | https://amendments-rules.house.gov/amendments/2026.06.16%20FY27%20NDAA%20Amendment%20on%20OSINT260617132543401.pdf |

**关键认知**：OSINT 不是一个独立的 AI Agent 协议，而是一类情报数据源。其与本体系的对接路径是通过 MCP Server 包装 OSINT 工具，由 Agent 通过 MCP 协议消费情报数据。**本报告建议将 OSI 不作为独立标准域处理，仅在 08 协议对接标准中作为 MCP Server 用例之一提及**。

### 3.2 协议生态与本体系 7 域的对应关系

| 本体系域 | MCP 对应 | A2A 对应 | AG-UI 对应 | ANP 对应 | 对接策略 |
|---------|---------|---------|-----------|---------|---------|
| **RT（运行时）** | Host / Client | Client / Server | Runtime | Agent Identity | 桥接（AgentCard ↔ 元数据） |
| **IPC（进程间通信）** | JSON-RPC 2.0 消息层 | JSON-RPC 2.0 over HTTPS | SSE 事件流 | HTTP + DID 签名 | 适配层（128B 头 ↔ JSON-RPC） |
| **SEC（安全模型）** | OAuth 2.1 + PKCE | HTTPS + OAuth 2.1 | Transport-agnostic | DID + capability | 桥接（capability ↔ OAuth token） |
| **MEM（记忆卷载）** | Resources | Task State | Shared State | Agent Description | 适配层（L1-L4 ↔ Resources） |
| **COG（认知循环）** | Tools / Prompts | Task lifecycle | RUN / STEP 事件 | Meta-Protocol | 原生映射（CoreLoopThree ↔ RUN） |
| **SCHED（调度）** | （无直接对应） | Async Task | Run lifecycle | （无直接对应） | 独立保留 |
| **SYS（系统调用）** | （无直接对应） | （无直接对应） | （无直接对应） | （无直接对应） | 独立保留 |

**关键观察**：

1. **MCP 主要影响 IPC / SEC / MEM / COG 四域**，其 JSON-RPC 2.0 与本体系 02 IPC 标准的 REQUEST/RESPONSE payload 类型天然对齐。
2. **A2A 主要影响 RT / IPC / SEC 三域**，其 AgentCard 与本体系 01 元数据 JSON Schema 可双向映射。
3. **AG-UI 主要影响 COG / RT 两域**，其 16 事件类型与本体系 05 CoreLoopThree 三阶段存在原生映射。
4. **ANP 主要影响 SEC / RT 两域**，其 did:wba 方法可补充本体系 03 capability 模型缺少的身份层。
5. **SCHED 与 SYS 两域基本独立**，因为外部协议不涉及内核调度与系统调用层面。

### 3.3 对接策略建议

基于上述映射，建议采用**三层对接策略**：

1. **原生支持（Native）**：对于与本体系契约天然对齐的部分，直接采用对方协议作为本体系的对外接口。例如：

   - AG-UI 的 RUN_STARTED / STEP_STARTED 事件直接对应 CoreLoopThree 的 PERCEPTION / THINKING / ACTION 阶段，可在 05 标准附录中定义"AG-UI 事件 ↔ CoreLoopThree 阶段"原生映射。
   - A2A 的 AgentCard 与 01 元数据 JSON Schema 的字段可建立 1:1 映射，01 标准可直接引用 A2A AgentCard 作为对外发布格式。

2. **桥接层（Bridge）**：对于协议格式不同但语义对齐的部分，提供桥接层转换。例如：

   - 02 IPC 标准的 128B 消息头与 MCP JSON-RPC 2.0 消息格式不同，但 REQUEST/RESPONSE payload 语义对齐。在 02 标准附录中定义"AgentsIPC ↔ MCP JSON-RPC"桥接规范。
   - 03 capability 令牌与 OAuth 2.1 access token 在权限模型上等价，定义"capability ↔ OAuth token"双向转换接口。

3. **适配层（Adapter）**：对于深度集成的部分，提供独立的适配层标准。例如：

   - 新增 `08-airy-agent-protocol-standard.md`（PROTO 域），定义本体系如何对接 MCP（工具接入）、A2A（Agent 协作）。
   - 新增 `09-airy-agent-interop-standard.md`（INTEROP 域），定义本体系如何对接 AG-UI（用户交互）、ANP（去中心化身份）。

***

## 4. 成熟开放标准治理模式研究

### 4.1 OCI OWFa 1.0 专利授权模式

#### 4.1.1 OCI 治理结构

OCI（Open Container Initiative）由 Docker、CoreOS 等于 2015 年 6 月 22 日在 Linux Foundation 框架下成立，目标是建立容器格式与运行时的开放标准。其治理结构包含三层：

| 层 | 名称 | 职责 |
|----|------|------|
| 1 | Trademark Board（TB） | 商标管理、品牌保护 |
| 2 | Technical Leadership（TDC） | 项目贡献者与维护者，负责日常技术决策 |
| 3 | Technical Oversight Board（TOB） | 中立监督委员会，提供仲裁与战略 oversight |

OCI 维护三个核心规范：runtime-spec（v1.2）、image-spec（v1.1）、distribution-spec（v1.1）。

参考链接：

- OCI 概览：https://opencontainers.org/about/overview/
- OCI FAQ：https://opencontainers.org/faq/

#### 4.1.2 OWFa 1.0 核心机制

OCI 规范采用 [OWFa 1.0](https://www.openwebfoundation.org/the-agreements/the-owf-1-0-agreements-granted-claims)（Open Web Foundation Final Specification Agreement）作为专利授权机制，包含两个变体：

- **OWFa 1.0 - Patent & Copyright**：同时授权专利与版权。
- **OWFa 1.0 - Patent Only**：仅授权专利（版权另由 CC-BY-4.0 处理）。

核心条款：

| 条款 | 内容 |
|------|------|
| §2.1 Patent Non-Assert | 贡献者以个人名义不可撤销地承诺不对其 Granted Claims 主张专利侵权 |
| §2.2 Patent License Commitment | 在 Non-Assert 之外，额外授予免版税、非歧视的专利许可 |
| §2.1.2.1 Defensive Termination | 若被授权方主动起诉贡献者专利侵权，则其获得的承诺终止 |
| §2.1.4 Bankruptcy | 参考美国破产法第 365(n) 条，确保贡献者破产时承诺仍可保留 |
| §3 No Other Rights | 明确不授予商标、版权等其他权利（避免默示授权） |
| §4 Antitrust Compliance | 承认参与者可能竞争，无义务实现规范，可开发竞争技术 |
| §5 Non-Circumvention | 禁止故意规避协议义务 |
| §6 Representations & Warranties | 规范"按原样"提供，不承担任何担保 |

参考链接：

- OWFa 1.0 Patent Only：https://www.openwebfoundation.org/the-agreements/the-owf-1-0-agreements-granted-claims/owfa-1-0-patent-only
- OWF CLA 1.0 & OWFa 1.0 FAQ：https://www.openwebfoundation.org/faqs/open-web-foundation-cla-1-0-owfa-1-0-faq

#### 4.1.3 OCI 许可证分离实践

OCI 严格区分规范文档与参考实现的许可证：

| 产物 | 许可证 | SPDX 标识 |
|------|--------|----------|
| 规范文档 | Creative Commons Attribution 4.0 | CC-BY-4.0 |
| 参考实现（runc 等） | Apache License 2.0 | Apache-2.0 |
| 测试套件 | Apache License 2.0 | Apache-2.0 |

这种分离确保：

- 规范文档可被任何方自由引用、转述、翻译（CC-BY-4.0 要求署名）。
- 参考实现允许商业闭源派生（Apache-2.0 不强制 copyleft）。
- 测试套件允许社区贡献（Apache-2.0 + OWFa 1.0 双重保护）。

### 4.2 CNCF 三级孵化机制

#### 4.2.1 三级成熟度模型

CNCF（Cloud Native Computing Foundation）采用四级项目生命周期（含归档）：

| 级别 | 定位 | 准入门槛 | 维持要求 | 归档率 |
|------|------|---------|---------|--------|
| **Sandbox** | 实验性项目，创新探索 | 与云原生原则对齐 + 增长潜力 | 公开路线图 + 基础贡献指南 | 15-20%（3 年内） |
| **Incubation** | 生产就绪候选 | 3+ 组织生产部署 + committer 多样性 + 文档化治理 + 安全审计 | 持续采纳增长 + 稳定 API | 5-8% |
| **Graduated** | 企业级稳定 | 大规模生产部署 + 多组织 maintainer + 第三方安全审计 + 超多数 TOC 投票 | 持续运营 + 社区自维持 | <1% |
| **Archived** | 不再活跃或推荐 | TOC 决议 | — | — |

参考链接：

- CNCF Project Lifecycle：https://contribute.cncf.io/projects/lifecycle/
- CNCF Project Metrics：https://www.cncf.io/project-metrics/
- CNCF Graduation Criteria：https://github.com/cncf/toc/blob/main/process/graduation_criteria.md

#### 4.2.2 CNCF 治理核心要求

CNCF 项目升级到 Graduated 需满足以下核心要求：

1. **Code of Conduct**：采纳 [CNCF Code of Conduct](https://github.com/cncf/foundation/blob/master/code-of-conduct.md)。
2. **CII Best Practices Badge**：取得并维持 [Core Infrastructure Initiative Best Practices Badge](https://bestpractices.coreinfrastructure.org/)。
3. **Adoption Documentation**：公开采纳者列表（含终端用户，不仅是供应商）。
4. **Committer Diversity**：单一供应商贡献占比不超过 50%。
5. **Security Audit**：由第三方安全公司完成审计，并公开报告。
6. **Governance Documentation**：清晰的贡献指南、安全政策、决策流程。
7. **TOC Supermajority Vote**：Graduated 升级需超多数（通常 2/3）TOC 投票通过。

#### 4.2.3 对 OpenStandards 的借鉴

本体系不适合直接照搬 CNCF 三级孵化（因为本体系是标准规范而非软件项目），但其核心理念可移植：

| CNCF 概念 | OpenStandards 借鉴方案 |
|----------|----------------------|
| Sandbox | Draft（草案）：RFC 已提交但未通过评审的标准条目 |
| Incubation | Proposed（提案）：通过评审但未达稳定的标准条目 |
| Graduated | Stable（稳定）：通过完整公示期 + 兼容性测试验证的标准条目 |
| Archived | Deprecated（弃用）：进入弃用流程的标准条目 |
| TOC | 标准委员会（重组后） |
| CII Badge | OpenChain ISO/IEC 5230 自认证 |
| CoC | 新增 CODE_OF_CONDUCT.md |

### 4.3 seL4 Foundation 微内核标准治理

#### 4.3.1 seL4 Foundation 双重法律实体

seL4 Foundation 采用独特的双重法律实体结构：

- **LF Projects, LLC**（美国）：作为 Linux Foundation 框架下的"seL4 Project a Series of LF Projects, LLC"，处理美国法律事务。
- **seL4 International**（瑞士协会）：作为瑞士法律实体，处理欧洲事务，符合 EU Cyber Resilience Act 与 EU AI Act 的管辖要求。

参考链接：

- seL4 Foundation 概览：https://sel4.systems/Foundation/
- seL4 Foundation Technical Charter：https://sel4.systems/Foundation/Governance/seL4_Foundation_Technical_Charter.pdf

#### 4.3.2 seL4 三段式许可证

seL4 采用精细的三段式许可证（参考 [seL4 Licensing](https://www.sel4.org/Legal/license.html)）：

| 产物 | 许可证 | SPDX 标识 | 设计意图 |
|------|--------|----------|---------|
| seL4 kernel 本身 | GPL Version 2 | GPL-2.0-only | 强 copyleft 保障内核改动回馈 |
| seL4 proofs | GPL Version 2 | GPL-2.0-only | 同上 |
| 用户代码与证明库 | BSD 2-Clause | BSD-2-Clause | 宽松允许商业闭源 |
| Foundation 框架 | BSD 2-Clause | BSD-2-Clause | 宽松允许商业闭源 |
| 文档 | CC BY-SA-4.0 | CC-BY-SA-4.0 | copyleft 保护文档衍生 |

关键设计：**GPL propagation 在 kernel/user boundary 停止**（参考 Linux syscall note），用户态代码可任意许可。这使 seL4 既保持内核开源，又允许商业闭源 OS 构建于其上。

#### 4.3.3 seL4 形式化验证基线

seL4 是全球首个完整形式化验证的操作系统内核，使用 Isabelle/HOL 证明助手，证明代码约 50 万行，建立三大定理：

1. **Functional Correctness**：C 实现精化了抽象功能规范。
2. **Integrity（Spatial Isolation）**：主体只能读写其持有 capability 的内存与内核对象。
3. **Confidentiality（Information-Flow Security）**：高安全主体无法通过任何内核操作序列向低安全主体泄露信息（互不干扰）。

参考链接：

- seL4 官网：https://www.sel4.org/
- seL4 部署到欧洲的 2026 分析：https://www.sota.io/blog/deploy-sel4-europe-eu-hosting

#### 4.3.4 对 OpenStandards 的借鉴

本体系 03 安全模型与 07 系统调用明确借鉴 seL4 的 capability 模型与 syscall 设计，但缺少形式化验证。建议在阶段 4 引入：

| seL4 概念 | OpenStandards 借鉴方案 |
|----------|----------------------|
| Isabelle/HOL 证明 | 选择性形式化 AOS-STD-SEC-008~011（mint/mintcopy/derive/revoke 权限约束） |
| Three Theorems | 建立 capability 派生权限不增、revoke 递归性两大不变式证明 |
| 三段式许可 | 借鉴 seL4 的 kernel/user 边界许可分离思路，区分 agentrt 内核与用户态许可 |
| 双重法律实体 | 长期考虑（阶段 4 之后） |

### 4.4 openEuler OpenChain 认证

#### 4.4.1 openEuler 社区治理

openEuler 由 OpenAtom 开放原子开源基金会孵化及运营，采用 SIG（Special Interest Group）组织模式：

- **三类 CLA**：个人 CLA / 企业 CLA / 员工 CLA，覆盖不同参与身份。
- **100+ SIG 组**：按技术领域组织，任何人均可参与。
- **Technical Committee**：技术决策机构。
- **行为准则**：明确的 [Code of Conduct](https://atomgit.com/openeuler/community/blob/master/code-of-conduct.md)。
- **开发行为规范**：[openEuler 社区开发行为规范](https://atomgit.com/openeuler/community/blob/master/zh/technical-committee/governance/openEuler%E7%A4%BE%E5%8C%BA%E5%BC%80%E5%8F%91%E8%A1%8C%E4%B8%BA%E8%A7%84%E8%8C%83.md)。

参考链接：

- openEuler 贡献攻略：https://www.openeuler.org/zh/community/contribution/detail.html
- openEuler 社区组织：https://www.openeuler.org/zh/community/organization/

#### 4.4.2 OpenChain ISO/IEC 5230 与 ISO/IEC 18974

OpenChain 项目维护两个国际标准：

| 标准 | 名称 | 关注点 | 验证材料数 |
|------|------|--------|-----------|
| [ISO/IEC 5230:2020](https://www.iso.org/standard/81039.html) | OpenChain License Compliance | 开源许可证合规 | 25 项 |
| [ISO/IEC 18974:2023](https://www.iso.org/standard/86450.html) | OpenChain Security Assurance | 开源安全保证 | 25 项 |

ISO/IEC 5230 的 25 项验证材料覆盖六大领域：

1. **程序基础**（§3.1）：政策、能力、意识、范围、许可证义务
2. **相关任务**（§3.2）：外部询问应对、有效资源
3. **内容审查与批准**（§3.3）：SBOM、许可证合规
4. **合规产出物**（§3.4）：产出物管理
5. **社区参与**（§3.5）：贡献政策与流程
6. **规范一致性**（§3.6）：符合性与持续期

参考链接：

- OpenChain 项目官网：https://openchainproject.org/resources/faq
- OpenChain 韩文工作组指南（详细 50 项验证材料）：https://openchain-project.github.io/OpenChain-KWG/_print/guide/opensource_for_enterprise/

#### 4.4.3 对 OpenStandards 的借鉴

| openEuler / OpenChain 概念 | OpenStandards 借鉴方案 |
|---------------------------|----------------------|
| 三类 CLA | 阶段 3 引入个人 CLA + 企业 CLA（简化版，不含员工 CLA） |
| SIG 组 | 阶段 3 按域成立 SIG：RT-SIG / IPC-SIG / SEC-SIG / MEM-SIG / COG-SIG / SCHED-SIG / SYS-SIG / PROTO-SIG / INTEROP-SIG |
| OpenChain 自认证 | 阶段 1 建立 OpenChain 合规基线，阶段 4 完成自认证 |
| SBOM 要求 | 阶段 3 要求所有参考实现提供 SPDX SBOM |
| Code of Conduct | 阶段 3 新增 CODE_OF_CONDUCT.md |

### 4.5 四大治理模式综合对比与借鉴建议

| 治理要素 | OCI | CNCF | seL4 Foundation | openEuler | OpenStandards 借鉴方案 |
|---------|-----|------|-----------------|-----------|---------------------|
| 法律实体 | Linux Foundation | Linux Foundation | LF Projects + 瑞士协会 | OpenAtom 基金会 | 短期 SPHARX 主导，长期考虑 LF 托管 |
| 专利授权 | OWFa 1.0 | Apache-2.0 内置 | GPL/BSD 内置 | CLA 内置 | **OWFa 1.0 Patent Only**（阶段 1） |
| 规范许可 | CC-BY-4.0 | CC-BY-4.0 | CC-BY-SA-4.0 | 各项目独立 | **CC-BY-4.0**（阶段 1） |
| 实现许可 | Apache-2.0 | Apache-2.0 | GPL-2.0 / BSD-2-Clause | MulanPSL-2.0 | **agentrt: AGPL-3.0-or-later / 第三方: Apache-2.0**（阶段 1） |
| 测试套件许可 | Apache-2.0 | Apache-2.0 | BSD-2-Clause | MulanPSL-2.0 | **Apache-2.0**（阶段 3） |
| 分级孵化 | 无 | Sandbox→Incubation→Graduated | 无 | SIG 孵化 | **Draft→Proposed→Stable**（阶段 3） |
| 公示期 | TOB 评审 | TOC 评审 | TSC 评审 | TC 评审 | **30→60 天**（阶段 3） |
| 形式化验证 | 无 | 无 | Isabelle/HOL | 无 | **选择性形式化 capability 派生**（阶段 4） |
| 供应链合规 | 无 | CII Badge | 无 | OpenChain ISO/IEC 5230 + 18974 | **OpenChain 自认证**（阶段 4） |
| 商标体系 | Trademark Board | CNCF 商标 | seL4 商标 | openEuler 商标 | **Airymax Certified 商标注册**（阶段 4） |
| 行为准则 | LF CoC | CNCF CoC | LF CoC | openEuler CoC | **新增 CODE_OF_CONDUCT.md**（阶段 3） |
| CLA | OWFa 替代 | DCO + CLA | CLA | 三类 CLA | **个人 CLA + 企业 CLA**（阶段 3） |

***

## 5. OpenStandards 重建方案（核心）

### 5.1 许可证分离原则

#### 5.1.1 许可证分离矩阵

重建后本体系将严格区分四类产物的许可证：

| 产物类型 | 当前许可 | 重建后许可 | SPDX 标识 | 理由 |
|---------|---------|----------|----------|------|
| **规范文档**（`*.md` 主题标准） | AGPL-3.0-or-later OR Apache-2.0 | **CC-BY-4.0 + OWFa 1.0 Patent Only** | CC-BY-4.0 | 鼓励最广泛引用，专利授权独立 |
| **参考实现 agentrt**（SPHARX 主实现） | AGPL-3.0-or-later OR Apache-2.0 | **AGPL-3.0-or-later** | AGPL-3.0-or-later | 保障网络服务场景代码回流 |
| **第三方参考实现**（如 agentrt-linux） | AGPL-3.0-or-later OR Apache-2.0 | **Apache-2.0** | Apache-2.0 | 允许商业闭源派生 |
| **兼容性测试套件**（`compatibility/`） | 内嵌文档 | **Apache-2.0** | Apache-2.0 | 鼓励社区贡献测试用例 |
| **示例代码**（`examples/`） | 内嵌文档 | **MIT** | MIT | 允许直接复制到商业项目 |
| **研究报告**（`_research_v1.0/`） | — | **CC-BY-4.0** | CC-BY-4.0 | 鼓励学术引用 |

#### 5.1.2 双许可证退役路径

当前 AGPL-3.0-or-later OR Apache-2.0 双许可证将从规范文档中退役，但保留在 agentrt 参考实现中。退役分两步：

1. **阶段 1（v1.2）**：规范文档头部 SPDX 标识从 `AGPL-3.0-or-later OR Apache-2.0` 改为 `CC-BY-4.0`，新增 OWFa 1.0 Patent Only 引用条款。
2. **阶段 2（v2.0）**：移除规范文档中对 AGPL-3.0-or-later 的所有引用，仅保留 CC-BY-4.0 + OWFa 1.0。

#### 5.1.3 OWFa 1.0 引入步骤

引入 OWFa 1.0 Patent Only 需完成以下步骤：

1. **法律审查**：由 SPHARX 法务审查 OWFa 1.0 Patent Only 全文（参考 https://www.openwebfoundation.org/the-agreements/the-owf-1-0-agreements-granted-claims/owfa-1-0-patent-only）。
2. **专利清单**：SPHARX 公开其持有的、与本体系相关的专利清单（Granted Claims）。
3. **贡献者签署**：所有现有与未来贡献者签署 OWFa 1.0 Patent Only 协议。
4. **规范文档引用**：在每份主题标准文档头部新增"本规范受 OWFa 1.0 Patent Only 保护"条款。
5. **实现者声明**：第三方实现者无需签署任何协议即可自动获得 OWFa 1.0 专利授权（这是 OWFa 的核心设计）。

### 5.2 治理结构重建

#### 5.2.1 标准委员会重组

参考 OCI TOB + CNCF TOC + seL4 TSC + openEuler TC 的混合模式，重组标准委员会：

| 角色 | 当前 | 重建后 | 借鉴来源 |
|------|------|--------|---------|
| **标准总维护者** | SPHARX 任命 1 人 | SPHARX 任命 1 人（最终裁决权） | seL4 TSC Chair |
| **主题域维护者** | 7 域各 1 人 | 9 域各 1 人（新增 PROTO、INTEROP） | CNCF TOC |
| **社区代表** | 每届 1 年，可连任 | 每届 2 年，可连任 1 届，共 3 席 | CNCF 社区代表 |
| **企业代表** | 无 | 1 席（采纳企业代表，每年轮换） | openEuler 企业 CLA |
| **法务顾问** | 无 | 1 席（列席，无投票权） | OCI TOB |
| **总计** | — | 15 席（含 1 列席） | — |

#### 5.2.2 三级孵化机制

借鉴 CNCF Sandbox→Incubation→Graduated，建立标准条目三级生命周期：

| 级别 | 等价 CNCF | 准入条件 | 公示期 | 兼容性测试要求 | 标识 |
|------|----------|---------|--------|-------------|------|
| **Draft** | Sandbox | RFC 已提交，未通过评审 | 无 | 无 | `AOS-STD-<域>-<NNN>-DRAFT` |
| **Proposed** | Incubation | 通过域维护者评审 + 至少 1 个参考实现 | 60 天 | 部分测试用例通过 | `AOS-STD-<域>-<NNN>-PROPOSED` |
| **Stable** | Graduated | 通过完整公示期 + 全套兼容性测试 + 标准委员会超多数投票 | 已完成 | 全套测试通过 | `AOS-STD-<域>-<NNN>`（无后缀） |
| **Deprecated** | Archived | 弃用提案通过 | 2 个 MINOR 版本 | 保留但标记 | `AOS-STD-<域>-<NNN>-DEPRECATED` |

#### 5.2.3 公示期延长

当前公示期为 30 天，参考 CNCF（通常 30-90 天）与 OCI TOB 评审周期，建议：

- **Draft → Proposed**：30 天（保持现状，鼓励快速迭代）。
- **Proposed → Stable**：60 天（延长一倍，确保社区有充足时间审查）。
- **Stable → Deprecated**：90 天（最长，确保下游有充足时间迁移）。

#### 5.2.4 社区参与机制

| 机制 | 当前 | 重建后 |
|------|------|--------|
| 会议纪要 | 季度例会，承诺公开但未实施 | 月度例会，纪要在 7 个工作日内公开发布到 `docs/OpenStandards/governance/minutes/` |
| RFC 公开评论 | 无 | 所有 RFC 在 GitHub Discussions 公开评论 30 天 |
| 投票记录 | 无 | 标准委员会投票记录公开（含弃权与反对意见） |
| 邮件列表 | 无 | 新增 `standards@airymax.org` 邮件列表，公开归档 |
| SIG 组 | 无 | 9 个 SIG，每个 SIG 有独立 GitHub 团队与定期会议 |

### 5.3 协议生态对接（四阶段）

#### 5.3.1 阶段 1：专利授权补全（~2 周）

**目标**：建立法律基线，使本体系规范文档可被任何第三方自由引用与实现。

**交付物**：

1. `LICENSE.md`：根目录统一许可证声明文件。
2. `PATENTS.md`：OWFa 1.0 Patent Only 引用与 SPHARX 专利清单。
3. 所有 8 份现有文档头部 SPDX 标识从 `AGPL-3.0-or-later OR Apache-2.0` 改为 `CC-BY-4.0`。
4. `NOTICE.md`：第三方版权与商标声明。
5. `OpenChain-baseline.md`：OpenChain ISO/IEC 5230 合规基线声明（自评估）。

**版本变更**：v1.1 → v1.2

**风险**：低。仅涉及法律文档，不触及技术契约。

#### 5.3.2 阶段 2：协议对接（~4 周）

**目标**：建立本体系与 MCP / A2A / AG-UI / ANP 的对接契约。

**交付物**：

1. **新增 `08-airy-agent-protocol-standard.md`**（PROTO 域）：
   - PROTO-001~010：MCP 对接规范（AgentCard ↔ 元数据、JSON-RPC ↔ IPC 128B 头、OAuth 2.1 ↔ capability）
   - PROTO-011~020：A2A 对接规范（Task ↔ Agent 生命周期、AgentCard 发布到 `/.well-known/agent.json`）
   - PROTO-021~025：OSINT 工具 MCP Server 化用例
2. **新增 `09-airy-agent-interop-standard.md`**（INTEROP 域）：
   - INTEROP-001~010：AG-UI 对接规范（16 事件 ↔ CoreLoopThree 三阶段、Shared State ↔ MemoryRovol L1）
   - INTEROP-011~020：ANP 对接规范（did:wba ↔ capability owner、元协议协商）
3. **修订 `02-airy-ipc-protocol-standard.md`**：
   - 新增第十四章"MCP JSON-RPC 2.0 桥接"
   - 新增 AOS-STD-IPC-024~030：MCP 桥接条目
4. **修订 `01-airy-agent-runtime-standard.md`**：
   - 新增第十二章"A2A AgentCard 对外发布"
   - 新增 AOS-STD-RT-025~028：A2A 桥接条目

**版本变更**：v1.2 → v2.0（MAJOR 升级，因新增 2 个域）

**风险**：中。新增域不破坏既有 L1 契约，但需要 agentrt 与 agentrt-linux 同步实现桥接层。

#### 5.3.3 阶段 3：治理升级（~6 周）

**目标**：建立 CNCF 风格三级孵化治理机制。

**交付物**：

1. **新增 `GOVERNANCE.md`**：治理章程，定义标准委员会组成、三级孵化机制、投票规则、公示期。
2. **新增 `CONTRIBUTING.md`**：贡献指南，包括 DCO（Developer Certificate of Origin）签名要求、CLA 签署流程、SIG 参与方式。
3. **新增 `CODE_OF_CONDUCT.md`**：行为准则（参考 Contributor Covenant 2.1）。
4. **新增 `compatibility/` 目录**：独立兼容性测试套件仓库（Apache-2.0），包含 9 域测试用例。
5. **新增 `examples/` 目录**：MIT 许可的示例代码。
6. **新增 `governance/` 目录**：含 `minutes/`（会议纪要）、`rfcs/`（RFC 文档）、`votes/`（投票记录）。

**版本变更**：v2.0 → v2.1

**风险**：中。治理文档不影响技术契约，但需要 SPHARX 内部授权让渡部分决策权给社区。

#### 5.3.4 阶段 4：生态扩展（~8 周）

**目标**：建立完整的生态认证与形式化验证基线。

**交付物**：

1. **Airymax Certified 认证体系**：商标注册 + 第三方审计流程 + 认证标志使用规范。
2. **OCI 标准格式对接**：将 Agent 元数据封装为 OCI Image Manifest 兼容格式，支持 OCI Distribution Spec 推送拉取。
3. **seL4 Foundation 风格形式化验证基线**：选择性形式化 AOS-STD-SEC-008~011（capability 派生权限约束），使用 Isabelle/HOL 或 Coq 建立两大不变式证明：
   - 不变式 1：mint/derive 子权限必为父权限子集
   - 不变式 2：revoke 递归撤销所有派生令牌
4. **OpenChain ISO/IEC 5230 完整自认证**：完成 25 项验证材料，公开自认证结果。
5. **OpenChain ISO/IEC 18974 安全保证自认证**：完成 25 项安全验证材料。

**版本变更**：v2.1 → v2.2

**风险**：高。形式化验证需要专业人力投入，认证体系涉及商标法律事务。

### 5.4 文档结构重建

#### 5.4.1 文档清单对比

| 类别 | 当前（v1.1） | 重建后（v2.2） |
|------|-------------|---------------|
| 总索引 | `README.md` | `README.md`（更新） |
| 主题标准 | 7 份（01~07） | 9 份（01~09） |
| 治理文档 | 无 | `GOVERNANCE.md`、`CONTRIBUTING.md`、`CODE_OF_CONDUCT.md` |
| 许可文档 | 文档头部声明 | `LICENSE.md`、`PATENTS.md`、`NOTICE.md` |
| 测试套件 | 内嵌文档 | `compatibility/`（独立目录，9 个子目录） |
| 示例代码 | 内嵌文档 | `examples/`（独立目录） |
| 治理产出物 | 无 | `governance/minutes/`、`governance/rfcs/`、`governance/votes/` |
| 研究报告 | 无 | `_research_v1.0/`（本目录） |
| **总计** | **8 文件** | **12-15 文件 + 多目录** |

#### 5.4.2 目录结构

```
docs/OpenStandards/
├── README.md                                    # 总索引（更新）
├── 01-airy-agent-runtime-standard.md            # RT 域（修订）
├── 02-airy-ipc-protocol-standard.md             # IPC 域（修订）
├── 03-airy-security-model-standard.md           # SEC 域
├── 04-airy-memory-rovol-standard.md             # MEM 域
├── 05-airy-cognition-loop-standard.md           # COG 域
├── 06-airy-scheduling-standard.md               # SCHED 域
├── 07-airy-syscall-standard.md                  # SYS 域
├── 08-airy-agent-protocol-standard.md           # PROTO 域（新增）
├── 09-airy-agent-interop-standard.md            # INTEROP 域（新增）
├── LICENSE.md                                   # 许可证声明（新增）
├── PATENTS.md                                   # OWFa 1.0 专利授权（新增）
├── NOTICE.md                                    # 第三方声明（新增）
├── GOVERNANCE.md                                # 治理章程（新增）
├── CONTRIBUTING.md                              # 贡献指南（新增）
├── CODE_OF_CONDUCT.md                           # 行为准则（新增）
├── OpenChain-baseline.md                        # OpenChain 合规基线（新增）
├── _research_v1.0/                              # 研究报告目录
│   └── 01-open-standards-rebuild-proposal.md    # 本报告
├── compatibility/                               # 兼容性测试套件（Apache-2.0）
│   ├── rt/                                      # RT 域测试
│   ├── ipc/                                     # IPC 域测试
│   ├── sec/                                     # SEC 域测试
│   ├── mem/                                     # MEM 域测试
│   ├── cog/                                     # COG 域测试
│   ├── sched/                                   # SCHED 域测试
│   ├── sys/                                     # SYS 域测试
│   ├── proto/                                   # PROTO 域测试
│   └── interop/                                 # INTEROP 域测试
├── examples/                                    # 示例代码（MIT）
│   ├── weather-agent/                           # 天气 Agent 示例
│   ├── mcp-bridge/                              # MCP 桥接示例
│   └── a2a-agent-card/                          # A2A AgentCard 示例
└── governance/                                  # 治理产出物
    ├── minutes/                                 # 会议纪要
    ├── rfcs/                                    # RFC 文档
    └── votes/                                   # 投票记录
```

### 5.5 编号体系扩展

#### 5.5.1 新增域

| 域代号 | 全称 | 中文 | 起始条目号 | 用途 |
|--------|------|------|-----------|------|
| **PROTO** | Agent Protocol | 协议对接 | 001 | MCP / A2A 对接 |
| **INTEROP** | Agent Interoperability | 互操作 | 001 | AG-UI / ANP 互操作 |

#### 5.5.2 编号格式不变

编号格式保持 `AOS-STD-<域>-<NNN>`，新增域沿用此格式：

- `AOS-STD-PROTO-001`：MCP Host-Client-Server 架构对接
- `AOS-STD-PROTO-011`：A2A AgentCard 对外发布
- `AOS-STD-INTEROP-001`：AG-UI 事件 ↔ CoreLoopThree 阶段映射
- `AOS-STD-INTEROP-011`：ANP did:wba ↔ capability owner 映射

#### 5.5.3 完整域清单（重建后）

| 域 | 代号 | 起始条目 | 当前条目数 | 重建后条目数 |
|----|------|---------|----------|------------|
| 运行时 | RT | 001 | 24 | 28（+4 A2A 桥接） |
| IPC | IPC | 001 | 23 | 30（+7 MCP 桥接） |
| 安全 | SEC | 001 | 27 | 27 |
| 记忆 | MEM | 001 | 21 | 21 |
| 认知 | COG | 001 | 16 | 16 |
| 调度 | SCHED | 001 | 31 | 31 |
| 系统调用 | SYS | 001 | 32 | 32 |
| **协议对接** | **PROTO** | **001** | **0** | **~25** |
| **互操作** | **INTEROP** | **001** | **0** | **~20** |
| **总计** | — | — | **174** | **~230** |

***

## 6. 迁移路径

### 6.1 版本跃迁总览

| 版本 | 阶段 | 工期 | 主要变更 | 兼容性 |
|------|------|------|---------|--------|
| 1.1 → 1.2 | 阶段 1 | ~2 周 | 专利授权补全 + CC-BY-4.0 规范文档 + OpenChain 基线 | 完全向后兼容（仅法律文档变更） |
| 1.2 → 2.0 | 阶段 2 | ~4 周 | 新增 PROTO/INTEROP 两域 + 08/09 标准文档 + 修订 02/01 | 向后兼容（新增域不破坏既有契约） |
| 2.0 → 2.1 | 阶段 3 | ~6 周 | 三级孵化机制 + 治理文档 + 测试套件独立 | 向后兼容（治理文档不影响技术契约） |
| 2.1 → 2.2 | 阶段 4 | ~8 周 | Certified 认证 + OCI 对接 + 形式化验证 + OpenChain 自认证 | 向后兼容（认证与验证为可选） |

### 6.2 详细迁移计划

#### 6.2.1 v1.1 → v1.2（专利授权补全，~2 周）

| 周次 | 任务 | 负责人 | 交付物 |
|------|------|--------|--------|
| W1 | OWFa 1.0 法律审查 + SPHARX 专利清单 | 法务 + 标准总维护者 | `PATENTS.md` |
| W1 | 8 份文档头部 SPDX 标识更新 | 文档维护者 | 8 份 `.md` 头部修改 |
| W2 | `LICENSE.md` + `NOTICE.md` 编写 | 法务 | `LICENSE.md`、`NOTICE.md` |
| W2 | OpenChain 合规基线自评估 | 法务 + 工程师 | `OpenChain-baseline.md` |
| W2 | v1.2 发布公告 + 迁移指南 | 标准总维护者 | 公告 + 迁移指南 |

#### 6.2.2 v1.2 → v2.0（协议对接 + 治理升级，~10 周）

| 阶段 | 周次 | 任务 | 交付物 |
|------|------|------|--------|
| 协议对接 | W1-W2 | 08 PROTO 标准草案（MCP 部分） | `08-airy-agent-protocol-standard.md`（MCP 章节） |
| 协议对接 | W2-W3 | 08 PROTO 标准草案（A2A 部分） | `08-airy-agent-protocol-standard.md`（A2A 章节） |
| 协议对接 | W3-W4 | 09 INTEROP 标准草案（AG-UI + ANP） | `09-airy-agent-interop-standard.md` |
| 协议对接 | W4 | 修订 02 IPC 标准（MCP 桥接章节） | `02-airy-ipc-protocol-standard.md` 第 14 章 |
| 协议对接 | W4 | 修订 01 RT 标准（A2A AgentCard 章节） | `01-airy-agent-runtime-standard.md` 第 12 章 |
| 治理升级 | W5-W6 | `GOVERNANCE.md` 起草 + 标准委员会评审 | `GOVERNANCE.md` |
| 治理升级 | W6-W7 | `CONTRIBUTING.md` + `CODE_OF_CONDUCT.md` | 两份治理文档 |
| 治理升级 | W7-W8 | `compatibility/` 目录搭建 + 9 域测试用例迁移 | `compatibility/` 完整目录 |
| 治理升级 | W8-W9 | `examples/` 目录搭建 + 示例代码迁移 | `examples/` 完整目录 |
| 治理升级 | W9-W10 | 公示期 60 天 + 标准委员会投票 + v2.0 发布 | v2.0 正式发布 |

#### 6.2.3 v2.0 → v2.1（治理完善，~6 周）

| 周次 | 任务 | 交付物 |
|------|------|--------|
| W1-W2 | 9 个 SIG 组成立 + 各 SIG 首次会议 | SIG 章程 + 会议纪要 |
| W2-W3 | CLA 模板（个人 + 企业）+ DCO 流程 | CLA 模板 + DCO 配置 |
| W3-W4 | 邮件列表 `standards@airymax.org` 搭建 | 邮件列表 + 归档 |
| W4-W5 | GitHub Discussions 启用 + RFC 模板 | RFC 模板 + 流程文档 |
| W5-W6 | v2.1 发布 + 社区推广 | v2.1 正式发布 |

#### 6.2.4 v2.1 → v2.2（生态扩展，~8 周）

| 周次 | 任务 | 交付物 |
|------|------|--------|
| W1-W2 | Airymax Certified 商标注册申请 | 商标申请回执 |
| W2-W4 | OCI 标准格式对接规范 + 参考实现 | OCI 兼容 Agent 元数据格式 |
| W4-W6 | 形式化验证基线（capability 派生） | Isabelle/HOL 证明（两大不变式） |
| W6-W7 | OpenChain ISO/IEC 5230 完整自认证 | 25 项验证材料 + 自认证结果 |
| W7-W8 | OpenChain ISO/IEC 18974 安全自认证 | 25 项安全验证材料 + 自认证结果 |
| W8 | v2.2 发布 | v2.2 正式发布 |

### 6.3 与 agentrt / agentrt-linux 实现同步

OpenStandards 的重建必须与 agentrt（用户态微核心运行时）和 agentrt-linux（智能体操作系统发行版）的实现同步。同步原则：

| 标准变更类型 | agentrt 同步要求 | agentrt-linux 同步要求 |
|------------|----------------|---------------------|
| L1 条目新增 | MAJOR 版本同步 | MAJOR 版本同步 |
| L2 条目新增 | MINOR 版本同步 | MINOR 版本同步 |
| L3 条目新增 | MINOR 版本同步 | MINOR 版本同步 |
| 法律文档变更 | 不影响代码 | 不影响代码 |
| 治理文档变更 | 不影响代码 | 不影响代码 |
| PROTO/INTEROP 新增 | MAJOR 版本同步（实现桥接层） | MAJOR 版本同步（实现桥接层） |
| 兼容性测试新增 | 必须通过新测试 | 必须通过新测试 |

**关键约束**：agentrt 与 agentrt-linux 的实现进度**不得落后**于 OpenStandards 标准发布超过 1 个 MINOR 版本。若实现滞后，标准发布必须延期。

***

## 7. 风险评估

### 7.1 协议快速演进风险

**风险描述**：MCP、A2A、AG-UI、ANP 等协议在 2026 年仍处于快速演进期。MCP 2026-07-28 版本引入重大破坏性变更（无状态化、Extensions 框架），A2A 1.0.0 刚刚稳定，AG-UI 与 ANP 仍处于早期阶段。

**影响**：本体系若紧密耦合某一协议版本，可能在该协议下次破坏性升级时被迫 MAJOR 升级。

**缓解措施**：

1. **版本协商机制**：所有 PROTO/INTEROP 标准条目必须包含 `version` 字段，支持多版本共存。
2. **抽象层隔离**：PROTO/INTEROP 标准定义本体系的抽象接口，对外协议的具体版本通过适配层转换，避免直接耦合。
3. **年度回顾**：每年 Q1 对所有外部协议版本进行回顾，评估是否需要 MAJOR 升级。
4. **L3 稳定级**：PROTO/INTEROP 域的大部分条目标记为 L3（版本协商），允许在不触发 MAJOR 升级的情况下演进。

**风险等级**：中。

### 7.2 专利授权法律风险

**风险描述**：引入 OWFa 1.0 专利授权可能面临以下法律风险：

1. **SPHARX 自有专利暴露**：签署 OWFa 1.0 后，SPHARX 持有的与本标准相关的专利将自动授权给所有实现者，无法再通过专利诉讼维权。
2. **贡献者专利纠纷**：第三方贡献者贡献的条款若包含其专利，OWFa 1.0 将自动授权该专利，但贡献者可能未声明其专利，导致后续纠纷。
3. **跨境法律差异**：OWFa 1.0 主要依据美国法律，在欧洲、中国等司法管辖区可能存在解释差异。

**缓解措施**：

1. **专利清单公开**：SPHARX 在 `PATENTS.md` 中公开所有相关专利清单，明确 Granted Claims 范围。
2. **贡献者声明**：所有贡献者在提交 PR 时必须签署 DCO（Developer Certificate of Origin），声明其对贡献内容的版权与专利权属。
3. **法务审查**：所有 PROTO/INTEROP 新增条目在 Proposed 阶段必须经过 SPHARX 法务审查。
4. **本地化法律意见**：在欧洲与中国市场引入本地法律意见，确保 OWFa 1.0 解释一致性。

**风险等级**：中。

### 7.3 社区接受度风险

**风险描述**：本体系重建涉及多项治理变更（CLA、行为准则、社区代表、SIG 组等），可能面临社区接受度不足的风险：

1. **现有采纳者抗拒**：已在 v1.1 基础上构建实现的第三方可能不愿意升级到 v2.x，特别是涉及 CLA 签署的变更。
2. **社区参与不足**：SIG 组、邮件列表、RFC 公开评论等机制若无足够社区参与，将流于形式。
3. **SPHARX 主导权让渡阻力**：标准委员会重组后社区代表与企业代表获得投票权，SPHARX 内部可能对让渡决策权有阻力。

**缓解措施**：

1. **向后兼容承诺**：v1.x 与 v2.x 在 L1 契约上完全兼容，现有采纳者无需立即升级。
2. **渐进式治理**：阶段 3 的治理变更分步引入，先建立文档框架，再逐步开放社区参与。
3. **SPHARX 内部对齐**：在阶段 3 启动前，SPHARX 内部完成治理让渡的决策对齐，明确哪些决策权让渡、哪些保留。
4. **社区激励**：对积极参与 SIG 组的社区成员提供公开致谢、优先采纳、Airymax Certified 折扣等激励。

**风险等级**：中。

### 7.4 实现同步风险

**风险描述**：agentrt 与 agentrt-linux 的实现进度可能落后于标准发布，导致"标准先于实现"的悬空状态：

1. **PROTO/INTEROP 桥接层实现滞后**：阶段 2 新增的 PROTO/INTEROP 域需要 agentrt 与 agentrt-linux 同步实现桥接层，若实现滞后，标准将缺乏参考实现验证。
2. **形式化验证人力不足**：阶段 4 的形式化验证需要 Isabelle/HOL 或 Coq 专业人力，SPHARX 当前可能不具备该能力。
3. **OpenChain 自认证工作量**：25 + 25 = 50 项验证材料的准备需要法务、工程、运营多角色协作，可能拖延工期。

**缓解措施**：

1. **实现先行原则**：PROTO/INTEROP 标准在 Proposed 阶段必须至少有 1 个参考实现（agentrt 或 agentrt-linux），否则不进入 Stable。
2. **外部合作**：与高校或研究机构合作完成形式化验证，降低 SPHARX 内部人力压力。
3. **OpenChain 渐进式自认证**：阶段 1 完成基线评估，阶段 3 完成 50% 验证材料，阶段 4 完成全部。

**风险等级**：中-高。

### 7.5 商标法律风险

**风险描述**：阶段 4 涉及 Airymax Certified 商标注册，可能面临：

1. **商标冲突**：在目标司法管辖区（中国、美国、欧盟）可能与既有商标冲突。
2. **认证体系法律合规**：认证体系可能触及反垄断法（如拒绝特定方认证可能被诉垄断）。
3. **商标使用规范**：第三方滥用 Certified / Compatible / Inspired 标识可能导致商标稀释。

**缓解措施**：

1. **商标检索**：阶段 4 启动前在目标司法管辖区完成商标检索。
2. **认证体系公开透明**：认证标准、流程、费用全部公开，避免反垄断风险。
3. **商标使用规范**：在 `GOVERNANCE.md` 中明确三种标识的使用条件与违规处理。

**风险等级**：低-中。

***

## 8. 关键决策点（需用户裁决）

以下 5 项关键决策点需用户（SPHARX 标准总维护者或授权决策人）在阶段 1 启动前明确裁决。每项决策均附推荐方案与备选方案，供决策参考。

### 8.1 决策一：是否引入 OWFa 1.0 专利授权

| 项 | 内容 |
|----|------|
| **决策问题** | 是否在阶段 1 引入 OWFa 1.0 Patent Only 作为本体系的专利授权机制？ |
| **推荐方案** | **是**，引入 OWFa 1.0 Patent Only |
| **理由** | OWFa 1.0 是 OCI 等成熟标准的标配，缺少专利授权将阻碍企业级采纳；引入后规范文档采用 CC-BY-4.0 + OWFa 1.0 双重许可，与 OCI 实践一致 |
| **备选方案 A** | 仅使用 Apache-2.0 内置专利授权（更简单，但保护力度弱于 OWFa） |
| **备选方案 B** | 不引入专利授权（保持现状，但接受企业采纳阻力） |
| **影响范围** | 阶段 1 全部交付物 |
| **决策截止** | 阶段 1 启动前 1 周 |

### 8.2 决策二：是否采纳 CNCF 三级孵化机制

| 项 | 内容 |
|----|------|
| **决策问题** | 是否在阶段 3 采纳 CNCF 风格的 Draft→Proposed→Stable 三级孵化机制？ |
| **推荐方案** | **是**，采纳三级孵化机制 |
| **理由** | 三级孵化为社区提供清晰的标准成熟度信号，降低采纳风险；与 CNCF 生态对齐便于未来可能的 LF 托管 |
| **备选方案 A** | 保留当前 L1-L4 稳定性分级，不引入孵化机制（更简单，但缺少社区成熟度信号） |
| **备选方案 B** | 仅引入 Draft / Stable 两级（折中方案） |
| **影响范围** | 阶段 3 治理文档、标准委员会投票规则、所有 174 条现有条目的重新分级 |
| **决策截止** | 阶段 2 完成时 |

### 8.3 决策三：是否新增 PROTO/INTEROP 两个域

| 项 | 内容 |
|----|------|
| **决策问题** | 是否在阶段 2 新增 PROTO（协议对接）与 INTEROP（互操作）两个域？ |
| **推荐方案** | **是**，新增两域 |
| **理由** | MCP/A2A/AG-UI/ANP 的对接契约需要独立标准文档承载，强行塞入既有 7 域会破坏语义清晰度；新增域不破坏既有 L1 契约 |
| **备选方案 A** | 仅新增 PROTO 域，将 INTEROP 内容并入 PROTO（更紧凑，但语义混淆） |
| **备选方案 B** | 不新增域，将对接内容作为既有域的附录（最小变更，但可扩展性差） |
| **影响范围** | 阶段 2 全部交付物、编号体系扩展 |
| **决策截止** | 阶段 1 完成时 |

### 8.4 决策四：是否将测试套件以 Apache-2.0 独立开源

| 项 | 内容 |
|----|------|
| **决策问题** | 是否在阶段 3 将兼容性测试套件从文档内嵌迁移到独立 `compatibility/` 目录，并以 Apache-2.0 许可证开源？ |
| **推荐方案** | **是**，独立开源 |
| **理由** | 测试套件内嵌文档阻碍社区贡献（贡献者需接受 AGPL）；独立 Apache-2.0 仓库鼓励第三方贡献测试用例，与 OCI / CNCF 实践一致 |
| **备选方案 A** | 测试套件保留在文档内，但改用 Apache-2.0 许可（折中方案） |
| **备选方案 B** | 测试套件保持 AGPL 双许可（保守方案，社区贡献门槛高） |
| **影响范围** | 阶段 3 `compatibility/` 目录搭建、所有测试用例许可证变更 |
| **决策截止** | 阶段 3 启动前 |

### 8.5 决策五：是否对标 openEuler OpenChain 认证

| 项 | 内容 |
|----|------|
| **决策问题** | 是否在阶段 4 完成 OpenChain ISO/IEC 5230 与 ISO/IEC 18974 自认证？ |
| **推荐方案** | **是**，完成自认证 |
| **理由** | OpenChain 认证已成为政府与大型企业采购的预筛选条件；自认证成本可控（50 项验证材料），收益显著 |
| **备选方案 A** | 仅完成 ISO/IEC 5230 自认证，暂不做 18974（降低工作量） |
| **备选方案 B** | 不做自认证，仅在文档中声明"参考 OpenChain 实践"（最简方案） |
| **影响范围** | 阶段 4 全部交付物、法务与工程协作工作量 |
| **决策截止** | 阶段 3 完成时 |

***

## 9. 结语

本报告基于对 8 份现有 OpenStandards 源文件的完整阅读，结合 2026 年 7 月最新的 AI Agent 协议生态（MCP / A2A / AG-UI / ANP / OSINT）与成熟开放标准治理模式（OCI / CNCF / seL4 Foundation / openEuler）的 WebSearch 研究，提出了四阶段、~20 周的重建路径。

重建的核心价值在于：

1. **法律基线补全**：通过 OWFa 1.0 专利授权与 CC-BY-4.0 规范许可分离，使本体系可被任何第三方自由实现而不承担专利诉讼风险。
2. **协议生态对接**：通过新增 PROTO/INTEROP 两域，建立与 MCP/A2A/AG-UI/ANP 的原生支持、桥接、适配三层对接策略。
3. **治理机制升级**：通过 CNCF 风格三级孵化、公开 RFC、社区代表投票，将本体系从 SPHARX 单一主导演进为社区共治。
4. **生态认证建立**：通过 Airymax Certified 商标、OCI 格式对接、seL4 风格形式化验证、OpenChain 自认证，建立完整的生态信任体系。

重建的核心理念是**"不破坏既有契约，分层叠加新能力"**——所有 L1 永久稳定条目（约 84.5%）保持不变，新增能力以独立域、独立文档、独立许可的形式叠加。这确保了 agentrt、agentrt-linux 及任何已采纳 v1.1 的第三方实现可在零迁移成本下受益于 v2.x 的法律与生态增强。

本报告作为 v2.x 重建的起点，提交标准委员会评审。评审通过后，将按四阶段路径逐步落地，每阶段交付物独立发布、独立采纳。

***

## 10. 参考文献与外部链接

### 10.1 AI Agent 协议生态

| 协议 | 资源类型 | URL |
|------|---------|-----|
| MCP | 官方规范（latest） | https://modelcontextprotocol.io/specification/latest/index |
| MCP | 2026-07-28 Release Candidate 公告 | https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/ |
| MCP | 协议架构深度分析（2026） | https://iotdigitaltwinplm.com/anthropic-model-context-protocol-mcp-architecture-2026/ |
| MCP | 完全指南（中文） | https://blog.csdn.net/2301_80720675/article/details/162671946 |
| A2A | 官方规范 v1.0.0 | https://a2a-protocol.org/v1.0.0/specification |
| A2A | GitHub 仓库 | https://github.com/a2aproject/A2A |
| A2A | 中文技术文档 | https://agent2agent.info/zh-cn/docs/ |
| A2A | 协议深度解析 | https://agentry.com/blog/a2a-protocol-explained |
| A2A+MCP | 学术分析论文 | https://arxiv.org/pdf/2505.03864v1 |
| AG-UI | CopilotKit 官方文档 | https://docs.copilotkit.ai/learn/ag-ui-protocol |
| AG-UI | 官网 | https://ag-ui.com/ |
| AG-UI | 协议规范（Mintlify） | https://mintlify.wiki/CopilotKit/CopilotKit/concepts/ag-ui-protocol |
| AG-UI | Microsoft Agent Framework 集成 | https://learn.microsoft.com/agent-framework/integrations/ag-ui/ |
| ANP | 官方白皮书（中文） | https://www.agent-network-protocol.com/zh/specs/white-paper.html |
| ANP | 入门指南 | https://agent-network-protocol.com/guide/ |
| ANP | DID:WBA 方法规范 | https://agentnetworkprotocol.com/en/specs/03-did-wba-method-specification/ |
| AIP | IETF Internet-Draft | https://www.ietf.org/archive/id/draft-singla-agent-identity-protocol-02.txt |
| 协议对比 | A2A/MCP/ANP/Pilot 综合对比 | https://pilotprotocol.network/research/comparison.pdf |
| 协议全景 | CopilotKit 协议全景图 | https://copilotkit-public-assets.s3.us-east-1.amazonaws.com/socials/agent_protocol_landscape.pdf |
| OSINT | FY27 NDAA OSI 修正案 | https://amendments-rules.house.gov/amendments/2026.06.16%20FY27%20NDAA%20Amendment%20on%20OSINT260617132543401.pdf |

### 10.2 成熟开放标准治理模式

| 治理模式 | 资源类型 | URL |
|---------|---------|-----|
| OCI | 官方概览 | https://opencontainers.org/about/overview/ |
| OCI | FAQ | https://opencontainers.org/faq/ |
| OCI | 理解 OCI（2026） | https://woojar.com/posts/oci-introduction/ |
| OWFa 1.0 | Patent Only 协议全文 | https://www.openwebfoundation.org/the-agreements/the-owf-1-0-agreements-granted-claims/owfa-1-0-patent-only |
| OWFa 1.0 | CLA & OWFa FAQ | https://www.openwebfoundation.org/faqs/open-web-foundation-cla-1-0-owfa-1-0-faq |
| CNCF | 项目生命周期 | https://contribute.cncf.io/projects/lifecycle/ |
| CNCF | 项目指标 | https://www.cncf.io/project-metrics/ |
| CNCF | 毕业标准 | https://github.com/cncf/toc/blob/main/process/graduation_criteria.md |
| CNCF | 治理模式分析（2026） | https://timderzhavets.com/blog/how-the-cncf-governance-model-shapes-production/ |
| CNCF | 成熟度模型分析 | https://timderzhavets.com/blog/cncf-project-maturity-ladder-when-to-bet-on-sandbox-vs/ |
| CNCF | 战略选择指南 | https://timderzhavets.com/blog/cncf-project-maturity-levels-strategic-selection-guide/ |
| seL4 Foundation | 技术章程 | https://sel4.systems/Foundation/Governance/seL4_Foundation_Technical_Charter.pdf |
| seL4 Foundation | 基金会概览 | https://sel4.systems/Foundation/ |
| seL4 | 许可证模型 | https://www.sel4.org/Legal/license.html |
| seL4 | 官网 | https://www.sel4.org/ |
| seL4 | 2026 欧洲部署分析 | https://www.sota.io/blog/deploy-sel4-europe-eu-hosting |
| openEuler | 贡献攻略 | https://www.openeuler.org/zh/community/contribution/detail.html |
| OpenChain | 官方 FAQ | https://openchainproject.org/resources/faq |
| OpenChain | ISO/IEC 5230 | https://www.iso.org/standard/81039.html |
| OpenChain | ISO/IEC 18974 | https://www.iso.org/standard/86450.html |
| OpenChain | 韩文工作组合规指南 | https://openchain-project.github.io/OpenChain-KWG/_print/guide/opensource_for_enterprise/ |
| OpenChain | ISO/IEC 5230 准备指南 | https://openchain-project.github.io/OpenChain-KWG/_print/guide/iso5230_guide/ |

### 10.3 通用规范与标准

| 资源 | URL |
|------|-----|
| RFC 2119（规范用词） | https://www.rfc-editor.org/rfc/rfc2119 |
| JSON-RPC 2.0 | https://www.jsonrpc.org/specification |
| JSON Schema Draft 2020-12 | https://json-schema.org/ |
| 语义化版本 | https://semver.org/ |
| SPDX 许可证列表 | https://spdx.org/licenses/ |
| Creative Commons BY 4.0 | https://creativecommons.org/licenses/by/4.0/ |
| OpenTelemetry | https://opentelemetry.io/ |
| W3C DID 规范 | https://www.w3.org/TR/did-core/ |
| Contributor Covenant 2.1 | https://www.contributor-covenant.org/version/2/1/code_of_conduct/ |
| Linux sched_ext | https://docs.kernel.org/scheduler/sched-ext.html |
| Linux io_uring | https://docs.kernel.org/filesystems/io_uring.html |
| Linux LSM 框架 | https://docs.kernel.org/admin-guide/LSM/index.html |
| Linux capabilities(7) | https://man7.org/linux/man-pages/man7/capabilities.7.html |
| seL4 系统调用模型 | https://docs.sel4.systems/projects/sel4/manual/ |
| HNSW 算法 | https://arxiv.org/abs/1603.09320 |
| Speculative Decoding | https://arxiv.org/abs/2211.17192 |
| vLLM PagedAttention | https://arxiv.org/abs/2309.06180 |

### 10.4 Airymax 内部参考

| 资源 | 路径 |
|------|------|
| OpenStandards README | `docs/OpenStandards/README.md` |
| 01 Agent 运行时标准 | `docs/OpenStandards/01-airy-agent-runtime-standard.md` |
| 02 IPC 协议标准 | `docs/OpenStandards/02-airy-ipc-protocol-standard.md` |
| 03 安全模型标准 | `docs/OpenStandards/03-airy-security-model-standard.md` |
| 04 记忆卷载标准 | `docs/OpenStandards/04-airy-memory-rovol-standard.md` |
| 05 认知循环标准 | `docs/OpenStandards/05-airy-cognition-loop-standard.md` |
| 06 调度标准 | `docs/OpenStandards/06-airy-scheduling-standard.md` |
| 07 系统调用标准 | `docs/OpenStandards/07-airy-syscall-standard.md` |
| agentrt-linux 统一术语表 | `docs/AirymaxOS/TERMINOLOGY.md` |
| agentrt-linux 工程标准手册 | `docs/AirymaxOS/50-engineering-standards/00-engineering-standards-handbook.md` |
| 五维正交 24 原则 | `docs/AirymaxOS/10-architecture/02-five-dimensional-principles.md` |
| 跨项目代码共享 | `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md` |

***

## 11. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-07-13 | 初始草案：基于 8 份 OpenStandards 源文件 + 2026 年 7 月 WebSearch 研究，提出四阶段重建路径 |

***

Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
"From data intelligence emerges."
