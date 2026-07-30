SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 01 — 调度器深度对比：openEuler / seL4 MCS vs Airymax sched_tac

> **文档定位**：v3.6 深度对比研究 · 调度器子域
> **对比基准**：openEuler kernel-OLK-6.6 · seL4-master · Airymax agentrt-linux
> **最后更新**：2026-07-30
> **方法论**：逐字节阅读参考项目源码 + Airymax 现状代码，所有引用均标注文件路径与行号

---

## 1. 研究范围与对比维度

| 维度 | openEuler OLK-6.6 | seL4-master | Airymax sched_tac |
|------|-------------------|-------------|-------------------|
| 调度类多态 | sched_class 5 类 + ext | 固定优先级 + MCS SC | 复用 Linux 4 类 |
| 实时模型 | SCHED_DEADLINE CBS | MCS budget/refill | SCHED_DEADLINE + MCS 映射 |
| 公平调度 | EEVDF（KABI_REPLACE 改造） | N/A | 复用 EEVDF |
| 带宽治理 | dl_bw 准入 + rt_bandwidth | SC budget + refill_sufficient | 未实现准入 |
| CPU 选择 | cpudl + sched_domain | 单核/集群亲和 | 复用 Linux cpuset |
| 可扩展性 | BPF_SCHED + QOS_SCHED | N/A | 纯 C，禁 sched_ext |

---

## 2. openEuler 调度类多态架构（sched_class）

### 2.1 sched_class hook 全集

openEuler 在 [sched.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/sched.h) L2573-2653 定义了完整的 `struct sched_class`，包含 30+ 个 hook：

- 核心生命周期：`enqueue_task` / `dequeue_task` / `pick_next_task` / `put_prev_task` / `set_next_task`
- 抢占：`wakeup_preempt` / `yield_task` / `yield_to_task`
- 负载均衡：`balance` / `select_task_rq` / `migrate_task_rq`
- 事件回调：`task_tick` / `task_fork` / `task_dead` / `switched_from` / `switched_to` / `prio_changed`
- 节流：`task_is_throttled` / `reweight_task`
- 扩展：`task_change_group` / `switching_to` / `switch_class`

L2689-2692 的 `DEFINE_SCHED_CLASS(name)` 宏通过 `__aligned + __section` 实现链接器排序，L2695-2703 定义 6 个调度类实例（stop/dl/rt/fair/idle/ext）。

### 2.2 调度类遍历宏

[sched.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/sched.h) L2709-2733 提供 `next_active_class` / `for_class_range` / `for_active_class_range` 遍历宏，允许在不感知具体类的前提下遍历活跃调度类。

### 2.3 Airymax 现状对比

Airymax **不新增调度类**，而是通过 [stc_dispatch.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_dispatch.c) L26-40 的 `stc_policy_to_linux()` 将 4 种 sched_tac 策略映射到原生 Linux 调度类：

```
AIRY_SCHED_POLICY_DEADLINE   → SCHED_DEADLINE   (L29-30)
AIRY_SCHED_POLICY_FIFO       → SCHED_FIFO        (L31-32)
AIRY_SCHED_POLICY_EEVDF      → SCHED_NORMAL      (L33-34)
AIRY_SCHED_POLICY_BESTEFFORT → SCHED_BATCH       (L35-36)
```

[stc_policy.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_policy.h) L23-29 定义枚举别名，数值与 [sched.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/sched.h) L97-100 的 `AIRY_SCHED_POLICY_*` 宏一致。

**评价**：Airymax 的"映射而非新增"策略符合 ALK（只新增文件、不改主线）原则，避免了 openEuler 那样对 sched_class 的侵入式改造。但代价是**无法实现调度类级别的 hook 注入**（如 `task_is_throttled`、`switching_to`），所有调度行为受限于原生类的语义。

---

## 3. SCHED_DEADLINE / CBS 与 dl_bw 准入

### 3.1 openEuler DL 实现证据

[sched.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/sched.h) 关键定义：

- L182：`#define DL_SCALE 10` — SCHED_DEADLINE 内部数学精度（略高于 1us）
- L187：`#define RUNTIME_INF ((u64)~0ULL)` — runtime==period 表示无限制
- L287-294：`dl_entity_is_special()` — SUGOV 特殊优先级判定
- L299-304：`dl_entity_preempt()` — deadline 严格早于则抢占
- L350：`struct dl_bw` — DL 带宽准入控制结构
- L365：`dl_bw_check_overflow` — 带宽溢出检查（准入时调用）
- L977/L1096/L1100：`struct dl_bw dl_bw` 挂载于 root_domain，含检查标志

openEuler 的 `deadline.c` 实现完整 CBS（Constant Bandwidth Server）：每个 sched_dl_entity 拥有独立的 runtime/dl_runtime/dl_period，通过 hrtimer 周期性补充（replenishment），超限时 throttling。

### 3.2 seL4 MCS budget/refill 模型

seL4 采用不同的实时模型：

- [syscall.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/api/syscall.h) L19-30：`MCS_DO_IF_BUDGET` 宏在每个 syscall 入口执行 `updateTimestamp()` + `checkBudgetRestart()` — **budget 耗尽即停止执行**
- [schedcontext.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/schedcontext.c) L150-157：`maybeStallSC` — SMP 远程 TCB stall
- [schedcontext.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/schedcontext.c) L159-165：`replyFromKernel_consumed` — consumed time 通过 IPC buffer 返回给用户态
- [schedcontext.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/schedcontext.c) L184-200：`invokeSchedContext_YieldTo` — yieldTo + scYieldFrom 完成
- [endpoint.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/endpoint.c) L101-103：`schedContext_donate()` — **SC 捐赠**（发送方将 SC 捐给接收方）
- [endpoint.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/endpoint.c) L106-112：`refill_sufficient` / `refill_ready` / `refill_unblock_check` — refill 链检查

### 3.3 Airymax 现状

[stc_mcs_map.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_mcs_map.c) L18-24 定义 6 个 MCS 关键性标志位：

```
STC_MCS_FLAG_REALTIME    0x01  → SCHED_DEADLINE + GFP_ATOMIC|__GFP_HIGH  (L32-34)
STC_MCS_FLAG_HIGH        0x02  → SCHED_FIFO + GFP_KERNEL|__GFP_HIGH     (L35-37)
STC_MCS_FLAG_NORMAL      0x04  → SCHED_NORMAL + GFP_KERNEL              (L38-40)
STC_MCS_FLAG_BACKGROUND  0x08  → SCHED_BATCH + GFP_KERNEL|__GFP_NORETRY (L41-43)
```

L27-53 的 `stc_mcs_to_linux()` 将 MCS 标志映射为 `(gfp << 16) | linux_policy` 复合返回值。

[sched.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/sched.h) L58-71 定义任务描述符 `airy_task_desc`，包含 `runtime_ns` / `deadline_ns` / `period_ns`（L62-64）三件套，对应 SCHED_DEADLINE 的 CBS 参数。

### 3.4 差距分析

| 能力 | openEuler | seL4 | Airymax | 差距 |
|------|-----------|------|---------|------|
| CBS 带宽准入 | dl_bw_check_overflow | SC budget | **缺失** | P1 |
| Budget 入口检查 | task_tick hrtimer | MCS_DO_IF_BUDGET | **缺失** | P1 |
| SC 捐赠 | N/A | schedContext_donate | **缺失** | P2 |
| Consumed time 上报 | N/A | replyFromKernel_consumed | **缺失** | P2 |
| YieldTo | N/A | invokeSchedContext_YieldTo | **缺失** | P2 |
| Refill 链 | replenishment hrtimer | refill_sufficient | **依赖 Linux CBS** | 可接受 |

---

## 4. EEVDF 改造证据

### 4.1 openEuler KABI_REPLACE 改造

[sched.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/sched.h) L714-798 的 `struct cfs_rq` 包含三处关键 EEVDF 改造（通过 KABI_REPLACE 保持二进制兼容）：

- **L722**：`KABI_REPLACE(s64 avg_vruntime, s64 sum_w_vruntime)` — 原来的 `avg_vruntime` 改为 `sum_w_vruntime`（加权和），这是 EEVDF eligible 判定的核心
- **L723**：`KABI_REPLACE(u64 avg_load, u64 sum_weight)` — 配套权重累加器
- **L726**：`KABI_REPLACE(u64 min_vruntime, u64 zero_vruntime)` — 零点虚拟时间基准

L736：`struct rb_root_cached tasks_timeline` — EEVDF 红黑树（按虚拟截止时间排序）。

### 4.2 Airymax EEVDF 复用

Airymax **不改造 EEVDF 实现**，而是直接复用 Linux 6.6 原生 EEVDF（SCHED_NORMAL）。[sched.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/sched.h) L37-50 定义了 Q16.16 定点虚拟时间类型 `airy_vtime_t` 和衰减函数 `airy_vtime_decay()`：

```c
typedef __s32 airy_vtime_t;                          // L38
#define AIRY_VTIME_ONE  (1 << 16)                     // L40
static inline airy_vtime_t airy_vtime_decay(...)      // L42-50
    return vtime + (AIRY_SLICE_DFL * AIRY_VTIME_ONE) / weight;
```

**评价**：Airymax 的 `airy_vtime_decay` 是一个**用户态可见的 vtime 衰减近似公式**，但内核 EEVDF 实际使用的是 `sum_w_vruntime`（加权和）+ `avg_vruntime` + lag 计算，并非简单的 `slice/weight` 累加。二者语义不同：

- Airymax 公式：`vtime += slice / weight`（线性衰减，旧 CFS 语义）
- EEVDF 实际：`sum_w_vruntime += delta * weight`，`avg_vruntime = sum_w_vruntime / sum_weight`，eligible 判定基于 `lag = avg_vruntime - vruntime`

这是一个 **P1 语义偏差**：`airy_vtime_decay` 的注释声称是"EEVDF virtual time decay"，但公式是旧 CFS 语义。

---

## 5. openEuler 调度扩展（QoS / Soft-Quota / BPF_SCHED）

### 5.1 三项 openEuler 特有扩展

[sched.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/sched.h) 记录了 openEuler 在主线 6.6 之上的三项调度扩展：

- **L576-578**：`CONFIG_BPF_SCHED` + `tg_change_tag` — BPF 调度扩展（允许 BPF 程序干预 task_group 调度决策）
- **L611-627**：`CONFIG_QOS_SCHED_SMART_GRID` — QoS 智能网格调度，含 `auto_affinity` 自动亲和性
- **L629-631**：`CONFIG_SCHED_SOFT_QUOTA` — 软配额调度（允许超出硬配额的弹性分配）
- **L521**：`KABI_USE2(3, u32 scx_flags, u32 scx_weight)` — sched_ext task_group 字段（KABI 占用）

### 5.2 Airymax 立场

Airymax 明确**禁用 sched_ext**（[cross-project-code-sharing.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md) L30），理由是纯 C LSM 原则与 BPF 调度扩展冲突。`stc_mcs_map.c` 的 MCS 关键性映射在功能上对应 openEuler 的 `QOS_SCHED_SMART_GRID`（按关键性分级），但实现路径完全不同：

- openEuler：BPF 程序动态注入调度策略
- Airymax：编译期固定 MCS 标志 → Linux policy 静态映射

**评价**：Airymax 的静态映射更安全（可形式化验证），但灵活性远低于 openEuler BPF_SCHED。这是有意识的设计权衡，无需改变，但应在文档中记录决策依据。

---

## 6. seL4 MCS 关键性映射

### 6.1 seL4 MCS 模型

seL4 MCS（Mixed-Criticality Systems）通过 SchedContext（SC）对象实现：

- 每个 TCB 绑定一个 SC，SC 携带 budget（预算时间）和 period（周期）
- [schedcontext.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/schedcontext.c) L71-85：`invokeSchedContext_Bind` — TCB/Notification 绑定到 SC
- [schedcontext.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/schedcontext.c) L87-140：`decodeSchedContext_Bind` — 双重绑定检查 + `isBlocked && !sc_released` 检查
- [schedcontext.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/schedcontext.c) L142-148：`invokeSchedContext_Unbind` — `unbindAllTCBs` + `unbindNtfn` + `unbindReply`

### 6.2 Airymax MCS 映射

[stc_mcs_map.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_mcs_map.c) 的映射是**单向静态查表**，不涉及 SC 对象的绑定/解绑生命周期。Airymax 没有 SchedContext 等价物，关键性仅影响：

1. 调度策略选择（SCHED_DEADLINE/FIFO/NORMAL/BATCH）
2. GFP 分配掩码（GFP_ATOMIC vs GFP_KERNEL）

**差距**：seL4 的 SC 是一等对象（可 bind/unbind/donate/yieldTo），Airymax 的 MCS 标志是**只读属性**，无运行时生命周期管理。

---

## 7. 改进建议

### 7.1 [P1] stc_dispatch.c 用 pr_info 影响性能

**现状**：[stc_dispatch.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_dispatch.c) L73-75 在每次 `stc_dispatch_enqueue` 时调用 `pr_info()` 输出策略映射日志：

```c
pr_info("stc_dispatch: %s → %s (pid=%d comm=%s)\n",
    stc_name, stc_linux_policy_name(linux_policy),
    tsk->pid, tsk->comm);
```

**参考**：openEuler 调度器使用 `CONFIG_SCHED_DEBUG` 控制的 tracepoint + `/proc/sched_debug`（[sched.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/sched.h) sched_debug 机制），主线调度路径不使用 `pr_info`。

**建议**：将 L73 的 `pr_info` 替换为 `trace_airy_stc_dispatch(policy, linux_policy, tsk->pid)`，通过 tracepoint 暴露，仅在 `CONFIG_SCHED_DEBUG=y` 时启用。同时保留 `pr_warn_ratelimited`（L67/L89）用于异常路径。

**风险**：低。tracepoint 是零开销（disabled 时为 nop），不影响 fastpath。工作量约 2 小时（定义 tracepoint + 替换调用点）。

### 7.2 [P1] stc_stats 未通过 debugfs/sysfs 暴露

**现状**：[stc_stats.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_stats.c) L20-23 维护全局 `stc_dispatch_count` + `stc_policy_count[4]` 计数器，L37-39 提供 `stc_stats_read()` 查询接口，但**无 debugfs/sysfs 暴露**，用户态无法读取。

**参考**：openEuler 通过 `/proc/sched_debug` 暴露调度统计（对应 `CONFIG_SCHED_DEBUG`）。

**建议**：在 `stc_stats.c` 中增加 `debugfs_create_dir("airy_stc")` + `debugfs_create_devmem`/`debugfs_create_u32` 暴露 5 个计数器（1 总计 + 4 分策略）。

**风险**：低。debugfs 是可选模块，`CONFIG_DEBUG_FS=n` 时自动跳过。工作量约 3 小时。

### 7.3 [P1] airy_vtime_decay 语义偏差

**现状**：[sched.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/sched.h) L42-50 的 `airy_vtime_decay` 注释声称"EEVDF virtual time decay"，但公式 `vtime += slice / weight` 是旧 CFS 语义，非 EEVDF 的 `sum_w_vruntime += delta * weight` 语义。

**参考**：openEuler EEVDF 改造证据 [sched.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/sched.h) L722 `sum_w_vruntime`（加权和）+ L726 `zero_vruntime`（零点基准）。

**建议**：二选一：
- (A) 修正注释，明确这是"用户态可见的 vtime 近似"，不等于内核 EEVDF 内部算法；
- (B) 如果此函数实际被 cognition 子系统用于 vtime 预估，应改为 EEVDF 语义 `vtime += delta * weight / sum_weight`（需要传入 sum_weight 参数）。

**风险**：中。若选 (B) 需修改 UAPI 签名，可能影响下游消费者。建议优先 (A)，待 cognition 子系统实际集成时再评估 (B)。

### 7.4 [P2] 缺少 CBS 带宽准入

**现状**：Airymax 未实现 `dl_bw` 等价的带宽准入控制。`stc_dispatch_enqueue`（[stc_dispatch.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_dispatch.c) L54-96）直接调用 `sched_set_scheduler`，不检查总带宽是否溢出。

**参考**：openEuler [sched.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/sched.h) L350 `struct dl_bw` + L365 `dl_bw_check_overflow` — SCHED_DEADLINE 准入时检查 `runtime/period` 总和是否超过 CPU 容量。

**建议**：在 `stc_dispatch_enqueue` 调用 `sched_set_scheduler` 前增加带宽检查。可复用 Linux 原生 `__sched_dl_overflow`（通过 `sched_setattr` 路径自动触发），或实现 Airymax 自有的 `airy_dl_bw_check`。

**风险**：中。复用原生路径最安全（`sched_set_scheduler` 内部已含检查），但需确认 Airymax 调用路径是否绕过了检查。工作量约 4 小时（审计 + 测试）。

### 7.5 [P2] 缺少 MCS budget 入口检查

**现状**：[airy_syscalls.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/syscalls/airy_syscalls.c) 的 4 个 syscall 入口（L78/L143/L164/L189）均**无 budget 检查**。当前返回 -ENOSYS（M1 脚手架），但 M2-M5 实现真实逻辑时需要 budget guard。

**参考**：seL4 [syscall.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/api/syscall.h) L19-30 的 `MCS_DO_IF_BUDGET` 宏在每个 syscall 入口执行 `updateTimestamp()` + `checkBudgetRestart()`。

**建议**：在 M2 实现 `airy_sys_call` 真实逻辑时，增加 `airy_sched_budget_check(current)` 入口守卫，检查当前 agent 的 `sched_budget_ns`（[lsm_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/lsm_types.h) L32）是否耗尽。

**风险**：低（M2 阶段实施）。预算耗尽时返回 `-AIRY_EAGAIN` 或 `-ETIME`。

### 7.6 [P2] 缺少 SC 捐赠与 consumed time 上报

**现状**：Airymax 无 SchedContext 捐赠语义，`stc_mcs_map.c` 仅做静态标志映射。

**参考**：seL4 [endpoint.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/endpoint.c) L101-103 `schedContext_donate()` + [schedcontext.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/schedcontext.c) L159-165 `replyFromKernel_consumed`。

**建议**：这是 P2 长期项。若 cognition 子系统需要"调用方将预算捐赠给被调用方"的语义（如 Agent A 调用 Agent B 的推理服务，A 将自己的时间片捐给 B），可考虑通过 `airy_sys_sched_ctl`（550）扩展 `AIRY_SCHED_OP_DONATE` 操作。

**风险**：高。SC 捐赠涉及复杂的优先级反转防护和 refill 链管理。建议仅在确有需求时实施。

---

## 8. 小结

Airymax sched_tac 的"映射而非新增"策略在 ALK 约束下是合理的工程选择，成功复用了 Linux EEVDF/CBS/FIFO 的成熟实现。主要差距集中在：

1. **可观测性**（P1）：pr_info → tracepoint、stats → debugfs
2. **语义准确性**（P1）：airy_vtime_decay 注释/公式偏差
3. **运行时治理**（P2）：带宽准入、budget 入口检查、SC 捐赠

这些差距不构成 M0/M1 阶段阻断项，但应在 M2（io_uring IPC 集成）和 M3（sched_tac 策略守护进程）里程碑中逐步收敛。
