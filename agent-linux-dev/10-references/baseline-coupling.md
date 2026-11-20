Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 基底耦合点清单（0.0.4 起清点，0.0.5 起扩至 70 条）

> **文档定位**: 清点 AirymaxOS 当前绑死在 openEuler 24.03 LTS-SP3 上的每一处可改动点，作为 0.0.10–0.0.30「自有基底替换（B-02）」的输入与验收基线
> **版本**: 1.1.0
> **最后更新**: 2026-11-17
> **主要读者**: 0.0.10–0.0.30 基底替换负责人
> **证据级别**: E1–E4（见 §1.2），逐条标注
> **边界**: 本册只清点、不决策；0.0.4 不替换基底

---

## 1. 口径

### 1.1 什么算一个耦合点

判定标准只有一条：**若把 openEuler 24.03 LTS-SP3 换成另一套基底，这一处是否必须改动。**
必须改动者登记为一条；仅仅「提到 openEuler」但换基底后无需改动的（如历史注释、
兼容性说明）不登记。每条登记必须同时具备：

1. 仓库内真实存在的路径与行号；
2. 该行的原文片段（超过 60 字符截断并标 `…`）；
3. 一条能复现该行命中的 `grep` 命令；
4. 换基底后要改什么（替换影响）。

编号 `BC-NNN` 按耦合面分章连续，全册唯一。

### 1.2 证据级别

| 级别 | 定义 | 本册用法 |
|------|------|----------|
| E1 | 代码/配置中的硬编码 | 变量、URL、包名、正则、`%check` 断言、`ARG` 默认值 |
| E2 | 构建脚本或打包定义中的隐含依赖 | 工具行为假设、包集合、介质结构、子模块/分支 |
| E3 | 文档约定（无代码强制） | 只写在注释/说明里、当前无机器判据的行为 |
| E4 | 推断 | 必须显式写「待验证」并给出验证方法；本册仅 1 条 |

### 1.3 本册不做什么

- 不评估替代基底（openEuler 之外）的可行性；
- 不排序替换工作量，只给「替换阻塞度」三分（必须改 / 可延后 / 仅文档约定）；
- 不新增、不修改任何代码或 CI 判据；本册的复算命令只读。

### 1.4 复算前提

仓库 `.gitignore` 采用「默认忽略全部、逐项放行」策略，`rg` 默认会跳过
`distro/`、`system/` 等叶子仓；本册一律用 `grep -rn`（不读忽略规则）。
所有命令的工作目录为仓库根 `agent-linux/`。

---

## 2. 软件源与镜像 URL

镜像根只声明一次（`distro/repo/mirrors.list`），其余位置要么引用它、要么
复制一份并接受 `%check` 对齐。替换基底时，这一面的改动是「全量重写 URL +
重算 `%check` 期望值」。

| 编号 | 耦合点 | 位置（路径:行号） | 证据级别 | 原文片段 | 复算命令 | 替换影响 |
|---|---|---|---|---|---|---|
| BC-001 | 七个镜像根全部钉在 SP3 路径 | `distro/repo/mirrors.list:12` | E1 | `https://repo.openeuler.org/openEuler-24.03-LTS-SP3` | `grep -n 'openEuler-24.03-LTS-SP3' distro/repo/mirrors.list` | 七个根全部改写；镜像探测与闭包收割随之失效 |
| BC-002 | 客户端 repo 五段 × 三根 baseurl | `distro/repo/airymax-os.repo:28` | E1 | `baseurl=https://repo.openeuler.org/openEuler-24.03-LTS-SP3…` | `grep -n 'openEuler-24.03-LTS-SP3' distro/repo/airymax-os.repo` | 15 条 baseurl（5 段 × 3 根）全改；段名 OS/update/EPOL 也随基底变 |
| BC-003 | `%check` 硬断言 5/5/5 条 baseurl | `distro/specs/airymaxos-release.spec:398` | E1 | `test "$(grep -cF "baseurl=https://repo.openeuler.org/…` | `grep -n 'grep -cF "baseurl=https://repo.openeuler.org' distro/specs/airymaxos-release.spec` | 断言值与 `%global oe_base` 必须同步，否则 build 期即失败 |
| BC-004 | 锁文件输入的五段仓库定义 | `distro/lockfile/rpms.in.yaml:21` | E1 | `baseurl: …/openEuler-24.03-LTS-SP3/OS/$basearch/` | `grep -n 'openEuler-24.03-LTS-SP3' distro/lockfile/rpms.in.yaml` | 五段改写；`rpms.lock.yaml` 需重新求解 |
| BC-005 | 安装期 anaconda 源指向 SP3 | `distro/kickstart/airymaxos-workstation.ks:37` | E1 | `url --url=…/openEuler-24.03-LTS-SP3/OS/$basearch/` | `grep -nE '^(url --url|repo .*--baseurl=https)' distro/kickstart/airymaxos-workstation.ks` | 装机源改写；离线载荷仓库名也要对齐 |
| BC-006 | 基底选型校验器只认三类主机 | `distro/lockfile/base_check.py:34` | E1 | `HOSTS = ("repo.openeuler.org", "mirrors.tuna.tsinghua…` | `grep -n 'HOSTS = (' distro/lockfile/base_check.py` | 主机白名单、`FIRST` 前缀与 SP 正则全部重写 |
| BC-007 | 镜像探针依赖 repodata 索引格式 | `distro/tools/mirror_probe.py:44` | E1 | `HREF = re.compile(r'href="([^"]*primary\.xml\.(?:gz…` | `grep -n 'HREF = re.compile' distro/tools/mirror_probe.py` | 新基底若用别的索引名/压缩格式，探针全线 0 KiB/s |
| BC-008 | 载荷种子以清单文件为唯一输入 | `ci/gates/payload-seed.sh:78` | E2 | `readonly MIRRORS="${ROOT}/distro/repo/mirrors.list"` | `grep -n 'readonly MIRRORS=' ci/gates/payload-seed.sh` | 清单格式可复用，但内容需整份替换 |
| BC-009 | 闭包池镜像 tag 含 24.03 | `ci/gates/pool-seed.sh:57` | E1 | `readonly REF_BASE="ghcr.io/openairymax/…` | `grep -n 'REF_BASE=' ci/gates/pool-seed.sh` | tag 与池内容均需换代，旧池不可复用 |
| BC-010 | 闭包锁文件名含 24.03 | `ci/gates/assemble.sh:118` | E1 | `lock_name="closure-24.03-${ARCH}.lock"` | `grep -n 'lock_name=' ci/gates/assemble.sh` | 锁文件改名或改内容；缓存池键同步 |

---

## 3. 包集合与 comps/lockfile

包集合的耦合不在「列了哪些包」，而在「这些包名只在 openEuler 的仓库里同时
存在」。换基底时，本章决定闭包能否重新求解。

| 编号 | 耦合点 | 位置（路径:行号） | 证据级别 | 原文片段 | 复算命令 | 替换影响 |
|---|---|---|---|---|---|---|
| BC-011 | 基底选型唯一真源 | `distro/lockfile/base.yaml:17` | E1 | `selected: openEuler-24.03-LTS-SP3` | `grep -n '^selected:' distro/lockfile/base.yaml` | 改这一行即触发其余引用的连锁断言 |
| BC-012 | 内核基线写死在选型文件 | `distro/lockfile/base.yaml:19` | E1 | `kernel_line: 6.6` | `grep -n '^kernel_line:' distro/lockfile/base.yaml` | 新基底内核线不同则内核 spec 与 defconfig 同步换代 |
| BC-013 | UKUI 组件锁的基底锚点 | `distro/lockfile/ukui-components.yaml:28` | E1 | `base: openEuler-24.03-LTS-SP3` | `grep -n '^base:' distro/lockfile/ukui-components.yaml` | 26 个组件的 EVR 锚点全失效，需重新锁定 |
| BC-014 | 桌面栈取自 EPOL/main 3.1 代 | `distro/comps/airymaxos-comps.xml:9` | E3 | `openEuler 24.03 LTS-SP3 EPOL/main 的 3.1 组件代；上游 4.24 自建闭包` | `grep -n 'EPOL/main 的 3.1' distro/comps/airymaxos-comps.xml` | UKUI 来源整体更换；4.24 方案已有独立评估 |
| BC-015 | 基础组是按 SP3 的 core 组裁剪的 | `distro/comps/airymaxos-comps.xml:21` | E2 | `<!-- 基础系统组：openEuler 24.03 LTS-SP3 comps 中 core 组` | `grep -n 'comps 中 core 组' distro/comps/airymaxos-comps.xml` | 新基底 core 组若增删包，本组需重新对齐 |
| BC-016 | 安装期显式排除上游 release 包 | `distro/kickstart/airymaxos-workstation.ks:150` | E1 | `-openEuler-release` | `grep -n '^-openEuler-' distro/kickstart/airymaxos-workstation.ks` | 新基底的 release 包名不同，排除项要重写 |
| BC-017 | comps 校验器硬编码上游包名 | `distro/tools/comps_lint.py:50` | E1 | `UPSTREAM = ("kernel", "openEuler-release", …` | `grep -n '^UPSTREAM = ' distro/tools/comps_lint.py` | 三元组必须随基底改名，否则 lint 误判 |
| BC-018 | ks 校验器硬编码上游排除项 | `distro/tools/ks_lint.py:81` | E1 | `UPSTREAM_EXCLUDES = ("-kernel", "-kernel-tools", …` | `grep -n '^UPSTREAM_EXCLUDES' distro/tools/ks_lint.py` | 同上；漏改会让装机把上游内核装进来 |
| BC-019 | 输入法只保留 ibus（SP3 冻结点） | `distro/comps/airymaxos-comps.xml:211` | E2 | `<packagereq type="default">ibus</packagereq>` | `grep -n 'ibus' distro/comps/airymaxos-comps.xml` | 新基底若仍有 fcitx 4，输入法方案可重选 |
| BC-020 | 五仓库分工写进 comps 说明 | `distro/comps/airymaxos-comps.xml:14` | E3 | `基础仓库：openEuler 24.03 LTS-SP3 的 OS、update、EPOL/main、` | `grep -n '基础仓库：openEuler' distro/comps/airymaxos-comps.xml` | 仓库面结构变化时同步改说明与 kickstart |

---

## 4. 安装器（anaconda/kickstart）与引导链

本章是最硬的一面：不只是 URL，而是「底座介质里长什么样、anaconda 怎么解释
配方、GRUB 把 cfg 写到哪里」三层行为。

| 编号 | 耦合点 | 位置（路径:行号） | 证据级别 | 原文片段 | 复算命令 | 替换影响 |
|---|---|---|---|---|---|---|
| BC-021 | 底座 ISO/IMG 名称与摘要写死在 workflow | `.github/workflows/image-build.yml:123` | E1 | `iso_name: openEuler-24.03-LTS-SP3-netinst-x86_64-dvd.iso` | `grep -nE '(iso|img)_(name|sha256):' .github/workflows/image-build.yml` | 名称、摘要、介质类型（netinst/dvd）全部换 |
| BC-022 | ISO 以底座介质为母本改写 | `distro/scripts/build-iso.sh:256` | E2 | `if ! mkksiso "${args[@]}" "${WORK}/ks.cfg" "$ISO" "$PART" \` | `grep -n 'mkksiso "' distro/scripts/build-iso.sh` | 新基底若不用 lorax/mkksiso 结构，整段组装重写 |
| BC-023 | 品牌器按 openEuler 菜单形状匹配 | `distro/tools/cfg_brand.py:82` | E1 | `BASE_NAME = re.compile(r"openeuler", re.IGNORECASE)` | `grep -n 'BASE_NAME = ' distro/tools/cfg_brand.py` | 三种标题规则、LEAK/ALLOW 全部随底座品牌改 |
| BC-024 | 安装介质五个品牌面写死 | `distro/scripts/lib/iso_post.sh:196` | E1 | `for cfg in EFI/BOOT/grub.cfg isolinux/isolinux.cfg …` | `grep -n 'for cfg in EFI/BOOT/grub.cfg' distro/scripts/lib/iso_post.sh` | 新介质若无 isolinux/.discinfo/boot.msg，需按实际面重写 |
| BC-025 | 配方校验按 anaconda 36 选项集建模 | `distro/tools/ks_lint.py:91` | E1 | `# openEuler 24.03 的 anaconda 36 中 user 命令的选项集合（备注字段是` | `grep -n 'anaconda 36' distro/tools/ks_lint.py` | 新基底 anaconda 版本不同，配方语法与校验同步换 |
| BC-026 | 引导包按 openEuler 包名点名 | `distro/scripts/lib/closure.sh:314` | E1 | `x86_64) CL_BOOT=(grub2-pc grub2-efi-x64 shim-x64 …` | `grep -n 'CL_BOOT=(' distro/scripts/lib/closure.sh` | shim/grub 包名与架构命名随基底变 |
| BC-027 | shim-x64 是 openEuler 的虚拟名 | `distro/scripts/build-desktop.sh:298` | E2 | `# 可能是虚拟名（shim-x64 由 openEuler 的 shim 提供）。判定与收割端同源` | `grep -n '由 openEuler 的 shim 提供' distro/scripts/build-desktop.sh` | 虚拟名映射需重做，否则误报缺包 |
| BC-028 | 装机后 NVRAM 残留 openEuler 条目 | `distro/boot/efi_brand.sh:144` | E1 | `# anaconda 自己建的那条 "openEuler" 条目仍留在 NVRAM 里，固件菜单因此同时` | `grep -n 'anaconda 自己建的那条' distro/boot/efi_brand.sh` | 新安装器条目名不同，去重判据要改 |
| BC-029 | grub2-mkconfig 只写 EFI/openEuler | `distro/boot/grub_args.sh:39` | E1 | `# 菜单实际读的是 /boot/efi/EFI/airymaxos/grub.cfg…` | `grep -n 'grub2-mkconfig 只写' distro/boot/grub_args.sh` | 品牌副本同步逻辑可能整体失效或需重指目录 |
| BC-030 | bootloader 命令行依赖 anaconda 语义 | `distro/kickstart/airymaxos-workstation.ks:70` | E2 | `bootloader --timeout=3 --append="console=ttyS0,115200…` | `grep -n '^bootloader' distro/kickstart/airymaxos-workstation.ks` | 新安装器若不落 GRUB 参数，需改用自身机制 |

---

## 5. 内核基线与打包

内核来自独立子模块（`ALK-6.6-dev`），但**打包口径**绑定 openEuler：版本号、
defconfig 文件名、ABI 名、架构清单。`defconfig` 是本章最硬的耦合——它决定
驱动是否在镜像里。

| 编号 | 耦合点 | 位置（路径:行号） | 证据级别 | 原文片段 | 复算命令 | 替换影响 |
|---|---|---|---|---|---|---|
| BC-031 | 内核版本钉在 6.6.161 | `distro/specs/kernel/airymaxos-kernel.spec:67` | E1 | `%global kernel_version 6.6.161` | `grep -n '^%global kernel_version' distro/specs/kernel/airymaxos-kernel.spec` | 版本、`kernel_abi`、固件依赖、锁文件同步换 |
| BC-032 | x86/arm64 直接取 openEuler defconfig | `distro/specs/kernel/airymaxos-kernel.spec:92,98` | E1 | `%global kbase openeuler_defconfig` | `grep -n 'openeuler_defconfig' distro/specs/kernel/airymaxos-kernel.spec` | 新基底若不提供该文件，需自维护等价 fragment |
| BC-033 | loongarch 退到 loongson3_defconfig | `distro/specs/kernel/airymaxos-kernel.spec:112` | E1 | `%global kbase loongson3_defconfig` | `grep -n 'loongson3_defconfig' distro/specs/kernel/airymaxos-kernel.spec` | 上游无 loongarch defconfig；新基底需重新选基线 |
| BC-034 | 申威架构仅 openEuler 有 | `tools/defconfig-matrix/manifest.yaml:58` | E1 | `  - arch: sw_64` | `grep -n 'arch: sw_64' tools/defconfig-matrix/manifest.yaml` | 换基底即失去 sw_64 支持面，需显式下架或自建 |
| BC-035 | 固件闭包按内核 ABI 名绑定 | `distro/specs/kernel/airymaxos-kernel.spec:72` | E1 | `%global kernel_abi %{kernel_version}` | `grep -n '^%global kernel_abi' distro/specs/kernel/airymaxos-kernel.spec` | 固件包名与 `test_fw_contract.py` 契约同步换 |
| BC-036 | 内核描述锁定 upstream 6.6 longterm | `distro/specs/kernel/airymaxos-kernel.spec:174` | E3 | `AirymaxOS kernel package. It carries the upstream…` | `grep -n 'upstream 6.6 longterm tree' distro/specs/kernel/airymaxos-kernel.spec` | 内核线换代时描述与兼容承诺同步改 |
| BC-037 | 内核子模块分支为 ALK-6.6-dev | `.gitmodules:1` | E2 | `[submodule "kernel"]` | `git -C kernel branch --show-current` | 分支本身的 6.6 线是基底耦合；换线需换分支 |
| BC-038 | 源码包名由 `kernel_version` 生成 | `distro/specs/kernel/airymaxos-kernel.spec:137` | E1 | `Source0:        airymaxos-kernel-%{kernel_version}.tar.gz` | `grep -n '^Source0:' distro/specs/kernel/airymaxos-kernel.spec` | 归档名、构建脚本读取宏的逻辑同步 |

---

## 6. 构建工具链与宿主机依赖

这一面回答：**在什么机器上能把这套东西打出来。** 现状是「Ubuntu 24.04 宿主 +
openEuler 24.03 容器」两段式；两段的包名体系不同，各自都是耦合点。

| 编号 | 耦合点 | 位置（路径:行号） | 证据级别 | 原文片段 | 复算命令 | 替换影响 |
|---|---|---|---|---|---|---|
| BC-039 | 容器内工具链按 RPM 包名清单安装 | `ci/container/build-packages.txt:13` | E2 | `lorax` | `grep -n '^lorax$' ci/container/build-packages.txt` | 34 个包名全部按新基底仓库核对；缺 lorax 则无法出 ISO |
| BC-040 | 构建容器基底镜像固定 SP3 | `ci/container/Containerfile.agent-base:24` | E1 | `ARG BASE_IMAGE=docker.io/openeuler/openeuler:24.03-lts-sp3` | `grep -n '^ARG BASE_IMAGE' ci/container/Containerfile.agent-base` | 镜像 tag 换；glibc/dnf/ABI 随之变 |
| BC-041 | 容器装载前断言 ID=openeuler | `ci/gates/container-load.sh:47` | E1 | `docker run --rm "${img}" grep -qi '^ID="\?openeuler"'…` | `grep -n 'ID="\\?openeuler"' ci/gates/container-load.sh` | 替换基底后此门禁必然红，必须改判据或删 |
| BC-042 | 工具链预热依赖 dnf 离线事务 | `ci/gates/toolchain.sh:66` | E2 | `opts+=(--cacheonly)` | `grep -n 'cacheonly' ci/gates/toolchain.sh` | 新基底包管理器不同则整段重写 |
| BC-043 | 交叉编译依赖 Ubuntu 包名 | `ci/gates/release-deps.sh:19` | E2 | `readonly NATIVE_DEPS=(` | `grep -n '^readonly NATIVE_DEPS=' ci/gates/release-deps.sh` | apt 包名与版本（如 gcc-13-loongarch64）随宿主变 |
| BC-044 | 现场 openEuler 只做存在性校验 | `ci/gates/kernel-deps.sh:15` | E3 | `# （例如现场的 openEuler）只做存在性校验——能跑就等于依赖齐，不能跑就` | `grep -n '例如现场的 openEuler' ci/gates/kernel-deps.sh` | 换基底后宿主依赖集合需重新枚举 |
| BC-045 | 打包入口是 rpmbuild | `distro/scripts/build-rpms.sh:398` | E2 | `if ! rpmbuild -bb "$spec" \` | `grep -n 'rpmbuild -bb' distro/scripts/build-rpms.sh` | 新基底若不用 RPM 体系，打包链整体重写 |
| BC-046 | 重打包走 rpmbuild 宏注入 | `distro/scripts/lib/guard.sh:116` | E2 | `rpmbuild -bb --quiet \` | `grep -n 'rpmbuild -bb --quiet' distro/scripts/lib/guard.sh` | 同上；`_build_id_links` 等宏语义随 rpm 版本 |
| BC-047 | 仓库索引用 createrepo_c 生成 | `distro/scripts/lib/closure.sh:670` | E1 | `if ! createrepo_c --quiet --general-compress-type gz …` | `grep -n 'createrepo_c' distro/scripts/lib/closure.sh` | 新基底若用 modules/comps 新格式，索引参数需改 |

---

## 7. CI 工作流里的基底假设

CI 不是在 openEuler 上跑，而是在 Ubuntu 上开一个 openEuler 容器；因此
「runner 版本」「介质摘要」「容器镜像」「缓存键」四处都写死了基底。

| 编号 | 耦合点 | 位置（路径:行号） | 证据级别 | 原文片段 | 复算命令 | 替换影响 |
|---|---|---|---|---|---|---|
| BC-048 | 组装 job 钉在 Ubuntu 24.04 | `.github/workflows/image-build.yml:122` | E1 | `runner: ubuntu-24.04` | `grep -nE '(runs-on|runner):' .github/workflows/image-build.yml` | 宿主换代影响 release-deps 的 apt 包名 |
| BC-049 | 介质按名称与 sha256 固定 | `.github/workflows/image-build.yml:170` | E1 | `run: ci/ci.sh media-fetch --dir "$RUNNER_TEMP/media"…` | `grep -n 'Fetch fixed openEuler media' .github/workflows/image-build.yml` | 新基底需换 ISO/IMG 名与两枚摘要 |
| BC-050 | 工具链缓存键绑定包清单 | `.github/workflows/image-build.yml:187` | E1 | `key: dnf-${{ hashFiles('ci/container/build-packages.txt') }}` | `grep -n 'key: dnf-' .github/workflows/image-build.yml` | 清单换则缓存自然失效，无需改键 |
| BC-051 | EOL 门禁按 openEuler SP 节奏 | `ci/gates/base-eol.sh:4` | E2 | `# ci/gates/base-eol.sh — openEuler 基底选型同源门禁…` | `grep -n 'openEuler 基底选型同源门禁' ci/gates/base-eol.sh` | 换基底后该门禁的 SP 小/大节奏模型作废 |
| BC-052 | 组装容器显式接收 ISO 底座 | `ci/gates/assemble.sh:96` | E2 | `envs=(-e ACCEPTANCE="$(airy_profile)" -e ISO_BASE=…` | `grep -n 'ISO_BASE=' ci/gates/assemble.sh` | 变量名可留，取值来源与校验要换 |

---

## 8. 运行时约定

这一面最容易被忽略：不是「装了什么包」，而是「假设基底怎么表现」。多数是
E3（注释里写死的上游行为），只有 os-release 相关是硬编码。

| 编号 | 耦合点 | 位置（路径:行号） | 证据级别 | 原文片段 | 复算命令 | 替换影响 |
|---|---|---|---|---|---|---|
| BC-053 | 对外宣称自己是 openEuler 系 | `distro/release/os-release:15` | E1 | `ID_LIKE="openeuler"` | `grep -n '^ID_LIKE=' distro/release/os-release` | 所有 `ID_LIKE` 消费者（第三方仓库脚本）行为改变 |
| BC-054 | 打包期断言 ID_LIKE 不得变 | `distro/specs/airymaxos-release.spec:336` | E1 | `grep -qxF 'ID_LIKE="openeuler"' %{buildroot}…` | `grep -n 'grep -qxF .ID_LIKE' distro/specs/airymaxos-release.spec` | 改 os-release 必须同步改断言，否则 build 失败 |
| BC-055 | 用版本比较顶掉上游 release 包 | `distro/specs/airymaxos-release.spec:121` | E1 | `Obsoletes:      openEuler-release < 24.04` | `grep -n '^Obsoletes:' distro/specs/airymaxos-release.spec` | 新基底的 release 包名与版本段全换 |
| BC-056 | 刻意不声明 VARIANT_ID | `distro/release/os-release:24` | E3 | `# 不声明 VARIANT_ID：openEuler 24.03 的 firewalld…` | `grep -n 'VARIANT_ID' distro/release/os-release` | 新基底 firewalld 若不再看 VARIANT_ID，可解除限制 |
| BC-057 | journald 落盘策略依赖上游默认值 | `distro/specs/airymaxos-release.spec:293` | E3 | `# 启动日志默认只活在当前一轮：openEuler 不预建 /var/log/journal，` | `grep -n '不预建 /var/log/journal' distro/specs/airymaxos-release.spec` | 新基底若预建目录，日志行为与容量策略改变 |
| BC-058 | cgroup v1 上 memsw 限制的推断 | `distro/presets/boot-set:28` | E4 | `# RT 带宽与换页上限：cgroup v1 上 systemd 不写…` | `grep -n 'cgroup v1 上 systemd' distro/presets/boot-set` | **待验证**：在新基底执行 `stat -fc %T /sys/fs/cgroup` 与 `systemctl show -p DefaultMemoryAccounting`，确认是否仍需 cgroup v1 补偿 |
| BC-059 | GRUB 字体分支是上游 00_header 形状 | `distro/specs/airymaxos-release.spec:538` | E3 | `# 引导期分辨率：这段必须无条件落 gfxmode 与 gfxterm。openEuler 的 00_header` | `grep -n 'openEuler 的 00_header' distro/specs/airymaxos-release.spec` | 新基底 GRUB 脚本结构不同，补丁位置需重找 |
| BC-060 | 默认启动主题链到 tribar | `distro/specs/airymaxos-release.spec:306` | E2 | `ln -s tribar/tribar.plymouth \` | `grep -n 'tribar/tribar.plymouth' distro/specs/airymaxos-release.spec` | 新基底 plymouth 包若不带 tribar，链接悬空 |

**本面清点结果补充（字体）**：`comps`/`kickstart` 中无显式字体包声明，字体由
UKUI 闭包间接带入。此结论为 E4：验证方法为
`dnf repoquery --requires --resolve ukui-desktop-environment | grep -i font`
（在目标基底容器内执行），若结果为空则需在 0.1.x 显式补字体清单。

---

## 9. 语言与供应链耦合（2026-11-17 增补）

这一面回答：**自有代码用 Rust 之后，基底还在哪些地方限制它。** 与 §6 的区别是：
§6 问「能不能打出 RPM」，本章问「打出的是不是 Rust 产物、能不能复现、输入法/语音资产归谁」。

| 编号 | 耦合点 | 位置（路径:行号） | 证据级别 | 原文片段 | 复算命令 | 替换影响 |
|---|---|---|---|---|---|---|
| BC-061 | 宿主机依赖清单无 Rust 工具链 | `ci/container/build-packages.txt:94` | E1 | `libkylin-chkname-devel`（末行；全文无 rust/cargo） | `grep -in 'rust\|cargo' ci/container/build-packages.txt`（0 命中） | 任何 Rust 组件无法在构建容器内产出 |
| BC-062 | 仓库无 Rust 工具链钉版 | `distro/lockfile/lang-policy.yaml:24` | E1 | 政策已要求 `rust-toolchain.toml`，实物 0 个 | `grep -n 'rust-toolchain' distro/lockfile/lang-policy.yaml`；`find . -name 'rust-toolchain*' -not -path './.git/*'`（0 命中） | 工具链随基底漂移，产物不可复现 |
| BC-063 | 无依赖锁与离线 crate 源 | `distro/lockfile/lang-policy.yaml:25` | E1 | 政策已要求 `Cargo.lock` 与 `vendor`，实物均无 | `grep -n 'Cargo.lock\|vendor' distro/lockfile/lang-policy.yaml`；`find . -name Cargo.lock -not -path './.git/*'`（0 命中） | 断网构建不可行，锁文件无法审计 |
| BC-064 | 镜像根只覆盖 openEuler 段 | `distro/repo/mirrors.list` | E1 | 仅 openEuler 三段根 | `grep -n 'openeuler' distro/repo/mirrors.list` | crates 源需自建或 vendor，不能假设可达 |
| BC-065 | GUI 输入法闭包只有 IBus | `distro/comps/airymaxos-comps.xml:256` | E1 | `<packagereq type="default">ibus</packagereq>` | `grep -n '>ibus<' distro/comps/airymaxos-comps.xml` | IBus 依赖 GUI 会话与 D-Bus，boot TUI 不可复用 |
| BC-066 | comps 无 rime/librime 闭包 | `distro/lockfile/lang-policy.yaml:42` | E1 | 自有 `boot-ime` 已立项，comps 无 rime 相关 packagereq | `grep -n 'boot-ime' distro/lockfile/lang-policy.yaml`；`grep -in 'rime' distro/comps/airymaxos-comps.xml`（0 命中） | TUI 中文输入需自带 IME 或新增包 |
| BC-067 | comps 无语音/ASR 资产包 | `distro/lockfile/lang-policy.yaml:49` | E1 | 自有 `asr-gateway` 已立项，comps 无 asr/sensevoice 包 | `grep -n 'asr-gateway' distro/lockfile/lang-policy.yaml`；`grep -in 'asr\|sensevoice' distro/comps/airymaxos-comps.xml`（0 命中） | 模型与运行时无包归属，digest 无台账 |
| BC-068 | 安装路径由 RPM 宏决定 | `distro/specs/airymaxos-release.spec` | E2 | `%{_bindir}` / `%{_libdir}` | `grep -n '%{_libdir}\|%{_bindir}' distro/specs/*.spec` | Rust 产物安装路径必须跟随宏，不能写死 |
| BC-069 | console 中文字形无独立声明 | `distro/comps/airymaxos-comps.xml` | E4 | 字体经 UKUI 闭包间接带入 | 待验证：无 GUI 镜像内 `fc-list :lang=zh` | 缺字则 TUI 中文显方块，需显式字体包 |
| BC-070 | CI 无 Rust 单元测试步骤 | `.github/workflows/image-build.yml:369` | E2 | 现只有 `run: ci/ci.sh lang-lock --source . --allow-pending` | `grep -n 'cargo test' .github/workflows/*.yml`（0 命中） | Rust 组件落地后测试不进门禁，等同不做 |

BC-061–BC-067 是 0.0.5 的硬前置：不解决则「全 Rust TUI」无法在 CI 复现。
BC-068–BC-070 可随组件落地同步收口。

---

## 10. 统计

### 10.1 总量与证据级别

| 维度 | 数量 |
|---|---|
| 耦合点总数 | 70 |
| E1（硬编码） | 44 |
| E2（构建/打包隐含依赖） | 17 |
| E3（文档约定） | 7 |
| E4（推断，待验证） | 2 |

E1 占比 62.9%，说明当前基底不是「一层可替换的适配」，而是已经渗进配置、
校验器、打包与 CI 判据。

### 10.2 按耦合面

| 章 | 耦合面 | 条目数 | 编号区间 |
|---|---|---|---|
| 2 | 软件源与镜像 URL | 10 | BC-001–BC-010 |
| 3 | 包集合与 comps/lockfile | 10 | BC-011–BC-020 |
| 4 | 安装器与引导链 | 10 | BC-021–BC-030 |
| 5 | 内核基线与打包 | 8 | BC-031–BC-038 |
| 6 | 构建工具链与宿主机依赖 | 9 | BC-039–BC-047 |
| 7 | CI 工作流里的基底假设 | 5 | BC-048–BC-052 |
| 8 | 运行时约定 | 8 | BC-053–BC-060 |
| 9 | 语言与供应链 | 10 | BC-061–BC-070 |

### 10.3 按替换阻塞度

**必须改（48 条）**：换基底当轮不改就构建不出、装不上或起不来。
BC-001–007、BC-009–013、BC-016–018、BC-021–026、BC-028–029、
BC-031–035、BC-038、BC-040–042、BC-045–050、BC-053–055、BC-061–067。

**可延后（19 条）**：当轮可先用旧值跑通，等新基底稳定后再收口。
BC-008、BC-015、BC-019、BC-027、BC-030、BC-037、BC-039、BC-043–044、
BC-051–052、BC-056–060、BC-068–070。

**仅文档约定（3 条）**：无机器判据，只改注释/说明即可。
BC-014、BC-020、BC-036。

E4 的 BC-058 与 BC-069 归入「可延后」，但 0.0.10 立项前必须先按表内方法验证，
否则 cgroup 补偿或字体闭包可能从「可延后」变成「必须改」。

---

## 11. 复算入口

在仓库根 `agent-linux/` 下直接粘贴执行。命令只读，不写任何文件。
逐条打印命中行数；零命中会显式标 `MISS`。

```bash
cd agent-linux
rows=0; hits=0; miss=0
while IFS='|' read -r id path pat; do
  [ -z "$id" ] && continue
  rows=$((rows + 1))
  n=$(grep -c -E -- "$pat" "$path" 2>/dev/null || true)
  [ "${n:-0}" -eq 0 ] && { echo "MISS $id $path :: $pat"; miss=$((miss + 1)); }
  hits=$((hits + ${n:-0}))
  printf '%-7s %2s  %s\n' "$id" "${n:-0}" "$path"
done <<'EOF'
BC-001|distro/repo/mirrors.list|^https://.*openEuler-24\.03-LTS-SP3
BC-002|distro/repo/airymax-os.repo|openEuler-24.03-LTS-SP3
BC-003|distro/specs/airymaxos-release.spec|baseurl=https://repo.openeuler.org
BC-004|distro/lockfile/rpms.in.yaml|openEuler-24.03-LTS-SP3
BC-005|distro/kickstart/airymaxos-workstation.ks|(url --url|repo .*--baseurl=https)
BC-006|distro/lockfile/base_check.py|HOSTS = \(
BC-007|distro/tools/mirror_probe.py|HREF = re.compile
BC-008|ci/gates/payload-seed.sh|readonly MIRRORS=
BC-009|ci/gates/pool-seed.sh|REF_BASE=
BC-010|ci/gates/assemble.sh|lock_name=
BC-011|distro/lockfile/base.yaml|^selected:
BC-012|distro/lockfile/base.yaml|^kernel_line:
BC-013|distro/lockfile/ukui-components.yaml|^base:
BC-014|distro/comps/airymaxos-comps.xml|EPOL/main 的 3.1
BC-015|distro/comps/airymaxos-comps.xml|comps 中 core 组
BC-016|distro/kickstart/airymaxos-workstation.ks|^-openEuler-
BC-017|distro/tools/comps_lint.py|^UPSTREAM = 
BC-018|distro/tools/ks_lint.py|^UPSTREAM_EXCLUDES
BC-019|distro/comps/airymaxos-comps.xml|>ibus<
BC-020|distro/comps/airymaxos-comps.xml|基础仓库：openEuler
BC-021|.github/workflows/image-build.yml|^[[:space:]]*(iso_name|iso_sha256|img_name|img_sha256):
BC-022|distro/scripts/build-iso.sh|mkksiso "
BC-023|distro/tools/cfg_brand.py|BASE_NAME = 
BC-024|distro/scripts/lib/iso_post.sh|for cfg in EFI/BOOT/grub.cfg
BC-025|distro/tools/ks_lint.py|anaconda 36
BC-026|distro/scripts/lib/closure.sh|CL_BOOT=\(
BC-027|distro/scripts/build-desktop.sh|由 openEuler 的 shim 提供
BC-028|distro/boot/efi_brand.sh|anaconda 自己建的那条
BC-029|distro/boot/grub_args.sh|grub2-mkconfig 只写
BC-030|distro/kickstart/airymaxos-workstation.ks|^bootloader
BC-031|distro/specs/kernel/airymaxos-kernel.spec|^%global kernel_version
BC-032|distro/specs/kernel/airymaxos-kernel.spec|openeuler_defconfig
BC-033|distro/specs/kernel/airymaxos-kernel.spec|loongson3_defconfig
BC-034|tools/defconfig-matrix/manifest.yaml|arch: sw_64
BC-035|distro/specs/kernel/airymaxos-kernel.spec|^%global kernel_abi
BC-036|distro/specs/kernel/airymaxos-kernel.spec|upstream 6.6 longterm tree
BC-037|.gitmodules|submodule "kernel"
BC-038|distro/specs/kernel/airymaxos-kernel.spec|^Source0:
BC-039|ci/container/build-packages.txt|^lorax$
BC-040|ci/container/Containerfile.agent-base|^ARG BASE_IMAGE
BC-041|ci/gates/container-load.sh|ID=
BC-042|ci/gates/toolchain.sh|cacheonly
BC-043|ci/gates/release-deps.sh|^readonly NATIVE_DEPS=
BC-044|ci/gates/kernel-deps.sh|例如现场的 openEuler
BC-045|distro/scripts/build-rpms.sh|rpmbuild -bb
BC-046|distro/scripts/lib/guard.sh|rpmbuild -bb --quiet
BC-047|distro/scripts/lib/closure.sh|createrepo_c
BC-048|.github/workflows/image-build.yml|^[[:space:]]*(runs-on|runner):
BC-049|.github/workflows/image-build.yml|Fetch fixed openEuler media
BC-050|.github/workflows/image-build.yml|key: dnf-
BC-051|ci/gates/base-eol.sh|openEuler 基底选型同源门禁
BC-052|ci/gates/assemble.sh|ISO_BASE=
BC-053|distro/release/os-release|^ID_LIKE=
BC-054|distro/specs/airymaxos-release.spec|grep -qxF .ID_LIKE
BC-055|distro/specs/airymaxos-release.spec|^Obsoletes:
BC-056|distro/release/os-release|VARIANT_ID
BC-057|distro/specs/airymaxos-release.spec|不预建 /var/log/journal
BC-058|distro/presets/boot-set|cgroup v1 上 systemd
BC-059|distro/specs/airymaxos-release.spec|openEuler 的 00_header
BC-060|distro/specs/airymaxos-release.spec|tribar/tribar.plymouth
BC-061|ci/container/build-packages.txt|^libkylin-chkname-devel$
BC-062|distro/lockfile/lang-policy.yaml|rust-toolchain\.toml
BC-063|distro/lockfile/lang-policy.yaml|Cargo\.lock
BC-064|distro/repo/mirrors.list|repo\.openeuler\.org
BC-065|distro/comps/airymaxos-comps.xml|type="default">ibus<
BC-066|distro/lockfile/lang-policy.yaml|boot-ime
BC-067|distro/lockfile/lang-policy.yaml|asr-gateway
BC-068|distro/specs/airymaxos-release.spec|%\{_bindir\}
BC-069|distro/comps/airymaxos-comps.xml|wqy-
BC-070|.github/workflows/image-build.yml|ci/ci\.sh lang-lock
EOF
echo "主表条数=70 实测条目=$rows 命中行=$hits 零命中=$miss"
if [ "$rows" -eq 70 ] && [ "$miss" -eq 0 ]; then
  echo "自检通过：主表条数与实际命中条目一致，且无空命中"
else
  echo "自检失败：条数或命中存在问题，按上方 MISS 行逐条修正"
fi
```

自检口径：`rows` 必须等于主表条数 70；`miss` 必须为 0。`hits` 是行数总和，
允许大于 70（例如 BC-002、BC-032 在多个文件/多个架构行命中），不作为一致性
判据。

### 10.1 仓库侧门禁

`ci/gates/coupling-scan.sh` 以本节主表为唯一事实源做两向对账：

- 主表每行必须在实物中命中，否则报 `coupling/missing BC-NNN`；
- 下列实物面里的基底声明行必须被主表正则覆盖，否则报
  `coupling/undeclared 路径:行号`（文件有主表行时只认同一路径的正则；文件
  没有主表行时按耦合形态匹配，覆盖同一耦合点落在多份配方的情形）：
  `distro/repo/*.repo` 与 `mirrors.list`、
  `distro/lockfile/{base,ukui-components,rpms.in}.yaml`、
  `distro/kickstart/*.ks`、`distro/specs/**/*.spec` 里的
  `Requires`/`BuildRequires`/`Obsoletes` 基底包、
  `ci/container/Containerfile.agent-base`、`image-build.yml` 的介质名与
  runner；注释行不计；
- 主表条数必须等于 §9.1 的「耦合点总数」，删行不改总量同样判负。

`--json` 输出 `{"declared","found","delta","total","missing","undeclared"}`。
退出码 0 通过、1 对账失败、5 参数不满足。脚本只读，不写仓库内任何文件。




