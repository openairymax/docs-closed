SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 05 — capability/CNode 系统深度对比：seL4 vs Airymax

> **文档定位**：v3.6 深度对比研究 · capability/CNode 子域（cap 表示 / 派生操作 / 撤销语义 / 并发控制）
> **对比基准**：seL4-master `src/object/cnode.c`（cap_t 联合体 + decodeCNodeInvocation）· Airymax agent-linux `security/airy/airy_cap_derive.c`（64-bit Badge + 7 CNode 操作）
> **最后更新**：2026-07-30
> **方法论**：逐行阅读 seL4 `cnode.c` 全量 `decodeCNodeInvocation`/`invokeCNode*` 与 Airymax `airy_cap_derive.c` 全量 `airy_cap_derive`；所有引用标注文件路径与行号；严禁编造行号，行号均经 `cat -n` 交叉核验

---

## 1. 研究范围与对比维度

| 维度 | seL4 | Airymax |
|------|------|---------|
| cap 表示 | `cap_t` 联合体（多类型 cap：cnode/endpoint/ntfn/tcb/...） | `typedef __u64 cap_t`（64-bit 标量 Badge） |
| 操作集 | 7 MCS 操作 + SaveCaller(非 MCS) | 7 操作（对应 MCS 集，不实现 SaveCaller） |
| 权限降级 | `deriveCap` + `maskCapRights`（Copy/Mint 均降级） | COPY 不降级；MINT 降级（`new_perms & src->perms`） |
| badge 写入 | `updateCapData`（Mint/Mutate/Rotate） | `AIRY_BADGE_COMPILE`（MINT/MUTATE/ROTATE） |
| 撤销语义 | `cteRevoke` 递归（MDB 父子链，级联） | per-agent `epoch+1`（O(1) 定向，**非级联**） |
| cancelBadgedSends | 完整（`cancelBadgedSends(ep, badge)`） | **缺失** |
| 并发控制 | per-cte 锁（`cte_t` 粒度） | 全局单一 `spinlock`（1024 槽共享） |
| Rotate | 3 槽交换（pivot/src/dest） | 单槽 `randtag` 轮换 |
| 存储结构 | CNode 树 + MDB 父子链 | 平面数组 `agent_caps[1024]` |

---

## 2. cap 表示：seL4 cap_t 联合体 vs Airymax 64-bit 标量

### 2.1 seL4 多类型联合体

seL4 的 `cap_t` 是联合体，承载 CNode/Endpoint/Notification/TCB/Untyped/Page 等十余种能力类型。`decodeCNodeInvocation` 入口对类型做严格断言 `assert(cap_get_capType(cap) == cap_cnode_cap)`（[cnode.c L51](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L51)）。只有 `cap_cnode_cap` 才进入 CNode 分发，使 seL4 的 capability 空间是**异构**的——同一 CSpace 内可并存不同类型 cap，由 `cap_type` 标签决定可施加的操作。

### 2.2 Airymax 单一 Badge 标量

Airymax 将 capability 折叠为 64-bit 标量 `typedef __u64 cap_t`（[security_types.h L20](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/security_types.h#L20)），按 `EPOCH<<48 | RANDTAG<<16 | PERMS` 布局（[ipc.h L47-59](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/ipc.h#L47)），由 `AIRY_BADGE_COMPILE` 宏组装。`airy_cap_slot`（[lsm_types.h L45-53](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/lsm_types.h#L45)）以 64 字节对齐存放 badge/agent_id/flags/randtag/perms/epoch，1024 槽以平面数组 `agent_caps` 暴露（[airy_ipc_capability.c L29-32](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/ipc/airy_ipc_capability.c#L29)）。

### 2.3 评价

seL4 联合体支持异构 cap 空间，代价是每次操作需 `cap_get_capType` 分发与类型断言。Airymax 选择**同构**模型：所有 cap 都是同一 64-bit badge，类型信息折叠进 perms 字段，fastpath（[airy_cap.h L49-76](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap.h#L49)）仅需 3 次 `READ_ONCE` + 位运算即完成校验，约 10ns。这是用表达力换性能的工程取舍——Airymax 不需 seL4 那样细粒度的内核对象授权，只需"代理身份 + 权限位 + 防伪随机标签 + 撤销 epoch"。

---

## 3. CNode 操作集：7 MCS 操作 + SaveCaller vs Airymax 7 操作

### 3.1 seL4 操作集随 MCS 配置分叉

seL4 在 [cnode.c L36-40](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L36) 通过 `CONFIG_KERNEL_MCS` 宏定义 `CNODE_LAST_INVOCATION`：MCS 内核为 `CNodeRotate`，非 MCS 内核为 `CNodeSaveCaller`。即 MCS 支持 Copy/Mint/Move/Mutate/Revoke/Delete/Rotate 共 7 操作，非 MCS 用 SaveCaller 替换 Rotate。`decodeCNodeInvocation` 在 [L53-57](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L53) 校验 `invLabel` 范围，[L59-63](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L59) 校验长度，Copy/Mint/Move/Mutate 共享参数解析（[L74-193](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L74)），由 `switch(invLabel)` 在 [L115](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L115) 分派。

### 3.2 Airymax 7 操作精确对应 MCS 集

Airymax 在 [security_types.h L82-92](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/security_types.h#L82) 定义 `enum airy_cap_op`（COPY=0/MINT=1/MOVE=2/MUTATE=3/REVOKE=4/DELETE=5/ROTATE=6），注释明确"seL4 CNode 7 Derivation Operations"。`airy_cap_derive`（[airy_cap_derive.c L50-51](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L50)）以单一 `switch(op)`（[L76](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L76)）分派，操作名表见 [L30-32](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L30)。Airymax **不实现 SaveCaller**——合理选择，因 SaveCaller 与 MCS 的 Reply 语义强绑定，而 Airymax 采用 Linux 既有调度模型，无独立 Reply cap 概念。

---

## 4. 权限降级：deriveCap+maskCapRights vs COPY 不降级/MINT 降级

### 4.1 seL4 Copy 与 Mint 均经 maskCapRights 降级

seL4 `CNodeCopy`（[cnode.c L116-134](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L116)）通过两步实现权限子集：

```c
cap_rights = rightsFromWord(getSyscallArg(4, buffer));   /* L124 */
srcCap = maskCapRights(cap_rights, srcSlot->cap);        /* L125 */
dc_ret = deriveCap(srcSlot, srcCap);                     /* L126 */
```

`maskCapRights` 按调用方提供的 `cap_rights` 截断源 cap 权限，`deriveCap`（[L126](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L126)）再按目标 cap 类型做类型安全的派生（例如 Untyped cap 派生 Page cap）。`CNodeMint`（[L136-155](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L136)）同样在 [L145](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L145) 调用 `maskCapRights`，区别仅在于 Mint 额外写 badge。

### 4.2 Airymax COPY 明确不降级，仅 MINT 降级

Airymax `AIRY_CAP_OP_COPY`（[airy_cap_derive.c L78-103](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L78)）在 [L93](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L93) 注释"Copy badge unchanged (no demotion)"，[L94-99](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L94) 直接复制全部字段，**不调用任何权限掩码逻辑**：

```c
/* Copy badge unchanged (no demotion) */
dst->badge    = src->badge;
dst->agent_id = dst_agent;
dst->flags    = src->flags;
dst->randtag  = src->randtag;
dst->perms    = src->perms;       /* 原样复制，不与 new_perms 求交 */
dst->epoch    = src->epoch;
```

权限降级仅由 `AIRY_CAP_OP_MINT` 承担（[L106-136](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L106)），在 [L124](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L124) 以 `perms = new_perms & src->perms` 求交集（may demotion），再于 [L126](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L126) 用 `AIRY_BADGE_COMPILE` 重组 badge。

### 4.3 语义差异

seL4 中 Copy 与 Mint 的本质差异是"是否写 badge"（Mint 写、Copy 不写），二者都支持权限降级。Airymax 把"是否降级"作为 Copy/Mint 的区分维度：Copy = 原样克隆（含权限），Mint = 可降级 + 重组 badge。这导致 Airymax 的 COPY **无法**生成权限子集——若调用方想"复制一份权限更小的 cap"，必须用 MINT 而非 COPY。

---

## 5. badge 写入：updateCapData vs AIRY_BADGE_COMPILE

### 5.1 seL4 updateCapData 按类型分派

seL4 的 `updateCapData` 是类型相关的：对 CNode cap 写 guard/bits，对 Endpoint cap 写 badge。`CNodeMint` 在 [L147](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L147) 以 `updateCapData(false, capData, srcCap)` 写 badge（`false` 表示非强制），`CNodeMutate` 在 [L171](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L171) 以 `updateCapData(true, capData, srcSlot->cap)` 强制更新。`CNodeRotate` 在 [L292-293](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L292) 对 src/pivot 各调用一次。

### 5.2 Airymax AIRY_BADGE_COMPILE 宏组装

Airymax 不区分 cap 类型，badge 写入统一通过 `AIRY_BADGE_COMPILE(epoch, randtag, perms)` 宏（[ipc.h L56-59](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/ipc.h#L56)）：

- MINT（[L126](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L126)）：以源 epoch/randtag + 降级后 perms 重组 badge 写入 dst。
- MUTATE（[L180-182](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L180)）：原地保留 epoch/randtag，仅替换 perms，并同步重写 badge。
- ROTATE（[L238-239](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L238)）：保留 epoch/perms，替换 randtag，重写 badge。

seL4 的 `updateCapData` 是函数调用，内部按 `cap_type` switch；Airymax 的 `AIRY_BADGE_COMPILE` 是纯位运算宏，零分支开销，但失去了"按类型校验 capData 合法性"的能力（seL4 会在 `updateCapData` 返回 `cap_null_cap` 表示非法，见 [L181-185](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L181) 的空 cap 校验）。

---

## 6. 撤销语义：cteRevoke 递归(MDB) vs per-agent epoch+1(非级联)

> 这是两套系统**最深刻的语义差异**，直接影响安全模型的正确性边界。

### 6.1 seL4 cteRevoke 通过 MDB 父子链级联撤销

seL4 `CNodeRevoke` 经 `invokeCNodeRevoke` 直接调用 `cteRevoke(destSlot)`（[cnode.c L315-318](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L315)）。`cteRevoke` 沿 Capability Derivation Tree（CDT/MDB 父子链）递归撤销**所有从该 cap 派生的子孙 cap**。若 A 派生 B、B 派生 C，对 A 执行 Revoke 将使 B、C 一并失效。这是 seL4 能力安全的核心保证：父 cap 持有者可随时收回所有授权。

### 6.2 Airymax per-agent epoch+1 仅使目标 agent 自身失效

Airymax `AIRY_CAP_OP_REVOKE`（[airy_cap_derive.c L189-205](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L189)）只递增目标 slot 的 epoch 并清零 randtag：

```c
__u16 old_epoch = READ_ONCE(src->epoch);
__u16 new_epoch_val = old_epoch + 1;
WRITE_ONCE(src->epoch, new_epoch_val);     /* L200 */
WRITE_ONCE(src->randtag, 0);               /* L201 */
```

fastpath（[airy_cap.h L61-64](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap.h#L61)）校验 `badge_epoch == slot_epoch`，故 epoch 递增后，该 agent 持有的旧 badge 立即失效。但**关键局限**：若 agent A 的 cap 已被 MINT 到 agent B（[L122-131](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L122)），B 的 slot 拥有独立的 epoch 字段（`dst->epoch = src->epoch`，[L131](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L131)），A 的 REVOKE 只改 A 的 epoch，**B 的 cap 不受影响**。换言之，Airymax 的 REVOKE 语义是"撤销该 agent 自身现有授权"，而非 seL4 的"撤销所有派生授权"。

Airymax 的全局撤销走另一条路径——`airy_cap_epoch_bump_all`（[airy_ipc_capability.c L74-84](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/ipc/airy_ipc_capability.c#L74)）O(N) 遍历 1024 槽递增每个 agent 的 epoch 并 `atomic_inc` 全局 epoch，属 UNFREEZE 语义，而非单 cap 的级联撤销。

---

## 7. cancelBadgedSends：seL4 完整 vs Airymax 缺失

seL4 `CNodeCancelBadgedSends`（[cnode.c L218-230](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L218)）先校验 `hasCancelSendRights`，再经 `invokeCNodeCancelBadgedSends`（[L324-333](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L324)）取出 endpoint 指针与 badge，调用 `cancelBadgedSends(ep, badge)` 清除所有挂在该 endpoint 上、携带指定 badge 的待发送消息。这解决了真实问题：发送方持 badge 的 IPC 可能已阻塞在 endpoint 队列上，单纯撤销 cap 无法丢弃这些挂起消息。Airymax 当前**未实现**等价机制——`airy_cap_derive.c` 7 操作中无对应项，`airy_ipc_capability.c` 也未暴露相关接口。若 Airymax IPC 路径存在基于 badge 的阻塞发送队列，则 REVOKE/DELETE 后这些挂起消息将成为孤儿。

---

## 8. 并发控制：seL4 per-cte vs Airymax 全局单一 spinlock

### 8.1 seL4 cte 粒度锁

seL4 的 `cteInsert`/`cteMove`/`cteRevoke` 等操作在 `cte_t` 粒度加锁（具体锁实现随架构），不同 CSpace、同一 CSpace 内不相关 slot 的操作可并行。这是 seL4 作为微内核在多核上的可扩展性基础。

### 8.2 Airymax 全局 spinlock

Airymax 在 [airy_cap_derive.c L27](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L27) 定义单一全局自旋锁 `DEFINE_SPINLOCK(airy_cap_derive_lock)`。`airy_cap_derive` 在 [L59](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L59) `spin_lock_irqsave` 后，所有 7 操作全程持锁直到 [L254](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L254) `spin_unlock_irqrestore`。任意两个 agent 的派生操作**串行化**——即便操作完全不相关的 slot。注释（[L45-48](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L45)）解释此举为关闭"slot 状态检查与后续写入的 TOCTOU 窗口"，且 `get_random_u32()`/`atomic_inc()` 非睡眠、可在 spinlock 下安全调用。在 1024 agent 高并发场景下，每次 REVOKE（仅递增一个 epoch）也要与全局所有派生操作争用同一锁，成为瓶颈。

---

## 9. Rotate：3 槽交换 vs 单槽 randtag 轮换

### 9.1 seL4 CNodeRotate 三槽原子交换

seL4 `CNodeRotate`（[cnode.c L232-310](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L232)）是三槽操作：pivot/src/dest。它先校验 pivot 与 src/dest 不重名（[L265-269](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L265)），对 src/pivot 各做 `updateCapData(true, ...)`（[L292-293](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L292)），再经 `invokeCNodeRotate`（[L349-360](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L349)）完成：若 `slot1==slot3` 走 `cteSwap`，否则两次 `cteMove`。Rotate 用于在不丢 cap 的前提下原子重排 CSpace。

### 9.2 Airymax ROTATE 单槽 randtag 轮换

Airymax `AIRY_CAP_OP_ROTATE`（[airy_cap_derive.c L222-241](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L222)）语义完全不同——不交换 slot，而是原地轮换单个 slot 的 `randtag`：先 `get_random_u32()`（[L226](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L226)）取新 tag，再以 `smp_store_release` 先写 randtag（[L237](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L237)）后写 badge（[L238-239](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L238)，`AIRY_BADGE_COMPILE`）。这是**防伪刷新**：旧 randtag 立即失效，缓存的旧 badge 不再通过 fastpath C-S9.2 校验（[airy_cap.h L66-69](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap.h#L66)）。`smp_store_release` 保证 randtag 先于 badge 写入，避免弱序架构读到"新 badge + 旧 randtag"的瞬态不一致。Airymax ROTATE 与 seL4 同名异义——前者刷新防伪标签，后者重排 cap 槽位。

---

## 10. 改进建议

### [P1] REVOKE 无级联撤销

- **现状**：Airymax `AIRY_CAP_OP_REVOKE`（[airy_cap_derive.c L189-205](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L189)）仅递增目标 agent 自身 epoch（[L200](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L200)），已 MINT 到其他 agent 的派生 cap 不受影响。
- **参考**：seL4 `invokeCNodeRevoke` → `cteRevoke`（[cnode.c L315-318](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L315)）沿 MDB 父子链递归撤销所有派生 cap。
- **建议**：二选一——(a) 在 `airy_cap_slot` 增加 `derive_parent` 字段（指向源 agent）构建派生树，REVOKE 时沿树递归失效；或 (b) 显式文档化"Airymax REVOKE 语义为 per-agent 非级联"，并在 enum 注释（[security_types.h L88](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/security_types.h#L88)）将"Revoke capability globally"更正为"Revoke per-agent (non-cascading)"，避免与 seL4 语义混淆。
- **风险**：方案(a) 增加 1024 槽的内存开销与递归撤销延迟，且需在 MINT/COPY 时维护 parent 链，改动面大；方案(b) 零代码风险，但需同步更新安全模型文档与测试用例。

### [P1] COPY 不支持权限子集

- **现状**：Airymax COPY（[airy_cap_derive.c L78-103](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L78)）在 [L93](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L93) 明确"no demotion"，[L98](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L98) 原样复制 perms，调用方无法通过 COPY 获得权限子集。
- **参考**：seL4 `CNodeCopy`（[cnode.c L124-126](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L124)）通过 `maskCapRights` 支持权限降级，Copy 与 Mint 均可降级。
- **建议**：为 `airy_cap_derive` 的 COPY 分支增加可选 `new_perms` 参数（当 `new_perms != 0` 时取 `new_perms & src->perms`），或在文档中明确"权限降级仅通过 MINT 实现，COPY 是原样克隆"，并在 enum 注释（[security_types.h L84](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/security_types.h#L84)）补注。
- **风险**：若改 COPY 签名，所有调用点需同步；若仅文档化，需确保调用方理解"想要降级必须用 MINT"。

### [P1] 全局单一 spinlock 可扩展性

- **现状**：`airy_cap_derive_lock`（[airy_cap_derive.c L27](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L27)）保护全部 1024 槽，[L59](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L59) 入锁、[L254](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive.c#L254) 出锁，任意两 agent 派生操作串行化。
- **参考**：seL4 以 `cte_t` 粒度加锁，不相关 slot 可并行。
- **建议**：改为 per-bucket 锁（如 64 个 bucket，按 `agent_id >> 4` 散列）或 per-agent 锁（每个 slot 内嵌 `spinlock_t`，但 `airy_cap_slot` 已 64 字节对齐，需评估 cacheline 占用）。REVOKE/DELETE 等单 slot 操作只需持自身锁；COPY/MINT/MOVE 涉及 src+dst 两锁，按 agent_id 升序加锁避免死锁。
- **风险**：多锁引入死锁风险，需严格锁序；`airy_cap_epoch_bump_all`（[airy_ipc_capability.c L74-84](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/ipc/airy_ipc_capability.c#L74)）需改为遍历持所有 bucket 锁或改用 RCU，改动面较大。

### [P2] 缺少 cancelBadgedSends

- **现状**：Airymax 7 操作无 cancelBadgedSends 对应项；REVOKE/DELETE 后，已阻塞在 IPC 发送队列上的 badge 消息成为孤儿。
- **参考**：seL4 `CNodeCancelBadgedSends`（[cnode.c L218-230](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L218)）+ `invokeCNodeCancelBadgedSends`（[L324-333](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L324)）。
- **建议**：若 Airymax IPC 路径存在基于 badge 的阻塞发送队列，增加 `airy_cap_cancel_badged_sends(agent_id, badge)` 接口，在 REVOKE/DELETE 时联动调用；若 IPC 无此队列（纯 io_uring 命令模型，无阻塞发送端），则文档化"无需 cancelBadgedSends"决策。
- **风险**：需先确认 Airymax IPC 是否存在 badge 粒度的阻塞发送语义，否则可能引入不必要的复杂度。

### [P2] 缺少 derive_tree（派生关系追踪）

- **现状**：`agent_caps[1024]`（[airy_ipc_capability.c L29-32](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/ipc/airy_ipc_capability.c#L29)）为平面数组，slot 间无父子关系，无法支持级联撤销。
- **参考**：seL4 MDB 维护 cap 派生父子链，`cteRevoke` 据此递归。
- **建议**：与 [P1] REVOKE 建议联动——若决定支持级联撤销，需在 `airy_cap_slot` 增加 `derive_parent`（源 agent_id）字段；若决定保持非级联语义，则文档化"Airymax 刻意不维护派生树，以 O(1) epoch 撤销换取简化"的设计决策。
- **风险**：维护派生树在 MINT/COPY/MOVE 时需额外写入，且 REVOKE 递归深度不可控（最坏 O(N)）；非级联方案需明确安全边界。

### [P2] 不实现 CNodeSaveCaller 的决策应文档化

- **现状**：Airymax 7 操作对应 seL4 MCS 集，不实现非 MCS 的 `CNodeSaveCaller`。
- **参考**：seL4 [cnode.c L36-40](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L36) 通过 `CONFIG_KERNEL_MCS` 在 `CNodeRotate` 与 `CNodeSaveCaller` 间二选一；`invokeCNodeSaveCaller`（[L362-389](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c#L362)）操作 `tcbCaller` 槽的 reply cap。
- **建议**：在 `airy_cap_derive.c` 顶部注释或安全设计文档中说明"Airymax 采用 Linux 既有调度与回复模型，无独立 Reply cap 概念，故不实现 SaveCaller"。
- **风险**：纯文档改动，零代码风险。

---

## 11. 总结

Airymax 的 capability 系统在**操作集层面**与 seL4 MCS 高度对齐——7 派生操作一一对应。但在**语义层面**存在三处关键分叉：撤销非级联（seL4 `cteRevoke` 递归 vs Airymax per-agent epoch+1，已派生到其他 agent 的 cap 不受影响，最需文档化或补强）；权限降级路径不同（seL4 Copy/Mint 均降级 vs Airymax 仅 MINT 降级、COPY 原样克隆）；并发模型（seL4 per-cte 并行 vs Airymax 全局 spinlock 串行）。此外 ROTATE 同名异义（防伪刷新 vs 槽位重排）、cancelBadgedSends 缺失。这些差异并非缺陷，而是 Airymax 以"64-bit 标量 badge + 平面数组 + O(1) epoch 撤销"换取 fastpath ~10ns 极致性能的工程取舍。当前最紧迫的工作是**文档化语义边界**（REVOKE 非级联、COPY 不降级、ROTATE 语义、无 SaveCaller），其次在高并发场景评估 per-bucket 锁改造收益。
