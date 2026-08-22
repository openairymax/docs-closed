Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# AirymaxRT（agentrt）整体方案系统性深度审查报告 v1.0

> **审查范围**：`/home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxRT/` 全量文档（88 个 .md 文件）
> **审查基线**：AirymaxOS 文档体系（123 个 .md 文件）+ IRON-9 v2 三层共享模型 + SSoT 注册表（09-ssot-registry.md）+ 120-cross-project-code-sharing.md
> **审查日期**：2026-07-13
> **审查者**：Airymax 架构审查专家（agentrt 子代理）
> **审查维度**：目录结构 / 文档深度 / 方案冲突 / 工程标准对齐 / 命名前缀 / 跨平台 / 29 仓拆分 / 草案清单 / IPC 一致性 / 改进建议

---

## 0. 执行摘要

| 维度 | 评分 | 状态 |
|------|------|------|
| 目录结构完整性 | 70/B- | 基本合理，50-specifications/ 近乎空置，缺少 60+ 高层目录 |
| 文档内容深度 | 75/B | 核心架构文档质量高，但草案文件偏多（~15 个 <200 行） |
| 方案冲突 | 45/D+ | **严重**：6 套错误码、"操作系统"定位冲突、[SC] 头文件清单不一致 |
| 工程标准对齐 | 80/B | 符号链接正确，SSoT 引用规范，但三作用域模型未落地 |
| 命名前缀 | 72/B- | `airy_*`/`are_*` 分层合理，但 `agentrt_*` 专属前缀缺失，IPC 头命名违规 |
| 跨平台一致性 | 78/B | 用户态定位正确，但多处文档误称"操作系统" |
| 29 仓拆分对齐 | 30/F | **完全缺失**：agentrt 仓库结构未文档化 |
| 草案文档 | 65/C+ | ~15 个 <200 行文件需充实 |
| IPC 协议一致性 | 55/D+ | magic 值正确，但 IPC 头结构体命名/类型/布局三重违规 |
| **综合** | **62/C+** | 核心设计扎实，但存在系统性一致性问题，需 P0 修复后方可进入 1.0.1 M1 |

**核心结论**：AirymaxRT 文档体系在**架构设计层面**（MicroCoreRT / CoreLoopThree / MemoryRovol / Thinkdual / Cupolas / 12 Daemons）质量较高，理论根基（MCIS 体系并行论 + 五维正交 24 原则）完整。但在**工程一致性层面**存在系统性问题：(1) 错误码 6 套并行、(2) "操作系统"定位与用户态运行时矛盾、(3) [SC] 共享契约层头文件清单与 SSoT 不一致、(4) IPC 消息头结构体命名/类型/布局三重违规、(5) 29 仓拆分完全未文档化。建议优先修复 5 项 P0 问题后进入 1.0.1 M1 代码开发。

---

## 1. 目录结构完整性评估（对比 AirymaxOS）

### 1.1 总体统计

| 项目 | .md 文件数 | 顶层目录数 | 说明 |
|------|-----------|-----------|------|
| AirymaxRT | 88 | 7 | 含 3 个根级文件 |
| AirymaxOS | 123 | 12 | 对比基准 |

> **证据**：`find /home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxRT -type f -name "*.md" | wc -l` = 88；`find .../AirymaxOS ...` = 123

### 1.2 顶层目录分布

| 目录 | 文件数 | 评估 |
|------|--------|------|
| `00-requirements/` | 8 | 充实（MCIS / 认知 / 记忆 / 设计原则，中英双语） |
| `10-architecture/` | 14 | 充实（架构原则 / 系统架构 / CoreLoopThree / MemoryRovol / MicroCoreRT / Syscall / IRON-9 / 哲学 / 工程 / 服务 / 内核边界） |
| `20-modules/` | 6 | **偏少**（仅 contracts/ 子目录，6 个契约文件） |
| `30-interfaces/` | 29 | 充实（API / CLI / Doxygen / 运行时接口 L1-L3 / IPC / RPC / 服务发现 / 算法 / Core / Daemon / Docker / Syscalls / Toolkit） |
| `50-engineering-standards/` | 23 | **符号链接** → `../AirymaxOS/50-engineering-standards`（共享，正确） |
| `50-specifications/` | 1 | **近乎空置**（仅 1 个 glossary-index.md，且与 20-modules/ 版本近乎重复） |
| `140-application-development/` | 27 | 充实（快速上手 / 构建 / 部署 / 配置 / 监控 / 迁移 / 安全 / 测试 / CI/CD / 插件 / 协议 / Agent / Skill / DAG 集成等） |

> **证据**：`for d in */; do echo "$d: $(find "$d" -type f -name '*.md' | wc -l)"; done`

### 1.3 符号链接验证

```
50-engineering-standards -> ../AirymaxOS/50-engineering-standards
```

> **证据**：`readlink 50-engineering-standards` = `../AirymaxOS/50-engineering-standards` ✓

**评估**：符号链接正确，工程标准 23 文档与 AirymaxOS 共享，符合 IRON-9 v2 同源原则。

### 1.4 与 AirymaxOS 目录结构差异

AirymaxOS 拥有而 AirymaxRT 缺失的顶层目录：

| AirymaxOS 目录 | AirymaxRT 对应 | 说明 |
|----------------|---------------|------|
| `60-driver-model/` | 无 | agentrt 无内核驱动模型（用户态，合理缺失） |
| `70-build/` | 无 | 构建系统文档缺失（KBuild 为 OS 专属，但 agentrt 应有 CMake 构建文档） |
| `80-testing/` | `10-architecture/20-engineering/01-testing.md` | agentrt 有测试架构文档但未独立成目录 |
| `90-observability/` | 无独立目录 | 可观测性散落在各文档中 |
| `110-security/` | 无独立目录 | 安全设计散落在 Cupolas 相关文档中 |
| `120-development-process/` | 无 | 开发流程文档缺失 |

**评估**：部分缺失合理（60-driver-model 为内核专属），但 70-build（CMake 构建）、80-testing（测试框架）、120-development-process（开发流程）应为 agentrt 独立文档化。

### 1.5 命名规范

- **NN-name 模式**：`00-requirements`、`10-architecture`、`20-modules`、`30-interfaces`、`50-engineering-standards`、`50-specifications`、`140-application-development` ✓
- **kebab-case**：子目录和文件名均遵循 kebab-case（如 `01-getting-started.md`、`06-iron9-shared-model.md`）✓
- **异常**：`140-application-development/01-sdk/README.md` 中 `01-sdk` 为目录但仅有 1 个 README，结构冗余

### 1.6 目录结构评级

| 检查项 | 结果 |
|--------|------|
| 符号链接正确 | ✓ 通过 |
| NN-name 命名 | ✓ 通过 |
| kebab-case 命名 | ✓ 通过 |
| 50-specifications/ 充实 | ✗ 失败（仅 1 文件） |
| 60+ 高层目录覆盖 | ✗ 部分缺失（build/testing/process） |
| 与 AirymaxOS 结构对齐 | △ 部分（合理缺失 + 不合理缺失并存） |

**目录结构完整性评分：70/B-**

---

## 2. 文档内容深度评估（逐文档）

### 2.1 高质量文档（≥500 行，设计完整）

| 文件 | 行数 | 评估 |
|------|------|------|
| `10-architecture/00-architectural-principles.md` | 1530 | 24 原则五维正交体系完整，但存在路径引用错误和"操作系统"定位冲突 |
| `30-interfaces/02-api-reference.md` | 2682 | Gateway API 完整参考，JSON-RPC 2.0 + REST + 协议适配器 |
| `10-architecture/03-memoryrovol.md` | 981 | 四层记忆系统设计完整 |
| `10-architecture/02-coreloopthree.md` | 986 | 三阶段认知循环架构完整 |
| `20-modules/10-contracts/05-logging-format.md` | 983 | 结构化日志格式规范完整 |
| `10-architecture/04-microcorert.md` | 806 | 微核心 vs 微内核论证清晰，正确区分 Ring 3 用户态 |
| `10-architecture/50-services/02-logging.md` | 765 | 日志系统设计完整 |
| `20-modules/10-contracts/04-syscall-api-contract.md` | 1388 | 系统调用 API 契约完整 |
| `30-interfaces/01-doxygen-guide.md` | 337 | Doxygen 文档生成指南 |
| `10-architecture/06-iron9-shared-model.md` | 346 | IRON-9 v2 三层模型，但 [SC] 头文件清单与 SSoT 冲突 |

> **证据**：`find . -type f -name "*.md" -exec wc -l {} \; | sort -rn | head -20`

### 2.2 中等质量文档（200-500 行）

| 文件 | 行数 | 评估 |
|------|------|------|
| `10-architecture/40-philosophy/01-design-philosophy.md` | 253 | 设计哲学完整，但多处误称"操作系统" |
| `10-architecture/20-engineering/02-toolkit.md` | 248 | 工具链概述 |
| `10-architecture/20-engineering/01-testing.md` | 224 | 双层测试架构 |
| `TERMINOLOGY.md` | 612 | 术语表完整，12 daemon 清单正确，但路径引用错误 |
| `10-architecture/01-system-architecture.md` | 594 | 系统架构概述，但 daemon 数量标注"10"与实际"12"冲突 |
| `10-architecture/05-syscall.md` | 942 | 系统调用设计，但错误码方案独立（正值 1001+） |
| `20-modules/10-contracts/03-protocol-contract.md` | 894 | 协议契约完整 |
| `20-modules/10-contracts/01-agent-contract.md` | 840 | Agent 契约完整 |

### 2.3 草案 / 过短文档（<200 行）

详见第 8 节"草案文档清单"。

### 2.4 技术准确性评估

| 检查项 | 结果 | 证据 |
|--------|------|------|
| MicroCoreRT 定位为用户态 Ring 3 | ✓ 正确 | `10-architecture/04-microcorert.md:183` "MicroCoreRT 运行在用户态（Ring 3）" |
| IPC magic 0x41524531 ('ARE1') | ✓ 正确 | `10-architecture/06-iron9-shared-model.md:113` |
| 任务 magic 0x41475453 ('AGTS') | ✓ 正确 | `10-architecture/06-iron9-shared-model.md:153` |
| 12 Daemons 完整清单 | ✓ 正确 | `10-architecture/50-services/01-daemon.md` V8.0 版本 |
| Cupolas 7 子系统 | ✓ 正确 | `TERMINOLOGY.md` 附录 A |
| 错误码统一 | ✗ 严重失败 | 6 套不同方案（详见第 3 节） |
| "操作系统"定位 | ✗ 冲突 | 15+ 处误称"操作系统"（详见第 3 节） |

### 2.5 上下游关系评估

| 文档 | 上游依赖 | 下游消费者 | 评估 |
|------|---------|-----------|------|
| `06-iron9-shared-model.md` | `120-cross-project-code-sharing.md`（SSoT） | 所有 IPC/sched/syscall 文档 | **[SC] 头文件清单与 SSoT 冲突** |
| `TERMINOLOGY.md` | 无 | 全部文档引用 | 路径引用错误（`00-basic-theories/` 不存在） |
| `01-daemon.md` | `TERMINOLOGY.md` | 系统架构文档 | 正确引用 TERMINOLOGY v3.0 裁决 #4 |
| `06-ipc/README.md` | `06-iron9-shared-model.md` + `120-cross-project-code-sharing.md` | 应用开发文档 | **IPC 头结构体命名违规** |

### 2.6 抄袭风险评估

| 检查项 | 结果 |
|--------|------|
| seL4 借鉴 | ✓ 仅限架构层（IRON-012 约束），注明参考来源 |
| Linux 6.6 基线 | ✓ 引用具体源码路径（`include/uapi/linux/sched.h:121` 等） |
| openEuler 标准 | ✓ 规范声明层对齐 |
| 原创性 | ✓ MCIS 体系并行论、五维正交 24 原则为原创理论框架 |

**文档深度评分：75/B**

---

## 3. 方案冲突清单

### 3.1 [P0-CRITICAL] 错误码 6 套并行——系统性 SSoT 崩溃

**问题描述**：AirymaxRT 文档中存在 **6 套不同的错误码定义方案**，严重违反 SSoT 原则。

| 方案 | 文件 | 行号 | 成功码 | AIRY_EINVAL | AIRY_ENOMEM | 类型 |
|------|------|------|--------|-------------|-------------|------|
| A | `10-architecture/00-architectural-principles.md` | 922-940 | — | `= EINVAL` | `= ENOMEM` | POSIX errno 直接赋值 |
| B | `10-architecture/06-iron9-shared-model.md` | — | `AIRY_EOK` | `-22` | `-12` | POSIX 对齐负值 |
| C | `10-architecture/05-syscall.md` | 641-646 | `AIRY_EOK=0` | `1001` | `1002` | 正值序列 |
| D | `20-modules/10-contracts/04-syscall-api-contract.md` | 99-108 | — | `-1` | `-2` | 负值序列 |
| E | `20-modules/10-contracts/06-glossary-index.md` | 173-180 | `AIRY_OK`（非 EOK！） | `-1` | `-2` | 负值 + 命名不一致 |
| F | `30-interfaces/README.md` | 78-86 | `AIRY_EOK=0` | `-1` | `-2` | 负值序列 |
| G | `20-modules/10-contracts/03-protocol-contract.md` | 494-500 | `AIRY_OK=0`（非 EOK！） | `-1` | `-2` | 负值 + 命名不一致 |
| H | `30-interfaces/05-runtime-interfaces/01-l1-runtime-interface.md` | 48+ | `ARE_OK (0)`（非 AIRY_！） | — | — | ARE 标准前缀 |
| SSoT | `50-engineering-standards/120-cross-project-code-sharing.md` | 81 | — | — | — | 13 个 `AIRY_E*` 宏，`airy_err_t` 定义于 `cognition_types.h` |

**冲突点**：
1. 成功码：`AIRY_EOK` vs `AIRY_OK` vs `ARE_OK`（3 种命名）
2. `AIRY_EINVAL`：`EINVAL` / `-22` / `1001` / `-1`（4 种值）
3. `AIRY_ENOMEM`：`ENOMEM` / `-12` / `1002` / `-2`（4 种值）
4. 超时码：`AIRY_ETIMEOUT` vs `AIRY_ETIMEDOUT`（2 种命名）
5. 前缀：`AIRY_*` vs `ARE_*`（2 种前缀，虽 ARE 为标准 ABI 层但未明确分层边界）

> **证据**：`grep -rn "AIRY_E\|ARE_OK\|ARE_E" --include="*.md" docs/AirymaxRT/` 确认 6+ 套方案

**影响**：开发者无法确定应使用哪套错误码，C 代码编译将出现宏重定义冲突，违反 IRON-1（用户空间 ABI 永不破坏）。

### 3.2 [P0-CRITICAL] "操作系统"定位与用户态运行时矛盾

**问题描述**：agentrt 定位为"AI Agent 运行时平台工程"（用户态微核心，Ring 3），但 15+ 处文档误称其为"操作系统"。

| 文件 | 行号 | 文本 | 冲突 |
|------|------|------|------|
| `10-architecture/00-architectural-principles.md` | 54 | "Airymax 是一个**驱动多智能体协作的操作系统**" | ✗ 应为"运行时平台" |
| `10-architecture/40-philosophy/01-design-philosophy.md` | 45 | "Airymax 不是'一个框架'，而是一个'操作系统'" | ✗ |
| `10-architecture/40-philosophy/01-design-philosophy.md` | 110 | "不是'框架'…而是'操作系统'（Operating System）" | ✗ |
| `10-architecture/40-philosophy/01-design-philosophy.md` | 117 | "agentrt — 内部操作系统层" | ✗ 应为"运行时层" |
| `10-architecture/40-philosophy/01-design-philosophy.md` | 119 | "agentrt 是 Airymax 的内部 OS 层" | ✗ |
| `10-architecture/40-philosophy/01-design-philosophy.md` | 38 | "Airymax 的系统观源自操作系统设计的经典智慧" | ✗ 借鉴 ≠ 就是 |
| `10-architecture/04-microcorert.md` | 19 | "为整个智能体操作系统提供可靠…运行时基础" | ✗ |
| `10-architecture/04-microcorert.md` | 271 | "共同构成完整的智能体操作系统架构" | ✗ |
| `10-architecture/05-syscall.md` | 104 | "将操作系统接口理论…系统整合" | ✗ |
| `20-modules/10-contracts/05-logging-format.md` | 73 | "Airymax 作为一个分布式多智能体操作系统" | ✗ |
| `00-requirements/04-design-principles-cn.md` | 99 | "现代操作系统的 MicroCoreRT 微核心思想" | ✗ |
| `30-interfaces/04-mainpage.dox` | 2,6 | "多体控制论智能操作系统" / "智能体操作系统" | ✗ |
| `30-interfaces/10-algorithms/README.md` | 179,182 | "Airymax 是一个先进的智能体操作系统" | ✗ |

**矛盾点**：`10-architecture/04-microcorert.md:183` 明确指出"MicroCoreRT 运行在用户态（Ring 3），依赖宿主操作系统（Linux/macOS/Windows）"——这与上述"操作系统"自称直接矛盾。

> **证据**：`grep -rn "操作系统" --include="*.md" docs/AirymaxRT/` = 40 行匹配

**影响**：技术定位混乱，开源社区误解 agentrt 为 OS 内核项目，与 AirymaxOS（agent-linux）产生定位混淆。

### 3.3 [P0-CRITICAL] [SC] 头文件清单与 SSoT 不一致

**问题描述**：`06-iron9-shared-model.md` 列出的 6 个 [SC] 核心头文件与 SSoT（`120-cross-project-code-sharing.md`）不一致。

| 序号 | `06-iron9-shared-model.md`（agentrt 侧） | `120-cross-project-code-sharing.md`（SSoT） | 一致性 |
|------|------------------------------------------|---------------------------------------------|--------|
| 1 | `memory_types.h` | `memory_types.h` | ✓ |
| 2 | `security_types.h` | `security_types.h` | ✓ |
| 3 | `cognition_types.h` | `cognition_types.h` | ✓ |
| 4 | `sched.h` | `sched.h` | ✓ |
| 5 | `ipc.h` | `ipc.h` | ✓ |
| 6 | **`bpf_struct_ops.h`** | **`syscalls.h`** | ✗ 冲突 |

**SSoT 明确说明**（`120-cross-project-code-sharing.md:85-117`）：`bpf_struct_ops.h` 是**补充共享文件**（非 [SC] 核心头文件），第 6 个核心头文件应为 `syscalls.h`（Syscall 编号体系 24 槽位）。

> **证据**：
> - `06-iron9-shared-model.md` 列出 `bpf_struct_ops.h` 作为第 6 个 [SC] 核心头文件
> - `120-cross-project-code-sharing.md:76` 明确第 6 个为 `syscalls.h`
> - `120-cross-project-code-sharing.md:85` 标题 "2.2 补充共享文件：bpf_struct_ops.h（非 [SC] 核心头文件）"
> - `09-ssot-registry.md` OS-IRON-014 "[SC] 共享契约层 6 头文件单一数据源"

**影响**：违反 IRON-014（[SC] 共享契约层 6 头文件单一数据源），开发者无法确定 `syscalls.h` 是否为 [SC] 头文件。

### 3.4 [P1-MAJOR] Cupola（单数）vs Cupolas（复数）术语不一致

**问题描述**：安全穹顶模块标准名称为 **Cupolas**（7 子系统复数形式），但 4 个文件使用单数 **Cupola**。

| 使用 Cupola（单数，错误） | 使用 Cupolas（复数，正确） |
|--------------------------|--------------------------|
| `10-architecture/01-system-architecture.md` | `10-architecture/06-iron9-shared-model.md` |
| `10-architecture/30-kernel/02-c-language-boundary.md` | `10-architecture/01-system-architecture.md`（混用） |
| `10-architecture/40-philosophy/01-design-philosophy.md` | `10-architecture/04-microcorert.md` |
| `20-modules/10-contracts/05-logging-format.md` | `TERMINOLOGY.md` |
| — | `10-architecture/20-engineering/01-testing.md` |
| — | `140-application-development/` 4 个文件 |

> **证据**：`grep -rl "Cupola[^s]" --include="*.md" .` = 4 文件；`grep -rl "Cupolas" --include="*.md" .` = 10 文件

**影响**：术语不一致，Cupola 暗示单一服务包装器，Cupolas 是 7 子系统安全层，语义不同。

### 3.5 [P1-MAJOR] Daemon 数量标注冲突（10 vs 12）

**问题描述**：`01-system-architecture.md` 标注"10 个核心用户态服务"，但实际 daemon 清单为 12 个。

| 文件 | 行号 | 文本 | 冲突 |
|------|------|------|------|
| `10-architecture/01-system-architecture.md` | 305 | "10 个核心用户态服务" | ✗ 应为 12 |
| `10-architecture/01-system-architecture.md` | 309 | ASCII "Airymax Daemon Services (10)" | ✗ 应为 12 |
| `10-architecture/01-system-architecture.md` | 575 | "Team A (12 daemons)" | ✓ 正确 |
| `10-architecture/50-services/01-daemon.md` | 131 | "V8.0…daemon 清单从 10 个修正为 12 个" | ✓ 正确（已修正） |

> **证据**：`01-daemon.md` V8.0 已修正为 12 个，但 `01-system-architecture.md` 仍保留旧值"10"

### 3.6 [P1-MAJOR] MemoryRovol 层级命名冲突

**问题描述**：MemoryRovol 四层记忆系统标准命名为 L1 Raw → L2 Feature → L3 Structure → L4 Pattern，但部分文档使用不同命名。

| 文件 | 行号 | 命名方案 | 冲突 |
|------|------|---------|------|
| `10-architecture/03-memoryrovol.md` | — | L1 Raw / L2 Feature / L3 Structure / L4 Pattern | ✓ 标准 |
| `50-engineering-standards/120-cross-project-code-sharing.md` | 135-139 | L1 HOT / L2 WARM / L3 COLD / L4 PMEM | ✓ [SC] 语义层 |
| `10-architecture/30-kernel/02-c-language-boundary.md` | 72 | Working → Short-term → Long-term → Archival | ✗ 完全不同 |
| `10-architecture/50-services/02-logging.md` | — | L1-L4（日志层级） | ✗ 与 MemoryRovol L1-L4 冲突 |

### 3.7 [P1-MAJOR] 文件路径引用错误（系统性）

**问题描述**：多个文档引用 `00-basic-theories/` 目录，但实际目录名为 `00-requirements/`。

| 文件 | 行号 | 错误引用 | 正确路径 |
|------|------|---------|---------|
| `TERMINOLOGY.md` | 604-612 | `00-basic-theories/01-mcis-cn.md` 等 | `00-requirements/01-mcis-cn.md` |
| `10-architecture/00-architectural-principles.md` | 1516-1519 | `00-basic-theories/` | `00-requirements/` |
| `20-modules/10-contracts/01-agent-contract.md` | 42,44 | `00-basic-theories/` | `00-requirements/` |
| `20-modules/10-contracts/04-syscall-api-contract.md` | 65 | `../30-coding-standard/10-log-standard.md` | 路径不存在 |
| `20-modules/10-contracts/06-glossary-index.md` | 124-127 | `../30-coding-standard/13-rust-coding-style.md` 等 | 路径不存在 |
| `20-modules/10-contracts/06-glossary-index.md` | 183 | `../../50-engineering-standards/50-project-erp/error_code_reference.md` | 文件不存在 |
| `README.md` | 62 | `50-engineering-standards/08-compliance-checklist.md` | 文件不存在 |
| `README_zh.md` | 87 | `50-engineering-standards/08-compliance-checklist.md` | 文件不存在 |
| `10-architecture/06-iron9-shared-model.md` | 331-334 | `C_coding_style_standard.md` 等 4 个文件 | 实际为 `C_Cpp_coding_style.md` 等 |
| `10-architecture/00-architectural-principles.md` | 1524 | `C_Cpp_secure_coding_standard.md` | 不存在 |
| `10-architecture/00-architectural-principles.md` | 1525 | `../../AirymaxOS/TERMINOLOGY.md` | 本地 `TERMINOLOGY.md` 存在 |

> **证据**：`50-engineering-standards/10-coding-style/` 实际文件为 `C_Cpp_coding_style.md`、`Go_coding_style.md`、`Rust_coding_style.md`、`coding_conventions.md`、`scripting_coding_style.md`

### 3.8 [P2-MINOR] 06-iron9-shared-model.md 递归注释

**问题描述**：`06-iron9-shared-model.md:214` 存在递归注释。

```c
#define AIRY_EOK 0 /* 成功（替代 AIRY_EOK） */
```

> **证据**：注释说"替代 AIRY_EOK"但自身就是 AIRY_EOK 的定义，应为"成功"或"替代 POSIX errno"

### 3.9 [P2-MINOR] TERMINOLOGY.md 路径头错误

**问题描述**：`TERMINOLOGY.md:8` 标注路径为 `Docs/TERMINOLOGY.md`，实际路径为 `docs/AirymaxRT/TERMINOLOGY.md`。

**方案冲突评分：45/D+**

---

## 4. 工程标准对齐评估

### 4.1 50-engineering-standards 符号链接

| 检查项 | 结果 | 证据 |
|--------|------|------|
| 符号链接存在 | ✓ | `readlink 50-engineering-standards` = `../AirymaxOS/50-engineering-standards` |
| 23 文档共享 | ✓ | `find 50-engineering-standards -type f -name "*.md" \| wc -l` = 23 |
| SSoT 注册表存在 | ✓ | `09-ssot-registry.md` 为全局规则编号 SSoT |

### 4.2 规则编号体系（IRON/BAN/STD/ACC）

| 前缀 | SSoT 定义 | AirymaxRT 引用 | 评估 |
|------|----------|---------------|------|
| OS-IRON-001~014 | `09-ssot-registry.md §2` | 06-iron9-shared-model.md 引用 IRON-8/9/14 | ✓ 正确引用 |
| OS-KER-001~155 | `09-ssot-registry.md §3` | 架构文档引用 | ✓ |
| OS-STD-* | `09-ssot-registry.md §4` | 工程标准文档 | ✓ |
| OS-BAN-* | `09-ssot-registry.md §5` | 禁止规则 | ✓ |
| OS-ACC-* | `09-ssot-registry.md §6` | 验收标准 | ✓ |
| OS-ABI-* | `09-ssot-registry.md §7` | 接口稳定性 | ✓ |

**评估**：规则编号体系对齐 SSoT，未发现私自定义新编号。

### 4.3 三作用域文档总数模型（~79/85/122）

| 作用域 | 数量 | 上下文 | AirymaxRT 是否引用 |
|--------|------|--------|-------------------|
| ~79 | P0 基线 | "文档体系完成"上下文 | ✗ 未引用 |
| ~85 | 工程基线 | "0.1.1 合计/总产出"上下文 | ✗ 未引用 |
| ~122 | 全量展开 | "全部三大支柱"上下文 | ✗ 未引用 |

**实际统计**：
- AirymaxRT 独有文档：88 - 23（共享工程标准）= 65 个
- AirymaxOS 文档：123 个
- 合计去重：65 + 123 = 188 个（远超 ~122）

**评估**：三作用域模型未在 AirymaxRT 文档中引用，且实际文档数量（88）与三作用域模型（~79/85/122）不匹配。AirymaxRT 应建立自己的文档计数模型，或明确说明 88 文档在三作用域中的归属。

### 4.4 IRON-9 v2 三层共享模型对齐

| 层次 | SSoT 定义（120-cross-project-code-sharing.md） | AirymaxRT 实现 | 评估 |
|------|-----------------------------------------------|---------------|------|
| [SC] 共享契约层 | 6 头文件逐字节相同 | 06-iron9-shared-model.md 定义 | ✗ 第 6 头文件不一致（bpf_struct_ops.h vs syscalls.h） |
| [SS] 语义同源层 | 高层 API 语义同源，签名独立 | 架构文档描述 | ✓ |
| [IND] 完全独立层 | 各自独立仓库 | 跨平台用户态/SDK 四语言 | ✓ |
| 双向 CI 校验 | 契约层变更双向校验 | 未文档化 | △ 缺失 |

### 4.5 工程标准对齐评分：80/B

---

## 5. 函数前缀和命名评估

### 5.1 前缀分层设计

| 前缀 | 用途 | SSoT 定义 | AirymaxRT 使用 | 评估 |
|------|------|----------|---------------|------|
| `airy_*` | [SC] 共享契约层 + 内部实现 | 120-cross-project-code-sharing.md | `airy_ipc_msg_hdr`、`airy_task_desc`、`airy_sys_agent_spawn` 等 | ✓ 正确 |
| `are_*` | ARE 标准 ABI（L1/L2/L3 公开接口） | 05-runtime-interfaces/ | `are_error_t`、`are_permission_check`、`are_ipc_message_header_t` | △ 部分违规（IPC 头） |
| `agentrt_*` | agentrt 专属 API | 任务描述提及 | **完全未出现** | ✗ 缺失 |
| `agentos_*` | 旧前缀（已改名） | — | **0 处残留** | ✓ 清理彻底 |
| `airymaxos_*` | AirymaxOS 专属（agentrt 禁用） | 06-iron9-shared-model.md:268 禁止 | **0 处误用**（仅出现在禁止声明中） | ✓ 正确 |

> **证据**：
> - `grep -rn "agentrt_" docs/AirymaxRT/` = No matches found
> - `grep -rn "agentos_" docs/AirymaxRT/` = No matches found
> - `grep -rn "airymaxos_" docs/AirymaxRT/` = 2 处（均为禁止声明："不使用 `airymaxos_` 前缀"）

### 5.2 [P1-MAJOR] `agentrt_*` 专属 API 前缀缺失

**问题描述**：任务描述明确要求 agentrt 拥有专属 API 前缀 `agentrt_*`，但全文档中 0 处使用。

**影响**：agentrt 专属 API（如 daemon 管理、配置管理、运行时控制等非 [SC] 共享、非 ARE 标准的内部 API）缺乏统一命名前缀，与 `airy_*`（共享）和 `are_*`（标准 ABI）的分层不完整。

**建议**：文档化三层前缀分层：
- `airy_*` — [SC] 共享契约层 + 微核心原语（atoms 层）
- `are_*` — ARE 标准 ABI（L1/L2/L3 公开接口，第三方可实现）
- `agentrt_*` — agentrt 专属 API（daemon 管理、配置、运行时控制）

### 5.3 [P0-CRITICAL] IPC 消息头结构体命名违规

**问题描述**：`30-interfaces/06-ipc/README.md` 定义 IPC 消息头结构体为 `are_ipc_message_header_t`，但 [SC] SSoT 明确要求为 `airy_ipc_msg_hdr`。

| 属性 | `06-ipc/README.md`（违规） | `120-cross-project-code-sharing.md`（SSoT） | `06-iron9-shared-model.md`（agentrt 侧） |
|------|---------------------------|---------------------------------------------|------------------------------------------|
| 结构体名 | `are_ipc_message_header_t` | `airy_ipc_msg_hdr` | `airy_ipc_msg_hdr`（正确引用） |
| 类型 | `uint32_t` / `uint16_t` / `uint64_t` | `__u32` / `__u16` / `__u64` | `__u32` / `__u16` / `__u64` |
| 对齐 | 无 `__attribute__((packed))` | `__attribute__((packed))` | `__attribute__((packed))` |
| 字段布局 | 13 字段（magic/version/msg_type/protocol/msg_id/trace_id/correlation_id/source[32]/target[32]/payload_len/flags/timestamp_ns/checksum/reserved） | 8 字段（magic/opcode/flags/trace_id/timestamp_ns/src_task/dst_task/payload_len/reserved[84]） | 8 字段（同 SSoT） |
| 大小 | 声称 128 字节但实际 >128 | 128 字节（`_Static_assert` 验证） | 128 字节 |

> **证据**：
> - `30-interfaces/06-ipc/README.md:27` `typedef struct are_ipc_message_header`
> - `120-cross-project-code-sharing.md:343` `struct airy_ipc_msg_hdr`
> - `06-iron9-shared-model.md:140` "结构体名称为 `airy_ipc_msg_hdr`（**不是** `airymaxos_ipc_msg_hdr` 或 `are_ipc_message_header_t`）"

**三重违规**：
1. **命名违规**：`are_ipc_message_header_t` → 应为 `airy_ipc_msg_hdr`
2. **类型违规**：`uint32_t` → 应为 `__u32`（UAPI 类型，通过 `uapi_compat.h`）
3. **布局违规**：13 字段含 `source[32]`/`target[32]` 字符数组 → 应为 8 字段含 `src_task`/`dst_task` 整型

**影响**：IPC 消息头是 [SC] 共享契约层核心头文件 `ipc.h` 的关键结构，三重违规导致 agentrt 与 AirymaxOS 无法互操作，违反 IRON-008（[SC] 共享契约层双向 CI 验证）和 IRON-014（6 头文件单一数据源）。

### 5.4 函数前缀和命名评分：72/B-

---

## 6. 跨平台一致性评估

### 6.1 用户态跨平台定位

| 检查项 | 结果 | 证据 |
|--------|------|------|
| MicroCoreRT 定位为 Ring 3 用户态 | ✓ | `04-microcorert.md:183` "运行在用户态（Ring 3），依赖宿主操作系统" |
| 跨 Linux/macOS/Windows 三平台 | ✓ | `01-getting-started.md:15` "Ubuntu 22.04+ / macOS 13+ / Windows 11 (WSL2)" |
| 通过 libc/POSIX 跨平台 | ✓ | `04-microcorert.md` 描述 POSIX 抽象 |
| UAPI 类型兼容（uapi_compat.h） | ✓ | `120-cross-project-code-sharing.md:119-123` 定义 macOS/Windows 通过 `<stdint.h>` + typedef |
| Linux 可选内核加速路径 | ✓ | `06-iron9-shared-model.md` 描述 [SS] 语义同源层 |
| macOS/Windows 仅走用户态 | ✓ | 无内核态路径文档 |

### 6.2 [P0-CRITICAL] "操作系统"自称与用户态定位矛盾

详见第 3.2 节。15+ 处文档自称"操作系统"，但 agentrt 实际为用户态运行时（Ring 3），依赖宿主 OS。

**核心矛盾**：
- `04-microcorert.md:183`："MicroCoreRT 运行在用户态（Ring 3），依赖宿主操作系统"
- `00-architectural-principles.md:54`："Airymax 是一个**驱动多智能体协作的操作系统**"

两者直接矛盾。agentrt 不是操作系统，而是运行在操作系统之上的用户态运行时平台。

### 6.3 跨平台 SDK 四语言支持

| 语言 | 文档 | 评估 |
|------|------|------|
| Go | `30-interfaces/70-toolkit/10-go/README.md` | ✓ 存在 |
| Python | `30-interfaces/70-toolkit/20-python/README.md` | ✓ 存在 |
| Rust | `30-interfaces/70-toolkit/30-rust/README.md` | ✓ 存在（438 行，充实） |
| TypeScript | `30-interfaces/70-toolkit/40-typescript/README.md` | ✓ 存在 |

### 6.4 跨平台一致性评分：78/B

---

## 7. 29 仓拆分对齐评估

### 7.1 [P0-CRITICAL] 29 仓拆分完全未文档化

**问题描述**：AirymaxRT 文档中**完全没有**提及 29 仓拆分方案（1 伞仓 + 4 管理仓 + 21 叶子仓 + 3 顶层仓）。

> **证据**：`grep -rn "29 仓\|29 repo\|29-repo\|29 子仓" docs/AirymaxRT/` = No matches found

### 7.2 SSoT 中的仓库结构信息

| SSoT 条目 | 内容 | 评估 |
|-----------|------|------|
| `09-ssot-registry.md` OS-IRON-013 | "8 子仓独立 git 仓库 + submodule" | 仅描述 AirymaxOS 8 子仓，未描述 agentrt 仓库结构 |
| `120-cross-project-code-sharing.md` | "各自独立仓库，无依赖"（[IND] 层） | 笼统提及，无具体仓库清单 |

### 7.3 agentrt 仓库结构缺失

**应有内容**：
- agentrt 作为管理仓的定位（与 AirymaxOS 同级，伞仓直属）
- agentrt 管理的子仓清单（如 atoms / coreloopthree / memoryrovol / daemon / sdk 等）
- submodule 管理方式
- 与 29 仓拆分方案的关系（agentrt 在 1 伞仓 + 4 管理仓 + 21 叶子仓 + 3 顶层仓中的位置）

**实际内容**：完全缺失。

### 7.4 `01-getting-started.md` 中的仓库引用

```bash
git clone https://atomgit.com/openairymax/agentrt.git
```

> **证据**：`01-getting-started.md:38` 引用单一 `agentrt.git` 仓库，未提及 submodule 或多仓结构。

### 7.5 29 仓拆分对齐评分：30/F

---

## 8. 草案文档清单和充实优先级

### 8.1 草案文档清单（<200 行）

| 优先级 | 文件 | 行数 | 充实方向 |
|--------|------|------|---------|
| **P0** | `50-specifications/10-contracts/06-glossary-index.md` | 229 | **删除或合并**——与 `20-modules/10-contracts/06-glossary-index.md` 近乎重复 |
| **P0** | `30-interfaces/05-runtime-interfaces/README.md` | 49 | 充实 L1/L2/L3 标准总览 |
| **P0** | `30-interfaces/06-ipc/README.md` | 69 | **重写**——IPC 头结构体三重违规，需对齐 SSoT |
| **P0** | `30-interfaces/08-service-discovery/README.md` | 76 | 充实服务发现机制 |
| **P0** | `140-application-development/01-sdk/README.md` | 80 | 充实 SDK 概述或删除冗余目录 |
| **P1** | `30-interfaces/07-rpc-api/README.md` | 90 | 充实 RPC API 规范 |
| **P1** | `00-requirements/04-design-principles-cn.md` | 99 | 充实设计原则中文版 |
| **P1** | `00-requirements/04-design-principles.md` | 106 | 充实设计原则英文版 |
| **P1** | `30-interfaces/60-syscalls/06-telemetry.md` | 112 | 充实遥测系统调用 |
| **P1** | `README.md` | 112 | 充实英文 README（vs 中文 187 行） |
| **P1** | `00-requirements/02-cognition-design-cn.md` | 123 | 充实认知设计中文版 |
| **P1** | `00-requirements/02-cognition-design.md` | 130 | 充实认知设计英文版 |
| **P2** | `10-architecture/50-services/01-daemon.md` | 141 | 已充实（V8.0），可扩展部署细节 |
| **P2** | `00-requirements/03-memory-design-cn.md` | 143 | 充实记忆设计中文版 |
| **P2** | `30-interfaces/60-syscalls/05-task.md` | 145 | 充实任务管理系统调用 |
| **P2** | `00-requirements/03-memory-design.md` | 152 | 充实记忆设计英文版 |
| **P2** | `00-requirements/01-mcis-cn.md` | 158 | 充实 MCIS 理论中文版 |
| **P2** | `00-requirements/01-mcis.md` | 169 | 充实 MCIS 理论英文版 |
| **P2** | `30-interfaces/60-syscalls/02-memory.md` | 170 | 充实记忆管理系统调用 |
| **P2** | `30-interfaces/60-syscalls/01-agent.md` | 179 | 充实 Agent 管理系统调用 |
| **P2** | `30-interfaces/60-syscalls/03-session.md` | 184 | 充实会话管理系统调用 |
| **P2** | `README_zh.md` | 187 | 已充实，可扩展英文版对齐 |

### 8.2 50-specifications/ 目录评估

**问题**：`50-specifications/` 目录仅含 1 个文件 `10-contracts/06-glossary-index.md`（229 行），且与 `20-modules/10-contracts/06-glossary-index.md` 近乎重复（仅路径引用不同）。

**建议**：
- **方案 A**（推荐）：删除 `50-specifications/` 目录，保留 `20-modules/10-contracts/06-glossary-index.md` 作为唯一术语索引
- **方案 B**：将 `50-specifications/` 重新定位为"规范规格书"目录，充实正式规范文档

### 8.3 草案文档评分：65/C+

---

## 9. IPC 协议一致性评估

### 9.1 Magic 值验证

| Magic | 值 | SSoT 定义 | AirymaxRT 引用 | 评估 |
|-------|-----|---------|---------------|------|
| IPC magic | `0x41524531` ('ARE1') | `120-cross-project-code-sharing.md:303` | `06-iron9-shared-model.md:113` | ✓ 一致 |
| 任务描述符 magic | `0x41475453` ('AGTS') | `120-cross-project-code-sharing.md:237` | `06-iron9-shared-model.md:153` | ✓ 一致 |

### 9.2 [P0-CRITICAL] IPC 消息头结构体三重违规

详见第 5.3 节。

**违规汇总**：

| 维度 | `06-ipc/README.md`（违规） | SSoT 要求 | 违规类型 |
|------|---------------------------|----------|---------|
| 结构体名 | `are_ipc_message_header_t` | `airy_ipc_msg_hdr` | 命名违规 |
| 类型前缀 | `uint32_t` / `uint16_t` / `uint64_t` | `__u32` / `__u16` / `__u64` | UAPI 类型违规 |
| 对齐属性 | 无 | `__attribute__((packed))` | 对齐违规 |
| 字段数 | 13 字段 | 8 字段 | 布局违规 |
| 字段类型 | `char source[32]` / `char target[32]` | `__u64 src_task` / `__u64 dst_task` | 语义违规 |
| 大小验证 | 无 | `_Static_assert(sizeof(...) == 128)` | 缺失验证 |

### 9.3 IPC 头文件路径

| 检查项 | 结果 | 证据 |
|--------|------|------|
| [SC] 头文件名 | `ipc.h` | `120-cross-project-code-sharing.md:75` |
| 落地路径 | `include/airymax/ipc.h` | SSoT 定义 |
| 06-iron9-shared-model.md 引用 | `ipc.h`（曾误为 `ipc_msg_hdr.h`，已修正） | ✓ 已修正 |

### 9.4 任务描述符一致性

| 属性 | SSoT（`sched.h`） | AirymaxRT 引用 | 评估 |
|------|------------------|---------------|------|
| 结构体名 | `airy_task_desc` | `06-iron9-shared-model.md` 引用 | ✓ 一致 |
| magic 字段 | `__u32 magic` | ✓ | ✓ 一致 |
| magic 值 | `0x41475453` ('AGTS') | ✓ | ✓ 一致 |
| vtime 类型 | `airy_vtime_t`（=`__s32` Q16.16） | ✓ | ✓ 一致 |
| 优先级范围 | 0-139 | ✓ | ✓ 一致 |

### 9.5 ARE 标准 ABI 与 [SC] 共享契约层的关系

**设计意图**：
- `[SC]` 共享契约层（`airy_*` 前缀）：agentrt 与 AirymaxOS 逐字节相同的 6 头文件
- `ARE` 标准 ABI（`are_*` 前缀）：第三方可实现的公开标准接口（L1/L2/L3）

**冲突点**：`06-ipc/README.md` 将 IPC 消息头（[SC] 共享结构 `airy_ipc_msg_hdr`）重新定义为 ARE 标准结构 `are_ipc_message_header_t`，混淆了两层边界。

**正确做法**：
- IPC 消息头是 [SC] 共享结构，必须使用 `airy_ipc_msg_hdr`（`airy_` 前缀）
- ARE 标准 ABI 可在 L1/L2/L3 文档中引用 `airy_ipc_msg_hdr`，但不得重新定义

### 9.6 IPC 协议一致性评分：55/D+

---

## 10. 改进建议（P0/P1/P2 分级）

### 10.1 P0 改进建议（Critical，阻断 1.0.1 M1）

#### P0-01：统一错误码体系（预计 8h）

**问题**：6 套错误码并行（第 3.1 节）

**修复方案**：
1. 在 `50-engineering-standards/` 中建立错误码 SSoT 文档（或扩展 `120-cross-project-code-sharing.md`）
2. 统一为 SSoT 方案：`airy_err_t`（`int32_t`），`AIRY_EOK=0`，错误码为负值，13 个 `AIRY_E*` 宏
3. 明确 `AIRY_*`（内部 + [SC]）与 `ARE_*`（标准 ABI）的映射关系
4. 全量替换 6 套方案为统一方案
5. 统一命名：`AIRY_EOK`（非 `AIRY_OK`）、`AIRY_ETIMEOUT`（非 `AIRY_ETIMEDOUT`）

**影响文件**：
- `10-architecture/00-architectural-principles.md`（行 922-940）
- `10-architecture/06-iron9-shared-model.md`
- `10-architecture/05-syscall.md`（行 641-646）
- `20-modules/10-contracts/04-syscall-api-contract.md`（行 99-108）
- `20-modules/10-contracts/06-glossary-index.md`（行 173-180）
- `20-modules/10-contracts/03-protocol-contract.md`（行 494-500）
- `30-interfaces/README.md`（行 78-86）
- `30-interfaces/05-runtime-interfaces/01-l1-runtime-interface.md`

#### P0-02：消除"操作系统"定位冲突（预计 4h）

**问题**：15+ 处误称"操作系统"（第 3.2 节）

**修复方案**：
1. 全量替换"操作系统"为"运行时平台"或"运行时"（除真正指代宿主 OS 的上下文）
2. 修正 `04-mainpage.dox` 标题"多体控制论智能操作系统" → "多体控制论智能运行时"
3. 修正 `00-architectural-principles.md:54` "驱动多智能体协作的操作系统" → "驱动多智能体协作的运行时平台"
4. 修正 `40-philosophy/01-design-philosophy.md` 中"操作系统"相关表述（行 38/45/110/117/119）
5. 保留 `04-microcorert.md` 中正确描述（"借鉴操作系统设计" ≠ "是操作系统"）

**影响文件**：13 个文件，40 处匹配

#### P0-03：修正 [SC] 头文件清单（预计 1h）

**问题**：`06-iron9-shared-model.md` 第 6 头文件为 `bpf_struct_ops.h`，SSoT 为 `syscalls.h`（第 3.3 节）

**修复方案**：
1. 修正 `06-iron9-shared-model.md` 第 6 头文件：`bpf_struct_ops.h` → `syscalls.h`
2. 将 `bpf_struct_ops.h` 移至"补充共享文件"小节
3. 对齐 `120-cross-project-code-sharing.md` 的 6 头文件清单

**影响文件**：`10-architecture/06-iron9-shared-model.md`

#### P0-04：修正 IPC 消息头结构体三重违规（预计 3h）

**问题**：`06-ipc/README.md` 的 `are_ipc_message_header_t` 三重违规（第 5.3/9.2 节）

**修复方案**：
1. 重写 `30-interfaces/06-ipc/README.md`，对齐 SSoT `airy_ipc_msg_hdr`
2. 结构体名：`are_ipc_message_header_t` → `airy_ipc_msg_hdr`
3. 类型：`uint32_t` → `__u32`，`uint16_t` → `__u16`，`uint64_t` → `__u64`
4. 对齐：添加 `__attribute__((packed))`
5. 字段布局：对齐 SSoT 8 字段（magic/opcode/flags/trace_id/timestamp_ns/src_task/dst_task/payload_len/reserved[84]）
6. 添加 `_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128)`
7. 引用 `#include <airymax/uapi_compat.h>` 获取 UAPI 类型

**影响文件**：`30-interfaces/06-ipc/README.md`

#### P0-05：修正文件路径引用错误（预计 3h）

**问题**：系统性路径引用错误（第 3.7 节）

**修复方案**：
1. `00-basic-theories/` → `00-requirements/`（全量替换）
2. `../30-coding-standard/10-log-standard.md` → 正确路径
3. `50-engineering-standards/08-compliance-checklist.md` → 删除引用或创建文件
4. `50-engineering-standards/50-project-erp/error_code_reference.md` → 删除引用或创建文件
5. `C_coding_style_standard.md` → `C_Cpp_coding_style.md`
6. `C_Cpp_secure_coding_standard.md` → 删除引用（不存在）
7. `Rust_coding_style_standard.md` → `Rust_coding_style.md`
8. `log_standard.md` → `coding_conventions.md` 或正确路径
9. `../../AirymaxOS/TERMINOLOGY.md` → `../../TERMINOLOGY.md`（本地存在）

**影响文件**：~10 个文件

### 10.2 P1 改进建议（Major，1.0.1 M1 内完成）

#### P1-01：统一 Cupola/Cupolas 术语（预计 1h）

**修复**：全量替换 `Cupola`（单数）为 `Cupolas`（复数），除明确指代单一子系统的上下文。

**影响文件**：4 个文件

#### P1-02：修正 daemon 数量标注（预计 0.5h）

**修复**：`01-system-architecture.md` 行 305/309 的"10" → "12"。

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
   - `airy_*` — [SC] 共享契约层 + 微核心原语
   - `are_*` — ARE 标准 ABI（L1/L2/L3）
   - `agentrt_*` — agentrt 专属 API
2. 在 `TERMINOLOGY.md` 中添加前缀分层说明

#### P1-05：修正 MemoryRovol 层级命名（预计 1h）

**修复**：
1. `02-c-language-boundary.md:72` "Working → Short-term → Long-term → Archival" → "L1 Raw → L2 Feature → L3 Structure → L4 Pattern"
2. `02-logging.md` 日志 L1-L4 改为 LOG_DEBUG/INFO/WARN/ERROR 或其他非冲突命名

#### P1-06：处理 50-specifications/ 目录（预计 1h）

**修复**：删除 `50-specifications/` 目录及其重复的 `06-glossary-index.md`，或重新定位为规范规格书目录。

#### P1-07：充实 5 个 <100 行草案文档（预计 10h）

**优先充实**：
1. `05-runtime-interfaces/README.md`（49 行）→ L1/L2/L3 总览
2. `06-ipc/README.md`（69 行）→ 重写对齐 SSoT（P0-04 已覆盖）
3. `08-service-discovery/README.md`（76 行）→ 服务发现机制
4. `01-sdk/README.md`（80 行）→ SDK 概述或删除
5. `07-rpc-api/README.md`（90 行）→ RPC API 规范

#### P1-08：对齐中英文 README（预计 2h）

**修复**：英文 `README.md`（112 行）与中文 `README_zh.md`（187 行）内容不对等，需补全英文版文档索引。

### 10.3 P2 改进建议（Minor，1.0.1 内完成）

#### P2-01：修正 06-iron9-shared-model.md 递归注释（预计 0.1h）

**修复**：行 214 `/* 成功（替代 AIRY_EOK） */` → `/* 成功 */`

#### P2-02：修正 TERMINOLOGY.md 路径头（预计 0.1h）

**修复**：行 8 `Docs/TERMINOLOGY.md` → `docs/AirymaxRT/TERMINOLOGY.md`

#### P2-03：充实 00-requirements/ 中英双语文档（预计 8h）

**修复**：8 个文件均为 <170 行，需充实理论内容至 ≥250 行。

#### P2-04：充实 60-syscalls/ 系统调用文档（预计 6h）

**修复**：6 个文件均为 <185 行，需补充参数说明、返回值、错误码、示例代码。

#### P2-05：建立 AirymaxRT 文档计数模型（预计 1h）

**修复**：在 `README.md` 或 `09-ssot-registry.md` 中建立 AirymaxRT 文档计数模型（当前 88 文档），明确与三作用域模型（~79/85/122）的关系。

#### P2-06：补充缺失的工程目录（预计 4h）

**修复**：考虑新建：
- `70-build/` — CMake 构建系统文档
- `80-testing/` — 测试框架文档（独立于 `10-architecture/20-engineering/01-testing.md`）
- `120-development-process/` — 开发流程文档

### 10.4 改进建议汇总

| 优先级 | 数量 | 预计工时 | 阻断 1.0.1 M1 |
|--------|------|---------|--------------|
| P0 | 5 项 | ~19h | ✓ 阻断 |
| P1 | 8 项 | ~23h | △ 建议在 M1 内完成 |
| P2 | 6 项 | ~19h | ✗ 不阻断 |
| **合计** | **19 项** | **~61h** | — |

---

## 附录 A：审查文件清单

### A.1 已完整阅读文件

| 文件 | 行数 | 审查深度 |
|------|------|---------|
| `10-architecture/06-iron9-shared-model.md` | 346 | 完整 |
| `10-architecture/00-architectural-principles.md` | 1530 | 完整 |
| `10-architecture/01-system-architecture.md` | 594 | 完整 |
| `10-architecture/04-microcorert.md` | 806 | 完整 |
| `10-architecture/40-philosophy/01-design-philosophy.md` | 253 | 完整 |
| `10-architecture/50-services/01-daemon.md` | 141 | 完整 |
| `10-architecture/30-kernel/02-c-language-boundary.md` | 456 | 部分（100 行） |
| `10-architecture/20-engineering/01-testing.md` | 224 | 部分 |
| `TERMINOLOGY.md` | 612 | 完整 |
| `README.md` | 112 | 完整 |
| `README_zh.md` | 187 | 完整 |
| `30-interfaces/README.md` | 120 | 完整 |
| `30-interfaces/06-ipc/README.md` | 69 | 完整 |
| `30-interfaces/02-api-reference.md` | 2682 | 部分（80 行） |
| `30-interfaces/05-runtime-interfaces/01-l1-runtime-interface.md` | — | 部分（50 行） |
| `30-interfaces/05-runtime-interfaces/03-l3-security-governance.md` | — | 部分（80 行） |
| `30-interfaces/60-syscalls/01-agent.md` | 179 | 部分（50 行） |
| `20-modules/10-contracts/06-glossary-index.md` | 229 | 完整 |
| `50-specifications/10-contracts/06-glossary-index.md` | 229 | 完整（重复） |
| `50-engineering-standards/120-cross-project-code-sharing.md` | — | 部分（200 行） |
| `50-engineering-standards/09-ssot-registry.md` | — | 部分（200 行） |
| `140-application-development/01-getting-started.md` | 261 | 部分（60 行） |
| `140-application-development/24-create-agent.md` | — | 部分（60 行） |
| `00-requirements/01-mcis.md` | 169 | 部分 |
| `00-requirements/02-cognition-design.md` | 130 | 部分 |
| `00-requirements/03-memory-design.md` | 152 | 部分 |

### A.2 Grep / Shell 验证命令

```bash
# 文档总数
find docs/AirymaxRT -type f -name "*.md" | wc -l  # = 88

# 符号链接验证
readlink 50-engineering-standards  # = ../AirymaxOS/50-engineering-standards

# 错误码方案搜索
grep -rn "AIRY_E\|ARE_OK\|ARE_E" --include="*.md" docs/AirymaxRT/

# "操作系统"冲突搜索
grep -rn "操作系统" --include="*.md" docs/AirymaxRT/  # = 40 行

# 前缀检查
grep -rn "agentrt_" docs/AirymaxRT/  # = 0（缺失）
grep -rn "agentos_" docs/AirymaxRT/  # = 0（清理彻底）
grep -rn "airymaxos_" docs/AirymaxRT/  # = 2（均为禁止声明）

# 29 仓搜索
grep -rn "29 仓\|29 repo" docs/AirymaxRT/  # = 0（完全缺失）

# Cupola vs Cupolas
grep -rl "Cupola[^s]" --include="*.md" docs/AirymaxRT/  # = 4 文件
grep -rl "Cupolas" --include="*.md" docs/AirymaxRT/  # = 10 文件

# 草案文档（<200 行）
find docs/AirymaxRT -type f -name "*.md" -exec wc -l {} \; | sort -n | head -22
```

---

## 附录 B：与前序审查报告的关系

| 报告 | 范围 | 关系 |
|------|------|------|
| `01-atoms-source-deep-review.md` | agentrt atoms 模块源代码 | 源码级审查，本文档为方案级审查，互补 |
| `02-daemons-others-source-deep-review.md` | daemon 及其他模块源代码 | 源码级审查，本文档为方案级审查，互补 |
| **`03-airymaxrt-solution-review.md`（本文档）** | AirymaxRT 全量文档方案 | 方案级审查，覆盖目录/冲突/命名/IPC/29 仓等 |

---

## 附录 C：综合评分矩阵

| 维度 | 评分 | 等级 | 关键问题 |
|------|------|------|---------|
| 1. 目录结构完整性 | 70 | B- | 50-specifications/ 空置，60+ 目录部分缺失 |
| 2. 文档内容深度 | 75 | B | 核心架构质量高，草案偏多 |
| 3. 方案冲突 | 45 | D+ | 6 套错误码 + "操作系统"冲突 + [SC] 头文件不一致 |
| 4. 工程标准对齐 | 80 | B | 符号链接正确，SSoT 引用规范 |
| 5. 函数前缀和命名 | 72 | B- | agentrt_* 缺失，IPC 头命名违规 |
| 6. 跨平台一致性 | 78 | B | 用户态定位正确，"操作系统"自称矛盾 |
| 7. 29 仓拆分对齐 | 30 | F | 完全未文档化 |
| 8. 草案文档 | 65 | C+ | ~15 个 <200 行文件 |
| 9. IPC 协议一致性 | 55 | D+ | magic 正确，IPC 头三重违规 |
| **综合** | **62** | **C+** | 核心设计扎实，系统性一致性问题需 P0 修复 |

---

**审查结论**：AirymaxRT 文档体系在**架构设计层面**（MicroCoreRT / CoreLoopThree / MemoryRovol / Thinkdual / Cupolas / 12 Daemons / MCIS 体系并行论 / 五维正交 24 原则）质量较高，理论根基完整，原创性强。但在**工程一致性层面**存在 5 项 P0 级系统性问题（错误码 6 套并行、"操作系统"定位冲突、[SC] 头文件清单不一致、IPC 头三重违规、路径引用错误），需优先修复后方可进入 1.0.1 M1 代码开发。29 仓拆分完全未文档化是最重大缺失，需在 M1 阶段补齐。

建议修复路径：P0（~19h）→ 进入 1.0.1 M1 → P1（~23h）M1 内完成 → P2（~19h）1.0.1 内完成。

---

<div align="center">

**© 2025-2026 SPHARX Ltd.** All Rights Reserved.

</div>
