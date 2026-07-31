Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 编译与烧录策略（全面复用 openEuler 构建体系）

> **保密级别**: SPHARX Ltd 内部参考，**闭源不公开**
> **版本**: 1.0.0
> **最后更新**: 2026-07-30
> **适用范围**: AirymaxOS 构建工程组 + 内核开发组 + 发布工程组
> **前置文档**: [10-olk66-vanilla-diff.md](10-olk66-vanilla-diff.md)（OLK-6.6 与 vanilla 差异对比 SSoT）、[11-layer-feasibility-study.md](11-layer-feasibility-study.md)（LAYER 方案可行性论证）

---

## 0. 方案概述

AirymaxOS 1.x.x 的内核编译、镜像构建、烧录部署、图形 UI 全链路**全面复用 openEuler 24.03 LTS（OLK-6.6）构建体系**，采用"**叠加层 + 配置覆盖**"模式，**不 fork** openEuler 构建工具链。

核心依据：

1. **版本天然对齐**：openEuler 24.03 LTS 当前内核版本为 `kernel-6.6.0-145.0.8.135`（安全公告 openEuler-BA-2026-1011 确认），与 AirymaxOS vanilla 6.6.145 在 `6.6.0-145` 段完全对齐（详见 [11-layer-feasibility-study.md §1.3](11-layer-feasibility-study.md)）
2. **LAYER 正交性**：硬件驱动层与微内核化改造补丁正交，构建可独立叠加（详见 [11-layer-feasibility-study.md §1.1](11-layer-feasibility-study.md)）
3. **GPL-2.0 兼容**：openEuler 构建工具链（imageTailor/Yocto/isocut 等）均为开源工具，AirymaxOS 可自由复用（详见 [11-layer-feasibility-study.md §3.1](11-layer-feasibility-study.md)）

```
AirymaxOS 构建链 = openEuler 构建工具链（不 fork）
                 + airy-kernel.spec（覆盖 kernel.spec 品牌与包名）
                 + configs/defconfig{-agent,-embedded}（叠加 fragment）
                 + custom/cfg_airymax/（imageTailor/Yocto 配置覆盖）
                 + ks.cfg（Kickstart 安装脚本定制）
```

---

## 1. 内核编译策略

### 1.1 defconfig 体系复用

openEuler 在 `arch/{x86,arm64,sw_64}/configs/` 下维护 `openeuler_defconfig`，是经过大规模硬件兼容性验证的企业级默认配置。AirymaxOS 以其为底座，叠加自有 fragment：

| 层次 | 文件 | 作用 | 来源 |
|------|------|------|------|
| 底座 | `arch/{x86,arm64,sw_64}/configs/openeuler_defconfig` | 硬件适配基线配置 | openEuler（LAYER 导入，详见 [10-olk66-vanilla-diff.md §3.3](10-olk66-vanilla-diff.md)） |
| 叠加层 | `configs/defconfig-agent` | agentrt-linux 微内核化改造 CONFIG（sched_tac/airy_lsm/AgentsIPC/[SC] 等） | AirymaxOS 自有 |
| 叠加层 | `configs/defconfig-embedded` | 嵌入式裁剪 CONFIG（去除非必要驱动、调试项） | AirymaxOS 自有 |
| 硬件碎片 | `configs/euler_hw_{x86,arm64,sw64}.config` | 从 openeuler_defconfig 提取的硬件相关 CONFIG 碎片 | AirymaxOS 提取（详见 [10-olk66-vanilla-diff.md §8.3](10-olk66-vanilla-diff.md)） |

**合并机制**：使用 Linux 内核官方 `scripts/kconfig/merge_config.sh`，按"底座 → 硬件碎片 → agent → embedded"顺序叠加，后者覆盖前者。

```bash
# 示例：x86 agent 版本编译
./scripts/kconfig/merge_config.sh \
  arch/x86/configs/openeuler_defconfig \
  configs/euler_hw_x86.config \
  configs/defconfig-agent \
  -O build/x86-agent
make O=build/x86-agent -j$(nproc)
```

**关键约束**：

1. **IRON-7 不变**：openeuler_defconfig 中触及调度（`CONFIG_SCHED_*`）、安全（`CONFIG_LSM_*`、`CONFIG_LANDLOCK*`）、内存核心子系统的 CONFIG 项，由 `configs/defconfig-agent` 覆盖回 vanilla 默认值
2. **sched_ext 不存在**：OLK-6.6 与 vanilla 6.6.145 均不含 `CONFIG_SCHED_EXT`（详见 [10-olk66-vanilla-diff.md §5.2](10-olk66-vanilla-diff.md)），无需处理
3. **KABI 标记剥离**：openeuler_defconfig 中若引用 `__KABI_*` 宏的 CONFIG，剥离后保留功能、去除 KABI 占位

### 1.2 airy-kernel.spec RPM 打包

openEuler 的 `kernel.spec` 是经过企业级生产验证的 RPM 打包模板，采用 **5 包拆分**规则。AirymaxOS 改名为 `airy-kernel.spec`，保留拆分结构，覆盖品牌与包名：

| openEuler 包名 | AirymaxOS 包名 | 内容 | 处置 |
|---------------|---------------|------|------|
| `kernel` | `airy-kernel` | 内核镜像（vmlinuz）+ initramfs | 改名 |
| `kernel-devel` | `airy-kernel-devel` | 内核头文件 + Makefile（模块编译所需） | 改名 |
| `kernel-headers` | `airy-kernel-headers` | UAPI 头文件（含 `include/uapi/linux/airymax/`） | 改名 |
| `kernel-modules` | `airy-kernel-modules` | 内核模块（.ko） | 改名 |
| `kernel-debuginfo` | `airy-kernel-debuginfo` | 调试符号 | 改名 |

**关键改动点**：

1. `Name:` 字段：`kernel` → `airy-kernel`
2. `Version:` 字段：保留 `6.6.0`（与 openEuler 对齐）
3. `Release:` 字段：自定义 AirymaxOS 发行号（如 `airy.1`）
4. `%define build_flavor`：保留 openEuler 的 flavor 机制
5. Source0：指向 AirymaxOS 内核源码 tarball
6. 补丁应用区：`%patch` 宏应用 LAYER 驱动补丁 + agentrt-linux 微内核化改造补丁
7. `Provides:`/`Obsoletes:`：声明提供 `airy-kernel`，废弃旧包名

**优势**：复用 openEuler 的 `%post`/`%preun` 脚本（initramfs 重建、grub 更新、模块签名等），无需重新实现。

### 1.3 编译产物

| 产物 | 用途 | 来源 |
|------|------|------|
| `airy-kernel-6.6.0-airy.1.x86_64.rpm` | x86 内核安装包 | airy-kernel.spec |
| `airy-kernel-devel-*.x86_64.rpm` | 模块开发包 | airy-kernel.spec |
| `airy-kernel-modules-*.x86_64.rpm` | 内核模块包 | airy-kernel.spec |
| `vmlinuz-6.6.0-airy.1` | 裸内核镜像 | 编译输出 |
| `System.map-6.6.0-airy.1` | 符号表 | 编译输出 |
| `config-6.6.0-airy.1` | 编译配置存档 | 编译输出 |

---

## 2. 镜像构建策略

AirymaxOS 按部署形态分流为两类镜像构建工具链，均复用 openEuler：

| 部署形态 | 工具链 | 适用场景 | AirymaxOS 适配 |
|---------|--------|---------|---------------|
| 服务器/桌面 | **imageTailor** | x86/arm64 服务器 ISO 与磁盘镜像 | `custom/cfg_airymax/` 配置覆盖 |
| 嵌入式/边缘 | **Yocto Project** | 资源受限设备（arm64/sw_64 嵌入式） | `meta-airymax` 自定义层 |

### 2.1 imageTailor（服务器/桌面镜像）

imageTailor 是 openEuler 官方的 ISO/磁盘镜像裁剪工具，基于 RPM 仓库 + XML 配置生成定制镜像。

**AirymaxOS 适配层**：

```
imageTailor/
├── custom/
│   └── cfg_airymax/              # AirymaxOS 配置覆盖目录
│       ├── airymax.xml           # 镜像内容描述（RPM 包列表）
│       ├── airymax-repo.xml      # 仓库配置（指向 AirymaxOS dnf 仓库）
│       └── boot/
│           └── grub.cfg          # 启动菜单（品牌定制）
└── tailor.config                 # 调用入口
```

**关键配置项**：

1. **RPM 仓库**：`airymax-repo.xml` 指向 AirymaxOS 自有 dnf 仓库（详见 §3）
2. **包列表**：`airymax.xml` 引入 `airy-kernel` + openEuler base + AirymaxOS 专属包
3. **品牌定制**：grub.cfg 主题、启动 Logo、发行版名称
4. **镜像类型**：支持 ISO（安装介质）、qcow2（虚拟机）、raw（物理机）

**优势**：复用 openEuler 的 RPM 依赖解析、initramfs 生成、grub 配置逻辑，无需重新实现镜像构建管线。

### 2.2 Yocto Project（嵌入式镜像）

对于资源受限的嵌入式部署（如边缘网关、工控设备），AirymaxOS 复用 openEuler Embedded 的 Yocto 体系。

**AirymaxOS 适配层**：

```
meta-airymax/                     # AirymaxOS 自定义 Yocto 层
├── conf/layer.conf
├── recipes-kernel/
│   └── airy-kernel/
│       ├── airy-kernel_6.6.bb    # 内核 recipe（源码 + defconfig + 补丁）
│       └── files/
│           └── defconfig-embedded
├── recipes-core/
│   └── airy-init/                # 微内核化改造的 init 系统
└── recipes-graphics/             # UI 层（详见 §5）
```

**关键配置项**：

1. **内核 recipe**：`airy-kernel_6.6.bb` 引用 AirymaxOS 内核源码 + `configs/defconfig-embedded`
2. ** MACHINE 配置**：支持 x86-64、arm64、sw_64 嵌入式板卡
3. **镜像 recipe**：`core-image-airymax-minimal.bb`（无 GUI）、`core-image-airymax-edge.bb`（含 XFCE）

### 2.3 isocut（ISO 精简）

openEuler 的 `isocut` 工具用于从官方 ISO 中裁剪出精简 ISO。AirymaxOS 在以下场景复用：

- **最小化安装介质**：从完整 ISO 裁剪出仅含内核 + 最小 base 的安装 ISO
- **离线部署**：为无网络环境生成自包含 ISO

```bash
isocut -t /usr1/isocut/imageTailor/ -e /usr1/isocut/env airymax-original.iso airymax-minimal.iso
```

---

## 3. 仓库与分发策略

### 3.1 dnf 仓库结构

AirymaxOS 自建 dnf 仓库，结构对齐 openEuler 仓库约定：

```
/airymax-os/
├── everything/          # 全量包仓库
│   ├── x86_64/
│   ├── aarch64/
│   └── sw_64/
├── update/              # 更新包仓库
│   ├── x86_64/
│   ├── aarch64/
│   └── sw_64/
└── EPOL/                # Extended Package OL（扩展包，对齐 openEuler EPOL）
    ├── x86_64/
    ├── aarch64/
    └── sw_64/
```

**仓库内容来源**：

1. **airy-kernel.\*** 系列：AirymaxOS 自编译（§1.2）
2. **openEuler base 包**：从 openEuler 24.03 LTS 仓库同步（bash/glibc/systemd 等基础包，不修改）
3. **AirymaxOS 专属包**：agentrt-linux 用户态工具、[SC] 工具链、airy_lsm 管理工具等

### 3.2 OBS（Open Build Service）CI/CD

AirymaxOS 复用 openEuler 的 OBS 基础设施进行 CI/CD 构建，项目命名为 `AirymaxOS:Factory`：

| OBS 项目 | 用途 | 构建目标 |
|---------|------|---------|
| `AirymaxOS:Factory` | 主线滚动构建 | x86_64、aarch64、sw_64 |
| `AirymaxOS:1.0` | 1.0 发布版稳定构建 | x86_64、aarch64、sw_64 |
| `AirymaxOS:Factory:Kernel` | 内核专项构建 | 上述三架构 + kernel-devel/debuginfo |

**优势**：复用 openEuler OBS 的多架构交叉编译、依赖解析、签名、发布管线，无需自建构建集群。

### 3.3 镜像签名

所有 RPM 包与镜像产物通过 GPG 签名保障完整性：

1. **RPM 签名**：OBS 构建时使用 AirymaxOS GPG 私钥签名
2. **镜像签名**：ISO/qcow2 生成 `.sig` 签名文件
3. **仓库元数据签名**：`repodata/repomd.xml.asc` 防止仓库篡改

---

## 4. 烧录与安装部署策略

### 4.1 Anaconda + Kickstart（服务器/桌面）

openEuler 24.03 LTS 服务器版采用 Anaconda 安装器 + Kickstart 自动化脚本。AirymaxOS 全面复用：

| 组件 | openEuler | AirymaxOS | 处置 |
|------|----------|----------|------|
| 安装器 | Anaconda | Anaconda | 复用（不改代码） |
| 安装脚本 | `ks-openEuler.cfg` | `ks-airymax.cfg` | 改 ks.cfg |
| 安装介质 | ISO（含 Anaconda） | ISO（含 Anaconda） | imageTailor 生成 |
| 品牌 | openEuler | AirymaxOS | 改 ks.cfg + 主题包 |

**`ks-airymax.cfg` 关键定制**：

```kickstart
# AirymaxOS Kickstart
install
cdrom
lang zh_CN.UTF-8
keyboard us
timezone Asia/Shanghai

# 网络默认 DHCP
network --bootproto=dhcp --device=link --activate

# Root 密码（安装后强制修改）
rootpw --lock

# AirymaxOS 专属包组
%packages
@airy-base
airy-kernel
airy-kernel-devel
airy-lsm-tools
airy-sc-toolchain
cockpit                 # 默认 Web UI（详见 §5）
%end

# 安装后脚本：启用 cockpit
%post --nochroot
systemctl enable cockpit.socket
%end

reboot
```

**优势**：复用 Anaconda 的分区、引导、网络配置、依赖解析能力，AirymaxOS 仅需维护一份 ks.cfg。

### 4.2 嵌入式烧录（Yocto 镜像）

嵌入式部署不使用 Anaconda，采用直接烧录镜像：

| 目标介质 | 烧录方式 | 工具 |
|---------|---------|------|
| SD 卡 | `dd` 写入 raw/img | `dd if=core-image-airymax-*.img of=/dev/mmcblk0` |
| eMMC | U-Boot 引导写入 | `bmaptool copy` |
| QEMU | 直接挂载 qcow2 | `qemu-system-* -drive file=*.qcow2` |
| 网络 | PXE + TFTP | openEuler netboot（复用） |

### 4.3 OTA 升级

| 部署形态 | OTA 方案 | 来源 |
|---------|---------|------|
| 服务器/桌面 | `dnf upgrade`（原子更新 via rpm-ostree 可选） | openEuler dnf 体系 |
| 嵌入式 | RAUC 或 SWUpdate（A/B 分区） | 开源 OTA 工具 |

---

## 5. 图形 UI 策略（三层分流架构）

AirymaxOS 按部署形态与资源约束，采用**三层分流架构**选择图形 UI：

| 层次 | 部署形态 | UI 方案 | 资源占用 | 默认 |
|------|---------|---------|---------|------|
| **Layer 0** | 服务器/云/无头边缘 | 无 GUI + Cockpit Web UI | <50MB | **是** |
| **Layer 1** | 边缘工作站 | XFCE 轻量桌面 | ~200MB | 否（可选） |
| **Layer 2** | 开发工作站 | DDE 或 UKUI 完整桌面 | ~1GB | 否（可选） |

### 5.1 Layer 0：无 GUI + Cockpit（默认）

**定位**：服务器、云实例、无头边缘设备。资源占用最低，通过 Web 浏览器远程管理。

**Cockpit 选型理由**：

1. **openEuler 官方支持**：openEuler 24.03 LTS 仓库原生提供 `cockpit` 包，无需额外维护
2. **零桌面依赖**：Cockpit 是 Web 服务（cockpit-ws + cockpit-bridge），不依赖 X/Wayland
3. **内核管理能力**：Cockpit 原生支持内核模块加载、性能监控、KVM 虚拟化管理
4. **AirymaxOS 适配**：开发 `cockpit-airymax` 插件面板，提供 agentrt-linux 微内核化改造状态、[SC] 契约视图、airy_lsm 策略管理

**安装形态**：

```bash
# ks.cfg 中默认安装
dnf install cockpit cockpit-airymax
systemctl enable --now cockpit.socket
# 默认监听 9090 端口
```

**访问**：`https://<host>:9090`

### 5.2 Layer 1：XFCE 轻量桌面（边缘可选）

**定位**：边缘工作站、工业终端、需要本地图形交互但资源受限的场景。

**XFCE 选型理由**：

1. **轻量**：内存占用 ~200MB，适合 4GB 内存设备
2. **openEuler 仓库提供**：`dnf install @xfce-desktop` 即可
3. **稳定成熟**：XFCE 长期维护，无激进变更
4. **Wayland/X11 双支持**：兼容老旧硬件

**安装形态**：

```bash
# ks.cfg 中按需安装
%packages
@xfce-desktop
%end
```

### 5.3 Layer 2：DDE / UKUI 完整桌面（开发可选）

**定位**：开发工作站、桌面评估环境、需要完整图形体验的场景。

**DDE / UKUI 选型理由**：

1. **openEuler 原生桌面**：openEuler 24.03 LTS 同时提供 DDE（深度桌面环境）与 UKUI（麒麟桌面环境）
2. **国产化对齐**：DDE/UKUI 均为国产桌面环境，与 AirymaxOS 国产硬件适配定位一致
3. **开发者友好**：提供完整文件管理器、终端、设置中心

**安装形态**：

```bash
# 二选一
dnf install @dde-desktop      # 深度桌面
# 或
dnf install @ukui-desktop     # 麒麟桌面
```

### 5.4 UI 层与内核解耦

**关键设计原则**：UI 层与 agentrt-linux 微内核化改造完全解耦——

1. UI 层运行在用户态，通过标准 syscall 与内核交互
2. agentrt-linux 的 4 核心 syscall（548-551）+ op-dispatch 不影响 UI 层兼容性
3. [SC] 共享契约层（10 个 UAPI 头文件）为 UI 层提供稳定接口
4. 三层 UI 方案可按部署形态自由组合，不影响内核编译

---

## 6. 版本对齐矩阵

| 组件 | openEuler 版本 | AirymaxOS 版本 | 对齐情况 |
|------|---------------|---------------|---------|
| 内核基线 | `kernel-6.6.0-145.0.8.135` | vanilla 6.6.145 | ✓ `6.6.0-145` 段完全对齐 |
| glibc | 2.38 | 同步 openEuler | ✓ |
| systemd | 254 | 同步 openEuler | ✓ |
| Anaconda | openEuler 定制版 | 复用不改 | ✓ |
| imageTailor | openEuler 24.03 LTS 版 | 复用不改 | ✓ |
| Yocto | openEuler Embedded（Yocto 4.0 Kirkstone 基线） | 复用 + meta-airymax | ✓ |
| Cockpit | 295+ | 同步 openEuler | ✓ |
| XFCE | 4.18 | 同步 openEuler | ✓ |
| DDE | openEuler 24.03 LTS 版 | 同步 | ✓ |
| UKUI | openEuler 24.03 LTS 版 | 同步 | ✓ |

**关键结论**：由于 `6.6.0-145` 段天然对齐，AirymaxOS 无需等待 openEuler 版本迁移，可直接复用 24.03 LTS 全套构建工具链。

---

## 7. 部署形态组合矩阵

| 部署形态 | 内核 | 镜像 | UI 层 | 安装方式 | 目标硬件 |
|---------|------|------|-------|---------|---------|
| 服务器（标准） | airy-kernel RPM | imageTailor ISO | Layer 0（Cockpit） | Anaconda + ks | x86/arm64 服务器 |
| 云实例 | airy-kernel RPM | imageTailor qcow2 | Layer 0（Cockpit） | 镜像引导 | x86/arm64 虚拟机 |
| 边缘工作站 | airy-kernel RPM | imageTailor ISO | Layer 1（XFCE） | Anaconda + ks | x86/arm64 边缘设备 |
| 嵌入式设备 | airy-kernel（Yocto） | Yocto raw/img | Layer 0 或无 | dd/bmaptool | arm64/sw_64 嵌入式板 |
| 开发工作站 | airy-kernel RPM | imageTailor ISO | Layer 2（DDE/UKUI） | Anaconda + ks | x86 工作站 |

---

## 8. 风险与缓解

| # | 风险 | 等级 | 缓解措施 |
|---|------|------|---------|
| 1 | openEuler base 包升级引入与 agentrt-linux 不兼容的 syscall 行为变更 | 低 | AirymaxOS 仓库锁定 base 包版本，每次同步前跑 KUnit + kselftest + LTP |
| 2 | openeuler_defconfig 中的核心子系统 CONFIG 未被 fragment 覆盖 | 中 | CI 门禁：编译后 `diffconfig` 验证核心子系统 CONFIG 与 vanilla 一致 |
| 3 | imageTailor/Yocto 工具链版本升级破坏 `custom/cfg_airymax/` 配置 | 低 | 跟随 openEuler LTS 节奏升级，每次升级跑全量镜像构建测试 |
| 4 | openEuler 停止维护 OLK-6.6 / 24.03 LTS | 低 | 24.03 LTS 支持至 2029+，且有 atomgit/gitee 多镜像；7.1 迁移时 openEuler 会发布新基线（详见 [11-layer-feasibility-study.md §2.4](11-layer-feasibility-study.md)） |
| 5 | DDE/UKUI 桌面与 agentrt-linux syscall 不兼容 | 低 | UI 层通过标准 syscall 交互，4 核心 syscall（548-551）不影响 POSIX 兼容性 |
| 6 | OBS 多架构构建（sw_64）交叉编译链缺失 | 中 | 申威交叉编译链需独立配置；初期可仅构建 x86/arm64，sw_64 后续补齐 |

---

## 9. 一致性声明

1. **不 fork 原则**：AirymaxOS 全面复用 openEuler 构建工具链（imageTailor/Yocto/isocut/Anaconda/OBS/dnf），不 fork 任何工具代码，仅通过配置覆盖（`custom/cfg_airymax/`、`meta-airymax/`、`ks-airymax.cfg`、`airy-kernel.spec`）实现定制
2. **版本对齐**：openEuler `kernel-6.6.0-145.0.8.135` 与 AirymaxOS vanilla 6.6.145 在 `6.6.0-145` 段完全对齐（详见 [11-layer-feasibility-study.md §1.3](11-layer-feasibility-study.md)），构建工具链无需版本迁移
3. **IRON-7 不变**：复用 openEuler 构建体系不改变 vanilla 6.6.145 为唯一核心基线的事实——openeuler_defconfig 中的核心子系统 CONFIG 由 `configs/defconfig-agent` 覆盖回 vanilla 默认值
4. **BAN-INTERNAL-002（硬件适配语境豁免）**：本文档为闭源参考，不进入开源 `docs/AirymaxOS/`。硬件适配语境下允许在开源文档中明确表述"复用openEuler的硬件适配能力"（详见 `00-alk-kernel-overview.md` §3.1 等式与 §3.5.1 定位）
5. **GPL-2.0 合规**：复用 openEuler 构建工具链满足 GPL-2.0 许可证要求（工具链本身开源，AirymaxOS 产物源码公开）

---

## 10. 引用

1. [10-olk66-vanilla-diff.md](10-olk66-vanilla-diff.md) — OLK-6.6 与 vanilla 6.6.145 差异对比 SSoT
2. [11-layer-feasibility-study.md](11-layer-feasibility-study.md) — LAYER 方案可行性论证（技术/维护/法律/工程四维度）
3. openEuler 24.03 LTS 安全公告 openEuler-BA-2026-1011（kernel-6.6.0-145 版本确认）
4. openEuler imageTailor 官方文档（https://docs.openeuler.org/zh/docs/24.03 LTS/docs/Application-Development/imageTailor.html）
5. openEuler Embedded Yocto 文档（https://docs.openeuler.org/zh/docs/24.03 LTS/docs/embedded/embedded-yocto.html）
6. Cockpit 项目官方文档（https://cockpit-project.org/）
7. Anaconda/Kickstart 文档（https://docs.openeuler.org/zh/docs/24.03 LTS/docs/Installation/installation.html）

---

## 11. 实施进度（2026-07-31 落地登记）

### 11.1 已落地产物清单

**P0 内核层（kernel 仓库 ALK-6.6-dev）：**

| # | 产物 | 路径 | 规模 | 来源 |
|---|------|------|------|------|
| 1 | sw_64 架构完整导入 | `arch/sw_64/` | 366 文件（327 源 + 39 配置/脚本） | openEuler OLK-6.6 LAYER 导入 |
| 2 | sw_64 Airymax defconfig | `arch/sw_64/configs/airy_defconfig` | 695 行 | openeuler_defconfig + Airymax CONFIG |
| 3 | x86 openEuler 底座 | `arch/x86/configs/openeuler_defconfig` | 9573 行 | openEuler OLK-6.6 LAYER 导入 |
| 4 | arm64 openEuler 底座 | `arch/arm64/configs/openeuler_defconfig` | 8448 行 | openEuler OLK-6.6 LAYER 导入 |
| 5 | x86 硬件碎片 | `configs/euler_hw_x86.config` | 9390 行 | 提取自 openeuler_defconfig，剥离核心子系统 |
| 6 | arm64 硬件碎片 | `configs/euler_hw_arm64.config` | 8267 行 | 同上 |
| 7 | sw_64 硬件碎片 | `configs/euler_hw_sw64.config` | 634 行 | 同上 |
| 8 | defconfig-agent IRON-7 增强 | `configs/defconfig-agent` | 54 行 | 追加 IRON-7 覆盖块 |
| 9 | Kconfig 修复 | `Kconfig` | -1 行 | 移除 stale `source "config/Kconfig.alk"` |

**P1 构建链（agentrt-linux 管理仓 build/ 目录）：**

| # | 产物 | 路径 | 规模 |
|---|------|------|------|
| 10 | RPM 打包模板 | `build/airy-kernel.spec` | 164 行（5 包拆分） |
| 11 | Yocto 层骨架 | `build/meta-airymax/` | 5 文件（layer.conf + 3 recipes + defconfig） |
| 12 | imageTailor 配置 | `build/custom/cfg_airymax/` | 3 文件（XML + repo + grub.cfg） |
| 13 | Kickstart 脚本 | `build/ks-airymax.cfg` | 56 行 |

### 11.2 IRON-7 覆盖明细

`configs/defconfig-agent` 追加的 IRON-7 覆盖项（将 openEuler 特有扩展覆盖回 vanilla 默认值）：

- **调度器**：`# CONFIG_SCHED_STEAL is not set`、`SCHED_PARAL`、`SCHED_SOFT_QUOTA`、`SCHED_SOFT_DOMAIN`、`SCHED_CLASS_EXT`
- **内存 cgroup**：`# CONFIG_MEMCG_QOS is not set`、`MEMCG_MEMFS_INFO`、`MEMCG_OOM_PRIORITY`、`MEMCG_SWAP_QOS`、`MEMCG_KMEM_STOCK`
- **NUMA**：`# CONFIG_NUMA_AWARE_SPINLOCKS is not set`、`NUMA_EMU`、`NUMABALANCING_MEM_SAMPLING`
- **安全**：`# CONFIG_SECURITY_FEATURE_BYPASS is not set`、`# CONFIG_BPF_LSM is not set`

### 11.3 验证结果

| 验证项 | 结果 |
|--------|------|
| `make ARCH=sw_64 airy_defconfig` | ✅ 生成 .config（3851 行），CONFIG_SW64=y，CONFIG_SECURITY_AIRY=y |
| `make ARCH=x86 airy_defconfig` | ✅ 生成 .config（1369 行），CONFIG_X86_64=y，CONFIG_SECURITY_AIRY=y |
| `make ARCH=arm64 airy_defconfig` | ✅ 生成 .config（1314 行），CONFIG_ARM64=y，CONFIG_SECURITY_AIRY=y |
| `make ARCH=x86 -j$(nproc)` | ✅ 编译通过，`arch/x86/boot/bzImage is ready` |
| `grep -r '__KABI' arch/sw_64/ configs/` | ✅ 零命中 |
| `grep -r 'Makefile.oever' arch/sw_64/ configs/` | ✅ 零命中 |
| arch/sw_64/ 不触及 kernel/sched/、security/ | ✅ 验证通过 |

### 11.4 附带修复

修复 commit `1e61116e6153` ("airymax: correct sched_tac, capability MDB tree
and LSM entry symmetry") 遗留的 stale `source "config/Kconfig.alk"` 引用
——该 commit 删除了 `config/Kconfig.alk` 文件（消除与 `security/airy/Kconfig`
的重复定义）但未移除顶层 Kconfig 的 source 行，导致所有 `make *defconfig`
调用失败。本次实施中移除该 stale 引用，恢复配置生成能力。

### 11.5 提交登记

- **kernel 仓库**（ALK-6.6-dev）：`airy/arch: import sw_64 and add LAYER config fragments`（374 文件，+93636/-2）
- **agentrt-linux 管理仓**（main）：`airy/build: add LAYER build artifacts for openEuler toolchain reuse`（11 文件，+418）
- **docs-closed 仓库**（main）：本文档实施进度章节

### 11.6 后续工作

1. sw_64 交叉编译链配置（当前仅验证配置生成，未验证完整编译）
2. arm64 完整编译验证（x86 已通过）
3. `drivers/hooks/` Vendor Hooks 逐个甄别（排除触及 sched/security 的钩子）
4. OBS 多架构构建配置（`AirymaxOS:Factory:Kernel` 项目）
5. CI 门禁：编译后 `diffconfig` 验证核心子系统 CONFIG 与 vanilla 一致

---

> **文档结束** | SPHARX Ltd 内部参考 | 闭源不公开
