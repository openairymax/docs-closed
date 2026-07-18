# 25 — A-IPC 根本性重构方案

## "IPC 不是承载能力校验——IPC 就是能力校验"

> **文档性质**：agentrt-linux A-IPC 模块的根本性重构方案
> **撰写日期**：2026-07-18
> **设计层级**：内核级工程——不是"在现有 IPC 上增加 Capability Folding"，而是"以 Capability 为 IPC 的基石重新推导全部设计"
> **前置基础**：16~24 号共 9 份审查报告的全部发现

---

## 0. 起点：当前 A-IPC 的根本矛盾

### 0.1 当前架构的本质

九轮审查最终可以收敛为一个论断：

> **当前 A-IPC 不是一个统一的通信体系。它是两个独立 IPC 子系统的并列——控制面是 seL4 风格的同步阻塞 syscall，数据面是 io_uring 风格的异步 CQE。这两个子系统共享一个消息头格式（Layout C），但在能力校验、错误语义、故障隔离上互不贯通。**

```
当前 A-IPC 的实质架构：

   控制面 IPC（seL4 风格）              数据面 IPC（io_uring 风格）
   ┌──────────────────────┐          ┌──────────────────────────┐
   │ airy_sys_send        │          │ io_uring SQE/CQE          │
   │ airy_sys_recv        │          │ IORING_OP_URING_CMD       │
   │ airy_sys_call        │          │ kfifo (kthread 间)        │
   │ airy_sys_reply       │          │ MSG_RING (跨 ring)        │
   │ ... (共 8+4=12 个)   │          │ eventfd 通知              │
   │                      │          │                           │
   │ 同步阻塞              │          │ 异步非阻塞                │
   │ ~1μs syscall 开销     │          │ 零 syscall (SQPOLL)       │
   │ 能力校验: decode_and  │          │ 能力校验: cap_check_fast  │
   │   _invoke()          │          │   (per-CPU cache)         │
   └──────────────────────┘          └──────────────────────────┘
            ↑                                  ↑
            │         共享 Layout C 消息头       │
            └──────────────┬───────────────────┘
                           │
                    但这只是格式共享——不是体系统一。
                    两个平面的能力校验是两条独立的代码路径。
                    两个平面的错误语义互不传播。
                    两个平面的故障影响互不隔离。
```

**这不是"有 bug 的 IPC 设计"——这是"两个 IPC 系统被称作一个系统"。**

### 0.2 这个矛盾的表现（对应九轮审查的全部发现）

| 发现 | 来源 | 根因 |
|------|------|------|
| 控制面同步阻塞在 12 daemon 网格中可能死锁 | 21 号审查维度三 | 控制面和数据面是两个独立系统，数据通信不得不经过控制面 |
| 能力校验两条路径不可通约 | 21 号审查维度四 | 控制面的 `decode_and_invoke` 和数据面的 `cap_check_fast` 不共享代码 |
| 控制面超时 5s 导致 daemon 崩溃级联冻结 | 21 号审查维度三 | 控制面是同步的，发送方无法在接收方崩溃时立即感知 |
| 消息排序无法跨三通道保证 | 19 号审查 D1 | 控制面的同步 Send 和数据面的异步 CQE 不共享排序域 |
| OP 码在两个平面上定义不同 | 18 号审查 | 控制面有 12 个 syscall，数据面有 4-6 个 OP，语义不对齐 |
| Capability Folding 在论文存在但工程不存在 | 20 号审查 | 论文设计的是统一的消息-能力模型，工程实现走的是双平面 |
| 总纲代码正确（cmd_op 而非 sqe.opcode）但下层文档未同步 | 18 号审查 | 双平面导致两份文档体系偏离 |

**九轮审查的所有问题，根源都是同一个：能力校验没有被设计为 IPC 的内生属性，而是被设计为 IPC 的外挂检查。**

---

## 1. 重构的核心原则

### 1.1 第一条原则：消息即能力

> **在重构后的 A-IPC 中，一条消息能够被投递，当且仅当它携带一个合法的 Badge。不存在"先发送一条没有 Badge 的消息，然后再检查权限"的路径。**

```
重构前：
Message → [独立的 Capability Check] → Deliver or Reject
         ↑ 这是一个外挂检查

重构后：
Message(Badge) → Deliver or Reject
                ↑ Badge 是 Message 的一部分，不是外挂检查
```

这意味着：不存在"控制面的能力校验"——所有的能力校验都在消息头中的 Badge 字段中完成。`airy_sys_call` 不再是一个"IPC 原语"——它是一个"能力管理操作"。它做的事情是 mint/derive/revoke——修改 Epoch，编译 Badge——而不是"发送消息"。

### 1.2 第二条原则：控制面不存在

> **重构后的 A-IPC 只有一个平面：数据面。12 个 seL4 风格 syscall 中的 8 个 IPC 原语被消除。保留的 `airy_sys_call` 和 `airy_sys_notify` 不是 IPC——它们是能力管理操作和异步信号。**

```
重构后的 A-IPC 只有一个平面：

   A-IPC（数据面 io_uring）
   ┌──────────────────────────────────────────┐
   │ io_uring SQE/CQE                         │
   │   ├── AIRY_CMD_IPC_SEND (cmd_op=0x01)    │
   │   ├── AIRY_CMD_IPC_RECV (cmd_op=0x02)    │
   │   ├── AIRY_CMD_IPC_SEND_BATCH (0x03)     │
   │   ├── AIRY_CMD_IPC_CANCEL   (0x04)       │
   │   └── AIRY_CMD_IPC_FREEZE   (0x05)       │
   │                                           │
   │ 每条消息携带 capability_badge 字段          │
   │ 能力校验 = (badge >> 32) == epoch          │
   │           && (badge & required) == required│
   └──────────────────────────────────────────┘

   能力管理操作（不是 IPC）：
   ┌──────────────────────────────────────────┐
   │ airy_sys_call    → mint/derive/revoke    │
   │ airy_sys_notify  → async signal          │
   └──────────────────────────────────────────┘
```

### 1.3 第三条原则：Epoch 是唯一全局状态

> **重构后的 A-IPC 中，内核维护的与能力相关的唯一全局状态是一组原子 Epoch 计数器。没有 per-CPU capability cache，没有 radix tree，没有 IPI coherency 协议。**

```
重构前的能力模型：
  radix tree (O(1) lookup)
    └── per-CPU cache (TTL + IPI invalidation)
         └── fastpath cache hit (common)
              └── fastpath cache miss → radix tree lookup (uncommon)

重构后的能力模型：
  atomic_t epoch[AIRY_CAP_NR_TYPES]  (10 × 4B = 40B 全局状态)
    └── fastpath: (badge >> 32) == epoch[cap_type]  (一条 shift + 一条 compare)
         └── 没有 cache。没有 miss。没有 IPI。
```

### 1.4 第四条原则：发送方持有证明，不查询授权方

> **在重构后的 A-IPC 中，发送方 Agent 在建立连接时从 sec_d 获取一个编译好的 Badge。此后，发送方不需要再次联系 sec_d 来"检查权限"——Badge 本身就是权限证明。sec_d 不需要在线，不需要响应查询。如果权限被撤销，Epoch 递增，Badge 自然失效。**

---

## 2. A-IPC 的重新推导

### 2.1 步骤一：定义 A-IPC 要做的事情

A-IPC 是 Airymax 中所有 Agent 和 daemon 之间通信的唯一机制。它需要做到：

1. 将一条消息从发送方传递到接收方
2. 在传递的同时，验证发送方有权限向接收方发送此类消息
3. 如果验证失败，不投递消息，不唤醒接收方
4. 在任何组件崩溃的情况下，不丢失消息、不产生死锁、不级联故障

**从这个定义出发，A-IPC 的数学抽象是：**

```
deliver(src, dst, msg) =
    if authorized(src, dst, msg.capability_type) then
        ring_write(dst, msg)
        notify(dst)
    else
        reject(msg)
```

**关键：`authorized()` 必须在 `ring_write()` 之前完成并且是同一路径上的原子操作。** 当前设计中，控制面的 `authorized()` 和 `ring_write()` 是两条不同路径——这就是所有问题的根源。

### 2.2 步骤二：将 authorized() 折叠进消息本身

```
authorized(src, dst, cap_type) 在 Native Word 方案中等价于:
    badge = msg.capability_badge
    return (badge >> 32) == epoch[cap_type]
           && (badge & permission_mask(cap_type)) != 0
```

**两条 CPU 指令。在 `ring_write()` 之前执行。在同一代码路径上。**

这意味着 A-IPC 的 fastpath 逻辑是：

```
FAST_SEND:
  1. badge = msg.capability_badge
  2. if (badge >> 32) != epoch → REJECT  // 能力已过期
  3. if (badge & AIRY_CAP_PERM_IPC_SEND) == 0 → REJECT  // 无发送权限
  4. kfifo_in(ring, msg)               // 投递
  5. eventfd_signal(recv_ring)         // 通知
  6. → IDLE
```

**不需要查任何表。不需要联系任何 daemon。不需要缓存一致性协议。这就是数学上的 `authorized()` 的内联实现。**

### 2.3 步骤三：重新定义"控制面"——它不是 IPC，是能力管理

重构后，12 个 seL4 风格 syscall 被重新分类：

| 原分类 | Syscall | 重构后分类 | 说明 |
|--------|---------|-----------|------|
| IPC 原语 | `airy_sys_call` | **能力管理** | mint/derive/revoke，改变 Epoch |
| IPC 原语 | `airy_sys_send` | **消除** | 所有 Send 走 io_uring 数据面 + Badge |
| IPC 原语 | `airy_sys_recv` | **消除** | 所有 Recv 走 io_uring 数据面 |
| IPC 原语 | `airy_sys_nbsend` | **消除** | io_uring 异步提交替代 |
| IPC 原语 | `airy_sys_nbrecv` | **消除** | io_uring CQE 替代 |
| IPC 原语 | `airy_sys_reply_recv` | **消除** | io_uring SEND + RECV 替代 |
| IPC 原语 | `airy_sys_yield` | **消除** | io_uring IORING_ENTER_GETEVENTS 替代 |
| IPC 原语 | `airy_sys_reply` | **消除** | 数据面 RESPONSE 消息替代 |
| 控制原语 | `airy_sys_rovol_ctl` | **控制原语** | 不变 |
| 控制原语 | `airy_sys_sched_ctl` | **控制原语** | 不变 |
| 控制原语 | `airy_sys_clt_notify` | **控制原语** | 不变 |
| 通知原语 | `airy_sys_notify` | **异步信号** | 不变 |

**消除 8 个 syscall。syscall 总数从 12 → 4。**

### 2.4 步骤四：seL4 映射的重新阐释

当前设计将 seL4 的 8 个 IPC syscall 映射为 Linux syscall（`airy_sys_send`, `airy_sys_recv` 等）。重构后，seL4 IPC 概念映射到 io_uring 数据面：

| seL4 IPC 操作 | 重构后 A-IPC 的映射 | 映射质量 |
|:-------------|:-------------------|:-------:|
| `seL4_Send` | `io_uring_prep_cmd(SEND, badge=...)` + `io_uring_submit()` | 机制不同，语义等价 |
| `seL4_Recv` | `io_uring_wait_cqe()` 后从 registered buffer 读取 | 同上 |
| `seL4_Call` | SEND + 等待 CQE（RECV） | 异步化，reply 由 request_id 匹配 |
| `seL4_Reply` | SEND(type=RESPONSE, correlation_id=request_id) | 异步化 |
| `seL4_NBSend` | io_uring_submit() 即返回 | 天然非阻塞 |
| `seL4_NBRecv` | io_uring_peek_cqe() | 天然非阻塞 |
| `seL4_ReplyRecv` | io_uring SEND → 等待 CQE → poll 下一个 | 异步化 |
| `seL4_Yield` | IORING_ENTER_GETEVENTS | 语义等价 |

**seL4 的 API 语义全部保留，但实现从同步 syscall 变为异步 io_uring。这没有丢失 seL4 的任何能力——它保留了同样的操作语义，同时消除了同步阻塞带来的死锁风险。**

---

## 3. 重构后的 A-IPC 完整架构

### 3.1 单一平面的消息生命周期

```
Agent A (发送方)                     内核 (io_uring + kfifo)            Agent B (接收方)
─────────────────                    ─────────────────────            ─────────────────

1. 构建 128B 消息头
   (含 capability_badge =
    Epoch || Permissions Mask)
   ↓

2. io_uring_prep_cmd(
     sqe,
     IORING_OP_URING_CMD,
     cmd_op = AIRY_CMD_IPC_SEND,
     msg_hdr, 128)
   ↓
                                3. io_uring_cmd 回调
                                   ↓
                                4. [BADGE CHECK]
                                   epoch = badge >> 32
                                   if epoch != current_epoch → REJECT
                                   if (badge & SEND) == 0 → REJECT
                                   ↓
                                5. kfifo_in(dst_ring, msg)
                                   ↓
                                6. eventfd_signal(dst_ring)
                                                                          ↓
                                                                       7. epoll_wait 触发
                                                                          ↓
                                                                       8. 读取 registered buffer
                                                                          ↓
                                                                       9. [BADGE CHECK 可选]
                                                                          接收方可选择再次验证
```

### 3.2 Fastpath 状态机（简化）

```
重构前: 12 seL4-syscall 控制面 + 8 状态 io_uring 数据面
重构后: 1 个 io_uring 数据面（7 状态） + 4 个能力管理 syscall

状态:
IDLE ——空闲，等待 SQE
CHECK —— Badge 校验（epoch + permissions）    [新增，极快路径]
FAST_SEND —— 同 CPU kfifo 写入（无 payload）
FAST_RECV —— 同 CPU kfifo 读取（无 payload）
SLOW_PATH —— payload > 128B 或跨 CPU [合并了 SLOW_SEND/SLOW_RECV]
BATCH —— 批量聚合
CANCEL —— 取消
ERROR —— 错误

关键变化:
- CHECK 状态: 仅 2 条 CPU 指令，在 kfifo 操作之前
- 消除了 SLOW_SEND 和 SLOW_RECV 的区分（都是 io_uring 异步路径）
- 消除了控制面状态机（因为控制面不存在了）
```

### 3.3 Badge 编译的完整流程

```
Agent A 首次连接:
  1. Agent A 通过 io_uring 向 sec_d 发送 CAP_REQUEST(type=IPC_SEND)
     (此消息本身不需要 Badge——系统为每个 Agent 预留一个 "NULL Badge"
      仅允许向 sec_d 发送 CAP_REQUEST)
  2. sec_d 接收 CAP_REQUEST
  3. sec_d 查询安全策略: Agent A 被授权 IPC_SEND? ALLOW
  4. sec_d 编译 Badge:
     perms = 0
     perms |= AIRY_CAP_PERM_IPC_SEND
     epoch = atomic_read(&airy_cap_epoch[AIRY_CAP_IPC_SEND])
     badge = (epoch << 32) | perms
  5. sec_d 通过 io_uring 向 Agent A 发送 CAP_RESPONSE(badge=badge)
  6. Agent A 将 badge 存储在连接上下文中
  7. 此后所有消息的 capability_badge = badge

能力撤销:
  1. macro_superv 通过 airy_sys_call(revoke) 请求撤销 Agent A 的 IPC_SEND
  2. sec_d 调用 airy_cap_epoch_increment(AIRY_CAP_IPC_SEND)
  3. Epoch 从 N → N+1
  4. 所有携带 Epoch=N 的 Badge 立即失效（两阶段递增后）
  5. Agent A 的下一条消息: (badge >> 32) = N ≠ N+1 → REJECT
  6. Agent A 收到 REJECT → 重新向 sec_d 请求能力
  7. sec_d 重新裁决: 已被撤销 → DENY → Agent A 无法获取新 Badge
```

### 3.4 NULL Badge：自举机制

```
系统为每个 Agent 预留一个 "NULL Badge":
  NULL_BADGE = (Epoch_MAX << 32) | AIRY_CAP_PERM_NULL

NULL Badge 仅允许以下操作:
  1. 向 sec_d 发送 CAP_REQUEST（请求能力）
  2. 向 gateway_d 发送 REGISTER（服务注册）
  3. 接收任何消息（RECV 不需要发送权限）

Fastpath 中:
  if badge == NULL_BADGE && op == SEND && dst == sec_d:
      PASS  // 允许请求能力
  else if badge == NULL_BADGE && op == SEND:
      REJECT  // NULL Badge 不允许发送数据消息
  else:
      正常 Badge 校验
```

---

## 4. 重构对整体方案的影响分析

### 4.1 Syscall 表重设计

```
重构前: 12 核心 syscall（8 IPC + 3 控制 + 1 通知）
重构后: 4 syscall（1 能力管理 + 3 控制 + [0 通知，已被 eventfd 替代]）

| # | 重构前 | 重构后 | 变化 |
|---|--------|--------|------|
| 0 | airy_sys_call | airy_sys_call | [保留] 能力管理（mint/derive/revoke） |
| 1 | airy_sys_send | — | [消除] io_uring SEND 替代 |
| 2 | airy_sys_recv | — | [消除] io_uring CQE 替代 |
| 3 | airy_sys_nbsend | — | [消除] io_uring 异步提交替代 |
| 4 | airy_sys_nbrecv | — | [消除] io_uring CQE 替代 |
| 5 | airy_sys_reply_recv | — | [消除] io_uring SEND+RECV 替代 |
| 6 | airy_sys_yield | — | [消除] io_uring IORING_ENTER_GETEVENTS 替代 |
| 7 | airy_sys_reply | — | [消除] 数据面 RESPONSE 替代 |
| 8 | airy_sys_rovol_ctl | airy_sys_rovol_ctl | [保留] |
| 9 | airy_sys_sched_ctl | airy_sys_sched_ctl | [保留] |
| 10 | airy_sys_clt_notify | airy_sys_clt_notify | [保留] |
| 11 | airy_sys_notify | airy_sys_notify | [保留] |
```

**syscall 编号表从 12 条目简化为 4 条目。**

### 4.2 对 01-syscalls.md 的重写范围

[01-syscalls.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/01-syscalls.md) 当前定义：
- §1.1 控制面 12 核心 syscall → **重写为 4 syscall**
- §1.2 数据面 io_uring → **重写为 A-IPC 唯一 IPC 机制**
- §1.4 Capability Invocation 模型 → **重写为 Badge + Epoch 模型**
- §2 syscall 编号表 → **重写为 4 条目**
- §6 seL4 映射 → **重写为 io_uring 映射**

### 4.3 对 02-ipc-protocol.md 的重写范围

[02-ipc-protocol.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/02-ipc-protocol.md) 当前定义：
- §2 Layout C 消息头 → **升级为 Layout C v2**（capability_badge + seq_num + negotiated_ver + crc32）
- §4 io_uring 零拷贝实现 → **修正 IORING_OP_IPC_* → IORING_OP_URING_CMD + cmd_op**
- §4.6 capability 携带与权限校验 → **重写为 Badge + Epoch 模型**
- §4.7 端点状态机 → **保留了 Idle/Send/Recv 三态，简化实现描述**
- §4.8 Reply 原子性 → **重写为数据面异步 reply + request_id 匹配**
- §5 与 agentrt 同源映射 → **增加 Badge 字段的 [SC] 共享声明**

### 4.4 对 07-ipc-fastpath.md 的重写范围

[07-ipc-fastpath.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/07-ipc-fastpath.md) 当前定义：
- §2 状态机 8 状态 → **简化为 7 状态**（消除 SLOW_SEND/SLOW_RECV 区分，新增 CHECK）
- §3 Fastpath 触发条件 → **C-S9 从黑盒变为 2 条 CPU 指令 + 新增 C-S0 (frozen) + C-S11 (preempt)**
- §4 Slowpath 回退 → **简化**（不再区分 Send/Recv 的 slowpath）
- §5 io_uring 集成 → **修正 sqe.opcode 为 IORING_OP_URING_CMD + cmd_op**
- §A.2 Capability 缓存 → **消除**（Epoch 替代）

### 4.5 对各模块文档的影响

| 文档 | 影响程度 | 说明 |
|------|:---:|------|
| [01-syscalls.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/01-syscalls.md) | **重写** | syscall 表从 12 → 4 |
| [02-ipc-protocol.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/02-ipc-protocol.md) | **大幅修改** | Layout C v2 + Badge 模型 |
| [07-ipc-fastpath.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/07-ipc-fastpath.md) | **大幅修改** | 状态机简化 + C-S9 实现 |
| [03-ipc-flow.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/40-dataflows/03-ipc-flow.md) | **中** | 消除控制面数据流部分 |
| [03-ipc-performance.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/170-performance/03-ipc-performance.md) | **小** | fastpath 延迟数值更新 |
| [10-unify-design.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/10-unify-design.md) | **小** | §8 A-IPC 的实现代码更新 |
| [01-kernel.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/01-kernel.md) | **中** | syscall 表简化 |
| [02-services.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/02-services.md) | **中** | daemon 通信路径变更 |
| [03-capability-model.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/110-security/03-capability-model.md) | **大幅修改** | Epoch 替代 radix tree cache |
| [04-ipc-data-plane-autonomy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/110-security/04-ipc-data-plane-autonomy.md) | **小** | 离线缓存改为离线 Epoch 快照 |

**受影响文档：10 份。其中重写 1 份，大幅修改 3 份，中等修改 3 份，小修改 3 份。**

---

## 5. 风险与本方案的边界

### 5.1 本方案解决的核心问题

| 问题 | 解决方案 |
|------|---------|
| 控制面/数据面双轨（21号审查核心问题） | 消除控制面 IPC，统一为单一数据面 + Badge |
| 12 daemon 同步阻塞死锁 | 所有 IPC 变为异步 io_uring，无阻塞 Send |
| 能力校验两条独立代码路径 | Badge 是唯一能力证明，fastpath C-S9 是唯一校验点 |
| seL4 IPC 原语映射到 Linux syscall 的开销和复杂度 | seL4 语义映射到 io_uring 操作，消除 8 个冗余 syscall |
| per-CPU capability cache 的 IPI coherency | Epoch 替代，无 cache，无 IPI |

### 5.2 本方案不解决的问题（需要独立设计）

| 问题 | 说明 |
|------|------|
| MSG_RING 12方网格 uring_lock 争用 | io_uring 内部锁机制，需要独立的并发控制设计 |
| io-wq 饱和 | io_uring 内部线程池管理问题 |
| BATCH 部分失败语义 | 需要独立修正 BATCH 提交模型（19号审查 D2） |
| CLOCK_REALTIME 回拨 | 时间戳语义问题（19号审查 D6/D7） |

### 5.3 主要风险

| # | 风险 | 严重度 | 缓解 |
|---|------|:---:|------|
| R1 | 消除 8 个 syscall 后，已存在的 seL4 对齐文档/代码需要全局更新 | 高 | 影响 4 份文档 + agentrt [SC] 共享头文件 |
| R2 | NULL Badge 自举机制的安全性审计不完全 | 中 | NULL Badge 仅允许向 sec_d 发 CAP_REQUEST——这是一个极小的攻击面 |
| R3 | Epoch 递增的消息排空等待（5ms）可能被高频撤销触发 | 低 | 撤销是低频操作（秒级），5ms 排空可接受 |

---

## 6. 实施计划

### Phase 0：Layout C 修正 + io_uring OP 修正（2 天）
```
□ 02-ipc-protocol.md §2: Layout C v2 定义
□ 02-ipc-protocol.md §4: IORING_OP_IPC_* → IORING_OP_URING_CMD + cmd_op
□ 03-ipc-flow.md §2.5: SQPOLL/DEFER_TASKRUN 互斥修正
□ 07-ipc-fastpath.md §5.1: sqe.opcode 映射表修正
```

### Phase 1：Epoch + Badge 内核实现（3 天）
```
□ kernel/ipc/airy_epoch.c: Epoch 管理模块
□ kernel/ipc/airy_badge.c: Badge 编译模块
□ 07-ipc-fastpath.md §3: C-S9 实现（2 条 CPU 指令）
□ A-UEF: 注册 4 个新错误码
```

### Phase 2：消除控制面 IPC syscall（3 天）
```
□ 01-syscalls.md: syscall 表从 12 → 4
□ 02-ipc-protocol.md §4.7-4.8: seL4 映射重写为 io_uring 映射
□ 02-services.md: daemon 通信路径全部走数据面
□ 01-kernel.md §6: 消除控制面 IPC 模块描述
```

### Phase 3：文档体系更新（3 天）
```
□ 10-unify-design.md §8: A-IPC 描述更新
□ 03-capability-model.md: Epoch 替代 radix tree
□ 07-ipc-fastpath.md: 状态机简化为 7 状态
□ 03-ipc-flow.md: 消除控制面数据流
□ 全量 Grep: IORING_OP_IPC_* / airy_sys_send / control plane / 控制面
```

### Phase 4：验证（2 天）
```
□ Epoch 递增 + 并发通信混沌测试
□ Badge 编译 → 发送 → 校验 → 撤销 → 拒绝 全链路测试
□ Daemon 崩溃恢复测试
□ Layout C v2 CI 校验规则更新
```

### 总工期：11 天

---

## 7. 最终判定

### 7.1 重构的本质

**这不是"在 A-IPC 上增加 Capability Folding"。这是"认识到当前的 A-IPC 不是真正的统一 IPC 体系后，以 Badge + Epoch 为基石重新推导出真正的 A-IPC"。**

重构后的 A-IPC 与重构前的区别：

| 维度 | 重构前 | 重构后 |
|------|--------|--------|
| IPC 平面数 | 2（控制面 + 数据面） | **1（数据面）** |
| 能力校验路径数 | 2（decode_and_invoke + cap_check_fast） | **1（Badge >> 32 + AND）** |
| Syscall 数 | 12 | **4** |
| 同步阻塞风险 | 存在（控制面 Send 阻塞） | **消除（全部异步 io_uring）** |
| 能力缓存 | radix tree + per-CPU cache + IPI | **atomic_t Epoch[10]** |
| Fastpath C-S9 | ~160ns 黑盒 | **~5ns 两条指令** |
| seL4 映射 | syscall → syscall | **语义映射到 io_uring 操作** |
| Daemon 崩溃影响 | 5s 阻塞 + 级联 | **立即 -EINVAL + 独立恢复** |

### 7.2 一句话

**A-IPC 需要一个根本性的重构——不是因为它设计错了，而是因为它将两个本应统一的维度（IPC 和能力）设计成了两个独立的子系统。重构将它们融合为一个单一的、以 Badge 为自验证令牌的、异步非阻塞的 io_uring 数据面。消除 8 个 syscall，消除双轨能力校验，消除同步阻塞死锁风险，消除 per-CPU cache + IPI coherency 的整个复杂度栈。净复杂度降低，净能力提升。**

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
