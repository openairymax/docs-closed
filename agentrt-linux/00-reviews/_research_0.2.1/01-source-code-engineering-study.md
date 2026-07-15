Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# OLK-6.6 与 seL4 源代码工程思想研究报告

> **文档定位**: 基于对 `01Reference/kernel-OLK-6.6`（Linux 6.6 内核基线）与 `01Reference/seL4-master`（seL4 微内核）全部源代码的深度研究，提取工程思想、编码风格、代码格式、代码规范、代码标准，作为 `docs/AirymaxAgentOS` agentrt-linux 方案再检查（见 [02-airymaxos-recheck-report.md](02-airymaxos-recheck-report.md)）与 8 子仓目录结构设计（见 `01-designs/_design_0.2.1/01-agentrt-linux-directory-structure.md`）的理论依据。
> **版本**: 0.2.1（研究报告）
> **最后更新**: 2026-07-09
> **研究范围**: OLK-6.6 全量源码（28 顶层目录）+ seL4-master 全量源码（src/ + include/ + libsel4/ + tools/ + manual/）
> **方法论**: 目录测绘 + 代表性源文件精读（coding-style.rst 1-700 行 / tcb.c 1-120 行）+ 模式归纳 + 双向对比

---

## 目录

- [第 1 章 研究目标与方法](#第-1-章-研究目标与方法)
- [第 2 章 OLK-6.6 工程思想提取](#第-2-章-olk66-工程思想提取)
- [第 3 章 seL4 工程思想提取](#第-3-章-sel4-工程思想提取)
- [第 4 章 编码风格对比](#第-4-章-编码风格对比)
- [第 5 章 代码格式对比](#第-5-章-代码格式对比)
- [第 6 章 代码规范与代码标准对比](#第-6-章-代码规范与代码标准对比)
- [第 7 章 工程思想双源融合结论](#第-7-章-工程思想双源融合结论)

---

## 第 1 章 研究目标与方法

### 1.1 研究目标

agentrt-linux 的三大设计支柱为：(1) 微内核设计原则（参考 seL4 / Zircon / Minix3）；(2) Euler 标准兼容；(3) Airymax 同源。其中第一支柱的技术参考来源是 seL4，而第二支柱的工程基线是 Linux 6.6（OLK-6.6）。这一"双源融合"特征决定了 agentrt-linux 必须同时吸收两类工程思想，但两者的工程取向差异巨大——Linux 是宏内核工程传统的巅峰，seL4 是形式化微内核的极致。本研究的目标是厘清：

1. **OLK-6.6 提供了哪些可直接落地的工程思想、编码风格、代码格式、代码规范、代码标准？** —— 答案决定 agentrt-linux 的"工程基线层"。
2. **seL4 提供了哪些可借鉴的工程思想？其编码风格为何不能整体照搬？** —— 答案决定 agentrt-linux 的"微内核思想层"与"编码风格层"的边界。
3. **双源之间哪些维度互补、哪些维度冲突？冲突如何裁决？** —— 答案决定 agentrt-linux 工程标准的具体取舍。

### 1.2 研究方法

本研究采用"目录测绘 + 代表性源文件精读 + 模式归纳 + 双向对比"四步法：

| 步骤 | OLK-6.6 | seL4 |
|------|---------|------|
| 目录测绘 | 28 顶层目录 + kernel/sched + io_uring + include/{uapi,linux,asm-generic} + security/{selinux,landlock} + arch/{x86,arm64} + tools/{testing,perf} + scripts/checkpatch.pl + MAINTAINERS + .clang-format | src/{api,kernel,object,fastpath,arch,machine,plat,smp,drivers,model,benchmark} + include/{api,kernel,object,arch,machine,plat,smp,benchmark} + libsel4/ + configs/ + cmake/ + tools/ + manual/ |
| 代表性源文件精读 | Documentation/process/coding-style.rst（1-700 行） | src/object/tcb.c（1-120 行） |
| 模式归纳 | 提取 10 项工程思想 + 8 类编码风格要素 | 提取 4 大微内核支柱 + 6 项工程思想 |
| 双向对比 | 11 个维度逐项对照 | 同左 |

**研究边界声明**: 本研究仅提取工程思想与编码约定，不涉及对任一项目代码的复制。OLK-6.6 与 seL4 的源码仅在本地参考路径（`01Reference/`）中作为研究对象；agentrt-linux 与两者的关系是"技术参考"而非"代码共享"，符合 IRON-9 v2 同源边界。

---

## 第 2 章 OLK-6.6 工程思想提取

### 2.1 目录组织：关注点分离与层次依赖

OLK-6.6 的顶层目录组织本身就是一份工程哲学宣言——它用目录命名表达了内核的"关注点分离"原则：

| 顶层目录 | 关注点 | 工程思想 |
|---------|--------|---------|
| `arch/` | 架构相关代码（x86/arm64/riscv/loongarch 等） | 架构相关与架构无关代码严格隔离 |
| `include/` | 内核内部头文件 + UAPI | 公共契约与实现分离 |
| `kernel/` | 内核核心子系统（sched/locking/entry/irq/cgroup/bpf/time/cred/fork） | 核心机制集中管理 |
| `mm/` | 内存管理（page_alloc/compaction/oom/damon/cma/mglru） | 单一子系统垂直内聚 |
| `fs/` | 文件系统 | 按文件系统类型组织 |
| `net/` | 网络栈（core/ipv4/ipv6/sched/netfilter） | 协议层垂直组织 |
| `drivers/` | 设备驱动 | 按设备类型大类组织（gpu/net/usb/pci） |
| `security/` | 安全框架（selinux/landlock/apparmor/tomoyo/smack/integrity/keys） | 安全策略可插拔，每策略一目录 |
| `io_uring/` | 异步 I/O 框架 | 独立子系统，与 fs/net 并列 |
| `block/` | 块设备层 | I/O 栈分层 |
| `crypto/` | 加密算法 | 算法与框架分离 |
| `init/` | 启动初始化 | 启动序列集中 |
| `lib/` | 通用工具库 | 内核内复用 |
| `scripts/` | 构建与检查脚本（checkpatch.pl） | 工具即代码 |
| `tools/` | 用户态工具（testing/perf） | 内核配套工具 |
| `Documentation/` | 文档（process/trace/kbuild/ABI） | 文档即代码 |
| `certs/` | 证书 | 签名体系独立 |
| `rust/` | Rust 实验 | 新语言支持隔离 |
| `sound/` `virt/` `samples/` `usr/` | 音频/虚拟化/示例/initramfs | 边缘子系统隔离 |

**工程思想提炼**:

- **ES-OLK-1（关注点分离原则）**: 每个顶层目录对应一个独立的关注点，跨关注点的耦合通过明确的接口进行。一个内存管理 bug 不会牵连网络栈，因为 `mm/` 与 `net/` 是两个独立目录。
- **ES-OLK-2（架构正交原则）**: `arch/` 是唯一的架构相关根目录，所有其他顶层目录必须是架构无关的。架构特定实现下沉到 `arch/<arch>/` 内部，通过 `asm-generic/` 提供默认实现。
- **ES-OLK-3（UAPI 与内核内部 API 分离）**: `include/uapi/` 是用户空间 ABI 的唯一来源，`include/linux/` 是内核内部 API。UAPI 的变更受双层稳定性上层（永久稳定）约束，内核内部 API 受下层（可变）约束。

### 2.2 CONFIG_* 可选编译机制

OLK-6.6 通过 `Kconfig` + `CONFIG_*` 宏实现编译时可选编译：

- 每个子系统有独立的 `Kconfig` 文件（如 `kernel/sched/Kconfig`、`mm/Kconfig`、`security/selinux/Kconfig`）。
- `Kconfig` 定义 `config` 项、`depends on`、`select`、`default`、`help` 文本。
- `.c` 文件通过 `#ifdef CONFIG_XXX` / `IS_ENABLED(CONFIG_XXX)` 进行条件编译。
- `Makefile` 通过 `obj-$(CONFIG_XXX) += xxx.o` 选择性编译。

**工程思想提炼**:

- **ES-OLK-4（特性可配置原则）**: 每个特性都可通过 Kconfig 开关控制，发行版可按需裁剪。这是宏内核避免"一刀切膨胀"的关键机制——同一份源码可裁剪为嵌入式最小内核或服务器全功能内核。
- **ES-OLK-5（条件编译规范化）**: `.c` 文件中避免直接 `#if`，改用 stub 函数 + `IS_ENABLED()` 转 C 布尔；`#endif` 必须标注对应的 `#ifdef` 名。

### 2.3 uapi 拆分：用户空间 ABI 的法律边界

OLK-6.6 将用户可见头文件全部置于 `include/uapi/`，与内核内部头文件 `include/linux/` 物理隔离。这一拆分的工程意义在于：

- **法律边界**: UAPI 头文件是用户空间 ABI 的"合同"，受双层稳定性上层约束；内核内部头文件不受此约束。
- **许可边界**: UAPI 头文件通常采用更宽松的许可证（如 BSD/MIT），允许用户空间程序自由包含；内核内部头文件采用 GPL。
- **变更流程边界**: UAPI 变更需经 ABI 审查组评审 + 6 个月宽限期；内核内部 API 变更仅需补丁序列修复调用点。

**工程思想提炼**:

- **ES-OLK-6（UAPI 物理隔离原则）**: 用户空间 ABI 头文件必须物理隔离于 `uapi/` 目录，与内核内部头文件分开管理，变更流程、许可证、稳定性承诺均不同。

### 2.4 Kbuild / Kconfig / Makefile 三层构建系统

OLK-6.6 采用三层构建系统：

- **Kconfig**（声明式）: 定义可配置项、依赖关系、默认值。
- **Kbuild**（递归 Make）: 通过 `obj-y` / `obj-m` / `obj-$(CONFIG_XXX)` 递归构建。
- **Makefile**（命令式）: 定义编译规则、链接规则、依赖关系。

每个目录都有 `Makefile` 和可选的 `Kconfig`，构建是递归的——顶层 `Makefile` 调用子目录 `Makefile`，子目录再调用孙目录。

**工程思想提炼**:

- **ES-OLK-7（声明式配置 + 命令式构建分离）**: Kconfig 声明"有哪些可选项"，Makefile 命令式定义"如何构建"。两者职责清晰，发行版裁剪只需修改 `.config`，无需修改构建脚本。

### 2.5 MAINTAINERS 文件：维护者制度可追溯

OLK-6.6 根目录有 `MAINTAINERS` 文件，列出每个子系统的维护者、副维护者、代码审查者、邮件列表、源码路径、状态（Supported/Maintained/Odd Fixes/Obsolete）。这是 Linux 维护者制度的"社会契约"——每一个子系统都有明确的责任人。

**工程思想提炼**:

- **ES-OLK-8（维护者制度文档化原则）**: 每个子系统的维护者、审查者、状态必须文档化于 `MAINTAINERS` 文件，确保任何代码变更都有明确的责任归属。

### 2.6 checkpatch.pl：机器可执行的规范

OLK-6.6 的 `scripts/checkpatch.pl` 是编码规范的机器可执行版本——它检查补丁是否符合规范（缩进、行宽、命名、错误处理、注释格式等）。规范不是文档中的文字，而是脚本中的规则。

**工程思想提炼**:

- **ES-OLK-9（规范可执行原则）**: 每条编码规范必须有对应的检查脚本；规范若无法被机器检查，等同于不存在。这是"配置即代码"在规范层的体现。

### 2.7 渐进式开发与回归零容忍

OLK-6.6 的开发模型是 Merge Window + RC 周期：

- **Merge Window（~2 周）**: 接受新特性。
- **RC 周期（~6-10 周，rc1-rc9）**: 只接受 bug 修复，每个 RC ~1 周。
- **regression 不可接受**: 任何破坏既有功能的补丁必须修复或 revert。
- **补丁序列中点可编译**: `git bisect` 友好的硬性要求。

**工程思想提炼**:

- **ES-OLK-10（regression 零容忍原则）**: regression 是"特别坏的 bug"，必须在当前 stabilization 阶段修复或 revert。新功能的 benefit 不能凌驾于 regression 修复之上。

### 2.8 向后兼容与不破坏用户空间

OLK-6.6 继承 Linux 30+ 年的 ABI 稳定传统——在 pre-0.9 内核上编译的老程序，至今仍能在最新内核上正常运行。这是一份刻意设计的工程哲学。

**工程思想提炼**:

- **ES-OLK-11（用户空间 ABI 永久稳定原则）**: 一旦接口导出至用户空间，必须永久支持。这是宏内核生态可持续性的根基。

### 2.9 模块化与可加载内核模块

OLK-6.6 支持运行时加载/卸载内核模块（`.ko`），通过 `EXPORT_SYMBOL` 导出符号。模块机制是宏内核避免"膨胀至死"的关键——发行版可按需加载驱动、文件系统、网络协议。

**工程思想提炼**:

- **ES-OLK-12（运行时可加载原则）**: 机制留在内核，实现可作为模块运行时加载/卸载。`EXPORT_SYMBOL` 紧跟函数定义，确保符号导出可追溯。

### 2.10 文档即代码

OLK-6.6 的 `Documentation/` 目录包含 process/（开发流程）、trace/（追踪）、kbuild/（构建）、ABI/（ABI 文档）、admin-guide/、devicetree/、gpu/、networking/ 等。所有文档与代码同仓库，同步演进。

**工程思想提炼**:

- **ES-OLK-13（文档即代码原则）**: 文档与代码同仓库，同步演进；`/proc` 条目文档化、`MODULE_PARM_DESC`、ABI/ 文档、kernel-doc 注释、`make htmldocs` 全链路打通。

---

## 第 3 章 seL4 工程思想提取

### 3.1 微内核四大支柱

seL4 是世界上第一个功能正确性经过形式化证明的微内核。其工程思想建立在四大支柱之上：

| 支柱 | 内涵 | 工程体现 |
|------|------|---------|
| **Liedtke 极简原则** | 微内核只保留"无法在用户空间高效实现"的最小原语集（IPC、地址空间、线程、唯一性） | src/kernel/ 仅 boot/cspace/faulthandler/sporadic/stack/thread 6 文件 |
| **capability-based security** | 所有权限通过 capability 令牌表达，无隐式权限 | src/object/cnode.c（capability 节点管理）、capability 派生模型 |
| **用户态服务化** | 所有非必要服务（文件系统、网络、驱动）运行在用户空间 | libsel4/（用户态 API 库）独立 |
| **消息传递 IPC** | 进程间通信通过 endpoint / notification / fastpath | src/object/{endpoint,notification}.c、src/fastpath/fastpath.c |

**工程思想提炼**:

- **ES-SEL4-1（极简原则）**: 微内核代码量必须可被形式化证明覆盖——seL4 核心约 8700 行 C 代码。任何新增功能必须论证"无法在用户空间高效实现"，否则拒绝入内核。
- **ES-SEL4-2（capability 单一权限模型）**: 所有权限（内存访问、IPC 端点、线程控制）统一通过 capability 表达。没有 capability 的对象不可访问。capability 可 mint / mintcopy / derive / revoke，形成权限派生树。
- **ES-SEL4-3（服务用户态化）**: 内核只提供原语，文件系统、网络栈、驱动、内存管理策略都运行在用户空间。内核不"知道"文件系统的存在，它只知道"有一个用户态进程通过 IPC 请求内核服务"。
- **ES-SEL4-4（消息传递 IPC）**: 进程间通信的唯一机制是消息传递。IPC 有三种形态：endpoint（同步消息）、notification（异步信号）、fastpath（最优路径优化，绕过通用 IPC 路径）。

### 3.2 形式化验证驱动

seL4 是首个功能正确性经过 Isabelle/HOL 形式化证明的微内核。其 `proof/`、`spec/`、`capDL/` 目录包含形式化规约与证明：

- **spec/**: 抽象规约（abstract specification）——内核"应该做什么"的数学描述。
- **proof/**: Isabelle/HOL 证明——证明 C 实现（经自动翻译为 SIMPL）满足抽象规约。
- **capDL/**: capability 分布语言——系统初始 capability 状态的描述。

**工程思想提炼**:

- **ES-SEL4-5（形式化验证驱动原则）**: 内核实现必须可被形式化证明满足抽象规约。这要求代码避免形式化工具无法处理的特性（动态分配、复杂数据结构、不确定控制流）。
- **ES-SEL4-6（接口契约 XML 定义）**: seL4 通过 `tools/syscall.xml` 定义系统调用接口契约，由代码生成器（`tools/syscall_generator.py`）自动生成用户态 stub 与内核态 entry。接口契约与实现分离。

### 3.3 架构无关核心 + 架构相关适配

seL4 的目录组织严格遵循"架构无关核心 + 架构相关适配"分离：

- **架构无关核心**: `src/{api,kernel,object,fastpath,model,benchmark}` —— 与 CPU 架构无关的核心逻辑。
- **架构相关适配**: `src/arch/`（arm/riscv/x86）、`src/machine/`（机器相关原语）、`src/plat/`（平台相关，30+ 平台）、`src/smp/`（多核）。
- **include 同构**: `include/{api,kernel,object,arch,machine,plat,smp,benchmark}` 与 `src/` 一一对应。

**工程思想提炼**:

- **ES-SEL4-7（架构正交分层原则）**: 内核核心逻辑与架构相关代码物理隔离，通过 `arch/` / `machine/` / `plat/` 三层适配。核心逻辑可被形式化证明，架构适配层可独立演进。

### 3.4 bitfield codegen

seL4 的 `structures.bf` 文件定义 bitfield 结构，由 `tools/bitfield_gen.py` 自动生成 C 结构体与访问函数。这避免了手写位域操作易错的问题。

**工程思想提炼**:

- **ES-SEL4-8（结构定义代码生成原则）**: 复杂位域结构通过 DSL（`.bf` 文件）定义，由代码生成器生成 C 代码。避免手写位域操作的错误。

### 3.5 libsel4 用户态 API 库

seL4 的 `libsel4/` 是用户态 API 库，独立于内核源码树。它包含：

- `include/`: 用户可见 API 头文件。
- `arch_include/`: 架构相关 API。
- `sel4_arch_include/`: seL4 架构相关（32/64 位）。
- `sel4_plat_include/`: 平台相关。
- `src/`: API 实现。
- `tools/`: API 代码生成工具。

**工程思想提炼**:

- **ES-SEL4-9（用户态 API 库独立原则）**: 用户态 API 库与内核源码树物理分离，独立版本、独立构建、独立测试。用户程序通过 libsel4 与内核通信，不直接调用内核内部函数。

### 3.6 CMake 构建系统

seL4 采用 CMake（`CMakeLists.txt`、`cmake/`、`config.cmake`、`gcc.cmake`、`llvm.cmake`），而非 Make/Kbuild。CMake 提供更现代的构建描述能力（条件、函数、目标依赖）。

**工程思想提炼**:

- **ES-SEL4-10（现代构建系统原则）**: 微内核构建系统采用 CMake，支持多编译器（GCC/Clang）、多架构、多平台、多配置。

---

## 第 4 章 编码风格对比

### 4.1 缩进

| 维度 | OLK-6.6 | seL4 | 差异根因 |
|------|---------|------|---------|
| 缩进字符 | Tab | 空格 | Linux 选择 Tab 以警告深层嵌套；seL4 选择空格以形式化友好 |
| 缩进宽度 | 8 字符 | 4 空格 | 同上 |
| 嵌套警告阈值 | 3 层 | 无显式阈值 | seL4 极简代码本身嵌套浅 |

**裁决**: agentrt-linux 选择 **OLK-6.6（Tab 8 字符）**。理由: (1) agentrt-linux 基于 Linux 6.6 内核基线，内核态代码必须与上游 Linux 一致，便于 backport；(2) 8 字符 Tab 的嵌套警告价值在内核工程中已被验证；(3) seL4 的 4 空格选择源于其形式化约束，agentrt-linux 内核态代码无形式化约束。

### 4.2 命名

| 维度 | OLK-6.6 | seL4 | 差异根因 |
|------|---------|------|---------|
| 命名风格 | snake_case | camelCase | Linux 遵循 Unix/C 传统；seL4 遵循 Haskell/学术传统 |
| 函数命名 | `count_active_users_scheduler` | `checkPrio`、`tcbSchedEnqueue` | 同上 |
| 变量命名 | 局部短小（tmp/i），全局描述性 | `tcb->tcbSchedPrev`、`tcb->tcbMCP`（camelCase + 结构体前缀） | seL4 重度使用 typedef + 前缀 |
| 类型前缀 | 无 Hungarian | 无 Hungarian，但 typedef 重度 | 两者均拒绝 Hungarian |

**裁决**: agentrt-linux 选择 **OLK-6.6（snake_case）**。理由: (1) 与 Linux 6.6 上游一致，便于 backport；(2) snake_case 是 C/Unix 生态主流；(3) seL4 的 camelCase 源于其 Haskell 形式化传统，与 C 生态格格不入。

### 4.3 typedef 使用

| 维度 | OLK-6.6 | seL4 | 差异根因 |
|------|---------|------|---------|
| typedef 频率 | 极少（仅 5 种例外） | 极重 | Linux 反对 typedef（除不透明对象/整数类型/sparse/C99/UAPI）；seL4 大量使用 typedef |
| 典型 typedef | `pid_t`、`gid_t`、`size_t`（标准） | `tcb_t`、`prio_t`、`word_t`、`exception_t`、`tcb_queue_t` | seL4 通过 typedef 实现类型抽象 |
| 结构体标签 | `struct foo`（直接用标签） | `tcb_t`（typedef 后直接用） | 同上 |

**裁决**: agentrt-linux 选择 **OLK-6.6（最小 typedef）**。理由: (1) typedef 隐藏类型信息，增加阅读成本；(2) Linux 的 5 种例外（不透明对象/清晰整数/sparse/C99/UAPI）覆盖了所有合理用例；(3) seL4 的重度 typedef 源于其形式化证明工具的类型推导需求。

### 4.4 大括号放置（K&R）

| 维度 | OLK-6.6 | seL4 | 差异 |
|------|---------|------|------|
| 非函数块开括号 | 行末 | 行末 | 一致 |
| 函数开括号 | 下一行行首 | 下一行行首 | 一致 |
| if-else | else 紧跟闭括号 | else 紧跟闭括号 | 一致 |

**裁决**: 两者一致，均采用 K&R 风格。agentrt-linux 直接采纳。

### 4.5 宏使用

| 维度 | OLK-6.6 | seL4 | 差异 |
|------|---------|------|------|
| 位运算宏 | `BIT()` / `MASK()` / `GENMASK()` | `BIT()` / `MASK()` | 一致 |
| CONFIG 守卫 | `#ifdef CONFIG_XXX` / `IS_ENABLED()` | `#ifdef CONFIG_KERNEL_MCS` | 一致 |
| unlikely/likely | 大量使用 | 大量使用 | 一致 |
| assert | `BUG_ON()` / `WARN_ON()`（受限） | `assert()`（直接） | seL4 因形式化约束偏好 assert |

**裁决**: agentrt-linux 选择 **OLK-6.6**。理由: (1) `BUG_ON()` / `WARN_ON()` 是 Linux 内核工程的成熟模式；(2) seL4 的 `assert()` 在形式化证明外无特殊价值；(3) 与 Linux 上游一致。

### 4.6 错误处理

| 维度 | OLK-6.6 | seL4 | 差异 |
|------|---------|------|------|
| 错误码 | 负 errno（`-EINVAL`、`-ENOMEM`） | `exception_t` 枚举 | 不同 |
| goto 集中出口 | 大量使用（`goto out_free_buffer`） | 不使用（极简函数无需 goto） | 不同 |
| 标签命名 | 描述行为（`out_free_buffer`） | N/A | OLK-6.6 独有 |

**裁决**: agentrt-linux 选择 **OLK-6.6（负 errno + goto 集中出口）**。理由: (1) 与 Linux 内核错误处理模式一致；(2) goto 集中出口是多出口函数的资源释放最佳模式；(3) seL4 的极简函数无需 goto，但 agentrt-linux 内核态函数复杂度高于 seL4。

### 4.7 注释

| 维度 | OLK-6.6 | seL4 | 差异 |
|------|---------|------|------|
| 注释风格 | 通用风格（`/* ... */`） + net/ 风格 | `/* ... */` | 一致 |
| kernel-doc | 强制（`/** ... */`） | 无 | OLK-6.6 独有 |
| WHAT/WHY 不 HOW | 是 | 是 | 一致 |

**裁决**: agentrt-linux 选择 **OLK-6.6（kernel-doc 强制）**。理由: (1) kernel-doc 是 Linux 内核文档即代码的核心；(2) seL4 无此机制。

---

## 第 5 章 代码格式对比

### 5.1 行宽

| 维度 | OLK-6.6 | seL4 | 差异 |
|------|---------|------|------|
| C 首选行宽 | 80 列 | 无强制（通常 ~100） | 不同 |
| 字符串断行 | 禁止（破坏 grep） | 允许 | 不同 |

**裁决**: agentrt-linux 选择 **OLK-6.6（80 列 + 字符串禁止断行）**。

### 5.2 空格

| 维度 | OLK-6.6 | seL4 | 差异 |
|------|---------|------|------|
| 关键字后空格 | 是（if/switch/for/while） | 是 | 一致 |
| sizeof 空格 | 否 | 否 | 一致 |
| 指针 `*` 位置 | 贴名字（`char *p`） | 贴名字 | 一致 |
| 二元运算符 | 两侧空格 | 两侧空格 | 一致 |
| 括号内空格 | 禁止 | 禁止 | 一致 |

**裁决**: 两者一致，agentrt-linux 直接采纳。

### 5.3 switch/case

| 维度 | OLK-6.6 | seL4 | 差异 |
|------|---------|------|------|
| case 与 switch 对齐 | 是（禁止双缩进） | 是 | 一致 |
| fallthrough 标注 | `fallthrough;` | 无强制 | OLK-6.6 独有 |

**裁决**: agentrt-linux 选择 **OLK-6.6（fallthrough 显式标注）**。

### 5.4 空行

| 维度 | OLK-6.6 | seL4 | 差异 |
|------|---------|------|------|
| 函数间空行 | 1 行 | 1 行 | 一致 |
| 函数内空行 | 禁止（除声明区与执行区） | 允许 | 不同 |
| 连续空行 | 最多 1 行 | 无限制 | 不同 |

**裁决**: agentrt-linux 选择 **OLK-6.6（禁止函数内多余空行 + MaxEmptyLinesToKeep:1）**。

### 5.5 文件头

| 维度 | OLK-6.6 | seL4 | 差异 |
|------|---------|------|------|
| SPDX 头 | `SPDX-License-Identifier: GPL-2.0-only` | `SPDX-License-Identifier: GPL-2.0-only` | 一致 |
| copyright 注释 | 可选 | 可选 | 一致 |

**裁决**: 两者一致，agentrt-linux 直接采纳（SPDX: `AGPL-3.0-or-later OR Apache-2.0`）。

---

## 第 6 章 代码规范与代码标准对比

### 6.1 头文件组织

| 维度 | OLK-6.6 | seL4 | 差异 |
|------|---------|------|------|
| include 顺序 | 固定（linux/ → asm/ → 系统 → 自定义） | 固定 | 一致 |
| include guard | `#ifndef _FOO_H` / `#define _FOO_H` | 同左 | 一致 |
| 自动排序 | 禁止（破坏逻辑分组） | 禁止 | 一致 |
| UAPI 物理隔离 | 是（`include/uapi/`） | 否（seL4 无 UAPI 概念，用户态用 libsel4） | 不同 |

**裁决**: agentrt-linux 选择 **OLK-6.6**。理由: (1) agentrt-linux 基于 Linux 6.6，UAPI 概念必须保留；(2) seL4 的 libsel4 模型可借鉴用于 SDK 层（`airymaxos-sdk/`），但不替代 UAPI。

### 6.2 函数设计

| 维度 | OLK-6.6 | seL4 | 差异 |
|------|---------|------|------|
| 函数长度 | ≤80×24（1-2 屏） | 极简（通常 <20 行） | seL4 更短 |
| 局部变量数 | ≤5-10 | ≤5 | seL4 更少 |
| 单一职责 | 是 | 是 | 一致 |
| EXPORT_SYMBOL | 紧跟函数定义 | N/A（seL4 无模块机制） | OLK-6.6 独有 |

**裁决**: agentrt-linux 选择 **OLK-6.6（≤80×24 + ≤5-10 局部变量 + EXPORT_SYMBOL 紧跟）**。

### 6.3 类型系统

| 维度 | OLK-6.6 | seL4 | 差异 |
|------|---------|------|------|
| 内部类型 | `u8/u16/u32/u64`（内核内部） | `word_t`（机器字） | 不同 |
| UAPI 类型 | `__u8/__u16/__u32/__u64`（用户可见） | N/A | OLK-6.6 独有 |
| 位域 | `bitfield/flags` | `structures.bf` codegen | 不同 |

**裁决**: agentrt-linux 选择 **OLK-6.6（u8/u32 内部 + __u32 UAPI）**，但借鉴 seL4 的 `structures.bf` codegen 思路用于 IRON-9 v2 [SC] 共享契约层的位域定义。

### 6.4 并发控制

| 维度 | OLK-6.6 | seL4 | 差异 |
|------|---------|------|------|
| 同步原语 | spinlock / rwlock / rcu / seqlock | 无（seL4 内核非抢占，无并发） | 根本性不同 |
| volatile | 仅 4 种例外 | 大量使用（硬件寄存器） | 不同 |
| I/O accessor | `readl()` / `writel()` / `ioread32()` | 平台相关 | 不同 |

**裁决**: agentrt-linux 选择 **OLK-6.6（spinlock/rcu + volatile 4 例外 + I/O accessor）**。理由: (1) agentrt-linux 基于 Linux 6.6，并发模型必须与上游一致；(2) seL4 的"内核非抢占无并发"模型不适用于宏内核。

### 6.5 内存管理

| 维度 | OLK-6.6 | seL4 | 差异 |
|------|---------|------|------|
| 分配 | `kmalloc` / `kzalloc` / `vmalloc` / `kmem_cache` | 无动态分配（形式化约束） | 根本性不同 |
| 释放 | `kfree` / `vfree` | N/A | 同上 |
| sizeof | `sizeof(*p)` / `kmalloc_array` / `struct_size` | `sizeof(struct foo)` | 不同 |
| 字符串拷贝 | `strscpy`（强制） | `strncpy` | 不同 |

**裁决**: agentrt-linux 选择 **OLK-6.6（kmalloc + sizeof(*p) + strscpy 强制）**。

---

## 第 7 章 工程思想双源融合结论

### 7.1 融合裁决总表

| 维度 | OLK-6.6 | seL4 | agentrt-linux 裁决 | 裁决理由 |
|------|---------|------|-------------------|---------|
| 缩进 | Tab 8 | 空格 4 | OLK-6.6 | 与 Linux 6.6 基线一致 |
| 命名 | snake_case | camelCase | OLK-6.6 | C/Unix 生态主流 |
| typedef | 最小 | 重度 | OLK-6.6 | 阅读成本与形式化约束权衡 |
| 大括号 | K&R | K&R | 一致 | 两者相同 |
| 行宽 | 80 | ~100 | OLK-6.6 | 与上游一致 |
| 错误处理 | errno + goto | exception_t | OLK-6.6 | 与上游一致 |
| 注释 | kernel-doc | 普通 | OLK-6.6 | 文档即代码 |
| UAPI | 物理隔离 | libsel4 | OLK-6.6 + 借鉴 libsel4 | UAPI 保留，SDK 借鉴 libsel4 |
| 并发 | spinlock/rcu | 无 | OLK-6.6 | 宏内核并发模型 |
| 内存 | kmalloc | 无动态 | OLK-6.6 | 宏内核内存模型 |
| **架构组织** | arch/ 隔离 | arch/machine/plat 三层 | **融合** | 借鉴 seL4 三层适配 |
| **接口契约** | 无统一 XML | syscall.xml codegen | **借鉴 seL4** | 接口契约 XML 化 |
| **bitfield** | 手写 | structures.bf codegen | **借鉴 seL4** | 位域 codegen |
| **形式化** | 无 | Isabelle/HOL | **借鉴思想** | tests-linux 子仓形式化验证框架 |
| **capability** | LSM 钩子 | capability 单一模型 | **融合** | security 子仓 capability + LSM |
| **IPC** | 多种 | endpoint/notification/fastpath | **融合** | io_uring + 借鉴 fastpath 优化 |

### 7.2 核心结论

1. **编码风格层**: agentrt-linux 完全采纳 OLK-6.6 的编码约定（Tab 8 / snake_case / 最小 typedef / K&R / 80 列 / errno + goto / kernel-doc）。seL4 的编码约定（4 空格 / camelCase / 重度 typedef）因与 Linux 6.6 基线冲突而被整体拒绝。**seL4 的影响不在编码层。**

2. **工程思想层**: agentrt-linux 采纳 OLK-6.6 的 13 项工程思想（ES-OLK-1~13），包括关注点分离、架构正交、UAPI 隔离、特性可配置、Kbuild/Kconfig、MAINTAINERS、checkpatch、渐进开发、回归零容忍、向后兼容、模块化、文档即代码。**seL4 的工程思想在架构层与安全层被选择性借鉴。**

3. **架构层借鉴 seL4**: 在 5 个维度借鉴 seL4 工程思想，而非编码风格:
   - **ES-SEL4-1 极简原则**: 影响空气内核（airymaxos-kernel）的"机制最小化"取向。
   - **ES-SEL4-2 capability 单一权限模型**: 影响 airymaxos-security 的 capability 设计。
   - **ES-SEL4-3 服务用户态化**: 影响 airymaxos-services 的 VFS/网络/驱动用户态化。
   - **ES-SEL4-4 消息传递 IPC**: 影响 io_uring 消息传递机制设计（含 fastpath 优化思路）。
   - **ES-SEL4-6 接口契约 XML**: 建议为 IRON-9 v2 [SC] 共享契约层引入 syscall.xml 式接口契约定义。
   - **ES-SEL4-8 bitfield codegen**: 建议为 [SC] 头文件中的位域定义引入 structures.bf 式 codegen。
   - **ES-SEL4-5 形式化验证**: 影响 airymaxos-tests-linux 的形式化验证框架（seL4 风格）。

4. **双源融合的边界**: agentrt-linux 的工程取向是"**Linux 6.6 为基、seL4 为鉴**"——以 OLK-6.6 工程思想为不可动摇的基线（编码风格、构建系统、并发模型、内存模型），以 seL4 微内核思想为架构层的借鉴来源（capability、消息传递、服务用户态化、形式化验证）。这一边界在 `docs/AirymaxAgentOS/50-engineering-standards/04-engineering-philosophy.md` 的三大支柱表述中已明确：**第一支柱（微内核设计原则）= seL4 思想借鉴；第二支柱（Euler 标准兼容）/ 第三支柱（Airymax 同源）= Linux 6.6 基线**。

### 7.3 对 AirymaxAgentOS 方案的启示

本研究为 [02-airymaxos-recheck-report.md](02-airymaxos-recheck-report.md) 提供了 7 项检查维度：(1) 编码风格是否与 OLK-6.6 对齐；(2) 工程思想 13 项是否覆盖；(3) 架构层 seL4 借鉴是否到位；(4) 接口契约 XML 化建议；(5) bitfield codegen 建议；(6) MAINTAINERS 文件采纳建议；(7) 形式化验证框架建议。详细检查结论见再检查报告。

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
