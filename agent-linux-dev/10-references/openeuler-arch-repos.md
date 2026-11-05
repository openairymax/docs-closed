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

## 4. 仍未取证的部分（不得当作已成立）

仓库有包 ≠ 镜像能装能启动。下列四项尚缺 E1 证据，`check_arch()` 在补齐前
**不得对 riscv64 放行**：

1. **安装介质**：`ISO/` 下是否存在 riscv64 的 `netinst` / `boot.iso` 及其
   `images/pxeboot` 内核与 initrd；
2. **anaconda 可用性**：riscv64 的安装器是否随介质发布（若上游只发 rootfs
   镜像而不发 anaconda，装机路径必须另设，不能假装 `build-iso.sh` 能产 ISO）；
3. **引导链**：riscv64 的 `EFI/BOOT/` 引导文件名与 QEMU `virt` 机型的固件
   （`edk2-riscv64` 或 `opensbi`）是否可用；
4. **UKUI 运行期**：上述闭包在 riscv64 上的实际启动结果（本版只到「可解」，
   未到「可跑」）。

---

## 5. 对工程的落点（本台账约束的实现方向）

| 位置 | 现状 | 本台账要求 |
|------|------|-----------|
| `distro/lockfile/rpms.in.yaml` | 五段 baseurl 全部 `$basearch` 扁平；`arches: [x86_64]` | 仓库地址改为「架构 → 路径模板」映射，riscv64 模板带 `<profile>`；`arches` 随取证结论逐架构追加 |
| `distro/scripts/lib/arch.sh` | 只归一化 `x86_64`/`aarch64`（`amd64`/`arm64` 别名） | 增加 riscv64 归一化，并把「档位」作为独立维度返回，不与架构名混为一谈 |
| `distro/scripts/build-iso.sh` `check_arch()` | `x86_64|aarch64`，其余 `die` | 保持 `die` 直到 §4 四项取证完成；届时按「架构 + 档位」双键放行 |
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
