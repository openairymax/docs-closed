# 04 — agent-linux 缺失设计文档清单

> **审计日期**：2026-07-16
> **审计方法**：基于 5 模块 Airymax Unify Design + docs/AirymaxOS 现有文档体系 逐模块对比
> **结论**：agent-linux 需要补充完成的设计文档至少有 **20 份**。

---

## 1. 审计方法

以"开发前必须有设计文档"为准则，对以下两类文档进行对比分析：

1. **对话中确立了设计方案但未进入项目文档体系**：需要从对话上下文提取并固化为正式文档
2. **现有文档版本过低（< 1.0）需要升级到工程实现级**：需要补充实现细节

---

## 2. 需要新增的文档（对话设计 → 正式文档）

### 2.1 架构层

| # | 文档标题 | 建议路径 | 内容 | 优先级 |
|---|---------|---------|------|--------|
| DOC-N01 | Airymax Unify Design 总纲 | docs/AirymaxOS/10-architecture/08-unify-design.md | 5 模块统一方案总体设计、[SC]/[SS]/[IND]/[DSL] 四层架构说明 | P0 |
| DOC-N02 | [DSL] 降级生存层设计 | docs/AirymaxOS/10-architecture/09-degraded-survival-layer.md | 每模块 AIRY_SC_FALLBACK 降级块、Panic 回退、控制面离线回退 | P0 |

### 2.2 接口层

| # | 文档标题 | 建议路径 | 内容 | 优先级 |
|---|---------|---------|------|--------|
| DOC-N03 | [SC] error.h 共享契约 | docs/AirymaxOS/30-interfaces/08-sc-error-contract.md | 统一错误码 AIRY_E* 定义、AIRY_E_ERRNO 映射、分段哨兵、UAPI 类型桥接 | P0 |
| DOC-N04 | [SC] log_types.h 共享契约 | docs/AirymaxOS/30-interfaces/09-sc-log-types-contract.md | struct airy_log_record 128B、5 级别、printk 映射表、producer/consumer 契约 | P0 |
| DOC-N05 | [SC] sched.h 扩展方案 | docs/AirymaxOS/30-interfaces/10-sc-sched-extension.md | enum airy_agent_state 8 态、Supervisor 事件枚举、IPC CONTROL 通知格式 | P1 |

### 2.3 数据流层

| # | 文档标题 | 建议路径 | 内容 | 优先级 |
|---|---------|---------|------|--------|
| DOC-N06 | 二进制 Ring Buffer 共享日志设计 | docs/AirymaxOS/40-dataflows/05-ring-buffer-logging.md | reserved-memory DT、mmap、producer-consumer、背压、Daemon 崩溃恢复 | P0 |
| DOC-N07 | Logger Daemon 进程架构 | docs/AirymaxOS/40-dataflows/06-logger-daemon-design.md | 启动顺序、systemd 集成、格式化引擎、错误码字典渲染、多输出目标 | P1 |
| DOC-N08 | Panic 生存路径设计 | docs/AirymaxOS/40-dataflows/07-panic-survival-path.md | printk_safe_enter/exit、emergency buffer、kdump 导出 airy_log_reserved 区 | P1 |

### 2.4 安全层

| # | 文档标题 | 建议路径 | 内容 | 优先级 |
|---|---------|---------|------|--------|
| DOC-N09 | IPC 数据面自治设计 | docs/AirymaxOS/110-security/04-ipc-data-plane-autonomy.md | 离线 capability 缓存校验、Reconciliation 流程、Ring 生命周期解耦 | P1 |
| DOC-N10 | IPC 控制面恢复 Reconciliation | docs/AirymaxOS/110-security/05-ipc-control-plane-reconciliation.md | 恢复后 ring 扫描/校验/吊销步骤、事件通知、debugfs 接口 | P1 |

### 2.5 模块层

| # | 文档标题 | 建议路径 | 内容 | 优先级 |
|---|---------|---------|------|--------|
| DOC-N11 | 内核态 Agent 生命周期 Supervisor 设计 | docs/AirymaxOS/20-modules/09-kernel-agent-supervisor.md | L0 kthread supervisor、SCHED_AGENT BPF 策略、心跳检测、强制终止 | P1 |
| DOC-N12 | 用户态 Supervisor Daemon 设计 | docs/AirymaxOS/20-modules/10-user-supervisor-daemon.md | L1 airy-supervisord、systemd 集成、SIGCHLD 处理、状态机 | P1 |
| DOC-N13 | 统一配置管理 [SS] 语义同源设计 | docs/AirymaxOS/20-modules/11-unified-config.md | key-value schema、Kconfig ↔ config_unified 映射、热重载 | P1 |
| DOC-N14 | Logger Daemon 模块设计 | docs/AirymaxOS/20-modules/12-logger-daemon-module.md | 作为 12 daemon 之一的设计、API、配置、依赖关系 | P2 |
| DOC-N15 | printk → airy_klog_write 转换层 | docs/AirymaxOS/20-modules/13-printk-bridge.md | /dev/kmsg 拦截、级别映射、Ring Buffer 写入路径 | P2 |

### 2.6 工程标准层

| # | 文档标题 | 建议路径 | 内容 | 优先级 |
|---|---------|---------|------|--------|
| DOC-N16 | [SC] 头文件类型桥接规范 | docs/AirymaxOS/50-engineering-standards/11-sc-header-type-bridging.md | `#ifdef __KERNEL__` 路径、UAPI 类型使用准则、禁止模式 | P1 |
| DOC-N17 | agentrt 日志系统收敛计划 | docs/AirymaxRT/50-engineering-standards/11-log-convergence-plan.md | LOG_*/AIRY_LOG_* 二选一、BAN 违规修复路线、logging_compat.h 退休时间表 | P1 |
| DOC-N18 | AIRY_ERR_* → AIRY_E* 错误码迁移计划 | docs/AirymaxRT/50-engineering-standards/12-error-code-migration-plan.md | 迁移映射表、渐进策略、兼容期、死代码清理时间表 | P1 |

---

## 3. 需要升级的现有文档（< 1.0 → 工程实现级）

| # | 现有文档 | 当前版本 | 需补充内容 | 优先级 |
|---|---------|---------|-----------|--------|
| DOC-U01 | 03-microkernel-strategy.md | 0.1.1 | [DSL] 降级策略、内核态生存层设计 | P1 |
| DOC-U02 | 07-ipc-fastpath.md | 0.2.8 | capability daemon 离线降级路径、数据面自治状态转换 | P1 |
| DOC-U03 | 03-capability-model.md | 0.1.1 | 离线缓存校验数据结构、Reconciliation 算法 | P1 |
| DOC-U04 | 06-iron9-shared-model.md | — | 新增 [DSL] 层定义、error.h/log_types.h 列入 [SC] 清单 | P1 |

---

## 4. agentrt 侧需要修复的技术债（阻塞统一）

| # | 工作项 | 参考 BAN/LOG ID | 优先级 |
|---|--------|---------------|--------|
| FIX-01 | 删除 heapstore_log.h，替换为 logging_compat.h | BAN-294 | P0 |
| FIX-02 | svc_logger.h 补充 `#include "logging_compat.h"` | BAN-305 | P1 |
| FIX-03 | memory.c 11 处 fprintf → logging_compat.h | BAN-299 | P1 |
| FIX-04 | 决定 LOG_* vs AIRY_LOG_* 唯一 SSoT + 68 文件迁移 | LOG-001 | P0 |
| FIX-05 | 决定 AIRY_E* vs AIRY_ERR_* 唯一 SSoT + 全仓库迁移 | ERR-001 | P0 |
| FIX-06 | 实现 LOG-21~26 高级功能或标记为废弃 | LOG-002 | P2 |

---

## 5. 总结

**agent-linux 需要的设计文档（20 份）** 分为四类：

| 类别 | 数量 | 状态 |
|------|------|------|
| 对话中已设计但未文档化 | P0: 4 份, P1: 10 份, P2: 1 份 | 需从对话上下文提取 |
| 现有文档版本过低需升级 | 4 份 | 需补充工程实现细节 |
| agentrt 技术债修复 | 6 项 | 需先修复才能开始统一 |
| **总计** | **25 项** | — |

这些文档**必须在 agent-linux 1.0.1 全面开发启动之前**完成撰写和审核。没有这些文档，开发团队将面临"边开发边改设计"的混乱局面。
