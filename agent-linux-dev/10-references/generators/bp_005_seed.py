#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0
# Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
"""AirymaxOS 0.0.5 施工图纸种子（人工只改本文件）。

约定与 bp_004_seed.py 一致：本种子只声明「做什么、多大、先后」，
任务卡由 bp_005_gen.py 按 50 行/任务切分（硬上限 300 行/任务），
再按泳道产能（150 行/泳道/施工日 = 3 个任务）拓扑排程。

与 0.0.4 的差别只有一条：0.0.5 的交付面是**用户态会话层 + 两条内核面**，
因此 WP 的产出物列全部落在 `tui/`（新增 Rust 工作区）、`system/`、`distro/`、
`ci/` 与 `kernel/` 五个根，且每个 WP 必须带 docs-linux 锚点（MODULE_DOCREF）。
"""

# ---------------------------------------------------------------- 模块
# id, 名称, 承接的用户任务, 说明
MODULES = [
    ("U", "TUI 内核与渲染", "①", "终端渲染循环、布局、对话框、命令面板、状态面、降级、持久化、帧预算"),
    ("N", "输入抽象与 IME", "①②", "RawEvent 抽象、键盘规范化、AIRYIME1 独立 IME、语音 ASR、结构化 API、批处理"),
    ("A", "会话执行面与 Intent", "①③", "intent 校验、airy-tui-exec、审批与沙箱、会话状态机、trace、超时取消"),
    ("S", "服务面消费与 CLI 契约", "①", "四个已冻结 --json 契约的消费侧适配、网络状态面、docs-linux 19 模块映射"),
    ("K", "内核侧两条（抬基线）", "④", "KRN-01 注入通道与计数、I-27 W^X 受理面、ABI 快照回归"),
    ("R", "Rust 供应链与构建", "⑤", "工具链钉版、vendor 离线源、crate 工作区与 CI、供应链证明"),
    ("Q", "文档面盘点与契约", "⑥", "三态登记册、契约册、文档↔代码一致性门禁"),
    ("V", "验证与取证", "全部", "四通道矩阵、TUI 端到端、中文语料、实机与降级、M1/M2 自证、无桩扫描"),
]

MODULE_ORDER = ["U", "N", "A", "S", "K", "R", "Q", "V"]

# 模块 ↔ docs-linux 方案锚点（路径相对 docs/ 目录）。
# 锚点为空或文件不存在则该模块不得开工（引擎在 check() 里判，判负退出码 3）。
MODULE_DOCREF = {
    "U": ["docs-linux/30-interfaces/11-input-ingress.md",
          "docs-linux/20-modules/06-agent.md"],
    "N": ["docs-linux/30-interfaces/11-input-ingress.md",
          "docs-linux/140-application-development/06-agent-deployment.md"],
    "A": ["docs-linux/40-dataflows/04-scheduling-flow.md",
          "docs-linux/20-modules/06-agent.md"],
    "S": ["docs-linux/100-operations/03-monitoring.md",
          "docs-linux/20-modules/07-system.md"],
    "K": ["docs-linux/10-architecture/08-threat-model.md",
          "docs-linux/40-dataflows/04-scheduling-flow.md"],
    "R": ["docs-linux/70-build-system/03-ci-cd-pipeline.md",
          "docs-linux/190-distribution/06-sbom-generation.md"],
    "Q": ["docs-linux/00-requirements/03-non-functional-requirements.md"],
    "V": ["docs-linux/80-testing/03-kernel-selftests.md",
          "docs-linux/100-operations/03-monitoring.md"],
}

# ---------------------------------------------------------------- 泳道
# id, 名称, 说明
LANES = [
    ("U1", "渲染内核", "事件循环、绘制、布局、帧预算"),
    ("U2", "视图与面板", "对话框、会话视图、命令面板"),
    ("U3", "状态面与降级", "状态/轨迹视图、无 GPU 与无 tty 降级、持久化恢复"),
    ("N1", "输入抽象", "RawEvent、InputSource、键盘与终端规范化"),
    ("N2", "中文 IME", "AIRYIME1 词典、boot-ime 进程、候选排序"),
    ("N3", "语音与外部通道", "ASR 网关、Unix socket 结构化输入、批处理回放"),
    ("A1", "Intent 与会话", "intent schema 校验、会话状态机、超时取消"),
    ("A2", "执行与审计", "airy-tui-exec、审批与沙箱、trace 审计"),
    ("S1", "磁盘与模型", "airy-disk、airy-model status 的消费适配"),
    ("S2", "探针与网络", "airy-probe/airy-rt-cap、网络三级状态、19 模块映射"),
    ("K1", "内核两条", "注入通道、W^X 受理面、ABI 快照"),
    ("R1", "Rust 供应链", "工具链、vendor、工作区与 CI、来源证明"),
    ("Q1", "文档与契约", "三态登记册、契约册、一致性门禁"),
    ("V1", "矩阵与语料", "四通道矩阵、中文输入语料"),
    ("V2", "端到端与实机", "tty1 冷启动端到端、实机与降级取证"),
    ("V3", "自证与扫描", "M1/M2 发版自证、无桩与死代码扫描"),
]

# ---------------------------------------------------------------- 工作包
# 字段：id, mod, lane, loc, deps, name, art, debt
#   loc ：净新增行数，必须为 150 的整数倍（= 3 个 50 行任务 = 1 个泳道日）
#   art ：任务卡「产出物」列的主干；「(首片)」「(中片 i/N)」「(末片)」由生成器追加
WPS = [
    # ---------------- U TUI 内核与渲染 ----------------
    dict(id="U-01", mod="U", lane="U1", loc=2700, deps=[],
         name="boot-tui 骨架与渲染循环", art="tui/crates/boot-tui/src/{main,loop,screen}.rs、tui/Cargo.toml",
         debt=["TUI-01"]),
    dict(id="U-02", mod="U", lane="U1", loc=2400, deps=["U-01"],
         name="主题、布局与东亚宽度排版", art="tui/crates/boot-tui/src/{theme,layout,wcwidth}.rs、tui/themes/*.toml",
         debt=["TUI-02"]),
    dict(id="U-03", mod="U", lane="U2", loc=3000, deps=["U-01"],
         name="对话框与会话视图", art="tui/crates/boot-tui/src/{dialog,session,scrollback}.rs",
         debt=["TUI-03"]),
    dict(id="U-04", mod="U", lane="U2", loc=2100, deps=["U-03"],
         name="命令面板与键盘导航", art="tui/crates/boot-tui/src/{palette,nav,keymap}.rs",
         debt=[]),
    dict(id="U-06", mod="U", lane="U3", loc=1500, deps=["U-01"],
         name="降级路径：无 GPU、非 tty、极小终端", art="tui/crates/boot-tui/src/degrade.rs、tests/degrade/",
         debt=["TUI-05"]),
    dict(id="U-05", mod="U", lane="U3", loc=1800, deps=["U-01", "S-03"],
         name="状态面与 trace 轨迹视图", art="tui/crates/boot-tui/src/{status,trace_view}.rs",
         debt=["TUI-04"]),
    dict(id="U-07", mod="U", lane="U3", loc=1500, deps=["U-05"],
         name="会话持久化与崩溃恢复", art="tui/crates/boot-tui/src/{session_store,recover}.rs",
         debt=[]),
    dict(id="U-08", mod="U", lane="U1", loc=1500, deps=["U-03"],
         name="帧预算与渲染性能门禁", art="tui/crates/boot-tui/benches/frame.rs、ci/gates/tui-frame.sh",
         debt=["TUI-06"]),

    # ---------------- N 输入抽象与 IME ----------------
    dict(id="N-01", mod="N", lane="N1", loc=2400, deps=[],
         name="RawEvent 与 InputSource 抽象", art="tui/crates/boot-tui/src/input/{event,source,arbiter}.rs",
         debt=["IN-01"]),
    dict(id="N-02", mod="N", lane="N1", loc=1800, deps=["N-01"],
         name="键盘与终端输入规范化", art="tui/crates/boot-tui/src/input/{key,term,escape}.rs",
         debt=["IN-02"]),
    dict(id="N-03", mod="N", lane="N2", loc=3000, deps=["N-01"],
         name="AIRYIME1 词典与 boot-ime 进程", art="tui/crates/boot-ime/src/{dict,lookup,rank}.rs、tui/crates/boot-ime/src/ipc.rs、tui/crates/boot-ime/SPEC.md、tui/crates/boot-ime/src/bin/dict-build.rs",
         debt=["IME-01", "IME-02"]),
    dict(id="N-04", mod="N", lane="N3", loc=2400, deps=["N-01"],
         name="离线语音 ASR 网关", art="tui/crates/asr-gateway/src/{capture,asr,ipc}.rs",
         debt=["ASR-01"]),
    dict(id="N-05", mod="N", lane="N3", loc=1500, deps=["N-01"],
         name="外接结构化输入（Unix socket）", art="tui/crates/boot-tui/src/input/api.rs、docs/airy.intent/1.md",
         debt=["IN-03"]),
    dict(id="N-06", mod="N", lane="N3", loc=900, deps=["N-05"],
         name="批处理回放通道", art="tui/crates/boot-tui/src/input/batch.rs、tests/batch/",
         debt=["IN-04"]),

    # ---------------- A 会话执行面与 Intent ----------------
    dict(id="A-01", mod="A", lane="A1", loc=2100, deps=["N-01"],
         name="intent crate 与 airy.intent/1 校验", art="tui/crates/intent/src/{schema,trust,route}.rs",
         debt=["IT-01"]),
    dict(id="A-02", mod="A", lane="A2", loc=2400, deps=["A-01"],
         name="airy-tui-exec 与 CLI 结果归一", art="tui/crates/airy-tui-exec/src/{exec,normalize}.rs",
         debt=["EX-01"]),
    dict(id="A-03", mod="A", lane="A2", loc=1800, deps=["A-02"],
         name="审批与沙箱（polkit 单一路径）", art="tui/crates/airy-tui-exec/src/{approve,sandbox}.rs、tui/polkit/*.policy",
         debt=["EX-02"]),
    dict(id="A-04", mod="A", lane="A1", loc=1800, deps=["A-01"],
         name="会话状态机", art="tui/crates/intent/src/session.rs",
         debt=["IT-02"]),
    dict(id="A-05", mod="A", lane="A2", loc=1200, deps=["A-02"],
         name="trace_id 与审计记录", art="tui/crates/airy-tui-exec/src/audit.rs、docs/audit-record.md",
         debt=["EX-03"]),
    dict(id="A-06", mod="A", lane="A1", loc=1200, deps=["A-04"],
         name="超时、取消与失败路径", art="tui/crates/intent/src/{timeout,cancel}.rs、tests/failures/",
         debt=["IT-03"]),

    # ---------------- S 服务面消费与 CLI 契约 ----------------
    dict(id="S-01", mod="S", lane="S1", loc=1500, deps=["A-02"],
         name="airy-disk --json 消费适配", art="tui/crates/airy-adapters/src/disk.rs",
         debt=["AD-01"]),
    dict(id="S-02", mod="S", lane="S1", loc=1500, deps=["A-02"],
         name="airy-model status --json 消费适配", art="tui/crates/airy-adapters/src/model.rs",
         debt=["AD-02"]),
    dict(id="S-03", mod="S", lane="S2", loc=1800, deps=["A-02"],
         name="airy-probe / airy-rt-cap 消费适配", art="tui/crates/airy-adapters/src/{probe,rtcap}.rs",
         debt=["AD-03"]),
    dict(id="S-04", mod="S", lane="S2", loc=1500, deps=["S-03"],
         name="网络三级状态面与会话状态", art="tui/crates/airy-adapters/src/net.rs、tui/crates/boot-tui/src/net_view.rs",
         debt=["AD-04"]),
    dict(id="S-05", mod="S", lane="S2", loc=1200, deps=["S-04"],
         name="docs-linux 19 模块入口映射", art="tui/crates/airy-adapters/src/modmap.rs、tui/modmap.toml",
         debt=["AD-05"]),

    # ---------------- K 内核侧两条（抬基线） ----------------
    dict(id="K-01", mod="K", lane="K1", loc=1500, deps=[],
         name="KRN-01 注入通道与单调计数", art="kernel/fs/airy/inject.c、kernel/include/uapi/linux/airymax/inject.h",
         debt=["KRN-01"]),
    dict(id="K-02", mod="K", lane="K1", loc=1200, deps=["K-01"],
         name="I-27 W^X 受理面与策略表", art="kernel/security/airy/wx_policy.c、distro/policy/wx_policy.toml",
         debt=["I-27"]),
    dict(id="K-03", mod="K", lane="K1", loc=300, deps=["K-01", "K-02"],
         name="UAPI 快照与 ABI 回归", art="ci/gates/abi-snapshot.py、10-references/abi-snapshot/",
         debt=["KRN-02"]),

    # ---------------- R Rust 供应链与构建 ----------------
    dict(id="R-01", mod="R", lane="R1", loc=1500, deps=[],
         name="工具链钉版与容器清单", art="tui/rust-toolchain.toml、ci/container/build-packages.txt",
         debt=["RS-01"]),
    dict(id="R-02", mod="R", lane="R1", loc=1200, deps=["R-01"],
         name="vendor 离线源与三件套", art="tui/vendor/、tui/Cargo.lock、ci/gates/rust-vendor.sh",
         debt=["RS-02"]),
    dict(id="R-03", mod="R", lane="R1", loc=1200, deps=["R-02"],
         name="crate 工作区与 CI 接线", art="tui/Cargo.toml、.github/workflows/tui.yml、ci/gates/lang-lock.sh",
         debt=["RS-03"]),
    dict(id="R-04", mod="R", lane="R1", loc=600, deps=["R-03"],
         name="供应链证明与 SBOM", art="ci/gates/rust-sbom.sh、tui/deny.toml",
         debt=["RS-04"]),

    # ---------------- Q 文档面盘点与契约 ----------------
    dict(id="Q-01", mod="Q", lane="Q1", loc=1200, deps=[],
         name="三态登记册与 36 条缺口对账", art="10-references/completeness-audit.md、ci/gates/completeness.sh",
         debt=["DC-01"]),
    dict(id="Q-02", mod="Q", lane="Q1", loc=900, deps=["Q-01"],
         name="契约册：airy.intent/1 与四通道", art="docs/contracts/{intent,input,audit}.md",
         debt=["DC-02"]),
    dict(id="Q-03", mod="Q", lane="Q1", loc=900, deps=["Q-02"],
         name="文档↔代码一致性门禁", art="ci/gates/doc-contract.sh、ci/tests/test_doc_contract.sh",
         debt=["DC-03"]),

    # ---------------- V 验证与取证 ----------------
    dict(id="V-01", mod="V", lane="V1", loc=1800, deps=["A-06", "N-06"],
         name="四通道矩阵（成功 + 失败各一路）", art="tui/tests/matrix/、ci/gates/input-matrix.sh",
         debt=["VF-01"]),
    dict(id="V-02", mod="V", lane="V2", loc=2100, deps=["U-04", "U-06"],
         name="tty1 冷启动端到端", art="tui/tests/e2e/、ci/gates/tui-e2e.sh",
         debt=["VF-02"]),
    dict(id="V-03", mod="V", lane="V1", loc=1500, deps=["N-03"],
         name="中文输入语料与回归", art="tui/tests/corpus/、ci/gates/ime-corpus.sh",
         debt=["VF-03"]),
    dict(id="V-04", mod="V", lane="V1", loc=1500, deps=["U-06"],
         name="实机与降级取证", art="tui/tests/field/、10-references/tui-field-evidence.md",
         debt=["VF-04"]),
    dict(id="V-06", mod="V", lane="V3", loc=900, deps=["V-01"],
         name="无桩与死代码扫描", art="ci/gates/no-stub.sh、ci/gates/dead-code.sh",
         debt=["VF-06"]),
    dict(id="V-05", mod="V", lane="V3", loc=1200, deps=["V-01", "V-02", "V-04", "U-07"],
         name="M1/M2 发版自证", art="ci/gates/release-005.sh、10-references/0.0.5-release-evidence.md",
         debt=["VF-05"]),
]
