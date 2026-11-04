#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0
# Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
"""AirymaxOS 0.0.4 任务图纸生成器。

读 bp_004_seed.py（种子：做什么、多大、先后）与 bp_004_prose.py（散文：判断与口径），
确定性产出 0.0.4-极境OS任务方案.md 的 §0~§19。

与 bp_003_gen.py 的关系：本文件是 0.0.4 独立轨的引擎，不修改也不调用 0.0.3 生成器；
0.0.3 的主图纸账本仍按原生成器对账。

纪律：账本（§5~§8）的每一行数字都由本文件算出；散文不接受手写数字，只接受 c 字典里的值。
"""

import math
import os
import sys
from datetime import date, timedelta

import bp_004_seed as S
import bp_004_prose as P

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "0.0.4-极境OS任务方案.md")

# 切分模型（§0.2）：LOC 固定由种子给出，任务粒度与泳道产能解耦。
#   PER_TASK         单任务净新增行数（用户硬约束：不得超过 TASK_CAP）
#   TASK_CAP         单任务行数硬上限（300，越界即不落盘）
#   LANE_LOC_PER_DAY 每泳道每施工日的净新增产能（与 0.0.3 的 150 行/日等价）
#   TASKS_PER_DAY    每泳道每施工日允许并行推进的任务数 = 产能 / 单任务行数
PER_TASK = 50
TASK_CAP = 300
LANE_LOC_PER_DAY = 150
TASKS_PER_DAY = LANE_LOC_PER_DAY // PER_TASK

START = date(2027, 5, 10)          # 0.0.3 收口（2027-05-07）后的下一个周一
ACCEPT_EVERY = 10                  # 每 10 个施工日插入 1 个验收日
MIN_TASKS = 1000                   # 用户口径：全版任务数不得少于一千个

# ---------------------------------------------------------------- 债号闭合判据

DEBT = {
    "ALK-01": "0.0.4 轨内核侧净新增 0 行：`git diff --stat v0.0.3..v0.0.4 -- kernel/` 为空，"
              "新增文件全部落 `ci/ distro/ tools/ system/ desktop/`；未新增任何 `CONFIG_*`；"
              "`ci/gates/alk-size.sh` 在同配置构建下给出内核镜像体积与 0.0.3 的差值（须为 0，非 0 即红）；"
              "微内核化能力只经既有 `/proc/sys/agentrt` 与 `/sys/kernel/security/airy/policy` 通道表达（J-34）",
    "B-02": "基底耦合点清单成册，逐项标注 0.1.x 处理方式；`coupling-scan.sh` 可复算项数",
    "CI-01": "构建器脚本无死代码，改名后全部调用点已更新，`ci/ci.sh` 全绿",
    "CI-02": "发布自证给出 ISO 摘要 ↔ 内核 NEVRA 对照（D-12 的收口形态），缺任一侧即 BLOCKED",
    "CI-03": "`build-manifest.txt` 记录每架构归档时刻、产物时刻与耗时，可作为预算依据",
    "CI-04": "候选池在 x86_64 与 arm64 均命中；未命中必须打印原因与回退路径",
    "CI-05": "workflow 内联 `run:` 块计数为 0（QG-06）",
    "CI-07": "同 tag 仅一个 in_progress；遗留 run 被显式取消并留有日志",
    "CI-08": "预算漂移超阈值即告警，台账可由种子复算",
    "CI-09": "`ci/check-workflows.py` 断言每个 `runs-on:` 逐字等于 "
              "`tools/nightly/manifest.yaml` 的 `runner.label`，清单缺该键同样判红",
    "CI-10": "门禁不得由字符串形状推语义（`-latest`、路径后缀、包名前缀），一律读显式字段；"
              "`ci/check-workflows.py` 有对应禁用模式",
    "CI-11": "内容寻址层命中/未命中均打印，tag 前缀区分 `build-`/`install-`/`seed-`",
    "CI-12": "治理规则与 `ci/check-workflows.py` 的规则一一对应",
    "CI-13": "全部 `uses:` 钉 40 位 SHA",
    "CI-14": "无 `curl | bash`、无浮动 tag、无隐式 latest",
    "CI-15": "第三方 action 白名单与许可证清单成册",
    "CI-16": "预热 workflow 可定时运行，产物可按 digest 拉取",
    "CI-17": "构建产物带来源证明，可在发布页查询",
    "D-01": "固件包进闭包清单且系统内文件存在（构建期与运行期双判）",
    "D-02": "逐器件核对固件文件存在且可加载",
    "D-03": "逐器件核对固件文件存在且可加载",
    "D-04": "逐器件核对固件文件存在且可加载",
    "D-07": "两份 `grub.cfg` 内容一致，且被加载的那份生效（J-12）",
    "D-29": "每条 active 物料登记生成命令 argv，`--replay` 可按记录重放并核对产物",
    "D-30": "安装器选盘结果与 `lsblk` 一致，多盘场景有回归用例",
    "D-31": "W^X 白名单经既有 `/sys/kernel/security/airy/policy` 接口受控，回归器覆盖全部例外",
    "D-33": "裸盘 / 多盘 / 双系统三拓扑选盘均正确",
    "D-34": "RTC 长停后偏差在阈值内，超阈告警",
    "DEV-01": "新环境一条命令拉起，`ci/ci.sh` 全绿",
    "DOC-01": "文档与账本一致性检查纳入门禁",
    "DOC-02": "悬空链接检查结果为 0",
    "FL-01": "取件子命令统一，`--json` 覆盖全部子命令",
    "FL-02": "三段均输出 `AIRY-FLASH-PASS/FAIL`，退出码与末行一致",
    "FL-03": "`iso-oci.txt` 作为 `<tag>-ledger` 制品在发布页公开可匿名下载；干净环境仅凭公开 URL 完成 `fetch --oci` 取件与校验；`oras manifest fetch` 手工重建列为降级路径且打印命中/未命中",
    "FL-04": "载荷以 digest 引用；断网可回落整包；同 digest 两次装机字节一致",
    "FW-01": "固件清单与 comps 一一对应",
    "FW-02": "缺失项在构建期即红",
    "FW-03": "运行期探针可读出固件版本与加载状态",
    "G-01": "显示策略以能力求交，无硬编码机型分支",
    "G-02": "候选串降序、`auto` 末位，回归用例覆盖",
    "G-03": "输出不支持时回落到共同模式，并打印回落原因",
    "HW-01": "能力矩阵五类逐项有判定，无静默跳过",
    "HW-02": "按能力选机，不按机型白名单",
    "HW-03": "屏幕背光与键盘背光均有用户态入口且可读写",
    "HW-04": "三级登录成功 + 23 进程基线 + 首启 `journalctl -p err -b` 为 0 行",
    "HW-05": "cmdline 无遗留调试项，console 收敛到单一口",
    "HW-06": "Xorg 判据为「KMS 有可枚举模式且 EDID 非空」",
    "HW-07": "桌面显式依赖补齐，comps 可解析",
    "BR-01": "ISO 解包文本召回 openEuler 字样全部命中可复算白名单，白名单外为 0；"
             "`install.img` 内 anaconda 产品名、`splash.png`、`splash.lss` 全部品牌化且引用一致",
    "DISK-01": "装机后 `lsblk` ≥2 个独立分区，`/` 与 `/data` 独立挂载（`findmnt` 可分别取证）；"
               "`/data` 可独立扩容且系统分区 UUID 与 `fsck` 结果不变；裸盘/多盘/双系统三拓扑同一代码路径；"
               "无机型/品牌/盘符硬编码（J-23/J-33）",
    "KM-01": "镜像内全量 `.ko` 具 `.module_sig` 段且 `modinfo -F sig_id` 非空；"
             "`/proc/sys/kernel/tainted` 的 8192 位为 0；T6 kernel identity 实机转绿",
    "KRN-01": "`airy-probe` 经既有 `/proc/sys/agentrt` 与 `/sys/kernel/security/airy/policy` 通道触发并回读计数；既有通道不受理的注入动作如实降级登记，不声称终端事件流",
    "OE-01": "基底按「大 SP + EOL 覆盖交付窗口」规则选型并由 `ci/gates/base-eol.sh` 断言："
             "候选基底的大 SP 属性（12 月 Release，EOL 24 个月）与其 Planned EOL 由"
             "`10-references/openeuler-sp-eol.md` 台账给出且可溯源到官方生命周期页；"
             "基底 Planned EOL 必须晚于本版收口日 2027-09-17，否则该候选不得选为基底（小 SP 一律排除，"
             "如 24.03 LTS SP4 的 Planned EOL 为 2027/03，早于收口日故不可选）；"
             "`%oe_base`、repo 五段 baseurl、lockfile、comps 四处指向同一候选且无 `$releasever`；"
             "候选内核仍为 6.6 线，不违反内核基线铁律；包级差异成册，ABI 破坏项逐条登记",
    "REL-02": "发布说明与资产一致，无未列出资产",
    "REL-03": "发布流程可由「命令 + 摘要」复算",
    "RT-01": "`cpu.rt_runtime_us` 默认非 0 且可被 `airy-rt-cap` 读出",
    "TD-08": "`release.yml` 从 tag 检出构建",
    "TD-09": "`iso-oci.txt` 账本与 `oras pull` 回读逐字段一致（通道 0.0.3 已落地，本条只做回读取证与状态改判）",
    "UK-01": "UKUI 追新以**基底仓库实测 NVRA** 为唯一版本证据：`10-references/ukui-delta.md` "
             "逐组件登记 `ukui-kwin / ukui-panel / ukui-session-manager / ukui-control-center / "
             "ukui-desktop-environment` 在基底各段 repodata 中解析出的实际 NVRA（含 EPOL 段），"
             "与 `distro/lockfile/ukui-*.yaml` 钉住的取值逐字一致；`dnf -q repoquery` 可复算，"
             "依赖闭包可解析，会话 smoke 与 23 进程基线全绿；禁止用上游发布公告替代仓库实测值",
    "UK-02": "UKUI 4.24 可行性成册：`10-references/ukui-424-feasibility.md` 明确记录 openKylin 4.24 "
             "存在于 openKylin 3.0 线而基底 openEuler 24.03 LTS 全条线仓库内 UKUI 停在 3.x 组件代、"
             "无任何 4.2x 且不存在 `ukui-shell` 包这一实测结论；据此给出两条路线的取舍与代价"
             "（按 openKylin 上游重组包名自建源码包闭包 vs. 采用基底内最高稳定组件代），"
             "并把选定路线的自建闭包工作项、风险与顺延结论登记成册；结论必须可由仓库数据复算，"
             "未成册即判 BLOCKED（追新目标与内核基线冲突时内核基线优先，J-35/J-36）",
    "UP-01": "升级通道可下载、可校验、可回滚",
}

# 里程碑：WP 集合全部「已验收」且门禁绿跑才达成。
MILESTONES = [
    ("M4-1", "交付链归零", ["L-40", "L-42"],
     "内联 `run:` 块 = 0；预算台账可复算（QG-06 / QG-08）"),
    ("M4-2", "供应链与发布同源", ["L-41", "L-46", "L-47", "L-48", "L-49", "L-51"],
     "全部 `uses:` 钉 SHA；来源证明可查；发布自证通过（QG-07）；"
     "安装介质品牌面白名单外命中为 0"),
    ("M4-3", "载荷通道", ["L-43", "L-44", "T-01", "T-02", "T-03"],
     "候选池命中可复算；`install-` 通道按 digest 取件（QG-09）"),
    ("M4-4", "磁盘管理", ["M-30", "M-31", "M-32", "M-34", "M-36", "K-24"],
     "三拓扑探测与 `lsblk` 逐字段一致；破坏性操作需二次确认；"
     "至少两个分区且 `/` 与 `/data` 独立挂载，`/data` 可独立扩容"),
    ("M4-5", "桌面追新与使用强化", ["M-33", "R1-10", "R1-11", "R1-13", "R1-12", "R1-14", "R1-15"],
     "23 进程基线绿；锁屏三条根因关闭；内核 NEVRA 未变（QG-11）；"
     "日常使用路径可观测（登录→中文输入→设置面板→磁盘/网络/模型状态）；"
     "内置壁纸集合恰为三张指定件且 digest 与清单一致；"
     "UKUI 组件 NVRA 与 `ukui-delta.md` 逐字一致，4.24 可行性结论成册"),
    ("M4-6", "硬件与固件", ["I-20", "I-21", "I-22", "I-23", "I-24", "I-25", "I-26", "I-27", "I-28", "I-29"],
     "固件闭包门禁绿；五类能力矩阵无静默跳过（QG-10）；烧录后首启 60s 内至少一路网络 DHCP 成功并可达网关"),
    ("M4-7", "模型环境", ["K-20", "K-21", "K-22", "K-23"],
     "完全断网 `airy-model selftest` 通过；降级路径显式"),
    ("M4-8", "RT 适配", ["X-01", "X-02", "X-03", "X-04", "X-05"],
     "`cpu.rt_runtime_us` 非 0；`airy-probe` 十点可读；验收不劣于基线 ×1.2"),
    ("M4-9", "烧录与回归", ["T-04", "V-11"],
     "三段烧录回归均出 `AIRY-FLASH-PASS`；判负集分层可复算"),
    ("M4-10", "收口", ["L-45", "L-50", "M-35", "V-10", "V-12", "V-13", "V-14", "V-15", "V-16"],
     "发布自证齐备；升级通道可回滚；实机矩阵完成（QG-12）；"
     "基底经 `base-eol.sh` 判定为大 SP 且 Planned EOL 晚于收口日，装机 `dnf makecache` 四段成功；"
     "模块签名齐全且 tainted 8192 位为 0；"
     "完整性盘点 `systemctl --failed` 为 0、包闭包对账差 0、docs-linux 功能面缺口登记成册"),
]


# ---------------------------------------------------------------- 账本计算

def topo():
    order, seen = [], set()

    def visit(k):
        if k in seen:
            return
        seen.add(k)
        for d in BYID[k]["deps"]:
            visit(d)
        order.append(k)

    for w in S.WPS:
        visit(w["id"])
    return order


WPS = S.WPS
BYID = {w["id"]: w for w in WPS}
NT, DUR = {}, {}
for _w in WPS:
    if _w["loc"] % PER_TASK:
        sys.exit(f"种子错误：{_w['id']} 的 loc {_w['loc']} 不是 {PER_TASK} 的整数倍")
    if _w["loc"] % LANE_LOC_PER_DAY:
        sys.exit(f"种子错误：{_w['id']} 的 loc {_w['loc']} 不是 {LANE_LOC_PER_DAY} 的整数倍")
    NT[_w["id"]] = _w["loc"] // PER_TASK
    DUR[_w["id"]] = _w["loc"] // LANE_LOC_PER_DAY

ORDER = topo()
SUCC = {w["id"]: [] for w in WPS}
for _w in WPS:
    for _d in _w["deps"]:
        SUCC[_d].append(_w["id"])

# 排程：泳道内串行，WP 间按依赖；每施工日每泳道推进 LANE_LOC_PER_DAY 行当量。
# 施工日按「产能」而非「任务条数」计——细化任务粒度只增加检查点，不拉长日历。
FREE = {l[0]: 0 for l in S.LANES}
WP_START, WP_FIN = {}, {}
for _k in ORDER:
    _w = BYID[_k]
    _ready = max([WP_FIN[d] for d in _w["deps"]] + [FREE[_w["lane"]]])
    WP_START[_k] = _ready + 1
    WP_FIN[_k] = _ready + DUR[_k]
    FREE[_w["lane"]] = WP_FIN[_k]

NDAYS = max(WP_FIN.values())

_WORK = []
_d = START
while len(_WORK) < NDAYS * (ACCEPT_EVERY + 1) // ACCEPT_EVERY + 12:
    if _d.weekday() < 5:
        _WORK.append(_d)
    _d += timedelta(days=1)


def cal(day):
    """施工日序号 -> 日历日（每 10 个施工日后插 1 个验收日）。"""
    return _WORK[day + day // ACCEPT_EVERY - 1]


# 任务表
TASKS = []          # dict(id, wp, idx, n, lane, day, prev, next)
TBY = {}
for _k in ORDER:
    _w = BYID[_k]
    n = NT[_k]
    for i in range(1, n + 1):
        tid = f"{_k}-{i:02d}"
        if i > 1:
            prev = [f"{_k}-{i - 1:02d}"]
        else:
            prev = [f"{d}-{NT[d]:02d}" for d in _w["deps"]]
        if i < n:
            nxt = [f"{_k}-{i + 1:02d}"]
        else:
            nxt = [f"{s}-01" for s in SUCC[_k]]
        t = dict(id=tid, wp=_k, idx=i, n=n, lane=_w["lane"],
                 day=WP_START[_k] + (i - 1) // TASKS_PER_DAY, prev=prev, next=nxt)
        TASKS.append(t)
        TBY[tid] = t

# 关键路径：WP 级 DAG 上按产能日数求最长链
_best, _back = {}, {}
for _k in ORDER:
    _cand = [(_best[d], d) for d in BYID[_k]["deps"]]
    _b = max(_cand) if _cand else (0, None)
    _best[_k] = _b[0] + DUR[_k]
    _back[_k] = _b[1]
_cp_end = max(_best, key=lambda k: _best[k])
CP = []
_k = _cp_end
while _k:
    CP.append(_k)
    _k = _back[_k]
CP.reverse()

TLOC = sum(w["loc"] for w in WPS)
TTASK = len(TASKS)
NLOC = sum(w["loc"] for w in WPS)

# ---------------------------------------------------------------- 断言

def check():
    assert TLOC == TTASK * PER_TASK, "LOC 与任务数不一致"
    assert TTASK == sum(NT.values())
    assert PER_TASK <= TASK_CAP, "单任务行数超过硬上限"
    assert TASKS_PER_DAY * PER_TASK == LANE_LOC_PER_DAY, "泳道产能与任务粒度不整除"
    for _k in NT:
        assert NT[_k] == DUR[_k] * TASKS_PER_DAY, f"{_k} 的任务数与产能日数不匹配"
    assert TTASK >= MIN_TASKS, f"任务总数 {TTASK} 少于 {MIN_TASKS}"
    ids = [t["id"] for t in TASKS]
    assert len(ids) == len(set(ids)), "任务编号重复"
    for t in TASKS:
        for p in t["prev"]:
            assert p in TBY, f"{t['id']} 前驱 {p} 不存在"
            assert t["id"] in TBY[p]["next"], f"前驱 {p} 未登记后继 {t['id']}"
        for s in t["next"]:
            assert s in TBY, f"{t['id']} 后继 {s} 不存在"
            assert t["id"] in TBY[s]["prev"], f"后继 {s} 未登记前驱 {t['id']}"
    owned = {d for w in WPS for d in w["debt"]}
    assert owned == set(DEBT), f"债号不闭合：缺 {owned - set(DEBT)}，多 {set(DEBT) - owned}"
    for m, _n, wl, _g in MILESTONES:
        for k in wl:
            assert k in BYID, f"{m} 引用了不存在的 {k}"
    for _k in ("M-36", "L-51", "V-16"):
        assert _k in BYID, f"缺失必做 WP {_k}"
    assert "分区" in BYID["M-36"]["name"], "M-36 必须交付分区布局"
    assert "品牌" in BYID["L-51"]["name"], "L-51 必须交付安装介质品牌面"
    assert "taint" in BYID["V-16"]["name"].lower(), "V-16 必须复核 taint"
    # ALK 体积与 docs-linux 遵循（用户口径）：模块必须有方案锚点，且本轨不得触碰内核树。
    assert set(S.MODULE_DOCREF) == {m[0] for m in S.MODULES}, "模块锚点与模块表不一致"
    _docs = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
    for _mid, _refs in S.MODULE_DOCREF.items():
        assert _refs, f"{_mid} 缺 docs-linux 锚点"
        for _r in _refs:
            assert _r.startswith("docs-linux/"), f"{_mid} 锚点不在 docs-linux 下：{_r}"
            if os.path.isdir(_docs):
                assert os.path.exists(os.path.join(_docs, _r)), f"{_mid} 锚点文件不存在：{_r}"
    for _w in WPS:
        assert "kernel/" not in _w["art"], f"{_w['id']} 触及 kernel/，违反 ALK 体积边界"
    assert "V-15" in [w["id"] for w in WPS if "ALK-01" in w["debt"]], "ALK-01 未由 V-15 承接"
    assert sum(DUR[k] for k in CP) == NDAYS, "关键路径长度与总施工日不一致"


# ---------------------------------------------------------------- 表格发射

def t_scope():
    out = ["| 模块 | WP | 名称 | 净新增 LOC | 任务数 | 泳道 | 严格前驱 | 承接债 |",
           "|---|---|---|---|---|---|---|---|"]
    for k in ORDER:
        w = BYID[k]
        out.append("| {} | {} | {} | {:,} | {} | {} | {} | {} |".format(
            w["mod"], w["id"], w["name"], w["loc"], NT[k], w["lane"],
            ", ".join(w["deps"]) if w["deps"] else "—",
            ", ".join(w["debt"]) if w["debt"] else "—"))
    return "\n".join(out) + "\n"


def t_edges():
    out = ["| 消费方 WP | 被旁路事项 | 替代物（本版如何成立） |", "|---|---|---|"]
    for e in S.EDGE_REG:
        out.append("| {} | {} | {} |".format(e["consumer"], e["bypass"], e["repl"]))
    return "\n".join(out) + "\n"


def t_cut():
    out = ["| 裁撤项 | 承接版本 | 理由 |", "|---|---|---|"]
    for c in S.CUT_REASON:
        out.append("| {} | {} | {} |".format(c["item"], c["ver"], c["why"]))
    return "\n".join(out) + "\n"


def t_assets():
    out = ["| 已落地资产 | 落点 | 对 0.0.4 的意义 |", "|---|---|---|"]
    for a, b, c in S.ASSETS:
        out.append(f"| {a} | {b} | {c} |")
    return "\n".join(out) + "\n"


def mods():
    res = []
    for mid, name, task, desc in S.MODULES:
        wl = [k for k in ORDER if BYID[k]["mod"] == mid]
        res.append(dict(id=mid, name=name, task=task, desc=desc, wps=wl,
                        loc=sum(BYID[k]["loc"] for k in wl),
                        nt=sum(NT[k] for k in wl),
                        lanes=sorted({BYID[k]["lane"] for k in wl}),
                        start=min(WP_START[k] for k in wl) if wl else 0,
                        fin=max(WP_FIN[k] for k in wl) if wl else 0))
    return res


MODS = mods()


def t_mod_acct():
    out = ["| 模块 | 名称 | 承接用户任务 | WP 数 | 净新增 LOC | 任务数 | 泳道 | 起 / 止施工日 |",
           "|---|---|---|---|---|---|---|---|"]
    for m in MODS:
        out.append("| {} | {} | {} | {} | {:,} | {} | {} | D{} / D{} |".format(
            m["id"], m["name"], m["task"], len(m["wps"]), m["loc"], m["nt"],
            ", ".join(m["lanes"]), m["start"], m["fin"]))
    return "\n".join(out) + "\n"


def t_moddoc():
    out = ["| 模块 | 名称 | docs-linux 方案锚点 | 内核侧净新增 | 模块 WLOC |",
           "|---|---|---|---|---|"]
    for m in MODS:
        out.append("| {} | {} | {} | 0 行 | {:,} |".format(
            m["id"], m["name"],
            "；".join("`{}`".format(r.replace("docs-linux/", "")) for r in S.MODULE_DOCREF[m["id"]]),
            m["loc"]))
    return "\n".join(out) + "\n"


def t_lanes():
    out = ["| 泳道 | 名称 | 说明 | 承担 WP | 任务数 | 起 / 止施工日 |", "|---|---|---|---|---|---|"]
    for lid, name, desc in S.LANES:
        wl = [k for k in ORDER if BYID[k]["lane"] == lid]
        days = [WP_START[k] for k in wl] + [WP_FIN[k] for k in wl]
        out.append("| {} | {} | {} | {} | {} | D{} / D{} |".format(
            lid, name, desc, ", ".join(wl) if wl else "—",
            sum(NT[k] for k in wl), min(days), max(days)))
    return "\n".join(out) + "\n"


def t_cp():
    out = ["| 序 | WP | 片数 | 起 / 止施工日 | 起 / 止日历日 |", "|---|---|---|---|---|"]
    for i, k in enumerate(CP, 1):
        out.append("| {} | {} | {} | D{} / D{} | {} / {} |".format(
            i, k, NT[k], WP_START[k], WP_FIN[k],
            cal(WP_START[k]), cal(WP_FIN[k])))
    return "\n".join(out) + "\n"


def t_recon():
    out = ["| 模块 | WP 数 | 净新增 LOC | 任务数 | LOC 占比 | 任务占比 | 差 |",
           "|---|---|---|---|---|---|---|"]
    for m in MODS:
        out.append("| {} | {} | {:,} | {} | {:.1f}% | {:.1f}% | 0 |".format(
            m["id"], len(m["wps"]), m["loc"], m["nt"],
            100.0 * m["loc"] / TLOC, 100.0 * m["nt"] / TTASK))
    out.append("| **合计** | **{}** | **{:,}** | **{}** | **100.0%** | **100.0%** | **0** |".format(
        len(WPS), TLOC, TTASK))
    return "\n".join(out) + "\n"


def t_adj():
    out = ["| WP | 名称 | 严格前驱 | 直接后继 | 片数 | 起 / 止施工日 |", "|---|---|---|---|---|---|"]
    for k in ORDER:
        w = BYID[k]
        out.append("| {} | {} | {} | {} | {} | D{} / D{} |".format(
            k, w["name"], ", ".join(w["deps"]) if w["deps"] else "—",
            ", ".join(SUCC[k]) if SUCC[k] else "—", NT[k], WP_START[k], WP_FIN[k]))
    return "\n".join(out) + "\n"


def role(i, n):
    if n == 1:
        return "单片：接口 + 实现 + 测试"
    if i == 1:
        return "首片：接口与类型（禁写实现）"
    if i == n:
        return "末片：单元测试与文档"
    return f"中片：实现段 {i - 1}/{n - 2}"


def art(w, i, n):
    a = w["art"]
    if n == 1:
        return f"{a}（单片）"
    if i == 1:
        return f"{a}（契约/声明段）"
    if i == n:
        return f"tests/ 与 {a}（测试与文档段）"
    return f"{a}（实现段 {i - 1}/{n - 2}）"


def t_tasks(mod):
    out = []
    for k in [x for x in ORDER if BYID[x]["mod"] == mod]:
        w = BYID[k]
        n = NT[k]
        out.append(f"#### {k} {w['name']}（{n} 个任务 / {w['loc']:,} 行 / 泳道 {w['lane']}）\n")
        out.append("| 任务 | 描述 | 产出物 | 净新增 LOC | 泳道 | 施工日 / 日历日 | 严格前驱 | 直接后继 | 状态 |")
        out.append("|---|---|---|---|---|---|---|---|---|")
        for t in [x for x in TASKS if x["wp"] == k]:
            out.append("| {} | {}（{}） | {} | {} | {} | D{} / {} | {} | {} | 待启动 |".format(
                t["id"], w["name"], role(t["idx"], n), art(w, t["idx"], n), PER_TASK,
                t["lane"], t["day"], cal(t["day"]),
                ", ".join(t["prev"]) if t["prev"] else "—",
                ", ".join(t["next"]) if t["next"] else "—"))
        out.append("")
    return "\n".join(out)


def t_sched():
    out = ["| 施工日 | 日历日 | 承担任务（泳道：任务） |", "|---|---|---|"]
    for d in range(1, NDAYS + 1):
        ts = [t for t in TASKS if t["day"] == d]
        out.append("| D{} | {} | {} |".format(
            d, cal(d), "；".join(f"{t['lane']}：{t['id']}" for t in ts)))
    return "\n".join(out) + "\n"


def t_ms():
    out = ["| 编号 | 里程碑 | WP 集合 | 达成施工日 | 日历日 | 达成判据 |", "|---|---|---|---|---|---|"]
    for mid, name, wl, gate in MILESTONES:
        fin = max(WP_FIN[k] for k in wl)
        out.append("| {} | {} | {} | D{} | {} | {} |".format(
            mid, name, ", ".join(wl), fin, cal(fin), gate))
    return "\n".join(out) + "\n"


def t_debt():
    out = ["| 债号 | 承接 WP | 完成判据（全部取证通过才可标「已验收」） |", "|---|---|---|"]
    for d in sorted(DEBT):
        owners = [w["id"] for w in WPS if d in w["debt"]]
        out.append(f"| {d} | {', '.join(owners)} | {DEBT[d]} |")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- 正文拼装

def build():
    c = dict(nloc=TLOC, nwp=len(WPS), ntask=TTASK, nmods=len(S.MODULES),
             nlanes=len(S.LANES), ndays=NDAYS, start=cal(1), end=cal(NDAYS),
             cp_n=sum(NT[k] for k in CP), cp_days=sum(DUR[k] for k in CP),
             per=PER_TASK, cap=TASK_CAP, lane_loc=LANE_LOC_PER_DAY, tpd=TASKS_PER_DAY,
             min_tasks=math.ceil(TLOC / TASK_CAP), avg_cap=TLOC / MIN_TASKS,
             base_task=TLOC // LANE_LOC_PER_DAY,
             ndebt=len({d for w in WPS for d in w["debt"]}),
             mod_rows=[(m["id"], m["name"], len(m["wps"]), m["loc"], m["nt"],
                        len({d for k in m["wps"] for d in BYID[k]["debt"]}))
                       for m in MODS])

    parts = [
        P.header(c),
        P.sec0_assess(c),
        P.sec1(c),
        P.sec2_head(),
        t_scope(),
        "\n",
        P.sec2_tail(),
        t_edges(),
        "\n### 2.3 能力裁撤登记\n\n"
        "本版只做能落地的；做不到的逐条写清「为什么不做、承接在哪一版」。"
        "**不做的理由必须比做的理由更硬。**\n\n",
        t_cut(),
        "\n",
        P.sec2_cut_tail(),
        "\n",
        P.sec2_rest(),
        "\n### 2.6 存量抵扣（0.0.3 已交付，本版不重复排程）\n\n",
        t_assets(),
        "\n",
        P.sec3(c),
        "\n",
        P.sec4_head(),
        t_mod_acct(),
        "\n",
        P.sec4_anchor(c),
        t_moddoc(),
        "\n### 4.2 并行泳道\n\n",
        t_lanes(),
        "\n",
        P.sec4_rules(c),
        "\n关键路径共 **{}** 个 WP / **{}** 个施工日 / **{}** 个任务，占全版施工日的 100%：\n\n".format(
            len(CP), c["cp_days"], c["cp_n"]),
        t_cp(),
        "\n",
        P.sec5_head(),
        t_recon(),
        "\n> 断言结果：总 LOC {:,} = Σ WP LOC；总任务 {} = Σ 片数；WP 总数 {}；三项差均为 0。"
        "生成器在写出前执行，任一不等即不落盘。\n\n".format(TLOC, TTASK, len(WPS)),
        P.sec6_head(),
        t_adj(),
        "\n### 6.1~6.8 分模块任务卡\n\n"
        "> 任务编号规则 `T<WP>-<序号>`；「状态」只有 `待启动`/`进行中`/`已验收` 三值，"
        "初始全为 `待启动`，由施工时逐条推进。\n\n",
    ]
    for i, m in enumerate(MODS, 1):
        parts.append(f"### 6.{i} {m['id']} {m['name']}（{len(m['wps'])} WP / {m['loc']:,} 行 / {m['nt']} 任务）\n\n")
        parts.append(t_tasks(m["id"]))
        parts.append("\n")

    parts += [
        "## 7. 逐日排程总表\n\n"
        "> 一个施工日可并行多泳道；每泳道每施工日承担 {} 行当量（= {} 个任务），"
        "不允许同一泳道超出该产能。"
        "每 10 个施工日后的验收日不排任务，只跑 QG 全集。\n\n".format(
            LANE_LOC_PER_DAY, TASKS_PER_DAY),
        t_sched(),
        "\n",
        P.sec8_intro(),
        t_ms(),
        "\n",
        P.sec9(c),
        "\n",
        P.sec10(),
        "\n",
        P.sec11_intro(),
        t_debt(),
        "\n",
        P.sec12(),
        "\n",
        P.sec13(c),
        "\n",
        P.sec14(c),
        "\n",
        P.sec15(),
        "\n",
        P.sec16(),
        "\n",
        P.sec17(),
        "\n",
        P.sec18(),
        "\n",
        P.sec19(),
        "\n---\n\n"
        "> **生成入口**：`python3 10-references/generators/bp_004_gen.py`。"
        "改任务请改 `bp_004_seed.py`；改口径请改 `bp_004_prose.py`；**不要手改本文件**。\n"
        ">\n"
        "> 本文件与《agentrt-linux开发路线和进度.md》的 0.0.4 施工轨互为正副本："
        "主图纸记状态与里程碑，本文件记任务与判据。\n",
    ]
    return "".join(parts)


def main():
    check()
    text = build()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"写出 {OUT}")
    print(f"LOC {TLOC:,} / WP {len(WPS)} / 任务 {TTASK} / 模块 {len(S.MODULES)} / 泳道 {len(S.LANES)}")
    print(f"施工日 {NDAYS}：{cal(1)} ~ {cal(NDAYS)}；关键路径 {sum(NT[k] for k in CP)} 任务")


if __name__ == "__main__":
    main()
