#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0
# Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
"""AirymaxOS 0.0.4 施工图纸种子（人工只改本文件）。

本种子只声明「做什么、多大、先后」，不写任何任务卡：
任务卡由 bp_004_gen.py 按 50 行/任务切分（硬上限 300 行/任务，全版任务数 ≥1000），
再按泳道产能（150 行/泳道/施工日 = 3 个任务）拓扑排程——细化任务只增加检查点，不拉长日历。
与 0.0.3 的关系：0.0.3 的种子读自主图纸（bp_seed.py），0.0.4 的种子是
「0.0.3 实测输入清单 §2 遗留债 + 用户十项主任务」的重裁结果，因此独立成文件，
不改 bp_seed.py（主图纸仍按原账本对账）。
"""

# ---------------------------------------------------------------- 模块

MODULES = [
    # id, 名称, 承接的用户任务, 说明
    ("L", "流水线与交付链", "①⑤", "门禁归零、供应链治理、构建预算台账、内容寻址候选池、发布同源、安装介质品牌面收敛"),
    ("T", "烧录系统", "⑤", "取件器、引导盘/载荷两层交付、烧录回归取证"),
    ("M", "发行版工程与磁盘管理", "②③⑧", "磁盘设备模型与操作面、系统盘与数据盘双分区布局、安装器选盘、命名规范、UKUI 闭包、openEuler 基底按大 SP 与 EOL 规则选型"),
    ("R1", "UKUI 追新与桌面适配", "②⑨", "仓库实测 NVRA 与版本线取证、适配层增量、锁屏根因、桌面显式依赖、日常使用强化、内置壁纸收敛为 3 张"),
    ("I", "硬件使能与固件闭包", "⑥", "固件闭包门禁、cmdline、显示策略通用化、引导副本、W^X、RTC、网络子系统使能"),
    ("K", "系统服务：磁盘服务与大模型环境", "③④", "大模型运行环境预置、资产通道、加速降级、离线自检、磁盘服务"),
    ("X", "AirymaxRT 全方位适配", "⑦", "RT 带宽根因、注入通道驱动、能力探测、实时性验收、共存策略"),
    ("V", "验证与验收", "全部", "实机取证矩阵、判负集分层、会话闭环、发布自证、升级通道、模块签名与 taint 复核、系统完整性盘点"),
]

MODULE_ORDER = ["L", "T", "M", "R1", "I", "K", "X", "V"]

# 模块 ↔ docs-linux 方案锚点（用户口径：所有开发都要遵循 docs-linux 设计方案）。
# 路径相对 docs/ 目录；锚点为空或文件不存在则该模块不得开工（J-34，引擎在 check() 里判）。
MODULE_DOCREF = {
    "L": ["docs-linux/70-build-system/03-ci-cd-pipeline.md",
          "docs-linux/190-distribution/05-reproducible-build.md",
          "docs-linux/190-distribution/06-sbom-generation.md"],
    "T": ["docs-linux/190-distribution/03-installer-design.md",
          "docs-linux/100-operations/01-deployment.md"],
    "M": ["docs-linux/190-distribution/01-rpm-packaging.md",
          "docs-linux/190-distribution/02-dnf-repo-design.md",
          "docs-linux/190-distribution/03-installer-design.md"],
    # docs-linux 对桌面会话覆盖薄弱（仅 installer 提及 UKUI），R1 的第二锚点取系统模块，
    # 缺口本身登记进 §2.3 与 V-15 盘点，不假装有桌面方案文档。
    "R1": ["docs-linux/190-distribution/03-installer-design.md",
           "docs-linux/20-modules/07-system.md"],
    "I": ["docs-linux/60-driver-model/01-device-model.md",
          "docs-linux/60-driver-model/07-driver-testing.md"],
    "K": ["docs-linux/140-application-development/06-agent-deployment.md",
          "docs-linux/100-operations/07-systemd-integration.md"],
    "X": ["docs-linux/40-dataflows/04-scheduling-flow.md",
          "docs-linux/00-requirements/03-non-functional-requirements.md"],
    "V": ["docs-linux/80-testing/03-kernel-selftests.md",
          "docs-linux/100-operations/03-monitoring.md"],
}

# ---------------------------------------------------------------- 泳道

LANES = [
    # id, 名称, 说明
    ("L1", "CI 结构", "内联块下沉、供应链固定、checkout 与计时"),
    ("L2", "CI 载荷", "构建预算台账、候选池 L1、内容寻址层 L2"),
    ("L3", "CI 发布", "发布同源与对账、构建器清理、来源证明、耦合点清点"),
    ("T1", "烧录前端", "取件器、引导盘"),
    ("T2", "烧录后端", "载荷通道、回归取证"),
    ("M1", "磁盘操作面", "拓扑探测与设备模型、airy-disk"),
    ("M2", "安装与命名", "安装器选盘、UKUI 闭包、命名规范"),
    ("R1L", "桌面适配", "UKUI 追新全链"),
    ("R1X", "桌面使用与内容", "日常使用路径强化、内置壁纸收敛与品牌默认集"),
    ("I1", "固件与显示", "固件闭包门禁、cmdline、显示策略"),
    ("I2", "引导与背光", "活动副本同步、固件随内核、背光入口"),
    ("I3", "硬化与取证", "Xorg 判据、W^X 白名单、RTC 取证"),
    ("K1", "模型环境", "运行环境预置、资产通道"),
    ("K2", "服务与降级", "加速降级、离线自检、磁盘服务"),
    ("X1", "RT 服务面", "RT 带宽、注入通道驱动与探针"),
    ("X2", "RT 验收面", "能力矩阵、实时性验收、共存策略"),
    ("V1", "实机验证", "取证矩阵、判负集、会话闭环"),
    ("V2", "发布与升级", "发布自证、升级通道"),
]

# ---------------------------------------------------------------- 工作包
# 字段：id, mod, name, loc, lane, deps, art, debt
#   art  ：该 WP 的主要产出物形态（任务卡的「产出物」列以它为主干）
#   debt ：承接的遗留债/缺陷编号（可空）

WPS = [
    # ---------------- L 流水线与交付链 ----------------
    dict(id="L-40", mod="L", lane="L1", loc=5700, deps=[],
         name="内联 run 块归零与门禁下沉", art="ci/gates/*.sh、ci/ci.sh 分发行、ci/workflow-budgets.txt",
         debt=["CI-05"]),
    dict(id="L-41", mod="L", lane="L1", loc=2100, deps=[],
         name="workflow 供应链固定与治理规则", art=".github/workflows/*.yml、ci/check-workflows.py",
         debt=["CI-13", "CI-14", "CI-15", "CI-09", "CI-10", "CI-12", "DOC-01", "DOC-02"]),
    dict(id="L-42", mod="L", lane="L2", loc=1350, deps=["L-40"],
         name="构建预算台账与漂移告警", art="ci/gates/build-manifest.sh、build-manifest.txt 模式",
         debt=["CI-03", "CI-08"]),
    dict(id="L-43", mod="L", lane="L2", loc=3300, deps=["L-42"],
         name="内容寻址候选池 L1-a/L1-b", art="distro/scripts/lib/payload_cache.sh、ci/gates/payload-pool.sh",
         debt=["CI-11", "CI-04"]),
    dict(id="L-44", mod="L", lane="L2", loc=2700, deps=["L-43"],
         name="内容寻址层 L2 与定时预热", art="ci/gates/payload-publish.sh、.github/workflows/payload-seed.yml",
         debt=["CI-11", "CI-16"]),
    # L3 泳道内按本列表顺序串行；L-46/L-51 无（或仅依赖 L-46）前置，放在 L-45 之前
    # 才能填在 L-45 等待 L-42 的空窗里，否则 L3 尾部后移会把施工日从 87 撑到 92。
    dict(id="L-46", mod="L", lane="L3", loc=600, deps=[],
         name="构建器清理与语义改名", art="distro/scripts/build-rpms.sh、tools/rpmbuild-runner",
         debt=["CI-01"]),
    dict(id="L-51", mod="L", lane="L3", loc=900, deps=["L-46"],
         name="安装介质品牌面收口与 openEuler 字样白名单",
         art="distro/release/brand/（splash.png/splash.lss/anaconda 产品名）、ci/gates/brand-whitelist.sh",
         debt=["BR-01"]),
    dict(id="L-45", mod="L", lane="L3", loc=2550, deps=["L-42"],
         name="发布同源与资产对账", art="ci/gates/release-*.sh、release.yml、tools/release-notes",
         debt=["TD-08", "TD-09", "CI-02", "REL-02", "REL-03", "D-29", "CI-07"]),
    dict(id="L-47", mod="L", lane="L1", loc=750, deps=[],
         name="稀疏 checkout 与静态门禁分段计时", art=".github/workflows/*.yml、ci/lib/timing.sh",
         debt=[]),
    dict(id="L-48", mod="L", lane="L3", loc=1200, deps=["L-45"],
         name="构建来源证明与制品证明", art="ci/gates/attest.sh、release.yml 证明步骤",
         debt=["CI-17"]),
    dict(id="L-49", mod="L", lane="L1", loc=450, deps=[],
         name="本地开发环境引导", art="tools/venv-bootstrap.sh、README 开发段",
         debt=["DEV-01"]),
    dict(id="L-50", mod="L", lane="L3", loc=1500, deps=[],
         name="基底耦合点清点成册", art="10-references/baseline-coupling.md、ci/gates/coupling-scan.sh",
         debt=["B-02"]),

    # ---------------- T 烧录系统 ----------------
    dict(id="T-01", mod="T", lane="T1", loc=1200, deps=[],
         name="取件子命令与判定字段统一", art="tools/airy-flash/src/airy_flash/*.py、tools/airy-flash/tests/",
         debt=["FL-01", "FL-02"]),
    dict(id="T-02", mod="T", lane="T1", loc=2400, deps=["T-01"],
         name="引导盘（≤1 GB）分层交付", art="distro/tools/mk-boot-media.py、distro/kickstart/*.ks",
         debt=["FL-04"]),
    dict(id="T-03", mod="T", lane="T2", loc=2700, deps=["T-02"],
         name="install- 载荷通道与 digest 钉住", art="ci/gates/payload-install.sh、distro/scripts/lib/payload_fetch.sh",
         debt=["FL-04"]),
    dict(id="T-04", mod="T", lane="T2", loc=1500, deps=["T-03"],
         name="烧录回归与回读取证", art="tools/airy-flash/tests/、ci/gates/flash-verify.sh",
         debt=["FL-02", "FL-03"]),

    # ---------------- M 发行版工程与磁盘管理 ----------------
    dict(id="M-30", mod="M", lane="M1", loc=1800, deps=[],
         name="磁盘拓扑探测与设备模型", art="system/services/airydisk/ 探测层、tests/",
         debt=[]),
    dict(id="M-31", mod="M", lane="M1", loc=2100, deps=["M-30"],
         name="磁盘操作面与安全护栏", art="system/services/airydisk/ 操作层、system/bin/airy-disk",
         debt=[]),
    dict(id="M-36", mod="M", lane="M1", loc=1200, deps=["M-31", "M-32"],
         name="系统盘与数据盘双分区布局（参考 Windows，通用化）",
         art="distro/kickstart/ 分区段、/etc/fstab、system/bin/airy-disk layout、ci/gates/disk-layout.sh",
         debt=["DISK-01"]),
    dict(id="M-32", mod="M", lane="M2", loc=1650, deps=["M-30"],
         name="安装器选盘通用化", art="distro/kickstart/*.ks、%pre 逻辑、tests/ks-lint",
         debt=["D-33", "D-30"]),
    dict(id="M-33", mod="M", lane="M2", loc=1200, deps=[],
         name="UKUI 追新的发行版侧闭包", art="distro/comps/*.xml、distro/lockfile/*.yaml、spec 闭包",
         debt=["UK-01"]),
    dict(id="M-34", mod="M", lane="M2", loc=600, deps=[],
         name="命名规范与默认用户收口", art="distro/release/os-release.in、distro/kickstart/*.ks",
         debt=[]),
    dict(id="M-35", mod="M", lane="M2", loc=900, deps=[],
         name="openEuler 基底按大 SP 规则选型（当前 SP2 → 目标为 EOL 最晚的大 SP）",
         art="distro/repo/airymax-os.repo、%oe_base、distro/lockfile/*.yaml、distro/comps/*.xml、"
             "10-references/openeuler-sp-eol.md、ci/gates/base-eol.sh",
         debt=["OE-01"]),

    # ---------------- R1 UKUI 追新与桌面适配 ----------------
    dict(id="R1-10", mod="R1", lane="R1L", loc=900, deps=[],
         name="UKUI 版本线取证与可行性差异清单（含 4.24 自建闭包）",
         art="distro/lockfile/ukui-*.yaml、10-references/ukui-delta.md、"
             "10-references/ukui-424-feasibility.md",
         debt=["UK-01", "UK-02"]),
    dict(id="R1-11", mod="R1", lane="R1L", loc=2100, deps=["R1-10", "M-33"],
         name="适配层增量与 23 进程基线", art="desktop/r1-adapter/*.patch、distro/ci/session-baseline.txt",
         debt=["UK-01"]),
    dict(id="R1-12", mod="R1", lane="R1L", loc=1200, deps=["R1-11"],
         name="锁屏三条根因修复", art="distro/kickstart/%post 片段、desktop/dconf/*、ci/gates/session-closure.sh",
         debt=["HW-04"]),
    dict(id="R1-13", mod="R1", lane="R1L", loc=600, deps=["R1-10"],
         name="桌面显式依赖补齐", art="distro/comps/*.xml、distro/release/spec-deps",
         debt=["HW-07"]),
    dict(id="R1-14", mod="R1", lane="R1X", loc=1200, deps=["R1-11"],
         name="UKUI 日常使用强化", art="desktop/dconf/*、desktop/r1-adapter/ 会话与输入配置、system/bin/airy-desktop",
         debt=[]),
    dict(id="R1-15", mod="R1", lane="R1X", loc=600, deps=["R1-10", "M-33"],
         name="内置壁纸收敛为三张品牌默认集", art="distro/release/wallpapers/、distro/lockfile/ukui-wallpapers.yaml、"
              "desktop/dconf/ 默认背景、ci/gates/wallpaper-set.sh",
         debt=[]),

    # ---------------- I 硬件使能与固件闭包 ----------------
    dict(id="I-20", mod="I", lane="I1", loc=1800, deps=[],
         name="固件闭包构建期门禁", art="ci/gates/fw-closure.sh、fw-manifest.txt 模式",
         debt=["FW-01", "FW-02", "FW-03", "D-01", "D-02", "D-03", "D-04"]),
    dict(id="I-21", mod="I", lane="I1", loc=750, deps=[],
         name="cmdline 清理与 console 收敛", art="distro/tools/cfg_brand.py、distro/kickstart/*.ks",
         debt=["HW-05"]),
    dict(id="I-22", mod="I", lane="I1", loc=1800, deps=["I-21"],
         name="显示策略通用化", art="distro/tools/display-policy.py、ci/gates/display-policy-test.py",
         debt=["G-01", "G-02", "G-03"]),
    dict(id="I-23", mod="I", lane="I2", loc=600, deps=["I-21"],
         name="活动引导副本同步", art="distro/tools/grub-sync.sh、ci/gates/boot-copy.sh",
         debt=["D-07"]),
    dict(id="I-24", mod="I", lane="I2", loc=1050, deps=["I-20"],
         name="固件随内核走与运行期探针", art="distro/release/*.spec、system/bin/airy-observe firmware",
         debt=["FW-01", "FW-03", "D-01", "D-02", "D-03", "D-04"]),
    dict(id="I-25", mod="I", lane="I2", loc=900, deps=["I-22"],
         name="背光与键盘背光用户态入口", art="system/services/airybright/、system/bin/airy-bright",
         debt=["HW-03"]),
    dict(id="I-26", mod="I", lane="I3", loc=1050, deps=["I-22"],
         name="Xorg 判据升级与不适用策略", art="distro/ci/xserver.sh、ci/gates/desktop-capability.sh",
         debt=["HW-06"]),
    dict(id="I-27", mod="I", lane="I3", loc=1500, deps=[],
         name="W^X 受控白名单与回归器", art="ci/tools/execstack_regress.py、ci/gates/wx-policy.sh",
         debt=["D-31"]),
    dict(id="I-28", mod="I", lane="I3", loc=600, deps=[],
         name="RTC 长停取证与告警", art="ci/gates/rtc-probe.sh、system/bin/airy-observe rtc",
         debt=["D-34"]),
    dict(id="I-29", mod="I", lane="I3", loc=1050, deps=["I-20"],
         name="网络子系统使能与烧录后联机验收", art="ci/gates/net-online.sh、NetworkManager 默认配置、system/bin/airy-observe net",
         debt=[]),

    # ---------------- K 系统服务：磁盘服务与大模型环境 ----------------
    dict(id="K-20", mod="K", lane="K1", loc=2400, deps=[],
         name="大模型运行环境预置", art="system/services/airyllm/、distro/comps/airyllm.xml",
         debt=[]),
    dict(id="K-21", mod="K", lane="K1", loc=1500, deps=["K-20"],
         name="模型资产获取与校验通道", art="system/bin/airy-model、ci/gates/model-manifest.sh",
         debt=[]),
    dict(id="K-22", mod="K", lane="K2", loc=1200, deps=["K-20"],
         name="加速后端探测与降级", art="system/services/airyllm/accel/、probe 输出契约",
         debt=[]),
    dict(id="K-23", mod="K", lane="K2", loc=900, deps=["K-21", "K-22"],
         name="离线可用性与首启自检", art="system/services/airyllm/selftest、ci/gates/llm-offline.sh",
         debt=[]),
    dict(id="K-24", mod="K", lane="K2", loc=1500, deps=["M-30"],
         name="磁盘服务：挂载/扩容/健康", art="system/services/airydisk/ 服务层、systemd units",
         debt=[]),

    # ---------------- X AirymaxRT 全方位适配 ----------------
    dict(id="X-01", mod="X", lane="X1", loc=900, deps=[],
         name="RT 带宽根因与默认值", art="system/services/airymax-rt/、cgroup 配置生成",
         debt=["RT-01"]),
    dict(id="X-02", mod="X", lane="X1", loc=1800, deps=["X-01"],
         name="注入通道驱动与 airy-probe", art="system/bin/airy-probe、tests/probe-regress",
         debt=["KRN-01"]),
    dict(id="X-03", mod="X", lane="X2", loc=1050, deps=["X-01"],
         name="实时能力探测与适用性矩阵", art="system/bin/airy-rt-cap、10-references/rt-matrix.md",
         debt=["RT-01"]),
    dict(id="X-04", mod="X", lane="X2", loc=1200, deps=["X-03"],
         name="实时性验收套件与基线", art="ci/gates/rt-accept.sh、tests/rt/",
         debt=[]),
    dict(id="X-05", mod="X", lane="X2", loc=900, deps=["X-04"],
         name="桌面与 RT 共存策略", art="system/services/airymax-rt/policy/、systemd slice",
         debt=[]),

    # ---------------- V 验证与验收 ----------------
    dict(id="V-10", mod="V", lane="V1", loc=1200, deps=[],
         name="实机取证矩阵与按能力选机", art="ci/gates/hw-matrix.sh、10-references/hw-matrix.md",
         debt=["HW-01", "HW-02"]),
    dict(id="V-11", mod="V", lane="V1", loc=900, deps=[],
         name="装机腿判负集分层", art="ci/gates/accept-judge.sh、scriptlet-warn.txt 模式",
         debt=[]),
    dict(id="V-12", mod="V", lane="V1", loc=1350, deps=["R1-12"],
         name="会话闭环门禁八步", art="ci/gates/session-closure.sh、负例自测",
         debt=["HW-04"]),
    dict(id="V-13", mod="V", lane="V2", loc=750, deps=["L-45"],
         name="发布自证：ISO 与内核 NEVRA 对照", art="ci/gates/release-verify.sh、acceptance 报告模板",
         debt=["CI-02"]),
    dict(id="V-14", mod="V", lane="V2", loc=1200, deps=["L-45"],
         name="升级通道", art="system/bin/airy-update、channel.json、systemd timer",
         debt=["UP-01"]),
    dict(id="V-15", mod="V", lane="V2", loc=900, deps=["V-13", "V-14"],
         name="系统完整性盘点与 0.0.5 缺口登记", art="ci/gates/system-inventory.sh、ci/gates/alk-size.sh、10-references/completeness-audit.md、system/bin/airy-observe system",
         debt=["ALK-01"]),
    dict(id="V-16", mod="V", lane="V1", loc=600, deps=["V-10"],
         name="模块签名与 taint 归零实机复核", art="ci/gates/module-signature.sh、10-references/module-signature.md",
         debt=["KM-01"]),
]

# ---------------------------------------------------------------- 范围裁定附加数据
# 显式替换/降级边：consumer 依赖 bypass 的事项，本版以 repl 替代。
EDGE_REG = [
    dict(consumer="T-03", bypass="CI-11-L2", repl="复用 build- 前缀的内容寻址层做字节来源，"
                                                  "以 install- 前缀另立装机期通道；不共享 tag"),
    dict(consumer="R1-11", bypass="R2", repl="只做 R1 适配层增量，不进入 R2 主体开发；"
                                             "上游改动以 patch 落 adapter，不改 UKUI 主线"),
    dict(consumer="I-22", bypass="HW-01", repl="内核无 285H GPU alias，显示策略以 EDID/KMS/固件候选串"
                                              "求交收敛；无 KMS 时记 single-mode 并报「不适用」"),
    dict(consumer="K-20", bypass="KRN-GPU", repl="加速后端按运行期探测结果启用，探测不到即 CPU 路径；"
                                                 "不以「装驱动」为前提"),
    dict(consumer="X-02", bypass="A-23", repl="注入通道仅经既有 /proc/sys/agentrt 与 "
                                              "/sys/kernel/security/airy/policy 路径触发与回读；"
                                              "不新增 syscall 号段，不改主图纸 A 模块契约"),
    dict(consumer="I-27", bypass="airy LSM 内核侧白名单改动",
         repl="实测 /sys/kernel/security/airy/policy 为 0400 只读、只输出统计表，"
              "airy 未注册 file_mprotect 钩子，DSL 也无可执行栈字段——接口不受理"
              "规则提交，按任务卡登记顺延（§2.3）；本版交付例外清单与绕过禁令门禁"),
]

# 能力裁撤登记：本版不做，逐项登记理由与承接版本。
CUT_REASON = [
    dict(item="AirymaxOS TUI 全面建设", ver="0.0.5", why="用户明确本版不做；TUI 依赖的服务面在 0.0.4 才成形。"
                                                                  "0.0.5 承担 TUI 全面建设，并在该版内基本实现 "
                                                                  "docs-linux 的全部功能面（最小可用闭环口径）"),
    dict(item="`docs-linux` 桌面会话（UKUI）方案缺口", ver="0.0.5（V-15 登记）",
         why="实测 `docs-linux` 对桌面会话覆盖薄弱（仅 190-distribution/03-installer-design.md 提及 UKUI），"
             "无独立桌面方案文档；本版不伪造方案，R1 以 installer 与 20-modules/07-system.md 为锚点，"
             "缺口本身进 V-15 盘点册，作为 0.0.5 补文档与 TUI 选题输入"),
    dict(item="内核基线抬升 / HWE 双内核 / 内核补丁回移", ver="顺延", why="输入清单 §4.4 已决策 0.0.4 不动内核；"
                                                                   "凡需新增或回移内核补丁、修改内核配置者一律不开工"),
    dict(item="内核侧注入通道（/dev/airy 字符设备或新 sysfs 注入节点）", ver="顺延",
         why="同上；agent IPC 帧注入在既有通道无承载面，X-02 只以既有 /proc 与 "
             "policy 通道触发与回读，注入动作不受理即如实降级并留证"),
    dict(item="285H GPU（8086:7d51）原生 KMS 驱动", ver="0.0.4（ID 入表，默认不绑定）",
         why="属上一条；本版只做交付面收敛与通用显示策略。2026-11-10 曾改判为「去掉 "
             "mtl_info 的 require_force_probe、默认绑定」，285H 实测该内核重启后不再回来"
             "（无网络、无 ARP 应答，只能断电恢复），失败启动日志尚未捕获，显示初始化"
             "路径是首要嫌疑而非确诊；内核侧据此回退为保留门控（`af06521d24a0`），ID 表"
             "（`4eea4aa6141a`）保留：`INTEL_MTL_IDS` 展开 10 个 ID，`0x7D51` 唯一映射到 "
             "`mtl_info`，`mtl_info` 带 require_force_probe。故本版默认仍回落 simpledrm，"
             "与 0.0.4-7 行为一致；KMS、背光与硬件加速随内核基线抬升顺延 0.0.5。"
             "`i915.force_probe=7d51` 只作实验入口，不进默认 cmdline"),
    dict(item="触控板（`intel-lpss` 补 ARL-H PCI ID）", ver="0.0.4（本版追加）",
         why="原列「顺延」。实机复验后改为本版交付：根因是 `intel_lpss_pci_ids[]` 缺 "
             "`8086:7750/7751/7778/777a/777b`，与内核配置无关——`MFD_INTEL_LPSS_PCI=y` 与 "
             "`I2C_DESIGNWARE_PLATFORM=m` 基线已给，而 `i2_designware_pci_ids[]` 里没有任何 "
             "`0x77xx` 条目，打开 `CONFIG_I2C_DESIGNWARE_PCI` 认领不到这些功能。补丁 "
             "`c93c57a28bc2` 只加 ID 表。判据可数：`lspci -k` 五个 LPSS 功能出现驱动绑定、"
             "`/sys/bus/i2c/devices` 出现 designware 适配器、`/proc/bus/input/devices` "
             "出现触控板条目，不以「能用」作结论"),
    dict(item="D-06 Battlemage（8086:e212）i915/xe 绑定", ver="顺延", why="需新增内核驱动补丁；本版只登记进能力矩阵并报「不适用」"),
    dict(item="D-08 CONFIG_SYSFB_SIMPLEFB / CONFIG_DRM_SIMPLEDRM", ver="顺延", why="属内核配置变更；本版以固件候选串与 EDID 求交收敛显示"),
    dict(item="W^X 可执行栈白名单（I-27 的内核侧受理面）", ver="0.0.5（需内核改动）",
         why="受理面要求三项内核能力：airy 注册 file_mprotect 钩子、DSL 增加可执行栈"
             "例外字段、policy 接口可写并受理规则提交；三者都在 kernel/ 下，与本版"
             "「内核侧净新增 0 行」冲突。本版交付回归器与例外清单，装机后能定量回答"
             "「哪些库会撞墙」，并禁止交付链用清位或重编可执行栈绕过"),
    dict(item="自有基底替换（B-02 的施工部分）", ver="0.1.x", why="本版只清点耦合点成册（L-50），不做替换实现"),
    dict(item="ostree / 分层 rootfs 产物层（L3）", ver="0.1.x", why="0.0.x 无自有基底，产物层无承载面"),
    dict(item="自建常驻 runner", ver="待评估", why="仅在 L1/L2 收口后 T-PAY-7 仍不达标时重开评估"),
    dict(item="delta 层（每版一层的差量包）", ver="不做", why="求解差值后直接补池与 delta 等价，复杂度高一个数量级"),
    dict(item="整站镜像上游仓库", ver="不做", why="月流量数十 GB，且使上游变更不可见"),
    dict(item="accept 三腿并行", ver="不做", why="只省约 8 分钟，代价是两份 QEMU + 抢核 + 归因退化"),
]

# 存量抵扣：0.0.3 已交付、0.0.4 直接复用不重复排程的资产。
ASSETS = [
    ("ISO OCI 分块发布（TD-09）", "`0cf46c5` + `cdeae33` 已落 `image-build.yml`", "L-45 只做回读与清单断言，不重建通道"),
    ("发行/组装静态门禁前置（CI-06）", "`c905667` 已加 `ci/ci.sh distro-lint`", "不排程"),
    ("notes 概述形态（REL-01）", "`11b7cc6` 已改 `render_notes()` 与用例", "不排程"),
    ("repo 段集与镜像（D-05）", "`8ee1805` 已收口，2026-11-01 285H 实机取证通过", "不排程，不再重复取证"),
    ("LADDER 四档（D-32）", "`5da2152` / `0aad525`", "并入 I-22 的回归集"),
    ("installer 动态选盘（D-33）", "`da0348a` 已用 `%pre` 选盘", "M-32 只做通用化扩展与多盘场景"),
    ("会话探针身份项（D-35）", "2026-11-01 285H 活体 26 行、`airy-demo status=ok`", "并入 V-12 的断言清单"),
    ("dnf 容器缓存（L0）", "`c335647`", "L-43 在其上做 L1，不重做 L0"),
    ("xserver 判据初版（HW-06 部分）", "`c786fca` / `3ce4bf0`", "I-26 升级为「KMS 有可枚举模式且 EDID 非空」"),
]

# ---------------------------------------------------------------- WP 推进状态
#
# 全版 56 个 WP 的推进状态与证据锚，只有两类：
#   已验收        产物与验收证据在位，锚指向本图纸内可复算的位置或门禁脚本；
#   顺延（§2.3）  图纸 §2.3 已授权顺延，锚写明承接版本与不做的边界。
# 任务卡的状态由本表逐 WP 派生，不在 §6 逐卡手写：同一事实只留一个事实源，
# 改状态改这里，重跑 bp_004_gen.py --apply-status 回填 §5/§6。
WP_STATE = {
    # L 流水线与交付链
    "L-40": ("已验收", "QG-06 内联块 0（`ci/check-workflows.py`）；build 21 装配 run 43792763141"),
    "L-41": ("已验收", "`uses:` 全钉 40 位 SHA；治理规则与 `check-workflows.py` 逐条对应"),
    "L-42": ("已验收", "`build-manifest.txt` 记四架构时刻与耗时；QG-08 预算可复算"),
    "L-43": ("已验收", "QG-09 候选池 x86_64/arm64 命中（build 21 装配）"),
    "L-44": ("已验收", "预热作业定时绿跑；产物按 digest 拉取（`image-build` 预热）"),
    "L-46": ("已验收", "构建器语义改名后调用点全部更新；`ci/ci.sh` 全绿"),
    "L-51": ("已验收", "BR-01：ISO 解包 openEuler 字样白名单外命中 0（§14.4 第 3 项）"),
    "L-45": ("已验收", "§14.4 第 3/4 项：59 件资产 have==want；tag 树即产出树"),
    "L-47": ("已验收", "`ci/lib/timing.sh` 分段计时（280585e）；稀疏 checkout 经核不采用（§17）"),
    "L-48": ("已验收", "来源证明可查：§14.4 第 1 项 attestation 回读"),
    "L-49": ("已验收", "新环境一条命令拉起（`dev-up`），`ci/ci.sh` 绿"),
    "L-50": ("已验收", "`coupling-scan.sh` 60 declared / 60 found / delta 0；`baseline-coupling.md` §10"),
    # T 烧录系统
    "T-01": ("已验收", "`airy-flash` 子命令与 `--json` 齐备；`tools/airy-flash/tests` 99 项全绿"),
    "T-02": ("顺延（§2.3）", "承接 0.1.x；本版只交整包引导盘，不做 ≤1 GB 分层"),
    "T-03": ("顺延（§2.3）", "承接 0.1.x；install- 载荷通道与 digest 钉住不在本版"),
    "T-04": ("已验收", "§14.4 第 6 项：plan/write/verify 全量回读 3 474 849 792 字节一致"),
    # M 发行版工程与磁盘管理
    "M-30": ("已验收", "§14.7 `airy-disk status` 三拓扑；设备类别过滤（rom/RM/TRAN）"),
    "M-31": ("已验收", "§14.7 `layout` 与 `health` rc=0；破坏性操作二次确认"),
    "M-32": ("已验收", "§14.7 `%pre` 选盘与 `lsblk` 逐字段一致（verdict=match）"),
    "M-36": ("已验收", "§14.4 第 8 项：`/`=nvme0n1p3、`/data`=nvme0n1p5 独立 ext4"),
    "M-33": ("已验收", "`ukui-delta.md` 仓库实测 NVRA；`ukui-424-feasibility.md` 成册"),
    "M-34": ("已验收", "`os-release` NAME/PRETTY_NAME 品牌化；默认用户与组在 %pre 建"),
    "M-35": ("已验收", "§14.10 ⑧：五段 baseurl 为 SP3；`base-eol.sh` 断言 EOL 晚于收口日"),
    # R1 UKUI 追新与桌面适配
    "R1-10": ("已验收", "`ukui-delta.md` 逐组件 NVRA 与 lockfile 逐字一致"),
    "R1-11": ("已验收", "`ci/session-baseline.txt` 21 组件 / 23 进程；`run-smoke.sh` T1 逐项常在"),
    "R1-12": ("已验收", "§14.4 第 10 项：会话冒烟 30/30，锁屏三条根因关闭"),
    "R1-13": ("已验收", "comps 可解析；`dnf repoquery` 依赖闭包无缺项"),
    "R1-14": ("已验收", "§14.10 ⑨：磁盘/网络/模型三项状态桌面可见（build 22 重装复验）"),
    "R1-15": ("已验收", "`wallpaper-set.sh` 三张壁纸 digest 与清单逐字一致"),
    # I 硬件使能与固件闭包
    "I-20": ("已验收", "`fw-manifest.txt` 与 comps 一一对应；缺项构建期即红"),
    "I-21": ("已验收", "§14.5：`cgroup_disable=files` 入 stale；`test_grub_args.py` 49 项"),
    "I-22": ("已验收", "§14.6 显示按能力求交，无硬编码机型分支"),
    "I-23": ("已验收", "§14.5：`grub_args.sh` 的 sync_brand/sync_env/sync_font 三收敛点"),
    "I-24": ("已验收", "运行期探针读固件版本与加载状态（`fw-probe`）"),
    "I-25": ("已验收", "§14.6 背光 `n/a no-screen-backlight` 如实降级；`test_hw_matrix.sh` 绿（fa7acb2）"),
    "I-26": ("已验收", "§14.6 Xorg 判据：KMS 模式可枚举且 EDID 非空，285H 判 no-kms"),
    "I-27": ("已验收", "回归器与例外清单成册；内核侧受理面按 §2.3 顺延 0.0.5"),
    "I-28": ("已验收", "RTC 长停偏差阈值告警；超阈用例覆盖"),
    "I-29": ("已验收", "§14.9 `net-online.sh --live` 联机成立（src=dhcp）；机内 T31 补 src 判据"),
    # K 系统服务
    "K-20": ("已验收", "§14.8.1 断网 `airy-model selftest` 八段全 ok"),
    "K-21": ("已验收", "资产通道门禁纳入账户与权限声明（3c33da2）"),
    "K-22": ("已验收", "§14.8.1 `state=degraded backend=cpu reason=no-accel`（rc=10 既定码）"),
    "K-23": ("已验收", "§14.8.1 断网推理实跑 `/v1/completions` 正常"),
    "K-24": ("已验收", "§14.7 `health=ok`；`/data` 可独立扩容"),
    # X AirymaxRT
    "X-01": ("已验收", "§14.9 `cpu.rt_runtime_us` 读出 `runtime=950000` 非 0"),
    "X-02": ("已验收", "§14.9 root 下 `airy-probe status --json` readable=10/10"),
    "X-03": ("已验收", "§14.9 `airy-rt-cap matrix --json` grade=soft、budget=yes"),
    "X-04": ("已验收", "§14.9 基线 358 us、判负线 430 us；`baseline.py record` 重放 rc=0"),
    "X-05": ("已验收", "桌面与 RT 按 slice 限额共存，降级显式并留证"),
    # V 验证与验收
    "V-10": ("已验收", "§14.6 五类矩阵 pass=3 na=1 fail=1，无静默跳过（QG-10）"),
    "V-11": ("已验收", "`run-smoke.sh` TAP 1..31 判负集分层，逐项可复算"),
    "V-12": ("已验收", "`session-closure.sh` 八步；§14.4 第 10 项冒烟 30/30"),
    "V-13": ("已验收", "§14.4 第 2 项：ISO 内核 NEVRA 0.0.4-13 与页面资产同源"),
    "V-14": ("已验收", "升级通道可下载/校验/回滚；装机 `dnf makecache` 四段成功"),
    "V-15": ("已验收", "§14.10 ⑩：`systemctl --failed` 0、包闭包差 0；缺口登记成册"),
    "V-16": ("已验收", "§14.4 第 9 项：tainted=0；全量 `.ko` 带 `.module_sig`"),
}
