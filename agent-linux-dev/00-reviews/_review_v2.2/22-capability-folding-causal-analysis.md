# 22 — Capability Folding 融合推论验证报告

## "如果加入，A-IPC 的六个维度会变成什么样？"

> **报告日期**：2026-07-18
> **报告性质**：客观推论验证 — 不评价"是否应该做"，只验证"如果做了，因果链是什么"
> **方法**：逐条推演 Capability Folding 融合前后的差异，量化影响范围
> **前置报告**：[21-ipc-production-readiness.md](file:///home/spharx/SpharxWorks/airymaxhub/docs-closed/agent-linux/00-reviews/_review_v2.2/21-ipc-production-readiness.md)（生产就绪度六维度判定）

---

## 0. 推演方法论

**前提假设**：
1. Capability Folding 融入 Layout C：`reserved[84]` 中编码 `cap_badge`（8B）+ `checksum`（4B）
2. `cap_badge = HMAC-SHA256(cap_id, kernel_secret)` 或更轻量的 keyed hash
3. 数据面 fastpath C-S9 从黑盒变为具体实现：cache lookup → badge verify → inline deny
4. 控制面保留，但仅用于能力管理操作（mint/derive/revoke/policy_load）

**验证逻辑**：对于 21 号审查中的每一项判定（通过/不通过/部分通过），推演融合后的变化。如果有改善，量化改善程度。如果没有改善，说明为什么没有改善。

---

## 1. 推演一：维度三（隔离）— 控制面同步阻塞死锁风险

### 1.1 融合前（21号审查判定：不通过）

```
问题：12 daemon 的网格通信中，控制面的同步阻塞 syscall 可能形成死锁链
根本原因：daemon 使用 airy_sys_send（阻塞）进行数据传递
```

### 1.2 融合后的变化

**关键因果链1：数据消息从控制面迁移到数据面**

当前 12 daemon 的通信可以按频率分为两类：

| 通信类型 | 频率 | 当前路径 | 融合后路径 |
|---------|------|---------|-----------|
| **数据消息**（cogn_d 发送认知任务、gateway_d 路由请求、vfs_d 文件操作、audit_d 审计事件、mem_d 记忆查询） | **高频**（每认知循环数十条） | 控制面 `airy_sys_send` + 数据面 io_uring（混合） | **纯数据面 io_uring SEND/RECV** — 携带 cap_badge |
| **能力操作**（sec_d 授权/撤销 capability、macro_superv 生命周期裁决） | **低频**（策略变更时才触发） | 控制面 `airy_sys_call` | **保持控制面 `airy_sys_call`** |

**关键因果链2：控制面退化为"稀疏管理图"**

融合前，控制面承载 12 daemon 的全部数据消息——这是一个密集网格：

```
控制面通信密度（融合前）：        控制面通信密度（融合后）：
macro_superv ──── cogn_d       macro_superv ──── sec_d（仅能力操作）
    │    ╲    ╱    │               │
    │     ╳  ╳     │               │（其他 daemon 之间的数据消息
    │    ╱    ╲    │                │  全部通过数据面 io_uring，
  sec_d ──── gateway_d             │  不经过控制面）
    │    ╲    ╱    │
    ...
  （密集网格，12×12 方向）          （稀疏图，仅 4×4 能力管理方向）
```

**量化改善**：

| 指标 | 融合前 | 融合后 |
|------|--------|--------|
| 控制面 Syscall 频率 | ~10K-100K calls/s（全部数据消息经过） | ~10-100 calls/s（仅能力操作） |
| 死锁风险概率 | 高（密集网格，每次数据通信都是潜在死锁节点） | **极低**（稀疏图，能力操作不形成环——sec_d 不调用其他 daemon，macro_superv 仅向下管理） |
| 5s 超时的实际影响 | 严重（数据消息 5s 延迟 = Agent 认知循环断裂） | **可接受**（能力操作等待 5s = 策略更新延迟 5s，不影响 Agent 运行） |

### 1.3 推论

**Capability Folding 不会消除控制面死锁的可能性（能力管理操作仍然存在），但会将死锁风险从"密集网格中每次数据通信都可能触发"降级为"稀疏管理图中几乎不可能触发"。**

**维度三判定从"不通过"变为"通过"。**

---

## 2. 推演二：维度四（一致性）— 控制面/数据面能力模型不统一

### 2.1 融合前（21号审查判定：不通过）

```
问题：控制面使用 airy_decode_and_invoke() 校验能力，
      数据面使用 airy_cap_check_fast() 校验能力，
      两条路径不共享代码，能力撤销有 IPI 延迟窗口。
```

### 2.2 融合后的变化

**关键因果链：cap_badge 作为能力的一致标识符**

融合前，能力校验依赖两个不同的标识符：

| 标识符 | 控制面 | 数据面 |
|--------|--------|--------|
| 能力标识 | `cap` 参数（syscall 传入） | 消息头 `flags` 的 `AIRY_IPC_F_CAP_CARRY` |
| 校验方式 | `cap_rights_check + cap_type_check` | `airy_cap_check_fast()`（缓存查询） |
| 校验结果 | 立即 | 缓存命中时立即，未命中时降级 |

融合后，**cap_badge 是唯一的、跨平面的能力证明**：

```
控制面（sec_d 授权时）：                数据面（消息传递时）：
cap_id → generate cap_badge            消息头 嵌入 cap_badge
         = hash(secret, cap_id)                ↓
         ↓                              fastpath C-S9:
存储到内核 radix tree                   ① cache lookup: cap_badge in cache?
         ↓                             ② 若命中 → 比对 → PASS/REJECT
控制面 `airy_sys_call` 中使用           ③ 若未命中 → 完全校验:
同一个 cap_badge 查找                       cap_badge == hash(secret, cap_id)?
                                           是 → 更新缓存 → PASS
                                           否 → REJECT (AIRY_ECAPABILITY)
```

**关键因果链：cap_badge 自带防伪造能力**

这是 Capability Folding 对一致性的最大贡献：

- **融合前**：数据面 fastpath 仅查缓存。如果缓存未命中（新 Agent、冷启动），必须降级到 slowpath（~10μs）。更关键的是，一个恶意 Agent 可以声称持有任何 cap_id——如果它恰好命中一个过期的缓存条目，就能通过。
- **融合后**：数据面 fastpath 可以独立验证 cap_badge 的真伪。cap_badge 只能由内核/ sec_d 生成（需要 kernel_secret），恶意 Agent 无法伪造。即使缓存命中一个过期的条目，badge 比对也会失败。

**关于 IPI 延迟窗口的修正**：

21号审查指出"能力撤销后，IPI 有 1-5μs 延迟，数据面可能通过已撤销的能力"。融合后：

- 缓存命中且 badge 匹配 + 条目状态为 REVOKED → REJECT（无论 IPI 是否到达）
- 缓存命中且 badge 匹配 + 条目状态为 ACTIVE → PASS（正常路径）

**IPI 延迟窗口仍然存在**——如果缓存尚未被 IPI 失效，条目状态仍为 ACTIVE。但 cap_badge 提供的额外保护是：**攻击者无法伪造一个"应该被撤销但缓存尚未更新"的能力**——因为攻击者没有 kernel_secret。

### 2.3 推论

**Capability Folding 不会完全消除 IPI 延迟窗口（物理上不可能），但消除了"伪造能力"这一攻击面。控制面和数据面现在使用同一个 cap_badge 作为能力证明，能力模型从"双轨制"变为"单轨制"。**

**维度四判定从"不通过"变为"通过——带已知约束（IPI 窗口仍存在）。"**

---

## 3. 推演三：维度五（恢复）— 控制面恢复

### 3.1 融合前（21号审查判定：部分通过）

```
问题：控制面 daemon 崩溃后，阻塞在 airy_sys_send 上的发送方冻结 5 秒
```

### 3.2 融合后的变化

**关键因果链：控制面不再承载数据消息，崩溃的影响范围缩小**

融合前：
- cogn_d 崩溃 → 所有向 cogn_d 发送数据消息的 daemon（gateway_d, mem_d, macro_superv）冻结 5 秒
- **影响：3+ 个 daemon 同时冻结 → 整系统降级**

融合后：
- cogn_d 崩溃 → 数据面的 io_uring ring 不可用 → MSG_RING 立即返回 -EINVAL（不需要 5s）
- 控制面仅 sec_d 在策略更新时可能调用 cogn_d → 低概率、低频次

**量化改善**：

| 指标 | 融合前 | 融合后 |
|------|--------|--------|
| 单个 daemon 崩溃影响的其他 daemon 数量 | 3-5 个（所有向它发送控制面消息的 daemon） | 0-1 个（仅 sec_d 在能力操作时可能受影响） |
| 冻结时长 | 5s（控制面超时） | 立即（数据面返回 -EINVAL）或 5s（仅能力操作） |
| 整系统恢复时间 | 5s（最坏） | < 100ms（数据面立即感知 + 重启恢复） |

### 3.3 推论

**Capability Folding 通过将数据通信从控制面剥离，使得 daemon 崩溃的影响从"多 daemon 级联冻结"缩小为"单 daemon 数据面不可用 + 能力操作可能超时"。**

**维度五判定从"部分通过"变为"通过"。**

---

## 4. 推演四：Capability Folding 不能解决的问题

### 4.1 仍然存在的问题

| 问题 | 来源 | 为什么 Capability Folding 无法解决 |
|------|------|----------------------------------|
| **MSG_RING 12方网格锁争用** | 21号审查维度六 | cap_badge 不改变 io_uring 的 uring_lock 机制——12 daemon 的 MSG_RING 仍然需要 trylock 对方的 ring |
| **io-wq 饱和风险** | 21号审查维度六 | cap_badge 不改变 MSG_RING punt-to-io-wq 的机制 |
| **三通道消息排序无保证** | 19号审查 D1 | cap_badge 嵌入的是**能力证明**而非**序列号**——不解决 io_uring/kfifo/MSG_RING 之间的顺序问题 |
| **BATCH 部分失败假设** | 19号审查 D2 | cap_badge 校验在 BATCH 聚合后——整批提交，无法部分失败 |
| **per-CPU kfifo 抢占** | 19号审查 D3 | kfifo 是内核 kthread 通道，不使用 io_uring，cap_badge 不相关 |
| **Reconciliation ring 销毁竞态** | 19号审查 D4 | cap_badge 不改变 ring 生命周期管理 |
| **CLOCK_REALTIME 回拨** | 19号审查 D6/D7 | 时间戳问题 |

**共计 7 个已知问题中的 5 个不受 Capability Folding 影响。**

### 4.2 受 Capability Folding 直接影响的问题

| 问题 | 改善程度 |
|------|---------|
| 控制面同步阻塞死锁（维度三） | **大幅改善** — 数据通信移出控制面 |
| 能力模型不一致（维度四） | **根本解决** — cap_badge 统一了两个平面的能力证明 |
| daemon 崩溃恢复（维度五） | **大幅改善** — 影响面从多 daemon 缩小为单 daemon |

---

## 5. 六维度再判定

| 维度 | 融合前 | 融合后 | 变化原因 |
|------|:---:|:---:|---------|
| **吞吐** | ✅ 通过 | ✅ 通过 | 不受影响 |
| **延迟** | ✅ 通过 | ⚠️ 需验证 | fastpath 增加 badge verify + CRC32（~60ns），仍在预算内 |
| **隔离** | ❌ 不通过 | ✅ 通过 | 数据通信移出控制面，死锁风险从密集网格降为稀疏管理图 |
| **一致性** | ❌ 不通过 | ✅ 通过（带已知约束） | cap_badge 统一能力证明，消除双轨制，IPI 窗口仍存在但攻击面缩小 |
| **恢复** | ⚠️ 部分通过 | ✅ 通过 | daemon 崩溃影响面从 3-5 个缩小到 0-1 个 |
| **上限** | ❌ 不通过 | ❌ 不通过 | MSG_RING 争用、io-wq 饱和与 Capability Folding 无关 |

**融合后：4个通过 + 1个需验证 + 1个不通过（但该不通过项与 Capability Folding 无关）**

---

## 6. 融合的实现代价

### 6.1 Layout C 的修改

```
当前 Layout C:
offset 44: reserved[84]    (84B 保留，填零)

融合后 Layout C:
offset 44: cap_badge       (8B)   = hash(kernel_secret, cap_id, permissions_mask)
offset 52: checksum         (4B)   = CRC32(header[0:44) + payload)
offset 56: negotiated_ver   (2B)   = 握手协商版本
offset 58: __pad            (70B)  = 保留
```

**影响文档**：02-ipc-protocol.md §2 的消息头结构 + 07-ipc-fastpath.md §5.1 的 SQE/CQE 映射表

### 6.2 fastpath C-S9 的实现变化

融合前（黑盒）:
```c
if (likely(airy_cap_check_fast(hdr.dst_task, cap)))  // 未实现
```

融合后（具体实现）:
```c
static int airy_cap_folding_check(const struct airy_ipc_msg_hdr *hdr) {
    struct airy_cap_cache_entry *entry;
    
    rcu_read_lock();
    entry = radix_tree_lookup(&airy_cap_cache, hdr->cap_badge);
    if (entry) {
        /* 缓存命中：比对权限掩码 */
        if (entry->state == AIRY_CAP_REVOKED) { rcu_read_unlock(); return -AIRY_ECAP_REVOKED; }
        if (entry->badge != hdr->cap_badge)     { rcu_read_unlock(); return -AIRY_ECAP_BADGE; }
        rcu_read_unlock();
        return 0;  // PASS
    }
    rcu_read_unlock();
    
    /* 缓存未命中：独立验证 cap_badge */
    if (airy_cap_badge_verify(hdr->cap_badge, hdr->src_task, hdr->dst_task))
        return 0;  // PASS, update cache async
    
    return -AIRY_ECAPABILITY;  // REJECT — inline deny
}
```

### 6.3 新增的内核基础设施

| 组件 | 用途 | 复杂度 |
|------|------|--------|
| `kernel_secret` | 生成 cap_badge 的密钥，仅内核可读 | 低（boot time 生成 256-bit 随机数） |
| `airy_cap_badge_generate()` | `hash(secret, cap_id, mask)` | 低（keyed hash，~50ns） |
| `airy_cap_badge_verify()` | 验证 cap_badge 有效性 | 低（同 hash 比对） |
| CRC32 header 校验 | `crc32_le(0, header, 44) ^ crc32_le(0, payload, len)` | 极低（编译时查表，<10ns） |

---

## 7. 总体推论

**Capability Folding 的融合将使 A-IPC 的生产就绪度从"3/6 通过"提升至"4/6 通过 + 1 需验证"。**

融合不解决 MSG_RING 争用和 io-wq 饱和（需要独立的并发控制设计），但它从根本上改善了 A-IPC 最薄弱的两个维度：
- **隔离**（维度三）：控制面从密集通信网格变为稀疏管理图
- **一致性**（维度四）：从控制面/数据面双轨校验变为 cap_badge 统一证明

这两个改善的共同因果根源是同一个：**cap_badge 将能力证明从"控制面专属"变为"跨平面统一标识"**，从而使得数据面可以独立承载需要能力校验的数据通信，不再依赖控制面的同步阻塞 syscall。

这不是一个"锦上添花"的优化——它解决了 21 号审查中发现的三个"不通过"中的两个。

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
