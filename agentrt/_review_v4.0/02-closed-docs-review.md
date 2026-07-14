Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
<!-- SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0 -->
<!-- 保密级别：SPHARX Ltd 内部参考，闭源不公开 -->
<!-- 版本：4.0 | 日期：2026-07-14 -->

# Airymax agentrt 闭源文档 v4.0 深化审查报告

> **文档定位**：v4.0 对 `docs-closed/agentrt/` 闭源文档的第四轮深化审查。在前三轮（v1.0/v2.0/v3.0）基础上，独立审查 v3.0 修正持久性、v3.0 修正副作用、v1~v3 未覆盖盲区，作为 1.0.1 M1 启动前闭源文档侧的最终判定基线。
> **保密级别**：SPHARX Ltd 内部参考，**闭源不公开**。
> **版本**：4.0（2026-07-14）。
> **审查范围**：仅 `docs-closed/agentrt/`（不含 `docs-closed/agentrt-linux/`、`docs/AirymaxRT/`、`agentrt/` 源码）。
> **审查方法**：v3.0 三份报告精读 + 18 项 Grep 机器检查 + 全文系统性扫描 + 跨文件交叉一致性验证。
> **证据要求**：所有结论附 `文件路径:L行号`，可通过 Read/Grep 工具复核。
> **SPDX-License-Identifier**：AGPL-3.0-or-later OR Apache-2.0。

---

## 目录

- [1. 执行摘要](#1-执行摘要)
- [2. v3.0 修正持久性验证矩阵](#2-v30-修正持久性验证矩阵)
- [3. v3.0 修正副作用清单](#3-v30-修正副作用清单)
- [4. v4.0 新发现问题清单](#4-v40-新发现问题清单)
- [5. 残留项状态复核](#5-残留项状态复核)
- [6. 修正后评分预估](#6-修正后评分预估)

---

## 1. 执行摘要

### 1.1 审查目标与边界

本报告是 agentrt 闭源文档 v4.0 深化审查，**四维度独立审查**：

1. **v3.0 修正持久性验证**：验证 v3.0 域3（302+44 处 `agentos_`→`airy_` + §11.6 历史声明 + §34.2 IPC 重写 + 遗留项）的修正是否持久保留。
2. **v3.0 修正副作用检测**：v3.0 修正是否引入新问题（如误替换、strncmp 长度、§34.2 重写一致性、错误码 SSoT 统一后闭源手册未同步）。
3. **未发现新问题扫描**：v1.0/v2.0/v3.0 未覆盖的盲区，重点：主手册各节间逻辑一致性、主手册与子系统规格/合约间一致性、错误码分段对齐、`daemon/`→`daemons/` 改名同步、路径引用完整性。
4. **残留项状态复核**：R3-1（1738 处归档声明）/ R3-2（7 处 AirymaxAgentOS 路径）。

**审查边界**：仅 `docs-closed/agentrt/`（不审查 `docs-closed/agentrt-linux/`、`docs/`、源码）。

### 1.2 综合评分

| 评分维度 | v3.0 修正后（预估） | v4.0 审查后 | 变化 | 主要原因 |
|---------|-------------------|------------|------|---------|
| 技术准确性 | B+ | **B-** | -1 | §34.5 错误码分段未修正（P1-V3-3 遗漏）+ 错误码分段三重不一致 + `AIRY_OK` 残留 + 错误码名称不匹配 |
| 工程指导性 | B+ | **B-** | -1 | `daemon/`→`daemons/` 18 处未同步 + `agentos/` 39 处当前路径残留 |
| 一致性（与开源 SSoT） | B+ | **B-** | -1 | 错误码分段/权威源未对齐 SSoT 方案 A + `Docs/` 大写路径 29 处 |
| 修正持久性 | A | **A** | 0 | v3.0 18 项修正全部持久 |
| **闭源文档总评** | **80/B+**（预估） | **75/B** | **-5** | v3.0 修正盲区（§34.5 遗漏 + daemon→daemons 未同步）+ v3.0 域1/域4 副作用未传播到闭源手册 |

### 1.3 核心结论

> **v3.0 域3 闭源文档修正的 18 项关键修正全部持久保留（0 回退）**，修正质量良好。但 v4.0 深化审查发现三类问题：
>
> 1. **v3.0 修正遗漏（2 项 P1）**：v3.0 闭源文档审查报告（02-closed-docs-review.md）识别的 P1-V3-2（`agentos/` 目录路径 60+ 处）和 P1-V3-3（§34.5 错误码分段）在 v3.0 修正验证报告（fix-verification-report-v3.md）中**既未被列入修正范围，也未被列入残留项**，属于静默遗漏。当前 `agentos/` 当前路径残留 39 处，§34.5 仍为 9 段未对齐 SSoT 11 段。
>
> 2. **v3.0 域1/域4 副作用未传播（3 项 P1）**：v3.0 域1 错误码 SSoT 统一（移除 `AIRY_OK`、统一为方案 A POSIX errno）和域4 并发安全修复（使用 `AIRY_ERR_SYS_NOT_INIT`）的修正**未同步到闭源手册**。闭源手册仍引用已移除的 `AIRY_OK`（2 处），使用 `AIRY_ERR_NOT_INITIALIZED`（4 处，源码用 `AIRY_ERR_SYS_NOT_INIT`），且 §4.9 与 §34.5 存在两套冲突的错误码分段表。
>
> 3. **v1~v3 未覆盖盲区（1 项 P1 + 7 项 P2）**：`daemon/`→`daemons/` 目录改名（§11.6 L8 已声明）未同步到 07-subsystem-specs/（12 处）和 06-contracts/（6 处），共 18 处 `agentrt/daemon/`（单数）残留——这是 v3.0 域3 仅替换 `agentos_`→`airy_`（前缀）但未处理 `daemon/`→`daemons/`（目录名）的盲区。此外发现 BAN 规则计数错误、JSON-RPC 命名空间与 daemon 二进制不匹配、`Docs/` 大写路径等 7 项 P2 问题。
>
> **1.0.1 M1 启动判定**：闭源文档侧**条件性通过**——v3.0 P0 阻断全部持久清零，但 6 项 P1 需在 M1 早期修正（~7.5h），其中 `daemon/`→`daemons/` 和错误码分段对齐为开发者直接影响项。

### 1.4 与 v3.0 报告的关系

| 评分阶段 | 评分 | 评分范围 | 说明 |
|---------|------|---------|------|
| v3.0 复审后 | 66/C+ | `docs-closed/agentrt/` 全目录 | v3.0 扩大审查范围，暴露 340 处 `agentos_*` 残留 |
| v3.0 修正后（预估） | 80/B+ | `docs-closed/agentrt/` 全目录 | v3.0 验证报告预估（20 项 Grep 通过） |
| **v4.0 审查后** | **75/B** | `docs-closed/agentrt/` 全目录 | v4.0 深化审查发现 v3.0 遗漏 + 副作用 + 盲区 |

> **关键说明**：v4.0 评分 75/B 与 v3.0 预估 80/B+ 的差异**不是修正倒退**（v3.0 修正全部持久），而是**深化审查发现新问题**：v3.0 修正验证报告的 20 项 Grep 检查聚焦于"已修项是否持久"，未覆盖"遗漏项"和"副作用传播"。v4.0 补充了这些维度的检查。

---

## 2. v3.0 修正持久性验证矩阵

### 2.1 验证方法

对 v3.0 修正验证报告（fix-verification-report-v3.md §3）声明的修正项，使用 Grep 机器检查独立复核当前状态（截至 2026-07-14）。共 18 项验证。

### 2.2 验证矩阵

| # | 验证项 | Grep 模式 | 期望 | 实际 | 状态 | 证据 |
|---|--------|----------|------|------|------|------|
| 1 | 07-subsystem-specs/ `agentos_` 零残留 | `agentos_` | 0 | **0** | ✅ 持久 | 07-subsystem-specs/ Grep count=0 |
| 2 | 06-contracts/ `agentos_` 零残留 | `agentos_` | 0 | **0** | ✅ 持久 | 06-contracts/ Grep count=0 |
| 3 | 主手册 `agentos_` 零残留 | `agentos_` | 0 | **0** | ✅ 持久 | 手册 Grep count=0 |
| 4 | 主手册 `AGENTOS_` 零残留 | `AGENTOS_` | 0 | **0** | ✅ 持久 | 手册 Grep count=0 |
| 5 | 主手册 `airy_error_t` 仅历史上下文 | `airy_error_t` | ≤2（§11.6） | **2**（L1520, L1532） | ✅ 持久 | L1520 附加说明 + L1532 §11.6 L5 历史矩阵 |
| 6 | 主手册 `are_ipc_message_header_t` 仅迁移表 | `are_ipc_message_header_t` | ≤1 | **1**（L3393 迁移表） | ✅ 持久 | L3393 "早期草案字段（已废弃）" |
| 7 | 主手册 `struct airy_ipc_msg_hdr` 存在 | `struct airy_ipc_msg_hdr` | >0 | **7** | ✅ 持久 | L3341/3343/3354/3369/3381/3386/3393 |
| 8 | 主手册 §11.6 历史声明 | `历史决策记录` | 2（L1511, L1518） | **2** | ✅ 持久 | L1511 + L1518 |
| 9 | 主手册 `agentos.yaml` 零残留 | `agentos\.yaml` | 0 | **0** | ✅ 持久 | Grep: No matches |
| 10 | 主手册 `_Static_assert(sizeof(struct airy_ipc_msg_hdr)` | 同左 | 1 | **1**（L3381） | ✅ 持久 | L3381 |
| 11 | 主手册 `airy_err_t` 正确（5 处修正+1 历史） | `airy_err_t` | 6 | **6**（L251/507/535/764/787/1520） | ✅ 持久 | 5 处修正 + 1 处历史说明 |
| 12 | 主手册 `agentrt.yaml` 替换 | `agentrt\.yaml` | 13 | **13** | ✅ 持久 | Grep count=13 |
| 13 | 主手册 L40 "12 个 daemon" | `16 个 daemon` | 0 | **0** | ✅ 持久 | L40 已改为"12 个 daemon" |
| 14 | 主手册 L9 29→38 仓标注 | `29 仓拆分` | 1（含标注） | **1**（L9 含"v27.0 已迁移至 38 仓"标注） | ✅ 持久 | L9 末尾历史标注 |
| 15 | README.md 版本号一致 | `版本` | 0.1.1 | **0.1.1**（L7 + L96） | ✅ 持久 | L7 "版本: 0.1.1" + L96 "文档版本: 0.1.1" |
| 16 | 05-tech-reference 归档声明 | 05-tech.../README.md | 存在 | **存在** | ✅ 持久 | 1738 处归档声明完整 |
| 17 | 06-contracts strncmp 长度 5 | `strncmp.*PREFIX, 5` | 14 | **14** | ✅ 持久 | contract_test.c L295-334 全部为 5 |
| 18 | 06-contracts 指标前缀 `airy_` | `CONTRACT_AC_METRIC_PREFIX` | `"airy_"` | **`"airy_"`** | ✅ 持久 | contract_A_C.h L131 |

### 2.3 验证结论

> **v3.0 域3 闭源文档修正 18/18 项全部持久通过（100%）**。v3.0 声明的所有修正项（302+44 处前缀替换 + §11.6 历史声明 + §34.2 IPC 重写 + 5 处类型名 + 13 处 yaml + 遗留项 + README + 归档说明）均完整保留，0 回退。
>
> **关键确认**：
> - `agentos_error_t` → `airy_err_t` 替换正确（非 `airy_error_t`），07-subsystem-specs/ 和 06-contracts/ 中 `airy_error_t` 残留为 0。
> - strncmp 长度 8→5 修正完整（14/14），与 "airy_" 5 字符匹配。
> - §34.2 IPC 头重写对齐 SSoT（`struct airy_ipc_msg_hdr`，128 字节，8 字段，`__attribute__((packed))`，`_Static_assert`），字段偏移量验证正确（4+2+2+8+8+8+8+4+84=128）。
> - §11.6 历史决策声明完整，明确标注"该决策未实际执行"和"当前前缀以 SSoT §3.12 为准"。

---

## 3. v3.0 修正副作用清单

### 3.1 副作用检测方法

v3.0 修正涉及 4 个域（错误码 SSoT / IPC 头+路径术语 / 闭源文档 / 源码并发安全），其中域1（错误码 SSoT 统一）和域4（源码并发安全）的修正可能对闭源手册产生副作用——即闭源手册未同步域1/域4 的变更。

### 3.2 副作用清单

| # | 副作用 | 来源域 | 严重度 | 证据 | 说明 |
|---|--------|-------|--------|------|------|
| SE-1 | `AIRY_OK` 残留引用 | 域1 | P1 | `手册:L847` `@return AIRY_OK (0) 成功`；`手册:L2803` `定义 AIRY_OK/AIRY_ERR_* 错误码` | v3.0 域1 修正移除了 error.h 中的 `AIRY_OK` 定义（fix-verification §2.1），但闭源手册仍引用 `AIRY_OK`（2 处），开发者按手册编写代码将引用不存在的宏 |
| SE-2 | `AIRY_ERR_NOT_INITIALIZED` 与源码不匹配 | 域4 | P1 | `手册:L3222/L3238/L3261/L3309` 使用 `AIRY_ERR_NOT_INITIALIZED`；源码 `core_init.c:L78` 使用 `AIRY_ERR_SYS_NOT_INIT`（fix-verification §3.5） | v3.0 域4 修复 DCLP 时使用 `AIRY_ERR_SYS_NOT_INIT`，但闭源手册 4 处仍用 `AIRY_ERR_NOT_INITIALIZED`，名称不匹配 |
| SE-3 | 错误码权威源声明未同步域1 SSoT | 域1 | P1 | `手册:L2803` 声明 `error.h` 定义 `AIRY_OK`/`AIRY_ERR_*`；`手册:L3442` 声明 `agentos/commons/utils/error/include/error.h` 为权威源 | v3.0 域1 统一 SSoT 为方案 A（POSIX errno 负值），`airy_err_t` 定位为 `airy_types.h:41`，但闭源手册 §34.5 和 LOG-09 仍用旧权威源路径和旧定义描述 |

### 3.3 副作用结论

> **v3.0 域1（错误码 SSoT）和域4（源码并发安全）的修正对闭源手册产生了 3 项副作用**，均因为域3 闭源文档修正未同步域1/域4 的变更。这些副作用不影响 v3.0 域3 修正本身的正确性（域3 修正的 18 项全部持久），但导致闭源手册与最新 SSoT/源码之间出现新的不一致。
>
> **根因分析**：v3.0 修正采用 4 域并行模型，域3（闭源文档）的修正范围仅基于 v3.0 闭源文档审查报告（02-closed-docs-review.md）发现的问题，未包含域1/域4 修正对闭源手册的影响传播。这是并行修正模型的固有盲区——各域修正独立完成后，未执行跨域一致性验证。

---

## 4. v4.0 新发现问题清单

### 4.1 P0 级问题（0 项）

> **无 P0 级新发现问题**。v3.0 修正的 4 项 P0（P0-V3-1/2/3/4）全部持久清零，v4.0 未发现新的 P0 级阻断项。

### 4.2 P1 级问题（6 项，1.0.1 M1 早期完成）

#### P1-V4-1：§34.5 错误码分段未修正（P1-V3-3 静默遗漏）

**严重度**：P1

**问题描述**：v3.0 闭源文档审查报告（02-closed-docs-review.md §4.2 P1-V3-3）识别了 §34.5 错误码分段与开源 SSoT 不一致（9 段 vs 11 段，缺 i18n/发行版；权威源路径用旧 `agentos/`）。但 v3.0 修正验证报告（fix-verification-report-v3.md §2.3 域3）的修正清单中**未包含 §34.5**，残留项清单（§5.3）中也**未列出 §34.5**，属于静默遗漏。

**证据**：

| 维度 | 当前状态（v4.0 验证） | SSoT 方案 A（v3.0 域1） | 一致性 |
|------|---------------------|----------------------|--------|
| 分段数 | 9 段（`手册:L3447-3455`） | 11 段（含 i18n/发行版） | ✗ |
| 权威源路径 | `agentos/commons/utils/error/include/error.h`（`手册:L3442`） | `airy_types.h:41`（`airy_err_t`）+ `agentrt/commons/utils/error/include/error.h` | ✗（路径仍用 `agentos/`） |
| 分段范围 | 通用 -1~-99 / 系统 -100~-199 / ... | POSIX errno 负值（AIRY_EINVAL=(-22) 等） | ✗ |
| 类型名 | 未在 §34.5 明确引用 `airy_err_t` | `airy_err_t`（`airy_types.h:41`） | ✗ |

**影响**：开发者按 §34.5 定义的 9 段分段注册错误码，将与 SSoT 方案 A 的 11 段分段和 POSIX errno 值不一致，CI 门禁 `check_error_codes.sh` 将失败。

**工作量**：~1h（§34.5 全节对齐 SSoT 方案 A：补 i18n/发行版分段、修正权威源路径、引用 `airy_err_t`/`airy_types.h`）。

#### P1-V4-2：`agentos/` 目录路径 39 处当前引用残留（P1-V3-2 未列入残留项）

**严重度**：P1

**问题描述**：v3.0 闭源文档审查报告（02-closed-docs-review.md §4.2 P1-V3-2）识别了主手册 `agentos/` 目录路径 60+ 处残留。v3.0 修正验证报告的域3 修正清单和残留项清单中**均未提及此项**，属于静默遗漏。v4.0 独立 Grep 确认当前 `agentos/` 残留 44 行，其中 ~5 行为 §11.6 历史改名矩阵中的合法历史引用，~39 行为当前引用（应改为 `agentrt/`）。

**证据**（Grep `agentos/` 共 44 行，分类）：

| 类别 | 行数 | 典型行号 | 处理建议 |
|------|------|---------|---------|
| §11.6 历史改名矩阵（合法） | ~5 | L1528/1531/1534/1535/1573 | 保留（历史记录） |
| 当前代码路径引用 | ~12 | L83/84（团队代码范围）、L1835（`agentos/atoms/memoryrovol/`）、L2069-2071（团队三权分立）、L2481/2723/2742 | 改为 `agentrt/` |
| 当前 `#include`/grep 路径 | ~8 | L365/383/3174-3177/3235-3236/3436 | 改为 `agentrt/` |
| 运行时路径 | ~4 | L381（`/var/lib/agentos/`）、L1261/1263（`~/.agentos/hooks/`）、L1415（`~/.agentos/`）、L2877（`/var/log/agentos/agentos.log`） | 改为 `agentrt/` |
| 许可证表 `AgentRT/agentos/` | ~7 | L3030-3036 | 改为 `agentrt/`（双重错误：`AgentRT/` 大写 + `agentos/` 旧名） |
| 其他当前引用 | ~8 | L1068/1493/2909/3159/3442/3513-3517 | 逐项核对 |

**子问题**：其中 17 处为 `AgentRT/agentos/`（大写 AgentRT + 旧 agentos 目录），是双重路径错误。v3.0 域2 在开源文档中将 `AgentRT/` → `agentrt/`（42 处），但闭源手册未同步。

**影响**：开发者按手册路径引用源码将找不到文件（实际目录为 `agentrt/`）；错误码权威源路径 `agentos/commons/utils/error/include/error.h`（L3442）与实际 `agentrt/commons/utils/error/include/error.h` 不一致。

**工作量**：~3h（39 处逐项核对，区分目录路径 vs 历史记录，含 17 处 `AgentRT/agentos/` 双重修正）。

#### P1-V4-3：`daemon/` → `daemons/` 目录改名未同步（18 处）

**严重度**：P1

**问题描述**：§11.6 L8 明确声明 `agentos/daemon/` → `agentrt/daemons/` 改名（daemon → daemons，模块名/目录/CMake target/仓库名统一）。v3.0 域2 在开源文档中将 `agentrt/daemon/` → `agentrt/daemons/`（15 文件 46 处）。但 v3.0 域3 闭源文档修正仅替换 `agentos_` → `airy_`（前缀），**未处理 `daemon/` → `daemons/`（目录名）**，导致 07-subsystem-specs/ 和 06-contracts/ 中 18 处 `agentrt/daemon/`（单数）残留。

**证据**（Grep `agentrt/daemon/`）：

| 文件 | 行号 | 内容 |
|------|------|------|
| `07-subsystem-specs/05-gateway-d.md` | L4/305/331 | `agentrt/daemon/gateway_d/` |
| `07-subsystem-specs/06-llm-d.md` | L4/299 | `agentrt/daemon/llm_d/` |
| `07-subsystem-specs/08-market-d.md` | L4/312 | `agentrt/daemon/market_d/` |
| `07-subsystem-specs/12-tool-d.md` | L4/362 | `agentrt/daemon/tool_d/` |
| `07-subsystem-specs/11-orchestrator.md` | L4/333 | `agentrt/daemon/common/` |
| `07-subsystem-specs/03-coreloopthree.md` | L258 | `agentrt/daemon/common/` |
| `06-contracts/contract_A_B.h` | L19/20 | `agentrt/daemon/market_d/`、`agentrt/daemon/gateway_d/` |
| `06-contracts/contract_A_C.h` | L16/17/18/19 | `agentrt/daemon/common/`（4 处） |

**影响**：开发者按子系统规格和合约中的路径引用源码将找不到文件（实际目录为 `agentrt/daemons/`，复数），CMake 构建失败。

**工作量**：~1h（18 处 `daemon/` → `daemons/` 全量替换，需区分 `agentrt/daemon/` 目录路径 vs `daemon/` 在其他上下文中的使用）。

#### P1-V4-4：错误码分段三重不一致（§4.9 vs §34.5 vs SSoT 方案 A）

**严重度**：P1

**问题描述**：主手册存在**两套互相冲突的错误码分段表**，且均与 v3.0 域1 统一的 SSoT 方案 A 不一致。这是 v1~v3 未覆盖的盲区。

**证据**：

| 维度 | §4.9（L797-811） | §34.5（L3444-3455） | SSoT 方案 A（域1） |
|------|-----------------|--------------------|--------------------|
| 分段数 | 10 段（成功/通用/Task/Memory/Session/Telemetry/Internal/Skill/Agent/Sandbox/Security） | 9 段（通用/系统/内核/服务/LLM/执行/记忆/安全/协议） | 11 段（含 i18n/发行版） |
| 范围格式 | 4 位数（-1~-999, -1001~-1099, ...） | 2 位数（-1~-99, -100~-199, ...） | POSIX errno 负值（-22, -12, ...） |
| 成功码 | `AIRY_SUCCESS`（L801） | 未提及 | `AIRY_OK` 已移除（域1） |
| 来源 | "源自 10-terminology.md ErrorCodeSystem"（L797） | STD-05 强制规则（L3440） | 方案 A 唯一权威（域1） |

**子问题**：
- §4.9（L801）使用 `AIRY_SUCCESS` 表示成功码 0，L847 使用 `AIRY_OK` 表示成功码 0——同一手册内成功码名称不一致。
- §4.9（L797）声称"源自 10-terminology.md"，但该文档路径在手册中引用为 `../Docs/10-terminology.md`（L94，大写 `Docs/`），实际路径可能为 `docs/` 小写。

**影响**：开发者面对两套冲突的分段表，无法确定错误码应注册在哪一段；CI 门禁 `check_error_codes.sh` 的分段验证标准不明确。

**工作量**：~2h（统一 §4.9 和 §34.5 为单一分段表，对齐 SSoT 方案 A 11 段；统一成功码名称；修正 `10-terminology.md` 引用路径）。

#### P1-V4-5：`AIRY_OK` 残留引用（v3.0 域1 副作用）

**严重度**：P1

**问题描述**：v3.0 域1 修正移除了 error.h 中的 `AIRY_OK` 定义（fix-verification §2.1："移除 `AIRY_OK` 定义"），但闭源手册仍引用 `AIRY_OK`（2 处），是 v3.0 域1 修正未传播到闭源手册的副作用。

**证据**：

| 位置 | 内容 | 问题 |
|------|------|------|
| `手册:L847` | `@return AIRY_OK (0) 成功；其他值为错误码。` | 引用已移除的 `AIRY_OK` |
| `手册:L2803` | `commons/utils/error/include/error.h（权威源，定义 AIRY_OK/AIRY_ERR_* 错误码）` | 声明 error.h 定义 `AIRY_OK`，但已被移除 |

**影响**：开发者按手册使用 `AIRY_OK` 将引用不存在的宏，编译失败。

**工作量**：~0.2h（2 处 `AIRY_OK` 清理：L847 改为 `0` 或 `AIRY_SUCCESS`；L2803 移除 `AIRY_OK` 引用）。

#### P1-V4-6：`AIRY_ERR_NOT_INITIALIZED` 与源码 `AIRY_ERR_SYS_NOT_INIT` 名称不匹配（v3.0 域4 副作用）

**严重度**：P1

**问题描述**：v3.0 域4 修复 DCLP 并发安全时，在源码 `core_init.c` 和 `cupolas.c` 中使用 `AIRY_ERR_SYS_NOT_INIT`（fix-verification §3.5/§3.6）。但闭源手册 4 处仍使用 `AIRY_ERR_NOT_INITIALIZED`，名称不匹配。

**证据**：

| 位置 | 手册内容 | 源码（域4 修正后） |
|------|---------|------------------|
| `手册:L3222` | `return AIRY_ERR_NOT_INITIALIZED;` | `core_init.c:L78` `return AIRY_ERR_SYS_NOT_INIT;` |
| `手册:L3238` | `cognition 返回 AIRY_ERR_NOT_INITIALIZED` | 同上 |
| `手册:L3261` | `ops 未注入时返回 AIRY_ERR_NOT_INITIALIZED` | 同上 |
| `手册:L3309` | `BAN-319 必须返回 AIRY_ERR_NOT_INITIALIZED` | 同上 |

**影响**：开发者按手册使用 `AIRY_ERR_NOT_INITIALIZED` 将与源码 `AIRY_ERR_SYS_NOT_INIT` 不匹配，编译失败或语义不一致。

**工作量**：~0.3h（4 处 `AIRY_ERR_NOT_INITIALIZED` → `AIRY_ERR_SYS_NOT_INIT`）。

### 4.3 P2 级问题（7 项，1.0.1 全阶段改进）

#### P2-V4-1：BAN 规则计数错误（L13 v28.0 变动说明）

**严重度**：P2

**问题描述**：主手册 L13（v28.0 变动说明）声明"BAN 规则从 356 项扩展为 357 项"，但 v27.0 变动说明（L23）已将 BAN 规则扩展至 360 项（BAN-357~360），v28.0 新增 BAN-361 后应为 361 项。L13 错误地以 v26.0 的 356 项为基准。

**证据**：

| 位置 | 声明 | 正确值 |
|------|------|-------|
| `手册:L9`（v26.0） | "BAN 规则从 340 项扩展为 356 项（+16）" | ✅ 正确 |
| `手册:L23`（v27.0） | "BAN 规则从 356 项扩展为 360 项" | ✅ 正确 |
| `手册:L13`（v28.0） | "BAN 规则从 356 项扩展为 357 项" | ✗ 应为"从 360 项扩展为 361 项" |
| `手册:L4563`（总计） | "BAN 规则 361 项" | ✅ 正确（与 L13 矛盾） |

**影响**：v28.0 变动说明的 BAN 计数与总计（L4563）矛盾，读者困惑。

**工作量**：~0.1h（L13 "356 项扩展为 357 项" → "360 项扩展为 361 项"）。

#### P2-V4-2：JSON-RPC 12 命名空间与 12 daemon 二进制不匹配

**严重度**：P2

**问题描述**：§34.4（L3429-3430）声明"12 个 daemons 命名空间"并列出 12 个命名空间，但这 12 个命名空间与 §37.3（L4225）/§1.6（L1522）的 12 个 daemon 进程二进制名不匹配。

**证据**：

| JSON-RPC 命名空间（§34.4 L3430） | 对应 daemon 二进制（§37.3 L4225） | 匹配 |
|----------------------------------|----------------------------------|------|
| `llm.` | llm_d | ✅ |
| `tool.` | tool_d | ✅ |
| `sched.` | sched_d | ✅ |
| `hook.` | hook_d | ✅ |
| `plugin.` | plugin_d | ✅ |
| `monit.` | monit_d | ✅ |
| `market.` | market_d | ✅ |
| `mem.` | ??? | ✗ 无 mem_d |
| `agent.` | ??? | ✗ 无 agent_d |
| `a2a.` | ??? | ✗ 无 a2a_d（合约路由表显示 a2a 通道由 sched_d 服务） |
| `mcp.` | ??? | ✗ 无 mcp_d（合约路由表显示 mcp 通道由 tool_d 服务） |
| `cupolas.` | ??? | ✗ 无 cupolas_d（cupolas 是子系统，非 daemon） |
| 缺失 | gateway_d | ✗ 无 `gateway.` 命名空间 |
| 缺失 | channel_d | ✗ 无 `channel.` 命名空间 |
| 缺失 | info_d | ✗ 无 `info.` 命名空间 |
| 缺失 | notify_d | ✗ 无 `notify.` 命名空间 |
| 缺失 | observe_d | ✗ 无 `observe.` 命名空间 |

**影响**：§34.4 声称"12 个 daemons 命名空间"暗示 1:1 映射，但实际 5 个命名空间无对应 daemon，5 个 daemon 无对应命名空间。读者无法确定哪个 daemon 服务哪个命名空间。

**工作量**：~0.5h（补充命名空间与 daemon 的映射说明表，或修正"12 个 daemons 命名空间"表述）。

#### P2-V4-3：`are_svc_discovery_adapter_t` 使用 `are_` 前缀而非 `airy_`

**严重度**：P2

**问题描述**：§34.3 STD-03（L3412）使用 `are_svc_discovery_adapter_t` 作为服务发现适配器接口类型名，使用 `are_` 前缀而非 SSoT 规定的 `airy_` 前缀。同理，§34.6（L3466-3468）使用 `are_standards/` 作为标准文档目录名。

**证据**：
- `手册:L3412`：`are_svc_discovery_adapter_t`（C 类型名）
- `手册:L3466-3468`：`are_standards/L1_runtime_interface.md` 等（目录名）
- `手册:L3393`：`are_ipc_message_header_t`（已标注"已废弃"，合法）

**评估**：`are_standards/` 可能是"ARE Standards"（Agent Runtime Environment Standards）的 deliberate 命名，属文档目录名而非代码前缀。但 `are_svc_discovery_adapter_t` 是 C 类型名，应遵循 `airy_` 前缀规范。需确认源码实际使用的类型名。

**工作量**：~0.2h（确认 `are_svc_discovery_adapter_t` 在源码中的实际名称，若源码用 `airy_` 则修正手册）。

#### P2-V4-4：验证命令使用 `daemon/`（单数）而非 `daemons/`（复数）

**严重度**：P2

**问题描述**：§33.2（L3258-3259）的验证命令使用 `daemon/`（单数）匹配目录路径，但实际目录已改名为 `daemons/`（复数）。`grep 'daemon/'` 不会匹配 `daemons/`（因 `daemon` 后跟 `s` 而非 `/`），导致验证命令失效。

**证据**：

| 位置 | 当前命令 | 问题 |
|------|---------|------|
| `手册:L3258` | `grep -rn '#include.*daemon/' atoms/` → 0 | 不会匹配 `daemons/` |
| `手册:L3259` | `grep -rn 'daemon/' atoms/*/CMakeLists.txt` → 0 | 同上 |
| `手册:L1545` | `grep -rn '\bdaemon/' --include='CMakeLists.txt' .` → 0 | 同上（§11.6 历史验证标准） |
| `手册:L1554` | BAN-343 grep `daemon/` 在 CMakeLists.txt 期望 0 | 同上 |
| `手册:L1602` | `grep -rn '\bdaemon/' --include='CMakeLists.txt' .` | 同上（§11.6 操作步骤） |

**影响**：CI 验证命令无法检测 `daemons/` 目录的反向依赖，门禁失效。

**工作量**：~0.2h（5 处 `daemon/` → `daemons/` 验证命令修正，§11.6 历史上下文中的可保留并添加说明）。

#### P2-V4-5：`Docs/` 大写路径 29 处应为 `docs/`

**严重度**：P2

**问题描述**：主手册 29 处引用 `Docs/`（大写 D），实际路径为 `docs/`（小写，Linux 区分大小写）。v3.0 域2 在开源文档中将 `Docs/` → `docs/`（7 处 P2 路径修正），但闭源手册未同步。

**证据**（Grep `Docs/` 共 29 行，典型位置）：

| 类别 | 行号 | 内容 |
|------|------|------|
| 相对路径链接 | L94/115/391/671/726/759/1047/1112/1459-1462/2097/2101-2106 | `../Docs/10-terminology.md` 等 |
| 团队代码范围 | L85/2071/2331 | `Docs/` |
| 许可证表 | L3042/3060/3093 | `Docs/` |
| 其他 | L179/2047/3319/3477 | `Docs/` |

**影响**：在 Linux（区分大小写）上，相对路径链接 `../Docs/...` 将断链（实际目录为 `docs/`）。

**工作量**：~0.5h（29 处 `Docs/` → `docs/` 逐项核对，需确认每处是路径引用还是专有名称）。

#### P2-V4-6：`AIRY_SUCCESS` 与 `AIRY_OK` 成功码名称不一致

**严重度**：P2

**问题描述**：主手册使用两个不同的成功码名称：`AIRY_SUCCESS`（§4.9 L801、L520、L675 BAN-01）和 `AIRY_OK`（L847、L2803）。v3.0 域1 已移除 `AIRY_OK`，但 `AIRY_SUCCESS` 的状态未明确。

**证据**：

| 位置 | 名称 | 上下文 |
|------|------|--------|
| `手册:L801` | `AIRY_SUCCESS` | §4.9 错误码分段表成功码 |
| `手册:L520` | `return AIRY_SUCCESS;` | 代码示例 |
| `手册:L675` | BAN-01 禁止 `return AIRY_SUCCESS` 占位返回 | BAN 规则 |
| `手册:L847` | `AIRY_OK (0)` | 代码示例（已移除的宏） |
| `手册:L2803` | `定义 AIRY_OK` | LOG-09 权威源描述（已移除的宏） |

**影响**：开发者不确定应使用 `AIRY_SUCCESS` 还是 `AIRY_OK`（后者已不存在）。

**工作量**：~0.3h（统一成功码名称：确认 SSoT 中的成功码定义，清理 `AIRY_OK` 引用，统一为 `AIRY_SUCCESS` 或 `0`）。

#### P2-V4-7：测试覆盖率表 `daemon/` 应为 `daemons/`

**严重度**：P2

**问题描述**：§12.3（L1782）测试覆盖率表中 `daemon/` 应为 `daemons/`（目录已改名）。

**证据**：`手册:L1782`：`| daemon/ | ≥ 50% | ≥ 30% |`

**影响**：测试覆盖率目标引用旧目录名，CI 可能无法正确匹配目录。

**工作量**：~0.1h（L1782 `daemon/` → `daemons/`）。

### 4.4 问题汇总

| 类别 | P0 | P1 | P2 | 合计 |
|------|----|----|----|------|
| v3.0 遗漏（P1-V3-2/3 静默遗漏） | 0 | 2（P1-V4-1/2） | 0 | 2 |
| v3.0 域1/域4 副作用 | 0 | 3（P1-V4-4/5/6） | 1（P2-V4-6） | 4 |
| daemon→daemons 改名未同步 | 0 | 1（P1-V4-3） | 2（P2-V4-4/7） | 3 |
| 路径/目录一致性 | 0 | 0 | 2（P2-V4-3/5） | 2 |
| 规则编号/命名空间一致性 | 0 | 0 | 2（P2-V4-1/2） | 2 |
| **合计** | **0** | **6** | **7** | **13** |

**工作量估算**：
- P1 合计：~7.5h（P1-V4-1 ~1h + P1-V4-2 ~3h + P1-V4-3 ~1h + P1-V4-4 ~2h + P1-V4-5 ~0.2h + P1-V4-6 ~0.3h）
- P2 合计：~1.9h
- **v4.0 闭源文档深化审查总工作量**：~9.4h

---

## 5. 残留项状态复核

### 5.1 R3-1：05-tech-reference-and-improvement/ 1738 处 `agentos_` 归档声明

**当前状态**：✅ **已正确归档**

**证据**：
- `05-tech-reference-and-improvement/README.md` 存在且完整（76 行）
- L15-26 明确记录 1738 处 `agentos_` 残留及 5 个文件的分布
- L28-34 说明不修正原因（历史记录完整性 + 无工程影响 + 成本收益不匹配）
- L36-43 引用当前前缀规范（SSoT §3.12，`airy_*`）

**v4.0 复核结论**：R3-1 归档声明完整、准确，无需修改。

### 5.2 R3-2：7 处 `docs/AirymaxAgentOS/` 路径

**当前状态**：⚠️ **仍残留（7 处，已知残留项）**

**证据**：

| 位置 | 内容 |
|------|------|
| `手册:L20` | `OS 设计文档全部在 docs/AirymaxAgentOS/ 模块内` |
| `手册:L2243` | `BAN-358 禁止 OS 设计文档放置在 docs-closed/（必须放置在 docs/AirymaxAgentOS/）` |
| `手册:L4379` | `OS 详细设计文档全部在 docs/AirymaxAgentOS/ 模块内` |
| `手册:L4393` | `文档位置: docs-closed/ \| docs/AirymaxAgentOS/` |
| `手册:L4450` | `文档: docs.openeuler.org \| docs/AirymaxAgentOS/` |
| `手册:L4473` | `OS 设计文档: docs/AirymaxAgentOS/（docs 顶层仓下子目录，12 个文档）` |
| `手册:L4494` | `BAN-358 禁止 OS 设计文档放置在 docs-closed/（必须放置在 docs/AirymaxAgentOS/）` |

**路径验证**：实际目录为 `docs/AirymaxOS/`（已通过 `ls` 确认存在），`docs/AirymaxAgentOS/` 不存在。7 处引用均为错误路径。

**v4.0 复核结论**：R3-2 仍残留 7 处，与 v3.0 fix-verification §5.3 声明一致（列为 P1 残留，建议 1.0.1 M1 中期处理）。路径错误已确认（`AirymaxAgentOS/` → `AirymaxOS/`）。

### 5.3 新发现残留项（v4.0 补充）

| # | 残留项 | 严重度 | v3.0 状态 | v4.0 发现 |
|---|--------|--------|----------|----------|
| R4-V4-1 | `agentos/` 目录路径 39 处当前引用 | P1 | 未列入残留项（静默遗漏） | P1-V4-2 |
| R4-V4-2 | §34.5 错误码分段未对齐 SSoT | P1 | 未列入残留项（静默遗漏） | P1-V4-1 |
| R4-V4-3 | `daemon/` → `daemons/` 18 处未同步 | P1 | 未识别（v1~v3 盲区） | P1-V4-3 |
| R4-V4-4 | `AIRY_OK` 残留 2 处 | P1 | 未识别（域1 副作用） | P1-V4-5 |
| R4-V4-5 | `AIRY_ERR_NOT_INITIALIZED` 4 处 | P1 | 未识别（域4 副作用） | P1-V4-6 |

---

## 6. 修正后评分预估

### 6.1 评分变化轨迹

| 版本阶段 | 综合评分 | 级别 | 变化 | 主要原因 |
|---------|---------|------|------|---------|
| v1.0（初始审查） | 65 | C+ | — | 8 项 P0 + 多项 P1/P2 |
| v2.0（修正后） | 72 | B- | +7 | 9/10 P0 修正 |
| v3.0（复审） | 66 | C+ | -6 | 新发现 10 P0 + 19 P1 + 18 P2 |
| v3.0（修正后预估） | ~80 | B+ | +14 | 10 P0 全部清零 + 主要 P1 修正 |
| **v4.0（深化审查）** | **75** | **B** | **-5** | v3.0 遗漏 + 副作用 + 盲区 |
| **v4.0（修正后预估）** | **~82** | **B+** | **+7** | 6 P1 + 7 P2 全部修正 |

### 6.2 v4.0 评分分析

| 维度 | v3.0 修正后预估 | v4.0 审查后 | 变化 | 扣分原因 |
|------|---------------|------------|------|---------|
| 技术准确性 | B+ | B- | -1 | §34.5 未修正 + 错误码三重不一致 + AIRY_OK 残留 + 错误码名称不匹配 |
| 工程指导性 | B+ | B- | -1 | daemon→daemons 18 处未同步 + agentos/ 39 处残留 |
| 一致性（与 SSoT） | B+ | B- | -1 | 错误码分段/权威源未对齐 + Docs/ 29 处 |
| 修正持久性 | A | A | 0 | 18/18 项持久 |
| **加权综合** | **80** | **75** | **-5** | — |

### 6.3 v4.0 修正后预估

若 v4.0 发现的 6 项 P1 + 7 项 P2 全部修正（~9.4h），闭源文档总评可回升至 **~82/B+**（比 v3.0 预估 80/B+ 高 2 分，因修正后错误码分段统一、daemon/daemons 同步、副作用清除，一致性更高）。

### 6.4 修正优先级建议

| 优先级 | 问题 | 工作量 | 理由 |
|--------|------|--------|------|
| **M1 早期** | P1-V4-3（daemon→daemons 18 处） | ~1h | 直接影响开发者路径引用，CI 构建失败 |
| **M1 早期** | P1-V4-5（AIRY_OK 残留） | ~0.2h | 直接影响编译，工作量极小 |
| **M1 早期** | P1-V4-6（错误码名称不匹配） | ~0.3h | 直接影响编译，工作量极小 |
| **M1 早期** | P1-V4-1（§34.5 错误码分段） | ~1h | 影响错误码注册标准 |
| **M1 中期** | P1-V4-2（agentos/ 39 处） | ~3h | 影响路径引用，工作量较大 |
| **M1 中期** | P1-V4-4（错误码三重不一致） | ~2h | 需决策统一方向 |
| **M1 全阶段** | P2-V4-1~7（7 项 P2） | ~1.9h | 渐进式改进 |
| **M1 中期** | R3-2（AirymaxAgentOS 7 处） | ~0.3h | 已知残留项 |

### 6.5 1.0.1 M1 就绪判定

> **闭源文档侧条件性通过 1.0.1 M1 代码开发启动条件**。
>
> **通过条件**：
> - ✅ v3.0 P0 阻断全部持久清零（18/18 项验证通过）
> - ✅ 综合评分 75/B ≥ 70/B- 最低门槛
> - ✅ 函数前缀清零（07-subsystem-specs/ + 06-contracts/ agentos_ 残留为 0）
> - ✅ IPC 消息头 SSoT 对齐（§34.2 struct airy_ipc_msg_hdr）
> - ✅ §11.6 历史决策声明就位
>
> **需并行处理**：
> - ⚠️ 6 项 P1 需在 M1 早期/中期修正（~7.5h），其中 P1-V4-3/5/6 直接影响编译
> - ⚠️ R3-2（7 处 AirymaxAgentOS 路径）需在 M1 中期修正
>
> **建议**：
> 1. **M1 启动时可并行推进代码开发**——v3.0 P0 阻断已清零，核心 SSoT 已收敛
> 2. **M1 早期优先处理（~1.5h）**：P1-V4-3（daemon→daemons）+ P1-V4-5（AIRY_OK）+ P1-V4-6（错误码名称）——这三项直接影响编译，工作量小
> 3. **M1 中期处理（~6h）**：P1-V4-1（§34.5）+ P1-V4-2（agentos/ 路径）+ P1-V4-4（错误码分段统一）+ R3-2（AirymaxAgentOS）
> 4. **M1 全阶段渐进**：7 项 P2（~1.9h）

---

<div align="center">

**© 2025-2026 SPHARX Ltd.** All Rights Reserved.

</div>

---

**报告结束** | SPHARX Ltd 内部参考 | 闭源不公开 | 审查日期：2026-07-14 | 审查版本：v4.0 | 维度：闭源文档深化审查
