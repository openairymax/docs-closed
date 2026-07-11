Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agentrt-linux v0.7.0 深度综合审查报告

## 三大核心议题：Syscall 极简研究 / 01-kernel.md vs SSoT 对比 / 系统性审查

> **审查版本**: v0.7.0
> **审查日期**: 2026-07-11
> **审查范围**: 核心 Syscall 槽位缩减可行性研究 + 01-kernel.md 与 SSoT 根本性分歧对比分析 + agentrt-linux 方案更深层次系统性审查
> **前序版本**: v0.6.0 (58/100, C+)

---

# 第一部分：核心 Syscall 槽位 < 20 的可行性研究

## 1.1 seL4 基线参考

seL4 是微内核 syscall 极简主义的标杆。其 `syscall.xml`（`libsel4/include/api/syscall.xml`）定义：

| 模式 | Syscall 数量 | 具体调用 |
|------|-------------|---------|
| **非 MCS** | **8** | Call, ReplyRecv, Send, NBSend, Recv, NBRecv, Reply, Yield |
| **MCS** | **11** | Call, ReplyRecv, NBSendRecv, NBSendWait, Send, NBSend, Recv, NBRecv, Wait, NBWait, Yield |

**核心洞察**：seL4 的 8 个 syscall **全部是 IPC/调度原语**，没有"任务管理"、"内存管理"、"安全管理"等独立 syscall 类别。一切操作通过 **capability invocation**（即向 capability 发送 IPC 消息）完成。seL4 的错误码也仅 10 种（`libsel4/include/sel4/errors.h`），使用 `seL4_NumErrors` 哨兵模式。

## 1.2 当前 agentrt-linux Syscall 清单分析

当前（01-syscalls.md）共 **20 个 syscall**，分配 **120 个槽位**（6 类 × 20），存在严重的 **槽位膨胀**：

| 编号 | Syscall | 分类 | 可消除? | 替代方案 |
|------|---------|------|---------|---------|
| 512 | `task_submit` | 任务管理 | ✅ | IPC 消息 → 调度器 capability |
| 513 | `task_cancel` | 任务管理 | ✅ | IPC 消息 → 调度器 capability |
| 514 | `task_status` | 任务管理 | ✅ | 共享内存 / IPC 查询 |
| 515 | `task_migrate` | 任务管理 | ✅ | IPC 消息 → 迁移服务 |
| 532 | `ipc_send` | IPC | ✅ | io_uring SQE（已规划） |
| 533 | `ipc_recv` | IPC | ✅ | io_uring CQE（已规划） |
| 534 | `ipc_register_ring` | IPC | ⚠️ | io_uring_register() 已有 |
| 552 | `rovol_snapshot` | 内存 | ⚠️ | 可合并为 `rovol_ctl` |
| 553 | `rovol_restore` | 内存 | ⚠️ | 可合并为 `rovol_ctl` |
| 554 | `rovol_migrate` | 内存 | ⚠️ | 可合并为 `rovol_ctl` |
| 555 | `cxl_tier_set` | 内存 | ✅ | sysfs / cgroupfs |
| 556 | `mglru_config` | 内存 | ✅ | sysfs / cgroupfs |
| 572 | `sched_set_policy` | 调度 | ⚠️ | 可合并为 `sched_ctl` |
| 573 | `sched_get_policy` | 调度 | ⚠️ | 可合并为 `sched_ctl` |
| 592 | `capability_request` | 安全 | ✅ | IPC capability invocation |
| 593 | `capability_revoke` | 安全 | ✅ | IPC capability invocation |
| 594 | `lsm_load_policy` | 安全 | ⚠️ | 可合并为 `lsm_ctl` |
| 612 | `clt_phase_notify` | 认知 | ✅ | 共享内存 ring buffer |
| 613 | `clt_register_kthread` | 认知 | ⚠️ | 可合并为 `kthread_ctl` |
| 614 | `wasm_load_module` | 认知 | ⚠️ | 保留（需内核验证签名） |

## 1.3 极简方案：核心 Syscall ≤ 12

借鉴 seL4 的 capability invocation 模型，将 agentrt-linux syscall 缩减为两大层：

### 第一层：IPC 原语层（7 个，借鉴 seL4）

| # | Syscall | 用途 |
|---|---------|------|
| 1 | `agentrt_sys_call` | **capability invocation**：向 capability 发送请求并等待回复。替代 task_submit/cancel/status/capability_request/revoke/clt_phase_notify |
| 2 | `agentrt_sys_reply_recv` | 回复上一条消息并等待下一条（seL4 ReplyRecv） |
| 3 | `agentrt_sys_send` | 异步发送（不等待回复） |
| 4 | `agentrt_sys_nbsend` | 非阻塞发送 |
| 5 | `agentrt_sys_recv` | 阻塞等待消息 |
| 6 | `agentrt_sys_nbrecv` | 非阻塞接收 |
| 7 | `agentrt_sys_yield` | 让出 CPU |

### 第二层：控制面原语层（5 个，agentrt-linux 专属）

| # | Syscall | 用途 |
|---|---------|------|
| 8 | `agentrt_sys_rovol_ctl` | 统一记忆卷载控制（合并 snapshot/restore/migrate 3 个） |
| 9 | `agentrt_sys_sched_ctl` | 统一调度策略控制（合并 set/get_policy 2 个） |
| 10 | `agentrt_sys_lsm_ctl` | LSM 策略加载 |
| 11 | `agentrt_sys_wasm_load` | Wasm 模块加载（需内核验证签名） |
| 12 | `agentrt_sys_kthread_ctl` | CoreLoopThree kthread 注册 |

**总计：12 个核心 syscall，远小于 20 个目标。**

### 1.4 缩减原理

| 被消除的 Syscall | 消除方式 | 原理 |
|-----------------|---------|------|
| task_submit/cancel/status/migrate | → `agentrt_sys_call` | seL4 风格：操作编码在 IPC 消息中，capability 决定权限 |
| capability_request/revoke | → `agentrt_sys_call` | capability 本身即权限，通过 IPC 传递 |
| ipc_send/recv | → io_uring SQE/CQE | 数据面走 io_uring 零拷贝，控制面走 syscall |
| cxl_tier_set/mglru_config | → sysfs/cgroupfs | 内核配置不应用 syscall，应用标准 Linux 接口 |
| clt_phase_notify | → 共享内存 ring buffer | 高频状态更新不应走 syscall（NFR-P-001a < 1μs 无法满足） |

### 1.5 槽位重新分配

| 编号段 | 分类 | 数量 | 说明 |
|--------|------|------|------|
| 512-518 | IPC 原语 | 7 | Call/ReplyRecv/Send/NBSend/Recv/NBRecv/Yield |
| 519-523 | 控制面原语 | 5 | rovol_ctl/sched_ctl/lsm_ctl/wasm_load/kthread_ctl |
| 524-543 | 预留 | 20 | 未来扩展（MAJOR 版本内可追加） |

**总槽位：32 个（12 核心 + 20 预留），从 120 缩减 73%。**

### 1.6 结论

**核心 syscall 完全可以 ≤ 12 个（< 20 目标）**。关键是将 seL4 的 capability invocation 模型落地：操作类型编码在 IPC 消息中而非 syscall 编号中，capability 决定权限边界。这与 agentrt-linux 已在设计的 seL4 风格 capability 系统（01-kernel.md §5）天然一致——当前 20 个 syscall 的设计与 capability 模型存在架构矛盾：如果已有 capability 系统，为什么还需要独立的 `capability_request` syscall？

---

# 第二部分：01-kernel.md vs SSoT 对比分析表

SSoT = `50-engineering-standards/120-cross-project-code-sharing.md`

## 冲突矩阵（共 12 项冲突）

### 冲突 1：`struct airymax_task_desc` 结构体定义

| 维度 | SSoT (§2.6) | 01-kernel.md (§10.1.1 L673) | 冲突等级 |
|------|-------------|---------------------------|----------|
| 字段数量 | **4 字段** | **11 字段** | 🔴 CRITICAL |
| 字段列表 | `magic(__u32)`, `prio(__u16)`, `_pad(__u16)`, `vtime(airymax_vtime_t)` | `magic`, `version`, `priority`, `flags`, `task_id`, `trace_id`, `deadline_ns`, `max_retries`, `cpu_affinity`, `role[32]`, `reserved[32]` | 🔴 CRITICAL |
| 结构体大小 | 8 字节 | ~104 字节 | 🔴 CRITICAL |
| vtime 类型 | `airymax_vtime_t` (int32_t, Q16.16) | `u64` | 🔴 CRITICAL |
| 优先级字段名 | `prio` | `priority` | 🟡 HIGH |

**SSoT 定义**（120-cross-project-code-sharing.md L231-236）：
```c
struct airymax_task_desc {
    __u32       magic;      /* 0x41475453 'AGTS' */
    __u16       prio;       /* 0-139 */
    __u16       _pad;
    airymax_vtime_t vtime;  /* Q16.16 fixed-point */
};
```

**01-kernel.md 定义**（L673）：
```c
struct airymax_task_desc {
    uint32_t magic;          /* 0x41475453 'AGTS' */
    uint16_t version;        /* [IND] */
    uint16_t priority;       /* 0-139 */
    uint32_t flags;          /* [IND] */
    uint64_t task_id;        /* [IND] */
    uint64_t trace_id;       /* [IND] */
    uint64_t deadline_ns;   /* [IND] */
    uint32_t max_retries;    /* [IND] */
    uint32_t cpu_affinity;   /* [IND] */
    char     role[32];       /* [IND] */
    uint8_t  reserved[32];   /* [IND] */
};
```

**推荐统一标准**：以 **SSoT 4 字段为 [SC] 共享契约层**（逐字节相同），01-kernel.md 中 11 字段版本应标注为 **[IND] 内核态扩展视图**（`struct airymax_task_desc_ext`），明确区分 [SC] 核心字段和 [IND] 扩展字段。SSoT 结构体名保持 `struct airymax_task_desc`，内核扩展版本命名为 `struct airymax_task_desc_kern`。

### 冲突 2：`struct airymax_ipc_msg_hdr` 结构体定义

| 维度 | SSoT (§2.7 Layout C) | 01-kernel.md (§10.1.2 L686) | 冲突等级 |
|------|----------------------|---------------------------|----------|
| 字段顺序 | `magic/opcode/flags/trace_id/timestamp_ns/src_task/dst_task/payload_len/reserved[84]` | `magic/version/type/payload_len/flags/src_pid/dst_pid/trace_id/timestamp_ns/reserved` | 🔴 CRITICAL |
| 有无 version | **无** | **有** (`version`) | 🔴 CRITICAL |
| 有无 type | **无**（用 opcode） | **有** (`type`) | 🔴 CRITICAL |
| 任务标识字段名 | `src_task/dst_task` (u64) | `src_pid/dst_pid` | 🔴 CRITICAL |
| 字段数量 | 9 字段 | 10 字段 | 🔴 CRITICAL |
| 结构体名 | `struct airymax_ipc_msg_hdr` | `agentrt_ipc_msg_hdr_t` (typedef) | 🔴 CRITICAL |
| 对齐方式 | `__attribute__((packed))` | 未声明 | 🟡 HIGH |

**SSoT 定义**（120-cross-project-code-sharing.md L276-286）：
```c
struct airymax_ipc_msg_hdr {
    __u32   magic;           /* offset 0, 'ARE1' */
    __u16   opcode;          /* offset 4 */
    __u16   flags;           /* offset 6 */
    __u64   trace_id;        /* offset 8 */
    __u64   timestamp_ns;    /* offset 16 */
    __u64   src_task;        /* offset 24 */
    __u64   dst_task;        /* offset 32 */
    __u32   payload_len;     /* offset 40 */
    __u8    reserved[84];    /* offset 44, 84 bytes */
} __attribute__((packed));
```

**01-kernel.md 描述**（L686）：
```
magic/version/type/payload_len/flags/src_pid/dst_pid/trace_id/timestamp_ns/reserved
```

**推荐统一标准**：完全采用 **SSoT Layout C**。Layout C 是经过 v0.3.0-v0.6.0 多轮审查后确定的唯一合法布局。01-kernel.md 必须：
1. 删除 `version`/`type` 字段（语义由 `opcode` + `flags` 承载）
2. 重命名 `src_pid/dst_pid` → `src_task/dst_task`
3. 重命名 `agentrt_ipc_msg_hdr_t` → `struct airymax_ipc_msg_hdr`
4. 添加 `__attribute__((packed))`
5. 添加 SSoT 声明（指向 120-cross-project-code-sharing.md §2.7）

### 冲突 3：`airymax_struct_ops_state` 枚举值

| 维度 | SSoT (§2.2) | 01-kernel.md (§10.1.3 L692) | 冲突等级 |
|------|-------------|---------------------------|----------|
| 枚举值 | `INIT=0, REGISTERED=1, ACTIVE=2, DRAINING=3` | `INIT=0, INUSE=1, TOBEFREE=2, READY=3` | 🔴 CRITICAL |
| 语义差异 | REGISTERED→ACTIVE→DRAINING 生命周期 | INUSE→TOBEFREE→READY（不同语义） | 🔴 CRITICAL |
| 二进制兼容 | 值相同但语义完全不同 | 值相同但语义完全不同 | 🔴 CRITICAL |

**SSoT 定义**（120-cross-project-code-sharing.md L103-108）：
```c
enum airymax_struct_ops_state {
    AIRYMAX_OPS_INIT       = 0,
    AIRYMAX_OPS_REGISTERED = 1,
    AIRYMAX_OPS_ACTIVE     = 2,
    AIRYMAX_OPS_DRAINING   = 3,
};
```

**01-kernel.md 定义**（L692）：
```
INIT=0/INUSE=1/TOBEFREE=2/READY=3
```

**推荐统一标准**：以 **SSoT 为准**（`INIT/REGISTERED/ACTIVE/DRAINING`）。SSoT 的语义更清晰：REGISTERED 表示已注册但未激活，ACTIVE 表示正在运行，DRAINING 表示正在排空。01-kernel.md 的 `INUSE/TOBEFREE/READY` 语义模糊且与 Linux BPF subsystem 的 struct_ops 生命周期不一致。

### 冲突 4：`airymax_vtime_t` 类型定义

| 维度 | SSoT (§2.6) | 01-kernel.md (§10.1.1 L671) | 冲突等级 |
|------|-------------|---------------------------|----------|
| 类型 | `int32_t` (Q16.16 定点数) | `u64` | 🔴 CRITICAL |
| 有无符号 | 有符号（支持负 vtime） | 无符号（不支持负值） | 🔴 CRITICAL |

**推荐统一标准**：以 **SSoT `int32_t` 为准**。Q16.16 定点数需要符号位，且与内核 `-mno-80387` 禁浮点约束一致。`u64` 类型无法表达 vtime 衰减中的负偏移。

### 冲突 5：struct_ops 状态枚举名称

| 维度 | SSoT | 01-kernel.md | 冲突等级 |
|------|------|-------------|----------|
| 名称 | `airymax_struct_ops_state` | §2.1 L136: `agentrt_struct_ops_state` / §16.1 L1013: `bpf_struct_ops_state` | 🟡 HIGH |

**推荐统一标准**：**`airymax_struct_ops_state`**（SSoT 名称）。同一文档内出现 3 种不同名称，必须统一。

### 冲突 6：Capability 操作命名风格

| 维度 | SSoT | 01-kernel.md (§16.1 L1014) | 冲突等级 |
|------|------|---------------------------|----------|
| 命名风格 | `mint/mintcopy/derive/revoke`（小写） | `Mint/Copy/Derive/Revoke`（PascalCase） | 🟡 HIGH |
| mintcopy vs Copy | `mintcopy` | `Copy`（语义名称不同） | 🟡 HIGH |

**推荐统一标准**：**小写 `mint/mintcopy/derive/revoke`**（SSoT）。C 函数命名遵循 snake_case，PascalCase 仅用于类型名。

### 冲突 7：`agentrt_ipc_msg_hdr_t` typedef vs `struct airymax_ipc_msg_hdr`

| 维度 | SSoT | 01-kernel.md (§10.1 L657) | 冲突等级 |
|------|------|---------------------------|----------|
| 形式 | `struct airymax_ipc_msg_hdr`（无 typedef） | `agentrt_ipc_msg_hdr_t`（typedef） | 🟡 HIGH |

**推荐统一标准**：**`struct airymax_ipc_msg_hdr`**（无 typedef）。遵循 Linux 内核编码规范（OLK-6.6 coding-style.rst §5：禁止结构体 typedef）。

### 冲突 8：LSM 钩子数量

| 维度 | SSoT (§2.4) | 01-kernel.md (§10.1 L659) | 冲突等级 |
|------|-------------|---------------------------|----------|
| 数量 | 252 | 252 | ✅ 一致 |
| 但 OLK-6.6 实际 | — | 250（`include/linux/lsm_hook_defs.h`） | ⚠️ |

**推荐统一标准**：与 OLK-6.6 源码实际计数 **250** 对齐（v0.6.0 P0-04 已识别）。

### 冲突 9：Syscall 数量目标 vs 槽位分配

| 维度 | 01-kernel.md §1.3 L99 | 01-syscalls.md §2.2 L88-95 | 冲突等级 |
|------|----------------------|---------------------------|----------|
| 目标 | ≤ 20 个 syscall | 120 槽位（6 类 × 20） | 🔴 CRITICAL |
| 实际定义 | — | 20 个 syscall | 🔴 CRITICAL |

**矛盾**：目标 ≤ 20，但分配 120 个槽位。如果已达到 20 个（已定义），则无扩展空间；如果 120 槽位是预留，则与 ≤ 20 目标矛盾——预留 120 暗示计划远超 20。

**推荐统一标准**：采用本文第一部分的 **12 核心 + 20 预留 = 32 槽位** 方案。槽位总数 32 与 ≤ 20 目标一致。

### 冲突 10：SCHED_AGENT 在架构图中的使用

| 维度 | SSoT | 01-kernel.md (§10.5 L800) | 冲突等级 |
|------|------|---------------------------|----------|
| 约束 | 禁止 `SCHED_AGENT` 宏，仅作为策略名称 | 架构图中使用 `SCHED_AGENT` 作为标签 | 🟡 MEDIUM |

**推荐统一标准**：架构图中将 `SCHED_AGENT` 标签改为 `SCHED_EXT (SCHED_AGENT 策略)`，明确标注为调度类编号复用 SCHED_EXT=7。

### 冲突 11：IPC 消息头中 `version` 字段存在性

| 维度 | SSoT Layout C | 01-kernel.md §6.2 L419 & §10.1.2 L686 | 冲突等级 |
|------|-------------|--------------------------------------|----------|
| version 字段 | 明确不存在 | 存在（§6.2 描述含 version，§10.1.2 表含 version） | 🔴 CRITICAL |

**推荐统一标准**：删除 `version` 字段。SSoT Layout C 明确声明"无 version 与 type 字段"，版本信息由 magic 值承载（'ARE1' → 'ARE2' 表示协议版本升级）。

### 冲突 12：`AIRYMAX_SLICE_DFL` 单位

| 维度 | SSoT (§2.6) | 01-kernel.md (§10.1.1 L669) | 冲突等级 |
|------|-------------|---------------------------|----------|
| 值 | `20`（毫秒） | `20ms` | ✅ 一致 |
| 但 04-scheduling-flow.md | — | `20 * 1000000ULL`（纳秒） | 🟡 MEDIUM |

**推荐统一标准**：SSoT 中明确定义为 `AIRYMAX_SLICE_DFL_MS 20`，内核代码中使用纳秒单位 `AIRYMAX_SLICE_DFL_NS (20 * 1000000ULL)`。在 SSoT 中同时定义两种单位避免歧义。

---

## 冲突汇总统计

| 等级 | 数量 | 涉及项 |
|------|------|--------|
| 🔴 CRITICAL | 7 | task_desc 定义、IPC 消息头布局、struct_ops_state 枚举、vtime_t 类型、version 字段、syscall 预算、IPC 消息头字段名 |
| 🟡 HIGH | 4 | struct_ops 命名、capability 命名风格、typedef 违规、SLICE_DFL 单位 |
| 🟢 MEDIUM | 1 | SCHED_AGENT 标签 |

**根本原因分析**：01-kernel.md 作为 v2.0（2026-07-09）重写版本，在重写过程中自行定义了结构体布局，未与 SSoT（120-cross-project-code-sharing.md）同步。这违反了 IRON-9 v2 的"单一数据源"原则——[SC] 共享契约层的定义必须以 SSoT 为唯一权威来源。

---

# 第三部分：更深层次系统性审查（v0.7.0 新增发现）

## 3.1 架构层面新发现

### 发现 1：Capability 系统与 Syscall 的架构矛盾

**问题**：01-kernel.md §5 详细设计了 seL4 风格的 capability 系统（CTE/CNode/MDB/7 种 CNode 操作），但 01-syscalls.md 中仍保留了独立的 `capability_request`/`capability_revoke` syscall。

**矛盾**：seL4 的 capability 模型核心思想是 **capability invocation = IPC**。在 seL4 中，没有"申请 capability"的 syscall——capability 通过 CNode 操作（Mint/Copy/Move）在进程间传递。如果 agentrt-linux 已经实现了完整的 CNode 7 操作，那么 `capability_request` syscall 就是多余的——它应该是一个 IPC 消息，发送到拥有该 capability 的 server。

**建议**：删除 `agentrt_sys_capability_request` 和 `agentrt_sys_capability_revoke`，改为通过 `agentrt_sys_call`（capability invocation）实现。

### 发现 2：io_uring 与 syscall IPC 的双轨矛盾

**问题**：01-kernel.md §6.5 明确将 io_uring 作为 Endpoint 的物理载体，但 01-syscalls.md 仍定义了 `agentrt_sys_ipc_send`/`agentrt_sys_ipc_recv` 作为独立 syscall。

**矛盾**：如果 io_uring 已经是 IPC 的物理载体（SQE 提交 = 发送，CQE 完成 = 接收），那么额外的 `ipc_send`/`ipc_recv` syscall 就是多余的。io_uring 的设计目标就是"零 syscall 的 I/O"——通过共享内存的 SQ/CQ ring 避免陷入内核。

**建议**：删除 `agentrt_sys_ipc_send`/`agentrt_sys_ipc_recv`，IPC 数据面完全走 io_uring。仅保留 `agentrt_sys_send`/`agentrt_sys_recv` 作为同步 IPC 控制面（seL4 风格 rendezvous），用于需要同步语义的 capability invocation。

### 发现 3：kthread 注册与 CoreLoopThree 的耦合过紧

**问题**：01-cognition-flow.md 中 CoreLoopThree 的三个 kthread（cognition/execution/memory）通过 `agentrt_sys_clt_register_kthread` 注册。但 kthread 的创建和管理是内核机制，不应暴露为 syscall。

**建议**：kthread 的创建通过内核模块参数或 sysfs 配置，而非 syscall。`agentrt_sys_kthread_ctl` 仅用于运行时控制（绑定/解绑 capability）。

## 3.2 文档交叉引用新发现

### 发现 4：01-kernel.md §10.1.1 task_desc 表与 SSoT 完全不一致

01-kernel.md L673 的 `sched.h` 详细内容表列出了 11 个字段的 task_desc，但 SSoT 中 `sched.h` 只有 4 个字段。这不仅仅是"扩展视图"的问题——01-kernel.md 声称这是 `sched.h` 的内容，而 SSoT 中 `sched.h` 的内容完全不同。

### 发现 5：03-ipc-performance.md 头文件路径仍指向错误文件

该文档 L51 注释"定义于 `include/airymax/bpf_struct_ops.h`"，实际应为 `include/airymax/ipc.h`。虽然 L63 有 `#include <airymax/ipc.h>`，但 L51 的注释仍有误导性。这是 v0.6.0 P0-24 的残留问题。

### 发现 6：01-kernel.md §2.1 维度对比表中 struct_ops 状态命名不一致

L136: `airymax_struct_ops_state` vs `enum bpf_struct_ops_state`。同一行中 agentrt 侧和 agentrt-linux 侧使用了不同的类型名，但标注为 [SC] 共享——[SC] 共享意味着类型必须完全相同。

## 3.3 数值一致性新发现

### 发现 7：IPC 消息头 reserved 字段大小不一致

| 来源 | reserved 大小 | 
|------|-------------|
| SSoT Layout C | `reserved[84]`（84 字节） |
| 01-kernel.md §10.1.2 L686 | `reserved`（未标注大小） |

SSoT 中 128 字节布局：magic(4) + opcode(2) + flags(2) + trace_id(8) + timestamp_ns(8) + src_task(8) + dst_task(8) + payload_len(4) = 44 字节。128 - 44 = 84 字节 reserved。01-kernel.md 的字段布局不同，reserved 大小也不同。

### 发现 8：AIRYMAX_WEIGHT_MIN/MAX 仅存在于 01-kernel.md

SSoT sched.h 中没有定义 `AIRYMAX_WEIGHT_MIN/MAX`（1/10000），但 01-kernel.md §10.1.1 L670 列出了这些宏。如果它们是 [SC] 共享的，应该出现在 SSoT 中。

## 3.4 综合评分（v0.7.0）

| 维度 | v0.6.0 | v0.7.0 变化 | 说明 |
|------|--------|------------|------|
| D5 [SC] 完整性 | 50% | 40% ⬇ | 新增发现：01-kernel.md 与 SSoT 冲突比 v0.6.0 记录的更严重（12 项冲突 vs 原记录的 3 项） |
| D6 接口一致性 | 10% | 10% ➡ | 未修复 |
| D10 SSoT | 30% | 25% ⬇ | 新增发现：WEIGHT_MIN/MAX 缺失 |
| D17 数据流正确性 | 40% | 35% ⬇ | 新增发现：capability-syscall 架构矛盾、io_uring-syscall 双轨矛盾 |

**v0.7.0 综合评分**：**55/100（C+，维持）**——v0.6.0 的 19 项 P0 均未修复，新增 3 项架构层面发现和 5 项文档交叉引用/数值一致性发现。

---

# 第四部分：修复优先级建议

## 立即修复（M0 第 1 周，阻断 1.0.1 开发）

| 优先级 | 修复项 | 工时 | 涉及文件 |
|--------|--------|------|---------|
| 🔴 P0 | 统一 `airymax_task_desc` 为 SSoT 4 字段定义 | 4h | 01-kernel.md §10.1.1, 04-scheduling-flow.md |
| 🔴 P0 | 统一 `airymax_ipc_msg_hdr` 为 SSoT Layout C | 4h | 01-kernel.md §10.1.2, §6.2 |
| 🔴 P0 | 统一 `airymax_struct_ops_state` 枚举值 | 2h | 01-kernel.md §10.1.3 |
| 🔴 P0 | 统一 `airymax_vtime_t` 为 int32_t | 2h | 01-kernel.md §10.1.1 |
| 🔴 P0 | 删除 01-kernel.md 中 IPC 消息头的 version/type 字段 | 2h | 01-kernel.md §6.2, §10.1.2 |
| 🔴 P0 | 解决 syscall 预算矛盾（12 核心 + 20 预留 = 32 槽位） | 4h | 01-kernel.md §1.3, 01-syscalls.md §2.2 |
| 🔴 P0 | 删除 capability_request/revoke syscall（改为 IPC invocation） | 2h | 01-syscalls.md |
| 🔴 P0 | 删除 ipc_send/recv syscall（数据面走 io_uring） | 2h | 01-syscalls.md |

## 短期修复（M0 第 2-3 周）

| 优先级 | 修复项 | 工时 | 涉及文件 |
|--------|--------|------|---------|
| 🟡 P1 | 统一 struct_ops 命名（3 种 → 1 种） | 2h | 01-kernel.md |
| 🟡 P1 | 统一 capability 操作命名风格（PascalCase → snake_case） | 2h | 01-kernel.md §16.1 |
| 🟡 P1 | 消除 typedef 违规（agentrt_ipc_msg_hdr_t → struct airymax_ipc_msg_hdr） | 1h | 01-kernel.md §10.1 |
| 🟡 P1 | 修复 03-ipc-performance.md 头文件路径注释 | 1h | 03-ipc-performance.md L51 |
| 🟡 P1 | SSoT 中补充 WEIGHT_MIN/MAX 定义 | 1h | 120-cross-project-code-sharing.md §2.6 |
| 🟡 P1 | 统一 LSM 钩子数量为 250 | 2h | 01-kernel.md §10.1, 03-security.md |

---

## 附录：关键决策点（待用户确认）

1. **Syscall 预算**：是否采纳 12 核心 + 20 预留 = 32 槽位方案？这将替代当前的 120 槽位方案，使 syscall 数量与 seL4 极简哲学和 ≤ 20 目标一致。
2. **Capability invocation 模型**：是否采纳 `agentrt_sys_call` 作为统一的 capability invocation 入口，替代 task_submit/cancel/status/capability_request/revoke 等独立 syscall？
3. **IPC 数据面与控制面分离**：是否确认 IPC 数据面走 io_uring（零 syscall），控制面走 `agentrt_sys_send`/`agentrt_sys_recv`（同步 rendezvous）？
4. **01-kernel.md 修复策略**：是否以 SSoT 为唯一权威来源，将 01-kernel.md 中所有不一致的结构体定义、枚举值、字段名全部对齐到 SSoT？

---

> **报告结束** | agentrt-linux v0.7.0 深度综合审查报告 | 2026-07-11