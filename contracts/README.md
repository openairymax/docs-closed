# Contracts — 跨团队接口合约

`contracts/`

## 概述

`contracts/` 目录包含 AgentRT 三智能体团队协作模式下的跨团队接口合约文件。合约文件是团队间唯一的接口真理来源，所有跨团队接口必须通过合约定义，优先于任何代码实现。遵循"合约先行"策略，确保三团队并行开发时接口一致、无冲突。

> **注意**：本目录为本地开发辅助，不纳入 git 追踪（已加入 `.gitignore`）。

## 设计原则

- **合约先行**：合约定义优先于代码实现，任何接口变更必须先更新合约
- **ABI 稳定**：合约版本冻结后，接口签名不得破坏性变更
- **编译验证**：合约文件必须能通过 `gcc -std=c11` 编译，确保类型完整性
- **三权分立**：每个合约文件仅涉及两个团队的接口，避免三方耦合

## 目录结构

```
contracts/
├── contract_A_B.h      # 团队A（核心引擎）↔ 团队B（生态+SDK）接口合约
├── contract_A_C.h      # 团队A（核心引擎）↔ 团队C（基础设施）接口合约
├── contract_B_C.h      # 团队B（生态+SDK）↔ 团队C（基础设施）接口合约
└── contract_test.c     # 合约编译验证测试
```

## 合约文件说明

### contract_A_B.h — 团队A ↔ 团队B

定义 C 核心引擎向多语言 SDK 和生态层暴露的接口：

| 章节 | 内容 | 对应连接线 |
|------|------|-----------|
| 第1节 | IPC 消息格式（三层 IPC 架构） | C-L01 |
| 第2节 | HTTP/WS/STDIO 网关 API 定义 | C-L03 |
| 第3节 | 协议路由表（多协议适配与转换） | C-L11 |
| 第4节 | 内存布局（MemoryRovol 桥接接口） | C-L12 |
| 第5节 | agentos.yaml 配置 Schema（C 结构体映射） | — |
| 第6节 | Hook 系统接口（生命周期回调） | — |
| 第7节 | 错误码映射表（A 错误码 → B SDK 异常映射） | — |
| 第8节 | 时序约束（跨语言调用超时与重试） | — |

### contract_A_C.h — 团队A ↔ 团队C

定义 C 核心引擎向测试/CI/部署基础设施暴露的接口：

| 章节 | 内容 |
|------|------|
| 第1节 | Daemon 测试注入点（Testing Injection Points） |
| 第2节 | Prometheus 指标命名规范与数据结构 |
| 第3节 | IPC Bus 测试 Hooks（消息注入/拦截/监控） |
| 第4节 | 健康检查端点定义 |
| 第5节 | 错误码映射表（A 错误码 → C 测试断言期望） |
| 第6节 | 时序约束（启动/就绪/心跳/超时） |

### contract_B_C.h — 团队B ↔ 团队C

定义多语言 SDK/CLI/TUI 向 CI/CD 和部署基础设施暴露的接口：

| 章节 | 内容 |
|------|------|
| 第1节 | CLI/TUI 退出码规范 |
| 第2节 | SDK 测试 Harness 接口 |
| 第3节 | 多语言 SDK 版本兼容矩阵 |
| 第4节 | Docker 健康检查端点与容器契约 |
| 第5节 | CI 产物命名规范 |
| 第6节 | 测试覆盖率阈值 |
| 第7节 | 部署环境变量契约 |
| 第8节 | 发布版本号规范 |

### contract_test.c — 编译验证测试

验证所有合约头文件的类型完整性和宏定义正确性。不链接任何团队实现，仅验证合约可编译。

## 使用方式

```bash
# 编译验证合约文件
cd contracts/
gcc -std=c11 -Wall -Wextra -Werror -c contract_test.c -o contract_test.o

# 验证单个合约头文件
gcc -std=c11 -c contract_A_B.h -o /dev/null
gcc -std=c11 -c contract_A_C.h -o /dev/null
gcc -std=c11 -c contract_B_C.h -o /dev/null
```

## 合约版本管理

| 字段 | 说明 |
|------|------|
| `@contract_version` | 语义化版本号（MAJOR.MINOR.PATCH） |
| `@teams` | 涉及的团队标识 |
| `@owner` | 接口定义方和消费方 |
| `@frozen` | 合约冻结日期 |

合约冻结后，任何变更必须通过 CI 通知机制告知相关团队。MAJOR 版本变更需要两团队共同审查。

## 团队职责

| 团队 | 合约角色 | 职责 |
|------|---------|------|
| **团队A（核心引擎）** | contract_A_B.h 定义方、contract_A_C.h 定义方 | 保证 ABI 稳定性，变更需通知 B/C |
| **团队B（生态+SDK）** | contract_A_B.h 消费方、contract_B_C.h 定义方 | 基于 A_B 合约编写 SDK，保证 B_C 合约稳定 |
| **团队C（基础设施）** | contract_A_C.h 消费方、contract_B_C.h 消费方 | 基于合约编写测试/CI/部署，验证合约合规 |

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
