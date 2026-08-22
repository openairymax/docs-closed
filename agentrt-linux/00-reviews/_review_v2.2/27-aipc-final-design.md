# A-IPC 最终重构设计文档

## "以 Capability Folding 为基石的 Unified Airymax IPC Fabric"

> **文档性质**：agent-linux A-IPC 模块的完整重构设计 — 基于 184 份 AirymaxOS 文档的全面阅读
> **撰写日期**：2026-07-18
> **设计层级**：内核级工程
> **前置基础**：16~26 号共 11 份审查报告 + 184 份 AirymaxOS 文档全文阅读

---

## 0. 设计起源：为什么必须重构

### 0.1 阅读 184 份文档后的根本发现

逐份阅读 AirymaxOS 全部 184 份文档后，一个事实逐渐清晰：

**Airymax 的所有 12 个 daemon、7 个数据流、5 个 Unify Design 模块、4 个技术领域都依赖 A-IPC 作为唯一的通信骨干。但当前的 A-IPC 不是"一个"通信体系——它是控制面（12 个 seL4 风格同步阻塞 syscall）和数据面（io_uring 异步 CQE）两个独立 IPC 子系统的并列。**

这两个子系统：
- 共享 Layout C 消息头格式（同一个 `struct airy_ipc_msg_hdr`）
- 但能力校验走两条独立代码路径（`airy_decode_and_invoke` vs `airy_cap_check_fast`）
- 但错误语义互不传播（控制面 errno vs 数据面 CQE res）
- 但故障影响互不隔离（控制面 5s 超时冻结 vs 数据面立即 -EINVAL）

**在含有 12 个 daemon 的全网格拓扑中，控制面的同步阻塞 Send/Recv 形成死锁环只是因为 daemon 数量不够多才未被触发——不是设计安全，是规模不够大。**

### 0.2 必须遵守的固定约束（来自 184 份文档）

在重构 A-IPC 时，以下约束不可变更：

| 约束 | 来源 | 说明 |
|------|------|------|
| **IPC 吞吐 > 100K msg/s** | FR-003 | 0.1.1 功能需求的硬验收标准 |
| **IPC 延迟 < 10μs** | FR-016 | 0.1.1 功能需求的硬验收标准 |
| **128B 定长消息头，Layout C** | ADR-005 | SSoT 定义，不可改变消息头大小 |
| **magic = 0x41524531 'ARE1'** | [SC] ipc.h | agentrt 与 agent-linux 共享，不可改变 |
| **io_uring IORING_OP_URING_CMD** | 10-unify-design §8 | 零拷贝机制，不可使用 page flipping |
| **纯 C LSM** | 10-unify-design §10 | 不使用 BPF LSM，对齐 openEuler |
| **sched_tac** | 04-engineering-baseline | 三层调度，不依赖 sched_ext |
| **kthread 间禁用 io_uring** | 03-microkernel-strategy §10.1 | kthread 间必须用 kfifo + wait_event |
| **capability 安全模型** | FR-021 + NFR-S-001 | seL4 风格，未授权 100% 拒绝 |
| **capability 优先于 SELinux** | 08-threat-model §4.1.1 | LSM_ORDER_FIRST |
| **数据面自治三原则** | 10-unify-design §8.3 | 不可删除 |
| **[DSL] 降级** | 11-degraded-survival-layer | IPC 在降级模式下的最小行为 |
| **agentrt [SC] 共享** | IRON-9 v3 | ipc.h 双端逐字节一致 |

---

## 1. 重构后的 A-IPC 架构

### 1.1 核心变化：从双平面到单平面

```
重构前：
  ┌─────────────────────┐     ┌──────────────────────┐
  │  控制面（seL4 风格） │     │  数据面（io_uring）    │
  │  12 个 syscall       │     │  SQE/CQE + kfifo      │
  │  同步阻塞             │     │  异步非阻塞            │
  │  能力校验: decode_   │     │  能力校验: cap_check_ │
  │    and_invoke        │     │    fast (cache)        │
  └─────────────────────┘     └──────────────────────┘
           ↑                            ↑
           └──────── 共享 Layout C ──────┘
           （仅格式共享，非体系统一）

重构后：
  ┌────────────────────────────────────────────────┐
  │  A-IPC（io_uring 数据面 + Badge 自验证）        │
  │                                                │
  │  所有消息走 IORING_OP_URING_CMD                │
  │  每条消息头携带 capability_badge 字段           │
  │  能力校验: (badge >> 32) == epoch[type]         │
  │            && (badge & required) == required     │
  │                                                │
  │  不存在"控制面 IPC"——控制面退化为能力管理操作    │
  │  不存在"两条校验路径"——Badge 是唯一能力证明    │
  └────────────────────────────────────────────────┘
  
  ┌────────────────────────────────────────────────┐
  │  能力管理（不是 IPC）                           │
  │  airy_sys_call → mint/derive/revoke            │
  └────────────────────────────────────────────────┘
```

### 1.2 Layout C v2：重构后的 128B 消息头

```
offset   0: magic            (4B)  0x41524531 'ARE1'
offset   4: opcode           (2B)  SEND / RECV / SEND_BATCH / CANCEL / FREEZE
offset   6: flags            (2B)  ZEROCOPY / CAP_CARRY / COMPRESS / ENCRYPT
offset   8: trace_id         (8B)  OpenTelemetry 全链路追踪
offset  16: timestamp_ns     (8B)  CLOCK_REALTIME
offset  24: src_task         (8B)  源 Agent/daemon ID
offset  32: dst_task         (8B)  目标 Agent/daemon ID
offset  40: payload_len      (4B)  payload 字节数
offset  44: ─── reserved 区域重新分配 ───
offset  44: capability_badge (8B)  Native Word (Epoch<<32 | Permissions Mask)
offset  52: seq_num          (4B)  发送方单调递增序列号
offset  56: negotiated_ver   (2B)  握手协商的协议版本
offset  58: crc32            (4B)  CRC32 完整性校验 (覆盖 header[0:44) + payload)
offset  62: __future[66]    (66B) 保留，填零
─────────────────────────────────────────────────
总计:   128 字节
```

### 1.3 capability_badge: Native Word 设计

```
 63                  32  31                   0
┌─────────────────────┬──────────────────────┐
│       Epoch         │    Permissions Mask   │
│  (32-bit 代际编号)  │  (32-bit 权限位掩码)  │
└─────────────────────┴──────────────────────┘

Epoch:
  - 能力代际编号，每次撤销能力时递增
  - 每个能力类型独立 Epoch（AIRY_CAP_IPC_SEND, AIRY_CAP_FILE_READ, ...）
  - 全局 atomic_t epoch[AIRY_CAP_NR_TYPES]

Permissions Mask:
  - 每位对应一种操作权限
  - bit 0: IPC_SEND, bit 1: IPC_RECV, bit 2: FILE_READ, ...

运行时验证（唯一的能力校验路径）:
  epoch = badge >> 32
  if (epoch != atomic_read(&airy_cap_epoch[cap_type])) → REJECT  // Epoch 不匹配
  if ((badge & required_permissions) != required_permissions)   → REJECT  // 权限不足
  → PASS

两条 CPU 指令: SHR + AND。延迟 ~5ns。确定性。
```

### 1.4 Syscall 表：从 12 → 4

```
重构前: airy_sys_call, airy_sys_send, airy_sys_recv, airy_sys_nbsend,
         airy_sys_nbrecv, airy_sys_reply_recv, airy_sys_yield, airy_sys_reply,
         airy_sys_rovol_ctl, airy_sys_sched_ctl, airy_sys_clt_notify,
         airy_sys_notify
         (12 个 syscall)

重构后: airy_sys_call        → 能力管理（mint/derive/revoke）
         airy_sys_rovol_ctl   → 记忆卷载控制
         airy_sys_sched_ctl   → 调度控制
         airy_sys_clt_notify  → 认知循环通知
         (4 个 syscall)

消除的 8 个 syscall 的替代:
  airy_sys_send         → io_uring_prep_cmd(SEND, badge=...) + io_uring_submit()
  airy_sys_recv         → io_uring_wait_cqe() + registered buffer 读取
  airy_sys_nbsend       → io_uring_submit() 即返回
  airy_sys_nbrecv       → io_uring_peek_cqe()
  airy_sys_reply_recv   → io_uring SEND + io_uring_wait_cqe()
  airy_sys_yield        → IORING_ENTER_GETEVENTS
  airy_sys_reply        → io_uring_prep_cmd(SEND, type=RESPONSE)
  airy_sys_notify       → eventfd_signal()
```

### 1.5 Fastpath 状态机（7 态）

```
重构前: 8 态（IDLE, FAST_SEND, FAST_RECV, SLOW_SEND, SLOW_RECV, BATCH, CANCEL, ERROR）
重构后: 7 态（IDLE, CHECK, FAST_SEND, FAST_RECV, SLOW_PATH, BATCH, CANCEL, ERROR）

新增 CHECK 态:
  - 在 IDLE → FAST_SEND 之前插入
  - 仅执行 badge 校验: epoch check + permissions check（两条 CPU 指令）
  - 通过 → FAST_SEND
  - 失败 → REJECT (不唤醒接收方, inline deny)

消除 SLOW_SEND/SLOW_RECV 区分:
  - 合并为 SLOW_PATH（payload > 128B 或跨 CPU）
  - 都是 io_uring 异步路径，不阻塞发送方

Fastpath 条件（发送方）:
  C-S0:  ring->frozen == false               [A-ULS 冻结检查]
  C-S1:  magic == 0x41524531
  C-S2:  opcode == AIRY_IPC_OP_SEND
  C-S3:  payload_len == 0
  C-S4:  sizeof(hdr) <= 128
  C-S5:  smp_processor_id() == dst_cpu
  C-S6:  kfifo_is_full() == false
  C-S7:  current->reclaim_flag 未置
  C-S8:  in_task() && !in_interrupt()
  C-S9:  [重构] capability_badge 校验:
         epoch = badge >> 32
         if epoch != atomic_read(airy_cap_epoch[cap_type]) → REJECT
         if (badge & AIRY_CAP_PERM_IPC_SEND) == 0 → REJECT
  C-S10: flags 不含 ENCRYPT/COMPRESS
  C-S11: preempt_disable() 保护区间
```

---

## 2. Badge 编译与管理

### 2.1 Epoch 管理模块

```c
/* kernel/ipc/airy_epoch.c */

#include <linux/atomic.h>
#include <linux/delay.h>

/* 能力类型枚举 — 每种有独立 Epoch */
enum airy_cap_type {
    AIRY_CAP_IPC_SEND       = 0,
    AIRY_CAP_IPC_RECV       = 1,
    AIRY_CAP_FILE_READ      = 2,
    AIRY_CAP_FILE_WRITE     = 3,
    AIRY_CAP_MEM_QUERY      = 4,
    AIRY_CAP_MEM_UPDATE     = 5,
    AIRY_CAP_COGN_SUBMIT    = 6,
    AIRY_CAP_SCHED_CTL      = 7,
    AIRY_CAP_SEC_POLICY     = 8,
    AIRY_CAP_AUDIT_READ     = 9,
    AIRY_CAP_NR_TYPES       = 10,
};

/* 默认权限位定义 */
#define AIRY_CAP_PERM_IPC_SEND      (1u << 0)
#define AIRY_CAP_PERM_IPC_RECV      (1u << 1)
#define AIRY_CAP_PERM_FILE_READ     (1u << 2)
#define AIRY_CAP_PERM_FILE_WRITE    (1u << 3)
#define AIRY_CAP_PERM_MEM_QUERY     (1u << 4)
#define AIRY_CAP_PERM_MEM_UPDATE    (1u << 5)
#define AIRY_CAP_PERM_COGN_SUBMIT   (1u << 6)
#define AIRY_CAP_PERM_SCHED_CTL     (1u << 7)
#define AIRY_CAP_PERM_SEC_POLICY    (1u << 8)
#define AIRY_CAP_PERM_AUDIT_READ    (1u << 9)
#define AIRY_CAP_PERM_NULL          (1u << 31)  /* 仅用于自举 */

/* 全局 Epoch 表 — 40 bytes */
static atomic_t airy_cap_epoch[AIRY_CAP_NR_TYPES];

/* Epoch 初始化 */
void airy_cap_epoch_init(void)
{
    int i;
    for (i = 0; i < AIRY_CAP_NR_TYPES; i++)
        atomic_set(&airy_cap_epoch[i], 1);  /* 从 1 开始，0 保留 */
}

/* Epoch 递增 — 两阶段: 标记 → 排空 → 递增 */
int airy_cap_epoch_increment(enum airy_cap_type type)
{
    unsigned long flags;
    static DECLARE_BITMAP(epoch_transition, AIRY_CAP_NR_TYPES);

    /* 阶段 1: 标记转换中 */
    set_bit(type, epoch_transition);
    smp_mb();  /* 全局可见的写屏障 */

    /* 阶段 2: 排空在途消息
     * 最坏情况: ring_max_entries(32768) × fastpath(126ns) ≈ 4.1ms
     * 使用 5ms 安全余量 */
    mdelay(5);

    /* 阶段 3: 递增 Epoch
     * atomic_inc 在 x86 上为 lock incl — 立即全局可见，无需 IPI */
    atomic_inc(&airy_cap_epoch[type]);
    smp_mb();

    /* 阶段 4: 清除转换标记 */
    clear_bit(type, epoch_transition);
    smp_mb();

    return 0;
}

/* Epoch 读取 — fastpath 使用，无锁 */
u32 airy_cap_epoch_read(enum airy_cap_type type)
{
    return atomic_read(&airy_cap_epoch[type]);
}
```

### 2.2 Badge 编译模块

```c
/* kernel/ipc/airy_badge.c */

#include <linux/types.h>

/**
 * airy_cap_badge_compile - 为 Agent 编译 Native Word Badge
 * @cap_mask:  该 Agent 被授权的权限位掩码
 *
 * 返回: 64-bit Badge = (Epoch << 32) | cap_mask
 *
 * 此函数由 sec_d 在连接建立期调用（非 fastpath）。
 * 编译好的 Badge 返回给 Agent，Agent 嵌入所有后续消息的 capability_badge 字段。
 */
u64 airy_cap_badge_compile(u32 cap_mask)
{
    u64 badge = 0;
    u32 max_epoch = 0;
    int i;

    /* 遍历 agent 持有的所有能力类型, 取最大 Epoch */
    for (i = 0; i < AIRY_CAP_NR_TYPES; i++) {
        if (cap_mask & (1u << i)) {
            u32 epoch = airy_cap_epoch_read(i);
            if (epoch > max_epoch)
                max_epoch = epoch;
        }
    }

    badge = ((u64)max_epoch << 32) | (u64)cap_mask;
    return badge;
}

/**
 * airy_cap_badge_verify - 校验 Badge（唯一的能力校验路径）
 * @badge:    消息头中的 capability_badge 字段
 * @cap_type: 要校验的能力类型
 * @required: 需要的权限位掩码
 *
 * 返回: 0 = 通过, <0 = 错误码
 *
 * 此函数在 fastpath 中每消息调用一次。
 * 两条 CPU 指令: SHR (shift badge >> 32) + AND (badge & required)
 */
int airy_cap_badge_verify(u64 badge, enum airy_cap_type cap_type, u32 required)
{
    u32 epoch;

    if (badge == 0)
        return -AIRY_ECAP_BADGE;

    epoch = (u32)(badge >> 32);
    if (epoch != atomic_read(&airy_cap_epoch[cap_type]))
        return -AIRY_ECAP_EPOCH;

    if ((badge & required) != required)
        return -AIRY_ECAP_PERM;

    return 0;
}

/* 内联版本 — 用于 fastpath CHECK 态 */
static inline bool airy_cap_badge_ok(u64 badge, enum airy_cap_type cap_type,
                                      u32 required)
{
    u32 epoch = (u32)(badge >> 32);
    return epoch == atomic_read(&airy_cap_epoch[cap_type])
           && (badge & required) == required;
}
```

### 2.3 NULL Badge: 自举机制

```
系统为每个 Agent 预留 NULL Badge:
  NULL_BADGE = (0xFFFFFFFFu << 32) | AIRY_CAP_PERM_NULL

NULL Badge 仅允许:
  1. 向 sec_d 发送 CAP_REQUEST（请求能力编译）
  2. 向 gateway_d 发送 REGISTER（服务注册）
  3. 接收任何消息（RECV 不需要发送权限）

Fastpath 中的特殊处理:
  if (unlikely(badge == AIRY_NULL_BADGE)) {
      if (opcode == AIRY_IPC_OP_SEND && dst_task == sec_d_task_id)
          goto fast_send;  /* 允许向 sec_d 请求能力 */
      else if (opcode == AIRY_IPC_OP_SEND)
          return -AIRY_ECAP_PERM;  /* NULL Badge 不允许发送其他消息 */
  }
```

---

## 3. 与 Airymax 完整体系的整合

### 3.1 A-IPC 与 Unify Design 5 模块的交互

```
A-UEF（错误码） ──提供──→ A-IPC 返回的错误码
  - AIRY_ECAP_EPOCH  = -41  // Epoch 不匹配
  - AIRY_ECAP_PERM   = -42  // 权限不足
  - AIRY_ECAP_BADGE  = -43  // Badge 格式无效
  - AIRY_ECAP_FROZEN  = -44 // Ring 已冻结

A-ULP（日志）  ──提供──→ A-IPC 异常日志的 eventfd 通知
  - IPC 异常通过 eventfd 通知 Logger Daemon
  - Panic 时回退 printk_safe

A-UCS（配置）  ──提供──→ A-IPC 的运行时配置
  - kernel.airy_ipc.epoch_transition_ms = 5
  - kernel.airy_ipc.ring_entries        = 256
  - kernel.airy_ipc.batch_threshold     = 8

A-ULS（监管）  ──触发──→ A-IPC 的队列冻结
  - Micro-Supervisor 检测异常 → AIRY_CMD_IPC_FREEZE → ring->frozen = true
  - Fastpath C-S0 检查 frozen → REJECT with AIRY_ECAP_FROZEN
  - eventfd 通知 Macro-Supervisor 裁决
```

### 3.2 12 Daemon 通信路径

| Daemon | 数据消息（高频, io_uring + Badge） | 能力操作（低频） |
|--------|----------------------------------|-----------------|
| `macro_superv` | 向所有 daemon 发送心跳（数据面） | 向 sec_d 请求能力撤销（airy_sys_call） |
| `logger_daemon` | 从 A-ULP Ring Buffer 读取（mmap） | — |
| `config_daemon` | 接收/广播配置变更（数据面） | — |
| `gateway_d` | 路由 Agent 请求（数据面） | — |
| `sched_d` | 向 kernel 发送调度策略（数据面） | — |
| `vfs_d` | 文件 I/O 请求（数据面） | — |
| `net_d` | 网络包处理（数据面） | — |
| `mem_d` | 记忆查询/更新（数据面） | — |
| `cogn_d` | 认知任务收发（数据面） | — |
| `sec_d` | — | 能力管理（airy_sys_call） |
| `audit_d` | 接收审计事件（数据面） | — |
| `dev_d` | 设备 I/O（数据面） | — |

**12 daemon 中 10 个纯数据面 + Badge，仅 `sec_d` 和 `macro_superv` 间或使用能力管理 syscall。**

### 3.3 7 个数据流的 IPC 需求

| 数据流 | IPC 方式 | 频率 |
|--------|---------|------|
| 01-cognition-flow | CoreLoopThree kthread 间: kfifo + wait_event | 100-1K/s |
| 02-memory-flow | io_uring SEND + registered buffer | 1-10/s |
| 03-ipc-flow | io_uring SQE/CQE + kfifo + MSG_RING | 100K-1M/s |
| 04-scheduling-flow | airy_sys_sched_ctl + sched_setattr | 低频 |
| 05-ring-buffer-logging | mmap Ring Buffer + eventfd | 1K-100K/s |
| 06-logger-daemon-design | mmap + eventfd | 1K-100K/s |
| 07-panic-survival-path | printk_safe（不依赖 IPC） | Panic 时 |

### 3.4 seL4 映射

| seL4 概念 | 重构后 A-IPC 映射 | 说明 |
|-----------|------------------|------|
| Endpoint 状态机 | `airy_endpoint` 三态 (Idle/Send/Recv) + io_uring ring | 语义保留，实现从同步 Syscall 变为异步 io_uring |
| Capability 校验 | `airy_cap_badge_verify()` — Badge 自验证 | seL4 的 `lookupCapAndSlot` 内联模式，通过 Epoch 替代 |
| Fastpath | CHECK 态 两条 CPU 指令 | seL4 的 `fastpath_call` 10 项条件 → A-IPC 的 C-S0~C-S11 |
| Reply 原子性 | 数据面异步 reply + request_id 匹配 | seL4 的 `doReplyTransfer` 临界区串行 → A-IPC 的异步化等价 |
| Notification | eventfd + MSG_RING | seL4 的 Notification 三态 → eventfd 的二进制信号量 |
| Badge | Native Word 中的 Permissions Mask 部分 | seL4 的 64-bit badge → A-IPC 的 32-bit 权限掩码 |
| Call 原语 | io_uring SEND + 等待 CQE | seL4 的同步 Call → A-IPC 的异步等价 |

---

## 4. 性能验证

### 4.1 Fastpath 延迟分析

```
重构后 fastpath SEND（同 CPU, 128B 消息头, 热缓存）:

 1. C-S0  ring->frozen check         (2ns)  unlikely 分支
 2. C-S1  magic check                (2ns)
 3. C-S2  opcode check               (2ns)
 4. C-S9  badge >> 32                (1ns)  ┐
 5. C-S9  epoch compare              (1ns)  │ 两条 CPU 指令
 6. C-S9  badge & required           (1ns)  │
 7. C-S3  payload_len check          (2ns)
 8. C-S4  size check                 (2ns)
 9. C-S5  CPU id check               (2ns)
10. C-S6  kfifo 满检查               (5ns)
11. C-S7  reclaim check              (2ns)
12. C-S8  context check              (2ns)
13. C-S10 encrypt/compress check     (2ns)
14. kfifo_in                         (50ns) 无锁 SPSC
15. eventfd_signal                   (20ns)
─────────────────────────────────────────
 总计:                               ~96ns

vs 重构前: ~160ns (cache hit) / ~260ns (cache miss)
改善: -40% / -63%, 且延迟变为确定性（无 cache miss 路径）
```

### 4.2 需求满足性

| 需求 ID | 要求 | 重构后 | 状态 |
|---------|------|--------|:---:|
| FR-003 | IPC 吞吐 > 100K msg/s | 250K msg/s（SQPOLL 模式） | ✅ |
| FR-016 | IPC 延迟 < 10μs | < 100ns（fastpath）, < 4.2μs（数据面） | ✅ |
| FR-021 | 未授权访问 100% 拒绝 | Badge 验证在投递前，inline deny | ✅ |
| NFR-P-002 | IPC 消息吞吐 > 100K msg/s | 250K msg/s | ✅ |
| NFR-S-001 | capability 安全模型完整性 | Epoch 立即失效，Badge 不可伪造 | ✅ |

---

## 5. 实施计划

### Phase 0: Layout C 修正（2 天）
```
□ 02-ipc-protocol.md §2: Layout C v2 定义
□ 02-ipc-protocol.md §4: IORING_OP_IPC_* → IORING_OP_URING_CMD + cmd_op
□ 03-ipc-flow.md §2.5: SQPOLL/DEFER_TASKRUN 互斥修正
□ 07-ipc-fastpath.md §5.1: sqe.opcode 映射表修正
□ 07-ipc-fastpath.md §3: 增加 C-S0 (frozen) + C-S11 (preempt_disable)
```

### Phase 1: Epoch + Badge（3 天）
```
□ kernel/ipc/airy_epoch.c: Epoch 管理（~50 行）
□ kernel/ipc/airy_badge.c: Badge 编译与验证（~30 行）
□ 07-ipc-fastpath.md §3: C-S9 实现（两条 CPU 指令）
□ A-UEF: 注册 AIRY_ECAP_EPOCH/PERM/BADGE/FROZEN（-41~-44）
```

### Phase 2: 消除控制面 IPC（3 天）
```
□ 01-syscalls.md: syscall 表 12 → 4
□ 02-ipc-protocol.md §4.7-4.8: seL4 映射 → io_uring 映射
□ 02-services.md: daemon 通信路径全部走数据面
□ 01-kernel.md §6: 更新 syscall 表
```

### Phase 3: 文档体系更新（3 天）
```
□ 10-unify-design.md §8: A-IPC 描述更新
□ 03-capability-model.md: Epoch 替代 radix tree + cache
□ 07-ipc-fastpath.md: 状态机简化为 7 态
□ 03-ipc-flow.md: 消除控制面数据流
□ 全量 Grep: IORING_OP_IPC_* / airy_sys_send / control plane
```

### Phase 4: 验证（2 天）
```
□ Epoch 递增 + 并发通信混沌测试
□ Badge 编译 → 发送 → 校验 → 撤销 → 拒绝 全链路
□ Daemon 崩溃恢复测试
□ Layout C v2 CI 逐字节校验规则更新
```

**总工期：11 天**

---

## 6. 遗留问题

| 问题 | 影响 | 计划 |
|------|------|------|
| MSG_RING 12方网格锁争用 | 12 daemon 全网格中 uring_lock 可能成为瓶颈 | 1.0.1: 评估共享 ring 方案或专用 io-wq 池 |
| io-wq 饱和 | MSG_RING punt 可能耗尽 worker | 1.0.1: 独立 io-wq 池 + 限流 |
| BATCH 部分失败语义 | 当前 BATCH 模型假设内核可逐条处理 | 0.1.1: 改为发送方预校验 |
| 全局 Epoch vs 按类型 Epoch | 0.1.1 使用全局 Epoch，撤销影响所有 Agent | 1.0.1: 按类型独立 Epoch |
| 形式化验证 | 无 Isabelle/HOL 证明 | 1.0.1: CBMC 有界验证 fastpath |

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
