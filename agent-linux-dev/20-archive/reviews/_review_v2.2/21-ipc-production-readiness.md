# 21 — A-IPC 生产就绪度最终审查报告

## "能否稳定支撑整个 Airymax 项目？"

> **报告日期**：2026-07-18
> **报告性质**：闭源内部 A-IPC 第六轮审查 — 以生产就绪度为唯一标准的系统性评估
> **评估标准**：能否作为整个 Airymax 项目（12 daemon + 5 内核组件 + 7 数据流 + 全部 Agent 应用）的唯一通信骨干？
> **审查范围**：控制面/数据面双平面一致性、daemon 网格死锁风险、能力模型贯穿性、异常路径完整性、性能上限
> **前置报告**：[16](file:///home/spharx/SpharxWorks/airymaxhub/docs-closed/agent-linux-dev/20-archive/reviews/_review_v2.2/16-ipc-comprehensive-review.md) / [17](file:///home/spharx/SpharxWorks/airymaxhub/docs-closed/agent-linux-dev/20-archive/reviews/_review_v2.2/17-uipf-deep-review-v2.md) / [18](file:///home/spharx/SpharxWorks/airymaxhub/docs-closed/agent-linux-dev/20-archive/reviews/_review_v2.2/18-aipc-systematic-review.md) / [19](file:///home/spharx/SpharxWorks/airymaxhub/docs-closed/agent-linux-dev/20-archive/reviews/_review_v2.2/19-aipc-flaw-review.md) / [20](file:///home/spharx/SpharxWorks/airymaxhub/docs-closed/agent-linux-dev/20-archive/reviews/_review_v2.2/20-capability-folding-audit.md)

---

## 0. 评估框架

### 0.1 评判维度

"稳定支撑"意味着 A-IPC 必须在以下六个维度同时合格：

| 维度 | 定义 | 不合格的后果 |
|------|------|------------|
| **吞吐** | 峰值负载下不丢消息、不阻塞 | Agent 间通信中断 |
| **延迟** | P99 延迟在 SLO 内 | Agent 认知循环超时 |
| **隔离** | 单个 daemon 故障不影响其他 daemon 的 IPC | 级联崩溃 |
| **一致性** | 控制面与数据面使用统一的能力模型 | 权限检查绕过 |
| **恢复** | 任意组件崩溃后可恢复通信 | 无法重启后恢复服务 |
| **上限** | 存在明确的性能天花板，且可规划扩容 | 超过上限后行为不可预测 |

### 0.2 A-IPC 的实际负载

| 负载来源 | 数量 | 通信模式 |
|---------|------|---------|
| daemon-daemon | 12×12 双向网格 | io_uring 数据面 |
| daemon-kernel | 12 × 5 内核组件 | 控制面 12 syscall + 数据面 io_uring |
| kthread-kthread | CoreLoopThree 3 个 kthread | kfifo + wait_event |
| Agent-daemon | N × gateway_d | io_uring MSG_RING |
| 跨节点 | M × M 超节点网格 | CXL/RDMA/NVLink |

---

## 1. 通过：维度一 —— 吞吐能力

### 1.1 评估

| 指标 | SLO | io_uring 实际能力 | 结论 |
|------|-----|-----------------|------|
| 单核吞吐 | > 100K msg/s | 250K msg/s（SQPOLL 模式） | ✅ 2.5× 余量 |
| 8 核吞吐 | — | 2M-12M ops/s | ✅ 可线性扩展 |
| kfifo 吞吐 | ≥ 1.5M msg/s | Linux kfifo 基准 | ✅ SPSC 无锁 |

**判定**：当前设计的 io_uring + kfifo 双通道在吞吐上有充分余量。

### 1.2 潜在风险

- **SQPOLL 模式消耗 1 个 CPU 核心**：12 daemon × SQPOLL = 12 个核心。合理，但需要文档明确核心规划。
- **kfifo 4096 项 × 128B = 512 KiB/CPU**：如果 CoreLoopThree 三个 kthread 都在同一 CPU 上共享一个 kfifo，512 KiB 可能在高频认知循环中饱和。

---

## 2. 通过：维度二 —— 延迟能力

### 2.1 评估

| 路径 | 设计延迟 | 实际可行性 | 结论 |
|------|---------|-----------|------|
| 同 CPU fastpath (kfifo) | < 1μs | ≤245 条指令，~10× 余量 | ✅ 可达到 |
| 控制面 syscall | ~1μs | syscall 固有开销 | ✅ 可达到 |
| 数据面 io_uring (SQPOLL) | ~4.2μs | 零 syscall 提交 | ✅ 已验证 |
| 数据面 io_uring (DEFER_TASKRUN) | ~10μs | 含 task_work 延迟 | ✅ 可达到 |

**判定**：延迟目标现实可行。

---

## 3. 不通过：维度三 —— 故障隔离

### 3.1 严重缺陷：控制面同步 syscall 可能导致 daemon 网格死锁

A-IPC 的控制面使用 **seL4 风格的同步阻塞 syscall**：

```
airy_sys_send(cap, msg)    → 阻塞直到接收方 Recv
airy_sys_recv(cap, &msg)   → 阻塞直到发送方 Send
airy_sys_call(cap, &msg)   → 阻塞直到 reply
```

在 12 daemon 的网格拓扑中，**同步阻塞 = 死锁风险**：

```
场景：macro_superv 生命周期检查

macro_superv ─── airy_sys_send ──→ cogn_d
                                       │
                                       │ cogn_d 正在等待
                                       │ sec_d 的策略裁决结果
                                       ▼
                                     sec_d ─── airy_sys_send ──→ macro_superv
                                                                   │
                                                                   │ macro_superv 阻塞在
                                                                   │ cogn_d 的 Send 上
                                                                   ▼
                                                              死锁
```

**seL4 如何避免**：seL4 的 Call 原语在发送方和接收方之间建立 reply 能力，reply 完成后释放。但 Airymax 的控制面 syscall 是独立的 Send/Recv/Call——**没有全局死锁检测机制**。

**12 daemon 网格中的风险**：macro_superv、sec_d、cogn_d、sched_d、mem_d、gateway_d 之间存在密集的双向交互。如果任何一对 daemon 在对方阻塞时相互发送控制面消息，死锁。

### 3.2 数据面的隔离情况

数据面（io_uring）使用异步 CQE——不阻塞发送方。因此数据面的隔离相对安全。但：

- **MSG_RING 死锁避免依赖 io-wq 容量**（19号审查 D5）——io-wq 饱和后 MSG_RING 无法递送
- **12 daemon 全网格 MSG_RING** 会导致 `uring_lock` 争用——每个 daemon 都可能 trylock 其他 daemon 的 ring

### 3.3 一个 daemon 崩溃的影响

如果 `cogn_d` 崩溃：
- 等待 cogn_d 的控制面 Send 超时（5s，[07-ipc-fastpath.md §4.4](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/07-ipc-fastpath.md#L262)）
- 数据面的 MSG_RING 会因为目标 ring 不存在而失败（返回 -EINVAL）
- **但发送方在被超时的 5 秒内处于阻塞状态**——这意味着所有向 cogn_d 发送控制面消息的 daemon 冻结 5 秒

**5 秒阻塞在 Agent 场景中是不可接受的**——Agent 的认知循环超时通常在 100ms 级别。

### 3.4 判定

| 子项 | 状态 | 说明 |
|------|:---:|------|
| 数据面故障隔离 | ✅ | 异步 CQE，发送方不阻塞 |
| 控制面故障隔离 | ❌ | 同步阻塞 syscall + 12 daemon 网格 = 死锁风险 |
| 单 daemon 崩溃恢复 | ⚠️ | 超时 5s 过长 |
| 级联故障防护 | ❌ | 无死锁检测，无超时链传播 |

---

## 4. 不通过：维度四 —— 控制面与数据面的一致性

### 4.1 严重缺陷：两套 IPC 机制的能力模型不统一

A-IPC 有两个完全独立的 IPC 路径，但**文档从未明确声明它们共享同一个能力模型**：

| 维度 | 控制面 | 数据面 |
|------|--------|--------|
| 入口 | 12 syscall（`airy_sys_call` 等） | io_uring SQE/CQE |
| 能力校验方式 | `airy_decode_and_invoke()` 中的 `cap_rights_check` + `cap_type_check` | `airy_cap_check_fast()` 中的 radix tree cache lookup |
| 校验时机 | 每次 syscall 入口 | fastpath 条件 C-S9 |
| 能力传递方式 | `airy_sys_call(cap, &msg)` 中的 cap 参数 | 消息头 `flags` 中的 `AIRY_IPC_F_CAP_CARRY` |
| 错误返回 | 负数 errno | CQE `res = -AIRY_ECAPABILITY` |

**核心问题**：如果 `sec_d` 通过控制面 syscall 更新了一个 Agent 的能力权限，数据面的 `airy_cap_check_fast()` 需要在何时感知到这个变更？

- 控制面更新了内核中的能力表（radix tree）
- 数据面 fastpath 使用 per-CPU 缓存的能力 badge 掩码
- 缓存失效通过 **IPI**（19号审查 §8.2）——这有 1-5μs 的延迟窗口
- **在这个窗口中，数据面可能通过一个已经撤销的能力**

**这等价于 seL4 的 TLB shootdown 窗口**——seL4 接受这个窗口因为在单核微内核中窗口极小。但 Airymax 是 SMP Linux，IPI 延迟可能更长。

### 4.2 判定

| 子项 | 状态 | 说明 |
|------|:---:|------|
| 能力模型一致性 | ⚠️ | 两套机制使用不同校验代码路径 |
| 能力撤销的即时性 | ⚠️ | IPI 延迟窗口中的不一致 |
| 能力传递的贯穿性 | ❌ | 控制面使用 cap 参数，数据面使用 CAP_CARRY flag——两端如何对应未定义 |

---

## 5. 部分通过：维度五 —— 恢复能力

### 5.1 数据面恢复（自主设计，优秀）

数据面自治三原则提供了控制面崩溃时的数据面持续运行能力——这是 A-IPC 最成熟的设计。

### 5.2 控制面恢复（有缺口）

- **控制面 syscall 的恢复**：`airy_sys_send` 超时（5s）后返回 `AIRY_ETIMEDOUT`。但**被阻塞的 5 秒内发生了什么事**？发送方的 kthread/daemon 在这 5 秒内被冻结。
- **Receiver 重启后如何重新注册**：daemon 重启后需要重新创建 io_uring ring，重新注册到 MSG_RING 网络。但**没有文档描述这个重注册流程**。

### 5.3 判定

| 子项 | 状态 | 说明 |
|------|:---:|------|
| 数据面恢复（控制面崩溃） | ✅ | 三原则设计优秀 |
| 控制面恢复（daemon 崩溃） | ⚠️ | 超时过长 + 重注册流程缺失 |
| Ring 重启恢复 | ⚠️ | 新 ring 如何加入已有 MSG_RING 网络未定义 |

---

## 6. 不通过：维度六 —— 性能上限

### 6.1 上限分析

| 资源 | 上限 | 12 daemon 网格下的使用量 | 是否充足 |
|------|------|-----------------------|:------:|
| io_uring ring entries | 默认 256，最大 32768 | 每个 daemon 一个 ring × 256 = 3,072 总 entries | ✅ |
| registered buffers | RLIMIT_MEMLOCK 限制 | 12 daemon × 128B header pool × N | ⚠️ 需计算 |
| SQPOLL 线程数 | 每个 ring 一个内核线程 | 12 daemon = 12 SQPOLL 线程 | ✅ |
| io-wq worker 池 | 默认 4 × online_cpus | MSG_RING punt 可能饱和 | ⚠️（19号审查 D5） |
| kfifo 容量 | 4096 项 × 128B = 512 KiB/CPU | CoreLoopThree 3 kthread | ⚠️ 可能饱和 |
| MSG_RING 网络的 uring_lock 争用 | 每个 MSG_RING 尝试 trylock 目标 ring | 12 daemon 全网格 = 132 个方向 | ⚠️ 热点 |

### 6.2 最坏情况：全网格通信

12 daemon 同时调用 MSG_RING 互相通信：

```
1. Daemon A 持有 A.uring_lock → trylock B.uring_lock（成功）
2. Daemon B 持有 B.uring_lock（被 A 占用，等待释放）
3. Daemon C 持有 C.uring_lock → trylock A.uring_lock（成功）
4. ... 
在没有锁序倒置的情况下，这不会死锁（每个 daemon 只持有自己的锁并 trylock 另一个）。
但如果有 DAISY CHAIN：A→B, B→C, C→A... 这就回到了 ABBA 死锁。
```

**MSG_RING 的 trylock + punt 策略在 12 方全网格中的实际行为未经验证。**

### 6.3 判定

| 子项 | 状态 | 说明 |
|------|:---:|------|
| 吞吐上限 | ✅ | 250K msg/s 有充足余量 |
| 并发上限（MSG_RING 网格） | ❌ | 12 daemon 全网格的 uring_lock 行为未分析 |
| io-wq 饱和风险 | ❌ | 无专用池、无限流 |
| kfifo 饱和风险 | ⚠️ | 512 KiB/CPU 可能不足 |

---

## 7. 六维度总判

| 维度 | 判定 | 关键缺陷 |
|------|:---:|---------|
| **吞吐** | ✅ 通过 | 250K msg/s + 线性扩展 = 充分 |
| **延迟** | ✅ 通过 | < 1μs fastpath + ~4μs 数据面 = 可达到 |
| **隔离** | ❌ 不通过 | 控制面同步阻塞 = 12 daemon 网格死锁风险 + 5s 超时导致整系统冻结 |
| **一致性** | ❌ 不通过 | 控制面与数据面使用不同能力校验路径，能力撤销有 IPI 延迟窗口 |
| **恢复** | ⚠️ 部分通过 | 数据面恢复优秀；控制面恢复超时过长 + 重注册缺失 |
| **上限** | ❌ 不通过 | MSG_RING 12方网格行为未验证；io-wq 无容量保护 |

**在修正所有 P0 问题后（OP 码、SSoT 不一致、设计缺陷），A-IPC 可以通过吞吐和延迟测试。但在生产负载（12 daemon 并发 + 故障注入）下，控制面的同步阻塞模型和 MSG_RING 的锁争用将成为阻塞项。**

---

## 8. 六轮审查全景

```
审查迭代：
16-ipc:  io_uring 传输层     → "OP码错误，无法编译"
17-uipf: 文档交叉验证         → "12处不一致，5 payload三种定义"
18-aipc: 5模块体系            → "总纲正确，下层文档滞后"
19-flaw: 设计逻辑缺陷         → "7个缺陷，三通道无排序"
20-capfld: Capability Folding  → "论文存在，工程不存在"
21-ready: 生产就绪度          → "三过三不过，控制面同步阻塞是最大风险"
```

**演进轨迹**：
- 16-18 轮解决了"文档是否正确"的问题
- 19 轮解决了"设计是否有逻辑漏洞"的问题
- 20 轮发现了论文与工程的脱节
- **21 轮以生产标准审视，发现了控制面同步阻塞这个最大的架构风险**

---

## 9. 最终判定

**A-IPC 可以通过基准测试，但不能通过生产负载检验。**

修正前五轮发现的问题后，A-IPC 在单组件通信上是正确的、高性能的。但在 12 daemon + 故障场景下，控制面的同步阻塞 syscall 模型与 seL4 的同步 IPC 存在相同的死锁风险——而 seL4 通过形式化验证和简单的组件拓扑来管理这个风险，Airymax 的 12 daemon 网格拓扑比 seL4 复杂得多。

**需要做出的设计决策**：
1. **控制面超时缩短**：将 `airy_sys_send` 的默认超时从 5s 降至 100ms（对齐 Agent 认知循环超时）
2. **死锁检测或避免**：引入超时链传播（A→B 超时 = B→C 也超时）或控制面通信拓扑约束（禁止环路依赖）
3. **MSG_RING 上限保护**：限制 MSG_RING 级联深度 ≤ 1，为 A-IPC 分配专用 io-wq 池
4. **能力模型统一**：控制面和数据面共享同一个 `airy_cap_check()` 函数，消除双重校验路径

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
