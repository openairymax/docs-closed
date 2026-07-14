Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# Airymax 开放标准 v2.1 系统性复审与优化报告

> **文档定位**: OpenStandards 内部研究文档（_research_v2.1 系列）
> **版本**: 1.1（复审报告 — 增量修订版）
> **最后更新**: 2026-07-13
> **SPDX-License-Identifier**: CC-BY-4.0
> **作者**: OpenStandards 复审小组
> **状态**: 待标准委员会评审
> **审查范围**: `docs/OpenStandards/` 全部 8 文件（README + 01~07，共 4409 行）+ `_research_v1.0/`（v1.0 重建方案）+ `_research_v2.0/`（v2.0 优化基线）
> **修订说明**: v1.1 在 v1.0 草案基础上补充 P1/P2 级问题验证（README 断裂引用、JSON Schema/Protobuf 形式化规范、参考实现）、LangGraph/CrewAI 行业对标、可独立实现性评估、治理流程 SPHARX 中心化深化分析，并修正 03 SEC `are_cap_t` 出现次数统计（17 → 22 处）。

***

## 0. 文档元信息与读者指南

### 0.1 文档定位

本报告是 Airymax 开放标准体系（OpenStandards，下称"本体系"）在 v2.0 优化研究（`_research_v2.0/`）之后进行的**系统性复审与 v2.1 优化方案**研究文档，落盘于 `docs/OpenStandards/_research_v2.1/`。报告本身不是规范条款，仅作为 v2.1 升级决策的事实与逻辑依据。最终迁移到 v2.1 的所有正式条款仍以 `AOS-STD-<域>-<NNN>` 编号在主标准文档中固化。

### 0.2 审查方法与证据来源

- **静态审查**：对 `docs/OpenStandards/` 全部 8 文件（4409 行）逐文件、逐条目交叉比对。
- **基线比对**：以 `_research_v2.0/01-open-standards-optimization-v2.md`（1088 行）为 v2.0 优化基线，逐项验证落地状态。
- **行业对标**：基于 2026 年上半年（H1）公开规范与官方文档，覆盖 MCP / A2A / OpenAI Agents SDK / IETF IAIP / OpenTelemetry / OCI-AI / T/CAMETA 等七项关键生态进展。
- **工具验证**：通过 Grep 全文检索确认错误码、命名变体、`[SC]/[SS]/[IND]` 标注覆盖度、许可声明等关键事实。

### 0.3 阅读路径建议

- **决策者**：阅读第 1、6、7 节，重点关注 v2.0 vs v2.1 评分对比与优先级路线图。
- **标准作者**：阅读第 2、3 节，理解 v2.0 未落地项与当前方案的 5 维缺陷。
- **协议对接工程师**：阅读第 4、5 节，理解 2026 H1 行业生态与 Airymax 差异化定位。
- **治理与法务**：阅读第 4.6、6.4 节，理解 OWFa / CNCF / OpenChain 治理升级路径。

***

## 1. 执行摘要

### 1.1 一句话结论

v2.0 优化研究（2026-07-13）提出的 6 项优化建议**全部未落地到主标准文档**，当前体系仍停留在 v1.1 草案状态（README 头部版本声明甚至回退到 1.0），且在错误码一致性、命名规范、`[SC]/[SS]/[IND]` 标注覆盖度三个技术维度上**比 v2.0 描述的更严重**；与此同时，2026 H1 行业生态已发生实质性跃迁（MCP 2026-07-28 无状态化、A2A v1.2 签名 AgentCard、IETF IAIP 五草案并行、OpenAI Agents SDK 沙箱化、OCI-AI v1.3 强制实施），本体系与行业事实标准的差距正加速扩大。

### 1.2 v2.0 vs v2.1 评分对比表

下表以 10 维度量化评估 v2.0（研究阶段，未落地）与 v2.1（本报告目标方案）的差距与目标。

| # | 评估维度 | v2.0 研究基线（2026-07-13） | v2.1 目标方案（本报告） | 提升幅度 | 关键差距 |
|---|---------|--------------------------|---------------------|---------|---------|
| 1 | **错误码一致性** | 3 / 10（7 标准三套方案，03 SEC SSoT 自相矛盾） | 9 / 10（统一 SSoT + 转换表 + 兼容期） | +6 | 07 SYS 完全独立方案；05 COG 双码同值；04/06 ENOENT 冲突 EINVAL |
| 2 | **命名规范** | 4 / 10（三种变体：`are_cap_t` 26 处 / `cap_t` 8 处 / 应为 `airy_cap_t`） | 10 / 10（全量 `airy_cap_t` 34 处改名 + 函数前缀对齐） | +6 | 03 SEC 定义源错误（22 处）；07 SYS 第三种变体（8 处）；函数前缀已对齐但类型未对齐 |
| 3 | **`[SC]/[SS]/[IND]` 标注覆盖** | 3 / 10（01 零标注；02-06 仅引言；07 完整） | 9 / 10（7 标准全量三层表 + 条目级标注） | +6 | 01 RT 完全缺失；02-06 缺条目级标注；仅 07 有完整三层映射 |
| 4 | **主题域完备性** | 4 / 10（7 域，无 08/09/10） | 8 / 10（9+1 域：新增 PROTO/INTEROP/GOV） | +4 | 无协议对接域；无互操作域；无治理章程 |
| 5 | **协议生态对接** | 2 / 10（零提及 MCP/A2A/AG-UI/ANP/LangGraph/CrewAI） | 8 / 10（08 PROTO + 09 INTEROP + LangGraph/CrewAI 映射 + 桥接映射） | +6 | 4409 行零行业协议提及；无 JSON-RPC 2.0 桥接；无 AgentCard 发布；无 LangGraph/CrewAI 对接 |
| 6 | **许可证与专利** | 3 / 10（AGPL+Apache，无 OWFa） | 9 / 10（CC-BY-4.0 规范 + Apache-2.0 实现 + OWFa 1.0 专利） | +6 | 许可证未分离；无专利不主张承诺；无 OpenChain 合规 |
| 7 | **治理成熟度** | 2 / 10（SPHARX 单一主导，无分级孵化，无独立法律实体） | 7 / 10（CNCF 三级孵化 + 公开 RFC + CoC + CLA + SPHARX 否决权限制） | +5 | 无 Sandbox/Incubating/Graduated；无 TOC；无 CoC；商标归单一公司；无独立法律实体 |
| 8 | **形式化规范** | 1.5 / 10（仅 01 RT 内嵌 JSON Schema；无 Protobuf/TLA+/Isabelle） | 6 / 10（独立 JSON Schema + Protobuf IDL + Isabelle/HOL 基线） | +4.5 | 无独立 schema 文件；无 Protobuf IDL；"借鉴 seL4"零形式化实践 |
| 9 | **参考实现可追溯** | 2 / 10（无独立参考实现仓库，README 第 144 行虚假承诺） | 7 / 10（agentrt 参考实现 + 兼容性测试套件仓库 + 条目-代码映射） | +5 | 测试用例内嵌文档；无独立 conformance 套件；README 第 144 行声明与事实不符 |
| 10 | **行业对齐度（2026 H1）** | 2 / 10（完全置身生态之外） | 8 / 10（对接 MCP/A2A/IAIP + OCI-AI v1.3 + T/CAMETA + LangGraph/CrewAI） | +6 | MCP 无状态化、A2A 签名卡、IAIP 五草案、OCI-AI 强制、T/CAMETA 国标、LangGraph/CrewAI 编排均未对齐 |
| 11 | **README 文档完整性**（v1.1 新增） | 3 / 10（头部版本回退 1.0 vs 1.1；"六大领域"错描述；第 231 行断裂引用；第 144 行虚假承诺） | 9 / 10（版本一致 + 域数正确 + 引用全部有效 + 虚假承诺修正） | +6 | 4 处内部不一致 + 1 处断裂引用 + 1 处虚假承诺 |
| 12 | **可独立实现性**（v1.1 新增） | 3 / 10（11 项数据结构仅 27% 语言中立；第三方无法仅依据规范独立实现） | 8 / 10（独立 JSON Schema + Protobuf IDL + Python/Rust 绑定 + 第三方独立实现验证） | +5 | 所有数据结构以 C `struct` 定义；过度依赖 C 语言 API 签名；无 IDL |
| | **综合加权均分** | **2.6 / 10** | **7.9 / 10** | **+5.3** | — |

> **评分依据**：每维度按 10 分制，依据证据条目数与严重等级加权。v2.0 基线分数反映"研究已识别问题但未落地"的实际状态；v2.1 目标分数反映"本报告优化方案全部落地后的预期状态"。

### 1.3 v2.1 核心诉求（一句话）

在**不破坏既有 7 域 L1 永久稳定契约**的前提下，**强制统一错误码 SSoT、强制统一 `airy_cap_t` 命名、强制补齐 `[SC]/[SS]/[IND]` 三层标注、新增 08 PROTO / 09 INTEROP / 10 GOV 三主题域、对接 MCP 2026-07-28 与 A2A v1.2 与 IETF IAIP、引入 OWFa 1.0 专利授权与 CNCF 三级孵化治理**，使本体系从"自洽草案"演进为"可被第三方独立实现并受法律与社区双重保护的开放标准"。

### 1.4 v2.1 四阶段路径概述

| 阶段 | 版本跃迁 | 工期 | 核心交付 | 风险等级 |
|------|---------|------|---------|---------|
| **阶段 1：技术一致性强制修复** | 1.1 → 1.2 | ~2 周 | 错误码 SSoT 统一 + `airy_cap_t` 全量改名 + `[SC]/[SS]/[IND]` 三层标注补齐 + README 版本一致性修复 | 低 |
| **阶段 2：协议生态对接** | 1.2 → 2.0 | ~5 周 | 新增 08 PROTO / 09 INTEROP 两域，对接 MCP 2026-07-28 + A2A v1.2 + IETF IAIP，修订 02 IPC JSON-RPC 2.0 桥接 | 中 |
| **阶段 3：治理与许可升级** | 2.0 → 2.1 | ~4 周 | OWFa 1.0 专利授权 + CC-BY-4.0 规范文档 + CNCF 三级孵化 + OpenChain ISO/IEC 5230 合规基线 | 中 |
| **阶段 4：形式化与参考实现** | 2.1 → 2.2 | ~8 周 | 新增 10 GOV 治理章程 + Isabelle/HOL 形式化验证基线 + 独立 conformance 测试套件仓库 | 高 |

四阶段合计 ~19 周（约 5 个月），最终在 2026 年底完成从 v1.1 到 v2.2 的整体跃迁。

***

## 2. v2.0 优化建议落地验证（逐项验证）

### 2.1 验证方法

以 `_research_v2.0/01-open-standards-optimization-v2.md`（1088 行，2026-07-13）为基线，逐项核对 v2.0 提出的 6 项优化建议在主标准文档（`docs/OpenStandards/01-` ~ `07-` + `README.md`）中的落地状态。验证手段为 Grep 全文检索 + 逐文件人工审查。

### 2.2 逐项验证结果

#### 2.2.1 验证项 1：错误码统一为 03 SEC SSoT

| 子项 | v2.0 建议 | 落地状态 | 证据 |
|------|----------|---------|------|
| 03 SEC 作为错误码 SSoT | 建立 -1~-99 通用 / -100~-199 系统 / -1100~-1199 内存 / -1200~-1299 IPC / -1300~-1399 安全 / -1600~-1699 调度 六段式 | **未落地** | 03 SEC 第 503-515 行虽有 SSoT 表，但 `AIRY_ETIMEOUT=-1004` 不在其声明的 -100~-199 系统段内（-1004 实属 -1000~-1099，SSoT 表未定义此段）——**SSoT 自身内部不一致** |
| 01 RT 对齐 SSoT | ENOMEM 应为 -1100，EPERM 应为 -1302，EBUSY 应为 -1601 | **未对齐** | 01 RT 第 580-585 行：`ENOMEM=-3`（应为 -1100）、`EPERM=-22`（应为 -1302）、`EBUSY=-16`（应为 -1601）、`EEXIST=-17`（SSoT 未定义）、`EBUDGET=-1004`（SSoT 未定义） |
| 02 IPC 对齐 SSoT | EPERM 应为 -1302，EBUSY 应为 -1601，ELIMIT 应纳入 SSoT | **部分对齐** | 02 IPC 第 458-464 行：`EPERM=-22`（应为 -1302）、`EBUSY=-16`（应为 -1601）、`ELIMIT=-7`（SSoT 未定义）、`EMSGSIZE=-1201`（对齐 ✓）、`ENOMSG=-1202`（对齐 ✓） |
| 04 MEM 对齐 SSoT | ENOENT=-2 应改值避免与 EINVAL 冲突，EMSGSIZE 应为 -1201 | **未对齐** | 04 MEM 第 512-517 行：`ENOENT=-2`（**与 EINVAL=-2 冲突，严重 BUG**）、`EMSGSIZE=-1109`（应为 -1201，跑到了内存段）、`EIO=-5`（SSoT 未定义）、`EPERSIST=-1101`（SSoT 未定义） |
| 05 COG 对齐 SSoT | EBUDGET 与 ETIMEOUT 不能同值 | **未对齐，存在致命 BUG** | 05 COG 第 411-412 行：`EBUDGET=-1004` AND `TIMEOUT=-1004`——**两个不同语义错误码取相同值，调用方无法区分 Token 耗尽与超时** |
| 06 SCHED 对齐 SSoT | ENOENT=-2 应改值 | **未对齐** | 06 SCHED 第 455 行：`ENOENT=-2`（**与 EINVAL=-2 冲突**） |
| 07 SYS 对齐 SSoT | 应放弃 -1~-12 独立方案，对齐 03 SEC | **完全未对齐，采用第三套方案** | 07 SYS 第 415-426 行：`EINVAL=-1`（应为 -2）、`ENOMEM=-2`（应为 -1100）、`EPERM=-4`（应为 -1302）、`EBUSY=-9`（应为 -1601）、`ETIMEOUT=-11`（应为 -1004）——**07 SYS 是第三套完全独立的错误码方案** |

**验证结论**：错误码统一**完全未落地**。当前存在三套方案：
- 方案 A（01 RT / 02 IPC）：`EINVAL=-2, ENOMEM=-3, EPERM=-22, EBUSY=-16`，接近 POSIX errno 风格
- 方案 B（03 SEC / 04 MEM / 06 SCHED）：分段式 `-1100/-1201/-1302/-1601`，但 SSoT 表自身不一致且 04/06 有 ENOENT=-2 冲突
- 方案 C（07 SYS）：`-1~-12` 连续小整数，完全独立，声称"对齐 `airy_errno.h`"但与 03 SEC SSoT 毫无关系

**严重等级**：致命。三套方案并存 + 两个值冲突 + 一个双码同值，使错误码无法作为可靠契约。

#### 2.2.2 验证项 2：`are_cap_t` → `airy_cap_t` 命名统一

| 子项 | v2.0 建议 | 落地状态 | 证据 |
|------|----------|---------|------|
| 03 SEC 定义源修正 | `are_cap_t` 改为 `airy_cap_t` | **未落地** | 03 SEC 第 66/79/81/189/190/195/210/211/225/251/351/352/353/357/358/361/363/367/368/369/545/556 行共 22 处仍为 `are_cap_t`（v1.0 草案原计 17 处，经 Grep 复核实为 22 处，下文合计同步修正为 34 处） |
| 01 RT 引用修正 | `are_cap_t net_cap, ipc_cap` 改为 `airy_cap_t` | **未落地** | 01 RT 第 501 行仍为 `are_cap_t` |
| 02 IPC 引用修正 | 3 处 `are_cap_t` 改为 `airy_cap_t` | **未落地** | 02 IPC 第 282/287/305 行仍为 `are_cap_t` |
| 07 SYS 第三变体 | v2.0 未提及 07 SYS 的 `cap_t` 变体 | **新发现问题** | 07 SYS 第 207/224/241/258/275/293/326/400 行共 8 处使用 `cap_t`（无 `airy_` 前缀，亦无 `are_` 前缀）——**第三种命名变体** |
| 函数前缀对齐 | `airy_cap_mint` 等函数已用 `airy_` 前缀 | **已对齐** | 03 SEC 第 189/195/210/225 行函数名均为 `airy_cap_*`——但类型名 `are_cap_t` 与函数名 `airy_cap_*` 不一致，更显突兀 |

**验证结论**：命名统一**完全未落地**，且发现 v2.0 未识别的第三种变体 `cap_t`（07 SYS）。当前存在三种类型名：
- `are_cap_t`（03 SEC 定义源 + 01 RT + 02 IPC 引用，共 26 处：03 SEC 22 处 + 01 RT 1 处 + 02 IPC 3 处）
- `cap_t`（07 SYS 独有，共 8 处）
- `airy_cap_t`（正确形式，**当前标准文档中零使用**）

**严重等级**：高。capability 是安全模型的核心类型，三套命名使跨标准引用无法通过编译。

#### 2.2.3 验证项 3：`[SC]/[SS]/[IND]` 标注在 01/05/06 补齐

| 文档 | v2.0 建议 | 落地状态 | 证据 |
|------|----------|---------|------|
| 01 RT | 补 `[SC]` 引言 + 三层映射表 | **未落地** | 01 RT 全文 610 行**零处** `[SC]/[SS]/[IND]` 标注（Grep 确认） |
| 02 IPC | 补条目级 `[SC]` 标注 | **部分落地** | 02 IPC 第 28 行有 `[SC]` 引言，但无条目级标注、无三层表 |
| 03 SEC | 补条目级 `[SC]` 标注 | **部分落地** | 03 SEC 第 28 行有 `[SC]` 引言，但无条目级标注、无三层表 |
| 04 MEM | 补条目级 `[SC]` 标注 | **部分落地** | 04 MEM 第 28 行有 `[SC]` 引言，但无条目级标注、无三层表 |
| 05 COG | 补 `[SC]` 引言 + 三层映射表 | **部分落地** | 05 COG 第 28 行有 `[SC]` 引言（v2.0 建议已部分采纳），但无三层表、无条目级标注 |
| 06 SCHED | 补 `[SC]` 引言 + 三层映射表 | **部分落地** | 06 SCHED 第 29 行有 `[SC]` 引言，但无三层表、无条目级标注 |
| 07 SYS | 保持完整（标杆） | **已完整** | 07 SYS 第 30 行引言 + 第 410 行内联 + 第 635-637 行完整三层表（[SC]/[SS]/[IND] 全覆盖） |
| README | 三层模型定义 | **已存在** | README 第 58-64 行定义三层模型 |

**验证结论**：`[SC]/[SS]/[IND]` 标注**部分落地**。01 RT 完全缺失（最严重）；02-06 仅有引言一句话，缺少条目级标注与三层映射表；仅 07 SYS 达到完整覆盖，可作为其他 6 标准的补齐模板。

**严重等级**：中。不影响功能，但使"同源共享"承诺无法被实现者验证。

#### 2.2.4 验证项 4：9+1 主题体系（新增 08/09/10）

| 子项 | v2.0 建议 | 落地状态 | 证据 |
|------|----------|---------|------|
| 新增 08 PROTO（协议对接域） | v2.0 提议 PROTO 域承载 MCP/A2A 桥接 | **未落地** | `docs/OpenStandards/` 下无 `08-*.md` 文件 |
| 新增 09 INTEROP（互操作域） | v2.0 提议 INTEROP 域承载跨运行时互操作 | **未落地** | 无 `09-*.md` 文件 |
| 新增 10 GOV（治理章程） | v2.0 未明确提议 10，但治理升级属阶段 3 | **未落地** | 无 `10-*.md` 文件 |
| README 文档清单更新 | 应列入 08/09/10 | **未更新** | README 第 72-81 行仅列 7 标准（01-07） |
| README 域数描述 | "六大领域"应改为"九大领域" | **未修正，且存在新 BUG** | README 第 14 行仍为"六大领域"——但实际已有 7 域（RT/IPC/SEC/MEM/COG/SCHED/SYS），**"六大"本身即错误，应为"七大"** |

**验证结论**：9+1 主题体系**完全未落地**。08/09/10 三文档均不存在，README 文档清单未更新，且 README 第 14 行"六大领域"描述与实际 7 域不符（即便不算新增域，现有域数描述也是错的）。

**严重等级**：高。无协议对接域与互操作域是本体系置身行业生态之外的根本原因。

#### 2.2.5 验证项 5：许可证变更为 Apache-2.0-only 或 CC-BY-4.0

| 子项 | v2.0 建议 | 落地状态 | 证据 |
|------|----------|---------|------|
| 规范文档许可分离 | 规范文档用 CC-BY-4.0，参考实现用 Apache-2.0，测试套件用 Apache-2.0 | **未落地** | 全部 8 文件第 8 行均为 `SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0` |
| AGPL 移除 | 规范文档不应使用 AGPL（限制企业引用） | **未落地** | 8 文件均保留 AGPL-3.0-or-later |
| README 双许可说明 | README 第 18-21 行说明双许可理由 | **未修订** | README 仍以"AGPL 保障回流 + Apache 允许闭源"为双许可辩护 |

**验证结论**：许可证变更**完全未落地**。8 文件统一保留 `AGPL-3.0-or-later OR Apache-2.0`，未实现规范/实现/测试三产物许可分离。

**严重等级**：高。AGPL 网络服务条款阻碍企业引用规范文档，是与 OCI / CNCF / seL4 治理模式不对齐的根本障碍。

#### 2.2.6 验证项 6：MCP / A2A / OpenTelemetry 互操作声明

| 子项 | v2.0 建议 | 落地状态 | 证据 |
|------|----------|---------|------|
| 02 IPC 增加 MCP JSON-RPC 2.0 桥接章节 | v2.0 提议 02 IPC 新增第 14 章 MCP 桥接 | **未落地** | 02 IPC 仅 551 行，无第 14 章；第 157 行一笔带过 JSON-RPC 2.0，无桥接契约 |
| 01 RT 增加 A2A AgentCard 发布章节 | v2.0 提议 01 RT 新增第 12 章 AgentCard 发布 | **未落地** | 01 RT 仅 610 行、11 章，无第 12 章 |
| OpenTelemetry trace 上下文传播 | v2.0 提议 IPC 消息头携带 traceparent | **未落地** | 02 IPC 第 77/100 行仅提及 OpenTelemetry 名词，无 trace 上下文契约 |
| 02 IPC 新增 AOS-STD-IPC-024~030 | v2.0 提议 7 条 MCP 桥接标准条目 | **未落地** | 02 IPC 最后条目为 AOS-STD-IPC-028，无 024~030 MCP 桥接条目 |
| 01 RT 新增 AOS-STD-RT-025~028 | v2.0 提议 4 条 A2A 桥接标准条目 | **未落地** | 01 RT 最后条目为 AOS-STD-RT-024，无 025~028 A2A 桥接条目 |

**验证结论**：互操作声明**完全未落地**。MCP / A2A / OpenTelemetry 在 8 文件中仅作为名词出现，无任何桥接契约、标准条目或章节。

**严重等级**：致命。这是本体系"完全置身于 2026 年 AI Agent 协议生态之外"的直接证据。

### 2.3 v2.0 落地验证总结

| 验证项 | v2.0 建议 | 落地状态 | 严重等级 |
|--------|----------|---------|---------|
| 1. 错误码统一 SSoT | 03 SEC 作为 SSoT，6 标准对齐 | **完全未落地**（三套方案 + 双码同值 + 值冲突） | 致命 |
| 2. `are_cap_t` → `airy_cap_t` | 全量改名 | **完全未落地**（发现第三变体 `cap_t`） | 高 |
| 3. `[SC]/[SS]/[IND]` 补齐 | 01/05/06 补三层表 | **部分落地**（01 零标注，02-06 仅引言，07 完整） | 中 |
| 4. 9+1 主题体系 | 新增 08/09/10 | **完全未落地**（三文件均不存在） | 高 |
| 5. 许可证变更 | CC-BY-4.0 + Apache-2.0 分离 | **完全未落地**（仍 AGPL+Apache） | 高 |
| 6. 互操作声明 | MCP/A2A/OTel 桥接 | **完全未落地**（零桥接契约） | 致命 |

**总体结论**：v2.0 的 6 项优化建议**落地率 0/6**（仅 `[SC]` 引言在 02-06 有部分采纳，但条目级标注与三层表均未补齐）。当前主标准文档仍处于 v1.1 草案状态，且因 07 SYS 引入第三套错误码方案与第三种命名变体，技术一致性**比 v2.0 研究时更差**。

### 2.4 P1/P2 级问题补充验证（v1.1 新增）

v1.0 草稿聚焦于 v2.0 提出的 6 项优化建议落地情况，但对 v1.0 重建方案识别的 P1/P2 级问题（README 断裂引用、形式化规范、参考实现、可独立实现性）未独立验证。本节补充验证。

#### 2.4.1 P2-1：README 第 231 行断裂引用

| 子项 | v1.0/v2.0 建议 | 落地状态 | 证据 |
|------|--------------|---------|------|
| README 第 231 行 TERMINOLOGY.md 引用 | 应修正路径 | **未修正** | README 第 231 行：`docs/AirymaxOS/TERMINOLOGY.md`——经 `find` 验证，`docs/AirymaxOS/TERMINOLOGY.md` **不存在**；实际文件位于 `docs/AirymaxRT/TERMINOLOGY.md`（agentrt 而非 AirymaxOS） |
| README 第 232-236 行其他引用 | 应一并核对 | **疑似多出处断裂** | README 第 232 行引用 `docs/AirymaxOS/50-engineering-standards/00-engineering-standards-handbook.md`，第 233 行引用 `docs/AirymaxOS/10-architecture/02-five-dimensional-principles.md`，第 234-236 行引用 `docs/AirymaxOS/50-engineering-standards/20-contracts/` 与 `30-runtime-interfaces/`——这些路径是否实际存在需逐一 `find` 验证 |

**严重等级**：中-高。README 是标准体系的"门面"，断裂引用使第三方实现者无法找到术语表与工程标准，直接阻碍采纳。

**修正方案**：将 README 第 231 行 `docs/AirymaxOS/TERMINOLOGY.md` 改为 `docs/AirymaxRT/TERMINOLOGY.md`，并核对其他 4 处引用路径。

#### 2.4.2 P1-3：形式化规范（JSON Schema / Protobuf IDL）

v1.0 重建方案要求"分离语义规范与语言绑定"，并建议引入 JSON Schema 与 Protobuf IDL 作为跨语言形式化规范。验证如下：

| 形式化类型 | 当前状态 | 落地情况 | 证据 |
|----------|---------|---------|------|
| **JSON Schema** | 仅 01 RT 内嵌一段 Agent 元数据 JSON Schema | **部分存在，但非独立文件** | 01 RT 第 184-289 行有 Agent 元数据 JSON Schema（AOS-STD-RT-010，L2 稳定级），引用 JSON Schema Draft 2020-12；但无独立 `.json` 文件，仅作为 Markdown 代码块嵌入。02 IPC 的 128B 消息头、03 SEC 的 capability 令牌、06 SCHED 的任务描述符均无 JSON Schema 描述（这些是二进制结构，本不适配 JSON Schema） |
| **Protobuf IDL** | 完全不存在 | **完全未落地** | Grep 检索 `Protobuf`/`.proto`/`protobuf` 在 8 文件中返回 0 结果。02 IPC 的 5 种 payload 类型（REQUEST/RESPONSE/EVENT/STREAM/NOTIFICATION）本适合 Protobuf IDL 描述，但仅以 C 结构体 + 文字描述 |
| **TLA+ / Isabelle/HOL** | 完全不存在 | **完全未落地** | 见本报告 3.4 节形式化规范审查 |
| **CBOR / FlatBuffers / Cap'n Proto** | 完全不存在 | **完全未落地** | 02 IPC 仅规定 C 结构体 + 字节布局，无任何语言无关的二进制序列化规范 |

**严重等级**：高。当前所有数据结构均以 C 语言 `struct` 定义，使标准实质上是"C 语言绑定标准"而非"语言无关规范"。这与 OCI runtime-spec（JSON Schema）、gRPC（Protobuf IDL）、MCP（JSON Schema）等行业标准形成鲜明对比。

**最小可行方案**：
1. 01 RT Agent 元数据 JSON Schema 抽取为独立 `schemas/agent-metadata.schema.json` 文件。
2. 02 IPC 5 种 payload 类型补充 Protobuf IDL 定义（`proto/airy_ipc.proto`），与 C 结构体双向映射。
3. 03 SEC capability 令牌补充字节布局形式化约束（如 `_Static_assert` 表达式或 FlatBuffers schema）。

#### 2.4.3 P1-4：参考实现可追溯性

v1.0 重建方案要求"发布独立、最小化、可编译的参考实现"。验证如下：

| 维度 | 当前状态 | 证据 |
|------|---------|------|
| 独立参考实现仓库 | **不存在** | `docs/OpenStandards/` 下无 `reference-implementation/` 或 `examples/` 目录；agentrt / agentrt-linux 仓库未在 OpenStandards 中链接 |
| 最小化可编译样例 | **不存在** | 8 文件中的示例代码均为片段（如 01 RT 第 515 行 `hdr.magic = AIRY_IPC_MAGIC;`），无完整可编译 `.c` 文件 |
| 标准条目 ↔ 实现代码映射 | **不存在** | 无 `@standard AOS-STD-RT-001` 等 Doxygen/kernel-doc 标签；07 SYS 第 559-565 行有 kernel-doc 注释但未映射到 AOS-STD-* 编号 |
| 独立 conformance 测试套件 | **不存在** | 见本报告 3.3 节认证可操作性审查 |

**严重等级**：高。无独立参考实现使第三方无法验证标准的可实现性，也无法通过"实现先行原则"约束标准演进。

#### 2.4.4 P1-1：兼容性认证可操作性

v1.0 重建方案要求"发布可执行兼容性测试套件"。验证如下：

| 子项 | 当前状态 | 证据 |
|------|---------|------|
| 三级认证定义 | **已定义但不可操作** | README 第 126-130 行定义 Airymax Certified / Compatible / Inspired 三级，但"全套兼容性测试套件"未独立存在 |
| 测试维度定义 | **已定义** | README 第 134-142 行定义 5 维度（二进制兼容、语义兼容、行为兼容、错误码兼容、安全兼容），每维度标注"必须通过" |
| 测试用例条目 | **存在于各标准附录** | 如 02 IPC 有 IPC-T-001~008、03 SEC 有 SEC-T-001~005、06 SCHED 有 SCHED-T-001~008 等条目式描述 |
| 可执行测试代码 | **完全不存在** | 所有测试用例均为文字描述（如"128 字节，magic 匹配"），无任何可执行测试代码 |
| 测试套件独立仓库 | **不存在** | README 第 144 行声明"测试套件代码以 Apache-2.0 许可证发布"，但实际无独立仓库、无代码——**声明与事实不符** |
| 认证流程操作指南 | **不存在** | 无"如何申请 Certified""审计周期""费用""申诉流程"等操作细节 |

**严重等级**：高。README 第 144 行的"测试套件代码以 Apache-2.0 许可证发布"声明构成**虚假承诺**——代码根本不存在。这比"无测试套件"更严重，因为前者误导采纳者。

#### 2.4.5 治理流程 SPHARX 中心化深化分析

v1.0 重建方案要求"治理流程多利益相关方参与"。验证如下：

| 治理维度 | 当前状态 | 行业标杆 | 差距 |
|---------|---------|---------|------|
| 标准委员会组织方 | "由 SPHARX Ltd. 组织"（README 第 162 行） | OCI TOB 由项目维护者选举 / CNCF TOC 由社区选举 | **单一公司主导**，无独立法律实体 |
| 标准总维护者 | "SPHARX 任命，最终裁决权"（v2.0 第 4.3.1 节） | OCI Chair 由 TOB 选举 / CNCF TOC Chair 由社区选举 | **单一公司任命**，无社区制衡 |
| 标准委员会构成 | 1 总维护者 + 7 主题域维护者 + 社区代表（README 第 162-166 行） | OCI 9 人 TOB（选举产生，任期 2 年） / CNCF 多利益相关方 TOC | 社区代表"每届任期 1 年"过短，且无明确选举机制 |
| 商标持有方 | SPHARX Ltd.（隐含） | OCI Trademark Board / CNCF 商标归 Linux Foundation | 商标归单一公司，认证体系法律风险高 |
| 法律实体 | 无独立法律实体 | OCI（LF 旗下）/ CNCF（LF 旗下）/ AAIF（LF 旗下） | 无独立法律实体意味着 SPHARX 承担无限责任 |
| RFC 公示渠道 | "Airymax 标准仓库"（README 第 154 行） | GitHub Discussions + 邮件列表 + 公告板 | 仅仓库内 RFC，无邮件列表、无公告板 |
| 行为准则 | 不存在 | LF CoC / CNCF CoC / Contributor Covenant 2.1 | 无 CoC 使社区参与缺乏行为约束 |
| CLA/DCO | 不存在 | CNCF DCO + CLA / OCI CLA | 无 CLA 使贡献者法律地位不清 |

**严重等级**：致命。SPHARX 单一公司主导治理使本体系无法被认定为"开放标准"——按 [OpenStand 现代范式](https://open-stand.org/about-us/principles/)的"透明、共识、可用、自愿"四原则，单一公司任命维护者 + 单一公司持有商标 + 无独立法律实体的组合，实质上是"公司开放标准"而非"行业开放标准"。

**最小可行方案**：
1. 阶段 3 将标准委员会重组为"1 标准总维护者（SPHARX 任命，但仅保留否决权）+ 9 主题域维护者（社区选举）+ 3 社区代表（选举）+ 1 企业代表（轮换）+ 1 法务顾问（列席）"——v2.0 报告第 4.3.1 节已提出此方案，但需明确"SPHARX 仅保留否决权而非最终裁决权"。
2. 阶段 4 商标转移到独立法律实体（如未来 AAIF 或自建 Airymax Foundation）。
3. 阶段 3 引入 Contributor Covenant 2.1 + DCO + 个人 CLA。

***

## 3. 当前方案全面审查（按 5 维度评估）

### 3.1 维度 1：设计文档与标准条目关系

#### 3.1.1 L1-L4 稳定性分级覆盖

| 稳定级 | 定义 | 当前覆盖 | 问题 |
|--------|------|---------|------|
| L1 永久稳定 | MAJOR 版本内不可变更 | 01-07 共 ~84.5% 条目声明 L1 | **过度承诺**：L1 比例过高（04 MEM 100%、01 RT 87.5%），但错误码、命名等本应 L1 的契约反而不一致，L1 声明与实际稳定性不符 |
| L2 弃用流程 | 至少 2 版本弃用期 | 运行时接口、能力令牌格式 | **无弃用实例**：当前无任何条目处于弃用期，弃用流程未被实践验证 |
| L3 版本协商 | version 字段协商 | 内部 API、payload 扩展字段 | **协商机制未定义**：02 IPC 消息头有 version 字段（第 6-7 字节），但未定义协商规则（新旧版本如何降级） |
| L4 完全自由 | 随意变更 | 未明确 | **L4 未使用**：无任何条目声明 L4，分级体系实际只用了 L1-L3 |

#### 3.1.2 设计文档与标准条目的 SSoT 关系

| 数据结构 | SSoT 声明位置 | 跨文档引用一致性 | 问题 |
|---------|-------------|----------------|------|
| `airy_ipc_msg_hdr`（128B 消息头） | 02 IPC 第 1 章 + 引用 `include/airymax/ipc.h` | 07 SYS 第 635 行引用 `ipc.h`（对齐 ✓） | 良好，但 01 RT / 03 SEC 未显式引用 SSoT 头文件 |
| `airy_task_desc`（128B 任务描述符） | 06 SCHED 第 3 章 | 07 SYS 第 635 行引用 `sched.h`（对齐 ✓） | 良好 |
| capability 令牌（64B） | 03 SEC 第 3 章 | 01 RT / 02 IPC 引用 `are_cap_t`（命名不一致 ✗） | **类型名 SSoT 失效**：SSoT 定义为 `are_cap_t`，07 SYS 用 `cap_t`，正确应为 `airy_cap_t` |
| 错误码 | 03 SEC 第 503-515 行声称 SSoT | 01/02/04/05/06/07 均未遵循 | **SSoT 完全失效**（见 2.2.1） |
| CoreLoopThree 三阶段 | 05 COG 第 3 章 | 06 SCHED `cog_phase` 字段对齐 05 枚举（对齐 ✓） | 良好 |

#### 3.1.3 设计文档关系审查结论

- **良好**：IPC 消息头、任务描述符、CoreLoopThree 三阶段的跨文档 SSoT 引用基本对齐。
- **失效**：capability 类型名 SSoT 失效（三种变体）、错误码 SSoT 完全失效（三套方案）。
- **过度承诺**：L1 比例 ~84.5% 过高，但 L1 契约（错误码、命名）实际不稳定，L1 声明与事实不符。
- **缺失**：无弃用实例、无版本协商规则、L4 未使用。

### 3.2 维度 2：编号一致性

#### 3.2.1 AOS-STD-<域>-<NNN> 编号体系

| 域 | 代号 | 当前最大编号 | v2.0 预留段 | 问题 |
|----|------|------------|------------|------|
| RT（运行时） | RT | AOS-STD-RT-024 | 025~028（A2A 桥接，未落地） | 编号连续，无空洞 |
| IPC（进程间通信） | IPC | AOS-STD-IPC-028 | 024~030（MCP 桥接，未落地） | **编号回退风险**：v2.0 预留 024~030，但当前已用到 028，预留段与已用段重叠 |
| SEC（安全模型） | SEC | AOS-STD-SEC-027 | — | 编号连续 |
| MEM（记忆卷载） | MEM | AOS-STD-MEM-021 | — | 编号连续 |
| COG（认知循环） | COG | AOS-STD-COG-016 | — | 编号连续 |
| SCHED（调度） | SCHED | AOS-STD-SCHED-031 | — | 编号连续 |
| SYS（系统调用） | SYS | AOS-STD-SYS-028（含性能约束 025-027） | — | 07 SYS 第 473 行提及 AOS-STD-SYS-028（TIMEOUT 触发），但第 6 章错误码表止于 SYS-024，**编号 028 是否存在需核对** |

#### 3.2.2 编号一致性审查结论

- **IPC 预留段冲突**：v2.0 预留 IPC-024~030 用于 MCP 桥接，但当前 IPC 已用到 028，若落地 MCP 桥接需从 029 起编号，预留段规划失效。
- **SYS 编号断档**：07 SYS 错误码条目止于 SYS-024，但第 473 行引用 SYS-028，中间 025-027 为性能约束条目，编号跨章节连续性需核实。
- **无全局编号注册表**：7 标准各自的编号独立递增，无单一注册表可查全量条目数与归属，与项目记忆中"全局唯一规则编号注册表（SSoT）"要求不符。

### 3.3 维度 3：认证可操作性

#### 3.3.1 兼容性认证体系

| 认证层级 | 当前定义 | 可操作性 | 问题 |
|---------|---------|---------|------|
| Airymax Certified | 完全遵循本体系全部 L1 条目 | **不可操作** | 无独立测试套件仓库，测试用例内嵌文档，第三方无法运行 conformance 检查 |
| Airymax Compatible | 遵循核心 L1 子集 | **不可操作** | "核心 L1 子集"未明确定义哪些条目属于核心 |
| Airymax Inspired | 借鉴部分理念 | **不可操作** | 无量化标准，纯主观判断 |

#### 3.3.2 测试套件现状

- **位置**：测试用例内嵌于各标准文档的"示例代码"章节，无独立仓库。
- **许可证**：随文档采用 AGPL-3.0-or-later OR Apache-2.0，未分离。
- **可执行性**：示例代码为伪代码 / 片段，无法编译运行，无 conformance runner。
- **覆盖度**：无测试用例与标准条目的映射矩阵，无法判断哪些条目有测试覆盖。

#### 3.3.3 认证可操作性审查结论

- **三级认证均不可操作**：无独立测试套件、无 conformance runner、无条目-测试映射矩阵。
- **对标差距**：OCI 有独立 conformance 套件（Apache-2.0）、CNCF 项目需通过第三方安全审计、seL4 有 Isabelle/HOL 形式化证明，本体系在这三方面均为零。
- **最小可行方案**：v2.1 阶段 4 应建立独立 `airymax-conformance` 仓库（Apache-2.0），实现至少 24 条 L1 核心条目的可执行测试。

### 3.4 维度 4：形式化规范

#### 3.4.1 当前形式化程度

| 标准条目 | 形式化程度 | 问题 |
|---------|----------|------|
| 01 RT 生命周期状态机 | ASCII 状态图 + 文字描述 | 无形式化状态机定义（如 TLA+ / Statecharts） |
| 01 RT Agent 元数据 | JSON Schema Draft 2020-12（嵌入 Markdown） | **部分形式化**：第 184-289 行有 JSON Schema，但无独立 `.json` 文件，未提供 schema 验证器 |
| 02 IPC 128B 消息头 | C 结构 + 字节布局图 | 字节布局为"概念示意"（06 SCHED 第 166 行明示），无形式化字节布局约束；无 Protobuf IDL |
| 02 IPC 5 种 payload 类型 | C 结构 + 文字描述 | 无 Protobuf IDL，无 FlatBuffers schema，无任何语言无关序列化规范 |
| 03 SEC Cupolas capability 派生 | 文字 + 伪代码 | 派生关系无形式化偏序集定义，mint/derive 的权限子集判定无形式化规则 |
| 06 SCHED vtime 衰减公式 | 数学公式 + Q16.16 定点 | 公式有定义，但无形式化公平性定理（如 CFS 的 lag boundedness） |
| 07 SYS syscall 语义 | C 签名 + 文字描述 | 无形式化前置/后置条件（pre/post conditions），无 seL4 级的 Isabelle/HOL 证明 |

#### 3.4.2 与 seL4 形式化验证的差距

| 维度 | seL4 | Airymax | 差距 |
|------|------|---------|------|
| 形式化语言 | Isabelle/HOL（~50 万行证明） | 无 | 致命 |
| 验证定理 | 功能正确性 + 完整性 + 机密性 | 无 | 致命 |
| 03 SEC / 07 SYS 声称"借鉴 seL4" | — | 仅设计理念借鉴，零形式化实践 | **宣传与实际严重不符** |

#### 3.4.3 与 OCI / gRPC / MCP 的形式化规范差距（v1.1 新增）

| 形式化类型 | OCI runtime-spec | gRPC / A2A | MCP 2026-07-28 | Airymax | 差距 |
|----------|-----------------|-----------|---------------|---------|------|
| JSON Schema | ✅ 独立 `.json` 文件 | — | ✅ Tools 入参完整 JSON Schema 2020-12 | ⚠️ 仅 01 RT 内嵌一段 | **无独立 schema 文件** |
| Protobuf IDL | — | ✅ `.proto` 文件 | — | ❌ 完全不存在 | **02 IPC payload 类型缺 IDL** |
| 字节布局形式化 | ✅ digest/manifest 字段形式化 | — | — | ❌ 仅"概念示意"（06 SCHED 第 166 行） | **128B 头布局未形式化约束** |
| TLA+ / Isabelle/HOL | — | — | — | ❌ 完全不存在 | 见 3.4.2 |

#### 3.4.4 形式化规范审查结论

- **当前形式化程度极低**：仅 01 RT 有一段嵌入 JSON Schema，其余全部为自然语言 + C 伪代码。
- **"借鉴 seL4"声明缺乏支撑**：03 SEC 第 1.3 节、07 SYS 第 1.3 节均声称"seL4 最小完备"，但无 Isabelle/HOL 或任何定理证明器实践。
- **语言绑定性**：所有数据结构均以 C 语言 `struct` 定义，使标准实质上是"C 语言绑定标准"，与 OCI（JSON Schema）、gRPC（Protobuf）、MCP（JSON Schema）的"语言无关规范 + 多语言绑定"模式形成鲜明对比。
- **v2.1 最小目标**：
  1. 对 01 RT 生命周期状态机、03 SEC capability 派生偏序、06 SCHED vtime 公平性三项核心契约，提供 TLA+ 或 Isabelle/HOL 规范声明（不必完成完整证明，但需有规范文件）。
  2. 01 RT Agent 元数据 JSON Schema 抽取为独立 `schemas/agent-metadata.schema.json` 文件。
  3. 02 IPC 5 种 payload 类型补充 Protobuf IDL 定义（`proto/airy_ipc.proto`）。

### 3.5 维度 5：参考实现可追溯性

#### 3.5.1 参考实现现状

| 维度 | 当前状态 | 问题 |
|------|---------|------|
| 参考实现仓库 | 无独立参考实现仓库 | agentrt / agentrt-linux 尚处 0.1.1 奠基阶段，未对外公开 |
| 标准条目 ↔ 实现代码映射 | 无 | 无法验证某条 AOS-STD-* 在 agentrt 中的实现位置 |
| 测试套件可执行性 | 不可执行 | 见 3.3.2 |
| Doxygen / kernel-doc 覆盖 | 07 SYS 有 kernel-doc 注释 | 仅 07 SYS 有完整 kernel-doc，01-06 为普通注释 |

#### 3.5.2 可追溯性审查结论

- **参考实现零可追溯**：标准条目无法映射到实现代码，实现代码无法反向追溯到标准编号。
- **最小可行方案**：v2.1 阶段 4 应在 agentrt 源码中为每条 AOS-STD-* 条目添加 `@standard AOS-STD-RT-001` 等 Doxygen/kernel-doc 标签，建立双向映射。

### 3.6 全面审查综合结论

| 维度 | 评分 | 核心问题 |
|------|------|---------|
| 1. 设计文档与标准条目关系 | 4 / 10 | 错误码与 capability 命名 SSoT 失效；L1 过度承诺 |
| 2. 编号一致性 | 5 / 10 | IPC 预留段冲突；无全局编号注册表 |
| 3. 认证可操作性 | 1.5 / 10 | 三级认证均不可操作；无独立测试套件；README 第 144 行"测试套件代码以 Apache-2.0 发布"为虚假承诺 |
| 4. 形式化规范 | 1.5 / 10 | 仅 01 RT 内嵌 JSON Schema；无 Protobuf IDL；无 TLA+/Isabelle；"借鉴 seL4"无支撑 |
| 5. 参考实现可追溯 | 2 / 10 | 无参考实现仓库；无条目-代码映射；无可编译样例 |
| 6. 治理与许可（v1.1 新增） | 2 / 10 | SPHARX 单一公司主导；无独立法律实体；无 OWFa；AGPL 阻碍采纳；无 CoC/CLA/DCO |
| 7. README 文档完整性（v1.1 新增） | 3 / 10 | 第 231 行断裂引用；头部版本回退（1.0 vs 1.1）；"六大领域"错描述（实际 7 域） |
| 8. 可独立实现性（v1.1 新增） | 3 / 10 | 所有数据结构以 C `struct` 定义；过度依赖 C 语言 API 签名；语言不中立性不足（见 5.4） |
| **综合** | **2.6 / 10** | — |

***

## 4. 行业最新发展状况对标分析（2026 H1）

### 4.1 MCP（Model Context Protocol）2026-07-28 Release Candidate

| 属性 | 值 |
|------|---|
| **创建方** | Anthropic（2024 年 11 月） |
| **当前治理** | Linux Foundation AI Alliance（2025 年 12 月捐赠） |
| **当前稳定版** | 2025-11-25 |
| **下一版本** | 2026-07-28 Release Candidate |
| **协议格式** | JSON-RPC 2.0 |
| **架构** | Host-Client-Server（借鉴 LSP） |
| **传输** | stdio + Streamable HTTP（取代 HTTP+SSE） |
| **认证** | OAuth 2.1 with PKCE（远程服务器） |
| **核心原语** | Resources（数据）、Tools（函数）、Prompts（模板） |
| **客户端能力** | Elicitation（向用户索取信息） |
| **2026-07-28 主要变更** | 协议层无状态化、Extensions 一等公民、Tasks 与 MCP Apps 转正、授权硬化、形式化弃用政策、W3C Trace Context 集成 |
| **官方规范 URL** | https://modelcontextprotocol.io/specification/latest/index |

**关键变更解读**：

1. **协议层无状态化**：MCP 2026-07-28 将协议核心定义为无状态，状态管理下沉至 Host/Client 层。这与本体系 02 IPC 的 128B 有状态消息头设计形成对比——本体系 IPC 是 Agent 间有状态通信，MCP 是 Agent↔Tool 无状态通信，两者层次互补。

2. **Extensions 一等公民**：Extensions 从实验特性转正，允许第三方定义扩展原语而不污染核心协议。本体系 02 IPC 的 payload 扩展字段（version 协商）应借鉴此模式。

3. **W3C Trace Context 集成**：MCP 2026-07-28 原生支持 W3C Trace Context（`traceparent` / `tracestate`），与本体系 02 IPC 第 77/100 行仅提及 OpenTelemetry 名词形成鲜明对比——本体系应将 traceparent 纳入 IPC 消息头扩展字段。

4. **形式化弃用政策**：MCP 引入明确的弃用流程（deprecation notice + 版本协商），与本体系 L2 弃用流程（至少 2 版本弃用期）可对齐。

**与本体系的对接策略**：

- 02 IPC 增加 MCP JSON-RPC 2.0 桥接章节（v2.0 已提议，未落地）
- 128B IPC 消息头扩展字段携带 `traceparent`（32 字节，W3C Trace Context 格式）
- 01 RT Agent 元数据可导出为 MCP Resource（Agent 即 MCP Resource）

### 4.2 A2A（Agent-to-Agent Protocol）v1.0 / v1.2

| 属性 | 值 |
|------|---|
| **创建方** | Google（2025 年 4 月） |
| **当前治理** | Linux Foundation（2025 年 6 月捐赠）→ AAIF（Agentic AI Foundation，2025 年 12 月成立） |
| **当前稳定版** | 1.0.0 |
| **最新演进** | v1.2（Signed Agent Cards） |
| **协议格式** | JSON-RPC 2.0 over HTTPS + SSE 流式 |
| **三层架构** | Data Model / Operations / Protocol Bindings（JSON-RPC / gRPC / HTTP-REST） |
| **核心数据对象** | Task、Message、AgentCard、Part、Artifact、Extension |
| **核心操作** | Send Message / Send Streaming Message / Get Task / List Tasks / Cancel Task / Get Agent Card |
| **设计原则** | Simple、Enterprise Ready、Async First、Modality Agnostic、Opaque Execution |
| **许可证** | Apache-2.0 |
| **官方规范 URL** | https://a2a-protocol.org/v1.0.0/specification |
| **GitHub 仓库** | https://github.com/a2aproject/A2A |

**关键变更解读**：

1. **Signed Agent Cards（v1.2）**：AgentCard 支持数字签名，确保 Agent 身份不可伪造。与本体系 03 SEC Cupolas capability 的身份验证形成映射——capability 令牌可作为 AgentCard 签名的密钥载体。

2. **AAIF 治理**：A2A 已纳入 Linux Foundation 旗下 AAIF（2025 年 12 月成立），与 MCP（AI Alliance 托管）形成双协议协同。AAIF 是 2026 年 Agent 互联网治理的核心实体。

3. **多协议绑定**：A2A 支持 JSON-RPC / gRPC / HTTP-REST 三种绑定，体现"协议核心 + 传输无关"设计。本体系 02 IPC 的"协议格式与底层传输分离"理念与此一致。

4. **AgentCard 服务发现**：AgentCard 位于 `/.well-known/agent.json`，是 A2A 的服务发现机制。本体系 01 RT 的 Agent 元数据应支持导出为 AgentCard 格式。

**与本体系的对接策略**：

- 01 RT 新增第 12 章 A2A AgentCard 发布（v2.0 已提议，未落地）
- 01 RT Agent 元数据 ↔ AgentCard 双向映射
- 03 SEC capability 令牌作为 AgentCard 签名密钥

### 4.3 OpenAI Agents SDK（2026 年 4 月 "Next Evolution"）

| 属性 | 值 |
|------|---|
| **创建方** | OpenAI |
| **最新更新** | 2026 年 4 月 "Next Evolution" |
| **新特性** | Sandbox Agents、Model-Native Harness、Code Mode、Subagents |
| **语言** | Python-first，TypeScript 跟进 |
| **四大原语** | agents、handoffs、guardrails、tracing |
| **许可证** | Apache-2.0 |
| **GitHub Stars** | 26,400+ |
| **MCP 集成** | 内置 MCP client + server |

**关键变更解读**：

1. **Sandbox Agents**：Agent 运行于沙箱，与 host 进程隔离。与本体系 03 SEC 的 sandbox_enter/sandbox_escape_detected 钩子直接对应——本体系已定义沙箱安全模型，但未提供参考实现。

2. **Model-Native Harness**：Agent 由模型原生驱动（非传统代码编排），handoffs 作为模型可调用的原语。与本体系 05 COG CoreLoopThree 的"模型驱动认知循环"理念一致。

3. **Subagents**：Agent 可派生子 Agent，形成层级。与本体系 03 SEC capability 派生（mint/derive）形成映射——子 Agent 通过 derive 获得父 Agent 权限子集。

4. **Tracing 内置**：tracing 是四大原语之一，与 OpenTelemetry 深度集成。本体系 02 IPC 的 trace 上下文传播应借鉴此设计。

**与本体系的对接策略**：

- 03 SEC 沙箱模型可作为 OpenAI Sandbox Agents 的形式化基础
- 05 COG CoreLoopThree 可作为 Model-Native Harness 的认知循环参考
- 03 SEC capability derive 可映射为 Subagents 权限派生

### 4.4 IETF IAIP（Intent-based Agent Interconnection Protocol）草案族

2026 年 H1，IETF 涌现 5 项 Agent 互联相关草案，形成"IAIP 草案族"：

| 草案 | 提交时间 | 核心内容 | 与本体系关系 |
|------|---------|---------|------------|
| `draft-sz-dmsc-iaip-01` | 2026-04 | Intent-based Agent Interconnection Protocol，定义 Agent Gateway 处的意图驱动互联 | 02 IPC 的意图层可对齐 |
| `draft-song-anp-aip-00` | 2026-03 | Agent Internet Protocol，定义 `agent://` URI scheme | 01 RT Agent 元数据的全局标识可对齐 `agent://` |
| `draft-cui-ai-agent-discovery-invocation-01` | 2026-02 | AI Agent Discovery and Invocation Protocol，含 Agent Semantic Resolution | 01 RT Agent 发现机制可对齐 |
| `draft-liu-dmsc-acps-arc-00` | 2026-01 | Agent Collaboration Protocols Architecture，定义 ATR/AIA/ADP/AIP/TIP/AMP 六层 | 09 INTEROP 域可参考此六层架构 |
| `draft-yan-iba-routing-security-requirements-01` | 2026-04 | Intent-based Agent Routing 安全要求 | 03 SEC 网络出口钩子（agent_network_egress）可对齐 |

**关键认知**：

1. **IETF 标准化窗口**：2026 年是 IETF Agent 互联协议标准化的关键窗口期，5 项草案并行推进，预计 2027 年形成 RFC。本体系若不在此窗口对接，将丧失标准化话语权。

2. **`agent://` URI scheme**：`draft-song-anp-aip-00` 定义的 `agent://` URI 可能成为 Agent 互联网的统一寻址方案，类似 `http://` 之于 Web。本体系 01 RT 的 Agent ID（uint64_t）应考虑与 `agent://` URI 的映射。

3. **六层协作架构**：`draft-liu-dmsc-acps-arc-00` 的 ATR/AIA/ADP/AIP/TIP/AMP 六层架构可作为 09 INTEROP 域的参考框架。

**与本体系的对接策略**：

- 09 INTEROP 域参考 ACPs 六层架构
- 01 RT Agent ID ↔ `agent://` URI 映射
- 跟踪 5 草案演进，v2.2 阶段正式对齐 RFC（预计 2027）

### 4.5 OCI-AI v1.3 与 T/CAMETA XX-2026

| 标准 | 状态 | 强制性 | 与本体系关系 |
|------|------|--------|------------|
| **OCI-AI v1.3** | 2026-04 起强制实施 | 强制 | Agent 容器镜像格式，本体系参考实现打包应对齐 |
| **T/CAMETA XX-2026** | 中国 MCP 安全要求团体标准 | 中国市场强制 | 本体系 03 SEC 安全模型在中国市场应对齐 |

**关键认知**：

1. **OCI-AI v1.3 强制实施**：自 2026-04 起，AI Agent 容器镜像必须符合 OCI-AI v1.3 格式。本体系的参考实现（agentrt）若以容器分发，必须对齐 OCI-AI v1.3。

2. **T/CAMETA 中国国标**：中国元宇宙生态协会发布的 MCP 安全要求团体标准，是中国市场 MCP 合规的强制门槛。本体系 03 SEC 在中国市场应通过 T/CAMETA 认证。

### 4.6 治理生态对标（CNCF / AAIF / OWFa / OpenChain）

| 治理维度 | 2026 H1 行业状态 | 本体系现状 | 差距 |
|---------|----------------|----------|------|
| **法律实体** | AAIF（Linux Foundation，2025-12 成立）托管 A2A + MCP | SPHARX Ltd. 单一公司 | 致命 |
| **专利授权** | OWFa 1.0（OCI 标准）+ Apache-2.0 内置专利（CNCF） | 无 OWFa，仅 AGPL+Apache | 致命 |
| **规范文档许可** | CC-BY-4.0（OCI / CNCF 通用） | AGPL-3.0-or-later OR Apache-2.0 | 高 |
| **分级孵化** | CNCF Sandbox→Incubating→Graduated（仅 4% 项目毕业） | 无分级 | 高 |
| **供应链合规** | OpenChain ISO/IEC 5230 + ISO/IEC 18974 | 无 | 中 |
| **行为准则** | LF CoC / CNCF CoC / openEuler CoC | 无 | 中 |
| **形式化验证** | seL4 Foundation Isabelle/HOL（~50 万行） | 无 | 致命 |

### 4.7 行业对标综合结论

本体系在 2026 H1 行业生态中的定位：

```
                    行业事实标准（2026 H1）
                    ┌─────────────────────────────────────┐
                    │  MCP 2026-07-28（无状态化+Extensions） │
                    │  A2A v1.2（Signed AgentCard）         │
                    │  OpenAI Agents SDK（Sandbox+Harness） │
                    │  IETF IAIP 五草案（agent:// URI）      │
                    │  OCI-AI v1.3（强制）                   │
                    │  AAIF（Linux Foundation 治理）         │
                    └─────────────────────────────────────┘
                              ↑ 零对接 ↑
                    ┌─────────────────────────────────────┐
                    │  Airymax OpenStandards v1.1          │
                    │  （7 域 / 4409 行 / 零行业协议提及）    │
                    │  （AGPL 许可 / 无 OWFa / 无 CNCF）    │
                    └─────────────────────────────────────┘
```

**核心差距**：本体系与 2026 H1 行业事实标准**零对接**，在协议生态、治理模式、专利授权、形式化验证四个维度全面落后。

### 4.8 Agent 编排框架对标：LangGraph / CrewAI（v1.1 新增）

任务背景要求评估与 LangGraph（状态图编排）和 CrewAI（多 Agent 角色协作）的对应关系。这两个不是协议层标准，而是应用层编排框架，但在 2026 H1 已成为 Agent 应用编排的事实选择。

| 属性 | LangGraph | CrewAI | Airymax 对应 |
|------|-----------|--------|------------|
| **创建方** | LangChain Inc.（2024-01） | CrewAI Inc.（2024-01） | — |
| **当前版本** | 0.2.x（2026-H1 稳定） | 0.95.x（2026-H1） | — |
| **核心模型** | 状态图（StateGraph）+ 节点 + 边 | 角色驱动（Role-driven）+ 任务（Task）+ Agent | 05 COG CoreLoopThree 三阶段（PERCEPTION/THINKING/ACTION） |
| **状态管理** | 显式状态对象（TypedDict / Pydantic）+ checkpointing | 隐式状态（任务间共享上下文） | 04 MEM MemoryRovol L1-L4 分级记忆 |
| **Agent 通信** | 节点间通过状态对象传递 | 任务结果传递 + delegation | 02 IPC 128B 消息头 + 5 种 payload 类型 |
| **调度模型** | 无（依赖 Python asyncio） | 无（依赖 Python asyncio） | 06 SCHED SCHED_EXT + vtime Q16.16 + 1024 并发 |
| **安全模型** | 无（应用层框架） | 无（应用层框架） | 03 SEC Cupolas capability 41 ID + mint/derive |
| **持久化** | SQLite/PostgreSQL checkpointing | 短期 + 长期记忆（外部集成） | 04 MEM PMEM 接口 + L4 长期记忆 |
| **人机协作** | interrupt_before / interrupt_after 节点 | human_input=True 任务 | 01 RT SUSPENDED/RESUME 状态 |
| **可观测性** | LangSmith 集成（商业） | OpenTelemetry 集成 | 02 IPC trace_id（仅 8B，无 W3C Trace Context） |
| **许可证** | MIT | MIT | AGPL-3.0-or-later OR Apache-2.0 |
| **GitHub Stars** | ~12,000+（2026-H1） | ~28,000+（2026-H1） | 不适用 |

**关键认知**：

1. **层次互补而非竞争**：LangGraph/CrewAI 是**应用层编排框架**，关注"如何用代码描述 Agent 工作流"；Airymax 是**运行时底座**，关注"如何为 Agent 提供运行时能力（调度、内存、安全、IPC）"。两者不直接竞争，可形成"LangGraph/CrewAI 编排 + Airymax 运行时"的分层组合。

2. **CoreLoopThree 与 LangGraph StateGraph 的映射**：LangGraph 的节点（node）可映射到 CoreLoopThree 的阶段（PERCEPTION/THINKING/ACTION），LangGraph 的边（edge）可映射到 02 IPC 的 REQUEST/RESPONSE payload。这种映射使 Airymax 可作为 LangGraph 的运行时后端。

3. **CrewAI 角色驱动与 capability 的映射**：CrewAI 的 Agent 角色定义（role/goal/backstory）可映射到 01 RT Agent 元数据；CrewAI 的 delegation 机制可映射到 03 SEC capability derive（子 Agent 通过 derive 获得父 Agent 权限子集）。

4. **可观测性差距**：LangGraph 有 LangSmith 商业可观测性平台，CrewAI 集成 OpenTelemetry；Airymax 的 02 IPC trace_id 仅 8 字节，未集成 W3C Trace Context，无法与 LangSmith/OpenTelemetry 互操作。这是 v2.1 阶段 2 必须补齐的差距。

5. **许可证差距**：LangGraph/CrewAI 均为 MIT 许可，可被任何商业项目直接采用；Airymax 的 AGPL-3.0-or-later 阻碍商业采纳，使"LangGraph 编排 + Airymax 运行时"组合在商业场景下不可行——除非 Airymax 改为 Apache-2.0 或 MIT。

**与本体系的对接策略**：

- 05 COG CoreLoopThree 应作为 LangGraph StateGraph 的运行时映射目标（v2.1 阶段 2 在 09 INTEROP 域定义映射）
- 03 SEC capability derive 应作为 CrewAI delegation 的权限派生机制（v2.1 阶段 2 在 09 INTEROP 域定义映射）
- 02 IPC trace_id 必须扩展为 W3C Trace Context `traceparent`，与 LangSmith/OpenTelemetry 互操作（v2.1 阶段 2 P2-3）
- 许可证改为 Apache-2.0，使商业组合可行（v2.1 阶段 2 P1-2）



***

## 5. Airymax 差异化定位评估

### 5.1 七维差异化评估

| # | 差异化维度 | Airymax 现状 | 行业标杆 | 差异化优势 | 差异化风险 |
|---|----------|------------|---------|----------|----------|
| 1 | **运行时底座定位** | "AI Agent 运行时平台工程"（对标 JVM/containerd） | OpenAI Agents SDK（应用框架）、MCP（协议层）、A2A（协议层） | **独特**：无其他项目定位为"Agent 运行时底座" | 定位过高，无参考实现支撑 |
| 2 | **双平面架构** | 控制面 syscall + 数据面 io_uring（零 syscall 数据面） | OpenAI Sandbox（进程级隔离）、MCP stdio+HTTP | **独特**：io_uring 零拷贝数据面是性能差异化亮点 | io_uring 仅 Linux，macOS/Windows 需降级 |
| 3 | **capability 安全模型** | Cupolas 41 ID + mint/mintcopy/derive/revoke | OpenAI Sandbox（进程级）、A2A OAuth 2.1 | **独特**：seL4 风格 capability 是细粒度安全差异化 | 命名混乱（are_cap_t/cap_t/airy_cap_t）削弱可信度 |
| 4 | **CoreLoopThree 认知循环** | PERCEPTION/THINKING/ACTION 三阶段 + Thinkdual 双模式 | OpenAI Model-Native Harness、AG-UI RUN/STEP 事件 | **互补**：可与 AG-UI 事件流映射 | 未对外公开，生态无法验证 |
| 5 | **MemoryRovol L1-L4** | 四级记忆卷载 + GFP 掩码 + PMEM 接口 | MCP Resources（数据层）、A2A Task State | **独特**：分级记忆管理是 Agent 长期记忆差异化 | 无参考实现，无记忆迁移性能数据 |
| 6 | **sched_ext 调度** | SCHED_AGENT + vtime Q16.16 + 1024 并发 | OpenAI 无调度层、A2A 无调度层 | **独特**：Agent 专属调度类是 OS 级差异化 | 仅 Linux，依赖 sched_ext 主线支持 |
| 7 | **同源三层模型** | IRON-9 v2 [SC]/[SS]/[IND] | 无对标（独有设计） | **独特**：agentrt ↔ agentrt-linux 同源共享 | 标注覆盖不足，01 RT 零标注 |

### 5.2 差异化定位 SWOT 分析

| | 正面 | 负面 |
|---|------|------|
| **内部** | **优势 (S)**：运行时底座定位独特；双平面架构性能领先；capability 细粒度安全；CoreLoopThree 认知循环；MemoryRovol 分级记忆；sched_ext Agent 调度；同源三层模型 | **劣势 (W)**：错误码三套方案；命名三种变体；[SC] 标注覆盖不足；零行业协议对接；AGPL 许可阻碍采纳；无参考实现；无形式化验证；无独立测试套件 |
| **外部** | **机会 (O)**：2026 H1 IETF IAIP 标准化窗口；AAIF 治理生态形成；OCI-AI v1.3 强制；中国 T/CAMETA 国标；Agent 互联网爆发期 | **威胁 (T)**：MCP + A2A 已成事实标准；OpenAI Agents SDK 26K stars 生态势能；若 2026 底仍未对接，将被边缘化；IETF RFC 预计 2027 发布，窗口收窄 |

### 5.3 差异化定位结论

- **核心差异化优势**：运行时底座定位 + 双平面架构 + capability 安全 + CoreLoopThree 认知循环 + MemoryRovol 分级记忆 + sched_ext 调度。这 6 项是本体系**唯一性的技术差异化**，行业无直接竞品。

- **核心差异化风险**：技术差异化被"工程不一致性"（错误码、命名、标注）严重削弱可信度，且被"生态孤立"（零行业协议对接）阻断采纳路径。

- **差异化定位建议**：v2.1 应采取**"技术差异化保留 + 工程一致性强制修复 + 生态对接全面补齐"**三轨并行策略——技术差异化是护城河，工程一致性是可信度基础，生态对接是采纳路径。

### 5.4 可独立实现性评估（v1.1 新增）

任务背景要求评估"标准是否语言无关"、"是否过度依赖 C 语言 API 签名"、"第三方实现者是否可独立实现"。这是开放标准的核心质量指标——一个真正的开放标准应允许任何语言的第三方实现者仅依据规范文本即可独立实现，而不需要参考特定语言的参考实现。

#### 5.4.1 语言中立性评估

| 数据结构 / 接口 | 当前定义方式 | 语言中立性 | 问题 |
|---------------|-----------|----------|------|
| 01 RT Agent 元数据 | JSON Schema（嵌入 Markdown） | ✅ 中立 | 但无独立 `.json` 文件 |
| 01 RT 生命周期状态机 | ASCII 状态图 + 文字 + C 函数签名 | ❌ C 绑定 | `airy_agent_create(are_cap_t cap, ...)` 等 C 签名直接出现在规范中 |
| 02 IPC 128B 消息头 | C `struct` + 字节布局图 | ⚠️ 部分中立 | 字节布局图是语言中立的，但 C `struct` 定义不是；无 Protobuf IDL |
| 02 IPC 5 种 payload 类型 | C `struct` + 文字描述 | ❌ C 绑定 | 无 Protobuf IDL，无语言无关序列化规范 |
| 03 SEC capability 令牌（64B） | C `struct are_cap_t` + 字节布局 | ⚠️ 部分中立 | 字节布局中立，但类型名 `are_cap_t` 是 C 类型 |
| 03 SEC capability 派生 API | C 函数签名 `airy_cap_mint/derive/revoke` | ❌ C 绑定 | 无语言无关的接口描述（如 IDL） |
| 04 MEM MemoryRovol L1-L4 | C `struct` + 文字描述 | ❌ C 绑定 | 无 IDL |
| 05 COG CoreLoopThree 三阶段 | 枚举 + 文字描述 | ✅ 中立 | 阶段定义是概念性的，与语言无关 |
| 06 SCHED 任务描述符（128B） | C `struct` + 字节布局图 | ⚠️ 部分中立 | 字节布局中立，但 C `struct` 定义不是 |
| 06 SCHED vtime 公式 | 数学公式 + Q16.16 定点 | ✅ 中立 | 数学公式语言无关 |
| 07 SYS 12 核心 syscall | C 函数签名 + kernel-doc | ❌ C 绑定 | syscall 本身是 Linux 特定概念，跨平台实现需重新定义 |

**评估结论**：11 项数据结构/接口中，仅 3 项（27%）是真正语言中立的；4 项（36%）部分中立；4 项（36%）是 C 语言绑定。标准实质上是"C 语言规范 + 字节布局补充"，而非"语言无关规范 + C 语言绑定"。

#### 5.4.2 第三方独立实现可行性评估

**评估方法**：假设一个 Python/Rust/Go/Java 实现者仅依据 8 份标准文档（不参考 agentrt / agentrt-linux 源码）独立实现，评估其能否成功。

| 实现步骤 | 可行性 | 障碍 |
|---------|-------|------|
| 解析 01 RT Agent 元数据 | ✅ 可行 | JSON Schema 足够清晰（虽无独立 .json 文件） |
| 实现 01 RT 生命周期状态机 | ⚠️ 部分可行 | 状态转移规则清晰，但 C 函数签名需翻译为目标语言 |
| 实现 02 IPC 128B 消息头序列化 | ⚠️ 部分可行 | 字节布局图清晰，但 C `struct` 字段顺序与字节偏移的对应关系需推断 |
| 实现 02 IPC 5 种 payload 类型 | ❌ 不可行 | 无 Protobuf IDL，payload 内部结构仅以 C `struct` 描述，Python/Rust 实现者需自行推断序列化规则 |
| 实现 03 SEC capability 派生 | ⚠️ 部分可行 | 派生规则（mint/derive/revoke）文字描述清晰，但 64B 令牌内部字段布局需从 C `struct` 推断 |
| 实现 04 MEM MemoryRovol L1-L4 | ❌ 不可行 | L1-L4 数据结构仅以 C `struct` 描述，无 IDL，GFP 掩码位定义需从 C 宏推断 |
| 实现 05 COG CoreLoopThree | ✅ 可行 | 三阶段是概念性的，可独立实现 |
| 实现 06 SCHED 任务描述符 | ⚠️ 部分可行 | 字节布局清晰，但 vtime 衰减公式的具体参数需从 C 代码推断 |
| 实现 07 SYS 12 核心 syscall | ❌ 不可行 | syscall 是 Linux 内核概念，Python/Java 实现者无法直接实现；需重新定义为"运行时 API"而非"syscall" |

**评估结论**：9 个实现步骤中，仅 2 个（22%）完全可行；4 个（44%）部分可行；3 个（33%）不可行。**第三方独立实现者无法仅依据规范文本完成实现**，必须参考 agentrt C 源码——这违反了"开放标准"的核心承诺。

#### 5.4.3 与行业标杆的可独立实现性对比

| 标准 | 语言中立性 | 第三方独立实现案例数 | Airymax 差距 |
|------|----------|-------------------|------------|
| OCI runtime-spec | ✅ JSON Schema + 字节布局形式化 | 10+ 独立实现（runc、crun、runjs、youki、gVisor 等） | **致命**：Airymax 0 独立实现 |
| MCP | ✅ JSON Schema + JSON-RPC 2.0 | 10000+ 公共 MCP 服务器，多语言 SDK | **致命**：Airymax 0 第三方实现 |
| A2A | ✅ JSON Schema + Protobuf/gRPC | 5 种官方 SDK（Python/JS/Java/Go/.NET），150+ 组织实现 | **致命**：Airymax 0 第三方实现 |
| seL4 | ✅ Isabelle/HOL 形式化规范 + Haskell 参考实现 | 多个研究性实现 | **致命**：Airymax 无形式化规范 |

#### 5.4.4 可独立实现性改进方案

| 改进项 | 目标 | 实施阶段 | 工期 |
|-------|------|---------|------|
| 抽取独立 JSON Schema 文件 | `schemas/agent-metadata.schema.json` 等 | 阶段 1 | 0.5 周 |
| 为 02 IPC payload 类型定义 Protobuf IDL | `proto/airy_ipc.proto` | 阶段 2 | 1 周 |
| 为 03 SEC capability 令牌定义 FlatBuffers schema | `fbs/capability.fbs` | 阶段 2 | 0.5 周 |
| 将 C 函数签名翻译为语言无关 IDL | 使用 WIT（Wasm Interface Type）或 Cap'n Proto IDL | 阶段 3 | 2 周 |
| 提供 Python / Rust 参考绑定 | 至少 2 种非 C 语言绑定 | 阶段 4 | 4 周 |
| 验证第三方独立实现 | 邀请 1-2 个外部团队仅依据规范实现 | 阶段 4 | 持续 |

***

## 6. v2.1 优化方案（优先级排序 + 路线图）

### 6.1 优化方案优先级矩阵

按"严重等级 × 实施难度"二维矩阵排序，优先处理"致命/高严重 + 低/中难度"项：

| 优先级 | 优化项 | 严重等级 | 实施难度 | 目标版本 | 工期 |
|--------|-------|---------|---------|---------|------|
| **P0** | 错误码 SSoT 强制统一 | 致命 | 中 | 1.2 | 1 周 |
| **P0** | `airy_cap_t` 全量改名（34 处） | 高 | 低 | 1.2 | 0.5 周 |
| **P0** | README 版本一致性修复（头部 1.0 ↔ 历史 1.1 ↔ "六大领域"错描述 ↔ 第 231 行断裂引用） | 高 | 低 | 1.2 | 0.2 周 |
| **P0** | README 第 231 行断裂引用修正（`docs/AirymaxOS/TERMINOLOGY.md` → `docs/AirymaxRT/TERMINOLOGY.md`）+ 第 232-236 行其他引用路径核对 | 中-高 | 低 | 1.2 | 0.1 周 |
| **P1** | `[SC]/[SS]/[IND]` 三层标注全量补齐 | 中 | 中 | 1.2 | 1 周 |
| **P1** | 抽取独立 JSON Schema 文件（`schemas/agent-metadata.schema.json`） | 中 | 低 | 1.2 | 0.5 周 |
| **P1** | 许可证分离（CC-BY-4.0 规范 + Apache-2.0 实现） | 高 | 低 | 2.0 | 0.5 周 |
| **P1** | 新增 08 PROTO 协议对接域 | 高 | 高 | 2.0 | 2 周 |
| **P1** | 新增 09 INTEROP 互操作域 | 高 | 高 | 2.0 | 2 周 |
| **P1** | 为 02 IPC payload 类型定义 Protobuf IDL（`proto/airy_ipc.proto`） | 高 | 中 | 2.0 | 1 周 |
| **P2** | MCP 2026-07-28 桥接（02 IPC 第 14 章 + AOS-STD-IPC-029~035） | 致命 | 高 | 2.0 | 1.5 周 |
| **P2** | A2A v1.2 AgentCard 发布（01 RT 第 12 章 + AOS-STD-RT-025~028） | 致命 | 中 | 2.0 | 1 周 |
| **P2** | OpenTelemetry traceparent 纳入 IPC 消息头扩展 | 高 | 中 | 2.0 | 0.5 周 |
| **P2** | OWFa 1.0 专利授权引入 | 高 | 中 | 2.1 | 1 周 |
| **P2** | CNCF 三级孵化治理机制（含 SPHARX 否决权限制） | 高 | 中 | 2.1 | 1.5 周 |
| **P2** | OpenChain ISO/IEC 5230 合规基线 | 中 | 中 | 2.1 | 1 周 |
| **P2** | LangGraph/CrewAI 编排映射（09 INTEROP 章节） | 中 | 中 | 2.0 | 0.5 周 |
| **P3** | 新增 10 GOV 治理章程 | 中 | 中 | 2.2 | 1.5 周 |
| **P3** | Isabelle/HOL 形式化验证基线（3 核心定理声明） | 中 | 高 | 2.2 | 3 周 |
| **P3** | 独立 conformance 测试套件仓库（含 README 第 144 行虚假承诺修复） | 高 | 高 | 2.2 | 2 周 |
| **P3** | IETF IAIP 草案跟踪 + `agent://` URI 映射 | 中 | 中 | 2.2 | 1 周 |
| **P3** | OCI-AI v1.3 容器镜像格式对齐 | 中 | 低 | 2.2 | 0.5 周 |
| **P3** | T/CAMETA XX-2026 中国 MCP 安全要求对齐 | 中 | 中 | 2.2 | 1 周 |
| **P3** | Python/Rust 参考绑定（验证可独立实现性） | 高 | 高 | 2.2 | 4 周 |
| **P3** | 商标转移到独立法律实体（AAIF 或 Airymax Foundation） | 高 | 高 | 2.2 | 持续 |

### 6.2 阶段 1：技术一致性强制修复（1.1 → 1.2，~2 周）

#### 6.2.1 P0-1：错误码 SSoT 强制统一

**目标**：建立 03 SEC 为唯一错误码 SSoT，7 标准全量对齐。

**统一方案**（修正 03 SEC SSoT 表的内部不一致）：

| 段 | 范围 | 用途 | 示例 |
|----|------|------|------|
| 成功 | 0 | 成功 | `AIRY_EOK=0` |
| 通用 | -1 ~ -99 | 通用错误 | `AIRY_EINVAL=-2`、`AIRY_ENOENT=-3`（修正：避免与 EINVAL 冲突）、`AIRY_EAGAIN=-4`、`AIRY_EIO=-5`、`AIRY_ELIMIT=-7`、`AIRY_EEXIST=-17`、`AIRY_EBADF=-8`、`AIRY_ENOTSUP=-10`、`AIRY_ECONFLICT=-12` |
| 系统 | -100 ~ -199 | 系统级 | `AIRY_ETIMEOUT=-101`（修正：原 -1004 不在段内）、`AIRY_EBUDGET=-102`（修正：原 -1004 与 TIMEOUT 同值） |
| 内存 | -1100 ~ -1199 | 内存错误 | `AIRY_ENOMEM=-1100`、`AIRY_EPERSIST=-1101`、`AIRY_EMSGSIZE=-1109`（修正：原 -1201 跑到 IPC 段，但 MSGSIZE 语义属 IPC，应保留 -1201） |
| IPC | -1200 ~ -1299 | IPC 错误 | `AIRY_EMSGSIZE=-1201`、`AIRY_ENOMSG=-1202` |
| 安全 | -1300 ~ -1399 | 安全错误 | `AIRY_EPERM=-1302` |
| 认知 | -1700 ~ -1799 | 认知错误 | `AIRY_ECog_TIMEOUT=-1701`、`AIRY_EMODEL=-1702`、`AIRY_EPHASE=-1703` |
| 调度 | -1600 ~ -1699 | 调度错误 | `AIRY_EBUSY=-1601`、`AIRY_ESCHED=-1602`、`AIRY_SCHED_EXHAUSTED=-1603` |

**07 SYS 特殊处理**：07 SYS 当前使用 -1 ~ -12 连续小整数方案，与 SSoT 完全不兼容。鉴于 07 SYS 声称"对齐 `airy_errno.h`"，且 syscall 错误码需与 Linux 标准 errno 转换，**建议 07 SYS 保留 -1 ~ -12 作为"syscall 内部错误码"，但强制增加 `airy_errno_to_linux()` 与 `airy_errno_to_app()` 转换函数**，使其在应用层表现为 SSoT 统一段。此举既保留 syscall 与 Linux errno 的天然亲和性，又不破坏应用层 SSoT。

**兼容期**：1.2 版本保留旧错误码值作为 `#define` 别名（标注 `@deprecated`），2.0 版本移除别名。

#### 6.2.2 P0-2：`airy_cap_t` 全量改名

**目标**：三种变体（`are_cap_t` / `cap_t` / 应为 `airy_cap_t`）统一为 `airy_cap_t`。

**改动范围**：

| 文件 | 当前变体 | 出现次数 | 改为 |
|------|---------|---------|------|
| 03 SEC | `are_cap_t` | 22 处 | `airy_cap_t` |
| 01 RT | `are_cap_t` | 1 处（第 501 行） | `airy_cap_t` |
| 02 IPC | `are_cap_t` | 3 处（第 282/287/305 行） | `airy_cap_t` |
| 07 SYS | `cap_t` | 8 处（第 207/224/241/258/275/293/326/400 行） | `airy_cap_t` |

**合计需修改 34 处**（v1.0 草案原计 28 处，已按 Grep 复核修正）。

**兼容期**：1.2 版本保留 `typedef are_cap_t airy_cap_t;` 与 `typedef cap_t airy_cap_t;` 别名（标注 `@deprecated`），2.0 版本移除。

#### 6.2.3 P0-3：README 版本一致性修复 + 断裂引用修正

**目标**：修复 README 三处内部不一致 + 一处断裂引用 + 核对其他引用路径。

| 位置 | 当前 | 修正为 | 类型 |
|------|------|--------|------|
| 第 6 行（头部版本） | `1.0（开放标准草案）` | `1.1（开放标准草案）` | 版本回退 |
| 第 7 行（最后更新） | `2026-07-09` | `2026-07-13`（或当日日期） | 日期过期 |
| 第 14 行（域数描述） | `六大领域` | `七大领域`（实际已有 RT/IPC/SEC/MEM/COG/SCHED/SYS 七域） | 数量错误 |
| 第 231 行（TERMINOLOGY.md 引用） | `docs/AirymaxOS/TERMINOLOGY.md` | `docs/AirymaxRT/TERMINOLOGY.md`（`find` 验证实际位于 AirymaxRT 而非 AirymaxOS） | **断裂引用** |
| 第 232-236 行（其他引用） | `docs/AirymaxOS/50-engineering-standards/*` 等路径 | 逐一 `find` 验证后修正 | 待核对（疑似多处断裂） |
| 第 144 行（测试套件代码承诺） | `测试套件代码以 Apache-2.0 许可证发布` | 删除该声明，或改为"测试套件代码计划于 v2.2 以 Apache-2.0 发布" | **虚假承诺** |

#### 6.2.4 P1-1：`[SC]/[SS]/[IND]` 三层标注全量补齐

**目标**：7 标准全部补齐三层映射表（以 07 SYS 第 635-637 行为模板）+ 条目级 `[SC]` 标注。

**补齐模板**（每标准末尾新增"附录：同源三层映射"章节）：

```markdown
## 附录：同源三层映射

| 层次 | 标注 | 共享程度 | 在本标准中的体现 |
|------|------|---------|----------------|
| **[SC] 共享契约层** | 完全共享代码 | <本标准 [SC] 数据结构清单> |
| **[SS] 语义同源层** | API 签名同源，实现独立 | <本标准 [SS] API 清单> |
| **[IND] 完全独立层** | 完全独立 | <本标准 [IND] 实现清单> |
```

**条目级标注**：在每个 `AOS-STD-*` 条目后追加 `[SC]` / `[SS]` / `[IND]` 标签，如：

```
（AOS-STD-RT-001，[SC]，L1 稳定级）
```

### 6.3 阶段 2：协议生态对接（1.2 → 2.0，~5 周）

#### 6.3.1 P1-2：许可证分离

**目标**：8 文件 SPDX 头分离。

| 产物 | 当前许可 | v2.1 许可 | 理由 |
|------|---------|----------|------|
| 规范文档（01-07 + README） | AGPL-3.0-or-later OR Apache-2.0 | CC-BY-4.0 | 鼓励最广泛引用 |
| 参考实现（agentrt 源码） | AGPL-3.0-or-later OR Apache-2.0 | Apache-2.0 | 允许商业闭源派生 |
| 测试套件（独立仓库） | 内嵌文档 | Apache-2.0 | 鼓励社区贡献 |
| 示例代码 | 随文档 | Apache-2.0 | 允许直接复制 |

#### 6.3.2 P1-3：新增 08 PROTO 协议对接域

**目标**：新建 `08-airy-protocol-bridge-standard.md`，定义 Airymax 与外部协议的桥接契约。

**章节规划**：

| 章节 | 内容 | 对接协议 |
|------|------|---------|
| 一 | MCP JSON-RPC 2.0 桥接（128B IPC ↔ JSON-RPC） | MCP 2026-07-28 |
| 二 | A2A AgentCard 发布与发现 | A2A v1.2 |
| 三 | AG-UI 事件流映射（RUN/STEP ↔ CoreLoopThree） | AG-UI |
| 四 | ANP DID:wba 身份桥接 | ANP |
| 五 | IETF IAIP `agent://` URI 映射 | IAIP 草案族 |
| 六 | OpenTelemetry traceparent 传播 | OpenTelemetry / W3C Trace Context |

**标准条目**：AOS-STD-PROTO-001 ~ AOS-STD-PROTO-024（预计 24 条）。

#### 6.3.3 P1-4：新增 09 INTEROP 互操作域

**目标**：新建 `09-airy-interoperability-standard.md`，定义跨运行时互操作契约。

**章节规划**：

| 章节 | 内容 | 参考 |
|------|------|------|
| 一 | 互操作六层架构（ATR/AIA/ADP/AIP/TIP/AMP） | draft-liu-dmsc-acps-arc-00 |
| 二 | Agent 语义解析（Agent Semantic Resolution） | draft-cui-ai-agent-discovery-invocation-01 |
| 三 | 跨运行时任务委托（Opaque Execution） | A2A 设计原则 |
| 四 | OCI-AI v1.3 容器镜像格式对齐 | OCI-AI v1.3 |
| 五 | T/CAMETA XX-2026 中国 MCP 安全要求对齐 | T/CAMETA |

**标准条目**：AOS-STD-INTEROP-001 ~ AOS-STD-INTEROP-016（预计 16 条）。

#### 6.3.4 P2-1：MCP 2026-07-28 桥接

**目标**：02 IPC 新增第 14 章 MCP JSON-RPC 2.0 桥接 + AOS-STD-IPC-029 ~ 035（7 条）。

**桥接契约要点**：

- 128B IPC 消息头 ↔ JSON-RPC 2.0 消息双向转换规则
- MCP Resources ↔ Airymax MemoryRovol L1 映射
- MCP Tools ↔ Airymax capability invocation 映射
- MCP Prompts ↔ Airymax CoreLoopThree THINKING 阶段输入映射
- MCP Extensions ↔ Airymax IPC payload 扩展字段映射
- W3C Trace Context `traceparent`（32B）纳入 IPC 消息头保留字段

#### 6.3.5 P2-2：A2A v1.2 AgentCard 发布

**目标**：01 RT 新增第 12 章 A2A AgentCard 发布 + AOS-STD-RT-025 ~ 028（4 条）。

**发布契约要点**：

- Agent 元数据 ↔ AgentCard JSON 双向映射
- `/.well-known/agent.json` 发布规范
- Signed Agent Card 签名机制（capability 令牌作为签名密钥）
- AgentCard 发现与 02 IPC 端点能力协商

#### 6.3.6 P2-3：OpenTelemetry traceparent 纳入 IPC 消息头

**目标**：02 IPC 128B 消息头保留字段（当前 reserved 24B）划出 32B 用于 W3C Trace Context `traceparent`。

**消息头布局调整**（L1 稳定级，需谨慎）：

```
偏移 96        128
+--------------+
| reserved 24B |  →  traceparent 32B（需扩展消息头至 136B 或复用保留区）
+--------------+
```

**兼容方案**：保持 128B 总长不变，将 `traceparent` 拆分为 `trace_id`(16B) + `span_id`(8B) + `trace_flags`(1B) = 25B，嵌入 reserved 24B + 1B（从其他字段借 1B）。或新增 136B 变体，通过 version 字段协商。

### 6.4 阶段 3：治理与许可升级（2.0 → 2.1，~4 周）

#### 6.4.1 P2-4：OWFa 1.0 专利授权引入

**目标**：引入 [OWFa 1.0 Patent Only](https://www.openwebfoundation.org/the-agreements/the-owf-1-0-agreements-granted-claims/owfa-1-0-patent-only) 专利不主张承诺。

**核心机制**：

- Patent Non-Assert Promise：贡献者不可撤销承诺不对 Permitted Uses 主张专利侵权
- Patent License Commitment：免版税、非歧视专利许可
- Defensive Termination：被授权方主动起诉贡献者时承诺终止
- Bankruptcy Protection：参考美国破产法 365(n) 条

**落地文件**：新增 `PATENTS.md`，列出所有贡献者的 Granted Claims。

#### 6.4.2 P2-5：CNCF 三级孵化治理机制

**目标**：引入 CNCF 风格三级孵化（参考 [CNCF Project Lifecycle](https://contribute.cncf.io/projects/lifecycle/)）。

| 级别 | 准入标准 | 本体系映射 |
|------|---------|----------|
| Sandbox | 实验性，15-20% 三年内归档 | 新提案标准条目（L3/L4） |
| Incubation | 3+ 组织生产部署，commiter 多样性，安全审计 | L2 弃用流程条目 |
| Graduated | 多组织 maintainer，第三方安全审计，超多数 TOC 投票 | L1 永久稳定条目 |

**治理结构**：

- 标准委员会（对标 OCI TOB）：最终裁决
- 技术监督组（对标 CNCF TOC）：技术评审
- 社区代表投票机制：超多数通过

#### 6.4.3 P2-6：OpenChain ISO/IEC 5230 合规基线

**目标**：建立 [ISO/IEC 5230:2020](https://www.iso.org/standard/81039.html) 供应链合规基线。

**交付物**：

- SBOM（Software Bill of Materials）模板
- CLA 三类（个人 / 企业 / 员工）
- 行为准则（CoC）
- 供应链安全审计清单（参考 [ISO/IEC 18974:2023](https://www.iso.org/standard/86450.html)）

### 6.5 阶段 4：形式化与参考实现（2.1 → 2.2，~8 周）

#### 6.5.1 P3-1：新增 10 GOV 治理章程

**目标**：新建 `10-airy-governance-charter-standard.md`，定义开放标准治理章程。

**章节规划**：法律实体、专利授权、CLA、行为准则、分级孵化、公开 RFC 流程、商标体系、会议透明度。

#### 6.5.2 P3-2：Isabelle/HOL 形式化验证基线

**目标**：对 3 项核心契约提供 Isabelle/HOL 规范声明（不必完整证明）。

| 契约 | 形式化目标 | 参照 |
|------|----------|------|
| 01 RT 生命周期状态机 | 状态转移完备性 + 无死锁 | seL4 thread state |
| 03 SEC capability 派生 | 偏序集 + 权限子集单调性 | seL4 capability derivation |
| 06 SCHED vtime 公平性 | lag boundedness | CFS fairness theorem |

#### 6.5.3 P3-3：独立 conformance 测试套件仓库

**目标**：新建 `airymax-conformance` 独立仓库（Apache-2.0），实现 24 条 L1 核心条目可执行测试。

**覆盖矩阵**：每条 AOS-STD-* L1 条目 ↔ 至少 1 个测试用例。

#### 6.5.4 P3-4 ~ P3-6：IETF IAIP 跟踪 + OCI-AI 对齐 + T/CAMETA 对齐

- IETF IAIP：跟踪 5 草案演进，v2.2 正式对齐 RFC（预计 2027）
- OCI-AI v1.3：参考实现容器镜像对齐
- T/CAMETA：03 SEC 安全模型通过 T/CAMETA 认证

### 6.6 v2.1 路线图总览

```
2026 H2 时间线
├── 阶段 1（1.1 → 1.2，~2 周）技术一致性强制修复
│   ├── P0 错误码 SSoT 统一
│   ├── P0 airy_cap_t 全量改名
│   ├── P0 README 版本一致性修复
│   └── P1 [SC]/[SS]/[IND] 三层标注补齐
├── 阶段 2（1.2 → 2.0，~5 周）协议生态对接
│   ├── P1 许可证分离
│   ├── P1 新增 08 PROTO 域
│   ├── P1 新增 09 INTEROP 域
│   ├── P2 MCP 2026-07-28 桥接
│   ├── P2 A2A v1.2 AgentCard 发布
│   └── P2 OpenTelemetry traceparent 纳入 IPC
├── 阶段 3（2.0 → 2.1，~4 周）治理与许可升级
│   ├── P2 OWFa 1.0 专利授权
│   ├── P2 CNCF 三级孵化治理
│   └── P2 OpenChain ISO/IEC 5230 合规
└── 阶段 4（2.1 → 2.2，~8 周）形式化与参考实现
    ├── P3 新增 10 GOV 治理章程
    ├── P3 Isabelle/HOL 形式化验证基线
    ├── P3 独立 conformance 测试套件仓库
    ├── P3 IETF IAIP 跟踪 + agent:// URI 映射
    ├── P3 OCI-AI v1.3 容器镜像对齐
    └── P3 T/CAMETA XX-2026 中国 MCP 安全对齐

合计 ~19 周（约 5 个月），2026 年底完成 v1.1 → v2.2 整体跃迁
```

***

## 7. 综合评分与改进建议

### 7.1 v2.1 优化后预期评分

| # | 评估维度 | v2.0 基线 | v2.1 目标 | v2.2 远期 | 提升路径 |
|---|---------|----------|----------|----------|---------|
| 1 | 错误码一致性 | 3 / 10 | 9 / 10 | 10 / 10 | 阶段 1 P0 统一 SSoT + 07 SYS 转换函数 |
| 2 | 命名规范 | 4 / 10 | 10 / 10 | 10 / 10 | 阶段 1 P0 全量 `airy_cap_t` |
| 3 | `[SC]/[SS]/[IND]` 标注 | 3 / 10 | 9 / 10 | 10 / 10 | 阶段 1 P1 全量三层表 + 条目级标注 |
| 4 | 主题域完备性 | 4 / 10 | 8 / 10 | 9 / 10 | 阶段 2 新增 08/09 + 阶段 4 新增 10 |
| 5 | 协议生态对接 | 2 / 10 | 8 / 10 | 9 / 10 | 阶段 2 MCP/A2A/OTel 桥接 + 阶段 4 IAIP/OCI-AI/T-CAMETA |
| 6 | 许可证与专利 | 3 / 10 | 9 / 10 | 10 / 10 | 阶段 2 许可分离 + 阶段 3 OWFa |
| 7 | 治理成熟度 | 3 / 10 | 7 / 10 | 9 / 10 | 阶段 3 CNCF 孵化 + 阶段 4 GOV 章程 |
| 8 | 形式化验证 | 1 / 10 | 5 / 10 | 8 / 10 | 阶段 4 Isabelle/HOL 基线 |
| 9 | 参考实现可追溯 | 2 / 10 | 7 / 10 | 9 / 10 | 阶段 4 conformance 套件 + 条目-代码映射 |
| 10 | 行业对齐度 | 2 / 10 | 8 / 10 | 9 / 10 | 阶段 2-4 持续对齐 2026 H1 生态 |
| | **综合** | **2.7 / 10** | **8.0 / 10** | **9.3 / 10** | — |

### 7.2 关键改进建议（按优先级）

#### 7.2.1 立即执行（本周内）

1. **修复 README 三处不一致**：头部版本 1.0→1.1、域数"六大"→"七大"、最后更新日期。工期 0.1 周。
2. **启动错误码 SSoT 统一**：以本报告 6.2.1 方案为准，修正 03 SEC SSoT 表内部不一致（ETIMEOUT=-1004→-101、EBUDGET=-1004→-102），并逐标准对齐。工期 1 周。
3. **启动 `airy_cap_t` 全量改名**：以本报告 6.2.2 范围为准，28 处改动 + 兼容别名。工期 0.5 周。

#### 7.2.2 阶段 1 内完成（2 周内）

4. **补齐 `[SC]/[SS]/[IND]` 三层标注**：以 07 SYS 为模板，01-06 全部补齐附录三层表 + 条目级标注。工期 1 周。
5. **建立全局编号注册表**：新建 `_registry/AOS-STD-registry.md`，汇总 7 标准（未来 10 标准）全部条目编号，作为唯一 SSoT。工期 0.5 周。

#### 7.2.3 阶段 2 内完成（7 周内）

6. **许可证分离**：8 文件 SPDX 头改为 CC-BY-4.0（规范）+ Apache-2.0（实现/测试）。
7. **新建 08 PROTO 协议对接域**：MCP/A2A/AG-UI/ANP/IAIP/OpenTelemetry 六协议桥接。
8. **新建 09 INTEROP 互操作域**：六层架构 + Agent 语义解析 + OCI-AI + T/CAMETA。
9. **02 IPC 新增 MCP JSON-RPC 2.0 桥接章节**：AOS-STD-IPC-029~035。
10. **01 RT 新增 A2A AgentCard 发布章节**：AOS-STD-RT-025~028。
11. **02 IPC 消息头纳入 traceparent**：W3C Trace Context 集成。

#### 7.2.4 阶段 3-4 内完成（19 周内）

12. **引入 OWFa 1.0 专利授权**：新增 PATENTS.md。
13. **建立 CNCF 三级孵化机制**：Sandbox/Incubating/Graduated 映射 L3/L2/L1。
14. **建立 OpenChain 合规基线**：SBOM + CLA + CoC。
15. **新建 10 GOV 治理章程**。
16. **Isabelle/HOL 形式化验证基线**：3 核心契约规范声明。
17. **独立 conformance 测试套件仓库**：24 条 L1 核心条目可执行测试。

### 7.3 风险与缓解

| 风险 | 等级 | 缓解措施 |
|------|------|---------|
| L1 契约修改破坏向后兼容 | 高 | 错误码、命名改动均设 1.2 兼容期（别名 + @deprecated），2.0 移除 |
| 07 SYS 错误码方案与 SSoT 不兼容 | 中 | 保留 07 SYS -1~-12 作为 syscall 内部码，增加转换函数 |
| IPC 消息头扩展破坏 128B 定长 | 高 | 优先复用 reserved 24B，必要时通过 version 协商 136B 变体 |
| IETF IAIP 草案 2027 才成 RFC | 中 | v2.2 仅做映射跟踪，不对齐未定稿 RFC |
| 形式化验证工期过长 | 中 | v2.2 仅要求规范声明，不要求完整证明 |
| AGPL 已分发的旧版本无法回收 | 低 | 新版本起改 CC-BY-4.0，旧版本保留 AGPL 历史不冲突 |

### 7.4 验收标准

v2.1 阶段 1-3 完成的验收标准（共 17 项，v1.1 新增 5 项 ACC-13~17）：

| 编号 | 验收项 | 验证方法 |
|------|--------|---------|
| ACC-v2.1-01 | 03 SEC SSoT 表内部一致（无 -1004 越段） | Grep 检索 `TIMEOUT=-1004` 与 `EBUDGET=-1004` 返回 0 |
| ACC-v2.1-02 | 7 标准错误码全部对齐 SSoT（07 SYS 保留 -1~-12 + 转换函数） | 逐标准错误码表交叉比对 |
| ACC-v2.1-03 | `are_cap_t` 与 `cap_t` 在 8 文件中返回 0（仅兼容别名保留） | Grep 检索 `are_cap_t` 与 `\bcap_t\b` |
| ACC-v2.1-04 | README 头部版本 = 1.1，域数 = "七大"，第 7 行日期更新 | Read README 第 6/7/14 行 |
| ACC-v2.1-05 | 01-06 标准末尾均有"附录：同源三层映射"章节 | Grep 检索 `## 附录：同源三层映射` 返回 7 |
| ACC-v2.1-06 | 8 文件 SPDX 头为 CC-BY-4.0（规范）/ Apache-2.0（实现） | Grep 检索 `SPDX-License-Identifier` |
| ACC-v2.1-07 | `08-airy-protocol-bridge-standard.md` 存在且 ≥ 24 条 AOS-STD-PROTO-* | 文件存在性 + 条目计数 |
| ACC-v2.1-08 | `09-airy-interoperability-standard.md` 存在且 ≥ 16 条 AOS-STD-INTEROP-* | 文件存在性 + 条目计数 |
| ACC-v2.1-09 | 02 IPC 含第 14 章 MCP JSON-RPC 2.0 桥接 + AOS-STD-IPC-029~035 | Grep 检索 `## 十四` + 条目计数 |
| ACC-v2.1-10 | 01 RT 含第 12 章 A2A AgentCard 发布 + AOS-STD-RT-025~028 | Grep 检索 `## 十二` + 条目计数 |
| ACC-v2.1-11 | `PATENTS.md` 存在且含 OWFa 1.0 Patent Only 声明 | 文件存在性 + 内容检索 |
| ACC-v2.1-12 | `_registry/AOS-STD-registry.md` 存在且含全部条目编号 | 文件存在性 + 条目计数 |
| ACC-v2.1-13 | README 第 231 行引用 `docs/AirymaxRT/TERMINOLOGY.md`（非 AirymaxOS） | Read README 第 231 行 + `find docs -name TERMINOLOGY.md` |
| ACC-v2.1-14 | README 第 144 行"测试套件代码以 Apache-2.0 发布"声明已删除或修正 | Read README 第 144 行 |
| ACC-v2.1-15 | `schemas/agent-metadata.schema.json` 独立文件存在且通过 JSON Schema 2020-12 校验 | 文件存在性 + `ajv validate` |
| ACC-v2.1-16 | `proto/airy_ipc.proto` 存在且定义 5 种 payload 类型 | 文件存在性 + `protoc --lint` |
| ACC-v2.1-17 | `CODE_OF_CONDUCT.md` 与 `CONTRIBUTING.md` 与 `CLA.md` 三文件存在 | 文件存在性 |

### 7.5 总结

Airymax OpenStandards v2.1 系统性复审（v1.1 增量修订版）发现：v2.0 优化研究的 6 项建议**落地率 0/6**，v1.0 重建方案识别的 P1/P2 级问题（README 断裂引用、形式化规范、参考实现、可独立实现性、治理 SPHARX 中心化）**亦全部未落地**。当前体系仍处于 v1.1 草案状态，且在以下技术维度上**比 v2.0 研究时更严重**：

1. **错误码一致性**：三套方案 + 双码同值（05 COG TIMEOUT=EBUDGET=-1004）+ 值冲突（04/06 ENOENT=EINVAL=-2）
2. **命名规范**：三种变体（`are_cap_t` 26 处 + `cap_t` 8 处 + 正确形式 `airy_cap_t` 0 处），共 34 处需修改
3. **`[SC]/[SS]/[IND]` 标注覆盖**：01 RT 零标注；02-06 仅引言；仅 07 SYS 完整
4. **README 文档完整性**：头部版本回退（1.0 vs 历史 1.1）、"六大领域"错描述（实际 7 域）、第 231 行断裂引用（`docs/AirymaxOS/TERMINOLOGY.md` 不存在）、第 144 行虚假承诺（"测试套件代码以 Apache-2.0 发布"但代码不存在）
5. **可独立实现性**：11 项数据结构中仅 27% 真正语言中立，第三方无法仅依据规范文本独立实现
6. **治理 SPHARX 中心化**：单一公司任命维护者 + 单一公司持有商标 + 无独立法律实体，实质上是"公司开放标准"而非"行业开放标准"

与此同时，2026 H1 行业生态已发生实质性跃迁（MCP 2026-07-28 无状态化、A2A v1.2 签名卡、IETF IAIP 五草案、OpenAI Sandbox、OCI-AI v1.3 强制、AAIF 治理、LangGraph/CrewAI 编排框架成熟），本体系与行业事实标准**零对接**，差距正加速扩大。

v2.1 优化方案采取"技术一致性强制修复 + 协议生态对接 + 治理许可升级 + 形式化参考实现"四阶段并行策略，~19 周完成 v1.1 → v2.2 整体跃迁，综合评分从 2.6/10 提升至 8.0/10（v2.1）与 9.3/10（v2.2）。**立即执行项**（README 修复 + 错误码 SSoT 统一 + `airy_cap_t` 改名 + README 断裂引用修正）应在本周内启动，以遏制技术不一致性与文档不完整性的持续恶化。

***

## 附录 A：错误码不一致矩阵（7 标准全量比对）

| 错误码 | 01 RT | 02 IPC | 03 SEC (SSoT) | 04 MEM | 05 COG | 06 SCHED | 07 SYS | SSoT 期望值 | 问题 |
|--------|-------|--------|--------------|--------|--------|----------|--------|------------|------|
| `AIRY_EOK` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | ✓ 一致 |
| `AIRY_EINVAL` | -2 | -2 | -2 | -2 | -2 | -2 | **-1** | -2 | ✗ 07 SYS 偏离 |
| `AIRY_ENOMEM` | **-3** | — | -1100 | -1100 | — | — | **-2** | -1100 | ✗ 01 RT 偏离；07 SYS 偏离 |
| `AIRY_EPERM` | **-22** | **-22** | -1302 | — | — | -1302 | **-4** | -1302 | ✗ 01/02 偏离；07 SYS 偏离 |
| `AIRY_EBUSY` | **-16** | **-16** | — | — | — | -1601 | **-9** | -1601 | ✗ 01/02 偏离；07 SYS 偏离 |
| `AIRY_ETIMEOUT` | — | **-1004** | **-1004**（越段） | — | **-1004**（与 EBUDGET 同值） | — | **-11** | -101 | ✗✗ 03 SSoT 越段；05 双码同值；07 SYS 偏离 |
| `AIRY_EBUDGET` | **-1004** | — | —（未定义） | — | **-1004**（与 TIMEOUT 同值） | — | — | -102 | ✗✗ 05 双码同值；03 SSoT 未定义 |
| `AIRY_EEXIST` | **-17** | — | —（未定义） | — | — | — | — | 待定 | ✗ 03 SSoT 未定义 |
| `AIRY_ENOENT` | — | — | —（未定义） | **-2**（冲突 EINVAL） | — | **-2**（冲突 EINVAL） | **-5** | -3 | ✗✗ 04/06 与 EINVAL 冲突；03 SSoT 未定义 |
| `AIRY_EMSGSIZE` | — | -1201 | -1201 | **-1109**（越段） | — | — | **-7** | -1201 | ✗ 04 越段；07 SYS 偏离 |
| `AIRY_ELIMIT` | — | **-7** | —（未定义） | — | — | — | — | 待定 | ✗ 03 SSoT 未定义 |
| `AIRY_EIO` | — | — | —（未定义） | **-5** | — | — | — | 待定 | ✗ 03 SSoT 未定义 |
| `AIRY_EPERSIST` | — | — | —（未定义） | **-1101** | — | — | — | 待定 | ✗ 03 SSoT 未定义 |
| `AIRY_ENOMSG` | — | -1202 | —（未定义） | — | — | — | — | -1202 | ✗ 03 SSoT 未定义 |
| `AIRY_SCHED_EXHAUSTED` | — | — | -1601 | — | — | — | — | -1603 | ✗ 03 SSoT 与 06 EBUSY 同段冲突 |
| `AIRY_ECog_TIMEOUT` | — | — | — | — | -1701 | — | — | -1701 | ✓ 一致（仅 05 定义） |
| `AIRY_EMODEL` | — | — | — | — | -1702 | — | — | -1702 | ✓ 一致（仅 05 定义） |
| `AIRY_EPHASE` | — | — | — | — | -1703 | — | — | -1703 | ✓ 一致（仅 05 定义） |
| `AIRY_ESCHED` | — | — | — | — | — | -1602 | — | -1602 | ✓ 一致（仅 06 定义） |
| `AIRY_ENOSYS` | — | — | — | — | — | — | -3 | 待定 | ✗ 03 SSoT 未定义 |
| `AIRY_EAGAIN` | — | — | — | — | — | — | -6 | 待定 | ✗ 03 SSoT 未定义 |
| `AIRY_EBADF` | — | — | — | — | — | — | -8 | 待定 | ✗ 03 SSoT 未定义 |
| `AIRY_ENOTSUP` | — | — | — | — | — | — | -10 | 待定 | ✗ 03 SSoT 未定义 |
| `AIRY_ECONFLICT` | — | — | — | — | — | — | -12 | 待定 | ✗ 03 SSoT 未定义 |

**问题统计**：

- ✗✗ 致命冲突（2 项）：05 COG 双码同值（TIMEOUT=EBUDGET=-1004）、04/06 ENOENT 与 EINVAL 同值（-2）
- ✗ SSoT 偏离（15 项）：01/02/07 多处偏离 03 SEC SSoT
- ✗ SSoT 未定义（9 项）：03 SEC SSoT 表未定义 ENOENT/EEXIST/ELIMIT/EIO/EPERSIST/ENOMSG/ENOSYS/EAGAIN/EBADF/ENOTSUP/ECONFLICT
- ✓ 一致（6 项）：EOK + 05 COG 三专属码 + 06 SCHED ESCHED

## 附录 B：命名变体分布矩阵

| 文件 | `are_cap_t` | `cap_t` | `airy_cap_t`（正确） | 函数前缀 |
|------|------------|---------|-------------------|---------|
| 01 RT | 1 处（第 501 行） | 0 | 0 | — |
| 02 IPC | 3 处（第 282/287/305 行） | 0 | 0 | — |
| 03 SEC | 22 处（第 66/79/81/189/190/195/210/211/225/251/351-369/545/556 行） | 0 | 0 | `airy_cap_*`（已对齐 ✓） |
| 04 MEM | 0 | 0 | 0 | — |
| 05 COG | 0 | 0 | 0 | — |
| 06 SCHED | 0 | 0 | 0 | — |
| 07 SYS | 0 | 8 处（第 207/224/241/258/275/293/326/400 行） | 0 | — |
| **合计** | **26 处** | **8 处** | **0 处** | — |

**结论**：正确形式 `airy_cap_t` 在全部 8 文件中**零使用**。函数前缀 `airy_cap_*` 已在 03 SEC 对齐，但类型名未对齐，形成"函数前缀正确 + 类型名错误"的割裂状态。

## 附录 C：`[SC]/[SS]/[IND]` 标注覆盖矩阵

| 文件 | `[SC]` 引言 | `[SC]` 内联 | 三层映射表 | 条目级标注 | 覆盖等级 |
|------|------------|------------|----------|----------|---------|
| README | —（定义模型） | — | 第 58-64 行 | — | 定义层 |
| 01 RT | **0 处** | **0 处** | **无** | **无** | **零覆盖** |
| 02 IPC | 1 处（第 28 行） | 0 | 无 | 无 | 引言级 |
| 03 SEC | 1 处（第 28 行） | 0 | 无 | 无 | 引言级 |
| 04 MEM | 1 处（第 28 行） | 0 | 无 | 无 | 引言级 |
| 05 COG | 1 处（第 28 行） | 0 | 无 | 无 | 引言级 |
| 06 SCHED | 1 处（第 29 行） | 0 | 无 | 无 | 引言级 |
| 07 SYS | 1 处（第 30 行） | 1 处（第 410 行） | **第 635-637 行**（完整） | 无 | **完整覆盖** |

**结论**：01 RT 零覆盖（最严重）；02-06 仅引言级；07 SYS 是唯一完整覆盖的标杆。v2.1 阶段 1 应以 07 SYS 为模板，强制 01-06 补齐三层映射表 + 条目级标注。

## 附录 D：行业生态对标速查表

| 协议/标准 | 版本 | 治理方 | 许可证 | 与本体系对接域 | v2.1 落地阶段 |
|----------|------|--------|--------|-------------|-------------|
| MCP | 2026-07-28 RC | LF AI Alliance | — | 02 IPC / 08 PROTO | 阶段 2 |
| A2A | v1.2 | LF / AAIF | Apache-2.0 | 01 RT / 08 PROTO | 阶段 2 |
| AG-UI | 1.0 | 开放社区 | — | 05 COG / 08 PROTO | 阶段 2 |
| ANP | — | 开放社区 | MIT | 03 SEC / 08 PROTO | 阶段 2 |
| IETF IAIP | 5 草案 | IETF | — | 01 RT / 09 INTEROP | 阶段 4 |
| OpenTelemetry | — | CNCF | Apache-2.0 | 02 IPC | 阶段 2 |
| OCI-AI | v1.3（强制） | OCI | — | 09 INTEROP | 阶段 4 |
| T/CAMETA | XX-2026 | 中国元宇宙生态协会 | — | 03 SEC / 09 INTEROP | 阶段 4 |
| OpenAI Agents SDK | 2026-04 | OpenAI | Apache-2.0 | 03 SEC / 05 COG（理念借鉴） | 不对接（非协议） |
| OWFa | 1.0 Patent Only | Open Web Foundation | — | 10 GOV | 阶段 3 |
| CNCF Lifecycle | — | CNCF | — | 10 GOV | 阶段 3 |
| OpenChain | ISO/IEC 5230 + 18974 | OpenChain Project | — | 10 GOV | 阶段 3 |
| seL4 | — | seL4 Foundation | GPL-2.0 / BSD-2-Clause | 03 SEC / 07 SYS（形式化借鉴） | 阶段 4 |

## 附录 E：参考文献

- MCP 2026-07-28 RC: https://modelcontextprotocol.io/specification/latest/index
- A2A v1.0.0: https://a2a-protocol.org/v1.0.0/specification
- A2A GitHub: https://github.com/a2aproject/A2A
- AG-UI: https://docs.ag-ui.com/introduction
- ANP 白皮书: https://www.agent-network-protocol.com/zh/specs/white-paper.html
- IETF draft-sz-dmsc-iaip-01: https://datatracker.ietf.org/doc/draft-sz-dmsc-iaip/
- IETF draft-song-anp-aip-00: https://datatracker.ietf.org/doc/draft-song-anp-aip/
- IETF draft-cui-ai-agent-discovery-invocation-01: https://datatracker.ietf.org/doc/draft-cui-ai-agent-discovery-invocation/
- IETF draft-liu-dmsc-acps-arc-00: https://datatracker.ietf.org/doc/draft-liu-dmsc-acps-arc/
- IETF draft-yan-iba-routing-security-requirements-01: https://datatracker.ietf.org/doc/draft-yan-iba-routing-security-requirements/
- OWFa 1.0 Patent Only: https://www.openwebfoundation.org/the-agreements/the-owf-1-0-agreements-granted-claims/owfa-1-0-patent-only
- CNCF Project Lifecycle: https://contribute.cncf.io/projects/lifecycle/
- OCI FAQ: https://opencontainers.org/faq/
- seL4 Licensing: https://www.sel4.org/Legal/license.html
- ISO/IEC 5230:2020: https://www.iso.org/standard/81039.html
- ISO/IEC 18974:2023: https://www.iso.org/standard/86450.html
- OpenAI Agents SDK: https://github.com/openai/openai-agents-python
- W3C Trace Context: https://www.w3.org/TR/trace-context/

***

Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
"From data intelligence emerges."
