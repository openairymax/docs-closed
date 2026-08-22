SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 21 — openEuler 工程标准与工程思想研究（第三轮）

> **文档定位**：agent-linux 内核设计深度对比研究 · 第三轮 · openEuler 工程标准研究
> **研究主体**：openEuler kernel-OLK-6.6（`/home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6`）
> **最后更新**：2026-08-01
> **方法论**：逐字节阅读源码与工程文档，所有引用标注文件路径+行号，严禁编造
> **研究目的**：提炼 openEuler（Linux 6.6 OLK）的工程标准体系与工程思想，为极境内核工程标准建设提供参照系

---

## 0. 摘要

openEuler OLK-6.6 是 vanilla Linux 6.6.0 + openEuler 深度定制。其工程标准体系完整继承上游 Linux（代码风格/提交流程/测试/锁/内存序），openEuler 特有实践集中在 **KABI 兼容层** 与 **华为硬件子系统（UB/URMA/xSched/UMMU）**。核心研究结论：openEuler 的工程思想是"**不另起炉灶，在 vanilla 之上叠加可维护的二进制兼容层**"——KABI 宏体系（[kabi.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/kabi.h) L335-507）实现了"稳定性靠预留而非承诺"的工程化，为极境内核的 UAPI/syscall 预留体系提供了最直接的参照模板。

---

## 1. KABI 工程标准（openEuler 最大特色）

### 1.1 KABI 体系架构

openEuler 从 RHEL 的 `rh_kabi.h` 移植并去品牌化（[kabi.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/kabi.h) L26-27 注释明确注明 *"The macro helpers are derived from RHEL include/linux/rh_kabi.h. Mostly debrand from RHEL."*），建立"宏 + genksyms 双面展开 + 工具链校验"三层防护：

| 组件 | 文件 | 行号 | 作用 |
|------|------|------|------|
| 核心宏 | `include/linux/kabi.h` | L335/L359 | `__GENKSYMS__` 双面宏（生成 checksum 时展开为空/原始，构建时展开为真实代码） |
| Kconfig | `lib/Kconfig.kabi` | L2/L17/L26 | `CONFIG_KABI_COMPAT`/`KABI_RESERVE`/`KABI_SIZE_ALIGN_CHECKS` |
| 工具链 | `scripts/kabideps` | L4-8 | 生成模块引用符号表，对照 Module.kabi 检查 |
| 工具链 | `scripts/kabisyms` | L4-15 | 生成 kABI baseline（输出 Module.kabi） |
| 工具链 | `scripts/check-kabi` | L4-8 | Red Hat kABI 参考校验工具（Jon Masters, 2007-2009） |

### 1.2 KABI 预留宏体系（极境内核最值得借鉴的工程机制）

| 宏 | 行号 | 语义 |
|----|------|------|
| `KABI_RESERVE(n)` | L439 | 预留 8 字节槽（`u64 kabi_reserved##n`），编号从 1 起、须在 kABI freeze 前使用 |
| `KABI_USE(n, _new)` | L443 | 事后用新字段替换预留槽 |
| `KABI_USE2` | L448 | 双字段替换 |
| `KABI_EXTEND(_new)` | L365 | 结构体末尾扩展（不破坏既有布局） |
| `KABI_EXTEND_WITH_SIZE` | L452 | 带尺寸校验的扩展 |
| `KABI_FORCE_CHANGE(ver)` | L341 | 强制改变 checksum（最后手段，阻止第三方模块静默加载） |
| `KABI_EXCLUDE` | L450 | 危险宏：从 checksum 排除字段，必须配对 KABI_FORCE_CHANGE |
| `KABI_AUX_PTR/EMBED/USE_AUX_PTR` | L459-507 | 辅助结构模式（事后扩展 + 尺寸检查） |
| `KABI_SIZE_ALIGN_CHECKS` | L380-390 | 编译期 `_Static_assert` 强制新字段 ≤ 原字段且对齐一致 |

**架构差异化 KABI 处理**：[sched.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/sched.h) L1668-1684——x86 用 `KABI_BROKEN_INSERT(struct sched_ext_entity scx)`、arm64 用 `KABI_EXTEND(...)`，均限定 `!defined(__GENKSYMS__)`（genksyms 计算 checksum 时"看不见"该字段）。注释（L1662-1667）解释 x86 上 thread_struct 变长导致"必须置尾"的约束。

### 1.3 工程思想提炼：稳定性靠预留而非承诺

**金句 1**：kABI 兼容不在事后修补，而在冻结期前预埋扩展点——`KABI_RESERVE`（[kabi.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/kabi.h) L439）留 8 字节槽，事后用 `KABI_USE` 消费（L443）；不能预留的结构用 `KABI_AUX` 辅助结构 + 尺寸校验事后扩展（L459-507）。

**与极境内核的对比**：极境内核的 syscall 24 槽预留（[syscalls.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/syscalls.h) L26-29：548-551 核心 + 552-571 预留）与 openEuler KABI_RESERVE 思想同构，但 openEuler 有"宏双面展开 + genksyms 隐藏 + 编译期 size/align 断言"三层防护，极境内核目前只有"编号规划"一层。**建议引入 KABI_USE 式"预留 → 消费"登记机制**：在 [SC] syscalls.h 中为 552-571 预留槽定义"消费即显式登记"的编译期宏（对应第三轮 E1 的 compile_assert 机制）。

---

## 2. UAPI 稳定性工程

### 2.1 UAPI 与 kABI 的边界（Linux 工程契约核心）

[stable-api-nonsense.rst](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/Documentation/process/stable-api-nonsense.rst)：

- L10-11：*"Linux does not have a binary kernel interface, nor does it have a stable kernel interface"*——指内核**内部**接口。
- L13-23：内核到用户空间的 syscall 接口 *"very stable over time, and will not break"*。
- L26-34：Executive Summary——"你想要的不是稳定内核接口，而是稳定运行的驱动，唯一途径是进主线树"。

**工程思想金句 2**：稳定性承诺的边界是工程契约的核心——UAPI 绝对稳定、kABI 明确不承诺。极境内核的 OS-IRON-001/002（[04-engineering-philosophy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/04-engineering-philosophy.md) L102-128）完整继承此边界，且扩展为 4 层分级（L130-161），方向正确。

### 2.2 UAPI 目录组织

- `include/uapi/linux/`：标准 UAPI 头；openEuler 特有 `include/uapi/linux/xsched/`（`xcu_vstream.h`、`types.h`）与 `include/uapi/linux/ummu_core.h`。
- `include/uapi/asm-generic/`：架构无关定义（`unistd.h` 含 `__NR3264_*` 兼容宏，L87-138）。
- 顶层 Makefile L1245-1246：`asm-generic` UAPI 头自动生成机制。

**openEuler 特有实践**：`include/uapi/linux/xsched/xcu_vstream.h` L13-14 自研 `KABI_RESERVE_BYTES(idx, n)` 宏（`__u8 __kabi_reserved_##idx[n]`），在 ioctl 结构体 `vstream_alloc_args_t`（L31-38）预留字节——**把 kABI 预留思想移植到 UAPI 结构**。这是极境内核 [SC] 头文件可借鉴的直接范例（UAPI 结构体也应有预留扩展点）。

---

## 3. 代码风格与检查工具

### 3.1 checkpatch：工具固化标准

- [checkpatch.pl](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/scripts/checkpatch.pl) L21 版本 `V = '0.32'`；L30 `chk_signoff = 1`（强制 Signed-off-by 检查）、L31 `chk_fixes_tag = 1`（强制 Fixes 标签检查）；支持 `.checkpatch.conf`（L59）。
- [checkpatch.rst](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/Documentation/dev-tools/checkpatch.rst) L11-13 金句：*"Checkpatch is not always right. Your judgement takes precedence over checkpatch messages."*

### 3.2 coding-style 与 SPDX

- [coding-style.rst](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/Documentation/process/coding-style.rst) L18-39：8 字符 tab 缩进（L22-24 "4 字符缩进运动等于把 π 定义为 3"）；超过 3 层嵌套说明代码结构有问题（L33-35）。
- [spdxcheck.py](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/scripts/spdxcheck.py)：license 语法校验（L47-50 读 LICENSES/ 目录），配套 `spdxcheck-test.sh`。
- 配套：`.clang-format`、`.rustfmt.toml`、`.cocciconfig`。

**工程思想金句 3**：用工具固化标准，同时承认"工具不总是对的，工程师判断优先"。

**与极境内核的对比**：极境内核采用 Linux 风格（[03-microkernel-strategy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) L502-512），checkpatch 纳入 CI 门禁（[08-threat-model.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/08-threat-model.md) L369-376）。对齐充分。

---

## 4. 内核开发流程文档（提交规范）

[submitting-patches.rst](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/Documentation/process/submitting-patches.rst) 是 Linux 提交规范 SSoT：

| 规则 | 行号 | 内容 |
|------|------|------|
| 描述 why | L48-52 | 必须描述底层问题（why），非 what |
| 一个补丁一个问题 | L81 | *"Solve only one problem per patch"* |
| 祈使句 | L94-97 | commit message 用 imperative mood |
| 引用 commit | L99-113 | ≥12 字符 hash + oneline summary（L104-107 示例） |
| Closes 标签 | L138-143 | 禁止私有 bug tracker |
| Fixes 标签 | L146-151 | 12 字符 hash、不拆行、豁免 75 列规则 |
| 逻辑变更分离 | L166-171 | *"Separate each logical change into a separate patch"* |
| Co-developed-by | L489-497 | 必须紧随对应 Signed-off-by |
| 审查标签 | L525-548 | Reported-by/Tested-by/Reviewed-by + Reviewer's statement |
| canonical patch format | L603-635 | `Subject: [PATCH 001/123] subsystem: summary`（L615）；正文 75 列（L622）；`---` 分隔（L630） |

**工程思想金句 4**：commit message 是机器可解析的承诺——`Fixes:` 12 字符 hash、tags 豁免 75 列不拆行，是为了让解析脚本与 bug tracker 自动处理。

**与极境内核的对比**：极境内核的提交规则（[04-engineering-philosophy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/04-engineering-philosophy.md) L396-447：OS-KER-067 Fixes 标签、OS-KER-068 DCO 链、多审查标签）与 Linux 完全对齐。且 workspace 规则（git-commit-message.md）已对照 submitting-patches.rst 编写。

---

## 5. MAINTAINERS 治理

- [MAINTAINERS](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/MAINTAINERS) L7-48：条目标签语义（M 维护者/R reviewer/L 列表/S 状态/F 文件通配/N regex 匹配）。
- [get_maintainer.pl](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/scripts/get_maintainer.pl) L17 版本 0.26：`perl scripts/get_maintainer.pl [OPTIONS] <patch>` 自动推荐审查者。
- `.get_maintainer.ignore`：忽略历史邮箱。

**工程思想金句 5**：治理机械化为可执行工具（get_maintainer 自动推荐审查者），减少"补丁无人审"的漂移。

**与极境内核的对比**：极境内核采纳 MAINTAINERS 模式（[03-microkernel-strategy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) L560-568，R-03 建议 8 子仓各含 MAINTAINERS）。

---

## 6. 测试工程

### 6.1 KUnit（内核单元测试）

- [lib/kunit/](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/lib/kunit/) 完整存在（21 个文件）。
- [kunit-example-test.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/lib/kunit/kunit-example-test.c) L22-31：`KUNIT_EXPECT_EQ(test, 1+1, 2)` 期望式断言。
- [kunit/index.rst](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/Documentation/dev-tools/kunit/index.rst) L26-33：结果以 **KTAP** 格式输出，受 JUnit/Python unittest.mock/GoogleTest 启发。

### 6.2 kselftest

- [tools/testing/selftests/](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/tools/testing/selftests/)：`Makefile` 以 `TARGETS += alsa/bpf/cgroup/...` 注册（L2-40）；含 `kselftest_harness.h`、`lib.mk`、`run_kselftest.sh`。

**与极境内核的对比**：极境内核已有 KUnit 先例——[airy_ipc_ring_test.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/corekern/ipc/airy_ipc_ring_test.c)、[stc_dispatch_test.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/corekern/sched/stc_dispatch_test.c)、[airy_cap_derive_test.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap_derive_test.c)、[airy_lsm_test.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_lsm_test.c) 四个测试文件已存在，与 openEuler KUnit 模式一致。

---

## 7. 安全工程

- [security-bugs.rst](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/Documentation/process/security-bugs.rst) L14-16：漏洞上报 `security@kernel.org`（私密列表）；L36-52 embargo 规则（修复发布可推迟 7 日历日，经同意延长至 14 天；embargo 信息永久保密）。
- [embargoed-hardware-issues.rst](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/Documentation/process/embargoed-hardware-issues.rst) L9-18：硬件漏洞需跨厂商协调。
- [deprecated.rst](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/Documentation/process/deprecated.rst)：维护弃用 API 清单。

**工程思想金句 6**：安全披露有严格的 embargo 纪律——修复发布可推迟、细节永久保密，为部署协调留窗口。

**与极境内核的对比**：极境内核 [08-threat-model.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/08-threat-model.md) L401-438 有完整漏洞响应流程（私密报告/CVSS v3.1/协调披露 + 90 天宽限期），与 Linux 对齐。

---

## 8. 锁与并发工程

### 8.1 lockdep（运行时锁序校验）

- [spinlock.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/spinlock.h) L63 `#include <linux/lockdep.h>`（lockdep 内建）。
- [lockdep.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/lockdep.h)：`struct lock_class`（L50-51）、`lockdep_register_key`（L176）、`lockdep_set_class`（L214）——锁类注解体系。
- [kernel/locking/](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/locking/)：33 个文件（lockdep.c/qspinlock.c/qrwlock.c/mutex.c/rwsem.c/rtmutex.c/osq_lock.c 等）。
- [Documentation/locking/](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/Documentation/locking/)：18 个文档（lockdep-design/lockstat/locktypes/spinlocks/mutex-design 等）。

### 8.2 内存序工程

- [barrier.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/asm-generic/barrier.h) L29-51：`mb/rmb/wmb` 包裹 **KCSAN 插桩**（`kcsan_mb()` 等）——并发原语带动态检测。
- [memory-barriers.txt](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/Documentation/memory-barriers.txt) L14-21 金句：*"This document is not a specification"*——疑问以 `tools/memory-model/` 形式化模型为准。
- [tools/memory-model/](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/tools/memory-model/)：`linux-kernel.cat`/`linux-kernel.bell`/`linux-kernel.def`——Linux 内核内存一致性的**形式化模型**（数学化验证工具链）。

**工程思想金句 7**：并发正确性由三层保障——编译期（lockdep 静态注解）、运行时（lockdep 动态校验锁序 + KCSAN 数据竞争检测）、数学层（tools/memory-model 形式化模型）。barrier 宏内建 KCSAN 插桩（[barrier.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/asm-generic/barrier.h) L29-51）。

**与极境内核的对比**：极境内核第二轮 N10（[airy_locking.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/corekern/locking/airy_locking.c) 无 RCU wrapper）表明其 lockdep/KCSAN 依赖 Linux 内建（LOCKDEP 是 Kconfig 全局开关，不用 wrapper），但锁类注解（lockdep_set_class）在 airy 代码中零使用——建议对 per-bucket 锁（[airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap.h) L52-56）与全局锁添加 lockdep 注解，使锁序错误在开发期暴露。

---

## 9. 构建工程

- 顶层 [Makefile](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/Makefile) L1-6：`VERSION = 6`/`PATCHLEVEL = 6`/`SUBLEVEL = 0`/`NAME = Hurr durr I'ma ninja sloth`。
- L1252 `include $(srctree)/Makefile.oever`（openEuler 版本变量挂载点）；L1279-1284 将 `OPENEULER_LTS/MAJOR/MINOR` 生成进 version.h。
- [Makefile.oever](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/Makefile.oever)（openEuler 特有，5 行）：`OPENEULER_LTS = 0`/`OPENEULER_MAJOR = 9999`/`OPENEULER_MINOR = 0`（源码树占位值，构建时外部注入）。
- [Kbuild](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/Kbuild) L10-30：`bounds.h`/`timeconst.h`/`asm-offsets.h` 自动生成（`filechk_offsets` 机制）。
- [scripts/Makefile.build](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/scripts/Makefile.build) L6-30：统一初始化 kbuild 变量（防环境变量污染）。

**工程思想金句 8**：发行版版本号独立于内核 VERSION 体系（`Makefile.oever`），由构建系统注入——发行版工程与内核工程解耦。

---

## 10. openEuler 特有工程实践总结（与 vanilla 6.6 差异）

| 差异点 | 证据 | 性质 |
|--------|------|------|
| KABI 抽象层（最大差异） | [kabi.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/kabi.h)（509 行）+ [lib/Kconfig.kabi](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/lib/Kconfig.kabi) | 源自 RHEL，三层防护（宏双面 + genksyms 隐藏 + size/align 断言） |
| KABI 工具链 | scripts/kabideps、scripts/kabisyms、scripts/check-kabi | 构建期/发布期生成 KABI baseline 并 diff 校验 |
| 版本变量文件 | [Makefile.oever](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/Makefile.oever) | 发行版本号独立于内核 VERSION |
| UB 子系统（华为硬件） | `drivers/ub/`（ubus/urma/ubcore/ubfi/obmm/cdma/sentry）+ `include/ub/ubus.h`（L9 直接 include kabi.h） | HiSilicon 硬件总线/URMA 网络栈 |
| xSched UAPI | `include/uapi/linux/xsched/xcu_vstream.h`（L13-14 KABI_RESERVE_BYTES） | 加速器调度专用 UAPI，自带 KABI 预留 |
| UMMU UAPI | `include/uapi/linux/ummu_core.h` L3 | 统一内存管理单元用户接口 |
| 架构级 KABI 处理 | [sched.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/sched.h) L1668-1684 | x86 KABI_BROKEN_INSERT / arm64 KABI_EXTEND 差异化插 sched_ext |
| SCSI 等子系统预留 | `include/scsi/scsi_eh.h` L46-47、`scsi_transport_fc.h` L387-406（20 个预留槽） | 冻结期前预埋扩展点 |

其余（checkpatch、spdxcheck、KUnit、selftests、lockdep、memory-barriers、MAINTAINERS、submitting-patches、Kbuild）均与 vanilla 6.6 一致——**openEuler 不另起炉灶**。

---

## 11. 对极境内核的借鉴结论

### 11.1 openEuler 工程思想 8 条金句

1. **"UAPI 永不破坏、kABI 明确不承诺"**——稳定性承诺的边界是工程契约的核心（stable-api-nonsense.rst L10-23）。
2. **"稳定性靠预留而非承诺"**——KABI_RESERVE 预埋扩展点，事后 KABI_USE 消费（kabi.h L439/L443）。
3. **"每个 commit 一个逻辑变更"**——保证 git bisect 可用（submitting-patches.rst L81）。
4. **"机器可解析的承诺"**——Fixes 12 字符 hash、tags 不拆行（L146-151）。
5. **"流程文档化即治理"**——1.Intro→8.Conclusion 系列文档 + Reviewer's Statement（L545-548）。
6. **"用工具固化标准"**——checkpatch/spdxcheck/get_maintainer/kabideps 全部机械化，同时承认工具不总是对（checkpatch.rst L11-13）。
7. **"并发正确性三层保障"**——lockdep 静态注解 + 运行时校验 + tools/memory-model 形式化模型。
8. **"企业发行版的工程桥梁是抽象层"**——KABI 宏在 vanilla 之上搭建二进制兼容层，技术债显式登记（kabi.h L21-24 注释要求补丁说明"为什么这样用合法"）。

### 11.2 极境内核可借鉴项（补充第三轮改进清单）

| 编号 | 借鉴点 | 极境内核落点 |
|------|--------|-------------|
| E14 | KABI_USE 式"预留→消费"登记机制 | [syscalls.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/syscalls.h) L26-29 的 20 预留槽引入显式消费宏 + 编译期断言 |
| E15 | KABI_RESERVE_BYTES 式 UAPI 结构体预留 | [SC] 头文件结构体（如 [ipc.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/ipc.h) 128B 消息头）末尾预留扩展字节 |
| E16 | lockdep_set_class 锁类注解 | [airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap.h) L52-56 per-bucket 锁 + [airy_object.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/corekern/object/airy_object.c) 全局锁添加锁类，使锁序错误开发期暴露 |
| E17 | 构建期 KABI baseline diff 校验 | 极境内核 [SC] 头文件三方一致性（syscalls.h L8-12）引入"登记表 diff"脚本（当前靠 CI 手动比对） |

### 11.3 正面确认

极境内核已在多个工程维度对齐 openEuler：提交规范（Fixes/DCO/审查标签）、MAINTAINERS 治理、KUnit 测试（4 个 *_test.c 文件）、安全披露流程（CVSS + 协调披露）、UAPI 编译器无关（OS-IRON-016，比 openEuler 更进一步——openEuler 的 UAPI 仍用 `__aligned` 编译器扩展）。工程标准层面无方向性差距，差距集中在"预留机制工程化"（E14/E15）与"锁类注解"（E16）。

---

## 12. 小结

openEuler 工程思想的精髓是"**不破坏上游标准，用抽象层搭建企业级兼容桥梁**"——KABI 宏体系、UAPI 预留、工具链校验构成一个完整的三层防护闭环。极境内核作为 Linux 衍生工程，其工程标准已与 Linux/openEuler 高度对齐（提交/治理/测试/安全），最值得借鉴的是 openEuler 的**预留机制工程化**：KABI_RESERVE→KABI_USE 的"预留→消费"登记模型（E14）、UAPI 结构体预留字节（E15）、构建期 baseline diff（E17）。这三项与第三轮 E1（compile_assert）共同构成极境内核"接口稳定性三层防护"（预留登记 + 编译期断言 + CI diff）的完整闭环。
