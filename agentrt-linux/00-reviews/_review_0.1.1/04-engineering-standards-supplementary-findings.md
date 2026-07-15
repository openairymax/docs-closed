Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agentrt-linux（AirymaxOS）工程标准补充发现报告

> **审查日期**: 2026-07-09
> **文档定位**: [03-technical-standards-and-specifications-review.md](./03-technical-standards-and-specifications-review.md) 的补充发现。主报告已识别 39 项问题（13 P0 + 14 P1 + 8 P2 + 4 P3），本文档记录经源码级**二次验证**后确认的补充发现，以及对工程标准 Agent 部分初步报告的**误报澄清**。
> **审查范围**: OpenAirymax/docs/AirymaxAgentOS/50-engineering-standards/（8 文件 ~4,684 行）+ 70-build-system/ + 80-testing/ + 90-observability/ + 110-security/ + 20-modules/03-security.md
> **参考基线**: `/home/spharx/SpharxWorks/01Reference/kernel-OLK-6.6`（Linux 6.6 内核源码）
> **验证方法**: Grep 精确扫描 + OLK-6.6 源码交叉验证 + SSoT 注册表逐条比对

---

## 目录

1. [补充发现总览](#1-补充发现总览)
2. [P0 补充阻断性问题](#2-p0-补充阻断性问题)
3. [P1 补充开发障碍](#3-p1-补充开发障碍)
4. [Agent 初步报告误报澄清](#4-agent-初步报告误报澄清)
5. [SSoT 规则编号体系完整性审计](#5-ssot-规则编号体系完整性审计)
6. [修复优先级与工时估算](#6-修复优先级与工时估算)
7. [对主报告评分的影响](#7-对主报告评分的影响)

---

## 1. 补充发现总览

### 1.1 验证方法论

工程标准 Agent（034667e9）初步报告了 52 项问题（12 P0 + 24 P1 + 16 P2）。为保证报告准确性，本轮对其中 5 项关键发现执行了**源码级二次验证**：

| 验证项 | 验证方法 | 验证结论 |
|--------|---------|---------|
| OS-KER-007 多重冲突定义 | Grep 全仓扫描 OS-KER-007 所有引用 + SSoT 注册表比对 | ✅ **确认**（实际比 Agent 报告的 3 种更严重，达 7 种） |
| SPDX 许可证三套策略冲突 | Grep 全仓扫描 SPDX-License-Identifier + OLK-6.6 内核许可证要求比对 | ✅ **确认**（AGPL-3.0 / GPL-2.0 / Apache-2.0 三套并存） |
| SSoT 编号大面积未注册 | 07-maintainers-and-governance.md 注册表逐条比对实际文档引用 | ✅ **确认**（注册表仅 8 条 OS-KER，实际文档使用 17+ 条） |
| static_assert trace_id 偏移矛盾 | 读取 02-ipc-protocol.md 结构体定义 + 手动计算字段偏移 | ❌ **误报**（偏移 24 正确且一致） |
| IRON-9 v2 四种不同定义 | Grep 全仓扫描 IRON-9 v2 所有引用 | ❌ **误报**（表述一致："同源且部分代码共享" + [SC]/[SS]/[IND]） |

### 1.2 补充发现统计

| 严重级别 | 主报告数量 | 本轮补充 | 合计 | 验证状态 |
|---------|-----------|---------|------|---------|
| P0 阻断性 | 13 | **+3** | 16 | 全部源码级验证确认 |
| P1 开发障碍 | 14 | **+1** | 15 | 源码级验证确认 |
| 误报澄清 | — | **2** | — | 源码级验证排除 |
| **合计** | **39** | **+6** | **45** | — |

---

## 2. P0 补充阻断性问题

### TS-P0-14: OS-KER-007 七重冲突定义（SSoT 系统性违反）

| 属性 | 内容 |
|------|------|
| **严重级别** | P0 阻断性 |
| **问题类型** | SSoT 规则编号系统性冲突 |
| **比主报告 TS-P0-08 更严重** | TS-P0-08 报告 OS-KER-013/014/015 三重冲突；本项发现 OS-KER-007 存在**七重冲突**，影响范围更广 |

**SSoT 注册表权威定义**（[07-maintainers-and-governance.md:477](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/50-engineering-standards/07-maintainers-and-governance.md)）：

> OS-KER-007 | 内核态禁止使用 float/double 类型（`-mno-80387`），改用 Q16.16 定点数 | 01 代码规范（2026-07-08 新增）

**实际文档中的 7 种不同定义**：

| # | 定义 | 文件:行号 | 与注册表一致性 |
|---|------|---------|--------------|
| 1 | 内核态禁止 float/double，改用 Q16.16（**注册表定义**） | 07-maintainers-and-governance.md:477、00-engineering-standards-handbook.md:153、60-checkpatch-rule-map.md:718、C_coding_style_standard_supplement.md:22/194/602 | ✅ 一致 |
| 2 | 共享数据必须用同步原语保护（spinlock/mutex/barrier/RCU） | C_coding_style_standard.md:475、01-coding-standards.md:484/657 | ❌ 冲突 |
| 3 | 非函数语句块开括号在行末（K&R 风格） | 02-code-format.md:156/158/436/438/439/459 | ❌ 冲突 |
| 4 | 子目录禁止修改上游 Makefile，仅 `TARGETS +=` 单行追加 | 80-testing/02-kselftest.md:120/384 | ❌ 冲突 |
| 5 | Makefile.airymaxos 仅放版本四元组，禁止塞特性 | 70-build-system/01-kbuild-system.md:322/413 | ❌ 冲突 |
| 6 | ruleset 是策略载体，运行时不可变 | 110-security/02-landlock-sandbox.md:413/451 | ❌ 冲突 |
| 7 | trace_array_create 创建独立 instance，不污染全局主缓冲 | 90-observability/01-ftrace-framework.md:316 | ❌ 冲突 |

**影响分析**：

- 7 种定义分属 4 个完全不同的工程领域（内核类型约束 / 代码格式 / 构建系统 / 安全策略 / 可观测性），同一编号被 7 份文档指代 7 条互不相关的规则
- SSoT 注册表声称是"单一事实源"，但 OS-KER-007 的 6/7 引用与注册表定义冲突，注册表权威性被架空
- `02-code-format.md` 甚至将 OS-KER-007 同时用于"开括号风格"（行 156）和引用 OS-KER-007/008 作为 clang-format `BreakBeforeBraces` 配置依据（行 436），但注册表中 OS-KER-008 是"bool 仅用于返回值"，与括号风格无关

**修复方案**：

```
1. 以 SSoT 注册表定义为准（OS-KER-007 = 内核态禁 float）
2. 6 处冲突引用重新编号：
   - "共享数据同步原语" → OS-KER-009（新增，内核并发规则）
   - "开括号 K&R 风格" → OS-STD-FMT-003（新增，格式规则）
   - "子目录不改上游 Makefile" → OS-STD-CODE-005（新增，构建规则）
   - "Makefile.airymaxos 版本四元组" → OS-STD-CODE-006（新增，构建规则）
   - "ruleset 策略载体" → OS-KER-010（新增，内核安全规则）
   - "trace_array 独立 instance" → OS-KER-011（新增，可观测性规则）
3. 全部新编号注册到 SSoT 注册表 10.3 节
4. 6 份文档的旧引用批量更新
```

**涉及文件**（6 份）：

1. [50-engineering-standards/10-coding-style/C_coding_style_standard.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/50-engineering-standards/10-coding-style/C_coding_style_standard.md)（1 处）
2. [50-engineering-standards/01-coding-standards.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/50-engineering-standards/01-coding-standards.md)（2 处）
3. [50-engineering-standards/02-code-format.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/50-engineering-standards/02-code-format.md)（6 处）
4. [80-testing/02-kselftest.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/80-testing/02-kselftest.md)（2 处）
5. [70-build-system/01-kbuild-system.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/70-build-system/01-kbuild-system.md)（2 处）
6. [110-security/02-landlock-sandbox.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/110-security/02-landlock-sandbox.md)（2 处）
7. [90-observability/01-ftrace-framework.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/90-observability/01-ftrace-framework.md)（1 处）

**验证命令**：

```bash
grep -rn "OS-KER-007" docs/AirymaxAgentOS/ | grep -v "07-maintainers-and-governance"
# 预期修复后：所有非注册表引用的规则语义应与"内核态禁 float"一致
```

**修复工时**：4h（编号分配 1h + 注册表更新 0.5h + 6 文件引用更新 2h + 验证 0.5h）

---

### TS-P0-15: SPDX 许可证三套策略冲突（内核许可证合规风险）

| 属性 | 内容 |
|------|------|
| **严重级别** | P0 阻断性 |
| **问题类型** | 许可证策略不一致 + 内核许可证合规风险 |

**三套 SPDX 许可证策略**：

| 策略 | 许可证 | 使用位置 | 文件数 |
|------|--------|---------|--------|
| A（项目标准） | `AGPL-3.0-or-later OR Apache-2.0` | 文档头 `> **SPDX-License-Identifier**` | ~30+ |
| B（内核/构建代码示例） | `GPL-2.0` | 构建系统 Makefile 示例 + C/Rust 代码示例 | ~8 |
| C（合规检查示例） | `Apache-2.0` | compliance-checklist 检查脚本示例 | 1 |

**冲突详情**：

| # | 文件:行号 | 实际 SPDX | 应使用策略 | 冲突类型 |
|---|---------|---------|-----------|---------|
| 1 | [70-build-system/README.md:66](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/70-build-system/README.md) | `GPL-2.0` | B（内核代码） | 无冲突，但未声明策略 B 适用范围 |
| 2 | [70-build-system/02-kconfig-system.md:269](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/70-build-system/02-kconfig-system.md) | `GPL-2.0` | B | 同上 |
| 3 | [70-build-system/01-kbuild-system.md:155/281](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/70-build-system/01-kbuild-system.md) | `GPL-2.0` | B | 同上 |
| 4 | [50-engineering-standards/10-coding-style/C_coding_style_standard.md:615](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/50-engineering-standards/10-coding-style/C_coding_style_standard.md) | `GPL-2.0-only` | B | `-only` 后缀与策略 B 的 `GPL-2.0`（含 or-later）不一致 |
| 5 | [50-engineering-standards/10-coding-style/Rust_coding_style_standard.md:441](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/50-engineering-standards/10-coding-style/Rust_coding_style_standard.md) | `GPL-2.0` | B | 无冲突 |
| 6 | [50-engineering-standards/80-clang-format-enforcement.md:21](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/50-engineering-standards/80-clang-format-enforcement.md) | `GPL-2.0`（.clang-format 文件） | B | 无冲突 |
| 7 | [50-engineering-standards/08-compliance-checklist.md:222](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/50-engineering-standards/08-compliance-checklist.md) | `Apache-2.0` | C | 与策略 A/B 均不同 |

**核心合规风险**：

1. **AGPL-3.0 与 GPL-2.0 不兼容**：AGPL-3.0（策略 A）与 GPL-2.0（策略 B）在许可证条款上**不兼容**。Linux 内核代码必须使用 GPL-2.0（`include/uapi/linux/capability.h` 等内核头文件均为 GPL-2.0），但项目文档头声明 AGPL-3.0。若 agentrt-linux 内核代码引用 AGPL-3.0 许可证，将无法与 GPL-2.0 内核代码合法链接
2. **策略边界未声明**：三套许可证的使用边界未在任何文档中明确声明（何时用 AGPL-3.0、何时用 GPL-2.0、何时用 Apache-2.0）
3. **`-only` 后缀不一致**：`C_coding_style_standard.md:615` 使用 `GPL-2.0-only`，其他位置使用 `GPL-2.0`（默认含 or-later），条款范围不一致

**OLK-6.6 源码验证**：

```bash
# OLK-6.6 内核源码许可证
grep -r "SPDX-License-Identifier" 01Reference/kernel-OLK-6.6/COPYING
# 结果：GPL-2.0-only WITH Linux-syscall-note
```

**修复方案**：

```
1. 在 50-engineering-standards/ 建立许可证策略矩阵：
   - 内核态代码（.c/.h 进入 vmlinuz）：GPL-2.0-only WITH Linux-syscall-note（对齐 OLK-6.6）
   - 用户态运行时代码（agentrt）：AGPL-3.0-or-later OR Apache-2.0
   - 文档（.md）：AGPL-3.0-or-later OR Apache-2.0
   - 构建脚本（Makefile/.clang-format）：GPL-2.0
   - 检查脚本（.sh/.py）：Apache-2.0
2. 08-compliance-checklist.md:222 的 Apache-2.0 示例补充说明"适用于检查脚本"
3. C_coding_style_standard.md:615 的 GPL-2.0-only 统一为 GPL-2.0-only WITH Linux-syscall-note
4. 全仓 SPDX-License-Identifier 一致性 CI 检查
```

**涉及文件**（7 份，~15 处）

**修复工时**：3h（策略矩阵设计 1h + 7 文件修复 1h + CI 检查脚本 1h）

---

### TS-P0-16: SSoT 规则编号大面积未注册 + 双格式并存

| 属性 | 内容 |
|------|------|
| **严重级别** | P0 阻断性 |
| **问题类型** | SSoT 注册表完整性失效 + 编号格式双轨制 |

**问题一：OS-KER 编号超范围使用**

SSoT 注册表（[07-maintainers-and-governance.md:467-478](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/50-engineering-standards/07-maintainers-and-governance.md)）仅注册 **OS-KER-001 ~ OS-KER-008**（8 条），但实际文档使用了**未注册的 OS-KER-009 ~ OS-KER-017+**：

| 未注册编号 | 实际使用位置 | 规则语义 |
|-----------|------------|---------|
| OS-KER-011 | 80-clang-format-enforcement.md:41/560/561/562 | Tab 缩进宽度 8 |
| OS-KER-012 | 80-clang-format-enforcement.md:55/559/569 | 行宽 80 |
| OS-KER-013 | 80-clang-format-enforcement.md:549 | typedef 限制 |
| OS-KER-015 | 80-clang-format-enforcement.md:548 | BUG_ON 禁用 |
| OS-KER-017 | 02-code-format.md:459 | 连续空行最多 1 |

> **注**：OS-KER-013/014/015 的三重冲突已在主报告 TS-P0-08 中记录。本项补充发现的是**未注册**问题——这些编号从未进入 SSoT 注册表。

**问题二：OS-STD 编号双格式并存**

SSoT 注册表定义的格式为 `OS-STD-<子域>-NNN`（如 OS-STD-CODE-001、OS-STD-FMT-001、OS-STD-GOV-001），但 [06-toolchain-and-automation.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/50-engineering-standards/06-toolchain-and-automation.md) 大量使用**无子域**的 `OS-STD-NNN` 格式：

| 无子域编号 | 文件:行号 | 规则语义 | 应归属子域 |
|-----------|---------|---------|-----------|
| OS-STD-002 | 06:46 | C 代码双编译器交叉验证 | OS-STD-CODE |
| OS-STD-003 | 06:47 | Rust 代码 cargo build + clippy | OS-STD-CODE |
| OS-STD-011 | 06:53 | 静态分析 0 错误 | OS-STD-CODE |
| OS-STD-012 | 06:54 | 新增 sparse/Smatch 警告禁止合并 | OS-STD-CODE |
| OS-STD-021 | 06:60 | pre-commit-config.yaml | OS-STD-GOV |
| OS-STD-022 | 06:61 | DCO bot 验证 | OS-STD-GOV |
| OS-STD-023 | 06:62 | make format-check | OS-STD-FMT |
| OS-STD-031 | 06:68 | PR 通过所有 Actions | OS-STD-GOV |
| OS-STD-032 | 06:69 | CI 矩阵 9 种组合 | OS-STD-GOV |
| OS-STD-033 | 06:70 | CI 总时长 ≤ 60 分钟 | OS-STD-GOV |
| OS-STD-041 | 06:76 | EXPORT_SYMBOL 须在 Module.symvers | OS-STD-CODE |
| OS-STD-042 | 06:77 | check_abisym.sh ABI 兼容性 | OS-STD-CODE |
| OS-STD-051 | 06:83 | airymax-ipc-check 向后兼容 | OS-STD-CODE |
| OS-STD-052 | 06:84 | SDK 行为契约测试 | OS-STD-CODE |
| OS-STD-061 | 06:90 | 发布版本 GPG 签名 | OS-STD-GOV |
| OS-STD-062 | 06:91 | 内核模块必须签名 | OS-STD-GOV |
| OS-STD-071 | 06:142 | gcc -W 编译通过 | OS-STD-CODE |
| OS-STD-072 | 06:158 | allnoconfig/allmod/defconfig 编译 | OS-STD-CODE |
| OS-STD-073 | 06:166 | x86_64/aarch64/riscv64 交叉编译 | OS-STD-CODE |
| OS-STD-074 | 06:167 | ppc64 推荐交叉编译 | OS-STD-CODE |
| OS-STD-075 | 06:172 | Rust cargo build --target | OS-STD-CODE |

此外，[02-code-format.md:459](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/50-engineering-standards/02-code-format.md) 引用了 `OS-STD-206`（3 位数字格式），[06-toolchain-and-automation.md:68](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/50-engineering-standards/06-toolchain-and-automation.md) 引用了 `OS-STD-233`——这两个编号在 SSoT 注册表中**完全不存在**（幽灵引用）。

**影响分析**：

- SSoT 注册表声称是"单一事实源"并规定了 `OS-<前缀>-<子域>-NNN` 格式，但 21 条 OS-STD 规则使用了无子域格式，注册表权威性失效
- OS-STD-206 和 OS-STD-233 是**幽灵引用**——引用了不存在的规则，开发者无法追溯
- 与主报告 TS-P0-08（OS-KER-013/014/015 三重冲突）叠加，SSoT 体系存在**三个层面**的失效：编号冲突 + 编号未注册 + 编号格式不统一

**修复方案**：

```
1. 将 21 条 OS-STD-NNN 重新编号为带子域格式：
   OS-STD-002 → OS-STD-CODE-006
   OS-STD-003 → OS-STD-CODE-007
   ...（按子域归类）
2. OS-STD-206 → 查明实际规则后分配新编号或删除幽灵引用
3. OS-STD-233 → 同上
4. OS-KER-009~017 全部注册到 SSoT 10.3 节
5. 06-toolchain-and-automation.md 全文编号更新（~21 处）
6. 建立 CI 检查：所有引用的规则编号必须在 SSoT 注册表中存在
```

**涉及文件**：06-toolchain-and-automation.md（21 处）+ 02-code-format.md（1 处）+ 80-clang-format-enforcement.md（5 处）

**修复工时**：6h（编号重分配 2h + 注册表扩充 1h + 文档更新 2h + CI 检查脚本 1h）

---

## 3. P1 补充开发障碍

### TS-P1-15: OS-STD-233 幽灵规则引用

| 属性 | 内容 |
|------|------|
| **严重级别** | P1 开发障碍 |
| **问题类型** | 引用不存在的规则编号 |

**问题**：[06-toolchain-and-automation.md:68](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/50-engineering-standards/06-toolchain-and-automation.md) 第 68 行：

> OS-STD-031：PR 必须通过所有 GitHub Actions 检查才能合并；任一失败禁止合并（与 OS-STD-233 对齐）。

`OS-STD-233` 在 SSoT 注册表和全仓文档中**均不存在**。开发者无法追溯"OS-STD-233"所指的规则。

**验证命令**：

```bash
grep -rn "OS-STD-233" docs/AirymaxAgentOS/
# 仅返回 06-toolchain-and-automation.md:68 自身引用，无定义来源
```

**修复方案**：删除"（与 OS-STD-233 对齐）"引用，或查明实际规则后替换为有效编号。

**修复工时**：0.5h

---

## 4. Agent 初步报告误报澄清

工程标准 Agent（034667e9）初步报告了部分问题，经源码级二次验证后确认为**误报**。此处记录澄清，避免误报传播。

### 4.1 误报一：static_assert trace_id 偏移矛盾（已排除）

| 属性 | 内容 |
|------|------|
| **Agent 初步报告** | static_assert 与结构体定义矛盾（trace_id offset 24 vs 实际 16） |
| **验证结论** | ❌ **误报**——偏移 24 正确且一致 |

**验证过程**：

读取 [30-interfaces/02-ipc-protocol.md:58-69](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxAgentOS/30-interfaces/02-ipc-protocol.md) 的结构体定义：

```c
typedef struct __attribute__((aligned(64))) agentrt_ipc_msg_hdr {
    uint32_t magic;          /* offset 0,  size 4 */
    uint16_t version;        /* offset 4,  size 2 */
    uint16_t type;           /* offset 6,  size 2 */
    uint32_t payload_len;    /* offset 8,  size 4 */
    uint32_t flags;          /* offset 12, size 4 */
    uint32_t src_pid;        /* offset 16, size 4 */
    uint32_t dst_pid;        /* offset 20, size 4 */
    uint64_t trace_id;       /* offset 24, size 8 */  ← 正确
    uint64_t timestamp_ns;   /* offset 32, size 8 */
    uint8_t  reserved[72];   /* offset 40, size 72 */
} agentrt_ipc_msg_hdr_t;
```

手动计算偏移：magic(0) → version(4) → type(6) → payload_len(8) → flags(12) → src_pid(16) → dst_pid(20) → **trace_id(24)**。

`uint64_t trace_id` 要求 8 字节对齐，offset 24 是 8 的倍数，无需填充。偏移 24 **正确**。

三处引用一致：
- 02-ipc-protocol.md:88 字段表：`trace_id | 24 | 8`
- 02-ipc-protocol.md:71 `static_assert(sizeof(...) == 128)`（sizeof 校验，非 offset）
- 40-integration/agentrt_integration.md:616 `static_assert(offsetof(airymax_ipc_msg_hdr_t, trace_id) == 24)`

**结论**：Agent 报告的"实际 16"是错误计算（遗漏了 src_pid 和 dst_pid 两个 uint32_t 字段共 8 字节）。trace_id 偏移在所有文档中**完全一致**，不存在矛盾。**此项不纳入问题清单**。

### 4.2 误报二：IRON-9 v2 四种不同定义（已排除）

| 属性 | 内容 |
|------|------|
| **Agent 初步报告** | IRON-9 v2 有 4 种不同定义（三层模型 / 硬件平台 / CI/CD 引擎 / 集成层） |
| **验证结论** | ❌ **误报**——IRON-9 v2 表述全仓一致 |

**验证过程**：

Grep 全仓扫描 `IRON-9 v2`（60 行匹配），所有引用的表述统一为：

> **IRON-9 v2 同源且部分代码共享**——[SC] 共享契约层 / [SS] 语义同源层 / [IND] 完全独立层

三层模型在以下文档中表述完全一致：
- 30-interfaces/README.md:109
- 110-security/01-lsm-framework.md:10/422/488
- 150-cloudnative/README.md:143
- 160-compatibility/README.md:147
- 170-performance/README.md:169
- 110-security/02-landlock-sandbox.md:10/421/489

**结论**：IRON-9 v2 的定义在全仓范围内**完全一致**，不存在"4 种不同定义"。Agent 可能将不同文档对三层模型的不同**应用场景描述**误判为"不同定义"。**此项不纳入问题清单**。

> **注**：主报告 TS-P0-12 报告的"IRON-9 v2 三层模型 RT 侧缺失"是**不同问题**——指 agentrt（用户态）侧文档未定义 [SC]/[SS]/[IND] 模型，而非模型本身定义不一致。该问题经独立验证确认成立，保留在主报告中。

---

## 5. SSoT 规则编号体系完整性审计

### 5.1 注册表 vs 实际使用对比

| 编号前缀 | SSoT 注册数量 | 实际文档使用数量 | 缺口 | 完整性 |
|---------|-------------|----------------|------|--------|
| OS-IRON | 10 | 10 | 0 | ✅ 100% |
| OS-STD-CODE | 4 | 4 + 21（无子域格式） | 21 未注册 | ⚠️ 16% |
| OS-STD-FMT | 2 | 2 | 0 | ✅ 100% |
| OS-STD-STY | 2 | 2 | 0 | ✅ 100% |
| OS-STD-GOV | 7 | 7 | 0 | ✅ 100% |
| OS-KER | 8 | 13（含 009-017 未注册） | 5 未注册 | ⚠️ 62% |
| OS-BAN | 6 | 6 | 0 | ✅ 100% |
| OS-ABI | 1 | 1 | 0 | ✅ 100% |
| OS-ACC | 5 | 5 | 0 | ✅ 100% |
| **合计** | **45** | **61** | **26 未注册** | **74%** |

### 5.2 SSoT 失效三层模型

```
┌─────────────────────────────────────────────────────────────┐
│              SSoT 规则编号体系失效（三层）                    │
├─────────────────────────────────────────────────────────────┤
│  层面 1：编号冲突（主报告 TS-P0-08）                         │
│  ├── OS-KER-013/014/015 三重冲突                             │
│  └── OS-KER-007 七重冲突（本报告 TS-P0-14）                  │
├─────────────────────────────────────────────────────────────┤
│  层面 2：编号未注册（本报告 TS-P0-16）                       │
│  ├── OS-KER-009~017 共 5 条未注册                            │
│  └── OS-STD-NNN 无子域格式 21 条未注册                       │
├─────────────────────────────────────────────────────────────┤
│  层面 3：编号格式不统一（本报告 TS-P0-16）                   │
│  ├── 注册表格式：OS-STD-<子域>-NNN                           │
│  ├── 实际格式 1：OS-STD-NNN（无子域，21 处）                 │
│  └── 实际格式 2：OS-STD-NNN（3 位数字，2 处幽灵引用）        │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 修复优先级

| 优先级 | 修复项 | 影响范围 | 工时 |
|--------|--------|---------|------|
| P0 | OS-KER-007 七重冲突消解 | 6 文件 15 处 | 4h |
| P0 | OS-KER-009~017 注册到 SSoT | 注册表 + 3 文件 | 2h |
| P0 | OS-STD-NNN → OS-STD-<子域>-NNN | 06-toolchain 21 处 | 4h |
| P0 | OS-STD-206/233 幽灵引用消解 | 2 文件 | 0.5h |
| P0 | SPDX 许可证策略矩阵 | 7 文件 15 处 | 3h |
| **合计** | — | ~18 文件 ~55 处 | **13.5h** |

---

## 6. 修复优先级与工时估算

### 6.1 补充发现修复工时

| 编号 | 严重级别 | 标题 | 工时 | 修复阶段 |
|------|---------|------|------|---------|
| TS-P0-14 | P0 | OS-KER-007 七重冲突消解 | 4h | M0 第 1 周 |
| TS-P0-15 | P0 | SPDX 许可证三套策略冲突 | 3h | M0 第 1 周 |
| TS-P0-16 | P0 | SSoT 编号大面积未注册 + 双格式 | 6h | M0 第 1 周 |
| TS-P1-15 | P1 | OS-STD-233 幽灵规则引用 | 0.5h | M0 第 2 周 |
| **合计** | — | — | **13.5h** | — |

### 6.2 与主报告修复计划合并

| 阶段 | 主报告工时 | 补充工时 | 合计 |
|------|-----------|---------|------|
| M0 第 1 周（P0） | 49h | +13h（TS-P0-14/15/16） | 62h |
| M0 第 2 周（P1） | 26h | +0.5h（TS-P1-15） | 26.5h |
| **总计** | **75h** | **13.5h** | **88.5h** |

---

## 7. 对主报告评分的影响

### 7.1 工程标准维度评分修正

主报告第 11 章工程标准维度评分 75/100。补充发现 3 项 P0 后，该维度实际状况更严峻：

| 工程标准子维度 | 主报告评估 | 补充发现影响 | 修正评估 |
|--------------|-----------|------------|---------|
| SSoT 注册表完整性 | 已消解 OS-KER-001/OS-STD-001 冲突 | +OS-KER-007 七重冲突 + 26 条未注册 | ⬇️ 显著下降 |
| 规则编号一致性 | 14 处旧编号已更新 | +21 处无子域格式 + 2 处幽灵引用 | ⬇️ 下降 |
| 许可证策略 | 未审查 | +3 套策略冲突 + AGPL/GPL 不兼容风险 | ⬇️ 新增扣分 |
| 编码规范可追溯性 | 11 个不存在文件（TS-P0-03） | +OS-STD-233 幽灵引用 | ⬇️ 略降 |

**工程标准维度修正评分**：75 → **68/100**

### 7.2 综合评分修正

| 维度 | 主报告评分 | 修正评分 | 变化 | 说明 |
|------|-----------|---------|------|------|
| 合规性 | 82 | 82 | 0 | 无新发现 |
| 文档完整性 | 80 | 80 | 0 | 无新发现 |
| 工程标准 | 75 | **68** | **-7** | SSoT 三层失效 + SPDX 冲突 |
| 技术正确性 | 78 | 78 | 0 | 无新发现 |
| 交付就绪度 | 80 | 80 | 0 | 无新发现 |
| **综合评分** | **79** | **76** | **-3** | B- 级，有条件 Go |

### 7.3 修正后 Go/No-Go 判定

**修正后状态**：76/100（B- 级）—— **有条件 Go**

Go 条件（M0 第 1 周内完成）：
1. 主报告 13 项 P0 + 本报告 3 项 P0 = **16 项 P0 全部修复**（预估 62h）
2. 主报告 14 项 P1 关键项 + 本报告 1 项 P1 = **15 项 P1 修复计划确认**
3. SSoT 规则编号体系完整性提升至 ≥ 95%（当前 74%）

---

## 附录：验证命令清单

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | OS-KER-007 冲突 | `grep -rn "OS-KER-007" docs/AirymaxAgentOS/ \| grep -v "float\|mno-80387\|q16"` | 修复后 0 结果 |
| 2 | SPDX 许可证一致性 | `grep -rn "SPDX-License-Identifier" docs/AirymaxAgentOS/ \| grep -v "AGPL-3.0-or-later OR Apache-2.0"` | 仅保留策略 B/C 声明位置 |
| 3 | OS-KER 未注册编号 | `grep -rEn "OS-KER-0(09\|1[0-9])" docs/AirymaxAgentOS/50-engineering-standards/07-maintainers-and-governance.md` | 修复后全部注册 |
| 4 | OS-STD 无子域格式 | `grep -rEn "OS-STD-[0-9]{3}" docs/AirymaxAgentOS/ \| grep -v "CODE\|FMT\|STY\|GOV"` | 修复后 0 结果 |
| 5 | 幽灵引用 | `grep -rn "OS-STD-233\|OS-STD-206" docs/AirymaxAgentOS/` | 修复后 0 结果 |
| 6 | capability 数量 | `grep -c "#define CAP_" 01Reference/kernel-OLK-6.6/include/uapi/linux/capability.h` | 41（已验证） |

---

> **文档结束** | agentrt-linux（AirymaxOS）工程标准补充发现报告 | v1.0 | 2026-07-09
> 
> **配套文档**：[03-technical-standards-and-specifications-review.md](./03-technical-standards-and-specifications-review.md)（主报告，39 项问题）
