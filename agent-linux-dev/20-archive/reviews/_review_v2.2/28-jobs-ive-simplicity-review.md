# 28 — 以乔布斯/艾夫设计哲学审查 A-IPC 重构方案

## "简约不是摒弃杂乱——简约是对复杂事物的精髓进行深度挖掘和精准提炼的结果"

> **文档性质**：对 27 号重构方案的哲学级工程审查
> **审查标准**：乔布斯/艾夫设计哲学——"产品中看不见的部分也应该像其外表一样精美"、"简单就是美"
> **核心问题**：当前的 A-IPC 重构方案是否做到了真正的简约，还是仅仅将复杂度从一个地方移到了另一个地方？

---

## 0. 审查框架

乔布斯和艾夫的哲学为内核工程审查提供了三个无法绕过的标准线：

```
标准 1: 深度理解
  "要做到真正的简约，就必须做到真正的深入。"
  → 问题：我们是否深入理解了 A-IPC 的本质？

标准 2: 隐藏螺丝测试
  "如果为了达到看不到一颗螺丝的目标，结果却做出一个极为烦琐的产品，反倒违背了初心。"
  → 问题：重构方案中是否存在"看不见的螺丝"？

标准 3: 精髓提炼
  "只有深入了解一个产品的本质和精髓，才能真正去芜存菁。"
  → 问题：我们提炼的是 A-IPC 的真正精髓，还是我们想象中的精髓？
```

---

## 1. 问题一：Epoch Drain — 最大的"看不见的螺丝"

### 1.1 问题描述

27 号方案的 Epoch 递增使用了"两阶段 drain 协议"：

```c
/* 阶段 1: 标记转换中 */
set_bit(type, epoch_transition);
smp_mb();

/* 阶段 2: 排空在途消息 — 在此阻塞 5ms */
mdelay(5);

/* 阶段 3: 递增 Epoch */
atomic_inc(&airy_cap_epoch[type]);
smp_mb();

/* 阶段 4: 清除转换标记 */
clear_bit(type, epoch_transition);
smp_mb();
```

### 1.2 隐藏螺丝测试

**这是典型的"看不到一颗螺丝"的问题。** 我们想要实现"能力撤销后立即生效"（看不到螺丝），于是引入了一个 5ms 的阻塞等待 + 四阶段状态机 + bitmap 转换标记（一个极为烦琐的实现）。

具体的问题链：
1. 撤销一个 Agent 的能力（一个管理操作）→ 调用 `airy_cap_epoch_increment()`
2. 这个调用阻塞了 5ms（在 Linux 内核中，5ms 是一次调度时间片）
3. 在这 5ms 内，所有 CPU 上的 fastpath 仍在处理旧 Epoch 的消息
4. 在这 5ms 内，新的消息仍在以旧 Epoch 排队进入 kfifo/ring buffer
5. 5ms 后，Epoch 递增——但此时又有新的"在途消息"进入了 ring buffer

**drain 永远不会完全清空——它只是等待了一个估计值。这不是一个精确的机制，而是一个尽力而为的启发式。**

更根本的问题：我们真的需要 drain 吗？

### 1.3 深度理解分析

**A-IPC 的能力撤销的精髓是什么？**

不是"立即阻止所有消息"，而是"确保不再有新的未授权消息被投递"。区别在于：
- "立即阻止所有消息"：需要 drain + 原子切换
- "确保不再有新的未授权消息被投递"：递增 Epoch 即可，drain 不需要

为什么？因为 Badge 的语义是"生成时的权限快照"——不是"持续有效的权限许可证"。

```
Agent A 的 Badge (Epoch=N, Perms=IPC_SEND)
  ↓
消息 M1 被发送（Badge Epoch=N）
  ↓
Epoch 递增为 N+1
  ↓
M1 到达接收方 → epoch check: N ≠ N+1 → REJECT
```

**这没有问题。** M1 被拒绝是因为它的 Epoch 已过期——这正是我们想要的"不再有新的未授权消息被投递"。Agent A 收到 REJECT，知道 Badge 过期了，重新向 sec_d 请求。如果权限已被撤销，sec_d 返回 DENY。

**drain 解决的真正问题是：发送方认为消息已发送，但接收方拒绝了它。这是一个"通知发送方"的问题，不是"阻止未授权消息"的问题。** drain 是在试图保证"发送方不会遇到意外的 REJECT"——但发送方总是应该准备处理 REJECT（网络会丢包、接收方会崩溃、权限会过期）。

### 1.4 精髓提炼后的简化

**消除 drain。** Epoch 递增变为一条原子操作：

```c
void airy_cap_epoch_increment(enum airy_cap_type type)
{
    atomic_inc(&airy_cap_epoch[type]);
    /* 完成。Epoch 递增立即全局可见（x86 lock incl）。无需 drain。无需 bitmap。无需 mdelay。 */
}
```

从 ~20 行（四阶段 + bitmap + smp_mb + mdelay）变为 **1 行**。这才是真正的简约。

代价：极少数的在途消息（在 ring buffer 中等待被消费的）会被拒绝。但这本来就是撤销的语义——被撤销的权限不应该再被使用。发送方会收到 REJECT，可以重新请求权限或处理失败。

---

## 2. 问题二：CRC32 不覆盖 capability_badge

### 2.1 问题描述

27 号方案的 CRC32 覆盖范围：

```
CRC32 覆盖: header[0:44) + payload
            ↑           ↑
            │           └── 从 offset 0 到 offset 44（不含）
            │               即 magic + opcode + flags + trace_id +
            │               timestamp_ns + src_task + dst_task + payload_len
            │
            └── 不覆盖 offset 44-61，即：
               capability_badge (offset 44, 8B) — 未覆盖
               seq_num          (offset 52, 4B) — 未覆盖
               negotiated_ver   (offset 56, 2B) — 未覆盖
               crc32 自身       (offset 58, 4B) — 未覆盖
```

**capability_badge 不受 CRC32 保护。Badge 中任何一位被翻转——无论因硬件错误还是恶意篡改——CRC32 都检测不到。**

### 2.2 隐藏螺丝测试

这是一个"因为文件结构而未被发现的设计漏洞"。CRC32 被放在头部后段，而它需要覆盖前面的字段——这是一个常见的实现陷阱。

### 2.3 修复

```
CRC32 覆盖范围改为: header[0:58) + payload
即覆盖 magic 到 negotiated_ver 的全部字段（包含 capability_badge, seq_num, negotiated_ver）

CRC32 自身（offset 58-61）不覆盖自身（循环依赖）
__future[66] 不覆盖（始终为零，无覆盖价值）
```

---

## 3. 问题三：NULL Badge — Fastpath 中的硬编码特例

### 3.1 问题描述

27 号方案的 fastpath 包含一个特殊分支：

```c
if (unlikely(badge == AIRY_NULL_BADGE)) {
    if (opcode == AIRY_IPC_OP_SEND && dst_task == sec_d_task_id)
        goto fast_send;  /* 仅允许向 sec_d 发送能力请求 */
    else if (opcode == AIRY_IPC_OP_SEND)
        return -AIRY_ECAP_PERM;  /* 不允许发送其他消息 */
}
```

### 3.2 隐藏螺丝测试

**每一条 "if (special_case)" 都是一颗螺丝。** 这里有三颗：
1. `badge == AIRY_NULL_BADGE` — 第一颗
2. `dst_task == sec_d_task_id` — 第二颗（硬编码了 sec_d 的特权地位）
3. `opcode == AIRY_IPC_OP_SEND` — 第三颗

fastpath 的理想形式应该是：

```c
if (!airy_cap_badge_ok(badge, cap_type, required))
    return -AIRY_ECAP_PERM;
/* 通过，继续 */
```

没有特例，没有硬编码的 dst_task。Badge 本身就应该编码了"允许向谁发送什么"的全部信息。

### 3.3 精髓提炼

**NULL Badge 的真正需求是什么？**

Agent 在获得正式 Badge 之前，需要能够：
1. 向 sec_d 请求能力（CAP_REQUEST）
2. 接收来自 sec_d 的能力响应（CAP_RESPONSE）

这不是"NULL Badge"的问题——这是"sec_d 是一个公开的服务端点，任何人都需要能向它发起能力请求"的问题。

**简化方案：将能力请求设计为 A-IPC 的一个内置操作，不需要 Badge。**

```
opcode = AIRY_IPC_OP_CAP_REQUEST  → 不需要 Badge，内核直接路由到 sec_d
opcode = AIRY_IPC_OP_CAP_RESPONSE → sec_d 通过此操作码返回编译好的 Badge

其他所有 opcode               → 需要 Badge
```

这样，fastpath 中不再是 `if (badge == NULL_BADGE && dst == sec_d)` 的特例——而是 `opcode == CAP_REQUEST` 的通用路由。消除了三颗螺丝。

---

## 4. 问题四：全局 Epoch 矛盾

### 4.1 问题描述

27 号方案中存在一个矛盾：

1. 声明使用"每种能力类型独立 Epoch"：`atomic_t airy_cap_epoch[AIRY_CAP_NR_TYPES]`
2. Badge 编译却使用"全局 max_epoch"：遍历所有类型，取最大 Epoch 作为 Badge 的 Epoch
3. 遗留问题中承认"0.1.1 使用全局 Epoch"

**代码和语义不一致：10 个独立 Epoch 存在，却只用最大值。**

### 4.2 隐藏螺丝测试

这种不一致说明：我们在设计的时候意识到"全局 Epoch 太粗"，所以设计了独立 Epoch；但又因为"独立 Epoch 太复杂"（Badge 需要携带多个 Epoch），所以退回到全局 Epoch。进退两难导致了一个半成品。

### 4.3 精髓提炼后的简化

**接受并明确定义为全局 Epoch。**

```c
/* 一个全局 Epoch。一个 atomic_t。 */
static atomic_t airy_global_epoch = ATOMIC_INIT(1);

u64 airy_cap_badge_compile(u32 cap_mask)
{
    u32 epoch = atomic_read(&airy_global_epoch);
    return ((u64)epoch << 32) | (u64)cap_mask;
}
```

从 10 个 atomic_t + 10 个类型的枚举 + for 循环取 max → **1 个 atomic_t。**

代价：撤销任何 Agent 的任何能力 → 全局 Epoch + 1 → 所有 Agent 的所有 Badge 失效 → 所有 Agent 需要重新请求 Badge。

**这个代价在 0.1.1 阶段是可接受的。** Agent 数量少（< 100），撤销频率低（运维操作），重新请求 Badge 是一个轻量操作（io_uring 往返，< 100μs）。

1.0.1 如需精细粒度，可以在 Badge 中使用位图编码每种类型的独立 Epoch：
```
per-type badge = (epoch_0 << 0) | (epoch_1 << 8) | ... | (epoch_9 << 72) | permissions
```
但这是 1.0.1 的优化，不是 0.1.1 的需求。

---

## 5. 问题五：未定义字段

### 5.1 seq_num 没有排序模型

```
"seq_num (4B) — 发送方单调递增序列号"
```

定义了一个字段却没有定义：
- 接收方如何处理乱序？
- 接收方如何处理丢号（gap）？
- seq_num 在 SEND_BATCH 中如何递增？
- seq_num 溢出（32-bit, 40 亿条消息）后如何处理？

一个没有完整语义定义的消息头字段，是一颗"只画在图纸上的螺丝"——它看起来很好，但实际上没有功能。

**修复建议**：在 0.1.1 阶段移除 seq_num。排序问题可以通过应用层协议（request_id / correlation_id）解决。当真正需要内核层排序保证时（1.0.1），增加带完整语义的排序机制。

### 5.2 negotiated_ver 没有握手协议

```
"negotiated_ver (2B) — 握手协商的协议版本"
```

定义了一个字段却没有定义：
- 握手协议是什么？
- 谁发起握手？
- 版本不匹配时回退到什么行为？
- 与 128B 头部的 Layout C 版本是什么关系？

**修复建议**：在 0.1.1 阶段移除 negotiated_ver。版本协商可以通过 io_uring 的 registered buffer 元数据区域完成，不需要占用消息头空间。或者——更简单的——使用 opcode 的高位或 flags 的高位编码版本号。

---

## 6. 问题六：SLOW_PATH 合并丢失语义

### 6.1 问题描述

27 号方案将 SLOW_SEND 和 SLOW_RECV 合并为 SLOW_PATH。但它们的语义不同：

- SLOW_SEND: payload > 128B 或跨 CPU → 发送方使用 io_uring 异步提交，不阻塞
- SLOW_RECV: 接收方等待 io_uring CQE → 接收方阻塞或 poll

合并后，状态转换不明确：从 SLOW_PATH 之后，是回到 IDLE（如果是 SEND）还是进入 FAST_RECV（如果是 RECV）？

### 6.2 修复

状态机应该是：

```
IDLE → CHECK → FAST_SEND → IDLE       (发送完成)
             → SLOW_SEND → IDLE       (异步发送)
             → FAST_RECV → IDLE       (接收完成)
             → SLOW_RECV → IDLE       (异步接收)
             → BATCH     → IDLE       (批量)
             → CANCEL                 (取消)
             → ERROR                  (错误)
```

SLOW_SEND 和 SLOW_RECV 的区别保留，因为它们返回 IDLE 的方式不同（SEND 是提交 SQE 后立即返回，RECV 是等待 CQE）。

---

## 7. 问题七：__future[66] 是 128B 设计中最大的"图纸螺丝"

### 7.1 问题描述

Layout C v2 留下了 66 个字节的 `__future[66]`——超过 50% 的消息头空间被标记为"保留"。

**对于定长 128B 消息头，每一字节都应该是精心设计的。66 字节的"未来保留"不是简约——是对当前设计的未完成状态的诚实承认。**

### 7.2 深度理解后的建议

在 0.1.1 阶段，消息头应该包含已完全定义的字段。不需要的字段不应该占据空间。简化后的 Layout C v2：

```
offset   0: magic            (4B)  0x41524531
offset   4: opcode           (2B)  SEND/RECV/SEND_BATCH/CANCEL/FREEZE/CAP_REQUEST
offset   6: flags            (2B)  ZEROCOPY/CAP_CARRY/COMPRESS/ENCRYPT
offset   8: trace_id         (8B)  OpenTelemetry
offset  16: timestamp_ns     (8B)  CLOCK_REALTIME
offset  24: src_task         (8B)  源 ID
offset  32: dst_task         (8B)  目标 ID
offset  40: payload_len      (4B)  负载长度
offset  44: capability_badge (8B)  Epoch<<32 | Permissions
offset  52: crc32            (4B)  覆盖 header[0:52) + payload
offset  56: __reserved[72]  (72B)  保留，必须为零
─────────────────────────────────────────────────
总计:   128B
```

移除了 seq_num（无定义）、negotiated_ver（无协议），仍保留未来扩展空间。

---

## 8. 总结：重构后的真正简约形态

### 8.1 找到的 7 颗"看不见的螺丝"

| # | 问题 | 严重度 | 修复 |
|---|------|:---:|------|
| 1 | Epoch drain: 5ms 阻塞 + 四阶段状态机 | ★★★ | 消除 drain，1 行 atomic_inc |
| 2 | CRC32 不覆盖 capability_badge | ★★★ | 覆盖范围扩展至 header[0:52) |
| 3 | NULL Badge 硬编码特例 | ★★ | opcode CAP_REQUEST 替代特殊判断 |
| 4 | 全局/独立 Epoch 矛盾 | ★★ | 明确定义为全局 Epoch（1 个 atomic_t） |
| 5 | seq_num + negotiated_ver 无协议 | ★★ | 移除，不在 0.1.1 引入未定义字段 |
| 6 | SLOW_PATH 合并丢失语义 | ★ | 保留 SLOW_SEND / SLOW_RECV 区分 |
| 7 | __future[66] 超过 50% 为保留 | ★ | 精简为 __reserved[72]，移除非必要字段 |

### 8.2 修复后的复杂度对比

```
重构前（当前 A-IPC）:
  控制面: 12 syscall, decode_and_invoke (~200行)
  数据面: io_uring CQE, cap_check_fast (~50行)
  能力模型: radix tree + per-CPU cache + IPI coherency (~300行)
  ────────────────────────────────────────────
  总复杂度: 高（双平面 + 缓存一致性）

27号方案（第一版重构）:
  数据面: io_uring + Badge, 7 态状态机 (~80行)
  能力模型: atomic_t epoch[10] + Badge (~80行)
  Epoch drain: 四阶段 + bitmap + mdelay + smp_mb (~20行)  ← 看不见的螺丝
  NULL Badge: fastpath 特例分支 (~5行)                     ← 看不见的螺丝
  未定义字段: seq_num + negotiated_ver                     ← 图纸螺丝
  ────────────────────────────────────────────
  总复杂度: 中（简化了但隐藏了复杂度）

28号方案（经过本审查修复）:
  数据面: io_uring + Badge, 7 态状态机 (~80行)
  能力模型: atomic_t global_epoch（1 行）+ Badge (~60行)
  能力请求: CAP_REQUEST opcode（无特例）
  CRC32: 完整覆盖 capability_badge
  无 drain，无 bitmap，无 mdelay
  无未定义字段
  ────────────────────────────────────────────
  总复杂度: 低（真正去芜存菁）
```

### 8.3 简约的最终体现

```
通信 = io_uring 数据面（唯一平面）
授权 = 1 个 Badge（嵌入消息头，shrift + AND）
撤销 = 1 条 atomic_inc（无阻塞，无 drain）
自举 = 1 个 CAP_REQUEST opcode（无特殊 Badge）
完整性 = 1 个 CRC32（覆盖 Badge）
管理器 = sec_d（编译 Badge，低频调用）
```

---

**七颗螺丝拧掉了。现在可以看见产品真正的轮廓。**

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
