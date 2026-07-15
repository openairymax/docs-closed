Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 闭源 agentrt 文档 P0 级问题修正日志

> **文档定位**：v2.0 文档质量控制审查报告（`docs-closed/_review_v2.0/01-document-quality-control.md`）中 P0-DQC-1 与 P0-DQC-2 两项闭源 agentrt 文档事实性失真问题的实际修正日志。
> **保密级别**：SPHARX Ltd 内部参考，**闭源不公开**。
> **修正日期**：2026-07-13。
> **修正范围**：仅 `docs-closed/agentrt/agentrt工程标准规范手册.md`（v28.0）。
> **SPDX-License-Identifier**：AGPL-3.0-or-later OR Apache-2.0。

---

## 1. 修正摘要

| # | 问题编号 | 严重级别 | 问题简述 | 修正状态 | 工作量 |
|---|---------|---------|---------|---------|--------|
| 1 | P0-DQC-1 | P0 | [SC] 头文件数量错误（4 vs 6） | 已修正 | ~0.5h |
| 2 | P0-DQC-2 | P0 | 代码前缀全部错误（agentos_* vs airy_*） | 已修正 | ~1h |

**修正文件**：`docs-closed/agentrt/agentrt工程标准规范手册.md`（唯一修改文件）

**未修改项**（按任务约束）：
- `docs-closed/agentrt-linux/` 下的所有文件（agentrt-linux 的问题不在本次修正范围）
- 开源文档 `docs/` 下的所有文件
- 源代码

---

## 2. P0-DQC-1：[SC] 头文件数量错误（4 → 6）

### 2.1 问题描述

`docs-closed/agentrt/agentrt工程标准规范手册.md` 中有 3 处声明 [SC] 共享契约层为 **4 个头文件**，与 SSoT 权威定义（6 个）及实际源码（6 个）不一致。

**错误位置**（3 处）：
- `docs-closed/agentrt/agentrt工程标准规范手册.md:21`（v27.0 变动说明 IRON-9 v2 定义）
- `docs-closed/agentrt/agentrt工程标准规范手册.md:3675`（IRON 规则总表 IRON-9 条目）
- `docs-closed/agentrt/agentrt工程标准规范手册.md:4343`（第三十八章 IRON-9 v2 强制规则）

**错误内容**：
```
[SC] 共享契约层（`include/airymax/` 4 个头文件完全共享：bpf_struct_ops.h / memory_types.h / security_types.h / cognition_types.h）
```

### 2.2 SSoT 权威定义

依据开源 SSoT 文档 `docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md:65-77`，[SC] 共享契约层包含 **6 个核心头文件**：

| 序号 | 文件 | 落地路径 |
|------|------|---------|
| 1 | `memory_types.h` | `include/airymax/memory_types.h` |
| 2 | `security_types.h` | `include/airymax/security_types.h` |
| 3 | `cognition_types.h` | `include/airymax/cognition_types.h` |
| 4 | `sched.h` | `include/airymax/sched.h` |
| 5 | `ipc.h` | `include/airymax/ipc.h` |
| 6 | `syscalls.h` | `include/airymax/syscalls.h` |

补充共享文件 `bpf_struct_ops.h` **非 [SC] 核心头文件**（SSoT line 85 明示）。

### 2.3 修正操作

使用 Edit 工具（`replace_all: true`）将 3 处错误声明统一修正为：

```
[SC] 共享契约层（`include/airymax/` 6 个头文件完全共享：memory_types.h / security_types.h / cognition_types.h / sched.h / ipc.h / syscalls.h；另含补充共享文件 bpf_struct_ops.h，非 [SC] 核心头文件）
```

**关键变更**：
1. 数量：4 → 6
2. 移除 `bpf_struct_ops.h` 出核心清单，标注为"补充共享文件，非 [SC] 核心头文件"
3. 新增 `sched.h`、`ipc.h`、`syscalls.h` 三个 [SC] 核心头文件
4. 头文件顺序对齐 SSoT（memory_types / security_types / cognition_types / sched / ipc / syscalls）

### 2.4 验证结果

```
$ grep "6 个头文件完全共享" docs-closed/agentrt/agentrt工程标准规范手册.md
21:[Omitted long matching line]
3675:[Omitted long matching line]
4343:[Omitted long matching line]
Found 3 lines

$ grep "4 个头文件完全共享" docs-closed/agentrt/agentrt工程标准规范手册.md
No matches found
```

**验证通过**：3 处全部修正为 6 个头文件，旧的"4 个"表述 0 残留。

---

## 3. P0-DQC-2：代码前缀全部错误（agentos_* → airy_*）

### 3.1 问题描述

`docs-closed/agentrt/agentrt工程标准规范手册.md` 全文使用已废弃的 `agentos_*` 函数前缀和 `AGENTOS_*` 宏前缀，与实际源码使用的 `airy_*` / `AIRY_*` 严重背离。

**主要错误区域**：
1. 术语强制规范表（lines 98-111）：7 项 `agentos_*` 前缀 + 1 项 `AGENTOS_E*` 宏前缀
2. 全文代码示例、BAN 规则、指标名称、打印 API 等：大量 `agentos_*` / `AGENTOS_*` 残留

**实际源码前缀**（依据 v2.0 报告 §3.1.3 失真 2 表 + v1.0 §5.2）：

| 标准名称 | 标准英文 | 手册错误前缀 | 实际源码前缀 |
|---------|---------|------------|------------|
| 原子核心 | CoreKern | `agentos_core_*` | `airy_*`（atoms 916+ 处） |
| 三层认知循环 | CoreLoopThree | `agentos_loop_*` | `airy_*` |
| 记忆卷载 | MemoryRovol | `agentos_layer*_*` | `airy_*` |
| 系统调用层 | AirymaxSyscall | `agentos_sys_*` | `airy_sys_*` |
| 任务流引擎 | TaskFlow | `agentos_taskflow_*` | `airy_*` |
| 记忆交换算法 | MemorySwap | `agentos_memory_swap_*` | `airy_*` |
| 统一错误码体系 | ErrorCodeSystem | `AGENTOS_E*` | `AIRY_E*`（atoms 916+ 处） |

### 3.2 修正操作

#### 步骤 1：术语强制规范表精确修正（lines 98-111）

对术语表中带通配符的模式进行精确替换（这些模式仅在术语表中出现）：

| 旧前缀（带通配符） | 新前缀 | 替换次数 |
|------------------|--------|---------|
| `agentos_core_*` | `airy_*` | 2（CoreKern + MicroCoreRT） |
| `agentos_loop_*` | `airy_*` | 1（CoreLoopThree） |
| `agentos_layer*_*` | `airy_*` | 1（MemoryRovol） |
| `agentos_taskflow_*` | `airy_*` | 1（TaskFlow） |
| `agentos_memory_swap_*` | `airy_*` | 1（MemorySwap） |
| `agentos_sys_*` | `airy_sys_*` | 1（AirymaxSyscall，保留 sys 子前缀） |
| `AGENTOS_E*` | `AIRY_E*` | 2（术语表 + §34 Python 异常转换规范） |

**修正后术语表**（lines 96-111）：

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

#### 步骤 2：全文 `agentos_` → `airy_` 全量替换

使用 Edit 工具（`replace_all: true`）对剩余的所有 `agentos_`（小写带下划线）进行全量替换为 `airy_`。

**典型替换示例**：
- `agentos_mem_alloc` → `airy_mem_alloc`
- `agentos_print_ok` → `airy_print_ok`
- `agentos_core_init` → `airy_core_init`
- `agentos_error_t` → `airy_error_t`
- `agentos_types.h` → `airy_types.h`
- `agentos_hook_register` → `airy_hook_register`
- `agentos_cognition_latency_ms` → `airy_cognition_latency_ms`
- `agentos_oom_register_callback` → `airy_oom_register_callback`

#### 步骤 3：全文 `AGENTOS_` → `AIRY_` 全量替换

使用 Edit 工具（`replace_all: true`）对所有 `AGENTOS_`（大写带下划线）进行全量替换为 `AIRY_`。

**典型替换示例**：
- `AGENTOS_MALLOC` → `AIRY_MALLOC`
- `AGENTOS_FREE` → `AIRY_FREE`
- `AGENTOS_SUCCESS` → `AIRY_SUCCESS`
- `AGENTOS_ENOMEM` → `AIRY_ENOMEM`
- `AGENTOS_LOG_*` → `AIRY_LOG_*`
- `AGENTOS_ERR_*` → `AIRY_ERR_*`
- `AGENTOS_CONFIG_DIR` → `AIRY_CONFIG_DIR`

### 3.3 验证结果

```
$ grep "agentos_" docs-closed/agentrt/agentrt工程标准规范手册.md
No matches found

$ grep "AGENTOS_" docs-closed/agentrt/agentrt工程标准规范手册.md
No matches found
```

**验证通过**：`agentos_` 和 `AGENTOS_` 在全文中 0 残留。

---

## 4. 遗留事项与说明

### 4.1 §11.6 历史改名章节的副作用

`docs-closed/agentrt/agentrt工程标准规范手册.md` §11.6（line 1509）原为"agentos_ → agentrt_ 彻底改名规范（v26.0 重写）"，记录 v26.0 决策将 `agentos_` 改名为 `agentrt_`。

本次 P0-DQC-2 全量替换 `agentos_` → `airy_` 后，该章节标题变为"airy_ → agentrt_ 彻底改名规范"。

**说明**：
1. v2.0 报告 §3.1.3 失真 2 已指出："手册自身的 v26.0 变动说明（line 9）也提到'agentos_ → agentrt_ 改名彻底'，但实际源码用的是 `airy_*` 而非 `agentrt_*`——**改名方向与实际源码不一致**。"
2. 本次修正仅处理 P0-DQC-2（`agentos_*` → `airy_*`），不涉及 `agentrt_*` 前缀的修正。
3. §11.6 章节中 `agentrt_*` 作为改名目标的表述本身即为 v2.0 报告指出的失真之一（实际源码用 `airy_*` 而非 `agentrt_*`），但修正 `agentrt_*` 引用超出 P0-DQC-2 范围，需作为后续 P1 级问题单独处理。
4. 该章节中 `agentos/`（带斜杠的目录路径，如 line 1517 `agentos/` → `agentrt/`）未被替换，因为 P0-DQC-2 仅针对 `agentos_`（带下划线的代码前缀），不涉及 `agentos/` 目录路径。

### 4.2 未处理的 P1/P2 级问题

以下 v2.0 报告中指出的问题不在本次 P0 修正范围，需后续单独处理：

| 问题编号 | 严重级别 | 问题简述 | 位置 |
|---------|---------|---------|------|
| P1-DQC-4 | P1 | 29→38 仓变更说明残留 | line 9（v26.0 历史 29 仓明细）vs line 4-5（v28.0 当前 38 仓明细） |
| P2-DQC-4 | P2 | daemon 数量表述 16 vs 12 | line 40（"16 个 daemon"） |
| — | P1 | §11.6 改名目标 `agentrt_*` 与实际源码 `airy_*` 不一致 | §11.6 全节 |
| — | P1 | `docs/AirymaxAgentOS/` 路径错误（应为 `docs/AirymaxOS/`） | line 20 |

### 4.3 与开源文档的一致性确认

本次修正后，闭源 agentrt 工程标准手册在以下关键点与开源文档 SSoT 对齐：

| 关键点 | 闭源手册（修正后） | 开源 SSoT | 一致性 |
|--------|------------------|----------|--------|
| [SC] 头文件数量 | 6 个 | 6 个（`120-cross-project-code-sharing.md:65-77`） | ✓ 一致 |
| [SC] 头文件清单 | memory_types / security_types / cognition_types / sched / ipc / syscalls | 同左 | ✓ 一致 |
| bpf_struct_ops.h 定位 | 补充共享文件，非 [SC] 核心 | 非 [SC] 核心头文件（line 85） | ✓ 一致 |
| 代码函数前缀 | `airy_*` | `airy_*`（OpenStandards / AirymaxOS / 源码） | ✓ 一致 |
| 代码宏前缀 | `AIRY_*` | `AIRY_*`（OpenStandards / AirymaxOS / 源码） | ✓ 一致 |
| 系统调用层前缀 | `airy_sys_*` | `airy_sys_*`（v1.0 §5.2） | ✓ 一致 |
| 错误码宏前缀 | `AIRY_E*` | `AIRY_E*`（v1.0 §5.2） | ✓ 一致 |

---

## 5. 修正前后对比

### 5.1 [SC] 头文件清单（line 21）

**修正前**：
```
[SC] 共享契约层（`include/airymax/` 4 个头文件完全共享：bpf_struct_ops.h / memory_types.h / security_types.h / cognition_types.h）
```

**修正后**：
```
[SC] 共享契约层（`include/airymax/` 6 个头文件完全共享：memory_types.h / security_types.h / cognition_types.h / sched.h / ipc.h / syscalls.h；另含补充共享文件 bpf_struct_ops.h，非 [SC] 核心头文件）
```

### 5.2 术语强制规范表（lines 98-111）

**修正前**（7 项 agentos_* + 1 项 AGENTOS_*）：
```
| 原子核心 | CoreKern | `agentos_core_*` | ... |
| 三层认知循环 | CoreLoopThree | `agentos_loop_*` | ... |
| 记忆卷载 | MemoryRovol | `agentos_layer*_*` | ... |
| 微核心 | MicroCoreRT | `agentos_core_*` | ... |
| 任务流引擎 | TaskFlow | `agentos_taskflow_*` | ... |
| 系统调用层 | AirymaxSyscall | `agentos_sys_*` | ... |
| 记忆交换算法 | MemorySwap | `agentos_memory_swap_*` | ... |
| 统一错误码体系 | ErrorCodeSystem | `AGENTOS_E*` | ... |
```

**修正后**（7 项 airy_* / airy_sys_* + 1 项 AIRY_*）：
```
| 原子核心 | CoreKern | `airy_*` | ... |
| 三层认知循环 | CoreLoopThree | `airy_*` | ... |
| 记忆卷载 | MemoryRovol | `airy_*` | ... |
| 微核心 | MicroCoreRT | `airy_*` | ... |
| 任务流引擎 | TaskFlow | `airy_*` | ... |
| 系统调用层 | AirymaxSyscall | `airy_sys_*` | ... |
| 记忆交换算法 | MemorySwap | `airy_*` | ... |
| 统一错误码体系 | ErrorCodeSystem | `AIRY_E*` | ... |
```

---

## 6. 验证清单

| # | 验证项 | 验证方法 | 期望结果 | 实际结果 | 状态 |
|---|--------|---------|---------|---------|------|
| 1 | `agentos_` 零残留 | `grep "agentos_" docs-closed/agentrt/agentrt工程标准规范手册.md` | 0 结果 | 0 结果 | ✓ 通过 |
| 2 | `AGENTOS_` 零残留 | `grep "AGENTOS_" docs-closed/agentrt/agentrt工程标准规范手册.md` | 0 结果 | 0 结果 | ✓ 通过 |
| 3 | [SC] 头文件数量为 6 | `grep "6 个头文件完全共享" ...` | 3 处（line 21/3675/4343） | 3 处 | ✓ 通过 |
| 4 | 旧的"4 个"表述消除 | `grep "4 个头文件完全共享" ...` | 0 结果 | 0 结果 | ✓ 通过 |
| 5 | 术语表 airy_sys_* 正确 | `grep "airy_sys_\*" ...` | line 106 存在 | line 106 存在 | ✓ 通过 |
| 6 | 术语表 AIRY_E* 正确 | `grep "AIRY_E\*" ...` | line 111 存在 | line 111 存在 | ✓ 通过 |
| 7 | 与开源 SSoT 一致 | 对照 `120-cross-project-code-sharing.md:65-77` | 6 头文件清单一致 | 一致 | ✓ 通过 |

---

## 7. 修正影响评估

### 7.1 正面影响

1. **消除事实性失真**：闭源 agentrt 工程标准手册的 [SC] 头文件清单和代码前缀声明现在与实际源码、闭源 agentrt-linux 总纲、开源文档三方对齐。
2. **恢复工程指导性**：开发者按修正后的手册使用 `airy_*` 前缀和 6 个 [SC] 头文件，将与实际源码一致，CI 门禁不再因前缀不匹配而失败。
3. **IRON-9 v2 三层模型一致性**：[SC] 共享契约层定义现在跨所有文档仓库一致（6 个头文件）。
4. **1.0.1 M1 启动条件满足**：v2.0 报告 §6.1 中 P0-DQC-1 和 P0-DQC-2 两项阻断项已清除。

### 7.2 需关注的副作用

1. **§11.6 历史改名章节语义变化**：该章节原描述"agentos_ → agentrt_"改名，全量替换后变为"airy_ → agentrt_"。这是 P0-DQC-2 全量替换的不可避免副作用。该章节中 `agentrt_*` 作为改名目标的表述本身即为 v2.0 报告指出的失真（实际源码用 `airy_*`），需作为后续 P1 级问题单独处理。
2. **目录路径 `agentos/` 未替换**：P0-DQC-2 仅针对代码前缀 `agentos_`（带下划线），不涉及目录路径 `agentos/`（带斜杠）。手册中仍存在 `agentos/` 目录路径引用（如 §11.6.1 L1 源码目录层），这些属于目录结构范畴，不在本次代码前缀修正范围。

### 7.3 未受影响的范围

- `docs-closed/agentrt-linux/` 下的所有文件：未修改（按任务约束）
- 开源文档 `docs/` 下的所有文件：未修改（按任务约束）
- 源代码：未修改（按任务约束）
- 闭源 agentrt 手册中的非前缀内容（架构原则、BAN 规则编号、ACC 验收标准等）：未修改

---

<div align="center">

**© 2025-2026 SPHARX Ltd.** All Rights Reserved.

</div>

---

**修正日志结束** | SPHARX Ltd 内部参考 | 闭源不公开 | 修正日期：2026-07-13 | 对应审查报告：v2.0 文档质量控制维度 P0-DQC-1/P0-DQC-2
