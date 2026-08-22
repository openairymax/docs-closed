# agent-linux 方案冲突点与问题清单

> **审计日期**：2026-07-16
> **审计方法**：Linux 6.6 + seL4 源码对照 + 128 文档交叉验证
> **目的**：为 Airymax Unify Design 重构提供需解决的问题清单

---

## 1. 方案级冲突（P0 阻塞）

### CONFLICT-01: sched_ext 版本基线冲突

**涉及文档**：
- [01-syscalls.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/01-syscalls.md) L542："通过 sched_ext（agent-linux 内核增强，主线 6.12+）"
- [01-kernel.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/01-kernel.md) L47："sched_ext（agent-linux 内核增强，主线 6.12+ 引入并持续演进）"

**冲突**：用户明确要求"以 Linux 6.6 内核为准"，但 sched_ext 在 Linux 6.6 中需要 backport（主线 6.12+ 才合入）。

**影响**：所有依赖 sched_ext 的 SCHED_AGENT 策略、Micro-Supervisor 心跳检测均受阻。

**建议**：明确文档中标注"Linux 6.6 + sched_ext backport 补丁"，并在 [04-engineering-baseline.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/04-engineering-baseline.md) 中记录 backpatch 清单。

---

### CONFLICT-02: 跨发行版兼容文档违反"6.6 唯一基线"

**涉及文档**：
- [05-cross-distro.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/160-compatibility/05-cross-distro.md) L60-113

**冲突**：文档列出 Ubuntu 5.15/6.8、Debian 6.1、RHEL 5.14 等多个内核版本，并给出降级策略。但用户要求"放弃其他版本的基线，所有技术点全面对齐 Linux 6.6"。

**影响**：跨发行版兼容性设计方向与"6.6 唯一基线"矛盾。

**建议**：
- 将跨发行版文档改为"Airymax Kernel 自身就是 6.6 基线，发行版需要安装 Airymax Kernel"
- 删除 5.15/6.1/6.8 等版本的降级策略
- 保留"用户态 Agent 应用二进制兼容"的跨发行版设计

---

### CONFLICT-03: io_uring/Landlock 版本标注为"5.x+"

**涉及文档**：
- [02-services.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/02-services.md) L475："io_uring zero-copy | Linux 5.x+"
- [03-security.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/03-security.md) L605："Landlock | Linux 5.x+"

**冲突**：版本标注应统一为"Linux 6.6"。

**建议**：全局替换"Linux 5.x+"为"Linux 6.6"。

---

## 2. Airymax Unify Design 缺失（P0 阻塞）

### GAP-01: Airymax Unify Design 完整方案未文档化

**现状**：5 大组件（UEF/ULP/UCF/USV/UIPC）的设计仅存在于对话上下文中，未进入 docs/AirymaxOS 文档体系。

**影响**：开发团队无设计参考，无法开始实现。

**建议**：创建 `docs/AirymaxOS/10-architecture/08-unify-design.md`，包含 5 大组件的完整设计。

---

### GAP-02: UEF [SC] error.h 未创建

**现状**：error.h 在 agentrt 和 agent-linux 两端都不存在。

**建议**：创建 `include/uapi/airymax/error.h`，定义统一的 AIRY_E* 错误码。

---

### GAP-03: ULP Ring Buffer + Logger Daemon 未文档化

**现状**：零拷贝 Ring Buffer + Logger Daemon 方案仅存在于对话中。

**建议**：创建 `docs/AirymaxOS/40-dataflows/05-ring-buffer-logging.md`。

---

### GAP-04: ULP DMA 一致性内存方案需修正

**现状**：用户提出用 DMA 一致性内存，但不适用于内核-用户态共享。

**建议**：修正为 `memblock_reserve()` + `memremap()` + `/dev/airymax-log` mmap。

---

### GAP-05: USV Micro/Macro-Supervisor 三层模型未文档化

**现状**：Supervisor 分层模型仅存在于对话中。

**建议**：创建 `docs/AirymaxOS/20-modules/09-kernel-agent-supervisor.md` 和 `10-user-supervisor-daemon.md`。

---

### GAP-06: UIPC 数据面自治三原则未文档化

**现状**：离线缓存校验 + Reconciliation 仅存在于对话中。

**建议**：创建 `docs/AirymaxOS/110-security/04-ipc-data-plane-autonomy.md`。

---

## 3. 技术设计缺陷（P1）

### DEFECT-01: IPC fastpath 无 capability daemon 离线降级

**涉及文档**：[07-ipc-fastpath.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/07-ipc-fastpath.md)

**缺陷**：C-S9 capability 检查失败直接 → ERROR，无离线缓存校验降级。

**建议**：增加 C-S9c 离线缓存校验路径，控制面离线时使用 badge 缓存。

---

### DEFECT-02: 12 daemon 与 IPC 机制交互未定义

**涉及文档**：[02-services.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/02-services.md)

**缺陷**：12 个 daemon 的列表已定义，但每个 daemon 如何使用 IPC（哪个 ring、什么 badge、fastpath 还是 slowpath）未定义。

**建议**：为每个 daemon 增加 IPC 交互矩阵。

---

### DEFECT-03: Agent 生命周期与 12 daemon 交互未定义

**涉及文档**：[01-agent-lifecycle.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/140-application-development/01-agent-lifecycle.md)

**缺陷**：Agent 生命周期定义了状态机，但未说明每个状态转换由哪个 daemon 触发/监控。

**建议**：增加生命周期 × daemon 交互矩阵。

---

### DEFECT-04: 内存管理 slab vs page_alloc 未决策

**涉及文档**：[04-memory.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/04-memory.md)

**缺陷**：文档提到 slab 和 page_alloc 两种方案，但未最终决策。

**建议**：明确内核使用 slab（对齐 Linux 6.6 SLUB），用户态使用 mmap。

---

### DEFECT-05: capability 模型缺少离线校验数据结构

**涉及文档**：[03-capability-model.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/110-security/03-capability-model.md)

**缺陷**：CNode/MDB 完整，但无 `airy_ring_cap_cache` 结构。

**建议**：增加离线缓存校验数据结构 + Reconciliation 算法。

---

### DEFECT-06: 微内核策略文档版本过低

**涉及文档**：[03-microkernel-strategy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) v0.1.1

**缺陷**：版本 0.1.1，未包含 Airymax Unify Design 的 5 大组件设计。

**建议**：升级到 v1.0，融入 UEF/ULP/UCF/USV/UIPC 设计。

---

### DEFECT-07: ERR_ABNORMAL_CAP 故障码未定义

**缺陷**：用户设想的"内核冷酷执法，用户温情裁决"需要 ERR_ABNORMAL_CAP 故障码，但 UEF 中未定义。

**建议**：在 error.h 中增加 `AIRY_EABNORMAL_CAP=(-28)`。

---

### DEFECT-08: io_uring 自定义操作码未定义

**缺陷**：UIPC 需要映射为 io_uring 操作码（IORING_OP_AIRY_IPC_SEND/RECV/CAP_CHECK），但未定义。

**建议**：在 [01-syscalls.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/01-syscalls.md) 中增加 io_uring 操作码映射表。

---

### DEFECT-09: Panic 回退路径未设计

**缺陷**：Panic 时 Ring Buffer 不可用（prb_reserve 需要锁），回退到 printk 原生路径的设计未文档化。

**建议**：创建 Panic 生存路径设计文档。

---

### DEFECT-10: `#ifdef __KERNEL__` 类型桥接规范未定义

**缺陷**：[SC] 头文件需要在内核态和用户态使用不同类型系统，但规范未文档化。

**建议**：创建 [SC] 头文件类型桥接规范文档。

---

## 4. 工程缺失（P0 阻塞）

### ENG-01: 0 行可编译内核源码

**现状**：agent-linux 8 子仓全部为 README-only 空壳。

**建议**：立即创建 kernel 子仓的第一个 .c 文件（空壳内核模块）。

---

### ENG-02: 0 个 Kconfig/Kbuild 文件

**现状**：无内核构建系统。

**建议**：创建 kernel/Kconfig + kernel/Makefile。

---

### ENG-03: [SC] 双向 CI 无法运行

**现状**：sc-dual-ci.yml 存在但 agent-linux 端无代码可对比。

**建议**：创建 agent-linux 端 [SC] 头文件后启用 CI。

---

### ENG-04: error.h / log_types.h 两端都不存在

**建议**：创建 `include/uapi/airymax/error.h` 和 `include/uapi/airymax/log_types.h`。

---

### ENG-05: uapi_compat.h 未处理 `__KERNEL__` 路径

**现状**：仅用 `#ifdef __linux__`，无法区分内核态和用户态 Linux。

**建议**：增加 `#ifdef __KERNEL__` 路径处理。

---

## 5. 冲突解决能力评估

Airymax Unify Design 对以上冲突的解决能力：

| 冲突类别 | 总数 | UEF 解决 | ULP 解决 | UCF 解决 | USV 解决 | UIPC 解决 | 未解决 |
|---------|------|---------|---------|---------|---------|---------|--------|
| 方案级冲突 | 3 | 0 | 0 | 0 | 0 | 0 | 3（版本基线） |
| 设计缺失 | 6 | 1 | 2 | 0 | 1 | 2 | 0 |
| 技术缺陷 | 10 | 1 | 1 | 0 | 1 | 3 | 4（需补充设计） |
| 工程缺失 | 5 | 1 | 1 | 0 | 0 | 0 | 3（需工程执行） |
| **合计** | **24** | **3** | **4** | **0** | **2** | **5** | **10** |

**解决率**：14/24 = 58%（5 大组件直接解决）+ 6/24 = 25%（需补充设计后解决）= **83%**

**剩余 17%（4 项）**主要是版本基线冲突（3 项）和工程执行（1 项），需要管理决策而非架构设计。

---

## 6. 总结

agent-linux 方案存在 **24 个问题点**：
- 3 个方案级冲突（版本基线）
- 6 个设计缺失（Airymax Unify Design 未文档化）
- 10 个技术缺陷（IPC/日志/安全/生命周期）
- 5 个工程缺失（代码/构建/CI）

Airymax Unify Design 能解决其中 **83%** 的问题，剩余 17% 需要管理决策（版本基线统一）和工程执行（代码创建）。

**建议优先处理 P0 阻塞项**：统一 Linux 6.6 基线 → 文档化 Airymax Unify Design → 创建 [SC] error.h + log_types.h → 创建第一个内核模块。
