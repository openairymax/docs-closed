Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 29 — A-IPC 全面深化重新设计

## "以 Capability Folding 为基石的 Unified Airymax IPC Fabric"

> **文档性质**：基于 16~28 号共 13 份审查报告的最终工程方案
> **撰写日期**：2026-07-18
> **设计层级**：agent-linux 内核级工程
> **设计基准**：Airymax Unify Design 总纲（[10-unify-design.md](../../../../../docs-linux/10-architecture/10-unify-design.md) v1.0）
> **前置基础**：184 份 AirymaxOS 文档完整阅读 + 13 份 IPC 审查报告
> **设计哲学**：乔布斯/艾夫"简约就是美"——"对复杂事物的精髓进行深度挖掘和精准提炼"

---

## §0 设计起源

### 0.1 十三轮审查收敛的根本结论

| 轮次 | 发现 | 本轮贡献 |
|------|------|---------|
| 16 | IORING_OP_IPC_* 不可行，必须走 IORING_OP_URING_CMD + cmd_op | 传输层基线 |
| 17 | 12 处文档不一致 + 4 处设计空缺 | 文档一致性基线 |
| 18 | 总纲 §8 代码正确，下层文档滞后 | 确立总纲为 SSoT |
| 19 | 7 个设计缺陷（排序/BATCH/抢占/竞态/MSG_RING/时钟/timestamp） | 设计深度基线 |
| 20 | Capability Folding 仅论文存在，工程文档零存在 | 论文与工程的脱节 |
| 21 | 生产就绪度 3/6 不通过（隔离/一致性/上限） | 量化评估基线 |
| 22 | Capability Folding 融合可改善至 4/6 + 1 需验证 | 融合可行性 |
| 23 | Native Word 方案不需全面重构，5 个风险可缓解 | 方案精确化 |
| 24 | 融入方案可行，9-15 天工期 | 融入路径 |
| 25 | 不是融入——是重构。消除控制面作为独立 IPC 子系统 | 重构定性 |
| 26 | 第三方五大风险证伪——重构方案同时降低复杂度/提升效率/强化安全 | 风险证伪 |
| 27 | 第一版完整重构方案 | 工程方案 v1 |
| 28 | 发现 7 颗"看不见的螺丝"——drain/CRC32/NULL Badge/Epoch 矛盾/未定义字段/SLOW_PATH 合并/__future | 简约化精炼 |

**收敛结论**：A-IPC 必须以 Capability Folding（Native Word / Badge+Epoch）为基石重新设计，消除控制面作为独立 IPC 子系统，所有通信走 io_uring 数据面，能力校验通过两条 CPU 指令完成。

### 0.2 与 Airymax Unify Design 总纲的对齐

本设计严格遵循 [10-unify-design.md](../../../../../docs-linux/10-architecture/10-unify-design.md) v1.0 的 SSoT 声明：

| 总纲约束 | 本设计对齐方式 |
|---------|---------------|
| §10 SSoT：IPC 采用 IORING_OP_URING_CMD + registered buffer + mmap | §1.1 完全采用，不使用 page flipping |
| §10 SSoT：安全采用纯 C LSM 模块 | §3.2 Badge 校验作为纯 C LSM 第一层 |
| §10 SSoT：调度使用 sched_tac | §4.3 sched_tac 不变，A-IPC 不修改调度语义 |
| §10 SSoT：日志内存 alloc_pages + mmap | §3.1 A-IPC 共享内存同样使用 alloc_pages + mmap |
| §10 SSoT：[SC] 物理宿主 kernel/include/airymax/ | §5.1 ipc.h 唯一物理宿主不变 |
| §2.1：A-IPC 是通信骨干 | §4 全面对接 A-UEF/A-ULP/A-UCS/A-ULS |
| §3：A-IPC 核心覆盖通信 + 辅助覆盖韧性 | §6 数据面自治三原则保留 |
| §8.3：数据面自治三原则 | §6.1 完整保留 |
| §8.4：IPC 队列冻结 | §6.2 完整保留 |
| §9：[DSL] 降级生存层 | §7 [DSL] 下 A-IPC 的最小行为定义 |

### 0.3 不可变更的硬约束（来自 184 份文档 + 总纲）

| # | 约束 | 来源 |
|---|------|------|
| H1 | IPC 吞吐 > 100K msg/s | FR-003 / NFR-P-002 |
| H2 | IPC 延迟 < 10μs | FR-016 |
| H3 | 128B 定长消息头，Layout C | ADR-005 |
| H4 | magic = 0x41524531 'ARE1' | [SC] ipc.h |
| H5 | IORING_OP_URING_CMD + registered buffer + mmap | 总纲 §10 |
| H6 | 纯 C LSM，不使用 BPF LSM | 总纲 §10 |
| H7 | sched_tac，不使用 sched_ext | 总纲 §10 |
| H8 | kthread 间禁用 io_uring，必须用 kfifo + wait_event | 03-microkernel-strategy §10.1 |
| H9 | capability 安全模型，未授权 100% 拒绝 | FR-021 / NFR-S-001 |
| H10 | capability 优先于 SELinux，LSM_ORDER_FIRST | 08-threat-model §4.1.1 |
| H11 | 数据面自治三原则不可删除 | 总纲 §8.3 |
| H12 | [DSL] 降级生存层 | 11-degraded-survival-layer |
| H13 | agentrt [SC] 共享，双端逐字节一致 | IRON-9 v3 |
| H14 | [SC] error.h 错误码空间：IPC [-41, -70] | 总纲 §4.2 |

---

## §1 A-IPC 架构总览

### 1.1 核心设计原则：四条工程铁律

经过 13 轮审查的精炼，A-IPC 的设计原则从 27 号方案的隐含假设提炼为四条明示铁律：

```
铁律 1: 消息即能力（Message IS Capability）
  一条消息能够被投递，当且仅当它携带一个合法的 Badge。
  不存在"先校验、后投递"的两步流程——校验即投递。

铁律 2: 控制面不存在（No Control Plane for IPC）
  12 个 seL4 风格 IPC syscall 中的 8 个被消除。
  保留的 airy_sys_call 不是 IPC——它是能力管理操作。
  通信与能力管理是两个独立的问题域，不应共享 syscall 入口。

铁律 3: Epoch 是唯一全局状态（Epoch Is The Single Global State）
  atomic_t airy_global_epoch（4 bytes）替代 radix tree + per-CPU cache +
  IPI coherency 的整个栈。
  无 drain，无 bitmap，无 mdelay。一条 atomic_inc 完成撤销。

铁律 4: 发送方持有证明（Sender Holds The Proof）
  Agent 从 sec_d 获取 Badge 后不再查询任何授权方。
  接收方不查询——接收方仅验证 Badge 的合法性与 Epoch 的新鲜度。
```

### 1.2 单平面架构

```
重构前（当前 agent-linux 方案）:
  ┌─────────────────────────┐    ┌──────────────────────────┐
  │ 控制面（seL4 风格）       │    │ 数据面（io_uring）         │
  │ 12 syscall, 同步阻塞     │    │ SQE/CQE + kfifo, 异步     │
  │ decode_and_invoke        │    │ cap_check_fast (cache)    │
  │ 能力校验路径 #1           │    │ 能力校验路径 #2           │
  └─────────────────────────┘    └──────────────────────────┘
              共享 Layout C（仅格式共享）

重构后（本设计）:
  ┌──────────────────────────────────────────────────┐
  │  A-IPC（io_uring 数据面 + Badge 自验证）           │
  │                                                  │
  │  所有消息走 IORING_OP_URING_CMD                   │
  │  每条消息头携带 capability_badge 字段              │
  │  能力校验 = (badge >> 32) == epoch                │
  │           && (badge & required) == required       │
  │                                                  │
  │  唯一能力校验路径，两条 CPU 指令                   │
  └──────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────┐
  │  能力管理（不是 IPC）                              │
  │  airy_sys_call → mint/derive/revoke/epoch_bump    │
  │  低频操作，不传递数据                              │
  └──────────────────────────────────────────────────┘
```

### 1.3 Layout C v3：精炼后的 128B 消息头

经 28 号审查移除 seq_num（无协议）、negotiated_ver（无握手）、修正 CRC32 覆盖范围后：

```
offset   0: magic            (4B)  0x41524531 'ARE1'
offset   4: opcode           (2B)  见 §2.1
offset   6: flags            (2B)  见 §2.2
offset   8: trace_id         (8B)  OpenTelemetry 全链路追踪
offset  16: timestamp_ns     (8B)  CLOCK_REALTIME（沿用 19 号审查 D6 修复）
offset  24: src_task         (8B)  源 Agent/daemon ID（内核填充，禁止用户态设置）
offset  32: dst_task         (8B)  目标 Agent/daemon ID
offset  40: payload_len      (4B)  payload 字节数
offset  44: capability_badge (8B)  Native Word (Epoch<<32 | Permissions Mask)
offset  52: crc32            (4B)  CRC32 覆盖 header[0:52) + payload
offset  56: __reserved[72]  (72B) 保留，必须为零（接收方校验）
─────────────────────────────────────────────────
总计:   128 字节
```

**28 号审查的 7 颗螺丝全部拧掉：**
- drain（消除，1 行 atomic_inc）
- CRC32 漏洞（修复，覆盖 capability_badge）
- NULL Badge 特例（消除，opcode CAP_REQUEST 替代）
- 全局/独立 Epoch 矛盾（统一为 1 个 global Epoch）
- seq_num + negotiated_ver（移除，不引入未定义字段）
- SLOW_PATH 合并（保留 SLOW_SEND / SLOW_RECV）
- __future[66] → __reserved[72]（明确为保留，不假装有定义）

### 1.4 Syscall 表：12 → 4

```
重构前: airy_sys_call, airy_sys_send, airy_sys_recv, airy_sys_nbsend,
         airy_sys_nbrecv, airy_sys_reply_recv, airy_sys_yield, airy_sys_reply,
         airy_sys_rovol_ctl, airy_sys_sched_ctl, airy_sys_clt_notify,
         airy_sys_notify
         (12 个 syscall，占用 512-523 编号段)

重构后: airy_sys_call        (512)  能力管理（mint/derive/revoke/epoch_bump）
         airy_sys_rovol_ctl   (519)  记忆卷载控制
         airy_sys_sched_ctl   (520)  调度控制
         airy_sys_clt_notify  (521)  认知循环通知
         (4 个 syscall)

消除的 8 个 syscall 的数据面等价物:
  airy_sys_send         → io_uring_prep_uring_cmd(SEND, badge=...) + io_uring_submit()
  airy_sys_recv         → io_uring_prep_uring_cmd(RECV) + io_uring_wait_cqe()
  airy_sys_nbsend       → io_uring_submit() 即返回（不 wait）
  airy_sys_nbrecv       → io_uring_peek_cqe()
  airy_sys_reply_recv   → io_uring SEND(RESPONSE) + io_uring_wait_cqe()
  airy_sys_yield        → IORING_ENTER_GETEVENTS（让出 + 等待）
  airy_sys_reply        → io_uring_prep_uring_cmd(SEND, flags=RESPONSE)
  airy_sys_notify       → eventfd_signal()（无 io_uring 开销）

保留编号 513-518, 522-523 作为 ABI 稳定性预留（禁止复用，标注 @deprecated）
```

---

## §2 A-IPC 操作码与控制流

### 2.1 opcode 表（6 个）

| opcode 值 | 符号 | 数据面 | 说明 |
|----------|------|:---:|------|
| 0x01 | `AIRY_IPC_OP_SEND` | ✅ | 标准发送 |
| 0x02 | `AIRY_IPC_OP_RECV` | ✅ | 标准接收 |
| 0x03 | `AIRY_IPC_OP_SEND_BATCH` | ✅ | 批量发送（一次 SQE 多消息） |
| 0x04 | `AIRY_IPC_OP_CANCEL` | ✅ | 取消未完成的异步操作 |
| 0x05 | `AIRY_IPC_OP_FREEZE` | ✅ | A-ULS 触发的队列冻结（仅 macro_superv 可用） |
| 0x10 | `AIRY_IPC_OP_CAP_REQUEST` | ✅ | 能力请求（无需 Badge，内核直接路由到 sec_d） |

**CAP_REQUEST 的设计意义（28 号审查修复）**：消除 NULL Badge 特例。Agent 启动时使用此 opcode 向 sec_d 请求能力编译，sec_d 返回编译好的 Badge。此后 Agent 使用标准 SEND + Badge 通信。

### 2.2 flags 位定义

| bit | 符号 | 含义 |
|-----|------|------|
| 0 | `AIRY_IPC_F_ZEROCOPY` | 使用 registered buffer 零拷贝 |
| 1 | `AIRY_IPC_F_CAP_CARRY` | 消息携带 capability_badge（默认置位） |
| 2 | `AIRY_IPC_F_RESPONSE` | 此消息是对先前请求的响应（替代 airy_sys_reply） |
| 3 | `AIRY_IPC_F_BATCH_HEAD` | BATCH 消息的起始 |
| 4 | `AIRY_IPC_F_BATCH_TAIL` | BATCH 消息的结束 |
| 5 | `AIRY_IPC_F_ENCRYPT` | payload 已加密（SM4，见 BR-007-05） |
| 6 | `AIRY_IPC_F_COMPRESS` | payload 已压缩 |
| 7-15 | — | 保留，必须为零 |

### 2.3 完整的 SEND 控制流

```
用户态 Agent:
  1. 准备 128B 消息头 + payload
  2. 填充 capability_badge（启动时从 sec_d 获取）
  3. 设置 flags |= AIRY_IPC_F_CAP_CARRY
  4. 计算 crc32（覆盖 header[0:52) + payload）
  5. io_uring_prep_uring_cmd(SQ, cmd_op=SEND, issue_flags=0)
  6. io_uring_submit()  ← 非阻塞，立即返回

内核态 fastpath（C-S0~C-S11 全部检查）:
  C-S0:  ring->frozen == false              ← A-ULS 冻结检查
  C-S1:  magic == 0x41524531
  C-S2:  opcode == AIRY_IPC_OP_SEND
  C-S3:  payload_len 合法
  C-S4:  sizeof(hdr) == 128
  C-S5:  smp_processor_id() == dst_cpu      ← 同 CPU fastpath 条件
  C-S6:  kfifo_is_full() == false
  C-S7:  current->reclaim_flag 未置          ← 内存回收上下文检查
  C-S8:  in_task() && !in_interrupt()
  C-S9:  [Capability Folding] badge 校验:
         epoch = (u32)(badge >> 32)
         if (epoch != atomic_read(&airy_global_epoch))
             → REJECT with AIRY_ECAP_EPOCH  ← inline deny
         if ((badge & AIRY_CAP_PERM_IPC_SEND) == 0)
             → REJECT with AIRY_ECAP_PERM   ← inline deny
  C-S10: flags 不含 ENCRYPT/COMPRESS（否则走 slowpath）
  C-S11: preempt_disable() 保护 kfifo 操作

通过 C-S0~C-S11:
  → kfifo_in(dst_kfifo, msg, 128 + payload_len)
  → eventfd_signal(dst_eventfd)
  → io_uring_cqe_fill(SQ, res=0)
  → preempt_enable()

任一检查失败:
  → io_uring_cqe_fill(SQ, res=-Exxx)
  → 不唤醒接收方（inline deny）
```

---

## §3 Capability Folding：A-IPC 的基石

### 3.1 Native Word 设计

```
 63                  32  31                   0
┌─────────────────────┬──────────────────────┐
│       Epoch         │    Permissions Mask   │
│  (32-bit 代际编号)  │  (32-bit 权限位掩码)  │
└─────────────────────┴──────────────────────┘

Epoch:
  - 全局唯一 atomic_t（4 bytes），初始化为 1
  - 每次能力撤销递增 1（一条 atomic_inc，无 drain）
  - 0 保留（表示"未初始化 Badge"）

Permissions Mask（位定义）:
  bit 0:  AIRY_CAP_PERM_IPC_SEND       IPC 发送
  bit 1:  AIRY_CAP_PERM_IPC_RECV       IPC 接收
  bit 2:  AIRY_CAP_PERM_FILE_READ      文件读
  bit 3:  AIRY_CAP_PERM_FILE_WRITE     文件写
  bit 4:  AIRY_CAP_PERM_MEM_QUERY      记忆查询
  bit 5:  AIRY_CAP_PERM_MEM_UPDATE     记忆更新
  bit 6:  AIRY_CAP_PERM_COGN_SUBMIT    认知任务提交
  bit 7:  AIRY_CAP_PERM_SCHED_CTL      调度控制
  bit 8:  AIRY_CAP_PERM_SEC_POLICY     安全策略
  bit 9:  AIRY_CAP_PERM_AUDIT_READ     审计读
  bit 31: AIRY_CAP_PERM_BOOTSTRAP      自举（仅 CAP_REQUEST 使用）
  bit 10-30: 保留，必须为零
```

### 3.2 Epoch 管理（极简实现）

```c
/* kernel/ipc/airy_epoch.c —— 完整实现，1 个 atomic_t */

#include <linux/atomic.h>

static atomic_t airy_global_epoch = ATOMIC_INIT(1);

/**
 * airy_cap_epoch_get - 读取当前 Epoch（fastpath 使用，无锁）
 */
static inline u32 airy_cap_epoch_get(void)
{
    return (u32)atomic_read(&airy_global_epoch);
}

/**
 * airy_cap_epoch_bump - 撤销能力时递增 Epoch
 *
 * 一条 atomic_inc。无 drain，无 bitmap，无 mdelay，无 smp_mb。
 *
 * 语义：Epoch 递增后，所有携带旧 Epoch 的 Badge 立即失效。
 *       在途消息（已在 kfifo/ring buffer 中的）会在接收时被拒绝。
 *       发送方收到 -AIRY_ECAP_EPOCH 后，重新向 sec_d 请求 Badge。
 *
 * 这不是"立即阻止所有消息"——这是"确保不再有新的未授权消息被投递"。
 * 区别在于：drain 试图保证发送方不遇到意外 REJECT；epoch_bump 接受
 * 极少数在途消息被拒绝，因为发送方本就应该处理 REJECT。
 */
void airy_cap_epoch_bump(void)
{
    atomic_inc(&airy_global_epoch);
    /* x86 上 lock incl 立即全局可见，无需额外屏障 */
}

/**
 * airy_cap_epoch_init - 系统启动时初始化
 */
void airy_cap_epoch_init(void)
{
    atomic_set(&airy_global_epoch, 1);
}
```

**代码量：3 个函数，~30 行 C。**

### 3.3 Badge 编译（sec_d 在连接建立期调用）

```c
/* kernel/ipc/airy_badge.c —— 完整实现 */

#include <linux/types.h>

/**
 * airy_cap_badge_compile - 为 Agent 编译 Native Word Badge
 * @cap_mask:  该 Agent 被授权的权限位掩码
 *
 * 返回: 64-bit Badge = (Epoch << 32) | cap_mask
 *
 * 由 sec_d 在 Agent 启动期调用（非 fastpath）。
 * 编译好的 Badge 通过 CAP_RESPONSE 返回给 Agent，Agent 嵌入所有
 * 后续消息的 capability_badge 字段。
 */
u64 airy_cap_badge_compile(u32 cap_mask)
{
    u32 epoch = airy_cap_epoch_get();
    return ((u64)epoch << 32) | (u64)cap_mask;
}

/**
 * airy_cap_badge_verify - 校验 Badge（唯一的能力校验路径）
 * @badge:    消息头中的 capability_badge 字段
 * @required: 需要的权限位掩码
 *
 * 返回: 0 = 通过, <0 = 错误码
 *
 * 此函数在 fastpath 中每消息调用一次。
 * 两条 CPU 指令: SHR (badge >> 32) + AND (badge & required)
 * 延迟: ~5ns，确定性（无 cache miss 路径）
 */
int airy_cap_badge_verify(u64 badge, u32 required)
{
    u32 epoch;

    if (unlikely(badge == 0))
        return -AIRY_ECAP_BADGE;  /* 不允许全零 Badge */

    epoch = (u32)(badge >> 32);
    if (epoch != airy_cap_epoch_get())
        return -AIRY_ECAP_EPOCH;  /* Epoch 不匹配，Badge 已失效 */

    if ((badge & required) != required)
        return -AIRY_ECAP_PERM;   /* 权限不足 */

    return 0;
}

/* 内联版本 — 用于 fastpath C-S9 */
static inline bool airy_cap_badge_ok(u64 badge, u32 required)
{
    u32 epoch = (u32)(badge >> 32);
    return epoch == airy_cap_epoch_get()
           && (badge & required) == required;
}
```

**代码量：2 个函数 + 1 个 inline，~30 行 C。**

### 3.4 CAP_REQUEST 自举流程（消除 NULL Badge 特例）

```
Agent 启动序列:
  1. Agent 进程 fork/exec 完成
  2. Agent 初始化 io_uring ring
  3. Agent 发送 CAP_REQUEST:
       opcode = AIRY_IPC_OP_CAP_REQUEST
       capability_badge = 0  ← 全零，不携带任何权限
       payload = { agent_id, requested_permissions_mask }
       dst_task = sec_d_task_id  ← 内核直接路由（不经过通用 SEND 路径）
  4. sec_d 收到 CAP_REQUEST:
       - 验证 agent_id 的合法性
       - 查询安全策略（SELinux + Cupolas + 国密证书链）
       - 编译 Badge: airy_cap_badge_compile(granted_mask)
       - 返回 CAP_RESPONSE:
           opcode = AIRY_IPC_OP_SEND
           flags |= AIRY_IPC_F_RESPONSE
           payload = { compiled_badge, granted_mask, expires_at }
  5. Agent 提取 Badge，嵌入所有后续消息

内核 fastpath 对 CAP_REQUEST 的特殊处理:
  if (unlikely(opcode == AIRY_IPC_OP_CAP_REQUEST)) {
      if (dst_task != sec_d_task_id)
          return -AIRY_ECAP_PERM;  /* CAP_REQUEST 只能发给 sec_d */
      goto route_to_sec_d;  /* 跳过 C-S9 badge 校验 */
  }
  /* 其他 opcode 走标准 C-S9 badge 校验 */

这是一颗"通用螺丝"——不是针对特定 Badge 值的特例。
任何 Agent 任何时候都可以通过 CAP_REQUEST 重新请求能力。
```

### 3.5 能力撤销流程

```
撤销场景：Agent A 的 IPC_SEND 权限被撤销

  1. macro_superv 通过 airy_sys_call(ROVOL_CTL, REVOKE, agent_id=A) 发起撤销
  2. sec_d 执行:
     - 从 CNode 表中标记 A 的 IPC_SEND 权限为 revoked
     - 调用 airy_cap_epoch_bump()
       ↓
       一条 atomic_inc。全局 Epoch N → N+1。
       所有 Agent 的所有 Badge 立即失效。
       ↓
     - 通知所有活跃 Agent：通过 eventfd 广播 EPOCH_BUMP 事件
  3. 各 Agent 收到 EPOCH_BUMP 事件:
     - 重新发送 CAP_REQUEST（携带原 requested_permissions_mask）
     - sec_d 重新编译 Badge:
         - 权限仍存在的 Agent：获得新 Badge（Epoch=N+1）
         - 权限被撤销的 Agent A：获得新 Badge（Epoch=N+1, IPC_SEND=0）
  4. Agent A 尝试 SEND:
     - C-S9: badge & AIRY_CAP_PERM_IPC_SEND == 0
     - REJECT with -AIRY_ECAP_PERM

总成本:
  - 1 条 atomic_inc（撤销生效）
  - N 次 eventfd_signal（通知，N=活跃 Agent 数）
  - N 次 CAP_REQUEST/CAP_RESPONSE（重编译，每个 ~100μs）
  - 0 次 IPI，0 次 per-CPU cache invalid，0 次 drain
```

---

## §4 A-IPC 与 Unify Design 五模块的完整对接

### 4.1 A-IPC × A-UEF（错误码空间）

A-IPC 的错误码全部归入 A-UEF 的 IPC 码空间 `[-41, -70]`：

| 错误码 | 值 | 含义 | 触发场景 |
|--------|-----|------|---------|
| `AIRY_ECAP_EPOCH` | -41 | Epoch 不匹配 | Badge 已失效，需重新编译 |
| `AIRY_ECAP_PERM` | -42 | 权限不足 | Badge 不含所需权限位 |
| `AIRY_ECAP_BADGE` | -43 | Badge 格式无效 | 全零 Badge 或格式错误 |
| `AIRY_ECAP_FROZEN` | -44 | Ring 已冻结 | A-ULS 触发的队列冻结 |
| `AIRY_EIPC_MAGIC` | -45 | magic 校验失败 | 消息头 magic ≠ 0x41524531 |
| `AIRY_EIPC_CRC32` | -46 | CRC32 校验失败 | 消息被篡改或损坏 |
| `AIRY_EIPC_OPCOD` | -47 | opcode 非法 | opcode 不在 §2.1 表中 |
| `AIRY_EIPC_RANGE` | -48 | payload_len 超限 | payload_len > 注册缓冲区大小 |
| `AIRY_EIPC_KFIFO` | -49 | kfifo 满 | 接收方 kfifo 已满 |
| `AIRY_EIPC_BATCH` | -50 | BATCH 部分失败 | BATCH 中部分消息失败（见 19 号 D2 修复） |
| `AIRY_EIPC_CROSS` | -51 | 跨 CPU 路径失败 | SLOW_PATH 跨 CPU 投递失败 |
| `AIRY_EIPC_TIMEOUT` | -52 | 异步操作超时 | io_uring 操作超时 |
| -53~-70 | — | 保留 | 未来扩展 |

### 4.2 A-IPC × A-ULP（日志传递）

```
A-IPC 异常 → A-ULP Ring Buffer:

  1. fastpath 校验失败（C-S0~C-S11 任一失败）
  2. 内核调用 airy_log_ring_reserve(128B slot)
  3. memcpy 128B raw binary 日志记录:
       magic = 0x414C4F47 ('ALOG')
       level = LOG_WARN / LOG_ERROR
       facility = AIRY_FACILITY_IPC
       timestamp_ns = CLOCK_MONOTONIC
       caller_id = smp_processor_id()
       payload = { opcode, failed_check, badge, src_task, dst_task }
  4. airy_log_ring_commit()
  5. eventfd_signal(logger_daemon_eventfd)

Logger Daemon 异步消费:
  - mmap 读取 Ring Buffer
  - 格式化: "IPC REJECT: opcode=%d check=C-S%d badge=0x%llx src=%d dst=%d"
  - 过滤 + 落盘 + 轮转

A-IPC 不直接调用 printk——遵循 A-ULP 的"Fastpath 禁止格式化"原则。
```

### 4.3 A-IPC × A-UCS（配置热重载）

A-IPC 的运行时配置通过 A-UCS 的 sysctl + JSON 双向同步：

| sysctl 路径 | 默认值 | 说明 |
|------------|--------|------|
| `kernel.airy_ipc.ring_entries` | 256 | 每个 io_uring ring 的 SQ/CQ 条目数 |
| `kernel.airy_ipc.batch_threshold` | 8 | 触发 BATCH 模式的消息数阈值 |
| `kernel.airy_ipc.cap_cache_ttl_ms` | 0 | Badge 缓存 TTL（0=不缓存，每次校验） |
| `kernel.airy_ipc.frozen_timeout_ms` | 5000 | 冻结后自动解冻的超时（watchdog fallback） |
| `kernel.airy_ipc.epoch_bump_broadcast` | 1 | Epoch 递增时是否广播 eventfd（1=是，0=否） |

配置变更通过 RCU 原子切换，读者通过 `rcu_dereference()` 获取最新配置。

### 4.4 A-IPC × A-ULS（生命周期监管）

```
A-ULS 触发 A-IPC 冻结:

  1. Micro-Supervisor（纯 C LSM）检测到非法 Capability
     - 例：fastpath C-S9 返回 -AIRY_ECAP_BADGE
     - 或：CNode 表完整性校验失败
  2. Micro-Supervisor 设置 ring->frozen = true
     - smp_store_release(&ring->frozen, true)
     - 立即对所有 CPU 可见
  3. fastpath C-S0 检查:
     if (unlikely(ring->frozen))
         return -AIRY_ECAP_FROZEN;
     ← 零开销（unlikely 分支预测）
  4. eventfd 通知 Macro-Supervisor
  5. Macro-Supervisor 裁决:
     - 警告: 不解冻，记录日志
     - 降级: 不解冻，缩减 Agent 预算
     - 暂停: 不解冻，kill(SIGSTOP)
     - 终止: 不解冻，kill(SIGKILL)
  6. 裁决完成后（如需解冻）:
     macro_superv 发送 AIRY_IPC_OP_FREEZE（flags=UNFREEZE）
     → ring->frozen = false

A-ULS 的 Macro-Supervisor 通过 A-IPC 通信:
  - 心跳: 每 1s 向所有 daemon 发送 PING（io_uring SEND）
  - 裁决: 通过 airy_sys_call(ROVOL_CTL, ...) 触发
  - 撤销: 通过 airy_sys_call(CAP_REVOKE) → epoch_bump
```

### 4.5 A-IPC × [DSL]（降级生存层）

[DSL] 降级模式下 A-IPC 的最小行为（对齐 11-degraded-survival-layer）：

| 维度 | 正常模式 | [DSL] 降级模式 |
|------|---------|---------------|
| 消息头 | 完整 128B Layout C v3 | 最简 128B（仅 magic + opcode + payload_len，其余置零） |
| opcode | 6 个 | 2 个（SEND, RECV） |
| Badge 校验 | C-S9 完整校验 | 跳过（仅 POSIX capability） |
| 冻结机制 | 支持 | 不支持（直接 kill 进程） |
| BATCH | 支持 | 不支持 |
| CAP_REQUEST | 支持 | 不支持（使用 POSIX capability 自举） |
| io_uring | IORING_OP_URING_CMD | 降级为 Unix socket（io_uring 不可用时） |
| 错误码 | 完整 -41~-70 | 仅 POSIX -1~-40 |

[DSL] 降级由 `#ifdef AIRY_SC_FALLBACK` 编译时触发，或在运行时由 Micro-Supervisor 检测到 [SC] 头文件校验失败时触发。

---

## §5 [SC] 共享契约层

### 5.1 ipc.h 的物理宿主与双端一致性

```
物理宿主: kernel/include/airymax/ipc.h（唯一）
消费方:
  - agent-linux: kernel/, services/ 通过 -I../kernel/include 引用
  - agentrt: 通过 git submodule 或 -I 引用

CI 校验: sc-dual-ci.yml
  - 提取 agentrt 的 ipc.h 哈希
  - 提取 agent-linux 的 ipc.h 哈希
  - 两者必须逐字节一致
  - 不一致则 CI 失败
```

### 5.2 ipc.h 的内容定义

```c
/* kernel/include/airymax/ipc.h —— [SC] 共享契约层 */

#ifndef _AIRY_IPC_H
#define _AIRY_IPC_H

/* §1 magic */
#define AIRY_IPC_MAGIC          0x41524531u  /* 'ARE1' */

/* §2 opcode */
#define AIRY_IPC_OP_SEND        0x01
#define AIRY_IPC_OP_RECV        0x02
#define AIRY_IPC_OP_SEND_BATCH  0x03
#define AIRY_IPC_OP_CANCEL      0x04
#define AIRY_IPC_OP_FREEZE      0x05
#define AIRY_IPC_OP_CAP_REQUEST 0x10

/* §3 flags */
#define AIRY_IPC_F_ZEROCOPY     0x0001
#define AIRY_IPC_F_CAP_CARRY    0x0002
#define AIRY_IPC_F_RESPONSE     0x0004
#define AIRY_IPC_F_BATCH_HEAD   0x0008
#define AIRY_IPC_F_BATCH_TAIL   0x0010
#define AIRY_IPC_F_ENCRYPT      0x0020
#define AIRY_IPC_F_COMPRESS     0x0040

/* §4 Capability Permissions Mask */
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
#define AIRY_CAP_PERM_BOOTSTRAP     (1u << 31)

/* §5 128B 消息头 Layout C v3 */
#pragma pack(push, 1)
struct airy_ipc_msg_hdr {
    uint32_t magic;             /* offset  0: 0x41524531 */
    uint16_t opcode;            /* offset  4: 见 §2 */
    uint16_t flags;             /* offset  6: 见 §3 */
    uint64_t trace_id;          /* offset  8: OpenTelemetry */
    uint64_t timestamp_ns;      /* offset 16: CLOCK_REALTIME */
    uint64_t src_task;          /* offset 24: 内核填充 */
    uint64_t dst_task;          /* offset 32: 目标 ID */
    uint32_t payload_len;       /* offset 40: payload 字节数 */
    uint64_t capability_badge;  /* offset 44: Native Word */
    uint32_t crc32;             /* offset 52: 覆盖 [0:52)+payload */
    uint8_t  __reserved[72];    /* offset 56: 保留，必须为零 */
}; /* sizeof = 128 */
#pragma pack(pop)

/* §6 编译时断言 */
_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128,
               "airy_ipc_msg_hdr must be exactly 128 bytes");

/* §7 io_uring cmd_op 编码（agent-linux 专用，agentrt 不使用） */
#define AIRY_URING_CMD_IPC_SEND        0x0001
#define AIRY_URING_CMD_IPC_RECV        0x0002
#define AIRY_URING_CMD_IPC_SEND_BATCH  0x0003
#define AIRY_URING_CMD_IPC_CANCEL      0x0004
#define AIRY_URING_CMD_IPC_FREEZE      0x0005
#define AIRY_URING_CMD_IPC_CAP_REQUEST 0x0010

/* §8 [DSL] 降级块 */
#ifdef AIRY_SC_FALLBACK
/* 降级模式：仅 magic + opcode + payload_len 有效，其余必须为零 */
#define AIRY_IPC_OP_SEND_FALLBACK    0x01
#define AIRY_IPC_OP_RECV_FALLBACK    0x02
#warning "AIRY_SC_FALLBACK active: IPC reduced to SEND/RECV only"
#endif /* AIRY_SC_FALLBACK */

#endif /* _AIRY_IPC_H */
```

### 5.3 agentrt 与 agent-linux 的使用差异

| 维度 | agentrt（用户态） | agent-linux（内核态） |
|------|------------------|----------------------|
| 传输层 | POSIX MQ + mmap 共享内存 | IORING_OP_URING_CMD + registered buffer |
| 同步原语 | 信号量 | eventfd |
| Badge 校验 | 用户态 airy_cap_badge_verify() | 内核态 fastpath C-S9 |
| Epoch 管理 | 不管理（读取 agent-linux 的 Epoch） | 唯一管理者（atomic_t） |
| 消息头 | 同一份 ipc.h（[SC] 共享） | 同一份 ipc.h（[SC] 共享） |

agentrt 在普通 Linux/macOS/Windows 上运行时，不使用 Badge 机制——使用用户态 Cupolas 权限引擎。仅在 agent-linux 上运行时，agentrt 通过 airy_sys_call 获取 Badge，嵌入 IPC 消息头。

---

## §6 数据面自治三原则（保留总纲 §8.3）

### 6.1 Ring 生命周期解耦

```
Ring Buffer 的生命周期独立于控制面连接:

  - io_uring ring 通过 io_uring_setup() 创建，独立于 Agent 进程
  - Agent 进程崩溃重启后，重新 mmap 同一个 ring（通过 ring_fd）
  - 未消费的消息不丢失（在 kfifo 中等待）
  - ring 的销毁由 macro_superv 通过 AIRY_IPC_OP_FREEZE 显式触发

实现:
  - ring_fd 作为独立的匿名 inode（anon_inode_get("airy_ipc_ring")）
  - Agent 进程持有 ring_fd 的 fd
  - Agent 崩溃时 fd 自动关闭，但 ring 内存不立即释放
  - macro_superv 通过 /proc/airy/rings/ 查看所有活跃 ring
  - macro_superv 决定何时销毁 ring（通常在 Agent 重启后或终止后）
```

### 6.2 离线缓存校验（重构为离线 Epoch 快照）

```
重构前（总纲 §8.3 原文）:
  Capability 校验结果缓存在内核 radix tree，控制面离线时仍可基于缓存校验

重构后（本设计）:
  Badge 已由 sec_d 在连接建立期编译，嵌入消息头。
  sec_d 离线时，fastpath 仍可基于 Badge 的 Epoch 校验——
  因为 Epoch 是全局 atomic_t，不依赖 sec_d 在线。

  sec_d 离线的影响:
  - 新的 CAP_REQUEST 无法处理（Agent 无法获取新 Badge）
  - 已有 Badge 仍可正常使用（Epoch 校验不依赖 sec_d）
  - 能力撤销无法执行（epoch_bump 由 sec_d 触发）

  sec_d 恢复后:
  - 处理积压的 CAP_REQUEST
  - 如有撤销操作待执行，执行 epoch_bump
  - 通过 Reconciliation 同步离线期间的安全策略变更
```

### 6.3 Reconciliation

```
sec_d 恢复后，数据面将离线期间的状态变更同步给 sec_d:

  1. 数据面记录离线期间的:
     - 所有 REJECT 事件（C-S9 失败的）
     - 所有 CAP_REQUEST 失败事件
     - kfifo 溢出事件
  2. sec_d 恢复后，数据面通过 io_uring SEND 将记录发送给 sec_d
  3. sec_d 分析 Reconciliation log:
     - 如有异常模式（某 Agent 频繁 REJECT），触发撤销
     - 如有合法 Agent 无法获取 Badge，优先处理
  4. Reconciliation 完成后，sec_d 进入正常服务状态
```

---

## §7 Fastpath 状态机（7 态）

### 7.1 状态定义

```
重构前（8 态）: IDLE, FAST_SEND, FAST_RECV, SLOW_SEND, SLOW_RECV, BATCH, CANCEL, ERROR
重构后（7 态）: IDLE, CHECK, FAST_SEND, FAST_RECV, SLOW_SEND, SLOW_RECV, BATCH, CANCEL, ERROR

新增 CHECK 态: 在 IDLE → FAST_SEND/RECV 之前插入，仅执行 Badge 校验。
保留 SLOW_SEND / SLOW_RECV 区分（28 号审查修复 #6）。
```

### 7.2 状态转换表

```
IDLE
  ├─[SQE arrives]→ CHECK
  │                 ├─[badge OK, all C-S pass]→ FAST_SEND ──→ IDLE
  │                 ├─[badge OK, payload>128B or cross-CPU]→ SLOW_SEND ──→ IDLE
  │                 ├─[opcode=RECV]→ FAST_RECV ──→ IDLE
  │                 ├─[opcode=RECV, no msg]→ SLOW_RECV ──→ IDLE
  │                 ├─[opcode=SEND_BATCH]→ BATCH ──→ IDLE
  │                 ├─[opcode=CANCEL]→ CANCEL ──→ IDLE
  │                 ├─[any C-S fail]→ ERROR ──→ IDLE
  │                 └─[opcode=CAP_REQUEST]→ route_to_sec_d ──→ IDLE
  └─[ring->frozen]→ ERROR (-AIRY_ECAP_FROZEN) ──→ IDLE
```

### 7.3 fastpath 条件检查完整表

| 条件 | 检查内容 | 失败返回码 | 28 号审查修复 |
|------|---------|-----------|-------------|
| C-S0 | `ring->frozen == false` | -AIRY_ECAP_FROZEN | 保留（总纲 §8.4） |
| C-S1 | `magic == 0x41524531` | -AIRY_EIPC_MAGIC | 保留 |
| C-S2 | `opcode` 合法 | -AIRY_EIPC_OPCOD | 保留 |
| C-S3 | `payload_len` 合法 | -AIRY_EIPC_RANGE | 保留 |
| C-S4 | `sizeof(hdr) == 128` | -AIRY_EIPC_RANGE | 保留 |
| C-S5 | `smp_processor_id() == dst_cpu` | 走 SLOW_PATH | 保留 |
| C-S6 | `kfifo_is_full() == false` | -AIRY_EIPC_KFIFO | 保留 |
| C-S7 | `current->reclaim_flag` 未置 | -AIRY_EIPC_CROSS | 保留 |
| C-S8 | `in_task() && !in_interrupt()` | -AIRY_EIPC_CROSS | 保留 |
| C-S9 | Badge 校验（2 条指令） | -AIRY_ECAP_EPOCH / -AIRY_ECAP_PERM | **重构**：从黑盒变为 2 条指令 |
| C-S10 | flags 不含 ENCRYPT/COMPRESS | 走 SLOW_PATH | 保留 |
| C-S11 | `preempt_disable()` 保护 | — | 保留（19 号 D3 修复） |

### 7.4 fastpath 延迟分析

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
10. C-S6  kfifo 滀检查               (5ns)
11. C-S7  reclaim check              (2ns)
12. C-S8  context check              (2ns)
13. C-S10 encrypt/compress check     (2ns)
14. preempt_disable                  (1ns)
15. kfifo_in                         (50ns) 无锁 SPSC
16. eventfd_signal                   (20ns)
17. io_uring_cqe_fill                (20ns)
18. preempt_enable                   (1ns)
─────────────────────────────────────────
 总计:                               ~118ns

vs 重构前: ~160ns (cache hit) / ~260ns (cache miss)
改善: -26% / -55%, 延迟变为确定性
```

---

## §8 12 Daemon 通信路径

### 8.1 通信路径矩阵

| Daemon | 数据消息（io_uring + Badge） | 能力操作（低频 syscall） |
|--------|----------------------------|----------------------|
| `macro_superv` | 心跳 PING（每 1s × 11 daemon = 11 msg/s） | airy_sys_call(CAP_REVOKE) |
| `logger_daemon` | mmap Ring Buffer 读取（非 IPC） | — |
| `config_daemon` | 配置变更广播（0-10/h） | — |
| `gateway_d` | Agent 请求路由（10K-1M msg/s） | — |
| `sched_d` | 调度策略下发（低频） | airy_sys_sched_ctl |
| `vfs_d` | 文件 I/O 请求（10K-500K msg/s） | — |
| `net_d` | 网络包处理（10K-1M msg/s） | — |
| `mem_d` | 记忆查询/更新（1-100 msg/s） | airy_sys_rovol_ctl |
| `cogn_d` | 认知任务收发（10-1K msg/s） | airy_sys_clt_notify |
| `sec_d` | CAP_RESPONSE（按需） | airy_sys_call(MINT/DERIVE/REVOKE/EPOCH_BUMP) |
| `audit_d` | 审计事件接收（1K-10K msg/s） | — |
| `dev_d` | 设备 I/O（1-10K msg/s） | — |

**12 daemon 中 10 个纯数据面 + Badge，仅 `sec_d` 和 `macro_superv` 间或使用能力管理 syscall。**

### 8.2 12 daemon 的 Badge 权限矩阵

| Daemon | IPC_SEND | IPC_RECV | FILE_READ | FILE_WRITE | MEM_QUERY | MEM_UPDATE | COGN_SUBMIT | SCHED_CTL | SEC_POLICY | AUDIT_READ |
|--------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| macro_superv | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| logger_daemon | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| config_daemon | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| gateway_d | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| sched_d | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| vfs_d | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| net_d | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| mem_d | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| cogn_d | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| sec_d | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| audit_d | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| dev_d | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

sec_d 不需要 IPC_SEND——它是能力管理的服务端，通过 CAP_REQUEST opcode 接收请求（内核路由，不走通用 SEND 路径）。

---

## §9 对 agent-linux 整体方案的影响

### 9.1 影响的文档清单

| 文档 | 影响类型 | 修改内容 |
|------|---------|---------|
| 10-unify-design.md §8 | 重大修改 | A-IPC 描述更新为 Capability Folding 基石 |
| 30-interfaces/01-syscalls.md | 重大修改 | syscall 表 12 → 4，移除 8 个 IPC syscall |
| 30-interfaces/02-ipc-protocol.md | 重大修改 | Layout C v3，移除 IORING_OP_IPC_*，新增 CAP_REQUEST |
| 30-interfaces/07-ipc-fastpath.md | 重大修改 | 状态机 8 → 7 态，C-S9 重构为 2 条指令 |
| 40-dataflows/03-ipc-flow.md | 重大修改 | 消除控制面数据流，统一为数据面 |
| 20-modules/01-kernel.md | 中等修改 | syscall 表更新，IPC 模块描述更新 |
| 20-modules/02-services.md | 中等修改 | daemon 通信路径全部走数据面 |
| 20-modules/03-security.md | 中等修改 | Capability 模型增加 Badge + Epoch |
| 110-security/03-capability-model.md | 重大修改 | 移除 radix tree + per-CPU cache，新增 Badge + Epoch |
| 110-security/04-ipc-data-plane-autonomy.md | 中等修改 | 数据面自治三原则的离线缓存改为离线 Epoch 快照 |
| 110-security/05-ipc-control-plane-reconciliation.md | 重大修改 | 控制面 Reconciliation 重新定义为 sec_d 恢复后的状态同步 |
| 170-performance/03-ipc-performance.md | 重大修改 | 性能 SLO 更新（fastpath ~118ns） |
| 160-compatibility/04-ipc-versioning.md | 中等修改 | 版本协商通过 CAP_REQUEST 完成 |
| 50-engineering-standards/90-terminology.md | 小修改 | 新增术语：Badge, Epoch, Capability Folding |
| 50-engineering-standards/09-ssot-registry.md | 小修改 | 新增 SSoT 条目：A-IPC v2 |

### 9.2 影响的代码模块

| 代码模块 | 影响类型 | 估计代码量 |
|---------|---------|-----------|
| `kernel/ipc/airy_epoch.c` | 新增 | ~30 行 |
| `kernel/ipc/airy_badge.c` | 新增 | ~30 行 |
| `kernel/ipc/airy_uring_cmd.c` | 修改 | 新增 CAP_REQUEST 路由 |
| `kernel/ipc/airy_ipc_fastpath.c` | 修改 | C-S9 重构 |
| `kernel/ipc/airy_ipc_cap.c` | 删除 | radix tree + per-CPU cache 消除 |
| `kernel/ipc/airy_ipc_reconcile.c` | 修改 | Reconciliation 逻辑更新 |
| `kernel/superv/airy_cap_check.c` | 修改 | 纯 C LSM 钩子使用 badge_verify |
| `services/daemons/sec_d/` | 修改 | 新增 Badge 编译服务 |
| `services/daemons/macro_superv/` | 修改 | 心跳通过 io_uring SEND |

**净代码变化：新增 ~60 行，删除 ~300 行（radix tree + cache + IPI），净减少 ~240 行。**

### 9.3 对 agentrt（用户态运行时）的影响

agentrt 在 agent-linux 上运行时：
- 通过 `airy_sys_call(CAP_REQUEST)` 获取 Badge（新增 API）
- 将 Badge 嵌入 IPC 消息头（新增字段）
- 其他行为不变

agentrt 在普通 Linux/macOS/Windows 上运行时：
- 不使用 Badge 机制
- 使用用户态 Cupolas 权限引擎（不变）
- IPC 消息头的 capability_badge 字段为零（接收方不校验）

---

## §10 需求满足性验证

| 需求 ID | 要求 | 重构后 | 状态 |
|---------|------|--------|:---:|
| FR-003 | IPC 吞吐 > 100K msg/s | 250K msg/s（SQPOLL 模式） | ✅ |
| FR-016 | IPC 延迟 < 10μs | < 118ns（fastpath）, < 4.2μs（数据面 E2E） | ✅ |
| FR-021 | 未授权访问 100% 拒绝 | Badge 在投递前校验，inline deny | ✅ |
| NFR-P-002 | IPC 吞吐 > 100K msg/s | 250K msg/s | ✅ |
| NFR-S-001 | capability 安全模型完整性 | Epoch 立即失效，Badge 不可伪造 | ✅ |
| NFR-R-003 | 关键路径形式化验证 | fastpath 简化为 2 条指令，CBMC 有界验证可行 | ✅（1.0.1） |
| 总纲 §10 SSoT | IORING_OP_URING_CMD | 完全采用 | ✅ |
| 总纲 §10 SSoT | 纯 C LSM | Badge 校验作为纯 C LSM 第一层 | ✅ |
| 总纲 §8.3 | 数据面自治三原则 | 完整保留 | ✅ |
| 总纲 §8.4 | IPC 队列冻结 | 完整保留 | ✅ |
| 总纲 §9 | [DSL] 降级 | 完整定义 | ✅ |

---

## §11 实施计划

### Phase 0: Layout C v3 + 文档修正（2 天）
```
□ 30-interfaces/02-ipc-protocol.md: Layout C v3 定义
□ 30-interfaces/02-ipc-protocol.md: IORING_OP_IPC_* → IORING_OP_URING_CMD + cmd_op
□ 30-interfaces/07-ipc-fastpath.md: 状态机 7 态
□ 30-interfaces/07-ipc-fastpath.md: C-S0~C-S11 完整条件
□ 40-dataflows/03-ipc-flow.md: 消除控制面数据流
□ 170-performance/03-ipc-performance.md: SLO 更新
```

### Phase 1: Badge + Epoch 实现（3 天）
```
□ kernel/ipc/airy_epoch.c: Epoch 管理（~30 行）
□ kernel/ipc/airy_badge.c: Badge 编译与验证（~30 行）
□ kernel/include/airymax/ipc.h: Layout C v3 + opcode + flags 更新
□ 30-interfaces/08-sc-error-contract.md: A-UEF IPC 错误码 -41~-52
```

### Phase 2: 消除控制面 IPC（3 天）
```
□ 30-interfaces/01-syscalls.md: syscall 表 12 → 4
□ 20-modules/01-kernel.md: syscall 表更新
□ 20-modules/02-services.md: daemon 通信路径全部走数据面
□ kernel/ipc/airy_uring_cmd.c: 新增 CAP_REQUEST 路由
```

### Phase 3: Capability 模型更新（3 天）
```
□ 110-security/03-capability-model.md: 移除 radix tree + cache，新增 Badge + Epoch
□ 110-security/04-ipc-data-plane-autonomy.md: 离线 Epoch 快照
□ 110-security/05-ipc-control-plane-reconciliation.md: Reconciliation 重定义
□ kernel/ipc/airy_ipc_cap.c: 删除（radix tree + cache）
□ kernel/superv/airy_cap_check.c: 使用 badge_verify
```

### Phase 4: Unify Design 总纲更新（2 天）
```
□ 10-unify-design.md §8: A-IPC 描述更新为 Capability Folding 基石
□ 10-unify-design.md §8.2: Capability 分层校验 → Badge 自验证
□ 10-unify-design.md §8.3: 数据面自治三原则（离线 Epoch 快照）
□ 50-engineering-standards/90-terminology.md: 新增术语
□ 50-engineering-standards/09-ssot-registry.md: A-IPC v2 SSoT
```

### Phase 5: 验证（2 天）
```
□ Epoch bump + 并发通信混沌测试
□ Badge 编译 → 发送 → 校验 → 撤销 → 拒绝 全链路
□ Daemon 崩溃恢复测试
□ [DSL] 降级模式测试
□ Layout C v3 CI 逐字节校验规则更新
□ agentrt 双端 ipc.h 一致性校验
```

**总工期：15 天**

---

## §12 遗留问题与未来工作

| 问题 | 影响 | 0.1.1 处理 | 1.0.1 计划 |
|------|------|-----------|-----------|
| MSG_RING 12 方网格锁争用 | 12 daemon 全网格中 uring_lock 可能成为瓶颈 | 接受，12 daemon 规模下可承受 | 共享 ring 方案或专用 io-wq 池 |
| io-wq 饱和 | MSG_RING punt 可能耗尽 worker | 接受，配置 io-wq 限流 | 独立 io-wq 池 |
| BATCH 部分失败语义 | 当前 BATCH 假设内核可逐条处理 | 发送方预校验 | 原子 BATCH 事务 |
| 全局 Epoch 影响范围 | 撤销一个 Agent 使所有 Agent 重编译 Badge | 接受（< 100 Agent，重编译 < 100μs） | 按类型独立 Epoch |
| 形式化验证 | 无 Isabelle/HOL 证明 | CBMC 有界验证 fastpath | seL4 风格完整证明 |
| 跨节点 IPC | 超节点 OS 的 RDMA/CXL IPC | 不在 0.1.1 范围 | A-IPC 扩展为分布式 IPC |

---

## §13 设计哲学总结

### 13.1 乔布斯/艾夫哲学的工程落地

```
"产品中看不见的部分也应该像其外表一样精美"
  → A-IPC 的内部实现（fastpath）与外部接口（io_uring）同样精美
  → 两条 CPU 指令完成能力校验，无隐藏的 drain/cache/IPI 复杂度

"简单就是美"
  → 1 个 atomic_t 替代 radix tree + per-CPU cache + IPI coherency
  → 1 个 opcode (CAP_REQUEST) 替代 NULL Badge 特例
  → 1 条 atomic_inc 替代四阶段 drain 协议

"对复杂事物的精髓进行深度挖掘和精准提炼"
  → 深度挖掘：13 轮审查发现 A-IPC 的本质问题是双平面分裂
  → 精准提炼：Capability Folding 将能力校验折叠进消息头
  → 去芜存菁：移除 seq_num/negotiated_ver/NULL Badge/drain/cache/IPI

"如果为了达到看不到一颗螺丝的目标，结果却做出一个极为烦琐的产品，反倒违背了初心"
  → 28 号审查发现的 7 颗螺丝全部拧掉
  → 不用 drain 伪装"立即生效"，接受极少数在途消息被拒绝
  → 不用 NULL Badge 伪装"无特例"，用 CAP_REQUEST opcode 显式路由
```

### 13.2 A-IPC 的最终形态

```
通信 = io_uring 数据面（唯一平面）
授权 = 1 个 Badge（嵌入消息头，SHR + AND）
撤销 = 1 条 atomic_inc（无阻塞，无 drain）
自举 = 1 个 CAP_REQUEST opcode（无特殊 Badge）
完整性 = 1 个 CRC32（覆盖 Badge）
管理器 = sec_d（编译 Badge，低频调用）
错误码 = A-UEF IPC 空间（-41~-70）
降级 = [DSL] 最简 128B + 2 opcode
```

**这便是 A-IPC 的最终形态。不是融入，不是修补——是以 Capability Folding 为基石的重新设计。**

---

## §14 相关文档

- [10-unify-design.md](../../../../../docs-linux/10-architecture/10-unify-design.md) — Airymax Unify Design 总纲（SSoT）
- [16~28 号审查报告](./) — 13 轮 IPC 审查的完整链
- [30-interfaces/02-ipc-protocol.md](../../../../../docs-linux/30-interfaces/02-ipc-protocol.md) — IPC 协议（待按本设计更新）
- [30-interfaces/07-ipc-fastpath.md](../../../../../docs-linux/30-interfaces/07-ipc-fastpath.md) — IPC fastpath（待按本设计更新）
- [110-security/03-capability-model.md](../../../../../docs-linux/110-security/03-capability-model.md) — Capability 模型（待按本设计更新）

---

## §15 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0 | 2026-07-18 | 初始版本：基于 16~28 号共 13 份审查报告的最终工程方案；以 Capability Folding 为基石；Layout C v3；syscall 12→4；fastpath 7 态；完整对接 Unify Design 五模块；15 天实施计划 |

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. | A-IPC 全面深化重新设计 | v1.0 | 2026-07-18
