Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 认知 kthread 工程规范（参考 OLK-6.6 kthread + accel + drm_sched）

> **文档定位**: 闭源内部参考，基于 OLK-6.6 `kernel/kthread.c` + `drivers/accel/` + `drivers/gpu/drm/scheduler/` + 行业最新 LLM 推理理论，制定 AirymaxOS 认知循环（CoreLoopThree kthread + Thinkdual + LLM 调度 + GPU/NPU 池化）工程规范
> **保密级别**: SPHARX Ltd 内部参考，**闭源不公开**
> **版本**: 0.1.1（文档体系完成）
> **最后更新**: 2026-07-07
> **源码基线**: OLK-6.6（Linux 6.6 内核源码）
> **代码共享边界**: IRON-9 v2——agentrt ↔ AirymaxOS 共享 [SC] 契约层；与 OLK-6.6/Euler 仅技术参考，**不共享代码**
> **方法论**: 三段式——参考 Euler 工程规范 → 调研行业最新理论与最佳实践 → 形成 AirymaxOS 独有技术方案

---

## 1. 文档说明

### 1.1 目的

本文档基于 OLK-6.6 kthread/accel/drm_sched 源码工程实践，结合 2023-2026 行业最新 LLM 推理理论（vLLM/SGLang/LMCache/Mooncake/DeepSeek-V3/Sarathi/Speculative Decoding/DistServe），制定 AirymaxOS 认知子系统工程规范。

**三段式方法论**：
1. **第一阶段（参考 Euler）**：逐行核对 OLK-6.6 kthread.c/accel.c/sched_main.c 工程实践，提取可借鉴的协议与模式
2. **第二阶段（行业最新理论）**：调研 2023-2026 LLM 推理调度最佳实践（学术论文 + 开源项目）
3. **第三阶段（AirymaxOS 独有方案）**：基于前两阶段，结合微内核设计思想 + IRON-9 v2 三层共享模型，形成 AirymaxOS 认知子系统技术方案

### 1.2 与开源文档的关系

| 文档 | 性质 | 内容 |
|------|------|------|
| `docs/AirymaxOS/20-modules/05-cognition.md`（开源） | 公开 | 模块设计（不含 OLK-6.6 引用） |
| `docs/AirymaxOS/40-dataflows/01-cognition-flow.md`（开源） | 公开 | 数据流设计（不含 OLK-6.6 引用） |
| `docs-closed/agent-linux/02-olk66-source-mapping/06-cognition-mapping.md`（闭源） | 内部 | OLK-6.6 源码映射（38 条 OS-COG-MAP 规则） |
| **本文档**（闭源） | 内部 | 工程规范（kthread + LLM 调度 + GPU/NPU + 采纳决策） |

### 1.3 IRON-9 v2 三层共享模型

| 标注 | 含义 | 共享程度 |
|------|------|----------|
| **[SC]** | Shared Contract 共享契约层 | agentrt ↔ AirymaxOS 完全共享代码 |
| **[SS]** | Semantic Same-origin 语义同源层 | API 签名同源，实现独立 |
| **[IND]** | Independent 完全独立层 | AirymaxOS 独立实现 |

### 1.4 Euler 兼容性约束

AirymaxOS 认知子系统的工程思想与实现方式与 Euler 保持一致性，以便未来兼容 Euler 标准的发行版工具链：

- **协议层兼容**：kthread 创建/停止/驻留协议与 Euler 一致（不直接采用代码，但协议同源）
- **接入层兼容**：accel/drm_sched 模式与 Euler 一致（统一加速器接入、通用 GPU 调度器）
- **模块化兼容**：Kconfig 风格、模块组织与 Euler 一致
- **代码层独立**：AirymaxOS 自行实现内核态认知 kthread 机制，不直接采用 Euler 代码

---

## 2. kthread 工程规范

### 2.1 创建模式规范（kthread_run vs kthread_create_on_node）

**OLK-6.6 提供的创建入口**（`include/linux/kthread.h`）：

| API | 行号 | 语义 | 适用场景 |
|-----|------|------|----------|
| `kthread_create_on_node(fn, data, node, namefmt...)` | kthread.h:L11-14 | 底层原语，NUMA 节点感知，创建后处于 stopped 状态 | 需 NUMA 感知 / 延迟启动 |
| `kthread_create(fn, data, namefmt...)` | kthread.h:L27-28 | = create_on_node(NUMA_NO_NODE) | 无 NUMA 要求 |
| `kthread_create_on_cpu(fn, data, cpu, namefmt)` | kthread.c:L570-584 | create_on_node(cpu_to_node) + kthread_bind(cpu) | per-CPU 绑定 |
| `kthread_run(fn, data, namefmt...)` | kthread.h:L51-58 | kthread_create + wake_up_process 便捷封装 | 创建即启动 |
| `kthread_run_on_cpu(fn, data, cpu, namefmt)` | kthread.h:L72-83 | create_on_cpu + wake_up_process | per-CPU 即启动 |

**关键工程事实**：

1. **所有 kthread 经由 kthreadd 守护进程 fork**（kthread.c:L738-774）。kthreadd 由 `rest_init()` 在 boot 早期创建（PID=2），承担"为 kthread 提供干净环境"的职责——即使从用户态触发（modprobe、CPU hotplug），也能继承干净上下文。

2. **kthread 主体函数 `kthread()`（kthread.c:L340-391）的初始化序列**（CoreLoopThree kthread 必须理解的"出生环境"）：
   - `sched_setscheduler_nocheck(current, SCHED_NORMAL, &{.sched_priority=0})`（L369）——重置继承自 kthreadd 的优先级到 SCHED_NORMAL/0
   - `set_cpus_allowed_ptr(current, housekeeping_cpumask(HK_TYPE_KTHREAD))`（L370）——默认亲和到 housekeeping CPU 集（隔离 CPU 除外）
   - `__set_current_state(TASK_UNINTERRUPTIBLE)` + `complete(done)` + `schedule_preempt_disabled()`（L373-381）——通知创建者"我已出生"，然后睡眠等 `wake_up_process()`
   - `cgroup_kthread_ready()`（L386）——cgroup 关联就绪钩子
   - `__kthread_parkme(self)`（L387）——若被 park 则停留
   - `ret = threadfn(data)`（L388）——调用用户函数

3. **创建时默认不接收信号**：`create_kthread`（kthread.c:L403-425）以 `kernel_thread(kthread, create, name, CLONE_FS | CLONE_FILES | SIGCHLD)` 创建（L411-412），注释明确"we take no signals by default"。

4. **OOM 安全**：创建者用 `wait_for_completion_killable`（L460）等待，因为创建者可能被 OOM killer 选中。

**AirymaxOS 决策建议**（OS-COG-DEC-01）：
- CoreLoopThree 的 3 个 kthread（cognition / execution / memory）**必须使用 `kthread_create_on_node` + `wake_up_process`** 而非 `kthread_run`，原因：
  - (a) NUMA 感知——认知 kthread 应绑定到 GPU/NPU 所在 NUMA 节点
  - (b) 需在 `wake_up_process` 前完成 `kthread_bind` + `sched_setscheduler`（设 SCHED_EXT 策略优先级，加载 SCHED_AGENT BPF 策略）
- `kthread_run` 仅适合"创建即跑"的简单场景（如 drm_sched 的 helper）

### 2.2 优先级与 CPU 亲和性规范

**优先级设置 API**（OLK-6.6 `kernel/sched/`）：

| API | 用途 | kthread 适用性 |
|-----|------|----------------|
| `sched_setscheduler(p, policy, &param)` | 设置调度策略 + 优先级 | 通用 |
| `sched_setscheduler_nocheck(p, policy, &param)` | 同上但不检查 capabilities | kthread 内部用（kthread.c:L369） |
| `sched_setparam(p, &param)` | 仅设优先级 | RT 优先级调整 |
| `sched_set_fifo(p)` | 设 SCHED_FIFO prio=50（中） | 简便 RT |
| `sched_set_fifo_low(p)` | 设 SCHED_FIFO prio=1（低） | **drm_sched 选用** |
| `sched_set_normal(p, nice)` | 设 SCHED_NORMAL + nice | 普通优先级 |

**DRM 调度器的选择**（`drivers/gpu/drm/scheduler/sched_main.c:L1020`）：`drm_sched_main` 一进入就 `sched_set_fifo_low(current)`——SCHED_FIFO 优先级 1（最低 RT 优先级），避免与高优先级 RT kthread（如 ksoftirqd）竞争，但高于普通 CFS 任务。这是 GPU 调度类 kthread 的**事实标准**。

**CPU 亲和性 API**：

| API | 行号 | 行为 |
|-----|------|------|
| `kthread_bind(p, cpu)` | kthread.c:L554-558 | 绑定单 CPU，设 `PF_NO_SETAFFINITY` |
| `kthread_bind_mask(p, mask)` | kthread.c:L540 | 绑定 cpumask |
| `set_cpus_allowed_ptr(p, mask)` | — | 运行时动态调整（不设 PF_NO_SETAFFINITY） |
| `kthread_set_per_cpu(k, cpu)` | kthread.c:L587-602 | 标记 per-CPU |
| `kthread_is_per_cpu(p)` | kthread.c:L604-611 | 查询 per-CPU 标记 |

**关键点**：
- `__kthread_bind`（kthread.c:L519-538）通过 `wait_task_inactive(p, state)` 等待 kthread 进入指定状态后才 `do_set_cpus_allowed`，并置 `PF_NO_SETAFFINITY`——绑定后**用户态无法再改 affinity**
- `kthread_create_on_cpu`（L570-584）会缓存 `to_kthread(p)->cpu = cpu`，供 `kthread_unpark` 时 `__kthread_bind(k, kthread->cpu, TASK_PARKED)` 重新绑定——这是 CPU hotplug 友好设计
- `housekeeping_cpumask(HK_TYPE_KTHREAD)`：kthread 默认 cpumask，隔离 CPU（isolcpus）被排除

**AirymaxOS 决策建议**（OS-COG-DEC-02）：
- cognition kthread（思考循环，含 LLM 推理）→ SCHED_AGENT 高优先级，绑到 GPU/NPU 所在 NUMA 节点的 CPU
- execution kthread → SCHED_AGENT 中优先级
- memory kthread（L1→L4 卷载）→ SCHED_AGENT 低优先级，可设 SCHED_NORMAL 以避免抢占推理

### 2.3 停止协议规范（协作式停止）

OLK-6.6 采用**协作式停止**（cooperative stop），kthread 必须主动检查停止标志。`struct kthread` 的 `flags` 字段有 3 个 bit（kthread.c:L68-72）：

| bit | 名称 | 设置者 | 检查 API |
|-----|------|--------|----------|
| 0 | `KTHREAD_IS_PER_CPU` | `kthread_set_per_cpu` | `kthread_is_per_cpu` |
| 1 | `KTHREAD_SHOULD_STOP` | `kthread_stop` | `kthread_should_stop` |
| 2 | `KTHREAD_SHOULD_PARK` | `kthread_park` | `kthread_should_park` |

**`kthread_stop` 的完整序列**（kthread.c:L698-717，CoreLoopThree 停止协议必须遵循）：
1. `trace_sched_kthread_stop(k)`——ftrace 钩子
2. `get_task_struct(k)`——获取引用，防止 task_struct 释放
3. `set_bit(KTHREAD_SHOULD_STOP, flags)`——设置停止标志
4. `kthread_unpark(k)`——若 kthread 被 park，先 unpark 唤醒
5. `set_tsk_thread_flag(k, TIF_NOTIFY_SIGNAL)`——打破 `wait_event_interruptible` 等阻塞点（关键！）
6. `wake_up_process(k)`——唤醒 kthread
7. `wait_for_completion(&kthread->exited)`——等待 kthread 调用 `kthread_exit`
8. `ret = kthread->result`——取回 threadfn 返回值
9. `put_task_struct(k)`——释放引用
10. `trace_sched_kthread_stop_ret(ret)`

**AirymaxOS 决策建议**（OS-COG-DEC-03）：CoreLoopThree kthread 主循环模板**必须**为：

```c
while (!kthread_should_stop()) {
    if (kthread_should_park()) {
        clt_save_partial_kv(ctx);  /* 保存半完成 KV 到 MemoryRovol */
        kthread_parkme();          /* 内部 schedule() */
        clt_restore_kv(ctx);       /* unpark 后恢复 */
        continue;
    }
    wait_event_interruptible(ctx->wq,
        condition || kthread_should_stop());
    /* 三阶段循环 */
    clt_perception(ctx);
    clt_thinking(ctx);
    clt_action(ctx);
    cond_resched();
}
return 0;
```

**关键反模式**：长循环不检查 `kthread_should_stop()`——会导致 `kthread_stop` 永久阻塞。

### 2.4 cgroup 与信号处理

**cgroup 归属**（kthread.c）：
- kthreadd（L738-774）：`cgroup_init_kthreadd()`（L749）将 kthreadd 纳入特定 cgroup（通常是根 cgroup 或 system.slice）
- 每个 kthread 在 `kthread()` 主体中 `cgroup_kthread_ready()`（L386）后才开始运行——**默认情况下 kthread 不纳入应用 cgroup**，避免被应用 cgroup 限速策略干扰
- 可选 blkcg 关联：`kthread_associate_blkcg(css)` / `kthread_blkcg()`（kthread.h:L221-226，需 `CONFIG_BLK_CGROUP`）
- `free_kthread_struct`（L130-147）有 `WARN_ON_ONCE(kthread->blkcg_css)`——kthread 退出时必须已解绑 blkcg

**信号处理**：
- kthread 默认不接收信号（`create_kthread` 注释 L410："we take no signals by default"）
- 如需处理特定信号，threadfn 内调用 `allow_signal(sig)`——典型如 `allow_signal(SIGKILL)`
- `kthread_stop` 不靠 SIGKILL，而靠 `TIF_NOTIFY_SIGNAL`（L709）打破阻塞——因此 kthread **不应依赖信号实现停止**
- `kthreadd` 用 `ignore_signals(tsk)`（L744）忽略所有信号
- `PF_NOFREEZE`（L748，kthreadd）——kthreadd 不被 freezer 冻结

**AirymaxOS 决策建议**（OS-COG-DEC-04）：
- CoreLoopThree kthread **不纳入应用 cgroup**（遵循内核默认）——避免应用 cgroup CPU 限速拖垮认知循环
- LLM 推理任务**本身**（用户态进程）纳入 `agent-inference` cgroup，但 CoreLoopThree kthread 不纳入
- kthread **不使用 `allow_signal`**，停止完全靠 `kthread_should_stop()` 协作——避免信号竞态
- kthread 设 `KTW_FREEZABLE`——支持系统休眠/冻结

### 2.5 内存分配与 sched_ext 兼容

**内存分配安全性**（kthread 是进程上下文，可睡眠）：
- `set_kthread_struct`（L111-128）：`kzalloc(sizeof(*kthread), GFP_KERNEL)`——kthread 结构用 GFP_KERNEL
- `__kthread_create_on_node`（L427-478）：`kmalloc(GFP_KERNEL)` + `kvasprintf(GFP_KERNEL)`——创建路径全程 GFP_KERNEL
- **GFP_KERNEL 在 kthread 上下文安全**（process context，允许睡眠、允许 IO）
- **反模式**：kthread 中持自旋锁时调 `GFP_KERNEL`——会睡眠导致死锁；持锁时应 `GFP_ATOMIC`

**sched_ext（SCHED_AGENT）与 kthread 的兼容性**（核对 `kernel/sched/ext.c`）：
1. **`SCX_OPS_SWITCH_PARTIAL` 标志**（ext.c:L127-130）：注释明确"If clear, SCHED_NORMAL tasks are also included"——即**默认（不设该标志）时，SCHED_NORMAL 任务（含 kthread）也被 sched_ext 调度**
2. **PF_KTHREAD 的 CPU 放宽**（ext.c:L2419）：`task_allowed_on_cpu` 中 `if (!(p->flags & PF_KTHREAD) && !task_cpu_possible(cpu, p))`——kthread（PF_KTHREAD）**绕过 user-thread CPU 检查**
3. **sched_ext 自身依赖 kthread**：`scx_create_rt_helper`（ext.c:L5172-5176）用 `kthread_create_worker` 创建 RT helper kthread
4. **per-CPU kthread 与 SCX**：per-CPU kthread（`KTHREAD_IS_PER_CPU`）有 migration 限制，sched_ext 的 `ops.select_cpu()` 不应为它选别的 CPU

**AirymaxOS 决策建议**（OS-COG-DEC-05）：
- CoreLoopThree kthread 用 SCHED_AGENT 策略（sched_ext BPF 策略，调度类编号为 SCHED_EXT=7），**但需注意**：
  - 默认（不设 SCX_OPS_SWITCH_PARTIAL）下，SCHED_NORMAL kthread 也会进 SCX
  - 若 CoreLoopThree kthread 设 SCHED_FIFO/RT（如 drm_sched 那样），则**绕过 sched_ext**（RT 类优先级高于 SCX）
  - **建议**：cognition/execution kthread 用 SCHED_AGENT（经 sched_ext），memory kthread 用 SCHED_NORMAL
- per-CPU 绑定的 CoreLoopThree kthread 不应被 `ops.select_cpu()` 迁移——sub-scheduler `scx_agent` 需识别 `PF_KTHREAD` + `kthread_is_per_cpu`

### 2.6 性能基线

| 指标 | 典型值 | 来源 | 工程含义 |
|------|--------|------|----------|
| `wake_up_process` 唤醒延迟 | 2-5 µs（x86，本地 CPU） | 内核社区 perf 基准 | cognition→execution 切换下限 |
| `wake_up_process` 跨 CPU 唤醒 | 5-15 µs（含 IPI） | 同上 | NUMA 跨节点唤醒更慢 |
| kthread→kthread 上下文切换 | 3-10 µs | 同上 | 避免 user/kernel 切换的核心收益 |
| 用户态→内核态 syscall | ~1 µs | 通用 | kthread 内循环省去此开销 |
| `wait_event_interruptible` 唤醒 | 3-8 µs | 通用 | 事件驱动优于轮询 |
| `kthread_stop` 完整停止 | 10-50 µs（无阻塞时） | 推算 | 含 wake + exit completion |
| drm_sched job 派发 | ~10 µs | drm_sched 实践 | GPU job 调度基线 |

**CoreLoopThree 目标基线**（对齐 NFR-P-001）：
- 认知循环单次 P99 < 100ms（标准场景）/ < 10ms（实时场景）
- kthread 间 io_uring IPC 延迟 < 5µs（零拷贝）
- kthread 上下文切换开销占比应 < 5%（即 < 5ms/100ms）

### 2.7 反模式清单（12 项）

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|----------|
| RP-COG-01 | 主循环不检查 `kthread_should_stop()` | `kthread_stop` 死锁 | 每次循环顶部检查 |
| RP-COG-02 | 长时间忙等（`while(!cond) cpu_relax()`） | 浪费 CPU，阻塞 stop | `wait_event_interruptible` |
| RP-COG-03 | 持自旋锁时 `GFP_KERNEL` | 睡眠致死锁 | 持锁用 `GFP_ATOMIC` |
| RP-COG-04 | kthread 间共享锁竞争 | 优先级反转、活锁 | 用 io_uring 零拷贝解耦 |
| RP-COG-05 | 不 yield 的长循环 | 阻止调度、饿死其他任务 | `cond_resched()` 或 `schedule()` |
| RP-COG-06 | 用 `allow_signal(SIGKILL)` 实现停止 | 信号竞态、与 stop 协议冲突 | 用 `kthread_should_stop()` |
| RP-COG-07 | `kthread_run` 后立即 `kthread_bind` | race（kthread 已跑） | 用 `kthread_create_on_node` + bind + wake |
| RP-COG-08 | 在 `threadfn` 中 `do_exit()` 直接退出 | 绕过 result 传递、资源泄漏 | 用 `kthread_exit(result)` |
| RP-COG-09 | kthread 内 `printk` 大量输出 | log 锁竞争、影响实时性 | 用 ftrace/relay，限速 printk |
| RP-COG-10 | per-CPU kthread 不处理 CPU hotplug | CPU offline 时 kthread 失效 | 用 `kthread_park`/`unpark` hotplug 回调 |
| RP-COG-11 | kthread 创建在 atomic 上下文 | `__kthread_create_on_node` 会睡眠 | 在 process context 创建 |
| RP-COG-12 | 不释放 `kthread_associate_blkcg` 关联 | `WARN_ON_ONCE(blkcg_css)` | 退出前 `kthread_associate_blkcg(NULL)` |

---

## 3. LLM 推理调度最佳实践（行业最新理论 2023-2026）

### 3.1 vLLM PagedAttention 详解

**来源**：vLLM（UC Berkeley，SOSP 2023，"Efficient Memory Management for Large Language Model Serving with PagedAttention"，Kwon et al.），项目 v0.3+（2023-2026 持续演进）。

**核心机制——PagedAttention**：
- 借鉴 OS 虚拟内存分页思想：将 KV cache 划分为固定大小的 **block**（通常 16 token/block），按需分配，而非连续大块
- **Block table**（类比页表）：每个 sequence 维护逻辑 block → 物理 block 的映射，物理 block 可不连续
- 解决传统 KV cache 的**内部碎片**（continuous batching 下 60-80% 浪费）与**外部碎片**
- 内存利用率从 ~40% 提升至 ~96%+，吞吐 2-4x（vs HF Transformers）

**与 Linux 内存管理类比**（AirymaxOS MemoryRovol 协同点）：
- PagedAttention block ≈ Linux 物理页 frame（`struct page`）
- Block table ≈ 进程页表（PML4/PDPT/PD/PT）
- 按 block 分配 ≈ Buddy allocator + SLUB
- **AirymaxOS 增强**：可将 PagedAttention 物理块映射到 MemoryRovol L1-L4 分层——L1（热 KV）驻 DRAM，L2/L3（温）下沉 CXL，L4（冷）落 PMEM，由 MGLRU aging 驱动迁移

**Continuous Batching（迭代级调度）**：
- 传统 static batching：batch 内所有 sequence 必须完成才能加入新 sequence
- Continuous batching（iteration-level）：**每个 decode step 检查**，完成的 sequence 立即移出，新 sequence 加入
- 吞吐提升 2-8x（vs static batching），延迟波动更小

**Prefix Caching（自动前缀缓存）**：
- vLLM v0.4+（2024）引入 Automatic Prefix Caching
- 检测共享 system prompt / few-shot 前缀，缓存其 KV，命中时跳过 prefill
- 缓存粒度：block 级（16 token），LRU 淘汰
- 共享 prompt 场景 KV 计算减少 50%+

### 3.2 SGLang RadixAttention 详解

**来源**：SGLang（UC Berkeley，NeurIPS 2024，"SGLang: Efficient Execution of Structured Language Model Programs"，Zheng et al.），项目 v0.2+（2024-2026）。

**核心机制——RadixAttention**：
- 用 **基数树（Radix Tree）** 索引所有历史 sequence 的 KV cache，按 token 前缀组织
- 新请求到来时，在 radix tree 中**最长前缀匹配**——命中部分直接复用 KV，仅对增量 token prefill
- 比 vLLM 的 block-level prefix caching 更细粒度（token 级前缀共享），且支持**多请求共享中间前缀**
- 缓存淘汰：LRU on radix tree 叶子节点
- 多轮对话场景 SGLang 命中率比 vLLM 高 20-40%

**Constrained Decoding**：SGLang 原生支持 JSON Schema / Regex 约束解码（用 FSM 编译约束）。**AirymaxOS 落地**：Thinkdual System 1（快思考）路径可用约束解码保证结构化输出。

### 3.3 LMCache / Mooncake / Bifrost 详解

**LMCache**（NSDI 2025，"LMCache: Reducing LLM Inference Latency through KV Cache Reuse"，vLLM 团队）：
- **跨请求 KV 复用**：将 KV cache 从"per-request 私有"提升为"集群共享资源"
- **多层缓存**：进程内 → 跨进程（共享内存）→ 跨节点（RDMA/TCP）
- 跨节点共享减少 30%+ 重复推理
- **AirymaxOS 增强**：跨节点 KV 通过 CXL 3.0 Type 3 内存池化共享，延迟从 RDMA ~10µs 降至 CXL ~1µs

**Mooncake**（Moonshot AI，arXiv:2407.00079，2024，"Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving"）：
- **KVCache-centric 架构**：将 KV cache 视为一等公民，独立 **KV cache pool**（全局池）
- **P2P 传输**：节点间 KV 传输用 RDMA/NVLink
- **PD 分离**：Prefill 节点与 Decode 节点物理分离
- **AirymaxOS 落地**：KV cache pool 映射到 MemoryRovol L3（结构层）

**Bifrost**（NVIDIA，2024）：
- **多模态 pipeline 并行**：为多模态 LLM 设计的流水线调度
- 跨模态 encoder/decoder 流水线并行，减少 bubble
- **AirymaxOS 落地**：具身智能多模态感知融合场景

### 3.4 DeepSeek-V3 MLA + DualPipe 详解

**来源**：DeepSeek-V3 Technical Report（2024，DeepSeek-AI）。

**MLA（Multi-head Latent Attention）**：
- 传统 MHA/KV cache：每 head 独立 K、V，KV cache 随 head 数线性增长
- **MLA**：将 K、V **压缩到低秩 latent 向量**，推理时再上投影恢复——KV cache 只存 latent（~1/10 大小），精度近似 MHA
- DeepSeek-V2/V3 实测：KV cache 减少 93%+，长序列吞吐显著提升

**DualPipe**：
- 双向流水线并行（bidirectional pipeline parallelism）：从流水线两端同时注入 micro-batch，减少 bubble
- 相比传统 1F1B / ZB-H2，DualPipe 在同节点 NP×PP 配置下 bubble 最少
- **AirymaxOS 增强**：结合 CoreLoopThree 多 kthread 编排——cognition kthread 跑 prefill DualPipe，execution kthread 跑 decode，memory kthread 异步迁移 KV

### 3.5 Chunked Prefill + Speculative Decoding 详解

**Chunked Prefill**（Sarathi-Serve，OSDI 2024，"Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve"，Agrawal et al.）：
- **问题**：长 prompt prefill 是 compute-bound 的突发负载，期间 decode 请求被阻塞
- **方案**：将长 prompt 拆分为 **chunk**（如 512 token/chunk），与 decode 请求**混合调度**
- **效果**：TTFT 与 TPOT 解耦，吞吐不降，延迟波动大幅降低
- **AirymaxOS 落地**：`llm-scheduler` 的 `batch-scheduler` 实现 chunked prefill，chunk 大小可配（默认 512）

**Speculative Decoding**（Leviathan et al., ICML 2023 "Fast Inference from Transformers via Speculative Decoding"；Chen et al. 2023 "Accelerating LLM Decoding with Speculative Sampling"）：
- **Draft model + Target model**：小模型（draft）快速生成 k 个候选 token，大模型（target）并行验证
- **接受率（acceptance ratio）**：典型 50-80%
- **无损失加速**：输出分布与 target model 完全一致
- **加速比**：1.5-3x
- **AirymaxOS 落地**：Thinkdual System 1（快思考）用 draft model 投机，System 2（慢思考）用 target model 验证——投机解码天然契合双思考架构！

### 3.6 PD-Disaggregation 详解

**来源**：DistServe（OSDI 2024，"DistServe: Disaggregating Prefill and Decoding for Goodput-optimized LLM Serving"，Zhong et al.），Mooncake。

**核心思想**：Prefill 与 Decode 计算特征迥异，应物理分离到不同节点。

| 阶段 | 计算特征 | 瓶颈 | 适合硬件 |
|------|----------|------|----------|
| Prefill | compute-bound（GEMM 密集） | FLOPS | H100/A100（高 FLOPS） |
| Decode | memory-bandwidth-bound（每 step 取全 KV） | HBM 带宽 | 低显存高带宽卡 / CXL 内存 |

**AirymaxOS 落地**：
- CoreLoopThree cognition kthread（prefill）与 execution kthread（decode）可跨 NUMA/跨节点部署
- KV 传输走 CXL 3.0 或 io_uring zero-copy

### 3.7 Token 能效指标体系

**核心指标**（对齐 `agentrt_token_efficiency_t` [SC]）：

| 指标 | 定义 | 单位 | 目标 |
|------|------|------|------|
| **TTFT**（Time To First Token） | 请求到首 token 延迟 | ms | < 200ms（标准） |
| **TPOT**（Time Per Output Token） | decode 阶段单 token 延迟 | ms | < 20ms |
| **E2E Latency** | 请求总延迟 | ms | P99 < 100ms（NFR-P-001） |
| **Throughput** | 系统吞吐 | token/s | — |
| **Token/s/W**（能效） | 单位功耗 token 产率 | token/s/W | +25%（NFR-P-004） |
| **Token/J**（能量效率） | 单位能量 token 数 | token/J | — |
| **Cache hit rate** | KV cache 命中率 | % | > 50% |
| **Speculative accept rate** | 投机接受率 | % | > 60% |
| **Goodput** | 满足 SLA 的有效吞吐 | token/s | DistServe 核心 |

**AirymaxOS 工程建议**：
- `token_efficiency_record()` [SS] 由内核 ftrace 采集
- 指标通过 OpenTelemetry span 暴露
- Token/J 指标需结合 RAPL（Running Average Power Limit）读取 CPU/GPU 能耗

---

## 4. GPU/NPU 调度最佳实践

### 4.1 NVIDIA MPS / MIG / GDS

**CUDA MPS（Multi-Process Service）**：
- 允许多进程共享同一 GPU 的 compute context
- 提升小 kernel 多租户场景 GPU 利用率
- 限制：共享 context 无硬件隔离

**NVIDIA MIG（Multi-Instance GPU）**：
- **硬件级** GPU 切分（A100/H100）：一张卡切 1/2/3/4/7 个 instance
- 真正硬件隔离（fault isolation），适合多租户/安全场景
- H100 最多 7 个 instance
- **AirymaxOS**：`gpu-npu/mig` 模块封装 MIG 配置，按 Agent 租户分配 instance

**NVIDIA GDS（GPUDirect Storage）**：
- GPU 显存 ↔ 存储设备**直接 DMA**，bypass CPU 主存
- 适合大模型权重加载、KV checkpoint 持久化
- **AirymaxOS**：`super-node-sandbox` 快照恢复用 GDS 加速

**TensorRT-LLM**（NVIDIA 2023-2026）：
- **In-flight batching**：continuous batching 的 NVIDIA 实现
- **KV cache 重用**：跨 request 复用
- **FP8/FP4 量化**（Hopper/Blackwell）：吞吐 2-4x

### 4.2 AMD ROCm MPS

- 类似 CUDA MPS，多进程共享 GPU compute
- ROCm 5.0+ 支持，MI200/MI300 系列
- 与 vLLM/SGLang ROCm 后端兼容
- **AirymaxOS**：`gpu-npu/mps` 抽象层统一 NVIDIA MPS 与 ROCm MPS

### 4.3 国产加速器（昇腾/寒武纪/海光）

**华为昇腾 CANN**：
- Ascend 910B（训练）/ 310P（推理），CANN 软件栈
- MindIE（推理引擎）支持 continuous batching
- 达卡算力 256 TFLOPS（FP16，910B）
- **AirymaxOS**：`gpu-npu/npu-scheduler` 通过 `drivers/accel/` 统一接入

**寒武纪 MLU**（Cambricon NeuWare）：
- MLU370/590 系列，NeuWare 软件栈
- 支持 INT8/INT16 量化推理

**海光 DCU**（DTK，Data Center Unit）：
- 兼容 ROCm/HIP 生态，DTK 工具链
- **AirymaxOS**：复用 ROCm MPS 抽象

**统一接入原则**：国产加速器经 OLK-6.6 `drivers/accel/`（habanalabs/ivpu/qaic 已有范例）统一接入，`agentrt_accel_capabilities_t` [SC] 描述能力，调度器按描述符抽象调度。

### 4.4 DRM 调度器（drm_sched）

**来源**：OLK-6.6 `drivers/gpu/drm/scheduler/`，逐行核对。

**架构**：
- **`drm_gpu_scheduler`**：每 GPU 一个调度器实例，由 `drm_sched_init()`（sched_main.c:L1095）创建
- **创建方式**：`sched->thread = kthread_run(drm_sched_main, sched, sched->name)`（sched_main.c:L1123）
- **调度器主循环**（`drm_sched_main`，sched_main.c:L1015-1048）：
  - `sched_set_fifo_low(current)`——SCHED_FIFO prio=1
  - `while (!kthread_should_stop())`——协作式停止
  - `wait_event_interruptible` + 三条件（cleanup / entity ready / stop）——事件驱动
  - 调度实体（entity）：每进程/每上下文一个 entity
  - 调度策略：Round-Robin / FIFO
  - fence 同步：`drm_sched_fence` 提供依赖与完成信号

**AirymaxOS 工程启示**（drm_sched 是 GPU 调度 kthread 的范例）：
- 用 `kthread_run`（创建即跑）适合——GPU 调度器生命周期与设备一致
- `sched_set_fifo_low`——RT 低优先级，不抢关键 RT 任务
- `wait_event_interruptible` + 三条件——事件驱动，不忙等
- `kthread_should_stop()` 协作停止
- **CoreLoopThree kthread 应借鉴此模板**：`sched_set_fifo_low` 改为 SCHED_AGENT（经 sched_ext），主循环结构同构

### 4.5 CXL 3.0 内存池化

**来源**：CXL 3.0 Spec（2022，Compute Express Link），Linux 6.6 `drivers/cxl/`（OLK-6.6 已纳入）。

**核心能力**：
- **Type 3 设备**：内存扩展器（memory expander），host 可访问扩展内存（DRAM/PMEM 混合）
- **CXL 3.0 多级交换**：支持 fabric 拓扑，跨 switch 内存池化，多 host 共享内存设备
- **缓存一致**：host 与 device 间 cache coherence

**LLM 推理加速应用**：
- **KV cache 池化**：Mooncake 风格 KV pool 落到 CXL Type 3 内存，多节点共享——跨节点 KV 传输延迟从 RDMA ~10µs 降至 CXL ~1µs
- **Decode 节点扩展内存**：Decode 是 memory-bandwidth-bound，CXL 内存扩展 HBM 不足
- **PD 分离的 KV 桥**：prefill 节点 → CXL 内存 → decode 节点，零拷贝

**AirymaxOS 增强**：
- 结合 MemoryRovol L3（结构层）：L3 关系图数据放 CXL 共享内存，多 Agent 协同图遍历
- `kv-cache-aware` 调度器识别 CXL 内存 tier，热 KV 驻 HBM/本地 DRAM，温 KV 驻 CXL

### 4.6 DPU/IPU 卸载

**NVIDIA BlueField DPU**：
- 独立 ARM 核 + 网卡 + 可编程加速，卸载网络/存储/安全
- vDPA、OVS offload、存储虚拟化卸载
- **LLM 场景**：KV cache 跨节点传输用 BlueField RDMA 卸载，CPU 不参与

**Intel IPU（Infrastructure Processing Unit）**：
- 类似 DPU，Intel 实现
- 与 oneAPI 协同

**AirymaxOS 落地**：`super-node-sandbox` 跨节点迁移、KV pool P2P 传输可卸载到 DPU，CoreLoopThree kthread 不感知

### 4.7 CPU 侧 LLM 推理加速

**Intel AMX（Advanced Matrix Extensions）**：
- Sapphire Rapids+ 内置矩阵乘加速（TMUL：tile multiply）
- BF16/INT8 矩阵乘，适合 prefill GEMM
- Linux 6.6 已支持 AMX 调度

**Intel AVX-512**：
- VNNI（Vector Neural Network Instructions）：INT8 GEMM
- BF16 推理加速

**AirymaxOS 落地**：`llm-scheduler` 识别 CPU AMX/AVX-512 能力，小模型 / draft model 投机解码跑 CPU 侧

---

## 5. AirymaxOS 采纳决策建议

### 5.1 决策项清单（24 项）

决策标注：**A**=采纳 / **NA**=不采纳 / **E**=增强 / **I**=独立（依赖闭源/厂商）/ **NA-OS**=不适配（路径独立）

| # | 决策项 | 来源 | 决策 | 关联 IRON / 子仓 |
|---|--------|------|------|------------------|
| OS-COG-DEC-01 | kthread_create_on_node + NUMA 感知 | OLK-6.6 kthread.c:L503 | A | cognition [IND] |
| OS-COG-DEC-02 | kthread_bind CPU 亲和性 | OLK-6.6 kthread.c:L554 | A | cognition [IND] |
| OS-COG-DEC-03 | kthread_should_stop 协作式停止 | OLK-6.6 kthread.c:L156 | A | cognition [IND] |
| OS-COG-DEC-04 | kthread_should_park 驻留协议 | OLK-6.6 kthread.c:L178 | A | cognition [IND] |
| OS-COG-DEC-05 | kthread 与 sched_ext 隔离（SCHED_AGENT） | OLK-6.6 ext.c:L127/2419 | A | cognition+sched [SS] |
| OS-COG-DEC-06 | kthread 不纳入应用 cgroup | OLK-6.6 kthread.c:L386 | A | cognition [IND] |
| OS-COG-DEC-07 | drm_sched 模板（kthread+wait_event+stop） | OLK-6.6 sched_main.c:L1015 | A | gpu-npu [IND] |
| OS-COG-DEC-08 | vLLM PagedAttention | SOSP 2023 | E | llm-scheduler [SS] |
| OS-COG-DEC-09 | vLLM Continuous Batching | SOSP 2023 | A | llm-scheduler [SS] |
| OS-COG-DEC-10 | SGLang RadixAttention | NeurIPS 2024 | A | llm-scheduler [SS] |
| OS-COG-DEC-11 | LMCache KV 跨节点复用 | NSDI 2025 | E | token-efficiency [IND] |
| OS-COG-DEC-12 | Mooncake PD 分离 + KV pool | arXiv:2407.00079 | A | llm-scheduler [IND] |
| OS-COG-DEC-13 | DeepSeek-V3 MLA | DeepSeek-V3 TR 2024 | A | llm-scheduler [SS] |
| OS-COG-DEC-14 | DeepSeek-V3 DualPipe | DeepSeek-V3 TR 2024 | E | gpu-npu [IND] |
| OS-COG-DEC-15 | Chunked Prefill（Sarathi） | OSDI 2024 | A | llm-scheduler [SS] |
| OS-COG-DEC-16 | Speculative Decoding | ICML 2023 | A | thinkdual [SS] |
| OS-COG-DEC-17 | NVIDIA MIG | NVIDIA | I | gpu-npu [IND] |
| OS-COG-DEC-18 | AMD ROCm MPS | AMD | I | gpu-npu [IND] |
| OS-COG-DEC-19 | 国产加速器（昇腾/寒武纪/海光） | CANN/NeuWare/DTK | I | gpu-npu [IND] |
| OS-COG-DEC-20 | CXL 3.0 内存池化 | CXL 3.0 Spec + OLK-6.6 | E | memory+cognition [IND] |
| OS-COG-DEC-21 | Intel AMX/AVX-512 | Intel + OLK-6.6 | A | llm-scheduler [IND] |
| OS-COG-DEC-22 | DPU/IPU 卸载 | NVIDIA BlueField / Intel IPU | A（可选） | super-node [IND] |
| OS-COG-DEC-23 | Apple Metal Performance Shaders | Apple | NA-OS | — |
| OS-COG-DEC-24 | kthread_run 标准创建模式 | OLK-6.6 kthread.h:L51 | A | cognition [IND] |

### 5.2 增强项工程化建议

**OS-COG-DEC-08 PagedAttention + MemoryRovol L1-L4 增强**：
- L1（原始卷，DRAM）：当前请求活跃 KV，PagedAttention block 表索引
- L2（特征层，DRAM/CXL）：近期完成请求 KV，RadixAttention 前缀树索引，MGLRU aging 监控
- L3（结构层，CXL 共享）：跨 Agent 共享 KV，多节点 graph 遍历
- L4（模式层，PMEM 持久化）：冷 KV 持久化，断电不丢失，跨节点恢复
- 迁移触发：MGLRU aging → L1→L2，CXL bandwidth 监控 → L2→L3，PMEM 容量水位 → L3→L4
- 迁移机制：userfaultfd 缺页处理 + io_uring 异步拷贝

**OS-COG-DEC-11 LMCache + CXL 增强**：
- 跨节点 KV 复用走 CXL 3.0 fabric（多级 switch 拓扑），延迟 < 1µs
- KV block 在 CXL 内存以 PagedAttention block 格式存储，复用时零拷贝映射到目标节点页表
- 一致性：CXL cache coherence 保证（Type 3 + CXL.cache）

**OS-COG-DEC-14 DualPipe + CoreLoopThree 增强**：
- DualPipe 的双向注入映射到 cognition kthread 双向流水线
- micro-batch 粒度对齐 CoreLoopThree cycle（每 cycle 一个 micro-batch）
- bubble 期间 memory kthread 异步迁移 KV 到 decode 节点

**OS-COG-DEC-20 CXL + MemoryRovol 增强**：
- L3 关系图数据放 CXL 共享内存，多 Agent 协同图遍历（零拷贝）
- `gpu-npu` 调度器识别 CXL tier，热路径 KV 强制驻本地 HBM/DRAM

---

## 6. CoreLoopThree 工程化建议

### 6.1 三阶段 kthread 编排建议

**对齐 `01-cognition-flow.md` §4 三 kthread 分工**，基于 OLK-6.6 kthread 机制的编排建议：

| kthread | 创建方式 | 调度策略 | CPU 亲和 | NUMA | 停止协议 |
|---------|----------|--------|----------|------|----------|
| `coreloop_cognition_kthread` | kthread_create_on_node(GPU node) + wake | SCHED_AGENT 高 | GPU/NPU 所在 NUMA CPU | 是 | kthread_should_stop + park |
| `coreloop_execution_kthread` | kthread_create_on_node + wake | SCHED_AGENT 中 | 同上或独立 | 是 | 同上 |
| `coreloop_memory_kthread` | kthread_create_on_node + wake | SCHED_NORMAL 低 | 任意（可迁移） | 否 | 同上 |

**主循环模板**（基于 drm_sched `sched_main.c:L1015` + kthread 反模式清单）：

```c
static int coreloop_cognition_kthread(void *data)
{
    struct clt_ctx *ctx = data;
    sched_setparam(current, &(struct sched_param){.sched_priority = CLT_HIGH_PRIO});
    /* 或经 sched_ext 设 SCHED_AGENT */
    
    while (!kthread_should_stop()) {
        if (kthread_should_park()) {
            clt_save_partial_kv(ctx);  /* 保存半完成 KV 到 MemoryRovol */
            kthread_parkme();
            clt_restore_kv(ctx);       /* unpark 后恢复 */
            continue;
        }
        /* 事件驱动等待，避免忙等（反模式 RP-COG-02） */
        wait_event_interruptible(ctx->wq,
            clt_has_pending(ctx) || kthread_should_stop_or_park());
        if (kthread_should_stop_or_park()) continue;
        
        /* 三阶段循环 */
        clt_perception(ctx);   /* 感知：多模态输入采集 */
        clt_thinking(ctx);     /* 思考：LLM 推理（io_uring 提交至 System 2） */
        clt_action(ctx);       /* 行动：执行决策 */
        
        cond_resched();  /* 反模式 RP-COG-05：主动让出 */
    }
    return 0;
}
```

**关键工程要点**：
- 创建顺序：`kthread_create_on_node` → `kthread_bind`（若 per-CPU）→ `sched_setparam` → `wake_up_process`（避免反模式 RP-COG-07 race）
- 三 kthread 通过 io_uring 零拷贝 IPC，避免共享锁（反模式 RP-COG-04）
- trace_id 贯穿三 kthread，OpenTelemetry span 嵌套

### 6.2 Thinkdual 切换时机建议

| 切换方向 | 触发条件 | kthread 行为 |
|----------|----------|--------------|
| System 1 → System 2 | complexity_score ≥ 0.3 | cognition kthread 通过 io_uring 提交至 System 2（慢思考） |
| System 2 → System 1 | 任务完成 / 降级 | 切回 System 1 快速响应 |
| Speculative（投机）| System 1 draft 生成 | target model（System 2）并行验证，accept 则继续，reject 则回退 |

**与 Speculative Decoding 协同**（OS-COG-DEC-16）：
- System 1（draft model）生成 k 个候选 token——低延迟，CPU/小 GPU
- System 2（target model）并行验证——高准确度，大 GPU
- 接受率 > 60% 时，整体延迟降至 System 2 单跑的 1/2-1/3
- `speculative_accept_rate` 由 ftrace 采集

**切换延迟目标**：System 1→2 切换 < 1ms（共享内核态内存零拷贝）

### 6.3 LLM 推理调度器集成建议

**`llm-scheduler` 模块集成清单**：

| 子模块 | 采纳决策 | 实现要点 |
|--------|----------|----------|
| `inference-aware` | OS-COG-DEC-09 continuous batching | execution kthread 每 decode step 唤醒调度 |
| `kv-cache-aware` | OS-COG-DEC-08 PagedAttention + OS-COG-DEC-13 MLA | block 表 + latent 压缩，L1-L4 分层 |
| `batch-scheduler` | OS-COG-DEC-15 chunked prefill | chunk 默认 512，与 decode 混合 |
| `prefill-decode` | OS-COG-DEC-12 Mooncake PD 分离 | cognition（prefill）↔ execution（decode）跨节点 |
| `speculative-decoding` | OS-COG-DEC-16 | System 1 draft + System 2 target |
| RadixAttention 索引 | OS-COG-DEC-10 | token 级前缀树，L2 特征层共享存储 |
| LMCache 跨节点 | OS-COG-DEC-11 | CXL 共享内存，L4 PMEM 持久化 |

### 6.4 GPU/NPU 池化建议

**`gpu-npu` 模块集成清单**：

| 子模块 | 采纳决策 | 实现要点 |
|--------|----------|----------|
| `gpu-scheduler` | OS-COG-DEC-07 drm_sched 模板 | kthread + wait_event + kthread_should_stop，调度策略换 SCHED_EXT（加载 SCHED_AGENT BPF 策略） |
| `npu-scheduler` | OS-COG-DEC-19 drivers/accel/ | 国产加速器统一接入 |
| `mps` | OS-COG-DEC-17/18 | NVIDIA MPS / ROCm MPS 抽象统一 |
| `mig` | OS-COG-DEC-17 | MIG instance 分配，按租户 |
| `pooling` | OS-COG-DEC-12 + OS-COG-DEC-20 | 跨设备/跨节点调度，CXL 内存池 |

**池化调度策略**：
- 按 `agentrt_accel_capabilities_t` [SC] 描述符匹配任务与设备
- prefill 任务优先分到高 FLOPS 设备（H100/A100），decode 任务优先分到高带宽设备（CXL 扩展内存）
- 故障切换：设备失效时迁移到 pool 中备用设备，KV 从 CXL pool 恢复

---

## 7. Euler 兼容性声明

AirymaxOS 认知子系统的工程思想与实现方式与 Euler 保持一致性，以便未来兼容 Euler 标准的发行版工具链：

| 维度 | Euler 标准 | AirymaxOS 实现 | 兼容性 |
|------|-----------|----------------|--------|
| kthread 创建协议 | `kthread_create_on_node` + `wake_up_process` | 同源协议（[IND] 独立实现） | ✅ 兼容 |
| kthread 停止协议 | `kthread_should_stop` + `kthread_stop`（TIF_NOTIFY_SIGNAL） | 同源协议 | ✅ 兼容 |
| kthread 驻留协议 | `kthread_park` + `kthread_unpark` | 同源协议 | ✅ 兼容 |
| 加速器接入 | `drivers/accel/`（habanalabs/ivpu/qaic） | 参考设计（[IND] 独立实现） | ✅ 兼容 |
| GPU 调度器 | `drm_sched`（kthread + wait_event + fifo_low） | 参考模板（[IND] 独立实现） | ✅ 兼容 |
| 模块化 | `CONFIG_DRM_ACCEL` / `CONFIG_DRM_GPU_SCHED` | 同源 Kconfig 风格 | ✅ 兼容 |
| 调度策略 | SCHED_NORMAL / SCHED_FIFO / SCHED_EXT | 复用 SCHED_EXT=7，SCHED_AGENT 为 BPF 策略名 | ✅ 兼容 |

**代码共享边界澄清**（IRON-9 v2）：
- agentrt ↔ AirymaxOS：[SC] 共享契约层完全共享代码（`include/airymax/cognition_types.h`）
- AirymaxOS ↔ OLK-6.6/Euler：**仅技术参考，不共享代码**——OLK-6.6 的 kthread.c/accel.c/sched_main.c 是 AirymaxOS [IND] 独立层的实现参考
- AirymaxOS 工程思想与 Euler 一致性体现在协议层（创建/停止/驻留协议）和接入层（accel/drm_sched 模式），不体现在代码层

---

## 8. 相关文档

- [认知模块设计](../../docs/AirymaxOS/20-modules/05-cognition.md)：CoreLoopThree + Thinkdual + LLM 调度（开源）
- [认知循环数据流](../../docs/AirymaxOS/40-dataflows/01-cognition-flow.md)：12 步数据流 + IRON-9 v2 三层标注（开源）
- [认知子系统源码映射](../02-olk66-source-mapping/06-cognition-mapping.md)：38 条 OS-COG-MAP 规则
- [调度子系统技术规范](01-scheduler-spec.md)：sched_ext + SCHED_AGENT
- [内存子系统技术规范](04-memory-spec.md)：MemoryRovol + CXL + PMEM
- [安全子系统技术规范](05-security-spec.md)：capability + LSM
- [IRON-9 v2 三层共享模型定义](../../docs/AirymaxOS/50-engineering-standards/README.md)

---

## 9. 附录 A：OLK-6.6 源码引用索引

| 引用 | 文件:行号 | 内容 |
|------|-----------|------|
| kthread.h:L11-14 | kthread_create_on_node 声明 | NUMA 感知创建原语 |
| kthread.h:L27-28 | kthread_create 宏 | = create_on_node(NUMA_NO_NODE) |
| kthread.h:L51-58 | kthread_run 宏 | create + wake_up_process |
| kthread.h:L72-83 | kthread_run_on_cpu | per-CPU 即启动 |
| kthread.h:L221-226 | kthread_associate_blkcg | blkcg 关联 |
| kthread.c:L68-72 | KTHREAD_BITS 枚举 | IS_PER_CPU/SHOULD_STOP/SHOULD_PARK |
| kthread.c:L111-128 | set_kthread_struct | kzalloc GFP_KERNEL |
| kthread.c:L130-147 | free_kthread_struct | blkcg_css WARN |
| kthread.c:L156-160 | kthread_should_stop | test_bit |
| kthread.c:L178-192 | kthread_should_park/_or_park | 协作驻留 |
| kthread.c:L312-338 | kthread_exit/_complete_and_exit | 显式退出 |
| kthread.c:L340-391 | kthread 主体 | SCHED_NORMAL reset + housekeeping + cgroup_ready |
| kthread.c:L394-401 | tsk_fork_get_node | NUMA fork node |
| kthread.c:L403-425 | create_kthread | kernel_thread CLONE_FS\|CLONE_FILES\|SIGCHLD |
| kthread.c:L427-478 | __kthread_create_on_node | kmalloc GFP_KERNEL + wait_for_completion_killable |
| kthread.c:L503-517 | kthread_create_on_node | NUMA 节点参数 |
| kthread.c:L519-538 | __kthread_bind/_mask | do_set_cpus_allowed + PF_NO_SETAFFINITY |
| kthread.c:L540-558 | kthread_bind_mask/bind | CPU 亲和 |
| kthread.c:L570-584 | kthread_create_on_cpu | create_on_node + bind |
| kthread.c:L587-611 | kthread_set/is_per_cpu | per-CPU 标记 |
| kthread.c:L621-640 | kthread_unpark | re-bind + wake_up_state |
| kthread.c:L654-681 | kthread_park | SHOULD_PARK + wait_for_completion(parked) |
| kthread.c:L698-718 | kthread_stop | 完整停止序列 |
| kthread.c:L738-774 | kthreadd | ignore_signals + PF_NOFREEZE + cgroup_init_kthreadd |
| ext.c:L127-130 | SCX_OPS_SWITCH_PARTIAL | SCHED_NORMAL 是否纳入 SCX |
| ext.c:L908 | scx_ops_helper | sched_ext 自身用 kthread_worker |
| ext.c:L2419 | task_allowed_on_cpu | PF_KTHREAD 绕过 CPU 检查 |
| ext.c:L5172-5176 | scx_create_rt_helper | sched_ext 用 kthread_create_worker |
| sched_main.c:L1015-1048 | drm_sched_main | GPU 调度 kthread 范例 |
| sched_main.c:L1020 | sched_set_fifo_low | SCHED_FIFO prio=1 |
| sched_main.c:L1095/1123 | drm_sched_init | kthread_run(drm_sched_main) |

## 10. 附录 B：行业论文/项目引用索引

| 引用 | 来源 | 应用决策 |
|------|------|----------|
| PagedAttention | vLLM, SOSP 2023, Kwon et al. | OS-COG-DEC-08 |
| Continuous Batching | vLLM v0.3+, 2023-2026 | OS-COG-DEC-09 |
| RadixAttention | SGLang, NeurIPS 2024, Zheng et al. | OS-COG-DEC-10 |
| Constrained Decoding | SGLang, 2024 | Thinkdual System 1 |
| LMCache | NSDI 2025, vLLM 团队 | OS-COG-DEC-11 |
| Mooncake | arXiv:2407.00079, Moonshot AI, 2024 | OS-COG-DEC-12 |
| Bifrost | NVIDIA, 2024 | 多模态 pipeline |
| MLA | DeepSeek-V3 Technical Report, 2024 | OS-COG-DEC-13 |
| DualPipe | DeepSeek-V3 Technical Report, 2024 | OS-COG-DEC-14 |
| Sarathi/Chunked Prefill | OSDI 2024, Agrawal et al. | OS-COG-DEC-15 |
| Speculative Decoding | ICML 2023, Leviathan et al.; Chen et al. 2023 | OS-COG-DEC-16 |
| DistServe/PD-Disagg | OSDI 2024, Zhong et al. | OS-COG-DEC-12 |
| S-LoRA | SOSP 2023 | Multi-LoRA |
| CUDA MPS / MIG / GDS | NVIDIA 文档 | OS-COG-DEC-17/22 |
| ROCm MPS | AMD 文档 | OS-COG-DEC-18 |
| CXL 3.0 Spec | CXL Consortium 2022 + OLK-6.6 drivers/cxl/ | OS-COG-DEC-20 |
| AMX/AVX-512 | Intel + OLK-6.6 arch/x86/ | OS-COG-DEC-21 |
| Kahneman "Thinking, Fast and Slow" | Kahneman | Thinkdual 理论根基 |
| Liedtke minimality | SOSP 1995 | 微内核机制/策略分离 |

---

## 11. 文档变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|---|---|---|---|
| 0.1.1 | 2026-07-07 | 初始版本，基于 OLK-6.6 kthread/accel/drm_sched + 行业最新 LLM 推理理论，制定 24 项 OS-COG-DEC 采纳决策 + 12 项反模式 + CoreLoopThree 工程化建议 | Airymax 架构委员会 |

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
"From data intelligence emerges."
