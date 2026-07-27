Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agentrt-linux v4.3 待决策事项迁移实施计划
> **文档定位**：v4.3 闭环报告中 6 项待用户决策事项的详细迁移实施计划，含操作步骤、回滚方案与推进理由\
> **文档版本**：v1.0\
> **最后更新**：2026-07-26\
> **上级文档**：[17-closure-report-v4.3.md](17-closure-report-v4.3.md)\
> **决策原则**：IRON-8（0.1.1 → 1.0.1 直接过渡，禁止兼容别名/双轨制）+ IRON-2（禁止桩函数/桩文件）+ SSoT 单一权威源

---

## 总览

| # | 待决策事项 | 严重性 | 建议时机 | 影响范围 | 推荐方案 |
|---|---------|--------|---------|---------|---------|
| 1 | IPC v1.0/v1.1 双轨迁移评估 | 中 | M0 保持 v1.0，M1 前评估 | IPC 协议层 | 禁止双轨，直接锁定 v1.1 |
| 2 | 错误码 `AIRY_ERR_*` → `AIRY_E*` 迁移 | 高 | 0.1.1 内完成 | agentrt 用户态全量 | 语义合并，非别名映射 |
| 3 | 日志 `AIRY_LOG_*` → `LOG_*` 迁移 | 低 | 0.1.1 内完成 | agentrt 用户态 | **反向迁移**：统一为 `AIRY_LOG_*` |
| 4 | `airy_ind` LSM 迁移 | 高 | M1 前完成 | security/airy_lsm/ | 合并到 `airy_lsm`，删除 airy_ind |
| 5 | v1.1 规划头文件实现 | 低 | M0 保持设计，M1 实现 | [SC] 层 | 按需实现，不预先创建桩文件 |
| 6 | commons/ipc.h [IND] 扩展重定位 | 低 | M1 随 IPC 运行时实现 | agentrt/commons/ | 新建 `ipc_runtime.h` |

---

## 事项 1：IPC v1.0/v1.1 双轨迁移评估

### 1.1 待决策内容详解

**现状**：AgentsIPC 协议定义了多版本演进模型（v1.0/v1.1/v1.2/v2.0），见 [04-ipc-versioning.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/160-compatibility/04-ipc-versioning.md)。当前 [SC] `ipc.h` 中的 7 个操作码标注为"v1.1+ 稳定"（L367-373），但实际代码中已全部定义并使用。版本协商机制设计了 `AIRY_IPC_VERSION_1_0`/`AIRY_IPC_VERSION_1_1` 常量（L465-466）和 bitmap 协商逻辑。

**核心矛盾**：
- IRON-8 要求 0.1.1 → 1.0.1 直接过渡，**禁止双轨制**
- 但 IPC 版本协商文档设计了 v1.0 基线 + v1.1 扩展的双版本共存机制
- v1.0 与 v1.1 的实际差异仅为 `trace_id` 字段（v1.0 无 trace_id，v1.1 新增），消息头布局完全相同（128B 固定）

**实际影响**：
- 消息头字段兼容性矩阵（L264-275）显示所有字段在 v1.0/v1.1 间"永不变更"或"向后兼容"
- v1.0 降级仅影响 `trace_id` 贯穿能力（退化为本地日志关联）和批量提交（退化为单条）
- 当前处于设计阶段，无实际 v1.0 实现代码需要迁移

### 1.2 推进理由

**推荐方案：禁止双轨，直接锁定 v1.1 为唯一基线**

理由：
1. **IRON-8 硬约束**：0.1.1 → 1.0.1 直接过渡，禁止兼容层/双轨制。IPC 版本双轨制本质是兼容层，违反此铁律
2. **0.1.1 是唯一奠基版本**：所有架构、标准、许可证必须在 0.1.1 内完成。IPC 协议基线必须在此阶段锁定
3. **v1.0 无实际用户**：agentrt-linux 仍处于设计阶段，v1.0 从未发布，无遗留用户需要兼容
4. **版本协商机制是过度设计**：M0 阶段只需单一协议版本，版本协商逻辑增加 ~500 行代码复杂度，违反"简单即美"原则
5. **UABI 永不破坏哲学已保障前向兼容**：128B 定长消息头 + reserved 字段策略已确保未来扩展不破坏兼容，无需多版本协商

### 1.3 具体操作步骤

```
阶段 1：文档修正（M0 阶段，设计层）
├── 步骤 1.1：修改 04-ipc-versioning.md
│   ├── 将"v1.0/v1.1 双版本"描述改为"v1.1 唯一基线"
│   ├── 保留版本演进模型文档（供未来 v2.0 参考），但标注"M0 阶段仅实现 v1.1"
│   ├── 删除 v1.0 降级策略表（L297-302），改为"无降级，v1.1 是最低支持版本"
│   └── 保留版本协商协议设计文档（供 v2.0+ 使用），但标注"M0 不实现协商逻辑"
├── 步骤 1.2：修改 02-ipc-protocol.md
│   ├── 移除所有"v1.0 退化为..."描述
│   └── 统一标注"v1.1 基线，7 opcode 自 0.1.1 起稳定"
└── 步骤 1.3：修改 120-cross-project-code-sharing.md
    └── [SC] ipc.h 节标注"v1.1 唯一基线，无版本协商"

阶段 2：代码锁定（M1 阶段，实现层）
├── 步骤 2.1：在 ipc.h 中定义 AIRY_IPC_VERSION = 1（v1.1 对应版本号 1）
├── 步骤 2.2：移除版本协商相关常量（AIRY_IPC_VERSION_1_0/1_1/1_2）
└── 步骤 2.3：移除版本 bitmap 协商逻辑（如已实现）

阶段 3：CI 验证（M1 阶段）
└── 步骤 3.1：在 sc-dual-ci.yml 中添加版本唯一性检查
```

### 1.4 回滚方案

| 触发条件 | 回滚操作 | 回滚成本 |
|---------|---------|---------|
| 用户决定保留双轨制 | 恢复 04-ipc-versioning.md 原文，在 M1 实现版本协商逻辑 | 低（仅文档变更，无代码影响） |
| v2.0 需要引入不兼容变更 | 启用版本协商机制，此时 v1.1 已有实际用户 | 中（需实现协商逻辑，但 v1.1 基线不变） |

---

## 事项 2：错误码 `AIRY_ERR_*` → `AIRY_E*` 双轨迁移

### 2.1 待决策内容详解

**现状**：agentrt 用户态错误码存在两套命名空间，共存于 [error.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt/commons/utils/error/include/error.h)：

| 命名空间 | 前缀 | 数量 | 语义 | 示例 |
|---------|------|------|------|------|
| POSIX 风格 | `AIRY_E*` | ~40+ | 对标 POSIX errno 负值，SSoT 定义于 `types.h` | `AIRY_EINVAL=-22`, `AIRY_ENOMEM=-12` |
| 扩展风格 | `AIRY_ERR_*` | ~80+ | agentrt 专属扩展错误码，定义于 `error.h` | `AIRY_ERR_INVALID_PARAM=-36`, `AIRY_ERR_LLM_RATE_LIMIT=-403` |

**当前问题**：
1. 两套命名空间语义重叠：`AIRY_ERR_INVALID_PARAM(-36)` ≈ `AIRY_EINVAL(-22)`，`AIRY_ERR_OUT_OF_MEMORY(-59)` ≈ `AIRY_ENOMEM(-12)`
2. 已有别名映射（L86-104）：`AIRY_ECANCELED = AIRY_ERR_CANCELED`，但这些别名是"死代码"（`#ifndef` 守卫恒为 false）
3. v4.3 刚修复了 `AIRY_ERR_*` 与 `AIRY_EIPC_*` 的值碰撞，但 `AIRY_ERR_*` 与 `AIRY_E*` 的语义重叠仍未解决
4. IRON-8 要求禁止兼容别名/双轨制

**影响范围**：
- `agentrt/commons/utils/error/include/error.h`：~80 个 `AIRY_ERR_*` 定义
- agentrt 用户态源文件：引用 `AIRY_ERR_*` 的文件数量未统计（设计阶段，引用较少）
- agentrt-linux 内核：**不受影响**（内核 [SC] `error.h` 仅定义 `AIRY_E*` POSIX 风格 + `AIRY_EIPC_*`/`AIRY_ECAP_*` 子空间码，无 `AIRY_ERR_*`）

### 2.2 推进理由

**推荐方案：语义合并，将 `AIRY_ERR_*` 专属码迁移为 `AIRY_E*` 命名空间，禁止别名**

理由：
1. **IRON-8 硬约束**：禁止兼容别名/双轨制。当前 `AIRY_ECANCELED = AIRY_ERR_CANCELED` 别名是典型双轨制
2. **SSoT 单一权威源**：`AIRY_E*` 是 [SC] `error.h` 的权威命名空间，agentrt 用户态应与内核统一
3. **"一码一义"原则**：`AIRY_ERR_INVALID_PARAM` 和 `AIRY_EINVAL` 语义相同，应合并为单一宏
4. **命名一致性**：内核使用 `AIRY_E*`，用户态应跟随，避免认知负担

**但需区分三类 `AIRY_ERR_*` 码**：

| 类别 | 示例 | 处理方式 |
|------|------|---------|
| 有 POSIX 等价物 | `AIRY_ERR_INVALID_PARAM` → `AIRY_EINVAL` | 直接替换引用，删除 `AIRY_ERR_*` 定义 |
| 无 POSIX 等价物但属通用层 | `AIRY_ERR_LLM_RATE_LIMIT` | 重命名为 `AIRY_ELLM_RATE_LIMIT`，值不变 |
| 系统层专属 | `AIRY_ERR_SYS_THREAD` | 重命名为 `AIRY_ESYS_THREAD`，值不变 |

### 2.3 具体操作步骤

```
阶段 1：分类映射表制作（0.1.1 设计阶段）
├── 步骤 1.1：列出全部 ~80 个 AIRY_ERR_* 定义
├── 步骤 1.2：逐个标注 POSIX 等价物（如有）
│   ├── AIRY_ERR_INVALID_PARAM → AIRY_EINVAL
│   ├── AIRY_ERR_NULL_POINTER → AIRY_EFAULT
│   ├── AIRY_ERR_OUT_OF_MEMORY → AIRY_ENOMEM
│   ├── AIRY_ERR_BUFFER_TOO_SMALL → AIRY_ENOBUFS（新增 POSIX 码）
│   ├── AIRY_ERR_NOT_FOUND → AIRY_ENOENT
│   ├── AIRY_ERR_ALREADY_EXISTS → AIRY_EEXIST
│   ├── AIRY_ERR_TIMEOUT → AIRY_ETIMEDOUT
│   ├── AIRY_ERR_NOT_SUPPORTED → AIRY_ENOTSUP
│   ├── AIRY_ERR_PERMISSION_DENIED → AIRY_EPERM
│   ├── AIRY_ERR_IO → AIRY_EIO
│   ├── AIRY_ERR_PARSE_ERROR → AIRY_EPARSE（新增）
│   ├── AIRY_ERR_STATE_ERROR → AIRY_ESTATE（新增）
│   ├── AIRY_ERR_OVERFLOW → AIRY_ERANGE
│   ├── AIRY_ERR_CANCELED → AIRY_ECANCELED
│   ├── AIRY_ERR_BUSY → AIRY_EBUSY
│   └── ... 其余通用码
├── 步骤 1.3：无等价物的码确定新名（AIRY_ERR_LLM_* → AIRY_ELLM_*）
└── 步骤 1.4：生成迁移映射表文档 docs/AirymaxOS/30-interfaces/09-error-migration-map.md

阶段 2：types.h 扩展（0.1.1 设计阶段）
├── 步骤 2.1：在 airy_types.h 中新增缺失的 POSIX 等价码
│   ├── AIRY_EPARSE = -55（原 AIRY_ERR_PARSE_ERROR 的值）
│   ├── AIRY_ESTATE = -56（原 AIRY_ERR_STATE_ERROR 的值）
│   └── ... 其余新增码
└── 步骤 2.2：确保新增码值不与现有 AIRY_E* / AIRY_EIPC_* / AIRY_ECAP_* 碰撞

阶段 3：批量替换（0.1.1 实现阶段）
├── 步骤 3.1：编写 sed/Python 脚本，按映射表批量替换 .c/.h 文件中的 AIRY_ERR_* 引用
├── 步骤 3.2：删除 error.h 中所有 AIRY_ERR_* 定义（保留 AIRY_E* 定义）
├── 步骤 3.3：删除别名映射块（L86-104）
└── 步骤 3.4：全量编译验证

阶段 4：CI 验证（0.1.1 完成后）
└── 步骤 4.1：在 CI 中添加 grep 检查，确保无 AIRY_ERR_* 残留
    └── grep -rn "AIRY_ERR_" agentrt/ → 必须 0 匹配
```

### 2.4 回滚方案

| 触发条件 | 回滚操作 | 回滚成本 |
|---------|---------|---------|
| 迁移后发现语义错误 | git revert 迁移 commit，恢复 AIRY_ERR_* 定义 | 低（单一 commit 回滚） |
| 某些 AIRY_ERR_* 码无法找到等价物 | 保留为 AIRY_E* 前缀（如 AIRY_ELLM_RATE_LIMIT），值不变 | 低（仅命名变更） |
| 迁移脚本误替换 | git checkout 受影响文件，手动修正 | 中（需逐文件检查） |

**回滚保障措施**：
- 迁移前创建 git tag `pre-error-migration-v0.1.1`
- 迁移分多个 commit（每类一个），支持部分回滚
- 迁移脚本保存为 `tools/migrate_error_codes.py`，可重复执行

---

## 事项 3：日志 `AIRY_LOG_*` → `LOG_*` 双轨迁移

### 3.1 待决策内容详解

**现状**：经全仓扫描，[SC] `log_types.h`（kernel 和 commons 双端字节级一致）定义的日志级别宏为 `AIRY_LOG_*` 前缀：

```c
// log_types.h L37-44
AIRY_LOG_DEBUG = 0,
AIRY_LOG_INFO = 1,
AIRY_LOG_WARN = 2,
AIRY_LOG_ERROR = 3,
AIRY_LOG_FATAL = 4,
```

agentrt 用户态源文件中**未发现任何 `LOG_*` 前缀的使用**（经 grep 确认为 0 匹配）。v3.5 修复报告中提到"日志级别前缀 `LOG_*` → `AIRY_LOG_*`（对齐 SSoT `log_types.h` L37-44）"，说明此前已完成了从 `LOG_*` 到 `AIRY_LOG_*` 的迁移。

**v4.3 审查结论**：此事项实际上**已完成**，不存在双轨制。v4.3 报告中将其列为"待决策"是过于保守——实际状态是"已统一为 `AIRY_LOG_*`，无残留 `LOG_*`"。

### 3.2 推进理由

**推荐方案：标记为"已完成"，无需进一步迁移**

理由：
1. **SSoT 已对齐**：`AIRY_LOG_*` 是 [SC] `log_types.h` 的权威定义，kernel 和 commons 字节级一致
2. **无残留**：全仓 grep 确认无 `LOG_*`（非 `AIRY_LOG_*`）的使用
3. **命名一致性**：`AIRY_LOG_*` 前缀与项目命名规范一致（`AIRY_` 前缀统一）

### 3.3 具体操作步骤

```
阶段 1：状态确认（M0 阶段，立即完成）
├── 步骤 1.1：执行 grep -rn "LOG_DEBUG\|LOG_INFO\|LOG_WARN\|LOG_ERROR\|LOG_FATAL" agentrt/
│   └── 排除 AIRY_LOG_* 前缀的匹配 → 确认 0 残留
├── 步骤 1.2：在 v4.3 闭环报告中将此事项状态更新为"已完成"
└── 步骤 1.3：在 CI 中添加检查，防止 LOG_* 前缀重新引入
    └── grep -rn "LOG_DEBUG\|LOG_INFO\|..." agentrt/ --exclude="AIRY_LOG_*" → 必须 0 匹配
```

### 3.4 回滚方案

| 触发条件 | 回滚操作 | 回滚成本 |
|---------|---------|---------|
| 无（此事项已完成，无需回滚） | — | — |

---

## 事项 4：`airy_ind` LSM 迁移

### 4.1 待决策内容详解

**现状**：agentrt-linux 存在两个 LSM 模块实现：

| 模块 | 路径 | 安全上下文管理 | 注册方式 | 用途 |
|------|------|-------------|---------|------|
| `airy` | `kernel/security/airy/airy_lsm.c` | LSM blob 机制（`task->security + offset`） | `DEFINE_LSM(airy)` with `.blobs` | 生产环境 |
| `airy_ind` | `security/airy_lsm/airy_lsm.c` | 直接覆写 `task->security = sec` | `DEFINE_LSM(airy_ind)` 无 `.blobs` | 教学/研究 |

**UAF 风险**（v3.5 P0-3 确认）：如果两个 LSM 同时加载，`airy_ind` 的 `task_alloc` 会覆写 `task->security` 指针，导致 `airy` 的 `task_free` 通过 blob 偏移读取到错误内存，触发 use-after-free 或 double-free。

**当前缓解措施**：
- `airy_ind` 的 `airy_lsm.c` 顶部已添加 UAF 安全警告注释（L7-24）
- 明确标注"禁止在生产构建中同时加载"

**根本矛盾**：
- IRON-2 禁止桩函数/桩文件，`airy_ind` 不是桩，是完整实现
- IRON-8 要求 0.1.1 → 1.0.1 直接过渡，禁止双轨制
- 两个 LSM 实现共存本质是"双轨制"

### 4.2 推进理由

**推荐方案：M1 前将 `airy_ind` 迁移到 LSM blob 机制，然后合并到 `airy_lsm`，删除 `airy_ind` 独立模块**

理由：
1. **消除 UAF 风险**：即使有警告注释，两个 LSM 共存仍是定时炸弹。M1 实现阶段开发者可能误同时加载
2. **IRON-8 硬约束**：禁止双轨制。两个 LSM 实现是典型双轨制
3. **简化架构**：`airy_ind` 仅用于"教学和研究目的"，但 1.0.1 是生产就绪版本，不需要教学模块
4. **代码复用**：`airy_ind` 的钩子逻辑（task_alloc/task_free）与 `airy` 完全相同，仅安全上下文管理方式不同。合并后可删除重复代码
5. **"简单即美"原则**：一个安全模块比两个更简单、更可预测、更易验证

**不推荐"保留 airy_ind 作为独立模块但迁移到 blob 机制"的理由**：
- 即使迁移到 blob 机制，两个 `DEFINE_LSM()` 注册同名钩子会产生冲突
- 维护两份相同逻辑的代码违反 DRY 原则
- `airy_ind` 的"教学"价值可通过阅读 `airy_lsm.c` 源码实现，不需要独立可加载模块

### 4.3 具体操作步骤

```
阶段 1：逻辑迁移（M1 阶段，实现层）
├── 步骤 1.1：分析 airy_ind 与 airy 的钩子差异
│   ├── 读取 security/airy_lsm/airy_lsm.c 全部钩子实现
│   ├── 对比 kernel/security/airy/airy_lsm.c 的钩子实现
│   └── 确认差异仅为安全上下文管理方式（blob vs 直接覆写）
├── 步骤 1.2：将 airy_ind 独有逻辑（如有）合并到 airy_lsm.c
│   ├── 检查 airy_ind 是否有 airy_lsm 未实现的钩子
│   └── 如有，移植到 airy_lsm.c 并使用 blob 机制
└── 步骤 1.3：确保 airy_lsm.c 覆盖所有 airy_ind 的功能

阶段 2：模块删除（M1 阶段）
├── 步骤 2.1：删除 security/airy_lsm/ 目录
│   ├── 删除 airy_lsm.c
│   └── 删除 Kbuild
├── 步骤 2.2：更新 .gitmodules（如 airy_lsm 是子模块）
├── 步骤 2.3：更新 MAINTAINERS 文件，移除 airy_ind 相关条目
├── 步骤 2.4：更新 CODEOWNERS，移除 airy_ind 相关条目
└── 步骤 2.5：更新 CI 配置
    ├── ci-airy.yml：移除 security/airy_lsm/ 路径触发条件
    └── mgmt-orchestrator.yml：更新子模块计数（如适用）

阶段 3：文档更新（M1 阶段）
├── 步骤 3.1：更新 docs/AirymaxOS/110-security/01-lsm-framework.md
│   ├── 移除 airy_ind 相关描述
│   └── 标注"单一 LSM 模块 airy，使用 blob 机制"
├── 步骤 3.2：更新 docs/AirymaxOS/110-security/07-airy-lsm-design.md
└── 步骤 3.3：在 v3.5 审查报告中标注 P0-3 已完全闭环

阶段 4：验证（M1 阶段）
├── 步骤 4.1：编译验证 — airy_defconfig 构建无 airy_ind 模块
├── 步骤 4.2：运行时验证 — 加载 airy LSM，确认无 UAF
└── 步骤 4.3：CI 验证 — grep "airy_ind" → 仅在历史文档中存在
```

### 4.4 回滚方案

| 触发条件 | 回滚操作 | 回滚成本 |
|---------|---------|---------|
| airy_lsm.c 缺少 airy_ind 的关键功能 | git revert 删除 commit，恢复 airy_ind 模块 | 低（git 回滚） |
| 合并后 airy_lsm.c 出现回归 | 检查合并逻辑，修复后重新验证 | 中（需调试 LSM 钩子） |
| 用户决定保留 airy_ind 用于教学 | 将 airy_ind 迁移到 blob 机制但保留独立模块（不推荐） | 中（需重构安全上下文管理） |

**回滚保障措施**：
- 删除前创建 git tag `pre-airy-ind-removal-v1.0.1`
- 删除操作使用单一 commit，便于整体回滚
- airy_ind 的完整源码保留在 git 历史中，可随时恢复

---

## 事项 5：v1.1 规划头文件实现

### 5.1 待决策内容详解

**现状**：[SC] 层 10 个核心头文件已在 M0 阶段完成设计定义（kernel 和 commons 双端字节级一致）。v1.1 规划的头文件指以下两类：

**类别 A：已规划但未创建的头文件**：
- 根据 [120-cross-project-code-sharing.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md) §2.2，`bpf_struct_ops.h` 是"补充共享文件"（非 10 核心 [SC]），已实现
- `syscall.h` 是 codegen 产物，已实现
- 无其他明确规划的未实现头文件

**类别 B：现有头文件中标注"v1.1"的功能**：
- `ipc.h` 中 7 个 opcode 标注"v1.1+ 稳定"（见事项 1）
- `error.h` 中 Capability Folding 错误码（-78~-82）标注"v1.1 新增"
- `syscalls.h` 中 4 核心 syscall 标注"v1.1: 4 核心 + 20 预留 = 24 槽位"

**实际状态**：所有"v1.1 规划"的头文件内容已在 M0 阶段的设计文档和 [SC] 头文件中定义完成。"v1.1"标签是版本标识，不代表"未实现"。

### 5.2 推进理由

**推荐方案：M0 阶段保持现状（设计文档 + [SC] 头文件定义），M1 阶段按需实现 .c 文件**

理由：
1. **IRON-2 禁止桩函数/桩文件**：M0 阶段不创建只有声明无实现的 .c 文件
2. **M0 是设计阶段**：头文件的宏/结构体/枚举定义已足够，.c 实现属于 M1 范畴
3. **"v1.1"是版本标签不是待办标志**：[SC] 头文件中的"v1.1"标注表示"自 v1.1 起稳定"，不是"v1.1 才实现"
4. **按需实现**：M1 阶段每个模块开始实现时，自然需要对应的 .c 文件，无需预先创建

### 5.3 具体操作步骤

```
阶段 1：M0 现状确认（立即完成）
├── 步骤 1.1：确认 10 个 [SC] 核心头文件已全部定义完成
│   └── ls kernel/include/uapi/linux/airymax/ → 确认 10 个 .h + bpf_struct_ops.h
├── 步骤 1.2：确认 bpf_struct_ops.h（补充共享文件）已实现
├── 步骤 1.3：确认 syscall.h（codegen 产物）已实现
└── 步骤 1.4：在 v4.3 闭环报告中将此事项状态更新为"M0 已完成设计，M1 按需实现"

阶段 2：M1 按需实现（M1 阶段）
├── 步骤 2.1：IPC 模块实现时，创建 kernel/kernel/ipc/ 下的 .c 文件
├── 步骤 2.2：调度模块实现时，创建 kernel/kernel/corekern/sched/ 下的 .c 文件
├── 步骤 2.3：安全模块实现时，完善 kernel/security/airy/ 下的 .c 文件
└── ... 其余模块按 M1 计划推进

阶段 3：版本标签清理（M1 阶段）
└── 步骤 3.1：将头文件中的"v1.1"标签统一改为"v1.0.1"（对齐 IRON-8）
    ├── ipc.h: "v1.1+ 稳定" → "v1.0.1+ 稳定"
    ├── error.h: "v1.1 新增" → "v1.0.1 新增"
    └── syscalls.h: "v1.1: 4 核心" → "v1.0.1: 4 核心"
```

### 5.4 回滚方案

| 触发条件 | 回滚操作 | 回滚成本 |
|---------|---------|---------|
| 无（此事项是"按需推进"，无破坏性变更） | — | — |

---

## 事项 6：commons/ipc.h [IND] 扩展重定位

### 6.1 待决策内容详解

**现状**：v4.2 修复 #10 中，为实现 `commons/ipc.h` 与 `kernel/ipc.h` 字节级一致，从 `commons/ipc.h` 中移除了以下 [IND]（完全独立层）扩展内容：

| 移除的常量 | 用途 | 引用情况 |
|-----------|------|---------|
| `AIRY_IPC_RING_DEF_ENTRIES` | 运行时默认 ring 条目数 | 0 引用（移除安全） |
| `AIRY_IPC_RING_MAX_ENTRIES` | 运行时最大 ring 条目数 | 0 引用（移除安全） |
| `AIRY_IPC_SQE_F_*` | io_uring SQE 标志位 | 0 引用（移除安全） |
| `AIRY_IPC_CQE_F_*` | io_uring CQE 标志位 | 0 引用（移除安全） |

**当前状态**：这些常量已从 `commons/ipc.h` 移除，agentrt 用户态代码未引用这些常量（经 grep 确认 0 匹配），因此移除无影响。

**待决策内容**：当 M1 阶段 agentrt 用户态需要实现 IPC 运行时（ring buffer 管理、io_uring 交互）时，这些常量需要重新定义在何处？

### 6.2 推进理由

**推荐方案：M1 阶段新建 `agentrt/commons/include/airymax/ipc_runtime.h`（[IND] 层独立头文件）**

理由：
1. **IRON-9 v3 四层模型**：[IND] 层定义"完全独立"内容，不与 kernel 共享。这些运行时常量属于 [IND] 层
2. **[SC] 层纯净性**：`ipc.h` 是 [SC] 共享契约层，应仅包含跨端共享的数据结构和 magic。运行时常量是 agentrt 用户态专属，不应污染 [SC]
3. **命名清晰**：`ipc_runtime.h` 明确表示"IPC 运行时扩展"，与 `ipc.h`（IPC 契约）职责分离
4. **kernel 侧不需要这些常量**：内核 IPC 实现使用不同的 ring 管理机制（kfifo），不需要 SQE/CQE 标志位的用户态定义

### 6.3 具体操作步骤

```
阶段 1：M0 现状确认（立即完成）
├── 步骤 1.1：确认 commons/ipc.h 已无 [IND] 扩展（v4.2 已完成）
├── 步骤 1.2：确认 agentrt 用户态未引用已移除的常量
└── 步骤 1.3：在 v4.3 闭环报告中标注"M1 阶段创建 ipc_runtime.h"

阶段 2：M1 创建 ipc_runtime.h（M1 阶段，IPC 运行时实现时）
├── 步骤 2.1：创建 agentrt/commons/include/airymax/ipc_runtime.h
│   ├── SPDX: AGPL-3.0-or-later OR Apache-2.0（agentrt 用户态许可证）
│   ├── 守卫: _AIRY_IPC_RUNTIME_H
│   ├── 包含 <airymax/ipc.h>（依赖 [SC] IPC 契约）
│   └── 定义 [IND] 层扩展常量：
│       ├── AIRY_IPC_RING_DEF_ENTRIES (256)
│       ├── AIRY_IPC_RING_MAX_ENTRIES (4096)
│       ├── AIRY_IPC_SQE_F_* (io_uring SQE 标志位)
│       └── AIRY_IPC_CQE_F_* (io_uring CQE 标志位)
├── 步骤 2.2：更新 docs/AirymaxOS/50-engineering-standards/11-sc-header-type-bridging.md
│   └── 新增 ipc_runtime.h 作为 [IND] 层示例
└── 步骤 2.3：更新 docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md
    └── [IND] 层清单新增 ipc_runtime.h

阶段 3：验证（M1 阶段）
├── 步骤 3.1：确认 commons/ipc.h 仍与 kernel/ipc.h 字节级一致
│   └── diff <(grep -v '#include' kernel/ipc.h) <(grep -v '#include' commons/ipc.h) → 0 差异
└── 步骤 3.2：确认 ipc_runtime.h 不被 kernel 侧引用
    └── grep -rn "ipc_runtime.h" agentrt-linux/kernel/ → 0 匹配
```

### 6.4 回滚方案

| 触发条件 | 回滚操作 | 回滚成本 |
|---------|---------|---------|
| ipc_runtime.h 常量需要与 kernel 共享 | 将常量提升到 [SC] ipc.h（需更新双端） | 低（复制定义到 ipc.h） |
| agentrt 不需要这些常量 | 删除 ipc_runtime.h | 低（单一文件删除） |

---

## 实施优先级与时间线

| 优先级 | 事项 | 建议时机 | 预计工作量 | 依赖关系 |
|--------|------|---------|-----------|---------|
| P0 | 事项 3：日志迁移确认 | 立即（M0） | 极小（仅状态确认） | 无 |
| P0 | 事项 5：v1.1 头文件确认 | 立即（M0） | 极小（仅状态确认） | 无 |
| P1 | 事项 1：IPC v1.0/v1.1 锁定 | M0 文档修正 + M1 代码锁定 | 小（文档变更为主） | 无 |
| P1 | 事项 6：ipc_runtime.h 规划 | M0 文档标注 + M1 实现 | 小（M1 时按需创建） | 事项 1 完成 |
| P2 | 事项 2：错误码迁移 | 0.1.1 实现阶段 | 大（~80 个码迁移） | types.h 扩展完成 |
| P2 | 事项 4：airy_ind 删除 | M1 前完成 | 中（代码删除 + 验证） | airy_lsm 功能确认完整 |

## 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 错误码迁移遗漏引用 | 中 | 编译失败 | CI grep 检查 + 全量编译验证 |
| airy_ind 删除后功能缺失 | 低 | 安全钩子缺失 | 迁移前完整对比两个 LSM 的钩子覆盖 |
| IPC v1.1 锁定后需支持 v1.0 | 极低 | 需重新实现版本协商 | v1.0 从未发布，无实际用户 |
| ipc_runtime.h 与 [SC] 边界模糊 | 低 | [SC] 层污染 | CI diff 检查 + 设计评审 |

---

## 附录：决策矩阵

| 事项 | 立即执行 | M0 阶段 | M1 阶段 | 1.0.1 阶段 |
|------|---------|---------|---------|-----------|
| 1. IPC v1.0/v1.1 | — | 文档锁定 v1.1 | 代码实现 v1.1 | — |
| 2. 错误码迁移 | — | 制作映射表 | — | 批量迁移执行 |
| 3. 日志迁移 | 状态确认 | — | — | — |
| 4. airy_ind 删除 | — | — | 合并 + 删除 | — |
| 5. v1.1 头文件 | 状态确认 | — | 按需实现 .c | — |
| 6. ipc_runtime.h | — | 文档标注 | 创建文件 | — |

---

*迁移实施计划完毕。请用户审阅并决策各事项的推进时机。*
