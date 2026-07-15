Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# C-2.3 agentrt-linux 7 层架构模型与 agentrt 用户态关系论证报告

> **文档定位**: agentrt-linux（AirymaxOS）7 层架构模型范围界定与 agentrt 用户态关系的技术论证决策参考报告
> **报告版本**: v1.0
> **生成日期**: 2026-07-09
> **触发指令**: 用户 C-2.3（"深入分析 agentrt-linux 的架构模型问题：针对 7 层架构模型中是否包含 agentrt 组件，以及 agentrt 是否可以直接作为 agentrt-linux 的用户态（而非仅保持同源映射关系）进行详细技术论证"）
> **关联 ADR**: ADR-011（7 层架构模型范围界定与 agentrt 用户态关系论证）、ADR-010（与 agentrt 同源且部分代码共享，IRON-9 v2）
> **关联文档**: `10-architecture/README.md` §3、`10-architecture/01-system-architecture.md`、`10-architecture/05-adrs.md`、`20-modules/README.md` §2、`50-engineering-standards/120-cross-project-code-sharing.md`

---

## 0. 摘要（TL;DR）

本报告针对 agentrt-linux 7 层架构模型的两个核心架构问题进行技术论证：

1. **7 层架构模型是否包含 agentrt 组件？** —— **结论：不包含**。agentrt 是跨平台用户态运行时（Linux/macOS/Windows），作为外部组件运行于 agentrt-linux 之上，不属于 7 层架构（L1-L7）的任何一层。此结论受三条硬约束支撑：(a) 跨平台硬约束（2026-07-04 用户决策）；(b) 架构正交性原则；(c) IRON-9 v2 已实现零适配层天然契合，无需纳入即可获得同源红利。

2. **agentrt 是否可以直接作为 agentrt-linux 的用户态？** —— **结论：不可直接"成为"，但可"运行于"其上**。agentrt 是 agentrt-linux 的**推荐用户态运行时**，但非**唯一**用户态。两者关系是"平台—应用"关系（platform-application），而非"内核—用户态"关系（kernel-userspace）。IRON-9 v2 三层共享模型（[SC] 共享契约层 + [SS] 语义同源层 + [IND] 完全独立层）已是最优实现，无需将 agentrt 纳入 agentrt-linux 内部架构。

**关键发现（需修复的问题）**：

- **P0 严重问题（必须修复）**: ADR-011 中的 7 层架构表与权威定义（`10-architecture/README.md` §3）存在 **4 处不一致**——L1 定义错误（Linux 6.6 基线 vs 硬件层）、L3 缺失 services 子仓、L5 子仓错位（services vs cloudnative）、L7 子仓错位（cloudnative+tests-linux vs tests-linux）。此不一致会导致架构理解混乱，必须修复。
- **P1 次要问题（建议修复）**: `01-system-architecture.md` §2.1 的概念性架构分层图显示"4 层"结构，与 7 层架构模型并存易引起读者混淆，建议增加交叉引用澄清。

**修复执行**: 本报告在 §6 给出具体修复方案，§7 给出技术依据与优缺点分析，§8 给出技术推论与决策建议。P0 问题已在报告中标记为"待修复"，修复操作见 §6.1。

---

## 1. 任务背景

### 1.1 用户指令原文

> "2.3 深入分析 agentrt-linux 的架构模型问题：针对 7 层架构模型中是否包含 agentrt 组件，以及 agentrt 是否可以直接作为 agentrt-linux 的用户态（而非仅保持同源映射关系）进行详细技术论证。需提供充分的技术依据、优缺点分析及合理的技术推论，形成决策参考报告，供最终决策使用。"

### 1.2 任务要素拆解

| 要素 | 内容 |
|------|------|
| 问题一 | 7 层架构模型（L1-L7）是否包含 agentrt 组件？ |
| 问题二 | agentrt 是否可以直接作为 agentrt-linux 的用户态？（而非仅保持同源映射关系） |
| 要求 | 充分的技术依据 + 优缺点分析 + 合理的技术推论 |
| 产出 | 决策参考报告（供最终决策使用） |

### 1.3 决策现状

经审查，**ADR-011（2026-07-09 Accepted）已记录此决策**：

- 决策一：7 层架构模型不包含 agentrt 组件
- 决策二：agentrt 是推荐用户态运行时但非唯一，以 IRON-9 v2 同源关系运行于其上

因此本报告的任务**不是重新决策**，而是：
1. **验证 ADR-011 决策的论证充分性**——提供更详尽的技术依据、优缺点分析、技术推论
2. **发现并修复 ADR-011 中的事实性错误**——7 层架构表与权威定义不一致
3. **形成决策参考报告**——作为 ADR-011 的支撑材料，供后续回顾与决策巩固

---

## 2. 现状分析

### 2.1 7 层架构模型权威定义

**权威来源**: [10-architecture/README.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/10-architecture/README.md) §3「架构层次模型」（含 Mermaid 图 + 各层职责详述表 + 层次纪律说明）

权威定义的 7 层架构（自底向上）：

| 层次 | 子仓 | 核心机制 | 依赖下层 |
|------|------|----------|----------|
| L1 硬件层 | （硬件，非子仓） | CPU / 内存 / CXL / PMEM / NIC / NVMe | - |
| L2 内核层 | airymaxos-kernel | EEVDF + sched_ext + eBPF kfunc + io_uring + MGLRU + Rust | L1 |
| L3 服务层 | airymaxos-services + airymaxos-security + airymaxos-memory | VFS 用户态化 + 网络 + 驱动 + capability + MemoryRovol + CXL | L2 |
| L4 认知层 | airymaxos-cognition | CoreLoopThree kthread + Wasm 3.0 + LLM 调度 + 双系统协同 | L3 |
| L5 云原生层 | airymaxos-cloudnative | K8s CRD + containerd shim + OCI + CNI + 超节点 OS | L4 |
| L6 系统层 | airymaxos-system | RPM + dnf + systemd + 配置 + shell + DevStation | L5 |
| L7 测试层（横向） | airymaxos-tests-linux | 单元 + 集成 + 形式化验证 + Soak + 混沌 | L2-L6 全部 |

**层次纪律**（S-2 层次分解原则）：
1. 每层只依赖其直接下层的抽象接口，禁止越级访问
2. 同层之间通过 IPC 通信，禁止直接函数调用
3. 层次之间的接口契约通过 `30-interfaces/` 文档定义
4. 任何新增跨层依赖必须通过 ADR 评审

### 2.2 ADR-011 决策内容

[ADR-011](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/10-architecture/05-adrs.md) 记录了两个核心决策：

**决策一**: 7 层架构模型**不包含** agentrt 组件。agentrt 作为独立跨平台项目不属于此 7 层架构的任何一层。

**决策二**: agentrt 是 agentrt-linux 的**推荐用户态运行时**，但非**唯一**用户态。agentrt 不直接"成为"agentrt-linux 的用户态，而是以 IRON-9 v2 同源关系运行于其上。两者关系是"平台—应用"关系，而非"内核—用户态"关系。

**ADR-011 给出的 5 条理由**：
1. 硬约束：agentrt 必须保持跨平台（Linux/macOS/Windows）
2. 架构正交性：7 层架构是 agentrt-linux 内部依赖管理工具
3. IRON-9 v2 已是最优实现：三层共享模型已实现零适配层天然契合
4. seL4 root task 模型验证：agentrt 类比于 seL4 的 root task（独立外部组件）
5. "微核心"与"微内核"的区分：agentrt 是微核心（MicroCoreRT），agentrt-linux 是微内核

### 2.3 IRON-9 v2 三层共享模型

[120-cross-project-code-sharing.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md) 定义了 agentrt 与 agentrt-linux 的代码共享边界：

| 层次 | 缩写 | 共享程度 | 内容 | 落地路径 |
|------|------|---------|------|---------|
| 共享契约层 | [SC] | 完全共享代码 | 6 个头文件（bpf_struct_ops.h / memory_types.h / security_types.h / cognition_types.h / sched.h / ipc.h） | `include/airymax/` |
| 语义同源层 | [SS] | API 签名相同，实现独立 | 调度语义 / 安全模型 / IPC 传输 / 记忆模型 | 各自独立实现 |
| 完全独立层 | [IND] | 完全独立 | 内核驱动/Kbuild（agentrt-linux）；跨平台用户态/SDK（agentrt） | 各自独立仓库 |

**关键洞察**: IRON-9 v2 的 [SC] 层（6 个头文件逐字节共享）已实现"零适配层天然契合"——agentrt 在 agentrt-linux 上运行时，IPC 消息头（magic 0x41524531 'ARE1'）、任务描述符（magic 0x41475453 'AGTS'）、capability 模型、MemoryRovol L1-L4 结构、CoreLoopThree 上下文等全部语义一致，无需任何转换层。这意味着"将 agentrt 纳入 agentrt-linux 内部架构"并非获得同源红利的必要条件。

### 2.4 agentrt 跨平台硬约束

**用户决策（2026-07-04）**: atoms 核心路径保持用户态跨 Linux/macOS/Windows 三平台（通过 libc/POSIX）。

此硬约束记录于项目记忆（project_memory.md）"Hard Constraints"首条，是不可动摇的架构约束。任何使 agentrt 丧失跨平台能力的方案均违反此约束。

### 2.5 seL4 root task 模型参考

seL4 微内核架构中，**root task**（用户态初始进程）是独立于内核的外部组件：
- 内核启动后通过 bootinfo 将初始 capability 集合传递给 root task
- root task 负责初始化用户态服务（文件系统、网络、驱动等）
- root task 与内核通过 capability + IPC 交互，但**不属于内核**

agentrt 与 agentrt-linux 的关系类比于此：agentrt 是 agentrt-linux 上的"root task 级"用户态运行时，但并非内核的一部分。此类比由 ADR-011 理由 4 提出，是 seL4 工程思想在架构关系层面的借鉴（ES-SEL4-3 服务用户态化）。

---

## 3. 核心问题论证

### 3.1 问题一：7 层架构模型是否包含 agentrt 组件？

#### 3.1.1 论证结论

**结论：不包含。** agentrt 不属于 7 层架构（L1-L7）的任何一层。

#### 3.1.2 技术依据

**依据 1：跨平台硬约束**

agentrt 的核心定位是"跨平台用户态运行时"（Linux/macOS/Windows）。若将 agentrt 纳入 agentrt-linux 的 7 层架构（即作为某一层），意味着 agentrt 成为 agentrt-linux 的内部组件，其演进将受 agentrt-linux 内部层次变化制约，且将丧失在 macOS/Windows 上的独立运行能力——这直接违反 2026-07-04 用户确立的跨平台硬约束。

| 假设场景 | 后果 |
|---------|------|
| agentrt 作为 L8（应用层）纳入 7 层架构 | agentrt 演进受 agentrt-linux 制约；macOS/Windows 版本需"剥离"agentrt-linux 依赖 |
| agentrt 作为 L5/L6 某层纳入 | 破坏层次正交性；agentrt 跨平台语义被 agentrt-linux 特定层污染 |
| agentrt 作为 L1 硬件抽象层 | 语义错位（agentrt 是用户态，非硬件层） |

**依据 2：架构正交性原则**

7 层架构是 agentrt-linux 的**内部依赖管理工具**，仅涵盖 agentrt-linux 自身的 8 个子仓。其设计目的是组织 agentrt-linux 内部 8 子仓的依赖关系（kernel → services/security/memory → cognition → cloudnative → system → tests）。

agentrt 是**外部独立项目**，有自己的版本节奏、治理结构、发布周期。将其纳入 agentrt-linux 内部架构会破坏架构正交性——两个独立项目的内部架构不应相互嵌套。

**依据 3：IRON-9 v2 已实现目标**

用户问题中的"而非仅保持同源映射关系"暗示了一个潜在疑虑：同源映射关系是否"足够"？

答案：**足够**。IRON-9 v2 的 [SC] 共享契约层（6 个头文件逐字节共享）已实现：
- IPC 消息头布局完全一致（magic 0x41524531 'ARE1'，128B 定长）
- 任务描述符完全一致（magic 0x41475453 'AGTS'，Q16.16 vtime）
- capability 模型完全一致（38 ID + 254 LSM hook + 4 值裁决）
- MemoryRovol L1-L4 结构完全一致
- CoreLoopThree 上下文结构完全一致
- syscall 编号、错误码、规则编号体系一致

这意味着 agentrt 在 agentrt-linux 上运行时，**所有跨边界数据结构逐字节兼容**，无需任何转换层。此"天然契合"程度已等同于"agentrt 是 agentrt-linux 内部组件"的效果，但保留了 agentrt 的跨平台独立性。

**依据 4：seL4 root task 模型验证**

seL4 的 root task 是独立于内核的外部组件，通过 capability 与内核交互，但**不属于内核**。agentrt 与 agentrt-linux 的关系类比于此——agentrt 是 agentrt-linux 上的"root task 级"用户态运行时，但并非 agentrt-linux 内部架构的一部分。

此类比是 seL4 工程思想（ES-SEL4-3 服务用户态化）在架构关系层面的合法借鉴，且与 ADR-014（微内核来源单一化，仅 seL4）一致。

**依据 5："微核心"与"微内核"的语义区分**

用户决策（2026-07-09）：agentrt 是"微核心"（MicroCoreRT，用户态微核心运行时），agentrt-linux 是"微内核"（基于 Linux 改造的微内核化 OS）。两者是不同层级的概念：
- **微核心**（micro-core）：用户态的极简运行时核心，跨平台
- **微内核**（micro-kernel）：内核态的极简内核，OS 专属

将"微核心"纳入"微内核"的内部架构，是概念层级的混淆——微核心是微内核的**用户态伙伴**，而非其内部层次。

#### 3.1.3 优缺点分析

**纳入 7 层架构的优缺点**（假设方案，未采纳）：

| 维度 | 优点 | 缺点 |
|------|------|------|
| 集成度 | 紧密集成，单一架构视图 | 破坏跨平台硬约束（致命） |
| 演进 | 统一演进 | agentrt 演进受 agentrt-linux 制约 |
| 治理 | 统一治理 | 两个独立项目的治理结构冲突 |
| 复用 | — | macOS/Windows 版本需"剥离"agentrt-linux 依赖 |

**不纳入（采纳方案）的优缺点**：

| 维度 | 优点 | 缺点 |
|------|------|------|
| 集成度 | IRON-9 v2 [SC] 层已实现零适配层天然契合 | 需双向 CI 校验 [SC] 变更 |
| 演进 | 两者独立演进，互不制约 | 设计理念变更需双向同步 |
| 治理 | 各自独立治理 | 需 ADR 流程管理同源关系 |
| 复用 | agentrt 保持跨平台能力 | 部分代码可能重复实现（如命名空间、错误码） |

#### 3.1.4 技术推论

基于上述论证，**7 层架构模型不包含 agentrt 组件**是唯一符合所有硬约束的方案。agentrt 作为外部组件运行于 agentrt-linux 之上，通过 IRON-9 v2 [SC] 共享契约层实现零适配层天然契合。

---

### 3.2 问题二：agentrt 是否可以直接作为 agentrt-linux 的用户态？

#### 3.2.1 论证结论

**结论：agentrt 不可直接"成为"agentrt-linux 的用户态，但可"运行于"其上。** agentrt 是 agentrt-linux 的**推荐用户态运行时**，但非**唯一**用户态。两者关系是"平台—应用"关系（platform-application），而非"内核—用户态"关系（kernel-userspace）。

#### 3.2.2 术语澄清

此问题需澄清"作为用户态"的两种语义：

| 语义 | 含含 | 是否采纳 |
|------|------|---------|
| "成为"agentrt-linux 的用户态 | agentrt 是 agentrt-linux 专属用户态，agentrt-linux 的用户态只有 agentrt | **不采纳**（违反跨平台硬约束） |
| "运行于"agentrt-linux 的用户态 | agentrt 作为用户态应用运行于 agentrt-linux 之上，是推荐但非唯一 | **采纳**（IRON-9 v2 同源关系） |

用户问题中的"而非仅保持同源映射关系"指向的是第一种语义（"成为"），本报告论证此语义不可行，并论证第二种语义（"运行于"）已由 IRON-9 v2 实现。

#### 3.2.3 技术依据

**依据 1：跨平台硬约束禁止"成为"**

若 agentrt"成为"agentrt-linux 的专属用户态，则 agentrt 将绑定于 Linux 6.6 内核基线，丧失在 macOS/Windows 上的独立运行能力。这违反 2026-07-04 用户确立的跨平台硬约束。

**依据 2：agentrt-linux 用户态不限于 agentrt**

agentrt-linux 作为 Linux 发行版，其用户态遵循 POSIX 标准，任何符合 POSIX 的应用均可运行（如 bash、Python、Go 程序、其他 Linux 应用）。若规定"agentrt-linux 的用户态只有 agentrt"，将：
- 破坏 POSIX 兼容性（其他 Linux 应用无法运行）
- 退化为封闭系统（违反开放生态目标）
- 与"生产级 Linux 发行版"定位冲突

**依据 3：IRON-9 v2 "运行于"已是最优**

IRON-9 v2 的"运行于"模式已实现：
- agentrt 在 agentrt-linux 上运行时，获得同源红利（零适配层天然契合）
- agentrt 在普通 Linux 上运行时，标准 libc/POSIX
- agentrt 在 macOS 上运行时，标准 libc/POSIX
- agentrt 在 Windows 上运行时，Win32 API

此模式兼顾了跨平台独立性与同源红利，是唯一满足所有约束的方案。

**依据 4：seL4 root task 模型**

seL4 的 root task 是"运行于"内核之上的用户态进程，但不是内核的"专属用户态"——seL4 可以有多个 root task 或用户态进程。agentrt 与 agentrt-linux 的关系类比于此：agentrt 是 agentrt-linux 上"运行于"用户态的推荐运行时，但 agentrt-linux 的用户态不限于 agentrt。

**依据 5："微核心"与"微内核"的层级区分**

agentrt 是"微核心"（用户态），agentrt-linux 是"微内核"（内核态 OS）。微核心运行于微内核之上是自然关系，但微核心不是微内核的"专属用户态"——微内核可以承载多种用户态（如 systemd、bash、其他 POSIX 应用），微核心（agentrt）只是其中之一（尽管是推荐的）。

#### 3.2.4 优缺点分析

**agentrt 直接"成为"agentrt-linux 用户态的优缺点**（假设方案，未采纳）：

| 维度 | 优点 | 缺点 |
|------|------|------|
| 集成度 | 零适配（但 IRON-9 v2 已实现） | 丧失跨平台（致命） |
| 性能 | 可能微优化（但 [SC] 已逐字节共享，无优化空间） | — |
| 治理 | 单一项目 | 两个项目强行合并 |
| 生态 | — | 退化为封闭系统，违反 POSIX 兼容 |

**IRON-9 v2 "运行于"模式的优缺点**（采纳方案）：

| 维度 | 优点 | 缺点 |
|------|------|------|
| 集成度 | [SC] 6 头文件逐字节共享，零适配层 | 需双向 CI 校验 |
| 跨平台 | agentrt 保持 Linux/macOS/Windows | — |
| 生态 | agentrt-linux 保持 POSIX 兼容，开放生态 | — |
| 演进 | 两者独立演进 | 设计理念变更需双向同步 |

#### 3.2.5 技术推论

基于上述论证，**agentrt 不直接"成为"agentrt-linux 的用户态，而是以 IRON-9 v2 同源关系"运行于"其上**是唯一符合所有硬约束的方案。此方案已由 IRON-9 v2 三层共享模型实现，无需进一步改造。

---

## 4. 发现的问题

### 4.1 P0 严重问题：ADR-011 的 7 层架构表与权威定义不一致

**问题描述**: [ADR-011](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/10-architecture/05-adrs.md) 的「决策一」中给出了 7 层架构表，但此表与权威定义（[10-architecture/README.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/10-architecture/README.md) §3）存在 **4 处不一致**：

| 层次 | 权威定义（10-architecture/README.md §3） | ADR-011 表 | 不一致类型 |
|------|------------------------------------------|------------|-----------|
| L1 | **硬件层**（CPU/内存/CXL/PMEM，非子仓） | **Linux 6.6 基线**（模型 A 自包含于 kernel 子仓） | 定义错误 |
| L3 | **services + security + memory** | **security / memory**（缺失 services） | 子仓遗漏 |
| L5 | **cloudnative** | **services** | 子仓错位 |
| L7 | **tests-linux** | **cloudnative / tests-linux** | 子仓错位（cloudnative 应在 L5） |

**影响分析**:

此不一致会导致：
1. **架构理解混乱**: 读者参考 ADR-011 与参考 10-architecture/README.md 会得到不同的 7 层架构理解
2. **子仓归属错误**: 按ADR-011 表，services 在 L5（与 cloudnative 同层），但实际 services 应在 L3（与 security/memory 同层）
3. **依赖关系错误**: 按ADR-011 表，cloudnative 在 L7（与 tests-linux 同层），但实际 cloudnative 在 L5，依赖 L4 cognition
4. **L1 语义错误**: 权威定义 L1 是硬件层（非子仓），ADR-011 表将 L1 定义为"Linux 6.6 基线"——这混淆了"硬件层"与"内核基线"两个概念

**根因分析**:

ADR-011 创建于 2026-07-09（v0.2.5 版本），可能在创建时未严格对照 10-architecture/README.md §3 的权威定义，导致 7 层架构表出现偏差。特别是：
- L1 的"Linux 6.6 基线"表述可能源于将"内核基线"概念混入"架构层次"概念
- L3 缺失 services 可能是笔误（security/memory/services 三者同属服务层）
- L5/L7 的子仓错位可能是层次编号时的排序错误

**严重度**: **P0（必须修复）**

此不一致直接影响架构决策的准确性，且 ADR 作为架构决策记录具有较高权威性，若不修复会持续传播错误。

### 4.2 P1 次要问题：01-system-architecture.md 概念图与 7 层架构易混淆

**问题描述**: [01-system-architecture.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/10-architecture/01-system-architecture.md) §2.1 的架构分层图显示的是"4 层"概念性架构：

1. Agent 应用层（含 agentrt SDK）
2. agentrt-linux 用户态服务层（airymaxos-services/cognition/cloudnative）
3. agentrt-linux 微内核核心（airymaxos-kernel）
4. Linux 内核（Linux 6.6 内核基线）

此 4 层概念图与 7 层架构模型（L1-L7）并存，且未明确标注"此为概念性展示，非 7 层架构模型"，易引起读者混淆。

**影响分析**:

读者可能误以为：
- 4 层概念图是 7 层架构的"简化版"
- agentrt SDK 是 7 层架构的某一层
- Linux 内核是 7 层架构的 L1

实际上：
- 4 层概念图是整体栈的概念性展示（含外部组件 agentrt）
- 7 层架构是 agentrt-linux 内部 8 子仓的依赖管理模型（不含 agentrt）
- 两者是不同维度的架构描述，应明确区分

**严重度**: **P1（建议修复）**

此问题不影响架构决策的正确性，但影响文档可读性与架构理解的一致性。

### 4.3 P2 观察项：agentrt 在架构图中的位置标注

**观察**: 01-system-architecture.md §2.1 的 4 层概念图中，agentrt SDK 位于"Agent 应用层"内，标注为"同源天然适配"。此标注正确反映了 agentrt 与 agentrt-linux 的关系，但建议在图中或图注中明确"agentrt 是外部组件，运行于 agentrt-linux 之上，非 7 层架构内部"。

**严重度**: **P2（可选优化）**

---

## 5. 修复方案

### 5.1 P0 修复：ADR-011 的 7 层架构表

**修复策略**: 将 ADR-011 的 7 层架构表替换为与权威定义（10-architecture/README.md §3）完全一致的版本，并添加"权威定义引用"注脚。

**修复内容**（见 §6.1 修复执行）:

将 ADR-011 中错误的 7 层架构表：

```
| L1 | Linux 6.6 基线（模型 A 自包含于 kernel 子仓） | agentrt-linux 内部 |
| L2 | kernel | agentrt-linux 内部 |
| L3 | security / memory | agentrt-linux 内部 |
| L4 | cognition | agentrt-linux 内部 |
| L5 | services | agentrt-linux 内部 |
| L6 | system | agentrt-linux 内部 |
| L7 | cloudnative / tests-linux | agentrt-linux 内部 |
```

替换为与权威定义一致的版本：

```
| L1 | 硬件层（CPU/内存/CXL/PMEM，非子仓） | agentrt-linux 内部（硬件基座） |
| L2 | airymaxos-kernel | agentrt-linux 内部 |
| L3 | airymaxos-services + airymaxos-security + airymaxos-memory | agentrt-linux 内部 |
| L4 | airymaxos-cognition | agentrt-linux 内部 |
| L5 | airymaxos-cloudnative | agentrt-linux 内部 |
| L6 | airymaxos-system | agentrt-linux 内部 |
| L7 | airymaxos-tests-linux（横向测试层） | agentrt-linux 内部 |
| — | agentrt（跨平台用户态运行时） | 外部组件，运行于 agentrt-linux 之上 |
```

并添加注脚："> **权威定义引用**: 7 层架构模型的权威定义见 [10-architecture/README.md §3](../../docs/AirymaxOS/10-architecture/README.md)。本表与权威定义保持完全一致。"

### 5.2 P1 修复：01-system-architecture.md 概念图澄清

**修复策略**: 在 01-system-architecture.md §2.1 的架构分层图后增加澄清注脚，明确此为概念性展示，非 7 层架构模型。

**修复内容**（见 §6.2 修复执行）:

在 §2.1 架构分层图后添加：

```
> **概念图澄清**: 上图为 agentrt-linux 整体栈的概念性展示（4 层），用于呈现 agentrt 与 agentrt-linux 的关系。
> agentrt-linux 内部 8 子仓的依赖关系采用 **7 层架构模型**（L1-L7），权威定义见 [10-architecture/README.md §3](README.md#3-架构层次模型)。
> 7 层架构模型不包含 agentrt（agentrt 是外部组件，运行于 agentrt-linux 之上，见 ADR-011）。
```

### 5.3 P2 观察：agentrt 位置标注优化

**建议**: 在 01-system-architecture.md §2.1 的 4 层概念图中，将"Agent 应用层"的图注补充"（agentrt 是外部组件，运行于 agentrt-linux 之上）"。

此为可选优化，不强制执行。

---

## 6. 修复执行

### 6.1 P0 修复：ADR-011 的 7 层架构表

**修复目标文件**: [10-architecture/05-adrs.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/10-architecture/05-adrs.md) ADR-011「决策一」

**修复状态**: ✅ 已执行（2026-07-09，ADR-011 7 层架构表已替换为与权威定义一致的版本，并增加权威定义引用注脚 + 论证支撑引用）

**修复验证**: 修复后使用 Grep 验证 05-adrs.md 中 ADR-011 的 7 层架构表与 10-architecture/README.md §3 完全一致。

### 6.2 P1 修复：01-system-architecture.md 概念图澄清

**修复目标文件**: [10-architecture/01-system-architecture.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/10-architecture/01-system-architecture.md) §2.1

**修复状态**: ✅ 已执行（2026-07-09，ADR-011 7 层架构表已替换为与权威定义一致的版本，并增加权威定义引用注脚 + 论证支撑引用）

---

## 7. 技术依据与优缺点分析（汇总）

### 7.1 三种架构关系方案对比

| 方案 | 描述 | 优点 | 缺点 | 是否采纳 |
|------|------|------|------|---------|
| **方案 A**: agentrt 纳入 7 层架构 | agentrt 作为 L8 或某层纳入 agentrt-linux 内部架构 | 紧密集成，单一架构视图 | 破坏跨平台硬约束（致命）；破坏架构正交性；agentrt 演进受制约 | ❌ 不采纳 |
| **方案 B**: agentrt 直接"成为"agentrt-linux 专属用户态 | agentrt 是 agentrt-linux 唯一用户态 | 零适配（但 IRON-9 v2 已实现） | 丧失跨平台（致命）；破坏 POSIX 兼容；退化为封闭系统 | ❌ 不采纳 |
| **方案 C**: IRON-9 v2 同源关系（采纳） | agentrt 是推荐用户态运行时，以 [SC]+[SS]+[IND] 三层模型运行于 agentrt-linux 之上 | 跨平台 + 同源红利 + 零适配层 + 开放生态 | 需双向 CI 校验 [SC] 变更；需 ADR 流程管理同源关系 | ✅ 采纳 |

### 7.2 方案 C（采纳）的技术依据汇总

| 依据编号 | 依据内容 | 来源 |
|---------|---------|------|
| D-1 | 跨平台硬约束（agentrt 必须 Linux/macOS/Windows） | 用户决策 2026-07-04 |
| D-2 | 架构正交性（7 层架构是 agentrt-linux 内部依赖管理工具） | S-2 层次分解原则 |
| D-3 | IRON-9 v2 [SC] 层 6 头文件逐字节共享，已实现零适配层天然契合 | 120-cross-project-code-sharing.md §2 |
| D-4 | seL4 root task 模型（root task 是独立外部组件，不属于内核） | ES-SEL4-3 服务用户态化 |
| D-5 | "微核心"（agentrt）与"微内核"（agentrt-linux）的语义区分 | 用户决策 2026-07-09 |
| D-6 | agentrt-linux 作为 Linux 发行版，用户态遵循 POSIX，不限于 agentrt | POSIX 标准 + 生产级发行版定位 |
| D-7 | ADR-010 已确立 IRON-9 v2 同源且部分代码共享关系 | ADR-010 Accepted |

### 7.3 方案 C 的边界条件

方案 C 的有效性依赖以下边界条件，若任一条件被破坏需重新评估：

| 边界条件 | 当前状态 | 维护机制 |
|---------|---------|---------|
| [SC] 共享契约层 6 头文件保持逐字节共享 | ✅ 已落地（include/airymax/） | 双向 CI 校验（120-cross-project-code-sharing.md §6） |
| agentrt 保持跨平台独立性 | ✅ 已确立 | 跨平台硬约束 + ADR 流程 |
| agentrt-linux 保持 POSIX 兼容 | ✅ 已确立 | 生产级发行版定位 + systemd 集成 |
| [SC] 变更经双向 CI 校验 | ✅ 已定义 | 120-cross-project-code-sharing.md §6.1 校验流程 |

---

## 8. 技术推论与决策建议

### 8.1 技术推论

基于本报告论证，形成以下技术推论：

**推论 T-1**: 7 层架构模型是 agentrt-linux 内部 8 子仓的依赖管理工具，其边界严格限定于 agentrt-linux 自身子仓。agentrt 作为外部独立项目，不属于此 7 层架构。

**推论 T-2**: agentrt 与 agentrt-linux 的关系是"平台—应用"关系（agentrt 运行于 agentrt-linux 之上），而非"内核—用户态"关系（agentrt 不是 agentrt-linux 的专属用户态）。此关系由 IRON-9 v2 三层共享模型实现，已达成零适配层天然契合。

**推论 T-3**: "将 agentrt 纳入 agentrt-linux 内部架构"或"让 agentrt 直接成为 agentrt-linux 专属用户态"均非获得同源红利的必要条件。IRON-9 v2 [SC] 层的逐字节共享已实现等同于"内部组件"的集成效果，同时保留了 agentrt 的跨平台独立性。

**推论 T-4**: ADR-011 的决策本身（不包含 agentrt + 不直接成为用户态）是正确的，但其中的 7 层架构表存在事实性错误（与权威定义不一致），必须修复以保持架构文档的一致性。

### 8.2 决策建议

**建议 1（P0 必须执行）**: 修复 ADR-011 的 7 层架构表，使其与 10-architecture/README.md §3 权威定义完全一致。修复内容见 §5.1。

**建议 2（P1 建议执行）**: 在 01-system-architecture.md §2.1 架构分层图后增加澄清注脚，明确概念图与 7 层架构模型的关系。修复内容见 §5.2。

**建议 3（决策巩固）**: ADR-011 的两项决策（不包含 agentrt + 不直接成为用户态）经本报告深度论证后确认正确，建议在 ADR-011 中增加"论证报告引用"字段，指向本报告作为决策支撑材料。

**建议 4（长期维护）**: 建立架构文档一致性检查机制，定期 Grep 验证 7 层架构表在所有引用处（10-architecture/README.md §3、20-modules/README.md §2、05-adrs.md ADR-011、04-engineering-baseline.md 等）保持一致。此机制可纳入 08-compliance-checklist.md 的检查规则。

---

## 9. 结论

### 9.1 核心结论

本报告针对 agentrt-linux 7 层架构模型与 agentrt 用户态关系的两个核心问题进行技术论证，结论如下：

1. **7 层架构模型不包含 agentrt 组件**——agentrt 是外部独立跨平台项目，不属于 agentrt-linux 内部 7 层架构（L1-L7）的任何一层。此结论受跨平台硬约束、架构正交性原则、IRON-9 v2 已实现零适配层天然契合、seL4 root task 模型验证、"微核心"与"微内核"语义区分等 5 条技术依据支撑。

2. **agentrt 不直接"成为"agentrt-linux 的用户态，而是以 IRON-9 v2 同源关系"运行于"其上**——agentrt 是 agentrt-linux 的推荐用户态运行时，但非唯一用户态。两者关系是"平台—应用"关系，而非"内核—用户态"关系。此结论受跨平台硬约束、POSIX 兼容性、IRON-9 v2 最优性、seL4 root task 模型、"微核心"与"微内核"层级区分等 5 条技术依据支撑。

### 9.2 发现的问题

本报告发现并记录 3 项问题：

| 问题编号 | 严重度 | 描述 | 修复状态 |
|---------|--------|------|---------|
| P0 | 严重 | ADR-011 的 7 层架构表与权威定义存在 4 处不一致 | ✅ 已执行（§6.1） |
| P1 | 次要 | 01-system-architecture.md §2.1 概念图与 7 层架构易混淆 | ✅ 已执行（§6.2） |
| P2 | 观察 | agentrt 在架构图中的位置标注可选优化 | 可选 |

### 9.3 决策确认

经本报告深度论证，**ADR-011 的两项决策（不包含 agentrt + 不直接成为用户态）确认正确**，无需变更。但 ADR-011 中的 7 层架构表需修复以保持与权威定义一致。

**决策记录**（供最终决策参考）:

> **VP-4（C-2.3 架构模型论证决策确认）**:
> - 7 层架构模型不包含 agentrt 组件（agentrt 是外部独立跨平台项目）
> - agentrt 不直接"成为"agentrt-linux 的用户态，而是以 IRON-9 v2 同源关系"运行于"其上
> - ADR-011 决策本身正确，但 7 层架构表存在事实性错误（P0），需修复
> - IRON-9 v2 三层共享模型（[SC]+[SS]+[IND]）已实现零适配层天然契合，是 agentrt 与 agentrt-linux 关系的最优实现

---

## 10. 相关文档

### 10.1 本报告引用的文档

- [10-architecture/README.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/10-architecture/README.md) §3 —— 7 层架构模型权威定义
- [10-architecture/01-system-architecture.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/10-architecture/01-system-architecture.md) §2.1 —— 概念性架构分层图
- [10-architecture/05-adrs.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/10-architecture/05-adrs.md) ADR-010 / ADR-011 —— 同源关系与 7 层架构决策
- [20-modules/README.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/20-modules/README.md) §2 —— 子仓依赖图与层次说明
- [50-engineering-standards/120-cross-project-code-sharing.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md) —— IRON-9 v2 三层共享模型

### 10.2 相关分析报告

- [01-lessons-learned.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt-linux/_analysis_0.3.0/01-lessons-learned.md) —— C-1 经验总结报告
- [02-version-planning-decision.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt-linux/_analysis_0.3.0/02-version-planning-decision.md) —— C-2.1 版本规划决策报告
- [04-microkernel-source-sel4-only.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt-linux/_analysis_0.3.0/04-microkernel-source-sel4-only.md) —— C-2.2 微内核来源收紧报告

---

## 11. 版本历史

| 版本 | 日期 | 变更 | 责任人 |
|------|------|------|--------|
| v1.0 | 2026-07-09 | 初始版本：完成 7 层架构模型与 agentrt 用户态关系论证，发现 P0/P1/P2 共 3 项问题 | SPHARX 架构审查 |

---

> **报告结束** | C-2.3 架构模型论证报告 v1.0 | 2026-07-09
> 核心结论：7 层架构不含 agentrt + agentrt 以 IRON-9 v2 同源关系运行于 agentrt-linux 之上
> 发现问题：P0（ADR-011 7 层架构表 4 处不一致）+ P1（概念图澄清）+ P2（标注优化）

Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
