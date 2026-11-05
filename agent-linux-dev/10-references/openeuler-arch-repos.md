# openEuler 三架构仓库布局台账（F-01 / ARCH-01）

> 版本: 1.0.0
> 取证日期: 2026-11-05
> 证据级别: E1（基底仓库 HTTP 探测 + repodata primary 实解析，可复算）
> 服务对象: `distro/lockfile/rpms.in.yaml` 的 `contentOrigin` 与 `distro/scripts/build-iso.sh` 的 `check_arch()`

---

## 1. 结论

三个目标架构在基底 SP3 上**都有可用的 RPM 基线**，但 **riscv64 的仓库路径多一层
指令集档位目录**，与 x86_64 / aarch64 的扁平布局不同：

| 架构 | OS 仓库 baseurl（相对 `<repo>/openEuler-24.03-LTS-SP3/`） |
|------|----------------------------------------------------------|
| x86_64 | `OS/x86_64/` |
| aarch64 | `OS/aarch64/` |
| riscv64 | `OS/riscv64/<profile>/riscv64/`，`<profile>` ∈ `rva20`、`rva23` |
| loongarch64 | `OS/loongarch64/`（非本版目标，仅登记布局） |

因此「按 `$basearch` 拼 baseurl」在 riscv64 上**必然拼错**：`OS/riscv64/` 本身没有
`repodata/`，只有 `rva20/` 与 `rva23/` 两个档位目录。这不是可绕过的边角，而是
`contentOrigin` 必须显式携带档位变量的原因。

`rva20` 与 `rva23` 是 RISC-V 的两个应用处理器档位（RVA20 = 2019 年档位，
RVA23 = 2024 年档位，后者要求向量扩展等强制特性）。二者包集合不同，**不得混用**：
一台 rva20 机器装 rva23 的包会在第一条向量指令上非法指令退出。档位必须由安装目标
决定，不能由构建宿主决定。

---

## 2. 逐仓库探测结果

探测方法：对每个仓库取 `repodata/repomd.xml`，记录 HTTP 状态；200 视为该仓库
在该架构上成立。带重定向（`repo.openeuler.org` → CDN）一律跟随。

| 仓库 | x86_64 | aarch64 | riscv64 (rva20) | riscv64 (rva23) | loongarch64 |
|------|--------|---------|-----------------|-----------------|-------------|
| `OS/` | 200 | 200 | 200 | 200 | 200 |
| `update/` | 200 | 200 | 200 | 200 | — |
| `EPOL/main/` | 200 | 200 | 200 | 200 | 200 |
| `EPOL/update/main/` | 200 | 200 | **404** | **404** | — |
| `everything/` | 200 | 200 | 200 | 200 | — |

两条直接后果：

1. **riscv64 没有 EPOL 勘误仓库**。`rpms.in.yaml` 现用 `epol-update` 做 EPOL 组件的
   勘误吸收；在 riscv64 上该仓库不存在，拼进去会让 `dnf` 直接报「Cannot download
   repomd.xml」。故该仓库在 riscv64 剖面必须**整体省略**，而不是留空 baseurl。
2. **`everything` 在 riscv64 上存在**，桌面闭包兜底路径成立（`qt5-qtgraphicaleffects`
   一类只发布于此的包不会因架构而缺席）。

---

## 3. 包级可用性（riscv64 rva23 / EPOL/main 实测）

对 `EPOL/main/riscv64/rva23/riscv64/repodata/*-primary.xml.zst` 解压后统计：
**4,067 个唯一包名**，含完整 UKUI 3.x 会话闭包与显示管理器。

关键组件 NVRA 与 x86_64 同代（版本、发布号逐字一致，仅架构不同）：

| 包 | riscv64 NVRA | x86_64 锁文件钉住值 |
|----|--------------|--------------------|
| `ukui-panel` | `3.1.0-14.oe2403sp3` | `3.1.0-14.oe2403sp3` |
| `ukui-kwin` | `1.0.5-8.oe2403sp3` | `1.0.5-8.oe2403sp3` |
| `ukui-session-manager` | `3.1.0-7.oe2403sp3` | `3.1.0-7.oe2403sp3` |
| `lightdm` | `1.30.0-14.oe2403sp3` | `1.30.0-*`（闭包求解） |

包名清单中存在 `ukui-control-center`、`ukui-sidebar`、`ukui-search`、`ukui-themes`、
`ukui-wallpapers`、`ukui-menu`、`ukui-notification-daemon`、`ukui-power-manager`、
`ukui-bluetooth`、`ukui-clock`、`ukui-notebook`、`ukui-system-monitor`、
`ukui-window-switch`、`ukui-polkit`、`ukui-interface`、`ukui-greeter`、
`ukui-screensaver`、`ukui-media`、`ukui-biometric-manager` 等，与
`lockfile/ukui-components.yaml` 的 `present` 集合可逐项对齐。

**这说明「UKUI 桌面闭包在 riscv64 上可解」**，是能否做 riscv64 ISO 的第一道前提，
且已被证成。

---

## 4. 安装介质与引导链（二次取证，2026-11-05）

仓库有包 ≠ 镜像能装能启动。上一版把四项全部记为「未取证」；本轮已对前三项
取到 E1 证据，第四项仍未成立。

| # | 项目 | 结论 | 证据 |
|---|------|------|------|
| 1 | 安装介质 | **成立** | `ISO/riscv64/rva20/` 与 `ISO/riscv64/rva23/` 均发布 `netinst-riscv64-dvd.iso` 及 `.sha256sum`；`OS/riscv64/<profile>/riscv64/images/pxeboot/` 下有 `vmlinuz`、`initrd.img`，`images/` 下有 `efiboot.img`、`install.img` |
| 2 | anaconda | **成立** | rva23 介质包清单（`ISO/riscv64/rva23/openEuler-24.03-LTS-SP3-riscv64.rpmlist`，2351 行）含 `anaconda-36.16.5-49.oe2403sp3.riscv64`、`anaconda-core`、`anaconda-tui`、`lorax-34.1-8`、`isomd5sum-1.2.3-9`，与 x86_64 同代 |
| 3 | 引导链 | **成立（无 shim）** | 同清单含 `grub2-efi-riscv64-2.12-52.oe2403sp3`、`grub2-efi-riscv64-cdboot`、`grub2-efi-riscv64-modules`、`edk2-ovmf-riscv64-202308-29`；**无 `shim-*` 包**，riscv64 走 grub2-efi 直启，不经 shim 中转 |
| 4 | UKUI 运行期 | **未成立** | 只证到「闭包可解」，未证「可跑」。需要一次真实装机 + 冷启动观测 |

两条对工程有直接约束的差异：

- **riscv64 没有 shim**。x86_64/aarch64 的 ESP 品牌布局是 `shim → grub2 → 内核`
  三段签名链（验收 T11 断言的正是这份完整签名套件）；riscv64 只有 grub2-efi
  一段。ESP 布局必须按架构分叉，用 x86_64 的布局去装 riscv64 会得到一个
  `grubx64.efi` 指向不存在 shim 的空引导项。
- **档位进 ISO 文件名**。rva23 的介质名多一段 `RVA23`（
  `openEuler-24.03-LTS-SP3-RVA23-netinst-riscv64-dvd.iso`），rva20 则没有。
  媒体摘要表若按「版本 + 架构」两键索引，两个档位会撞成同一个键。

`check_arch()` 仍未放行 riscv64：前三项只说明「能造出安装介质」，第四项才决定
「装了能不能用」。放行必须在 rva23 实机上完成一次装机 + 冷启动之后。

---

## 5. 对工程的落点（本台账约束的实现方向）

| 位置 | 现状 | 本台账要求 |
|------|------|-----------|
| `distro/lockfile/rpms.in.yaml` | 五段 baseurl 全部 `$basearch` 扁平；`arches: [x86_64]` | 仓库地址改为「架构 → 路径模板」映射，riscv64 模板带 `<profile>`；`arches` 随取证结论逐架构追加 |
| `distro/scripts/lib/arch.sh` | 只归一化 `x86_64`/`aarch64`（`amd64`/`arm64` 别名） | 增加 riscv64 归一化，并把「档位」作为独立维度返回，不与架构名混为一谈 |
| `distro/scripts/build-iso.sh` `check_arch()` | `x86_64|aarch64`，其余 `die` | 保持 `die`：§4 前三项已成立，第四项（UKUI 运行期）未成立，放行须以 rva23 实机装机 + 冷启动为前置 |
| ESP 品牌布局（`distro/` 引导资产） | 单一路径假定 `shim → grub2` | 按架构分叉：riscv64 为 `grub2-efi` 直启，无 shim 段 |
| 媒体摘要表（`ci/gates/media-fetch.sh`） | 「版本 + 架构」两键 | 增加档位维度，riscv64 用 `版本 + 架构 + rva20/rva23` 三键 |
| `distro/lockfile/ukui_check.py` / `base_check.py` | `ARCH = "x86_64"` 硬编码 | 改为入参，按架构分别复算 NVRA |

**未取证前不放开 `check_arch()`**：放行一个装不上的架构，等于把「不支持」伪装成
「支持」，这正是本版铁律明令禁止的演示性实现。

---

## 6. 复算方法

```
# 仓库存在性（200 即成立；riscv64 注意档位路径）
curl -sL -o /dev/null -w '%{http_code}\n' \
  https://repo.openeuler.org/openEuler-24.03-LTS-SP3/OS/riscv64/rva23/riscv64/repodata/repomd.xml

# 包集合与 NVRA（需 zstd）
curl -sL -o /tmp/rv.xml.zst <repomd 里 primary 的 href>
zstdcat /tmp/rv.xml.zst | grep -c '<package '
zstdcat /tmp/rv.xml.zst | grep -A2 '<name>ukui-panel</name>' | grep -o 'ver="[^"]*" rel="[^"]*"'
```

判定口径：`repomd.xml` 取不到即该仓库在该架构上不存在，**不得用「大概有」推断**。

---

> **文档结束** | AgentRT 开源维护团队
