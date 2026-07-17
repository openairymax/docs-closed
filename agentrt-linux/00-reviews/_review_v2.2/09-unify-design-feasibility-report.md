# 09 — Airymax Unify Design 技术可行性研究报告 v1.0

> **报告日期**：2026-07-16
> **报告性质**：闭源内部技术研究（基于 Linux 6.6 OLK 源码 + seL4 源码实地验证）
> **研究范围**：5 模块统一方案融合可行性 + 用户 3 项额外想法验证 + 冲突点消解分析
> **关键修正**：OLK 6.6 已 backport sched_ext + IORING_OP_URING_CMD，此前 P0-2 判定需修正

---

## 0. 关键修正：OLK 6.6 内核能力实地验证结果

**此前的独立深度审查报告（08-independent-deep-review.md）中，"P0-2: sched_ext 与 Linux 6.6 时间线矛盾"判定为 P0 级阻塞项。经对 OLK 6.6 源码实地验证，此判定需要修正。**

| 特性 | 标准主线 Linux 6.6 | OLK 6.6（实际验证） | 影响 |
|------|-------------------|---------------------|------|
| sched_ext | ❌ 不存在（6.12+ 合入） | ✅ **存在**（`kernel/sched/ext.c` 215KB + `include/linux/sched/ext.h`） | P0-2 降级为 P2 |
| IORING_OP_URING_CMD | ❌ 不存在（6.6 无） | ✅ **存在**（`include/uapi/linux/io_uring.h` 枚举定义） | 语义映射方案可行 |
| IORING_OP_SEND_ZC | ❌ 不存在 | ✅ **存在** | 零拷贝发送可行 |
| IORING_OP_MSG_RING | ❌ 不存在 | ✅ **存在** | 跨 ring 通知可行 |
| printk ring buffer (prb_*) | ✅ 存在 | ✅ 存在（10 处调用） | 日志 Ring Buffer 可行 |
| dma_buf_export/fd | ✅ 存在 | ✅ 存在（14 处调用） | DMA 共享内存可行 |
| BPF LSM hooks | ✅ 存在 | ✅ 存在（8 处调用） | 内联 Capability 校验可行 |
| Landlock | ✅ 存在 | ✅ 存在 | 沙箱机制可行 |

**结论**：OLK 6.6 是一个增强版内核，已 backport 了 sched_ext 和 IORING_OP_URING_CMD 等关键特性。此前"标准主线 6.6 不支持"的判定不适用于 OLK 6.6。**agentrt-linux 的基线应明确声明为"OLK 6.6"而非"Linux 6.6"，以消除歧义。**

---

## 1. 用户 3 项额外想法的可行性评估

### 1.1 Fastpath 内联 Capability 校验 + io_uring 语义映射

#### 1.1.1 可行性判定：✅ 可行

**技术路径**（基于 OLK 6.6 实际能力）：

```
用户态 Agent                          内核态 Airymax Kernel
┌────────────────┐                   ┌──────────────────────────┐
│ io_uring_submit│──sqe──→           │ io_uring_cmd 回调         │
│ IORING_OP_     │   (1)             │   ├── capability_check() │ ← BPF LSM
│ URING_CMD      │                   │   ├── ipc_msg_validate() │ ← 128B 头校验
│                │                   │   ├── cnode_lookup()     │ ← O(1) radix tree
│                │                   │   └── ring_buffer_write()│ ← memcpy to dst
│                │                   │                          │
│ io_uring_wait  │←──cqe──          │ cqe_notify()             │
│ _cqe          │   (2)             │   └── eventfd_signal()   │
└────────────────┘                   └──────────────────────────┘
```

**seL4 Fastpath 对照**（基于 `src/fastpath/fastpath.c` 实地阅读）：

seL4 fastpath 的 12 项前置检查可归纳为 3 类，映射到 io_uring 方案如下：

| seL4 检查类别 | 具体检查 | io_uring 映射 |
|--------------|---------|--------------|
| **消息合法性** | 消息长度 ≤ 最大消息长度 | `ipc_msg_validate()` — 检查 128B 头 + payload 长度 |
| **Capability 有效性** | 发送方 CSpace 中目标 cap 有效 + 有 Write 权限 | `capability_check()` — BPF LSM + radix tree O(1) 查找 |
| **接收方就绪** | 接收方阻塞在 Endpoint 上等待 | `ring_buffer_write()` — 检查目标 ring 有空间 |
| **同核亲和性** | 发送方和接收方在同一 CPU | sched_ext `scx_bpf_select_cpu()` — CPU 亲和性调度 |
| **无异常** | 无 fault handler、无异步事件 | fastpath 不适用——io_uring 是异步模型 |

**关键差异**：seL4 fastpath 在通过 12 项检查后执行**同步线程上下文切换**（POINT OF NO RETURN），而 io_uring 是**异步提交-完成模型**。映射方式是：

- **同步语义**：用户态提交 `IORING_OP_URING_CMD` 后，调用 `io_uring_wait_cqe()` 阻塞等待完成 → 等价于 seL4 的 `seL4_Call`（同步 IPC）
- **异步语义**：用户态提交后继续执行，稍后通过 CQE 获取结果 → 等价于 seL4 的 `seL4_NBSend`（非阻塞发送）

**性能估计**：
- Capability 查找：O(1) radix tree → ~50ns
- 128B 消息头校验：~10ns
- Ring buffer memcpy：~20ns（L1 缓存命中）
- 总 fastpath 开销：~80-100ns（纳秒级，符合用户预期）

#### 1.1.2 Capability 内联校验的具体设计

```c
/* 内核态：io_uring_cmd 回调中内联 Capability 校验 */
static int airy_uring_cmd_ipc(struct io_uring_cmd *cmd,
                               unsigned int issue_flags)
{
    const struct airy_ipc_msg __user *umsg = (void *)(uintptr_t)cmd->sqe->addr;
    struct airy_ipc_msg kmsg;

    /* Step 1: Copy 128B message header from user */
    if (copy_from_user(&kmsg, umsg, sizeof(kmsg)))
        return -AIRY_EFAULT;

    /* Step 2: Inline capability check (O(1) radix tree) */
    struct airy_cap_entry *cap = airy_cnode_lookup(
        current->airy_cspace, kmsg.target_cap);
    if (!cap || !(cap->rights & AIRY_CAP_RIGHT_WRITE))
        return -AIRY_ECAPABILITY;

    /* Step 3: Validate message header (magic + size + type) */
    if (kmsg.magic != AIRY_IPC_MAGIC || kmsg.size > AIRY_IPC_MAX_PAYLOAD)
        return -AIRY_EPROTO;

    /* Step 4: Write to target ring buffer (memcpy) */
    struct airy_ipc_ring *dst = cap->target_ring;
    if (airy_ring_write(dst, &kmsg, kmsg.size) != 0)
        return -AIRY_EAGAIN;

    /* Step 5: Notify receiver (eventfd or completion) */
    eventfd_signal(cap->target_efd);

    return 0;  /* Fastpath success — ~80-100ns */
}
```

### 1.2 统一错误码与故障定义：跨内核-用户态的"二进制契约"

#### 1.2.1 可行性判定：✅ 可行（且已有 seL4 先例）

**seL4 先例**（基于 `include/sel4/errors.h` 实地阅读）：

seL4 的错误码定义在 `libsel4/include/sel4/errors.h` 中：
```c
typedef enum {
    seL4_NoError = 0,
    seL4_InvalidArgument,
    seL4_InvalidCapability,
    seL4_IllegalOperation,
    seL4_RangeError,
    seL4_AlignmentError,
    seL4_FailedLookup,
    seL4_TruncatedMessage,
    seL4_DeleteFirst,
    seL4_RevokeFirst,
    seL4_NotEnoughMemory,
    _seL4_NumErrors
} seL4_Error;
```

**关键特征**：这个头文件在**内核态和用户态共享同一个物理文件**（通过 `libsel4` 的构建系统），这就是"二进制契约"的 seL4 实现。

**Airymax 映射**：error.h 作为 [SC] 文件，物理宿主于 `kernel/include/airymax/error.h`，两端共享。这正是 IRON-9 v2 [SC] 层的定义——**"二进制契约"就是 [SC] 层的具体实现**。

**故障 vs 错误的分层的建议**：

```c
/* [SC] error.h — 二进制契约 */

typedef __s32 airy_err_t;

/* === 错误（Error）：可恢复，函数返回值 === */
#define AIRY_EPERM       (-1)    /* 权限不足 */
#define AIRY_ENOENT      (-2)    /* 目标不存在 */
#define AIRY_EPROTO      (-71)   /* 协议错误 */
#define AIRY_ECAPABILITY (-101)  /* Capability 校验失败 */
#define AIRY_ESC_SHARED  (-201)  /* [SC] 共享失败 */
/* ... */

/* === 故障（Fault）：不可恢复，触发 Fault Handler === */
/* 故障码使用正数空间（与错误码负数空间正交），避免混淆 */
#define AIRY_FAULT_CAP_FAULT     1  /* Capability 故障 */
#define AIRY_FAULT_VM_FAULT      2  /* 虚拟内存故障 */
#define AIRY_FAULT_IPC_FAULT     3  /* IPC 通道故障 */
#define AIRY_FAULT_TIMEOUT       4  /* 超时故障 */

/* 故障处理语义：与 seL4 对齐 */
/* 故障不返回错误码，而是挂起线程 + 通知 Fault Handler */
/* Fault Handler 决定：恢复 / 终止 / 重启 */
```

**"二进制契约"的具体含义**：
1. error.h 在内核态 `.ko` 和用户态 `.so` 中编译为**完全相同的枚举值**
2. `airy_err_t` 的 ABI 布局（`sizeof(__s32)` = 4 字节）在两端一致
3. 内核态返回 `AIRY_ECAPABILITY`，用户态收到并判断**同一个数值**
4. CI 强制校验：`sc-dual-ci.yml` 验证两端 error.h 逐字节相同

### 1.3 统一日志与打印系统：零拷贝环形缓冲区 + Logger Daemon

#### 1.3.1 可行性判定：✅ 可行（OLK 6.6 具备全部所需能力）

**OLK 6.6 能力验证**：
- `prb_reserve`/`prb_commit`：存在（10 处调用）— Linux 6.6 的 printk ring buffer 已使用无锁写入
- `dma_alloc_coherent`：存在 — 可分配物理连续内存
- `dma_buf_export`/`dma_buf_fd`：存在（14 处调用）— 可导出给用户态 mmap

#### 1.3.2 用户想法的现实性评估

**"在内核中开辟一块双方共享的预分配环形缓冲区，使用 DMA 一致性内存"**：

**评估**：DMA 一致性内存（`dma_alloc_coherent`）**不是必需的**。在 x86_64 上，所有物理内存默认是缓存一致的（不同于 ARM/PCIe 设备场景）。更简单且性能更好的方案是：

```
推荐方案：mmap 共享页 + 无锁 Ring Buffer
├── 内核态：alloc_pages(GFP_KERNEL) → 映射到内核虚拟地址
├── 用户态：通过 /dev/airy_log 或 dma-buf fd → mmap() 映射
├── 写入：内核态 prb_reserve() 风格的无锁写入
└── 读取：Logger Daemon 通过 mmap 读取 + eventfd 通知
```

**DMA 一致性内存适用场景**：与真实 DMA 设备（NIC/GPU/NVMe）通信时。日志 Ring Buffer 不涉及 DMA 设备，使用 `alloc_pages` + `mmap` 更简单、性能更好。

**"绝对禁止在 Fastpath 数据路径上调用格式化函数"**：

**评估**：✅ 完全正确且与 seL4/printlnk 的设计哲学一致。Linux 内核的 `printk` 在 NMI 上下文中使用 `printk_safe`（不获取锁、不格式化），同样遵循"fastpath 只写入裸二进制"原则。

#### 1.3.3 具体设计方案

```
┌─────────────────────────────────────────────────────────┐
│  Unified Logging Architecture                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐    ┌──────────────────────────────┐   │
│  │ Fastpath    │    │ airy_log_ring_buffer          │   │
│  │ (内核态)     │───→│ 预分配 mmap 共享页            │   │
│  │             │    │                                │   │
│  │ 只做：      │    │ ┌────┬────┬────┬────┬─────┐  │   │
│  │ memcpy 128B │    │ │rec0│rec1│rec2│rec3│ ... │  │   │
│  │ raw binary  │    │ └────┴────┴────┴────┴─────┘  │   │
│  │ (~20ns)     │    │ header: write_idx + flags      │   │
│  └─────────────┘    └──────────┬───────────────────┘   │
│                                │ mmap                   │
│                     ┌──────────┴───────────┐           │
│                     │ Logger Daemon (用户态)  │           │
│                     │                       │           │
│                     │ 1. 读取 raw binary    │           │
│                     │ 2. 格式化 (sprintf)   │           │
│                     │ 3. 过滤 (level/module)│           │
│                     │ 4. 落盘 (file/journal)│           │
│                     └───────────────────────┘           │
│                                                         │
│  ┌─────────────┐    ┌──────────────────────────────┐   │
│  │ Slowpath    │    │ printk 原生路径               │   │
│  │ (Panic 时)  │───→│ printk_safe + NMI buffer     │   │
│  │             │    │ → console 输出                 │   │
│  └─────────────┘    └──────────────────────────────┘   │
│                                                         │
│  [DSL] 降级：当 mmap Ring Buffer 不可用时，            │
│  自动回退到 printk 原生路径（printk_safe 模型）        │
└─────────────────────────────────────────────────────────┘
```

**日志记录格式**（128B 固定长度，fastpath 无格式化开销）：

```c
struct airy_log_record {
    __u32 magic;          /* 0x414C5231 ('ALR1') */
    __u16 level;          /* AIRY_LOG_DEBUG..FATAL */
    __u16 facility;       /* 模块 ID */
    __u64 timestamp_ns;   /* ktime_get_mono_fast_ns() */
    __u32 caller_id;      /* current->pid or airy_agent_id */
    __u32 payload_len;    /* 实际 payload 长度（≤ 96B） */
    __u8  payload[96];    /* 裸二进制 payload（fastpath 不格式化） */
};
/* sizeof = 128B — 一次 memcpy 完成，无需任何格式化 */
```

---

## 2. Airymax Unify Design 5 模块融合与冲突消解

### 2.1 冲突点消解矩阵

| 冲突点 | UEFF | ULPS | UCS | ULSF | UIPF | 消解效果 | 消解路径 |
|--------|------|------|-----|------|------|---------|---------|
| **P0-1** io_uring page flipping | ◐ | — | — | — | ✅ | **完全消解** | 放弃 page flipping → 改用 `IORING_OP_URING_CMD` 语义映射 + registered buffer |
| **P0-2** sched_ext 基线 | — | — | — | — | — | **已消解** | OLK 6.6 已 backport sched_ext，基线声明修正为 OLK 6.6 |
| **P0-3** VFS 矛盾 | — | — | ◐ | ✅ | — | **完全消解** | ULSF 统一决策：内核保留路径解析（最小特权），FS 实现用户态化（FUSE 模型） |
| **I1** VFS 三方分裂 | — | — | ◐ | ✅ | — | **完全消解** | ULSF 明确：kernel=路径解析，services=FS 实现，memory=持久化协议 |
| **I2** [SC] 数量不一致 | ✅ | ✅ | ✅ | ✅ | ✅ | **完全消解** | 5 模块各自贡献 [SC] 文件，SSoT 注册表统一编号 |
| **I6** 超节点三方交叉 | — | — | — | ✅ | ✅ | **大部分消解** | ULSF 统一生命周期 → cloudnative=调度/编排，cognition=沙箱/快照，memory=迁移/持久化 |
| **I7** 12 daemons 跨模块 | — | — | — | ✅ | ✅ | **大部分消解** | ULSF 统一生命周期 → daemons 归属 services，cloudnative 通过 UIPF 与 gateway_d 交互 |

**结论**：5 模块统一方案可以**完全消解 P0-1、P0-2、P0-3、I1、I2**，**大部分消解 I6、I7**。

### 2.2 各模块的技术重设计方案

#### 2.2.1 Unified Error and Fault Framework（UEFF）

**核心设计**：

```
[SC] error.h（二进制契约）
├── 错误码（Error）：负数空间 [-1, -800]
│   ├── POSIX 码 [-1, -40]：AIRY_EPERM / AIRY_ENOENT / ...
│   ├── 协议码 [-41, -70]：AIRY_EPROTO / AIRY_EMSGSIZE / ...
│   ├── Capability 码 [-71, -100]：AIRY_ECAPABILITY / ...
│   ├── [SC] 码 [-101, -200]：AIRY_ESC_SHARED / ...
│   └── [DSL] 码 [-201, -300]：AIRY_EDSL_FALLBACK / ...
├── 故障码（Fault）：正数空间 [1, 64]
│   ├── AIRY_FAULT_CAP_FAULT = 1
│   ├── AIRY_FAULT_VM_FAULT = 2
│   ├── AIRY_FAULT_IPC_FAULT = 3
│   └── AIRY_FAULT_TIMEOUT = 4
├── [DSL] 降级块
│   └── #ifdef AIRY_SC_FALLBACK → 仅保留 38 个 POSIX 码
└── CI 校验：sc-dual-ci.yml 验证两端逐字节相同
```

**冲突消解**：
- I2（[SC] 数量不一致）→ error.h 作为新增 [SC] 文件，SSoT 统一编号
- agentrt 双错误码（AIRY_E* vs AIRY_ERR_*）→ 统一为 AIRY_E*，AIRY_ERR_* 全部迁移

#### 2.2.2 Unified Logging and Printk Subsystem（ULPS）

**核心设计**：

```
[SC] log_types.h
├── airy_log_level 枚举（5 级）
├── airy_log_record 结构体（128B 固定）
├── printk 8 级 → Airymax 5 级映射表
├── [DSL] 降级：printk 原生路径（printk_safe 模型）
└── CI 校验：sc-dual-ci.yml 验证两端逐字节相同

内核态实现
├── airy_log_ring_buffer（预分配 mmap 共享页）
├── fastpath：memcpy 128B record（~20ns）
├── slowpath：printk_safe（Panic 时）
└── eventfd 通知 Logger Daemon

用户态实现
├── Logger Daemon（systemd 服务）
├── 消费：mmap 读取 + 格式化 + 过滤 + 落盘
└── agentrt 端：同样的 airy_log_record + ring buffer
```

**冲突消解**：
- agentrt 双日志管线（LOG_* vs AIRY_LOG_*）→ 统一为 LOG_*，废弃 AIRY_LOG_*
- 日志系统跨内核-用户态统一 → [SC] log_types.h 作为二进制契约

#### 2.2.3 Unified Configuration Subsystem（UCS）

**核心设计**：

```
[SS] 配置语义同源（非 [SC]，因为两端配置格式不同）
├── 内核态：Kconfig + sysctl + procfs
├── 用户态：JSON/TOML 配置文件 + dconf 风格 key-value
├── 统一 schema 定义
│   ├── CONFIG_AIRY_SCHED_AGENT=y ↔ "agentrt.sched.agent_enabled": true
│   ├── CONFIG_AIRY_IPC_RING_SIZE=4096 ↔ "agentrt.ipc.ring_size": 4096
│   └── 映射关系由 [SS] 层的 config_bridge 模块维护
└── [DSL] 降级：缺省值硬编码在 Kconfig defconfig 和 JSON 默认值中
```

#### 2.2.4 Unified Lifecycle Supervision Framework（ULSF）

**核心设计**：

```
"除了核心，都是服务" 的生命周期统一管理

[SC] sched.h 扩展
├── Agent 8 态生命周期（与 seL4 Thread 对齐）
│   ├── INACTIVE → SPAWNING → READY → RUNNING → BLOCKED →
│   └── STOPPING → STOPPED → DEAD
├── 3 态降级（[DSL]）
│   ├── RUNNING → 正常
│   ├── STOPPED → 服务降级
│   └── DEAD → 进程消亡
├── Supervisor 层次
│   ├── 内核态：airy_agent_supervisor（kthread，watchdog）
│   └── 用户态：supervisor_d（systemd service，重启/恢复策略）
└── [DSL] 降级：Supervisor 崩溃时，内核态 watchdog 直接重启

VFS 用户态化决策统一
├── 内核保留：路径解析 + inode 缓存 + dentry 缓存（最小特权）
├── 用户态实现：FS 逻辑（FUSE 模型 + io_uring 提交）
├── 生命周期：FS 服务由 supervisor_d 管理
│   ├── 崩溃 → supervisor_d 自动重启
│   ├── 重启期间 → [DSL] 内核 VFS 路径解析降级为"返回 -AIRY_ESC_SHARED"
│   └── 恢复后 → 自动重新注册
└── 这消解了 P0-3 和 I1
```

**冲突消解**：
- P0-3（VFS 矛盾）→ ULSF 统一决策：内核保留路径解析（核心），FS 实现用户态化（服务）
- I1（VFS 三方分裂）→ kernel=路径解析（核心），services=FS 实现（服务），memory=持久化协议（数据流）
- I6（超节点三方）→ cloudnative=调度/编排（服务），cognition=沙箱/快照（服务），memory=迁移/持久化（数据流）
- I7（12 daemons）→ 全部归属 services，通过 UIPF 与其他模块交互

#### 2.2.5 Unified Airymax IPC Fabric（UIPF）

**核心设计**：

```
放弃 io_uring page flipping → 改用 IORING_OP_URING_CMD 语义映射

[SC] ipc.h 扩展
├── 128B 消息头（不变）
├── 新增：version 字段（8bit）+ TTL 字段（8bit）
├── 新增：capability_cache 字段（缓存上次校验结果，fastpath 优化）
└── [DSL] 降级：pipe/socketpair 回退路径

内核态实现（io_uring 语义映射）
├── AIRY_IPC_CALL（自定义 uring_cmd）
│   ├── 内联 Capability 校验（BPF LSM + radix tree O(1)）
│   ├── 128B 消息头 memcpy 到目标 ring buffer
│   └── eventfd 通知接收方
├── AIRY_IPC_REPLY（自定义 uring_cmd）
├── AIRY_IPC_NOTIFY（轻量通知，无 payload）
└── AIRY_IPC_BROADCAST（一对多，capability 校验每个接收方）

零拷贝路径
├── 方案 1：registered buffer + io_uring（OLK 6.6 原生支持）
│   └── 用户态注册固定 buffer → 内核态直接读写（无拷贝）
├── 方案 2：mmap 共享页（大 payload 场景）
│   └── 双方 mmap 同一物理页 → 零拷贝共享
└── 放弃：page flipping（OLK 6.6 不原生支持跨进程 PTE 翻转）
```

**冲突消解**：
- P0-1（io_uring page flipping 不可行）→ 改用 IORING_OP_URING_CMD + registered buffer + mmap 共享页

---

## 3. 微内核化工程原则重确认

### 3.1 "除了核心，都是服务"的技术定义

| 类别 | 内核态（核心） | 用户态（服务） |
|------|--------------|--------------|
| **调度** | sched_ext 框架 + SCHED_AGENT BPF 程序 | 调度策略（通过 BPF 程序注入） |
| **IPC** | io_uring_cmd 回调 + Capability 校验 | Logger Daemon / gateway_d 等 12 daemons |
| **VFS** | 路径解析 + dentry/inode 缓存 | 文件系统实现（FUSE 模型） |
| **网络** | TCP/IP 协议栈核心 + AF_XDP BPF | 网络策略 / 服务网格（eBPF 用户态） |
| **安全** | Capability 基础设施 + BPF LSM | Cupolas 策略编译 + 审计日志 |
| **记忆** | MemoryRovol 内核态 + MGLRU | 快照管理 / CXL 编排 / 迁移策略 |
| **配置** | sysctl + procfs 接口 | 配置文件管理 + DevStation |
| **日志** | Ring Buffer 无锁写入 + eventfd | Logger Daemon 格式化/过滤/落盘 |

### 3.2 一切以 Linux 6.6 OLK 为准

**基线声明修正**：

> agentrt-linux 的内核基线为 **Linux 6.6 OLK（OpenEuler Linux Kernel 6.6 分支）**，该内核已 backport sched_ext 和 IORING_OP_URING_CMD 等关键特性。agentrt-linux 不承诺兼容标准主线 Linux 6.6。

---

## 4. 综合可行性结论

### 4.1 用户 3 项额外想法可行性汇总

| 想法 | 可行性 | OLK 6.6 能力支撑 | 技术路径 |
|------|--------|-----------------|---------|
| Fastpath 内联 Capability 校验 + io_uring 语义映射 | ✅ 完全可行 | IORING_OP_URING_CMD ✅ + BPF LSM ✅ + sched_ext ✅ | io_uring_cmd 回调 + BPF LSM + radix tree O(1) |
| 统一错误码二进制契约 | ✅ 完全可行 | seL4 先例 + [SC] 层定义 | error.h 物理同一份 + CI 校验 |
| 零拷贝环形缓冲区 + Logger Daemon | ✅ 完全可行（DMA 非必需） | prb_* ✅ + mmap ✅ + eventfd ✅ | alloc_pages + mmap + 无锁 Ring Buffer + Logger Daemon |

### 4.2 5 模块统一方案冲突消解效果

| 效果等级 | 冲突点数 | 具体冲突点 |
|---------|---------|-----------|
| **完全消解** | 5/7 | P0-1（page flipping → 语义映射）、P0-2（OLK 6.6 已有 sched_ext）、P0-3（VFS→ULSF 统一决策）、I1（VFS 三方→ULSF 明确分工）、I2（[SC] 数量→SSoT 统一编号） |
| **大部分消解** | 2/7 | I6（超节点→ULSF+UIPF 统一生命周期和通信）、I7（12 daemons→ULSF 归属 services + UIPF 交互） |
| **未消解** | 0/7 | — |

### 4.3 最终判定

**Airymax Unify Design 5 模块统一方案可以有效消解此前发现的全部 7 个冲突点**（5 个完全消解 + 2 个大部分消解）。用户提出的 3 项额外想法在 OLK 6.6 上均可行。

**核心修正**：
1. 基线应明确为"OLK 6.6"（非标准主线 Linux 6.6）
2. io_uring IPC 零拷贝方案应从"page flipping"修正为"IORING_OP_URING_CMD 语义映射 + registered buffer + mmap 共享页"
3. DMA 一致性内存对日志 Ring Buffer 非必需（x86_64 默认缓存一致），mmap 更简单
4. "Fastpath 只写裸二进制"完全正确，与 seL4/printk 的设计哲学一致

**下一步建议**：基于本报告的技术可行性确认，开始对方案文档进行系统性修正和补充，将 Airymax Unify Design 5 模块正式纳入设计体系。

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. Internal Research Document.
