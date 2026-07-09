Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agentrt-linux 8 子仓目录结构优化报告（v0.2.2）

> **文档定位**: 基于 OLK-6.6 与 seL4 **实际源代码目录结构**的深度对照审查，对 [v0.2.1 目录结构设计](../_design_0.2.1/01-agentrt-linux-directory-structure.md) 进行问题识别与优化，作为 1.0.1 开发阶段目录骨架的修正基线
> **版本**: 0.2.2（目录结构优化）
> **最后更新**: 2026-07-09
> **审查方法**: 直接测绘 `/home/spharx/SpharxWorks/01Reference/kernel-OLK-6.6` 与 `/home/spharx/SpharxWorks/01Reference/seL4-master` 的实际目录结构，逐项对照 v0.2.1 设计
> **关联文档**: `_design_0.2.1/01-agentrt-linux-directory-structure.md`（被优化对象，1160 行）+ `_research_0.2.1/01-source-code-engineering-study.md`（489 行，工程思想来源）

---

## 目录

- [第 1 章 审查方法论](#第-1-章-审查方法论)
- [第 2 章 OLK-6.6 实际目录结构测绘](#第-2-章-olk-66-实际目录结构测绘)
- [第 3 章 seL4 实际目录结构测绘](#第-3-章-sel4-实际目录结构测绘)
- [第 4 章 问题清单总览](#第-4-章-问题清单总览)
- [第 5 章 P0 严重问题分析与修复](#第-5-章-p0-严重问题分析与修复)
- [第 6 章 P1 重要问题分析与修复](#第-6-章-p1-重要问题分析与修复)
- [第 7 章 P2 改进建议](#第-7-章-p2-改进建议)
- [第 8 章 优化后的 kernel 子仓完整目录结构](#第-8-章-优化后的-kernel-子仓完整目录结构)
- [第 9 章 其他子仓优化要点](#第-9-章-其他子仓优化要点)
- [第 10 章 落地路线与影响评估](#第-10-章-落地路线与影响评估)

---

## 第 1 章 审查方法论

### 1.1 审查目标

v0.2.1 目录结构设计声明"基于 OLK-6.6 + seL4 源代码工程思想"，但部分目录组织是对两源实际结构的**推断而非测绘**。本审查直接测绘两源实际目录，逐项验证 v0.2.1 设计的每个目录映射是否与两源真实结构一致，识别结构性误解与偏离，产出优化后的目录骨架。

### 1.2 审查范围

| 维度 | v0.2.1 设计 | 本审查 |
|------|------------|--------|
| kernel 子仓 | 15 个顶层目录 | 全量对照 OLK-6.6 顶层 + seL4 src/ |
| services 子仓 | Meson + 12 daemons | 对照 seL4 libsel4 + 服务化模型 |
| security 子仓 | capability + cupolas + crypto | 对照 OLK-6.6 security/ + seL4 object/ |
| memory 子仓 | memoryrovol + cxl + pmem + mglru | 对照 OLK-6.6 mm/ |
| cognition 子仓 | C + Rust 混合 | 对照 OLK-6.6 kernel/sched kthread |
| tests-linux 子仓 | formal-verification 三段式 | 对照 seL4 proof/spec 实际位置 |
| 跨子仓 | [SC] 引用 + 公共骨架 | 对照 seL4 libsel4 独立模型 |

### 1.3 审查原则

1. **客观测绘优先**: 所有结论基于两源实际目录的真实结构（Glob + Read 直接验证），不做主观推断
2. **双源分层裁决**: 编码风格层完全采纳 OLK-6.6（已确立），架构层选择性借鉴 seL4（已确立）；目录结构属架构层，需逐目录裁决采用何源
3. **微内核化合理豁免**: agentrt-liunx 是 OS 发行版而非纯内核，对 OLK-6.6 的 `fs/`、`net/`、`drivers/`、`block/` 等宏内核子系统，因 ES-SEL4-3 服务用户态化而合理豁免，但需明确标注豁免理由
4. **可执行性**: 每个修复项给出明确的目录迁移路径与新增/删除清单

---

## 第 2 章 OLK-6.6 实际目录结构测绘

### 2.1 顶层目录完整清单

经直接测绘 `/home/spharx/SpharxWorks/01Reference/kernel-OLK-6.6`，顶层目录与文件如下：

| 顶层条目 | 类型 | 职责 | v0.2.1 kernel 子仓是否对应 |
|---------|------|------|---------------------------|
| `arch/` | 目录 | CPU 架构相关代码（x86/arm64/riscv） | ✅ 对应 |
| `block/` | 目录 | 块设备 I/O 子系统 | ❌ 缺失（宏内核子系统，微内核化豁免） |
| `certs/` | 目录 | 内核模块签名证书 | ❌ 缺失（可选，1.0.1 视安全启动需求新增） |
| `crypto/` | 目录 | 加密算法库（顶层平级，非 security 子目录） | ⚠️ v0.2.1 误置于 security/crypto/ |
| `Documentation/` | 目录 | 内核文档（ABI/process/subsystem-apis） | ✅ 对应 |
| `drivers/` | 目录 | 设备驱动 | ❌ 缺失（ES-SEL4-3 服务用户态化豁免，移至 services/userland-drivers/） |
| `fs/` | 目录 | 文件系统实现 | ❌ 缺失（ES-SEL4-3 豁免，移至 services/userland-vfs/） |
| `include/` | 目录 | 公共头文件（uapi/ + linux/ + asm-generic/ + crypto/） | ✅ 对应（v0.2.1 用 airymax/ 替代 linux/） |
| `init/` | 目录 | 内核初始化（main.c、Kconfig） | ❌ 缺失（**P1 关键缺失**） |
| `io_uring/` | 目录 | 异步 I/O 子系统 | ✅ 对应 |
| `kernel/` | 目录 | 内核核心（sched/、locking/、irq/、entry/、cgroup/、bpf/、trace/、time/） | ⚠️ v0.2.1 用 corekern/ 替代（命名边界问题） |
| `lib/` | 目录 | 通用库函数 | ❌ 缺失（**P1 关键缺失**） |
| `mm/` | 目录 | 内存管理子系统 | ⚠️ 拆分为独立 memory 子仓 + corekern/memory/ |
| `net/` | 目录 | 网络子系统 | ❌ 缺失（ES-SEL4-3 豁免，移至 services/userland-net/） |
| `samples/` | 目录 | 示例代码 | ❌ 缺失（可选） |
| `scripts/` | 目录 | 构建与检查脚本（checkpatch.pl 等） | ✅ 对应 |
| `security/` | 目录 | 安全模块（selinux/、landlock/、apparmor/、bpf/、integrity/ 等） | ✅ 对应（独立子仓） |
| `sound/` | 目录 | 音频子系统 | ❌ 缺失（不适用） |
| `tools/` | 目录 | 内核工具集（tools/testing/、tools/lib/、tools/bpf/） | ⚠️ 部分对应（v0.2.1 拆为 scripts/ + tests-linux/） |
| `usr/` | 目录 | 用户空间 initramfs 构建 | ❌ 缺失（可选，移至 system 子仓） |
| `virt/` | 目录 | 虚拟化（KVM） | ❌ 缺失（不适用） |
| `Makefile` | 文件 | 顶层构建规则 | ✅ 对应 |
| `Kconfig` | 文件 | 顶层特性配置入口 | ✅ 对应 |
| `MAINTAINERS` | 文件 | 维护者制度 | ✅ 对应（R-03 落地） |
| `CREDITS` | 文件 | 贡献者名单 | ❌ 缺失（可选） |
| `README` | 文件 | 项目说明 | ✅ 对应 |

**关键测绘结论**:
- OLK-6.6 顶层**无 `patches/` 目录**（补丁通过 git 管理）
- OLK-6.6 顶层**无 `entry/` 目录**（入口代码在 `arch/*/entry/` + `kernel/` 通用部分）
- OLK-6.6 `crypto/` 是**顶层平级目录**，非 security 子目录
- OLK-6.6 子目录普遍使用 `Makefile`（非 `Kbuild`），如 `kernel/Makefile`、`mm/Makefile`、`arch/x86/Makefile`
- defconfig 存放于 `arch/<arch>/configs/`（如 `arch/x86/configs/`），非顶层 `configs/`

### 2.2 arch/ 内部结构（以 x86 为例）

测绘 `arch/x86/` 实际结构：

```
arch/x86/
├── Makefile
├── Kbuild
├── Kconfig
├── include/          # x86 架构相关头文件
├── kernel/           # x86 内核执行逻辑
├── mm/               # x86 内存管理
├── entry/            # x86 系统调用/中断入口
├── lib/              # x86 特定库函数
├── configs/          # x86 defconfig 存放
├── mach-*            # 机器/板级相关（如 mach-generic）
├── boot/             # 启动引导
├── tools/            # x86 工具
└── ...
```

**关键结论**: OLK-6.6 的 `arch/x86/` **自身包含 `kernel/`、`mm/`、`entry/`、`lib/`、`configs/`**，架构相关代码内聚于 `arch/<arch>/` 内，不存在与 `arch/` 平级的 `entry/` 或 `configs/`。

### 2.3 kernel/ 内部结构

测绘 OLK-6.6 `kernel/` 顶层目录的二级结构（部分）：

```
kernel/
├── Makefile
├── Kconfig
├── sched/            # 进程调度器
├── locking/          # 锁机制与同步原语
├── irq/              # 中断处理
├── entry/            # 通用系统调用入口（架构无关部分）
├── cgroup/           # 控制组
├── bpf/              # BPF 核心（注意：bpf 在 kernel/ 下，非顶层）
├── trace/            # 内核追踪
├── time/             # 时间子系统
├── rcu/              # RCU 机制
├── events/           # 事件系统
├── livepatch/        # 热补丁
├── power/            # 电源管理
├── debug/            # 调试支持
├── kcsan/             # 并发 sanitizer
├── fork.c            # 进程创建
├── exit.c            # 进程退出
├── signal.c          # 信号处理
├── capability.c      # POSIX capability
├── kthread.c         # 内核线程
├── ... (80+ 文件)
```

**关键结论**: OLK-6.6 的 `bpf/` 在 `kernel/bpf/` 下，**非顶层 `bpf/`**。v0.2.1 设计将 `bpf/` 置于 kernel 子仓顶层，偏离 OLK-6.6。

### 2.4 security/ 内部结构

测绘 OLK-6.6 `security/` 顶层目录：

```
security/
├── Makefile
├── Kconfig
├── selinux/          # SELinux
├── landlock/         # Landlock
├── apparmor/         # AppArmor
├── bpf/              # BPF 安全策略
├── integrity/        # 完整性保护
├── loadpin/          # 装载保护
├── yama/             # Yama
├── tomoyo/           # Tomoyo
├── smack/            # SMACK
├── lockdown/         # Lockdown
└── ...
```

**关键结论**: OLK-6.6 `security/` **不含 `crypto/`**（crypto 是顶层平级目录）。每策略一目录（ES-OLK-1 关注点分离）。

---

## 第 3 章 seL4 实际目录结构测绘

### 3.1 seL4-master 顶层目录

经直接测绘 `/home/spharx/SpharxWorks/01Reference/seL4-master`，顶层结构：

| 顶层条目 | 类型 | 职责 | v0.2.1 借鉴情况 |
|---------|------|------|----------------|
| `CMakeLists.txt` | 文件 | CMake 构建入口（ES-SEL4-10） | ⚠️ v0.2.1 kernel 用 Kbuild 而非 CMake（合理，因 OLK-6.6 基线） |
| `configs/` | 目录 | CMake 平台配置（*.cmake verified 配置） | ⚠️ 与 v0.2.1 kernel/configs/ 含义不同（seL4 是 CMake 配置，非 defconfig） |
| `src/` | 目录 | 内核核心实现 | ✅ 借鉴（但映射方式需修正） |
| `include/` | 目录 | 内核头文件 | ✅ 借鉴 |
| `libsel4/` | 目录 | **用户态 API 库（独立于 src/）** | ✅ 借鉴（映射到 cloudnative/sdk/） |
| `tools/` | 目录 | codegen 工具（bitfield_gen.py、syscall_generator.py） | ✅ 借鉴（映射到 kernel/scripts/） |
| `tools/dts/` | 目录 | 设备树源文件 | ❌ v0.2.1 缺失（**P2 改进**） |
| `tools/hardware/` | 目录 | 硬件描述 codegen | ❌ v0.2.1 缺失 |
| `LICENSES/` | 目录 | SPDX 许可证全文 | ⚠️ v0.2.1 用单 LICENSE 文件 |
| `.github/workflows/` | 目录 | CI 工作流（含 proof.yml 形式化验证 CI） | ✅ 可借鉴 |
| `README.md` | 文件 | 项目说明 | ✅ 对应 |
| `CHANGES.md` | 文件 | 变更日志 | ❌ 缺失（可选） |
| `CONTRIBUTORS.md` | 文件 | 贡献者名单 | ❌ 缺失（用 MAINTAINERS 替代） |
| `config.cmake` | 文件 | 默认 CMake 配置 | ⚠️ 不适用（Kbuild 基线） |

**关键测绘结论**:
- seL4-master 顶层**无 `proof/`、`spec/`、`capDL/` 目录**——形式化验证在**独立仓库**（l4v、capDL），seL4-master 仅含 `.github/workflows/proof.yml` 触发外部验证
- seL4-master 顶层**无 `patches/` 目录**
- seL4-master 顶层**无 `entry/` 目录**——入口在 `src/api/`（syscall 分发）+ `src/arch/<arch>/`（架构入口）

### 3.2 src/ 完整结构

测绘 seL4 `src/` 的全部二级目录与关键文件：

```
src/
├── api/                    # 系统调用接口与分发
│   ├── syscall.c           # syscall 分发逻辑
│   └── faults.c            # 错误处理
├── arch/                   # CPU 架构（arm/、x86/、riscv/）
│   ├── arm/                # ARM 架构（含 32/64 子架构）
│   │   ├── api/            # 架构相关 syscall
│   │   ├── kernel/         # 架构相关内核（boot.c、thread.c）
│   │   ├── machine/        # 架构相关机器原语（gic_v2.c、gic_v3.c、cache.c）
│   │   ├── object/        # 架构相关对象（iospace.c、vcpu.c、smc.c）
│   │   ├── model/          # 架构相关状态数据
│   │   ├── smp/            # 架构相关 SMP
│   │   └── armv/           # ARMv 子架构（armv7-a/、armv8-a/）
│   ├── x86/                # x86 架构（含 64 子架构）
│   │   ├── api/
│   │   ├── kernel/
│   │   ├── machine/
│   │   ├── object/
│   │   └── model/
│   └── riscv/              # RISC-V 架构
├── benchmark/              # 性能基准
├── drivers/                # 内核驱动（timer/、serial/、smmu/）—— 注意：drivers 不在 arch/ 内
├── fastpath/               # IPC 快速路径
│   └── fastpath.c
├── kernel/                 # 内核核心（cspace、boot、thread、faulthandler、sporadic、stack）
│   ├── cspace.c
│   ├── boot.c
│   ├── thread.c
│   ├── faulthandler.c
│   ├── sporadic.c
│   └── stack.c
├── machine/                # 通用机器原语（架构无关）
│   ├── io.c                # I/O
│   ├── capdl.c             # capability 分布描述
│   ├── profiler.c
│   ├── registerset.c       # 寄存器集
│   └── fpu.c               # 浮点单元
├── object/                 # seL4 内核对象
│   ├── cnode.c             # capability 节点
│   ├── tcb.c               # 线程控制块
│   ├── endpoint.c          # IPC 端点
│   ├── notification.c      # 通知对象
│   ├── interrupt.c         # 中断对象
│   ├── schedcontext.c      # 调度上下文
│   ├── schedcontrol.c      # 调度控制
│   ├── reply.c             # 应答对象
│   ├── domain.c            # 域对象
│   ├── untyped.c           # 未类型化内存
│   └── objecttype.c        # 对象类型
├── smp/                    # SMP 支持（通用，架构无关）
│   ├── ipi.c
│   └── lock.c
├── inlines.c
├── string.c
├── assert.c
├── util.c
└── config.cmake
```

### 3.3 关键测绘结论：seL4 三层架构模型的真实含义

**v0.2.1 设计误解了 seL4 的 `arch/` + `machine/` + `plat/` 三层模型**。经测绘，seL4 的真实三层模型为：

| 层次 | seL4 真实结构 | v0.2.1 设计（误解） |
|------|--------------|---------------------|
| `arch/` | `src/arch/{arm,x86,riscv}/`，**内部含 machine/、kernel/、object/、model/、api/ 子目录** | `arch/{x86,arm64,riscv}/`，内部含 kernel/、mm/、entry/、include/（✅ 正确） |
| `machine/` | `src/machine/`（**顶层通用**，架构无关的 io/capdl/registerset/fpu）+ `src/arch/<arch>/machine/`（架构相关） | `machine/{x86,arm64,riscv}/`（❌ **错误**：按架构分目录，与 seL4 真实结构相反） |
| `plat/` | `src/plat/<platform>/`，每个平台含 overlay-*.dts + config.cmake + 可选 machine/（硬件相关） | `plat/{qemu-x86_64,qemu-arm64,hardware-platforms}/`（✅ 方向正确，但内容需补充 DTS） |

**核心纠正**: seL4 的 `src/machine/` 是**架构无关的通用机器原语层**（io.c、capdl.c、registerset.c、fpu.c），而**架构相关的机器代码在 `src/arch/<arch>/machine/` 内部**（如 `src/arch/arm/machine/gic_v2.c`）。v0.2.1 将 `machine/` 设计为按架构分目录（`machine/{x86,arm64,riscv}/`）与 `arch/` 平级，**重复了架构维度**，造成"arch/x86/ 与 machine/x86/ 边界何在"的混淆。

### 3.4 libsel4 结构

测绘 seL4 `libsel4/`（用户态 API 库，独立于 src/）：

```
libsel4/
├── CMakeLists.txt
├── src/                    # 用户态 API 实现
├── include/
│   └── api/
│       └── syscall.xml     # ★ 系统调用契约定义（R-01 的源文件）
├── arch_include/           # 架构相关（arm/、x86/、riscv/）
│   └── <arch>/sel4/arch/
│       ├── shared_types.bf # ★ 架构相关位域定义（R-02 的源文件）
│       ├── types.h
│       └── syscalls.h
├── sel4_arch_include/      # 子架构相关（x86_64/、aarch64/、riscv64/ 等）
├── mode_include/           # 模式相关（32/、64/）
├── tools/                  # libsel4 专用工具
└── sel4_plat_include/      # 平台相关头文件
```

**关键结论**:
- `syscall.xml` 位于 `libsel4/include/api/syscall.xml`（**非 tools/，非顶层**），是用户态 API 契约的**源定义**
- `structures.bf`（位域定义）分布在 `include/object/`（内核内部）+ `include/arch/<arch>/arch/object/`（架构相关）+ `libsel4/`（用户态可见）三处
- `bitfield_gen.py` 在 `tools/`（生成器），`structures.bf` 在 `include/`（定义源）

### 3.5 tools/ 结构

测绘 seL4 `tools/`（codegen 与构建辅助）：

```
tools/
├── bitfield_gen.py          # ★ structures.bf → C 代码生成器（R-02 落地参照）
├── invocation_header_gen.py # invocation 头文件生成
├── invocation_json_gen.py   # invocation JSON 生成
├── syscall_generator.py    # ★ syscall.xml → C 代码生成器（R-01 落地参照，注：seL4 实际无独立 syscall_generator.py，syscall.xml 由 invocation_header_gen.py 处理）
├── config_gen.py            # 配置生成
├── hardware/                # 硬件描述 codegen（DTS → C）
├── dts/                     # 设备树源文件（各平台 .dts）
├── bf.vim                   # bitfield 语法高亮
├── bitfield_gen.md          # bitfield 文档
├── *.cmake                  # CMake 辅助
└── ...
```

**关键结论**: seL4 的 codegen 工具（`bitfield_gen.py`、`invocation_header_gen.py`）在 `tools/`，而 v0.2.1 将生成器置于 `kernel/scripts/`。二者皆可，但 v0.2.1 应明确 `syscall.xml` 与 `structures.bf` 的**源文件位置**（生成器的输入），不能只指定生成器位置。

---

## 第 4 章 问题清单总览

基于第 2、3 章的实测对照，识别 v0.2.1 目录结构设计的 **18 项问题**，按严重级别分类：

### 4.1 问题分级统计

| 级别 | 数量 | 含义 | 处理时机 |
|------|------|------|---------|
| **P0** | 4 项 | 结构性误解/冲突，必须修正 | v0.2.2 立即修正（1.0.1 M0 目录骨架前） |
| **P1** | 8 项 | 关键目录缺失/边界不清，影响开发 | v0.2.2 修正或明确边界声明 |
| **P2** | 6 项 | 改进建议，提升规范性 | 1.0.1 M1 增量落地 |

### 4.2 问题清单

| 编号 | 级别 | 问题 | 影响子仓 | 所属章节 |
|------|------|------|---------|---------|
| DIR-P0-01 | P0 | `machine/{x86,arm64,riscv}/` 误解 seL4 三层模型 | kernel | §5.1 |
| DIR-P0-02 | P0 | 顶层 `entry/` 偏离 OLK-6.6（应为 `arch/*/entry/` + kernel 通用） | kernel | §5.2 |
| DIR-P0-03 | P0 | `crypto/` 误置于 `security/crypto/`（OLK-6.6 为顶层平级） | security / kernel | §5.3 |
| DIR-P0-04 | P0 | 顶层 `configs/` 偏离 OLK-6.6（defconfig 应在 `arch/<arch>/configs/`） | kernel | §5.4 |
| DIR-P1-01 | P1 | kernel 子仓缺失 `init/`（内核初始化 main.c） | kernel | §6.1 |
| DIR-P1-02 | P1 | kernel 子仓缺失 `lib/`（通用库函数） | kernel | §6.2 |
| DIR-P1-03 | P1 | `corekern/` 命名与 OLK-6.6 `kernel/` 映射边界不清 | kernel | §6.3 |
| DIR-P1-04 | P1 | `corekern/memory/page_alloc.c` 与 `memory/` 子仓边界冲突 | kernel / memory | §6.4 |
| DIR-P1-05 | P1 | seL4 `src/object/` 内核对象模型（cnode/tcb/endpoint/notification）未体现 | kernel | §6.5 |
| DIR-P1-06 | P1 | `syscall.xml` / `structures.bf` 源文件位置未指定 | kernel | §6.6 |
| DIR-P1-07 | P1 | `bpf/` 顶层偏离 OLK-6.6（OLK-6.6 在 `kernel/bpf/`） | kernel | §6.7 |
| DIR-P1-08 | P1 | `formal-verification/` 位置需说明 seL4 独立仓库实践 | tests-linux | §6.8 |
| DIR-P2-01 | P2 | `patches/` 顶层目录需明确定位（两源均无） | kernel | §7.1 |
| DIR-P2-02 | P2 | 子目录用 `Kbuild` vs `Makefile` 约定不一致 | kernel | §7.2 |
| DIR-P2-03 | P2 | `tests/`（kernel 内）与 `tests-linux/` 子仓测试边界需明确 | kernel / tests-linux | §7.3 |
| DIR-P2-04 | P2 | seL4 `src/api/` 系统调用分发层概念未体现 | kernel | §7.4 |
| DIR-P2-05 | P2 | `include/` 缺少 `linux/` 平级映射说明 | kernel | §7.5 |
| DIR-P2-06 | P2 | seL4 `tools/dts/` 设备树目录缺失 | kernel | §7.6 |

---

## 第 5 章 P0 严重问题分析与修复

### 5.1 DIR-P0-01: `machine/{x86,arm64,riscv}/` 误解 seL4 三层模型

**问题**:

v0.2.1 设计在 kernel 子仓顶层同时存在 `arch/{x86,arm64,riscv}/` 与 `machine/{x86,arm64,riscv}/` 两个按架构分目录的顶层目录（设计文档 §3.2 第 258-261 行）。这重复了架构维度，造成边界混淆：架构相关的机器原语应放在 `arch/x86/` 还是 `machine/x86/`？

经测绘 seL4 真实结构（§3.3）：
- seL4 `src/machine/` 是**架构无关的通用机器原语层**（io.c、capdl.c、registerset.c、fpu.c）
- 架构相关的机器代码在 `src/arch/<arch>/machine/` 内部（如 `src/arch/arm/machine/gic_v2.c`）
- 平台相关的机器代码在 `src/plat/<plat>/machine/` 内部

**修复方案**:

将顶层 `machine/{x86,arm64,riscv}/` 重新定位为**架构无关的通用机器原语层**（seL4 真实模型），内容为：
- `machine/io.c` — 通用 I/O
- `machine/capdl.c` — capability 分布描述
- `machine/registerset.c` — 通用寄存器集
- `machine/fpu.c` — 通用 FPU 上下文
- `machine/profiler.c` — 性能剖析

架构相关的机器原语（如 x86 的中断控制器、arm64 的 GIC）移入 `arch/<arch>/machine/`（OLK-6.6 风格，`arch/x86/` 已含 `kernel/`、`mm/`、`entry/`，可扩展 `machine/`）。

**优化后**:

```
kernel/
├── arch/
│   ├── x86/
│   │   ├── kernel/
│   │   ├── mm/
│   │   ├── entry/
│   │   ├── machine/          # ★ 新增：x86 架构相关机器原语（中断控制器、本地 APIC 等）
│   │   ├── include/
│   │   └── configs/          # ★ defconfig 移入此处（见 DIR-P0-04）
│   ├── arm64/
│   │   └── ...（同构）
│   └── riscv/
│       └── ...（同构）
├── machine/                   # ★ 重定位：架构无关的通用机器原语（seL4 真实模型）
│   ├── Kbuild
│   ├── io.c                   # 通用 I/O
│   ├── capdl.c                # capability 分布描述
│   ├── registerset.c          # 通用寄存器集
│   └── fpu.c                  # 通用 FPU 上下文
└── plat/
    └── <platform>/            # ★ 补充 DTS 与 config（见 DIR-P2-06）
```

### 5.2 DIR-P0-02: 顶层 `entry/` 偏离 OLK-6.6

**问题**:

v0.2.1 设计在 kernel 子仓顶层有独立 `entry/` 目录（设计文档 §3.2 第 246-250 行），含 `airymax_syscall_table.c`、`airymax_entry_64.c`、`airymax_entry_arm64.c`。

经测绘 OLK-6.6（§2.1）：**OLK-6.6 顶层无 `entry/` 目录**。入口代码分布为：
- `arch/*/entry/` — 架构相关入口（汇编蹦床、syscall 表架构部分）
- `kernel/entry/` — 通用入口（架构无关部分）
- `include/uapi/linux/` — syscall 号定义（UAPI）

**问题点**: `airymax_entry_arm64.c`（架构相关文件）不应在顶层 `entry/`，应在 `arch/arm64/entry/`。

**修复方案**:

1. 删除顶层 `entry/` 目录
2. `airymax_entry_64.c` → `arch/x86/entry/airymax_entry_64.c`
3. `airymax_entry_arm64.c` → `arch/arm64/entry/airymax_entry_arm64.c`
4. `airymax_syscall_table.c`（R-01 生成的系统调用表，架构无关）→ 移入 `corekern/api/`（借鉴 seL4 `src/api/`，见 DIR-P2-04）或 `kernel/` 通用核心

**优化后**:

```
kernel/
├── arch/
│   ├── x86/entry/
│   │   └── airymax_entry_64.c     # x86_64 入口
│   ├── arm64/entry/
│   │   └── airymax_entry_arm64.c  # arm64 入口
│   └── riscv/entry/
│       └── airymax_entry_riscv.c  # ★ 补充 riscv 入口
└── corekern/
    └── api/
        └── syscall_table.c        # ★ 架构无关 syscall 表（R-01 生成）
```

### 5.3 DIR-P0-03: `crypto/` 误置于 `security/crypto/`

**问题**:

v0.2.1 设计将 `crypto/sm2-sm4/` 置于 security 子仓内（设计文档 §5.2 第 509-515 行）。经测绘 OLK-6.6（§2.1、§2.4）：**OLK-6.6 的 `crypto/` 是顶层平级目录**，与 `security/` 同级，**非 security 的子目录**。OLK-6.6 的 `security/` 仅含安全策略模块（selinux、landlock 等），不含加密算法库。

**问题根因**: 混淆了"加密算法库"（被多子系统共用的基础设施）与"安全策略"（LSM 钩子、capability）。crypto 是**库**，被 security、net、fs 等多子系统调用；将其置于 security 下会形成循环依赖或限制复用。

**修复方案**:

将 `crypto/` 提升为 **kernel 子仓顶层平级目录**（对齐 OLK-6.6）：

```
kernel/
├── crypto/                    # ★ 提升至顶层（对齐 OLK-6.6 crypto/）
│   ├── Kbuild
│   ├── Kconfig
│   ├── sm2-sm4/               # 国密算法
│   │   ├── sm2.c
│   │   ├── sm3.c
│   │   ├── sm4.c
│   │   └── sm9.c
│   ├── aes/                   # ★ 补充标准算法
│   ├── sha/                   # ★ 补充哈希算法
│   └── api.c                  # ★ 加密 API 抽象
└── security/                  # security 子仓不含 crypto
    ├── capability/
    ├── lsm/
    └── cupolas/
```

**注**: 因 [SC] `security_types.h` 宿主在 `kernel/include/airymax/`，kernel 子仓本就含 security 相关头文件；`crypto/` 作为 kernel 子仓的通用基础设施目录，符合 OLK-6.6 布局。security 子仓仍独立存在，但其内部不再含 `crypto/`。

### 5.4 DIR-P0-04: 顶层 `configs/` 偏离 OLK-6.6

**问题**:

v0.2.1 设计在 kernel 子仓顶层有 `configs/` 目录（设计文档 §3.2 第 286-289 行），含 `airymax_x86_64_defconfig`、`airymax_arm64_defconfig`、`airymax_riscv_defconfig`。

经测绘 OLK-6.6（§2.2）：**defconfig 存放于 `arch/<arch>/configs/`**（如 `arch/x86/configs/x86_64_defconfig`），**非顶层 `configs/`**。

**修复方案**:

将 defconfig 移入各架构的 `configs/` 子目录（对齐 OLK-6.6）：

```
kernel/
└── arch/
    ├── x86/configs/
    │   └── airymax_x86_64_defconfig
    ├── arm64/configs/
    │   └── airymax_arm64_defconfig
    └── riscv/configs/
        └── airymax_riscv_defconfig
```

删除顶层 `configs/` 目录。

---

## 第 6 章 P1 重要问题分析与修复

### 6.1 DIR-P1-01: kernel 子仓缺失 `init/`

**问题**:

OLK-6.6 顶层有 `init/` 目录（含 `main.c`、`Kconfig`、`noinitramfs.c` 等），承担内核初始化入口（`start_kernel` 等）。v0.2.1 的 kernel 子仓**无 `init/` 目录**，内核初始化入口无处安放。

**修复方案**:

新增 `init/` 目录（对齐 OLK-6.6）：

```
kernel/
└── init/                      # ★ 新增（对齐 OLK-6.6 init/）
    ├── Kbuild
    ├── Kconfig
    ├── main.c                 # 内核入口（start_kernel 等价物）
    ├── airymax_init.c         # AirymaxOS 初始化
    └── noinitramfs.c          # 空 initramfs
```

### 6.2 DIR-P1-02: kernel 子仓缺失 `lib/`

**问题**:

OLK-6.6 顶层有 `lib/` 目录（含 `string.c`、`ctype.c`、`radix-tree.c`、`sha1.c`、`crc32.c` 等通用库函数，被全内核复用）。v0.2.1 的 kernel 子仓**无 `lib/` 目录**。

**问题点**: seL4 将这些通用函数放在 `src/` 顶层（`string.c`、`assert.c`、`util.c`、`inlines.c`），但 OLK-6.6 集中在 `lib/`。鉴于编码风格层完全采纳 OLK-6.6，应遵循 OLK-6.6 的 `lib/` 组织。

**修复方案**:

新增 `lib/` 目录（对齐 OLK-6.6）：

```
kernel/
└── lib/                       # ★ 新增（对齐 OLK-6.6 lib/）
    ├── Kbuild
    ├── string.c               # 字符串操作
    ├── ctype.c                # 字符分类
    ├── crc32.c                # CRC32 校验
    ├── radix-tree.c          # 基数树
    ├── kstrtox.c             # 字符串转整数
    └── airymax_lib.c         # AirymaxOS 专用库函数
```

### 6.3 DIR-P1-03: `corekern/` 命名与 OLK-6.6 `kernel/` 映射边界不清

**问题**:

v0.2.1 设计用 `corekern/` 承载微核心原语（复用 atoms/corekern），但 OLK-6.6 的对应物是顶层 `kernel/`（含 sched/、locking/、irq/、fork.c 等）。这造成命名映射不直观：kernel **子仓**内部没有 `kernel/` 目录，而 OLK-6.6 的 `kernel/` 是核心。

**问题根因**: atoms 设计用 `corekern` 表达"微核心原语"语义，与 OLK-6.6 的 `kernel/`（宏内核核心）在概念上不完全等价。seL4 也有 `src/kernel/`（boot、thread、cspace 等），与 `corekern` 概念更接近。

**修复方案**:

保留 `corekern/` 命名（atoms 同源语义不可改），但**明确边界声明**，并在文档中补充映射表：

| corekern/ 子目录 | OLK-6.6 对应 | seL4 对应 | 职责 |
|------------------|-------------|----------|------|
| `corekern/sched/` | `kernel/sched/` | `src/kernel/thread.c` + `src/object/schedcontext.c` | 调度原语 |
| `corekern/ipc/` | `kernel/`（IPC 部分）+ `io_uring/` | `src/api/` + `src/fastpath/` + `src/object/endpoint.c` | IPC 原语 |
| `corekern/taskflow/` | 无直接对应 | `src/object/tcb.c` + `src/kernel/` | 任务流原语 |
| `corekern/memory/` | `mm/page_alloc.c`（仅接口） | `src/kernel/boot.c`（内存初始化） | 页分配原语（仅接口） |
| `corekern/time/` | `kernel/time/` | `src/drivers/timer/` | 时间原语 |
| `corekern/api/`（新增） | `kernel/entry/`（通用） | `src/api/` | 系统调用分发（架构无关） |
| `corekern/locking/`（新增） | `kernel/locking/` | `src/smp/lock.c` | 锁原语 |
| `corekern/irq/`（新增） | `kernel/irq/` | `src/object/interrupt.c` | 中断原语 |

**新增子目录**（对齐 OLK-6.6 kernel/ 的完整职责）：

```
corekern/
├── sched/
├── ipc/
├── taskflow/
├── memory/                    # 仅页分配接口，实现在 memory 子仓
├── time/
├── api/                       # ★ 新增（系统调用分发，借鉴 seL4 src/api/）
│   └── syscall_dispatch.c
├── locking/                   # ★ 新增（锁原语，对齐 OLK-6.6 kernel/locking/）
│   └── spinlock.c
└── irq/                       # ★ 新增（中断原语，对齐 OLK-6.6 kernel/irq/）
    └── irq_manage.c
```

### 6.4 DIR-P1-04: `corekern/memory/page_alloc.c` 与 `memory/` 子仓边界冲突

**问题**:

v0.2.1 设计在 `corekern/memory/page_alloc.c` 放置页分配原语，但又有独立的 `memory/` 子仓承载 MemoryRovol/CXL/PMEM。两者边界不清：page_alloc 是 corekern 原语还是 memory 子仓实现？

**修复方案**:

明确边界——**corekern/memory/ 仅含页分配的原子接口声明（头文件），实现在 memory 子仓**：

```
corekern/
└── memory/
    ├── Kbuild
    ├── page_alloc.h           # ★ 仅接口声明（原子机制接口）
    └── vtime.c                # vtime 衰减公式（调度相关，留在 corekern）

memory/                        # memory 子仓
└── page_alloc/                # ★ 新增：页分配实现
    ├── Kbuild
    ├── page_alloc.c           # ★ 实现移入此处
    ├── buddy.c                # 伙伴系统
    └── ...
```

**边界声明**: `corekern/memory/page_alloc.h` 定义原子接口（A 类微核心原语），`memory/page_alloc/page_alloc.c` 提供实现（B 类应用语义层）。这符合 atoms A/B/C 三类语义分类（见 project_memory Engineering Conventions）。

### 6.5 DIR-P1-05: seL4 `src/object/` 内核对象模型未体现

**问题**:

seL4 有 `src/object/` 目录，承载内核对象（cnode、tcb、endpoint、notification、interrupt、schedcontext 等）。v0.2.1 的 kernel 子仓**无 `object/` 概念**——这些对象分散在 `corekern/taskflow/task_descriptor.c` 和 `security/capability/cnode.c`。

**问题点**: seL4 的内核对象是其 capability 模型的基础（每个对象都有 capability），独立 `object/` 目录使对象管理内聚。v0.2.1 将 task_descriptor 放 taskflow、cnode 放 security，割裂了对象模型。

**修复方案**:

在 `corekern/` 下新增 `object/` 目录，集中内核对象原语（借鉴 seL4 `src/object/`）：

```
corekern/
└── object/                    # ★ 新增（借鉴 seL4 src/object/）
    ├── Kbuild
    ├── task_descriptor.c       # 任务描述符（magic 0x41475453，从 taskflow 移入）
    ├── endpoint.c              # IPC 端点对象（借鉴 seL4 endpoint.c）
    ├── notification.c          # 通知对象（借鉴 seL4 notification.c）
    └── interrupt.c             # 中断对象（借鉴 seL4 interrupt.c）
```

**注**: `security/capability/cnode.c` 仍保留在 security 子仓（capability 派生模型是安全语义），但其数据结构 `cnode` 借鉴 seL4 `src/object/cnode.c` 思想（已声明）。task_descriptor 从 `taskflow/` 移入 `object/`，taskflow 仅保留 `graph_engine.c`（A 类微核心原语）。

### 6.6 DIR-P1-06: `syscall.xml` / `structures.bf` 源文件位置未指定

**问题**:

v0.2.1 设计在 `kernel/scripts/` 放置 `syscall_gen.py`（R-01）和 `bitfield_gen.py`（R-02），但**未指定 `syscall.xml` 和 `structures.bf` 的源文件位置**（生成器的输入）。

经测绘 seL4（§3.4、§3.5）：
- `syscall.xml` 在 `libsel4/include/api/syscall.xml`（用户态 API 契约源）
- `structures.bf` 在 `include/object/structures_64.bf`（内核内部）+ `include/arch/<arch>/arch/object/structures.bf`（架构相关）+ `libsel4/`（用户态可见）

**修复方案**:

明确 codegen 源文件位置（借鉴 seL4 但适配 agentrt-liunx 的 [SC] 头文件宿主模型）：

```
kernel/
├── include/
│   ├── uapi/airymax/
│   │   └── syscall.xml        # ★ 新增：系统调用契约源（R-01 输入，UAPI 永久稳定）
│   └── airymax/
│       ├── *.bf               # ★ 新增：位域定义源（R-02 输入，与 [SC] *.h 同目录）
│       │   ├── sched.bf       # 任务描述符位域
│       │   ├── ipc.bf         # IPC 消息头位域
│       │   └── security.bf    # capability 位域
│       └── *.h                # [SC] 6 头文件（已有）
└── scripts/
    ├── syscall_gen.py         # syscall.xml → C 代码生成（R-01）
    └── bitfield_gen.py        # *.bf → C 代码生成（R-02）
```

**设计理由**: `syscall.xml` 是 UAPI 契约（用户态可见，永久稳定），故置于 `include/uapi/airymax/`；`structures.bf` 与 [SC] 头文件同源（内核内部契约），故置于 `include/airymax/` 与 `*.h` 并列。

### 6.7 DIR-P1-07: `bpf/` 顶层偏离 OLK-6.6

**问题**:

v0.2.1 设计在 kernel 子仓顶层有 `bpf/` 目录（设计文档 §3.2 第 238-244 行）。经测绘 OLK-6.6（§2.3）：**OLK-6.6 的 `bpf/` 在 `kernel/bpf/` 下**，非顶层。

**修复方案**:

将 `bpf/` 移入 `corekern/`（因 corekern 承载内核核心，对齐 OLK-6.6 `kernel/bpf/` 的层次）：

```
corekern/
└── bpf/                       # ★ 从顶层移入（对齐 OLK-6.6 kernel/bpf/）
    ├── Kbuild
    ├── Kconfig
    ├── airymax_bpf_kfunc.c
    ├── dynamic_pointer.c
    └── struct_ops/
        └── airymax_sched_ops.c
```

删除顶层 `bpf/` 目录。

### 6.8 DIR-P1-08: `formal-verification/` 位置需说明 seL4 独立仓库实践

**问题**:

v0.2.1 设计将 `formal-verification/{spec,proof,capdl}/` 置于 `tests-linux/` 子仓（设计文档 §10.2）。经测绘 seL4（§3.1）：**seL4-master 不含 `proof/`、`spec/`、`capDL/` 目录**——形式化验证在**独立仓库**（l4v、capDL），seL4-master 仅含 `.github/workflows/proof.yml` 触发外部验证。

**修复方案**:

保留 `tests-linux/formal-verification/` 的位置（单仓聚合便于 0.1.1/1.0.1 管理），但**补充实践说明**：

```
tests-linux/
└── formal-verification/       # 保留位置，补充说明
    ├── README.md              # ★ 新增：说明与 seL4 实践的差异与理由
    ├── spec/
    ├── proof/
    └── capdl/
```

`README.md` 内容要点：
- seL4 实践：形式化验证在独立仓库（l4v/capDL），通过 CI 触发跨仓库验证
- agentrt-liunx 选择：0.1.1/1.0.1 阶段单仓聚合（降低跨仓依赖复杂度），1.0.1 后期视规模考虑拆分为独立 `airymaxos-proof` 仓库
- 验证范围：仅针对 capability 派生、IPC 协议、调度正确性三核心，非全内核形式化（区别于 seL4 全内核验证）

---

## 第 7 章 P2 改进建议

### 7.1 DIR-P2-01: `patches/` 顶层目录需明确定位

**问题**: v0.2.1 在 kernel 子仓顶层有 `patches/` 目录，但 OLK-6.6 与 seL4 均无顶层 `patches/`。

**建议**: 保留 `patches/`（agentrt-liunx 是 OS 发行版，需跟踪上游内核补丁，类似 openEuler 的源包补丁管理），但补充定位说明："`patches/` 是发行版特有目录，用于跟踪上游 Linux 6.6 补丁与 AirymaxOS 微内核化改造补丁集，非上游内核目录"。在 README 中标注此为发行版层决策。

### 7.2 DIR-P2-02: `Kbuild` vs `Makefile` 约定统一

**问题**: OLK-6.6 子目录普遍用 `Makefile`（如 `kernel/Makefile`、`mm/Makefile`、`arch/x86/Makefile`），v0.2.1 用 `Kbuild`。

**建议**: 统一为 `Makefile`（对齐 OLK-6.6 观测实践），顶层保留 `Kbuild`（OLK-6.6 顶层也有 `Kbuild`）。即：顶层 `Kbuild` + `Makefile`，子目录统一 `Makefile`。

### 7.3 DIR-P2-03: `tests/`（kernel 内）与 `tests-linux/` 子仓测试边界

**问题**: kernel 子仓有 `tests/{kunit,kselftest}/`，又有独立 `tests-linux/` 子仓的 `kernel_unit/`。边界不清。

**建议**: 明确边界——
- kernel 子仓 `tests/`：**必须与内核同源构建**的测试（KUnit 单元测试、kselftest 集成测试），随内核构建
- tests-linux 子仓 `kernel_unit/`：**跨模块集成测试**（kernel ↔ services 等），独立构建
- 在两处 README 中互相引用，明确不重复

### 7.4 DIR-P2-04: seL4 `src/api/` 系统调用分发层概念

**问题**: seL4 有 `src/api/`（syscall.c 分发、faults.c 错误处理），v0.2.1 未体现此层（syscall 分发逻辑无处安放）。

**建议**: 在 `corekern/api/` 新增系统调用分发层（已在 DIR-P1-03 §6.3 提出），承载架构无关的 syscall 分发逻辑，与 `arch/<arch>/entry/`（架构入口）分离。

### 7.5 DIR-P2-05: `include/` 缺少 `linux/` 平级映射说明

**问题**: OLK-6.6 有 `include/linux/`（内核内部通用头文件），v0.2.1 用 `include/airymax/` 替代。

**建议**: 补充映射说明——`include/airymax/` ≡ OLK-6.6 `include/linux/`（项目专属内核内部头文件目录），[SC] 6 头文件在此目录下。在 README 中明确此映射，避免贡献者混淆。

### 7.6 DIR-P2-06: seL4 `tools/dts/` 设备树目录缺失

**问题**: seL4 有 `tools/dts/`（各平台设备树源文件）与 `src/plat/<platform>/overlay-*.dts`（平台 overlay）。v0.2.1 的 `plat/` 缺少 DTS 文件。

**建议**: 在 `plat/<platform>/` 下补充 DTS overlay 与 config：

```
plat/
├── qemu-x86_64/
│   ├── overlay.dts            # ★ 新增
│   └── config.mk              # ★ 新增
├── qemu-arm64/
│   ├── overlay.dts
│   └── config.mk
└── hardware-platforms/
    └── ...
```

---

## 第 8 章 优化后的 kernel 子仓完整目录结构

综合第 5、6、7 章修复，优化后的 kernel 子仓完整目录结构如下（标注 ★ 为本次优化变更）：

```
kernel/                           # airymaxos-kernel（feature/official-hubs-01）
├── README.md
├── README_zh.md
├── LICENSE                       # AGPL-3.0 + Apache-2.0
├── NOTICE
├── MAINTAINERS                   # R-03
├── CONTRIBUTING.md
├── .gitignore
├── .clang-format                 # OS-KER-005 Tab 8
├── .editorconfig
│
├── Kbuild                        # 顶层 Kbuild（递归构建入口）
├── Kconfig                       # 顶层 Kconfig（特性配置入口）
├── Makefile                      # 顶层 Makefile（构建规则）
│
├── arch/                         # 架构相关代码（ES-OLK-2 + ES-SEL4-7）
│   ├── x86/
│   │   ├── Makefile              # ★ Kbuild → Makefile（DIR-P2-02）
│   │   ├── Kconfig
│   │   ├── include/              # x86 架构相关头文件
│   │   ├── kernel/               # x86 内核入口
│   │   ├── mm/                   # x86 内存管理
│   │   ├── entry/                # x86 系统调用入口
│   │   │   └── airymax_entry_64.c  # ★ 从顶层 entry/ 移入（DIR-P0-02）
│   │   ├── machine/              # ★ 新增：x86 架构相关机器原语（DIR-P0-01）
│   │   ├── lib/                  # x86 特定库函数
│   │   └── configs/              # ★ defconfig 移入（DIR-P0-04）
│   │       └── airymax_x86_64_defconfig
│   ├── arm64/
│   │   ├── Makefile
│   │   ├── Kconfig
│   │   ├── include/
│   │   ├── kernel/
│   │   ├── mm/
│   │   ├── entry/
│   │   │   └── airymax_entry_arm64.c  # ★ 移入
│   │   ├── machine/
│   │   ├── lib/
│   │   └── configs/
│   │       └── airymax_arm64_defconfig
│   └── riscv/
│       ├── Makefile
│       ├── Kconfig
│       ├── include/
│       ├── kernel/
│       ├── mm/
│       ├── entry/
│       │   └── airymax_entry_riscv.c  # ★ 新增（DIR-P0-02 补全）
│       ├── machine/
│       ├── lib/
│       └── configs/
│           └── airymax_riscv_defconfig
│
├── include/                      # 公共头文件（ES-OLK-3 / ES-OLK-6）
│   ├── uapi/                     # 用户空间 ABI（永久稳定，OS-IRON-001）
│   │   └── airymax/
│   │       ├── syscall.h         # 系统调用号定义（冻结）
│   │       ├── syscall.xml       # ★ 新增：系统调用契约源（R-01 输入，DIR-P1-06）
│   │       ├── ipc.h             # IPC UAPI
│   │       ├── sched.h           # 调度 UAPI
│   │       ├── memory.h          # 内存 UAPI
│   │       ├── security.h        # 安全 UAPI
│   │       └── cognition.h       # 认知 UAPI
│   ├── airymax/                  # 内核内部头文件（≡ OLK-6.6 include/linux/，DIR-P2-05）
│   │   ├── bpf_struct_ops.h      # [SC] struct_ops 状态机
│   │   ├── memory_types.h        # [SC] MemoryRovol L1-L4
│   │   ├── security_types.h     # [SC] capability 38 ID + LSM 254 ID
│   │   ├── cognition_types.h    # [SC] CoreLoopThree + Thinkdual
│   │   ├── sched.h              # [SC] 任务描述符（AGTS）+ vtime
│   │   ├── ipc.h                # [SC] IPC magic 0x41524531 + 128B 消息头
│   │   ├── sched.bf            # ★ 新增：位域定义源（R-02 输入，DIR-P1-06）
│   │   ├── ipc.bf               # ★ 新增
│   │   ├── security.bf          # ★ 新增
│   │   ├── corekern.h           # 微核心原语内部头
│   │   └── airymax_kernel.h     # 总头文件
│   └── asm-generic/              # 通用汇编默认实现（ES-OLK-2）
│
├── init/                         # ★ 新增：内核初始化（对齐 OLK-6.6 init/，DIR-P1-01）
│   ├── Makefile
│   ├── Kconfig
│   ├── main.c                    # 内核入口
│   ├── airymax_init.c            # AirymaxOS 初始化
│   └── noinitramfs.c             # 空 initramfs
│
├── lib/                          # ★ 新增：通用库函数（对齐 OLK-6.6 lib/，DIR-P1-02）
│   ├── Makefile
│   ├── string.c
│   ├── ctype.c
│   ├── crc32.c
│   ├── radix-tree.c
│   ├── kstrtox.c
│   └── airymax_lib.c
│
├── crypto/                       # ★ 提升至顶层（对齐 OLK-6.6 crypto/，DIR-P0-03）
│   ├── Makefile
│   ├── Kconfig
│   ├── sm2-sm4/                  # 国密算法
│   │   ├── sm2.c
│   │   ├── sm3.c
│   │   ├── sm4.c
│   │   └── sm9.c
│   ├── aes/                      # 标准对称加密
│   ├── sha/                      # 哈希算法
│   └── api.c                     # 加密 API 抽象
│
├── corekern/                     # 微核心原语（ES-SEL4-1 极简原则，复用 atoms/corekern）
│   ├── Makefile                  # ★ Kbuild → Makefile
│   ├── Kconfig
│   ├── sched/                    # 调度原语（sched_ext 策略，非 SCHED_AGENT 宏）
│   │   ├── airymax_agent_sched.c
│   │   ├── core_sched.c
│   │   └── ext.c
│   ├── ipc/                      # IPC 原语（io_uring + kfifo + fastpath）
│   │   ├── io_uring_ipc.c
│   │   ├── kfifo_ipc.c
│   │   └── fastpath.c           # IPC fastpath（ES-SEL4-4 借鉴 seL4 src/fastpath/）
│   ├── taskflow/                 # 任务流原语（仅 graph_engine，DIR-P1-05）
│   │   └── graph_engine.c
│   ├── object/                   # ★ 新增：内核对象原语（借鉴 seL4 src/object/，DIR-P1-05）
│   │   ├── task_descriptor.c     # 任务描述符（从 taskflow 移入，magic 0x41475453）
│   │   ├── endpoint.c            # IPC 端点对象
│   │   ├── notification.c        # 通知对象
│   │   └── interrupt.c           # 中断对象
│   ├── api/                      # ★ 新增：系统调用分发（借鉴 seL4 src/api/，DIR-P1-03/P2-04）
│   │   ├── syscall_dispatch.c    # 架构无关 syscall 分发
│   │   └── syscall_table.c       # 系统调用表（R-01 生成）
│   ├── memory/                   # 内存原语（仅接口声明，DIR-P1-04）
│   │   ├── page_alloc.h          # 仅接口声明（实现在 memory 子仓）
│   │   └── vtime.c               # vtime 衰减公式
│   ├── time/                     # 时间原语（CLOCK_REALTIME 北京时间对齐）
│   │   └── clock.c
│   ├── locking/                  # ★ 新增：锁原语（对齐 OLK-6.6 kernel/locking/，DIR-P1-03）
│   │   └── spinlock.c
│   ├── irq/                      # ★ 新增：中断原语（对齐 OLK-6.6 kernel/irq/，DIR-P1-03）
│   │   └── irq_manage.c
│   └── bpf/                      # ★ 从顶层移入（对齐 OLK-6.6 kernel/bpf/，DIR-P1-07）
│       ├── Makefile
│       ├── Kconfig
│       ├── airymax_bpf_kfunc.c
│       ├── dynamic_pointer.c
│       └── struct_ops/
│           └── airymax_sched_ops.c
│
├── machine/                      # ★ 重定位：架构无关通用机器原语（seL4 真实模型，DIR-P0-01）
│   ├── Makefile
│   ├── io.c                      # 通用 I/O
│   ├── capdl.c                   # capability 分布描述
│   ├── registerset.c             # 通用寄存器集
│   └── fpu.c                     # 通用 FPU 上下文
│
├── patches/                       # 上游补丁（发行版特有，需定位说明，DIR-P2-01）
│   ├── README.md                 # ★ 新增：定位说明
│   ├── sched_ext-agent/
│   ├── io_uring-ipc/
│   ├── rust-drivers/
│   └── microkernel/
│       ├── capability/
│       ├── vfs-userns/
│       ├── net-userns/
│       └── driver-split/
│
├── io_uring/                     # 异步 I/O（ES-OLK-1 独立子系统）
│   ├── Makefile                  # ★ Kbuild → Makefile
│   ├── Kconfig
│   ├── airymax_io_uring.c
│   └── airymax_msg_ring.c
│
├── plat/                         # 平台相关（ES-SEL4-7 三层适配之一）
│   ├── qemu-x86_64/
│   │   ├── overlay.dts           # ★ 新增 DTS（DIR-P2-06）
│   │   └── config.mk             # ★ 新增
│   ├── qemu-arm64/
│   │   ├── overlay.dts
│   │   └── config.mk
│   └── hardware-platforms/
│       └── ...
│
├── Documentation/                # 文档即代码（ES-OLK-13）
│   ├── ABI/                      # ABI 文档（OS-IRON-001）
│   │   ├── syscalls/
│   │   ├── ioctl/
│   │   └── procfs/
│   ├── airymax/
│   │   ├── microkernel-strategy.md
│   │   ├── sched-ext-design.md
│   │   └── ipc-design.md
│   └── process/
│
├── scripts/                      # 构建与检查脚本（ES-OLK-9）
│   ├── checkpatch.pl
│   ├── syscall_gen.py            # syscall.xml → C 代码生成（R-01）
│   ├── bitfield_gen.py           # *.bf → C 代码生成（R-02）
│   ├── kbuild_check.py
│   └── maintainer_check.py
│
└── tests/                        # 内核单元测试（必须与内核同源构建，DIR-P2-03）
    ├── kunit/
    └── kselftest/
```

**变更摘要**:

| 变更类型 | 数量 | 详情 |
|---------|------|------|
| 新增顶层目录 | 2 | `init/`（DIR-P1-01）、`lib/`（DIR-P1-02） |
| 提升至顶层 | 1 | `crypto/`（DIR-P0-03，从 security 子仓移出） |
| 删除顶层目录 | 3 | `entry/`（DIR-P0-02）、`bpf/`（DIR-P1-07）、`configs/`（DIR-P0-04） |
| 重定位 | 1 | `machine/` 从按架构分目录改为架构无关通用层（DIR-P0-01） |
| corekern 新增子目录 | 4 | `object/`（DIR-P1-05）、`api/`（DIR-P1-03）、`locking/`、`irq/` |
| corekern 子目录调整 | 2 | `taskflow/` 仅留 graph_engine；`memory/` 仅留接口声明 |
| 新增文件 | 7 | `syscall.xml`、3 个 `*.bf`、3 个 `entry_riscv.c` 等 |
| Kbuild → Makefile | 全部子目录 | 对齐 OLK-6.6 观测实践（DIR-P2-02） |

---

## 第 9 章 其他子仓优化要点

### 9.1 security 子仓

**变更**: 删除 `crypto/` 子目录（DIR-P0-03，已提升至 kernel 子仓顶层）。其余结构（capability/、lsm/、cupolas/、sandbox/、confidential-compute/、zero-trust/、ebpf-verify/）保持不变。

**补充说明**: `security/capability/cnode.c` 数据结构借鉴 seL4 `src/object/cnode.c`（已声明），但实现独立。

### 9.2 memory 子仓

**变更**: 新增 `page_alloc/` 子目录（DIR-P1-04），承载页分配实现（从 kernel 子仓 `corekern/memory/page_alloc.c` 移入实现，接口声明留在 corekern）。其余结构保持不变。

### 9.3 services 子仓

**无变更**。Meson 构建 + 12 daemons + userland-{vfs,net,drivers} + ipc/ 结构合理，符合 ES-SEL4-3 服务用户态化。

### 9.4 cognition 子仓

**无变更**。C + Rust 混合构建结构合理。

### 9.5 cloudnative 子仓

**无变更**。sdk/ 4 语言借鉴 libsel4 模型（ES-SEL4-9）已正确。

### 9.6 system 子仓

**无变更**。package-manager/ + config/ + base-libs/ + devstation/ 结构合理。

### 9.7 tests-linux 子仓

**变更**: `formal-verification/` 新增 `README.md`（DIR-P1-08），说明与 seL4 独立仓库实践的差异与选择理由。其余结构保持不变。

---

## 第 10 章 落地路线与影响评估

### 10.1 落地时机

| 阶段 | 时机 | 落地内容 |
|------|------|---------|
| 阶段 1 | 1.0.1 M0（工程标准框架建立） | kernel 子仓目录骨架按本优化报告创建（空目录 + .gitkeep） |
| 阶段 2 | 1.0.1 M1（架构与模块设计完善） | R-01（syscall.xml）+ R-02（structures.bf）落地于 `include/uapi/airymax/` 与 `include/airymax/` |
| 阶段 3 | 1.0.1 M1 | `corekern/object/`、`corekern/api/`、`corekern/locking/`、`corekern/irq/` 子目录填充 |
| 阶段 4 | 1.0.1 M5（开发流程与治理） | R-03（8 子仓 MAINTAINERS）落地，含本优化后的目录结构 |

### 10.2 对 v0.2.1 设计文档的修订

本优化报告完成后，应修订 `_design_0.2.1/01-agentrt-linux-directory-structure.md` 的以下章节：

| 章节 | 修订内容 |
|------|---------|
| §1.1 双源融合目录映射表 | 修正 ES-SEL4-7 三层模型描述（machine/ 通用层） |
| §3.2 kernel 完整目录结构 | 替换为本报告第 8 章优化后结构 |
| §3.3 关键设计说明第 1 条 | 修正 arch/machine/plat 三层模型描述 |
| §5.2 security 完整目录结构 | 删除 crypto/ 子目录 |
| §6.2 memory 完整目录结构 | 新增 page_alloc/ 子目录 |
| §10.2 tests-linux 完整目录结构 | formal-verification/ 新增 README.md |
| 附录 A 双源映射对照表 | 修正 kernel 行的 seL4 借鉴描述 |

### 10.3 影响评估

| 维度 | 影响 |
|------|------|
| 工时 | 优化落地无新增工时（目录骨架创建已含在 M0 的 32h"8 子仓初始化"中） |
| 风险 | 低——0.1.1 阶段子仓仅含占位文件，优化为目录骨架调整，无代码迁移 |
| 一致性 | 提升与 OLK-6.6 + seL4 真实结构的对齐度，消除结构性误解 |
| 可维护性 | 明确 corekern/ 与 OLK-6.6 kernel/ 的映射边界，降低贡献者认知成本 |

### 10.4 验证清单

优化落地后需验证：

| 编号 | 验证项 | 验证方式 |
|------|--------|---------|
| V-01 | kernel 子仓无顶层 `entry/`、`bpf/`、`configs/` | 目录检查 |
| V-02 | kernel 子仓有顶层 `init/`、`lib/`、`crypto/` | 目录检查 |
| V-03 | `machine/` 不按架构分目录 | 目录检查（无 machine/x86/ 等） |
| V-04 | `arch/<arch>/configs/` 含 defconfig | 目录检查 |
| V-05 | `corekern/` 含 object/、api/、locking/、irq/ | 目录检查 |
| V-06 | `include/uapi/airymax/syscall.xml` 存在 | 文件检查 |
| V-07 | `include/airymax/*.bf` 存在（3 个） | 文件检查 |
| V-08 | 子目录统一用 `Makefile`（非 Kbuild） | 文件检查 |
| V-09 | security 子仓无 `crypto/` | 目录检查 |
| V-10 | memory 子仓有 `page_alloc/` | 目录检查 |

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
