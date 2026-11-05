# UKUI 版本线取证与差异清单（R1-10 / UK-01）

> 版本: 1.0.0
> 取证日期: 2026-11-02
> 证据级别: E1（基底仓库 repodata 实测，可复算）
> 唯一事实源: `agent-linux/distro/lockfile/ukui-components.yaml`

---

## 1. 结论

0.0.4 的 UKUI 取 **openEuler 24.03 LTS-SP3 EPOL/main 的 3.1 组件代**。
该结论只由仓库解析结果支撑：OS、update、EPOL/main、EPOL/update/main、
everything 五段 repodata 中，UKUI 二进制包仅存在于 EPOL/main；OS、update、
EPOL/update/main、everything 四段为零条。

包名存在性与选型分三态登记（`distro/lockfile/ukui-components.yaml`）：

| 包名 | 实测 | 本版处置 |
|---|---|---|
| `ukui` | EPOL/main 有 `0:2.0.2-20.oe2403sp3` | available，不选 |
| `ukui-desktop-environment` | EPOL/main 有 `0:2.0.2-20.oe2403sp3` | available，不选 |
| `ukui-shell` | 五段均无 | absent，壳层由 `ukui-kwin` 承担 |

两个元包拉的是整代闭包，与本版逐组件钉版的口径冲突：选元包等于把版本
决定权交回仓库，NVRA 台账随即失效。故二者只作存在性取证，不进 comps，
也不进冻结输入。

历史记载勘误：早期文档把 `ukui`、`ukui-desktop-environment` 记作
「基底不存在」，与 2026-11-02 的 repodata 实测不符；以本文件与台账为准。
禁止用上游发布公告替代实测（J-35）。

---

## 2. 段位分布（24.03 LTS-SP3，x86_64）

| 段 | `ukui*` 条数 | 说明 |
|---|---|---|
| `OS` | 0 | 基础仓库不含桌面组件 |
| `update` | 0 | 勘误段不含 |
| `EPOL/main` | 74 | 全部 UKUI 组件与子包、debuginfo/debugsource |
| `EPOL/update/main` | 0 | 勘误段不含 |
| `everything` | 0 | 兜底仓库不含 |

74 条中组件级包 26 个：台账 24 个 present 项，
另有 `ukui`、`ukui-desktop-environment` 两个 available 元包。
present 项里 `libpam-biometric` 与 `libqt5-ukui-style1` 不带 `ukui` 前缀，
故 74 条 `ukui*` 之外单列，见 §5.2。
其余为 `debuginfo`、`debugsource` 与 `-common`、`-data`、`-devel`、
`-wayland`、`-x11`、`-systemdbus`、`-tcp-search-plugin` 等子包。
子包版本随主包，不单独钉。

---

## 3. 组件 NVRA（24.03 LTS-SP3，逐字）

| 组件 | NVRA |
|---|---|
| `ukui-kwin` | `ukui-kwin-0:1.0.5-8.oe2403sp3.x86_64` |
| `ukui-panel` | `ukui-panel-0:3.1.0-14.oe2403sp3.x86_64` |
| `ukui-session-manager` | `ukui-session-manager-0:3.1.0-7.oe2403sp3.x86_64` |
| `ukui-control-center` | `ukui-control-center-0:3.1.2-33.oe2403sp3.x86_64` |
| `ukui-settings-daemon` | `ukui-settings-daemon-0:3.1.2-9.oe2403sp3.x86_64` |
| `ukui-greeter` | `ukui-greeter-0:3.1.2-12.oe2403sp3.x86_64` |
| `ukui-themes` | `ukui-themes-0:3.0.2-2.oe2403sp3.x86_64` |
| `ukui-screensaver` | `ukui-screensaver-0:3.1.1-8.oe2403sp3.x86_64` |
| `ukui-menu` | `ukui-menu-0:3.1.1-14.oe2403sp3.x86_64` |
| `ukui-sidebar` | `ukui-sidebar-0:3.3.0-5.oe2403sp3.x86_64` |
| `ukui-notification-daemon` | `ukui-notification-daemon-0:3.3.1-7.oe2403sp3.x86_64` |
| `ukui-search` | `ukui-search-0:3.1-5.oe2403sp3.x86_64` |
| `ukui-media` | `ukui-media-0:3.1.0-5.oe2403sp3.x86_64` |
| `ukui-power-manager` | `ukui-power-manager-0:3.1.2-6.oe2403sp3.x86_64` |
| `ukui-bluetooth` | `ukui-bluetooth-0:1.0.3-5.oe2403sp3.x86_64` |
| `ukui-clock` | `ukui-clock-0:3.1.3-3.oe2403sp3.x86_64` |
| `ukui-notebook` | `ukui-notebook-0:3.1.1-1.oe2403sp3.x86_64` |
| `ukui-system-monitor` | `ukui-system-monitor-0:3.1.2-5.oe2403sp3.x86_64` |
| `ukui-window-switch` | `ukui-window-switch-0:3.1.0-2.oe2403sp3.x86_64` |
| `ukui-biometric-manager` | `ukui-biometric-manager-0:3.1.2-5.oe2403sp3.x86_64` |
| `libpam-biometric` | `libpam-biometric-0:1.2.4-2.oe2403sp3.x86_64` |
| `ukui-polkit` | `ukui-polkit-0:1.2.4-2.oe2403sp3.x86_64` |
| `ukui-interface` | `ukui-interface-0:1.0.3-3.oe2403sp3.x86_64` |
| `libqt5-ukui-style1` | `libqt5-ukui-style1-0:3.1.4-2.oe2403sp3.x86_64` |

`ukui-biometric-auth` 只是源包名：该源码构建出的二进制是 `ukui-polkit`
与 `libpam-biometric`，五段 repodata 中没有同名二进制，闭包只能登记后者。

`libqt5-ukui-style1` 由源包 `qt5-ukui-platformtheme` 构建，是 UKUI 的 Qt
风格库。`ukui-panel`、`ukui-kwin`、`ukui-settings-daemon` 均在运行时按名
加载它，却都没有声明这条依赖，闭包求解因此不会带入；`repoquery
--whatrequires` 只回 `-dev`、`qt5-styles-ukui`、`qt5-ukui-platformtheme`
三个同样不在本版闭包的子包。2026-11-05 在 285H 用同一 chroot 做加减对照
闭环：装回此包面板存活，移除后立即在 `CustomStyle` 构造期 SIGSEGV。
该包不带 `ukui` 前缀，闭包校验只看命名空间会漏判，故逐字登记。

`ukui-wallpapers-0:20.04.4-4.oe2403sp3` 只作媒体资产来源，按 R1-15 的
`ukui-wallpapers.yaml` 排除在安装闭包之外，不计入组件台账。

---

## 4. 版本线差异矩阵（epoch:version-release）

| 版本线 | `ukui-kwin` | `ukui-panel` | `ukui-session-manager` | `ukui-control-center` |
|---|---|---|---|---|
| 24.03-LTS | 0:1.0.5-7 | 0:3.1.0-14 | 0:3.1.0-7 | 0:3.1.2-30 |
| 24.03-LTS-SP1 | 0:1.0.5-8 | 0:3.1.0-14 | 0:3.1.0-7 | 0:3.1.2-33 |
| 24.03-LTS-SP2 | 0:1.0.5-8 | 0:3.1.0-14 | 0:3.1.0-7 | 0:3.1.2-33 |
| 24.03-LTS-SP3 | 0:1.0.5-8 | 0:3.1.0-14 | 0:3.1.0-7 | 0:3.1.2-33 |
| 24.03-LTS-SP4 | 0:1.0.5-8 | 0:3.1.0-14 | 0:3.1.0-7 | 0:3.1.2-34 |
| 24.09 | 0:5.24.4-1 | 0:4.0.0.0-2 | 0:4.0.0.0-4 | 0:3.22.1.25-3 |
| 25.03 | 0:5.24.4-3 | 0:4.0.0.0-4 | 0:4.0.0.0-5 | 0:3.22.1.25-3 |
| 25.09 | 0:5.24.4-5 | 0:4.10.4.3-2 | 0:4.0.0.0-7 | 0:4.10.0.0-2 |

读法：

- 24.03 LTS 全条线的控制中心停在 3.1.2，面板 3.1.0，会话 3.1.0，
  窗管 1.0.5；SP4 只把控制中心推进一个编译号（-33 → -34）。
- 24.03-LTS 首发线的控制中心在 `EPOL/update/main` 有 3.1.2-31，
  其余版本段以 `EPOL/main` 为准；段优先级按 `rpms.in.yaml` 的 cost。
- 24.09 起组件代前进到 4.0，25.09 出现 4.10，但**任何一条线都没有
  4.2x**，也没有 `ukui-shell`。4.0/4.10 不等于 4.24，不能据此声称追新完成。

---

## 5. 复算

### 5.1 dnf（有 dnf 的构建环境）

```sh
base=https://repo.openeuler.org/openEuler-24.03-LTS-SP3
dnf -q repoquery \
    --repofrompath=epol,${base}/EPOL/main/x86_64/ \
    --repo=epol --disablerepo='*' \
    --qf '%{name}-%{epoch}:%{version}-%{release}.%{arch}\n' 'ukui-*' |
    sort
```

对 `OS`、`update`、`EPOL/update/main`、`everything` 四段重复同一命令，
应得到零行。版本线矩阵把 `${base}` 换成对应版本的目录名即可。

### 5.2 repodata 直读（无 dnf 的取证机）

1. 取 `…/repodata/repomd.xml`，找 `type="primary"` 的 `location href`；
2. 该文件是 `.xml.zst` 或 `.xml.gz`，解压后迭代
   `{http://linux.duke.edu/metadata/common}package`；
3. 取 `name` 以 `ukui` 开头、`arch=x86_64` 的条目，按
   `name-epoch:version-release.arch` 输出。

2026-11-02 的取证即按此路径执行：SP3/EPOL/main 得到 74 条 `ukui*`
x86_64 条目（另有 5 个 noarch 元包及其子包、`libpam-biometric`
一条），与台账一致；其余四段零条。SP2 到 SP3 的包名集合与版本全部相同，
只有发行标记 `oe2403sp2` → `oe2403sp3` 变化，故换基底不改变组件选型。

---

## 6. 拓扑影响

| 对象 | 修正 |
|---|---|
| `distro/comps/airymaxos-comps.xml` | 不列 `ukui` 元包，按台账逐组件声明 |
| `distro/lockfile/rpms.in.yaml` | 同上；冻结输入不得包含元包 |
| `distro/lockfile/README.md` | 桌面组口径由「UKUI 4.x」改为实测 3.1 组件代 |
| `distro/desktop/README.md` | 冻结点核对表删去 `ukui 2.0.2-20` |
| `docs-linux/190-distribution/03-installer-design.md` | 同步组件代表述 |

门禁 `ci/gates/ukui-lock.sh` 断言台账、comps、冻结输入与本文件的
NVRA 逐字一致；任一环出现未登记或版本漂移即判红。
