Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 基底定义与替换决策（0.0.10–0.1.1）

> **文档定位**：回答「openEuler 基底到底是什么、要替换哪些、用什么语言、怎么换」的唯一决策件。
> 本文件取代此前所有关于「自有基底」的散落表述；与 `baseline-coupling.md`（清点）分工明确：
> 那册只清点、不决策，本册只决策、不重复清点。
> **版本**：1.0.0
> **最后更新**：2026-11-17
> **裁定人**：项目负责人（2026-11-17，三条裁定逐字见 §1.2）
> **适用范围**：0.0.5–0.1.1；0.0.30 为「自有基底完成」的验收点，0.1.1 为「默认基底切换」点。

---

## 1. 结论先行

### 1.1 五条结论

| # | 结论 | 一句话依据 |
|---|---|---|
| C-1 | 要替换的不是 6,000 个源码包，而是 **113 个二进制包展开后的 500–900 个源码包构建闭包** | `comps` 113 条 packagereq，逐包 BuildRequires 递归后收敛于 500–900 |
| C-2 | 自有的含义是 **掌握供应权与构建权**，不是重写 glibc/内核 | 上游组件继续用上游代码，自有的是「能自己构建、能自己发、能自己改」 |
| C-3 | 基底 **可以用 Rust**，但不是「基底整体换 Rust」 | 新代码用 Rust；内核、glibc、systemd、rpm、Qt/UKUI、GRUB、anaconda 保持既有语言 |
| C-4 | 双基底 **永久保留，但只在装配与通道层** | 源码层不做双实现，避免死代码；两条产品线共用同一套源码 |
| C-5 | 「对齐 openEuler 逐步替换」= **行为等价复刻**，不是代码拷贝 | 以差分语料证明等价，再单实现切换并删除旧实现 |

### 1.2 三条约束性裁定（2026-11-17）

1. **0.0.5 口径 = 用户态面 + 已有 ABI**：TUI 让 `docs-linux` 的用户态可观测功能全部可用，
   只消费既有 `airy_*` ABI 与 `airy-*` CLI；未完成模块显式登记为缺口，**严禁桩**。
2. **boot TUI 中文输入 = 独立 Rust IME crate**：只共享 `AIRYIME1` 词典格式与数据资产，
   **不链接 agentrt**。
3. **0.0.6 右侧 dock 渲染 = Slint**：dock 复用 AirymaxRT 的智能体能力，不复用 boot TUI 的运行时。

### 1.3 两条被撤销的旧表述（不得再被引用）

| 旧表述 | 处置 | 原因 |
|---|---|---|
| 「一个协议、两个渲染器」 | **撤销** | 0.0.5 的 boot TUI 与 0.0.6 的 dock 不共享运行时。正确的是**一个契约层、两条独立通路**（见 §6） |
| 「复刻性替换 = 拷贝 openEuler 代码再改」 | **撤销** | 拷贝引入许可证与死代码双重问题。正确的是**行为等价复刻 + 差分语料 + 单实现切换**（见 §5） |

---

## 2. 基底是什么：三个尺度

同一个词「openEuler 基底」在三种尺度上范围差两个数量级。任何工期或工作量结论必须先声明尺度，
否则必然出现「说要换 6,000 个包」与「实际只依赖 113 个包」并存的矛盾。

### 2.1 尺度 A：完整发行版（约 6,000 个源码包）

指 openEuler 24.03 LTS 全仓库的源码包总量。它**不是**本项目的替换标的：本项目从不构建全仓库，
也不发布全仓库。尺度 A 只用于一个判断——**上游生命周期**（SP 节奏、EOL、errata 供给能力）。

### 2.2 尺度 B：实际使用闭包（113 个二进制包 → 500–900 个源码包）

| 事实 | 数值 | 可复算入口（仓库根 `agent-linux/`） |
|---|---|---|
| `comps` 显式声明的二进制包 | 113 条 | `grep -c '<packagereq' distro/comps/airymaxos-comps.xml` |
| 客户端 repo 段数 × 镜像根 | 5 段 × 3 根 = 15 条 URL | `grep -o 'baseurl=' distro/repo/airymax-os.repo`（5 条，每行 3 个 URL） |
| 构建宿主机依赖清单 | 94 行，**Rust 0 条** | `wc -l ci/container/build-packages.txt`；`grep -in 'rust\|cargo' ci/container/build-packages.txt` |
| 自有 spec | 4 份 | `ls distro/specs/` |
| spec 内 BuildRequires/Requires | 24 条 | `grep -cE '^(BuildRequires|Requires):' distro/specs/*.spec` |
| UKUI 组件台账 | 26 项 | `distro/lockfile/ukui-components.yaml` |
| 安装器链 | anaconda + kickstart + 引导链 | `distro/kickstart/`、`distro/specs/airymaxos-release.spec` |

**关键推论**：113 个二进制包只是「装进镜像的叶子」；要自己构建它们，必须把每个包的
BuildRequires 递归展开，规模落在 **500–900 个源码包**。这个闭包才是 0.0.10–0.0.30 的真实标的。
超出闭包的部分（尺度 A 的其余包）不进入替换计划。

**逐域实物清点（2026-11-17 复算，回答「基底具体有哪些」）**：113 条 `packagereq` 按
5 组分布——airymax-core 66、desktop-core 27、desktop 17、desktop-extras 3（复算命令：
`grep -c '<packagereq' distro/comps/airymaxos-comps.xml` 与逐组 sed 计数）。按域归属与
替换窗口如下：

| 域 | 包数 | 代表包 | 目标自持 | 替换窗口 |
|---|---|---|---|---|
| 仓库面（W1） | 15 条 URL | `mirrors.list` 3 根 × 5 段 | S3 | 0.0.8–0.0.9 |
| 构建宿主面（W5） | 94 行 | gcc、make、createrepo_c | S3 | 0.0.10–0.0.12 |
| 包管理 | 4 | rpm、dnf、dnf-plugins-core、yum | S2 | 0.0.16–0.0.19 |
| 存储工具 | 5 | e2fsprogs、xfsprogs、parted、lsscsi、sg3_utils | S1 | 0.0.16–0.0.19 |
| 运行时底座 | 24 | glibc、systemd、util-linux、coreutils、bash、shadow、tuned | S1 | 0.0.20–0.0.23 |
| 网络栈 | 12 | NetworkManager、wpa_supplicant、iproute、firewalld、curl | S1 | 0.0.20–0.0.23 |
| 时间与日志 | 2 | chrony、rsyslog | S1 | 0.0.20–0.0.23 |
| 内核与引导 | 9 | grub2-tools、grubby、kexec-tools、dracut-config-rescue、linux-firmware、irqbalance | S1/S0（firmware S0） | 0.0.24–0.0.26 |
| 安装器链（W3） | — | anaconda、lorax、kickstart、plymouth | S2 | 0.0.24–0.0.26 |
| 安全与身份 | 10 | selinux-policy-targeted、audit、sssd、openssh、sudo、authselect | S1/S2 | 0.0.27–0.0.29 |
| UKUI 桌面 | 47 | ukui-kwin、ukui-panel、peony、qt5-ukui-platformtheme | S2 | 0.0.27–0.0.29 |
| 桌面应用与输入 | 6 | ibus、ibus-libpinyin、mate-terminal、firefox | S0/S1 | 0.0.27–0.0.29 |

清点口径：core 66 项逐包归类为上表第 2–8 行（运行时底座 24 + 包管理 4 + 网络 12 +
存储 5 + 安全身份 10 + 时间日志 2 + 内核引导与硬件取证 9 = 66，其中 usbutils、lshw
归入内核引导域的硬件取证位）；desktop-core 27 + desktop 17 + extras 3 = 47 归入
UKUI 桌面与桌面应用两行。该表是 0.0.16 起各窗口立项时「先语料后代码」的语料清单底册，
任何窗口开工前先在此表对应行登记差分语料的位置，再动代码。

### 2.3 尺度 C：耦合点（60 条，扩至 70 条）

`baseline-coupling.md` 按「换基底是否必须改这一行」清点出 60 条，证据级别 E1 37 / E2 15 / E3 7 / E4 1。
本册新增第 9 章 10 条（BC-061–BC-070，语言与供应链面），总量 70 条。

七个耦合面与基底七层一一对应：

| 层 | 内容 | 耦合册章节 | 替换动作的性质 |
|---|---|---|---|
| W1 仓库面 | 镜像根、repo 段、锁文件输入 | §2 | 全量重写 URL 与索引格式 |
| W2 包集合面 | comps、ukui 组件、字体闭包 | §3 | 重排包集合与依赖求解 |
| W3 安装与引导链 | anaconda、kickstart、GRUB、plymouth | §4 | 换安装器还是适配安装器，需单独立项 |
| W4 内核与打包 | 内核基线、模块签名、`%global kernel_local` | §5 | 编译参数与签名链保持，包名自有 |
| W5 构建工具链 | 容器、宿主机依赖、宏 | §6 | 自持构建容器与宏定义 |
| W6 CI 判据面 | 断言、门禁、工作流假设 | §7 | 判据随基底重写，不得静默放宽 |
| W7 运行时约定 | os-release、cgroup、journald、GRUB 形状 | §8 | 逐条以实测替换推断 |

### 2.4 当前自有程度（诚实基线）

- 用户态几乎全部是 openEuler 上游二进制；真正自有的只有 4 份 spec 与 10 个 `airy-*` 入口
  （`system/bin`，其中 1 份为 `.c` 源码）。
- 内核为 ALK：4 个 `airy_*` syscall、19 份 `kernel/include/uapi/linux/airymax/` 头文件；
  其余为 Linux 6.6 线。
- 原生模块多为起步规模（认知主循环、记忆 L1、LSM 等），只能算「有实现」，不能算「能替代上游」。

---

## 3. 自有基底的分层与自持级别

### 3.1 五层模型（L0–L4）

| 层 | 名称 | 包含 | 自有判据 |
|---|---|---|---|
| L0 | 内核与固件 | ALK 内核、固件闭包、模块签名 | 能用自有源码与配置构建出同 ABI 内核 |
| L1 | 最小根文件系统 | glibc、init、coreutils 子集、shell、包管理 | 断网可从自有介质装出可启动系统 |
| L2 | 包管理与更新 | rpm/dnf、仓库、签名、锁文件 | 自有仓库可发、可升、可回滚 |
| L3 | 桌面与会话 | UKUI、显示管理器、输入法、dock | 会话可登录、可输入中文、可操作 |
| L4 | 应用与智能体面 | `airy-*`、TUI、AirymaxRT 接入 | 意图可输入、计划可见、动作可审批 |

「自有基底完成」指 L0–L3 达到 S2（见 §3.2），L4 达到 S1；不要求 L0–L3 全部达到 S3。

### 3.2 自持四级（S0–S3）

| 级别 | 名称 | 定义 | 判据 |
|---|---|---|---|
| S0 | 消费 | 二进制取自上游仓库 | 能装、能跑；无构建权 |
| S1 | 重建 | 我方 spec 能从上游源码重建同一二进制 | 同源码、同配置、同编译器下产物行为等价（差分语料通过） |
| S2 | 接管 | 自有实现接管同名包，上游包退出 | 旧包被 `Obsoletes/Provides` 顶替；依赖方无感 |
| S3 | 自立 | 上游仓库不可用时仍能构建发行版 | 断网、空上游缓存下从源码闭包构建出完整镜像 |

替换不是「一次性跳到 S3」，而是每个包独立沿 S0→S1→S2 前进；S3 只在 0.1.1 之后按整体验收。

### 3.3 自持级别的选择规则

1. 上游组件（glibc、systemd、rpm、Qt、GRUB）：目标 S1，不追 S2。理由：重写它们不产生产品差异，
   只产生维护负债。
2. 差异面组件（`airy-*`、TUI、dock、输入法网关、ASR 网关、更新通道）：目标 S2。
3. 供应链基础设施（仓库、签名、锁文件、构建容器）：必须 S3，否则「双基底」只是两个上游镜像。
4. 内核：目标 S1（自有源码 + 自有配置 + 自有签名），不追 S2（不重写 Linux）。

---

## 4. 语言政策：Rust 还是 C

### 4.1 总原则：进程边界即语言边界

- 语言选择以**进程**为单位，不以仓库或模块为单位。
- 跨语言只走两种边界：**可执行文件 + IPC**（默认），或**显式 C ABI**（例外，需登记）。
- Rust 不承诺稳定 C ABI；因此不允许「Rust 写一个 `.so` 给 C 调用」作为默认集成方式。

### 4.2 分层语言矩阵

| 层 | 语言 | 理由 |
|---|---|---|
| 内核（L0） | C（Linux 6.6 线） | ALK 是「基于 Linux 的微内核化改造」，不是新内核；内核 Rust 抽象层在 6.6 不完善 |
| glibc / systemd / rpm / dnf | 上游语言（C/C++） | 重写无产品收益，且破坏 ABI 兼容 |
| Qt / UKUI / 显示管理器 | 上游语言（C++/QML） | 桌面适配只做外挂，不改上游源码 |
| GRUB / anaconda / plymouth | 上游语言 | 只做配置与主题，不重写 |
| **全部自有新代码** | **Rust** | TUI、会话层、dock、输入网关、ASR 网关、新 CLI、新 daemon |
| 必须提供 C ABI 的模块 | C 或 Rust `cdylib`（例外） | 需 cbindgen 生成头文件 + 显式例外登记，禁止隐式导出 |

### 4.3 Rust 工具链事实与钉版

- openEuler 24.03 LTS-SP3 仓库提供 Rust 1.90 工具链，满足本项目需要；**不得依赖 rustup 在线安装**。
- 构建机必须在 `ci/container/build-packages.txt` 中显式列出 `rust` 与 `cargo`；当前该文件 94 行
  **0 条 Rust**，这是 0.0.5 的前置缺口（BC-061）。
- 所有 Rust 组件必须三件套齐全：`rust-toolchain.toml`（钉版本）、`Cargo.lock`（钉依赖）、
  vendor 或离线 crates 源（钉可得性）。当前三者皆无（BC-062/063/064）。
- 允许 stage0 预编译种子：Rust 无法完全自举，这是业界通用做法；种子二进制的 digest 必须进锁文件。

### 4.4 禁止事项

1. 禁止在 `kernel/` 下启用 `CONFIG_RUST`（0.0.30 前）；需要 Rust 的内核侧能力一律登记顺延。
2. 禁止用 Rust 重写 glibc/systemd/rpm/Qt 以「统一语言」；语言统一不是目标。
3. 禁止在 Rust 与 C 之间传递裸指针所有权；跨界只传 POD 或经 IPC 序列化。
4. 禁止为「将来可能用到」预建 Rust crate；每个 crate 必须有当期消费者。

### 4.5 例外审批

唯一例外通道：`distro/lockfile/lang-policy.yaml` 的 `exceptions` 列表。每条必须写
`path`、`language`、`reason`、`owner`、`expires`（版本号）。无 `expires` 的例外视为无效，
`ci/gates/lang-lock.sh` 直接判负。

---

## 5. 复刻性替换：三段式与四铁律

### 5.1 「对齐 openEuler 基底代码」的准确含义

对齐的是**四张表**，不是源码文本：

| 表 | 对齐内容 | 证据形式 |
|---|---|---|
| ABI 表 | syscall 号、结构体布局、ioctl 号、文件路径 | 头文件 diff + 运行时探针 |
| 行为表 | 退出码、错误码、输出格式、边界条件 | 差分语料（同输入两实现对比） |
| 布局表 | 文件安装路径、单元名、配置键、默认值 | `rpm -ql` 对比 + 配置快照 |
| 元数据表 | 包名、Provides/Obsoletes、版本段、依赖 | `rpm -q --provides/--requires` 对比 |

源码只在必要时阅读以确认行为，**不拷贝**。GPL 代码拷贝会改变本项目的许可证边界，
也会把上游的维护负债原样搬进来。

### 5.2 三段式

| 段 | 名称 | 动作 | 通过判据 |
|---|---|---|---|
| 1 | 冻结行为 | 为待替换包建立差分语料：正常路径、错误路径、边界值、并发路径 | 语料可复跑，旧实现 100% 通过 |
| 2 | 双跑等价 | 新实现在影子模式跑同一语料，与旧实现逐字段比对 | 差异为 0，或差异逐条登记为「有意变更」 |
| 3 | 单实现切换 | 切换默认实现，**删除旧实现**，更新 Provides/Obsoletes | 旧符号/旧文件在仓库内 0 命中，语料仍全绿 |

### 5.3 四铁律

1. **先语料后代码**：没有差分语料的包不得开工；「我觉得行为一样」不是判据。
2. **一次只切一处**：一个提交只切换一个包或一个入口；禁止批量切换后一次性验收。
3. **切换即删除**：禁止 `#if 0`、禁止 `OLD=1` 开关、禁止两份实现长期并存。回滚靠 git 回退到
   上一个 tag，不靠保留死代码。
4. **可观测等价**：判据只看外部可观测面（退出码、stdout/stderr、文件、协议），不看内部结构。
   内部结构允许不同，这正是「复刻行为而非复刻代码」的意义。

### 5.4 死代码防治（机器判据）

`ci/gates/lang-lock.sh` 与既有 `coupling-scan.sh` 共同承担：

- 仓库内不存在 `#if 0` 包裹的可执行代码块；
- 被替换包的旧符号在 `git grep` 中 0 命中；
- 不存在未被任何 spec/单元/入口引用的源文件（新增文件必须有消费者）；
- 不存在 `TODO: remove after switch` 类延期删除标记。

---

## 6. 永久双基底：一个契约层、两条独立通路

### 6.1 双基底的定义

「双基底」指同一套源码可以装配成两种发行形态：

| 形态 | 上游依赖 | 用途 |
|---|---|---|
| **上游基底形态** | openEuler 24.03 LTS-SP3（随 SP 前进） | 追新、硬件支持、上游 errata |
| **自有基底形态** | 自有仓库 + 自有构建闭包 | 供应自主、长期可维护 |

两种形态**共用同一套源码**，差异只出现在装配层（包选择、仓库地址、签名根）与通道层
（更新通道、发布通道）。**源码层不出现 `#ifdef AIRYMAX_SELF_BASE` 一类分支**。

### 6.2 两条独立通路（取代「两个渲染器」）

| 通路 | 入口 | 运行时 | 契约 |
|---|---|---|---|
| boot TUI 通路 | 开机 TUI（0.0.5） | 独立 Rust 会话层，**不链接 agentrt** | 共用 Intent schema 与 trace_id |
| dock 通路 | 桌面右侧 dock（0.0.6） | AirymaxRT gateway（HTTP/JSON-RPC + SSE） | 同上 |

两条通路共享的是**契约**（Intent、审批记录、trace_id、错误码），不是代码。任何「抽一个公共
渲染器给两边用」的提议都违反本裁定。

### 6.3 成本控制：两个对冲

| 对冲 | 机制 | 失效信号 |
|---|---|---|
| 节奏对冲 | 自有基底的 GA 不得晚于所追随上游 SP 的 EOL；由 `ci/gates/base-eol.sh` 与版本账本双断言 | 自有基底 GA 晚于上游 EOL → 供应断档 |
| 分叉对冲 | 每季度跑一次「同源断言」：两种形态的 `airy-*` 行为语料结果必须一致 | 差异 >0 且未登记 → 已分裂为两个产品 |

### 6.4 退出条件

永久双基底**不设退出条件**。0.1.1 只切换「默认发布形态」为自有基底，上游基底形态保留为
追新与回退通道。删除任一形态需要新的决策件，不在本册授权范围内。

### 6.5 「只在装配层」的代码级含义

「装配层」不是比喻，是**四个允许两形态不同的输入变量**。四个之外，任何差异都是缺陷。

| 变量 | 唯一来源（今日位置） | 消费点 | 上游形态 | 自有形态 |
|---|---|---|---|---|
| `airy_profile` | 构建命令行 `--define 'airy_profile …'` | 全部生成器与门禁 | `upstream` | `self` |
| `airy_oe_base` | `distro/repo/mirrors.list:12-18` 的首根 | `airymax-os.repo`、kickstart、`scripts/lib/closure.sh` | 上游 SP 路径 | 自有仓库路径 |
| `airy_sign_key` | 新增 `distro/sign/keys.yaml` | rpm 签名、`sign-file`、`sbsign` | 上游密钥 | 自有 MOK 密钥 |
| `airy_variant_id` | 由 profile 派生 | `/etc/os-release` | `upstream-base` | `self-base` |

四个变量之外**必须逐字相同**：113 条包名集合、`%dist`（当前为空）、glibc soname、
`PRETTY_NAME` 格式、内核 NEVRA 命名规则、`airy-*` 行为语料结果。

生成链是单向的，生成物不进 git：

```
distro/profiles/{upstream,self}.yaml
        │  distro/tools/profile_expand.py（唯一展开器）
        ▼
--define 'airy_profile …' / 'airy_oe_base …' / 'airy_sign_key …'
        ├── distro/repo/airymax-os.repo.in  → /etc/yum.repos.d/airymaxos.repo
        ├── distro/kickstart/*.ks.in        → .ks（anaconda 只认一个源）
        └── distro/specs/airymaxos-release.spec → rpmbuild
```

改造步骤（六步，每步一个提交，每步单独绿跑）：

1. 新增两份 profile（`schema: 1`），只写上述四个变量与闭包来源，不写任何包清单。
2. `distro/specs/airymaxos-release.spec:80` 的
   `%global oe_base openEuler-24.03-LTS-SP3` 改为 `%global oe_base %{?airy_oe_base}`；
   沿用该文件第 82 行既有约定——未传入即 `%{error:}` 硬失败，**不允许静默回落到某个形态**。
3. `distro/repo/airymax-os.repo` 改为 `.repo.in`，baseurl 用 `@AIRY_REPO_ROOT@` 占位；
   `%check`（第 398 / 549 / 550 行）的字面断言改为对展开值断言，条数仍是 5 / 5 / 5。
4. kickstart 第 37 行 `url --url=…` 由同一变量渲染；上游形态取 `mirrors.list` 首根。
5. `ci/gates/assemble.sh:118` 的 `closure-24.03-${ARCH}.lock` 改为
   `closure-${airy_profile}-${ARCH}.lock`：两形态各持一份锁，一份锁不能服务两种仓库。
6. 新增 `ci/gates/base-parity.sh`，判据即 §8 的 A-8。

**为什么不用条件编译**：源码层 `#ifdef` 会让两份产物共享一份二进制却行为不同，
差分语料只能覆盖编译期选中的那一支，死代码与「只测了一种形态」同时发生。
装配层分叉则两份产物各自完整，可分别跑全量语料。

---

## 7. 版本账本（0.0.5–0.1.1）

| 版本 | 主题 | 交付物 | 验收判据（摘要） |
|---|---|---|---|
| 0.0.5 | 全 Rust boot TUI + 四通道输入 | TUI、输入抽象层、librime 独立进程、ASR 网关、Rust 供应链前置 | 中文可输入可显示；四通道各有端到端路径与失败路径；无桩；主体七册三态登记齐（§11.4） |
| 0.0.6 | 智能体交互桌面 | Slint dock（默认 25%，20–40% 可调）、AirymaxRT 接入 | 对话可操作计算机；dock 宽度可调；GUI 输入走 IBus |
| 0.0.7 | 源码归档与四立项 | 上游源码快照、四份立项书（安装器/包管理/运行时/桌面） | 快照 digest 可核；立项书有验收判据 |
| 0.0.8 | 自有仓库 + T-03 | 自有仓库、签名根、内容寻址载荷通道 | 可发、可升、可按 digest 取件 |
| 0.0.9 | 自举预演 | 断网构建演练、失败清单 | 能列出缺哪些源码包，不要求补齐 |
| 0.0.10–12 | 供应源自持 | 镜像、锁文件、构建容器、宏 | 断网可解析全部构建依赖 |
| 0.0.13–15 | 对齐台账 | ABI/行为/布局/元数据四张表 + 差分语料框架 | 四表覆盖 500–900 闭包 |
| 0.0.16–19 | 核心工具群复刻替换 | `airy-*` 接管、包管理前端、磁盘、更新 | 每包 S1→S2，旧实现删除 |
| 0.0.20–23 | 运行时族 | init 边界、IPC、策略、会话 | 关键路径不依赖上游私有行为 |
| 0.0.24–26 | 内核与交付 | 内核包、initramfs、安装链 + 签名与安装器二选一决策登记 | 自有源码 + 自有签名可装；A-7 决策已登记 |
| 0.0.27–29 | 桌面与身份 | UKUI 适配、登录、os-release/身份 | 会话与输入可用；身份不冒充上游 |
| 0.0.30 | 双基底成形 | 两种形态同源装配 | 九条验收全绿（§8） |
| 0.0.31 | 只收口 | 缺陷修复、文档、缺口清单 | 不新增功能 |
| 0.1.0 | 过渡 | 默认形态切换预演 | 回退路径可用 |
| 0.1.1 | 稳定 | 默认发布形态 = 自有基底 | 双形态同源断言通过 |

### 7.1 前置约束

- 0.0.5 的 Rust 供应链前置**不能推迟**：没有钉版工具链，后续所有 Rust 交付都不可复现。
- 0.0.7–0.0.9 是 0.0.10 的必要准备，不得从 0.0.6 直接跳到 0.0.10。
- 0.0.31 是预览版最后一个；0.1.0 起不再接受「新增基底模块」，只做切换与修复。

---

## 8. 0.0.30 九条验收

| # | 判据 | 复算方式 |
|---|---|---|
| A-1 | 500–900 闭包内每个包都有 S1 或 S2 记录 | 台账逐包状态非 S0 |
| A-2 | 断网、空上游缓存下能构建出可启动镜像 | 隔离网络 + 空缓存构建 |
| A-3 | 自有仓库可发、可升、可回滚 | 三动作各一次，回滚后版本正确 |
| A-4 | 两种形态的 `airy-*` 行为语料结果一致 | 差分语料差异为 0 或已登记 |
| A-5 | 仓库内不存在双实现与死代码 | `#if 0` 0 命中、旧符号 0 命中 |
| A-6 | 内核 ABI 未变 | `uname -r` 线不变、syscall 号段不变、UAPI diff 为空 |
| A-7 | 签名链与 dist tag 可断言 | 两形态各自给出 shim 来源（上游沿用或 MOK 自有，二选一登记）；`%dist` 与 glibc soname 逐字一致；签名验收 S-1–S-6（§11.5）全绿 |
| A-8 | 装配层同源可复算 | `ci/gates/base-parity.sh` 退出 0：`#ifdef AIRY*` 0 命中、两形态 `os-release` 仅 `VARIANT_ID` 不同、包名集合差集仅限自有前缀与 Obsoletes 顶替 |
| A-9 | ABI 混装矩阵通过 | 四种组合（全上游 / 全自有 / 自有核心+上游桌面 / 上游核心+自有工具）装配全绿；`abi_snapshot.py --check` 无未登记差异；`rpm -Va` 无未登记输出；原地 `dnf upgrade` 与 `dnf downgrade` 各一次成功 |

九条全绿才算「自有基底完成」；任一条未过，0.0.30 不得发布，0.1.0 不得开工。

---

## 9. 不做什么

| 不做 | 理由 |
|---|---|
| 重写 glibc/systemd/rpm/Qt | 无产品收益，破坏 ABI，制造维护负债 |
| 内核启用 Rust | 6.6 抽象层不完善；ALK 的约束是「微内核化改造」而非「新内核」 |
| 源码层双实现 | 死代码之源；回滚靠 git，不靠开关 |
| 一次性全量替换 | 无法归因；违反「一次只切一处」 |
| 整站镜像上游仓库 | 流量与可见性都不可接受 |
| 追最新 SP | 小 SP 窗口 9 个月，交付即过保；只取 EOL 覆盖收口日的大 SP |

---

## 10. 相关文档与复算入口

- 清点册：[baseline-coupling.md](baseline-coupling.md)（BC-001–BC-070）
- 基底选型：[base.yaml](../../../../agent-linux/distro/lockfile/base.yaml)、`openeuler-sp-eol.md`
- 语言政策：`agent-linux/distro/lockfile/lang-policy.yaml`
- 输入契约：`docs-linux/30-interfaces/11-input-ingress.md`
- 版本图纸：`0.0.4-极境OS任务方案.md`、`0.0.5-极境OS任务方案.md`、`0.0.6-智能体交互桌面预立案.md`

```bash
# 在 agent-linux/ 仓库根执行，只读
grep -c '<packagereq' distro/comps/airymaxos-comps.xml
grep -in 'rust\|cargo' ci/container/build-packages.txt || echo 'Rust: 0'
grep -o 'baseurl=' distro/repo/airymax-os.repo | wc -l
ls distro/specs | wc -l
```

---

## 11. 第二轮补全（2026-11-17）：六部件、中间态三硬题、Rust 深边界

### 11.1 openEuler 基底的六个构成部件与我方实际消费形态

「基底」不是一个整体，换基底前必须先分清六个部件——每个部件的消费形态
与替换形态都不同，混为一谈才会得出「要重写 6,000 个包」的错误规模。

| # | 部件 | 内容 | 我方消费形态（取证） | 替换后的形态 |
|---|---|---|---|---|
| 1 | repodata 二进制包 | 约 6,000 源码包产出的全部二进制；comps 113 条是叶子 | 纯二进制消费 | 自有仓库（0.0.8）+ 闭包自持（0.0.10–12） |
| 2 | 内核 fork | 6.6 线 + openEuler 补丁 + `openeuler_defconfig` | **唯一消费源码处**（ALK 叠于其上） | 已自有；0.0.24–26 继续 |
| 3 | 工具链 | gcc/binutils/glibc、rpm 宏、rust/cargo 宏 | 隐式消费（构建容器 94 行） | S1 同源重建；窗口期 dist tag 不动 |
| 4 | 签名链 | openEuler 密钥签的 shim → GRUB → 内核 | BC-027；`shimx64.hash` 进介质（`build-desktop.sh:328`） | 0.0.24–26 决策点：MOK 自有密钥或上游 shim 沿用 |
| 5 | 安装器 | anaconda + lorax + comps 语义 + kickstart 语法 | 适配使用（W3） | 0.0.24–26 决策：继续适配 vs 另立自有安装器 |
| 6 | 发布与安全工程 | EBS 构建服务、errata/CVE 响应、镜像与 CDN | 未消费（我方走自有 CI） | 0.0.8–0.0.9 仓库自持；0.0.10–12 构建自持 |

**结论**：「替换基底」≠ 重写六部件。部件 2 已自有；1/3/6 是供应链自持
（工程问题，不写产品代码）；4/5 是两个必须显式决策的点，已登记为
0.0.30 验收 A-7 与 0.0.24–26 窗口判据。

### 11.2 中间态的三个硬问题（第一轮未覆盖）

逐步替换意味着存在一个「一半自有、一半上游」的长期中间态。该状态
有三个此前未回答的问题：

1. **ABI 共存**：自有包与上游包必须互相可解析。裁定：**glibc soname 与
   rpm `%dist` 标签在 0.0.30 前保持不变**；自有身份靠包名前缀
   （`airymaxos-*` / `airy_*`）表达，不靠 dist tag 分叉。dist tag 分叉
   会让 dnf 求解把两形态的包当成不同代际，双基底同源装配即失效。
2. **签名切换**：Secure Boot 链当前锚定 openEuler 密钥。自有形态要么
   MOK 注册自有密钥，要么沿用上游 shim 到 0.1.1。二选一在 0.0.24–26
   登记，不得拖到 0.0.30 才决定——A-7 即此判据。
3. **安全响应交接**：每把一个包从 S1 升到 S2，CVE 响应责任就从上游
   转到我方。容量约束裁定：**S2 只覆盖差异面**（§2.2 清点表的七个域 +
   TUI/dock），**S3 只覆盖供应链**（仓库/构建/签名），其余闭包包
   **长期停留 S1（同源重建，不接管补丁）**。A-1 的「S1 或 S2」中，
   S1 是默认落点而非过渡态——这是小团队维护 500–900 闭包唯一可行解。

### 11.3 Rust 的深边界：不是偏好问题，是有无对等物问题

- **关键路径（glibc/systemd/rpm/GRUB/anaconda）在 0.1.1 前没有成熟
  Rust 对等物**：uutils 可覆盖 coreutils 的 CLI 面，但 init、包管理求解、
  引导加载器均无生产级 Rust 实现。§4 的「上游保持既有语言」的深层理由
  是替换缺失，不是语言偏好。
- **Rust 进打包体系走上游 rust/cargo 宏**：openEuler 24.03 SP3 仓库内
  已有 Rust 1.90 与配套宏；`airy-tools-rs`（0.0.16）不自造宏，直接采用，
  否则每个 Rust 包的 spec 都是一座自维护孤岛。
- **uutils/coreutils 是唯一允许「社区 Rust 项目替代上游实现」的实例**，
  限定 CLI 面且必须过差分语料门禁；该例外不外推到其它上游组件。

### 11.4 0.0.5 范围风险的定量口径

docs-linux 实测 **21 个目录、190 份文档**。「全部功能基本实现」必须有
分母，否则「基本」不可判定。固定为功能面主体七册：

| 计入 TUI 实现分母 | 不计入（交付/运维/流程面） |
|---|---|
| 20-modules、30-interfaces、40-dataflows、110-security、170-performance、180-i18n、90-observability | 00-requirements、10-architecture、50/60/70/80（工程标准/驱动模型/构建/测试）、100/120/130/140/150/160/190、analysis |

主体七册内**每份文档**在 0.0.5 收口时登记三态之一：已消费 / 缺口已登记 /
不适用（注明归属版本）。该三态登记就是无桩判据的分母——缺登记即判负，
而不是「实现了大多数」即通过。

### 11.5 签名切换：改造步骤与验收

**今日事实**：上游包与 repodata 均无 PGP 签名，`distro/repo/airymax-os.repo` 的
`gpgcheck=0` / `repo_gpgcheck=0` 被 `airymaxos-release.spec` 的 `%check`（第 547–550 行）
写成 5 + 5 条字面断言；Secure Boot 链由 `distro/boot/efi_brand.sh` 整目录搬
`shimx64.efi` / `shimx64.hash` / `grubx64.efi` / `mmx64.efi`，shim 来自上游 `shim-x64`；
内核模块由 `CONFIG_MODULE_SIG_ALL=y` + `scripts/sign-file` 签
（`distro/specs/kernel/` 内 `%check` 已有「签名追加在文件尾、不是 ELF 段」的判据）。

**关键推论**：shim 只信任编译进它的证书与 MokList。因此「自签内核 + 上游 shim」不会自动成立，
必须把自有证书放进 MokList，否则开启 Secure Boot 的机器拒载。这就是二选一的技术实质：

| 选项 | 做法 | 装机交互 | 适用 |
|---|---|---|---|
| S-A 沿用上游 shim + MOK | shim 不变；自有 `kernel-sign` 证书首启经 `mokutil --import` 入 MokList | 一次人工确认（MokManager） | 开发机、内部试用 |
| S-B 自建 shim | 自有密钥签 shim，提交 Microsoft UEFI CA 签名 | 零交互 | 量产；周期以月计，0.1.1 前不保证 |

0.0.24–26 必须登记选择，未登记则 A-7 判负。

改造步骤（以 S-A 为例；S-B 只替换第 2、4 步的签名主体）：

1. 新增密钥台账 `distro/sign/keys.yaml`：三类密钥 `rpm-sign` / `module-sign` / `kernel-sign`，
   每条记 `id`、算法（RSA-4096 + SHA-256）、`not_after`、存储（离线 / HSM）、轮换策略。
   私钥不入库，CI 只拿 key id 与公钥。
2. RPM 签名：`%_gpg_name` 指向 `rpm-sign`；`rpmsign --addsign` 在 `assemble.sh` 收口前执行；
   `airymax-os.repo` 的 `gpgcheck` / `repo_gpgcheck` 由 0 改 1，`%check` 第 549–550 行的
   `-eq 5` 断言同步改为 1，并把仍存在的上游段排除在断言外。
3. 模块签名：内核 spec 的 `CONFIG_MODULE_SIG_KEY` 指向 `module-sign`；保留现有尾部签名判据，
   不改用 `readelf -S`。
4. 内核 PE 签名：`sbsign --key … --cert … --output vmlinuz.signed vmlinuz`，在 `%install`
   之后、打包之前执行。
5. 装机链：S-A 下 shim 不变；`mokutil --import airy-kernel.der` 于首次进系统时执行；
   未导入时状态栏报 `sb=unsigned`，不静默。
6. 新增 `ci/gates/signature-chain.sh`，判据即下表。

| # | 判据 | 复算 |
|---|---|---|
| S-1 | 全部 RPM 验签通过 | `rpm -K` 对闭包逐包 `digests signatures OK` |
| S-2 | 全部 `.ko` 由自有 key 签 | `modinfo -F signer` 全为 key id；开机 taint 不含 8192 |
| S-3 | 内核 PE 签名可上溯 | `pesign -S -i vmlinuz` 证书链末端 ∈ MokList |
| S-4 | 两种固件模式均可启动 | Secure Boot on / off 各一次装机 |
| S-5 | 轮换可回退 | 旧 key 签的包在换新 key 后仍可 `dnf install`（旧公钥保留一个版本周期） |
| S-6 | 门禁可判负 | 篡改任一包 / 模块 / 内核后对应命令必须失败（三个反例各一次） |

### 11.6 ABI 共存：改造步骤与验收

**今日事实**：`Release: %{airy_release}%{?dist}`，`%dist` 当前未定义、实际为空；
glibc / openssl 等 soname 全部来自上游二进制；自有包仅 4 份 spec 与 10 个 `airy-*` 入口。

**裁定**：0.0.30 前 `%dist` 保持为空、glibc soname 不变。自有身份靠包名前缀，
不靠 dist tag——dist tag 一旦分叉，dnf 会把两种形态当成不同代际，双基底立刻变成两个产品。

改造步骤：

1. ABI 基线快照 `distro/lockfile/abi-baseline.json`：字段 `nevra`、`provides_soname`、
   `requires_soname`，由 `distro/tools/abi_snapshot.py` 对 113 包生成，进锁文件；
   每次 S1→S2 切换后更新，差异必须登记。
2. 禁止 dist 分叉：CI 断言 `rpm --eval '%{?dist}'` 两形态一致，`git grep -n '^%define dist'`
   0 命中。
3. S1 包：同版本同 soname 重建，`rpm -q --provides` 与基线逐行相等（build-id 相关字段除外）。
4. S2 包：只允许两类——不提供 soname 的 CLI / daemon，或提供同名同 soname 的兼容实现。
   接管时写 `Provides: <上游名> = <上游EVR>`、`Obsoletes: <上游名> < <上游EVR>`；
   不得提高 epoch，不得改 soname。
5. 混装矩阵：`ci/gates/abi-coexist.sh` 跑四种组合（全上游 / 全自有 / 自有核心+上游桌面 /
   上游核心+自有工具），每种做全量 `dnf install` 求解、`ldconfig -p` 比对、`rpm -Va`。
6. 例外登记：任何有意 ABI 变更写 `distro/lockfile/abi-exceptions.yaml`，带 `path` / `reason` /
   `owner` / `expires`；无 `expires` 判负，与 `lang-policy.yaml` 的例外通道同构。

| # | 判据 | 复算 |
|---|---|---|
| B-1 | 四组合均可求解装配 | 四种组合 `dnf install` 全绿 |
| B-2 | soname 集合未变 | `abi_snapshot.py --check` 与基线 diff 为空或已登记 |
| B-3 | 文件级无冲突 | 四组合 `rpm -Va` 无非登记输出 |
| B-4 | dist tag 未分叉 | 两形态 `%{?dist}` 逐字相同 |
| B-5 | 旧包可被顶替 | 从上游形态原地 `dnf upgrade` 到自有形态，无需 `--allowerasing` |
| B-6 | 回退可逆 | 自有形态 `dnf downgrade` 回上游包成功 |

B-5 是真正的硬判据：它同时验证 `Obsoletes` 写法、epoch 未抬、依赖可解三件事；
B-1 到 B-4 都可能绿而 B-5 红。
