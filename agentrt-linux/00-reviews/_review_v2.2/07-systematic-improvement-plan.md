# 07 — agent-linux 系统性改进报告与实施计划 v1.0

> **报告日期**：2026-07-16
> **报告性质**：闭源内部审查报告（docs-closed 路径）
> **报告范围**：基于 _review_v2.2 7 份审查报告 + 3 轮实地调研的系统性改进方案
> **执行基线**：IRON-9 v2 共享模型 + Airymax Unify Design 5 模块 + agent-linux 1.0.1 工程铁律
> **关联审查**：[00-comprehensive-analysis-v2.2.md](00-comprehensive-analysis-v2.2.md)~[06-ipc-data-plane-autonomy-report.md](06-ipc-data-plane-autonomy-report.md)

---

## 0. 执行摘要

### 0.1 核心判定

**复核结论：agent-linux 当前状态确实尚未达到"可按方案启动全面开发"的标准。**

_v2.2 审查报告揭示的 5 大系统性缺陷全部经实地复核确认：

| # | 缺陷类别 | 复核结果 | 阻塞等级 |
|---|---------|---------|---------|
| 1 | 代码真空（0 行可编译源码） | **复核通过** — agent-linux 8 子仓均为 README-only，kernel/include/airymax/ 目录不存在 | P0 |
| 2 | [SC] 共享头文件不完整 | **复核通过** — error.h + log_types.h 两端均不存在；agentrt 端实际 8 个 [SC] 头文件（含 uapi_compat.h），agent-linux 端 0 个 | P0 |
| 3 | agentrt 技术债阻塞统一 | **复核通过** — BAN-294/299/305 仍然存在；双错误码（AIRY_E* vs AIRY_ERR_*）+ 双日志管线（LOG_* vs AIRY_LOG_*）并存 | P0 |
| 4 | 设计文档鸿沟（20 份缺失） | **复核通过** — 10-architecture 缺 08-unify-design/09-degraded-survival-layer；20-modules 缺 09~13；30-interfaces 缺 08~10；40-dataflows 缺 05~07；110-security 缺 04~05 | P0+P1 |
| 5 | 生存层 + IPC 数据面自治缺失 | **复核通过** — IRON-9 v2 仅定义 [SC]/[SS]/[IND] 三层，无 [DSL] 第四层 | P0+P1 |

### 0.2 改进路径

本报告提出 **4 阶段改进路径**，总工期 ~28 个工作日，按"先奠基 → 再文档化 → 再修复技术债 → 最后启动开发"的顺序推进：

| 阶段 | 工期 | 核心工作 | 验收 |
|------|------|---------|------|
| **Phase 0：奠基修复** | 5 天 | 修复 SSoT 权威性 + 创建第一个可编译内核模块 + 创建 [SC] 头文件物理宿主 | 1 个 .ko 可 insmod + sc-dual-ci 可运行 |
| **Phase 1：方案文档化** | 12 天 | 撰写 20 份缺失设计文档 + 升级 4 份现有文档至工程级 | docs/AirymaxOS 文档完整度 ≥ 95% |
| **Phase 2：agentrt 技术债修复** | 6 天 | BAN-294/299/305 修复 + 双错误码收敛 + 双日志管线收敛 | agentrt 全仓库单一 SSoT |
| **Phase 3：开发启动前置** | 5 天 | Airymax Unify Design 完整集成 + [DSL] 层落地 + 双向 CI 全绿 | 5 模块工程可行性达标 |

### 0.3 风险声明

本改进计划**不引入新特性**（遵守 IRON-1）、**不创建桩文件**（遵守 IRON-2）、**不绕开功能限制**（遵守 IRON-3）、**不简化功能**（遵守 IRON-4）、**不设计未实现的功能**（遵守 IRON-5）。所有改进均以"将对话上下文中的设计固化为正式文档 + 修复已识别的工程缺陷"为边界。

---

## 1. 历史问题系统性跟踪清单

### 1.1 历史问题分类总览

经全面回顾所有对话记录，agent-linux 方案历史问题共 **47 项**，分为 6 类：

| 类别 | 问题数 | 已修复 | 待修复 | 阻塞开发 |
|------|--------|--------|--------|---------|
| 代码真空 | 6 | 0 | 6 | 6 |
| [SC] 共享头文件 | 6 | 0 | 6 | 4 |
| agentrt 技术债 | 9 | 0 | 9 | 6 |
| 设计文档缺失 | 22 | 0 | 22 | 8 |
| 生存层缺失 | 5 | 0 | 5 | 3 |
| 微内核化设计风险 | 9 | 0 | 9 | 4 |

### 1.2 历史问题逐项清单

#### 1.2.1 代码真空类（VAC-001~006）

| ID | 问题描述 | 当前状态 | 阻塞等级 | 修复路径 |
|----|---------|---------|---------|---------|
| VAC-001 | agent-linux 无任何 .c/.h 源文件 | 待修复 | P0 | Phase 0 创建首个 airy_core.c |
| VAC-002 | 8 子仓全部为 README-only 空壳 | 待修复 | P0 | Phase 0 kernel/ 创建 include/airymax/ + airy_core.c |
| VAC-003 | 无 Kconfig 文件 | 待修复 | P0 | Phase 0 创建 kernel/Kconfig |
| VAC-004 | 无 Kbuild 文件 | 待修复 | P0 | Phase 0 创建 kernel/Makefile |
| VAC-005 | CI workflows 无法验证空仓库 | 待修复 | P1 | Phase 0 后 ci-kernel.yml 可运行 |
| VAC-006 | kernel 子仓无第一个可 insmod 的内核模块 | 待修复 | P0 | Phase 0 交付 airy_core.ko |

#### 1.2.2 [SC] 共享头文件类（SC-001~006）

| ID | 问题描述 | 当前状态 | 阻塞等级 | 修复路径 |
|----|---------|---------|---------|---------|
| SC-001 | error.h 不存在（两端） | 待修复 | P0 | Phase 0 创建于 agent-linux/kernel/include/airymax/ |
| SC-002 | log_types.h 不存在（两端） | 待修复 | P0 | Phase 0 创建于 agent-linux/kernel/include/airymax/ |
| SC-003 | uapi_compat.h 未处理 `#ifdef __KERNEL__` 路径 | 待修复 | P0 | Phase 0 修复为三路桥接 |
| SC-004 | [SC] 双向 CI 无法验证（无 agent-linux 代码端） | 待修复 | P0 | Phase 0 后 sc-dual-ci.yml 可运行 |
| SC-005 | sched.h 缺少 Agent 生命周期状态枚举 | 待修复 | P1 | Phase 1 扩展 sched.h |
| SC-006 | ipc.h 缺少 capability 缓存校验字段 | 待修复 | P1 | Phase 1 扩展 ipc.h reserved[84] |

#### 1.2.3 agentrt 技术债类（BAN/ERR/LOG）

| ID | 问题描述 | 当前状态 | 阻塞等级 | 修复路径 |
|----|---------|---------|---------|---------|
| BAN-294 | heapstore_log.h 自建独立日志管线 | 待修复 | P0 | Phase 2 删除并替换为 logging_compat.h |
| BAN-299 | memory.c 11 处 fprintf(stderr) | 待修复 | P1 | Phase 2 替换为 LOG_ERROR |
| BAN-305 | svc_logger.h 不含 logging_compat.h | 待修复 | P1 | Phase 2 补充 #include |
| ERR-001 | AIRY_E* 和 AIRY_ERR_* 双错误码并存 | 待修复 | P0 | Phase 2 统一为 AIRY_E* |
| ERR-D01 | error.h 物理文件未创建 | 待修复 | P0 | Phase 0 创建 |
| ERR-D02 | AIRY_ERR_* 未收敛 | 待修复 | P0 | Phase 2 收敛到 AIRY_E* |
| ERR-D03 | 迁移计划未确定 | 待修复 | P0 | Phase 1 撰写 12-error-code-migration-plan.md |
| LOG-001 | LOG_* 和 AIRY_LOG_* 双日志管线并存 | 待修复 | P0 | Phase 2 二选一收敛 |
| LOG-002 | LOG-21~26 高级功能接口已定义但实现为空 | 待修复 | P2 | Phase 2 标记为废弃或实现 |

#### 1.2.4 设计文档缺失类（DOC-N01~N18 + DOC-U01~U04）

| ID | 文档路径 | 优先级 | 阶段 |
|----|---------|--------|------|
| DOC-N01 | 10-architecture/08-unify-design.md | P0 | Phase 1 |
| DOC-N02 | 10-architecture/09-degraded-survival-layer.md | P0 | Phase 1 |
| DOC-N03 | 30-interfaces/08-sc-error-contract.md | P0 | Phase 1 |
| DOC-N04 | 30-interfaces/09-sc-log-types-contract.md | P0 | Phase 1 |
| DOC-N05 | 30-interfaces/10-sc-sched-extension.md | P1 | Phase 1 |
| DOC-N06 | 40-dataflows/05-ring-buffer-logging.md | P0 | Phase 1 |
| DOC-N07 | 40-dataflows/06-logger-daemon-design.md | P1 | Phase 1 |
| DOC-N08 | 40-dataflows/07-panic-survival-path.md | P1 | Phase 1 |
| DOC-N09 | 110-security/04-ipc-data-plane-autonomy.md | P1 | Phase 1 |
| DOC-N10 | 110-security/05-ipc-control-plane-reconciliation.md | P1 | Phase 1 |
| DOC-N11 | 20-modules/09-kernel-agent-supervisor.md | P1 | Phase 1 |
| DOC-N12 | 20-modules/10-user-supervisor-daemon.md | P1 | Phase 1 |
| DOC-N13 | 20-modules/11-unified-config.md | P1 | Phase 1 |
| DOC-N14 | 20-modules/12-logger-daemon-module.md | P2 | Phase 1 |
| DOC-N15 | 20-modules/13-printk-bridge.md | P2 | Phase 1 |
| DOC-N16 | 50-engineering-standards/11-sc-header-type-bridging.md | P1 | Phase 1 |
| DOC-N17 | docs/AirymaxRT/50-engineering-standards/11-log-convergence-plan.md | P1 | Phase 2 |
| DOC-N18 | docs/AirymaxRT/50-engineering-standards/12-error-code-migration-plan.md | P1 | Phase 2 |
| DOC-U01 | 03-microkernel-strategy.md 升级 v0.1.1 → v1.0+ | P1 | Phase 1 |
| DOC-U02 | 07-ipc-fastpath.md 升级 v0.2.8 → v1.0+ | P1 | Phase 1 |
| DOC-U03 | 03-capability-model.md 升级 v0.1.1 → v1.0+ | P1 | Phase 1 |
| DOC-U04 | 06-iron9-shared-model.md 新增 [DSL] 层 | P1 | Phase 1 |

#### 1.2.5 生存层缺失类（DSL-001~005）

| ID | 问题描述 | 阻塞等级 | 阶段 |
|----|---------|---------|------|
| DSL-001 | error.h 无 AIRY_SC_FALLBACK 降级块 | P0 | Phase 0 + Phase 1 |
| DSL-002 | log_types.h 无 Panic 回退 printk 原生路径 | P0 | Phase 0 + Phase 1 |
| DSL-003 | sched.h 无 3 态降级（RUNNING/STOPPED/DEAD） | P1 | Phase 1 |
| DSL-004 | ipc.h 无共享失败降级（pipe/socket 回退） | P1 | Phase 1 |
| DSL-005 | 无 [DSL] 层统一框架设计 | P0 | Phase 1（DOC-N02） |

#### 1.2.6 微内核化设计风险类（MKR-001~009）

详见第 3 章深度审查。

---

## 2. 当前状态实地评估

### 2.1 agent-linux 仓库实际状态（复核结果）

#### 2.1.1 顶层目录结构

```
agent-linux/
├── CODEOWNERS              # 工程治理
├── CONTRIBUTING.md         # 工程治理
├── LICENSE                 # 许可证
├── MAINTAINERS             # 维护者
├── Makefile                # 空顶层 Makefile
├── NOTICE                  # 声明
├── README.md              # 管理仓 README
├── README_zh.md           # 中文 README
├── SECURITY.md             # 安全策略
├── ssot-registry.yaml      # SSoT 机器可读
├── scripts/                # 工具脚本
├── tools/                  # 工具
├── kernel/                 # 子仓：仅 README + LICENSE + NOTICE（空壳）
├── services/               # 子仓：仅 README（空壳）
├── security/               # 子仓：仅 README（空壳）
├── cognition/              # 子仓：仅 README（空壳）
├── memory/                 # 子仓：仅 README（空壳）
├── system/                 # 子仓：仅 README（空壳）
├── cloudnative/            # 子仓：仅 README（空壳）
└── tests-linux/            # 子仓：仅 README（空壳）
```

#### 2.1.2 关键缺失项

- **kernel/include/airymax/ 目录不存在** — 比 _v2.2 审查报告所述"目录存在但为空"更严重
- **0 个 .c 文件**
- **0 个 .h 文件**
- **0 个 Kconfig**
- **0 个 Kbuild**
- **0 个可 insmod 的内核模块**

### 2.2 agentrt 端 [SC] 头文件实际状态

`agentrt/commons/include/airymax/` 实际包含 8 个文件：

| # | 文件名 | 状态 | 用途 |
|---|--------|------|------|
| 1 | bpf_struct_ops.h | 存在 | BPF 结构操作 |
| 2 | cognition_types.h | 存在 | 认知类型 |
| 3 | ipc.h | 存在（82 行） | IPC 消息头 |
| 4 | memory_types.h | 存在 | 记忆类型 |
| 5 | sched.h | 存在（79 行） | 调度描述符 |
| 6 | security_types.h | 存在 | 安全类型 |
| 7 | syscalls.h | 存在 | syscall 契约 |
| 8 | uapi_compat.h | 存在 | UAPI 类型桥接（仅 `#ifdef __linux__` 二路） |
| — | error.h | **不存在** | 错误码 SSoT（5 模块统一核心） |
| — | log_types.h | **不存在** | 日志类型 SSoT（5 模块统一核心） |

### 2.3 docs/AirymaxOS 文档体系实际盘点

#### 2.3.1 顶级目录文件计数（实测）

| 目录 | 实际 .md 数（含 README） | 缺失文档数 | 完整度 |
|------|--------------------------|-----------|--------|
| 10-architecture | 9 | 2 | 78% |
| 20-modules | 9 | 5 | 50% |
| 30-interfaces | 8 | 3 | 62% |
| 40-dataflows | 5 | 3 | 40% |
| 50-engineering-standards | 9 + 5 子目录 | 4 | 60% |
| 70-build-system | 4 | 1 | 75% |
| 110-security | 4 | 2 | 50% |
| 90-observability | 3 | 0（已完整） | 100% |
| 100-operations | 3 | 0（已完整） | 100% |
| 其他 13 个目录 | ~70 | 0 | ~95% |

**整体文档体系完整度：~85%**（128 份现有 + 20 份缺失 = 148 份应有，已存在 86.5%）

#### 2.3.2 关键文档版本状态

| 文档 | 当前版本 | 目标版本 | 需升级内容 |
|------|---------|---------|-----------|
| 03-microkernel-strategy.md | v0.1.1 | v1.0+ | [DSL] 降级策略 + 内核态生存层 |
| 07-ipc-fastpath.md | v0.2.8 | v1.0+ | capability daemon 离线降级路径 |
| 03-capability-model.md | v0.1.1 | v1.0+ | 离线缓存校验 + Reconciliation |
| 06-iron9-shared-model.md | v0.1.0 | v1.0+ | 新增 [DSL] 第四层定义 |

---

## 3. 微内核化改造深度审查

### 3.1 技术选型合理性矩阵

依据 `03-microkernel-strategy.md` 实地审查，对 4 大技术选型逐一评估：

#### 3.1.1 sched_ext（SCHED_AGENT）调度策略

| 维度 | 评估 | 详情 |
|------|------|------|
| **合理性** | ✅ 合理 | sched_ext 是 Linux 6.6 已合入的 extensible scheduler 框架，BPF 驱动，正是"微内核化"的正确路径 |
| **成熟度** | ⚠️ 需验证 | sched_ext 在 6.6 中首次合入主线，生产部署案例较少 |
| **风险** | 中 | 内核 ABI 不稳定，可能跨小版本变更；BPF 程序无法调试 |
| **边界** | kthread 优先级倒置、cgroup 与 sched_ext 冲突 | 已知风险，需 Kconfig + sysctl 开关控制 |
| **改进建议** | 1) 增加 sched_ext 版本兼容矩阵 2) 定义 SCHED_AGENT BPF 程序的最小接口集 3) 增加 fallback 到 EEVDF 的降级路径 |

#### 3.1.2 eBPF kfunc + dynamic pointer

| 维度 | 评估 | 详情 |
|------|------|------|
| **合理性** | ✅ 合理 | eBPF 是 Linux 6.6 推荐的内核扩展机制，kfunc + dynamic pointer 是 6.6 新特性 |
| **成熟度** | ✅ 成熟 | eBPF 在内核中已被大量使用（XDP、io_uring、cgroup） |
| **风险** | 低 | dynamic pointer 提升了 eBPF 内存安全性，但可加载的 kfunc 数量在 6.6 中有限 |
| **边界** | eBPF verifier 拒绝复杂程序 | 需在设计阶段约束 BPF 程序复杂度 |
| **改进建议** | 1) 列出 agent-linux 必需的 kfunc 清单 2) 定义 BPF 程序大小上限 3) 增加 verifier 失败的降级路径 |

#### 3.1.3 io_uring 零拷贝 IPC

| 维度 | 评估 | 详情 |
|------|------|------|
| **合理性** | ✅ 合理 | io_uring 是 Linux 5.1+ 的高性能异步 IO 框架，6.6 中已具备零拷贝能力 |
| **成熟度** | ✅ 成熟 | io_uring 已被大量生产部署（数据库、网络、存储） |
| **风险** | 中 | (1) io_uring 历史安全漏洞多；(2) 旧内核不支持；(3) 与 seL4 Endpoint 模型映射不完美 |
| **边界** | 旧内核回退、安全沙箱限制 | 需 Kconfig 依赖 CONFIG_IO_URING |
| **改进建议** | 1) 定义 io_uring 安全加固清单（注册 sqpoll、限制 opcode） 2) 定义 POSIX MQ 回退路径（[DSL] 层） 3) 明确 io_uring 与 seL4 Endpoint 的语义差异 |

#### 3.1.4 Rust 实验性支持

| 维维度 | 评估 | 详情 |
|------|------|------|
| **合理性** | ⚠️ 需谨慎 | Linux 6.6 已合入 Rust 基础设施（Kbuild、bindings），但驱动可用性有限 |
| **成熟度** | ⚠️ 不成熟 | Rust for Linux 在 6.6 中仅支持基础驱动，不支持核心子系统 |
| **风险** | 高 | (1) LLVM 版本绑定；(2) bindgen 不稳定；(3) 编译时间显著增加 |
| **边界** | 仅限叶子驱动 | 不可用于 IPC、调度、安全等核心子系统 |
| **改进建议** | 1) 明确 Rust 仅用于叶子驱动（[IND] 层） 2) 不将 Rust 列为 P0 特性 3) 增加 C 版本作为参考实现 |

### 3.2 seL4 微内核思想借鉴深度评估

#### 3.2.1 已借鉴的核心思想

| seL4 概念 | agent-linux 借鉴点 | 借鉴深度 | 评估 |
|-----------|---------------------|---------|------|
| Capability-based security | security 子仓 capability 模型（93 字节 airy_cnode） | 深度 | ✅ 充分借鉴 |
| Minimal IPC（消息传递） | services 子仓 io_uring + 128B 消息头 | 中度 | ⚠️ 缺离线校验（IPC-D02） |
| Fastpath 优化 | kernel 子仓 IPC fastpath 状态机 | 中度 | ⚠️ 缺控制面离线降级 |
| Minimal privileged code（Liedtke minimality） | kernel 子仓最小化改造 | 深度 | ✅ 充分借鉴 |
| User-space servers | services 子仓 VFS/网络/驱动用户态化 | 深度 | ✅ 充分借鉴 |
| Verified kernel（形式化验证） | tests-linux 子仓形式化验证 | 中度 | ⚠️ 仅声明，未设计验证策略 |

#### 3.2.2 遗漏的关键 seL4 思想（NEW-MKR-001~003）

| ID | 遗漏的 seL4 思想 | 影响 | 修复建议 |
|----|-----------------|------|---------|
| NEW-MKR-001 | **seL4 的 MDB（Capability Derivation Tree）完整性约束** | capability 撤销的传递性未明确 | DOC-U03 升级 03-capability-model.md 时补充 |
| NEW-MKR-002 | **seL4 的 Fault Handler 模型** | Agent 故障处理路径未设计 | 新增 20-modules/14-agent-fault-handler.md（P2，Phase 1） |
| NEW-MKR-003 | **seL4 的 Domain scheduling** | 多域调度隔离未设计 | 评估后决定是否纳入 1.0.1 或延期至 2.x |

### 3.3 微内核化设计风险清单（MKR-001~009）

| ID | 风险点 | 严重度 | 影响范围 | 缓解方案 |
|----|--------|--------|---------|---------|
| MKR-001 | sched_ext BPF 程序在 6.6 内核 ABI 变更风险 | 高 | 调度子系统 | 定义最小 BPF 接口集 + 版本兼容矩阵 |
| MKR-002 | io_uring 安全漏洞历史（CVE-2023-21490 等） | 中 | IPC 子系统 | 启用 io_uring 注册模式 + 限制 opcode |
| MKR-003 | Rust 内核驱动编译时间显著增加 | 中 | 构建系统 | 仅叶子驱动允许 Rust + 增量编译 |
| MKR-004 | capability 离线校验的安全边界（expires_ns 时钟源） | 高 | IPC + 安全子系统 | 使用 CLOCK_MONOTONIC + 显式时钟同步 |
| MKR-005 | 控制/数据面分离后的内存一致性 | 高 | IPC 子系统 | 显式内存屏障 + READ_ONCE/WRITE_ONCE |
| MKR-006 | Panic 时 Ring Buffer 锁的死锁风险 | 高 | 日志子系统 | printk_safe 模型 + NMI-safe buffer |
| MKR-007 | Logger Daemon 崩溃后日志丢失 | 中 | 日志子系统 | ring buffer 持久化 + 重启后扫描 |
| MKR-008 | 多核 capability 缓存的原子性 | 高 | 安全子系统 | per-CPU 缓存 + RCU 同步 |
| MKR-009 | 微内核化改造的渐进性（不可一次性切换） | 高 | 全系统 | 分 Phase 1（VFS）→ Phase 2（网络/驱动）→ Phase 3（IPC） |

### 3.4 工程实现细节评估

#### 3.4.1 文档-工程断层

经审查 `03-microkernel-strategy.md`、`03-capability-model.md`、`07-ipc-fastpath.md` 三份核心文档：

| 文档 | 工程实现细节覆盖 | 缺失项 |
|------|-----------------|--------|
| 03-microkernel-strategy.md | 60% | 缺 sched_ext BPF 程序接口、io_uring opcode 限制清单 |
| 03-capability-model.md | 70% | 缺离线缓存校验、Reconciliation 流程 |
| 07-ipc-fastpath.md | 85% | 缺控制面离线降级路径、capability daemon 离线时的 fastpath 行为 |

**结论**：现有文档平均工程实现细节覆盖率 ~72%，需提升至 ≥ 95%。

---

## 4. Airymax Unify Design 整合方案

### 4.1 设计理念评估

Airymax Unify Design 是在 IRON-9 v2 [SC]/[SS]/[IND] 三层共享模型基础上提出的"5 模块统一方案"。

#### 4.1.1 设计合理性

| 维度 | 评估 | 详情 |
|------|------|------|
| **架构正确性** | ✅ 正确 | [SC] 物理同一份 + [SS] 语义同源 + [IND] 完全独立 是正确的三层共享架构 |
| **覆盖完整性** | ⚠️ 不完整 | 缺少 [DSL] 第四层（共享失败时的生存路径） |
| **可实施性** | ⚠️ 需奠基 | 当前 agentrt 技术债阻塞统一，需先修复 |
| **与 IRON-9 v2 一致性** | ✅ 一致 | 5 模块设计未违反 IRON-9 v2 三层模型 |

#### 4.1.2 可行性判定（设计层 vs 工程层）

| 模块 | 设计可行性 | 工程可行性 | 工程阻塞项 |
|------|-----------|-----------|-----------|
| 1. 统一错误码 | ✅ | ❌ | error.h 物理文件未创建 + AIRY_ERR_* 未收敛 |
| 2. 统一日志+打印 | ✅ | ❌ | log_types.h 未创建 + 双日志管线并存 + 3 BAN 违规 |
| 3. 统一生命周期 | ⚠️ 部分 | ❌ | sched.h 缺状态枚举 + 无 Supervisor 设计文档 |
| 4. 统一配置管理 | ⚠️ 部分 | ❌ | 无两端代码 + schema 未定义 |
| 5. IPC 数据面自治 | ⚠️ 部分 | ❌ | 0 行代码 + 缓存校验未文档化 |

**结论**：5 模块在**设计层**可行，在**工程层**全部阻塞。需先完成 Phase 0~2 的奠基与技术债修复，5 模块才能从"设计可行"跃迁为"工程可行"。

### 4.2 整合方案

#### 4.2.1 整合到 IRON-9 v2

```
原 IRON-9 v2（3 层）：
  [SC]  Shared Contract Layer  — 物理同一份，逐字节相同
  [SS]  Semantic Source Layer   — API 语义一致，签名独立
  [IND] Independent Layer       — 完全独立演进

扩展后 IRON-9 v3（4 层）：
  [SC]  Shared Contract Layer     — 物理同一份，逐字节相同
  [SS]  Semantic Source Layer     — API 语义一致，签名独立
  [IND] Independent Layer         — 完全独立演进
  [DSL] Degraded Survival Layer   — 共享失败时的最小可运行子集
```

**[DSL] 层核心原则**（4 条）：
1. 内核态永远不依赖用户态可用性
2. 用户态永远不假设内核态 [SC] 头文件版本一致
3. [SC] 共享失败不导致系统不可用
4. [DSL] 是设计时约束，不是运行时 fallback

#### 4.2.2 5 模块在 4 层架构中的映射

| 模块 | [SC] 层 | [SS] 层 | [IND] 层 | [DSL] 层 |
|------|---------|---------|---------|---------|
| 1. 统一错误码 | error.h | errno 映射 API | 各端实现 | AIRY_SC_FALLBACK 块（38 个 POSIX 码） |
| 2. 统一日志 | log_types.h | log_write API | 各端格式化 | Panic 回退 printk |
| 3. 统一生命周期 | sched.h 扩展 | supervisor API | 各端实现 | 3 态降级（RUNNING/STOPPED/DEAD） |
| 4. 统一配置 | — | key-value schema | Kconfig vs JSON/TOML | 默认值降级 |
| 5. IPC 数据面自治 | ipc.h 扩展 | send/recv API | 各端实现 | pipe/socket 回退 |

#### 4.2.3 整合实施步骤

| 步骤 | 内容 | 阶段 | 关联文档 |
|------|------|------|---------|
| 1 | 更新 06-iron9-shared-model.md，新增 [DSL] 层定义 | Phase 1 | DOC-U04 |
| 2 | 撰写 08-unify-design.md 总纲 | Phase 1 | DOC-N01 |
| 3 | 撰写 09-degraded-survival-layer.md | Phase 1 | DOC-N02 |
| 4 | 撰写 [SC] error.h 契约文档 | Phase 1 | DOC-N03 |
| 5 | 撰写 [SC] log_types.h 契约文档 | Phase 1 | DOC-N04 |
| 6 | 撰写 [SC] sched.h 扩展文档 | Phase 1 | DOC-N05 |
| 7 | 撰写 Ring Buffer 日志设计 | Phase 1 | DOC-N06 |
| 8 | 撰写 IPC 数据面自治设计 | Phase 1 | DOC-N09 |
| 9 | 创建 [SC] error.h + log_types.h 物理文件 | Phase 0 | SC-001/002 |
| 10 | 在每个 [SC] 文件底部增加 `#ifdef AIRY_SC_FALLBACK` 降级块 | Phase 0+1 | DSL-001~005 |

### 4.3 风险评估

| 风险 | 严重度 | 缓解 |
|------|--------|------|
| [DSL] 层设计过度复杂化 | 中 | 严格遵守"最小可运行子集"原则 |
| 5 模块统一在工程实施前未充分验证 | 高 | Phase 3 必须完成双向 CI 全绿 |
| agentrt 技术债修复影响生产可用性 | 中 | 严格按 ERR-D03 迁移计划渐进式收敛 |
| [SC] 双向 CI 增加构建时间 | 低 | 仅在 PR 触发，不在 push 触发 |

---

## 5. SSoT 体系强化方案

### 5.1 SSoT 权威性强化原则

#### 5.1.1 三层 SSoT 一致性模型

```
┌───────────────────────────────────────────────────┐
│  Tier 1: 机器可读 SSoT                            │
│  agent-linux/ssot-registry.yaml                 │
│  ↓ CI 自动校验                                    │
├───────────────────────────────────────────────────┤
│  Tier 2: 人类可读 SSoT                            │
│  docs/AirymaxOS/50-engineering-standards/         │
│  09-ssot-registry.md                              │
│  ↓ 文档交叉引用                                   │
├───────────────────────────────────────────────────┤
│  Tier 3: 镜像引用 SSoT                            │
│  00-handbook.md / 04-engineering-philosophy.md    │
│  / 03-microkernel-strategy.md 等所有引用文档       │
└───────────────────────────────────────────────────┘
```

**强化规则**：
- Tier 1 是唯一权威源，Tier 2/3 必须与之一一对应
- 任何 SSoT 编号变更必须先在 Tier 1 修改，然后 CI 自动验证 Tier 2/3 一致性
- 禁止在 Tier 3 重新定义编号

### 5.2 日志系统统一规范

#### 5.2.1 决策：LOG_* 为唯一 SSoT

**理由**：
1. LOG_* 是更现代的命名（与 Linux printk 的 pr_* 一致）
2. AIRY_LOG_* 是兼容桥接，应废弃
3. 68 个文件依赖 logging_compat.h，迁移工作量可控

#### 5.2.2 统一日志管线架构

```
┌──────────────────────────────────────────────────┐
│  统一日志管线（5 模块之 2）                       │
├──────────────────────────────────────────────────┤
│  [SC] log_types.h  →  struct airy_log_record 128B │
│                     + 5 级别枚举                  │
│                     + Linux 8 级 printk 映射表   │
├──────────────────────────────────────────────────┤
│  [SS] log_write()  →  统一写入 API                │
│                     内核态：prb_reserve + commit  │
│                     用户态：mmap 写入 ring buffer │
├──────────────────────────────────────────────────┤
│  [IND] 格式化       →  Logger Daemon（用户态）     │
│                     异步：从 ring buffer 读取     │
│                     输出：file/syslog/journal     │
├──────────────────────────────────────────────────┤
│  [DSL] Panic 回退   →  printk 原生路径             │
│                     printk_safe_enter/exit        │
│                     NMI-safe emergency buffer     │
└──────────────────────────────────────────────────┘
```

#### 5.2.3 5 级别枚举定义（强制统一）

```c
/* [SC] log_types.h */
enum airy_log_level {
    AIRY_LOG_DEBUG   = 0,
    AIRY_LOG_INFO    = 1,
    AIRY_LOG_WARN    = 2,
    AIRY_LOG_ERROR   = 3,
    AIRY_LOG_FATAL   = 4,
};

/* Linux printk 8 级 → Airymax 5 级映射（强制） */
static const int airy_printk_to_level[8] = {
    [0] = AIRY_LOG_FATAL,   /* KERN_EMERG */
    [1] = AIRY_LOG_FATAL,   /* KERN_ALERT */
    [2] = AIRY_LOG_FATAL,   /* KERN_CRIT */
    [3] = AIRY_LOG_ERROR,   /* KERN_ERR */
    [4] = AIRY_LOG_WARN,    /* KERN_WARNING */
    [5] = AIRY_LOG_INFO,    /* KERN_NOTICE */
    [6] = AIRY_LOG_INFO,    /* KERN_INFO */
    [7] = AIRY_LOG_DEBUG,   /* KERN_DEBUG */
};
```

### 5.3 函数命名统一规范

#### 5.3.1 决策：`airy_` 为 Airymax 全项目唯一前缀

**理由**：
1. `airy_` 与 agent-linux 的 `airy_*` 函数前缀一致
2. `agentrt_` 前缀仅用于 CMake target / 包名（不用于函数）
3. `agentos_` 前缀已于 2026-07-05 全面废弃（IRON 决策）
4. 子模块前缀（heapstore_*、memoryrovol_*、coreloopthree_*）需收敛到 `airy_*`

#### 5.3.2 函数前缀映射表

| 旧前缀 | 新前缀 | 影响范围 | 迁移阶段 |
|--------|--------|---------|---------|
| agentos_* | airy_* | 已完成（2026-07-05） | — |
| agentrt_*（函数） | airy_* | agentrt 全仓库 | Phase 2 |
| heapstore_* | airy_heapstore_* | heapstore 模块 | Phase 2 |
| memoryrovol_* | airy_memoryrovol_* | memory 模块 | Phase 2 |
| coreloopthree_* | airy_coreloopthree_* | cognition 模块 | Phase 2 |
| cupolas_* | airy_cupolas_* | security 模块 | Phase 2 |
| AIRY_LOG_*（宏） | LOG_*（宏） | 68 文件 | Phase 2 |
| AIRY_ERR_* | AIRY_E* | 全仓库 | Phase 2 |

**注意**：CMake target / 包名仍保留 `agentrt_*`（如 `agentrt_all`、`agentrt_commons`），因为这是构建系统标识，不是函数前缀。

### 5.4 错误码体系统一规范

#### 5.4.1 决策：AIRY_E* 为唯一 SSoT

**理由**：
1. AIRY_E* 与 POSIX errno 命名一致（AIRY_EPERM、AIRY_ENOENT 等）
2. AIRY_ERR_* 是 agentrt 早期扩展码，命名风格不统一
3. ~30 个 POSIX 码 + ~90 个扩展码，迁移工作量可控

#### 5.4.2 统一错误码架构

```c
/* [SC] error.h */
typedef __s32 airy_err_t;

/* 分段哨兵 */
#define AIRY_E_BASE       (-1)
#define AIRY_E_POSIX_END  (-40)     /* POSIX 码段 [-1, -40] */
#define AIRY_E_CUSTOM_END (-800)    /* 自定义码段 [-41, -800] */
#define AIRY_ERR_COUNT    800       /* 哨兵值 */

/* POSIX 码（30 个） */
#define AIRY_EPERM        (-1)
#define AIRY_ENOENT       (-2)
/* ... */

/* 自定义码（按域分组） */
#define AIRY_EPROTO       (-71)     /* 协议错误 */
#define AIRY_ECAPABILITY  (-101)    /* capability 错误 */
#define AIRY_ESC_SHARED   (-201)    /* [SC] 共享失败 */
#define AIRY_EDSL_FALLBACK (-301)   /* [DSL] 降级模式 */
/* ... */

/* [DSL] 降级块 */
#ifdef AIRY_SC_FALLBACK
#undef  AIRY_ERR_COUNT
#define AIRY_ERR_COUNT  38
#define AIRY_SC_FALLBACK_ERRCODE  1
#endif
```

### 5.5 数据结构统一规范

#### 5.5.1 [SC] 头文件类型桥接规范

```c
/* [SC] 共享头文件必须使用三路桥接 */
#ifdef __KERNEL__
  #include <linux/types.h>          /* 内核态：从内核源码树 */
#elif defined(__linux__)
  #include <linux/types.h>          /* Linux 用户态：从系统头文件 */
#else
  #include <stdint.h>               /* 非 Linux：C11 标准类型 */
  typedef uint8_t  __u8;
  typedef uint16_t __u16;
  typedef uint32_t __u32;
  typedef uint64_t __u64;
  typedef int8_t   __s8;
  typedef int16_t  __s16;
  typedef int32_t  __s32;
  typedef int64_t  __s64;
#endif
```

#### 5.5.2 OS-IRON-016 强制执行

**OS-IRON-016 已定义**：`include/uapi/airymax/` 下头文件必须坚持 C11 标准，禁止编译器扩展。

**新增 CI 强制校验脚本** `scripts/check-uapi-compiler-agnostic.sh`：
```bash
#!/bin/bash
# 扫描 include/uapi/airymax/ 下所有 .h 文件
# 禁止出现：__attribute__、__builtin_*、__asm__、typeof
```

---

## 6. agentrt 与 agent-linux 一致性规范

### 6.1 项目定位与边界（再次明确）

| 维度 | agentrt | agent-linux |
|------|---------|-----------|
| **定位** | AI Agent 运行时平台工程 | 智能体操作系统（AirymaxOS） |
| **形态** | 用户态运行时（库 + 守护进程） | 操作系统发行版 |
| **平台** | Linux / macOS / Windows（跨平台） | 仅 Linux 6.6 内核基线 |
| **代码性质** | 用户态库 + 守护进程 | Linux 内核 + 用户态服务 |
| **关系** | 可独立运行 | agent-linux 是 agentrt 的最佳载体 |
| **共享** | [SC] 契约层代码共享 + 实现独立 | [SC] 契约层代码共享 + 实现独立 |

### 6.2 工程标准统一清单

| 标准维度 | agentrt 现状 | agent-linux 标准 | 统一方向 |
|---------|-------------|------------------|---------|
| **函数前缀** | airy_* + heapstore_* + memoryrovol_* 等多前缀 | airy_* 唯一 | Phase 2 收敛 |
| **错误码** | AIRY_E* + AIRY_ERR_* 双轨 | AIRY_E* 唯一 | Phase 2 收敛 |
| **日志宏** | LOG_* + AIRY_LOG_* 双轨 | LOG_* 唯一 | Phase 2 收敛 |
| **C 标准** | C11 | C11 + Linux 内核扩展（仅 .c） | 已统一 |
| **编译器扩展** | 部分使用 | [SC] 头文件禁止（OS-IRON-016） | Phase 0 修复 |
| **CI/CD** | CMake + ctest | Kbuild + KUnit + kselftest | 各自独立 |
| **[SC] 头文件宿主** | commons/include/airymax/ | kernel/include/airymax/（待创建） | Phase 0 创建 |
| **构建产物** | .a / .so | .ko / RPM | 各自独立 |

### 6.3 交互接口契约

#### 6.3.1 共享契约层（[SC]）

agentrt 和 agent-linux 通过以下 8+1 个 [SC] 头文件共享契约：

| [SC] 文件 | 物理宿主 | 引用方式 | 状态 |
|-----------|---------|---------|------|
| ipc.h | agent-linux/kernel/include/airymax/ | agentrt: `-I../agent-linux/kernel/include` | 待创建 |
| sched.h | 同上 | 同上 | 待创建 |
| memory_types.h | 同上 | 同上 | 待创建 |
| security_types.h | 同上 | 同上 | 待创建 |
| cognition_types.h | 同上 | 同上 | 待创建 |
| syscalls.h | 同上 | 同上 | 待创建 |
| bpf_struct_ops.h | 同上 | 同上 | 待创建 |
| uapi_compat.h | 同上 | 同上 | 待创建 |
| **error.h**（新增） | 同上 | 同上 | 待创建 |
| **log_types.h**（新增） | 同上 | 同上 | 待创建 |

#### 6.3.2 语义同源层（[SS]）

| API 类别 | agentrt 实现 | agent-linux 实现 | 语义契约 |
|---------|-------------|-------------------|---------|
| log_write() | vsnprintf + fwrite | prb_reserve + commit | 同签名，同语义 |
| airy_err_t | 返回 AIRY_E* | 返回 AIRY_E* | 同类型，同值域 |
| IPC send/recv | commons IPC | io_uring + fastpath | 128B 消息头同源 |
| Agent 状态 | 状态机 | kthread + systemd | 8 态同源 |

---

## 7. 实施计划

### 7.1 Phase 0：奠基修复（5 个工作日）

**目标**：从 0 行代码到 1 个可编译可验证的内核模块。

| 天 | 工作项 | 交付物 | 关联缺陷 |
|----|--------|--------|---------|
| D1 | 创建 agent-linux/kernel/include/airymax/ 目录 | 空目录 + .gitkeep | VAC-002 |
| D1 | 创建 [SC] error.h（基于 5 模块设计） | error.h（~200 行） | SC-001 |
| D1 | 创建 [SC] log_types.h（基于 Ring Buffer 设计） | log_types.h（~150 行） | SC-002 |
| D2 | 复制 7 个现有 [SC] 头文件到 agent-linux 端 | 7 个 .h 文件 | VAC-002 |
| D2 | 修复 uapi_compat.h 三路桥接 | uapi_compat.h 更新 | SC-003 |
| D3 | 创建 kernel/airy_core.c（最小内核模块） | airy_core.c（~50 行） | VAC-001/006 |
| D3 | 创建 kernel/Makefile + kernel/Kconfig | Makefile + Kconfig | VAC-003/004 |
| D4 | 修复 ci-kernel.yml 验证 `make modules` + `insmod` | CI 可运行 | VAC-005 |
| D4 | 修复 sc-dual-ci.yml 验证两端 [SC] 头文件一致性 | CI 可运行 | SC-004 |
| D5 | 在每个 [SC] 头文件底部增加 `#ifdef AIRY_SC_FALLBACK` 降级块 | 10 个 .h 更新 | DSL-001/002 |
| D5 | 端到端验证：`make modules` + `insmod airy_core.ko` + `rmmod` | 验证报告 | 全部 |

**Phase 0 验收标准**：
- ✅ `agent-linux/kernel/airy_core.ko` 可成功 insmod
- ✅ `sc-dual-ci.yml` 双向 CI 全绿
- ✅ 10 个 [SC] 头文件两端逐字节相同
- ✅ 每个头文件含 `#ifdef AIRY_SC_FALLBACK` 降级块

### 7.2 Phase 1：方案文档化（12 个工作日）

**目标**：将 20 份缺失设计文档 + 4 份升级文档全部完成，docs/AirymaxOS 完整度 ≥ 95%。

| 天 | 工作项 | 交付文档 | 优先级 |
|----|--------|---------|--------|
| D1~D2 | 撰写 Airymax Unify Design 总纲 | DOC-N01 | P0 |
| D2~D3 | 撰写 [DSL] 降级生存层设计 | DOC-N02 | P0 |
| D3~D4 | 撰写 [SC] error.h 契约 | DOC-N03 | P0 |
| D4~D5 | 撰写 [SC] log_types.h 契约 | DOC-N04 | P0 |
| D5~D6 | 撰写 Ring Buffer 共享日志设计 | DOC-N06 | P0 |
| D6 | 撰写 [SC] sched.h 扩展方案 | DOC-N05 | P1 |
| D7 | 撰写 Logger Daemon 进程架构 | DOC-N07 | P1 |
| D7 | 撰写 Panic 生存路径设计 | DOC-N08 | P1 |
| D8 | 撰写 IPC 数据面自治设计 | DOC-N09 | P1 |
| D8 | 撰写 IPC 控制面恢复 Reconciliation | DOC-N10 | P1 |
| D9 | 撰写内核态 Agent 生命周期 Supervisor | DOC-N11 | P1 |
| D9 | 撰写用户态 Supervisor Daemon | DOC-N12 | P1 |
| D10 | 撰写统一配置管理 [SS] 语义同源 | DOC-N13 | P1 |
| D10 | 撰写 Logger Daemon 模块设计 | DOC-N14 | P2 |
| D10 | 撰写 printk → airy_klog_write 转换层 | DOC-N15 | P2 |
| D11 | 撰写 [SC] 头文件类型桥接规范 | DOC-N16 | P1 |
| D11 | 升级 03-microkernel-strategy.md v0.1.1 → v1.0+ | DOC-U01 | P1 |
| D11 | 升级 07-ipc-fastpath.md v0.2.8 → v1.0+ | DOC-U02 | P1 |
| D12 | 升级 03-capability-model.md v0.1.1 → v1.0+ | DOC-U03 | P1 |
| D12 | 升级 06-iron9-shared-model.md（新增 [DSL] 层）v0.1.0 → v1.0+ | DOC-U04 | P1 |

**Phase 1 验收标准**：
- ✅ 20 份新增文档全部完成并审核通过
- ✅ 4 份现有文档升级至 v1.0+ 工程级
- ✅ docs/AirymaxOS 完整度 ≥ 95%
- ✅ SSoT 三层一致性 CI 全绿

### 7.3 Phase 2：agentrt 技术债修复（6 个工作日）

**目标**：agentrt 全仓库实现日志、错误码、函数前缀的单一 SSoT。

| 天 | 工作项 | 影响 | 关联 BAN/ERR/LOG |
|----|--------|------|-----------------|
| D1 | 删除 heapstore/include/heapstore_log.h，替换为 logging_compat.h | heapstore 模块 | BAN-294 |
| D1 | 修复 svc_logger.h 补充 `#include "logging_compat.h"` | svc_logger 模块 | BAN-305 |
| D2 | 修复 memory.c 11 处 fprintf(stderr) → LOG_ERROR | memory 模块 | BAN-299 |
| D2 | 撰写 agentrt 日志收敛计划 | docs/AirymaxRT/50-engineering-standards/11-log-convergence-plan.md | DOC-N17 |
| D3 | 撰写 AIRY_ERR_* → AIRY_E* 错误码迁移计划 | docs/AirymaxRT/50-engineering-standards/12-error-code-migration-plan.md | DOC-N18 |
| D3 | 决策 LOG_* vs AIRY_LOG_* 唯一 SSoT（LOG_*） | 决策记录 | LOG-001 |
| D4 | 68 文件迁移：AIRY_LOG_* → LOG_*（自动化脚本） | 68 文件 | LOG-001 |
| D4 | 删除 logging_compat.h | 1 文件 | LOG-001 |
| D5 | 决策 AIRY_E* vs AIRY_ERR_* 唯一 SSoT（AIRY_E*） | 决策记录 | ERR-001 |
| D5 | 全仓库迁移：AIRY_ERR_* → AIRY_E*（自动化脚本） | ~90 处 | ERR-001 |
| D6 | 函数前缀收敛：heapstore_* → airy_heapstore_* 等 | 全仓库 | 函数命名 |
| D6 | LOG-21~26 标记为废弃或实现 | logging 模块 | LOG-002 |

**Phase 2 验收标准**：
- ✅ agentrt 全仓库仅使用 LOG_* 日志宏
- ✅ agentrt 全仓库仅使用 AIRY_E* 错误码
- ✅ agentrt 全仓库函数前缀统一为 airy_*
- ✅ logging_compat.h 已删除
- ✅ BAN-294/299/305 全部修复

### 7.4 Phase 3：开发启动前置（5 个工作日）

**目标**：Airymax Unify Design 完整集成 + [DSL] 层落地 + 双向 CI 全绿。

| 天 | 工作项 | 交付物 |
|----|--------|--------|
| D1 | 验证 5 模块工程可行性 | 5 模块可行性报告 |
| D2 | 验证 [DSL] 层落地完整性 | [DSL] 验证报告 |
| D3 | 验证 sc-dual-ci 双向 CI 全绿 | CI 报告 |
| D4 | 验证 ssot-validate CI 全绿 | SSoT 一致性报告 |
| D5 | 提交"开发启动就绪评估报告" | 评估报告 |

**Phase 3 验收标准**：
- ✅ 5 模块工程可行性达标
- ✅ [DSL] 层 5 个降级块全部设计完成
- ✅ sc-dual-ci 双向 CI 全绿
- ✅ ssot-validate CI 全绿
- ✅ "开发启动就绪评估报告"通过评审

### 7.5 总工期与里程碑

| 阶段 | 工期 | 起始 | 结束 | 里程碑 |
|------|------|------|------|--------|
| Phase 0 | 5 天 | D1 | D5 | M0.1：首个内核模块可编译 |
| Phase 1 | 12 天 | D6 | D17 | M0.2：文档体系完整 |
| Phase 2 | 6 天 | D18 | D23 | M0.3：agentrt 技术债清零 |
| Phase 3 | 5 天 | D24 | D28 | M0.4：开发启动就绪 |
| **总计** | **28 天** | | | |

---

## 8. 验收标准与就绪评估

### 8.1 开发启动就绪评估矩阵

| 维度 | 验收标准 | 当前状态 | 目标状态 | 阶段 |
|------|---------|---------|---------|------|
| 代码基础 | kernel/airy_core.ko 可 insmod | ❌ | ✅ | Phase 0 |
| [SC] 头文件 | 10 个头文件两端存在 + CI 验证 | ❌ | ✅ | Phase 0 |
| 设计文档 | docs/AirymaxOS 完整度 ≥ 95% | 85% | ≥ 95% | Phase 1 |
| agentrt 技术债 | BAN-294/299/305 修复 + 双轨制收敛 | ❌ | ✅ | Phase 2 |
| Airymax Unify Design | 5 模块工程可行性达标 | ❌ | ✅ | Phase 3 |
| [DSL] 降级生存层 | 5 个降级块设计完成 | ❌ | ✅ | Phase 0+1 |
| SSoT 一致性 | 三层 SSoT CI 全绿 | ⚠️ 部分 | ✅ | Phase 0+1 |
| 函数命名统一 | airy_* 全项目唯一前缀 | ❌ | ✅ | Phase 2 |
| 日志系统统一 | LOG_* 唯一 + log_types.h 存在 | ❌ | ✅ | Phase 0+2 |
| 错误码统一 | AIRY_E* 唯一 + error.h 存在 | ❌ | ✅ | Phase 0+2 |
| 微内核化风险 | 9 个风险点全部有缓解方案 | ❌ | ✅ | Phase 1 |
| CI/CD | 6 个 workflow 全部可运行 | ⚠️ 部分 | ✅ | Phase 0+3 |

### 8.2 阻塞项清单（必须全部解决才能启动开发）

**P0 阻塞项（22 项）**：
- VAC-001/002/003/004/006（5 项代码真空）
- SC-001/002/003/004（4 项 [SC] 头文件）
- BAN-294（1 项 agentrt 技术债）
- ERR-001/D01/D02/D03（4 项错误码）
- LOG-001（1 项日志管线）
- DOC-N01/N02/N03/N04/N06（5 项 P0 文档）
- DSL-001/002/005（3 项生存层）

**P1 阻塞项（17 项）**：
- VAC-005、SC-005/006、BAN-299/305、LOG-002、DOC-N05/N07~N18（13 项）、DOC-U01~U04（4 项升级）、DSL-003/004

**P2 优化项（5 项）**：
- LOG-002 高级功能、DOC-N14/N15、NEW-MKR-002、NEW-MKR-003

### 8.3 就绪评估流程

```
Phase 0 完成 → M0.1 评估 → 通过 → 进入 Phase 1
       ↓ 不通过
     返回修复

Phase 1 完成 → M0.2 评估 → 通过 → 进入 Phase 2
       ↓ 不通过
     返回修复

Phase 2 完成 → M0.3 评估 → 通过 → 进入 Phase 3
       ↓ 不通过
     返回修复

Phase 3 完成 → M0.4 评估 → 通过 → 启动 1.0.1 全面开发
       ↓ 不通过
     返回修复
```

---

## 9. 附录

### 9.1 关键决策记录

| 决策 ID | 决策内容 | 决策日期 | 依据 |
|---------|---------|---------|------|
| DEC-001 | [DSL] 层作为 IRON-9 v3 第四层加入 | 2026-07-16 | 05-survival-layer-design.md |
| DEC-002 | LOG_* 为日志系统唯一 SSoT | 2026-07-16 | 5.2.1 节 |
| DEC-003 | AIRY_E* 为错误码唯一 SSoT | 2026-07-16 | 5.4.1 节 |
| DEC-004 | airy_* 为函数命名唯一前缀 | 2026-07-16 | 5.3.1 节 |
| DEC-005 | Phase 0~3 总工期 28 天 | 2026-07-16 | 7.5 节 |
| DEC-006 | Rust 仅用于叶子驱动（[IND] 层） | 2026-07-16 | 3.1.4 节 |
| DEC-007 | 5 模块工程可行性达标作为开发启动前置 | 2026-07-16 | 8.1 节 |

### 9.2 文档引用清单

本报告引用的审查报告：
- [00-comprehensive-analysis-v2.2.md](00-comprehensive-analysis-v2.2.md)
- [01-code-vacuum-report.md](01-code-vacuum-report.md)
- [02-sc-shared-headers-audit.md](02-sc-shared-headers-audit.md)
- [03-five-unify-modules-gap-report.md](03-five-unify-modules-gap-report.md)
- [04-missing-design-docs.md](04-missing-design-docs.md)
- [05-survival-layer-design.md](05-survival-layer-design.md)
- [06-ipc-data-plane-autonomy-report.md](06-ipc-data-plane-autonomy-report.md)

本报告引用的工程标准文档：
- `docs/AirymaxOS/50-engineering-standards/09-ssot-registry.md`（SSoT 权威源）
- `docs/AirymaxOS/50-engineering-standards/04-engineering-philosophy.md`（16 条 OS-IRON 铁律）
- `docs/AirymaxOS/50-engineering-standards/00-engineering-standards-handbook.md`（工程标准手册）
- `agent-linux/ssot-registry.yaml`（SSoT 机器可读源）

### 9.3 实施计划文件清单

需要在 Phase 0~3 期间创建/修改的文件：

**Phase 0（10 个文件）**：
- agent-linux/kernel/include/airymax/error.h（新建）
- agent-linux/kernel/include/airymax/log_types.h（新建）
- agent-linux/kernel/include/airymax/ipc.h（新建，从 agentrt 复制）
- agent-linux/kernel/include/airymax/sched.h（新建，从 agentrt 复制 + 扩展）
- agent-linux/kernel/include/airymax/memory_types.h（新建，从 agentrt 复制）
- agent-linux/kernel/include/airymax/security_types.h（新建，从 agentrt 复制）
- agent-linux/kernel/include/airymax/cognition_types.h（新建，从 agentrt 复制）
- agent-linux/kernel/include/airymax/syscalls.h（新建，从 agentrt 复制）
- agent-linux/kernel/include/airymax/bpf_struct_ops.h（新建，从 agentrt 复制）
- agent-linux/kernel/include/airymax/uapi_compat.h（新建，从 agentrt 复制 + 修复三路桥接）
- agent-linux/kernel/airy_core.c（新建）
- agent-linux/kernel/Makefile（新建）
- agent-linux/kernel/Kconfig（新建）

**Phase 1（20 个文档）**：
- 见 1.2.4 节 DOC-N01~N18 + DOC-U01~U04

**Phase 2（修改 N 个文件）**：
- agentrt 全仓库 .c/.h 文件（68 + ~90 处修改）

**Phase 3（验证报告）**：
- 5 模块可行性报告
- [DSL] 验证报告
- CI 双向验证报告
- SSoT 一致性报告
- 开发启动就绪评估报告

---

## 10. 结论

agent-linux 方案的**设计层**是完整且自洽的（128 个 .md 文档覆盖了操作系统设计的方方面面），但存在**设计→工程的系统性断层**。_review_v2.2 揭示的 5 大缺陷经实地复核全部确认。

本报告提出的 **4 阶段 28 天改进路径** 以"先奠基、再文档化、再修复技术债、最后启动开发"为原则，严格遵守 IRON-1~5 工程铁律，不引入新特性、不创建桩文件、不绕开功能限制、不简化功能、不设计未实现的功能。

**核心建议**：

1. **立即启动 Phase 0**：从 0 行代码到 1 个可 insmod 的内核模块，这是从文档体系到工程体系的第一个质变点
2. **Phase 1 必须在 Phase 0 之后**：文档化需要基于真实的 [SC] 头文件和内核模块，而非空中楼阁
3. **Phase 2 必须在 Phase 1 之后**：agentrt 技术债修复需要明确的迁移计划（DOC-N17/N18）作为指导
4. **Phase 3 必须在 Phase 2 之后**：5 模块工程可行性达标依赖于 agentrt 技术债清零
5. **1.0.1 全面开发启动的前置条件**：Phase 0~3 全部完成，M0.4 评估通过

**最终判定**：在本报告所述 4 阶段改进全部完成前，agent-linux 不具备启动 1.0.1 全面开发的条件。建议按本计划严格推进，预计 28 个工作日后达到开发就绪状态。

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. Internal Review Document.
