Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agentrt-linux 8 子仓完整项目目录结构设计（v0.2.3 修正版）

> **文档定位**: 基于 OLK-6.6 与 seL4 **实际源代码目录结构的穷尽式直接测绘**，对 [v0.2.1 目录结构设计](../_design_0.2.1/01-agentrt-linux-directory-structure.md) 进行全面修正，吸收 [v0.2.2 优化报告](../_design_0.2.2/01-directory-structure-optimization.md) 的 18 项发现（16 项有效）、纠正 v0.2.2 报告自身的 9 处缺陷、修复 Phase 4 独立审查发现的 11 项新问题。本设计是 agentrt-linux 1.0.1 开发阶段目录骨架的**权威基线**，亦是未来十年项目演进的目录结构根基。
> **版本**: 0.2.3（修正版目录结构设计）
> **最后更新**: 2026-07-09
> **质量要求**: 绝对严谨、严格、严肃——每一处目录设计决策均附直接源代码证据引用，经得起第三方独立推敲
> **设计原则**: (1) Linux 6.6 内核基线对齐（ES-OLK-1~13）；(2) seL4 架构层借鉴（ES-SEL4-1~10）；(3) IRON-9 v2 [SC] 共享契约层 6 个头文件**单一物理宿主**于 `kernel/include/airymax/`；(4) Airymax 同源（atoms/corekern 复用）；(5) 双许可证 AGPL-3.0+Apache-2.0；(6) 8 子仓依赖层次（L2-L7，本版首次明确定义）
> **当前状态**: 0.1.1 各子仓仅含 README/LICENSE/NOTICE/.gitignore 占位文件，本设计为 1.0.1 开发提供目标骨架

---

## 目录

- [第 0 章 修正依据与直接证据索引](#第-0-章-修正依据与直接证据索引)
- [第 1 章 设计总则（修正版）](#第-1-章-设计总则修正版)
- [第 2 章 管理仓 agentrt-linux 目录结构](#第-2-章-管理仓-agentrt-linux-目录结构)
- [第 3 章 airymaxos-kernel（kernel/）](#第-3-章-airymaxos-kernelkernel)
- [第 4 章 airymaxos-services（services/）](#第-4-章-airymaxos-servicesservices)
- [第 5 章 airymaxos-security（security/）](#第-5-章-airymaxos-securitysecurity)
- [第 6 章 airymaxos-memory（memory/）](#第-6-章-airymaxos-memorymemory)
- [第 7 章 airymaxos-cognition（cognition/）](#第-7-章-airymaxos-cognitioncognition)
- [第 8 章 airymaxos-cloudnative（cloudnative/）](#第-8-章-airymaxos-cloudnativecloudnative)
- [第 9 章 airymaxos-system（system/）](#第-9-章-airymaxos-systemsystem)
- [第 10 章 airymaxos-tests-linux（tests-linux/）](#第-10-章-airymaxos-tests-linuxtests-linux)
- [第 11 章 跨子仓一致性约束（修正版）](#第-11-章-跨子仓一致性约束修正版)
- [附录 A：双源映射对照表（修正版）](#附录-a双源映射对照表修正版)
- [附录 B：规则编号映射](#附录-b规则编号映射)
- [附录 C：v0.2.1 → v0.2.3 变更记录](#附录-cv021--v023-变更记录)

---

## 第 0 章 修正依据与直接证据索引

### 0.1 修正来源

本版（v0.2.3）综合三类修正输入：

| 修正输入 | 来源 | 修正项数 | 处理结果 |
|---------|------|---------|---------|
| v0.2.2 优化报告 18 项发现 | `_design_0.2.2/01-directory-structure-optimization.md` | 18 项 | 16 项有效采纳，2 项修正后采纳；同时纠正 v0.2.2 报告自身 9 处缺陷 |
| Phase 4 独立审查新发现 | 本轮对 v0.2.1 设计文档全文逐行审查 | 11 项 | 全部采纳（1 P0 + 6 P1 + 4 P2） |
| 直接源代码重新测绘 | seL4-master + OLK-6.6 穷尽式 `ls`/`find` 验证 | — | 作为全部修正的直接证据基础 |

### 0.2 直接证据索引（v0.2.3 全部修正的可复现证据）

下列证据均经本轮直接 `ls`/`find`/`Grep` 命令复核，任何第三方可在相同路径复现：

| 证据编号 | 证据内容 | 复现命令 | 修正影响 |
|---------|---------|---------|---------|
| EV-01 | seL4 `src/` 实有 **11** 个子目录（含 model/ + plat/） | `ls -la 01Reference/seL4-master/src/` | 纠正 v0.2.2 §3.2 声称"9 个"；DIR-P0-01 修复方案补全 model/ |
| EV-02 | OLK-6.6 顶层实有 **24** 个目录（含 ipc/ + rust/ + LICENSES/） | `ls -d 01Reference/kernel-OLK-6.6/*/` | 纠正 v0.2.2 §2.1 声称"21 个"；双源映射补全 |
| EV-03 | seL4 `src/machine/` 含 **5** 文件（含 profiler.c） | `ls 01Reference/seL4-master/src/machine/` | 纠正 v0.2.2 §5.1 遗漏 profiler.c；DIR-P0-01 修复方案补全 |
| EV-04 | seL4 `src/plat/` 含 **42** 个平台扁平枚举 | `ls -d 01Reference/seL4-master/src/plat/*/ \| wc -l` | 纠正 v0.2.2 §3.3 评估偏松；plat/ 设计修正为扁平结构 |
| EV-05 | seL4 `.bf` 文件共 **25** 个，分布于 **7 层** | `find 01Reference/seL4-master -name "*.bf"` | 纠正 v0.2.2 §3.4 "三处分布"严重简化；DIR-P1-06 修复方案精确化 |
| EV-06 | seL4 `libsel4/` 四级 include 分层 | `ls -d 01Reference/seL4-master/libsel4/*/` | 纠正 v0.2.2 完全遗漏；DIR-P1-06 + 附录 A 修正 |
| EV-07 | seL4-master 仓库内**无** proof/spec/capDL 目录 | `find 01Reference/seL4-master -maxdepth 3 -type d` | 纠正 v0.2.1 附录 A 误称"借鉴 proof/spec/capDL"；DIR-P1-08 修正 |
| EV-08 | v0.2.1 §1.4+§11.1 声明 [SC] 仅宿主于 kernel，但 §5.2/§6.2/§7.2 物理列出 | `Grep security_types.h memory_types.h cognition_types.h` | **NEW-P0-01 最严重发现**：[SC] 单一数据源违规 |
| EV-09 | OLK-6.6 `arch/x86/` 实有 **26** 个子目录 | `ls -d 01Reference/kernel-OLK-6.6/arch/x86/*/` | 纠正 v0.2.2 §2.2 严重简化（声称"~6"）；arch/ 设计精确化 |
| EV-10 | OLK-6.6 `kernel/` 实有 **22** 个子目录 | `ls -d 01Reference/kernel-OLK-6.6/kernel/*/` | 验证 DIR-P1-03 corekern/ 子目录设计依据 |
| EV-11 | OLK-6.6 顶层 Kbuild(2573B) + Makefile(68KB) **并存** | `ls -la 01Reference/kernel-OLK-6.6/Kbuild 01Reference/kernel-OLK-6.6/Makefile` | 纠正 v0.2.2 DIR-P2-02"Kbuild→Makefile"过度简化；改为 Kbuild+Makefile 并存 |

### 0.3 修正优先级矩阵

| 优先级 | 来源 | 数量 | 处理时机 |
|--------|------|------|---------|
| **P0** | v0.2.2 DIR-P0-01~04 + Phase 4 NEW-P0-01 | 5 项 | v0.2.3 立即修正（1.0.1 M0 目录骨架前） |
| **P1** | v0.2.2 DIR-P1-01~08 + Phase 4 NEW-P1-01~06 | 14 项 | v0.2.3 修正 |
| **P2** | v0.2.2 DIR-P2-01~06 + Phase 4 NEW-P2-01~04 | 10 项 | v0.2.3 修正或明确边界声明 |

---

## 第 1 章 设计总则（修正版）

### 1.1 双源融合的目录映射（修正后）

本设计将"双源融合裁决"落实为目录组织规则，每条映射附直接证据：

| 裁决来源 | 目录映射 | 适用子仓 | 证据 |
|---------|---------|---------|------|
| ES-OLK-1 关注点分离 | 8 子仓顶层划分即 8 个关注点 | 全部 | OLK-6.6 顶层 24 目录各司其职（EV-02） |
| ES-OLK-2 架构正交 | `arch/{x86,arm64,riscv}/` 隔离架构相关代码 | kernel | OLK-6.6 `arch/x86/` 26 子目录（EV-09）；seL4 `src/arch/{arm,riscv,x86}/` 各内部镜像 src/ 结构 |
| ES-OLK-3 / ES-OLK-6 UAPI 物理隔离 | `include/uapi/airymax/`（UAPI）与 `include/airymax/`（内部）分离 | kernel / security / memory / cognition | OLK-6.6 `include/uapi/` + `include/linux/` 分离 |
| ES-OLK-4 / ES-OLK-7 Kconfig + Kbuild | `Kbuild` + `Kconfig` + `Makefile` 三层构建（Kbuild 与 Makefile 并存） | kernel / security / memory / cognition | OLK-6.6 顶层 Kbuild(2573B)+Makefile(68KB) 并存（EV-11） |
| ES-OLK-8 MAINTAINERS | 每子仓根 `MAINTAINERS` 文件（R-03 落地） | 全部 | OLK-6.6 顶层 MAINTAINERS |
| ES-OLK-9 规范可执行 | `scripts/` 检查脚本 + CI 集成 | 全部 | OLK-6.6 `scripts/checkpatch.pl` |
| ES-OLK-13 文档即代码 | `Documentation/` 子目录 | kernel | OLK-6.6 `Documentation/` |
| ES-SEL4-1 极简原则 | `corekern/` 仅保留 4 原子机制（IPC/内存/任务/时间） | kernel | seL4 `src/kernel/` 仅 6 文件（boot/cspace/faulthandler/sporadic/stack/thread） |
| ES-SEL4-2 capability 单一模型 | `capability/` 独立模块 + [SC] security_types.h | security | seL4 `src/object/cnode.c` capability 节点模型 |
| ES-SEL4-3 服务用户态化 | `userland-vfs/` `userland-net/` `userland-drivers/` | services | seL4 服务用户态化设计思想 |
| ES-SEL4-4 消息传递 IPC | `ipc/` 基于 io_uring，含 fastpath 优化 | kernel / services | seL4 `src/fastpath/fastpath.c` |
| ES-SEL4-5 形式化验证 | `formal-verification/{spec,proof}/`（seL4 风格，但证明在独立仓库） | tests-linux | seL4-master 无 proof/ 目录，仅 `.github/workflows/proof.yml` 触发外部验证（EV-07） |
| ES-SEL4-7 架构正交分层 | `arch/` + `machine/`（架构无关通用）+ `plat/`（扁平平台枚举）三层 | kernel | seL4 `src/machine/` 为架构无关通用层（EV-03）；`src/plat/` 42 平台扁平（EV-04） |
| ES-SEL4-9 用户态 API 库独立 | `sdk/`（libsel4 模型借鉴，4 语言） | cloudnative | seL4 `libsel4/` 独立于 `src/`（EV-06） |

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
├── .clang-format          # C 代码格式（OS-FMT-001 Tab 8，仅 kernel/security/memory/cognition）
├── .editorconfig          # 编辑器统一配置
└── CONTRIBUTING.md        # 贡献指南（DCO + Signed-off-by + 审查流程）
```

**[NEW-P1-01 修正]**: 含 Rust 代码的子仓（cognition + cloudnative）必须额外包含 `rustfmt.toml`（OS-FMT-001 4 空格）。v0.2.1 仅 cognition/ 有 rustfmt.toml，cloudnative/ 遗漏，本版补全。

### 1.3 子仓类型与构建系统

8 子仓按代码形态分为 4 类，每类对应不同构建系统：

| 类型 | 子仓 | 构建系统 | 依据 |
|------|------|---------|------|
| 内核态 C | kernel / security / memory / cognition（kthread 部分） | Kbuild + Kconfig + Makefile（三者并存，EV-11） | ES-OLK-7（与 Linux 6.6 一致） |
| 用户态 C | services（daemons） | Meson（推荐，现代用户态构建） | ES-SEL4-10 现代构建系统借鉴 |
| 用户态多语言 | cloudnative（Go/Rust/TS） / cognition（Wasm/Rust） / system（Rust/Python） | Cargo + Go Modules + tsc + Meson（按语言） | 各语言生态主流 |
| 测试 | tests-linux | CTest + Cargo + Go + Shell | 多语言测试聚合 |

### 1.4 IRON-9 v2 [SC] 共享契约层单一数据源（NEW-P0-01 核心修正）

> **本节是 v0.2.3 最关键的修正**。v0.2.1 存在严重的单一数据源违规：§1.4 + §11.1 声明 6 个 [SC] 头文件**仅物理宿主**于 `kernel/include/airymax/`，但 §5.2、§6.2、§7.2 又分别在 security/memory/cognition 子仓自身的 `include/airymax/<sub>/` 下**物理列出** security_types.h、memory_types.h、cognition_types.h，造成 3 个 [SC] 头文件存在**两份物理副本**（EV-08 直接证据）。

#### 1.4.1 单一数据源铁律

6 个 [SC] 共享契约头文件**仅物理宿主**于 `kernel/include/airymax/`，是**唯一物理副本**：

| [SC] 头文件 | 物理宿主路径（唯一） | 用途 | 引用方 |
|------------|---------------------|------|--------|
| bpf_struct_ops.h | `kernel/include/airymax/bpf_struct_ops.h` | struct_ops 状态机 + common_value | kernel |
| memory_types.h | `kernel/include/airymax/memory_types.h` | MemoryRovol L1-L4 + GFP 掩码 + PMEM | kernel / memory / tests-linux |
| security_types.h | `kernel/include/airymax/security_types.h` | capability 38 ID + LSM 254 ID + Cupolas blob | kernel / security / tests-linux |
| cognition_types.h | `kernel/include/airymax/cognition_types.h` | CoreLoopThree 三阶段 + Thinkdual + LLM 推理 | kernel / cognition / tests-linux |
| sched.h | `kernel/include/airymax/sched.h` | 任务描述符（magic 0x41475453）+ vtime + 优先级 | kernel / services / tests-linux |
| ipc.h | `kernel/include/airymax/ipc.h` | IPC magic 0x41524531 + 128B 消息头 + SQE/CQE | kernel / services / tests-linux |

#### 1.4.2 子仓引用方式（禁止物理副本）

其他子仓**不得**在自身 `include/` 下创建 [SC] 头文件的物理副本，**必须**通过构建系统 include path 引用 kernel 子仓的物理宿主：

```
# 各子仓 Makefile / Kbuild 中的引用方式（示例）
# security/Makefile:
ccflags-y += -I$(srctree)/../kernel/include

# memory/Kbuild:
ccflags-y += -I$(srctree)/../kernel/include

# cognition/Kbuild:
ccflags-y += -I$(srctree)/../kernel/include
```

#### 1.4.3 子仓内部头文件命名规范（避免与 [SC] 混淆）

子仓自身的 `include/airymax/<sub>/` 目录**只存放该子仓内部头文件**（非 [SC]），命名以 `_internal.h` 后缀区分：

| 子仓 | 内部头文件目录 | 内容（均为非 [SC] 内部头） |
|------|--------------|--------------------------|
| security | `security/include/airymax/security/` | capability_internal.h / lsm_internal.h / cupolas_internal.h |
| memory | `memory/include/airymax/memory/` | memoryrovol_internal.h / cxl_internal.h / pmem_internal.h |
| cognition | `cognition/include/airymax/cognition/` | clt_internal.h / llm_internal.h / thinkdual_internal.h |

**关键区分**: [SC] 头文件无 `_internal` 后缀（如 `security_types.h`），子仓内部头文件有 `_internal` 后缀（如 `capability_internal.h`）。任何子仓的 `include/airymax/<sub>/` 下**禁止出现** [SC] 头文件名。

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

| 依据 | 来源 | 体现 | 直接证据 |
|------|------|------|---------|
| ES-OLK-2 架构正交 | OLK-6.6 arch/ | `arch/{x86,arm64,riscv}/` 隔离 | EV-09：arch/x86/ 26 子目录 |
| ES-OLK-6 UAPI 物理隔离 | OLK-6.6 include/uapi/ | `include/uapi/airymax/` + `include/airymax/` | OLK-6.6 include/{uapi,linux} 分离 |
| ES-OLK-7 Kbuild+Kconfig+Makefile | OLK-6.6 三层构建 | `Kbuild` + `Kconfig` + `Makefile` 并存 | EV-11：Kbuild(2573B)+Makefile(68KB) |
| ES-SEL4-1 极简原则 | seL4 src/kernel/ 6 文件 | `corekern/` 仅 4 原子机制 | seL4 src/kernel/ boot/cspace/... |
| ES-SEL4-7 架构正交分层 | seL4 src/{machine,plat} | `arch/` + `machine/`（通用）+ `plat/`（扁平） | EV-03 + EV-04 |
| atoms/corekern 复用 | Airymax 同源 | `corekern/` 模块 | atoms/corekern MicroCoreRT |
| [SC] 6 头文件唯一宿主 | IRON-9 v2 + NEW-P0-01 修正 | `include/airymax/*.h`（唯一物理副本） | EV-08 |

### 3.2 完整目录结构（修正版）

> **修正摘要**（相对 v0.2.1）：
> - **DIR-P0-01**: `machine/{x86,arm64,riscv}/` → `machine/`（架构无关通用层）+ 架构相关移入 `arch/<arch>/machine/`
> - **DIR-P0-02**: 删除顶层 `entry/`，移入 `arch/<arch>/entry/`
> - **DIR-P0-04**: `configs/` 移入 `arch/<arch>/configs/`
> - **DIR-P1-01**: 新增 `init/`
> - **DIR-P1-02**: 新增 `lib/`
> - **DIR-P1-03**: `corekern/` 新增 `api/` `locking/` `irq/`
> - **DIR-P1-04**: `corekern/memory/` 仅留接口
> - **DIR-P1-05**: 新增 `corekern/object/`
> - **DIR-P1-06**: `syscall.xml` → `include/uapi/airymax/`，`structures.bf` → `include/airymax/`
> - **DIR-P1-07**: `bpf/` 移入 `corekern/bpf/`
> - **DIR-P2-02**: Kbuild + Makefile 并存（非仅 Kbuild）
> - **DIR-P2-06**: 新增 `scripts/dts/`

```
kernel/                           # airymaxos-kernel（feature/official-hubs-01 分支）
├── README.md                     # 英文 README
├── README_zh.md                  # 中文 README
├── LICENSE                       # AGPL-3.0 + Apache-2.0
├── NOTICE
├── MAINTAINERS                   # 维护者制度（R-03）
├── CONTRIBUTING.md
├── .gitignore
├── .clang-format                 # OS-FMT-001 Tab 8
├── .editorconfig
│
├── Kbuild                        # 顶层 Kbuild（递归构建入口）[EV-11: OLK-6.6 顶层 Kbuild 2573B]
├── Kconfig                       # 顶层 Kconfig（特性配置入口）
├── Makefile                      # 顶层 Makefile（构建规则）[EV-11: OLK-6.6 顶层 Makefile 68KB]
│
├── arch/                         # 架构相关代码（ES-OLK-2 + ES-SEL4-7）
│   │                             # [EV-09: OLK-6.6 arch/x86/ 26 子目录]
│   │                             # [seL4: src/arch/{arm,riscv,x86}/ 各内部镜像 src/ 结构]
│   ├── x86/                      # x86/x86_64 架构
│   │   ├── Kbuild
│   │   ├── Kconfig
│   │   ├── configs/              # x86 defconfig [DIR-P0-04: 从顶层 configs/ 移入]
│   │   │   ├── airymax_x86_64_defconfig
│   │   │   └── hardening.config
│   │   ├── include/              # x86 架构相关头文件
│   │   ├── kernel/               # x86 内核执行逻辑
│   │   ├── mm/                    # x86 内存管理
│   │   ├── entry/                 # x86 系统调用/中断入口 [DIR-P0-02: 从顶层移入]
│   │   ├── machine/               # x86 架构相关机器原语 [DIR-P0-01: 从顶层 machine/x86 移入]
│   │   │   ├── capdl.c            # capability 分布描述（架构特定版）
│   │   │   ├── fpu.c              # 浮点单元（架构特定版）
│   │   │   ├── registerset.c      # 寄存器集（架构特定版）
│   │   │   └── hardware.c         # 硬件探测
│   │   ├── lib/                   # x86 特定库函数 [对应 OLK-6.6 arch/x86/lib/]
│   │   └── boot/                  # x86 启动引导 [对应 OLK-6.6 arch/x86/boot/]
│   ├── arm64/                     # ARM64 架构
│   │   ├── Kbuild
│   │   ├── Kconfig
│   │   ├── configs/               # arm64 defconfig [DIR-P0-04]
│   │   │   └── airymax_arm64_defconfig
│   │   ├── include/
│   │   ├── kernel/
│   │   ├── mm/
│   │   ├── entry/
│   │   ├── machine/               # arm64 架构相关机器原语 [DIR-P0-01]
│   │   │   ├── capdl.c
│   │   │   ├── fpu.c
│   │   │   ├── registerset.c
│   │   │   └── gic_v3.c           # GIC v3 中断控制器
│   │   ├── lib/
│   │   └── boot/
│   └── riscv/                     # RISC-V 架构
│       ├── Kbuild
│       ├── Kconfig
│       ├── configs/               # riscv defconfig [DIR-P0-04]
│       │   └── airymax_riscv64_defconfig
│       ├── include/
│       ├── kernel/
│       ├── mm/
│       ├── entry/
│       ├── machine/               # riscv 架构相关机器原语 [DIR-P0-01]
│       │   ├── capdl.c
│       │   ├── fpu.c
│       │   └── registerset.c
│       ├── lib/
│       └── boot/
│
├── include/                      # 公共头文件（ES-OLK-3 / ES-OLK-6）
│   ├── uapi/                     # 用户空间 ABI（永久稳定，OS-IRON-001）
│   │   └── airymax/
│   │       ├── syscall.h         # 系统调用号定义（冻结）
│   │       ├── syscall.xml       # [R-01] 系统调用契约源定义 [DIR-P1-06]
│   │       │                     # [证据: seL4 libsel4/include/api/syscall.xml 4114B]
│   │       ├── ipc.h             # IPC UAPI（128B 消息头用户可见部分）
│   │       ├── sched.h           # 调度 UAPI
│   │       ├── memory.h         # 内存 UAPI
│   │       ├── security.h       # 安全 UAPI
│   │       └── cognition.h      # 认知 UAPI
│   ├── airymax/                  # 内核内部头文件（[SC] 唯一物理宿主，NEW-P0-01 修正）
│   │   ├── bpf_struct_ops.h      # [SC] struct_ops 状态机（唯一物理副本）
│   │   ├── memory_types.h        # [SC] MemoryRovol L1-L4（唯一物理副本）
│   │   ├── security_types.h      # [SC] capability 38 ID + LSM 254 ID（唯一物理副本）
│   │   ├── cognition_types.h     # [SC] CoreLoopThree + Thinkdual（唯一物理副本）
│   │   ├── sched.h               # [SC] 任务描述符（AGTS）+ vtime（唯一物理副本）
│   │   ├── ipc.h                 # [SC] IPC magic 0x41524531 + 128B 消息头（唯一物理副本）
│   │   ├── structures_32.bf      # [R-02] 32-bit 位域定义 [DIR-P1-06]
│   │   ├── structures_64.bf      # [R-02] 64-bit 位域定义 [DIR-P1-06]
│   │   │                         # [证据 EV-05: seL4 include/object/structures_{32,64}.bf，非单一 structures.bf]
│   │   ├── corekern.h            # 微核心原语内部头
│   │   └── airymax_kernel.h      # 总头文件
│   └── asm-generic/              # 通用汇编默认实现（ES-OLK-2）
│
├── corekern/                     # 微核心原语（ES-SEL4-1 极简原则，复用 atoms/corekern）
│   ├── Kbuild
│   ├── Kconfig
│   ├── api/                      # 系统调用分发 [DIR-P1-03 新增]
│   │   │                         # [对应 seL4 src/api/ — syscall.c + faults.c]
│   │   ├── syscall_dispatch.c    # syscall 分发逻辑
│   │   └── faults.c              # 错误处理
│   ├── sched/                    # 调度原语（sched_ext 策略，非 SCHED_AGENT 宏）
│   │   ├── airymax_agent_sched.c  # 默认 Agent 感知 BPF 调度器
│   │   ├── core_sched.c
│   │   └── ext.c                  # sched_ext 框架接入
│   ├── ipc/                      # IPC 原语（io_uring 用户态-内核态 + kfifo kthread 间）
│   │   ├── io_uring_ipc.c        # 用户态-内核态 IPC
│   │   ├── kfifo_ipc.c           # kthread 间 IPC
│   │   └── fastpath.c            # IPC fastpath 优化（ES-SEL4-4 借鉴）
│   │                             # [对应 seL4 src/fastpath/fastpath.c 31KB]
│   ├── taskflow/                 # 任务流原语（graph_engine A 类微核心）
│   │   ├── graph_engine.c
│   │   └── task_descriptor.c     # 任务描述符（magic 0x41475453）
│   ├── memory/                   # 内存原语接口 [DIR-P1-04: 仅留接口，实现移入 memory 子仓]
│   │   ├── page_alloc.h          # page alloc 接口声明
│   │   └── vtime.c               # vtime 衰减公式（调度相关，留此）
│   ├── time/                     # 时间原语（CLOCK_REALTIME 北京时间对齐）
│   │   └── clock.c
│   ├── object/                   # 内核对象 [DIR-P1-05 新增]
│   │   │                         # [对应 seL4 src/object/ — cnode/tcb/endpoint/notification]
│   │   ├── cnode.c               # capability 节点（内核侧）
│   │   ├── tcb.c                 # 线程控制块（内核侧）
│   │   ├── endpoint.c            # IPC 端点对象
│   │   └── notification.c       # 通知对象
│   ├── locking/                  # 锁机制与同步原语 [DIR-P1-03 新增]
│   │   │                         # [对应 OLK-6.6 kernel/locking/]
│   │   ├── spinlock.c
│   │   ├── rwsem.c
│   │   └── futex_core.c
│   ├── irq/                      # 中断处理 [DIR-P1-03 新增]
│   │   │                         # [对应 OLK-6.6 kernel/irq/]
│   │   ├── irq_manage.c
│   │   └── irq_domain.c
│   └── bpf/                      # eBPF 可编程内核 [DIR-P1-07: 从顶层 bpf/ 移入]
│       │                         # [对应 OLK-6.6 kernel/bpf/，非顶层]
│       ├── Kbuild
│       ├── Kconfig
│       ├── airymax_bpf_kfunc.c   # eBPF kfunc 注册
│       ├── dynamic_pointer.c     # dynamic pointer 支持
│       └── struct_ops/           # struct_ops 状态机（[SC] bpf_struct_ops.h）
│           └── airymax_sched_ops.c
│
├── init/                         # 内核初始化 [DIR-P1-01 新增]
│   │                             # [对应 OLK-6.6 init/ — main.c + Kconfig]
│   ├── Kbuild
│   ├── main.c                    # 内核入口主函数
│   ├── do_initcalls.c            # 初始化调用链
│   └── version.c                 # 版本信息
│
├── lib/                          # 通用库函数 [DIR-P1-02 新增]
│   │                             # [对应 OLK-6.6 lib/]
│   ├── Kbuild
│   ├── string.c                  # 字符串操作
│   ├── ctype.c                   # 字符类型
│   ├── bitmap.c                  # 位图操作
│   └── radix-tree.c              # 基数树
│
├── machine/                      # 架构无关通用机器原语层 [DIR-P0-01 核心修正]
│   │                             # [证据 EV-03: seL4 src/machine/ — io.c/capdl.c/registerset.c/fpu.c/profiler.c]
│   │                             # [修正: v0.2.1 machine/{x86,arm64,riscv}/ 误解 seL4 三层模型，
│   │                             #  与 arch/ 重复架构维度；改为架构无关通用层]
│   ├── capdl.c                   # capability 分布描述（通用版）
│   ├── fpu.c                     # 浮点单元（通用版）
│   ├── io.c                      # I/O（通用版）
│   ├── registerset.c             # 寄存器集（通用版）
│   └── profiler.c                # 性能剖析（通用版）[EV-03: v0.2.2 遗漏，本版补全]
│
├── crypto/                       # 加密算法库 [DIR-P0-03: 从 security/crypto/ 提升至 kernel 顶层]
│   │                             # [证据: OLK-6.6 crypto/ 是顶层平级目录，非 security 子目录]
│   │                             # [理由: crypto 被 kernel/fs/net 等多子系统使用，非 security 专属]
│   ├── Kbuild
│   ├── Kconfig
│   ├── api.c                     # 加密 API 框架
│   ├── sm2-sm4/                  # 国密算法（SM2/SM3/SM4/SM9）
│   │   ├── sm2.c
│   │   ├── sm3.c
│   │   ├── sm4.c
│   │   └── sm9.c
│   ├── aes/                      # AES
│   └── sha/                      # SHA 系列
│
├── io_uring/                     # 异步 I/O（ES-OLK-1 独立子系统）
│   │                             # [对应 OLK-6.6 io_uring/ 顶层目录]
│   ├── Kbuild
│   ├── Kconfig
│   ├── airymax_io_uring.c        # io_uring 核心扩展
│   └── airymax_msg_ring.c        # msg_ring IPC 优化
│
├── patches/                      # 上游补丁集 [DIR-P2-01: 明确定位为"对上游 Linux 内核的修改补丁"]
│   │                             # [定位澄清 NEW-P1-06: 补丁是修改上游内核的 diff，
│   │                             #  实现代码在对应子仓（security/services），不在此重复]
│   ├── sched_ext-agent/          # Agent 感知调度补丁
│   │   └── 0001-sched_ext-add-airymax-agent-sched.patch
│   ├── io_uring-ipc/             # IPC 消息传递补丁
│   │   └── 0001-io_uring-add-airymax-ipc-opcodes.patch
│   ├── rust-drivers/             # Rust 安全驱动补丁
│   │   └── 0001-rust-add-airymax-driver-framework.patch
│   └── microkernel/              # 微内核化改造补丁集（修改上游内核的 diff，非实现）
│       ├── capability.patch      # capability 令牌接入补丁（实现在 security/capability/）
│       ├── vfs-userns.patch      # VFS 用户态化补丁（实现在 services/userland-vfs/）
│       ├── net-userns.patch      # 网络栈用户态化补丁（实现在 services/userland-net/）
│       └── driver-split.patch    # 驱动拆分补丁（实现在 services/userland-drivers/）
│
├── Documentation/                # 文档即代码（ES-OLK-13）
│   │                             # [对应 OLK-6.6 Documentation/]
│   ├── ABI/                      # ABI 文档（OS-IRON-001）
│   │   ├── syscalls/
│   │   ├── ioctl/
│   │   └── procfs/
│   ├── airymax/                  # airymax 专属文档
│   │   ├── microkernel-strategy.md
│   │   ├── sched-ext-design.md
│   │   └── ipc-design.md
│   └── process/                  # 开发流程文档
│
├── scripts/                      # 构建与检查脚本（ES-OLK-9）
│   │                             # [对应 OLK-6.6 scripts/checkpatch.pl]
│   ├── checkpatch.pl             # 编码规范检查（OS-STD-CODE-001~027）
│   ├── syscall_gen.py            # syscall.xml → C 代码生成（R-01）
│   │                             # [证据: seL4 tools/invocation_header_gen.py 处理 syscall.xml]
│   ├── bitfield_gen.py           # structures.bf → C 代码生成（R-02）
│   │                             # [证据 EV-05: seL4 tools/bitfield_gen.py 123KB + bitfield_gen.md 36KB]
│   ├── kbuild_check.py           # Kbuild/Kconfig 规范检查
│   ├── maintainer_check.py       # MAINTAINERS 完整性检查（R-03）
│   └── dts/                      # 设备树源文件 [DIR-P2-06 新增]
│       │                         # [证据: seL4 tools/dts/ 含各平台 .dts]
│       ├── qemu-x86_64.dts
│       ├── qemu-arm64.dts
│       └── qemu-riscv64.dts
│
└── tests/                        # 内核单元测试
    │                             # [DIR-P2-03 边界澄清: 此处仅 kernel 子仓自身测试，
    │                             #  跨子仓集成测试在 tests-linux/integration/]
    ├── kunit/                    # KUnit 单元测试
    └── kselftest/                # kselftest 集成测试
```

### 3.3 关键设计说明（修正版）

1. **arch/ + machine/ + plat/ 三层架构适配（DIR-P0-01 核心修正）**:

   v0.2.1 的 `machine/{x86,arm64,riscv}/` 与 `arch/` 平级、按架构分目录，**误解了 seL4 三层模型**。经直接证据（EV-03）确认 seL4 的真实三层结构：

   | 层次 | seL4 真实结构（EV-03/04） | v0.2.3 修正 | v0.2.1 错误 |
   |------|--------------------------|-------------|-------------|
   | `machine/` | `src/machine/`（**架构无关通用**：io.c/capdl.c/registerset.c/fpu.c/**profiler.c**）+ `src/arch/<arch>/machine/`（架构特定） | `machine/`（架构无关通用层）+ `arch/<arch>/machine/`（架构特定） | `machine/{x86,arm64,riscv}/`（与 arch/ 重复架构维度） |
   | `arch/` | `src/arch/{arm,riscv,x86}/`，内部镜像 src/ 结构 | `arch/{x86,arm64,riscv}/`，内部含 machine/ + entry/ + configs/ | `arch/` 内部无 machine/ |
   | `plat/` | `src/plat/` **42 平台扁平枚举**（EV-04） | v0.2.3 删除顶层 plat/，平台特定代码在 `scripts/dts/` + `arch/<arch>/` | `plat/{qemu-x86_64,qemu-arm64,hardware-platforms}/` 三分类 |

   **plat/ 删除理由**: seL4 的 `src/plat/` 含 42 个真实硬件平台（bcm2711/imx8m/rk3568/zynqmp 等），是**编译期选择的具体平台**。agentrt-linux 1.0.1 阶段仅支持 QEMU 虚拟平台，平台特定差异通过 DTS（`scripts/dts/`）+ arch（`arch/<arch>/`）覆盖，不需要独立 plat/ 顶层目录。若未来支持真实硬件平台，可按 seL4 模式新增 `plat/` 扁平枚举。

2. **corekern/ 极简原则与子目录扩展（DIR-P1-03/05/07）**:

   `corekern/` 对应 seL4 极简原语（ES-SEL4-1），但 v0.2.1 仅 4 子目录（sched/ipc/taskflow/memory/time），遗漏 seL4 `src/api/`（syscall 分发）+ `src/object/`（内核对象）+ OLK-6.6 `kernel/{locking,irq}/`。v0.2.3 补全为 9 子目录：api/sched/ipc/taskflow/memory/time/object/locking/irq/bpf。

   **[SC] 对齐**: `corekern/sched/airymax_agent_sched.c` 对齐 [SC] sched.h（任务描述符 magic 0x41475453 + vtime 衰减公式 + 优先级 0-139）；`corekern/ipc/` 对齐 [SC] ipc.h（IPC magic 0x41524531 + 128B 消息头）；`corekern/bpf/struct_ops/` 对齐 [SC] bpf_struct_ops.h。

3. **[SC] 6 头文件唯一物理宿主（NEW-P0-01 核心修正）**:

   `include/airymax/*.h` 是 IRON-9 v2 [SC] 共享契约层的**唯一物理宿主**。其他子仓（security/memory/cognition）通过 `-I../kernel/include` 引用，**禁止**在自身 `include/airymax/<sub>/` 下创建物理副本（详见 §1.4）。

4. **patches/ 定位澄清（DIR-P2-01 + NEW-P1-06）**:

   `patches/` 仅存放**对上游 Linux 内核的修改 diff**（每个补丁独立可编译，OS-IRON-004，符合 git bisect 友好 ES-OLK-10）。补丁修改的功能，其**实现代码在对应子仓**：
   - `capability.patch` 修改上游内核 → 实现在 `security/capability/`
   - `vfs-userns.patch` 修改上游内核 → 实现在 `services/userland-vfs/`
   - `net-userns.patch` 修改上游内核 → 实现在 `services/userland-net/`
   - `driver-split.patch` 修改上游内核 → 实现在 `services/userland-drivers/`

5. **scripts/ codegen 工具与源文件位置（DIR-P1-06）**:

   生成器在 `scripts/`（`syscall_gen.py` + `bitfield_gen.py`），源文件在 `include/`：
   - `syscall.xml`（R-01 源）→ `include/uapi/airymax/syscall.xml`（证据：seL4 在 `libsel4/include/api/syscall.xml`）
   - `structures_{32,64}.bf`（R-02 源）→ `include/airymax/structures_{32,64}.bf`（证据 EV-05：seL4 在 `include/object/structures_{32,64}.bf`，**非单一 structures.bf**，v0.2.2 报告此处严重简化）

---

## 第 4 章 airymaxos-services（services/）

### 4.1 设计依据

| 依据 | 来源 | 体现 | 直接证据 |
|------|------|------|---------|
| ES-SEL4-3 服务用户态化 | seL4 用户态服务 | `userland-{vfs,net,drivers}/` | seL4 服务用户态化思想 |
| ES-SEL4-4 消息传递 IPC | seL4 endpoint/notification | `ipc/` 基于 io_uring | seL4 src/object/endpoint.c |
| 12 daemons | Airymax 同源 | `daemons/` 12 子目录 | Airymax daemons |
| ES-SEL4-10 现代构建 | seL4 CMake | Meson（用户态现代构建） | seL4 CMakeLists.txt |

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
│   │                             # [边界澄清 NEW-P1-02: 用户态 VFS 服务进程，
│   │                             #  与 memory/vfs-persist/（内核态持久化后端接口）职责不同]
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
│   └── include/
│
├── userland-drivers/             # 驱动用户态化（ES-SEL4-3 Phase 2）
│   ├── meson.build
│   ├── src/
│   └── include/
│
├── ipc/                          # io_uring 消息传递（ES-SEL4-4）
│   ├── meson.build
│   ├── src/
│   │   ├── io_uring_client.c
│   │   ├── io_uring_server.c
│   │   └── msg_ring.c           # msg_ring IPC（128B 消息头）
│   └── include/
│       └── airymax_ipc.h         # 引用 [SC] ipc.h（通过 -I../kernel/include，非物理副本）
│
├── systemd/                      # systemd 集成（daemon unit 文件）
│   │                             # [边界澄清 NEW-P2-03: 此处存放 12 daemons 的 .service unit 文件，
│   │                             #  与 system/config/systemd/（systemd 守护进程自身配置）职责不同]
│   ├── units/                    # systemd unit 文件
│   │   ├── airymax-gateway.service
│   │   ├── airymax-llm.service
│   │   └── ... (12 daemons)
│   └── configs/
│
├── include/                      # 公共头文件（仅 services 内部头，无 [SC] 物理副本）
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

3. **userland-* 与 memory/vfs-persist 边界（NEW-P1-02 澄清）**:
   - `services/userland-vfs/` = **用户态 VFS 服务进程**（运行在用户空间，提供文件系统服务）
   - `memory/vfs-persist/` = **内核态持久化后端接口**（内核模块，提供多后端持久化能力）
   - 两者职责不同：前者是服务进程，后者是内核接口；通过 [SC] ipc.h 的消息传递通信。

4. **systemd 边界（NEW-P2-03 澄清）**:
   - `services/systemd/` = 12 daemons 的 `.service` unit 文件（启动 12 个守护进程）
   - `system/config/systemd/` = systemd 守护进程自身配置（system.conf、journal.conf）

---

## 第 5 章 airymaxos-security（security/）

### 5.1 设计依据

| 依据 | 来源 | 体现 | 直接证据 |
|------|------|------|---------|
| ES-SEL4-2 capability 单一模型 | seL4 capability | `capability/` 独立模块 | seL4 src/object/cnode.c |
| ES-OLK-1 关注点分离 | OLK-6.6 security/ | 每策略一目录 | OLK-6.6 security/{selinux,landlock,...} |
| ES-OLK-3 UAPI 隔离 | OLK-6.6 include/uapi/ | `include/uapi/airymax/security/` | OLK-6.6 include/uapi/ |
| Cupolas 四层 | Airymax 同源 | `cupolas/{rules,policy,sanitize,audit}/` | Airymax cupolas |
| [SC] security_types.h 唯一宿主 | IRON-9 v2 + NEW-P0-01 | 引用 kernel/include/airymax/（无物理副本） | EV-08 |

### 5.2 完整目录结构（修正版）

> **修正摘要**（相对 v0.2.1）：
> - **DIR-P0-03**: `crypto/` 移出（提升至 kernel 顶层）
> - **NEW-P0-01**: `include/airymax/security/security_types.h` 删除（[SC] 唯一宿主在 kernel，本仓仅留 `_internal.h`）

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
├── Kbuild                       # 内核态构建
├── Kconfig
├── Makefile
│
├── include/
│   ├── uapi/airymax/security/    # 安全 UAPI（永久稳定）
│   │   ├── capability.h          # capability 38 ID 枚举
│   │   ├── lsm_hooks.h           # LSM 254 ID 枚举
│   │   └── cupolas.h            # Cupolas UAPI
│   └── airymax/security/         # 内核内部头文件（仅 security 内部，无 [SC] 物理副本）
│       ├── capability_internal.h # [NEW-P0-01 修正: security_types.h 已删除，改为引用 kernel/include/airymax/]
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
│   │                             # [对应 OLK-6.6 security/{selinux,landlock,apparmor,bpf,...}]
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
│   │   ├── input_sanitize.c
│   │   ├── output_desens.c
│   │   └── prompt_injection.c    # Prompt 注入防护
│   └── audit/                    # L4 审计层（不可插拔，强制）
│       ├── audit_log.c           # 全量操作日志
│       └── audit_replay.c        # 行为回放
│
├── sandbox/                      # 进程沙箱
│   ├── Kbuild
│   ├── landlock/                 # Landlock（文件访问控制）
│   └── seccomp/                  # seccomp（系统调用过滤）
│
├── confidential-compute/         # TEE 机密计算
│   ├── Kbuild
│   ├── sgx/                      # Intel SGX
│   ├── sev-snp/                  # AMD SEV-SNP
│   └── tdx/                      # Intel TDX
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

### 5.3 关键设计说明（修正版）

1. **[SC] security_types.h 引用方式（NEW-P0-01 核心修正）**:

   v0.2.1 在 `security/include/airymax/security/` 下物理列出 `security_types.h`，造成与 `kernel/include/airymax/security_types.h` **两份物理副本**。v0.2.3 删除本仓的物理副本，改为通过 `-I../kernel/include` 引用唯一宿主：

   ```makefile
   # security/Kbuild
   ccflags-y += -I$(srctree)/../kernel/include
   ```

   本仓 `include/airymax/security/` 仅保留 `capability_internal.h` / `lsm_internal.h` / `cupolas_internal.h`（security 子仓内部头，非 [SC]）。

2. **crypto/ 移出（DIR-P0-03）**: v0.2.1 将 `crypto/` 置于 `security/crypto/`，偏离 OLK-6.6（crypto/ 是顶层平级目录）。v0.2.3 将 crypto/ 提升至 kernel 子仓顶层（`kernel/crypto/`），因为加密算法被 kernel/fs/net 等多子系统使用，非 security 专属。

3. **capability/ 借鉴 seL4 cnode.c 思想**: `capability/cnode.c` 借鉴 seL4 `src/object/cnode.c` 的 capability 节点管理思想（ES-SEL4-2），但不复制 seL4 代码，实现独立。

4. **cupolas/ 四层 L1-L4 对齐 [SC]**: `cupolas/{rules,policy,sanitize,audit}/` 严格对齐 [SC] security_types.h 中的 Cupolas blob 布局，L4 audit 不可插拔（强制）。

---

## 第 6 章 airymaxos-memory（memory/）

### 6.1 设计依据

| 依据 | 来源 | 体现 | 直接证据 |
|------|------|------|---------|
| ES-OLK-1 关注点分离 | OLK-6.6 mm/ | 单一子系统垂直内聚 | OLK-6.6 mm/ 顶层 |
| ES-OLK-3 UAPI 隔离 | OLK-6.6 include/uapi/ | `include/uapi/airymax/memory/` | OLK-6.6 include/uapi/ |
| MemoryRovol 内核态 | Airymax 同源 | `memoryrovol/` | Airymax memoryrovol |
| [SC] memory_types.h 唯一宿主 | IRON-9 v2 + NEW-P0-01 | 引用 kernel/include/airymax/（无物理副本） | EV-08 |

### 6.2 完整目录结构（修正版）

> **修正摘要**（相对 v0.2.1）：
> - **NEW-P0-01**: `include/airymax/memory/memory_types.h` 删除（[SC] 唯一宿主在 kernel，本仓仅留 `_internal.h`）
> - **NEW-P1-02**: `vfs-persist/` 重命名为 `vfs-persist-kern/` 明确内核态边界

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
│   └── airymax/memory/           # 内核内部头文件（仅 memory 内部，无 [SC] 物理副本）
│       ├── memoryrovol_internal.h # [NEW-P0-01 修正: memory_types.h 已删除，改为引用 kernel/include/airymax/]
│       ├── cxl_internal.h
│       └── pmem_internal.h
│
├── memoryrovol/                  # 记忆卷内核态（Airymax 同源 memoryrovol）
│   ├── Kbuild
│   ├── rovol-kmod/               # 记忆卷内核模块
│   │   ├── rovol_core.c          # MemoryRovol 核心
│   │   ├── rovol_l1.c            # L1 数据结构（对齐 [SC] memory_types.h）
│   │   ├── rovol_l2.c            # L2
│   │   ├── rovol_l3.c            # L3
│   │   └── rovol_l4.c            # L4
│   ├── snapshot/                 # 记忆快照（fork + COW）
│   └── migrate/                  # 记忆迁移（跨节点）
│
├── cxl/                          # CXL 内存分层（CXL 3.0 池化）
│   ├── Kbuild
│   ├── cxl_core.c
│   ├── cxl_pool.c
│   ├── cxl_tiering.c             # 内存分层（替代 numa_remote）
│   └── cxl_hotplug.c
│
├── pmem/                         # 持久化内存（PMEM 非易失）
│   ├── Kbuild
│   ├── pmem_core.c
│   ├── pmem_persist.c            # 持久化接口（对齐 [SC] memory_types.h PMEM 接口）
│   └── pmem_map.c
│
├── mglru/                        # MGLRU 多代 LRU（Linux 6.6 内存回收）
│   │                             # [注: 使用"MGLRU 多代 LRU"，禁止"MGLRU 2.0"违规表述]
│   ├── Kbuild
│   ├── mglru_core.c
│   ├── mglru_gen.c               # 多代管理
│   └── mglru_reclaim.c           # 内存回收（替代 etmem）
│
├── vfs-persist-kern/             # 内核态 VFS 持久化后端接口 [NEW-P1-02 重命名]
│   │                             # [边界澄清: 内核态持久化后端接口，
│   │                             #  与 services/userland-vfs/（用户态 VFS 服务进程）职责不同]
│   ├── Kbuild
│   ├── vfs_persist.c             # 持久化后端接口
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

### 6.3 关键设计说明（修正版）

1. **[SC] memory_types.h 引用方式（NEW-P0-01 核心修正）**:

   v0.2.1 在 `memory/include/airymax/memory/` 下物理列出 `memory_types.h`，造成两份物理副本。v0.2.3 删除本仓物理副本，改为 `-I../kernel/include` 引用。本仓 `include/airymax/memory/` 仅保留 `memoryrovol_internal.h` / `cxl_internal.h` / `pmem_internal.h`。

2. **memoryrovol/rovol-kmod/ L1-L4 对齐 [SC]**: `rovol_{l1,l2,l3,l4}.c` 严格对齐 `kernel/include/airymax/memory_types.h`（[SC] 唯一宿主）中的 MemoryRovol L1-L4 数据结构。

3. **不含 etmem/dynamic_pool/numa_remote**: 遵循 project_memory 决策——etmem 用 `memory.reclaim + tiering` 替代（`mglru/` + `cxl/cxl_tiering.c`），dynamic_pool 用 memcg 替代，numa_remote 用 CXL 替代。

4. **vfs-persist-kern/ 重命名（NEW-P1-02）**: v0.2.1 的 `vfs-persist/` 与 `services/userland-vfs/` 命名易混淆。v0.2.3 重命名为 `vfs-persist-kern/`，明确"内核态持久化后端接口"边界，与 services/userland-vfs/（用户态 VFS 服务进程）职责分离。

---

## 第 7 章 airymaxos-cognition（cognition/）

### 7.1 设计依据

| 依据 | 来源 | 体现 | 直接证据 |
|------|------|------|---------|
| CoreLoopThree kthread | Airymax 同源 | `coreloopthree/clt-kmod/` | Airymax coreloopthree |
| ES-SEL4-1 极简 | seL4 kthread | kthread 最小化 | seL4 src/kernel/thread.c |
| ES-SEL4-10 现代构建 | seL4 CMake | Cargo（Rust）+ Kbuild（C kthread） | seL4 CMakeLists.txt |
| [SC] cognition_types.h 唯一宿主 | IRON-9 v2 + NEW-P0-01 | 引用 kernel/include/airymax/（无物理副本） | EV-08 |

### 7.2 完整目录结构（修正版）

> **修正摘要**（相对 v0.2.1）：
> - **NEW-P0-01**: `include/airymax/cognition/cognition_types.h` 删除（[SC] 唯一宿主在 kernel）
> - **NEW-P2-01**: `embodied-ai/` 重命名为 `embodied-io/`（传感器/运动 I/O，非认知核心）
> - **NEW-P2-02**: `super-node-sandbox/` 重命名为 `super-node-cog-snapshot/`（与 cloudnative/super-node-os/ 区分）

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
├── rustfmt.toml                  # Rust 部分（OS-FMT-001 4 空格）
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
│   └── airymax/cognition/        # 内核内部头文件（仅 cognition 内部，无 [SC] 物理副本）
│       ├── clt_internal.h        # [NEW-P0-01 修正: cognition_types.h 已删除，改为引用 kernel/include/airymax/]
│       ├── llm_internal.h
│       └── thinkdual_internal.h
│
├── coreloopthree/                # 三层认知循环（Airymax 同源 coreloopthree）
│   ├── Kbuild
│   └── clt-kmod/                 # kthread 内核模块
│       ├── clt_kthread.c         # CoreLoopThree kthread
│       ├── clt_perception.c      # PERCEPTION 阶段（对齐 [SC] cognition_types.h）
│       ├── clt_thinking.c        # THINKING 阶段
│       ├── clt_action.c          # ACTION 阶段
│       └── clt_context.c         # CoreLoopThree 上下文
│
├── thinkdual/                    # 双思考（快/慢思考切换）
│   ├── Kbuild
│   └── system1-system2/
│       ├── thinkdual_core.c      # 双思考核心
│       ├── system1_fast.c        # SYSTEM1_FAST（对齐 [SC] cognition_types.h）
│       └── system2_slow.c        # SYSTEM2_SLOW
│
├── wasm-runtime/                 # Wasm 3.0 安全沙箱（Rust）
│   ├── Cargo.toml
│   ├── src/
│   │   ├── lib.rs
│   │   ├── wasm_runtime.rs
│   │   ├── sandbox.rs
│   │   └── memory_isolation.rs
│   └── tests/
│
├── llm-scheduler/                # LLM 推理调度
│   ├── Kbuild
│   ├── src/
│   │   ├── llm_sched_core.c      # LLM 调度核心
│   │   ├── prefill_sched.c       # PREFILL 阶段调度（对齐 [SC] cognition_types.h）
│   │   ├── decode_sched.c        # DECODE 阶段调度
│   │   └── speculative_sched.c  # SPECULATIVE 调度
│   └── include/
│
├── compute-accel/                # 算力加速调度（GPU/NPU 池化）[NEW-P2-01 重命名]
│   │                             # [重命名理由: gpu-npu 偏硬件驱动命名，compute-accel 聚焦"算力加速调度"认知职责]
│   ├── Kbuild
│   ├── gpu_scheduler.c
│   ├── npu_scheduler.c
│   └── compute_pool.c           # 算力池化
│
├── token-efficiency/             # Token 能效（KVC-Gateway + LMCache）
│   ├── Kbuild
│   ├── token_metrics.c          # Token 能效指标（对齐 [SC] cognition_types.h）
│   ├── kvc_gateway.c
│   └── lmcache.c
│
├── super-node-cog-snapshot/      # 超节点认知快照（认知态镜像快照）[NEW-P2-02 重命名]
│   │                             # [重命名理由: 与 cloudnative/super-node-os/ 区分。
│   │                             #  本仓是认知态快照恢复，cloudnative/super-node-os 是超节点拓扑管理]
│   ├── Kbuild
│   ├── super_node.c
│   └── snapshot_restore.c        # 认知态快照恢复
│
├── embodied-io/                  # 具身 I/O（传感器输入/运动控制）[NEW-P2-01 重命名]
│   │                             # [重命名理由: embodied-ai 范围过广，embodied-io 聚焦"I/O 通道"
│   │                             #  传感器/运动控制是认知循环的 I/O 通道，非认知核心]
│   ├── Kbuild
│   ├── sensor_input.c           # 传感器输入
│   └── motion_control.c         # 运动控制
│
└── tests/
    ├── unit/
    ├── integration/
    └── cognition_benchmark/      # 认知基准测试
```

### 7.3 关键设计说明（修正版）

1. **[SC] cognition_types.h 引用方式（NEW-P0-01 核心修正）**:

   v0.2.1 在 `cognition/include/airymax/cognition/` 下物理列出 `cognition_types.h`，造成两份物理副本。v0.2.3 删除本仓物理副本，改为 `-I../kernel/include` 引用。本仓 `include/airymax/cognition/` 仅保留 `clt_internal.h` / `llm_internal.h` / `thinkdual_internal.h`。

2. **CoreLoopThree 三阶段对齐 [SC]**: `clt_{perception,thinking,action}.c` 严格对齐 `kernel/include/airymax/cognition_types.h`（[SC] 唯一宿主）中的 PERCEPTION/THINKING/ACTION 三阶段枚举。

3. **Thinkdual 两模式对齐 [SC]**: `system1_fast.c` + `system2_slow.c` 对齐 [SC] cognition_types.h 中的 SYSTEM1_FAST/SYSTEM2_SLOW 枚举。

4. **C + Rust 混合构建**: 内核态 kthread（C，Kbuild）+ Wasm runtime（Rust，Cargo）混合，`clt-kmod/` 是 C kthread，`wasm-runtime/` 是 Rust。

---

## 第 8 章 airymaxos-cloudnative（cloudnative/）

### 8.1 设计依据

| 依据 | 来源 | 体现 | 直接证据 |
|------|------|------|---------|
| K8s 生态 | 云原生主流 | `kubernetes/crds/` + `containerd-shim/` | K8s 生态主流 |
| ES-SEL4-9 用户态 API 库独立 | seL4 libsel4 | `sdk/`（4 语言） | EV-06：seL4 libsel4 四级 include |
| ES-SEL4-10 现代构建 | seL4 CMake | Go Modules + Cargo + tsc | seL4 CMakeLists.txt |

### 8.2 完整目录结构（修正版）

> **修正摘要**（相对 v0.2.1）：
> - **NEW-P1-01**: 新增 `rustfmt.toml`（sdk/rust/ 需要 Rust 格式配置）

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
├── rustfmt.toml                  # Rust 代码格式（OS-FMT-001 4 空格）[NEW-P1-01 新增]
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
├── super-node-os/                # 超节点 OS（超节点拓扑管理）
│   │                             # [NEW-P2-02 边界澄清: 超节点拓扑管理，
│   │                             #  与 cognition/super-node-cog-snapshot/（认知态快照）职责不同]
│   ├── go.mod
│   └── pkg/
│       ├── super_node_manager.go
│       └── topology.go           # 超节点拓扑
│
├── sdk/                          # SDK（libsel4 模型借鉴，4 语言，ES-SEL4-9）
│   │                             # [证据 EV-06: seL4 libsel4 独立于 src/，
│   │                             #  四级 include: arch_include + sel4_arch_include + sel4_plat_include + mode_include]
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

1. **sdk/ 借鉴 libsel4 模型**: 4 语言 SDK 独立于运行时，用户程序通过 SDK 与 agentrt-linux 通信，不直接调用内核/daemon 内部函数（ES-SEL4-9）。seL4 的 libsel4 采用四级 include 分层（arch_include + sel4_arch_include + sel4_plat_include + mode_include，EV-06），agentrt-linux SDK 因面向高层应用（非内核 ABI），简化为按语言分层。

2. **Go 为主语言**: K8s 生态主流语言，CRD 控制器/containerd shim/agentctl 均为 Go。

3. **rustfmt.toml 补全（NEW-P1-01）**: v0.2.1 cloudnative/ 有 sdk/rust/ 但无 rustfmt.toml，与 cognition/ 不一致。v0.2.3 补全，确保含 Rust 代码的子仓均有 rustfmt.toml。

---

## 第 9 章 airymaxos-system（system/）

### 9.1 设计依据

| 依据 | 来源 | 体现 | 直接证据 |
|------|------|------|---------|
| OLK-6.6 包管理 | RPM + dnf | `package-manager/` | OLK-6.6 tools/ |
| Euler 标准兼容 | 发行版工具集 | RPM/dnf/sysctl | Euler 标准兼容约束 |
| Airymax 同源 commons | 公共工具 | `base-libs/` + `devstation/` | Airymax commons |

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
│   ├── systemd/                  # systemd 守护进程自身配置 [NEW-P2-03 边界澄清]
│   │   │                         # [此处存放 systemd 守护进程配置（system.conf/journal.conf），
│   │   │                         #  与 services/systemd/（12 daemons 的 .service unit 文件）职责不同]
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

2. **systemd 配置边界（NEW-P2-03 澄清）**:
   - `services/systemd/` = 12 daemons 的 `.service` unit 文件（启动哪些守护进程）
   - `system/config/systemd/` = systemd 守护进程自身配置（system.conf 日志级别、journal.conf 日志轮转）

3. **devstation/ AI 助手**: DevStation 是 Airymax 同源模块，Python CLI + C 核心 + 插件机制。

---

## 第 10 章 airymaxos-tests-linux（tests-linux/）

### 10.1 设计依据

| 依据 | 来源 | 体现 | 直接证据 |
|------|------|------|---------|
| ES-OLK-9 规范可执行 | OLK-6.6 tools/testing | 多语言测试聚合 | OLK-6.6 tools/testing/ |
| ES-SEL4-5 形式化验证 | seL4 proof/spec（独立仓库） | `formal-verification/{spec,proof}/` + README 说明 | EV-07：seL4-master 无 proof/ 目录，仅 .github/workflows/proof.yml 触发外部验证 |
| ES-OLK-10 regression 零容忍 | OLK-6.6 kselftest | 回归测试覆盖 | OLK-6.6 tools/testing/kselftest |

### 10.2 完整目录结构（修正版）

> **修正摘要**（相对 v0.2.1）：
> - **DIR-P1-08**: `formal-verification/` 新增 README.md 说明 seL4 独立仓库实践
> - **NEW-P1-03**: `formal-verification/` 位置说明（Isabelle/HOL 重依赖说明）

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
├── integration/                  # 集成测试（模块间）[DIR-P2-03 边界: 跨子仓集成]
│   ├── kernel_services/          # kernel ↔ services
│   ├── kernel_security/          # kernel ↔ security
│   ├── kernel_memory/            # kernel ↔ memory
│   ├── kernel_cognition/        # kernel ↔ cognition
│   ├── services_cognition/       # services ↔ cognition
│   ├── security_cognition/      # security ↔ cognition
│   ├── memory_cognition/        # memory ↔ cognition
│   └── e2e/                      # 端到端集成
│
├── formal-verification/         # 形式化验证（seL4 风格，ES-SEL4-5）
│   ├── README.md                 # [DIR-P1-08 + NEW-P1-03 新增]
│   │                             # 说明: seL4 的形式化证明在独立仓库（l4v/capDL），
│   │                             # seL4-master 仓库内无 proof/spec/capDL 目录（EV-07 证据），
│   │                             # 仅 .github/workflows/proof.yml 触发外部验证。
│   │                             # agentrt-linux 采用相同模式：本目录是形式化验证的
│   │                             # 入口与规约，Isabelle/HOL 重依赖证明在独立仓库
│   │                             # airymaxos-proofs（1.0.1 M2 阶段创建）。
│   ├── spec/                     # 抽象规约（Isabelle/HOL）
│   │   ├── kernel_spec/          # 内核规约
│   │   ├── security_spec/        # 安全规约
│   │   └── ipc_spec/             # IPC 规约
│   ├── proof/                    # 形式化证明（轻量入口，重依赖在独立仓库）
│   │   ├── capability_proof/    # capability 派生证明
│   │   ├── ipc_proof/            # IPC 协议证明
│   │   └── sched_proof/          # 调度正确性证明
│   └── capdl/                    # capability 分布描述（参考 seL4 capDL 思想）
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

### 10.3 关键设计说明（修正版）

1. **formal-verification/ seL4 独立仓库实践（DIR-P1-08 + NEW-P1-03 修正）**:

   v0.2.1 附录 A 称"tests-linux seL4 借鉴 proof/spec/capDL"，但经直接证据（EV-07）确认：**seL4-master 仓库内无 proof/spec/capDL 目录**，形式化证明在独立仓库（l4v、capDL），seL4-master 仅含 `.github/workflows/proof.yml`（2168 字节）触发外部仓库验证。

   v0.2.3 修正：
   - 新增 `formal-verification/README.md` 说明此实践
   - `spec/` + `proof/` + `capdl/` 保留作为形式化验证的**入口与规约**
   - Isabelle/HOL 重依赖证明在独立仓库 `airymaxos-proofs`（1.0.1 M2 阶段创建），避免将重依赖捆绑在测试子仓

2. **integration/ 7 子仓两两集成**: 按 `20-modules/README.md` §2 的依赖图组织，每条依赖关系对应一个集成测试目录。

3. **benchmark/regression/ 回归基准**: `baseline.json` 记录性能基线，每次提交对比，符合 ES-OLK-10 regression 零容忍。

---

## 第 11 章 跨子仓一致性约束（修正版）

### 11.1 [SC] 共享契约层单一数据源强制约束（NEW-P0-01 核心修正）

> **v0.2.1 严重违规**: §1.4 + §11.1 声明 [SC] 头文件仅物理宿主于 kernel，但 §5.2/§6.2/§7.2 又在 security/memory/cognition 子仓物理列出 [SC] 头文件，造成 3 个 [SC] 头文件两份物理副本（EV-08）。

6 个 [SC] 头文件**唯一物理宿主**在 `kernel/include/airymax/`，其他子仓**禁止**物理副本，必须通过 include path 引用：

| 引用方 | 引用方式 | 引用的 [SC] 头文件 |
|--------|---------|-------------------|
| security/ | `-I../kernel/include` | security_types.h |
| memory/ | `-I../kernel/include` | memory_types.h |
| cognition/ | `-I../kernel/include` | cognition_types.h |
| services/ | `-I../kernel/include` | ipc.h + sched.h |
| tests-linux/ | `-I../kernel/include` | 全部 6 个 [SC] 头文件（测试） |

**铁律**: 任何子仓的 `include/airymax/<sub>/` 目录下**禁止出现** [SC] 头文件名（security_types.h / memory_types.h / cognition_types.h / bpf_struct_ops.h / sched.h / ipc.h）。子仓内部头文件必须以 `_internal.h` 后缀命名区分。违反此约束的 CI 检查规则见 `08-compliance-checklist.md` STD-IRON-19。

### 11.2 8 子仓依赖层次定义（NEW-P2-04 修正）

v0.2.1 §11.5 引用"L2→L3→L4→L5→L6→L7"依赖层次但全文未定义。v0.2.3 首次明确定义：

| 层次 | 子仓 | 依赖关系 | 理由 |
|------|------|---------|------|
| **L2** | kernel | 依赖 L1（Linux 6.6 基线） | kernel 是最底层，[SC] 头文件唯一宿主 |
| **L3** | security / memory | 依赖 L2（kernel [SC] 头文件） | 安全/内存子系统引用 kernel [SC] 类型 |
| **L4** | cognition | 依赖 L2 + L3（kernel [SC] + security capability） | 认知子系统需 capability 授权 |
| **L5** | services | 依赖 L2 + L3 + L4（kernel [SC] + security + cognition） | daemons 调用安全/认知能力 |
| **L6** | system | 依赖 L2-L5（全部运行时子仓） | 系统级集成打包全部子仓 |
| **L7** | cloudnative / tests-linux | 依赖 L2-L6（全部子仓） | 云原生集成 + 测试聚合全部 |

**落地顺序**: L2（kernel）→ L3（security/memory）→ L4（cognition）→ L5（services）→ L6（system）→ L7（cloudnative/tests-linux）。1.0.1 M1 阶段按此层次逐步填充实现。

### 11.3 公共骨架一致性

8 子仓根目录公共文件（README/LICENSE/NOTICE/MAINTAINERS/CONTRIBUTING.md/.gitignore/.editorconfig）必须保持一致：
- **LICENSE**: 全部 AGPL-3.0+Apache-2.0 双许可证
- **MAINTAINERS**: 全部 R-03 落地，格式统一
- **CONTRIBUTING.md**: 全部引用 DCO + Signed-off-by + 审查流程
- **.editorconfig**: 全部对齐 OS-FMT-001（C Tab 8）/ OS-FMT-001（Rust 4 空格）/ OS-FMT-001（Python 4 空格）
- **rustfmt.toml**: 含 Rust 代码的子仓（cognition + cloudnative）必须有（NEW-P1-01）

### 11.4 分支策略一致性

8 子仓全部在 `feature/official-hubs-01` 分支开发，管理仓在 `main` 分支聚合。子仓不得创建未授权的 feature 分支，符合 `04-engineering-philosophy.md` §6 审查优先文化。

### 11.5 版本号一致性

8 子仓当前版本统一为 `0.1.1`（文档体系完成），1.0.1 开发阶段统一升级。子仓不得擅自升级版本号，符合 `20-modules/README.md` §6.1 版本号规则。

### 11.6 目录结构落地路线（NEW-P1-05 修正：统一 v0.2.2 §10.1 与 v0.2.1 §11.5）

> **修正**: v0.2.1 §11.5 称 R-01/R-02 在 M1 落地于 kernel/scripts/；v0.2.2 §10.1 称在 M0 落地于 include/。v0.2.3 统一为：R-01/R-02 在 **M1**（架构与模块设计完善阶段）落地，生成器在 kernel/scripts/，源文件在 include/。

| 阶段 | 时机 | 落地内容 | 落地位置 |
|------|------|---------|---------|
| 阶段 1 | 1.0.1 M1（架构与模块设计完善） | 8 子仓内部目录结构骨架创建（空目录 + .gitkeep） | 全部 8 子仓 |
| 阶段 2 | 1.0.1 M1 | R-01（syscall.xml）+ R-02（structures.bf）落地 | 生成器：`kernel/scripts/{syscall_gen.py,bitfield_gen.py}`；源文件：`kernel/include/uapi/airymax/syscall.xml` + `kernel/include/airymax/structures_{32,64}.bf` |
| 阶段 3 | 1.0.1 M5（开发流程与治理） | R-03（8 子仓 MAINTAINERS 文件）落地 | 全部 8 子仓根 MAINTAINERS |
| 阶段 4 | 1.0.1 M1-M5 | 各子仓按依赖层次（L2→L3→L4→L5→L6→L7，§11.2）逐步填充实现 | 按 §11.2 层次顺序 |

---

## 附录 A：双源映射对照表（修正版）

> **修正说明**: v0.2.1 附录 A 存在多处不准确（NEW-P1-04），v0.2.3 逐项修正。

| 子仓 | OLK-6.6 借鉴 | seL4 借鉴 | Airymax 同源 | v0.2.1 错误（已修正） |
|------|-------------|----------|-------------|---------------------|
| kernel | arch/{x86,arm64,riscv}/（26 子目录，EV-09）+ include/{uapi,linux,asm-generic} + Kbuild/Kconfig/Makefile 并存（EV-11）+ Documentation + scripts + MAINTAINERS + init/ + lib/ + io_uring/ + crypto/（顶层平级） | src/{api,kernel,object,fastpath} 极简（11 子目录，EV-01）+ src/machine/ 架构无关通用层（5 文件含 profiler.c，EV-03）+ arch/machine 通用+架构特定覆写模式 | atoms/corekern | seL4 src/ 声称 9 子目录（实际 11）；遗漏 init/lib/crypto；machine 误解为按架构分目录 |
| services | security/ 可插拔模式 | libsel4 服务化 + endpoint/notification IPC（src/object/endpoint.c） | daemons (12) | 无重大错误 |
| security | security/{selinux,landlock,apparmor} 每策略一目录 + LSM 钩子（security/bpf/）+ **不含 crypto/**（crypto 是顶层平级，EV-02） | capability 单一模型 + src/object/cnode.c 思想 | cupolas | v0.2.1 误置 crypto/ 于 security/crypto/（DIR-P0-03 修正） |
| memory | mm/ 单一子系统 + MGLRU 多代 LRU | src/kernel/boot.c + src/object/untyped.c（内存对象管理思想，**非"无"**） | heapstore + memoryrovol | v0.2.1 附录写 seL4 借鉴"无"，实际 seL4 有 boot.c/untyped.c（NEW-P1-04 修正）；提及"damon"但目录结构中无 damon/ 目录（本版删除 damon 引用） |
| cognition | kernel/sched kthread 模式 | 极简 kthread（ES-SEL4-1，src/kernel/thread.c） | coreloopthree + frameworks | 无重大错误 |
| cloudnative | tools/ 用户态工具 | libsel4 SDK 独立模型（ES-SEL4-9，四级 include，EV-06） | gateway + sdk | v0.2.1 遗漏 libsel4 四级 include 分层细节 |
| system | scripts/ + 配置管理 | 无（形式化约束不适用） | commons | 无重大错误 |
| tests-linux | tools/testing + kselftest | **seL4-master 仓库内无 proof/spec/capDL 目录**（EV-07），形式化证明在独立仓库，仅 .github/workflows/proof.yml 触发外部验证；借鉴"独立仓库 + CI 触发"实践 | 全模块测试 | v0.2.1 附录写 seL4 借鉴"proof/spec/capDL"，但 seL4-master 仓库内无这些目录（NEW-P1-04 修正） |

---

## 附录 B：规则编号映射

本设计涉及的 agentrt-linux 工程标准规则编号：

| 规则编号 | 含义 | 落地位置 |
|---------|------|---------|
| OS-IRON-001 | 用户空间 ABI 永久稳定 | include/uapi/airymax/ |
| OS-IRON-002 | 内核内部 API 不稳定 | include/airymax/（非 uapi） |
| OS-IRON-004 | 补丁自包含、中点可编译、支持 git bisect | kernel/patches/ |
| OS-KER-001 | goto 集中出口模式 + 分级标签 | 各 .c 实现 |
| OS-KER-002 | 禁止 #if 桩函数模式（对齐 IRON-1） | 全部 .c |
| OS-KER-003 | 条件编译必须用 IS_ENABLED() 宏 | 全部 .c |
| OS-FMT-001 | C Tab 8 / Rust 4 空格 / Python 4 空格 / TS 2 空格 | .clang-format / rustfmt.toml |
| OS-STD-008 | EXPORTed 函数必须有 kernel-doc | kernel/corekern/ |
| OS-STD-010 | typedef 严格限制（仅 5 种例外） | 全部 .c/.h |
| IRON-9 v2 [SC] | 6 头文件共享契约，单一物理宿主 | kernel/include/airymax/*.h（唯一） |
| STD-IRON-19 | [SC] 单一数据源 CI 检查（NEW-P0-01 衍生） | 08-compliance-checklist.md |

---

## 附录 C：v0.2.1 → v0.2.3 变更记录

### C.1 P0 严重问题修正（5 项）

| 编号 | 来源 | 问题 | v0.2.3 修正 | 证据 |
|------|------|------|------------|------|
| DIR-P0-01 | v0.2.2 | `machine/{x86,arm64,riscv}/` 误解 seL4 三层模型 | 改为 `machine/`（架构无关通用层，5 文件含 profiler.c）+ `arch/<arch>/machine/`（架构特定） | EV-03 |
| DIR-P0-02 | v0.2.2 | 顶层 `entry/` 偏离 OLK-6.6 | 删除顶层 entry/，移入 `arch/<arch>/entry/` | EV-09 |
| DIR-P0-03 | v0.2.2 | `crypto/` 误置于 `security/crypto/` | 提升至 kernel 顶层 `kernel/crypto/`（OLK-6.6 crypto/ 是顶层平级） | EV-02 |
| DIR-P0-04 | v0.2.2 | 顶层 `configs/` 偏离 OLK-6.6 | 移入 `arch/<arch>/configs/`（OLK-6.6 defconfig 在 arch/x86/configs/） | EV-09 |
| NEW-P0-01 | Phase 4 | [SC] 头文件单一数据源违规（3 个 [SC] 两份物理副本） | 删除 security/memory/cognition 子仓的 [SC] 物理副本，改为 `-I../kernel/include` 引用唯一宿主 | EV-08 |

### C.2 P1 重要问题修正（14 项）

| 编号 | 来源 | 问题 | v0.2.3 修正 |
|------|------|------|------------|
| DIR-P1-01 | v0.2.2 | kernel 缺失 `init/` | 新增 `kernel/init/`（main.c + do_initcalls.c + version.c） |
| DIR-P1-02 | v0.2.2 | kernel 缺失 `lib/` | 新增 `kernel/lib/`（string.c + ctype.c + bitmap.c + radix-tree.c） |
| DIR-P1-03 | v0.2.2 | `corekern/` 子目录不全 | 新增 `corekern/{api,object,locking,irq}/`（对应 seL4 src/api + src/object + OLK-6.6 kernel/{locking,irq}） |
| DIR-P1-04 | v0.2.2 | `corekern/memory/` 与 memory 子仓边界冲突 | `corekern/memory/` 仅留 `page_alloc.h` 接口，实现移入 memory 子仓 |
| DIR-P1-05 | v0.2.2 | seL4 `src/object/` 内核对象模型未体现 | 新增 `corekern/object/`（cnode.c + tcb.c + endpoint.c + notification.c） |
| DIR-P1-06 | v0.2.2 | `syscall.xml`/`structures.bf` 源文件位置未指定 | syscall.xml → `include/uapi/airymax/`；structures_{32,64}.bf → `include/airymax/`（修正 v0.2.2 .bf 描述：25 文件 7 层，非单一 structures.bf，EV-05） |
| DIR-P1-07 | v0.2.2 | `bpf/` 顶层偏离 OLK-6.6 | 移入 `corekern/bpf/`（OLK-6.6 在 kernel/bpf/，非顶层） |
| DIR-P1-08 | v0.2.2 | `formal-verification/` 未说明 seL4 独立仓库实践 | 新增 `formal-verification/README.md` 说明 seL4 证明在独立仓库（EV-07） |
| NEW-P1-01 | Phase 4 | cloudnative/ 缺 rustfmt.toml | 新增 `cloudnative/rustfmt.toml` |
| NEW-P1-02 | Phase 4 | memory/vfs-persist/ 与 services/userland-vfs/ 边界冲突 | memory/vfs-persist/ 重命名为 `vfs-persist-kern/`，明确内核态持久化后端接口边界 |
| NEW-P1-03 | Phase 4 | formal-verification/ Isabelle/HOL 重依赖捆绑在测试子仓 | 说明重依赖证明在独立仓库 airymaxos-proofs（M2 创建） |
| NEW-P1-04 | Phase 4 | 附录 A 双源映射对照表多处不准确 | 逐项修正（memory seL4 借鉴"无"→"boot.c/untyped.c"；删除 damon 引用；tests seL4 借鉴"proof/spec/capDL"→"独立仓库实践"） |
| NEW-P1-05 | Phase 4 | §11.5 与 v0.2.2 §10.1 落地路线冲突 | 统一为 M1 落地，生成器在 kernel/scripts/，源文件在 include/ |
| NEW-P1-06 | Phase 4 | kernel/patches/microkernel/ 与子仓内容重叠 | patches/ 定位为"对上游 Linux 内核的修改 diff"，实现代码在对应子仓 |

### C.3 P2 改进建议（10 项）

| 编号 | 来源 | 问题 | v0.2.3 修正 |
|------|------|------|------------|
| DIR-P2-01 | v0.2.2 | `patches/` 顶层目录需明确定位 | 明确为"上游内核修改 diff"，补丁修改功能实现在对应子仓 |
| DIR-P2-02 | v0.2.2 | Kbuild→Makefile 过度简化 | 修正为 Kbuild + Makefile 并存（EV-11：OLK-6.6 顶层 Kbuild 2573B + Makefile 68KB） |
| DIR-P2-03 | v0.2.2 | tests 边界不清 | kernel/tests/ 仅 kernel 自身测试；tests-linux/integration/ 跨子仓集成 |
| DIR-P2-04 | v0.2.2 | src/api 概念未映射 | `corekern/api/` 对应 seL4 src/api/（syscall 分发） |
| DIR-P2-05 | v0.2.2 | include/linux 映射未说明 | OLK-6.6 include/linux/ → agentrt-linux include/airymax/（等价映射） |
| DIR-P2-06 | v0.2.2 | tools/dts 缺失 | 新增 `kernel/scripts/dts/`（seL4 tools/dts/ 各平台 .dts） |
| NEW-P2-01 | Phase 4 | cognition/embodied-ai + gpu-npu 范围问题 | embodied-ai→embodied-io（I/O 通道）；gpu-npu→compute-accel（算力加速调度） |
| NEW-P2-02 | Phase 4 | super-node 命名重叠 | cognition/super-node-sandbox→super-node-cog-snapshot（认知态快照） |
| NEW-P2-03 | Phase 4 | services/systemd 与 system/config/systemd 职责重叠 | 明确：services/systemd/ = daemon unit 文件；system/config/systemd/ = 守护进程自身配置 |
| NEW-P2-04 | Phase 4 | L2-L7 依赖层次未定义 | §11.2 首次明确定义 6 层依赖（L2 kernel → L3 security/memory → L4 cognition → L5 services → L6 system → L7 cloudnative/tests-linux） |

### C.4 v0.2.2 报告自身缺陷纠正（9 处）

| 编号 | v0.2.2 缺陷 | v0.2.3 纠正 | 证据 |
|------|------------|------------|------|
| V22-DEF-01 | §3.2 src/ 测绘遗漏 model/ 和 plat/（声称 9，实际 11） | 修正为 11 个子目录 | EV-01 |
| V22-DEF-02 | §5.1 修复方案遗漏 profiler.c | machine/ 补全 profiler.c | EV-03 |
| V22-DEF-03 | §3.4 .bf 分布严重简化（"三处"） | 修正为 25 文件 7 层精确分布 | EV-05 |
| V22-DEF-04 | §3.3 plat/ 评估偏松（"方向正确"） | 修正为 seL4 实际 42 平台扁平结构；v0.2.3 删除顶层 plat/，用 scripts/dts/ + arch/ 替代 | EV-04 |
| V22-DEF-05 | 遗漏子架构 32/64/armv 拆分模式 | 附录说明 seL4 arch/{arm,x86}/ 含 32/64 子目录 + arm/armv/ 变体 | seL4 src/arch/ |
| V22-DEF-06 | 遗漏 libsel4 四级 include 分层 | 附录 A cloudnative seL4 借鉴补全四级 include 细节 | EV-06 |
| V22-DEF-07 | §2.1 OLK-6.6 顶层遗漏 ipc/rust/LICENSES（声称 21，实际 24） | 修正为 24 个目录 | EV-02 |
| V22-DEF-08 | §2.2 arch/x86/ 严重简化（声称 ~6，实际 26） | §3.2 补全 arch/x86/ 26 子目录 | EV-09 |
| V22-DEF-09 | §3.5 自我纠错（先提 syscall_generator.py 再注"实际无"） | 修正：seL4 实际用 invocation_header_gen.py 处理 syscall.xml，无独立 syscall_generator.py | seL4 tools/ |

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
