# AirymaxOS 终端验证命令墙

> **版本 v0.0.3** ｜ 2026-10-30 ｜ 密级：内部机密（docs-closed）
>
> Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

面向评审与实机验收的可复现命令集。**全部命令在装机后的 AirymaxOS 终端内执行，只读，
不需要 root 增权以外的任何准备**（标注 `sudo` 的除外）。目标是让「系统是什么」与
「系统在做什么」两类问题都能被第三方在任意一台同版本机器上复现。

## 0. 使用与防造假

三条铁律，写在命令之前：

1. **命令先于数字**。展示的任何数值都必须由文档中的命令当场产出，不引用截图、不引用
   历史记录。评审可要求重跑，重跑必须得到同量级结果。
2. **口径写在同一行**。每个数字都带单位、样本数与统计方式（如 `p50/p99`、`N 次中位数`）。
   没有口径的数字不展示。
3. **留证用原生工具**。`airy-record` 基于 util-linux `script(1)`，整场终端输出与时间轴
   分别落盘为 `typescript` 与 `timing`，`scriptreplay` 可原样回放。录屏文件本身可被
   评审带走并回放，不依赖任何私有格式。

**关于抖动**：真实测量的分位数不会两次完全一致。同一台机器上重复运行 `airy-bench`，
p50 波动在 ±5% 以内、p99 波动在 ±15% 以内属正常；如果两次结果**逐位相同**，反而是
测量被缓存或被伪造的信号。这一点本身就是可复现性的证据。

**关于执行位置**：第 16–20 条与 `airy-observe` / `airy-demo` 的会话类字段读的是
「本地图形会话」（`loginctl` 的 `seat0`、`DISPLAY`、`xrandr`）。在 SSH 会话里这些
来源不存在，`airy-observe` 会给出 `status=partial`、`airy-demo` 给出
`status=degraded`——那是采集面缺失，不是系统故障。内核态条目（第 3–15 条）、
网络（第 21–24 条）、启动（第 25–29 条）、IPC（第 30–34 条）在 SSH 下与本地一致，
可放心远程取证。

## 1. 身份与归属（系统是什么）

| # | 命令 | 看什么 | 判定 |
|---|---|---|---|
| 1 | `hostnamectl` | `Operating System` / `Kernel` / `Architecture` 三行 | 版本行含 `AirymaxOS` 与版本号（如 `AirymaxOS 0.0.3 (OpenAirymax)`）；主机名为 `AIRYMAX_PC`（`/etc/hostname` 与内核名一致；systemd 会按 RFC 1123 去掉下划线，运行期名由 `sysctl.d/99-airymax-hostname.conf` 写回） |
| 2 | `cat /etc/os-release` | `PRETTY_NAME`、`ID`、`VERSION_ID` | `ID=airymaxos`，非 openEuler 的投影 |
| 3 | `uname -srm` | 内核名、版本、架构 | 形如 `Linux 6.6.157-alk x86_64`；`-alk` 后缀是自有内核标识 |
| 4 | `cat /proc/version` | 编译者与编译器 | `(airymax@build)` 与 `gcc 13.3.0`，证明内核由本项目构建 |
| 5 | `rpm -qf /boot/vmlinuz-$(uname -r)` | 内核文件归属 | 输出 `airymaxos-kernel-core-<版本>-<release>.x86_64` |
| 6 | `rpm -V airymaxos-kernel-core; echo rc=$?` | 已安装文件与 RPM 数据库比对 | `rc=0` 且无输出，说明运行中的内核未被替换 |
| 7 | `cat /proc/cmdline` | 引导参数 | 含 `BOOT_IMAGE=/vmlinuz-<ver>-alk`、`root=UUID=…`、`resume=UUID=…` |
| 8 | `sudo grubby --default-kernel` / `sudo grep -m1 '^menuentry' /boot/efi/EFI/airymaxos/grub.cfg` | 引导项与菜单名 | 默认内核为 `-alk`；菜单名首词为 `AirymaxOS`（本机实测 `menuentry 'AirymaxOS (6.6.157-alk) 0.0.3 (OpenAirymax)'`）。两条都要 `sudo`：`grubby` 读 `/etc/grub2-efi.cfg` 需 root；本产品的 grub.cfg 生成在 ESP，`/boot/grub2/` 只有 `grubenv`，按旧路径查会得到 `No such file or directory` |

第 5、6 条是「内核归属」的硬证据：前者说明文件来自本项目 RPM，后者说明运行中的内核
与安装时刻逐字节一致。二者缺一，品牌就可能只是改了个字符串。

## 2. 内核能力面（AirymaxOS 特有）

| # | 命令 | 看什么 | 判定 |
|---|---|---|---|
| 9 | `cat /sys/kernel/security/lsm` | 已启用的 LSM 链 | 链中含 `airy` 与 `airy_lockdown`（本机实测 `airy_lockdown,lockdown,capability,yama,airy,selinux`） |
| 10 | `cat /proc/sys/agentrt/present` | Agent 运行时是否在内核侧就位 | `1` |
| 11 | `sysctl kernel.airy.` | 能力折叠的四个旋钮 | `cap_epoch_bits`、`cap_max_agents`、`cap_randtag_bits`、`cap_used` 四项齐全（本机为 16 / 1024 / 32） |
| 12 | `ls /sys/kernel/security/airy/` | 执法面出口 | 存在 `policy` 与 `lockdown` |
| 13 | `sudo cat /sys/kernel/security/airy/policy` | 策略表 | 表头 `# name hook rows evals allow deny audit complain fault` 与当前条目。必须 `sudo`：普通用户读该文件返回 `Permission denied`，与「策略为空」在屏幕上都是空结果，容易误判 |
| 14 | `sudo dmesg \| grep -E 'airy\|Airymax'` | 启动期自检结论 | 含 `airy contract: 59 [SC] invariants verified (ABI v4)`、`registered 5 Micro-Supervisor hooks`、`Airymax ALK-0.1.1` |
| 15 | `sudo ls /sys/kernel/tracing/events/airy/`（或 `/sys/kernel/debug/tracing/events/airy/`） | 事件面注册情况 | 10 个事件：`airy_ipc_send`/`airy_ipc_recv`/`airy_sched_switch`/`airy_sched_latency`/`airy_agent_state_change`/`airy_policy_decision`/`airy_superv_enforce`/`airy_ring_buffer_write`/`airy_lockdown_change`/`airy_lockdown_reject`。须 `sudo`：tracefs 的 `events/` 对非 root 关闭，非 root 执行得到 `Permission denied`，与「事件未注册」不可区分 |

第 15 条**只证明事件已注册，不证明事件被触发**。这些 tracepoint 的调用点位于
corekern 的 agent IPC 路径，普通进程的 `pipe()`/`socketpair()` 不经过，因此终端里
不会刷出事件。该缺口的补齐已登记为 0.0.4 的 `KRN-01`（需 `/dev/airy` 注入通道 +
示例客户端）。**在补齐之前，不得以 trace_pipe 的空输出或人为构造的事件行充当证据。**

## 3. 桌面与会话（能登录、分辨率对）

| # | 命令 | 看什么 | 判定 |
|---|---|---|---|
| 16 | `loginctl show-session $(loginctl \| awk '/seat0/{print $1; exit}') -p Type -p Remote -p Seat` | 会话类型 | `Type=x11`、`Remote=no`、`Seat=seat0`，说明本地图形会话已建立 |
| 17 | `systemctl --user is-system-running` | 用户会话管理器 | `running` |
| 18 | `ps -e --no-headers \| wc -l` / `pgrep -c ukui` | 进程规模与桌面组件 | UKUI 组件在列；进程总数与版本基线同量级（0.0.3 实测 22 个 UKUI 进程、总进程数 313，判据取 `pgrep -c ukui >= 20`：进程数随会话与实际加载的面板项浮动，逐位比对会把正常波动当成故障） |
| 19 | `xrandr --current \| head -3` | 生效分辨率与驱动 | 首选模式与面板一致；`Screen 0: minimum … current WxH` 行给出实际值。必须在桌面会话内执行（本地终端，或 `DISPLAY=:0`）：SSH 会话没有 `DISPLAY`，输出 `Can't open display` 是环境问题而非桌面故障 |
| 20 | `ls /run/airymaxos/ && head -20 /run/airymaxos/xserver-*.conf` | 启动期生成的 X 配置 | 存在 `xserver-*.conf`，内容为 modesetting/fbdev 选择结果 |

第 19 条的口径边界：Xorg 1.20.11 在部分新平台上不接管 `simpledrm`，此时分辨率由
固件单模式决定，属于已知限制（`D-06` / `D-32`），不应记为桌面故障。

## 4. 网络（联网可用）

| # | 命令 | 看什么 | 判定 |
|---|---|---|---|
| 21 | `ip -br addr show` | 接口与地址 | 无线或有线接口为 `UP`，持有 IPv4 地址 |
| 22 | `nmcli -t -f DEVICE,STATE,CONNECTION device` | NetworkManager 状态 | 目标设备 `connected` 且连接名非空 |
| 23 | `curl -sS -o /dev/null -w '%{http_code} %{time_total}s\n' https://mirrors.huaweicloud.com/` | 端到端连通性与耗时 | HTTP 状态码 `200`；耗时按当日网络计，只在同一会话内横向比较 |
| 24 | `dnf -q makecache && echo rc=$?` | 仓库闭包可用性 | `rc=0`，说明 `/etc/yum.repos.d` 的段集可解析（`D-05` 的实机判据） |

## 5. 启动与稳定性

| # | 命令 | 看什么 | 判定 |
|---|---|---|---|
| 25 | `systemd-analyze` | 固件 / 引导 / 内核 / 用户态四段耗时 | 四段均给出毫秒到秒级实数，末行 `= …s` 为总计 |
| 26 | `systemd-analyze blame \| head -10` | 最慢的十个单元 | 无异常长尾；同一机器两次运行排序基本一致 |
| 27 | `systemctl --failed --no-legend \| wc -l` | 失败单元数 | `0` |
| 28 | `journalctl -b -p err --no-pager \| wc -l` | 本次引导的错误级日志条数 | 与上一版本同量级；新增条目需能逐条归因 |
| 29 | `sudo smartctl -H /dev/nvme0n1`（若安装 `smartmontools`） | 磁盘健康 | `PASSED`；未安装时此条不演示，不得以 `dmesg` 替代 |

## 6. IPC 与并发（可测量）

| # | 命令 | 看什么 | 判定 |
|---|---|---|---|
| 30 | `airy-bench` | 三族往返时延与吞吐 | 每族给出 `rtt_p50_us`/`rtt_p99_us`/`rate`；同一机器重复运行 p50 波动 ≤5%、p99 ≤15% |
| 31 | `for i in 1 2 3 4 5; do airy-bench \| grep rtt_p99; done` | 重复测量的分布 | 五轮数值不逐位相同，且中位数与单轮接近 |
| 32 | `taskset -c 0-7 airy-bench --procs 8 \| grep fork` | 8 进程聚合吞吐与扩展比 | 输出行含 `rate` 与 `scale`，`scale > 1`（本机实测 1.29M 往返/秒、`scale=3.64`） |
| 33 | `dd if=/dev/zero of=/tmp/airy.bin bs=1M count=64 conv=fdatasync 2>&1 \| tail -1` | 顺序写带宽 | 给出 `MiB/s`；结束后 `rm -f /tmp/airy.bin` |
| 34 | `for i in 1 2 4 8; do taskset -c 0-$((i-1)) airy-bench --procs $i \| grep fork; done` | 并发扫描曲线 | 1/2/4/8 的聚合吞吐上升但边际递减，出现拐点属正常 |

第 30–34 条的量纲是**进程间通信往返**，不是网络往返，也不是磁盘 IO。口径必须随数字
一起展示，否则容易被误读为「比 Linux 快多少」——AirymaxOS 的对照基线就是同一台机器上
的同一套 syscall，不做跨系统比较。

## 7. 留证与复现

| # | 命令 | 用途 |
|---|---|---|
| 35 | `airy-observe` | 一份 `key=value` 的全机对账，末行 `mode=` / `status=`，`status != ok` 时非零退出，可直接进 CI |
| 36 | `airy-observe --static` | 构建期口径（镜像内核对），与活体报告同字段名 |
| 37 | `airy-demo` | 把 observe 与 bench 排成一张终端总览，含 1/2/4/8 并发中位数扫描；不产生新数字 |
| 38 | `airy-record --tty --out /tmp/airy-session -- airy-demo` | 把一次 demo 全程连同时间轴录下；`scriptreplay /tmp/airy-session.timing /tmp/airy-session` 原样回放（`--tty` 不采画面，只录终端字节） |
| 39 | `sha256sum $(command -v airy-observe airy-bench airy-demo airy-record) && rpm -qf $(command -v airy-observe)` | 把二进制钉到包上：摘要 + 归属，评审可核对演示用的就是发行版里的那四个文件 |

第 39 条是整套演示的锚：任何一段录像里出现的数字，都能通过这四个二进制的摘要与 RPM
归属回溯到具体版本，录像与二进制不能各说各话。

## 8. 明确不展示的内容

以下三项在 0.0.4 补齐 `KRN-01` 之前不进入任何演示材料：

- `trace_pipe` 实时事件流（普通进程无法驱动 corekern 路径，缓冲区恒空）；
- `kernel.airy.cap_used` 的增长曲线（无用户态投递通道，恒为 0）；
- `/sys/kernel/debug/airy_stc/stats` 的四类调度计数（同上，四项恒为 0）。

能展示的是它们的**注册状态与配置值**（第 11、15 条），这两类信息真实且可核。
把「已注册」说成「在工作」，是本次参赛材料唯一必须主动回避的夸大。

## 9. 一次跑完

若只需一条命令产出全部证据：

```
airy-record --tty --out /tmp/airy-session -- airy-demo
```

`airy-demo` 内部依次调用 `airy-observe` 与 `airy-bench`，两者都不写系统状态，
因此这一条命令同时产出全机对账与 IPC 分位；`airy-record` 只追加
`/tmp/airy-session` 与 `/tmp/airy-session.timing` 两个文件。回放：

```
scriptreplay /tmp/airy-session.timing /tmp/airy-session
```

三者都可安全重复执行，重跑不会污染系统状态。