SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 15 — 日志可观测性基础设施（v3.6b 深度对比）

> **文档定位**：agentrt-linux 内核设计深度对比研究 · 第二轮 · 维度 7
> **对比基准**：openEuler kernel-OLK-6.6 · seL4-master · Airymax agentrt-linux
> **最后更新**：2026-07-31
> **方法论**：逐字节阅读三项目源码，所有引用标注文件路径+行号，严禁编造

---

## 0. 摘要

本报告对比三项目的日志可观测性基础设施。openEuler 用 printk ringbuffer（[prb_reserve](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/printk/printk_ringbuffer.c) L1485 / [prb_commit](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/printk/printk_ringbuffer.c) L1632）+ [vprintk_emit](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/printk/printk.c) L2316 实现全局锁-free 日志；seL4 无 ringbuffer 日志，仅 `printf` 串口输出（debug build）；Airymax 以三层日志体系——[airy_log_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_ring.c) lock-free ring + [airy_log_kern.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_kern.c) printk 桥 + [airy_log_persist.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_persist.c) 文件持久化——构建可观测性。核心发现：N12（ring 满时 overwrite 无溢出计数器/告警）、N17（persist 同步 kernel_write 无异步刷盘线程）、N19（kern 8→5 级别映射丢失 ALERT/CRIT/NOTICE 粒度）。正面发现：lock-free ring 内存序正确，质量高于第一轮多数子系统。

---

## 1. 对比基准

### 1.1 openEuler OLK-6.6 printk ringbuffer

openEuler 沿用 Linux 5.10+ 的 lock-free printk ringbuffer：

| 要素 | 位置 | 行号 | 说明 |
|------|------|------|------|
| `struct printk_ringbuffer` | [printk_ringbuffer.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/printk/printk_ringbuffer.h) | L87 | 三索引结构（desc_ring/data_ring/seq） |
| `prb_reserve` | [printk_ringbuffer.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/printk/printk_ringbuffer.c) | L1485 | 生产者预约槽位 |
| `prb_commit` | printk_ringbuffer.c | L1632 | 提交（普通） |
| `prb_final_commit` | printk_ringbuffer.c | L1664 | 提交（最终，无后续续写） |
| `prb_init` | printk_ringbuffer.c | L2075 | 初始化 |
| `vprintk_store` | [printk.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/printk/printk.c) | L2192 | 格式化 + 入 ringbuffer |
| `vprintk_emit` | printk.c | L2316 | 入口：level 处理 + console + store |
| `vprintk_default` | printk.c | L2369 | 默认 vprintk |
| `vprintk_store` 声明 | [internal.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/printk/internal.h) | L39 | 内部声明 |
| `vprintk_default` 声明 | internal.h | L43 | 内部声明 |

**机制**：printk ringbuffer 用 desc_ring + data_ring 分离描述符与数据，三索引（head/tail/seq）cmpxchg 推进。`prb_reserve`（L1485）原子预约 desc + data block，`prb_commit`（L1632）通过 `smp_store_release` 发布 seq。NMI/递归安全通过 per-CPU `printk_safe` 上下文实现。8 级日志（LOGLEVEL_EMERG..DEBUG）原样保留，console_loglevel 控制台过滤。

### 1.2 seL4 日志（无 ringbuffer）

seL4 不维护运行时日志 ringbuffer。`CONFIG_PRINTING`（[faulthandler.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/faulthandler.c) L106-143 `print_fault`）下，`printf` 直接走串口/平台输出函数，无缓冲、无持久化。`CONFIG_DEBUG_BUILD` 下附带线程名与栈回溯（L164 `tcbName`、L169 `Arch_userStackTrace`）。这是形式化微内核的极简设计——日志属于"非内核职责"，由用户态 logger component 承载。

### 1.3 Airymax 三层日志体系

**层 1：lock-free ring** — [airy_log_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_ring.c)（321 行）：

| 要素 | 行号 | 说明 |
|------|------|------|
| `struct airy_log_ring_header` | L52-60 | head/committed_head/tail/capacity/record_size/frozen/pad |
| `airy_log_ring_init` | L77 | `alloc_pages` + power-of-2 capacity |
| `airy_log_reserve` | L131 | L145 frozen 检查；L148-157 cmpxchg head；L153-154 满时推进 tail overwrite |
| `airy_log_commit` | L174 | L191 `READ_ONCE(head)`；L192 `smp_store_release(committed_head)`；L195-196 eventfd 通知 |
| `airy_log_write` | L205 | reserve+fill+commit fastpath（~50-100ns） |
| `airy_log_ring_mmap` | L241 | `remap_pfn_range` 零拷贝暴露给 Logger Daemon |
| `airy_log_ring_register_eventfd` | L266 | eventfd 注册（spinlock 保护） |
| `airy_log_ring_freeze` | L291 | `smp_store_release(frozen, 1)` |

**层 2：printk 桥** — [airy_log_kern.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_kern.c)（103 行）：

| 要素 | 行号 | 说明 |
|------|------|------|
| `airy_log_level_map[]` | L37-46 | 8→5 级别映射表 |
| L38-40 | EMERG/ALERT/CRIT → FATAL | 三级合并为 FATAL |
| L43 | NOTICE → INFO | 合并为 INFO |
| `airy_log_kern_to_level` | L56 | 越界返回 INFO |
| `airy_log_emit` | L76 | L92 `vprintk_emit(0, kern_level, NULL, fmt, args)` |
| `late_initcall` | L98-102 | 启动就绪通告 |

**层 3：文件持久化** — [airy_log_persist.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_persist.c)（102 行）：

| 要素 | 行号 | 说明 |
|------|------|------|
| 默认路径 | L25 | `/var/log/airy/airy.log` |
| `DEFINE_MUTEX` | L31 | 串行化 flush/init |
| `airy_log_persist_open` | L34 | `filp_open` O_WRONLY\|O_CREAT\|O_APPEND |
| `airy_log_persist_init` | L44 | 写 session header |
| `airy_log_persist_flush` | L70 | L88-97 循环 `kernel_write`（同步） |

---

## 2. 关键发现

### 2.1 【发现 1】log_ring 满时 overwrite 无溢出计数器/告警

**现状**：[airy_log_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_ring.c) L153-154 在 ring 满时执行 `smp_store_release(&hdr->tail, tail + 1)` 推进 tail 覆盖最旧记录，但**无溢出计数器**（header 结构 L52-60 不含 `dropped` 字段）、**无告警**（不调 `pr_warn`/`pr_debug_ratelimited`）。生产者静默覆盖，消费者无法感知丢失量。

**参考**：openEuler printk ringbuffer 满时通过 `prb_first_seq` 回卷 + `console_seq` 跟踪，并在 `printk_safe` 路径维护 per-CPU 计数；Linux `printk` 还有 `console_dropped_count`/`seq` 机制让用户态感知丢失。seL4 无 ringbuffer 故无此问题。

**风险**：agent RT 系统的日志是故障归因的关键证据。静默覆盖会导致事故后无法判断"丢失了多少记录""丢失了哪个时间窗口"。Micro-Supervisor 据此做"是否升级为 fatal"的裁决时，信息缺失可能误判。

**建议**：(1) 在 `airy_log_ring_header`（L52-60）增加 `__u64 dropped` 字段；(2) L153-154 overwrite 分支原子递增 `dropped`（cmpxchg）；(3) 消费者侧（Logger Daemon）通过 mmap 读取 `dropped` 并周期上报 Macro-Supervisor；(4) 可选：`dropped` 超阈值时 `airy_eventfd_signal_fault` 告警。对应 N12。

**优先级**：P2 · 工作量 2h · 风险低（header 增字段需确认 mmap ABI 兼容，但 M0/M1 阶段无外部消费者）

### 2.2 【发现 2】log_persist 同步 kernel_write，无异步刷盘线程

**现状**：[airy_log_persist.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_persist.c) L70-101 `airy_log_persist_flush` 在 mutex 内同步循环 `kernel_write`（L89），每次 flush 都 `filp_open`（L82）+ N 次 `kernel_write` + `filp_close`（L99）。无后台刷盘线程、无 writeback 合并。

**参考**：openEuler 的 `printk` 持久化由用户态 `klogd`/`journald` 异步消费 ringbuffer，内核侧不直接 `kernel_write` 文件——这避免了在 panic/异常路径里阻塞。seL4 把日志完全留给用户态 component。

**风险**：(1) `kernel_write` 在故障路径可能阻塞（磁盘 IO 慢/文件系统锁），若在 die_notifier 链路里调用会延长 panic 时延；(2) 每次 flush 开关文件描述符开销大；(3) ring 高吞吐时同步 flush 成瓶颈。当前 `airy_log_persist_flush` 仅由显式调用触发（非每条记录），问题被部分缓解，但仍是 M2 之后的可扩展性隐患。

**建议**：M3 引入内核线程 `airy_log_flushd`，ring 用 `eventfd`（已有 L266 注册机制）唤醒 flushd 批量 writeback；短期（M0/M1）文档化"同步 flush 仅用于低频场景（如 session header）"。对应 N17。

**优先级**：P2 · 工作量 4h · 风险中（异步线程涉及停机/同步语义）

### 2.3 【发现 3】log_kern 8→5 级别映射丢失 ALERT/CRIT/NOTICE 粒度

**现状**：[airy_log_kern.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_kern.c) L37-46 `airy_log_level_map[]` 将 printk 8 级压缩为 A-ULP 5 级：

- L38-40 `LOGLEVEL_EMERG/ALERT/CRIT` → `AIRY_LOG_FATAL`（3 级合并为 1）
- L43 `LOGLEVEL_NOTICE` → `AIRY_LOG_INFO`（与 INFO 合并）

**参考**：openEuler printk 全程保留 8 级语义（[printk.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/printk/printk.c) L2316 `vprintk_emit` 透传 level），console_loglevel 按精确级别过滤。seL4 无级别体系。

**风险**：(1) `ALERT`（需立即人工介入）与 `EMERG`（系统不可用）合并为 FATAL，丢失"是否还能救"的区分；(2) `CRIT`（硬件/严重软件故障）与 `ERR` 被拆到 FATAL/ERROR，但 `CRIT` 实际更接近 `ERR` 的严重版而非 `EMERG`；(3) `NOTICE`（正常但显著）与 `INFO`（一般信息）合并，过滤 `INFO` 时会连带丢 `NOTICE`。

**影响**：当前 [airy_log_emit](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_kern.c) L92 实际转发的是**原始 8 级**给 `vprintk_emit`（L89 注释明确说明保留 8 级以便 console_loglevel 生效），映射结果 `airy_level` 仅"计算并丢弃"（L89 `__maybe_unused`）。所以现状的**功能影响为零**，但映射表的**意图**（用于 ring-buffer 路由的 `rec->level`）在落地后会丢失粒度。

**建议**：(1) 短期：保留 5 级映射但文档化"粒度损失是 A-ULP 5 级模型的有意取舍"；(2) 中期：扩展 `airy_log_level` 枚举为 7 级（FATAL/CRIT/ERROR/WARN/NOTICE/INFO/DEBUG），映射表 1:1 对齐 printk 前 7 级，`AIRY_LOG_DEBUG` 仍对应 `LOGLEVEL_DEBUG`；(3) 或保留 5 级但在 ring record 中额外存原始 8 级 `kern_level` 字段，消费者按需还原。对应 N19。

**优先级**：P2 · 工作量 1h · 风险低（M0/M1 阶段映射结果未消费）

### 2.4 正面发现：lock-free ring 内存序正确

[airy_log_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_ring.c) 的三索引 reserve/commit 模型内存序设计正确：

- **reserve**（L148-157）：`smp_load_acquire(&hdr->head)`（L149）+ `smp_load_acquire(&hdr->tail)`（L150）+ `cmpxchg(&hdr->head, head, head+1)`（L157）。满时 `smp_store_release(&hdr->tail, tail+1)`（L154）推进 tail。
- **commit**（L191-192）：`READ_ONCE(hdr->head)` 快照 + `smp_store_release(&hdr->committed_head, pos)` 发布。release 保证 record body 写入先于 committed_head 可见。
- **消费者配对**：注释 L170-171 说明消费者用 `smp_load_acquire(&hdr->committed_head)` 而非 head——head 在 reserve 时推进（body 未填），committed_head 在 commit 时推进（body 已填），正确性成立。
- **freeze**（L145-146/L299）：`READ_ONCE(hdr->frozen)` + `unlikely()` fastpath；`airy_log_ring_freeze` 用 `smp_store_release(&hdr->frozen, 1)` 配对。

这套设计借鉴了 Linux printk ringbuffer 的三索引思路，但用固定 128B 记录简化了 data block 管理。相比第一轮报告中部分子系统的"全局 spinlock 包打天下"，这里是无锁 fastpath + 仅 eventfd 注册用 spinlock（L69/L277），质量明显高于第一轮平均水平。是本轮**最强正面发现**之一。

### 2.5 正面发现：mmap 零拷贝 + eventfd 通知

[airy_log_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_ring.c) L241-258 `airy_log_ring_mmap` 用 `remap_pfn_range` 把 ring pages 直接映射到 Logger Daemon 地址空间，L252 `VM_DONTEXPAND|VM_DONTDUMP` 是合理的 VMA 保护。L266-285 eventfd 注册让消费者被"推送"而非轮询，L282-283 替换旧 ctx 时 `eventfd_ctx_put` 防泄漏。这套"kernel 写 + user mmap 读 + eventfd 唤醒"是 Linux 内核日志的传统优秀模式（cf. `relay`/`relayfs`），Airymax 的实现完整且正确。

---

## 3. 改进点清单

| 编号 | 标题 | 优先级 | 现状行号 | 工作量 |
|------|------|--------|----------|--------|
| N12 | log_ring 满时 overwrite 无溢出计数器/告警 | P2 | [airy_log_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_ring.c) L153-154 | 2h |
| N17 | log_persist 同步 kernel_write，无异步刷盘线程 | P2 | [airy_log_persist.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_persist.c) L70-101 | 4h |
| N19 | log_kern 8→5 级别映射丢失 ALERT/CRIT/NOTICE 粒度 | P2 | [airy_log_kern.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_kern.c) L37-46 | 1h |
| — | lock-free ring 内存序正确（正面） | — | [airy_log_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_ring.c) L148-157/L191-192 | — |
| — | mmap 零拷贝 + eventfd 通知完整（正面） | — | [airy_log_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_ring.c) L241-285 | — |

---

## 4. 小结

Airymax 的三层日志体系（ring/kern/persist）在结构上完整，[airy_log_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_ring.c) 的 lock-free reserve/commit 内存序经核验正确，mmap+eventfd 消费链路完整，质量高于第一轮多数子系统，是本轮正面亮点。三处 P2 发现均为"完整性补齐"而非"设计错误"：N12 加溢出计数器、N17 引入异步刷盘线程、N19 决定级别粒度策略。三者均不阻断 M0/M1，但 N12/N17 建议在 M2/M3 落地以支撑 agent RT 系统的故障归因可靠性。
