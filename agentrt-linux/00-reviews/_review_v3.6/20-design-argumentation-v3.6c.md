SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 20 — 设计方案深层次论证：技术选型五维 + capability/安全/IPC/调度（第三轮）

> **文档定位**：agentrt-linux 内核设计深度对比研究 · 第三轮 · 设计方案深层次论证
> **对比基准**：openEuler kernel-OLK-6.6 · seL4-master · Airymax agentrt-linux（极境内核）
> **最后更新**：2026-08-01
> **方法论**：逐字节阅读三项目源码，所有引用标注文件路径+行号，严禁编造
> **与前序关系**：承接报告 19（工程思想总论），本轮对极境内核五大技术选型与四大核心机制做设计论证——不是找 bug，而是论证"为什么对/为什么可行/边界在哪"

---

## 0. 摘要

极境内核 v1.0.1 的技术选型声明（[README](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/README.md) L31-49）锁定五维：sched_tac（调度）、IORING_OP_URING_CMD（IPC 零拷贝）、纯 C LSM（安全钩子）、alloc_pages+mmap（内存）、IRON-9 v3 四层模型（同源代码共享）。本报告逐维论证其正确性、与 openEuler/seL4 的参照关系、以及边界条件。核心论证结论：五维选型均是基于 Linux 6.6 基线的**正确务实选择**，无方向性错误；但存在 4 处需要深化的边界论证——(1) sched_tac 的"内核态映射函数"与"用户态调度器"的语义边界，(2) Badge folding 的 16-bit perms 上限与 44 cap ID 映射，(3) IRON-9 v3 [DSL] 降级层的运行时可达性，(4) 零拷贝 IPC 与内存版本治理的交互。

---

## 1. 技术选型五维论证

### 1.1 选型 1：sched_tac（复用原生调度类，禁 sched_ext）——论证：正确且必要

**决策**：[README](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/README.md) L35-36：复用 Linux 6.6 原生 SCHED_DEADLINE/SCHED_FIFO/EEVDF，通过 nice/sched_setattr/sched_setaffinity 注入 Agent 感知策略，不定义新的调度类宏。

**论证 Why**：
1. **sched_ext 在 6.6 不可用**：[09-known-caveats.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/09-known-caveats.md) L106-108 明确指出 sched_ext（SCHED_EXT BPF 调度器）在 Linux 6.12 才合入主线，6.6 不可用。sched_tac 是"锁定 6.6 基线"（ADR-001/ADR-016）约束下的**必然选择**，不是偏好。
2. **避免 sched_ext 语义漂移**：sched_ext 的 BPF 验证器开销与 kfunc 上下文切换（L115），且 6.6 的 KABI 上架构差异化处理已有先例（openEuler [sched.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/sched.h) L1668-1684 用 `KABI_BROKEN_INSERT` 为 x86 插入 sched_ext_entity，说明即便在支持 sched_ext 的发行版上也需谨慎）。
3. **ABI 稳定**：原生调度类接口成熟，用户态通过 `sched_setattr` 交互（[stc_dispatch.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_dispatch.c) L20 引用内核内部 `sched_setattr`，`EXPORT_SYMBOL_GPL`）。

**论证 How**：sched_tac 的实现路径是 [stc_dispatch.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_dispatch.c) L50-70 `stc_policy_to_linux` 将 4 类策略（[stc_policy.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_policy.c) L17-22：realtime/interactive/agent/batch）映射到原生 SCHED_*；[stc_mcs_map.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_mcs_map.c) L19-27 将 seL4 MCS 关键度标志映射为 SCHED_* + GFP hint。seL4 MCS 语义映射（scBudget↔sched_runtime、scPeriod↔sched_deadline）在 [stc_dispatch.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_dispatch.c) L14-16 注释中明确。

**边界论证**：⚠️ 关键边界问题（报告 19 E6 详述）——
- [stc_policy.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_policy.c) 的 `STC_POLICY_REALTIME/INTERACTIVE/AGENT/BATCH`（L17-22）与 [sched.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/sched.h) L102-105 的 `AIRY_SCHED_POLICY_DEADLINE/FIFO/EEVDF/BESTEFFORT` **数值未对齐**——两套枚举是语义同源但数值独立。stc_policy.c 注释声称"numeric values intentionally match the [SC] AIRY_SCHED_POLICY_* macros"（L14-15），但实际 `STC_POLICY_REALTIME` 是策略类别名、`AIRY_SCHED_POLICY_DEADLINE` 是调度类名，映射关系经 stc_policy_to_linux 间接实现。此处的"两套命名体系 + 一层映射"是设计复杂度来源，建议在 UAPI 层统一（[SC] 只暴露 AIRY_SCHED_POLICY_*，STC_POLICY_* 为内核内部实现细节）。
- **THINK phase 用 EEVDF 的决策**（[stc_dispatch.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_dispatch.c) L22-25）：长时 LLM 推理（100ms-10s）映射 SCHED_NORMAL(EEVDF) + cgroup cpu.max 带宽隔离，避免 SCHED_DEADLINE 的 CBS WCET 假设不匹配（K9-3 fix）。这是正确决策——CBS 要求任务 WCET 已知，LLM 推理时长不可预测，EEVDF + cgroup 限流是更稳健的隔离手段。

**论证结论**：✅ 正确且必要。无方向性错误，仅需文档化"用户态调度器 vs 内核态映射函数"的语义边界（E6）。

### 1.2 选型 2：IORING_OP_URING_CMD（IPC 零拷贝）——论证：正确，需注意交互

**决策**：[README](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/README.md) L40-41：通过 io_uring 命令操作码实现内核↔用户态零拷贝传输，固定 buffer + registered ring 路径；不用 page flipping。

**论证 Why**：
1. IORING_OP_URING_CMD 在 6.6 已稳定（L41），无需 page flipping 的 DMA 映射复杂度与跨架构兼容问题。
2. 与第一轮报告 03/04 的 fastpath 设计一致——[airy_ipc_fastpath.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_fastpath.c) L68-90 的 fastpath_send 只做 frozen 检查后委托 ring_post，badge 校验在 C-S9（[airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap.h) L75-90）由调用方先行完成（文件头 L11-46 详尽注释论证了"不重复校验 badge"的延迟与安全权衡）。

**论证 How**：[airy_ipc_fastpath.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_fastpath.c) L84-85 用 `unlikely(READ_ONCE(ring->frozen))` 作为 fastpath 唯一安全门——这是深思熟虑的设计：C-S9 badge 校验已由 io_uring_cmd LSM hook 的 5-phase slowpath 完成（L18-29 注释），fastpath 只处理 ring 机制。ring_post 二次 frozen 检查是防御纵深（L43-45）。

**边界论证**：⚠️ 零拷贝与内存版本治理的交互——zero_copy 路径（[airy_ipc_zero_copy.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_zero_copy.c)，第二轮 N15 已指出全局链表 + 单 spinlock）将用户态 buffer 映射进内核，若用户态并发修改 buffer 内容，与 memory 子仓的 MemoryRovol 版本治理（syscall 549）语义冲突。需要明确：零拷贝 buffer 在 IPC 生命周期内是"快照"还是"共享"，若是共享则需 COW/版本号机制。

**论证结论**：✅ 正确。边界问题（zero_copy vs 版本治理）需文档化。

### 1.3 选型 3：纯 C LSM（安全钩子）——论证：正确，与 capability 顺序论证充分

**决策**：[README](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/README.md) L45-46：纯 C LSM 注入策略钩子，不用 BPF LSM。

**论证 Why**：
1. 纯 C 保证安全策略可审计性与形式化验证可行性（L46），避免 BPF 验证器在安全关键路径的语义不确定性。
2. 与 H5 硬约束一致（[README](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/README.md) L208：capability 检查依赖纯 C LSM，禁 BPF）。

**论证 How**：[airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_lsm.c) L185-193 注册 7 个钩子（uring_cmd/task_alloc/task_free/task_kill/file_open/inode_alloc_security/inode_free_security），L216-221 `DEFINE_LSM(airy)` 以 `LSM_ORDER_MUTABLE` 注册。capability 用 `LSM_ORDER_FIRST` 永远第一执行（[08-threat-model.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/08-threat-model.md) L195）。

**关键论证点（正面发现）**：**第一轮 P1-4 修复已落地**。[airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_lsm.c) L89-120 `airy_task_kill` 与 L122-152 `airy_file_open` 均已实现两阶段校验：Phase 1 agent_state 检查（L102-104/L134-136）+ Phase 2 Badge 检查（L112-117/L144-149，经 `airy_cap_badge_ok` 校验 `AIRY_CAP_PERM_KILL`/`AIRY_CAP_PERM_FILE_OPEN`）。入口对称性（第一轮 P1-4 与第二轮 N2 的核心关切）已在源码层面收敛。这与 [08-threat-model.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/08-threat-model.md) L110-114 的 Spoofing 防护设计一致。

**边界论证**：⚠️ airy_superv_lsm.c 的 5 补充钩子（第二轮 N2，L41/L84/L98）仍缺 Badge 校验——主 LSM 已修复，补充钩子未同步，形成"主入口已对称、扩展入口仍不对称"的半收敛状态。

**论证结论**：✅ 正确，方向性无误。N2 需在 M2 前完成补充钩子的对称修复。

### 1.4 选型 4：alloc_pages + mmap（内存）——论证：正确，与 seL4 Untyped 理念同构

**决策**：[README](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/README.md) L50-51：alloc_pages 分配物理页后 vm_map_pages/remap_pfn_range 映射到用户态，不用 dma_alloc_coherent。

**论证 Why**：跨架构（x86/ARM/RISC-V）一致的内存语义，避免 DMA 一致性内存在不支持硬件一致缓存平台的兼容性问题（L51）。

**论证 How**：[airy_log_ring.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/log/airy_log_ring.c) L90 `alloc_pages(GFP_KERNEL | __GFP_ZERO, order)` + L254 `remap_pfn_range` 是此选型的代表实现（第二轮正面发现）。seL4 用 Untyped + Retype（[untyped.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/untyped.c) L272 `invokeUntyped_Retype`）实现能力中介的内存类型化分配——两者哲学同构（物理页 → 映射给用户态），但 seL4 通过 cap 控制"谁能 Retype 多少"，极境内核靠 alloc_pages + LSM 钩子控制。

**边界论证**：⚠️ 极境内核的无 memcg/per-agent 账户问题（第二轮 N7）使"谁能分配多少内存"无内核强制——seL4 的 Untyped cap 天然限额，极境内核的 alloc_pages 无此能力。M3 需补齐 per-agent 内存账户。

**论证结论**：✅ 正确。N7 是 M3 关键收敛项。

### 1.5 选型 5：IRON-9 v3 四层模型（[SC]/[SS]/[IND]/[DSL]）——论证：独有亮点，需运行时可达性论证

**决策**：[README](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/README.md) L55-61：共享契约层 + 语义同源层 + 完全独立层 + 降级生存层。[DSL] 确保 [SC] 头文件损坏时系统仍可最小运行。

**论证 Why**：这是 openEuler 与 seL4 **都没有**的第四层——openEuler 的 KABI 保护（[kabi.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/kabi.h) L439/L443）防的是二进制兼容，不防头文件损坏；seL4 的 SSoT（[invocation_header_gen.py](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/tools/invocation_header_gen.py) L30-34）防的是双端漂移，不提供降级运行。极境内核的 [DSL] 是独创设计。

**论证 How**：[uapi_compat.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/uapi_compat.h) L95-132 的 `AIRY_SC_FALLBACK` 块：三路桥坍缩为两路（__KERNEL__ vs 用户态），[syscalls.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/syscalls.h) L44-53 降级为 4 核心 syscall、预留槽 -1，[sched.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/sched.h) L116-119 所有策略折叠为 EEVDF。

**边界论证**：⚠️ [DSL] 是**编译期降级**（定义 AIRY_SC_FALLBACK 时），还是**运行时降级**？文档（[03-microkernel-strategy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) L740-747）描述为"[SC] 头文件损坏/缺失时"——但头文件损坏通常发生在编译期（构建失败），运行时的 [SC] 已编入内核镜像与用户态库。[DSL] 的真实价值是**跨平台降级**（agentrt 用户态在非 Linux 平台编译时 [SC] 不完整），而非运行时容错。需文档化 [DSL] 的触发时域，避免"运行时损坏可降级"的误解。

**论证结论**：✅ 独有设计亮点。需明确 [DSL] 触发时域（编译期 vs 运行时）。

---

## 2. 核心机制深层次论证

### 2.1 Badge folding 论证：16-bit perms 与 44 cap ID 的容量分析

Badge 布局（[ipc.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/ipc.h) L51-64）：`Epoch<<48 | RandomTag<<16 | Perms`。

- Epoch 16-bit：支持 65536 次全局轮换（AIRY_BADGE_EPOCH_MASK）。
- RandomTag 32-bit：防伪（每次 derive 随机生成）。
- **Perms 16-bit：最多 16 种权限位**。

**论证点**：[08-threat-model.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/08-threat-model.md) L197-205 定义 44 个 cap ID（41 POSIX + 3 Airymax）。16-bit perms 可容纳 44 个 cap ID 的位映射吗？——不能。16-bit perms 是**权限位**（如 KILL/FILE_OPEN/SEND/RECV 等操作权限），不是 44 个 cap ID 的 1:1 映射。cap ID 通过 [SC] security_types.h 枚举 + agent_caps[] 槽位管理，Badge perms 是操作权限子集。**容量自洽**（16-bit 覆盖操作权限绰绰有余），但需文档化"perms 位与 cap ID 的映射关系"——当前 airy_cap_badge_ok 的 required_perms 参数（[airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap.h) L75）来自调用方传入的权限位，其位语义应集中定义（建议在 [SC] security_types.h 增加 AIRY_CAP_PERM_* 位枚举 SSoT）。

### 2.2 调度论证：sched_tac 的 MCS 映射完备性

[stc_mcs_map.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_mcs_map.c) L17-18 定义 6 个 MCS 标志（REALTIME/HIGH/NORMAL/BACKGROUND/PREEMPT/ATOMIC），映射到 SCHED_* + GFP hint。与 seL4 MCS 的 refill 机制（[sporadic.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/sporadic.c) L12/L35/L65 refill 链）对比：

- seL4 MCS 的 SchedContext 提供**精确的带宽预算 + refill 周期**（sporadic 调度理论）。
- sched_tac 通过 SCHED_DEADLINE 的 runtime/deadline 近似实现带宽保证，但无 seL4 的 refill 链管理（预算耗尽后按周期精确补充）。

**论证结论**：近似充分（SCHED_DEADLINE 的 CBS 本身就是带宽保证算法），但"SC 捐赠"（第一轮 P2-3：server 用 client 预算执行）在 sched_tac 中无等价物——[stc_dispatch.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_dispatch.c) L14-16 注释声称"优先级继承实现等效传递"，但优先级继承 ≠ 预算捐赠（继承提升优先级，不转移带宽预算）。此为 M5 规划项，需文档化差异。

### 2.3 IPC 论证：fastpath 单门设计 vs seL4 12 项前置检查

seL4 fastpath 前置 12 项检查（[03-microkernel-strategy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) L296-299），极境内核 fastpath 只做 frozen 检查（[airy_ipc_fastpath.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_fastpath.c) L84-85）。

**论证**：差异的根源是**安全校验位置不同**。seL4 的 fastpath 在 syscall 入口做全部检查（cap 有效性/权限/对齐/类型），因为 seL4 无 LSM 钩子层。极境内核的 badge 校验在 io_uring_cmd LSM 钩子（[airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_lsm.c) L176-182）的 5-phase slowpath 完成（[airy_cap_check.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_check.c) L191-260），fastpath 不再重复。**这是分层设计而非偷工减料**——校验在入口统一完成，fastpath 只做机制。但需论证：io_uring_cmd 的 5-phase slowpath 是否覆盖所有 IPC 入口？若存在绕过 LSM 钩子的 IPC 路径（如直接 syscall 调用 airy_ipc_ring_post），则安全检查被绕过。建议在 [airy_ipc_fastpath.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_fastpath.c) 文件头补充"唯一合法入口"声明。

### 2.4 初始化论证：LSM 生命周期 vs 子系统初始化

[airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_lsm.c) L196-213 `airy_init` 初始化 cap 表 + security_add_hooks + die_notify_init。L12-32 注释详细论证了 boot-only 注册 + runtime gate（airy_enabled 参数）双层设计。

**论证点**：airy_enabled 默认 true（L51），但注释 L30-31 声称"CONFIG_SECURITY_AIRY=y 时默认禁用（airy_enabled=false）"——**注释与默认值矛盾**（注释说 false，代码默认 true）。这是文档-代码漂移，需修正注释或默认值。此点应纳入改进清单。

---

## 3. 改进点清单（第三轮设计论证视角）

| 编号 | 标题 | 优先级 | 现状位置 | 工作量 |
|------|------|--------|----------|--------|
| E7 | sched.h/stc_policy.h 两套策略枚举语义统一（UAPI 只暴露 AIRY_SCHED_POLICY_*） | P1 | [stc_policy.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_policy.c) L17-22 vs [sched.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/sched.h) L102-105 | 3h |
| E8 | zero_copy buffer 与 MemoryRovol 版本治理交互文档化（快照 or 共享） | P2 | [airy_ipc_zero_copy.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_zero_copy.c) L1-168 | 2h(文档) |
| E9 | [DSL] 触发时域文档化（编译期跨平台降级，非运行时容错） | P1 | [uapi_compat.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/uapi_compat.h) L95-132 | 1h(文档) |
| E10 | airy_enabled 默认值注释与代码一致性修复（true vs 注释声称 false） | P1 | [airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_lsm.c) L30-31/L51 | 0.5h |
| E11 | AIRY_CAP_PERM_* 权限位枚举 SSoT（集中定义于 [SC] security_types.h） | P2 | [airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap.h) L75 | 2h |
| E12 | IPC 唯一合法入口声明（fastpath 不得绕过 LSM 5-phase 校验） | P1 | [airy_ipc_fastpath.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_fastpath.c) L11-46 | 1h(文档) |
| E13 | airy_ipc_fastpath.c L3 版权行 SPHARx 拼写修复 | P3 | [airy_ipc_fastpath.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_fastpath.c) L3 | 0.1h |

---

## 4. 小结

五大技术选型经论证全部为**正确且务实**的选择：sched_tac 是 6.6 基线约束下的必然（sched_ext 不可用）；IORING_OP_URING_CMD 成熟稳定；纯 C LSM 保证可审计性且第一轮 P1-4 已落地；alloc_pages+mmap 跨架构一致；IRON-9 v3 [DSL] 是 openEuler/seL4 都没有的独有设计。核心机制论证确认 Badge folding 容量自洽、IPC fastpath 单门设计是分层而非偷工、MCS 映射近似充分。本轮新增 7 项改进（E7-E13），其中 E7（策略枚举统一）、E9（[DSL] 时域）、E10（注释漂移）、E12（唯一入口声明）为 P1 文档化/小改项，建议 M2 前收敛。无方向性设计错误——极境内核的设计方案在论证层面成立。
