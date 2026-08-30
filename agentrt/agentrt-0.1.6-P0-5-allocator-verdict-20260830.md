# P0-5 分配器收敛裁决（2026-08-30）

**范围**：`agentrt-0.1.6-improvement-plan-20260828.md` P0-5「两套分配器逐文件 diff，消除真重复」。

## 裁决结论

corekern 与 commons 的 arena / tcache 经逐文件 diff 判定为**假重复**，按 v4.3 判据（同名不同实现保留，不强行合并）**保留两套**，不合并。

## 证据（逐文件 diff）

### arena

| 维度 | corekern（atoms/corekern/src/mem/arena.c, 297 行） | commons（commons/utils/memory/src/arena.c, 373 行） |
|------|----------------------------------------------|---------------------------------------------|
| API | `airy_arena_create(block_size)` 族 | `arena_create(chunk_size, max_chunks)` 族 |
| 独有能力 | `alloc_aligned` / `reset_to` | `calloc` / `get_stats` / `contains` / `max_chunks` / `release` |
| 结构 | `airy_arena_block`（数据内嵌结构体）+ `first->next` 链 | `arena_chunk`（start/bump/end 独立指针）+ `current` 链 |
| 定位 | 内核态可复用原语（`export.h` AIRY_API，未来内核态复用） | 用户态门面（含统计/包含检测/块数上限） |

diff 行数：551。机制同源（链式 bump + mark）但**非逐行同构**。唯一使用方 `atoms/coreloopthree/src/loop/loop.c` 依赖 commons 的 `arena_get_stats`（corekern 无此能力）。

### tcache

| 维度 | corekern（atoms/corekern/src/mem/tcache.c, 176 行） | commons（commons/utils/memory/src/tcache.c, 313 行） |
|------|----------------------------------------------|---------------------------------------------|
| API | `airy_tcache_create(config)` 族（独立配置） | `tcache_create(pool, batch_size, max_cached)` 族 |
| 依赖 | 独立分配缓存 | **深度绑定 `memory_pool_t`**（batch_fill/flush 从池取/还） |
| diff 行数 | 432 | — |

职责不同：corekern tcache 是独立缓存原语，commons tcache 是 pool 的缓存层。

## 引用判据

- 决策 4（改进方案 3.x）：「与 corekern 逐行同构的 arena/tcache 改为调 corekern」——**逐行同构**是合并前提，diff 证明不同构。
- v4.3 判据：「同名不同实现（如 pool 语义不同）保留，不强行合并」——两套实现 API 不同名、能力面不同，属假重复。

## 后续（0.1.7+ 可选）

若推进内核态复用，可将 corekern arena/tcache 作为共享原语下沉，commons 改为纯包装——需统一 API 面（stats/contains/calloc 等）后再议，不在 0.1.6 范围。

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. | agentrt-0.1.6 P0-5 裁决 | 2026-08-30
