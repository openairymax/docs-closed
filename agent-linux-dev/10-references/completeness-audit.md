Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# docs-linux 功能归属册（0.0.5）

> **文档定位**：V-15 判据③的交付物。把 `docs-linux` 中每一块功能面逐条钉到「已实现」「0.0.5」「移出（承接版本 X）」三态之一。0.0.5 版把施工方案 §2.4 的裁撤落账：12 条内核侧条目与 CA-030、CA-089 改判移出，承接版本写进归属列。本册只登记事实，不提出新方案。
>
> **版本** 2.0.1 ｜ **最后更新** 2026-11-23 ｜ **密级**：内部机密（docs-closed）
>
> **主要读者**：0.0.5 执行人、发布评审、交付链维护者。

## 1. 判定口径

### 1.1 三态定义

| 归属 | 判定条件 |
|---|---|
| 已实现 | 仓库内存在可指认的实现（源码、单元、打包定义、脚本之一），且至少有一条可复核的验证入口（门禁、测试或装机后命令） |
| 0.0.5 | 功能面在本版边界内可以做，但仓库内无实现；或实现只到「接口/单元」一层，缺承载它的二进制与数据面 |
| 移出（承接版本 X） | 本版不为它留 WP、判据与日历，承接版本写在括号内；括号为空即视为「未归属」，本册不接受 |

「未归属」不是第四态，是本册不允许出现的缺陷。

### 1.2 证据要求

- **路径证据**：相对 `agent-linux/` 仓库根的路径，必须能在工作树中打开。文档类产物不算实现证据（`docs-linux` 自身、`*.md` 说明不计入「已实现」）。
- **门禁证据**：写 `ci/gates/<name>.sh` 全路径，文件必须存在且带 `# 用法:` 头（否则 `ci/ci.sh --list` 看不到它）。裸脚本名不构成证据——它无法定位到文件。
- **设计锚点**：锚点列指向 `docs-linux/` 内的设计文档，必须能打开；指不到设计出处的条目不计入任何一态。
- **命令证据**：装机后可执行的只读命令（如 `airy-observe system --json`、`systemctl --failed`）。
- **反例优先**：只有单元文件、没有二进制的功能面判为 0.0.5，并在备注写明缺哪个二进制；`airy-incident@.service` 即按此办理（`distro/specs/airymaxos-system.spec` 的 0.0.4-32 条目与 `system/tools/units_lint.py` 均记录 `airyctl` 与 `airy` 账户不在本版镜像内）。

### 1.3 复核方式

本册可被第三方从头重算，不需要作者在场：

1. 跑 `ci/ci.sh completeness`：三态计数、统计表与明细一致、证据路径与设计锚点落地、
   门禁可用性一次判完。
2. 发布前跑 `ci/ci.sh completeness --release`：账上不许再有 0.0.5。
3. 抽查「已实现」行是否真能执行：门禁跑得通，或装机后命令有输出。
4. 抽查「0.0.5 / 移出」行是否确实缺件：备注里点名的二进制、目录或门禁在仓库内不存在。

2026-11-23 范围裁定：当时仍标 `0.0.5` 的 34 条平台功能面**全部在本版实现**，
任务卡见同目录 `0.0.5-平台功能面范围.md` 的 P-01–P-31；发版口径不变，
`completeness --release` 仍以「账上无 0.0.5」判负。

## 2. 功能归属主表

| 编号 | 功能面 | docs-linux 锚点 | 归属 | 证据 / 缺口说明 |
|---|---|---|---|---|
| CA-001 | 内核 airy 系统调用面（invoke/clt/rovol/sched/sysabi） | `20-modules/01-kernel.md` | 已实现 | `kernel/kernel/syscalls/`（5 组实现 + 5 组 KUnit）；`ci/gates/kernel-airy.sh` |
| CA-002 | 内核安全控制面（securityfs 目录 + sysctl） | `20-modules/01-kernel.md` | 已实现 | `kernel/security/airy/airy_fs.c`、`airy_cap_sysctl.c`；`ci/gates/kernel-kunit.sh` |
| CA-003 | 服务框架与 Macro-Supervisor 客户端对接 | `20-modules/02-services.md` | 已实现 | `services/daemons/macro_d/`、`kernel/kernel/superv/` |
| CA-004 | 服务单元集与依赖排序 | `20-modules/02-services.md` | 已实现 | `system/units/`（15 个 `agentrt-*` + `airymax-agent.slice`）；`system/tools/units_lint.py`；`ci/gates/mgmt-files.sh` |
| CA-005 | airy LSM 钩子与 Capability 模型 | `20-modules/03-security.md` | 已实现 | `kernel/security/airy/airy_lsm.c`、`airy_cap_*.c`；`ci/gates/kernel-airy.sh` |
| CA-006 | io_uring 安全加固 | `20-modules/03-security.md` | 移出（0.0.24–0.0.26） | `kernel/io_uring/` 无 airy 改动；需内核补丁与基线抬升，§2.3 禁止 |
| CA-007 | MemoryRovol L1 卷载 | `20-modules/04-memory.md` | 已实现 | `memory/memoryrovol/mr_l1.c`、`kernel/kernel/syscalls/airy_rovol.c` |
| CA-008 | 记忆 L2–L4 递进层与 CXL/PMEM | `20-modules/04-memory.md` | 移出（0.0.24–0.0.26） | 仅 L1 存在；L2–L4 依赖 DAX/CXL 内核能力 |
| CA-009 | CoreLoopThree 主循环骨架 | `20-modules/05-cognition.md` | 已实现 | `cognition/coreloopthree/clt_main.c`、`kernel/kernel/syscalls/airy_clt.c` |
| CA-010 | 双系统思考与 thinkdual 分支 | `20-modules/05-cognition.md` | 0.0.5 | 仓库内无 thinkdual/System1-2 实现，仅有单循环 syscall |
| CA-011 | agentctl 云原生入口 | `20-modules/06-cloudnative.md` | 已实现 | `cloudnative/agentctl/agentctl.c`（CMake 目标 `agentctl`） |
| CA-012 | CRD/CRI 与 K8s 侧交付 | `20-modules/06-cloudnative.md` | 0.0.5 | 仅 `cloudnative/Documentation/{crd,agentctl}.md`，无 CRD manifest 与控制器 |
| CA-013 | 系统服务集（磁盘/观测/电源/RT/模型/亮度/升级） | `20-modules/07-system.md` | 已实现 | `system/services/{airydisk,airymax_observe,airymax_power,airymax_rt,airyllm,airybright,airyupdate}/` |
| CA-014 | 系统软件包定义与版本宏 | `20-modules/07-system.md` | 已实现 | `distro/specs/airymaxos-system.spec`、`distro/specs/macros.airymax`；`ci/gates/release-rpms.sh` |
| CA-015 | 内核 KUnit/kselftest 执行面 | `20-modules/08-tests-linux.md` | 已实现 | `kernel/kernel/syscalls/{airy_clt,airy_invoke,airy_rovol,airy_sched,airy_sysabi}_test.c`、`kernel/kernel/superv/airy_superv_{ring,fault,wdog,adjud,exec,proto}_test.c`；`ci/gates/kernel-kunit.sh`、`ci/gates/kernel-kselftest.sh` |
| CA-016 | 用户态单元测试套件 | `20-modules/08-tests-linux.md` | 已实现 | `tests-linux/unit/` 四例契约单测（`test_{ipc_magic,error_codes,log_ring_uapi,superv_uapi}.c`）在 CTest 下全跑；`ci/gates/tests-linux.sh` 断言导出头硬前提、出树构建、全绿与套件形态（≥4 例、`unit` 标签）；`c-verify.yml` 的 `tests-linux build & ctest` 作业承接 |
| CA-017 | Micro-Supervisor 内核模块 | `20-modules/09-kernel-agent-supervisor.md` | 已实现 | `kernel/kernel/superv/`（ring/fault/wdog/adjud/exec/proto，6 组测试） |
| CA-018 | Macro-Supervisor 守护进程源码 | `20-modules/10-user-supervisor-daemon.md` | 已实现 | `services/daemons/macro_d/macro_d.c` + `CMakeLists.txt` |
| CA-019 | Macro-Supervisor 入镜像 | `20-modules/10-user-supervisor-daemon.md` | 已实现 | `distro/specs/airymaxos-system.spec` 以 `--target config_d logger_d macro_d` 出树构建并安装 `%{_sbindir}/macro_d`、`macro-superv.conf` 与 unit；`ci/gates/c-verify.sh` 的 services 腿跑守护进程单测 |
| CA-020 | A-UCS 统一配置守护进程 | `20-modules/11-unified-config.md` | 已实现 | `services/daemons/config_d/`（`cfg_core`/`cfg_ini`/`cfg_sys` 分层 + `tests/` + `etc/config.conf`）；spec 构建并安装 `config_d`、`agentrt.conf`；热加载与非法版本拒绝已在 285H 实机验收 |
| CA-021 | A-ULP Logger Daemon 模块 | `20-modules/12-logger-daemon-module.md` | 已实现 | `services/daemons/logger_d/`（`logd_ring`/`logd_file`/`logd_cfg` + `tests/` + `etc/logger.conf`）；spec 构建并安装 `logger_d` 与 `logger.conf` |
| CA-022 | printk 桥接 | `20-modules/13-printk-bridge.md` | 移出（0.0.24–0.0.26） | `kernel/kernel/printk/` 无 airy 改动；桥接需内核侧新增 |
| CA-023 | RPM 打包规范与三包定义 | `190-distribution/01-rpm-packaging.md` | 已实现 | `distro/specs/{airymaxos-system,airymaxos-release,airymaxos-firmware}.spec`；`ci/gates/release-rpms.sh` |
| CA-024 | dnf 仓库、lockfile 与 comps | `190-distribution/02-dnf-repo-design.md` | 已实现 | `distro/repo/`、`distro/lockfile/`、`distro/comps/`、`tools/repo-scaffold/`；`ci/gates/release-deps.sh` |
| CA-025 | 载荷通道（seed/publish/取件） | `190-distribution/02-dnf-repo-design.md` | 已实现 | `ci/gates/payload-seed.sh`、`ci/gates/payload-publish.sh`、`ci/gates/channel-fetch.sh`、`ci/gates/media-fetch.sh` |
| CA-026 | 安装器与两档 kickstart profile | `190-distribution/03-installer-design.md` | 已实现 | `distro/kickstart/airymaxos-{minimal,workstation}.ks`；`ci/gates/disk-layout.sh`、`ci/gates/qemu-setup.sh`、`ci/gates/accept.sh` |
| CA-027 | 装机后桌面就绪与 UKUI 会话 | `190-distribution/03-installer-design.md` | 已实现 | `distro/desktop/airy_observe.sh`、`distro/desktop/xinitrc.d/70-airymax-im.sh`；`ci/gates/session-closure.sh`、`ci/gates/desktop-capability.sh`、`ci/gates/ukui-lock.sh` |
| CA-028 | 桌面会话独立方案文档 | `190-distribution/03-installer-design.md` | 0.0.5 | §2.3 已登记：`docs-linux` 无独立桌面方案，R1 以 installer 与 `20-modules/07-system.md` 为锚点 |
| CA-029 | 升级检查 / 状态 / 会话提醒 | `190-distribution/04-update-mechanism.md` | 已实现 | `system/services/airyupdate/`、`system/bin/airy-update`、`system/units/airymax-update-check.{service,timer}` |
| CA-030 | ostree / 分层 rootfs 切换 | `190-distribution/04-update-mechanism.md` | 移出（0.1.x） | `distro/ostree/` 仅 README 与 `airymaxos-workstation.treefile`，无产物链；两处口径冲突按施工方案 §2.4 裁为移出，0.1.x 重新取口径 |
| CA-031 | 可重现构建与来源证明 | `190-distribution/05-reproducible-build.md` | 已实现 | `ci/gates/build-provenance.sh`、`ci/gates/build-drift.sh`、`ci/gates/attest.sh`、`ci/gates/release-source.sh` |
| CA-032 | SBOM 生成与发布审计 | `190-distribution/06-sbom-generation.md` | 已实现 | `ci/gates/release-sbom.sh`、`ci/gates/release-audit.sh` |
| CA-033 | 设备枚举与硬件能力矩阵 | `60-driver-model/01-device-model.md` | 已实现 | `system/services/airymax_observe/hw.py`；`ci/gates/hw-matrix.sh` |
| CA-034 | device/driver/bus 绑定实现 | `60-driver-model/01-device-model.md` | 移出（0.0.24–0.0.26） | `kernel/drivers/` 无 `airy*` 驱动；需内核侧新增 |
| CA-035 | platform 总线与 SoC 设备适配 | `60-driver-model/02-platform-driver.md` | 移出（0.0.24–0.0.26） | 同上；本版只做固件闭包（`ci/gates/fw-closure.sh`） |
| CA-036 | devm 资源托管与智能体资源扩展 | `60-driver-model/03-devm-resource.md` | 移出（0.0.24–0.0.26） | 无内核实现；与「内核净新增 0 行」冲突 |
| CA-037 | misc 字符设备框架 | `60-driver-model/04-misc-framework.md` | 移出（0.0.24–0.0.26） | `/dev/airy` 注入节点在 §2.3 明确顺延 |
| CA-038 | Agent 虚拟设备驱动 | `60-driver-model/05-agent-driver.md` | 移出（0.0.24–0.0.26） | 无 airy 虚拟设备驱动源码 |
| CA-039 | VFIO 直通与 IOMMU 隔离 | `60-driver-model/06-vfio-passthrough.md` | 移出（0.0.24–0.0.26） | 属内核配置与驱动变更，§2.3 禁止 |
| CA-040 | 驱动测试框架（KUnit 执行面） | `60-driver-model/07-driver-testing.md` | 已实现 | `ci/gates/kernel-kunit.sh`、`ci/gates/kernel-analyze.sh`；内核树内 KUnit 用例 |
| CA-041 | Kbuild 递归构建 | `70-build-system/01-kbuild-system.md` | 已实现 | `ci/gates/kernel-build.sh`、`ci/gates/kernel-refbuild.sh`、`ci/gates/build-budget.sh` |
| CA-042 | Kconfig 与 defconfig 矩阵 | `70-build-system/02-kconfig-system.md` | 已实现 | `tools/defconfig-matrix/`、`tools/kbuild-version/`；`ci/gates/kernel-deps.sh`、`ci/gates/kernel-consistency.sh` |
| CA-043 | BTF 与类型导出 | `70-build-system/02-kconfig-system.md` | 已实现 | `tools/btf-integration/`；`ci/gates/kernel-analyze.sh` |
| CA-044 | CI/CD 管道与门禁体系 | `70-build-system/03-ci-cd-pipeline.md` | 已实现 | `ci/ci.sh`（77 个 gate）、`.github/workflows/`、`ci/workflow-budgets.txt`；`ci/gates/ssot-verify.sh` |
| CA-045 | 部署体系（ISO / QEMU / 裸机） | `100-operations/01-deployment.md` | 已实现 | `ci/gates/iso-publish.sh`、`ci/gates/iso-checksum.sh`、`ci/gates/image-verify.sh`、`ci/gates/qemu-setup.sh`、`ci/gates/accept.sh` |
| CA-046 | 配置管理（preset / firstboot / 交付清单） | `100-operations/02-configuration.md` | 已实现 | `distro/presets/`、`system/scripts/firstboot.sh`；`ci/gates/system-inventory.sh` 断言 `/etc/airymaxos-packages` |
| CA-047 | A-UCS 配置总线运行时 | `100-operations/02-configuration.md` | 已实现 | `services/daemons/config_d/`：启动装载、合法修改热重载、非法版本拒绝保留旧值、`SIGHUP` 重载、不可热改项冻结、主配置缺失降级只读；实机八项验收通过 |
| CA-048 | 监控体系 | `100-operations/03-monitoring.md` | 已实现 | `system/services/airymax_observe/`（hw/fw/sys）、`system/units/agentrt-health-check.service`；`ci/gates/system-inventory.sh` |
| CA-049 | 告警体系 | `100-operations/04-alerting.md` | 0.0.5 | 仅 `system/services/airymax_power/notify.py` 会话级提醒；无告警路由、抑制、升级链路 |
| CA-050 | 事件响应 | `100-operations/05-incident-response.md` | 0.0.5 | `airy-incident@.service` 只有单元接口；`/usr/sbin/airyctl` 与 `airy` 账户属 agentrt 载荷，未入本版镜像 |
| CA-051 | 备份恢复 | `100-operations/06-backup-recovery.md` | 0.0.5 | 仓库无备份/快照实现与对应门禁 |
| CA-052 | systemd 集成 | `100-operations/07-systemd-integration.md` | 已实现 | `system/units/`、`system/tools/units_lint.py`、`system/tests/units/`；`ci/gates/mgmt-files.sh`、`ci/gates/mgmt-leaves.sh` |
| CA-053 | Agent 运维 | `100-operations/08-agent-operations.md` | 0.0.5 | 无 agent 生命周期 CLI 与运维面；`macro_d` 仅源码未入包 |
| CA-054 | 记忆运维 | `100-operations/09-memory-operations.md` | 0.0.5 | 无记忆卷运维工具；内核侧仅 L1 |
| CA-055 | DevStation | `100-operations/10-devstation.md` | 0.0.5 | 无工作站镜像/profile 与工具链闭包定义 |
| CA-056 | 认知循环数据流 | `40-dataflows/01-cognition-flow.md` | 0.0.5 | 仅有 clt 单循环 syscall 与骨架，无 System1/2 分支与流编排 |
| CA-057 | 记忆卷载 L1 数据流 | `40-dataflows/02-memory-flow.md` | 已实现 | `memory/memoryrovol/mr_l1.c`、`kernel/kernel/syscalls/airy_rovol.c` |
| CA-058 | L1→L4 递进与 CXL/PMEM 数据流 | `40-dataflows/02-memory-flow.md` | 移出（0.0.24–0.0.26） | 需 DAX/CXL 内核能力，见 CA-008 |
| CA-059 | IPC 消息流（128 字节固定头） | `40-dataflows/03-ipc-flow.md` | 已实现 | `kernel/kernel/syscalls/airy_invoke.h`（128 字节头 + 编译期断言）、`kernel/security/airy/airy_ipc_freeze.c` |
| CA-060 | 调度数据流（EEVDF + RT 带宽） | `40-dataflows/04-scheduling-flow.md` | 已实现 | `kernel/kernel/syscalls/airy_sched.c`、`airy_sched_test.c`、`system/services/airymax_rt/` |
| CA-061 | 零拷贝 Ring Buffer 日志数据流 | `40-dataflows/05-ring-buffer-logging.md` | 0.0.5 | `kernel/kernel/superv/airy_superv_ring.c` 是 IPC 环冻结状态机，非日志环；缺日志环与消费者 |
| CA-062 | Logger Daemon 详细设计 | `40-dataflows/06-logger-daemon-design.md` | 已实现 | `services/daemons/logger_d/`：`logd_ring`（环形缓冲）、`logd_file`（落盘与轮转）、`logd_cfg`（配置解析），`tests/` 覆盖三者 |
| CA-063 | Panic 生存路径 | `40-dataflows/07-panic-survival-path.md` | 移出（0.0.24–0.0.26） | 无 airy `panic_notifier` 与崩溃落盘钩子 |
| CA-064 | ftrace 框架与 airy tracepoint | `90-observability/01-ftrace-framework.md` | 已实现 | `kernel/include/trace/events/airy.h`（11 个 TRACE_EVENT）、`system/bin/airy-probe` |
| CA-065 | eBPF 可编程探针 | `90-observability/02-ebpf-probes.md` | 0.0.5 | 无 BPF 程序与加载链；探针现走 tracefs（`system/services/airymax_probe/`） |
| CA-066 | perf 性能分析 | `90-observability/03-perf-analysis.md` | 0.0.5 | 无 airy perf 集成；仅 `system/bin/airy-rt-lat.c` 单点延迟测量 |
| CA-067 | sysctl 控制面 | `90-observability/04-sysfs-procfs.md` | 已实现 | `kernel/security/airy/airy_cap_sysctl.c`（`/proc/sys/agentrt`） |
| CA-068 | sysfs 设备属性节点 | `90-observability/04-sysfs-procfs.md` | 0.0.5 | 无 airy sysfs 节点；现用 securityfs 与 sysctl |
| CA-069 | tracefs 接口 | `90-observability/05-debugfs-tracefs.md` | 已实现 | `kernel/security/airy/airy_probe.c`、`kernel/include/trace/events/airy.h` |
| CA-070 | debugfs 接口 | `90-observability/05-debugfs-tracefs.md` | 0.0.5 | 无 airy debugfs 节点 |
| CA-071 | user_events 接口 | `90-observability/06-user-events.md` | 0.0.5 | 未使用 user_events；需内核 config 与用户态注册链 |
| CA-072 | Token 效率监控 | `90-observability/07-token-efficiency.md` | 0.0.5 | 无 token 计量实现（`airyllm` 只做运行环境与状态） |
| CA-073 | Agent 行为追踪 | `90-observability/08-agent-tracing.md` | 已实现 | `airy_agent_state_change`、`airy_superv_enforce` 事件；`system/services/airymax_probe/` |
| CA-074 | 记忆监控 | `90-observability/09-memory-monitoring.md` | 0.0.5 | 无记忆卷监控模块 |
| CA-075 | LSM 框架接入 | `110-security/01-lsm-framework.md` | 已实现 | `kernel/security/airy/airy_lsm.c`、`airy_superv_lsm.c`；`ci/gates/kernel-airy.sh` |
| CA-076 | Landlock 用户态沙箱 | `110-security/02-landlock-sandbox.md` | 0.0.5 | 无 Landlock 规则集与沙箱封装 |
| CA-077 | Capability 安全模型 | `110-security/03-capability-model.md` | 已实现 | `kernel/security/airy/airy_cap_{array,derive,rotate,check,sysctl}.c` 及测试 |
| CA-078 | IPC 数据面自治三原则 | `110-security/04-ipc-data-plane-autonomy.md` | 已实现 | `kernel/security/airy/airy_ipc_freeze.c`、`airy_eventfd.c`、`airy_contract_check.c` |
| CA-079 | IPC 控制面 Reconciliation | `110-security/05-ipc-control-plane-reconciliation.md` | 0.0.5 | 只有 policy 评估与 superv 裁决，无期望态比对与 reconcile 循环 |
| CA-080 | io_uring 加固 | `110-security/06-io-uring-hardening.md` | 移出（0.0.24–0.0.26） | 同 CA-006 |
| CA-081 | 纯 C LSM 模块实现 | `110-security/07-airy-lsm-design.md` | 已实现 | `kernel/security/airy/`（32 个文件，含 10 个 KUnit 测试源） |
| CA-082 | Lockdown 阶梯 | `110-security/09-lockdown.md` | 已实现 | `kernel/security/airy/airy_lockdown.c`、securityfs `airy/lockdown`、`airy_lockdown_test.c` |
| CA-083 | 安全策略 DSL 编译器 | `110-security/10-policy-compiler.md` | 已实现 | `tools/dsl/`（lexer/parser/semantics/codegen + tests）、`tools/dsl/examples/security_policy.adl` |
| CA-084 | 决策表内核运行时接入 | `110-security/10-policy-compiler.md` | 0.0.5 | 生成物 `security_policy_tables.h` 无任何 C 侧消费者；内核仍走 `airy_policy.c` 自带规则 |
| CA-085 | K8s CRD | `150-cloudnative/01-k8s-crd-design.md` | 0.0.5 | 仅 `cloudnative/Documentation/crd.md`，无 CRD manifest 与 reconciler |
| CA-086 | containerd shim | `150-cloudnative/02-containerd-shim.md` | 0.0.5 | 无 shim 实现 |
| CA-087 | CNI 网络策略 | `150-cloudnative/03-cni-network-policy.md` | 0.0.5 | 无 CNI 插件与 NetworkPolicy 实现 |
| CA-088 | 超节点 OS | `150-cloudnative/04-supernode-os.md` | 0.0.5 | 无实现 |
| CA-089 | MemoryRovol CSI | `150-cloudnative/05-memoryrovol-csi.md` | 移出（0.0.24–0.0.26） | 依赖 L2–L4（CA-008，已随内核窗口移出），且无 CSI 驱动 |
| CA-090 | Locale 设计与生成 | `180-i18n/01-locale-design.md` | 已实现 | `system/services/airylocale/`（矩阵 8 条 + `list/show/gen/check`）、`system/bin/airy-locale`；`ci/gates/locale-matrix.sh`；两个剖面语言包与装机段 `airy-locale check --require-generated` |
| CA-091 | UTF-8 严格编码原语 | `180-i18n/02-encoding-spec.md` | 已实现 | `kernel/include/airymax/airy_utf8.h`、`kernel/kernel/corekern/charset/airy_utf8_test.c` |
| CA-092 | 编码设置与转换面 | `180-i18n/02-encoding-spec.md` | 已实现 | `system/services/airycharset/`（`scan`/`conf`/`cli` 三层 + 默认 `charset.conf`）、共用的 `system/services/airylib/`、`system/bin/airy-charset`、`system/tests/services/`、`ci/gates/charset.sh`；spec 以源包装入 `%{_sysconfdir}/agentrt/charset.conf` 与站点包，workstation 装机段判负 |
| CA-093 | 错误消息国际化 | `180-i18n/03-error-message-i18n.md` | 已实现 | gettext 域 `airymaxos`：`services/tools/error-msg/error_msg.py` 由 [SC] 错误码契约生成映射表与 `po/airymaxos.pot`，`po/zh_CN.po` 全量覆盖；运行期 `services/common/error_msg.c` 经 `dgettext` 查目录并回退；`ci/gates/i18n.sh` 重生成比对并断言无空译文 |
| CA-094 | CJK 输入法与字体落位 | `180-i18n/04-cjk-support.md` | 已实现 | `distro/desktop/xinitrc.d/70-airymax-im.sh`；`distro/specs/airymaxos-release.spec` 断言 `ibus-daemon` 与 `unicode.pf2` |
| CA-095 | 文档国际化 | `180-i18n/05-doc-i18n.md` | 已实现 | 各子模块 `README.md` / `README_zh.md` 成对；`ci/gates/docs-links.sh` 校验链接 |

## 3. 统计

| 归属 | 条目数 |
|---|---|
| 已实现 | 56 |
| 0.0.5 | 25 |
| 移出（承接版本） | 14 |
| **合计** | **95** |

**未归属条目：0。**

三态分布的两个结构性结论：

1. 「移出（承接版本）」14 条：12 条落在内核侧（驱动模型 6 条、io_uring 2 条、printk/panic 2 条、记忆 L2–L4 2 条），与「内核侧净新增 0 行」的边界完全重合；另外 2 条是 CA-030（ostree，按 §2.4 裁为 0.1.x）与 CA-089（MemoryRovol CSI，随 CA-008 移出）。没有一条用户态工作是单纯被版本边界挡下的。
2. 「0.0.5」25 条里，14 条的缺口是「只有单元/文档、没有二进制或数据面」（CA-012、028、049、050、053、054、055、061、065、068、071、079、084、085），接口已经摆好，缺的是承载实现。

## 4. 复核入口

以下命令在 `agent-linux/` 仓库根执行，输出与本册 §3 对账。

```sh
# 1) 三态对账：计数、统计表、证据路径、门禁头、设计锚点一次判完
#    归属册缺席时自动跳过；显式 --doc 给错则退 5
ci/ci.sh completeness
ci/ci.sh completeness --json     # 机器可读：合计/已实现/0.0.5/移出

# 2) 发布前判据：账上不许再有 0.0.5
ci/ci.sh completeness --release
```

`--release` 是「登记缺口」与「移出范围」的分界线（施工方案 §2.4）：发布前
每条缺口必须落成已实现或移出（承接版本），不接受「还没做」。

装机侧的对应命令（第三态之外的第二证据面）：

```sh
systemctl --failed
journalctl -p err -b --no-pager | wc -l
airy-observe system --json
```

## 5. 36 条缺口的对账

0.0.5 的进度口径是 19 个功能模块的端到端覆盖（施工方案 §2.5），36 条缺口
是其中的明细登记，不单独计进度。本版开工时的对账结果：

- **移出 2 条**：CA-030（ostree，按 §2.4 裁为 0.1.x 重新取口径）、
  CA-089（MemoryRovol CSI，依赖的 CA-008 已随内核窗口移出）。
- **留在账上 25 条**：按 docs-linux 设计锚点分布如下。发布前每条必须落成
  已实现或移出（承接版本），由 `ci/ci.sh completeness --release` 强制。

| 设计锚点 | 留在账上的缺口 |
|---|---|
| `100-operations/04-alerting.md` | CA-049 |
| `100-operations/05-incident-response.md` | CA-050 |
| `100-operations/06-backup-recovery.md` | CA-051 |
| `100-operations/08-agent-operations.md` | CA-053 |
| `100-operations/09-memory-operations.md` | CA-054 |
| `100-operations/10-devstation.md` | CA-055 |
| `110-security/02-landlock-sandbox.md` | CA-076 |
| `110-security/05-ipc-control-plane-reconciliation.md` | CA-079 |
| `110-security/10-policy-compiler.md` | CA-084 |
| `150-cloudnative/01-k8s-crd-design.md` | CA-085 |
| `150-cloudnative/02-containerd-shim.md` | CA-086 |
| `150-cloudnative/03-cni-network-policy.md` | CA-087 |
| `150-cloudnative/04-supernode-os.md` | CA-088 |
| `190-distribution/03-installer-design.md` | CA-028 |
| `20-modules/05-cognition.md` | CA-010 |
| `20-modules/06-cloudnative.md` | CA-012 |
| `40-dataflows/01-cognition-flow.md` | CA-056 |
| `40-dataflows/05-ring-buffer-logging.md` | CA-061 |
| `90-observability/02-ebpf-probes.md` | CA-065 |
| `90-observability/03-perf-analysis.md` | CA-066 |
| `90-observability/04-sysfs-procfs.md` | CA-068 |
| `90-observability/05-debugfs-tracefs.md` | CA-070 |
| `90-observability/06-user-events.md` | CA-071 |
| `90-observability/07-token-efficiency.md` | CA-072 |
| `90-observability/09-memory-monitoring.md` | CA-074 |
