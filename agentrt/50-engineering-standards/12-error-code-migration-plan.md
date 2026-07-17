Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 错误码迁移计划

> **文档定位**：agentrt 用户态运行时错误码迁移计划——将 agentrt 仓库现存的 `AIRY_ERR_*` 双轨错误码统一为 `AIRY_E*` 单一轨的迁移工程方案\
> **文档版本**：v1.0\
> **最后更新**：2026-07-17\
> **上级文档**：[agentrt 工程标准规范手册](agentrt工程标准规范手册.md)\
> **设计依据**：[15-comprehensive-correction-plan.md](../agentrt-linux/00-reviews/_review_v2.2/15-comprehensive-correction-plan.md) §4.2.1（UEF 设计）+ §6 文档逐一检查 C-05（错误码双轨制）

---

## SSoT 声明

> **单一权威源声明**：本文件是 **agentrt `AIRY_ERR_*` → `AIRY_E*` 错误码迁移计划** 的唯一权威源。迁移目标、五阶段迁移流程（识别 → 别名 → 迁移 → 废弃 → 删除）、时间线、CI 强制校验门槛均以本文件为唯一权威定义。
>
> `AIRY_E*` 错误码（Error 负数空间）与 `AIRY_FAULT_*` 故障码（Fault 正数空间）的权威源为 AirymaxOS [08-sc-error-contract.md](../../docs/AirymaxOS/30-interfaces/08-sc-error-contract.md)（[SC] `error.h` 共享契约）。本迁移计划是 agentrt 侧对齐 UEF 模块（见 [08-unify-design.md](../../docs/AirymaxOS/10-architecture/08-unify-design.md) §5）C-05 冲突点消解的工程落地。

---

## §1 目标：将 agentrt 的 AIRY_ERR_* 双轨错误码统一为 AIRY_E*

### 1.1 双轨制现状

agentrt 仓库在历史演进中累积了两套并存的错误码命名：

| 错误码轨 | 前缀 | 来源 | 当前规模 | 问题 |
|---------|------|------|---------|------|
| 旧轨 | `AIRY_ERR_*` | agentrt 早期自研 | ~900 处引用 | 与 AirymaxOS `AIRY_E*` 不一致，跨端错误码割裂 |
| 新轨 | `AIRY_E*` | UEF 模块统一错误码（[SC] `error.h`） | ~250 处引用 | 与 AirymaxOS 共享 [SC] 契约，是迁移目标 |

两套错误码的语义模型不同：

- `AIRY_ERR_*`：采用正向整数枚举（`AIRY_ERR_NOENT=1`、`AIRY_ERR_PERM=2`...），调用方需自行取负返回
- `AIRY_E*`：采用负数返回值（`AIRY_ENOENT=-2`、`AIRY_EPERM=-1`...），直接作为函数返回值，对齐 Linux errno 语义（见 [08-sc-error-contract.md](../../docs/AirymaxOS/30-interfaces/08-sc-error-contract.md)）

双轨并存导致：

1. **跨端错误码割裂**：agentrt（用户态）返回 `AIRY_ERR_*` 正数，AirymaxOS（内核态）返回 `AIRY_E*` 负数，跨 IPC 边界传递时需转换，易出错
2. **[SC] 契约违反**：`AIRY_E*` 是 [SC] `error.h` 共享契约，agentrt 单独使用 `AIRY_ERR_*` 等于绕过 [SC]，违反 OS-IRON-008（[SC] 共享契约层双向 CI 验证）
3. **语义混淆**：`AIRY_ERR_NOENT`（正数）与 `AIRY_ENOENT`（负数）并存，开发者易误用，导致返回值符号错误

### 1.2 迁移目标

将 agentrt 全仓库 `AIRY_ERR_*` 统一迁移为 `AIRY_E*`，达成：

- **单一轨**：agentrt 与 AirymaxOS 共享 `AIRY_E*` 单一错误码空间，经 [SC] `error.h` 物理共享
- **[SC] 对齐**：agentrt 通过 `-I` 引用 `kernel/include/airymax/error.h`，与 AirymaxOS 逐字节一致
- **errno 语义统一**：所有错误返回值为负数，对齐 Linux errno 习惯，消除正/负数混淆
- **零语义损失**：每个 `AIRY_ERR_*` 一一映射到 `AIRY_E*`，无错误码丢失或合并

### 1.3 迁移边界

| 范围 | 是否迁移 | 说明 |
|------|---------|------|
| agentrt 仓库 C/C++ 源码 | 是 | `AIRY_ERR_*` → `AIRY_E*`，返回值取负 |
| agentrt 仓库 Rust 源码 | 是 | `AiryErr*` 枚举 → `AiryE*` 枚举 |
| agentrt 仓库 Go 源码 | 是 | `airy.Err*` 常量 → `airy.E*` 常量 |
| agentrt 文档/注释中的 `AIRY_ERR_*` | 是 | 统一为 `AIRY_E*` |
| 第三方依赖错误码 | 否 | 不修改第三方代码，通过 adapter 在边界转换 |
| AirymaxOS 内核态 | 否 | 已是 `AIRY_E*`，无需迁移 |
| `AIRY_FAULT_*` 故障码 | 否 | 故障码是 UEF 的正数空间，不在本迁移范围（已是统一轨） |

### 1.4 映射规则

`AIRY_ERR_*` → `AIRY_E*` 的核心映射（完整映射表见 [08-sc-error-contract.md](../../docs/AirymaxOS/30-interfaces/08-sc-error-contract.md)）：

| 旧轨（正数） | 新轨（负数） | 语义 |
|-------------|------------|------|
| `AIRY_ERR_PERM` (2) | `AIRY_EPERM` (-1) | 权限不足 |
| `AIRY_ERR_NOENT` (1) | `AIRY_ENOENT` (-2) | 不存在 |
| `AIRY_ERR_INVAL` (3) | `AIRY_EINVAL` (-22) | 无效参数 |
| `AIRY_ERR_NOMEM` (4) | `AIRY_ENOMEM` (-12) | 内存不足 |
| `AIRY_ERR_BUSY` (5) | `AIRY_EBUSY` (-16) | 资源忙 |
| `AIRY_ERR_AGAIN` (6) | `AIRY_EAGAIN` (-11) | 重试 |
| `AIRY_ERR_TIMEDOUT` (7) | `AIRY_ETIMEDOUT` (-110) | 超时 |

迁移的关键变化：函数返回值由 `return AIRY_ERR_NOENT;`（正数）改为 `return AIRY_ENOENT;`（负数），调用方判断由 `if (ret == AIRY_ERR_NOENT)` 改为 `if (ret == AIRY_ENOENT)` 或 `if (ret < 0)`。

---

## §2 迁移阶段：识别 → 别名 → 迁移 → 废弃 → 删除

### 2.1 阶段总览

错误码迁移采用与日志收敛（见 [11-log-convergence-plan.md](11-log-convergence-plan.md)）同构的五阶段渐进迁移，每阶段独立可回退，CI 设置强制门槛：

```
阶段 1 识别    →  阶段 2 别名    →  阶段 3 迁移    →  阶段 4 废弃    →  阶段 5 删除
（盘点+映射）   （兼容垫片）       （逐文件替换）      （标记废弃）       （移除旧码）
```

### 2.2 阶段 1：识别（Identify）

**目标**：全量盘点 `AIRY_ERR_*` 引用点，建立迁移清单与映射表。

**动作**：
- `grep -rn "AIRY_ERR_" --include="*.{c,h,rs,go}"` 扫描全仓库
- 逐条确认 `AIRY_ERR_*` 到 `AIRY_E*` 的映射，标记异常项（无对应 `AIRY_E*` 的需新增 [SC] 条目）
- 生成 `err-migration-inventory.csv`，含文件、行号、旧码、新码、返回值符号变化（正→负）
- 识别"返回值符号依赖点"：调用方若假设正数返回，需同步修改

**CI 门槛**：无（识别阶段不修改代码）

**产出**：迁移清单 CSV + 映射表 + 异常项报告

### 2.3 阶段 2：别名（Alias）

**目标**：建立 `AIRY_ERR_*` → `AIRY_E*` 的兼容垫片，使旧码在编译期等价于新码（含符号转换），为逐文件迁移提供安全网。

**动作**：
- 在 `include/airymax/err_compat.h`（agentrt 侧兼容头）定义别名宏，**显式取负**对齐 errno 语义：

```c
/* err_compat.h —— 阶段 2 兼容垫片 */
#ifndef AIRY_ERR_COMPAT_H
#define AIRY_ERR_COMPAT_H
#include <airymax/error.h>   /* [SC] 共享契约，AIRY_E* 负数空间 */

/* AIRY_ERR_* 旧码映射到 AIRY_E* 新码（负数）。
 * 旧码原为正数，此处重定义为负数，使 return AIRY_ERR_NOENT
 * 直接返回负数，与新轨语义一致。 */
#define AIRY_ERR_PERM      AIRY_EPERM        /* -1 */
#define AIRY_ERR_NOENT     AIRY_ENOENT       /* -2 */
#define AIRY_ERR_INVAL     AIRY_EINVAL       /* -22 */
#define AIRY_ERR_NOMEM     AIRY_ENOMEM       /* -12 */
#define AIRY_ERR_BUSY      AIRY_EBUSY        /* -16 */
#define AIRY_ERR_AGAIN     AIRY_EAGAIN       /* -11 */
#define AIRY_ERR_TIMEDOUT  AIRY_ETIMEDOUT    /* -110 */
/* ... 完整映射见 08-sc-error-contract.md ... */
#endif
```

- **关键风险**：旧码由正数变负数，调用方若有 `if (ret == AIRY_ERR_NOENT)` 比较仍成立（因宏值同步变化），但若有 `if (ret > 0)` 判断错误码则需同步修改为 `if (ret < 0)`。阶段 1 识别须标记此类符号依赖点

**CI 门槛**：
- `static_assert(AIRY_ERR_NOENT == AIRY_ENOENT)` 编译期校验等价
- 全量测试通过（符号变化可能暴露隐式正数假设）

**产出**：兼容垫片头文件，全仓库编译 + 测试通过

### 2.4 阶段 3：迁移（Migrate）

**目标**：按迁移清单逐文件将 `AIRY_ERR_*` 机械替换为 `AIRY_E*`，修正返回值符号依赖点，移除对 `err_compat.h` 的依赖。

**动作**：
- 按子系统分批 PR（每个子系统一个 PR）
- 机械替换：`AIRY_ERR_NOENT` → `AIRY_ENOENT`，`AIRY_ERR_PERM` → `AIRY_EPERM`
- 修正符号依赖点：`if (ret > 0 && ret == AIRY_ERR_*)` → `if (ret < 0 && ret == AIRY_E*)`，或简化为 `if (ret == AIRY_E*)` / `if (ret < 0)`
- 替换后移除该文件的 `#include <airymax/err_compat.h>`
- 每 PR 通过完整 CI（编译 + 单元测试 + 集成测试）

**CI 门槛**：
- 新增 `AIRY_ERR_*` 引用 = 0（checkpatch 规则 `AIRY_ERR_FORBIDDEN`）
- 已迁移文件不得重新引入 `err_compat.h`
- 错误码符号校验：所有错误返回值必须为负数（`ret < 0`），CI 静态扫描正数错误码返回

**产出**：`AIRY_ERR_*` 引用点归零

### 2.5 阶段 4：废弃（Deprecate）

**目标**：将 `AIRY_ERR_*` 宏标记为废弃，保留但产生编译警告，防止遗漏回潮。

**动作**：
- `err_compat.h` 中所有 `AIRY_ERR_*` 宏追加 `__attribute__((deprecated("use AIRY_E* instead")))`
- Rust 侧追加 `#[deprecated]`，Go 侧追加 `// Deprecated:` 注释
- 文档中 `AIRY_ERR_*` 标注"已废弃，使用 `AIRY_E*`"

**CI 门槛**：
- 编译警告中 `AIRY_ERR_* deprecated` 计数 = 0（即无任何文件引用 `err_compat.h`）
- 若计数 > 0，CI 失败，要求对应文件完成迁移

**产出**：`err_compat.h` 仅剩废弃声明，无实际引用

### 2.6 阶段 5：删除（Delete）

**目标**：物理删除 `AIRY_ERR_*` 宏与 `err_compat.h`，双轨制彻底终结。

**动作**：
- 删除 `include/airymax/err_compat.h`
- 删除 Rust/Go 侧别名声明
- 更新文档：移除所有 `AIRY_ERR_*` 引用

**CI 门槛**：
- `grep -rn "AIRY_ERR_" --include="*.{c,h,rs,go}"` 输出为空
- `err_compat.h` 不存在
- CI 规则 `AIRY_ERR_FORBIDDEN` 升级为 error（此前为 warning）
- [SC] `error.h` 双端逐字节校验通过（`sc-dual-ci.yml`）

**产出**：单一 `AIRY_E*` 轨，[SC] `error.h` 成为唯一权威源

---

## §3 时间线：与 agentrt-linux Phase 2 同步

### 3.1 同步原则

错误码迁移与 agentrt-linux（AirymaxOS）开发阶段同步推进，确保 agentrt 与 AirymaxOS 在 Phase 2 结束时共享同一 `AIRY_E*` [SC] 契约。与日志收敛计划（[11-log-convergence-plan.md](11-log-convergence-plan.md)）并行推进，但错误码迁移先行——错误码是日志参数的基础，统一错误码后再统一日志可减少中间态复杂度。

### 3.2 阶段时间线

| 迁移阶段 | 对应 AirymaxOS 阶段 | 时间窗口 | 里程碑 |
|---------|-------------------|---------|--------|
| 阶段 1 识别 | Phase 1 尾声（1.0.1 开发） | T0 ~ T0+2w | 迁移清单 + 映射表冻结 |
| 阶段 2 别名 | Phase 2 启动（1.0.1 锁定） | T0+2w ~ T0+4w | 兼容垫片合入，CI static_assert 生效 |
| 阶段 3 迁移 | Phase 2 中期（1.0.1 ~ 1.x.x+） | T0+4w ~ T0+14w | `AIRY_ERR_*` 引用点归零 |
| 阶段 4 废弃 | Phase 2 后期（1.x.x+） | T0+14w ~ T0+18w | deprecated 警告计数归零 |
| 阶段 5 删除 | Phase 2 收尾（2.x.x 启动前） | T0+18w ~ T0+22w | `err_compat.h` 物理删除 |

> **与日志收敛的时序**：错误码迁移阶段 5（删除）比日志收敛阶段 5 提前 2 周完成，确保日志宏引用的错误码参数（如 `log_error("failed: %d", AIRY_EINVAL)`）在日志收敛前已统一为 `AIRY_E*`。

### 3.3 与 AirymaxOS Phase 2 的协同

agentrt-linux Phase 2（1.x.x+ 阶段）引入 12 daemons 用户态化（见 [03-microkernel-strategy.md](../../docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) §9.1），daemons 与 agentrt 通过 IPC 交互，错误码跨 IPC 边界传递。若 agentrt 仍用 `AIRY_ERR_*` 正数、AirymaxOS 用 `AIRY_E*` 负数，IPC 错误码传递需双向转换，是高频 bug 源。因此：

- **阶段 2 别名**与 Phase 2 启动同步：Phase 2 新增 daemons 全部使用 `AIRY_E*`，agentrt 侧别名垫片确保旧码与新码共存期 IPC 边界无符号断裂
- **阶段 3 迁移**与 Phase 2 中期同步：优先迁移与 daemons 有 IPC 交互的 agentrt 子系统，消除跨边界符号转换
- **阶段 5 删除**在 2.x.x 启动前完成：2.x.x 升级 Linux 7.1 基线（ADR-013），[SC] `error.h` 可能扩展错误码空间，双轨制必须在基线升级前终结

### 3.4 风险与回退

| 风险 | 影响 | 缓解 |
|------|------|------|
| 阶段 2 符号变化（正→负）导致调用方隐式正数假设失效 | 测试失败 | 阶段 1 识别标记所有 `ret > 0` 错误码判断；阶段 2 全量测试必过 |
| `AIRY_ERR_*` 无对应 `AIRY_E*`（旧码超出 [SC] 范围） | 阻塞映射 | 阶段 1 识别异常项，通过 RFC 在 [SC] `error.h` 新增对应 `AIRY_E*` |
| 第三方依赖返回 `AIRY_ERR_*` | 阶段 5 无法彻底清零 | 第三方代码不修改，adapter 在调用边界转换符号 |
| 与日志收敛并行导致中间态庞大 | PR 冲突 | 错误码迁移先行 2 周，日志收敛在错误码阶段 3 后启动 |

每阶段设置 1 周缓冲期，若 CI 门槛未达则回退至上一阶段。阶段 2 的符号变化是最高风险点，若全量测试失败率 > 5%，回退至阶段 1 重新识别符号依赖点。

---

## §4 相关文档

- [agentrt 工程标准规范手册](agentrt工程标准规范手册.md) —— agentrt 工程标准上级文档
- [08-unify-design.md](../../docs/AirymaxOS/10-architecture/08-unify-design.md) —— Airymax Unify Design 总纲（UEF 模块 + C-05 冲突点）
- [08-sc-error-contract.md](../../docs/AirymaxOS/30-interfaces/08-sc-error-contract.md) —— `AIRY_E*` 错误码与 `AIRY_FAULT_*` 故障码 [SC] 契约（迁移目标）
- [06-iron9-shared-model.md](../../docs/AirymaxOS/10-architecture/06-iron9-shared-model.md) —— IRON-9 v3 [SC] 共享契约层（`error.h` 物理宿主）
- [11-log-convergence-plan.md](11-log-convergence-plan.md) —— 日志收敛计划（与本计划并行推进，错误码先行）

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. | 错误码迁移计划 | v1.0 | 2026-07-17
