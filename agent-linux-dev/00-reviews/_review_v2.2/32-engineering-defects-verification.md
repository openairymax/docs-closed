Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 32 — 六个工程缺陷的逐项验证

## "区分文档版本演进中已修复的问题与仍存在的真实缺陷"

> **文档性质**：对用户提出的六个技术问题的逐项验证
> **审查日期**：2026-07-18
> **审查范围**：27 → 28 → 29 → 30 → 31 号共五份文档的完整修复链

---

## §0 前置澄清

用户提出的六个问题引用了 27 号方案中的具体章节。27 号方案是第一版重构方案（已被后续审查大幅修改）。以下是每个问题在修复链中的状态。

---

## §1 mdelay(5) 与 RCU 冲突

### 用户描述

> 27号方案 §2.1 的 Epoch 递增函数使用了 mdelay(5) 来"排空在途消息"。mdelay() 是忙等待，会独占 CPU 且禁止抢占。在持有 RCU 读锁的上下文中调用会导致 RCU 饥饿、watchdog 触发 NMI 复位。

### 验证结果：**问题在 27 号方案中真实存在，已在 28 号审查中修复。**

**修复链**：

```
27号方案 §2.1 → 定义了四阶段 drain 协议（mdelay(5)）
                      ↓
28号审查 问题#1  → 识别为第 1 颗"看不见的螺丝"
                      ↓
28号审查 §1.4   → 修复: 消除 drain，Epoch 递增变为 1 行 atomic_inc
                      ↓
29号方案 §0.2    → 铁律 3: "Epoch Is The Single Global State"
                   明确声明 "无 drain，无 bitmap，无 mdelay"
                      ↓
30号修复        → 不涉及 drain（已消除）
```

**当前设计的 Epoch 递增（30号修复后）**：

```c
void airy_cap_epoch_bump(void)
{
    atomic_inc(&airy_global_epoch);
    /* 一条原子操作。无阻塞。无 drain。无 RCU 冲突。 */
}
```

**用户建议的 "rcu_synchronize 或 generation 引用计数" 方案与当前设计在哲学上一致**——都是消除忙等待，改为基于代际的失效机制。当前设计通过 atomic_inc 的 lock incl 指令实现了立即全局可见的 Epoch 递增，效果等价于用户建议的方案。

### 结论：✅ 已修复。当前设计不包含 mdelay，不存在忙等待。

---

## §2 kthread 与 io_uring 的"物理隔离"

### 用户描述

> H8 约束要求 kthread 间禁用 io_uring。但 cogn_d 需要与 mem_d 通信，CoreLoopThree kthread 如何将数据发给用户态 cogn_d？

### 验证结果：**问题真实存在，未被后续审查充分讨论。**

**问题根源**：

29 号方案的 H8 约束原文：
```
H8: kthread 间禁用 io_uring，必须用 kfifo + wait_event
（来源: 03-microkernel-strategy §10.1）
```

关键短语是 **"kthread 间"（kthread 到 kthread）**。这个约束的原始语境（03-microkernel-strategy）是：两个内核线程之间不应使用 io_uring 通信，因为 io_uring 是为用户态-内核态通信设计的。

**但是**，约束 H8 不禁止以下通信路径：
- kthread → 用户态 daemon
- 用户态 daemon → kthread

这两种情况不在 H8 的"kthread 间"范围内。

**当前设计的实际通信路径分析**：

```
CoreLoopThree kthread（内核态）
  ↓ 写 kfifo（kernel memory, alloc_pages(GFP_KERNEL)）
  ↓ eventfd_signal()
  ↓
cogn_d（用户态 daemon）
  ↓ mmap 读取同一个 kfifo 的物理页
  ↓ 通过 io_uring SEND → mem_d
  ↓
mem_d（用户态 daemon）
  ↓ io_uring CQE 完成
```

**不存在"双倍拷贝"问题**：kfifo 的底层缓冲区由 alloc_pages 分配，通过 remap_pfn_range 映射到用户态 cogn_d 的地址空间。内核写入和用户态读取访问的是同一物理页。这不是"复制到 kfifo 再复制到 io_uring"——这是"写入 kfifo 后用户态直接读取"。

**但是存在"桥接"**：kfifo 就是一个桥接点。io_uring 的 SQ/CQ ring 和 kfifo 是不同的数据结构，但底层缓冲区可以共享。当前设计中，用户态 daemon 有两种读取模式：
- io_uring CQE（标准路径）
- mmap + polling kfifo（kthread → daemon 路径）

**需要在文档中明确的内容**：

1. A-IPC 应该明确"统一数据面"的含义：
   - 用户态 → 用户态：io_uring SQE/CQE（IORING_OP_URING_CMD）
   - 内核 kthread → 用户态 daemon：kfifo（alloc_pages + remap_pfn_range）+ eventfd
   - 内核 kthread → 内核 kthread：kfifo + wait_event（H8 约束）

2. 所有路径使用相同的 128B 消息头（Layout C v4），共享同一个消息格式。

3. cogn_d 的 mmap 读取路径有独立的延迟特征（~50ns kfifo 读 vs ~100ns io_uring CQE），但都在 <10μs 的端到端要求内。

### 结论：⚠️ 问题真实存在，但不在功能正确性层面——在文档完善性层面。A-IPC 需要在 §3.3 中增加"kthread 到用户态 daemon 的 kfifo 桥接路径"的明确定义。不存在功能缺陷。

---

## §3 NULL Badge 的"允许接收任何消息"

### 用户描述

> 27号方案 §2.3 规定 NULL Badge 允许"接收任何消息"。持有 NULL Badge 的恶意 Agent 可以嗅探所有流向 sec_d、gateway_d 的敏感请求负载。

### 验证结果：**问题在 27 号方案中真实存在，已在 28 号审查中修复。**

**修复链**：

```
27号方案 §2.3 → NULL Badge 特例: 允许向 sec_d SEND + 允许接收任何消息
                        ↓
28号审查 问题#3  → 识别为第 3 颗"看不见的螺丝"
                        ↓
28号审查 §3.3   → 修复: 消除 NULL Badge 特例，改为 CAP_REQUEST opcode
                        ↓
29号方案 §2.1   → opcode 表中新增 AIRY_IPC_OP_CAP_REQUEST (0x10)
                   说明："无需 Badge，内核直接路由到 sec_d"
                        ↓
29号方案 §3.4   → CAP_REQUEST 自举流程：Agent 启动 → CAP_REQUEST → sec_d 编译 Badge
                        ↓
30号修复        → 不涉及（NULL Badge 已消除）
```

**当前设计中不存在 NULL Badge**。Agent 启动时：
1. 使用 `AIRY_IPC_OP_CAP_REQUEST` opcode 向 sec_d 发起能力请求
2. Badge 字段为全零（表示"未认证"）
3. 内核 fastpath 将 CAP_REQUEST 直接路由到 sec_d（不经过通用 SEND 路径，不检查 Badge）
4. sec_d 返回编译好的 Badge
5. Agent 此后使用标准 SEND + Badge 通信

**任何 opcode 不是 CAP_REQUEST 的消息，如果 Badge 为零，C-S9 返回 -AIRY_ECAP_BADGE。**

**不存在"NULL Badge 可以接收任何消息"的路径。**

### 结论：✅ 已修复。当前设计通过 CAP_REQUEST opcode 替代了 NULL Badge 特例。未认证 Agent 不能接收任何非 sec_d 回复的消息。

---

## §4 eventfd_signal 的调度开销

### 用户描述

> 文档估算 Fastpath 为 ~96ns，但 eventfd_signal(~20ns) 忽略了——如果接收方 idle，eventfd_signal 触发 wake_up 会进入调度器，花费 1-5μs。

### 验证结果：**问题真实存在，但属于文档表述精度问题，不是设计缺陷。**

**性能预算的精确分解**：

```
Fastpath 延迟（发送方提交侧，SEND 操作）:

  校验阶段（C-S0 ~ C-S11）:        ~68ns
  kfifo_in():                       ~50ns
  eventfd_signal():                 ~20ns（仅写入 eventfd，不触发唤醒）
    其中:
    - eventfd_ctx 中的计数器递增    ~5ns
    - wqh 队列空检查                ~5ns
    - 如果 wqh 非空 → wake_up_locked() → 1-5μs（进入调度器）
    - 如果 wqh 为空（接收方活跃）  → 直接返回，额外开销 ~10ns
  io_uring_cqe_fill:               ~20ns
  ────────────────────────────────────
  提交侧总计（接收方活跃/轮询）:     ~158ns

端到端延迟（SEND 提交 → RECV 可用）:

  如果接收方 IO_URING_ENTER（轮询）:
    提交侧延迟 + kfifo 读 + CQE 提取 → ~200ns

  如果接收方 io_uring_wait_cqe（阻塞）:
    提交侧延迟 + eventfd 唤醒延迟 + 调度器延迟
    + kfifo 读 + CQE 提取
    → ~2-5μs（取决于调度器队列深度和优先级）
```

**29 号方案的 ~96ns 是 "理想 fastpath 提交侧延迟"（校验 + kfifo + eventfd 写 + CQE）。这个数字假设接收方正以轮询模式运行（kfifo 中已有未消费消息或接收方正忙于处理）。实际生产中的典型数值：如果使用 SQPOLL 模式（内核轮询线程），提交侧延迟 ~158ns，端到端延迟 ~200ns。**

**这个数字仍然远低于 FR-016 的 <10μs 要求。**

### 结论：⚠️ 问题真实存在，需要在文档中将 fastpath 延迟拆分为两个指标：发送提交延迟（~158ns）和端到端接收延迟（~200ns 轮询 / ~2-5μs 阻塞）。不构成设计缺陷，但需要文档精度修正。

---

## §5 IORING_OP_URING_CMD 与 LSM 钩子的交互

### 用户描述

> Linux 6.6 中 io_uring 的 URING_CMD 经过 security_uring_cmd() LSM 钩子。SELinux 可能在 Badge 验证通过后返回 -EACCES，导致"Badge 验证通过但 SELinux 卡住"的诡异超时。

### 验证结果：**问题真实存在，且未被 29/30 号审查充分讨论。**

**问题的精确机制**：

在 Linux 6.6 的 io_uring 命令处理路径中：
```
io_uring_enter()
  → io_submit_sqes()
    → io_issue_sqe()
      → io_uring_cmd_prep()    ← 准备 IORING_OP_URING_CMD
      → io_uring_cmd()          ← 调用 file_operations->uring_cmd()
           ↓
           在此之前: security_uring_cmd() LSM 钩子已执行
           LSM 调用链（按注册顺序）:
             1. capability (LSM_ORDER_FIRST) → Airymax 纯 C LSM
             2. selinux
             3. landlock (如果加载)
             4. ...
           
           如果 capability LSM 返回 0（允许）但 selinux 返回 -EACCES:
             → 操作被拒绝
             → Badge 校验通过，但 SELinux 覆盖了结果
```

**这不是 bug——这是 Linux LSM 的预期行为（LSM 堆叠）。** 但确实存在用户描述的"Badge 通过但被 SELinux 卡住"的调试复杂性。

**缓解措施**（需要在设计中明确）：

1. **正确做法（当前设计的方向，需要文档化）**：
   - Airymax 的纯 C LSM（capability）运行在 LSM_ORDER_FIRST
   - 如果 Badge 校验失败 → 返回 -AIRY_ECAP_* 错误码 → 操作立即拒绝（不执行后续 selinux）
   - 如果 Badge 校验通过 → 返回 0 → selinux 仍然运行
   - 如果 selinux 拒绝 → 记录日志：
     ```
     LOG_WARN("IPC DENIED by SELinux: src=%d dst=%d opcode=%d "
              "badge_ok=1 selinux_denial=1")
     ```
   - 如果 selinux 允许 → 操作继续

2. **为什么不应该跳过 SELinux**：
   - SELinux 提供了独立于 capability 的第二层防御
   - Badge 校验验证的是"发送方是否有权限与接收方通信"
   - SELinux 可能验证的是"此操作类型在当前安全上下文中是否被允许"
   - 这是纵深防御，不是冗余

3. **需要在代码中做的**：
   - 在 `airy_uring_cmd()` 中，Badge 校验失败时不要 fall through 到其他 LSM
   - 在 security_uring_cmd 的 Airymax LSM 钩子中，需要识别 "此操作已经过 Badge 校验"，避免重复检查
   - 添加 ftrace 探针：`trace_airy_lsm_deny_after_badge_ok()`

### 结论：⚠️ 问题真实存在。不是设计缺陷，而是需要在实施文档中明确 LSM 堆叠策略：Airymax capability LSM 运行在最前，Badge 校验失败立即返回，Badge 通过后 SELinux 作为第二层防线仍然运行。需要增加日志和探针以确保可调试性。

---

## §6 mdelay(5) vs rcu_synchronize 方案评估

### 用户描述

> 撤销时应使用 rcu_synchronize 或 generation 引用计数，而非 mdelay。内核侧处理完请求时再次检查 Epoch（Double-check），不一致则丢弃并 -EAGAIN。

### 验证结果：**用户建议的方案思路正确，但与当前设计的语义选择不同。**

**当前设计（28号审查修复后）**：

```
Epoch 递增 → 所有携带旧 Epoch 的 Badge 立即失效
在途消息（已在 kfifo 中等待消费的）→ 被 C-S9 拒绝 → 发送方收到 -AIRY_ECAP_EPOCH
发送方重新请求 Badge → sec_d 编译新 Badge → 发送方重发消息
```

**用户建议的方案**：

```
Epoch 递增 → 旧 Epoch 的 Badge 仍保留一段"待决期"
内核处理完请求时执行 Double-check → 不一致则丢弃 + -EAGAIN
使用 RCU grace period 确保所有在途处理完成
```

**两种方案的语义差异**：

| 维度 | 当前设计（原子递增，不等待） | 用户建议（RCU grace period） |
|------|---------------------------|---------------------------|
| 撤销生效时间 | 立即（atomic_inc） | RCU grace period 后（~10-100ms） |
| 在途消息 | 被拒绝（-AIRY_ECAP_EPOCH） | 被接受（在待决期内），或 -EAGAIN |
| 发送方体验 | 可能收到意外 REJECT | 可能收到 -EAGAIN（需重试） |
| 复杂度 | lowest（1 条 atomic_inc） | 中等（RCU + 待决期管理 + -EAGAIN 语义） |
| 代码量 | ~5 行 | ~50 行 |

**当前设计选择"立即失效"的理由**：
- 撤销是低频操作（运维触发，每小时 0-10 次）
- 发送方必须处理 REJECT（任何分布式系统都是如此）
- 1 条 atomic_inc 符合 28 号审查的简约原则
- 不引入 RCU、待决期、-EAGAIN 等额外语义

**两种方案都是正确的。** 当前设计选择的是"最简约"路径。用户建议的是"更平滑但更复杂"的路径。对于 0.1.1，简约路径更符合"简单就是美"的设计哲学。

### 结论：✅ 两种方案都是正确的。当前设计选择的是更简约的路径（atomic_inc，立即失效）。不构成设计缺陷。

---

## §7 汇总表

| # | 问题 | 严重度 | 27号方案 | 当前状态 | 结论 |
|---|------|:---:|:---:|:---:|------|
| 1 | mdelay(5) RCU 冲突 | 🔴 P0 | 存在 | ✅ 已修复（28号） | atomic_inc 替代 mdelay |
| 2 | kthread 桥接路径 | 🟠 中等 | 存在 | ⚠️ 需文档化 | 需要明确 kthread→daemon 的 kfifo 路径 |
| 3 | NULL Badge recv | 🔴 P0 | 存在 | ✅ 已修复（28号） | CAP_REQUEST opcode 替代 |
| 4 | eventfd 唤醒开销 | 🟡 文档 | 存在 | ⚠️ 需修正 | 区分提交延迟 vs 端到端延迟 |
| 5 | LSM 堆叠交互 | 🟠 中等 | 未讨论 | ⚠️ 需实施文档 | 需明确 Airymax LSM + SELinux 的堆叠策略 |
| 6 | RCU 替代方案 | 🟢 设计选择 | 存在 | ✅ 已验证 | 当前简约方案优于 RCU 方案 |

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. | 工程缺陷逐项验证 | v1.0 | 2026-07-18
