Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agentrt-linux 8 子仓完整项目目录结构设计（v0.2.1）

> **文档定位**: 基于 [OLK-6.6 与 seL4 源代码工程思想研究报告](../../00-reviews/_research_0.2.1/01-source-code-engineering-study.md) 提取的目录组织模式（OLK-6.6: include/{uapi,linux,asm-generic} + kernel/{sched,...} + mm/ + security/ + io_uring/ + arch/ + scripts/ + Documentation/ + MAINTAINERS；seL4: src/{api,kernel,object,fastpath,arch,machine,plat} + include/ + libsel4/ + proof/ + spec/ + capDL/），为 `OpenAirymax/agentrt-linux/` 下 8 个子仓设计完整的内部项目目录结构，作为 1.0.1 开发阶段的目录骨架。
> **版本**: 0.2.1（目录结构设计）
> **最后更新**: 2026-07-09
> **设计原则**: (1) Linux 6.6 内核基线对齐（ES-OLK-1~13）；(2) seL4 架构层借鉴（ES-SEL4-1~10）；(3) IRON-9 v2 [SC] 共享契约层 6 个头文件落地于 include/airymax/；(4) Airymax 同源（atoms/corekern 复用）；(5) 双许可证 AGPL-3.0+Apache-2.0；(6) 8 子仓依赖层次（L2-L7）
> **当前状态**: 0.1.1 各子仓仅含 README/LICENSE/NOTICE/.gitignore 占位文件，本设计为 1.0.1 开发提供目标骨架

---

## 目录

- [第 1 章 设计总则](#第-1-章-设计总则)
- [第 2 章 管理仓 agentrt-linux 目录结构](#第-2-章-管理仓-agentrt-linux-目录结构)
- [第 3 章 airymaxos-kernel（kernel/）](#第-3-章-airymaxos-kernelkernel)
- [第 4 章 airymaxos-services（services/）](#第-4-章-airymaxos-servicesservices)
- [第 5 章 airymaxos-security（security/）](#第-5-章-airymaxos-securitysecurity)
- [第 6 章 airymaxos-memory（memory/）](#第-6-章-airymaxos-memorymemory)
- [第 7 章 airymaxos-cognition（cognition/）](#第-7-章-airymaxos-cognitioncognition)
- [第 8 章 airymaxos-cloudnative（cloudnative/）](#第-8-章-airymaxos-cloudnativecloudnative)
- [第 9 章 airymaxos-system（system/）](#第-9-章-airymaxos-systemsystem)
- [第 10 章 airymaxos-tests-linux（tests-linux/）](#第-10-章-airymaxos-tests-linuxtests-linux)
- [第 11 章 跨子仓一致性约束](#第-11-章-跨子仓一致性约束)

---

## 第 1 章 设计总则

### 1.1 双源融合的目录映射

本设计将研究报告的"双源融合裁决"落实为目录组织规则：

| 裁决来源 | 目录映射 | 适用子仓 |
|---------|---------|---------|
| ES-OLK-1 关注点分离 | 8 子仓顶层划分即 8 个关注点 | 全部 |
| ES-OLK-2 架构正交 | `arch/{x86,arm64,riscv}/` 隔离架构相关代码 | kernel |
| ES-OLK-3 / ES-OLK-6 UAPI 物理隔离 | `include/uapi/airymax/`（UAPI）与 `include/airymax/`（内部）分离 | kernel / security / memory / cognition |
| ES-OLK-4 / ES-OLK-7 Kconfig + Kbuild | `Kconfig` + `Kbuild` + `Makefile` 三层构建 | kernel / security / memory / cognition |
| ES-OLK-8 MAINTAINERS | 每子仓根 `MAINTAINERS` 文件（R-03 落地） | 全部 |
| ES-OLK-9 规范可执行 | `scripts/` 检查脚本 + CI 集成 | 全部 |
| ES-OLK-13 文档即代码 | `Documentation/` 子目录 | kernel |
| ES-SEL4-1 极简原则 | `corekern/` 仅保留 4 原子机制（IPC/内存/任务/时间） | kernel |
| ES-SEL4-2 capability 单一模型 | `capability/` 独立模块 + [SC] security_types.h | security |
| ES-SEL4-3 服务用户态化 | `userland-vfs/` `userland-net/` `userland-drivers/` | services |
| ES-SEL4-4 消息传递 IPC | `ipc/` 基于 io_uring，含 fastpath 优化 | kernel / services |
| ES-SEL4-5 形式化验证 | `formal-verification/{spec,proof}/`（seL4 风格） | tests-linux |
| ES-SEL4-7 架构正交分层 | `arch/` + `machine/` + `plat/` 三层（kernel 子仓） | kernel |
| ES-SEL4-9 用户态 API 库独立 | `sdk/`（libsel4 模型借鉴，4 语言） | cloudnative |

### 1.2 公共骨架（8 子仓共有）

每个子仓根目录必须包含以下公共文件（双许可证 + 治理 + 元信息）：

```
<submodule>/
├── README.md              # 英文 README
├── README_zh.md           # 中文 README
├── LICENSE                # AGPL-3.0 + Apache-2.0 双许可证全文
├── NOTICE                 # 版权、商标、第三方声明
├── MAINTAINERS            # 维护者制度（R-03 落地，ES-OLK-8）
├── .gitignore
├── .clang-format          # C 代码格式（OS-KER-005 Tab 8，仅 kernel/security/memory/cognition）
├── .editorconfig          # 编辑器统一配置
└── CONTRIBUTING.md        # 贡献指南（DCO + Signed-off-by + 审查流程）
```

### 1.3 子仓类型与构建系统

8 子仓按代码形态分为 4 类，每类对应不同构建系统：

| 类型 | 子仓 | 构建系统 | 依据 |
|------|------|---------|------|
| 内核态 C | kernel / security / memory / cognition（kthread 部分） | Kbuild + Kconfig + Makefile | ES-OLK-7（与 Linux 6.6 一致） |
| 用户态 C | services（daemons） | Meson（推荐，现代用户态构建） | ES-SEL4-10 现代构建系统借鉴 |
| 用户态多语言 | cloudnative（Go/Rust/TS） / cognition（Wasm/Rust） / system（Rust/Python） | Cargo + Go Modules + tsc + Meson（按语言） | 各语言生态主流 |
| 测试 | tests-linux | CTest + Cargo + Go + Shell | 多语言测试聚合 |

### 1.4 IRON-9 v2 [SC] 共享契约层落地

6 个 [SC] 共享契约头文件统一落地于 `kernel/include/airymax/`（kernel 子仓为 [SC] 头文件的"宿主"，其他子仓通过 git submodule 或 include path 引用）：

| [SC] 头文件 | 落地路径 | 用途 |
|------------|---------|------|
| bpf_struct_ops.h | kernel/include/airymax/bpf_struct_ops.h | struct_ops 状态机 + common_value |
| memory_types.h | kernel/include/airymax/memory_types.h | MemoryRovol L1-L4 + GFP 掩码 + PMEM |
| security_types.h | kernel/include/airymax/security_types.h | capability 38 ID + LSM 254 ID + Cupolas blob |
| cognition_types.h | kernel/include/airymax/cognition_types.h | CoreLoopThree 三阶段 + Thinkdual + LLM 推理 |
| sched.h | kernel/include/airymax/sched.h | 任务描述符（magic 0x41475453）+ vtime + 优先级 |
| ipc.h | kernel/include/airymax/ipc.h | IPC magic 0x41524531 + 128B 消息头 + SQE/CQE |

---

## 第 2 章 管理仓 agentrt-linux 目录结构

管理仓（非 leaf 仓）聚合 8 个子模块，自身不含实现代码，仅含治理与文档索引。

```
agentrt-linux/                    # 管理仓（main 分支）
├── README.md                     # 英文 README（8 子仓矩阵 + 架构层次图）
├── README_zh.md                  # 中文 README
├── LICENSE                       # AGPL-3.0 + Apache-2.0 双许可证
├── NOTICE                        # 版权、商标、第三方声明
├── CONTRIBUTING.md               # 贡献指南
├── .gitmodules                   # 8 子模块定义（feature/official-hubs-01 分支）
├── .gitignore
│
├── kernel/                       # [submodule] airymaxos-kernel
├── services/                     # [submodule] airymaxos-services
├── security/                     # [submodule] airymaxos-security
├── memory/                       # [submodule] airymaxos-memory
├── cognition/                    # [submodule] airymaxos-cognition
├── cloudnative/                  # [submodule] airymaxos-cloudnative
├── system/                       # [submodule] airymaxos-system
├── tests-linux/                  # [submodule] airymaxos-tests-linux
│
└── docs/                         # 软链接/引用 → umbrella docs/AirymaxAgentOS/
                                  # （设计文档维护在 umbrella 仓库，管理仓仅引用）
```

**说明**: 管理仓的 `docs/` 是对 umbrella 仓库 `docs/AirymaxAgentOS/` 的引用（软链接或文档指针），避免设计文档与代码分离维护。agentrt-linux 管理仓本身不创建 feature 分支（`main` only），所有子仓开发在 `feature/official-hubs-01` 分支进行。

---

## 第 3 章 airymaxos-kernel（kernel/）

### 3.1 设计依据

| 依据 | 来源 | 体现 |
|------|------|------|
| ES-OLK-2 架构正交 | OLK-6.6 arch/ | `arch/{x86,arm64,riscv}/` 隔离 |
| ES-OLK-6 UAPI 物理隔离 | OLK-6.6 include/uapi/ | `include/uapi/airymax/` + `include/airymax/` |
| ES-OLK-7 Kbuild+Kconfig | OLK-6.6 三层构建 | `Kbuild` + `Kconfig` + `Makefile` |
| ES-SEL4-1 极简原则 | seL4 src/kernel/ 6 文件 | `corekern/` 仅 4 原子机制 |
| ES-SEL4-7 架构正交分层 | seL4 arch/machine/plat | `arch/` + `machine/` + `plat/` 三层 |
| atoms/corekern 复用 | Airymax 同源 | `corekern/` 模块 |
| [SC] 6 头文件宿主 | IRON-9 v2 | `include/airymax/*.h` |

### 3.2 完整目录结构

```
kernel/                           # airymaxos-kernel（feature/official-hubs-01 分支）
├── README.md                     # 英文 README
├── README_zh.md                  # 中文 README
├── LICENSE                       # AGPL-3.0 + Apache-2.0
├── NOTICE
├── MAINTAINERS                   # 维护者制度（R-03）
├── CONTRIBUTING.md
├── .gitignore
├── .clang-format                 # OS-KER-005 Tab 8
├── .editorconfig
│
├── Kbuild                         # 顶层 Kbuild（递归构建入口）
├── Kconfig                        # 顶层 Kconfig（特性配置入口）
├── Makefile                       # 顶层 Makefile（构建规则）
│
├── arch/                          # 架构相关代码（ES-OLK-2 + ES-SEL4-7）
│   ├── x86/                       # x86/x86_64 架构
│   │   ├── Kbuild
│   │   ├── Kconfig
│   │   ├── include/               # x86 架构相关头文件
│   │   ├── kernel/                # x86 内核入口
│   │   ├── mm/                    # x86 内存管理
│   │   └── entry/                 # x86 系统调用入口
│   ├── arm64/                     # ARM64 架构
│   │   ├── Kbuild
│   │   ├── Kconfig
│   │   ├── include/
│   │   ├── kernel/
│   │   ├── mm/
│   │   └── entry/
│   └── riscv/                     # RISC-V 架构
│       ├── Kbuild
│       ├── Kconfig
│       ├── include/
│       ├── kernel/
│       ├── mm/
│       └── entry/
│
├── include/                       # 公共头文件（ES-OLK-3 / ES-OLK-6）
│   ├── uapi/                      # 用户空间 ABI（永久稳定，OS-IRON-001）
│   │   └── airymax/
│   │       ├── syscall.h          # 系统调用号定义（冻结）
│   │       ├── ipc.h              # IPC UAPI（128B 消息头用户可见部分）
│   │       ├── sched.h            # 调度 UAPI
│   │       ├── memory.h           # 内存 UAPI
│   │       ├── security.h         # 安全 UAPI
│   │       └── cognition.h        # 认知 UAPI
│   ├── airymax/                   # 内核内部头文件
│   │   ├── bpf_struct_ops.h       # [SC] struct_ops 状态机
│   │   ├── memory_types.h         # [SC] MemoryRovol L1-L4
│   │   ├── security_types.h       # [SC] capability 38 ID + LSM 254 ID
│   │   ├── cognition_types.h      # [SC] CoreLoopThree + Thinkdual
│   │   ├── sched.h                # [SC] 任务描述符（AGTS）+ vtime
│   │   ├── ipc.h                  # [SC] IPC magic 0x41524531 + 128B 消息头
│   │   ├── corekern.h             # 微核心原语内部头
│   │   └── airymax_kernel.h       # 总头文件
│   └── asm-generic/               # 通用汇编默认实现（ES-OLK-2）
│
├── corekern/                      # 微核心原语（ES-SEL4-1 极简原则，复用 atoms/corekern）
│   ├── Kbuild
│   ├── Kconfig
│   ├── sched/                     # 调度原语（sched_ext 策略，非 SCHED_AGENT 宏）
│   │   ├── airymax_agent_sched.c   # 默认 Agent 感知 BPF 调度器
│   │   ├── core_sched.c
│   │   └── ext.c                   # sched_ext 框架接入
│   ├── ipc/                       # IPC 原语（io_uring 用户态-内核态 + kfifo kthread 间）
│   │   ├── io_uring_ipc.c         # 用户态-内核态 IPC
│   │   ├── kfifo_ipc.c            # kthread 间 IPC
│   │   └── fastpath.c             # IPC fastpath 优化（ES-SEL4-4 借鉴）
│   ├── taskflow/                  # 任务流原语（graph_engine A 类微核心）
│   │   ├── graph_engine.c
│   │   └── task_descriptor.c      # 任务描述符（magic 0x41475453）
│   ├── memory/                   # 内存原语（page alloc 4 原子机制之一）
│   │   ├── page_alloc.c
│   │   └── vtime.c                # vtime 衰减公式
│   └── time/                      # 时间原语（CLOCK_REALTIME 北京时间对齐）
│       └── clock.c
│
├── patches/                       # 上游补丁（微内核化改造）
│   ├── sched_ext-agent/           # Agent 感知调度补丁
│   │   └── 0001-sched_ext-add-airymax-agent-sched.patch
│   ├── io_uring-ipc/              # IPC 消息传递补丁
│   │   └── 0001-io_uring-add-airymax-ipc-opcodes.patch
│   ├── rust-drivers/              # Rust 安全驱动补丁
│   │   └── 0001-rust-add-airymax-driver-framework.patch
│   └── microkernel/               # 微内核化改造补丁集
│       ├── capability/            # capability 令牌（ES-SEL4-2）
│       │   └── 0001-capability-add-airymax-cap-model.patch
│       ├── vfs-userns/            # VFS 用户态化（ES-SEL4-3）
│       │   └── 0001-vfs-add-userns-migration.patch
│       ├── net-userns/            # 网络栈用户态化
│       │   └── 0001-net-add-userns-migration.patch
│       └── driver-split/          # 驱动拆分（VFIO 用户态驱动）
│           └── 0001-driver-add-vfio-split.patch
│
├── bpf/                           # eBPF 可编程内核（ES-OLK-4 + ES-SEL4-4）
│   ├── Kbuild
│   ├── Kconfig
│   ├── airymax_bpf_kfunc.c        # eBPF kfunc 注册
│   ├── dynamic_pointer.c          # dynamic pointer 支持
│   └── struct_ops/                # struct_ops 状态机（[SC] bpf_struct_ops.h）
│       └── airymax_sched_ops.c
│
├── entry/                         # 系统调用入口
│   ├── Kbuild
│   ├── airymax_syscall_table.c    # 系统调用表（R-01 syscall.xml 生成）
│   ├── airymax_entry_64.c         # x86_64 入口
│   └── airymax_entry_arm64.c      # arm64 入口
│
├── io_uring/                      # 异步 I/O（ES-OLK-1 独立子系统）
│   ├── Kbuild
│   ├── Kconfig
│   ├── airymax_io_uring.c         # io_uring 核心扩展
│   └── airymax_msg_ring.c         # msg_ring IPC 优化
│
├── machine/                       # 机器相关原语（ES-SEL4-7 三层适配之一）
│   ├── x86/
│   ├── arm64/
│   └── riscv/
│
├── plat/                          # 平台相关（ES-SEL4-7 三层适配之一）
│   ├── qemu-x86_64/
│   ├── qemu-arm64/
│   └── hardware-platforms/
│
├── Documentation/                 # 文档即代码（ES-OLK-13）
│   ├── ABI/                       # ABI 文档（OS-IRON-001）
│   │   ├── syscalls/
│   │   ├── ioctl/
│   │   └── procfs/
│   ├── airymax/                   # airymax 专属文档
│   │   ├── microkernel-strategy.md
│   │   ├── sched-ext-design.md
│   │   └── ipc-design.md
│   └── process/                   # 开发流程文档
│
├── scripts/                       # 构建与检查脚本（ES-OLK-9）
│   ├── checkpatch.pl              # 编码规范检查（OS-STD-CODE-001~027）
│   ├── syscall_gen.py             # syscall.xml → C 代码生成（R-01）
│   ├── bitfield_gen.py            # structures.bf → C 代码生成（R-02）
│   ├── kbuild_check.py            # Kbuild/Kconfig 规范检查
│   └── maintainer_check.py        # MAINTAINERS 完整性检查（R-03）
│
├── configs/                       # 内核配置（defconfig）
│   ├── airymax_x86_64_defconfig
│   ├── airymax_arm64_defconfig
│   └── airymax_riscv_defconfig
│
└── tests/                        # 内核单元测试
    ├── kunit/                    # KUnit 单元测试
    └── kselftest/                # kselftest 集成测试
```

### 3.3 关键设计说明

1. **arch/ + machine/ + plat/ 三层架构适配**（ES-SEL4-7）: 借鉴 seL4 三层适配模型而非 OLK-6.6 单一 `arch/`，理由是 agentrt-linux 需要支持虚拟平台（QEMU）与真实硬件平台分离，`plat/` 隔离平台特定代码（如 QEMU virt vs 真实服务器主板）。

2. **corekern/ 仅 4 原子机制**（ES-SEL4-1）: `corekern/{sched,ipc,taskflow,memory,time}` 对应 seL4 的"IPC/地址空间/线程/唯一性"极简原语，复用 atoms/corekern MicroCoreRT 设计。time 单列以对齐"北京时间 CLOCK_REALTIME"工程约定。

3. **[SC] 6 头文件宿主**: `include/airymax/*.h` 是 IRON-9 v2 [SC] 共享契约层的物理宿主，其他子仓（security/memory/cognition）通过 `-I include` 引用，确保单一数据源。

4. **patches/ 补丁集**: 微内核化改造以补丁集形式组织，每个补丁独立可编译（OS-KER-021），符合 `git bisect` 友好（ES-OLK-10）。

5. **scripts/ 含 codegen 工具**: `syscall_gen.py`（R-01）+ `bitfield_gen.py`（R-02）落地于本仓 scripts/，其他子仓引用。

---

## 第 4 章 airymaxos-services（services/）

### 4.1 设计依据

| 依据 | 来源 | 体现 |
|------|------|------|
| ES-SEL4-3 服务用户态化 | seL4 用户态服务 | `userland-{vfs,net,drivers}/` |
| ES-SEL4-4 消息传递 IPC | seL4 endpoint/notification | `ipc/` 基于 io_uring |
| 12 daemons | Airymax 同源 | `daemons/` 12 子目录 |
| ES-SEL4-10 现代构建 | seL4 CMake | Meson（用户态现代构建） |

### 4.2 完整目录结构

```
services/                         # airymaxos-services（feature/official-hubs-01）
├── README.md
├── README_zh.md
├── LICENSE
├── NOTICE
├── MAINTAINERS                   # R-03
├── CONTRIBUTING.md
├── .gitignore
├── .clang-format
├── .editorconfig
│
├── meson.build                   # 顶层 Meson 构建（用户态现代构建，ES-SEL4-10）
├── meson_options.txt             # 构建选项
│
├── daemons/                      # 12 daemons（Airymax 同源 daemons）
│   ├── gateway_d/                # 网关守护进程
│   │   ├── meson.build
│   │   ├── src/
│   │   │   ├── main.c
│   │   │   ├── gateway_handler.c
│   │   │   └── gateway_router.c
│   │   ├── include/
│   │   └── tests/
│   ├── llm_d/                    # LLM 推理守护进程
│   │   ├── meson.build
│   │   ├── src/
│   │   └── include/
│   ├── tool_d/                   # 工具守护进程
│   ├── sched_d/                  # 调度守护进程
│   ├── market_d/                 # 市场守护进程
│   ├── monit_d/                  # 监控守护进程
│   ├── channel_d/                # 通道守护进程
│   ├── info_d/                   # 信息守护进程
│   ├── notify_d/                 # 通知守护进程
│   ├── observe_d/                # 观测守护进程
│   ├── hook_d/                   # 钩子守护进程
│   └── plugin_d/                 # 插件守护进程
│
├── userland-vfs/                 # VFS 用户态化（ES-SEL4-3 Phase 1）
│   ├── meson.build
│   ├── src/
│   │   ├── vfs_core.c            # VFS 核心用户态实现
│   │   ├── vfs_proxy.c           # 内核 VFS 代理
│   │   └── vfs_cache.c          # 用户态缓存
│   └── include/
│
├── userland-net/                 # 网络栈用户态化（ES-SEL4-3 Phase 2）
│   ├── meson.build
│   ├── src/
│   │   ├── net_stack.c           # 用户态网络栈
│   │   ├── net_proxy.c           # 内核网络代理
│   │   └── net_filter.c         # 用户态 netfilter
│   └── include/
│
├── userland-drivers/             # 驱动用户态化（ES-SEL4-3 Phase 2）
│   ├── meson.build
│   ├── src/
│   │   ├── vfio_driver.c         # VFIO 用户态驱动框架
│   │   └── driver_proxy.c        # 内核驱动代理
│   └── include/
│
├── ipc/                          # io_uring 消息传递（ES-SEL4-4）
│   ├── meson.build
│   ├── src/
│   │   ├── io_uring_client.c     # io_uring 客户端
│   │   ├── io_uring_server.c    # io_uring 服务端
│   │   └── msg_ring.c           # msg_ring IPC（128B 消息头）
│   └── include/
│       └── airymax_ipc.h         # 引用 [SC] ipc.h
│
├── systemd/                      # systemd 集成
│   ├── units/                    # systemd unit 文件
│   │   ├── airymax-gateway.service
│   │   ├── airymax-llm.service
│   │   └── ... (12 daemons)
│   └── configs/
│
├── include/                      # 公共头文件
│   └── airymax/
│       ├── daemons.h             # 12 daemons 公共接口
│       └── services_common.h
│
└── tests/
    ├── unit/
    └── integration/
```

### 4.3 关键设计说明

1. **Meson 而非 CMake**: 用户态服务采用 Meson（GNOME/FreeDesktop 主流），比 CMake 更现代、更简洁，符合 ES-SEL4-10。

2. **12 daemons 各自独立子目录**: 每个 daemon 是独立可执行文件，有自己的 src/include/tests，便于独立演进、独立部署。

3. **userland-* 三阶段**: VFS（Phase 1）→ 网络 + 驱动（Phase 2），对应 ES-SEL4-3 服务用户态化渐进策略。

---

## 第 5 章 airymaxos-security（security/）

### 5.1 设计依据

| 依据 | 来源 | 体现 |
|------|------|------|
| ES-SEL4-2 capability 单一模型 | seL4 capability | `capability/` 独立模块 |
| ES-OLK-1 关注点分离 | OLK-6.6 security/ | 每策略一目录 |
| ES-OLK-3 UAPI 隔离 | OLK-6.6 include/uapi/ | `include/uapi/airymax/security/` |
| Cupolas 四层 | Airymax 同源 | `cupolas/{rules,policy,sanitize,audit}/` |
| [SC] security_types.h | IRON-9 v2 | `include/airymax/security_types.h` |

### 5.2 完整目录结构

```
security/                         # airymaxos-security（feature/official-hubs-01）
├── README.md
├── README_zh.md
├── LICENSE
├── NOTICE
├── MAINTAINERS                   # R-03
├── CONTRIBUTING.md
├── .gitignore
├── .clang-format
├── .editorconfig
│
├── Kbuild                        # 内核态构建
├── Kconfig
├── Makefile
│
├── include/
│   ├── uapi/airymax/security/    # 安全 UAPI（永久稳定）
│   │   ├── capability.h          # capability 38 ID 枚举
│   │   ├── lsm_hooks.h           # LSM 254 ID 枚举
│   │   └── cupolas.h            # Cupolas UAPI
│   └── airymax/security/         # 内核内部头文件
│       ├── security_types.h      # [SC] capability + LSM + Cupolas blob
│       ├── capability_internal.h
│       ├── lsm_internal.h
│       └── cupolas_internal.h
│
├── capability/                   # seL4 风格 capability（ES-SEL4-2）
│   ├── Kbuild
│   ├── capability.c              # capability 核心（mint/mintcopy/derive/revoke）
│   ├── cnode.c                   # capability 节点管理（借鉴 seL4 src/object/cnode.c 思想）
│   ├── capability_derive.c       # 派生模型
│   └── tests/
│
├── lsm/                          # LSM 钩子机制（ES-OLK-1 + 策略可插拔）
│   ├── Kbuild
│   ├── agent_lsm/                # Cupolas LSM（Airymax 同源）
│   │   ├── agent_lsm.c
│   │   ├── agent_lsm_hooks.c
│   │   └── include/
│   └── common/
│       └── lsm_framework.c       # LSM 框架接入
│
├── cupolas/                      # 安全穹顶四层（Airymax 同源 cupolas）
│   ├── Kbuild
│   ├── rules/                    # L1 规则层（BPF 热加载）
│   │   ├── rule_engine.c
│   │   └── bpf_rules/
│   ├── policy/                   # L2 权限层（LSM 钩子链）
│   │   ├── policy_engine.c
│   │   └── multi_tenant.c        # 多租户 Agent 权限隔离
│   ├── sanitize/                 # L3 净化层（可加载模块）
│   │   ├── input_sanitize.c      # 输入净化
│   │   ├── output_desens.c      # 输出脱敏
│   │   └── prompt_injection.c    # Prompt 注入防护
│   └── audit/                    # L4 审计层（不可插拔，强制）
│       ├── audit_log.c           # 全量操作日志
│       └── audit_replay.c        # 行为回放
│
├── sandbox/                      # 进程沙箱
│   ├── Kbuild
│   ├── landlock/                 # Landlock（文件访问控制）
│   │   ├── airymax_landlock.c
│   │   └── landlock_rules.c
│   └── seccomp/                  # seccomp（系统调用过滤）
│       ├── airymax_seccomp.c
│       └── seccomp_filter.c
│
├── confidential-compute/         # TEE 机密计算
│   ├── Kbuild
│   ├── sgx/                      # Intel SGX
│   ├── sev-snp/                  # AMD SEV-SNP
│   └── tdx/                      # Intel TDX
│
├── crypto/                       # 加密算法
│   ├── Kbuild
│   └── sm2-sm4/                  # 国密算法（SM2/SM3/SM4/SM9）
│       ├── sm2.c
│       ├── sm3.c
│       ├── sm4.c
│       └── sm9.c
│
├── zero-trust/                   # 零信任网络（BeyondCorp）
│   ├── Kbuild
│   ├── zero_trust_engine.c
│   └── trust_evaluator.c
│
├── ebpf-verify/                  # eBPF 安全验证
│   ├── Kbuild
│   ├── bpf_verifier_ext.c       # eBPF 验证器扩展
│   └── kfunc_verify.c           # kfunc 安全验证
│
└── tests/
    ├── unit/
    ├── integration/
    └── capability_test/          # capability 派生测试
```

### 5.3 关键设计说明

1. **capability/ 借鉴 seL4 cnode.c 思想**: `capability/cnode.c` 借鉴 seL4 `src/object/cnode.c` 的 capability 节点管理思想（ES-SEL4-2），但不复制 seL4 代码，实现独立。

2. **cupolas/ 四层 L1-L4 对齐**: `cupolas/{rules,policy,sanitize,audit}/` 严格对齐 `04-engineering-philosophy.md` §3.5 的四层模型，L4 audit 不可插拔（强制）。

3. **confidential-compute/ 三 TEE 并列**: SGX/SEV-SNP/TDX 三大 TEE 各自独立子目录，通过统一抽象接口暴露。

---

## 第 6 章 airymaxos-memory（memory/）

### 6.1 设计依据

| 依据 | 来源 | 体现 |
|------|------|------|
| ES-OLK-1 关注点分离 | OLK-6.6 mm/ | 单一子系统垂直内聚 |
| ES-OLK-3 UAPI 隔离 | OLK-6.6 include/uapi/ | `include/uapi/airymax/memory/` |
| MemoryRovol 内核态 | Airymax 同源 | `memoryrovol/` |
| [SC] memory_types.h | IRON-9 v2 | `include/airymax/memory_types.h` |

### 6.2 完整目录结构

```
memory/                           # airymaxos-memory（feature/official-hubs-01）
├── README.md
├── README_zh.md
├── LICENSE
├── NOTICE
├── MAINTAINERS                   # R-03
├── CONTRIBUTING.md
├── .gitignore
├── .clang-format
├── .editorconfig
│
├── Kbuild
├── Kconfig
├── Makefile
│
├── include/
│   ├── uapi/airymax/memory/      # 内存 UAPI
│   │   ├── memoryrovol.h         # MemoryRovol UAPI
│   │   ├── cxl.h                 # CXL UAPI
│   │   └── pmem.h                # PMEM UAPI
│   └── airymax/memory/           # 内核内部头文件
│       ├── memory_types.h        # [SC] MemoryRovol L1-L4 + GFP 掩码 + PMEM
│       ├── memoryrovol_internal.h
│       ├── cxl_internal.h
│       └── pmem_internal.h
│
├── memoryrovol/                  # 记忆卷内核态（Airymax 同源 memoryrovol）
│   ├── Kbuild
│   ├── rovol-kmod/               # 记忆卷内核模块
│   │   ├── rovol_core.c          # MemoryRovol 核心
│   │   ├── rovol_l1.c            # L1 数据结构
│   │   ├── rovol_l2.c            # L2
│   │   ├── rovol_l3.c            # L3
│   │   └── rovol_l4.c            # L4
│   ├── snapshot/                 # 记忆快照（fork + COW）
│   │   ├── snapshot.c
│   │   └── cow_snapshot.c
│   ├── restore/                  # 记忆恢复（mmap + userfaultfd）
│   │   ├── restore.c
│   │   └── userfaultfd_handler.c
│   └── migrate/                  # 记忆迁移（跨节点）
│       ├── migrate.c
│       └── cross_node.c
│
├── cxl/                          # CXL 内存分层（CXL 3.0 池化）
│   ├── Kbuild
│   ├── cxl_core.c                # CXL 核心
│   ├── cxl_pool.c                # CXL 池化
│   ├── cxl_tiering.c             # 内存分层
│   └── cxl_hotplug.c             # CXL 热插拔
│
├── pmem/                         # 持久化内存（PMEM 非易失）
│   ├── Kbuild
│   ├── pmem_core.c
│   ├── pmem_persist.c            # 持久化接口
│   └── pmem_map.c                # PMEM 映射
│
├── mglru/                        # MGLRU 多代 LRU（Linux 6.6 内存回收）
│   ├── Kbuild
│   ├── mglru_core.c              # MGLRU 核心
│   ├── mglru_gen.c               # 多代管理
│   └── mglru_reclaim.c           # 内存回收
│
├── vfs-persist/                  # VFS 持久化层（多后端）
│   ├── Kbuild
│   ├── vfs_persist.c
│   └── backends/
│       ├── ext4_backend.c
│       ├── xfs_backend.c
│       └── pmem_backend.c
│
└── tests/
    ├── unit/
    ├── integration/
    └── memoryrovol_test/         # MemoryRovol L1-L4 测试
```

### 6.3 关键设计说明

1. **memoryrovol/rovol-kmod/ L1-L4 对齐 [SC]**: `rovol_{l1,l2,l3,l4}.c` 严格对齐 `memory_types.h` 中的 MemoryRovol L1-L4 数据结构。

2. **不含 etmem/dynamic_pool/numa_remote**: 遵循 project_memory 决策——etmem 用 `memory.reclaim + tiering` 替代（`mglru/` + `cxl/cxl_tiering.c`），dynamic_pool 用 memcg 替代，numa_remote 用 CXL 替代。

---

## 第 7 章 airymaxos-cognition（cognition/）

### 7.1 设计依据

| 依据 | 来源 | 体现 |
|------|------|------|
| CoreLoopThree kthread | Airymax 同源 | `coreloopthree/clt-kmod/` |
| ES-SEL4-1 极简 | seL4 kthread | kthread 最小化 |
| ES-SEL4-10 现代构建 | seL4 CMake | Cargo（Rust）+ Kbuild（C kthread） |
| [SC] cognition_types.h | IRON-9 v2 | `include/airymax/cognition_types.h` |

### 7.2 完整目录结构

```
cognition/                        # airymaxos-cognition（feature/official-hubs-01）
├── README.md
├── README_zh.md
├── LICENSE
├── NOTICE
├── MAINTAINERS                   # R-03
├── CONTRIBUTING.md
├── .gitignore
├── .clang-format                 # C 部分（kthread）
├── .editorconfig
├── rustfmt.toml                  # Rust 部分（OS-STD-202 4 空格）
│
├── Kbuild                        # 内核态 C 构建（kthread 部分）
├── Kconfig
├── Makefile
├── Cargo.toml                    # Rust 构建（Wasm runtime 等）
│
├── include/
│   ├── uapi/airymax/cognition/   # 认知 UAPI
│   │   ├── coreloopthree.h       # CoreLoopThree UAPI
│   │   ├── thinkdual.h           # Thinkdual UAPI
│   │   └── llm_scheduler.h       # LLM 调度 UAPI
│   └── airymax/cognition/        # 内核内部头文件
│       ├── cognition_types.h     # [SC] CoreLoopThree 三阶段 + Thinkdual + LLM
│       ├── clt_internal.h
│       └── llm_internal.h
│
├── coreloopthree/                # 三层认知循环（Airymax 同源 coreloopthree）
│   ├── Kbuild
│   └── clt-kmod/                 # kthread 内核模块
│       ├── clt_kthread.c         # CoreLoopThree kthread
│       ├── clt_perception.c      # PERCEPTION 阶段
│       ├── clt_thinking.c        # THINKING 阶段
│       ├── clt_action.c          # ACTION 阶段
│       └── clt_context.c        # CoreLoopThree 上下文
│
├── thinkdual/                    # 双思考（快/慢思考切换）
│   ├── Kbuild
│   └── system1-system2/
│       ├── thinkdual_core.c      # 双思考核心
│       ├── system1_fast.c        # SYSTEM1_FAST（快思考）
│       └── system2_slow.c        # SYSTEM2_SLOW（慢思考）
│
├── wasm-runtime/                 # Wasm 3.0 安全沙箱（Rust）
│   ├── Cargo.toml
│   ├── src/
│   │   ├── lib.rs
│   │   ├── wasm_runtime.rs       # Wasm 3.0 运行时
│   │   ├── sandbox.rs            # 安全沙箱
│   │   └── memory_isolation.rs   # 内存隔离
│   └── tests/
│
├── llm-scheduler/                # LLM 推理调度
│   ├── Kbuild
│   ├── src/
│   │   ├── llm_sched_core.c      # LLM 调度核心
│   │   ├── prefill_sched.c       # PREFILL 阶段调度
│   │   ├── decode_sched.c        # DECODE 阶段调度
│   │   └── speculative_sched.c  # SPECULATIVE 调度
│   └── include/
│
├── gpu-npu/                      # 算力调度（GPU/NPU 池化）
│   ├── Kbuild
│   ├── gpu_scheduler.c
│   ├── npu_scheduler.c
│   └── compute_pool.c           # 算力池化
│
├── token-efficiency/             # Token 能效（KVC-Gateway + LMCache）
│   ├── Kbuild
│   ├── token_metrics.c          # Token 能效指标
│   ├── kvc_gateway.c            # KVC-Gateway
│   └── lmcache.c                # LMCache
│
├── super-node-sandbox/           # 超节点沙箱（镜像快照）
│   ├── Kbuild
│   ├── super_node.c
│   └── snapshot_restore.c        # 镜像快照恢复
│
├── embodied-ai/                  # 具身智能（传感器/运动控制）
│   ├── Kbuild
│   ├── sensor_input.c           # 传感器输入
│   └── motion_control.c         # 运动控制
│
└── tests/
    ├── unit/
    ├── integration/
    └── cognition_benchmark/      # 认知基准测试
```

### 7.3 关键设计说明

1. **C + Rust 混合构建**: 内核态 kthread（C，Kbuild）+ Wasm runtime（Rust，Cargo）混合，`clt-kmod/` 是 C kthread，`wasm-runtime/` 是 Rust。

2. **CoreLoopThree 三阶段对齐 [SC]**: `clt_{perception,thinking,action}.c` 严格对齐 `cognition_types.h` 中的 PERCEPTION/THINKING/ACTION 三阶段枚举。

3. **Thinkdual 两模式对齐 [SC]**: `system1_fast.c` + `system2_slow.c` 对齐 SYSTEM1_FAST/SYSTEM2_SLOW 枚举。

---

## 第 8 章 airymaxos-cloudnative（cloudnative/）

### 8.1 设计依据

| 依据 | 来源 | 体现 |
|------|------|------|
| K8s 生态 | 云原生主流 | `kubernetes/crds/` + `containerd-shim/` |
| ES-SEL4-9 用户态 API 库独立 | seL4 libsel4 | `sdk/`（4 语言） |
| ES-SEL4-10 现代构建 | seL4 CMake | Go Modules + Cargo + tsc |

### 8.2 完整目录结构

```
cloudnative/                     # airymaxos-cloudnative（feature/official-hubs-01）
├── README.md
├── README_zh.md
├── LICENSE
├── NOTICE
├── MAINTAINERS                   # R-03
├── CONTRIBUTING.md
├── .gitignore
├── .editorconfig
├── .golangci.yml                 # Go 代码检查
│
├── Makefile                      # 顶层构建（多语言聚合）
├── go.mod                        # Go 模块（K8s CRD + agentctl）
│
├── kubernetes/                   # Kubernetes 集成
│   ├── crds/                     # Agent CRD（声明式）
│   │   ├── agent.yaml
│   │   ├── agentruntime.yaml
│   │   └── cognitivelayer.yaml
│   ├── controllers/              # CRD 控制器（Go）
│   │   ├── agent_controller.go
│   │   └── agentruntime_controller.go
│   └── webhook/                  # 准入 webhook
│       └── validating_webhook.go
│
├── containerd-shim/               # containerd shim（Agent 容器化）
│   ├── go.mod
│   ├── cmd/
│   │   └── airymax-shim/
│   │       └── main.go
│   ├── pkg/
│   │   ├── shim.go               # shim 核心
│   │   ├── agent_runtime.go      # Agent 运行时
│   │   └── oci.go                # OCI 集成
│   └── configs/
│
├── oci/                          # OCI 镜像规范
│   ├── specs/                    # OCI 规范扩展
│   │   ├── agent_image_spec.md
│   │   └── agent_runtime_spec.md
│   └── tools/
│       └── oci_builder.go        # OCI 镜像构建工具
│
├── cni/                          # CNI 网络插件
│   ├── go.mod
│   ├── pkg/
│   │   ├── airymax_cni.go        # CNI 插件
│   │   └── service_mesh.go      # 服务网格
│   └── configs/
│
├── agentctl/                     # 管理工具（对标 kubectl）
│   ├── go.mod
│   ├── cmd/
│   │   ├── root.go
│   │   ├── create.go
│   │   ├── delete.go
│   │   ├── get.go
│   │   └── logs.go
│   └── pkg/
│       ├── client.go             # API 客户端
│       └── output.go             # 输出格式化
│
├── observability/                # 可观测性（OpenTelemetry 标准化）
│   ├── go.mod
│   ├── pkg/
│   │   ├── metrics.go            # 指标采集
│   │   ├── tracing.go            # 分布式追踪
│   │   └── logging.go            # 日志聚合
│   └── exporters/
│
├── dpu-ipu/                      # 硬件卸载（DPU/IPU）
│   ├── go.mod
│   └── pkg/
│       ├── dpu_offload.go        # DPU 卸载
│       └── ipu_offload.go        # IPU 卸载
│
├── super-node-os/                # 超节点 OS（超节点拓扑）
│   ├── go.mod
│   └── pkg/
│       ├── super_node_manager.go
│       └── topology.go           # 超节点拓扑
│
├── sdk/                          # SDK（libsel4 模型借鉴，4 语言，ES-SEL4-9）
│   ├── python/
│   │   ├── setup.py
│   │   ├── airymax_sdk/
│   │   └── tests/
│   ├── rust/
│   │   ├── Cargo.toml
│   │   ├── src/
│   │   └── tests/
│   ├── go/
│   │   ├── go.mod
│   │   └── airymax_sdk.go
│   └── typescript/
│       ├── package.json
│       ├── src/
│       └── tests/
│
└── tests/
    ├── e2e/                      # 端到端测试
    └── helm/                     # Helm chart 测试
```

### 8.3 关键设计说明

1. **sdk/ 借鉴 libsel4 模型**: 4 语言 SDK 独立于运行时，用户程序通过 SDK 与 agentrt-linux 通信，不直接调用内核/daemon 内部函数（ES-SEL4-9）。

2. **Go 为主语言**: K8s 生态主流语言，CRD 控制器/containerd shim/agentctl 均为 Go。

3. **containerd-shim/ 对标 OCI**: Agent 容器化遵循 OCI 规范，通过 containerd shim 接入。

---

## 第 9 章 airymaxos-system（system/）

### 9.1 设计依据

| 依据 | 来源 | 体现 |
|------|------|------|
| OLK-6.6 包管理 | RPM + dnf | `package-manager/` |
| Euler 标准兼容 | 发行版工具集 | RPM/dnf/sysctl |
| Airymax 同源 commons | 公共工具 | `base-libs/` + `devstation/` |

### 9.2 完整目录结构

```
system/                           # airymaxos-system（feature/official-hubs-01）
├── README.md
├── README_zh.md
├── LICENSE
├── NOTICE
├── MAINTAINERS                   # R-03
├── CONTRIBUTING.md
├── .gitignore
├── .editorconfig
│
├── Makefile                      # 顶层构建
│
├── package-manager/              # 包管理（RPM + dnf）
│   ├── rpms/                     # RPM spec 文件
│   │   ├── airymax-kernel.spec
│   │   ├── airymax-services.spec
│   │   ├── airymax-security.spec
│   │   ├── airymax-memory.spec
│   │   ├── airymax-cognition.spec
│   │   └── airymax-cloudnative.spec
│   ├── dnf/                      # dnf 仓库配置
│   │   ├── airymax.repo
│   │   └── dnf_plugins/
│   └── build_scripts/
│       └── build_rpm.sh
│
├── config/                       # 系统配置
│   ├── sysctl/                   # sysctl 配置
│   │   ├── airymax.conf
│   │   └── agent_runtime.conf
│   ├── systemd/                  # systemd 配置
│   │   ├── system.conf
│   │   └── journal.conf
│   ├── modprobe/                 # 模块加载配置
│   └── pam/                      # PAM 配置
│
├── shell/                        # shell 环境
│   ├── bash/
│   │   ├── airymax_bashrc
│   │   └── airymax_profile
│   └── fish/
│       └── airymax_config.fish
│
├── base-libs/                    # 基础库
│   ├── meson.build
│   ├── glibc/                    # glibc 配置与补丁
│   └── musl/                     # musl 配置（可选）
│
├── monitoring/                   # 监控工具
│   ├── meson.build
│   ├── top/                      # airymax-top（增强版 top）
│   ├── perf/                     # perf 集成
│   └── htop/                     # htop 配置
│
├── devstation/                   # DevStation AI 助手（Airymax 同源）
│   ├── meson.build
│   ├── src/
│   │   ├── devstation.c
│   │   ├── ai_assistant.c        # AI 助手核心
│   │   └── dev_tools.c           # 开发工具集成
│   ├── python/
│   │   ├── devstation_cli.py     # CLI 工具
│   │   └── ai_plugins/
│   └── configs/
│
└── tests/
    ├── unit/
    └── integration/
```

### 9.3 关键设计说明

1. **package-manager/rpms/ 7 子仓 spec**: 每个 leaf 仓对应一个 RPM spec，便于发行版打包。

2. **devstation/ AI 助手**: DevStation 是 Airymax 同源模块，Python CLI + C 核心 + 插件机制。

---

## 第 10 章 airymaxos-tests-linux（tests-linux/）

### 10.1 设计依据

| 依据 | 来源 | 体现 |
|------|------|------|
| ES-OLK-9 规范可执行 | OLK-6.6 tools/testing | 多语言测试聚合 |
| ES-SEL4-5 形式化验证 | seL4 proof/spec/capDL | `formal-verification/{spec,proof}/` |
| ES-OLK-10 regression 零容忍 | OLK-6.6 kselftest | 回归测试覆盖 |

### 10.2 完整目录结构

```
tests-linux/                      # airymaxos-tests-linux（feature/official-hubs-01）
├── README.md
├── README_zh.md
├── LICENSE
├── NOTICE
├── MAINTAINERS                   # R-03
├── CONTRIBUTING.md
├── .gitignore
├── .editorconfig
│
├── CMakeLists.txt                # CMake 构建（ES-SEL4-10）
├── Makefile                      # 顶层聚合
│
├── unit/                         # 单元测试（全模块）
│   ├── kernel_unit/              # kernel 子仓单元
│   ├── services_unit/            # services 子仓单元
│   ├── security_unit/            # security 子仓单元
│   ├── memory_unit/              # memory 子仓单元
│   ├── cognition_unit/           # cognition 子仓单元
│   └── cloudnative_unit/         # cloudnative 子仓单元
│
├── integration/                  # 集成测试（模块间）
│   ├── kernel_services/          # kernel ↔ services
│   ├── kernel_security/          # kernel ↔ security
│   ├── kernel_memory/            # kernel ↔ memory
│   ├── kernel_cognition/         # kernel ↔ cognition
│   ├── services_cognition/       # services ↔ cognition
│   ├── security_cognition/       # security ↔ cognition
│   ├── memory_cognition/         # memory ↔ cognition
│   └── e2e/                      # 端到端集成
│
├── formal-verification/         # 形式化验证（seL4 风格，ES-SEL4-5）
│   ├── spec/                     # 抽象规约（Isabelle/HOL）
│   │   ├── kernel_spec/          # 内核规约
│   │   ├── security_spec/        # 安全规约
│   │   └── ipc_spec/             # IPC 规约
│   ├── proof/                    # 形式化证明
│   │   ├── capability_proof/    # capability 派生证明
│   │   ├── ipc_proof/            # IPC 协议证明
│   │   └── sched_proof/          # 调度正确性证明
│   └── capdl/                    # capability 分布描述（参考 seL4 capDL）
│       └── initial_state.cdl
│
├── soak/                         # Soak 测试（72h 持续运行）
│   ├── scripts/
│   │   ├── run_soak_72h.sh
│   │   └── monitor_resources.sh
│   ├── workloads/
│   └── results/
│
├── chaos/                        # 混沌测试（Chaos Mesh 类）
│   ├── experiments/
│   │   ├── network_partition.yaml
│   │   ├── pod_kill.yaml
│   │   └── memory_pressure.yaml
│   └── scripts/
│       └── run_chaos.sh
│
├── benchmark/                    # 性能基准测试
│   ├── micro/                    # 微基准
│   │   ├── ipc_latency/
│   │   ├── sched_overhead/
│   │   └── memory_throughput/
│   ├── macro/                    # 宏基准
│   │   ├── agent_workload/
│   │   └── llm_inference/
│   └── regression/               # 回归基准（ES-OLK-10）
│       └── baseline.json
│
├── observability-verify/         # eBPF 可观测性验证
│   ├── bpf_trace_tests/
│   ├── perf_tests/
│   └── metrics_verify/
│
├── tools/                        # 测试工具
│   ├── test_runner/              # 测试运行器
│   ├── coverage/                 # 覆盖率工具
│   └── report_gen/               # 报告生成
│
└── configs/                      # 测试配置
    ├── kselftest.config
    ├── kunit.config
    └── ci.config
```

### 10.3 关键设计说明

1. **formal-verification/ seL4 风格**: `spec/`（抽象规约）+ `proof/`（Isabelle/HOL 证明）+ `capdl/`（capability 分布）三段式严格借鉴 seL4（ES-SEL4-5），但不复制 seL4 证明，针对 agentrt-linux 的 capability/IPC/调度建立独立规约与证明。

2. **integration/ 7 子仓两两集成**: 按 `20-modules/README.md` §2 的依赖图组织，每条依赖关系对应一个集成测试目录。

3. **benchmark/regression/ 回归基准**: `baseline.json` 记录性能基线，每次提交对比，符合 ES-OLK-10 regression 零容忍。

---

## 第 11 章 跨子仓一致性约束

### 11.1 [SC] 共享契约层引用一致性

6 个 [SC] 头文件物理宿主在 `kernel/include/airymax/`，其他子仓引用方式：

| 引用方 | 引用方式 | 约束 |
|--------|---------|------|
| security/ | `-I../kernel/include` | [SC] security_types.h 直接引用 |
| memory/ | `-I../kernel/include` | [SC] memory_types.h 直接引用 |
| cognition/ | `-I../kernel/include` | [SC] cognition_types.h 直接引用 |
| services/ | `-I../kernel/include` | [SC] ipc.h + sched.h 引用 |
| tests-linux/ | `-I../kernel/include` | 全部 [SC] 头文件引用（测试） |

**约束**: 任何子仓不得重新定义 [SC] 头文件内容，必须通过 include 引用 kernel 子仓的物理宿主，确保 IRON-9 v2 单一数据源。

### 11.2 公共骨架一致性

8 子仓根目录公共文件（README/LICENSE/NOTICE/MAINTAINERS/CONTRIBUTING.md/.gitignore/.editorconfig）必须保持一致：
- **LICENSE**: 全部 AGPL-3.0+Apache-2.0 双许可证
- **MAINTAINERS**: 全部 R-03 落地，格式统一
- **CONTRIBUTING.md**: 全部引用 DCO + Signed-off-by + 审查流程
- **.editorconfig**: 全部对齐 OS-KER-005（C Tab 8）/ OS-STD-202（Rust 4 空格）/ OS-STD-203（Python 4 空格）

### 11.3 分支策略一致性

8 子仓全部在 `feature/official-hubs-01` 分支开发，管理仓在 `main` 分支聚合。子仓不得创建未授权的 feature 分支，符合 `04-engineering-philosophy.md` §6 审查优先文化。

### 11.4 版本号一致性

8 子仓当前版本统一为 `0.1.1`（文档体系完成），1.0.1 开发阶段统一升级。子仓不得擅自升级版本号，符合 `20-modules/README.md` §6.1 版本号规则。

### 11.5 目录结构落地路线

| 阶段 | 时机 | 落地内容 |
|------|------|---------|
| 阶段 1 | 1.0.1 M1（架构与模块设计完善） | 8 子仓内部目录结构骨架创建（空目录 + .gitkeep） |
| 阶段 2 | 1.0.1 M1 | R-01（syscall.xml）+ R-02（structures.bf）落地于 kernel/scripts/ |
| 阶段 3 | 1.0.1 M5（开发流程与治理） | R-03（8 子仓 MAINTAINERS 文件）落地 |
| 阶段 4 | 1.0.1 M1-M5 | 各子仓按依赖层次（L2→L3→L4→L5→L6→L7）逐步填充实现 |

---

## 附录 A：双源映射对照表

| 子仓 | OLK-6.6 借鉴 | seL4 借鉴 | Airymax 同源 |
|------|-------------|----------|-------------|
| kernel | arch/ + include/{uapi,linux} + Kbuild/Kconfig + Documentation + scripts + MAINTAINERS | src/{kernel,object,fastpath} 极简 + arch/machine/plat 三层 + fastpath 优化 | atoms/corekern |
| services | security/ 可插拔模式 | libsel4 服务化 + endpoint/notification IPC | daemons (12) |
| security | security/{selinux,landlock} 每策略一目录 + LSM 钩子 | capability 单一模型 + cnode.c 思想 | cupolas |
| memory | mm/ 单一子系统 + MGLRU + damon | 无（形式化约束不适用） | heapstore + memoryrovol |
| cognition | kernel/sched kthread 模式 | 极简 kthread（ES-SEL4-1） | coreloopthree + frameworks |
| cloudnative | tools/ 用户态工具 | libsel4 SDK 独立模型（ES-SEL4-9） | gateway + sdk |
| system | scripts/ + 配置管理 | 无 | commons |
| tests-linux | tools/testing + kselftest | proof/spec/capDL 形式化三段式 | 全模块测试 |

---

## 附录 B：规则编号映射

本设计涉及的 agentrt-linux 工程标准规则编号：

| 规则编号 | 含义 | 落地位置 |
|---------|------|---------|
| OS-IRON-001 | 用户空间 ABI 永久稳定 | include/uapi/airymax/ |
| OS-IRON-002 | 内核内部 API 不稳定 | include/airymax/（非 uapi） |
| OS-KER-005 | C Tab 8 缩进 | .clang-format |
| OS-KER-003 | goto 集中出口 | 各 .c 实现 |
| OS-STD-009 | EXPORT_SYMBOL 紧跟 | kernel/corekern/ |
| OS-STD-020 | typedef 5 例外 | 全部 .c/.h |
| OS-STD-024 | .c 避免 #if 用 stub | 全部 .c |
| OS-STD-025 | IS_ENABLED | 全部 .c |
| OS-STD-202 | Rust 4 空格 | cognition/cloudnative rustfmt.toml |
| OS-STD-203 | Python 4 空格 | cloudnative/sdk/python + system/devstation/python |
| OS-STD-204 | TypeScript 2 空格 | cloudnative/sdk/typescript |
| IRON-9 v2 [SC] | 6 头文件共享契约 | kernel/include/airymax/*.h |

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
