Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# docs-linux 功能归属册（0.0.5）

> **文档定位**：V-15 判据③的交付物。把 `docs-linux` 中每一块功能面逐条钉到「已实现」「0.0.5」「移出（承接版本 X）」三态之一。0.0.5 版把施工方案 §2.4 的裁撤落账：12 条内核侧条目与 CA-030、CA-089 改判移出，承接版本写进归属列。本册只登记事实，不提出新方案。
>
> **版本** 2.0.7 ｜ **最后更新** 2026-11-27 ｜ **密级**：内部机密（docs-closed）
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
| CA-028 | 桌面会话独立方案文档 | `190-distribution/07-session-entry.md` | 已实现 | 文档成文：状态面（`desired`/`mode`/`switch-reason` 三文件与写者闭包）、引导期 120 秒选择、运行期双向切换（顺序、就绪判据、90/15 秒超时与回滚）、注销回退、失败形态、打包归属与 AC-A3/AC-A10 验收 |
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
| CA-049 | 告警体系 | `100-operations/04-alerting.md` | 已实现 | `system/services/daemons/alert_d/`（模型/规则/引擎/持久化/守护/CLI 六层）、`system/bin/airy-alert{,d}`、默认规则随包安装到 `share/airymax/alert/rules.d`、独立单元 `airy-alert.service`；`ci/gates/alert-d.sh` 覆盖布局、出厂规则、五个包单测、守护与 CLI 的真实进程对跑及三条失败路径，`ops-verify.yml` 的 `alert-verify` 承接；285H 三架构触发验收待现场 |
| CA-050 | 事件响应 | `100-operations/05-incident-response.md` | 已实现 | `system/ops/incident/`（模型/台账/告警取样/复盘/命令行五层）、`system/bin/airy-incident`、内置运行手册安装到 `share/airymax/incident/runbooks`；状态机单一边表、台账编号与保留归档（常规 90 天、安全 365 天）、按告警编号幂等取样、检测到复盘闭环；`ci/gates/incident.sh` 覆盖布局、单测、三条失败路径与报告结构，`ops-verify.yml` 的 `incident-verify` 承接；与载荷 `airy-incident@.service` 分工见文档 §13.4；285H 三架构演练待现场 |
| CA-051 | 备份恢复 | `100-operations/06-backup-recovery.md` | 已实现 | `system/ops/backup/`（模型/归档/仓库/命令行四层）、`system/bin/airy-backup`、`airymax-backup.service` 与小时定时器；全量与增量按日编号、旁挂 `.sha256`/`.sig`、单件清单与全局索引、深核验、全量确认门、单 Agent 回放、篡改在解包前以 4 退出、保留期删旧留新且永远保留最新全量；`ci/gates/backup.sh` 覆盖布局、33 项单测、三条失败路径与保留期，`ops-verify.yml` 的 `backup-verify` 承接；285H 三架构恢复演练待现场 |
| CA-052 | systemd 集成 | `100-operations/07-systemd-integration.md` | 已实现 | `system/units/`、`system/tools/units_lint.py`、`system/tests/units/`；`ci/gates/mgmt-files.sh`、`ci/gates/mgmt-leaves.sh` |
| CA-053 | Agent 运维 | `100-operations/08-agent-operations.md` | 已实现 | `system/ops/agent/`（模型/存储/健康/调优/日志/命令行六层）、`system/bin/airy-agent`；8 态单一边表、六因素健康分按可得数据重归一化并给出覆盖度、调度与内存整组校验后才落盘、令牌预算与手动重置、元数据加锁原子写与终止归档、日志读取与保留归档受 log 组约束，跨节点迁移与滚动升级按单节点边界显式报错；`ci/gates/agent-ops.sh` 覆盖布局、36 项单测、三条失败路径、生命周期、日志权限、配置覆盖、迁移边界与打包接线，`ops-verify.yml` 的 `agent-verify` 承接；285H 三架构编排待现场 |
| CA-054 | 记忆运维 | `100-operations/09-memory-operations.md` | 已实现 | `system/ops/memory/`（模型/存储/统计/整理/迁移/擦除/审计/配置/命令行十二模块）、`system/bin/airy-memory`；数据块带魔数与版本，索引与实际项双向一致，全部变更在仓库同一把文件锁下完成，整理走暂存重建再原子替换并真实回收碎片，克隆保留源、移动移除源、敏感项与跨属主边界显式拒绝，覆写擦除按 quick/overwrite/secure 真实落盘并留审计，加密擦除在落盘前显式报不可用而不冒充完成；`ci/gates/memory-ops.sh` 覆盖布局、87 项单测、三条失败路径、碎片整理前后读数、擦除证据、配置覆盖与打包接线，`agent-verify.yml` 的 `memory-verify` 承接；285H 三架构观测待现场 |
| CA-055 | DevStation | `100-operations/10-devstation.md` | 已实现 | `system/ops/devstation/`（模型/采集/面板/渲染/终端/权限/审计/配置/解析/命令行十二模块）、`system/bin/airy-station`、出厂配置 `default.conf`：八类面板经既有 Agent、记忆、告警、事件、备份的公开接口取数，采集层按根目录参数化，缺源标为不可用并指明缺失路径而不出占位数；八项配置逐项校验，未知键与越界值退出 3；权限三级共用一张排序表，拒绝先写审计再退出 4，admin 动作需显式确认；Web 与远程传输属下一小版本，显式拒绝而不静默接受；出厂配置随包落成并在升级时保留，`%check` 与门禁逐项比对内建默认值；`Requires: ncurses-libs` 声明终端闭包，工作站配方已含 `airymaxos-system` 与 `airymaxos-kernel-devel`；`ci/gates/station-ops.sh` 覆盖布局、55 项单测、八面板读数、空源降级、权限与审计、坏配置、帧尺寸与镜像闭包，`station-verify.yml` 的 `station-verify` 承接；285H 起栈待现场 |
| CA-056 | 认知循环数据流 | `40-dataflows/01-cognition-flow.md` | 0.0.5 | 仅有 clt 单循环 syscall 与骨架，无 System1/2 分支与流编排 |
| CA-057 | 记忆卷载 L1 数据流 | `40-dataflows/02-memory-flow.md` | 已实现 | `memory/memoryrovol/mr_l1.c`、`kernel/kernel/syscalls/airy_rovol.c` |
| CA-058 | L1→L4 递进与 CXL/PMEM 数据流 | `40-dataflows/02-memory-flow.md` | 移出（0.0.24–0.0.26） | 需 DAX/CXL 内核能力，见 CA-008 |
| CA-059 | IPC 消息流（128 字节固定头） | `40-dataflows/03-ipc-flow.md` | 已实现 | `kernel/kernel/syscalls/airy_invoke.h`（128 字节头 + 编译期断言）、`kernel/security/airy/airy_ipc_freeze.c` |
| CA-060 | 调度数据流（EEVDF + RT 带宽） | `40-dataflows/04-scheduling-flow.md` | 已实现 | `kernel/kernel/syscalls/airy_sched.c`、`airy_sched_test.c`、`system/services/airymax_rt/` |
| CA-061 | 零拷贝 Ring Buffer 日志数据流 | `40-dataflows/05-ring-buffer-logging.md` | 已实现 | `kernel/kernel/log/`：`airy_log_ring` 固定 128B 记录环（reserve/commit 两阶段发布、覆盖写时 tail 前移、eventfd 唤醒、freeze、40B 头与 mmap 区），`airy_log_console` 以只写环的控制台把 printk 逐条送入并在注册时回放启动日志，`airy_log_dev` 经 `/dev/airy_log` 暴露 mmap 区与三条 ioctl，`logger_d` 的 `logd_ring` 按 mmap 只读消费、`logd_file` 是唯一落盘方（`/var/log/agentrt/airy.log`，按量/按时轮转）；`airy_log_ring_test.c` 九例覆盖容量、越界、裁剪、冻结、预留提交、条目守卫与释放；`ci/gates/kernel-obs.sh` 固化 `/sys/airy/log` 计数一致性，`ci/gates/tests-linux.sh` 固化 UAPI 布局；285H 环满与唤醒读数待现场 |
| CA-062 | Logger Daemon 详细设计 | `40-dataflows/06-logger-daemon-design.md` | 已实现 | `services/daemons/logger_d/`：`logd_ring`（环形缓冲）、`logd_file`（落盘与轮转）、`logd_cfg`（配置解析），`tests/` 覆盖三者 |
| CA-063 | Panic 生存路径 | `40-dataflows/07-panic-survival-path.md` | 移出（0.0.24–0.0.26） | 无 airy `panic_notifier` 与崩溃落盘钩子 |
| CA-064 | ftrace 框架与 airy tracepoint | `90-observability/01-ftrace-framework.md` | 已实现 | `kernel/include/trace/events/airy.h`（11 个 TRACE_EVENT）、`system/bin/airy-probe` |
| CA-065 | eBPF 可编程探针 | `90-observability/02-ebpf-probes.md` | 已实现 | `system/obs/ebpf/`：四个内核边界（`airy_cap_check`、`airy_clt_serve`、`airy_sched_ctl`、`airy_invoke_dispatch`）各一对 kprobe／kretprobe，加 `airy_policy_decision`／`airy_superv_enforce` 两个 tracepoint，共十个程序；加载器按规格表挂十条 link、失败按程序名报错，ringbuf 事件逐条输出 JSON 行；`ci/gates/ebpf-probe.sh` 固化四架构 defconfig 装载项、四符号非 static 且无 `notrace`／`__always_inline`、上下文顺序、map 尺寸、资源释放与 `-target bpf` 出树构建；285H 加载读数待现场 |
| CA-066 | perf 性能分析 | `90-observability/03-perf-analysis.md` | 已实现 | `system/obs/perf/`：`airy-perf` 只编排上游 perf——stat 落 CSV（六大硬件计数器，`-x,`）、record 以 99Hz+DWARF 采样、report 取前 20 项热点出 JSON、bench 把三段产物与 irq_balancing 读值归入同一目录；`ci/gates/perf-hooks.sh` 固化统计口径、只读边界、出树构建与三条入口失败路径；`obs-verify.yml` 的 `perf-verify` 作业承接；285H 采样读数待现场 |
| CA-067 | sysctl 控制面 | `90-observability/04-sysfs-procfs.md` | 已实现 | `kernel/security/airy/airy_cap_sysctl.c`（`/proc/sys/agentrt`） |
| CA-068 | sysfs 设备属性节点 | `90-observability/04-sysfs-procfs.md` | 已实现 | `kernel/kernel/obs/` 发布 `/sys/airy`（version/sec/superv/daemons/log/sched/ipc）与 `/proc/airy/fault_log`，只导出各子系统自用的真实计数；能力面 `/sys/airy/ipc/capabilities` 按 `AIRY_CAP_PERM_*` 位名逐 Agent 成行（`airy_obs_cap_perms`，超页给 `truncated: shown of total`）；预算面由 superv 发布 `superv/budgets/` 目录、token 按 Agent 建立只读文件并与 `token_stats` 同源，`superv/macro/budget_alerts` 输出开机以来档位上升次数（`tok_note` 只在档位上升时计数）；`ci/gates/kernel-obs.sh` 固化注册时序、只读属性、清单一致性与上述三处节点；285H 读值待现场 |
| CA-069 | tracefs 接口 | `90-observability/05-debugfs-tracefs.md` | 已实现 | `kernel/security/airy/airy_probe.c`、`kernel/include/trace/events/airy.h` |
| CA-070 | debugfs 接口 | `90-observability/05-debugfs-tracefs.md` | 已实现 | `kernel/kernel/obs/airy_obs_debugfs.c` 以 `fs_initcall` 发布 `/sys/kernel/debug/airy/{sec/cap_table,superv/last_decision,log/ring_buffer_dump}`，仅补稳定面无法提供的原始信息且不导出防伪标签，设计文档明确本版只发布三个有真实数据源的节点；`ci/gates/kernel-debugfs.sh` 固化注册时序、只读节点、机密边界与四架构调试基线；285H 读值待现场 |
| CA-071 | user_events 接口 | `90-observability/06-user-events.md` | 0.0.5 | 内核侧契约表已发布：`kernel/kernel/obs/airy_uevent.c` 经 sysfs 导出事件族，UAPI `include/uapi/linux/airymax/user_events.h` 带尺寸断言，四架构与 agent 片段开启 `CONFIG_USER_EVENTS`；`ci/gates/kernel-uevent.sh` 固化契约。缺口是守护进程侧的注册与上报链（`DIAG_IOCSREG`）尚未接入 |
| CA-072 | Token 效率监控 | `90-observability/07-token-efficiency.md` | 已实现 | 内核只出事实：`kernel/kernel/obs/airy_token.c` 按 Agent 累计四类计数，维护 60 秒观测窗口与 1 小时预算窗口，比例统一 ppm，`/proc/airy/agents/<id>/token_stats` 只读快照与 `/dev/airy_token` 三条 ioctl 并存，上报校验调用者身份与 SEND、预算改写校验 SUPERVISE；`include/uapi/linux/airymax/token.h` 带三处布局断言，`airy_token_test.c` 覆盖进位、窗口回绕与档位边界；`system/obs/token/` 的 `airy-token` 提供 show/top/budget/report 且只透传不重算；`ci/gates/token-obs.sh` 固化口径、字段面双向对齐与出树构建，`obs-verify.yml` 的 `token-verify` 作业承接；285H 读数与 TUI 面板接线待现场 |
| CA-073 | Agent 行为追踪 | `90-observability/08-agent-tracing.md` | 已实现 | `airy_agent_state_change`、`airy_superv_enforce` 事件；`system/services/airymax_probe/` |
| CA-074 | 记忆监控 | `90-observability/09-memory-monitoring.md` | 已实现 | 内核只出事实：`kernel/kernel/obs/airy_mem.c` 按 Agent 维护 L1–L4 四层的访问、命中、延迟、淘汰、页与字节吞吐、模式条数与占用，比例统一 ppm，配额 0 表示未设限，档位（NORMAL/SOFT/DEGRADE/EXCEED）只供读者判断，处置留给 macro_d；`/proc/airy/agents/<id>/memory_stats` 只读快照与 `/dev/airy_mem` 四条 ioctl 并存，上报与占用校验调用者身份与 SEND、配额改写校验 SUPERVISE；`include/uapi/linux/airymax/mem.h` 带四处布局断言，`airy_mem_test.c` 覆盖档位边界、窗口滚动与占用绝对覆盖；`system/obs/mem/` 的 `airy-mem` 提供 show/top/quota/gauge/report 且只透传不重算；`ci/gates/mem-obs.sh` 固化四层字段面、鉴权位置与出树构建，`obs-verify.yml` 的 `mem-verify` 作业承接；285H 读数与 TUI 面板接线待现场 |
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
| 已实现 | 70 |
| 0.0.5 | 11 |
| 移出（承接版本） | 14 |
| **合计** | **95** |

本表不是手抄的旁注：`ci/ci.sh completeness` 逐格核对它与明细行数，改明细必须
同轮重算本表，否则门禁判负。

**未归属条目：0。**

三态分布的两个结构性结论：

1. 「移出（承接版本）」14 条：12 条落在内核侧（驱动模型 6 条、io_uring 2 条、printk/panic 2 条、记忆 L2–L4 2 条），与「内核侧净新增 0 行」的边界完全重合；另外 2 条是 CA-030（ostree，按 §2.4 裁为 0.1.x）与 CA-089（MemoryRovol CSI，随 CA-008 移出）。没有一条用户态工作是单纯被版本边界挡下的。
2. 「0.0.5」11 条里，5 条的缺口是「只有单元/文档、没有二进制或数据面」（CA-012、071、079、084、085），接口已经摆好，缺的是承载实现。

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
- **留在账上 24 条**：按 docs-linux 设计锚点分布如下。发布前每条必须落成
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
