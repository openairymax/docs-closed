Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# OLK-6.6 sched_ext → AirymaxOS SCHED_AGENT 源码映射

> **文档定位**: 闭源内部参考，OLK-6.6 `kernel/sched/ext.c` + `ext.h` 源码 → AirymaxOS SCHED_AGENT 设计映射
> **保密级别**: SPHARX Ltd 内部参考，**闭源不公开**
> **版本**: 0.1.1（文档体系完成）/ 1.0.1（开发）
> **最后更新**: 2026-07-07
> **源码基线**: OLK-6.6（Linux 6.6 内核源码）

---

## 1. 文档说明

### 1.1 目的

本文档建立 OLK-6.6 sched_ext（可插拔 BPF 调度器框架）源码到 AirymaxOS SCHED_AGENT 策略设计的精确映射，标注 IRON-9 v2 三层共享模型边界：

| 标注 | 含义 | 共享程度 |
|------|------|----------|
| **[SC]** | Shared Contract 共享契约层 | 完全共享代码（`include/airymax/`） |
| **[SS]** | Semantic Same-origin 语义同源层 | API 签名同源，实现独立 |
| **[IND]** | Independent 完全独立层 | 各自独立实现 |

### 1.2 源码定位

| 路径 | 说明 | 行数 |
|------|------|------|
| `kernel/sched/ext.c` | sched_ext 主实现 | ~5800 行 |
| `kernel/sched/ext.h` | 内部头文件（生命周期函数） | 119 行 |
| `include/linux/sched/ext.h` | 公共头文件（`struct sched_ext_entity`） | 217 行 |
| `Documentation/scheduler/sched-ext.rst` | 设计文档 | ~2000 行 |
| `tools/sched_ext/` | 示例 BPF 调度器（6 个示例） | - |
| `kernel/Kconfig.preempt` | `CONFIG_SCHED_CLASS_EXT` 配置说明 | - |

### 1.3 关键配置选项

```kconfig
CONFIG_BPF=y
CONFIG_SCHED_CLASS_EXT=y      # 启用 sched_ext 调度类
CONFIG_BPF_SYSCALL=y           # BPF 系统调用
CONFIG_BPF_JIT=y              # BPF JIT 编译
CONFIG_DEBUG_INFO_BTF=y       # BTF 调试信息
CONFIG_EXT_GROUP_SCHED=y      # sched_ext cgroup 集成（可选）
```

---

## 2. sched_ext 核心数据结构映射

### 2.1 struct sched_ext_entity [SS]

**源码位置**: `include/linux/sched/ext.h:140-204`

`struct sched_ext_entity` 嵌入在 `task_struct` 中，承载每个任务在 sched_ext 下的全部状态。AirymaxOS SCHED_AGENT 的 `agentrt_task_desc` 与其语义同源。

| sched_ext 字段 | 类型 | AirymaxOS SCHED_AGENT 对应 | 同源标注 |
|---------------|------|---------------------------|----------|
| `dsq` | `struct scx_dispatch_q *` | agent_dispatch_queue 引用 | [SS] |
| `dsq_list` / `dsq_priq` | list_head / rb_node | 双向链表 + vtime 红黑树 | [SS] |
| `flags` | u32 | SCX_TASK_QUEUED / RESET_RUNNABLE_AT / DEQD_FOR_SLEEP / CURSOR | [SS] |
| `weight` | u32 | Agent 任务权重 [1..10000] | [SC] |
| `sticky_cpu` / `holding_cpu` | s32 | CPU 亲和性临时锚定 | [SS] |
| `kf_mask` | u32 | kfunc 调用上下文掩码（5 类） | [IND] |
| `ops_state` | atomic_long_t | NONE→QUEUEING→QUEUED→DISPATCHING | [SS] |
| `runnable_node` / `runnable_at` | list_head / unsigned long | runnable 链表节点 + 入队时间 | [SS] |
| `slice` | u64 | 运行预算（ns），自动衰减 | [SC] |
| `dsq_vtime` | u64 | vtime 优先队列排序键 | [SC] |
| `disallow` | bool | 拒绝后续 sched_setscheduler 切换到 SCX | [IND] |

### 2.2 struct scx_dispatch_q（DSQ 调度队列） [SS]

**源码位置**: `include/linux/sched/ext.h:60-70`

DSQ（Dispatch Queue）是 sched_ext 的核心队列抽象，每个 CPU 拥有本地 DSQ，可创建用户 DSQ。

| sched_ext 字段 | 类型 | AirymaxOS 对应 | 备注 |
|---------------|------|----------------|------|
| `lock` | raw_spinlock_t | raw_spinlock_t | 队列自旋锁 |
| `list` | list_head | list_head | FIFO 顺序链表 |
| `priq` | rb_root | rb_root | vtime 优先红黑树 |
| `nr` | u32 | u32 | 队列任务计数 |
| `id` | u64 | u64 | DSQ ID（builtin/user 区分） |

**DSQ ID 编码**（`enum scx_dsq_id_flags`）：

```
[63] B = 1 builtin / 0 user
[62] L = 1 LOCAL_ON
[61..32] R = reserved
[31..0]  V = value / cpu

Builtin: INVALID(0) | GLOBAL(1) | LOCAL(2) | BYPASS(3) | LOCAL_ON(cpu)
```

### 2.3 内置 DSQ 语义映射 [SS]

| Builtin DSQ | sched_ext 语义 | AirymaxOS SCHED_AGENT 语义 |
|-------------|---------------|---------------------------|
| `SCX_DSQ_INVALID` | 无效 DSQ | 未初始化 |
| `SCX_DSQ_GLOBAL` | 全局 FIFO DSQ | 全局 Agent 调度队列 |
| `SCX_DSQ_LOCAL` | 当前 CPU 本地 DSQ | per-CPU Agent 本地队列 |
| `SCX_DSQ_BYPASS` | bypass 队列（卸载期使用） | 策略卸载过渡队列 |
| `SCX_DSQ_LOCAL_ON` | 指定 CPU 的本地 DSQ | 远端 CPU Agent 派发 |

---

## 3. struct sched_ext_ops 回调映射 [SS]

**源码位置**: `kernel/sched/ext.c:238-728`

`struct sched_ext_ops` 是 sched_ext 的核心回调表，BPF 调度器通过实现此表的回调函数定义调度策略。AirymaxOS SCHED_AGENT 的 BPF 程序同源实现这些回调。

### 3.1 任务生命周期回调

| sched_ext 回调 | 签名 | 触发时机 | AirymaxOS SCHED_AGENT 映射 | [SC/SS/IND] |
|---------------|------|---------|---------------------------|-------------|
| `init_task` | `s32 (*)(task_struct *p, scx_init_task_args *args)` | BPF 加载或 fork 时初始化任务 | Agent 任务初始化（分配 agentrt_task_desc） | [SS] |
| `exit_task` | `void (*)(task_struct *p, scx_exit_task_args *args)` | 任务退出或 BPF 卸载 | Agent 任务清理 | [SS] |
| `enable` | `void (*)(task_struct *p)` | 任务进入 SCX 时 | Agent 任务启用 SCHED_AGENT | [SS] |
| `disable` | `void (*)(task_struct *p)` | 任务退出 SCX 或 BPF 卸载 | Agent 任务禁用 | [SS] |

### 3.2 队列管理回调（核心）

| sched_ext 回调 | 签名 | 触发时机 | AirymaxOS SCHED_AGENT 映射 | [SC/SS/IND] |
|---------------|------|---------|---------------------------|-------------|
| `select_cpu` | `s32 (*)(task_struct *p, s32 prev_cpu, u64 wake_flags)` | 任务唤醒时选择目标 CPU | NUMA 亲和性 + EEVDF 资格判定 | [SS] |
| `enqueue` | `void (*)(task_struct *p, u64 enq_flags)` | 任务入 BPF 调度器 | Agent 入队（per-CPU agent_queue） | [SS] |
| `dequeue` | `void (*)(task_struct *p, u64 deq_flags)` | 任务出 BPF 调度器 | Agent 出队（属性更新时） | [SS] |
| `dispatch` | `void (*)(s32 cpu, task_struct *prev)` | CPU 本地 DSQ 空时 | EEVDF 选择派发到 LOCAL_DSQ | [SS] |

### 3.3 任务状态通知回调

| sched_ext 回调 | 签名 | 语义 | AirymaxOS SCHED_AGENT 映射 | [SC/SS/IND] |
|---------------|------|------|---------------------------|-------------|
| `runnable` | `void (*)(task_struct *p, u64 enq_flags)` | 任务变为 runnable | Agent 进入就绪状态 | [SS] |
| `running` | `void (*)(task_struct *p)` | 任务开始执行 | Agent 执行开始 | [SS] |
| `stopping` | `void (*)(task_struct *p, bool runnable)` | 任务停止执行 | Agent 执行停止（slice 耗尽/抢占） | [SS] |
| `quiescent` | `void (*)(task_struct *p, u64 deq_flags)` | 任务变为非 runnable | Agent 进入阻塞 | [SS] |

### 3.4 时钟与性能回调

| sched_ext 回调 | 签名 | 语义 | AirymaxOS SCHED_AGENT 映射 | [SC/SS/IND] |
|---------------|------|------|---------------------------|-------------|
| `tick` | `void (*)(task_struct *p)` | 周期 tick（1/HZ 秒） | Agent 执行 tick 统计 + 抢占检查 | [SS] |
| `can_stop_tick` | 内核实现（`ext.h`） | 是否允许停止 tick | 高优先级 Agent 不允许 | [IND] |
| `set_weight` | `void (*)(task_struct *p, u32 weight)` | 任务权重更新 [1..10000] | Agent 优先级映射 | [SC] |
| `set_cpumask` | `void (*)(task_struct *p, const cpumask *)` | CPU 亲和性更新 | Agent CPU 亲和性 | [SS] |

### 3.5 CPU 与 SMP 回调

| sched_ext 回调 | 签名 | 语义 | AirymaxOS SCHED_AGENT 映射 | [SC/SS/IND] |
|---------------|------|------|---------------------------|-------------|
| `update_idle` | `void (*)(s32 cpu, bool idle)` | CPU 进入/离开 idle | 超节点 idle 追踪 | [SS] |
| `cpu_acquire` | `void (*)(s32 cpu, scx_cpu_acquire_args *)` | CPU 回到 BPF 控制 | Agent 重获 CPU | [SS] |
| `cpu_release` | `void (*)(s32 cpu, scx_cpu_release_args *)` | CPU 被高优先级抢占 | Agent 释放 CPU | [SS] |
| `cpu_online` | `void (*)(s32 cpu)` | CPU 上线 | 超节点 CPU 扩容 | [SS] |
| `cpu_offline` | `void (*)(s32 cpu)` | CPU 下线 | 超节点 CPU 缩容 | [SS] |

### 3.6 调度核心集成回调

| sched_ext 回调 | 签名 | 语义 | AirymaxOS SCHED_AGENT 映射 | [SC/SS/IND] |
|---------------|------|------|---------------------------|-------------|
| `yield` | `bool (*)(task_struct *from, task_struct *to)` | 任务 yield CPU | Agent 显式让出 | [SS] |
| `core_sched_before` | `bool (*)(task_struct *a, task_struct *b)` | core-sched 排序 | SMT 兄弟核 Agent 排序 | [IND] |
| `balance` | 内核实现 | SMP 负载均衡 | 超节点间负载均衡 | [SS] |

### 3.7 cgroup 回调（CONFIG_EXT_GROUP_SCHED）

| sched_ext 回调 | 签名 | 语义 | AirymaxOS SCHED_AGENT 映射 | [SC/SS/IND] |
|---------------|------|------|---------------------------|-------------|
| `cgroup_init` | `s32 (*)(cgroup *, scx_cgroup_init_args *)` | cgroup 初始化 | Agent cgroup 初始化 | [IND] |
| `cgroup_exit` | `void (*)(cgroup *)` | cgroup 退出 | Agent cgroup 清理 | [IND] |
| `cgroup_prep_move` | `s32 (*)(task_struct *, cgroup *from, cgroup *to)` | 任务跨 cgroup 准备 | Agent 跨 cgroup 迁移 | [IND] |
| `cgroup_move` | `void (*)(task_struct *, cgroup *from, cgroup *to)` | 任务跨 cgroup 提交 | Agent cgroup 提交 | [IND] |
| `cgroup_cancel_move` | `void (*)(task_struct *, cgroup *from, cgroup *to)` | 任务跨 cgroup 取消 | Agent cgroup 取消 | [IND] |
| `cgroup_set_weight` | `void (*)(cgroup *, u32 weight)` | cgroup 权重更新 | Agent cgroup 权重 | [IND] |

### 3.8 BPF 调度器生命周期回调

| sched_ext 回调 | 签名 | 语义 | AirymaxOS SCHED_AGENT 映射 | [SC/SS/IND] |
|---------------|------|------|---------------------------|-------------|
| `init` | `s32 (*)(void)` | BPF 调度器初始化（可阻塞） | 调度策略加载初始化 | [SS] |
| `exit` | `void (*)(scx_exit_info *info)` | BPF 调度器退出（含 init 失败） | 调度策略卸载 + 错误信息 | [SS] |
| `dump` / `dump_cpu` / `dump_task` | `void (*)(scx_dump_ctx *, ...)` | 错误时 dump 调试 | Agent 调度器调试 dump | [IND] |

### 3.9 ops 字段（非回调）

| 字段 | 类型 | 默认值 | AirymaxOS 对应 | [SC/SS/IND] |
|------|------|--------|---------------|-------------|
| `name` | char[128] | - | 调度策略名（如 "agent_realtime"） | [SC] |
| `flags` | u64 | 0 | SCX_OPS_* 标志位 | [SS] |
| `dispatch_max_batch` | u32 | - | dispatch 单次最大派发数 | [SS] |
| `timeout_ms` | u32 | 30000 | runnable 超时阈值（30s） | [SC] |
| `exit_dump_len` | u32 | 32768 | exit dump 缓冲区大小 | [IND] |
| `hotplug_seq` | u64 | 0 | 热插拔序列号检测 | [SS] |

---

## 4. SCX_OPS 标志位映射 [SS]

**源码位置**: `kernel/sched/ext.c:103-171`

| 标志位 | 值 | 语义 | AirymaxOS SCHED_AGENT 使用 | [SC/SS/IND] |
|--------|-----|------|---------------------------|-------------|
| `SCX_OPS_KEEP_BUILTIN_IDLE` | 1<<0 | 保留内核内置 idle 追踪 | Agent 调度器依赖内置 idle | [SS] |
| `SCX_OPS_ENQ_LAST` | 1<<1 | enqueue 最后一个任务时通知 BPF | Agent 独占 CPU 模式 | [SS] |
| `SCX_OPS_SWITCH_PARTIAL` | 1<<3 | 仅 SCHED_EXT 任务走 SCX，CFS 任务走 CFS | Agent 混合部署模式 | [SS] |

**关键决策**：AirymaxOS SCHED_AGENT 默认**不设置** `SCX_OPS_SWITCH_PARTIAL`，即 BPF 加载后所有 SCHED_NORMAL/SCHED_BATCH/SCHED_IDLE/SCHED_EXT 任务均走 SCHED_AGENT，最大化 Agent 调度优先级。

---

## 5. SCX 状态机映射 [SS]

**源码位置**: `kernel/sched/ext.c:853-896`（scx_ops_state）+ `839-851`（scx_ops_enable_state）

### 5.1 调度器级状态机（scx_ops_enable_state）

```
SCX_OPS_DISABLED → SCX_OPS_ENABLING → SCX_OPS_ENABLED
                       ↑                  ↓
                       └──── SCX_OPS_DISABLING ←────┘
```

| 状态 | AirymaxOS 对应 | 触发 |
|------|---------------|------|
| `DISABLED` | 未加载策略 | 系统启动/策略卸载完成 |
| `ENABLING` | 策略加载中 | `scx_ops_enable()` 调用 |
| `ENABLED` | 策略运行中 | init 成功 + 所有任务迁移完成 |
| `DISABLING` | 策略卸载中 | exit / 错误 / SysRq-S |

### 5.2 任务级状态机（scx_task_state）

```
SCX_TASK_NONE → SCX_TASK_INIT → SCX_TASK_READY → SCX_TASK_ENABLED
                                       ↑              ↓
                                       └──────────────┘
```

| 状态 | 语义 | AirymaxOS 对应 |
|------|------|---------------|
| `NONE` | init_task 未调用 | Agent 任务未注册 |
| `INIT` | init_task 成功，可取消 | Agent 注册中 |
| `READY` | 完全初始化，未进入 SCX | Agent 待激活 |
| `ENABLED` | 完全初始化且在 SCX | Agent 运行中 |

### 5.3 任务 ops_state（BPF/SCX 所有权追踪）

```
NONE → QUEUEING → QUEUED → DISPATCHING
  ^                 |             |
  |                 v             v
  └─────────────────────────────────┘
```

`atomic_long_t ops_state` 让 SCX 核心随时可靠判定任务是否可被 BPF 派发，从而放宽对 BPF 调度器的要求（BPF 可尝试派发任意状态的任务，SCX 核心拒绝无效派发）。AirymaxOS SCHED_AGENT 同源采用此机制实现**软可靠性**。

---

## 6. BPF kfunc 调用上下文掩码 [IND]

**源码位置**: `include/linux/sched/ext.h:108-121`（enum scx_kf_mask）

sched_ext 通过 `kf_mask` 限制不同回调上下文可调用的 kfunc 集合，避免 BPF 程序在不安全上下文中调用需 rq 锁的 kfunc。

| 掩码 | 值 | 上下文 | AirymaxOS SCHED_AGENT 对应 |
|------|-----|--------|---------------------------|
| `SCX_KF_UNLOCKED` | 0 | sleepable，无 rq 锁 | Agent init/exit 回调 |
| `SCX_KF_CPU_RELEASE` | 1<<0 | `cpu_release()` 回调内 | Agent CPU 释放回调 |
| `SCX_KF_DISPATCH` | 1<<1 | `dispatch()` 回调内 | Agent dispatch 回调 |
| `SCX_KF_ENQUEUE` | 1<<2 | `enqueue()` / `select_cpu()` | Agent 入队回调 |
| `SCX_KF_SELECT_CPU` | 1<<3 | `select_cpu()` 回调内 | Agent CPU 选择回调 |
| `SCX_KF_REST` | 1<<4 | 其他 rq-locked 操作 | Agent 其他回调 |

**AirymaxOS 决策**：完全同源采用 kf_mask 机制（[IND] 标注的原因是掩码实现是 AirymaxOS 内核增强的内核态机制，不进入 `include/airymax/` 共享头文件）。

---

## 7. SCX 标志位枚举映射 [SS]

### 7.1 enqueue 标志（`enum scx_enq_flags`）

| 标志 | 值 | 语义 | AirymaxOS 使用 |
|------|-----|------|---------------|
| `SCX_ENQ_WAKEUP` | ENQUEUE_WAKEUP | 唤醒入队 | ✅ |
| `SCX_ENQ_HEAD` | ENQUEUE_HEAD | 入队头（高优先级） | ✅ |
| `SCX_ENQ_CPU_SELECTED` | ENQUEUE_RQ_SELECTED | CPU 已选 | ✅ |
| `SCX_ENQ_PREEMPT` | 1<<32 | 触发抢占 | ✅ Agent 实时抢占 |
| `SCX_ENQ_REENQ` | 1<<40 | reenqueue | ✅ |
| `SCX_ENQ_LAST` | 1<<41 | 最后一个任务 | ✅ 独占模式 |

### 7.2 kick 标志（`enum scx_kick_flags`）

| 标志 | 值 | 语义 | AirymaxOS 使用 |
|------|-----|------|---------------|
| `SCX_KICK_IDLE` | 1<<0 | 唤醒 idle CPU | ✅ Agent 唤醒 |
| `SCX_KICK_PREEMPT` | 1<<1 | 抢占当前任务 | ✅ 高优先级 Agent 抢占 |
| `SCX_KICK_WAIT` | 1<<2 | 等待目标切换出 | ✅ core-sched |

---

## 8. sched_ext 与 EEVDF 协同机制 [SS]

### 8.1 调度类优先级

`ext_sched_class` 位于 `fair_sched_class`（EEVDF）之上、`rt_sched_class` 之下。当 BPF 调度器加载且 `SCX_OPS_SWITCH_PARTIAL` 未设置时，所有 SCHED_NORMAL/BATCH/IDLE/EXT 任务走 sched_ext，EEVDF 退化为 fallback。

### 8.2 fallback_dsq 回退机制

sched_ext 内置 `SCX_DSQ_BYPASS` 队列，当 BPF 调度器卸载或失败时：
1. 所有任务迁入 `SCX_DSQ_BYPASS`（FIFO）
2. CFS 重新接管调度
3. 触发 `SCX_OPS_DISABLING` → `SCX_OPS_DISABLED` 状态迁移

AirymaxOS SCHED_AGENT 同源实现 fallback 机制，确保 BPF 调度器失败时回退到 EEVDF 默认调度。

### 8.3 runnable 超时保护

`ops.timeout_ms`（默认 30000ms = 30s）限制 runnable 任务最长等待时间。超时触发 BPF 调度器卸载 + 错误 dump。

AirymaxOS SCHED_AGENT 同源采用 30s 超时保护，并增强为分级超时：
- 高优先级 Agent（0-49）：5s 超时
- 标准 Agent（50-99）：30s 超时
- 后台 Agent（100-139）：60s 超时

---

## 9. scx_simple 示例调度器映射 [SS]

**源码位置**: `tools/sched_ext/scx_simple.bpf.c`（151 行）

scx_simple 是 sched_ext 最简示例，实现全局加权 vtime 调度（可切换 FIFO 模式）。AirymaxOS SCHED_AGENT 的 `default_eevdf` 策略与此同源。

### 9.1 scx_simple 关键回调实现

```c
/* select_cpu: 使用默认 CPU 选择 + idle 直接入队 */
s32 BPF_STRUCT_OPS(simple_select_cpu, struct task_struct *p,
                   s32 prev_cpu, u64 wake_flags) {
    bool is_idle = false;
    s32 cpu = scx_bpf_select_cpu_dfl(p, prev_cpu, wake_flags, &is_idle);
    if (is_idle)
        scx_bpf_dsq_insert(p, SCX_DSQ_LOCAL, SCX_SLICE_DFL, 0);
    return cpu;
}

/* enqueue: FIFO 或 vtime 入队到 SHARED_DSQ */
void BPF_STRUCT_OPS(simple_enqueue, struct task_struct *p, u64 enq_flags) {
    if (fifo_sched) {
        scx_bpf_dsq_insert(p, SHARED_DSQ, SCX_SLICE_DFL, enq_flags);
    } else {
        u64 vtime = p->scx.dsq_vtime;
        if (time_before(vtime, vtime_now - SCX_SLICE_DFL))
            vtime = vtime_now - SCX_SLICE_DFL;
        scx_bpf_dsq_insert_vtime(p, SHARED_DSQ, SCX_SLICE_DFL, vtime, enq_flags);
    }
}

/* dispatch: SHARED_DSQ → LOCAL_DSQ */
void BPF_STRUCT_OPS(simple_dispatch, s32 cpu, struct task_struct *prev) {
    scx_bpf_dsq_move_to_local(SHARED_DSQ);
}

/* running: 推进 vtime_now */
void BPF_STRUCT_OPS(simple_running, struct task_struct *p) {
    if (fifo_sched) return;
    if (time_before(vtime_now, p->scx.dsq_vtime))
        vtime_now = p->scx.dsq_vtime;
}

/* stopping: 按权重逆比例累计 vtime */
void BPF_STRUCT_OPS(simple_stopping, struct task_struct *p, bool runnable) {
    if (fifo_sched) return;
    p->scx.dsq_vtime += (SCX_SLICE_DFL - p->scx.slice) * 100 / p->scx.weight;
}

/* enable: 任务进入 SCX 时初始化 vtime */
void BPF_STRUCT_OPS(simple_enable, struct task_struct *p) {
    p->scx.dsq_vtime = vtime_now;
}

/* init: 创建 SHARED_DSQ */
s32 BPF_STRUCT_OPS_SLEEPABLE(simple_init) {
    return scx_bpf_create_dsq(SHARED_DSQ, -1);
}

/* exit: 记录退出信息 */
void BPF_STRUCT_OPS(simple_exit, struct scx_exit_info *ei) {
    UEI_RECORD(uei, ei);
}

SCX_OPS_DEFINE(simple_ops,
    .select_cpu = (void *)simple_select_cpu,
    .enqueue    = (void *)simple_enqueue,
    .dispatch   = (void *)simple_dispatch,
    .running    = (void *)simple_running,
    .stopping   = (void *)simple_stopping,
    .enable     = (void *)simple_enable,
    .init       = (void *)simple_init,
    .exit       = (void *)simple_exit,
    .name       = "simple");
```

### 9.2 AirymaxOS default_eevdf 策略映射

| scx_simple 实现 | AirymaxOS default_eevdf 策略 | 同源标注 |
|----------------|----------------------------|----------|
| `simple_select_cpu` + `scx_bpf_select_cpu_dfl` | NUMA 亲和 + EEVDF 资格判定 | [SS] |
| `simple_enqueue` + `scx_bpf_dsq_insert_vtime` | vtime 入队 SHARED_DSQ | [SS] |
| `simple_dispatch` + `scx_bpf_dsq_move_to_local` | 派发到 LOCAL_DSQ | [SS] |
| `simple_running` + `vtime_now` 推进 | 全局 vtime 时钟 | [SC] |
| `simple_stopping` + 权重逆比例 | vtime 衰减公式 | [SC] |
| `simple_enable` + `vtime` 初始化 | Agent 任务 vtime 初始化 | [SS] |
| `simple_init` + `scx_bpf_create_dsq` | 创建 Agent SHARED_DSQ | [SS] |
| `simple_exit` + UEI_RECORD | 策略卸载错误记录 | [SS] |

---

## 10. 其他示例调度器参考 [IND]

**源码位置**: `tools/sched_ext/`（6 个示例调度器）

| 示例 | 调度策略 | AirymaxOS 对应策略 | 适用场景 |
|------|---------|---------------------|---------|
| `scx_simple` | 全局 FIFO / vtime | `default_eevdf` | 通用 |
| `scx_qmap` | 多优先级 FIFO 队列 | `agent_realtime` | 实时 Agent |
| `scx_central` | 单 CPU 集中调度 | `agent_throughput` | 批处理 |
| `scx_flatcg` | 扁平 cgroup 调度 | `agent_fairness` | 多租户 |
| `scx_pair` | CPU 配对调度 | SMT 兄弟核 Agent 配对 | core-sched |
| `scx_userland` | 用户态调度器 | （实验性） | 调度策略原型 |

**AirymaxOS 决策**：参考 `scx_qmap` 实现 `agent_realtime`，参考 `scx_flatcg` 实现 `agent_fairness`，但均独立实现（[IND]），不直接复制示例代码。

---

## 11. IRON-9 v2 共享边界汇总

### 11.1 [SC] 共享契约层（`include/airymax/sched.h`）

完全共享的契约定义（agentrt 和 AirymaxOS 均包含此头文件）：

```c
/* include/airymax/sched.h — 共享契约层 [SC] */

#ifndef AIRYMAX_SCHED_H
#define AIRYMAX_SCHED_H

/*
 * 复用内核 SCHED_EXT=7 调度类编号（include/uapi/linux/sched.h:121）。
 * 禁止定义 SCHED_AGENT 宏——SCHED_AGENT 仅作为 sched_ext BPF 策略名称。
 */
#define SCHED_AGENT_NAME  "sched_agent"  /* BPF 策略名称，非调度类编号 */

/* 任务描述符 magic（独立于 IPC 消息头） */
#define AGENTRT_TASK_DESC_MAGIC  0x41475453u  /* 'AGTS' */

/* SCX_SLICE_DFL 同源（20ms） */
#define AIRYMAX_SLICE_DFL  (20 * 1000000ULL)

/* 任务权重范围（与 sched_ext set_weight 同源） */
#define AIRYMAX_WEIGHT_MIN  1
#define AIRYMAX_WEIGHT_MAX  10000

/* vtime 数据类型同源 */
typedef u64 airymax_vtime_t;

/* 优先级范围 */
#define AIRYMAX_PRIO_RT_HIGH   0
#define AIRYMAX_PRIO_RT_LOW    49
#define AIRYMAX_PRIO_STD_HIGH  50
#define AIRYMAX_PRIO_STD_LOW   99
#define AIRYMAX_PRIO_BG_HIGH   100
#define AIRYMAX_PRIO_BG_LOW    139

/* 任务描述符（共享契约） */
typedef struct __attribute__((aligned(64))) agentrt_task_desc {
    uint32_t magic;          /* 0x41475453 'AGTS' */
    uint16_t version;
    uint16_t priority;       /* 0-139 */
    uint32_t flags;
    uint64_t task_id;
    uint64_t trace_id;
    uint64_t deadline_ns;
    uint32_t max_retries;
    uint32_t cpu_affinity;
    char     role[32];
    uint8_t  reserved[32];
} agentrt_task_desc_t;

/* vtime 衰减公式同源 */
static inline airymax_vtime_t
airymax_vtime_decay(airymax_vtime_t vtime, u64 consumed_slice, u32 weight) {
    return vtime + consumed_slice * 100 / weight;
}

#endif /* AIRYMAX_SCHED_H */
```

### 11.2 [SS] 语义同源层（API 签名同源，实现独立）

AirymaxOS SCHED_AGENT BPF 程序实现以下回调（签名与 sched_ext_ops 同源，但实现独立于 agentrt）：

- `agent_select_cpu`（对应 `select_cpu`）
- `agent_enqueue` / `agent_dequeue`（对应 `enqueue` / `dequeue`）
- `agent_dispatch`（对应 `dispatch`）
- `agent_runnable` / `agent_running` / `agent_stopping` / `agent_quiescent`
- `agent_init` / `agent_exit` / `agent_enable` / `agent_disable`
- `agent_tick` / `agent_set_weight` / `agent_set_cpumask`
- `agent_cpu_online` / `agent_cpu_offline` / `agent_update_idle`

agentrt 的 MicroCoreRT 不实现这些回调（用户态无 BPF），但消费同样的 `agentrt_task_desc_t` 契约，调度语义一致。

### 11.3 [IND] 完全独立层

AirymaxOS 专属（agentrt 不涉及）：
- `ext_sched_class` 注册（内核调度类）
- `scx_ops_enable` / `scx_ops_disable` 实现（内核态 BPF 加载）
- kf_mask 上下文追踪（内核态机制）
- fallback_dsq 回退（内核态机制）
- cgroup 集成（`CONFIG_EXT_GROUP_SCHED`）
- core-sched 集成（`core_sched_before`）
- debug dump（`dump` / `dump_cpu` / `dump_task`）
- Kbuild 集成（`Makefile` + `Kconfig`）

agentrt 专属（AirymaxOS 不涉及）：
- Python/Go/Rust/TS SDK 绑定
- 跨平台抽象层（Linux/macOS/Windows）
- CLI / TUI 工具

---

## 12. 设计合理性验证

### 12.1 sched_ext 设计优势（AirymaxOS 采纳）

| 优势 | 说明 | AirymaxOS 落地 |
|------|------|---------------|
| 可插拔 | BPF 程序运行时加载/卸载 | 调度策略热替换（FR-050） |
| 软可靠性 | SCX 核心拒绝无效 BPF 派发 | BPF 错误自动回退 EEVDF |
| 系统完整性 | 失败/超时/SysRq-S 自动卸载 | runnable 超时 30s 回退 |
| 性能 | DSQ per-CPU 本地队列 | 队列自旋锁不跨 CPU |
| 生态 | BPF 工具链复用 | bpftool + libbpf 直接可用 |

### 12.2 AirymaxOS 增强（超越 sched_ext）

| 增强 | sched_ext | AirymaxOS SCHED_AGENT |
|------|-----------|------------------------|
| 分级超时 | 单一 30s | 高 5s / 标准 30s / 后台 60s |
| 超节点迁移 | 无 | CXL + RDMA 跨节点迁移（< 100ms） |
| Agent 优先级 | weight [1..10000] | priority 0-139 + weight 映射 |
| 认知循环集成 | 无 | CoreLoopThree kthread 协同 |
| 同源红利 | 无 | agentrt 天然适配（无适配层） |

### 12.3 风险与缓解

| 风险 | 缓解措施 |
|------|---------|
| BPF 调度器 bug 导致系统卡死 | fallback_dsq 自动回退 EEVDF |
| runnable 超时无任务可调度 | 30s 超时阈值 + SysRq-S 紧急回退 |
| BPF 验证器拒绝复杂策略 | 策略分拆为多个简单 BPF 程序 |
| kf_mask 限制 kfunc 调用 | 严格按回调上下文调用 |
| cgroup 集成复杂度 | `CONFIG_EXT_GROUP_SCHED` 可选 |

---

## 13. 与 agentrt 设计一致性检查

### 13.1 命名一致性

| 维度 | agentrt | AirymaxOS SCHED_AGENT | 一致性 |
|------|---------|------------------------|--------|
| 任务描述符 | `agentrt_task_desc_t` | `agentrt_task_desc_t` | ✅ 共享契约 |
| 调度类编号 | （用户态无） | `SCHED_EXT=7`（复用内核，SCHED_AGENT 为 BPF 策略名） | ✅ AirymaxOS 专属 |
| magic | `0x41475453 'AGTS'` | `0x41475453 'AGTS'` | ✅ 共享契约 |
| 优先级 | 0-139 | 0-139 | ✅ 共享契约 |
| vtime 类型 | `airymax_vtime_t` (u64) | `airymax_vtime_t` (u64) | ✅ 共享契约 |
| 衰减公式 | `airymax_vtime_decay()` | `airymax_vtime_decay()` | ✅ 共享契约 |

### 13.2 语义一致性

| 语义 | agentrt MicroCoreRT | AirymaxOS SCHED_AGENT | 一致 |
|------|---------------------|------------------------|------|
| 调度类 | 用户态调度协程 | 内核调度类 + BPF 策略 | ✅ 同源语义 |
| 入队/出队 | 用户态链表 | DSQ + BPF 回调 | ✅ 同源语义 |
| 优先级抢占 | 用户态软抢占 | 内核硬抢占 + SCX_KICK_PREEMPT | ✅ AirymaxOS 增强 |
| vtime 计算 | 用户态计算 | BPF 计算（同公式） | ✅ 同源公式 |
| 策略切换 | 用户态动态切换 | BPF 运行时替换 | ✅ 同源机制 |

### 13.3 IRON-9 v2 合规性

| IRON-9 v2 三层 | 本文档覆盖 | 合规 |
|---------------|-----------|------|
| 共享契约层 [SC] | §11.1 `include/airymax/sched.h` 完整定义 | ✅ |
| 语义同源层 [SS] | §11.2 BPF 回调签名同源 | ✅ |
| 完全独立层 [IND] | §11.3 各自独立实现明确划分 | ✅ |

---

## 14. 相关文档

### 14.1 闭源参考（本目录）

- [闭源参考索引](../README.md)：4 子目录闭源参考框架
- [openEuler 调度器技术规范](../01-openeuler-tech-reference/01-scheduler-spec.md)：Euler 调度器规范参考
- [微内核设计参考](../03-microkernel-design-ref/README.md)：seL4/Zircon/Minix3 参考

### 14.2 开源设计文档（`docs/AirymaxAgentOS/`）

- [调度数据流](../../docs/AirymaxAgentOS/40-dataflows/04-scheduling-flow.md)：SCHED_AGENT 数据流（开源版）
- [内核模块设计](../../docs/AirymaxAgentOS/20-modules/01-kernel.md)：airymaxos-kernel 子仓
- [系统调用接口](../../docs/AirymaxAgentOS/30-interfaces/01-syscalls.md)：agentrt_sys_task_submit
- [工程基线](../../docs/AirymaxAgentOS/10-architecture/04-engineering-baseline.md)：Linux 6.6 内核基线
- [IRON-9 v2 定义](../../docs/AirymaxAgentOS/50-engineering-standards/README.md)：三层共享模型

### 14.3 OLK-6.6 源码（参考，不公开引用）

- `kernel/sched/ext.c` — sched_ext 主实现
- `kernel/sched/ext.h` — 内部头文件
- `include/linux/sched/ext.h` — 公共头文件
- `Documentation/scheduler/sched-ext.rst` — 设计文档
- `tools/sched_ext/` — 示例 BPF 调度器

---

## 15. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 0.1.1 | 2026-07-07 | 初始版本，建立 sched_ext → SCHED_AGENT 完整映射（14 节） |

---

> **文档结束** | SPHARX Ltd 内部参考 | 闭源不公开
