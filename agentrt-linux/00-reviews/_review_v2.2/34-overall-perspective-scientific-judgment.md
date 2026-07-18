Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 34 — 从 agentrt-linux 整体方案高度对 A-IPC 重构的科学论证

## "A-IPC 是 AirymaxOS 的第一块基石——基石的形状决定整座建筑"

> **文档性质**：跳出 A-IPC 单点视角，从 agentrt-linux 整体工程方案高度的科学严谨论证
> **撰写日期**：2026-07-18
> **审查依据**：逐份阅读 AirymaxOS 22 个子目录核心文档 + _review_v2.2 全部 34 份审查报告
> **核心问题**：对于 agentrt-linux 是否要采用 Capability Folding 重构方案，从整体方案高度进行科学、严谨的推论
> **设计哲学**：乔布斯/艾夫"简约就是美"——"对复杂事物的精髓进行深度挖掘和精准提炼"

---

## §0 论证框架

### 0.1 为什么需要这份论证

用户在 14 轮对话后提出一个根本性质疑：

> "目前的近十多轮对话，都是只看 A-IPC 方案本身，没有在 agentrt-linux 的整体方案上去深度总结和思考，这样的技术方案是孤立的。"

这一质疑是正确的。前 33 份审查报告虽然深度逐增，但视角始终聚焦于 A-IPC 内部——从漏洞到修复，从耦合到隔离，从物理鸿沟到简约化。**没有一份报告从 agentrt-linux 整体工程的高度，论证 Capability Folding 重构是否是正确的选择。**

本论证补足这个缺口。论证框架如下：

```
维度 1: 整体定位论证
  └── A-IPC 作为"第一块基石"在 AirymaxOS 中的位置与责任

维度 2: 契约一致性论证
  └── Capability Folding 与 IRON-9 v3 四层模型 + Airymax Unify Design §10 SSoT 的冲突分析

维度 3: 工程现实论证
  └── 0 行代码现状 + 184 份文档 + 5 模块依赖矩阵 + 12 daemon 通信网格

维度 4: 替代方案论证
  └── 保守改良 / Capability Folding / 混合方案 三选一的科学比较

维度 5: 风险边界论证
  └── 重构带来的 5 大风险与对应的工程缓解

维度 6: 决策与硬约束
  └── 最终结论 + 必须同时修改的 11 份文档清单
```

### 0.2 论证的科学性原则

本论证遵循三条科学原则：

1. **证伪优先于证实**：不收集支持证据，而是寻找可能推翻结论的反证。如果反证站得住脚，结论必须修改。
2. **整体优先于局部**：A-IPC 的优化不能以破坏整体契约一致性为代价。如果存在不可调和的冲突，整体契约优先。
3. **工程优先于理论**：理论上的优雅不等于工程上的正确。0 行代码现状、CI 校验机制、维护成本等工程现实必须纳入论证。

---

## §1 维度 1：A-IPC 作为"第一块基石"的整体定位论证

### 1.1 用户的核心命题

用户提出："对于极境内核来说，A-IPC 将是 AirymaxOS 的第一块基石。"

这个命题的工程含义是什么？

### 1.2 基石的三个工程属性

在建筑工程学中，基石（cornerstone）有三个不可妥协的属性：

| 属性 | 建筑学含义 | agentrt-linux 工程含义 |
|------|----------|---------------------|
| **不可移动性** | 基石一旦奠定，整座建筑以它为参照 | A-IPC 的 128B 消息头、magic、opcode 一旦发布即冻结 |
| **承重性** | 基石承受整座建筑的重量 | A-IPC 承载 12 daemon 通信网格 + 5 模块协作 |
| **形状确定性** | 基石的形状决定上层结构的对齐方式 | A-IPC 的能力校验机制决定 110-security/03-capability-model.md 的实现 |

### 1.3 当前 A-IPC 设计的基石属性评估

读取 [10-unify-design.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/10-unify-design.md) §8 A-IPC 章节后的评估：

```
当前 A-IPC 设计（双平面架构）:

  ┌─────────────────────────────────────────────────────┐
  │ 控制面（seL4 风格 12 syscall）                       │
  │  ├─ decode_and_invoke() 能力校验路径 #1              │
  │  ├─ 同步阻塞 → 12 daemon 网格死锁风险（21 号审查）   │
  │  └─ ~1μs syscall 开销                                │
  ├─────────────────────────────────────────────────────┤
  │ 数据面（io_uring 异步）                              │
  │  ├─ cap_check_fast() 能力校验路径 #2                 │
  │  ├─ per-CPU cache + radix tree + IPI coherency      │
  │  └─ ~160ns fastpath                                 │
  ├─────────────────────────────────────────────────────┤
  │ 共享：仅 Layout C 128B 消息头格式                    │
  └─────────────────────────────────────────────────────┘

基石属性评估：
  ✗ 不可移动性：弱。控制面 12 syscall 中 8 个可被 io_uring 替代，
                 形态不稳定。
  ✗ 承重性：弱。两条能力校验路径互不贯通，12 daemon 通信存在
            死锁风险，承重结构存在裂缝。
  ✓ 形状确定性：中。Layout C 128B 消息头是确定的，但能力校验
                机制是双轨的，上层 capability-model.md 难以对齐。
```

**结论：当前 A-IPC 设计作为"第一块基石"，三个属性中两个为弱。这不是一个稳定的基石。**

### 1.4 Capability Folding 重构后的基石属性评估

```
Capability Folding 重构后（单平面架构）:

  ┌─────────────────────────────────────────────────────┐
  │ A-IPC（io_uring 数据面 + Badge 自验证）              │
  │  ├─ 唯一能力校验路径：C-S9 Badge 校验（~10ns）       │
  │  ├─ 全异步 io_uring，无同步阻塞死锁                  │
  │  ├─ atomic_t Epoch + 静态数组，无 radix tree         │
  │  └─ ~158ns fastpath（含 33 号 NONBLOCK 修复）        │
  ├─────────────────────────────────────────────────────┤
  │ 能力管理（独立于 IPC）                                │
  │  └─ airy_sys_call → mint/derive/revoke/epoch_bump   │
  └─────────────────────────────────────────────────────┘

基石属性评估：
  ✓ 不可移动性：强。Layout C v4（含 capability_badge）一经发布即冻结，
                magic 不变，128B 总长不变。
  ✓ 承重性：强。单平面无死锁，单能力路径无歧义，12 daemon 通信
            网格稳定。
  ✓ 形状确定性：强。Badge + Epoch 模型为 capability-model.md
                提供唯一对齐目标。
```

**结论：Capability Folding 重构后，A-IPC 三个基石属性全部为强。这是一个稳定的基石。**

### 1.5 定位论证小结

从"第一块基石"的定位出发，Capability Folding 重构是**必要的**。当前设计的双平面架构不符合基石的工程属性要求。这个论证不依赖于性能数据或复杂度比较——它从用户提出的"基石"命题直接推导得出。

---

## §2 维度 2：契约一致性论证

### 2.1 IRON-9 v3 四层模型的硬约束

读取 [06-iron9-shared-model.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/06-iron9-shared-model.md) 和 [120-cross-project-code-sharing.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md) 后，提取 IRON-9 v3 的硬约束：

| 约束 ID | 内容 | 来源 |
|---------|------|------|
| IC-1 | [SC] 层 10 个头文件物理宿主唯一：`kernel/include/airymax/` | 120 号 §2.1 |
| IC-2 | [SC] 层双端逐字节相同，CI 通过 `sc-dual-ci.yml` 校验 | 120 号 §7.1 |
| IC-3 | [SC] 头文件变更分类：新增字段（向后兼容）需双端同步 | 120 号 §7.4 |
| IC-4 | magic 值一经发布即冻结，禁止修改 | 120 号 §7.5 |
| IC-5 | [SC] `ipc.h` 当前定义：128B 消息头，offset 44-127 为 `reserved[84]` | 120 号 §2.7 |
| IC-6 | [SC] `ipc.h` 包含 `_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128)` | 120 号 §2.7 |
| IC-7 | [DSL] 降级块在 `ipc.h` 底部：仅保留 magic + opcode + payload_len | 11 号 §2.2 |

### 2.2 Capability Folding 与 [SC] 契约的冲突分析

29/30 号方案提出的 Layout C v4：

```
offset  44: capability_badge (8B)  ← 新增
offset  52: crc32            (4B)  ← 新增
offset  56: __reserved[72]  (72B) ← 缩减（原 reserved[84]）
```

**冲突分析**：

| 约束 | 是否冲突 | 分析 |
|------|---------|------|
| IC-1（物理宿主） | 不冲突 | `ipc.h` 仍在 `kernel/include/airymax/` |
| IC-2（逐字节相同） | **需要同步** | agentrt 和 agentrt-linux 两端 `ipc.h` 必须同步修改 |
| IC-3（变更分类） | **向后兼容** | 新增字段在原 reserved 空间内，128B 总长不变，magic 不变。属于"新增字段（向后兼容）"分类 |
| IC-4（magic 冻结） | 不冲突 | magic 仍为 0x41524531 'ARE1' |
| IC-5（当前定义） | **需要更新** | `reserved[84]` → `capability_badge + crc32 + reserved[72]` |
| IC-6（_Static_assert） | 不冲突 | 总长仍为 128 字节 |
| IC-7（[DSL] 降级块） | **需要更新** | [DSL] 模式下 capability_badge 字段必须存在但被忽略（值=0） |

**结论**：Capability Folding 与 [SC] 契约**没有不可调和的冲突**。所有冲突都属于"向后兼容的新增字段"分类，按照 120 号 §7.4 的变更流程处理即可。

### 2.3 跨端语义一致性论证（核心冲突点）

这是最关键的论证点。Capability Folding 的核心机制是：

```
内核侧：agent_caps[1024] 静态数组 + atomic_t Epoch
         ↓
         Badge 编译（sec_d 调用，使用 get_random_bytes()）
         ↓
         Badge 校验（fastpath C-S9，3 次 READ_ONCE + 4 次比较）
```

**问题**：agentrt 用户态（运行在普通 Linux 上，没有 agentrt-linux 内核）**无法维护这个机制**：

1. agentrt 用户态没有内核静态数组 `agent_caps[]`
2. agentrt 用户态没有 `get_random_bytes()` 内核函数
3. agentrt 用户态没有 `atomic_t` 全局 Epoch
4. agentrt 用户态没有 sec_d 守护进程

**这意味着**：如果 `capability_badge` 字段进入 [SC] `ipc.h`，两端对这个字段的**语义理解**不同：

| 端 | capability_badge 字段语义 |
|----|--------------------------|
| agentrt-linux 内核 | 编译的 Badge (Epoch<<48 \| RandomTag<<16)，由 sec_d 生成，内核静态数组校验 |
| agentrt 用户态 | 始终为 0，不使用 Badge 机制，使用传统 capability 引用（cap_t） |

**这违反了 IRON-9 v3 [SC] 层的"逐字节相同 + 语义一致"原则吗？**

### 2.4 深度论证：[SC] 语义一致性的精确定义

重新读取 [06-iron9-shared-model.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/06-iron9-shared-model.md) §2 和 [120-cross-project-code-sharing.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md) §2.1 后，[SC] 层的精确语义是：

> **[SC] 共享契约层**：完全共享代码，10 个头文件，定义**数据结构、magic、操作码、枚举**。两端共同依赖，**逐字节相同**。

关键：[SC] 共享的是**数据结构定义**，不是**实现语义**。这正是 [SS] 语义同源层的存在意义：

> **[SS] 语义同源层**：高层 API 语义同源，签名独立演进。两端通过 [SC] 契约层保证语义一致，无需适配层。

具体到 IPC 传输，120 号 §5.2 明确：
- agentrt：用户态消息队列（mqueue/io_uring）
- agentrt-linux：内核 io_uring 驱动（IORING_OP_URING_CMD）
- [SC] 契约依据：`ipc.h` 128B 消息头 + magic 'ARE1'

**结论**：[SC] 共享的是 128B 消息头的**二进制布局**，不是**校验机制**。两端对 `capability_badge` 字段的校验机制不同，是完全符合 IRON-9 v3 四层模型的——这属于 [SS] 语义同源层的范畴。

### 2.5 精确的 [SC] 更新方案

基于上述论证，[SC] `ipc.h` 的更新方案如下：

```c
/* kernel/include/airymax/ipc.h —— [SC] 共享契约层 */

/* IPC magic: 0x41524531 = 'ARE1' (不变，IC-4 冻结) */
#define AIRY_IPC_MAGIC    0x41524531u

/* Fixed 128-byte message header (总长不变，IC-6 _Static_assert 保持) */
#define AIRY_IPC_HDR_SZ   128

/* SQE/CQE operation codes (新增 CAP_REQUEST) */
enum airy_ipc_op {
    AIRY_IPC_OP_SEND        = 0,
    AIRY_IPC_OP_RECV        = 1,
    AIRY_IPC_OP_SEND_BATCH  = 2,
    AIRY_IPC_OP_CANCEL      = 3,
    AIRY_IPC_OP_FREEZE      = 4,   /* 新增：A-ULS 触发的队列冻结 */
    AIRY_IPC_OP_CAP_REQUEST = 0x10, /* 新增：能力请求（无需 Badge） */
};

/* Message flags (新增 CAP_CARRY, RESPONSE, BATCH, ENCRYPT, COMPRESS) */
#define AIRY_IPC_F_NOWAIT      (1u << 0)
#define AIRY_IPC_F_SIGNAL      (1u << 1)
#define AIRY_IPC_F_CAP_CARRY   (1u << 2)  /* 新增：消息携带 capability_badge */
#define AIRY_IPC_F_RESPONSE    (1u << 3)  /* 新增：响应消息 */
#define AIRY_IPC_F_BATCH_HEAD  (1u << 4)  /* 新增：BATCH 起始 */
#define AIRY_IPC_F_BATCH_TAIL  (1u << 5)  /* 新增：BATCH 结束 */
#define AIRY_IPC_F_ENCRYPT     (1u << 6)  /* 新增：payload 已加密 */
#define AIRY_IPC_F_COMPRESS    (1u << 7)  /* 新增：payload 已压缩 */

/**
 * struct airy_ipc_msg_hdr - IPC message header (128 bytes, [SC] shared)
 *
 * Layout C v4：在原 reserved[84] 空间内新增 capability_badge + crc32，
 * 总长保持 128 字节，magic 保持 'ARE1' 不变。
 *
 * 跨端语义（[SS] 语义同源层）：
 * - agentrt-linux 内核：capability_badge 由 sec_d 编译，fastpath C-S9 校验
 * - agentrt 用户态：capability_badge 始终为 0，使用传统 cap_t 引用
 * - 两端共享二进制布局，校验机制属于 [SS] 层
 */
struct airy_ipc_msg_hdr {
    __u32   magic;              /* offset  0, 'ARE1' */
    __u16   opcode;             /* offset  4 */
    __u16   flags;              /* offset  6 */
    __u64   trace_id;           /* offset  8 */
    __u64   timestamp_ns;       /* offset 16 */
    __u64   src_task;           /* offset 24 */
    __u64   dst_task;           /* offset 32 */
    __u32   payload_len;        /* offset 40 */
    __u64   capability_badge;   /* offset 44, [SS] 语义同源：agentrt-linux 用，agentrt=0 */
    __u32   crc32;              /* offset 52, CRC32 覆盖 header[0:52) + payload */
    __u8    reserved[72];       /* offset 56, 保留，必须为零 */
} __attribute__((packed));

_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128,
    "IPC message header must be exactly 128 bytes");
```

**这个方案的科学性**：
1. 二进制布局两端完全相同（满足 IC-2 逐字节相同）
2. magic 不变（满足 IC-4 冻结）
3. 总长不变（满足 IC-6 _Static_assert）
4. 新增字段在原 reserved 空间内（属于 IC-3 "向后兼容"分类）
5. 校验机制差异由 [SS] 层承载（符合 IRON-9 v3 四层模型）

### 2.6 契约一致性论证小结

Capability Folding 与 IRON-9 v3 四层模型**没有不可调和的冲突**。核心机制（Badge 编译与校验）属于 [SS] 语义同源层，不是 [SC] 共享契约层。[SC] `ipc.h` 的更新属于"向后兼容的新增字段"分类，按照 120 号 §7.4 的变更流程处理即可。

---

## §3 维度 3：工程现实论证

### 3.1 0 行代码现状的战略价值

读取 [00-comprehensive-analysis-v2.2.md](file:///home/spharx/SpharxWorks/airymaxhub/docs-closed/agentrt-linux/00-reviews/_review_v2.2/00-comprehensive-analysis-v2.2.md) 后确认：

```
agentrt-linux 当前工程状态：
  .md 文档：128+ 份（设计完整）
  .c 源文件：0 行（代码真空）
  .h 头文件：0 个
  Kconfig：0 个
  Kbuild：1 个（仅顶层空 Makefile）
  8 子仓：全部 README-only
```

**这个状态对 Capability Folding 重构的影响**：

| 因素 | 影响 |
|------|------|
| 0 行内核代码 | **正向**：无任何代码需要重构，无任何 ABI 需要兼容 |
| 128 份设计文档 | **中性**：文档需要同步更新，但文档更新成本远低于代码重构 |
| 8 子仓 README-only | **正向**：子仓设计可同步调整，无既有实现约束 |
| [SC] 头文件未创建 | **正向**：`ipc.h` 还未物理存在，可直接以 Layout C v4 创建 |

**战略结论**：当前是采用 Capability Folding 重构的**最佳时间窗口**。一旦第一行内核代码落地，重构成本将以 10 倍量级上升。

### 3.2 Airymax Unify Design §10 SSoT 硬约束分析

读取 [10-unify-design.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/10-unify-design.md) §10 SSoT 声明：

```
技术选型权威声明：
  - 调度：sched_tac，不使用 sched_ext
  - IPC：IORING_OP_URING_CMD + registered buffer + mmap，不使用 page flipping
  - 安全：纯 C LSM 模块（对齐 openEuler），不使用 BPF LSM    ← 关键
  - 日志内存：alloc_pages(GFP_KERNEL) + mmap，不使用 DMA 一致性内存
  - [SC] 物理宿主：kernel/include/airymax/，共 10 个头文件
```

**冲突分析**：

Capability Folding 将能力校验从"纯 C LSM 模块"转移到"fastpath 内联 Badge 校验"。这是否违反 §10 SSoT 的"安全采用纯 C LSM 模块"？

**深度论证**：

读取 [10-unify-design.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/10-unify-design.md) §7.1 Micro-Supervisor 设计：

```
Micro-Supervisor 是内核态的纯 C LSM 模块（不使用 BPF LSM，对齐 openEuler 纯 C 模式），
负责检测非法 Capability 并立即执法：

1. 检测：纯 C LSM 钩子检测到伪造/越权 Capability
2. 冻结：立即设置 ring->frozen = true
3. 返回：返回 AIRY_FAULT_ABNORMAL_CAP (0x1005)
4. 通知：eventfd 通知 Macro-Supervisor
```

**关键发现**：§10 SSoT 的"纯 C LSM"约束针对的是**检测机制**（不用 BPF LSM），不是**校验位置**。Capability Folding 的 Badge 校验（C-S9）仍然可以**作为纯 C LSM 的第一层快速校验**，而完整的 capability 撤销、审计、策略裁决仍由纯 C LSM 模块承担。

**精确的职责划分**：

```
纯 C LSM 模块（不变，对齐 §10 SSoT）：
  ├─ Capability 策略加载（通过 airy_sys_call）
  ├─ Capability 撤销裁决（mint/derive/revoke）
  ├─ 审计日志记录
  ├─ AIRY_FAULT_ABNORMAL_CAP 触发
  └─ ring->frozen 执法

Capability Folding Badge 校验（新增，作为纯 C LSM 的 fastpath 内联）：
  ├─ C-S9：badge_epoch == global_epoch（~3ns）
  ├─ C-S9：badge_rtag == agent_caps[src_task].random_tag（~3ns）
  ├─ C-S9：agent_perms & required == required（~3ns）
  └─ 失败 → 返回 AIRY_ECAP_* 错误码（不触发 Fault，不冻结 ring）
```

**结论**：Capability Folding **不违反** §10 SSoT 的"纯 C LSM"约束。Badge 校验是纯 C LSM 的 fastpath 内联优化，完整的 LSM 职责（策略、撤销、审计、执法）仍由纯 C LSM 模块承担。

### 3.3 五模块依赖矩阵

读取 [10-unify-design.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/10-unify-design.md) §2.1 模块间关系后，构建依赖矩阵：

```
        A-UEF   A-ULP   A-UCS   A-ULS   A-IPC
A-UEF    -       -       -       -       -
A-ULP   使用     -       -       -       -
A-UCS   使用     -       -       -       -
A-ULS   使用    使用    使用     -      使用
A-IPC   使用    使用     -      使用     -
```

**A-IPC 重构对其他 4 模块的影响**：

| 模块 | 影响程度 | 具体影响 |
|------|:------:|---------|
| A-UEF | 中 | 新增 3 个 Capability 错误码（AIRY_ECAP_BADGE/EPOCH/FORGED），值域 [-78, -80] |
| A-ULP | 小 | fastpath 中 Badge 校验失败时通过 A-ULP Ring Buffer 记录（已有机制） |
| A-UCS | 小 | 新增配置项：`kernel.airy.ipc.badge_epoch` （sysctl 可读） |
| A-ULS | 中 | ring->frozen 机制不变，但触发条件从"radix tree miss"变为"Badge verify fail + repeat > threshold" |

**结论**：A-IPC 重构对其他 4 模块的影响可控。最大影响在 A-UEF（新增错误码）和 A-ULS（触发条件调整），都属于增量修改，不是结构性重构。

### 3.4 工程现实论证小结

工程现实**支持** Capability Folding 重构：
1. 0 行代码现状是最佳时间窗口
2. 不违反 §10 SSoT 的"纯 C LSM"约束
3. 对其他 4 模块影响可控（增量修改）

---

## §4 维度 4：替代方案论证

### 4.1 三种方案的科学比较

| 方案 | 描述 | 核心机制 |
|------|------|---------|
| **方案 A：保守改良** | 保留双平面，修复已知缺陷 | 12 syscall + io_uring，radix tree + per-CPU cache，修复死锁与排序问题 |
| **方案 B：Capability Folding** | 重构为单平面，Badge 自验证 | io_uring + Badge + Epoch，消除 8 syscall，消除 radix tree |
| **方案 C：混合方案** | 保留双平面，Badge 作为 fastpath 优化 | 12 syscall + io_uring，Badge 替代 radix tree fastpath |

### 4.2 方案 A（保守改良）评估

**优点**：
- 最小变更，文档改动最少
- 保留 seL4 形式化验证路径（理论上）

**缺点**：
1. **不解决根本矛盾**：25 号审查已论证，双平面的"两条能力校验路径"是所有问题的根源
2. **死锁风险仅缓解不消除**：12 daemon 同步阻塞死锁需要复杂的超时与重试机制
3. **复杂度持续累积**：radix tree + per-CPU cache + IPI coherency 栈需长期维护
4. **违背"简约就是美"**：28 号审查已论证，当前设计有 7 颗"看不见的螺丝"

**科学判定**：方案 A 是"推迟问题"，不是"解决问题"。

### 4.3 方案 C（混合方案）评估

**优点**：
- 保留 12 syscall 用于需要同步语义的场景（如 airy_sys_call 的 capability invocation）
- Badge 作为 fastpath 优化，radix tree 作为 slowpath 兜底

**缺点**：
1. **双轨制长期存在**：Badge 和 radix tree 并行维护，复杂度翻倍
2. **语义混淆**：何时用 Badge、何时用 radix tree，需要明确的调度规则
3. **违背"每个技术点只允许有一个权威源"**：10-unify-design.md §1.2 第三条设计哲学
4. **不是真正的简约**：28 号审查的"隐藏螺丝测试"不通过

**科学判定**：方案 C 是"两头不讨好"，既没有方案 A 的保守稳定性，也没有方案 B 的彻底简约性。

### 4.4 方案 B（Capability Folding）评估

**优点**：
1. 解决根本矛盾（25 号审查论证）
2. 真正简约（28 号审查 7 颗螺丝全部拧掉）
3. 性能提升（C-S9 从 ~50-100ns 到 ~10ns）
4. 死锁消除（全异步 io_uring）
5. 复杂度降低（消除 radix tree + per-CPU cache + IPI coherency）
6. 契约一致性可达成（§2 论证）

**缺点**：
1. 牺牲 seL4 架构级隔离（31 号审查论证，可接受）
2. 丧失 seL4 形式化验证路径（30 号审查论证，agentrt-linux 不需要）
3. 原子性丢失（30 号审查论证，异步场景可接受）
4. 需要同步更新 11 份文档（成本可控）

**科学判定**：方案 B 是"经过深度理解后的精髓提炼"，符合乔布斯/艾夫设计哲学。

### 4.5 替代方案论证小结

三方案比较的决策矩阵：

| 评估维度 | 方案 A（保守） | 方案 B（重构） | 方案 C（混合） |
|---------|:---:|:---:|:---:|
| 解决根本矛盾 | ✗ | ✓ | ✗ |
| 契约一致性 | ✓ | ✓ | ✗ |
| 工程现实可行性 | ✓ | ✓ | ✗ |
| 简约性（28 号哲学） | ✗ | ✓ | ✗ |
| 性能 | 中 | 优 | 良 |
| 长期维护成本 | 高 | 低 | 极高 |
| **综合** | **不推荐** | **推荐** | **不推荐** |

---

## §5 维度 5：风险边界论证

### 5.1 重构带来的 5 大风险

| # | 风险 | 严重度 | 来源 | 缓解措施 |
|---|------|:---:|------|---------|
| R1 | Badge 伪造攻击 | P0 | 30 号审查 | 随机标签 + 内核静态数组（已修复） |
| R2 | uring_lock 持有 wake_up 导致争用 | P0 | 33 号审查 | NONBLOCK 模式 + io-wq 接管（已修复） |
| R3 | seL4 架构级隔离丧失 | P1 | 31 号审查 | 数据结构级隔离 + CBMC 全函数验证（可接受） |
| R4 | 原子性丢失（seL4 Call 语义） | P1 | 30 号审查 | request_id/correlation_id 模式（异步场景可接受） |
| R5 | [SC] 双端同步更新成本 | P2 | 120 号 §7.4 | sc-dual-ci.yml 已有机制，一次同步更新即可 |

### 5.2 风险边界的精确定义

```
可接受风险（已缓解，不阻塞重构）：
  - R1（Badge 伪造）：30 号审查已修复
  - R2（uring_lock）：33 号审查已修复

可接受 trade-off（经过论证，不阻塞重构）：
  - R3（隔离丧失）：31 号审查论证 agentrt-linux 不需要架构级隔离
  - R4（原子性丢失）：30 号审查论证异步场景不需要原子性

工程成本（可控，不阻塞重构）：
  - R5（[SC] 同步）：sc-dual-ci.yml 已有机制
```

### 5.3 不可接受的风险（不存在）

经过 33 份审查报告的逐项验证，**没有发现不可接受的风险**。所有风险都有明确的缓解措施或可接受的 trade-off。

---

## §6 维度 6：决策与硬约束

### 6.1 最终决策

**基于 6 个维度的科学论证，agentrt-linux 应当采用 Capability Folding 重构方案。**

决策依据：
1. **维度 1（定位）**：A-IPC 作为"第一块基石"，Capability Folding 提供更强的基石属性
2. **维度 2（契约）**：与 IRON-9 v3 四层模型没有不可调和的冲突
3. **维度 3（工程）**：0 行代码现状是最佳时间窗口，不违反 §10 SSoT
4. **维度 4（替代）**：三方案比较中，Capability Folding 综合最优
5. **维度 5（风险）**：5 大风险全部可控或可接受
6. **设计哲学**：符合乔布斯/艾夫"简约就是美"原则

### 6.2 必须同时修改的 11 份文档清单

重构不能孤立进行，必须同时修改以下文档以保持整体一致性：

| # | 文档 | 修改内容 | 优先级 |
|---|------|---------|:---:|
| 1 | [10-unify-design.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/10-unify-design.md) §8 | A-IPC 章节：双平面 → 单平面 + Capability Folding | P0 |
| 2 | [10-unify-design.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/10-unify-design.md) §10 | SSoT 声明：新增 "A-IPC 采用 Capability Folding" | P0 |
| 3 | [30-interfaces/01-syscalls.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/01-syscalls.md) | syscall 表 12 → 4，§1.4 Capability Invocation 重写 | P0 |
| 4 | [30-interfaces/02-ipc-protocol.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/02-ipc-protocol.md) | Layout C v4，opcode 表新增 FREEZE/CAP_REQUEST | P0 |
| 5 | [30-interfaces/07-ipc-fastpath.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/07-ipc-fastpath.md) | C-S9 实现（Badge 校验），状态机 7 态 | P0 |
| 6 | [50-engineering-standards/120-cross-project-code-sharing.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md) §2.7 | [SC] `ipc.h` Layout C v4 定义 | P0 |
| 7 | [30-interfaces/08-sc-error-contract.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/08-sc-error-contract.md) §2.4 | Capability 码空间新增 AIRY_ECAP_BADGE/EPOCH/FORGED | P0 |
| 8 | [110-security/03-capability-model.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/110-security/03-capability-model.md) | radix tree → Epoch + 静态数组 | P1 |
| 9 | [10-architecture/11-degraded-survival-layer.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/11-degraded-survival-layer.md) §2.2 | [DSL] `ipc.h` 降级块：capability_badge=0 | P1 |
| 10 | [40-dataflows/03-ipc-flow.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/40-dataflows/03-ipc-flow.md) | 消除控制面数据流，数据面自治三原则重定义 | P1 |
| 11 | [170-performance/03-ipc-performance.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/170-performance/03-ipc-performance.md) | fastpath 延迟数值更新（~158ns） | P2 |

### 6.3 6 条硬约束（不可妥协）

基于本论证，A-IPC 重构必须遵守以下 6 条硬约束：

```
H1: Layout C v4 总长保持 128 字节，magic 保持 0x41524531 'ARE1'
H2: capability_badge 字段进入 [SC] ipc.h，但校验机制属于 [SS] 层
H3: agentrt 用户态 capability_badge 始终为 0，使用传统 cap_t 引用
H4: agentrt-linux 内核 capability_badge 由 sec_d 编译，fastpath C-S9 校验
H5: 纯 C LSM 模块职责不变（策略/撤销/审计/执法），Badge 校验是其 fastpath 内联
H6: [DSL] 降级模式下 capability_badge 字段存在但被忽略（值=0，跳过校验）
```

### 6.4 错误码空间修正

30 号审查提出的 AIRY_ECAP_BADGE_FORGED (-53) 错误码值定位错误（-53 在 IPC 码空间 [-41, -70]，不在 Capability 码空间 [-71, -100]）。修正后的错误码分配：

```c
/* kernel/include/airymax/error.h —— Capability 码空间 [-71, -100] */

#define AIRY_ECAP_MISSING       (-71)  /* 已有：Capability 缺失 */
#define AIRY_ECAP_REVOKED       (-72)  /* 已有：Capability 已撤销 */
#define AIRY_ECAP_EXPIRED       (-73)  /* 已有：Capability 已过期 */
#define AIRY_ECAP_MISMATCH      (-74)  /* 已有：Capability 不匹配 */
#define AIRY_ECAP_LSM_DENIED    (-75)  /* 已有：纯 C LSM 拒绝 */
#define AIRY_ECAP_RADIX_MISS    (-76)  /* 已有：radix tree 查找失败（保留，[DSL] 模式使用） */
#define AIRY_ECAP_STATIC_KEY    (-77)  /* 已有：static_key 禁用（保留，[DSL] 模式使用） */

/* 新增：Capability Folding Badge 校验错误码 */
#define AIRY_ECAP_BADGE         (-78)  /* 新增：Badge 格式无效或 Random Tag 不匹配 */
#define AIRY_ECAP_EPOCH         (-79)  /* 新增：Badge Epoch 不匹配（已撤销或过期） */
#define AIRY_ECAP_FORGED        (-80)  /* 新增：检测到 Badge 伪造尝试（触发 Fault） */
```

**注意**：AIRY_ECAP_RADIX_MISS (-76) 和 AIRY_ECAP_STATIC_KEY (-77) 保留，因为 [DSL] 降级模式下仍使用 radix tree 兜底路径。

---

## §7 论证总结

### 7.1 一句话结论

**从 agentrt-linux 整体方案高度的科学严谨论证得出：应当采用 Capability Folding 重构 A-IPC，因为它是"第一块基石"的正确形状，与 IRON-9 v3 四层模型没有不可调和的冲突，在 0 行代码现状下是最佳时间窗口，且所有风险可控。**

### 7.2 论证的局限性

本论证有以下局限性，需要在实施中持续验证：

1. **性能数据基于理论推导**：C-S9 ~10ns 是基于 L1 cache hit 假设，实际性能需在第一行代码落地后基准测试
2. **CBMC 验证可行性未实证**：fastpath 100 行代码的 CBMC 全函数验证需要实际工具链测试
3. **12 daemon 通信网格未仿真**：死锁消除的论证基于理论分析，需要实际 12 daemon 原型验证

### 7.3 下一步

基于本论证结论，下一步是：

1. **阶段 4**：基于 6 条硬约束，重新设计 A-IPC 完整方案（35 号文档）
2. **阶段 5**：全面检查 Airymax Unify Design 五模块一致性（36 号文档）
3. **实施前**：同步更新 11 份文档（§6.2 清单）

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. | 从整体方案高度的科学论证 | v1.0 | 2026-07-18
