Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 10-references — 设计依据

> **文档定位**: AirymaxOS 设计的全部外部依据与账本生成器
> **版本**: 1.0.0
> **最后更新**: 2026-11-01
> **主要读者**: agent-linux 架构委员会 + 内核开发组

---

## 1. 本目录定位

本目录回答一个问题：**AirymaxOS 的设计从哪儿来？** 它收纳四类外部参考与一套账本生成器：

| 子目录 | 回答的问题 | 权威性 |
|--------|-----------|--------|
| `openeuler-tech-reference/` | openEuler（OLK-6.6 基线）在对应子系统上是怎么做的、为什么这么做 | 技术规范级，可溯源到源码 |
| `olk66-source-mapping/` | OLK-6.6 的具体源码位置 / 数据结构 / 函数，与 AirymaxOS 概念如何一一对应 | 源码级映射，可定位到文件与函数 |
| `microkernel-design-ref/` | seL4 / Zircon / Minix3 三代微内核的核心机制与工程思想 | 实现参考级，附改造策略 |
| `industry-best-practices/` | 行业最新的微内核 / OS 理论与最佳实践 | 理论级，用于校准方向 |
| `generators/` | 逐版本任务账本如何确定性产出 | 工具级，账本的唯一来源 |

---

## 2. 三段式方法论

AirymaxOS 的技术方案不是任取一端，而是三段的合成：

```
① openEuler 工程实践  ──┐
   （能跑、能维护）       │
② 行业最新理论        ──┼──→ ③ AirymaxOS 自身技术方案
   （方向不跑偏）         │      （写入 docs/docs-linux/，用自身语言）
③ 微内核工程思想      ──┘
   （结构正确）
```

- **只照抄 openEuler** → 得不到智能体操作系统的差异化，且失去对外表达独立性；
- **只看行业理论** → 缺少可落地的工程细节与验证过的实现路径；
- **只谈微内核** → 忽视 Linux 6.6 基线的既有资产与生态。

三者的合成结论写在 `industry-best-practices/03-airymaxos-synthesis.md`，
落地表达写入 `docs/docs-linux/`（BAN-INTERNAL-002/005）。

---

## 3. 各子目录的阅读顺序建议

| 场景 | 建议顺序 |
|------|---------|
| 新写一个子系统的正式设计文档 | `openeuler-tech-reference/` → `industry-best-practices/` → `microkernel-design-ref/` → 落笔 |
| 定位某个行为的内核实现来源 | `olk66-source-mapping/` → `openeuler-tech-reference/` |
| 评估微内核化改造的边界 | `microkernel-design-ref/04-microkernel-strategy.md` → `05-sel4-extension-plan.md` |
| 重算某个版本的任务账本 | `generators/README`（见 §4） |

---

## 4. 账本生成器（`generators/`）

```
bp_seed.py          种子：WP 清单、LOC、依赖边、范围白名单
   ↓
bp_gen.py           引擎：依赖闭包、拓扑排程、渲染与断言
   ↓
bp_002_gen.py       0.0.2 版方案（输出到上级目录 agent-linux-dev/）
bp_003_gen.py       0.0.3 版方案（同上；支持 AIRYMAX_LEDGER_OUT 覆盖路径）
bp_003_assets.py    0.0.3 存量抵扣基线快照（纯数据，无副作用）
```

**铁律：账本永远由脚本产出，人工只改种子。** 若账本内容与种子不一致，
以重算结果为准；若需调整账本，改种子后重跑，不得手改产物。

> `bp_003_gen.py` 重跑会覆盖 `0.0.3-极境OS任务方案.md`。该文件已并入收尾整合
> §13~§16（验收发行方案、烧录方案、验收报告），重跑前须先确认这些章节已在生成器中
> 落地，否则会造成整合成果丢失。

---

## 5. 与正式设计文档的分层

| 规则 | 说明 |
|------|------|
| BAN-INTERNAL-001 | 外部参考与溯源记录集中在本目录维护 |
| BAN-INTERNAL-002 | 正式设计文档 `docs/docs-linux/` 以 AirymaxOS 自身语言表述 |
| BAN-INTERNAL-003 | 参考内容必须消化吸收后才能进入正式设计文档 |
| BAN-INTERNAL-004 | 对外交付以 `docs/docs-linux/` 为准，本目录不对外 |
| BAN-INTERNAL-005 | 正式设计文档不得是 openEuler 的直接翻译 |

---

## 6. 相关目录

- 历史归档：`../20-archive/`（逐版本评审 + 目录结构设计）
- 总索引：`../README.md`
- 正式设计文档：`docs/docs-linux/`

---

> **文档结束** | AgentRT 开源维护团队
