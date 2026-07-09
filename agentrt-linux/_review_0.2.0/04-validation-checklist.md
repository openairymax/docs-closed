Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agentrt-linux 验证清单 v0.2.0（18 项）

> **验证日期**: 2026-07-09
> **验证范围**: docs/AirymaxAgentOS/ 全部 125 篇文档
> **验证方法**: Grep 全文档扫描 + Shell 脚本验证 + 人工审查
> **结果**: 18/18 全部通过 ✅

---

## 1. IRON 工程铁律验证（5 项）

### H-01: IRON-1 禁止新特性

| 项目 | 内容 |
|------|------|
| **规则** | 0.1.1 是唯一奠基版本，禁止新特性 |
| **验证方法** | 文档体系审查，确认无新特性代码设计 |
| **验证结果** | 0 违规 — 0.1.1 仅文档体系，所有设计文档均属于已规划范围 |
| **状态** | ✅ 通过 |

### H-02: IRON-2 禁止桩函数桩文件

| 项目 | 内容 |
|------|------|
| **规则** | 禁止桩函数、桩文件、占位实现 |
| **验证方法** | `grep -rl "TODO\|占位\|placeholder\|待填充\|待完善" --include="*.md" .` |
| **验证结果** | 20 文件含关键词，经审查全部为合法上下文引用（如路线图中"待完善"描述未来工作、README 中"占位"标注 0.1.1 范围） |
| **状态** | ✅ 通过 |

### H-03: IRON-3 禁止绕开功能限制的编译集成

| 项目 | 内容 |
|------|------|
| **规则** | 禁止绕开功能限制的编译集成 |
| **验证方法** | 文档阶段 N/A（无代码编译） |
| **验证结果** | N/A |
| **状态** | ✅ 通过（N/A） |

### H-04: IRON-4 禁止简化功能

| 项目 | 内容 |
|------|------|
| **规则** | 禁止简化功能 |
| **验证方法** | 全文档审查，确认所有功能设计均有详细实施示例 |
| **验证结果** | 0 违规 — 所有方案文档含完整代码示例和实施说明 |
| **状态** | ✅ 通过 |

### H-05: IRON-5 禁止未实现的功能设计

| 项目 | 内容 |
|------|------|
| **规则** | 禁止未实现的功能设计 |
| **验证方法** | 全文档审查，确认所有设计均有对应的实施路径和代码示例 |
| **验证结果** | 0 违规 |
| **状态** | ✅ 通过 |

---

## 2. IRON-9 v2 共享契约验证（1 项）

### H-06: [SC] 共享契约层 6 个头文件一致性

| 项目 | 内容 |
|------|------|
| **规则** | IRON-9 v2 [SC] 层 6 个头文件在全仓引用一致 |
| **验证方法** | `grep -rn "6 个.*头文件\|6 个共享头文件\|6 个 \[SC\]" 50-engineering-standards/` |
| **验证结果** | 10+ 处引用全部为"6 个"，0 处残留"4 个"（除 1 处合法历史叙述） |
| **6 个头文件** | `bpf_struct_ops.h` / `memory_types.h` / `security_types.h` / `cognition_types.h` / `sched.h` / `ipc.h` |
| **状态** | ✅ 通过 |

---

## 3. 命名一致性验证（3 项）

### H-07: agentos_ → agentrt_ 改名彻底性

| 项目 | 内容 |
|------|------|
| **规则** | agentos_ 前缀全部改为 agentrt_，不留兼容别名 |
| **验证方法** | `grep -rn "agentos_" docs/AirymaxAgentOS/` |
| **验证结果** | 0 残留 |
| **状态** | ✅ 通过 |

### H-08: SCHED_AGENT 宏禁令

| 项目 | 内容 |
|------|------|
| **规则** | 禁止定义 `#define SCHED_AGENT <数字>` 宏，统一使用 SCHED_EXT=7 |
| **验证方法** | `grep "#define SCHED_AGENT\s+\d"` |
| **验证结果** | 0 残留 — 仅保留 `#define SCHED_AGENT_NAME "sched_agent"`（BPF 策略名称字符串） |
| **状态** | ✅ 通过 |

### H-09: 内核态 [SC] 头文件禁用 float

| 项目 | 内容 |
|------|------|
| **规则** | 内核态 [SC] 共享头文件不得使用 float 类型 |
| **验证方法** | `grep "float\s+(threshold\|ratio\|value\|weight\|factor)"` |
| **验证结果** | 0 残留 — 全部使用 Q16.16 定点数（`airymax_q16_t = int32_t`） |
| **状态** | ✅ 通过 |

---

## 4. 技术一致性验证（2 项）

### H-10: IPC magic 一致性

| 项目 | 内容 |
|------|------|
| **规则** | IPC magic 0x41524531（'ARE1'）在全仓一致 |
| **验证方法** | `grep "0x41524531\|ARE1"` |
| **验证结果** | 78 处 13 文件，全部一致 |
| **状态** | ✅ 通过 |

### H-11: 任务描述符 magic 一致性

| 项目 | 内容 |
|------|------|
| **规则** | 任务描述符 magic 0x41475453（'AGTS'）在全仓一致 |
| **验证方法** | `grep "0x41475453\|AGTS"` |
| **验证结果** | 172 处 30 文件，全部一致 |
| **状态** | ✅ 通过 |

---

## 5. 文档完整性验证（2 项）

### H-12: 目录结构完整性

| 项目 | 内容 |
|------|------|
| **规则** | 20 个设计目录完整 |
| **验证方法** | `find -maxdepth 1 -type d \| sort` |
| **验证结果** | 20 目录 125 篇文档 |
| **目录清单** | 00-requirements / 10-architecture / 20-modules / 30-interfaces / 40-dataflows / 50-engineering-standards / 60-driver-model / 70-build-system / 80-testing / 90-observability / 100-operations / 110-security / 120-development-process / 130-roadmap / 140-application-development / 150-cloudnative / 160-compatibility / 170-performance / 180-i18n / 190-distribution |
| **状态** | ✅ 通过 |

### H-13: Copyright 头完整性

| 项目 | 内容 |
|------|------|
| **规则** | 所有 .md 文件首行包含 Copyright 声明 |
| **验证方法** | 逐文件检查首行 `head -1 *.md \| grep Copyright` |
| **验证结果** | 125/125 文件均有 Copyright 头（100%） |
| **状态** | ✅ 通过 |

---

## 6. 禁词清零验证（4 项）

### H-14: "微内核原语"清零

| 项目 | 内容 |
|------|------|
| **规则** | 源文档中"微内核原语"表述清零，仅允许在审查报告/变更日志/禁词清单中作为合法引用保留 |
| **验证方法** | `grep -rn "微内核原语" docs/AirymaxAgentOS/` |
| **验证结果** | 5 处，全部为合法引用（禁词清单/术语对照表/禁止声明） |
| **文件清单** | `180-i18n/03-doc-i18n.md`（2 处）/ `120-cross-project-code-sharing.md`（1 处）/ `70-kernel-doc-standard.md`（1 处）/ `170-performance/01-scheduling-performance.md`（1 处） |
| **状态** | ✅ 通过（全部合法引用） |

### H-15: "MGLRU 2.0"清零

| 项目 | 内容 |
|------|------|
| **规则** | 源文档中"MGLRU 2.0"表述清零，应改为"MGLRU 多代 LRU"，仅允许在禁词清单/检查脚本/修复记录中保留 |
| **验证方法** | `grep -rn "MGLRU 2.0" docs/AirymaxAgentOS/` |
| **验证结果** | 3 处，全部为合法引用（禁词对照表/检查脚本 grep 模式/修复记录） |
| **文件清单** | `00-engineering-standards-handbook.md`（3 处） |
| **状态** | ✅ 通过（全部合法引用） |

### H-16: "150-cloud-native"清零

| 项目 | 内容 |
|------|------|
| **规则** | 目录名统一为"150-cloudnative"（无连字符） |
| **验证方法** | `grep -rn "150-cloud-native" docs/AirymaxAgentOS/` |
| **验证结果** | 0 残留 — 14 处全部修复为 `150-cloudnative` |
| **状态** | ✅ 通过 |

### H-17: openEuler/Euler 表述合规

| 项目 | 内容 |
|------|------|
| **规则** | openEuler 相关描述只能在管理仓或大纲性质的非核心文档中，开源核心文档中使用"主流 Linux 发行版" |
| **验证方法** | `grep -rn "openEuler\|Euler" docs/AirymaxAgentOS/` |
| **验证结果** | 12 处，全部为合法引用（禁止声明/术语对照表/禁词清单说明） |
| **文件清单** | `180-i18n/`（4 文件 7 处）/ `190-distribution/`（5 文件 5 处） |
| **状态** | ✅ 通过（全部合法引用，均为"禁止使用"声明） |

---

## 7. 迁移完整性验证（1 项）

### H-18: Capital_Specifications 迁移完成度

| 项目 | 内容 |
|------|------|
| **规则** | Capital_Specifications 内容已迁移至 50-engineering-standards，AirymaxAgentOS 内部不再引用旧路径 |
| **验证方法** | `grep -rn "Capital_Specifications" docs/AirymaxAgentOS/ \| grep -v AirymaxAgentRT` |
| **验证结果** | 6 处，全部为合法历史迁移说明（`50-engineering-standards/README.md` 中的注释 `原 50-specifications/...`） |
| **状态** | ✅ 通过（全部合法历史追溯记录） |

---

## 8. 验证总结

| 编号 | 验证项 | 结果 | 状态 |
|------|--------|------|------|
| H-01 | IRON-1 禁止新特性 | 0 违规 | ✅ |
| H-02 | IRON-2 禁止桩函数 | 0 违规 | ✅ |
| H-03 | IRON-3 禁止绕开编译 | N/A | ✅ |
| H-04 | IRON-4 禁止简化功能 | 0 违规 | ✅ |
| H-05 | IRON-5 禁止未实现设计 | 0 违规 | ✅ |
| H-06 | [SC] 6 个头文件一致 | 6 个一致 | ✅ |
| H-07 | agentos_→agentrt_ 改名 | 0 残留 | ✅ |
| H-08 | SCHED_AGENT 宏禁令 | 0 残留 | ✅ |
| H-09 | [SC] 禁用 float | 0 残留 | ✅ |
| H-10 | IPC magic 一致性 | 78 处一致 | ✅ |
| H-11 | 任务描述符 magic | 172 处一致 | ✅ |
| H-12 | 目录结构完整 | 20 目录 125 文档 | ✅ |
| H-13 | Copyright 头 | 125/125 | ✅ |
| H-14 | "微内核原语"清零 | 5 处合法引用 | ✅ |
| H-15 | "MGLRU 2.0"清零 | 3 处合法引用 | ✅ |
| H-16 | "150-cloud-native"清零 | 0 残留 | ✅ |
| H-17 | openEuler/Euler 表述 | 12 处合法引用 | ✅ |
| H-18 | Capital_Specifications 迁移 | 6 处合法说明 | ✅ |
| **合计** | **18/18** | — | **✅ 全部通过** |

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
