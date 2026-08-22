# 03 — Airymax Unify Design 5 模块统一方案缺陷报告

> **审计日期**：2026-07-16
> **审计来源**：近 10 轮对话中讨论的 5 模块统一方案
> **对照基准**：agentrt 现有实现 + agent-linux 现有文档 + 工程可行性标准

---

## 1. 五个统一模块概述

### 1.1 模块定义

| # | 模块 | 目标 | 共享层级 |
|---|------|------|---------|
| 1 | 统一错误码与故障定义 | agentrt + agent-linux 使用同一套 AIRY_E* 错误码 | [SC] error.h |
| 2 | 统一日志和打印系统 | printk + log_write 整合为一条观测管线 | [SC] log_types.h + [SS] 写入 API |
| 3 | 统一生命周期管理 | Supervisor 三层模型（kthread → systemd daemon → Agent） | [SC] sched.h 扩展 + [SS] 操作 |
| 4 | 统一配置管理 | 内核 Kconfig + 用户态 JSON/TOML 语义同源 | [SS] |
| 5 | IPC 数据面自治 | 控制面离线时数据面继续工作 | [SC] ipc.h 扩展 + 离线校验 |

### 1.2 可行性矩阵

| 模块 | 设计完整性 | [SC] 文件存在 | agentrt 侧代码基础 | agent-linux 侧代码 | 工程可行性 |
|------|-----------|-------------|------------------|-------------------|-----------|
| 统一错误码 | 完整（对话中设计） | error.h **不存在** | AIRY_E* 和 AIRY_ERR_* 双轨并存 | **0 行** | **不可行** |
| 统一日志+打印 | 完整（对话中设计） | log_types.h **不存在** | 双日志管线 + 3 BAN 违规 | **0 行** | **不可行** |
| 统一生命周期 | 部分（Supervisor 模型在对话中） | sched.h 缺状态枚举 | 无 Agent 生命周期管理 | **0 行** | **不可行** |
| 统一配置管理 | 部分（[SS] 语义同源） | 无 [SC] 文件 | config_unified 模块存在 | **0 行** | **不可行** |
| IPC 数据面自治 | 部分（对话中设计） | ipc.h 缺 cap 字段 | capability 未离线化 | **0 行** | **不可行** |

---

## 2. 逐模块缺陷详情

### 2.1 统一错误码

**设计方案**（对话中确立）：
- [SC] error.h 定义 `airy_err_t` (__s32) + AIRY_E* POSIX 码 (30+ 个) + 自定义码 + 分段哨兵 + AIRY_ERR_COUNT
- AIRY_ERR_* 仅作为兼容别名保留，逐步废弃
- Linux errno 映射表：AIRY_E_ERRNO → Linux -EXXX
- 哨兵值 AIRY_ERR_COUNT=800

**当前缺陷**：

| ID | 缺陷 | 详情 |
|----|------|------|
| ERR-D01 | error.h 物理文件未创建 | 两端都不存在，设计仅存在于对话上下文 |
| ERR-D02 | AIRY_ERR_* 未收敛 | airy_types.h 30 个 POSIX 码 + error.h ~90 个扩展码，值域部分冲突 |
| ERR-D03 | 迁移计划未确定 | AIRY_ERR_* → AIRY_E* 的渐进迁移策略未定义 |
| ERR-D04 | 内核端 linux/errno.h 映射未定义 | AIRY_EPERM=(-1) 与 Linux EPERM=(-1) 如何保证同值未验证 |
| ERR-D05 | 自定义码与 POSIX 码值域重叠检查未完成 | AIRY_ERR_PROTOCOL=-900 vs AIRY_EPROTO=-71 已知重叠 |
| ERR-D06 | 内核 errno 返回约定未定义 | 内核态函数返回 -EXXX 还是 AIRY_EXXX？ |
| ERR-D07 | `#ifdef __KERNEL__` 桥接未处理 | error.h 的用户态/内核态类型桥接未设计 |

### 2.2 统一日志+打印

**设计方案**（对话中确立）：
- [SC] log_types.h：`struct airy_log_record` 128B + 5 级别枚举 + Linux 8 级映射
- 内核 printk → airy_klog_write → Ring Buffer (reserved-memory) → Logger Daemon (mmap 只读)
- 用户态 log_write → Ring Buffer → Logger Daemon
- 格式化完全推出数据面，由 Logger Daemon 负责
- Panic 时回退到 printk 原生路径

**当前缺陷**：

| ID | 缺陷 | 详情 |
|----|------|------|
| LOG-D01 | log_types.h 物理文件未创建 | 两端都不存在 |
| LOG-D02 | LOG_* 和 AIRY_LOG_* 双管线并存 | 68 文件通过 logging_compat.h 桥接 |
| LOG-D03 | BAN-294：heapstore_log.h 自建独立日志管线 | heapstore 模块 |
| LOG-D04 | BAN-299：memory.c 11 处 fprintf(stderr) | commons/utils/memory/src/memory.c |
| LOG-D05 | BAN-305：svc_logger.h 不含 logging_compat.h | commons/utils/logging/include/svc_logger.h |
| LOG-D06 | Ring Buffer 方案未文档化 | reserved-memory / mmap / producer-consumer 未曾进入 docs/AirymaxOS |
| LOG-D07 | Logger Daemon 进程架构未设计/文档化 | 包括：启动顺序、与 systemd 集成、崩溃恢复策略 |
| LOG-D08 | printk → airy_klog_write 转换层未设计 | Linux 8 级 → Airymax 5 级映射表已设计但未实现 |
| LOG-D09 | Panic 回退路径未设计/文档化 | printk_safe_enter/exit 机制未集成 |
| LOG-D10 | ring buffer 多生产者写入的并发控制未设计 | 内核 per-CPU + 用户态原子操作如何协调 |
| LOG-D11 | LOG-21~26 高级功能接口已定义但实现为空 | 异步/JSON/Syslog/轮转/监控/全功能 |
| LOG-D12 | 现有 log_write() 改造路径未定义 | vsnprintf + format_log_message + fwrite → prb_reserve+commit |

### 2.3 统一生命周期管理

**设计方案**（对话中确立）：
- L0：内核态 kthread Supervisor (sched_ext SCHED_AGENT)
- L1：用户态 systemd daemon Supervisor (airy-supervisord)
- L2：Agent 执行 Supervisor (CoreLoopThree)
- [SC] sched.h 扩展：`enum airy_agent_state` (8 态) + Supervisor 事件

**当前缺陷**：

| ID | 缺陷 | 详情 |
|----|------|------|
| LIF-D01 | sched.h 缺少 Agent 生命周期状态枚举 | 仅有 task_desc 和调度原语 |
| LIF-D02 | sched.h 缺少 Supervisor 事件枚举 | HEARTBEAT_LOST/OOM_KILL/CAP_VIOLATION/PHASE_TIMEOUT/BUDGET_EXHAUST |
| LIF-D03 | L0 kthread Supervisor 设计未文档化 | 内核态 Agent 监控 kthread 如何实现未定义 |
| LIF-D04 | L1 airy-supervisord daemon 设计未文档化 | 与 systemd 集成方式、SIGCHLD 处理未定义 |
| LIF-D05 | L0→L1 通知机制未设计 | IPC CONTROL 消息格式未定义 |
| LIF-D06 | 3 态降级（[DSL] 层）未设计 | 共享失败时内核用 RUNNING/STOPPED/DEAD，用户态用 8 态 |
| LIF-D07 | agentrt 侧 Agent 生命周期管理实现状态不明 | 当前 agentrt 是否有状态机实现？ |

### 2.4 统一配置管理

**设计方案**（对话中确立）：
- 无 [SC] 层（配置不适用于定长二进制）
- [SS] 层：key-value + schema 语义同源
- [IND] 层：内核 Kconfig/sysctl/eBPF map vs 用户态 JSON/TOML

**当前缺陷**：

| ID | 缺陷 | 详情 |
|----|------|------|
| CFG-D01 | 无任何统一配置设计文档 | 仅对话中讨论 |
| CFG-D02 | agentrt config_unified 模块与 Kconfig 的语义映射未定义 | 哪些 key 有对应关系？ |
| CFG-D03 | 热重载机制未设计（[SS] 层） | 内核 sysctl 和用户态 log_reload_config 如何对应？ |
| CFG-D04 | 配置验证 schema 未设计 | 两端共享的配置 schema 格式未定义 |

### 2.5 IPC 数据面自治

**设计方案**（对话中确立）：
- 三原则：Ring 生命周期与控制面解耦 + Capability 离线缓存校验 + 控制面恢复 Reconciliation
- 借鉴 seL4 Endpoint 状态机（Idle/Send/Recv）
- fastpath 状态机 C-S9 内联 capability 检查的离线版本

**当前缺陷**：

| ID | 缺陷 | 详情 |
|----|------|------|
| IPC-D01 | 数据面自治三原则未文档化 | 仅对话中讨论 |
| IPC-D02 | Capability 离线缓存校验结构未进 ipc.h | ring_id/badge/expires_ns 三元组未定义 |
| IPC-D03 | 07-ipc-fastpath.md 无 capability daemon 离线降级路径 | C-S9 失败 → ERROR，无降级设计 |
| IPC-D04 | Reconciliation 流程未定义 | 控制面恢复后的 ring 扫描/校验/吊销步骤未定义 |
| IPC-D05 | Ring 生命周期与控制面解耦的设计未文档化 | 创建/销毁 vs 使用 的职责分离未定义 |
| IPC-D06 | Capability 过期策略未定义 | expires_ns=0 永不过期，非 0 时检查是否用 wall clock？ |
| IPC-D07 | 无 reconciliation 事件通知机制 | 权限吊销时如何通知使用方？ |

---

## 3. agentrt 技术债汇总

### 3.1 BAN 违规（阻塞统一日志）

| BAN ID | 文件 | 违规内容 | 严重度 |
|--------|------|---------|--------|
| BAN-294 | heapstore/include/heapstore_log.h | 自建独立日志管线，未使用统一 logging_compat.h | P0 |
| BAN-299 | commons/utils/memory/src/memory.c | 11 处 fprintf(stderr) 替代日志 | P1 |
| BAN-305 | commons/utils/logging/include/svc_logger.h | 不含 `#include "logging_compat.h"` | P1 |

### 3.2 双轨制（阻塞统一设计）

| 双轨项 | 两条轨道 | 影响模块 |
|--------|---------|---------|
| 错误码 | AIRY_E* (airy_types.h, 30 个) vs AIRY_ERR_* (error.h, ~90 个) | 全部模块 |
| 日志管线 | LOG_* (logging.h) vs AIRY_LOG_* (logging_compat.h → logger.h) | 68 文件 |
| 打印输出 | printk (内核) vs printf/fprintf (用户态) vs airy_print_* (已委托) | 内存管理、堆存储 |
| IPC 模型 | corekern 轻量 IPC vs commons 应用级 IPC | 核心层 vs 服务层 |

### 3.3 未实现的接口声明

| LOG ID | 功能 | logging.h 声明 | logging.c 实现 |
|--------|------|---------------|---------------|
| LOG-21 | 异步写入 | async_mode 配置存在 | async_buffer_size 未使用 |
| LOG-22 | JSON 格式化 | LOG_FORMAT_JSON 枚举存在 | 格式化函数未实现 JSON 分支 |
| LOG-23 | Syslog 输出 | LOG_OUTPUT_SYSLOG 枚举存在 | syslog_facility 未使用 |
| LOG-24 | 时间轮转 | max_file_size / max_backup_count 配置存在 | 轮转函数未实现 |
| LOG-25 | 监控采集 | enable_statistics 配置存在 | 指标统计未实现 |
| LOG-26 | 全功能集成 | log_config_t 完整 | 多项能力空实现 |

---

## 4. 综合判定

5 个统一模块全部处于"概念阶段"——设计在对话上下文中进行了充分讨论，逻辑上自洽，但：

1. **无一进入项目文档体系**：所有设计仅存在于对话历史中，未固化为 docs/AirymaxOS 或 docs-closed 中的正式文档
2. **[SC] 核心文件未创建**：error.h 和 log_types.h 是最关键的两个 [SC] 文件，两端都不存在
3. **agentrt 技术债阻塞统一**：双错误码、双日志管线、BAN 违规必须先行修复
4. **agent-linux 无代码实现任何统一模块的内核端**：0 行代码意味着所有模块的 agent-linux 侧实现为零

**统一方案的设计是正确的，但从设计到实现之间存在 0→1 的根本性鸿沟**——需要先创建共享头文件、修复技术债、建立构建系统，然后每个模块才能开始实际的代码实现。
