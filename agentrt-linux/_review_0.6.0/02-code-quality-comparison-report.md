Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agentrt vs OLK-6.6 代码品质对比分析报告

> **审查日期**: 2026-07-11
> **审查范围**: agentrt 全量 C 源码（~250 .c 文件 + ~200 .h 文件）vs OLK-6.6 核心源码（kernel/sched/core.c、mm/mmap.c、kernel/printk/printk.c、include/linux/sched.h 等）
> **审查方法论**: 逐行源码对比 + 12 维度逐一评分

---

## 执行摘要

agentrt 源码与 OLK-6.6 对比，综合代码品质评分 **72/100（B级）**。agentrt 在多方面展现了良好的工程素养——C11 原子操作显式内存序、Doxygen 风格的接口文档、跨平台 compat 抽象层、以及清晰的分节注释风格。但也存在若干与 OLK-6.6 品味不一致或可优化的问题，主要集中在：过多的宏魔法、名称冗长、goto 标签不够语义化、以及 `#ifdef _WIN32` 内联导致的代码噪音。

---

## 一、12 维度对比评分

| 维度 | OLK-6.6 评分 | agentrt 评分 | 差距 | 关键差异 |
|------|-------------|-------------|------|---------|
| **1. 文件头与 SPDX** | 9/10 | 8/10 | -1 | agentrt 头部信息更丰富但冗长 |
| **2. Include 组织** | 9/10 | 7/10 | -2 | agentrt 系统头文件与项目头文件混排 |
| **3. 注释风格** | 10/10 | 8/10 | -2 | agentrt 注释质量高但风格不统一 |
| **4. 命名约定** | 9/10 | 6/10 | -3 | agentrt 名称过长（平均 30+ 字符） |
| **5. 错误处理** | 10/10 | 7/10 | -3 | agentrt 宏魔法多，goto 标签不够语义化 |
| **6. 函数设计** | 9/10 | 7/10 | -2 | agentrt 部分函数偏长，职责偏重 |
| **7. 锁与并发** | 10/10 | 9/10 | -1 | agentrt 显式内存序优于 OLK-6.6 |
| **8. 类型系统** | 9/10 | 7/10 | -2 | agentrt typedef 偏多，struct 文档不足 |
| **9. 跨平台抽象** | 8/10 | 9/10 | +1 | agentrt compat 层优于 OLK-6.6 |
| **10. 宏使用** | 8/10 | 5/10 | -3 | agentrt 宏定义过多（ALLOC_RET_ERR 等） |
| **11. 防御性编程** | 9/10 | 8/10 | -1 | 双方都在高水平 |
| **12. 代码品味** | 10/10 | 6/10 | -4 | OLK-6.6 极简克制，agentrt 偏冗长装饰 |

**加权平均**: OLK-6.6 **91/100 (A+)**，agentrt **72/100 (B)**

---

## 二、逐维度详细分析

### 2.1 文件头与 SPDX 声明

**OLK-6.6 风格**:
```c
// SPDX-License-Identifier: GPL-2.0-only
/*
 *  kernel/sched/core.c
 *
 *  Core kernel CPU scheduler code
 *
 *  Copyright (C) 1991-2002  Linus Torvalds
 */
```

**agentrt 风格**:
```c
// SPDX-FileCopyrightText: 2025-2026 SPHARX Ltd.
// SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0
/**
 * @file alloc.c
 * @brief 物理内存分配器（带追踪的 malloc/free 封装）
 * @copyright (c) 2026 SPHARX. All Rights Reserved.
 *
 * @details
 * 本模块实现线程安全的内存分配追踪系统。
 * - 使用原子标志确保初始化线程安全
 * - 使用互斥锁保护统计数据
 * ...
 */
```

**评估**: agentrt 的头部含金量更高（Doxygen 结构化的模块描述），但略显冗长。OLK-6.6 的简洁是一种品味选择——"代码应该自解释，不需要太长介绍"。

**建议**: ✅ 保持 agentrt 的 `@brief` + `@details` 风格（对 API 消费者有很大价值），但去掉装饰性内容（`"From data intelligence emerges."` 口号）。

---

### 2.2 Include 组织

**OLK-6.6 风格** (`kernel/sched/core.c`):
```c
#include <linux/highmem.h>       /* linux/ 头文件严格字母序 */
#include <linux/hrtimer_api.h>
#include <linux/ktime_api.h>
#include <linux/sched/signal.h>   /* linux/sched/ 子目录也严格字母序 */
...
#include <asm/irq_regs.h>         /* asm/ 头文件在 linux/ 之后 */
#include <asm/switch_to.h>

#include "sched.h"                /* 本地头文件在最末 */
#include "stats.h"
```

**agentrt 风格** (`alloc.c`):
```c
#include "agentrt.h"
#include "mem.h"
#include "task.h"
#include <stdlib.h>
#include "memory_compat.h"       /* 本地头文件与系统头文件混排 */
#include "string_compat.h"
#include "check.h"
#include <stdio.h>
#include <string.h>
#include "atomic_compat.h"
#include "error.h"
```

**评估**: OLK-6.6 的 include 组织严格分层：`linux/` → `asm/` → `"local.h"`，每个组内字母序。agentrt 的 include 是混排的——系统头文件（`<stdlib.h>`, `<stdio.h>`, `<string.h>`）与项目头文件交错出现。

**建议**: ❗ **需要改进**。按以下顺序重组所有文件的 include：
1. 项目主入口头文件（`"agentrt.h"` / `"airymax_rt.h"`）
2. 系统头文件（`<stdlib.h>`, `<stdio.h>`, `<string.h>` 等，字母序）
3. 跨平台 compat 头文件（`"atomic_compat.h"`, `"memory_compat.h"` 等）
4. 项目其他头文件（`"mem.h"`, `"task.h"` 等，字母序）

---

### 2.3 注释风格

**OLK-6.6 风格**:
```c
/*
 * Magic required such that:
 *
 *	raw_spin_rq_lock(rq);
 *	...
 *	raw_spin_rq_unlock(rq);
 *
 * ends up locking and unlocking the _same_ lock, and all CPUs
 * always agree on what rq has what lock.
 */
static DEFINE_MUTEX(sched_core_mutex);

/* kernel prio, less is more */
static inline int __task_prio(const struct task_struct *p)
```

**agentrt 风格**:
```c
/* ==================== 全局状态 ==================== */

/** @brief 总分配字节数 */
static atomic_size_t total_allocated = 0;

/** @brief 当前使用字节数 */
static atomic_size_t used_allocated = 0;

/**
 * @brief 更新峰值内存使用量
 * @note 必须在持有 mem_stats_mutex 时调用，使用 relaxed 内存顺序
 */
static void update_peak_unlocked(void)
```

**评估**: agentrt 的 Doxygen `@brief` / `@param` / `@return` / `@note` 注释系统质量很高，对接口消费者极其友好。但有两个问题：

1. **分节注释风格不一致**: `/* ==================== 全局状态 ==================== */` 这种 ASCII 装饰性分节在 OLK-6.6 中不存在——OLK-6.6 用简洁的 `/* Scheduling policies */` 做分节。
2. **`/* 单行注释 */` vs `// 单行注释`**: agentrt 中 `//` 和 `/* */` 混用，OLK-6.6 几乎只用 `/* */`。

**建议**: ⚠️ 建议统一：
- 分节注释改为 OLK-6.6 风格：`/* 全局状态 */` 代替 `/* ==================== 全局状态 ==================== */`
- 非 Doxygen 单行注释统一使用 `/* */`
- 公共 API 保持 Doxygen `/** */` 风格不变

---

### 2.4 命名约定（最需要改进的维度）

这是 agentrt 与 OLK-6.6 差距最大的维度。

**OLK-6.6 命名特征**:
- 简洁、精准、动词在先
- 模块前缀短：`sched_`, `mm_`, `printk_`, `rcu_`
- 函数名平均 15-25 个字符
- 示例: `sched_core_enqueue`, `__task_prio`, `rb_sched_core_less`, `vma_set_page_prot`

**agentrt 命名特征**:
- 完全限定、明确来源模块
- 函数名平均 25-40 个字符
- 示例: `airymax_rt_mem_alloc_ex` (22字符), `scheduler_core_fetch_add_task_id` (31字符),
  `airymax_rt_gateway_service_load_config` (37字符), `airymax_rt_daemon_bootstrap_sd_start` (38字符)

**具体问题**:

| agentrt 当前命名 | 字符数 | 建议 OLK-6.6 风格 | 字符数 |
|-----------------|--------|-------------------|--------|
| `airymax_rt_mem_alloc_ex` | 22 | `mem_alloc_tracked` | 16 |
| `scheduler_core_fetch_add_task_id` | 31 | `sched_next_id` | 12 |
| `airymax_rt_gateway_service_load_config` | 37 | `gw_config_load` | 14 |
| `airymax_rt_daemon_bootstrap_sd_start` | 38 | `sd_bootstrap_start` | 17 |
| `airymax_rt_mem_aligned_alloc_ex` | 30 | `mem_alloc_aligned_tracked` | 23 |
| `atomic_load_explicit(&g_core_ctx, memory_order_acquire)` | 52+ | 定义 `sched_ctx()` 内联访问器 | ~12 |

**建议**: ❗ **重要改进点**:
1. 模块公有函数使用短前缀：`gw_` (gateway), `sched_` (scheduler), `cup_` (cupolas)
2. 内部 static 函数可以更短，不需要 `airymax_rt_` 前缀
3. `_ex` 后缀（表示"带调试信息"版本）不符合 OLK-6.6 风格，改为 OLK-6.6 的 `_tracked` 或使用 `__` 前缀标记扩展版本
4. 对频繁访问的全局变量，定义内联访问器函数代替裸 atomic_load

---

### 2.5 错误处理模式（最需要改进的维度之二）

**OLK-6.6 风格** (`mm/mmap.c`):
```c
static int do_brk_flags(...)
{
    ...
    vma = vm_area_alloc(mm);
    if (!vma)
        goto out_free_vmi;      /* ← 语义化标签 */
    ...
out_free_mpol:
    mpol_put(vma_policy(vma));
out_free_vma:
    vm_area_free(vma);
out_free_vmi:
    vma_iter_free(&vmi);
out_fput:
    fput(file);
out:
    mmap_write_unlock(mm);
    return error;
}
```
- 标签命名了要释放/解锁的**资源名称**（`vma`, `mpol`, `fput`）
- 标签按**资源分配的逆序**排列
- 每个标签只做一件事

**agentrt 风格** (`daemons/gateway_d/src/main.c`):
```c
    airymax_rt_error_t err = airymax_rt_gateway_service_create(&g_service, &config);
    if (err != AIRYMAX_RT_SUCCESS) {
        SVC_LOG_ERROR("Failed to create service (err=%d)", err);
        goto cleanup;               /* ← 通用标签 */
    }

    err = airymax_rt_gateway_service_init(g_service);
    if (err != AIRYMAX_RT_SUCCESS) {
        SVC_LOG_ERROR("Failed to init service (err=%d)", err);
        goto cleanup_service;       /* ← 命名了资源但不够具体 */
    }
    ...
cleanup_service:
    airymax_rt_gateway_service_destroy(g_service);
cleanup:
    airymax_rt_mutex_destroy(&g_running_lock);
    airymax_rt_socket_cleanup();
```

**具体问题**:

| 问题 | OLK-6.6 做法 | agentrt 当前 |
|------|-------------|-------------|
| goto 标签语义 | `out_free_mpol` / `out_unlock` | `cleanup` / `error` / `cleanup_service` |
| 错误推送 | 直接 `return -EINVAL` | `ALLOC_RET_ERR(c)` 宏（封装了 error_push） |
| 错误日志 | 不记录（调用者决定） | 每个错误路径都打 log + push |
| 返回值 | `-EINVAL` / `-ENOMEM` | `AIRYMAX_RT_ERR_INVALID_PARAM` |

**建议**: ❗ **重要改进点**:

1. **goto 标签语义化**: `cleanup_service` → `out_destroy_service`，`cleanup` → `out_unlock`

2. **减少宏魔法**: `ALLOC_RET_ERR(c)` / `ATM_RET_ERR(c)` / `AIRYMAX_RT_ERROR()` / `AIRYMAX_RT_ERROR_NULL()` 四种错误宏形态，建议统一为一种：
   ```c
   // 改为 OLK-6.6 风格
   if (!init_lock) {
       airymax_rt_error_push(AIRYMAX_RT_EINVAL);
       return AIRYMAX_RT_EINVAL;
   }
   ```

3. **错误日志控制**: OLK-6.6 的内核函数不在每个错误点打印日志——它信任调用者会处理。agentrt 可以保持日志（对调试更友好），但应该用 `pr_debug` 级别的条件日志而非 `SVC_LOG_ERROR`

4. **返回值**: OLK-6.6 使用 `0/-Exxx`（负值=错误），agentrt 使用 `AIRYMAX_RT_SUCCESS=0` / 正负值混合。建议与 OLK-6.6 对齐：0=成功，负值=错误码

---

### 2.6 函数设计

**OLK-6.6 特征**:
- 函数短小：大多数 20-50 行
- 单一职责
- 函数体前有清晰的注释说明"做什么"和"为什么"
- `static inline` 用于频繁调用的短小辅助函数

**agentrt 特征**:
- 部分函数长度合理（`ensure_initialized` 44行，`airymax_rt_mem_cleanup` 28行）
- 但也存在一些过长的函数
- 函数职责划分较好
- Doxygen 注释在函数头部

**建议**: ⚠️ agentrt 的函数设计总体不错，但 `parse_args`（52行，混杂了参数解析与 daemonize 逻辑）建议拆分为 `parse_options` + `maybe_daemonize`。

---

### 2.7 锁与并发

**这是 agentrt 领先 OLK-6.6 的维度**。

**OLK-6.6** (`kernel/sched/core.c`):
```c
static void sched_core_lock(int cpu, unsigned long *flags) {
    for_each_cpu(t, smt_mask)
        raw_spin_lock_nested(&cpu_rq(t)->__lock, i++);
}
```

**agentrt** (`task/scheduler_core.c`):
```c
/* 快速路径：已初始化（使用 acquire 语义） */
int state = atomic_load_explicit(&mem_initialized, memory_order_acquire);
if (state == 1) return 0;

/* 慢速路径：CAS 获得初始化权 */
int expected = 0;
if (atomic_compare_exchange_strong_explicit(&mem_initialized, &expected, 2,
    memory_order_acq_rel, memory_order_acquire)) {
    /* 获得初始化权 */
    ...
    atomic_store_explicit(&mem_initialized, 1, memory_order_release);
}
```

**评估**: agentrt 对 C11 原子操作显式内存序的使用是**教科书级别的**。每个 `atomic_load/store/fetch_add/compare_exchange` 都明确指定了 `memory_order_*`，并且代码注释解释了为什么选择该内存序。这超过了 OLK-6.6 的 `atomic_inc`/`atomic_dec`（隐式 seq_cst）的精确度。

**建议**: ✅ 保持现有风格，这是 agentrt 的亮点。

---

### 2.8 类型系统

**OLK-6.6**: 几乎不 typedef 结构体，强制使用 `struct task_struct` 而非 `task_t`。

**agentrt**: 
- `airymax_rt_mem_alloc_info_t` — 结构体 typedef
- `airymax_rt_error_t` — 错误码 typedef
- `scheduler_core_ctx_t` — 上下文 typedef
- `gw_forward_t` — 转发器 typedef
- `airymax_rt_mutex_t` — 互斥锁 typedef

**OLK-6.6 coding-style.rst §5** 明确说：
> "It's a **mistake** to use typedef for structures and pointers."

允许的例外：完全不透明类型（`pte_t`）、整数类型别名（`u8/u16/u32`）、sparse 类型检查。

**建议**: ❗ **需要重大调整**:
1. 移除结构体的 `_t` typedef，改为 `struct airymax_mem_alloc_info`
2. 保留 `airymax_rt_error_t`（属于整数类型别名的例外）
3. 保留完全不透明的句柄 typedef（如 `gw_forward_t` 如果其内部结构对外不可见）

---

### 2.9 跨平台抽象（agentrt 领先维度）

**OLK-6.6**: 使用 `#ifdef CONFIG_ARCH_X86` / `arch/x86/` / `arch/arm64/` 分离平台代码。

**agentrt**: 使用 `#ifdef _WIN32` + compat 头文件（`atomic_compat.h`, `memory_compat.h`, `string_compat.h`）+ `platform_compat.c` 实现 Windows/Linux/macOS 跨平台。

agentrt 的 compat 抽象层设计得很好——每个平台差异点封装在独立的 `_compat.h` 头文件中。

**建议**: ✅ 保持。但 `#ifdef _WIN32` 在业务逻辑函数中散落太多（如 `alloc.c` 中 `#ifdef _WIN32` 出现了 5 次），建议将这些平台判断也抽入 compat 层。

---

### 2.10 宏使用（最需要改进的维度之三）

agentrt 使用了大量宏来"简化"代码，反而增加了认知负担：

```c
// 4 种不同的错误处理宏
#define ALLOC_RET_ERR(c)  do { airymax_rt_error_push_ex(...); return (c); } while(0)
#define ATM_RET_ERR(c)    do { airymax_rt_error_push_ex(...); return (c); } while(0)
AIRYMAX_RT_ERROR(AIRYMAX_RT_ERR_IO, "failed to load config file");
AIRYMAX_RT_ERROR_NULL(AIRYMAX_RT_ERR_INVALID_PARAM, "null parameter");

// 封装了 malloc/free 的宏
AIRYMAX_RT_MALLOC(size)
AIRYMAX_RT_CALLOC(n, size)
AIRYMAX_RT_FREE(ptr)
```

**问题**:
| 问题 | 说明 |
|------|------|
| 宏功能相同但前缀不同 | `ALLOC_RET_ERR` vs `ATM_RET_ERR` 做同样的事 |
| 宏隐藏了控制流 | `AIRYMAX_RT_ERROR` 和 `AIRYMAX_RT_ERROR_NULL` 内部有 `return` |
| 宏与函数重名 | `AIRYMAX_RT_MALLOC` 看起来像函数但无法取地址 |
| ALL_CAPS 过度使用 | 不是所有需要大写 |

**OLK-6.6 对此的态度**: OLK-6.6 极少使用此类"便利宏"。`return -EINVAL` 就是 `return -EINVAL`，不会包装成 `RETURN_ERR(EINVAL)`。

**建议**: ❗ **重要改进**:
1. 统一错误处理宏为一种：移除 `ALLOC_RET_ERR` 和 `ATM_RET_ERR`，只保留 `rt_error_return(err)`
2. `AIRYMAX_RT_MALLOC` / `AIRYMAX_RT_FREE` 改为小写内联函数：`static inline void *rt_malloc(size_t size)`
3. 删除 `AIRYMAX_RT_ERROR_NULL` —— 这个宏隐藏了 `return NULL` 的控制流，阅读者不知道函数会在哪里返回

---

### 2.11 防御性编程

**双方都在高水平**。agentrt 的 NULL 检查、参数校验、原子操作、锁保护都做得很到位。

**agentrt 的部分亮点**:
- `ensure_initialized()` 中的双重检查锁定模式
- `scheduler_core_init()` 中的 CAS 单次创建 init_lock
- `airymax_rt_mem_free()` 中的 `if (!ptr) return` 空指针防护
- 所有原子操作都指定了显式内存序

**建议**: ✅ 保持现有水平。

---

### 2.12 代码品味（"Code Taste"）

这是最主观但也是最重要的维度。OLK-6.6 的代码品味可以用几个词概括：**克制、简洁、信任读者**。

**OLK-6.6 品味体现**:
```c
/* kernel prio, less is more */
static inline int __task_prio(const struct task_struct *p)
{
    if (p->sched_class == &stop_sched_class)   /* trumps deadline */
        return -2;
    if (rt_prio(p->prio))                     /* includes deadline */
        return p->prio;
    if (p->sched_class == &idle_sched_class)
        return MAX_RT_PRIO + NICE_WIDTH;
    if (task_on_scx(p))
        return MAX_RT_PRIO + MAX_NICE + 1;
    return MAX_RT_PRIO + MAX_NICE;
}
```
- 12 行实现 5 种调度类的优先级映射
- 注释精简到极致：`/* trumps deadline */`、`/* includes deadline */`
- 信任读者理解调度类层次

**agentrt 品味差距体现**:
```c
/* ==================== 全局状态 ==================== */

/** @brief 总分配字节数 */
static atomic_size_t total_allocated = 0;

/** @brief 当前使用字节数 */
static atomic_size_t used_allocated = 0;

/** @brief 峰值使用字节数 */
static atomic_size_t peak_allocated = 0;

/** @brief 堆大小上限（0=无限制） */
static atomic_size_t max_heap_size = 0;

/** @brief 分配记录链表头 */
static airymax_rt_mem_alloc_info_t *alloc_list = NULL;

/** @brief 统计数据互斥锁 */
static airymax_rt_mutex_t *mem_stats_mutex = NULL;

/** @brief 初始化状态标志（原子操作保护） */
static atomic_int mem_initialized = 0;

/** @brief 初始化锁（用于双重检查锁定） */
static airymax_rt_mutex_t *init_lock = NULL;
```
- 每个变量都有 `@brief` 注释，但对理解代码没有新增信息（`total_allocated` 已经是"总分配字节数"的意思）
- ASCII 分节符 `/* ============ */` 增加了视觉噪音
- 40 行代码定义了 8 个变量（OLK-6.6 同样内容可能在 15 行内完成）

**建议**: ❗ **品味提升**:
1. 去掉 ASCII 装饰分节符
2. 对自解释的变量名去掉冗余 `@brief` 注释
3. 整体追求"少即是多"的克制美学
4. 注释回答"为什么"（`Why`）而非"是什么"（`What`）

---

## 三、改进优先清单

### 3.1 高优先级（影响代码品质感知）

| # | 改进项 | 工时 | 影响范围 |
|---|--------|------|---------|
| **1** | 移除结构体 `_t` typedef，改用 `struct` 前缀 | ~16h | 全项目 ~150 处 |
| **2** | 统一 goto 标签语义化（`cleanup` → `out_unlock` 等） | ~8h | ~50 个 goto 标签 |
| **3** | 统一错误宏为 1 种（移除 `ALLOC_RET_ERR` / `ATM_RET_ERR` / `*_NULL`） | ~12h | ~30 处宏定义 + ~200 处调用点 |
| **4** | 简化函数命名（移除冗余 `airymax_rt_` 前缀） | ~20h | ~200 个函数声明 |
| **5** | 重组 include 顺序（系统头文件 → compat → 项目头文件，字母序） | ~8h | ~250 个 .c 文件 |

### 3.2 中优先级（提升代码可读性）

| # | 改进项 | 工时 | 影响范围 |
|---|--------|------|---------|
| **6** | 去掉 ASCII 装饰分节符 | ~4h | ~100 处分节注释 |
| **7** | 自解释变量去掉冗余 Doxygen | ~6h | ~200 个静态变量 |
| **8** | 将 `#ifdef _WIN32` 业务逻辑内联迁移至 compat 层 | ~16h | ~50 处平台条件编译 |
| **9** | `AIRYMAX_RT_MALLOC` → 内联函数 | ~4h | ~100 处调用点 |

### 3.3 低优先级（锦上添花）

| # | 改进项 | 工时 |
|---|--------|------|
| **10** | 统一非 Doxygen 注释为 `/* */` 风格 | ~4h |
| **11** | `parse_args` 拆分 → `parse_options` + `maybe_daemonize` | ~2h |
| **12** | 错误返回值改为 0 成功 / 负值错误 | ~24h（破坏性变更） |

---

## 四、agentrt 代码亮点（应保持的部分）

以下是 agentrt 做得比 OLK-6.6 更好或至少同样好的方面，应该保持：

1. **C11 原子操作显式内存序**: `memory_order_acquire/release/acq_rel/seq_cst` 精确指定，优于 OLK-6.6 的隐式原子语义
2. **Doxygen 公共 API 注释**: `@brief`, `@param`, `@return`, `@note`, `@see` 结构化的接口文档
3. **跨平台 compat 抽象层**: `atomic_compat.h`, `memory_compat.h`, `string_compat.h` 设计良好
4. **双重检查锁定**: `ensure_initialized()` 和 `scheduler_core_init()` 中的 CAS 模式实现正确
5. **全面测试覆盖**: agentrt 有丰富的单元测试（test_*.c 文件）
6. **代码注释中的修复标记**: `W09.4 (BUG-4 修复)` 标注了修复历史，对维护者有价值
7. **编译时 CRC32 表**: `g_crc32_table[256]` 作为编译时常量，零运行时开销

---

## 五、示例：重构前后对比

### 示例 1: 内存分配器全局状态区域

**重构前** (40 行):
```c
/* ==================== 全局状态 ==================== */

/** @brief 总分配字节数 */
static atomic_size_t total_allocated = 0;

/** @brief 当前使用字节数 */
static atomic_size_t used_allocated = 0;

/** @brief 峰值使用字节数 */
static atomic_size_t peak_allocated = 0;

/** @brief 堆大小上限（0=无限制） */
static atomic_size_t max_heap_size = 0;

/** @brief 分配记录链表头 */
static airymax_rt_mem_alloc_info_t *alloc_list = NULL;

/** @brief 统计数据互斥锁 */
static airymax_rt_mutex_t *mem_stats_mutex = NULL;

/** @brief 初始化状态标志（原子操作保护） */
static atomic_int mem_initialized = 0;

/** @brief 初始化锁（用于双重检查锁定） */
static airymax_rt_mutex_t *init_lock = NULL;
```

**重构后** (OLK-6.6 风格，15 行):
```c
/* Memory allocator tracking state, protected by mem_stats_mutex */
static atomic_size_t total_allocated;
static atomic_size_t used_allocated;
static atomic_size_t peak_allocated;
static atomic_size_t max_heap_size;       /* 0 = unlimited */
static struct airymax_mem_alloc_info *alloc_list;
static struct airymax_mutex *mem_stats_mutex;

/* Lazy initialization state with double-checked locking */
static atomic_int mem_initialized;        /* 0=uninit, 1=ready, 2=in-progress */
static struct airymax_mutex *init_lock;
```

### 示例 2: 错误处理

**重构前**:
```c
    init_lock = airymax_rt_mutex_create();
    if (!init_lock) {
        atomic_store_explicit(&mem_initialized, 0, memory_order_release);
        ALLOC_RET_ERR(AIRYMAX_RT_EINVAL);
    }

    mem_stats_mutex = airymax_rt_mutex_create();
    if (!mem_stats_mutex) {
        airymax_rt_mutex_free(init_lock);
        init_lock = NULL;
        atomic_store_explicit(&mem_initialized, 0, memory_order_release);
        ALLOC_RET_ERR(AIRYMAX_RT_EINVAL);
    }
```

**重构后** (OLK-6.6 风格):
```c
    init_lock = airymax_rt_mutex_create();
    if (!init_lock)
        goto out_reset;

    mem_stats_mutex = airymax_rt_mutex_create();
    if (!mem_stats_mutex)
        goto out_free_init_lock;

    /* ... success ... */
    return 0;

out_free_init_lock:
    airymax_rt_mutex_free(init_lock);
    init_lock = NULL;
out_reset:
    atomic_store_explicit(&mem_initialized, 0, memory_order_release);
    return AIRYMAX_RT_EINVAL;
```

---

## 六、总结

agentrt 的 C 源码整体质量在**及格线之上**（B 级 72/100），核心逻辑正确、并发安全、跨平台设计良好。与 OLK-6.6 的差距主要在"品味层面"而非"正确性层面"：

| 差距类型 | 严重度 | 描述 |
|---------|--------|------|
| 命名冗长 | 中 | 函数名平均长 10-15 字符，降低密度 |
| 宏过多 | 中 | 4 种错误宏 + ALL_CAPS 分配宏隐藏了控制流 |
| 装饰过度 | 低 | ASCII 分节符、冗余 Doxygen 增加了视觉噪音 |
| typedef `_t` | 中 | 违反 OLK-6.6 §5 规范 |
| include 混排 | 低 | 不分组不排序 |
| goto 标签 | 中 | 不够语义化 |

**总体评价**: agentrt 是一个**工程认真、但品味有待提升**的代码库。修复上述问题后，预期代码品质可从 B 级（72/100）提升至 A- 级（85/100）。
