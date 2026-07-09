Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agentrt-linux 修复变更日志 v0.2.0

> **日志日期**: 2026-07-09
> **版本**: v0.2.0
> **范围**: v0.1.1 → v0.2.0 全部修复记录

---

## 1. 变更概览

| 类别 | 修复项 | 文件数 | 修改处数 |
|------|--------|--------|---------|
| P0 | SCHED_AGENT 宏违规修复 | 1 | 2 |
| P0 | [SC] 头文件 4→6 统一 | 12 | 20+ |
| P1 | 150-cloud-native → 150-cloudnative | 7 | 14 |
| P1 | Capital_Specifications 交叉引用更新 | 5 | 5 |
| P1 | Copyright 头补全 | 2 | 2 |
| 新增 | 阶段 B-D 文档充实 | 27 | ~18,020 行 |
| 新增 | 阶段 E 工程标准 | 8 | ~4,684 行 |
| 新增 | 阶段 F 开放标准 | 7 | ~3,718 行 |
| **合计** | — | **69** | **~26,445+** |

---

## 2. P0 阻断性问题修复

### 2.1 SCHED_AGENT 调度类编号违规（P0-13）

**ID**: P0-13
**严重级别**: P0（阻断）
**发现日期**: 2026-07-09（二次问题检查）
**修复日期**: 2026-07-09

**问题描述**：
`160-compatibility/02-posix-compat.md` 第 252 行定义了 `#define SCHED_AGENT 7`，与 OLK-6.6 已有的 `SCHED_EXT=7`（`include/uapi/linux/sched.h:121`）编号冲突。违反 IRON-9 v2 和 project_memory 中的硬约束："SCHED_AGENT=7 与 OLK-6.6 已有的 SCHED_EXT=7 编号冲突，必须删除 SCHED_AGENT 宏，统一使用 SCHED_EXT；SCHED_AGENT 仅作为 sched_ext 策略名称"。

**修复前**：
```c
/* 新增 SCHED_AGENT 调度类（不与 POSIX 冲突） */
#define SCHED_AGENT    7   /* agentrt-linux 专属（Linux 6.6 SCHED_EXT=7） */
```

**修复后**：
```c
/*
 * 复用内核 SCHED_EXT=7 调度类编号，禁止定义 SCHED_AGENT 宏。
 * SCHED_AGENT 仅作为 sched_ext BPF 策略名称（字符串），非调度类编号。
 * 参见 include/uapi/linux/sched.h:121（OLK-6.6 已定义 SCHED_EXT=7）。
 */
#define SCHED_AGENT_NAME  "sched_agent"  /* BPF 策略名称，非调度类编号 */
```

**兼容性表格修复**：
- `sched_setscheduler(pid, SCHED_AGENT, &param)` → `sched_setscheduler(pid, SCHED_EXT, &param)`
- `非 Agent 进程设置 SCHED_AGENT` → `非 Agent 进程设置 SCHED_EXT 策略`

**影响文件**: `160-compatibility/02-posix-compat.md`
**验证**: `grep "#define SCHED_AGENT\s+\d"` → 0 结果 ✅

---

### 2.2 [SC] 头文件数量 4→6 统一（P0-14）

**ID**: P0-14（升级自 P1）
**严重级别**: P0（阻断）
**发现日期**: 2026-07-09
**修复日期**: 2026-07-09

**问题描述**：
IRON-9 v2 [SC] 共享契约层头文件于 2026-07-07 确立基础 4 个（`bpf_struct_ops.h`/`memory_types.h`/`security_types.h`/`cognition_types.h`），2026-07-08 新增 `sched.h` 和 `ipc.h` 扩展至 6 个。但 12 个文件仍引用旧的"4 个头文件"数量，且部分文件使用了完全错误的头文件名（`airymax_ipc.h`/`airymax_errno.h`/`airymax_cap.h`/`airymax_mem.h`）。

**修复清单**：

| 文件 | 修复类型 | 详情 |
|------|---------|------|
| `20-modules/README.md` | 数量修复 | "4 个" → "6 个" |
| `40-dataflows/README.md` | 数量修复 | "4 个" → "6 个" |
| `TERMINOLOGY.md` | 数量+清单 | "4 个" → "6 个" + 添加 sched.h/ipc.h |
| `10-coding-style/README.md` | 数量+表格 | 2 处修复 + 表格从 4 行扩展为 6 行 |
| `C_coding_style_standard.md` | 层级+表格 | 错误码 [SC]→[SS] 修正 + 表格替换 |
| `Rust_coding_style_standard.md` | Mermaid 图 | 4 节点 → 6 节点 |
| `20-contracts/README.md` | 数量+表格 | 4 处修复 + 表格扩展 |
| `syscall_api_contract.md` | 数量+表格 | "4 个" → "6 个" + 表格扩展 |
| `agentrt_integration.md` | **整章重写** | 第 2.2 节 ~235 行重写 + 6 处修复 |
| `40-integration/README.md` | 头文件名 | 错误名 → 正确 6 个名 |
| `08-compliance-checklist.md` | 数量+脚本 | 4 处修复 + SC_HEADERS 脚本扩展 |
| `error_code_reference.md` | 概念调整 | 4 处修复 + [SC]→[SS] 层级 |

**关键修复 — agentrt_integration.md 第 2.2 节整章重写**：
- 原：4 个错误头文件名（`airymax_ipc.h`/`airymax_errno.h`/`airymax_cap.h`/`airymax_mem.h`）
- 新：6 个正确头文件名，每个含完整表格、代码示例、落地说明

**验证**: `grep "airymax_ipc\.h\|airymax_errno\.h\|airymax_cap\.h\|airymax_mem\.h"` → 0 结果 ✅

---

## 3. P1 开发障碍修复

### 3.1 150-cloud-native → 150-cloudnative（P1-08）

**ID**: P1-08
**严重级别**: P1
**发现日期**: 2026-07-09（二次问题检查）
**修复日期**: 2026-07-09

**问题描述**：
实际目录名为 `150-cloudnative`（无连字符），但 14 处文档引用为 `150-cloud-native`（有连字符），导致路径引用不一致。

**修复文件（7 个）**：

| 文件 | 处数 |
|------|------|
| `150-cloudnative/README.md` | 1 |
| `130-roadmap/01-development-strategy.md` | 1 |
| `130-roadmap/06-acceptance-criteria.md` | 6 |
| `130-roadmap/02-milestones-and-timeline.md` | 3 |
| `130-roadmap/03-resource-estimation.md` | 1 |
| `20-modules/README.md` | 1 |
| `README.md` | 1（含链接文本+路径） |

**验证**: `grep "150-cloud-native"` → 0 结果 ✅

---

### 3.2 Capital_Specifications 交叉引用更新（P1-09）

**ID**: P1-09
**严重级别**: P1
**发现日期**: 2026-07-09
**修复日期**: 2026-07-09

**问题描述**：
`Capital_Specifications` 内容已于 2026-07-08 迁移至 `50-engineering-standards/`，但 5 处 AirymaxAgentOS 文档仍引用旧路径 `docs/Capital_Specifications/coding_standard/`。

**修复文件（5 个）**：

| 文件 | 修复前 | 修复后 |
|------|--------|--------|
| `30-interfaces/04-coding-standard.md:14` | `docs/Capital_Specifications/coding_standard/` | `50-engineering-standards/10-coding-style/` |
| `30-interfaces/04-coding-standard.md:482` | `docs/Capital_Specifications/coding_standard/` | `50-engineering-standards/10-coding-style/` |
| `10-architecture/04-engineering-baseline.md:271` | `docs/Capital_Specifications/coding_standard/` | `50-engineering-standards/10-coding-style/` |
| `10-architecture/02-five-dimensional-principles.md:387` | `docs/Capital_Specifications/coding_standard/` | `50-engineering-standards/10-coding-style/` |
| `TERMINOLOGY.md:8` | `AirymaxAgentOS/Capital_Specifications/TERMINOLOGY.md` | `AirymaxAgentOS/TERMINOLOGY.md` |

**保留引用**：`50-engineering-standards/README.md` 中 6 处历史迁移说明（`原 Capital_Specifications/...`）为合法追溯记录。

---

### 3.3 Copyright 头补全（P1-10）

**ID**: P1-10
**严重级别**: P1
**发现日期**: 2026-07-09
**修复日期**: 2026-07-09

**问题描述**：2 个文件缺少 Copyright 头。

**修复文件**：
1. `00-requirements/README.md` — 首行添加 `Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.`
2. `10-architecture/04-engineering-baseline.md` — 同上

**验证**: 125/125 文件均有 Copyright 头 ✅

---

## 4. 新增文档清单

### 4.1 阶段 B：140-160 目录充实（9 文件 5,520 行）

| 文件 | 行数 |
|------|------|
| `140-application-development/01-agent-lifecycle.md` | 608 |
| `140-application-development/02-sdk-integration.md` | 692 |
| `140-application-development/03-agent-orchestration.md` | 621 |
| `150-cloudnative/01-k8s-crd-design.md` | 718 |
| `150-cloudnative/02-containerd-shim.md` | 704 |
| `150-cloudnative/03-cni-network-policy.md` | 625 |
| `160-compatibility/01-abi-stability.md` | 487 |
| `160-compatibility/02-posix-compat.md` | 417 |
| `160-compatibility/03-upstream-tracking.md` | 648 |

### 4.2 阶段 D：170-190 目录充实（18 文件 ~12,500 行）

| 文件 | 行数 |
|------|------|
| `170-performance/01-scheduling-performance.md` | 649 |
| `170-performance/02-memory-performance.md` | 701 |
| `170-performance/03-ipc-performance.md` | 789 |
| `180-i18n/01-locale-design.md` | 672 |
| `180-i18n/02-error-message-i18n.md` | 783 |
| `180-i18n/02-encoding-spec.md` | 740 |
| `180-i18n/03-doc-i18n.md` | 719 |
| `180-i18n/03-cjk-support.md` | 682 |
| `190-distribution/01-rpm-packaging.md` | 714 |
| `190-distribution/02-dnf-repo-design.md` | 608 |
| `190-distribution/02-installer-design.md` | 760 |
| `190-distribution/03-installer-design.md` | 843 |
| `190-distribution/03-update-mechanism.md` | 711 |

### 4.3 阶段 E：工程标准（8 文件 4,684 行）

| 文件 | 行数 |
|------|------|
| `C_coding_style_standard_supplement.md` | 645 |
| `60-checkpatch-rule-map.md` | 781 |
| `70-kernel-doc-standard.md` | 547 |
| `80-clang-format-enforcement.md` | 581 |
| `90-maintainers-subsystem-model.md` | 474 |
| `100-deprecated-api-registry.md` | 639 |
| `110-spdx-license-compliance.md` | 479 |
| `120-cross-project-code-sharing.md` | 538 |

### 4.4 阶段 F：开放标准（7 文件 3,718 行）

| 文件 | 行数 |
|------|------|
| `README.md` | 247 |
| `01-airymax-agent-runtime-standard.md` | 610 |
| `02-airymax-ipc-protocol-standard.md` | 533 |
| `03-airymax-security-model-standard.md` | 619 |
| `04-airymax-memory-rovol-standard.md` | 617 |
| `05-airymax-cognition-loop-standard.md` | 543 |
| `06-airymax-scheduling-standard.md` | 549 |

---

## 5. 变更统计

### 5.1 按文件类型

| 操作 | 文件数 | 处数 |
|------|--------|------|
| 修改（修复） | 27 | 43+ |
| 新增（文档） | 42 | ~26,445 行 |
| 迁移（目录重组） | 2 | — |
| **合计** | **69** | — |

### 5.2 按严重级别

| 级别 | 修复项 | 状态 |
|------|--------|------|
| P0 | 2 项（SCHED_AGENT + [SC] 统一） | ✅ 全部修复 |
| P1 | 3 项（150-cloudnative + Capital_Spec + Copyright） | ✅ 全部修复 |

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
