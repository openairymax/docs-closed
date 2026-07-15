Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# AirymaxRT（agentrt）整体方案系统性深度复审报告 v2.1

> **审查范围**：`/home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxRT/` 全量文档（88 个 .md 文件 + 3 个 .drawio 文件）
> **审查基线**：AirymaxOS 文档体系（123 个 .md 文件）+ IRON-9 v2 三层共享模型 + SSoT 注册表（09-ssot-registry.md）+ 120-cross-project-code-sharing.md
> **对比基线**：v1.0 审查报告（`docs-closed/agentrt/00-reviews/_review_v1.0/03-airymaxrt-solution-review.md`）
> **审查日期**：2026-07-13
> **审查者**：Airymax 架构审查专家（agentrt 子代理）
> **审查维度**：v1.0 修复验证 / 目录结构 / 文档深度 / 方案冲突 / 工程标准对齐 / 命名前缀 / 跨平台 / 29 仓拆分 / 草案清单 / IPC 一致性 / 技术准确性 / 抄袭风险 / 改进建议

---

## 0. 执行摘要

### 0.1 v1.0 vs v2.1 评分对比

| 维度 | v1.0 评分 | v2.1 评分 | 修复进展 | 关键问题 |
|------|----------|----------|---------|---------|
| 目录结构完整性 | 70/B- | 68/C+ | **未修复**（70-build / 80-testing / 120-development-process 仍缺失） | 50-specifications/ 仍空置 1 文件 |
| 文档内容深度 | 75/B | 76/B | 持平 | 5 个 <100 行草案仍存在；新增 70-toolkit/01-protocol-guide.md（1220 行） |
| 方案冲突 | 45/D+ | **40/D** | **倒退**（错误码方案仍 4+ 套并行） | 06-iron9-shared-model.md 错误码与 L3 安全治理直接冲突 |
| 工程标准对齐 | 80/B | 78/B | 持平 | 符号链接正确；引用断链（08-compliance-checklist.md 仍不存在） |
| 命名前缀 | 72/B- | 70/C+ | **未修复** | `agentrt_*` 专属前缀仍 0 处使用；IPC 头违规蔓延至 2 文件 |
| 跨平台一致性 | 78/B | 75/B- | **未修复** | "操作系统"自称 51 处匹配（v1.0 为 40 行） |
| 29 仓拆分对齐 | 30/F | **30/F** | **完全未修复** | 0 处提及"29 仓 / 伞仓 / 管理仓 / 叶子仓" |
| 草案文档 | 65/C+ | 66/C+ | 持平 | 21 个 <200 行文件 |
| IPC 协议一致性 | 55/D+ | **50/D** | **倒退** | IPC 头违规从 1 文件蔓延至 2 文件 |
| **综合** | **62/C+** | **58/C** | **下降 4 分** | 5 项 P0 全部未修复，部分问题加剧 |

### 0.2 核心结论

**v1.0 → v2.1 关键变化：评分下降 4 分（62 → 58），5 项 P0-CRITICAL 问题全部未修复，且部分问题加剧。**

**v1.0 P0-CRITICAL 5 项问题修复验证**：

| # | 问题 | v1.0 状态 | v2.1 状态 | 修复进展 |
|---|------|----------|----------|---------|
| P0-1 | 错误码 6 套并行 | 6+ 套 | **仍 4+ 套**（A: -1 / B: -22 / C: EINVAL / D: 1001 / E: ARE_* / F: AIRY_OK） | ✗ 未修复 |
| P0-2 | "操作系统"定位矛盾 | 40 行匹配 | **51 行匹配，分布 18 文件** | ✗ 未修复（数量增加） |
| P0-3 | [SC] 头文件清单不一致 | bpf_struct_ops.h 列第 6 位 | **bpf_struct_ops.h 升至第 1 位，syscalls.h 完全缺失** | ✗ 倒退（更严重） |
| P0-4 | Cupola/Cupolas 术语不一致 | 4 文件用单数 | **5 文件用单数**（新增 03-overall-architecture.drawio） | ✗ 未修复（数量增加） |
| P0-5 | Daemon 数量标注冲突（10 vs 12） | 01-system-architecture.md 标"10" | **仍标"10"** | ✗ 未修复 |

**v1.0 P1/P2 其他问题修复验证**：

| # | 问题 | v2.1 状态 |
|---|------|----------|
| P1-3 | 29 仓拆分未文档化 | ✗ 仍未文档化（0 处提及） |
| P1-4 | `agentrt_*` 专属 API 前缀缺失 | ✗ 仍 0 处使用 |
| P1-5 | MemoryRovol 层级命名冲突 | ✗ 02-c-language-boundary.md:72 仍为 "Working/Short-term/Long-term/Archival" |
| P1-7 | 草案文档充实 | △ 70-toolkit/01-protocol-guide.md 新增 1220 行，但 5 个 <100 行文件未充实 |
| P2-1 | 06-iron9-shared-model.md 递归注释 | ✗ 行 214 仍为 `/* 成功（替代 AIRY_EOK） */` |
| P2-2 | TERMINOLOGY.md 路径头错误 | ✗ 行 8 仍为 `Docs/TERMINOLOGY.md` |

**核心问题**：v1.0 报告的所有 5 项 P0-CRITICAL 问题在 v2.1 中**全部未修复**，且 [SC] 头文件清单问题甚至倒退（从"第 6 位错列 bpf_struct_ops.h"恶化为"第 1 位就是 bpf_struct_ops.h，syscalls.h 完全缺失"）。AirymaxRT 文档体系在**架构设计层面**仍保持高质量（MicroCoreRT / CoreLoopThree / MemoryRovol / Cupolas 7 子系统 / 12 Daemons V8.0 / MCIS 体系并行论 / 五维正交 24 原则），但在**工程一致性层面**存在系统性问题，**强烈建议在进入 1.0.1 M1 代码开发前优先修复全部 P0 问题**。

---

## 1. v1.0 问题修复验证（逐项验证）

### 1.1 [P0-CRITICAL] 错误码 6 套并行 —— 未修复

**v1.0 问题**：6 套不同错误码定义方案并行，违反 SSoT 原则。

**v2.1 验证**：经 Grep 验证，**仍存在至少 4+ 套错误码方案并行**。

| 方案 | 文件 | 行号 | 成功码 | AIRY_EINVAL | AIRY_ENOMEM |
|------|------|------|--------|-------------|-------------|
| A | `30-interfaces/05-runtime-interfaces/03-l3-security-governance.md` | 306-310 | `AIRY_EOK=0` | `-1` | `-2` |
| B | `10-architecture/06-iron9-shared-model.md` | 215-216 | `AIRY_EOK=0` | `-22` | `-12` |
| C | `10-architecture/00-architectural-principles.md` | 924-925 | — | `EINVAL` | `ENOMEM` |
| D | `10-architecture/05-syscall.md` | 644-645 | `AIRY_EOK=0` | `1001` | `1002` |
| E | `30-interfaces/05-runtime-interfaces/01-l1-runtime-interface.md` | 52-61 | `ARE_OK (0)` | `ARE_EINVAL=-1` | `ARE_ENOMEM=-2` |
| F | `20-modules/10-contracts/06-glossary-index.md` | 175 | `AIRY_OK=0`（非 EOK！） | `-1` | `-2` |
| SSoT-A | `TERMINOLOGY.md` | 209 | `AIRY_EOK=0` | `-1` | — |
| SSoT-B | `20-modules/10-contracts/04-syscall-api-contract.md` | 100-101 | `AIRY_EOK=0` | `-1` | `-2` |

**冲突点**：

1. **成功码 3 种命名**：`AIRY_EOK`（多数文档）/ `AIRY_OK`（`06-glossary-index.md:175`）/ `ARE_OK`（`01-l1-runtime-interface.md:52`）
2. **`AIRY_EINVAL` 4 种值**：`-1`（TERMINOLOGY/L3/syscall-api-contract）/ `-22`（06-iron9-shared-model.md，POSIX 对齐）/ `EINVAL`（00-architectural-principles.md）/ `1001`（05-syscall.md，正值）
3. **`AIRY_ENOMEM` 4 种值**：`-2` / `-12`（POSIX 对齐）/ `ENOMEM` / `1002`
4. **超时码 2 种命名**：`AIRY_ETIMEOUT`（14 处）/ `AIRY_ETIMEDOUT`（`06-glossary-index.md:180`）
5. **超时码值冲突**：`AIRY_ETIMEOUT=-11`（多数）/ `AIRY_ETIMEDOUT=-6`（glossary-index.md）

**L3 安全治理内部自相矛盾**（`30-interfaces/05-runtime-interfaces/03-l3-security-governance.md`）：
- 第 5.2 节定义 `AIRY_EINVAL=-1, AIRY_ENOMEM=-2, AIRY_EPERM=-4, AIRY_ETIMEOUT=-11, AIRY_ENOSYS=-3`
- 第 5.3 节禁令 #1："禁止多套并行错误码系统"
- 但 `06-iron9-shared-model.md:215` 的 `AIRY_EINVAL=-22` 与本标准直接冲突
- **文档自身的禁令被另一个文档违反**——属于系统性 SSoT 崩溃

**证据**：
```bash
grep -rn "AIRY_EINVAL" --include="*.md" docs/AirymaxRT/  # 仍返回 4 种不同值
```

**影响**：开发者无法确定应使用哪套错误码；C 代码编译将出现宏重定义冲突；违反 IRON-1（用户空间 ABI 永不破坏）和 IRON-014（[SC] 共享契约层单一数据源）。

**修复进展**：✗ **未修复**，部分维度甚至加剧（L3 安全治理文档明确禁令多套错误码，但 06-iron9-shared-model.md 仍用 -22）。

### 1.2 [P0-CRITICAL] "操作系统"定位与用户态运行时矛盾 —— 未修复，加剧

**v1.0 问题**：40 行匹配"操作系统"，15+ 处误称"操作系统"。

**v2.1 验证**：经 Grep 验证，**51 处匹配，分布 18 个文件**（数量从 40 → 51 增加）。

**至少 9 处明确误称"操作系统"**（与 agentrt 用户态 Ring 3 定位直接矛盾）：

| 文件 | 行号 | 文本 | 冲突 |
|------|------|------|------|
| `10-architecture/00-architectural-principles.md` | 54 | "Airymax 是一个**驱动多智能体协作的操作系统**" | ✗ 应为"运行时平台" |
| `10-architecture/04-microcorert.md` | 19 | "微核心为整个智能体操作系统提供可靠…运行时基础" | ✗ 应为"运行时" |
| `10-architecture/04-microcorert.md` | 271 | "共同构成完整的智能体操作系统架构" | ✗ 应为"运行时架构" |
| `10-architecture/40-philosophy/01-design-philosophy.md` | 110 | "不是'框架'…而是'操作系统'（Operating System）" | ✗ |
| `10-architecture/40-philosophy/01-design-philosophy.md` | 117 | "agentrt — 内部操作系统层" | ✗ 应为"运行时层" |
| `10-architecture/40-philosophy/01-design-philosophy.md` | 119 | "agentrt 是 Airymax 的内部 OS 层" | ✗ |
| `20-modules/10-contracts/05-logging-format.md` | 73 | "Airymax 作为一个分布式多智能体操作系统" | ✗ |
| `30-interfaces/10-algorithms/README.md` | 179 | "Airymax 是一个先进的智能体操作系统" | ✗ |
| `30-interfaces/04-mainpage.dox` | 2, 6 | "多体控制论智能操作系统" / "构建的智能体操作系统" | ✗ |

**合理的"操作系统"引用**（指代 AirymaxOS / agentrt-linux，不冲突）：
- `README.md:105` / `README_zh.md:179`："agentrt-linux 智能体操作系统文档"（指 AirymaxOS）
- `06-iron9-shared-model.md:34`："agentrt-linux（AirymaxOS）| 智能体操作系统"（指 AirymaxOS）

**核心矛盾**：
- `04-microcorert.md:183`（v1.0 引用）："MicroCoreRT 运行在用户态（Ring 3），依赖宿主操作系统"
- `00-architectural-principles.md:54`："Airymax 是一个**驱动多智能体协作的操作系统**"

两者直接矛盾。agentrt 不是操作系统，而是运行在操作系统之上的用户态运行时平台。

**修复进展**：✗ **未修复**，且数量从 40 → 51 增加（约 27.5% 增长）。

### 1.3 [P0-CRITICAL] [SC] 头文件清单与 SSoT 不一致 —— 倒退

**v1.0 问题**：`06-iron9-shared-model.md` 第 6 个 [SC] 头文件错列为 `bpf_struct_ops.h`，应为 `syscalls.h`。

**v2.1 验证**：经读取 `06-iron9-shared-model.md` 与 `120-cross-project-code-sharing.md` 对比，**问题倒退**——`bpf_struct_ops.h` 从第 6 位升至**第 1 位**，且 `syscalls.h` 完全从清单中消失。

| 序号 | `06-iron9-shared-model.md`（agentrt 侧，v2.1） | `120-cross-project-code-sharing.md`（SSoT） | 一致性 |
|------|----------------------------------------------|---------------------------------------------|--------|
| 1 | **`bpf_struct_ops.h`** | `memory_types.h` | ✗ **完全冲突** |
| 2 | `memory_types.h` | `security_types.h` | ✗ 错位 |
| 3 | `security_types.h` | `cognition_types.h` | ✗ 错位 |
| 4 | `cognition_types.h` | `sched.h` | ✗ 错位 |
| 5 | `sched.h` | `ipc.h` | ✗ 错位 |
| 6 | `ipc.h` | `syscalls.h` | ✗ **完全缺失** |

**SSoT 明确说明**（`120-cross-project-code-sharing.md:65-76`）：
- 6 个 [SC] 核心头文件第 1 个是 `memory_types.h`，第 6 个是 `syscalls.h`
- `bpf_struct_ops.h` 是**补充共享文件**（§2.2，非 [SC] 核心头文件）

**证据**：
- `06-iron9-shared-model.md:68` 第 1 行就列出 `bpf_struct_ops.h`
- `120-cross-project-code-sharing.md:71` 第 1 行是 `memory_types.h`
- `120-cross-project-code-sharing.md:76` 第 6 行明确是 `syscalls.h`
- `120-cross-project-code-sharing.md:85` 标题 "2.2 补充共享文件：bpf_struct_ops.h（非 [SC] 核心头文件）"

**修复进展**：✗ **倒退**——比 v1.0 更严重，从"第 6 位错列"恶化为"第 1 位就是错列 + syscalls.h 完全缺失"。

### 1.4 [P1-MAJOR] Cupola vs Cupolas 术语不一致 —— 未修复，加剧

**v1.0 问题**：4 个文件使用单数 Cupola。

**v2.1 验证**：经 Grep 验证，**5 个文件使用单数 Cupola**（新增 1 个 .drawio 文件）。

**使用 Cupola（单数，错误）的文件**：

| 文件 | 使用情况 |
|------|---------|
| `10-architecture/01-system-architecture.md` | 22 处（行 34, 52, 80, 82, 86, 107, 108, 147, 152, 175, 261, 455, 468, 490, 502, 504, 525, 538, 571, 586 等） |
| `10-architecture/30-kernel/02-c-language-boundary.md` | 行 18, 59 |
| `10-architecture/40-philosophy/01-design-philosophy.md` | 行 128, 142（"每一个 Cupola 都是一个…"） |
| `20-modules/10-contracts/05-logging-format.md` | 行 478（"Cupola policy violation detected"） |
| **`10-architecture/60-diagrams/03-overall-architecture.drawio`** | **11 处**（新增违规，v1.0 未列入） |

**使用 Cupolas（复数，正确）的文件**：19 个文件（包括 `TERMINOLOGY.md`、`04-microcorert.md`、`06-iron9-shared-model.md`、`06-glossary-index.md` 等）

**核心矛盾**：
- `TERMINOLOGY.md:193` 明确"Cupolas…包含 Guards、Permission、Sanitizer、Audit、Workbench、Security Vault、Network Security **七个子系统**"
- `01-system-architecture.md:34` 使用 ASCII 图 "Cupola (LLM Svc) | Cupola (Tool Svc) | Cupola (Info Svc)"
- 单数 Cupola 暗示单一服务包装器，复数 Cupolas 是 7 子系统安全层，语义不同

**修复进展**：✗ **未修复**，且新增 1 个违规文件（`03-overall-architecture.drawio`，11 处 Cupola）。

### 1.5 [P1-MAJOR] Daemon 数量标注冲突（10 vs 12） —— 未修复

**v1.0 问题**：`01-system-architecture.md` 标注"10 个核心用户态服务"，实际清单为 12 个。

**v2.1 验证**：经读取 `01-system-architecture.md`，**第 305 行仍标注"10 个"，第 309 行 ASCII 图仍标 "(10)"**。

| 文件 | 行号 | 文本 | 冲突 |
|------|------|------|------|
| `10-architecture/01-system-architecture.md` | 305 | "Airymax 系统包含 **10 个**核心用户态服务 (Daemon Processes)" | ✗ 应为 12 |
| `10-architecture/01-system-architecture.md` | 309 | ASCII "Airymax Daemon Services **(10)**" | ✗ 应为 12 |
| `10-architecture/01-system-architecture.md` | 351-366 | 实际列出 **12 个 daemon**（含 hook_d, plugin_d） | ✓ 12 个 |
| `10-architecture/01-system-architecture.md` | 575 | "Team A (**12 daemons**)" | ✓ 正确 |
| `10-architecture/50-services/01-daemon.md` | 16 | "实际存在 **12 个独立服务进程**"（V8.0 已修正） | ✓ 正确 |

**矛盾**：同一文档 `01-system-architecture.md` 内部第 305 行"10 个" 与第 351-366 行"12 个 daemon" 直接冲突，且与第 575 行"Team A (12 daemons)" 冲突。

**修复进展**：✗ **未修复**，与 v1.0 完全一致。

### 1.6 [P1-MAJOR] MemoryRovol 层级命名冲突 —— 未修复

**v1.0 问题**：`02-c-language-boundary.md:72` 使用 "Working → Short-term → Long-term → Archival"，与标准命名 "L1 Raw → L2 Feature → L3 Structure → L4 Pattern" 完全不同。

**v2.1 验证**：经读取，**`02-c-language-boundary.md:72` 仍为 "Working → Short-term → Long-term → Archival"**。

| 文件 | 行号 | 命名方案 | 冲突 |
|------|------|---------|------|
| `10-architecture/03-memoryrovol.md` | — | L1 Raw / L2 Feature / L3 Structure / L4 Pattern | ✓ 标准 |
| `50-engineering-standards/120-cross-project-code-sharing.md` | 135-139 | L1 HOT / L2 WARM / L3 COLD / L4 PMEM | ✓ [SC] 语义层（物理存储） |
| `10-architecture/30-kernel/02-c-language-boundary.md` | 72 | Working → Short-term → Long-term → Archival | ✗ 第三套命名 |
| `10-architecture/50-services/02-logging.md` | 22, 24 | 日志 L1→L4（L1 原始日志 → L4 智洞察报告） | ✗ 与 MemoryRovol L1-L4 冲突 |

**修复进展**：✗ **未修复**。

### 1.7 [P1-MAJOR] 文件路径引用错误（系统性） —— 部分修复

**v1.0 问题**：多个文档引用 `00-basic-theories/` 等不存在路径。

**v2.1 验证**：

**仍未修复的路径引用错误**：

| 文件 | 行号 | 错误引用 | 正确路径 |
|------|------|---------|---------|
| `TERMINOLOGY.md` | 604-607 | `00-basic-theories/01-mcis-cn.md` 等 4 处 | `00-requirements/01-mcis-cn.md` |
| `10-architecture/00-architectural-principles.md` | 1516-1519 | `00-basic-theories/` | `00-requirements/` |
| `20-modules/10-contracts/04-syscall-api-contract.md` | 1366 | `00-basic-theories/04-design-principles-cn.md` | `00-requirements/` |
| `20-modules/10-contracts/02-skill-contract.md` | 42, 43, 1005, 1006 | `00-basic-theories/` | `00-requirements/` |
| `20-modules/10-contracts/01-agent-contract.md` | 42, 44, 821, 822 | `00-basic-theories/` | `00-requirements/` |
| `20-modules/10-contracts/05-logging-format.md` | 960 | `00-basic-theories/` | `00-requirements/` |
| `20-modules/10-contracts/03-protocol-contract.md` | 874 | `00-basic-theories/` | `00-requirements/` |
| `README.md` | 62 | `50-engineering-standards/08-compliance-checklist.md` | 文件不存在 |
| `README_zh.md` | 87 | `50-engineering-standards/08-compliance-checklist.md` | 文件不存在 |
| `20-modules/10-contracts/06-glossary-index.md` | 183, 185 | `50-engineering-standards/50-project-erp/error_code_reference.md` | 文件不存在（实际只有 README.md / project_erp.md） |
| `20-modules/10-contracts/04-syscall-api-contract.md` | 1293 | `../70-project-erp/02-error-code-reference.md` | 路径不存在 |
| `140-application-development/24-create-agent.md` | 704 | `50-engineering-standards/10-coding-style/C_coding_style_standard.md` | 实际为 `C_Cpp_coding_style.md` |
| `140-application-development/25-create-skill.md` | 658 | `50-engineering-standards/10-coding-style/C_coding_style_standard.md` | 实际为 `C_Cpp_coding_style.md` |
| `140-application-development/15-testing-standards.md` | 477 | `C_coding_style_standard.md` | 实际为 `C_Cpp_coding_style.md` |
| `140-application-development/10-migration-guide.md` | 418 | `C_coding_style_standard.md` | 实际为 `C_Cpp_coding_style.md` |
| `10-architecture/00-architectural-principles.md` | 1524 | `C_Cpp_secure_coding_standard.md` | 文件不存在 |
| `06-iron9-shared-model.md` | 331-334 | `C_coding_style_standard.md` / `C_Cpp_secure_coding_standard.md` / `Rust_coding_style_standard.md` / `log_standard.md` | 实际为 `C_Cpp_coding_style.md` / `Rust_coding_style.md` 等（4 个全错） |
| `20-modules/10-contracts/06-glossary-index.md` | 124, 164, 165 | `../30-coding-standard/13-rust-coding-style.md` 等 | 路径完全不存在 |

**TERMINOLOGY.md 路径头错误**：
- `TERMINOLOGY.md:8` 标注 `Docs/TERMINOLOGY.md`（应为 `docs/AirymaxRT/TERMINOLOGY.md`）
- `50-specifications/10-contracts/06-glossary-index.md:8` 标注 `OpenAirymax/Docs/50-specifications/...`（大小写错误，应为 `docs/AirymaxRT/...`）

**修复进展**：✗ **大部分未修复**（19 处 `00-basic-theories/` 错误仍存在；6+ 处 `08-compliance-checklist.md` 等断链）。

### 1.8 [P0-CRITICAL] IPC 消息头结构体三重违规 —— 未修复，蔓延

**v1.0 问题**：`30-interfaces/06-ipc/README.md` 的 `are_ipc_message_header_t` 三重违规。

**v2.1 验证**：经读取，**06-ipc/README.md 完全未修改**，且**违规蔓延至 30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md**。

| 文件 | 行号 | 违规类型 |
|------|------|---------|
| `30-interfaces/06-ipc/README.md` | 27-42 | `are_ipc_message_header_t` / `uint32_t` / 无 `__attribute__((packed))` / 13 字段 / `char source[32]` |
| `30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md` | 60, 93-109 | `ARE_IPC_MAGIC` / `are_ipc_message_header_t` / `uint32_t` / 14 字段 / `char source[32]` |

**对比 SSoT**（`120-cross-project-code-sharing.md:343` + `06-iron9-shared-model.md:126-136`）：

| 属性 | 违规文件 | SSoT 要求 |
|------|---------|----------|
| 结构体名 | `are_ipc_message_header_t` | `airy_ipc_msg_hdr` |
| 类型 | `uint32_t`/`uint16_t`/`uint64_t` | `__u32`/`__u16`/`__u64` |
| 对齐 | 无 | `__attribute__((packed))` |
| 字段数 | 13-14 字段 | 8 字段 |
| 字段类型 | `char source[32]`/`char target[32]` | `__u64 src_task`/`__u64 dst_task` |
| 大小验证 | 无 | `_Static_assert(sizeof(...) == 128)` |
| magic 宏名 | `ARE_IPC_MAGIC` | `AIRY_IPC_MAGIC` |

**06-iron9-shared-model.md 的反讽**：
- 行 140 明确："结构体名称为 `airy_ipc_msg_hdr`（**不是** `airymaxos_ipc_msg_hdr` 或 `are_ipc_message_header_t`）"
- 行 268 明确："使用 `airy_` 前缀（如 `airy_ipc_msg_hdr`），不使用 `airymaxos_` 或 `are_` 前缀"
- 但同项目的 `06-ipc/README.md` 和 `02-l2-service-protocol.md` 仍违规使用 `are_ipc_message_header_t`

**修复进展**：✗ **未修复**，且违规从 1 文件蔓延至 2 文件。

### 1.9 [P2-MINOR] 06-iron9-shared-model.md 递归注释 —— 未修复

**v1.0 问题**：`06-iron9-shared-model.md:214` 注释 `/* 成功（替代 AIRY_EOK） */` 自相矛盾。

**v2.1 验证**：经 Grep 验证，**行 214 仍为 `/* 成功（替代 AIRY_EOK） */`**。

**修复进展**：✗ **未修复**（0.1h 工作量未完成）。

### 1.10 [P2-MINOR] TERMINOLOGY.md 路径头错误 —— 未修复

**v1.0 问题**：`TERMINOLOGY.md:8` 标注 `Docs/TERMINOLOGY.md`，应为 `docs/AirymaxRT/TERMINOLOGY.md`。

**v2.1 验证**：经 Grep 验证，**行 8 仍为 `Docs/TERMINOLOGY.md`**。

**修复进展**：✗ **未修复**（0.1h 工作量未完成）。

### 1.11 [P0-CRITICAL] 29 仓拆分完全未文档化 —— 未修复

**v1.0 问题**：0 处提及 29 仓拆分方案。

**v2.1 验证**：经 Grep 验证，**仍 0 处提及"29 仓 / 29-repo / 伞仓 / 管理仓 / 叶子仓 / 顶层仓"**。

唯一相关的 submodule 引用：
- `30-interfaces/05-runtime-interfaces/README.md:29` 仅提及"`Docs/` 本身已是独立 git submodule"
- `140-application-development/23-troubleshooting-faq.md:843` 仅引用 `git submodule update --init --recursive` 命令

**修复进展**：✗ **完全未修复**。

### 1.12 [P1-MAJOR] `agentrt_*` 专属 API 前缀缺失 —— 未修复

**v1.0 问题**：全文档 0 处使用 `agentrt_*` 前缀。

**v2.1 验证**：经 Grep 验证，**仍 0 处使用 `agentrt_*` 作为函数/API 前缀**。

仅在文件路径中出现 `agentrt`（如 `AgentRT/agentrt/...`），不构成 API 前缀使用。

**修复进展**：✗ **未修复**。

---

## 2. 新发现问题清单（按 P0/P1/P2 分级）

### 2.1 P0 新发现问题

#### [P0-NEW-01] L3 安全治理禁令被 06-iron9-shared-model.md 直接违反

**问题描述**：`30-interfaces/05-runtime-interfaces/03-l3-security-governance.md` 第 5.3 节禁令 #1 明确"禁止多套并行错误码系统"，但 `06-iron9-shared-model.md:215-216` 仍使用 `AIRY_EINVAL=-22, AIRY_ENOMEM=-12`（POSIX errno 对齐值），与 L3 安全治理标准的 `AIRY_EINVAL=-1, AIRY_ENOMEM=-2` 直接冲突。

**影响**：两个声称自己是 SSoT 的文档相互矛盾，开发者无法判断哪一份是权威。

**证据**：
- `03-l3-security-governance.md:306` "AIRY_EINVAL | -1 | 参数无效"
- `06-iron9-shared-model.md:215` "AIRY_EINVAL (-22) /* 参数无效（对齐 POSIX EINVAL） */"

#### [P0-NEW-02] 06-iron9-shared-model.md [SC] 头文件清单顺序全部错位

**问题描述**：除 v1.0 已识别的 `bpf_struct_ops.h` 错列问题外，**所有 6 个 [SC] 头文件的顺序都与 SSoT 不一致**（v1.0 仅识别第 6 位错列，v2.1 发现全表错位）。

**证据**：见第 1.3 节对比表。

#### [P0-NEW-03] IPC 头违规蔓延至 02-l2-service-protocol.md

**问题描述**：v1.0 仅识别 `06-ipc/README.md` 的 IPC 头违规，v2.1 发现 `30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md` 同样违规（行 60-109），违规从 1 文件蔓延至 2 文件。

**证据**：见第 1.8 节。

### 2.2 P1 新发现问题

#### [P1-NEW-01] 60-diagrams/03-overall-architecture.drawio Cupola 单数违规

**问题描述**：v1.0 未识别的 .drawio 文件 `10-architecture/60-diagrams/03-overall-architecture.drawio` 含 11 处 `Cupola`（单数），包括：
- "Cupola 间通信"
- "调度 Cupola 执行"
- "IPC Bus（调度 Cupola）"
- "Layer 6: Cupola Layer 服务穹顶层"
- "Cupola (LLM Svc)" / "Cupola (Tool Svc)" / "Cupola (Info Svc)" / "Cupola (其他)"
- "Cupola Sandbox"
- 图例 "L6 Cupola"

**影响**：v1.0 漏检，需在 v2.2 修复时一并清理。

#### [P1-NEW-02] 50-specifications/06-glossary-index.md 路径头错误

**问题描述**：`50-specifications/10-contracts/06-glossary-index.md:8` 标注 `OpenAirymax/Docs/50-specifications/10-contracts/06-glossary-index.md`，路径大小写错误（`Docs` 应为 `docs`）。

**证据**：经 Grep 验证。

#### [P1-NEW-03] 50-specifications/06-glossary-index.md 内容与 20-modules 版本重复

**问题描述**：v1.0 P1-06 已指出此问题，v2.1 经 diff 验证，两份文件**仅路径头和路径引用不同**（`Docs/50-specifications/...` vs `docs/AirymaxRT/20-modules/...`），内容完全重复。

**证据**：
```bash
diff 50-specifications/10-contracts/06-glossary-index.md 20-modules/10-contracts/06-glossary-index.md
# 仅路径头和路径引用不同，内容重复
```

#### [P1-NEW-04] 50-specifications/06-glossary-index.md 引用错误路径

**问题描述**：除 v1.0 已识别的 `00-basic-theories/` 错误外，`50-specifications/10-contracts/06-glossary-index.md` 还引用：
- `../30-coding-standard/13-rust-coding-style.md`（路径不存在）
- `../30-coding-standard/01-c-coding-style.md`（路径不存在）
- `../30-coding-standard/02-c-cpp-secure-coding.md`（路径不存在）
- `../70-project-erp/02-error-code-reference.md`（路径不存在）

#### [P1-NEW-05] 06-glossary-index.md 中 AGENTRT_SECURE_ZERO 宏名错误

**问题描述**：`50-specifications/10-contracts/06-glossary-index.md:165` 使用 `AGENTRT_SECURE_ZERO`，而 `20-modules/10-contracts/06-glossary-index.md:165` 使用 `AIRY_SECURE_ZERO`。两份"重复"文件连宏名都不一致。

**证据**：经 diff 验证。

### 2.3 P2 新发现问题

#### [P2-NEW-01] README.md 英文版内容明显简于中文版

**问题描述**：英文 `README.md` 仅 112 行，中文 `README_zh.md` 187 行。英文版缺少：
- 子目录详细列表（仅列顶层目录）
- 文档质量标准段
- 完整的 140-application-development 子文件列表（仅列 4 个，中文列 24 个）

**证据**：经 wc -l 和内容对比验证。

#### [P2-NEW-02] README.md 与 README_zh.md 引用同样的断链

**问题描述**：两份 README 同时引用不存在的 `50-engineering-standards/08-compliance-checklist.md`（v1.0 已指出，v2.1 仍未修复）。

**证据**：`README.md:62` / `README_zh.md:87`。

---

## 3. 目录结构完整性评估

### 3.1 总体统计

| 项目 | .md 文件数 | 顶层目录数 | 说明 |
|------|-----------|-----------|------|
| AirymaxRT | 88 | 7（含符号链接） | 含 3 个根级文件 |
| AirymaxOS | 123 | 12 | 对比基准 |

**与 v1.0 一致**：文档总数 88，与 v1.0 完全相同。

### 3.2 顶层目录分布

| 目录 | 文件数 | v1.0 评估 | v2.1 评估 |
|------|--------|----------|----------|
| `00-requirements/` | 8 | 充实 | 充实 |
| `10-architecture/` | 14 | 充实 | 充实（新增 `60-diagrams/`，含 3 个 .drawio） |
| `20-modules/` | 6 | 偏少 | 偏少（无变化） |
| `30-interfaces/` | 29 | 充实 | 充实（`70-toolkit/` 新增 2 个文件：`01-protocol-guide.md` 1220 行、`02-protocol-quickstart.md` 322 行） |
| `50-engineering-standards/` | 23（符号链接） | 共享，正确 | 共享，正确（符号链接仍指向 `../AirymaxOS/50-engineering-standards`） |
| `50-specifications/` | 1 | 近乎空置 | **近乎空置**（仍未充实，仍 1 个文件且与 20-modules 重复） |
| `140-application-development/` | 27 | 充实 | 充实 |

### 3.3 v1.0 已识别但未修复的目录缺失

| AirymaxOS 目录 | AirymaxRT 对应 | v2.1 状态 |
|---------------|---------------|----------|
| `60-driver-model/` | 无 | 合理缺失（agentrt 无内核驱动） |
| `70-build/` | 无 | ✗ **未创建**（CMake 构建文档仍缺失） |
| `80-testing/` | `10-architecture/20-engineering/01-testing.md` | ✗ **未独立成目录** |
| `90-observability/` | 无独立目录 | ✗ 散落各文档 |
| `110-security/` | 无独立目录 | ✗ 散落 Cupolas 文档 |
| `120-development-process/` | 无 | ✗ **未创建** |

**README.md:89 设计原则辩护**：
> "AirymaxRT 仅保留 agentrt 自身有实际内容的目录。不创建仅用于镜像 AirymaxOS 的空占位目录。"

**评估**：该辩护合理但不足以解释 `70-build/`（CMake 构建）和 `120-development-process/`（开发流程）的缺失——这两者并非"镜像 AirymaxOS 的空占位"，而是 agentrt 自身应有内容。

### 3.4 符号链接验证

```
50-engineering-standards -> ../AirymaxOS/50-engineering-standards
```

**验证**：经 `readlink` + `find -L` 验证，符号链接正确，含 23 个 .md 文件，与 AirymaxOS 共享。**符合 IRON-9 v2 同源原则。**

### 3.5 目录结构评分

| 检查项 | v1.0 | v2.1 |
|--------|------|------|
| 符号链接正确 | ✓ | ✓ |
| NN-name 命名 | ✓ | ✓ |
| kebab-case 命名 | ✓ | ✓ |
| 50-specifications/ 充实 | ✗ | ✗（仍 1 文件，重复） |
| 60+ 高层目录覆盖 | ✗ | ✗（70-build / 80-testing / 120-development-process 仍缺失） |
| 与 AirymaxOS 结构对齐 | △ | △ |

**目录结构完整性评分：68/C+**（v1.0: 70/B-，下降 2 分）

---

## 4. 文档内容深度评估

### 4.1 高质量文档（≥500 行，设计完整）

| 文件 | 行数 | v2.1 评估 |
|------|------|----------|
| `30-interfaces/02-api-reference.md` | 2682 | Gateway API 完整参考 |
| `30-interfaces/03-cli-reference.md` | 1944 | CLI 命令参考 |
| `140-application-development/03-deployment-guide.md` | 1859 | 部署指南 |
| `30-interfaces/10-algorithms/README.md` | 1746 | 核心算法 |
| `10-architecture/00-architectural-principles.md` | 1530 | 24 原则五维正交体系（但仍有"操作系统"误称 + 路径错误） |
| `140-application-development/19-prompt-engineering.md` | 1501 | Prompt 工程 |
| `20-modules/10-contracts/04-syscall-api-contract.md` | 1388 | 系统调用 API 契约（错误码仍 -1，与 06-iron9-shared-model.md 冲突） |
| `140-application-development/17-plugin-sdk-tutorial.md` | 1236 | Plugin SDK 教程 |
| **`30-interfaces/70-toolkit/01-protocol-guide.md`** | **1220** | **新增**：协议指南 |
| `10-architecture/30-kernel/01-ipc.md` | 1082 | IPC 内核架构 |
| `20-modules/10-contracts/02-skill-contract.md` | 1024 | Skill 契约 |
| `30-interfaces/20-core/01-coreloop-api.md` | 996 | CoreLoop API |
| `10-architecture/02-coreloopthree.md` | 986 | 三阶段认知循环 |
| `20-modules/10-contracts/05-logging-format.md` | 983 | 结构化日志格式（仍称"操作系统"） |
| `10-architecture/03-memoryrovol.md` | 981 | 四层记忆系统 |
| `10-architecture/05-syscall.md` | 942 | 系统调用设计（错误码仍 1001，与 SSoT 冲突） |
| `140-application-development/23-troubleshooting-faq.md` | 919 | 故障排查 FAQ |
| `20-modules/10-contracts/03-protocol-contract.md` | 894 | 协议契约（错误码仍 -1） |
| `20-modules/10-contracts/01-agent-contract.md` | 840 | Agent 契约 |
| `10-architecture/04-microcorert.md` | 806 | 微核心架构（含 9 处"操作系统"误称） |
| `30-interfaces/05-runtime-interfaces/01-l1-runtime-interface.md` | 797 | L1 运行时接口（ARE_* 错误码方案） |
| `30-interfaces/05-runtime-interfaces/03-l3-security-governance.md` | 784 | L3 安全治理（错误码 SSoT，与 06-iron9 冲突） |
| `30-interfaces/30-daemon/02-gateway-api.md` | 769 | Gateway API |
| `30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md` | 767 | L2 服务协议（IPC 头违规蔓延至此） |
| `10-architecture/50-services/02-logging.md` | 765 | 日志系统（L1-L4 与 MemoryRovol 命名冲突） |

### 4.2 草案 / 过短文档（<200 行）

| 优先级 | 文件 | 行数 | v2.1 状态 |
|--------|------|------|----------|
| **P0** | `50-specifications/10-contracts/06-glossary-index.md` | 229 | **未删除**——仍与 `20-modules/10-contracts/06-glossary-index.md` 重复 |
| **P0** | `30-interfaces/05-runtime-interfaces/README.md` | 49 | **未充实** |
| **P0** | `30-interfaces/06-ipc/README.md` | 69 | **未重写**——IPC 头三重违规仍未修复 |
| **P0** | `30-interfaces/08-service-discovery/README.md` | 76 | **未充实** |
| **P0** | `140-application-development/01-sdk/README.md` | 80 | **未充实或删除** |
| **P1** | `30-interfaces/07-rpc-api/README.md` | 90 | **未充实** |
| **P1** | `00-requirements/04-design-principles-cn.md` | 99 | **未充实** |
| **P1** | `00-requirements/04-design-principles.md` | 106 | **未充实** |
| **P1** | `30-interfaces/60-syscalls/06-telemetry.md` | 112 | **未充实** |
| **P1** | `README.md` | 112 | 英文版仍简于中文版（187 行） |
| **P1** | `30-interfaces/README.md` | 120 | **未充实** |
| **P1** | `00-requirements/02-cognition-design-cn.md` | 123 | **未充实** |
| **P1** | `00-requirements/02-cognition-design.md` | 130 | **未充实** |
| **P2** | `10-architecture/50-services/01-daemon.md` | 141 | V8.0 已扩充 |
| **P2** | `00-requirements/03-memory-design-cn.md` | 143 | **未充实** |
| **P2** | `30-interfaces/60-syscalls/05-task.md` | 145 | **未充实** |
| **P2** | `00-requirements/03-memory-design.md` | 152 | **未充实** |
| **P2** | `00-requirements/01-mcis-cn.md` | 158 | **未充实** |
| **P2** | `00-requirements/01-mcis.md` | 169 | **未充实** |
| **P2** | `30-interfaces/60-syscalls/02-memory.md` | 170 | **未充实** |
| **P2** | `30-interfaces/60-syscalls/01-agent.md` | 179 | **未充实** |
| **P2** | `30-interfaces/60-syscalls/03-session.md` | 184 | **未充实** |
| **P2** | `README_zh.md` | 187 | 已充实 |

**草案文档统计**：5 个 <100 行 + 16 个 100-200 行 = **21 个草案文件**（v1.0 为 ~15 个，**新增 6 个**）。

**新增充实**：`70-toolkit/01-protocol-guide.md`（1220 行）和 `02-protocol-quickstart.md`（322 行）为 v2.1 新增充实文档。

### 4.3 文档内容深度评分

**文档深度评分：76/B**（v1.0: 75/B，上升 1 分——主要得益于 70-toolkit 新增 2 个充实文档，但被新增 6 个草案文件部分抵消）

---

## 5. 技术准确性检查

### 5.1 技术准确性验证矩阵

| 检查项 | v2.1 结果 | 证据 |
|--------|----------|------|
| MicroCoreRT 定位为用户态 Ring 3 | ✓ 正确 | `04-microcorert.md:183` "运行在用户态（Ring 3），依赖宿主操作系统"；`TERMINOLOGY.md:322` "不运行在 ring 0，不管理硬件"；`README.md:16` "用户态 AI Agent 运行时，定位为**微核心**（micro-core）" |
| IPC magic 0x41524531 ('ARE1') | ✓ 正确 | `06-iron9-shared-model.md:113`；`02-l2-service-protocol.md:60`；`05-syscall.md:285` |
| 任务 magic 0x41475453 ('AGTS') | ✓ 正确 | `06-iron9-shared-model.md:153`；`05-syscall.md:285` |
| 12 Daemons 完整清单 | ✓ 正确 | `01-daemon.md` V8.0 完整列出 12 个：gateway_d / llm_d / tool_d / market_d / sched_d / monit_d / channel_d / observe_d / notify_d / info_d / hook_d / plugin_d；`TERMINOLOGY.md:553-568` 附录 A 同步；`04-mainpage.dox:56-67` 同步 |
| Cupolas 7 子系统 | ✓ 正确 | `TERMINOLOGY.md:193` 明确：Guards / Permission / Sanitizer / Audit / Workbench / Security Vault / Network Security 七个子系统 |
| IRON-9 v2 三层模型落地 | △ 部分 | `06-iron9-shared-model.md` 描述 [SC]/[SS]/[IND] 三层（行 49-104），但 [SC] 头文件清单与 SSoT 完全错位（见第 1.3 节） |
| 错误码统一 | ✗ 严重失败 | 4+ 套方案并行（详见第 1.1 节） |
| "操作系统"定位 | ✗ 冲突 | 51 处匹配，9 处明确误称"操作系统"（详见第 1.2 节） |
| IPC 头结构体命名 | ✗ 违规 | 2 文件违规（详见第 1.8 节） |
| MemoryRovol 层级命名 | ✗ 冲突 | `02-c-language-boundary.md:72` 与标准完全不同（详见第 1.6 节） |
| Daemon 数量标注 | ✗ 冲突 | `01-system-architecture.md` 标"10 个" 与实际 12 个冲突（详见第 1.5 节） |

### 5.2 上下游关系评估

| 文档 | 上游依赖 | 下游消费者 | v2.1 评估 |
|------|---------|-----------|----------|
| `06-iron9-shared-model.md` | `120-cross-project-code-sharing.md`（SSoT） | 所有 IPC/sched/syscall 文档 | ✗ **[SC] 头文件清单完全错位** |
| `TERMINOLOGY.md` | 无 | 全部文档引用 | ✗ 路径头错误 + 路径引用错误（`00-basic-theories/`） |
| `01-daemon.md` | `TERMINOLOGY.md` v3.0 裁决 #4 | 系统架构文档 | ✓ 正确引用 TERMINOLOGY V8.0 |
| `06-ipc/README.md` | `06-iron9-shared-model.md` + `120-cross-project-code-sharing.md` | 应用开发文档 | ✗ **IPC 头三重违规** |
| `02-l2-service-protocol.md` | 同上 | L2 标准消费者 | ✗ **IPC 头三重违规**（v2.1 新发现） |
| `03-l3-security-governance.md` | `commons/utils/error/include/error.h` | L3 标准消费者 | ✗ **错误码与 06-iron9-shared-model.md 冲突** |

### 5.3 抄袭风险评估

| 检查项 | v2.1 结果 | 证据 |
|--------|----------|------|
| seL4 借鉴 | ✓ 规范 | `04-microcorert.md:61,70,148,151,649,661,669,687,697` 多处注明"借鉴 seL4 的形式化验证思想"；行 669 明确"seL4 运行于 Ring 0，是真正的操作系统微内核"区分清晰 |
| Linux 6.6 基线 | ✓ 规范 | `06-iron9-shared-model.md:197,206` 引用具体源码路径 `include/linux/lsm_hook_defs.h`；`120-cross-project-code-sharing.md:31-39` 引用 `include/uapi/linux/sched.h:121`、`arch/x86/Makefile:137-138`、`scripts/checkpatch.pl:836-851` |
| OLK-6.6 引用 | ✓ 规范 | `06-iron9-shared-model.md:206` 注明 `OLK-6.6 include/linux/lsm_hook_defs.h` |
| openEuler 标准 | ✓ 规范 | `120-cross-project-code-sharing.md:30-31` 通过 OLK-6.6 间接对齐 |
| 原创性 | ✓ 强 | MCIS 体系并行论、五维正交 24 原则、Cupolas 7 子系统、Thinkdual 双思考系统、MemoryRovol 四层记忆卷载均为原创理论框架 |

**抄袭风险评估**：✓ **通过**——所有外部参考均规范注明来源，与 v1.0 评估一致。

### 5.4 工程标准对齐评估

| 检查项 | v2.1 结果 | 证据 |
|--------|----------|------|
| 50-engineering-standards 符号链接 | ✓ | `readlink` = `../AirymaxOS/50-engineering-standards`；`find -L` = 23 文件 |
| SSoT 注册表存在 | ✓ | `09-ssot-registry.md` 为全局规则编号 SSoT |
| 规则编号体系对齐 | ✓ | OS-IRON/KER/STD/BAN/ACC/ABI 编号体系正确引用 |
| 三作用域模型落地 | ✗ | 88 文档与 ~79/85/122 三作用域模型不匹配，未在文档中引用 |
| IRON-9 v2 三层模型 | △ | [SC] 头文件清单错位，[SS]/[IND] 层描述正确 |
| 双向 CI 校验 | △ | `06-iron9-shared-model.md` §5 描述 CI 校验机制，但未文档化实际落地 |

**工程标准对齐评分：78/B**（v1.0: 80/B，下降 2 分——主要因 IPC 头违规蔓延与 [SC] 头文件清单倒退）

---

## 6. 综合评分与改进建议

### 6.1 综合评分矩阵

| 维度 | v1.0 评分 | v2.1 评分 | 变化 | 关键问题 |
|------|----------|----------|------|---------|
| 1. 目录结构完整性 | 70/B- | 68/C+ | -2 | 70-build / 80-testing / 120-development-process 仍缺失；50-specifications/ 仍空置 |
| 2. 文档内容深度 | 75/B | 76/B | +1 | 70-toolkit 新增充实，但草案数量从 15 → 21 |
| 3. 方案冲突 | 45/D+ | 40/D | -5 | 错误码 4+ 套；[SC] 头文件清单倒退；L3 禁令被 06-iron9 违反 |
| 4. 工程标准对齐 | 80/B | 78/B | -2 | 符号链接正确；引用断链未修复；[SC] 错位 |
| 5. 函数前缀和命名 | 72/B- | 70/C+ | -2 | `agentrt_*` 缺失；IPC 头违规从 1 → 2 文件 |
| 6. 跨平台一致性 | 78/B | 75/B- | -3 | "操作系统"自称从 40 → 51 处 |
| 7. 29 仓拆分对齐 | 30/F | 30/F | 0 | 完全未文档化 |
| 8. 草案文档 | 65/C+ | 66/C+ | +1 | 21 个 <200 行文件（v1.0 为 15 个） |
| 9. IPC 协议一致性 | 55/D+ | 50/D | -5 | IPC 头违规从 1 → 2 文件 |
| 10. 技术准确性 | — | 75/B | — | magic / 12 Daemons / Cupolas 7 子系统正确；错误码/[SC]/IPC 头/Daemon 数量错误 |
| 11. 抄袭风险 | — | 90/A | — | seL4 / Linux 6.6 / OLK-6.6 引用规范 |
| **综合** | **62/C+** | **58/C** | **-4** | **5 项 P0 全部未修复，部分加剧** |

### 6.2 P0 改进建议（Critical，阻断 1.0.1 M1）

#### P0-01：统一错误码体系（预计 8h）

**问题**：4+ 套错误码并行（第 1.1 节）

**修复方案**：
1. 确认 SSoT：以 `commons/utils/error/include/error.h` + `03-l3-security-governance.md` §5.2 为权威（AIRY_EINVAL=-1, AIRY_ENOMEM=-2）
2. 修正 `06-iron9-shared-model.md:215-216` 将 `AIRY_EINVAL (-22)` / `AIRY_ENOMEM (-12)` 改为 `-1` / `-2`
3. 修正 `00-architectural-principles.md:924-925` 将 `AIRY_EINVAL = EINVAL` / `AIRY_ENOMEM = ENOMEM` 改为 `-1` / `-2`
4. 修正 `05-syscall.md:644-645` 将 `AIRY_EINVAL = 1001` / `AIRY_ENOMEM = 1002` 改为 `-1` / `-2`
5. 修正 `06-glossary-index.md:175` 将 `AIRY_OK` 改为 `AIRY_EOK`
6. 修正 `06-glossary-index.md:180` 将 `AIRY_ETIMEDOUT` 改为 `AIRY_ETIMEOUT`
7. 明确 `AIRY_*`（内部 + [SC]）与 `ARE_*`（标准 ABI）的映射关系，禁止 `ARE_*` 在 IPC 头等 [SC] 共享结构中使用
8. 在 `01-l1-runtime-interface.md` 中说明 `ARE_OK` / `ARE_EINVAL` 等 ARE_* 错误码是 AIRY_* 的别名（如 `#define ARE_OK AIRY_EOK`）

**影响文件**：8 个

#### P0-02：消除"操作系统"定位冲突（预计 4h）

**问题**：51 处匹配"操作系统"，9 处明确误称（第 1.2 节）

**修复方案**：
1. 全量替换 9 处明确误称"操作系统"为"运行时平台"或"运行时"
2. 修正 `04-mainpage.dox:2` "多体控制论智能操作系统" → "多体控制论智能运行时"
3. 修正 `04-mainpage.dox:6` "构建的智能体操作系统" → "构建的智能体运行时"
4. 修正 `00-architectural-principles.md:54` "驱动多智能体协作的操作系统" → "驱动多智能体协作的运行时平台"
5. 修正 `04-microcorert.md:19, 271` "智能体操作系统" → "智能体运行时"
6. 修正 `01-design-philosophy.md:110, 117, 119` 中"操作系统"相关表述
7. 修正 `05-logging-format.md:73` "分布式多智能体操作系统" → "分布式多智能体运行时"
8. 修正 `10-algorithms/README.md:179` "先进的智能体操作系统" → "先进的智能体运行时"
9. 保留指代 AirymaxOS（agentrt-linux）的"操作系统"引用（README.md:105、README_zh.md:179、06-iron9-shared-model.md:34）

**影响文件**：9 个

#### P0-03：修正 [SC] 头文件清单（预计 1h）

**问题**：[SC] 头文件清单完全错位，syscalls.h 缺失（第 1.3 节）

**修复方案**：
1. 重写 `06-iron9-shared-model.md` 第 2.1 节 [SC] 头文件表，对齐 SSoT（`120-cross-project-code-sharing.md:65-76`）：

| # | 头文件 | 物理路径 | 共享内容 |
|---|--------|---------|---------|
| 1 | `memory_types.h` | `include/airymax/memory_types.h` | MemoryRovol L1-L4 + GFP 掩码 + PMEM |
| 2 | `security_types.h` | `include/airymax/security_types.h` | POSIX capability + LSM 钩子 + Cupolas blob |
| 3 | `cognition_types.h` | `include/airymax/cognition_types.h` | CoreLoopThree + Thinkdual + airy_err_t |
| 4 | `sched.h` | `include/airymax/sched.h` | SCHED_EXT + 任务描述符 + vtime |
| 5 | `ipc.h` | `include/airymax/ipc.h` | IPC magic + 128B 消息头 + SQE/CQE |
| 6 | `syscalls.h` | `include/airymax/syscalls.h` | Syscall 编号体系 24 槽位 |

2. 将 `bpf_struct_ops.h` 移至"补充共享文件"小节（§2.2）
3. 删除 §3.11 BPF struct_ops 小节中"6 个 [SC] 核心头文件"的暗示

**影响文件**：`10-architecture/06-iron9-shared-model.md`

#### P0-04：修正 IPC 消息头结构体三重违规（预计 4h）

**问题**：IPC 头违规从 1 文件蔓延至 2 文件（第 1.8 节）

**修复方案**：
1. 重写 `30-interfaces/06-ipc/README.md` 第 2.1 节，对齐 SSoT `airy_ipc_msg_hdr`
2. 重写 `30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md` 第 2.1 节，对齐 SSoT
3. 结构体名：`are_ipc_message_header_t` → `airy_ipc_msg_hdr`
4. 类型：`uint32_t` → `__u32`，`uint16_t` → `__u16`，`uint64_t` → `__u64`
5. 对齐：添加 `__attribute__((packed))`
6. 字段布局：对齐 SSoT 8 字段（magic / opcode / flags / trace_id / timestamp_ns / src_task / dst_task / payload_len / reserved[84]）
7. 添加 `_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128)`
8. 引用 `#include <airymax/uapi_compat.h>` 获取 UAPI 类型
9. magic 宏名：`ARE_IPC_MAGIC` → `AIRY_IPC_MAGIC`

**影响文件**：2 个

#### P0-05：修正文件路径引用错误（预计 4h）

**问题**：19+ 处路径引用错误（第 1.7 节）

**修复方案**：
1. `00-basic-theories/` → `00-requirements/`（19 处全量替换）
2. 删除 `README.md:62` / `README_zh.md:87` 对 `08-compliance-checklist.md` 的引用（文件不存在）
3. 删除 `06-glossary-index.md:183, 185` 对 `error_code_reference.md` 的引用（文件不存在），改为引用 `50-project-erp/project_erp.md` 或 `04-syscall-api-contract.md` 第 7 章
4. 删除 `04-syscall-api-contract.md:1293` 对 `../70-project-erp/02-error-code-reference.md` 的引用
5. `C_coding_style_standard.md` → `C_Cpp_coding_style.md`（4 处：24-create-agent.md:704 / 25-create-skill.md:658 / 15-testing-standards.md:477 / 10-migration-guide.md:418 / 06-iron9-shared-model.md:331）
6. 删除 `00-architectural-principles.md:1524` 对 `C_Cpp_secure_coding_standard.md` 的引用（不存在）
7. `Rust_coding_style_standard.md` → `Rust_coding_style.md`（`06-iron9-shared-model.md:333`）
8. 删除 `06-glossary-index.md:124, 164, 165` 对 `../30-coding-standard/` 的引用（路径完全不存在）
9. `TERMINOLOGY.md:8` 路径头 `Docs/TERMINOLOGY.md` → `docs/AirymaxRT/TERMINOLOGY.md`
10. `50-specifications/10-contracts/06-glossary-index.md:8` 路径头 `OpenAirymax/Docs/...` → `docs/AirymaxRT/...`

**影响文件**：~12 个

### 6.3 P1 改进建议（Major，1.0.1 M1 内完成）

#### P1-01：统一 Cupola/Cupolas 术语（预计 2h）

**修复**：全量替换 `Cupola`（单数）为 `Cupolas`（复数），除明确指代单一子系统的上下文。

**影响文件**：5 个（含新增的 `03-overall-architecture.drawio`）

#### P1-02：修正 daemon 数量标注（预计 0.5h）

**修复**：`01-system-architecture.md` 行 305 / 309 的"10" → "12"，ASCII 图标题同步。

**影响文件**：`10-architecture/01-system-architecture.md`

#### P1-03：文档化 29 仓拆分结构（预计 6h）

**修复**：
1. 新建 `10-architecture/07-repository-structure.md`，描述 agentrt 在 29 仓拆分中的位置
2. 明确 agentrt 作为管理仓的子仓清单（atoms / coreloopthree / memoryrovol / daemon / sdk-go / sdk-python / sdk-rust / sdk-typescript 等）
3. 描述 submodule 管理方式
4. 引用 SSoT OS-IRON-013

#### P1-04：文档化 `agentrt_*` 专属 API 前缀（预计 2h）

**修复**：
1. 在 `06-iron9-shared-model.md` 或新建命名规范文档中，定义三层前缀分层：
   - `airy_*` — [SC] 共享契约层 + 微核心原语（atoms 层）
   - `are_*` — ARE 标准 ABI（L1/L2/L3 公开接口，第三方可实现）
   - `agentrt_*` — agentrt 专属 API（daemon 管理、配置、运行时控制）
2. 在 `TERMINOLOGY.md` 中添加前缀分层说明

#### P1-05：修正 MemoryRovol 层级命名（预计 1h）

**修复**：
1. `02-c-language-boundary.md:72` "Working → Short-term → Long-term → Archival" → "L1 Raw → L2 Feature → L3 Structure → L4 Pattern"
2. `02-logging.md` 日志 L1-L4 改为 LOG_DEBUG/INFO/WARN/ERROR 或其他非冲突命名

#### P1-06：处理 50-specifications/ 目录（预计 1h）

**修复**：删除 `50-specifications/` 目录及其重复的 `06-glossary-index.md`，保留 `20-modules/10-contracts/06-glossary-index.md` 作为唯一术语索引。

#### P1-07：充实 5 个 <100 行草案文档（预计 10h）

**优先充实**：
1. `05-runtime-interfaces/README.md`（49 行）→ L1/L2/L3 总览
2. `06-ipc/README.md`（69 行）→ 重写对齐 SSoT（P0-04 已覆盖）
3. `08-service-discovery/README.md`（76 行）→ 服务发现机制
4. `01-sdk/README.md`（80 行）→ SDK 概述或删除冗余目录
5. `07-rpc-api/README.md`（90 行）→ RPC API 规范

#### P1-08：对齐中英文 README（预计 2h）

**修复**：英文 `README.md`（112 行）补全至与中文 `README_zh.md`（187 行）对等，包括：
- 子目录详细列表
- 文档质量标准段
- 完整的 140-application-development 子文件列表（24 个）

### 6.4 P2 改进建议（Minor，1.0.1 内完成）

#### P2-01：修正 06-iron9-shared-model.md 递归注释（预计 0.1h）

**修复**：行 214 `/* 成功（替代 AIRY_EOK） */` → `/* 成功 */`

#### P2-02：充实 00-requirements/ 中英双语文档（预计 8h）

**修复**：8 个文件均为 <170 行，需充实理论内容至 ≥250 行。

#### P2-03：充实 60-syscalls/ 系统调用文档（预计 6h）

**修复**：6 个文件均为 <185 行，需补充参数说明、返回值、错误码、示例代码。

#### P2-04：建立 AirymaxRT 文档计数模型（预计 1h）

**修复**：在 `README.md` 或 `09-ssot-registry.md` 中建立 AirymaxRT 文档计数模型（当前 88 文档），明确与三作用域模型（~79/85/122）的关系。

### 6.5 改进建议汇总

| 优先级 | 数量 | 预计工时 | 阻断 1.0.1 M1 | v1.0 工时对比 |
|--------|------|---------|--------------|--------------|
| P0 | 5 项 | ~21h | ✓ 阻断 | v1.0: 19h（增加 2h，因 IPC 违规蔓延至 2 文件） |
| P1 | 8 项 | ~24h | △ 建议在 M1 内完成 | v1.0: 23h |
| P2 | 4 项 | ~15h | ✗ 不阻断 | v1.0: 19h |
| **合计** | **17 项** | **~60h** | — | v1.0: 61h |

---

## 附录 A：审查文件清单

### A.1 已完整阅读文件

| 文件 | 行数 | 审查深度 |
|------|------|---------|
| `10-architecture/06-iron9-shared-model.md` | 346 | 完整 |
| `10-architecture/01-system-architecture.md` | 594 | 完整 |
| `10-architecture/30-kernel/02-c-language-boundary.md` | 100+ | 部分（前 100 行） |
| `10-architecture/50-services/01-daemon.md` | 141 | 完整 |
| `10-architecture/50-services/02-logging.md` | 60+ | 部分（前 60 行） |
| `TERMINOLOGY.md` | 612 | 完整 |
| `README.md` | 112 | 完整 |
| `README_zh.md` | 187 | 完整 |
| `30-interfaces/04-mainpage.dox` | 149 | 完整 |
| `30-interfaces/06-ipc/README.md` | 69 | 完整 |
| `30-interfaces/05-runtime-interfaces/03-l3-security-governance.md` | 130+ | 部分（§5 错误码段） |
| `30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md` | 130+ | 部分（§2 IPC 头段） |
| `50-specifications/10-contracts/06-glossary-index.md` | 229 | 完整（重复） |
| `50-engineering-standards/120-cross-project-code-sharing.md` | 200+ | 部分（前 200 行） |
| `10-architecture/60-diagrams/03-overall-architecture.drawio` | 204+ | 部分（Cupola 段） |

### A.2 Grep / Shell 验证命令

```bash
# 文档总数
find docs/AirymaxRT -type f -name "*.md" | wc -l  # = 88

# 符号链接验证
readlink 50-engineering-standards  # = ../AirymaxOS/50-engineering-standards
find -L 50-engineering-standards -type f -name "*.md" | wc -l  # = 23

# 错误码方案搜索
grep -rn "AIRY_E\|ARE_OK\|ARE_E" --include="*.md" docs/AirymaxRT/  # 仍返回 4+ 套

# "操作系统"冲突搜索
grep -rn "操作系统" --include="*.md" --include="*.dox" docs/AirymaxRT/  # = 51 行匹配，18 文件

# 前缀检查
grep -rn "agentrt_" docs/AirymaxRT/  # = 0（缺失）
grep -rn "agentos_" docs/AirymaxRT/  # = 0（清理彻底）
grep -rn "airymaxos_" docs/AirymaxRT/  # = 2（均为禁止声明）

# 29 仓搜索
grep -rn "29 仓\|29 repo\|伞仓\|管理仓\|叶子仓\|顶层仓" docs/AirymaxRT/  # = 0（完全缺失）

# Cupola vs Cupolas
grep -rl "Cupola[^s]" --include="*.md" --include="*.drawio" docs/AirymaxRT/  # = 5 文件
grep -rl "Cupolas" --include="*.md" --include="*.drawio" docs/AirymaxRT/  # = 19 文件

# 路径引用错误
grep -rn "00-basic-theories" --include="*.md" docs/AirymaxRT/  # = 19 行匹配
grep -rn "08-compliance-checklist\|error_code_reference\|C_coding_style_standard\|C_Cpp_secure_coding_standard\|Rust_coding_style_standard\|log_standard" --include="*.md" docs/AirymaxRT/  # = 20 行匹配

# IPC 头违规
grep -rn "are_ipc_message_header" --include="*.md" docs/AirymaxRT/  # = 7 行（2 文件）
grep -rn "ARE_IPC_MAGIC" --include="*.md" docs/AirymaxRT/  # = 1 文件（违规）

# 递归注释
grep -n "替代 AIRY_EOK" docs/AirymaxRT/10-architecture/06-iron9-shared-model.md  # = 行 214

# 草案文档（<200 行）
find docs/AirymaxRT -type f -name "*.md" -exec wc -l {} \; | sort -n | head -22  # 21 个草案
```

---

## 附录 B：与前序审查报告的关系

| 报告 | 范围 | 关系 |
|------|------|------|
| `01-atoms-source-deep-review.md` | agentrt atoms 模块源代码 | 源码级审查，本文档为方案级审查，互补 |
| `02-daemons-others-source-deep-review.md` | daemon 及其他模块源代码 | 源码级审查，本文档为方案级审查，互补 |
| `03-airymaxrt-solution-review.md`（v1.0） | AirymaxRT 全量文档方案 | v1.0 方案级审查，本文档（v2.1）为其复审 |
| **`02-airymaxrt-solution-review-v2.1.md`（本文档）** | AirymaxRT 全量文档方案 v2.1 复审 | 验证 v1.0 修复进展 + 发现新问题 |

---

## 附录 C：v1.0 → v2.1 修复进展总结

| v1.0 问题 | v2.1 状态 | 修复进展评级 |
|----------|----------|------------|
| P0-1 错误码 6 套并行 | 仍 4+ 套并行 | ✗ 未修复 |
| P0-2 "操作系统"定位 | 51 处匹配（v1.0 为 40） | ✗ 加剧 |
| P0-3 [SC] 头文件清单 | bpf_struct_ops.h 升至第 1 位，syscalls.h 完全缺失 | ✗ 倒退 |
| P0-4 Cupola/Cupolas | 5 文件用单数（v1.0 为 4） | ✗ 加剧 |
| P0-5 Daemon 数量 | 仍标"10" | ✗ 未修复 |
| P1-1 Cupola 统一 | 同 P0-4 | ✗ 未修复 |
| P1-2 Daemon 数量 | 同 P0-5 | ✗ 未修复 |
| P1-3 29 仓拆分 | 0 处提及 | ✗ 未修复 |
| P1-4 `agentrt_*` 前缀 | 0 处使用 | ✗ 未修复 |
| P1-5 MemoryRovol 层级 | 仍为 Working/Short-term/... | ✗ 未修复 |
| P1-6 50-specifications/ | 仍 1 文件，重复 | ✗ 未修复 |
| P1-7 草案充实 | 5 个 <100 行未充实 | △ 部分修复（70-toolkit 新增 2 充实文件） |
| P1-8 中英 README 对齐 | 英 112 vs 中 187 | ✗ 未修复 |
| P2-1 递归注释 | 行 214 仍存在 | ✗ 未修复 |
| P2-2 TERMINOLOGY 路径头 | 行 8 仍为 `Docs/TERMINOLOGY.md` | ✗ 未修复 |
| P2-3 00-requirements 充实 | 8 文件仍 <170 行 | ✗ 未修复 |
| P2-4 60-syscalls 充实 | 6 文件仍 <185 行 | ✗ 未修复 |
| P2-5 文档计数模型 | 未建立 | ✗ 未修复 |
| P2-6 70-build / 80-testing / 120-process | 未创建 | ✗ 未修复 |

**修复进展汇总**：19 项问题中，**0 项完全修复**，1 项部分修复（P1-7），18 项未修复（含 2 项加剧 + 1 项倒退）。

---

**审查结论**：AirymaxRT 文档体系在 v2.1 中**没有实质性修复 v1.0 提出的任何 P0-CRITICAL 问题**，且 [SC] 头文件清单问题甚至倒退（从"第 6 位错列"恶化为"第 1 位错列 + syscalls.h 完全缺失"）。同时 IPC 头违规从 1 文件蔓延至 2 文件，"操作系统"自称从 40 → 51 处增加，Cupola 单数使用从 4 → 5 文件增加。

**架构设计层面**（MicroCoreRT / CoreLoopThree / MemoryRovol / Cupolas 7 子系统 / 12 Daemons V8.0 / MCIS 体系并行论 / 五维正交 24 原则 / Thinkdual 双思考 / TimeSliceInfer 分时推理）仍保持高质量，理论根基完整，原创性强。**工程一致性层面**存在 5 项 P0 级系统性问题，且修复进展为零甚至倒退。

**强烈建议**：在进入 1.0.1 M1 代码开发前，**必须**优先完成全部 5 项 P0 修复（~21h），并按 P1 → P2 顺序推进。否则代码将基于错误码冲突 / [SC] 错位 / IPC 头违规的文档基础开发，导致后期返工成本指数级增长。

**修复路径**：P0（~21h）→ 进入 1.0.1 M1 → P1（~24h）M1 内完成 → P2（~15h）1.0.1 内完成。

**评分变化关键洞察**：
- 综合评分从 62/C+ 降至 58/C，下降 4 分
- 主要下降维度：方案冲突（-5）、IPC 协议一致性（-5）、跨平台一致性（-3）
- 主要上升维度：文档内容深度（+1）、草案文档（+1）
- 净变化：-4 分，等级从 C+ 降至 C

---

<div align="center">

**© 2025-2026 SPHARX Ltd.** All Rights Reserved.

</div>
