#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0
# Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
"""AirymaxOS 0.0.5 施工图纸生成器。

读 bp_005_seed.py，算出账目、模块账本、泳道、关键路径、双向邻接、任务卡与逐日排程，
写回 0.0.5-极境OS任务方案.md 的 <!--GEN:name--> ... <!--/GEN:name--> 区块。
人工只改种子与区块外的散文；区块内一律由本脚本产出。

退出码：0 = 已写入或复核一致；2 = 种子自身断言失败；3 = 区块与种子不一致（--check）。
（3 是「陈旧」而非「失败」——历史台账里 lang-lock 的 rc=3 曾被误判为失败，此处显式约定。）
"""
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bp_005_seed as S  # noqa: E402

DOC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "..", "..", "0.0.5-极境OS任务方案.md"))
AGENT_LINUX = os.path.abspath(os.path.join(os.path.dirname(DOC),
                                            "..", "..", "..", "agent-linux"))
DOCS_ROOT = os.path.abspath(os.path.join(os.path.dirname(DOC), "..", ".."))
DAY_LOC = 150          # 每泳道每施工日净新增行数
TASK_LOC = 50          # 单任务净新增行数
START = datetime.date(2027, 9, 20)   # 0.0.4 纸面收口 2027-09-17（周五）后的第一个工作日
# 窗口 2027-09-20 → 2028-02 内的法定节假日：国庆 10-01…10-07、元旦 01-01。
# 只登记「整段不排工」的日期；调休上班日不补（保守口径：宁可排长，不排短）。
HOLIDAYS = {datetime.date(2027, 10, d) for d in range(1, 8)} | {datetime.date(2028, 1, 1)}

MOD_NAME = {m[0]: m[1] for m in S.MODULES}
LANE_NAME = {l[0]: l[1] for l in S.LANES}


def die(msg):
    sys.stderr.write("SEED-INVALID: %s\n" % msg)
    sys.exit(2)


def assert_seed():
    ids = [w["id"] for w in S.WPS]
    if len(ids) != len(set(ids)):
        die("WP id 重复")
    for w in S.WPS:
        if w["loc"] % DAY_LOC:
            die("%s loc=%d 不是 %d 的整数倍" % (w["id"], w["loc"], DAY_LOC))
        if w["loc"] > 300 * 60:
            die("%s loc=%d 超过单 WP 上限" % (w["id"], w["loc"]))
        if w["mod"] not in MOD_NAME:
            die("%s 模块 %s 未登记" % (w["id"], w["mod"]))
        if w["lane"] not in LANE_NAME:
            die("%s 泳道 %s 未登记" % (w["id"], w["lane"]))
        if not S.MODULE_DOCREF.get(w["mod"]):
            die("%s 模块 %s 无 docs-linux 锚点，不得开工" % (w["id"], w["mod"]))
        for d in w["deps"]:
            if d not in ids:
                die("%s 依赖 %s 不存在" % (w["id"], d))
    for m in S.MODULE_ORDER:
        if not any(w["mod"] == m for w in S.WPS):
            die("模块 %s 无 WP" % m)
    # 无环
    seen, stack = set(), set()

    def walk(i):
        if i in stack:
            die("依赖成环：%s" % i)
        if i in seen:
            return
        stack.add(i)
        for d in {w["id"]: w["deps"] for w in S.WPS}[i]:
            walk(d)
        stack.discard(i)
        seen.add(i)
    for i in ids:
        walk(i)
    assert_gates()
    assert_docrefs()
    assert_owners()
    assert_debts()


def assert_owners():
    """§4.3「同一文件归属第一个创建它的 WP」的机器判据。

    两个 WP 的交付物出现同一文件时，必须存在依赖边（直接或传递），
    否则两者会并行改同一文件——这正是 F-22 的形状。
    """
    owner, expanded = {}, {}
    for w in S.WPS:
        files = set()
        for part in w["art"].split("、"):
            part = re.sub(r"（[^）]*）", "", part).strip()
            if not part:
                continue
            m = re.match(r"^(.*)\{([^}]*)\}(.*)$", part)
            if m:
                files |= {m.group(1) + a.strip() + m.group(3)
                          for a in m.group(2).split(",")}
            else:
                files.add(part)
        expanded[w["id"]] = files
        for f in files:
            owner.setdefault(f, []).append(w["id"])
    deps = {w["id"]: set(w["deps"]) for w in S.WPS}

    def reach(a, b, seen=None):
        if a == b:
            return True
        for d in deps[a]:
            if d not in (seen or set()):
                if reach(d, b, (seen or set()) | {d}):
                    return True
        return False

    for f, ws in owner.items():
        for i in range(len(ws)):
            for j in range(i + 1, len(ws)):
                a, b = ws[i], ws[j]
                if not reach(a, b) and not reach(b, a):
                    die("%s 被 %s 与 %s 同时主张且无依赖边" % (f, a, b))


def assert_debts():
    """§11「一条债一个承接方」的机器判据（§13.5 C7）。

    同一条债被两个 WP 承接时，两边都会以为对方在收口；
    去重后的条数还会让 §0 的 39 与账面对不上（F-60 的形状）。
    """
    owner = {}
    for w in S.WPS:
        for d in w["debt"]:
            owner.setdefault(d, []).append(w["id"])
    for d, ws in sorted(owner.items()):
        if len(ws) > 1:
            die("债 %s 被多个 WP 承接：%s" % (d, "、".join(ws)))


def assert_docrefs():
    """每个模块的 docs-linux 锚点必须在 docs/ 下真实存在（缺一即 rc=2）。

    §8 的 M0 判据②要求「锚点文件实际存在」，这条必须由脚本判，
    否则路径写错时图纸照样「通过」，而开工第一天就找不到设计依据。
    """
    for mod in S.MODULE_ORDER:
        for rel in S.MODULE_DOCREF.get(mod, []):
            if not os.path.isfile(os.path.join(DOCS_ROOT, rel)):
                die("模块 %s 的 docs-linux 锚点不存在：%s" % (mod, rel))


def assert_gates():
    """门禁脚本的三条硬约束（缺一即 rc=2）：

    1. 归属 WP 必须存在；
    2. 有归属的脚本必须出现在该 WP 的交付物列里（否则账本与门禁脱节）；
    3. 声明「既有只消费」（owner=None）的脚本必须真实存在于磁盘。
    另外：正文中出现的每个 ci/gates/*.sh 都必须在 GATES 登记（第 4 条），
    这条在文档侧执行，见 check_cited_gates()。
    """
    byid = {w["id"]: w for w in S.WPS}
    for path, owner, _ in S.GATES:
        if owner is None:
            if not os.path.isfile(os.path.join(AGENT_LINUX, path)):
                die("门禁 %s 声明为既有只消费，但磁盘上不存在" % path)
            continue
        if owner not in byid:
            die("门禁 %s 的归属 WP %s 不存在" % (path, owner))
        if path not in byid[owner]["art"]:
            die("门禁 %s 的归属 WP %s 的交付物列未登记它" % (path, owner))


def check_cited_gates(text):
    """正文（附录 A 之前的部分）引用的每个 ci/**.sh 与 ci/**.py 都必须已登记。"""
    body = text.split("## 附录 A：")[0]
    known = {g[0] for g in S.GATES}
    for m in re.finditer(r"ci/[A-Za-z0-9._/-]+\.(?:sh|py)\b", body):
        if m.group(0) not in known:
            die("正文引用了未登记的门禁脚本：%s" % m.group(0))


def schedule():
    """泳道内串行、跨泳道按依赖的最早可行日；返回 {wp: (start, end, dur)}。"""
    order = [w["id"] for w in S.WPS]
    byid = {w["id"]: w for w in S.WPS}
    lane_prev = {}
    for w in S.WPS:
        lane_prev.setdefault(w["lane"], []).append(w["id"])
    plan, lane_free = {}, {}
    pending = list(order)
    while pending:
        moved = False
        for wid in list(pending):
            w = byid[wid]
            seq = lane_prev[w["lane"]]
            i = seq.index(wid)
            if any(p in pending for p in seq[:i]):
                continue
            if any(d not in plan for d in w["deps"]):
                continue
            ready = [lane_free.get(w["lane"], 1)]
            ready += [plan[d][1] + 1 for d in w["deps"]]
            start = max(ready)
            dur = w["loc"] // DAY_LOC
            plan[wid] = (start, start + dur - 1, dur)
            lane_free[w["lane"]] = start + dur
            pending.remove(wid)
            moved = True
        if not moved:
            die("排程死锁，剩余 %s" % pending)
    return plan


def workday_to_date(d):
    """施工日序号 → 日历日：每 10 个施工日后插 1 个验收日，跳过周末与假日。"""
    slot = d + (d - 1) // 10
    cur = START
    n = 1 if (cur.weekday() < 5 and cur not in HOLIDAYS) else 0
    while n < slot:
        cur += datetime.timedelta(days=1)
        if cur.weekday() < 5 and cur not in HOLIDAYS:
            n += 1
    return cur


def critical(plan):
    byid = {w["id"]: w for w in S.WPS}
    lane_prev = {}
    for w in S.WPS:
        lane_prev.setdefault(w["lane"], []).append(w["id"])
    prev = {}
    for w in S.WPS:
        seq = lane_prev[w["lane"]]
        i = seq.index(w["id"])
        cands = list(w["deps"]) + (seq[:i][-1:] if i else [])
        if cands:
            prev[w["id"]] = max(cands, key=lambda x: plan[x][1])
    cur = max(plan, key=lambda x: plan[x][1])
    chain = []
    while cur:
        chain.append(cur)
        cur = prev.get(cur)
    return list(reversed(chain))


def task_rows():
    """每个 WP 切成 loc/50 张卡：首片接口、中片实现、末片测试与文档。"""
    out = []
    for w in S.WPS:
        n = w["loc"] // TASK_LOC
        for i in range(n):
            if n == 1:
                seg, art = "单片：实现与自测", w["art"]
            elif i == 0:
                seg, art = "首片：接口与类型（禁写实现）", w["art"] + "（契约/声明段）"
            elif i == n - 1:
                seg, art = "末片：测试与文档", w["art"] + "（用例/文档段）"
            else:
                seg, art = "中片：实现段 %d/%d" % (i, n - 2), w["art"] + "（实现段 %d/%d）" % (i, n - 2)
            out.append(dict(wp=w, no=i, tid="%s-%02d" % (w["id"], i + 1),
                            desc="%s（%s）" % (w["name"], seg), art=art))
    return out


def blocks():
    assert_seed()
    plan = schedule()
    chain = critical(plan)
    rows = task_rows()
    nodes = {w["id"] for w in S.WPS}
    succ = {i: [] for i in nodes}
    for w in S.WPS:
        for d in w["deps"]:
            succ[d].append(w["id"])
    for w in S.WPS:
        seq = [x["id"] for x in S.WPS if x["lane"] == w["lane"]]
        i = seq.index(w["id"])
        if i + 1 < len(seq):
            succ[w["id"]].append(seq[i + 1])

    total_loc = sum(w["loc"] for w in S.WPS)
    days = max(p[1] for p in plan.values())
    debts = sorted({d for w in S.WPS for d in w["debt"]})
    accept = (days - 1) // 10
    B = {}

    # ---- §0 账目
    B["ledger"] = "\n".join([
        "| 项 | 值 |", "|---|---|",
        "| 净新增代码 | **%s 行** |" % f"{total_loc:,}",
        "| 工作包（WP） | **%d 个** |" % len(S.WPS),
        "| 原子任务 | **%s 个**（每任务 %d 行，硬上限 300 行） |" % (f"{len(rows):,}", TASK_LOC),
        "| 模块 | **%d 个** |" % len(S.MODULE_ORDER),
        "| 泳道 | **%d 条**（每泳道每施工日 %d 行当量 = 3 个任务） |" % (len(S.LANES), DAY_LOC),
        "| 施工日 | **%d 个**（每 10 个施工日插 1 个验收日，周末不排） |" % days,
        "| 验收日 | **%d 个**（D10 之后起算） |" % accept,
        "| 起算 / 收口 | **%s** / **%s** |" % (START.isoformat(), workday_to_date(days).isoformat()),
        "| 关键路径 | **%d 个任务**（%d 个 WP，占施工日 %d/%d） |"
        % (sum(1 for r in rows if r["wp"]["id"] in chain), len(chain),
           plan[chain[-1]][1], days),
        "| 遗留债 | **%d 条**（§11 逐条闭合，承接 WP 双向可核） |" % len(debts),
    ])

    # ---- §0.1 总量评估
    lines = ["| 模块 | 名称 | WP | 净新增 LOC | 占比 | 任务数 | 承接债 | 首个施工日 |",
             "|---|---|---|---|---|---|---|---|"]
    for m in S.MODULE_ORDER:
        ws = [w for w in S.WPS if w["mod"] == m]
        loc = sum(w["loc"] for w in ws)
        ds = sorted({d for w in ws for d in w["debt"]})
        first = min(plan[w["id"]][0] for w in ws)
        lines.append("| %s | %s | %d | %s | %.1f%% | %d | %d | D%d |"
                     % (m, MOD_NAME[m], len(ws), f"{loc:,}", 100.0 * loc / total_loc,
                        loc // TASK_LOC, len(ds), first))
    lines.append("| **合计** | — | **%d** | **%s** | **100.0%%** | **%s** | **%d** | — |"
                 % (len(S.WPS), f"{total_loc:,}", f"{len(rows):,}", len(debts)))
    B["assessment"] = "\n".join(lines)

    # ---- §4.1 模块账本
    lines = ["| 模块 | WP 数 | 净新增 LOC | 任务数 | 承接债 | docs-linux 锚点 |",
             "|---|---|---|---|---|---|"]
    for m in S.MODULE_ORDER:
        ws = [w for w in S.WPS if w["mod"] == m]
        loc = sum(w["loc"] for w in ws)
        ds = sorted({d for w in ws for d in w["debt"]})
        lines.append("| %s %s | %d | %s | %d | %d | %s |"
                     % (m, MOD_NAME[m], len(ws), f"{loc:,}", loc // TASK_LOC, len(ds),
                        "<br>".join("`%s`" % p for p in S.MODULE_DOCREF[m])))
    B["modledger"] = "\n".join(lines)

    # ---- §4.2 泳道表
    lines = ["| 泳道 | 名称 | 负责 WP | 行数 | 泳道日 | 起止 |", "|---|---|---|---|---|---|"]
    for l in S.LANES:
        ws = [w for w in S.WPS if w["lane"] == l[0]]
        loc = sum(w["loc"] for w in ws)
        s = min(plan[w["id"]][0] for w in ws)
        e = max(plan[w["id"]][1] for w in ws)
        lines.append("| %s | %s | %s | %s | %d | D%d–D%d |"
                     % (l[0], l[1], "、".join(w["id"] for w in ws), f"{loc:,}", loc // DAY_LOC, s, e))
    B["lanes"] = "\n".join(lines)

    # ---- §4.4 关键路径
    lines = ["| # | WP | 名称 | 泳道 | 起 | 止 | 任务数 |", "|---|---|---|---|---|---|---|"]
    for i, wid in enumerate(chain, 1):
        w = next(x for x in S.WPS if x["id"] == wid)
        s, e, _ = plan[wid]
        lines.append("| %d | %s | %s | %s | D%d | D%d | %d |"
                     % (i, wid, w["name"], w["lane"], s, e, w["loc"] // TASK_LOC))
    B["critical"] = "\n".join(lines)

    # ---- §5.1 对账
    lines = ["| 模块 | §0.1 LOC | §4.1 LOC | 差 | §0.1 任务 | §6 任务卡行 | 差 |",
             "|---|---|---|---|---|---|---|"]
    for m in S.MODULE_ORDER:
        ws = [w for w in S.WPS if w["mod"] == m]
        loc = sum(w["loc"] for w in ws)
        n = sum(1 for r in rows if r["wp"]["mod"] == m)
        lines.append("| %s | %s | %s | 0 | %d | %d | 0 |"
                     % (m, f"{loc:,}", f"{loc:,}", loc // TASK_LOC, n))
    lines.append("| **合计** | **%s** | **%s** | **0** | **%s** | **%s** | **0** |"
                 % (f"{total_loc:,}", f"{total_loc:,}", f"{len(rows):,}", f"{len(rows):,}"))
    B["recon"] = "\n".join(lines)

    # ---- §6.0 双向邻接
    lines = ["| WP | 模块 | 严格前驱 | 直接后继 | 推进状态（证据） |", "|---|---|---|---|---|"]
    for w in S.WPS:
        lines.append("| %s | %s | %s | %s | 未开工 |"
                     % (w["id"], w["mod"],
                        "、".join(w["deps"]) or "—",
                        "、".join(sorted(set(succ[w["id"]]))) or "—"))
    B["adj"] = "\n".join(lines)

    # ---- §6.1–6.8 任务卡
    cards, idx = [], 1
    for m in S.MODULE_ORDER:
        ws = [w for w in S.WPS if w["mod"] == m]
        loc = sum(w["loc"] for w in ws)
        cards.append("### 6.%d %s %s（%d WP / %s 行 / %d 任务）\n"
                     % (idx, m, MOD_NAME[m], len(ws), f"{loc:,}", loc // TASK_LOC))
        cards.append("| 任务 | 描述 | 产出物 | 净新增 LOC | 泳道 | 施工日 | 严格前驱 | 直接后继 | 状态 |")
        cards.append("|---|---|---|---|---|---|---|---|---|")
        for r in rows:
            w = r["wp"]
            if w["mod"] != m:
                continue
            s, e, _ = plan[w["id"]]
            if r["no"] == w["loc"] // TASK_LOC - 1:
                nxt = ("、".join(sorted(set(succ[w["id"]]))) or "—")
            else:
                nxt = "%s-%02d" % (w["id"], r["no"] + 2)
            cards.append("| %s | %s | %s | %d | %s | D%d / %s | %s | %s | 未开工 |"
                         % (r["tid"], r["desc"], r["art"], TASK_LOC, w["lane"], s,
                            workday_to_date(s).isoformat(),
                            "—" if r["no"] == 0 else "%s-%02d" % (w["id"], r["no"]), nxt))
        cards.append("")
        idx += 1
    B["cards"] = "\n".join(cards).rstrip()

    # ---- §9.1 门禁脚本登记（存在性由磁盘实测，归属由种子声明）
    lines = ["| 脚本 | 归属 WP | 现状（磁盘实测） | 判据要点 |", "|---|---|---|---|"]
    n_exist = n_new = n_consume = 0
    for path, owner, why in S.GATES:
        exists = os.path.isfile(os.path.join(AGENT_LINUX, path))
        if owner is None:
            state = "已存在·只消费"
            n_consume += 1
        elif exists:
            state = "已存在·本版扩展"
            n_exist += 1
        else:
            state = "**本版新建**"
            n_new += 1
        lines.append("| `%s` | %s | %s | %s |"
                     % (path, owner or "—（0.0.4 既有）", state, why))
    lines.append("| **合计** | %d 个有归属 / %d 个只消费 | **已存在 %d 个·本版新建 %d 个** | — |"
                 % (len(S.GATES) - n_consume, n_consume, n_exist + n_consume, n_new))
    B["gates"] = "\n".join(lines)

    # ---- §7 逐日排程（当日产能 = 150 行 × 在办 WP 数，累计必须回到总 LOC）
    lines = ["| 施工日 | 日历日 | 在办 WP（每包 150 行/日） | 当日行数 | 累计行数 | 备注 |",
             "|---|---|---|---|---|---|"]
    acc = 0
    for d in range(1, days + 1):
        on = [w for w in S.WPS if plan[w["id"]][0] <= d <= plan[w["id"]][1]]
        loc = DAY_LOC * len(on)
        acc += loc
        notes = []
        if d % 10 == 0:
            notes.append("D%d 后接验收日" % d)
        done = [wid for wid in chain if plan[wid][1] == d]
        if done:
            notes.append("关键路径 %s 完成" % "、".join(done))
        lines.append("| D%d | %s | %s | %s | %s | %s |"
                     % (d, workday_to_date(d).isoformat(),
                        "、".join(w["id"] for w in on) or "—",
                        f"{loc:,}", f"{acc:,}", "；".join(notes)))
    if acc != total_loc:
        die("排程累计 %d 行 ≠ 总 LOC %d" % (acc, total_loc))
    B["schedule"] = "\n".join(lines)

    # ---- §8 里程碑：M1 取「用户态六模块全部结束」，M1.5 取内核两条结束，M2 = 收口日
    def last_day(mods):
        return max(plan[w["id"]][1] for w in S.WPS if w["mod"] in mods)
    m1 = last_day({"U", "N", "A", "S", "R", "Q"})
    m15 = last_day({"K"})
    m2 = days
    v_done = sum(1 for w in S.WPS if w["mod"] == "V" and plan[w["id"]][1] <= m1)
    v_all = sum(1 for w in S.WPS if w["mod"] == "V")
    B["milestones"] = "\n".join([
        "| 里程碑 | 施工日 | 日历日 | 判据 |", "|---|---|---|---|",
        "| M0 开工 | D1 | %s | 无「非末位 WP 后继为空」；三个入口 WP（R-01／K-01／Q-01）前驱为空属设计；8 模块锚点实测存在；`bp_005_gen.py --check` 为 0 |"
        % workday_to_date(1).isoformat(),
        "| M1 用户态全量落地可内测 | D%d | %s | U/N/A/S/R/Q 六个模块全部收口；V 模块 %d/%d 通过 |"
        % (m1, workday_to_date(m1).isoformat(), v_done, v_all),
        "| M1.5 内核两条实机转绿 | D%d | %s | K-01：`instances/agent_trace/events/airy` 四阶段事件 `entries-written > 0` 且逐事件 ≥1，`cap_used` 可逆，`policy` 可写而 `agentrt` 只读；K-02：未授权 W→X 返回 `EACCES`、白名单放行 |"
        % (m15, workday_to_date(m15).isoformat()),
        "| M2 全绿发版 | D%d | %s | §15 的 AC-A、AC-S、AC-B、AC-V 四组判据全部 PASS |"
        % (m2, workday_to_date(m2).isoformat()),
    ])

    # ---- §11 债号索引
    lines = ["| 债号 | 承接 WP | 债号 | 承接 WP |", "|---|---|---|---|"]
    owner = {d: [w["id"] for w in S.WPS if d in w["debt"]] for d in debts}
    half = (len(debts) + 1) // 2
    for i in range(half):
        a = debts[i]
        b = debts[i + half] if i + half < len(debts) else None
        lines.append("| %s | %s | %s | %s |"
                     % (a, "、".join(owner[a]), b or "—",
                        "、".join(owner[b]) if b else "—"))
    B["debtindex"] = "\n".join(lines)
    return B


def render(path, bl):
    text = open(path, encoding="utf-8").read()
    for name, body in bl.items():
        pat = re.compile(r"(<!--GEN:%s-->)(.*?)(<!--/GEN:%s-->)" % (name, name), re.S)
        if not pat.search(text):
            die("文档缺少区块标记 GEN:%s" % name)
        # 区块可能为空（两行紧邻），故不假设开闭标记之间已有换行，统一补齐。
        text = pat.sub(lambda m: m.group(1) + "\n" + body + "\n" + m.group(3), text, count=1)
    return text


def main():
    bl = blocks()
    old = open(DOC, encoding="utf-8").read()
    check_cited_gates(old)
    new = render(DOC, bl)
    if "--check" in sys.argv:
        if old != new:
            sys.stderr.write("STALE: 文档区块与种子不一致，请运行 bp_005_gen.py 重新生成\n")
            sys.exit(3)
        print("OK: 0.0.5 区块与种子一致（%d 行账目，%d 个任务卡）" % (len(bl), len(task_rows())))
        return
    if old != new:
        open(DOC, "w", encoding="utf-8").write(new)
        print("WRITE: 已刷新 %d 个区块" % len(bl))
    else:
        print("OK: 无变化")


if __name__ == "__main__":
    main()
