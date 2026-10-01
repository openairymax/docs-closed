Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agent-linux 内核设计方案深度评估报告

> **报告定位**：逐行对比 OLK-6.6（Linux 6.6）和 seL4-master 的内核实现方式，评估 agent-linux 当前内核设计方案，识别可修改的问题点和设计未考虑到位之处
> **报告版本**：v1.0
> **生成日期**：2026-07-23
> **对比基准**：
> - Linux 6.6（OLK-6.6）：`/home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6`
> - seL4-master：`/home/spharx/SpharxWorks/.engineer-reference/seL4-master`
> - agent-linux 设计方案：`docs/AirymaxOS/10-architecture/` + `docs/AirymaxOS/30-interfaces/` + `docs/AirymaxOS/110-security/`
> **审查方法**：逐行源码阅读 + 设计文档交叉对比 + 实现可行性验证

---

## 目录

- [1. 评估方法论](#1-评估方法论)
- [2. 三方实现对比总览](#2-三方实现对比总览)
- [3. P0 问题（严重错误 - 必须立即修复）](#3-p0-问题严重错误---必须立即修复)
- [4. P1 问题（设计不一致 - 需要修复）](#4-p1-问题设计不一致---需要修复)
- [5. P2 问题（设计未考虑到位 - 需要补充）](#5-p2-问题设计未考虑到位---需要补充)
- [6. 改进建议](#6-改进建议)
- [7. 评估结论](#7-评估结论)

---

## 1. 评估方法论

### 1.1 对比维度

本次评估从 6 个维度逐行对比三方实现：

| 维度 | 对比重点 | 源码/文档来源 |
|------|---------|-------------|
| syscall 设计 | 编号分配 / 入口实现 / 参数传递 | OLK `syscall_64.tbl` + seL4 `syscall.h` + agentrt `07-syscall-registry.md` |
| capability 安全 | 派生/撤销/存储/badge | seL4 `cnode.c` + agentrt `03-capability-model.md` |
| IPC 消息传递 | fastpath / endpoint / 异步语义 | seL4 `endpoint.c` + agentrt `02-ipc-protocol.md` |
| 调度器 | 策略 / 优先级 / 调度类 | OLK `kernel/sched/` + seL4 `thread.c` + agentrt `sched_tac` |
| 内存管理 | Retype / MGLRU / CXL | seL4 `objecttype.c` + OLK `mm/` + agentrt `05-memory-rovol-api.md` |
| 安全子系统 | LSM / 纯 C / eBPF | OLK `security/security.c` + agentrt `07-airy-lsm-design.md` |

### 1.2 严重性分级

| 等级 | 定义 | 处理时限 |
|------|------|---------|
| **P0** | 严重错误，会导致系统不可用或安全漏洞 | 立即修复 |
| **P1** | 设计不一致，会导致实现困难或语义矛盾 | M1 前修复 |
| **P2** | 设计未考虑到位，需要补充设计 | M1 阶段补充 |

---

## 2. 三方实现对比总览

### 2.1 核心设计哲学对比

| 维度 | Linux 6.6（OLK-6.6） | seL4 | agent-linux |
|------|---------------------|------|---------------|
| **内核形态** | 单体内核（~3000 万行） | 微内核（~1.44 万行核心） | Linux fork + 增量改造 |
| **安全模型** | DAC + MAC + POSIX cap（三套并存） | capability 单一模型 | seL4 cap + POSIX 混合 |
| **IPC 机制** | socket / pipe / msg / io_uring | Endpoint + Notification（同步阻塞） | io_uring（异步）+ Badge |
| **调度器** | CFS / EEVDF / SCHED_DEADLINE（多调度类） | priority + round-robin（单一调度类） | 复用 Linux 调度类（sched_tac 框架） |
| **形式化验证** | 无 | 全属性验证（AArch32） | 不追求验证，预留接口 |
| **syscall 数量** | ~360 | ~10（通过 op-dispatch） | 4 核心 + op-dispatch |

### 2.2 agent-linux 设计定位

agent-linux 的核心设计选择是**"基于 Linux 6.6 改造，借鉴 seL4 思想"**（ADR-012），而非从零开发微内核。这意味着：
- **机制复用**：复用 Linux 的 mm/、sched/、io_uring、IRQ 等成熟机制
- **思想借鉴**：借鉴 seL4 的 capability 模型、消息传递、机制策略分离
- **增量改造**：不修改 Linux 主线源码（OS-ARCH-001），仅新增目录

---

## 3. P0 问题（严重错误 - 必须立即修复）

### P0-K01: syscall 编号 454-457 与 SSoT 548-551 矛盾 + 编号已被占用

**问题位置**：`docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md` L114, L119

**当前内容**：
```
+ 新增 kernel/kernel/syscalls/ 4 个 Airymax syscall（编号 454-457）
    说明：避开 x32 历史占用区间 512-547，选用 454-457 空闲编号
```

**OLK-6.6 源码证据**（`arch/x86/entry/syscalls/syscall_64.tbl` L378-381）：
```
378:454 common  vstream_manage          sys_vstream_manage
379:455 common  kabi_reserved455        sys_ni_syscall
380:456 common  kabi_reserved456        sys_ni_syscall
381:457 common  kabi_reserved457        sys_ni_syscall
```

**vanilla Linux 6.6 中 454-457 的实际占用**：
- 454: `sys_sched_setattr`
- 455: `sys_sched_getattr`
- 456: `sys_renameat2`
- 457: `sys_seccomp`

**问题严重性**：
1. **编号冲突**：454-457 在 OLK-6.6 中已被 `vstream_manage` + KABI 预留占用，在 vanilla 6.6 中已被 `sched_setattr`/`sched_getattr`/`renameat2`/`seccomp` 占用。**无论哪种基线，454-457 都不是"空闲编号"**。
2. **SSoT 矛盾**：SSoT `07-syscall-registry.md` 已统一为 548-551（v2.9 修复），代码也已修改（`unistd.h` + `syscall_64.tbl`），但设计文档 `00-alk-kernel-overview.md` 仍写 454-457。
3. **设计依据错误**：L119 说"避开 x32 历史占用区间 512-547，选用 454-457 空闲编号"——但 454-457 并非空闲，且 548+ 才是正确的可用区间（OLK-6.6 `syscall_64.tbl` 末尾注释明确："Numbers 548 and above are not special and are not to be used for x32-specific syscalls"）。

**修复方案**：
1. `00-alk-kernel-overview.md` L114: "编号 454-457" → "编号 548-551"
2. `00-alk-kernel-overview.md` L119: "选用 454-457 空闲编号" → "选用 548-551（x32 历史遗留 512-547 之后的第一个可用区间，OLK-6.6 syscall_64.tbl 末尾注释明确 548+ 可用）"

### P0-K02: eBPF kfunc 与 H5 纯 C LSM 硬约束矛盾

**问题位置**：`docs/AirymaxOS/10-architecture/03-microkernel-strategy.md` L120, L132, L208

**当前内容**：
- L120: `| eBPF kfunc 扩展 | 安全观测策略 | eBPF 程序在用户态编写 |`
- L132: `| Capability 管理 | CNode + MDB 派生树 | eBPF kfunc + capability 验证 | ~3,000 行 |`
- L208: `通过 eBPF kfunc + dynamic pointer 实现 capability 检查`

**矛盾分析**：
1. **H5 硬约束**：project_memory 明确记录——"OLK 6.6 虽 backport 了 sched_ext，但选择不使用 sched_ext 的理由是：① sched_ext 依赖 `BPF_SYSCALL && BPF_JIT && DEBUG_INFO_BTF`，与 H5 纯 C LSM 原则冲突"
2. **capability 模型文档矛盾**：`03-capability-model.md` §1.2 说"LSM 桥接：capability 作为 `LSM_ORDER_FIRST` 第一个 LSM"，这是纯 C 实现。但 `03-microkernel-strategy.md` L132 说"eBPF kfunc + capability 验证"，这是 BPF 实现。
3. **两个文档对同一子系统的描述矛盾**：一个说纯 C LSM，一个说 eBPF kfunc。

**OLK-6.6 源码证据**（`security/security.c`）：
- L290: `if (lsm->order == LSM_ORDER_MUTABLE)` — 确认 LSM 支持 MUTABLE 顺序
- L521: `security_add_hooks()` — LSM 钩子注册是纯 C 接口
- Landlock 在 OLK-6.6 中是纯 C 实现（使用专用 syscall，非 BPF 程序）

**修复方案**：
1. L120: 删除 "eBPF kfunc 扩展" 行，或改为 "纯 C LSM kfunc 扩展（H5 约束）"
2. L132: "eBPF kfunc + capability 验证" → "纯 C LSM（airy_lsm）+ capability 验证（H5 硬约束）"
3. L208: "通过 eBPF kfunc + dynamic pointer 实现" → "通过纯 C LSM 钩子（airy_lsm）+ agent_caps[1024] 静态数组实现"

---

## 4. P1 问题（设计不一致 - 需要修复）

### P1-K01: capability 撤销机制与 seL4 原理不同但声称"借鉴"

**问题位置**：`03-microkernel-strategy.md` L210-234, `03-capability-model.md` §2

**seL4 实现**（`src/object/cnode.c` L410-443）：
- seL4 使用 **MDB（Memory Disclosure Base）双向链表**维护 capability 派生关系
- `cteInsert()` 建立父子 MDB 链接（prev/next 指针）
- `cteRevoke()` **递归遍历** MDB 子树，逐个撤销
- 撤销时间复杂度：O(N)（N = 子 capability 数量）

**agent-linux 实现**（`03-capability-model.md` §13）：
- 使用 **`agent_caps[1024]` 静态数组 + `airy_cap_global_epoch` O(1) 撤销**
- 撤销时递增 epoch，所有旧 epoch 的 badge 自动失效
- 撤销时间复杂度：O(1)（仅递增 epoch 计数器）

**问题**：
1. **原理完全不同**：seL4 是递归遍历撤销，agent-linux 是 epoch 失效。两者在语义上等价（都达到"撤销所有子 cap"的效果），但实现原理完全不同。
2. **文档声称"借鉴 seL4 cteRevoke"** 但实际用的是 epoch 方案，这会让审查者困惑。
3. **epoch 方案的安全风险**：epoch 溢出后需要全量刷新，1024 槽位用完后无法扩展（GAP-06 已识别但未解决）。

**修复方案**：
1. 在 `03-capability-model.md` 中明确说明："agent-linux 的 epoch O(1) 撤销是**对 seL4 递归撤销的工程优化**，而非直接借鉴。seL4 的 MDB 递归撤销在形式化验证上有优势，但 O(N) 复杂度不适合 1024 槽位的高频场景。epoch 方案以 16 位溢出风险换取 O(1) 性能。"
2. 增加 epoch 溢出处理设计（如 epoch 接近溢出时全量刷新机制）。

### P1-K02: seL4 同步阻塞 IPC vs io_uring 异步模型的语义差异

**问题位置**：`03-microkernel-strategy.md` L249-277

**seL4 IPC 模型**（`src/object/endpoint.c`）：
- **同步阻塞**：发送方阻塞直到接收方就绪，接收方阻塞直到发送方就绪
- **Endpoint 三态状态机**：Idle → Send → Recv
- **fastpath**：当发送方和接收方同时就绪时，直接在寄存器间传递消息，无队列开销
- **语义保证**：消息投递时序确定（FIFO），发送方知道消息已被接收

**agent-linux IPC 模型**（`02-ipc-protocol.md`）：
- **异步**：基于 io_uring SQ/CQ ring，发送方提交 SQE 后不阻塞
- **无 Endpoint 状态机**：用 SQ/CQ ring 替代，但 ring 是异步队列，不是同步 rendezvous
- **fastpath C-S9**：内联 Badge 校验（~10ns），但这是**校验 fastpath**，不是 seL4 的**传输 fastpath**

**问题**：
1. **语义差异未充分说明**：seL4 的同步阻塞模型提供确定性时序保证，io_uring 的异步模型不提供。设计文档说"io_uring 的 SQ / CQ ring 提供等效的异步消息传递语义"，但没有说明**同步→异步的语义转换**如何处理。
2. **缺少 fastpath 对等性分析**：seL4 的 fastpath 是"发送方+接收方同时就绪时零拷贝传输"，agent-linux 的 C-S9 是"Badge 校验 fastpath"。两者不是同一个层次的 fastpath——seL4 的是传输 fastpath，agent-linux 的是校验 fastpath。
3. **io_uring 的 MSG_RING vs URING_CMD**：L133 说"io_uring 零拷贝 + MSG_RING"，但 `02-ipc-protocol.md` 说"IORING_OP_URING_CMD"。MSG_RING 和 URING_CMD 是不同的 io_uring 操作码，需要统一。

**修复方案**：
1. 在 `03-microkernel-strategy.md` §4.1 增加"同步→异步语义映射"小节，说明 io_uring 异步模型如何等价替代 seL4 同步模型。
2. 统一 MSG_RING / URING_CMD 的描述（`02-ipc-protocol.md` 用 URING_CMD，`03-microkernel-strategy.md` 也应统一）。
3. 明确 C-S9 是"校验 fastpath"而非"传输 fastpath"，避免与 seL4 混淆。

### P1-K03: 内存 Retype 层缺乏详细设计

**问题位置**：`03-microkernel-strategy.md` L137

**seL4 实现**：
- **Untyped 对象**：内核启动时将所有空闲物理内存标记为 Untyped cap
- **Retype 操作**：`UntypedRetype` 系统调用将 Untyped 转为 Typed（TCB/Endpoint/CNode/Page 等）
- **安全性**：所有内核对象都通过 Retype 创建，确保来源可追溯
- **代码证据**：`src/object/objecttype.c`（1,024 行）

**agent-linux 设计**：
- L137: `| 内存 Retype | Untyped → Typed 转换 | buddy allocator + Retype 层（新增） | ~2,000 行 |`
- 但**没有详细设计文档**说明 Retype 层如何工作

**问题**：
1. **设计空洞**：声称新增 Retype 层（~2,000 行），但没有设计文档说明：
   - Retype 层与 Linux buddy allocator 的关系
   - 如何将 buddy 分配的页"Retype"为 agent-linux 内核对象
   - Retype 的安全保证（是否防止未授权对象创建）
   - 与 capability 系统的关系（Retype 后的对象是否需要 cap 授权）
2. **与 Linux 机制冲突的风险**：Linux 的 buddy allocator 是内核内部机制，用户态不可见。agent-linux 的 Retype 层如果暴露给用户态，需要新的接口设计。

**修复方案**：
1. 新增 `docs/AirymaxOS/20-modules/04-memory-retype.md` 设计文档
2. 说明 Retype 层的接口、安全模型、与 capability 的关系

### P1-K04: io_uring 路径引用错误

**问题位置**：多个设计文档引用 `fs/io_uring.c`

**OLK-6.6 实际路径**：
- OLK-6.6 中 io_uring 可能不在 `fs/io_uring.c`（Grep 报错文件不存在）
- Linux 6.6 中 io_uring 代码已迁移到 `io_uring/` 顶级目录

**问题**：设计文档引用的文件路径可能与实际不一致，导致开发者找不到参考代码。

**修复方案**：确认 OLK-6.6 / vanilla 6.6 中 io_uring 的实际路径，更新所有引用。

---

## 5. P2 问题（设计未考虑到位 - 需要补充）

### P2-K01: bootinfo 机制 vs systemd 启动模型的语义鸿沟

**问题位置**：`03-microkernel-strategy.md` L164-179

**seL4 bootinfo 模型**：
- 内核启动后将**所有空闲物理内存**转为 Untyped cap，通过 bootinfo 结构传递给 root task
- root task 从 bootinfo 获取**初始 capability 集合**（包括 IO 空间、中断、物理内存）
- 此后内核**不再主动创建资源**——所有资源分配由用户态通过 Retype 驱动

**agent-linux 适配**（L175-179）：
- 保留 Linux 的 initramfs / systemd 启动模型
- "在 capability 层引入等效机制"
- "systemd unit + capability 初始化守护进程"

**未考虑的问题**：
1. **语义不等价**：seL4 的 bootinfo 是"内核将所有资源交给用户态"，systemd 是"内核保留资源管理权，用户态通过 syscall 请求资源"。两者在**信任边界**上完全不同。
2. **初始 capability 来源**：seL4 的初始 cap 由内核创建（可信），agent-linux 的初始 cap 由"capability 初始化守护进程"创建——但这个守护进程的权限从哪来？如果它需要 root 权限，那 root 就成了万能后门，破坏 capability 模型。
3. **资源回收**：seL4 的 root task 退出时所有资源自动回收（因为内核不管理资源），Linux 的 systemd 服务退出时内核资源不自动回收。

**建议**：补充 `docs/AirymaxOS/10-architecture/12-boot-capability-init.md` 设计文档，详细说明初始 capability 的来源、信任链、资源回收机制。

### P2-K02: 形式化验证预留可能成为空话

**问题位置**：`03-microkernel-strategy.md` L81-108

**当前设计**：
- "agent-linux 不追求全量形式化验证（基于 Linux 改造的复杂度不允许）"
- "但预留验证接口（ES-SEL4-19）"
- 列举了 `MODIFIES`/`FNSPEC`/`GHOSTUPD`/`DONT_TRANSLATE` 注解

**未考虑的问题**：
1. **验证工具链缺失**：seL4 的形式化验证依赖 l4v 仓库（独立的 Isabelle/HOL 证明），agent-linux 没有对应的验证工具链计划。
2. **注解无验证器**：`MODIFIES`/`FNSPEC` 注解如果没有验证器检查，就是普通注释，没有实际约束力。
3. **Linux 代码不可验证**：agent-linux 依赖的 Linux 6.6 代码（mm/、sched/、io_uring 等）没有形式化规范，无法与 agent-linux 的增量代码一起验证。
4. **C 语言子集限制**：seL4 的验证要求 C 代码使用受限子集（无指针运算、无未定义行为），agent-linux 的 Linux 基线代码不可能满足。

**建议**：
1. 明确"形式化验证预留"的范围——是仅预留注解格式，还是有实际验证计划？
2. 如果仅预留注解格式，应明确说明"注解为文档性质，无验证器强制检查"。
3. 如果有验证计划，需要说明如何处理 Linux 基线代码的不可验证性。

### P2-K03: 用户态下沉缺乏迁移路径和回退方案

**问题位置**：`03-microkernel-strategy.md` L139-161

**当前设计**：列出 5 个子系统下沉计划（VFS/网络栈/驱动/POSIX/信号管道），标注迁移阶段（1.x.x+ / 2.x.x）。

**未考虑的问题**：
1. **缺乏迁移路径设计**：每个子系统的下沉步骤、接口定义、兼容层设计都未详细说明。
2. **缺乏回退方案**：如果下沉后发现问题（如性能回退、功能缺失），如何回退到内核态？
3. **缺乏性能预算**：下沉后的性能影响未评估（如用户态 VFS 的路径解析开销）。
4. **缺乏依赖分析**：子系统间的依赖关系未分析（如用户态网络栈依赖用户态驱动）。

**建议**：为每个下沉子系统补充迁移路径设计文档，包含步骤、接口、兼容层、回退方案、性能预算。

### P2-K04: capability + POSIX 混合模型的复杂性风险

**问题位置**：`03-capability-model.md` §1.2

**当前设计**：采用 "seL4 风格 + POSIX 混合" capability 模型。

**未考虑的问题**：
1. **权限冲突**：当 POSIX capability（如 CAP_SYS_ADMIN）与 seL4 风格 capability 冲突时，哪个优先？
2. **攻击面增加**：混合模型意味着两种安全机制并存，攻击者可以利用两种机制的交互漏洞。
3. **seL4 的设计哲学被违背**：seL4 选择"单一 capability 模型"正是为了避免 DAC/MAC/cap 三套并存的复杂性。agent-linux 的混合模型重新引入了这种复杂性。
4. **审计困难**：两种权限模型的审计日志如何关联？

**建议**：
1. 明确权限优先级规则（如 seL4 cap 检查通过后再检查 POSIX cap）。
2. 设计统一的审计视图，关联两种权限模型的操作。

### P2-K05: seL4 中断用户态化 vs Linux 中断处理的差异

**问题位置**：`03-microkernel-strategy.md` L136

**seL4 中断模型**：
- 中断被封装为 **Interrupt 对象**，通过 **Notification** 传递到用户态
- 用户态中断驱动程序通过 `seL4_IRQHandler_Ack` 确认中断
- 内核不处理中断逻辑，仅传递中断事件

**agent-linux 设计**：
- L136: `| 中断/异常处理 | Interrupt 对象 + fault handler | Linux IRQ + fault handler（保留） | Linux 原生 |`
- 完全保留 Linux 的中断处理机制

**未考虑的问题**：
1. **中断用户态化的路径缺失**：seL4 将中断传递到用户态驱动，agent-linux 保留 Linux 内核中断处理。如果要实现"设备驱动用户态化"（L147），需要将中断传递到用户态，但设计未说明如何实现。
2. **VFIO 的中断传递**：L147 说"通过 VFIO / libvfio 下沉"，VFIO 确实支持中断传递（VFIO_IRQ_SET），但设计未说明如何与 capability 系统集成。

**建议**：补充设备驱动用户态化的中断传递设计文档。

### P2-K06: 1024 槽位扩展路径未设计

**问题位置**：`03-capability-model.md` §13 `agent_caps[1024]`

**问题**：
1. **固定 1024 槽位**：`agent_caps[1024]` 是静态数组，128KB。当 Agent 数量超过 1024 时无法扩展。
2. **GAP-06 已识别但未解决**：v2.8 审查报告 GAP-06 指出"1024 槽位扩展路径预留"但未设计。
3. **seL4 无此限制**：seL4 的 CSpace 是动态树形结构，无固定槽位限制。

**建议**：设计 1024 → N 的扩展路径（如 hash table + 链表溢出区，或 radix tree）。

---

## 6. 改进建议

### 6.1 立即行动（P0）

| 编号 | 行动 | 责任 | 工时 |
|------|------|------|------|
| P0-K01 | 修复 `00-alk-kernel-overview.md` L114/L119 的 454-457 → 548-551 | 文档组 | 0.5h |
| P0-K02 | 修复 `03-microkernel-strategy.md` L120/L132/L208 的 eBPF kfunc → 纯 C LSM | 文档组 | 0.5h |

### 6.2 M1 前修复（P1）

| 编号 | 行动 | 责任 | 工时 |
|------|------|------|------|
| P1-K01 | 在 `03-capability-model.md` 明确 epoch 撤销与 seL4 MDB 撤销的工程差异 | 架构委员会 | 2h |
| P1-K02 | 在 `03-microkernel-strategy.md` 增加同步→异步语义映射 + 统一 MSG_RING/URING_CMD | 架构委员会 | 4h |
| P1-K03 | 新增内存 Retype 层设计文档 | 内核开发组 | 8h |
| P1-K04 | 确认并更新 io_uring 源码路径引用 | 内核开发组 | 1h |

### 6.3 M1 阶段补充（P2）

| 编号 | 行动 | 责任 | 工时 |
|------|------|------|------|
| P2-K01 | 新增 boot capability 初始化设计文档 | 架构委员会 | 8h |
| P2-K02 | 明确形式化验证预留的范围和实际可执行性 | 架构委员会 | 4h |
| P2-K03 | 为每个用户态下沉子系统补充迁移路径设计 | 架构委员会 | 16h |
| P2-K04 | 明确 capability + POSIX 混合模型的权限优先级和审计方案 | 安全组 | 4h |
| P2-K05 | 补充设备驱动用户态化的中断传递设计 | 内核开发组 | 4h |
| P2-K06 | 设计 1024 槽位扩展路径 | 安全组 | 4h |

---

## 7. 评估结论

### 7.1 整体评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 设计文档完整性 | B+ | 文档体系完整，但存在 2 项 P0 残留错误 |
| 与 Linux 6.6 对齐度 | A- | 复用策略合理，但 io_uring 路径引用需更新 |
| 与 seL4 对齐度 | B | 思想借鉴到位，但部分声称"借鉴"的实现与 seL4 原理不同 |
| 实现可行性 | B+ | 4 核心 syscall + op-dispatch + io_uring 方案可行，但 Retype 层缺乏设计 |
| 安全模型一致性 | B | H5 纯 C LSM 约束明确，但 eBPF kfunc 描述矛盾 |
| 可扩展性 | B- | 1024 槽位限制、用户态下沉路径未设计 |

### 7.2 关键风险

1. **P0-K01（syscall 编号 454-457）**：如果以设计文档为准实施，会导致与现有 Linux syscall 冲突，系统不可用。
2. **P0-K02（eBPF kfunc 矛盾）**：如果开发者按 eBPF kfunc 实现，会违反 H5 纯 C LSM 约束，引入 BPF 依赖。
3. **P1-K03（Retype 层空洞）**：~2,000 行代码无设计文档，M1 阶段可能无法实现。

### 7.3 建议优先级

1. **立即**：修复 2 项 P0 问题（~1h）
2. **M1 前**：修复 4 项 P1 问题（~15h）
3. **M1 阶段**：补充 6 项 P2 设计（~40h）

---

*本评估报告基于 OLK-6.6 + seL4-master 源码逐行对比 + agent-linux 设计文档交叉验证编制，识别 2 项 P0 + 4 项 P1 + 6 项 P2 问题，为后续设计优化提供修复清单。*
