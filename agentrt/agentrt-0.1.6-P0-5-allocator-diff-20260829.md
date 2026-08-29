# agentrt-0.1.6 P0-5 实证报告：两套分配器逐文件 diff

- 日期：2026-08-29
- 范围：`commons/utils/memory`（用户态门面）vs `atoms/corekern/src/mem`（内核原语）
- 结论：**无安全可删真重复（同名异实的假重复）；4 处死面候选记录待 0.1.7+ 收敛**

## 一、审计对象

| 层 | 目录 | 文件数 | 定位 |
|----|------|--------|------|
| commons | `commons/utils/memory` | ~18（.c/.h） | 用户态分配门面 + 调试 + 统计 |
| corekern | `atoms/corekern/src/mem` | 15 | 微核心分配原语 + OOM 全家桶 |

## 二、逐文件对照

| 功能 | commons | corekern | 接口差异 | 使用方（生产） | 判定 |
|------|---------|----------|---------|--------------|------|
| arena | `arena.c`（有锁 + 统计 + mark/release + TLS） | `arena.c`（无锁、内嵌块头、轻量） | 裸名 `arena_*` vs `airy_arena_*` | commons→loop.c（1 处）；corekern→**零调用** | 假重复（分层）；corekern 面为死面 |
| tcache | `tcache.c`（绑定 memory_pool_t） | `tcache.c`（回调注入 global_alloc/free） | 裸名 `tcache_*` vs `airy_tcache_*` | commons→测试；corekern→**零调用** | 假重复（依赖模型不同）；corekern 面为死面 |
| mempool | `memory_pool.c/_alloc/_stats`（用户态池） | `mempool.c`（含 emergency 应急机制） | `memory_pool_*` vs `airy_mempool_*` | commons→**零生产**；corekern→cupolas | 假重复 |
| slab | — | `slab.c` | — | cupolas→活跃 | 无重复 |
| guard | — | `guard.c` | — | **零调用** | 死面候选 |
| refcount | `refcounted.h`（独立设计） | `refcount.c` + `refcount.h` | — | corekern 内→**零调用** | 死面候选 |
| OOM | — | `oom_*`（6 文件） | — | 内部活跃，依赖 commons prealloc | 无重复，活跃 |
| prealloc | `memory_prealloc.c` | — | — | corekern OOM 全家桶 | 活跃 |
| stats_reporter | `memory_stats_reporter.c` | — | — | daemons/common svc | 活跃 |
| debug 五件套 | `memory_debug*.c`（5 文件） | — | — | **零生产调用** | 死面候选 |

## 三、关键交叉引用（防误判验证）

1. **corekern arena 与 commons 桥接已存在**：`airy_arena_get_current/set_current`（TLS）由 commons 实现，corekern arena.c 明确注释不重定义；`airy_memory.h` 的 `AIRY_ARENA_ALLOC` 宏声明依赖 `airy_arena_alloc`（corekern 实现）。
2. **AIRY_ARENA_ALLOC 宏当前零调用方**（除定义处）→ corekern `airy_arena_*` 无活跃消费者。
3. corekern tcache/slab 的 "commons 引用" 经核实为函数定义自身（子串误报），无真实交叉。

## 四、结论与决策

- **真重复 = 0**：两套 arena/tcache/mempool 算法思想同源，但 API 命名、锁策略、依赖模型、服务层级（commons=用户态门面，atoms=内核原语）不同，属**同名异实的假重复**，分层设计合理，不可简单二选一。
- **不删除分配器组件**：corekern 面（arena/tcache/mempool）为公共头声明（`airy_memory.h`/`refcount.h`）依赖的稳定接口，删除需同步公共头且无产物体积收益（静态库按需抽取，死 .o 不链接）。
- **4 处死面候选**（`corekern/arena.c`、`corekern/tcache.c`、`corekern/refcount.c`、`commons/memory_debug*.c`）：生产零调用，记录为 **0.1.7+ 统一分配器接口收敛**的清理项（届时以"公共接口迁移 + 悬空声明清理"一步完成，避免 0.1.6 版本内半删状态）。
- **分配器单测**：`test_arena_tcache` 等通过（ctest 183/183，见 P0-4 报告）。

## 五、0.1.7+ 建议（记录，不本版实施）

统一分配器收敛方向：以 commons `airy_memory.h` 宏面为唯一公共接口（SSoT），corekern 原语面作为底层实现收敛至 commons；或 corekern 面为唯一原语、commons 门面包裹。需独立方案评估依赖环（atoms→commons 单向，方向明确）。
