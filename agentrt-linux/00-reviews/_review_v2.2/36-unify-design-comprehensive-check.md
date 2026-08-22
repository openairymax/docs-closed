Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 36 — Airymax Unify Design 五模块全面检查

## "五模块如五指——握拳则成基石，张开则成体系"

> **文档性质**：基于 35 号 A-IPC 最终设计，对 Airymax Unify Design 五模块（A-UEF/A-ULP/A-UCS/A-ULS/A-IPC）的一致性、完整性、正确性全面检查
> **检查范围**：[10-unify-design.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/10-unify-design.md) 总纲 + 各模块 [SC] 契约文档 + 35 号 A-IPC 设计
> **检查标准**：6 条硬约束 H1-H6 + IRON-9 v3 四层模型 + 乔布斯/艾夫"简约就是美"
> **核心问题**：A-IPC 重构后，五模块是否仍然自洽？是否存在孤立设计？是否存在契约断裂？

---

## §0 检查框架

### 0.1 五模块定位（10-unify-design.md §2）

```
┌─────────────────────────────────────────────────────────────────┐
│                   Airymax Unify Design 五模块                     │
│                                                                   │
│   基础层（横向贯穿）                                              │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐                         │
│   │ A-UEF   │  │ A-ULP   │  │ A-UCS   │                         │
│   │ 统一    │  │ 统一    │  │ 统一    │                         │
│   │ 错误码  │  │ 日志    │  │ 配置    │                         │
│   └─────────┘  └─────────┘  └─────────┘                         │
│                                                                   │
│   韧性层（纵向承重）                                              │
│   ┌─────────┐  ┌─────────┐                                       │
│   │ A-ULS   │  │ A-IPC   │                                       │
│   │ 统一    │  │ 统一    │                                       │
│   │ 生命周期│  │ IPC     │                                       │
│   └─────────┘  └─────────┘                                       │
└─────────────────────────────────────────────────────────────────┘

模块依赖关系（10-unify-design.md §3）:
  - A-UEF ← A-ULP/A-UCS/A-ULS/A-IPC（所有模块依赖错误码）
  - A-ULP ← A-ULS/A-IPC（韧性层通过 A-ULP 观测）
  - A-UCS ← A-ULS/A-IPC（韧性层通过 A-UCS 治理）
  - A-ULS ← A-IPC（A-ULS 通过 A-IPC 执行裁决）
  - A-IPC 自洽（第一块基石）
```

### 0.2 检查维度

```
维度 1: 一致性（Consistency）
  - 模块间接口是否一致？
  - 错误码/日志/配置字段是否对齐？
  - [SC] 共享契约是否双端同步？

维度 2: 完整性（Completeness）
  - 每个模块的 [SC] 头文件是否完整？
  - 每个模块的错误码空间是否覆盖？
  - 每个模块的 [DSL] 降级块是否定义？

维度 3: 正确性（Correctness）
  - 模块间依赖关系是否正确？
  - 是否存在循环依赖？
  - 是否存在契约断裂？

维度 4: 与 35 号 A-IPC 设计的对齐
  - 35 号 §10 五模块对接是否落地？
  - 6 条硬约束 H1-H6 是否满足？
  - [SC]/[SS]/[IND]/[DSL] 四层映射是否清晰？

维度 5: 与 IRON-9 v3 四层模型的对齐
  - [SC] 共享契约层是否完整？
  - [SS] 语义同源层是否清晰？
  - [IND] 完全独立层是否无依赖？
  - [DSL] 降级生存层是否可生存？
```

### 0.3 检查输入

| 输入 | 来源 | 状态 |
|------|------|:---:|
| Airymax Unify Design 总纲 | [10-unify-design.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/10-unify-design.md) | ✓ 已读 |
| A-UEF [SC] 契约 | [08-sc-error-contract.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/08-sc-error-contract.md) | ✓ 已读 |
| A-ULP [SC] 契约 | [09-sc-log-types-contract.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/09-sc-log-types-contract.md) | ✓ 已读 |
| [SC] 跨端共享规范 | [120-cross-project-code-sharing.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md) | ✓ 已读 |
| A-IPC 最终设计 | [35-aipc-final-redesign.md](file:///home/spharx/SpharxWorks/airymaxhub/docs-closed/agent-linux/00-reviews/_review_v2.2/35-aipc-final-redesign.md) | ✓ 已读 |
| IRON-9 v3 四层模型 | [06-iron9-shared-model.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/06-iron9-shared-model.md) | ✓ 已读 |
| [DSL] 降级生存层 | [11-degraded-survival-layer.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/11-degraded-survival-layer.md) | ✓ 已读 |
| syscall 接口 | [01-syscalls.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/01-syscalls.md) | ✓ 已读 |

---

## §1 A-UEF 检查（统一错误码框架）

### 1.1 模块定位

```
模块: A-UEF (Unified Error & Fault Framework)
[SC] 头文件: kernel/include/airymax/error.h
[SC] 契约文档: 30-interfaces/08-sc-error-contract.md
错误码空间分配:
  - POSIX 码空间 [-1, -40]
  - IPC 码空间 [-41, -70]
  - Capability 码空间 [-71, -100]
  - [SC] 码空间 [-101, -200]
  - [DSL] 码空间 [-201, -300]
  - Fault 码空间 [0x1000, 0x1FFF]
```

### 1.2 一致性检查

| 检查项 | 现状 | 35 号设计 | 状态 |
|--------|------|----------|:---:|
| 错误码空间分配 | 5 子空间 + Fault | 35 号 §8.1 一致 | ✓ |
| IPC 码空间 [-41, -70] | 已定义 -41~-52 | 35 号 §8.1 新增 -44/-45/-46/-47/-48/-49/-50 | ⚠ 需同步 |
| Capability 码空间 [-71, -100] | 已定义 -71~-77 | 35 号 §8.1 新增 -78/-79/-80/-81/-82 | ⚠ 需同步 |
| Fault 码 [0x1000, 0x1FFF] | 未定义具体值 | 35 号 §8.1 新增 0x1001/0x1002/0x1003 | ⚠ 需同步 |
| AIRY_ECAP_RADIX_MISS (-76) | 已定义（当前主用） | 35 号保留（[DSL] 模式兜底） | ✓ |
| AIRY_ECAP_STATIC_KEY (-77) | 已定义（当前主用） | 35 号保留（[DSL] 模式兜底） | ✓ |
| AIRY_ECFGVERSION (-40) | 已定义 | 不变 | ✓ |

### 1.3 完整性检查

```
[SC] error.h 完整性:
  ✓ POSIX 码空间（38 个错误码）
  ✓ IPC 码空间（12 个错误码 + 18 个预留）
  ✓ Capability 码空间（12 个错误码 + 18 个预留）
  ✓ [SC] 码空间（100 个槽位，AIRY_ECFGVERSION 已分配）
  ✗ [DSL] 码空间（100 个槽位，未定义具体值）→ 需补充
  ✓ Fault 码空间（4096 个槽位，0x1001-0x1003 已分配）

缺失项:
  - [DSL] 码空间 [-201, -300] 未定义具体错误码
  - 建议: 至少定义 AIRY_EDSL_FALLBACK_ACTIVE (-201)、AIRY_EDSL_VERSION_MISMATCH (-202)
```

### 1.4 正确性检查

```
错误码值域无冲突:
  ✓ POSIX [-1, -40] 与 IPC [-41, -70] 不重叠
  ✓ IPC [-41, -70] 与 Capability [-71, -100] 不重叠
  ✓ Capability [-71, -100] 与 [SC] [-101, -200] 不重叠
  ✓ [SC] [-101, -200] 与 [DSL] [-201, -300] 不重叠
  ✓ Fault [0x1000, 0x1FFF] 为正数，与负数错误码不冲突

30 号审查错误码空间定位错误（-53 在 IPC 码空间而非 Capability）:
  ✓ 35 号 §8.1 已修正为 -78/-79/-80（Capability 码空间）

错误码语义清晰:
  ✓ 每个 Capability 错误码有明确的触发条件（35 号 §8.2）
  ✓ Fault 码触发 sec_d 审计 + 可能的 Agent 终止
  ✓ [DSL] 模式使用 AIRY_ECAP_RADIX_MISS/STATIC_KEY 兜底
```

### 1.5 与 35 号 A-IPC 的对齐

```
35 号 §8.1 新增的错误码:
  AIRY_EIPC_HDRSIZE  (-44)  — 头部大小检查失败
  AIRY_EIPC_RESERVED (-45)  — reserved 字段非零
  AIRY_EIPC_FLAGS    (-46)  — flags 非法
  AIRY_EIPC_NOTSUPP  (-47)  — 不支持的 opcode/flag
  AIRY_EIPC_KFIFO    (-48)  — kfifo 入队失败
  AIRY_EIPC_RECLAIM  (-49)  — reclaim flag 置位
  AIRY_EIPC_CONTEXT  (-50)  — 上下文检查失败
  AIRY_EIPC_CRC32    (-51)  — CRC32 校验失败
  AIRY_EIPC_TIMEOUT  (-52)  — 超时
  
  AIRY_ECAP_BADGE    (-78)  — Badge 格式无效或 Random Tag 不匹配
  AIRY_ECAP_EPOCH    (-79)  — Badge Epoch 不匹配
  AIRY_ECAP_FORGED   (-80)  — Badge 伪造尝试
  AIRY_ECAP_PERM     (-81)  — 权限不足
  AIRY_ECAP_FROZEN   (-82)  — Ring 已冻结
  
  AIRY_FAULT_CAP_FORGED   (0x1001)  — Badge 伪造
  AIRY_FAULT_CAP_LEAK     (0x1002)  — Badge 泄漏
  AIRY_FAULT_RING_CORRUPT (0x1003)  — Ring 数据损坏

对齐状态: ✓ 一致
需要同步: 08-sc-error-contract.md §2.4 Capability 码空间
```

### 1.6 A-UEF 检查结论

```
一致性: ✓（需同步错误码新增项）
完整性: ⚠（[DSL] 码空间未定义具体值）
正确性: ✓
与 35 号对齐: ✓

发现的问题:
  P-A-UEF-01: 08-sc-error-contract.md 需新增 IPC 错误码 -44~-52
  P-A-UEF-02: 08-sc-error-contract.md 需新增 Capability 错误码 -78~-82
  P-A-UEF-03: 08-sc-error-contract.md 需新增 Fault 码 0x1001-0x1003
  P-A-UEF-04: 08-sc-error-contract.md 需补充 [DSL] 码空间具体值
```

---

## §2 A-ULP 检查（统一日志框架）

### 2.1 模块定位

```
模块: A-ULP (Unified Logging & Profiling Framework)
[SC] 头文件: kernel/include/airymax/log_types.h
[SC] 契约文档: 30-interfaces/09-sc-log-types-contract.md
日志记录格式: 128 字节固定长度
日志级别: 5 级（LOG_DEBUG~LOG_FATAL）
printk 映射: 8 级
```

### 2.2 一致性检查

| 检查项 | 现状 | 35 号设计 | 状态 |
|--------|------|----------|:---:|
| 日志记录格式（128B） | 已定义 | 35 号 §10.2 引用 | ✓ |
| 5 级日志枚举 | 已定义 | 不变 | ✓ |
| printk 8 级映射 | 已定义 | 不变 | ✓ |
| trace_id 字段对齐 | offset 8 | 35 号 Layout C v4 offset 8 | ✓ |
| timestamp_ns 字段对齐 | offset 16 | 35 号 Layout C v4 offset 16 | ✓ |
| magic 值区分 | log_types.h 与 ipc.h 不同 magic | 35 号 §10.2 一致 | ✓ |
| 禁止结构体复用 | 09 号 §5.4 | 35 号 §10.2 一致 | ✓ |

### 2.3 完整性检查

```
[SC] log_types.h 完整性:
  ✓ 128B 日志记录结构体定义
  ✓ 5 级日志枚举（LOG_DEBUG~LOG_FATAL）
  ✓ printk 8 级映射
  ✓ magic 值定义（与 ipc.h 区分）
  ✓ _Static_assert(sizeof == 128)

日志记录字段（128B）:
  offset  0: magic          (4B)
  offset  4: level          (1B)
  offset  5: facility       (1B)
  offset  6: reserved       (2B)
  offset  8: timestamp      (8B)  ← 与 ipc.h trace_id 对齐
  offset 16: caller_id      (8B)
  offset 24: payload[96]    (96B)
  offset 120: reserved      (8B)

与 Layout C v4 对齐:
  ✓ offset 8: log_types.h timestamp == ipc.h trace_id
  ✓ offset 16: log_types.h caller_id == ipc.h timestamp_ns
  ✓ 两者长度相同（128B），但语义不同，使用不同 magic
```

### 2.4 正确性检查

```
日志记录与 IPC 消息头的隔离:
  ✓ 不同 magic 值（避免混淆）
  ✓ 不同语义（日志记录 vs IPC 消息头）
  ✓ 禁止复用同一结构体（09 号 §5.4）

A-ULP 的依赖关系:
  ✓ A-ULP 不依赖 A-IPC（基础框架独立）
  ✓ A-IPC 依赖 A-ULP（fastpath 错误时记录日志）
  ✓ 无循环依赖

trace_id 全链路追踪:
  ✓ IPC 消息携带 trace_id（Layout C v4 offset 8）
  ✓ 日志记录携带 timestamp（log_types.h offset 8）
  ✓ 两者字段位置对齐，便于关联查询
```

### 2.5 与 35 号 A-IPC 的对齐

```
35 号 §10.2 A-ULP 对接:
  ✓ airy_log_record (128B) 日志记录格式
  ✓ 5 级日志枚举
  ✓ printk 8 级映射
  ✓ trace_id 字段贯穿 IPC 消息 + 日志记录

关键不变量:
  - airy_log_record (128B) 与 airy_ipc_msg_hdr (128B) 长度相同
  - 但语义不同，使用不同 magic 避免混淆
  - 禁止复用同一结构体（09 号 §5.4）

对齐状态: ✓ 完全一致
需要同步: 无（A-ULP 设计无需修改）
```

### 2.6 A-ULP 检查结论

```
一致性: ✓
完整性: ✓
正确性: ✓
与 35 号对齐: ✓

发现的问题:
  无（A-ULP 设计已完整，与 35 号 A-IPC 完全对齐）
```

---

## §3 A-UCS 检查（统一配置框架）

### 3.1 模块定位

```
模块: A-UCS (Unified Configuration Subsystem)
[SC] 头文件: kernel/include/airymax/config.h（待确认是否在 10 个 [SC] 头文件中）
配置分类:
  - [SC] 共享配置（跨端同步）
  - [IND] 独立配置（各自管理）
配置机制: sysctl + JSON 双向同步，RCU 指针原子切换
配置版本: AIRY_CONFIG_VERSION 字段，不匹配返回 AIRY_ECFGVERSION (-101)
```

### 3.2 一致性检查

| 检查项 | 现状 | 35 号设计 | 状态 |
|--------|------|----------|:---:|
| 配置分类（[SC]/[IND]） | 10-unify-design.md §6 | 35 号 §10.3 引用 | ✓ |
| RCU 热重载机制 | 10-unify-design.md §6 | 不变 | ✓ |
| AIRY_CONFIG_VERSION | 已定义 | 35 号 §10.3 引用 | ✓ |
| AIRY_ECFGVERSION (-101) | 已定义 | 35 号 §8.1 一致 | ✓ |
| A-IPC 配置项 | 未明确 | 35 号 §10.3 新增 | ⚠ 需补充 |

### 3.3 完整性检查

```
A-UCS 配置项完整性:
  ✓ AIRY_CONFIG_VERSION 字段
  ✓ RCU 指针原子切换机制
  ✓ sysctl + JSON 双向同步
  ✗ A-IPC 具体配置项未明确列出 → 需补充

A-IPC 需要的配置项（35 号 §10.3）:
  - ring 配置: kfifo 大小、registered buffer 大小
  - Badge 配置: Epoch 初始值、Random Tag 长度
  - [DSL] 模式开关: AIRY_SC_FALLBACK
  - agent_caps[] 容量: 1024（可配置？）
  - fastpath 超时: SLOW_SEND 超时阈值
  - CPU 亲和性绑定: daemon 绑定的 CPU 列表

缺失项:
  - A-IPC 配置项清单未在 A-UCS 文档中列出
  - 建议: 在 20-modules/11-unified-config.md 中新增 A-IPC 配置项章节
```

### 3.4 正确性检查

```
A-UCS 的依赖关系:
  ✓ A-UCS 不依赖 A-IPC（基础框架独立）
  ✓ A-IPC 依赖 A-UCS（读取配置初始化）
  ✓ 无循环依赖

配置热重载与 A-IPC 的交互:
  - ring 配置变更: 需要重建 ring（不能热重载）
  - Badge 配置变更: 可以热重载（不影响在途 Badge）
  - [DSL] 模式开关: 需要重启相关 daemon
  - agent_caps[] 容量: 需要重新分配数组（不能热重载）

潜在问题:
  - 部分配置项不支持热重载，但 A-UCS 默认热重载机制
  - 建议: 在 A-UCS 文档中明确标注哪些配置项支持热重载，哪些需要重启
```

### 3.5 与 35 号 A-IPC 的对齐

```
35 号 §10.3 A-UCS 对接:
  ✓ ring 配置（kfifo 大小、registered buffer 大小）
  ✓ Badge 配置（Epoch 初始值、Random Tag 长度）
  ✓ [DSL] 模式开关（AIRY_SC_FALLBACK）

对接点:
  - 配置文件 /etc/agentrt/ipc.conf
  - sysfs 接口 /sys/kernel/airy/ipc/
  - 进程启动时读取配置 → 初始化 ring + kfifo + agent_caps[]

对齐状态: ✓ 一致
需要同步: 20-modules/11-unified-config.md 需新增 A-IPC 配置项章节
```

### 3.6 A-UCS 检查结论

```
一致性: ✓
完整性: ⚠（A-IPC 配置项未在 A-UCS 文档中列出）
正确性: ✓
与 35 号对齐: ✓

发现的问题:
  P-A-UCS-01: 20-modules/11-unified-config.md 需新增 A-IPC 配置项章节
  P-A-UCS-02: A-UCS 文档需明确标注哪些配置项支持热重载，哪些需要重启
```

---

## §4 A-ULS 检查（统一生命周期框架）

### 4.1 模块定位

```
模块: A-ULS (Unified Lifecycle Supervision Framework)
核心组件:
  - Micro-Supervisor（内核侧，冷酷执法）
  - Macro-Supervisor（用户侧，温情裁决）
Agent 生命周期: 8 态
调度策略: sched_tac（策略性调度）
执法机制: 内核侧立即冻结异常 Agent
```

### 4.2 一致性检查

| 检查项 | 现状 | 35 号设计 | 状态 |
|--------|------|----------|:---:|
| 8 态生命周期 | 10-unify-design.md §7 | 不变 | ✓ |
| 双 Supervisor 模型 | 10-unify-design.md §7 | 不变 | ✓ |
| sched_tac 调度策略 | 10-unify-design.md §1 | 不变 | ✓ |
| ring->frozen 标志位 | A-IPC C-S0 检查 | 35 号 §5.2 实现 | ✓ |
| FREEZE opcode (0x0005) | 未定义 | 35 号 §4.1 新增 | ⚠ 需同步 |
| Badge 撤销与 A-ULS 解耦 | 未明确 | 35 号 §10.4 明确 | ✓ |

### 4.3 完整性检查

```
A-ULS 8 态生命周期:
  ✓ 8 态完整定义（10-unify-design.md §7）
  ✓ 与 Linux 进程状态映射
  ✓ sched_tac 调度承载

A-ULS 与 A-IPC 的交互:
  ✓ ring->frozen 标志位（C-S0 检查）
  ✓ FREEZE opcode（35 号 §4.1）
  ✓ Badge 撤销通过 atomic_inc（与 A-ULS 解耦）

缺失项:
  - A-ULS 触发 ring 冻结的具体流程未明确
  - 建议: 在 A-ULS 文档中新增"通过 A-IPC FREEZE opcode 冻结 ring"章节
```

### 4.4 正确性检查

```
A-ULS 的依赖关系:
  ✓ A-ULS 依赖 A-IPC（通过 io_uring 执行裁决）
  ✓ A-IPC 不依赖 A-ULS（ring->frozen 是简单的标志位）
  ✓ 无循环依赖

冷酷执法与温情的裁决:
  ✓ 内核侧 Micro-Supervisor: 检测异常 → 立即冻结（FREEZE opcode）
  ✓ 用户侧 Macro-Supervisor: 根据 A-ULP 日志 → 人性化裁决
  ✓ 两者通过 A-IPC 通信

Badge 撤销与 A-ULS 的解耦:
  ✓ Badge 撤销 = atomic_inc（无阻塞，无 drain）
  ✓ 不需要 A-ULS 介入（撤销是 sec_d 的特权操作）
  ✓ A-ULS 可以观察 Badge 撤销事件（通过 A-ULP 日志）
```

### 4.5 与 35 号 A-IPC 的对齐

```
35 号 §10.4 A-ULS 对接:
  ✓ ring 生命周期（创建/冻结/销毁）
  ✓ Badge 生命周期（编译/撤销/过期）
  ✓ C-S0 ring->frozen 检查（A-ULS 控制）

对接点:
  - ring->frozen 标志位（C-S0 检查）
  - FREEZE opcode（0x0005）触发 ring 冻结
  - sec_d 撤销 Badge 时通知 A-ULS（可选）

对齐状态: ✓ 一致
需要同步: 20-modules/09-kernel-agent-supervisor.md 需新增 FREEZE opcode 章节
```

### 4.6 A-ULS 检查结论

```
一致性: ✓
完整性: ⚠（A-ULS 触发 ring 冻结的具体流程未明确）
正确性: ✓
与 35 号对齐: ✓

发现的问题:
  P-A-ULS-01: 20-modules/09-kernel-agent-supervisor.md 需新增 FREEZE opcode 章节
  P-A-ULS-02: A-ULS 文档需明确 Badge 撤销与 A-ULS 的解耦关系
```

---

## §5 A-IPC 检查（基于 35 号设计）

### 5.1 模块定位

```
模块: A-IPC (Unified Airymax IPC Fabric)
[SC] 头文件: kernel/include/airymax/ipc.h
[SC] 契约文档: 30-interfaces/02-ipc-protocol.md + 07-ipc-fastpath.md
架构: 单平面（io_uring 数据面 + 4 个控制面 syscall）
消息头: Layout C v4（128 字节）
fastpath: 7 态状态机，C-S0~C-S11 校验链
Badge: 64-bit Native Word（Epoch + Random Tag + Perms）
```

### 5.2 一致性检查（35 号设计内部）

| 检查项 | 35 号章节 | 状态 |
|--------|----------|:---:|
| Layout C v4（128 字节） | §2.1 | ✓ |
| opcode 完整定义 | §4.1 | ✓ |
| syscall 12→4 映射 | §1.3 | ✓ |
| 7 态状态机 | §5.1 | ✓ |
| fastpath 完整实现 | §5.2 | ✓ |
| Badge 64-bit 格式 | §6.1 | ✓ |
| Badge 编译流程 | §6.2 | ✓ |
| Badge 校验流程 | §6.3 | ✓ |
| 数据结构隔离 | §7.1 | ✓ |
| 代码组织隔离 | §7.2 | ✓ |
| CBMC 全函数验证 | §7.3 | ✓ |
| 错误码定义 | §8.1 | ✓ |
| [DSL] 降级模式 | §9 | ✓ |
| 五模块对接 | §10 | ✓ |
| IRON-9 v3 四层映射 | §11 | ✓ |
| §10 SSoT 对齐 | §12 | ✓ |

### 5.3 完整性检查

```
[SC] ipc.h 完整性:
  ✓ Layout C v4 消息头定义（128 字节）
  ✓ opcode 枚举（7 个: SEND/RECV/SEND_BATCH/CANCEL/FREEZE/CAP_REQUEST/CAP_RESPONSE）
  ✓ flags 位定义（5 个: ZEROCOPY/CAP_CARRY/ENCRYPT/COMPRESS/BATCH_TAIL）
  ✓ Badge 位布局宏（EPOCH/RANDTAG/PERMS）
  ✓ Capability 权限位（7 个: SEND/RECV/CALL/GRANT/REVOKE/FREEZE/BATCH）
  ✓ _Static_assert(sizeof == 128)

[SC] error.h 完整性（A-IPC 相关）:
  ✓ IPC 错误码（-41~-52）
  ✓ Capability 错误码（-71~-82）
  ✓ Fault 码（0x1001-0x1003）

[SS] 语义同源层完整性:
  ✓ Badge 校验机制（airy_cap_badge_ok）
  ✓ agent_caps[] 静态数组
  ✓ airy_global_epoch
  ✓ Random Tag 生成
  ✓ C-S9 校验逻辑
  ✓ sec_d Badge 编译流程

[IND] 完全独立层完整性:
  ✓ agentrt 用户态: capability_badge=0
  ✓ agentrt 用户态: 传统 cap_t 引用
  ✓ agent-linux 内核: capability_badge + C-S9

[DSL] 降级生存层完整性:
  ✓ capability_badge=0
  ✓ C-S9 跳过
  ✓ 退化到 radix tree 兜底
  ✓ 仅支持 SEND/RECV opcode
```

### 5.4 正确性检查

```
6 条硬约束自检（35 号 §15.1）:
  ✓ H1: Layout C v4 总长 128 字节，magic 0x41524531
  ✓ H2: capability_badge 进 [SC]，校验机制属 [SS]
  ✓ H3: agentrt 用户态 capability_badge=0
  ✓ H4: agent-linux 内核 capability_badge 由 sec_d 编译
  ✓ H5: 纯 C LSM 职责不变，Badge 校验是 fastpath 内联
  ✓ H6: [DSL] 降级模式 capability_badge=0，跳过 C-S9

7 颗螺丝自检（35 号 §15.2）:
  ✓ 1. Epoch drain 5ms 阻塞 → 1 行 atomic_inc
  ✓ 2. CRC32 不覆盖 capability_badge → 覆盖 header[0:52)
  ✓ 3. NULL Badge 硬编码特例 → CAP_REQUEST opcode
  ✓ 4. 全局/独立 Epoch 矛盾 → 1 个全局 atomic_t
  ✓ 5. seq_num + negotiated_ver 无协议 → 移除
  ✓ 6. SLOW_PATH 合并丢失语义 → SLOW_SEND/SLOW_RECV 分离
  ✓ 7. __future[66] 超 50% 保留 → reserved[72]

三大物理鸿沟自检（35 号 §15.3）:
  ✓ 1. uring_lock 持有 wake_up → NONBLOCK + io-wq
  ✓ 2. MMU 页表开销 → registered buffer
  ✓ 3. CFS 调度迁移 → C-S5 优化条件 + CPU 亲和性
```

### 5.5 A-IPC 检查结论

```
一致性: ✓
完整性: ✓
正确性: ✓
与 35 号对齐: ✓（自身就是 35 号设计）

发现的问题:
  无（A-IPC 设计已完整自洽）
```

---

## §6 跨模块一致性检查

### 6.1 模块间接口一致性

```
A-UEF ↔ A-IPC:
  ✓ A-IPC 使用 A-UEF 的错误码空间
  ✓ A-IPC 新增错误码（-44~-52, -78~-82, 0x1001-0x1003）符合 A-UEF 分配
  ⚠ 08-sc-error-contract.md 需同步更新

A-ULP ↔ A-IPC:
  ✓ A-IPC 使用 A-ULP 的日志记录格式
  ✓ trace_id 字段位置对齐（offset 8）
  ✓ timestamp_ns 字段位置对齐（offset 16）
  ✓ 无需修改 A-ULP 文档

A-UCS ↔ A-IPC:
  ✓ A-IPC 使用 A-UCS 的配置机制
  ⚠ A-IPC 配置项未在 A-UCS 文档中列出
  ⚠ 20-modules/11-unified-config.md 需新增 A-IPC 配置项章节

A-ULS ↔ A-IPC:
  ✓ A-ULS 通过 A-IPC 的 FREEZE opcode 冻结 ring
  ✓ A-IPC 的 C-S0 检查 ring->frozen
  ⚠ A-ULS 触发 ring 冻结的具体流程未明确
  ⚠ 20-modules/09-kernel-agent-supervisor.md 需新增 FREEZE opcode 章节
```

### 6.2 模块间依赖关系正确性

```
依赖关系图（10-unify-design.md §3）:

  A-UEF ←─── A-ULP
    ↑           ↑
    │           │
  A-UCS ←─── A-ULS ←─── A-IPC
    ↑                  ↑
    └──────────────────┘
       （A-IPC 依赖 A-UCS）

依赖关系验证:
  ✓ A-UEF: 无依赖（最底层）
  ✓ A-ULP: 依赖 A-UEF
  ✓ A-UCS: 依赖 A-UEF
  ✓ A-ULS: 依赖 A-UEF + A-ULP + A-UCS + A-IPC
  ✓ A-IPC: 依赖 A-UEF + A-ULP + A-UCS

循环依赖检查:
  ✓ 无循环依赖
  
潜在问题:
  - A-ULS 依赖 A-IPC（通过 io_uring 执行裁决）
  - A-IPC 的 ring->frozen 由 A-ULS 控制
  - 这是单向依赖（A-ULS → A-IPC），不是循环依赖
  - 但 A-IPC 的 C-S0 检查 ring->frozen，意味着 A-IPC 需要感知 A-ULS 的状态
  - 解决方案: ring->frozen 是简单的标志位，A-ULS 设置，A-IPC 读取，无循环依赖
```

### 6.3 共享数据结构一致性

```
128 字节固定长度结构体:
  - airy_ipc_msg_hdr（A-IPC）: 128B
  - airy_log_record（A-ULP）: 128B

字段对齐:
  ✓ offset 8: ipc.h trace_id == log_types.h timestamp
  ✓ offset 16: ipc.h timestamp_ns == log_types.h caller_id
  ✓ 两者使用不同 magic 避免混淆
  ✓ 禁止复用同一结构体

[SC] 共享契约层 10 个头文件:
  ✓ ipc.h（A-IPC）
  ✓ error.h（A-UEF）
  ✓ log_types.h（A-ULP）
  ✓ sched.h（A-ULS/sched_tac）
  ✓ memory_types.h（MemoryRovol）
  ✓ security_types.h（sec_d）
  ✓ cognition_types.h（cogn_d）
  ✓ syscalls.h（syscall 编号）
  ✓ uapi_compat.h（UAPI 兼容性）
  ✓ lsm_types.h（纯 C LSM）

  注意: config.h 是否在 10 个 [SC] 头文件中？
  - 10-unify-design.md §10 SSoT 声明: 10 个头文件
  - 120-cross-project-code-sharing.md §2.1: 10 个头文件清单
  - config.h 不在 10 个 [SC] 头文件中
  - A-UCS 的配置是 [IND] 独立层，不共享
```

### 6.4 错误码空间一致性

```
错误码空间分配（A-UEF 定义，所有模块遵守）:

  POSIX [-1, -40]:        38 个错误码（所有模块可用）
  IPC [-41, -70]:         12 个错误码（A-IPC 专用）+ 18 个预留
  Capability [-71, -100]: 12 个错误码（A-IPC/sec_d 专用）+ 18 个预留
  [SC] [-101, -200]:      100 个槽位（[SC] 共享契约专用）
  [DSL] [-201, -300]:     100 个槽位（[DSL] 降级生存专用）
  Fault [0x1000, 0x1FFF]: 4096 个槽位（严重错误，正数）

跨模块错误码使用:
  ✓ A-IPC 使用 IPC + Capability + Fault 码空间
  ✓ A-ULS 使用 POSIX + Fault 码空间
  ✓ A-UCS 使用 POSIX + [SC] 码空间（AIRY_ECFGVERSION -101）
  ✓ A-ULP 使用 POSIX 码空间
  ✓ A-UEF 定义所有码空间

无冲突:
  ✓ 各模块使用的码空间不重叠
  ✓ 35 号新增错误码（-44~-52, -78~-82, 0x1001-0x1003）在正确码空间
```

---

## §7 与 IRON-9 v3 四层模型的对齐检查

### 7.1 [SC] 共享契约层

```
[SC] 层内容（10 个头文件）:
  ✓ ipc.h —— A-IPC 消息头定义
  ✓ error.h —— A-UEF 错误码定义
  ✓ log_types.h —— A-ULP 日志记录定义
  ✓ sched.h —— A-ULS 调度类型定义
  ✓ memory_types.h —— MemoryRovol 类型定义
  ✓ security_types.h —— sec_d 安全类型定义
  ✓ cognition_types.h —— cogn_d 认知类型定义
  ✓ syscalls.h —— syscall 编号定义
  ✓ uapi_compat.h —— UAPI 兼容性定义
  ✓ lsm_types.h —— 纯 C LSM 类型定义

[SC] 层物理宿主:
  ✓ kernel/include/airymax/（10-unify-design.md §10 SSoT）

[SC] 层变更分类（120 号 §7.4）:
  ✓ 新增字段（向后兼容）: 需双端同步
  ✓ 修改字段语义（破坏性）: 禁止
  ✓ magic 值: 一经发布即冻结

35 号对 [SC] 层的变更:
  ✓ ipc.h: 新增 capability_badge 字段 → 向后兼容
  ✓ ipc.h: 新增 CAP_REQUEST/CAP_RESPONSE opcode → 向后兼容
  ✓ ipc.h: 新增 AIRY_IPC_F_CAP_CARRY 标志位 → 向后兼容
  ✓ error.h: 新增 AIRY_ECAP_BADGE/EPOCH/FORGED/PERM/FROZEN → 向后兼容
```

### 7.2 [SS] 语义同源层

```
[SS] 层内容（不在 [SC] 头文件中，在实现侧）:

A-IPC [SS] 层:
  ✓ Badge 校验机制: airy_cap_badge_ok() 内联函数
  ✓ agent_caps[] 静态数组: 内核内存
  ✓ airy_global_epoch: atomic_t
  ✓ Random Tag 生成: get_random_bytes()
  ✓ C-S9 校验逻辑: READ_ONCE + 位运算 + 比较
  ✓ sec_d Badge 编译流程: airy_sys_call(COMPILE_BADGE)

A-UEF [SS] 层:
  ✓ 错误码语义解释（每个错误码的触发条件）
  ✓ Fault 码处理流程（sec_d 审计 + Agent 终止）

A-ULP [SS] 层:
  ✓ 日志记录写入流程（per-cpu ring buffer）
  ✓ printk 映射逻辑

A-UCS [SS] 层:
  ✓ RCU 指针原子切换
  ✓ sysctl + JSON 双向同步

A-ULS [SS] 层:
  ✓ 8 态生命周期转换逻辑
  ✓ 双 Supervisor 模型
  ✓ sched_tac 调度策略

[SS] 层契约:
  ✓ agentrt 与 agent-linux 共享 [SC] 数据结构定义
  ✓ 校验机制/实现逻辑属于 [SS] 语义同源层
  ✓ 34 号 §2 核心论证: [SC] 共享数据结构定义，不是实现语义
```

### 7.3 [IND] 完全独立层

```
[IND] 层内容:

agentrt 用户态:
  ✓ 传统 cap_t 引用 + airy_ipc_send() 库函数
  ✓ 不使用 capability_badge 字段（始终为 0）
  ✓ 不调用 sec_d 的 Badge 编译接口

agent-linux 内核:
  ✓ capability_badge + C-S9 内联校验
  ✓ 不依赖 agentrt 的 cap_t 引用机制

[IND] 层契约:
  ✓ agentrt 不感知 capability_badge 字段的存在
  ✓ agent-linux 不依赖 agentrt 的 cap_t 引用机制
  ✓ 两者通过 [SC] 数据结构 + [SS] 语义同源保持契约一致
```

### 7.4 [DSL] 降级生存层

```
[DSL] 层内容:

A-IPC [DSL] 层（35 号 §9）:
  ✓ capability_badge 字段存在但被忽略（值=0）
  ✓ C-S9 跳过 Badge 校验
  ✓ 退化到 radix tree 兜底路径
  ✓ 仅支持 SEND/RECV opcode
  ✓ 使用 AIRY_ECAP_RADIX_MISS/STATIC_KEY 错误码

A-UEF [DSL] 层:
  ✓ [DSL] 码空间 [-201, -300] 预留
  ⚠ 具体错误码未定义

A-ULP [DSL] 层:
  ✓ 日志记录格式不变（128B）
  ✓ 日志级别降级（仅 LOG_ERROR~LOG_FATAL）

A-UCS [DSL] 层:
  ✓ AIRY_SC_FALLBACK 编译开关
  ✓ 配置项简化

A-ULS [DSL] 层:
  ✓ 8 态生命周期简化为 3 态（RUNNING/FROZEN/DEAD）
  ✓ 双 Supervisor 简化为单 Supervisor

[DSL] 层触发条件:
  ✓ [SC] 共享契约层不可用
  ✓ 内核编译时定义 AIRY_SC_FALLBACK
  ✓ 运行时检测到版本不匹配

[DSL] 层退出:
  ✓ 重新建立 [SC] 共享契约
  ✓ 重启相关 daemon
  ✓ 取消 AIRY_SC_FALLBACK 编译选项
```

---

## §8 与 35 号 A-IPC 设计的对齐检查

### 8.1 6 条硬约束 H1-H6 的跨模块影响

```
H1: Layout C v4 总长 128 字节，magic 0x41524531
  影响: A-IPC [SC] ipc.h
  跨模块: A-ULP（128B 对齐，但不同 magic）
  状态: ✓

H2: capability_badge 字段进入 [SC] ipc.h，但校验机制属于 [SS] 层
  影响: A-IPC [SC] + [SS]
  跨模块: 无（A-UEF/A-ULP/A-UCS/A-ULS 不涉及）
  状态: ✓

H3: agentrt 用户态 capability_badge 始终为 0
  影响: A-IPC [IND] 层
  跨模块: 无（仅 agentrt 用户态）
  状态: ✓

H4: agent-linux 内核 capability_badge 由 sec_d 编译
  影响: A-IPC [SS] 层 + A-ULS（sec_d 是 A-ULS 的组件）
  跨模块: A-ULS 需明确 sec_d 的 Badge 编译职责
  状态: ⚠ 需同步 A-ULS 文档

H5: 纯 C LSM 模块职责不变，Badge 校验是其 fastpath 内联
  影响: A-IPC [SS] 层 + 纯 C LSM 模块
  跨模块: 纯 C LSM 模块文档需明确 Badge 校验是 fastpath 内联
  状态: ⚠ 需同步纯 C LSM 文档

H6: [DSL] 降级模式下 capability_badge 字段存在但被忽略
  影响: A-IPC [DSL] 层
  跨模块: A-UCS（AIRY_SC_FALLBACK 开关）
  状态: ✓
```

### 8.2 35 号 §10 五模块对接的落地检查

```
35 号 §10.1 A-UEF 对接:
  ✓ AIRY_EIPC_* 错误码（IPC 码空间）
  ✓ AIRY_ECAP_* 错误码（Capability 码空间）
  ✓ AIRY_FAULT_* 错误码（Fault 码空间）
  状态: ✓（需同步 08-sc-error-contract.md）

35 号 §10.2 A-ULP 对接:
  ✓ airy_log_record (128B) 日志记录格式
  ✓ trace_id 字段贯穿 IPC 消息 + 日志记录
  状态: ✓（无需修改 A-ULP 文档）

35 号 §10.3 A-UCS 对接:
  ✓ ring 配置（kfifo 大小、registered buffer 大小）
  ✓ Badge 配置（Epoch 初始值、Random Tag 长度）
  ✓ [DSL] 模式开关（AIRY_SC_FALLBACK）
  状态: ⚠（需同步 20-modules/11-unified-config.md）

35 号 §10.4 A-ULS 对接:
  ✓ ring->frozen 标志位（C-S0 检查）
  ✓ FREEZE opcode（0x0005）触发 ring 冻结
  ✓ Badge 撤销（atomic_inc）与 A-ULS 解耦
  状态: ⚠（需同步 20-modules/09-kernel-agent-supervisor.md）

35 号 §10.5 A-IPC 自身:
  ✓ Layout C v4 完整定义
  ✓ opcode 完整定义
  ✓ syscall 12→4 映射
  ✓ fastpath 7 态状态机
  ✓ Badge 安全模型
  状态: ✓
```

---

## §9 发现的问题清单

### 9.1 问题汇总

| # | 问题 | 模块 | 严重度 | 修正建议 |
|---|------|------|:---:|---------|
| P-A-UEF-01 | 08-sc-error-contract.md 需新增 IPC 错误码 -44~-52 | A-UEF | P0 | 同步更新 |
| P-A-UEF-02 | 08-sc-error-contract.md 需新增 Capability 错误码 -78~-82 | A-UEF | P0 | 同步更新 |
| P-A-UEF-03 | 08-sc-error-contract.md 需新增 Fault 码 0x1001-0x1003 | A-UEF | P0 | 同步更新 |
| P-A-UEF-04 | 08-sc-error-contract.md 需补充 [DSL] 码空间具体值 | A-UEF | P1 | 同步更新 |
| P-A-UCS-01 | 20-modules/11-unified-config.md 需新增 A-IPC 配置项章节 | A-UCS | P1 | 同步更新 |
| P-A-UCS-02 | A-UCS 文档需明确标注哪些配置项支持热重载 | A-UCS | P2 | 同步更新 |
| P-A-ULS-01 | 20-modules/09-kernel-agent-supervisor.md 需新增 FREEZE opcode 章节 | A-ULS | P1 | 同步更新 |
| P-A-ULS-02 | A-ULS 文档需明确 Badge 撤销与 A-ULS 的解耦关系 | A-ULS | P2 | 同步更新 |
| P-SC-01 | 纯 C LSM 模块文档需明确 Badge 校验是 fastpath 内联 | 纯 C LSM | P1 | 同步更新 |
| P-SC-02 | sec_d 文档需明确 Badge 编译职责 | sec_d | P1 | 同步更新 |

### 9.2 问题分类

```
P0 问题（必须立即修正）:
  - P-A-UEF-01/02/03: 错误码同步（3 项）
  → 影响: 35 号 A-IPC 设计的错误码无法落地
  → 修正: 同步更新 08-sc-error-contract.md

P1 问题（需要同步更新）:
  - P-A-UEF-04: [DSL] 码空间具体值
  - P-A-UCS-01: A-IPC 配置项章节
  - P-A-ULS-01: FREEZE opcode 章节
  - P-SC-01: 纯 C LSM Badge 校验
  - P-SC-02: sec_d Badge 编译职责
  → 影响: 五模块对接的细节不完整
  → 修正: 同步更新相关文档

P2 问题（建议同步更新）:
  - P-A-UCS-02: 配置项热重载标注
  - P-A-ULS-02: Badge 撤销解耦说明
  → 影响: 文档完整性
  → 修正: 同步更新相关文档
```

---

## §10 同步更新文档清单

### 10.1 与 34 号 §6.2 清单的对齐

34 号 §6.2 列出的 11 份文档同步清单:

| # | 文档 | 34 号修改内容 | 36 号新增问题 | 优先级 |
|---|------|-------------|-------------|:---:|
| 1 | 10-unify-design.md §8 | A-IPC 章节: 双平面 → 单平面 | - | P0 |
| 2 | 10-unify-design.md §10 | SSoT 新增 "A-IPC 采用 Capability Folding" | - | P0 |
| 3 | 30-interfaces/01-syscalls.md | syscall 表 12 → 4 | - | P0 |
| 4 | 30-interfaces/02-ipc-protocol.md | Layout C v4, opcode 表 | - | P0 |
| 5 | 30-interfaces/07-ipc-fastpath.md | C-S9, 7 态状态机 | - | P0 |
| 6 | 120-cross-project-code-sharing.md §2.7 | [SC] ipc.h Layout C v4 | - | P0 |
| 7 | 30-interfaces/08-sc-error-contract.md §2.4 | Capability 码空间新增 | P-A-UEF-01/02/03/04 | P0 |
| 8 | 110-security/03-capability-model.md | radix tree → Epoch + 静态数组 | P-SC-01/02 | P1 |
| 9 | 10-architecture/11-degraded-survival-layer.md §2.2 | [DSL] ipc.h 降级块 | - | P1 |
| 10 | 40-dataflows/03-ipc-flow.md | 消除控制面数据流 | - | P1 |
| 11 | 170-performance/03-ipc-performance.md | fastpath 延迟数值更新 | - | P2 |

### 10.2 36 号新增的同步更新文档

| # | 文档 | 新增内容 | 对应问题 | 优先级 |
|---|------|---------|---------|:---:|
| 12 | 20-modules/11-unified-config.md | A-IPC 配置项章节 | P-A-UCS-01/02 | P1 |
| 13 | 20-modules/09-kernel-agent-supervisor.md | FREEZE opcode 章节 + Badge 撤销解耦 | P-A-ULS-01/02 | P1 |
| 14 | 20-modules/10-user-supervisor-daemon.md | Badge 撤销解耦说明 | P-A-ULS-02 | P2 |
| 15 | 110-security/02-lsm-framework.md | Badge 校验是 fastpath 内联 | P-SC-01 | P1 |
| 16 | 110-security/01-security-daemon.md | sec_d Badge 编译职责 | P-SC-02 | P1 |

### 10.3 同步更新总清单

```
P0 同步（7 份，与 34 号 §6.2 一致）:
  1. 10-unify-design.md §8
  2. 10-unify-design.md §10
  3. 30-interfaces/01-syscalls.md
  4. 30-interfaces/02-ipc-protocol.md
  5. 30-interfaces/07-ipc-fastpath.md
  6. 50-engineering-standards/120-cross-project-code-sharing.md §2.7
  7. 30-interfaces/08-sc-error-contract.md §2.4

P1 同步（6 份，含 34 号 3 份 + 36 号 3 份）:
  8. 110-security/03-capability-model.md（34 号）
  9. 10-architecture/11-degraded-survival-layer.md §2.2（34 号）
  10. 40-dataflows/03-ipc-flow.md（34 号）
  11. 20-modules/11-unified-config.md（36 号新增）
  12. 20-modules/09-kernel-agent-supervisor.md（36 号新增）
  13. 110-security/02-lsm-framework.md（36 号新增）
  14. 110-security/01-security-daemon.md（36 号新增）

P2 同步（3 份，含 34 号 1 份 + 36 号 2 份）:
  15. 170-performance/03-ipc-performance.md（34 号）
  16. 20-modules/10-user-supervisor-daemon.md（36 号新增）
  17. 08-sc-error-contract.md [DSL] 码空间（36 号新增，合并到 P0 第 7 份）

总计: 17 份文档同步更新（34 号 11 份 + 36 号新增 6 份）
```

---

## §11 五模块自洽性最终评估

### 11.1 自洽性评分

| 模块 | 一致性 | 完整性 | 正确性 | 与 35 号对齐 | 综合 |
|------|:---:|:---:|:---:|:---:|:---:|
| A-UEF | ✓ | ⚠ | ✓ | ✓ | 良（需同步错误码） |
| A-ULP | ✓ | ✓ | ✓ | ✓ | 优 |
| A-UCS | ✓ | ⚠ | ✓ | ✓ | 良（需补充配置项） |
| A-ULS | ✓ | ⚠ | ✓ | ✓ | 良（需补充 FREEZE） |
| A-IPC | ✓ | ✓ | ✓ | ✓ | 优 |

### 11.2 跨模块自洽性评分

| 检查项 | 状态 |
|--------|:---:|
| 模块间接口一致性 | ✓ |
| 模块间依赖关系正确性 | ✓ |
| 共享数据结构一致性 | ✓ |
| 错误码空间一致性 | ✓ |
| [SC] 共享契约层完整性 | ✓ |
| [SS] 语义同源层清晰度 | ✓ |
| [IND] 完全独立层无依赖 | ✓ |
| [DSL] 降级生存层可生存 | ✓ |

### 11.3 最终评估

```
五模块自洽性: 优（仅需同步更新文档，无设计缺陷）

论证:
  1. A-IPC 重构（35 号设计）没有破坏五模块的依赖关系
  2. 6 条硬约束 H1-H6 的跨模块影响全部可控
  3. IRON-9 v3 四层模型的对齐完整
  4. 发现的 10 个问题全部是文档同步问题，不是设计缺陷
  5. 17 份文档同步更新后，五模块完全自洽

与 34 号论证的一致性:
  ✓ 34 号 §6.1 决策: 采用 Capability Folding 重构
  ✓ 34 号 §6.2 清单: 11 份文档同步（36 号扩展为 17 份）
  ✓ 34 号 §6.3 硬约束: H1-H6 全部满足
  ✓ 34 号 §6.4 错误码: 修正后正确

与 35 号设计的一致性:
  ✓ 35 号 §10 五模块对接: 全部落地
  ✓ 35 号 §11 IRON-9 v3 四层映射: 完整
  ✓ 35 号 §12 §10 SSoT 对齐: 完整
  ✓ 35 号 §15 设计完整性自检: 全部通过
```

---

## §12 检查结论

### 12.1 一句话结论

**Airymax Unify Design 五模块（A-UEF/A-ULP/A-UCS/A-ULS/A-IPC）在 35 号 A-IPC 最终设计下保持自洽，发现的 10 个问题全部是文档同步问题（非设计缺陷），通过 17 份文档同步更新后五模块完全一致、完整、正确。**

### 12.2 检查的局限性

```
1. 文档同步未执行: 本检查仅识别问题，未实际修改文档
2. 代码未实现: 0 行代码现状下，无法验证运行时行为
3. 性能数据基于理论: fastpath ~158ns 是理论推导
4. CBMC 验证未实证: 工具链可行性需要在 Phase 3 验证
```

### 12.3 下一步

```
1. 实施前: 同步更新 17 份文档（§10.3 清单）
2. Phase 1: [SC] 头文件更新（35 号 §13.1）
3. Phase 2: fastpath 实现（35 号 §13.2）
4. Phase 3: 验证（35 号 §13.3）
5. Phase 4: 文档同步（35 号 §13.4）

五模块检查完成。A-IPC 作为"第一块基石"的形状已确定，五模块体系自洽。
```

---

## §13 附录：五模块检查矩阵

### 13.1 完整检查矩阵

| 检查维度 | A-UEF | A-ULP | A-UCS | A-ULS | A-IPC |
|---------|:---:|:---:|:---:|:---:|:---:|
| [SC] 头文件 | error.h | log_types.h | - | sched.h | ipc.h |
| [SC] 契约文档 | 08-sc | 09-sc | - | - | 02/07 |
| 错误码空间 | 全部 | POSIX | POSIX+[SC] | POSIX+Fault | IPC+Cap+Fault |
| 日志记录 | - | 128B | - | - | 透传 trace_id |
| 配置项 | - | - | RCU 热重载 | - | ring/Badge/[DSL] |
| 生命周期 | - | - | - | 8 态 | ring 冻结 |
| [SS] 语义同源 | 错误码语义 | 日志写入 | RCU 切换 | 8 态转换 | Badge 校验 |
| [IND] 完全独立 | - | - | [IND] 配置 | - | agentrt=0 |
| [DSL] 降级生存 | [DSL] 码 | LOG_ERROR+ | AIRY_SC_FALLBACK | 3 态简化 | badge=0 |
| 与 35 号对齐 | ⚠ 同步 | ✓ | ⚠ 补充 | ⚠ 补充 | ✓ |
| 跨模块接口 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 依赖关系 | 无依赖 | A-UEF | A-UEF | A-UEF+ULP+UCS+IPC | A-UEF+ULP+UCS |
| 循环依赖 | 无 | 无 | 无 | 无 | 无 |

### 13.2 文档同步优先级矩阵

| 优先级 | 文档数 | 文档清单 |
|--------|:---:|---------|
| P0 | 7 | 10-unify-design §8/§10, 01-syscalls, 02-ipc-protocol, 07-ipc-fastpath, 120-cross-project §2.7, 08-sc-error-contract |
| P1 | 7 | 03-capability-model, 11-degraded-survival §2.2, 03-ipc-flow, 11-unified-config, 09-kernel-agent-supervisor, 02-lsm-framework, 01-security-daemon |
| P2 | 3 | 03-ipc-performance, 10-user-supervisor-daemon, 08-sc-error-contract [DSL] |
| 总计 | 17 | - |

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. | Airymax Unify Design 五模块全面检查 | v1.0 | 2026-07-18
