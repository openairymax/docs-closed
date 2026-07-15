Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0

# Airymax v2.1 综合审查报告

> **文档定位**：v2.1 综合审查报告，汇总 5 个并行 v2.1 子审查 agent 的成果，作为 1.0.1 M1 代码开发启动前就绪度判定的最终基线。
> **保密级别**：SPHARX Ltd 内部参考，**闭源不公开**。
> **版本**：2.1（2026-07-13）。
> **审查基线**：v1.0（atoms + daemons 深度审查 + 方案审查 + 文档审查）、v2.0（工程代码审查 + 优化研究）、IRON-9 v2 三层共享模型、OLK-6.6 六大支柱、SSoT 注册表（09-ssot-registry.md）。
> **审查方法**：5 个并行 agent 独立执行 Grep 全局扫描 + 代表性文件深读 + 跨文档一致性验证，所有结论附 `文件路径:行号` 证据。

---

## 0. 执行摘要

### 0.1 一句话核心结论

v2.1 阶段 5 大维度综合审查结论：**v1.0 识别的核心问题修复进展极低（P0 修复率 0%），部分维度甚至倒退，5 大维度综合评分仅 49/100（F/E+），距离 1.0.1 M1 代码开发就绪门槛 80/B 差距 31 分，当前不具备进入 M1 代码开发的条件。**

### 0.2 五大审查维度评分总表（v1.0 vs v2.1）

| # | 维度 | 权重 | v1.0 评分 | v2.1 评分 | 趋势 | v1.0 等级 | v2.1 等级 | 就绪度 |
|---|------|------|----------|----------|------|----------|----------|--------|
| A1 | agentrt 源码 | 25% | 25 | 32 | ↑ +7 | D | D+ | ❌ 未达标 |
| A2 | AirymaxRT 整体方案 | 20% | 62 | 58 | ↓ -4 | C+ | C | ❌ 未达标 |
| A3 | agentrt-linux 方案 | 20% | 80 | 70 | ↓ -10 | B | C+ | ❌ 未达标 |
| A4 | OpenStandards 开放标准 | 20% | 26 | 26 | → 0 | F | F | ❌ 未达标 |
| A5 | 文档规范与质量控制 | 15% | 58 | 68 | ↑ +10 | D+ | C+ | ❌ 未达标 |
| — | **加权综合** | 100% | **48.6** | **49.0** | **↑ +0.4** | **F** | **F/E+** | **❌ 未达标** |

> **A4 评分说明**：OpenStandards v2.1 报告以 10 分制评估，v2.0 基线 2.6/10（=26/100），v2.1 目标 7.9/10（=79/100）。但 v2.0 提出的 6 项优化建议落地率 0/6，当前体系仍停留在 v1.1 草案状态，故 v2.1 实际评分取 v2.0 基线 26/100。

### 0.3 进入 1.0.1 M1 代码开发的就绪度判定

**判定结果：未达标（NO）**

| 判定标准 | 要求 | v2.1 实际 | 判定 |
|---------|------|----------|------|
| 综合评分 | ≥80/B | 49/F | ❌ |
| P0 问题修复率 | 100% | 0% | ❌ |
| 错误码 SSoT 唯一性 | 唯一 | 3+ 套并行 | ❌ |
| IPC 消息头布局一致性 | 128B/9 字段 | 112B vs 128B 冲突 | ❌ |
| [SC] 头文件清单一致性 | 6 文件顺序对齐 | bpf_struct_ops.h 错列第 1 位 | ❌ |
| 前缀迁移完成度 | airy_* 100% | 606 处 agentrt_* 残留 | ❌ |
| 断裂引用修复 | 全部修复 | 67+ 处跨 34 文件 | ❌ |

**差距**：31 分（49 → 80），需完成全部 P0 阻断项（~85h）方可将综合评分提升至 ~70，再推进 P1 质量项（~185h）后有望达到 80/B 门槛。

---

## 1. 审查范围与方法

### 1.1 五个并行 agent 的审查范围

| Agent | 维度 | 审查范围 | 报告路径 | 行数 |
|-------|------|---------|---------|------|
| A1 | agentrt 源码 | `/agentrt/`（~875 个 C/H 文件） | `docs-closed/agentrt/00-reviews/_review_v2.1/01-agentrt-source-review-v2.1.md` | 537 |
| A2 | AirymaxRT 方案 | `/docs/AirymaxRT/`（88 .md + 3 .drawio） | `docs-closed/agentrt/00-reviews/_review_v2.1/02-airymaxrt-solution-review-v2.1.md` | 924 |
| A3 | agentrt-linux 方案 | `/docs/AirymaxOS/` + `/docs-closed/agentrt-linux/` | `docs-closed/agentrt-linux/_review_v2.1/01-systematic-recheck-v2.1.md` | 886 |
| A4 | OpenStandards | `/docs/OpenStandards/`（8 文件 4409 行）+ `_research_v1.0/v2.0/v2.1` | `docs/OpenStandards/_research_v2.1/01-open-standards-review-v2.1.md` | 1241 |
| A5 | 文档规范与质量控制 | 5 个文档子仓库（228 开源 + 225 闭源 .md） | `docs-closed/agentrt/00-reviews/_review_v2.1/03-docs-quality-review-v2.1.md` | 939 |

### 1.2 审查基线

- **v1.0 综合分析**：`docs-closed/agentrt/00-reviews/_review_v1.0/00-comprehensive-analysis.md`
- **v2.0 工程审查**：`docs-closed/agentrt/00-reviews/_review_v2.0/01-engineering-code-review-v2.md`
- **v2.0 文档质控**：`docs-closed/_review_v2.0/01-document-quality-control.md`
- **v2.0 OpenStandards 优化研究**：`docs/OpenStandards/_research_v2.0/01-open-standards-optimization-v2.md`（1088 行）
- **IRON-9 v2 三层共享模型**：`docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md`
- **OLK-6.6 六大支柱**：`docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md`
- **SSoT 注册表**：`docs/AirymaxOS/50-engineering-standards/09-ssot-registry.md`

### 1.3 审查方法

1. **Grep 全局扫描**：对全量文件执行模式匹配，统计违规数量与分布。
2. **代表性文件深读**：每个维度选取 3-5 个关键文件逐行审查，提取行号证据。
3. **跨文档一致性验证**：SSoT 定义 vs 各文档引用的交叉比对。
4. **v1.0 → v2.1 修复验证**：逐项验证 v1.0 识别问题的修复状态（✅ 完全修复 / △ 部分修复 / ❌ 未修复 / ⚠️ 倒退）。
5. **新发现问题清单**：识别 v1.0 未覆盖的问题，按 P0/P1/P2 分级。
6. **跨维度交叉分析**：识别横跨多个维度的系统性问题（错误码 SSoT、[SC] 头文件清单等）。

---

## 2. 五大审查维度详细评分

### 2.1 agentrt 源码（A1）— 32/100 (D+)

**评分变化：v1.0=25/D → v2.1=32/D+（+7）**

#### 2.1.1 v1.0 问题修复率

| 修复状态 | 数量 | 占比 |
|---------|------|------|
| ✅ 完全修复 | 0/10 | 0% |
| ⚠️ 部分修复 | 2/10 | 20% |
| ❌ 未修复 | 8/10 | 80% |

**10 项 v1.0 问题逐项状态**（`01-agentrt-source-review-v2.1.md:153-164`）：

| # | 问题 | 优先级 | v2.1 状态 |
|---|------|--------|----------|
| 1 | `.clang-format` 不存在 | P0 | ❌ 未修复 |
| 2 | 4 空格缩进全面违规 | P0 | ❌ 未修复（Tab 8 仅 71 处） |
| 3 | agentrt-linux 空仓库 | P1 | ⚠️ 部分修复（55 文件脚手架，0 源码） |
| 4 | fprintf 直接使用 | P0 | ❌ 未修复（memory.c 10 处 + heapstore_migration.c 5 处） |
| 5 | Windows localtime 线程不安全 | P1 | ⚠️ 部分修复（POSIX 已修，Windows 未修） |
| 6 | typedef struct _t 命名违规 | P1 | ❌ 未修复（421 处/100 文件） |
| 7 | ASCII 装饰分节符 | P2 | ❌ 未修复（590 处/100 文件） |
| 8 | banned_functions 合规机制 | P2 | ⚠️ 部分修复（基础设施完善，豁免合理） |
| 9 | malloc/free 混用 | P0 | ❌ 未修复（memory.c 20 处） |
| 10 | 中文注释尾部 `?` 截断 | P2 | ❌ 未修复（logging.c 10+ 处） |

#### 2.1.2 3 项新发现 P0 问题

**N1：错误码 SSoT 冲突——AIRY_SUCCESS 三处定义 + AIRY_OK 一处定义**（`01-agentrt-source-review-v2.1.md:174-181`）

| 定义 | 文件:行号 | 性质 |
|------|----------|------|
| `#define AIRY_SUCCESS 0` | `commons/include/airy_types.h:67` | 权威定义 |
| `#define AIRY_SUCCESS 0` | `commons/utils/types/include/types.h:67` | 重复定义 |
| `#define AIRY_SUCCESS AIRY_COMPAT_SUCCESS` | `commons/utils/error/include/error_compat.h:298` | 第三处 |
| `#define AIRY_OK 0` | `commons/utils/error/include/error.h:43` | 第四处（不同名称，相同语义） |

**N2：airy_err_t 重复 typedef**（`01-agentrt-source-review-v2.1.md:183-190`）

- `commons/include/airy_types.h:40` — 权威定义 `typedef int32_t airy_err_t;`
- `commons/utils/types/include/types.h:62` — 重复 typedef（已 include airy_types.h:36）

**N3：危险警告抑制 `#pragma GCC diagnostic ignored "-Wfree-nonheap-object"`**（`01-agentrt-source-review-v2.1.md:192-199`）

- 证据：`cupolas/src/security/cupolas_network_security.c:94-100`
- 影响：可能掩盖真实的内存破坏漏洞（释放非堆对象）

#### 2.1.3 正面进展

| 项目 | v1.0 | v2.1 | 增长 |
|------|------|------|------|
| goto 集中出口 | 14 处 | 151 处/36 文件 | +978% |
| [SC] 共享契约层完整性 | — | 95/100（8 头文件齐备） | 新增 |
| banned_functions 基础设施 | 缺失 | 85/100（132 行禁用清单） | 新增 |
| airy_err_t 错误码体系 | — | 981 处/100 文件 | 新增 |
| C11 atomic 使用 | — | 280 处/49 文件 | 新增 |
| _Static_assert 编译期校验 | — | 32 处/8 文件 | 新增 |

### 2.2 AirymaxRT 整体方案（A2）— 58/C

**评分变化：v1.0=62/C+ → v2.1=58/C（-4）**

#### 2.2.1 5 项 P0-CRITICAL 全部未修复且部分倒退

| # | 问题 | v1.0 状态 | v2.1 状态 | 修复进展 |
|---|------|----------|----------|---------|
| P0-1 | 错误码 6 套并行 | 6+ 套 | 仍 4+ 套（A: -1 / B: -22 / C: EINVAL / D: 1001 / E: ARE_* / F: AIRY_OK） | ❌ 未修复 |
| P0-2 | "操作系统"定位矛盾 | 40 行匹配 | 51 行匹配/18 文件 | ⚠️ 加剧（+27.5%） |
| P0-3 | [SC] 头文件清单不一致 | bpf_struct_ops.h 第 6 位 | bpf_struct_ops.h **升至第 1 位**，syscalls.h **完全缺失** | ⚠️ 倒退 |
| P0-4 | Cupola/Cupolas 术语不一致 | 4 文件用单数 | 5 文件用单数（新增 .drawio） | ⚠️ 加剧 |
| P0-5 | Daemon 数量标注冲突（10 vs 12） | 标"10" | 仍标"10"（行 305/309） | ❌ 未修复 |

**证据**：`02-airymaxrt-solution-review-v2.1.md:35-43, 134-159`

#### 2.2.2 [SC] 头文件清单倒退详解

| 序号 | `06-iron9-shared-model.md`（v2.1） | `120-cross-project-code-sharing.md`（SSoT） | 一致性 |
|------|-----------------------------------|---------------------------------------------|--------|
| 1 | **`bpf_struct_ops.h`** | `memory_types.h` | ❌ 完全冲突 |
| 2 | `memory_types.h` | `security_types.h` | ❌ 错位 |
| 3 | `security_types.h` | `cognition_types.h` | ❌ 错位 |
| 4 | `cognition_types.h` | `sched.h` | ❌ 错位 |
| 5 | `sched.h` | `ipc.h` | ❌ 错位 |
| 6 | `ipc.h` | `syscalls.h` | ❌ 完全缺失 |

**证据**：`02-airymaxrt-solution-review-v2.1.md:140-147`，`06-iron9-shared-model.md:68`，`120-cross-project-code-sharing.md:65-76`

#### 2.2.3 IPC 消息头三重违规蔓延

| 文件 | 行号 | 违规类型 |
|------|------|---------|
| `30-interfaces/06-ipc/README.md` | 27-42 | `are_ipc_message_header_t` / `uint32_t` / 无 packed / 13 字段 / `char source[32]` |
| `30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md` | 60, 93-109 | `ARE_IPC_MAGIC` / `are_ipc_message_header_t` / 14 字段（**v2.1 新发现蔓延**） |

**vs SSoT 要求**（`120-cross-project-code-sharing.md:343`）：`airy_ipc_msg_hdr` / `__u32` / `__attribute__((packed))` / 8 字段 / `__u64 src_task` / `_Static_assert(sizeof(...) == 128)`

**证据**：`02-airymaxrt-solution-review-v2.1.md:260-282`

#### 2.2.4 L3 安全治理禁令被违反

- `30-interfaces/05-runtime-interfaces/03-l3-security-governance.md:306`：`AIRY_EINVAL | -1`（L3 标准）
- `10-architecture/06-iron9-shared-model.md:215`：`AIRY_EINVAL (-22)`（违反 L3 标准）
- L3 第 5.3 节禁令 #1 明确"禁止多套并行错误码系统"，但 06-iron9 仍用 -22

**证据**：`02-airymaxrt-solution-review-v2.1.md:87-91, 328-336`

### 2.3 agentrt-linux 方案（A3）— 70/C+

**评分变化：v1.0=80/B → v2.1=70/C+（-10）**

#### 2.3.1 4 项 P0 全部未修复

**P0-1：IPC 消息头布局互不兼容**（`01-systematic-recheck-v2.1.md:55-101`）

- `contracts.md:42`（SSoT 声明）：声明字段顺序为 magic/opcode/flags/trace_id/timestamp_ns/src_task/dst_task/payload_len/reserved[84]——与 SSoT Layout C 一致
- `contracts.md:49-57`（字段语义表）：实际使用 magic/version/type/payload_len/flags/src_pid/dst_pid/trace_id/timestamp_ns/reserved[72]——与 SSoT 不兼容
- 字段累加 = 4+2+2+4+4+4+4+8+8+72 = **112 字节**，但文档声称 128B
- **结论**：contracts.md 内部自相矛盾（line 42 声明 SSoT 但 49-57 用旧布局）

**P0-2：syscall 数量自相矛盾**（`01-systematic-recheck-v2.1.md:104-119`）

- `01-kernel.md:99`（§1.3）：12 核心 + 12 预留 = 24 槽位
- `01-kernel.md:463`（§5.5）：`将 syscall 数量从 12 缩减到 10` ← 矛盾点
- `01-kernel.md:786`（§10.1.7）：12 核心 + 12 预留 = 24 槽位
- **结论**：§1.5 "12→10" 与 §1.3/§10.1.7 均 12 直接矛盾

**P0-3：子仓库命名系统性矛盾**（`01-systematic-recheck-v2.1.md:122-146`）

- 开源文档：裸名（kernel, services, ...）— `06-directory-structure.md:175-184`
- 闭源文档：`airymaxos-` 前缀 **401 处**/37 文件
- **结论**：开源裸名 vs 闭源前缀，命名系统性不一致

**P0-4：IPC 操作码碎片化**（`01-systematic-recheck-v2.1.md:149-196`）

| 来源 | 操作码数 | 值范围 | 兼容性 |
|------|---------|--------|--------|
| SSoT（`120-cross-project-code-sharing.md:309-313`） | 4 个 | SEND=0, RECV=1, SEND_BATCH=2, CANCEL=3 | 权威 |
| `02-services.md:317` | 5 个 | NOP/SEND/RECV/MSG_RING/SEND_ZC | ❌ 不兼容 |
| `04-ipc-versioning.md:353-365` | 11 个 | NOP=0x00 ~ RELIABLE_SEND=0x60 | ❌ 完全不兼容 |

- SSoT `SEND=0` vs ipc-versioning.md `NOP=0x00`——编号冲突
- ipc-versioning.md 引用不存在的 `hdr->version` 字段（lines 88/383/727），SSoT Layout C 无 version 字段
- **结论**：3 套互不兼容的操作码定义，编号互相冲突

#### 2.3.2 正面进展

| 项目 | 状态 | 证据 |
|------|------|------|
| IPC magic 值 0x41524531 | ✅ 唯一 | 全文一致 |
| 任务 magic 值 0x41475453 | ✅ 唯一 | 全文一致 |
| seL4 三态机（EPState_Idle/Send/Recv） | ✅ 对齐 | `02-ipc-protocol.md:336` |
| doReplyTransfer 临界区串行 | ✅ 借鉴 | `02-ipc-protocol.md:354-388` |
| Fastpath POINT OF NO RETURN | ✅ 吸收 | `03-microkernel-strategy.md:288-301` |
| 8 子仓映射完整 | ✅ 通过 | `06-directory-structure.md:175-184` |
| 14 ADR 全部 Accepted | ✅ 通过 | `05-adrs.md:35-48` |
| IRON-9 v2 三层模型定义清晰 | ✅ 唯一 | `120-cross-project-code-sharing.md:43-51` |

### 2.4 OpenStandards 开放标准（A4）— v2.0=2.6/10 → v2.1 目标=7.9/10（+5.3）

**实际状态：v2.0 优化建议 0/6 落地，当前仍为 v1.1 草案状态，评分 2.6/10 = 26/100**

#### 2.4.1 v2.0 优化建议落地率 0/6

| # | v2.0 建议 | 落地状态 | 严重等级 |
|---|----------|---------|---------|
| 1 | 错误码统一为 03 SEC SSoT | ❌ 完全未落地（三套方案 + 双码同值 + 值冲突） | 致命 |
| 2 | are_cap_t → airy_cap_t | ❌ 完全未落地（发现第三变体 cap_t） | 高 |
| 3 | [SC]/[SS]/[IND] 标注补齐 | ⚠️ 部分落地（01 零标注，02-06 仅引言，07 完整） | 中 |
| 4 | 9+1 主题体系（新增 08/09/10） | ❌ 完全未落地（三文件均不存在） | 高 |
| 5 | 许可证变更为 CC-BY-4.0/Apache | ❌ 完全未落地（仍 AGPL+Apache） | 高 |
| 6 | MCP/A2A/OpenTelemetry 互操作 | ❌ 完全未落地（零桥接契约） | 致命 |

**证据**：`01-open-standards-review-v2.1.md:184-195`

#### 2.4.2 错误码三套方案并行 + 05 COG 双码同值 BUG

| 方案 | 适用标准 | EINVAL | ENOMEM | EPERM | EBUSY |
|------|---------|--------|--------|-------|-------|
| A（POSIX 风格） | 01 RT / 02 IPC | -2 | -3 | -22 | -16 |
| B（分段式） | 03 SEC / 04 MEM / 06 SCHED | -2 | -1100 | -1302 | -1601 |
| C（连续小整数） | 07 SYS | -1 | -2 | -4 | -9 |

**致命 BUG**：
- `05 COG:411-412`：`EBUDGET=-1004` AND `TIMEOUT=-1004`——两个不同语义错误码取相同值，调用方无法区分 Token 耗尽与超时
- `04 MEM:512` / `06 SCHED:455`：`ENOENT=-2` 与 `EINVAL=-2` 冲突

**证据**：`01-open-standards-review-v2.1.md:91-108, 1133-1167`

#### 2.4.3 命名三种变体

| 变体 | 出现次数 | 文件 |
|------|---------|------|
| `are_cap_t`（错误） | 26 处 | 03 SEC 22 处 + 01 RT 1 处 + 02 IPC 3 处 |
| `cap_t`（第三变体，v2.0 未识别） | 8 处 | 07 SYS 8 处 |
| `airy_cap_t`（正确） | **0 处** | 全部 8 文件零使用 |

**证据**：`01-open-standards-review-v2.1.md:110-126, 1169-1182`

#### 2.4.4 可独立实现性仅 27% 语言中立

| 评估结果 | 数量 | 占比 |
|---------|------|------|
| ✅ 真正语言中立 | 3/11 | 27% |
| ⚠️ 部分中立 | 4/11 | 36% |
| ❌ C 语言绑定 | 4/11 | 36% |

**结论**：第三方独立实现者无法仅依据规范文本完成实现，必须参考 agentrt C 源码——违反"开放标准"核心承诺。

**证据**：`01-open-standards-review-v2.1.md:675-731`

#### 2.4.5 治理 SPHARX 中心化

| 治理维度 | 当前状态 | 行业标杆 |
|---------|---------|---------|
| 标准总维护者 | SPHARX 任命，最终裁决权 | OCI Chair 由 TOB 选举 |
| 商标持有方 | SPHARX Ltd. | OCI Trademark Board / Linux Foundation |
| 法律实体 | 无独立法律实体 | OCI/CNCF（LF 旗下） |
| 行为准则 | 不存在 | LF CoC / CNCF CoC |
| CLA/DCO | 不存在 | CNCF DCO + CLA |

**结论**：单一公司主导使本体系无法被认定为"行业开放标准"，实质上是"公司开放标准"。

**证据**：`01-open-standards-review-v2.1.md:258-279`

#### 2.4.6 行业生态差距加速扩大

| 协议/标准 | 2026 H1 状态 | Airymax 对接 |
|----------|-------------|-------------|
| MCP | 2026-07-28 RC（无状态化 + Extensions） | ❌ 零对接 |
| A2A | v1.2（Signed AgentCard） | ❌ 零对接 |
| IETF IAIP | 5 草案并行 | ❌ 零对接 |
| OpenAI Agents SDK | 2026-04（Sandbox + Harness） | ❌ 零对接 |
| OCI-AI | v1.3 强制实施 | ❌ 零对接 |
| LangGraph / CrewAI | 0.2.x / 0.95.x | ❌ 零对接 |

**证据**：`01-open-standards-review-v2.1.md:428-640`

### 2.5 文档规范与质量控制（A5）— 68/C+

**评分变化：v1.0=58/D+ → v2.1=68/C+（+10）**

#### 2.5.1 内部审查描述清理 12/13 关键词零残留

13 个关键词 Grep 检查中 **12 个零残留**，仅"审查状态"2 处匹配均为合法技术内容（PR 模板字段 + C 结构体注释）。

**证据**：`03-docs-quality-review-v2.1.md:62-91`

#### 2.5.2 URL 格式 100% https 转换完成

- `git@atomgit.com` SSH 格式：0 匹配 ✅
- `git@` 通用 SSH 格式：0 匹配 ✅
- 49 处 atomgit.com 全部 https:// 格式 ✅

**证据**：`03-docs-quality-review-v2.1.md:136-170`

#### 2.5.3 断裂引用系统性恶化（v1.0 ~10 处 → v2.1 67+ 处跨 34 文件）

| 断裂类型 | 处数 | 文件数 | v1.0 标记 | v2.1 状态 |
|---------|------|--------|----------|----------|
| `docs/AirymaxOS/TERMINOLOGY.md`（已迁移） | 3 | 3 | ✅ 1 处 | ❌ 未修复，扩散至 3 处 |
| `08-compliance-checklist.md`（已合并） | 8+ | 8 | ❌ | ❌ 新增 |
| `00-basic-theories/`（目录不存在） | 25 | 9 | ❌ | ❌ 未修复 |
| `30-coding-standard/`（目录不存在） | 23 | 9 | ❌ | ❌ 新增 |
| `PROTOCOL_GUIDE.md`（文件名错误） | 4 | 1 | ❌ | ❌ 新增 |
| `../../../DocsClosed/0.1.1详细任务清单.md`（跨边界） | 4 | 4 | ❌ | ❌ 新增 |
| **合计** | **67+** | **34** | — | **全部未修复** |

**证据**：`03-docs-quality-review-v2.1.md:350-361`

#### 2.5.4 开源/闭源边界违规（3 内部审查目录越界 + 4 处跨引用）

| 违规类型 | 详情 |
|---------|------|
| 3 个 `_research_v*` 目录越界 | `docs/OpenStandards/_research_v1.0/v2.0/v2.1/` 物理路径在开源工作树（虽未跟踪但已违反边界） |
| 4 处 DocsClosed/ 跨引用 | `06-ipc/README.md:61` / `07-rpc-api/README.md:82` / `08-service-discovery/README.md:68` / `01-sdk/README.md:72` |

**证据**：`03-docs-quality-review-v2.1.md:93-121, 193-219`

#### 2.5.5 闭源前缀迁移停滞（606 处 agentrt_* 残留）

| 仓库 | agentrt_* 残留 | airy_* 已迁移 |
|------|---------------|--------------|
| `docs-closed/agentrt/` | 218 处/12 文件 | 163 处（手册） |
| `docs-closed/agentrt-linux/` | 388 处/34 文件 | **0 处**（手册完全未迁移） |
| **合计** | **606 处** | — |

**矛盾点**：手册 §1518-1524 标注 `agentrt_*` 为"已废弃"，但手册自身代码示例（§1578、§3176-3226）仍使用 `agentrt_*` 前缀。

**证据**：`03-docs-quality-review-v2.1.md:476-555`

---

## 3. v1.0 → v2.1 问题修复情况对比表

按优先级（P0/P1/P2）列出 v1.0 已识别问题及 v2.1 修复状态。

### 3.1 P0 级问题（阻断项，共 15 项）

| # | 维度 | 问题 | v2.1 状态 | 证据 |
|---|------|------|----------|------|
| 1 | A1 | `.clang-format` 不存在 | ❌ 未修复 | `01-agentrt-source-review-v2.1.md:41-51` |
| 2 | A1 | 4 空格缩进全面违规（vs Tab 8） | ❌ 未修复 | `01-agentrt-source-review-v2.1.md:53-61` |
| 3 | A1 | fprintf 直接使用违反 banned_functions | ❌ 未修复 | `01-agentrt-source-review-v2.1.md:74-83` |
| 4 | A1 | memory.c malloc/free 与 AIRY_FREE 混用 | ❌ 未修复 | `01-agentrt-source-review-v2.1.md:129-138` |
| 5 | A2 | 错误码 6 套并行 | ❌ 未修复（仍 4+ 套） | `02-airymaxrt-solution-review-v2.1.md:62-101` |
| 6 | A2 | "操作系统"定位与用户态运行时矛盾 | ⚠️ 加剧（40→51 行） | `02-airymaxrt-solution-review-v2.1.md:102-133` |
| 7 | A2 | [SC] 头文件清单与 SSoT 不一致 | ⚠️ 倒退（#6→#1，syscalls.h 缺失） | `02-airymaxrt-solution-review-v2.1.md:134-160` |
| 8 | A2 | IPC 消息头结构体三重违规 | ⚠️ 蔓延（1→2 文件） | `02-airymaxrt-solution-review-v2.1.md:254-283` |
| 9 | A2 | 29 仓拆分完全未文档化 | ❌ 未修复（0 处提及） | `02-airymaxrt-solution-review-v2.1.md:300-311` |
| 10 | A3 | IPC 消息头布局互不兼容（112B vs 128B） | ❌ 未修复 | `01-systematic-recheck-v2.1.md:55-101` |
| 11 | A3 | syscall 数量自相矛盾（12 vs 10） | ❌ 未修复 | `01-systematic-recheck-v2.1.md:104-119` |
| 12 | A3 | 子仓库命名系统性矛盾 | ❌ 未修复（401 处 airymaxos-） | `01-systematic-recheck-v2.1.md:122-146` |
| 13 | A3 | IPC 操作码碎片化（4/5/11 套） | ❌ 未修复（3 套不兼容） | `01-systematic-recheck-v2.1.md:149-196` |
| 14 | A5 | 断裂引用系统性扩散 | ⚠️ 倒退（10→67+ 处） | `03-docs-quality-review-v2.1.md:350-361` |
| 15 | A5 | 开源/闭源边界违规 | ⚠️ 倒退（3 目录 + 4 跨引用） | `03-docs-quality-review-v2.1.md:193-219` |

**P0 汇总**：15 项中 **0 项完全修复**、**0 项部分修复**、**9 项未修复**、**6 项倒退/加剧**

### 3.2 P1 级问题（重要项，共 13 项）

| # | 维度 | 问题 | v2.1 状态 | 证据 |
|---|------|------|----------|------|
| 1 | A1 | agentrt-linux 空仓库 | ⚠️ 部分修复（脚手架已建，0 源码） | `01-agentrt-source-review-v2.1.md:63-73` |
| 2 | A1 | Windows localtime 线程不安全 | ⚠️ 部分修复（POSIX 已修，Windows 未修） | `01-agentrt-source-review-v2.1.md:85-94` |
| 3 | A1 | typedef struct _t 命名违规 | ❌ 未修复（421 处/100 文件） | `01-agentrt-source-review-v2.1.md:96-105` |
| 4 | A2 | Cupola vs Cupolas 术语不一致 | ⚠️ 加剧（4→5 文件） | `02-airymaxrt-solution-review-v2.1.md:161-184` |
| 5 | A2 | Daemon 数量标注冲突（10 vs 12） | ❌ 未修复 | `02-airymaxrt-solution-review-v2.1.md:186-202` |
| 6 | A2 | MemoryRovol 层级命名冲突 | ❌ 未修复 | `02-airymaxrt-solution-review-v2.1.md:204-217` |
| 7 | A2 | agentrt_* 专属 API 前缀缺失 | ❌ 未修复（0 处使用） | `02-airymaxrt-solution-review-v2.1.md:312-320` |
| 8 | A3 | 双重宏命名（AIRY_IPC_HDR_SZ vs MSG_HDR_SIZE） | ❌ 未修复（19 处） | `01-systematic-recheck-v2.1.md:199-227` |
| 9 | A3 | 字段命名不一致（src_task vs src_pid） | ❌ 未修复（51 处） | `01-systematic-recheck-v2.1.md:230-257` |
| 10 | A3 | contracts.md 112→128 字节 | ❌ 未修复 | `01-systematic-recheck-v2.1.md:277-298` |
| 11 | A3 | 控制平面数量误导（7 vs 8） | ❌ 未修复 | `01-systematic-recheck-v2.1.md:301-317` |
| 12 | A5 | 闭源 agentrt_ → airy_ 前缀迁移停滞 | ❌ 未修复（606 处） | `03-docs-quality-review-v2.1.md:476-555` |
| 13 | A5 | 闭源文档准确性 | ⚠️ 倒退（前缀迁移严重滞后） | `03-docs-quality-review-v2.1.md:457-590` |

**P1 汇总**：13 项中 **0 项完全修复**、**3 项部分修复**、**8 项未修复**、**2 项倒退**

### 3.3 P2 级问题（次要项，共 12 项）

| # | 维度 | 问题 | v2.1 状态 | 证据 |
|---|------|------|----------|------|
| 1 | A1 | ASCII 装饰分节符 `/* ====` | ❌ 未修复（590 处/100 文件） | `01-agentrt-source-review-v2.1.md:107-116` |
| 2 | A1 | banned_functions 合规机制 | ⚠️ 部分修复（基础设施完善） | `01-agentrt-source-review-v2.1.md:118-128` |
| 3 | A1 | 中文注释尾部 `?` 截断 | ❌ 未修复（logging.c 10+ 处） | `01-agentrt-source-review-v2.1.md:140-149` |
| 4 | A2 | 06-iron9-shared-model.md 递归注释 | ❌ 未修复（行 214 仍存在） | `02-airymaxrt-solution-review-v2.1.md:284-291` |
| 5 | A2 | TERMINOLOGY.md 路径头错误 | ❌ 未修复（行 8 仍错误） | `02-airymaxrt-solution-review-v2.1.md:293-299` |
| 6 | A3 | io_uring SETUP 互斥标志列为"必须启用" | ❌ 未修复 | `01-systematic-recheck-v2.1.md:322-335` |
| 7 | A3 | ES-OLK 映射缺乏具体代码示例 | ⚠️ 部分修复 | `01-systematic-recheck-v2.1.md:338-354` |
| 8 | A3 | seL4 约束在 contracts.md 被违反 | ⚠️ 部分修复 | `01-systematic-recheck-v2.1.md:357-371` |
| 9 | A3 | 各模块里程碑命名约定不一致 | ❌ 未修复 | `01-systematic-recheck-v2.1.md:374-394` |
| 10 | A3 | 03-ipc-flow.md 引用不存在的 src_pid/dst_pid | ❌ 未修复 | `01-systematic-recheck-v2.1.md:396-411` |
| 11 | A5 | 内部审查描述清理 | ✅ 大部分修复（12/13 关键词零残留） | `03-docs-quality-review-v2.1.md:62-91` |
| 12 | A5 | URL 格式一致性 | ✅ 完全修复（100% https） | `03-docs-quality-review-v2.1.md:136-170` |

**P2 汇总**：12 项中 **2 项完全修复**、**3 项部分修复**、**7 项未修复**

### 3.4 总修复率

| 优先级 | 总数 | ✅ 完全修复 | ⚠️ 部分修复/倒退 | ❌ 未修复 | 完全修复率 |
|--------|------|------------|-----------------|----------|-----------|
| P0 | 15 | 0 | 6 | 9 | **0%** |
| P1 | 13 | 0 | 3 | 8 | **0%** |
| P2 | 12 | 2 | 3 | 7 | **17%** |
| **合计** | **40** | **2** | **12** | **24** | **5%** |

---

## 4. v2.1 新发现问题清单

v1.0 未识别、v2.1 新发现的问题，按维度分组。

### 4.1 A1 新发现（agentrt 源码）

| # | 严重级别 | 问题 | 证据 |
|---|---------|------|------|
| A1-N1 | P0 | 错误码 SSoT 冲突——AIRY_SUCCESS 3 处 + AIRY_OK 1 处 | `01-agentrt-source-review-v2.1.md:174-181` |
| A1-N2 | P0 | airy_err_t 重复 typedef（airy_types.h:40 + types.h:62） | `01-agentrt-source-review-v2.1.md:183-190` |
| A1-N3 | P0 | 危险警告抑制 -Wfree-nonheap-object（cupolas_network_security.c:94-100） | `01-agentrt-source-review-v2.1.md:192-199` |
| A1-N4 | P1 | .bak 文件含 43 处 agentrt_ 残留（triple_coordinator.c.bak） | `01-agentrt-source-review-v2.1.md:203-210` |
| A1-N5 | P1 | 39 处 #pragma GCC diagnostic ignored 警告抑制/22 文件 | `01-agentrt-source-review-v2.1.md:212-219` |
| A1-N6 | P1 | 35 处函数内 static char 缓冲区（线程不安全）/28 文件 | `01-agentrt-source-review-v2.1.md:221-228` |
| A1-N7 | P1 | agent_registry_core_get() 数据竞争未修复（L123-137, L194-208） | `01-agentrt-source-review-v2.1.md:230-238` |
| A1-N8 | P1 | cupolas 错误码 4 种命名变体（41 处/3 文件） | `01-agentrt-source-review-v2.1.md:240-247` |

### 4.2 A2 新发现（AirymaxRT 方案）

| # | 严重级别 | 问题 | 证据 |
|---|---------|------|------|
| A2-N1 | P0 | L3 安全治理禁令被 06-iron9-shared-model.md:215-216 违反 | `02-airymaxrt-solution-review-v2.1.md:328-337` |
| A2-N2 | P0 | [SC] 头文件清单 6 个全部错位（v1.0 仅发现第 6 位） | `02-airymaxrt-solution-review-v2.1.md:339-342` |
| A2-N3 | P0 | IPC 头违规蔓延至 02-l2-service-protocol.md | `02-airymaxrt-solution-review-v2.1.md:344-349` |
| A2-N4 | P1 | 03-overall-architecture.drawio 含 11 处 Cupola 单数（v1.0 漏检） | `02-airymaxrt-solution-review-v2.1.md:352-363` |
| A2-N5 | P1 | 50-specifications/06-glossary-index.md 与 20-modules 版本内容重复但宏名不一致（AGENTRT_SECURE_ZERO vs AIRY_SECURE_ZERO） | `02-airymaxrt-solution-review-v2.1.md:389-394` |

### 4.3 A3 新发现（agentrt-linux 方案）

| # | 严重级别 | 问题 | 证据 |
|---|---------|------|------|
| A3-N1 | P0 | contracts.md 内部自相矛盾（line 42 声明 SSoT 但 49-57 用旧布局） | `01-systematic-recheck-v2.1.md:94-100` |
| A3-N2 | P0 | ipc-versioning.md 引用不存在的 version 字段（lines 88/383/727） | `01-systematic-recheck-v2.1.md:186-189, 451-454` |
| A3-N3 | P0 | 操作码 3 套完全互不兼容（值冲突：SEND=0 vs NOP=0x00） | `01-systematic-recheck-v2.1.md:149-196` |
| A3-N4 | P1 | 标志位命名前缀不一致（contracts.md AIRY_IPC_FLAG_* vs SSoT AIRY_IPC_F_*） | `01-systematic-recheck-v2.1.md:449-455` |

### 4.4 A4 新发现（OpenStandards）

| # | 严重级别 | 问题 | 证据 |
|---|---------|------|------|
| A4-N1 | P0 | 05 COG 双码同值 BUG（TIMEOUT=-1004 = EBUDGET=-1004） | `01-open-standards-review-v2.1.md:99` |
| A4-N2 | P0 | 04 MEM/06 SCHED ENOENT=-2 与 EINVAL=-2 冲突 | `01-open-standards-review-v2.1.md:98, 100` |
| A4-N3 | P0 | 07 SYS 第三套完全独立错误码方案（-1~-12） | `01-open-standards-review-v2.1.md:101` |
| A4-N4 | P1 | 07 SYS 第三种命名变体 cap_t（8 处，v2.0 未识别） | `01-open-standards-review-v2.1.md:117` |
| A4-N5 | P1 | README 头部版本回退（1.0 vs 历史 1.1）+ "六大领域"错描述（实际 7 域） | `01-open-standards-review-v2.1.md:152` |
| A4-N6 | P1 | README 第 144 行虚假承诺（"测试套件代码以 Apache-2.0 发布"但代码不存在） | `01-open-standards-review-v2.1.md:253-256` |
| A4-N7 | P1 | 治理 SPHARX 中心化（无独立法律实体 + 商标归单一公司 + 无 CoC/CLA） | `01-open-standards-review-v2.1.md:258-279` |

### 4.5 A5 新发现（文档规范与质量控制）

| # | 严重级别 | 问题 | 证据 |
|---|---------|------|------|
| A5-N1 | P0 | 08-compliance-checklist.md 断裂引用 8+ 处（文件已合并但引用未更新） | `03-docs-quality-review-v2.1.md:269-283` |
| A5-N2 | P0 | 00-basic-theories/ 目录断裂引用 25 处/9 文件 | `03-docs-quality-review-v2.1.md:285-310` |
| A5-N3 | P0 | 30-coding-standard/ 目录断裂引用 23 处/9 文件 | `03-docs-quality-review-v2.1.md:312-336` |
| A5-N4 | P1 | 3 个 _research 内部审查目录误入开源工作树 | `03-docs-quality-review-v2.1.md:93-121` |
| A5-N5 | P1 | 4 处开源文档跨引用闭源 DocsClosed/0.1.1详细任务清单.md | `03-docs-quality-review-v2.1.md:203-219` |
| A5-N6 | P1 | 4 个邮箱域名未统一（.cn/.com/.io/.dev） | `03-docs-quality-review-v2.1.md:690-705` |

### 4.6 新发现问题汇总

| 优先级 | A1 | A2 | A3 | A4 | A5 | 合计 |
|--------|----|----|----|----|----|------|
| P0 | 3 | 3 | 3 | 3 | 3 | **15** |
| P1 | 5 | 2 | 1 | 4 | 3 | **15** |
| **合计** | 8 | 5 | 4 | 7 | 6 | **30** |

---

## 5. 跨维度交叉问题分析

### 5.1 错误码 SSoT 冲突横跨 A1/A2/A4 三个维度

**这是 v2.1 审查发现的最严重系统性问题，错误码冲突贯穿源码、方案文档和开放标准三个层面。**

| 维度 | 表现 | 证据 |
|------|------|------|
| A1（源码） | AIRY_SUCCESS 3 处定义 + AIRY_OK 1 处 + airy_err_t 重复 typedef | `airy_types.h:67`, `types.h:67`, `error_compat.h:298`, `error.h:43` |
| A2（AirymaxRT） | 4+ 套方案并行（A: -1 / B: -22 / C: EINVAL / D: 1001 / E: ARE_* / F: AIRY_OK） | `03-l3-security-governance.md:306`, `06-iron9-shared-model.md:215`, `05-syscall.md:644`, `01-l1-runtime-interface.md:52` |
| A4（OpenStandards） | 三套方案（01RT/02IPC POSIX 风格 / 03SEC分段式 / 07SYS 连续小整数）+ 05 COG 双码同值 BUG | `01-open-standards-review-v2.1.md:91-108` |

**影响**：开发者无法确定应使用哪套错误码；C 代码编译将出现宏重定义冲突；违反 IRON-1（用户空间 ABI 永不破坏）和 IRON-014（[SC] 共享契约层单一数据源）。

### 5.2 [SC] 头文件清单问题横跨 A2/A3 两个维度

| 维度 | 表现 | 证据 |
|------|------|------|
| A2（AirymaxRT） | `06-iron9-shared-model.md` 将 bpf_struct_ops.h 列第 1 位，syscalls.h 完全缺失 | `06-iron9-shared-model.md:68` |
| A3（agentrt-linux） | SSoT（`120-cross-project-code-sharing.md:65-76`）正确定义，但 contracts.md 使用旧布局 112B | `contracts.md:49-57` |

**根因**：`06-iron9-shared-model.md` 未对齐 SSoT `120-cross-project-code-sharing.md`，导致下游消费者（IPC/syscall 文档）引用错误布局。

### 5.3 agentrt_* → airy_* 前缀迁移横跨 A1/A5 两个维度

| 维度 | 表现 | 证据 |
|------|------|------|
| A1（源码） | `triple_coordinator.c.bak` 含 43 处 agentrt_ 残留 | `01-agentrt-source-review-v2.1.md:203-210` |
| A5（文档） | 闭源文档 606 处 agentrt_* 残留（agentrt 218 + agentrt-linux 388） | `03-docs-quality-review-v2.1.md:476-555` |

**矛盾点**：源码已迁移至 airy_*，但闭源工程标准手册仍使用 agentrt_* 且标注"已废弃"——手册内容自相矛盾。

### 5.4 IPC 消息头布局问题横跨 A2/A3 两个维度

| 维度 | 表现 | 证据 |
|------|------|------|
| A2（AirymaxRT） | `are_ipc_message_header_t` 13-14 字段 / 无 packed / `char source[32]` / 2 文件违规 | `06-ipc/README.md:27-42`, `02-l2-service-protocol.md:60-109` |
| A3（agentrt-linux） | contracts.md 112B 旧布局（version/type/src_pid/dst_pid）vs SSoT 128B（opcode/src_task/dst_task） | `contracts.md:49-57` |

**vs SSoT**：`airy_ipc_msg_hdr` / 8 字段 / `__attribute__((packed))` / `_Static_assert(sizeof(...) == 128)`

**影响**：IPC 消息头布局未统一前，无法实现 IPC 协议；字段集不兼容导致跨进程通信失败。

---

## 6. 综合评分

### 6.1 五维度加权综合评分

| 维度 | 权重 | v1.0 评分 | v1.0 加权 | v2.1 评分 | v2.1 加权 | 变化 |
|------|------|----------|----------|----------|----------|------|
| A1 agentrt 源码 | 25% | 25 | 6.25 | 32 | 8.00 | +1.75 |
| A2 AirymaxRT 方案 | 20% | 62 | 12.40 | 58 | 11.60 | -0.80 |
| A3 agentrt-linux 方案 | 20% | 80 | 16.00 | 70 | 14.00 | -2.00 |
| A4 OpenStandards | 20% | 26 | 5.20 | 26 | 5.20 | 0.00 |
| A5 文档质控 | 15% | 58 | 8.70 | 68 | 10.20 | +1.50 |
| **综合** | **100%** | **48.6** | — | **49.0** | — | **+0.4** |

### 6.2 v1.0 → v2.1 综合评分变化

| 项目 | v1.0 | v2.1 | 变化 |
|------|------|------|------|
| 综合评分 | 48.6/100 (F) | 49.0/100 (F/E+) | +0.4 |
| 综合等级 | F | F/E+ | 持平 |
| 距 80/B 门槛 | -31.4 | -31.0 | 持平 |

### 6.3 进入 1.0.1 M1 代码开发的就绪度判定

**判定标准**：≥80/B 为达标

**当前评分**：49.0/100（F/E+）

**判定结果**：❌ **未达标**（差距 31 分）

**评分构成分析**：
- A1（源码 32 分）拖累综合评分 -12 分（vs 80 分门槛的 25% 权重）
- A2（方案 58 分）拖累综合评分 -4.4 分
- A3（方案 70 分）拖累综合评分 -2.0 分
- A4（标准 26 分）拖累综合评分 -10.8 分
- A5（文档 68 分）拖累综合评分 -1.8 分

**主要短板**：A1 源码质量（32 分）和 A4 开放标准（26 分）是最大的拖累项。

---

## 7. 优先级修复路线图

### 7.1 P0 阻断项（必须 M1 启动前修复）

| # | 维度 | 问题 | 工作量 | 责任 agent | 证据 |
|---|------|------|--------|-----------|------|
| P0-1 | A1 | 统一 AIRY_SUCCESS 定义为 airy_types.h 唯一 SSoT | 4h | A1 | `01-agentrt-source-review-v2.1.md:400` |
| P0-2 | A1 | 删除 types.h:62 的 airy_err_t 重复 typedef | 1h | A1 | `01-agentrt-source-review-v2.1.md:402` |
| P0-3 | A1 | 修复 cupolas_network_security.c 的 -Wfree-nonheap-object 抑制 | 8h | A1 | `01-agentrt-source-review-v2.1.md:403` |
| P0-4 | A1 | 创建 .clang-format（IndentWidth: 8 + UseTab: Always） | 2h | A1 | `01-agentrt-source-review-v2.1.md:404` |
| P0-5 | A1 | 执行全量 clang-format -i 批量重格式化 | 16h | A1 | `01-agentrt-source-review-v2.1.md:405` |
| P0-6 | A1 | memory.c fprintf → airy_log_write；heapstore_migration.c 改用封装 | 8h | A1 | `01-agentrt-source-review-v2.1.md:406` |
| P0-7 | A1 | memory.c malloc/free 统一为 AIRY_MALLOC/AIRY_FREE | 8h | A1 | `01-agentrt-source-review-v2.1.md:407` |
| P0-8 | A2 | 统一错误码体系（8 文件修正） | 8h | A2 | `02-airymaxrt-solution-review-v2.1.md:623-637` |
| P0-9 | A2 | 消除"操作系统"定位冲突（9 文件） | 4h | A2 | `02-airymaxrt-solution-review-v2.1.md:639-653` |
| P0-10 | A2 | 修正 [SC] 头文件清单（06-iron9-shared-model.md） | 1h | A2 | `02-airymaxrt-solution-review-v2.1.md:655-674` |
| P0-11 | A2 | 修正 IPC 消息头三重违规（2 文件重写） | 4h | A2 | `02-airymaxrt-solution-review-v2.1.md:676-693` |
| P0-12 | A2 | 修正文件路径引用错误（~12 文件） | 4h | A2 | `02-airymaxrt-solution-review-v2.1.md:695-711` |
| P0-13 | A3 | 统一 IPC 消息头布局（contracts.md 字段表全文替换） | 4h | A3 | `01-systematic-recheck-v2.1.md:813` |
| P0-14 | A3 | 收敛 IPC 操作码（services.md + ipc-versioning.md 统一到 SSoT 4 个） | 6h | A3 | `01-systematic-recheck-v2.1.md:815` |
| P0-15 | A3 | 统一 syscall 数量（删除 §5.5 "12→10"） | 0.5h | A3 | `01-systematic-recheck-v2.1.md:816` |
| P0-16 | A3 | 统一子仓命名（闭源 401 处 airymaxos- → 裸名） | 6h | A3 | `01-systematic-recheck-v2.1.md:817` |
| P0-17 | A4 | 错误码 SSoT 强制统一（7 标准对齐） | 1 周 | A4 | `01-open-standards-review-v2.1.md:741` |
| P0-18 | A4 | airy_cap_t 全量改名（34 处） | 0.5 周 | A4 | `01-open-standards-review-v2.1.md:742` |
| P0-19 | A4 | README 版本一致性修复 + 断裂引用修正 | 0.2 周 | A4 | `01-open-standards-review-v2.1.md:743-744` |
| P0-20 | A5 | 修复断裂引用系统性扩散（67+ 处/34 文件） | 8h | A5 | `03-docs-quality-review-v2.1.md:816-833` |
| P0-21 | A5 | 修复开源/闭源边界违规（3 目录迁移 + 4 跨引用删除） | 2h | A5 | `03-docs-quality-review-v2.1.md:835-851` |

**P0 合计：~85h + 1.7 周**

### 7.2 P1 重要项（M1 期间修复）

| # | 维度 | 问题 | 工作量 |
|---|------|------|--------|
| P1-1 | A1 | 删除 triple_coordinator.c.bak + .gitignore 添加 *.bak | 1h |
| P1-2 | A1 | 审查 39 处 #pragma GCC diagnostic ignored | 8h |
| P1-3 | A1 | 35 处 static char 缓冲区改为调用方传入或 _Thread_local | 16h |
| P1-4 | A1 | agent_registry_core_get() 数据竞争修复 | 4h |
| P1-5 | A1 | cupolas 错误码 4 变体统一为 AIRY_ERR_* | 8h |
| P1-6 | A1 | typedef struct _t 分批重构 | 32h |
| P1-7 | A1 | agentrt-linux kernel 子仓填充微内核核心代码 | 80h |
| P1-8 | A2 | 统一 Cupola/Cupolas 术语（5 文件） | 2h |
| P1-9 | A2 | 修正 daemon 数量标注（10→12） | 0.5h |
| P1-10 | A2 | 文档化 29 仓拆分结构 | 6h |
| P1-11 | A2 | 文档化 agentrt_* 专属 API 前缀 | 2h |
| P1-12 | A3 | 统一宏命名（AIRY_IPC_HDR_SZ） | 2h |
| P1-13 | A3 | 统一字段命名（src_task/dst_task，u32→u64） | 4h |
| P1-14 | A3 | 删除 ipc-versioning.md version 字段引用 | 2h |
| P1-15 | A4 | [SC]/[SS]/[IND] 三层标注全量补齐 | 1 周 |
| P1-16 | A4 | 抽取独立 JSON Schema 文件 | 0.5 周 |
| P1-17 | A4 | 许可证分离（CC-BY-4.0 + Apache-2.0） | 0.5 周 |
| P1-18 | A4 | 新增 08 PROTO + 09 INTEROP 域 | 4 周 |
| P1-19 | A5 | 闭源 agentrt_ → airy_ 前缀迁移（606 处） | 12h |
| P1-20 | A5 | 邮箱域名统一（4 域名→1 域名） | 2h |

**P1 合计：~185h + 6 周**

### 7.3 P2 次要项（M1 后修复）

| # | 维度 | 问题 | 工作量 |
|---|------|------|--------|
| P2-1 | A1 | 590 处 ASCII 装饰分节符替换 | 8h |
| P2-2 | A1 | logging.c 中文注释 ? 截断修复 | 2h |
| P2-3 | A1 | AIRY_ERROR_NULL 宏隐式 return 改为显式模式 | 8h |
| P2-4 | A2 | 06-iron9-shared-model.md 递归注释修正 | 0.1h |
| P2-5 | A2 | 充实 00-requirements/ 中英双语文档 | 8h |
| P2-6 | A3 | io_uring 互斥标志修正 | 0.5h |
| P2-7 | A3 | ES-OLK 编号追溯链补全 | 2h |
| P2-8 | A3 | 里程碑命名统一（M0-M8） | 1h |
| P2-9 | A3 | 03-ipc-flow.md 字段引用修正 | 0.5h |
| P2-10 | A3 | Euler API 兼容性文档补充 | 4h |
| P2-11 | A3 | Rust 驱动规范补充 | 8h |
| P2-12 | A4 | MCP 2026-07-28 桥接 | 1.5 周 |
| P2-13 | A4 | A2A v1.2 AgentCard 发布 | 1 周 |
| P2-14 | A4 | OWFa 1.0 专利授权引入 | 1 周 |
| P2-15 | A5 | Go 代码 XXX 占位符替换 | 0.25h |
| P2-16 | A5 | your-team 邮箱标记修正 | 0.08h |

**P2 合计：~44h + 3.5 周**

### 7.4 总工作量估算

| 级别 | 工时 | 周数 | 占比 |
|------|------|------|------|
| P0（阻断） | ~85h | 1.7 周 | 26% |
| P1（重要） | ~185h | 6 周 | 57% |
| P2（次要） | ~44h | 3.5 周 | 13% |
| **合计** | **~314h** | **~11.2 周** | 100% |

---

## 8. 关键决策建议

### 8.1 是否可进入 1.0.1 M1 代码开发

**判定：NO（不可进入）**

**理由**：
1. 综合评分 49/100，距离 80/B 门槛差距 31 分；
2. P0 问题修复率 0%（15 项全部未修复，其中 6 项倒退/加剧）；
3. 错误码 SSoT 冲突横跨 A1/A2/A4 三个维度，代码将基于错误码冲突的文档基础开发；
4. IPC 消息头布局未统一（112B vs 128B），无法实现 IPC 协议；
5. [SC] 头文件清单完全错位，下游消费者引用错误布局；
6. agentrt_* → airy_* 前缀迁移未完成（606 处残留），代码与文档不一致。

### 8.2 优先修复顺序建议

**第一优先级（P0 阻断项，~85h）**：

1. **统一错误码 SSoT**（横跨 A1/A2/A4，~13h）——这是最核心的修复，影响所有维度的正确性
2. **统一 IPC 消息头布局**（横跨 A2/A3，~8h）——影响 IPC 协议正确性
3. **修正 [SC] 头文件清单**（A2，~1h）——影响 IRON-9 v2 三层模型落地
4. **修复断裂引用**（A5，~8h）——影响开源文档可用性
5. **修复边界违规**（A5，~2h）——防止内部审查报告误提交
6. **创建 .clang-format + 批量重格式化**（A1，~18h）——OLK-6.6 合规基础
7. **修复源码 P0 问题**（A1，~21h）——内存安全与错误处理
8. **收敛 IPC 操作码**（A3，~6h）——IPC 操作码分发基础
9. **统一子仓命名**（A3，~6h）——命名一致性
10. **airy_cap_t 全量改名**（A4，~0.5 周）——命名规范

**第二优先级（P1 质量项，M1 期间并行推进，~185h）**

**第三优先级（P2 品味项，M1 后期或 M2，~44h）**

### 8.3 风险提示

| 风险 | 等级 | 缓解措施 |
|------|------|---------|
| L1 契约修改破坏向后兼容 | 高 | 错误码、命名改动设兼容期（别名 + @deprecated），2.0 移除 |
| IPC 消息头布局统一涉及字段类型变更（u32→u64） | 高 | 需全量审计 src_pid/dst_pid → src_task/dst_task 的 51 处引用 |
| 07 SYS 错误码方案与 SSoT 不兼容 | 中 | 保留 -1~-12 作为 syscall 内部码，增加转换函数 |
| 行业生态差距持续扩大 | 高 | v2.1 阶段 2 启动 MCP/A2A 桥接，遏制边缘化风险 |
| 闭源前缀迁移工作量超预期 | 中 | 优先修复工程标准手册（2 本），设计文档与归档可延后 |
| 断裂引用修复后再次因文件迁移扩散 | 中 | CI/CD 引入引用解析检查脚本，文件迁移流程追加引用同步检查 |

---

## 9. 附录

### 附录 A：五大审查报告文件清单

| # | 报告 | 路径 | 行数 |
|---|------|------|------|
| 1 | agentrt 源码 v2.1 深度复审 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt/00-reviews/_review_v2.1/01-agentrt-source-review-v2.1.md` | 537 |
| 2 | AirymaxRT 整体方案 v2.1 复审 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt/00-reviews/_review_v2.1/02-airymaxrt-solution-review-v2.1.md` | 924 |
| 3 | agentrt-linux 方案 v2.1 系统性复审 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt-linux/_review_v2.1/01-systematic-recheck-v2.1.md` | 886 |
| 4 | OpenStandards v2.1 复审 | `/home/spharx/SpharxWorks/OpenAirymax/docs/OpenStandards/_research_v2.1/01-open-standards-review-v2.1.md` | 1241 |
| 5 | 文档规范与质量控制 v2.1 复审 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt/00-reviews/_review_v2.1/03-docs-quality-review-v2.1.md` | 939 |
| — | **合计** | — | **4527** |

### 附录 B：v1.0 → v2.1 评分对比表（完整版）

| 维度 | 子维度 | v1.0 | v2.1 | 变化 |
|------|--------|------|------|------|
| A1 | .clang-format 配置 | 0 | 0 | 0 |
| A1 | Tab 8 缩进合规 | 0 | 5 | +5 |
| A1 | typedef 规范 | 0 | 15 | +15 |
| A1 | goto 集中出口 | 10 | 55 | +45 |
| A1 | 内存安全 | 30 | 35 | +5 |
| A1 | 线程安全 | 40 | 40 | 0 |
| A1 | 错误处理模式 | 50 | 55 | +5 |
| A1 | **综合** | **25/D** | **32/D+** | **+7** |
| A2 | 目录结构完整性 | 70/B- | 68/C+ | -2 |
| A2 | 文档内容深度 | 75/B | 76/B | +1 |
| A2 | 方案冲突 | 45/D+ | 40/D | -5 |
| A2 | 工程标准对齐 | 80/B | 78/B | -2 |
| A2 | 命名前缀 | 72/B- | 70/C+ | -2 |
| A2 | 跨平台一致性 | 78/B | 75/B- | -3 |
| A2 | 29 仓拆分对齐 | 30/F | 30/F | 0 |
| A2 | 草案文档 | 65/C+ | 66/C+ | +1 |
| A2 | IPC 协议一致性 | 55/D+ | 50/D | -5 |
| A2 | **综合** | **62/C+** | **58/C** | **-4** |
| A3 | 内部冲突 | 78 | 62 | -16 |
| A3 | 技术点唯一性 | 85 | 68 | -17 |
| A3 | openEuler 工程实践 | 78 | 80 | +2 |
| A3 | seL4 工程思想 | 82 | 80 | -2 |
| A3 | 开发就绪度 | 78 | 62 | -16 |
| A3 | 细节完成度 | 75 | 68 | -7 |
| A3 | **综合** | **80/B** | **70/C+** | **-10** |
| A4 | 错误码一致性 | 3/10 | 3/10 | 0 |
| A4 | 命名规范 | 4/10 | 4/10 | 0 |
| A4 | [SC]/[SS]/[IND] 标注 | 3/10 | 3/10 | 0 |
| A4 | 主题域完备性 | 4/10 | 4/10 | 0 |
| A4 | 协议生态对接 | 2/10 | 2/10 | 0 |
| A4 | 许可证与专利 | 3/10 | 3/10 | 0 |
| A4 | 治理成熟度 | 2/10 | 2/10 | 0 |
| A4 | **综合** | **2.6/10 (F)** | **2.6/10 (F)** | **0** |
| A5 | 内部审查描述清理 | 60/D | 78/B+ | +18 |
| A5 | URL 格式一致性 | 75/B | 100/A+ | +25 |
| A5 | 开源/闭源边界 | 65/C+ | 55/C | -10 |
| A5 | 断裂引用修复 | 35/D- | 30/D- | -5 |
| A5 | 反抄袭合规 | 80/B+ | 85/B+ | +5 |
| A5 | 闭源文档准确性 | 70/B- | 65/C+ | -5 |
| A5 | 上下游关系描述 | 65/C+ | 78/B+ | +13 |
| A5 | 模板与占位符 | — | 80/B | 新增 |
| A5 | **综合** | **58/D+** | **68/C+** | **+10** |
| — | **加权综合** | **48.6/F** | **49.0/F/E+** | **+0.4** |

### 附录 C：关键证据行号索引

| 证据 | 文件:行号 |
|------|----------|
| AIRY_SUCCESS 3 处定义 | `commons/include/airy_types.h:67`, `commons/utils/types/include/types.h:67`, `commons/utils/error/include/error_compat.h:298` |
| AIRY_OK 1 处定义 | `commons/utils/error/include/error.h:43` |
| airy_err_t 重复 typedef | `commons/include/airy_types.h:40`, `commons/utils/types/include/types.h:62` |
| -Wfree-nonheap-object 抑制 | `cupolas/src/security/cupolas_network_security.c:94-100` |
| [SC] 头文件清单错位 | `06-iron9-shared-model.md:68` vs `120-cross-project-code-sharing.md:65-76` |
| L3 安全治理禁令被违反 | `03-l3-security-governance.md:306` vs `06-iron9-shared-model.md:215` |
| IPC 头违规文件 1 | `30-interfaces/06-ipc/README.md:27-42` |
| IPC 头违规文件 2 | `30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md:60-109` |
| contracts.md 内部矛盾 | `contracts.md:42`（声明 SSoT）vs `contracts.md:49-57`（旧布局 112B） |
| syscall 数量矛盾 | `01-kernel.md:99`（12 核心）vs `01-kernel.md:463`（"从 12 缩减到 10"） |
| IPC 操作码 3 套不兼容 | `120-cross-project-code-sharing.md:309-313`（4 个）vs `02-services.md:317`（5 个）vs `04-ipc-versioning.md:353-365`（11 个） |
| ipc-versioning.md version 字段引用 | `04-ipc-versioning.md:88, 383, 727` |
| 05 COG 双码同值 BUG | `05-airy-cognition-loop-standard.md:411-412`（TIMEOUT=-1004 = EBUDGET=-1004） |
| are_cap_t 26 处 + cap_t 8 处 | `03-airy-security-model-standard.md`（22 处）+ `01-airy-agent-runtime-standard.md:501`（1 处）+ `02-airy-ipc-protocol-standard.md:282,287,305`（3 处）+ `07-airy-syscall-standard.md:207,224,241,258,275,293,326,400`（8 处） |
| 断裂引用 67+ 处 | `docs/OpenStandards/README.md:231` + 8 处 `08-compliance-checklist.md` + 25 处 `00-basic-theories/` + 23 处 `30-coding-standard/` + 4 处 `PROTOCOL_GUIDE.md` + 4 处 `DocsClosed/` |
| agentrt_* 606 处残留 | `docs-closed/agentrt/`（218 处/12 文件）+ `docs-closed/agentrt-linux/`（388 处/34 文件） |
| goto 集中出口 151 处 | 36 文件（v1.0 为 14 处，+978%） |
| IPC magic 0x41524531 | `120-cross-project-code-sharing.md:302-303`（全文一致） |
| 任务 magic 0x41475453 | `120-cross-project-code-sharing.md:236-237`（全文一致） |
| 8 子仓映射 | `06-directory-structure.md:175-184` |
| 14 ADR 全部 Accepted | `05-adrs.md:35-48` |
| seL4 三态机对齐 | `02-ipc-protocol.md:336`（EPState_Idle/Send/Recv） |
| doReplyTransfer 临界区 | `02-ipc-protocol.md:354-388` |
| Fastpath POINT OF NO RETURN | `03-microkernel-strategy.md:288-301` |
| _Static_assert 32 处 | 8 文件（ipc.h、are_ipc.h 等） |
| C11 atomic 280 处 | 49 文件 |
| _Thread_local 8 处 | 6 文件 |
| URL 100% https | 49 处 atomgit.com 全部 https 格式 |
| 内部审查清理 12/13 | 13 关键词 12 个零残留 |

---

> **报告结束** | Airymax v2.1 综合审查报告 | 2026-07-13
> **审查员**：Airymax v2.1 综合审查协调 agent
> **保密级别**：SPHARX Ltd 内部参考，**闭源不公开**
> **SPDX-License-Identifier**：AGPL-3.0-or-later OR Apache-2.0
> **本报告基于 5 个 v2.1 子审查 agent 的独立审查成果汇总生成，所有结论均有具体文件路径和行号证据支撑。**
