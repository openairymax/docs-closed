Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
<!-- SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0 -->
<!-- 保密级别：SPHARX Ltd 内部参考，闭源不公开 -->
<!-- 版本：4.0 | 日期：2026-07-14 -->

# Airymax agentrt 开源文档 v4.0 深化审查报告

> **文档定位**：agentrt 开源文档（`docs/AirymaxRT/`）v4.0 深化审查报告。在 v1.0（综合 65/C+）、v2.0（修正后 72/B-）、v3.0（修正后预估 ~76/B）基础上执行 v3.0 修正持久性独立复核 + v3.0 修正副作用检测 + v4.0 新发现问题扫描 + 残留项状态复核。
> **保密级别**：SPHARX Ltd 内部参考，**闭源不公开**。
> **版本**：4.0（2026-07-14）。
> **审查范围**：仅 `docs/AirymaxRT/` 开源文档（87 个 .md + 1 个 .dox + 1 个 .drawio + 2 个 .json + 1 个 Dockerfile）；**不涉及** `docs/AirymaxOS/`、`docs-closed/`、`agentrt/` 源码、`agentrt-linux`、`docs/OpenStandards/`。
> **审查方法**：四维度（v3.0 修正持久性验证 + 副作用检测 + 新问题扫描 + 残留项复核）→ Grep 机器检查独立复核 → 关键文件 Read 深读 → 证据归档。
> **证据要求**：所有结论附 `文件路径:L行号` 或 Grep 命令与匹配数，可通过 Read/Grep 工具复核。
> **SPDX-License-Identifier**：AGPL-3.0-or-later OR Apache-2.0。

---

## 目录

- [1. 执行摘要](#1-执行摘要)
- [2. v3.0 修正持久性验证矩阵](#2-v30-修正持久性验证矩阵)
- [3. v3.0 修正副作用清单](#3-v30-修正副作用清单)
- [4. v4.0 新发现问题清单](#4-v40-新发现问题清单)
- [5. 残留项状态复核](#5-残留项状态复核)
- [6. 修正后评分预估](#6-修正后评分预估)
- [7. 附录](#7-附录)

---

## 1. 执行摘要

### 1.1 v3.0 修正持久性验证结果

| 维度 | 结果 | 说明 |
|------|------|------|
| 验证项总数 | 8 | 覆盖 v3.0 域2 全部修正项（IPC 头 SSoT + daemon→daemons + AgentRT→agentrt + 4 处断链 + Cupolas 7 子系统 + L1/L2/L3 cross-reference + Docs/ 大小写 + cupolas/src/mainpage.dox） |
| 完全持久 | **6** | IPC 头 SSoT / daemon→daemons / 0.1.1详细任务清单.md 断链 / Cupolas 7 子系统 / L1-L2-L3 cross-reference / Docs/ 大小写 |
| 部分持久 | **1** | AgentRT→agentrt：5 处 `AgentRT/` 残留（3 处 GitHub URL + 2 处 JSON schema 标题，经核实多为合法残留，但需统一） |
| 不适用 | **1** | `cupolas/src/mainpage.dox` 属源码文件（`agentrt/cupolas/src/mainpage.dox`），不在开源文档审查范围 |

**核心结论**：v3.0 域2 修正整体持久性良好（6/7 完全持久），IPC 头 SSoT 对齐、daemon→daemons、Cupolas 7 子系统等关键修正全部持久保留，无明显回退。

### 1.2 v4.0 新发现总览

| 级别 | 数量 | 关键问题 |
|------|------|---------|
| **P0** | 2 | v4.0-P0-1：`airy_err_t` 定义位置 SSoT 分裂（8 处仍引用 `cognition_types.h`，v3.0 P0-3 修正不完整）/ v4.0-P0-2：错误码分段表 SSoT 分裂（TERMINOLOGY.md 千位分段 vs L3 标准百位分段） |
| **P1** | 6 | `10-contracts/` 40 处 broken Markdown 链接 / `error_code_reference.md` 3 处 broken link（v3.0-P1-5 未修正）/ `01-doxygen-guide.md` broken links（v3.0-P2-1/P2-2 未修正）/ `../specifications/` 4 处 broken link / 04-mainpage.dox 协议数量 4 vs 9 / `ARE_EMSGSIZE` 引用未定义宏 |
| **P2** | 4 | `code_comment_template.md`/`naming_conventions.md` 3 处不存在文件引用 / `../architecture/` 路径错误 / GitHub repo URL 不一致 / `@since 1.1.0` 版本号不一致 |
| **合计** | **12** | — |

### 1.3 综合判定

> **agentrt 开源文档体系 v4.0 深化审查结论**：v3.0 修正整体持久（6/7 完全持久），无修正副作用。但 v4.0 发现 2 项 P0 级 SSoT 分裂问题：（1）`airy_err_t` 定义位置在 8 处文档中仍错误引用 `cognition_types.h`（v3.0 P0-3 修正仅覆盖 4 个文件，遗漏 6 个文件 8 处）；（2）错误码分段表在 TERMINOLOGY.md（千位分段 -1~-999/-1001~-1099/...）与 03-l3-security-governance.md（百位分段 -1~-99/-100~-199/...）完全不一致，构成 SSoT 分裂。新发现的 6 项 P1 + 4 项 P2 集中在 broken links（`10-contracts/` 40 处 + `../specifications/` 4 处 + 其他）与数量不一致（协议 4 vs 9），均为文档可用性问题。
>
> **修正后综合评分**：v3.0 修正后 ~76/B → v4.0 复审 **72/B-**（2 项新 P0 SSoT 分裂 -4 分，P1/P2 broken links -2 分，v3.0 持久性确认 +2 分）→ v4.0 修正后预估 **78/B**（修复 2 项 P0 +6 分，修复 P1/P2 +0 分，因属可用性问题加分有限）。

---

## 2. v3.0 修正持久性验证矩阵

每项均通过 Grep 工具独立执行并记录实际匹配数。

### 2.1 验证项总表

| # | 验证项 | Grep 命令 | 期望 | 实际 | 状态 |
|---|--------|----------|------|------|------|
| 1 | **IPC 头 SSoT 对齐** | `Grep "are_ipc_message_header" docs/AirymaxRT` | ≤2（仅迁移说明） | **2 处**（`02-l2-service-protocol.md:58` + `06-ipc/README.md:28`，均为"修正说明"段落中的历史引用，非实际定义） | ✅ 持久 |
| 2 | **IPC 头 SSoT 实际定义** | `Grep "struct airy_ipc_msg_hdr" docs/AirymaxRT` | >0 | **22 处/3 文件**（`02-l2-service-protocol.md` 14 处 + `06-ipc/README.md` 7 处 + `06-iron9-shared-model.md` 1 处），含 `_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128)` 真实编译期校验 | ✅ 持久 |
| 3 | **daemon→daemons** | `Grep "agentrt/daemon/" docs/AirymaxRT` | 0 残留 | **0 匹配** | ✅ 持久 |
| 4 | **AgentRT→agentrt** | `Grep "AgentRT/" docs/AirymaxRT` | 0 或仅合法残留 | **5 处**（3 处 GitHub URL `github.com/spharx/AgentRT/` + 2 处 JSON schema 标题 `"Agent Contract Schema (AgentRT/)"` / `"Skill Contract Schema (AgentRT/)"`），经核实 GitHub repo 名可能保留大写，JSON schema 标题为元数据 | ⚠️ 部分持久 |
| 5 | **0.1.1详细任务清单.md 断链** | `Grep "0\.1\.1详细任务清单\.md" docs/AirymaxRT` | 0 残留 | **0 匹配** | ✅ 持久 |
| 6 | **Cupolas 4→7 子系统** | `Grep "四重纵深防护" docs/AirymaxRT` | 0 残留 | **0 匹配**（`04-mainpage.dox:43` 已改为"七大子系统"，L57 添加"四重防护链"vs"七大子系统"区分说明） | ✅ 持久 |
| 7 | **L1/L2/L3 cross-reference** | `Grep "L1_runtime_interface\|L2_service_protocol\|L3_security_governance" docs/AirymaxRT` | 0 残留 | **0 匹配** | ✅ 持久 |
| 8 | **Docs/→docs/ 大小写** | `Grep "Docs/" docs/AirymaxRT` | 0 残留 | **0 匹配** | ✅ 持久 |

### 2.2 验证小结

- **6/7 项完全持久**：v3.0 域2 修正质量整体良好，IPC 头 SSoT 对齐、daemon→daemons（46 处）、Cupolas 7 子系统、L1/L2/L3 cross-reference（15 处）、0.1.1详细任务清单.md 断链（4 处）、Docs/ 大小写（2 处）均经 Grep 独立复核确认持久。
- **1/7 项部分持久**：AgentRT→agentrt 修正后仍有 5 处 `AgentRT/` 残留，但经核实多为合法残留（GitHub URL 中的 repo 名保留大写、JSON schema 标题元数据），需进一步核实 GitHub repo 实际名称以判定是否需要修正。
- **cupolas/src/mainpage.dox**：该文件位于 `agentrt/cupolas/src/mainpage.dox`（源码目录），不在 `docs/AirymaxRT/` 开源文档范围内，本次审查不覆盖。

---

## 3. v3.0 修正副作用清单

### 3.1 副作用检测矩阵

| # | 检测项 | 方法 | 结果 | 状态 |
|---|--------|------|------|------|
| 1 | **daemon→daemons 误替换** | `Grep "agentrt/daemons/" docs/AirymaxRT` 检查是否有过度替换（如 `agentrt/daemons/` 出现在不应出现的位置） | **10+ 处**正常使用（如 `agentrt/daemons/common/include/` / `agentrt/daemons/observe_d/`），无误替换 | ✅ 无副作用 |
| 2 | **AgentRT→agentrt 上下文割裂** | 检查修正后是否有大小写混乱（如同一句子中 `agentrt` 与 `AgentRT` 混用） | `04-mainpage.dox` 中产品名 `AgentRT`（大写）与目录名 `agentrt/`（小写）共存，符合惯例（产品名大写、路径小写），无割裂 | ✅ 无副作用 |
| 3 | **IPC 头修正引入新断链** | 检查 `struct airy_ipc_msg_hdr` 引用是否有指向不存在文件的链接 | 22 处引用均为代码示例或文本引用，无 Markdown 链接断链 | ✅ 无副作用 |
| 4 | **Cupolas 7 子系统补全引入不一致** | 检查 `04-mainpage.dox` 7 子系统清单与 `TERMINOLOGY.md` 是否一致 | `04-mainpage.dox:47-53` 列 7 子系统（Workbench/Permission/Sanitizer/Audit/Guards/Security Vault/Network Security）与 `TERMINOLOGY.md:193` 一致 | ✅ 无副作用 |
| 5 | **新断链检测** | `Grep "0\.1\.1详细任务清单\|L1_runtime_interface\|Docs/" docs/AirymaxRT` | 0 匹配，v3.0 修正未引入新断链 | ✅ 无副作用 |

### 3.2 副作用检测小结

> **v3.0 修正无副作用**：daemon→daemons 替换精确无误替换；IPC 头 SSoT 对齐未引入新断链；Cupolas 7 子系统补全与权威术语表一致。v3.0 修正质量良好。

---

## 4. v4.0 新发现问题清单

### 4.1 P0 级问题（2 项）

#### v4.0-P0-1：`airy_err_t` 定义位置 SSoT 分裂（v3.0 P0-3 修正不完整）

| 属性 | 内容 |
|------|------|
| **问题描述** | v3.0 P0-3 修正声明"SSoT 声明 airy_err_t 在 cognition_types.h"已修正为 `airy_types.h:41`，但实际仅修正了 4 个文件（TERMINOLOGY.md / 06-iron9-shared-model.md / 00-architectural-principles.md / 03-protocol-contract.md），**遗漏了 6 个文件共 8 处**仍错误引用 `cognition_types.h` 作为 `airy_err_t` 的定义位置。 |
| **证据** | **仍错误引用 `cognition_types.h`（8 处/6 文件）**：<br/>1. `20-modules/10-contracts/04-syscall-api-contract.md:94`："类型 `airy_err_t = int32_t` 定义于 `cognition_types.h`"<br/>2. `20-modules/10-contracts/06-glossary-index.md:173`："类型 `airy_err_t = int32_t` 定义于 `cognition_types.h`"<br/>3. `20-modules/10-contracts/06-glossary-index.md:185`："`airy_err_t` 类型见 `cognition_types.h`"<br/>4. `30-interfaces/05-runtime-interfaces/01-l1-runtime-interface.md:50`："类型 `airy_err_t = int32_t`（定义于 `cognition_types.h`）"<br/>5. `30-interfaces/05-runtime-interfaces/03-l3-security-governance.md:304`："类型 `airy_err_t = int32_t` 定义于 `cognition_types.h`"<br/>6. `30-interfaces/README.md:78`："类型 `airy_err_t = int32_t` 定义于 `cognition_types.h`"<br/>7. `10-architecture/05-syscall.md:638`："类型 `airy_err_t = int32_t` 定义于 `cognition_types.h`"<br/>8. `20-modules/10-contracts/05-logging-format.md:301`："`airy_err_t` 类型见 `cognition_types.h`"<br/><br/>**已正确修正为 `airy_types.h:41`（6 处/4 文件）**：<br/>- `TERMINOLOGY.md:209`："类型定义于 `airy_types.h:41`，**非 cognition_types.h**" ✅<br/>- `06-iron9-shared-model.md:217,225` ✅<br/>- `00-architectural-principles.md:921,925` ✅<br/>- `03-protocol-contract.md:490,692` ✅<br/><br/>**v3.0 验证报告检查项 #3 误判**：`fix-verification-report-v3.md` L131 检查项 #3 "airy_err_t in cognition_types.h = 0 matches PASS"，但该检查搜索的是 `cognition_types.h` **文件内**是否包含 `airy_err_t`（源码文件检查），而非**文档中对 `cognition_types.h` 的引用**（文档引用检查）。这导致 8 处文档引用遗漏。 |
| **影响评估** | (1) SSoT 分裂：同一 `airy_err_t` 类型定义位置在 14 处文档声明中，6 处正确引用 `airy_types.h:41`，8 处错误引用 `cognition_types.h`，开发者无法确定权威定义位置；(2) 违反 IRON-014（[SC] 头文件单一数据源）；(3) v3.0 P0-3 修正声明"已修正"但实际覆盖不完整。 |
| **修复建议** | 将 8 处 `cognition_types.h` 引用统一修正为 `airy_types.h:41`，并添加"**非 cognition_types.h**"声明（与 TERMINOLOGY.md:209 一致）。 |
| **工作量估算** | ~1h（8 处 Edit） |

#### v4.0-P0-2：错误码分段表 SSoT 分裂（TERMINOLOGY.md vs L3 标准）

| 属性 | 内容 |
|------|------|
| **问题描述** | 错误码分段表在两个权威文档中完全不一致：TERMINOLOGY.md 使用**千位分段**（-1~-999 / -1001~-1099 / -2001~-2099 / ... / -9001~-9099），而 03-l3-security-governance.md 使用**百位分段**（-1~-99 / -100~-199 / -200~-299 / ... / -800~-889）。两套分段方案数值范围完全不同，构成 SSoT 分裂。 |
| **证据** | **TERMINOLOGY.md:586-598（千位分段，9 段）**：<br/>```<br/>| 成功 | 0 | AIRY_EOK |<br/>| 通用 | -1 ~ -999 | AIRY_EUNKNOWN 等 |<br/>| Task | -1001 ~ -1099 | 任务相关错误 |<br/>| Memory | -2001 ~ -2099 | 记忆相关错误 |<br/>| Session | -3001 ~ -3099 | 会话相关错误 |<br/>| Telemetry | -4001 ~ -4099 | 遥测相关错误 |<br/>| Internal | -5001 ~ -5099 | 内部通用错误 |<br/>| Skill | -6001 ~ -6099 | 技能相关错误 |<br/>| Agent | -7001 ~ -7099 | Agent 相关错误 |<br/>| Sandbox | -8001 ~ -8099 | 沙箱相关错误 |<br/>| Security | -9001 ~ -9099 | 安全相关错误 |<br/>```<br/><br/>**03-l3-security-governance.md:306-334（百位分段，9 段）**：<br/>```<br/>| 通用 | -1 ~ -99 | 基础错误（参数、内存、权限、超时等） |<br/>| 系统 | -100 ~ -199 | 平台、线程、socket、文件 |<br/>| 内核 | -200 ~ -299 | IPC、任务、调度、内存 |<br/>| 服务 | -300 ~ -399 | 服务状态、依赖、负载均衡 |<br/>| LLM | -400 ~ -499 | LLM provider、限流、上下文 |<br/>| 执行 | -500 ~ -599 | 工具执行、沙箱、超时 |<br/>| 记忆 | -600 ~ -699 | 记忆读写、查询、演化 |<br/>| 安全 | -700 ~ -799 | 权限、净化、审计、沙箱 |<br/>| 协议 | -800 ~ -889 | 编排、协调、补偿 |<br/>```<br/><br/>**冲突示例**：`AIRY_EUNKNOWN` 在 TERMINOLOGY.md 属"通用段 -1~-999"，在 L3 标准属"通用段 -1~-99"；`AIRY_ESYS_NOT_INIT (-101)` 在 TERMINOLOGY.md 属"通用段 -1~-999"，在 L3 标准属"系统段 -100~-199"；Task 相关错误在 TERMINOLOGY.md 是 -1001~-1099，在 L3 标准是 -200~-299（内核段）。 |
| **影响评估** | (1) 错误码分段定义冲突：实现者无法确定正确的分段方案；(2) 同一错误码值在不同文档中归属不同段；(3) 违反 v3.0 域1 错误码 SSoT 统一目标；(4) L3 标准 §5.3"禁令#4 禁止跨段借用"在两套分段下无法执行。 |
| **修复建议** | 确定唯一权威分段方案（建议以 03-l3-security-governance.md 百位分段为准，因其更精细且与 POSIX errno 负值段更兼容），统一 TERMINOLOGY.md 附录 C 分段表。 |
| **工作量估算** | ~2h（需评估两套方案的合理性 + 统一 + 验证） |

---

### 4.2 P1 级问题（6 项）

#### v4.0-P1-1：`20-modules/10-contracts/` 目录下约 40 处 broken Markdown 链接

| 属性 | 内容 |
|------|------|
| **问题描述** | `20-modules/10-contracts/` 目录下 5 个契约文档相互引用时使用旧命名约定（无 NN- 前缀），与实际文件名（NN- 前缀命名约定）不匹配，构成系统性 broken links。v3.0 审查了 `05-runtime-interfaces/` 目录下的同类问题（15 处，v3.0-P1-2），但**遗漏了** `10-contracts/` 目录下的同类问题。 |
| **证据** | 实际文件名：`01-agent-contract.md` / `02-skill-contract.md` / `03-protocol-contract.md` / `04-syscall-api-contract.md` / `05-logging-format.md`<br/>错误引用：`agent_contract.md` / `skill_contract.md` / `protocol_contract.md` / `syscall_api_contract.md` / `logging_format.md`<br/><br/>**40 处分布**：<br/>- `06-glossary-index.md`：**29 处** Markdown 链接（L84/85/86/92/93/94/100/101/102/108/109/110/116/117/118/137/138/139/140/146/147/148/149/155/156/157/158/187/199）<br/>- `04-syscall-api-contract.md`：**3 处**（L1315/1360/1362）<br/>- `03-protocol-contract.md`：**4 处**（L44/660/867/868）<br/>- `05-logging-format.md`：**3 处**（L63/950/951）<br/>- `02-skill-contract.md`：**1 处**（L995） |
| **影响评估** | 同目录内 cross-reference 全部 broken；Markdown 渲染器与 CI 链接检查器报错；外部读者无法在 5 个契约文档间导航。 |
| **修复建议** | 全量替换（5 类文件名）：<br/>- `agent_contract.md` → `01-agent-contract.md`<br/>- `skill_contract.md` → `02-skill-contract.md`<br/>- `protocol_contract.md` → `03-protocol-contract.md`<br/>- `syscall_api_contract.md` → `04-syscall-api-contract.md`<br/>- `logging_format.md` → `05-logging-format.md`<br/>**注意**：需区分 Markdown 链接 `[文本](./xxx.md)`（需修正）与纯文本引用（如表格中"agent_contract.md - 3.1 节"，可保留或统一）。 |
| **工作量估算** | ~1h（40 处 Edit，需逐个核实是链接还是文本） |

#### v4.0-P1-2：`error_code_reference.md` broken link 3 处（v3.0-P1-5 未修正）

| 属性 | 内容 |
|------|------|
| **问题描述** | v3.0-P1-5 识别了 `06-glossary-index.md` 两处 `error_code_reference.md` broken link，但**未修正**。v4.0 额外发现 `05-logging-format.md:301` 第 3 处引用。 |
| **证据** | 3 处引用不存在的 `error_code_reference.md`：<br/>1. `06-glossary-index.md:185`：`完整映射关系参见 [error_code_reference.md](../../50-engineering-standards/50-project-erp/error_code_reference.md)`<br/>2. `06-glossary-index.md:187`：`[error_code_reference.md](../../50-engineering-standards/50-project-erp/error_code_reference.md)`<br/>3. `05-logging-format.md:301`：`SDK/外部层使用十六进制字符串（如 "0x0003"，定义于 error_code_reference.md）`（纯文本引用，非链接，但仍指向不存在的文件）<br/><br/>**实际文件**：`50-engineering-standards/50-project-erp/` 目录下仅有 `README.md` + `project_erp.md`，无 `error_code_reference.md`。 |
| **影响评估** | 链接 broken；开发者无法访问错误码完整映射关系。 |
| **修复建议** | `error_code_reference.md` → `project_erp.md`（3 处）。 |
| **工作量估算** | ~0.1h |

#### v4.0-P1-3：`01-doxygen-guide.md` v3.0-P2-1/P2-2 broken links 未修正

| 属性 | 内容 |
|------|------|
| **问题描述** | v3.0-P2-1（L326 路径错误）和 v3.0-P2-2（L327 引用不存在的 `code_comment_template.md`）均**未修正**。v4.0 额外发现 L13 纯文本引用 `Code_comment_template.md`（大写 C）。 |
| **证据** | 1. `01-doxygen-guide.md:326`：`- **Airymax 架构原则**: ../../00-architectural-principles.md` —— 应为 `../10-architecture/00-architectural-principles.md`（`../../00-architectural-principles.md` 解析到 `docs/00-architectural-principles.md`，不存在）<br/>2. `01-doxygen-guide.md:327`：`- **代码注释规范**: ../../50-engineering-standards/10-coding-style/code_comment_template.md` —— `code_comment_template.md` 不存在<br/>3. `01-doxygen-guide.md:13`：`✅ 遵循 \`Code_comment_template.md\` C/C++ 注释规范` —— 纯文本引用不存在的文件（大写 C） |
| **影响评估** | broken links；开发者无法访问架构原则和代码注释规范。 |
| **修复建议** | (1) L326：`../../00-architectural-principles.md` → `../10-architecture/00-architectural-principles.md`；(2) L327：删除该行或改为指向 `coding_conventions.md`；(3) L13：删除 `Code_comment_template.md` 引用或改为 `coding_conventions.md`。 |
| **工作量估算** | ~0.1h |

#### v4.0-P1-4：`../specifications/` 路径 broken links（4 处）

| 属性 | 内容 |
|------|------|
| **问题描述** | 4 处文档引用 `../specifications/` 或 `../../specifications/` 路径，但 `specifications/` 目录不存在（实际目录为 `20-modules/`）。 |
| **证据** | 1. `140-application-development/24-create-agent.md:98`：`[agent_contract.md](../specifications/10-contracts/01-agent-contract.md)` —— 双重错误（`specifications/` 不存在 + `agent_contract.md` 旧文件名）<br/>2. `140-application-development/24-create-agent.md:701`：`[Agent 契约规范](../specifications/10-contracts/01-agent-contract.md)` —— `specifications/` 不存在<br/>3. `140-application-development/25-create-skill.md:656`：`[Skill 契约规范](../specifications/10-contracts/02-skill-contract.md)` —— `specifications/` 不存在<br/>4. `30-interfaces/10-algorithms/README.md:1736`：`[功能需求文档](../../specifications/manuals_module_requirements.md)` —— `specifications/` 不存在 |
| **影响评估** | 跨目录链接 broken；开发者无法从应用开发文档导航到契约规范。 |
| **修复建议** | `../specifications/` → `../20-modules/`（3 处）；`../../specifications/` → `../../20-modules/`（1 处）。同时修正 L98 的 `agent_contract.md` → `01-agent-contract.md`。 |
| **工作量估算** | ~0.2h |

#### v4.0-P1-5：04-mainpage.dox 协议数量不一致（4 vs 9）

| 属性 | 内容 |
|------|------|
| **问题描述** | `04-mainpage.dox` 的"多协议支持"表格仅列 4 种协议（JSON-RPC/MCP/A2A/OpenAI），但 TERMINOLOGY.md 等权威文档定义 9 种协议，构成数量不一致。 |
| **证据** | **04-mainpage.dox:108-113（4 种）**：<br/>```<br/>| **JSON-RPC 2.0** | 2.0 | 标准远程过程调用 |<br/>| **MCP** | 0.5+ | Model Context Protocol，工具集成 |<br/>| **A2A** | 0.2+ | Agent-to-Agent，智能体协作 |<br/>| **OpenAI API** | v1 | OpenAI兼容接口 |<br/>```<br/><br/>**TERMINOLOGY.md:338（9 种）**："支持 9 种协议类型：JSON-RPC 2.0、MCP v1、A2A v0.3、OpenAI、Claude、OpenJiuwen、OpenClaw、ChinaEco、AGNTCY ACP"<br/>**18-protocol-integration.md:9（9 种）**："支持 JSON-RPC 2.0、MCP v1、A2A v0.3、OpenAI、Claude、OpenJiuwen、OpenClaw、ChinaEco、AGNTCY ACP 共 9 种协议"<br/>**21-best-practices.md:271,305（9 种）**：均引用"9 种协议" |
| **影响评估** | Doxygen 主页生成的文档与权威术语表矛盾；外部开发者对协议数量产生混淆。 |
| **修复建议** | 补全 `04-mainpage.dox:108-113` 协议表为 9 种（添加 Claude/OpenJiuwen/OpenClaw/ChinaEco/AGNTCY ACP），或在表格下方注明"主要协议，完整列表见 TERMINOLOGY.md"。 |
| **工作量估算** | ~0.3h |

#### v4.0-P1-6：`ARE_EMSGSIZE` / `ARE_IPC_MAX_MSG_SIZE` 引用未定义的宏

| 属性 | 内容 |
|------|------|
| **问题描述** | `01-l1-runtime-interface.md` 在一致性要求（L136）和 CTS 测试用例（L706）中引用 `ARE_EMSGSIZE` 和 `ARE_IPC_MAX_MSG_SIZE` 宏，但前者在错误码表（L52-64）中未定义，后者在全文中未定义。 |
| **证据** | 1. `01-l1-runtime-interface.md:136`：`are_ipc_send 在 msg->size > ARE_IPC_MAX_MSG_SIZE（默认 512 KiB）时返回 ARE_EMSGSIZE` —— `ARE_EMSGSIZE` 未在 L52-64 错误码表中定义；`ARE_IPC_MAX_MSG_SIZE` 宏未在全文定义<br/>2. `01-l1-runtime-interface.md:706`：`| L1-CTS-002 | IPC | are_ipc_send 超长消息（> 512 KiB） | 返回 ARE_EMSGSIZE |` —— 同上<br/><br/>**L52-64 错误码表仅定义 11 个码**：ARE_OK/ARE_EPERM/ARE_ENOENT/ARE_ENOMEM/ARE_EINVAL/ARE_EBUSY/ARE_ENOSYS/ARE_ENOTSUP/ARE_ENOTINIT/ARE_ETIMEDOUT/ARE_EUNKNOWN，无 `ARE_EMSGSIZE`。 |
| **影响评估** | 代码示例引用未定义宏；CTS 测试用例无法执行；实现者无法确定超长消息的错误返回码。 |
| **修复建议** | (1) 在 L52-64 错误码表中添加 `ARE_EMSGSIZE`（对齐 POSIX EMSGSIZE，如 -90）；(2) 在 §2.2 中定义 `ARE_IPC_MAX_MSG_SIZE` 宏（如 `#define ARE_IPC_MAX_MSG_SIZE (512u * 1024u)`）。 |
| **工作量估算** | ~0.2h |

---

### 4.3 P2 级问题（4 项）

#### v4.0-P2-1：`code_comment_template.md` / `naming_conventions.md` 不存在的文件引用（3 处）

- **证据**：
  - `01-doxygen-guide.md:13`：`✅ 遵循 \`Code_comment_template.md\` C/C++ 注释规范`（大写 C，文本引用）
  - `01-doxygen-guide.md:327`：`../../50-engineering-standards/10-coding-style/code_comment_template.md`（链接，文件不存在）
  - `30-interfaces/README.md:109`：`[命名规范](../50-engineering-standards/10-coding-style/naming_conventions.md)`（链接，文件不存在）
- **实际目录**：`50-engineering-standards/10-coding-style/` 下仅有 `C_Cpp_coding_style.md` / `Go_coding_style.md` / `Rust_coding_style.md` / `coding_conventions.md` / `scripting_coding_style.md` / `README.md`
- **修复**：删除引用或改为指向 `coding_conventions.md`
- **工作量**：~0.05h
- **注**：与 v4.0-P1-3 部分重叠（L13/L327）

#### v4.0-P2-2：`24-create-agent.md:97` `../architecture/` 路径错误

- **证据**：`140-application-development/24-create-agent.md:97`：`[00-architectural-principles.md](../architecture/00-architectural-principles.md)`
- **问题**：`architecture/` 目录不存在，实际为 `10-architecture/`
- **修复**：`../architecture/` → `../10-architecture/`
- **工作量**：~0.05h

#### v4.0-P2-3：GitHub repo URL 不一致（17 处/4 种不同 URL）

- **证据**：`Grep "github\.com/spharx" docs/AirymaxRT` = 17 处，4 种不同 URL：
  - `github.com/spharx/AgentRT`（大写 AgentRT）：3 处（Dockerfile:12 / docker/README.md:497 / quickstart.md:580/581）
  - `github.com/spharx/Airymax`（大写 Airymax）：1 处（quickstart.md:48）
  - `github.com/spharx/agentrt-go`（小写）：5 处（go/README.md:32/49/111/374/405/406）
  - `github.com/spharxworks/agentrt-toolkit-go`（不同 org `spharxworks`）：4 处（protocol-quickstart.md:234/235 / protocol-guide.md:424/437/438）
  - `github.com/spharx/agentrt/toolkit/go/agentrt`（含路径分隔）：1 处（02-logging.md:742）
- **问题**：多个不同组织名（`spharx` vs `spharxworks`）、不同 repo 名（`AgentRT` vs `agentrt-go` vs `agentrt-toolkit-go` vs `Airymax`）。需核实实际 GitHub repo 名称，统一引用。
- **修复**：核实实际 GitHub repo 名称后统一；若为不同 repo（主仓库 vs SDK 仓库），需在文档中明确区分
- **工作量**：~0.5h（核实 + 修正）

#### v4.0-P2-4：`01-doxygen-guide.md:299` `@since 1.1.0` 版本号与当前 0.1.1 不一致

- **证据**：`01-doxygen-guide.md:299`：`* @since 1.1.0 新增此函数`
- **问题**：当前项目版本为 0.1.1（见 README.md / 闭源手册），`@since 1.1.0` 引用未来版本号
- **说明**：其他文档中 `v1.1.0` 出现 7 处（22-known-issues.md:89 / 20-manager-development.md:459 / 02-build-guide.md:425 / 19-prompt-engineering.md:950/978/1004 / 10-migration-guide.md:409），多为历史版本记录或 prompt 模板版本，可能合法。但 `@since 1.1.0` 在 Doxygen 注释中暗示函数自 1.1.0 版本引入，与当前 0.1.1 不一致。
- **修复**：核实是否应为 `@since 0.1.1`，或确为未来版本预留
- **工作量**：~0.05h

---

### 4.4 正面发现（v3.0 修正质量确认）

| # | 正面发现 | 证据 |
|---|---------|------|
| 1 | **IPC 头 SSoT 完全对齐** | `struct airy_ipc_msg_hdr` 在 3 文件 22 处一致使用，含 `_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128)` 真实编译期校验；`are_ipc_message_header` 仅 2 处迁移说明 |
| 2 | **daemon→daemons 精确修正** | 46 处替换全部正确，0 处 `agentrt/daemon/` 残留，10+ 处 `agentrt/daemons/` 正常使用，无误替换 |
| 3 | **Cupolas 7 子系统补全** | `04-mainpage.dox:43-53` 列 7 子系统（Workbench/Permission/Sanitizer/Audit/Guards/Security Vault/Network Security），与 `TERMINOLOGY.md:193` 一致；L57 添加"四重防护链"vs"七大子系统"区分说明 |
| 4 | **L1/L2/L3 cross-reference 修正** | 15 处旧文件名（`L1_runtime_interface.md` 等）全部修正为 NN- 前缀（`01-l1-runtime-interface.md` 等），0 残留 |
| 5 | **断链修正持久** | 4 处 `0.1.1详细任务清单.md` 断链全部修正，0 残留；2 处 `Docs/` 大小写全部修正 |
| 6 | **12 个 daemon 跨文档一致** | `TERMINOLOGY.md` 附录 A / `04-mainpage.dox` / `01-system-architecture.md` / `04-microcorert.md` / `02-l2-service-protocol.md` 均确认 12 个 daemon |
| 7 | **Doxygen 注释规范良好** | `30-interfaces/60-syscalls/` 目录下文档（01-agent.md / 02-memory.md / 03-session.md / 04-skill.md / 05-task.md / 06-telemetry.md）均有完整 @brief/@param/@return 注释 |

---

## 5. 残留项状态复核

### 5.1 R2-1（are_ipc_message_t 便利包装）

| 属性 | 内容 |
|------|------|
| **来源** | v3.0 验证报告 §5.2 R2-1 |
| **原始描述** | `02-l2-service-protocol.md:131` 仍有 `are_ipc_message_t`（非 `are_ipc_message_header_t`）便利包装类型 |
| **v4.0 复核结果** | **仍存在，状态未变** |
| **证据** | `Grep "are_ipc_message_t" docs/AirymaxRT` = **9 处/2 文件**：<br/>- `01-l1-runtime-interface.md`：5 处（L90 定义 + L103/110/125/130 函数签名）—— L1 内核级 IPC 消息（40 字节，5 字段），与 L2 的 `struct airy_ipc_msg_hdr`（128 字节，8 字段）是不同层级<br/>- `02-l2-service-protocol.md`：4 处（L131 定义 + L712/713/737 代码示例）—— L2 特有便利包装类型<br/><br/>**判定**：`are_ipc_message_t` 是 L1/L2 标准的合法便利类型（非 SSoT 头结构体），与 `struct airy_ipc_msg_hdr` 是不同概念。L1 的 `are_ipc_message_t`（40 字节内核级消息）与 L2 的 `struct airy_ipc_msg_hdr`（128 字节应用层头）分层合理。**建议保留**，但需在文档中明确区分两者关系。 |
| **处理建议** | 保留（L2 特有便利类型），无需修正 |

### 5.2 R3-2（docs/AirymaxAgentOS/ 路径 7 处）

| 属性 | 内容 |
|------|------|
| **来源** | v3.0 验证报告 §5.3 R3-2 |
| **原始描述** | 7 处 `docs/AirymaxAgentOS/` 路径（属 P1-9 工作流 D 范围） |
| **v4.0 复核结果** | **✅ 已修正** |
| **证据** | `Grep "docs/AirymaxAgentOS" docs/AirymaxRT` = **0 匹配** |
| **处理建议** | 无需进一步处理 |

### 5.3 残留项汇总

| 残留项 | v3.0 状态 | v4.0 复核 | 处理建议 |
|--------|----------|----------|---------|
| R2-1（are_ipc_message_t 便利包装） | P2，1.0.1 评估 | 仍存在 9 处，合法保留 | 保留 |
| R3-2（docs/AirymaxAgentOS/ 7 处） | P1，1.0.1 M1 中期 | ✅ 已修正（0 处） | 已关闭 |

---

## 6. 修正后评分预估

### 6.1 评分变化轨迹

| 版本阶段 | 综合评分 | 级别 | 变化 | 主要原因 |
|---------|---------|------|------|---------|
| v1.0（初始审查） | 65 | C+ | — | 8 项 P0 + 多项 P1/P2 |
| v2.0（修正后） | 72 | B- | +7 | 9/10 P0 修正 |
| v3.0（复审） | 66 | C+ | -6 | 新发现 10 P0 + 19 P1 + 18 P2 |
| v3.0（修正后预估） | ~76 | B | +10 | 10 P0 全部清零 + 主要 P1 修正 |
| **v4.0（复审）** | **72** | **B-** | **-4** | **2 项新 P0 SSoT 分裂 + 6 项 P1 broken links** |
| **v4.0（修正后预估）** | **~78** | **B** | **+6** | **修复 2 项 P0 SSoT 分裂 + P1 broken links** |

### 6.2 评分维度分析

| 维度 | v3.0 修正后 | v4.0 复审 | v4.0 修正后 | 变化 | 主要原因 |
|------|------------|----------|------------|------|---------|
| 规范声明层（35%） | 78 | 72 | 78 | -6→+6 | v4.0-P0-1 airy_err_t SSoT 分裂 + v4.0-P0-2 错误码分段分裂 |
| 方案设计层（40%） | 77 | 75 | 78 | -2→+3 | v4.0-P1-5 协议数量 4 vs 9 |
| 实现落地层（25%） | 72 | 70 | 74 | -2→+4 | v4.0-P1-1/P1-4 broken links + v4.0-P1-6 未定义宏 |
| **加权综合** | **~76** | **72** | **~78** | **-4→+6** | — |

### 6.3 v4.0 修正后评分说明

> **v4.0 修正后预估 ~78/B** 的计算逻辑：
>
> 1. **v3.0 修正后基线**：~76/B（v3.0 验证报告 §6.1）
> 2. **v4.0 新发现扣分**：
>    - v4.0-P0-1（airy_err_t SSoT 分裂 8 处）：-3 分（P0 级，SSoT 完整性受损）
>    - v4.0-P0-2（错误码分段表 SSoT 分裂）：-2 分（P0 级，分段方案冲突）
>    - v4.0-P1-1（10-contracts/ 40 处 broken links）：-1 分（系统性路径错误）
>    - v4.0-P1-2~P1-6（5 项 P1）：-1.5 分（broken links + 数量不一致 + 未定义宏）
>    - v4.0-P2-1~P2-4（4 项 P2）：-0.5 分（次要路径/版本号问题）
> 3. **v4.0 修正后预估**：76 - 8 + 10（修复 2 项 P0 SSoT 分裂 +6，修复 P1/P2 broken links +4）= **~78/B**
>
> **关键判定**：v4.0 发现的 2 项 P0 均为 v3.0 修正不完整导致的 SSoT 分裂（airy_err_t 定义位置 + 错误码分段表），修复后可恢复 SSoT 完整性。6 项 P1 集中在 broken links，均为文档可用性问题，不影响架构设计正确性。

### 6.4 是否达到"可开发"状态

| 判定标准 | v3.0 状态 | v4.0 状态 | 说明 |
|---------|----------|----------|------|
| 架构设计完成度 | ✅ 达标 | ✅ 达标 | MicroCoreRT / CoreLoopThree / MemoryRovol / Thinkdual / Cupolas / 12 Daemons 完整 |
| 工程标准规范 | ✅ 达标 | ✅ 达标 | 50-engineering-standards 共享层完整 |
| 无方案冲突点 | ✅ 达标 | ⚠️ **部分达标** | v4.0-P0-2 错误码分段表 SSoT 分裂 |
| 跨平台一致性 | ✅ 达标 | ✅ 达标 | magic 值/函数前缀/SCHED_EXT 一致 |
| SSoT 收敛 | ✅ 达标 | ⚠️ **部分达标** | v4.0-P0-1 airy_err_t 定义位置 SSoT 分裂 + v4.0-P0-2 错误码分段 SSoT 分裂 |
| 历史问题修复 | ✅ 达标 | ✅ 达标 | v3.0 修正 6/7 持久 |
| 文档可用性 | ✅ 达标 | ⚠️ **部分达标** | 40 处 10-contracts/ broken links + 4 处 specifications/ broken links |

> **总体判定**：agentrt 开源文档体系 v4.0 复审后**接近"可开发"状态**，但需先修复 2 项 P0 SSoT 分裂（airy_err_t 定义位置 + 错误码分段表）以恢复 SSoT 完整性。修复后即可达到"可开发"状态。

---

## 7. 附录

### 7.1 审查范围

| 类别 | 数量 | 路径 |
|------|------|------|
| Markdown 文档 | 87 | `docs/AirymaxRT/**/*.md` |
| Doxygen 文件 | 1 | `docs/AirymaxRT/30-interfaces/04-mainpage.dox` |
| Drawio 文件 | 1 | `docs/AirymaxRT/10-architecture/60-diagrams/03-overall-architecture.drawio` |
| JSON Schema | 2 | `docs/AirymaxRT/20-modules/10-contracts/01-agent-contract-schema.json` / `02-skill-contract-schema.json` |
| Dockerfile | 1 | `docs/AirymaxRT/30-interfaces/40-docker/Dockerfile` |
| **合计** | **92** | — |

### 7.2 v4.0 验证命令汇总

```bash
# v3.0 修正持久性验证
Grep "are_ipc_message_header" docs/AirymaxRT
# 结果：2 处（均为迁移说明），IPC 头 SSoT 对齐持久

Grep "agentrt/daemon/" docs/AirymaxRT
# 结果：0 匹配，daemon→daemons 持久

Grep "AgentRT/" docs/AirymaxRT
# 结果：5 处（3 GitHub URL + 2 JSON schema 标题），部分持久

Grep "0\.1\.1详细任务清单\.md" docs/AirymaxRT
# 结果：0 匹配，断链修正持久

Grep "四重纵深防护" docs/AirymaxRT
# 结果：0 匹配，Cupolas 7 子系统持久

Grep "L1_runtime_interface|L2_service_protocol|L3_security_governance" docs/AirymaxRT
# 结果：0 匹配，L1/L2/L3 cross-reference 持久

Grep "Docs/" docs/AirymaxRT
# 结果：0 匹配，Docs/→docs/ 持久

# v4.0 新发现问题验证
Grep "cognition_types\.h" docs/AirymaxRT
# 结果：15 处，其中 8 处为错误引用（airy_err_t 定义位置），7 处为合法引用

Grep "agent_contract\.md|skill_contract\.md|protocol_contract\.md|syscall_api_contract\.md|logging_format\.md" docs/AirymaxRT
# 结果：73 处，其中约 40 处为 broken Markdown 链接

Grep "error_code_reference\.md" docs/AirymaxRT
# 结果：3 处 broken link

Grep "\.\./specifications/" docs/AirymaxRT
# 结果：4 处 broken link

Grep "docs/AirymaxAgentOS" docs/AirymaxRT
# 结果：0 匹配，R3-2 已修正
```

### 7.3 v4.0 新发现问题修正工作量汇总

| 编号 | 级别 | 工作量 | 说明 |
|------|------|--------|------|
| v4.0-P0-1 | P0 | ~1h | 8 处 cognition_types.h → airy_types.h:41 |
| v4.0-P0-2 | P0 | ~2h | 错误码分段表统一（TERMINOLOGY.md vs L3 标准） |
| v4.0-P1-1 | P1 | ~1h | 40 处 10-contracts/ broken Markdown 链接 |
| v4.0-P1-2 | P1 | ~0.1h | 3 处 error_code_reference.md → project_erp.md |
| v4.0-P1-3 | P1 | ~0.1h | 01-doxygen-guide.md L326/327/13 修正 |
| v4.0-P1-4 | P1 | ~0.2h | 4 处 ../specifications/ → ../20-modules/ |
| v4.0-P1-5 | P1 | ~0.3h | 04-mainpage.dox 协议表补全 4→9 |
| v4.0-P1-6 | P1 | ~0.2h | ARE_EMSGSIZE/ARE_IPC_MAX_MSG_SIZE 定义补全 |
| v4.0-P2-1 | P2 | ~0.05h | 3 处不存在文件引用修正 |
| v4.0-P2-2 | P2 | ~0.05h | ../architecture/ → ../10-architecture/ |
| v4.0-P2-3 | P2 | ~0.5h | GitHub repo URL 核实与统一 |
| v4.0-P2-4 | P2 | ~0.05h | @since 1.1.0 版本号核实 |
| **合计** | — | **~5.55h** | 可在 0.1.1 收尾阶段完成 |

### 7.4 必读历史报告索引

| # | 报告 | 路径 | 版本 |
|---|------|------|------|
| 1 | v1.0 综合分析 | `docs-closed/agentrt/00-reviews/_review_v1.0/00-comprehensive-analysis.md` | 1.0（2026-07-13） |
| 2 | v2.0 工程规范与代码审查 | `docs-closed/agentrt/00-reviews/_review_v2.0/01-engineering-code-review-v2.md` | 2.0（2026-07-13） |
| 3 | v2.0 修正验证报告 | `docs-closed/agentrt/00-reviews/_review_v2.0/fix-verification-report.md` | 1.0（2026-07-13） |
| 4 | v3.0 开源文档审查 | `docs-closed/agentrt/00-reviews/_review_v3.0/01-open-docs-review.md` | 3.0（2026-07-14） |
| 5 | v3.0 修正验证报告 | `docs-closed/agentrt/00-reviews/_review_v3.0/fix-verification-report-v3.md` | 3.0（2026-07-14） |
| 6 | **v4.0 开源文档审查（本文档）** | `docs-closed/agentrt/00-reviews/_review_v4.0/01-open-docs-review.md` | **4.0（2026-07-14）** |

---

<div align="center">

**© 2025-2026 SPHARX Ltd.** All Rights Reserved.

</div>

---

**报告结束** | SPHARX Ltd 内部参考 | 闭源不公开 | 审查日期：2026-07-14 | 审查版本：v4.0
