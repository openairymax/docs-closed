SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# sw_64 架构 OBS 远程构建方案（AirymaxOS:Factory:Kernel）

> **保密级别**: SPHARX Ltd 内部参考，**闭源不公开**
> **版本**: 1.0.0
> **最后更新**: 2026-08-01
> **适用范围**: AirymaxOS 发布工程组 + 内核开发组 + 构建工程组
> **前置文档**: [12-build-and-flash-strategy.md](12-build-and-flash-strategy.md)（编译与烧录策略）、[11-layer-feasibility-study.md](11-layer-feasibility-study.md)（LAYER 方案可行性论证）

---

## 0. 方案概述

AirymaxOS 内核（ALK，仓库分支 `ALK-6.6-dev`）在 v3.6 评审后遗留一项 ⚠️：`arch/sw_64/`（366 文件）自 openEuler OLK-6.6 LAYER 导入后，其 defconfig **从未被实际编译验证**（详见 [12-build-and-flash-strategy.md §11.6](12-build-and-flash-strategy.md) 后续工作 #1、§8 风险 #6）。根因是本机与 CI 环境对 sw_64 均不可构建——mainline qemu 8.2.2 与 openEuler qemu 8.2.0 均不支持 sw_64 仿真、openEuler repo 无 sw_64 交叉 gcc 包、docker.io 不可达（详见 §1.2）。

本方案落地 **OBS（Open Build Service）远程构建**，在 OBS 项目 `AirymaxOS:Factory:Kernel` 下定义 sw_64 的完整构建链，借助 OBS 后端（openEuler 官方 OBS 或自建实例）的 sw_64 构建能力绕过 qemu 仿真缺失，使 sw_64 首次进入可验证的构建通道：

```
sw_64 构建链 = AirymaxOS:Factory:Kernel（OBS 项目，§2）
             + _service（git 拉取 ALK-6.6-dev 源码 + quilt 补丁，§3）
             + prjconf（sw_64 宏 + toolchain 依赖，§4）
             + airy-kernel.spec（%ifarch sw_64 / merge_config 合入，§5 §6）
             + osc build --arch=sw_64 远程构建（§7）
             + 静态验证（vmlinux 符号 / modinfo / objdump，§7.4）
```

**诚实边界**（§7.5、§10）：OBS 远程构建只能消除"无法编译验证"这一 ⚠️ 项；**运行态验证**（启动、驱动加载、微内核化改造行为）仍依赖原生申威硬件或未来 qemu 上游支持，本方案不虚报该能力。

---

## 1. 问题陈述与目标

### 1.1 问题陈述

sw_64（申威架构）是 AirymaxOS 目标硬件架构之一。`arch/sw_64/`（366 文件）已按 LAYER 直接导入轨从 OLK-6.6 整体导入（[11-layer-feasibility-study.md §2.3](11-layer-feasibility-study.md)），并落地 `arch/sw_64/configs/airy_defconfig`（695 行）与 `configs/euler_hw_sw64.config`（634 行）（[12-build-and-flash-strategy.md §11.1](12-build-and-flash-strategy.md)）。但自导入以来，sw_64 仅完成了**配置生成**验证（`make ARCH=sw_64 airy_defconfig` 产出 3851 行 `.config`，`CONFIG_SW64=y`、`CONFIG_SECURITY_AIRY=y`，见 [12-build-and-flash-strategy.md §11.3](12-build-and-flash-strategy.md)），**完整 `make` 编译从未执行**——架构代码的编译正确性处于未验证状态。

### 1.2 四个阻塞点（已核验）

| # | 阻塞点 | 现状（已核验） | 影响 |
|---|--------|---------------|------|
| 1 | mainline qemu 8.2.2 不支持 sw_64 仿真 | 上游 qemu 无 `qemu-system-sw_64`，亦无 sw_64 user-mode | 本机无法 `qemu-system` 启动 sw_64，CI 无法用 qemu-user 辅助交叉构建 |
| 2 | openEuler qemu 8.2.0 也不支持 sw_64 仿真 | openEuler 24.03 LTS 的 qemu 包未携带 sw_64 target | 复用 openEuler qemu 路径同样不可行 |
| 3 | openEuler 官方 repo 无 sw_64 交叉 gcc 包 | openEuler 仓库仅提供 sw_64 **原生** gcc（运行于申威主机），无交叉编译包 | x86/arm64 主机无法本地交叉编译 sw_64 内核 |
| 4 | docker.io 不可达 | 构建环境无法拉取第三方 sw_64 交叉构建镜像 | 无法用 docker 容器化交叉构建 |

**前提条件**（本方案的第一性前提）：**本机无 sw_64 工具链**——既无原生 gcc（无申威硬件），也无交叉 gcc（openEuler repo 未提供），更无 qemu 仿真可用。任何声称"在本机构建 sw_64"的方案都必须先破除上述 4 个阻塞点。

### 1.3 方案对比与选型

| 方案 | 可行性 | 结论 |
|------|--------|------|
| 本地 qemu-system 仿真 | ❌ mainline/openEuler qemu 均无 sw_64 target | 阻塞点 #1/#2 |
| 本地 qemu-user 交叉构建 | ❌ 无 sw_64 user-mode | 阻塞点 #1/#2 |
| docker 容器交叉构建 | ❌ docker.io 不可达 + 无 sw_64 交叉 gcc | 阻塞点 #3/#4 |
| 本机 x86 交叉编译 | ❌ openEuler repo 无 `gcc-cross-sw_64` 类交叉包 | 阻塞点 #3 |
| **OBS 远程构建（后端 sw_64 能力）** | ✅ OBS 后端（openEuler 官方 OBS 或自建实例）具备 sw_64 架构构建支持，工具链由 sw_64 repository 解析提供 | **本方案** |
| 原生 sw_64 硬件直连 make | ✅ 但需独立申威服务器/工控机 | 回退方案（§7.6、§10.2） |

**选型理由**：OBS 是 openEuler（以及 openSUSE/SUSE）官方使用的构建系统，其后端已具备 sw_64 架构的构建能力（构建环境、工具链解析、worker 调度均为现成基础设施）。OBS 已在 [12-build-and-flash-strategy.md §3.2](12-build-and-flash-strategy.md) 被选定为 AirymaxOS 的 CI/CD 构建基础设施，本方案在既有体系内补齐 sw_64 通道，**零新增工具链**，与"全面复用 openEuler 构建体系、不 fork"原则（[12-build-and-flash-strategy.md §0](12-build-and-flash-strategy.md)）一致。

### 1.4 目标与消除标准

| # | 目标 | 完成判据 |
|---|------|---------|
| G1 | sw_64 完整编译进入可验证通道 | OBS `AirymaxOS:Factory:Kernel` `standard_sw_64` 仓库构建状态 `succeeded`，产出 5 个 RPM（kernel/devel/headers/modules/debuginfo） |
| G2 | 编译产物可被静态验证 | 从 RPM 提取 vmlinux/模块，完成 strings/modinfo/kallsyms/objdump 检查（§7.4） |
| G3 | 构建可重复触发与回滚 | CI 联动 sync-euler-drivers.sh E4/E5（§8），失败可回退到上次成功构建 |
| G4 | v3.6 ⚠️ 项闭合 | sw_64 从"仅配置生成"升级为"完整编译 + 静态验证"，证据归档（§7.5） |

---

## 2. OBS 架构与项目设计

### 2.1 项目层次设计

OBS 项目采用两级结构：`AirymaxOS:Factory`（主线滚动）→ `AirymaxOS:Factory:Kernel`（内核专项，本方案落地对象）。内核专项单独成项目，理由：内核构建链（toolchain、KABI 校验、debuginfo）与普通包差异大，隔离便于独立滚动与回滚。

| OBS 项目 | 定位 | 构建目标 | 滚动策略 |
|---------|------|---------|---------|
| `AirymaxOS:Factory` | 主线滚动构建（全包） | x86_64 / aarch64 / sw_64 | 持续滚动 |
| `AirymaxOS:Factory:Kernel` | **内核专项滚动构建（本方案）** | 上述三架构 + kernel-devel / kernel-debuginfo | 跟随 ALK-6.6-dev 提交触发（§8） |
| `AirymaxOS:1.0:Kernel` | 1.0 发布版稳定构建（后续派生） | 同上 | 从 Factory 分支锁定 |

**层级关系**：`Factory` 为滚动基线，验证通过后经 OBS project link / branch 机制派生 `:1.0` 稳定版。本方案先落地 `Factory:Kernel`，稳定版派生在 1.0 发布阶段执行。

### 2.2 包名与项目元数据

包名：`airy-kernel`（与 [12-build-and-flash-strategy.md §1.2](12-build-and-flash-strategy.md) 的改名规则一致：`kernel` → `airy-kernel`）。项目元数据（`osc meta prj AirymaxOS:Factory:Kernel --edit` 写入）：

```xml
<project name="AirymaxOS:Factory:Kernel">
  <title>AirymaxOS Kernel Factory (ALK-6.6-dev)</title>
  <description>
    Kernel-only rolling builds for AirymaxOS 1.x.
    Covers x86_64 / aarch64 / sw_64 with the airy-kernel 5-package split.
  </description>
  <person userid="build-robot" role="maintainer"/>
  <repository name="standard_sw_64">
    <path project="openEuler:Main" repository="standard_sw_64"/>
    <arch>sw_64</arch>
  </repository>
  <repository name="standard_x86_64">
    <path project="openEuler:Main" repository="standard_x86_64"/>
    <arch>x86_64</arch>
  </repository>
  <repository name="standard_aarch64">
    <path project="openEuler:Main" repository="standard_aarch64"/>
    <arch>aarch64</arch>
  </repository>
</project>
```

### 2.3 sw_64 repository 设计

- **repository 名**：`standard_sw_64`（对齐 openEuler `standard_sw_64` 命名习惯，`osc build` 时以 `--repository=standard_sw_64 --arch=sw_64` 指定）。
- **path 依赖**：`<path project="openEuler:Main" repository="standard_sw_64"/>` —— sw_64 的工具链（gcc/binutils/glibc/make/bc/flex/bison 等）与构建依赖全部从 openEuler 官方仓库路径解析，AirymaxOS 项目内**不重复维护**申威工具链。这是"不 fork openEuler 构建体系"的直接体现（[12-build-and-flash-strategy.md §0](12-build-and-flash-strategy.md)）。
- **架构约束**：sw_64 仓库的 `<arch>sw_64</arch>` 使 OBS scheduler 只派发到支持 sw_64 的构建环境（openEuler OBS 后端为 sw_64 配置了构建环境/worker；若为自建实例则需在服务器端注册 sw_64 架构支持，见 §2.4）。

### 2.4 与 openEuler 官方 OBS / 自建 OBS 的关系

| 维度 | openEuler 官方 OBS（build.openeuler.org） | 自建 OBS 实例（openSUSE OBS 开源部署） |
|------|------------------------------------------|----------------------------------------|
| 定位 | openEuler 社区官方构建 | AirymaxOS 内部构建 |
| 优点 | 零运维；sw_64 架构支持现成 | 完全自主（项目可见性/签名/token 可控）；与内部 dnf 仓库无缝集成 |
| 缺点 | 需在社区申请项目；内部仓库源码需公开或走私有认证 | 需自行部署并配置 sw_64 构建环境（工作量预估：1-2 人周） |
| sw_64 toolchain | 现成（openEuler:Main standard_sw_64） | 同左（path 依赖 openEuler:Main，或镜像其仓库） |

**建议路径**：初期评估 openEuler 官方 OBS 可行性（成本最低）；若因闭源约束（ALK 源码含内部微内核化改造，不愿提交社区）受阻，则部署自建 OBS 实例。两者对本方案的 `_service`/`prjconf`/`spec` 配置完全通用，仅服务器地址与认证方式不同。

> **TODO(待核验)**：OBS 服务器 API 端点（`https://build.openeuler.org` 或自建实例地址）与 AirymaxOS 的 OBS 账号/token 尚未申请，落地时以实际为准，并写入 `~/.config/osc/oscrc` 的 apiurl 配置。

**访问与分发策略**：
- 项目可见性：内部项目（`access protected`），仅构建工程组成员可读；写入需 maintainer 权限。
- 触发认证：CI 通过 `osc` 命令提交时携带 OBS API token（scope 限 `AirymaxOS:Factory:Kernel`），token 存入 CI secret，不落仓库明文。
- 产物分发：构建产物 RPM 经内部 dnf 仓库 `/airymax-os/` 树的 `sw_64/` 子目录分发（[12-build-and-flash-strategy.md §3.1](12-build-and-flash-strategy.md)）。

---

## 3. _service 文件配置

`_service` 定义 OBS 如何从 ALK-6.6-dev git 仓库拉取源码与补丁。放在 `AirymaxOS:Factory:Kernel` 项目的 `airy-kernel` 包目录下。

### 3.1 完整 _service 示例

```xml
<services>
  <!-- 1. 从 ALK-6.6-dev 分支拉取内核源码 tarball（全量，含 arch/sw_64/ 与 patches/hw-vendor/） -->
  <service name="tar_scm">
    <param name="scm">git</param>
    <param name="url"><!-- TODO(待核验): ALK-6.6-dev 仓库地址，例如 https://gitee.example.com/airymax/agent-linux.git（私有仓库用 ssh + deploy key） --></param>
    <param name="revision">ALK-6.6-dev</param>
    <param name="filename">airy-kernel</param>
    <!-- 版本号：6.6.0 对齐 openEuler kernel-6.6.0-145 段（见 11-layer-feasibility-study.md §1.3）；
         @TAG_OFFSET@ 为距最近 tag 的提交数，%ct 提交时间戳，%h 短 hash -->
    <param name="versionformat">6.6.0.@TAG_OFFSET@.%ct.%h</param>
    <!-- ALK 无 git submodule，禁用递归以加速 -->
    <param name="submodules">disable</param>
  </service>

  <!-- 2. 提取 quilt 补丁系列（patches/hw-vendor/，双轨制 quilt 轨）：
         若 tar_scm 已全量拉取（仓库内含该目录），此步可省略；
         若补丁独立于源码仓库维护，则用 extract_file 按需提取 -->
  <service name="extract_file">
    <param name="url"><!-- TODO(待核验): 同上仓库地址 --></param>
    <param name="scm">git</param>
    <param name="revision">ALK-6.6-dev</param>
    <param name="file">patches/hw-vendor/series</param>
  </service>
  <service name="extract_file">
    <param name="url"><!-- TODO(待核验): 同上仓库地址 --></param>
    <param name="scm">git</param>
    <param name="revision">ALK-6.6-dev</param>
    <param name="file">patches/hw-vendor/*.patch</param>
  </service>

  <!-- 3. 重新压缩为 .tar.gz，供 spec Source0 引用（与 openEuler kernel.spec 格式一致） -->
  <service name="recompress">
    <param name="file">*.tar</param>
    <param name="compression">gz</param>
  </service>

  <!-- 4. 将 tarball 名中的版本号写入 spec 的 Version: 字段 -->
  <service name="set_version">
    <param name="basename">airy-kernel</param>
  </service>
</services>
```

### 3.2 服务链说明

| 服务 | 作用 | 说明 |
|------|------|------|
| `tar_scm`（scm=git） | 从 git 拉取源码 tarball | 主服务；`revision=ALK-6.6-dev` 锁定分支；私有仓库用 ssh + deploy key |
| `extract_file` | 从 git 单独提取文件 | 用于 **quilt 补丁独立维护** 场景：提取 `patches/hw-vendor/series` 与 `*.patch`；若补丁已随源码全量拉取则删除本服务 |
| `recompress` | 重压为 `.tar.gz` | `Source0: airy-kernel_%{version}.tar.gz` 引用 |
| `set_version` | 版本注入 | 将 tarball 名中版本写入 spec `Version:`，保证 spec 与源码版本一致 |

> **注意**：`extract_file` 的 `*.patch` 通配符支持取决于 OBS 服务版本，落地时若实例不支持通配符，改用逐文件 `file` 参数列出（patch 数量有限）。`obs_scm`/`download_files` 为 tar_scm 的等价替代（obs_scm 支持更多 SCM 后端、download_files 面向二进制源），本方案默认 tar_scm 即可满足。

### 3.3 kernel 源码包 + quilt 补丁的处理约定

- **源码包**：`tar_scm` 全量拉取 ALK-6.6-dev（含 `arch/sw_64/`、`configs/`、`patches/hw-vendor/`）。ALK 内核仓库即 agent-linux 内核源码树，不含 build/docs 等管理仓内容，全量拉取即为内核源码包。
- **quilt 补丁（双轨制 quilt 轨）**：`patches/hw-vendor/` 下以 `NNNN-<hash>.patch` + `series` 文件组织（sync-euler-drivers.sh E3 Track 2 产出，见 §8.1）。OBS 构建时补丁的应用在 spec 的 `%prep` 区完成（§6.2）：`%patch` 逐条应用，或 `quilt push -a` 按 series 批量应用。sw_64 属**直接导入轨**（[11-layer-feasibility-study.md §2.3](11-layer-feasibility-study.md)），`arch/sw_64/` 不经过 quilt，quilt 补丁仅覆盖 `drivers/` 重叠区。
- **版本一致性**：`set_version` 注入的 `%{version}` 与 spec `Release: airy.1%{?dist}` 组合为 RPM 版本，与内核源码 `Makefile` 的 `VERSION=6/PATCHLEVEL=6/SUBLEVEL=0` 解耦（借鉴 openEuler `Makefile.oever` 的发行版版本解耦思想，见 §6.1）。

---

## 4. prjconf 配置

prjconf 是 OBS 项目级构建配置，定义目标架构宏、toolchain 依赖与构建约束。通过 `osc meta prjconf AirymaxOS:Factory:Kernel --edit` 写入。

### 4.1 完整 prjconf 示例

```text
# ====================================================================
# AirymaxOS:Factory:Kernel prjconf
# Target: sw_64 (Sunway) — repository standard_sw_64
# 构建模式：OBS 后端 sw_64 构建环境（无 qemu 仿真，见 §1.2 阻塞点 #1/#2）
# ====================================================================

# --- 架构宏 --------------------------------------------------------
%define _target_platform sw_64-oe-linux
%define _target_cpu sw_64
%define airy_arch sw_64
%define airy_kernel_flavor default

# --- toolchain 与构建依赖（sw_64 由 openEuler:Main standard_sw_64 path 解析） ---
Preinstall: gcc binutils glibc glibc-common bash coreutils util-linux
Preinstall: rpm-build make sed grep gawk tar gzip findutils diffutils
# 构建依赖最小集（BuildRequires 解析前强制安装；完整清单见 §5.3）
Require: gcc binutils make bc flex bison openssl-devel
Require: elfutils-libelf-devel dwarves perl python3
# 支持包（可用但不强制）
Support: gcc-c++ pahole

# --- AirymaxOS 宏定义（供 spec / Kbuild 引用） -----------------------
Macros:
# 发行版版本注入（借鉴 openEuler Makefile.oever 构建时外部注入模式，见 §6.1）
%oemver_lts 1
%oemver_major 0
%oemver_minor 0
%airy_arch sw_64
%airy_defconfig airy_defconfig
# KABI 检查关闭（LAYER 已剥离 __KABI 标记，见 12-build-and-flash-strategy.md §1.1/§11.3）
%kabi_check 0
:Macros

# --- 构建约束 ------------------------------------------------------
# 禁用 qemu 仿真回退：sw_64 无 qemu target，必须使用后端 sw_64 构建环境
BuildFlags: emulator:none
# 以下标志在 openEuler OBS 上的等价语义：仓库 <arch>sw_64</arch> 已约束派发
# （自建实例若支持 worker 过滤，可追加：BuildFlags: nativebuild）
```

### 4.2 配置项说明

| 配置项 | 作用 | 为何如此 |
|--------|------|---------|
| `%define _target_platform sw_64-oe-linux` | 锁定目标 ABI | openEuler sw_64 的标准 toolchain triple，与 openEuler:Main 的 sw_64 包二进制兼容 |
| `%define _target_cpu sw_64` | 架构标识 | 供 spec `%ifarch sw_64` 判定与 Kbuild 引用 |
| `Preinstall` / `Require` | 预装与强制构建依赖 | sw_64 构建环境中 gcc/binutils 由 openEuler:Main path 解析，无需交叉包前缀（原生 gcc） |
| `%oemver_lts/major/minor` | 发行版版本注入 | 借鉴 `Makefile.oever` 占位 + 构建时注入模式（来源：`agent-linux/00-reviews/_review_v3.6/21-openEuler-engineering-standards-v3.6c.md` §9：顶层 Makefile L1252 `include $(srctree)/Makefile.oever`、L1279-1284 生成 version.h；`Makefile.oever` 5 行占位值 `OPENEULER_LTS=0/MAJOR=9999/MINOR=0`，构建时外部注入） |
| `%kabi_check 0` | 禁用 KABI 检查 | LAYER 导入已剥离 `__KABI` 标记（[12-build-and-flash-strategy.md §11.3](12-build-and-flash-strategy.md) 验证 `grep -r '__KABI' arch/sw_64/ configs/` 零命中） |
| `BuildFlags: emulator:none` | 禁用 qemu 回退 | sw_64 无 qemu 仿真（§1.2 阻塞点 #1/#2）；标志名以 OBS 实例版本为准，等价替代：不在 repository meta 声明 emulator 并仅声明 `<arch>sw_64</arch>` |

### 4.3 sw_64 交叉工具链包依赖（方法论 + 占位）

**关键事实**：openEuler 官方 repo 不提供 sw_64 交叉 gcc 包（阻塞点 #3，已核验）。OBS 侧 sw_64 构建因此有两种可能形态，prjconf 的依赖声明随之不同：

| 形态 | 工具链形态 | prjconf 依赖声明 | 状态 |
|------|-----------|-----------------|------|
| A：后端原生 sw_64 构建环境 | sw_64 原生 gcc/binutils/glibc（来自 openEuler:Main standard_sw_64） | `Require: gcc binutils ...`（无交叉前缀） | **本方案默认** |
| B：x86 worker + 交叉工具链 | 交叉 gcc 包（命名类推 openEuler 的 `gcc-cross-s390x` 等交叉包体系） | `Require: gcc-cross-sw_64` 等 | **TODO(待核验)** |

**方法论**（形态 B 无法回避时使用）：从 openEuler sw_64 repository 的**构建依赖解析**获取确切包名，不猜测：

```bash
# 在 OBS 上查询 openEuler:Main standard_sw_64 中某个内核包的构建环境依赖
osc buildinfo openEuler:Main kernel standard_sw_64 sw_64 \
    | grep -E 'gcc|binutils|bc|bison' | sort -u
# 或在自建实例上登录 sw_64 构建机后：
rpm -q --whatprovides gcc; rpm -qa | grep -E '^(gcc|binutils|glibc)'
```

> **TODO(待核验)**：若走形态 B，sw_64 交叉 gcc 的确切包名（占位名 `gcc-cross-sw_64`）需以上述 buildinfo 解析结果为准；openEuler 交叉包实际命名（如 `gcc-cross-<arch>` 变体）以 `osc search gcc-cross` 结果为准，本方案不编造包名。当前判断以形态 A（openEuler OBS 后端原生 sw_64 构建环境）为主路径。

---

## 5. 构建依赖与 sw_64 交叉工具链

### 5.1 工具链来源与解析

OBS 侧 sw_64 构建的完整工具链（gcc / binutils / glibc / make / bc / flex / bison / openssl 等）由 **openEuler 官方 repo 的 sw_64 仓库**（path 依赖 `openEuler:Main standard_sw_64`）解析提供。`osc build` 时通过 `--arch=sw_64` 与 repository 配置（§2.3）让 OBS 自动解析：

```bash
# 本地调试模式（可选）：利用 OBS 后端能力构建，本地仅提交与查看日志
osc build standard_sw_64 sw_64 airy-kernel.spec --no-init
# 常规远程构建（推荐，见 §7.2）：osc commit 后在 OBS 后端调度
```

**本机无需任何 sw_64 工具链**——构建全部发生在 OBS 后端，本机仅需安装 `osc` 客户端与 OBS API token。

### 5.2 原生 vs 交叉（对包名的影响）

- **形态 A（默认，原生 sw_64 构建环境）**：构建环境内 `gcc` 即 sw_64 原生编译器，spec 与 prjconf 中**不需要** `gcc-cross-*` 交叉包，直接 `BuildRequires: gcc`。
- **形态 B（x86 worker + 交叉）**：需要交叉包，包名与 ABI 前缀（如 `--target=sw_64-oe-linux`）以 §4.3 方法论解析为准（**TODO(待核验)**）。

### 5.3 kernel spec 的 BuildRequires 清单

对齐 openEuler kernel 构建模式（x86/arm64 相同的依赖集，sw_64 无差异项）：

```spec
Name:           airy-kernel
Version:        6.6.0
Release:        airy.1%{?dist}
Summary:        AirymaxOS kernel (ALK-6.6-dev)
License:        GPL-2.0-only
URL:            TODO(待核验): 内部源码仓库地址
Source0:        airy-kernel_%{version}.tar.gz

# --- 编译工具链 ---
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  bc
BuildRequires:  flex
BuildRequires:  bison
BuildRequires:  perl
BuildRequires:  python3

# --- 内核构建依赖 ---
BuildRequires:  openssl-devel
BuildRequires:  elfutils-libelf-devel
BuildRequires:  elfutils-devel
BuildRequires:  dwarves
BuildRequires:  pahole
BuildRequires:  binutils-devel
BuildRequires:  diffutils

# --- 架构声明（本 spec 单包面向三架构，sw_64 由 %ifarch 分支处理） ---
# （若独立 sw_64 spec，则改用：ExclusiveArch: sw_64）
```

> 说明：与 [12-build-and-flash-strategy.md §1.2](12-build-and-flash-strategy.md) 一致，`airy-kernel.spec` 复用 openEuler `kernel.spec` 的 5 包拆分（kernel/devel/headers/modules/debuginfo），BuildRequires 集合覆盖内核完整构建（含模块签名与 BTF 生成所需的 dwarves/pahole）。

---

## 6. kernel spec 模板要点

### 6.1 发行版版本号与内核 VERSION 解耦（借鉴 Makefile.oever）

openEuler 将发行版版本号与内核 `VERSION/PATCHLEVEL/SUBLEVEL` 解耦：源码树内 `Makefile.oever` 为占位值（`OPENEULER_LTS=0/OPENEULER_MAJOR=9999/OPENEULER_MINOR=0`），由构建系统在构建时外部注入；顶层 Makefile L1252 `include $(srctree)/Makefile.oever`、L1279-1284 将注入值生成进 `version.h`（来源：`agent-linux/00-reviews/_review_v3.6/21-openEuler-engineering-standards-v3.6c.md` §9）。

AirymaxOS 对应实现（不改内核源码，在 spec 侧完成）：

```spec
# --- 发行版版本注入（对应 prjconf Macros %oemver_*） ---
%{!?oemver_lts:%define oemver_lts 1}
%{!?oemver_major:%define oemver_major 0}
%{!?oemver_minor:%define oemver_minor 0}
%define oemver %{oemver_lts}.%{oemver_major}.%{oemver_minor}

%build
# 构建前将发行版版本注入环境（供 scripts/setlocalversion / Kbuild 消费），
# 内核源码树保持 vanilla VERSION=6.6.0 不变（IRON-7 基线纯净性）
export OPENEULER_LTS=%{oemver_lts} OPENEULER_MAJOR=%{oemver_major} OPENEULER_MINOR=%{oemver_minor}
```

> 若 ALK 源码树未 include `Makefile.oever`（LAYER 已排除该文件，[11-layer-feasibility-study.md §1.1](11-layer-feasibility-study.md) 构建系统隔离），则注入点为 `scripts/setlocalversion` 的 `scm-version` 或 spec `%{?dist}` 即可，具体注入路径在落地时核对 ALK 树的 version 生成链（**TODO(待核验)**）。

### 6.2 %ifarch 分支与 quilt 补丁应用（%prep）

```spec
%prep
%setup -q -n airy-kernel-%{version}
# 应用 LAYER quilt 补丁（drivers/ 重叠区；sw_64 直接导入轨无补丁）
%if 0%{?with_quilt}
quilt push -a
%else
%patch -P1   # 或逐条 %patch1 / %patch2 ...（对应 patches/hw-vendor/series 顺序）
%endif

# 架构分支变量（三架构共用一份 spec）
%ifarch sw_64
%define build_arch     sw_64
%define build_defconfig airy_defconfig
%define kernel_image    arch/sw_64/boot/vmlinuz
%endif
%ifarch x86_64
%define build_arch     x86_64
%define build_defconfig airy_defconfig
%define kernel_image    arch/x86/boot/bzImage
%endif
%ifarch aarch64
%define build_arch     aarch64
%define build_defconfig airy_defconfig
%define kernel_image    arch/arm64/boot/Image
%endif
```

### 6.3 defconfig 合入流程（merge_config.sh → airy_defconfig）

`airy_defconfig` 的生成遵循 [12-build-and-flash-strategy.md §1.1](12-build-and-flash-strategy.md) 的合并顺序（底座 → 硬件碎片 → agent），用内核官方 `scripts/kconfig/merge_config.sh` 完成。sw_64 已固化 695 行 `arch/sw_64/configs/airy_defconfig`（[12-build-and-flash-strategy.md §11.1](12-build-and-flash-strategy.md) 产物 #2），**构建期优先直接使用固化文件**；若需重新生成（如硬件碎片更新），在构建期动态合入：

```spec
%build
%ifarch sw_64
# 方式一（默认）：使用仓库已固化的 airy_defconfig
make ARCH=%{build_arch} %{build_defconfig}

# 方式二（硬件碎片更新时动态合入，产出与固化文件一致性由 E5 校验）：
# ./scripts/kconfig/merge_config.sh \
#     arch/sw_64/configs/openeuler_defconfig \
#     configs/euler_hw_sw64.config \
#     configs/defconfig-agent \
#     -O %{_builddir}/build-sw_64
# make ARCH=sw_64 O=%{_builddir}/build-sw_64 -j$(nproc)
%endif
```

**合入语义**：`openeuler_defconfig`（底座，硬件兼容基线）→ `euler_hw_sw64.config`（硬件碎片，634 行）→ `defconfig-agent`（IRON-7 覆盖块，54 行，将核心子系统 CONFIG 覆盖回 vanilla 默认，[12-build-and-flash-strategy.md §11.2](12-build-and-flash-strategy.md)）——后者覆盖前者。三架构共用同一套 fragment 机制，sw_64 仅为 `ARCH` 与碎片文件名的差异。

### 6.4 %build 段（sw_64）

```spec
%build
# （发行版版本注入见 §6.1；defconfig 合入见 §6.3）
make ARCH=%{build_arch} -j$(nproc) \
     KCFLAGS="%{?build_cflags}" \
     CONFIG_MODULE_SIG=%{?with_module_sign:1}%{!?with_module_sign:0}
# 记录最终 .config 用于产物归档与 E5 diffconfig 校验（§7.4）
cp .config config-%{version}-%{release}.%{build_arch}
```

### 6.5 %install 段（arch 条件）

```spec
%install
# 1. 内核镜像（按架构区分产物路径）
%ifarch sw_64
install -m 0644 arch/sw_64/boot/vmlinuz %{buildroot}/boot/vmlinuz-%{version}-%{release}
%endif
%ifarch x86_64
install -m 0644 arch/x86/boot/bzImage %{buildroot}/boot/vmlinuz-%{version}-%{release}
%endif
%ifarch aarch64
install -m 0644 arch/arm64/boot/Image %{buildroot}/boot/vmlinuz-%{version}-%{release}
%endif

# 2. 符号表与配置存档
install -m 0644 System.map %{buildroot}/boot/System.map-%{version}-%{release}
install -m 0644 config-%{version}-%{release}.%{build_arch} \
        %{buildroot}/boot/config-%{version}-%{release}

# 3. 内核模块
make ARCH=%{build_arch} modules_install INSTALL_MOD_PATH=%{buildroot}/usr INSTALL_MOD_STRIP=1

# 4. kernel-devel（头文件 + Makefile，供 out-of-tree 模块编译）
mkdir -p %{buildroot}/usr/src/kernels/%{version}-%{release}.%{build_arch}
cp -a include %{buildroot}/usr/src/kernels/%{version}-%{release}.%{build_arch}/
cp -a arch/%{build_arch}/include \
        %{buildroot}/usr/src/kernels/%{version}-%{release}.%{build_arch}/arch/%{build_arch}/
cp Makefile scripts %{buildroot}/usr/src/kernels/%{version}-%{release}.%{build_arch}/

# 5. defconfig 产物（回灌本地 ALK 树与 E5 校验用）
install -m 0644 arch/%{build_arch}/configs/airy_defconfig \
        %{buildroot}/boot/defconfig-%{version}-%{release}.%{build_arch}
```

> **TODO(待核验)**：sw_64 内核镜像在构建目录中的确切路径（`arch/sw_64/boot/vmlinuz` 为占位推断，与 openEuler OLK-6.6 的 sw_64 Makefile 实际产物一致与否待首次构建确认；若差异，仅需更新 `%define kernel_image` 与 %install 分支，不影响方案结构）。

### 6.6 KABI 构建期校验的借鉴与取舍

openEuler 的 KABI 构建期校验体系：`scripts/kabideps`（模块引用符号表）与 `scripts/kabisyms`（生成 kABI baseline `Module.kabi`）在构建期/发布期生成 baseline，`scripts/check-kabi` 对 baseline 做 diff 校验（来源：`agent-linux/00-reviews/_review_v3.6/21-openEuler-engineering-standards-v3.6c.md` §1.1 与 §10）。

AirymaxOS 取舍：
- **不启用** openEuler KABI baseline 校验：LAYER 导入已剥离 `__KABI` 标记（[12-build-and-flash-strategy.md §11.3](12-build-and-flash-strategy.md) 零命中验证），无 KABI 占位可校验；`%kabi_check 0`（§4.1）关闭。
- **借鉴其"构建期 baseline + diff"方法论**：用于 sw_64 的配置一致性校验——把 OBS 构建产物的 `config-*.sw_64` 作为 baseline，与本地 `make ARCH=sw_64 airy_defconfig` 结果做 diff（§7.4 step 3），以及 E5 的 IRON-7 关键配置漂移检测（§8.2）。这正是 v3.6 审查 E17 借鉴点（构建期 baseline diff 校验）在 sw_64 构建链上的落点。

---

## 7. 构建流程与验证

### 7.1 osc checkout 与本地配置

```bash
# 一次性配置：OBS API 端点与认证（TODO(待核验): 以实际 OBS 地址为准）
# osc 的 ~/.config/osc/oscrc 写入 [general] apiurl=... 与用户凭据

# 检出项目包
osc co AirymaxOS:Factory:Kernel airy-kernel
cd AirymaxOS:Factory:Kernel/airy-kernel
# 目录内容：_service、airy-kernel.spec、（可选）本地补丁文件
```

### 7.2 触发远程构建

```bash
# 1. 更新 _service / spec 后，强制重新拉取源码 tarball 并本地生成源
osc service manualrun

# 2. 本地提交（可选，校验 spec 合法性）
osc build --no-verify standard_sw_64 sw_64 airy-kernel.spec   # 形态 A 本地试跑（需 OBS 后端）

# 3. 提交到 OBS，触发后端 sw_64 构建
osc addremove
osc commit -m "trigger sw_64 build for ALK-6.6-dev <commit-hash>"
```

> 构建实际发生在 OBS 后端（openEuler OBS 或自建实例），本机 `osc build` 仅为可选本地试跑；推荐流程为 `osc commit` 触发后端调度。

### 7.3 构建状态与产物下载

```bash
# 查看 sw_64 仓库构建状态
osc results AirymaxOS:Factory:Kernel airy-kernel --repository=standard_sw_64

# 实时跟踪构建日志
osc buildlog AirymaxOS:Factory:Kernel airy-kernel standard_sw_64 sw_64

# 下载全部 sw_64 产物 RPM
osc getbinaries AirymaxOS:Factory:Kernel airy-kernel standard_sw_64 sw_64 \
    --outdir=~/airy-build/sw_64/

# 产物清单（5 包拆分）
ls ~/airy-build/sw_64/
# airy-kernel-6.6.0-airy.1.sw_64.rpm
# airy-kernel-devel-6.6.0-airy.1.sw_64.rpm
# airy-kernel-headers-6.6.0-airy.1.sw_64.rpm
# airy-kernel-modules-6.6.0-airy.1.sw_64.rpm
# airy-kernel-debuginfo-6.6.0-airy.1.sw_64.rpm
```

**关键日志检查点**：
1. `_service` 阶段：`tar_scm` 拉取 `ALK-6.6-dev` 成功（无认证/网络错误）。
2. defconfig 阶段：`make ARCH=sw_64 airy_defconfig` 产出 `.config`（行数 ≈ 3851，与 [12-build-and-flash-strategy.md §11.3](12-build-and-flash-strategy.md) 本地验证一致）。
3. 编译阶段：`Kernel: arch/sw_64/... vmlinuz is ready`（镜像路径以实际产物为准，§6.5 TODO）。
4. 无 qemu 调用：日志中无 `qemu-sw_64` / `qemu-system-sw_64` 字样（`grep -i qemu` 零命中）。

### 7.4 构建侧静态验证（本机执行）

OBS 产物回灌本机后，执行**静态验证**（本方案的核心验证手段，运行态验证见 §7.5 边界）：

```bash
# 0. 解包 debuginfo 获取带符号 vmlinux（静态检查首选对象）
mkdir -p ~/airy-build/sw_64/dbg && cd ~/airy-build/sw_64/dbg
rpm2cpio ../airy-kernel-debuginfo-6.6.0-airy.1.sw_64.rpm | cpio -idmv
VMLINUX=$(find . -name vmlinux | head -1)
SYSMAP=System.map   # 从 airy-kernel RPM 解出 /boot/System.map-*

# 1. strings：CONFIG_AIRY 相关字符串（配置/模块名/版本串在镜像中的落字）
strings "$VMLINUX" | grep -iE 'airy|CONFIG_AIRY' | sort -u | head -30
strings "$VMLINUX" | grep -E '6\.6\.0' | head -10    # 版本串（发行版注入值）

# 2. kallsyms：airy 符号在符号表中的存在性（微内核化改造模块符号）
nm "$VMLINUX" | grep -E ' [tTdDrR] airy_' | head -20
grep -c ' airy_' "$SYSMAP"    # 预期 >0（airy_lsm / airy_cap / airy_die_notify 等）

# 3. modinfo：内核模块元数据（vermagic 反映内核版本与 MODVERSIONS）
modinfo ./usr/lib/modules/*/kernel/security/airy/*.ko 2>/dev/null \
    | grep -E 'filename|vermagic|description'

# 4. objdump/readelf：架构指令与 ELF 机器类型（确认是 sw_64 目标而非误编译为 x86/arm64）
readelf -h "$VMLINUX" | grep -E 'Class|Machine|Flags'
objdump -d "$VMLINUX" | head -30   # sw_64 指令形态（32/64 位混排、专属寻址模式）
objdump -i | grep -i sw64 || echo "本机 binutils 无 sw64 target"  # 工具链能力探测
```

> **边界（诚实声明）**：步骤 4 的 `objdump` 依赖支持 sw_64 目标的 binutils。本机（x86 发行版）binutils 通常不含 sw_64 target（**TODO(待核验)**：本机 `objdump -i` 是否含 sw64）；若缺，则 objdump 步骤回退到 OBS 侧执行（在 sw_64 构建环境内跑同一命令），或使用 LLVM 工具链（`llvm-objdump`，其 sw_64 支持程度 **TODO(待核验)**）。步骤 1-3（strings/nm/modinfo/readelf）不依赖架构 target，本机可直接执行。

### 7.5 运行态验证边界

**OBS 远程构建只能证明"编译通过 + 静态符号/指令形态正确"，不能证明"能启动、能运行"**。运行态验证（boot、驱动加载、微内核化改造行为、`airy_die_notify` 等 die reason 映射在 sw_64 上的行为）仍依赖：

1. 原生申威硬件（§7.6 回退、§10.2 采购建议）；
2. 或未来 qemu 上游对 sw_64 的仿真支持（§10.1）。

在两者到位前，sw_64 的验证等级为：**配置生成 ✓ → 完整编译 ✓（本方案）→ 静态验证 ✓（本方案）→ 运行态 ✗（待硬件/模拟器）**。

### 7.6 回退方案（OBS 不可用时的原生硬件直连）

若 OBS 不可用（实例宕机、token 失效、path 依赖中断），回退为**原生申威硬件直连 make**：

```bash
# 在申威主机（openEuler 24.03 LTS sw_64）上：
git clone <ALK-6.6-dev-url> alk && cd alk
git checkout ALK-6.6-dev
sudo dnf install -y gcc make bc flex bison openssl-devel \
     elfutils-libelf-devel dwarves diffutils
make ARCH=sw_64 airy_defconfig
make ARCH=sw_64 -j$(nproc)
ls arch/sw_64/boot/vmlinuz
```

回退方案产物用同一 `airy-kernel.spec` `rpmbuild -ba` 打包入库。OBS 为主路径、硬件直连为应急回退，与 §8.3 的失败回滚衔接。

---

## 8. CI 集成与触发策略

### 8.1 与 sync-euler-drivers.sh E4/E5 的衔接

上游同步脚本 `sync-euler-drivers.sh`（位于 `/home/spharx/SpharxWorks/sync-upstream/sync-euler-drivers.sh`，五阶段 E1-E5）当前对 sw_64 的处理：

| 阶段 | 现状 | 衔接方案 |
|------|------|---------|
| E4（三架构 defconfig 验证） | sw_64 因"本机无交叉 gcc"记录跳过（脚本 L603-605：`[sw_64][skip] 本机无交叉 gcc，需 OBS 远程构建`） | **E4 检测到 sw_64 相关变更时，改触发 OBS 远程构建**（§8.2），以 OBS 构建日志中 defconfig/编译阶段结果替代本地跳过；本地 E4 对 sw_64 保持跳过，但报告从"跳过"升级为"已交 OBS" |
| E5（diffconfig IRON-7 一致性验证） | sw_64 因无 baseline/current config 而跳过（脚本 L664-666、L676-677） | **E5 使用 OBS 产物 config 作为 sw_64 的 current config**：从 `airy-kernel-*.sw_64.rpm` 解出 `/boot/config-*`，与本地 `make ARCH=sw_64 airy_defconfig` 基线做 diffconfig；IRON-7 关键配置（`CONFIG_AIRY/AIRYMAX/SECURITY/SCHED/MODULES`，脚本 L647-653）漂移检测沿用 |

**触发点**：E4 阶段在 `SYNC_PATHS`（`drivers/`、`arch/x86/`、`arch/arm64/`、`arch/sw_64/`）与 `configs/euler_hw_*.config` 检出变更时，调用 OBS 触发（§8.3 脚本）。

### 8.2 触发条件

sw_64 OBS 构建的触发条件（满足任一即触发）：

| 触发条件 | 检测方式 | 理由 |
|---------|---------|------|
| `arch/sw_64/` 任何文件变更 | `git diff --name-only <base>..<tip> -- arch/sw_64/` 非空 | 直接导入轨的架构代码变更（[11-layer-feasibility-study.md §2.3](11-layer-feasibility-study.md)） |
| `configs/euler_hw_*.config` 变更 | 同上匹配 `configs/euler_hw_sw64.config`（含 x86/arm64 碎片同源变更） | 硬件碎片影响 sw_64 配置合入（§6.3） |
| `configs/defconfig-agent` 变更 | 同上 | IRON-7 覆盖块影响全部架构 |
| 手动触发（发布/验收） | `osc commit` | 1.0 发布前的强制重建 |

**不触发**的情形：`kernel/sched/`、`security/airy/` 等 airy 核心路径变更（这些不进入 sw_64 的 LAYER 双轨同步，[12-build-and-flash-strategy.md §11](12-build-and-flash-strategy.md)）——除非该变更被判定影响三架构共性（由 E5 的 IRON-7 漂移检测兜底）。

### 8.3 触发脚本与失败回滚

```bash
#!/usr/bin/env bash
# trigger-obs-sw64.sh —— E4/E5 阶段调用的 OBS sw_64 构建触发器（骨架）
set -euo pipefail
ALK_DIR="${ALK_DIR:-/home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel}"
PROJ="AirymaxOS:Factory:Kernel"
PKG="airy-kernel"
# TODO(待核验): OBS API 端点/token 由环境注入（CI secret），不落仓库
OSC_APIURL="${OSC_APIURL:?}"; OBS_TOKEN="${OBS_TOKEN:?}"
LASTGOOD_FILE="${LASTGOOD_FILE:-/var/lib/airy-obs/last-good-sw64}"   # 上次成功 commit

# 1. 检测 sw_64 相关变更
CHANGED=$(git -C "$ALK_DIR" diff --name-only HEAD~1..HEAD -- \
    arch/sw_64/ configs/euler_hw_sw64.config configs/defconfig-agent 2>/dev/null || true)
[[ -z "$CHANGED" ]] && { echo "no sw_64 change, skip"; exit 0; }

# 2. 触发 OBS 构建（osc 客户端 + token；等价于人工 osc commit 流程）
osc -A "$OSC_APIURL" co "$PROJ" "$PKG"
cd "$PROJ/$PKG"
osc service manualrun
osc addremove
osc commit -m "trigger sw_64 build for ALK-6.6-dev $(git -C "$ALK_DIR" rev-parse --short HEAD)"

# 3. 等待构建结果（轮询 osc results，超时 120min）
#    succeeded → 记录 last-good
#    failed    → 告警 + 失败回滚（见下）
```

**失败回滚策略**：

| 回滚层级 | 动作 | 依据 |
|---------|------|------|
| OBS 包级 | 回退 `_service` 的 `revision` 到 `LASTGOOD` commit（上次成功构建的 ALK commit），`osc service manualrun && osc commit` 重建 | OBS 保留历史成功二进制，`osc getbinaries` 可直接取回 last-good RPM |
| 产物级 | 直接从 OBS 仓库下载上次成功 RPM 分发（不回滚源码） | 同步阻断（sync-euler-drivers E4 失败即阻断合并） |
| 源码级 | 内核仓库 `git reset --hard <pre-E3-head>`（复用 sync-euler-drivers.sh E3 的 pre-head 记录机制，脚本 L363-367） | 仅当 E3 应用阶段出错时 |

**门禁语义**：OBS sw_64 构建失败即阻断涉及 sw_64 路径的合并（与 sync-euler-drivers E4 "任一可构建架构失败则退出非零"一致，脚本 L611-617）；构建成功但 E5 检出 IRON-7 漂移则告警并人工审查（脚本 L727-731 语义）。

---

## 9. 与既有基础设施的衔接

| 既有设施 | 衔接点 | 本方案落地 |
|---------|--------|-----------|
| [11-layer-feasibility-study.md](11-layer-feasibility-study.md) | §2.3 双轨制：`arch/sw_64/` **直接导入轨**（366 文件，vanilla 无此树、零冲突）；`drivers/` quilt 轨 | sw_64 构建即验证直接导入轨的编译完整性；quilt 补丁经 §3.1 `extract_file`/§6.2 `%patch` 应用 |
| [12-build-and-flash-strategy.md](12-build-and-flash-strategy.md) | §1.1 defconfig 体系（openeuler_defconfig 底座 + euler_hw_*.config + defconfig-agent，merge_config.sh 合入）；§1.2 airy-kernel.spec 5 包拆分；§3.2 OBS 项目命名（`AirymaxOS:Factory:Kernel`）；§3.1 dnf 仓库 `sw_64/` 子目录；§11 双轨制落地登记（产物 #1-#13） | 本方案的 OBS 项目/包/spec/产物分发全部对齐上述章节；§11.6 后续工作 #1（sw_64 交叉编译链）与 #4（OBS 多架构构建配置）由本文档承接 |
| sync-euler-drivers.sh（`/home/spharx/SpharxWorks/sync-upstream/sync-euler-drivers.sh`） | E4 三架构 defconfig 验证（sw_64 记录跳过）；E5 diffconfig IRON-7 一致性验证（sw_64 跳过） | §8.1/§8.2 将 sw_64 从"跳过"升级为"OBS 触发构建 + 产物回灌参与 E5 校验" |
| v3.6 审查报告（`agent-linux/00-reviews/_review_v3.6/`） | OBS 相关内容**未提及**（本方案自建）；构建事实来源：`21-openEuler-engineering-standards-v3.6c.md` §9（Makefile.oever/Kbuild filechk_offsets/Makefile.build）、§1.1+§10（KABI 构建期校验 kabideps/kabisyms/check-kabi）；sw_64 唯一提及为 `16-fault-handling-isolation-v3.6b.md` L134 与 `18-closure-summary-v3.6b.md` L152（airy_die_notify 需补 `CONFIG_SW64` 守卫，N13） | §6.1（版本解耦）、§6.6（KABI 取舍）引用上述事实；N13 的 `CONFIG_SW64` 守卫补丁纳入后续内核提交（§10.3），其编译验证经 OBS 通道 |

**保密与合规边界**（与 [12-build-and-flash-strategy.md §9](12-build-and-flash-strategy.md) 一致）：本文档为闭源参考，不进入开源 `docs/AirymaxOS/`；OBS 项目名、API 端点、toolchain path 等内部基础设施信息不对外暴露（BAN-INTERNAL-002 硬件适配语境豁免）；OBS 构建产物（含 LAYER sw_64 驱动源码）发布时须公开源码以满足 GPL-2.0 强 copyleft 要求（[11-layer-feasibility-study.md §3.2](11-layer-feasibility-study.md)）。

---

## 10. 已知限制与后续工作

### 10.1 qemu 无 sw_64 仿真的长远解

| 路径 | 说明 | 状态 |
|------|------|------|
| 跟踪 mainline qemu 上游 | 关注 qemu-devel 对 Sunway/申威 target 的补丁进展；一旦合入，qemu 仿真可用于运行态验证（boot + smoke test） | **TODO(待核验)**：持续跟踪，未设置自动轮询机制 |
| 评估申威生态模拟器 | 申威生态存在模拟/仿真工具（如 shenwei 相关模拟器项目），可用于早期运行态验证 | **TODO(待核验)**：模拟器项目名、可用性、许可证未核验，落地前调研 |
| openEuler qemu 包 | openEuler qemu 8.2.0 不含 sw_64 target（阻塞点 #2），其后续版本是否跟进取决于上游 | 待上游 |

**近期不动摇结论**：在 qemu/模拟器就绪前，sw_64 运行态验证只可能来自原生硬件（§10.2），OBS 构建链维持"编译 + 静态验证"等级（§7.5）。

### 10.2 原生硬件采购建议

| 项 | 建议 |
|----|------|
| 硬件形态 | 申威 SW64 处理器服务器/工控机（如 SW-3900 系）或申威开发板，跑 openEuler 24.03 LTS sw_64 版 |
| 最低配置 | ≥ 8 GB 内存（内核全量编译峰值约 4 GB）、≥ 50 GB 磁盘、网络可达 |
| 用途 | (1) OBS 形态 A 的后端 sw_64 构建环境（若自建 OBS）；(2) §7.6 回退直连构建；(3) 运行态验证（boot/驱动/微内核化改造） |
| 替代 | 若采购受阻，评估申威云服务/托管服务（**TODO(待核验)**：供应商与可用性） |

### 10.3 已验证 vs 待验证（诚实清单）

**已验证**（来源：[12-build-and-flash-strategy.md §11.3](12-build-and-flash-strategy.md)）：

- ✅ `arch/sw_64/` 366 文件完整导入（直接导入轨）
- ✅ `make ARCH=sw_64 airy_defconfig` 配置生成（3851 行，`CONFIG_SW64=y`、`CONFIG_SECURITY_AIRY=y`）
- ✅ `grep -r '__KABI' arch/sw_64/ configs/` 与 `Makefile.oever` 零命中
- ✅ arch/sw_64/ 不触及 kernel/sched/、security/（正交性）

**本方案交付后待验证**：

- ⏳ `make ARCH=sw_64` 完整编译（OBS 构建 succeeded）
- ⏳ 5 包 RPM 产出完整（kernel/devel/headers/modules/debuginfo）
- ⏳ 静态验证通过（strings/modinfo/kallsyms/objdump，§7.4）
- ⏳ E5 使用 OBS 产物 config 的 IRON-7 一致性（§8.1）

**仍待后续（非本方案范围）**：

- ⏳ 运行态验证（原生硬件/模拟器，§10.1/§10.2）
- ⏳ N13 修复：`airy_die_notify.c` 补 `CONFIG_SW64` 守卫的 die reason 映射（来源：`00-reviews/_review_v3.6/16-fault-handling-isolation-v3.6b.md` L134），修复后的编译验证走 OBS 通道

### 10.4 后续任务表

| # | 任务 | 优先级 | 依赖 |
|---|------|--------|------|
| F1 | 申请/确认 OBS 实例与账号 token（openEuler 官方或自建，§2.4） | P0 | — |
| F2 | 落地 `AirymaxOS:Factory:Kernel` 项目（meta/prjconf/_service/spec，§2-§6） | P0 | F1 |
| F3 | 首次 sw_64 构建并完成 §7.4 静态验证 | P0 | F2 |
| F4 | 核验 sw_64 交叉包命名与镜像路径（§4.3/§6.5 TODO） | P1 | F3 |
| F5 | sync-euler-drivers.sh E4/E5 联动 OBS（§8.1-§8.3） | P1 | F3 |
| F6 | 评估 qemu 上游与申威模拟器（§10.1） | P2 | — |
| F7 | 原生硬件采购/云资源（§10.2） | P2 | — |
| F8 | N13 `CONFIG_SW64` 守卫补丁 + OBS 验证（§10.3） | P2 | F3 |

---

## 11. 引用

1. [12-build-and-flash-strategy.md](12-build-and-flash-strategy.md) — 编译与烧录策略（§1.1 defconfig 合入、§1.2 spec 5 包拆分、§3.1 dnf 仓库、§3.2 OBS 项目命名、§11 双轨制落地登记）
2. [11-layer-feasibility-study.md](11-layer-feasibility-study.md) — LAYER 方案可行性论证（§1.1 正交性、§1.3 版本对齐、§2.3 双轨制）
3. `agent-linux/00-reviews/_review_v3.6/21-openEuler-engineering-standards-v3.6c.md` — openEuler 工程标准研究（§9 Makefile.oever 版本解耦 / Kbuild filechk_offsets / scripts/Makefile.build；§1.1+§10 KABI 构建期校验 kabideps/kabisyms/check-kabi）
4. `agent-linux/00-reviews/_review_v3.6/16-fault-handling-isolation-v3.6b.md` L134 — sw_64 需补 `CONFIG_SW64` 守卫（N13）
5. `agent-linux/00-reviews/_review_v3.6/18-closure-summary-v3.6b.md` L152 — arm64/sw_64 架构未深查声明
6. `/home/spharx/SpharxWorks/sync-upstream/sync-euler-drivers.sh` — 五阶段同步脚本（E3 pre-head 回退机制 L363-367、E4 sw_64 跳过 L603-605、E5 IRON-7 校验 L627-736）

---

> **文档结束** | SPHARX Ltd 内部参考 | 闭源不公开
