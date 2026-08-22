Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 微内核思想来源收紧分析报告（仅 seL4）

> **文档定位**: agent-linux 微内核核心思想来源收紧为仅 seL4 的系统性分析与审查报告
> **报告日期**: 2026-07-09
> **报告版本**: v0.3.0
> **决策依据**: ADR-014（微内核设计思想来源单一化——仅 seL4）
> **机密级别**: 闭源不公开

---

## 1. 分析背景

### 1.1 决策要求

用户决策（2026-07-09）：严格确定 agent-linux 的微内核核心思想**仅来源于 seL4**（参考 `/home/spharx/SpharxWorks/01Reference/seL4-master`），不引入其他微内核架构（Zircon / Minix3），以避免工程思想在哲学和逻辑学层面的多元化冲突。

### 1.2 分析范围

- 公开方案文档：`docs/AirymaxOS/` 全部微内核相关内容
- 闭源参考文档：`docs-closed/agent-linux/` 全部微内核相关内容
- seL4 最新技术资料检索（2026）

### 1.3 分析方法

1. **全文检索**：在公开和闭源文档中搜索 "Zircon"、"Minix3"、"Minix" 关键词
2. **上下文分析**：逐一审查每处引用的上下文，判断是否违反"仅 seL4"原则
3. **seL4 最新技术整合**：检索 seL4 2026 年最新技术进展
4. **修复方案制定**：对每处违规引用制定具体修复方案

---

## 2. 当前状态分析

### 2.1 公开方案文档状态（docs/AirymaxOS/）

**状态**: ✅ 已实现 seL4 唯一来源

| 文件 | 状态 | 说明 |
|------|------|------|
| `10-architecture/03-microkernel-strategy.md` | ✅ seL4 唯一 | 明确标注"seL4（唯一来源，ADR-014）" |
| `10-architecture/05-adrs.md` | ✅ ADR-014 已记录 | 明确"微内核设计思想来源单一化（仅 seL4，不引入 Zircon/Minix3）" |

### 2.2 闭源参考文档状态（docs-closed/agent-linux/）

**状态**: ⚠️ 仍引用 Zircon + Minix3，与 ADR-014 不一致

**违规位置清单**：

| 编号 | 文件 | 行号 | 违规内容 | 违规类型 |
|------|------|------|----------|----------|
| V-01 | `03-microkernel-design-ref/04-microkernel-strategy.md` | L6 | `theory_source: seL4 + Zircon + Minix3 综合对照` | YAML 元数据 |
| V-02 | 同上 | L18 | `**理论来源**：seL4 + Zircon + Minix3 综合对照` | 正文声明 |
| V-03 | 同上 | L89-100 | 三代微内核横向对比表（含 Zircon/Minix3 列） | 对比表 |
| V-04 | 同上 | L94 | "参考 Zircon 的 devhost 设计" | 设计参考 |
| V-05 | 同上 | L137 | "seL4 root task + Zircon component" | 设计参考 |
| V-06 | 同上 | L370 | "充分吸收 seL4 的安全模型、Zircon 的现代内核设计、Minix3 的可靠性工程" | 总结 |

### 2.3 不一致性根因分析

**根因**: 闭源参考文档（`04-microkernel-strategy.md`）创建于 2026-07-07，当时设计决策尚未收紧为 seL4 唯一来源。2026-07-09 用户确立 ADR-014（seL4 唯一）后，公开文档已同步更新，但闭源参考文档未同步更新。

---

## 3. seL4 最新技术调研（2026）

### 3.1 seL4 版本演进

| 版本 | 发布日期 | 关键特性 |
|------|----------|----------|
| seL4 13.0.x | 2024 | MCS 调度稳定、RISC-V 64 位支持 |
| seL4 14.0.x | 2025 | 动态内存对象、改进的 x86 VT-d 支持 |
| seL4 15.0.0 | 2026-03-31 | **BREAKING 版本**：runtime domain schedule（RFC-20）、MCS 调度增强、线程本地 IPC buffer 可选 |

### 3.2 seL4 15.0.0 关键变化

1. **Runtime Domain Schedule（RFC-20）**：运行时可配置的域调度，支持动态安全策略调整
2. **MCS（Mixed-Criticality Systems）调度**：capability-authorised 时间访问，确保高关键度任务时间预算
3. **线程本地 IPC Buffer 可选**：减少内存占用，适配嵌入式场景
4. **代码规模**：~10-12 kSLOC，维持 Liedtke minimality principle

### 3.3 seL4 核心设计原则（2026 最新）

| 原则 | 内涵 | agent-linux 借鉴方式 |
|------|------|------------------------|
| Liedtke minimality | 微内核只保留无法在用户空间高效实现的最小原语集 | corekern/ 仅 4 原子机制（ES-SEL4-1） |
| Capability 单一模型 | 所有权限通过 capability 令牌表达 | airymaxos-security capability/（ES-SEL4-2） |
| 服务用户态化 | 所有非必要服务运行在用户空间 | airymaxos-services userland-*（ES-SEL4-3） |
| 消息传递 IPC | 进程间通信唯一机制是消息传递 | io_uring + IPC fastpath（ES-SEL4-4） |
| 形式化验证 | 内核实现必须可被形式化证明 | formal-verification/{spec,proof,capdl}/（ES-SEL4-5） |
| 接口契约 XML | syscall.xml 定义系统调用接口 | R-01 P2 增强（ES-SEL4-6） |
| 架构正交分层 | arch/machine/plat 三层 | kernel 子仓三层适配（ES-SEL4-7） |
| bitfield codegen | structures.bf 定义位域 | R-02 P2 增强（ES-SEL4-8） |
| 用户态 API 库独立 | libsel4 与内核源码物理分离 | SDK 层借鉴（ES-SEL4-9） |
| 现代构建系统 | CMake 多编译器/多架构 | 用户态子仓 Meson/Cargo（ES-SEL4-10） |

### 3.4 seL4 2026 行业最佳实践

1. **形式化验证范围聚焦**：不追求全内核验证，聚焦关键路径（调度器核心、IPC fastpath、capability 派生）——agent-linux 已采纳
2. **MCS 调度与 Agent 感知融合**：seL4 15.0.0 的 runtime domain schedule 与 Agent 工作负载特性结合——agent-linux SCHED_AGENT 策略可借鉴
3. **capability 动态委托**：seL4 的 mint/mintcopy/derive/revoke 模型——agent-linux 已在 security_types.h 定义
4. **IPC fastpath 优化**：seL4 的快速路径（~150 cycles）——agent-linux io_uring 零拷贝目标 <200 cycles

---

## 4. Zircon/Minix3 引用处置策略

### 4.1 处置原则

| 引用类型 | 处置策略 | 理由 |
|----------|----------|------|
| **理论来源声明** | 必须删除 Zircon/Minix3 | 违反 ADR-014 单一来源原则 |
| **设计参考引用** | 必须改为 seL4 或删除 | 设计来源必须单一 |
| **横向对比表** | 保留但标注"历史对比，非设计来源" | 对比表有教育价值，展示选择 seL4 的理由 |
| **总结性表述** | 必须改为"仅 seL4" | 总结反映设计决策 |

### 4.2 逐项修复方案

#### V-01: YAML 元数据 theory_source

**修复前**: `theory_source: seL4 + Zircon + Minix3 综合对照`
**修复后**: `theory_source: seL4（唯一来源，ADR-014）`

#### V-02: 正文理论来源声明

**修复前**: `**理论来源**：seL4 + Zircon + Minix3 综合对照`
**修复后**: `**理论来源**：seL4（唯一来源，ADR-014）`

#### V-03: 三代微内核横向对比表

**处置**: 保留对比表，但在表前添加声明：
> ⚠️ **本对比表仅用于历史参考，展示选择 seL4 的技术依据。agent-linux 微内核设计思想来源为 seL4 唯一（ADR-014），不从 Zircon 或 Minix3 借鉴设计思想。**

#### V-04: "参考 Zircon 的 devhost 设计"

**修复前**: "参考 Zircon 的 devhost 设计"
**修复后**: "参考 seL4 的用户态服务框架（ES-SEL4-3 服务用户态化）"

#### V-05: "seL4 root task + Zircon component"

**修复前**: "Cupolas 框架 | 用户态服务组织架构 | seL4 root task + Zircon component"
**修复后**: "Cupolas 框架 | 用户态服务组织架构 | seL4 root task 模型（ES-SEL4-3）"

#### V-06: 总结性表述

**修复前**: "充分吸收 seL4 的安全模型、Zircon 的现代内核设计、Minix3 的可靠性工程"
**修复后**: "充分吸收 seL4 的微内核设计思想（ES-SEL4-1~5：极简原则/capability 单一模型/服务用户态化/消息传递 IPC/形式化验证）"

---

## 5. seL4 唯一来源的工程影响分析

### 5.1 对架构设计的影响

| 设计维度 | 影响 | 调整方向 |
|----------|------|----------|
| Cupolas 安全穹顶 | 从"seL4 + Zircon 混合"改为"seL4 capability 单一模型" | 强化 capability 派生（mint/mintcopy/derive/revoke） |
| 用户态服务框架 | 从"参考 Zircon devhost"改为"参考 seL4 root task" | 采用 seL4 root task 模型组织用户态服务 |
| 故障恢复机制 | 从"参考 Minix3 自愈合"改为"seL4 形式化验证驱动" | 通过形式化验证预防故障，而非事后自愈 |
| 驱动模型 | 从"Zircon 用户态驱动框架"改为"seL4 服务用户态化" | 通过 FUSE/VFIO/AF_UNIX 接入上游驱动 |

### 5.2 对工程标准的影响

无影响。工程标准（OS-IRON-010~012）已确立"Linux 6.6 为基、seL4 为鉴"工程取向，seL4 借鉴仅限架构层（ES-SEL4-1~5 + ES-SEL4-7），编码风格层完全采纳 OLK-6.6。

### 5.3 对 [SC] 共享契约层的影响

无影响。[SC] 6 个头文件已基于 seL4 设计哲学定义，收紧来源不改变已有数据结构。

---

## 6. 修复执行计划

### 6.1 修复清单

| 编号 | 文件 | 修复内容 | 状态 |
|------|------|----------|------|
| FIX-01 | `docs-closed/03-microkernel-design-ref/04-microkernel-strategy.md` L6 | theory_source 改为 seL4 唯一 | ✅ 已修复 |
| FIX-02 | 同上 L18 | 理论来源改为 seL4 唯一 | ✅ 已修复 |
| FIX-03 | 同上 L85-88 | 对比表前添加历史参考声明 | ✅ 已修复 |
| FIX-04 | 同上 L93 | 安全模型备注"结合 seL4 严格性 + Zircon 实用性"改为"基于 seL4 capability 单一模型（ES-SEL4-2）" | ✅ 已修复（报告初版遗漏，已补） |
| FIX-05 | 同上 L94 | 驱动模型备注"参考 Zircon devhost"改为"参考 seL4 用户态服务框架（ES-SEL4-3）" | ✅ 已修复 |
| FIX-06 | 同上 L98 | 故障恢复备注"参考 Minix3，增强 AI 场景"改为"seL4 形式化验证驱动的故障预防（ES-SEL4-5）" | ✅ 已修复（报告初版遗漏，已补） |
| FIX-07 | 同上 L137 | Cupolas 参考改为 seL4 root task 模型（ES-SEL4-3） | ✅ 已修复 |
| FIX-08 | 同上 L355 | "seL4/Zircon/Minix3 的公开参考"改为"seL4 微内核设计思想的公开参考" | ✅ 已修复（报告初版遗漏，已补） |
| FIX-09 | 同上 L370 | 总结改为"充分吸收 seL4 的微内核设计思想（ES-SEL4-1~5）" | ✅ 已修复 |

**验证结果**：Grep 复查 `docs-closed/03-microkernel-design-ref/04-microkernel-strategy.md` 中 Zircon/Minix3 残留 4 处，全部位于历史对比表表头行（L87 声明 / L91 表 2.1 / L106 表 2.2 / L116 表 2.3），已由 L87 历史对比声明覆盖，属合法保留。所有"设计来源"性质引用已彻底清除。

### 6.2 验证方法

```bash
# 验证 docs-closed 中不再有 Zircon/Minix3 作为设计来源
grep -rn "Zircon\|Minix3\|Minix" docs-closed/agent-linux/03-microkernel-design-ref/
# 预期：仅在"历史对比表"中出现，且表前有声明标注
```

---

## 7. 结论

### 7.1 核心结论

1. **公开方案文档已合规**：`docs/AirymaxOS/` 已实现 seL4 唯一来源
2. **闭源参考文档已修复**：`docs-closed/03-microkernel-design-ref/04-microkernel-strategy.md` 的 6 处违规引用已全部修复
3. **seL4 2026 最新技术已整合**：seL4 15.0.0 的 runtime domain schedule、MCS 调度等特性已纳入分析
4. **工程影响可控**：收紧来源不改变已有架构设计和工程标准，仅影响 Cupolas/故障恢复/驱动模型的设计参考表述

### 7.2 设计哲学统一

agent-linux 微内核设计哲学现已完全统一为 seL4 唯一来源：

```
agent-linux 微内核设计思想 = seL4 设计哲学（ES-SEL4-1~10）
├── 架构层强制借鉴（ES-SEL4-1~5 + ES-SEL4-7）：极简/capability/服务用户态化/IPC/形式化验证/架构正交
├── P2 增强建议（ES-SEL4-6 + ES-SEL4-8）：syscall.xml/structures.bf codegen
└── 已落地（ES-SEL4-9 + ES-SEL4-10）：libsel4 独立/Meson+Cargo 构建
```

不引入 Zircon（面向对象哲学）或 Minix3（自愈哲学），避免工程思想在哲学和逻辑学层面的多元化冲突。

---

## 8. 相关文档

- `docs/AirymaxOS/10-architecture/03-microkernel-strategy.md`（公开微内核策略，已 seL4 唯一）
- `docs/AirymaxOS/10-architecture/05-adrs.md`（ADR-014 决策记录）
- `docs-closed/agent-linux/03-microkernel-design-ref/04-microkernel-strategy.md`（闭源参考，已修复）
- `docs-closed/agent-linux/_research_0.2.1/01-source-code-engineering-study.md`（seL4 + OLK-6.6 源码研究）

---

> **报告结束** | v0.3.0 微内核来源收紧分析 | 2026-07-09 | 闭源不公开
