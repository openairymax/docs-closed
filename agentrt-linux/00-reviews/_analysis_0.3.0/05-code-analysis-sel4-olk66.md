Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# C-2.5 seL4 + OLK-6.6 源码深度代码分析报告

> **文档定位**: 基于对 `01Reference/seL4-master`（seL4 微内核）与 `01Reference/kernel-OLK-6.6`（Linux 6.6 LTS / openEuler 参考实现）两个参考代码库的穷尽式深度源码阅读，为 agent-linux 微内核化改造提供"源码级"工程思想证据与融合裁决依据。本报告是 v0.2.1 研究报告（`00-reviews/_research_0.2.1/01` + `02`）的扩展与深化，不重复既有结论，而是为每一条工程思想补充具体源码位置引用与代码片段证据，并补充 v0.2.1 遗漏的工程机制。
> **报告版本**: 0.3.0（深度代码分析报告）
> **最后更新**: 2026-07-09
> **分析范围**: seL4-master 全量源码（src/ 13 子目录 + include/ 15 子目录 + libsel4/ + tools/ + manual/）+ OLK-6.6 全量源码（28 顶层目录 + scripts/ + Documentation/）
> **方法论**: 穷尽式源码阅读 + 证据引用（文件:行号 + 代码片段）+ 横向三栏对比 + 设计哲学裁决
> **机密级别**: 闭源不公开

---

## 目录

- [0. 摘要](#0-摘要)
- [1. 研究范围与方法](#1-研究范围与方法)
- [2. OLK-6.6 工程思想深度提炼（ES-OLK-1~13 扩展）](#2-olk66-工程思想深度提炼es-olk-113-扩展)
- [3. seL4 工程思想深度提炼（ES-SEL4-1~10 扩展）](#3-sel4-工程思想深度提炼es-sel4-110-扩展)
- [4. 关键子系统横向对比（三栏对照表）](#4-关键子系统横向对比三栏对照表)
- [5. 设计哲学对比与融合裁决](#5-设计哲学对比与融合裁决)
- [6. 可落地的工程标准条目（新增/强化建议）](#6-可落地的工程标准条目新增强化建议)
- [7. 与 v0.2.1 再检查结论的一致性](#7-与-v021-再检查结论的一致性)
- [8. 结论与后续工作建议](#8-结论与后续工作建议)
- [9. 附录：关键源码位置索引](#9-附录关键源码位置索引)

---

## 0. 摘要

本报告基于对 seL4-master 与 kernel-OLK-6.6 两个参考代码库的穷尽式深度阅读，对 v0.2.1 研究报告已提炼的 **ES-OLK-1~13**（13 项 OLK-6.6 工程思想）与 **ES-SEL4-1~10**（10 项 seL4 工程思想）进行"源码级证据强化"，为每一条思想补充**具体源码位置引用**（`文件:行号` 或 `文件:函数名`）与**代码片段摘要**作为证据。

**关键发现**（详见第 2-5 章）：

1. **EEVDF 调度器**（OLK-6.6 `kernel/sched/fair.c`）以 `avg_vruntime()`（fair.c:925）、`entity_eligible()`（fair.c:1057）、`pick_eevdf()`（fair.c:1252）三函数实现 O(log n) 增强红黑树选择，是 Linux 6.6 替代 CFS 的核心算法——agent-linux 调度子系统应完整保留并据此设计微内核化后的调度策略接口。

2. **seL4 fastpath**（`src/fastpath/fastpath.c:26`）通过 `fastpath_call()` 将最常见的 Call/ReplyRecv IPC 路径从通用 slowpath 中剥离，以 `unlikely()` 早期降级——这是 agent-linux io_uring 消息传递机制可借鉴的"热路径优化"范式。

3. **seL4 capability 派生模型**（`src/object/cnode.c:80/126/146` 调用 `deriveCap()`、`src/object/cnode.c:528` `cteRevoke()`、`:552` `cteDelete()`）通过 Copy/Mint/Move/Mutate/Revoke/Delete 六操作构建权限派生树——agent-linux security 子仓的 capability 设计应以此为蓝本。

4. **OLK-6.6 KABI 宏机制**（`include/linux/kabi.h`、`lib/Kconfig.kabi`）通过 `KABI_EXTEND`/`KABI_BROKEN_INSERT_ENUM`/`KABI_USE` 在不破坏二进制兼容性的前提下演进内核数据结构——这是 v0.2.1 未充分展开的工程思想，对 agent-linux 的"内核态 ABI 演进"具有直接参考价值。

5. **seL4 bitfield codegen + Isabelle/HOL 证明**（`tools/bitfield_gen.py:14` 注释明确"generating bitfield structures with get/set/new methods including Isabelle/HOL specifications and correctness proofs"）——这是形式化验证驱动工程思想的代码级证据，agent-linux 的 [SC] 共享契约层位域定义可借鉴此 codegen 思路。

6. **OLK-6.6 sparse + W=1/2/3/e 分级警告**（`Makefile:111-119`、`scripts/Makefile.extrawarn`）+ **checkpatch.pl 72 条规则**——构成"规范可执行"的完整工具链，agent-linux 应完整继承。

7. **设计哲学融合裁决**：Linux "演化式增量改进"（28 顶层目录 + Kconfig 可配置 + KABI 兼容）vs seL4 "形式化验证驱动极简"（8700 行核心 + capability 单一模型 + fastpath）——agent-linux 取"Linux 6.6 为基、seL4 为鉴"取向，编码风格层完全采纳 OLK-6.6，架构层选择性借鉴 seL4。

8. **新增 2 项工程思想**（v0.2.1 遗漏）：ES-OLK-14（KABI 二进制兼容演进机制）、ES-SEL4-11（CI 多工具矩阵验证），建议纳入工程标准。

本报告为 agent-linux 的工程标准体系（`50-engineering-standards/`）提供了源码级证据基础，并提出 6 项可落地工程标准条目（详见第 6 章）。

---

## 1. 研究范围与方法

### 1.1 参考代码库版本

| 代码库 | 路径 | 版本 | 规模 | 用途 |
|--------|------|------|------|------|
| seL4-master | `01Reference/seL4-master` | master 分支（VERSION 文件） | src/ 13 子目录 / include/ 15 子目录 / libsel4/ / tools/ / manual/ | 微内核设计思想唯一来源（ADR-014） |
| kernel-OLK-6.6 | `01Reference/kernel-OLK-6.6` | Linux 6.6 LTS（Makefile:5-7 `VERSION=6 PATCHLEVEL=6 SUBLEVEL=0`） | 28 顶层目录 / 24218 行 MAINTAINERS / 1271 行 coding-style.rst | 工程基线（Linux 6.6 LTS / openEuler 参考实现） |

**OLK-6.6 相对原生 Linux 6.6 的增量**（openEuler 特有）：`kernel/sched/{ext.c,bpf_sched.c,smt_qos.c,soft_domain.c,grid/}`（调度增强）、`mm/{gmem.c,gmem_phys.c,etmem.c,dynamic_pool.c}`（内存增强）、`include/linux/kabi.h` + `lib/Kconfig.kabi`（KABI 兼容机制）、`lib/Kconfig.openeuler`（openEuler 特有配置项如 `KWORKER_NUMA_AFFINITY`）。

### 1.2 研究方法（穷尽式阅读 + 证据引用 + 横向对比）

本研究采用"穷尽式源码阅读 + 证据引用 + 横向三栏对比 + 设计哲学裁决"四步法：

| 步骤 | seL4 | OLK-6.6 |
|------|------|---------|
| 目录测绘 | src/{api,kernel,object,fastpath,arch,machine,plat,smp,model,benchmark,drivers} + include/ + libsel4/ + tools/ + manual/ | 28 顶层目录 + kernel/sched/（48 文件）+ mm/（含 gmem/etmem）+ security/{selinux,landlock,apparmor,...} + io_uring/（52 文件）+ scripts/ + Documentation/ |
| 关键文件精读 | syscall.c（662 行）/ boot.c（41KB）/ tcb.c（69KB）/ cnode.c（27KB）/ endpoint.c（18KB）/ fastpath.c（31KB）/ bitfield_gen.py（123KB）/ syscall.xml | fair.c（EEVDF）/ fork.c / vmscan.c（MGLRU）/ commoncap.c / selinux/hooks.c（215 LSM hooks）/ io_uring.c（4752 行）/ checkpatch.pl / coding-style.rst / kabi.h |
| 证据引用 | 每条 ES 补充 `文件:行号` + 代码片段 | 同左 |
| 横向对比 | 7 个子系统三栏对照表（seL4 / OLK-6.6 / agent-linux） | 同左 |

### 1.3 与 v0.2.1 研究的关系（扩展而非重复）

v0.2.1 研究报告（`00-reviews/_research_0.2.1/01-source-code-engineering-study.md`）已提炼 ES-OLK-1~13 + ES-SEL4-1~10 共 23 项工程思想，并给出 16 维度融合裁决。v0.2.1 的方法论是"目录测绘 + 代表性源文件精读（coding-style.rst 1-700 行 / tcb.c 1-120 行）"，证据深度有限。

**本报告的扩展点**：

1. **证据强化**：为每一条 ES-* 思想补充**具体源码位置引用**（`文件:行号` 或 `文件:函数名`）与**代码片段摘要**，将 v0.2.1 的"模式归纳"升级为"源码级证据"。
2. **遗漏补充**：补充 v0.2.1 未展开的工程机制——OLK-6.6 的 `sparse`/`smatch`/`W=1` 分级警告、`kernel-doc` 校验、KABI 宏机制；seL4 的 `cppcheck`、`proof/` 形式化证明工作流（bitfield_gen.py 生成 Isabelle/HOL 证明）、CI 多工具矩阵。
3. **横向对比深化**：将 v0.2.1 的 11 维度对照扩展为 7 个子系统的三栏对照表（seL4 如何做 / OLK-6.6 如何做 / agent-linux 应当如何融合）。
4. **设计哲学层**：新增 Linux "演化式增量改进"哲学 vs seL4 "形式化验证驱动极简"哲学的对比与融合裁决。

---

## 2. OLK-6.6 工程思想深度提炼（ES-OLK-1~13 扩展）

> 本章为 v0.2.1 提炼的 ES-OLK-1~13 补充源码级证据，每条包含：思想描述 / 源码证据（文件:行号 + 片段）/ 对 agent-linux 的落地建议 / 对应工程标准文件。

### ES-OLK-1（关注点分离原则）

**思想描述**：每个顶层目录对应一个独立的关注点，跨关注点的耦合通过明确的接口进行。

**源码证据**：
- `Kbuild:48-72`——顶层构建文件以 `obj-y += kernel/` / `obj-y += mm/` / `obj-y += security/` / `obj-$(CONFIG_IO_URING) += io_uring/` 明确声明各子系统为独立构建单元。
- `Kconfig:11-33`——顶层配置以 `source "init/Kconfig"` / `source "mm/Kconfig"` / `source "security/Kconfig"` / `source "net/Kconfig"` 分source 各子系统配置，物理隔离。
- `security/` 目录进一步细分：`security/selinux/`（SELinux）、`security/landlock/`（Landlock）、`security/apparmor/`、`security/smack/`、`security/tomoyo/`、`security/yama/`、`security/loadpin/`、`security/safesetid/`、`security/lockdown/`、`security/bpf/`、`security/integrity/`、`security/keys/`——每个安全策略一个子目录。

**对 agent-linux 的落地建议**：8 子仓划分即关注点分离的体现。`airymaxos-kernel` / `airymaxos-security` / `airymaxos-services` / `airymaxos-tests-linux` 等子仓的边界应与 OLK-6.6 的目录边界对齐。

**对应工程标准文件**：`50-engineering-standards/04-engineering-philosophy.md` §1。

### ES-OLK-2（架构正交原则）

**思想描述**：`arch/` 是唯一的架构相关根目录，所有其他顶层目录必须是架构无关的。

**源码证据**：
- `arch/` 目录包含 25 个架构子目录（x86/arm64/arm/riscv/loongarch/mips/powerpc/s390/...）。
- `include/asm-generic/` 提供架构无关的默认实现，各架构通过 `arch/<arch>/include/asm/` 覆盖。
- `Kbuild:15`——`arch/$(SRCARCH)/kernel/asm-offsets.s` 生成架构相关的 asm-offsets，但通过 `include/generated/asm-offsets.h` 暴露给架构无关代码。

**对 agent-linux 的落地建议**：`airymaxos-kernel` 应保留 `arch/x86`、`arch/arm64` 目录结构，架构相关代码物理隔离。

**对应工程标准文件**：`20-modules/01-kernel.md`。

### ES-OLK-3（UAPI 与内核内部 API 分离）

**思想描述**：`include/uapi/` 是用户空间 ABI 的唯一来源，受永久稳定约束；`include/linux/` 是内核内部 API，可变。

**源码证据**：
- `include/uapi/` 包含 14 个子目录（linux/asm-generic/drm/fwctl/misc/mtd/rdma/scsi/sound/ub/video/xen），其中 `include/uapi/linux/` 有 584 个头文件。
- `include/uapi/linux/capability.h:1`——`/* SPDX-License-Identifier: GPL-2.0 WITH Linux-syscall-note */`，许可证含 `WITH Linux-syscall-note` 例外，允许用户空间程序自由包含。
- `include/uapi/linux/capability.h:17-33`——`_LINUX_CAPABILITY_VERSION_3`（`0x20080522`）、`__u32 version`——使用 `__u32`（UAPI 类型）而非 `u32`（内核内部类型）。
- 对比 `include/linux/capability.h`（内核内部）使用 `u32` 类型。

**对 agent-linux 的落地建议**：`include/uapi/airymax/` 物理隔离 UAPI，使用 `__u32`/`__u64` 类型；内核内部使用 `u32`/`u64`。

**对应工程标准文件**：`30-interfaces/01-syscalls.md` + `50-engineering-standards/04-engineering-philosophy.md` §2.3（L1-L4 接口稳定性分级）。

### ES-OLK-4（特性可配置原则）

**思想描述**：每个特性都可通过 Kconfig 开关控制，发行版可按需裁剪。

**源码证据**：
- `Kconfig`（顶层）——`mainmenu "Linux/$(ARCH) $(KERNELVERSION) Kernel Configuration"`，通过 `source` 引入各子系统 Kconfig。
- `lib/Kconfig.openeuler`——openEuler 特有配置项，如 `config KWORKER_NUMA_AFFINITY`（`bool "kworker NUMA affinity"`）。
- `Kbuild:65`——`obj-$(CONFIG_IO_URING) += io_uring/`，io_uring 子系统可通过 `CONFIG_IO_URING` 开关。
- `Kbuild:66`——`obj-$(CONFIG_RUST) += rust/`，Rust 支持可配置。
- `kernel/sched/fair.c:1059-1064`——`#ifdef CONFIG_BPF_SCHED` 条件编译 BPF 调度钩子，`entity_eligible()` 中通过 `bpf_sched_enabled()` 运行时检查。

**对 agent-linux 的落地建议**：每个微内核化特性（VFS 用户态化、capability、io_uring 消息传递）都应有独立 Kconfig 开关。

**对应工程标准文件**：`70-build-system/02-kconfig-system.md`。

### ES-OLK-5（条件编译规范化）

**思想描述**：`.c` 文件中避免直接 `#if`，改用 stub 函数 + `IS_ENABLED()` 转 C 布尔；`#endif` 必须标注对应的 `#ifdef` 名。

**源码证据**：
- `Documentation/process/coding-style.rst:1140-1189`（第 21 章 Conditional Compilation）——明确"Wherever possible, don't use preprocessor conditionals (#if, #ifdef) in .c files"，推荐"use the IS_ENABLED macro to convert a Kconfig symbol into a C boolean expression"。
- `Documentation/process/coding-style.rst:1183-1188`——`#endif /* CONFIG_SOMETHING */` 标注规范示例。
- `src/api/syscall.c:80-96`（seL4 同样遵循此规范）——`#ifdef CONFIG_IRQ_REPORTING` / `#else` / `#define checkInterrupt(was_interrupt_entry) checkInterrupt()` / `#endif`。
- `kernel/sched/fair.c:1058-1064`——`#ifdef CONFIG_BPF_SCHED` 包裹 BPF 钩子，主体逻辑通过 `IS_ENABLED` 风格的运行时检查 `bpf_sched_enabled()`。

**对 agent-linux 的落地建议**：`01-coding-standards.md` OS-STD-024/025/026 已覆盖，应强化检查。

**对应工程标准文件**：`50-engineering-standards/01-coding-standards.md`（OS-STD-024/025/026）。

### ES-OLK-6（UAPI 物理隔离原则）

**思想描述**：用户空间 ABI 头文件必须物理隔离于 `uapi/` 目录，变更流程、许可证、稳定性承诺均与内核内部头文件不同。

**源码证据**：
- `include/uapi/linux/capability.h:1`——SPDX 头 `GPL-2.0 WITH Linux-syscall-note`，含 syscall-note 例外。
- 对比 `include/linux/capability.h`（内核内部）——SPDX 头 `GPL-2.-only`，无 syscall-note 例外。
- `include/uapi/asm-generic/`——架构无关的 UAPI 默认实现。

**对 agent-linux 的落地建议**：`include/uapi/airymax/` 物理隔离，SPDX 头使用 `AGPL-3.0-or-later OR Apache-2.0 WITH Airymax-syscall-note`。

**对应工程标准文件**：`30-interfaces/01-syscalls.md` + 目录结构设计。

### ES-OLK-7（声明式配置 + 命令式构建分离）

**思想描述**：Kconfig 声明"有哪些可选项"，Kbuild/Makefile 命令式定义"如何构建"。

**源码证据**：
- `Kconfig`（声明式）——`mainmenu` / `source` / `config` / `bool` / `depends on` / `default` / `help` 语法定义可选项。
- `Kbuild`（命令式递归 Make）——`obj-y += kernel/` / `obj-$(CONFIG_IO_URING) += io_uring/` 定义构建规则。
- `Makefile:5-7`——`VERSION = 6` / `PATCHLEVEL = 6` / `SUBLEVEL = 0` 定义版本。
- `Makefile:515`——`CHECK = sparse` 定义检查工具。
- `Kbuild:23-46`——`bounds-file` / `timeconst-file` / `offsets-file` / `missing-syscalls` / `atomic-checks`（sha1 校验原子头文件未被手动修改）——声明式生成与校验。

**对 agent-linux 的落地建议**：内核子仓用 Kconfig + Kbuild，非内核子仓用 CMake（借鉴 seL4 ES-SEL4-10）。

**对应工程标准文件**：`70-build-system/01-kbuild-system.md` + `02-kconfig-system.md`。

### ES-OLK-8（维护者制度文档化原则）

**思想描述**：每个子系统的维护者、审查者、状态必须文档化于 `MAINTAINERS` 文件。

**源码证据**：
- `MAINTAINERS`（24218 行）——文件头明确定义字段：`M:`（Mail patches to）/ `R:`（Designated Reviewer）/ `L:`（Mailing list）/ `S:`（Status: Supported/Maintained/Odd Fixes/Orphan/Obsolete）/ `W:`（Web-page）/ `Q:`（Patchwork）/ `B:`（Bugs）/ `C:`（Chat）/ `P:`（Subsystem Profile）/ `T:`（SCM tree）/ `F:`（Files）/ `X:`（Excluded files）。
- 每个 subsystem 条目包含多个 `F:` 行，精确到文件/目录通配符。

**对 agent-linux 的落地建议**：8 子仓每个仓根目录新增 `MAINTAINERS` 文件（R-03 建议）。

**对应工程标准文件**：`120-development-process`（治理）+ R-03 建议。

### ES-OLK-9（规范可执行原则）

**思想描述**：每条编码规范必须有对应的检查脚本；规范若无法被机器检查，等同于不存在。

**源码证据**：
- `scripts/checkpatch.pl`（v0.32，14 行版本声明）——Perl 脚本，包含 72 个 `sub` 规则子例程，检查补丁的缩进、行宽、命名、错误处理、注释格式、签名等。
- `Makefile:111-119`——`# Use 'make C=1' to enable checking of only re-compiled files.` / `# Use 'make C=2' to enable checking of *all* source files` / `# See the file "Documentation/dev-tools/sparse.rst"`——sparse 静态分析器集成。
- `Makefile:1676-1689`——`make W=n` 分级警告：`1: warnings which may be relevant and do not occur too often` / `2: warnings which occur quite often but may still be relevant` / `3: more obscure warnings, can most likely be ignored` / `e: warnings are being treated as errors` / `Multiple levels can be combined with W=12 or W=123`。
- `scripts/Makefile.extrawarn:1-80`——W=1/2/3/e 四组警告的精确编译器 flag 定义（`-Wall` / `-Wundef` / `-Werror=implicit-function-declaration` / `-Wvla` 等）。
- `Documentation/dev-tools/`——含 `checkpatch.rst` / `sparse.rst` / `coccinelle.rst` / `kasan.rst` / `kcov.rst` / `kcsan.rst` / `kfence.rst` / `kmemleak.rst` / `kmsan.rst` / `kselftest.rst` / `ubsan.rst` 等工具文档——完整的"规范可执行"工具链。

**对 agent-linux 的落地建议**：`50-engineering-standards/08-compliance-checklist.md`（558 行，17 项检查 + 16 个检查脚本）已覆盖，应增补 R-04 四项 seL4 借鉴检查规则。

**对应工程标准文件**：`50-engineering-standards/08-compliance-checklist.md`。

### ES-OLK-10（regression 零容忍原则）

**思想描述**：regression 是"特别坏的 bug"，必须在当前 stabilization 阶段修复或 revert。

**源码证据**：
- `Documentation/process/coding-style.rst:1189`（第 22 章 "Do not crash the kernel"）——明确内核不应主动崩溃的工程取向。
- `Kbuild:38-46`——`missing-syscalls` 检查（`scripts/checksyscalls.sh`）确保系统调用完整性，防止回归。
- `Kbuild:42-46`——`atomic-checks`（sha1 校验）防止原子操作头文件被手动修改导致回归。

**对 agent-linux 的落地建议**：`04-engineering-philosophy.md` OS-IRON-003 已覆盖，应建立 regression 自动化检测。

**对应工程标准文件**：`50-engineering-shandards/04-engineering-philosophy.md` §5（OS-IRON-003）。

### ES-OLK-11（用户空间 ABI 永久稳定原则）

**思想描述**：一旦接口导出至用户空间，必须永久支持。

**源码证据**：
- `include/uapi/linux/capability.h:17-25`——`_LINUX_CAPABILITY_VERSION_1`（`0x19980330`）/ `_LINUX_CAPABILITY_VERSION_2`（`0x20071026`，deprecated）/ `_LINUX_CAPABILITY_VERSION_3`（`0x20080522`）——三版本共存，永久向后兼容。
- `include/uapi/linux/capability.h:1`——`GPL-2.0 WITH Linux-syscall-note` 许可证例外，明确用户空间可自由包含。

**对 agent-linux 的落地建议**：`04-engineering-philosophy.md` OS-IRON-001/005 已覆盖。

**对应工程标准文件**：`50-engineering-standards/04-engineering-philosophy.md` §2.1（OS-IRON-001）+ §9（OS-IRON-005）。

### ES-OLK-12（运行时可加载原则）

**思想描述**：机制留在内核，实现可作为模块运行时加载/卸载；`EXPORT_SYMBOL` 紧跟函数定义。

**源码证据**：
- `kernel/fork.c:656`——`EXPORT_SYMBOL(free_task);` 紧跟 `free_task` 函数定义。
- `kernel/fork.c:992`——`EXPORT_SYMBOL_GPL(__mmdrop);` 紧跟 `__mmdrop` 定义。
- `kernel/fork.c:1046`——`EXPORT_SYMBOL_GPL(__put_task_struct);` 紧跟定义。
- `kernel/fork.c:1488`——`EXPORT_SYMBOL_GPL(mmput);` 紧跟定义。
- `Kbuild:66`——`obj-$(CONFIG_RUST) += rust/`，Rust 模块可加载。

**对 agent-linux 的落地建议**：`60-driver-model` + `20-modules/01-kernel.md` 已覆盖，`EXPORT_SYMBOL` 紧跟规范应强化。

**对应工程标准文件**：`50-engineering-standards/01-coding-standards.md`（OS-STD-009）。

### ES-OLK-13（文档即代码原则）

**思想描述**：文档与代码同仓库，同步演进；kernel-doc 注释、ABI 文档、`make htmldocs` 全链路打通。

**源码证据**：
- `Documentation/process/coding-style.rst`（1271 行，22 章）——完整的编码规范文档，与代码同仓库。
- `Documentation/dev-tools/`——20+ 工具文档（checkpatch/sparse/coccinelle/kasan/...）。
- `Documentation/process/`——开发流程文档（coding-style/maintainer/submitting-patches/...）。
- `MAINTAINERS`（24218 行）——维护者文档即代码。
- `Kbuild:38-46`——`missing-syscalls` / `atomic-checks` 校验脚本即代码。

**对 agent-linux 的落地建议**：`04-engineering-philosophy.md` OS-KER-050 已覆盖。

**对应工程标准文件**：`50-engineering-standards/04-engineering-philosophy.md` §8（OS-KER-050）+ `01-coding-standards.md`（OS-STD-012 kernel-doc 强制）。

### 新增 ES-OLK-14（KABI 二进制兼容演进机制）

> **v0.2.1 遗漏补充**：openEuler 特有的 KABI 宏机制是 OLK-6.6 相对原生 Linux 6.6 的重要工程增量。

**思想描述**：通过宏在不破坏二进制兼容性的前提下演进内核数据结构——新增字段用 `KABI_EXTEND`、废弃字段用 `KABI_DEPRECATE`、枚举变更用 `KABI_BROKEN_INSERT_ENUM`/`KABI_BROKEN_REMOVE_ENUM`、预留空间用 `KABI_USE`。

**源码证据**：
- `include/linux/kabi.h`（头文件注释）——明确"openEuler kABI abstraction header"，"These kabi macros hide the changes from the kabi checker and from the process that computes the exported symbols' checksums"。
- `include/linux/kabi.h:60-80`——宏定义注释：`KABI_EXTEND`（Adds a new field to a struct，must always be added to the end）/ `KABI_DEPRECATE`（Marks the element as deprecated，keeping a hole in its place）/ `KABI_BROKEN_INSERT_ENUM(_new)` / `KABI_BROKEN_REMOVE_ENUM(_orig)`。
- `include/linux/bpf.h:321`——`KABI_BROKEN_REPLACE(` 实际使用示例。
- `include/linux/bpf.h:336-337`——`KABI_USE(1, atomic64_t sleepable_refcnt)` / `KABI_USE(2, const struct btf_type *attach_func_proto)`——预留空间填充新字段。
- `include/linux/bpf.h:721`——`KABI_BROKEN_INSERT_ENUM(MEM_ALIGNED = BIT(17 + BPF_BASE_TYPE_BITS))`——枚举插入。
- `lib/Kconfig.kabi:1-30`——`config KABI_COMPAT`（`bool "Enable kabi compatible fix"`，`depends on X86_64 || ARM64`）/ `config KABI_RESERVE`（`bool "Enable KABI PADDING RESERVE"`，`default y`）/ `config KABI_SIZE_ALIGN_CHECKS`（`bool "Enable more stringent kabi checks in the macros"`，`default y`）。
- `kernel/sched/sched.h:722-733`——`KABI_REPLACE(s64 avg_vruntime, s64 sum_w_vruntime)` / `KABI_REPLACE(u64 min_vruntime, u64 zero_vruntime)` / `KABI_BROKEN_REMOVE(u64 min_vruntime_copy)`——EEVDF 引入时通过 KABI 宏保持二进制兼容。

**对 agent-linux 的落地建议**：agent-linux 的内核态 ABI 演进应借鉴 KABI 宏机制——在数据结构变更时通过宏保持二进制兼容，而非直接修改结构体。建议在 `50-engineering-standards/` 新增 `09-kabi-evolution.md` 规范。

**对应工程标准文件**：建议新增 `50-engineering-standards/09-kabi-evolution.md`（P1 优先级）。

---

## 3. seL4 工程思想深度提炼（ES-SEL4-1~10 扩展）

> 本章为 v0.2.1 提炼的 ES-SEL4-1~10 补充源码级证据。

### ES-SEL4-1（Liedtke 极简原则）

**思想描述**：微内核代码量必须可被形式化证明覆盖——seL4 核心约 8700 行 C 代码。任何新增功能必须论证"无法在用户空间高效实现"。

**源码证据**：
- `src/kernel/` 仅 6 个文件：`boot.c`（41KB）/ `cspace.c`（5.8KB）/ `faulthandler.c`（5.3KB）/ `sporadic.c`（12KB）/ `stack.c`（249B）/ `thread.c`（23KB）——内核核心机制极简。
- `src/api/` 仅 2 个文件：`faults.c`（261 行）/ `syscall.c`（662 行）——API 层极简。
- `src/object/` 11 个文件：`cnode.c` / `domain.c` / `endpoint.c` / `interrupt.c` / `notification.c` / `objecttype.c` / `reply.c` / `schedcontext.c` / `schedcontrol.c` / `tcb.c` / `untyped.c`——对象类型有限。
- `src/fastpath/fastpath.c`（31KB）——独立的最优路径优化，证明"性能与极简可共存"。
- `src/util.c`（452 行）/ `src/assert.c`（43 行）/ `src/string.c`（42 行）/ `src/inlines.c`（16 行）——工具库极简。

**对 agent-linux 的落地建议**：`airymaxos-kernel` 复用 atoms/corekern MicroCoreRT 极简内核，机制最小化（IPC/内存/任务/时间 4 原子机制）。

**对应工程标准文件**：`10-architecture/03-microkernel-strategy.md`。

### ES-SEL4-2（capability 单一权限模型）

**思想描述**：所有权限（内存访问、IPC 端点、线程控制）统一通过 capability 表达。capability 可 mint/mintcopy/derive/revoke，形成权限派生树。

**源码证据**：
- `src/object/cnode.c:50-230`（`decodeCNodeInvocation`）——capability 操作解码：`CNodeCopy`（line 116）/ `CNodeMint`（line 136）/ `CNodeMove`（line 157）/ `CNodeMutate`（line 163）/ `CNodeRevoke`（line 195）/ `CNodeDelete`（line 200）/ `CNodeCancelBadgedSends`（line 229）/ `CNodeRotate`（line 308）。
- `src/object/cnode.c:80,126,146`——`deriveCap_ret_t dc_ret = deriveCap(srcSlot, srcCap);` 调用 capability 派生。
- `src/object/cnode.c:315-364`——`invokeCNodeRevoke`（调用 `cteRevoke`）/ `invokeCNodeDelete`（调用 `cteDelete`）/ `invokeCNodeInsert`（调用 `cteInsert`）/ `invokeCNodeMove`（调用 `cteMove`）/ `invokeCNodeRotate`（调用 `cteSwap`/`cteMove`）。
- `src/object/cnode.c:528`——`exception_t cteRevoke(cte_t *slot)`——capability 树撤销（递归删除所有子节点）。
- `src/object/cnode.c:552`——`exception_t cteDelete(cte_t *slot, bool_t exposed)`——capability 节点删除。
- `src/object/objecttype.c:62`——`deriveCap_ret_t deriveCap(cte_t *slot, cap_t cap)`——capability 派生核心函数，按 capType 分发。
- `include/object/structures_64.bf:11-50`——bitfield DSL 定义 capability 布局：`block null_cap` / `block untyped_cap` / `block endpoint_cap(capEPBadge, capCanGrantReply, capCanGrant, capCanSend, capCanReceive, capEPPtr, capType)` / `block notification_cap` / `block reply_cap` / `block cnode_cap(capCNodeRadix, capCNodeGuardSize, capCNodeGuard, capCNodePtr, capType)`——每个 capability 类型有明确的权限位字段。

**对 agent-linux 的落地建议**：`airymaxos-security` 的 capability 模块应以 seL4 派生模型为蓝本（Copy/Mint/Move/Mutate/Revoke/Delete），IRON-9 v2 [SC] `security_types.h` 已设计 38 ID capability 枚举 + mint/mintcopy/derive/revoke 派生模型。

**对应工程标准文件**：`20-modules/03-security.md` + IRON-9 v2 [SC] `security_types.h`。

### ES-SEL4-3（服务用户态化）

**思想描述**：内核只提供原语，文件系统、网络栈、驱动、内存管理策略都运行在用户空间。

**源码证据**：
- `libsel4/`（独立目录）——用户态 API 库，与内核源码树物理分离。
- `libsel4/include/sel4/`（23 个头文件）——`assert.h` / `bootinfo.h` / `config.h` / `constants.h` / `errors.h` / `faults.h` / `functions.h` / `macros.h` / `objecttype.h` / `sel4.h` / `shared_types.h` / `simple_types.h` / `syscalls.h` / `types.h` 等——用户态通过 libsel4 与内核通信，不直接调用内核内部函数。
- `src/kernel/faulthandler.c:21-44`——`handleFault()` 通过 capability（`TCB_PTR_CTE_PTR(tptr, tcbFaultHandler)->cap`）查找 fault handler endpoint，将 fault IPC 发送到用户态 fault handler——内核不处理 fault 恢复策略，由用户态决定。

**对 agent-linux 的落地建议**：`airymaxos-services` 的 VFS/网络/驱动用户态化（Phase 1 VFS + Phase 2 网络/驱动），`airymaxos-sdk`（4 语言 SDK）借鉴 libsel4 独立模型。

**对应工程标准文件**：`20-modules/02-services.md` + `10-architecture/03-microkernel-strategy.md`。

### ES-SEL4-4（消息传递 IPC）

**思想描述**：进程间通信的唯一机制是消息传递。IPC 有三种形态：endpoint（同步消息）、notification（异步信号）、fastpath（最优路径优化）。

**源码证据**：
- `src/object/endpoint.c:20-50`（`sendIPC`）——endpoint 同步消息发送，状态机 `EPState_Idle`/`EPState_Send`/`EPState_Recv`。
- `src/object/notification.c:21-50`——`ntfn_ptr_get_queue()` / `maybeDonateSchedContext()`（MCS 调度上下文捐赠）——notification 异步信号。
- `src/fastpath/fastpath.c:26-100`（`fastpath_call`）——fastpath 最优路径：`info = messageInfoFromWord_raw(msgInfo)` 解析消息 → `lookup_fp()` 查找 capability → `cap_capType_equals(ep_cap, cap_endpoint_cap)` 检查端点 → `endpoint_ptr_get_state(ep_ptr) != EPState_Recv` 检查接收方 → 任何检查失败则 `slowpath(SysCall)` 降级到通用路径。
- `src/api/syscall.c:557-660`（`handleSyscall`）——syscall 分发：`case SysCall:` → `handleInvocation(true, true, true, false, ...)` / `case SysReplyRecv:` → `handleInvocation` + `handleRecv` / `case SysSend:` / `case SysNBSend:` / `case SysRecv:` / `case SysNBRecv:` / `case SysYield:` → `handleYield()`。

**对 agent-linux 的落地建议**：`30-interfaces/02-ipc-protocol.md`（128B 定长消息头 + io_uring 消息传递）+ IRON-9 v2 [SC] `ipc.h`，借鉴 fastpath 优化思路。

**对应工程标准文件**：`30-interfaces/02-ipc-protocol.md` + IRON-9 v2 [SC] `ipc.h`。

### ES-SEL4-5（形式化验证驱动原则）

**思想描述**：内核实现必须可被形式化证明满足抽象规约。这要求代码避免形式化工具无法处理的特性。

**源码证据**：
- `tools/bitfield_gen.py:14-16`（文件头注释）——`# A tool for generating bitfield structures with get/set/new methods including Isabelle/HOL specifications and correctness proofs.`——bitfield 代码生成器同时生成 Isabelle/HOL 规约与正确性证明。
- `tools/bitfield_gen.md`——"accessor code in C with formal specifications and proofs in Isabelle/HOL"，"in HOL for that data type, as well as proofs that the generated C code correctly"，"the generated correctness proof"——文档明确 codegen 与证明的绑定关系。
- `CMakeLists.txt`（seL4 根）——`string(REPLACE ".bf" "_proofs.thy" proofs_target "${bf_name}")` / `GenProofsBFTarget(...)`——CMake 构建系统为每个 `.bf` 文件生成对应的 `_proofs.thy`（Isabelle 理论文件）证明目标。
- `libsel4/CMakeLists.txt:18-25`——`config_choice(LibSel4FunctionAttribute ... "Verification friendly default configuration. syscalls will be inlined, but generated functions will not.")`——libsel4 提供形式化验证友好的配置选项。
- `README.md`——CI badges 含 `[![Proof Sync](https://github.com/seL4/seL4/actions/workflows/preprocess-deploy.yml/badge.svg)]`——Proof Sync CI 工作流确保源码与形式化证明同步。
- `src/api/faults.c:18-25`——`compile_assert(InvalidRoot, lookup_fault_invalid_root + 1 == seL4_InvalidRoot)` / `compile_assert(MissingCapability, ...)`——编译时断言确保内核常量与 libsel4 一致（形式化证明的前置条件）。

**对 agent-linux 的落地建议**：`airymaxos-tests-linux` 的 formal-verification 模块借鉴 seL4 风格形式化验证框架（思想借鉴，不引入 Isabelle/HOL 全套工具链）。

**对应工程标准文件**：`20-modules/08-tests.md` + `80-testing`。

### ES-SEL4-6（接口契约 XML 定义）

**思想描述**：seL4 通过 `tools/syscall.xml` 定义系统调用接口契约，由代码生成器自动生成用户态 stub 与内核态 entry。

**源码证据**：
- `libsel4/include/api/syscall.xml`——系统调用契约 XML：`<syscalls>` / `<api-master>` / `<config>` / `<syscall name="Call"/>` / `<syscall name="ReplyRecv"/>` / `<syscall name="Send"/>` / `<syscall name="NBSend"/>` / `<syscall name="Recv"/>` / `<syscall name="Reply"/>` / `<syscall name="Yield"/>` / `<syscall name="NBRecv"/>`——8 个 API syscall + `<api-mcs>` 11 个 MCS syscall + `<debug>` 条件编译的 debug syscall。
- `libsel4/include/interfaces/object-api.xml`——对象 API 契约 XML：`<api name="ObjectApi">` / `<interface name="seL4_Untyped">` / `<method id="UntypedRetype" name="Retype">` / `<param dir="in" name="type" type="seL4_Word"/>` / `<error name="seL4_DeleteFirst"/>`——定义每个方法的参数、错误码、描述。
- `tools/syscall_header_gen.py:13-15`——`# seL4 System Call ID Generator` / `from jinja2 import Environment, BaseLoader` / `import xml.dom.minidom`——使用 Jinja2 模板从 XML 生成 C 头文件。
- `tools/syscall_header_gen.py:33-40`——`COMMON_HEADER = "/* This header was generated by kernel/tools/syscall_header_gen.py. To add a system call number, edit kernel/libsel4/include/api/syscall.xml */"`——生成的头文件含溯源注释。
- `tools/invocation_header_gen.py`（5.5KB）+ `tools/invocation_json_gen.py`（2.5KB）——invocation 代码生成器（头文件 + JSON）。
- `libsel4/tools/syscall_stub_gen.py` / `libsel4/tools/syscall_stub_gen_rs.py`——syscall stub 生成器（C + Rust）。
- `libsel4/tools/sel4_idl.xsd`——XML schema 定义接口契约格式。
- `README.md`——`[![XML](https://github.com/seL4/seL4/actions/workflows/xml_lint.yml/badge.svg)]`——XML lint CI 工作流确保契约 XML 格式正确。

**对 agent-linux 的落地建议**：在 `50-engineering-standards/40-integration/` 下新增 `syscall-contract.xml` 规范（R-01 建议，~16h），由 `scripts/syscall_gen.py` 自动生成 `include/uapi/airymax/syscall.h` + `kernel/entry/airymax_syscall_table.c`。

**对应工程标准文件**：建议新增 `50-engineering-standards/40-integration/syscall-contract.xml`（P2）。

### ES-SEL4-7（架构正交分层原则）

**思想描述**：内核核心逻辑与架构相关代码物理隔离，通过 `arch/` / `machine/` / `plat/` 三层适配。

**源码证据**：
- `src/arch/`——3 个架构：`arm/`（11 子目录）/ `riscv/`（8 子目录）/ `x86/`（11 子目录）。
- `src/machine/`——5 个文件：`capdl.c` / `fpu.c` / `io.c` / `profiler.c` / `registerset.c`——机器相关原语。
- `src/plat/`——42 个平台子目录（pc99/tk1/...）——平台相关。
- `src/smp/`——2 个文件：`ipi.c` / `lock.c`——多核支持。
- `include/` 与 `src/` 同构：`include/{api,kernel,object,arch,machine,plat,smp,benchmark,model,drivers,fastpath}` 与 `src/{api,kernel,object,arch,machine,plat,smp,benchmark,model,drivers,fastpath}` 一一对应。
- `include/object/structures.h:9-12`——`#include <arch/object/structures_gen.h>` / `#include <mode/types.h>`——架构相关生成的头文件被架构无关核心引用。

**对 agent-linux 的落地建议**：`airymaxos-kernel` 的 `arch/machine/plat` 三层适配（待目录结构落地）。

**对应工程标准文件**：`10-architecture` + 目录结构设计。

### ES-SEL4-8（结构定义代码生成原则）

**思想描述**：复杂位域结构通过 DSL（`.bf` 文件）定义，由代码生成器生成 C 代码 + Isabelle/HOL 证明。

**源码证据**：
- `include/object/structures_64.bf`（64 位位域定义）——DSL 语法定义 capability 布局：`block null_cap { padding 64; field capType 5; ... }` / `block endpoint_cap(capEPBadge, capCanGrantReply, capCanGrant, capCanSend, capCanReceive, capEPPtr, capType) { field capEPBadge 64; ... }`。
- `include/object/structures_32.bf`（32 位位域定义）。
- `include/arch/{arm,riscv,x86}/arch/object/structures.bf`——架构相关位域定义。
- `include/plat/pc99/plat/{32,64}/plat_mode/machine/hardware.bf`——平台相关位域定义。
- `libsel4/sel4_arch_include/{aarch64,aarch32,riscv64,riscv64,ia32,x86_64}/sel4/sel4_arch/types.bf`——libsel4 架构相关位域定义。
- `tools/bitfield_gen.py`（123KB）——代码生成器：读取 `.bf` DSL → 生成 C 结构体 + get/set/new 访问函数 + Isabelle/HOL 规约 + 正确性证明。
- `include/object/structures.h:8`——`#include <arch/object/structures_gen.h>`——引用生成的头文件。
- `tools/bf.vim`——Vim 语法高亮文件，`.bf` DSL 有工具支持。

**对 agent-linux 的落地建议**：为 IRON-9 v2 [SC] 共享契约层 6 个头文件引入 `structures.bf` 式 codegen（R-02 建议，~12h），由 `scripts/bitfield_gen.py` 自动生成 C 结构体与访问函数。

**对应工程标准文件**：建议新增 `50-engineering-standards/40-integration/bitfield-contract.bf`（P2）。

### ES-SEL4-9（用户态 API 库独立原则）

**思想描述**：用户态 API 库与内核源码树物理分离，独立版本、独立构建、独立测试。

**源码证据**：
- `libsel4/`（独立目录）——包含 `CMakeLists.txt`（独立 CMake 构建）/ `include/`（API 头文件）/ `arch_include/`（arm/riscv/x86 架构相关）/ `sel4_arch_include/`（aarch64/aarch32/riscv64/riscv64/ia32/x86_64 seL4 架构相关）/ `sel4_plat_include/`（45 个平台）/ `src/`（API 实现）/ `tools/`（代码生成工具）。
- `libsel4/CMakeLists.txt:1-10`——`cmake_minimum_required(VERSION 3.16.0)` / `project(libsel4 C)`——独立 CMake 项目。
- `libsel4/include/sel4/sel4.h`——用户态总入口头文件。
- `libsel4/src/sel4_bootinfo.c`——libsel4 唯一的 `.c` 实现文件（bootinfo 处理），其余均为生成代码。

**对 agent-linux 的落地建议**：`airymaxos-sdk`（4 语言 SDK）借鉴 libsel4 独立模型——独立版本、独立构建、独立测试。

**对应工程标准文件**：`airymaxos-cloudnative` 的 SDK + `airymaxos-sdk`。

### ES-SEL4-10（现代构建系统原则）

**思想描述**：微内核构建系统采用 CMake，支持多编译器（GCC/Clang）、多架构、多平台、多配置。

**源码证据**：
- `CMakeLists.txt`（seL4 根，27KB）——`CMakeLists.txt` 主构建文件。
- `config.cmake`（20KB）——配置选项。
- `gcc.cmake`（6.8KB）——GCC 编译器配置。
- `llvm.cmake`（1.2KB）——Clang/LLVM 编译器配置。
- `cmake/`（目录）——CMake 模块。
- `configs/`（目录）——预置配置。
- `.cmake-format.yaml`——CMake 格式化配置。

**对 agent-linux 的落地建议**：内核子仓用 Kbuild（与 Linux 6.6 一致），非内核子仓用 CMake（借鉴 seL4）。

**对应工程标准文件**：`70-build-system`。

### 新增 ES-SEL4-11（CI 多工具矩阵验证）

> **v0.2.1 遗漏补充**：seL4 的 CI 多工具矩阵是形式化验证之外的质量保障工程思想。

**思想描述**：通过 CI 矩阵并行运行多种验证工具（C Parser / Compile / Proof Sync / seL4Test / RefMan / XML lint），确保代码质量多维覆盖。

**源码证据**：
- `README.md`——8 个 CI badges：`[![CII Best Practices](...)]` / `[![CI](.../push.yml/badge.svg)]` / `[![seL4Test](.../sel4test-deploy.yml/badge.svg)]` / `[![C Parser](.../cparser.yml/badge.svg)]` / `[![Compile](.../compilation-checks.yml/badge.svg)]` / `[![Proof Sync](.../preprocess-deploy.yml/badge.svg)]` / `[![RefMan](.../manual.yml/badge.svg)]` / `[![XML](.../xml_lint.yml/badge.svg)]`。
- `tools/kernel_pylint.sh`——Python 代码 lint 脚本。
- `tools/kernel_xmllint.sh`——XML lint 脚本。
- `tools/xmllint.sh`——通用 XML lint。
- `tools/pylintrc`——Python lint 配置。
- `tools/circular_includes.py`——循环 include 检测。
- `.github/`——GitHub Actions 工作流目录。

**对 agent-linux 的落地建议**：`airymaxos-tests-linux` 应建立 CI 多工具矩阵——编译检查 / 静态分析（sparse/smatch/cppcheck）/ 单元测试（KUnit）/ 集成测试（kselftest）/ 文档生成 / 契约一致性检查。

**对应工程标准文件**：`20-modules/08-tests.md` + `80-testing`。

---

## 4. 关键子系统横向对比（三栏对照表）

### 4.1 调度子系统

| 维度 | seL4 如何做 | OLK-6.6 如何做 | agent-linux 应当如何融合 |
|------|------------|---------------|---------------------------|
| 调度算法 | 固定优先级多级队列（`src/object/tcb.c:30` `checkPrio` 基于 MCP；`:115` `tcbSchedEnqueue`；L1/L2 bitmap 加速） | EEVDF（`kernel/sched/fair.c:925` `avg_vruntime`；`:1057` `entity_eligible`；`:1252` `pick_eevdf` O(log n) 增强红黑树）+ RT/DL/EXT 多类 | 保留 OLK-6.6 EEVDF 为基线；微内核化后调度策略接口借鉴 seL4 MCP（最大优先级控制） |
| 调度上下文 | MCS 模型（`src/object/notification.c:38` `maybeDonateSchedContext` 调度上下文捐赠） | `sched.h:722` `KABI_REPLACE` 保持 EEVDF 引入的二进制兼容 | io_uring 消息传递时借鉴 MCS 调度上下文捐赠思路 |
| 可扩展调度 | 无（极简） | `kernel/sched/ext.c`（sched_ext BPF 可编程调度器）+ `bpf_sched.c`（BPF 调度钩子，`fair.c:1059` `bpf_sched_cfs_tag_entity_eligible`） | 借鉴 sched_ext 思路，agent-linux 安全策略可通过 BPF 钩子注入调度决策 |
| 调度策略可配置 | `#ifdef CONFIG_KERNEL_MCS`（`src/object/endpoint.c:21`） | `kernel/sched/Kconfig`（无独立文件，通过 `CONFIG_SCHED_DEBUG` 等） | Kconfig 开关控制调度策略 |

### 4.2 IPC 子系统

| 维度 | seL4 如何做 | OLK-6.6 如何做 | agent-linux 应当如何融合 |
|------|------------|---------------|---------------------------|
| IPC 机制 | endpoint（同步，`src/object/endpoint.c`）+ notification（异步，`src/object/notification.c`）+ fastpath（`src/fastpath/fastpath.c:26` `fastpath_call`） | 系统调用（`sys_*`）+ pipe/socket/shared memory + io_uring（`io_uring/io_uring.c` 4752 行） | io_uring 消息传递机制 + 借鉴 seL4 fastpath 热路径优化（`unlikely()` 早期降级 slowpath） |
| 消息格式 | 定长 MessageInfo（`seL4_MessageInfo_t`，length/badge/caps）+ IPC buffer | 变长 struct msghdr / iovec | 128B 定长消息头 + io_uring SQE/CQE |
| fastpath | `src/fastpath/fastpath.c:26-100`——`fastpath_call()` 检查无 extra caps / 无 fault / endpoint 可发送 / 接收方等待，任一失败则 `slowpath(SysCall)` | io_uring SQpoll 模式（`io_uring/sqpoll.c`）——内核轮询 SQ ring，避免系统调用开销 | io_uring fastpath：常见操作走 SQpoll，复杂操作走系统调用 |
| 错误处理 | `exception_t` 枚举（`include/api/failures.h:16-22`：`EXCEPTION_NONE/FAULT/LOOKUP_FAULT/SYSCALL_ERROR/PREEMPTED`）+ `current_syscall_error` 结构体 | 负 errno（`-EINVAL`/`-ENOMEM`）+ goto 集中出口 | OLK-6.6 负 errno + goto（与 Linux 一致） |

### 4.3 内存管理子系统

| 维度 | seL4 如何做 | OLK-6.6 如何做 | agent-linux 应当如何融合 |
|------|------------|---------------|---------------------------|
| 分配模型 | 无动态分配（形式化约束）——untyped 内存预分配，Retype 创建对象（`libsel4/include/interfaces/object-api.xml` `UntypedRetype`） | kmalloc/kzalloc/vmalloc/kmem_cache + MGLRU（`mm/vmscan.c` LRU_GEN 多代 LRU） | OLK-6.6 kmalloc 模型（宏内核内存模型） |
| 页面回收 | 无（用户态管理） | MGLRU 多代 LRU（`mm/vmscan.c`）+ damon（`mm/damon/`）+ compaction/oom | 保留 OLK-6.6 MGLRU |
| openEuler 增量 | N/A | `mm/gmem.c`/`gmem_phys.c`（guest 内存）/ `mm/etmem.c`（etmem 内存增强）/ `mm/dynamic_pool.c`（动态内存池） | 评估 gmem/etmem 是否适用于 agent-linux 的用户态服务内存管理 |
| 地址空间 | vspace capability（`include/object/structures_64.bf` `vspace_cap`） | 页表管理（`arch/x86/mm/` / `arch/arm64/mm/`） | OLK-6.6 页表模型 + seL4 capability 控制地址空间访问权限 |

### 4.4 安全/capability 子系统

| 维度 | seL4 如何做 | OLK-6.6 如何做 | agent-linux 应当如何融合 |
|------|------------|---------------|---------------------------|
| 权限模型 | capability 单一模型（`src/object/cnode.c` Copy/Mint/Move/Mutate/Revoke/Delete；`:528` `cteRevoke` 撤销派生树） | POSIX capabilities（`security/commoncap.c:66` `cap_capable`）+ LSM 钩子（`security/selinux/hooks.c` 215 个 `LSM_HOOK_INIT`）+ LSM stacking（`security/security.c:93` `ordered_lsm_init`） | 融合：security 子仓 capability（seL4 派生模型）+ LSM 钩子（OLK-6.6 可插拔策略） |
| 权限派生 | `deriveCap()`（`src/object/objecttype.c:62`）+ mint/mintcopy/derive/revoke | 无派生（POSIX capabilities 是位掩码，无派生树） | 借鉴 seL4 派生树（IRON-9 v2 [SC] `security_types.h` 38 ID + mint/mintcopy/derive/revoke） |
| 策略可插拔 | 无（capability 即策略） | LSM 框架（`security/security.c` `ordered_lsms` 排序初始化）+ SELinux/Landlock/AppArmor/Smack/Tomoyo/Yama/LoadPin/SafeSetID/Lockdown/BPF | 保留 LSM 框架 + 新增 capability 模块 |
| 安全标签 | capability badge（`include/object/structures_64.bf` `capEPBadge`） | SELinux 安全上下文（`security/selinux/ss/context.c`） | capability badge 借鉴用于权限标记 |

### 4.5 构建系统（Kbuild vs seL4 build system）

| 维度 | seL4 如何做 | OLK-6.6 如何做 | agent-linux 应当如何融合 |
|------|------------|---------------|---------------------------|
| 构建系统 | CMake（`CMakeLists.txt` + `config.cmake` + `gcc.cmake` + `llvm.cmake`） | Kbuild + Kconfig + Makefile 三层（`Makefile` 68KB + `Kbuild` + `Kconfig`） | 内核子仓用 Kbuild（与 Linux 6.6 一致），非内核子仓用 CMake（借鉴 seL4） |
| 配置 | `config.cmake`（`config_choice`/`config_option`/`config_string`） | Kconfig（`source`/`config`/`bool`/`depends on`/`select`/`default`/`help`） | 内核用 Kconfig，非内核用 CMake config |
| 代码生成 | `tools/bitfield_gen.py`（.bf → C + HOL）/ `tools/syscall_header_gen.py`（XML → C 头文件）/ `tools/invocation_header_gen.py` | `scripts/`（checkpatch/checksyscalls/check-kabi/kabisyms/kabideps）+ `Kbuild:23-46`（bounds/timeconst/offsets/atomic-checks 生成） | 借鉴 seL4 codegen（syscall.xml + bitfield.bf）+ 保留 OLK-6.6 scripts |
| 检查工具 | `tools/kernel_pylint.sh` / `tools/kernel_xmllint.sh` / `tools/circular_includes.py` | sparse（`Makefile:515` `CHECK = sparse`）+ smatch + `scripts/Makefile.extrawarn` W=1/2/3/e | 完整继承 OLK-6.6 sparse/W 分级 + 借鉴 seL4 XML/pylint |

### 4.6 文档系统（kernel-doc vs seL4 spec）

| 维度 | seL4 如何做 | OLK-6.6 如何做 | agent-linux 应当如何融合 |
|------|------------|---------------|---------------------------|
| 文档格式 | LaTeX（`manual/manual.tex` + `manual/parts/` + `manual/figures/`）+ Doxygen（`manual/Doxyfile`） | reStructuredText（`Documentation/` 80+ 子目录）+ kernel-doc 注释 + `make htmldocs` | OLK-6.6 kernel-doc + reST（与 Linux 一致） |
| 接口文档 | XML 契约（`libsel4/include/api/syscall.xml` + `libsel4/include/interfaces/object-api.xml`）含 `<brief>`/`<description>`/`<param>`/`<error>` | UAPI 头文件 + `Documentation/ABI/` | OLK-6.6 UAPI + 借鉴 seL4 XML 契约（含参数/错误码描述） |
| 规范文档 | `manual/manual.tex`（手册） | `Documentation/process/coding-style.rst`（1271 行 22 章）+ `Documentation/maintainer/` | OLK-6.6 规范文档体系 |
| 文档生成 | `manual/Makefile` + RefMan CI（`README.md` `[![RefMan]`） | `make htmldocs` + `scripts/kernel-doc` | OLK-6.6 `make htmldocs` |

### 4.7 测试与验证（Linux KUnit/kselftest vs seL4 proof/）

| 维度 | seL4 如何做 | OLK-6.6 如何做 | agent-linux 应当如何融合 |
|------|------------|---------------|---------------------------|
| 形式化验证 | Isabelle/HOL 证明（`tools/bitfield_gen.py` 生成 `_proofs.thy`；`CMakeLists.txt` `GenProofsBFTarget`；Proof Sync CI） | 无 | `airymaxos-tests-linux` formal-verification 模块借鉴 seL4 思想（不引入全套 Isabelle/HOL） |
| 单元测试 | seL4Test（`README.md` `[![seL4Test]` CI） | KUnit（`lib/kunit/`）+ kselftest（`tools/testing/kselftest/`） | OLK-6.6 KUnit + kselftest |
| 静态分析 | C Parser CI（`README.md` `[![C Parser]`）+ cppcheck | sparse（`Documentation/dev-tools/sparse.rst`）+ smatch + coccinelle（`scripts/coccinelle/`） | OLK-6.6 sparse/smatch/coccinelle + 借鉴 seL4 C Parser |
| 运行时检查 | `assert()`（`src/assert.c`）+ `compile_assert`（`src/api/faults.c:18`） | KASAN/KCSAN/KFENCE/KMSAN/UBSAN（`Documentation/dev-tools/`）| OLK-6.6 KASAN/KCSAN/KFENCE/KMSAN/UBSAN |
| CI 矩阵 | 8 个 CI 工作流（CII/CI/seL4Test/C Parser/Compile/Proof Sync/RefMan/XML） | GitHub Actions + kernelci.org | 借鉴 seL4 CI 矩阵思路（ES-SEL4-11） |

---

## 5. 设计哲学对比与融合裁决

### 5.1 Linux 演化式增量改进哲学

**哲学内核**：Linux 30+ 年的成功源于"演化式增量改进"——不追求完美设计，而是通过渐进式改进、向后兼容、可配置裁剪，让同一份源码服务于从嵌入式到服务器的全场景。

**工程体现**：
1. **目录演化**：28 顶层目录是 30 年演化的结果——`fs/`（文件系统）从最初到 ext4/btrfs/overlay，`net/`（网络栈）从 TCP/IP 到 eBPF/XDP，`io_uring/`（异步 I/O）是 5.1 引入的新顶层目录。目录随技术演进增量添加，不重构全局。
2. **Kconfig 可配置**：每个特性可开关（`Kbuild:65` `obj-$(CONFIG_IO_URING) += io_uring/`），同一份源码裁剪为嵌入式最小内核或服务器全功能内核。
3. **KABI 二进制兼容**：openEuler 通过 KABI 宏（`include/linux/kabi.h`）在不破坏二进制兼容性的前提下演进数据结构——`KABI_EXTEND` 新增字段、`KABI_BROKEN_INSERT_ENUM` 插入枚举、`KABI_USE` 填充预留空间。这是"演化式改进"的极致体现：即使 EEVDF 替代 CFS 这样的重大算法变更，也通过 `KABI_REPLACE`（`kernel/sched/sched.h:722-733`）保持二进制兼容。
4. **UAPI 永久稳定**：`include/uapi/linux/capability.h` 三版本共存（`_LINUX_CAPABILITY_VERSION_1/2/3`），30 年前的程序仍能运行。
5. **LSM 可插拔**：安全策略可插拔（`security/security.c` `ordered_lsm_init`），SELinux/Landlock/AppArmor 共存，不强制单一策略。

**优势**：生态可持续、向后兼容、渐进改进风险低。
**代价**：历史包袱、代码膨胀、设计一致性弱。

### 5.2 seL4 形式化验证驱动极简哲学

**哲学内核**：seL4 是世界上第一个功能正确性经过形式化证明的微内核。其设计哲学是"形式化验证驱动极简"——任何新增功能必须论证"无法在用户空间高效实现"，否则拒绝入内核；代码量必须可被形式化证明覆盖。

**工程体现**：
1. **极简代码量**：`src/kernel/` 仅 6 文件、`src/api/` 仅 2 文件、`src/object/` 11 文件——核心约 8700 行 C 代码，可被 Isabelle/HOL 证明覆盖。
2. **capability 单一权限模型**：所有权限通过 capability 表达（`src/object/cnode.c` Copy/Mint/Move/Mutate/Revoke/Delete），无隐式权限——形式化证明可覆盖全部权限流转。
3. **无动态分配**：内核无 kmalloc（形式化约束），untyped 内存预分配 + Retype 创建对象——避免形式化工具无法处理的动态数据结构。
4. **bitfield codegen + 证明**：`tools/bitfield_gen.py` 同时生成 C 代码 + Isabelle/HOL 规约 + 正确性证明——代码与证明同源生成。
5. **fastpath 优化但不破坏极简**：`src/fastpath/fastpath.c` 将最常见的 IPC 路径优化，但不增加内核功能——性能优化与极简可共存。
6. **compile_assert 一致性**：`src/api/faults.c:18` `compile_assert(InvalidRoot, ...)` 确保内核常量与 libsel4 一致——形式化证明的前置条件。

**优势**：可证明正确性、安全性高、设计一致性强。
**代价**：功能受限、生态小、开发成本高。

### 5.3 融合裁决：agent-linux 的"Linux 6.6 为基、seL4 为鉴"取向

**裁决原则**：agent-linux 的工程取向是"**Linux 6.6 为基、seL4 为鉴**"——以 OLK-6.6 工程思想为不可动摇的基线（编码风格、构建系统、并发模型、内存模型），以 seL4 微内核思想为架构层的借鉴来源（capability、消息传递、服务用户态化、形式化验证）。

**分层裁决**：

| 层次 | 取向 | 依据 |
|------|------|------|
| 编码风格层 | 完全采纳 OLK-6.6（Tab 8 / snake_case / 最小 typedef / K&R / 80 列 / errno + goto / kernel-doc） | 与 Linux 6.6 基线一致，便于 backport；seL4 的 4 空格/camelCase 源于 Haskell 形式化传统，与 C 生态格格不入 |
| 构建系统层 | 内核用 Kbuild（与 Linux 6.6 一致），非内核用 CMake（借鉴 seL4 ES-SEL4-10） | 内核态必须与上游 Linux 一致；非内核态 CMake 更现代 |
| 并发模型层 | OLK-6.6（spinlock/rcu + volatile 4 例外） | seL4 的"内核非抢占无并发"模型不适用于宏内核 |
| 内存模型层 | OLK-6.6（kmalloc + sizeof(*p) + strscpy） | seL4 的"无动态分配"源于形式化约束，不适用于宏内核 |
| 架构组织层 | **融合**——OLK-6.6 `arch/` 隔离 + 借鉴 seL4 `arch/machine/plat` 三层适配 | 取两者之长 |
| 安全模型层 | **融合**——OLK-6.6 LSM 钩子框架 + 借鉴 seL4 capability 派生模型 | LSM 保留可插拔策略，capability 提供权限派生 |
| IPC 层 | **融合**——OLK-6.6 io_uring + 借鉴 seL4 fastpath 热路径优化 | io_uring 为基，fastpath 优化思路借鉴 |
| 接口契约层 | **借鉴 seL4**——syscall.xml 式契约 XML + bitfield.bf codegen | OLK-6.6 无统一 XML 契约机制 |
| 形式化验证层 | **借鉴 seL4 思想**——tests-linux 子仓形式化验证框架 | 不引入全套 Isabelle/HOL，借鉴思想 |
| ABI 演进层 | **借鉴 OLK-6.6 KABI**——KABI 宏机制保持二进制兼容 | seL4 无此机制（极简内核无 ABI 演进问题） |

**裁决理由**：
1. **为何编码风格层完全采纳 OLK-6.6**：agent-linux 基于 Linux 6.6 内核基线，内核态代码必须与上游 Linux 一致，便于 backport 补丁。seL4 的 4 空格/camelCase/重度 typedef 源于其 Haskell 形式化传统，与 C/Unix 生态主流冲突，且 agent-linux 内核态代码无形式化约束。
2. **为何架构层借鉴 seL4**：seL4 的 `arch/machine/plat` 三层适配比 OLK-6.6 的单一 `arch/` 更精细，核心逻辑可独立演进。agent-linux 可借鉴此分层。
3. **为何安全层融合**：OLK-6.6 的 LSM 框架提供了策略可插拔性（SELinux/Landlock/AppArmor 共存），但 POSIX capabilities 是位掩码无派生树。seL4 的 capability 派生模型（Copy/Mint/Move/Mutate/Revoke/Delete）提供了更细粒度的权限控制。agent-linux 融合两者——LSM 框架保留 + capability 模块新增。
4. **为何 IPC 层融合**：OLK-6.6 的 io_uring 是成熟的异步 I/O 框架，seL4 的 fastpath 是热路径优化范式。agent-linux 以 io_uring 为基，借鉴 fastpath 的"常见路径快速处理、复杂路径降级"思路。
5. **为何接口契约层借鉴 seL4**：OLK-6.6 无统一的接口契约 XML 机制（UAPI 头文件是手写 C）。seL4 的 `syscall.xml` + `object-api.xml` + codegen 提供了"契约与实现分离"的范式，agent-linux 可借鉴此思路实现 SSoT。

---

## 6. 可落地的工程标准条目（新增/强化建议）

基于本次源码深度分析，提出以下 6 项可落地为工程标准的条目，标注优先级与对应 `50-engineering-standards/` 文件：

### 6.1 STD-KABI-01：引入 KABI 二进制兼容演进机制（P1）

**上游依据**：ES-OLK-14（`include/linux/kabi.h` + `lib/Kconfig.kabi`）

**现状**：agent-linux 无二进制兼容演进机制。微内核化改造会频繁变更数据结构（如 TCB、capability 表），可能导致内核态 ABI 破坏。

**建议**：在 `50-engineering-standards/` 新增 `09-kabi-evolution.md`，定义 agent-linux 的 KABI 宏机制（借鉴 OLK-6.6 `KABI_EXTEND`/`KABI_DEPRECATE`/`KABI_BROKEN_INSERT_ENUM`/`KABI_USE` 但不复制其实现）。新增字段必须追加到结构体末尾，废弃字段保留 hole。

**优先级**：P1（微内核化改造的关键基础设施，1.0.1 M1 落地）

**对应文件**：建议新增 `50-engineering-standards/09-kabi-evolution.md`。

### 6.2 STD-CODE-07：强化 sparse + W=1/2/3/e 分级警告集成（P1）

**上游依据**：ES-OLK-9（`Makefile:111-119` sparse + `scripts/Makefile.extrawarn` W 分级）

**现状**：`08-compliance-checklist.md` 已有 16 个检查脚本，但未明确 sparse + W 分级警告的集成要求。

**建议**：在 `01-coding-standards.md` 增补规则——CI 必须运行 `make C=1`（sparse 检查重编译文件）+ `make W=1`（相关警告）+ `make W=e`（警告即错误）三档。W=2/W=3 可选。

**优先级**：P1（CI 基础设施，1.0.1 M1 落地）

**对应文件**：`50-engineering-standards/01-coding-standards.md`（增补）+ `08-compliance-checklist.md`（增补检查规则）。

### 6.3 STD-DOC-18：引入 syscall.xml 式接口契约定义（P2）

**上游依据**：ES-SEL4-6（`libsel4/include/api/syscall.xml` + `tools/syscall_header_gen.py`）

**现状**：agent-linux 的 `30-interfaces/01-syscalls.md` 以 Markdown 描述系统调用接口，无机器可读契约。

**建议**：在 `50-engineering-standards/40-integration/` 新增 `syscall-contract.xml`，由 `scripts/syscall_gen.py` 自动生成 `include/uapi/airymax/syscall.h` + `kernel/entry/airymax_syscall_table.c`。XML 格式借鉴 seL4（`<syscalls>`/`<syscall name="..."/>`/`<param>`/`<error>`）但不复制其内容。

**优先级**：P2（R-01 建议，~16h，1.0.1 M1 落地）

**对应文件**：建议新增 `50-engineering-standards/40-integration/syscall-contract.xml`。

### 6.4 STD-CODE-08：[SC] 头文件位域定义必须经 bitfield_gen 生成（P2）

**上游依据**：ES-SEL4-8（`include/object/structures_64.bf` + `tools/bitfield_gen.py`）

**现状**：IRON-9 v2 [SC] 共享契约层 6 个头文件中的位域定义是手写 C 位域。

**建议**：在 `50-engineering-standards/40-integration/` 新增 `bitfield-contract.bf` 规范，定义 `.bf` DSL 格式，由 `scripts/bitfield_gen.py` 自动生成 C 结构体与访问函数。借鉴 seL4 `block`/`field`/`field_ptr`/`padding` 语法。

**优先级**：P2（R-02 建议，~12h，1.0.1 M1 落地）

**对应文件**：建议新增 `50-engineering-standards/40-integration/bitfield-contract.bf`。

### 6.5 STD-IRON-18：8 子仓落地 MAINTAINERS 文件（P2）

**上游依据**：ES-OLK-8（`MAINTAINERS` 24218 行）

**现状**：agent-linux 8 子仓无 MAINTAINERS 文件。

**建议**：为 8 子仓每个仓根目录新增 `MAINTAINERS` 文件，格式精简（`M:`/`S:`/`F:`/`W:` 四字段），每个子系统有明确责任人。

**优先级**：P2（R-03 建议，~8h，1.0.1 M5 落地）

**对应文件**：`120-development-process`（治理）+ 8 子仓 MAINTAINERS。

### 6.6 STD-TEST-09：建立 CI 多工具矩阵（P2）

**上游依据**：ES-SEL4-11（seL4 8 个 CI 工作流）+ ES-OLK-9（OLK sparse/W/checkpatch）

**现状**：agent-linux 的 CI 矩阵未明确。

**建议**：在 `80-testing` 定义 CI 多工具矩阵——(1) 编译检查（多编译器/多架构）；(2) 静态分析（sparse/smatch/cppcheck/coccinelle）；(3) 单元测试（KUnit）；(4) 集成测试（kselftest）；(5) 文档生成（`make htmldocs`）；(6) 契约一致性检查（syscall.xml / bitfield.bf）；(7) checkpatch 规范检查；(8) 形式化验证（tests-linux 子仓）。

**优先级**：P2（1.0.1 M3 落地）

**对应文件**：`80-testing` + `20-modules/08-tests.md`。

---

## 7. 与 v0.2.1 再检查结论的一致性

本报告与 v0.2.1 再检查报告（`00-reviews/_research_0.2.1/02-airymaxos-recheck-report.md`）的结论完全一致，并在此基础上深化：

| 维度 | v0.2.1 结论 | 本报告深化 |
|------|------------|-----------|
| 编码风格对齐（D1） | 16/16 全部对齐 | 通过源码证据确认（`coding-style.rst:359-443` typedef 5 规则 / `:526-598` goto 集中出口 / `:1140-1189` IS_ENABLED 条件编译） |
| OLK-6.6 工程思想覆盖（D2） | 12/13 覆盖，ES-OLK-8 MAINTAINERS 未落地（R-03） | 新增 ES-OLK-14（KABI 机制），建议 STD-KABI-01 落地 |
| seL4 架构层借鉴（D3） | 8/10 借鉴，ES-SEL4-6/8 未引入（R-01/R-02） | 通过源码证据确认（`syscall.xml` + `bitfield_gen.py` + Isabelle/HOL 证明），建议 STD-DOC-18/STD-CODE-08 落地 |
| 综合成熟度 | 100/100（A+，无条件 Go） | 维持。本次源码深度分析未发现阻断性问题，仅识别 6 项可落地工程标准条目（P1×2 + P2×4） |

**一致性结论**：本报告是 v0.2.1 研究的"源码级证据强化"，不改变 v0.2.1 的综合成熟度结论（100/100 A+ 无条件 Go），而是为工程标准的落地提供了源码级依据。

---

## 8. 结论与后续工作建议

### 8.1 结论

1. **源码级证据已完备**：本报告为 ES-OLK-1~13 + ES-SEL4-1~10 共 23 项工程思想补充了具体源码位置引用（`文件:行号` + 代码片段），将 v0.2.1 的"模式归纳"升级为"源码级证据"。

2. **新增 2 项工程思想**：ES-OLK-14（KABI 二进制兼容演进机制）、ES-SEL4-11（CI 多工具矩阵验证），均为 v0.2.1 遗漏的工程机制。

3. **设计哲学裁决明确**：agent-linux 取"Linux 6.6 为基、seL4 为鉴"取向——编码风格层/构建系统层/并发模型层/内存模型层完全采纳 OLK-6.6，架构组织层/安全模型层/IPC 层融合两者，接口契约层/形式化验证层借鉴 seL4。

4. **6 项可落地工程标准**：STD-KABI-01（KABI 机制，P1）/ STD-CODE-07（sparse+W 分级，P1）/ STD-DOC-18（syscall.xml 契约，P2）/ STD-CODE-08（bitfield codegen，P2）/ STD-IRON-18（MAINTAINERS，P2）/ STD-TEST-09（CI 矩阵，P2）。

5. **综合成熟度维持**：100/100（A+，无条件 Go）。本次源码深度分析未发现阻断性问题。

### 8.2 后续工作建议

| 优先级 | 编号 | 内容 | 建议落地时机 | 预估工时 |
|--------|------|------|-------------|---------|
| P1 | STD-KABI-01 | KABI 二进制兼容演进机制 | 1.0.1 M1 | ~20h |
| P1 | STD-CODE-07 | sparse + W=1/2/3/e 分级警告集成 | 1.0.1 M1 | ~8h |
| P2 | STD-DOC-18 | syscall.xml 式接口契约定义 | 1.0.1 M1 | ~16h |
| P2 | STD-CODE-08 | bitfield codegen | 1.0.1 M1 | ~12h |
| P2 | STD-IRON-18 | 8 子仓 MAINTAINERS 文件 | 1.0.1 M5 | ~8h |
| P2 | STD-TEST-09 | CI 多工具矩阵 | 1.0.1 M3 | ~16h |
| — | 合计 | 6 项工程标准 | 1.0.1 M1-M5 | ~80h |

**建议**：P1 两项（STD-KABI-01 / STD-CODE-07）是微内核化改造的基础设施，应在 1.0.1 M1 优先落地；P2 四项可在 1.0.1 M1-M5 增量落地，不影响 0.1.1 文档体系"无条件 Go"状态。

---

## 9. 附录：关键源码位置索引

### 9.1 seL4-master 关键源码位置

| 子系统 | 文件:行号 | 函数/内容 |
|--------|----------|----------|
| syscall 分发 | `src/api/syscall.c:557` | `handleSyscall()` |
| syscall 分发 | `src/api/syscall.c:97` | `handleUnknownSyscall()` |
| syscall 分发 | `src/api/syscall.c:580` | `case SysCall:` → `handleInvocation` |
| fault 处理 | `src/api/faults.c:18` | `compile_assert` 一致性检查 |
| fault 处理 | `src/kernel/faulthandler.c:21` | `handleFault()` (MCS) |
| fault 处理 | `src/kernel/faulthandler.c:34` | `sendFaultIPC()` |
| boot | `src/kernel/boot.c:30` | `get_p_reg_kernel_img_boot()` |
| boot | `src/kernel/boot.c:47` | `merge_regions()` |
| boot | `src/kernel/boot.c:67` | `reserve_region()` |
| 线程 | `src/kernel/thread.c` | `activateThread()` / `configureIdleThread()` |
| TCB 调度 | `src/object/tcb.c:30` | `checkPrio()` (MCP) |
| TCB 调度 | `src/object/tcb.c:115` | `tcbSchedEnqueue()` |
| TCB 调度 | `src/object/tcb.c:144` | `tcbSchedAppend()` |
| TCB 调度 | `src/object/tcb.c:173` | `tcbSchedDequeue()` |
| capability 操作 | `src/object/cnode.c:50` | `decodeCNodeInvocation()` |
| capability 操作 | `src/object/cnode.c:116` | `case CNodeCopy:` |
| capability 操作 | `src/object/cnode.c:136` | `case CNodeMint:` |
| capability 操作 | `src/object/cnode.c:157` | `case CNodeMove:` |
| capability 操作 | `src/object/cnode.c:195` | `case CNodeRevoke:` |
| capability 操作 | `src/object/cnode.c:200` | `case CNodeDelete:` |
| capability 操作 | `src/object/cnode.c:315` | `invokeCNodeRevoke()` |
| capability 操作 | `src/object/cnode.c:320` | `invokeCNodeDelete()` |
| capability 操作 | `src/object/cnode.c:528` | `cteRevoke()` |
| capability 操作 | `src/object/cnode.c:552` | `cteDelete()` |
| capability 派生 | `src/object/objecttype.c:62` | `deriveCap()` |
| capability 派生 | `src/object/objecttype.c:395` | `updateCapData()` |
| IPC endpoint | `src/object/endpoint.c:20` | `sendIPC()` |
| IPC endpoint | `src/object/endpoint.c` | `EPState_Idle/Send/Recv` |
| IPC notification | `src/object/notification.c:21` | `ntfn_ptr_get_queue()` |
| IPC notification | `src/object/notification.c:38` | `maybeDonateSchedContext()` |
| fastpath | `src/fastpath/fastpath.c:26` | `fastpath_call()` |
| fastpath | `src/fastpath/fastpath.c:46` | `slowpath(SysCall)` 降级 |
| exception 模型 | `include/api/failures.h:16-22` | `enum exception` (EXCEPTION_NONE/FAULT/LOOKUP_FAULT/SYSCALL_ERROR/PREEMPTED) |
| 结构定义 | `include/object/structures.h:8` | `#include <arch/object/structures_gen.h>` |
| 结构定义 | `include/object/structures.h:38` | `EP_PTR`/`NTFN_PTR`/`CTE_PTR` 宏 |
| bitfield DSL | `include/object/structures_64.bf:11` | `block null_cap` |
| bitfield DSL | `include/object/structures_64.bf:19` | `block untyped_cap` |
| bitfield DSL | `include/object/structures_64.bf:28` | `block endpoint_cap(...)` |
| syscall 契约 XML | `libsel4/include/api/syscall.xml` | `<syscalls>` / `<api-master>` / `<syscall name="Call"/>` |
| 对象 API 契约 XML | `libsel4/include/interfaces/object-api.xml` | `<api name="ObjectApi">` / `<method id="UntypedRetype">` |
| bitfield codegen | `tools/bitfield_gen.py:14-16` | "generating bitfield structures ... including Isabelle/HOL specifications and correctness proofs" |
| syscall codegen | `tools/syscall_header_gen.py:13-15` | "seL4 System Call ID Generator" / Jinja2 / XML |
| invocation codegen | `tools/invocation_header_gen.py` | invocation 头文件生成 |
| CMake 证明生成 | `CMakeLists.txt` | `GenProofsBFTarget` / `_proofs.thy` |
| libsel4 独立构建 | `libsel4/CMakeLists.txt:18-25` | `config_choice(LibSel4FunctionAttribute ...)` |
| CI 矩阵 | `README.md` | 8 个 CI badges (CII/CI/seL4Test/C Parser/Compile/Proof Sync/RefMan/XML) |

### 9.2 kernel-OLK-6.6 关键源码位置

| 子系统 | 文件:行号 | 函数/内容 |
|--------|----------|----------|
| 版本 | `Makefile:5-7` | `VERSION=6` / `PATCHLEVEL=6` / `SUBLEVEL=0` |
| sparse 检查器 | `Makefile:111-119` | `C=1` / `C=2` sparse 集成 |
| sparse 定义 | `Makefile:515` | `CHECK = sparse` |
| WERROR | `Makefile:853` | `KBUILD_RUSTFLAGS-$(CONFIG_WERROR) += -Dwarnings` |
| W= 分级 | `Makefile:1676-1689` | `W=1/2/3/e` help |
| Kbuild 构建规则 | `Kbuild:48-72` | `obj-y += kernel/` / `obj-$(CONFIG_IO_URING) += io_uring/` |
| Kbuild 生成检查 | `Kbuild:23-46` | `bounds-file` / `timeconst-file` / `offsets-file` / `missing-syscalls` / `atomic-checks` (sha1) |
| Kconfig 顶层 | `Kconfig:1-33` | `mainmenu` / `source "init/Kconfig"` / `source "lib/Kconfig.openeuler"` |
| EEVDF avg_vruntime | `kernel/sched/fair.c:925` | `avg_vruntime()` |
| EEVDF entity_lag | `kernel/sched/fair.c:973` | `entity_lag()` (lag 计算) |
| EEVDF vruntime_eligible | `kernel/sched/fair.c:1012` | `vruntime_eligible()` |
| EEVDF entity_eligible | `kernel/sched/fair.c:1057` | `entity_eligible()` (含 BPF 钩子) |
| EEVDF pick_eevdf | `kernel/sched/fair.c:1252` | `pick_eevdf()` (O(log n) 增强红黑树) |
| KABI 宏使用 | `kernel/sched/sched.h:722-733` | `KABI_REPLACE` / `KABI_BROKEN_REMOVE` (EEVDF 引入) |
| BPF 调度钩子 | `kernel/sched/fair.c:1059-1064` | `#ifdef CONFIG_BPF_SCHED` / `bpf_sched_cfs_tag_entity_eligible` |
| sched_ext | `kernel/sched/ext.c` | 可编程调度器 |
| fork EXPORT_SYMBOL | `kernel/fork.c:656` | `EXPORT_SYMBOL(free_task)` |
| fork EXPORT_SYMBOL_GPL | `kernel/fork.c:992` | `EXPORT_SYMBOL_GPL(__mmdrop)` |
| MGLRU | `mm/vmscan.c` | LRU_GEN 多代 LRU |
| openEuler gmem | `mm/gmem.c` / `mm/gmem_phys.c` | guest 内存 |
| openEuler etmem | `mm/etmem.c` | etmem 内存增强 |
| POSIX capabilities | `security/commoncap.c:66` | `cap_capable()` |
| POSIX capabilities | `security/commoncap.c:242` | `cap_capset()` |
| SELinux LSM hooks | `security/selinux/hooks.c:7009-7019` | `LSM_HOOK_INIT(binder_set_context_mgr, ...)` 等 |
| SELinux hook 数 | `security/selinux/hooks.c` | 215 个 `LSM_HOOK_INIT` |
| LSM stacking | `security/security.c:93` | `ordered_lsm_init()` |
| UAPI capability | `include/uapi/linux/capability.h:17-33` | `_LINUX_CAPABILITY_VERSION_3` / `__u32` |
| UAPI 许可证 | `include/uapi/linux/capability.h:1` | `GPL-2.0 WITH Linux-syscall-note` |
| UAPI 目录 | `include/uapi/` | 14 子目录 / `include/uapi/linux/` 584 文件 |
| KABI 宏定义 | `include/linux/kabi.h:1-80` | `KABI_EXTEND` / `KABI_DEPRECATE` / `KABI_BROKEN_INSERT_ENUM` / `KABI_USE` |
| KABI 实际使用 | `include/linux/bpf.h:321` | `KABI_BROKEN_REPLACE` |
| KABI 实际使用 | `include/linux/bpf.h:336-337` | `KABI_USE(1, ...)` / `KABI_USE(2, ...)` |
| KABI 实际使用 | `include/linux/bpf.h:721` | `KABI_BROKEN_INSERT_ENUM` |
| KABI Kconfig | `lib/Kconfig.kabi:1-30` | `KABI_COMPAT` / `KABI_RESERVE` / `KABI_SIZE_ALIGN_CHECKS` |
| openEuler Kconfig | `lib/Kconfig.openeuler` | `KWORKER_NUMA_AFFINITY` 等 |
| checkpatch | `scripts/checkpatch.pl:14` | v0.32，72 个规则子例程 |
| W= 警告定义 | `scripts/Makefile.extrawarn:1-80` | W=1/2/3/e 四组警告 flag |
| coding-style | `Documentation/process/coding-style.rst:18` | 第 1 章 Indentation (Tab 8) |
| coding-style | `Documentation/process/coding-style.rst:359-443` | 第 5 章 Typedefs (5 规则 a-e) |
| coding-style | `Documentation/process/coding-style.rst:526-598` | 第 7 章 Centralized exiting (goto) |
| coding-style | `Documentation/process/coding-style.rst:1140-1189` | 第 21 章 Conditional Compilation (IS_ENABLED) |
| coding-style | `Documentation/process/coding-style.rst:1189` | 第 22 章 Do not crash the kernel |
| MAINTAINERS | `MAINTAINERS` | 24218 行，M/R/L/S/W/Q/B/C/P/T/F/X 字段 |
| dev-tools 文档 | `Documentation/dev-tools/` | checkpatch/sparse/coccinelle/kasan/kcov/kcsan/kfence/kmemleak/kmsan/kselftest/ubsan |

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
