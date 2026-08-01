SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 11 — 时间/定时器（v3.6b 深度对比）

> **文档定位**：agentrt-linux 内核设计深度对比研究 · 第二轮 · 维度 3
> **对比基准**：openEuler kernel-OLK-6.6 · seL4-master · Airymax agentrt-linux
> **最后更新**：2026-07-31
> **方法论**：逐字节阅读三项目源码，所有引用标注文件路径+行号，严禁编造

---

## 0. 摘要

本报告对比三项目的时间服务与定时器机制。openEuler 提供完整的 `hrtimer` 高精度定时器框架（struct hrtimer + hrtimer_init + hrtimer_start + 回调机制）；seL4 通过 arch-specific `initTimer` 驱动 tick，配合 [sporadic.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/sporadic.c) 的 refill scheduling 实现 per-SC budget/period 周期补给；Airymax 的 [airy_time.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/time/airy_time.c) 仅 33 行，提供 `ktime_get_ns` wrapper 和溢出安全的 deadline 加法，**无 hrtimer 封装、无 per-agent 时间配额、无超时唤醒机制**。核心发现：N5（agent 超时唤醒缺失）。

---

## 1. 对比基准

### 1.1 openEuler OLK-6.6 hrtimer 框架

openEuler 沿用 Linux hrtimer 高精度定时器框架：

| 要素 | 位置 | 行号 | 说明 |
|------|------|------|------|
| `struct hrtimer` | [hrtimer.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/hrtimer.h) | L119 | 定时器结构体（含 node、function 回调、base 指针） |
| `hrtimer_init` | hrtimer.h | L385 | 初始化定时器（指定 clockid） |
| `hrtimer_start` | hrtimer.h | L428 | 启动/重启定时器（inline，调 `__hrtimer_start_range_ns`） |

**特征**：hrtimer 基于 rbtree 组织，由 per-CPU `hrtimer_cpu_base` 管理；到期触发 `function` 回调（硬中断上下文或软中断，取决于 mode）；支持 `HRTIMER_MODE_ABS`/`REL`/`PINNED` 等。`ktime_get_ns()` 提供单调纳秒时间戳（timekeeping.c）。

### 1.2 seL4 时间与定时器

seL4 时间机制分两层：

**硬件层**（arch-specific）：[src/drivers/timer/generic_timer.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/drivers/timer/generic_timer.c)

| 函数 | 行号 | 作用 |
|------|------|------|
| `initGenericTimer` | L9 | 初始化通用定时器（ARM generic timer） |
| `resetTimer` | L30 | 重置定时器计数 |
| `initTimer` | L44 | 设置下一次定时器中断（设置 compare 寄存器） |

**内核层**（budget 调度）：[src/kernel/sporadic.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/sporadic.c) 实现 Scheduling Context（SC）的 sporadic budget 补给：

| 要素 | 行号 | 作用 |
|------|------|------|
| `refill_next` | L35 | 取 refill 队列下一项 |
| `refill_ordered` | L65 | 校验 refill 队列按时间有序 |
| refill scheduling | L12 注释 | "sporadic budget replenishments (refills for short)" |

**机制**：每个 SC 有 budget/period，内核按 period 周期性向 refill 队列补给 budget；`initTimer` 设置下一次 tick 中断，tick 到达后 `schedule` 选择可运行线程并消耗其 SC budget；budget 耗尽则线程被挂起直到下次 refill。这实现了**per-SC 时间配额与超时唤醒**。

### 1.3 Airymax 时间服务

[airy_time.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/time/airy_time.c) 全文 33 行，两个函数：

| 函数 | 行号 | 实现 |
|------|------|------|
| `airy_time_now_ns` | L18 | L20 `return ktime_get_ns();` |
| `airy_time_deadline_ns` | L24 | L29 `check_add_overflow(base, delta, &deadline)` 溢出保护，L30 溢出返回 `U64_MAX` |

**特征**：纯整数运算（无浮点，符合 ALK 约束，L8 注释）；`check_add_overflow` 是 Linux 提供的编译器内置溢出检测，正确可靠；但**无 hrtimer 封装、无 timer 回调注册、无 per-agent deadline 调度**。

---

## 2. 三方对比

| 维度 | openEuler | seL4 | Airymax |
|------|-----------|------|---------|
| 时间戳获取 | `ktime_get_ns` (timekeeping.c) | arch timer counter | `airy_time_now_ns` = `ktime_get_ns` (airy_time.c L20) |
| 定时器抽象 | `struct hrtimer` (hrtimer.h L119) | arch `initTimer` (generic_timer.c L44) | 无 |
| 定时器回调 | `hrtimer_start` + function (hrtimer.h L428) | tick → schedule | 无 |
| per-agent 配额 | 无（CFS vruntime） | SC budget/period + refill (sporadic.c) | 无 |
| 超时唤醒 | hrtimer 回调唤醒 wait_queue | SC refill 唤醒线程 | 无 |
| deadline 算术 | ktime_add_safe | refill 时间计算 | `airy_time_deadline_ns` 溢出保护 (airy_time.c L29) |
| 溢出保护 | ktime_add_safe | — | `check_add_overflow` (airy_time.c L29) ✅ |

---

## 3. 关键发现

### 3.1 【发现 1】无 hrtimer 封装，agent 超时唤醒机制缺失

**现状**：[airy_time.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/time/airy_time.c) 仅提供 `now_ns` 和 `deadline_ns`，无任何定时器注册/启动/回调机制。Airymax 的 agent 模型需要超时唤醒（如 agent 等待 IPC 超时、budget 耗尽、watchdog），但当前无机制将 deadline 转化为实际的定时器中断。

**参考**：
- openEuler [hrtimer.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/hrtimer.h) L119 `struct hrtimer` + L428 `hrtimer_start` 提供 complete 定时器框架，agent 可注册回调在指定 deadline 触发。
- seL4 [sporadic.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/sporadic.c) L12/L35/L65 的 refill scheduling 实现 per-SC budget 配额，`initTimer`（generic_timer.c L44）驱动 tick，budget 耗尽挂起线程、refill 唤醒。

**风险**：第一轮报告 01 指出 Airymax 缺少 CBS 带宽准入（P2-1）和 SC 捐赠（P2-3）；本报告补充更基础的缺口——连"超时唤醒"原语都不存在。M2 IPC 集成若需要 IPC 超时（seL4 的 `TimeTrigger` / openEuler 的 `schedule_timeout`），当前无底层支撑。

**建议**：M2 前实现 `airy_timer_arm(deadline, callback, agent_id)` 封装 hrtimer，最小可用：
1. `airy_timer_init` 封装 `hrtimer_init`（CLOCK_MONOTONIC）
2. `airy_timer_arm` 封装 `hrtimer_start`，回调中调用 agent 唤醒路径
3. `airy_timer_cancel` 封装 `hrtimer_cancel`
对应 N5。

**优先级**：P1 · 工作量 6h · 风险中（回调在硬中断上下文，需注意锁）

### 3.2 【发现 2】deadline 算术设计正确，可复用

**现状**：[airy_time.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/time/airy_time.c) L29 `check_add_overflow(base, delta, &deadline)` 是本轮少数实现正确的溢出保护，L30 溢出返回 `U64_MAX` 语义清晰。

**参考**：openEuler `ktime_add_safe` 同样做溢出保护（返回 KTIME_MAX）。

**评价**：这是 Airymax 的正面发现。`check_add_overflow` 利用编译器内置（GCC/Clang `__builtin_add_overflow`），比手写 `if (a + b < a)` 更可靠。建议后续 hrtimer 封装复用 `airy_time_deadline_ns` 计算 timer expires。

**优先级**：无需改进（记录为正面发现）

---

## 4. 改进点清单

| 编号 | 标题 | 优先级 | 现状行号 | 工作量 |
|------|------|--------|----------|--------|
| N5 | 无 hrtimer 封装，agent 超时唤醒缺失 | P1 | [airy_time.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/time/airy_time.c) L18-33 | 6h |
| — | deadline 算术溢出保护正确（正面发现） | — | [airy_time.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/time/airy_time.c) L29 | — |

---

## 5. 小结

airy_time.c 的 `check_add_overflow` 用法正确，是本轮正面发现。但"时间服务"仅停留在时间戳读取+算术层面，缺失定时器这一时间维度的核心原语。seL4 的 SC refill scheduling 是 Airymax agent budget 模型的目标形态（与第一轮 P2-1/P2-3 呼应），而 hrtimer 封装是实现该形态的必要前置。建议 M2 前补齐 `airy_timer_arm/cancel` 最小封装。
