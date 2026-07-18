Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 33 — 三大物理鸿沟的逐项审查

## "A-IPC 与 Linux 内核物理现实的硬碰撞"

> **文档性质**：对 A-IPC 与 Linux 6.6 内核物理机制交互的深度审查
> **审查日期**：2026-07-18
> **审查范围**：uring_lock 污染、MMU 页表开销、CFS 调度迁移

---

## §1 uring_lock 持有时间与快慢路径分离

### 1.1 问题精确复现

Linux 6.6 的 io_uring 调用路径：

```
io_uring_enter()
  → io_submit_sqes()
    → mutex_lock(&ctx->uring_lock)           ← 持有锁
      → io_issue_sqe()
        → io_uring_cmd_prep()
        → io_uring_cmd()                     ← airy_uring_cmd() 在此被调用
          → [当前设计: C-S0~C-S11 + kfifo_in + eventfd_signal + cqe_fill]
            ↑ 全部在 uring_lock 保护下执行
    → mutex_unlock(&ctx->uring_lock)          ← 释放锁
```

**当前设计在 uring_lock 内的执行链（按 30 号修复）**：

```
C-S0:    ring->frozen check              2ns
C-S1:    magic check                      2ns
C-S2:    opcode check                     2ns
C-S3:    payload_len check                2ns
C-S4:    size check                       2ns
C-S5:    CPU id check                     2ns
C-S6:    kfifo 满检查                     5ns
C-S7:    reclaim check                    2ns
C-S8:    context check                    2ns
C-S9:    Badge 校验 (3 READ_ONCE + 4 比较) 10ns
C-S10:   flag check                       2ns
C-S11:   preempt_disable                  1ns
kfifo_in:                                  50ns
eventfd_signal (无唤醒):                    20ns
eventfd_signal (有唤醒):                    1-5μs  ← 关键差异
io_uring_cqe_fill:                         20ns
preempt_enable:                            1ns
────────────────────────────────────────
锁内总时间（无唤醒）:                        ~127ns ← 可接受
锁内总时间（有唤醒）:                        ~1-5μs ← 不可接受
```

### 1.2 问题评估

**问题真实存在，但仅在接收方阻塞模式下才有影响。**

在 io_uring 的两种模式中：

| 模式 | 锁内时间 | 影响 |
|------|---------|------|
| SQPOLL（内核轮询线程） | ~127ns | 可忽略。SQPOLL 线程独占 ring，uring_lock 不争用 |
| IORING_SETUP_DEFER_TASKRUN（接收方阻塞） | ~1-5μs（eventfd 触发 wake_up） | **不可接受。其他 SQ 提交被阻塞 1-5μs** |

**当前设计的第 32 号审查 §4 已区分了这两种情况**，但未从 uring_lock 的角度分析。

### 1.3 修复方案

**利用 io_uring 的标准 NONBLOCK 模式进行快慢路径分离**：

```c
/* kernel/ipc/airy_uring_cmd.c */

static int airy_uring_cmd(struct io_uring_cmd *ioucmd, unsigned int issue_flags)
{
    struct airy_ipc_cmd *cmd = (struct airy_ipc_cmd *)ioucmd->cmd;
    int ret;

    /* Phase 1: Badge 校验 — 在锁内，一直执行 */
    ret = airy_ipc_validate(cmd);
    if (ret < 0)
        return ret;  /* 立即失败，不持有锁额外时间 */

    /* Phase 2: 数据投递 — 检查是否可以非阻塞完成 */
    if (issue_flags & IO_URING_F_NONBLOCK) {
        /*
         * 在 NONBLOCK 模式下（由 io_uring 在持有 uring_lock 时传入）:
         * - 如果 kfifo 有空位且接收方未阻塞 → 直接投递（~90ns 在锁内）
         * - 如果需要唤醒接收方 → 返回 -EAGAIN
         *   io_uring 会自动将操作重新排队到 io-wq 线程
         *   （io-wq 不持有 uring_lock，可以安全地执行 wake_up）
         */
        if (dst_is_active(cmd->dst_task) && kfifo_avail(cmd->dst_kfifo) > 0) {
            /* Fastpath: 锁内完成 ~90ns (kfifo_in + cqe_fill) */
            ret = airy_ipc_deliver_fast(cmd);
            if (ret >= 0)
                return ret;
        }
        return -EAGAIN;  /* 需要阻塞 → io-wq 接管 */
    }

    /*
     * 不在 NONBLOCK 模式下（已经在 io-wq 线程中）:
     * - 可以安全地执行 wake_up（io-wq 不持有 uring_lock）
     * - 可以安全地执行跨 CPU kfifo
     */
    return airy_ipc_deliver_full(cmd);
}

static int airy_ipc_validate(struct airy_ipc_cmd *cmd)
{
    /* C-S0 ~ C-S10 全部在锁内执行，~68ns，纯校验，零副作用 */
    if (cmd->ring->frozen)
        return -AIRY_ECAP_FROZEN;
    if (cmd->hdr->magic != AIRY_IPC_MAGIC)
        return -AIRY_EIPC_MAGIC;
    /* ... C-S1~C-S8 ... */
    if (!airy_cap_badge_ok(cmd->src_task, cmd->hdr->capability_badge,
                           cmd->required_perms))
        return -AIRY_ECAP_EPOCH; /* C-S9 在内联函数中 */
    /* ... C-S10 ... */
    return 0;
}

static int airy_ipc_deliver_fast(struct airy_ipc_cmd *cmd)
{
    /* kfifo_in + cqe_fill，无 wake_up。~90ns。在锁内。 */
    preempt_disable();
    kfifo_in(&cmd->dst->kfifo, cmd->hdr, AIRY_IPC_HDR_SIZE + cmd->hdr->payload_len);
    preempt_enable();
    io_uring_cmd_done(cmd->ioucmd, 0, 0);
    return 0;
}

static int airy_ipc_deliver_full(struct airy_ipc_cmd *cmd)
{
    /* 完整的投递路径: 可包含跨 CPU kfifo、wake_up 等阻塞操作 */
    /* 在 io-wq 中执行，不持有 uring_lock */
    int ret;

    ret = airy_ipc_deliver_internal(cmd);
    if (ret >= 0)
        eventfd_signal(cmd->dst->eventfd_ctx, 1);  /* 可包含 wake_up */
    io_uring_cmd_done(cmd->ioucmd, ret, 0);
    return 0;
}
```

### 1.4 修复后的延迟分解

```
SQPOLL 模式（内核轮询，接收方永不阻塞）:
  airy_ipc_validate():     ~68ns (锁内)
  airy_ipc_deliver_fast(): ~90ns (锁内, kfifo_in + cqe_fill)
  锁内总计:                 ~158ns
  端到端:                    ~158ns（接收方轮询消费）

IORING_SETUP_DEFER_TASKRUN（接收方阻塞）:
  airy_ipc_validate():     ~68ns (锁内)
  返回 -EAGAIN              → 释放 uring_lock
  调度到 io-wq:             ~500ns (io-wq 调度开销)
  airy_ipc_deliver_full():  ~100ns + wake_up(~1-5μs) (锁外)
  端到端:                    ~600ns ~5.5μs
```

### 1.5 结论

**问题真实存在。** 当前设计未区分 NONBLOCK 模式和阻塞模式。修复方案利用 io_uring 的内置 NONBLOCK 重试机制（返回 -EAGAIN → io-wq 接管），确保了：
- 锁内时间恒定为 ~68ns（仅校验，不投递）或 ~158ns（投递但不唤醒）
- 唤醒操作（wake_up，可能 1-5μs）发生在 io-wq 线程中，不持有 uring_lock
- 这是 io_uring 框架的标准设计模式（如 IORING_OP_READ/WRITE 的 NONBLOCK 路径）

**修复需要并入 A-IPC 实施计划。**

---

## §2 MMU 页表开销与共享物理内存池

### 2.1 问题精确复现

用户态 VFS_d 操作文件的路径：

```
当前路径:
  VFS_d 收到 IPC 请求 → 需要读取文件
  → openat()   → 内核 syscall → 构造 struct file
  → read(fd)   → 内核 syscall → 创建用户态缓冲区映射
     → get_user_pages_remote() → 遍历 VMA → 锁定页表 → 钉住物理页
     → 用户态 VFS_d 访问页 → 页表遍历（每次 L1/L2/L3 TLB 查找）
     → unpin_user_pages() → 解除页表锁定
  → IPC SEND 返回结果

get_user_pages_remote() 开销: ~1μs/页
4KB 数据: 1 页 × 1μs = 1μs
MMU TLB 查找: ~0.5ns（L1 TLB hit）或 ~5ns（L2 TLB hit）

IPC fastpath: ~158ns
MMU 开销: ~1μs
IPC 占比: 13.6%
MMU 占比: 86.4%
```

**用户的判断正确——MMU 开销确实淹没了 IPC 的优化。**

### 2.2 当前 A-IPC 已有的缓解

**registered buffer 机制已在设计中（IOURING_OP_URING_CMD + registered buffer）**：

```
io_uring 的 registered buffer 机制:
  VFS_d 启动时:
    io_uring_register_buffers(ring, iovecs, nr_iovecs)
      → 内核调用 get_user_pages() 一次性钉住所有注册的页面
      → 将物理页帧号记录在 io_mapped_ubuf[] 中

  VFS_d 运行时（每次 IPC）:
    io_uring_prep_uring_cmd(SQ, op=SEND, buf_index=5)
      → 内核通过 io_mapped_ubuf[5] 直接获取物理页帧号
      → 绕过 VMA 遍历
      → 绕过 get_user_pages_remote()
      → 零 MMU 开销
```

**registered buffer 已将 per-message 的 1μs 开销降为 per-registration 的一次性开销。**

### 2.3 但用户提出的 struct file / mm_struct 问题是真实的

**registered buffer 解决了"用户态缓冲区访问"的 MMU 开销。但 struct file 的共享仍然是一个独立的问题：**

```
场景: VFS_d 从 Agent A 收到 open(fd=5) → read() 请求
  VFS_d 需要操作 Agent A 的 fd 5
  但 fd 5 在 Agent A 的进程空间中，不在 VFS_d 的空间中

  传统做法: VFS_d 通过 pidfd_getfd() → 获取 Agent A 的 fd 5 的副本
    → 内核在 VFS_d 的 fd 表中创建一个新 fd
    → 新 fd 指向同一个 struct file（引用计数 +1）
    → VFS_d 通过自己的 fd 操作文件

  A-IPC 的做法: 使用 io_uring 的 fixed file 机制
    io_uring_register_files(ring, fds, nr_fds)
    → 内核将 fds 绑定到 ring 的 fixed file table
    → IPC 消息携带 fixed_fd_index 而非 fd 号
    → 接收方通过 IORING_OP_URING_CMD 直接操作 fixed file
```

**所以 struct file 的传递不是通过"复制 struct file"（这确实不可能），而是通过 io_uring 的 fixed file 机制间接引用。** 这不需要 IPC 传递 struct file——IPC 传递的只是一个索引号。

### 2.4 共享物理内存池方案评估

用户建议"预映射共享物理内存池（类 DPDK 大页），IPC 只传递 PFN"。

**评估：对于 0.1.1 不必要。** 理由：

1. **registered buffer 已等效于"共享物理内存池"**：io_uring_register_buffers() 已将用户态内存页钉住，后续 IPC 操作直接使用物理页帧号。IPC 的 registered buffer 和用户建议的"预映射大页"在效果上等价——都是预钉住物理页，避免 per-message 的 MMU 开销。

2. **struct file 问题已通过 fixed file 解决**：io_uring_register_files() + fixed_fd_index 允许 daemon 通过索引引用另一个进程的文件。

3. **mm_struct 传递不是 A-IPC 需要解决的问题**：微内核的 VFS 用户态化意味着 VFS_d 在自己的地址空间操作文件。VFS_d 永远不需要访问 Agent 的 mm_struct——它只需要 Agent 的 struct file（通过 fixed file 获取）。

### 2.5 结论

**问题真实存在，但 A-IPC 的 registered buffer + fixed file 机制已在设计层面解决了它。** MMU 开销通过 per-registration 的一次性 pinning 消除，struct file 通过 fixed file 索引传递。

**需要补充到文档中**：明确 registered buffer 是 A-IPC 的必要组件（不是可选优化），并在实施计划中标注 VFS_d/net_d 等 daemon 必须在启动时注册 buffers 和 files。

---

## §3 CFS 调度迁移与 C-S5 的碰撞

### 3.1 问题精确复现

```
C-S5: smp_processor_id() == dst_cpu

场景:
  cogn_d 绑定到 CPU 3
  CFS 负载均衡器决定将 cogn_d 迁移到 CPU 5
  
  所有在 CPU 3 上向 cogn_d 发送消息的 Agent:
    发送方 CPU = 3
    目标 CPU = 5（因为 cogn_d 已被迁移）
    C-S5: 3 ≠ 5 → SLOW_PATH → 跨 CPU kfifo → ~4μs

  如果 cogn_d 有 100 个活跃的发送 Agent:
    FAST_PATH 消息数: 0（全部走 SLOW_PATH）
    SLOW_PATH 消息数: 100K msg/s × 4μs = 400ms CPU/s
    vs FAST_PATH: 100K msg/s × 0.158μs = 15.8ms CPU/s
    吞吐退化: 25×
```

### 3.2 问题评估

**问题真实存在，但有明确的系统管理缓解措施，且是 C-S5 优化的已知代价。**

**C-S5 是一个优化条件，不是正确性条件。** 如果 C-S5 失败，消息仍然会被正确投递——只是走 SLOW_PATH（跨 CPU kfifo）。所以：
- C-S5 通过 → 158ns fastpath（优化效果）
- C-S5 失败 → ~4μs slowpath（基线性能）
- 不存在 "C-S5 失败导致消息丢失" 的问题

### 3.3 缓解措施

**1. CPU 亲和性绑定（推荐，对 0.1.1 足够）**：

```
systemd service unit for cogn_d:
  [Service]
  CPUAffinity=3          ← 绑定到 CPU 3
  AllowedCPUs=3          ← 禁用 CFS 迁移
```

通过 sched_setaffinity() 调用，将 cogn_d 锁定在单 CPU 上：
- CFS 不会将它迁移到其他 CPU
- C-S5 始终通过（发送方在 CPU 3，cogn_d 在 CPU 3）
- 需要同时配置 isolcpus 将该 CPU 从 CFS 负载均衡域中隔离

**2. 发送方 CPU 亲和性**：

对于高频发送 Agent，也绑定到同一个 CPU，确保 C-S5 通过。

**3. SLOW_PATH 阈值告警（补充措施）**：

```c
/* 在 airy_ipc_slowpath() 中 */
if (unlikely(cross_cpu_delivery)) {
    this_cpu_inc(airy_cross_cpu_stats);
    if (this_cpu_read(airy_cross_cpu_stats) > 100) {
        /* 每秒超过 100 次跨 CPU 投递 → 告警 */
        trace_airy_ipc_cross_cpu_threshold(src_task, dst_task);
    }
}
```

通过 ftrace 探针暴露 SLOW_PATH 频率，运维人员可以据此调整 CPU 绑定。

**4. 用户建议的"动态 IPI 拉回"方案评估**：

```
用户建议: 如果 SLOW_PATH 频率 > 阈值，发送 IPI 将 dst_task 拉回到 sender 的 CPU。

评估:
  - IPI 本身开销: ~1μs（跨核中断）
  - IPI 中断 dst_task，使其从其他 CPU 重新调度到 sender CPU
  - 调度延迟: ~5-20μs
  - 总拉回时间: ~6-21μs

  vs SLOW_PATH 延迟: ~4μs
  
  拉回开销 > SLOW_PATH 开销。只有在 dst_task 长时间留在错误 CPU 上
  （数秒级的持续迁移）时，拉回才有收益。一次性的迁移应该走 SLOW_PATH。
  
  结论: 对 0.1.1 不推荐。CPU 亲和性绑定是更简单、更可靠的方案。
```

### 3.4 结论

**问题真实存在，但 C-S5 是优化条件（不是正确性条件）。** CPU 亲和性绑定（sched_setaffinity + isolcpus）是标准方案。需要在文档中明确标注：
- 高频 IPC 的 daemon 必须绑定到固定 CPU
- 如果未绑定，C-S5 可能失败，系统以 ~4μs 延迟工作（仍满足 <10μs SLO）
- 动态 IPI 拉回对 0.1.1 不必要

---

## §4 汇总

| # | 问题 | 严重度 | 当前状态 | 修复 |
|---|------|:---:|:---:|------|
| 1 | uring_lock 持有 wake_up 导致锁争用 | 🔴 **P0** | 存在 | NONBLOCK 模式分离 + io-wq 接管 |
| 2 | MMU 页表开销淹没 IPC 延迟 | 🟡 **已缓解** | registered buffer + fixed file 已解决 | 需文档明确注册是强制要求 |
| 3 | CFS 迁移使 C-S5 失效，吞吐退化 | 🟠 **已知代价** | C-S5 是优化，不是正确性条件 | CPU 亲和性绑定 + SLOW_PATH 阈值告警 |

**仅 uring_lock 问题需要代码级修复（NONBLOCK 模式 + io-wq 重试）。MMU 问题已由 registered buffer 解决，CFS 问题通过 CPU 亲和性绑定缓解。**

---

## §5 对实施计划的影响

| Phase | 修改 |
|-------|------|
| Phase 1（Badge + Epoch） | 增加：airy_uring_cmd() 的 NONBLOCK 模式处理 |
| Phase 2（消除控制面 IPC） | 不变 |
| Phase 3（Capability 模型更新） | 不变 |
| Phase 4（总纲更新） | 增加：引用 io_uring registered buffer 为强制要求 |
| Phase 5（验证） | 增加：uring_lock 争用压力测试；CFS 迁移 + SLOW_PATH 退化测试 |

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. | 物理鸿沟审查 | v1.0 | 2026-07-18
