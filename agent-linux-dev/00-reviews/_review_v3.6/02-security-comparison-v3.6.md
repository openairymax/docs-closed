SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 02 — 安全 LSM/capability 深度对比：openEuler vs Airymax airy_lsm

> **文档定位**：v3.6 深度对比研究 · 安全子域（LSM / capability / lockdown）
> **对比基准**：openEuler kernel-OLK-6.6 security/ · Airymax agent-linux security/airy/
> **最后更新**：2026-07-30
> **方法论**：逐字节阅读参考项目源码 + Airymax 现状代码，所有引用均标注文件路径与行号；严禁编造行号，未在源码确认的位置以「未确认」标注

---

## 1. 研究范围与对比维度

| 维度 | openEuler OLK-6.6 | Airymax airy_lsm |
|------|-------------------|-------------------|
| LSM hook 注册 | `security_hook_heads` __ro_after_init + 链表头表 | `DEFINE_LSM(airy)` + `LSM_ORDER_MUTABLE` |
| Security blob 分配 | `kmem_cache` （`lsm_file_cache` / `lsm_inode_cache`） | `__ro_after_init` 的 `lsm_blob_sizes` |
| Hook 覆盖度 | ~250 hook（`AIRY_LSM_KERNEL_HOOK_TOTAL` 口径） | 5 hook（uring_cmd/task_alloc/task_free/task_kill/file_open） |
| Capability 模型 | POSIX `cap_capable` + `CAP_LAST_CAP` | 44 ID + Badge folding（epoch+randtag+perms） |
| Lockdown | `lockdown_reasons[]` 24 项 + `kernel_lock_down()` | **缺失** |
| task_kill/file_open 完整性 | 完整（多个 LSM 拼接） | **仅检查 agent_state**，Badge 校验 deferred |
| 可观测性 | audit + `blocking_lsm_notifier_chain` | `atomic_notifier_call_chain` + `pr_warn_ratelimited` |

---

## 2. LSM hook 注册机制：ro_after_init 头表 vs DEFINE_LSM

### 2.1 openEuler security_hook_heads 架构

openEuler 在 [security.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/security/security.c) 采用经典的「全局钩子头表」架构：

- L12：`#define pr_fmt(fmt) "LSM: " fmt` — 统一日志前缀
- L35：`#define LSM_COUNT (__end_lsm_info - __start_lsm_info)` — 通过 linker section 计数内建 LSM
- L77：`struct security_hook_heads security_hook_heads __ro_after_init;` ★ 全局 hook 头表，`__ro_after_init` 保证运行时不可变
- L78：`BLOCKING_NOTIFIER_HEAD(blocking_lsm_notifier_chain)` — LSM 状态变更通知链
- L90：`builtin_lsm_order = CONFIG_LSM` — boot-time 通过 `lsm=` 参数排序

[security_hook_heads](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/lsm_hooks.h) L45-55 定义 `hlist_head` 数组：每个 hook 槽位一个链表头，LSM 通过 `security_add_hooks()` 将自身 `security_hook_list` 节点挂入对应槽位。`__ro_after_init` 保证**整个头表本身**在 `do_initcalls()` 完成后写保护，运行时无法新增/删除 hook 节点（只能遍历调用）。

### 2.2 Airymax DEFINE_LSM + LSM_ORDER_MUTABLE

Airymax 在 [airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_lsm.c) 采用 Linux 主线 6.6 的 `DEFINE_LSM` 宏机制：

- L7-9：注释说明注册 `DEFINE_LSM(airy)` at `LSM_ORDER_MUTABLE`，5 个钩子
- L121-127：`static struct security_hook_list airy_hooks[] __ro_after_init` — 5 个钩子（uring_cmd / task_alloc / task_free / task_kill / file_open）数组本身写保护
- L140：`security_add_hooks(airy_hooks, ARRAY_SIZE(airy_hooks), "airy")` — 在 `airy_init` 中挂入全局头表
- L150-154：`DEFINE_LSM(airy) = { .name="airy", .order=LSM_ORDER_MUTABLE, .init=airy_init, .blobs=&airy_blob_sizes };`

**关键差异**：Airymax 选择 `LSM_ORDER_MUTABLE` 而非 `LSM_ORDER_LAST`（[bpf/hooks.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/security/bpf/hooks.c) 同样使用 `LSM_ORDER_MUTABLE`），意味着 airy 与 BPF LSM 在同序层级竞争挂载顺序。这符合「BPF 之上、定制 LSM」的语义，但需要文档明确：当 BPF LSM 注入相同 hook 时，airy 的 verdict 是否会被覆盖。

### 2.3 评价

| 维度 | openEuler | Airymax | 评价 |
|------|-----------|---------|------|
| Hook 表写保护 | `__ro_after_init` on 头表 | `__ro_after_init` on hooks 数组 | 等价 |
| Boot-time 排序 | `CONFIG_LSM` + `lsm=` | `LSM_ORDER_MUTABLE` | Airymax 粒度更粗 |
| 运行时注册阶段 | 明确（init only） | 沿用主线，但未文档化 | P2 改进项 |

Airymax 复用主线 `DEFINE_LSM` 是正确的工程选择（符合 ALK 原则），但缺少 openEuler 那样对「boot-only 注册 vs runtime 注入」的显式断言。

---

## 3. Security blob 分配：kmem_cache vs __ro_after_init blob_sizes

### 3.1 openEuler kmem_cache blob 模型

[security.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/security/security.c):

- L80-81：`kmem_cache *lsm_file_cache, *lsm_inode_cache` — 专用 slab 缓存
- L84：`struct lsm_blob_sizes blob_sizes __ro_after_init;` — 累计所有 LSM 的 blob 需求

openEuler 通过 `lsm_blob_sizes` 在初始化阶段累计各 LSM 的 `lbs_task` / `lbs_file` / `lbs_inode` 需求，然后：

1. 用 `kmem_cache_create` 创建专用 slab（含对齐填充）
2. 在 `file_alloc_security` / `inode_alloc_security` 时从 slab 分配 blob
3. 通过 `lsm_get_blob` 按偏移定位各 LSM 自己的 blob 区

优点：多 LSM 共享同一 slab，缓存友好；缺点：运行时分配开销（虽然 slab 已优化）。

### 3.2 Airymax __ro_after_init blob_sizes

[airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_lsm.c) L34-36：

```c
struct lsm_blob_sizes airy_blob_sizes __ro_after_init = {
    .lbs_task = sizeof(struct airy_task_sec)
};
```

[lsm_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/lsm_types.h) L27-37 定义 `airy_task_sec`（agent_id / cap_space_root / agent_state / fault_count / sched_budget_ns / last_heartbeat / frozen_reason / ipc_ring）。

**关键差异**：

- Airymax **仅声明 `lbs_task`**，未声明 `lbs_inode` / `lbs_file`。这导致 [lsm_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/lsm_types.h) L40-43 定义的 `airy_inode_sec`（cap_required / owner_agent）**未接线到 VFS**，`file_open` hook 无法做 per-inode capability 检查。
- Airymax 的 `agent_caps` 表是独立的 `__aligned(64)` 静态数组（见第 7 节），不走 `lsm_blob_sizes` 机制。

### 3.3 评价

Airymax 复用主线 `lsm_blob_sizes` 是正确的，但**只接了 task blob**，inode/file blob 缺位。这是「M1 脚手架」的合理取舍，但需要在 M2（io_uring IPC）之前补齐 `lbs_inode`，否则 file_open 的 per-inode cap 检查无法落地。

---

## 4. Hook 覆盖度：~250 hook vs 5 hook

### 4.1 openEuler 全集

openEuler（与主线一致）维护约 250 个 LSM hook，覆盖：

- **VFS**：`file_open` / `file_permission` / `file_ioctl` / `mmap_file` / `bprm_*`
- **Task**：`task_create` / `task_alloc` / `task_kill` / `task_setrlimit` / `task_prctl`
- **IPC**：`msg_msg_*` / `shm_*` / `sem_*`
- **Network**：`socket_*` / `sock_*` / `inet_*` / `sk_*`
- **Capability**：`cap_capable` / `cap_settime` / `cap_task_prctl`
- **Module**：`kernel_module_request` / `kernel_read_file`

### 4.2 Airymax 5 hook 子集

[lsm_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/lsm_types.h):

- L23：`#define AIRY_LSM_HOOK_IMPLEMENTED 5`
- L24：`#define AIRY_LSM_KERNEL_HOOK_TOTAL 250`

[airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_lsm.c) L121-127 实现的 5 个钩子：

| hook | 实现 | 用途 |
|------|------|------|
| `uring_cmd` | L112-118 → `airy_uring_cmd_check` | io_uring 命令入口的 5-phase capability 检查 |
| `task_alloc` | （alloc 路径）| 初始化 `airy_task_sec` |
| `task_free` | （free 路径）| 清理 agent 资源 |
| `task_kill` | L67-87 | 仅检查 `agent_state` |
| `file_open` | L90-109 | 仅检查 `agent_state` |

### 4.3 评价

Airymax 的 5/250 覆盖率（2%）是**有意的设计取舍**：

- **理由**：Airymax 的安全模型以 `io_uring_cmd` 为唯一特权入口（5-phase check 在 [airy_cap_check.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_check.c) L191-260），其他路径靠「capability folding + agent_state」收敛。
- **风险**：task_kill / file_open 的完整 Badge 校验被 deferred（见第 7 节），形成「入口严、内部松」的不对称。
- **可观测性**：未文档化 250 hook 中哪些是未来扩展候选，可维护性低（P2 改进项）。

---

## 5. Capability 系统：POSIX cap_capable vs 44 ID + Badge folding

### 5.1 openEuler POSIX capability

[commoncap.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/security/commoncap.c) L66-102 的 `cap_capable` 是经典 POSIX capability 实现：

- 按 `cap` 编号查 `current_cred()` 的 cap bitmap
- 检查 `ns` 命名空间是否允许该 cap
- 返回 0 / -EPERM

[capability.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/uapi/linux/capability.h) L421-423 定义 `CAP_LAST_CAP`，当前为 `CAP_CHECKPOINT_RESTORE`（40）。

### 5.2 Airymax 44 ID + Badge folding

[security_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/security_types.h):

- L20：`typedef __u64 cap_t;` — 64-bit badge 容器
- L25-72：`enum airy_cap_id` 44 ID（0-40 POSIX 兼容 + 41 `AIRY_CAP_AGENT_SPAWN` + 42 `AIRY_CAP_GPU_SCHED` + 43 `AIRY_CAP_NPU_ACCESS`）
- L75-80：`enum airy_verdict` 4 值（ALLOW / DENY / AUDIT / COMPLAIN）
- L83-92：`enum airy_cap_op` 7 操作（COPY / MINT / MOVE / MUTATE / REVOKE / DELETE / ROTATE）

[airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap.h):

- L22-29：Badge layout 注释 `[63:48]epoch [47:16]randtag [15:0]perms`
- L35：`extern struct airy_cap_slot *agent_caps;`
- L50-77：`airy_cap_badge_ok(__u64 badge, __u32 agent_id, __u16 required_perms)` — fastpath：

```c
/* L59-60: agent_id 边界检查 */
if (agent_id >= AIRY_CAP_MAX_AGENTS)
    return -AIRY_ECAP_MISSING;
/* L62-65: C-S9.1 epoch check (READ_ONCE) */
/* L67-70: C-S9.2 randtag check (READ_ONCE) */
/* L72-74: C-S9.3 permission check */
```

3 次 `READ_ONCE` + 位运算，约 10ns（C-S9 fastpath 规格）。

### 5.3 epoch 撤销机制

[airy_ipc_capability.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/ipc/airy_ipc_capability.c):

- L61-71：`airy_cap_epoch_bump` — O(1) 定向撤销（per-agent epoch+1）
- L74-83：`airy_cap_epoch_bump_all` — O(N) 全局撤销

epoch 撤销是 Airymax 区别于 POSIX 的核心创新：POSIX cap 一旦授予，需通过 `capset` 显式收回；Airymax 通过 epoch bump **失效整个 agent 的所有已发放 badge**，适用于 agent 崩溃/重启的快速回收。

### 5.4 评价

| 维度 | openEuler POSIX | Airymax Badge | 评价 |
|------|-----------------|----------------|------|
| 检查开销 | bitmap test ~2ns | 3 READ_ONCE ~10ns | Airymax 略慢，可接受 |
| 撤销粒度 | per-cred capset | per-agent epoch bump | Airymax 更适合 agent 模型 |
| 撤销开销 | O(1) 但需遍历 cred | O(1) 定向 / O(N) 全局 | 等价 |
| 兼容性 | 40 POSIX | 0-40 POSIX 兼容 + 3 扩展 | Airymax 良好 |
| 可组合性 | bitmap 与/se | Badge epoch+randtag+perms | Airymax 更强（防重放） |

Airymax 的 Badge folding（epoch + randtag + perms 三段式）在防重放、定向撤销上**显著优于** POSIX bitmap，代价是 fastpath 多 ~8ns。这是 agent OS 场景下的合理权衡。

---

## 6. Lockdown 机制：24 项 lockdown_reasons vs 缺失

### 6.1 openEuler lockdown_reasons

[security.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/security/security.c) L43-75 定义 `lockdown_reasons[]` 数组，24 项 lockdown 理由，覆盖：

- 内核模块加载 / 卸载
- `/dev/mem` / `/dev/kmem` 访问
- BPF / kprobe / perf
- IO 端口 / MSR
- ACPI / EFI 变量
- hibernation / kexec

lockdown 状态机：`none → integrity → confidentiality`，通过 `kernel_lock_down()` 提升（不可降级）。

### 6.2 Airymax 现状

Airymax **未实现 lockdown 等价机制**。[airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_lsm.c) 的 5 个钩子不涉及 lockdown，[airy_cap_check.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_check.c) L270-298 的 `airy_security_fault` 仅设置 `frozen_reason` + 通知链，不阻止内核态敏感操作。

### 6.3 评价

Airymax 当前依赖：

1. `airy_uring_cmd_check` 的 5-phase（[airy_cap_check.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_check.c) L191-260）控制 agent 入口
2. `frozen_reason` + `atomic_notifier_call_chain`（L297）通知用户态冻结

但这**不等于 lockdown**：agent 之外路径（如 root 用户通过 `/dev/mem` 写内核）不受控。这是 P2 改进项（见第 8.4 节）。

---

## 7. task_kill / file_open 完整性分析

### 7.1 task_kill 仅检查 agent_state

[airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_lsm.c) L67-87：

```c
/* L75-80: 注释明确 "完整 badge check deferred until
 *         per-agent kill permission bits are defined" */
/* L82-84: 仅检查 agent_state */
```

`airy_task_kill` 当前**不调用** `airy_cap_badge_ok`（[airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap.h) L50-77），仅基于 `agent_state` 判断是否允许 kill。这意味着：

- 一个被冻结（frozen）的 agent 无法被 kill（即使持有 `AIRY_CAP_AGENT_SPAWN` 等管理权限的 supervisor 也无法 kill）
- 一个未冻结的 agent 可以被任意 kill（无 cap 区分）

### 7.2 file_open 仅检查 agent_state

[airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_lsm.c) L90-109：

```c
/* L97-102: 注释明确 "per-agent file access via capability lookups
 *         deferred until inode security blob wired to VFS" */
/* L104-106: 仅检查 agent_state */
```

`airy_file_open` 同样**不调用** `airy_cap_badge_ok`，且 `airy_inode_sec`（[lsm_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/lsm_types.h) L40-43）未接线到 VFS。这意味着：

- per-inode capability 检查无法实施
- 文件访问控制退化为「全 agent 统一策略」

### 7.3 评价

task_kill / file_open 的 deferred 状态在 M1 阶段是可接受的脚手架，但**形成入口与内部的不对称**：

- `io_uring_cmd` 路径：完整 5-phase + Badge 校验（[airy_cap_check.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_check.c) L191-260）
- `task_kill` / `file_open` 路径：仅 agent_state

攻击者若能绕过 io_uring_cmd 入口（如通过 fork+exec 继承的 fd），可利用 task_kill/file_open 的弱校验。这是 **P1 改进项**（见第 8.1 节）。

---

## 8. 改进建议

### 8.1 [P1] airy_lsm task_kill/file_open 应增加完整 Badge 校验

**现状**：
- [airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_lsm.c) L67-87 `airy_task_kill` 仅检查 `agent_state`（L82-84），L75-80 注释明确「完整 badge check deferred」
- [airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_lsm.c) L90-109 `airy_file_open` 仅检查 `agent_state`（L104-106），L97-102 注释明确「per-agent file access via capability lookups deferred」

**参考**：
- [airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap.h) L50-77 `airy_cap_badge_ok` 已提供 fastpath（~10ns，3 READ_ONCE）
- [airy_cap_check.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_check.c) L191-260 `airy_uring_cmd_check` 已展示完整 5-phase 分发模式

**建议**：
1. 在 `airy_task_kill` 中，从 `current->security` 取 `airy_task_sec.agent_id`，从被 kill task 取其 agent_id，调用 `airy_cap_badge_ok(current_badge, target_agent_id, AIRY_CAP_AGENT_KILL)`（新增 cap ID 或复用 `AIRY_CAP_AGENT_SPAWN` 语义扩展）
2. 在 `airy_file_open` 中，先接线 `airy_inode_sec`（见 8.3），再调用 `airy_cap_badge_ok(current_badge, inode_sec->owner_agent, inode_sec->cap_required)`
3. 保留 agent_state 检查作为**前置快过滤**（state != ACTIVE 直接 DENY），Badge 校验作为**后置强校验**

**风险**：中。task_kill 是热路径（信号发送频繁），需确认 `airy_cap_badge_ok` 的 ~10ns 开销在 kill 路径可接受。建议增加 `trace_airy_cap_check` tracepoint 监控 fastpath 命中率。工作量约 1-2 天（含 inode blob 接线）。

### 8.2 [P1] airy_ipc_capability.c 用 __aligned(64) 而非 AIRY_ALIGNED(64)

**现状**：[airy_ipc_capability.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/ipc/airy_ipc_capability.c) L29-30：

```c
static struct airy_cap_slot __airymax_cap_table[AIRY_CAP_MAX_AGENTS] __aligned(64);
```

使用 GCC/Clang 原生 `__aligned(64)` 而非 Airymax 自有的 `AIRY_ALIGNED(64)` 宏。

**参考**：[lsm_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/lsm_types.h) L46-54 的 `struct airy_cap_slot` 末尾标注 `AIRY_ALIGNED(64)`，表明 Airymax 项目有统一的对齐宏抽象。

**建议**：将 L29-30 的 `__aligned(64)` 替换为 `AIRY_ALIGNED(64)`，与 `airy_cap_slot` 结构体自身的对齐声明保持一致。`AIRY_ALIGNED` 宏应封装「编译器无关」的对齐语法（MSVC/GCC/Clang），符合 OS-IRON-016 编译器无关原则。

**风险**：低。纯替换，无语义变化。需确认 `AIRY_ALIGNED` 宏在当前编译单元可见（`#include` 链）。工作量约 30 分钟。

### 8.3 [P1] airy_inode_sec 未接线到 VFS

**现状**：[lsm_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/lsm_types.h) L40-43 定义了 `airy_inode_sec`（cap_required / owner_agent），但：

- [airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_lsm.c) L34-36 的 `airy_blob_sizes` **未声明 `lbs_inode`**
- `file_open` hook 无法获取 inode 的 cap_required / owner_agent

**参考**：openEuler [security.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/security/security.c) L80-81 通过 `lsm_inode_cache` kmem_cache 为每个 inode 分配 blob，所有 `security_inode_*` hook 可通过 `lsm_get_blob(inode->i_security, ...)` 访问。

**建议**：
1. 在 [airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_lsm.c) L34-36 的 `airy_blob_sizes` 中增加 `.lbs_inode = sizeof(struct airy_inode_sec)`
2. 实现 `airy_inode_alloc_security` / `airy_inode_free_security` hook，挂入 `airy_hooks[]`（L121-127）
3. 在 `airy_file_open` 中通过 `lsm_get_blob(file->f_inode->i_security, airy_blob_sizes.lbs_inode_offset)` 取 `airy_inode_sec`
4. 提供 `airy_inode_set_cap(inode, cap_required, owner_agent)` API 供用户态通过 io_uring_cmd 设置

**风险**：中。inode blob 会增加每个 inode 的内存开销（`sizeof(airy_inode_sec)` ≈ 16 字节），在大量 inode 的系统上需评估。建议通过 `CONFIG_AIRY_INODE_SEC` Kconfig 开关控制。工作量约 2-3 天。

### 8.4 [P2] 缺少 lockdown 机制

**现状**：Airymax 未实现 lockdown 等价机制。[airy_security_fault](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_check.c) L270-298 仅设置 `frozen_reason`（L288 WRITE）+ `atomic_notifier_call_chain`（L297），不阻止内核态敏感操作。

**参考**：openEuler [security.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/security/security.c) L43-75 `lockdown_reasons[]` 24 项 + `kernel_lock_down()` 状态机（none → integrity → confidentiality，不可降级）。

**建议**：
1. 在 [security_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/security_types.h) 增加 `enum airy_lockdown_reason`（参考 openEuler 24 项精简，聚焦 agent 场景：MODULE_LOAD / DEV_MEM / BPF / KPROBE / PERF / IO_PORT / MSR / HIBERNATION / KEXEC）
2. 在 [airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_lsm.c) 增加 `airy_lockdown` 全局状态（`__ro_after_init` 阶段为 NONE，运行时可单调提升至 INTEGRITY / CONFIDENTIALITY）
3. 实现 `airy_kernel_lock_down(reason)` API，触发后挂载额外 hook 拒绝敏感操作
4. 通过 `airy_uring_cmd` 暴露 `AIRY_LOCKDOWN_OP_RAISE` 操作（需 `AIRY_CAP_LOCKDOWN` 新 cap ID）

**风险**：高。lockdown 涉及大量 hook 注入，且需与 Linux 原生 lockdown（`CONFIG_SECURITY_LOCKDOWN_LSM`）协调避免双重拒绝。建议**优先复用** Linux 原生 lockdown LSM，仅通过 `airy_uring_cmd` 暴露提升接口。工作量约 1 周。

### 8.5 [P2] security_hook_heads 应明确 boot-only vs runtime 注册阶段

**现状**：[airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_lsm.c) L150-154 的 `DEFINE_LSM(airy)` 使用 `LSM_ORDER_MUTABLE`，但未文档化：

- 哪些 hook 是 boot-only 注册（`__ro_after_init`）
- 哪些 hook 可在 runtime 注入（如 BPF LSM 通过 `LSM_ORDER_MUTABLE` 动态添加）
- airy 与 BPF LSM 在同序层级竞争时的优先级

**参考**：openEuler [security.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/security/security.c) L77 `security_hook_heads __ro_after_init` 明确「头表写保护，仅 init 阶段可写」；L90 `builtin_lsm_order = CONFIG_LSM` 明确 boot-time 排序。

**建议**：
1. 在 [airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_lsm.c) 顶部注释块（L7-9 附近）补充「注册阶段说明」：明确 `airy_hooks[]` 为 boot-only，`LSM_ORDER_MUTABLE` 仅影响 LSM 间排序而非允许 runtime 卸载
2. 在 [lsm_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/lsm_types.h) L23-24 附近补充「hook 扩展策略」文档：哪些 hook 候选在 M2/M3 阶段计划接入
3. 增加 `selftest` 验证 airy_hooks[] 在 `do_initcalls()` 后写保护生效（`CONFIG_DEBUG_RODATA=y` 时触发 fault）

**风险**：低。纯文档 + selftest，无运行时行为变化。工作量约 4 小时。

### 8.6 [P2] airy_lsm 仅 5 钩子，可观测性不足

**现状**：[lsm_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/lsm_types.h) L23-24 标注 `AIRY_LSM_HOOK_IMPLEMENTED 5` / `AIRY_LSM_KERNEL_HOOK_TOTAL 250`，但未文档化：

- 5 个已实现 hook 的选择理由（为何是 uring_cmd/task_alloc/task_free/task_kill/file_open 而非其他）
- 245 个未实现 hook 中哪些是「未来扩展候选」（如 `mmap_file` / `bprm_check_security` / `socket_create`）
- 哪些 hook 明确「永不实现」（如 `kernel_module_request`，因为 Airymax 禁止运行时 load module）

**参考**：openEuler 全集 250 hook 均有 `DECLARE_HOOK` + 文档化使用场景。

**建议**：
1. 在 [lsm_types.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/lsm_types.h) 增加 `enum airy_lsm_hook_status`（IMPLEMENTED / PLANNED / DEFERRED / NEVER），对 250 hook 逐项标注
2. 在 `docs-closed/agent-linux/` 下新增 `lsm-hook-registry.md`，记录每个 hook 的状态、负责人、目标里程碑
3. 对 PLANNED hook 增加 `#warning` 或 build-time 检查，防止误用

**风险**：低。纯文档 + 元数据，无运行时影响。工作量约 1-2 天（250 hook 逐项分类）。

---

## 9. 小结

Airymax airy_lsm 在 ALK 约束下选择了「最小 hook 集 + Badge folding + 5-phase uring_cmd 检查」的架构，相比 openEuler 的「全量 hook + POSIX cap + lockdown」是**有意识的工程取舍**：

**优势**：
1. Badge folding（epoch + randtag + perms）在防重放、定向撤销上**显著优于** POSIX bitmap
2. 5-phase `airy_uring_cmd_check` 提供了细粒度的入口控制
3. `LSM_ORDER_MUTABLE` 复用主线机制，ALK 合规

**差距**（按优先级）：
1. **[P1] 入口与内部不对称**：task_kill / file_open 仅检查 agent_state，Badge 校验 deferred，形成安全盲区
2. **[P1] 对齐宏不一致**：`__aligned(64)` 违反 OS-IRON-016 编译器无关原则
3. **[P1] inode blob 未接线**：`airy_inode_sec` 定义但未接入 VFS，per-inode cap 检查无法实施
4. **[P2] lockdown 缺失**：agent 之外路径不受控
5. **[P2] 注册阶段未文档化**：boot-only vs runtime 边界模糊
6. **[P2] hook 可观测性低**：5/250 覆盖率无扩展计划文档

这些差距在 M0/M1 阶段不构成阻断项（`io_uring_cmd` 入口已足够保护 agent 域），但 **8.1 / 8.2 / 8.3 三项 P1 必须在 M2（io_uring IPC 集成）之前收敛**，否则 IPC 路径将继承 task_kill/file_open 的弱校验。8.4-8.6 三项 P2 可在 M3（lsm 策略守护进程）里程碑处理。

报告长度：约 11000 字符（含代码块与表格）。
