# 硬件能力矩阵与按能力选机台账（V-10 / HW-01、HW-02）

> 版本: 1.0.0
> 取证日期: 2026-11-04
> 证据级别: E2（判据由合成夹具逐分支回归，可复算）；E1 目标机取证待 285H 复验后补录
> 唯一事实源: 内核 sysfs/procfs 能力节点（`/sys/class/drm`、`/sys/class/ieee80211`、
> `/sys/class/sound`、`/sys/class/input`、`/sys/class/backlight`、`/sys/class/leds`）
> 判据实现: `ci/lib/hwcap.py`（门禁 `ci/gates/hw-matrix.sh`）
> 登记册: docs-linux `160-compatibility/`（OS-ACC-104 硬件兼容矩阵）

---

## 1. 结论

HW-01 要求「五类硬件能力矩阵逐项有判定，无静默跳过」；HW-02 要求「按能力
选机，不按机型白名单」。

0.0.3 的验收清单按机型名登记目标机。机型名只说明厂商怎么命名，说明不了
这台机器当下有没有可用的显示、无线、音频、输入与背光：同一机型换一批网卡、
同一主板换一代声卡、外接键盘拔掉，登记表都不会变。更坏的是「驱动绑上了」
被当成「设备可用」——`phy` 注册了但没有网络接口、声卡在位但没有 PCM 节点、
背光节点存在但 `max_brightness` 为 0，这些状态在机型表里全部显示为「支持」。

本版把判定改成五类能力节点，每类只输出 `pass` / `n/a` / `fail` 三种结论。
`n/a` 必须带 `note`，说明是「本机无此硬件」还是「硬件在位但缺内核能力」，
后者写明顺延版本。五类每次都打印，缺证据也落一行，故不存在静默跳过。

---

## 2. 五类判据

| 类 | 证据节点 | pass | fail（稳定判据名） | n/a |
|---|---|---|---|---|
| display | `/sys/class/drm/card*`、`card*-*`、`/sys/bus/pci/devices/*/class` | 非 simpledrm 的 KMS 驱动 + 至少一个 `connected` 连接器同时有 `modes` 与非空 `edid` | `no-connector`、`no-kms`、`no-output`、`no-mode`、`no-edid` | `no-display-hardware`（无 DRM 卡、无 PCI 显示设备、无 `fb0`） |
| wireless | `/sys/class/ieee80211/phy*`、`/sys/class/net/*/phy80211` | PHY 已注册且至少一个网络接口挂在其下 | `phy-without-netdev` | `no-ieee80211` |
| audio | `/sys/class/sound/card*`、`card*/pcm*` | 有 sound card 且至少一个 PCM 节点 | `card-without-pcm` | `no-sound-card` |
| input | `/sys/class/input/input*`、`capabilities/key` | 至少一个设备的键位图含 `KEY_A`（30） | `input-without-keyboard` | `no-input-device` |
| backlight | `/sys/class/backlight/*`、`/sys/class/leds/*kbd_backlight*` | 至少一个节点 `max_brightness > 0` 且 `brightness` 可读 | `backlight-unusable` | `no-backlight` |

判据的取舍理由：

- **display 要求四条同时成立**，与 HW-06 的 Xorg 判定同源。只有驱动名说明
  不了面板点亮：KMS 之外的 `simpledrm` 在 X 1.20 下不被 modesetting 接管，
  已连接但无模式或 EDID 为空时 X 会在模式求交上失败，表现为「进了桌面但
  黑屏」。矩阵在此报 `fail` 并给出缺口，而不是记成「有显卡」。
- **wireless 以 netdev 为可用标志**。PHY 存在只说明固件与驱动加载到一半，
  没有 netdev 时 `nmcli` 看不到设备，用户态再全也无法联网（0.0.3 的
  D-01~D-04 就是用户态四件套与驱动两侧都缺的叠加）。
- **audio 以 PCM 为可用标志**。只有 `card*` 目录而无声卡注册的流节点，通
  常是 HDA 控制器在位但 codec 未绑定；此时混音器能枚举但放不出声。
- **input 以键位图为可用标志**。按设备名找「keyboard」在多语言与多外设
  环境下不可靠；`KEY_A` 是键盘类设备的最小共同能力，触摸板与手柄不置该位。
  位图按内核 `%*pb` 的打印顺序解析：最后一个 64 位字是最低位。
- **backlight 两类节点都收**。笔记本屏幕背光在 `/sys/class/backlight`，
  键盘背光在 `/sys/class/leds/*kbd_backlight*`；只有键盘背光的机器（外接
  屏、台式机加背光键盘）仍记为 `pass`，并在证据里给出 `kbd=1`。

---

## 3. 判定语义

```
CLASS display PASS driver=i915,connector=card0-DP-1,edid=1
CLASS wireless N/A no-ieee80211 note=本机无无线硬件
CLASS audio PASS card=card0,pcm=3
CLASS input PASS devices=4,keyboards=1
CLASS backlight PASS node=intel_backlight,kbd=1
HW-MATRIX pass=4 na=1 fail=0
```

- 每类一行，字段固定为「CLASS / 类名 / 结论 / 证据」，`note` 只在非空时出现。
  现场只认这一行，不解析告警文本。
- `HW-MATRIX` 汇总行用于流水线判读；任何 `fail` 使门禁退 1。
- `--json` 输出同构对象（`classes` / `summary` / `select`），供报告与看板
  消费，不再要求下游解析空格分隔的文本。
- `--class LIST` 只判定列出的类，但不会改变每类的判据；用于单类排查。
- `--root DIR` 指向抓取下来的证据树（含 `sys/`、`proc/`），历史产物与远端
  机器都能复算；缺省为 `/`，直接在本机取证。

---

## 4. 按能力选机（HW-02）

```sh
ci/ci.sh hw-matrix --require display,wireless,audio,input,backlight
```

- 列出的类必须全部 `pass`；任一 `n/a` 或 `fail` 即拒绝，输出
  `SELECT machine reject missing=<类名列表>`，门禁退 1。
- 判定链只读 sysfs/procfs 能力节点，没有 DMI、机型名、品牌白名单。
  合成夹具里写入任意 `product_name` / `sys_vendor` 不改变结论，回归脚本
  对此有断言。
- 选机的输入是这五个结论而不是机器清单，因此同一台机器换内核、换网卡、
  换外设后重新取证即可，不需要维护机型表；多台候选机由上层按同一门禁逐台
  判定，取第一台全通过的机器。

---

## 5. 跨架构

三类架构的 sysfs 形态一致，判据不含架构分支：

- x86_64 与 aarch64 的显示设备通常经 PCI 暴露，`gpu_bus()` 用 PCI 基类
  `0x03` 区分「无显示硬件」与「有硬件但未绑定驱动」。
- riscv64 与部分 aarch64 平台经设备树暴露 GPU，没有 PCI 节点；此时只要
  `/sys/class/drm/card*` 存在就按有显示硬件判定，`gpu_bus()` 只是补充证据，
  不是必要条件。
- 无线、音频、输入、背光四类不依赖总线类型，只认 class 节点。

---

## 6. 已知顺延登记

| 条目 | 状态 | 说明 |
|---|---|---|
| D-06 Battlemage（`8086:e212`）i915/xe 绑定 | 顺延 | 6.6 基线无该 PCI ID，`xe` 不在树内；本版在矩阵中报 `no-kms` 或 `fail`，登记进 `160-compatibility/`，不静默记「支持」 |
| 285H GPU（`8086:7d51`）原生 KMS | 顺延 | 属内核配置与驱动变更，本版只收敛交付面与通用显示策略 |
| I2C_DESIGNWARE_PCI 与触控板原生支持 | 顺延 | 属内核配置变更；输入类在矩阵中按实际键位图判定，不按机型推断 |
| `CONFIG_SYSFB_SIMPLEFB` / `CONFIG_DRM_SIMPLEDRM` | 顺延 | 属内核配置变更；本版把 simpledrm 明确判为 `fail/no-kms`，不以固件 framebuffer 冒充可用显示 |

顺延条目必须在 `160-compatibility/` 有对应行，矩阵报 `fail` 或 `n/a` 时
`note` 与登记册一致；不得用「机型支持」覆盖实测缺口。

---

## 7. 取证与验收记录

目标机上取证（只读，不改系统状态）：

```sh
ci/ci.sh hw-matrix --json > hw-matrix.json
ci/ci.sh hw-matrix --require display,wireless,audio,input,backlight
```

证据树离线复算：

```sh
mkdir -p evidence/sys/class evidence/sys/bus
cp -a /sys/class/{drm,ieee80211,sound,input,backlight,leds} evidence/sys/class/
cp -a /sys/bus/pci/devices evidence/sys/bus/pci/
ci/ci.sh hw-matrix --root evidence --json
```

验收记录（E1 待补）：

| 日期 | 机器 | 架构 | 结论 | 证据 |
|---|---|---|---|---|
| 2026-11-04 | 合成夹具（全能力） | 无关 | pass=5 | `ci/tests/test_hw_matrix.sh` |
| 2026-11-04 | 合成夹具（五类缺口各一） | 无关 | 对应类 fail | 同上 |
| 待补 | 285H 目标机 | x86_64 | 待取证 | `hw-matrix.json` |
| 待补 | ARM 验收机 | aarch64 | 待取证 | `hw-matrix.json` |
| 待补 | RISC-V 验收机 | riscv64 | 待取证 | `hw-matrix.json` |

E1 记录补齐前，矩阵只能证明判据没有漏判与误判，不能证明目标机通过；
正式发行版的验收报告必须引用三架构各一份 `hw-matrix.json`。
