SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 13 — 内存分配与分层治理（v3.6b 深度对比）

> **文档定位**：agentrt-linux 内核设计深度对比研究 · 第二轮 · 维度 5
> **对比基准**：openEuler kernel-OLK-6.6 · seL4-master · Airymax agentrt-linux
> **最后更新**：2026-07-31
> **方法论**：逐字节阅读三项目源码，所有引用标注文件路径+行号，严禁编造

---

## 0. 摘要

本报告对比三项目的内存分配与分层治理。openEuler 提供 alloc_pages + SLUB + memcg 完整体系；seL4 用 Untyped + Retype 实现能力中介的内存类型化分配；Airymax 的 [airy_mem_alloc.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/memory/airy_mem_alloc.c) 仅 `alloc_pages(GFP_KERNEL)` wrapper，[airy_mem_tier.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/memory/airy_mem_tier.c) 的 L1-L4 tier 分类仅靠 GFP 低 4 位、无实际 NUMA/CXL 路由。正面发现：[memory_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/memory_types.h) 的 DSL 降级回退设计（L36-61）周全。核心发现：N7（无 memcg/per-agent 账户）、N8（tier 无实际路由）、N15（zero_copy 注册表全局锁）、N16（tier 表无 sysfs）。

---

## 1. 对比基准

### 1.1 openEuler OLK-6.6 内存体系

openEuler 沿用 Linux 完整内存栈：

| 层 | 位置 | 说明 |
|----|------|------|
| 页分配 | [gfp.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/gfp.h) | GFP 标志体系（L129-148 zone 表：DMA/DMA32/HIGHMEM/MOVABLE 组合） |
| 伙伴分配器 | mm/page_alloc.c | `alloc_pages`/`__free_pages` |
| 对象分配器 | mm/slub.c | `kmem_cache_create`/`kmem_cache_alloc`/`kmem_cache_free` |
| 内存计费 | [memcontrol.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/memcontrol.h) | `struct mem_cgroup` + `try_charge`/`mem_cgroup_alloc` |

**特征**：GFP 标志编码 zone/movable/reclaim/IO 等多维语义；memcg 实现 per-cgroup 内存配额与计费；SLUB 提供固定大小对象池（减少内碎片）。

### 1.2 seL4 Untyped 内存

seL4 将物理内存抽象为 Untyped capability，通过 Retype 转化为具体类型：

| 函数 | 位置 | 行号 | 说明 |
|------|------|------|------|
| `decodeUntypedInvocation` | [untyped.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/untyped.c) | L26 | 解码 Retype 调用 |
| `invokeUntyped_Retype` | untyped.c | L272 | 执行 Retype（L229 调用点） |

**机制**：boot 阶段将全部空闲物理内存作为 Untyped cap 分配给 root task；用户态通过 `invokeUntyped_Retype` 将 Untyped 切分为 Frame/CNode/TCB 等具体类型 cap。每次 Retype 记录父子关系（MDB），支持 cap revoke 递归回收。这实现了**能力中介的内存类型化分配**——无 cap 无法分配内存，revoke 即回收。

### 1.3 Airymax 内存分配与分层

**页分配** — [airy_mem_alloc.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/memory/airy_mem_alloc.c)（46 行）：

| 函数 | 行号 | 实现 |
|------|------|------|
| `airy_mem_alloc_pages` | L19 | L26 `get_order`，L27 `MAX_ORDER` 检查，L33 `alloc_pages(GFP_KERNEL, order)` |
| `airy_mem_free_pages` | L37 | L45 `__free_pages(page, order)` |

**tier 分类** — [airy_mem_tier.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/memory/airy_mem_tier.c)（52 行）：

| 要素 | 行号 | 说明 |
|------|------|------|
| `enum airy_mem_tier` | L20-26 | L1 HBM/DDR / L2 DDR / L3 CXL/NVMe / L4 PMEM |
| `airy_mem_tier_shift[]` | L29-34 | 静态 shift 表（L1=0/L2=3/L3=6/L4=9） |
| `airy_mem_tier_of` | L37 | L39 `gfp & 0x0f` 取低 4 位，L41-48 按位匹配 tier，L51 默认 L2 |

**UAPI 契约** — [memory_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/memory_types.h)：

| 要素 | 行号 | 说明 |
|------|------|------|
| `enum airy_mem_level` | L16-22 | L1-L4 tier 枚举 |
| `AIRY_GFP_HOT/WARM/COLD/PMEM` | L25-28 | 0x01/0x02/0x04/0x08（占 GFP 低 4 位） |
| `AIRY_PAGE_CLASS_*` | L31-34 | ANON/FILE/SHMEM/AGENT 4 类 |
| DSL 降级回退 | L36-61 | `AIRY_SC_FALLBACK` 时所有 tier 折叠为 L1，`#warning` 提示 |

---

## 2. 关键发现

### 2.1 【发现 1】tier 分类仅靠 GFP 低 4 位，无实际 NUMA/CXL 路由

**现状**：[airy_mem_tier.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/memory/airy_mem_tier.c) L37 `airy_mem_tier_of` 仅做 GFP 低 4 位（L39 `gfp & 0x0f`）的位匹配分类，返回 tier 枚举，但该 tier 值**未被任何实际分配路径消费**——[airy_mem_alloc.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/memory/airy_mem_alloc.c) L33 始终用 `alloc_pages(GFP_KERNEL, order)`，不区分 tier，不调用 `alloc_pages_node` 选 NUMA 节点，不查 CXL 距离表。

**参考**：openEuler 通过 GFP zone 位（[gfp.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/gfp.h) L129-148）实际路由到不同 zone；NUMA 策略通过 `alloc_pages_node`/`mpol` 实现。seL4 [untyped.c](file:///home/spharxWorks/.engineer-reference/seL4-master/src/object/untyped.c) L272 `invokeUntyped_Retype` 按物理地址范围选择 Untyped 源。

**风险**：tier 分类目前是"文档化意图"而非可执行机制。`airy_mem_tier_shift[]`（L29-34）的批量分配偏移也未接入 alloc_pages 的 order 计算。M4 前需补齐或明确标记为"占位"。

**建议**：M4 实现 tier→NUMA node 映射，`airy_mem_alloc_pages` 接受 tier 参数并调 `alloc_pages_node`；或短期在 airy_mem_tier.c 头部加 `TODO(M4)` 注释。对应 N8。

**优先级**：P1 · 工作量 M4 · 风险低（占位不影响当前功能）

### 2.2 【发现 2】无 memcg 集成，无 per-agent 内存账户

**现状**：[airy_mem_alloc.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/memory/airy_mem_alloc.c) L33 `alloc_pages(GFP_KERNEL, order)` 不传 memcg，不按 agent 计费。无 `mem_cgroup_try_charge`、无 per-agent 内存配额。

**参考**：openEuler [memcontrol.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/memcontrol.h) 的 `struct mem_cgroup` + `try_charge` 实现 per-cgroup 配额；seL4 通过 Untyped cap 父子关系实现 per-agent 内存隔离（revoke 即回收全部派生内存）。

**风险**：agent 可无限制分配内存，无法实现 Micro-Supervisor 的内存配额隔离。第一轮报告 06 的 MemoryRovol（syscall 549，M5 规划）需要 per-agent 内存账户作为底层支撑。

**建议**：M3 设计 `airy_mem_account` 结构，关联 agent_id 与 memcg（或自维护 per-agent 页计数），`airy_mem_alloc_pages` 按 agent 计费，超限拒绝。对应 N7。

**优先级**：P1 · 工作量 8h · 风险中

### 2.3 【发现 3】airy_ipc_zero_copy 注册表全局链表+单 spinlock

**现状**：[airy_ipc_zero_copy.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_zero_copy.c) L1-168 的 buffer 注册表用全局链表 + 单 spinlock，无 per-agent 命名空间。

**参考**：与报告 12 N4（airy_object.c 全局锁）同源问题。

**建议**：改 per-agent 命名空间或 idr。对应 N15。

**优先级**：P2 · 工作量 6h · 风险中

### 2.4 正面发现：DSL 降级回退设计

[memory_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/memory_types.h) L36-61 的 `AIRY_SC_FALLBACK` 块是周全的降级设计：定义 `AIRY_SC_FALLBACK` 时所有 tier 折叠为 L1 hot、所有 page class 折叠为 ANON，L60 `#warning` 编译期提示。这保证 CXL/PMEM 不可用时系统仍可降级运行（仅 L1 可用），符合 agent RT 系统的生存性要求。建议其他子系统借鉴此 DSL 模式。

### 2.5 正面发现：MAX_ORDER 校验

[airy_mem_alloc.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/memory/airy_mem_alloc.c) L27 `order > MAX_ORDER` 检查 + L28 pr_warn 是合理的边界保护，避免 `alloc_pages` 收到超大 order 的未定义行为。

---

## 3. 改进点清单

| 编号 | 标题 | 优先级 | 现状行号 | 工作量 |
|------|------|--------|----------|--------|
| N7 | 无 memcg 集成，无 per-agent 内存账户 | P1 | [airy_mem_alloc.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/memory/airy_mem_alloc.c) L33 | 8h |
| N8 | tier 分类仅靠 GFP 低 4 位，无 NUMA/CXL 路由 | P1 | [airy_mem_tier.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/memory/airy_mem_tier.c) L37-51 | M4 |
| N15 | airy_ipc_zero_copy 注册表全局链表+单 spinlock | P2 | [airy_ipc_zero_copy.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_zero_copy.c) L1-168 | 6h |
| N16 | airy_mem_tier_shift 静态表无 sysfs 暴露 | P2 | [airy_mem_tier.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/memory/airy_mem_tier.c) L29-34 | 2h |
| — | DSL 降级回退设计周全（正面） | — | [memory_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/memory_types.h) L36-61 | — |
| — | MAX_ORDER 校验合理（正面） | — | [airy_mem_alloc.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/memory/airy_mem_alloc.c) L27 | — |

---

## 4. 小结

airy_mem_alloc.c 的 `alloc_pages` wrapper + `MAX_ORDER` 校验是合格的 M0 占位；airy_mem_tier.c 的 L1-L4 分类是"设计意图文档化"，尚未落地为可执行路由。DSL 降级回退（memory_types.h L36-61）是本轮正面亮点，体现了 agent RT 系统对生存性的重视。M3-M4 需补齐 per-agent 账户（N7）与 tier→NUMA 路由（N8），以支撑第一轮 MemoryRovol（syscall 549）的落地。
