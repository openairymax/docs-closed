# HotOS 2027 短论文大纲

> **论文标题**：Capability-Data Convergence: Collapsing Access Control into the IPC Data Plane for AI Agent Operating Systems  
> **投稿目标**：HotOS 2027 (Workshop on Hot Topics in Operating Systems)，6 页  
> **创新点**：(1) 双层消息嵌套模型（Double-Layer Message Nesting）(2) Capability Invocation 折叠（Capability Folding）  
> **状态**：大纲 v1.0，待实验数据填充  
> **日期**：2026-07-11  
> **SPDX**: AGPL-3.0-or-later OR Apache-2.0

---

## 0. 论文信息卡

| 属性 | 值 |
|------|-----|
| 论文类型 | Position Paper / Experience Report |
| 页数 | 6 页（不含参考文献） |
| 预计字数 | ~4,500 words |
| 图表数量 | 3-4 张 |
| 基准测试 | ~2 周（微基准 + 对比 seL4 / io_uring raw） |
| 写作时间 | ~1 周 |
| 系统 | Airymax AgentRT (agentrt) + AirymaxOS (agent-linux) |
| 代码基础 | agentrt 177K LOC C, agent-linux 设计文档 (~110+ 文档) |

---

## 1. 论文结构（6 页分配）

```
§1. Introduction                    0.75 页
§2. Background & Motivation         0.75 页
§3. Design                          1.5 页
§4. Implementation Notes            0.75 页
§5. Evaluation                      1.0 页
§6. Discussion & Related Work       0.75 页
§7. Conclusion                      0.25 页
References                          0.25 页
────────────────────────────────────────
TOTAL                               6.0 页
```

---

## 2. 各章节详细大纲

### §1. Introduction（0.75 页）

**核心论述推进**：

```
Paragraph 1: AI Agent 操作系统面临的 IPC 挑战

  传统 IPC 的设计假设：
  ─ 通信模式是请求-响应（RPC 模型）
  ─ 安全是"先校验、后通信"的三步分离（authenticate → authorize → execute）
  ─ 用户态/内核态之间有明确的序列化/反序列化边界

  AI Agent 操作系统的不同假设：
  ─ 通信是持续的多跳流水线（cognition → planning → execution → memory）
  ─ Agent 间的 capability 传递需要和消息在同一路径上，否则延迟不达标
  ─ 用户态 Agent 运行时和内核态 Agent OS 共享同一套 IPC 契约

Paragraph 2: 现有方案的三个困境

  (1) seL4 IPC：单层 capability 传递，无协议层 → Agent 之间的语义通信依赖上层重建
  (2) Linux io_uring：高吞吐零拷贝，但无 access control 语义 → 每次操作前需要独立的 capability check
  (3) gRPC / JSON-RPC：协议层丰富，但与内核态 capability 完全无关 → 跨用户/内核边界需要翻译层

  这三个方案各自解决了一部分，但没有一个方案把 capability control 和 data path 折叠到
  同一条 IPC 消息路径上。

Paragraph 3: 本文的贡献

  我们提出 Airymax IPC——一个面向 AI Agent 操作系统的双层 IPC 消息模型：
  
  (1) Double-Layer Message Nesting（双层消息嵌套）：L1 机制层 (40B) 包裹 L2 协议层 (128B + payload)，
      接收方按 magic 字节自解释、自路由；零拷贝仅发生在 L1，L2 由上层解析。

  (2) Capability Invocation Folding（Capability 折叠）：将 capability check 从"独立的前置操作"折叠到
      IPC 消息头本身的字段验证中——每条消息头携带 source、target、cap_badge，路由时即完成 capability
      校验。不需要额外的 RPC 来回。

  我们展示了 Airymax IPC 在 agentrt（用户态）和 agent-linux（内核态）的协同实现，并通过微基准
  对比 seL4 raw IPC 和 io_uring bare-metal 吞吐，证明这个设计在性能上不劣于现有方案，在安全性上
  优于纯数据面的方案。
```

---

### §2. Background & Motivation（0.75 页）

**核心论述推进**：

```
Paragraph 1: Airymax 的双端架构

  ┌─────────────────┐          ┌──────────────────────┐
  │ agentrt (用户态)  │          │ agent-linux (内核态) │
  │ 12 daemons       │          │ Linux 6.6 + capability │
  │ CoreLoopThree    │          │ sched_ext + eBPF       │
  │ Cupolas (安全穹顶) │          │ io_uring + seL4 LSM    │
  └────────┬────────┘          └───────────┬──────────┘
           │                               │
           └─── IRON-9 v2 [SC] 共享契约 ────┘
                 6 头文件逐字节相同

  关键约束：
  ─ agentrt 是跨平台用户态 C 程序，使用 POSIX + shared memory + semaphore 实现 IPC
  ─ agent-linux 是 Linux 内核模块，使用 io_uring + seL4 风格 capability
  ─ 两端必须共享同一 IPC 消息布局——否则翻译层会吃掉性能，也引入不一致性风险

Paragraph 2: 为什么传统 IPC 设计不适合 Agent 场景

  三种典型 IPC 范式在 Agent 场景中的局限（配一张小对比表）：

  ┌──────────────┬──────────────┬──────────────┬──────────────┐
  │              │ seL4 IPC     │ io_uring     │ Airymax IPC  │
  ├──────────────┼──────────────┼──────────────┼──────────────┤
  │ Capability   │ 原生（CTE）   │ 无（需 LSM）  │ 折叠进消息头   │
  │ 零拷贝        │ 单次 memcpy  │ 完全零拷贝     │ 单次 memcpy  │
  │ 协议可插拔     │ 无（裸字节）  │ 无（裸字节）   │ JSON-RPC/MCP/A2A │
  │ 跨用户/内核    │ 需要翻译层    │ 需要 syscall  │ [SC] 头文件共享 │
  │ 跨平台        │ ARM/x86/RISC │ 仅 Linux     │ Linux/macOS/Win │
  └──────────────┴──────────────┴──────────────┴──────────────┘

Paragraph 3: 两个必须同时解决的设计张力

  张力 1：安全性要求"每次操作前验证"，性能要求"路径上不要额外来回"
    → 解决：控制路径（capability）和数据路径（消息）折叠到一次传递

  张力 2：用户态和内核态需要共享语义，但不能共享运行时
    → 解决：L1/L2 分层——L2 128B 消息头通过 [SC] 逐字节共享，L1 binder 各自平台实现
```

---

### §3. Design（1.5 页）⭐ 核心章节

#### §3.1 Double-Layer Message Nesting（0.6 页）

```
核心图（全页宽的 ASCII 或 SVG）：

  ┌─────────────────────────────────────────────────────────────┐
  │                    L2 PROTOCOL LAYER (128B + payload)       │
  │  ┌──────────────────────────────────────────────────────┐   │
  │  │ magic | opcode | flags | trace_id | timestamp_ns     │   │
  │  │ src_task | dst_task | payload_len | reserved[84]     │   │
  │  │ CRC32 | source[16] | target[16] | cap_badge         │   │
  │  │ version | msg_type | protocol | msg_id              │   │
  │  │ correlation_id | _abi_pad                           │   │
  │  ├──────────────────────────────────────────────────────┤   │
  │  │ payload[] (JSON-RPC / MCP / A2A / raw bytes)        │   │
  │  └──────────────────────────────────────────────────────┘   │
  │                           ↑ nested into                      │
  └─────────────────────────────────────────────────────────────┘
                              │
  ┌─────────────────────────────────────────────────────────────┐
  │                    L1 MECHANISM LAYER (40B)                 │
  │  ┌──────────────────────────────────────────────────────┐   │
  │  │ code | data (→ L2 msg ptr) | size | fd | msg_id      │   │
  │  └──────────────────────────────────────────────────────┘   │
  │  零拷贝：L2 消息作为 data 指针传递，仅一次 __builtin_memcpy  │
  │  自路由：接收方通过 magic 0x41524531 ('ARE1') 识别 L2 消息  │
  └─────────────────────────────────────────────────────────────┘
```

**设计要点**：

1. **Magic 自识别**：`0x41524531` ('ARE1') 作为 L2 消息的开头 4 字节。接收方在 L1 binder
   拿到指针后，通过检查前 4 字节即可判断这是一个 AgentsIPC 消息还是裸字节流。不需要元数据
   通道来声明协议类型。

2. **零拷贝仅在 L1**：L1 binder 唯一的拷贝是 `__builtin_memcpy` 将 L2 消息从发送方通道
   复制到接收方通道（单次 128B+N 字节的块拷贝）。L2 的协议解析（JSON-RPC method dispatch、
   MCP tool call、A2A negotiation）全部直接在这个拷贝后的共享内存段上进行，没有二次拷贝。

3. **协议可插拔**：L2 消息头的 `protocol` 字段支持 JSON-RPC、MCP、A2A、OpenAI 兼容等 9+ 种
   协议。L1 binder 完全不关心 L2 协议是什么——它只需要 magic 来区分消息类型，以及
   `payload_len` 来分配/传递正确的缓冲区大小。

4. **编译时布局保证**：16 个 `_Static_assert` 强制校验 L2 128B 消息头的每个字段偏移量，
   任何对结构体的修改如果破坏了字节布局，编译直接失败。
```

#### §3.2 Capability Invocation Folding（0.6 页）

```
核心图：

  传统 IPC（控制面独立）：
    
    Sender ──cap_request──▶ Capability Checker (seL4 / LSM)
      ↓                        │
      ↓ (等待 capability 判决)   │
      │◄──cap_reply─────────────┘
      │
      └──payload_send──▶ Kernel ──payload_deliver──▶ Receiver

    最少 3 个往返：cap 请求→cap 回复→payload 发送
    安全关键路径延迟：~6μs (seL4 raw IPC × 3) + capability lookup

  
  Airymax IPC（控制面折叠进数据面）：
    
    Sender ──single message──▶ Kernel capability check ──▶ Receiver
     │         │                     │ (inline, 0 额外往返)    │
     │         ├─ src_task           ├─ lookup cap(src→dst)    │
     │         ├─ dst_task           ├─ verify badge           │
     │         ├─ cap_badge          └─ pass/fail inline       │
     │         └─ payload

    仅 1 个往返。capability 验证与消息传递同步完成。
    安全关键路径延迟：~2μs (单次 memcpy + inline cap lookup)
```

**设计要点**：

1. **Capability badge 嵌入消息头**：`cap_badge` 字段是发送方持有的 capability token 的
   加密哈希，接收方内核通过查表 (CNode) 验证发送方是否有权向接收方发送此类消息。

2. **inline 拒绝**：如果 capability 校验失败，接收方内核在 IPC fastpath 上直接返回
   `AIRY_EPERM`，不唤醒接收方 daemon。这避免了"接收方被唤醒后发现无权处理"的浪费。

3. **与 seL4 capability invocation 的语义同形**：`mint / derive / revoke` 三种操作
   映射到 L2 消息头的 flags 位，不需要额外的 CTE lookup 往返。

4. **跨端一致**：agentrt（用户态）的 Cupolas permission engine 和 agent-linux（内核态）
   的 agent_lsm 使用同一份 `security_types.h` [SC] 共享契约层——capability 枚举和
   策略裁决结果的 4 值枚举（ALLOW / DENY / ASK / DEFER）在两端的含义完全一致。
```

#### §3.3 设计空间权衡（0.3 页）

```
  为什么不直接采用方案 A（L4 IPC + gRPC 适配层）？
  → 适配层引入序列化开销 + 语义丢失（L4 不理解 gRPC 的 streaming 语义）

  为什么不直接采用方案 B（纯 io_uring + eBPF capability check）？
  → io_uring SQE/CQE 队列是裸字节，无法承载 Agent 语义（trace_id, correlation_id）
  → eBPF capability check 在 IO 提交时是一个独立的 kernel 路径，仍需额外的上下文切换

  为什么选择双层嵌套？
  → (1) 协议无关：L1 binder 是通用机制，L2 是策略——换协议不影响零拷贝路径
  → (2) 渐进复杂度：简单场景（daemon 内部通信）只需 L1，复杂场景（A2A）加 L2
  → (3) 形式化可验证：L1 40B 头 + 单次 memcpy——CBMC 可以直接进行有界验证
```

---

### §4. Implementation Notes（0.75 页）

```
Paragraph 1: agentrt 用户态实现（~500 LOC）

  核心文件：
  - atoms/corekern/src/ipc/binder.c（~500 行）：L1 机制层，通道管理 + 单次 memcpy
  - atoms/corekern/src/ipc/are_ipc.c（~800 行）：L2 协议层，128B 消息创建/解析/校验
  - atoms/corekern/include/are_ipc.h（16 个 _Static_assert）：编译时布局保证

  关键实现细节：
  - 通道创建：shm_open + mmap (Linux) / CreateFileMapping (Windows)
  - OOM 保护：32 个预分配 msg 节点的应急池（SEC-13 合规）
  - CRC32：编译时 256 条目查表，IEEE 802.3 多项式

Paragraph 2: agent-linux 内核态设计（设计文档，代码在 M1 阶段实现）

  核心映射：
  - L1 binder → io_uring SQE/CQE 队列（内核态零拷贝数据面）
  - L2 消息头 → [SC] ipc.h 共享契约（逐字节与 agentrt 一致）
  - capability check → agent_lsm LSM hook（LSM_ORDER_FIRST）
  - protocol dispatch → service_d 用户态 daemon（策略层）

Paragraph 3: 共享契约层的落地

  IRON-9 v2 定义的 [SC] 层 6 个共享头文件：
  ─ ipc.h（IPC 128B 消息头，本文核心）
  ─ sched.h（SCHED_EXT + 任务描述符 magic）
  ─ security_types.h（POSIX capability + LSM hooks + Cupolas blob）
  ─ memory_types.h（MemoryRovol L1-L4 + GFP masks）
  ─ cognition_types.h（CoreLoopThree + Thinkdual + LLM 推理）
  ─ syscalls.h（12 核心 + 12 预留 syscall 编号）

  物理宿主：agent-linux/kernel/include/airymax/
  引用方式：agentrt 通过 -I 编译选项引用同一物理文件
  保证逐字节相同的机制：CI 校验两侧 grep magic 值是否一致
```

---

### §5. Evaluation（1.0 页）

```
目标：证明 Airymax IPC 在安全性和性能上的折中是合理的——不比最快的方案慢太多，但比纯数据面方案安全得多。

§5.1 微基准：IPC 吞吐与延迟（待实验数据填充）

  比较对象：
  ─ Airymax IPC (L1 binder，单次 memcpy)
  ─ seL4 raw IPC (seL4_MessageInfo + Call/ReplyRecv)
  ─ io_uring bare-metal (cqe peek + submit，无 capability 语义)
  ─ Unix Domain Socket (AF_UNIX SOCK_DGRAM)

  指标：
  ─ 单次消息往返延迟 (P50/P99, μs)
  ─ 吞吐 (msg/sec @ 1 producer, 1 consumer)
  ─ CPU 开销 (per-message CPU cycles)

  预期结果（基于设计分析）：
  ─ Airymax IPC 延迟接近 io_uring (~2-3μs)，是 seL4 IPC 的 ~1.5-2x
  ─ 但 Airymax IPC 自带 capability check，seL4 需要额外往返
  ─ 等价安全级别下，Airymax IPC 有效延迟优于 seL4 (2μs vs. ~6μs for seL4 3 往返)

  配图 1：单次消息延迟对比（柱状图，P50/P99）

§5.2 Capability 校验开销（待实验数据填充）

  测量 Airymax inline capability check 的开销 vs. 独立 LSM hook 的开销：
  ─ Airymax IPC (capability badge + inline CNode lookup)
  ─ Linux LSM (security_* hook 函数调用)
  
  预期结果：
  ─ inline CNode lookup ~50ns (一次哈希表查找)
  ─ LSM hook 调用 ~200ns (函数指针间接调用 + 参数推栈)

  配图 2：capability 校验路径的 CPU 时间分解 (flamegraph 缩略图)

§5.3 协议可插拔性验证

  演示同一个 L1 binder 上三种协议的共存：
  ─ JSON-RPC 2.0 (daemon-to-daemon, 4KB payload)
  ─ MCP v1.0 (tool call, 64KB payload)
  ─ A2A v0.3 (agent negotiation, 2KB payload)

  指标：协议检测延迟（magic + protocol 字段解析，< 10ns）

§5.4 安全性案例：capability badge 不可伪造

  展示：
  ─ 恶意 Agent 尝试伪造 capability badge → inline check 返回 AIRY_EPERM
  ─ 审计日志完整记录拒绝事件（SHA-256 哈希链）
  ─ 接收方 daemon 未被唤醒（节约 CPU）

  配图 3：攻击尝试 vs. 防御结果的时间线
```

---

### §6. Discussion & Related Work（0.75 页）

```
§6.1 已知局限

  ─ 单机限制：当前 Airymax IPC 是同一主机的多进程 IPC，不支持跨节点（集群场景需 A2A 协议）
  ─ L2 消息头可扩展性：128B 中 reserved[84] 足够当前协议扩展，但未来可能需要更大的头部
  ─ 形式化验证范围：当前仅对 L2 消息头布局有 16 个 _Static_assert（编译时），完整的形式化
    验证（CBMC 零拷贝路径 + 哈希链审计）是后续工作

§6.2 与其他 Agent 系统的对比

  ┌──────────┬───────────────┬──────────────┬───────────────┐
  │ 系统     │ IPC 模型       │ Capability   │ 消息层        │
  ├──────────┼───────────────┼──────────────┼───────────────┤
  │ LangGraph│ Python asyncio │ 无           │ Python dict   │
  │ CrewAI   │ Python call   │ 无           │ Python object │
  │ AutoGen  │ gRPC           │ 无           │ Protobuf      │
  │ MemGPT   │ REST API       │ API key      │ JSON          │
  │ Airymax  │ L1/L2 nested   │ Capability折叠│ Magic自识别   │
  └──────────┴───────────────┴──────────────┴───────────────┘

  这些 Agent 框架在 1-10 个 Agent 的规模下工作良好，但在 100+ Agent 时：
  ─ 没有 capability 模型 → Agent 间攻击面随数量平方增长
  ─ 没有零拷贝 IPC → Token 消耗变成瓶颈
  ─ 没有跨用户/内核共享 → 无法利用内核态安全加速

§6.3 与 OS 社区的关系

  Airymax IPC 受到三个操作系统社区的启发：
  ─ seL4：capability 作为唯一安全模型（但 Airymax 是混合模型：capability + 策略守护进程）
  ─ Linux io_uring：零拷贝数据面（但 Airymax 加入了协议层和语义标签）
  ─ SDN 数据面/控制面分离（但 Airymax 证明了可以"折叠"而非"分离"来获得更好的性能）
```

---

### §7. Conclusion（0.25 页）

```
  本文提出 Airymax IPC——一个将 AI Agent 通信的 capability control 路径折叠到
  IPC 数据面的操作系统级设计。关键创新是双层消息嵌套（L1 40B 机制 + L2 128B + payload
  协议层）和 capability invocation 折叠（inline badge 验证 + 单次往返）。

  初步微基准表明，这个设计的 IPC 延迟接近裸 io_uring（~2μs），同时提供 seL4 级别的
  capability 安全保证——这在同等安全级别下是显著的性能改进（3 个 seL4 往返 ~6μs vs.
  Airymax 单次 ~2μs）。

  我们正在将 Airymax IPC 实现为 agentrt（用户态，C）和 agent-linux（内核态，Linux 6.6）
  的一部分，并通过 IRON-9 v2 [SC] 共享契约层保证跨端消息一致性。这项工作的更广泛意义是：
  AI Agent 操作系统需要的不仅是更快的 IPC——而是更安全的 IPC 语义。
```

---

## 3. 待补充的实验数据清单

| 实验 | 指标 | 对比对象 | 预计工时 |
|------|------|---------|---------|
| IPC 吞吐基准 | msg/sec @ 8/32/1024B payload | Airymax vs. seL4 vs. io_uring vs. UDS | 8h |
| IPC 延迟分布 | P50/P99/P999 μs | 同上 | 4h |
| Capability 校验开销 | CPU cycles | inline vs. LSM hook | 4h |
| 伪造 badge 防御 | 拒绝率、审计日志完整性 | Airymax only | 2h |
| 协议切换开销 | 检测延迟 ns | JSON-RPC/MCP/A2A | 2h |
| **合计** | | | **~20h** |

---

## 4. 建议的标题备选

| # | 标题 | 风格 |
|---|------|------|
| A | **Capability-Data Convergence: Collapsing Access Control into the IPC Data Plane for AI Agent Operating Systems** | 学术正式 |
| B | **Why Your AI Agent OS Needs an IPC That Folds Capability Into the Fast Path** | HotOS 风格 |
| C | **Double-Layer IPC: A Capability-First Message Model for Cross-Domain Agent Communication** | 平衡风格 |
| D | **Unified Control and Data: Rethinking IPC for the Agent Operating System** | 简短有力 |

**推荐 A**（目标 HotOS 审稿人：OS + 安全背景）

---

## 5. 作者信息（草案）

| 作者 | 机构 | 贡献 |
|------|------|------|
| [待定] | SPHARX Ltd. | IPC 系统架构设计 + 实现 |
| [待定] | SPHARX Ltd. | agent-linux 内核态 capability 模型设计 |
| [待定] | SPHARX Ltd. | 实验设计 + 基准测试 |

注：HotOS 通常接受 3-6 名作者。

---

## 6. 时间线

| 阶段 | 内容 | 日期 |
|------|------|------|
| 大纲完成 | 本文档 | 2026-07-11 |
| 微基准实验 | §5 所有数据采集 | +2 周 |
| 初稿撰写 | 完整 6 页初稿 | +1 周 |
| 内部评审 | SPHARX Ltd. 内部 | +1 周 |
| 投稿 | HotOS 2027 | 预计 2027-01 (deadline ~2026-10) |

---

## 7. 附录：与 Airymax 全系统论文的关系

本短论文是全系统论文（目标 arXiv / EuroSys）的切片——聚焦 IPC 双向消息嵌套 +
capability folding 这一子系统设计决策。全系统论文将覆盖 CoreLoopThree（认知循环）、
MemoryRovol（记忆卷载）、Cupolas（安全穹顶）和 12 daemon 架构。

---

> **文档结束** | HotOS 2027 短论文大纲 v1.0 | 2026-07-11 | SPHARX Ltd.
