# 23 — Native Word Capability Folding 重构评估报告

## "Badge + Epoch 方案对 A-IPC 全栈的影响分析"

> **报告日期**：2026-07-18
> **报告性质**：客观推论验证 — 评估 Native Word（64-bit Badge+Epoch）方案是否需要全面重构、是否存在风险、是否提升稳健性
> **评估标准**：
> - 是否需要全面重构设计？→ 逐层分析修改范围
> - 是否有风险？→ 枚举风险点 + 可缓解性
> - 是否更完善和稳健？→ 量化对比融合前后的六维度 + 工程复杂度
> **前置报告**：[21-ipc-production-readiness.md](file:///home/spharx/SpharxWorks/airymaxhub/docs-closed/agentrt-linux/00-reviews/_review_v2.2/21-ipc-production-readiness.md) / [22-capability-folding-causal-analysis.md](file:///home/spharx/SpharxWorks/airymaxhub/docs-closed/agentrt-linux/00-reviews/_review_v2.2/22-capability-folding-causal-analysis.md)

---

## 0. Native Word 方案的定义

```
64-bit Native Word = Badge（高 32 bits：Epoch 能力代际编号） + Badge（低 32 bits：权限位掩码）

格式：
[63:32]  Epoch        — 能力代际编号（控制面在连接建立期编译）
[31:0]   Permissions  — 权限位掩码（每位对应一种操作权限）

运行时验证（数据面）：
  if ((badge >> 32) != current_epoch)  → REJECT  （Epoch 不匹配，能力已失效）
  if ((badge & required) != required)  → REJECT  （权限不足）
  → PASS

成本：两条 CPU 指令（移位 + 位运算），~5-10ns
```

**核心洞察**：这个方案消除了数据面对控制面的**所有**运行时依赖——不再需要 cache lookup、不再需要 radix tree 查询、不再需要 IPI 缓存失效。

---

## 1. 问题一：是否需要全面重构设计？

### 1.1 逐层分析修改范围

| A-IPC 层 | 当前设计 | Native Word 融合后 | 变化程度 |
|---------|---------|-------------------|:------:|
| **Layer 0: 传输层**（io_uring SQE/CQE/kfifo） | IORING_OP_URING_CMD + registered buffer | **不变** | 0% |
| **Layer 1: 协议层**（128B 消息头 Layout C） | reserved[84] 全零 | reserved[0:7] = `__u64 capability_badge` | **< 5%**（仅改动 reserved 的 8 字节） |
| **Layer 2: 语义层**（fastpath 状态机 8 态 + C-S1~C-S10） | C-S9 = `airy_cap_check_fast()` 黑盒 | C-S9 = 两条 CPU 指令（epoch check + bitwise AND） | **< 5%**（仅改动一个条件检查的实现） |
| **Layer 3: 原语层**（Channel/Socket/FIFO/Eventpair） | 设计概念，未实现 | 所有原语的消息头均自动携带 capability_badge | **不变**（由协议层统一处理） |
| **Layer 4: 应用层**（12 daemon IPC 拓扑） | 使用控制面 syscall + 数据面 io_uring | 数据通信完全走数据面 io_uring + cap_badge | **~20%**（通信路径变化） |
| **Layer 5: 韧性层**（数据面自治三原则） | Ring 解耦 + 离线缓存 + Reconciliation | 离线缓存变为离线 Epoch 快照（更简单） | **~30%**（离线缓存校验机制简化） |
| **Layer 6: 版本层**（协商 + 兼容） | 握手协商版本 | **不变** | 0% |
| **Layer 7: 性能层**（SLO + 基准） | 单核 250K msg/s，P99 4.2μs | fastpath 延迟从 ~160ns → ~5-10ns | **~5%**（仅 fastpath 数值改善） |
| **Layer 8: 安全层**（Capability + LSM） | 纯 C LSM + radix tree cache | Epoch 代际管理替代 cache | **~40%**（能力模型从"运行时校验"变为"编译时嵌入 + 运行时位运算"） |

### 1.2 判定

**不需要全面重构设计。** Native Word 方案是 A-IPC 协议层的局部增强——仅修改 Layout C 的 8 个 reserved 字节和 fastpath 的一个条件检查。8 层中的 4 层完全不变（0%），3 层小幅修改（<30%），仅安全层的变化较大（40%），但安全层的变化方向是**简化**而非复杂化（Epoch 替代 radix tree cache + IPI coherency）。

对比：
- 不融合 Capability Folding：A-IPC 的设计不变，但 21 号审查判定三维度不通过
- 融合 hash-based Capability Folding（22号审查）：6 层小幅修改，需要 keyed hash + CRC32 + cache lookup
- 融合 Native Word（本次）：**更少的修改，更简单的实现**——因为不需要 hash 计算和 cache lookup

---

## 2. 问题二：是否有风险？

### 2.1 风险一：Epoch 溢出

| 风险 | 量化 | 缓解 |
|------|------|------|
| 32-bit Epoch 计数器溢出 | 1 次/秒 revocation = 136 年 | 可接受。如果 revocation 频率 > 1 次/秒，128 年仍有充足余量 |
| Epoch 溢出后 wraps around | 旧 Badge 重新变为有效 | 在 0 值转换时增加 grace period：旧 Epoch=0xFFFFFFFF → 新 Epoch=1，中间不允许授权新 capability |

**可缓解性**：高。32-bit Epoch 在 revocation 频率 < 10次/秒 时足够使用 13 年。

### 2.2 风险二：Epoch 递增后的消息丢失

| 风险 | 量化 | 缓解 |
|------|------|------|
| Epoch 从 N → N+1 后，已在数据面传输中的消息（携带 Epoch=N 的 Badge）被拒绝 | 在途消息数量 = ring buffer 中的消息数（≤ 32768） | 两阶段 Epoch 递增：(1) 标记 "epoch_transition"，停止接受新 Epoch=N 的消息 → (2) 等待在途消息排空（最多 32768 × fastpath 延迟 ≈ 5ms）→ (3) 递增 Epoch → 清除 "epoch_transition" |
| 在途消息的发送方不知道 Epoch 已变 | 发送方继续使用旧 Badge | 发送方在 fastpath C-S9 中收到 REJECT → 重新向控制面请求能力 → 获取新 Badge |

**可缓解性**：高。两阶段递增 + 重请求机制。

### 2.3 风险三：Badge 泄露

| 风险 | 量化 | 缓解 |
|------|------|------|
| 攻击者截获 Badge 后重放 | Badge 是 64-bit 明文，本身不加密 | Epoch 递增后旧 Badge 失效。攻击者必须在同一 Epoch 内截获并使用 Badge——如果攻击者已经能截获 IPC 消息，安全模型已经破裂 |
| Badge 被写入日志/转储 | Badge 可能出现在 core dump 或日志中 | Badge 无保密要求——仅证明权限，不证明身份。丢失 Badge 不会赋予攻击者额外权限（攻击者仍需访问 IPC channel） |

**可缓解性**：中。Badge 机制本身不提供机密性（设计如此），安全性仍依赖 IPC channel 的访问控制。

### 2.4 风险四：Epoch 全局 vs 按能力类型

| 风险 | 量化 | 缓解 |
|------|------|------|
| 全局 Epoch：撤销一个 Agent 的能力（如 revoke Agent A 的 cap_X）会使得所有 Agent 的 Badge 失效 | 12 daemon × N Agent 全部需要重新请求能力 | 按能力类型分 Epoch：每个能力类型（IPC_SEND、FILE_READ、MEM_QUERY 等）有独立的 Epoch。撤销 cap_X 仅使该类型的 Badge 失效 |
| 按类型的 Epoch 增加存储开销 | 10 种能力类型 × 4B Epoch = 40B 全局存储 | 可忽略 |

**可缓解性**：高。按能力类型分 Epoch 是标准实践。

### 2.5 风险五：连接建立期的 Badge 编译开销

| 风险 | 量化 | 缓解 |
|------|------|------|
| Agent 首次连接时，控制面需要编译 Badge | 查找 Agent 的所有能力 → 计算 permissions mask → 嵌入 Badge | 这是 O(n) 操作（n = Agent 的能力数），在连接建立期执行一次，运行时零开销 |

**可缓解性**：高。连接建立非高频操作。

### 2.6 风险总结

| # | 风险 | 严重度 | 可缓解性 |
|---|------|:---:|:---:|
| R1 | Epoch 溢出 | 低 | 高（32-bit > 136 年） |
| R2 | Epoch 递增后消息丢失 | 中 | 高（两阶段递增 + 重请求） |
| R3 | Badge 泄露 | 低 | 中（Epoch 递增后失效） |
| R4 | 全局 vs 按类型 Epoch | 中 | 高（按类型分 Epoch） |
| R5 | 连接建立期编译开销 | 低 | 高（一次性操作） |

**五个风险均在可缓解范围内。与传统 cache-based Capability 的 IPI coherency 风险（无法根本消除，仅能缩小窗口）相比，Native Word 方案的风险更容易管理。**

---

## 3. 问题三：是否更完善和稳健？

### 3.1 对比：融合前 vs Native Word 融合后（六维度）

| 维度 | 当前 A-IPC | + Native Word | 变化 |
|------|:---:|:---:|------|
| **吞吐** | ✅ | ✅ | 不变 |
| **延迟** | ✅ | ✅ + fastpath 从 ~160ns → ~5ns | **改善** |
| **隔离** | ❌（控制面同步阻塞死锁） | ✅（数据通信移出控制面） | **根本改善** |
| **一致性** | ❌（双轨能力校验） | ✅（Badge 唯一证明） | **根本改善** |
| **恢复** | ⚠️（daemon 崩溃冻结 5s） | ✅（数据面立即感知） | **改善** |
| **上限** | ❌（MSG_RING 争用） | ❌（与 Native Word 无关） | 不变 |

### 3.2 工程复杂度的变化

| 组件 | 融合前 | 融合后 | 复杂度变化 |
|------|-------|--------|:--:|
| **fastpath C-S9** | `airy_cap_check_fast()` 黑盒（~110ns） | 两条 CPU 指令（~5ns） | **↓ 显著降低** |
| **per-CPU capability cache** | radix tree + TTL + IPI 失效 | 不需要（Epoch 替代） | **↓ 完全消除** |
| **capability IPI coherency** | 复杂（IPI + 内存屏障） | 不需要 | **↓ 完全消除** |
| **Epoch 管理** | 不存在 | 每个能力类型一个 32-bit 计数器 + 两阶段递增 | **↑ 新增，但 ~50 行 C** |
| **Badge 编译** | 不存在 | 连接建立期编译，~30 行 C | **↑ 新增，少量** |
| **控制面 syscall 频率** | 10K-100K/s | 10-100/s | **↓ 1000× 降低** |
| **daemon 网格死锁风险** | 高 | 极低 | **↓ 根本改善** |

**净复杂度：显著降低。新增的两个组件（Epoch + Badge 编译）合计约 80 行 C，但消除了 per-CPU capability cache（~200-300 行 C）和控制面高频同步阻塞（~1000× 频率降低）。**

### 3.3 与 agentrt-linux 三大支柱的对齐

| 支柱 | 融合前 | 融合后 |
|------|--------|--------|
| **微内核设计思想**（机制在内核，策略在用户态） | 部分对齐——数据面机制在内核，能力策略仍在控制面 | **更彻底**——内核仅保留 Epoch 计数器（纯机制），sec_d 编译 Badge（纯策略） |
| **工程基线**（Linux 6.6 LTS） | `airy_cap_check_fast()` 未实现 + radix tree 运维复杂 | Epoch 管理 + Badge 编译全部使用 Linux 6.6 标准机制（atomic_t + cmpxchg） |
| **Airymax 同源性**（agentrt ↔ agentrt-linux [SC] 共享） | `ipc.h` 共享 128B 头 | `ipc.h` 共享 128B 头 + `capability_badge` 字段语义同源 |

---

## 4. 最终判定

### 4.1 是否需要全面重构？

**不需要。** Native Word 方案是 A-IPC 的局部增强——修改范围：Layout C 的 8 字节 + fastpath 的 1 个条件 + 新增 Epoch 管理（~80 行 C）+ 消除 per-CPU cache（~200 行 C）。8 层中的 4 层完全不变。

### 4.2 是否有风险？

**五个风险均在可缓解范围内。** 最严重的风险（Epoch 递增导致在途消息丢失）可通过两阶段递增机制缓解。与当前 cache-based 方案的 IPI coherency 风险（不可根本消除）相比，Native Word 方案的风险更可控。

### 4.3 是否更完善和稳健？

**是。** Native Word 方案在三个维度上显著提升：
1. **一致性**（21号审查维度四）从"不通过"变为"通过"——Badge 消除了双轨制能力校验
2. **隔离**（21号审查维度三）从"不通过"变为"通过"——数据通信离开控制面，死锁风险消失
3. **工程复杂度**净降低——Fastpath 从 ~160ns 黑盒变为 2 条 CPU 指令；per-CPU cache 及其 IPI coherency 完全消除

**如果将 A-IPC 比作一个操作系统的基础设施，Native Word 相当于用一条原子指令替代了一个复杂的缓存一致性协议——不是"增加功能"，而是"用更简单的机制实现相同或更强的语义"。**

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
