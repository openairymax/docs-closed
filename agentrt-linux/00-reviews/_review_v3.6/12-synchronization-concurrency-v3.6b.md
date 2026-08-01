SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 12 — 同步原语与并发正确性（v3.6b 深度对比）

> **文档定位**：agentrt-linux 内核设计深度对比研究 · 第二轮 · 维度 4
> **对比基准**：openEuler kernel-OLK-6.6 · seL4-master · Airymax agentrt-linux
> **最后更新**：2026-07-31
> **方法论**：逐字节阅读三项目源码，所有引用标注文件路径+行号，严禁编造

---

## 0. 摘要

本报告对比三项目的同步原语与并发正确性。openEuler 提供完整 spinlock + RCU + atomic 体系（含 lockdep）；seL4 用单一 CLH `big_kernel_lock` 做粗粒度 SMP 同步；Airymax 并发质量**分层显著**——[airy_log_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_ring.c) 的 lock-free ring 内存序正确（正面），[airy_cap_array.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_array.c) per-bucket 锁已收敛第一轮 P1-11（正面），但 [airy_object.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/object/airy_object.c) 全局单 spinlock + O(N) lookup（N4），[airy_locking.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/locking/airy_locking.c) 无 RCU wrapper（N10），BPF 占位未接入（N9）。

---

## 1. 对比基准

### 1.1 openEuler OLK-6.6 同步体系

| 原语 | 位置 | 行号 | 说明 |
|------|------|------|------|
| `__raw_spin_lock_init` | [spinlock.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/spinlock.h) | L101 | raw spinlock 初始化 |
| `spin_lock_nested` | spinlock.h | L364 | lockdep 注解的层级锁（L366 调 `raw_spin_lock_nested`） |
| `synchronize_rcu` | [rcupdate.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/rcupdate.h) | L45 | 等待所有读者退出 |
| `__rcu_read_lock` | rcupdate.h | L74 | RCU 读侧临界区 |

**特征**：spinlock 带 lockdep 子类注解（`spin_lock_nested` 防 false positive 死锁告警）；RCU 提供无锁读路径，写者 `synchronize_rcu` 等宽限期；atomic 操作（cmpxchg/READ_ONCE/WRITE_ONCE）由 arch 提供。

### 1.2 seL4 同步模型

seL4 SMP 同步用单一 CLH 锁（Craig-Landin-Hagersten 队列锁）：

| 要素 | 位置 | 行号 | 说明 |
|------|------|------|------|
| `big_kernel_lock` | [lock.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/smp/lock.c) | L14 | `clh_lock_t big_kernel_lock` — 全局 BKL |
| `clh_lock_init` | lock.c | L16 | 初始化 CLH 队列（L20-22 per-node myreq，L25 tail=Granted） |
| `CLHState_Granted` | lock.c | L25 | CLH 状态机初始态 |

**特征**：seL4 用**单一全局 BKL** 串行化所有 SMP 内核操作，粗粒度但形式化验证友好（证明简单）。无 RCU，无 lockdep。CLH 锁比简单 test-and-set spinlock 更公平（FIFO 排队，减少缓存抖动）。

### 1.3 Airymax 同步原语

Airymax 同步分三个层次，质量差异显著：

**层次 1：锁框架 wrapper（弱）** — [airy_locking.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/locking/airy_locking.c)

| 要素 | 行号 | 说明 |
|------|------|------|
| `airy_locking_self_lock` | L19 | `DEFINE_SPINLOCK` 自测锁 |
| `airy_locking_init` | L22 | L31-32 self-test（acquire+release），L34 pr_info |
| `airy_spin_lock_nested` | L39 | L41 NULL 检查 + L46 `spin_lock_nested` wrapper |

仅此而已：无 RCU wrapper、无 rwlock wrapper、无 mutex wrapper。

**层次 2：per-bucket 锁（正面）** — [airy_cap_array.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_array.c)

| 要素 | 行号 | 说明 |
|------|------|------|
| `airy_cap_bucket_locks[AIRY_CAP_BUCKET_NR]` | L27-30 | 静态初始化 per-bucket spinlock 数组 |
| `airy_cap_lookup` | L39 | L47 `READ_ONCE(badge)` 无锁查找 |
| `airy_cap_register` | L74 | L85-86 `spin_lock_irqsave` bucket 锁，L107 释放 |

L17-26 注释说明：per-bucket 数组同时被 register 与 derive 路径共享，关闭了两者用不相交锁导致的 TOCTOU 窗口。这是第一轮 P1-11 的正确收敛。

**层次 3：lock-free ring（正面）** — airy_log_ring.c

| 要素 | 行号 | 说明 |
|------|------|------|
| ring header 三索引 | L52-60 | head/committed_head/tail |
| reserve cmpxchg | L131-162 | 无锁预留，满时 L153-154 推进 tail |
| commit smp_store_release | L174-197 | 发布 committed_head |
| 消费 smp_load_acquire | — | 配对 acquire 读 |

内存序正确（详见报告 15）。

**层次 4：全局单锁（弱）** — [airy_object.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/object/airy_object.c)

| 要素 | 行号 | 说明 |
|------|------|------|
| `airy_object_lock` | L29 | `DEFINE_SPINLOCK` 全局单锁 |
| `airy_object_list` | L30 | `LIST_HEAD` 全局链表 |
| `airy_object_register` | L33 | L44 `list_for_each_entry` O(N) 去重 |
| `airy_object_lookup` | L75 | L80 加锁 + L81 O(N) 遍历 |

---

## 2. 关键发现

### 2.1 【发现 1】airy_object.c 全局单 spinlock + O(N) lookup

**现状**：[airy_object.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/object/airy_object.c) L29 单一 `airy_object_lock` 保护全局链表；L44 register 用 O(N) `list_for_each_entry` 去重；L75 lookup 同样 O(N) 遍历并持锁。

**参考**：openEuler 内核对象注册普遍用 `idr`（O(log N) 红黑树）或 `xa`（xarray）；高频读路径用 RCU（[rcupdate.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/rcupdate.h) L45 `synchronize_rcu`）实现无锁读。seL4 用 CSpace（CNode 槽位数组）O(1) 索引。

**风险**：对象数增长后，register/lookup 的 O(N) 持锁遍历成为瓶颈；register 与 lookup 共用同一锁，读写不分离，并发读被串行化。当前对象数少（IPC ring、调度策略实例），暂不致命，但 M3+ 会暴露。

**建议**：改用 `idr` 或 `xarray`（O(log N) 或 O(1)），lookup 路径用 RCU 读（`rcu_read_lock` + `rcu_read_unlock`），register 用 spinlock 写。对应 N4。

**优先级**：P1 · 工作量 8h · 风险中

### 2.2 【发现 2】airy_locking.c 无 RCU wrapper，cap 高频读未利用 RCU

**现状**：[airy_locking.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/locking/airy_locking.c) 仅 `airy_spin_lock_nested` 一个 wrapper（L39-46），无 `airy_rcu_read_lock`/`airy_rcu_read_unlock`/`airy_synchronize_rcu` 封装。[airy_cap_array.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_array.c) L47 `airy_cap_lookup` 用 `READ_ONCE` 做无锁读，但无 RCU 宽限期保护，若 register 路径释放/重分配 slot，读路径可能读到悬空指针。

**参考**：openEuler [rcupdate.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/rcupdate.h) L45 `synchronize_rcu` + L74 `__rcu_read_lock` 是高频读路径的标准无锁方案。seL4 用 BKL 串行化（无 RCU 需求，因粗粒度）。

**风险**：cap lookup 的 `READ_ONCE` 仅保证单次读的原子性，不保证 slot 生命周期。当前 slot 为静态数组（无释放），暂安全；但若 M3 引入动态 cap 回收，需 RCU 保护。

**建议**：在 airy_locking.c 增加 RCU wrapper，cap lookup 改为 `rcu_read_lock` + `READ_ONCE` + `rcu_read_unlock`，register 写侧 `synchronize_rcu`。对应 N10。

**优先级**：P1 · 工作量 6h · 风险中

### 2.3 【发现 3】BPF struct_ops 占位未真正接入

**现状**：[airy_struct_ops.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/bpf/airy_struct_ops.c) L1-61 仅 state machine + register 函数 + state 名 lookup，注释"deferred to integration layer"，未真正调用 `bpf_struct_ops_register()`。[airy_bpf_probe.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/bpf/airy_bpf_probe.c) L1-39 的 `airy_bpf_probe_trace()` 用 pr_info+%pV，非真正 BPF probe（应叫 trace helper）。

**参考**：openEuler BPF 子系统提供完整的 `bpf_struct_ops_register`、`register_bpf_kfunc`、tracepoint 体系。

**风险**：占位文件给读者"已接入 BPF"的错觉。CONFIG_BPF=y 时编译，但运行时无功能。

**建议**：要么 M3 真正接入（实现 `bpf_struct_ops_register` 调用），要么在 Kconfig 加 `depends on BROKEN` 或文件头加显著 `TODO(M3)` 标记。对应 N9。

**优先级**：P1 · 工作量 M3 · 风险低（占位不影响功能，但需避免误导）

### 2.4 正面发现：cap_array per-bucket 锁与 log_ring lock-free

- [airy_cap_array.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_array.c) L27-30 per-bucket 锁比 seL4 [lock.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/smp/lock.c) L14 单一 BKL 更细粒度，且正确关闭了 register/derive TOCTOU（L17-26 注释）。
- airy_log_ring.c 的 cmpxchg + release/acquire 模式是本轮最高质量并发代码，内存序正确。

---

## 3. 改进点清单

| 编号 | 标题 | 优先级 | 现状行号 | 工作量 |
|------|------|--------|----------|--------|
| N4 | airy_object.c 全局单 spinlock + O(N) lookup | P1 | [airy_object.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/object/airy_object.c) L29/L44/L75 | 8h |
| N9 | BPF struct_ops/probe 占位未真正接入 | P1 | [airy_struct_ops.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/bpf/airy_struct_ops.c) L1-61 | M3 |
| N10 | airy_locking.c 无 RCU wrapper，cap 高频读未利用 RCU | P1 | [airy_locking.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/locking/airy_locking.c) L1-47 | 6h |
| — | cap_array per-bucket 锁正确收敛 P1-11（正面） | — | [airy_cap_array.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_array.c) L27-30 | — |
| — | log_ring lock-free 内存序正确（正面） | — | airy_log_ring.c L52-197 | — |

---

## 4. 小结

Airymax 并发质量分层明显：log_ring（lock-free，优）> cap_array（per-bucket，良）> locking（仅 wrapper，中）> object（全局 O(N)，差）。这种分层反映 M0 阶段"按重要性分批实现"的策略——IPC fastpath 和 cap 查找已用最优并发模式，object registry 等低频路径暂用简单实现。建议 M3 前收敛 N4/N10，BPF 占位需明确标记避免误导。
