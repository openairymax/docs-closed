SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 23 — 第三轮改进建议汇总与闭环总结（v3.6c）

> **文档定位**：agentrt-linux 内核设计深度对比研究 · 第三轮 · 改进建议汇总 + 闭环
> **数据来源**：报告 19（工程思想总论）/ 20（设计方案论证）/ 21（openEuler 工程标准）/ 22（seL4 工程思想）
> **最后更新**：2026-08-01
> **方法论**：交叉比对四份第三轮报告，去重合并（E18-E22 并入 E1-E3），按优先级评定
> **与前序关系**：第一轮 29 项（P0-1 + P1-11 + P2-17）+ 第二轮 22 项（N1-N22）+ 第三轮 17 项（E1-E17），三轮回合计 68 项（去重后 66 项）

---

## 1. 第三轮改进点优先级矩阵

### 1.1 P0 — 阻断项

**本轮无新增 P0**。第一轮 P0-1（[syscall_64.tbl](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/arch/x86/entry/syscalls/syscall_64.tbl) L384-387，552-571 预留槽未显式登记）仍是唯一阻断项。第三轮聚焦工程思想与设计论证，未发现新的设计阻断——**五维技术选型全部论证通过，无方向性错误**（报告 20 结论）。

### 1.2 P1 — 高优先级（M2 前收敛）

| 编号 | 标题 | 来源 | 现状位置 | 参考 | 工作量 |
|------|------|------|----------|------|--------|
| E1 | [SC] 头文件引入 AIRY_COMPILE_ASSERT 编译期契约宏（内核-用户态常量一致性编译期钉死） | 19/22 | [uapi_compat.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/uapi_compat.h) | seL4 [assert.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/assert.h) L45-69 + [faults.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/api/faults.c) L20-26 | 4h |
| E4 | known-caveats 增加 SMP 验证覆盖标注（多核 lock-free ring、per-bucket 锁） | 19 | [09-known-caveats.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/09-known-caveats.md) L65-72 | seL4 [CAVEATS.md](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/CAVEATS.md) L127-155 | 1h(文档) |
| E6 | sched_tac 机制/策略边界文档化（stc_policy_to_linux 是机制还是策略） | 19/20 | [stc_dispatch.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_dispatch.c) L50-70 | seL4 内核零策略 | 1h(文档) |
| E7 | sched.h/stc_policy.h 两套策略枚举语义统一（UAPI 只暴露 AIRY_SCHED_POLICY_*） | 20 | [stc_policy.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/sched/stc_policy.c) L17-22 vs [sched.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/sched.h) L102-105 | — | 3h |
| E9 | [DSL] 触发时域文档化（编译期跨平台降级，非运行时容错） | 20 | [uapi_compat.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/uapi_compat.h) L95-132 | — | 1h(文档) |
| E10 | airy_enabled 默认值注释与代码一致性修复（true vs 注释声称 false） | 20 | [airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_lsm.c) L30-31/L51 | — | 0.5h |
| E12 | IPC 唯一合法入口声明（fastpath 不得绕过 LSM 5-phase 校验） | 20 | [airy_ipc_fastpath.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_fastpath.c) L11-46 | — | 1h(文档) |
| E14 | KABI_USE 式"预留→消费"登记机制（syscall 20 预留槽显式消费宏 + 编译期断言） | 21 | [syscalls.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/syscalls.h) L26-29 | openEuler [kabi.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/kabi.h) L439/L443 | 2h |

### 1.3 P2 — 中优先级（M3-M5 渐进收敛）

| 编号 | 标题 | 来源 | 现状位置 | 参考 | 工作量 |
|------|------|------|----------|------|--------|
| E2 | 验证注解机制落地（MODIFIES/FNSPEC 标注 capability/IPC fastpath） | 19/22 | [airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap.h) L75-90、[airy_ipc_fastpath.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_fastpath.c) | seL4 [util.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/util.h) L93/L189-196 | 8h |
| E3 | 验证配置锁存（airymax_verified.cmake 等价物声明） | 19/22 | 新增 [09-known-caveats.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/09-known-caveats.md) 附录 | seL4 `configs/*_verified.cmake`（40+） | 2h |
| E5 | Liedtke 论证义务落地（新增内核子系统"无法在用户态实现"论证 gate） | 19 | [09-ssot-registry.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/09-ssot-registry.md) | — | 2h(文档) |
| E8 | zero_copy buffer 与 MemoryRovol 版本治理交互文档化（快照 or 共享） | 20 | [airy_ipc_zero_copy.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_zero_copy.c) L1-168 | — | 2h(文档) |
| E11 | AIRY_CAP_PERM_* 权限位枚举 SSoT（集中于 [SC] security_types.h） | 20 | [airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap.h) L75 | — | 2h |
| E15 | KABI_RESERVE_BYTES 式 UAPI 结构体预留字节 | 21 | [ipc.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/ipc.h) 128B 头 | openEuler [xcu_vstream.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/uapi/linux/xsched/xcu_vstream.h) L13-14 | 2h |
| E16 | lockdep_set_class 锁类注解（per-bucket 锁/全局锁） | 21 | [airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap.h) L52-56 | openEuler [lockdep.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/lockdep.h) L214 | 2h |
| E17 | [SC] 头文件三方一致性构建期 baseline diff 校验脚本 | 21 | [syscalls.h](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/syscalls.h) L8-12 | openEuler scripts/kabideps/kabisyms | 4h |

### 1.4 P3 — 低优先级

| 编号 | 标题 | 来源 | 现状位置 | 工作量 |
|------|------|------|----------|--------|
| E13 | airy_ipc_fastpath.c L3 版权行 SPHARx 拼写修复 | 20 | [airy_ipc_fastpath.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_fastpath.c) L3 | 0.1h |

---

## 2. 改进点分类统计

### 2.1 第三轮（E1-E17，去重合并后 17 项）

| 类别 | P1 | P2 | P3 | 合计 |
|------|----|----|----|----|
| 可验证性预留（compile_assert/验证注解/配置锁存） | 1 | 2 | 0 | 3 |
| 文档一致性（SMP 标注/[DSL] 时域/机制策略边界/入口声明） | 4 | 1 | 0 | 5 |
| 接口工程（预留登记/UAPI 预留字节/权限位 SSoT/枚举统一） | 2 | 2 | 0 | 4 |
| 并发与锁（lockdep 注解） | 0 | 1 | 0 | 1 |
| 构建与 CI（baseline diff） | 0 | 1 | 0 | 1 |
| 细节修正（注释漂移/版权拼写） | 1 | 0 | 1 | 2 |
| 治理（Liedtke 论证 gate） | 0 | 1 | 0 | 1 |
| **合计** | **8** | **8** | **1** | **17** |

### 2.2 三轮回合计（去重后）

| 轮次 | 范围 | P0 | P1 | P2 | P3 | 合计 |
|------|------|----|----|----|----|----|
| 第一轮 v3.6 | 核心机制（sched/security/IPC/syscall/cap/mem-version） | 1 | 11 | 17 | 0 | 29 |
| 第二轮 v3.6b | 基础设施（boot/irq/time/sync/mem-alloc/task/log/fault） | 0 | 10 | 12 | 0 | 22 |
| 第三轮 v3.6c | 工程思想与设计论证 | 0 | 8 | 8 | 1 | 17 |
| **累计（去重）** | 14 子域 + 工程标准 | **1** | **29** | **37** | **1** | **68** |

> 去重说明：第三轮 E18-E22 为报告 22 对 E1-E3 的重述（不同视角论证同一改进），已并入 E1-E3；E1（compile_assert）同时对应第一轮 R-01/R-02 的 codegen 建议与第二轮 E1 的验证注解建议，属跨轮次同源项。

### 2.3 与第一/二轮交叉项

| 第三轮编号 | 跨轮次对应 | 说明 |
|-----------|-----------|------|
| E1 | 第一轮 R-01/R-02（syscall.xml/bitfield codegen 建议） | compile_assert 是 R-01 的最小可行先行步 |
| E2 | 第二轮 N12/N17（日志）/N9（BPF）的验证视角 | 验证注解优先用于最热路径 |
| E7 | 第二轮 N11（task lifecycle）+ 第一轮 P2-8（sched_attr） | 策略枚举统一是调度接口稳定前提 |
| E16 | 第二轮 N4/N10（全局锁/RCU） | lockdep 注解与 per-bucket 锁改造并行 |

---

## 3. 实施路线图

### 3.1 阶段一：M0/M1（立即，约 8h 文档化/小改）

| 编号 | 工作量 | 说明 |
|------|--------|------|
| E4 | 1h | known-caveats 增加 SMP 验证覆盖标注 |
| E6 | 1h | sched_tac 机制/策略边界文档化 |
| E9 | 1h | [DSL] 触发时域文档化（编译期非运行时） |
| E10 | 0.5h | airy_enabled 默认值注释修复 |
| E12 | 1h | IPC 唯一合法入口声明 |
| E13 | 0.1h | 版权拼写修复 |

小计：约 4.6h，全部为文档/注释修正，不改功能。

### 3.2 阶段二：M2 前（约 9h 编译期契约）

| 编号 | 工作量 | 说明 |
|------|--------|------|
| E1 | 4h | AIRY_COMPILE_ASSERT 双模式宏（uapi_compat.h 定义 + syscalls.h/ipc.h 应用） |
| E7 | 3h | 策略枚举统一（UAPI 只暴露 AIRY_SCHED_POLICY_*） |
| E14 | 2h | syscall 预留槽"预留→消费"登记机制 |

小计：约 9h，与第二轮 N3/N5/N10 并列 M2 前收敛项。E1 同时满足第一轮 R-01 的先行步。

### 3.3 阶段三：M3-M5（约 24h 可验证性预留 + 接口工程）

| 编号 | 工作量 | 说明 |
|------|--------|------|
| E2 | 8h | 验证注解（MODIFIES/FNSPEC）用于 cap/IPC fastpath |
| E3 | 2h | 验证配置锁存声明 |
| E5 | 2h | Liedtke 论证义务 gate |
| E8 | 2h | zero_copy 与版本治理交互文档化 |
| E11 | 2h | AIRY_CAP_PERM_* 权限位 SSoT |
| E15 | 2h | UAPI 结构体预留字节 |
| E16 | 2h | lockdep 锁类注解 |
| E17 | 4h | 构建期 baseline diff 校验脚本 |

小计：约 24h，配合第一轮 P1-6/P1-9/P1-11 与第二轮 N6/N8/N9 的 M3-M5 项并行。

---

## 4. Go/No-Go 判断（第三轮视角）

| 阶段 | 判断 | 条件 |
|------|------|------|
| M0 设计 | ✅ GO | 五维技术选型论证全部通过（报告 20），无方向性错误；E4/E6/E9/E10/E12 文档化即可完善 |
| M1 脚手架 | ✅ GO | 第一轮 P1-4 已落地（[airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_lsm.c) L112-117/L144-149 Badge 校验），脚手架质量达标 |
| M2 IPC 集成 | ⚠️ 条件 GO | 收敛 E1（compile_assert）/E7（枚举统一）/E12（入口声明）+ 第二轮 N3/N5/N10 + 第一轮 P1-4 残余（superv_lsm N2） |

**第三轮新增判断**：极境内核的"seL4 为鉴"在架构层（capability 模型/机制策略分离/decode-invoke）落地良好，在工程标准层（compile_assert/验证注解/配置锁存）存在"文档承诺、实现空白"差距。E1 是弥合此差距的关键一步，建议 M2 前落地，使 [SC] 头文件一致性从"CI 比对"升级为"编译期强制"。

---

## 5. 成熟度评分更新

### 5.1 第三轮工程标准维度评分

| 维度 | 评分 | 等级 | 说明 |
|------|------|------|------|
| 工程思想自洽性 | 92 | A | 16 条 OS-IRON + 五维 24 原则 + 4 层接口分级，哲学层完整 |
| 设计方案论证 | 90 | A- | 五维选型全部论证通过，E7/E9/E10 为边界完善非方向错误 |
| 工程标准对齐（Linux/openEuler） | 88 | B+ | 提交/治理/测试/安全对齐，缺预留机制工程化（E14/E15） |
| 工程标准对齐（seL4） | 72 | C+ | compile_assert/验证注解/配置锁存零落地，文档承诺空白最大 |
| 可验证性预留 | 68 | D+ | 本轮最大短板——OS-KER-229 声称编译期断言已落地但源码零命中 |

**第三轮工程标准综合评分：82.0（B）**

> 说明：第三轮评分（82.0）低于第一轮（89.5）与第二轮（86.0），因本轮考核维度是"工程标准/可验证性预留"——极境内核在架构与机制层成熟，但在"为可验证性而设计"的工程方法层明显薄弱。这是项目阶段使然（M0/M1 阶段尚未进入验证投入期），但文档承诺超前于实现是必须正视的工程诚信问题。

### 5.2 三轮加权整体成熟度

| 轮次 | 维度 | 评分 | 权重 |
|------|------|------|------|
| 第一轮 v3.6 | 核心机制 | 89.5 | 6 |
| 第二轮 v3.6b | 基础设施 | 86.0 | 8 |
| 第三轮 v3.6c | 工程标准 | 82.0 | 4（工程标准维度权重） |
| **加权整体** | 18 维度 | **86.8** | — |

加权计算：(89.5×6 + 86.0×8 + 82.0×4) / 18 = (537 + 688 + 328) / 18 = 86.3

**三轮回合计加权成熟度：86.3（B+）**——核心机制成熟、基础设施良好、工程标准是下一阶段提升重点。

### 5.3 评分变化分析

| 维度 | v3.6 | v3.6b | v3.6c | 趋势 |
|------|------|-------|-------|------|
| 核心机制成熟度 | 85 (B+) | — | 89.5 (A-) | ↑ 第一轮基础 |
| 基础设施成熟度 | — | 82 (B) | 86.0 (B+) | ↑ 第二轮基础 |
| 工程标准对齐 | — | — | 82.0 (B) | NEW 第三轮考核 |
| 可验证性预留 | — | — | 68 (D+) | NEW 最大短板 |
| 安全完整性 | 86 (B+) | 82 (B) | 88 (B+) | ↑ P1-4 已落地 |

---

## 6. 第三轮核心结论

1. **极境内核设计方案在论证层面成立**：五大技术选型（sched_tac/URING_CMD/纯 C LSM/alloc_pages+mmap/IRON-9 v3）全部论证通过，无方向性错误。sched_tac 是 6.6 基线约束下的必然选择，[DSL] 降级层是 openEuler/seL4 都没有的独有设计。

2. **第一轮 P1-4 修复已落地**：[airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_lsm.c) L112-117/L144-149 的 Badge 校验表明主 LSM 入口已对称，剩余 N2（superv_lsm 补充钩子）为半收敛状态。

3. **工程标准层存在"文档承诺、实现空白"**：compile_assert（E1）、验证注解（E2）、验证配置锁存（E3）在 [03-microkernel-strategy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) L99-107 有明确预留承诺，但源码 grep 零命中。这是第三轮最重要的发现——**文档不能替代实现，诚实标注"预留"与"已落地"的边界**（seL4 CAVEATS.md 的诚实声明传统）。

4. **openEuler 的借鉴价值在"预留机制工程化"**：KABI_RESERVE→KABI_USE 登记模型（E14）、UAPI 结构体预留（E15）、构建期 baseline diff（E17）为极境内核的接口稳定性提供了三层防护模板。

5. **seL4 的借鉴价值在"可验证性工程方法"**：compile_assert 双模式宏、验证注解内嵌源码、验证配置锁存是"为可验证性而设计"的完整闭环，极境内核应从"借鉴思想"迈向"借鉴方法"。

---

## 7. 研究局限性

1. **工程标准考核为主观评分**：E1-E17 的优先级与工作量基于三轮源码阅读判断，未经过实际实施验证。
2. **openEuler 证据来自 OLK-6.6 单一版本**：KABI 宏体系（[kabi.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/kabi.h) L335-507）在 openEuler 不同 LTS 版本间的演进未覆盖。
3. **seL4 证据来自 master 分支**：MCS 验证状态（CAVEATS L107-126 "in progress"）与验证配置（configs/*_verified.cmake）的具体时效性未交叉验证。
4. **性能与验证声明**：~10ns badge 校验已由新增微基准实测（2-10ns，[airy_fastpath_bench.c](file:///home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_fastpath_bench.c)，详见 08-closure-summary-v3.6.md L109 实测标注）；compile_assert 的 CI 成本等仍为设计估算。
5. **第三轮聚焦工程标准**：未重新审阅第一/二轮 51 项改进的实施状态（P1-4 已确认落地，其余未逐一复核）。

---

## 8. 结论

第三轮研究完成了对极境内核设计方案的深层次论证（报告 20）、工程思想总论（报告 19）、以及 openEuler（报告 21）/seL4（报告 22）工程标准的深度研究。核心结论：

- **设计方案成立**：五维选型无方向性错误，P1-4 已落地，极境内核的设计哲学在"Linux 为基、seL4 为鉴"的定位下自洽。
- **工程标准待补齐**：17 项改进（8 P1 + 8 P2 + 1 P3）聚焦可验证性预留与接口工程，E1（compile_assert）是 M2 前的关键一步。
- **Go 判断维持**：M0 ✅ / M1 ✅ / M2 ⚠️ 条件 GO（E1/E7/E12 + 第二轮 N3/N5/N10）。
- **成熟度**：第三轮工程标准 82.0（B），三轮加权 86.3（B+），可验证性预留（68，D+）是下一阶段提升重点。

**最终建议**：极境内核下一阶段的工程投入应优先弥合"文档承诺与实现空白"的差距——以 E1（compile_assert）为起点，逐步引入验证注解（E2）与验证配置锁存（E3），使"seL4 为鉴"从架构层延伸到工程方法层。这与第一轮 R-01/R-02（codegen 建议）和第二轮 N1-N22（基础设施）形成三阶段递进：核心机制 → 基础设施 → 工程方法。
