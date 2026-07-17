Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 日志收敛计划

> **文档定位**：agentrt 用户态运行时日志收敛计划——将 agentrt 仓库现存的 `AIRY_LOG_*` 双轨日志统一为 `LOG_*` 单一轨的迁移工程方案\
> **文档版本**：v1.0\
> **最后更新**：2026-07-17\
> **上级文档**：[agentrt 工程标准规范手册](agentrt工程标准规范手册.md)\
> **设计依据**：[15-comprehensive-correction-plan.md](../agentrt-linux/00-reviews/_review_v2.2/15-comprehensive-correction-plan.md) §4.2.2（ULPS 设计）+ §6 文档逐一检查 C-06（日志双轨制）

---

## SSoT 声明

> **单一权威源声明**：本文件是 **agentrt `AIRY_LOG_*` → `LOG_*` 日志收敛计划** 的唯一权威源。收敛目标、五阶段迁移流程（识别 → 别名 → 迁移 → 废弃 → 删除）、时间线、CI 强制校验门槛均以本文件为唯一权威定义。
>
> `LOG_*` 5 级日志枚举与 128B 记录格式的权威源为 AirymaxOS [09-sc-log-types-contract.md](../../docs/AirymaxOS/30-interfaces/09-sc-log-types-contract.md)（[SC] `log_types.h` 共享契约）。本收敛计划是 agentrt 侧对齐 ULPS 模块（见 [08-unify-design.md](../../docs/AirymaxOS/10-architecture/08-unify-design.md) §5）C-06 冲突点消解的工程落地。

---

## §1 目标：将 agentrt 的 AIRY_LOG_* 双轨日志统一为 LOG_*

### 1.1 双轨制现状

agentrt 仓库在历史演进中累积了两套并存的日志宏：

| 日志轨 | 宏前缀 | 来源 | 当前规模 | 问题 |
|--------|--------|------|---------|------|
| 旧轨 | `AIRY_LOG_*` | agentrt 早期自研 | ~1200 处调用 | 与 AirymaxOS `LOG_*` 不一致，跨端日志语义割裂 |
| 新轨 | `LOG_*` | ULPS 模块统一枚举（[SC] `log_types.h`） | ~300 处调用 | 与 AirymaxOS 共享 [SC] 契约，是收敛目标 |

两套宏的级别枚举不同：`AIRY_LOG_*` 采用 `AIRY_LOG_DEBUG/INFO/WARN/ERROR/FATAL`，`LOG_*` 采用 `LOG_DEBUG/INFO/WARN/ERROR/FATAL`（无 `AIRY_` 前缀，与 [SC] `log_types.h` 一致）。语义虽同构，但前缀差异导致：

1. **跨端日志割裂**：agentrt（用户态）输出 `AIRY_LOG_*`，AirymaxOS（内核态）输出 `LOG_*`，Logger Daemon（见 [12-logger-daemon-module.md](../../docs/AirymaxOS/20-modules/12-logger-daemon-module.md)）需识别两套 facility，归档检索复杂
2. **[SC] 契约违反**：`LOG_*` 是 [SC] `log_types.h` 共享契约，agentrt 单独使用 `AIRY_LOG_*` 等于绕过 [SC]，违反 OS-IRON-008（[SC] 共享契约层双向 CI 验证）
3. **认知负担**：开发者需记忆两套宏的等价关系，新增日志时随机选用，加剧双轨扩散

### 1.2 收敛目标

将 agentrt 全仓库 `AIRY_LOG_*` 统一收敛为 `LOG_*`，达成：

- **单一轨**：agentrt 与 AirymaxOS 共享 `LOG_*` 单一日志枚举，经 [SC] `log_types.h` 物理共享
- **[SC] 对齐**：agentrt 通过 `-I` 引用 `kernel/include/airymax/log_types.h`，与 AirymaxOS 逐字节一致
- **零语义损失**：收敛前后日志级别一一对应，无级别丢失或合并

### 1.3 收敛边界

| 范围 | 是否收敛 | 说明 |
|------|---------|------|
| agentrt 仓库 C/C++ 源码 | 是 | `AIRY_LOG_*` → `LOG_*` |
| agentrt 仓库 Rust 源码 | 是 | `airy_log_*!` 宏 → `log_*!` 宏 |
| agentrt 仓库 Go 源码 | 是 | `airy.Log*` → `log.*` |
| agentrt 文档/注释中的 `AIRY_LOG_*` | 是 | 统一为 `LOG_*` |
| 第三方依赖日志 | 否 | 不修改第三方代码，通过 adapter 适配 |
| AirymaxOS 内核态 | 否 | 已是 `LOG_*`，无需收敛 |

---

## §2 迁移阶段：识别 → 别名 → 迁移 → 废弃 → 删除

### 2.1 阶段总览

收敛采用五阶段渐进迁移，每阶段独立可回退，CI 在各阶段设置强制门槛：

```
阶段 1 识别    →  阶段 2 别名    →  阶段 3 迁移    →  阶段 4 废弃    →  阶段 5 删除
（盘点）        （兼容垫片）       （逐文件替换）      （标记废弃）       （移除旧宏）
```

### 2.2 阶段 1：识别（Identify）

**目标**：全量盘点 `AIRY_LOG_*` 调用点，建立迁移清单。

**动作**：
- 使用 `grep -rn "AIRY_LOG_" --include="*.{c,h,rs,go}"` 扫描全仓库
- 按子系统/目录归类，生成 `log-convergence-inventory.csv`，含文件、行号、宏名、对应 `LOG_*` 目标
- 统计各语言分布：C/C++、Rust、Go

**CI 门槛**：无（识别阶段不修改代码）

**产出**：迁移清单 CSV + 统计报告

### 2.3 阶段 2：别名（Alias）

**目标**：建立 `AIRY_LOG_*` → `LOG_*` 的兼容垫片，使两套宏等价，为逐文件迁移提供安全网。

**动作**：
- 在 `include/airymax/log_compat.h`（agentrt 侧兼容头）定义别名宏：

```c
/* log_compat.h —— 阶段 2 兼容垫片 */
#ifndef AIRY_LOG_COMPAT_H
#define AIRY_LOG_COMPAT_H
#include <airymax/log_types.h>   /* [SC] 共享契约 */

#define AIRY_LOG_DEBUG   LOG_DEBUG
#define AIRY_LOG_INFO    LOG_INFO
#define AIRY_LOG_WARN    LOG_WARN
#define AIRY_LOG_ERROR   LOG_ERROR
#define AIRY_LOG_FATAL   LOG_FATAL
/* 日志输出函数别名 */
#define airy_log_debug   log_debug
#define airy_log_info    log_info
#define airy_log_warn    log_warn
#define airy_log_error   log_error
#define airy_log_fatal   log_fatal
#endif
```

- Rust/Go 侧建立等价 `pub use` / type alias

**CI 门槛**：`AIRY_LOG_*` 与 `LOG_*` 必须编译期等价（同一枚举值），通过 `static_assert(AIRY_LOG_DEBUG == LOG_DEBUG)` 校验

**产出**：兼容垫片头文件，全仓库编译通过

### 2.4 阶段 3：迁移（Migrate）

**目标**：按迁移清单逐文件将 `AIRY_LOG_*` 机械替换为 `LOG_*`，移除对 `log_compat.h` 的依赖。

**动作**：
- 按目录分批 PR（每个子系统一个 PR，避免巨型 diff）
- 机械替换：`AIRY_LOG_DEBUG` → `LOG_DEBUG`，`airy_log_debug(...)` → `log_debug(...)`
- 替换后移除该文件的 `#include <airymax/log_compat.h>`
- 每 PR 通过完整 CI（编译 + 测试 + 日志级别校验）

**CI 门槛**：
- 新增 `AIRY_LOG_*` 调用 = 0（checkpatch 规则 `AIRY_LOG_FORBIDDEN`）
- 已迁移文件不得重新引入 `log_compat.h`

**产出**：`AIRY_LOG_*` 调用点归零

### 2.5 阶段 4：废弃（Deprecate）

**目标**：将 `AIRY_LOG_*` 宏标记为废弃，保留但产生编译警告，防止遗漏调用点回潮。

**动作**：
- `log_compat.h` 中所有 `AIRY_LOG_*` 宏追加 `__attribute__((deprecated("use LOG_* instead")))`
- Rust 侧追加 `#[deprecated]`，Go 侧追加 `// Deprecated:` 注释
- 文档中 `AIRY_LOG_*` 标注"已废弃，使用 `LOG_*`"

**CI 门槛**：
- 编译警告中 `AIRY_LOG_* deprecated` 计数 = 0（即无任何文件仍引用 `log_compat.h`）
- 若计数 > 0，CI 失败，要求对应文件完成迁移

**产出**：`log_compat.h` 仅剩废弃声明，无实际引用

### 2.6 阶段 5：删除（Delete）

**目标**：物理删除 `AIRY_LOG_*` 宏与 `log_compat.h`，双轨制彻底终结。

**动作**：
- 删除 `include/airymax/log_compat.h`
- 删除 Rust/Go 侧别名声明
- 更新文档：移除所有 `AIRY_LOG_*` 引用

**CI 门槛**：
- `grep -rn "AIRY_LOG_" --include="*.{c,h,rs,go}"` 输出为空
- `log_compat.h` 不存在
- CI 规则 `AIRY_LOG_FORBIDDEN` 升级为 error（此前为 warning）

**产出**：单一 `LOG_*` 轨，[SC] `log_types.h` 成为唯一权威源

---

## §3 时间线：与 agentrt-linux Phase 2 同步

### 3.1 同步原则

日志收敛与 agentrt-linux（AirymaxOS）开发阶段同步推进，确保 agentrt 与 AirymaxOS 在 Phase 2 结束时共享同一 `LOG_*` [SC] 契约。同步锚点为 AirymaxOS 版本基线（ADR-013：1.x.x 锁定 Linux 6.6 LTS）。

### 3.2 阶段时间线

| 收敛阶段 | 对应 AirymaxOS 阶段 | 时间窗口 | 里程碑 |
|---------|-------------------|---------|--------|
| 阶段 1 识别 | Phase 1 尾声（1.0.1 开发） | T0 ~ T0+2w | 迁移清单 CSV 冻结 |
| 阶段 2 别名 | Phase 2 启动（1.0.1 锁定） | T0+2w ~ T0+4w | 兼容垫片合入，CI static_assert 生效 |
| 阶段 3 迁移 | Phase 2 中期（1.0.1 ~ 1.x.x+） | T0+4w ~ T0+16w | `AIRY_LOG_*` 调用点归零 |
| 阶段 4 废弃 | Phase 2 后期（1.x.x+） | T0+16w ~ T0+20w | deprecated 警告计数归零 |
| 阶段 5 删除 | Phase 2 收尾（2.x.x 启动前） | T0+20w ~ T0+24w | `log_compat.h` 物理删除 |

### 3.3 与 AirymaxOS Phase 2 的协同

agentrt-linux Phase 2（1.x.x+ 阶段）的核心任务是 VFS / 网络栈 / 驱动框架用户态化（见 [03-microkernel-strategy.md](../../docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) §9.1）。此阶段 ULPS 模块的 Ring Buffer + Logger Daemon 已稳定（见 [05-ring-buffer-logging.md](../../docs/AirymaxOS/40-dataflows/05-ring-buffer-logging.md)），是 agentrt 侧收敛日志的最佳窗口：

- **阶段 2 别名**与 Phase 2 启动同步：agentrt-linux Phase 2 引入的 12 daemons 全部使用 `LOG_*`，agentrt 侧别名垫片确保新旧代码共存期无断裂
- **阶段 3 迁移**与 Phase 2 中期同步：agentrt 侧逐子系统迁移，与 agentrt-linux 用户态服务化并行，避免冲突
- **阶段 5 删除**在 2.x.x 启动前完成：2.x.x 将升级 Linux 7.1 基线（ADR-013），届时 [SC] `log_types.h` 可能演进，双轨制必须在基线升级前终结，避免迁移负担叠加

### 3.4 风险与回退

| 风险 | 影响 | 缓解 |
|------|------|------|
| 阶段 3 迁移中发现 `AIRY_LOG_*` 有非标语义（如带额外参数） | 阻塞机械替换 | 阶段 1 识别时标记异常项，单独设计映射 |
| AirymaxOS Phase 2 延期 | 阶段 4/5 顺延 | 收敛各阶段独立，可暂停于任一阶段，兼容垫片保证可用 |
| 第三方依赖输出 `AIRY_LOG_*` | 阶段 5 无法彻底清零 | 第三方代码不修改，通过 adapter 在调用边界转换 |

每阶段设置 1 周缓冲期，若 CI 门槛未达则回退至上一阶段，不计为阻塞失败。

---

## §4 相关文档

- [agentrt 工程标准规范手册](agentrt工程标准规范手册.md) —— agentrt 工程标准上级文档
- [08-unify-design.md](../../docs/AirymaxOS/10-architecture/08-unify-design.md) —— Airymax Unify Design 总纲（ULPS 模块 + C-06 冲突点）
- [09-sc-log-types-contract.md](../../docs/AirymaxOS/30-interfaces/09-sc-log-types-contract.md) —— `LOG_*` 枚举与 128B 记录格式 [SC] 契约（收敛目标）
- [05-ring-buffer-logging.md](../../docs/AirymaxOS/40-dataflows/05-ring-buffer-logging.md) —— Ring Buffer 日志数据流（消费侧）
- [12-logger-daemon-module.md](../../docs/AirymaxOS/20-modules/12-logger-daemon-module.md) —— Logger Daemon 模块设计
- [12-error-code-migration-plan.md](12-error-code-migration-plan.md) —— 错误码迁移计划（与本计划并行推进）

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. | 日志收敛计划 | v1.0 | 2026-07-17
