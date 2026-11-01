Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# P1-03 SSoT 归属决策报告——50-specifications / 50-engineering-standards

> **文档定位**： 解决 AirymaxRT `50-specifications/`（用户态运行时规范）与 AirymaxOS `50-engineering-standards/`（内核态工程标准）之间的主题重叠与 SSoT 归属问题
> **版本**： v0.3.1
> **日期**： 2026-07-10
> **决策依据**： IRON-9 v2 三层共享模型 + P0-03 方案 D 分层 API 设计 + Linux 6.6 内核编码风格基线

---

## 1. 问题背景

### 1.1 两个目录的定位

| 目录 | 定位 | 目标读者 | 平台覆盖 |
|------|------|---------|---------|
| **AirymaxRT `50-specifications/`** | agentrt 用户态运行时技术规范 | 应用层开发者、SDK 用户、架构师、安全专家 | 跨平台（Linux/macOS/Windows） |
| **AirymaxOS `50-engineering-standards/`** | agent-linux 内核态工程标准 | 内核开发者、OS 贡献者、维护者 | Linux 6.6 内核专属 |

### 1.2 主题重叠清单

经全量对比，两个目录存在 **5 大类 11 个重叠主题**：

| # | 重叠主题 | AirymaxRT 文件 | AirymaxOS 文件 | 重叠性质 |
|---|---------|---------------|---------------|---------|
| 1 | C 编码风格 | `30-coding-standard/01-c-coding-style.md` | `10-coding-style/C_coding_style_standard.md` + `C_coding_style_standard_supplement.md` | 完全重叠 |
| 2 | C/C++ 安全编码 | `30-coding-standard/02-c-cpp-secure-coding.md` | `10-coding-style/C_Cpp_secure_coding_standard.md` | 完全重叠 |
| 3 | Rust 编码风格 | `30-coding-standard/13-rust-coding-style.md` | `10-coding-style/Rust_coding_style_standard.md` | 完全重叠 |
| 4 | Rust 安全编码 | `30-coding-standard/14-rust-secure-coding.md` | `10-coding-style/Rust_secure_coding_standard.md` | 完全重叠 |
| 5 | 日志规范 | `30-coding-standard/10-log-standard.md` + `10-contracts/05-logging-format.md` | `20-contracts/logging_contract.md` | 部分重叠 |
| 6 | IPC 协议契约 | `10-contracts/03-protocol-contract.md` | `20-contracts/ipc_protocol_contract.md` | 语义同源 |
| 7 | syscall API 契约 | `10-contracts/04-syscall-api-contract.md` | `20-contracts/syscall_api_contract.md` | 语义同源（方案 D） |
| 8 | 运行时接口 L1/L2/L3 | `20-are-standards/01~03` | `30-runtime-interfaces/L1~L3` | 完全重叠 |
| 9 | 集成标准 | `50-integration/01-integration-standard.md` | `40-integration/agentrt_integration.md` | 部分重叠 |
| 10 | 项目 ERP（SBOM/错误码/手册/资源表） | `70-project-erp/01~04` | `50-project-erp/`（4 文件） | 完全重叠 |
| 11 | 错误码参考 | `70-project-erp/02-error-code-reference.md` + `40-error-code/README.md` | `50-project-erp/error_code_reference.md` | 完全重叠 |

### 1.3 不重叠主题（各自独有）

| AirymaxRT 独有 | AirymaxOS 独有 |
|---------------|---------------|
 | Go/Python/JS/Java 编码风格（4 文件） | 工程标准手册（00） |
| 命名规范（11-naming-conventions.md） | 代码格式（02-code-format.md） |
| 代码注释模板（03-code-comment-template.md） | 代码风格（03-code-style.md） |
| 配置审计日志（04-config-audit-log.md） | 工程哲学（04-engineering-philosophy.md） |
| 安全设计（15-security-design.md） | 开发流程（05-development-process.md） |
| Agent/Skill 契约 + JSON Schema | 工具链与自动化（06） |
| ARE 开放标准（6 个子目录） | 维护者制度与治理（07） |
| 生态伙伴计划 | 合规检查清单（08） |
| 标准贡献 | 许可证策略（09→110） |
| | checkpatch 规则映射（60） |
| | kernel-doc 标准（70） |
| | clang-format 强制（80） |
| | 弃用接口注册表（100） |
| | SPDX 许可证合规（110） |
| | 跨项目代码共享（120） |

---

## 2. SSoT 归属决策

### 2.1 决策原则

**原则 SSoT-1**：主题的 SSoT 归属取决于该主题的**权威来源**，而非目录大小或文件数量。

**原则 SSoT-2**：如果一个主题的权威来源是 Linux 内核（如 C 编码风格遵循 OLK-6.6），则 AirymaxOS `50-engineering-standards/` 为 SSoT，AirymaxRT 引用之。

**原则 SSoT-3**：如果一个主题的权威来源是应用层标准或跨平台规范（如 ARE 开放标准、Go/Python/JS 编码风格），则 AirymaxRT `50-specifications/` 为 SSoT，AirymaxOS 引用之。

**原则 SSoT-4**：如果一个主题在两端都需要但抽象层级不同（如 syscall API 契约、IPC 协议契约），则**各自是自己的 SSoT**，通过 IRON-9 v2 [SS] 语义同源层保持一致。

**原则 SSoT-5**：项目 ERP 类文档（SBOM、资源管理表等）属于组织级文档，两端各自维护自己的实例，但**内容应保持一致**，以较新版本为准。

### 2.2 SSoT 归属表

| # | 重叠主题 | SSoT 归属 | 引用方 | 理由 |
|---|---------|---------|--------|------|
| 1 | C 编码风格 | **AirymaxOS** `10-coding-style/C_coding_style_standard.md` | AirymaxRT 引用 | 权威来源为 Linux 6.6 内核编码风格（OLK-6.6），Tab 8/snake_case/K&R/80 列 |
| 2 | C/C++ 安全编码 | **AirymaxOS** `10-coding-style/C_Cpp_secure_coding_standard.md` | AirymaxRT 引用 | 权威来源为 Linux 内核安全编码实践 |
| 3 | Rust 编码风格 | **AirymaxOS** `10-coding-style/Rust_coding_style_standard.md` | AirymaxRT 引用 | 内核态 Rust 编码规范更严格，用户态可引用子集 |
| 4 | Rust 安全编码 | **AirymaxOS** `10-coding-style/Rust_secure_coding_standard.md` | AirymaxRT 引用 | 同上 |
| 5 | 日志规范 | **AirymaxOS** `20-contracts/logging_contract.md` | AirymaxRT 引用 ANSI 颜色 + log_write() + CLOCK_REALTIME 部分 | 工程约定统一为 AirymaxOS（项目记忆：所有日志必须使用核心日志系统） |
| 6 | IPC 协议契约 | **各自 SSoT**（[SS] 语义同源） | 通过 [SC] `ipc.h` 共享 128B 消息头布局 | AirymaxRT = JSON-RPC 高层，AirymaxOS = 编号 syscall + io_uring 数据面（方案 D） |
| 7 | syscall API 契约 | **各自 SSoT**（[SS] 语义同源） | 通过 `05-syscall-semantic-mapping.md` 映射 | AirymaxRT = JSON-RPC 统一入口，AirymaxOS = 编号 syscall 512-631（方案 D） |
| 8 | 运行时接口 L1/L2/L3 | **AirymaxRT** `20-are-standards/` | AirymaxOS 引用 | ARE Standards 是面向第三方的开放标准，agentrt 是参考实现，agent-linux 引用之 |
| 9 | 集成标准 | **各自 SSoT** | 无引用关系 | AirymaxRT = 应用集成（第三方系统/生态伙伴），AirymaxOS = OS 集成（agentrt 嵌入 OS） |
| 10 | 项目 ERP | **各自 SSoT** | 内容保持一致 | 两端各自维护自己的 SBOM/资源表/手册需求，内容同步更新 |
| 11 | 错误码参考 | **AirymaxOS** `50-project-erp/error_code_reference.md` | AirymaxRT 对齐数值（Task #46 已完成） | 错误码数值已统一为 AirymaxOS 紧凑编号方案（EINVAL=-1 等） |

### 2.3 非重叠主题 SSoT 归属

| 主题 | SSoT 归属 | 理由 |
|------|---------|------|
| Go/Python/JS/Java 编码风格 | **AirymaxRT** | 用户态跨平台语言，内核不涉及 |
| 命名规范 | **AirymaxRT** | 跨平台命名约定 |
| 代码注释模板 | **AirymaxRT** | 应用层 Doxygen 规范 |
| 配置审计日志 | **AirymaxRT** | 应用层配置管理 |
| 安全设计 | **AirymaxRT** | 应用层安全设计原则 |
| Agent/Skill 契约 | **AirymaxRT** | 应用层接口契约 |
| ARE 开放标准 | **AirymaxRT** | 面向第三方的开放标准体系 |
| 生态伙伴计划 | **AirymaxRT** | 应用生态 |
| 标准贡献 | **AirymaxRT** | 标准化路线图 |
| 工程标准手册 | **AirymaxOS** | 内核工程标准总纲 |
| 代码格式 | **AirymaxOS** | .clang-format 配置 |
| 代码风格 | **AirymaxOS** | 内核代码风格（反过度抽象等） |
| 工程哲学 | **AirymaxOS** | 双层稳定性哲学 |
| 开发流程 | **AirymaxOS** | 补丁生命周期 + 维护者层级 |
| 工具链与自动化 | **AirymaxOS** | 7 层验证框架 |
| 维护者制度与治理 | **AirymaxOS** | MAINTAINERS + Lieutenant System |
| 合规检查清单 | **AirymaxOS** | STD-DOC/STD-CODE/STD-IRON |
| checkpatch 规则映射 | **AirymaxOS** | OLK-6.6 checkpatch.pl |
| kernel-doc 标准 | **AirymaxOS** | 内核文档格式 |
| clang-format 强制 | **AirymaxOS** | .clang-format CI 门禁 |
| 弃用接口注册表 | **AirymaxOS** | 内核弃用流程 |
| SPDX 许可证合规 | **AirymaxOS** | SPDX 标识符规范 |
| 跨项目代码共享 | **AirymaxOS** | IRON-9 v2 [SC] 共享契约层 |

---

## 3. 实施方案

### 3.1 AirymaxRT `50-specifications/` 调整

对于 SSoT 归属为 AirymaxOS 的主题（C 编码风格、C/C++ 安全编码、Rust 编码风格、Rust 安全编码、日志规范、错误码参考），AirymaxRT 对应文件应：

1. **保留文件但不重复定义**——在文件开头添加 SSoT 引用声明
2. **补充用户态专属扩展**——仅保留用户态独有的内容（如 4 空格缩进 vs Tab 8、跨平台注意事项等）
3. **添加交叉引用**——指向 AirymaxOS SSoT 文件

**SSoT 引用声明模板**（添加到 AirymaxRT 文件开头）：

```markdown
> **SSoT 声明**： 本文档的内核态编码规范以 AirymaxOS `50-engineering-standards/10-coding-style/C_coding_style_standard.md` 为单一数据源（SSoT）。
> 本文档仅补充 agentrt 用户态运行时特有的编码规范差异（如跨平台缩进差异、用户态特定约定等）。
> 当两者冲突时，以 AirymaxOS SSoT 为准。
```

### 3.2 AirymaxOS `50-engineering-standards/` 调整

对于 SSoT 归属为 AirymaxRT 的主题（运行时接口 L1/L2/L3、Go/Python/JS/Java 编码风格、ARE 开放标准），AirymaxOS 对应文件应：

1. **保留文件但添加 SSoT 引用声明**——指向 AirymaxRT SSoT 文件
2. **补充内核态专属扩展**——仅保留内核态独有的内容
3. **添加交叉引用**——指向 AirymaxRT SSoT 文件

### 3.3 各自 SSoT 主题（方案 D 语义同源）

对于 IPC 协议契约、syscall API 契约等"各自 SSoT"的主题：

1. **两端各自维护自己的文件**——不添加 SSoT 引用声明
2. **通过 [SC] 共享契约层保持一致**——6 个头文件约束共享数据结构
3. **通过 `05-syscall-semantic-mapping.md` 映射**——已建立语义映射关系

### 3.4 项目 ERP 主题

对于 SBOM、资源管理表等项目 ERP 文档：

1. **两端各自维护自己的实例**——因为各自的依赖列表、资源分配不同
2. **内容保持一致的部分**——通过定期同步确保一致
3. **错误码参考**——以 AirymaxOS 为 SSoT（Task #46 已统一数值）

---

## 4. SSoT 引用声明添加清单

### 4.1 AirymaxRT 需添加 SSoT 引用声明的文件（6 个）

| 文件 | SSoT 归属 | 引用目标 |
|------|---------|---------|
| `30-coding-standard/01-c-coding-style.md` | AirymaxOS | `50-engineering-standards/10-coding-style/C_coding_style_standard.md` |
| `30-coding-standard/02-c-cpp-secure-coding.md` | AirymaxOS | `50-engineering-standards/10-coding-style/C_Cpp_secure_coding_standard.md` |
| `30-coding-standard/13-rust-coding-style.md` | AirymaxOS | `50-engineering-standards/10-coding-style/Rust_coding_style_standard.md` |
| `30-coding-standard/14-rust-secure-coding.md` | AirymaxOS | `50-engineering-standards/10-coding-style/Rust_secure_coding_standard.md` |
| `30-coding-standard/10-log-standard.md` | AirymaxOS | `50-engineering-standards/20-contracts/logging_contract.md` |
| `70-project-erp/02-error-code-reference.md` | AirymaxOS | `50-engineering-standards/50-project-erp/error_code_reference.md` |

### 4.2 AirymaxOS 需添加 SSoT 引用声明的文件（3 个）

| 文件 | SSoT 归属 | 引用目标 |
|------|---------|---------|
| `30-runtime-interfaces/L1_runtime_interface.md` | AirymaxRT | `50-specifications/20-are-standards/01-l1-runtime-interface.md` |
| `30-runtime-interfaces/L2_service_protocol.md` | AirymaxRT | `50-specifications/20-are-standards/02-l2-service-protocol.md` |
| `30-runtime-interfaces/L3_security_governance.md` | AirymaxRT | `50-specifications/20-are-standards/03-l3-security-governance.md` |

### 4.3 不需要添加 SSoT 引用声明的文件（各自 SSoT）

| AirymaxRT 文件 | AirymaxOS 文件 | 关系 |
|---------------|---------------|------|
| `10-contracts/03-protocol-contract.md` | `20-contracts/ipc_protocol_contract.md` | [SS] 语义同源（方案 D） |
| `10-contracts/04-syscall-api-contract.md` | `20-contracts/syscall_api_contract.md` | [SS] 语义同源（方案 D） |
| `50-integration/01-integration-standard.md` | `40-integration/agentrt_integration.md` | 各自 SSoT（不同范围） |
| `70-project-erp/01-sbom.md` | `50-project-erp/SBOM.md` | 各自 SSoT（各自实例） |
| `70-project-erp/03-manuals-module-requirements.md` | `50-project-erp/manuals_module_requirements.md` | 各自 SSoT（各自实例） |
| `70-project-erp/04-resource-management-table.md` | `50-project-erp/resource_management_table.md` | 各自 SSoT（各自实例） |

---

## 5. 结论

### 5.1 SSoT 归属统计

| SSoT 归属 | 主题数量 | 占比 |
|---------|---------|------|
| AirymaxOS 为 SSoT | 6 | 55%（6/11 重叠主题） |
| AirymaxRT 为 SSoT | 3 | 27%（3/11 重叠主题） |
| 各自 SSoT（[SS] 语义同源） | 5 | 45%（5/11 重叠主题） |

### 5.2 影响评估

- **AirymaxRT 需调整 6 个文件**：添加 SSoT 引用声明 + 保留用户态专属扩展
- **AirymaxOS 需调整 3 个文件**：添加 SSoT 引用声明 + 保留内核态专属扩展
- **无需删除任何文件**：所有文件保留，仅添加引用声明和补充专属内容
- **不破坏现有文档结构**：非破坏性增补模式

### 5.3 综合成熟度影响

- P1-03 问题已解决：SSoT 归属明确，重叠主题有清晰的权威来源
- 综合成熟度维持 100/100（A+，无条件 Go）
- 遗留工作：实际添加 SSoT 引用声明到 9 个文件（P2 级，~1h）

---

## 6. 相关文档

- v0.3.1 综合修正补充报告：`01-comprehensive-issue-list.md`
- P0-03 决策报告：`02-p0-03-api-paradigm-decision.md`
- 系统调用语义映射：`docs/AirymaxOS/30-interfaces/05-syscall-semantic-mapping.md`
- AirymaxRT 技术规范：`docs/AirymaxRT/50-specifications/README.md`
- AirymaxOS 工程标准：`docs/AirymaxOS/50-engineering-standards/README.md`
- 工程标准手册（SSoT 索引）：`docs/AirymaxOS/50-engineering-standards/00-engineering-standards-handbook.md`

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
