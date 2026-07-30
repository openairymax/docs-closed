SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 03 — IPC 深度对比：seL4 endpoint+badge vs Airymax io_uring+SPSC ring

> **文档定位**：agentrt-linux v3.6 内核设计深度对比研究第 03 篇，聚焦 IPC 子系统的 seL4 ↔ Airymax 实现差异。
> **对比基准**：seL4 master（verified）+ Airymax agentrt-linux v3.6（kernel/corekern/ipc + security/airy）。
> **最后更新**：2026-07-30。
> **方法论**：基于已逐行核验的代码证据，从模型、传递、校验、取消、内存序、SC 捐赠 6 个维度展开对比；改进建议按 P1/P2 优先级排序，每条给出现状/参考/建议/风险四要素。引用行号均来自代码审查时的实证，禁止凭空捏造。

## 1. 引言

seL4 的 IPC 设计是微内核线最经典的工程范例之一：以 endpoint + badge 为核心，把"谁来送"、"送给谁"、"以何权限送"三件事封装在一次内核进入里。Airymax 在 v3.6 选择了 io_uring_cmd + SPSC 无锁环 + C-S9 Badge 内联校验的异步路径，把传统内核态同步调用转化为 LSM hook 5-phase slowpath + 用户态可观测 fastpath 的组合。

两者并非简单替换关系：seL4 的同步阻塞语义提供了天然的 cancel-by-badge 能力，而 Airymax 的 SPSC 异步路径在去掉内核同步点的同时，也丢掉了某些"内核才知道的状态"。本报告的目标是把丢失的能力一一列出，给出可落地的补齐方案。

## 2. IPC 模型对比

### 2.1 seL4：endpoint 阻塞式 sendIPC

seL4 IPC 的入口在 [endpoint.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/endpoint.c#L20) L20-23：

```c
void sendIPC(bool_t blocking, bool_t do_call, word_t badge,
             ...);
```

`badge` 作为函数参数直接传入，意味着每次 send 都已经携带身份信息。L38 把 badge 写入 TCB 状态：

```c
thread_state_ptr_set_blockingIPCBadge(&thread->tcbState, badge);
```

L86 把 badge 传给 doIPCTransfer：

```c
doIPCTransfer(thread, epptr, badge, canGrant, dest);
```

整个流程是同步的：sender 阻塞在 endpoint 的 send 队列上，receiver 阻塞在 recv 队列上，二者配对时内核一次性完成 badge、消息、可能的 SC 捐赠、可能的 cap grant。这种"一次进入完成全部语义"的设计简化了竞争窗口。

### 2.2 Airymax：io_uring_cmd + SPSC 无锁环

Airymax 把 IPC 投递路径搬到了 io_uring_cmd 异步接口。fastpath 入口在 [airy_ipc_fastpath.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_fastpath.c#L21) L21-35：

```c
int airy_ipc_fastpath_send(struct airy_ipc_ring *ring,
                           const struct airy_ipc_msg_hdr *hdr)
```

L24-25 做 null check，L31-32 仅做 `frozen` 检查：

```c
if (unlikely(READ_ONCE(ring->frozen)))
    return -AIRY_EIPC_FROZEN;
```

L34 直接 `airy_ipc_ring_post(ring, hdr)`。badge 校验不在 fastpath，而在 LSM 的 uring_cmd hook（详见 §4）。

底层是 SPSC 无锁环，定义在 [airy_ipc_internal.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_internal.h#L23) L23-29：`struct airy_ipc_ring` 含 head/tail/mask/frozen/*slots。post 路径见 [airy_ipc_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_ring.c#L60) L60-97：L78 SPSC head 推进，L79 满判定，L94 memcpy 入环，L95 `smp_store_release(&ring->head, next)` 发布。

### 2.3 模型本质差异

| 维度 | seL4 endpoint | Airymax io_uring+SPSC |
|------|---------------|----------------------|
| 同步性 | sender 阻塞直到配对 | 异步投递，无 sender 阻塞 |
| 进入点 | 单一 sendIPC 内核路径 | uring_cmd hook → fastpath |
| 状态载体 | TCB（badge/state） | ring slots（msg_hdr） |
| 取消粒度 | 内核可达所有等待者 | 仅 frozen 全环冻结 |
| 进度模型 | 内核决定配对 | producer/consumer 独立推进 |

## 3. Badge 传递时机对比

### 3.1 seL4：写 TCB → 接收时读回

seL4 的 badge 不只是消息里的字段，它是 sender 退出阻塞时的"身份"：

- 写入：[endpoint.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/endpoint.c#L38) L38 `thread_state_ptr_set_blockingIPCBadge(&thread->tcbState, badge)`，badge 在 sender 阻塞前就钉进 TCB 状态。
- 读回：[endpoint.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/endpoint.c#L241) L241 `badge = thread_state_ptr_get_blockingIPCBadge(&sender->tcbState)`，receiver 配对时由内核从 sender TCB 取出。
- reply 路径 badge=0：[endpoint.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/endpoint.c#L305) L305、L322 `setRegister(thread, badgeRegister, 0)`。

这种设计的关键点：**badge 在内核空间，从不经过用户态缓冲**，所以无法被 sender 篡改。

### 3.2 Airymax：msg_hdr 固定 offset + C-S9 fastpath 校验

Airymax 把 badge 直接放进消息头：

- 位置：[ipc.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/ipc.h#L77) L77-89 `struct airy_ipc_msg_hdr`，其中 `capability_badge` 位于 offset 40（128 字节 Layout C v4）。
- 布局：[ipc.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/ipc.h#L47) L47-63，64 位 badge 分 EPOCH(48) / RANDTAG(16) / PERMS(0)，`AIRY_BADGE_COMPILE` 宏 L56-59 编译期合成，`AIRY_BADGE_EPOCH/RANDTAG/PERMS` 提取宏 L61-63。
- 校验：[airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap.h#L50) L50-77 `airy_cap_badge_ok` fastpath inline，3 次 READ_ONCE + bit ops，约 10ns。
- 权限位：[ipc.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/ipc.h#L66) L66-74 共 7 位（SEND/RECV/CALL/GRANT/REVOKE/FREEZE/BATCH），`ALL=0x007F`、`RESERVED=0xFF80`。

### 3.3 差异与权衡

seL4 的 TCB-embedding 保证 badge 可信；Airymax 把 badge 放进 msg_hdr 后必须依赖 LSM 校验拦截。Airymax 的优势是 badge 与消息一起在用户态可见，便于 trace_id/capability_badge 联动观察；代价是任何未走 uring_cmd hook 直接调用 `airy_ipc_fastpath_send` 的路径都会绕过 badge 校验——这正是 §4 与 §8 关注的核心。

## 4. Badge 校验位置对比

### 4.1 seL4：endpoint 内核路径内嵌

seL4 校验与投递在同一次内核进入内完成：[endpoint.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/endpoint.c#L20) L20 起，badge 从参数到 TCB 到 doIPCTransfer 全程在内核态流转，无"校验与投递分离"的可能。

### 4.2 Airymax：LSM uring_cmd hook + fastpath 不重复校验

Airymax 的校验集中在 LSM 5-phase slowpath：[airy_cap_check.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_check.c#L191) L191-260 `airy_uring_cmd_check`：

- phase1：L210 ring frozen；
- phase2：L228 CAP_REQUEST；
- phase3：L235 DSL 降级；
- phase4：L241 fastpath recheck；
- phase5：L248 slowpath enforce。

badge 从 `ioucmd->pdu[0..7]` 提取（L223-224），`required_perms` 从 `pdu[8..9]` 提取。

而 [airy_ipc_fastpath.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_fastpath.c#L31) L31-32 仅做 frozen 检查，**没有 badge 校验**。这是设计选择：fastpath 假定已被 LSM 放行。

### 4.3 校验分离的副作用

- 优点：fastpath ~158ns 不被 3 次 READ_ONCE 拖累，C-S9 在 LSM 路径完成即"够用一次"。
- 风险：fastpath_send 是导出符号，任何内核模块直调即绕过校验；DSL 降级到固定 0 后（[ipc.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/ipc.h#L107) L107-145 H6）校验意义本身被弱化。

## 5. cancelBadgedSends 对比

### 5.1 seL4：按 badge 取消挂起发送

seL4 在 [endpoint.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/endpoint.c#L476) L476-489 实现 `cancelBadgedSends`：

```c
/* removeAndRestartBadgedThread / cancelBadgedSends(ep, badge) */
```

机制：遍历 endpoint 上所有阻塞的 sender，badge 匹配者被 removeAndRestart（取消发送、回到就绪、消息丢弃）。这给 cap revoke 提供了"原子撤回"语义——revoke 一个 capability 不仅是禁止未来发送，还能把已经在 endpoint 队列里等待的同 badge 发送一并清除。

### 5.2 Airymax：缺失

Airymax 的 SPSC ring 没有"按 badge 取消"的等价 API：

- [airy_ipc_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_ring.c#L100) L100-128 `airy_ipc_ring_consume` 只能按 head→tail 顺序消费，无法选择性丢弃；
- `freeze` 是全环级，不是 badge 级（[airy_ipc_fastpath.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_fastpath.c#L31) L31-32）。

后果：Airymax 的 cap revoke 只能"禁未来"，不能"清当前"。revoke 后已经在 ring slots 里待消费的同 badge 消息仍会被 consumer 处理——这是一个安全语义弱化点，见 §8 改进建议 P1。

## 6. 内存序对比

### 6.1 seL4：单核原子假设

seL4 verified 配置强假设单核或强一致内存模型，IPC 配对在内核态串行，badge 写 TCB 与 badge 读 TCB 不需要 acquire/release 配对——内核态切换本身提供所需 ordering。

### 6.2 Airymax：SPSC acquire/release 配对

Airymax 走 SMP：

- producer：[airy_ipc_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_ring.c#L95) L95 `smp_store_release(&ring->head, next)`；
- consumer：[airy_ipc_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_ring.c#L116) L116 `smp_load_acquire(&ring->head)`。

SPSC 的关键不变式：head 的发布次序保证 consumer 看到 head 推进时，slots 内容已经写入完毕。`frozen` 用 `READ_ONCE`（[airy_ipc_fastpath.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_fastpath.c#L31) L31），但 frozen 翻转需要配对写侧也用 release 语义，否则 fastpath 读到的 frozen=1 与 consumer 看到的 head 不一致——这是个细节，需要在 §8 P2 中明确。

## 7. SC（Scheduling Context）捐赠对比

### 7.1 seL4：endpoint.c L101-103 直接捐赠

seL4 MCS 把 SC 作为可捐赠资源：[endpoint.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/endpoint.c#L101) L101-103 `schedContext_donate(thread->tcbSchedContext, dest)`，紧随 L106-112 的 `refill_sufficient/refill_ready` + `refill_unblock_check` 检查。这保证被动唤醒的 receiver 在配对完成时获得 sender 携带的 budget，避免"被叫醒但没预算跑"。

### 7.2 Airymax：缺失

Airymax fastpath 完全不涉及调度上下文传递：[airy_ipc_fastpath.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_fastpath.c#L21) L21-35 没有 SC 字段操作。Airymax 的 SC 概念由 sched_ctl 单独管理，没有"借调用方 budget 给被叫方"的路径。后果是 Airymax 的被动唤醒 receiver 必须自带 budget，否则会立刻被 scheduler 挂回——这对 latency-sensitive 的 RPC 场景是隐性风险。

## 8. 改进建议

### [P1] 文档化 fastpath_send 不含 Badge 校验的设计决策

- **现状**：[airy_ipc_fastpath.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_fastpath.c#L31) L31-32 仅 frozen 检查；badge 校验全部集中在 [airy_cap_check.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_check.c#L191) L191-260 LSM 5-phase slowpath。`airy_ipc_fastpath_send` 是导出符号，任何直调路径都会绕过 C-S9 校验。
- **参考**：seL4 [endpoint.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/endpoint.c#L20) L20 把 badge 作为内核参数传入，校验与投递在同一内核进入内完成。
- **建议**：
  1. 在 `airy_ipc_fastpath.c` 头部添加注释块明确"caller 必须保证 badge 已由 LSM uring_cmd hook 通过"的前置条件；
  2. 将 `airy_ipc_fastpath_send` 改名为 `airy_ipc_fastpath_send_trusted` 或加 `__airy_trusted_path` 注解，让 reviewer 在 codereview 时一眼识别；
  3. 考虑在 [airy_ipc_internal.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_internal.h#L39) L39-40 的导出声明上使用 `EXPORT_SYMBOL_GPL` 而非 `EXPORT_SYMBOL`，缩小可触达面。
- **风险评估**：改名会影响现有调用方，需要同步更新 airy_uring_cmd hook 内的调用点；零运行时性能影响。

### [P1] 补齐 cancelBadgedSends 等价机制

- **现状**：SPSC ring 无法选择性丢弃；[airy_ipc_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_ring.c#L60) L60-97 的 post 与 L100-128 的 consume 都是 head/tail 顺序推进，不存在"按 badge 移除"。cap revoke 后已在 ring slots 内的同 badge 消息仍会被消费。
- **参考**：seL4 [endpoint.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/endpoint.c#L476) L476-489 `cancelBadgedSends(ep, badge)`。
- **建议**：在 `airy_lsm` 或 `airy_cap` 模块新增 `airy_cap_cancel_badged_sends(agent_id, badge)`：
  - 若 ring 未消费区段内有匹配 badge 的 slot：在 msg_hdr 上打 `AIRY_IPC_F_CANCELLED` 标志（占用 [ipc.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/ipc.h#L40) L40-45 RESERVED 区或 reserved[72]），consumer 读取后丢弃；
  - 若 ring 整段都需要清理：fallback 到 `airy_ipc_ring_freeze`（已有 frozen 字段，见 [airy_ipc_internal.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_internal.h#L23) L23-29）。
- **风险评估**：consumer 改动需要识别 `AIRY_IPC_F_CANCELLED`，会侵入 fastpath ~5ns；建议把检查放在 `airy_ipc_ring_consume` 的 memcpy 之后（[airy_ipc_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_ring.c#L123) L123），代价最小。

### [P2] 评估 airy_ipc_ring_post L71 magic check 的冗余性

- **现状**：[airy_ipc_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_ring.c#L71) L71 在每次 post 都做 magic check（[ipc.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/ipc.h#L18) L18 `AIRY_IPC_MAGIC=0x41524531u`）。但若 caller 已经过 LSM 5-phase + C-S9，msg_hdr 的 magic 已经隐含可信。
- **参考**：seL4 不在 sendIPC 内做 magic 之类的协议校验——校验在 cap_invoke 时完成。
- **建议**：把 magic check 移到 `CONFIG_AIRY_IPC_PARANOID`（默认 off），或仅在 ring init 时校验一次。预期可省下 ~158ns fastpath 中的 ~10-20ns。
- **风险评估**：关闭 magic check 后，若内核 OOB（out-of-band）写入 ring slots，损坏更难定位。建议保留 KASAN hook 以在开发期抓 OOB。

### [P2] 增加 consumed time 上报机制

- **现状**：Airymax 当前没有 seL4 `replyFromKernel_consumed` 等价物——receiver 无法知道 sender 用了多少 budget。
- **参考**：seL4 reply 路径在 [endpoint.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/endpoint.c#L305) L305 / L322 的 `setRegister(thread, badgeRegister, 0)` 给出回复 badge=0，类似寄存器机制可承载 consumed。
- **建议**：在 slowpath（[airy_cap_check.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_check.c#L248) L248 phase5）或 sched_ctl 上报 consumed_ns；msg_hdr 的 `reserved[72]` 区（[ipc.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/ipc.h#L77) L77-89）可复用 16 字节作为 reply consumed 字段。
- **风险评估**：reserved 区语义复用需要在 ABI 版本表里登记，避免 v3.6 之后被复用冲突；同时需在 [ipc.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/ipc.h#L91) L91-105 的 `_Static_assert` 校验集中补一条 offset 断言。

## 9. 总结

seL4 与 Airymax 在 IPC 设计上代表了两代工程哲学：

- seL4 把"身份"、"投递"、"调度预算"、"撤销"四件事压在一次内核进入内同步完成，badge 始终在内核态，永不外泄到用户可见缓冲；代价是同步阻塞与单核假设。
- Airymax 把投递异步化（SPSC）、把校验 LSM 化（5-phase）、把 badge 显式化（msg_hdr offset 40 + C-S9 fastpath），换取用户态可观测性与 ~158ns 量级的 fastpath；代价是"投递与校验分离"的语义窗口、cancel-by-badge 的缺失、SC 捐赠的缺失。

报告识别出 4 项改进点，其中 2 项 P1（fastpath 前置条件文档化、cancelBadgedSends 补齐）建议在 v3.6 → v3.7 周期内立项；2 项 P2（magic check 精简、consumed 上报）可在 v3.7 之后再评估。Airymax 不必照搬 seL4 同步语义——补齐 cancel 与文档化校验前置条件，即可在不放弃异步优势的前提下，收回 seL4 留下的"撤销原子性"与"投递可信链"两项关键安全语义。
