# 26 — 第三方风险审查的逐条证伪分析

## "重构方案是否解决了这些问题，还是没有解决，还是制造了新问题？"

> **文档性质**：对第三方审查的五项风险，逐一证伪重构方案的有效性
> **审查方法**：对每一项风险：(1) 重构前的状态；(2) 重构声称的改善；(3) 严苛验证改善是否真实；(4) 是否存在残留风险或新引入的风险
> **前提**：证伪不是"证明方案正确"，而是"检验方案没有解决它声称解决的问题"

---

## 风险一：控制面同步阻塞与死锁风险

### 第三方描述
> 控制面使用类似 seL4 的同步阻塞 syscall。在 12 个守护进程的网格拓扑中，若 A 向 B 发送同步消息时 B 正阻塞等待 C，而 C 又在等待 A，就会形成死锁。

### 重构声称
> 消除 8 个 seL4 风格 IPC syscall。所有 IPC 统一走 io_uring 数据面 + Badge。

### 证伪过程

**步骤 1：重构后是否还有"控制面 IPC"？**

重构后，12 个 syscall 的变化：

| Syscall | 重构后状态 | 是否还有？ |
|---------|-----------|:---:|
| `airy_sys_send` | **消除** | ❌ |
| `airy_sys_recv` | **消除** | ❌ |
| `airy_sys_nbsend` | **消除** | ❌ |
| `airy_sys_nbrecv` | **消除** | ❌ |
| `airy_sys_reply_recv` | **消除** | ❌ |
| `airy_sys_yield` | **消除** | ❌ |
| `airy_sys_reply` | **消除** | ❌ |
| `airy_sys_call` | **保留**（能力管理，非 IPC） | ⚠️ |
| `airy_sys_rovol_ctl` | 保留 | — |
| `airy_sys_sched_ctl` | 保留 | — |
| `airy_sys_clt_notify` | 保留 | — |
| `airy_sys_notify` | 保留 | — |

**8 个能产生死锁环的同步阻塞 Send/Recv/Call 中，7 个被消除。唯一保留的 `airy_sys_call` 仅用于能力管理操作（mint/derive/revoke），不用于数据通信。**

**步骤 2：`airy_sys_call` 是否能形成死锁环？**

重构后 `airy_sys_call` 的使用模式：

```
macro_superv ──airy_sys_call(revoke, cap_id)──→ sec_d
                                                   │
                                                   │ sec_d 执行:
                                                   │  - 验证 macro_superv 有 REVOKE 权限
                                                   │  - 调用 airy_cap_epoch_increment()
                                                   │  - 返回结果
                                                   │
                                                   │ sec_d 不调用任何其他 daemon
                                                   │
                                                   ▼
                                              返回 AIRY_OK 或错误码
```

**死锁环的形成条件**：A 调用 B，同时 B 调用 A（或 A→B→C→A）。

在这个场景中：
- `macro_superv` → `sec_d`（revoke 请求）
- `sec_d` 处理 → 返回结果
- `sec_d` 在处理 revoke 期间**不调用任何其他 daemon**（仅操作内存中的 Epoch 原子变量）
- 不存在 `sec_d` → `macro_superv` 的同步调用

**证伪结论：`airy_sys_call` 的使用模式是单向非环状的。不存在形成死锁环的条件。**

**步骤 3：数据面 io_uring 是否有死锁风险？**

重构后，所有 daemon 间数据通信通过 io_uring 数据面。io_uring 的 SQE/CQE 是异步的——发送方提交 SQE 后立即返回，接收方通过 epoll/eventfd 被通知。**不存在发送方阻塞等待接收方的情况。**

**证伪结论：数据面 io_uring 天然不具备形成分布式死锁的条件（无同步等待语义）。**

**步骤 4：残留学风险？**

**有。** 如果 `sec_d` 在处理 revoke 请求时崩溃（在处理 `airy_sys_call` 期间），`macro_superv` 的 `airy_sys_call` 会超时。但：
- 超时可以缩短至 100ms（对齐认知循环超时，不再是 5s）
- `sec_d` 崩溃不影响数据面通信（Badge 自验证，不需要 sec_d 在线）
- `macro_superv` 在超时后可以重试或进入降级模式

**残留学风险级别**：低。影响面从"12 daemon 网格中的任意两个都可能死锁"缩小为"macrov_superv → sec_d 的单向调用可能超时"。

### 证伪判定：**声称属实。** 重构消除了 7/8 同步阻塞 IPC syscall，保留的 `sec_d` 能力管理调用不具备形成死锁环的条件。残留学风险是 `sec_d` 崩溃导致的单向超时（可缩短至 100ms），而非分布式死锁。

---

## 风险二：控制面与数据面的能力模型不一致

### 第三方描述
> 控制面（syscall）和数据面（io_uring）使用不同的代码路径进行 Capability 校验。在权限撤销后，存在一个短暂的 IPI 延迟窗口（1-5μs），数据面可能仍会基于过时的缓存放行请求。

### 重构声称
> 消除双平面。Badge 是唯一能力证明。Epoch 替代 per-CPU cache + IPI coherency。

### 证伪过程

**步骤 1：重构后是否还有两条能力校验路径？**

重构前：控制面 `decode_and_invoke → cap_rights_check` + 数据面 `airy_cap_check_fast → per-CPU cache lookup`

重构后：**无论消息来自哪个入口，能力校验走同一个代码路径：**

```c
// kernel/ipc/airy_cap_badge_verify() — 唯一的能力校验函数
static inline int airy_cap_badge_verify(u64 badge, u32 cap_type, u32 required)
{
    u32 epoch = atomic_read(&airy_cap_epoch[cap_type]);  // 无锁读取
    if ((badge >> 32) != epoch)
        return -AIRY_ECAP_EPOCH;  // Epoch 不匹配 → 立即拒绝
    if ((badge & required) != required)
        return -AIRY_ECAP_PERM;   // 权限不足 → 立即拒绝
    return 0;                      // 通过
}
```

**证伪：不存在两条路径。只有一条路径。不存在"控制面校验"和"数据面校验"的区分。**

**步骤 2：IPI 延迟窗口是否仍然存在？**

重构前的 IPI 延迟窗口：sec_d 更新 radix tree → 发送 IPI 到所有 CPU → per-CPU cache 失效。在 IPI 到达之前（1-5μs），数据面可能从过时的 cache 中读取旧权限。

重构后的 Epoch 模型：sec_d 调用 `atomic_inc(&airy_cap_epoch[cap_type])`。这是一个**原子操作，带有隐式的全局内存屏障**（`atomic_inc` 在 x86 上编译为 `lock incl`，在所有 CPU 上可见）。下一个读取 `airy_cap_epoch` 的 CPU 将看到新值。

**Epoch 递增后的第一个 badg 校验：**
```
CPU 0 (sec_d):                     CPU 1 (fastpath):
atomic_inc(&epoch)  ───────────→   badge_epoch = (badge >> 32)
  │ (lock incl: 全局可见)            │
  │ epoch: N → N+1                  │ atomic_read(&epoch) → N+1
  │                                 │ badge_epoch = N ≠ N+1 → REJECT
```

**证伪：不存在 IPI 延迟窗口。`atomic_inc` 的全局可见性由硬件保证（x86 的 `lock` 前缀立即在所有 CPU 上可见）。没有 per-CPU cache，没有 TTL，没有 IPI。** 这是 Epoch 方案对 cache-based 方案的结构性优势。

**步骤 3：是否存在新引入的漏洞？**

考虑以下序列：

```
T1: Agent A 从 sec_d 获取 Badge (epoch=N, perms=IPC_SEND)
T2: macro_superv 请求 revoke Agent A 的 IPC_SEND 权限
T3: (badge >> 32) = N
T4: sec_d 执行 atomic_inc(&epoch) → N+1
T5: (badge >> 32) = N ≠ N+1 → REJECT ✓
```

**没有问题。Badge 在 Epoch 递增后立即失效。**

考虑另一个序列：

```
T1: Agent A 从 sec_d 获取 Badge (epoch=N, perms=IPC_SEND)
T2: Agent A 发出消息 M1 (badge_epoch=N)
T3: M1 在 kfifo/ring buffer 中排队（尚未被处理）
T4: sec_d 执行 atomic_inc → N+1
T5: M1 被处理: (badge_epoch = N) ≠ (current_epoch = N+1) → REJECT
```

**M1 被拒绝。这是设计意图——权限已撤销，不应投递。但 Agent A 可能期望 M1 被投递（因为它在权限撤销前发出）。**

这是一个值得讨论的语义问题（不是安全漏洞，而是正确性语义）：

| 语义选择 | 行为 | 权衡 |
|---------|------|------|
| **立即拒绝**（当前设计） | M1 被 REJECT | 安全优先。已撤销权限的 Agent 不应发送任何消息。Agent A 收到 REJECT 后重新请求权限 |
| **在途消息豁免** | M1 被投递 | 一旦权限撤销延迟生效。需要在撤销前"排空"——这正是两阶段递增机制 |

**两阶段递增机制**（§1.2）：在 Epoch 递增之前，先标记 `AIRY_EPOCH_TRANSITION`，等待 5ms（最坏情况 ring buffer 排空时间），再执行 `atomic_inc`。这个等待确保在途消息被处理完毕后 Epoch 才递增。

**证伪：两阶段递增机制消除了"在途消息被意外拒绝"的语义歧义。**

**步骤 4：残留学风险？**

- **没有**：IPI 延迟窗口被 Epoch 的原子递增消除
- **没有**：双路径能力校验变为单路径
- **有**：两阶段递增的 5ms 排空等待是硬编码的，如果 ring buffer 使用了非默认的更大值（最大 32768），5ms 可能不足以排空（32768 × 160ns ≈ 5.2ms > 5ms）。需修正为基于 ring 大小的动态排空时间。

### 证伪判定：**声称属实。** 重构将能力校验从双路径 + IPI coherency 统一为单路径 + 原子 Epoch。IPI 延迟窗口不存在，因为 Epoch 递增通过 `atomic_inc` 立即全局可见。残留学风险是两阶段递增的排空等待未根据实际 ring 大小动态计算。

---

## 风险三：MSG_RING 全网格通信的锁争用与死锁

### 第三方描述
> 12 个守护进程通过 MSG_RING 进行全网格通信时，存在 uring_lock 的争用和潜在的 ABBA 死锁风险。

### 重构声称
> §5.2 明确声明："MSG_RING 12方网格 uring_lock 争用 — io_uring 内部锁机制，需要独立的并发控制设计"

### 证伪过程

**步骤 1：重构是否声称解决了此问题？**

**没有。** 重构方案 §5.2 的"本方案不解决的问题"表格中明确列出了 MSG_RING 锁争用。重构者承认此问题不在方案范围内。

**步骤 2：重构是否恶化了此问题？**

重构前：12 daemon 通过控制面 syscall 进行数据通信（MSG_RING 仅用于跨 ring 消息）+ 数据面。

重构后：所有 IPC 走数据面。daemon 间通过 io_uring 通信。如果每个 daemon 有独立的 io_uring 实例，跨 daemon 通信必然通过 MSG_RING。

**MSG_RING 的使用频率可能增加**（因为控制面被消除，原本走控制面的数据通信现在走数据面，其中涉及跨 ring 的部分走 MSG_RING）。

**步骤 3：是否有缓解？**

重构方案未提供 MSG_RING 的缓解措施。但可以推导出两个潜在的缓解方向：

1. **减少 MSG_RING 的使用**：如果 12 daemon 共享一个 io_uring 实例（而非各自持有独立实例），则 daemon 间通信不需要 MSG_RING——它们写入同一个 ring buffer。这是可行的（io_uring 支持 multi-producer）但不推荐（失败隔离减弱）。

2. **MSG_RING 级联限制**：限制 MSG_RING 的级联深度 ≤ 1，防止 ABBA 死锁的级联传播。但单层 ABBA 死锁仍然可能。

3. **专用 io-wq 池**：为 A-IPC 的 MSG_RING 操作分配专用的 io-wq worker 池（`IORING_REGISTER_IOWQ_AFF`），防止与普通 I/O 的 io-wq 饱和竞争。

### 证伪判定：**声称未解决——重构者自己也承认未解决。** 重构可能间接增加了 MSG_RING 的使用频率（因为控制面被消除）。方案需要补充 MSG_RING 的独立并发控制设计（共享 ring 或专用 io-wq + 级联限制）。

---

## 风险四：组件崩溃后的恢复能力

### 第三方描述
> 当一个守护进程崩溃后，其他等待其响应的守护进程会被阻塞长达 5 秒。崩溃的守护进程重启后，如何重新注册其 io_uring 环并重新加入通信网络，目前也缺乏清晰的流程定义。

### 重构声称
> 消除了同步阻塞，所有 IPC 为异步 io_uring CQE。Sender 在 Receiver 崩溃时立即收到 -EINVAL（无需等待 5s）。恢复流程：重启 → 重建 ring → 重新请求 Badge → 发送 READY 通知。

### 证伪过程

**步骤 1：是否消除了 5s 阻塞？**

重构前：`airy_sys_send (阻塞, timeout=5s)`。Receiver 崩溃 → Sender 阻塞 5s。

重构后：`io_uring_prep_cmd(SEND) + io_uring_submit()`。Receiver ring 不存在 → `io_uring_submit` 返回 -EINVAL 或 CQE res = -EINVAL（立即，无需超时等待）。

**证伪：5s 阻塞被消除。Sender 立即感知 Receiver 的不可用状态。**

**步骤 2：恢复流程是否存在缺口？**

重构方案定义的恢复流程（25号审查 §3.3 + 24号审查 §5.2）：

```
1. systemd 自动重启 daemon
2. daemon 重新创建 io_uring ring
3. daemon 通过 NULL Badge 向 sec_d 发送 CAP_REQUEST
4. sec_d 编译新 Badge → 返回 CAP_RESPONSE
5. daemon 向 gateway_d 发送 READY(data_plane + new_badge)
6. gateway_d 从 offline queue 取出暂存请求 → 重新发送
```

**缺口 1：步骤 5 中，如果 gateway_d 尚未感知 daemon 的恢复（gateway_d 怎么知道 daemon 已重启？）。**

- 缓解：systemd 的 `WantedBy=airymaxos.target` 和 `After=cogn_d.service` 确保启动顺序。gateway_d 可以通过 poll MSG_RING 或监听 daemon 的 ring fd 来感知恢复。
- **重构方案未具体说明 gateway_d 的感知机制。**

**缺口 2：步骤 3 中，如果 sec_d 也崩溃了怎么办？**

- 这是双组件崩溃的极端情况。如果 sec_d 不可用，daemon 无法获取新 Badge，只能使用 NULL Badge（仅限于最简操作）。
- **重构方案未定义 sec_d 不可用时的降级模式。**

**缺口 3：步骤 6 中的 offline queue 在重构方案中未显式设计。**

- 24号审查提到了 "offline queue"，但 25号审查的重构方案中未包含 offline queue 的设计。
- 这是一个具体实现细节，但影响恢复的完整性。

### 证伪判定：**声称部分属实。** 5s 阻塞被消除（属实）。恢复流程的基本路径已定义（属实）。但存在三个缺口：(1) gateway_d 的恢复感知机制未定义；(2) sec_d 也崩溃时的降级模式未定义；(3) offline queue 的设计未包含在重构方案中。这些缺口不阻塞核心架构，但需要在详细设计中补充。

---

## 风险五：形式化验证的缺失

### 第三方描述
> 与经过完整形式化验证（Isabelle/HOL）的 seL4 不同，Airymax 的 Capability Folding 机制目前缺乏同等级别的数学证明。

### 重构声称
> 未声称提供形式化验证。重构将系统复杂度从 radix tree + per-CPU cache + IPI coherency 简化为 atomic_t[10] + 两条 CPU 指令，使得验证问题更小。

### 证伪过程

**步骤 1：重构是否提供了形式化验证？**

**没有。** 重构方案没有包含 Isabelle/HOL 或任何形式化验证的交付物。第三方在这点上的断言是准确的。

**步骤 2：重构是否使形式化验证更可行？**

重构前的形式化验证范围：
- radix tree 的插入/查找/删除正确性
- per-CPU cache 的一致性（在 IPI 延迟窗口内的行为）
- RCU 的 grace period 期间的内存安全
- cap_check_fast 与 cap_rights_check 语义等价

重构后的形式化验证范围：
- `atomic_inc` 的全局可见性（由 x86 硬件保证，无需证明）
- `(badge >> 32) == epoch` 的等价性（无需证明，是类型转换）
- `(badge & required) == required` 的等价性（无需证明，是位运算）

**验证空间从"分布式缓存一致性协议"缩小为"两个 CPU 指令"。这是数个数量级的简化。**

但这仍然不是形式化验证。第三方关注的是"没有 Isabelle/HOL 证明"，这点事实正确。

**步骤 3：seL4 的可比性**

seL4 的形式化验证覆盖了：
- 约 8,700 行 C 代码的功能正确性
- 无死锁、无活锁、无缓冲区溢出
- 能力传递的安全性（authority confinement）
- 约 200 人年的验证工作量

Airymax 基于 Linux 6.6（约 3000 万行），完整的形式化验证在工程上不可行。可验证的范围是 Airymax 在 Linux 之上的增量代码（agent-linux 的微内核化补丁 + A-IPC 模块），约 1-5 万行。

重构后的 A-IPC 核心模块（Epoch + Badge + fastpath C-S9）约 200-500 行 C。这个范围内的形式化验证（如 CBMC 有界验证或 Isabelle/HOL 对特定属性的证明）**在工程上可行**，但如果要求"seL4 级别的完整功能正确性证明"，则在 0.1.1 奠基版本的工期约束下不可行。

### 证伪判定：**声称属实。** 重构没有提供形式化验证。但重构将验证问题从"分布式缓存一致性协议"缩小为"两条 CPU 指令 + 原子计数器"，使有界验证在工程上可行。完全的形式化验证（Isabelle/HOL 级别）在当前阶段不可行，也不在重构方案的范围内。

---

## 六项风险的总结

| # | 第三方风险 | 重构是否解决 | 残留学风险 | 严重度 |
|---|-----------|:---:|------|:---:|
| 1 | 控制面同步阻塞死锁 | ✅ **完全消除** | `sec_d` 崩溃可能导致单向超时（可缩短至 100ms） | 低 |
| 2 | 能力模型不一致 + IPI 延迟 | ✅ **完全消除** | 两阶段递增的排空等待需根据实际 ring 大小动态计算 | 低 |
| 3 | MSG_RING 锁争用 | ❌ **未解决（重构承认）** | MSG_RING 频率可能因控制面消除而增加；需补充共享 ring 方案或专用 io-wq | 中 |
| 4 | 组件崩溃恢复 | ⚠️ **部分解决** | 5s 阻塞消除，基本恢复路径已定义，但 gateway_d 感知机制、sec_d 降级模式、offline queue 设计需补充 | 中 |
| 5 | 形式化验证缺失 | ❌ **未解决（重构承认）** | 简化后的系统使有界验证可行，但完整 Isabelle/HOL 证明不在 0.1.1 范围内 | 低 |

**五项风险中，两项完全消除（1, 2），一项部分消除（4），两项未解决但重构承认且严重度可控（3, 5）。**

---

## 最终证伪结论

**重构方案没有过度承诺。它在 §5.2 明确承认了 MSG_RING 和 io-wq 饱和不在方案范围内。它在设计部分消除了同步阻塞和双轨能力校验这两个最严重的架构风险。它没有声称提供形式化验证。**

**第三方审查的五个关切点中，两个被完全消除，一个被部分消除，两个被承认未解决但提供了缓解方向。重构方案经得起证伪——它没有声称解决它没有解决的问题。**

**需要注意的一个残留点是 MSG_RING 频率可能因控制面消除而增加。如果这是生产中的实际瓶颈，需要独立的并发控制设计（共享 ring 架构或专用 io-wq 池）。**

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
