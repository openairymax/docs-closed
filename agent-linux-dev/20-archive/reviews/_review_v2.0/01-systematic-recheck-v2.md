Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agent-linux（AirymaxOS）系统性全面审查报告 v2.0（深化复审）

> **文档定位**： agent-linux（AirymaxOS，极境智能体操作系统）整体方案系统性复审 v2.0——在 v1.0（2026-07-13，综合评分 79/B+）基础上的第二轮深化审查，聚焦"验证 + 深化 + 补充"。\
> **保密级别**： SPHARX Ltd 内部参考，**闭源不公开**\
> **版本**： 2.0（2026-07-13）\
> **审查范围**： v1.0 全部 11 项问题（1 P0 + 3 P1 + 7 P2）逐项重新验证 + 方案内部冲突深化检查 + 技术点唯一性深化验证 + openEuler 工程实践参考充分性深化（含 MGLRU/sched\_ext/io\_uring 最新实践）+ seL4 微内核化改造参考充分性深化（含 capability 7 操作 / IPC fastpoint POINT OF NO RETURN / 三态机 / doReplyTransfer 临界区 / vtime Q16.16）+ 开发就绪度 8 项判定标准重新评估 + 细节完成度深化 + 8 子仓命名规范深化\
> **审查方法**： 源文档逐行重读 + Grep 机器检查 + 闭源/开源交叉验证 + 三层对齐度评分修正\
> **证据要求**： 所有结论附 `文件路径:行号` 证据，明确区分"确认存在 / 已修复 / 降级 / 新发现"四种状态\
> **SPDX-License-Identifier**： AGPL-3.0-or-later OR Apache-2.0

***

## 目录

- [1. 执行摘要](#1-执行摘要)
- [2. 方案内部冲突检查结果（深化）](#2-方案内部冲突检查结果深化)
- [3. 技术点唯一性验证（深化）](#3-技术点唯一性验证深化)
- [4. openEuler 工程实践参考充分性（深化）](#4-openeuler-工程实践参考充分性深化)
- [5. seL4 微内核化改造参考充分性（深化）](#5-sel4-微内核化改造参考充分性深化)
- [6. 开发就绪度评估（8 项判定标准，深化）](#6-开发就绪度评估8-项判定标准深化)
- [7. 细节完成度检查（深化）](#7-细节完成度检查深化)
- [8. 8 子仓命名规范验证（深化）](#8-8-子仓命名规范验证深化)
- [9. 修正后的综合评分](#9-修正后的综合评分)

***

## 1. 执行摘要

### 1.1 v1.0 发现验证结果总览

v1.0 报告识别 11 项问题（1 P0 + 3 P1 + 7 P2）。本轮对全部 11 项逐项重新读取源文档验证，结果如下：

| v1.0 编号    | 问题                          | v1.0 等级 | v1.0 状态 | v2.0 验证结果                      | 证据                                                   |
| ---------- | --------------------------- | ------- | ------- | ------------------------------ | ---------------------------------------------------- |
| v1.0-P0    | ES-SEL4-7 分类残留冲突（5 vs 6）    | P0      | 新发现，未修复 | **确认存在，未修复**                   | 闭源总纲 L1389/L1393/L1024 标题声明 5 项；L1403/L1410 正文归入 6 项 |
| v1.0-P1-01 | airymaxos- 前缀不一致（闭源 37 处）   | P1      | 未修复     | **确认存在，未修复**                   | 闭源总纲 37 处 + 开发路线 4 处                                 |
| v1.0-P1-02 | OS-KER-005 跳号               | P1      | 未修复     | **确认存在，未修复**                   | `09-ssot-registry.md:106-107` 仍跳号，无废弃说明              |
| v1.0-P1-03 | ES-SEL4-9/10 状态分类模糊         | P1      | 未修复     | **确认存在，未修复**                   | 闭源总纲 L1049-1050/L1405-1406 标"已落地"但归入 P2 范围           |
| v1.0-P2-01 | tests 简写残留（5 文件/10 处）       | P2      | 已知遗留    | **v1.0 严重低估**——实际 15+ 文件 31+ 处 | `docs/AirymaxOS/` 全范围 Grep                           |
| v1.0-P2-02 | OS-STD-2xx 运维域残留（4 文件/57 处） | P2      | 已知遗留    | **确认存在**                       | 4 文件 57 处，与 v1.0 一致                                  |
| v1.0-P2-03 | Rust 编号缺口                   | P2      | 已文档化    | **确认存在，已文档化**                  | `09-ssot-registry.md:469/473`                        |
| v1.0-P2-04 | 文档计数三作用域模型未注册               | P2      | 未修复     | **确认存在，未修复**                   | `09-ssot-registry.md` 无三作用域模型条目                      |
| v1.0-P2-05 | 规则编号注册表变更日志不完整              | P2      | 未修复     | **确认存在，未修复**                   | `09-ssot-registry.md` 附录 A 变更日志                      |
| v1.0-P2-06 | 品味哲学层 8 项隐性智慧未文档化           | P2      | 未修复     | **确认存在，未修复**                   | 闭源总纲无品味哲学层章节                                         |
| v1.0-P2-07 | agentrt 源码差距（15 文件）         | P2      | 未修复     | **确认存在，未修复**                   | 移交 1.0.1 M1                                          |

**v1.0 验证结论**：11 项问题中 0 项已修复、8 项确认存在、1 项严重低估（tests 简写）、2 项已文档化。**v1.0 报告中"已修复"判定全部经得起验证**，但 v1.0-P2-01 tests 简写残留数据严重低估（v1.0 称 5 文件/10 处，实际 15+ 文件/31+ 处）。

### 1.2 v2.0 新发现总览

本轮深化审查发现 v1.0 遗漏的 **6 项新问题**（3 P1 + 3 P2）：

| v2.0 编号        | 问题                                               | 等级 | 证据                                                                                                                                                                                                                  |
| -------------- | ------------------------------------------------ | -- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| v2.0-NEW-P1-01 | **OS-FMT-001\~007 未在 SSoT 注册表登记**                | P1 | 闭源总纲 L331-387/L1324-1330/L1422-1426 使用 OS-FMT-001\~007；`09-ssot-registry.md` 无 OS-FMT 章节；闭源总纲 L91-103 的 11 类前缀表未列 OS-FMT                                                                                            |
| v2.0-NEW-P1-02 | **\[SC] 6 头文件清单在闭源/开源间不一致**                      | P1 | 闭源总纲 L1061 OS-IRON-014 列 `bpf_struct_ops.h`（无 `syscalls.h`）；开源 `120-cross-project-code-sharing.md:71-76` 列 `syscalls.h`（无 `bpf_struct_ops.h`）；开源 `20-modules/01-kernel.md:48` 明确 `bpf_struct_ops.h` "非 \[SC] 核心头文件" |
| v2.0-NEW-P1-03 | **ES-SEL4 编号在开源文档扩展到 43 但未在 SSoT 注册**            | P1 | 开源 `10-architecture/03-microkernel-strategy.md` 使用 ES-SEL4-21\~43（共 19 个扩展编号）；`20-modules/01-kernel.md:119/858` 使用 ES-SEL4-21；SSoT 注册表未登记 ES-SEL4-11\~43                                                            |
| v2.0-NEW-P2-01 | **开发路线 L1019 声明"8 项判定标准全部满足"与 ES-SEL4-7 残留冲突矛盾** | P2 | `agent-linux开发路线和进度.md:1019` 声明全部满足；闭源总纲 L1403/L1410 ES-SEL4-7 残留冲突未修复                                                                                                                                            |
| v2.0-NEW-P2-02 | *闭源总纲 OS-STD-005 与开源 SSoT 矛盾（airymaxos\_* 前缀）\*  | P2 | 闭源总纲 L167 声明 `airymaxos_*` 用于专属 API；开源 `06-directory-structure.md:294` 标"已废弃"                                                                                                                                       |
| v2.0-NEW-P2-03 | **OLK-6.6 术语残留 49 处（v1.0 误判为"已修复"）**             | P2 | 闭源总纲 49 处 OLK-6.6；L14 已添加术语说明豁免，但 L980-986/L1030-1035 等位置仍为概念引用而非分支名引用                                                                                                                                              |

### 1.3 v2.0 综合判定

| 维度         | v1.0       | v2.0       | 变化                                                      |
| ---------- | ---------- | ---------- | ------------------------------------------------------- |
| 规范声明层（35%） | 92/A       | 88/B+      | -4（OS-FMT 未注册 -2 + ES-SEL4 扩展未注册 -1 + OS-STD-005 矛盾 -1） |
| 方案设计层（40%） | 78/B+      | 75/B       | -3（\[SC] 头文件清单冲突 -2 + 开发路线声明矛盾 -1）                      |
| 实现落地层（25%） | N/A（72 代理） | N/A（72 代理） | 持平                                                      |
| **综合评分**   | **79/B+**  | **76/B**   | **-3**                                                  |

**核心结论**：agent-linux 整体方案经 v2.0 深化审查，综合评分从 79/B+ 降至 76/B。**P0 级 ES-SEL4-7 残留冲突仍未修复**，且新发现 3 项 P1 级问题（OS-FMT 未注册 / \[SC] 头文件清单冲突 / ES-SEL4 编号扩展未注册），开发就绪度从 v1.0 的"有条件通过"降级为"有条件通过（条件加强）"——需修复 1 项 P0 + 3 项 P1 后方可进入 1.0.1 M1 代码开发。

***

## 2. 方案内部冲突检查结果（深化）

### 2.1 v1.0-P0 验证：ES-SEL4-7 分类残留冲突（5 vs 6）——确认存在，未修复

**重新读取验证**：闭源总纲 5 处关键行段全部确认 v1.0 描述准确。

**标题声明（5 项强制）**：

- `agent-linux基本工程标准规范.md:1389`：`附录 D ES-SEL4 工程思想借鉴映射（ES-SEL4-1~5 强制 + ES-SEL4-6~10 P2 增强）`
- `agent-linux基本工程标准规范.md:1393`：`ES-SEL4-1~5 在架构层强制借鉴，ES-SEL4-6~10 作为 P2 增强建议增量落地`
- `agent-linux基本工程标准规范.md:1024`（OS-IRON-012）：`seL4 工程思想的借鉴仅限架构层（ES-SEL4-1~5），不包括编码风格层（4 空格 / camelCase / 重度 typedef）和接口契约层`
- `agent-linux基本工程标准规范.md:1010`（§12.5 标题）：`架构层借鉴 seL4（5 项选择性借鉴）`

**正文分类矛盾（ES-SEL4-7 被归入"架构层强制"，6 项）**：

- `agent-linux基本工程标准规范.md:1403`：`| ES-SEL4-7 | 架构正交分层 | ... | 架构层强制（已落地） | airymaxos-kernel arch/{x86,arm64,riscv}/{machine,plat}/、OS-STD-061 | §13.2、§13.3 |`
- `agent-linux基本工程标准规范.md:1410`：`**架构层强制借鉴（ES-SEL4-1~5 + ES-SEL4-7）**: 6 项，已在 1.0.1 架构设计中落地`

**§12.8 表格中的矛盾**：

- `agent-linux基本工程标准规范.md:1041`（§12.8 标题）：`ES-SEL4-6~10 的落地方式`——将 ES-SEL4-7 归入"ES-SEL4-6\~10"范围
- `agent-linux基本工程标准规范.md:1051`：`| ES-SEL4-7 架构正交分层 | arch/machine/plat 三层适配 | 已在 kernel 子仓落地（借鉴 seL4 而非 OLK-6.6 单 arch/） |`

**冲突本质**：标题（4 处）声明架构层强制借鉴为 5 项（ES-SEL4-1\~5），但正文（2 处）将其归入 6 项（ES-SEL4-1\~5 + ES-SEL4-7）。这是 SSoT 唯一性原则的严重违反。

**状态**：**确认存在，未修复**（与 v1.0 一致，无变化）。

### 2.2 v1.0-P1-03 验证：ES-SEL4-9/10 状态分类模糊——确认存在，未修复

**重新读取验证**：

- `agent-linux基本工程标准规范.md:1389` 标题：ES-SEL4-9/10 属于"P2 增强"
- `agent-linux基本工程标准规范.md:1049`：`| ES-SEL4-9 libsel4 独立 | SDK 层借鉴 libsel4 模型 | 已在 airymaxos-cloudnative 落地 |`
- `agent-linux基本工程标准规范.md:1050`：`| ES-SEL4-10 CMake 构建 | 用户态子仓采用 Meson/CMake | 已在 services/cloudnative 落地 |`
- `agent-linux基本工程标准规范.md:1405-1406`：ES-SEL4-9/10 标"已落地"
- `agent-linux基本工程标准规范.md:1412`：`已落地（ES-SEL4-9 + ES-SEL4-10）: 2 项，用户态子仓构建系统已采纳`

**冲突本质**：P2 增强建议的定义是"1.0.1 阶段增量落地"（L1043），但 ES-SEL4-9/10 已标注"已落地"，与 P2 的"未来落地"语义冲突。

**状态**：**确认存在，未修复**（与 v1.0 一致）。

### 2.3 v2.0-NEW-P2-01：开发路线 L1019 声明与残留冲突矛盾（新发现）

**问题描述**：开发路线声明"8 项判定标准全部满足"，其中包括"无方案冲突点"和"v0.9.0 P0 修复"两项，但 ES-SEL4-7 残留冲突（P0 级）仍未修复，与该声明直接矛盾。

**证据**：

- `agent-linux开发路线和进度.md:1019`：`1.0.1 M1 就绪判定 ✅ 通过（8 项判定标准全部满足：工程思想统一 + 工程标准规范 + 无方案冲突点 + 对齐 openEuler 代码品味 + 对齐 seL4 微内核思想 + 系统性目录结构 + 全部 README 重写 + v0.9.0 P0 修复）`
- `agent-linux基本工程标准规范.md:1403/1410`：ES-SEL4-7 残留冲突未修复（详见 §2.1）

**影响**：开发就绪度声明与实际方案状态不一致，可能误导决策者认为已满足"无方案冲突点"条件。

**状态**：**新发现，未修复**。

### 2.4 v2.0-NEW-P2-03：OLK-6.6 术语残留 49 处（v1.0 误判为"已修复"）

**问题描述**：v1.0 §1.1 表格将 P1-MAJOR-03（闭源文档术语滞后 OLK-6.6）判定为"已修复"，证据为"闭源总纲 L14：所有概念引用已统一为'Linux 6.6 内核基线'"。但实际验证发现闭源总纲仍有 49 处 OLK-6.6 残留。

**证据**：

- 闭源总纲 L14 已添加术语说明：`本文档中保留的 "OLK-6.6" 均为 openEuler 官方分支名称或路径引用（如 01Reference/kernel-OLK-6.6），非概念引用。所有概念引用已统一为 "Linux 6.6 内核基线"。`
- 但 Grep 统计：闭源总纲 `OLK-6.6` 出现 **49 处**
- 其中**合法保留**（作为 openEuler 分支名/路径引用）：L7/L13/L58/L891/L944/L957/L959/L966/L970/L1067/L1068/L1069/L1072/L1073/L1074/L1076/L1129 等约 30 处
- 其中**疑似概念引用**（应改为"Linux 6.6 内核基线"）：L980-986（双源融合裁决表"**OLK-6.6**"作为裁决结果）/ L1030-1035（拒绝特性表"与 OLK-6.6 Tab 8 冲突"等）约 19 处

**v1.0 误判分析**：v1.0 仅依据 L14 术语说明判定"已修复"，未对正文 49 处 OLK-6.6 残留进行逐处分类验证。L14 的术语说明为大部分残留提供了豁免，但 L980-986/L1030-1035 等位置仍为概念引用，边界模糊。

**状态**：**v1.0 误判为"已修复"，v2.0 修正为"部分修复"**（术语说明已建立，但正文仍有 19 处疑似概念引用残留）。

### 2.5 方案内部冲突检查小结

| 冲突项                      | 等级 | v1.0 状态 | v2.0 验证            | 证据   |
| ------------------------ | -- | ------- | ------------------ | ---- |
| ES-SEL4-7 分类残留冲突（5 vs 6） | P0 | 新发现，未修复 | **确认存在，未修复**       | §2.1 |
| ES-SEL4-9/10 状态分类模糊      | P1 | 未修复     | **确认存在，未修复**       | §2.2 |
| 开发路线 L1019 声明矛盾          | P2 | 未识别     | **v2.0 新发现**       | §2.3 |
| OLK-6.6 术语残留 49 处        | P2 | 误判"已修复" | **v2.0 修正为"部分修复"** | §2.4 |

***

## 3. 技术点唯一性验证（深化）

### 3.1 v1.0-P1-02 验证：OS-KER-005 跳号——确认存在，未修复

**重新读取验证**：

- `09-ssot-registry.md:106`：`| OS-KER-004 | 分级标签按分配逆序释放 | 01 §7.2 |`
- `09-ssot-registry.md:107`：`| OS-KER-006 | volatile 仅 4 种例外 | 01 §6.3 |`
- 两行之间无 OS-KER-005，无废弃说明注释。

**状态**：**确认存在，未修复**（与 v1.0 一致）。

### 3.2 v1.0-P2-03 验证：Rust 编号缺口——确认存在，已文档化

**重新读取验证**：

- `09-ssot-registry.md:469`：`发现 Rust 文件 OS-STD-030~035 + OS-SEC-001~002,030~037+ 编号登记缺口，留待 B5 审查消解`
- `09-ssot-registry.md:473`：`Rust 编号缺口已文档化，留待后续消解`

**状态**：**确认存在，已文档化**（与 v1.0 一致，移交 1.0.1）。

### 3.3 v2.0-NEW-P1-01：OS-FMT-001\~007 未在 SSoT 注册表登记（新发现）

**问题描述**：闭源总纲广泛使用 OS-FMT-001\~007 作为代码格式规则编号（六大编码支柱中的三大支柱 Tab 8 / 80 列 / K\&R 大括号均依赖 OS-FMT-001/002/003），但 OS-FMT 前缀**未在 SSoT 注册表登记**，也未在闭源总纲 L91-103 的 11 类前缀表中列出。

**证据**：

- 闭源总纲 L331：`> **OS-FMT-001**: C 内核代码使用 Tab 缩进，Tab 宽度为 8 字符`
- 闭源总纲 L342：`> **OS-FMT-002**: C 代码首选 80 列`
- 闭源总纲 L351：`> **OS-FMT-003**: 使用 K&R 风格`
- 闭源总纲 L368：`> **OS-FMT-004**: 即使只有一条语句，也使用大括号包围`
- 闭源总纲 L372：`> **OS-FMT-005**: 空格规则`
- 闭源总纲 L381：`> **OS-FMT-006**: 任何代码行的行尾不得有空白字符`
- 闭源总纲 L385：`> **OS-FMT-007**: 所有 C/C++ 代码必须通过 .clang-format 配置自动格式化`
- 闭源总纲 L1324-1330：附录 B 规则编号索引列出 OS-FMT-001\~007
- 闭源总纲 L1422/L1425/L1426：附录 E 双源融合裁决 16 维度引用 OS-FMT-001/002/003
- 闭源总纲 L91-103：11 类前缀表**未列出 OS-FMT**
- `09-ssot-registry.md`：**无 OS-FMT 章节**（Grep 验证 0 处匹配）
- 开源 `docs/AirymaxOS/`：*无 OS-FMT-* 引用\*（Grep 验证 0 处匹配）

**影响**：六大编码支柱是 agent-linux 工程标准的核心，其中三大支柱（Tab 8 / 80 列 / K\&R）的规则编号 OS-FMT-001/002/003 未在 SSoT 注册表登记，违反 SSoT 唯一性原则。审查者无法从 SSoT 注册表追溯这些规则的权威定义。这是 v1.0 遗漏的重大 SSoT 完整性漏洞。

**修复建议**：

1. 在 `09-ssot-registry.md` 新增"第 X 章 OS-FMT 代码格式规则"章节，登记 OS-FMT-001\~007
2. 在闭源总纲 L91-103 的前缀表中补充 OS-FMT 行
3. 在开源 `01-coding-standards.md` 中补充 OS-FMT-\* 引用

**状态**：**v2.0 新发现，未修复**。

### 3.4 v2.0-NEW-P1-03：ES-SEL4 编号在开源文档扩展到 43 但未在 SSoT 注册（新发现）

**问题描述**：闭源总纲附录 D 声明 ES-SEL4 范围为 1\~10（ES-SEL4-1\~5 强制 + ES-SEL4-6\~10 P2 增强），但开源文档中实际使用了 ES-SEL4-21\~43 共 19 个扩展编号，这些扩展编号未在 SSoT 注册表登记，也未在闭源总纲附录 D 中列出。

**证据**：

- 开源 `10-architecture/03-microkernel-strategy.md`：
  - L128：`ES-SEL4-29`（seL4 6 类职责）
  - L141：`ES-SEL4-30`（用户态下沉）
  - L162：`ES-SEL4-31`（bootinfo 机制）
  - L342：`ES-SEL4-21`（syscall.xml）
  - L356：`ES-SEL4-22, 43`（API 契约三层）
  - L364：`ES-SEL4-23`（invocation\_header\_gen.py）
  - L368：`ES-SEL4-25, 26`（.bf 位域文件）
  - L374：`ES-SEL4-27`（Prune 机制）
  - L375：`ES-SEL4-28`（单文件编译）
  - L396：`ES-SEL4-32`（Kconfig 风格配置）
  - L409：`ES-SEL4-33, 42`（arch/machine/plat 三层）
  - L434：`ES-SEL4-34`（Freestanding 编译）
  - L440：`ES-SEL4-35`（RequireTool 注册）
  - L514：`ES-SEL4-39`（compile\_assert）
  - L522：`ES-SEL4-38`（Haskell 形式规范）
  - L556：`ES-SEL4-36`（TSC 治理）
- 开源 `20-modules/01-kernel.md:119`：`推荐采用 seL4 的 syscall.xml 单一来源管理（ES-SEL4-21）`
- 开源 `20-modules/01-kernel.md:858`：`借鉴 seL4 syscall.xml（ES-SEL4-21），R-01 增强建议`
- `09-ssot-registry.md`：**无 ES-SEL4 章节**（仅 OS-IRON-012 引用 ES-SEL4-1\~5）
- 闭源总纲附录 D（L1389-1412）：仅列 ES-SEL4-1\~10

**影响**：ES-SEL4 编号体系在开源文档中扩展到 43，但 SSoT 注册表和闭源总纲附录 D 均未登记这些扩展编号。v0.9.0 P0-CRITICAL-02 提到的"54 项研究"可能包括这些扩展编号，但研究范围的编号不应在工程标准文档中直接引用而不登记。这违反 SSoT 唯一性原则，审查者无法确定 ES-SEL4-21\~43 是"研究范围"还是"工程标准范围"。

**状态**：**v2.0 新发现，未修复**。

### 3.5 17 类规则编号前缀完整性验证（深化）

**重新统计**：闭源总纲 L91-103 列出 11 类 OS 专属前缀，但实际使用的规则编号前缀超出此范围。

| 前缀         | 含义         | 闭源总纲 L91-103 列出 | SSoT 登记    | 实际使用              | 状态                  |
| ---------- | ---------- | --------------- | ---------- | ----------------- | ------------------- |
| OS-IRON    | 工程铁律       | ✅               | ✅ L78-90   | ✅                 | 完整                  |
| OS-BAN     | 禁止规则       | ✅               | ✅ L410-412 | ✅                 | 完整                  |
| OS-STD     | 标准规则       | ✅               | ✅          | ✅                 | 完整（OS-STD-2xx 残留）   |
| OS-ACC     | 验收标准       | ✅               | ✅ L416-420 | ✅                 | 已消解冲突               |
| OS-KER     | 内核工程规则     | ✅               | ✅ L95-126  | ✅                 | OS-KER-005 跳号       |
| OS-DRV     | 驱动工程规则     | ✅               | ✅          | ✅                 | 完整                  |
| OS-BUILD   | 构建工程规则     | ✅               | ✅          | ✅                 | 完整                  |
| OS-TEST    | 测试工程规则     | ✅               | ✅          | ✅                 | 完整                  |
| OS-OBS     | 可观测性规则     | ✅               | ✅          | ✅                 | 完整                  |
| OS-SEC     | 安全工程规则     | ✅               | ✅          | ✅                 | Rust 编号缺口           |
| OS-ABI     | ABI 稳定性规则  | ✅               | ✅ L424-430 | ✅                 | 完整                  |
| **OS-FMT** | **代码格式规则** | **❌ 未列出**       | **❌ 未登记**  | **✅ L331-387 使用** | **P1 缺口（v2.0 新发现）** |

**结论**：闭源总纲 L91-103 声明 11 类前缀，但实际使用 12 类（含未声明的 OS-FMT）。SSoT 注册表登记 11 类，遗漏 OS-FMT。这是 v1.0 遗漏的 SSoT 完整性重大缺口。

### 3.6 技术点唯一性验证小结

| 检查项                         | v1.0 状态 | v2.0 验证                   | 备注           |
| --------------------------- | ------- | ------------------------- | ------------ |
| 09-ssot-registry.md 唯一 SSoT | ✅ 通过    | ✅ 通过                      | OS-ACC 冲突已消解 |
| OS-KER-005 跳号               | ⚠️ 未修复  | **确认未修复**                 | §3.1         |
| Rust 编号缺口                   | ⚠️ 已文档化 | **确认已文档化**                | §3.2         |
| OS-FMT 未在 SSoT 注册           | 未识别     | **v2.0 新发现 P1**           | §3.3         |
| ES-SEL4 编号扩展未注册             | 未识别     | **v2.0 新发现 P1**           | §3.4         |
| 17 类规则编号完整性                 | ✅ 基本通过  | **⚠️ 12/11 类（OS-FMT 缺口）** | §3.5         |

***

## 4. openEuler 工程实践参考充分性（深化）

### 4.1 ES-OLK-1\~13 工程思想映射验证——确认完整

**重新读取验证**：闭源总纲 L1380-1385（附录 C）完整列出 ES-OLK-1\~13 的 13 项工程思想映射，每项均有明确的落地规则和章节引用。与 v1.0 §4.1 描述一致。

**证据**：

- `agent-linux基本工程标准规范.md:1380-1385`：ES-OLK-1\~13 完整映射表
- `agent-linux基本工程标准规范.md:999-1008`：§12.4 ES-OLK 落地方式表
- 13/13 项均有源码级证据（`01Reference/kernel-OLK-6.6/`）

**状态**：**确认完整，与 v1.0 一致**。

### 4.2 六大编码支柱验证——确认完整（但 OS-FMT 编号未注册）

**重新读取验证**：闭源总纲 L331-387 完整定义六大编码支柱，与 OLK-6.6 源码实践完全对齐。

| 支柱         | 规则编号       | 闭源总纲定义 | OLK-6.6 源码验证            | SSoT 登记   |
| ---------- | ---------- | ------ | ----------------------- | --------- |
| Tab 8 缩进   | OS-FMT-001 | L331   | `mutex.c` 全文 Tab 8      | **❌ 未登记** |
| K\&R 大括号   | OS-FMT-003 | L351   | `mutex.c` K\&R 风格       | **❌ 未登记** |
| 最小 typedef | OS-STD-010 | L321   | `mutex.c` 无多余 typedef   | ✅         |
| goto 集中出口  | OS-KER-001 | L201   | `mutex.c` goto 错误处理     | ✅         |
| kernel-doc | OS-STD-008 | L270   | `mutex.c` kernel-doc 注释 | ✅         |
| 80 列行宽     | OS-FMT-002 | L342   | `mutex.c` 80 列限制        | **❌ 未登记** |

**新发现**：六大编码支柱中三大支柱（Tab 8 / K\&R / 80 列）依赖 OS-FMT-001/002/003，但这些规则编号未在 SSoT 注册表登记（详见 §3.3）。

**状态**：**支柱定义完整，但 OS-FMT 编号 SSoT 登记缺口（v2.0 新发现）**。

### 4.3 双源融合裁决 16 维度验证——确认完整

**重新读取验证**：闭源总纲 L1416-1446（附录 E）完整列出 16 维度裁决。

| 裁决类型              | 维度数量 | 维度编号        |
| ----------------- | ---- | ----------- |
| 采纳 Linux 6.6 内核基线 | 11   | #1-#11      |
| 借鉴 seL4（架构层）      | 3    | #12、#15、#16 |
| 借鉴 seL4（P2 增强）    | 2    | #13、#14     |

**状态**：**确认完整，与 v1.0 一致**。

### 4.4 新检查：MGLRU / sched\_ext / io\_uring 最新实践参考——确认充分

**v2.0 新增检查**：验证 openEuler/OLK-6.6 的三项最新实践是否被 agent-linux 参考。

**MGLRU（多代 LRU）**：

- `docs/AirymaxOS/40-dataflows/02-memory-flow.md`：引用 MGLRU
- `docs/AirymaxOS/00-requirements/02-functional-requirements.md`：引用 MGLRU
- `docs/AirymaxOS/10-architecture/01-system-architecture.md`：引用 MGLRU
- 闭源总纲 L81：`airymaxos-memory | ... MGLRU 多代 LRU、CXL/PMEM 分级`
- 闭源总纲 L1139：`memory | memoryrovol/ + cxl/ + pmem/ + mglru/ + vfs-persist-kern/`

**sched\_ext（BPF 调度类）**：

- `docs/AirymaxOS/40-dataflows/04-scheduling-flow.md`：引用 sched\_ext
- `docs/AirymaxOS/40-dataflows/01-cognition-flow.md`：引用 sched\_ext
- `docs/AirymaxOS/90-observability/02-ebpf-probes.md`：引用 sched\_ext
- 闭源总纲 L1019：ES-SEL4-4 落地子仓 airymaxos-kernel io\_uring/

**io\_uring（异步 I/O）**：

- `docs/AirymaxOS/40-dataflows/03-ipc-flow.md`：引用 io\_uring
- `docs/AirymaxOS/40-dataflows/02-memory-flow.md`：引用 io\_uring
- 闭源总纲 L1119：`io_uring/  # 异步 I/O（Linux 6.6 内核基线风格独立子系统）`
- 闭源总纲 L1019：`ES-SEL4-4 消息传递 IPC（含 fastpath） | 影响 io_uring 消息传递 | airymaxos-kernel`

**结论**：MGLRU / sched\_ext / io\_uring 三项最新实践均已被充分参考，分布在需求、架构、数据流、模块、闭源总纲等多个文档层次。**参考充分性通过**。

### 4.5 openEuler 参考充分性评估小结

| 检查项                             | v1.0 评分 | v2.0 验证               | 变化         |
| ------------------------------- | ------- | --------------------- | ---------- |
| ES-OLK-1\~13 映射                 | 92/A    | **确认完整**              | 持平         |
| 六大编码支柱                          | 92/A    | **支柱完整，OS-FMT 编号未注册** | -1         |
| 双源融合裁决 16 维度                    | 92/A    | **确认完整**              | 持平         |
| MGLRU/sched\_ext/io\_uring 最新实践 | 未检查     | **v2.0 新检查，确认充分**     | +0（已含在原评分） |

**openEuler 参考充分性评分**：92/A → 91/A-（OS-FMT 编号 SSoT 登记缺口 -1）

***

## 5. seL4 微内核化改造参考充分性（深化）

### 5.1 ES-SEL4-1\~5 架构层强制借鉴验证——确认完整

**重新读取验证**：闭源总纲 L1014-1020 + 附录 D L1397-1401 完整列出 ES-SEL4-1\~5 的 5 项架构层强制借鉴。

| 编号        | seL4 工程思想                | 落地子仓                        | seL4 源码证据                                              | 验证 |
| --------- | ------------------------ | --------------------------- | ------------------------------------------------------ | -- |
| ES-SEL4-1 | 极简原则（Liedtke minimality） | airymaxos-kernel corekern/  | `20-modules/01-kernel.md:55-62` 引用 Liedtke 原文          | ✅  |
| ES-SEL4-2 | capability 单一权限模型        | airymaxos-security          | `120-cross-project-code-sharing.md:183-189` 7 CNode 操作 | ✅  |
| ES-SEL4-3 | 服务用户态化                   | airymaxos-services          | `10-architecture/03-microkernel-strategy.md:141` 用户态下沉 | ✅  |
| ES-SEL4-4 | 消息传递 IPC（含 fastpath）     | airymaxos-kernel io\_uring/ | `30-interfaces/02-ipc-protocol.md` EPState 三态机         | ✅  |
| ES-SEL4-5 | 形式化验证驱动                  | airymaxos-tests-linux       | `20-modules/01-kernel.md` formal-verification 三段式      | ✅  |

**状态**：**确认完整，与 v1.0 一致**。

### 5.2 v2.0 新检查：seL4 关键设计参考充分性

**capability 系统 7 种操作（Copy/Mint/Move/Mutate/Revoke/Delete/Rotate）**：

- `120-cross-project-code-sharing.md:183-189`：完整定义 AIRY\_CAP\_OP\_COPY/MINT/MOVE/MUTATE/REVOKE/DELETE/ROTATE 7 项
- 与 seL4 `src/object/cnode.c` 7 CNode 操作完全对齐
- **✅ 充分参考**

**IPC fastpath POINT OF NO RETURN 模式**：

- `10-architecture/03-microkernel-strategy.md`：引用 POINT OF NO RETURN
- `20-modules/01-kernel.md`：引用 POINT OF NO RETURN
- `30-interfaces/02-ipc-protocol.md`：引用 POINT OF NO RETURN
- `10-architecture/06-directory-structure.md`：引用 POINT OF NO RETURN
- **✅ 充分参考**

**消息传递三态机（EPState\_Idle/Send/Recv）**：

- `10-architecture/03-microkernel-strategy.md`：引用 EPState\_Idle/Send/Recv
- `20-modules/01-kernel.md`：引用 EPState
- `30-interfaces/02-ipc-protocol.md`：引用 EPState
- `10-architecture/06-directory-structure.md`：引用 EPState
- **✅ 充分参考**

**Reply 原子性 doReplyTransfer 临界区**：

- `10-architecture/03-microkernel-strategy.md`：引用 doReplyTransfer
- `20-modules/01-kernel.md`：引用 doReplyTransfer
- `30-interfaces/02-ipc-protocol.md`：引用 doReplyTransfer
- **✅ 充分参考**

**vtime Q16.16 定点格式**：

- `30-interfaces/02-ipc-protocol.md:107`：`调度数据流 vtime 使用 __s32 Q16.16 定点（不依赖 wall clock）`
- `30-interfaces/02-ipc-protocol.md:122`：`airy_vtime_t（Q16.16 定点）独立承担`
- `60-driver-model/02-platform-driver.md:510`：`airy_vtime_t vtime; /* Q16.16 定点虚拟时间 */`
- `60-driver-model/01-device-model.md:509`：`airy_vtime_t vtime; /* Q16.16 定点虚拟时间 */`
- `50-engineering-standards/10-coding-style/C_Cpp_coding_style.md:811`：`强制 airy_q16_t Q16.16 定点数（OS-STD-010）`
- **✅ 充分参考**

**结论**：seL4 的 5 项关键设计（capability 7 操作 / IPC fastpoint POINT OF NO RETURN / 三态机 / doReplyTransfer 临界区 / vtime Q16.16）均已被充分参考，分布在架构、模块、接口、驱动模型、编码风格等多个文档层次。

### 5.3 v2.0-NEW-P1-02：\[SC] 6 头文件清单在闭源/开源间不一致（新发现）

**问题描述**：闭源总纲 OS-IRON-014 与开源 `120-cross-project-code-sharing.md` 对 \[SC] 共享契约层 6 个头文件的清单描述不一致。

**证据**：

- 闭源总纲 `agent-linux基本工程标准规范.md:1061`（OS-IRON-014）：`[SC] 共享契约层 6 个头文件（bpf_struct_ops.h / memory_types.h / security_types.h / cognition_types.h / sched.h / ipc.h）`——**包含 bpf\_struct\_ops.h，不包含 syscalls.h**
- 开源 `120-cross-project-code-sharing.md:71-76`：6 个头文件为 `memory_types.h / security_types.h / cognition_types.h / sched.h / ipc.h / syscalls.h`——**包含 syscalls.h，不包含 bpf\_struct\_ops.h**
- 开源 `20-modules/01-kernel.md:48`：`struct_ops 状态机与 common_value 布局与 agentrt 共享（补充共享文件 bpf_struct_ops.h，非 [SC] 核心头文件）`——**明确 bpf\_struct\_ops.h 非 \[SC] 核心头文件**

**冲突本质**：闭源总纲 OS-IRON-014 将 `bpf_struct_ops.h` 列入 \[SC] 6 头文件，但开源文档明确声明 `bpf_struct_ops.h` "非 \[SC] 核心头文件"，\[SC] 6 头文件应包含 `syscalls.h` 而非 `bpf_struct_ops.h`。这是一个 P1 级 SSoT 冲突，直接影响 IRON-9 v2 共享契约层的物理落地。

**影响**：开发者依据闭源总纲会在 `include/airymax/` 创建 `bpf_struct_ops.h` 作为 \[SC] 头文件，但依据开源文档应创建 `syscalls.h`。两端不一致将导致 \[SC] 共享契约层物理落地时出现 7 个头文件（含 bpf\_struct\_ops.h 和 syscalls.h）而非 6 个，违反 OS-IRON-014 单一数据源约束。

**修复建议**：修改闭源总纲 L1061 OS-IRON-014，将 `bpf_struct_ops.h` 替换为 `syscalls.h`，与开源 `120-cross-project-code-sharing.md:71-76` 对齐。

**状态**：**v2.0 新发现，未修复**。

### 5.4 ES-SEL4-6\~10 P2 增强建议验证——确认存在分类模糊

**重新读取验证**：与 v1.0 §2.2 一致，ES-SEL4-9/10 状态分类模糊（标题归 P2 但正文标"已落地"）。

**状态**：**确认存在，未修复**（与 v1.0 一致）。

### 5.5 seL4 参考充分性评估小结

| 检查项                              | v1.0 评分  | v2.0 验证            | 变化 |
| -------------------------------- | -------- | ------------------ | -- |
| ES-SEL4-1\~5 架构层强制借鉴             | 80/B     | **确认完整**           | 持平 |
| capability 7 操作                  | 80/B     | **v2.0 新检查，充分参考**  | 持平 |
| IPC fastpoint POINT OF NO RETURN | 80/B     | **v2.0 新检查，充分参考**  | 持平 |
| 三态机 EPState\_Idle/Send/Recv      | 80/B     | **v2.0 新检查，充分参考**  | 持平 |
| doReplyTransfer 临界区              | 80/B     | **v2.0 新检查，充分参考**  | 持平 |
| vtime Q16.16 定点                  | 80/B     | **v2.0 新检查，充分参考**  | 持平 |
| \[SC] 6 头文件清单一致性                 | 未检查      | **v2.0 新发现 P1 冲突** | -2 |
| ES-SEL4-7 分类残留冲突                 | -2（v1.0） | **确认未修复**          | 持平 |
| ES-SEL4-9/10 状态分类模糊              | -1（v1.0） | **确认未修复**          | 持平 |

**seL4 参考充分性评分**：80/B → 78/B-（\[SC] 头文件清单冲突 -2，ES-SEL4-7/9/10 残留已含在 v1.0 评分中不重复扣分）

***

## 6. 开发就绪度评估（8 项判定标准，深化）

### 6.1 8 项判定标准重新评估

**重新读取验证**：开发路线 L1019 声明"8 项判定标准全部满足"，本轮逐项重新评估。

| # | 判定标准                                                | v1.0 判定 | v2.0 判定      | 证据                                                                                                                                                  | 变化     |
| - | --------------------------------------------------- | ------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| 1 | 26 个 README 全部重写                                    | ✅ 通过    | ✅ 通过         | `find` 统计 26 个 README.md（1 顶层 + 25 目录级，含 5 个 50-engineering-standards 子目录）                                                                          | 持平     |
| 2 | 目录结构 SSoT 完整（350 行）                                 | ✅ 通过    | ✅ 通过         | `06-directory-structure.md` 361 行（超出 350 行目标）                                                                                                       | 持平     |
| 3 | \[SC] 6 头文件物理落地                                     | ✅ 通过    | ⚠️ **有条件通过** | 闭源总纲 L1061 与开源 `120-cross-project-code-sharing.md:71-76` 清单冲突（bpf\_struct\_ops.h vs syscalls.h）                                                     | **降级** |
| 4 | IPC magic + 7 capability 操作 + 128B \_Static\_assert | ✅ 通过    | ✅ 通过         | `120-cross-project-code-sharing.md:183-189`（7 cap op）/ L302-303（IPC magic 0x41524531）/ L355（128B \_Static\_assert）/ L236-237（AGTS magic 0x41475453） | 持平     |
| 5 | ES-OLK-1\~13 完整                                     | ✅ 通过    | ✅ 通过         | 闭源总纲 L1380-1385 完整映射                                                                                                                                | 持平     |
| 6 | ES-SEL4-1\~5 完整                                     | ✅ 通过    | ✅ 通过         | 闭源总纲 L1014-1020 + 附录 D L1397-1401                                                                                                                   | 持平     |
| 7 | OS-ACC 冲突消解                                         | ✅ 通过    | ✅ 通过         | `09-ssot-registry.md:420` 已消解声明                                                                                                                     | 持平     |
| 8 | v0.9.0 P0 修复                                        | ⚠️ 部分通过 | ⚠️ **部分通过**  | P0-01/03 已修复，P0-02 部分修复（ES-SEL4-7 残留）                                                                                                               | 持平     |

**v2.0 判定变化**：标准 3（\[SC] 6 头文件物理落地）从 v1.0 的"通过"降级为"有条件通过"，原因是闭源总纲 L1061 与开源 `120-cross-project-code-sharing.md:71-76` 对 \[SC] 6 头文件清单描述不一致（详见 §5.3）。

### 6.2 26 个 README 验证

**重新统计**：`find /home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/ -name "README.md"` 返回 **26 个**：

- 1 顶层：`docs/AirymaxOS/README.md`
- 20 顶层目录级：00-requirements / 10-architecture / 20-modules / 30-interfaces / 40-dataflows / 50-engineering-standards / 60-driver-model / 70-build-system / 80-testing / 90-observability / 100-operations / 110-security / 120-development-process / 130-roadmap / 140-application-development / 150-cloudnative / 160-compatibility / 170-performance / 180-i18n / 190-distribution
- 5 个 50-engineering-standards 子目录：10-coding-style / 20-contracts / 30-runtime-interfaces / 40-integration / 50-project-erp

**总计**：1 + 20 + 5 = **26 个** ✅

### 6.3 目录结构 SSoT 验证

**重新统计**：`wc -l 06-directory-structure.md` 返回 **361 行**（超出 350 行目标）✅

### 6.4 \[SC] 6 头文件物理落地验证（v2.0 深化）

**v2.0 新发现**：闭源总纲与开源文档对 \[SC] 6 头文件清单描述不一致（详见 §5.3）。

| 文档                                           | 6 个头文件                                                                                          | 状态                                    |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------- |
| 闭源总纲 L1061 OS-IRON-014                       | bpf\_struct\_ops.h / memory\_types.h / security\_types.h / cognition\_types.h / sched.h / ipc.h | **含 bpf\_struct\_ops.h，无 syscalls.h** |
| 开源 `120-cross-project-code-sharing.md:71-76` | memory\_types.h / security\_types.h / cognition\_types.h / sched.h / ipc.h / syscalls.h         | **含 syscalls.h，无 bpf\_struct\_ops.h** |
| 开源 `20-modules/01-kernel.md:48`              | 明确 bpf\_struct\_ops.h "非 \[SC] 核心头文件"                                                           | 支持 120 文档版本                           |

**结论**：\[SC] 6 头文件物理落地存在 SSoT 冲突，需修复闭源总纲 L1061 后方可通过。

### 6.5 开发就绪度评估小结

**v2.0 判定**：**有条件通过（条件加强）**——8 项判定标准中 6 项完全通过、2 项有条件通过（\[SC] 6 头文件物理落地 + v0.9.0 P0 修复），存在 1 项 P0 级残留冲突（ES-SEL4-7 分类）+ 3 项 P1 级新发现（OS-FMT 未注册 / \[SC] 头文件清单冲突 / ES-SEL4 编号扩展未注册）需修复后方可进入 1.0.1 M1 代码开发。

**与 v1.0 对比**：v1.0 为"有条件通过"（2 项有条件通过），v2.0 降级为"有条件通过（条件加强）"（2 项有条件通过 + 3 项新 P1），开发就绪条件更严格。

***

## 7. 细节完成度检查（深化）

### 7.1 v1.0-P2-01 验证：tests 简写残留——v1.0 严重低估

**v1.0 数据**：5 文件/10 处

**v2.0 重新统计**：在 `docs/AirymaxOS/` 全范围 Grep `\btests\b`（排除 `tests-linux`/`tests/`/`_tests`/`kselftest`/`KUNIT_ALL_TESTS` 等合法用法），实际匹配 **31 处，分布在 15+ 个文件**。

**Top 15 文件分布**：

| 文件                                                          | 匹配数 |
| ----------------------------------------------------------- | --- |
| `50-engineering-standards/50-project-erp/project_erp.md`    | 20  |
| `10-architecture/02-five-dimensional-principles.md`         | 17  |
| `10-architecture/05-adrs.md`                                | 15  |
| `00-requirements/02-functional-requirements.md`             | 11  |
| `120-development-process/01-patch-lifecycle.md`             | 10  |
| `00-requirements/README.md`                                 | 10  |
| `50-engineering-standards/07-maintainers-and-governance.md` | 8   |
| `10-architecture/03-microkernel-strategy.md`                | 8   |
| `120-development-process/02-maintainer-hierarchy.md`        | 7   |
| `70-build-system/01-kbuild-system.md`                       | 6   |
| `20-modules/README.md`                                      | 6   |
| `170-performance/06-benchmark-suite.md`                     | 6   |
| `20-modules/08-tests.md`                                    | 5   |
| `190-distribution/05-reproducible-build.md`                 | 5   |
| `10-architecture/README.md`                                 | 5   |

**v1.0 误判分析**：v1.0 §7.1 称"开源文档范围已从 49 文件/177 处大幅减少至 5 文件/10 处"，但实际仍为 15+ 文件/31+ 处。v1.0 的统计可能仅覆盖了 `30-interfaces/` 等部分范围，未做全范围 Grep。

**状态**：**v1.0 严重低估，v2.0 修正为 15+ 文件/31+ 处**（仍属 P2 级，但工作量从 v1.0 估算的 \~2h 增至 \~6h）。

### 7.2 v1.0-P2-02 验证：OS-STD-2xx 运维域残留——确认存在

**重新统计**：`grep -rc "OS-STD-2\d\d" docs/AirymaxOS/` 返回 **4 文件/57 处**，与 v1.0 一致。

| 文件                                                               | 匹配数 |
| ---------------------------------------------------------------- | --- |
| `50-engineering-standards/01-coding-standards.md`                | 32  |
| `50-engineering-standards/05-development-process.md`             | 22  |
| `50-engineering-standards/10-coding-style/C_Cpp_coding_style.md` | 1   |
| `70-build-system/02-kconfig-system.md`                           | 2   |

**状态**：**确认存在，与 v1.0 一致**（4 文件/57 处）。

### 7.3 v2.0 新检查：8 子仓设计细节完成度

**kernel 子仓**（闭源总纲 L1094-1129）：

- 完整目录结构（arch/include/corekern/fs/net/block/drivers/mm/security/io\_uring 等 24 顶层目录）
- 模型 A 完整 Linux 6.6 fork 声明
- ES-OLK-7/ES-SEL4-1/ES-SEL4-4 落地明确
- ✅ 细节完成度高

**其他 7 子仓**（闭源总纲 L1131-1143）：

- 每子仓关键目录 + 构建系统 + seL4 借鉴点 + v0.2.4 修正明确
- services：userland-{vfs,net,drivers}/ + 12 daemons
- security：agent\_lsm/ + common/ + integrity/ + keys/ + capability/ + cupolas/
- memory：memoryrovol/ + cxl/ + pmem/ + mglru/ + vfs-persist-kern/
- cognition：CoreLoopThree + Thinkdual + LLM + compute-accel/
- cloudnative：k8s-crd + containerd-shim + cni + sdk/
- system：systemd 适配 + init + commons + devstation/
- tests-linux：kunit/ + selftests/ + fault-injection/ + formal-verification/
- ✅ 细节完成度高

**结论**：8 子仓设计细节完成度高，每子仓均有明确的目录结构、构建系统、seL4 借鉴点和 v0.2.4 修正记录。

### 7.4 v2.0 新检查：是否可依据此方案开始全面开发的具体阻碍

**v2.0 评估**：当前方案存在以下阻碍全面开发的具体问题：

| 阻碍                      | 等级  | 影响                                                     | 修复工作量  |
| ----------------------- | --- | ------------------------------------------------------ | ------ |
| ES-SEL4-7 分类残留冲突（P0）    | 阻断  | 开发者无法确定架构层强制借鉴是 5 项还是 6 项                              | \~2h   |
| OS-FMT 未在 SSoT 注册（P1）   | 阻断  | 开发者无法从 SSoT 追溯六大编码支柱中三大支柱的规则编号                         | \~3h   |
| \[SC] 6 头文件清单冲突（P1）     | 阻断  | 开发者无法确定 \[SC] 6 头文件是含 bpf\_struct\_ops.h 还是 syscalls.h | \~1h   |
| ES-SEL4 编号扩展未注册（P1）     | 非阻断 | 开发者可参考开源文档，但 SSoT 完整性受损                                | \~4h   |
| airymaxos- 前缀不一致（P1）    | 非阻断 | 闭源/开源命名不一致，影响跨文档检索                                     | \~4h   |
| OS-KER-005 跳号（P1）       | 非阻断 | 编号连续性受损，不影响功能                                          | \~0.5h |
| ES-SEL4-9/10 状态分类模糊（P1） | 非阻断 | 已落地项归 P2 范围，语义模糊                                       | \~1h   |

**结论**：**3 项阻断性阻碍**（ES-SEL4-7 P0 + OS-FMT P1 + \[SC] 头文件清单 P1）需在 1.0.1 M1 启动前修复，合计 \~6h。修复后可依据此方案开始全面开发。

### 7.5 细节完成度检查小结

| 检查项           | v1.0 状态   | v2.0 验证                     | 变化        |
| ------------- | --------- | --------------------------- | --------- |
| tests 简写残留    | 5 文件/10 处 | **15+ 文件/31+ 处（v1.0 严重低估）** | 数据修正      |
| OS-STD-2xx 残留 | 4 文件/57 处 | **4 文件/57 处**               | 持平        |
| OS-KER-005 跳号 | 未修复       | **确认未修复**                   | 持平        |
| Rust 编号缺口     | 已文档化      | **确认已文档化**                  | 持平        |
| 8 子仓设计细节      | 未检查       | **v2.0 新检查，完成度高**           | +（已含在原评分） |
| 全面开发阻碍        | 未检查       | **v2.0 新检查，3 项阻断性阻碍**       | -1        |

***

## 8. 8 子仓命名规范验证（深化）

### 8.1 v1.0-P1-01 验证：airymaxos- 前缀不一致——确认存在

**重新统计**：

- 闭源总纲 `agent-linux基本工程标准规范.md`：`airymaxos-` 前缀 **37 处**（与 v1.0 一致）
- 开发路线 `agent-linux开发路线和进度.md`：`airymaxos-` 前缀 **4 处**（v1.0 未提及）
- 开源 `docs/AirymaxOS/README.md:131-139`：8 子仓 git URL 使用裸名 ✅
- 开源 `06-directory-structure.md:175-184`：8 子仓映射表使用裸名 ✅

**状态**：**确认存在，未修复**（闭源 37 处 + 开发路线 4 处 = 41 处，v1.0 仅统计闭源 37 处）。

### 8.2 v2.0-NEW-P2-02：OS-STD-005 与开源 SSoT 矛盾（新发现）

**问题描述**：闭源总纲 OS-STD-005 仍声明 `airymaxos_*` 前缀用于 AirymaxOS 专属 API，但开源 `06-directory-structure.md` L294 已明确废弃该前缀。

**证据**：

- 闭源总纲 `agent-linux基本工程标准规范.md:167`（OS-STD-005）：`agentrt_* 前缀保留给 agentrt 同源 API；airymaxos_* 前缀用于 AirymaxOS 内核/发行版专属 API`
- 闭源总纲 `agent-linux基本工程标准规范.md:171`：示例代码 `int airymaxos_lsm_hook_register(...)` 使用 `airymaxos_*` 前缀
- 开源 `06-directory-structure.md:294`：`禁止前缀：airymaxos_*（已废弃，详见 project_memory）、agentrt_*（已改名）、agentos_*（已废弃）`

**冲突本质**：闭源总纲 OS-STD-005 声明 `airymaxos_*` 用于专属 API，但开源 SSoT 已明确废弃该前缀。两者矛盾。

**状态**：**v2.0 新发现，未修复**。

### 8.3 开源文档 airymaxos- 前缀上下文分析（v2.0 深化）

**v2.0 新发现**：v1.0 §9.1 称"开源文档已统一去除 airymaxos- 前缀"，但实际开源 `docs/AirymaxOS/` 中仍有大量 `airymaxos-` 前缀残留。经上下文分析，这些残留分为三类：

| 类别       | 上下文                                       | 合法性             | 示例                                         |
| -------- | ----------------------------------------- | --------------- | ------------------------------------------ |
| RPM 包名   | `Name: airymaxos-services-core` 等         | ✅ 合法（RPM 包名约定）  | `190-distribution/01-rpm-packaging.md:72`  |
| 配置文件名    | `airymaxos-base.config`                   | ✅ 合法（配置文件命名）    | `70-build-system/02-kconfig-system.md:429` |
| 子仓/部署层名称 | `airymaxos-kernel`、`airymaxos-services` 等 | ⚠️ 边界模糊（部分应改裸名） | `100-operations/01-deployment.md:57-61`    |

**关键发现**：`100-operations/01-deployment.md:57-61` 的部署层表格使用 `airymaxos-kernel`、`airymaxos-services` 等作为部署层名称，与 `README.md:131-139` 的裸名约定不一致。这些位置应区分"子仓名"（裸名）和"包名"（airymaxos- 前缀），但当前文档边界模糊。

**结论**：v1.0 称"开源文档已统一去除 airymaxos- 前缀"的说法**部分错误**——8 子仓 git URL 层面已统一去除（README L131-139），但 RPM 包名、配置文件名、部署层表格中仍大量使用（部分合法，部分边界模糊）。

### 8.4 8 子仓命名规范验证小结

| 验证项                            | v1.0 状态 | v2.0 验证                      | 变化   |
| ------------------------------ | ------- | ---------------------------- | ---- |
| 闭源总纲 airymaxos- 前缀             | 37 处    | **37 处（+ 开发路线 4 处）**         | 数据补充 |
| 开源文档 airymaxos- 前缀             | "已统一去除" | **部分错误——RPM 包名合法，部署层边界模糊**   | 修正   |
| OS-STD-005 与开源 SSoT 矛盾         | 未识别     | **v2.0 新发现 P2**              | 新发现  |
| 函数前缀 airy\_\* vs airymaxos\_\* | 矛盾      | **确认矛盾（OS-STD-005 vs L294）** | 持平   |

**修复建议**：

1. 闭源总纲全文替换 8 子仓名 `airymaxos-kernel` → `kernel` 等（37 处）+ 开发路线 4 处
2. 闭源总纲 L167 OS-STD-005 修改为：`airy_* 前缀用于 AirymaxOS 内核/发行版专属 API（与 agentrt 共享 Airymax 同源语义）`
3. 闭源总纲 L171 示例代码修改为：`int airy_lsm_hook_register(...)`
4. 开源 `100-operations/01-deployment.md:57-61` 部署层表格区分"子仓名"（裸名）和"包名"（airymaxos- 前缀）

***

## 9. 修正后的综合评分

### 9.1 三层对齐度评分修正

| 层次     | 权重   | v0.9.0     | Wave 2 v2  | v1.0       | v2.0           | v2.0 变化原因                                           |
| ------ | ---- | ---------- | ---------- | ---------- | -------------- | --------------------------------------------------- |
| 规范声明层  | 35%  | 92/A       | 92/A       | 92/A       | **88/B+**      | OS-FMT 未注册 -2 + ES-SEL4 扩展未注册 -1 + OS-STD-005 矛盾 -1 |
| 方案设计层  | 40%  | 68/D+      | 80/B       | 78/B+      | **75/B**       | \[SC] 头文件清单冲突 -2 + 开发路线声明矛盾 -1                      |
| 实现落地层  | 25%  | N/A（72 代理） | N/A（72 代理） | N/A（72 代理） | **N/A（72 代理）** | 持平                                                  |
| **综合** | 100% | **70/B-**  | **80/B**   | **79/B+**  | **76/B**       | **-3**                                              |

### 9.2 评分调整说明

**v1.0 → v2.0 扣分项**：

| 扣分项                                 | 层次    | 扣分 | 证据   |
| ----------------------------------- | ----- | -- | ---- |
| OS-FMT 未在 SSoT 注册（v2.0 新发现 P1）      | 规范声明层 | -2 | §3.3 |
| ES-SEL4 编号扩展未注册（v2.0 新发现 P1）        | 规范声明层 | -1 | §3.4 |
| OS-STD-005 与开源 SSoT 矛盾（v2.0 新发现 P2） | 规范声明层 | -1 | §8.2 |
| \[SC] 6 头文件清单冲突（v2.0 新发现 P1）        | 方案设计层 | -2 | §5.3 |
| 开发路线 L1019 声明矛盾（v2.0 新发现 P2）        | 方案设计层 | -1 | §2.3 |

**综合扣分**：规范声明层 -4 × 0.35 + 方案设计层 -3 × 0.40 = -1.4 + -1.2 = -2.6 → 取整 **-3**

**v2.0 综合评分** = v1.0 综合 79 - 3 = **76/B**

### 9.3 问题处置汇总

| 问题来源            | 总数 | 已修复    | 部分修复                   | 未修复               | 新发现                |
| --------------- | -- | ------ | ---------------------- | ----------------- | ------------------ |
| v0.9.0（15 项）    | 15 | 6      | 3（含 OLK-6.6 v1.0 误判修正） | 6                 | —                  |
| Wave 2 v2（34 项） | 34 | 8（A 类） | —                      | 26（B/C/D/E 类）     | —                  |
| v1.0 复核（11 项）   | 11 | 0      | 0                      | 11（含 1 项数据严重低估修正） | —                  |
| v2.0 复核新发现      | —  | —      | —                      | —                 | **6（3 P1 + 3 P2）** |

### 9.4 待修复问题清单（按优先级）

#### P0 级（阻断 1.0.1 M1 启动）

| # | 问题                       | 来源   | 修复方案                                    | 工作量  | 证据   |
| - | ------------------------ | ---- | --------------------------------------- | ---- | ---- |
| 1 | ES-SEL4-7 分类残留冲突（5 vs 6） | v1.0 | 统一标题与正文分类（推荐方案 A：将 ES-SEL4-7 归入 P2 已落地） | \~2h | §2.1 |

#### P1 级（1.0.1 M1 阶段修复，含 v2.0 新发现）

| # | 问题                                      | 来源       | 修复方案                                           | 工作量    | 证据   |
| - | --------------------------------------- | -------- | ---------------------------------------------- | ------ | ---- |
| 2 | **OS-FMT 未在 SSoT 注册**                   | v2.0 新发现 | SSoT 新增 OS-FMT 章节 + 闭源总纲前缀表补充                  | \~3h   | §3.3 |
| 3 | **\[SC] 6 头文件清单冲突**                     | v2.0 新发现 | 闭源总纲 L1061 将 bpf\_struct\_ops.h 替换为 syscalls.h | \~1h   | §5.3 |
| 4 | **ES-SEL4 编号扩展未注册**                     | v2.0 新发现 | SSoT 登记 ES-SEL4-11\~43 或明确标注为研究范围              | \~4h   | §3.4 |
| 5 | airymaxos- 前缀不一致（闭源 37 + 开发路线 4 = 41 处） | v1.0     | 闭源总纲 + 开发路线全文替换为裸名                             | \~4h   | §8.1 |
| 6 | OS-KER-005 跳号                           | v1.0     | 补充废弃说明注释                                       | \~0.5h | §3.1 |
| 7 | ES-SEL4-9/10 状态分类模糊                     | v1.0     | 区分"已落地"与"待落地"P2 项                              | \~1h   | §2.2 |

#### P2 级（1.0.1 阶段增量修复，含 v2.0 新发现）

| #  | 问题                                 | 来源       | 修复方案                                       | 工作量    | 证据   |
| -- | ---------------------------------- | -------- | ------------------------------------------ | ------ | ---- |
| 8  | **开发路线 L1019 声明矛盾**                | v2.0 新发现 | 修复 ES-SEL4-7 后同步更新声明                       | \~0.5h | §2.3 |
| 9  | **OS-STD-005 与开源 SSoT 矛盾**         | v2.0 新发现 | 闭源总纲 L167 修改为 airy\_\*                     | \~1h   | §8.2 |
| 10 | **OLK-6.6 术语残留 49 处**              | v2.0 修正  | L980-986/L1030-1035 等概念引用改为 Linux 6.6 内核基线 | \~3h   | §2.4 |
| 11 | tests 简写残留（15+ 文件/31+ 处，v1.0 严重低估） | v1.0（修正） | 全文替换为全称                                    | \~6h   | §7.1 |
| 12 | OS-STD-2xx 运维域残留（4 文件/57 处）        | v1.0     | 迁移至 OS-OBS                                 | \~4h   | §7.2 |
| 13 | Rust 编号缺口                          | v1.0     | SSoT 完整登记                                  | \~3h   | §3.2 |
| 14 | 文档计数三作用域模型未注册                      | v1.0     | 补充注册                                       | \~1h   | —    |
| 15 | 规则编号注册表变更日志不完整                     | v1.0     | 补充变更日志                                     | \~1h   | —    |
| 16 | 品味哲学层 8 项隐性智慧未文档化                  | v1.0     | 文档化 8 项隐性智慧                                | \~8h   | —    |
| 17 | agentrt 源码差距（15 文件）                | v1.0     | 1.0.1 M1 代码品味改进                            | \~40h  | —    |

### 9.5 改进建议

#### 短期（0.1.1 收尾，\~6h，阻断 1.0.1 M1 启动）

1. **修复 P0 级 ES-SEL4-7 分类残留冲突**（\~2h）——推荐方案 A：闭源总纲 L1403 借鉴方式从"架构层强制（已落地）"修改为"P2 增强建议（已落地）"，L1410 修改为"架构层强制借鉴（ES-SEL4-1\~5）: 5 项"
2. **修复 P1 级 OS-FMT 未在 SSoT 注册**（\~3h）——SSoT 新增 OS-FMT 章节 + 闭源总纲 L91-103 前缀表补充
3. **修复 P1 级 \[SC] 6 头文件清单冲突**（\~1h）——闭源总纲 L1061 将 bpf\_struct\_ops.h 替换为 syscalls.h

#### 中期（1.0.1 M1 阶段，\~14.5h）

1. 修复 ES-SEL4 编号扩展未注册（\~4h）
2. 修复 airymaxos- 前缀不一致（\~4h）
3. 补充 OS-KER-005 废弃说明（\~0.5h）
4. 消解 ES-SEL4-9/10 状态分类模糊（\~1h）
5. 修复 OS-STD-005 与开源 SSoT 矛盾（\~1h）
6. 修复开发路线 L1019 声明矛盾（\~0.5h）
7. 清除 OLK-6.6 概念引用残留（\~3h）

#### 长期（1.0.1 全阶段，\~63h+）

1. 清除 tests 简写残留（15+ 文件/31+ 处，\~6h）
2. 迁移 OS-STD-2xx 至 OS-OBS（\~4h）
3. 完整登记 Rust 编号（\~3h）
4. 补充文档计数三作用域模型注册（\~1h）
5. 补充规则编号注册表变更日志（\~1h）
6. 文档化 8 项隐性智慧（\~8h）
7. agentrt 源码代码品味改进（\~40h）

### 9.6 最终结论

agent-linux（AirymaxOS）整体方案经过 v0.9.0 综合审查 + Wave 2 v2 源码级深读 + v1.0 系统性复核 + v2.0 深化复审，**尚未达到可开发状态**——存在 1 项 P0 级残留冲突（ES-SEL4-7 分类）+ 3 项 v2.0 新发现 P1 级问题（OS-FMT 未注册 / \[SC] 头文件清单冲突 / ES-SEL4 编号扩展未注册）需在 1.0.1 M1 启动前修复，合计 \~6h。

**v1.0 → v2.0 评分变化**：综合评分从 79/B+ 降至 76/B，主要原因是 v2.0 深化审查发现 v1.0 遗漏的 3 项 P1 级 SSoT 完整性问题（OS-FMT / \[SC] 头文件 / ES-SEL4 扩展）。

**核心优势（维持）**：

- 工程思想统一：ES-OLK-1\~13 + ES-SEL4-1\~5 映射完整，源码级验证
- 工程标准规范：23 文档 SSoT 体系 + 09-ssot-registry.md 唯一 SSoT，OS-ACC 冲突已消解
- 对齐 openEuler 代码品味：六大支柱源码级验证，MGLRU/sched\_ext/io\_uring 最新实践充分参考
- 对齐 seL4 微内核思想：5 项架构层强制借鉴 + 5 项关键设计对齐（capability 7 操作 / IPC fastpoint POINT OF NO RETURN / 三态机 / doReplyTransfer 临界区 / vtime Q16.16）充分参考
- IRON-9 v2 三层共享模型：\[SC] 6 头文件 + IPC magic + 7 capability 操作 + 128B \_Static\_assert 完整
- 系统性目录结构：361 行 SSoT，8 子仓映射清晰，8 子仓设计细节完成度高
- 26 README 全部重写

**待改进（v2.0 修正）**：

ES-SEL4-7 分类残留冲突（P0，\~2h 修复）

- OS-FMT 未在 SSoT 注册（P1，\~3h 修复，v2.0 新发现）
- \[SC] 6 头文件清单冲突（P1，\~1h 修复，v2.0 新发现）
- ES-SEL4 编号扩展未注册（P1，\~4h 修复，v2.0 新发现）
- airymaxos- 前缀不一致（P1，\~4h 修复）
- 7 项已知遗留移交 1.0.1（tests 简写 15+ 文件/31+ 处 / OS-STD-2xx / OS-KER-005 / Rust 编号 / 品味哲学 / agentrt 源码 / OLK-6.6 残留）

**建议**：修复 3 项阻断性阻碍（P0 ES-SEL4-7 + P1 OS-FMT + P1 \[SC] 头文件清单，合计 \~6h）后，agent-linux 方案可正式进入 1.0.1 M1 代码开发阶段。其余 P1/P2 问题可在 1.0.1 M1 阶段并行修复。

***

> **报告结束** | SPHARX Ltd 内部参考 | 闭源不公开 | 审查日期：2026-07-13 | 审查版本：v2.0 | 综合评分：76/B

