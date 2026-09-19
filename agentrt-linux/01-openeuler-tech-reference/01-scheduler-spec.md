Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# openEuler 调度器技术规范参考

> **文档定位**: 闭源内部参考，openEuler 调度器技术规范全面参考
> **保密级别**: SPHARX Ltd 内部参考，**闭源不公开**
> **版本**: 0.1.1（文档体系完成）/ 1.0.1（开发）
> **最后更新**: 2026-07-07
> **参考源**: openEuler 社区 + OLK-6.6（Linux 6.6 内核源码）

---

## 1. 文档说明

### 1.1 目的

本文档全面参考 openEuler 社区的调度器技术规范，作为 AirymaxOS SCHED_AGENT 策略设计的参考基础。所有参考内容**仅供 SPHARX Ltd 内部使用**，不得出现在开源文档（`docs/docs-linux/`）中。

### 1.2 参考来源

| 来源 | 内容 | 路径 / URL |
|------|------|-----------|
| OLK-6.6 源码 | openEuler LTS 6.6 内核源码 | Linux 6.6 源码根目录 |
| openEuler 文档 | 调度器设计文档 | openEuler 社区文档站 |
| Linux 主线 | sched_ext / EEVDF 主线实现 | kernel.org |
| Meta sched_ext | BPF 可插拔调度器 | GitHub: sched_ext/sched_ext |

### 1.3 OLK-6.6 版本标记

```
OPENEULER_LTS = 0       # 非 LTS 修改版本（基线）
OPENEULER_MAJOR = 9999  # 占位
OPENEULER_MINOR = 0
OPENEULER_RELEASE = ""
```

OLK-6.6 是基于 Linux 6.6 主线的 openEuler 内核基线，包含从主线 6.12+ 前向移植的 sched_ext 特性。

### 1.4 三段式参考方法

按用户三段式方法论，AirymaxOS 调度器设计参考流程：

1. **先参考 Euler**：查阅本文档对应章节的 openEuler 调度器规范
2. **再参考行业最新理论**：查阅 `04-industry-best-practices/01-latest-theory.md` 中的最新理论
3. **最后形成 AirymaxOS 技术方案**：综合形成开源设计文档 `docs/docs-linux/40-dataflows/04-scheduling-flow.md`

---

## 2. openEuler 调度器整体架构

### 2.1 调度类层次

openEuler（基于 Linux 6.6）的调度类层次自上而下：

| 调度类 | 优先级 | 用途 | openEuler 增强 |
|--------|--------|------|---------------|
| `stop_sched_class` | 最高 | 停机任务 | 无 |
| `dl_sched_class` | 高 | Deadline 实时任务 | 无 |
| `rt_sched_class` | 中高 | POSIX 实时（SCHED_FIFO/RR） | per-CPU rt 优化 |
| `ext_sched_class` | 中 | sched_ext BPF 调度 | OLK-6.6 前向移植 |
| `fair_sched_class` | 中低 | EEVDF（SCHED_NORMAL/BATCH/IDLE） | EEVDF 调优 |
| `idle_sched_class` | 最低 | idle 任务 | 无 |

### 2.2 调度核心数据结构

| 数据结构 | 作用 | openEuler 增强 |
|---------|------|---------------|
| `struct rq` | per-CPU 运行队列 | 增加 scx 字段（sched_ext 集成） |
| `struct cfs_rq` | CFS/EEVDF 运行队列 | EEVDF augmented 红黑树 |
| `struct rt_rq` | 实时运行队列 | 无 |
| `struct dl_rq` | Deadline 运行队列 | 无 |
| `struct sched_ext_entity` | sched_ext 实体 | OLK-6.6 新增 |
| `struct scx_dispatch_q` | DSQ 调度队列 | OLK-6.6 新增 |
| `struct task_group` | cgroup 调度组 | 增加 scx 字段 |

### 2.3 openEuler 调度器子系统划分

| 子系统 | 路径 | 职责 |
|--------|------|------|
| 核心调度 | `kernel/sched/core.c` | 调度核心、tick、负载均衡 |
| EEVDF | `kernel/sched/fair.c` | EEVDF 算法实现 |
| 实时调度 | `kernel/sched/rt.c` | POSIX 实时 |
| Deadline | `kernel/sched/deadline.c` | Deadline 调度 |
| sched_ext | `kernel/sched/ext.c` + `ext.h` | BPF 可插拔调度 |
| cgroup | `kernel/sched/sched.h` | cgroup 调度集成 |
| CPU idle | `kernel/sched/idle.c` | idle 任务管理 |
| 等待队列 | `kernel/sched/wait_bit.c` | 等待位 |
| 自动 NUMA | `kernel/sched/numa_balancing.c` | NUMA 自动均衡 |

---

## 3. EEVDF 调度器规范

### 3.1 EEVDF 核心算法

EEVDF（Earliest Eligible Virtual Deadline First）是 Linux 6.6 默认调度算法，openEuler OLK-6.6 完整继承。

| 概念 | 定义 | 计算 |
|------|------|------|
| vruntime | 虚拟运行时间 | `vruntime += delta_exec * 1024 / weight` |
| lag | 延迟（实际 vs 期望） | `lag = ideal_runtime - actual_runtime` |
| eligible | 资格判定 | `lag <= lag_threshold`（默认 0） |
| virtual deadline | 虚拟截止时间 | `deadline = vruntime + timeslice` |
| timeslice | 时间片 | `timeslice = sysctl_sched_base_slice * weight / total_weight` |

### 3.2 EEVDF 选择算法

```
1. 过滤 eligible 任务（lag <= 0）
2. 在 eligible 中选 earliest virtual deadline
3. 若全部 ineligible，重置 lag 后重新选择
```

### 3.3 EEVDF vs CFS 对比

| 维度 | CFS | EEVDF | 优势 |
|------|-----|-------|------|
| 数据结构 | 红黑树 | augmented 红黑树 | 支持截止时间查询 |
| 选择依据 | 最小 vruntime | earliest eligible virtual deadline | 延迟更紧凑 |
| 时间片 | 固定公式 | 动态 timeslice + deadline | 实时性更好 |
| 抢占 | tick + wakeup | tick + wakeup + deadline | 抢占更精确 |
| P99 延迟 | ~150ms | ~100ms | 提升 33% |
| P99.9 延迟 | ~300ms | ~200ms | 提升 33% |

### 3.4 EEVDF 调优参数

| 参数 | 默认值 | 作用 | openEuler 调优建议 |
|------|--------|------|-------------------|
| `sched_base_slice_ns` | 1ms | 基础时间片 | 服务器 0.75ms，桌面 1ms |
| `sched_wakeup_granularity_ns` | 1ms | 唤醒粒度 | 实时场景 0.5ms |
| `sched_latency_ns` | 6ms | 调度延迟 | 服务器 6ms，桌面 3ms |
| `sched_migration_cost_ns` | 500us | 迁移成本 | NUMA 场景 1000us |
| `sched_min_granularity_ns` | （EEVDF 废弃） | - | EEVDF 用 sched_base_slice 替代 |

### 3.5 openEuler EEVDF 调优实践

openEuler 社区针对服务器工作负载的 EEVDF 调优建议：

```bash
# 服务器场景（吞吐优先）
echo 750000 > /proc/sys/kernel/sched_base_slice_ns       # 0.75ms
echo 1000000 > /proc/sys/kernel/sched_wakeup_granularity_ns  # 1ms
echo 6000000 > /proc/sys/kernel/sched_latency_ns         # 6ms

# 实时场景（延迟优先）
echo 500000 > /proc/sys/kernel/sched_base_slice_ns       # 0.5ms
echo 500000 > /proc/sys/kernel/sched_wakeup_granularity_ns  # 0.5ms
echo 3000000 > /proc/sys/kernel/sched_latency_ns         # 3ms

# NUMA 场景
echo 1000000 > /proc/sys/kernel/sched_migration_cost_ns  # 1ms
```

### 3.6 AirymaxOS 借鉴要点

| openEuler 规范 | AirymaxOS SCHED_AGENT 落地 |
|---------------|----------------------------|
| EEVDF 默认调度器 | SCHED_AGENT 的 fallback 策略 |
| augmented 红黑树 | DSQ vtime 优先队列 |
| eligible 资格判定 | Agent 任务 eligibility 检查 |
| 服务器调优建议 | 默认 `agent_throughput` 策略参数 |
| 实时调优建议 | 默认 `agent_realtime` 策略参数 |

---

## 4. sched_ext 框架规范

### 4.1 sched_ext 设计哲学

sched_ext（BPF extensible scheduler class）是 Meta 贡献给 Linux 主线的可插拔调度框架，openEuler OLK-6.6 从主线 6.12+ 前向移植。

**核心设计哲学**：

1. **可插拔**：BPF 程序运行时加载/卸载，无需重启
2. **软可靠性**：SCX 核心拒绝无效 BPF 派发，BPF 错误自动回退 CFS
3. **系统完整性**：失败/超时/SysRq-S 自动卸载，保证系统不卡死
4. **DSQ 解耦**：BPF 调度器与调度核心通过 DSQ（Dispatch Queue）解耦
5. **完整接口**：导出完整调度接口，任意调度算法可实现

### 4.2 sched_ext 配置要求

```kconfig
CONFIG_BPF=y                    # BPF 基础
CONFIG_SCHED_CLASS_EXT=y         # sched_ext 调度类
CONFIG_BPF_SYSCALL=y             # BPF 系统调用
CONFIG_BPF_JIT=y                 # BPF JIT 编译
CONFIG_DEBUG_INFO_BTF=y          # BTF 调试信息
CONFIG_BPF_JIT_ALWAYS_ON=y       # BPF JIT 强制开启
CONFIG_BPF_JIT_DEFAULT_ON=y      # BPF JIT 默认开启
CONFIG_PAHOLE_HAS_SPLIT_BTF=y    # pahole BTF 分割
CONFIG_PAHOLE_HAS_BTF_TAG=y      # pahole BTF tag
CONFIG_EXT_GROUP_SCHED=y         # cgroup 集成（可选）
```

### 4.3 struct sched_ext_ops 完整回调表

详见闭源源码映射文档 [`02-olk66-source-mapping/01-sched-ext-mapping.md`](../02-olk66-source-mapping/01-sched-ext-mapping.md) §3。

### 4.4 DSQ（Dispatch Queue）机制

| DSQ 类型 | 标识 | 语义 |
|---------|------|------|
| `SCX_DSQ_INVALID` | builtin 0 | 无效 |
| `SCX_DSQ_GLOBAL` | builtin 1 | 全局 FIFO |
| `SCX_DSQ_LOCAL` | builtin 2 | per-CPU 本地 |
| `SCX_DSQ_BYPASS` | builtin 3 | 卸载过渡 |
| `SCX_DSQ_LOCAL_ON` | builtin + cpu | 指定 CPU 本地 |
| 用户 DSQ | user-created | BPF 自定义 |

**DSQ ID 编码**（64 位）：

```
[63] B = 1 builtin / 0 user
[62] L = 1 LOCAL_ON
[61..32] R = reserved
[31..0]  V = value / cpu
```

### 4.5 SCX_OPS 标志位

| 标志 | 值 | 语义 | openEuler 使用 |
|------|-----|------|---------------|
| `SCX_OPS_KEEP_BUILTIN_IDLE` | 1<<0 | 保留内置 idle 追踪 | 多数策略使用 |
| `SCX_OPS_ENQ_LAST` | 1<<1 | 最后任务通知 BPF | 独占 CPU 策略 |
| `SCX_OPS_SWITCH_PARTIAL` | 1<<3 | 仅 SCHED_EXT 走 SCX | 混合部署 |

### 4.6 sched_ext 状态机

**调度器级状态机**（`scx_ops_enable_state`）：

```
DISABLED → ENABLING → ENABLED → DISABLING → DISABLED
```

**任务级状态机**（`scx_task_state`）：

```
NONE → INIT → READY → ENABLED → READY → ...
```

**任务 ops_state**（BPF/SCX 所有权追踪）：

```
NONE → QUEUEING → QUEUED → DISPATCHING → NONE
```

### 4.7 fallback_dsq 回退机制

触发条件：

| 触发 | 说明 |
|------|------|
| BPF 主动 exit | `ops.exit()` 调用 |
| runnable 超时 | 任务等待超过 timeout_ms（默认 30s） |
| BPF 程序错误 | 验证器拒绝 / 运行时错误 |
| SysRq-S | 紧急回退快捷键 |
| 内存分配失败 | BPF 程序 OOM |

回退流程：

1. 所有任务迁入 `SCX_DSQ_BYPASS`（FIFO）
2. CFS（EEVDF）重新接管调度
3. 状态迁移 `ENABLED → DISABLING → DISABLED`

### 4.8 BPF kfunc 调用上下文限制

`kf_mask` 限制不同回调上下文可调用的 kfunc 集合：

| 掩码 | 上下文 |
|------|-------|
| `SCX_KF_UNLOCKED` | sleepable，无 rq 锁 |
| `SCX_KF_CPU_RELEASE` | `cpu_release()` 回调内 |
| `SCX_KF_DISPATCH` | `dispatch()` 回调内 |
| `SCX_KF_ENQUEUE` | `enqueue()` / `select_cpu()` |
| `SCX_KF_SELECT_CPU` | `select_cpu()` 回调内 |
| `SCX_KF_REST` | 其他 rq-locked 操作 |

### 4.9 openEuler 示例调度器

OLK-6.6 的 `tools/sched_ext/` 包含 6 个示例调度器：

| 示例 | 调度策略 | 适用场景 |
|------|---------|---------|
| `scx_simple` | 全局 FIFO / vtime | 通用 |
| `scx_qmap` | 多优先级 FIFO 队列 | 实时 |
| `scx_central` | 单 CPU 集中调度 | 批处理 |
| `scx_flatcg` | 扁平 cgroup 调度 | 多租户 |
| `scx_pair` | CPU 配对调度 | core-sched |
| `scx_userland` | 用户态调度器 | 原型 |

### 4.10 AirymaxOS 借鉴要点

| openEuler sched_ext 规范 | AirymaxOS SCHED_AGENT 落地 |
|--------------------------|----------------------------|
| sched_ext 框架（主线 6.12+ 前向移植） | AirymaxOS 内核增强（FR-002） |
| struct sched_ext_ops 回调表 | SCHED_AGENT BPF 程序回调（[SS] 语义同源） |
| DSQ 调度队列 | agent_dispatch_q（[SS] 语义同源） |
| SCX_OPS 标志位 | SCHED_AGENT 策略标志 |
| 状态机 | 调度器级 + 任务级状态机 |
| fallback_dsq 回退 | BPF 失败自动回退 EEVDF |
| kf_mask 上下文限制 | 严格按回调上下文调用 kfunc |
| scx_simple 示例 | default_eevdf 策略参考 |
| scx_qmap 示例 | agent_realtime 策略参考 |
| scx_flatcg 示例 | agent_fairness 策略参考 |
| 30s 超时 | 分级超时（高 5s / 标准 30s / 后台 60s） |

---

## 5. cgroup 调度规范

### 5.1 cgroup v2 调度

openEuler 完整支持 cgroup v2 调度：

| cgroup 控制器 | 调度相关 | 用途 |
|--------------|---------|------|
| `cpu` | ✅ | CPU 带宽限制 |
| `cpuset` | ✅ | CPU 亲和性 |
| `cpuacct` | （v2 合并到 cpu） | CPU 计费 |
| `sched_ext` | （CONFIG_EXT_GROUP_SCHED） | sched_ext cgroup 集成 |

### 5.2 CPU 带宽限制

```bash
# 设置 cgroup CPU 带宽（quota/period）
echo 50000 > /sys/fs/cgroup/agent_group/cpu.max  # 50ms/100ms = 50%

# 查看 CPU 使用
cat /sys/fs/cgroup/agent_group/cpu.stat
```

### 5.3 CPU 亲和性

```bash
# 设置 cgroup CPU 亲和性
echo "0-15" > /sys/fs/cgroup/agent_group/cpuset.cpus
echo "0" > /sys/fs/cgroup/agent_group/cpuset.mems
```

### 5.4 sched_ext cgroup 集成

`CONFIG_EXT_GROUP_SCHED` 启用 sched_ext cgroup 集成：

| 回调 | 作用 |
|------|------|
| `cgroup_init` | cgroup 初始化 |
| `cgroup_exit` | cgroup 退出 |
| `cgroup_prep_move` | 任务跨 cgroup 准备 |
| `cgroup_move` | 任务跨 cgroup 提交 |
| `cgroup_cancel_move` | 任务跨 cgroup 取消 |
| `cgroup_set_weight` | cgroup 权重更新 |

### 5.5 AirymaxOS 借鉴要点

| openEuler cgroup 规范 | AirymaxOS SCHED_AGENT 落地 |
|---------------------|----------------------------|
| cgroup v2 调度 | Agent cgroup 多租户隔离 |
| cpu.max 带宽限制 | Agent 任务 CPU 配额 |
| cpuset 亲和性 | Agent 任务 CPU 绑定 |
| sched_ext cgroup 集成 | Agent cgroup 调度策略 |

---

## 6. NUMA 调度规范

### 6.1 自动 NUMA 均衡

openEuler 支持自动 NUMA 均衡（`kernel/sched/numa_balancing.c`）：

```bash
# 启用/禁用自动 NUMA 均衡
echo 1 > /proc/sys/kernel/numa_balancing

# NUMA 均衡参数
cat /proc/sys/kernel/numa_balancing
cat /proc/sys/kernel/numa_balancing_scan_period_min_ms  # 1000
cat /proc/sys/kernel/numa_balancing_scan_period_max_ms  # 60000
cat /proc/sys/kernel/numa_balancing_scan_size_mb        # 256
```

### 6.2 NUMA 亲和性调度

| 机制 | 说明 | openEuler 增强 |
|------|------|---------------|
| `sched_numa_find_nth_cpu` | NUMA CPU 查找 | 无 |
| `sched_numa_hop_mask` | NUMA hop 掩码 | 无 |
| `select_task_rq` | NUMA CPU 选择 | per-CPU 缓存优化 |
| `migrate_swap` | NUMA 任务交换 | 无 |

### 6.3 sched_ext NUMA 集成

sched_ext 通过 `ops.select_cpu` 回调实现 NUMA 亲和：

```c
s32 BPF_STRUCT_OPS(agent_select_cpu, struct task_struct *p,
                   s32 prev_cpu, u64 wake_flags) {
    /* NUMA 亲和性 + EEVDF 资格判定 */
    return scx_bpf_select_cpu_dfl(p, prev_cpu, wake_flags, NULL);
}
```

### 6.4 AirymaxOS 借鉴要点

| openEuler NUMA 规范 | AirymaxOS SCHED_AGENT 落地 |
|--------------------|-----------------------------|
| 自动 NUMA 均衡 | Agent 任务 NUMA 亲和 |
| NUMA hop 掩码 | 超节点 CPU 选择 |
| select_cpu 回调 | NUMA 亲和 + idle 判定 |
| CXL 内存池化 | 超节点间任务迁移（< 100ms） |

---

## 7. 实时调度规范

### 7.1 POSIX 实时调度

openEuler 支持 POSIX 实时调度（SCHED_FIFO / SCHED_RR）：

| 策略 | 说明 | 优先级范围 |
|------|------|-----------|
| `SCHED_FIFO` | 先进先出，不抢占 | 1-99 |
| `SCHED_RR` | 轮转，时间片抢占 | 1-99 |
| `SCHED_DEADLINE` | Deadline 调度 | （EDF） |

### 7.2 实时带宽限制

```bash
# 实时任务带宽限制（默认 95%）
echo 950000 > /proc/sys/kernel/sched_rt_runtime_us  # 950ms/1s
echo 1000000 > /proc/sys/kernel/sched_rt_period_us  # 1s
```

### 7.3 PREEMPT_RT 支持

openEuler 部分版本支持 PREEMPT_RT（实时内核）：

| 配置 | 说明 |
|------|------|
| `CONFIG_PREEMPT_RT` | 实时内核 |
| `CONFIG_PREEMPT_RT_FULL` | 完整实时 |
| `CONFIG_PREEMPT_VOLUNTARY` | 自愿抢占（默认） |

### 7.4 AirymaxOS 借鉴要点

| openEuler 实时规范 | AirymaxOS SCHED_AGENT 落地 |
|-------------------|----------------------------|
| POSIX 实时调度 | SCHED_AGENT 高优先级（0-49） |
| 实时带宽限制 | 实时 Agent CPU 配额 |
| PREEMPT_RT | kernel 可选启用 |
| Deadline 调度 | Agent 任务 deadline_ns 字段 |

---

## 8. 调度性能调优规范

### 8.1 性能测量工具

| 工具 | 用途 | 命令 |
|------|------|------|
| `perf sched` | 调度延迟分析 | `perf sched record -a -- sleep 60` |
| `ftrace` | 调度事件追踪 | `echo 1 > /sys/kernel/debug/tracing/events/sched/...` |
| `sched_debug` | 调度器状态 | `cat /proc/sched_debug` |
| `schedstat` | 调度统计 | `cat /proc/[pid]/schedstat` |
| `bpftool` | BPF 程序分析 | `bpftool prog show` |
| `scx_show_state` | sched_ext 状态 | `tools/sched_ext/scx_show_state.py` |

### 8.2 关键 sysctl 参数

| 参数 | 默认值 | 作用 | openEuler 调优建议 |
|------|--------|------|-------------------|
| `sched_base_slice_ns` | 1ms | 基础时间片 | 服务器 0.75ms |
| `sched_wakeup_granularity_ns` | 1ms | 唤醒粒度 | 实时 0.5ms |
| `sched_latency_ns` | 6ms | 调度延迟 | 桌面 3ms |
| `sched_migration_cost_ns` | 500us | 迁移成本 | NUMA 1ms |
| `sched_rt_runtime_us` | 950000 | 实时带宽 | 950ms/1s |
| `sched_rt_period_us` | 1000000 | 实时周期 | 1s |
| `numa_balancing` | 1 | NUMA 均衡 | 启用 |
| `sched_schedstats` | 0 | 调度统计 | 调试时启用 |

### 8.3 cgroup 调度调优

```bash
# CPU 带宽限制
echo 50000 > /sys/fs/cgroup/agent_group/cpu.max  # 50%

# CPU 亲和性
echo "0-15" > /sys/fs/cgroup/agent_group/cpuset.cpus

# CPU 权重
echo 100 > /sys/fs/cgroup/agent_group/cpu.weight  # 默认 100
```

### 8.4 sched_ext 调优

```bash
# sched_ext 状态
cat /sys/kernel/sched_ext/state         # enabled / disabled
cat /sys/kernel/sched_ext/root/ops      # 当前策略名
cat /sys/kernel/sched_ext/enable_seq    # 加载次数

# sched_ext 超时
echo 30000 > /sys/kernel/sched_ext/timeout_ms  # 30s

# 加载策略
agentrt-sched-bench --policy default_eevdf --duration 60s
agentrt-sched-bench --policy agent_realtime --duration 60s
```

### 8.5 AirymaxOS 借鉴要点

| openEuler 性能调优规范 | AirymaxOS SCHED_AGENT 落地 |
|----------------------|----------------------------|
| perf sched 调度延迟 | NFR-P-001 延迟分布目标 |
| ftrace 调度事件 | 可观测性 perf + ftrace |
| sched_debug 状态 | `/sys/fs/agentrt/sched/` |
| sysctl 调优参数 | EEVDF + SCHED_AGENT 调优 |
| cgroup 调度调优 | Agent cgroup 多租户 |
| sched_ext 状态查看 | Prometheus Metrics |

---

## 9. 调度可观测性规范

### 9.1 tracepoint 事件

openEuler 调度器 tracepoint：

| tracepoint | 触发 |
|-----------|------|
| `sched:sched_switch` | 任务切换 |
| `sched:sched_wakeup` | 任务唤醒 |
| `sched:sched_wakeup_new` | 新任务唤醒 |
| `sched:sched_process_fork` | 任务 fork |
| `sched:sched_process_exit` | 任务退出 |
| `sched:sched_stat_runtime` | 运行时统计 |
| `sched:sched_stat_sleep` | 睡眠统计 |
| `sched:sched_stat_iowait` | IO 等待统计 |
| `sched:sched_migrate_task` | 任务迁移 |
| `sched:sched_swap` | 任务交换 |

### 9.2 /proc 调度信息

| 路径 | 内容 |
|------|------|
| `/proc/sched_debug` | 调度器详细状态 |
| `/proc/[pid]/sched` | 单任务调度信息 |
| `/proc/[pid]/schedstat` | 单任务调度统计 |
| `/proc/schedstat` | 系统调度统计 |

### 9.3 /sys 调度信息

| 路径 | 内容 |
|------|------|
| `/sys/kernel/sched_ext/state` | sched_ext 状态 |
| `/sys/kernel/sched_ext/root/ops` | 当前策略名 |
| `/sys/kernel/sched_ext/enable_seq` | 加载次数 |
| `/sys/kernel/debug/sched_ext/` | sched_ext debug |

### 9.4 AirymaxOS 借鉴要点

| openEuler 可观测性规范 | AirymaxOS SCHED_AGENT 落地 |
|----------------------|----------------------------|
| tracepoint 事件 | perf + ftrace + Prometheus Metrics |
| /proc/sched_debug | `/sys/fs/agentrt/sched/` |
| /proc/[pid]/sched | 单 Agent 任务调度信息 |
| /sys/kernel/sched_ext/ | Prometheus Metrics + 结构化日志 |
| /sys/kernel/debug/sched_ext/ | AirymaxOS 调度器调试接口 |

---

## 10. 调度安全规范

### 10.1 capability 权限模型

openEuler 调度器权限模型：

| 操作 | 所需 capability |
|------|----------------|
| `sched_setscheduler` 提升优先级 | `CAP_SYS_NICE` |
| 加载 sched_ext BPF 程序 | `CAP_BPF` + `CAP_SYS_ADMIN` |
| 设置实时优先级 | `CAP_SYS_NICE` |
| 设置 CPU 亲和性 | `CAP_SYS_NICE` |
| 修改 cgroup CPU 配额 | `CAP_SYS_ADMIN` |

### 10.2 seccomp 过滤

openEuler 支持 seccomp 过滤调度相关 syscall：

| syscall | 过滤建议 |
|---------|---------|
| `sched_setscheduler` | 按策略过滤 |
| `sched_setaffinity` | 按 CPU 掩码过滤 |
| `sched_setattr` | 按属性过滤 |
| `bpf` | 按 command 过滤 |

### 10.3 LSM 钩子

openEuler LSM（Linux Security Module）调度钩子：

| 钩子 | 作用 |
|------|------|
| `security_task_setscheduler` | 拦截 sched_setscheduler |
| `security_task_setioprio` | 拦截 IO 优先级设置 |
| `security_task_prlimit` | 拦截 prlimit |
| `security_bpf` | 拦截 BPF 操作 |
| `security_bpf_map` | 拦截 BPF map 操作 |

### 10.4 AirymaxOS 借鉴要点

| openEuler 安全规范 | AirymaxOS SCHED_AGENT 落地 |
|-------------------|----------------------------|
| capability 权限 | SCHED_ADMIN capability（策略切换） |
| CAP_BPF + CAP_SYS_ADMIN | BPF 程序加载权限 |
| seccomp 过滤 | Agent 任务 seccomp 沙箱 |
| LSM 钩子 | Cupolas 安全穹顶集成 |

---

## 11. 与 AirymaxOS 设计的差异化声明

### 11.1 AirymaxOS 增强（超越 openEuler）

| 增强 | openEuler | AirymaxOS SCHED_AGENT |
|------|-----------|------------------------|
| 分级超时 | 单一 30s | 高 5s / 标准 30s / 后台 60s |
| 超节点迁移 | 无 | CXL + RDMA 跨节点迁移（< 100ms） |
| Agent 优先级 | weight [1..10000] | priority 0-139 + weight 映射 |
| 认知循环集成 | 无 | CoreLoopThree kthread 协同 |
| 同源红利 | 无 | agentrt 天然适配（无适配层） |
| IRON-9 v2 共享契约 | 无 | `include/airymax/sched.h` 共享 |

### 11.2 AirymaxOS 独立设计

| 设计 | openEuler | AirymaxOS |
|------|-----------|-----------|
| 任务描述符 | `task_struct` | `agentrt_task_desc_t`（同源 [SC]） |
| 调度类编号 | SCHED_EXT (6) | SCHED_AGENT (7) |
| magic | 无 | 0x41475453 'AGTS'（同源 [SC]） |
| 策略 API | 无统一 API | `agentrt_sched_load_policy` 等 |
| Metrics | 无统一 Metrics | Prometheus + 结构化日志 |
| 审计日志 | 无统一审计 | 策略切换审计 + fallback 审计 |

### 11.3 IRON-9 v2 共享边界

| IRON-9 v2 三层 | openEuler 参考 | AirymaxOS 落地 |
|---------------|---------------|----------------|
| [SC] 共享契约层 | 参考接口设计规范 | `include/airymax/sched.h` |
| [SS] 语义同源层 | 参考子系统实现思路 | SCHED_AGENT BPF 程序 |
| [IND] 完全独立层 | 不参考 openEuler 实现 | systemd 集成、Kbuild |

---

## 12. 参考文献与源码

### 12.1 openEuler 源码

| 路径 | 内容 |
|------|------|
| `kernel/sched/core.c` | 调度核心 |
| `kernel/sched/fair.c` | EEVDF |
| `kernel/sched/ext.c` | sched_ext |
| `kernel/sched/ext.h` | sched_ext 内部头 |
| `include/linux/sched/ext.h` | sched_ext 公共头 |
| `kernel/sched/rt.c` | 实时调度 |
| `kernel/sched/deadline.c` | Deadline |
| `kernel/sched/numa_balancing.c` | NUMA 均衡 |
| `Documentation/scheduler/sched-ext.rst` | sched_ext 文档 |
| `tools/sched_ext/` | 示例调度器 |
| `Makefile.oever` | openEuler 版本标记 |

### 12.2 openEuler 社区文档

- openEuler 内核 SIG 调度器文档
- openEuler 24.03 LTS 调度器性能调优指南
- openEuler 26.03 调度器新特性

### 12.3 Linux 主线文档

- `Documentation/scheduler/sched-ext.rst`
- `Documentation/scheduler/sched-eevdf.rst`
- `Documentation/admin-guide/cgroup-v2.rst`

### 12.4 学术参考

- EEVDF: "Earliest Eligible Virtual Deadline First" (Linux 6.6)
- sched_ext: Tejun Heo, David Vernet (Meta, 2022)
- seL4: Liedtke minimality principle
- Zircon: Fuchsia microkernel

---

## 13. 相关文档

### 13.1 闭源参考（本目录）

- [闭源参考索引](../README.md)：4 子目录闭源参考框架
- [sched_ext 源码映射](../02-olk66-source-mapping/01-sched-ext-mapping.md)：OLK-6.6 sched_ext → SCHED_AGENT 映射
- [微内核设计参考](../03-microkernel-design-ref/README.md)：seL4/Zircon/Minix3 参考
- [行业最佳实践](../04-industry-best-practices/README.md)：最新理论与最佳实践

### 13.2 开源设计文档（`docs/docs-linux/`）

- [调度数据流](../../docs/docs-linux/40-dataflows/04-scheduling-flow.md)：SCHED_AGENT 数据流（开源版）
- [内核模块设计](../../docs/docs-linux/20-modules/01-kernel.md)：kernel 子仓
- [工程基线](../../docs/docs-linux/10-architecture/04-engineering-baseline.md)：Linux 6.6 内核基线

---

## 14. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 0.1.1 | 2026-07-07 | 初始版本，全面参考 openEuler 调度器技术规范（13 节） |

---

> **文档结束** | SPHARX Ltd 内部参考 | 闭源不公开
