Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# seL4 微内核设计参考

> **保密级别**: SPHARX Ltd 内部参考，**闭源不公开**
> **版本**: 0.1.1（文档体系完成）/ 1.0.1（开发）
> **最后更新**: 2026-07-07
> **理论来源**: seL4 形式化验证论文、Proofcraft 2026 最新进展、seL4 基金会白皮书
> **AirymaxOS 对应**: Cupolas capability 安全模型 + airymaxos-tests 形式化验证

---

## 1. seL4 概述

### 1.1 定位

seL4 是全球首个（也是唯一）通过**完整代码级功能正确性形式化验证**的通用操作系统微内核。它属于 L4 微内核家族的第三代成员，由 NICTA/UNSW/Proofcraft 持续开发维护。

- **代码规模**: ~10,000-16,000 SLOC（取决于架构，2026年4月数据）
  - RISC-V 64-bit: ~10,000 SLOC
  - AArch32: ~12,100 SLOC（含虚拟化 13,500 SLOC）
  - AArch64: ~12,600 SLOC（含虚拟化支持）
  - X64: ~16,000 SLOC
- **二进制大小**: 66 KiB（RISC-V）~ 162 KiB（AArch64）
- **性能**: 全球最快微内核，IPC 性能领先竞品 2-10 倍
- **许可证**: GPLv2 + 开源
- **最新版本**: seL4 15.0.0（2026年）

### 1.2 核心差异化能力

| 能力 | 描述 | AirymaxOS 借鉴 |
|------|------|---------------|
| **功能正确性形式化证明** | C 实现严格遵循抽象规范，数学证明覆盖所有代码路径 | airymaxos-tests 形式化验证目标 |
| **CIA 三元组证明** | 机密性/完整性/可用性在形式化规范层面已证明 | Cupolas 安全模型 |
| **Capability 安全** | 不可伪造的权限令牌，最小权限原则 | Cupolas capability 派生模型 |
| **MCS 混合关键性** | 实时/非实时任务时间隔离（2026年6月 RISC-V 验证完成） | SCHED_AGENT 时间隔离 |
| **Dynamic Domain Scheduler** | 运行时半静态域调度（2026年6月，seL4 15.0.0） | 调度策略可插拔 |
| **静态多内核** | 每核独立 seL4 实例（2026年4月） | 多核隔离架构 |

---

## 2. seL4 架构设计精髓

### 2.1 微内核极简主义（Liedtke Minimality Principle）

> "A concept is tolerated inside the microkernel only if moving it outside the kernel, i.e., permitting competing implementations, would prevent the implementation of the system's required functionality."
> — Jochen Liedtke, 1995

seL4 严格遵循这一原则，内核仅提供 4 个原子机制：

| 机制 | 描述 | 对应 AirymaxOS |
|------|------|---------------|
| **线程抽象** | 执行单元，TCB（Thread Control Block） | MicroCoreRT 任务调度 |
| **地址空间** | 页表薄封装，VSpace | MemoryRovol 地址空间管理 |
| **IPC** | 同步消息传递，seL4_MessageInfo | AgentsIPC 128B 消息头 |
| **通知** | 二进制信号量，异步信号 | taskflow 事件通知 |

### 2.2 Capability 安全模型

seL4 的 capability 是其最核心的创新，也是 AirymaxOS Cupolas 安全模型的主要参考来源：

```
Capability = 不可伪造的权限令牌
├── 对象引用（指向内核对象）
├── 访问权限（读/写/执行/授权）
└── 派生关系（CSpace 管理）
```

**核心操作**：

| 操作 | API | 语义 |
|------|-----|------|
| **Mint** | `seL4_CNode_Mint()` | 创建新 capability，可降权 |
| **Copy** | `seL4_CNode_Copy()` | 复制 capability，不可降权 |
| **Move** | `seL4_CNode_Move()` | 移动 capability |
| **Revoke** | `seL4_CNode_Revoke()` | 递归撤销所有派生 capability |
| **Delete** | `seL4_CNode_Delete()` | 删除单个 capability |

**AirymaxOS Cupolas 映射**：

```
seL4 CNode → Cupolas capability 存储
seL4 Mint → Cupolas mint() 派生操作
seL4 Copy → Cupolas mintcopy() 复制操作
seL4 Revoke → Cupolas revoke() 递归撤销
seL4 CSpace → Cupolas blob 结构（cred/inode/file/task）
```

### 2.3 形式化验证栈

seL4 的验证栈是 AirymaxOS 形式化验证路线的黄金标准参考：

```
┌──────────────────────────────────────┐
│  Binaries (二进制)                    │  ← 二进制验证（SMT 求解器）
├──────────────────────────────────────┤
│  C Implementation (C 实现)            │  ← 功能正确性证明（Isabelle/HOL）
│  ~10,000 lines                        │     2026年6月 MCS 验证完成
├──────────────────────────────────────┤
│  Executable Specification (Haskell)   │  ← 可执行规范
├──────────────────────────────────────┤
│  Abstract Specification (Isabelle)    │  ← 抽象规范
├──────────────────────────────────────┤
│  Security Properties (CIA)            │  ← 安全属性证明（机密性/完整性/可用性）
└──────────────────────────────────────┘
```

**验证覆盖范围**（2026年最新）：
- ARM 平台：100% 覆盖
- AArch64 含虚拟化：完整验证
- RISC-V 64-bit MCS：2026年6月完成验证
- X64：完整验证，含 VT-x 虚拟化

### 2.4 IPC 性能设计

seL4 的 IPC 性能是微内核工程的标杆，其设计精髓：

| 设计决策 | 原理 | 效果 |
|---------|------|------|
| 同步 IPC | 发送方阻塞直到接收方回复 | 简化证明，减少缓冲区 |
| 寄存器传递 | 短消息通过寄存器传递，零拷贝 | 比竞品快 2-10 倍 |
| Capability 传递 | IPC 过程中可传递 capability | 安全委托 |
| 端点 (Endpoint) | 消息路由抽象 | 1对多通信 |
| 回复对象 (Reply) | 一次 IPC 的回复通道 | 防止重放攻击 |

---

## 3. 2026 年 seL4 最新进展

### 3.1 MCS 验证完成（2026年6月29日）

> **重大里程碑**：Proofcraft 完成了 seL4 MCS（Mixed-Criticality Systems）配置的功能正确性验证。

**MCS 核心特性**：
- 混合关键性实时系统必需的时间隔离
- 改动范围涉及内核实现和 API 的广泛变更
- 首先在 RISC-V 架构上完成验证
- 下一步：通过 DARPA PROVERS 项目移植到 AArch64

**AirymaxOS 借鉴**：
- SCHED_AGENT 策略需要时间隔离能力
- Agent 工作负载（System1 快速 + System2 慢速）天然是混合关键性场景
- 参考 MCS 的时间预算 + 优先级继承机制

### 3.2 Dynamic Domain Scheduler（2026年6月1日）

> seL4 15.0.0 新特性：运行时半静态域调度

**改进前**：信息流控制要求完全静态的编译时调度表，整个系统生命周期不可变。

**改进后**：
- 新 API 允许加载半静态域调度表
- 系统可在不同阶段切换调度策略（如启动阶段延长时隙，运行阶段缩短时隙）
- SDK 风格系统（如 Microkit）可在启动时设定域调度

**AirymaxOS 借鉴**：
- SCHED_AGENT 的 eBPF 调度策略应支持运行时切换
- 不同 Agent 工作负载阶段需要不同调度策略
- 域调度思想与 Thinkdual 模式（System1/System2）天然契合

### 3.3 静态多内核配置（2026年4月28日）

> 每核独立 seL4 实例，应用可利用多核性能

**架构**：每个 CPU 核心运行独立的 seL4 实例，核间通过共享内存通信。

**AirymaxOS 借鉴**：
- 超节点多核架构的隔离模式
- 认知 kthread 的核亲和性
- GPU/NPU 加速器的独立调度域

### 3.4 形式化验证最新状态

| 验证层级 | 状态 | 架构 |
|---------|------|------|
| 功能正确性 | ✅ 完成 | ARM, AArch64, X64, RISC-V |
| MCS 功能正确性 | ✅ 完成（2026.6.29） | RISC-V |
| AArch64 机密性 | 🔄 Q2/26 完成 | AArch64 |
| 信息流安全 | ✅ 完成 | ARM, AArch64, X64 |
| 二进制验证 | ✅ 完成 | ARM（部分） |
| 时间分析（WCET） | 🔄 进行中 | RISC-V |
| AArch64 MCS 移植 | 🔄 进行中（DARPA PROVERS，Q3/27） | AArch64 |
| 多内核验证 | 🔄 计划中（Q3/28） | 多核 |

### 3.5 LionsOS 生态系统（2026）

> LionsOS 是基于 seL4 Microkit 构建的安全、快速、可适应的操作系统。

**核心特性**：
- 基于 seL4 Microkit 框架，简化 seL4 系统构建
- 初始版本已发布，包含非平凡示例系统
- 由 UNSW Trustworthy Systems 团队持续研发
- 适用于需要形式化验证保证的实际部署场景

**agentrt-liunx 借鉴**：
- Microkit 风格的 OS 框架设计思路
- 基于能力的安全组件组合模式
- 形式化验证与实用性的平衡策略

### 3.6 sDDF 设备驱动框架（2026）

> seL4 Device Driver Framework（sDDF）：高性能、安全的 seL4 驱动框架。

**核心特性**：
- 用户态设备驱动，基于 capability 访问控制
- 高性能设计，减少驱动层性能损失
- 开源可用，由 UNSW 持续研发
- 支持多种设备类型

**agentrt-liunx 借鉴**：
- 驱动用户态化架构设计
- 驱动与内核间的 capability 传递机制
- DMA 隔离与 IOMMU/SystemMMU 集成

### 3.7 seL4 Summit 2026（2026年9月，温哥华）

> seL4 Summit 2026 议程已公布，为期三天。

**议程亮点**：
- Day 1：高层概述与展望（适合新接触 seL4 的参与者）
- Day 2-3：技术深入与更新（研究、开发、实地报告、技术讨论）
- 涵盖形式化验证、实时系统、安全应用等主题

**agentrt-liunx 参考价值**：
- 跟踪 seL4 社区最新技术方向
- 了解微内核在工业界的实际部署经验
- 形式化验证在真实系统中的应用案例

---

## 4. AirymaxOS 与 seL4 的对照分析

### 4.1 架构决策对比

| 维度 | seL4 | AirymaxOS | 决策理由 |
|------|------|-----------|---------|
| **内核模型** | 纯微内核（从零设计） | 宏内核微内核化改造（基于 Linux 6.6） | Linux 生态兼容性 + 渐进式演进 |
| **代码规模** | ~10,000 SLOC | ~30,000,000 SLOC（Linux 基线） | 生态不可替代 |
| **形式化验证** | 全内核已验证 | 仅关键路径（IPC/调度/安全） | 验证成本与收益权衡 |
| **Capability** | 原生 capability | 基于 Linux LSM + capability 扩展 | 兼容 POSIX capability |
| **IPC** | 同步 seL4_MessageInfo | 异步 io_uring + 128B 消息头 | 性能优先 |
| **调度** | 静态优先级 + MCS | sched_ext + SCHED_AGENT | eBPF 可编程调度 |
| **驱动** | 用户态驱动 | 用户态 + 内核态混合 | 渐进式迁移 |

### 4.2 借鉴清单

| seL4 特性 | 借鉴程度 | AirymaxOS 落地方式 | 优先级 |
|-----------|---------|-------------------|--------|
| Liedtke minimality | 完全借鉴 | K-1 内核极简原则 | P0 |
| Capability 安全模型 | 完全借鉴 | Cupolas capability 派生模型（mint/mintcopy/derive/revoke） | P0 |
| 形式化验证栈 | 方法论借鉴 | 关键路径形式化验证（IPC/调度/安全） | P1 |
| MCS 时间隔离 | 设计借鉴 | SCHED_AGENT 时间预算 + 优先级继承 | P0 |
| 域调度 | 设计借鉴 | Thinkdual 模式调度策略切换 | P1 |
| 多内核架构 | 部分借鉴 | 超节点多核隔离 | P1 |
| 用户态驱动 | 完全借鉴 | 驱动用户态化（services 子仓） | P0 |
| 策略机制分离 | 完全借鉴 | sched_ext + LSM + eBPF | P0 |

### 4.3 不借鉴清单

| seL4 特性 | 不借鉴原因 |
|-----------|-----------|
| 纯微内核路线 | Linux 生态兼容性不可替代，宏内核微内核化改造更务实 |
| 同步 IPC | Agent 工作负载需要异步高性能 IPC（io_uring） |
| 静态优先级调度 | Agent 工作负载需要 AI 感知的动态调度 |
| 纯用户态 OS 服务 | 高性能场景需要内核态路径（如 SCHED_AGENT） |

---

## 5. seL4 关键论文与参考资料

### 5.1 核心论文

| 论文 | 年份 | 主题 | AirymaxOS 参考价值 |
|------|------|------|-------------------|
| seL4: Formal Verification of an OS Kernel (Klein et al., SOSP 2009) | 2009 | 功能正确性验证 | ★★★★★ |
| Comprehensive Formal Verification of an OS Microkernel (Klein et al., TOCS 2014) | 2014 | 全栈验证 | ★★★★★ |
| From L3 to seL4: What Have We Learnt in 20 Years of L4 Microkernels? (Elphinstone & Heiser, 2013) | 2013 | 微内核演进 | ★★★★ |
| seL4: Operating Systems With the Reliability of Mathematics (Heiser, IEEE Micro, 2026) | 2026 | 可靠性视角 | ★★★★★ |
| seL4 is Free: What Does This Mean? (seL4 Foundation, 2020) | 2020 | 开源治理 | ★★★ |

### 5.2 在线资源

- seL4 官网: https://sel4.systems
- seL4 文档: https://docs.sel4.systems
- seL4 GitHub: https://github.com/seL4/seL4
- Proofcraft 进展: https://proofcraft.systems
- seL4 基金会: https://sel4.systems/Foundation

---

## 6. AirymaxOS 形式化验证路线图（参考 seL4）

### 6.1 短期目标（1.0.1）

| 验证目标 | 范围 | 方法 | 参考 seL4 |
|---------|------|------|----------|
| IPC 消息头正确性 | AgentsIPC 128B 消息头布局 | 静态分析 + 契约检查 | seL4 MessageInfo |
| Capability 派生模型 | Cupolas mint/mintcopy/derive/revoke | 模型检查（TLA+） | seL4 CNode 操作 |
| 调度安全 | SCHED_AGENT 不会饿死任务 | 形式化规范 | seL4 MCS 时间隔离 |

### 6.2 中期目标（1.1.x）

| 验证目标 | 范围 | 方法 | 参考 seL4 |
|---------|------|------|----------|
| 内存安全 | MemoryRovol 地址空间隔离 | 信息流分析 | seL4 VSpace |
| 中断安全 | 中断处理无重入 | 模型检查 | seL4 IRQ 处理 |
| 关键路径全覆盖 | IPC + 调度 + 安全 + 记忆 | Isabelle/HOL | seL4 功能正确性 |

### 6.3 长期目标（2.0）

- 全内核功能正确性形式化验证（参考 seL4 验证栈）
- 二进制级验证（编译器 + 汇编 + 硬件）
- 安全属性证明（CIA 三元组）

---

## 7. 五维原则映射

| 五维原则 | seL4 体现 | AirymaxOS 落地 |
|---------|----------|---------------|
| **K-1 内核极简** | 10,000 SLOC，仅 4 原子机制 | MicroCoreRT 极简内核 |
| **K-2 接口契约化** | 形式化规范 + 二进制验证 | [SC] 6 个头文件契约 |
| **K-3 服务隔离** | 用户态服务 + capability | Cupolas + 用户态 services |
| **K-4 可插拔策略** | Domain Scheduler | sched_ext + LSM |
| **E-1 安全内生** | CIA 三元组证明 | Cupolas 安全模型 |
| **E-8 可测试性** | 形式化验证替代传统测试 | 关键路径形式化验证 |

---

> **文档结束** | SPHARX Ltd 内部参考 | 闭源不公开 | seL4 是 AirymaxOS 微内核化改造的核心理论参考