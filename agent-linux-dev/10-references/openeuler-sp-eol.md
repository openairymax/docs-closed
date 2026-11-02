# openEuler 基底选型与生命周期台账（M-35 / OE-01）

> 版本: 1.0.0
> 取证日期: 2026-11-02
> 证据级别: E1（基底仓库 repodata 实测，可复算）+ 官方生命周期公告
> 唯一事实源: `agent-linux/distro/lockfile/base.yaml`

---

## 1. 结论

0.0.4 的基底取 **openEuler-24.03-LTS-SP3**。

选型不是一次人工判断，而是一条可复算的规则：候选表、GA 与 Planned EOL
落在 `base.yaml`，判定逻辑落在 `distro/lockfile/base_check.py`，门禁
`ci/gates/base-eol.sh` 每次构建前重算。本文件记录规则、候选、排除理由、
包级差异与 ABI 登记，供门禁与评审共同引用。

回答「为什么不是最新的 SP4」：**因为 SP4 是小 SP，Planned EOL 2027-03-30，
早于本版收口日 2027-09-17。** 追版本号会得到一台交付即过保的机器，这是
反目标。同理，**当前基底 SP2 也是小 SP，EOL 2026-03-30 已过**，0.0.3 的
基线在取证日已停止维护七个月——「保持 SP2 不动」不是保守，而是把风险留在
装机之后。

---

## 2. 选型规则

三条，优先级自上而下，全部由 `base_check.check_pick()` 复算：

1. **只取大 SP**。24.03 LTS 的 SP 有大、小两种节奏：12 月 Release 的大 SP
   支持 24 个月，6 月 Release 的小 SP 只有 9 个月。大规模部署的窗口必须由
   大 SP 承担，小 SP 只适合尝鲜与验证。
2. **Planned EOL 必须晚于收口日**。`base.yaml` 的 `deadline: 2027-09-17`
   与 `policy.eol-covers` 是同一天，二者不等即判 `schema/policy`。发行版的
   维护窗口不能短于自己的交付窗口。
3. **合格候选里取 GA 最晚的一个**，且 `kernel_line` 仍为 6.6。满足前两条
   的候选若不止一个，取最新 GA；内核基线的铁律在这一步收口。

规则实现为失败码而非提示：`base/small-sp`、`base/eol`、`base/not-newest`
任一命中即门禁退出 1。手改 `selected` 而不更新候选表，会被第 3 条当场
拒绝——选型结论不能靠人记。

---

## 3. 候选与排除

| 候选 | GA | 类型 | Planned EOL | 内核 | 判定 |
|---|---|---|---|---|---|
| `openEuler-24.03-LTS-SP1` | 2024-12-30 | large | 2026-12-30 | 6.6 | 排除：EOL 早于收口日 |
| `openEuler-24.03-LTS-SP2` | 2025-06-30 | small | 2026-03-30 | 6.6 | 排除：小 SP，且取证日已过保 |
| `openEuler-24.03-LTS-SP3` | 2025-12-30 | large | 2027-12-30 | 6.6 | **选定** |
| `openEuler-24.03-LTS-SP4` | 2026-06-30 | small | 2027-03-30 | 6.6 | 排除：小 SP，且 EOL 早于收口日 |

三条排除理由各自独立：SP1 只输在窗口（2026-12-30 < 2027-09-17），若不看
收口日它本可入选；SP2、SP4 输在类型与窗口两条。SP3 是唯一同时满足
「大 SP + 覆盖收口日」的候选，因此本轮不存在并列，第 3 条规则不会介入。

**SP5 的处理**：24.03 LTS SP5 计划 2026-12 GA，截至取证日未发布，故不入
候选表——候选表只登记已 GA 的事实，不登记计划。SP5 发布后只做两件事：
在 `candidates` 追加一条实测 GA/EOL，重跑门禁。若它是大 SP 且 EOL 晚于
收口日，第 3 条会自动把它选为基底（GA 最晚），无需改任何判定代码；若是
小 SP，规则同样自动排除。这正是把选型写成规则而不是写死版本号的原因。

---

## 4. 消费面清单

基底串在仓库里有九处表达，任何一处落后都会让装机闭包与冻结集分叉，而
dnf 只在装机现场报「找不到仓库」。门禁逐处断言同一候选：

| 消费面 | 断言内容 | 失败码 |
|---|---|---|
| `distro/lockfile/base.yaml` | `selected`/`deadline`/`policy`/`candidates` 自洽 | `schema/*`、`base/*` |
| `distro/repo/airymax-os.repo` | 五段 baseurl 各含 `/<base>/`，每段列三个宿主，无 `$releasever` | `repo/*` |
| `distro/repo/mirrors.list` | 每行 `<镜像根>/<base>`，首行为 `repo.openeuler.org` | `mirrors/*` |
| `distro/lockfile/rpms.in.yaml` | 五个 `baseurl` 同源 | `seeds/*` |
| `distro/specs/airymaxos-release.spec` | `%global oe_base` 唯一且等于 `selected`；`%changelog` 之前不出现第二个基底串 | `spec/*` |
| `distro/lockfile/ukui-components.yaml` | `base:` 等于 `selected` | `ukui/base` |
| `distro/kickstart/airymaxos-{workstation,minimal}.ks` | 含 `repo.openeuler.org/openEuler-` 的行必须带 `/<base>/` | `ks/base` |
| 说明面：`comps/*.xml`、`ostree/*.treefile`、`desktop/README.md`、`70-airymax-ukui-policy.sh`、`tools/cfg_brand.py` | 注释与文档同样不得残留第二个基底串 | `token/drift` |

五段固定为 `base`、`updates`、`epol`、`epol-updates`、`everything`，段名与
`base_check.SECS` 一一对应。`mirrors.list` 的宿主集合与 `repo` 文件的三宿主
是两组断言：前者防镜像清单漂移，后者防 baseurl 少写一个 fallback。

---

## 5. 包级差异成册（SP2 → SP3，x86_64）

### 5.1 段级总量

| 段 | SP2 | SP3 | 仅 SP2 有 | 仅 SP3 有 |
|---|---|---|---|---|
| `OS` | 2,532 | 2,462 | 79 | 9 |
| `update` | 2,196 | 3,043 | 495 | 1,342 |
| `EPOL/main` | 4,353 | 4,344 | 53 | 44 |
| `EPOL/update/main` | 102 | 196 | 58 | 152 |
| `everything` | 18,947 | 18,986 | 89 | 128 |
| **五段并集** | **23,781** | **24,028** | **279** | **526** |

并集小于各段之和，因为同一 NEVRA 在多段重复出现。`update` 段增加 847 条是
本次换基底的主因：SP3 把 SP2 之后的勘误整体并入基线，`OS` 段随之精简 70 条
（79 移出、9 移入），这是「勘误前移到基础段」的正常形态，不是仓库缩水。

### 5.2 上游版本变化

同一包名、版本或 release 前进：`OS` 36 条、`EPOL/main` 47 条、`update`
169 条。其余包名与 NEVRA 完全不变。

### 5.3 真实移除（组件级归类）

`fcitx` 全族、`libopenvino*`、`haoc-kernel*`、`libsexy`、`unique`、`vte`、
`gtkmm24`、`yaml-cpp03`、`enchant*`、`fros`、`custodia`、
`euler-copilot-shell`、`openeuler-intelligence-*`、`qt5-qtenginio`、
`rubygem-rspec2*`、`gnome-photos`、`gnome-online-miners`、`gfbgraph`、
`libtimezonemap`、`libgdl`、`cargo-rpm-macros`、`rust-srpm-macros`。

279 条里其余是子包、debuginfo 与 debugsource，随主包进出。**唯一命中我方
冻结输入的是 `fcitx` 全族**：输入法因此整体切到 `ibus` + `ibus-libpinyin`
（`distro` 提交 `bd41ecc`）。这是本次换基底唯一需要改实现的包级变化，也是
先做包级差异成册、再动冻结输入的原因——顺序反过来只会在闭包解析时报一堆
`no package provides`。

### 5.4 真实新增（组件级归类）

`postgresql-17*`、`golang-1.24`、`llvm-toolset-20*`、`java-25-openjdk*`、
`witty*`、`KASandbox`、`python3-vllm`、`erofs-utils`、`libummu`。

均不在冻结输入内：只改变仓库体积与 `everything` 段候选面，不改变镜像闭包。
需要留意的是 `libummu` 与 `KASandbox` 属内核旁路组件，本版不选，也不作为
微内核化通道（§2.3 的边界：ALK 只经既有 `/proc/sys/agentrt` 与
`/sys/kernel/security/airy/policy` 表达）。

### 5.5 闭包复算

以当前冻结输入解析出 105 个待解包名：SP2 缺 4、SP3 缺 4，残差集合逐项
相同（三个自建包 + 一个 x86_64 解析噪声）。**换基底没有引入新的缺包**，
SP3 的可解性与 SP2 等价。这条是 5.3 的验收条件：若输入法未迁移，SP3 会比
SP2 多缺四个 fcitx 包。

---

## 6. ABI 破坏项登记

### 6.1 结论：零项

七组核心 ABI 相关包在 SP2 → SP3 之间 `epoch` 与 `version` 均不变，只有
`release` 前进，属上游定义的兼容更新通道：

| 包 | SP2 | SP3 |
|---|---|---|
| `glibc` | 2.38-59 | 2.38-84 |
| `gcc` | 12.3.1-95 | 12.3.1-105 |
| `openssl` | 1:3.0.12-17 | 1:3.0.12-31 |
| `python3` | 3.11.6-12 | 3.11.6-20 |
| `systemd` | 255-43 | 255-50 |
| `rpm` | 4.18.2-23 | 4.18.2-30 |
| `kernel` | 6.6.0-98.0.0.103 | 6.6.0-132.0.0.111 |

内核仍为 6.6 线，不违反「不改内核基线」铁律；`6.6.0-132` 是同一基线的
勘误累积，不是换线。

### 6.2 判定口径

ABI 破坏项 = `epoch` 或 `version` 变化，或包内 soname 集合变化。只比完整
NEVRA 会把 release 前进误记为破坏（首轮 `EVRchg` 统计正是这样虚高的），
复算脚本在比较前剥掉 `.oe2403spN` 发行标记再比 `version`。

release 前进仍需逐项确认的唯一场景是发行版自建的预编译产物（`.ko`、预生成
schema）：它们按 NEVRA 钉版，release 变化会触发重构建。本版全部自建产物
走同一 RPM 构建链，不缓存跨基底的二进制，因此零项登记成立。

---

## 7. 复算

### 7.1 门禁

```sh
ci/ci.sh base-eol            # 或 ci/gates/base-eol.sh --source .
```

通过时打印 `基底 openEuler-24.03-LTS-SP3 覆盖收口日到 2027-09-17`；
失败时逐行列出失败码，任一非零即判红。

### 7.2 repodata 直读（无 dnf 的取证机）

1. 取 `…/<SP>/<段>/x86_64/repodata/repomd.xml`，找 `type="primary"` 的
   `location href`；
2. 该文件是 `.xml.zst` 或 `.xml.gz`，解压后迭代
   `{http://linux.duke.edu/metadata/common}package`；
3. 按 `name-epoch:version-release` 建集合，逐段与对侧 SP 求差。

2026-11-02 的取证即按此路径执行，得到 §5.1 的五段计数与 §5.3/§5.4 的
移除/新增清单。段间差异必须在**并集**上算，逐段相加会把跨段重复的包
重复计数。

### 7.3 生命周期复核

候选的 `ga`/`eol` 取自 openEuler 官方生命周期公告，与
<https://www.openeuler.org/zh/lifecycle/> 对账后写入 `base.yaml`。公告更新
时只改候选表，判定逻辑与门禁不变；改完重跑 7.1 即得到新的选型结论。

---

## 8. 拓扑影响

| 对象 | 状态 |
|---|---|
| `distro/lockfile/base.yaml` | 台账唯一事实源，四条候选 + 三条规则约束 |
| `distro/lockfile/base_check.py` | 规则复算与九处消费面断言，标准库、离线 |
| `ci/gates/base-eol.sh` | 仅参数校验与调用，不复制判定逻辑 |
| `distro/lockfile/ukui-components.yaml` | `base:` 随 `selected`，NVRA 见 `ukui-delta.md` |
| 输入法闭包 | 随 SP3 从 fcitx 全族切到 ibus（`bd41ecc`） |
| 内核 | 6.6 线不动；`6.6.0-132` 只前进 release |

门禁与台账的分工是单向的：`base.yaml` 只写事实（日期、类型、内核线），
`base_check.py` 只写判定，`base-eol.sh` 只写调用。三处任一处想「顺手」
补一条规则，都会让选型结论出现第二个事实源。
