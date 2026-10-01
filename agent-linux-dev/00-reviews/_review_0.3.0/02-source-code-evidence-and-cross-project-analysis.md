Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agent-linux v0.3.0 源码级证据与跨项目一致性分析

> **文档定位**：本文件是 `00-reviews/_review_0.3.0/01-comprehensive-review-report.md` 的配套证据文档，提供 P0 问题的源码级证据、OLK-6.6 与 seL4 工程思想的完整源码位置索引、以及 AirymaxRT ↔ AirymaxOS 跨项目一致性分析。\
> **报告版本**：v0.3.0\
> **审查日期**：2026-07-10\
> **机密级别**：闭源不公开（SPHARX Ltd 内部参考）

---

## 目录

- [第 1 章 P0 问题源码级验证证据](#第-1-章-p0-问题源码级验证证据)
- [第 2 章 OLK-6.6 工程思想源码位置索引（ES-OLK-1~14）](#第-2-章-olk-66-工程思想源码位置索引es-olk-114)
- [第 3 章 seL4 工程思想源码位置索引（ES-SEL4-1~11）](#第-3-章-sel4-工程思想源码位置索引es-sel4-111)
- [第 4 章 AirymaxRT ↔ AirymaxOS 跨项目一致性分析](#第-4-章-airymaxrt--airymacos-跨项目一致性分析)
- [第 5 章 6 项可落地工程标准](#第-5-章-6-项可落地工程标准)

---

## 第 1 章 P0 问题源码级验证证据

### 1.1 P0-05: POSIX capability 数量与 ID 冲突——源码验证

**验证命令**：

```bash
# 统计 OLK-6.6 capability.h 中的 #define CAP_ 数量
$ grep -c "^#define CAP_" 01Reference/kernel-OLK-6.6/include/uapi/linux/capability.h
44
```

**说明**：44 行 `#define CAP_` 中，去除版本宏（`_LINUX_CAPABILITY_VERSION_*`）和工具宏（`CAP_LAST_CAP`、`cap_valid`、`CAP_TO_MASK`、`CAP_TO_INDEX`），实际 capability 定义为 **41 个**（编号 0-40）。

**关键源码**（OLK-6.6 `include/uapi/linux/capability.h`）：

```c
/* line 381 */
#define CAP_PERFMON          38

/* line 412 */
#define CAP_BPF              39

/* line 419 */
#define CAP_CHECKPOINT_RESTORE 40

/* line 421 */
#define CAP_LAST_CAP         CAP_CHECKPOINT_RESTORE
```

**AirymaxOS 冲突定义**（`50-engineering-standards/120-cross-project-code-sharing.md:149-151`）：

```c
#define AIRYMAX_CAP_AGENT_SPAWN    38    /* 与 CAP_PERFMON(38) 冲突 */
#define AIRYMAX_CAP_GPU_SCHED      39    /* 与 CAP_BPF(39) 冲突 */
#define AIRYMAX_CAP_NPU_ACCESS     40    /* 与 CAP_CHECKPOINT_RESTORE(40) 冲突 */
```

**AirymaxOS 文档错误描述**（`110-security/03-capability-model.md:276`）：

> "对齐 `security_types.h`（[SC] 共享头文件）定义的 POSIX capability 38 ID 枚举。agent-linux 在 Linux 6.6 标准 40 个 POSIX capability 基础上，整合为 38 个有效枚举（排除 2 个已废弃）"

**事实纠正**：
1. Linux 6.6 有 **41 个** POSIX capability（0-40），**不是 40 个**
2. **没有已废弃的 capability**——所有 41 个都是有效的
3. AirymaxOS 自定义 capability 不应占用 38/39/40——这些编号已被 Linux 使用

---

### 1.2 P0-06: LSM 钩子数量——源码验证

**验证命令**：

```bash
# 统计 OLK-6.6 lsm_hook_defs.h 中的 LSM_HOOK( 数量
$ grep -c "LSM_HOOK(" 01Reference/kernel-OLK-6.6/include/linux/lsm_hook_defs.h
252
```

**AirymaxOS 文档错误描述**：
- `50-engineering-standards/120-cross-project-code-sharing.md:153`："LSM hook IDs (254 total)"
- `110-security/03-capability-model.md:846`："LSM 钩子 254 ID 枚举"
- 全仓 31 处引用"254"

**事实纠正**：实际为 **252 个** `LSM_HOOK(` 定义，文档声称 254，差 2 个。

---

### 1.3 P0-10: `__GFP_PMEM` 不存在——源码验证

**验证命令**：

```bash
# 在 OLK-6.6 全量源码中搜索 __GFP_PMEM
$ grep -r "__GFP_PMEM" 01Reference/kernel-OLK-6.6/
→ 0 个匹配

# 搜索 openEuler 实际使用的持久内存 GFP 标志
$ grep -r "__GFP_RELIABLE" 01Reference/kernel-OLK-6.6/include/linux/gfp_types.h
→ include/linux/gfp_types.h:257: #define __GFP_RELIABLE ((__force gfp_t)___GFP_RELIABLE)
```

**AirymaxOS 错误引用**：
- `50-engineering-standards/120-cross-project-code-sharing.md:134`：`#define AIRYMAX_GFP_PMEM (__GFP_HIGH)` —— 虽然此处用 `__GFP_HIGH` 而非 `__GFP_PMEM`，但注释和命名暗示 PMEM 应有专属 GFP 标志
- 其他多处文档引用 `__GFP_PMEM` 作为概念性标志名

**事实纠正**：openEuler 使用 `__GFP_RELIABLE`（受 `CONFIG_MEMORY_RELIABLE` 控制）作为可靠内存分配标志，不存在 `__GFP_PMEM`。

---

### 1.4 P0-11: `ring_fd.ring_fd` 编译错误——源码验证

**错误代码位置**：`170-performance/03-ipc-performance.md:162`

```c
/* 结构体定义（同文件 :219-224）*/
struct agentrt_ipc_ring {
    struct io_uring ring;
    int ring_fd;            /* ← ring_fd 是 int 类型 */
    __u32 submit_pending;
    __u32 batch_count;
};

/* 错误代码（:161-162）*/
io_uring_prep_rw(IORING_OP_AGENTRT_IPC_REGISTER_REGION, sqe,
                 ring_fd.ring_fd, NULL, 0, 0);
                 ^^^^^^^^^^^^^^^^
                 /* 错误：ring_fd 是 int，不是 struct，不能用 . 成员访问 */
```

**正确代码**：

```c
io_uring_prep_rw(IORING_OP_AGENTRT_IPC_REGISTER_REGION, sqe,
                 r->ring_fd, NULL, 0, 0);
                 /* r 是 struct agentrt_ipc_ring *，通过 -> 访问 ring_fd 成员 */
```

---

### 1.5 SCHED_EXT=7 验证（上一轮问题已修复确认）

**验证命令**：

```bash
$ grep "SCHED_EXT" 01Reference/kernel-OLK-6.6/include/uapi/linux/sched.h
#define SCHED_EXT        7
```

**AirymaxOS 当前状态**：
- `30-interfaces/01-syscalls.md:373`：明确写"`SCHED_AGENT` 宏禁用"
- `160-compatibility/02-posix-compat.md:252-253`：明确写"复用内核 SCHED_EXT=7 调度类编号，禁止定义 SCHED_AGENT 宏。SCHED_AGENT 仅作为 sched_ext BPF 策略名称（字符串），非调度类编号"

**结论**：✅ 已修复。SCHED_AGENT 宏已清零，统一使用 SCHED_EXT=7。

---

### 1.6 `__s128` 类型存在性验证（上一轮误报纠正）

**验证命令**：

```bash
$ grep -n "__s128\|__u128" 01Reference/kernel-OLK-6.6/include/uapi/linux/types.h
16: #ifdef __SIZEOF_INT128__
17: typedef __signed__ __int128 __s128 __attribute__((aligned(16)));
18: typedef unsigned __int128 __u128 __attribute__((aligned(16)));
19: #endif
```

**结论**：✅ `__s128` 确实存在（openEuler 扩展，受 `__SIZEOF_INT128__` 保护，带 `aligned(16)`）。上一轮声称"不存在"为误报。降级为 P2 可移植性提示（非所有架构都支持 `__int128`）。

---

## 第 2 章 OLK-6.6 工程思想源码位置索引（ES-OLK-1~14）

| 编号 | 工程思想 | 关键源码位置 | 验证状态 |
|------|---------|-------------|---------|
| ES-OLK-1 | 关注点分离 | `Kbuild:48-72`（`obj-y += kernel/` / `obj-y += mm/` / `obj-$(CONFIG_IO_URING) += io_uring/`）；`Kconfig:11-33`（`source` 分source 各子系统）；`security/` 12 个安全策略子目录 | ✅ |
| ES-OLK-2 | 架构正交 | `arch/` 25 架构子目录；`include/asm-generic/` 架构无关默认；`Kbuild:15` `arch/$(SRCARCH)/kernel/asm-offsets.s` | ✅ |
| ES-OLK-3 | UAPI 隔离 | `include/uapi/` 14 子目录 / `include/uapi/linux/` 584 头文件；`include/uapi/linux/capability.h:1` `GPL-2.0 WITH Linux-syscall-note`；`include/uapi/linux/capability.h:17-33` 使用 `__u32`（UAPI 类型）vs `include/linux/capability.h` 使用 `u32`（内部类型） | ✅ |
| ES-OLK-4 | 特性可配置 | `Kconfig` 顶层 `mainmenu`/`source`/`config`/`bool`/`depends on`；`lib/Kconfig.openeuler` `KWORKER_NUMA_AFFINITY`；`Kbuild:65` `obj-$(CONFIG_IO_URING) += io_uring/`；`Kbuild:66` `obj-$(CONFIG_RUST) += rust/`；`kernel/sched/fair.c:1059-1064` `#ifdef CONFIG_BPF_SCHED` | ✅ |
| ES-OLK-5 | 条件编译规范化 | `coding-style.rst:1140-1189` 第 21 章（IS_ENABLED 替代 #ifdef）；`coding-style.rst:1183-1188` `#endif /* CONFIG_SOMETHING */` 标注规范；`src/api/syscall.c:80-96`（seL4 同样遵循）；`kernel/sched/fair.c:1058-1064` | ✅ |
| ES-OLK-6 | UAPI 物理隔离 | `include/uapi/linux/capability.h:1` SPDX `GPL-2.0 WITH Linux-syscall-note`；对比 `include/linux/capability.h` SPDX `GPL-2.0-only`（无 syscall-note）；`include/uapi/asm-generic/` 架构无关 UAPI 默认 | ✅ |
| ES-OLK-7 | 声明式配置 + 命令式构建 | `Kconfig`（声明式 `mainmenu`/`source`/`config`/`bool`/`depends on`/`default`/`help`）；`Kbuild`（命令式 `obj-y += kernel/`）；`Makefile:5-7` `VERSION=6 PATCHLEVEL=6 SUBLEVEL=0`；`Makefile:515` `CHECK = sparse`；`Kbuild:23-46` bounds/timeconst/offsets/missing-syscalls/atomic-checks 生成 | ✅ |
| ES-OLK-8 | MAINTAINERS 文档化 | `MAINTAINERS` 24218 行，字段：`M:`/`R:`/`L:`/`S:`/`W:`/`Q:`/`B:`/`C:`/`P:`/`T:`/`F:`/`X:` | ✅ |
| ES-OLK-9 | 规范可执行 | `scripts/checkpatch.pl` v0.32，72 个 `sub` 规则；`Makefile:111-119` `C=1`/`C=2` sparse 集成；`Makefile:1676-1689` `W=1/2/3/e` 分级警告；`scripts/Makefile.extrawarn:1-80` W=1/2/3/e 编译器 flag；`Documentation/dev-tools/` 20+ 工具文档 | ✅ |
| ES-OLK-10 | 回归零容忍 | `coding-style.rst:1189` 第 22 章"Do not crash the kernel"；`Kbuild:38-46` missing-syscalls 检查 + atomic-checks sha1 校验 | ✅ |
| ES-OLK-11 | ABI 永久稳定 | `include/uapi/linux/capability.h:17-25` 三版本共存（`_LINUX_CAPABILITY_VERSION_1=0x19980330` / `_VERSION_2=0x20071026` deprecated / `_VERSION_3=0x20080522`）；`include/uapi/linux/capability.h:1` `GPL-2.0 WITH Linux-syscall-note` | ✅ |
| ES-OLK-12 | 模块化 | `kernel/fork.c:656` `EXPORT_SYMBOL(free_task)` 紧跟定义；`:992` `EXPORT_SYMBOL_GPL(__mmdrop)`；`:1046` `EXPORT_SYMBOL_GPL(__put_task_struct)`；`:1488` `EXPORT_SYMBOL_GPL(mmput)`；`Kbuild:66` `obj-$(CONFIG_RUST) += rust/` | ✅ |
| ES-OLK-13 | 文档即代码 | `Documentation/process/coding-style.rst` 1271 行 22 章；`Documentation/dev-tools/` 20+ 工具文档；`Documentation/process/` 开发流程文档；`MAINTAINERS` 24218 行；`Kbuild:38-46` 校验脚本即代码 | ✅ |
| **ES-OLK-14** | **KABI 二进制兼容演进**（新增） | `include/linux/kabi.h:1-80`（`KABI_EXTEND`/`KABI_DEPRECATE`/`KABI_BROKEN_INSERT_ENUM`/`KABI_BROKEN_REMOVE_ENUM`/`KABI_USE`/`KABI_REPLACE`）；`lib/Kconfig.kabi:1-30`（`KABI_COMPAT`/`KABI_RESERVE`/`KABI_SIZE_ALIGN_CHECKS`）；`include/linux/bpf.h:321` `KABI_BROKEN_REPLACE` 使用示例；`include/linux/bpf.h:336-337` `KABI_USE(1,...)`/`KABI_USE(2,...)`；`include/linux/bpf.h:721` `KABI_BROKEN_INSERT_ENUM`；`kernel/sched/sched.h:722-733` EEVDF 引入时 `KABI_REPLACE`/`KABI_BROKEN_REMOVE` | ✅ |

---

## 第 3 章 seL4 工程思想源码位置索引（ES-SEL4-1~11）

| 编号 | 工程思想 | 关键源码位置 | 验证状态 |
|------|---------|-------------|---------|
| ES-SEL4-1 | Liedtke 极简原则 | `src/kernel/` 仅 6 文件（boot.c 41KB / cspace.c 5.8KB / faulthandler.c 5.3KB / sporadic.c 12KB / stack.c 249B / thread.c 23KB）；`src/api/` 仅 2 文件（faults.c 261 行 / syscall.c 662 行）；`src/object/` 11 文件；`src/fastpath/fastpath.c` 31KB；`src/util.c` 452 行 / `src/assert.c` 43 行 / `src/string.c` 42 行 | ✅ |
| ES-SEL4-2 | capability 单一模型 | `src/object/cnode.c:50-230` `decodeCNodeInvocation`（Copy:116 / Mint:136 / Move:157 / Mutate:163 / Revoke:195 / Delete:200 / CancelBadgedSends:229 / Rotate:308）；`:80,126,146` `deriveCap()`；`:315-364` `invokeCNodeRevoke`/`invokeCNodeDelete`/`invokeCNodeInsert`/`invokeCNodeMove`/`invokeCNodeRotate`；`:528` `cteRevoke`；`:552` `cteDelete`；`src/object/objecttype.c:62` `deriveCap()`；`include/object/structures_64.bf:11-50` capability 布局 bitfield DSL | ✅ |
| ES-SEL4-3 | 服务用户态化 | `libsel4/` 独立目录 + 独立 `CMakeLists.txt`；`libsel4/include/sel4/` 23 头文件；`src/kernel/faulthandler.c:21-44` `handleFault()` 通过 capability 查找 fault handler endpoint 发送到用户态 | ✅ |
| ES-SEL4-4 | 消息传递 IPC | `src/object/endpoint.c:20-50` `sendIPC`（EPState_Idle/Send/Recv 三态状态机）；`src/object/notification.c:21-50` `ntfn_ptr_get_queue()` / `maybeDonateSchedContext()`（MCS 调度上下文捐赠）；`src/fastpath/fastpath.c:26-100` `fastpath_call()`（`lookup_fp()` → `cap_capType_equals` → `endpoint_ptr_get_state` 检查，失败则 `slowpath(SysCall)` 降级）；`src/api/syscall.c:557-660` `handleSyscall` 分发 7 种调用类型 | ✅ |
| ES-SEL4-5 | 形式化验证 | `tools/bitfield_gen.py:14-16` "generating bitfield structures with get/set/new methods including Isabelle/HOL specifications and correctness proofs"；`tools/bitfield_gen.md` 文档；`CMakeLists.txt` `GenProofsBFTarget(...)` 为每个 `.bf` 生成 `_proofs.thy`；`libsel4/CMakeLists.txt:18-25` `config_choice(LibSel4FunctionAttribute ...)` 形式化验证友好配置；`README.md` Proof Sync CI badge；`src/api/faults.c:18-25` `compile_assert` 一致性检查 | ✅ |
| ES-SEL4-6 | 接口契约 XML | `libsel4/include/api/syscall.xml`（`<syscalls>`/`<api-master>`/`<config>`/8 API syscall + 11 MCS syscall + debug syscall）；`libsel4/include/interfaces/object-api.xml`（`<api name="ObjectApi">`/`<interface>`/`<method>`/`<param>`/`<error>`）；`tools/syscall_header_gen.py:13-15` Jinja2 + XML；`tools/invocation_header_gen.py` + `tools/invocation_json_gen.py`；`libsel4/tools/syscall_stub_gen.py` / `libsel4/tools/syscall_stub_gen_rs.py`（C + Rust stub 生成）；`libsel4/tools/sel4_idl.xsd` XML schema；`README.md` XML lint CI badge | ✅ |
| ES-SEL4-7 | 架构正交分层 | `src/arch/` 3 架构（arm/ 11 子目录 / riscv/ 8 子目录 / x86/ 11 子目录）；`src/machine/` 5 文件（capdl/fpu/io/profiler/registerset）；`src/plat/` 42 平台子目录；`src/smp/` 2 文件（ipi/lock）；`include/` 与 `src/` 同构（11 子目录一一对应）；`include/object/structures.h:9-12` `#include <arch/object/structures_gen.h>` | ✅ |
| ES-SEL4-8 | bitfield codegen | `include/object/structures_64.bf` 64 位位域 DSL（`block null_cap`/`block endpoint_cap(...)`/`block cnode_cap(...)`）；`include/object/structures_32.bf`；`include/arch/{arm,riscv,x86}/arch/object/structures.bf`；`include/plat/pc99/plat/{32,64}/plat_mode/machine/hardware.bf`；`libsel4/sel4_arch_include/{aarch64,aarch32,riscv64,riscv64,ia32,x86_64}/sel4/sel4_arch/types.bf`；`tools/bitfield_gen.py` 123KB 代码生成器；`include/object/structures.h:8` `#include <arch/object/structures_gen.h>`；`tools/bf.vim` Vim 语法高亮 | ✅ |
| ES-SEL4-9 | libsel4 独立 | `libsel4/` 独立目录（CMakeLists.txt + include/ + arch_include/ + sel4_arch_include/ + sel4_plat_include/ 45 平台 + src/ + tools/）；`libsel4/CMakeLists.txt:1-10` `cmake_minimum_required(VERSION 3.16.0)` `project(libsel4 C)`；`libsel4/include/sel4/sel4.h` 用户态总入口；`libsel4/src/sel4_bootinfo.c` 唯一 .c 实现文件 | ✅ |
| ES-SEL4-10 | 现代构建 | `CMakeLists.txt` 27KB 主构建文件；`config.cmake` 20KB 配置选项；`gcc.cmake` 6.8KB GCC 配置；`llvm.cmake` 1.2KB Clang 配置；`cmake/` CMake 模块目录；`configs/` 预置配置；`.cmake-format.yaml` CMake 格式化配置 | ✅ |
| **ES-SEL4-11** | **CI 多工具矩阵**（新增） | `README.md` 8 个 CI badges（CII Best Practices / CI / seL4Test / C Parser / Compile / Proof Sync / RefMan / XML lint）；`tools/kernel_pylint.sh` Python lint；`tools/kernel_xmllint.sh` XML lint；`tools/xmllint.sh` 通用 XML lint；`tools/pylintrc` Python lint 配置；`tools/circular_includes.py` 循环 include 检测；`.github/` GitHub Actions 工作流 | ✅ |

---

## 第 4 章 AirymaxRT ↔ AirymaxOS 跨项目一致性分析

### 4.1 IRON-9 v2 [SC] 共享契约层映射验证

| [SC] 头文件 | AirymaxRT 来源模块 | AirymaxOS 物理宿主 | 验证状态 |
|-------------|-------------------|-------------------|---------|
| `bpf_struct_ops.h` | agentrt atoms/corekern（eBPF 策略引擎） | `kernel/include/airymax/` | ✅ |
| `memory_types.h` | agentrt MemoryRovol（memoryrovol 模块） | `kernel/include/airymax/` | ✅ |
| `security_types.h` | agentrt Cupolas（cupolas 模块） | `kernel/include/airymax/` | ✅ |
| `cognition_types.h` | agentrt CoreLoopThree（atoms/coreloopthree） | `kernel/include/airymax/` | ✅ |
| `sched.h` | agentrt MicroCoreRT（atoms/corekern/sched） | `kernel/include/airymax/` | ✅ |
| `ipc.h` | agentrt AgentsIPC（atoms/ipc） | `kernel/include/airymax/` | ✅ |

### 4.2 跨端一致性验证

| 验证项 | AirymaxRT 定义 | AirymaxOS 定义 | 一致性 |
|--------|---------------|---------------|--------|
| IPC magic | 0x41524531（'ARE1'） | 0x41524531（'ARE1'） | ✅ 一致 |
| 任务描述符 magic | **缺失**（P0-08） | 0x41475453（'AGTS'） | ❌ RT 侧缺失 |
| MAC_MAX_AGENTS | 1024 | 1024 | ✅ 一致 |
| 错误码前缀 | `AGENTRT_OK`/`AGENTRT_ERR_*` | `AGENTRT_EOK`/`AGENTRT_E*` | ❌ 命名不同（P0-04） |
| syscall 入口 | `agentrt_syscall_invoke()`（统一入口） | 编号 syscall 512-631 | ❌ 范式不同（P0-12） |
| [SC] 共享模型 | **完全缺失**（P0-07） | 完整定义（120-cross-project-code-sharing.md） | ❌ RT 侧零知觉 |
| SCHED_EXT | SCHED_EXT=7 | SCHED_EXT=7 | ✅ 一致 |

### 4.3 [SS] 语义同源层 API 映射

| agentrt API | agent-linux API | 同源类型 | 验证状态 |
|-------------|------------------|---------|---------|
| `agent_select_cpu` | BPF `select_cpu` 回调 | sched_ext 同源 | ✅ |
| `agent_enqueue`/`agent_dequeue` | BPF `enqueue`/`dispatch` 回调 | sched_ext 同源 | ✅ |
| `agentrt_ipc_ring_create()` | `io_uring_setup()` | io_uring 同源 | ✅ |
| `agentrt_ipc_ring_enter()` | `io_uring_enter()` | io_uring 同源 | ✅ |
| `agentrt_cap_mint()` | CNode Mint | capability 同源 | ✅ |
| `agentrt_cap_revoke()` | CNode Revoke | capability 同源 | ✅ |

### 4.4 一致性断裂根因分析

AirymaxRT ↔ AirymaxOS 之间的一致性断裂（P0-03/P0-04/P0-07/P0-08）的**根因**是：

> **AirymaxRT 文档体系对 IRON-9 v2 共享模型"零知觉"**

IRON-9 v2 三层共享模型（[SC]/[SS]/[IND]）在 AirymaxOS 侧有完整定义和标注（`120-cross-project-code-sharing.md` 专门文档 + Phase 3.3 完成的 9 个文档 IRON-9 v2 标注章节），但在 AirymaxRT 112 文档中**完全没有提及**。这导致：

1. agentrt 侧开发者不知道有 [SC] 共享契约层约束，各自独立定义 IPC 消息头（→ P0-03 4 种布局）
2. agentrt 侧开发者不知道有统一错误码 SSoT，各自定义错误码值（→ P0-04 4 套值系统）
3. agentrt 侧不知道有 magic 'AGTS' 定义（→ P0-08 缺失）
4. 双向 CI 校验机制在 agentrt 侧无落地基础

**修复策略**：在 AirymaxRT 文档体系中建立 IRON-9 v2 共享模型说明（P0-07 修复方案），这是一致性断裂的**根因修复**。修复 P0-07 后，P0-03/P0-04/P0-08 的修复有了文档基础。

---

## 第 5 章 6 项可落地工程标准

基于 OLK-6.6 和 seL4 源码深度分析，提出以下 6 项可落地为工程标准的条目：

### 5.1 STD-KABI-01：引入 KABI 二进制兼容演进机制（P1）

**上游依据**：ES-OLK-14（`include/linux/kabi.h` + `lib/Kconfig.kabi`）

**现状**：agent-linux 无二进制兼容演进机制。微内核化改造会频繁变更数据结构（如 TCB、capability 表），可能导致内核态 ABI 破坏。

**建议**：在 `50-engineering-standards/` 新增 `09-kabi-evolution.md`，定义 agent-linux 的 KABI 宏机制（借鉴 OLK-6.6 `KABI_EXTEND`/`KABI_DEPRECATE`/`KABI_BROKEN_INSERT_ENUM`/`KABI_USE` 但不复制其实现）。新增字段必须追加到结构体末尾，废弃字段保留 hole。

**优先级**：P1（微内核化改造关键基础设施，1.0.1 M1 落地，~20h）

### 5.2 STD-CODE-07：强化 sparse + W=1/2/3/e 分级警告集成（P1）

**上游依据**：ES-OLK-9（`Makefile:111-119` sparse + `scripts/Makefile.extrawarn` W 分级）

**现状**：`08-compliance-checklist.md` 已有 16 个检查脚本，但未明确 sparse + W 分级警告的集成要求。

**建议**：CI 必须运行 `make C=1`（sparse 检查重编译文件）+ `make W=1`（相关警告）+ `make W=e`（警告即错误）三档。W=2/W=3 可选。

**优先级**：P1（CI 基础设施，1.0.1 M1 落地，~8h）

### 5.3 STD-DOC-18：引入 syscall.xml 式接口契约定义（P2）

**上游依据**：ES-SEL4-6（`libsel4/include/api/syscall.xml` + `tools/syscall_header_gen.py`）

**现状**：agent-linux 的 `30-interfaces/01-syscalls.md` 以 Markdown 描述系统调用接口，无机器可读契约。

**建议**：新增 `syscall-contract.xml`，由 `scripts/syscall_gen.py` 自动生成 `include/uapi/airymax/syscall.h` + `kernel/entry/airymax_syscall_table.c`。XML 格式借鉴 seL4（`<syscalls>`/`<syscall name="..."/>`/`<param>`/`<error>`）但不复制其内容。

**优先级**：P2（R-01 建议，~16h，1.0.1 M1 落地）

### 5.4 STD-CODE-08：[SC] 头文件位域定义 bitfield codegen（P2）

**上游依据**：ES-SEL4-8（`include/object/structures_64.bf` + `tools/bitfield_gen.py`）

**现状**：IRON-9 v2 [SC] 共享契约层 6 个头文件中的位域定义是手写 C 位域。

**建议**：新增 `bitfield-contract.bf` 规范，定义 `.bf` DSL 格式，由 `scripts/bitfield_gen.py` 自动生成 C 结构体与访问函数。借鉴 seL4 `block`/`field`/`field_ptr`/`padding` 语法。

**优先级**：P2（R-02 建议，~12h，1.0.1 M1 落地）

### 5.5 STD-IRON-18：8 子仓落地 MAINTAINERS 文件（P2）

**上游依据**：ES-OLK-8（`MAINTAINERS` 24218 行）

**现状**：agent-linux 8 子仓无 MAINTAINERS 文件。

**建议**：为 8 子仓每个仓根目录新增 `MAINTAINERS` 文件，格式精简（`M:`/`S:`/`F:`/`W:` 四字段），每个子系统有明确责任人。

**优先级**：P2（R-03 建议，~8h，1.0.1 M5 落地）

### 5.6 STD-TEST-09：建立 CI 多工具矩阵（P2）

**上游依据**：ES-SEL4-11（seL4 8 个 CI 工作流）+ ES-OLK-9（OLK sparse/W/checkpatch）

**现状**：agent-linux 的 CI 矩阵未明确。

**建议**：定义 CI 多工具矩阵——(1) 编译检查（多编译器/多架构）；(2) 静态分析（sparse/smatch/cppcheck/coccinelle）；(3) 单元测试（KUnit）；(4) 集成测试（kselftest）；(5) 文档生成（`make htmldocs`）；(6) 契约一致性检查（syscall.xml / bitfield.bf）；(7) checkpatch 规范检查；(8) 形式化验证（tests-linux 子仓）。

**优先级**：P2（~16h，1.0.1 M3 落地）

---

> **文档结束** | agent-linux v0.3.0 源码级证据与跨项目一致性分析 | 2026-07-10 | SPHARX Ltd
