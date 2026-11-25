# TUI 实机与降级取证记录

> 适用版本：0.0.5 ｜ 密度：内部 ｜ SSoT：`0.0.5-极境OS任务方案.md` §14.13、§15.4
>
> 本文定义 V-04 的取证记录格式、必测格局与门禁用法。格式的判定实现在
> `system/tui/crates/boot-tui/tests/field/main.rs`，采集器在
> `ci/tools/tui_field_collect.sh`。三处改动必须同批：键集、用例名、判定词
> 任何一处单独变动，都会让记录「看起来有数据、统计时全落空」。

## 1. 为什么要把夹具与实机分开

实机取证最常见的失真不是伪造数据，而是把开发机上的演练记录混进发行台账。
因此记录用 `evidence` 硬分两类：

| 取值 | 含义 | 统计口径 |
|---|---|---|
| `field` | 目标机读数，带 `when` 与 `host` | 只有它能计入发版覆盖 |
| `fixture` | 仓库内的格式夹具，用例必须带 `fixture-` 前缀 | 只验证格式，永不计入覆盖 |

发版覆盖只统计 `evidence=field` 且 `result=pass` 的记录。夹具、失败读数与
`unavailable` 都不计入；失败读数还会让整个取证包判负。

## 2. 记录格式

每条记录是一段纯文本：`AIRYMAX-TUI-FIELD/1` 起，`AIRYMAX-TUI-FIELD-END` 止，
中间一行一个 `键=值`。空行只允许出现在记录之间；记录内不允许空行、未知键、
重复键。一个取证包里可以有多条记录，也可以有多个 `*.field` 文件。

| 键 | 必填 | 值域 / 说明 |
|---|---|---|
| `case` | 是 | 下表八个用例之一；夹具必须写成 `fixture-<用例>` |
| `evidence` | 是 | `field` 或 `fixture` |
| `arch` | 是 | `x86_64` / `aarch64` / `riscv64` |
| `os` | 是 | `/etc/os-release` 的 `PRETTY_NAME` |
| `build` | 是 | `/etc/airymaxos-build` 的 `BUILD_ID` |
| `when` | 实机必填 | UTC 秒级 ISO-8601，如 `2028-01-31T09:00:00Z` |
| `host` | 实机必填 | 机器标识（可用 `AIRYMAX_HOST_ID` 脱敏），不允许空白 |
| `term` | 是 | 采集时的 `TERM` |
| `cols` / `rows` | 是 | 正整数；采集时取自 `stty size` |
| `observed` | 是 | 操作者看到的事实，单行、非空 |
| `result` | 是 | `pass` / `fail` / `unavailable` / `blocked` |
| `note` | 否 | 补充说明，单行 |
| `screenshot` | 否 | 截图的小写 sha256（64 位十六进制） |

示例（实机）：

```
AIRYMAX-TUI-FIELD/1
case=ime-recover
evidence=field
arch=x86_64
os=AirymaxOS 0.0.5
build=20280131
when=2028-01-31T09:00:00Z
host=lab-01
term=linux
cols=85
rows=24
observed=ime=recovering;candidates=listed
result=pass
AIRYMAX-TUI-FIELD-END
```

## 3. 必测格局

降级矩阵的七格加中文显示一项，共八格。覆盖要求按出厂能力面分版：

- **0.0.5 口径（八格中的四格）**：`probe-stale`、`render-slow`、`tty-small`、
  `display-zh`，`x86_64` 与 `aarch64` 各一份 `pass` 实机记录（8 格）。本版
  出厂 TUI 只随包 `boot-tui`、`airy-session-pick`、`airy-session-mode` 三个
  可执行文件，输入面为键盘单通道；四格全部可在该能力面上触发。
- **N2/N3 起（其余四格）**：`ime-recover`、`ime-no-dict`、`asr-unavailable`、
  `inject-unknown` 依赖 `boot-ime` 常驻进程与 `asr-gateway` 通道（施工图纸
  §14.1、N2 泳道 D27 起）。在对应能力随包之前，这四格在实机上**不可触发**，
  采集器记 `result=unavailable` 并写明依据；`unavailable` 不计入覆盖，也不
  冒充通过。

`riscv64` 记入报告但不要求：本版 riscv64 用户态移出范围。

| 用例 | 触发条件 | 期望的可观测事实 |
|---|---|---|
| `ime-recover` | 输入法后端异常退出 | 界面不退出，恢复后候选恢复 |
| `ime-no-dict` | 词典缺失或损坏 | 显式显示降级，不静默吞键 |
| `asr-unavailable` | 语音模型未安装 | 通道标记 unavailable，文本输入可用 |
| `probe-stale` | 状态面契约不可读或过期 | 状态面显示未知，不伪造读数 |
| `render-slow` | 帧预算超限 | 降级到基本绘制，仍可操作 |
| `inject-unknown` | 未知输入通道 | 拒绝并留下可判定的原因 |
| `tty-small` | 终端小于最小尺寸 | 版面折叠，不丢关键状态 |
| `display-zh` | 中文显示验收（AC-V4） | 字形与断行正确，附截图摘要 |

## 4. 采集流程

在目标机上（TTY 内）执行：

```sh
ci/tools/tui_field_collect.sh --out ~/field --case ime-recover \
    --observed "ime=recovering;candidates=listed" --screenshot ~/shot.png
```

采集器只读本机事实：`/etc/os-release` 的 `ID` 必须是 `airymaxos`，
`/etc/airymaxos-build` 必须给出 `BUILD_ID`，终端尺寸取自 `stty size`。
开发机不是 AirymaxOS 时采集器拒绝写记录，这是校验在起作用，不是故障。

同一格（`arch` + `case`）不允许覆盖；需要重测时先人工确认后移除旧记录，
避免同一格出现两份互相矛盾的读数。

仓库内的格式夹具用 `--fixture --arch … --cols … --rows …` 生成，
产出记录固定带 `fixture-` 前缀，不进入实机台账。

## 5. 门禁与回归

```sh
ci/ci.sh tui-field                    # 格式自检 + 仓库夹具
ci/ci.sh tui-field --input ~/field    # 发版口径：实机覆盖（0.0.5 为 8 格）
```

不带 `--input` 时只证明「格式不会被误读」；带 `--input` 时，缺格、
`result=fail`、或把夹具混进实机都会判负。覆盖集由校验器里的 `RELEASE_CASES`
给出，与 `DEFERRED` 合起来恰好等于八格矩阵；通道随包时在同一提交里把名字
从 `DEFERRED` 移入 `RELEASE_CASES`。参数契约与采集器拒绝路径由
`ci/tests/test_tui_field.sh` 覆盖，随 lint 流水线执行。
