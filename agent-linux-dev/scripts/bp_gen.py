# -*- coding: utf-8 -*-
"""施工图纸生成器：读种子 -> 缩放对账 -> 拆 100-200 行任务 -> 拓扑排程 -> 输出 Markdown。"""
import datetime, sys, importlib.util, os, re as _re
from collections import defaultdict
sys.setrecursionlimit(300000)

_here = os.path.dirname(os.path.abspath(globals().get("__file__", "/tmp/bp_gen.py")))
_seed_path = os.path.join(_here, "bp_seed.py")
if not os.path.exists(_seed_path): _seed_path = "/tmp/bp_seed.py"
spec = importlib.util.spec_from_file_location("bp_seed", _seed_path)
seed = importlib.util.module_from_spec(spec); spec.loader.exec_module(seed)

TARGETS, MODULE_NAMES, LANE_DESC = seed.TARGETS, seed.MODULE_NAMES, seed.LANE_DESC
GATES, WPS, MILESTONES = seed.GATES, seed.WPS, seed.MILESTONES
SUPP = getattr(seed, "SUPP", {})  # v3.2：补充 WP -> 方案文档证据（docs-linux 路径:行号）
MOD_ORDER = list(WPS.keys())

# ---------- 1. 收集 WP ----------
class WP:
    __slots__ = ("id","mod","name","seed_loc","loc","lane","deps","is_gate","tasks")
    def __init__(s,i,m,n,l,ln,d,g):
        s.id,s.mod,s.name,s.seed_loc,s.lane,s.deps,s.is_gate=i,m,n,l,ln,d,g; s.loc=0; s.tasks=[]
wps={}
for m in MOD_ORDER:
    for (i,n,l,ln,d) in WPS[m]:
        assert i not in wps, f"dup {i}"
        w=WP(i,m,n,l,ln,d,False); wps[i]=w
for (i,n,ln,d) in GATES:
    w=WP(i,"GATE",n,0,ln,d,True); wps[i]=w
gate_ids={g[0] for g in GATES}

for i,w in wps.items():
    for d in w.deps:
        assert d in wps, f"{i} 依赖不存在: {d}"

# ---------- 1.5 示例代码语言路由（v3.4：发行版/运维工件不再误套 C 模板） ----------
def _art_lang(w):
    """按 WP 语义选择示例代码语言：M 泳道发行版工件分流 spec/xml/ini/sh；Q 泳道 CLI → Python。"""
    if w.mod == "L":
        return "python"
    if w.mod in ("R1", "R2"):
        return "cpp"
    if w.mod == "M":
        nm = w.name.lower()
        if "spec" in nm: return "spec"
        if "comps" in nm or "xml" in nm: return "xml"
        if "systemd" in nm or "journald" in nm or "自检服务" in nm: return "ini"
        if "dnf" in nm or "插件" in nm: return "python"
        return "sh"
    if w.mod == "Q" and "cli" in w.name.lower():
        return "python"
    return "c"

# 产出物描述（与 _art_lang 联动）：(整包, 接口片, 末片测试, 实现段)
_ART = {
 "c":      ("单文件完整实现 + 内联 KUnit + 契约快照",
            "头文件：类型/原型/常量 + 契约快照（不含实现）",
            "KUnit/kselftest 用例 + 文档 + DoD 四项收口",
            ".c 实现源文件（本段逻辑 + 错误路径）"),
 "python": ("单文件完整实现 + 内联 pytest + 契约快照",
            ".py 模块：类型/函数签名 + docstring（不含实现）",
            "pytest 用例 + 文档 + DoD 四项收口",
            ".py 实现源文件（本段逻辑 + 错误路径）"),
 "cpp":    ("单文件完整实现 + 内联 QtTest + 契约快照",
            ".h 头文件：类型/原型/常量（不含实现）",
            "QtTest 用例 + 文档 + DoD 四项收口",
            ".cpp 实现源文件（本段逻辑 + 错误路径）"),
 "spec":   ("完整 RPM spec + rpmspec/rpmlint 校验收口",
            "spec 元数据段：Name/License/BuildRequires（禁写构建段）",
            "spec %check + %changelog + rpmlint 校验",
            "spec 构建/安装段（本段指令，衔接前片）"),
 "sh":     ("完整脚本 + shellcheck 绿 + 内联自测",
            "脚本骨架：set -euo + 函数签名（不含实现）",
            "shell 自测用例 + shellcheck 校验 + DoD 收口",
            "脚本函数实现段（本段逻辑 + 错误处理，source 前片）"),
 "ini":    ("完整 systemd unit + systemd-analyze verify",
            "unit [Unit] 元数据段（禁写 [Service] 实现）",
            "unit [Install] + systemd-analyze verify 用例",
            "unit [Service] 实现段：ExecStart/沙箱/切片指令"),
 "xml":    ("完整 XML 文档 + xmllint 校验收口",
            "XML 骨架：声明/根元素/DTD 引用（不含条目）",
            "XML 闭合 + xmllint --valid 校验用例",
            "XML 条目段（本批 group/package 定义，续接前片）"),
}

# ---------- 2. 逐模块缩放到目标 LOC（最大余数法） ----------
for m in MOD_ORDER:
    group=[w for w in wps.values() if w.mod==m]
    s=sum(w.seed_loc for w in group); t=TARGETS[m]
    assert s>0
    scaled=[(w, w.seed_loc*t/s) for w in group]
    ints=[int(v) for _,v in scaled]
    rem = t-sum(ints)
    order=sorted(range(len(scaled)), key=lambda k: scaled[k][1]-ints[k], reverse=True)
    for k in order[:rem]: ints[k]+=1
    # 取整到 10 行粒度并修正总差（每步 ±10）
    diff=t-sum(ints)
    step=10 if diff>0 else -10
    i=0
    while diff!=0:
        j=order[i%len(order)]
        if (step>0) or ints[j]>=110+10: ints[j]+=step; diff-=step
        i+=1
    for w,v in zip(group,ints): w.loc=v
    assert sum(w.loc for w in group)==t,(m,sum(w.loc for w in group),t)

# ---------- 3. 拆分为 100~200 行任务（目标粒度 128 行/任务 ⇒ 全账本约 3,300 个原子任务） ----------
def split(loc):
    if loc==0: return [0]
    n=max(1,round(loc/128))
    while loc/n>200: n+=1
    while n>1 and loc/n<100: n-=1
    base,r=divmod(loc,n)
    return [base+1]*r+[base]*(n-r)

tasks={}  # id -> dict
class T:
    __slots__=("id","wp","idx","name","loc","dur","art")
tcount=0
for i,w in sorted(wps.items(), key=lambda kv:(MOD_ORDER.index(kv[1].mod) if kv[1].mod in MOD_ORDER else 99, kv[0])):
    locs=split(w.loc)
    n=len(locs)
    for k,lv in enumerate(locs):
        if w.is_gate:
            name=f"设计门禁：{w.name}"; dur=5
            art="详设文档 + 评审记录（docs，不计 LOC）"
        else:
            at=_ART[_art_lang(w)]
            if n==1:
                name=f"{w.name}（整包：接口+实现+测试）"
                art=at[0]
            elif k==0:
                name=f"{w.name}：接口与类型（1/{n}）"
                art=at[1]
            elif k==n-1:
                name=f"{w.name}：单元测试与文档（{n}/{n}）"
                art=at[2]
            else:
                name=f"{w.name}：实现段（{k+1}/{n}，主逻辑与错误路径）"
                art=at[3]
            dur=1
        t=T(); t.id=f"T{i}-{k+1:02d}"; t.wp=i; t.idx=k; t.name=name; t.loc=lv; t.dur=dur; t.art=art
        w.tasks.append(t.id); tasks[t.id]=t
    if not w.is_gate:
        for t in w.tasks:
            assert 100<=tasks[t].loc<=200, f"{t} loc={tasks[t].loc}"

# ---------- 4. 泳道序列（gate 插入到其同泳道直接后继之前） ----------
lanes=defaultdict(list)
for m in MOD_ORDER:
    for (i,_,_,ln,_) in WPS[m]: lanes[ln].append(i)
for (gi,_,gln,_) in GATES:
    succs=[x for x in lanes[gln] if gi in wps[x].deps]
    pos=min([lanes[gln].index(x) for x in succs]) if succs else len(lanes[gln])
    lanes[gln].insert(pos,gi)

preds=defaultdict(list)
succs=defaultdict(list)
def add_edge(a,b):  # a 是 b 的前驱
    if a not in preds[b]:
        preds[b].append(a)
        succs[a].append(b)
for ln,seq in lanes.items():
    for a,b in zip(seq,seq[1:]): add_edge(wps[a].tasks[-1], wps[b].tasks[0])
for i,w in wps.items():
    for d in w.deps:
        add_edge(wps[d].tasks[-1], w.tasks[0])
# WP 内分片串行链
for i,w in wps.items():
    for a,b in zip(w.tasks,w.tasks[1:]): add_edge(a,b)

# 双向一致性审计：前驱边与后继边必须互为逆
for a in tasks:
    for b in preds[a]:
        assert a in succs[b], (b,a)
for a in tasks:
    for b in succs[a]:
        assert a in preds[b], (a,b)

# WP 级逻辑被依赖（后继 WP）
wp_succ={i:sorted(x for x in wps if i in wps[x].deps) for i in wps}

# ---------- 5. 拓扑排程（最长路径 + 环检测） ----------
day={}
state={}
def dfs(v):
    st=state.get(v,0)
    if st==2: return day[v]
    if st==1: raise RuntimeError(f"依赖环涉及 {v}")
    state[v]=1
    d=1
    for p in preds[v]:
        d=max(d, dfs(p)+tasks[p].dur)
    day[v]=d; state[v]=2; return d
for v in tasks: dfs(v)
finish={v:day[v]+tasks[v].dur-1 for v in tasks}
maxraw=max(finish.values())

START=datetime.date(2026,10,5)
def cal_of(r): return r+(r-1)//10
def date_of(c):
    return START+datetime.timedelta(days=(c-1)+2*((c-1)//5))
# 校验 START 为周一、date_of 仅工作日
assert START.weekday()==0
for c in (1,5,6,10,11):
    assert date_of(c).weekday()<5,(c,date_of(c))

# ---------- 6. 校验 ----------
tot_loc=sum(t.loc for t in tasks.values())
assert tot_loc==sum(TARGETS.values()),tot_loc
for m in MOD_ORDER:
    s=sum(tasks[t].loc for w in wps.values() if w.mod==m for t in w.tasks)
    assert s==TARGETS[m],(m,s)
ntask=len(tasks); ngate=sum(1 for w in wps.values() if w.is_gate)
SUPP_LOC=sum(wps[w].loc for w in SUPP)          # 全部补充 WP（v3.2 62 + v3.4 39）缩放后实摊行数
SUPP_DECLARE=sum(wps[w].seed_loc for w in SUPP) # 补充 WP 台账申报总行数（实算，= V32+V34）
V32_DECLARE=sum(wps[w].seed_loc for w in list(SUPP)[:62])   # v3.2 轮补录 62 条申报实算
V34_DECLARE=SUPP_DECLARE-V32_DECLARE                        # v3.4 轮补录 39 条申报实算
BASE_LOC=sum(TARGETS.values())-SUPP_LOC         # v3.1 基线存续 258 WP 实摊行数（260 删 I-14/L-02）

# ---------- 7. 关键路径 ----------
last=max(tasks,key=lambda v:finish[v])
cp=[]; v=last
while True:
    cp.append(v)
    if not preds[v]: break
    v=max(preds[v],key=lambda p:finish[p])
cp.reverse()

# ---------- 8. 里程碑 ----------
ms_rows=[]
for (mid,mname,anchors) in MILESTONES:
    d=max(finish[t] for a in anchors for t in wps[a].tasks)
    ms_rows.append((mid,mname,", ".join(anchors),date_of(cal_of(d)),d))

# ---------- 9. 模块顺序 ----------
mod_stat=[]
for m in MOD_ORDER:
    ws=[w for w in wps.values() if w.mod==m]
    ts=[t for w in ws for t in w.tasks]
    st=min(day[t] for t in ts); en=max(day[t]+tasks[t].dur-1 for t in ts)
    depmods=set()
    for w in ws:
        for d in w.deps:
            dm=wps[d].mod
            if dm!=m: depmods.add(dm)
    mod_stat.append((m,len(ws),len(ts),sum(tasks[t].loc for t in ts),sorted({w.lane for w in ws}),st,en,sorted(depmods)))
mod_stat_sorted=sorted(mod_stat,key=lambda r:r[5])

# ---------- 10. 逐日排程 ----------
by_raw=defaultdict(list)
for v,t in tasks.items(): by_raw[day[v]].append(v)
daily=[]
c=1; r=1
maxcal=cal_of(maxraw+1)
day_tasks={}
for rr in range(1,maxraw+1): day_tasks.setdefault(cal_of(rr),[]).extend(sorted(by_raw.get(rr,[])))
allcals=sorted(day_tasks)
prev=None; rows=[]
for cc in allcals:
    if prev is not None and cc>prev+1:
        for gap in range(prev+1,cc): rows.append((gap,date_of(gap),"—","验收日（回归/门禁检查，无开发任务）"))
    ids=day_tasks[cc]
    rows.append((cc,date_of(cc),str(len(ids)),", ".join(ids)))
    prev=cc

# ---------- 10.5 任务示例代码生成（v3.3，遵循 50-engineering-standards） ----------
# 规则锚点：OS-STD-CODE-001（描述性命名）/012（kernel-doc）/016（include 顺序）/
# 017（头文件保护）/022（goto 集中出口）/030（动作函数 0/-Exxx、谓词 bool）/032（u32 类型）、
# OS-BAN-004（strscpy）；SPDX 双轨见 12-license-policy（内核 GPL-2.0-only / 用户态双许可）。
_STOP = {"and","the","for","with","from","into","using","this","that","http","https","doc","docs"}
def _slug(w):
    toks=[t for t in _re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", w.name) if t.lower() not in _STOP]
    if toks:
        base=max(toks,key=len).lower()
        if base.startswith("airy_"): base=base[5:]
    else:
        base="mod"
    base=_re.sub(r"[^a-z0-9_]","_",base)[:14].strip("_") or "mod"
    return w.id.replace("-","").lower()+"_"+base
wslug={i:_slug(w) for i,w in wps.items()}
_KLANE=("K","SEC","SUP","OBS","MEM","COG","DRV","QA")
def _kern(w): return any(w.lane.startswith(p) for p in _KLANE)
def _cls(sid): return "".join(p[:1].upper()+p[1:] for p in sid.split("_"))

def _kdoc(name, summary, params=(), ret=None):
    """生成 kernel-doc 注释块（OS-STD-CODE-012）：公共 API 必配。"""
    out=["/**", f" * {name} - {summary}"]
    for p,d in params:
        out.append(f" * @{p}: {d}")
    if ret:
        out+=[" *", f" * Return: {ret}"]
    out.append(" */")
    return out

def _strip_comments(txt, lang):
    """剥离注释后再做能力探测，避免把文档里的 -EINVAL 误判为代码依赖（OS-STD-CODE-015）。"""
    if lang in ("c","cpp"):
        txt=_re.sub(r"/\*.*?\*/"," ",txt,flags=_re.S)
        txt=_re.sub(r"//[^\n]*"," ",txt)
    else:
        txt=_re.sub(r'""".*?"""'," ",txt,flags=_re.S)
        txt=_re.sub(r"#[^\n]*"," ",txt)
    return txt

def _need_incs(txt, lang):
    """按示例代码实际使用的能力，推导需显式 include 的直接依赖头（OS-STD-CODE-015）。"""
    txt=_strip_comments(txt, lang)
    need=[]
    if lang=="c":
        if _re.search(r"\bktime_[a-z0-9_]*\s*\(", txt): need.append("linux/ktime.h")
        if _re.search(r"\bpr_(?:err|info|warn|debug|notice|alert|crit|emerg)\s*\(", txt): need.append("linux/printk.h")
        if _re.search(r"-E[A-Z][A-Z0-9_]{2,}\b", txt): need.append("linux/errno.h")
        if _re.search(r"\b(?:u8|u16|u32|u64|s8|s16|s32|s64|__u32|__u64)\b", txt): need.append("linux/types.h")
        if _re.search(r"\b(?:KUNIT_|kunit_)", txt): need.append("kunit/test.h")
        if "MODULE_LICENSE" in txt: need.append("linux/module.h")
    elif lang=="cpp":
        if _re.search(r"\b(?:QVERIFY|QCOMPARE|QTEST_MAIN|Q_OBJECT|QTest)\b", txt): need.append("QtTest")
        if _re.search(r"\bquint64\b", txt): need.append("QtGlobal")
        if _re.search(r"-E[A-Z][A-Z0-9_]{2,}\b", txt): need.append("cerrno")
    return need

def _inject_sys_incs(body, need):
    """把缺失的系统头插到首个 #include 之前（系统头先于本地头，OS-STD-CODE-016）。"""
    if not need: return body
    txt="\n".join(body); add=[]
    for h in need:
        if (f"<{h}>" in txt) or (f'"{h}"' in txt) or (h in add): continue
        add.append(h)
    if not add: return body
    idx=len(body)
    for i,ln in enumerate(body):
        if ln.lstrip().startswith("#include"):
            idx=i; break
    return body[:idx]+[f"#include <{h}>" for h in add]+body[idx:]

def code_lines(tid):
    t=tasks[tid]; w=wps[t.wp]; sid=wslug[t.wp]; SU=sid.upper(); CL=_cls(sid)
    n=len(w.tasks); k=t.idx; kk=k+1
    hd=[f"**{tid}｜{t.name}**",""]
    if w.is_gate:
        return hd+["> 设计门禁任务：产出详设文档 + 评审记录（docs，不计 LOC），无代码示例。",""]
    lic="GPL-2.0-only" if _kern(w) else "AGPL-3.0-or-later OR Apache-2.0"
    lang=_art_lang(w)
    dep=w.deps[0] if w.deps else None
    prev=w.tasks[k-1] if k>0 else None
    first=w.tasks[0]
    # 测试片调用「末段实现」以真正贯通整条调用链（n<4 时链上仅 init）
    entry=f"airy_{sid}_impl_{n-1}" if n>=4 else f"airy_{sid}_init"
    entry_mod=f"{sid}_impl_{n-1}" if n>=4 else f"{sid}_impl_2"
    if lang=="c":
        enm=[f"enum airy_{sid}_state {{",
f"\tAIRY_{SU}_IDLE    = 0,",
f"\tAIRY_{SU}_RUNNING = 1,",
"};"]
        if n==1:
            body=[f"/* SPDX-License-Identifier: {lic} */",
f"/* 整包任务：接口 + 实现 + 内联 KUnit（{w.name}） */",
"#include <kunit/test.h>",
"#include <linux/types.h>",
"",
"/**",
f" * enum airy_{sid}_state - {w.name} 状态机取值",
" */"]+enm+[
"",
"/**",
f" * struct airy_{sid}_ctx - {w.name} 上下文",
f" * @state: 状态机取值，见 enum airy_{sid}_state",
" * @stamp_ns: CLOCK_MONOTONIC 纳秒戳",
" */",
f"struct airy_{sid}_ctx {{",
"\tu32 state;",
"\tu64 stamp_ns;",
"};",
"",
"/**",
f" * airy_{sid}_init - 初始化 {w.name} 上下文",
" * @ctx: 待初始化上下文（输出参数）",
" * Return: 0 成功，-EINVAL 参数非法（OS-STD-CODE-030）",
" */",
f"int airy_{sid}_init(struct airy_{sid}_ctx *ctx)",
"{",
"\tif (!ctx)",
"\t\treturn -EINVAL;",
f"\tctx->state = AIRY_{SU}_RUNNING;",
"\tctx->stamp_ns = ktime_get_ns();",
"\treturn 0;",
"}",
"",
f"static void airy_{sid}_test_init(struct kunit *test)",
"{",
f"\tstruct airy_{sid}_ctx ctx = {{}};",
"",
f"\tKUNIT_EXPECT_EQ(test, airy_{sid}_init(&ctx), 0);",
f"\tKUNIT_EXPECT_EQ(test, ctx.state, AIRY_{SU}_RUNNING);",
"}",
"",
f"static struct kunit_case airy_{sid}_cases[] = {{",
f"\tKUNIT_CASE(airy_{sid}_test_init),",
"\t{}",
"};",
"",
f"static struct kunit_suite airy_{sid}_suite = {{",
f'\t.name = "airy_{sid}",',
f"\t.test_cases = airy_{sid}_cases,",
"};",
f"kunit_test_suite(airy_{sid}_suite);",
"",
'MODULE_LICENSE("GPL");']
        elif k==0:
            depinc=[f'#include "linux/airymax/{wslug[dep]}.h"  /* 前驱 WP {dep}：接口衔接 */'] if dep else []
            protos=[]
            for kk in range(3,n):  # 实现链 impl_3..impl_{n-1} 跨分片调用，须在接口头声明
                protos+=_kdoc(f"airy_{sid}_impl_{kk}",f"{w.name} 主逻辑链第 {kk-1} 段（分片 {w.tasks[kk-1]}）",
                              [("ctx","本 WP 上下文，见 struct airy_"+sid+"_ctx")],
                              "0 成功；-EINVAL 参数非法；-EAGAIN 上游失败（OS-STD-CODE-030）")
                protos+=[f"int airy_{sid}_impl_{kk}(struct airy_{sid}_ctx *ctx);",""]
            body=[f"/* SPDX-License-Identifier: {lic} */",
f"#ifndef _AIRY_{SU}_H",
f"#define _AIRY_{SU}_H",
"",
"#include <linux/types.h>"]+depinc+[
"",
"/**",
f" * enum airy_{sid}_state - {w.name} 状态机取值",
" */"]+enm+[
"",
"/**",
f" * struct airy_{sid}_ctx - {w.name} 上下文（本任务仅定义类型与原型，禁写实现）",
f" * @state: 状态机取值（见 enum airy_{sid}_state）",
f" * @stamp_ns: CLOCK_MONOTONIC 纳秒戳",
" */",
f"struct airy_{sid}_ctx {{",
"\tu32 state;",
"\tu64 stamp_ns;",
"};",
""]+_kdoc(f"airy_{sid}_init",f"初始化 {w.name} 上下文（实现在分片 {w.tasks[1] if n>1 else '—'}）",
         [("ctx","待初始化上下文（输出参数）")],
         "0 成功；-EINVAL 参数非法（OS-STD-CODE-030）")+[
f"int airy_{sid}_init(struct airy_{sid}_ctx *ctx);",
""]+protos+_kdoc(f"airy_{sid}_ready","判定上下文是否处于 RUNNING（谓词式，返回 bool）",
         [("ctx","待判定上下文（只读）")],
         "true 处于 RUNNING；false 其它状态（OS-STD-CODE-030）")+[
f"static inline bool airy_{sid}_ready(const struct airy_{sid}_ctx *ctx)",
"{",
f"\treturn ctx->state == AIRY_{SU}_RUNNING;",
"}",
"",
f"#endif /* _AIRY_{SU}_H */"]
        elif k==n-1:
            pre=[] if n>2 else _kdoc(f"airy_{sid}_init",f"初始化 {w.name} 上下文（实现接口片 {first} 的声明）",
[("ctx","待初始化上下文（输出参数）")],
"0 成功；-EINVAL 参数非法（OS-STD-CODE-030）")+[
f"int airy_{sid}_init(struct airy_{sid}_ctx *ctx)","{",
"\tif (!ctx)",
"\t\treturn -EINVAL;",f"\tctx->state = AIRY_{SU}_RUNNING;","\treturn 0;","}",""]
            body=[f"// SPDX-License-Identifier: {lic}",
f"// KUnit：覆盖 {first}..{prev} 的 airy_{sid}_* 全链（衔接前片符号）",
"#include <kunit/test.h>",
f'#include "{sid}.h"',
""]+pre+[
f"static void airy_{sid}_test_basic(struct kunit *test)",
"{",
f"\tstruct airy_{sid}_ctx ctx = {{}};",
"",
f"\tKUNIT_EXPECT_EQ(test, {entry}(&ctx), 0);",
f"\tKUNIT_EXPECT_TRUE(test, airy_{sid}_ready(&ctx));",
"}",
"",
f"static struct kunit_case airy_{sid}_cases[] = {{",
f"\tKUNIT_CASE(airy_{sid}_test_basic),",
"\t{}",
"};",
"",
f"static struct kunit_suite airy_{sid}_suite = {{",
f'\t.name = "airy_{sid}",',
f"\t.test_cases = airy_{sid}_cases,",
"};",
f"kunit_test_suite(airy_{sid}_suite);",
"",
'MODULE_LICENSE("GPL");']
        else:
            if kk==2:
                note=f"// 实现段 {kk}/{n}：定义接口片（{prev}）声明的 airy_{sid}_init"
                body=[f"// SPDX-License-Identifier: {lic}",note,f'#include "{sid}.h"',""]+_kdoc(
f"airy_{sid}_init",f"初始化 {w.name} 上下文（定义接口片 {prev} 的声明）",
[("ctx","待初始化上下文（输出参数）")],
"0 成功；-EINVAL 参数非法（OS-STD-CODE-030）")+[
f"int airy_{sid}_init(struct airy_{sid}_ctx *ctx)","{",
"\tif (!ctx)","\t\treturn -EINVAL;",
f"\tctx->state = AIRY_{SU}_RUNNING;","\tctx->stamp_ns = ktime_get_ns();",
"\treturn 0;","}"]
            else:
                note=f"// 实现段 {kk}/{n}：调用上一段（{w.tasks[kk-2]}）符号，主逻辑与错误路径"
                call=f"airy_{sid}_impl_{kk-1}(ctx)" if kk>3 else f"airy_{sid}_init(ctx)"
                body=[f"// SPDX-License-Identifier: {lic}",note,f'#include "{sid}.h"',""]+_kdoc(
f"airy_{sid}_impl_{kk}",f"{w.name} 主逻辑链第 {kk-1} 段（调用 {prev}）",
[("ctx","本 WP 上下文，见 struct airy_"+sid+"_ctx")],
"0 成功；-EINVAL 参数非法；-EAGAIN 上游失败（OS-STD-CODE-030）")+[
f"int airy_{sid}_impl_{kk}(struct airy_{sid}_ctx *ctx)","{","\tint ret;","",
"\tif (!ctx)","\t\treturn -EINVAL;",
f"\tret = {call};","\tif (ret)","\t\tgoto err;",
f"\tctx->state = AIRY_{SU}_RUNNING;","\treturn 0;","err:",
f'\tpr_err("airy_{sid}: seg {kk} failed (%d)\\n", ret);',"\treturn ret;","}"]
        fence="c"
    elif lang=="python":
        if n==1:
            body=[f"# SPDX-License-Identifier: {lic}",
f'"""airy_{sid} — {w.name}（整包：接口 + 实现 + 测试）。"""',
"from dataclasses import dataclass",
"",
f"@dataclass",
f"class Airy{CL}Ctx:",
f'    """{w.name} 上下文（state: 0=IDLE, 1=RUNNING）。"""',
"    state: int = 0",
"    stamp_ns: int = 0",
"",
f"def airy_{sid}_init(ctx: Airy{CL}Ctx) -> int:",
'    """动作函数返回 0/-Exxx（OS-STD-CODE-030）。"""',
"    if ctx.state < 0:",
"        return -22  # -EINVAL",
"    ctx.state = 1",
"    return 0",
"",
f"def test_airy_{sid}_basic() -> None:",
f"    ctx = Airy{CL}Ctx()",
f"    assert airy_{sid}_init(ctx) == 0"]
        elif k==0:
            depc=[f"from .{wslug[dep]} import *  # 前驱 WP {dep}：接口衔接"] if dep else []
            body=[f"# SPDX-License-Identifier: {lic}",
f'"""airy_{sid} — {w.name}（接口与类型；实现/测试分片 import 本模块衔接）。"""',
"from dataclasses import dataclass",
""]+depc+[
"",
f"@dataclass",
f"class Airy{CL}Ctx:",
f'    """{w.name} 上下文（state: 0=IDLE, 1=RUNNING）。"""',
"    state: int = 0",
"    stamp_ns: int = 0",
"",
f"def airy_{sid}_init(ctx: Airy{CL}Ctx) -> int:",
f'    """动作函数：0 成功 / -Exxx 失败（OS-STD-CODE-030）。实现在分片 {w.tasks[1]}，本片 raise 占位。"""',
f'    raise NotImplementedError("实现在 {w.tasks[1]} 分片")',
"",
f"def airy_{sid}_ready(ctx: Airy{CL}Ctx) -> bool:",
'    """谓词函数返回 bool（OS-STD-CODE-030）。"""',
"    return ctx.state == 1"]
        elif k==n-1:
            pre=[f"def airy_{sid}_init(ctx: Airy{CL}Ctx) -> int:",
f'    """实现接口片（{first}）声明的 init（OS-STD-CODE-030）。"""',
"    if ctx.state < 0:",
"        return -22  # -EINVAL",
"    ctx.state = 1",
"    ctx.stamp_ns = time.monotonic_ns()",
"    return 0"] if n==2 else []
            body=[f"# SPDX-License-Identifier: {lic}",
f'"""{tid} 单元测试：覆盖 {first}..{prev} 全链（衔接前片符号）。"""']+(
[f"import time"] if n==2 else [])+[
f"from .{sid} import Airy{CL}Ctx, airy_{sid}_ready"]+(
([f"from .{entry_mod} import {entry}"] if n>2 else [])+pre+[
"",
f"def test_airy_{sid}_basic() -> None:",
f"    ctx = Airy{CL}Ctx()",
f"    assert not airy_{sid}_ready(ctx)",
f"    assert {entry}(ctx) == 0",
f"    assert airy_{sid}_ready(ctx)"])
        else:
            if kk==2:
                body=[f"# SPDX-License-Identifier: {lic}",
f'"""{tid} 实现段 {kk}/{n}：定义接口片（{prev}）声明的 airy_{sid}_init。"""',
"import time",
f"from .{sid} import Airy{CL}Ctx",
"",
f"def airy_{sid}_init(ctx: Airy{CL}Ctx) -> int:",
'    """动作函数：0 成功 / -Exxx 失败（OS-STD-CODE-030）。"""',
"    if ctx.state < 0:",
"        return -22  # -EINVAL",
"    ctx.state = 1",
"    ctx.stamp_ns = time.monotonic_ns()",
"    return 0"]
            else:
                call=f"airy_{sid}_impl_{kk-1}(ctx)" if kk>3 else f"airy_{sid}_init(ctx)"
                src=(f"from .{sid}_impl_2 import airy_{sid}_init" if kk==3 else
                     f"from .{sid}_impl_{kk-1} import airy_{sid}_impl_{kk-1}")
                body=[f"# SPDX-License-Identifier: {lic}",
f'"""{tid} 实现段 {kk}/{n}：调用上一段（{w.tasks[kk-2]}）符号，主逻辑与错误路径。"""',
f"from .{sid} import Airy{CL}Ctx",src,
"",
f"def airy_{sid}_impl_{kk}(ctx: Airy{CL}Ctx) -> int:",
'    """动作函数：0 成功 / -Exxx 失败（OS-STD-CODE-030）。"""',
f"    if {call} < 0:",
"        return -11  # -EAGAIN",
"    ctx.state = 1",
"    return 0"]
        fence="python"
    elif lang=="cpp":  # cpp（UKUI 适配层，ALK：仅新增文件）
        cppctx=_kdoc(f"Airy{CL}Ctx",f"{w.name} 上下文",
             [("state","状态机取值（0=IDLE, 1=RUNNING）"),
              ("stamp_ns","CLOCK_MONOTONIC 纳秒戳")])+[
"struct Airy"+CL+"Ctx {",
"    int state = 0;          // 0=IDLE, 1=RUNNING",
"    quint64 stamp_ns = 0;",
"};"]
        cppinit=[f"int airy_{sid}_init(Airy{CL}Ctx *ctx)","{",
"    if (!ctx)","        return -EINVAL;",
"    ctx->state = 1;","    ctx->stamp_ns = 0;","    return 0;","}"]
        if n==1:
            body=[f"// SPDX-License-Identifier: {lic}",
f"// 整包任务：接口 + 实现 + QtTest（{w.name}；UKUI 适配层，ALK）",
"#include <QtTest>",
"#include <QtGlobal>",""]+cppctx+[""]+_kdoc(
f"airy_{sid}_init",f"初始化 {w.name} 上下文（整包任务内联定义）",
[("ctx","待初始化上下文（输出参数）")],
"0 成功；-EINVAL 参数非法（OS-STD-CODE-030）")+cppinit+["",
f"class Airy{CL}Test : public QObject",
"{",
"    Q_OBJECT",
"private slots:",
f"    void airy_{sid}_test_init();",
"};",
"",
f"void Airy{CL}Test::airy_{sid}_test_init()",
"{",
f"    Airy{CL}Ctx ctx;","",
f"    QVERIFY(airy_{sid}_init(&ctx) == 0);",
"    QVERIFY(ctx.state == 1);",
"}",
"",
f"QTEST_MAIN(Airy{CL}Test)",
f'#include "{sid}_test.moc"']
        elif k==0:
            depinc=[f'#include "{wslug[dep]}.h"  // 前驱 WP {dep}：接口衔接'] if dep else []
            cprotos=[]
            for kk in range(3,n):  # 实现链 impl_3..impl_{n-1} 跨分片调用，须在接口头声明
                cprotos+=_kdoc(f"airy_{sid}_impl_{kk}",f"{w.name} 主逻辑链第 {kk-1} 段（分片 {w.tasks[kk-1]}）",
                               [("ctx","本 WP 上下文，见 struct Airy"+CL+"Ctx")],
                               "0 成功；-EINVAL 参数非法；-EAGAIN 上游失败（OS-STD-CODE-030）")
                cprotos+=[f"int airy_{sid}_impl_{kk}(Airy{CL}Ctx *ctx);",""]
            body=[f"// SPDX-License-Identifier: {lic}",
f"#ifndef _AIRY_{SU}_H",           # OS-IRON-010：守卫对齐内核，禁 pragma once
f"#define _AIRY_{SU}_H",
"",
"#include <QtGlobal>"]+depinc+["",
f"// {w.name} 接口（本任务仅类型与原型，禁写实现；UKUI 适配层，ALK）",""]+cppctx+[""]+_kdoc(
f"airy_{sid}_init",f"初始化 {w.name} 上下文（实现在分片 {w.tasks[1] if n>1 else '—'}）",
[("ctx","待初始化上下文（输出参数）")],
"0 成功；-EINVAL 参数非法（OS-STD-CODE-030）")+[
f"int airy_{sid}_init(Airy{CL}Ctx *ctx);",
""]+cprotos+[
f"#endif /* _AIRY_{SU}_H */"]
        elif k==n-1:
            pre=[] if n>2 else _kdoc(f"airy_{sid}_init",f"初始化 {w.name} 上下文（实现接口片 {first} 的声明）",
[("ctx","待初始化上下文（输出参数）")],
"0 成功；-EINVAL 参数非法（OS-STD-CODE-030）")+cppinit
            body=[f"// SPDX-License-Identifier: {lic}",
f"// QtTest：覆盖 {first}..{prev} 全链（衔接前片符号）",
"#include <QtTest>",
f'#include "{sid}.h"',""]+pre+["",
f"class Airy{CL}Test : public QObject",
"{",
"    Q_OBJECT",
"private slots:",
f"    void airy_{sid}_test_init();",
"};",
"",
f"void Airy{CL}Test::airy_{sid}_test_init()",
"{",
f"    Airy{CL}Ctx ctx;","",
f"    QVERIFY({entry}(&ctx) == 0);",
"    QVERIFY(ctx.state == 1);",
"}",
"",
f"QTEST_MAIN(Airy{CL}Test)",
f'#include "{sid}_test.moc"']
        else:
            if kk==2:
                body=[f"// SPDX-License-Identifier: {lic}",
f"// 实现段 {kk}/{n}：定义接口片（{prev}）声明的 airy_{sid}_init",
f'#include "{sid}.h"',""]+_kdoc(
f"airy_{sid}_init",f"初始化 {w.name} 上下文（定义接口片 {prev} 的声明）",
[("ctx","待初始化上下文（输出参数）")],
"0 成功；-EINVAL 参数非法（OS-STD-CODE-030）")+cppinit
            else:
                call=f"airy_{sid}_impl_{kk-1}(ctx)" if kk>3 else f"airy_{sid}_init(ctx)"
                body=[f"// SPDX-License-Identifier: {lic}",
f"// 实现段 {kk}/{n}：调用上一段（{w.tasks[kk-2]}）符号，主逻辑与错误路径",
f'#include "{sid}.h"',""]+_kdoc(
f"airy_{sid}_impl_{kk}",f"{w.name} 主逻辑链第 {kk-1} 段（调用 {prev}）",
[("ctx","本 WP 上下文，见 struct Airy"+CL+"Ctx")],
"0 成功；-EINVAL 参数非法；-EAGAIN 上游失败（OS-STD-CODE-030）")+[
f"int airy_{sid}_impl_{kk}(Airy{CL}Ctx *ctx)","{",
"    if (!ctx)","        return -EINVAL;",
f"    if ({call})","        return -EAGAIN;",
"    ctx->state = 1;","    return 0;","}"]
        fence="cpp"
    elif lang in ("spec","sh","ini","xml"):  # v3.4：发行版/运维工件按真实载体出示例（M/Q 泳道）
        _f={"spec":"spec","sh":"bash","ini":"ini","xml":"xml"}[lang]
        depnote=f"衔接前驱 WP {dep}" if dep else "链首无前驱"
        deplang=_art_lang(wps[dep]) if dep else None
        if lang=="spec":
            meta=["# SPDX-License-Identifier: "+lic,
"# rpm/"+sid+".spec — "+w.name+"（"+depnote+"；OS-IRON-004：包名一律 airy-*，不占用上游命名空间）",
"Name:           airy-"+sid,
"Version:        1.0.0",
"Release:        1%airymax",
"Summary:        AirymaxOS "+w.name,
"License:        "+("GPLv2" if _kern(w) else "Apache-2.0"),
"URL:            https://www.airymax.internal/pkg/airy-"+sid,
"BuildRequires:  airymax-spec-macros",
"BuildRequires:  gcc, make"]
            if n==1:
                body=meta+["","%description",w.name+"（整包任务：元数据+构建+安装+校验一体）。","",
"%prep","%autosetup -p1","","%build","%make_build","","%install","%make_install","",
"%files","%license COPYING","%{_bindir}/airy-*","",
"%changelog","* Mon Oct 05 2026 Airymax Devel <devel@airymax.internal> - 1.0.0-1",
"- Initial AirymaxOS packaging (v3.4 账本)。"]
            elif k==0:
                body=meta+["",
"# 接口片：仅元数据与依赖声明，禁写 %prep/%build/%install（构建段在分片 "+w.tasks[1]+"）"]+([f"Requires:       airy-{wslug[dep]}"] if dep and deplang=="spec" else [f"# 前驱 WP {dep}（{'C/C++ 用户态' if deplang=='c' else deplang}载体）：随本包打包交付，无独立 RPM Requires" if dep else "# 链首：无前驱包 Requires"])
            elif k==n-1:
                body=["# SPDX-License-Identifier: "+lic,
"# 末片：%check + %changelog + 校验收口（续接分片 "+prev+" 的最后一个 %files 之后）","",
"%check","make check","",
"%changelog","* Mon Oct 05 2026 Airymax Devel <devel@airymax.internal> - 1.0.0-1",
"- "+w.name+"：分片 "+first+"…"+prev+" 全链合入（v3.4）。","",
"# 验收：rpmspec -P rpm/"+sid+".spec 展开无错；rpmlint -i 零 E 级"]
            elif kk==2:
                body=["# SPDX-License-Identifier: "+lic,
"# 实现段 2/"+str(n)+"：%prep/%build 段（紧接接口片 "+prev+" 元数据之后拼接）","",
"%prep","%autosetup -p1","","%build","%make_build"]
            else:
                body=["# SPDX-License-Identifier: "+lic,
"# 实现段 "+str(kk)+"/"+str(n)+"：子包片段（续接分片 "+w.tasks[kk-2]+"，每段一个 %package，禁重复前置段）","",
"%package sub"+str(kk),
"Summary:        AirymaxOS "+w.name+" 组件片段 "+str(kk),"",
"%description sub"+str(kk),
w.name+" 第 "+str(kk)+" 段组件（衔接上一段 "+prev+"）。","",
"%files sub"+str(kk),
"%{_bindir}/airy-"+sid+"-"+str(kk)]
        elif lang=="sh":
            hdr=["#!/bin/bash","# SPDX-License-Identifier: "+lic,
"# scripts/"+sid+".sh — "+w.name+"（"+depnote+"；shell 一律 set -euo pipefail）",
"set -euo pipefail"]
            initfn=["airy_"+sid+"_init() {",'    local ctx="${1:-}"',
'    [ -n "$ctx" ] || return 22   # -EINVAL 口径（OS-STD-CODE-030）',
'    echo "airy_'+sid+' ctx=$ctx" >>"${AIRY_LOG:-/dev/null}"',"    return 0","}"]
            if n==1:
                body=hdr+[""]+initfn+["","# 整包任务：内联自测（末片语义并入）",
"airy_"+sid+"_init demo && echo PASS","",
"# 验收：shellcheck scripts/"+sid+".sh 零 warning"]
            elif k==0:
                depsrc=[f'source "$AIRY_LIB_DIR/{wslug[dep]}.sh"   # 前驱 WP {dep}：接口衔接'] if dep and deplang=="sh" else ([f'# 前驱 WP {dep}（{deplang} 载体）：接口以其交付物为准，不经 AIRY_LIB_DIR source' if dep else '# 链首：无前驱 source'] if lang=="sh" else [])
                body=hdr+depsrc+["",
"# 接口片：仅声明函数契约（占位返回），实现在分片 "+w.tasks[1]+"；禁写业务逻辑",
"airy_"+sid+"_init() {",'    [ -n "${1:-}" ] || return 22',
"    : # 占位：定义见分片 "+w.tasks[1]+"（source 后覆盖本桩）","}"]
            elif k==n-1:
                srcs=[f'source "$AIRY_LIB_DIR/{sid}.sh"']+[f'source "$AIRY_LIB_DIR/{sid}_impl_{j}.sh"' for j in range(2,n)]
                pre=[] if n>2 else ["","airy_"+sid+"_init() {",'    local ctx="${1:-}"','    [ -n "$ctx" ] || return 22',"    return 0","}"]
                body=["#!/bin/bash","# SPDX-License-Identifier: "+lic,
"# tests/"+sid+"_test.sh — 末片全链自测（"+first+"…"+prev+"；入口 "+entry+" 贯通）",
"set -euo pipefail",""]+srcs+pre+["",
entry+" demo && echo PASS","",
"# 验收：shellcheck tests/"+sid+"_test.sh 零 warning；用例失败即 CI 阻断"]
            elif kk==2:
                body=hdr+["","# 实现段 2/"+str(n)+"：定义接口片（"+prev+"）声明的 airy_"+sid+"_init",""]+initfn
            else:
                srcf=f"{sid}_impl_2.sh" if kk==3 else f"{sid}_impl_{kk-1}.sh"
                call=f'airy_{sid}_init "$ctx"' if kk==3 else f'airy_{sid}_impl_{kk-1} "$ctx"'
                body=["#!/bin/bash","# SPDX-License-Identifier: "+lic,
f"# 实现段 {kk}/{n}：source {srcf}（分片 {w.tasks[kk-2]}）后扩展主逻辑",
"set -euo pipefail","",f'source "$AIRY_LIB_DIR/{srcf}"',"",
f"airy_{sid}_impl_{kk}() {{",'    local ctx="${1:-}"','    [ -n "$ctx" ] || return 22',
"    "+call+' || return 11   # -EAGAIN 口径：上游失败',"    return 0","}"]
        elif lang=="ini":
            unit="airy_"+sid+".service"
            reql=([f"Requires=airy_{wslug[dep]}.service", f"After=airy_{wslug[dep]}.service airymax-target.target"] if dep and deplang=="ini" else ([f"# 前驱 WP {dep}（{deplang} 载体）：非 unit 交付，依赖经 airymax-target 收口", "After=airymax-target.target"] if dep else ["After=airymax-target.target"]))
            svc=["[Service]","Type=exec","ExecStart=/usr/libexec/airy_"+sid,"Restart=on-failure"]
            if n==1:
                body=["# SPDX-License-Identifier: "+lic,
"# system-unit/"+unit+" — "+w.name+"（整包任务；"+depnote+"）","",
"[Unit]","Description=AirymaxOS "+w.name,
"Documentation=file:///usr/share/doc/airymax/"+sid]+reql+[""]+svc+["",
"SystemCallFilter=@system-service","MemoryDenyWriteExecute=yes","",
"[Install]","WantedBy=multi-user.target","",
"# 验收：systemd-analyze verify "+unit+" 零 error"]
            elif k==0:
                body=["# SPDX-License-Identifier: "+lic,
"# "+unit+" 接口片：仅 [Unit] 段，[Service]/[Install] 在分片 "+w.tasks[1]+"，本任务禁写","",
"[Unit]","Description=AirymaxOS "+w.name,
"Documentation=file:///usr/share/doc/airymax/"+sid]+reql
            elif k==n-1:
                pre=[] if n>2 else [""]+svc
                body=["# SPDX-License-Identifier: "+lic,
"# "+unit+" 末片：[Install] 收口（续接分片 "+prev+" 之后）",""]+pre+["",
"[Install]","WantedBy=multi-user.target","",
"# 验收：systemd-analyze verify "+unit+"；systemctl enable 后 is-active 为 active"]
            elif kk==2:
                body=["# SPDX-License-Identifier: "+lic,
"# 实现段 2/"+str(n)+"：[Service] 主段（紧接接口片 "+prev+" 的 [Unit] 之后）",""]+svc
            else:
                body=["# SPDX-License-Identifier: "+lic,
"# 实现段 "+str(kk)+"/"+str(n)+"：[Service] 加固续段（拼接于分片 "+w.tasks[kk-2]+" 的同段之后）","",
"# 以下指令并入本 unit 的 [Service] 段（07-scheduling：R1-04 资源切片铁律）",
"SystemCallFilter=@system-service","MemoryDenyWriteExecute=yes","ProtectSystem=strict",
"Slice=airymax-"+sid+".slice","CPUAccounting=yes","MemoryAccounting=yes"]
        else:  # xml（ comps 组件组元数据）
            decl=['<?xml version="1.0" encoding="UTF-8"?>',
"<!-- SPDX-License-Identifier: "+lic+" -->",
'<!DOCTYPE comps PUBLIC "-//Airymax//DTD Comps 1.0//EN">',
"<comps>  <!-- "+w.name+"（"+depnote+"） -->"]
            if n==1:
                body=decl+["","  <group>","    <id>airymax-"+sid+"</id>","    <name>AirymaxOS "+w.name+"</name>",
"    <packagelist>",'      <package name="airy-'+sid+'" type="default"/>',"    </packagelist>","  </group>",
"</comps>","",
"<!-- 验收：xmllint --noout --valid "+sid+".xml 零错误 -->"]
            elif k==0:
                body=decl+["",
"  <!-- 接口片：仅文档头与 <comps> 根，条目批在分片 "+w.tasks[1]+"，本任务禁写闭合标签 -->"]
            elif k==n-1:
                body=["<!-- SPDX-License-Identifier: "+lic+" -->",
"  <!-- 末片：闭合根元素（续接分片 "+prev+" 的最后一个条目之后） -->","</comps>","",
"<!-- 验收：分片 "+first+"…"+prev+" 顺序拼接后 xmllint --noout --valid "+sid+".xml 零错误 -->"]
            else:
                pkgs=['      <package name="airy-'+sid+'"/>']+([f'      <package name="airy-{wslug[dep]}"/>'] if dep else ["      <!-- 链首：无前驱包 -->"])
                body=["<!-- SPDX-License-Identifier: "+lic+" -->",
"  <!-- 实现段 "+str(kk)+"/"+str(n)+"：组条目批（续接分片 "+w.tasks[kk-2]+" 打开的 <comps> 根） -->",
"  <group>","    <id>airymax-"+sid+"-"+str(kk)+"</id>",
"    <name>AirymaxOS "+w.name+" 条目批 "+str(kk)+"</name>","    <packagelist>"]+pkgs+["    </packagelist>","  </group>"]
        fence=_f
    body=_inject_sys_incs(body,_need_incs("\n".join(body),lang))
    return hd+[f"```{fence}"]+body+["```",""]

# ---------- 11. Markdown ----------
L=[]; P=L.append
P("# AgentRT / AirymaxOS（agent-linux）开发施工图纸")
P("")
P("> **版本 v3.4（账本勘误 + 发行版工件模板版）** ｜ 2026-10-06 ｜ 密级：内部机密（docs-closed）")
P(">")
P(f"> 本版依据 `docs/docs-linux/analysis/loc-estimation-final.md`（基准净新增 383,724 行终版估算）+ **{len(SUPP)} 个补充 WP（v3.2 补录 62 + v3.4 补录 {len(SUPP)-62}，缩放后实摊 {SUPP_LOC:,} 行，见 §5.1）**，")
P("> 以 `docs/docs-linux` 全部 185 篇方案的内容为锚做覆盖审查，")
P("> 将整体工程拆解为 **工作包（WP）→ 原子任务（100~200 行）** 两级施工账本，并给出逐泳道、逐日排程。")
P("> v2.1 的 Phase 1~6 粗粒度规划由本版任务账本取代；**Phase 0 完成记录保留**（见 §1.3）。")
P(">")
P("> **v3.1 增量**（针对 v3.0 复核意见「施工图纸不够细化、每个任务的上下依赖不够严谨」）：")
P("> ① 种子层逐对显式化 **24 条跨 WP 逻辑依赖**（含 `L-04→A-01`「契约先于内核实现」硬闸，见 §4.2），全排程按新依赖闭包重算；")
P("> ② 任务分片按「接口与类型 / 实现段 / 单元测试与文档」语义命名，任务卡新增 **产出物** 与 **直接后继（阻塞）** 两列（§6）；")
P("> ③ 新增 **§6.0 WP 双向邻接反查表**，前序/后继/泳道前后包全部可审计；脚本断言任务级前驱边与后继边严格互逆。")
P(">")
P("> **v3.2 增量**（以 docs-linux 方案内容为锚的第二轮覆盖审查，逐目录扫描 185 篇文档的「需实现」交付点）：")
P("> ① 新增 **62 个补充 WP**，修复「方案有、图纸无」缺口（含 riscv 接线、零信任网络、")
P(">    Cupolas 网络穹顶、L2/L3/L4 语义记忆层、Service Mesh、DPU/IPU 卸载、Rust 内核模块、四语言 SDK、Coq/Isabelle 等），")
P(">    每个补充 WP 在 §5.1 附方案文档证据（文件:行）可溯源；")
P("> ② S8 整体验收锚点扩展为**全 WP 闭包**（原 4 锚点 + 62 个补充 WP 全部 ✅ 方可达成 OS-ACC-110）；")
P("> ③ 总工期相应顺延，新收口日见 §1.1 与 §7；补录 WP 依赖边与原 260 WP 同一依赖图，前驱/后继双向可审计。")
P("> docs 仓 `130-roadmap` 仍为路线权威口径；本文件是其在 agent-linux 方向的施工展开，施工轨里程碑命名 S0~S8（与 docs 仓文档轨 M0~M8 一一对应，命名隔离避免双轨混淆），验收口径与 OS-ACC-001~110 不变。")
P(">")
P("> **v3.3 增量**（针对「每个任务都要有示例代码、遵循 50 工程规范、上下任务标准统一与逻辑衔接」）：")
P(f"> ① 每个原子任务附一段骨架示例代码（§6.x.1，共 {ntask-ngate:,} 段），模板逐条对齐 `50-engineering-standards`（见 §2.1 规范映射表）；")
P("> ② 同一 WP 内分片**符号级衔接**：接口片声明 `airy_<wp>_init()` → 实现段定义/链式调用 → 末片 KUnit/pytest/QtTest 覆盖全链；")
P("> ③ 跨 WP 依赖落到代码层：接口片 `#include` 逻辑前驱 WP 的头文件；")
P("> ④ SPDX 按泳道自动双轨（内核 GPL-2.0-only / 用户态 AGPL-3.0-or-later OR Apache-2.0），头文件守卫统一 `#ifndef _AIRY_*_H`（OS-IRON-010）。")
P(">")
P(f"> **v3.4 增量**（第四轮逐任务深度审查勘误落地：补录 {len(SUPP)-62} 项、删除 2 项、21 项改名并重接依赖）：")
P(f"> ① 补充 WP 台账扩至 **{len(SUPP)} 包**（新增 UKUI 运行栈、记忆运维引擎、Q 部署主线、J 静态/动态分析等，申报 +{V34_DECLARE:,} 行），账本总量 **{sum(TARGETS.values()):,} 行**；")
P("> ② SSoT 冲突归零：安全轨统一「纯 C LSM、零 BPF LSM」铁律（03-security.md:127 BPF 孤文列为设计文档待修项）；删除 I-14/L-02 冗余 WP 并重接全部下游依赖；")
P("> ③ M/Q 发行版与运维工件（RPM spec / systemd unit / comps XML / shell 脚本 / CLI）改用与载体匹配的示例模板，不再误套 C 骨架（语言路由见 §2.1）；")
P("> ④ 新增 **S7「桌面与生态就绪」验收锚点**（UKUI 可登录、会话可运行，主干 `R1-01→R1-03→R1-05→R1-02→R1-06→M-23→M-15→M-17`），S8 全账本收口同步扩容。")
P("")
P("## 1. 定位与基线")
P("")
P("### 1.1 工程总账")
P("")
P(f"- 净新增代码总量：**{sum(TARGETS.values()):,} 行**（19 个模块；§5 逐模块对账差 0。其中 {len(SUPP)} 个补充 WP 缩放后实摊 {SUPP_LOC:,} 行，见 §5.1；其余 {BASE_LOC:,} 行为 v3.1 基线（删 I-14/L-02 后存续 258 WP））")
P(f"- 工作包（WP）：**{len(wps)-ngate} 个**（另有 {ngate} 个设计门禁 WP，0 行代码、各占 5 个设计日）")
P(f"- 原子任务：**{ntask:,} 个**，每个任务净增代码严格控制在 **100~200 行**（设计门禁除外）")
P(f"- 泳道：**{len(lanes)} 条**（每泳道每施工日承担 1 个原子任务）")
P(f"- 排程：起始 **2026-10-05**（W0），每 10 个施工日插入 1 个验收日，周末不排任务；")
P(f"  全账本共 {maxraw} 个施工日（约 {cal_of(maxraw)} 个工作日，跨度至 {date_of(cal_of(maxraw))}）；关键路径 {len(cp)} 个任务。")
P("")
P("### 1.2 原子化原则（质量保证机制）")
P("")
P("1. **100~200 行/任务**：单任务=单文件、单函数或单小组件，一次评审可看完；禁止跨语义打包。")
P("2. **契约先行**：所有 [SC]/[SS]/[IND]/[DSL] 接口先由 L-01/L-04（codegen）生成，人只写实现，杜绝手写 ABI 漂移。")
P("3. **ALK 铁律**：只新增文件、不改主线；每任务的 diff 天然限定在 airy/ 新文件与号段接线点内。")
P("4. **任务即提交**：一个任务=一个 commit=一次 PR，标题遵循内核 submitting-patches 规范（`airy/xxx: …`），")
P("   修复类落款 `lidecheng@spharx.cn`、功能类落款 `wangliren@spharx.cn`。")
P("5. **DoD（完成定义）**：实现 + KUnit/kselftest 挂点 + OS-CHK 门禁通过 + 契约快照更新，四项缺一不勾选。")
P("6. **设计空洞门禁（GT-*）**：方案低置信度处（机密计算、国密、Wasm 3.0、DevStation、用户态 VFS、用户态网络栈）")
P("   先排 5 天详设，详设评审通过前其后所有 WP 不得开工（见 §9）。")
P("")
P("### 1.3 Phase 0 完成记录（保留自 v2.1，不计入本账本）")
P("")
P("| 项 | 内容 | 落点 | 状态 |")
P("|---|---|---|---|")
P("| P0-1 | 版本库卫生（kernel 仓） | `0207ff0` | ✅ 2026-08-01 |")
P("| P0-2 | 分支模型建立 | `ef6103e` | ✅ |")
P("| P0-3 | 工具入库（codegen 雏形/checkpatch 基线） | `8fe4e7d` | ✅ |")
P("| P0-4 | CI 骨架（矩阵构建初版） | `7813134` | ✅ |")
P("| P0-5 | sw_64 syscall 号段 548~551 申请落位 | `dd990c6` | ✅ |")
P("")
P("## 2. 任务卡规范")
P("")
P("每张任务卡（账本行）的字段含义：")
P("")
P("```")
P("T<WP>-<序号> | 任务描述（WP 名 + 分片角色） | 产出物 | 净新增 LOC | 泳道 | 施工日/日历日 | 严格前驱 | 直接后继 | 状态")
P("```")
P("")
P("- **状态**：⬜ 未开工 / 🟨 进行中 / ✅ 已验收（初始全部 ⬜）；")
P("- **分片角色**：首片=接口与类型（头文件/原型，禁写实现）；中片=实现段（主逻辑+错误路径）；末片=单元测试与文档（DoD 收口）；")
P("- **产出物**：本任务合入后仓库中新增/更新的文件形态，评审按此验收，防止「实现（k/n）」式含糊任务；")
P("- **严格前驱**：列出必须已 ✅ 的任务 ID；同 WP 内为串行分片，WP 间为接口依赖（种子显式声明），同泳道为资源串行；")
P("- **直接后继（阻塞）**：本任务 ✅ 之前不得开工的下游任务 ID——与前驱列互为逆边，脚本逐边断言双向对称，任何一条边都可正反两个方向核对；")
P("- 前驱为空或仅含已完成分片的任务，即为**当日可并行领取**的任务；后继为「—（链尾）」表示该任务不阻塞任何下游。")
P("")
P("### 2.1 任务示例代码规范（v3.3 新增）")
P("")
P("每个原子任务附一段骨架示例代码（§6.x.1），全账本采用同一套模板，保证**上下任务标准统一与代码逻辑衔接**。")
P("模板逐条对齐 `docs/docs-linux/50-engineering-standards`（SSoT：`01-coding-standards.md`）：")
P("")
P("| 约定 | 规范来源 | 在示例中的体现 |")
P("|---|---|---|")
P("| 符号命名 `airy_<wp>_<slug>_*`，全局描述性命名 | OS-STD-CODE-001 / 前缀隔离 §1.6 | 函数与结构体名内嵌 WP 编号，跨任务可反查归属 |")
P("| 动作函数返回 `0 / -Exxx`，谓词函数返回 `bool` | OS-STD-CODE-030 | `airy_*_init()` 返 int，`airy_*_ready()` 返 bool |")
P("| 公共 API 必须 kernel-doc；Python 用 Google docstring | OS-STD-CODE-012 / 014 | 结构体与函数带 kernel-doc 注释块或 docstring |")
P("| include 顺序：系统头 → 架构头 → 本地头 | OS-STD-CODE-016 | `<linux/types.h>` 在前，本 WP 头文件其后 |")
P("| 头文件保护 `#ifndef _AIRY_<UP>_H` 与路径对应 | OS-STD-CODE-017 | 接口分片整段用 guard 包裹 |")
P("| 错误路径 goto 集中出口（C）/ `?`+RAII（Rust） | OS-STD-CODE-022 | 实现分片统一 `if (ret) goto err;` |")
P("| 内核内部类型用 `u32/u64`，UAPI 用 `__u32` | OS-STD-CODE-032 | 结构体字段用 `u32 state; u64 stamp_ns;` |")
P("| 禁 `strcpy/strncpy`，用 `strscpy` | OS-BAN-004 | 模板不含被禁接口（需要时按此替换） |")
P("| SPDX 双轨：内核 `GPL-2.0-only`，用户态 `AGPL-3.0-or-later OR Apache-2.0` | 12-license-policy.md:L152/L175 | 每段首行按 WP 泳道自动选择许可证 |")
P("| ALK 铁律：只新增文件、不改主线 | 00-architectural-principles | 示例均为新文件形态（`airy/<wp>.c`） |")
P("")
P("**衔接机制**（同一 WP 内分片串行，符号级可编译）：")
P("")
P("1. **首片（接口与类型）**：定义 `struct airy_<wp>_ctx` 与全部原型，并 `#include` 其**逻辑前驱 WP** 的头文件——跨 WP 依赖在代码层落地；")
P("2. **实现段 k/n**：`airy_<wp>_impl_<k>()` 调用上一段 `airy_<wp>_impl_<k-1>()`（首段则调用接口片声明的 `airy_<wp>_init()`），错误路径统一 goto 出口；")
P("3. **末片（测试与文档）**：KUnit / pytest / QtTest 引用**首片声明 + 各实现段符号**，覆盖 `T<wp>-01 … T<wp>-(n-1)` 全链，DoD 收口；")
P("4. 门禁任务（GT-*）产出详设文档，无代码示例，模板显式标注。")
P("")
P("语言按任务载体自动路由（v3.4）：L 工具链/CI → Python；R1/R2 UKUI 桌面 → C++/Qt；")
P("M/Q 发行版与运维工件按名称路由——spec 文件 → RPM spec、comps/XML → XML、systemd/journald/自检服务 → unit INI、dnf/插件与 Q-CLI → Python、其余脚本 → Bash；")
P("内核与其他用户态组件 → C。四类工件模板同样遵循「接口片→实现段→末片校验」分片语义（元数据/根元素/[Unit] → 构建/条目/[Service] 分段拼接 → %changelog/根闭合/[Install] 收口），SPDX 与片段衔接注记不缺失。")
P("")
P("## 3. 模块总览与开发顺序")
P("")
P("### 3.1 依赖关系（模块级）")
P("")
P("```")
P("L(工具链/CI) ──► A(syscall/Folding) ──► B(安全) ──► C(Supervisor) ──► D(可观测)")
P("                     │                    │            │")
P("                     ▼                    ▼            ▼")
P("                K4(内核调度)         E(内存/rovol)   F(认知运行时)")
P("                     │                    │            │")
P("                     ▼                    ▼            ▼")
P("                I(驱动) ─► K(用户态守护) ─► G(控制面) ─► H(系统服务/DevStation)")
P("                                          │")
P("                    N(兼容) ◄─ M(发行版) ─┴─► O(性能) / P(本地化) / Q(应用)")
P("                                          │")
P("                                          ▼")
P("                                    R1→R2(UKUI 桌面)")
P("```")
P("")
P("**顺序理由**：")
P("- **L 最先**（W0 起点）：[SC] 契约 codegen 与 CI 门禁是全工程的地基，先立规矩后写码；")
P("- **A 先于 B/C/D/E/F**：4 个 syscall、Badge、ipc_ring、Folding runtime 是所有子系统接入点；")
P("- **B/C/D 紧随**：安全强制、冻结原语、A-ULP 属于「先有刹车再踩油门」的链路；")
P("- **E/F/K 中段**：内存与认知运行时依赖 A/B 原语；用户态守护（K）依赖 C 的 superv IPC；")
P("- **G/H 后段**：控制面与系统服务是大规模用户态集成，需要 K/F/D 稳定；")
P("- **M/N/O/P/Q 收口**：发行版、兼容、性能、本地化、生态在功能冻结后展开；")
P("- **R1/R2 殿后**：UKUI 桌面依赖发行版镜像（M-14）与本地化（P-01），是最后可见层。")
P("")
P("### 3.2 模块账本（按计划开工先后排序）")
P("")
P("| 序 | 模块 | 名称 | WP | 任务 | LOC | 泳道 | 前序模块 | 开工日 | 收口日 |")
P("|---|---|---|---|---|---|---|---|---|---|")
for k,(m,nw,nt,loc,lst,st,en,dm) in enumerate(mod_stat_sorted,1):
    st1=en1=None
    P(f"| {k} | **{m}** | {MODULE_NAMES[m]} | {nw} | {nt} | {loc:,} | {','.join(lst)} | {','.join(dm) if dm else '—'} | {date_of(cal_of(st))} | {date_of(cal_of(en))} |")
P("")
P("> 「开工/收口日」为排程推导值（考虑前驱与泳道资源）；同序号区间内的模块大量并行。")
P("")
P("## 4. 并行泳道与关键路径")
P("")
P("### 4.1 泳道表（每泳道每日 1 任务；跨泳道可并行）")
P("")
P("| 泳道 | 职责 | WP | 任务 | LOC | 开工 | 收口 |")
P("|---|---|---|---|---|---|---|")
for ln in LANE_DESC:
    seq=lanes.get(ln,[])
    ts=[t for i in seq for t in wps[i].tasks]
    if not ts: P(f"| {ln} | {LANE_DESC[ln]} | 0 | 0 | 0 | — | — |"); continue
    st=min(day[t] for t in ts); en=max(day[t]+tasks[t].dur-1 for t in ts)
    P(f"| {ln} | {LANE_DESC[ln]} | {len(seq)} | {len(ts)} | {sum(tasks[t].loc for t in ts):,} | {date_of(cal_of(st))} | {date_of(cal_of(en))} |")
P("")
P("### 4.2 并行/串行规则")
P("")
P("- **可并行**：不同泳道之间、同泳道无链上关系的 WP 分片之间、契约已生成（L-04 ✅）后的任意实现任务之间；")
P("  典型并行面：A(K1~K4)、B(SEC1~2)、C(SUP1~2)、D、E、F(COG1~2)、J(QA1~2)、L(DEVOPS1~2) 在中前段同时满负荷。")
P("- **严格串行（硬依赖）**：")
P("  1. `L-01→L-03→L-04`（codegen→DSL 编译→[SC] 契约头补全与三路编译校验；v3.4 删冗余 L-02）先于一切内核实现任务：")
P("     由 `A-01←L-04` 硬闸兑现（v3.1 起排程真实生效，内核轨整体后移至契约就绪之后）；")
P("  2. `A-01→A-05→A-06`（syscall 入口→Badge→ipc_ring）先于 C/D/F/I/K 的接入层；")
P("  3. `A-10→A-11→A-24→…→A-28`（Folding→锁改造→freeze）先于 `C-01`（Micro-Supervisor）；")
P("  4. `B-02→B-03`（CNode→capability 链）先于 `E-05`（revoke）与 `R2-06`（权限 UX）；")
P("  5. `GT-*` 设计门禁先于对应 WP 群（见 §9）；UKUI 桌面会话主干 `M-14→R1-01→R1-03→R1-05→R1-02→R1-06→M-23→M-15→M-17`（R1-04 并行加固），`R2-01→…→R2-08` 应用套件全链；")
P("  6. 各 WP 内部分片严格串行（接口分片→实现分片→测试分片）。")
P("- **跨 WP 显式逻辑依赖（v3.1 新增 24 对，逐对写入种子，可双向审计）**：")
P("  契约先行：`A-01←L-04`、`A-26←L-04`、`A-11←L-04`、`A-23←L-01`、`B-06←L-03`、`C-08←L-03`；")
P("  守护进程宿主：`C-14←K-01`、`D-06←K-01`、`E-12←K-01`、`F-09←K-01`、`H-01←K-01`、`H-03←K-01`；")
P("  跨域协同：`B-20←E-01`（快照加密←rovol）、`D-04←A-23`（trace 集成←挂点）、`E-10←C-01`（回收←冻结）、")
P("  `F-06←I-10`（GPU 桥←VFIO）、`F-13←K-04`、`G-06←K-04`、`G-09←K-05`（llm 桥/CNI/网关←用户态网络栈）、")
P("  `H-22←O-06`（容量规划←压测模型）、`H-23←D-05`（变更审计←哈希链）、`I-15←M-07`（热更新←livepatch）、")
P("  `P-02←R1-01`（输入法←桌面会话基座）、`R2-04←H-06`（监控面板←指标采集）。")
P("  上述每条边同时出现在 §6.0 反查表与对应任务卡的「严格前驱/直接后继」两列，脚本断言正反边一一对应。")
P("- **资源串行（同泳道）**：同泳道任务不重叠；这是排程约束而非逻辑依赖，扩编泳道即可线性压缩工期。")
P("")
P("### 4.3 关键路径（最长依赖链，决定最早完工日）")
P("")
cp_loc=sum(tasks[t].loc for t in cp)
P(f"`{cp[0]}` → … → `{cp[-1]}`，共 {len(cp)} 个任务、{cp_loc:,} 行，全程 {maxraw} 施工日 → 最晚施工日 **{date_of(cal_of(maxraw))}**。")
P("")
P("关键路径任务（按序，可核对压缩空间）：")
P("")
P("| # | 任务 | 内容 | LOC | 施工日 | 日历日 |")
P("|---|---|---|---|---|---|")
for k,t in enumerate(cp,1):
    tt=tasks[t]
    P(f"| {k} | {t} | {tt.name} | {tt.loc if tt.loc else '—'} | {day[t]} | {date_of(cal_of(day[t]))} |")
P("")
P("## 5. 账目对账（与终版 LOC 估算严格一致）")
P("")
P("| 模块 | 终版估算目标 | 本图纸任务合计 | 差 |")
P("|---|---|---|---|")
for m in MOD_ORDER:
    s=sum(tasks[t].loc for w in wps.values() if w.mod==m for t in w.tasks)
    P(f"| {m} | {TARGETS[m]:,} | {s:,} | {s-TARGETS[m]} |")
P(f"| **合计** | **{sum(TARGETS.values()):,}** | **{tot_loc:,}** | **0** |")
P("")
P(f"- 任务总数 {ntask:,}；单任务 LOC 全部 ∈ [100, 200]（脚本断言校验通过）；均值 {tot_loc//(ntask-ngate)} 行；")
P(f"- WP 总数 {len(wps)-ngate}，设计门禁 {ngate}；依赖图无环（拓扑排程求解成功）。")
P(f"- 口径：基线（v3.1 原 260 WP，删 I-14/L-02 后存续 258 WP）实摊 **{BASE_LOC:,} 行** + 补充 {len(SUPP)} WP 实摊 **{SUPP_LOC:,} 行** = **{sum(TARGETS.values()):,} 行**；")
P(f"  补充 WP 申报 {SUPP_DECLARE:,} 行（v3.2 补录 {V32_DECLARE:,} + v3.4 补录 {V34_DECLARE:,}），按各模块 TARGETS 缩放取整后实摊如上（最大余数法的正常偏移，总量不变）。")
P("")
P(f"### 5.1 补充 WP 台账（v3.2 补录 62 包 + v3.4 补录 {len(SUPP)-62} 包，合计申报 {SUPP_DECLARE:,} 行）")
P("")
P("> 下列 WP 为 v3.2 / v3.4 两轮以 `docs/docs-linux` 方案内容为锚的覆盖审查补录项：方案明示「要实现」而 v3.1 图纸未覆盖的交付点。")
P("> 「证据」列为方案库中支撑该功能确属交付范围的文档位置（docs-linux 相对路径:行号），逐条可溯源核对。")
P("")
P("| WP | 模块 | 名称 | 申报 LOC | 实摊 LOC | 泳道 | 证据（docs-linux） |")
P("|---|---|---|---|---|---|---|")
for wid in SUPP:
    w=wps[wid]
    P(f"| {wid} | {w.mod} | {w.name} | {w.seed_loc:,} | {w.loc:,} | {w.lane} | {SUPP[wid]} |")
P(f"")
P(f"> 申报合计 {sum(wps[wid].seed_loc for wid in SUPP):,} 行（v3.2 补录 {V32_DECLARE:,} + v3.4 补录 {V34_DECLARE:,}）；按各模块 TARGETS 缩放后实摊合计 {sum(wps[wid].loc for wid in SUPP):,} 行（差额为最大余数法取整消化，总量不变）。缺失补录的方案条目仅限「纯规范/流程文档自身即交付物」类（不计代码）。")
P("")
P("## 6. 分模块施工任务账本")
P("")
P("> §6.0 为 WP 级双向邻接反查表（先审计工作包间的上下依赖），随后各模块先列 WP 表，再列全量任务明细（日期为计划日历日）。")
P("")
def lane_adj(wid):
    seq=lanes[wps[wid].lane]; k=seq.index(wid)
    return (seq[k-1] if k>0 else None, seq[k+1] if k+1<len(seq) else None)
P(f"### 6.0 WP 双向邻接反查表（全部 {len(wps)} 个工作包，含 {ngate} 个门禁）")
P("")
P("> **显式前序** = 种子中声明的逻辑依赖（其 ✅ 是本包开工硬条件）；**后继（被依赖）** = 反查出的引用本包的 WP——")
P("> 两列由同一份种子正反推导，任何一条依赖边必须同时出现在前包的“后继”与后包的“前序”中（脚本逐边断言）；")
P("> **泳道前包/后包** 为同泳道资源串行序（非逻辑依赖）。全工程显式前序为空的包仅 `L-01`（codegen 核心）——")
P("> Day-1 由此单点启动，其余所有包均受逻辑依赖闭包或泳道资源约束（与 §4.2「契约先行」规则一致）。")
P("")
P("| WP | 模块 | 显式前序（逻辑） | 后继（被依赖） | 泳道 | 泳道前包 | 泳道后包 |")
P("|---|---|---|---|---|---|---|")
for m in MOD_ORDER:
    for (i,_,_,_,_) in WPS[m]:
        w=wps[i]; lp,lsn=lane_adj(i)
        pd=",".join(w.deps) if w.deps else "—"
        post=wp_succ[i]; ptx=",".join(post) if post else "—"
        P(f"| {i} | {m} | {pd} | {ptx} | {w.lane} | {lp or '—'} | {lsn or '—'} |")
for (gi,gname,gln,gdep) in GATES:
    lp,lsn=lane_adj(gi)
    P(f"| {gi} | GATE | {','.join(gdep)} | {','.join(wp_succ[gi])} | {gln} | {lp or '—'} | {lsn or '—'} |")
P("")
for m in MOD_ORDER:
    ws=[wps[i] for i,_ in sorted(((i,MOD_ORDER.index(m)) for i in wps if wps[i].mod==m), key=lambda x:(min(day[t] for t in wps[x[0]].tasks),)) ] if False else [wps[i] for (i,_,_,_,_) in WPS[m]]
    nt=sum(len(w.tasks) for w in ws); loc=sum(tasks[t].loc for w in ws for t in w.tasks)
    P(f"### 6.{MOD_ORDER.index(m)+1} 模块 {m} —— {MODULE_NAMES[m]}（{loc:,} 行 / {len(ws)} WP / {nt} 任务）")
    P("")
    P("| WP | 名称 | LOC | 泳道 | 前序 WP（逻辑） | 后继 WP（被依赖） | 任务数 | 计划窗口 |")
    P("|---|---|---|---|---|---|---|---|")
    for w in ws:
        st=min(day[t] for t in w.tasks); en=max(day[t]+tasks[t].dur-1 for t in w.tasks)
        dep=",".join(w.deps) if w.deps else "—"
        post=",".join(wp_succ[w.id]) if wp_succ[w.id] else "—"
        P(f"| {w.id} | {w.name} | {w.loc:,} | {w.lane} | {dep} | {post} | {len(w.tasks)} | {date_of(cal_of(st))} ~ {date_of(cal_of(en))} |")
    P("")
    P("| 任务 ID | 内容 | 产出物 | LOC | 泳道 | 施工日 | 日历日 | 严格前驱 | 直接后继（阻塞） | 状态 |")
    P("|---|---|---|---|---|---|---|---|---|---|")
    for w in ws:
        for tid in w.tasks:
            t=tasks[tid]
            ps=sorted(set(preds[tid]))
            ss=sorted(set(succs[tid]))
            ptxt=", ".join(ps) if ps else "—（无前置，可即刻开工）"
            stxt=", ".join(ss) if ss else "—（链尾）"
            loc_s=str(t.loc) if t.loc else "0（设计日×5）"
            P(f"| {tid} | {t.name} | {t.art} | {loc_s} | {w.lane} | {day[tid]} | {date_of(cal_of(day[tid]))} | {ptxt} | {stxt} | ⬜ |")
    P("")
    mi=MOD_ORDER.index(m)+1
    P(f"#### 6.{mi}.1 任务示例代码（{nt} 个任务，遵循 50-engineering-standards）")
    P("")
    P("> 每任务一段骨架示例代码，统一约定见 §2.1；实现分片引用前一任务声明的符号（衔接），末片测试覆盖本 WP 全链。")
    P("")
    for w in ws:
        for tid in w.tasks:
            for l in code_lines(tid): P(l)
P("## 7. 逐日排程总表")
P("")
P("> 每施工日每泳道至多 1 任务；「当日任务」即当日可并行领取的工作项（前驱均已 ✅）。")
P("> 每 10 个施工日后插入 1 个**验收日**（跑 OS-CHK 全门禁 + 里程碑抽查），下表以「验收日」行显式列出。")
P("")
P("| 工作日 | 日历日 | 当日任务数 | 当日任务（ID） |")
P("|---|---|---|---|")
for cc,dte,cnt,ids in rows:
    if cnt=="—":
        P(f"| {cc} | {dte} | 0 | {ids} |")
    else:
        P(f"| {cc} | {dte} | {cnt} | {ids} |")
P("")
P("## 8. 里程碑与验收门禁映射")
P("")
P("| 里程碑 | 内容 | 锚点 WP | 达成日（推导） | 验收 |")
P("|---|---|---|---|---|")
ms_gate={
 "S0":"OS-CHK：codegen 快照一致 / CI 矩阵绿",
 "S1":"OS-ACC-001~015：4 syscall+Badge+Folding 贯通",
 "S2":"OS-ACC-016~040：LSM 强制、freeze、A-ULP 上线",
 "S3":"OS-ACC-041~060：双层裁决闭环、审计哈希链",
 "S4":"OS-ACC-061~072：CLT/Wasm/推理桥可用",
 "S5":"OS-ACC-073~088：用户态服务与控制面全量",
 "S6":"OS-ACC-089~098：可安装/可更新/兼容",
 "S7":"OS-ACC-099~104：桌面与生态",
 "S8":"OS-ACC-105~110：Soak/性能/等保整体验收",
}
for (mid,mname,anch,dte,rd) in ms_rows:
    P(f"| {mid} | {mname} | {anch} | {dte}（施工日 {rd}） | {ms_gate[mid]} |")
P("")
P("> 里程碑日期为**依赖闭包推导值**（锚点 WP 全部任务 ✅），实际以验收日门禁结果为准；任一锚点后移会自动顺延后续里程碑。")
P("> S8 锚点含 `R2-08`（桌面全量回归），保证整体验收晚于桌面收口；S5 与 S6 出现并行倒挂属正常——")
P("> 发行版可安装（M-17/N-03 闭包）不依赖 H 模块全部服务完成，两线在中段起并行推进（具体日期以 §8 推导表为准）。")
P("")
P("## 9. 设计空洞门禁（GT-*）")
P("")
P("| 门禁 | 详设内容 | 泳道 | 前置 WP | 门禁任务 | 计划窗口 | 解锁 WP | 前驱任务 | 后继任务 |")
P("|---|---|---|---|---|---|---|---|---|")
for (gi,gname,gln,gdep) in GATES:
    w=wps[gi]; tid=w.tasks[0]; st=day[tid]; en=st+4
    unlock=sorted(x for x in wps if gi in wps[x].deps)
    pv=", ".join(sorted(preds[tid])) or "—（无前置，可即刻开工）"
    sv=", ".join(sorted(succs[tid])) or "—（链尾）"
    P(f"| {gi} | {gname} | {gln} | {','.join(gdep)} | {tid} | {date_of(cal_of(st))} ~ {date_of(cal_of(en))} | {','.join(unlock)} | {pv} | {sv} |")
P("")
P("规则：GT 未 ✅ 前，被解锁 WP 的所有任务不得开工（排程已内置该约束）；详设产出计入 docs，不计 LOC。")
P("门禁任务同样具备任务级前驱/后继边，与其余任务共用同一张依赖图，故前驱列与其前驱的后继列严格互逆。")
P("")
P("## 10. 风险与进度跟踪")
P("")
P("| 风险 | 现象 | 处置 |")
P("|---|---|---|")
P("| R-A1 泳道过载 | 单泳道>120 任务（DEVOPS/SYS/GUI 段最重） | 拆分泳道即线性提速；扩编不改任务定义 |")
P("| R-A2 低置信度膨胀 | GT 解锁后实际 LOC 超预算 >20% | WP 追加拆片（保持 100~200 约束），重跑排程脚本 |")
P("| R-A3 主线漂移 | 上游 6.6 stable 更新 | 每验收日跑 L-05 ABI 检查 + L-06 OS-CHK |")
P("| R-A4 sw_64 生态 | 号段/工具链异常 | A-32 预留 1,000 行冗余；失败则 N-02 兼容层兜底 |")
P("| R-A5 桌面依赖 | UKUI 上游变更 | R2 全部走适配层新文件（ALK），不动 UKUI 主线 |")
P("")
P("**跟踪机制**：任务表逐行勾状态 → 每周对账「✅ 任务 LOC 和 vs 计划曲线」→ 每验收日出里程碑偏差报告；")
P("排程重算入口：`docs/docs-closed/agent-linux-dev/scripts/bp_seed.py`（改 WP/LOC/依赖）+ 同目录 `bp_gen.py`（重新生成本文件），账本永远由脚本产出、人工只改种子。")
P("")
P("---")
P("")
P(f"*施工图纸 v3.4 ｜ 由种子数据确定性生成（拆分、缩放、拓扑排程、示例代码模板均经脚本断言校验；preds⇄succs 双向依赖逐边对称断言通过）｜ 逐模块对账 0 差：基线 {BASE_LOC:,} + 补充 {len(SUPP)} 包 {SUPP_LOC:,} = {sum(TARGETS.values()):,} 行（§5.1 证据台账）｜ 每任务示例代码遵循 50-engineering-standards（§2.1）。*")

out="/tmp/bp_out.md"
open(out,"w",encoding="utf-8").write("\n".join(L)+"\n")
print(f"OK tasks={ntask} wps={len(wps)-ngate} gates={ngate} lanes={len(lanes)} maxraw={maxraw} caldays={maxcal if False else cal_of(maxraw)} loc={tot_loc}")
print(f"milestones:")
for r_ in ms_rows: print(" ",r_[0],r_[3])
print(f"critical path: {len(cp)} tasks, {date_of(cal_of(maxraw))}")
print("written:",out,"lines:",len(L))
