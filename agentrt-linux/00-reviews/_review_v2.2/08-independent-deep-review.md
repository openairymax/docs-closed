# 08 — agentrt-linux 独立深度审查报告 v1.0

> **审查日期**：2026-07-16
> **审查性质**：独立一手审查（基于方案文档直接阅读，非二手转述）
> **审查范围**：docs/AirymaxOS 全部 128+ 份 .md 文档 + agentrt 实际代码对照
> **审查方法论**：6 个维度独立评分 → 跨层交叉验证 → agentrt 代码对照 → 综合判定

---

## 0. 执行摘要

### 0.1 核心判定

**agentrt-linux 项目在设计层的完成度约为 60-70%，在工程层的完成度约为 5%。当前状态不具备启动 1.0.1 全面开发的条件。**

这个判定并非基于第三方审查报告，而是基于对以下全部文档的一手阅读和代码对照：

- **10-architecture**：7 份可用文档（9 份目录中 3 份缺失：03-capability-model.md、06-iron9-shared-model.md、07-ipc-fastpath.md）
- **20-modules**：9 份全部可用
- **30-interfaces**：3 份可用文档（8 份目录中 5 份缺失或仅占位）
- **40-dataflows**：5 份全部可用
- **50-engineering-standards**：9 份核心 + 5 个子目录
- **70-build-system**：5 份全部可用（含 04-kbuild-integration.md、05-boot-process.md）
- **110-security**：4 份全部可用
- **90-observability**：3 份全部可用
- **100-operations**：3 份全部可用
- **130-roadmap**：6 份全部可用
- **agentrt 代码对照**：commons/include/airymax/ 8 个头文件 + 日志/错误码系统

### 0.2 最关键发现（5 条，全部为独立发现）

1. **io_uring 跨进程 page flipping 不可行**：services.md 声称"内核仅翻转 page table entry，不拷贝数据"用于 IPC 零拷贝。这是整个 IPC 数据面的基石假设，但 Linux 6.6 的 io_uring **不支持两个独立进程之间的 page flipping**。现有机制（MSG_ZEROCOPY、FIXED_BUFFER）用于网络/文件 I/O，不是通用 IPC。要支持此功能需开发全新内核机制，这是一个**数月级别的内核工程**。

2. **sched_ext 与 Linux 6.6 基线存在时间线矛盾**：sched_ext 主线合入在 Linux 6.12，而非 6.6。如果将 6.6 锁定为内核基线，SCHED_AGENT 的全部调度能力需要 backport 一个跨越 6 个大版本（6.6→6.12）的调度框架，backport 的工程量和稳定性风险极高。

3. **VFS 用户态化存在根本性架构矛盾**：`01-system-architecture.md` 声称要"VFS/网络栈逐步用户态化"，但 `08-known-caveats.md` 的最终评估结论是"保留内核态"。同时，kernel/services/memory 三个模块都声称对 VFS 有所有权。这是一个**微内核化改造的核心设计矛盾**。

4. **接口层结构性坍塌 60%**：`30-interfaces/` 目录下 8 份文档中，5 份不存在或仅占位。特别是缺少 SCHED_AGENT BPF 接口（05-sched-contract.md）、BPF kfunc 清单（06-bpf-contract.md）、MemoryRovol 操作契约（07-memory-contract.md），而这些正是核心的工程实现接口。

5. **8 份模块设计文档的设计深度极度不均**：kernel（4.1/5）和 security（4.4/5）接近可编码状态，但 cloudnative（2.8/5）和 system（2.4/5）仅到"目录名列表"层面。12 daemons 无任何单独设计，SCHED_AGENT BPF 程序不存在。

---

## 1. 架构层深度审查（10-architecture）

### 1.1 文档存在性

| 编号 | 预期文档 | 实际状态 | 行数 |
|------|---------|---------|------|
| 01 | system-architecture.md | ✅ 存在 | ~600 行 |
| 02 | five-dimensional-principles.md | ✅ 存在 | ~700 行 |
| 03 | microkernel-strategy.md | ✅ 存在 | ~700 行 |
| * | capability-model.md | ❌ 不存在 | — |
| 04 | engineering-baseline.md | ✅ 存在 | ~500 行 |
| 05 | adrs.md | ✅ 存在 | ~800 行 |
| * | iron9-shared-model.md | ❌ 不存在 | — |
| * | ipc-fastpath.md | ❌ 不存在 | — |
| 06 | directory-structure.md | ✅ 存在（重复编号 06） | ~580 行 |
| 07 | threat-model.md | ✅ 存在 | ~400 行 |
| 08 | known-caveats.md | ✅ 存在 | ~300 行 |

**3 份关键文档缺失**，其中 `03-capability-model.md` 和 `07-ipc-fastpath.md` 在 README.md 索引中被列为架构层核心文档。

### 1.2 设计合理性与自洽性

**正面发现**：
- 五维正交 24 原则体系（S/K/C/E/A）设计精良，每项原则有明确的落地映射和验证方式
- seL4 微内核思想的借鉴深度超出预期——`03-microkernel-strategy.md` 中对 seL4 fastpath（`src/fastpath/fastpath.c:168-233`）和 capability（MDB）的源码级引用精确到文件:行号
- ADR-001~014 共 14 个架构决策记录覆盖了关键设计决策点

**关键矛盾**：

1. **VFS 用户态化矛盾**（P0）：
   - `01-system-architecture.md` Lxx 声称"VFS、网络栈、设备驱动等子系统逐步用户态化"
   - `08-known-caveats.md` §9.3 评估结论为"保留内核态"
   - 两份文档是同一架构层的核心文档，结论互斥。一个说要做，一个说风险评估后判定不做。

2. **[SC] 头文件数量不一致**（P1）：
   - 不同文档将 [SC] 头文件数量表述为 6 个、8 个（6+2）等不同数值
   - 实际 agentrt 端存在 8 个（不含 error.h/log_types.h）

3. **性能 SLO 全部是"6.6 基线值"占位**（P1）：
   - `04-engineering-baseline.md` 的 8 维度性能表中，全部指标标注为"6.6 基线值"
   - 作为工程基线文档，这是不可接受的——无法作为编码的验收标准

### 1.3 架构层评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 设计自洽性 | 3.0/5 | VFS 矛盾严重影响核心逻辑 |
| 技术深度 | 3.5/5 | seL4 借鉴有源码证据，但工程实现路径缺失 |
| 风险识别 | 3.0/5 | known-caveats 覆盖了部分，但遗漏了 io_uring 和 sched_ext 的关键风险 |
| 文档完整性 | 2.5/5 | 3/11 核心文档缺失 |
| 一致性 | 2.5/5 | [SC] 数量、VFS 决策、sched_ext 基线等多处不一致 |

---

## 2. 模块设计层深度审查（20-modules）

### 2.1 8 子仓设计深度排名

这是最核心的发现——不同模块的设计成熟度差异巨大，不应该用同样的"v0.2.0"版本号掩盖。

| 排名 | 模块 | 综合分 | 核心优势 | 核心缺陷 |
|------|------|--------|---------|---------|
| 1 | **security** | 4.4/5 | capability 数据结构完整（airy_capability_t/MDB/CNode radix tree）、LSM 252 钩子 + BPF 策略注入详实、Landlock 三系统调用精准、seL4 借鉴有深度 | 无性能指标；策略编译器输出格式缺失 |
| 2 | **kernel** | 4.1/5 | 12 核心 syscall 设计扎实、fastpath POINT OF NO RETURN + vtime 衰减公式有代码级描述、TCB/CTE/CSpace 结构完整 | io_uring 自定义 OP 缺失；SCHED_AGENT BPF 程序全缺；"2 万行补丁"预算疑为增量非修改量 |
| 3 | **memory** | 3.5/5 | MemoryRovol L1-L4 四种记录结构完整（airy_mr_l1_record_t 等）、内存分层模型（CXL/PMEM/MGLRU）清晰 | CXL 3.0 设备可用性未验证；fork+COW 多线程问题未解决；pooling 分配算法缺失 |
| 4 | **cognition** | 3.4/5 | 数据枚举完整（CoreLoopThree 三阶段、Thinkdual 快慢模式、LLM 三阶段）、理论来源丰富 | **全无算法**——8 个子模块没有一个有算法级描述；Wasm 3.0 成熟度/GPU 驱动阶段暴露接口未验证 |
| 5 | **tests-linux** | 3.3/5 | 测试类型 7 项全覆盖、覆盖率目标明确 | 形式化验证目标（capability 不可伪造、IPC 无死锁）严重脱离现实（seL4 耗费 20+ 人年） |
| 6 | **services** | 3.1/5 | systemd unit 示例、12 daemons 名称列表、io_uring IPC 架构清晰 | **12 daemons 无任何单独功能设计**；io_uring 跨进程 page flipping 不可行；VFS 角色矛盾 |
| 7 | **cloudnative** | 2.8/5 | K8s CRD YAML 示例、containerd shim 三模式切换概念 | 超节点功能与 cognition/memory 三方分裂；4 家 DPU/IPU 统一框架不可行 |
| 8 | **system** | 2.4/5 | RPM 仓库配置、sysctl 参数列表 | **全无算法**；DevStation AI 助手安全风险完全未分析（可执行任意系统命令） |

### 2.2 跨模块断裂点

1. **VFS 所有权三方分裂**（P0）：kernel §1 说"用户态化"；services §4.1 说"内核保留 VFS layer"；memory §1 说"VFS 持久化层"。三个模块都声称对 VFS 有所有权。

2. **超节点功能三方交叉**（P1）：cloudnative 负责"超节点 OS"（拓扑/调度/迁移）、cognition 负责"超节点沙箱"（快照/克隆/迁移）、memory 负责"记忆迁移"。三方都能做"迁移"，但迁移什么、何时迁移、谁触发迁移，完全未对齐。

3. **12 daemons 跨越两个模块**（P1）：12 daemons 名义上在 services 中定义，但 gateway_d 的设计在 cloudnative 中。sched_d、llm_d 等其他 daemon 功能与 kernel/cognition 紧密关联但未在任何模块中设计。

---

## 3. 接口层 + 数据流层 + 安全层深度审查

### 3.1 接口层（30-interfaces）— 结构性坍塌 60%

| 文档 | 状态 | 核心发现 |
|------|------|---------|
| 01-interfacing-concept.md | ❌ 不存在 | 接口层总纲缺失 |
| 02-infra-interfaces.md | ❌ 不存在 | 基础设施接口缺失 |
| 03-syscalls-contract.md | ⚠️ 实际文件为 05-syscall-semantic-mapping.md | syscall 编号映射存在不一致（#512 旧引用 vs 新定义） |
| 04-ipc-contract.md | ✅ 存在 | 128B 消息头设计质量高，含 6 个 payload 类型。但缺 version/TTL 字段 |
| 05-sched-contract.md | ❌ 不存在 | **SCHED_AGENT BPF 接口完全无定义** |
| 06-bpf-contract.md | ❌ 不存在 | **BPF kfunc 清单不存在** |
| 07-memory-contract.md | ❌ 不存在 | MemoryRovol 操作契约缺失 |

**结论**：接口层仅 128B IPC 消息头设计可称"工程级"。其余全部缺失。

### 3.2 数据流层（40-dataflows）— 覆盖率 60%

| 文档 | 核心发现 |
|------|---------|
| 01-data-flows-overview.md | Agent IPC 流 + kernel IPC 流 + 日志 IPC 流三层划分合理 |
| 02-agent-ipc-flow.md | 覆盖了正常路径和 fastpath，但**降级路径（io_uring 不可用时的 fallback）全缺** |
| 03-kernel-ipc-flow.md | io_uring 数据流描述清晰，但多核竞争下的内存一致性未考虑 |
| 04-ipc-logging.md | Ring Buffer 设计有基本结构但锁策略缺失 |

**缺失的数据流**：cloudnative/system/tests-linux 三个子仓的数据流完全未覆盖。IPC 日志流的 panic 路径缺失。

### 3.3 安全层（110-security）— 完成度 44%

现有 4 份文档（authz / security-scan / security-baseline / README），但平均内容深度约 200 行/份，远低于模块设计层的 500+ 行/份。缺失的关键安全子领域包括：输入验证策略、安全审计日志、安全事件响应、密钥管理生命周期。

---

## 4. 工程标准层深度审查（50-engineering-standards）

### 4.1 SSoT 注册表（09-ssot-registry.md）

**正面发现**：
- OS-IRON 16 条铁律 + OS-KER/OS-STD/OS-SEC/OS-TEST/OS-MISC 规则编号体系完整
- 规则均有交叉引用（指向 SSoT 文档章节）和执行机制描述

**缺陷发现**：
1. 规则编号的交叉引用路径与某些引用文档的路径不一致（已验证修复）
2. 缺少 agentrt 侧规则编号（DOC-N17/N18 应补充）
3. 执行机制描述偏概念化——例如"CI 中 scripts/check-uapi-compiler-agnostic.sh"引用了一个不存在的脚本

### 4.2 编码规范（10-coding-style/C_Cpp_coding_style.md）

该文档约 163KB，是 docs/AirymaxOS 下最大的单文件。但内容极长且非结构化——每条规范标注了 Linux 6.6 源码出处（文件名:行号），这个做法很好，但：
- 规范条目过多（估计 500+ 条），无优先级分级
- 缺少 CI 可自动化检查的规范子集标记
- 缺少 agentrt 端编码规范的对照表

### 4.3 工程哲学（04-engineering-philosophy.md）

16 条 OS-IRON 铁律都有哲学阐述，但：
- IRON-008~016（[SC] 共享契约层、代码共享边界等）的阐述集中于 §0.3 的简略声明，缺乏与 IRON-001~007 同等深度的哲学分析
- "附录 A：OS-IRON 规则索引表"是创新性的 SSoT 一致性辅助工具，但需要确保与 09-ssot-registry.md 的自动同步机制

---

## 5. 构建系统 + CI/CD + 路线图深度审查

### 5.1 构建系统（70-build-system）

**正面发现**：
- 04-kbuild-integration.md（v0.2.0）存在——这与之前第三方审查声称"缺失"不同，实际文件存在
- Kbuild 集成方案使用了 `select` 和 `depends on` 的标准 Kconfig 语法
- 内核构建方案覆盖了 defconfig/allnoconfig/allmodconfig 三配置

**缺陷发现**：
1. 8 个子仓的独立构建方案缺失——仅 kernel 有完整的 Kbuild 描述，其他 7 个子仓无独立构建方案
2. 联合构建的依赖顺序未定义
3. CI/CD pipeline 文档（03-ci-cd-pipeline.md）中列出的 10 个 workflow 与实际的 6 个 .yml 文件不一致

### 5.2 CI/CD Pipeline 文档与实现对照

| 文档描述 | 实际 workflow | 一致？ |
|---------|--------------|--------|
| 10 workflows, 4+6+3+4+3+6 jobs | 6 workflows × 2 jobs | ❌ 已更新，但 03-ci-cd-pipeline.md 是否同步到 6 workflow 状态待确认 |
| 语言级 CI（ci-cargo/ci-go/ci-meson/ci-tsc） | 已删除 | ✅ |
| release.yml 2 jobs | release.yml 2 jobs | ✅ |
| ci-kernel.yml 2 jobs | ci-kernel.yml 2 jobs | ✅ |

### 5.3 路线图（130-roadmap）

6 份文档覆盖了开发策略、里程碑、资源估算、依赖图、风险缓解、验收标准。

**正面发现**：
- 里程碑 M0-M8 与模块设计的 Part 1-9 对应关系合理
- 关键路径 M0→M1→M2→M6→M7→M8 定义清晰
- 总工期 126 天有各里程碑的工期分解

**缺陷发现**：
1. 路线图的时间线是基于"文档体系完成即可启动编码"的假设，但模块设计层审查表明多数模块尚未到可编码状态
2. 资源估算未考虑 io_uring 新内核机制开发、sched_ext backport 验证等前置工程量
3. 验收标准过于偏向文档产出（"X 份文档完成"），缺少"1 个内核模块可 insmod"等硬性工程标准

---

## 6. agentrt 实际代码与文档对照

### 6.1 agentrt 代码状态（实地核实）

**agentrt 端 [SC] 头文件**（`commons/include/airymax/`）：

| 文件 | 状态 | 与文档一致性 |
|------|------|------------|
| ipc.h | 存在（82 行） | ⚠️ 缺 version/TTL 字段（IPC-D01） |
| sched.h | 存在（79 行） | ⚠️ 缺 3 态降级枚举 |
| memory_types.h | 存在 | ✅ |
| security_types.h | 存在 | ✅ |
| cognition_types.h | 存在 | ✅ |
| syscalls.h | 存在 | ✅ |
| bpf_struct_ops.h | 存在 | ✅ |
| uapi_compat.h | 存在 | ❌ 仅 `#ifdef __linux__` 二路，缺 `__KERNEL__` 路径 |
| **error.h** | **不存在** | ❌ 5 模块统一错误码 SSoT 缺失 |
| **log_types.h** | **不存在** | ❌ 5 模块统一日志类型 SSoT 缺失 |

**agentrt 日志管线**：双轨制并存
- `LOG_*` 宏（logging.h）— 较新
- `AIRY_LOG_*` 宏（logger.h）— 旧版
- `logging_compat.h` 桥接存在，被多个文件引用

**agentrt 错误码系统**：双轨制并存
- `AIRY_E*`（airy_types.h）— POSIX 兼容
- `AIRY_ERR_*`（error.h）— 扩展码
- 值域存在重叠

### 6.2 agentrt-linux 代码状态（实地核实）

**代码真空状态确认**：
- 0 个 .c 文件
- 0 个 Kconfig 文件
- kernel/include/airymax/ **目录不存在**
- 8 个子仓全部为 README-only 空壳

**结论**：agentrt-linux 的代码状态与文档描述之间存在"全或无"断层——文档已覆盖到数据结构定义和算法伪代码层面，但代码端为绝对零。

---

## 7. 跨文档一致性总评

### 7.1 做得好的一致性机制

1. **IRON-9 v2 三层标注**：[SC]/[SS]/[IND] 在全部文档中统一使用
2. **术语统一**："微内核设计思想"、"agentrt-linux 工程基线"、"Airymax 同源性"三大支柱术语跨文档一致
3. **版本号格式统一**：全部文档使用 `v0.x.x` 语义化版本号

### 7.2 关键不一致清单

| # | 不一致点 | 涉及文档 | 严重度 |
|---|---------|---------|--------|
| I1 | VFS 用户态化决策 | 01-system-architecture.md vs 08-known-caveats.md | P0 |
| I2 | [SC] 头文件数量（6 vs 8 vs 10） | 多个文档 | P1 |
| I3 | sched_ext 在 6.6 中的可用性 | 03-microkernel-strategy.md vs 04-engineering-baseline.md | P0 |
| I4 | CI workflow 数量（10 vs 6） | 03-ci-cd-pipeline.md vs 实际 .yml | P1 |
| I5 | 路线图假设（文档完成 vs 可编码） | 130-roadmap vs 20-modules 实际深度 | P1 |
| I6 | 超节点功能所有权 | cloudnative vs cognition vs memory | P1 |
| I7 | 12 daemons 跨模块归属 | services vs cloudnative | P1 |

---

## 8. 技术可行性关键评估

### 8.1 P0 级技术不可行点（必须解决才能启动开发）

1. **io_uring 跨进程 page flipping 不可行**（详见上文）
2. **sched_ext 与 Linux 6.6 基线时间线矛盾**（详见上文）
3. **fork+COW 快照的多线程安全问题**（04-memory.md）— Agent 进程几乎必然多线程，fork 只复制调用线程
4. **seL4 fastpath 同步 IPC 到 io_uring 异步模型的映射未弥合**（01-kernel.md）

### 8.2 P1 级技术可行性疑虑

1. Wasm 3.0 特性（GC/Threads/SIMD）在系统级 runtime 中的成熟度
2. GPU 驱动暴露推理阶段信息给操作系统的可行性
3. CXL 3.0 设备在当前市场（2026-07）的实际可用性
4. 形式化验证目标（capability 不可伪造）与 seL 4 20+ 人年验证成本的现实差距

### 8.3 技术可行性综合评分

| 子系统 | 可行性 | 说明 |
|--------|--------|------|
| capability 安全模型 | ✅ 可行 | seL4 有成熟实现，agentrt-linux 的数据结构设计足够深入 |
| io_uring IPC（当前设计） | ❌ 不可行 | 跨进程 page flipping 需要新内核机制 |
| SCHED_AGENT 调度 | ⚠️ 需验证 | 取决于 sched_ext 在 6.6 中的可用状态 |
| MemoryRovol | ⚠️ 需验证 | fork+COW 多线程安全性需方案级修正 |
| eBPF kfunc | ✅ 可行 | Linux 6.6 原生支持 |
| VFS 用户态化 | ⚠️ 待决策 | 存在文档内矛盾，需先统一决策 |
| Wasm 3.0 runtime | ⚠️ 需验证 | 系统级 Wasm 的成熟度待独立核实 |

---

## 9. 整体质量评估

### 9.1 按层次评估

| 层次 | 文档数 | 平均深度 | 工程就绪度 | 评级 |
|------|--------|---------|-----------|------|
| 架构设计 (10-arch) | 7/11 | 3.0/5 | 40% | C+ |
| 模块设计 (20-modules) | 9/14 | 3.3/5 | 25% | C |
| 接口契约 (30-interfaces) | 3/8 | 4.1/5（仅 IPC） | 15% | D |
| 数据流 (40-dataflows) | 5/8 | 3.0/5 | 30% | C- |
| 工程标准 (50-std) | 9+X | 3.5/5 | 50% | C+ |
| 构建系统 (70-build) | 5/5 | 3.0/5 | 40% | C |
| 安全 (110-sec) | 4/6 | 2.5/5 | 25% | D+ |
| 可观测性 (90-obs) | 3/3 | 3.0/5 | 35% | C |
| 运维 (100-ops) | 3/3 | 2.5/5 | 30% | C- |
| 路线图 (130-roadmap) | 6/6 | 3.5/5 | 50% | C+ |
| 其他 (140/160/180/190) | ~20 | 2.5/5 | 30% | C- |

### 9.2 加权综合评分

| 维度 | 评分 | 权重 | 加权 |
|------|------|------|------|
| 设计完整性 | 60% | 30% | 18% |
| 技术深度 | 35% | 25% | 8.75% |
| 技术可行性 | 40% | 25% | 10% |
| 跨文档一致性 | 50% | 10% | 5% |
| 可实现性（代码对照） | 5% | 10% | 0.5% |
| **加权总分** | | | **42.25%** |

**解读**：方案在设计概念和文档规范层面达到了及格线（60%），但在技术深度和技术可行性层面严重不足（35-40%），在最关键的"可实现性"（代码对照）层面几乎为零（5%）。加权总分 42%，远未达到启动全面开发的标准线（建议 ≥75%）。

---

## 10. 关键阻塞项清单（独立判断）

### P0 阻塞（必须解决 → 8 项）

| # | 阻塞项 | 分类 | 预计工作量 |
|---|--------|------|-----------|
| P0-1 | io_uring 跨进程 page flipping 方案修正 | 技术可行性 | 2-3 周（重新设计方案或改用 shared memory） |
| P0-2 | sched_ext 在 Linux 6.6 中的可用性确认 + backport 评估 | 基线兼容性 | 1-2 周 |
| P0-3 | VFS 用户态化决策统一（做 vs 不做） | 设计矛盾 | 架构评审，无代码工作量 |
| P0-4 | error.h + log_types.h 物理文件创建 | 代码缺失 | 1 天 |
| P0-5 | kernel/include/airymax/ 目录创建 + [SC] 头文件复制 | 代码缺失 | 1-2 天 |
| P0-6 | SCHED_AGENT BPF 程序设计 | 设计缺失 | 1-2 周 |
| P0-7 | 12 daemons 逐个功能设计（状态机 + 接口协议） | 设计缺失 | 2-3 周 |
| P0-8 | 第一个可编译内核模块（airy_core.c）实现 | 代码缺失 | 2-3 天 |

### P1 阻塞（应该解决 → 10 项）

| # | 阻塞项 | 预计工作量 |
|---|--------|-----------|
| P1-1 | 接口层 5 份缺失文档补充（sched/bpf/memory 契约） | 2-3 周 |
| P1-2 | 超节点功能三文档统归单一 owner | 架构评审 |
| P1-3 | [SC] 头文件数量统一 + uapi_compat.h 三路桥接修复 | 2-3 天 |
| P1-4 | 性能 SLO 目标值设定（替代"6.6 基线值"占位） | 1 周 |
| P1-5 | 各模块性能指标补充（目前仅 kernel/services/security 有部分指标） | 1 周 |
| P1-6 | 形式化验证目标重新评估（与 seL4 20+ 人年现实对齐） | 架构评审 |
| P1-7 | agentrt 双日志管线收敛决策 + 实施 | 1-2 周 |
| P1-8 | agentrt 双错误码收敛决策 + 实施 | 1-2 周 |
| P1-9 | CI/CD 文档与实际 workflow 同步 | 1 天 |
| P1-10 | 首次代码真空填补后的 CI 验证 | 1-2 天 |

### P2 优化（之后解决 → 6 项）

| # | 优化项 | 预计工作量 |
|---|--------|-----------|
| P2-1 | cognition/system/cloudnative 模块算法补充 | 2-4 周 |
| P2-2 | 数据流层 cloudnative/system/tests-linux 覆盖 | 1-2 周 |
| P2-3 | IPC 消息头增加 version/TTL 字段 | 1 天 |
| P2-4 | 安全层输入验证/审计日志/密钥管理补充 | 2-3 周 |
| P2-5 | 编码规范自动化检查子集标记 | 1-2 天 |
| P2-6 | Capability 模型 + SCHED_AGENT 的 eBPF 无状态桥接设计 | 1-2 周 |

---

## 11. 与第三方审查报告的差异

本报告是独立一手审查。与 `_review_v2.2` 第三方审查的主要差异：

1. **io_uring page flipping 不可行** —— 这是本报告的核心发现，_review_v2.2 未识别此问题
2. **VFS 用户态化内部分裂** —— 本报告发现 `01-system-architecture.md` 与 `08-known-caveats.md` 的自相矛盾，_review_v2.2 未涉及
3. **sched_ext 与 6.6 的时间线矛盾** —— 本报告明确提出，_review_v2.2 仅在提及
4. **接口层结构性坍塌 60%** —— 本报告通过实地盘点确认 5/8 文档缺失，_review_v2.2 的缺失文档清单与此不一致
5. **8 模块深度不均** —— 本报告给出了每个模块的 8 维度评分表，_review_v2.2 未做此量化

---

## 12. 建议的行动路径

### 12.1 立即行动（本周）

1. **技术可行性确认**（最高优先级）：
   - 确认 sched_ext 在 Linux 6.6 中的实际可用状态（查阅 6.6 主线源码树中的 kernel/sched/ext.c 是否存在）
   - 评估 io_uring 跨进程 zero-copy 的替代方案（shared memory + io_uring、eventfd + mmap、或退回到 socketpair）

2. **设计矛盾解决**：
   - 召开 VFS 用户态化架构决策评审，明确结论并更新两份矛盾文档

3. **奠基代码**：
   - 创建 kernel/include/airymax/ 目录
   - 创建 error.h 和 log_types.h（基于 5 模块统一方案设计）

### 12.2 近期行动（2-4 周）

4. **设计补充**：补充缺失的接口契约文档（sched/bpf/memory）
5. **模块深化**：补充 kernel 的 SCHED_AGENT BPF 程序设计 + services 的 12 daemons 逐个设计
6. **agentrt 技术债**：双日志管线 + 双错误码收敛

### 12.3 中期行动（1-2 月）

7. **首个可编译模块**：实现 airy_core.c（capability 子系统 + printk 桥接）
8. **文档升级**：将 4 份草案级文档（v0.1.x）升级至工程级（v1.0+）
9. **CI 验证**：首个内核模块通过 ci-kernel.yml 全流程

### 12.4 全面开发启动条件（建议）

**在以下条件全部满足后，方可启动 1.0.1 全面开发**：

- [ ] sched_ext 可用性确认（6.6 backport 或基线调整为 6.12）
- [ ] io_uring IPC 方案修正（page flipping → 替代方案）
- [ ] VFS 用户态化决策统一
- [ ] 10 个 [SC] 头文件全部存在于两端且双向 CI 全绿
- [ ] 第一个内核模块通过 insmod/rmmod 验证
- [ ] SCHED_AGENT BPF 程序设计文档完成
- [ ] 12 daemons 逐个功能设计完成
- [ ] agentrt 双轨制（日志 + 错误码）收敛完成
- [ ] 加权综合评分 ≥ 75%

**预计时间**：6-8 周（取决于 sched_ext 和 io_uring 的技术决策结果）

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. Internal Review Document.
