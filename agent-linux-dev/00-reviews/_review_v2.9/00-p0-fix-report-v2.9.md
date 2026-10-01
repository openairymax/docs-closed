Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agent-linux P0 问题系统性修复报告（v2.9）

> **报告定位**：agent-linux（AirymaxOS）v2.8 全量文档审查确认的 4 项 P0 问题系统性修复报告，覆盖 P0-014 / P0-016 / P0-017 / P0-018 四项问题的修复方案、修改文件清单、验证结果与残留风险
> **报告版本**：v2.9
> **生成日期**：2026-07-22
> **上游报告**：[`_review_v2.8/00-full-doc-audit-v2.8.md`](../_review_v2.8/00-full-doc-audit-v2.8.md)
> **修复原则**：系统性修复（非打补丁）——先在文档中重新设计 → 验证整体一致性 → 实施技术修复 → 生成报告

---

## 目录

- [1. 修复总览](#1-修复总览)
- [2. P0-014: syscall 编号跨架构不一致 + 文档/代码多方矛盾](#2-p0-014-syscall-编号跨架构不一致--文档代码多方矛盾)
- [3. P0-016: 4 份 v0.2.8 文档需升级到 v1.0.1](#3-p0-016-4-份-v028-文档需升级到-v101)
- [4. P0-017: codegen 管道实现缺失](#4-p0-017-codegen-管道实现缺失)
- [5. P0-018: ABI 检查工具缺失](#5-p0-018-abi-检查工具缺失)
- [6. 下游文档残留修复](#6-下游文档残留修复)
- [7. 整体一致性验证](#7-整体一致性验证)
- [8. 残留风险与后续工作](#8-残留风险与后续工作)
- [附录 A: 完整修改文件清单](#附录-a-完整修改文件清单)

---

## 1. 修复总览

### 1.1 P0 问题清单

| 编号 | 问题 | 严重性 | 状态 |
|------|------|--------|------|
| P0-014 | syscall 编号跨架构不一致 + 文档/代码三方矛盾（4-syscall / 31-syscall / 120-syscall 三套模型并存） | P0 | ✅ 已修复 |
| P0-016 | 4 份 v0.2.8 文档需升级到 v1.0.1（违反 IRON-8） | P0 | ✅ 已修复 |
| P0-017 | codegen 管道实现缺失（06-codegen-pipeline.md 声明但无代码） | P0 | ✅ 已修复 |
| P0-018 | ABI 检查工具缺失（无自动化编号一致性校验） | P0 | ✅ 已修复 |

### 1.2 修复统计

- **修改文档文件**：18 份
- **新增工具文件**：6 份
- **修改代码文件**：2 份（上一轮完成）
- **ABI 检查结果**：6/6 PASS
- **下游文档残留修复**：本轮新发现并修复 10 份文档的旧 syscall 命名残留

---

## 2. P0-014: syscall 编号跨架构不一致 + 文档/代码多方矛盾

### 2.1 问题根因

v2.8 审查发现 docs/AirymaxOS 目录下存在 **三套完全矛盾的 syscall 模型**：

| 模型 | 来源 | 编号方案 | syscall 数量 |
|------|------|---------|-------------|
| 4-syscall + op-dispatch | `01-syscalls.md` (v1.0.1) + 代码 `unistd.h` / `syscall_64.tbl` | 548-551（4 核心 + 20 预留） | 4 |
| 31-syscall 独立模型 | `07-syscall-registry.md` (0.1.1) | 512-631（6 类 × 20 编号段） | 31（声明）/ 54（实际列出） |
| 120-syscall 完全不同命名 | `09-fuzz-testing.md` (0.1.1) | 512-631 | 120 |

**根因**：0.1.1 的 31-syscall 模型在 v1.0.1 Capability Folding 架构重构后已废弃，但下游文档未同步更新，导致三套模型并存。

### 2.2 修复方案：v1.0.1 统一模型

采用 **4 核心 syscall + op-dispatch + io_uring 数据面** 统一模型：

```
┌─────────────────────────────────────────────────────────────┐
│  控制面：4 核心 syscall（548-551）                          │
│  ├─ 548 airy_sys_call        (op-dispatch: COMPILE_BADGE /  │
│  │                            REVOKE_BADGE / LSM_CTL / ...) │
│  ├─ 549 airy_sys_rovol_ctl   (op-dispatch: SNAPSHOT /       │
│  │                            RESTORE / MIGRATE / TIER_SET) │
│  ├─ 550 airy_sys_sched_ctl   (op-dispatch: SET_POLICY /     │
│  │                            YIELD / GET_LATENCY)          │
│  └─ 551 airy_sys_clt_notify  (op-dispatch: PHASE_NOTIFY /   │
│                               REGISTER_KTHREAD)             │
├─────────────────────────────────────────────────────────────┤
│  数据面：io_uring（零 syscall）                             │
│  └─ IORING_OP_URING_CMD + cmd_op=IPC_SEND/RECV/CAP_REQUEST │
│     fastpath C-S9 内联 Badge 校验                           │
├─────────────────────────────────────────────────────────────┤
│  预留：552-571（20 槽位）                                   │
└─────────────────────────────────────────────────────────────┘
```

**编号起点 548 的依据**：x86_64 `syscall_64.tbl` L384-388 明确标注 512-547 为 x32 历史遗留禁止区域，548+ 才可用。

### 2.3 修改文件清单

#### 2.3.1 代码修复（上一轮完成）

| 文件 | 修改内容 |
|------|---------|
| `agent-linux/kernel/include/uapi/asm-generic/unistd.h` L826-843 | 新增 548-551 四个 airy syscall 编号 |
| `agent-linux/kernel/arch/x86/entry/syscalls/syscall_64.tbl` L378-387 | 新增 548-551 四个 airy syscall 入口 |

#### 2.3.2 SSoT 文档重写（本轮完成）

| 文件 | 修改内容 |
|------|---------|
| `docs/AirymaxOS/140-application-development/07-syscall-registry.md` | **完全重写**（914 行）：0.1.1 的 31-syscall 模型 → v1.0.1 的 4-syscall + op-dispatch 模型。新增 §1.4 Capability Folding 约束、§4 op-dispatch 映射表、§8 5 层 ABI 稳定性、Appendix A 历史 31-syscall 迁移映射 |

#### 2.3.3 下游文档更新（本轮完成）

| 文件 | 修改内容 |
|------|---------|
| `docs/AirymaxOS/30-interfaces/06-codegen-pipeline.md` | 版本 0.2.8 → v1.0.1；syscall.xml 从 12 syscall 改为 4 syscall；linux_base 512 → 548 |
| `docs/AirymaxOS/80-testing/09-fuzz-testing.md` | §3.1 完全重写（120 syscall → 4 核心 + io_uring）；magic 0xA1B2C3D4 → 0x41524531 |
| `docs/AirymaxOS/150-cloudnative/05-memoryrovol-csi.md` | 14 处：airy_sys_rovol_snapshot(552) → airy_sys_rovol_ctl(549, op=SNAPSHOT) 等 |
| `docs/AirymaxOS/150-cloudnative/04-supernode-os.md` | 8 处：airy_sys_rovol_migrate/snapshot/restore → op-dispatch 形式；L564 task_migrate(515) → sched_ctl(550)；L566 cxl_tier_set(555) → rovol_ctl(549, op=TIER_SET) |
| `docs/AirymaxOS/30-interfaces/04-coding-standard.md` | 7 处：airy_sys_task_submit → airy_sys_call(COMPILE_BADGE) |
| `docs/AirymaxOS/30-interfaces/05-syscall-semantic-mapping.md` | ~22 处：映射表全部更新为 v1.0.1 编号 + op-dispatch；L132-133 残留 #513/#514 → #550 sched_ctl；L240-241 残留 #555/#556 → #549 rovol_ctl |
| `docs/AirymaxOS/30-interfaces/README.md` | 2 处：airy_sys_task_submit → airy_sys_call(COMPILE_BADGE) |
| `docs/AirymaxOS/50-engineering-standards/20-contracts/contracts.md` | ~30 处：§1 分类表 6 类 120 调用 → 4 核心 + 20 预留 + IPC 数据面；L710-711 残留 cxl_tier_set/mglru_config → rovol_ctl |
| `docs/AirymaxOS/140-application-development/05-memory-rovol-api.md` | **系统性重写**（1649 → 1807 行）：100 处 0.1.1 独立 syscall（552-561）→ v1.0.1 `airy_sys_rovol_ctl` (549) + op-dispatch；覆盖 §2 编号表、§4-§9 全部 10 个 API 章节、§11 映射表、§12 四语言 SDK、§13 性能表、§14-§15 示例与测试 |

#### 2.3.4 下游文档残留修复（本轮验证阶段新发现）

验证阶段 Grep 扫描发现 10 份文档存在旧 syscall 命名残留（上一轮子代理未覆盖），本轮全部修复：

| 文件 | 修改内容 |
|------|---------|
| `docs/AirymaxOS/110-security/03-capability-model.md` | L6 日期 → 2026-07-22；L1566 对比表 "9 个（592-600）" → "9 个独立 syscall（0.1.1 模型 592-600）"；§13.1 代码示例 airy_sys_task_register → airy_sys_call(COMPILE_BADGE)；§13.2 代码示例 airy_sys_capability_request/mintcopy/ipc_send/revoke → v1.0.1 Badge 模型 |
| `docs/AirymaxOS/30-interfaces/02-ipc-protocol.md` | L6 日期 → 2026-07-22；L706-708 映射表 airy_sys_ipc_send/recv/register_ring → io_uring cmd_op（v1.0.1 无独立 syscall） |
| `docs/AirymaxOS/50-engineering-standards/10-coding-style/coding_conventions.md` | L2621 命名示例 airy_sys_task_submit → airy_sys_call |
| `docs/AirymaxOS/50-engineering-standards/90-terminology.md` | L1226 术语示例 airy_sys_task_submit → airy_sys_call |
| `docs/AirymaxOS/10-architecture/02-five-dimensional-principles.md` | L356 命名示例 airy_sys_task_submit → airy_sys_call |
| `docs/AirymaxOS/10-architecture/06-iron9-shared-model.md` | L142-149 [SS] 映射表 0.1.1 编号 #512-#545 → v1.0.1 #548-#550 + op-dispatch |
| `docs/AirymaxOS/00-requirements/03-non-functional-requirements.md` | L749 日志示例 airy_sys_task_submit → airy_sys_call |
| `docs/AirymaxOS/140-application-development/06-agent-deployment.md` | L567-571 seccomp 过滤器列表 8 个旧 syscall → 4 核心 syscall；L587 代码示例 airy_sys_capability_request → airy_sys_call(COMPILE_BADGE) |

### 2.4 op-dispatch 映射表

0.1.1 的 31 个独立 syscall 通过 4 核心 syscall 的 op 码分派承载（完整映射见 `07-syscall-registry.md` §4 与 Appendix A）：

| 0.1.1 独立 syscall | 0.1.1 编号 | v1.0.1 syscall + op-dispatch | v1.0.1 编号 |
|---------------------|-----------|------------------------------|------------|
| airy_sys_task_submit | 512 | airy_sys_call(COMPILE_BADGE) + io_uring | 548 + 数据面 |
| airy_sys_task_register | 516 | airy_sys_call(COMPILE_BADGE) | 548 |
| airy_sys_capability_request | 592 | airy_sys_call(COMPILE_BADGE) | 548 |
| airy_sys_capability_revoke | 593 | airy_sys_call(REVOKE_BADGE) | 548 |
| airy_sys_rovol_snapshot | 552 | airy_sys_rovol_ctl(SNAPSHOT) | 549 |
| airy_sys_rovol_restore | 553 | airy_sys_rovol_ctl(RESTORE) | 549 |
| airy_sys_rovol_migrate | 554 | airy_sys_rovol_ctl(MIGRATE) | 549 |
| airy_sys_cxl_tier_set | 555 | airy_sys_rovol_ctl(TIER_SET) | 549 |
| airy_sys_sched_set_policy | 572 | airy_sys_sched_ctl(SET_POLICY) | 550 |
| airy_sys_clt_phase_notify | 612 | airy_sys_clt_notify(PHASE_NOTIFY) | 551 |
| ... | ... | ... | ... |

---

## 3. P0-016: 4 份 v0.2.8 文档需升级到 v1.0.1

### 3.1 问题根因

4 份文档的版本号标记为 `0.2.8`，违反 IRON-8 铁律（禁止 0.2.x 中间过渡版本，0.1.1 后直接过渡到 1.0.1）。

### 3.2 修改文件清单

| 文件 | 修改内容 |
|------|---------|
| `docs/AirymaxOS/30-interfaces/06-codegen-pipeline.md` | 版本 0.2.8 → v1.0.1；所有 generator version 0.2.8 → 1.0.1 |
| `docs/AirymaxOS/10-architecture/08-threat-model.md` | L6 版本 0.2.8 → v1.0.1；L7 日期 → 2026-07-22；L490 页脚 v0.2.8 → v1.0.1 |
| `docs/AirymaxOS/70-build-system/03-ci-cd-pipeline.md` | L5 版本 0.2.8 → v1.0.1；L6 日期 → 2026-07-22；L822-823 tag 示例 v0.2.8 → v1.0.1；L1106 页脚 0.2.8 → v1.0.1 |
| `docs/AirymaxOS/190-distribution/06-sbom-generation.md` | L5 版本 0.2.8 → v1.0.1；L6 日期 → 2026-07-22；L1508 页脚 v1.0.1（验证阶段发现 L5 残留 0.2.8，已补修） |

### 3.3 验证

Grep 确认 `docs/AirymaxOS` 目录下无 `文档版本**：0.2.8` 残留。

---

## 4. P0-017: codegen 管道实现缺失

### 4.1 问题根因

`06-codegen-pipeline.md` 声明了 codegen 管道（从 `syscall.xml` 契约源生成 C UAPI 头文件），但无实际代码实现。

### 4.2 新增文件清单

| 文件 | 行数 | 功能 |
|------|------|------|
| `agent-linux/kernel/include/uapi/linux/airymax/syscall.xml` | 89 | codegen 契约源：4 个 `<syscall>` 元素 + `<reserved>` 段，`linux_base="548"` |
| `agent-linux/tools/codegen/syscall_gen.py` | 314 | codegen 生成器：解析 syscall.xml → 生成 `#define AIRY_SYS_*` 宏 + `__NR_airy_sys_*` 宏 + 函数原型；`--check` 模式用 difflib 对比已提交文件 |
| `agent-linux/tools/codegen/Makefile` | 45 | 构建入口：`all` / `syscall` / `check` / `clean` 四个 target |

### 4.3 syscall.xml 契约源结构

```xml
<syscalls version="0x0100" core_count="4" reserved_count="20"
          total_slots="24" linux_base="548">
  <syscall name="airy_sys_call"        number="0" .../>
  <syscall name="airy_sys_rovol_ctl"   number="1" .../>
  <syscall name="airy_sys_sched_ctl"   number="2" .../>
  <syscall name="airy_sys_clt_notify"  number="3" .../>
  <reserved from="4" to="23"/>
</syscalls>
```

---

## 5. P0-018: ABI 检查工具缺失

### 5.1 问题根因

无自动化工具校验 syscall 编号在 SSoT 文档 / `unistd.h` / `syscall_64.tbl` 三方之间的一致性，导致 P0-014 类问题无法被 CI 自动发现。

### 5.2 新增文件清单

| 文件 | 行数 | 功能 |
|------|------|------|
| `agent-linux/tools/abi-check/abi_check.py` | ~200 | ABI 稳定性检查工具：从三方源提取 syscall 编号 → 6 项检查 |
| `agent-linux/tools/abi-check/abi_baseline.json` | ~30 | v1.0.1 ABI 基线快照：4 syscalls, base=548, nr=552 |
| `agent-linux/tools/abi-check/README.md` | ~40 | 工具使用说明 |

### 5.3 ABI 检查项（6 项）

| # | 检查项 | 验证结果 |
|---|--------|---------|
| 1 | 三方一致性（SSoT / unistd.h / syscall_64.tbl） | ✅ PASS |
| 2 | 编号起点为 548 | ✅ PASS |
| 3 | 编号范围 548-571 内无冲突 | ✅ PASS |
| 4 | `__NR_syscalls` 值正确（=552） | ✅ PASS |
| 5 | 无 512-547 区域的 syscall（x32 禁止区域） | ✅ PASS |
| 6 | 编号与基线快照一致 | ✅ PASS |

### 5.4 运行结果

```
Checks: 6/6 passed, 0 failed
RESULT: PASS — all ABI checks passed (OS-IRON-001)
```

---

## 6. 下游文档残留修复

### 6.1 验证阶段新发现

在 h8（整体一致性验证）阶段，通过 Grep 扫描发现上一轮子代理未覆盖的 10 份文档存在旧 syscall 命名残留：

| 文件 | 残留类型 | 修复处数 |
|------|---------|---------|
| 03-capability-model.md | 代码示例使用 airy_sys_task_register / capability_request / mintcopy / ipc_send / revoke | 5 |
| 02-ipc-protocol.md | 映射表使用 airy_sys_ipc_send / recv / register_ring | 3 |
| coding_conventions.md | 命名示例使用 airy_sys_task_submit | 1 |
| 90-terminology.md | 术语示例使用 airy_sys_task_submit | 1 |
| 02-five-dimensional-principles.md | 命名示例使用 airy_sys_task_submit | 1 |
| 06-iron9-shared-model.md | [SS] 映射表使用 0.1.1 编号 #512-#545 | 6 |
| 03-non-functional-requirements.md | 日志示例使用 airy_sys_task_submit | 1 |
| 06-agent-deployment.md | seccomp 列表 8 个旧 syscall + 代码示例 | 2 |
| 05-memory-rovol-api.md | 100 处 0.1.1 独立 syscall（552-561） | 100 |
| 05-syscall-semantic-mapping.md | L132-133 残留 #513/#514；L240-241 残留 #555/#556 | 4 |

### 6.2 合理保留的旧命名引用

以下旧 syscall 命名引用为合理的迁移映射表 / agentrt 用户态 API 名，已验证保留：

| 文件 | 保留原因 |
|------|---------|
| 07-syscall-registry.md Appendix A | SSoT 历史 31-syscall 迁移映射表，明确标注"0.1.1 编号" |
| 03-capability-model.md §12.5.4 / L897-914 | v1.0 vs v1.0.1 对比表 + 迁移映射表 |
| 05-syscall-semantic-mapping.md L131/L134-135 | agentrt 用户态 API 名（非内核 syscall） |
| 06-iron9-shared-model.md L148-149 | agentrt 用户态 API 名（映射表左列） |
| 02-ipc-protocol.md L483/L711 | v1.0.1 变更说明（明确标注"已废弃"） |

---

## 7. 整体一致性验证

### 7.1 ABI 三方一致性

运行 `python3 tools/abi-check/abi_check.py`：

```
Sources:
  SSoT            : 07-syscall-registry.md
  unistd.h        : kernel/include/uapi/asm-generic/unistd.h
  syscall_64.tbl  : kernel/arch/x86/entry/syscalls/syscall_64.tbl
  baseline        : tools/abi-check/abi_baseline.json

Syscalls found:
  SSoT: 4, unistd.h: 4, syscall_64.tbl: 4

Checks: 6/6 passed, 0 failed
RESULT: PASS — all ABI checks passed (OS-IRON-001)
```

### 7.2 文档版本号一致性

Grep 确认 `docs/AirymaxOS` 目录下：
- ✅ 无 `文档版本**：0.2.8` 残留（P0-016 修复完成）
- ℹ️ 80 份文档版本号为 `0.1.1`（奠基版本，合理保留，非 P0-016 范围）

### 7.3 旧 syscall 命名残留扫描

Grep 扫描 `airy_sys_(task_submit|ipc_send|ipc_recv|agent_create|...|rovol_snapshot|...|cxl_tier_set|...)`：

- ✅ 所有作为"当前 syscall"使用的旧命名已清除
- ✅ 保留的旧命名均为迁移映射表 / agentrt 用户态 API 名 / 变更说明（已逐项验证）

### 7.4 旧编号残留扫描

Grep 扫描 `airy_sys_cxl_tier_set|cxl_tier_get|mglru_config`：

- ✅ 3 个文件的残留均为迁移映射表合理引用（05-memory-rovol-api.md §2.1、07-syscall-registry.md §4.3、05-syscall-semantic-mapping.md 已修复）

---

## 8. 残留风险与后续工作

### 8.1 已知残留风险

| # | 风险 | 影响 | 缓解措施 |
|---|------|------|---------|
| R1 | 80 份文档版本号仍为 `0.1.1` | 低（0.1.1 是奠基版本号，合理保留） | 如 IRON-8 要求所有文档版本号统一为 v1.0.1，需用户确认后批量升级 |
| R2 | codegen 管道未集成到 CI | 中（`syscall_gen.py --check` 未在 CI 中运行） | 后续在 `ci-kernel.yml` 中新增 codegen check job |
| R3 | ABI 检查工具未集成到 CI | 中（`abi_check.py` 未在 CI 中运行） | 后续在 `mgmt-orchestrator.yml` 中新增 ABI check job |
| R4 | `syscall.xml` 与 `unistd.h` 的自动生成关系未建立 | 中（目前手动同步） | 后续在 Makefile 中新增 `make syscall` → 自动生成 + `--check` 验证 |

### 8.2 后续工作建议

1. **CI 集成**：将 `abi_check.py` 和 `syscall_gen.py --check` 集成到 GitHub Actions，作为 PR 合并门禁
2. **codegen 扩展**：当前 `syscall.xml` 仅覆盖 4 核心 syscall，后续可扩展到 ioctl 编号、错误码、capability 位的 codegen
3. **80 份 0.1.1 文档版本号**：如用户要求统一为 v1.0.1，可批量 sed 替换（但需确认是否影响版本历史语义）

---

## 附录 A: 完整修改文件清单

### A.1 代码文件（2 份，上一轮完成）

| # | 文件路径 | 修改类型 |
|---|---------|---------|
| 1 | `agent-linux/kernel/include/uapi/asm-generic/unistd.h` | 修改（L826-843） |
| 2 | `agent-linux/kernel/arch/x86/entry/syscalls/syscall_64.tbl` | 修改（L378-387） |

### A.2 新增工具文件（6 份，本轮完成）

| # | 文件路径 | 行数 |
|---|---------|------|
| 1 | `agent-linux/kernel/include/uapi/linux/airymax/syscall.xml` | 89 |
| 2 | `agent-linux/tools/codegen/syscall_gen.py` | 314 |
| 3 | `agent-linux/tools/codegen/Makefile` | 45 |
| 4 | `agent-linux/tools/abi-check/abi_check.py` | ~200 |
| 5 | `agent-linux/tools/abi-check/abi_baseline.json` | ~30 |
| 6 | `agent-linux/tools/abi-check/README.md` | ~40 |

### A.3 修改文档文件（18 份，本轮完成）

| # | 文件路径 | 修改类型 | P0 归属 |
|---|---------|---------|---------|
| 1 | `docs/AirymaxOS/140-application-development/07-syscall-registry.md` | 完全重写（914 行） | P0-014 |
| 2 | `docs/AirymaxOS/30-interfaces/06-codegen-pipeline.md` | 修改 | P0-014 + P0-016 |
| 3 | `docs/AirymaxOS/80-testing/09-fuzz-testing.md` | 修改（§3 重写） | P0-014 |
| 4 | `docs/AirymaxOS/150-cloudnative/05-memoryrovol-csi.md` | 修改（14 处） | P0-014 |
| 5 | `docs/AirymaxOS/150-cloudnative/04-supernode-os.md` | 修改（8+2 处） | P0-014 |
| 6 | `docs/AirymaxOS/30-interfaces/04-coding-standard.md` | 修改（7 处） | P0-014 |
| 7 | `docs/AirymaxOS/30-interfaces/05-syscall-semantic-mapping.md` | 修改（~22 处） | P0-014 |
| 8 | `docs/AirymaxOS/30-interfaces/README.md` | 修改（2 处） | P0-014 |
| 9 | `docs/AirymaxOS/50-engineering-standards/20-contracts/contracts.md` | 修改（~30+2 处） | P0-014 |
| 10 | `docs/AirymaxOS/140-application-development/05-memory-rovol-api.md` | 系统性重写（1649→1807 行） | P0-014 |
| 11 | `docs/AirymaxOS/110-security/03-capability-model.md` | 修改（5 处） | P0-014 残留 |
| 12 | `docs/AirymaxOS/30-interfaces/02-ipc-protocol.md` | 修改（3 处） | P0-014 残留 |
| 13 | `docs/AirymaxOS/50-engineering-standards/10-coding-style/coding_conventions.md` | 修改（1 处） | P0-014 残留 |
| 14 | `docs/AirymaxOS/50-engineering-standards/90-terminology.md` | 修改（1 处） | P0-014 残留 |
| 15 | `docs/AirymaxOS/10-architecture/02-five-dimensional-principles.md` | 修改（1 处） | P0-014 残留 |
| 16 | `docs/AirymaxOS/10-architecture/06-iron9-shared-model.md` | 修改（6 处） | P0-014 残留 |
| 17 | `docs/AirymaxOS/00-requirements/03-non-functional-requirements.md` | 修改（1 处） | P0-014 残留 |
| 18 | `docs/AirymaxOS/140-application-development/06-agent-deployment.md` | 修改（2 处） | P0-014 残留 |

### A.4 P0-016 版本升级文件（4 份，本轮完成）

| # | 文件路径 | 修改类型 |
|---|---------|---------|
| 1 | `docs/AirymaxOS/10-architecture/08-threat-model.md` | 版本升级（3 处） |
| 2 | `docs/AirymaxOS/70-build-system/03-ci-cd-pipeline.md` | 版本升级（4 处） |
| 3 | `docs/AirymaxOS/190-distribution/06-sbom-generation.md` | 版本升级（3 处，含验证阶段补修 L5） |
| 4 | `docs/AirymaxOS/30-interfaces/06-codegen-pipeline.md` | 版本升级（已计入 A.3 #2） |

---

## 报告结束

> **报告版本** | agent-linux P0 问题系统性修复报告 v2.9 | 生成日期：2026-07-22
