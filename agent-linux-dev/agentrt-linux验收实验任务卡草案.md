# AgentRT / AirymaxOS（agent-linux）验收实验任务卡草案

> **版本 v0.1（实验大纲与竣工验收规程补全）** ｜ 2026-10-10 ｜ 密级：内部机密（docs-closed）
>
> Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
>
> 本草案为《agentrt-linux开发路线和进度.md》（v3.4）的增补件，用于补全第 11 轮反向证伪复审确认的最高优先缺口：**施工图纸只有"仪器"（L-19 QEMU 农场 / J-08 E2E 编排 / J-09 Soak / J-15 渗透 / M-13 镜像 CI），无一张"实验执行"卡，真机 bring-up 链 0 命中**。并入主图纸前需经设计-评审-证伪流程。
>
> 格式 SSoT：`agentrt-linux开发路线和进度.md` §1/§2/§2.1/§3/§6/§9。
> 工程规范：`docs-linux/50-engineering-standards/`（OS-CHK-DOC-01~06、OS-STD-CODE-030、SPDX 双轨、语言路由）。
> 判据来源：`docs-linux/00-requirements/03-non-functional-requirements.md`（NFR 原值）、`docs-linux/130-roadmap/06-acceptance-criteria.md`（OS-ACC 110 项）。

---

## 1. 编制说明

### 1.1 缺口定性

主图纸 3,334 个原子任务中，J/M/O 泳道交付的是**仪器与工具链**（测试农场、E2E 编排器、Soak 框架、渗透套件、镜像 CI），但没有任何任务实际"按下运行键"并把运行证据归档、对账、判定。导致：

1. NFR-P-001~P-006、NFR-R-001、NFR-S-001 的量化门槛无运行态实测任务承接；
2. 真机 bring-up（UEFI/BIOS 冷启动、kickstart 装机、首启 bootstrap 后的桌面就绪）无实证链；
3. 竣工没有总验收门禁，链尾 TR2-10-03 之后无收口动作。

### 1.2 补全方案总览

新增**模块 V（验收与实证）**，第 20 个模块（字母 V 经 grep 证实未占用）；新增**泳道 VAL1**（第 33 条泳道，"VAL" 仅命中 "INVALid" 子串，无命名冲突）。含 11 个 WP（V-01~V-11）+ 5 个运行态门禁（GT-RT-*），共 108 条目 = 103 个原子任务 + 5 个门禁，全局序号 3,335~3,442。

| 维度 | 原值（v3.4） | 并入后 | 增量 |
|------|-------------|--------|------|
| 总 LOC | 426,124 | 440,774 | +14,650 |
| 模块 | 19（A~Q、R1、R2） | 20（+V） | +1 |
| 泳道 | 32 | 33（+VAL1） | +1 |
| WP | 359 | 370 | +11 |
| 任务条目 | 3,340（3,334 任务 + 6 门禁） | 3,448（3,437 任务 + 11 门禁） | +108 |
| 总收口 | 2028-08-18（TR2-10-03） | 2028-09-04（TGT-RT-05） | +17 日 |

### 1.3 EX 型任务卡（DoD 扩展声明）

验证执行类任务的交付物是"**运行过的证据**"而非"契约快照"，故对 §1.2 标准 DoD 作显式扩展（此为对主图纸格式的唯一偏离，理由在此一次性声明）：

- **执行器实现**：代码交付，语言路由见 §1.4；
- **实验执行与证据归档**：证据包落盘 append-only + sha256 链（§3.4）；
- **OS-ACC-RT 判定**：按阈值表逐条对账，产生四态判定之一（§3.2）；
- **复现脚本**：第三方凭证据包可重放同一实验。

除上述 DoD 扩展外，任务卡分片语义（首片=接口与类型禁实现、中片=实现段、末片=单元测试与文档）、9 字段详设卡标题、10 列账本行、8 列 WP 台账行、9 列门禁行均与主图纸 §2/§2.1/§6/§9 严格同构。

### 1.4 语言路由补充（V 模块）

对齐主图纸 L-19/M-13 先例：

- 执行器、判定器、取证与归档 → **Python + pytest**（用户态 SPDX 双轨：`AGPL-3.0-or-later OR Apache-2.0`，Google docstring）；
- QEMU/装机/固件驱动、chaos 注入 shell 面 → **Bash**（同 SPDX，`set -euo pipefail`）。

---

## 2. 实验大纲矩阵（E1~E7）

实验编号规则：`E<域>-<序>`。每个实验必须绑定：唯一阈值来源（NFR/OS-ACC 原文，禁止自设数值）、执行 WP/任务、依赖 WP、证据产物、放行门禁。

| 实验编号 | 名称 | 判定阈值 | 判据来源 | 执行 WP/任务 | 依赖 WP | 证据产物 | 门禁 |
|---------|------|---------|---------|-------------|---------|---------|------|
| E1-01 | 镜像制品 sha256 与签名校验 | 校验 100% 通过 | M-13 镜像 CI 验收 | V-02/TV-02-02 | M-13 | manifest.json + 镜像摘要 | GT-RT-BOOT |
| E1-02 | UEFI/BIOS 双固件冷启动 | 双固件启动成功，串口无 kernel panic | NFR-P-005 | V-02/TV-02-03 | L-19 | console.log + 启动耗时 | GT-RT-BOOT |
| E1-03 | systemd-analyze 冷启动关键链 | 全系统 <30s，边缘 <10s | NFR-P-005 | V-02/TV-02-05 | M-13 | critical-chain 报告 | GT-RT-BOOT |
| E1-04 | kickstart 全自动装机实测 | 裸机/QEMU 各 3 连测成功率 100% | M-03 验收 | V-03/TV-03-03 | M-03 | 装机日志 + 分区校验 | GT-RT-BOOT |
| E1-05 | ostree 原子升级与回滚 | 升级成功 + 回滚成功 + 数据一致 | M-16 验收 | V-10/TV-10-03~08 | M-16 | 升级时间线 + 一致性报告 | — |
| E2-01 | UKUI 会话登录链实测 | lightdm/greeter/会话三级登录成功 | R1 验收 | V-04/TV-04-02~03 | M-17、R1 | 会话日志 + 就绪探针 | GT-RT-SMOKE |
| E2-02 | AgentsIPC 吞吐冒烟 | >100K msg/s、延迟 <10μs（冒烟抽测） | NFR-P-002 | V-04/TV-04-04 | J-08 | ipcbench 报告 | GT-RT-SMOKE |
| E2-03 | Agent 工作流首跑 | 工作流端到端成功 | ecosystem 验收 | V-04/TV-04-05 | J-08 | 工作流 trace | GT-RT-SMOKE |
| E2-04 | 核心服务 active 全量校验 | 关键 systemd 单元 100% active | NFR-P-005 | V-04/TV-04-06 | M-17 | systemctl 报告 | GT-RT-SMOKE |
| E3-01 | 调度延迟 perf+ftrace 实测 | P99<100ms、P99.9<200ms | NFR-P-001 | V-08/TV-08-02 | O-07 | perf/ftrace 原始数据 | GT-RT-PASS |
| E3-02 | 实时任务延迟实测 | <10ms | NFR-P-001 | V-08/TV-08-03 | O-07 | cyclictest 报告 | GT-RT-PASS |
| E3-03 | SMP 公平性与负载均衡 | 无饥饿，均衡偏差达 O-07 基线 | O-07 基线 | V-09/TV-09-02 | O-07 | 压测报告 | GT-RT-PASS |
| E3-04 | NUMA 亲和性与跨节点访问 | 跨节点访问比例达 O-07 基线 | O-07 基线 | V-09/TV-09-03 | O-07 | numastat 报告 | GT-RT-PASS |
| E4-01 | capability 未授权拒绝复验 | 100% 拒绝 + 100% 追踪 | NFR-S-001 | V-07/TV-07-03 | J-15 | 拒绝率报告 | GT-RT-SEC |
| E4-02 | 国密 SM2/SM3/SM4/SM9 与证书链 | 算法与证书链全通过 | 安全设计 | V-07/TV-07-03 | J-15 | 算法测试报告 | GT-RT-SEC |
| E4-03 | attestation 远程证明 | 证明链完整 | SEC2/B-13 设计 | V-07/TV-07-03 | J-15 | attestation 报告 | GT-RT-SEC |
| E4-04 | 外部渗透扫描与渗透用例执行 | 高危漏洞 0 | J-15 验收 | V-07/TV-07-02~03 | J-15 | 渗透报告 | GT-RT-SEC |
| E5-01 | Soak 7×24 长稳 | 无故障、无泄漏 | NFR-R-001 | V-05/TV-05-03~10 | J-09 | 每日快照 + RSS 趋势 | GT-RT-STABLE |
| E5-02 | chaos 注入 | 恢复行为正确、降级达标 | NFR-R-001 | V-06/TV-06-02~08 | J-09 | 注入时间线 | GT-RT-STABLE |
| E5-03 | MTTR 演练 | <5min | NFR-R-001 | V-05/TV-05-11 | J-09 | 演练计时 | GT-RT-STABLE |
| E5-04 | 断电/中断升级恢复 | 恢复成功且数据一致 | M-16 验收 | V-10/TV-10-05 | M-16 | 恢复日志 | — |
| E6-01 | 内存占用实测 | <512MB，边缘 <256MB | NFR-P-006 | V-08/TV-08-08 | O-07 | smem 报告 | GT-RT-PASS |
| E6-02 | KV-cache 命中率实测 | >90% | NFR-P-004 | V-08/TV-08-06 | O-07 | cache 报告 | GT-RT-PASS |
| E6-03 | 批处理吞吐实测 | >85% | NFR-P-004 | V-08/TV-08-07 | O-07 | 吞吐报告 | GT-RT-PASS |
| E6-04 | Token 能效对账 | 达 O-08 框架基线 | O-08 验收 | V-08/TV-08-09（引用 O-08 产物） | O-08 | 能效对账表 | GT-RT-PASS |
| E7-01 | E1~E6 全域回归重放 | 全 PASS / WAIVED 台账完整 | 本规程 §3 | V-11/TV-11-02 | 全域 | 重放汇总 | GT-RT-PASS |
| E7-02 | OS-ACC 110 项 grep 级验收重放 | 110/110 | 130-roadmap/06 | V-11/TV-11-03 | — | acc 报告 | GT-RT-PASS |
| E7-03 | OS-ACC-RT 运行态验收总判定 | 全域四态台账闭合 | 本规程 §3 | V-11/TV-11-04 | — | 总判定表 | GT-RT-PASS |
| E7-04 | 竣工报告与证据 sha256 总链 | 总链完整可验证 | 本规程 §3.4 | V-11/TV-11-06~08 | — | 竣工报告 | GT-RT-PASS |

域划分说明：E1 启动与装机域、E2 桌面与生态域、E3 内核与调度域、E4 安全域、E5 可靠性域、E6 资源与能耗域、E7 竣工域。E3-01/02 的 IPC 全量压测（非冒烟）由 V-04 抽测 + V-08 全量两级承接，与 NFR-P-002 的 128B 头口径一致。

---

## 3. OS-ACC-RT 运行态验收规程

与 `130-roadmap/06-acceptance-criteria.md` 的 OS-ACC（110 项 grep 级静态验收）衔接：OS-ACC-RT 是其**运行态子集与延伸**，编号格式 `OS-ACC-RT-<nnn>`，每个编号绑定 E 矩阵实验与阈值。

### 3.1 六步规程

1. **准备**：加载 ExpSpec（阈值必须逐条引自 NFR/OS-ACC 原文，禁止自设数值）；登记环境（镜像 sha256、机型、固件、日期）；BLOCKED 预登记（见 3.3）。
2. **执行**：runner 按 exp_id 顺序执行，支持断点续跑；禁止旁路输入，一切产物直接落盘证据目录。
3. **取证**：每步产物落盘 `evidence/<YYYY-MM-DD>/<exp-id>/`，manifest.json 登记路径与 sha256，形成哈希链。
4. **判定**：Judge 只读证据包，逐阈值对账 → PASS/FAIL；WAIVED 须工程规范委员会双签；BLOCKED 仅限 3.3 登记在册的实机缺失。
5. **复核**：第二人抽验证据 sha256 与判定一致性；复核不通过回退到执行步重跑。
6. **归档**：append-only 封链，生成复现脚本，登记四态台账。

### 3.2 判定状态机

```
INIT ──准备──> RUNNING ──取证──> EVIDENCED ──判定──> PASS
                    │                │
                    │                ├──> FAIL ──修复──> RUNNING（重跑）
                    │                └──> FAIL ──双签──> WAIVED（台账留痕）
                    └──环境登记实机缺失──> BLOCKED（唯一入口：准备步）
```

- BLOCKED 不参与"通过率"计算，但必须出现在竣工台账中，理由字段必填（机型/接口缺失描述）；
- WAIVED 仅允许用于：a) 有等价替代证据的项；b) 影响面经评审可接受的项。双签邮箱记录于 manifest。

### 3.3 BLOCKED 诚实降级登记（预登记项）

| 项 | 原因 | 影响实验 | 降级方式 |
|----|------|---------|---------|
| sw_64（申威）裸机 | 无实机 | E1-02/E1-04/E1-05 | QEMU 等效镜像冒烟 + BLOCKED 台账 |
| loongarch 裸机 | 无实机 | E1-02/E1-04 | 同上 |
| M2 SMP 大规模多核实机 | 无实机 | E3-03/E3-04 | 中小规模 QEMU SMP 实测 + 外推说明 + BLOCKED 台账 |

### 3.4 证据包规范

```
evidence/
  <YYYY-MM-DD>/
    <exp-id>/
      manifest.json          # 台账头：exp_id/阈值/判定/双签/前链头
      step-01-prepare.json   # 环境登记
      step-02-run.log        # 原始运行日志
      step-03-artifacts/     # 实验产物（报告/原始数据）
      step-04-verdict.json   # 判定器输出
      step-05-review.json    # 复核记录
      chain.sha256           # 哈希链封口
```

manifest.json 必填字段：`exp_id`、`date`、`host`、`image_sha256`、`thresholds[]`（逐条引 source）、`evidences[]`（path+sha256）、`verdict`、`waiver_sig?`（双签邮箱对）、`blocked_reason?`、`prev_chain_head`（链接前日链头，全项目成单链）。目录 append-only：任何回写需新开日期目录并在 manifest 声明 supersedes。

---

## 4. 模块 V 定义与 WP 台账

模块 V：验收与实证（VAL1 泳道独占）。LOC 14,650，WP 11 个，任务 103 个。

WP 台账（§6 八列同构）：

| WP | 名称 | LOC | 泳道 | 前序 WP | 后继 WP | 任务数 | 计划窗口 |
|----|------|-----|------|---------|---------|--------|---------|
| V-01 | OS-ACC-RT 标准与执行器 | 1,460 | VAL1 | L-19 | V-02 | 10 | 2027-08-02 ~ 2027-08-13 |
| V-02 | 镜像构建触发与启动冒烟 | 1,160 | VAL1 | V-01、M-13 | V-03（经 GT-RT-BOOT） | 8 | 2027-08-19 ~ 2027-08-30 |
| V-03 | kickstart 装机实测 | 1,140 | VAL1 | V-02、M-03 | V-10 | 8 | 2027-09-01 ~ 2027-09-10 |
| V-10 | ostree 原子更新实测 | 1,430 | VAL1 | V-03、M-16 | V-04 | 10 | 2027-09-13 ~ 2027-09-24 |
| V-04 | E2E 冒烟执行 | 1,450 | VAL1 | V-10、M-17、J-08 | V-05（经 GT-RT-SMOKE） | 10 | 2027-10-19 ~ 2027-11-01 |
| V-05 | Soak 7×24 执行 | 1,770 | VAL1 | V-04、J-09 | V-06 | 13 | 2027-11-03 ~ 2027-11-19 |
| V-06 | chaos 注入执行 | 1,400 | VAL1 | V-05 | V-07（经 GT-RT-STABLE） | 10 | 2027-11-22 ~ 2027-12-03 |
| V-07 | 渗透执行与安全判定 | 725 | VAL1 | V-06、J-15 | V-08（经 GT-RT-SEC） | 5 | 2027-12-07 ~ 2027-12-13 |
| V-08 | 性能基线实测与 NFR 对账 | 1,450 | VAL1 | V-07、O-07、O-08 | V-09 | 10 | 2028-01-14 ~ 2028-01-27 |
| V-09 | SMP/NUMA 压力实测 | 1,280 | VAL1 | V-08 | V-11 | 9 | 2028-01-28 ~ 2028-02-09 |
| V-11 | 竣工回归重放与总判定 | 1,385 | VAL1 | V-09、R2-10、R1-06 | —（经 GT-RT-PASS 收口） | 10 | 2028-08-21 ~ 2028-09-01 |

排程锚点说明（全部经主图纸账本行实证）：

- V-01 前驱 TL-19-12（QEMU 测试农场，2027-07-30 完工）——先有农场才有执行器落地验证；
- V-02 双前驱 TV-01-10 + TM-13-12（镜像 CI，2027-08-18 完工），次日开工；
- 桌面就绪锚点是 **M-17 首启 bootstrap（2027-10-18 完工）**，故 V-04 E2E 冒烟排 2027-10-19 起；R1-06 Gateway（2028-01-11 完工）场景改由 V-11 竣工重放覆盖；
- V-08 双前驱 TO-07-08（2027-12-14）与 TO-08-04（2028-01-13，原链尾），次年首个工作日开工；
- V-11 三前驱含 TR2-10-03（2028-08-18 完工），TGT-RT-05 为新链尾，总收口 2028-09-04；
- 每施工日 1 任务，周末不排（沿用主图纸规则，不建模节假日）。

---

## 5. 全量账本行（§6 十列同构，108 行）

### 5.1 V-01 OS-ACC-RT 标准与执行器（10 任务，1,460 行）

| ID | 名称 | 交付物 | LOC | 泳道 | 全局序号 | 日期 | 前驱 | 后继 | 状态 |
|----|------|--------|-----|------|---------|------|------|------|------|
| TV-01-01 | OS-ACC-RT 规程数据模型与判定器接口（1/10） | airy_v01/model.py | 142 | VAL1 | 3335 | 2027-08-02 | TL-19-12 | TV-01-02 | ⬜ |
| TV-01-02 | 证据包 schema 与 manifest/sha256 链（2/10） | airy_v01/evidence.py | 138 | VAL1 | 3336 | 2027-08-03 | TV-01-01 | TV-01-03 | ⬜ |
| TV-01-03 | append-only 证据库存储引擎（3/10） | airy_v01/store.py | 155 | VAL1 | 3337 | 2027-08-04 | TV-01-02 | TV-01-04 | ⬜ |
| TV-01-04 | PASS/FAIL/WAIVED/BLOCKED 判定状态机（4/10） | airy_v01/judge.py | 149 | VAL1 | 3338 | 2027-08-05 | TV-01-03 | TV-01-05 | ⬜ |
| TV-01-05 | NFR/OS-ACC 阈值表加载与校验（5/10） | airy_v01/spec.py | 160 | VAL1 | 3339 | 2027-08-06 | TV-01-04 | TV-01-06 | ⬜ |
| TV-01-06 | 实验执行器主循环与断点续跑（6/10） | airy_v01/runner.py | 131 | VAL1 | 3340 | 2027-08-09 | TV-01-05 | TV-01-07 | ⬜ |
| TV-01-07 | 复现脚本生成器（7/10） | airy_v01/repro.py | 127 | VAL1 | 3341 | 2027-08-10 | TV-01-06 | TV-01-08 | ⬜ |
| TV-01-08 | WAIVED 双签工作流（8/10） | airy_v01/waiver.py | 158 | VAL1 | 3342 | 2027-08-11 | TV-01-07 | TV-01-09 | ⬜ |
| TV-01-09 | BLOCKED 实机缺失诚实降级登记（9/10） | airy_v01/blocked.py | 164 | VAL1 | 3343 | 2027-08-12 | TV-01-08 | TV-01-10 | ⬜ |
| TV-01-10 | pytest 单元测试与规程文档（10/10） | tests/test_v01_judge.py + §3 规程定稿 | 136 | VAL1 | 3344 | 2027-08-13 | TV-01-09 | TV-02-01 | ⬜ |

### 5.2 V-02 镜像构建触发与启动冒烟（8 任务，1,160 行）

| ID | 名称 | 交付物 | LOC | 泳道 | 全局序号 | 日期 | 前驱 | 后继 | 状态 |
|----|------|--------|-----|------|---------|------|------|------|------|
| TV-02-01 | 镜像构建触发接口与制品定位（1/8） | airy_v02/trigger.py | 145 | VAL1 | 3345 | 2027-08-19 | TV-01-10、TM-13-12 | TV-02-02 | ⬜ |
| TV-02-02 | 镜像 sha256 校验与签名验证（2/8） | airy_v02/verify.py | 138 | VAL1 | 3346 | 2027-08-20 | TV-02-01 | TV-02-03 | ⬜ |
| TV-02-03 | QEMU UEFI/BIOS 双固件冷启动（3/8） | v02_qboot.sh | 152 | VAL1 | 3347 | 2027-08-23 | TV-02-02 | TV-02-04 | ⬜ |
| TV-02-04 | 串口/控制台日志采集与启动耗时（4/8） | airy_v02/console.py | 141 | VAL1 | 3348 | 2027-08-24 | TV-02-03 | TV-02-05 | ⬜ |
| TV-02-05 | systemd-analyze 冷启动关键链解析（5/8） | airy_v02/bootchain.py | 139 | VAL1 | 3349 | 2027-08-25 | TV-02-04 | TV-02-06 | ⬜ |
| TV-02-06 | 启动冒烟判定 NFR-P-005 <30s/边缘<10s（6/8） | airy_v02/smoke.py | 156 | VAL1 | 3350 | 2027-08-26 | TV-02-05 | TV-02-07 | ⬜ |
| TV-02-07 | 启动失败分类与 BLOCKED 登记（7/8） | airy_v02/bootfail.py | 148 | VAL1 | 3351 | 2027-08-27 | TV-02-06 | TV-02-08 | ⬜ |
| TV-02-08 | pytest 单元测试与复现脚本（8/8） | tests/test_v02_boot.py | 141 | VAL1 | 3352 | 2027-08-30 | TV-02-07 | TGT-RT-01 | ⬜ |

### 5.3 门禁 TGT-RT-01

| ID | 名称 | 交付物 | LOC | 泳道 | 全局序号 | 日期 | 前驱 | 后继 | 状态 |
|----|------|--------|-----|------|---------|------|------|------|------|
| TGT-RT-01 | GT-RT-BOOT 启动与装机实证门禁 | 门禁执行记录（§9） | 0 | VAL1 | 3353 | 2027-08-31 | TV-02-08 | TV-03-01 | ⬜ |

### 5.4 V-03 kickstart 装机实测（8 任务，1,140 行）

| ID | 名称 | 交付物 | LOC | 泳道 | 全局序号 | 日期 | 前驱 | 后继 | 状态 |
|----|------|--------|-----|------|---------|------|------|------|------|
| TV-03-01 | kickstart 应答文件实测驱动接口（1/8） | v03_ksdrive.sh | 142 | VAL1 | 3354 | 2027-09-01 | TGT-RT-01、TM-03-11 | TV-03-02 | ⬜ |
| TV-03-02 | 裸机/QEMU 装机环境准备与资源隔离（2/8） | v03_envprep.sh | 135 | VAL1 | 3355 | 2027-09-02 | TV-03-01 | TV-03-03 | ⬜ |
| TV-03-03 | kickstart 全自动装机执行（3/8） | v03_ksrun.sh | 148 | VAL1 | 3356 | 2027-09-03 | TV-03-02 | TV-03-04 | ⬜ |
| TV-03-04 | 装机后首次启动与分区校验（4/8） | airy_v03/firstboot.py | 139 | VAL1 | 3357 | 2027-09-06 | TV-03-03 | TV-03-05 | ⬜ |
| TV-03-05 | 装机日志取证与错误注入分类（5/8） | airy_v03/kslog.py | 144 | VAL1 | 3358 | 2027-09-07 | TV-03-04 | TV-03-06 | ⬜ |
| TV-03-06 | 装机成功率判定与重试策略（6/8） | airy_v03/ksjudge.py | 131 | VAL1 | 3359 | 2027-09-08 | TV-03-05 | TV-03-07 | ⬜ |
| TV-03-07 | 装机证据包归档（7/8） | airy_v03/ksarch.py | 157 | VAL1 | 3360 | 2027-09-09 | TV-03-06 | TV-03-08 | ⬜ |
| TV-03-08 | pytest 单元测试与复现脚本（8/8） | tests/test_v03_ks.py | 144 | VAL1 | 3361 | 2027-09-10 | TV-03-07 | TV-10-01 | ⬜ |

### 5.5 V-10 ostree 原子更新实测（10 任务，1,430 行）

| ID | 名称 | 交付物 | LOC | 泳道 | 全局序号 | 日期 | 前驱 | 后继 | 状态 |
|----|------|--------|-----|------|---------|------|------|------|------|
| TV-10-01 | ostree 更新实测驱动接口（1/10） | airy_v10/otadrv.py | 138 | VAL1 | 3362 | 2027-09-13 | TV-03-08、TM-16-13 | TV-10-02 | ⬜ |
| TV-10-02 | OTA 通道制品与签名校验（2/10） | airy_v10/artifact.py | 142 | VAL1 | 3363 | 2027-09-14 | TV-10-01 | TV-10-03 | ⬜ |
| TV-10-03 | 原子升级执行（在线场景）（3/10） | v10_upgrade.sh | 131 | VAL1 | 3364 | 2027-09-15 | TV-10-02 | TV-10-04 | ⬜ |
| TV-10-04 | 升级后健康检查与自动回滚验证（4/10） | airy_v10/health.py | 155 | VAL1 | 3365 | 2027-09-16 | TV-10-03 | TV-10-05 | ⬜ |
| TV-10-05 | 断电/中断注入升级恢复实测（5/10） | v10_powerfail.sh | 149 | VAL1 | 3366 | 2027-09-17 | TV-10-04 | TV-10-06 | ⬜ |
| TV-10-06 | 多版本来回升级 A/B 交替（6/10） | v10_abswitch.sh | 127 | VAL1 | 3367 | 2027-09-20 | TV-10-05 | TV-10-07 | ⬜ |
| TV-10-07 | 升级窗口与带宽受限场景（7/10） | v10_throttle.sh | 160 | VAL1 | 3368 | 2027-09-21 | TV-10-06 | TV-10-08 | ⬜ |
| TV-10-08 | 回滚后数据一致性校验（8/10） | airy_v10/consist.py | 144 | VAL1 | 3369 | 2027-09-22 | TV-10-07 | TV-10-09 | ⬜ |
| TV-10-09 | MTTR 升级路径计时与判定（9/10） | airy_v10/mttr.py | 152 | VAL1 | 3370 | 2027-09-23 | TV-10-08 | TV-10-10 | ⬜ |
| TV-10-10 | pytest 单元测试与复现脚本（10/10） | tests/test_v10_ota.py | 132 | VAL1 | 3371 | 2027-09-24 | TV-10-09 | TV-04-01 | ⬜ |

### 5.6 V-04 E2E 冒烟执行（10 任务，1,450 行）

| ID | 名称 | 交付物 | LOC | 泳道 | 全局序号 | 日期 | 前驱 | 后继 | 状态 |
|----|------|--------|-----|------|---------|------|------|------|------|
| TV-04-01 | E2E 冒烟执行编排接口（1/10） | airy_v04/e2e.py | 145 | VAL1 | 3372 | 2027-10-19 | TV-10-10、TM-17-11、TJ-08-12 | TV-04-02 | ⬜ |
| TV-04-02 | 桌面就绪探针与 UKUI 会话登录实测（2/10） | airy_v04/ukui.py | 138 | VAL1 | 3373 | 2027-10-20 | TV-04-01 | TV-04-03 | ⬜ |
| TV-04-03 | lightdm/ukui-greeter 登录链实测（3/10） | airy_v04/greeter.py | 152 | VAL1 | 3374 | 2027-10-21 | TV-04-02 | TV-04-04 | ⬜ |
| TV-04-04 | AgentsIPC 冒烟抽测 >100K msg/s（4/10） | airy_v04/ipcbench.py | 141 | VAL1 | 3375 | 2027-10-22 | TV-04-03 | TV-04-05 | ⬜ |
| TV-04-05 | Agent 工作流首跑场景（5/10） | airy_v04/wfrun.py | 139 | VAL1 | 3376 | 2027-10-25 | TV-04-04 | TV-04-06 | ⬜ |
| TV-04-06 | 核心服务 systemd 单元全量 active 校验（6/10） | airy_v04/units.py | 156 | VAL1 | 3377 | 2027-10-26 | TV-04-05 | TV-04-07 | ⬜ |
| TV-04-07 | 关键 syscall/接口 ENOSYS 清零复核（7/10） | airy_v04/enosys.py | 148 | VAL1 | 3378 | 2027-10-27 | TV-04-06 | TV-04-08 | ⬜ |
| TV-04-08 | 冒烟失败分类与证据归档（8/10） | airy_v04/smokefail.py | 150 | VAL1 | 3379 | 2027-10-28 | TV-04-07 | TV-04-09 | ⬜ |
| TV-04-09 | GT-RT-SMOKE 判定输入汇总（9/10） | airy_v04/gtinput.py | 131 | VAL1 | 3380 | 2027-10-29 | TV-04-08 | TV-04-10 | ⬜ |
| TV-04-10 | pytest 单元测试与复现脚本（10/10） | tests/test_v04_e2e.py | 150 | VAL1 | 3381 | 2027-11-01 | TV-04-09 | TGT-RT-02 | ⬜ |

### 5.7 门禁 TGT-RT-02

| ID | 名称 | 交付物 | LOC | 泳道 | 全局序号 | 日期 | 前驱 | 后继 | 状态 |
|----|------|--------|-----|------|---------|------|------|------|------|
| TGT-RT-02 | GT-RT-SMOKE E2E 冒烟门禁 | 门禁执行记录（§9） | 0 | VAL1 | 3382 | 2027-11-02 | TV-04-10 | TV-05-01 | ⬜ |

### 5.8 V-05 Soak 7×24 执行（13 任务，1,770 行）

| ID | 名称 | 交付物 | LOC | 泳道 | 全局序号 | 日期 | 前驱 | 后继 | 状态 |
|----|------|--------|-----|------|---------|------|------|------|------|
| TV-05-01 | Soak 编排接口对齐 J-09（1/13） | airy_v05/orch.py | 136 | VAL1 | 3383 | 2027-11-03 | TGT-RT-02、TJ-09-13 | TV-05-02 | ⬜ |
| TV-05-02 | Soak 负载画像与基线快照（2/13） | airy_v05/profile.py | 138 | VAL1 | 3384 | 2027-11-04 | TV-05-01 | TV-05-03 | ⬜ |
| TV-05-03 | 7×24 连续运行启动与心跳监控（3/13） | v05_soak.sh | 134 | VAL1 | 3385 | 2027-11-05 | TV-05-02 | TV-05-04 | ⬜ |
| TV-05-04 | 内存泄漏采样与 RSS 趋势判定（4/13） | airy_v05/rss.py | 139 | VAL1 | 3386 | 2027-11-08 | TV-05-03 | TV-05-05 | ⬜ |
| TV-05-05 | fd/句柄/线程泄漏巡检（5/13） | airy_v05/leak.py | 133 | VAL1 | 3387 | 2027-11-09 | TV-05-04 | TV-05-06 | ⬜ |
| TV-05-06 | 日志错误率统计与告警阈值（6/13） | airy_v05/errrate.py | 137 | VAL1 | 3388 | 2027-11-10 | TV-05-05 | TV-05-07 | ⬜ |
| TV-05-07 | 中途采样取证每日快照（7/13） | airy_v05/daily.py | 135 | VAL1 | 3389 | 2027-11-11 | TV-05-06 | TV-05-08 | ⬜ |
| TV-05-08 | 故障事件时间线与根因登记（8/13） | airy_v05/timeline.py | 140 | VAL1 | 3390 | 2027-11-12 | TV-05-07 | TV-05-09 | ⬜ |
| TV-05-09 | 长稳收尾取证与清场（9/13） | airy_v05/finish.py | 132 | VAL1 | 3391 | 2027-11-15 | TV-05-08 | TV-05-10 | ⬜ |
| TV-05-10 | NFR-R-001 无故障无泄漏判定（10/13） | airy_v05/verdict.py | 141 | VAL1 | 3392 | 2027-11-16 | TV-05-09 | TV-05-11 | ⬜ |
| TV-05-11 | MTTR 演练计时 <5min（11/13） | airy_v05/mttr.py | 130 | VAL1 | 3393 | 2027-11-17 | TV-05-10 | TV-05-12 | ⬜ |
| TV-05-12 | Soak 证据包 sha256 链归档（12/13） | airy_v05/archive.py | 142 | VAL1 | 3394 | 2027-11-18 | TV-05-11 | TV-05-13 | ⬜ |
| TV-05-13 | pytest 单元测试与文档（13/13） | tests/test_v05_soak.py | 133 | VAL1 | 3395 | 2027-11-19 | TV-05-12 | TV-06-01 | ⬜ |

### 5.9 V-06 chaos 注入执行（10 任务，1,400 行）

| ID | 名称 | 交付物 | LOC | 泳道 | 全局序号 | 日期 | 前驱 | 后继 | 状态 |
|----|------|--------|-----|------|---------|------|------|------|------|
| TV-06-01 | chaos 注入执行编排接口（1/10） | airy_v06/orch.py | 140 | VAL1 | 3396 | 2027-11-22 | TV-05-13 | TV-06-02 | ⬜ |
| TV-06-02 | CPU/内存/IO 资源压力注入（2/10） | v06_res.sh | 138 | VAL1 | 3397 | 2027-11-23 | TV-06-01 | TV-06-03 | ⬜ |
| TV-06-03 | 进程杀死与服务重启注入（3/10） | v06_kill.sh | 142 | VAL1 | 3398 | 2027-11-24 | TV-06-02 | TV-06-04 | ⬜ |
| TV-06-04 | 网络延迟/丢包/分区注入（4/10） | v06_net.sh | 139 | VAL1 | 3399 | 2027-11-25 | TV-06-03 | TV-06-05 | ⬜ |
| TV-06-05 | 磁盘满/坏块注入（5/10） | v06_disk.sh | 141 | VAL1 | 3400 | 2027-11-26 | TV-06-04 | TV-06-06 | ⬜ |
| TV-06-06 | 内核侧注入对齐 QA 泳道工具（6/10） | v06_kern.sh | 137 | VAL1 | 3401 | 2027-11-29 | TV-06-05 | TV-06-07 | ⬜ |
| TV-06-07 | 注入后恢复时间与降级行为判定（7/10） | airy_v06/recover.py | 143 | VAL1 | 3402 | 2027-11-30 | TV-06-06 | TV-06-08 | ⬜ |
| TV-06-08 | 数据一致性/完整性校验（8/10） | airy_v06/integrity.py | 136 | VAL1 | 3403 | 2027-12-01 | TV-06-07 | TV-06-09 | ⬜ |
| TV-06-09 | chaos 证据包归档与判定（9/10） | airy_v06/archive.py | 144 | VAL1 | 3404 | 2027-12-02 | TV-06-08 | TV-06-10 | ⬜ |
| TV-06-10 | pytest 单元测试与复现脚本（10/10） | tests/test_v06_chaos.py | 140 | VAL1 | 3405 | 2027-12-03 | TV-06-09 | TGT-RT-03 | ⬜ |

### 5.10 门禁 TGT-RT-03

| ID | 名称 | 交付物 | LOC | 泳道 | 全局序号 | 日期 | 前驱 | 后继 | 状态 |
|----|------|--------|-----|------|---------|------|------|------|------|
| TGT-RT-03 | GT-RT-STABLE 长稳与混沌门禁 | 门禁执行记录（§9） | 0 | VAL1 | 3406 | 2027-12-06 | TV-06-10 | TV-07-01 | ⬜ |

### 5.11 V-07 渗透执行与安全判定（5 任务，725 行）

| ID | 名称 | 交付物 | LOC | 泳道 | 全局序号 | 日期 | 前驱 | 后继 | 状态 |
|----|------|--------|-----|------|---------|------|------|------|------|
| TV-07-01 | 渗透执行编排接口对齐 J-15（1/5） | airy_v07/orch.py | 145 | VAL1 | 3407 | 2027-12-07 | TGT-RT-03、TJ-15-03 | TV-07-02 | ⬜ |
| TV-07-02 | 外部扫描器全量执行与资产核对（2/5） | v07_scan.sh | 142 | VAL1 | 3408 | 2027-12-08 | TV-07-01 | TV-07-03 | ⬜ |
| TV-07-03 | 渗透用例执行与漏洞复验（3/5） | airy_v07/pentest.py | 148 | VAL1 | 3409 | 2027-12-09 | TV-07-02 | TV-07-04 | ⬜ |
| TV-07-04 | 高危漏洞零容忍判定与 WAIVED 流程（4/5） | airy_v07/zerotrust.py | 139 | VAL1 | 3410 | 2027-12-10 | TV-07-03 | TV-07-05 | ⬜ |
| TV-07-05 | 渗透证据包归档与 GT-RT-SEC 判定输入（5/5） | airy_v07/archive.py | 151 | VAL1 | 3411 | 2027-12-13 | TV-07-04 | TGT-RT-04 | ⬜ |

### 5.12 门禁 TGT-RT-04

| ID | 名称 | 交付物 | LOC | 泳道 | 全局序号 | 日期 | 前驱 | 后继 | 状态 |
|----|------|--------|-----|------|---------|------|------|------|------|
| TGT-RT-04 | GT-RT-SEC 安全渗透门禁 | 门禁执行记录（§9） | 0 | VAL1 | 3412 | 2027-12-14 | TV-07-05 | TV-08-01 | ⬜ |

### 5.13 V-08 性能基线实测与 NFR 对账（10 任务，1,450 行）

| ID | 名称 | 交付物 | LOC | 泳道 | 全局序号 | 日期 | 前驱 | 后继 | 状态 |
|----|------|--------|-----|------|---------|------|------|------|------|
| TV-08-01 | 性能实测编排接口与基线登记（1/10） | airy_v08/orch.py | 148 | VAL1 | 3413 | 2028-01-14 | TGT-RT-04、TO-07-08、TO-08-04 | TV-08-02 | ⬜ |
| TV-08-02 | 调度延迟 perf+ftrace 实测 P99<100ms（2/10） | airy_v08/latency.py | 142 | VAL1 | 3414 | 2028-01-17 | TV-08-01 | TV-08-03 | ⬜ |
| TV-08-03 | 实时任务延迟 <10ms 实测（3/10） | airy_v08/rtlat.py | 155 | VAL1 | 3415 | 2028-01-18 | TV-08-02 | TV-08-04 | ⬜ |
| TV-08-04 | IPC 吞吐 >100K msg/s 与延迟 <10μs 实测（4/10） | airy_v08/ipcperf.py | 139 | VAL1 | 3416 | 2028-01-19 | TV-08-03 | TV-08-05 | ⬜ |
| TV-08-05 | 超节点切换 <10μs/迁移 <100ms 实测（5/10） | airy_v08/supernode.py | 151 | VAL1 | 3417 | 2028-01-20 | TV-08-04 | TV-08-06 | ⬜ |
| TV-08-06 | KV-cache 命中 >90% 实测（6/10） | airy_v08/kvcache.py | 136 | VAL1 | 3418 | 2028-01-21 | TV-08-05 | TV-08-07 | ⬜ |
| TV-08-07 | 批处理吞吐 >85% 实测（7/10） | airy_v08/batch.py | 158 | VAL1 | 3419 | 2028-01-24 | TV-08-06 | TV-08-08 | ⬜ |
| TV-08-08 | 内存占用 <512MB/边缘<256MB 实测（8/10） | airy_v08/memfoot.py | 144 | VAL1 | 3420 | 2028-01-25 | TV-08-07 | TV-08-09 | ⬜ |
| TV-08-09 | NFR 全量对账表生成与偏差登记（9/10） | airy_v08/nfrtab.py | 132 | VAL1 | 3421 | 2028-01-26 | TV-08-08 | TV-08-10 | ⬜ |
| TV-08-10 | pytest 单元测试与复现脚本（10/10） | tests/test_v08_perf.py | 145 | VAL1 | 3422 | 2028-01-27 | TV-08-09 | TV-09-01 | ⬜ |

### 5.14 V-09 SMP/NUMA 压力实测（9 任务，1,280 行）

| ID | 名称 | 交付物 | LOC | 泳道 | 全局序号 | 日期 | 前驱 | 后继 | 状态 |
|----|------|--------|-----|------|---------|------|------|------|------|
| TV-09-01 | SMP/NUMA 压测编排接口（1/9） | airy_v09/orch.py | 142 | VAL1 | 3423 | 2028-01-28 | TV-08-10 | TV-09-02 | ⬜ |
| TV-09-02 | 多核调度公平性与负载均衡实测（2/9） | airy_v09/smpfair.py | 138 | VAL1 | 3424 | 2028-01-31 | TV-09-01 | TV-09-03 | ⬜ |
| TV-09-03 | NUMA 亲和性与跨节点访问实测（3/9） | airy_v09/numa.py | 145 | VAL1 | 3425 | 2028-02-01 | TV-09-02 | TV-09-04 | ⬜ |
| TV-09-04 | 大规模并发任务压力实测（4/9） | airy_v09/concur.py | 131 | VAL1 | 3426 | 2028-02-02 | TV-09-03 | TV-09-05 | ⬜ |
| TV-09-05 | cgroup/资源格限流实测（5/9） | airy_v09/cgroup.py | 152 | VAL1 | 3427 | 2028-02-03 | TV-09-04 | TV-09-06 | ⬜ |
| TV-09-06 | 长时高压稳定性抽测 24h（6/9） | v09_sustain.sh | 139 | VAL1 | 3428 | 2028-02-04 | TV-09-05 | TV-09-07 | ⬜ |
| TV-09-07 | 压测指标对账与阈值判定（7/9） | airy_v09/recon.py | 148 | VAL1 | 3429 | 2028-02-07 | TV-09-06 | TV-09-08 | ⬜ |
| TV-09-08 | M2 SMP 实机缺失 BLOCKED 登记（8/9） | airy_v09/blocked.py | 135 | VAL1 | 3430 | 2028-02-08 | TV-09-07 | TV-09-09 | ⬜ |
| TV-09-09 | pytest 单元测试与复现脚本（9/9） | tests/test_v09_stress.py | 150 | VAL1 | 3431 | 2028-02-09 | TV-09-08 | TV-11-01 | ⬜ |

### 5.15 V-11 竣工回归重放与总判定（10 任务，1,385 行）

| ID | 名称 | 交付物 | LOC | 泳道 | 全局序号 | 日期 | 前驱 | 后继 | 状态 |
|----|------|--------|-----|------|---------|------|------|------|------|
| TV-11-01 | 竣工回归重放编排接口（1/10） | airy_v11/replay.py | 139 | VAL1 | 3432 | 2028-08-21 | TV-09-09、TR2-10-03、TR1-06-02 | TV-11-02 | ⬜ |
| TV-11-02 | E1~E6 全域回归用例重放（2/10） | airy_v11/e_replay.py | 135 | VAL1 | 3433 | 2028-08-22 | TV-11-01 | TV-11-03 | ⬜ |
| TV-11-03 | OS-ACC 110 项 grep 级验收重放（3/10） | airy_v11/acc_grep.py | 142 | VAL1 | 3434 | 2028-08-23 | TV-11-02 | TV-11-04 | ⬜ |
| TV-11-04 | OS-ACC-RT 运行态验收全量重放（4/10） | airy_v11/acc_rt.py | 128 | VAL1 | 3435 | 2028-08-24 | TV-11-03 | TV-11-05 | ⬜ |
| TV-11-05 | R1-06 Gateway 唯一入口竣工场景重放（5/10） | airy_v11/gateway.py | 146 | VAL1 | 3436 | 2028-08-25 | TV-11-04 | TV-11-06 | ⬜ |
| TV-11-06 | 竣工证据包汇总与 sha256 总链（6/10） | airy_v11/sumchain.py | 132 | VAL1 | 3437 | 2028-08-28 | TV-11-05 | TV-11-07 | ⬜ |
| TV-11-07 | GT-RT-PASS 总判定执行（7/10） | airy_v11/gtpass.py | 141 | VAL1 | 3438 | 2028-08-29 | TV-11-06 | TV-11-08 | ⬜ |
| TV-11-08 | 竣工报告生成（8/10） | airy_v11/report.py | 130 | VAL1 | 3439 | 2028-08-30 | TV-11-07 | TV-11-09 | ⬜ |
| TV-11-09 | 遗留 WAIVED/BLOCKED 台账复核（9/10） | airy_v11/ledger.py | 143 | VAL1 | 3440 | 2028-08-31 | TV-11-08 | TV-11-10 | ⬜ |
| TV-11-10 | pytest 单元测试与竣工验收报告模板（10/10） | tests/test_v11_replay.py | 149 | VAL1 | 3441 | 2028-09-01 | TV-11-09 | TGT-RT-05 | ⬜ |

### 5.16 门禁 TGT-RT-05（链尾）

| ID | 名称 | 交付物 | LOC | 泳道 | 全局序号 | 日期 | 前驱 | 后继 | 状态 |
|----|------|--------|-----|------|---------|------|------|------|------|
| TGT-RT-05 | GT-RT-PASS 竣工总验收门禁（链尾） | 竣工总判定记录（§9） | 0 | VAL1 | 3442 | 2028-09-04 | TV-11-10 | —（链尾） | ⬜ |

---

## 6. GT-RT-* 运行态门禁表（§9 九列同构，5 行）

| 门禁ID | 名称 | 泳道 | 触发WP | 任务ID | 窗口 | 下游WP | 前驱任务 | 后继任务 |
|--------|------|------|--------|--------|------|--------|---------|---------|
| GT-RT-BOOT | 启动与装机实证门禁（E1 域全 PASS/WAIVED 方可进入装机实测） | VAL1 | V-02 | TGT-RT-01 | 2027-08-31 | V-03 | TV-02-08、TM-13-12 | TV-03-01 |
| GT-RT-SMOKE | E2E 冒烟门禁（E2 域全 PASS/WAIVED 方可进入长稳） | VAL1 | V-04 | TGT-RT-02 | 2027-11-02 | V-05 | TV-04-10、TV-10-10、TM-17-11 | TV-05-01 |
| GT-RT-STABLE | 长稳与混沌门禁（E5-01~03 全 PASS 方可进入渗透） | VAL1 | V-06 | TGT-RT-03 | 2027-12-06 | V-07 | TV-06-10、TV-05-13 | TV-07-01 |
| GT-RT-SEC | 安全渗透门禁（E4 域高危 0 方可进入性能实测） | VAL1 | V-07 | TGT-RT-04 | 2027-12-14 | V-08 | TV-07-05、TJ-15-03 | TV-08-01 |
| GT-RT-PASS | 竣工总验收门禁（E7 域四态台账闭合，项目收口） | VAL1 | V-11 | TGT-RT-05 | 2028-09-04 | —（收口） | TV-11-10、TR2-10-03、TR1-06-02 | —（链尾） |

---

## 7. EX 型详设卡示例（§2.1 同构）

以下 6 张卡覆盖三种片型与两种语言。**其余 102 张卡并入主图纸时按 §2.1 同构展开**，此处不重复罗列。

**TV-01-01｜OS-ACC-RT 标准与执行器：接口与类型（1/10）**

```python
# SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0
# Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
"""OS-ACC-RT 规程数据模型与判定器接口（首片：仅接口与类型，禁实现）。"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class Verdict(Enum):
    """实验判定四态，与 OS-ACC-RT §3.2 状态机一一对应。"""

    PASS = "PASS"
    FAIL = "FAIL"
    WAIVED = "WAIVED"      # 工程规范委员会双签
    BLOCKED = "BLOCKED"    # 实机缺失诚实降级，仅准备步可进入


@dataclass(frozen=True)
class Threshold:
    """单条量化阈值，取值必须逐条引自 NFR/OS-ACC 原文。

    Attributes:
        key: 阈值键，如 nfr_p_001_p99。
        source: 判据来源编号，如 NFR-P-001。
        limit: 阈值原文，如 "P99 < 100ms"。
        unit: 计量单位，如 ms。
    """

    key: str
    source: str
    limit: str
    unit: str


@dataclass(frozen=True)
class Evidence:
    """证据条目：文件落盘后由 sha256 链封口，目录 append-only。"""

    path: str
    sha256: str
    step: str  # 准备/执行/取证/判定/复核/归档


@dataclass
class ExpResult:
    """单实验结果。判定器只读 evidences，禁止旁路输入。"""

    exp_id: str
    thresholds: tuple[Threshold, ...]
    evidences: list[Evidence] = field(default_factory=list)
    verdict: Verdict | None = None
    waiver_sig: tuple[str, str] | None = None  # 双签邮箱对
    blocked_reason: str = ""


class Judge(Protocol):
    """判定器协议，实现位于 TV-01-04。"""

    def decide(self, result: ExpResult) -> Verdict:
        """按阈值表逐条对账，返回四态之一；证据缺失直接 FAIL。"""
```

**TV-02-03｜镜像构建触发与启动冒烟：QEMU 双固件冷启动（3/8）**

```bash
#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0
# Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
# TV-02-03：QEMU UEFI/BIOS 双固件冷启动（中片：实现段）。
# E1-02 执行体；失败时按 OS-STD-CODE-030 返回非零并落盘 console.log。
set -euo pipefail

V02_OVMF="${V02_OVMF:-/usr/share/ovmf/OVMF.fd}"
V02_TIMEOUT="${V02_TIMEOUT:-120}"

qboot_wait() {  # $1=日志 $2=期待串；命中返 0，超时返 1
    local log="$1" want="$2" i=0
    while (( i < V02_TIMEOUT )); do
        grep -q "$want" "$log" && return 0
        sleep 1; i=$((i + 1))
    done
    return 1
}

qboot_run() {  # $1=镜像 $2=固件(uefi|bios) $3=证据目录；返 0 成功
    local img="$1" fw="$2" out="$3" extra=()
    mkdir -p "$out"
    [[ "$fw" == "uefi" ]] && extra=(-bios "$V02_OVMF")
    qemu-system-x86_64 -m 4096 -smp 4 \
        -drive "file=$img,format=qcow2,if=virtio" \
        "${extra[@]}" \
        -serial "file:$out/console.log" \
        -display none -daemonize -pidfile "$out/qemu.pid"
    qboot_wait "$out/console.log" "login:"
}

qboot_sweep() {  # 收尾清场：杀残留 QEMU，幂等
    local out="$1"
    if [[ -f "$out/qemu.pid" ]]; then
        kill "$(cat "$out/qemu.pid")" 2>/dev/null || true
        rm -f "$out/qemu.pid"
    fi
}
```

**TV-05-09｜Soak 7×24 执行：长稳收尾取证与清场（9/13）**

```python
# SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0
# Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
"""TV-05-09：长稳收尾取证与清场（中片：实现段）。E5-01 收口动作。"""

import hashlib
import json
import shutil
from pathlib import Path

V05_STEPS = ("执行", "取证", "判定", "复核", "归档")


def sha_of(path: Path) -> str:
    """流式计算文件 sha256，供链式封口使用。"""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def soak_finish(ev_dir: Path, exp_id: str) -> Path:
    """收尾：为实验目录生成 chain.sha256 并整体转只读。

    Args:
        ev_dir: 证据根目录（append-only 约定见 §3.4）。
        exp_id: 实验编号，如 e5-01。

    Returns:
        chain.sha256 文件路径。

    Raises:
        FileNotFoundError: manifest.json 缺失时拒绝封链。
    """
    exp = ev_dir / exp_id
    manifest = exp / "manifest.json"
    if not manifest.is_file():
        raise FileNotFoundError(f"manifest missing: {manifest}")
    lines = [f"{sha_of(p)}  {p.relative_to(exp)}\n"
             for p in sorted(exp.rglob("*")) if p.is_file()]
    chain = exp / "chain.sha256"
    chain.write_text("".join(lines), encoding="utf-8")
    lines.append(f"{sha_of(chain)}  chain.sha256\n")
    chain.write_text("".join(lines), encoding="utf-8")
    for p in exp.rglob("*"):
        shutil.chmod(p, 0o444 if p.is_file() else 0o555)
    return chain


def soak_manifest(ev_dir: Path, exp_id: str, verdict: str,
                  prev_head: str) -> dict:
    """组装台账头；verdict 取 Verdict 四态之一，prev_head 链接前日链头。"""
    return {"exp_id": exp_id, "verdict": verdict,
            "prev_chain_head": prev_head}
```

**TV-08-02｜性能基线实测与 NFR 对账：调度延迟 perf+ftrace（2/10）**

```python
# SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0
# Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
"""TV-08-02：调度延迟 perf+ftrace 实测（中片：实现段）。E3-01 执行体。"""

import json
import subprocess
from pathlib import Path

V08_PCTL = (99.0, 99.9)          # 对应 NFR-P-001：P99<100ms、P99.9<200ms
V08_LIMIT_MS = {99.0: 100.0, 99.9: 200.0}


def lat_ftrace(dur_s: int, out: Path) -> list[int]:
    """ftrace 采样 sched_switch 抓上下文切换延迟，返回毫秒样本列。

    Args:
        dur_s: 采样时长（秒），建议 >=60 抑制偶发抖动。
        out: 证据目录，原始 trace 落盘 trace.dat。

    Returns:
        延迟样本列表（ms），供 lat_pctl 分位计算。
    """
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["trace-cmd", "record", "-e", "sched:sched_switch",
         "-b", "8192", "-o", str(out / "trace.dat"),
         "sleep", str(dur_s)], check=True)
    rep = subprocess.run(
        ["trace-cmd", "report", str(out / "trace.dat")],
        check=True, capture_output=True, text=True)
    return lat_parse(rep.stdout)


def lat_parse(text: str) -> list[int]:
    """从 trace-cmd report 提取运行队列等待时长样本（ms）。"""
    samples = []
    for line in text.splitlines():
        if "switch" not in line:
            continue
        for tok in line.split():
            if tok.endswith("ms") and tok[:-2].replace(".", "").isdigit():
                samples.append(int(float(tok[:-2]) * 1000))
    return samples


def lat_pctl(samples: list[int], out: Path) -> dict:
    """计算 P99/P99.9 并对账 NFR-P-001，产出判定 JSON。

    Returns:
        {"p99": x, "p99_9": y, "verdict": "PASS"|"FAIL"}。
    """
    s = sorted(samples)
    n = len(s)
    got = {p: s[min(n - 1, int(n * p / 100))] / 1000.0 for p in V08_PCTL}
    verdict = "PASS" if all(
        got[p] < V08_LIMIT_MS[p] for p in V08_PCTL) else "FAIL"
    rep = {"source": "NFR-P-001", "p99": got[99.0],
           "p99_9": got[99.9], "verdict": verdict}
    (out / "step-04-verdict.json").write_text(
        json.dumps(rep, indent=2), encoding="utf-8")
    return rep
```

**TV-11-10｜竣工回归重放与总判定：单元测试与竣工验收报告模板（10/10）**

```python
# SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0
# Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
"""TV-11-10：V-11 单元测试（末片：单元测试与文档）。"""

import json

import pytest

from airy_v11.gtpass import gtpass_decide
from airy_v11.ledger import load_ledger


def test_gtpass_all_pass(tmp_path):
    """E1~E6 全 PASS 时 GT-RT-PASS 必须判 PASS。"""
    ledger = [{"exp_id": f"e{i}-01", "verdict": "PASS"} for i in range(1, 7)]
    assert gtpass_decide(ledger) == "PASS"


def test_gtpass_fail_blocks(tmp_path):
    """任一 FAIL 未转 WAIVED 必须判 FAIL，禁止带病收口。"""
    ledger = [{"exp_id": "e1-01", "verdict": "FAIL"}]
    assert gtpass_decide(ledger) == "FAIL"


def test_gtpass_blocked_requires_reason():
    """BLOCKED 必须携带降级理由，空理由判 FAIL。"""
    ledger = [{"exp_id": "e3-03", "verdict": "BLOCKED",
               "blocked_reason": "M2 SMP 实机缺失"}]
    assert gtpass_decide(ledger) == "PASS"
    assert gtpass_decide([{"exp_id": "e3-03", "verdict": "BLOCKED",
                           "blocked_reason": ""}]) == "FAIL"


def test_ledger_chain(tmp_path):
    """台账 sha256 链必须逐级可验证，篡改任一环即断链。"""
    root = tmp_path / "evidence"
    (root / "2028-08-28" / "e7-03").mkdir(parents=True)
    (root / "2028-08-28" / "e7-03" / "manifest.json").write_text(
        json.dumps({"exp_id": "e7-03", "verdict": "PASS"}))
    ent = load_ledger(root)
    assert ent["e7-03"]["verdict"] == "PASS"
```

**TGT-RT-01｜GT-RT-BOOT 启动与装机实证门禁（门禁执行体）**

```bash
#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0
# Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
# TGT-RT-01：GT-RT-BOOT 门禁。E1 域全 PASS/WAIVED 放行 V-03；
# FAIL 退出 1；BLOCKED 仅放行 §3.3 预登记项。
set -euo pipefail

EV_ROOT="${1:?用法: tgt_rt_01.sh <证据根目录>}"
ALLOWED_BLOCKED="sw_64|loongarch"

rc=0
while IFS= read -r mf; do
    verdict="$(python3 -c \
        "import json,sys;print(json.load(open(sys.argv[1]))['verdict'])" \
        "$mf")"
    reason="$(python3 -c "import json,sys; \
print(json.load(open(sys.argv[1])).get('blocked_reason',''))" "$mf")"
    case "$verdict" in
        PASS|WAIVED) ;;
        BLOCKED)
            echo "$reason" | grep -Eq "$ALLOWED_BLOCKED" || {
                echo "非法 BLOCKED: $mf"; rc=1; } ;;
        FAIL)
            echo "FAIL 未清零: $mf"; rc=1 ;;
        *) echo "未知判定: $mf"; rc=1 ;;
    esac
done < <(find "$EV_ROOT" -name manifest.json | sort)

(( rc == 0 )) && echo "GT-RT-BOOT: PASS" || echo "GT-RT-BOOT: REJECT"
exit "$rc"
```

---

## 8. 既有账本回填表（12 行）

并入主图纸 §6 时，以下既有末任务的"后继"列需追加 V 模块任务 ID（双向对称断言用）：

| 既有任务 ID | 既有任务名称 | 原后继 | 修订后后继 |
|------------|-------------|--------|-----------|
| TL-19-12 | QEMU 测试农场（12/12） | TL-21-01, TM-13-01 | TL-21-01, TM-13-01, TV-01-01 |
| TM-13-12 | 镜像 CI 集成（12/12） | TM-16-01 | TM-16-01, TV-02-01 |
| TM-03-11 | kickstart 自动安装（11/11） | TM-05-01, TM-19-01 | TM-05-01, TM-19-01, TV-03-01 |
| TM-16-13 | OTA 更新通道（13/13） | TM-18-01 | TM-18-01, TV-10-01 |
| TM-17-11 | 首启 bootstrap（11/11） | TM-19-01 | TM-19-01, TV-04-01 |
| TJ-08-12 | E2E 测试编排（12/12） | TJ-09-01, TJ-10-01, TJ-12-01 | TJ-09-01, TJ-10-01, TJ-12-01, TV-04-01 |
| TJ-09-13 | Soak/chaos 框架（13/13） | TJ-11-01, TJ-18-01 | TJ-11-01, TJ-18-01, TV-05-01 |
| TJ-15-03 | 渗透测试套件（3/3） | TJ-17-01 | TJ-17-01, TV-07-01 |
| TO-07-08 | 性能回归门禁固化（8/8） | TO-08-01 | TO-08-01, TV-08-01 |
| TO-08-04 | Token 能效框架（4/4） | —（链尾） | TV-08-01 |
| TR2-10-03 | GPLv3 合规与滚动发布解耦（3/3） | —（链尾） | TV-11-01 |
| TR1-06-02 | Gateway 唯一入口（2/2） | TR2-03-01 | TR2-03-01, TV-11-01 |

回填后链尾语义变更：TO-08-04 与 TR2-10-03 不再是链尾；唯一链尾为 TGT-RT-05（2028-09-04）。

---

## 9. 账目与排程影响核算

### 9.1 §3.1 LOC 对账表追加行

| 模块 | 申报 LOC | 核对 LOC | 偏差 |
|------|---------|---------|------|
| V | 14,650 | 14,650 | 0 |

### 9.2 分 WP LOC 明细（合计校验）

| WP | 任务数 | LOC 合计 | 各任务 LOC |
|----|--------|---------|-----------|
| V-01 | 10 | 1,460 | 142,138,155,149,160,131,127,158,164,136 |
| V-02 | 8 | 1,160 | 145,138,152,141,139,156,148,141 |
| V-03 | 8 | 1,140 | 142,135,148,139,144,131,157,144 |
| V-10 | 10 | 1,430 | 138,142,131,155,149,127,160,144,152,132 |
| V-04 | 10 | 1,450 | 145,138,152,141,139,156,148,150,131,150 |
| V-05 | 13 | 1,770 | 136,138,134,139,133,137,135,140,132,141,130,142,133 |
| V-06 | 10 | 1,400 | 140,138,142,139,141,137,143,136,144,140 |
| V-07 | 5 | 725 | 145,142,148,139,151 |
| V-08 | 10 | 1,450 | 148,142,155,139,151,136,158,144,132,145 |
| V-09 | 9 | 1,280 | 142,138,145,131,152,139,148,135,150 |
| V-11 | 10 | 1,385 | 139,135,142,128,146,132,141,130,143,149 |

### 9.3 排期影响

- 唯一排期影响：竣工窗口 +17 日（2028-08-18 → 2028-09-04），由 V-11 竣工重放与 TGT-RT-05 承接；
- V 泳道与其余 32 条泳道零冲突：V 的全部前驱均为各泳道末任务（后继为空或回填表所示追加），不插入任何既有泳道内部；
- VAL1 泳道内部为单链（每施工日 1 任务），首日 2027-08-02 恰在各前驱完工之后。

---

## 10. 规范符合性自查（50-engineering-standards 对照）

| 检查项 | 规则 | 结论 |
|--------|------|------|
| Copyright 头 | OS-CHK-DOC-01 | ✓ 全部代码卡含 `Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.` |
| 禁词 | OS-CHK-DOC-02 | ✓ 无"简单/仅需/基本完成"类禁词表述 |
| IRON-9 | OS-CHK-DOC-03 | ✓ 未触碰九条铁律；E4 域判定引用原设计编号 |
| [SC] 契约头 | OS-CHK-DOC-04 | ✓ EX 型任务不新增内核契约接口；判定器为用户态 |
| 链接完整性 | OS-CHK-DOC-05 | ✓ §8 回填表 12 行前驱/后继双向对称，无悬空引用 |
| 行数 | OS-CHK-DOC-06 | ✓ 本文档为任务卡草案（增补件），并入主图纸后按主图纸口径 |
| 返回值 | OS-STD-CODE-030 | ✓ Bash 卡 0/非零；Python 卡 raise/返回四态 |
| SPDX 双轨 | 01-coding-standards | ✓ Python/Bash 均用 `AGPL-3.0-or-later OR Apache-2.0` |
| 函数名 | 工程约定 ≤15 字节 | ✓ sha_of/qboot_run/lat_pctl/gtpass_decide 等均在限内 |
| 每任务 LOC | 100~200 | ✓ 103 任务全部在区间内（见 §9.2） |
| 禁止桩实现 | 工程约定 | ✓ 详设卡中片均为可运行实现，首片明示禁实现 |
| 一个实验一个阈值来源 | 50 规范可追溯性 | ✓ §2 矩阵每行判据来源为 NFR/OS-ACC/WP 验收原文 |
| 依赖图性质 | 图论+语义双审 | ✓ 单链无环；§4 锚点说明逐条给出日期一致性依据 |

---

## 11. 并入主图纸的操作清单

1. §4 WP 台账 11 行并入主图纸 §6 对应位置（模块 V 段）；
2. §5 账本行 108 行按全局序号 3,335~3,442 插入 §6 总台账；
3. §6 门禁表 5 行并入主图纸 §9；
4. §8 回填表 12 行执行既有后继列修订；
5. §3.1 对账表追加 V 行并更新总量行（440,774 / 3,448 / 370 WP / 33 泳道）；
6. §1.3 DoD 扩展声明写入主图纸 §1.2；
7. 版本号 v3.4 → v3.5，修订说明记录本增补件。
