# 00 — agentrt-linux 方案全面系统性分析报告 v2.2

> **审查日期**：2026-07-16
> **审查来源**：近 10 轮对话（d8 memory_compat.h → d12 Airymax Unify Design 评估）
> **审查范围**：agentrt-linux 仓库、docs/AirymaxOS 文档体系、agentrt 对照仓库、docs/AirymaxRT 文档体系
> **审查基线**：IRON-9 v2 三层共享模型（[SC]/[SS]/[IND]）+ 第四层 [DSL] 降级生存层

---

## 1. 执行摘要

### 1.1 核心判定

**agentrt-linux 目前不具备"可以根据方案开始全面开发"的条件。**

近 10 轮对话揭示了方案在五个维度上的系统性缺陷：

1. **代码真空**：0 行可编译内核源码，8 子仓均为 README-only 空壳
2. **[SC] 共享头文件不完整**：6+2 中 error.h 和 log_types.h 未创建
3. **agentrt 技术债阻塞统一**：BAN-294/299/305 + 双错误码 + 双日志管线
4. **文档-工程鸿沟**：128 个 .md 设计文档 → 0 行 .c 代码，无翻译路径
5. **生存层缺失**：无 [DSL] 降级设计，共享失败时无生存策略

### 1.2 五个统一模块可行性

| 模块 | 设计可行性 | 工程可行性 | 阻塞项 |
|------|-----------|-----------|--------|
| 统一错误码 | 可行 | 不可行 | error.h 未创建 + AIRY_ERR_* 未收敛 |
| 统一日志+打印 | 概念可行 | 不可行 | log_types.h 未创建 + BAN 违规未修复 |
| 统一生命周期 | 部分可行 | 不可行 | Agent 状态枚举未进 sched.h |
| 统一配置管理 | 概念可行 | 不可行 | 无两端代码 |
| IPC 数据面自治 | 概念可行 | 不可行 | 0 行代码 + 缓存校验未文档化 |

---

## 2. 项目现状统计

### 2.1 agentrt-linux 仓库

| 维度 | 数量 | 备注 |
|------|------|------|
| .md 文档 | 128+ | 含 8 子仓 README + .github README |
| .c 源文件 | **0** | 无任何可编译 C 代码 |
| .h 头文件 | **0** | 无任何头文件 |
| .yaml 配置 | 1 | ssot-registry.yaml |
| Kconfig | **0** | 无内核配置 |
| Makefile/Kbuild | 1 | 仅顶层空 Makefile |
| CI workflows | 6 | ci-kernel/sc-dual-ci/ssot-validate 等（无法验证空仓库） |
| 子仓 | 8 | kernel/services/security/cognition/memory/system/cloudnative/tests-linux（全部 README-only） |

### 2.2 agentrt 对照仓库

| 维度 | 数量 |
|------|------|
| .c 源文件 | 200+ |
| .h 头文件 | 200+ |
| CMake 构建 | 可编译成功 |
| [SC] 共享头文件物理宿主 | agentrt/commons/include/airymax/ (8 文件) |

### 2.3 docs/AirymaxOS 文档体系

| 类别 | 文档数 | 版本状态 |
|------|--------|---------|
| 10-architecture | 8 | 03-microkernel-strategy (v0.1.1), 其余 v1.0+ |
| 30-interfaces | 8 | 07-ipc-fastpath (v0.2.8), 其余 v1.0+ |
| 50-engineering-standards | ~15 | ssot-registry/120-cross-project-code-sharing v1.0+ |
| 110-security | 3 | capability-model (v0.1.1) |
| 20-modules | 8 | 内核/服务/安全/认知/记忆/云原生/系统/测试子仓定义 |
| 130-roadmap | 5 | 里程碑与时间线（含 1.0.0/1.0.1/2.x.x） |
| 其他 | ~60 | 测试/构建/驱动/性能/运维/兼容性/国际化/发布 |

---

## 3. 分类缺陷清单

### 3.1 代码真空（详见 [01-code-vacuum-report.md](01-code-vacuum-report.md)）

| ID | 缺陷 | 严重度 | 依据 |
|----|------|--------|------|
| VAC-001 | agentrt-linux 无任何 .c/.h 源文件 | **P0 阻塞** | Glob 扫描 0 结果 |
| VAC-002 | 8 子仓全部为 README-only 空壳 | **P0 阻塞** | 逐目录扫描 |
| VAC-003 | 无 Kconfig 文件 | P0 | Glob 扫描 0 结果 |
| VAC-004 | 无 Kbuild 文件 | P0 | Glob 扫描 0 结果 |
| VAC-005 | CI workflows (6 个) 无法验证空仓库 | P1 | sc-dual-ci.yml 依赖 .c/.h 文件 |
| VAC-006 | kernel 子仓无第一个可 insmod 的内核模块 | **P0 阻塞** | kernel/ 目录仅 README |

### 3.2 [SC] 共享头文件（详见 [02-sc-shared-headers-audit.md](02-sc-shared-headers-audit.md)）

| ID | 缺陷 | 严重度 | 依据 |
|----|------|--------|------|
| SC-001 | error.h 不存在 | **P0 阻塞** | Glob 扫描确认缺失 |
| SC-002 | log_types.h 不存在 | **P0 阻塞** | Glob 扫描确认缺失 |
| SC-003 | uapi_compat.h 未处理 `__KERNEL__` 路径 | P0 | 仅用 `#ifdef __linux__` 桥接 |
| SC-004 | [SC] 双向 CI 无法验证（无 agentrt-linux 代码端） | P0 | sc-dual-ci.yml 无输入 |
| SC-005 | sched.h 缺少 Agent 生命周期状态枚举 | P1 | 仅含 task_desc 和调度原语 |
| SC-006 | ipc.h 缺少 capability 缓存校验字段 | P1 | 仅有 header，无 cap 相关字段 |

### 3.3 agentrt 技术债（详见 [03-five-unify-modules-gap-report.md](03-five-unify-modules-gap-report.md)）

| ID | 缺陷 | 严重度 | 依据 |
|----|------|--------|------|
| BAN-294 | heapstore_log.h 自建独立日志管线 | P0 | heapstore 模块 |
| BAN-299 | memory.c 11 处 fprintf(stderr) 泄漏报告 | P1 | commons/utils/memory/src/memory.c |
| BAN-305 | svc_logger.h 不含 logging_compat.h | P1 | commons/utils/logging/include/svc_logger.h |
| ERR-001 | AIRY_E* 和 AIRY_ERR_* 双错误码并存 | P0 | airy_types.h vs error.h |
| LOG-001 | LOG_* 和 AIRY_LOG_* 双日志管线并存 | P0 | logging.h vs logging_compat.h vs logger.h |
| LOG-002 | LOG-21~26 高级功能接口已定义但实现为空 | P2 | logging.h 声明 vs logging.c 实现 |

### 3.4 设计文档鸿沟（详见 [04-missing-design-docs.md](04-missing-design-docs.md)）

| ID | 缺陷 | 严重度 |
|----|------|--------|
| DOC-001 | Airymax Unify Design 完整方案未文档化 | **P0** |
| DOC-002 | 二进制 Ring Buffer + Logger Daemon 方案未文档化 | **P0** |
| DOC-003 | [DSL] 降级生存层设计未文档化 | **P0** |
| DOC-004 | Panic 回退 printk 原生路径设计未文档化 | P1 |
| DOC-005 | Capability 离线缓存校验 + reconciliation 未文档化 | P1 |
| DOC-006 | 内核 mmap 共享 Ring Buffer 的 reserved-memory DT 方案未文档化 | P1 |
| DOC-007 | Logger Daemon 进程架构设计未文档化 | P1 |
| DOC-008 | Printk → airy_klog_write 转换层设计未文档化 | P1 |
| DOC-009 | 内核/用户态头文件 `#ifdef __KERNEL__` 类型桥接规范未文档化 | P1 |
| DOC-010 | Agent 生命周期 Supervisor 三层模型未文档化 | P1 |

### 3.5 生存层缺失（详见 [05-survival-layer-design.md](05-survival-layer-design.md)）

| ID | 缺陷 | 严重度 |
|----|------|--------|
| DSL-001 | error.h 无 AIRY_SC_FALLBACK 降级块 | P0 |
| DSL-002 | log_types.h 无 Panic 回退 printk 原生路径 | P0 |
| DSL-003 | sched.h 无 3 态降级（RUNNING/STOPPED/DEAD） | P1 |
| DSL-004 | ipc.h 无共享失败降级（pipe/socket 回退） | P1 |
| DSL-005 | 无 [DSL] 层统一框架设计 | P0 |

### 3.6 IPC 数据面自治（详见 [06-ipc-data-plane-autonomy-report.md](06-ipc-data-plane-autonomy-report.md)）

| ID | 缺陷 | 严重度 |
|----|------|--------|
| IPC-001 | 数据面自治三原则未文档化 | P0 |
| IPC-002 | Capability 离线缓存校验机制未定义 | P1 |
| IPC-003 | 控制面恢复 Reconciliation 流程未定义 | P1 |
| IPC-004 | Ring 生命周期与控制面解耦未设计 | P1 |
| IPC-005 | Fastpath 状态机无 capability daemon 离线降级路径 | P1 |

---

## 4. 前置工作优先级排序

### P0（阻塞一切开发启动）

| # | 工作项 | 关联缺陷 |
|---|--------|---------|
| 1 | agentrt-linux kernel 子仓创建第一个可 insmod 的内核模块（1 .c + Makefile + Kconfig） | VAC-001~006 |
| 2 | [SC] error.h 创建于 agentrt-linux/include/uapi/airymax/ | SC-001 |
| 3 | [SC] log_types.h 创建于 agentrt-linux/include/uapi/airymax/ | SC-002 |
| 4 | [SC] 双向 CI 验证可运行（两端均有代码可对比） | SC-004 |
| 5 | uapi_compat.h 增加 `#ifdef __KERNEL__` 路径 + agentrt/agentrt-linux 双端验证 | SC-003 |
| 6 | Airymax Unify Design 完整方案文档化（[SC] error.h + log_types.h 设计） | DOC-001 |
| 7 | 二进制 Ring Buffer + Logger Daemon 方案文档化进 docs/AirymaxOS | DOC-002 |
| 8 | [DSL] 降级生存层设计文档化进 docs/AirymaxOS | DOC-003, DSL-001~005 |

### P1（阻塞 5 模块统一）

| # | 工作项 | 关联缺陷 |
|---|--------|---------|
| 9 | agentrt BAN-294 修复：删除 heapstore_log.h，替换为 logging_compat.h | BAN-294 |
| 10 | agentrt BAN-305 修复：svc_logger.h 补充 logging_compat.h | BAN-305 |
| 11 | AIRY_ERR_* → AIRY_E* 收敛方案确定并文档化 | ERR-001 |
| 12 | LOG_* 和 AIRY_LOG_* 二选一收敛方案确定 | LOG-001 |
| 13 | Panic 回退路径设计文档化 | DOC-004 |
| 14 | Capability 离线缓存校验 + reconciliation 设计文档化 | DOC-005 |
| 15 | 内核 `#ifdef __KERNEL__` 桥接规范文档化 | DOC-009 |
| 16 | Agent 生命周期 Supervisor 三层模型文档化 | DOC-010 |
| 17 | IPC 数据面自治三原则文档化 | IPC-001 |

### P2（优化完善）

| # | 工作项 | 关联缺陷 |
|---|--------|---------|
| 18 | agentrt BAN-299 修复：memory.c fprintf → logging_compat.h | BAN-299 |
| 19 | LOG-21~26 高级功能实现 | LOG-002 |
| 20 | Logger Daemon 进程架构设计 | DOC-007 |
| 21 | Printk → airy_klog_write 转换层设计 | DOC-008 |
| 22 | sched.h 补充 Agent 生命周期状态枚举 | SC-005 |
| 23 | ipc.h 补充 capability 缓存校验字段 | SC-006 |

---

## 5. 5 模块统一可行性最终判定

### 5.1 设计可行性（概念层）

5 个模块在概念层面全部可行，IRON-9 v2 的 [SC]/[SS]/[IND] 三层模型为此类统一提供了正确的架构框架。具体的概念方案（[SC] error.h 统一错误码、Ring Buffer + Logger Daemon 统一日志、Supervisor 三层生命周期、[SS] 语义同源配置、capability 缓存校验数据面自治）在逻辑上是自洽的。

### 5.2 工程可行性（实现层）

**0/5 模块具备工程可行性。** 全部阻塞于缺少基础的工程构件（代码、构建系统、共享头文件、CI 验证）。

### 5.3 判定依据

工程可行性需要同时满足三个条件：
1. 存在至少一个可编译的目标（agentrt-linux 的内核模块 / agentrt 的库）
2. 共享契约层物理文件存在且两端可编译
3. CI 可验证共享头文件的一致性

当前三项条件全部不满足。

### 5.4 关于"内核态和用户态共享"

**概念上可行的前提**是 P0 和 P1 工作全部完成。在 P0/P1 完成前，断言"5 模块可以内核态和用户态共享"缺乏工程证据支撑。一旦 agentrt-linux kernel 子仓有了第一个可编译的内核模块、[SC] 共享头文件完整且 CI 验证通过、agentrt 技术债修复完毕，这些前提条件达成后，共享才从"概念可行"跃迁为"工程可行"。

---

## 6. 审查结论

agentrt-linux 方案的**设计文档体系**（128 个 .md 文件）在抽象层次上是完整且自洽的——从微内核策略到 IPC fastpath 状态机到 capability 模型到 syscall 注册表，覆盖了操作系统设计的方方面面。

但方案存在**设计文档 → 工程产物的系统性断层**：0 行可编译内核源码、0 个共享头文件的 agentrt-linux 端物理副本、0 个可运行的 CI 验证、0 个可安装的内核模块。

建议将 agentrt-linux 1.0.1 全面开发启动的前置条件明确为 **P0 工作项全部完成**（8 项）。在此期间，先完成 Airymax Unify Design 的文档化（将对话上下文中的设计方案固化为正式文档），再修复 agentrt 的技术债（BAN 违规和双轨制），最后以"第一个内核模块可编译可验证"作为全面开发的起点。
