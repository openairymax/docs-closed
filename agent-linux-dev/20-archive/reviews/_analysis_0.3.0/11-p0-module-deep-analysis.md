Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# Phase 3.2: P0 模块（60-120）深度审查与修复计划

> **文档定位**: agent-linux P0 优先级模块（60-driver-model 至 120-development-process 共 7 模块 20 文档）的系统性深度审查报告，识别草案级问题并制定修复计划
> **版本**: v0.3.0
> **日期**: 2026-07-09
> **审查范围**: `docs/AirymaxOS/{60,70,80,90,100,110,120}-*/` 全部 20 个 `.md` 文件
> **审查方法**: 自动化审计（Mermaid/IRON-9 v2/Copyright/五维原则）+ 深度人工阅读
> **参照标准**: 110-security/03-capability-model.md（1060 行，最完善文档）+ 90-observability/02-ebpf-probes.md（628 行，含完整 IRON-9 v2 标注）

---

## 1. 审计概览

### 1.1 模块文件清单

| 模块 | 文件数 | 总行数 | README 行数 | 主文档行数 |
|------|--------|--------|-------------|-----------|
| 60-driver-model | 3 | 1,159 | 159 | 500 + 500 |
| 70-build-system | 3 | 1,148 | 189 | 468 + 491 |
| 80-testing | 3 | 1,154 | 223 | 433 + 498 |
| 90-observability | 3 | 1,332 | 204 | 500 + 628 |
| 100-operations | 3 | 1,167 | 167 | 500 + 500 |
| 110-security | 4 | 2,259 | 203 | 499 + 497 + 1,060 |
| 120-development-process | 3 | 1,110 | 202 | 499 + 409 |
| **合计** | **22** | **9,329** | **1,347** | **7,982** |

### 1.2 合规性检查汇总

| 检查项 | 规则 | 合格 | 不合格 | 合格率 |
|--------|------|------|--------|--------|
| Copyright 头部 | STD-DOC-01 | 22/22 | 0 | 100% ✅ |
| Mermaid ≥2 | STD-DOC-07 | 15/15 | 0 | 100% ✅ |
| 五维原则引用 ≥1 | STD-DOC-08 | 22/22 | 0 | 100% ✅ |
| IRON-9 v2 [SC]/[SS]/[IND] | STD-DOC-03（仅 20-modules 强制） | 2/15 | 13/15 | 13% ⚠️ |

> **注**: STD-DOC-03 适用范围仅限 `20-modules/0[1-8]-*.md`（8 个子系统设计文档），60-120 模块不强制要求 IRON-9 v2 标注。但含有 agent-linux 专属扩展的文档**强烈建议**补充标注，以保持与 03-capability-model.md 和 02-ebpf-probes.md 的一致性。

### 1.3 IRON-9 v2 标注现状

| 文件 | SC | SS | IND | 状态 |
|------|----|----|-----|------|
| 90-observability/02-ebpf-probes.md | 12 | 7 | 6 | ✅ 完整 |
| 110-security/03-capability-model.md | 8 | 1 | 1 | ✅ 完整 |
| 其余 15 个主文档 | 0 | 0 | 0 | ❌ 缺失 |

---

## 2. 核心问题清单

### 2.1 P0 问题（阻断性，必须修复）

#### P0-01: 缺少 IRON-9 v2 三层标注（13 个文档）

**问题**: 13 个含有 agent-linux 专属扩展的主文档缺少 IRON-9 v2 [SC]/[SS]/[IND] 三层共享模型标注，导致与 agentrt 的同源映射关系不明确。

**影响文档**:
- 60-driver-model/01-device-model.md（Agent 驱动模型，与 agentrt daemons 同源）
- 60-driver-model/02-platform-driver.md（devm_ 扩展至智能体资源）
- 70-build-system/01-kbuild-system.md（agent-linux 子仓构建）
- 70-build-system/02-kconfig-system.md（CONFIG_AIRYMAX_* 配置项）
- 80-testing/01-kunit-framework.md（Agent 契约测试，与 agentrt 互操作）
- 80-testing/02-kselftest.md（Agent 行为测试）
- 90-observability/01-ftrace-framework.md（Agent 追踪，与 agentrt commons/trace 同源）
- 100-operations/01-deployment.md（agentrt 12 daemons 部署）
- 100-operations/02-configuration.md（/etc/agentrt/ 配置同源）
- 110-security/01-lsm-framework.md（Cupolas LSM 钩子）
- 110-security/02-landlock-sandbox.md（Agent 沙箱）
- 120-development-process/01-patch-lifecycle.md（子仓补丁流程）
- 120-development-process/02-maintainer-hierarchy.md（子仓维护者层级）

**修复方案**: 为每个文档在"五维原则映射"章节后新增"IRON-9 v2 三层共享模型"章节，参照 02-ebpf-probes.md §13 和 03-capability-model.md 的结构。

**修复模式**: 非破坏性增补——不修改现有正文，仅新增章节。

#### P0-02: 缺少具体 C 接口定义（多数文档）

**问题**: 多数文档以描述性文字为主，缺少：
- 完整的 struct 定义（字段、类型、注释）
- 函数签名（返回值、参数、错误码）
- 宏定义和枚举
- 具体代码示例（可编译级别）

**参照标准**: 03-capability-model.md 包含完整的 struct cnode、struct cte、struct mdb_node 定义和 7 种 cap 操作函数签名；02-ebpf-probes.md 包含完整的 BPF 程序代码示例。

**影响文档**: 全部 15 个主文档（除 02-ebpf-probes.md 和 03-capability-model.md 外）

**修复方案**: 在每个文档的相应章节增补接口定义表和代码示例。由于"不能随意大幅度删改设计文档"，采用**增补附录**方式——在文档末尾"文档结束"标记前新增"附录：接口定义"章节。

### 2.2 P1 问题（重大，应修复）

#### P1-01: 缺少状态机描述

**问题**: 多数文档缺少 Mermaid stateDiagram-v2 状态机描述，仅有 flowchart/graph 图。

**影响文档**:
- 60-driver-model/01-02（设备生命周期状态机缺失）
- 70-build-system/01-02（构建配置状态机缺失）
- 80-testing/01-02（测试套件生命周期状态机缺失）
- 100-operations/01-02（部署/配置状态机缺失）
- 110-security/01-02（LSM 钩子/Landlock 状态机缺失）
- 120-development-process/01-02（补丁状态机缺失）

**参照标准**: 02-ebpf-probes.md §10.3 包含 struct_ops 四状态机（INIT→INUSE→TOBEFREE→freed），03-capability-model.md 包含 capability 派生树状态。

**修复方案**: 在每个文档的相应章节增补 stateDiagram-v2 图。

#### P1-02: agent-linux 专属扩展内容不充分

**问题**: 部分文档内容偏向纯 Linux 内核文档复制，缺少 agent-linux 专属扩展的深度论述：
- 60-driver-model: Agent 虚拟设备驱动仅概念性描述，缺少 agent_driver_register() 完整签名和 Agent bus 匹配逻辑
- 70-build-system: 缺少 8 子仓的构建依赖图和交叉构建配置
- 80-testing: Agent 行为契约测试仅有示例代码片段，缺少完整测试矩阵
- 100-operations: agentrt 12 daemons 的 systemd 集成仅配置文件示例，缺少生命周期管理
- 110-security/01-02: LSM 和 Landlock 缺少与 Cupolas 的集成细节
- 120-development-process: 缺少 8 子仓的补丁流转路径

**修复方案**: 为每个文档增补"agent-linux 专属扩展深化"章节。

#### P1-03: 文档深度不一致

**问题**: 同一模块内文档深度差距大：
- 110-security: 01(499行) + 02(497行) vs 03(1060行) —— 03 是 01/02 的 2 倍
- 90-observability: 01(500行) vs 02(628行) —— 02 更完善（含 IRON-9 v2 §13）

**修复方案**: 为 01/02 文档增补接口定义和状态机章节，缩小与 03/02 的深度差距。

### 2.3 P2 问题（轻微，建议修复）

#### P2-01: 版本声明表述不一致

**问题**: 部分文档头部声明 "0.1.1（文档体系完成）/ 1.0.1（开发）"，但正文 §3.1 又说 "仅完成 README + 01 + 02"。C-2.8 已修复 140-190 模块的此类问题，但 60-120 模块仍存在。

**影响文档**: 全部 7 个 README.md 的 §3.1

**修复方案**: 统一为"0.1.1 完成 README + 01 + 02 文档，1.0.1 实施验证 + 完成全部 N 文档"。

#### P2-02: 前向引用标注不完整

**问题**: 90-observability 已在 C-2.8 修复前向引用标注（FIX-27/28），但其他模块的前向引用（引用 1.0.1 规划文档）可能未标注"（1.0.1 规划）"。

**修复方案**: 全量检查并补标。

---

## 3. 修复策略

### 3.1 修复原则

遵循用户确立的约束：

1. **非破坏性增补**: 不删除现有内容，不大幅度修改正文，仅增补新章节
2. **SSoT 对齐模式**: 参照 C-2.6 建立的三层结构（SSoT 声明 + 映射表 + 正文保留）
3. **参照标准一致**: 以 02-ebpf-probes.md 和 03-capability-model.md 为深度参照
4. **分优先级执行**: P0 先行 → P1 跟进 → P2 收尾

### 3.2 修复执行顺序

| 批次 | 修复项 | 文档数 | 优先级 | 预计工作量 |
|------|--------|--------|--------|-----------|
| Batch-1 | P0-01: IRON-9 v2 三层标注增补 | 13 | P0 | ~6h |
| Batch-2 | P0-02: 接口定义附录增补 | 15 | P0 | ~12h |
| Batch-3 | P1-01: 状态机图增补 | 12 | P1 | ~4h |
| Batch-4 | P1-02: 专属扩展深化章节 | 7 | P1 | ~8h |
| Batch-5 | P2-01/02: 版本声明与前向引用 | 7 | P2 | ~2h |
| **合计** | | | | **~32h** |

### 3.3 修复模板

#### IRON-9 v2 三层标注章节模板

每个文档在"五维原则映射"章节后新增：

```markdown
## N. IRON-9 v2 三层共享模型

### N.1 三层模型

| 层次 | 共享程度 | 本模块内容 |
|------|---------|-----------|
| **[SC] 共享契约层** | 完全共享代码 | `include/airymax/XXX.h`：... |
| **[SS] 语义同源层** | API 签名同源，实现独立 | ... |
| **[IND] 完全独立层** | 完全独立 | ... |

### N.2 跨态协作

（Mermaid 图展示 agentrt 用户态与 agent-linux 内核态的协作流）
```

#### 接口定义附录模板

每个文档在"文档结束"标记前新增：

```markdown
## 附录 A: 接口定义

### A.1 核心数据结构

（完整的 struct 定义，含字段注释）

### A.2 核心函数签名

（完整的函数签名，含参数说明和返回值）

### A.3 错误码

（完整的错误码枚举）
```

---

## 4. 逐模块问题详情

### 4.1 60-driver-model

#### 4.1.1 01-device-model.md（500 行）

| # | 行号 | 问题 | 严重度 | 修复方案 |
|---|------|------|--------|---------|
| 1 | 全文 | 缺少 IRON-9 v2 [SC]/[SS]/[IND] 标注 | P0 | 增补 IRON-9 v2 章节 |
| 2 | §4 | Agent 虚拟设备驱动缺少 agent_driver_register() 完整签名 | P0 | 增补接口定义附录 |
| 3 | §4 | agent_bus_type 匹配逻辑未展开 | P1 | 增补匹配算法描述 |
| 4 | 全文 | 缺少设备生命周期状态机 | P1 | 增补 stateDiagram-v2 |
| 5 | §11.2 | "一致性检查清单"仅为文字描述，缺少可执行脚本 | P2 | 增补检查脚本 |

#### 4.1.2 02-platform-driver.md（500 行）

| # | 行号 | 问题 | 严重度 | 修复方案 |
|---|------|------|--------|---------|
| 1 | 全文 | 缺少 IRON-9 v2 标注 | P0 | 增补 IRON-9 v2 章节 |
| 2 | §3 | devm_ 资源管理扩展至智能体资源仅有 API 名，缺签名 | P0 | 增补接口定义附录 |
| 3 | 全文 | 缺少 platform 驱动 probe/remove 状态机 | P1 | 增补 stateDiagram-v2 |

### 4.2 70-build-system

#### 4.2.1 01-kbuild-system.md（468 行）

| # | 行号 | 问题 | 严重度 | 修复方案 |
|---|------|------|--------|---------|
| 1 | 全文 | 缺少 IRON-9 v2 标注 | P0 | 增补 IRON-9 v2 章节 |
| 2 | 全文 | 缺少 8 子仓构建依赖图 | P0 | 增补构建依赖 Mermaid 图 |
| 3 | 全文 | 缺少交叉构建配置矩阵 | P1 | 增补配置矩阵表 |

#### 4.2.2 02-kconfig-system.md（491 行）

| # | 行号 | 问题 | 严重度 | 修复方案 |
|---|------|------|--------|---------|
| 1 | 全文 | 缺少 IRON-9 v2 标注 | P0 | 增补 IRON-9 v2 章节 |
| 2 | 全文 | 缺少 CONFIG_AIRYMAX_* 配置项完整清单 | P0 | 增补 Kconfig 定义附录 |
| 3 | 全文 | 缺少 Kconfig 状态机（y/m/n 选择逻辑） | P1 | 增补 stateDiagram-v2 |

### 4.3 80-testing

#### 4.3.1 01-kunit-framework.md（433 行）

| # | 行号 | 问题 | 严重度 | 修复方案 |
|---|------|------|--------|---------|
| 1 | 全文 | 缺少 IRON-9 v2 标注 | P0 | 增补 IRON-9 v2 章节 |
| 2 | §4 | Agent 行为契约测试仅有代码片段，缺完整测试矩阵 | P0 | 增补测试矩阵表 |
| 3 | 全文 | 缺少测试套件生命周期状态机 | P1 | 增补 stateDiagram-v2 |

#### 4.3.2 02-kselftest.md（498 行）

| # | 行号 | 问题 | 严重度 | 修复方案 |
|---|------|------|--------|---------|
| 1 | 全文 | 缺少 IRON-9 v2 标注 | P0 | 增补 IRON-9 v2 章节 |
| 2 | 全文 | 缺少 Agent 行为 kselftest 示例 | P0 | 增补代码示例 |
| 3 | 全文 | 缺少测试结果报告格式 | P1 | 增补报告模板 |

### 4.4 90-observability

#### 4.4.1 01-ftrace-framework.md（500 行）

| # | 行号 | 问题 | 严重度 | 修复方案 |
|---|------|------|--------|---------|
| 1 | 全文 | 缺少 IRON-9 v2 标注（02-ebpf-probes.md 已有，本文档缺失） | P0 | 增补 IRON-9 v2 章节 |
| 2 | §10 | Agent 追踪 instance 缺少完整事件格式定义 | P0 | 增补事件格式附录 |
| 3 | 全文 | 缺少 ftrace 启用/禁用状态机 | P1 | 增补 stateDiagram-v2 |

#### 4.4.2 02-ebpf-probes.md（628 行）

| # | 行号 | 问题 | 严重度 | 修复方案 |
|---|------|------|--------|---------|
| 1 | — | ✅ IRON-9 v2 标注完整（SC=12, SS=7, IND=6） | — | 无需修复 |
| 2 | — | ✅ Mermaid 图表充足（6 个） | — | 无需修复 |
| 3 | §13 | [SS] 语义同源层表中部分 API 映射可补充更多细节 | P2 | 可选增补 |

### 4.5 100-operations

#### 4.5.1 01-deployment.md（500 行）

| # | 行号 | 问题 | 严重度 | 修复方案 |
|---|------|------|--------|---------|
| 1 | 全文 | 缺少 IRON-9 v2 标注 | P0 | 增补 IRON-9 v2 章节 |
| 2 | §2 | agentrt 12 daemons 的 systemd 集成仅配置文件示例 | P0 | 增补生命周期管理章节 |
| 3 | 全文 | 缺少部署状态机（build→test→stage→deploy→rollback） | P1 | 增补 stateDiagram-v2 |

#### 4.5.2 02-configuration.md（500 行）

| # | 行号 | 问题 | 严重度 | 修复方案 |
|---|------|------|--------|---------|
| 1 | 全文 | 缺少 IRON-9 v2 标注 | P0 | 增补 IRON-9 v2 章节 |
| 2 | 全文 | 缺少 /etc/agentrt/ 配置文件完整清单和格式规范 | P0 | 增补配置规范附录 |
| 3 | 全文 | 缺少配置变更状态机 | P1 | 增补 stateDiagram-v2 |

### 4.6 110-security

#### 4.6.1 01-lsm-framework.md（499 行）

| # | 行号 | 问题 | 严重度 | 修复方案 |
|---|------|------|--------|---------|
| 1 | 全文 | 缺少 IRON-9 v2 标注（03-capability-model.md 已有） | P0 | 增补 IRON-9 v2 章节 |
| 2 | 全文 | LSM 钩子缺少完整函数签名列表 | P0 | 增补接口定义附录 |
| 3 | 全文 | 缺少 LSM 钩子注册/注销状态机 | P1 | 增补 stateDiagram-v2 |
| 4 | 全文 | 与 Cupolas 的集成仅概念性描述 | P1 | 增补集成细节章节 |

#### 4.6.2 02-landlock-sandbox.md（497 行）

| # | 行号 | 问题 | 严重度 | 修复方案 |
|---|------|------|--------|---------|
| 1 | 全文 | 缺少 IRON-9 v2 标注 | P0 | 增补 IRON-9 v2 章节 |
| 2 | 全文 | Landlock 权限模型缺少完整 struct 定义 | P0 | 增补接口定义附录 |
| 3 | 全文 | 缺少沙箱生命周期状态机 | P1 | 增补 stateDiagram-v2 |

#### 4.6.3 03-capability-model.md（1,060 行）

| # | 行号 | 问题 | 严重度 | 修复方案 |
|---|------|------|--------|---------|
| 1 | — | ✅ IRON-9 v2 标注存在（SC=8, SS=1, IND=1） | — | 无需修复 |
| 2 | — | ✅ Mermaid 图表充足（4 个） | — | 无需修复 |
| 3 | — | ✅ 内容深度充分（1060 行） | — | 参照标准 |
| 4 | §13 | [SS] 层仅 1 项，可补充更多 agentrt 同源 API 映射 | P2 | 可选增补 |

### 4.7 120-development-process

#### 4.7.1 01-patch-lifecycle.md（499 行）

| # | 行号 | 问题 | 严重度 | 修复方案 |
|---|------|------|--------|---------|
| 1 | 全文 | 缺少 IRON-9 v2 标注 | P0 | 增补 IRON-9 v2 章节 |
| 2 | 全文 | 缺少 8 子仓补丁流转路径图 | P0 | 增补子仓补丁流 Mermaid 图 |
| 3 | 全文 | 缺少补丁状态机（draft→review→merge→release） | P1 | 增补 stateDiagram-v2 |

#### 4.7.2 02-maintainer-hierarchy.md（409 行）

| # | 行号 | 问题 | 严重度 | 修复方案 |
|---|------|------|--------|---------|
| 1 | 全文 | 缺少 IRON-9 v2 标注 | P0 | 增补 IRON-9 v2 章节 |
| 2 | 全文 | 缺少 8 子仓维护者层级矩阵 | P0 | 增补维护者矩阵表 |
| 3 | 全文 | 缺少维护者晋升/降级状态机 | P1 | 增补 stateDiagram-v2 |

---

## 5. 修复执行计划

### 5.1 Batch-1: IRON-9 v2 三层标注增补（P0，~6h）

对 13 个缺少 IRON-9 v2 标注的文档，在"同源 agentrt 映射"章节末尾增补"IRON-9 v2 三层共享模型"子章节（非破坏性增补，不修改现有章节编号和目录）。

**执行方式**：在"同源 agentrt 映射"章节最后一段后、`---` 分隔符前，插入 `### N.1 IRON-9 v2 三层共享模型` 子章节。每个子章节包含 5 个部分：(1) 三层模型概览表 (2) [SC] 共享契约层 C 代码 (3) [SS] 语义同源层对照表 (4) [IND] 完全独立层表 (5) 跨态协作流 Mermaid 图。

**执行进度**（2026-07-10，全部完成 ✅）:

| # | 文档 | 子章节编号 | [SC] 头文件 | 处理者 | 状态 |
|---|------|-----------|------------|--------|------|
| 1 | 110-security/01-lsm-framework.md | §11.1 | security_types.h | 助手 | ✅ |
| 2 | 110-security/02-landlock-sandbox.md | §11.1 | security_types.h | Agent A | ✅ |
| 3 | 60-driver-model/01-device-model.md | §8.2¹ | sched.h（间接） | Agent A | ✅ |
| 4 | 60-driver-model/02-platform-driver.md | §9.2² | sched.h（间接） | Agent A | ✅ |
| 5 | 80-testing/01-kunit-framework.md | §11.2³ | 无 | Agent B | ✅ |
| 6 | 80-testing/02-kselftest.md | §9.2 | 无 | Agent B | ✅ |
| 7 | 90-observability/01-ftrace-framework.md | §12.1 | ipc.h | Agent B | ✅ |
| 8 | 100-operations/01-deployment.md | §13.3⁴ | sched.h + ipc.h | Agent C | ✅ |
| 9 | 100-operations/02-configuration.md | §12.3⁴ | sched.h + ipc.h | Agent C | ✅ |
| 10 | 70-build-system/01-kbuild-system.md | §8.1 | 无 | Agent B | ✅ |
| 11 | 70-build-system/02-kconfig-system.md | §9.1 | 无 | Agent B | ✅ |
| 12 | 120-development-process/01-patch-lifecycle.md | §13.2⁴ | 无 | Agent C | ✅ |
| 13 | 120-development-process/02-maintainer-hierarchy.md | §10.2⁴ | 无 | Agent C | ✅ |

> 编号适配说明：¹ 原 §8.2 重编号为 §8.3；² 原 §9.2 重编号为 §9.3；³ 因已有 §11.1；⁴ 因已有 §N.1/§N.2。

**验证结果**（自动化检查，2026-07-10）：13/13 文档均通过 IRON-9 v2 三层标注检查，每个文档的 [SC]/[SS]/[IND] 标注数量合理（SC 4-9 / SS 3-6 / IND 2-5），Mermaid 图数量 3-5，与参照模板 02-ebpf-probes.md §13（SC=12/SS=7/IND=6）和 03-capability-model.md §12 保持结构一致性。

**Batch-1 完成时间**：2026-07-10

### 5.2 Batch-2: 接口定义附录增补（P0，~12h）

对 13 个缺少接口定义的主文档（排除参照标准 02-ebpf-probes.md 和 03-capability-model.md），在"文档版本与维护"章节后、`---` 分隔符 + `> **文档结束**` 标记前，新增 `## 附录 A: 接口定义` 章节。

**执行方式**：非破坏性增补，不修改现有章节编号和目录，仅在文档末尾追加附录。每个附录包含 3 个标准部分（参照 03-capability-model.md §2-§9 的深度标准）：
- A.1 核心数据结构（完整的 struct 定义，含字段注释、`__attribute__` 对齐）
- A.2 核心函数签名（完整的函数签名，含 `@param`/`@return`/`@since` 文档注释）
- A.3 错误码与宏定义（完整的错误码枚举、CONFIG_* 宏、操作码常量）

**13 个文档的接口定义附录内容大纲**：

| # | 文档 | A.1 核心数据结构 | A.2 核心函数签名 | A.3 错误码与宏 |
|---|------|-----------------|-----------------|---------------|
| 1 | 60-driver-model/01-device-model.md | device, device_driver, bus_type, class | device_register/driver_register/bus_register, probe/remove | BUS_NOTIFY_*, DEVICE_ERR_* |
| 2 | 60-driver-model/02-platform-driver.md | platform_device, platform_driver, of_device_id | platform_driver_register, devm_platform_ioremap_resource | PLATFORM_DEVID_*, devm_* |
| 3 | 70-build-system/01-kbuild-system.md | build_target, kbuild_module, obj_config | if_changed, filechk, build_target_compile | obj-y/m/n 三态, KBUILD_* |
| 4 | 70-build-system/02-kconfig-system.md | kconfig_symbol, kconfig_entry, choice_entry | kconfig_parse, config_validate, menuconfig | CONFIG_AIRYMAX_* 完整清单 |
| 5 | 80-testing/01-kunit-framework.md | kunit_suite, kunit_case, kunit_resource | kunit_test_suite, kunit_run_suite | KUNIT_EXPECT_*/ASSERT_* 宏 |
| 6 | 80-testing/02-kselftest.md | kselftest_module, test_result, test_status | kselftest_run, TEST_PROGS 注册 | KSFT_*, TAP 13 格式 |
| 7 | 90-observability/01-ftrace-framework.md | trace_array, trace_buffer, tracer, trace_event | trace_array_create/destroy, tracing_on/off | TRACE_ITER_*, TRACE_TYPE_* |
| 8 | 100-operations/01-deployment.md | rpm_spec, systemd_unit, daemon_config | rpm_build, systemd_install, daemon_start | SYSTEMD_*, DAEMON_* 错误码 |
| 9 | 100-operations/02-configuration.md | config_schema, sysctl_entry, config_layer | config_validate, config_apply, sysctl_set | CONFIG_*, SYSCTL_* 参数清单 |
| 10 | 110-security/01-lsm-framework.md | security_hook_heads, security_hook_list, lsm_blob_sizes, cupolas_*_security | security_add_hooks, security_init, cupolas_init | LSM_HOOK 宏, LSM_ORDER_*, LSM_FLAG_* |
| 11 | 110-security/02-landlock-sandbox.md | landlock_ruleset, landlock_rule, landlock_object, landlock_blob | landlock_create_ruleset, landlock_add_rule, landlock_restrict_self | LANDLOCK_*, LANDLOCK_ACCESS_* |
| 12 | 120-development-process/01-patch-lifecycle.md | patch_stage, patch_metadata, pr_template | patch_validate, pr_create, stage_transition | PATCH_STAGE_*, PR_STATUS_* |
| 13 | 120-development-process/02-maintainer-hierarchy.md | maintainer_entry, contributor_level, dco_signoff | maintainers_parse, level_promote, dco_validate | MAINTAINERS_* 字段, LEVEL_0-5 枚举 |

**执行进度**（2026-07-10，全部完成 ✅）:

| # | 文档 | 处理者 | 附录行数 | struct 数 | 函数数 | 宏数 | 状态 |
|---|------|--------|---------|----------|--------|------|------|
| 1 | 110-security/01-lsm-framework.md | 助手 | ~430 | 6 | 5 | 6 部分 | ✅ |
| 2 | 110-security/02-landlock-sandbox.md | Agent D | 591 | 5 | 7 | 7 部分 | ✅ |
| 3 | 60-driver-model/01-device-model.md | Agent D | 610 | 5 | 7 | 5 部分 | ✅ |
| 4 | 60-driver-model/02-platform-driver.md | Agent D | 624 | 4 | 5 | 5 部分 | ✅ |
| 5 | 70-build-system/01-kbuild-system.md | Agent E | 326 | 4 | 2+2 | 10 | ✅ |
| 6 | 70-build-system/02-kconfig-system.md | Agent E | 350 | 4 | 5 | 28 | ✅ |
| 7 | 80-testing/01-kunit-framework.md | Agent E | 386 | 5 | 4 | 42 | ✅ |
| 8 | 80-testing/02-kselftest.md | Agent E | 373 | 3 | 11 | 22 | ✅ |
| 9 | 90-observability/01-ftrace-framework.md | Agent E | 489 | 6 | 11 | 48 | ✅ |
| 10 | 100-operations/01-deployment.md | Agent F | 511 | 6 | 8 | 58 | ✅ |
| 11 | 100-operations/02-configuration.md | Agent F | 459 | 6 | 7 | 69 | ✅ |
| 12 | 120-development-process/01-patch-lifecycle.md | Agent F | 489 | 5 | 7 | 52 | ✅ |
| 13 | 120-development-process/02-maintainer-hierarchy.md | Agent F | 540 | 6 | 7 | 57 | ✅ |

**验证结果**（自动化检查，2026-07-10）：13/13 文档均通过接口定义附录检查，每个文档的附录包含完整的 A.1 核心数据结构 / A.2 核心函数签名 / A.3 错误码与宏定义三部分，文档结束标记保持唯一。各文档总行数从原来的 ~500 行扩展到 874-1196 行（增量 50%-120%），达到与参照标准 03-capability-model.md（1060 行）相当的深度。

**Batch-2 完成时间**：2026-07-10

### 5.3 Batch-3: 状态机图增补（P1，~4h）

对 12 个缺少状态机的文档，在相应章节末尾增补 `stateDiagram-v2` 状态机图。参照 02-ebpf-probes.md §10.3 的 struct_ops 四状态机（INIT→INUSE→TOBEFREE→freed）和 03-capability-model.md §5.1 的 capability 令牌状态机。

**执行方式**：非破坏性增补，在相关章节末尾插入 `stateDiagram-v2` 代码块，不修改现有章节编号。

**12 个文档的状态机内容大纲**：

| # | 文档 | 状态机主题 | 状态转换路径 |
|---|------|-----------|-------------|
| 1 | 60-driver-model/01-device-model.md | 设备生命周期 | UNBOUND→PROBING→BOUND→UNBINDING→UNBOUND |
| 2 | 60-driver-model/02-platform-driver.md | probe/remove 生命周期 | UNBOUND→PROBING→BOUND→REMOVING→UNBOUND |
| 3 | 70-build-system/01-kbuild-system.md | 构建流程 | UNCONFIGURED→CONFIGURING→CONFIGURED→BUILDING→BUILT/FAILED |
| 4 | 70-build-system/02-kconfig-system.md | Kconfig 三态 | UNSET→y/m/n（depends on 检查→select 强制→choice 互斥） |
| 5 | 80-testing/01-kunit-framework.md | 测试套件生命周期 | INIT→RUNNING→PASSED/FAILED/SKIPPED→CLEANUP |
| 6 | 80-testing/02-kselftest.md | kselftest 执行 | DISCOVERED→COMPILED→RUNNING→PASS/FAIL/SKIP→REPORTED |
| 7 | 100-operations/01-deployment.md | 部署生命周期 | BUILD→TEST→STAGE→DEPLOY→VERIFIED/ROLLBACK |
| 8 | 100-operations/02-configuration.md | 配置变更 | DRAFT→VALIDATING→VALIDATED→APPLYING→APPLIED/ROLLED_BACK |
| 9 | 110-security/01-lsm-framework.md | LSM 钩子注册 | UNREGISTERED→REGISTERING→ACTIVE→UNREGISTERING→UNREGISTERED |
| 10 | 110-security/02-landlock-sandbox.md | Landlock 沙箱 | UNRESTRICTED→RULESET_CREATED→RESTRICTED→RELEASED |
| 11 | 120-development-process/01-patch-lifecycle.md | 补丁阶段 | DESIGN→EARLY_REVIEW→WIDER_REVIEW→MAINLINE→STABLE→LTS |
| 12 | 120-development-process/02-maintainer-hierarchy.md | 贡献者晋升 | L0(Contributor)→L1(Reviewer)→L2(Maintainer)→L3(Subsys)→L4(Core)→L5(Emeritus) |

**执行进度**（2026-07-10，全部完成 ✅）:

| # | 文档 | 状态机插入位置 | 状态数 | 转换表行数 | 处理者 | 状态 |
|---|------|--------------|--------|-----------|--------|------|
| 1 | 110-security/01-lsm-framework.md | §5.3 LSM 钩子注册/注销 | 9 | 9 | 助手 | ✅ |
| 2 | 60-driver-model/01-device-model.md | §3.4 设备生命周期 | 6 | 10 | Agent G | ✅ |
| 3 | 60-driver-model/02-platform-driver.md | §2.5 platform driver probe/remove | 5 | 8 | Agent G | ✅ |
| 4 | 70-build-system/01-kbuild-system.md | §6.1 构建目标生命周期 | 7 | 11 | Agent G | ✅ |
| 5 | 70-build-system/02-kconfig-system.md | §2.6 Kconfig 三态选择 | 5 | 12 | Agent G | ✅ |
| 6 | 80-testing/01-kunit-framework.md | §5.4 测试套件生命周期 | 6 | 10 | Agent H | ✅ |
| 7 | 80-testing/02-kselftest.md | §3.3 kselftest 执行 | 8 | 12 | Agent H | ✅ |
| 8 | 110-security/02-landlock-sandbox.md | §7.4 Landlock 沙箱生命周期 | 4 | 8 | Agent H | ✅ |
| 9 | 100-operations/01-deployment.md | §10.4 部署生命周期 | 9 | 14 | Agent I | ✅ |
| 10 | 100-operations/02-configuration.md | §8.3 配置变更生命周期 | 7 | 10 | Agent I | ✅ |
| 11 | 120-development-process/01-patch-lifecycle.md | §9.4 补丁生命周期 | 7 | 11 | Agent I | ✅ |
| 12 | 120-development-process/02-maintainer-hierarchy.md | §7.4 贡献者晋升 | 6 | 11 | Agent I | ✅ |

**汇总**：12/12 文档全部完成，共新增 12 个状态机子章节，合计 79 个状态、126 行转换条件表。所有状态机均使用 `stateDiagram-v2` 语法，含 (1) 一句话描述 (2) stateDiagram-v2 代码块（含状态/转换/note）(3) 状态转换条件表格（从状态/到状态/触发条件/系统行为 四列）。状态名均使用纯英文 ASCII（如 UNBOUND/PROBING/BOUND/PROBE_FAILED/UNBINDING/REMOVING 等），引用真实 Linux 内核 API 与 agent-linux 规则编号。

**Batch-3 完成时间**：2026-07-10

### 5.4 Batch-4: 专属扩展深化（P1，~8h）

对 7 个模块的 agent-linux 专属扩展内容进行深化。参照 P1-02 问题清单，各模块专属扩展深化要点：

| # | 模块 | 专属扩展深化要点 | 目标行数增量 |
|---|------|----------------|-------------|
| 1 | 60-driver-model | Agent 虚拟设备驱动：agent_driver_register() 完整签名 + Agent bus 匹配逻辑 + agent_device 结构定义 | +80 行 |
| 2 | 70-build-system | 8 子仓构建依赖图（Mermaid）+ 交叉构建配置矩阵表 | +60 行 |
| 3 | 80-testing | Agent 行为契约测试完整矩阵（Agent × 行为 × 预期结果） | +70 行 |
| 4 | 100-operations | agentrt 12 daemons 的 systemd 生命周期管理（启动/停止/重载/依赖排序/崩溃恢复） | +80 行 |
| 5 | 110-security/01 | LSM 与 Cupolas 集成细节（钩子映射表 + 策略下发流程 + 审计事件格式） | +60 行 |
| 6 | 110-security/02 | Landlock 与 Cupolas 集成细节（域叠加顺序 + 访问掩码合并算法） | +60 行 |
| 7 | 120-development-process | 8 子仓补丁流转路径图 + 跨仓依赖排序算法 | +70 行 |

**执行方式**：在对应模块的"agent-linux 专属扩展"章节或"同源 agentrt 映射"章节后增补深化内容，不修改现有章节编号。

**执行进度**（2026-07-10，全部完成 ✅）:

| # | 模块 | 深化内容 | 增补位置 | 新增规则 | 行数增量 | 处理者 | 状态 |
|---|------|---------|---------|---------|---------|--------|------|
| 1 | 60-driver-model/01 | agent_device 结构 + agent_driver_register() 签名 + agent_bus_match 逻辑 + 生命周期图 | §8.4 | OS-DRV-016~018 | +162 行 | 助手 | ✅ |
| 2 | 70-build-system/01 | 8 子仓构建依赖图 + 交叉构建配置矩阵 | §8.2 | OS-BUILD-013~016 | +77 行 | Agent J | ✅ |
| 3 | 80-testing/01 | Agent 行为契约测试矩阵（4 角色 × 8 行为 = 32 用例） | §11.3 | OS-TST-013~016 | +153 行 | Agent K | ✅ |
| 4 | 100-operations/01 | 12 daemons systemd 生命周期管理 + 崩溃恢复 + target 依赖 | §13.4 | OS-OPS-025~028 | +114 行 | Agent K | ✅ |
| 5 | 110-security/01 | LSM ↔ Cupolas 7 子系统钩子映射 + 策略下发 + 审计事件格式 | §11.2 | OS-SEC-008~011 | +63 行 | Agent L | ✅ |
| 6 | 110-security/02 | Landlock L0/L1/L2 三层域叠加 + 访问掩码交集合并算法 | §11.2 | OS-SEC-012~015 | +78 行 | Agent L | ✅ |
| 7 | 120-development-process/01 | 8 子仓补丁流转路径图 + 跨仓依赖排序算法 + submodule 触发 | §13.3 | OS-DEV-191~194 | +79 行 | Agent J | ✅ |

**汇总**：7/7 模块全部完成，共新增 7 个深化子章节，合计 26 条新规则（OS-DRV-016~018 + OS-BUILD-013~016 + OS-TST-013~016 + OS-OPS-025~028 + OS-SEC-008~015 + OS-DEV-191~194），总行数增量约 +726 行。所有增补均采用非破坏性模式，在 IRON-9 v2 章节后插入新子章节，未修改任何现有章节编号。深化内容涵盖：Agent 虚拟设备驱动完整结构体与匹配逻辑、8 子仓构建依赖与交叉构建矩阵、Agent 行为契约 32 用例测试矩阵、12 daemons systemd 生命周期与崩溃恢复、LSM ↔ Cupolas 钩子映射与审计事件、Landlock 域叠加与掩码合并算法、8 子仓补丁流转与跨仓依赖排序。

**Batch-4 完成时间**：2026-07-10

### 5.5 Batch-5: 版本声明与前向引用修复（P2，~2h）

统一版本声明表述，补标前向引用。

**7 个 README.md 版本声明统一**：将 §3.1 中"仅完成 README + 01 + 02"统一为"0.1.1 完成 README + 01 + 02 文档（N 文档奠基）+ 明确剩余文档范围 + 1.0.1 完成剩余 + 代码级验证"格式。

**执行进度**（2026-07-10，全部完成 ✅）:

| # | 文档 | §3.1 统一后表述 | §3.2 统一后表述 | 文档结束行 | 状态 |
|---|------|----------------|----------------|-----------|------|
| 1 | 60-driver-model/README.md | "0.1.1 完成 README + 01 + 02 文档（3 文档奠基）...其余 5 文档（03-devm-resource 至 07-driver-testing）在 1.0.1 版本完成" | "完成剩余 5 文档...进行代码级验证" | 无需修改 | ✅ |
| 2 | 70-build-system/README.md | "0.1.1 完成 README + 01 + 02 文档（3 文档奠基）...其余 6 文档（03-makefile-patterns 至 08-build-reproducibility）在 1.0.1 版本完成" | "完成剩余 6 文档...进行代码级验证" | 无需修改 | ✅ |
| 3 | 80-testing/README.md | "0.1.1 完成 README + 01 + 02 文档（3 文档奠基）...其余 8 文档（03-kernel-selftests 至 10-formal-verification）在 1.0.1 版本完成" | "完成剩余 8 文档...进行代码级验证" | 无需修改 | ✅ |
| 4 | 90-observability/README.md | "0.1.1 完成 README + 01 + 02 文档（3 文档奠基）...其余 7 文档（03-perf-analysis 至 09-memory-monitoring）在 1.0.1 版本完成" | "完成剩余 7 文档...进行代码级验证" | 无需修改 | ✅ |
| 5 | 100-operations/README.md | "0.1.1 完成 README + 01 + 02 文档（3 文档奠基）...其余 8 文档（03-monitoring 至 10-devstation）在 1.0.1 版本完成" | "完成剩余 8 文档...进行代码级验证" | 无需修改 | ✅ |
| 6 | 110-security/README.md | "0.1.1 完成 README + 01 + 02 + 03 文档（4 文档奠基）...其余 6 文档（04-module-signing 至 09-cryptography-compliance）在 1.0.1 版本完成" | "完成剩余 6 文档...进行代码级验证" | "0.1.1 P0 优先完成 README + 01 + 02 + 03"（从 01+02 修正为 01+02+03） | ✅ |
| 7 | 120-development-process/README.md | "0.1.1 完成 README + 01 + 02 文档（3 文档奠基）...其余 7 文档（03-pull-requests 至 09-release-process）在 1.0.1 版本完成" | "完成剩余 7 文档...进行代码级验证" | 无需修改 | ✅ |

**前向引用补标**：对 13 个主文档（01-*.md 和 02-*.md）执行全量 grep 检查，搜索 `1.0.1`、`(03-*.md)`、`(04-*.md)` 等前向引用模式。结果：13 个主文档中均无未标注的前向引用（主文档正文中未直接引用未创建的文档文件），前向引用问题主要存在于 README 文件中（已在 §3.1/§3.2 修复中覆盖）。

**Batch-5 完成时间**：2026-07-10

---

## 6. 后续工作

### 6.1 与 Phase 3.3 的协同

Phase 3.2 完成后，Phase 3.3 将审查核心设计层（00/10/20/30/40）。核心设计层文档质量已确认较高（ADR-012/013/014 已集成），但仍需检查：
- 30-interfaces 的接口定义完整性
- 40-dataflows 的数据流图一致性
- 20-modules 的 C-2.7 审查结果落地

### 6.2 与 1.0.1 开发阶段的衔接

Batch-1~5 的修复均为 0.1.1 文档体系完善工作，不涉及代码实施。1.0.1 开发阶段将：
1. 根据 Batch-2 的接口定义附录编写代码
2. 根据 Batch-3 的状态机图实现状态转换逻辑
3. 根据 Batch-4 的专属扩展深化实现 agent-linux 专属功能

---

## 7. 参照标准摘要

### 7.1 02-ebpf-probes.md 的 IRON-9 v2 结构（参照模板）

```
## 第 13 章 IRON-9 v2 三层共享模型落地

### 13.1 三层共享模型
| 层次 | 共享程度 | eBPF 内容 |
| [SC] | 完全共享代码 | include/airymax/bpf_struct_ops.h |
| [SS] | API 签名同源 | struct_ops 注册宏模式、bpf_prog 生命周期 |
| [IND] | 完全独立 | JIT 后端、trampoline、verifier |

### 13.2 [SC] 共享契约层
（完整 C 代码定义）

### 13.3 [SS] 语义同源层
（agentrt 用户态 vs agent-linux 内核态 对照表）

### 13.4 [IND] 完全独立层
（独立实现清单表）

### 13.5 跨态协作流
（Mermaid graph 图）
```

### 7.2 03-capability-model.md 的深度标准

- 1,060 行（其他文档 ~500 行的 2 倍）
- 包含完整的 struct cnode/cte/mdb_node 定义
- 包含 7 种 cap 操作函数签名
- 包含 capability 派生树状态图
- 包含 IRON-9 v2 [SC] 层 C 代码定义
- 包含策略裁决 4 值枚举

---

> **报告结束** | Phase 3.2 P0 模块深度审查 | v0.3.0 | 2026-07-09 | 闭源不公开
