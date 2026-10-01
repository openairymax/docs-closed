# 05-tech-reference-and-improvement/ 历史归档说明

> **归档声明**: 本目录为**历史归档目录**，内含 Airymax 运行时（agentrt）早期阶段的技术借鉴、分析报告与原型设计文档，随仓库公开，供项目历史研究参考。

---

## 1. 目录性质

本目录下的所有文档均为**历史归档文档**，产生于 Airymax 运行时早期设计阶段（v0.1.0 之前）。这些文档记录了项目演进过程中的技术决策思路、原型探索与改进策略，具有重要的历史参考价值。

**这些文档不在当前 0.1.1 版本的工程标准管辖范围内，不参与 CI/CD 质量门禁检查。**

## 2. 已知遗留：agentos_ 前缀残留

本目录下 5 个历史归档文档共含 **1738 处 `agentos_` 前缀残留**。这些残留是 v26.0 阶段 `agentos_` → `airy_` 改名决策之前的历史产物。

| 文件 | `agentos_` 残留数 |
|------|------------------|
| `historical-prototypes/AgentOS原型文档.md` | 1335 |
| `analysis-reports/第01版-AgentOS下一步改进建议.md` | 155 |
| `analysis-reports/第01版-AgentOS双思维模型详细落地方案.md` | 151 |
| `analysis-reports/第02版-AgentOS技术改进策略和详细方案.md` | 75 |
| `core-module-designs/CoreLoopThree具体实现方案01.md` | 22 |
| **合计** | **1738** |

## 3. 不修正原因

根据 v3.0 系统性修正决策（v3.0-综合-P2-14），**不修正**这些历史归档文档中的 `agentos_` 残留，原因如下：

1. **历史记录完整性**：这些文档记录了特定历史阶段的技术决策上下文，修改前缀会破坏历史记录的原始性与完整性
2. **无工程影响**：本目录文档不参与编译、不参与 CI/CD 质量门禁、不作为当前工程标准的权威来源
3. **成本收益不匹配**：1738 处修改的工作量与风险远超收益

## 4. 当前前缀规范

当前 `agentrt` 项目的前缀规范以 SSoT 为准：

- **SSoT**: `docs/docs-workload/10-architecture/06-iron9-shared-model.md` §3.12
- **正确前缀**: `airy_*`（源码 1788 处使用）
- **不使用**: `agentrt_*`（源码 0 处使用）
- **已废弃**: `agentos_*`（源码 0 处使用）

## 5. 目录结构

```
05-tech-reference-and-improvement/
├── README.md                              # 本文件 — 归档说明
├── 01-cicd-restructure-v11.14.md          # CI/CD 系统化重构方案
├── analysis-reports/                      # 分析报告（历史归档）
│   ├── AgentOS原型与现状对比分析及五个目标实现策略.md
│   ├── 前期多投入后期少消耗策略可行性分析01.md
│   ├── 第01版-AgentOS下一步改进建议.md
│   ├── 第01版-AgentOS双思维模型详细落地方案.md
│   ├── 第01版-AgentOS技术改进策略和详细方案.md
│   └── 第02版-AgentOS技术改进策略和详细方案.md
├── historical-prototypes/                 # 历史原型设计（历史归档）
│   ├── AgentOS原型文档.md
│   ├── 双思考系统全方位设计01.md
│   ├── 突破长上下文瓶颈.md
│   └── 记忆卷载独立突破上下文窗口限制的可行性.md
└── core-module-designs/                   # 核心模块设计方案（历史归档）
    ├── CoreLoopThree具体实现方案01.md
    ├── MemoryRovol可行性深度分析01.md
    ├── MemoryRovol方案深度分析报告01.md
    ├── MemoryRovol具体实现方案01.md
    └── MemoryRovol落地实操方案01.md
```

---

**文档版本**: 0.1.1
**生成时间**: 2026-07-14
**维护者**: AgentRT 开源维护团队
**关联决策**: v3.0-综合-P2-14（05-tech-reference-and-improvement/ 历史归档 1738 处 agentos_ 残留）
