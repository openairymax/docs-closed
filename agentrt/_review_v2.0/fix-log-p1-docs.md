Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# AirymaxRT 开源文档 P1 级问题修复日志

> **修复范围**： `docs/AirymaxRT/`（仅开源文档，不含源码、闭源文档、`docs/AirymaxOS/`）\
> **修复日期**： 2026-07-13\
> **修复版本**： 0.1.1（文档体系完成）\
> **修复依据**： `docs-closed/agentrt/_review_v2.0/01-engineering-code-review-v2.md` P1 级问题清单

---

## 修复总览

| P1 编号 | 问题摘要 | 状态 | 修改文件数 |
|---------|---------|------|-----------|
| P1-5 | 单数 "Cupola" 应统一为复数 "Cupolas" | ✅ 已完成 | 5（4 .md + 1 .drawio） |
| P1-6 | 守护进程数量 10 应改为 12 | ✅ 已完成 | 1 |
| P1-11 | MemoryRovol 四层命名标准化 + 与 [SC] 缓存层级区分 | ✅ 已完成 | 1 |
| P1-13 | 删除重复的 `50-specifications/10-contracts/06-glossary-index.md` | ✅ 已完成 | 删除 1 文件 + 2 空目录 |
| P1-1/3 | `06-iron9-shared-model.md` 补充函数前缀三层定义 | ✅ 已完成 | 1 |

---

## P1-5：单数 "Cupola" 统一为复数 "Cupolas"

### 问题描述

文档中混用单数 "Cupola" 与复数 "Cupolas"，应统一为复数 "Cupolas"（安全穹顶是多个独立实例的集合概念）。

### 修复方法

采用**三步替换法**，避免直接替换导致 "Cupolas" 变成 "Cupolass"：

1. 将已存在的 "Cupolas" 临时替换为 "CUPOLAS_TMP"（保护已正确的内容）
2. 将 "Cupola" 替换为 "Cupolas"（处理单数形式）
3. 将 "CUPOLAS_TMP" 恢复为 "Cupolas"（还原保护内容）

对于 ASCII 框图，因 "Cupolas"（7 字符）比 "Cupola"（6 字符）多 1 字符，需同步缩减尾部空格 1 个以保持框线对齐。

### 修改文件清单

#### 1. `10-architecture/01-system-architecture.md`

- **修改内容**：三步替换法替换 20 处 "Cupola"→"Cupolas"
- **ASCII 对齐修复**：
  - 第 34 行：3 处 `Cupolas    │` → `Cupolas   │`（4 空格→3 空格）
  - 第 86 行：移除 `│` 前 1 个尾部空格（通过 Python 脚本精确处理中文字符宽度）
- **验证**：`Grep "Cupola[^s]"` → 0 匹配；`Grep "Cupolas"` → 25 匹配

#### 2. `10-architecture/30-kernel/02-c-language-boundary.md`

- **修改内容**：
  - 第 18 行 ASCII 框图：`Cupola    │` → `Cupolas   │`（直接替换，无已存在 Cupolas）
  - 第 59 行表格：`| **Cupola** |` → `| **Cupolas** |`
- **验证**：`Grep "Cupola[^s]"` → 0 匹配

#### 3. `10-architecture/40-philosophy/01-design-philosophy.md`

- **修改内容**：三步替换法替换 3 处 "Cupola"→"Cupolas"（第 128、142 行）
- **说明**：文件中已有 5 处 "Cupolas"（第 61、89、93、128、138 行），经三步法保护后未受影响
- **验证**：`Grep "Cupola[^s]"` → 0 匹配

#### 4. `20-modules/10-contracts/05-logging-format.md`

- **修改内容**：三步替换法替换 1 处 "Cupola"→"Cupolas"
  - 第 478 行 JSON 字符串：`"message":"Cupola policy violation detected"` → `"message":"Cupolas policy violation detected"`
- **说明**：文件中已有 2 处 "Cupolas"（第 380、473 行），经三步法保护后未受影响
- **验证**：`Grep "Cupola[^s]"` → 0 匹配

#### 5. `10-architecture/60-diagrams/03-overall-architecture.drawio`

- **修改内容**：直接 `replace_all` "Cupola"→"Cupolas"（11 处，文件中无已存在 "Cupolas"，无需三步法）
- **说明**：XML 格式文件，无 ASCII 框图对齐问题
- **验证**：`Grep "Cupola[^s]"` → 0 匹配；`Grep "Cupolas"` → 12 匹配

### 全局验证

```
Grep "Cupola[^s]" docs/AirymaxRT/ → 0 匹配（无残留单数形式）
Grep "Cupolas" docs/AirymaxRT/*.md → 74 匹配（跨 18 个 .md 文件）
Grep "Cupolas" *.drawio → 12 匹配
```

---

## P1-6：守护进程数量 10 改为 12

### 问题描述

`01-system-architecture.md` 中守护进程（Daemon）数量标注为 10，实际应为 12（market_d/sched_d/gateway_d/monit_d/plugin_d/tool_d/llm_d/channel_d/notify_d/hook_d/info_d/observe_d）。

### 修改文件

#### `10-architecture/01-system-architecture.md`

- **第 305 行**（文本）：
  - 旧：`Airymax 系统包含 10 个核心用户态服务 (Daemon Processes)，各自负责独立的职责域：`
  - 新：`Airymax 系统包含 12 个核心用户态服务 (Daemon Processes)，各自负责独立的职责域：`
- **第 309 行**（ASCII 框图）：
  - 旧：`│                    Airymax Daemon Services (10)                   │`
  - 新：`│                    Airymax Daemon Services (12)                   │`

### 验证

```
Grep "10 个核心" 01-system-architecture.md → 0 匹配
Grep "Services \(10\)" 01-system-architecture.md → 0 匹配
Grep "12 个核心" 01-system-architecture.md → 1 匹配（第 305 行）
Grep "Services \(12\)" 01-system-architecture.md → 1 匹配（第 309 行）
```

---

## P1-11：MemoryRovol 四层命名标准化

### 问题描述

`02-c-language-boundary.md` 第 72 行 MemoryRovol 四层命名使用非标准名称 "Working/Short-term/Long-term/Archival"，应改为标准命名 "L1 Raw/L2 Feature/L3 Structure/L4 Pattern"（与 `03-memoryrovol.md` 一致）。同时需与 [SC] `memory_types.h` 中的缓存层级（L1 HOT/L2 WARM/L3 COLD/L4 PMEM）明确区分，避免混淆。

### 修改文件

#### `10-architecture/30-kernel/02-c-language-boundary.md`

- **第 72 行**（表格行）：
  - 旧：`| **MemoryRovol** | 四层记忆管理系统 (Working → Short-term → Long-term → Archival)，管理 token budget 与 memory budget。 |`
  - 新：`| **MemoryRovol** | 四层记忆管理系统 (L1 Raw → L2 Feature → L3 Structure → L4 Pattern)，管理 token budget 与 memory budget。注意：此 L1-L4 为**记忆抽象层级**（原始/特征/结构/模式），与 [SC] \`memory_types.h\` 中的**缓存层级** (\`AIRY_MEM_L1_HOT\`/\`L2_WARM\`/\`L3_COLD\`/\`L4_PMEM\`) 是不同概念，不应混淆。 |`

### 设计说明

- **MemoryRovol 记忆抽象层级**（L1 Raw → L2 Feature → L3 Structure → L4 Pattern）：描述记忆从原始数据到模式知识的抽象过程，权威定义见 `10-architecture/03-memoryrovol.md`
- **[SC] 缓存层级**（`AIRY_MEM_L1_HOT`/`L2_WARM`/`L3_COLD`/`L4_PMEM`）：描述数据存储介质的冷热分层，权威定义见 `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md` §2.1
- 两者使用相同的 L1-L4 编号但语义完全不同，必须显式区分

### 验证

```
Grep "Working.*Short-term.*Long-term.*Archival" 02-c-language-boundary.md → 0 匹配（旧命名已消除）
Grep "L1 Raw.*L2 Feature.*L3 Structure.*L4 Pattern" 02-c-language-boundary.md → 1 匹配（第 72 行）
```

---

## P1-13：删除重复的 glossary-index 文件

### 问题描述

存在两个内容近乎相同的 `06-glossary-index.md` 文件：

- `50-specifications/10-contracts/06-glossary-index.md`（229 行，旧版/错误版）
- `20-modules/10-contracts/06-glossary-index.md`（229 行，新版/正确版）

经对比，`50-specifications` 版本存在以下错误：

| 问题 | 50-specifications 版本（错误） | 20-modules 版本（正确） |
|------|------------------------------|----------------------|
| 错误码前缀 | `AGENTRT_EOK`/`AGENTRT_EINVAL` | `AIRY_EOK`/`AIRY_EINVAL` |
| 术语表引用 | `../10-terminology.md`（不存在） | `../../TERMINOLOGY.md`（正确） |
| 路径头大小写 | `OpenAirymax/Docs/50-specifications/` | `OpenAirymax/docs/AirymaxRT/20-modules/` |
| SSoT 声明 | 无 | 有（引用 `include/airymax/error.h` [SC] 共享契约层） |
| 安全编码宏 | `AGENTRT_SECURE_ZERO` | `AIRY_SECURE_ZERO` |
| 错误码参考路径 | `../70-project-erp/02-error-code-reference.md` | `../../50-engineering-standards/50-project-erp/error_code_reference.md` |

### 修复操作

1. **删除重复文件**：`50-specifications/10-contracts/06-glossary-index.md`
2. **删除空目录**：`50-specifications/10-contracts/`
3. **删除空目录**：`50-specifications/`
4. **保留正确版本**：`20-modules/10-contracts/06-glossary-index.md`（229 行，未修改）

### 引用检查

```
Grep "50-specifications/10-contracts/06-glossary" docs/AirymaxRT/ → 0 匹配（无外部引用）
```

仅被删除文件自身的路径头（第 8 行）引用 `50-specifications`，无其他文件引用此路径。

### 验证

```
find docs/AirymaxRT -name "06-glossary-index.md" -type f
→ /home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxRT/20-modules/10-contracts/06-glossary-index.md
（仅保留正确版本）

ls docs/AirymaxRT/50-specifications
→ No such file or directory（目录已完全移除）
```

---

## P1-1/3：补充函数前缀三层定义

### 问题描述

`06-iron9-shared-model.md` 描述了 IRON-9 v2 三层共享模型（[SC]/[SS]/[IND]），但未明确函数前缀的三层定义。需补充 `airy_*`/`are_*`/`agentrt_*` 三层前缀说明，并注明 `agentrt_*` 不使用、`agentos_*`/`airymaxos_*` 已废弃。

### 修改文件

#### `10-architecture/06-iron9-shared-model.md`

- **新增章节**：`### 3.12 函数前缀三层定义`（插入于 §3.11 BPF struct_ops 之后、§4 agentrt 侧落地约束之前）
- **新增内容**：
  - 函数前缀与共享层级对齐原则说明
  - 5 行前缀定义表（`airy_*` / `are_*` / `agentrt_*` 不使用 / `agentos_*` 已废弃 / `airymaxos_*` 已废弃）
  - 4 条关键约束：
    1. [SC] 共享契约层与应用层共用 `airy_*` 前缀
    2. 标准 ABI 层使用 `are_*` 前缀（ARE = AiRtymax Engine/ABI）
    3. 禁止使用 `agentrt_*` 前缀（避免与仓库名混淆）
    4. `agentos_*` 与 `airymaxos_*` 已废弃（禁止兼容别名头、禁止双轨制）
  - SSoT 声明（引用 AirymaxOS `coding_conventions.md` Part IV §4.4.2）

### 设计说明

| 前缀 | 所属层级 | 用途 |
|------|---------|------|
| `airy_*` | [SC] 共享契约层 + 应用层 | 共享头文件结构体/宏/枚举 + 应用层函数 |
| `are_*` | 标准 ABI 层 | 对外发布的稳定 ABI 接口（SDK 公开符号） |
| ~~`agentrt_*`~~ | — | **不使用**（避免与仓库名混淆） |
| ~~`agentos_*`~~ | — | **已废弃**（0.1.1 改名前遗留） |
| ~~`airymaxos_*`~~ | — | **已废弃**（AirymaxOS 子仓早期方案） |

### 验证

```
Grep "函数前缀三层定义" 06-iron9-shared-model.md → 1 匹配（第 260 行，§3.12 标题）
Grep "airy_\*.*are_\*" 06-iron9-shared-model.md → 匹配（前缀定义表）
Grep "agentrt_\*.*不使用" 06-iron9-shared-model.md → 1 匹配（第 268 行）
Grep "agentos_\*.*已废弃" 06-iron9-shared-model.md → 1 匹配（第 269 行）
Grep "airymaxos_\*.*已废弃" 06-iron9-shared-model.md → 1 匹配（第 270 行）
```

---

## 约束遵守确认

| 约束 | 遵守情况 |
|------|---------|
| 仅修改 `docs/AirymaxRT/` 文件 | ✅ 所有修改均在 `docs/AirymaxRT/` 范围内 |
| 不修改源码 | ✅ 未触及任何 `.c`/`.h` 源文件 |
| 不修改闭源文档 | ✅ 修复日志写入 `docs-closed/`（仅新增日志，未修改闭源文档内容） |
| 不修改 `docs/AirymaxOS/` | ✅ `50-engineering-standards/120-cross-project-code-sharing.md`（符号链接指向 AirymaxOS）未修改，仅引用 |
| 使用 Edit 工具精确修改 | ✅ 所有文本修改使用 Edit 工具，删除使用 DeleteFile 工具 |
| Grep 验证 | ✅ 每项修复均通过 Grep 验证 |

---

## 修改文件总清单

| # | 文件路径 | 修改类型 | P1 编号 |
|---|---------|---------|---------|
| 1 | `docs/AirymaxRT/10-architecture/01-system-architecture.md` | 编辑 | P1-5, P1-6 |
| 2 | `docs/AirymaxRT/10-architecture/30-kernel/02-c-language-boundary.md` | 编辑 | P1-5, P1-11 |
| 3 | `docs/AirymaxRT/10-architecture/40-philosophy/01-design-philosophy.md` | 编辑 | P1-5 |
| 4 | `docs/AirymaxRT/20-modules/10-contracts/05-logging-format.md` | 编辑 | P1-5 |
| 5 | `docs/AirymaxRT/10-architecture/60-diagrams/03-overall-architecture.drawio` | 编辑 | P1-5 |
| 6 | `docs/AirymaxRT/10-architecture/06-iron9-shared-model.md` | 编辑（新增 §3.12） | P1-1/3 |
| 7 | `docs/AirymaxRT/50-specifications/10-contracts/06-glossary-index.md` | 删除 | P1-13 |
| 8 | `docs/AirymaxRT/50-specifications/10-contracts/` | 删除空目录 | P1-13 |
| 9 | `docs/AirymaxRT/50-specifications/` | 删除空目录 | P1-13 |

**统计**：编辑 6 个文件，删除 1 个文件 + 2 个空目录

---

## 遗留问题（非 P1 范围，移交后续处理）

| 问题 | 级别 | 说明 |
|------|------|------|
| `06-iron9-shared-model.md` §2.1 [SC] 头文件清单第 1 项 `bpf_struct_ops.h` | P0 | 不在 P1 修复范围，移交 P0 处理 |
| `06-iron9-shared-model.md` §3.8 第 214 行注释 `/* 成功（替代 AIRY_EOK） */` 递归引用 | P2 | 不在 P1 修复范围，移交 P2 处理 |

---

**维护者**： Airymax 架构委员会\
**最后更新**： 2026-07-13
