# A-IPC Capability Folding 融合完整方案

## "以 Native Word（Badge + Epoch）为基石的 Unified Airymax IPC Fabric 系统性重设计"

> **文档性质**：agent-linux A-IPC 模块的系统性重设计方案
> **撰写日期**：2026-07-18
> **方案来源**：基于 16~23 号共 8 份 IPC 审查报告的发现与推论
> **审查范围**：Layout C 消息头 / fastpath 状态机 / 控制面与数据面关系 / daemon 通信拓扑 / 与 5 模块的交互
> **设计哲学**：「控制面编译，数据面执行」— 能力决策在连接建立期一次完成，编译为 64-bit Native Word 嵌入消息头，数据面仅需一条 CPU 位运算完成校验

---

## 0. 方案摘要

### 0.1 一句话

**将 Capability Folding（Native Word 方案）融入 A-IPC 作为基石，使 A-IPC 成为一个"数据面自治 + 能力内联验证 + 控制面仅用于低频管理操作"的统一通信体系。**

### 0.2 基于八轮审查的核心发现

经过 16~23 号共八轮递进式审查（传输层正确性 → 文档一致性 → 模块体系完整性 → 设计逻辑缺陷 → Capability Folding 存在性 → 生产就绪度 → 融合因果推论 → Native Word 方案评估），A-IPC 的根本问题可以归纳为一个：

> **当前 A-IPC 的控制面（seL4 风格同步阻塞 syscall）与数据面（io_uring 异步 CQE）是两个独立的 IPC 子系统，而非一个统一的通信体系。能力校验在两个平面上使用不同代码路径，数据通信不得不经过同步阻塞的控制面，导致死锁风险、能力不一致和 daemon 崩溃的级联影响。**

Native Word Capability Folding 解决了这个根本问题——它将能力证明从控制面专属变为嵌入数据面的 64-bit 自验证令牌，使数据面可以在不依赖控制面运行时查询的情况下独立完成能力校验，从而将"两个独立的 IPC 子系统"融合为"一个统一的、能力感知的 IPC 体系"。

### 0.3 方案的三大支柱

```
支柱一：Native Word Badge + Epoch
        └── 64-bit = Epoch(32b) + Permissions(32b)
        └── 连接建立期编译，数据面一条位运算校验
        └── Epoch 递增 = 立即全局撤销旧 Badge

支柱二：统一的数据面通信
        └── 所有 daemon 间的数据消息走 io_uring + Badge
        └── 控制面退化为低频管理操作（mint/derive/revoke）
        └── 消除控制面同步阻塞引发的死锁风险

支柱三：简化的能力模型
        └── 消除 per-CPU capability cache + radix tree + IPI coherency
        └── 替代为 Epoch 代际计数器（每个能力类型一个 32-bit atomic）
        └── 复杂度净降低：新增 ~100 行 C，消除 ~300 行 C
```

### 0.4 方案覆盖的已知问题

本方案解决以下 16~19 号审查中发现的问题：

| 问题 | 来源 | 如何解决 |
|------|------|---------|
| P0: IORING_OP_IPC_* 不可行 | 16 号审查 | 已在 18 号审查中确认为传输层修正，本方案继续使用 IORING_OP_URING_CMD + cmd_op |
| P0: 控制面/数据面双轨能力校验 | 21 号审查维度四 | Badge 统一为唯一能力证明，双轨消失 |
| P0: 控制面同步阻塞死锁风险 | 21 号审查维度三 | 数据通信完全走数据面，控制面退化为低频管理 |
| D1: 三通道无消息排序保证 | 19 号审查 | 在 128B 头 reserved 中增加 `seq_num` 字段（本方案一并处理） |
| D3: per-CPU kfifo 抢占 | 19 号审查 | Fastpath 入口增加 preempt_disable/eneable |
| D4: Reconciliation ring 销毁竞态 | 19 号审查 | Reconciliation 扫描时原子持有 ring 引用 |
| 缺失: fastpath 无 ring->frozen 检查 | 18 号审查 | 在 C-S0 增加 |

**不在本方案范围内的问题：**
- D2 (BATCH 部分失败): 需要独立修正 BATCH 提交模型
- D5 (MSG_RING io-wq 饱和): 需要独立的并发控制设计
- D6/D7 (CLOCK_REALTIME 问题): 需要独立的时间戳方案

---

## 1. Capability Folding 核心机制设计

### 1.1 Native Word = Badge + Epoch

```
64-bit Native Word 结构：

  63                  32  31                   0
  ┌─────────────────────┬──────────────────────┐
  │       Epoch         │    Permissions Mask   │
  │  (32-bit 代际编号)  │  (32-bit 权限位掩码)  │
  └─────────────────────┴──────────────────────┘

Epoch 语义：
  - 按能力类型独立计数（每种操作权限对应一个 Epoch）
  -sec_d 执行能力撤销时递增对应类型的 Epoch
  - 递增后，所有携带旧 Epoch 的 Badge 立即失效

Permissions Mask 语义：
  - 每位对应一种操作权限（如 bit 0 = IPC_SEND, bit 1 = IPC_RECV, bit 2 = FILE_READ, ...）
  - 连接建立期由 sec_d 根据 Agent 的实际能力编译
  - 数据面仅通过位运算验证：(badge & required) == required

运行时验证（C-S9 的真正实现）：
  1. epoch = badge >> 32
  2. if (epoch != current_epoch[cap_type]) → REJECT (AIRY_ECAP_EPOCH)
  3. if ((badge & required_permissions) != required_permissions) → REJECT (AIRY_ECAP_PERM)
  4. → PASS

  两条 CPU 指令：SHR (shift) + AND (bitwise)
  延迟：~5-10ns（远低于 160ns fastpath 预算）
```

### 1.2 Epoch 管理

```
能力类型定义（每种有独立的 Epoch）:

enum airy_cap_type {
    AIRY_CAP_IPC_SEND       = 0,    // IPC 发送权限
    AIRY_CAP_IPC_RECV       = 1,    // IPC 接收权限
    AIRY_CAP_FILE_READ      = 2,    // 文件读取权限
    AIRY_CAP_FILE_WRITE     = 3,    // 文件写入权限
    AIRY_CAP_MEM_QUERY      = 4,    // 记忆查询权限
    AIRY_CAP_MEM_UPDATE     = 5,    // 记忆更新权限
    AIRY_CAP_COGN_SUBMIT    = 6,    // 认知任务提交权限
    AIRY_CAP_SCHED_CTL      = 7,    // 调度控制权限
    AIRY_CAP_SEC_POLICY     = 8,    // 安全策略管理权限
    AIRY_CAP_AUDIT_READ     = 9,    // 审计日志读取权限
    AIRY_CAP_NR_TYPES       = 10,
};

/* 全局 Epoch 表（每个能力类型一个 32-bit atomic） */
static atomic_t airy_cap_epoch[AIRY_CAP_NR_TYPES];

/* Epoch 递增（sec_d 撤销能力时调用，两阶段） */
int airy_cap_epoch_increment(enum airy_cap_type type)
{
    // 阶段 1: 标记转换中
    set_bit(AIRY_EPOCH_TRANSITION, &airy_epoch_flags);
    smp_mb();  // 全局可见

    // 阶段 2: 等待在途消息排空
    //           最坏情况: ring max entries (32768) × fastpath (160ns) ≈ 5ms
    mdelay(5);

    // 阶段 3: 递增 Epoch
    atomic_inc(&airy_cap_epoch[type]);
    smp_mb();  // 全局可见

    // 阶段 4: 清除转换标志
    clear_bit(AIRY_EPOCH_TRANSITION, &airy_epoch_flags);
    smp_mb();  // 全局可见

    return 0;
}

/* Epoch 读取（fastpath 使用，无需锁） */
static inline u32 airy_cap_epoch_read(enum airy_cap_type type)
{
    return atomic_read(&airy_cap_epoch[type]);
}
```

### 1.3 Badge 编译（连接建立期）

```
Badge 编译流程（在 Agent 首次连接或能力更新时执行）:

1. Agent 向 sec_d 请求能力: AIRY_SYS_CAP_REQUEST(cap_types)
2. sec_d 根据安全策略裁决: ALLOW/DENY/AUDIT
3. sec_d 编译 Badge:
   badge = 0;
   for each cap_type in Agent's granted capabilities:
       if granted:
           badge |= (1 << cap_type);  // 设置权限位
4. sec_d 将 Epoch 嵌入 Badge:
   for each cap_type:
       badge |= (airy_cap_epoch_read(cap_type) << 32);
   // 注意: 如果多种能力类型的 Epoch 不同, 使用最大值
   // 实际实现: badge_epoch = max(epoch_i for each cap_type)
   // 如果 Epoch 不统一, 则需要按能力类型分离 Badge
5. 将编译好的 Badge 嵌入消息头的 capability_badge 字段
6. 后续所有消息自动携带此 Badge
```

### 1.4 按能力类型分离 Epoch 的优化

```
简化方案（推荐用于 0.1.1）:
  - 所有能力类型共享一个全局 Epoch
  - 撤销任何一个 Agent 的任何能力 → 全局 Epoch + 1
  - 所有 Agent 需要重新请求能力 → sec_d 重新编译 Badge
  - 代价: 撤销一个 Agent 的能力会影响所有 Agent
  - 适用: Agent 数量较少 (< 100) 的 0.1.1 部署场景

完全方案（1.0.1）:
  - 每个能力类型独立 Epoch
  - 撤销 IPC_SEND 能力仅使 IPC_SEND 的 Badge 失效
  - 其他能力类型的 Badge 继续有效
  - 代价: 10 个独立 Epoch + Badge 中需要包含每种类型的 Epoch
```

---

## 2. 128B 消息头重设计：Layout C v2

### 2.1 Layout C v2 定义

```
offset   0: magic           (4B)  0x41524531 'ARE1'
offset   4: opcode          (2B)  SEND / RECV / SEND_BATCH / CANCEL / FREEZE
offset   6: flags           (2B)  ZEROCOPY / CAP_CARRY / COMPRESS / ENCRYPT
offset   8: trace_id        (8B)  OpenTelemetry 全链路追踪
offset  16: timestamp_ns    (8B)  CLOCK_REALTIME
offset  24: src_task        (8B)  源 Agent/daemon ID
offset  32: dst_task        (8B)  目标 Agent/daemon ID
offset  40: payload_len     (4B)  payload 字节数
offset  44: ─── reserved 区域重新分配 ───
offset  44: capability_badge(8B)  Native Word (Epoch << 32 | Permissions Mask)
offset  52: seq_num         (4B)  发送方单调递增序列号（解决消息排序问题）
offset  56: negotiated_ver  (2B)  握手协商的协议版本
offset  58: crc32           (4B)  CRC32 完整性校验
offset  62: __future[66]   (66B) 保留，填零
─────────────────────────────────────────────────
总计:   128 字节
```

### 2.2 与 Layout C v1 的对比

| 偏移 | Layout C v1 | Layout C v2 | 变化 |
|------|------------|-------------|------|
| 0-43 | magic/opcode/flags/trace_id/timestamp_ns/src_task/dst_task/payload_len | 同 v1 | **不变** |
| 44-51 | reserved[0:7] | **capability_badge** (8B) | **新增** |
| 52-55 | reserved[8:11] | **seq_num** (4B) | **新增** |
| 56-57 | reserved[12:13] | **negotiated_ver** (2B) | **新增** |
| 58-61 | reserved[14:17] | **crc32** (4B) | **新增** |
| 62-127 | reserved[18:83] | __future[66] (66B) | 缩减保留空间 |

### 2.3 新增字段的语义

| 字段 | 来源 | 解决的问题 |
|------|------|----------|
| `capability_badge` | 本方案支柱一 | **21 号审查维度四（一致性）+ 维度三（隔离）** |
| `seq_num` | 19 号审查 D1 | **三通道消息排序无保证** |
| `negotiated_ver` | 18 号审查 §2.4 | **128B 头部无版本字段，握手后版本不可感知** |
| `crc32` | 本方案完整性增强 | **消息头 + payload 完整性校验（防数据损坏）** |

### 2.4 与 agentrt [SC] 共享契约层的兼容性

agentrt（用户态跨三平台）与 agent-linux（Linux 内核）共享 `include/airymax/ipc.h`。

| 字段 | agentrt 行为 | agent-linux 行为 |
|------|------------|-------------------|
| `capability_badge` | 通过 Cupolas engine 编译 Badge，嵌入消息头 | 通过 sec_d 编译 Badge，嵌入消息头 |
| `seq_num` | 发送方递增 | 发送方递增 |
| `negotiated_ver` | 握手阶段填充 | 握手阶段填充 |
| `crc32` | 发送方计算，接收方校验 | 发送方计算，接收方校验 |

**agentrt 在 agent-linux 上运行时**：Badge 由 agent-linux 的 sec_d 编译，通过 [SC] syscall 返回给 agentrt，agentrt 嵌入消息头。agentrt 在 macOS/Windows 上独立运行时：Badge 由 Cupolas engine 自行编译。

---

## 3. Fastpath 状态机升级

### 3.1 升级的发送方条件（C-S0 到 C-S11）

```
发送方条件（进入 FAST_SEND）:

C-S0:  ring->frozen == false                     // [新增] A-ULS 冻结检查
C-S1:  magic == 0x41524531                       // [不变]
C-S2:  opcode == AIRY_IPC_OP_SEND                // [不变]
C-S3:  payload_len == 0                          // [不变] 仅消息头
C-S4:  消息总大小 ≤ 128B                          // [不变]
C-S5:  smp_processor_id() == dst_cpu             // [不变]
C-S6:  kfifo_is_full() == false                  // [不变]
C-S7:  current->reclaim_flag 未置                // [不变]
C-S8:  in_task() && !in_interrupt()             // [不变]
C-S9:  [重设计] capability_badge 校验:
       epoch = badge >> 32;
       if epoch != airy_cap_epoch_read(cap_type) → REJECT (AIRY_ECAP_EPOCH)
       if (badge & required) != required → REJECT (AIRY_ECAP_PERM)
C-S10: flags 不含 ENCRYPT / COMPRESS               // [不变]
C-S11: preempt_disable() 保护区间                   // [新增] 防止抢占迁移
```

**实现简化**：C-S9 从复杂的 `airy_cap_check_fast()` 黑盒变为两条 CPU 指令。

### 3.2 升级的状态转换表（新增 FREEZE 转换）

```
新增行:
| IDLE | AIRY_IPC_OP_FREEZE | FREEZE |
  ring->frozen = true ; eventfd_signal to Macro-Supervisor ; → IDLE

| FAST_SEND | ring→frozen 被置 | ERROR |
  丢弃当前消息 ; 返回 AIRY_ECAP_FROZEN

| FAST_RECV | ring→frozen 被置 | ERROR |
  丢弃当前消息 ; 返回 AIRY_ECAP_FROZEN
```

### 3.3 Preempt 保护

```c
/* Fastpath 入口: 禁用抢占, 保护 per-CPU kfifo 的 SPSC 假设 */
preempt_disable();
/* ... fastpath 执行 (≤1μs) ... */
preempt_enable();
```

---

## 4. 控制面的重新定位

### 4.1 控制面职责缩小为"能力管理操作"

| 控制面 syscall | 融合前使用频率 | 融合后使用频率 | 融合后用途 |
|:--------------|:-------------|:-------------|-----------|
| `airy_sys_call` | 高（各种能力 invocation） | 低（仅能力管理） | mint/derive/revoke |
| `airy_sys_send` | 高（数据通信） | 极低（仅控制消息） | macro_superv 下达冻结/终止指令 |
| `airy_sys_recv` | 高（数据通信） | 极低（仅控制消息） | 接收能力操作响应 |
| `airy_sys_reply` | 中（会话回复） | 极低 | 响应能力操作 |
| `airy_sys_nbsend/recv` | 中 | 几乎不使用 | 保留兼容 |

### 4.2 控制面死锁风险分析（融合后）

```
融合后的控制面通信图（仅能力管理操作）:

macro_superv ───AIRY_SYS_CALL(mint/revoke)──→ sec_d
                                            │
                                            │ sec_d 不调用任何其他 daemon
                                            │
                                            ▼ 返回结果
                                          macro_superv

结论：能力管理操作为"macro_superv → sec_d → 返回"的单向流，
不具备形成死锁环的条件。死锁风险从"密集网格"降为"无环图"。
```

---

## 5. 12 Daemon 通信拓扑重构

### 5.1 融合后每个 Daemon 的通信路径

| Daemon | 数据消息（高频, io_uring + Badge） | 能力操作（低频, 控制面 syscall） |
|--------|----------------------------------|-------------------------------|
| `macro_superv` | 向所有 daemon 发送心跳检测 | 向 sec_d 请求能力撤销 |
| `logger_daemon` | 从 A-ULP Ring Buffer 读取（mmap） | — |
| `config_daemon` | 接收/广播配置变更 | — |
| `gateway_d` | 路由 Agent 请求 → cogn_d/sched_d/mem_d | — |
| `sched_d` | 向 kernel 发送调度策略 | — |
| `vfs_d` | 处理文件 I/O 请求 | — |
| `net_d` | 处理网络包 | — |
| `mem_d` | 处理记忆查询/更新 | — |
| `cogn_d` | 接收认知任务, 返回结果 | — |
| `sec_d` | — | 接收并裁决能力请求（仅此 daemon 使用控制面作为主要路径） |
| `audit_d` | 接收审计事件 | — |
| `dev_d` | 处理设备 I/O | — |

**关键**：12 daemon 中仅 `sec_d` 和 `macro_superv` 使用控制面（低频能力管理和生命周期指令）。其余 10 个 daemon 全部通过数据面 io_uring + Badge 进行通信。控制面从"高频数据通道"变为"低频管理通道"。

### 5.2 Daemon 崩溃的恢复流程

```
Cogn_d 崩溃（数据面不可用）:
  1. gateway_d 尝试 MSG_RING → cogn_d ring
  2. 返回 -EINVAL（ring 不存在）
  3. gateway_d 记录错误, 将请求暂存 offline queue
  4. systemd 自动重启 cogn_d
  5. cogn_d 重新创建 io_uring ring
  6. cogn_d 向 sec_d 重新请求能力 → sec_d 编译新 Badge
  7. cogn_d 向 gateway_d 发送 READY 通知（数据面 io_uring + 新 Badge）
  8. gateway_d 从 offline queue 取出暂存请求, 重新发送
  总恢复时间: ~2s (systemd 重启) + ~100ms (能力重建) ≈ 2.1s

对比融合前:
  控制面 airy_sys_send 阻塞 5s → 超时 → 恢复
  总恢复时间: 5s
```

---

## 6. 与 Unify Design 5 模块的整合

### 6.1 A-IPC × A-UEF（错误码整合）

```
新增 IPC 能力校验错误码（在 A-UEF 的 IPC 码空间 -41~-70 中注册）:

AIRY_ECAP_EPOCH    = -41   // Epoch 不匹配，Badge 已失效
AIRY_ECAP_PERM     = -42   // 权限不足（Badge 中缺少所需权限位）
AIRY_ECAP_BADGE    = -43   // Badge 格式无效（全零或非法值）
AIRY_ECAP_FROZEN   = -44   // Ring 已被 A-ULS 冻结
```

### 6.2 A-IPC × A-ULS（冻结整合）

```
A-ULS Micro-Supervisor 检测异常 → 
  发送 AIRY_IPC_OP_FREEZE (通过 io_uring_cmd cmd_op) →
    IPC 设置 ring->frozen = true →
      Fastpath C-S0 拒绝所有后续消息 (REJECT with AIRY_ECAP_FROZEN) →
        eventfd 通知 Macro-Supervisor 进行裁决
```

### 6.3 A-IPC × A-UCS（配置整合）

```
新增 A-UCS sysctl 配置项:

kernel.airy_ipc.epoch_transition_ms  = 5    // Epoch 递增时的排空等待 (ms)
kernel.airy_ipc.badge_ttl_ms         = 5000 // Badge 最大有效期 (ms)
kernel.airy_ipc.ring_entries         = 256  // Ring 默认大小
kernel.airy_ipc.batch_threshold      = 8    // BATCH 聚合阈值
```

### 6.4 A-IPC × A-ULP（不变）

A-ULP 的日志 Ring Buffer 和 eventfd 通知继续使用现有机制，不受 Native Word 方案影响。

---

## 7. 与 agentrt 的同源映射

### 7.1 [SC] 共享契约层 — ipc.h

```
新增共享定义:

#define AIRY_IPC_CAP_BADGE_OFFSET   44   // Badge 在消息头的偏移
#define AIRY_IPC_SEQ_NUM_OFFSET     52   // 序列号偏移
#define AIRY_IPC_NEG_VER_OFFSET     56   // 协商版本偏移
#define AIRY_IPC_CRC32_OFFSET       58   // CRC32 偏移

/* Native Word 结构 */
typedef __u64 airy_cap_badge_t;

/* 权限位定义 */
#define AIRY_CAP_PERM_IPC_SEND      (1 << 0)
#define AIRY_CAP_PERM_IPC_RECV      (1 << 1)
#define AIRY_CAP_PERM_FILE_READ     (1 << 2)
// ... 共 10-20 位

static inline u32 airy_cap_badge_epoch(airy_cap_badge_t badge) {
    return (u32)(badge >> 32);
}
static inline u32 airy_cap_badge_perms(airy_cap_badge_t badge) {
    return (u32)(badge & 0xFFFFFFFF);
}
```

### 7.2 [SS] 语义同源层 — agentrt ↔ agent-linux 对齐

| 语义 | agentrt (用户态) | agent-linux (内核态) |
|------|----------------|----------------------|
| Badge 编译 | Cupolas engine → `airy_cap_badge_compile()` | sec_d → `airy_cap_badge_compile()` |
| Badge 校验 | `(badge >> 32) == current_epoch && (badge & required)` | 同 agentrt |
| Epoch 管理 | Cupolas 内部维护 | 内核 atomic_t 数组 |
| Seq_num | 发送方递增 | 同 agentrt |
| CRC32 | 发送方计算, 接收方校验 | 同 agentrt |

---

## 8. 实施路线

### 8.1 Phase 0 — 奠基（1-2 天）

```
□ 修正 Layout C v2 的定义（02-ipc-protocol.md §2）
□ 修正 IORING_OP_IPC_* → IORING_OP_URING_CMD + cmd_op（02-ipc-protocol.md §4）
□ 修正 SQPOLL/DEFER_TASKRUN 互斥声明（03-ipc-flow.md §2.5）
□ 统一 5 种 payload 协议类型定义（对齐 Layout C SSoT）
□ 增加 ring->frozen 检查到 fastpath C-S0（07-ipc-fastpath.md §3.1）
□ 增加 AIRY_IPC_OP_FREEZE 到 opcode 表（07-ipc-fastpath.md §1.3）
```

### 8.2 Phase 1 — Native Word 植入（3-5 天）

```
□ 实现 Epoch 管理模块（kernel/ipc/airy_epoch.c）
  - atomic_t airy_cap_epoch[AIRY_CAP_NR_TYPES]
  - airy_cap_epoch_increment() 两阶段递增
  - airy_cap_epoch_read() 无锁读取

□ 实现 Badge 编译模块（kernel/ipc/airy_badge.c）
  - airy_cap_badge_compile(agent_id, cap_types) → badge

□ 修改 fastpath C-S9 实现:
  - 当前: airy_cap_check_fast() 黑盒
  - 修改为: epoch check + bitwise AND（两条指令）

□ 增加 fastpath preempt_disable/enable 保护

□ 在 A-UEF 错误码空间注册新的 IPC 错误码（-41~-44）
```

### 8.3 Phase 2 — 控制面降频（3-5 天）

```
□ 重构 daemon 通信: 所有数据消息走 io_uring 数据面 + Badge
□ 重构 sec_d: 实现 Badge 编译接口（AIRY_SYS_CAP_REQUEST → compile → return badge）
□ 重构 macro_superv: 生命周期指令仍走控制面（频率极低）
□ 减少控制面 syscall 超时: 从 5s 降至 100ms
□ 补充 daemon 重启恢复流程文档
```

### 8.4 Phase 3 — 验证（2-3 天）

```
□ 更新 IPC 性能基准测试（含 Badge 校验的 fastpath 延迟）
□ 注入 Epoch 递增 + 并发通信的混沌测试
□ daemon 崩溃恢复测试
□ 与 Layout C v1 的兼容性测试（agentrt 用户态）
```

### 8.5 总工期：9-15 天

---

## 9. 风险与缓解

| # | 风险 | 缓解 |
|---|------|------|
| R1 | Epoch 递增导致在途消息丢失 | 两阶段递增（标记→排空 5ms→递增） |
| R2 | 全局 Epoch 导致撤销一个 Agent 影响所有 Agent | 0.1.1 用全局 Epoch（Agent 少）；1.0.1 升级为按类型独立 Epoch |
| R3 | Layout C v2 与 agentrt 的 [SC] 共享契约层兼容性 | Badge 字段在 agentrt 跨平台模式下由 Cupolas 编译；在 Linux 下由 sec_d 编译 |
| R4 | 新增字段使 128B 空间紧张 | 66B 保留空间仍充足（未来 10 年扩展预算） |

---

## 10. 与 Layout C v1 的兼容迁移

### 10.1 向后兼容策略

```
v1 Agent（旧 Layout C，无 Badge）→ v2 内核:
  1. capability_badge = 0（全零 = "未携带 Badge"）
  2. fastpath C-S9: badge == 0 → 降级到 slowpath（传统 capability check）
  3. 降级后: 内核 radix tree lookup → pass/fail
  4. 回复中附带新 Badge → Agent 下次使用

v2 Agent（新 Layout C，有 Badge）→ v1 内核:
  1. 内核忽略 capability_badge 字段
  2. 走传统 capability check
  3. 无性能退化（Badge 未被使用）
```

### 10.2 迁移时间线

```
0.1.1: Layout C v2 定义完成，内核同时支持 v1 和 v2 Badge
0.1.1: agentrt SDK 支持 Badge 嵌入（Cupolas 编译）
1.0.1: 默认使用 v2 Badge，v1 降级路径保留但不推荐
2.0.0: 移除 v1 降级路径
```

---

## 11. 最终判定

### 11.1 可行性：可以全面融入作为 A-IPC 基石

Native Word Capability Folding 与 Layout C、fastpath 状态机、io_uring 传输层、数据面自治三原则、Unify Design 5 模块框架全部兼容。修改范围局部（Layout C 8B + C-S9 2 条指令 + ~100 行新增 C），影响全局（消除控制面双轨 + 隔离死锁风险 + 简化能力模型）。

### 11.2 是否需要系统重新设计：需要，但不是推翻重建

"重新设计"在这里的含义是：以 Native Word 为统一的跨平面能力证明，重新设计 A-IPC 的**能力校验路径**和**控制面职责边界**。128B 消息头（Layout C v2）、fastpath 状态机（C-S9 实现）、io_uring 传输层、数据面自治三原则——这些核心架构**不变**。

### 11.3 是否与现有方案冲突：无冲突

Native Word 方案与 Unify Design §8、工程基线（sched_tac + IORING_OP_URING_CMD）、IRON-9 v3（[SC] ipc.h 共享）、A-UEF/A-ULP/A-ULS/A-UCS 模块均兼容。唯一的"冲突"是消除了当前方案中的双轨制能力校验——这是改善，不是破坏。

### 11.4 一句话

**Capability Folding（Native Word 方案）是 A-IPC 从"正确的双轨设计"跃迁为"统一的、能力感知的、数据面自治的基石"的缺失一环——它不是推翻 A-IPC，而是完成 A-IPC。**

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
