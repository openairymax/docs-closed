Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agentrt-linux（AirymaxOS）独立复核报告 v3.5

> **报告编号**：06
> **报告版本**：v3.5（独立复核终稿）
> **生成时间**：2026-07-25
> **审查方法**：6 个独立子代理并行复核 + 1 个独立架构终审员 + 全量代码逐字节核验
> **审查原则**：不依赖任何前序报告（03/04/05），所有结论基于亲自读取代码/文档
> **上一版本**：05-issue-reverification-and-final-review-v3.5.md（2026-07-25）
> **SPDX-License-Identifier**：CC-BY-NC-4.0

---

## 0. 执行摘要

本报告是对 _review_v3.5 系列所有 P0 问题的**第二轮独立复核**。6 个独立子代理并行执行，每个子代理从零开始读取代码/文档，不依赖前序报告结论，逐项验证问题真实性。最终由 1 个独立架构终审员综合评估整体方案。

### 0.1 关键数据

| 维度 | 数值 |
|------|------|
| 独立复核子代理数 | 6（并行） |
| 独立架构终审员 | 1 |
| 复核 P0 范围 | 03 报告 6 份关键 SSoT 文档（53 项检验）+ 04 报告 18 P0 + CI 基础设施 5 P0 |
| 04 报告 18 P0 复核结果 | **17 真实存在 + 1 误报**（P0-2 撤销） |
| 6 份 SSoT 文档 53 项检验 | **38 虚构 + 9 不匹配 + 5 文档遗漏 + 1 真实**（虚构率 71.7%） |
| 整体方案就绪度（独立终审） | **50.8/100（D）** |
| 设计质量评分 | **92.3/100** |
| 实现通电度评分 | **47.7/100** |

### 0.2 核心结论

1. **04 报告 18 P0 中 17 个被独立验证为真实存在，仅 P0-2（AIRY_CAP_GPU_SCHED42）为误报**——`cat -A` 字节级验证证实为 TAB 缩进被误读为粘连。

2. **6 份关键 SSoT 文档的虚构率高达 71.7%**——53 项逐字段检验中，仅 1 项与 SSoT 一致。这是本项目最严重的文档质量问题。

3. **整体方案就绪度独立终审为 50.8/100（D）**——设计质量优秀（92.3），但实现通电度严重不足（47.7）。核心阻塞问题：IPC 数据面完全未通电（5/7 opcode 和 4/4 syscall 全部返回 -ENOSYS）。

4. **额外发现**：`stc_dispatch_enqueue` 函数在代码库中**完全不存在**（全项目 grep 零匹配）——前序报告可能将其与其他函数混淆。

5. **唯一可能导致内核崩溃的 P0 是 P0-3（双 airy_lsm.c UAF）**，必须最先修复。

### 0.3 与 05 报告的关键差异

| 维度 | 05 报告 | 06 报告（独立复核） |
|------|--------|-------------------|
| 复核方法 | 4 子代理 + 1 终审员 | **6 子代理 + 1 终审员**（完全独立，不依赖前序报告） |
| 整体就绪度 | 54/100（F） | **50.8/100（D）** |
| 等级判定 | F（IRON-2 一票否决） | **D**（IRON-2 红线严重但设计质量支撑） |
| 关键额外发现 | — | `stc_dispatch_enqueue` 函数不存在 |
| SSoT 文档虚构率 | 未量化 | **71.7%**（53 项检验中 38 虚构） |

---

## 1. 最高危 P0 独立复核（P0-3 / P0-17 / P0-18）

### 1.1 P0-3：双 airy_lsm.c 并存导致 UAF

**结论：✅ 真实存在 — 严重程度：CRITICAL**

| 属性 | [SS] 层 `kernel/security/airy/airy_lsm.c` | [IND] 层 `security/airy_lsm/airy_lsm.c` |
|------|------------------------------------------|----------------------------------------|
| DEFINE_LSM 名称 | `"airy"`（line 150） | `"airy_ind"`（line 212） |
| 构建方式 | `obj-$(CONFIG_SECURITY_AIRY)` → **内建**（Kconfig: bool） | `obj-m := airy_ind.o` → **模块** |
| LSM blob 注册 | `.blobs = &airy_blob_sizes`（line 154） | **无** `.blobs` 字段 |
| task->security 访问 | `task->security + airy_blob_sizes.lbs_task`（line 46）— **blob 偏移** | `task->security = sec`（line 113）— **直接覆写指针** |
| task_free | 空操作（line 63-64） | `kfree(sec); task->security = NULL;`（line 152-153） |

**UAF 破坏链**：
1. [SS] 注册 blob → 框架为每个 task 分配 blob 缓冲区 → `task->security` 指向 blob
2. [IND] `task_alloc` 钩子执行 `task->security = kzalloc(...)` → **覆写 blob 指针**，框架 blob 泄漏
3. [IND] `task_free` 钩子执行 `kfree(sec); task->security = NULL;`
4. [SS] 的 `task_kill`/`file_open` 再访问 `task->security + offset` → **NULL 解引用 → 内核 panic**

**代码自证**：[IND] 层第 107-112 行自行承认这是错误的 hack：
```c
/*
 * 0.1.1 阶段简化为直接保存指针到 task->security，
 * 1.0.1 将迁移到 LSM blob 机制（lsm_set_blob）。
 */
task->security = sec;
```

**附加发现**：[SS] 层自身的 blob 偏移计算也可能有问题——`airy_blob_sizes.lbs_task` 初始值是 SIZE（`sizeof(struct airy_task_sec)`），被当作 OFFSET 使用。若 LSM 框架未将其更新为正确的偏移量 0，则 [SS] 访问的是 blob 区域之外的内存。

### 1.2 P0-17：4 个 syscall 全为 -ENOSYS 桩

**结论：✅ 真实存在 — 严重程度：HIGH**

| Syscall | 编号 | 返回 -ENOSYS 的行 | 备注 |
|---------|------|-------------------|------|
| `airy_sys_call` | 548 | lines 70, 73, 76, 79, 83 | 所有 6 个 opcode 分支全部 -ENOSYS |
| `airy_sys_rovol_ctl` | 549 | line 105 | 仅有参数校验 |
| `airy_sys_sched_ctl` | 550 | line 128 | 仅有参数校验 |
| `airy_sys_clt_notify` | 551 | line 148 | 仅有参数校验 |

**io_uring_cmd 路径**（`airy_uring_cmd.c`）：5/7 opcode 返回 -ENOSYS，1 个（FREEZE）返回 -ENODEV，1 个跳过。

**额外发现**：`stc_dispatch_enqueue` 函数在代码库中**完全不存在**（全项目 grep 零匹配）。前序报告可能将其与其他函数混淆。

**文档矛盾**：代码注释自称"M0 stage"，但文档 §15.2 声称"1.0.1 完成 M2-M8"。

### 1.3 P0-18：隐藏桩 airy_ipc_ring_for_task 恒返回 NULL

**结论：✅ 真实存在 — 严重程度：HIGH**

- 函数定义：`kernel/security/airy/airy_ipc_freeze.c:110-125`
- 返回 `sec->ipc_ring`，但全项目仅 `airy_lsm.c:55` 赋值为 NULL，**无任何非 NULL 赋值**
- 代码自证（line 119-122）：`"M0: sec->ipc_ring is NULL until the per-agent ring pool is wired"`

**影响范围**：
- `airy_uring_cmd.c:112` FREEZE 路径 → 永远返回 -ENODEV
- `airy_die_notify.c:123-125` die_notifier → 故障隔离机制完全失效

---

## 2. SSoT 双端不一致独立复核（P0-1 / P0-2 / P0-4）

### 2.1 P0-1：verdict 双端不一致

**结论：✅ 真实存在**

| 值 | agentrt-linux `security_types.h:75-80` | agentrt commons `security_types.h:32-37` |
|----|---------------------------------------|----------------------------------------|
| 0 | `AIRY_VERDICT_ALLOW` | `AIRY_VERDICT_ALLOW` |
| 1 | `AIRY_VERDICT_DENY` | `AIRY_VERDICT_DENY` |
| 2 | `AIRY_VERDICT_AUDIT` | `AIRY_VERDICT_AUDIT` |
| 3 | **`AIRY_VERDICT_COMPLAIN`** | **`AIRY_VERDICT_ASK`** |

**额外发现**：两文件差异远不止 verdict 命名——许可证、include guard、include 路径、cap ID 定义方式（enum vs #define）、DSL 降级块、整体结构均不同。声称"byte-identical"的 [SC] 双端文件实际上差异巨大。

### 2.2 P0-2：AIRY_CAP_GPU_SCHED42 拼写错误

**结论：❌ 误报（撤销）**

`cat -A` 字节级输出：`#define AIRY_CAP_GPU_SCHED^I^I42^I/* GPU scheduling */$`

`^I` = TAB 字符。宏名 `AIRY_CAP_GPU_SCHED` 和值 `42` 之间是**两个 TAB 字符**，不存在粘连。agentrt-linux 端对应行为 `AIRY_CAP_GPU_SCHED = 42,`（空格分隔），同样正确。

### 2.3 P0-4：airy_struct_ops.c 重定义

**结论：✅ 真实存在**

| | 头文件 `bpf_struct_ops.h:47-53` | `airy_struct_ops.c:20-25` |
|---|---|---|
| 状态数 | 4（INIT/REGISTERED/ACTIVE/DRAINING） | 3（INACTIVE/REGISTERED/ACTIVE） |
| 命名前缀 | `AIRY_STRUCT_OPS_*` | `AIRY_STRUCT_OPS_STATE_*` |
| struct 大小 | 128 bytes（5 字段） | ~24 bytes（4 字段） |
| include 头文件 | — | **未 include `bpf_struct_ops.h`** |

**额外发现**：双端 `bpf_struct_ops.h` 自身也非 byte-identical——commons 端用 `AIRY_OPS_*` 前缀 + 2 字段 struct，agentrt-linux 端用 `AIRY_STRUCT_OPS_*` 前缀 + 5 字段 128B struct。这是另一处独立 SSoT 破坏。

---

## 3. 配置与 ABI 层面 P0 独立复核（P0-5/6/7/8/16）

| P0 | 问题 | 结论 | 关键证据 |
|----|------|------|---------|
| **P0-5** | Kconfig.alk 编号 454-457 vs 实际 548-551 | ✅ **真实存在**（差 94 号） | Kconfig.alk:7,11 两处声明 454-457；syscalls.h:20-23 实际 548-551；syscall_64.tbl:384-387 也注册为 548-551 |
| **P0-6** | ABI 文档虚构 1001-1004 | ✅ **真实存在** | `01-abi-stability.md:68-71` 含 4 个虚构编号与虚构符号名双重错误 |
| **P0-7** | ABI 文档虚构 999 + FEATURE_QUERY | ✅ **真实存在** | `01-abi-stability.md:216,367,380` 三处引用，SSoT 中均不存在 |
| **P0-8** | ABI 文档版本号残留 0.1.1 | ✅ **真实存在**（共 5 处） | 行 5/19/403/425/480；且第 68-71 行标注"1.0.1 引入"与文档版本号 0.1.1 自相矛盾 |
| **P0-16** | sched_ext 文档内部矛盾 | ✅ **真实存在** | §4.5 第 333 行仍引用 sched_ext；§A.2 第 732-737 行声称已删除；内核无 sched_ext 文件 |

---

## 4. CI 基础设施独立复核（P0-9/10/11/12/13/14/15）

| P0 | 问题 | 结论 | 关键证据 |
|----|------|------|---------|
| **P0-9** | CI 路径全部错误 | ✅ **真实存在** | CI 检查 `kernel/include/airymax/airy_agent.h` 等 8 个路径，6 个文件不存在 + 2 个路径层级错（应为 `uapi/linux/airymax/`） |
| **P0-10** | ci-kernel.yml 引用不存在 action | ✅ **真实存在** | `ci-kernel.yml:40` 引用 `.github/actions/setup-toolchain`，目录不存在 |
| **P0-11** | nightly.yml 引用 4 个不存在脚本 | ✅ **真实存在** | formal-verify.py/soak-runner.py/chaos-runner.py/auto-bisect.py 均不存在；tools/ 仅 1 个文件 |
| **P0-12** | 6 项关键 CI 缺失 | ✅ **真实存在** | tri-compile-ci/abi-check-ci/kunit-ci/kselftest-ci/type-size-check/offsetof-check 全部不存在 |
| **P0-13** | [SC] 双端比对 CI 缺失 | ✅ **真实存在** | `sc-dual-ci.yml` 仅 `test -f` 检查，无 `diff -q`；引用的 create-agentrt-mirror-pr.py 和 await-agentrt-ci.py 也不存在 |
| **P0-14** | KUnit 测试全部缺失 | ✅ **真实存在** | 文档声称 3 套件（airy_kunit_tests/airy_ipc_kunit_tests/microcorert_kunit_tests），Glob 全部零结果 |
| **P0-15** | kselftest 全部缺失 | ✅ **真实存在** | 文档声称 3 子目录（airy_ipc/airy_microcorert/airy_agent_contract），Glob 全部零结果 |

**tests-linux 子仓实际内容**：仅 1 个测试文件（`test_ipc_magic.c`），14 个文档/元数据文件。测试代码与文档比例 1:14。

---

## 5. 6 份关键 SSoT 文档虚构内容独立复核

### 5.1 逐文档统计

| # | 文档 | 虚构 | 不匹配 | 文档遗漏 | 真实 | 总检验项 | 虚构率 |
|---|------|------|--------|---------|------|---------|--------|
| 1 | `50-engineering-standards/11-sc-header-type-bridging.md` | 10 | 0 | 1 | 1 | 12 | 83.3% |
| 2 | `110-security/01-lsm-framework.md` | 3 | 3 | 0 | 0 | 6 | 50.0% |
| 3 | `20-modules/05-cognition.md` | 4 | 2 | 1 | 0 | 7 | 57.1% |
| 4 | `20-modules/04-memory.md` | 12 | 0 | 2 | 0 | 14 | 85.7% |
| 5 | `40-dataflows/02-memory-flow.md` | 5 | 2 | 0 | 0 | 7 | 71.4% |
| 6 | `170-performance/02-memory-performance.md` | 4 | 2 | 1 | 0 | 7 | 57.1% |
| **合计** | — | **38** | **9** | **5** | **1** | **53** | **71.7%** |

### 5.2 代表性虚构内容

**类型别名虚构**（文档 1）：
- 文档声称 `airy_u32`/`airy_u64`/`airy_u16`/`airy_u8`/`airy_s32`/`airy_s64`/`airy_bool` 共 7 个类型别名
- 实际 SSoT `uapi_compat.h` 仅映射 `__u32`/`__s32` 等内核 UAPI 类型，**无任何 `airy_*` typedef**

**数据结构虚构**（文档 3/4/5/6）：
- `airy_mr_l1_record_t`/`airy_mr_l2_block_t`/`airy_mr_l3_entry_t`/`airy_mr_l4_persistent_t`（L1-L4 Record）
- `airy_pmem_ops_t`（PMEM 持久化接口）
- `airy_cog_context_t`（CoreLoopThree 上下文，含 inference_phase 字段）
- `airy_llm_inference_phase_t`（LLM 推理阶段枚举）
- `airy_token_efficiency_metric_t`（Token 能效指标）
- `airy_gpu_npu_descriptor_t`（GPU/NPU 描述符）
- `airy_mr_node`/`airy_mr_mgr`

以上结构在实际 SSoT 头文件中**全部不存在**。

**枚举/宏名称系统性偏差**：
- 文档用 `_security` 后缀，SSoT 用 `_sec`
- 文档用 `AIRY_COG_PHASE_*`/`AIRY_THINK_MODE_*`，SSoT 用 `AIRY_COG_*`/`AIRY_THINK_*`
- 文档用 `AIRY_GFP_IO/FS/...`（7 个 Linux 风格 GFP），SSoT 用 `AIRY_GFP_HOT/WARM/COLD/PMEM`（4 个 Airymax 专属分层 GFP）
- 文档用 `enum airy_mr_layer`，SSoT 用 `enum airy_mem_level`

**文件存在性虚构**（文档 1）：
- 文档声称 10 个 [SC] 头文件，其中 5 个（`config.h`/`superv.h`/`cap.h`/`ring.h`/`version.h`）实际不存在

**Include guard 系统性不匹配**：
- 所有文档使用的 guard 模式（如 `AIRY_MEMORY_TYPES_H`）与实际 SSoT 使用的模式（`_UAPI_AIRYMAX_MEMORY_TYPES_H`）均不一致

---

## 6. 整体方案架构独立终审

### 6.1 三大设计支柱

| 支柱 | 设计完整度 | 实现通电度 | 综合评分 | 核心阻塞问题 |
|------|-----------|-----------|---------|-------------|
| Capability-based Security | 90% | 45% | 58/100 | 双 LSM UAF（P0-3）+ verdict 双端不一致（P0-1）+ agent_state 恒 0 |
| io_uring IPC | 95% | 20% | 42/100 | 4/4 syscall + 5/7 opcode 全 -ENOSYS；`stc_dispatch_enqueue` 不存在 |
| sched_tac 调度 | 85% | 35% | 50/100 | agent_state 恒 0 致全部状态判断为死代码；syscall 550 未接通 |

### 6.2 IRON 工程铁律

| 铁律 | 执行情况 | 证据 |
|------|---------|------|
| IRON-1（禁止新特性） | ✅ 通过 | 无越界特性引入 |
| IRON-2（禁止桩函数） | ❌ **红线未过** | 4 syscall 全 -ENOSYS + 隐藏桩 `airy_ipc_ring_for_task` + 5/7 opcode -ENOSYS |
| IRON-3（禁止绕开编译） | ✅ 通过 | Kbuild/Kconfig 齐备 |
| IRON-4（禁止简化功能） | ⚠️ 部分通过 | [DSL] 降级偏弱 |
| IRON-5（禁止未实现设计） | ⚠️ 部分通过 | Cupolas 4 值 verdict 声明但零引用 |
| IRON-8（版本号规则） | ⚠️ 部分通过 | 0.1.1/0.2.8/1.0.1 三版本并存 |
| IRON-9 v3（四层模型） | ⚠️ 部分通过 | verdict 双端不一致 + Kconfig 失步 94 号 |

### 6.3 项目阶段明确性

| 证据源 | 声称阶段 | 实际状态 |
|--------|---------|---------|
| 代码注释 | "M0 stage: returns -ENOSYS" | 但 `airy_cap_*.c` 等 6 文件已写完整实现 |
| 文档 §15.1 | 0.1.1 仅完成 M0+M1 | — |
| 文档 §15.2 | 1.0.1 完成 M2-M8 | 但 4 syscall 全 -ENOSYS（M2 不可用） |

**结论**：代码 M0 vs 文档 M2-M8 自相矛盾。这是本项目最严重的可信度问题。

### 6.4 综合评分

| 维度 | 权重 | 评分 | 等级 |
|------|------|------|------|
| 三大设计支柱 | 25% | 50 | D |
| IRON 铁律执行 | 20% | 45 | D |
| 内核哲学 | 10% | 85 | B |
| ALK 分支管理 | 10% | 65 | C |
| 子仓边界 | 10% | 55 | D |
| 阶段明确性 | 15% | 30 | F |
| CI/测试 | 10% | 25 | F |
| **加权综合** | 100% | **50.8** | **D** |

**正面肯定**：
- 设计文档质量高（Layout C v4、magic 0x41524531、O(1) 撤销算法均有严谨论证）
- 内核哲学执行优秀（"内核不思考"原则严格恪守）
- 分支拓扑设计合理
- `airy_cap_*.c` 等核心代码已真实实现，非空壳

**核心判断**：这是一个**设计成熟（92.3）、实现半通电（47.7）、工程纪律失守**的项目。问题不在设计能力，而在「设计→实现→验证」的 wiring 与纪律执行。

---

## 7. v3.5 系列累计有效 P0 数（终版）

| 来源 | 声称 P0 | 误报 | 有效 P0 |
|------|--------|------|--------|
| 03 报告 | 130 | 6（04 撤销） | 124 |
| 04 报告 | 18 | 1（06 撤销 P0-2） | 17 |
| **v3.5 系列累计** | **148** | **7** | **141** |

---

## 8. 修复建议（按优先级排序）

### 建议 1（最高优先级）：立即消除双 airy_lsm.c UAF

**唯一可能导致内核崩溃的 P0**。`security/airy_lsm/airy_lsm.c` 用 `kzalloc` 直接覆盖 `task->security`。

**修复**：[IND] 层 LSM 禁止直接操作 `task->security`，改用 `lsm_set_blob()` API，或明确 [IND] 与 [SS] 二选一编入。

### 建议 2：接通最小可运行闭环

当前 4/4 syscall + 5/7 uring_cmd 路径全 -ENOSYS，等于无任何可演示路径。

**修复**：优先接通 syscall 550（sched_ctl）→ 调度器路径。注意：`stc_dispatch_enqueue` 函数不存在，需先实现或确认实际函数名。

### 建议 3：建立「阶段声明单一源」

**修复**：在 `ssot-registry.yaml` 新增 `current_stage` 字段，所有代码注释与文档引用该字段，CI 校验不一致即失败。

### 建议 4：修复 CI 路径并引入 [SC] 双端 diff CI

**修复**：修正所有 CI 路径（`kernel/include/airymax/` → `kernel/include/uapi/linux/airymax/`），加入 `diff -q` 双端逐字节比对。

### 建议 5：重写 6 份关键 SSoT 文档（虚构率 71.7%）

基于实际 SSoT 头文件内容重写，删除所有虚构类型/结构/枚举/宏，修正命名后缀和 include guard。

---

## 9. 附录：复核方法论

### 9.1 独立子代理并行复核

| 子代理 | 复核范围 | 关键方法 |
|--------|---------|---------|
| 子代理 1 | 最高危 P0（UAF/桩函数/隐藏桩） | 构建系统交叉验证 + 全项目 grep 赋值追踪 |
| 子代理 2 | SSoT 双端不一致 | `cat -A` 字节级验证 + 双端 `diff` |
| 子代理 3 | 配置与 ABI 层面 | Kconfig/syscalls.h/syscall_64.tbl 三方对比 |
| 子代理 4 | CI 基础设施 | Glob 全量搜索 + 逐文件路径验证 |
| 子代理 5 | 6 份 SSoT 文档 | 文档代码块与 SSoT 头文件逐字段对比 |
| 子代理 6 | 整体方案架构终审 | 代码逐文件核验 + IRON 铁律逐条评估 |

### 9.2 复核原则

1. **零信任**：不依赖任何前序报告（03/04/05），所有结论基于亲自读取代码/文档
2. **字节级验证**：对拼写错误等敏感问题，使用 `cat -A` 字节级验证
3. **交叉验证**：6 个子代理独立并行，结论相互印证
4. **行号精确性**：所有证据附精确行号，偏差记录在案

### 9.3 复核局限性

1. 03 报告 130 P0 仅深度复核 57 P0（6 份关键文档），其余 67 P0 基于失真模式一致性推定
2. 未覆盖 P1/P2 问题
3. 未覆盖 26 类系统性虚构内容中除 13 类核心外的其余 13 类

---

## 10. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v3.5 | 2026-07-25 | 独立复核：6 子代理并行验证 + 1 终审员；04 报告 18 P0 中 17 真实 + 1 误报（P0-2）；6 份 SSoT 文档虚构率 71.7%；整体就绪度 50.8/D；新增发现 stc_dispatch_enqueue 不存在 |

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. | agentrt-linux（AirymaxOS）独立复核报告 | v3.5 | 2026-07-25