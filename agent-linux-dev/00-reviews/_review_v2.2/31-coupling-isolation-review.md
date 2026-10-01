Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 31 — 对 Capability Folding 架构耦合性的根本性审查

## "控制逻辑折叠进数据路径是否在工程上可接受"

> **文档性质**：对 Capability Folding 架构哲学的逆向思考
> **审查等级**：架构级 — 不发现漏洞，但审视工程基础
> **核心问题**：耦合（控制受数据影响）、安全风险（控制暴露于数据路径）、调试困难、缺乏隔离

---

## §0 问题陈述

Capability Folding 的定义本身包含了"将控制面折叠进数据面"。问题是：**这四件事——耦合、安全风险、调试困难、隔离缺失——是 Capability Folding 的固有缺陷，还是可以通过工程设计缓解的 trade-off？**

要回答这个问题，必须先清晰地定义"折叠前"和"折叠后"的架构差异。

---

## §1 架构对比：seL4 双平面 vs A-IPC Capability Folding

### 1.1 seL4 的控制面/数据面分离

```
seL4 的 IPC 路径（两个独立的服务调用）:

  ┌─────────────────────────────────────────────────────────────────┐
  │  控制面调用: seL4_Call(cap, msg_info)                           │
  │                                                                  │
  │  Step 1: lookupCapAndSlot(cap)       ← 在 CNode 中查找 cap       │
  │  Step 2: 验证 cap 类型 (Endpoint)                                │
  │  Step 3: 验证 cap 权限 (Write/Read/Grant)                       │
  │  Step 4: 检查 badge（多 Agent 共享 Endpoint 时）                 │
  │  Step 5: 查找 TCB 并设置接收方状态                               │
  │  ↓ 控制面结束 ↓                                                  │
  │                                                                  │
  │  数据面调用: doIPCTransfer(src_tcb, dst_tcb)                     │
  │                                                                  │
  │  Step 6: 复制 message registers → IPC buffer                    │
  │  Step 7: 设置接收方 TCB → Running                               │
  │  Step 8: 切换上下文（如果需要）                                   │
  │                                                                  │
  │  Step 1-5 和 Step 6-8 在不同的函数中                              │
  │  Step 1-5 是纯控制逻辑（零数据移动）                               │
  │  Step 6-8 是纯数据逻辑（零权限判断）                               │
  │  Step 1-5 的失败不影响 Step 6-8 的代码路径                        │
  └─────────────────────────────────────────────────────────────────┘

seL4 的隔离属性:
  攻击面 1: 如果数据传递 (Step 6-8) 有 bug → 可能丢失/损坏数据
           但不可能绕过能力校验 (Step 1-5 已经完成)
  攻击面 2: 如果能力校验 (Step 1-5) 有 bug → 可能接受未授权消息
           但不可能影响数据传递的正确性（Step 6-8 是独立的）
  
  两条攻击面完全独立。这是 Isabelle/HOL 证明可以分别验证两个子系统的结构基础。
```

### 1.2 A-IPC Capability Folding 的单路径

```
A-IPC 的 fastpath（12 个条件在一个线性序列中）:

  ┌─────────────────────────────────────────────────────────────────┐
  │  io_uring callback: airy_uring_cmd() → airy_ipc_send()          │
  │                                                                  │
  │  C-S0:  ring->frozen == false           ← 控制（A-ULS）          │
  │  C-S1:  magic == 0x41524531             ← 格式校验               │
  │  C-S2:  opcode 合法                      ← 格式校验               │
  │  C-S3:  payload_len 合法                 ← 格式校验               │
  │  C-S4:  sizeof(hdr) == 128              ← 格式校验               │
  │  C-S5:  CPU id 匹配                      ← 数据路径决策           │
  │  C-S6:  kfifo 不满                        ← 数据路径决策           │
  │  C-S7:  reclaim flag 未置               ← 上下文校验              │
  │  C-S8:  in_task()                        ← 上下文校验              │
  │  C-S9:  [Capability Folding] Badge 校验   ← 控制（能力校验）      │
  │  C-S10: flags 不含 ENCRYPT/COMPRESS       ← 格式校验               │
  │  C-S11: preempt_disable()               ← 原子性保护              │
  │                                                                  │
  │  kfifo_in()   ← 数据面：消息入队                                  │
  │  eventfd_signal() ← 数据面：唤醒接收方                            │
  │  io_uring_cqe_fill() ← 数据面：完成通知                           │
  │                                                                  │
  │  C-S9 在控制逻辑（C-S0/C-S9/C-S11）和数据逻辑                     │
  │  （C-S5/C-S6/kfifo_in/eventfd_signal）之间                        │
  │  没有函数调用边界。没有独立失败域。                                  │
  └─────────────────────────────────────────────────────────────────┘

A-IPC 的耦合属性:
  攻击面 1: 如果 C-S5（CPU 匹配）的代码在维护中被错误修改
           → 可能影响 C-S9 是否被执行
  攻击面 2: 如果 kfifo_in 有缓冲区溢出
           → 可能覆盖 fastpath 栈帧中的 C-S9 结果
  攻击面 3: 如果 C-S6（kfifo 满检查）有 TOCTOU 漏洞
           → 可能导致能力校验通过但数据未投递（不一致状态）
  
  这些攻击面在 seL4 的双平面设计中不存在，因为控制面和数据面
  在不同的函数中、不同的栈帧中、不同的失败域中。
```

---

## §2 四个风险的逐个分析

### 2.1 耦合（Coupling）：数据问题是否会影响控制决策

**风险的实质**：在单路径 fastpath 中，C-S9（能力校验）与 C-S5（CPU 匹配）、C-S6（kfifo 满检查）共享同一个执行上下文。如果这些数据路径检查被错误实现，可能影响 C-S9 的执行。

**当前设计的缓解措施**：

```
1. 线性 check-and-return 模式：
   每个 C-Sx 检查都遵循:
     if (condition_fails)
         return -Exxx;
   
   这种模式保证了：前面的检查失败不会影响后面的检查——它们根本不执行。
   它确实意味着：后面的检查（包括 C-S9）可能永远不会被执行。
   但这是正确的：如果一个消息格式不合法（C-S1 失败），为什么要检查它的能力？

2. C-S9 在 C-S6 之前：
   C-S6（kfifo 满检查）在 C-S9（能力校验）之后。
   如果 kfifo 满了：
   - 旧设计（双平面）：控制面通过 → 数据面拒绝 → 不一致
   - 新设计（Capability Folding）：C-S9 先通过 → C-S6 拒绝 → 两者在同一函数中返回 -AIRY_EIPC_KFIFO
   新旧设计在这个场景中语义相同。

3. C-S9 在 C-S5 之前：
   C-S5（CPU 匹配）在 C-S9 之前。如果 CPU 不匹配：
   - 消息走 SLOW_PATH（跨 CPU kfifo）
   - SLOW_PATH 仍然执行 C-S9（能力校验在 slowpath 中也存在）
   - 语义一致
```

**剩余的耦合风险**：

a) **kfifo 缓冲区溢出覆盖 fastpath 栈帧**

```
如果 kfifo_in 有缓冲区溢出漏洞:
  → 覆盖 fastpath 函数栈帧
  → 可能覆盖 C-S9 的中间变量（agent_epoch, agent_perms 等）
  → 这可能导致能力校验结果被污染

在 seL4 中，这个风险不存在，因为 doIPCTransfer 和 lookupCapAndSlot
在不同的栈帧中，一个栈溢出不会影响另一个。
```

**缓解**：这是一个"内核内存安全"问题，不是"Capability Folding 架构"问题。任何内核函数都存在栈溢出风险。seL4 通过形式化验证保证无栈溢出。A-IPC 需要通过静态分析（Coverity + GCC -fanalyzer + KASAN）和 CBMC 有界验证来保证。

b) **fastpath 代码修改可能意外跳过 C-S9**

```
如果开发者在 C-S1-C-S8 之间插入了一个 goto/early return 语句:
  → 可能绕过 C-S9

在 seL4 中，这个风险不存在，因为 lookupCapAndSlot 是独立函数调用，
不会因为 doIPCTransfer 的修改而被绕过。
```

**缓解**：
- C-S9 是 fastpath 中的一个显式步骤，代码审查明确要求 C-S9 不可跳过
- 静态分析规则：airy_uring_cmd() 必须包含 C-S9 检查
- CI 测试：发送没有 Badge 的消息，验证 REJECT

### 2.2 安全风险（Security）：控制逻辑暴露于数据路径

**风险的实质**：在 seL4 中，`lookupCapAndSlot` 是一个独立的特权操作。它不处理任何用户数据，只处理内核对象。在 A-IPC 中，`airy_cap_badge_ok` 嵌入在消息处理路径中，与用户提供的数据（消息头字段）交互。

**当前设计的缓解措施**：

```
1. C-S9 只读取三个数据源:
   a) agent_caps[src_task] — 内核静态数组，用户态不可写
   b) badge — 来自消息头的 offset 44-51，用户态可写
   c) airy_cap_epoch_get() — atomic_t，用户态不可写
   
   badge 是唯一受用户态控制的输入。
   C-S9 从 badge 中提取 epoch 和 random_tag，与内核侧的值比较。
   
   即使 badge 被恶意构造:
   - epoch 不匹配 → REJECT
   - random_tag 不匹配 → REJECT
   - 用户态无法控制 agent_caps[src_task].permissions ← 在内核内存中

2. C-S9 不调用任何其他函数:
   - 无 kmalloc
   - 无 lock
   - 无 RCU dereference
   - 无 kfifo 操作
   - 纯 READ_ONCE + 位运算 + 比较
   
   这意味着 C-S9 的"暴露面"仅限于 badge 字段的值，
   而这个值已在 30 号审查中通过随机标签机制保护。
```

**剩余的安全风险**：

a) **时序侧信道**

```
C-S9 的执行时间取决于比较结果:
  - epoch 不匹配: 3 次 READ_ONCE + 2 次比较 (~7ns)，提前返回
  - random_tag 不匹配: 3 次 READ_ONCE + 4 次比较 (~8ns)，提前返回
  - 全部通过: 3 次 READ_ONCE + 5 次比较 (~10ns)
  
差异 (~3ns) 可能泄露信息：攻击者通过测量 CQE 延迟可以推断
Badge 校验的哪一步失败了。这在理论上可用于侧信道攻击。

在 seL4 中，Capability lookup 的延迟差异也存在（CNode 深度不同）。
这是一个普遍的侧信道风险，不是 Capability Folding 特有的。
```

b) **agent_caps 数组的缓存侧信道**

```
agent_caps[src_task] 的访问延迟取决于 L1 cache 状态:
  - 热缓存 (src_task 最近通信过): ~3ns
  - 冷缓存 (src_task 长时间未通信): ~15ns (L2 hit)
  - 未缓存 (src_task 从未通信): ~50ns (L3 hit or DRAM)
  
延迟差异可能泄露"src_task 是否最近通信过"。
但 agent_caps 是对齐数组，1024 entries × 8 bytes = 8KB，
在 L1 缓存中 (32KB)，所以绝大多数情况下都是热缓存。
```

### 2.3 调试困难（Debugging）：无法独立测试能力层

**风险的实质**：在双平面设计中，你可以调用 `airy_sys_call(cap)` 只测试能力校验而不发送数据。在 Capability Folding 中，能力校验是数据发送的一部分，你无法独立测试。

**当前设计的缓解措施**：

```
1. A-UEF 错误码分区（能力错误 vs 数据错误）:

   能力错误（C-S9 区域）:
     AIRY_ECAP_EPOCH  (-41)  Epoch 不匹配
     AIRY_ECAP_PERM   (-42)  权限不足
     AIRY_ECAP_BADGE  (-43)  Badge 格式无效
     AIRY_ECAP_FROZEN  (-44)  Ring 冻结
   
   数据错误（非 C-S9 区域）:
     AIRY_EIPC_MAGIC  (-45)  magic 错误
     AIRY_EIPC_CRC32  (-46)  CRC32 错误
     AIRY_EIPC_OPCOD  (-47)  opcode 错误
     ...

   通过 io_uring CQE res 字段的值可以立即区分能力错误和数据错误。

2. ftrace 探针:
   trace_airy_cap_verify(badge, src_task, result)
   trace_airy_kfifo_enqueue(src_task, dst_task, len)
   
   这两个探针分别记录能力校验和数据投递。
   ftrace filter 可以只看能力相关的事件。

3. sysfs 统计计数器:
   /sys/kernel/airy/ipc/stats
     cap_epoch_rejects   = 1234   ← 能力错误总数
     cap_perms_rejects   = 567
     cap_badge_rejects   = 89
     data_kfifo_full     = 12     ← 数据错误总数
     data_crc32_fail     = 0
     data_magic_fail     = 0
```

**剩余的调试风险**：

```
无法做到的事：向内核发送"仅做能力校验，不投递数据"的请求。
seL4 可以做到（调用 seL4_Call 然后不发送数据）。

但 agent-linux 的场景不需要这个能力：
  - 能力只有在数据需要投递时才有意义
  - 如果一条消息的 Badge 无效，它会被拒绝（inline deny），
    接收方不会被唤醒——这与"不投递数据"等价
  - 发送方通过 CQE res 字段立即知道能力校验的结果
  - 没有需要"检查能力但不发送数据"的用例
```

### 2.4 缺乏隔离（Isolation）：控制与数据没有隔离边界

**风险的实质**：这是四个风险中最根本的一个。在 seL4 中，能力管理和 IPC 是两个不同的内核服务，有独立的代码路径、独立的数据结构、独立的失败模式。Capability Folding 将它们合并了。

**当前设计中存在的隔离**：

```
1. 数据结构隔离:
   agent_caps[1024]  ← 能力数据（静态数组，8KB）
   kfifo              ← 数据投递缓冲区
   io_uring ring      ← 通信原语
   
   三者是独立的内存区域。agent_caps 不会被 kfifo 操作修改。
   kfifo 不会被 capability 校验修改。

2. 更新路径隔离:
   agent_caps 的更新者: 仅 sec_d（通过 airy_sys_call(COMPILE_BADGE)）
   agent_caps 的读取者: fastpath C-S9（IOURING_OP_URING_CMD callback）
   kfifo 的写入者: fastpath kfifo_in
   kfifo 的读取者: 接收方 io_uring CQE 处理
   
   更新者只有一个（sec_d），读取者只有 fastpath。
   这是单写者 / 多读者模型，不需要锁，不需要 RCU。
   通过 READ_ONCE/WRITE_ONCE 配对保证可见性。

3. 失败域隔离:
   C-S9 失败 → 返回能力错误码 → 消息不投递
   kfifo_in 失败 → 返回数据错误码 → 能力校验已完成（无意义，因为消息未投递）
   
   但 C-S9 通过 + kfifo_in 失败的组合是明确定义的：
   消息通过了能力校验但没有被投递。
   这对安全无影响（未投递的消息不能造成伤害）。
   这对功能有影响（发送方认为成功但消息未达），但发送方通过 CQE res 知道失败。
```

**隔离的真正缺口**：

```
seL4 提供的隔离是 ARCHITECTURAL:
  - lookupCapAndSlot 是独立的内核对象操作
  - doIPCTransfer 是独立的消息传递操作
  - 它们可以分别被验证、分别被审计、分别被替换
  - Isabelle/HOL 的证明策略是分而治之

A-IPC 提供的隔离是 DATA-STRUCTURAL:
  - agent_caps[] 和 kfifo 是独立的内存区域
  - 能力和数据的代码在同一个 fastpath 函数中
  - 它们不能被分别验证——必须验证整个 fastpath
  - CBMC 的验证策略是全函数有界验证

关键区别:
  seL4: "我证明了 lookupCapAndSlot 是正确的" +
        "我证明了 doIPCTransfer 是正确的" +
        "它们之间没有交互" = 系统正确
  
  A-IPC: "我证明了 airy_ipc_send_fastpath 是正确的" = 系统正确
  
  seL4 的证明可以在 lookupCapAndSlot 被替换时
  不需要重新证明 doIPCTransfer。
  
  A-IPC 的证明在整个 fastpath 被任何一行修改时都需要重新验证。
```

---

## §3 这个 trade-off 对 agent-linux 是否可接受

### 3.1 agent-linux 与 seL4 的根本差异

| 维度 | seL4 | agent-linux |
|------|------|---------------|
| 目标场景 | 军事/航空/医疗（硬安全） | AI Agent 运行时（性能优先） |
| 认证等级 | EAL7 / SIL4 | 无认证要求 |
| 安全模型 | 形式化验证（Isabelle/HOL） | 工程安全（代码审查 + 静态分析 + 渗透测试） |
| 攻击者模型 | Nation-state adversary | 多租户隔离（良性 Agent + 恶意 Agent） |
| 性能约束 | 硬实时（实时 deadline） | 软性能（吞吐 + 延迟 SLO） |
| 代码规模 | ~10 kSLOC | ~5,000 行（IPC 子系统） |
| 维护模型 | 10 年 LTS | 持续迭代 |
| 隔离哲学 | 架构级（证明的）隔离 | 数据结构级（工程的）隔离 |

### 3.2 针对四个风险的最终判断

**耦合**：可接受。fastpath 是 100 行线性代码，维护风险可控。静态分析 + CI 测试保证 C-S9 不可被意外绕过。

**安全**：可接受。C-S9 只读取 agent_caps[]（内核内存）和 badge（用户可控但通过随机标签保护）。30 号审查修复后，Badge 不可伪造。

**调试**：可接受。A-UEF 错误码分区 + ftrace 探针 + sysfs 统计计数器提供了足够的能力/数据分离诊断手段。缺少"独立能力测试"不是 agent-linux 需要的特性。

**隔离**：**这是最大的 trade-off。** A-IPC 用"数据结构隔离"替代了 seL4 的"架构隔离"。对于 agent-linux 的非认证场景，数据结构隔离是可接受的，但必须清楚地记录：
- fastpath 的 CBMC 验证必须覆盖整个函数（100 行），而不是分别验证能力层和数据层
- 任何对 fastpath 的代码修改都需要重新运行完整的 CBMC 验证
- 静态分析规则必须保证 agent_caps[] 和 kfifo 是独立的内存区域

### 3.3 如果未来需要更强的隔离

如果 agent-linux 未来需要更强的隔离（例如，支持不可信硬实时负载），可以在不推翻 Capability Folding 的前提下增加隔离：

```
方案: 在 fastpath 内部增加显式的"能力门"（Capability Gate）

  C-S0: frozen check
  C-S1-C-S4: format checks
  ─── 能力门 ───
  C-S9: capability_badge_verify()  ← 独立的函数调用
  if (failed) return -Exxx;
  ─── 数据门 ───
  C-S5-C-S8: context checks
  C-S10: flag check
  preempt_disable
  kfifo_in + eventfd_signal + cqe_fill
  
  "能力门"之后的所有代码保证不与能力数据（agent_caps[]）交互。
  "数据门"之前的所有代码保证不与数据缓冲区（kfifo）交互。
  
  这是一个代码组织约定，在 0.1.1 中不需要，
  但可以在 1.0.1 中作为架构加强引入。
```

---

## §4 结论

**Capability Folding 确实牺牲了 seL4 的架构级隔离。这是一个真实的 trade-off，不是一个可以忽略的细节。**

但这个 trade-off 对 agent-linux 是可接受的，因为：
1. agent-linux 不是安全认证系统，不需要架构级隔离
2. 数据结构隔离（agent_caps[] 与 kfifo 独立）足以满足多租户隔离需求
3. fastpath 的 100 行代码规模使得全函数验证（CBMC）可行
4. Capability Folding 带来的性能改善（10ns vs 50-100ns）和复杂度的降低（消除 radix tree + per-CPU cache + IPI coherency）在实际工程中价值更大

**这不是"设计没有注意到这个问题"——这是"经过分析后，我们认为这个 trade-off 对 agent-linux 是正确的"。** 如果未来场景变化（例如 agent-linux 被用于安全认证系统），§3.3 中的"能力门"方案可以在不推翻 Capability Folding 的前提下增加隔离。

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. | Capability Folding 架构耦合性审查 | v1.0 | 2026-07-18
