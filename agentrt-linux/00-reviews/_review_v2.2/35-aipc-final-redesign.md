Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 35 — A-IPC 最终重新设计（基于 6 条硬约束）

## "第一块基石的形状必须确定——之后的一切都建立在它之上"

> **文档性质**：基于 34 号科学论证结论（6 条硬约束 H1-H6）的 A-IPC 完整重新设计
> **设计层级**：内核级工程——AirymaxOS 的第一块基石
> **前置约束**：[34-overall-perspective-scientific-judgment.md](file:///home/spharx/SpharxWorks/airymaxhub/docs-closed/agentrt-linux/00-reviews/_review_v2.2/34-overall-perspective-scientific-judgment.md) §6.3 6 条硬约束
> **设计哲学**：乔布斯/艾夫"简约就是美"——"产品中看不见的部分也应该像其外表一样精美"
> **核心论断**：通信 = io_uring 数据面（唯一平面）；授权 = 1 个 Badge；撤销 = 1 条 atomic_inc；自举 = 1 个 CAP_REQUEST opcode；完整性 = 1 个 CRC32；管理器 = sec_d

---

## §0 设计起点与约束边界

### 0.1 6 条硬约束（不可妥协，源自 34 号 §6.3）

```
H1: Layout C v4 总长保持 128 字节，magic 保持 0x41524531 'ARE1'
H2: capability_badge 字段进入 [SC] ipc.h，但校验机制属于 [SS] 层
H3: agentrt 用户态 capability_badge 始终为 0，使用传统 cap_t 引用
H4: agentrt-linux 内核 capability_badge 由 sec_d 编译，fastpath C-S9 校验
H5: 纯 C LSM 模块职责不变（策略/撤销/审计/执法），Badge 校验是其 fastpath 内联
H6: [DSL] 降级模式下 capability_badge 字段存在但被忽略（值=0，跳过校验）
```

### 0.2 设计输入（25-33 号审查的全部产出）

| 来源 | 输入 | 在本设计中的体现 |
|------|------|----------------|
| 25 号 §0 | "IPC 不是承载能力校验——IPC 就是能力校验" | §1 单平面架构 |
| 27 号 §2 | Badge 64-bit Native Word 格式 | §2 Layout C v4 |
| 28 号 §1 | Epoch drain 消除（1 行 atomic_inc） | §3 Epoch 模型 |
| 28 号 §2 | CRC32 覆盖 capability_badge | §2 Layout C v4 |
| 28 号 §3 | NULL Badge → CAP_REQUEST opcode | §4 opcode 设计 |
| 28 号 §4 | 全局 Epoch（1 个 atomic_t） | §3 Epoch 模型 |
| 28 号 §6 | 7 态状态机（保留 SLOW_SEND/SLOW_RECV） | §5 fastpath 状态机 |
| 30 号 §3 | Random Tag 防伪造 + 内核静态数组 | §6 Badge 安全模型 |
| 31 号 §3 | 数据结构隔离（agent_caps[] vs kfifo） | §7 隔离设计 |
| 33 号 §1 | NONBLOCK 模式 + io-wq 接管 | §5 fastpath 实现 |
| 34 号 §6.4 | 错误码空间修正 [-78, -80] | §8 错误码定义 |

### 0.3 设计目标

```
目标 1: 形状确定性（基石三属性之一）
  Layout C v4 + opcode 表 + syscall 表 = 第一块基石的精确形状

目标 2: 不可移动性（基石三属性之二）
  6 条硬约束不可妥协；任何后续设计都必须在此形状之上构建

目标 3: 承重性（基石三属性之三）
  fastpath 100 行代码 + CBMC 全函数验证 = 可承重的工程基础

目标 4: 简约性（乔布斯/艾夫哲学）
  7 颗螺丝全部拧掉后，最终形态见 §0.4

目标 5: 契约一致性（IRON-9 v3 四层模型）
  [SC] 数据结构定义 + [SS] 语义同源 + [IND] 完全独立 + [DSL] 降级生存
```

### 0.4 最终简约形态（28 号 §8.3 + 34 号 §7.1）

```
通信 = io_uring 数据面（唯一平面）
授权 = 1 个 Badge（嵌入消息头 offset 44-51，CPU 位运算校验）
撤销 = 1 条 atomic_inc（无阻塞，无 drain，无 bitmap）
自举 = 1 个 CAP_REQUEST opcode（无特殊 Badge，无硬编码 dst_task）
完整性 = 1 个 CRC32（覆盖 header[0:52) + payload）
管理器 = sec_d（编译 Badge，低频调用，唯一写者）
降级 = capability_badge=0 + 跳过 C-S9（[DSL] 模式生存）
```

---

## §1 单平面架构（H1, H4）

### 1.1 架构总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        A-IPC 单平面架构                                       │
│                                                                              │
│   用户态                         内核态                                       │
│   ┌─────────────────────┐       ┌──────────────────────────────────────┐  │
│   │  Agent A             │       │  io_uring 子系统                       │  │
│   │  ┌───────────────┐   │       │  ┌────────────────────────────────┐ │  │
│   │  │ io_uring SQ   │───┼──────▶│  │ io_uring_cmd()                 │ │  │
│   │  │ IORING_OP_    │   │       │  │   → airy_uring_cmd()           │ │  │
│   │  │ URING_CMD     │   │       │  │     │                           │ │  │
│   │  └───────────────┘   │       │  │     ▼                           │ │  │
│   │         ▲             │       │  │  airy_ipc_validate()  ── 锁内   │ │  │
│   │         │             │       │  │   C-S0~C-S11 (含 C-S9 Badge)   │ │  │
│   │  ┌───────────────┐   │       │  │     │                           │ │  │
│   │  │ io_uring CQE │◀──┼───────│  │     ▼ NONBLOCK + fastpath       │ │  │
│   │  │ res = 0/-Exxx│   │       │  │  airy_ipc_deliver_fast() ── 锁内 │ │  │
│   │  └───────────────┘   │       │  │     或                          │ │  │
│   │                      │       │  │  -EAGAIN → io-wq 接管 ── 锁外   │ │  │
│   └─────────────────────┘       │  │     ↓                           │ │  │
│                                  │  │  airy_ipc_deliver_full()        │ │  │
│                                  │  │   kfifo_in + eventfd_signal     │ │  │
│                                  │  └────────────────────────────────┘ │  │
│                                  │                                       │  │
│                                  │  ┌────────────────────────────────┐ │  │
│                                  │  │  agent_caps[1024]  静态数组     │ │  │
│                                  │  │  (Badge: Epoch + Random Tag +   │ │  │
│                                  │  │   Permissions)                  │ │  │
│                                  │  │  唯一写者: sec_d                 │ │  │
│                                  │  │  读者: fastpath C-S9            │ │  │
│                                  │  └────────────────────────────────┘ │  │
│                                  │                                       │  │
│                                  │  ┌────────────────────────────────┐ │  │
│                                  │  │  airy_global_epoch (atomic_t)   │ │  │
│                                  │  │  全局代际，1 行 atomic_inc 撤销 │ │  │
│                                  │  └────────────────────────────────┘ │  │
│                                  │                                       │  │
│                                  │  ┌────────────────────────────────┐ │  │
│                                  │  │  per-cpu kfifo (SPSC 无锁)      │ │  │
│                                  │  │  kthread 间通信通道              │ │  │
│                                  │  └────────────────────────────────┘ │  │
│                                  └──────────────────────────────────────┘  │
│                                                                              │
│   控制面 syscall（仅 4 个，低频管理操作）:                                     │
│     airy_sys_call        — Capability Invocation（sec_d 编译 Badge）          │
│     airy_sys_rovol_ctl   — MemoryRovol 控制                                  │
│     airy_sys_sched_ctl   — sched_tac 调度策略控制                             │
│     airy_sys_clt_notify  — 客户端事件通知                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 与 25 号 §0.1 双平面架构的对比

```
当前 A-IPC（双平面，25 号 §0.1）:
  控制面 IPC（seL4 风格）              数据面 IPC（io_uring 风格）
  ┌──────────────────────┐          ┌──────────────────────────┐
  │ airy_sys_send        │          │ io_uring SQE/CQE          │
  │ airy_sys_recv        │          │ IORING_OP_URING_CMD       │
  │ airy_sys_call        │          │ kfifo (kthread 间)        │
  │ airy_sys_reply       │          │ MSG_RING (跨 ring)        │
  │ airy_sys_delegate    │          │ eventfd 通知              │
  │ airy_sys_mint        │          │                           │
  │ airy_sys_revoke      │          │                           │
  │ airy_sys_call_batch  │          │                           │
  │ (共 8 IPC + 4 控制)  │          │                           │
  │ 同步阻塞              │          │ 异步非阻塞                │
  │ decode_and_invoke    │          │ cap_check_fast            │
  └──────────────────────┘          └───────────────────────────┘
  → 12 syscall，两套能力校验，互不贯通

本设计（单平面）:
  数据面 IPC（io_uring 风格，唯一平面）
  ┌──────────────────────────────────────────────────────────┐
  │ io_uring SQE/CQE                                          │
  │ IORING_OP_URING_CMD → airy_uring_cmd()                    │
  │   ├─ airy_ipc_validate()  [C-S0~C-S11, 含 C-S9 Badge]    │
  │   ├─ airy_ipc_deliver_fast()  [NONBLOCK, ~158ns]         │
  │   └─ airy_ipc_deliver_full()  [io-wq, wake_up]           │
  │ kfifo (kthread 间)                                        │
  │ eventfd 通知                                              │
  │                                                           │
  │ capability 校验: C-S9 内联（airy_cap_badge_ok）          │
  └──────────────────────────────────────────────────────────┘
  
  控制面 syscall（仅 4 个，低频管理操作）:
    airy_sys_call        — 仅 sec_d 调用，编译 Badge
    airy_sys_rovol_ctl   — MemoryRovol 控制
    airy_sys_sched_ctl   — sched_tac 调度策略
    airy_sys_clt_notify  — 客户端事件通知
  → 4 syscall，无 IPC 数据传递，无独立能力校验路径
```

### 1.3 syscall 12 → 4 的精确映射

| 旧 syscall (12 个) | 处理方式 | 新方案 |
|---|---|---|
| `airy_sys_send` | 移除 → io_uring URING_CMD | `IORING_OP_URING_CMD + cmd_op=SEND` |
| `airy_sys_recv` | 移除 → io_uring CQE | 接收方 poll CQE |
| `airy_sys_call` | 保留 | `airy_sys_call`（仅 sec_d 编译 Badge） |
| `airy_sys_reply` | 移除 → io_uring URING_CMD | `IORING_OP_URING_CMD + cmd_op=SEND`（反向） |
| `airy_sys_delegate` | 移除 → sec_d 重编译 Badge | `airy_sys_call + COMPILE_BADGE` |
| `airy_sys_mint` | 移除 → sec_d 编译 Badge | `airy_sys_call + COMPILE_BADGE` |
| `airy_sys_revoke` | 移除 → sec_d 撤销 + atomic_inc | `airy_sys_call + REVOKE_BADGE` |
| `airy_sys_call_batch` | 移除 → io_uring SQE 链 | 多个 `URING_CMD` SQE |
| `airy_sys_rovol_ctl` | 保留 | `airy_sys_rovol_ctl` |
| `airy_sys_sched_ctl` | 保留 | `airy_sys_sched_ctl` |
| `airy_sys_clt_notify` | 保留 | `airy_sys_clt_notify` |
| `airy_sys_lsm_ctl` | 合并 → `airy_sys_call` | `airy_sys_call + LSM_CTL` |

**保留的 4 个 syscall 注册号**（Linux 512-535 槽位）：
- `airy_sys_call` → 512
- `airy_sys_rovol_ctl` → 513
- `airy_sys_sched_ctl` → 514
- `airy_sys_clt_notify` → 515

### 1.4 控制面/数据面职责划分

```
控制面（4 个 syscall，低频）:
  ┌─────────────────────────────────────────────────────────────┐
  │ 职责: 管理操作，不传递 IPC 数据                              │
  │ 频率: < 100 次/秒（Badge 编译、策略更新）                    │
  │ 模式: 同步阻塞，特权操作                                     │
  │ 校验: 完整 11 阶段 decode_and_invoke（仅 airy_sys_call）     │
  │ 数据: 不接触 kfifo、不接触 io_uring ring                     │
  └─────────────────────────────────────────────────────────────┘

数据面（io_uring，高频）:
  ┌─────────────────────────────────────────────────────────────┐
  │ 职责: IPC 数据传递 + 内联能力校验（C-S9）                    │
  │ 频率: 100K~1M 次/秒                                         │
  │ 模式: 异步非阻塞（SQPOLL）或 DEFER_TASKRUN                   │
  │ 校验: C-S0~C-S11 线性检查链（含 C-S9 Badge）                 │
  │ 数据: kfifo + eventfd + CQE                                  │
  └─────────────────────────────────────────────────────────────┘

关键不变量:
  - 控制面不传递 IPC 数据 → 不存在控制面死锁
  - 数据面不做管理操作 → fastpath 保持纯线性
  - C-S9 在数据面 → 控制面不绕过能力校验（控制面的 airy_sys_call 仍走 11 阶段）
```

---

## §2 Layout C v4（H1, H2, H3, H4）

### 2.1 [SC] ipc.h 完整定义

```c
/* kernel/include/airymax/ipc.h —— [SC] 共享契约层，物理宿主 */
/* IRON-9 v3 [SC] 层：agentrt 与 agentrt-linux 共享数据结构定义 */
/* 校验机制属于 [SS] 语义同源层，不在本头文件中定义 */

#ifndef AIRYMAX_IPC_H
#define AIRYMAX_IPC_H

#include <airymax/types.h>  /* __u32, __u64, __u8 */

#ifdef __cplusplus
extern "C" {
#endif

/* ===== Layout C v4 — 128 字节定长消息头 ===== */
/* magic: 0x41524531 'ARE1' ——一经发布即冻结（120 号 §7.5）*/

#define AIRY_IPC_MAGIC          0x41524531u  /* 'ARE1' */
#define AIRY_IPC_HDR_SIZE       128

/* opcode 定义（§4） */
#define AIRY_IPC_OP_SEND        0x0001
#define AIRY_IPC_OP_RECV        0x0002  /* 仅用于接收方声明的 expected opcode */
#define AIRY_IPC_OP_SEND_BATCH  0x0003
#define AIRY_IPC_OP_CANCEL      0x0004
#define AIRY_IPC_OP_FREEZE      0x0005
#define AIRY_IPC_OP_CAP_REQUEST 0x0010  /* 自举：请求 Badge，无 Badge */
#define AIRY_IPC_OP_CAP_RESPONSE 0x0011 /* sec_d 返回编译好的 Badge */

/* flags 定义 */
#define AIRY_IPC_F_ZEROCOPY     0x0001
#define AIRY_IPC_F_CAP_CARRY    0x0002  /* 携带 Badge（agentrt-linux 内核必置） */
#define AIRY_IPC_F_ENCRYPT      0x0004  /* 保留，0.1.1 不启用 */
#define AIRY_IPC_F_COMPRESS     0x0008  /* 保留，0.1.1 不启用 */
#define AIRY_IPC_F_BATCH_TAIL   0x0010  /* SEND_BATCH 的最后一个 SQE */
#define AIRY_IPC_F_RESERVED     0xFFE0  /* 必须为零 */

/* Layout C v4 消息头（128 字节，packed） */
struct airy_ipc_msg_hdr {
    __u32   magic;              /* offset  0, 'ARE1' 0x41524531 */
    __u16   opcode;             /* offset  4, 见 opcode 定义 */
    __u16   flags;              /* offset  6, 见 flags 定义 */
    __u64   trace_id;           /* offset  8, OpenTelemetry trace ID */
    __u64   timestamp_ns;       /* offset 16, CLOCK_REALTIME 纳秒 */
    __u64   src_task;           /* offset 24, 源 Agent/daemon task_id */
    __u64   dst_task;           /* offset 32, 目标 Agent/daemon task_id */
    __u32   payload_len;        /* offset 40, 负载长度（不含头部） */
    __u64   capability_badge;   /* offset 44, [SS] 语义同源：agentrt-linux 用，agentrt=0 */
    __u32   crc32;              /* offset 52, CRC32 覆盖 header[0:52) + payload */
    __u8    reserved[72];       /* offset 56, 保留，必须为零 */
} __attribute__((packed));

_Static_assert(sizeof(struct airy_ipc_msg_hdr) == AIRY_IPC_HDR_SIZE,
               "airy_ipc_msg_hdr must be exactly 128 bytes");

/* ===== Badge 位布局（仅 [SS] 语义同源，定义在内核实现侧）===== */
/* agentrt 用户态：capability_badge 始终为 0（H3） */
/* agentrt-linux 内核：capability_badge 由 sec_d 编译（H4） */
/* [DSL] 降级模式：capability_badge = 0，跳过 C-S9（H6） */

#define AIRY_BADGE_EPOCH_SHIFT     48
#define AIRY_BADGE_EPOCH_MASK      0xFFFF000000000000ULL
#define AIRY_BADGE_RANDTAG_SHIFT   16
#define AIRY_BADGE_RANDTAG_MASK    0x0000FFFFFFFF0000ULL
#define AIRY_BADGE_PERMS_SHIFT     0
#define AIRY_BADGE_PERMS_MASK      0x000000000000FFFFULL
#define AIRY_BADGE_RESERVED_SHIFT  0  /* 低 16 位 reserved，必须为零 */

/* Badge 提取宏（仅内核侧使用，[SS] 语义同源层） */
#define AIRY_BADGE_EPOCH(b)    (((b) & AIRY_BADGE_EPOCH_MASK)   >> AIRY_BADGE_EPOCH_SHIFT)
#define AIRY_BADGE_RANDTAG(b)  (((b) & AIRY_BADGE_RANDTAG_MASK) >> AIRY_BADGE_RANDTAG_SHIFT)
#define AIRY_BADGE_PERMS(b)    (((b) & AIRY_BADGE_PERMS_MASK)   >> AIRY_BADGE_PERMS_SHIFT)

/* Badge 编译宏（仅 sec_d 使用） */
#define AIRY_BADGE_COMPILE(epoch, randtag, perms) \
    ((((u64)(epoch)   & 0xFFFF) << AIRY_BADGE_EPOCH_SHIFT)   | \
     (((u64)(randtag) & 0xFFFFFFFF) << AIRY_BADGE_RANDTAG_SHIFT) | \
     (((u64)(perms)   & 0xFFFF) << AIRY_BADGE_PERMS_SHIFT))

/* Capability 权限位（低 16 位） */
#define AIRY_CAP_PERM_SEND      0x0001
#define AIRY_CAP_PERM_RECV      0x0002
#define AIRY_CAP_PERM_CALL      0x0004  /* airy_sys_call 权限 */
#define AIRY_CAP_PERM_GRANT     0x0008  /* 派生能力（mint/derive） */
#define AIRY_CAP_PERM_REVOKE    0x0010  /* 撤销能力（仅 sec_d） */
#define AIRY_CAP_PERM_FREEZE    0x0020  /* 冻结 ring */
#define AIRY_CAP_PERM_BATCH     0x0040  /* 批量发送 */
#define AIRY_CAP_PERM_RESERVED  0xFF80  /* 必须为零 */

#ifdef __cplusplus
}
#endif

#endif /* AIRYMAX_IPC_H */
```

### 2.2 字段语义详解

| Offset | 字段 | 大小 | 语义 | 校验位置 |
|--------|------|------|------|---------|
| 0 | magic | 4B | `0x41524531 'ARE1'`，一经发布即冻结 | C-S1 |
| 4 | opcode | 2B | 操作码，见 §4 | C-S2 |
| 6 | flags | 2B | 标志位，见 §4.3 | C-S10 |
| 8 | trace_id | 8B | OpenTelemetry trace ID，全链路追踪 | 不校验（透传） |
| 16 | timestamp_ns | 8B | CLOCK_REALTIME 纳秒，发送方填写 | 不校验（透传） |
| 24 | src_task | 8B | 源 task_id，必须与 Badge 编译时绑定 | C-S9（与 agent_caps[] 对照） |
| 32 | dst_task | 8B | 目标 task_id，决定 kfifo 路由 | C-S5/C-S6（路由） |
| 40 | payload_len | 4B | 负载长度，不含头部 | C-S3/C-S4 |
| 44 | capability_badge | 8B | [SS] 语义同源：agentrt-linux 用，agentrt=0 | C-S9（Badge 校验） |
| 52 | crc32 | 4B | CRC32 覆盖 header[0:52) + payload | C-S12（投递前） |
| 56 | reserved[72] | 72B | 保留，必须为零 | C-S4（reserved 检查） |

### 2.3 [SC] 与 [SS] 的精确边界（H2）

```
[SC] 共享契约层（本头文件）:
  ✓ 数据结构定义: struct airy_ipc_msg_hdr
  ✓ 字段偏移与大小: offset 0-127
  ✓ magic 值: 0x41524531
  ✓ opcode 枚举值: SEND/RECV/SEND_BATCH/CANCEL/FREEZE/CAP_REQUEST/CAP_RESPONSE
  ✓ flags 位定义: ZEROCOPY/CAP_CARRY/ENCRYPT/COMPRESS/BATCH_TAIL
  ✓ Badge 位布局宏: EPOCH_SHIFT/RANDTAG_SHIFT/PERMS_SHIFT
  ✓ Capability 权限位: SEND/RECV/CALL/GRANT/REVOKE/FREEZE/BATCH
  ✓ _Static_assert(sizeof == 128)

[SS] 语义同源层（不在本头文件，在内核实现侧）:
  ✗ Badge 校验机制: airy_cap_badge_ok() 内联函数
  ✗ agent_caps[] 静态数组: 内核内存，用户态不可见
  ✗ airy_global_epoch: atomic_t，内核全局
  ✗ Random Tag 生成: get_random_bytes()
  ✗ C-S9 校验逻辑: READ_ONCE + 位运算 + 比较
  ✗ sec_d Badge 编译流程: airy_sys_call(COMPILE_BADGE)

[IND] 完全独立层:
  - agentrt 用户态: 不使用 capability_badge 字段（始终为 0）
  - agentrt 用户态: 使用传统 cap_t 引用 + airy_ipc_send() 库函数
  - agentrt-linux 内核: 使用 capability_badge + C-S9 内联校验

[DSL] 降级生存层:
  - capability_badge 字段存在但被忽略（值=0）
  - C-S9 跳过（badge == 0 时直接通过）
  - 退化到传统 radix tree 兜底路径（AIRY_ECAP_RADIX_MISS 仍保留）
```

### 2.4 CRC32 覆盖范围（28 号 §2 修复）

```
CRC32 覆盖范围: header[0:52) + payload
  ├─ magic              [0:4)    ✓
  ├─ opcode             [4:6)    ✓
  ├─ flags              [6:8)    ✓
  ├─ trace_id           [8:16)   ✓
  ├─ timestamp_ns       [16:24)  ✓
  ├─ src_task           [24:32)  ✓
  ├─ dst_task           [32:40)  ✓
  ├─ payload_len        [40:44)  ✓
  ├─ capability_badge   [44:52)  ✓  ← 28 号修复：包含 Badge
  ├─ crc32              [52:56)  ✗  ← 不覆盖自身
  └─ reserved[72]       [56:128) ✗  ← 不覆盖（必须为零，无覆盖价值）

CRC32 自身不覆盖自身（循环依赖）。
reserved[72] 必须为零，C-S4 检查其全零，无 CRC32 覆盖价值。
```

---

## §3 Epoch 模型（28 号 §1, §4 修复）

### 3.1 全局 Epoch（1 个 atomic_t）

```c
/* kernel/ipc/airy_cap.c */

#include <linux/atomic.h>
#include <linux/random.h>

/* 全局代际 —— 1 个 atomic_t（28 号 §4 修复） */
static atomic_t airy_global_epoch = ATOMIC_INIT(1);

/* agent_caps[] 静态数组 —— 唯一写者 sec_d，读者 fastpath C-S9 */
struct airy_cap_entry {
    u64     badge;       /* 编译后的 Badge（Epoch + Random Tag + Perms） */
    u32     randtag;     /* Random Tag 副本（用于校验） */
    u16     perms;       /* 权限位副本 */
    u16     reserved;
};
static struct airy_cap_entry agent_caps[1024] __cacheline_aligned;
/* 1024 entries × 16 bytes = 16KB，在 L1 cache 中（32KB） */

/* 获取当前全局 Epoch */
static inline u16 airy_cap_epoch_get(void)
{
    return (u16)atomic_read(&airy_global_epoch);
}

/* 撤销：1 行 atomic_inc，无 drain，无 bitmap，无 mdelay（28 号 §1 修复） */
void airy_cap_epoch_increment(void)
{
    atomic_inc(&airy_global_epoch);
    /* 完成。Epoch 递增立即全局可见（x86 lock incl）。 */
    /* 在途消息（持有旧 Epoch 的 Badge）会被 C-S9 拒绝。 */
    /* 发送方收到 -AIRY_ECAP_EPOCH，重新向 sec_d 请求 Badge。 */
    /* 如果权限已被撤销，sec_d 返回 DENY。 */
}
```

### 3.2 Epoch 语义精确化

```
Epoch 的语义: "Badge 生成时的全局代际快照"

不是: "持续有效的权限许可证"
而是: "生成时的权限快照 + 当前全局代际的对照"

校验逻辑（C-S9）:
  badge_epoch  = AIRY_BADGE_EPOCH(badge)       ← Badge 携带的 Epoch
  global_epoch = airy_cap_epoch_get()          ← 当前全局 Epoch
  
  if (badge_epoch != global_epoch)
      return -AIRY_ECAP_EPOCH;  /* 已撤销或过期 */
  
  /* Epoch 匹配后，校验 Random Tag 和权限 */
  ...

撤销语义:
  - 旧 Badge（Epoch=N）的所有在途消息会被 C-S9 拒绝
  - 这是"撤销立即生效"的精确语义
  - 不是"立即阻止所有消息"，而是"不再有新的未授权消息被投递"
  - 在途消息的发送方会收到 -AIRY_ECAP_EPOCH，可以重试或处理失败

为什么不需要 drain:
  - Badge 语义是"生成时的权限快照"，不是"持续有效的许可证"
  - 发送方总是应该准备处理 -AIRY_ECAP_EPOCH（类似网络丢包）
  - drain 试图保证"发送方不会遇到意外的 REJECT"——但 REJECT 是正常的
  - drain 是一个 5ms 的尽力而为启发式，不是精确机制
```

### 3.3 Epoch 溢出处理

```
Epoch 类型: u16（16 位）
溢出阈值: 65536 次撤销
溢出处理:
  - 撤销是低频操作（< 1 次/分钟）
  - 65536 次撤销 ≈ 1092 小时（45 天）连续撤销
  - 0.1.1 阶段不会触及溢出
  - 1.0.1 如需更长寿命，可扩展为 u32（Badge 中 Epoch 占 32 位，Random Tag 占 16 位）

当前设计（u16 Epoch + u32 Random Tag + u16 Perms）是 0.1.1 的正确选择:
  - Epoch 溢出风险可忽略
  - Random Tag 32 位提供 2^32 = 42 亿种可能，防伪造足够
  - Perms 16 位提供 16 种权限位，扩展空间充足
```

---

## §4 opcode 设计（28 号 §3 修复）

### 4.1 opcode 完整定义

| opcode | 值 | 名称 | 用途 | 是否需要 Badge |
|--------|---|------|------|:---:|
| SEND | 0x0001 | 发送消息 | 单条 IPC 消息发送 | ✓（除非 CAP_REQUEST） |
| RECV | 0x0002 | 接收声明 | 接收方声明 expected opcode（用于 CQE 匹配） | ✓ |
| SEND_BATCH | 0x0003 | 批量发送 | 多条消息原子提交（SQE 链） | ✓ |
| CANCEL | 0x0004 | 取消发送 | 取消未完成的 SQE | ✓ |
| FREEZE | 0x0005 | 冻结 ring | ring->frozen = true，拒绝新消息 | ✓（需要 FREEZE 权限） |
| CAP_REQUEST | 0x0010 | 能力请求 | Agent 向 sec_d 请求 Badge（自举） | ✗（无 Badge） |
| CAP_RESPONSE | 0x0011 | 能力响应 | sec_d 返回编译好的 Badge | ✓（sec_d 的 Badge） |

### 4.2 CAP_REQUEST 自举机制（28 号 §3 修复，消除 NULL Badge 硬编码）

```
自举流程:
  Agent A 启动 → 无 Badge → 需要向 sec_d 请求
  
  Step 1: Agent A 填写消息头
    magic = 0x41524531
    opcode = AIRY_IPC_OP_CAP_REQUEST  (0x0010)
    flags = 0
    src_task = A.task_id
    dst_task = sec_d.task_id  (内核启动时全局常量)
    capability_badge = 0  (无 Badge)
    payload = [请求的权限位 + 请求的 dst_task 列表]
  
  Step 2: Agent A 提交 io_uring SQE
    IORING_OP_URING_CMD + cmd_op = AIRY_IPC_OP_CAP_REQUEST
  
  Step 3: 内核 fastpath
    C-S0~C-S8: 常规校验
    C-S9: 检测 opcode == CAP_REQUEST → 跳过 Badge 校验（不是硬编码 dst_task）
         内核路由到 sec_d 的 kfifo（基于 dst_task == sec_d.task_id）
    C-S10~C-S11: 常规校验
  
  Step 4: sec_d 收到 CAP_REQUEST
    - 验证 Agent A 的身份（基于 task_id + cgroup + namespace）
    - 检查 Agent A 请求的权限是否在策略允许范围内
    - 编译 Badge: airy_cap_badge_compile(epoch, randtag, perms)
    - 写入 agent_caps[A.task_id]
    - 返回 CAP_RESPONSE，payload = 编译后的 Badge
  
  Step 5: Agent A 收到 CAP_RESPONSE
    - 提取 Badge，存入本地
    - 后续 IPC 消息携带此 Badge

关键设计点:
  - CAP_REQUEST 不需要 Badge（消除 NULL Badge 硬编码特例）
  - 内核路由基于 opcode == CAP_REQUEST，不是基于 dst_task == sec_d
  - sec_d 是公开的服务端点，任何 Agent 都可以发起 CAP_REQUEST
  - sec_d 仍然有完整的策略控制（可以拒绝请求）
```

### 4.3 flags 设计

```
flags 位定义（16 位）:

  bit 0: ZEROCOPY     — 启用零拷贝（registered buffer）
  bit 1: CAP_CARRY    — 携带 Badge（agentrt-linux 内核必置）
  bit 2: ENCRYPT      — 加密（保留，0.1.1 不启用）
  bit 3: COMPRESS     — 压缩（保留，0.1.1 不启用）
  bit 4: BATCH_TAIL   — SEND_BATCH 的最后一个 SQE
  bit 5-15: RESERVED  — 必须为零

CAP_CARRY 标志的作用:
  - agentrt-linux 内核: 始终置位（capability_badge 字段有效）
  - agentrt 用户态: 始终不置位（capability_badge = 0）
  - [DSL] 降级模式: 不置位（跳过 C-S9）
  - C-S10 检查: 如果 CAP_CARRY 置位但 capability_badge == 0 且 opcode != CAP_REQUEST → 拒绝
```

---

## §5 fastpath 状态机与实现（28 号 §6, 33 号 §1 修复）

### 5.1 7 态状态机（28 号 §6 修复）

```
状态机:

  IDLE ──▶ CHECK ──┬─▶ FAST_SEND ──▶ IDLE     (发送完成，~158ns)
                  │
                  ├─▶ SLOW_SEND ──▶ IDLE     (异步发送，io-wq)
                  │
                  ├─▶ FAST_RECV ──▶ IDLE     (接收完成)
                  │
                  ├─▶ SLOW_RECV ──▶ IDLE     (异步接收，等 CQE)
                  │
                  ├─▶ BATCH     ──▶ IDLE     (批量)
                  │
                  ├─▶ CANCEL                 (取消)
                  │
                  └─▶ ERROR                  (错误)

状态语义:
  IDLE:      空闲，等待 SQE
  CHECK:     执行 C-S0~C-S11 校验链
  FAST_SEND: NONBLOCK 模式 + 同 CPU + kfifo 有空位 → 锁内投递
  SLOW_SEND: 跨 CPU 或 kfifo 满 → io-wq 接管
  FAST_RECV: 接收方 poll CQE 立即获得
  SLOW_RECV: 接收方阻塞等待 CQE
  BATCH:     SEND_BATCH 链式处理
  CANCEL:    取消未完成 SQE
  ERROR:     错误处理，返回 -Exxx via CQE

SLOW_SEND 与 SLOW_RECV 的区别（28 号 §6 修复）:
  SLOW_SEND: 提交 SQE 后立即返回 IDLE（异步发送）
  SLOW_RECV: 等待 CQE 才返回 IDLE（阻塞接收）
  两者不能合并为 SLOW_PATH，否则状态转换不明确
```

### 5.2 fastpath 完整实现（33 号 NONBLOCK 修复）

```c
/* kernel/ipc/airy_uring_cmd.c */

#include <linux/io_uring.h>
#include <linux/io_uring_types.h>
#include <linux/kfifo.h>
#include <linux/random.h>
#include <linux/preempt.h>
#include <linux/atomic.h>
#include <airymax/ipc.h>
#include <airymax/error.h>
#include "airy_internal.h"

/**
 * airy_uring_cmd - A-IPC fastpath 入口
 * 
 * 调用上下文: io_uring 持有 ctx->uring_lock
 * 锁内时间: NONBLOCK fastpath ~158ns，校验失败 ~68ns
 * 
 * 设计原则:
 *   1. 锁内仅做校验 + 快速投递（无 wake_up）
 *   2. 需要唤醒时返回 -EAGAIN，io-wq 接管（锁外）
 *   3. C-S9 Badge 校验是纯读取，零副作用（OS-KER-225）
 */
static int airy_uring_cmd(struct io_uring_cmd *ioucmd, unsigned int issue_flags)
{
    struct airy_ipc_cmd *cmd = (struct airy_ipc_cmd *)ioucmd->cmd;
    int ret;

    /* Phase 1: 完整校验链 C-S0~C-S11（锁内，~68ns） */
    ret = airy_ipc_validate(cmd);
    if (ret < 0)
        return ret;  /* 立即失败，不持有额外锁时间 */

    /* Phase 2: 数据投递 —— NONBLOCK 快慢路径分离（33 号 §1 修复） */
    if (issue_flags & IO_URING_F_NONBLOCK) {
        /*
         * NONBLOCK 模式（io_uring 持有 uring_lock 时传入）:
         * - 同 CPU + kfifo 有空位 + 接收方轮询 → FAST_SEND（锁内 ~90ns）
         * - 否则返回 -EAGAIN → io_uring 自动排队到 io-wq
         */
        if (airy_ipc_can_fast_deliver(cmd)) {
            ret = airy_ipc_deliver_fast(cmd);
            if (ret >= 0)
                return ret;  /* FAST_SEND 完成，~158ns 端到端 */
        }
        return -EAGAIN;  /* 需要 io-wq 接管 */
    }

    /*
     * 非 NONBLOCK 模式（已在 io-wq 线程中，不持有 uring_lock）:
     * - 可以安全执行 wake_up（eventfd_signal）
     * - 可以安全执行跨 CPU kfifo
     */
    return airy_ipc_deliver_full(cmd);
}

/**
 * airy_ipc_validate - C-S0~C-S11 校验链
 * 
 * 锁内执行，~68ns，纯校验，零副作用。
 * 所有检查遵循 check-and-return 模式，前面失败不影响后面。
 */
static int airy_ipc_validate(struct airy_ipc_cmd *cmd)
{
    struct airy_ipc_msg_hdr *hdr = cmd->hdr;
    u64 badge;
    u16 badge_epoch, global_epoch;
    u32 badge_randtag, agent_randtag;
    u16 badge_perms, agent_perms;

    /* C-S0: ring 冻结检查 */
    if (unlikely(cmd->ring->frozen))
        return -AIRY_ECAP_FROZEN;

    /* C-S1: magic 检查 */
    if (unlikely(hdr->magic != AIRY_IPC_MAGIC))
        return -AIRY_EIPC_MAGIC;

    /* C-S2: opcode 合法性检查 */
    if (unlikely(!airy_ipc_opcode_valid(hdr->opcode)))
        return -AIRY_EIPC_OPCODE;

    /* C-S3: payload_len 合法性检查 */
    if (unlikely(hdr->payload_len > AIRY_IPC_MAX_PAYLOAD))
        return -AIRY_EIPC_PAYLOAD;

    /* C-S4: 头部大小 + reserved 全零检查 */
    if (unlikely(cmd->hdr_size != AIRY_IPC_HDR_SIZE))
        return -AIRY_EIPC_HDRSIZE;
    if (unlikely(!airy_ipc_reserved_zero(hdr->reserved, 72)))
        return -AIRY_EIPC_RESERVED;

    /* C-S5: CPU 匹配检查（优化条件，不是正确性条件） */
    cmd->same_cpu = (smp_processor_id() == cmd->dst_cpu);

    /* C-S6: kfifo 满检查（仅在 NONBLOCK 模式下需要） */
    /* 实际检查在 airy_ipc_can_fast_deliver() 中 */

    /* C-S7: reclaim flag 检查 */
    if (unlikely(cmd->reclaim))
        return -AIRY_EIPC_RECLAIM;

    /* C-S8: 上下文检查（in_task()） */
    if (unlikely(!in_task()))
        return -AIRY_EIPC_CONTEXT;

    /* C-S9: Capability Folding Badge 校验（关键步骤） */
    /* H2: 校验机制属于 [SS] 语义同源层 */
    /* H4: agentrt-linux 内核 capability_badge 由 sec_d 编译 */
    /* H6: [DSL] 降级模式 capability_badge=0，跳过校验 */
    
    if (unlikely(hdr->opcode == AIRY_IPC_OP_CAP_REQUEST)) {
        /* CAP_REQUEST 自举：无 Badge，内核路由到 sec_d */
        if (unlikely(hdr->dst_task != AIRY_SEC_D_TASK_ID))
            return -AIRY_ECAP_BADGE;  /* CAP_REQUEST 只能发给 sec_d */
        goto cap_request_pass;
    }

    badge = hdr->capability_badge;
    
    /* [DSL] 降级模式：badge == 0 跳过校验（H6） */
    if (badge == 0) {
        if (hdr->flags & AIRY_IPC_F_CAP_CARRY) {
            /* agentrt-linux 内核模式不应出现 badge=0 + CAP_CARRY */
            return -AIRY_ECAP_BADGE;
        }
        /* agentrt 用户态或 [DSL] 模式：badge=0，跳过 */
        goto cap_pass;
    }

    /* Badge 校验：3 个 READ_ONCE + 位运算 + 比较（~10ns） */
    badge_epoch   = AIRY_BADGE_EPOCH(badge);
    badge_randtag = AIRY_BADGE_RANDTAG(badge);
    badge_perms   = AIRY_BADGE_PERMS(badge);
    
    global_epoch  = airy_cap_epoch_get();
    if (unlikely(badge_epoch != global_epoch))
        return -AIRY_ECAP_EPOCH;  /* Epoch 不匹配，已撤销或过期 */
    
    /* agent_caps[] 是内核静态数组，用户态不可写（30 号 §3 修复） */
    agent_randtag = READ_ONCE(agent_caps[hdr->src_task].randtag);
    agent_perms   = READ_ONCE(agent_caps[hdr->src_task].perms);
    
    if (unlikely(badge_randtag != agent_randtag)) {
        /* Random Tag 不匹配 → 伪造尝试，触发 Fault */
        airy_security_fault(hdr->src_task, AIRY_FAULT_CAP_FORGED);
        return -AIRY_ECAP_FORGED;
    }
    
    /* 权限检查：badge_perms 必须包含 opcode 所需权限 */
    if (unlikely(!airy_cap_has_perm(badge_perms, hdr->opcode)))
        return -AIRY_ECAP_PERM;

cap_request_pass:
cap_pass:

    /* C-S10: flags 检查 */
    if (unlikely(hdr->flags & AIRY_IPC_F_RESERVED))
        return -AIRY_EIPC_FLAGS;
    if (unlikely((hdr->flags & AIRY_IPC_F_ENCRYPT) ||
                 (hdr->flags & AIRY_IPC_F_COMPRESS)))
        return -AIRY_EIPC_NOTSUPP;  /* 0.1.1 不支持 */

    /* C-S11: preempt_disable 准备（实际在 deliver 中执行） */
    return 0;
}

/**
 * airy_ipc_can_fast_deliver - 判断是否可以走 FAST_SEND
 * 
 * 条件: 同 CPU + kfifo 有空位 + 接收方轮询模式
 */
static inline bool airy_ipc_can_fast_deliver(struct airy_ipc_cmd *cmd)
{
    if (!cmd->same_cpu)
        return false;  /* C-S5 失败，走 SLOW_SEND */
    
    if (kfifo_avail(&cmd->dst_kfifo) < (AIRY_IPC_HDR_SIZE + cmd->hdr->payload_len))
        return false;  /* C-S6 失败，走 SLOW_SEND */
    
    if (!cmd->dst_polling)
        return false;  /* 接收方非轮询模式，需要 wake_up */
    
    return true;  /* FAST_SEND */
}

/**
 * airy_ipc_deliver_fast - FAST_SEND 路径
 * 
 * 锁内执行，~90ns，无 wake_up。
 * kfifo_in + cqe_fill，preempt_disable 保护。
 */
static int airy_ipc_deliver_fast(struct airy_ipc_cmd *cmd)
{
    struct airy_ipc_msg_hdr *hdr = cmd->hdr;
    size_t total = AIRY_IPC_HDR_SIZE + hdr->payload_len;
    int ret;

    /* C-S11: preempt_disable（保护 kfifo 操作） */
    preempt_disable();
    
    /* CRC32 校验（C-S12，在投递前） */
    if (unlikely(!airy_ipc_crc32_ok(hdr, total))) {
        preempt_enable();
        return -AIRY_EIPC_CRC32;
    }
    
    /* kfifo 入队（SPSC 无锁，per-cpu） */
    ret = kfifo_in(&cmd->dst_kfifo, hdr, total);
    if (unlikely(ret != total)) {
        preempt_enable();
        return -AIRY_EIPC_KFIFO;  /* 不应发生，can_fast_deliver 已检查 */
    }
    
    preempt_enable();
    
    /* CQE 填充（无 wake_up，接收方轮询消费） */
    io_uring_cmd_done(cmd->ioucmd, 0, 0);
    return 0;
}

/**
 * airy_ipc_deliver_full - SLOW_SEND 路径
 * 
 * io-wq 线程中执行，不持有 uring_lock。
 * 可以安全执行跨 CPU kfifo + eventfd_signal(wake_up)。
 */
static int airy_ipc_deliver_full(struct airy_ipc_cmd *cmd)
{
    struct airy_ipc_msg_hdr *hdr = cmd->hdr;
    size_t total = AIRY_IPC_HDR_SIZE + hdr->payload_len;
    int ret;

    /* CRC32 校验 */
    if (unlikely(!airy_ipc_crc32_ok(hdr, total)))
        return -AIRY_EIPC_CRC32;
    
    /* 跨 CPU kfifo 入队（需要锁保护，但不是 uring_lock） */
    spin_lock(&cmd->dst_kfifo_lock);
    ret = kfifo_in(&cmd->dst_kfifo, hdr, total);
    spin_unlock(&cmd->dst_kfifo_lock);
    
    if (unlikely(ret != total))
        return -AIRY_EIPC_KFIFO;
    
    /* 唤醒接收方（可能 1-5μs，在 io-wq 中，不持有 uring_lock） */
    if (!cmd->dst_polling)
        eventfd_signal(cmd->dst_eventfd_ctx, 1);
    
    /* CQE 填充 */
    io_uring_cmd_done(cmd->ioucmd, 0, 0);
    return 0;
}
```

### 5.3 fastpath 延迟分解

```
FAST_SEND 路径（SQPOLL + 同 CPU + kfifo 有空位 + 接收方轮询）:
  airy_ipc_validate():     ~68ns (锁内)
    C-S0~C-S8:             ~20ns
    C-S9 Badge 校验:        ~10ns (3 READ_ONCE + 位运算 + 比较)
    C-S10~C-S11:            ~5ns
  airy_ipc_deliver_fast(): ~90ns (锁内)
    CRC32:                  ~15ns
    kfifo_in:               ~50ns
    cqe_fill:               ~20ns
    preempt_disable/enable: ~5ns
  ────────────────────────────────────
  锁内总计:                  ~158ns
  端到端:                    ~158ns（接收方轮询消费）

SLOW_SEND 路径（跨 CPU 或 kfifo 满或接收方阻塞）:
  airy_ipc_validate():     ~68ns (锁内)
  返回 -EAGAIN              → 释放 uring_lock
  io-wq 调度:               ~500ns
  airy_ipc_deliver_full():  ~100ns + wake_up(~1-5μs) (锁外)
  ────────────────────────────────────
  端到端:                    ~600ns ~5.5μs

校验失败路径:
  airy_ipc_validate():     ~68ns (锁内)
  返回 -Exxx                → 立即失败
  ────────────────────────────────────
  端到端:                    ~68ns
```

### 5.4 性能 SLO（与 170-performance/03-ipc-performance.md 对齐）

```
128B 消息 P50 延迟:
  FAST_SEND: ~158ns
  SLOW_SEND: ~600ns
  目标: ≤ 5μs（170 号 §3 SLO）✓

128B 消息 P99 延迟:
  FAST_SEND + 偶发 SLOW_SEND: ~5.5μs
  目标: ≤ 20μs（170 号 §3 SLO）✓

128B 消息吞吐:
  FAST_SEND 单核: 1/158ns ≈ 6.3M msg/s
  目标: ≥ 1M msg/s（170 号 §3 SLO）✓
```

---

## §6 Badge 安全模型（30 号 §3 修复）

### 6.1 Badge 64-bit Native Word 格式

```
63                    48 47                16 15            0
┌──────────────────────┬─────────────────────┬──────────────┐
│   Epoch (16 bits)    │  Random Tag (32 bits)│ Perms (16 bits)│
└──────────────────────┴─────────────────────┴──────────────┘

Epoch (16 bits):
  - 全局代际，1 个 atomic_t
  - 撤销时 atomic_inc，立即失效所有旧 Badge
  - u16 范围: 65536 次撤销，0.1.1 阶段足够

Random Tag (32 bits):
  - 每个 Agent 唯一的随机标签
  - sec_d 编译 Badge 时使用 get_random_bytes() 生成
  - 存储在内核 agent_caps[] 静态数组中
  - 用户态不可见、不可写
  - 2^32 = 42 亿种可能，暴力枚举不可行

Perms (16 bits):
  - 权限位图
  - SEND/RECV/CALL/GRANT/REVOKE/FREEZE/BATCH
  - 见 §2.1 AIRY_CAP_PERM_* 定义
```

### 6.2 Badge 编译流程（仅 sec_d）

```c
/* kernel/security/airy_cap.c */

/**
 * airy_cap_badge_compile - sec_d 编译 Badge
 * @task_id: 目标 Agent 的 task_id
 * @perms: 请求的权限位
 *
 * 调用上下文: airy_sys_call(COMPILE_BADGE)，仅 sec_d 可调用
 * 返回值: 编译后的 64-bit Badge
 */
u64 airy_cap_badge_compile(u64 task_id, u16 perms)
{
    u16 epoch = airy_cap_epoch_get();
    u32 randtag;
    u64 badge;
    
    /* 生成 32-bit 随机标签 */
    get_random_bytes(&randtag, sizeof(randtag));
    
    /* 编译 Badge */
    badge = AIRY_BADGE_COMPILE(epoch, randtag, perms);
    
    /* 写入内核静态数组（唯一写者 sec_d） */
    WRITE_ONCE(agent_caps[task_id].badge, badge);
    WRITE_ONCE(agent_caps[task_id].randtag, randtag);
    WRITE_ONCE(agent_caps[task_id].perms, perms);
    
    return badge;
}

/**
 * airy_cap_badge_revoke - sec_d 撤销 Badge
 * @task_id: 目标 Agent 的 task_id
 *
 * 撤销语义: atomic_inc 全局 Epoch，所有旧 Badge 立即失效
 * 不需要 drain，不需要 bitmap，不需要 mdelay（28 号 §1 修复）
 */
void airy_cap_badge_revoke(u64 task_id)
{
    /* 清除 agent_caps[] 条目（可选，C-S9 会因 Epoch 不匹配而拒绝） */
    WRITE_ONCE(agent_caps[task_id].badge, 0);
    WRITE_ONCE(agent_caps[task_id].randtag, 0);
    WRITE_ONCE(agent_caps[task_id].perms, 0);
    
    /* 全局 Epoch +1，立即生效 */
    atomic_inc(&airy_global_epoch);
}
```

### 6.3 Badge 校验流程（C-S9 内联）

```c
/* kernel/ipc/airy_uring_cmd.c —— C-S9 内联实现 */

/**
 * airy_cap_badge_ok - C-S9 Badge 校验（内联，~10ns）
 * @src_task: 发送方 task_id
 * @badge: 消息头中的 capability_badge
 * @opcode: 消息 opcode（用于权限检查）
 *
 * 返回值: 0 通过，<0 错误码
 * 
 * 安全属性:
 *   - 3 个 READ_ONCE（无锁，无 RCU，无 kmalloc）
 *   - 用户态可控输入仅 badge 字段
 *   - agent_caps[] 在内核内存，用户态不可写
 *   - Random Tag 防伪造（30 号 §3 修复）
 */
static inline int airy_cap_badge_ok(u64 src_task, u64 badge, u16 opcode)
{
    u16 badge_epoch, global_epoch;
    u32 badge_randtag, agent_randtag;
    u16 badge_perms, agent_perms;
    
    /* 提取 Badge 字段（纯位运算） */
    badge_epoch   = AIRY_BADGE_EPOCH(badge);
    badge_randtag = AIRY_BADGE_RANDTAG(badge);
    badge_perms   = AIRY_BADGE_PERMS(badge);
    
    /* Epoch 校验（1 次 atomic_read） */
    global_epoch = airy_cap_epoch_get();
    if (unlikely(badge_epoch != global_epoch))
        return -AIRY_ECAP_EPOCH;  /* 已撤销或过期 */
    
    /* Random Tag 校验（1 次 READ_ONCE） */
    agent_randtag = READ_ONCE(agent_caps[src_task].randtag);
    if (unlikely(badge_randtag != agent_randtag)) {
        /* 伪造尝试，触发 Fault */
        return -AIRY_ECAP_FORGED;
    }
    
    /* 权限校验（1 次 READ_ONCE + 位运算） */
    agent_perms = READ_ONCE(agent_caps[src_task].perms);
    if (unlikely(!airy_cap_has_perm(badge_perms & agent_perms, opcode)))
        return -AIRY_ECAP_PERM;
    
    return 0;  /* 通过 */
}
```

### 6.4 防伪造分析

```
攻击模型: 恶意 Agent 试图伪造 Badge

攻击向量 1: 猜测 Random Tag
  - Random Tag: 32 bits = 2^32 = 42 亿种可能
  - 每次猜测: 1 次 IPC 提交 ~158ns
  - 暴力枚举时间: 2^32 × 158ns ≈ 679 秒 ≈ 11 分钟
  - 但每次失败都会触发 -AIRY_ECAP_FORGED，sec_d 记录审计日志
  - 100 次失败即可触发警报，攻击者实际无法完成枚举
  - 结论: 不可行

攻击向量 2: 窃取其他 Agent 的 Badge
  - Badge 存储在 Agent 的用户态内存中
  - 但 agent_caps[] 中的 Random Tag 是 per-Agent 的
  - Agent A 偷取 Agent B 的 Badge，提交时:
    - badge_epoch 匹配（全局 Epoch）
    - badge_randtag 匹配（B 的 Random Tag）
    - 但 C-S9 中 agent_caps[A.task_id].randtag != badge_randtag
    - → 返回 -AIRY_ECAP_FORGED
  - 结论: 不可行（Random Tag 绑定 task_id）

攻击向量 3: 修改 agent_caps[] 数组
  - agent_caps[] 在内核静态数组，用户态不可写
  - 需要 kernel exploit 才能修改
  - 一旦有 kernel exploit，任何安全机制都无效
  - 结论: 超出威胁模型

攻击向量 4: 时序侧信道
  - C-S9 执行时间差异: ~3ns（epoch mismatch vs full pass）
  - 理论上可推断 Badge 校验的哪一步失败
  - 但这只能推断"我的 Badge 是不是有效的"，不能伪造 Badge
  - seL4 也存在类似时序差异（CNode 深度不同）
  - 结论: 可接受（31 号 §2.2 论证）
```

---

## §7 隔离设计（31 号 §3 论证）

### 7.1 数据结构隔离

```
三个独立的内存区域:

  1. agent_caps[1024]  ── 能力数据（内核静态数组，16KB）
     ├─ 唯一写者: sec_d（通过 airy_sys_call）
     ├─ 读者: fastpath C-S9
     └─ 不会被 kfifo 操作修改

  2. kfifo              ── 数据投递缓冲区（per-cpu SPSC）
     ├─ 写者: fastpath kfifo_in
     ├─ 读者: 接收方 io_uring CQE 处理
     └─ 不会被 capability 校验修改

  3. io_uring ring      ── 通信原语
     ├─ 写者: 发送方 SQE
     ├─ 读者: 接收方 CQE
     └─ 独立于 agent_caps 和 kfifo

更新路径隔离:
  - agent_caps 单写者（sec_d）/ 多读者（fastpath）→ 无锁，READ_ONCE/WRITE_ONCE
  - kfifo SPSC 无锁模型 → 无锁
  - io_uring ring → uring_lock（仅 io_uring 框架使用）

失败域隔离:
  - C-S9 失败 → 返回 -Exxx → 消息不投递（能力失败）
  - kfifo_in 失败 → 返回 -Exxx → 能力已通过但消息未投递（数据失败）
  - 两者独立，能力失败不影响数据完整性，数据失败不影响能力正确性
```

### 7.2 代码组织隔离

```c
/* fastpath 函数的代码组织约定（31 号 §3.3 "能力门"方案） */

static int airy_uring_cmd(struct io_uring_cmd *ioucmd, unsigned int issue_flags)
{
    /* ─── 能力门（Capability Gate）─── */
    /* C-S0~C-S11 校验，含 C-S9 Badge 校验 */
    /* 之后的代码保证不与 agent_caps[] 交互 */
    int ret = airy_ipc_validate(cmd);
    if (ret < 0) return ret;
    
    /* ─── 数据门（Data Gate）─── */
    /* 之后的代码保证不与 capability 数据交互 */
    /* 仅与 kfifo、eventfd、CQE 交互 */
    if (issue_flags & IO_URING_F_NONBLOCK) {
        if (airy_ipc_can_fast_deliver(cmd))
            return airy_ipc_deliver_fast(cmd);
        return -EAGAIN;
    }
    return airy_ipc_deliver_full(cmd);
}

/* 0.1.1 阶段: 代码组织约定（无强制隔离边界） */
/* 1.0.1 阶段: 可引入静态分析规则强制检查（如 Coverity 规则） */
```

### 7.3 CBMC 全函数验证

```
验证目标: airy_uring_cmd() 全函数（~100 行）

验证属性:
  1. C-S9 不可被绕过
     - 任何执行路径都必须经过 C-S9 或 CAP_REQUEST 分支
     - CBMC 验证: 所有路径都包含 airy_cap_badge_ok() 调用
  
  2. agent_caps[] 与 kfifo 独立
     - kfifo_in 不修改 agent_caps[]
     - C-S9 不修改 kfifo
     - CBMC 验证: 内存区域不重叠
  
  3. check-and-return 模式
     - C-S0~C-S11 失败时立即返回，不执行后续操作
     - CBMC 验证: 每个 C-Sx 失败分支不修改全局状态
  
  4. 锁内无阻塞操作
     - 锁内不调用 eventfd_signal(wake_up)
     - 锁内不调用 kmalloc(GFP_KERNEL)
     - CBMC 验证: NONBLOCK 路径无阻塞调用

验证工具链:
  - CBMC 6.0+ （C 程序有界模型检查）
  - goto-cc （编译为 GOTO 程序）
  - 验证脚本: scripts/cbmc-verify-airy_uring_cmd.sh
```

---

## §8 错误码定义（34 号 §6.4 修正）

### 8.1 [SC] error.h Capability 码空间 [-71, -100]

```c
/* kernel/include/airymax/error.h —— [SC] 共享契约层 */
/* IRON-9 v3 [SC] 层：agentrt 与 agentrt-linux 共享错误码定义 */

#ifndef AIRYMAX_ERROR_H
#define AIRYMAX_ERROR_H

/* ===== POSIX 码空间 [-1, -40] ===== */
#define AIRY_EPERM             (-1)
#define AIRY_ENOENT            (-2)
/* ... 38 个 POSIX 错误码 ... */
#define AIRY_ECFGVERSION       (-40)

/* ===== IPC 码空间 [-41, -70] ===== */
#define AIRY_EIPC_MAGIC        (-41)
#define AIRY_EIPC_OPCODE       (-42)
#define AIRY_EIPC_PAYLOAD      (-43)
#define AIRY_EIPC_HDRSIZE      (-44)
#define AIRY_EIPC_RESERVED     (-45)
#define AIRY_EIPC_FLAGS        (-46)
#define AIRY_EIPC_NOTSUPP      (-47)
#define AIRY_EIPC_KFIFO        (-48)
#define AIRY_EIPC_RECLAIM      (-49)
#define AIRY_EIPC_CONTEXT      (-50)
#define AIRY_EIPC_CRC32        (-51)
#define AIRY_EIPC_TIMEOUT      (-52)
/* [-53, -70] 预留 */

/* ===== Capability 码空间 [-71, -100] ===== */
#define AIRY_ECAP_MISSING      (-71)  /* Capability 缺失 */
#define AIRY_ECAP_REVOKED      (-72)  /* Capability 已撤销 */
#define AIRY_ECAP_EXPIRED      (-73)  /* Capability 已过期 */
#define AIRY_ECAP_MISMATCH     (-74)  /* Capability 不匹配 */
#define AIRY_ECAP_LSM_DENIED   (-75)  /* 纯 C LSM 拒绝 */
#define AIRY_ECAP_RADIX_MISS   (-76)  /* radix tree 查找失败（[DSL] 模式使用） */
#define AIRY_ECAP_STATIC_KEY   (-77)  /* static_key 禁用（[DSL] 模式使用） */

/* Capability Folding Badge 校验错误码（新增） */
#define AIRY_ECAP_BADGE        (-78)  /* Badge 格式无效或 Random Tag 不匹配 */
#define AIRY_ECAP_EPOCH        (-79)  /* Badge Epoch 不匹配（已撤销或过期） */
#define AIRY_ECAP_FORGED       (-80)  /* 检测到 Badge 伪造尝试（触发 Fault） */
#define AIRY_ECAP_PERM         (-81)  /* 权限不足（opcode 所需权限未满足） */
#define AIRY_ECAP_FROZEN       (-82)  /* Ring 已冻结 */

/* [-82, -100] 预留 */

/* ===== [SC] 码空间 [-101, -200] ===== */
/* 见 08-sc-error-contract.md */

/* ===== [DSL] 码空间 [-201, -300] ===== */
/* 见 10-architecture/11-degraded-survival-layer.md */

/* ===== Fault 码空间 [0x1000, 0x1FFF] ===== */
#define AIRY_FAULT_CAP_FORGED  (0x1001)  /* Badge 伪造尝试 */
#define AIRY_FAULT_CAP_LEAK    (0x1002)  /* Badge 泄漏（跨 Agent 使用） */
#define AIRY_FAULT_RING_CORRUPT (0x1003) /* Ring 数据损坏 */

#endif /* AIRYMAX_ERROR_H */
```

### 8.2 错误码语义说明

| 错误码 | 值 | 触发条件 | 发送方处理 |
|--------|---|---------|-----------|
| AIRY_ECAP_BADGE | -78 | Badge 格式无效、Random Tag 不匹配、CAP_CARRY 但 badge=0 | 检查 Badge 是否正确编译 |
| AIRY_ECAP_EPOCH | -79 | Badge Epoch 与全局 Epoch 不匹配 | 重新向 sec_d 请求 Badge |
| AIRY_ECAP_FORGED | -80 | 检测到 Badge 伪造尝试 | 触发 Fault，sec_d 审计，可能终止 Agent |
| AIRY_ECAP_PERM | -81 | Badge 权限位不满足 opcode 所需 | 重新申请更高权限 Badge |
| AIRY_ECAP_FROZEN | -82 | Ring 已冻结 | 等待解冻或联系管理员 |
| AIRY_ECAP_RADIX_MISS | -76 | [DSL] 模式 radix tree 查找失败 | 降级模式兜底 |
| AIRY_ECAP_STATIC_KEY | -77 | [DSL] 模式 static_key 禁用 | 降级模式兜底 |

---

## §9 [DSL] 降级生存模式（H6）

### 9.1 [DSL] ipc.h 降级块

```c
/* kernel/include/airymax/ipc.h —— [DSL] 降级生存层 */

#ifdef AIRY_SC_FALLBACK
/* [DSL] 降级模式：[SC] 共享契约不可用时 */

/* 降级模式下的消息头（仍 128 字节，但字段语义简化） */
/* capability_badge 字段存在但被忽略（H6） */
struct airy_ipc_msg_hdr {
    __u32   magic;              /* offset  0, 'ARE1' */
    __u16   opcode;             /* offset  4, 仅支持 SEND/RECV */
    __u16   flags;              /* offset  6, 必须为零 */
    __u64   trace_id;           /* offset  8 */
    __u64   timestamp_ns;       /* offset 16 */
    __u64   src_task;           /* offset 24 */
    __u64   dst_task;           /* offset 32 */
    __u32   payload_len;        /* offset 40 */
    __u64   capability_badge;   /* offset 44, 存在但被忽略（值=0） */
    __u32   crc32;              /* offset 52 */
    __u8    reserved[72];       /* offset 56 */
} __attribute__((packed));

_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128, "...");

/* [DSL] 模式支持的 opcode（仅最简） */
#define AIRY_IPC_OP_SEND        0x0001
#define AIRY_IPC_OP_RECV        0x0002
/* SEND_BATCH/CANCEL/FREEZE/CAP_REQUEST/CAP_RESPONSE 不支持 */

/* [DSL] 模式的 fastpath（C-S9 跳过） */
static inline int airy_cap_badge_ok_dsl(u64 src_task, u64 badge, u16 opcode)
{
    /* H6: capability_badge 字段存在但被忽略（值=0，跳过校验） */
    if (badge != 0)
        return -AIRY_ECAP_BADGE;  /* [DSL] 模式 badge 必须为 0 */
    /* 跳过 C-S9，退化到 radix tree 兜底 */
    return airy_cap_radix_check(src_task, opcode);
}

#endif /* AIRY_SC_FALLBACK */
```

### 9.2 [DSL] 模式的退化语义

```
[DSL] 降级模式的能力校验:
  1. capability_badge 必须为 0（H6）
  2. C-S9 跳过 Badge 校验
  3. 退化到 radix tree 兜底路径
  4. 使用 AIRY_ECAP_RADIX_MISS (-76) 和 AIRY_ECAP_STATIC_KEY (-77)

[DSL] 模式的限制:
  - 仅支持 SEND/RECV opcode
  - 不支持 SEND_BATCH/CANCEL/FREEZE/CAP_REQUEST/CAP_RESPONSE
  - 性能退化（radix tree 查找 ~50-100ns）
  - 安全性退化（无 Random Tag 防伪造）

[DSL] 模式的触发条件:
  - [SC] 共享契约层不可用（agentrt 与 agentrt-linux 版本不匹配）
  - 内核编译时定义 AIRY_SC_FALLBACK
  - 运行时检测到 [SC] 头文件版本不匹配

[DSL] 模式的退出:
  - 重新建立 [SC] 共享契约
  - 重启相关 daemon
  - 取消 AIRY_SC_FALLBACK 编译选项
```

---

## §10 与 Airymax Unify Design 五模块的对接

### 10.1 A-UEF（统一错误码框架）对接

```
A-IPC → A-UEF 的依赖:
  - AIRY_EIPC_* 错误码（IPC 码空间 [-41, -70]）
  - AIRY_ECAP_* 错误码（Capability 码空间 [-71, -100]）
  - AIRY_FAULT_* 错误码（Fault 码空间 [0x1000, 0x1FFF]）

A-UEF → A-IPC 的依赖:
  - 无（A-UEF 是基础框架，不依赖 A-IPC）

对接点:
  - [SC] error.h 共享定义（08-sc-error-contract.md）
  - fastpath 返回错误码 → CQE res 字段 → 用户态获取
  - Fault 码触发 sec_d 审计 + 可能的 Agent 终止

一致性检查:
  ✓ AIRY_ECAP_BADGE/EPOCH/FORGED/PERM/FROZEN 已在 §8 定义
  ✓ AIRY_ECAP_RADIX_MISS/STATIC_KEY 保留供 [DSL] 模式使用
  ✓ Fault 码 AIRY_FAULT_CAP_FORGED 已在 §8 定义
```

### 10.2 A-ULP（统一日志框架）对接

```
A-IPC → A-ULP 的依赖:
  - airy_log_record (128B) 日志记录格式
  - 5 级日志枚举（LOG_DEBUG~LOG_FATAL）
  - printk 8 级映射

A-ULP → A-IPC 的依赖:
  - 无（A-ULP 是基础框架，不依赖 A-IPC）

对接点:
  - [SC] log_types.h 共享定义（09-sc-log-types-contract.md）
  - fastpath 错误时记录 airy_log_record
  - trace_id 字段贯穿 IPC 消息 + 日志记录（全链路追踪）

关键不变量:
  - airy_log_record (128B) 与 airy_ipc_msg_hdr (128B) 长度相同
  - 但语义不同，使用不同 magic 避免混淆
  - 禁止复用同一结构体（09 号 §5.4）

一致性检查:
  ✓ trace_id 字段在 Layout C v4 offset 8（与 A-ULP 日志记录对齐）
  ✓ timestamp_ns 字段在 Layout C v4 offset 16（与 A-ULP 日志记录对齐）
```

### 10.3 A-UCS（统一配置框架）对接

```
A-IPC → A-UCS 的依赖:
  - ring 配置（kfifo 大小、registered buffer 大小）
  - Badge 配置（Epoch 初始值、Random Tag 长度）
  - [DSL] 模式开关（AIRY_SC_FALLBACK）

A-UCS → A-IPC 的依赖:
  - 无（A-UCS 是基础框架，不依赖 A-IPC）

对接点:
  - 配置文件 /etc/agentrt/ipc.conf
  - sysfs 接口 /sys/kernel/airy/ipc/
  - 进程启动时读取配置 → 初始化 ring + kfifo + agent_caps[]

一致性检查:
  ✓ 配置项与 fastpath 实现对齐
  ✓ [DSL] 模式开关 AIRY_SC_FALLBACK 已定义
```

### 10.4 A-ULS（统一生命周期框架）对接

```
A-IPC → A-ULS 的依赖:
  - ring 生命周期（创建/冻结/销毁）
  - Badge 生命周期（编译/撤销/过期）
  - C-S0 ring->frozen 检查（A-ULS 控制）

A-ULS → A-IPC 的依赖:
  - 无（A-ULS 是基础框架，不依赖 A-IPC）

对接点:
  - ring->frozen 标志位（C-S0 检查）
  - FREEZE opcode（0x0005）触发 ring 冻结
  - sec_d 撤销 Badge 时通知 A-ULS（可选）

一致性检查:
  ✓ C-S0 ring->frozen 检查在 §5.2 实现
  ✓ FREEZE opcode 已在 §4.1 定义
  ✓ Badge 撤销（atomic_inc）与 A-ULS 解耦（无 drain）
```

### 10.5 A-IPC（统一 IPC 框架）自身

```
A-IPC 是本设计的核心，与自身的对接即完整性检查:

  ✓ Layout C v4 完整定义（§2）
  ✓ opcode 完整定义（§4）
  ✓ syscall 12→4 映射（§1.3）
  ✓ fastpath 7 态状态机（§5.1）
  ✓ fastpath 完整实现（§5.2）
  ✓ Badge 安全模型（§6）
  ✓ 隔离设计（§7）
  ✓ 错误码定义（§8）
  ✓ [DSL] 降级生存（§9）
  ✓ 与 A-UEF 对接（§10.1）
  ✓ 与 A-ULP 对接（§10.2）
  ✓ 与 A-UCS 对接（§10.3）
  ✓ 与 A-ULS 对接（§10.4）
```

---

## §11 与 IRON-9 v3 四层模型的精确映射

### 11.1 [SC] 共享契约层

```
[SC] 层共享内容（物理宿主: kernel/include/airymax/）:
  ✓ ipc.h —— Layout C v4 消息头定义（§2.1）
  ✓ error.h —— 错误码定义（§8.1）
  ✓ log_types.h —— 日志记录格式（A-ULP）
  ✓ sched.h —— 调度类型定义（sched_tac）
  ✓ memory_types.h —— 内存类型定义（MemoryRovol）
  ✓ security_types.h —— 安全类型定义（sec_d）
  ✓ cognition_types.h —— 认知类型定义（cogn_d）
  ✓ syscalls.h —— syscall 编号定义（§1.3）
  ✓ uapi_compat.h —— UAPI 兼容性定义
  ✓ lsm_types.h —— LSM 类型定义（纯 C LSM）

[SC] 层的变更分类（120 号 §7.4）:
  - 新增字段（向后兼容）: 需双端同步
  - 修改字段语义（破坏性）: 禁止，必须新增字段
  - magic 值: 一经发布即冻结（120 号 §7.5）

本设计对 [SC] 层的变更:
  - ipc.h: 新增 capability_badge 字段（offset 44-51）→ 向后兼容
  - ipc.h: 新增 CAP_REQUEST/CAP_RESPONSE opcode → 向后兼容
  - ipc.h: 新增 AIRY_IPC_F_CAP_CARRY 标志位 → 向后兼容
  - error.h: 新增 AIRY_ECAP_BADGE/EPOCH/FORGED/PERM/FROZED → 向后兼容
```

### 11.2 [SS] 语义同源层

```
[SS] 层语义同源内容（不在 [SC] 头文件中，在内核实现侧）:
  ✓ Badge 校验机制: airy_cap_badge_ok() 内联函数
  ✓ agent_caps[] 静态数组: 内核内存，用户态不可见
  ✓ airy_global_epoch: atomic_t，内核全局
  ✓ Random Tag 生成: get_random_bytes()
  ✓ C-S9 校验逻辑: READ_ONCE + 位运算 + 比较
  ✓ sec_d Badge 编译流程: airy_sys_call(COMPILE_BADGE)

[SS] 层的契约:
  - agentrt 用户态: 不使用 capability_badge（始终为 0）
  - agentrt-linux 内核: 使用 capability_badge + C-S9 内联校验
  - 两者共享 [SC] 数据结构定义，但校验机制属于 [SS] 语义同源层

关键论证（34 号 §2）:
  [SC] 共享的是数据结构定义，不是实现语义。
  校验机制差异属于 [SS] 语义同源层。
  这正是 [SS] 层的存在意义。
```

### 11.3 [IND] 完全独立层

```
[IND] 层独立内容:
  ✓ agentrt 用户态: 传统 cap_t 引用 + airy_ipc_send() 库函数
  ✓ agentrt-linux 内核: capability_badge + C-S9 内联校验
  ✓ 两者在 [IND] 层完全独立，无相互依赖

[IND] 层的契约:
  - agentrt 不感知 capability_badge 字段的存在
  - agentrt 不调用 sec_d 的 Badge 编译接口
  - agentrt-linux 不依赖 agentrt 的 cap_t 引用机制
  - 两者通过 [SC] 数据结构 + [SS] 语义同源保持契约一致
```

### 11.4 [DSL] 降级生存层

```
[DSL] 层降级内容（§9）:
  ✓ capability_badge 字段存在但被忽略（值=0）
  ✓ C-S9 跳过 Badge 校验
  ✓ 退化到 radix tree 兜底路径
  ✓ 仅支持 SEND/RECV opcode
  ✓ 使用 AIRY_ECAP_RADIX_MISS/STATIC_KEY 错误码

[DSL] 层的触发条件:
  - [SC] 共享契约层不可用
  - 内核编译时定义 AIRY_SC_FALLBACK
  - 运行时检测到版本不匹配

[DSL] 层的退出:
  - 重新建立 [SC] 共享契约
  - 重启相关 daemon
  - 取消 AIRY_SC_FALLBACK 编译选项
```

---

## §12 与 §10 SSoT 声明的对齐（10-unify-design.md §10）

### 12.1 §10 SSoT 硬约束技术选型清单

| §10 约束 | 本设计是否遵守 | 说明 |
|---------|:---:|------|
| sched_tac 调度策略 | ✓ | 不影响 A-IPC 设计（C-S5 是优化条件） |
| IORING_OP_URING_CMD + registered buffer + mmap | ✓ | §1 单平面架构基于 io_uring |
| 纯 C LSM（不用 BPF LSM） | ✓ | H5: Badge 校验是纯 C LSM 的 fastpath 内联 |
| alloc_pages + mmap | ✓ | registered buffer 底层机制 |
| [SC] 物理宿主 kernel/include/airymax/ 共 10 个头文件 | ✓ | §11.1 [SC] 层映射 |

### 12.2 §10 SSoT 新增声明（需同步更新）

```
新增 §10 声明:
  "A-IPC 采用 Capability Folding 重构方案：
   - 单平面架构（io_uring 数据面，4 个控制面 syscall）
   - Layout C v4 消息头（128 字节，含 capability_badge 字段）
   - Badge 64-bit Native Word（Epoch + Random Tag + Perms）
   - C-S9 fastpath 内联校验（~10ns）
   - 全局 Epoch 撤销（1 行 atomic_inc，无 drain）
   - CAP_REQUEST opcode 自举（无 NULL Badge 硬编码）
   - [DSL] 降级模式（capability_badge=0，跳过 C-S9）"
```

---

## §13 实施计划

### 13.1 Phase 1: [SC] 头文件更新（P0）

```
任务 1.1: 更新 kernel/include/airymax/ipc.h
  - 新增 capability_badge 字段（offset 44-51）
  - 新增 CAP_REQUEST/CAP_RESPONSE opcode
  - 新增 AIRY_IPC_F_CAP_CARRY 标志位
  - 新增 Badge 位布局宏
  - 新增 Capability 权限位定义
  - 更新 _Static_assert

任务 1.2: 更新 kernel/include/airymax/error.h
  - 新增 AIRY_ECAP_BADGE (-78)
  - 新增 AIRY_ECAP_EPOCH (-79)
  - 新增 AIRY_ECAP_FORGED (-80)
  - 新增 AIRY_ECAP_PERM (-81)
  - 新增 AIRY_ECAP_FROZEN (-82)
  - 新增 AIRY_FAULT_CAP_FORGED (0x1001)
  - 新增 AIRY_FAULT_CAP_LEAK (0x1002)
  - 新增 AIRY_FAULT_RING_CORRUPT (0x1003)

任务 1.3: 更新 [SC] 双端 CI
  - sc-dual-ci.yml 新增 Layout C v4 字节级校验
  - sc-dual-ci.yml 新增错误码值域校验
```

### 13.2 Phase 2: fastpath 实现（P0）

```
任务 2.1: 实现 kernel/ipc/airy_uring_cmd.c
  - airy_uring_cmd() 入口函数
  - airy_ipc_validate() C-S0~C-S11 校验链
  - airy_ipc_can_fast_deliver() FAST_SEND 判断
  - airy_ipc_deliver_fast() FAST_SEND 路径
  - airy_ipc_deliver_full() SLOW_SEND 路径
  - NONBLOCK 模式 + io-wq 接管（33 号 §1 修复）

任务 2.2: 实现 kernel/security/airy_cap.c
  - agent_caps[1024] 静态数组
  - airy_global_epoch (atomic_t)
  - airy_cap_epoch_get()
  - airy_cap_epoch_increment()
  - airy_cap_badge_compile()（sec_d 调用）
  - airy_cap_badge_revoke()（sec_d 调用）
  - airy_cap_badge_ok()（C-S9 内联）
  - airy_cap_has_perm()

任务 2.3: 实现控制面 syscall
  - airy_sys_call() 重写（仅 sec_d 调用，COMPILE_BADGE/REVOKE_BADGE/LSM_CTL）
  - 移除 airy_sys_send/recv/reply/delegate/mint/revoke/call_batch
  - 保留 airy_sys_rovol_ctl/sched_ctl/clt_notify
```

### 13.3 Phase 3: 验证（P0）

```
任务 3.1: CBMC 全函数验证
  - airy_uring_cmd() CBMC 验证脚本
  - 验证 C-S9 不可绕过
  - 验证 agent_caps[] 与 kfifo 独立
  - 验证 check-and-return 模式
  - 验证锁内无阻塞操作

任务 3.2: 性能基准测试
  - 128B 消息 P50/P99 延迟
  - 128B 消息吞吐量
  - 12 daemon 通信网格死锁检测
  - uring_lock 争用压力测试
  - CFS 迁移 + SLOW_PATH 退化测试

任务 3.3: 安全测试
  - Badge 伪造攻击测试
  - Random Tag 暴力枚举测试
  - 时序侧信道测试
  - agent_caps[] 越界访问测试
```

### 13.4 Phase 4: 文档同步（P0/P1/P2）

```
任务 4.1: P0 文档同步（7 份）
  - 10-unify-design.md §8 A-IPC 章节重写
  - 10-unify-design.md §10 SSoT 新增声明
  - 30-interfaces/01-syscalls.md syscall 表 12→4
  - 30-interfaces/02-ipc-protocol.md Layout C v4
  - 30-interfaces/07-ipc-fastpath.md C-S9 + 7 态状态机
  - 50-engineering-standards/120-cross-project-code-sharing.md §2.7 [SC] ipc.h
  - 30-interfaces/08-sc-error-contract.md §2.4 Capability 码空间

任务 4.2: P1 文档同步（3 份）
  - 110-security/03-capability-model.md radix tree → Epoch + 静态数组
  - 10-architecture/11-degraded-survival-layer.md §2.2 [DSL] ipc.h 降级块
  - 40-dataflows/03-ipc-flow.md 消除控制面数据流

任务 4.3: P2 文档同步（1 份）
  - 170-performance/03-ipc-performance.md fastpath 延迟数值更新
```

---

## §14 风险与缓解

### 14.1 已识别风险（34 号 §5）

| # | 风险 | 严重度 | 缓解措施 | 状态 |
|---|------|:---:|---------|:---:|
| R1 | Badge 伪造攻击 | P0 | 随机标签 + 内核静态数组（30 号修复） | ✓ 已缓解 |
| R2 | uring_lock 持有 wake_up 导致争用 | P0 | NONBLOCK 模式 + io-wq 接管（33 号修复） | ✓ 已缓解 |
| R3 | seL4 架构级隔离丧失 | P1 | 数据结构隔离 + CBMC 全函数验证（31 号论证） | ✓ 可接受 |
| R4 | 原子性丢失（seL4 Call 语义） | P1 | request_id/correlation_id 模式（异步场景可接受） | ✓ 可接受 |
| R5 | [SC] 双端同步更新成本 | P2 | sc-dual-ci.yml 已有机制 | ✓ 可控 |

### 14.2 新增风险（本设计引入）

| # | 风险 | 严重度 | 缓解措施 | 状态 |
|---|------|:---:|---------|:---:|
| R6 | Epoch u16 溢出（65536 次撤销） | P2 | 0.1.1 不会触及；1.0.1 可扩展 u32 | ✓ 可控 |
| R7 | Random Tag 32 位暴力枚举 | P2 | 100 次失败触发警报；枚举需 11 分钟 | ✓ 可控 |
| R8 | agent_caps[1024] 容量限制 | P2 | 0.1.1 Agent 数 < 100；1.0.1 可扩展 | ✓ 可控 |
| R9 | CBMC 验证工具链未实证 | P2 | Phase 3 任务 3.1 实证 | ⏳ 待验证 |
| R10 | 12 daemon 通信网格未仿真 | P2 | Phase 3 任务 3.2 实证 | ⏳ 待验证 |

### 14.3 不可接受的风险

```
经过 33 份审查报告 + 本设计的逐项验证，没有发现不可接受的风险。

所有 P0 风险已缓解（R1, R2）。
所有 P1 风险经过论证可接受（R3, R4）。
所有 P2 风险可控（R5-R10）。
```

---

## §15 设计完整性自检

### 15.1 6 条硬约束自检

| 约束 | 描述 | 本设计章节 | 状态 |
|------|------|-----------|:---:|
| H1 | Layout C v4 总长 128 字节，magic 0x41524531 | §2.1 | ✓ |
| H2 | capability_badge 进 [SC]，校验机制属 [SS] | §2.3, §11.2 | ✓ |
| H3 | agentrt 用户态 capability_badge=0 | §2.3, §11.3 | ✓ |
| H4 | agentrt-linux 内核 capability_badge 由 sec_d 编译 | §6.2, §11.2 | ✓ |
| H5 | 纯 C LSM 职责不变，Badge 校验是 fastpath 内联 | §5.2, §6.3 | ✓ |
| H6 | [DSL] 降级模式 capability_badge=0，跳过 C-S9 | §9 | ✓ |

### 15.2 7 颗螺丝自检（28 号）

| # | 螺丝 | 本设计修复 | 状态 |
|---|------|-----------|:---:|
| 1 | Epoch drain 5ms 阻塞 | §3.1: 1 行 atomic_inc | ✓ |
| 2 | CRC32 不覆盖 capability_badge | §2.4: 覆盖 header[0:52) | ✓ |
| 3 | NULL Badge 硬编码特例 | §4.2: CAP_REQUEST opcode | ✓ |
| 4 | 全局/独立 Epoch 矛盾 | §3.1: 1 个全局 atomic_t | ✓ |
| 5 | seq_num + negotiated_ver 无协议 | §2.1: 移除（reserved[72]） | ✓ |
| 6 | SLOW_PATH 合并丢失语义 | §5.1: SLOW_SEND/SLOW_RECV 分离 | ✓ |
| 7 | __future[66] 超 50% 保留 | §2.1: reserved[72]（移除非必要字段后） | ✓ |

### 15.3 三大物理鸿沟自检（33 号）

| # | 物理鸿沟 | 本设计修复 | 状态 |
|---|---------|-----------|:---:|
| 1 | uring_lock 持有 wake_up | §5.2: NONBLOCK + io-wq | ✓ |
| 2 | MMU 页表开销 | §1.1: registered buffer 已解决 | ✓ |
| 3 | CFS 调度迁移 | §5.2: C-S5 优化条件 + CPU 亲和性 | ✓ |

### 15.4 五模块对接自检

| 模块 | 对接章节 | 状态 |
|------|---------|:---:|
| A-UEF | §10.1, §8 | ✓ |
| A-ULP | §10.2 | ✓ |
| A-UCS | §10.3 | ✓ |
| A-ULS | §10.4 | ✓ |
| A-IPC | §10.5 | ✓ |

### 15.5 IRON-9 v3 四层模型自检

| 层级 | 本设计章节 | 状态 |
|------|-----------|:---:|
| [SC] 共享契约 | §2.1, §8.1, §11.1 | ✓ |
| [SS] 语义同源 | §2.3, §6, §11.2 | ✓ |
| [IND] 完全独立 | §11.3 | ✓ |
| [DSL] 降级生存 | §9, §11.4 | ✓ |

---

## §16 设计总结

### 16.1 一句话总结

**A-IPC 最终重新设计基于 6 条硬约束，将 Capability Folding 折叠到 io_uring 数据面 fastpath，实现"通信=io_uring、授权=1个Badge、撤销=1条atomic_inc、自举=1个CAP_REQUEST opcode、完整性=1个CRC32、管理器=sec_d、降级=badge=0跳过C-S9"的简约形态，与 IRON-9 v3 四层模型完全对齐，与 Airymax Unify Design 五模块完全对接，所有风险可控。**

### 16.2 设计的关键决策点

```
决策 1: 单平面架构（25 号 §0）
  - 消除控制面 IPC syscall（12→4）
  - 数据面 io_uring 唯一平面
  - C-S9 内联 Badge 校验

决策 2: Layout C v4（28 号 §7）
  - 128 字节定长
  - capability_badge offset 44-51
  - CRC32 覆盖 header[0:52)
  - reserved[72] 替代 __future[66]

决策 3: 全局 Epoch（28 号 §1, §4）
  - 1 个 atomic_t
  - 1 行 atomic_inc 撤销
  - 无 drain，无 bitmap，无 mdelay

决策 4: CAP_REQUEST 自举（28 号 §3）
  - opcode 0x0010
  - 无 Badge，内核路由到 sec_d
  - 消除 NULL Badge 硬编码

决策 5: NONBLOCK + io-wq（33 号 §1）
  - 锁内仅校验 + 快速投递
  - 需要唤醒时返回 -EAGAIN
  - io-wq 接管 wake_up

决策 6: Random Tag 防伪造（30 号 §3）
  - 32-bit 随机标签
  - 内核 agent_caps[] 静态数组
  - 3 个 READ_ONCE + 位运算 + 比较

决策 7: [DSL] 降级生存（H6）
  - capability_badge=0
  - 跳过 C-S9
  - 退化到 radix tree 兜底
```

### 16.3 下一步

```
1. 阶段 5: 全面检查 Airymax Unify Design 五模块一致性（36 号文档）
2. 实施前: 同步更新 11 份文档（34 号 §6.2 清单）
3. Phase 1: [SC] 头文件更新（§13.1）
4. Phase 2: fastpath 实现（§13.2）
5. Phase 3: 验证（§13.3）
6. Phase 4: 文档同步（§13.4）
```

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. | A-IPC 最终重新设计 | v1.0 | 2026-07-18
