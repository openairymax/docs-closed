Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 37 — Capability Folding 决策总纲与实施路线图

## "第一块基石已确定——现在开始建造"

> **文档性质**：用户决策采用 Capability Folding 后的系统性总纲与实施路线图
> **决策来源**：用户 2026-07-18 决定采用 Capability Folding 重构 A-IPC
> **前置基础**：34 号科学论证 + 35 号最终设计 + 36 号五模块检查
> **文档定位**：从论证阶段进入实施阶段的转折点
> **核心论断**：Capability Folding 是 AirymaxOS 第一块基石的正确形状

---

## §0 决策声明

### 0.1 决策

```
决策: 采用 Capability Folding 重构 A-IPC
决策日期: 2026-07-18
决策依据: 34 号 §6.1 六维度科学论证
决策性质: 不可逆（第一块基石不可移动）

决策依据六维度:
  维度 1（定位）: Capability Folding 提供更强的基石属性（3 强）
  维度 2（契约）: 与 IRON-9 v3 四层模型没有不可调和冲突
  维度 3（工程）: 0 行代码现状是最佳时间窗口
  维度 4（替代）: 三方案比较中综合最优
  维度 5（风险）: 5 大风险全部可控
  维度 6（哲学）: 符合乔布斯/艾夫"简约就是美"
```

### 0.2 决策不可逆性

```
为什么不可逆:
  1. A-IPC 是 AirymaxOS 第一块基石
  2. 后续所有设计（sched_tac/MemoryRovol/sec_d/cogn_d）都建立在 A-IPC 之上
  3. 一旦实施，Layout C v4 的 magic 值一经发布即冻结（120 号 §7.5）
  4. capability_badge 字段进入 [SC] ipc.h，向后兼容承诺
  5. 6 条硬约束 H1-H6 不可妥协

回退成本:
  - 实施前回退: 0（无代码）
  - Phase 1 后回退: 低（仅 [SC] 头文件）
  - Phase 2 后回退: 中（fastpath 代码）
  - Phase 3 后回退: 高（已验证）
  - Phase 4 后回退: 极高（文档已同步）
```

---

## §1 Capability Folding 是什么

### 1.1 字面定义

```
Capability = 能力令牌（seL4 风格的安全能力模型）
Folding    = 折叠（将外挂的前置操作折叠进内生路径）
```

**Capability Folding 是一种将 capability check（能力校验）从独立的控制面操作"折叠"到 IPC 数据面消息传递路径中的设计模式。**

### 1.2 核心思想

25 号 §0 的一句论断定义了它的本质：

> **"IPC 不是承载能力校验——IPC 就是能力校验。"**

这意味着：
- 能力校验不再是 IPC 发送前的独立前置步骤
- 能力校验本身就是 IPC 消息传递 fastpath 的一个内嵌步骤
- 消息头携带"能力证明"（Badge），fastpath 在投递消息的同时完成校验

### 1.3 与 seL4 双平面的对比

| 维度 | seL4 双平面 | Capability Folding 单平面 |
|------|------------|-------------------------|
| 控制面 | `seL4_Call(cap, msg)` 独立调用 | 不存在（折叠进数据面） |
| 数据面 | `doIPCTransfer()` 独立调用 | io_uring fastpath 唯一平面 |
| 能力校验位置 | 控制面 `lookupCapAndSlot()` | 数据面 fastpath C-S9 内联 |
| 校验与投递 | 两个函数、两个栈帧、两个失败域 | 一个函数、一个栈帧、一个失败域 |
| 隔离基础 | 架构级（Isabelle/HOL 证明） | 数据结构级（CBMC 全函数验证） |

---

## §2 Capability Folding 长什么样子

### 2.1 消息头层面：Layout C v4

128 字节定长消息头中，offset 44-51 这 8 个字节就是 Capability Folding 的物理载体：

```c
struct airy_ipc_msg_hdr {
    __u32   magic;              /* offset  0, 'ARE1' 0x41524531 */
    __u16   opcode;             /* offset  4 */
    __u16   flags;              /* offset  6 */
    __u64   trace_id;           /* offset  8 */
    __u64   timestamp_ns;       /* offset 16 */
    __u64   src_task;           /* offset 24 */
    __u64   dst_task;           /* offset 32 */
    __u32   payload_len;        /* offset 40 */
    __u64   capability_badge;   /* offset 44, ← Capability Folding 物理载体 */
    __u32   crc32;              /* offset 52, 覆盖 header[0:52) + payload */
    __u8    reserved[72];       /* offset 56 */
} __attribute__((packed));
_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128, "...");
```

### 2.2 Badge 层面：64-bit Native Word

那 8 个字节的内部结构（30 号审查修复后的最终形态）：

```
63                    48 47                16 15            0
┌──────────────────────┬─────────────────────┬──────────────┐
│   Epoch (16 bits)    │  Random Tag (32 bits)│ Perms (16 bits)│
└──────────────────────┴─────────────────────┴──────────────┘

Epoch (16 bits):       全局代际快照，撤销时 atomic_inc 立即失效
Random Tag (32 bits):  per-Agent 随机标签，sec_d 编译时生成，防伪造
Perms (16 bits):       权限位图（SEND/RECV/CALL/GRANT/REVOKE/FREEZE/BATCH）
```

### 2.3 fastpath 层面：C-S9 内联校验

在 11 个条件检查链（C-S0~C-S11）中，C-S9 就是 Capability Folding 的执行点：

```c
static inline int airy_cap_badge_ok(u64 src_task, u64 badge, u16 opcode)
{
    u16 badge_epoch = AIRY_BADGE_EPOCH(badge);
    u32 badge_randtag = AIRY_BADGE_RANDTAG(badge);
    u16 badge_perms = AIRY_BADGE_PERMS(badge);
    
    /* 1. Epoch 校验（1 次 atomic_read） */
    if (badge_epoch != airy_cap_epoch_get())
        return -AIRY_ECAP_EPOCH;
    
    /* 2. Random Tag 校验（1 次 READ_ONCE） */
    if (badge_randtag != READ_ONCE(agent_caps[src_task].randtag))
        return -AIRY_ECAP_FORGED;  /* 触发 Fault */
    
    /* 3. 权限校验（1 次 READ_ONCE + 位运算） */
    if (!airy_cap_has_perm(badge_perms, opcode))
        return -AIRY_ECAP_PERM;
    
    return 0;  /* ~10ns 完成 */
}
```

**关键属性**：3 个 READ_ONCE、零锁、零 RCU、零 kmalloc——纯读取 + 位运算 + 比较。

### 2.4 数据结构层面：三个独立区域

```
1. agent_caps[1024]   能力数据（内核静态数组，16KB）
   ├─ 唯一写者: sec_d
   └─ 读者: fastpath C-S9

2. kfifo              数据投递缓冲区（per-cpu SPSC 无锁）
   ├─ 写者: fastpath kfifo_in
   └─ 读者: 接收方 CQE

3. io_uring ring      通信原语
   ├─ 写者: 发送方 SQE
   └─ 读者: 接收方 CQE
```

三者内存区域独立，更新路径独立，失败域独立——这就是 31 号审查论证的"数据结构隔离"。

### 2.5 架构层面：单平面

```
┌─────────────────────────────────────────────────────────┐
│           A-IPC 单平面架构（Capability Folding）          │
│                                                          │
│  数据面（io_uring，高频）:                                │
│    IORING_OP_URING_CMD → airy_uring_cmd()                │
│      ├─ airy_ipc_validate()  [C-S0~C-S11, 含 C-S9 Badge] │
│      ├─ airy_ipc_deliver_fast()  [NONBLOCK, ~158ns]      │
│      └─ airy_ipc_deliver_full()  [io-wq, wake_up]        │
│                                                          │
│  控制面（4 个 syscall，低频）:                             │
│    airy_sys_call        — 仅 sec_d 编译 Badge             │
│    airy_sys_rovol_ctl   — MemoryRovol 控制                │
│    airy_sys_sched_ctl   — sched_tac 调度                  │
│    airy_sys_clt_notify  — 客户端通知                      │
└─────────────────────────────────────────────────────────┘
```

### 2.6 最终简约形态

28 号 §8.3 + 34 号 §7.1 + 35 号 §0.4 三处一致定义的最终形态：

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

## §3 Capability Folding 怎么来的

### 3.1 起点：当前 A-IPC 的根本矛盾（25 号 §0.1）

九轮审查最终收敛为一个论断：

> **当前 A-IPC 不是一个统一的通信体系。它是两个独立 IPC 子系统的并列——控制面是 seL4 风格的同步阻塞 syscall，数据面是 io_uring 风格的异步 CQE。这两个子系统共享一个消息头格式（Layout C），但在能力校验、错误语义、故障隔离上互不贯通。**

九轮审查发现的所有问题，根源都是同一个：**能力校验没有被设计为 IPC 的内生属性，而是被设计为 IPC 的外挂检查。**

### 3.2 演进时间线

```
阶段 0: 双平面架构（当前 A-IPC）
  ├─ 控制面: 12 syscall, decode_and_invoke (~200 行)
  ├─ 数据面: io_uring CQE, cap_check_fast (~50 行)
  ├─ 能力模型: radix tree + per-CPU cache + IPI coherency (~300 行)
  └─ 问题: 死锁、不可通约、排序丢失、OP 码不对齐

阶段 1: 27 号重构方案（第一版 Capability Folding）
  ├─ Badge = (Epoch<<32) | Permissions
  ├─ 两阶段 drain 协议 + mdelay(5) + bitmap
  ├─ NULL Badge 硬编码特例
  ├─ 全局/独立 Epoch 矛盾
  ├─ seq_num + negotiated_ver 无协议
  └─ 问题: 7 颗"看不见的螺丝"

阶段 2: 28 号乔布斯/艾夫简约化审查
  ├─ 消除 drain（1 行 atomic_inc）
  ├─ CRC32 覆盖 capability_badge
  ├─ CAP_REQUEST opcode 替代 NULL Badge
  ├─ 1 个全局 atomic_t
  ├─ 移除 seq_num/negotiated_ver
  ├─ SLOW_SEND/SLOW_RECV 分离
  └─ reserved[72] 替代 __future[66]

阶段 3: 30 号 P0 安全漏洞修复
  ├─ 自描述 Badge 可伪造（P0 漏洞）
  ├─ 引入 32-bit Random Tag
  ├─ 内核 agent_caps[] 静态数组
  └─ Badge = (Epoch<<48 | RandomTag<<16 | Perms)

阶段 4: 31 号架构耦合性审查
  ├─ 论证 seL4 架构级隔离 vs A-IPC 数据结构级隔离
  ├─ fastpath 100 行代码 CBMC 全函数验证可行
  └─ trade-off 对 agentrt-linux 可接受

阶段 5: 33 号三大物理鸿沟审查
  ├─ uring_lock 持有 wake_up → NONBLOCK + io-wq
  ├─ MMU 页表开销 → registered buffer 已解决
  └─ CFS 调度迁移 → C-S5 优化条件 + CPU 亲和性

阶段 6: 34 号从整体方案高度科学论证
  ├─ 6 维度论证（定位/契约/工程/替代/风险/决策）
  ├─ 核心发现: [SC] 共享数据结构，[SS] 语义同源校验
  ├─ 6 条硬约束 H1-H6
  └─ 最终结论: ADOPT Capability Folding

阶段 7: 35 号最终重新设计
  ├─ Layout C v4 完整定义
  ├─ fastpath 7 态状态机 + 完整 C 实现
  ├─ Badge 安全模型 + 防伪造分析
  ├─ [DSL] 降级生存模式
  └─ 五模块对接 + IRON-9 v3 四层映射

阶段 8: 36 号五模块全面检查
  ├─ 10 个问题全部是文档同步问题（非设计缺陷）
  ├─ 17 份文档同步清单
  └─ 五模块自洽性: 优

阶段 9: 37 号决策总纲（本文档）
  └─ 用户决策采用，进入实施阶段
```

### 3.3 核心论证发现（34 号 §2）

整个演进过程中最关键的发现：

> **[SC] 共享的是数据结构定义，不是实现语义——校验机制差异属于 [SS] 语义同源层。**

这个发现回答了"Capability Folding 是否违反 IRON-9 v3 四层模型"的根本问题：

```
[SC] 共享契约层: capability_badge 字段定义（数据结构）
[SS] 语义同源层: Badge 校验机制（实现语义）
[IND] 完全独立层: agentrt 用户态 capability_badge=0
[DSL] 降级生存层: capability_badge=0 跳过 C-S9
```

**没有不可调和的冲突。**

---

## §4 Capability Folding 要做什么

### 4.1 直接工程目标

```
1. 消除控制面/数据面双平面架构
   - 12 syscall → 4 syscall
   - 消除 8 个 seL4 风格 IPC syscall
   - 数据面 io_uring 唯一平面

2. 将能力校验折叠到数据面 fastpath
   - C-S9 内联 Badge 校验
   - ~10ns 完成（vs 原 radix tree ~50-100ns）
   - 3 个 READ_ONCE + 位运算 + 比较

3. 实现"IPC 就是能力校验"
   - 消息头携带 Badge
   - fastpath 投递消息时同时完成校验
   - 无独立能力校验路径
```

### 4.2 基石三属性（34 号 §1）

A-IPC 是 AirymaxOS 的"第一块基石"，Capability Folding 赋予它基石的三属性：

```
1. 不可移动性
   6 条硬约束 H1-H6 不可妥协
   任何后续设计都必须在此形状之上构建

2. 承重性
   fastpath 100 行代码 + CBMC 全函数验证
   可承重的工程基础

3. 形状确定性
   Layout C v4 + opcode 表 + syscall 表
   第一块基石的精确形状
```

### 4.3 解决的根本问题

| 问题 | 解决方式 |
|------|---------|
| 控制面同步阻塞死锁 | 消除控制面 IPC（12→4 syscall） |
| 两套能力校验不可通约 | C-S9 唯一校验路径 |
| 消息排序无法跨三通道保证 | io_uring 单平面，单一排序域 |
| OP 码在两个平面定义不同 | 单平面统一 opcode 表 |
| radix tree + per-CPU cache 复杂度 | agent_caps[] 静态数组 + 全局 Epoch |
| IPI 缓存一致性开销 | READ_ONCE/WRITE_ONCE 无锁模型 |
| 5ms drain 阻塞 | 1 行 atomic_inc |
| Badge 可伪造 | 32-bit Random Tag + 内核静态数组 |
| uring_lock 持有 wake_up | NONBLOCK + io-wq 接管 |

---

## §5 6 条硬约束（不可妥协）

### 5.1 硬约束清单

```
H1: Layout C v4 总长保持 128 字节，magic 保持 0x41524531 'ARE1'
H2: capability_badge 字段进入 [SC] ipc.h，但校验机制属于 [SS] 层
H3: agentrt 用户态 capability_badge 始终为 0，使用传统 cap_t 引用
H4: agentrt-linux 内核 capability_badge 由 sec_d 编译，fastpath C-S9 校验
H5: 纯 C LSM 模块职责不变（策略/撤销/审计/执法），Badge 校验是其 fastpath 内联
H6: [DSL] 降级模式下 capability_badge 字段存在但被忽略（值=0，跳过校验）
```

### 5.2 硬约束的工程含义

| 约束 | 工程含义 | 违反后果 |
|------|---------|---------|
| H1 | 字节级冻结，向后兼容承诺 | 破坏 [SC] 契约，双端不兼容 |
| H2 | 数据结构与实现分离 | [SC]/[SS] 边界模糊，违反 IRON-9 |
| H3 | agentrt 不感知 Badge | agentrt 用户态复杂化 |
| H4 | sec_d 是唯一 Badge 编译者 | 安全模型破坏 |
| H5 | 纯 C LSM 不变 | 违反 §10 SSoT，需重新选型 |
| H6 | [DSL] 可生存 | 降级模式失败，系统不可用 |

---

## §6 核心设计要素汇总

### 6.1 Layout C v4 字段定义

| Offset | 字段 | 大小 | 语义 | 校验位置 |
|--------|------|------|------|---------|
| 0 | magic | 4B | `0x41524531 'ARE1'` | C-S1 |
| 4 | opcode | 2B | 操作码 | C-S2 |
| 6 | flags | 2B | 标志位 | C-S10 |
| 8 | trace_id | 8B | OpenTelemetry trace ID | 透传 |
| 16 | timestamp_ns | 8B | CLOCK_REALTIME 纳秒 | 透传 |
| 24 | src_task | 8B | 源 task_id | C-S9 |
| 32 | dst_task | 8B | 目标 task_id | C-S5/C-S6 |
| 40 | payload_len | 4B | 负载长度 | C-S3/C-S4 |
| 44 | capability_badge | 8B | Badge | C-S9 |
| 52 | crc32 | 4B | CRC32 | C-S12 |
| 56 | reserved[72] | 72B | 保留，必须为零 | C-S4 |

### 6.2 opcode 完整定义

| opcode | 值 | 名称 | 用途 | 是否需要 Badge |
|--------|---|------|------|:---:|
| SEND | 0x0001 | 发送消息 | 单条 IPC 消息发送 | ✓ |
| RECV | 0x0002 | 接收声明 | 接收方声明 expected opcode | ✓ |
| SEND_BATCH | 0x0003 | 批量发送 | 多条消息原子提交 | ✓ |
| CANCEL | 0x0004 | 取消发送 | 取消未完成的 SQE | ✓ |
| FREEZE | 0x0005 | 冻结 ring | ring->frozen = true | ✓ |
| CAP_REQUEST | 0x0010 | 能力请求 | Agent 向 sec_d 请求 Badge（自举） | ✗ |
| CAP_RESPONSE | 0x0011 | 能力响应 | sec_d 返回编译好的 Badge | ✓ |

### 6.3 syscall 12 → 4 映射

| 保留的 4 个 syscall | 注册号 | 职责 |
|---|---|---|
| airy_sys_call | 512 | Capability Invocation（sec_d 编译 Badge） |
| airy_sys_rovol_ctl | 513 | MemoryRovol 控制 |
| airy_sys_sched_ctl | 514 | sched_tac 调度策略控制 |
| airy_sys_clt_notify | 515 | 客户端事件通知 |

### 6.4 fastpath 7 态状态机

```
IDLE ──▶ CHECK ──┬─▶ FAST_SEND ──▶ IDLE     (发送完成，~158ns)
                 ├─▶ SLOW_SEND ──▶ IDLE     (异步发送，io-wq)
                 ├─▶ FAST_RECV ──▶ IDLE     (接收完成)
                 ├─▶ SLOW_RECV ──▶ IDLE     (异步接收，等 CQE)
                 ├─▶ BATCH     ──▶ IDLE     (批量)
                 ├─▶ CANCEL                 (取消)
                 └─▶ ERROR                  (错误)
```

### 6.5 错误码空间

```c
/* IPC 码空间 [-41, -70] */
AIRY_EIPC_MAGIC    (-41)  AIRY_EIPC_OPCODE   (-42)
AIRY_EIPC_PAYLOAD  (-43)  AIRY_EIPC_HDRSIZE  (-44)
AIRY_EIPC_RESERVED (-45)  AIRY_EIPC_FLAGS    (-46)
AIRY_EIPC_NOTSUPP  (-47)  AIRY_EIPC_KFIFO    (-48)
AIRY_EIPC_RECLAIM  (-49)  AIRY_EIPC_CONTEXT  (-50)
AIRY_EIPC_CRC32    (-51)  AIRY_EIPC_TIMEOUT  (-52)

/* Capability 码空间 [-71, -100] */
AIRY_ECAP_MISSING    (-71)  AIRY_ECAP_REVOKED    (-72)
AIRY_ECAP_EXPIRED    (-73)  AIRY_ECAP_MISMATCH   (-74)
AIRY_ECAP_LSM_DENIED (-75)  AIRY_ECAP_RADIX_MISS  (-76)
AIRY_ECAP_STATIC_KEY (-77)  AIRY_ECAP_BADGE       (-78)
AIRY_ECAP_EPOCH      (-79)  AIRY_ECAP_FORGED      (-80)
AIRY_ECAP_PERM       (-81)  AIRY_ECAP_FROZEN      (-82)

/* Fault 码空间 [0x1000, 0x1FFF] */
AIRY_FAULT_CAP_FORGED    (0x1001)
AIRY_FAULT_CAP_LEAK      (0x1002)
AIRY_FAULT_RING_CORRUPT  (0x1003)
```

---

## §7 17 份文档同步清单

### 7.1 P0 同步（7 份，必须立即执行）

| # | 文档 | 修改内容 |
|---|------|---------|
| 1 | [10-unify-design.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/10-unify-design.md) §8 | A-IPC 章节：双平面 → 单平面 + Capability Folding |
| 2 | [10-unify-design.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/10-unify-design.md) §10 | SSoT 新增 "A-IPC 采用 Capability Folding" |
| 3 | [30-interfaces/01-syscalls.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/01-syscalls.md) | syscall 表 12 → 4，§1.4 重写 |
| 4 | [30-interfaces/02-ipc-protocol.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/02-ipc-protocol.md) | Layout C v4，opcode 表新增 FREEZE/CAP_REQUEST/CAP_RESPONSE |
| 5 | [30-interfaces/07-ipc-fastpath.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/07-ipc-fastpath.md) | C-S9 实现，7 态状态机 |
| 6 | [120-cross-project-code-sharing.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md) §2.7 | [SC] ipc.h Layout C v4 定义 |
| 7 | [30-interfaces/08-sc-error-contract.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/08-sc-error-contract.md) §2.4 | Capability 码空间新增 -78~-82 + Fault 码 + [DSL] 码 |

### 7.2 P1 同步（7 份）

| # | 文档 | 修改内容 |
|---|------|---------|
| 8 | [110-security/03-capability-model.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/110-security/03-capability-model.md) | radix tree → Epoch + 静态数组 |
| 9 | [10-architecture/11-degraded-survival-layer.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/11-degraded-survival-layer.md) §2.2 | [DSL] ipc.h 降级块：capability_badge=0 |
| 10 | [40-dataflows/03-ipc-flow.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/40-dataflows/03-ipc-flow.md) | 消除控制面数据流，数据面自治三原则重定义 |
| 11 | [20-modules/11-unified-config.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/11-unified-config.md) | 新增 A-IPC 配置项章节 |
| 12 | [20-modules/09-kernel-agent-supervisor.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/09-kernel-agent-supervisor.md) | 新增 FREEZE opcode 章节 + Badge 撤销解耦 |
| 13 | [110-security/02-lsm-framework.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/110-security/02-lsm-framework.md) | Badge 校验是 fastpath 内联 |
| 14 | [110-security/01-security-daemon.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/110-security/01-security-daemon.md) | sec_d Badge 编译职责 |

### 7.3 P2 同步（3 份）

| # | 文档 | 修改内容 |
|---|------|---------|
| 15 | [170-performance/03-ipc-performance.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/170-performance/03-ipc-performance.md) | fastpath 延迟数值更新（~158ns） |
| 16 | [20-modules/10-user-supervisor-daemon.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/10-user-supervisor-daemon.md) | Badge 撤销解耦说明 |
| 17 | [30-interfaces/08-sc-error-contract.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/08-sc-error-contract.md) | [DSL] 码空间具体值 |

---

## §8 实施路线图

### 8.1 四阶段实施计划

```
Phase 0: 文档同步（17 份）
  ├─ P0 同步: 7 份（必须先完成）
  ├─ P1 同步: 7 份（Phase 1 后完成）
  └─ P2 同步: 3 份（Phase 2 后完成）

Phase 1: [SC] 头文件更新
  ├─ kernel/include/airymax/ipc.h
  ├─ kernel/include/airymax/error.h
  └─ [SC] 双端 CI 更新

Phase 2: fastpath 实现
  ├─ kernel/ipc/airy_uring_cmd.c
  ├─ kernel/security/airy_cap.c
  └─ 控制面 syscall 重写

Phase 3: 验证
  ├─ CBMC 全函数验证
  ├─ 性能基准测试
  └─ 安全测试

Phase 4: 集成与文档定稿
  ├─ 12 daemon 通信网格仿真
  ├─ 文档最终同步
  └─ 发布 v0.1.1
```

### 8.2 Phase 0: 文档同步（先行）

**目标**：在写第一行代码前，完成所有文档同步，确保设计 SSoT。

**P0 同步任务（7 份，必须先完成）**：

| 任务 | 文档 | 关键修改 | 验收标准 |
|------|------|---------|---------|
| 0.1 | 10-unify-design.md §8 | 双平面 → 单平面架构图 | §8 描述单平面 + Capability Folding |
| 0.2 | 10-unify-design.md §10 | SSoT 新增声明 | §10 包含 6 条硬约束摘要 |
| 0.3 | 01-syscalls.md | syscall 表 12→4 | 仅 4 个 syscall，附 12→4 映射表 |
| 0.4 | 02-ipc-protocol.md | Layout C v4 | 128B 定义 + _Static_assert |
| 0.5 | 07-ipc-fastpath.md | C-S9 + 7 态状态机 | fastpath 完整 C 代码 |
| 0.6 | 120-cross-project-code-sharing.md §2.7 | [SC] ipc.h | Layout C v4 完整定义 |
| 0.7 | 08-sc-error-contract.md §2.4 | Capability 码空间 | -78~-82 + Fault 码 |

### 8.3 Phase 1: [SC] 头文件更新

**目标**：落地 [SC] 共享契约层的物理载体。

```c
// kernel/include/airymax/ipc.h （35 号 §2.1 完整定义）
// kernel/include/airymax/error.h （35 号 §8.1 完整定义）
```

**任务清单**：
- 任务 1.1: 创建 `kernel/include/airymax/ipc.h`（Layout C v4）
- 任务 1.2: 创建 `kernel/include/airymax/error.h`（错误码空间）
- 任务 1.3: 更新 `sc-dual-ci.yml`（双端字节级校验）

**验收标准**：
- `_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128)` 通过
- sc-dual-ci.yml 在 agentrt 和 agentrt-linux 双端校验通过
- magic 值 `0x41524531` 冻结

### 8.4 Phase 2: fastpath 实现

**目标**：实现 A-IPC fastpath 完整代码。

**任务清单**：

```
任务 2.1: kernel/ipc/airy_uring_cmd.c
  ├─ airy_uring_cmd() 入口函数
  ├─ airy_ipc_validate() C-S0~C-S11 校验链
  ├─ airy_ipc_can_fast_deliver() FAST_SEND 判断
  ├─ airy_ipc_deliver_fast() FAST_SEND 路径（锁内 ~90ns）
  └─ airy_ipc_deliver_full() SLOW_SEND 路径（io-wq）

任务 2.2: kernel/security/airy_cap.c
  ├─ agent_caps[1024] 静态数组
  ├─ airy_global_epoch (atomic_t)
  ├─ airy_cap_epoch_get() / airy_cap_epoch_increment()
  ├─ airy_cap_badge_compile()（sec_d 调用）
  ├─ airy_cap_badge_revoke()（sec_d 调用）
  ├─ airy_cap_badge_ok()（C-S9 内联）
  └─ airy_cap_has_perm()

任务 2.3: 控制面 syscall
  ├─ airy_sys_call() 重写（COMPILE_BADGE/REVOKE_BADGE/LSM_CTL）
  ├─ 移除 airy_sys_send/recv/reply/delegate/mint/revoke/call_batch
  └─ 保留 airy_sys_rovol_ctl/sched_ctl/clt_notify
```

**验收标准**：
- fastpath 100 行代码规模
- 锁内时间 ≤ 158ns（NONBLOCK fastpath）
- 锁内无 wake_up / kmalloc(GFP_KERNEL)
- C-S9 不可被绕过（代码审查 + 静态分析）

### 8.5 Phase 3: 验证

**目标**：科学验证设计的正确性、性能、安全性。

**任务清单**：

```
任务 3.1: CBMC 全函数验证
  ├─ airy_uring_cmd() CBMC 验证脚本
  ├─ 验证 C-S9 不可绕过
  ├─ 验证 agent_caps[] 与 kfifo 独立
  ├─ 验证 check-and-return 模式
  └─ 验证锁内无阻塞操作

任务 3.2: 性能基准测试
  ├─ 128B 消息 P50/P99 延迟
  ├─ 128B 消息吞吐量
  ├─ 12 daemon 通信网格死锁检测
  ├─ uring_lock 争用压力测试
  └─ CFS 迁移 + SLOW_PATH 退化测试

任务 3.3: 安全测试
  ├─ Badge 伪造攻击测试
  ├─ Random Tag 暴力枚举测试
  ├─ 时序侧信道测试
  └─ agent_caps[] 越界访问测试
```

**验收标准**：
- CBMC 验证全部通过
- P50 ≤ 5μs, P99 ≤ 20μs（170 号 SLO）
- 吞吐 ≥ 1M msg/s
- 12 daemon 通信网格无死锁
- Badge 伪造攻击不可行

### 8.6 Phase 4: 集成与文档定稿

**目标**：集成到 agentrt-linux 完整系统，发布 v0.1.1。

**任务清单**：

```
任务 4.1: 12 daemon 通信网格仿真
  ├─ sec_d / cogn_d / VFS_d / net_d 等 12 个 daemon 原型
  ├─ CAP_REQUEST 自举流程验证
  ├─ Badge 撤销 + atomic_inc 验证
  └─ [DSL] 降级模式验证

任务 4.2: 文档最终同步
  ├─ P1 同步（7 份）
  └─ P2 同步（3 份）

任务 4.3: 发布 v0.1.1
  ├─ [SC] 头文件冻结
  ├─ magic 值冻结
  └─ 向后兼容承诺
```

---

## §9 风险与缓解

### 9.1 已识别风险（10 项）

| # | 风险 | 严重度 | 缓解措施 | 状态 |
|---|------|:---:|---------|:---:|
| R1 | Badge 伪造攻击 | P0 | 随机标签 + 内核静态数组（30 号修复） | ✓ 已缓解 |
| R2 | uring_lock 持有 wake_up | P0 | NONBLOCK + io-wq 接管（33 号修复） | ✓ 已缓解 |
| R3 | seL4 架构级隔离丧失 | P1 | 数据结构隔离 + CBMC（31 号论证） | ✓ 可接受 |
| R4 | 原子性丢失（seL4 Call 语义） | P1 | request_id 模式（异步可接受） | ✓ 可接受 |
| R5 | [SC] 双端同步更新成本 | P2 | sc-dual-ci.yml 机制 | ✓ 可控 |
| R6 | Epoch u16 溢出 | P2 | 0.1.1 不会触及；1.0.1 可扩展 u32 | ✓ 可控 |
| R7 | Random Tag 32 位暴力枚举 | P2 | 100 次失败触发警报 | ✓ 可控 |
| R8 | agent_caps[1024] 容量限制 | P2 | 0.1.1 Agent < 100 | ✓ 可控 |
| R9 | CBMC 验证工具链未实证 | P2 | Phase 3 任务 3.1 实证 | ⏳ 待验证 |
| R10 | 12 daemon 通信网格未仿真 | P2 | Phase 3 任务 3.2 实证 | ⏳ 待验证 |

### 9.2 不可接受的风险

```
经过 33 份审查报告 + 34/35/36 号三份文档的逐项验证:
  没有发现不可接受的风险。

所有 P0 风险已缓解（R1, R2）。
所有 P1 风险经过论证可接受（R3, R4）。
所有 P2 风险可控（R5-R10）。
```

---

## §10 验收标准

### 10.1 设计验收（Phase 0 完成时）

| # | 验收项 | 验收标准 | 状态 |
|---|--------|---------|:---:|
| D-1 | 6 条硬约束 H1-H6 | 全部满足 | ✓ |
| D-2 | 7 颗螺丝 | 全部拧掉 | ✓ |
| D-3 | 三大物理鸿沟 | 全部修复 | ✓ |
| D-4 | IRON-9 v3 四层模型 | 完全对齐 | ✓ |
| D-5 | 五模块自洽性 | 优 | ✓ |
| D-6 | 17 份文档同步 | 全部完成 | ⏳ |

### 10.2 实现验收（Phase 2 完成时）

| # | 验收项 | 验收标准 |
|---|--------|---------|
| I-1 | fastpath 代码规模 | ≤ 100 行 |
| I-2 | 锁内时间 | ≤ 158ns（NONBLOCK fastpath） |
| I-3 | 锁内操作 | 无 wake_up / kmalloc(GFP_KERNEL) |
| I-4 | C-S9 不可绕过 | 代码审查 + 静态分析通过 |
| I-5 | syscall 数量 | 4 个（12→4） |
| I-6 | [SC] 头文件 | ipc.h + error.h 创建完成 |

### 10.3 验证验收（Phase 3 完成时）

| # | 验收项 | 验收标准 |
|---|--------|---------|
| V-1 | CBMC 全函数验证 | 全部属性通过 |
| V-2 | P50 延迟 | ≤ 5μs |
| V-3 | P99 延迟 | ≤ 20μs |
| V-4 | 吞吐 | ≥ 1M msg/s |
| V-5 | 12 daemon 死锁检测 | 无死锁 |
| V-6 | Badge 伪造攻击 | 不可行 |

### 10.4 集成验收（Phase 4 完成时）

| # | 验收项 | 验收标准 |
|---|--------|---------|
| C-1 | 12 daemon 通信网格 | 仿真通过 |
| C-2 | CAP_REQUEST 自举 | 验证通过 |
| C-3 | Badge 撤销 | atomic_inc 立即生效 |
| C-4 | [DSL] 降级模式 | 可生存 |
| C-5 | 文档同步 | 17 份全部完成 |
| C-6 | v0.1.1 发布 | [SC] 冻结 + magic 冻结 |

---

## §11 下一步详细行动计划

### 11.1 立即行动（本周内）

```
Step 1: 启动 Phase 0 P0 文档同步（7 份）
  ├─ 1.1 更新 10-unify-design.md §8（A-IPC 章节重写）
  ├─ 1.2 更新 10-unify-design.md §10（SSoT 新增声明）
  ├─ 1.3 更新 30-interfaces/01-syscalls.md（syscall 12→4）
  ├─ 1.4 更新 30-interfaces/02-ipc-protocol.md（Layout C v4）
  ├─ 1.5 更新 30-interfaces/07-ipc-fastpath.md（C-S9 + 7 态）
  ├─ 1.6 更新 120-cross-project-code-sharing.md §2.7（[SC] ipc.h）
  └─ 1.7 更新 30-interfaces/08-sc-error-contract.md §2.4（错误码）

Step 2: 创建实施 TODO 清单
  ├─ 2.1 创建 Phase 1-4 详细任务清单
  ├─ 2.2 创建文件级修改清单
  └─ 2.3 创建验收检查清单

Step 3: 建立实施基线
  ├─ 3.1 确认 agentrt-linux 仓库结构
  ├─ 3.2 确认 kernel/include/airymax/ 目录
  └─ 3.3 确认 sc-dual-ci.yml 配置
```

### 11.2 短期行动（2 周内）

```
Step 4: 完成 Phase 1 [SC] 头文件更新
  ├─ 4.1 创建 kernel/include/airymax/ipc.h
  ├─ 4.2 创建 kernel/include/airymax/error.h
  └─ 4.3 更新 sc-dual-ci.yml

Step 5: 完成 Phase 0 P1 文档同步（7 份）
  ├─ 5.1 更新 110-security/03-capability-model.md
  ├─ 5.2 更新 10-architecture/11-degraded-survival-layer.md §2.2
  ├─ 5.3 更新 40-dataflows/03-ipc-flow.md
  ├─ 5.4 更新 20-modules/11-unified-config.md
  ├─ 5.5 更新 20-modules/09-kernel-agent-supervisor.md
  ├─ 5.6 更新 110-security/02-lsm-framework.md
  └─ 5.7 更新 110-security/01-security-daemon.md
```

### 11.3 中期行动（4 周内）

```
Step 6: 完成 Phase 2 fastpath 实现
  ├─ 6.1 实现 kernel/ipc/airy_uring_cmd.c
  ├─ 6.2 实现 kernel/security/airy_cap.c
  └─ 6.3 重写控制面 syscall

Step 7: 启动 Phase 3 验证
  ├─ 7.1 CBMC 验证脚本
  ├─ 7.2 性能基准测试框架
  └─ 7.3 安全测试用例

Step 8: 完成 Phase 0 P2 文档同步（3 份）
  ├─ 8.1 更新 170-performance/03-ipc-performance.md
  ├─ 8.2 更新 20-modules/10-user-supervisor-daemon.md
  └─ 8.3 更新 08-sc-error-contract.md [DSL] 码空间
```

### 11.4 长期行动（6 周内）

```
Step 9: 完成 Phase 3 验证
  ├─ 9.1 CBMC 全函数验证通过
  ├─ 9.2 性能 SLO 达标
  └─ 9.3 安全测试通过

Step 10: 启动 Phase 4 集成
  ├─ 10.1 12 daemon 通信网格仿真
  ├─ 10.2 CAP_REQUEST 自举验证
  └─ 10.3 [DSL] 降级模式验证

Step 11: 发布 v0.1.1
  ├─ 11.1 [SC] 头文件冻结
  ├─ 11.2 magic 值冻结
  └─ 11.3 向后兼容承诺
```

---

## §12 实施治理

### 12.1 实施原则

```
原则 1: 文档先行
  - 任何代码修改前，必须先更新文档
  - 文档是 SSoT，代码是文档的实现

原则 2: [SC] 优先
  - [SC] 头文件是契约，必须先冻结
  - magic 值一经发布即冻结

原则 3: 渐进式实施
  - Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4
  - 每个 Phase 完成后才进入下一个

原则 4: 验证驱动
  - 每个 Phase 都有明确的验收标准
  - 验收未通过不进入下一个 Phase

原则 5: 风险可控
  - 所有 P0 风险必须已缓解
  - 所有 P1 风险必须经过论证
  - 所有 P2 风险必须有缓解措施
```

### 12.2 实施检查点

| 检查点 | 时机 | 检查内容 | 通过标准 |
|--------|------|---------|---------|
| CP-0 | Phase 0 完成 | 17 份文档同步 | 全部完成 |
| CP-1 | Phase 1 完成 | [SC] 头文件 | 双端 CI 通过 |
| CP-2 | Phase 2 完成 | fastpath 代码 | 代码审查通过 |
| CP-3 | Phase 3 完成 | 验证 | 全部验收通过 |
| CP-4 | Phase 4 完成 | 集成 | v0.1.1 发布 |

### 12.3 回滚策略

```
如果在任何检查点未通过:

CP-0 未通过: 修正文档，重新检查
CP-1 未通过: 修正 [SC] 头文件，重新检查
CP-2 未通过: 修正 fastpath 代码，重新检查
CP-3 未通过:
  - CBMC 失败: 修正代码，重新验证
  - 性能未达标: 分析瓶颈，优化或调整 SLO
  - 安全漏洞: 评估严重度，P0 立即修复，P1 评估后决定
CP-4 未通过: 修正集成问题，重新检查

极端情况回退:
  - 如果发现根本性设计缺陷
  - 回退到 Phase 0，重新设计
  - 但 6 条硬约束 H1-H6 不可妥协
```

---

## §13 决策总结

### 13.1 一句话决策

**用户决定采用 Capability Folding 重构 A-IPC，作为 AirymaxOS 的第一块基石，按 Phase 0-4 渐进式实施，17 份文档同步更新，6 条硬约束不可妥协，所有风险可控。**

### 13.2 决策的工程意义

```
1. A-IPC 从"双平面外挂校验"变为"单平面内生校验"
2. AirymaxOS 第一块基石形状确定
3. 后续设计（sched_tac/MemoryRovol/sec_d/cogn_d）建立在此基石之上
4. 0.1.1 版本的核心工程目标明确
5. IRON-9 v3 四层模型在 A-IPC 上完整落地
```

### 13.3 决策的哲学意义

```
"产品中看不见的部分也应该像其外表一样精美"
"简单就是美"

Capability Folding 是乔布斯/艾夫设计哲学在内核工程上的落地:
  - 7 颗"看不见的螺丝"全部拧掉
  - 最终形态: 1 平面 + 1 Badge + 1 atomic_inc + 1 opcode + 1 CRC32
  - 真正的简约，不是摒弃杂乱，而是对复杂事物的精髓进行深度挖掘和精准提炼
```

### 13.4 立即开始

```
下一步: 启动 Phase 0 P0 文档同步（7 份）
  ├─ 任务 1.1: 更新 10-unify-design.md §8
  ├─ 任务 1.2: 更新 10-unify-design.md §10
  ├─ 任务 1.3: 更新 30-interfaces/01-syscalls.md
  ├─ 任务 1.4: 更新 30-interfaces/02-ipc-protocol.md
  ├─ 任务 1.5: 更新 30-interfaces/07-ipc-fastpath.md
  ├─ 任务 1.6: 更新 120-cross-project-code-sharing.md §2.7
  └─ 任务 1.7: 更新 30-interfaces/08-sc-error-contract.md §2.4

"第一块基石已确定。现在开始建造。"
```

---

## §14 附录：完整文档索引

### 14.1 核心设计文档

| # | 文档 | 性质 | 行数 |
|---|------|------|------|
| 34 | [34-overall-perspective-scientific-judgment.md](file:///home/spharx/SpharxWorks/airymaxhub/docs-closed/agentrt-linux/00-reviews/_review_v2.2/34-overall-perspective-scientific-judgment.md) | 科学论证 | 612 |
| 35 | [35-aipc-final-redesign.md](file:///home/spharx/SpharxWorks/airymaxhub/docs-closed/agentrt-linux/00-reviews/_review_v2.2/35-aipc-final-redesign.md) | 最终设计 | 1806 |
| 36 | [36-unify-design-comprehensive-check.md](file:///home/spharx/SpharxWorks/airymaxhub/docs-closed/agentrt-linux/00-reviews/_review_v2.2/36-unify-design-comprehensive-check.md) | 五模块检查 | 870 |
| 37 | 本文 | 决策总纲 | - |

### 14.2 关键审查报告

| # | 文档 | 关键贡献 |
|---|------|---------|
| 25 | 25-aipc-fundamental-refactoring.md | "IPC 就是能力校验" |
| 27 | 27-aipc-final-design.md | Badge 64-bit Native Word |
| 28 | 28-jobs-ive-simplicity-review.md | 7 颗螺丝 |
| 30 | 30-critical-vulnerability-review.md | Random Tag 防伪造 |
| 31 | 31-coupling-isolation-review.md | 数据结构隔离 |
| 33 | 33-physical-bridge-review.md | NONBLOCK + io-wq |

### 14.3 AirymaxOS 文档（需同步）

| 文档 | 优先级 | 修改内容 |
|------|:---:|---------|
| 10-unify-design.md §8/§10 | P0 | A-IPC 章节 + SSoT 声明 |
| 30-interfaces/01-syscalls.md | P0 | syscall 12→4 |
| 30-interfaces/02-ipc-protocol.md | P0 | Layout C v4 |
| 30-interfaces/07-ipc-fastpath.md | P0 | C-S9 + 7 态 |
| 50-engineering-standards/120-cross-project-code-sharing.md §2.7 | P0 | [SC] ipc.h |
| 30-interfaces/08-sc-error-contract.md | P0 | 错误码空间 |
| 110-security/03-capability-model.md | P1 | Epoch + 静态数组 |
| 10-architecture/11-degraded-survival-layer.md §2.2 | P1 | [DSL] 降级块 |
| 40-dataflows/03-ipc-flow.md | P1 | 消除控制面数据流 |
| 20-modules/11-unified-config.md | P1 | A-IPC 配置项 |
| 20-modules/09-kernel-agent-supervisor.md | P1 | FREEZE opcode |
| 110-security/02-lsm-framework.md | P1 | Badge 校验内联 |
| 110-security/01-security-daemon.md | P1 | sec_d Badge 编译 |
| 170-performance/03-ipc-performance.md | P2 | 延迟数值 |
| 20-modules/10-user-supervisor-daemon.md | P2 | Badge 撤销解耦 |

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. | Capability Folding 决策总纲与实施路线图 | v1.0 | 2026-07-18
