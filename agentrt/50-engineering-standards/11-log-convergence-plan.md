Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 日志收敛计划

> **文档定位**：agentrt 用户态运行时日志收敛计划——将 agentrt 仓库现存的双轨日志统一为 `AIRY_LOG_*` 单一权威轨的迁移工程方案\
> **文档版本**：v2.0\
> **最后更新**：2026-08-14\
> **上级文档**：[agentrt 工程标准规范手册](agentrt工程标准规范手册.md)\
> **设计依据**：[09-sc-log-types-contract.md](../../docs/AirymaxOS/30-interfaces/09-sc-log-types-contract.md)（[SC] `log_types.h` 契约）+ [10-unify-design.md](../../docs/AirymaxOS/10-architecture/10-unify-design.md) §5（A-ULP 模块）+ C-06 冲突点消解

---

## SSoT 声明

> **单一权威源声明**：本文件是 **agentrt 日志统一收敛为 `AIRY_LOG_*` 单一轨** 的唯一权威源。收敛目标、迁移执行记录、CI 强制校验门槛均以本文件为唯一权威定义。
>
> `AIRY_LOG_*` 5 级日志枚举与 128B 记录格式的权威源为 AirymaxOS [09-sc-log-types-contract.md](../../docs/AirymaxOS/30-interfaces/09-sc-log-types-contract.md)（[SC] `log_types.h` 共享契约，agentrt 与 agentrt-linux 逐字节一致）。本收敛计划是 agentrt 侧对齐 A-ULP 模块（见 [10-unify-design.md](../../docs/AirymaxOS/10-architecture/10-unify-design.md) §5）C-06 冲突点消解的工程落地。

---

## §1 方向修正（2026-08-14）：统一为 AIRY_LOG_* 而非 LOG_*

### 1.1 方向修正背景

v1.0 版计划曾主张将 `AIRY_LOG_*` 收敛为 `LOG_*`，该方向经三重验证为**错误**：

1. **[SC] 契约**：[09-sc-log-types-contract.md](../../docs/AirymaxOS/30-interfaces/09-sc-log-types-contract.md) L16 明文规定"日志级别统一使用 `AIRY_LOG_*` 前缀（对齐 SSoT `log_types.h` L37-44）"，facility 统一使用 `AIRY_LOG_FAC_*` 前缀
2. **A-ULP 设计**：[10-unify-design.md](../../docs/AirymaxOS/10-architecture/10-unify-design.md) L229-230 定义 `AIRY_LOG_MAGIC` 与级别字段（`AIRY_LOG_DEBUG` ~ `AIRY_LOG_FATAL`）；L483 降级表明确 5 级为 `AIRY_LOG_*`
3. **agentrt-linux 设计方案**：`logger_d` 模块设计（[12-logger-daemon-module.md](../../docs/AirymaxOS/20-modules/12-logger-daemon-module.md)）错误码记录、facility 过滤、[DSL] 降级块全部使用 `AIRY_LOG_*`/`AIRY_LOG_FAC_*`

**结论（用户决策，2026-08-14）**：`AIRY_LOG_*` 是 agentrt 与 agentrt-linux（AirymaxOS）共享的权威日志命名，日志统一为 `AIRY_LOG_*`，设计冲突一律与 AirymaxOS 设计方案对齐。本计划 v2.0 起方向反转。

### 1.2 方向修正的文档联动

随方向反转同步修正的文档残留表述（A-ULP 文档侧，保证单一权威源一致）：

- [10-unify-design.md](../../docs/AirymaxOS/10-architecture/10-unify-design.md) C-06 冲突点："统一为 `LOG_*` 枚举" → "统一为 `AIRY_LOG_*` 枚举（对齐 [SC] log_types.h L37-44）"
- [12-logger-daemon-module.md](../../docs/AirymaxOS/20-modules/12-logger-daemon-module.md) §7.3 伪代码：`rec->level = LOG_ERROR/LOG_FATAL` → `AIRY_LOG_ERROR/AIRY_LOG_FATAL`
- [09-sc-log-types-contract.md](../../docs/AirymaxOS/30-interfaces/09-sc-log-types-contract.md) §7 版本历史 v1.0 条目：`LOG_DEBUG~LOG_FATAL` → `AIRY_LOG_DEBUG~AIRY_LOG_FATAL`

---

## §2 目标：将 agentrt 的双轨日志统一为 AIRY_LOG_*

### 2.1 双轨制现状（S-2 收敛前）

agentrt 仓库在历史演进中累积了三套并存的日志宏体系：

| 日志轨 | 宏前缀 | 来源 | 收敛前规模 | 处置 |
|--------|--------|------|-----------|------|
| 权威轨 | `AIRY_LOG_*` | [SC] `log_types.h` 共享契约 + agentrt observability/logger.h | ~913 处 | 保留，为收敛目标 |
| 旧轨 | `LOG_*` | agentrt 早期自研 logging.h | ~1131 处 | 全量迁移至 `AIRY_LOG_*` |
| 服务层轨 | `SVC_LOG_*` | svc_logger.h（服务层） | ~1273 处 | 保留，宏映射到 `AIRY_LOG_*` |

两套级别宏语义同构（`LOG_DEBUG` ↔ `AIRY_LOG_DEBUG`），但前缀割裂导致：

1. **跨端日志割裂**：agentrt（用户态）输出 `LOG_*`，AirymaxOS（内核态）输出 `AIRY_LOG_*`，Logger Daemon（见 [12-logger-daemon-module.md](../../docs/AirymaxOS/20-modules/12-logger-daemon-module.md)）需识别两套级别，归档检索复杂
2. **[SC] 契约违反**：`AIRY_LOG_*` 是 [SC] `log_types.h` 共享契约命名，agentrt 单独使用 `LOG_*` 等于绕过 [SC]，违反共享契约层双向 CI 验证
3. **认知负担**：开发者需记忆多套宏的等价关系，新增日志时随机选用，加剧双轨扩散

### 2.2 收敛目标

将 agentrt 全仓库 `LOG_*` 统一收敛为 `AIRY_LOG_*`，达成：

- **单一轨**：agentrt 与 AirymaxOS 共享 `AIRY_LOG_*` 单一日志枚举，经 [SC] `log_types.h` 物理共享（逐字节一致）
- **[SC] 对齐**：宏函数层收敛至唯一权威源 `commons/utils/observability/include/logger.h`
- **零语义损失**：收敛前后日志级别一一对应，无级别丢失或合并；`_T` 变体（trace）改名 `AIRY_LOG_*_T` 保留语义

### 2.3 收敛边界

| 范围 | 是否收敛 | 说明 |
|------|---------|------|
| agentrt 仓库 C/C++ 源码 | 是 | `LOG_*` → `AIRY_LOG_*`（S-2 已完成） |
| 服务层 `SVC_LOG_*` | 映射 | 宏保留，映射到 `AIRY_LOG_*` |
| agentrt 文档/注释中的 `LOG_*` 残留 | 是 | 与权威方向保持一致 |
| 第三方依赖日志 | 否 | 不修改第三方代码，通过 adapter 适配 |
| AirymaxOS 内核态 | 否 | 已是 `AIRY_LOG_*`，无需收敛 |

---

## §3 迁移执行记录（S-2，2026-08-14 完成）

收敛在 agentrt 0.1.2 Unify Design 规划（S-2 日志双轨收敛）中执行完毕：

### 3.1 调用点迁移

全仓 7 仓 128 文件 1134 处 `LOG_*(` → `AIRY_LOG_*(` 机械替换：

- atoms（42 文件）、daemons（24）、commons（21）、cupolas（12）、gateway（9）、protocols（28）
- `LOG_TRACE(` → `AIRY_LOG_DEBUG(`（trace 语义并入 DEBUG 级）
- 排除 `#define LOG_` 定义行、`SVC_LOG_*`、`AIRY_LOG_*` 前缀，无误伤
- `_T` trace 变体改名 `AIRY_LOG_*_T`（如 `AIRY_LOG_INFO_T(ctx, ...)`）

### 3.2 头文件收敛

| 头文件 | 处置 |
|--------|------|
| `commons/utils/observability/include/logger.h` | 权威宏源：`AIRY_LOG_LEVEL_*` 值宏 + `AIRY_LOG_DEBUG/INFO/WARN/ERROR/FATAL` 函数式宏（带 `#ifndef` 守卫），头部注释声明"S-2 收敛权威宏源" |
| `commons/utils/logging/include/logging.h` | 删除 `LOG_DEBUG/INFO/WARN/ERROR/FATAL` 宏、`LOG_IF`、`LOG_SAMPLE`；保留 `log_write`/`log_write_va`/`log_init` 函数层与 `log_level_t`；新增相对路径 `#include "../../observability/include/logger.h"` 引入权威宏 |
| `commons/utils/logging/include/svc_logger.h` | 删除 `LOG_TRACE~FATAL` 6 个旧宏；`LOG_*_T` → `AIRY_LOG_*_T`；`LOG_ERROR_RETURN` → `AIRY_LOG_ERROR_RETURN`、`LOG_CHECK` → `AIRY_LOG_CHECK`；`SVC_LOG_*` 保留并映射到 `AIRY_LOG_*` |
| `commons/utils/include/logging_compat.h` | 转发权威源：`#if __has_include("../observability/include/logger.h")` + 相对路径 include，保留 stderr fallback |

### 3.3 同名头遮蔽问题（关键回归）

`products/memoryrovol/include/logger.h` 在 `-I` 顺序中遮蔽权威 `observability/logger.h`（agentrt 源 `#include "logger.h"` 解析到 memoryrovol 的兼容映射头，不定义 `AIRY_LOG_*` 函数式宏）。修复：`logging.h`/`logging_compat.h` 改用**相对路径** include（不依赖 `-I` 顺序），注释说明遮蔽原因。回滚根 CMakeLists 的全局 observability 注入（正是该注入加剧遮蔽），改为各消费目标显式添加 include 路径（gateway/gateway_d/coreloopthree/tests）。

### 3.4 验证

- 库目标（airy_common/airy_core/airy_coreloopthree/airy_atoms）与最终目标（sched_d/hook_d/tool_d/think_d/airy_cli 等）全量构建通过
- 顺带修复 memoryrovol 既有链接遗留：`agentrt_memoryrovol` 声明 PRIVATE 链接 `airy_core`（源引用 `airy_time_monotonic_ns` 等 corekern 符号），使 CMake 将 core 排到 memoryrovol 之后，GNU ld 单遍扫描可回溯解析（此前 `--start-group` 因 INTERFACE 字符串项排到命令行末尾而不可靠，已弃用）

---

## §4 后续强制门槛（防回潮）

- **CI 禁止新增 `LOG_*(` 调用**：新增日志一律使用 `AIRY_LOG_*`，checkpatch 规则 `AIRY_LOG_ONLY`
- **`SVC_LOG_*` 仅服务层使用**：映射宏不得回流为独立轨
- **日志函数层**（`log_write`/`log_write_va`）保留为底层实现，宏层唯一权威为 `AIRY_LOG_*`

---

## §5 相关文档

- [agentrt 工程标准规范手册](agentrt工程标准规范手册.md) —— agentrt 工程标准上级文档
- [10-unify-design.md](../../docs/AirymaxOS/10-architecture/10-unify-design.md) —— Airymax Unify Design 总纲（A-ULP 模块 + C-06 冲突点）
- [09-sc-log-types-contract.md](../../docs/AirymaxOS/30-interfaces/09-sc-log-types-contract.md) —— `AIRY_LOG_*` 枚举与 128B 记录格式 [SC] 契约（唯一权威源）
- [05-ring-buffer-logging.md](../../docs/AirymaxOS/40-dataflows/05-ring-buffer-logging.md) —— Ring Buffer 日志数据流（消费侧）
- [12-logger-daemon-module.md](../../docs/AirymaxOS/20-modules/12-logger-daemon-module.md) —— Logger Daemon 模块设计
- [12-error-code-migration-plan.md](12-error-code-migration-plan.md) —— 错误码迁移计划（与本计划并行推进）

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. | 日志收敛计划 | v2.0 | 2026-08-14
