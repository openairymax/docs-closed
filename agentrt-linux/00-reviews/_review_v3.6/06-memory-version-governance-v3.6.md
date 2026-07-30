SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 06 — 内存管理 + 版本治理深度对比：seL4/openEuler vs Airymax

> **文档定位**：Airymax agentrt-linux v3.6 评审系列第 06 篇，聚焦内存管理模型与版本治理机制的跨项目深度对比。
> **对比基准**：seL4-master（microkernel 类型安全内存模型）、openEuler kernel-OLK-6.6（KABI 二进制兼容治理）、Airymax agentrt-linux/kernel（ALK 改造 + OS-IRON 原则）。
> **方法论**：基于已逐行核验的源码证据进行静态对比，不依赖推测；行号引用均来自证据清单，严禁编造。代码位置引用使用 `file:///` 绝对路径锚点。
> **最后更新**：2026-07-30

## 1. 引言

本报告对比三个内核项目在两个维度上的设计取舍：内存管理（物理页如何分配、类型化、映射）与版本治理（如何在不破坏既有 ABI 的前提下持续演进）。seL4 代表"类型安全、cap 粒度"的微内核内存模型；openEuler OLK-6.6 代表"宏内核 + KABI 宏"的二进制兼容治理实践；Airymax agentrt-linux 则以"只新增文件、不改主线 + OS-IRON 分级稳定性"为治理基线。

对比目的不是判定优劣，而是为 Airymax 在 0.1.1→1.0.1（IRON-8）演进窗口内识别可借鉴的机制与待修补的违规点。

## 2. 内存模型对比

### 2.1 seL4：Untyped + Frame 类型安全模型

seL4 将所有物理内存以 `Untyped` cap 的形式分配给 root task，再通过 `retype` 操作派生为 `Frame`/`PageTable`/`TCB` 等具体对象。这一模型在以下文件中体现：

- [src/object/untyped.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/untyped.c) — Untyped retype：将 Untyped 内存拆分为具体对象 cap。
- [src/object/frame.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/frame.c) — Frame cap 的 map/unmap：物理页映射到虚拟地址。
- [include/object/objecttype.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/object/objecttype.h) — `ObjectType` 枚举，定义所有 cap 类型。

其核心特征是**完全的类型安全**：一段物理内存在被 retype 为 `Frame` 之前，无法被当作页表或 TCB 使用；retype 操作原子且受 cap 层级约束，从机制上杜绝了"同一页被两种类型同时引用"。Frame 的 map/unmap 也以 cap 为粒度，而非以进程地址空间为粒度。

### 2.2 Airymax：vm_insert_pages + alloc_pages 复用 Linux mm

Airymax 没有重写 mm 子系统，而是复用 Linux 6.6 主线的 `alloc_pages` 与 `vm_insert_pages` 实现零拷贝 IPC：

- [kernel/corekern/ipc/airy_ipc_zero_copy.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/corekern/ipc/airy_ipc_zero_copy.c) — 零拷贝实现，基于 `vm_insert_pages` + `alloc_pages`。
- airy_ipc_internal.h L43-47 — `zero_copy register/unregister/map` 声明。

这一选择与 ALK"只新增文件"原则一致：不修改主线 `mm/` 既有代码，而是在新增目录 `kernel/corekern/ipc/` 内叠加实现。代价是 Airymax 无法获得 seL4 那种"机制级类型安全"——物理页类型由 Linux slab/buddy 管理，Airymax 只在调用点约束用途。

### 2.3 对比小结

| 维度 | seL4 | Airymax |
|------|------|---------|
| 物理页归属 | Untyped cap，root task 持有 | Linux buddy，Airymax 调用 `alloc_pages` |
| 类型安全 | 机制级（retype 原子） | 约定级（调用点约束） |
| 映射粒度 | Frame cap map/unmap | `vm_insert_pages` 批量映射 |
| 改动范围 | 自有微内核 | 复用 Linux mm，仅新增文件 |

Airymax 的取舍是工程现实的：在 6.6 主线之上叠加类型安全会破坏 ALK 原则，且收益有限——agentrt-linux 的威胁模型并不要求形式化证明级别的内存隔离，而依赖 LSM（`security/airy/`）与 capability 表（`airy_ipc_capability.c`）做策略层隔离。

## 3. 内存治理对比

### 3.1 seL4 retype 派生模型

seL4 的内存治理即 retype 治理：内存所有权通过 cap 派生树显式表达，子 cap 的生命周期受父 Untyped 约束。回收时 `Delete`/`Revoke` 可级联回收整棵子树。这是一套"卷轮换"的雏形——内存段在被 retype 之前属于"未定义类型池"，retype 后才获得语义。

### 3.2 Airymax MemoryRovol（549）现状

Airymax 设计了 `airy_sys_rovol_ctl`（syscall 549）作为内存卷轮换入口，但当前 M1 阶段返回 `-ENOSYS`：

- syscall 549 已在新增 `kernel/syscalls/` 下注册占位，但实现为 stub。
- 与 seL4 retype 不同，Airymax 的 MemoryRovol 设计目标不是"物理页类型化"，而是"agent 内存卷的轮换与回收"——更接近 epoch-based 回收，配合 `airy_ipc_capability.c` 的 cap 表做所有权交接。

这是 v3.6 评审中最大的"设计已立、实现未到"缺口之一，需在 M5 阶段闭合（见 §7.4）。

## 4. 版本治理对比

### 4.1 openEuler KABI 机制

openEuler OLK-6.6 通过一组宏在结构体与 syscall 表中预留扩展空间，保证二进制兼容：

- [arch/x86/entry/syscalls/syscall_64.tbl L379-390](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/arch/x86/entry/syscalls/syscall_64.tbl#L379) — `kabi_reserved455` ~ `kabi_reserved466` 共 12 个 KABI 保留槽，初值为 `sys_ni_syscall`，显式保留 syscall 编号。
- [kernel/sched/sched.h L722](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/sched.h#L722) — `KABI_REPLACE(s64 avg_vruntime, s64 sum_w_vruntime)`：字段替换，保持 offset/size 不变。
- [kernel/sched/sched.h L723](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/sched.h#L723) — `KABI_REPLACE(u64 avg_load, u64 sum_weight)`：配套替换。
- [kernel/sched/sched.h L726](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/sched.h#L726) — `KABI_REPLACE(u64 min_vruntime, u64 zero_vruntime)`：配套替换。
- [kernel/sched/sched.h L521](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/sched.h#L521) — `KABI_USE2(3, u32 scx_flags, u32 scx_weight)`：占用第 3 个 `KABI_RESERVE` 槽，拆分为两个字段。
- [kernel/sched/sched.h L314-323](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/sched.h#L314) — `struct rt_bandwidth` 含 `KABI_RESERVE` 保留字段。

宏语义：

```c
/* KABI_RESERVE(n): 在结构体中保留 n 字节空间供未来扩展 */
KABI_RESERVE(16);
/* KABI_USE2(n, f1, f2): 占用第 n 个 KABI_RESERVE 槽，拆分为两个字段 */
KABI_USE2(3, u32 scx_flags, u32 scx_weight);
/* KABI_REPLACE(old, new): 替换字段名/类型，保持 offset/size 不变 */
KABI_REPLACE(s64 avg_vruntime, s64 sum_w_vruntime);
```

KABI 的本质是"在既有结构体内做无破坏演进"，代价是结构体永远拖着保留字段、且字段替换需遵守严格的 offset/size 守恒。

### 4.2 Airymax ALK 只新增文件原则

Airymax 走相反路径——不修改 Linux 6.6 主线既有结构体，只在新目录中新增文件：

- 设计文档 `20-modules/01-kernel.md` L46/L66-83 — ALK 改造原则：只新增文件，不修改主线。
- 37 个 `.c` 文件全部位于 `kernel/corekern/` + `kernel/ipc/` + `kernel/syscalls/` + `security/airy/` + `kernel/superv/` + `kernel/log/` 等新增目录。

ALK 天然避免了对 `task_struct`、`struct file` 等主线结构体的二进制破坏，因为根本不触碰它们。Airymax 自己的结构体（如 `task_desc`、`cap_slot`、`msg_hdr`）通过 `_reserved`/`reserved` 字段自留扩展空间（见 §5.2）。

### 4.3 KABI vs ALK 权衡

| 维度 | openEuler KABI | Airymax ALK |
|------|----------------|-------------|
| 主线结构体可演进 | 可（受 KABI 宏约束） | 不可（不触碰主线） |
| 二进制兼容保证 | 机制级（宏 + 白名单） | 架构级（隔离） |
| 保留字段成本 | 每个结构体都拖 KABI_RESERVE | 仅自有 UAPI 结构体保留 |
| 升级代价 | 字段替换需守恒 offset/size | 无字段替换，但需新增文件 |
| 与上游同步 | KABI 宏是 openEuler 私有，上游不收 | 新增文件天然可随上游 rebase |

ALK 的代价是**无法在主线结构体中增加字段**——例如无法给 `task_struct` 注入 Airymax 私有指针，只能通过新增的 `task_desc` 间接关联。这是 Airymax 选择"外挂式"治理的必然结果。

## 5. ABI 稳定性对比

### 5.1 openEuler KABI 二进制兼容

openEuler 的 KABI 承诺是**内核模块二进制兼容**：同一 OLK 大版本内，第三方驱动无需重编即可加载。这通过 `KABI_RESERVE`/`KABI_USE2`/`KABI_REPLACE` 三件套 + syscall 保留槽共同实现。

### 5.2 Airymax OS-IRON-001 + _reserved 字段

Airymax 的 ABI 稳定性承诺分层（见 `50-engineering-standards/04-engineering-philosophy.md`）：

- L100-112 — OS-IRON-001：用户空间 ABI 永不破坏（L1 极稳定）。
- L114-128 — OS-IRON-002：内核内部 API 不保证稳定（you broke it, you fix it）+ OS-KER-060。
- L130-160 — 4 层接口稳定性分级（L1/L2/L3/L4）。

Airymax 的 UAPI 结构体通过 `_reserved`/`reserved` 字段自留扩展空间，思路类似 `KABI_RESERVE`：

- [include/uapi/linux/airymax/lsm_types.h L53](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/lsm_types.h#L53) — `__u8 _reserved[56];` — `cap_slot` 结构体内部保留字段。
- [include/uapi/linux/airymax/sched.h L70](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/sched.h#L70) — `__u8 reserved[12];` — `task_desc` 结构体内部保留字段。

二者均配合 `AIRY_ALIGNED(64)` 收尾对齐（lsm_types.h L54、sched.h L71），形成"保留字段 + 显式对齐"的 UAPI 演进范式。

## 6. 编译器无关性对比

### 6.1 openEuler 无此约束

openEuler OLK-6.6 是标准 Linux 内核，允许使用 `__attribute__`、`__builtin_*`、`__asm__` 等编译器扩展。KABI 宏本身也依赖 `__attribute__`。

### 6.2 Airymax OS-IRON-016

Airymax 在编译器无关性上设了硬约束（见 `04-engineering-philosophy.md` L163-199）：

- OS-IRON-016：UAPI 禁止 `__attribute__`/`__builtin_*`/`__asm__`/`__sync_*`，`AIRY_ALIGNED(N)` 是唯一例外。
- [include/uapi/linux/airymax/uapi_compat.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/uapi_compat.h) — 定义 `AIRY_ALIGNED(N)` 宏，作为编译器无关原则的唯一豁免出口。

UAPI 结构体普遍正确使用 `AIRY_ALIGNED(64)`：

- [include/uapi/linux/airymax/ipc.h L89](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/ipc.h#L89) — `msg_hdr` 正确使用 `AIRY_ALIGNED(64)`。
- [include/uapi/linux/airymax/lsm_types.h L54](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/lsm_types.h#L54) — `cap_slot` 正确使用 `AIRY_ALIGNED(64)`。
- [include/uapi/linux/airymax/sched.h L71](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/sched.h#L71) — `task_desc` 正确使用 `AIRY_ALIGNED(64)`。

### 6.3 AIRY_ALIGNED 违规点

但内核内部实现文件存在一处违规——`airy_ipc_capability.c` 直接用了 `__aligned(64)` 而非 `AIRY_ALIGNED(64)`：

- [kernel/ipc/airy_ipc_capability.c L29-30](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/ipc/airy_ipc_capability.c#L29) — `static struct airy_cap_slot __airymax_cap_table[AIRY_CAP_MAX_AGENTS] __aligned(64);` ★ 用 `__aligned(64)` 而非 `AIRY_ALIGNED(64)`，违反 OS-IRON-016。
- [kernel/ipc/airy_ipc_capability.c L32](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/ipc/airy_ipc_capability.c#L32) — `struct airy_cap_slot *agent_caps __ro_after_init = __airymax_cap_table;`

此处争议点在于：`airy_ipc_capability.c` 是内核内部实现文件，而非 UAPI 头文件。OS-IRON-016 的字面约束范围是 UAPI；但 Airymax 工程哲学倾向于在所有 agentrt-linux 新增代码中保持编译器无关，以便未来工具链迁移。这一点需在 §7.1 中明确处理。

## 7. 改进建议

### 7.1 [P1] airy_ipc_capability.c L30 __aligned(64) 违规修复

**现状**：[kernel/ipc/airy_ipc_capability.c L29-30](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/ipc/airy_ipc_capability.c#L29) 使用 `__aligned(64)`（GCC/Clang 内置宏），与 OS-IRON-016 编译器无关原则冲突。

**参考**：[include/uapi/linux/airymax/ipc.h L89](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/ipc.h#L89)、[lsm_types.h L54](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/lsm_types.h#L54)、[sched.h L71](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/sched.h#L71) 均正确使用 `AIRY_ALIGNED(64)`。

**建议**：将 L29-30 的 `__aligned(64)` 替换为 `AIRY_ALIGNED(64)`。由于 `airy_cap_slot` 定义在 UAPI 头（lsm_types.h）且其 64 字节对齐语义跨 UAPI/内核内部一致，统一使用 `AIRY_ALIGNED(64)` 可消除"同结构体两套对齐宏"的歧义。需确认 `uapi_compat.h` 在该 `.c` 文件的 include 链中可见。

**风险**：低。`AIRY_ALIGNED(N)` 在 `uapi_compat.h` 中应展开为等价的 `__attribute__((aligned(N)))`（GCC/Clang 路径）或对应编译器语法，行为等价。唯一风险是 `airy_ipc_capability.c` 未 include `uapi_compat.h` 导致展开失败——修复时需同步检查 include 链。

### 7.2 [P2] ALK vs KABI 权衡文档化

**现状**：ALK"只新增文件"策略（设计文档 `20-modules/01-kernel.md` L46/L66-83）天然避免 KABI 破坏，但代价是无法在主线结构体（如 `task_struct`）中增加字段。当前设计文档未显式记录这一权衡的决策依据。

**参考**：openEuler [kernel/sched/sched.h L722-726](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/sched.h#L722) 的 `KABI_REPLACE` 链展示了"在既有结构体中演进"的另一条路径。

**建议**：在 `20-modules/01-kernel.md` 增补一节"ALK 与 KABI 的权衡决策"，明确：
1. Airymax 为何选择"外挂式"而非"KABI 式"——与上游 6.6 rebase 成本、形式化隔离目标一致。
2. ALK 的不可演进面——主线结构体字段无法注入，需通过新增结构体（如 `task_desc`）间接关联。
3. 何种场景下可能引入 KABI 风格保留槽（若未来必须扩展主线结构体）。

**风险**：低。仅文档变更，无代码影响。需注意不要把 KABI 宏引入 ALK——那样会破坏"主线零修改"承诺。

### 7.3 [P2] _reserved 字段统一策略

**现状**：UAPI 结构体已采用 `_reserved`/`reserved` 字段预留扩展空间：
- [lsm_types.h L53](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/lsm_types.h#L53) — `cap_slot._reserved[56]`。
- [sched.h L70](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/sched.h#L70) — `task_desc.reserved[12]`。

但字段命名不统一（`_reserved` 带下划线前缀 vs `reserved` 无前缀），且是否所有 UAPI 结构体都保留了扩展槽尚需审计。

**参考**：openEuler `KABI_RESERVE(n)` 全局统一命名；Airymax 应在 `uapi_compat.h` 中定义等价的 `AIRY_RESERVE(n)` 宏收口。

**建议**：
1. 在 `uapi_compat.h` 新增 `AIRY_RESERVE(n)` 宏（展开为 `__u8 _reserved[n]`），统一命名。
2. 审计 `50-engineering-standards/120-cross-project-code-sharing.md` L72-83 列出的 10 个 SC 头文件中的所有 UAPI 结构体，确保每个跨用户/内核边界的结构体都含 `AIRY_RESERVE` 槽。
3. 将 `reserved[12]`（sched.h L70）改名为 `_reserved[12]` 或迁到 `AIRY_RESERVE(12)`，与 lsm_types.h 对齐。

**风险**：中。重命名 `_reserved` → `reserved` 或反之会破坏既有用户空间引用（若有）。需先确认 0.1.1 阶段无外部用户空间直接访问该字段；若有，按 OS-IRON-001（UAPI 永不破坏）需保留旧名并仅在内部新增字段使用新槽。

### 7.4 [P2] MemoryRovol（549）M5 实现规划

**现状**：`airy_sys_rovol_ctl`（syscall 549）当前 M1 阶段返回 `-ENOSYS`，实现为 stub。这是 0.1.1→1.0.1（IRON-8）演进窗口内必须闭合的语义缺口。

**参考**：seL4 [src/object/untyped.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/untyped.c) 的 retype 模型——内存段在被派生前属"未定义类型池"，派生后才获得语义；`Delete`/`Revoke` 级联回收。

**建议**：M5 阶段实现 MemoryRovol 时，明确 Airymax 语义与 seL4 retype 的差异：
1. **Airymax 不做物理页类型化**——页类型仍由 Linux buddy 管理。MemoryRovol 的"卷"是 agent 内存所有权概念，不是 seL4 式类型。
2. **轮换语义应为 epoch-based**——`airy_sys_rovol_ctl` 接受 agent id + epoch 号，回收该 agent 在旧 epoch 的页映射（`vmunmap`/`zap_vma_pages`），但保留 cap 表中的所有权记录直至显式 `revoke`。
3. **与 `airy_ipc_capability.c` 联动**——卷轮换时需同步更新 cap 表（L29-30 的 `__airymax_cap_table`）中该 agent 的 slot 状态，避免轮换后旧 cap 仍可映射。
4. **接口稳定性**——549 已是 OS-IRON-001 L1 承诺的一部分，M5 实现的 ABI 不可在 1.0.1 之后破坏；建议 M5 落地前先用 `_reserved` 字段为参数结构体预留扩展槽（见 §7.3）。

**风险**：高。MemoryRovol 涉及跨 agent 内存回收，若 epoch 推进与 IPC 零拷贝映射（`airy_ipc_zero_copy.c`）未同步，可能产生 use-after-unmap。建议 M5 实现前先写形式化时序图，覆盖"零拷贝映射进行中 + 卷轮换并发"场景。

## 8. 结论

Airymax 在内存管理上选择了"复用 Linux mm + 新增文件"的工程路径，放弃了 seL4 的机制级类型安全，换得与上游 6.6 的低摩擦同步；在版本治理上选择了"ALK 只新增文件 + UAPI _reserved 字段"的架构级兼容路径，放弃了 openEuler KABI 的"主线结构体内演进"能力，换得主线零修改承诺。这两条路径自洽——ALK 使 KABI 不必要，`_reserved` 使 UAPI 演进有空间。

v3.6 评审发现的核心待办：
1. **[P1]** `airy_ipc_capability.c` L30 的 `__aligned(64)` 违反 OS-IRON-016，需替换为 `AIRY_ALIGNED(64)`——这是本系列报告中唯一直接违反既定 IRON 原则的代码点，应在 0.1.1 冻结前修复。
2. **[P2]** ALK vs KABI 权衡、`_reserved` 命名统一、MemoryRovol M5 语义规划，均可在 1.0.1（IRON-8）窗口内闭合，不阻塞 0.1.1 发布。

Airymax 的治理基线整体清晰且自洽，关键是在 0.1.1→1.0.1 演进中守住 OS-IRON-001 的 UAPI 永不破坏承诺，并把 MemoryRovol 这类"设计已立、实现未到"的 syscall 在 M5 闭合前以 `_reserved` 字段预留扩展空间，避免 1.0.1 之后再破坏 ABI。
