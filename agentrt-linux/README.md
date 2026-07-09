Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agentrt-linux（AirymaxOS）闭源技术参考文档

> **文档定位**: agentrt-linux 内部技术参考文档索引，**闭源不公开**
> **保密级别**: SPHARX Ltd 内部参考
> **版本**: 0.1.1（文档体系完成）
> **最后更新**: 2026-07-07
> **适用范围**: agentrt-linux 架构委员会 + 内核开发组

---

## 1. 文档定位与保密声明

本目录存放 agentrt-linux（AirymaxOS）的**内部技术参考文档**，这些文档：

1. **全面参考 Euler 技术规范**：Euler 社区的技术规范、内核改动、工程实践对 agentrt-linux 设计具有重要参考价值，但参考文档不能公开
2. **闭源不公开**：本目录所有文档归 SPHARX Ltd 所有，仅供内部使用
3. **开源文档隔离**：开源文档（`docs/AirymaxAgentOS/`）中**严禁**出现对 Euler 参考发行版的相关描述；所有参考内容仅限本目录

---

## 2. 目录结构

```
docs-closed/agentrt-linux/
├── README.md                          # 本文件 — 闭源参考文档索引
├── 01-openeuler-tech-reference/       # openEuler 技术规范参考
│   ├── README.md                      # 索引
│   ├── 01-scheduler-spec.md           # 调度器技术规范（EEVDF + sched_ext）
│   ├── 02-io-uring-spec.md            # io_uring 异步 I/O 规范
│   ├── 03-ebpf-spec.md                # eBPF 可编程扩展规范
│   ├── 04-memory-mgmt-spec.md         # 内存管理规范（MGLRU + CXL）
│   ├── 05-security-spec.md            # 安全子系统规范（LSM + capability）
│   ├── 06-ipc-spec.md                  # IPC 子系统规范
│   ├── 07-rust-support-spec.md        # Rust 内核模块支持规范
│   └── 08-coding-standard-spec.md    # 编码规范与工程标准对照
├── 02-olk66-source-mapping/           # OLK-6.6 源码映射
│   ├── README.md                      # 索引
│   ├── 01-sched-ext-mapping.md        # sched_ext 源码 → AirymaxOS SCHED_AGENT
│   ├── 02-io-uring-mapping.md         # io_uring 源码 → AirymaxOS IPC
│   ├── 03-bpf-mapping.md              # eBPF 源码 → AirymaxOS 可编程扩展
│   ├── 04-mm-mapping.md               # 内存管理源码 → AirymaxOS MemoryRovol
│   └── 05-security-mapping.md         # 安全子系统源码 → AirymaxOS Cupolas
├── 03-microkernel-design-ref/         # 微内核设计参考
│   ├── README.md                      # 索引
│   ├── 01-sel4-reference.md           # seL4 微内核设计参考
│   ├── 02-zircon-reference.md         # Zircon 微内核设计参考
│   ├── 03-minix3-reference.md         # Minix3 微内核设计参考
│   └── 04-microkernel-strategy.md     # AirymaxOS 微内核化改造策略对照
├── 04-industry-best-practices/        # 行业最新理论与最佳实践
│   ├── README.md                      # 索引
│   ├── 01-latest-theory.md            # 2026 年最新微内核/OS 理论
│   ├── 02-best-practices.md           # 行业最佳实践汇总
│   └── 03-airymaxos-synthesis.md      # AirymaxOS 技术方案综合（Euler + 最新理论 → AirymaxOS）
├── agentrt-linux基本工程标准规范.md    # agentrt-linux 工程标准规范（1026 行）
└── agentrt-linux开发路线和进度.md      # agentrt-linux 开发路线与进度跟踪
```

---

## 3. 使用规范

### 3.1 何时参考本目录

AirymaxOS 开源设计文档（`docs/AirymaxAgentOS/`）的编写和修订流程：

1. **先参考 Euler**：查阅本目录 `01-openeuler-tech-reference/` 中对应子系统的 openEuler 技术规范
2. **再参考行业最新理论**：查阅 `04-industry-best-practices/` 中的最新理论和最佳实践
3. **最后形成 AirymaxOS 技术方案**：综合 Euler 参考 + 行业最新理论，形成 AirymaxOS 自己的技术方案
4. **开源文档输出**：在 `docs/AirymaxAgentOS/` 中编写开源文档，**严禁引用 openEuler**

### 3.2 开源/闭源隔离铁律

| 规则 | 说明 |
|------|------|
| **BAN-INTERNAL-001** | openEuler 技术规范参考内容**只能**存在于 `docs-closed/agentrt-linux/` 目录 |
| **BAN-INTERNAL-002** | 开源文档 `docs/AirymaxAgentOS/` 中**严禁**出现 "openEuler"、"open Euler"、"openeuler" 等描述 |
| **BAN-INTERNAL-003** | 闭源参考文档中的 openEuler 内容必须经过**消化吸收**后才能体现在开源设计文档中 |
| **BAN-INTERNAL-004** | 闭源参考文档**不对外发布**，不包含在任何开源 LICENSE 范围内 |
| **BAN-INTERNAL-005** | 开源文档中的技术方案表述必须用 **AirymaxOS 自身语言**，不能是 openEuler 的直接翻译 |

### 3.3 IRON-9 v2 代码共享原则下的参考方式

IRON-9 v2（同源且部分代码共享）下，openEuler 技术规范参考方式：

1. **共享契约层**（`include/airymax/`）：参考 openEuler 的 UAPI 接口设计规范，但不直接复制 openEuler 代码
2. **语义同源层**：参考 openEuler 的子系统实现思路（如 sched_ext 调度策略、io_uring 零拷贝机制），形成 AirymaxOS 自己的实现方案
3. **完全独立层**：AirymaxOS 专属机制（systemd 集成、Kbuild）独立设计，不参考 openEuler 对应实现

---

## 4. 与开源文档的关系

| 维度 | 闭源参考文档（本目录） | 开源设计文档（`docs/AirymaxAgentOS/`） |
|------|----------------------|--------------------------------------|
| 保密级别 | SPHARX Ltd 内部 | 开源（AGPL v3 + Apache 2.0） |
| openEuler 引用 | ✅ 允许，全面参考 | ❌ 严禁 |
| 技术深度 | 深度技术规范（源码级） | 设计方案级（架构 + 接口 + 数据流） |
| 编写语言 | 中文为主 | 中文为主 |
| 版本同步 | 与开源文档同步更新 | 与闭源参考文档同步更新 |

---

## 5. 文档清单（0.1.1 文档体系完成）

0.1.1 版本已完成全部闭源参考文档（26 个文件，~14,131 行）：

| 目录 | 文件数 | 行数 | 状态 |
|------|--------|------|------|
| 01-openeuler-tech-reference/ | 7 | 4,844 | ✅ 完成（6 子系统技术规范） |
| 02-olk66-source-mapping/ | 7 | 4,971 | ✅ 完成（6 子系统源码映射） |
| 03-microkernel-design-ref/ | 5 | 1,366 | ✅ 完成（seL4+Zircon+Minix3+改造策略） |
| 04-industry-best-practices/ | 4 | 918 | ✅ 完成（最新理论+最佳实践+技术方案综合） |
| 根级文档 | 3 | 2,032 | ✅ 完成（README+工程标准+开发路线） |
| **合计** | **26** | **14,131** | **✅ 全部完成** |

后续 1.0.1 开发阶段将随代码实施同步更新闭源参考文档。

---

## 6. 相关文档

- 开源设计文档：`docs/AirymaxAgentOS/README.md`（19 模块三层体系）
- 工程标准规范：`docs/AirymaxAgentOS/50-engineering-standards/README.md`（IRON-9 v2 定义）
- Airymax 架构原则：`docs/ARCHITECTURAL_PRINCIPLES.md`（五维正交 24 原则）
- agentrt 工程标准：`docs-closed/0.1.1工程标准规范手册.md`（17 类规则编号体系）

---

> **文档结束** | SPHARX Ltd 内部参考 | 闭源不公开
