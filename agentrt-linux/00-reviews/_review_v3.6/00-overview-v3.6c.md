SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 00 — v3.6c 第三轮深度研究主索引（工程思想与设计论证）

> **文档定位**：agentrt-linux 内核设计深度对比研究 · 第三轮主索引
> **对比基准**：openEuler kernel-OLK-6.6 · seL4-master · Airymax agentrt-linux（极境内核）
> **最后更新**：2026-08-01
> **方法论**：逐字节阅读三项目源码与工程文档，所有引用标注文件路径+行号，严禁编造
> **与前序关系**：第一轮（v3.6）核心机制对比、第二轮（v3.6b）基础设施对比、本轮（v3.6c）聚焦**工程思想深层次论证**——极境内核设计哲学论证 + openEuler/seL4 工程标准研究

---

## 1. 第三轮定位

前两轮回答"核心机制设计对不对"（第一轮）与"基础设施撑不撑得住"（第二轮），第三轮回答两个新问题：

1. **极境内核的设计方案论证是否成立？**——不是找 bug，而是论证五维技术选型的正确性、机制设计的自洽性、与参考项目映射的忠实度、边界条件。
2. **openEuler 与 seL4 的工程标准/工程思想是什么？**——从工程方法层面研究两个参考项目，提炼可借鉴的工程机制。

### 1.1 第三轮报告清单

| 编号 | 文件 | 主题 | 改进点 |
|------|------|------|--------|
| 00 | [本文件](00-overview-v3.6c.md) | 第三轮主索引 | — |
| 19 | [19-engineering-philosophy-v3.6c.md](19-engineering-philosophy-v3.6c.md) | 工程思想论证总论：极境内核设计哲学 vs openEuler vs seL4 | E1-E6 |
| 20 | [20-design-argumentation-v3.6c.md](20-design-argumentation-v3.6c.md) | 设计方案深层次论证：五维选型 + capability/安全/IPC/调度 | E7-E13 |
| 21 | [21-openEuler-engineering-standards-v3.6c.md](21-openEuler-engineering-standards-v3.6c.md) | openEuler 工程标准与工程思想研究（KABI/UAPI/process/测试/锁） | E14-E17 |
| 22 | [22-seL4-engineering-thought-v3.6c.md](22-seL4-engineering-thought-v3.6c.md) | seL4 工程标准与工程思想研究（形式化验证/SSoT/compile_assert/验证配置） | E18-E22（并入 E1-E3） |
| 23 | [23-improvement-closure-v3.6c.md](23-improvement-closure-v3.6c.md) | 第三轮改进建议汇总（17 项）与闭环总结 | E1-E17 去重后 |

### 1.2 研究主体

| 项目 | 路径 | 角色 |
|------|------|------|
| openEuler | `/home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/` | KABI 工程标准参考（kabi.h/checkpatch/submitting-patches/lockdep） |
| seL4 | `/home/spharx/SpharxWorks/.engineer-reference/seL4-master/` | 可验证性工程思想参考（CAVEATS/compile_assert/SSoT/验证注解） |
| Airymax | `/home/spharx/SpharxWorks/airymaxhub/` | 被论证对象（[04-engineering-philosophy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/04-engineering-philosophy.md) 16 条 OS-IRON + [03-microkernel-strategy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) + 内核源码 80 文件） |

---

## 2. 第三轮核心结论摘要

### 2.1 设计论证结论（报告 20）

- **五维技术选型全部论证通过，无方向性错误**：sched_tac（6.6 基线约束下的必然）、IORING_OP_URING_CMD（成熟稳定）、纯 C LSM（可审计 + P1-4 已落地）、alloc_pages+mmap（跨架构一致）、IRON-9 v3 [DSL]（openEuler/seL4 都没有的独有设计）。
- **第一轮 P1-4 修复已确认落地**：[airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_lsm.c) L112-117/L144-149 的 task_kill/file_open 已含 Badge 校验。

### 2.2 工程标准研究结论（报告 21/22）

- **openEuler**：精髓是"不破坏上游标准，用抽象层搭建企业级兼容桥梁"——KABI 宏体系（[kabi.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/kabi.h) L335-507）实现"稳定性靠预留而非承诺"。8 条工程思想金句。
- **seL4**：精髓是"为可验证性而设计"——SSoT codegen、compile_assert 双模式宏（[assert.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/assert.h) L45-69）、验证注解内嵌源码（[util.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/util.h) L93-306）、验证配置锁存、CAVEATS 诚实声明。10 条工程思想金句。

### 2.3 最大短板（第三轮核心发现）

**"文档承诺、实现空白"**：极境内核文档承诺的 compile_assert/验证注解/验证配置锁存三类机制，源码 grep 全部零命中。OS-KER-229 声称编译期断言已落地，但 airy 全部源码无一处 `BUILD_BUG_ON`/`static_assert`。seL4 的 CAVEATS.md 诚实声明传统（"未验证即明示"）是极境内核应学习的工程诚信——**文档不能替代实现，预留与已落地必须边界清晰**。

---

## 3. 第三轮改进点优先级矩阵（17 项，去重后）

### 3.1 P1 — 高优先级（M2 前收敛）

| 编号 | 标题 | 来源 | 工作量 |
|------|------|------|--------|
| E1 | [SC] 头文件引入 AIRY_COMPILE_ASSERT 编译期契约宏 | 19/22 | 4h |
| E4 | known-caveats 增加 SMP 验证覆盖标注 | 19 | 1h |
| E6 | sched_tac 机制/策略边界文档化 | 19/20 | 1h |
| E7 | sched.h/stc_policy.h 策略枚举语义统一 | 20 | 3h |
| E9 | [DSL] 触发时域文档化（编译期非运行时） | 20 | 1h |
| E10 | airy_enabled 默认值注释漂移修复 | 20 | 0.5h |
| E12 | IPC 唯一合法入口声明 | 20 | 1h |
| E14 | syscall 预留槽"预留→消费"登记机制（KABI_USE 式） | 21 | 2h |

### 3.2 P2 — 中优先级（M3-M5）

| 编号 | 标题 | 来源 | 工作量 |
|------|------|------|--------|
| E2 | 验证注解机制落地（MODIFIES/FNSPEC） | 19/22 | 8h |
| E3 | 验证配置锁存声明 | 19/22 | 2h |
| E5 | Liedtke 论证义务 gate | 19 | 2h |
| E8 | zero_copy 与版本治理交互文档化 | 20 | 2h |
| E11 | AIRY_CAP_PERM_* 权限位枚举 SSoT | 20 | 2h |
| E15 | UAPI 结构体预留字节（KABI_RESERVE_BYTES 式） | 21 | 2h |
| E16 | lockdep_set_class 锁类注解 | 21 | 2h |
| E17 | [SC] 三方一致性构建期 baseline diff 脚本 | 21 | 4h |

### 3.3 P3

| 编号 | 标题 | 来源 | 工作量 |
|------|------|------|--------|
| E13 | airy_ipc_fastpath.c L3 版权拼写修复 | 20 | 0.1h |

---

## 4. Go/No-Go 判断与成熟度

| 阶段 | 判断 | 条件 |
|------|------|------|
| M0 设计 | ✅ GO | 五维选型论证通过，E4/E6/E9/E10/E12 文档化 |
| M1 脚手架 | ✅ GO | P1-4 已落地，脚手架质量达标 |
| M2 IPC 集成 | ⚠️ 条件 GO | 收敛 E1/E7/E12 + 第二轮 N3/N5/N10 + 第一轮 P1-4 残余（N2） |

**成熟度评分**：第三轮工程标准 82.0（B）· 可验证性预留 68（D+，最大短板）· 三轮加权 **86.3（B+）**。

---

## 5. 三轮研究总览

| 维度 | 第一轮 v3.6 | 第二轮 v3.6b | 第三轮 v3.6c |
|------|------------|-------------|-------------|
| 视角 | 核心机制 | 基础设施 | 工程思想与设计论证 |
| 子域 | sched/security/IPC/syscall/cap/mem-version（6） | boot/irq/time/sync/mem-alloc/task/log/fault（8） | 工程标准（openEuler KABI/seL4 验证） |
| 报告数 | 9（00-08） | 11（00+09-18） | 6（00+19-23） |
| 改进点 | 29（1 P0 + 11 P1 + 17 P2） | 22（10 P1 + 12 P2） | 17（8 P1 + 8 P2 + 1 P3） |
| 累计（去重） | — | 51 | 68 |
| 评分 | 89.5（A-） | 86.0（B+） | 82.0（B）工程标准 / 加权 86.3 |

三阶段递进：核心机制 → 基础设施 → 工程方法。第三轮确立的"可验证性预留"改进路线（E1 → E2 → E3）是极境内核从"借鉴 seL4 思想"迈向"借鉴 seL4 工程方法"的关键路径。
