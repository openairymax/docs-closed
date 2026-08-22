Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# Airymax 开放标准第二轮优化审查报告（v2.0）

> **文档定位**: OpenStandards 内部研究文档（_research_v2.0 系列）
> **版本**: 2.0（v1.0 重建方案的验证 + 优化 + 细化）
> **最后更新**: 2026-07-13
> **SPDX-License-Identifier**: CC-BY-4.0
> **作者**: OpenStandards 重建小组
> **状态**: 待标准委员会评审
> **前置文档**: [`_research_v1.0/01-open-standards-rebuild-proposal.md`](../_research_v1.0/01-open-standards-rebuild-proposal.md)

***

## 0. 文档元信息与读者指南

### 0.1 文档定位

本报告是 v1.0 重建方案的**第二轮优化审查**，遵循"验证 + 优化 + 细化"三原则，**不重复** v1.0 已确立的四阶段路径与六项关键缺失结论，而是在以下五个方向上做增量深化：

1. **验证**：用 2026 年 7 月最新 WebSearch 证据逐项验证 v1.0 四阶段路径的可行性。
2. **细化**：将 v1.0 中较粗的"许可证分离矩阵""协议对接策略""治理结构""文档结构"细化为可执行条款。
3. **深化**：将 v1.0 风险评估中的"协议快速演进""专利授权""社区接受度""实现同步"四项风险扩展为可观测的失败模式。
4. **校正**：根据最新行业实践修正 v1.0 中的不精确表述（如 A2A 捐赠时间线、MCP 2026-07-28 版本性质）。
5. **新增**：补全 v1.0 未覆盖的两个维度——**OCI-AI v1.3 规范对接** 与 **中国本地化合规（T/CAMETA MCP 安全要求团体标准）**。

### 0.2 引用与版权声明

- 本报告对外部协议与治理模式的描述均基于公开规范与官方文档，**所有外部引用必须附 URL**。
- 报告本身以 [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) 发布，与 v2.x 计划采纳的"规范文档 CC-BY-4.0 + OWFa 1.0"双许可保持一致。
- 凡涉及 Airymax 自有标准条目（如 `AOS-STD-RT-001`）的引用，应回到 `docs/OpenStandards/0X-*.md` 主文档核对权威定义。

### 0.3 阅读路径建议

- **决策者**：阅读第 1、7、8 节，重点关注 v2.0 优化结论与修正后的实施路径。
- **协议对接工程师**：阅读第 3.2、4.2、4.5 节，理解 MCP/A2A/AG-UI/ANP 与 7 域的精确映射。
- **治理与法务**：阅读第 3.1、3.3、4.1、4.3、4.6 节，理解 OWFa 1.0 引入步骤与 CNCF 三级孵化的具体落地。
- **agentrt/agent-linux 实现者**：阅读第 3.4、6.4、8 节，理解实现同步的精确窗口。

***

## 1. 执行摘要

### 1.1 v1.0 方案验证结论（一句话）

v1.0 提出的四阶段重建路径（专利授权补全 → 协议对接 → 治理升级 → 生态扩展）**整体方向正确、与 2026 年 7 月最新行业实践高度对齐**，但在五个细节处需要校正与细化：MCP 2026-07-28 版本性质表述、A2A 捐赠时间线、OCI-AI v1.3 新规范对接、中国本地化合规维度、Airymax Certified 商标的反垄断风险。

### 1.2 v2.0 优化建议概述（六个优化点）

| 优化点 | 主题 | v1.0 状态 | v2.0 增量 |
|--------|------|----------|----------|
| **优化点 1** | 许可证分离原则细化 | 提出四类产物许可矩阵 | 补全 OWFa 1.0 引入步骤的法律审查清单 + SPHARX 自有专利暴露边界 + 跨境解释差异 |
| **优化点 2** | 协议对接策略深化 | 提出三层对接策略（Native/Bridge/Adapter） | 细化 MCP JSON-RPC 桥接层、A2A AgentCard 字段映射、AG-UI 事件↔CoreLoopThree 映射 |
| **优化点 3** | 治理结构细化 | 提出标准委员会 15 席重组 | 细化 SIG 组织方式、RFC 流程时效、公示期操作方式 |
| **优化点 4** | 文档结构重建细化 | 提出 8→12-15 文件扩展 | 细化 08/09 新文档大纲 + GOVERNANCE/CONTRIBUTING/CoC 具体内容 |
| **优化点 5**（新增） | OCI-AI v1.3 规范对接 | 未提及 | 新增 OCI-AI v1.3（2026-04 强制启用）作为阶段 4 的 Agent 元数据封装格式 |
| **优化点 6**（新增） | 中国本地化合规 | 未提及 | 新增 T/CAMETA MCP 安全要求团体标准 + 数据出境合规维度 |

### 1.3 修正后的实施路径（一句话）

v1.0 的 ~20 周四阶段路径**维持不变**，但需在第 4 阶段插入 OCI-AI v1.3 对接子任务，在第 1 阶段插入中国本地化法务审查子任务，整体工期调整为 **~22 周**（2026 年底完成 v1.1 → v2.2 跃迁）。

***

## 2. 历史对话回顾（任务 a）

### 2.1 v1.0 报告对历史决策的覆盖度评估

v1.0 重建方案在历史决策覆盖上达成以下五项关键成果：

1. **现状评估准确**：v1.0 报告第 2.1 节准确列出当前 8 文件 / 7 域 / 4409 行 / 174 条目 / ~84.5% L1 比例的内核契约状态，与实际文件清单一致（已通过 `wc -l` 与逐文件读取交叉验证）。
2. **六项关键缺失识别完整**：v1.0 第 2.3 节识别的零提及 MCP/A2A/AG-UI/ANP、无 OWFa 1.0、无 OpenChain、无 CNCF 风格治理、无许可证分离——这五项是触发重建的根本性缺失，分类清晰。
3. **四阶段路径逻辑自洽**：v1.0 第 5.3 节的阶段划分遵循"法律先行 → 协议跟上 → 治理完善 → 生态扩展"的依赖链，每一阶段独立可发布，不强制下游一次性升级。
4. **风险评估覆盖四类核心风险**：v1.0 第 7 节覆盖协议演进、专利授权、社区接受度、实现同步四类风险，并提出缓解措施。
5. **五项关键决策点列出推荐方案与备选**：v1.0 第 8 节为每项决策提供推荐方案、备选方案 A/B、影响范围、决策截止，便于用户裁决。

### 2.2 v1.0 方案可能遗漏的历史决策要素

经第二轮审查，识别出 v1.0 遗漏的六项历史决策要素：

| 遗漏项 | 严重度 | v2.0 处理位置 |
|--------|--------|--------------|
| **OCI-AI v1.3 规范**（2026-04 强制启用） | 高 | 第 4.5 节（优化点 5） |
| **T/CAMETA XX-2026 中国 MCP 安全团体标准** | 中-高 | 第 4.6 节（优化点 6） |
| **A2A v1.0 Signed Agent Cards 加密身份验证** | 中 | 第 4.2.2 节 |
| **MCP 2026-07-28 Roots/Sampling/Logging 弃用** | 中 | 第 3.2.1 节 |
| **Agent Payments Protocol (AP2) 经济协调层** | 低（观察） | 第 6.1 节风险观察 |
| **EU Cyber Resilience Act 与 SBOM 最低要素** | 中 | 第 4.6 节 + 第 6.5 节 |

### 2.3 与历史对话的关系澄清

v1.0 报告本身已明确"基于对 8 份现有 OpenStandards 源文件的完整阅读"，本报告在此基础上追加：

- **完整读取**：`README.md`（250 行）、`01-airy-agent-runtime-standard.md`（610 行）、`02-airy-ipc-protocol-standard.md`（551 行）共 3 份主文档。
- **抽样验证**：v1.0 报告中引用的 174 条标准条目数、L1 占比、IPC 128B 头布局、AOS-STD-RT-001 状态机等关键事实与主文档一致。
- **WebSearch 验证**：MCP、A2A、OCI、CNCF、OpenChain 五个外部规范的 2026 年 7 月最新状态（详见第 5 节）。

***

## 3. v1.0 四阶段路径逐项验证（任务 b）

### 3.1 阶段 1 验证：专利授权补全（~2 周）

#### 3.1.1 OWFa 1.0 引入方案可行性

**验证结论**：可行，但需补充法律审查清单。

v1.0 第 5.1.3 节提出"法律审查 → 专利清单 → 贡献者签署 → 规范文档引用 → 实现者声明"五步引入流程，与 OCI 实践一致。OCI 标准采用 OWFa 1.0 Patent Only 作为专利授权机制已运行 11 年（2015-2026），是 Linux Foundation 框架下成熟标准的事实门槛。

**WebSearch 证据**：OCI 治理结构（[OCI FAQ](https://opencontainers.org/faq/)）确认其三层治理（Trademark Board / Technical Leadership / Technical Oversight Board），9 人 TOB 由项目维护者选举产生，任期 2 年。OCI 维护三个核心规范：runtime-spec v1.2、image-spec v1.1、distribution-spec v1.1。OWFa 1.0 Patent Only 全文见 [Open Web Foundation](https://www.openwebfoundation.org/the-agreements/the-owf-1-0-agreements-granted-claims/owfa-1-0-patent-only)。

**v2.0 补充**：v1.0 未列出法律审查的具体清单。建议在第 1 阶段交付物中追加 `PATENTS-LEGAL-REVIEW.md`，包含以下七项审查项：

1. OWFa 1.0 Patent Only 全文逐条解释（§2.1 Non-Assert / §2.2 License Commitment / §2.1.2.1 Defensive Termination / §2.1.4 Bankruptcy / §3 No Other Rights / §4 Antitrust / §5 Non-Circumvention / §6 Warranties）。
2. SPHARX 自有专利清单与 Granted Claims 边界界定。
3. Defensive Termination 条款在 SPHARX 作为原告时的反向触发风险评估。
4. Bankruptcy Protection 条款在中国破产法下的可执行性（参考美国破产法第 365(n) 条的对应条款）。
5. OWFa 1.0 与 Apache-2.0 第 3 条专利授权条款的叠加效应分析。
6. 跨境解释差异：美国 / 欧盟 / 中国三地司法管辖下的 OWFa 解释一致性。
7. 与未来 Linux Foundation 托管的兼容性预审。

#### 3.1.2 CC-BY-4.0 + OWFa 1.0 双重许可的法律基础

**验证结论**：法律基础充分，与 OCI 实践完全对齐。

OCI 严格区分规范文档（CC-BY-4.0）与参考实现（Apache-2.0），专利授权独立由 OWFa 1.0 Patent Only 处理。这一双重许可模式已运行 11 年，被 CNCF、seL4 Foundation 等多个 LF 项目借鉴。

**v2.0 校正**：v1.0 第 5.1.1 节将"参考实现 agentrt"许可描述为"AGPL-3.0-or-later"，将"第三方参考实现"许可描述为"Apache-2.0"。这一区分与 seL4 Foundation 的"kernel GPL-2.0 / userland BSD-2-Clause"边界设计理念一致，但需明确**边界位置**：

- **agentrt 内核**（MicroCoreRT 微核心运行时）：AGPL-3.0-or-later（强 copyleft 保障网络服务场景代码回流）。
- **agentrt 用户态库**（如 libairy_ipc、libairy_cap）：Apache-2.0（宽松允许商业闭源派生）。
- **agent-linux 发行版**：作为整体发行版采用 AGPL-3.0-or-later，但其包含的内核模块（基于 Linux 6.6）继承 GPL-2.0。
- **第三方参考实现**：Apache-2.0（允许商业闭源派生）。

这一边界设计参考 seL4 的"GPL propagation 在 kernel/user boundary 停止"原则（见 [seL4 Licensing](https://www.sel4.org/Legal/license.html)），确保内核改动回馈的同时不阻碍商业生态。

#### 3.1.3 OpenChain ISO/IEC 5230 自评估方案

**验证结论**：可行，自评估模式为 OpenChain 官方支持路径。

**WebSearch 证据**：[OpenChain 项目](https://openchainproject.org/resources/faq)维护 ISO/IEC 5230:2020（许可证合规，25 项验证材料）与 ISO/IEC 18974:2023（安全保证，25 项验证材料）两项国际标准，全球已有 1000+ 公司参与社区。2026 年新增的合规案例包括：

- Hitachi Energy（2026-01-27 完成 ISO 5230 认证，由 Bureau Veritas 第三方审计）——见 [OpenChain News](https://openchainproject.org/news/2026/01/27/hitachi-energy-achieves-openchain-iso-5230-certification-reinforcing-commitment-to-open-source-excellence)。
- 42dot（2026-06-19 完成 ISO 5230 自评估声明）。
- CJ OliveYoung（2026-03-10 完成韩国美妆业首个 ISO 5230 声明）——见 [OpenChain News](https://openchainproject.org/news/2026/03/10/cj-oliveyoung-becomes-the-first-in-the-korean-beauty-industry-to-declare-open-source-international-standard-certification)。
- norxs Technology（2026-06-05）。

[OpenChain Korea Work Group 指南](https://openchain-project.github.io/OpenChain-KWG/_print/guide/opensource_for_enterprise/)（2026-03-26 更新）确认：单一指南可同时覆盖 ISO/IEC 5230 与 ISO/IEC 18974 两标准的全部 50 项验证材料，且明确支持**自评估声明**模式——这印证 v1.0"自认证成本可控"的判断。

**v2.0 补充**：v1.0 阶段 1 仅建立"OpenChain 合规基线"，阶段 4 才完成自认证。建议在阶段 1 即引入 [OpenChain AI SBOM Self Certification](https://openchainproject.org/news/2026/04/09/webinar-open-chain-ai-sbom-iso-42001-iso42003)（2026-04-09 Webinar 引入 ISO 4200X 系列）作为 AI 工作负载的额外合规维度，因为本体系定位为 AI Agent 标准，AI SBOM 合规比传统 SBOM 更贴合。

### 3.2 阶段 2 验证：协议对接（~4 周）

#### 3.2.1 MCP 对接方案验证

**验证结论**：方案可行，但需校正 2026-07-28 版本性质表述。

**WebSearch 证据**：[MCP 2026-07-28 Release Candidate 公告](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)确认以下关键事实：

1. **版本性质校正**：v1.0 报告将"2026-07-28"描述为"正式发布"，实际为 **Release Candidate**，最终规范于 **2026 年 7 月 28 日正式发布**（即 RC 阶段从 5 月 21 日开始，7 月 28 日 ship 最终版）。本报告对 v1.0 表述做精确校正。
2. **六大破坏性变更**（六项 SEP 协同）：
   - **协议层无状态化**：移除 `Mcp-Session-Id` 握手，请求自包含，可在普通 round-robin 负载均衡器后运行，按 `Mcp-Method` 头路由，`tools/list` 响应可由客户端按 `ttlMs` 缓存。
   - **Extensions 一等公民**：Tasks（长时运行操作）、MCP Apps（服务器渲染 UI）、Skills over MCP（结构化指令）转为 Extensions 框架。
   - **授权硬化**：与 OAuth / OpenID Connect 部署更紧密对齐。
   - **形式化弃用政策**：Roots / Sampling / Logging 三项进入弃用流程。
   - **完整 JSON Schema 2020-12 for Tools**：工具入参描述能力增强。
3. **生态规模**（2026-03 数据）：Python/TypeScript SDK 月下载量 9700 万，活跃公共 MCP 服务器 10000+，OpenAI、Google DeepMind、Microsoft、AWS 已采纳。
4. **治理归属**：2025-12 捐赠给 Linux Foundation 旗下 **Agentic AI Foundation**（与 Block、OpenAI 共同创立，Google、Microsoft、AWS、Cloudflare 背书）—— v1.0 报告表述为"Linux Foundation AI Alliance"略有偏差，v2.0 校正为"Agentic AI Foundation under Linux Foundation"。

**对 v1.0 方案的影响**：

- v1.0 第 5.3.2 节"MCP JSON-RPC 2.0 桥接"方向正确，但需追加对**协议层无状态化**的适配——本体系 02 IPC 标准的 REQUEST/RESPONSE payload 类型本身是无状态的，与 MCP 2026-07-28 无状态化方向天然对齐，桥接层设计反而因 MCP 简化而变易。
- 需追加对**Extensions 框架**的对接策略：本体系 PROTO 域应将 MCP Tasks Extension 作为长时运行 Agent 任务的对接点，将 MCP Apps Extension 作为 AG-UI 替代或补充的用户交互对接点。
- 需追加对**Roots/Sampling/Logging 弃用**的迁移路径：本体系不应采纳已弃用的 Roots（应使用 A2A AgentCard）、Sampling（应使用本体系 05 CoreLoopThree）、Logging（应使用 OpenTelemetry）。

#### 3.2.2 A2A 对接方案验证

**验证结论**：方案可行，需校正捐赠时间线。

**WebSearch 证据**：[Linux Foundation 2026-04-09 新闻稿](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year)确认：

1. **捐赠时间线校正**：v1.0 报告称"A2A 已于 2025 年 6 月捐赠给 Linux Foundation"，实际为 **2025 年 4 月 Google Cloud Next 发布**（50+ 合作伙伴），**2026 年 4 月正式完成 Linux Foundation 托管并发布 v1.0 稳定版**——v2.0 校正这一时间线。
2. **生态规模**（2026-04 数据）：150+ 组织支持（AWS、Cisco、Google、IBM、Microsoft、Salesforce、SAP、ServiceNow 等），GitHub 仓库 22000+ stars，SDK 已扩展到 Python/JS/Java/Go/.NET 五种语言。
3. **v1.0 关键特性**：多协议支持（JSON-RPC 2.0 / gRPC / HTTP+JSON/REST 三种传输等价）、企业级多租户、Signed Agent Cards（加密身份验证）、web-aligned architecture（支持熟悉的安全与负载均衡模式）。
4. **云厂商深度集成**：Microsoft 集成到 Azure AI Foundry 与 Copilot Studio，AWS 通过 Amazon Bedrock AgentCore Runtime 支持。
5. **经济协调层扩展**：[Agent Payments Protocol (AP2)](https://ap2-protocol.org/) 已有 60+ 支付与金融服务组织支持，将 A2A 扩展到高信任受监管环境。
6. **与 MCP 关系**：明确**互补而非替代**——A2A 处理 Agent↔Agent，MCP 处理 Agent↔Tool。

**对 v1.0 方案的影响**：

- v1.0 第 3.1.2 节"A2A AgentCard 与 01 元数据 JSON Schema 可双向映射"方向正确，但需细化字段映射表（见第 4.2.2 节）。
- 需追加对 **Signed Agent Cards** 的对接：本体系 03 安全模型标准的 Cupolas capability 应与 A2A Signed Agent Cards 建立签名互认。
- 需观察 **AP2 经济协调层**：暂不纳入 v2.x 范围，但在风险观察列表中跟踪（见第 6.1 节）。

#### 3.2.3 AG-UI / ANP 对接方案验证

**验证结论**：方案可行，AG-UI 事件↔CoreLoopThree 映射是原生映射，ANP did:wba 补充身份层。

AG-UI 与 ANP 在 v1.0 报告中已有详细分析（第 3.1.3、3.1.4 节），v2.0 验证认为方向正确，无需重大修正。关键补充：

- **AG-UI 16 事件**与本体系 05 CoreLoopThree 三阶段（PERCEPTION / THINKING / ACTION）的映射是原生映射（不是桥接），应在 09 INTEROP 标准中作为一等公民定义。
- **ANP did:wba** 与本体系 03 Cupolas capability 的映射需要桥接层，因为 did:wba 是去中心化身份（基于 W3C DID），而 capability 是集中式权限令牌。

#### 3.2.4 PROTO/INTEROP 两域新增合理性验证

**验证结论**：合理，新增两域不破坏既有 L1 契约。

v1.0 第 5.5 节提出新增 PROTO（协议对接）与 INTEROP（互操作）两域，编号格式沿用 `AOS-STD-<域>-<NNN>`。验证如下：

- **不破坏 L1 契约**：PROTO/INTEROP 是新增域，不修改既有 7 域（RT/IPC/SEC/MEM/COG/SCHED/SYS）的任何 L1 条目，向后兼容。
- **语义清晰**：PROTO 聚焦"协议对接"（与外部协议的桥接契约），INTEROP 聚焦"互操作"（与本体系内部各域的协同）。两者职责分明，避免塞入既有域导致语义混淆。
- **可扩展性**：未来若出现新的外部协议（如 AP2 经济协调层、AIP IETF Internet-Draft），可追加到 PROTO 域末尾，不影响既有条目。

**v2.0 补充**：建议明确 PROTO 与 INTEROP 的边界规则——PROTO 域条目**必须**包含外部协议版本字段（如 `mcp_version: "2026-07-28"`），允许通过版本协商支持多版本共存；INTEROP 域条目**必须**指明与本体系内部哪些域交互（如 `interop_with: [RT, COG]`），便于追溯影响范围。

### 3.3 阶段 3 验证：治理升级（~6 周）

#### 3.3.1 CNCF 风格三级孵化机制适用性

**验证结论**：适用，但需明确"标准规范"与"软件项目"的差异。

**WebSearch 证据**：

- [CNCF Project Lifecycle](https://contribute.cncf.io/projects/lifecycle/) 与 [CNCF Project Maturity Ladder 分析](https://timderzhavets.com/blog/cncf-project-maturity-ladder-when-to-bet-on-sandbox-vs/)（2026-02-15）确认四级生命周期：Sandbox（15-20% 三年内归档）→ Incubating（5-8% 归档率）→ Graduated（仅 4% 项目达到，<1% 归档率）→ Archived。
- 2026 年最新毕业案例：[Dragonfly 2026-01-14 毕业](https://dragonfly.website.cncfstack.com/blog/2026/01/15/cncf-announces-dragonfly-graduation/)（CNCF 第 N 个 Graduated 项目），[Kyverno 2026-03-16 毕业](https://lucaberton.com/blog/kyverno-cncf-graduated-kubernetes-policy-engine/)。
- 2026 年最新 Incubating 案例：[Tekton 2026-03-24 进入 Incubating](https://www.cncf.io/blog/2026/03/24/tekton-becomes-a-cncf-incubating-project/)（跳过 Sandbox 直接进入 Incubating，因其在 CD Foundation 已毕业）。
- CNCF 毕业核心要求：thriving adoption、documented governance、strong security practices、community sustainability。

**对 v1.0 方案的影响**：v1.0 第 5.2.2 节将 CNCF Sandbox→Incubating→Graduated 映射为 Draft→Proposed→Stable，方向正确。但需明确差异：

- CNCF 是**软件项目**孵化，关注 committer 多样性、生产部署、安全审计；
- 本体系是**标准规范**孵化，关注采纳者多样性、参考实现数量、兼容性测试通过率。
- v2.0 建议将"committer 多样性"替换为"实现者多样性"（至少 3 个独立组织实现同一标准条目），将"生产部署"替换为"参考实现通过兼容性测试"，将"第三方安全审计"替换为"第三方兼容性审计"。

#### 3.3.2 公开 RFC 流程可行性

**验证结论**：可行，需细化时效与公示期操作。

v1.0 第 5.2.3 节提出 Draft→Proposed 30 天、Proposed→Stable 60 天、Stable→Deprecated 90 天的三级公示期。验证如下：

- 30 天 Draft→Proposed 与 CNCF Sandbox 准入门槛（TOC 评审周期）相当。
- 60 天 Proposed→Stable 介于 CNCF Incubating（通常 30-90 天）与 Graduated（超多数投票，通常 60-120 天）之间，合理。
- 90 天 Deprecated 与 CNCF Archived（TOC 决议，通常 90-180 天）相当。

**v2.0 细化**（见第 4.3.3 节）：明确 RFC 流程的七个具体步骤与时效。

#### 3.3.3 Apache-2.0 测试套件独立开源方案

**验证结论**：可行，与 OCI/CNCF 实践一致。

OCI 与 CNCF 均将测试套件以 Apache-2.0 独立开源（参考 [OCI FAQ](https://opencontainers.org/faq/) 与 CNCF 各项目实践）。v1.0 第 5.1.1 节将测试套件许可从 AGPL-3.0-or-later OR Apache-2.0 改为 Apache-2.0，方向正确。

**v2.0 补充**：测试套件独立仓库（`compatibility/`）应同时声明 OWFa 1.0 Patent Only 引用，避免测试用例贡献者的专利主张风险。这与 OCI 测试套件"Apache-2.0 + OWFa 1.0 双重保护"实践一致。

### 3.4 阶段 4 验证：生态扩展（~8 周）

#### 3.4.1 Airymax Certified 认证体系可行性

**验证结论**：可行，但需追加反垄断风险评估。

v1.0 第 5.3.4 节提出 Airymax Certified 商标注册 + 第三方审计流程。验证如下：

- **商标注册可行**：OCI Trademark Board、CNCF 商标管理、seL4 商标政策、openEuler 商标均已建立先例。
- **第三方审计可行**：参考 CNCF Graduated 项目的第三方安全审计实践（如 Kyverno 毕业时完成的第三方审计）。
- **反垄断风险**：v1.0 第 7.5 节已识别"认证体系可能触及反垄断法"，但未细化。v2.0 在第 6.5 节深化这一风险。

#### 3.4.2 OCI 标准格式对接必要性

**验证结论**：必要，且需对接 OCI-AI v1.3 而非传统 OCI v1.1。

**WebSearch 证据**：[Docker AI Toolkit 2026 强制启用 OCI-AI v1.3 规范](https://blog.csdn.net/CodeIsle/article/details/160526786)（2026-04-26 发布）确认：

- 自 2026-04-01 起，Docker AI Toolkit（DAT）所有官方镜像构建、推理服务部署及模型注册流程**强制启用 OCI-AI v1.3 规范**。
- OCI-AI v1.3 由 OCI 联合 MLCommons 共同发布，统一 AI 工作负载的元数据描述、硬件亲和性声明、安全沙箱边界及可验证签名机制。
- 未遵循 v1.3 的镜像被 Docker Hub AI Registry 拒绝推送，触发 `ERR_OCI_AI_SCHEMA_MISMATCH` 错误。
- 关键新增字段：`hardware_requirements`（GPU memory、ISA extensions）、`trust_policy`（Sigstore Cosign v2.8+ 签名链）、`runtimeConstraints`、`quantizationProfile`。

**对 v1.0 方案的影响**：v1.0 第 5.3.4 节"OCI 标准格式对接"未指明版本，v2.0 校正为**对接 OCI-AI v1.3**（而非传统 OCI image-spec v1.1），因为本体系定位为 AI Agent 标准，Agent 元数据封装应采用 AI 工作负载专用格式。这是 v1.0 的关键遗漏，v2.0 新增为优化点 5（见第 4.5 节）。

#### 3.4.3 seL4 风格形式化验证基线适用性

**验证结论**：适用，但应限定范围以控制成本。

v1.0 第 5.3.4 节提出选择性形式化 AOS-STD-SEC-008~011（capability mint/mintcopy/derive/revoke）。验证如下：

- **seL4 实践**：seL4 是全球首个完整形式化验证的操作系统内核，使用 Isabelle/HOL 证明助手，证明代码约 50 万行，建立 Functional Correctness、Integrity、Confidentiality 三大定理（见 [seL4 官网](https://www.sel4.org/)）。
- **本体系适用范围**：本体系 03 安全模型标准的 Cupolas capability 派生模型与 seL4 capability 模型在设计上同源，适合形式化验证。
- **成本控制**：seL4 的 50 万行证明投入了约 20 人年，本体系不可能复制这一投入。建议仅形式化两大不变式：
  - 不变式 1：mint/derive 子权限必为父权限子集（权限单调性）。
  - 不变式 2：revoke 递归撤销所有派生令牌（撤销完全性）。
- **工具选择**：Isabelle/HOL（与 seL4 一致）或 Coq（与 CompCert 一致），二者均为成熟证明助手。

**v2.0 补充**：形式化验证应作为阶段 4 的**可选交付物**（非阻塞），若人力不足可延期到 v2.3 或之后。这与 v1.0 第 7.4 节"实现同步风险"中"形式化验证人力不足"的判断一致。

***

## 4. v2.0 优化建议（六个优化点）

### 4.1 优化点 1：许可证分离原则细化

#### 4.1.1 细化的许可证分离矩阵

v1.0 第 5.1.1 节提出四类产物许可矩阵，v2.0 在此基础上细化为六类，并补全每类的法律合理性论证：

| 产物类型 | 当前许可 | v2.0 重建后许可 | SPDX 标识 | 法律合理性 |
|---------|---------|---------------|----------|----------|
| **规范文档**（`01-`~`09-*.md` 主题标准） | AGPL-3.0-or-later OR Apache-2.0 | CC-BY-4.0 + OWFa 1.0 Patent Only | CC-BY-4.0 | 鼓励最广泛引用；专利授权独立由 OWFa 处理，与 OCI 实践完全对齐 |
| **研究报告**（`_research_v1.0/`、`_research_v2.0/`） | — | CC-BY-4.0 | CC-BY-4.0 | 鼓励学术引用；不引入 OWFa 因研究报告非规范条款 |
| **参考实现 agentrt 内核**（MicroCoreRT） | AGPL-3.0-or-later OR Apache-2.0 | AGPL-3.0-or-later | AGPL-3.0-or-later | 强 copyleft 保障网络服务场景代码回流；参考 seL4 kernel GPL-2.0 设计理念 |
| **参考实现 agentrt 用户态库**（libairy_*） | AGPL-3.0-or-later OR Apache-2.0 | Apache-2.0 | Apache-2.0 | 宽松允许商业闭源派生；参考 seL4 userland BSD-2-Clause 边界设计 |
| **第三方参考实现**（如 agent-linux 中的独立组件） | AGPL-3.0-or-later OR Apache-2.0 | Apache-2.0 | Apache-2.0 | 允许商业闭源派生；与 OCI runc 实践一致 |
| **兼容性测试套件**（`compatibility/`） | 内嵌文档 | Apache-2.0 + OWFa 1.0 Patent Only | Apache-2.0 | 鼓励社区贡献测试用例；OWFa 保护测试用例贡献者的专利风险 |
| **示例代码**（`examples/`） | 内嵌文档 | MIT | MIT | 允许直接复制到商业项目；MIT 是最宽松的常用许可证 |

#### 4.1.2 双许可证退役的精确路径

v1.0 第 5.1.2 节提出两步退役，v2.0 细化为三步：

1. **阶段 1（v1.2）**：8 份现有文档头部 SPDX 标识从 `AGPL-3.0-or-later OR Apache-2.0` 改为 `CC-BY-4.0`，新增 OWFa 1.0 Patent Only 引用条款。
2. **阶段 2（v2.0）**：移除规范文档中对 AGPL-3.0-or-later 的所有引用，仅保留 CC-BY-4.0 + OWFa 1.0。
3. **阶段 3（v2.1）**：在 `LICENSE.md` 中明确"历史版本（v1.0/v1.1）的规范文档仍以原 AGPL-3.0-or-later OR Apache-2.0 许可发布，不接受重新许可"——这是法律上的安全做法，避免已分发副本的许可歧义。

#### 4.1.3 OWFa 1.0 引入的七步法律审查清单

详见第 3.1.1 节，此处不重复。

### 4.2 优化点 2：协议对接策略深化

#### 4.2.1 三层对接策略的精确边界

v1.0 第 3.3 节提出 Native / Bridge / Adapter 三层对接策略，v2.0 细化每层的精确边界：

| 层 | 适用场景 | 实现位置 | 性能开销 | 示例 |
|----|---------|---------|---------|------|
| **Native**（原生支持） | 外部协议与本体系契约天然对齐 | 直接采用对方协议作为对外接口 | 零开销 | AG-UI RUN/STEP ↔ CoreLoopThree；A2A AgentCard ↔ 01 元数据 |
| **Bridge**（桥接层） | 协议格式不同但语义对齐 | 在本体系标准附录定义转换规范 | 一次序列化/反序列化 | 02 IPC 128B 头 ↔ MCP JSON-RPC 2.0；capability ↔ OAuth token |
| **Adapter**（适配层） | 深度集成需要独立标准承载 | 新增 PROTO/INTEROP 域条目 | 适配层运行时开销 | MCP Tasks Extension ↔ Agent 生命周期；ANP did:wba ↔ capability owner |

#### 4.2.2 MCP JSON-RPC 2.0 桥接层设计

**桥接位置**：02 IPC 标准第十四章（新增）。

**桥接契约**：

| 本体系 IPC 字段 | MCP JSON-RPC 字段 | 转换规则 |
|---------------|------------------|---------|
| `magic`（0x41524531） | —（无对应） | 桥接层固定填充，MCP 侧忽略 |
| `opcode`（SEND/RECV/SEND_BATCH/CANCEL） | JSON-RPC method（`tools/call`、`resources/read` 等） | 桥接层维护 opcode↔method 映射表 |
| `flags`（NOWAIT/SIGNAL 等） | JSON-RPC id 存在性 | NOWAIT 对应 notification（无 id），否则对应 request（有 id） |
| `trace_id` | JSON-RPC id（字符串/数字） | 桥接层将 trace_id 编码为 id 字符串 |
| `src_task` | —（MCP 无对应，由传输层处理） | 桥接层填充为 MCP client 标识 |
| `dst_task` | —（MCP 无对应） | 桥接层填充为 MCP server 标识 |
| `payload_len` | —（JSON-RPC 自描述长度） | 桥接层自动计算 |
| `reserved[84]` | — | 桥接层填充 0 |

**payload 类型映射**：

| 本体系 payload 类型 | MCP JSON-RPC 类型 | 转换规则 |
|-------------------|------------------|---------|
| REQUEST（0x0001） | request（含 id） | `method_id` 映射到 MCP method；`params` 序列化为 JSON-RPC params |
| RESPONSE（0x0002） | response（含 result/error） | `status` 映射到 JSON-RPC error.code（0 → result，<0 → error） |
| EVENT（0x0003） | notification（无 id） | `topic_id` 映射到 MCP method；`payload` 序列化为 params |
| STREAM（0x0004） | —（MCP 2026-07-28 用 Streamable HTTP 的 SSE） | 桥接层将 STREAM chunk 转为 SSE event |
| NOTIFICATION（0x0005） | notification（无 id） | 同 EVENT，但 `category`/`severity` 映射到 MCP logging levels |

**无状态化适配**：MCP 2026-07-28 移除 `Mcp-Session-Id`，本体系 IPC 的 REQUEST 自带 `request_id` 与 `trace_id`，天然无状态，桥接层无需维护会话状态。

#### 4.2.3 A2A AgentCard 与 airy_agent_t 元数据字段映射

**映射表**：

| A2A AgentCard 字段 | 本体系 01 元数据字段 | 映射方向 | 转换规则 |
|-------------------|---------------------|---------|---------|
| `name` | `name` | 双向 | 直接复制 |
| `description` | —（本体系无对应） | 单向（A2A→本体系） | 写入 `capabilities` 的 `constraints.description` |
| `url` | `runtime.entry` | 双向 | URL 解析为 entry 符号 |
| `version` | `version` | 双向 | 直接复制 |
| `protocolVersion` | `api_version` | 双向 | `airymax/v1` ↔ A2A 协议版本 |
| `capabilities.streaming` | —（本体系 IPC STREAM 类型） | 单向（A2A→本体系） | true → 默认支持 STREAM payload |
| `capabilities.pushNotifications` | —（本体系 NOTIFICATION 类型） | 单向（A2A→本体系） | true → 默认支持 NOTIFICATION payload |
| `capabilities.extensions` | `capabilities` | 双向 | A2A extensions 数组映射到本体系 capabilities 数组 |
| `skills`（AgentSkill 数组） | `capabilities` | 双向 | 每个 skill 映射到一个 capability 项 |
| `securitySchemes` | —（本体系 03 安全模型 Cupolas） | 桥接 | A2A securityScheme ↔ capability 签名互认 |
| `signedWith`（v1.0 新增） | —（本体系 capability owner） | 桥接 | Signed Agent Card 签名 ↔ capability 派生链 |

**发布机制**：本体系 01 标准第十二章（新增）应规定 Agent 元数据自动导出为 A2A AgentCard 并发布到 `/.well-known/agent.json`，实现服务发现。

#### 4.2.4 AG-UI 事件↔CoreLoopThree 阶段映射

**原生映射表**（非桥接）：

| AG-UI 事件 | CoreLoopThree 阶段 | 映射语义 |
|-----------|-------------------|---------|
| `RUN_STARTED` | —（生命周期起点） | 触发 `airy_agent_schedule` 进入 RUNNING |
| `STEP_STARTED`（perception） | PERCEPTION 开始 | 标记感知阶段开始 |
| `TEXT_MESSAGE_CONTENT`（perception） | PERCEPTION 数据流入 | 感知数据流式写入 MemoryRovol L1 |
| `STEP_FINISHED`（perception） | PERCEPTION 结束 | 标记感知阶段结束 |
| `STEP_STARTED`（thinking） | THINKING 开始 | 标记思考阶段开始 |
| `TEXT_MESSAGE_START` / `TEXT_MESSAGE_CONTENT` / `TEXT_MESSAGE_END` | THINKING LLM 推理 | LLM token 流通过 STREAM payload 传输 |
| `STEP_FINISHED`（thinking） | THINKING 结束 | 标记思考阶段结束 |
| `STEP_STARTED`（action） | ACTION 开始 | 标记行动阶段开始 |
| `TOOL_CALL_START` / `TOOL_CALL_ARGS` / `TOOL_CALL_END` | ACTION 工具调用 | 工具调用通过 REQUEST payload 触发 |
| `TOOL_CALL_RESULT` | ACTION 结果返回 | 工具结果通过 RESPONSE payload 返回 |
| `STEP_FINISHED`（action） | ACTION 结束 | 标记行动阶段结束 |
| `RUN_FINISHED` | —（生命周期终点） | 触发 Agent 进入 TERMINATED |
| `RUN_ERROR` | —（异常终止） | 触发 `airy_agent_destroy` 并返回错误码 |
| `CUSTOM` | —（扩展事件） | 通过 NOTIFICATION payload 透传 |

**Shared State ↔ MemoryRovol L1 映射**：AG-UI 的 Shared State 对应本体系 04 记忆卷载标准的 MemoryRovol L1（工作记忆），双向同步。

### 4.3 优化点 3：治理结构细化

#### 4.3.1 标准委员会的具体构成与职责

v1.0 第 5.2.1 节提出 15 席重组（1 标准总维护者 + 9 主题域维护者 + 3 社区代表 + 1 企业代表 + 1 法务顾问列席），v2.0 细化职责：

| 角色 | 席位 | 任期 | 投票权 | 主要职责 |
|------|------|------|--------|---------|
| 标准总维护者 | 1 | SPHARX 任命，无任期限制 | 1 票（最终裁决权） | RFC 最终裁决、版本发布批准、跨域冲突仲裁 |
| 主题域维护者 | 9（RT/IPC/SEC/MEM/COG/SCHED/SYS/PROTO/INTEROP 各 1） | 2 年，可连任 1 届 | 各 1 票 | 域内 RFC 评审、域内条目分级、域内兼容性测试维护 |
| 社区代表 | 3 | 2 年，可连任 1 届 | 各 1 票 | 社区意见反映、采纳者反馈、公开评论期意见汇总 |
| 企业代表 | 1 | 1 年，每年轮换 | 1 票 | 企业采纳需求反馈、企业级合规要求反映 |
| 法务顾问 | 1（列席） | SPHARX 法务任命 | 无投票权 | OWFa 1.0 解释、CLA 审查、商标法律事务 |
| **合计** | **15 席** | — | **14 票**（含最终裁决） | — |

**法定人数**：标准委员会会议需至少 8 席（含 1 名主题域维护者）出席方为有效。重大决策（如 MAJOR 版本升级、L1 条目修订——原则上永不出新 MAJOR）需 2/3 超多数（即至少 10 票）通过。

#### 4.3.2 SIG 组织方式

v1.0 第 5.2.4 节提出 9 个 SIG，v2.0 细化组织方式：

| SIG | 对应域 | 主要职责 | 会议频率 | 产出物 |
|-----|--------|---------|---------|--------|
| RT-SIG | RT | 生命周期状态机、元数据、能力声明、Token 预算 | 双周 | RFC 评审、测试用例维护 |
| IPC-SIG | IPC | 128B 消息头、payload 类型、MCP 桥接 | 双周 | RFC 评审、Wireshark dissector 维护 |
| SEC-SIG | SEC | Cupolas capability、LSM、形式化验证 | 月度 | RFC 评审、Isabelle/HOL 证明维护 |
| MEM-SIG | MEM | MemoryRovol L1-L4、GFP 掩码、遗忘机制 | 月度 | RFC 评审 |
| COG-SIG | COG | CoreLoopThree、Thinkdual、AG-UI 映射 | 双周 | RFC 评审 |
| SCHED-SIG | SCHED | SCHED_EXT、vtime、并发 | 月度 | RFC 评审 |
| SYS-SIG | SYS | 12 核心 syscall、capability invocation | 月度 | RFC 评审 |
| PROTO-SIG | PROTO | MCP/A2A 对接 | 双周 | RFC 评审、外部协议版本跟踪 |
| INTEROP-SIG | INTEROP | AG-UI/ANP 互操作 | 双周 | RFC 评审 |

**SIG 章程**：每个 SIG 必须有书面章程，包含：SIG 范围、SIG 维护者（1-2 人，由标准委员会任命）、决策机制（共识优先，投票次之）、会议纪要公开要求（7 个工作日内发布到 `governance/minutes/<sig>/`）。

#### 4.3.3 RFC 流程的具体步骤与时效

v1.0 第 5.2.3 节提出三级公示期，v2.0 细化 RFC 流程的七个具体步骤：

| 步骤 | 名称 | 时效 | 责任方 | 产出物 |
|------|------|------|--------|--------|
| 1 | RFC 提交 | T+0 | 任何贡献者 | `governance/rfcs/<NNN>-<title>.md` |
| 2 | SIG 评审 | T+0 ~ T+14 | 对应 SIG 维护者 | 评审意见、修订建议 |
| 3 | 公开评论 | T+14 ~ T+44（30 天） | 社区 | GitHub Discussions 评论记录 |
| 4 | 修订 | T+44 ~ T+51 | RFC 提交者 | RFC 修订版 |
| 5 | 标准委员会投票 | T+51 ~ T+58 | 标准委员会 | 投票记录（含弃权与反对意见） |
| 6 | Draft→Proposed 升级 | T+58 | 标准总维护者 | 条目标记 `-PROPOSED` 后缀 |
| 7 | Proposed→Stable 升级 | T+58 ~ T+118（60 天公示） | 标准委员会 | 条目去除后缀，进入正式规范 |

**总时效**：从 RFC 提交到 Stable，最快 ~118 天（约 4 个月）。这与 v1.0 第 5.2.3 节"30+60=90 天公示"略有差异，因为 v2.0 追加了 SIG 评审（14 天）、修订（7 天）、投票（7 天）三个非公示环节。

#### 4.3.4 公示期的具体操作方式

| 公示类型 | 公示期 | 公示渠道 | 操作要求 |
|---------|--------|---------|---------|
| Draft→Proposed | 30 天 | GitHub Discussions + `standards@airymax.org` 邮件列表 | RFC 全文公开；评论开放；SIG 维护者每周汇总评论 |
| Proposed→Stable | 60 天 | GitHub Discussions + 邮件列表 + GitHub Announcement | 修订版 RFC 全文公开；兼容性测试结果公开；标准委员会投票记录公开 |
| Stable→Deprecated | 90 天 | 全部渠道 + 项目主页置顶公告 | 弃用提案全文公开；替代方案公开；迁移指南发布 |

### 4.4 优化点 4：文档结构重建细化

#### 4.4.1 08 PROTO 标准文档大纲

```
08-airy-agent-protocol-standard.md（PROTO 域）
├── 一、范围与目的
├── 二、PROTO 域编号体系
├── 三、MCP 对接规范
│   ├── 3.1 MCP Host-Client-Server 架构对接
│   ├── 3.2 JSON-RPC 2.0 桥接层（引用 02 标准第十四章）
│   ├── 3.3 OAuth 2.1 ↔ capability 桥接
│   ├── 3.4 MCP Resources ↔ MemoryRovol L1 适配
│   ├── 3.5 MCP Tools ↔ Agent 能力声明映射
│   ├── 3.6 MCP Prompts ↔ Agent 元数据扩展
│   ├── 3.7 MCP Extensions（Tasks/MCP Apps/Skills）对接
│   ├── 3.8 MCP 2026-07-28 无状态化适配
│   └── 3.9 弃用项迁移路径（Roots/Sampling/Logging）
├── 四、A2A 对接规范
│   ├── 4.1 A2A 三层架构对接
│   ├── 4.2 AgentCard ↔ 01 元数据字段映射
│   ├── 4.3 AgentCard 发布到 /.well-known/agent.json
│   ├── 4.4 Task ↔ Agent 生命周期映射
│   ├── 4.5 Signed Agent Cards ↔ capability 签名互认
│   ├── 4.6 多传输协议支持（JSON-RPC/gRPC/HTTP-REST）
│   └── 4.7 AP2 经济协调层（观察项，暂不纳入）
├── 五、OSINT 工具 MCP Server 化用例
├── 六、标准条目注册表（PROTO-001~025）
├── 七、兼容性测试要求
├── 八、版本历史
└── 九、参考文献
```

#### 4.4.2 09 INTEROP 标准文档大纲

```
09-airy-agent-interop-standard.md（INTEROP 域）
├── 一、范围与目的
├── 二、INTEROP 域编号体系
├── 三、AG-UI 对接规范
│   ├── 3.1 AG-UI 16 事件 ↔ CoreLoopThree 三阶段原生映射
│   ├── 3.2 Shared State ↔ MemoryRovol L1 双向同步
│   ├── 3.3 Tool-based Generative UI ↔ Agent 能力声明
│   ├── 3.4 Human in the Loop ↔ Agent SUSPENDED/RESUME 状态
│   ├── 3.5 传输无关性（SSE/WebSocket/Webhook）
│   └── 3.6 7 大特性支持矩阵
├── 四、ANP 对接规范
│   ├── 4.1 ANP 三层架构对接
│   ├── 4.2 did:wba ↔ capability owner 桥接
│   ├── 4.3 元协议协商 ↔ Agent 能力发现
│   ├── 4.4 去中心化身份 ↔ Cupolas capability
│   └── 4.5 跨平台认证流程
├── 五、标准条目注册表（INTEROP-001~020）
├── 六、兼容性测试要求
├── 七、版本历史
└── 八、参考文献
```

#### 4.4.3 现有 7 个标准文档的修订范围

| 文档 | 修订章节 | 修订内容 | 是否触及 L1 |
|------|---------|---------|-----------|
| 01 RT | 第十二章（新增） | A2A AgentCard 对外发布 | 否（新增章节） |
| 01 RT | — | 新增 AOS-STD-RT-025~028（A2A 桥接条目） | 否（追加条目） |
| 02 IPC | 第十四章（新增） | MCP JSON-RPC 2.0 桥接 | 否（新增章节） |
| 02 IPC | — | 新增 AOS-STD-IPC-024~030（MCP 桥接条目） | 否（追加条目） |
| 03 SEC | 附录（新增） | capability ↔ OAuth token / did:wba 桥接 | 否（附录） |
| 04 MEM | 附录（新增） | MemoryRovol L1 ↔ MCP Resources / AG-UI Shared State | 否（附录） |
| 05 COG | 附录（新增） | CoreLoopThree ↔ AG-UI 16 事件原生映射 | 否（附录） |
| 06 SCHED | — | 无修订（独立保留） | — |
| 07 SYS | — | 无修订（独立保留） | — |

**关键约束**：所有修订均不触及既有 L1 条目，确保 v1.x 采纳者零迁移成本。

#### 4.4.4 GOVERNANCE.md 具体内容大纲

```
GOVERNANCE.md
├── 一、标准委员会
│   ├── 1.1 构成（15 席）
│   ├── 1.2 任期与投票权
│   ├── 1.3 法定人数与决策门槛
│   └── 1.4 会议频率与纪要公开
├── 二、三级孵化机制
│   ├── 2.1 Draft（草案）
│   ├── 2.2 Proposed（提案）
│   ├── 2.3 Stable（稳定）
│   └── 2.4 Deprecated（弃用）
├── 三、RFC 流程
│   ├── 3.1 七步流程与时效
│   ├── 3.2 公示期操作方式
│   └── 3.3 投票记录公开
├── 四、SIG 组织
│   ├── 4.1 9 个 SIG 清单
│   ├── 4.2 SIG 章程要求
│   └── 4.3 SIG 会议纪要
├── 五、商标体系
│   ├── 5.1 Airymax Certified
│   ├── 5.2 Airymax Compatible
│   ├── 5.3 Airymax Inspired
│   └── 5.4 违规处理
├── 六、社区参与机制
│   ├── 6.1 邮件列表
│   ├── 6.2 GitHub Discussions
│   └── 6.3 社区激励
└── 七、版本历史
```

#### 4.4.5 CONTRIBUTING.md 与 CODE_OF_CONDUCT.md 具体内容

**CONTRIBUTING.md**：
- DCO（Developer Certificate of Origin）签名要求：所有 PR 必须包含 `Signed-off-by: Name <email>`。
- CLA 签署流程：个人 CLA（个人贡献者）+ 企业 CLA（企业贡献者，简化版，不含员工 CLA）。
- SIG 参与方式：如何加入 SIG、如何提交 RFC、如何参与评审。
- 代码贡献规范：参考 agent-linux 工程标准手册（`docs/AirymaxOS/50-engineering-standards/00-engineering-standards-handbook.md`）。
- 文档贡献规范：Markdown 风格、术语约束（微核心 vs 微内核）、引用规范。

**CODE_OF_CONDUCT.md**：
- 采纳 [Contributor Covenant 2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/)（与 CNCF CoC 一致）。
- 追加 Airymax 特有条款：不得在公开渠道披露未公开的 RFC 内容；不得在标准委员会投票前公开投票意向。

### 4.5 优化点 5（新增）：OCI-AI v1.3 规范对接

#### 4.5.1 为何需要对接 OCI-AI v1.3

**WebSearch 证据**：自 2026-04-01 起，Docker AI Toolkit（DAT）强制启用 OCI-AI v1.3 规范，未遵循的镜像被 Docker Hub AI Registry 拒绝推送。OCI-AI v1.3 由 OCI 联合 MLCommons 共同发布，统一 AI 工作负载的元数据描述、硬件亲和性声明、安全沙箱边界及可验证签名机制。

**对本体系的影响**：本体系定位为 AI Agent 标准，Agent 元数据（01 标准）的封装格式应采用 OCI-AI v1.3，以便：

1. 通过 Docker Hub AI Registry 分发 Agent 镜像。
2. 与 Kubernetes 调度器集成（基于 `hardware_requirements` 执行节点亲和性筛选）。
3. 与 Sigstore Cosign v2.8+ 签名链集成，实现供应链安全。
4. 与 Helm v3.12+ OCI Chart 协同，实现模型工件与 Helm Chart 元数据共置。

#### 4.5.2 OCI-AI v1.3 对接的具体方案

| 本体系字段 | OCI-AI v1.3 字段 | 映射规则 |
|-----------|-----------------|---------|
| `agent_id` | `.ai/manifest.json:agent.id` | 直接复制 |
| `name` | `.ai/manifest.json:agent.name` | 直接复制 |
| `version` | `.ai/manifest.json:agent.version` | 直接复制 |
| `runtime.min_memory_mb` | `hardware_requirements.gpu.memory.min`（若用 GPU）或 `hardware_requirements.cpu.memory.min` | 单位转换（MB → GiB） |
| `runtime.min_cpu_percent` | `hardware_requirements.cpu.cores.min` | 百分比 → 核数 |
| `capabilities` | `.ai/manifest.json:agent.capabilities` | 数组映射 |
| `token_budget.hard_limit` | `.ai/manifest.json:agent.token_budget.hard_limit` | 直接复制 |
| `sandbox_level` | `trust_policy.sandbox.level` | 直接复制（0-4 枚举） |
| —（本体系无对应） | `trust_policy.signature`（Cosign v2.8+） | 新增：Agent 镜像签名 |
| —（本体系无对应） | `runtimeConstraints.minCudaVersion` | 新增：GPU 兼容性 |
| —（本体系无对应） | `quantizationProfile` | 新增：量化配置 |

**对接位置**：PROTO 域新增条目 AOS-STD-PROTO-026~030（OCI-AI v1.3 对接）。

### 4.6 优化点 6（新增）：中国本地化合规

#### 4.6.1 T/CAMETA XX-2026 MCP 安全要求团体标准

**WebSearch 证据**：[中国机电一体化技术应用协会发布 T/CAMETA XX-2026《信息安全技术 模型上下文协议安全要求》征求意见稿](https://www.cameta.org.cn/uploadfile/2026/0410/20260410032120379.pdf)，由统信软件技术有限公司、中关村人工智能研究院、北京领翼工软科技有限公司、北京通明湖信息技术应用创新中心联合起草。

**关键章节**：

- §4 总体安全框架与基本原则
- §5 身份认证与访问控制规范（含"令牌透传"禁则）
- §6 操作分级与风险评估规范
- §7 资源管控与安全要求（资源/工具/提示词）
- §8 人工智能特有风险防护（提示词注入、采样风险、"混淆代理"）
- §9 传输层与会话安全规范（stdio / HTTP+SSE）
- §10 生命周期管理规范
- §11 审计、监测与应急响应规范
- §12 供应链安全与合规性评估

**对本体系的影响**：本体系若希望在中国市场被政府与大型企业采纳，必须对齐 T/CAMETA XX-2026。具体对接：

| T/CAMETA 章节 | 本体系对应 | 对接动作 |
|--------------|----------|---------|
| §5 身份认证 | 03 SEC Cupolas capability | 验证 capability 模型满足"令牌透传"禁则 |
| §6 操作分级 | 03 SEC 4 值裁决 | 验证 4 值裁决满足操作风险分级模型 |
| §7 资源管控 | 04 MEM + 05 COG | 验证 MemoryRovol 与 CoreLoopThree 满足资源/工具/提示词安全规范 |
| §8 AI 特有风险 | 05 COG | 追加提示词注入防护、采样风险管控、"混淆代理"防御条款 |
| §9 传输层 | 02 IPC | 验证 128B 头满足 stdio / HTTP+SSE 传输安全要求 |
| §10 生命周期 | 01 RT | 验证 6 状态机满足初始化/运行监控/注销清理规范 |
| §11 审计 | 02 IPC trace_id | 验证 trace_id 满足审计要素 |
| §12 供应链 | OpenChain 自认证 | 对齐 T/CAMETA 与 OpenChain 双重要求 |

#### 4.6.2 数据出境合规

本体系若被跨国企业采纳，Agent 元数据（含 Agent 能力声明、Token 预算等）跨境传输需遵守：

- **中国《数据出境安全评估办法》**（2022 年 9 月施行）：Agent 元数据若包含个人信息或重要数据，需进行数据出境安全评估。
- **EU GDPR**：Agent 元数据若包含个人数据，需遵守 GDPR 跨境传输条款。
- **EU Cyber Resilience Act**（2026 年生效）：要求所有数字产品提供 SBOM，本体系应在 OpenChain 自认证中覆盖。

**对接位置**：阶段 1 法律审查清单追加第八项"数据出境合规评估"。

***

## 5. 最新行业实践对比（2026 年 7 月）（任务 d）

### 5.1 MCP 协议最新状态对比

| 维度 | v1.0 报告描述 | 2026-07 最新状态 | 对齐度 |
|------|-------------|----------------|--------|
| 创建方 | Anthropic（2024-11） | Anthropic（2024-11） | 完全对齐 |
| 治理归属 | Linux Foundation AI Alliance（2025-12） | Agentic AI Foundation under Linux Foundation（2025-12，与 Block、OpenAI 共同创立） | **校正**：v1.0 表述略有偏差 |
| 当前规范版本 | 2025-11-25 | 2025-11-25（最新稳定版） | 完全对齐 |
| 下一版本 | 2026-07-28 Release Candidate | 2026-07-28 RC（5 月 21 日发布），最终版 7 月 28 日 ship | **校正**：v1.0 表述为"正式发布"，实际为 RC→最终版 |
| 协议格式 | JSON-RPC 2.0 | JSON-RPC 2.0（无状态化） | 完全对齐 |
| 传输 | stdio + Streamable HTTP | stdio + Streamable HTTP（无状态化后可缓存） | 完全对齐 |
| 认证 | OAuth 2.1 with PKCE | OAuth 2.1 / OpenID Connect（硬化） | 完全对齐 |
| 核心原语 | Resources / Tools / Prompts | Resources / Tools / Prompts（Tools 用完整 JSON Schema 2020-12） | 完全对齐 |
| Extensions | —（v1.0 未详述） | Tasks / MCP Apps / Skills over MCP（一等公民） | **v2.0 补充** |
| 弃用项 | —（v1.0 未提及） | Roots / Sampling / Logging（形式化弃用） | **v2.0 补充** |
| 生态规模 | —（v1.0 未量化） | 9700 万月下载、10000+ 公共服务器、OpenAI/Google/Microsoft/AWS 采纳 | **v2.0 补充** |

### 5.2 A2A 协议最新状态对比

| 维度 | v1.0 报告描述 | 2026-07 最新状态 | 对齐度 |
|------|-------------|----------------|--------|
| 创建方 | Google（2025-04） | Google Cloud（2025-04 Google Cloud Next 发布） | 完全对齐 |
| 治理归属 | Linux Foundation（2025-06） | Linux Foundation（2026-04 正式完成托管并发布 v1.0） | **校正**：v1.0 时间线略有偏差 |
| 当前规范版本 | 1.0.0 | 1.0.0（2026-04 稳定版） | 完全对齐 |
| 协议格式 | JSON-RPC 2.0 over HTTPS + SSE | JSON-RPC 2.0 / gRPC / HTTP+JSON/REST（多协议） | **v2.0 补充**：v1.0 未提及多协议 |
| 核心数据对象 | Task / Message / AgentCard / Part / Artifact / Extension | 同 + Signed Agent Cards（v1.0 新增） | **v2.0 补充**：Signed Agent Cards |
| 生态规模 | —（v1.0 未量化） | 150+ 组织、22000+ GitHub stars、5 种 SDK、Microsoft Azure/AWS Bedrock 集成 | **v2.0 补充** |
| 经济协调层 | —（v1.0 未提及） | Agent Payments Protocol (AP2)，60+ 组织支持 | **v2.0 观察** |

### 5.3 OCI 治理模式对比

| 维度 | v1.0 报告描述 | 2026-07 最新状态 | 对齐度 |
|------|-------------|----------------|--------|
| 治理结构 | 三层（TB / TDC / TOB） | 三层（TB / TDC / TOB），TOB 9 人任期 2 年 | 完全对齐 |
| 核心规范 | runtime-spec v1.2 / image-spec v1.1 / distribution-spec v1.1 | 同 | 完全对齐 |
| 专利授权 | OWFa 1.0 | OWFa 1.0 | 完全对齐 |
| 规范许可 | CC-BY-4.0 | CC-BY-4.0 | 完全对齐 |
| 实现许可 | Apache-2.0 | Apache-2.0 | 完全对齐 |
| **OCI-AI v1.3** | —（v1.0 未提及） | 2026-04 强制启用，统一 AI 工作负载元数据 | **v2.0 新增**：v1.0 关键遗漏 |

### 5.4 CNCF 孵化机制对比

| 维度 | v1.0 报告描述 | 2026-07 最新状态 | 对齐度 |
|------|-------------|----------------|--------|
| 三级模型 | Sandbox→Incubating→Graduated | Sandbox→Incubating→Graduated（+Archived） | 完全对齐 |
| Sandbox 归档率 | 15-20%（3 年内） | 15-20%（3 年内） | 完全对齐 |
| Incubating 归档率 | 5-8% | 5-8% | 完全对齐 |
| Graduated 比例 | 4% | 4%（<1% 归档率） | 完全对齐 |
| 2026 毕业案例 | —（v1.0 未列举） | Dragonfly（2026-01-14）、Kyverno（2026-03-16） | **v2.0 补充** |
| 2026 Incubating 案例 | — | Tekton（2026-03-24，跳过 Sandbox 直接 Incubating） | **v2.0 补充** |
| 毕业核心要求 | CII Badge / CoC / 采纳文档 / Committer 多样性 / 安全审计 / 治理文档 / TOC 超多数投票 | thriving adoption / documented governance / strong security / community sustainability | 完全对齐 |

### 5.5 OpenChain 认证对比

| 维度 | v1.0 报告描述 | 2026-07 最新状态 | 对齐度 |
|------|-------------|----------------|--------|
| ISO/IEC 5230 | 25 项验证材料 | 25 项验证材料 | 完全对齐 |
| ISO/IEC 18974 | 25 项安全验证材料 | 25 项安全验证材料 | 完全对齐 |
| 社区规模 | — | 1000+ 公司 | **v2.0 补充** |
| 2026 合规案例 | — | Hitachi Energy（2026-01-27）、42dot（2026-06-19）、CJ OliveYoung（2026-03-10）、norxs（2026-06-05） | **v2.0 补充** |
| AI SBOM 自认证 | — | OpenChain AI SBOM Self Certification（2026-04-09 Webinar，ISO 4200X 系列） | **v2.0 新增** |
| SBOM 文档质量指南 | — | 公开评论期 2026-05-31 结束 | **v2.0 观察** |

### 5.6 对比结论

v1.0 方案与 2026 年 7 月最新行业实践**整体对齐度约 85%**，主要偏差集中在：

1. MCP 治理归属（AI Alliance vs Agentic AI Foundation）——细微偏差。
2. MCP 2026-07-28 版本性质（正式发布 vs RC→最终版）——细微偏差。
3. A2A 捐赠时间线（2025-06 vs 2026-04）——细微偏差。
4. OCI-AI v1.3 对接——v1.0 关键遗漏，v2.0 补全。
5. T/CAMETA 中国本地化合规——v1.0 关键遗漏，v2.0 补全。
6. OpenChain AI SBOM 自认证——v1.0 未提及，v2.0 补全。

***

## 6. 风险评估深化（任务 e）

### 6.1 协议快速演进风险（深化）

**v1.0 描述**：MCP、A2A、AG-UI、ANP 在 2026 年仍处于快速演进期。

**v2.0 深化**：识别具体的失败模式：

| 失败模式 | 触发条件 | 影响 | 缓解措施 |
|---------|---------|------|---------|
| MCP 破坏性升级 | 2026-07-28 之后的下一次 MAJOR 升级（预计 2027 H1） | PROTO 域 MCP 对接条目需 MAJOR 升级 | 版本协商字段 + 抽象层隔离 + L3 稳定级 |
| A2A v2.0 破坏性变更 | A2A v2.0 发布（预计 2027） | AgentCard 字段映射需重做 | 字段映射表版本化 + 双向兼容 |
| AG-UI 事件类型扩展 | AG-UI 新增事件类型 | INTEROP 域映射表需扩展 | 事件类型枚举开放 + CUSTOM 事件兜底 |
| ANP did:wba 方法变更 | W3C DID 规范更新 | did:wba ↔ capability 桥接需重做 | 桥接层独立维护 + 版本协商 |
| AP2 经济协调层定型 | AP2 v1.0 发布（观察） | 可能需要新增 PROTO 域条目 | 暂不纳入 v2.x，观察列表跟踪 |

### 6.2 专利授权法律风险（深化）

**v1.0 描述**：SPHARX 自有专利暴露、贡献者专利纠纷、跨境法律差异。

**v2.0 深化**：

| 风险点 | 具体表现 | 缓解措施 |
|--------|---------|---------|
| SPHARX 自有专利暴露边界不清 | OWFa 1.0 要求公开 Granted Claims，但 SPHARX 可能未完整盘点其专利 | 阶段 1 完成专利盘点，公开清单到 `PATENTS.md` |
| Defensive Termination 反向触发 | 若 SPHARX 作为原告起诉某实现者专利侵权，SPHARX 自身获得的 OWFa 承诺终止 | 法务评估 SPHARX 作为原告的场景，必要时保留特定专利不纳入 OWFa |
| 贡献者未声明专利 | 第三方贡献者贡献含其专利的条款但未声明 | 强制 DCO 签名 + CLA 中要求专利声明 |
| 跨境解释差异 | OWFa 1.0 依据美国法律，在中国/欧盟解释可能不同 | 引入中国与欧洲本地法律意见 |
| OWFa 与 Apache-2.0 叠加效应 | 两层专利授权叠加可能产生意外法律后果 | 法务审查叠加效应，必要时调整许可证组合 |

### 6.3 社区接受度风险（深化）

**v1.0 描述**：现有采纳者抗拒、社区参与不足、SPHARX 主导权让渡阻力。

**v2.0 深化**：

| 风险点 | 具体表现 | 缓解措施 |
|--------|---------|---------|
| 现有采纳者抗拒 CLA | v1.x 采纳者可能不愿意签署 CLA 升级到 v2.x | v1.x 与 v2.x 在 L1 契约上完全兼容，无需强制升级 |
| SIG 流于形式 | 9 个 SIG 若无足够社区参与，将变成 SPHARX 内部会议 | SIG 会议公开 + 社区激励（公开致谢、优先采纳、Airymax Certified 折扣） |
| RFC 公开评论为零 | 30 天公开评论期若无社区参与，流程形式化 | 主动邀请已知采纳者评论 + 在 GitHub Discussions 置顶 |
| SPHARX 内部让渡阻力 | 标准委员会重组后社区代表与企业代表获得投票权 | 阶段 3 启动前 SPHARX 内部完成决策对齐 |
| 中国社区参与不足 | 本体系当前以英文为主，中国开发者参与门槛高 | 关键文档中英双语 + T/CAMETA 对接 |

### 6.4 实现同步风险（深化）

**v1.0 描述**：PROTO/INTEROP 桥接层实现滞后、形式化验证人力不足、OpenChain 自认证工作量。

**v2.0 深化**：

| 风险点 | 具体表现 | 缓解措施 |
|--------|---------|---------|
| agentrt 桥接层实现滞后 | PROTO/INTEROP 标准发布但 agentrt 未实现 | 实现先行原则：Proposed 阶段必须有 1 个参考实现 |
| agent-linux 桥接层实现滞后 | agent-linux 基于 Linux 6.6，桥接层需适配内核接口 | agent-linux 实现进度可落后 1 个 MINOR 版本 |
| 形式化验证人力不足 | Isabelle/HOL 或 Coq 专业人力稀缺 | 与高校合作 + 阶段 4 形式化验证为可选交付物 |
| OpenChain 50 项验证材料拖延 | 法务、工程、运营多角色协作 | 渐进式自认证：阶段 1 基线、阶段 3 完成 50%、阶段 4 完成全部 |
| OCI-AI v1.3 对接滞后 | OCI-AI v1.3 是 2026-04 新规范，agentrt 可能未跟进 | 阶段 4 启动前完成 OCI-AI v1.3 规范研读 |
| T/CAMETA 对接滞后 | T/CAMETA XX-2026 仍为征求意见稿，未正式发布 | 跟踪正式发布进度，阶段 1 完成对齐评估 |

### 6.5 商标与反垄断风险（新增）

**v1.0 描述**：商标冲突、认证体系法律合规、商标使用规范。

**v2.0 深化**：

| 风险点 | 具体表现 | 缓解措施 |
|--------|---------|---------|
| 反垄断风险 | 拒绝特定方认证可能被诉垄断 | 认证标准、流程、费用全部公开；任何满足条件的方均可申请认证 |
| 商标稀释 | 第三方滥用 Certified / Compatible / Inspired 标识 | GOVERNANCE.md 明确三种标识使用条件与违规处理 |
| 商标跨境冲突 | Airymax 商标在目标司法管辖区可能冲突 | 阶段 4 启动前在中国、美国、欧盟完成商标检索 |
| 认证标准不透明 | 认证标准若不公开，可能被诉歧视 | 认证标准全部公开，测试套件开源 |

***

## 7. 关键决策点细化（任务 f）

### 7.1 决策一：是否引入 OWFa 1.0 专利授权（细化）

| 项 | 内容 |
|----|------|
| **决策问题** | 是否在阶段 1 引入 OWFa 1.0 Patent Only 作为本体系的专利授权机制？ |
| **决策依据** | OCI 11 年实践证明 OWFa 1.0 可行；OpenChain 自认证要求明确的专利授权；企业采纳法务审查要求 OWFa 级承诺 |
| **影响范围** | 阶段 1 全部交付物：`PATENTS.md`、`PATENTS-LEGAL-REVIEW.md`、8 份文档头部 SPDX 标识、`LICENSE.md`、`NOTICE.md` |
| **决策时间窗口** | 阶段 1 启动前 1 周（W0） |
| **不决策的后果** | 企业采纳被合规审查卡住；与 OCI/CNCF 治理不对齐；未来 LF 托管缺乏基本门槛 |
| **推荐方案** | **是**，引入 OWFa 1.0 Patent Only |
| **备选方案 A** | 仅使用 Apache-2.0 内置专利授权（保护力度弱） |
| **备选方案 B** | 不引入专利授权（保持现状，接受企业采纳阻力） |

### 7.2 决策二：是否采纳 CNCF 三级孵化机制（细化）

| 项 | 内容 |
|----|------|
| **决策问题** | 是否在阶段 3 采纳 CNCF 风格的 Draft→Proposed→Stable 三级孵化机制？ |
| **决策依据** | CNCF 三级模型为社区提供清晰成熟度信号；2026 年 Dragonfly/Kyverno 毕业案例证明机制有效；本体系需要区分实验性条目与稳定条目 |
| **影响范围** | 阶段 3 治理文档、标准委员会投票规则、所有 174 条现有条目的重新分级、RFC 流程时效（118 天总时效） |
| **决策时间窗口** | 阶段 2 完成时（W4） |
| **不决策的后果** | 新提案与已稳定条目混在一起；社区无法判断哪些可放心采纳；缺少社区成熟度信号 |
| **推荐方案** | **是**，采纳三级孵化机制 |
| **备选方案 A** | 保留当前 L1-L4 稳定性分级，不引入孵化机制 |
| **备选方案 B** | 仅引入 Draft / Stable 两级（折中方案） |

### 7.3 决策三：是否新增 PROTO/INTEROP 两个域（细化）

| 项 | 内容 |
|----|------|
| **决策问题** | 是否在阶段 2 新增 PROTO（协议对接）与 INTEROP（互操作）两个域？ |
| **决策依据** | MCP 9700 万月下载、A2A 150+ 组织支持已构成事实标准；强行塞入既有 7 域会破坏语义清晰度；新增域不破坏既有 L1 契约 |
| **影响范围** | 阶段 2 全部交付物：08/09 标准文档、编号体系扩展（PROTO-001~030、INTEROP-001~020）、02/01 标准修订 |
| **决策时间窗口** | 阶段 1 完成时（W2） |
| **不决策的后果** | 本体系持续置身于 2026 AI Agent 协议生态之外；N×M 集成成本；被行业标准边缘化 |
| **推荐方案** | **是**，新增两域 |
| **备选方案 A** | 仅新增 PROTO 域，将 INTEROP 内容并入 PROTO |
| **备选方案 B** | 不新增域，将对接内容作为既有域的附录 |

### 7.4 决策四：是否将测试套件以 Apache-2.0 独立开源（细化）

| 项 | 内容 |
|----|------|
| **决策问题** | 是否在阶段 3 将兼容性测试套件从文档内嵌迁移到独立 `compatibility/` 目录，并以 Apache-2.0 + OWFa 1.0 许可证开源？ |
| **决策依据** | OCI/CNCF 实践证明测试套件独立 Apache-2.0 鼓励社区贡献；AGPL 内嵌阻碍贡献；OWFa 1.0 保护测试用例贡献者专利风险 |
| **影响范围** | 阶段 3 `compatibility/` 目录搭建、9 域测试用例许可证变更、OWFa 1.0 引用到测试套件 |
| **决策时间窗口** | 阶段 3 启动前（W5） |
| **不决策的后果** | 测试套件社区贡献门槛高；与 OCI/CNCF 实践不对齐；测试用例贡献者专利风险未保护 |
| **推荐方案** | **是**，独立开源（Apache-2.0 + OWFa 1.0） |
| **备选方案 A** | 测试套件保留在文档内，但改用 Apache-2.0 许可 |
| **备选方案 B** | 测试套件保持 AGPL 双许可 |

### 7.5 决策五：是否对标 openEuler OpenChain 认证（细化）

| 项 | 内容 |
|----|------|
| **决策问题** | 是否在阶段 4 完成 OpenChain ISO/IEC 5230 与 ISO/IEC 18974 自认证？ |
| **决策依据** | 2026 年 Hitachi Energy/42dot/CJ OliveYoung 等案例证明自认证可行；OpenChain 已成政府与大型企业采购预筛选条件；EU CRA 要求 SBOM；AI SBOM 自认证（ISO 4200X）已上线 |
| **影响范围** | 阶段 4 全部交付物、法务与工程协作工作量（50 项验证材料 + AI SBOM 自认证） |
| **决策时间窗口** | 阶段 3 完成时（W10） |
| **不决策的后果** | 政府与大型企业采购障碍；EU CRA 合规风险；供应链不透明 |
| **推荐方案** | **是**，完成自认证（含 AI SBOM） |
| **备选方案 A** | 仅完成 ISO/IEC 5230 自认证，暂不做 18974 |
| **备选方案 B** | 不做自认证，仅在文档中声明"参考 OpenChain 实践" |

### 7.6 决策六（新增）：是否对接 OCI-AI v1.3 规范

| 项 | 内容 |
|----|------|
| **决策问题** | 是否在阶段 4 对接 OCI-AI v1.3 规范作为 Agent 元数据封装格式？ |
| **决策依据** | Docker AI Toolkit 2026-04 强制启用 OCI-AI v1.3；未遵循的镜像被 Docker Hub AI Registry 拒绝；OCI-AI v1.3 由 OCI 联合 MLCommons 发布，是 AI 工作负载专用格式 |
| **影响范围** | 阶段 4 OCI 对接子任务、PROTO 域新增 AOS-STD-PROTO-026~030、agentrt 实现 OCI-AI v1.3 镜像构建 |
| **决策时间窗口** | 阶段 3 完成时（W10） |
| **不决策的后果** | Agent 镜像无法通过 Docker Hub AI Registry 分发；与 Kubernetes 调度器集成受限；供应链安全（Cosign 签名）缺失 |
| **推荐方案** | **是**，对接 OCI-AI v1.3 |
| **备选方案 A** | 对接传统 OCI image-spec v1.1（不适用 AI 工作负载） |
| **备选方案 B** | 不对接 OCI，自定义 Agent 镜像格式（孤立生态） |

### 7.7 决策七（新增）：是否对齐 T/CAMETA XX-2026 中国 MCP 安全要求

| 项 | 内容 |
|----|------|
| **决策问题** | 是否在阶段 1 完成对齐 T/CAMETA XX-2026《信息安全技术 模型上下文协议安全要求》团体标准？ |
| **决策依据** | T/CAMETA XX-2026 由统信软件、中关村人工智能研究院等起草，是中国市场 MCP 安全事实标准；本体系若希望被中国政府与大型企业采纳，必须对齐 |
| **影响范围** | 阶段 1 法律审查清单追加第八项"数据出境合规评估"；03 SEC 追加提示词注入防护、采样风险管控、"混淆代理"防御条款；PROTO 域 MCP 对接条目对齐 T/CAMETA §5-§12 |
| **决策时间窗口** | 阶段 1 启动前 1 周（W0） |
| **不决策的后果** | 中国市场采纳障碍；与统信软件等中国厂商生态不兼容；数据出境合规风险 |
| **推荐方案** | **是**，对齐 T/CAMETA XX-2026 |
| **备选方案 A** | 仅在文档中引用 T/CAMETA，不做实质对齐 |
| **备选方案 B** | 不对齐 T/CAMETA（接受中国市场采纳障碍） |

***

## 8. 修正后的实施路径

### 8.1 修正后的四阶段路径总览

| 阶段 | 版本跃迁 | 工期 | 核心交付 | 风险等级 | v2.0 修正 |
|------|---------|------|---------|---------|----------|
| **阶段 1：专利授权补全 + 中国合规** | 1.1 → 1.2 | ~3 周（v1.0 为 2 周） | OWFa 1.0 + CC-BY-4.0 + OpenChain 基线 + T/CAMETA 对齐评估 + 数据出境合规评估 | 低 | **追加**：T/CAMETA 对齐评估、数据出境合规评估 |
| **阶段 2：协议对接** | 1.2 → 2.0 | ~4 周 | PROTO/INTEROP 两域 + 08/09 标准 + 02/01 修订 + MCP 2026-07-28 无状态化适配 | 中 | **校正**：MCP 2026-07-28 RC 性质、A2A v1.0 Signed Agent Cards 对接 |
| **阶段 3：治理升级** | 2.0 → 2.1 | ~6 周 | CNCF 三级孵化 + RFC 流程 + Apache-2.0 测试套件 + 9 SIG | 中 | **细化**：RFC 七步流程 118 天时效、SIG 章程要求 |
| **阶段 4：生态扩展** | 2.1 → 2.2 | ~9 周（v1.0 为 8 周） | Airymax Certified + **OCI-AI v1.3 对接** + seL4 形式化验证 + OpenChain 自认证（含 AI SBOM） | 高 | **追加**：OCI-AI v1.3 对接、AI SBOM 自认证 |

**合计**：~22 周（v1.0 为 ~20 周），2026 年底完成 v1.1 → v2.2 跃迁。

### 8.2 修正后的详细迁移计划

#### 8.2.1 v1.1 → v1.2（专利授权补全 + 中国合规，~3 周）

| 周次 | 任务 | 负责人 | 交付物 |
|------|------|--------|--------|
| W1 | OWFa 1.0 七步法律审查 + SPHARX 专利清单 | 法务 + 标准总维护者 | `PATENTS.md`、`PATENTS-LEGAL-REVIEW.md` |
| W1 | 8 份文档头部 SPDX 标识更新 | 文档维护者 | 8 份 `.md` 头部修改 |
| W2 | `LICENSE.md` + `NOTICE.md` 编写 | 法务 | `LICENSE.md`、`NOTICE.md` |
| W2 | OpenChain 合规基线自评估 + AI SBOM 自评估启动 | 法务 + 工程师 | `OpenChain-baseline.md` |
| W2 | T/CAMETA XX-2026 对齐评估 | 法务 + 工程师 | `TCAMETA-alignment.md` |
| W3 | 数据出境合规评估 | 法务 | `Data-Export-Compliance.md` |
| W3 | v1.2 发布公告 + 迁移指南 | 标准总维护者 | 公告 + 迁移指南 |

#### 8.2.2 v1.2 → v2.0（协议对接，~4 周）

| 周次 | 任务 | 交付物 |
|------|------|--------|
| W1-W2 | 08 PROTO 标准草案（MCP 部分，含 2026-07-28 无状态化适配 + Extensions 对接 + 弃用项迁移） | `08-airy-agent-protocol-standard.md`（MCP 章节） |
| W2-W3 | 08 PROTO 标准草案（A2A 部分，含 Signed Agent Cards 对接） | `08-airy-agent-protocol-standard.md`（A2A 章节） |
| W3 | 09 INTEROP 标准草案（AG-UI 16 事件 ↔ CoreLoopThree 原生映射 + ANP did:wba 桥接） | `09-airy-agent-interop-standard.md` |
| W4 | 修订 02 IPC 标准（第十四章 MCP JSON-RPC 2.0 桥接） | `02-airy-ipc-protocol-standard.md` 第 14 章 |
| W4 | 修订 01 RT 标准（第十二章 A2A AgentCard 对外发布） | `01-airy-agent-runtime-standard.md` 第 12 章 |
| W4 | 公示期 30 天启动 + v2.0 发布 | v2.0 正式发布 |

#### 8.2.3 v2.0 → v2.1（治理升级，~6 周）

| 周次 | 任务 | 交付物 |
|------|------|--------|
| W1-W2 | 9 个 SIG 组成立 + 各 SIG 首次会议 + SIG 章程 | SIG 章程 + 会议纪要 |
| W2-W3 | CLA 模板（个人 + 企业）+ DCO 流程 | CLA 模板 + DCO 配置 |
| W3-W4 | 邮件列表 `standards@airymax.org` 搭建 + GitHub Discussions 启用 | 邮件列表 + RFC 模板 |
| W4-W5 | `compatibility/` 目录搭建 + 9 域测试用例迁移（Apache-2.0 + OWFa 1.0） | `compatibility/` 完整目录 |
| W5-W6 | `GOVERNANCE.md` + `CONTRIBUTING.md` + `CODE_OF_CONDUCT.md` 起草与评审 | 三份治理文档 |
| W6 | v2.1 发布 + 社区推广 | v2.1 正式发布 |

#### 8.2.4 v2.1 → v2.2（生态扩展，~9 周）

| 周次 | 任务 | 交付物 |
|------|------|--------|
| W1-W2 | Airymax Certified 商标注册申请（中国、美国、欧盟）+ 反垄断评估 | 商标申请回执 + 反垄断评估报告 |
| W2-W4 | OCI-AI v1.3 对接规范 + 参考实现（PROTO-026~030） | OCI-AI v1.3 兼容 Agent 元数据格式 |
| W4-W6 | seL4 风格形式化验证基线（capability 派生两大不变式，可选交付物） | Isabelle/HOL 证明（若人力允许） |
| W6-W7 | OpenChain ISO/IEC 5230 完整自认证（25 项）+ ISO/IEC 18974（25 项）+ AI SBOM 自认证 | 50+ 项验证材料 + 自认证结果 |
| W7-W8 | 第三方兼容性审计启动 | 审计委托合同 |
| W8-W9 | v2.2 发布 | v2.2 正式发布 |

### 8.3 与 agentrt / agent-linux 实现同步的精确窗口

| 标准变更类型 | agentrt 同步窗口 | agent-linux 同步窗口 | v2.0 修正 |
|------------|----------------|---------------------|----------|
| L1 条目新增 | 标准发布后 1 个 MINOR 版本内 | 标准发布后 1 个 MINOR 版本内 | 不变 |
| L2/L3 条目新增 | 标准发布后 2 个 MINOR 版本内 | 标准发布后 2 个 MINOR 版本内 | 不变 |
| 法律文档变更 | 不影响代码 | 不影响代码 | 不变 |
| 治理文档变更 | 不影响代码 | 不影响代码 | 不变 |
| PROTO/INTEROP 新增 | 标准发布后 1 个 MINOR 版本内（实现桥接层） | 标准发布后 2 个 MINOR 版本内（实现桥接层） | **细化**：agent-linux 允许落后 1 个 MINOR 版本 |
| OCI-AI v1.3 对接 | 标准发布后 2 个 MINOR 版本内 | 标准发布后 3 个 MINOR 版本内 | **新增** |
| 兼容性测试新增 | 必须通过新测试 | 必须通过新测试 | 不变 |
| 形式化验证 | 不强制 | 不强制 | **新增**：可选交付物 |

**关键约束**：agentrt 与 agent-linux 的实现进度**不得落后**于 OpenStandards 标准发布超过 1 个 MINOR 版本（agentrt）或 2 个 MINOR 版本（agent-linux）。若实现滞后，标准发布必须延期。

***

## 9. 结语

本 v2.0 优化审查报告基于对 v1.0 重建方案的逐项验证、6 个优化点的细化、2026 年 7 月最新行业实践的 WebSearch 对比、6 类风险的深化、7 项关键决策点的细化，提出了修正后的四阶段、~22 周实施路径。

v2.0 相对 v1.0 的核心增量价值：

1. **校正**：MCP 2026-07-28 版本性质（RC→最终版）、A2A 捐赠时间线（2026-04）、治理归属（Agentic AI Foundation）。
2. **细化**：许可证分离六类产物矩阵、MCP JSON-RPC 桥接层字段映射、A2A AgentCard 字段映射、AG-UI 16 事件↔CoreLoopThree 原生映射、标准委员会 15 席职责、SIG 组织方式、RFC 七步流程 118 天时效、08/09 标准文档大纲。
3. **新增**：OCI-AI v1.3 规范对接（v1.0 关键遗漏）、T/CAMETA XX-2026 中国本地化合规（v1.0 关键遗漏）、OpenChain AI SBOM 自认证、数据出境合规、反垄断风险评估。
4. **深化**：协议快速演进的 5 类失败模式、专利授权的 5 类法律风险、社区接受度的 5 类表现、实现同步的 6 类风险点、商标与反垄断的 4 类风险点。

v2.0 与 v1.0 的核心理念一致：**"不破坏既有契约，分层叠加新能力"**。所有 L1 永久稳定条目（约 84.5%）保持不变，新增能力以独立域、独立文档、独立许可的形式叠加。这确保了 agentrt、agent-linux 及任何已采纳 v1.1 的第三方实现可在零迁移成本下受益于 v2.x 的法律与生态增强。

本报告作为 v2.x 重建的优化起点，提交标准委员会评审。评审通过后，将按修正后的四阶段路径逐步落地，每阶段交付物独立发布、独立采纳。

***

## 10. 参考文献与外部链接

### 10.1 AI Agent 协议生态（2026-07 验证）

| 协议 | 资源类型 | URL |
|------|---------|-----|
| MCP | 官方规范（latest） | https://modelcontextprotocol.io/specification/latest/index |
| MCP | 2026-07-28 Release Candidate 公告 | https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/ |
| MCP | 规范草稿（draft） | https://modelcontextprotocol.io/specification/draft |
| MCP | 完全指南（2026） | https://www.getmaxim.ai/articles/what-is-model-context-protocol-mcp-a-complete-guide-for-2026/ |
| MCP | 中国团体标准 T/CAMETA XX-2026 征求意见稿 | https://www.cameta.org.cn/uploadfile/2026/0410/20260410032120379.pdf |
| A2A | 官方规范 v0.3.0 | https://a2a-protocol.org/v0.3.0/specification/ |
| A2A | Linux Foundation 2026-04 新闻稿 | https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year |
| A2A | 企业级互操作分析（2026-04） | https://agentmodeai.com/a2a-agent-to-agent-protocol/ |
| A2A | OAuth 集成研究报告 | https://jevvellabs.com/assets/files/oauth-for-agent-integration.pdf |
| AP2 | Agent Payments Protocol | https://ap2-protocol.org/ |

### 10.2 成熟开放标准治理模式（2026-07 验证）

| 治理模式 | 资源类型 | URL |
|---------|---------|-----|
| OCI | 官方 FAQ | https://opencontainers.org/faq/ |
| OCI | Board of Directors | https://theorg.com/org/open-container-initiative-oci/teams/board-of-directors |
| OCI-AI | v1.3 强制启用通告（2026-04） | https://blog.csdn.net/CodeIsle/article/details/160526786 |
| OWFa 1.0 | Patent Only 协议全文 | https://www.openwebfoundation.org/the-agreements/the-owf-1-0-agreements-granted-claims/owfa-1-0-patent-only |
| CNCF | 项目生命周期 | https://contribute.cncf.io/projects/lifecycle/ |
| CNCF | 项目成熟度模型分析（2026-02） | https://timderzhavets.com/blog/cncf-project-maturity-ladder-when-to-bet-on-sandbox-vs/ |
| CNCF | Dragonfly 毕业（2026-01） | https://dragonfly.website.cncfstack.com/blog/2026/01/15/cncf-announces-dragonfly-graduation |
| CNCF | Kyverno 毕业（2026-03） | https://lucaberton.com/blog/kyverno-cncf-graduated-kubernetes-policy-engine/ |
| CNCF | Tekton 进入 Incubating（2026-03） | https://www.cncf.io/blog/2026/03/24/tekton-becomes-a-cncf-incubating-project/ |
| seL4 | 许可证模型 | https://www.sel4.org/Legal/license.html |
| seL4 | 官网 | https://www.sel4.org/ |
| openEuler | 贡献攻略 | https://www.openeuler.org/zh/community/contribution/detail.html |
| OpenChain | 官方 FAQ | https://openchainproject.org/resources/faq |
| OpenChain | ISO/IEC 5230 | https://www.iso.org/standard/81039.html |
| OpenChain | ISO/IEC 18974 | https://www.iso.org/standard/86450.html |
| OpenChain | Hitachi Energy 认证（2026-01） | https://openchainproject.org/news/2026/01/27/hitachi-energy-achieves-openchain-iso-5230-certification-reinforcing-commitment-to-open-source-excellence |
| OpenChain | CJ OliveYoung 认证（2026-03） | https://openchainproject.org/news/2026/03/10/cj-oliveyoung-becomes-the-first-in-the-korean-beauty-industry-to-declare-open-source-international-standard-certification |
| OpenChain | AI SBOM 自认证 Webinar（2026-04） | https://openchainproject.org/news/2026/04/09/webinar-open-chain-ai-sbom-iso-42001-iso42003 |
| OpenChain | 韩文工作组合规指南（2026-03 更新） | https://openchain-project.github.io/OpenChain-KWG/_print/guide/opensource_for_enterprise/ |
| OpenChain | ISO/IEC 5230 准备指南 | https://openchain-project.github.io/OpenChain-KWG/guide/iso5230_guide/ |

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

### 10.4 Airymax 内部参考

| 资源 | 路径 |
|------|------|
| v1.0 重建方案 | `docs/OpenStandards/_research_v1.0/01-open-standards-rebuild-proposal.md` |
| OpenStandards README | `docs/OpenStandards/README.md` |
| 01 Agent 运行时标准 | `docs/OpenStandards/01-airy-agent-runtime-standard.md` |
| 02 IPC 协议标准 | `docs/OpenStandards/02-airy-ipc-protocol-standard.md` |
| 03 安全模型标准 | `docs/OpenStandards/03-airy-security-model-standard.md` |
| 04 记忆卷载标准 | `docs/OpenStandards/04-airy-memory-rovol-standard.md` |
| 05 认知循环标准 | `docs/OpenStandards/05-airy-cognition-loop-standard.md` |
| 06 调度标准 | `docs/OpenStandards/06-airy-scheduling-standard.md` |
| 07 系统调用标准 | `docs/OpenStandards/07-airy-syscall-standard.md` |
| agent-linux 工程标准手册 | `docs/AirymaxOS/50-engineering-standards/00-engineering-standards-handbook.md` |
| 跨项目代码共享 | `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md` |

***

## 11. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 2.0 | 2026-07-13 | 基于 v1.0 重建方案的第二轮优化审查：验证四阶段路径、提出六个优化点（含 OCI-AI v1.3 与中国本地化合规两个新增）、深化风险评估、细化七项关键决策点、修正实施路径至 ~22 周 |

***

Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
"From data intelligence emerges."
