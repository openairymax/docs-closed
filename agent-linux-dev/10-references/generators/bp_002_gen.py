# -*- coding: utf-8 -*-
"""AirymaxOS 0.0.2 版任务方案生成器（bring-up 施工图纸）。

读主图纸种子（`bp_seed.py`）与主图纸引擎（`bp_gen.py`，复用其 LOC 缩放结果、任务拆分粒度与
§6.x.1 示例代码模板），按 0.0.2 的**显式范围裁定**（在范围 WP 白名单 + 替换/降级边登记）重算
依赖闭包与拓扑排程，输出到 `agent-linux-dev/` 下 `0.0.2-极境OS任务方案.md`。

设计约束（与主图纸 §1.2 原子化原则一致）：
  1. 0.0.2 不重算 LOC 缩放：直接沿用主图纸已定稿的「每 WP 实摊 LOC + 任务拆分」，保证 0.0.2 任务 ID
     与主图纸账本逐行可追溯（同一 WP 的分片序号与主图纸完全相同）。
  2. 每一条被旁路的依赖边必须在 `EDGE_REG` 中显式登记替换物，脚本断言完整性——缺登记直接报错退出，
     杜绝「静默删除依赖」造成的伪闭环（对应工程规范「严禁伪依赖语义」）。
  3. 新增模块 V（验收与实证）仅启用 5 个 WP，其 LOC/依赖取自《agentrt-linux验收实验任务卡草案》。
  4. 账本永远由脚本产出，人工只改种子（本文件的 `SCOPE_WHITELIST` / `EDGE_REG` / `CUT_REASON`）。
"""

import contextlib
import datetime
import importlib.util
import io
import os
import sys
from collections import defaultdict

_here = os.path.dirname(os.path.abspath(__file__))


def _load(mod_name, path):
    """按路径加载模块（不依赖包结构），返回模块对象。"""
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


# 主图纸种子（只读数据）；主图纸引擎（导入即生成 4.3MB 主账本到 /tmp，屏蔽其 stdout 噪声）。
seed = _load("bp_002_seed_view", os.path.join(_here, "bp_seed.py"))
_noise = io.StringIO()
with contextlib.redirect_stdout(_noise):
    bpg = _load("bp_002_engine_view", os.path.join(_here, "bp_gen.py"))

MASTER_WPS = bpg.wps           # id -> WP 对象（含已缩放的 .loc / .lane / .deps / .tasks）
MASTER_TASKS = bpg.tasks       # task id -> T 对象
MOD_ORDER = list(seed.WPS.keys())

# ============================================================================
# 1. 0.0.2 范围裁定
# ============================================================================

# 1.1 在范围 WP 白名单（按模块；模块内顺序沿用主图纸声明序，保证 §6 表布局与主图纸同构）。
SCOPE_WHITELIST = {
    "L": ["L-01", "L-03", "L-04", "L-09", "L-07", "L-11", "L-12", "L-14",
          "L-16", "L-05", "L-06", "L-19", "L-22", "L-23", "L-24", "L-31", "L-33"],
    "A": ["A-01", "A-20", "A-04", "A-02", "A-03", "A-05", "A-06", "A-10",
          "A-11", "A-23", "A-26", "A-30", "A-33", "A-38", "A-39", "A-40"],
    "B": ["B-01", "B-02", "B-03", "B-05", "B-06"],
    "C": ["C-03"],
    "K": ["K-01"],
    "M": ["M-01", "M-02", "M-04", "M-03", "M-14", "M-13", "M-18", "M-24",
          "M-23", "M-15", "M-17"],
    "P": ["P-01"],
    "R1": ["R1-01", "R1-02", "R1-03", "R1-04", "R1-05", "R1-06"],
    "V": ["V-01", "V-02", "V-03", "V-04", "V-11"],
}

# 1.2 新增模块 V（主图纸尚无 V 模块，其定义取自验收实验任务卡草案）。
#     字段：(id, 名称, LOC, 泳道, 前驱 WP)。V-04/V-11 的前驱已按 0.0.2 重裁
#     （原 V-04←V-10,M-17,J-08 → 0.0.2 V-04←V-03,M-17；原 V-11←V-09,R2-10,R1-06 → V-11←V-04,R1-06）。
V_WPS = [
    ("V-01", "OS-ACC-RT 标准与执行器（osaccrt）", 1460, "VAL1", ["L-19"]),
    ("V-02", "镜像构建触发与启动冒烟（image-smoke）", 1160, "VAL1", ["V-01", "M-13"]),
    ("V-03", "kickstart 装机实测（kickstart）", 1140, "VAL1", ["V-02", "M-03"]),
    ("V-04", "E2E 冒烟执行（e2e-smoke）", 1450, "VAL1", ["V-03", "M-17"]),
    ("V-11", "竣工回归重放与总判定（final-regression）", 1385, "VAL1", ["V-04", "R1-06"]),
]

# 1.3 显式替换/降级边登记表：consumer(在范围) ← bypass(主图纸原前驱,范围外) ⇒ 替换前驱 repl。
#     脚本断言：任何「在范围 WP 指向范围外 WP」的前驱边都必须在此表登记，否则报错退出。
#     repl 为替代前驱列表；空列表表示该依赖被**直接裁撤**（消费者不再需要该前驱能力）。
EDGE_REG = [
    dict(consumer="L-19", bypass="L-17", repl=["L-07"],
         orig="KCSAN/UBSAN 集成 → 文档站 → 容器化环境 → aucs-gen → OS-ACC runner 链",
         impact="E1-02（UEFI/BIOS 双固件冷启动）、E1-04（kickstart 全自动装机）的执行器宿主",
         gap="sanitizer 动态分析证据；由 0.1.x 的 L-17 + L-13/L-15 链补齐"),
    dict(consumer="A-33", bypass="A-32", repl=["A-30"],
         orig="A-33←A-32（sw_64 接线）←A-31（arm64 接线）←A-30（x86_64 接线）",
         impact="内核 airy 子系统的 initcall 装载与模块装配（B1 里程碑）",
         gap="arm64/sw_64/riscv 接线（A-31/A-32/A-36）；由 0.1.x 多架构轨补齐"),
    dict(consumer="M-14", bypass="M-11", repl=["M-04"],
         orig="M-14←M-11（制品签名）←M-08（ostree）←M-07（livepatch）←M-04",
         impact="基础镜像组装（E1-01 镜像制品、B2 发行版可构建可安装）",
         gap="制品签名/A/B 分区原子更新/livepatch；由 0.1.x 的 M-07/M-08/M-11 链补齐"),
    dict(consumer="M-15", bypass="M-12", repl=["M-04"],
         orig="M-15←M-12（repo 管理与分发）←M-10（SBOM）←M-09（可重现构建）←M-06←M-05←M-03",
         impact="桌面镜像组装（E2-01 UKUI 会话登录链、B4 首启与桌面就绪）",
         gap="内网 repo 分发/SBOM/可重现构建；0.0.2 直接以 openEuler 24.03-LTS-SP2 官方仓库 + 本仓 comps 组装"),
    dict(consumer="M-18", bypass="H-04", repl=[],
         orig="M-18←H-04（服务编排引擎）",
         impact="airy 守护进程的 systemd 兼容单元",
         gap="系统服务编排引擎（H-04）的托管式编排；0.0.2 由 systemd 直接管理 airy 单元，编排能力 0.1.x 落地"),
    dict(consumer="R1-06", bypass="G-09", repl=[],
         orig="R1-06←G-09（gateway_d API 网关）",
         impact="桌面生态入口唯一性（六条集成铁律第②条）",
         gap="Gateway 唯一代理入口；0.0.2 无 Gateway（G-09 不在范围），仅执行 kylin-ai* 服务 mask，"
             "入口唯一性由 0.1.x 的 G-09 + R1-06 全链兑现"),
]

# 1.4 能力裁撤登记（模块级 + 关键 WP 级）；键为范围外 WP id，值为裁撤理由。
MODULE_CUT_REASON = {
    "D": "可观测性与审计（A-ULP）整模块后置：0.0.2 以 journald + pstore 承接最小崩溃取证，A-ULP 环形缓冲与哈希链在 0.1.x 落地",
    "E": "内存管理（rovol/分层/回收）整模块后置：0.0.2 以 stock 内核页回收与 ext4 根卷承接，rovol/分层/记忆运维在 0.1.x 落地",
    "F": "认知运行时整模块后置：0.0.2 不启用 CLT/Wasm/推理桥，airymaxhub 侧 agentrt 以既有用户态运行",
    "G": "云原生控制面整模块后置：0.0.2 无 gateway_d/CNI/CSI/调度器扩展，桌面直连后端服务",
    "H": "系统服务与 DevStation 整模块后置：0.0.2 不做运维门户与多集群，运维面由 systemd-analyze/journalctl 承接",
    "I": "驱动框架与设备总线整模块后置：0.0.2 沿用 openEuler 主线驱动栈，agent_bus/VFIO/IOMMU 在 0.1.x 落地",
    "J": "质量保证与形式化验证整模块后置：0.0.2 的验收由模块 V 执行器承接，KUnit 聚合/CBMC/TLA+/渗透套件在 0.1.x 落地",
    "N": "兼容性层整模块后置：0.0.2 以 x86_64 单架构 + 上游 ABI 稳定为基线，不建转译表与 sw_64 兼容",
    "O": "性能工程整模块后置：0.0.2 只做功能贯通不做性能门禁，NFR-P-001/002/004/006 实测在 0.1.x 由模块 V 承接",
    "Q": "应用生态整模块后置：0.0.2 不建应用商店/TaskFlow/部署器，生态接入在 0.1.x 落地",
    "R2": "UKUI 桌面主体（应用套件）整模块后置：0.0.2 只需「桌面能进入」，窗口管理/文件管理/设置面板/监控面板在 0.1.x 落地",
}

CUT_REASON = {
    # A
    "A-07": "IPC 快路径 C-S0~S6 阶段", "A-08": "IPC 快路径 C-S7~S12 阶段",
    "A-09": "io_uring_cmd 桥接与背压", "A-18": "零拷贝描述符与页引用管理",
    "A-12": "per-agent 调度主路径", "A-13": "调度策略映射", "A-14": "亲和与拓扑映射",
    "A-15": "dispatch 决策与抢占", "A-16": "CBS 带宽核算", "A-17": "SC 捐赠调度",
    "A-19": "per-agent CPU 账户与记账", "A-21": "hrtimer 精确窗口", "A-22": "suspend/resume 协同",
    "A-29": "budget enforcement 与降级", "A-35": "超节点 Token 预算池",
    "A-24": "锁改造 raw_spin", "A-25": "die_notify 与故障隔离", "A-27": "epoch 回收",
    "A-28": "freeze 原语", "A-34": "KABI 符号导出与稳定追踪",
    "A-31": "arm64 接线", "A-32": "sw_64 接线", "A-36": "riscv 架构接线", "A-37": "printk hook 注册与桥",
    # B
    "B-04": "沙箱机制（seccomp+LSM）", "B-07": "MAC 标签强制访问控制", "B-08": "capability 验证快速路径",
    "B-09": "sec_d 服务接口", "B-10": "安全审计 hook 点位", "B-11": "LSM 钩子槽位管理",
    "B-12": "namespace 隔离集成", "B-13": "SGX attestation", "B-14": "TDX 适配", "B-15": "SEV-SNP",
    "B-16": "VirtCCA", "B-17": "SM3/SM4 算法内核", "B-18": "SM2/SM9 算法内核", "B-19": "Vault 密钥管理",
    "B-20": "rovol 快照加密", "B-21": "凭证 epoch 联动", "B-22": "安全回归 KUnit 套件",
    "B-23": "agent 输入净化", "B-24": "io_uring 安全加固", "B-25": "侧信道防护",
    "B-26": "Cupolas 网络穹顶", "B-27": "零信任网络架构", "B-28": "Landlock 网络访问控制",
    "B-29": "LSM 审计事件上报", "B-30": "COMPLAIN 学习模式",
    # C
    "C-01": "Micro-Supervisor 内核侧核心", "C-02": "freeze 状态机与恢复点", "C-04": "fault 采集管道",
    "C-05": "macro_d 裁决引擎", "C-06": "裁决规则语言与解析", "C-07": "裁决执行器",
    "C-08": "A-UCS schema 与版本树", "C-09": "A-UCS 配置下发", "C-10": "配置回滚与灰度",
    "C-11": "aucs CLI", "C-12": "watchdog 与自杀保护", "C-13": "恢复动作库",
    "C-14": "内核/用户态协同测试", "C-15": "Reconciliation 执行器",
    # K
    "K-02": "用户态 VFS 核心", "K-03": "vfs_d 文件系统守护", "K-04": "用户态网络栈 TCP/IP",
    "K-05": "net_d 网络守护进程", "K-06": "dev_d 设备守护进程", "K-07": "sec_d 策略守护",
    "K-08": "audit_d 审计守护", "K-09": "sched_d 调度守护", "K-10": "superv-client 库",
    "K-11": "服务注册与发现", "K-12": "用户态服务编排测试", "K-13": "time_d 时间服务",
    "K-14": "统一告警通道", "K-15": "libvfio 用户态库",
    # L
    "L-08": "OS-ACC 验收 runner", "L-10": "aucs-gen 配置模板生成", "L-13": "容器化构建环境",
    "L-15": "文档站与契约文档生成", "L-17": "KCSAN/UBSAN 集成", "L-18": "perf CI 基准回归",
    "L-20": "IDE 集成配置", "L-21": "DCO/commit 钩子", "L-25": "[DSL] 降级块生成",
    "L-26": "AIRY_VERIFICATION 开关", "L-27": "上游社区追踪", "L-28": "双语文档一致性校验",
    "L-29": "airy-commons 公共库", "L-30": "Rust 内核模块支持", "L-32": "Grafana 运维看板模板",
    # M
    "M-05": "dnf 插件扩展", "M-06": "anaconda 安装器集成", "M-07": "livepatch 框架集成",
    "M-08": "ostree/rpm-ostree 原子更新", "M-09": "可重现构建", "M-10": "SBOM 生成",
    "M-11": "制品签名体系", "M-12": "repo 管理与分发", "M-16": "OTA 更新通道",
    "M-19": "PXE 网络安装", "M-20": "SBOM 查询与 CVE 对账", "M-21": "迁移工具", "M-22": "journald 兼容/双实例",
    # P
    "P-02": "fcitx5 输入法集成", "P-03": "GB18030 全覆盖实现", "P-04": "时区/locale 体系",
    "P-05": "文档格式兼容", "P-06": "字体与打印栈", "P-07": "无障碍支持",
    "P-08": "等保/信创合规审计项", "P-09": "行业标准对齐报告", "P-10": "printk 多语言消息表",
    "P-11": "错误码生成器", "P-12": "错误消息 gettext 集成", "P-13": "中英双语文档同步治理",
}

# 1.5 里程碑：0.0.2 专用的 bring-up 里程碑（锚点 WP = 该 WP 全部任务 ✅）。
MILESTONES_002 = [
    ("B0", "工具链与契约就绪", ["L-04", "A-11"]),
    ("B1", "内核 airy 子系统贯通（x86_64）", ["A-33", "B-03", "C-03"]),
    ("B2", "发行版可构建可安装", ["M-02", "M-04", "M-03"]),
    ("B3", "镜像与装机实测通过", ["M-13", "V-03"]),
    ("B4", "首启与 UKUI 桌面就绪", ["M-17", "R1-05"]),
    ("B5", "0.0.2 竣工验收（OS-ACC-RT 子集）", ["V-11"]),
]

# ============================================================================
# 2. 构建 0.0.2 WP 集（沿用主图纸实摊 LOC 与任务拆分）
# ============================================================================

SCOPE_SET = {wid for ids in SCOPE_WHITELIST.values() for wid in ids if wid != "V"}
for m, ids in SCOPE_WHITELIST.items():
    if m == "V":
        continue
    for wid in ids:
        assert wid in MASTER_WPS, f"白名单 WP 不存在于主图纸: {wid}"

# 2.1 注册模块 V 的 WP 与任务到引擎命名空间（供 code_lines 复用同一套模板）
for vid, vname, vloc, vlane, vdeps in V_WPS:
    assert vid not in MASTER_WPS, f"V WP 与主图纸冲突: {vid}"
    w = bpg.WP(vid, "V", vname, vloc, vlane, vdeps, False)
    w.loc = vloc
    locs = bpg.split(vloc)
    n = len(locs)
    for k, lv in enumerate(locs):
        if n == 1:
            nm = f"{vname}（整包：接口+实现+测试）"
            art = "单文件完整实现 + 内联 pytest + 证据包 schema"
        elif k == 0:
            nm = f"{vname}：接口与类型（1/{n}）"
            art = "执行器模块：类型/函数签名 + Google docstring（不含实现）"
        elif k == n - 1:
            nm = f"{vname}：单元测试与文档（{n}/{n}）"
            art = "pytest 用例 + 证据包 schema 校验 + 复现脚本 + DoD 收口"
        else:
            nm = f"{vname}：实现段（{k + 1}/{n}，主逻辑与错误路径）"
            art = ".py 实现源文件（本段逻辑 + 错误路径）"
        assert 100 <= lv <= 200, f"{vid}-{k + 1} loc={lv} 越界"
        t = bpg.T()
        t.id = f"T{vid}-{k + 1:02d}"
        t.wp = vid
        t.idx = k
        t.name = nm
        t.loc = lv
        t.dur = 1
        t.art = art
        w.tasks.append(t.id)
        MASTER_TASKS[t.id] = t
    MASTER_WPS[vid] = w
    bpg.wslug[vid] = bpg._slug(w)

# 2.2 V 模块的语言路由：执行器/判定/取证 → Python+pytest（对齐验收规程草案 §1.4）
_orig_art_lang = bpg._art_lang
_M_art_lang = lambda w: "python" if w.mod == "V" else _orig_art_lang(w)
bpg._art_lang = _M_art_lang

MOD002 = [m for m in MOD_ORDER if m in SCOPE_WHITELIST] + ["V"]
WP002 = {wid: MASTER_WPS[wid] for m in SCOPE_WHITELIST for wid in SCOPE_WHITELIST[m]}
assert len(WP002) == sum(len(v) for v in SCOPE_WHITELIST.values())

# 2.3 裁撤理由完整性：范围外 WP（仅限在范围模块内的）必须逐项登记理由
for _m in MOD002:
    if _m == "V":
        continue
    for _wid in [i for (i, _, _, _, _) in seed.WPS[_m] if i not in SCOPE_WHITELIST[_m]]:
        assert _wid in CUT_REASON, f"在范围模块 {_m} 的裁撤 WP 缺登记理由: {_wid}"

# ============================================================================
# 3. 依赖重裁：替换/降级边逐条落地 + 完整性断言
# ============================================================================

REPL_MAP = {(e["consumer"], e["bypass"]): e["repl"] for e in EDGE_REG}
dep002 = {}
bypass_edges = []
for wid, w in WP002.items():
    kept = []
    for d in w.deps:
        if d in WP002:
            if d not in kept:
                kept.append(d)
            continue
        assert (wid, d) in REPL_MAP, (
            f"未登记的旁路边：{wid} <- {d}（范围外）。"
            f"必须在本文件 EDGE_REG 中显式登记替换物后方可越过。")
        bypass_edges.append((wid, d))
        for r in REPL_MAP[(wid, d)]:
            assert r in WP002, f"替换前驱不在范围: {wid} -> {r}"
            if r not in kept:
                kept.append(r)
    dep002[wid] = kept

assert len(bypass_edges) == len(EDGE_REG), (
    f"登记表 {len(EDGE_REG)} 条，实际旁路边 {len(bypass_edges)} 条：{bypass_edges}")
assert set(bypass_edges) == set(REPL_MAP), (set(bypass_edges) ^ set(REPL_MAP))

# ============================================================================
# 4. 泳道序列重建（同泳道资源串行 + 逻辑依赖边）
# ============================================================================

lanes002 = defaultdict(list)
for ln, seq in bpg.lanes.items():
    f = [x for x in seq if x in WP002]
    if f:
        lanes002[ln] = f
lanes002["VAL1"] = ["V-01", "V-02", "V-03", "V-04", "V-11"]

preds = defaultdict(list)
succs = defaultdict(list)


def _add(a, b):
    if a not in preds[b]:
        preds[b].append(a)
        succs[a].append(b)


for ln, seq in lanes002.items():
    for a, b in zip(seq, seq[1:]):
        _add(WP002[a].tasks[-1], WP002[b].tasks[0])
for wid, w in WP002.items():
    for d in dep002[wid]:
        _add(WP002[d].tasks[-1], w.tasks[0])
for wid, w in WP002.items():
    for a, b in zip(w.tasks, w.tasks[1:]):
        _add(a, b)

TASKS002 = {tid: MASTER_TASKS[tid] for w in WP002.values() for tid in w.tasks}

for a in TASKS002:
    for b in preds[a]:
        assert a in succs[b], f"前驱/后继不对称: {b} -> {a}"
    for b in succs[a]:
        assert a in preds[b], f"前驱/后继不对称: {a} -> {b}"

wp_succ002 = {wid: sorted(x for x in WP002 if wid in dep002[x]) for wid in WP002}

# ============================================================================
# 5. 拓扑排程 + 关键路径
# ============================================================================

_day, _st = {}, {}


def _dfs(v):
    st = _st.get(v, 0)
    if st == 2:
        return _day[v]
    if st == 1:
        raise RuntimeError(f"依赖环涉及 {v}")
    _st[v] = 1
    d = 1
    for p in preds[v]:
        d = max(d, _dfs(p) + TASKS002[p].dur)
    _day[v] = d
    _st[v] = 2
    return d


for v in TASKS002:
    _dfs(v)
finish = {v: _day[v] + TASKS002[v].dur - 1 for v in TASKS002}
maxraw = max(finish.values())

START = datetime.date(2026, 11, 2)


def cal_of(r):
    return r + (r - 1) // 10


def date_of(c):
    return START + datetime.timedelta(days=(c - 1) + 2 * ((c - 1) // 5))


assert START.weekday() == 0

_last = max(TASKS002, key=lambda v: finish[v])
CP = []
_v = _last
while True:
    CP.append(_v)
    if not preds[_v]:
        break
    _v = max(preds[_v], key=lambda p: finish[p])
CP.reverse()

by_raw = defaultdict(list)
for v in TASKS002:
    by_raw[_day[v]].append(v)
maxcal = cal_of(maxraw)
day_tasks = {}
for rr in range(1, maxraw + 1):
    day_tasks.setdefault(cal_of(rr), []).extend(sorted(by_raw.get(rr, [])))
rows = []
_prev = None
for cc in sorted(day_tasks):
    if _prev is not None and cc > _prev + 1:
        for gap in range(_prev + 1, cc):
            rows.append((gap, date_of(gap), "—", "验收日（回归/门禁检查，无开发任务）"))
    ids = day_tasks[cc]
    rows.append((cc, date_of(cc), str(len(ids)), ", ".join(ids)))
    _prev = cc

# ============================================================================
# 6. 对账统计
# ============================================================================

TOT_LOC = sum(t.loc for t in TASKS002.values())
NTASK = len(TASKS002)
NWP = len(WP002)
for t in TASKS002.values():
    assert 100 <= t.loc <= 200, f"{t.id} loc={t.loc}"

mod_stat = []
for m in MOD002:
    ws = [WP002[i] for i in SCOPE_WHITELIST[m]]
    ts = [t for w in ws for t in w.tasks]
    st = min(_day[t] for t in ts)
    en = max(_day[t] + TASKS002[t].dur - 1 for t in ts)
    mod_stat.append((m, len(ws), len(ts), sum(TASKS002[t].loc for t in ts),
                     sorted({w.lane for w in ws}), st, en))
mod_stat_sorted = sorted(mod_stat, key=lambda r: r[5])

ms_rows = []
for mid, mname, anchors in MILESTONES_002:
    d = max(finish[t] for a in anchors for t in WP002[a].tasks)
    ms_rows.append((mid, mname, ", ".join(anchors), date_of(cal_of(d)), d))


def _lane_adj(wid):
    seq = lanes002[WP002[wid].lane]
    k = seq.index(wid)
    return (seq[k - 1] if k > 0 else None, seq[k + 1] if k + 1 < len(seq) else None)


# ============================================================================
# 7. 文档生成
# ============================================================================

L = []
P = L.append

P("# AirymaxOS 0.0.2 版任务方案（OS bring-up 施工图纸）")
P("")
P("> **版本 v0.0.2** ｜ 2026-10-14 ｜ 密级：内部机密（docs-closed）")
P(">")
P("> Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.")
P(">")
P("> 本方案是《agentrt-linux开发路线和进度.md》（v3.4，下称**主图纸**）在 **0.0.2 bring-up 版本**上的施工展开，")
P("> 由 `10-references/generators/bp_002_gen.py` 读主图纸种子 + 引擎确定性生成——**账本永远由脚本产出，人工只改种子**。")
P(">")
P("> 0.0.2 任务目标（用户口径，逐字）：**初步实现完整的 AirymaxOS；OS 能正常安装；OS 能正常运行；")
P("> OS 的 UKUI 桌面也能正常进入。**")
P(">")
P("> **本版与主图纸的关系**：不是子集截断，而是**经显式替换/降级的内在重裁轨（re-scoped bring-up）**——")
P("> 每一条被旁路的依赖边在 §2.2 逐条登记替换物，每一处能力裁撤在 §2.3 逐项登记理由。")
P("> 生成器断言：任何「在范围 WP 指向范围外 WP」的前驱边，若未在 §2.2 登记，直接报错退出——")
P(f"> 本版实际旁路边 **{len(bypass_edges)} 条**，登记 **{len(EDGE_REG)} 条**，逐边一一对应。")
P("")
P("## 1. 定位与基线")
P("")
P("### 1.1 0.0.2 目标与验收口径")
P("")
P("0.0.2 的唯一目标是把 AirymaxOS 从「文档就绪」推进到「**可装机、可冷启动、可进入 UKUI 桌面**」：")
P("")
P("| 目标 | 可观测判据 | 承接实验 |")
P("|---|---|---|")
P("| ① 初步实现完整的 AirymaxOS | 内核 airy 子系统（4 个 syscall + Badge + ipc_ring + Folding）在 x86_64 贯通并装载；安全基座（LSM+CNode+capability）生效 | B1 里程碑（OS-CHK 静态门禁；运行态 E4-01 不在 0.0.2 启用集） |")
P("| ② OS 能正常安装 | kickstart 全自动装机 3 连测成功率 100%；装机日志与分区校验齐备 | E1-04 / V-03 |")
P("| ③ OS 能正常运行 | UEFI/BIOS 双固件冷启动成功、串口无 panic；systemd-analyze 关键链 < 30s；关键单元 100% active | E1-02 / E1-03 / E2-04 |")
P("| ④ UKUI 桌面能正常进入 | lightdm/greeter/会话三级登录成功；会话日志与就绪探针齐备 | E2-01 / V-04 |")
P("")
P("> 验收规程（六步：准备/执行/取证/判定/复核/归档）与四态判定（PASS/FAIL/WAIVED/BLOCKED）")
P("> 沿用《agentrt-linux验收实验任务卡草案》§3，本方案不另立口径。")
P("")
P("### 1.2 与版本谱系的关系")
P("")
P("| 版本 | 定位 | 与 0.0.2 的关系 |")
P("|---|---|---|")
P("| **0.1.1** | 文档奠基（方案库 185 篇 + 50 工程规范 + 账本对账 0 差），综合成熟度 93%「有条件 Go」 | 0.0.2 的直接输入：主图纸 §1.3 的 Phase 0 五项已 ✅，本版不改其结论 |")
P("| **0.0.2** | **bring-up 版本（本方案）**：最小可运行、可安装、可进桌面的闭环 | 自行定义；不替代 0.1.1 文档基线 |")
P("| **1.0.1** | 全面开发（施工轨 S0~S8，19 模块 426,124 行 / 3,340 任务 / 446 施工日） | 0.0.2 是其**前哨切片**：0.0.2 的每个 WP/任务均取自 1.0.1 账本，不新造编号体系 |")
P("")
P("### 1.3 已落地资产基线（`agent-linux` 管理仓实测，2026-10-14）")
P("")
P("0.0.2 必须建立在**已有资产**上排程，不得把已完成项重复列为待建：")
P("")
P("| 资产 | 位置 | 状态 | 对 0.0.2 的意义 |")
P("|---|---|---|---|")
P("| [SC] 契约头 | `kernel/include/uapi/linux/airymax/`（ipc.h / sched.h / error.h / cognition_types.h / lsm_types.h / memory_types.h / security_types.h / log_types.h / bpf_struct_ops.h / uapi_compat.h / syscalls.h / syscall.xml） | 已落地 | 直接支撑 §6.1 中 A-26/A-38/A-39/A-40 的契约收口 |")
P("| security/airy 实现 | `kernel/security/airy/` 11 个 `.c`（airy_lsm / airy_cap_* / airy_eventfd / airy_ipc_freeze / airy_superv_lsm 等）+ 2 测试 | 已落地 | 直接支撑 B-01/B-02/B-03/B-05 的补全收口 |")
P("| 内核装配点 | `kernel/init/airy_core.c`、`kernel/include/airymax/{build_types.h,kconfig_types.h}` | 已落地 | 直接支撑 A-33 的 initcall 装配 |")
P("| codegen 与 ABI 工具 | `tools/codegen`、`tools/sc-tri-compile`、`tools/abi-check`、`tools/validate-ssot.py`、`tools/parse-tap.py`、`tools/kunit-tap-diff.py`、`tools/await-agentrt-ci.py` | 已落地 | 直接支撑 L-01/L-04/L-05/L-06/L-31 的收口 |")
P("| DSL 编译器 | `tools/dsl/`（lexer/parser/semantics/codegen/compile + 6 个 pytest + 决策表模板） | 已落地 | 直接支撑 L-03 与 B-06 的策略编译器 |")
P("| 发行版工件 | `distro/{kickstart,comps,ostree,desktop,lockfile,ci}/`（含 `airymaxos-workstation.ks`、`airymaxos-comps.xml`、`airymax-desktop.slice`、`lockfile-openEuler-24.03-LTS-SP2.yaml`） | 已落地 | 直接支撑 M-03/M-04/M-15/R1-04 的收口 |")
P("| CI 流水线 | `.github/workflows/`（ci-airy / ci-kernel / codegen-verify / dsl-verify / sc-dual-ci / ssot-validate / release / nightly / mgmt-orchestrator） | 已落地 | §10 的流水线矩阵直接复用，不新建 |")
P("| 叶子仓拓扑 | `.gitmodules` 9 个 submodule（kernel 分支 `ALK-6.6-dev`；memory/security/cognition/services/system/cloudnative/tests-linux/distro 分支 `dev/hubs-01`） | 已落地 | §10 的 releases 发行矩阵直接复用 |")
P("| 标准登记 | `ssot-registry.yaml` v0.2.8（OS-IRON-001~016） | 已落地 | 0.0.2 的规范引用以 OS-IRON 编号为准 |")
P("| Phase 0 | P0-1 `0207ff0` / P0-2 `ef6103e` / P0-3 `8fe4e7d` / P0-4 `7813134` / P0-5 `dd990c6` | 已 ✅ | 不计入 0.0.2 账本 |")
P("")
P("> **已识别技术债（须在 0.0.2 内消除）**：`distro/ci/run-smoke.sh` 的 `t1_tauri_window` / `t2_input_method` /")
P("> `t3_pipewire` / `t4_cgroup_freeze` 四函数当前为 skeleton 桩（`echo \"1..0 # Tn skeleton — TODO implement on DevStation\"`），")
P("> 与「严禁桩实现」冲突，登记为 TD-01（见 §11），由 R1-04/R1-05/M-15 的真实检测任务替换。")
P("")
P("### 1.4 原子化原则（继承主图纸 §1.2，0.0.2 附加两条）")
P("")
P("1. **100~200 行/任务**：单任务 = 单文件、单函数或单小组件，一次评审可看完（脚本逐任务断言）；")
P("2. **契约先行**：接口先由 L-01/L-04 生成，人只写实现，杜绝手写 ABI 漂移；")
P("3. **ALK 铁律**：只新增文件、不改主线；每任务 diff 限定在 airy/ 新文件与号段接线点内；")
P("4. **任务即提交**：一个任务 = 一个 commit = 一次 PR，标题遵循 `submitting-patches.rst`（`airy/xxx: …`），")
P("   修复类落款 `Decheng Li <lidecheng@spharx.cn>`、功能类落款 `Liren Wang <wangliren@spharx.cn>`；")
P("5. **DoD 四项**：实现 + KUnit/kselftest 挂点 + OS-CHK 门禁通过 + 契约快照更新，四项缺一不勾选；")
P("6. **设计空洞门禁（GT-*）**：0.0.2 **不触发任何 GT-*** —— 6 个门禁（GT-BCC/GT-BGM/GT-FW/GT-DS/GT-V/GT-NET）")
P("   的解锁方（B-13/B-17/F-04/H-11/K-02/K-04）**全部在范围外**（脚本可核对，见 §2.3）；")
P("7. **【0.0.2 附加】禁止桩实现**：不得出现 `TODO`/`stub`/`skeleton`/占位返回；任何未实现能力必须")
P("   **显式降级**（返回 `-ENOTSUP`/`-ENOSYS` 并登记错误码），而非静默桩；")
P("8. **【0.0.2 附加】范围外能力不得越界调用**：模块 V 的执行器只驱动在范围 WP 的产物，")
P("   范围外能力一律以 BLOCKED/降级登记，不得伪造证据。")
P("")
P("### 1.5 工程总账（0.0.2 范围）")
P("")
P(f"- 净新增代码总量：**{TOT_LOC:,} 行**（{NWP} 个 WP；取自主图纸实摊 LOC 口径，见 §5）")
P(f"- 原子任务：**{NTASK} 个**，每个任务净增代码严格控制在 **100~200 行**（脚本断言校验通过）")
P(f"- 泳道：**{len(lanes002)} 条**（每泳道每施工日承担 1 个原子任务）")
P(f"- 排程：起始 **{START.isoformat()}**（周一，为主图纸 Day-1（2026-10-05）之后的 bring-up 独立轨起算日；")
P("  §1.3 已落地资产直接复用、不重复排程）；")
P(f"  每 10 个施工日插入 1 个验收日，周末不排任务；共 **{maxraw}** 个施工日")
P(f"  （约 {maxcal} 个工作日，跨度至 **{date_of(maxcal).isoformat()}**）；关键路径 **{len(CP)}** 个任务。")
P("")
P("## 2. 范围裁定")
P("")
P("### 2.1 在范围 WP 白名单（含依赖重裁对照）")
P("")
P("> 「主图纸原前序」列为主图纸种子中的显式逻辑前驱；「0.0.2 前序」列为本方案重裁后的前驱，")
P("> 两列不同处即 §2.2 登记的替换/降级边。")
P("")
P("| 模块 | WP | 名称 | 主图纸 LOC | 任务数 | 泳道 | 主图纸原前序 | 0.0.2 前序 |")
P("|---|---|---|---|---|---|---|---|")
for m in MOD002:
    for wid in SCOPE_WHITELIST[m]:
        w = WP002[wid]
        o = ",".join(w.deps) if w.deps else "—"
        n = ",".join(dep002[wid]) if dep002[wid] else "—"
        mark = " **(重裁)**" if o != n else ""
        P(f"| {m} | {wid} | {w.name} | {w.loc:,} | {len(w.tasks)} | {w.lane} | {o} | {n}{mark} |")
P(f"| — | **合计** | {NWP} 个 WP | **{TOT_LOC:,}** | **{NTASK}** | — | — | — |")
P("")
P("### 2.2 显式替换/降级边登记表（逐条可核）")
P("")
P("> 生成器对每个在范围 WP 的每条前驱边做检查：若该前驱在范围外，必须在下列表中登记替换物，否则报错退出。")
P(f"> 本版共 **{len(EDGE_REG)}** 条旁路边，全部登记如下，无遗漏、无多余（脚本双向集合断言通过）。")
P("")
P("| # | 消费者（在范围） | 被旁路 WP（范围外） | 主图纸原链 | 0.0.2 替换前驱 | 受影响能力 | 未覆盖项与补齐版本 |")
P("|---|---|---|---|---|---|---|")
for k, e in enumerate(EDGE_REG, 1):
    r = ",".join(e["repl"]) if e["repl"] else "**（直接裁撤）**"
    P(f"| {k} | {e['consumer']} | {e['bypass']} | {e['orig']} | {r} | {e['impact']} | {e['gap']} |")
P("")
P("### 2.3 能力裁撤登记")
P("")
P("> 模块级整裁 = 该模块全部 WP 后置到 0.1.x；WP 级裁撤 = 所在模块在范围内，但该 WP 单独裁撤。")
P("> 「处置」列统一为「0.1.x 落地」，本表的作用是**把裁撤显式化**，避免被误读为已完成。")
P("")
P("| 模块 | 裁撤粒度 | 裁撤 WP | 名称 | 主图纸 LOC | 裁撤理由 |")
P("|---|---|---|---|---|---|")
for m in MOD_ORDER:
    if m not in SCOPE_WHITELIST:
        ids = [i for (i, _, _, _, _) in seed.WPS[m]]
        loc = sum(w.loc for w in MASTER_WPS.values() if w.mod == m)
        P(f"| {m} | 模块整裁 | {len(ids)} 个 | {seed.MODULE_NAMES[m]} | {loc:,} | {MODULE_CUT_REASON[m]} |")
        continue
    for wid in [i for (i, _, _, _, _) in seed.WPS[m] if i not in SCOPE_WHITELIST[m]]:
        w = MASTER_WPS[wid]
        P(f"| {m} | WP 级 | {wid} | {w.name} | {w.loc:,} | {CUT_REASON.get(wid, '0.0.2 不启用')}；0.1.x 落地 |")
P("")
P("### 2.4 新增模块 V 的依据与边界")
P("")
P("主图纸（v3.4）只有「仪器」（L-19 QEMU 农场 / M-13 镜像 CI），无一张「实验执行」卡，")
P("真机 bring-up 链 0 命中——此为 0.0.2 目标的**直接阻塞项**。故本方案引入《agentrt-linux验收实验任务卡草案》")
P("定义的**模块 V（验收与实证，泳道 VAL1）**，但只启用其中 5 个 WP：")
P("")
P("| WP | 名称 | LOC | 前驱（0.0.2） | 承接实验 |")
P("|---|---|---|---|---|")
for vid, vname, vloc, vlane, vdeps in V_WPS:
    exp = {"V-01": "OS-ACC-RT 规程与执行器（全部 E 矩阵的宿主）", "V-02": "E1-01/E1-02/E1-03",
           "V-03": "E1-04", "V-04": "E2-01/E2-04", "V-11": "E7（0.0.2 子集重放与四态总判定）"}[vid]
    P(f"| {vid} | {vname} | {vloc:,} | {','.join(vdeps)} | {exp} |")
P("")
P("**边界**：V-05（Soak）/ V-06（chaos）/ V-07（渗透）/ V-08（性能）/ V-09（SMP-NUMA）/ V-10（ostree 原子更新）")
P("6 个 WP **不在 0.0.2 范围**——其前驱（J-09/J-15/O-07/O-08/M-16）全部在范围外。V-04、V-11 的前驱已按 §2.2 重裁。")
P("")
P("### 2.5 0.0.2 交付物定义（DoD 扩展）")
P("")
P("在标准 DoD 四项之外，0.0.2 增加「**运行证据**」一项（对模块 V 与装机/桌面相关任务强制）：")
P("")
P("| DoD 项 | 判据 | 证据形态 |")
P("|---|---|---|")
P("| D1 实现 | 代码合入且 checkpatch/sparse 绿 | 源文件 + CI 绿 |")
P("| D2 测试挂点 | KUnit / pytest / QtTest 用例挂入矩阵 | 测试文件 + TAP 输出 |")
P("| D3 OS-CHK 门禁 | `tools/validate-ssot.py` + `abi-check` + `sc-tri-compile` 通过 | 门禁报告 |")
P("| D4 契约快照 | [SC] 快照更新且三路编译一致 | 快照 diff |")
P("| **D5 运行证据（0.0.2）** | 镜像 sha256 + 冷启动日志 + 装机日志 + 会话日志，append-only 落盘 | `evidence/<date>/<exp-id>/` + `sha256` 链 |")
P("")
P("## 3. 任务卡规范")
P("")
P("每张任务卡（账本行）的字段含义与主图纸 §2 完全一致：")
P("")
P("```")
P("T<WP>-<序号> | 任务描述（WP 名 + 分片角色） | 产出物 | 净新增 LOC | 泳道 | 施工日/日历日 | 严格前驱 | 直接后继 | 状态")
P("```")
P("")
P("- **状态**：⬜ 未开工 / 🟨 进行中 / ✅ 已验收（初始全部 ⬜）；")
P("- **分片角色**：首片 = 接口与类型（头文件/原型，**禁写实现**）；中片 = 实现段（主逻辑 + 错误路径）；")
P("  末片 = 单元测试与文档（DoD 收口）。四类载体模板同样遵循此语义（元数据/根元素/[Unit] → 构建/条目/[Service] →")
P("  `%changelog`/根闭合/[Install] 收口）；")
P("- **产出物**：本任务合入后仓库中新增/更新的文件形态，评审按此验收，防止「实现（k/n）」式含糊任务；")
P("- **严格前驱 / 直接后继**：由同一份依赖图正反推导，脚本逐边断言双向对称；")
P("- **语言路由**：L 工具链/CI + V 执行器/判定/取证 → Python；R1/R2 → C++/Qt；")
P("  M 按名称路由（spec→RPM spec、comps/XML→XML、systemd/journald/自检服务→unit INI、dnf/插件→Python、其余→Bash）；")
P("  内核与其他用户态组件 → C。")
P("")
P("### 3.1 示例代码规范（对齐 50 工程规范）")
P("")
P("| 约定 | 规范来源 | 在示例中的体现 |")
P("|---|---|---|")
P("| 符号命名 `airy_<wp>_<slug>_*`，全局描述性命名 | OS-STD-CODE-001 | 函数与结构体名内嵌 WP 编号，跨任务可反查归属 |")
P("| 动作函数返回 `0 / -Exxx`，谓词函数返回 `bool` | OS-STD-CODE-030 | `airy_*_init()` 返 int，`airy_*_ready()` 返 bool |")
P("| 公共 API 必须 kernel-doc；Python 用 Google docstring | OS-STD-CODE-012 / 014 | 结构体与函数带 kernel-doc 注释块或 docstring |")
P("| include 顺序：系统头 → 架构头 → 本地头 | OS-STD-CODE-016 | `<linux/types.h>` 在前，本 WP 头文件其后 |")
P("| 头文件保护 `#ifndef _AIRY_<UP>_H` 与路径对应 | OS-STD-CODE-017 | 接口分片整段用 guard 包裹 |")
P("| 错误路径 goto 集中出口（C）/ 异常路径单一出口 | OS-STD-CODE-022 | 实现分片统一 `if (ret) goto err;` |")
P("| 内核内部类型用 `u32/u64`，UAPI 用 `__u32` | OS-STD-CODE-032 | 结构体字段用 `u32 state; u64 stamp_ns;` |")
P("| 禁 `strcpy/strncpy`，用 `strscpy` | OS-BAN-004 | 模板不含被禁接口 |")
P("| 禁 `%p` 打印裸指针 | OS-BAN-005 | 模板不出现裸指针打印 |")
P("| SPDX 双轨：内核 `GPL-2.0-only`，用户态 `AGPL-3.0-or-later OR Apache-2.0` | 12-license-policy | 每段首行按 WP 泳道自动选择许可证 |")
P("| 简洁文件头：SPDX 首行 + ≤20 行模块描述，随后直接 `#include` | OS-STD-STY-007 | 禁冗长版权块/作者列表/版本历史；文件头可用中文 |")
P("| ALK 铁律：只新增文件、不改主线 | OS-IRON-003 | 示例均为新文件形态（`airy/<wp>.c`） |")
P("")
P("**衔接机制**（同一 WP 内分片串行，符号级可编译）：")
P("")
P("1. **首片（接口与类型）**：定义 `struct airy_<wp>_ctx` 与全部原型，并 `#include` 其**逻辑前驱 WP** 的头文件；")
P("2. **实现段 k/n**：`airy_<wp>_impl_<k>()` 调用上一段 `airy_<wp>_impl_<k-1>()`（首段调用接口片声明的 `airy_<wp>_init()`），")
P("   错误路径统一 goto 出口；")
P("3. **末片（测试与文档）**：KUnit / pytest / QtTest 引用首片声明 + 各实现段符号，覆盖 `T<wp>-01 … T<wp>-(n-1)` 全链；")
P("4. 模块 V 的末片额外产出**证据包 schema 校验 + 复现脚本**（EX 型 DoD 扩展，见 §2.5）。")
P("")
P("> **接口分片的声明占位与 QG-03 判定口径**：Python/C++ 模板的接口分片以")
P("> `raise NotImplementedError(\"实现在 T<wp>-02 分片\")` 作编译粘合占位——这是分片串行的**声明手段**，")
P("> **必须在同一 WP 的下一分片（≤1 个任务）内被真实实现替换**；WP 末片收口时任何分片不得残留该占位，")
P("> 否则按 QG-03「桩实现」阻断验收。C/内核模板的接口分片仅声明原型（无函数体），不涉此判定。")
P("")
P("## 4. 模块与泳道")
P("")
P("### 4.1 模块账本（按计划开工先后排序）")
P("")
P("| 序 | 模块 | 名称 | WP | 任务 | LOC | 泳道 | 开工日 | 收口日 |")
P("|---|---|---|---|---|---|---|---|---|")
for k, (m, nw, nt, loc, lst, st, en) in enumerate(mod_stat_sorted, 1):
    P(f"| {k} | **{m}** | {seed.MODULE_NAMES.get(m, '验收与实证')} | {nw} | {nt} | {loc:,} |"
      f" {','.join(lst)} | {date_of(cal_of(st))} | {date_of(cal_of(en))} |")
P("")
P("### 4.2 泳道表（每泳道每日 1 任务；跨泳道可并行）")
P("")
P("| 泳道 | 职责 | WP | 任务 | LOC | 开工 | 收口 |")
P("|---|---|---|---|---|---|---|")
for ln in list(seed.LANE_DESC) + ["VAL1"]:
    seq = lanes002.get(ln, [])
    if not seq:
        P(f"| {ln} | {seed.LANE_DESC.get(ln, '验收与实证轨')} | 0 | 0 | 0 | — | — |")
        continue
    ts = [t for i in seq for t in WP002[i].tasks]
    st = min(_day[t] for t in ts)
    en = max(_day[t] + TASKS002[t].dur - 1 for t in ts)
    P(f"| {ln} | {seed.LANE_DESC.get(ln, '验收与实证轨')} | {len(seq)} | {len(ts)} |"
      f" {sum(TASKS002[t].loc for t in ts):,} | {date_of(cal_of(st))} | {date_of(cal_of(en))} |")
P("")
P("### 4.3 并行/串行规则")
P("")
P("- **可并行**：不同泳道之间、同泳道无链上关系的 WP 分片之间、契约已生成（L-04 ✅）后的任意实现任务之间。")
P("- **严格串行（硬依赖，0.0.2 主干）**：")
P("  1. `L-01 → L-03 → L-04`（codegen → DSL 编译 → [SC] 契约头三路编译校验）**先于一切内核实现任务**；")
P("  2. `A-01 → A-05 → A-06`（syscall 入口 → Badge → ipc_ring）先于 C/K 的接入层；")
P("  3. `A-10 → A-11 → L-09 → L-07`（Folding → 编译期校验 → 能力表生成 → CI 矩阵）先于一切门禁；")
P("  4. `L-19 → V-01 → V-02 → V-03 → V-04 → V-11`（农场 → 执行器 → 冒烟 → 装机 → 首启 → 总判定）；")
P("  5. 发行版主干 `M-01 → M-02 → M-04 → M-14 → M-13`，桌面支线 `M-14 → P-01 → R1-01 → R1-03 → R1-05`，")
P("     合流点 `M-23 ← M-04, R1-01` 与 `M-15 ← M-04, M-23, R1-02`，收口 `M-17 ← M-15`；")
P("  6. 各 WP 内部分片严格串行（接口分片 → 实现分片 → 测试分片）。")
P("- **资源串行（同泳道）**：同泳道任务不重叠；这是排程约束而非逻辑依赖，扩编泳道即可线性压缩工期。")
P("- **反例（禁止）**：范围外 WP 不得出现在任何在范围任务的「严格前驱」列——本版由 §2.2 登记表 + 脚本断言保证。")
P("")
P("### 4.4 关键路径（最长依赖链，决定最早完工日）")
P("")
_p = sum(TASKS002[t].loc for t in CP)
P(f"`{CP[0]}` → … → `{CP[-1]}`，共 {len(CP)} 个任务、{_p:,} 行，全程 {maxraw} 施工日 →")
P(f"最晚施工日 **{date_of(cal_of(maxraw))}**。")
P("")
P("| # | 任务 | 内容 | LOC | 施工日 | 日历日 |")
P("|---|---|---|---|---|---|")
for k, t in enumerate(CP, 1):
    tt = TASKS002[t]
    P(f"| {k} | {t} | {tt.name} | {tt.loc} | {_day[t]} | {date_of(cal_of(_day[t]))} |")
P("")
P("## 5. 账目对账")
P("")
P("> 0.0.2 **不重算 LOC 缩放**：直接沿用主图纸已定稿的每 WP 实摊 LOC，故同一 WP 的 LOC 与任务拆分")
P("> 与主图纸逐项相同，任务 ID 逐行可追溯。下表以「纳入 / 移出」口径对账。")
P("")
P("| 模块 | 主图纸模块总量 | 0.0.2 纳入 | 0.0.2 移出 | 纳入占比 |")
P("|---|---|---|---|---|")
_inc_total = 0
for m in MOD_ORDER:
    tgt = seed.TARGETS[m]
    inc = sum(TASKS002[t].loc for w in WP002.values() if w.mod == m for t in w.tasks)
    _inc_total += inc
    pct = "—" if tgt == 0 else f"{inc * 100 // tgt}%"
    P(f"| {m} | {tgt:,} | {inc:,} | {tgt - inc:,} | {pct} |")
_vloc = sum(TASKS002[t].loc for w in WP002.values() if w.mod == "V" for t in w.tasks)
P(f"| **V（0.0.2 新增）** | — | **{_vloc:,}** | — | — |")
_ma = sum(seed.TARGETS.values())
P(f"| **合计** | **{_ma:,}** | **{TOT_LOC:,}** | **{_ma - _inc_total:,}** | **{TOT_LOC * 100 // _ma}%** |")
P("")
P(f"- 0.0.2 净新增 **{TOT_LOC:,} 行** = 主图纸纳入 WP 实摊 **{_inc_total:,} 行** + 模块 V 新增 **{_vloc:,} 行**；")
P(f"- WP {NWP} 个（主图纸 365 个）+ 任务 {NTASK} 个（主图纸 3,340 个）；单任务 LOC 全部 ∈ [100, 200]；")
P(f"- 依赖图无环（拓扑排程求解成功，DFS 环检测通过）；前驱⇄后继逐边双向对称断言通过；")
P(f"- 旁路边 {len(bypass_edges)} 条，全部在 §2.2 登记（生成器集合断言通过）；")
P("- 0.0.2 不触发任何 GT-* 设计门禁（解锁方全部在范围外，见 §2.3）。")
P("")
P("## 6. 分模块施工任务账本")
P("")
P("> §6.0 为 WP 级双向邻接反查表（先审计工作包间的上下依赖），随后各模块先列 WP 表，再列全量任务明细")
P("> （日期为计划日历日）。")
P("")
P("### 6.0 WP 双向邻接反查表")
P("")
P("> **显式前序** = 0.0.2 重裁后的逻辑依赖（其 ✅ 是本包开工硬条件）；**后继（被依赖）** = 反查出的引用本包的 WP；")
P("> 两列由同一份依赖图正反推导，任何一条依赖边必须同时出现在前包的「后继」与后包的「前序」中（脚本逐边断言）；")
P("> **泳道前包/后包** 为同泳道资源串行序（非逻辑依赖）。0.0.2 显式前序为空的包仅 `L-01`（codegen 核心）——")
P("> Day-1 由此单点启动；`A-01`/`A-05`/`A-10`/`B-01`/`M-01` 等的「泳道前包」列显示其受契约（L-04）或")
P("> 泳道资源约束，非逻辑依赖。")
P("")
P("| WP | 模块 | 显式前序（逻辑） | 后继（被依赖） | 泳道 | 泳道前包 | 泳道后包 |")
P("|---|---|---|---|---|---|---|")
for m in MOD002:
    for wid in SCOPE_WHITELIST[m]:
        w = WP002[wid]
        lp, lsn = _lane_adj(wid)
        pd = ",".join(dep002[wid]) if dep002[wid] else "—"
        post = wp_succ002[wid]
        P(f"| {wid} | {m} | {pd} | {','.join(post) if post else '—'} | {w.lane} | {lp or '—'} | {lsn or '—'} |")
P("")
for k, m in enumerate(MOD002, 1):
    ws = [WP002[i] for i in SCOPE_WHITELIST[m]]
    nt = sum(len(w.tasks) for w in ws)
    loc = sum(TASKS002[t].loc for w in ws for t in w.tasks)
    mname = seed.MODULE_NAMES.get(m, "验收与实证")
    P(f"### 6.{k} 模块 {m} —— {mname}（{loc:,} 行 / {len(ws)} WP / {nt} 任务）")
    P("")
    P("| WP | 名称 | LOC | 泳道 | 前序 WP（逻辑） | 后继 WP（被依赖） | 任务数 | 计划窗口 |")
    P("|---|---|---|---|---|---|---|---|")
    for w in ws:
        st = min(_day[t] for t in w.tasks)
        en = max(_day[t] + TASKS002[t].dur - 1 for t in w.tasks)
        dep = ",".join(dep002[w.id]) if dep002[w.id] else "—"
        post = wp_succ002[w.id]
        P(f"| {w.id} | {w.name} | {w.loc:,} | {w.lane} | {dep} | {','.join(post) if post else '—'} |"
          f" {len(w.tasks)} | {date_of(cal_of(st))} ~ {date_of(cal_of(en))} |")
    P("")
    P("| 任务 ID | 内容 | 产出物 | LOC | 泳道 | 施工日 | 日历日 | 严格前驱 | 直接后继（阻塞） | 状态 |")
    P("|---|---|---|---|---|---|---|---|---|---|")
    for w in ws:
        for tid in w.tasks:
            t = TASKS002[tid]
            ps = sorted(set(preds[tid]))
            ss = sorted(set(succs[tid]))
            ptxt = ", ".join(ps) if ps else "—（无前置，可即刻开工）"
            stxt = ", ".join(ss) if ss else "—（链尾）"
            P(f"| {tid} | {t.name} | {t.art} | {t.loc} | {w.lane} | {_day[tid]} |"
              f" {date_of(cal_of(_day[tid]))} | {ptxt} | {stxt} | ⬜ |")
    P("")
    P(f"#### 6.{k}.1 任务示例代码（{nt} 个任务，遵循 50-engineering-standards）")
    P("")
    P("> 每任务一段骨架示例代码，统一约定见 §3.1；实现分片引用前一任务声明的符号（衔接），末片测试覆盖本 WP 全链。")
    P("")
    for w in ws:
        for tid in w.tasks:
            for ln in bpg.code_lines(tid):
                P(ln)
P("## 7. 逐日排程总表")
P("")
P("> 每施工日每泳道至多 1 任务；「当日任务」即当日可并行领取的工作项（前驱均已 ✅）。")
P("> 每 10 个施工日后插入 1 个**验收日**（跑 OS-CHK 全门禁 + 里程碑抽查），下表以「验收日」行显式列出。")
P("")
P("| 工作日 | 日历日 | 当日任务数 | 当日任务（ID） |")
P("|---|---|---|---|")
for cc, dte, cnt, ids in rows:
    P(f"| {cc} | {dte} | {0 if cnt == '—' else cnt} | {ids} |")
P("")
P("## 8. 里程碑与验收门禁映射")
P("")
P("| 里程碑 | 内容 | 锚点 WP | 达成日（推导） | 验收 |")
P("|---|---|---|---|---|")
ms_gate = {
    "B0": "OS-CHK：codegen 快照一致 / [SC] 三路编译绿",
    "B1": "OS-CHK：4 syscall + Badge + ipc_ring + Folding 的契约快照、三路编译与 KUnit 挂点齐备（x86_64）",
    "B2": "可构建可安装：RPM 批量构建 + comps 组 + kickstart 应答文件就绪",
    "B3": "E1-01/E1-02/E1-03/E1-04：镜像 sha256、双固件冷启动、关键链 <30s、装机 3 连测 100%",
    "B4": "E2-01/E2-04：UKUI 三级登录成功、关键单元 100% active",
    "B5": "E7 子集：E1/E2 全域重放 + OS-ACC-RT 四态台账闭合（竣工报告）",
}
for mid, mname, anch, dte, rd in ms_rows:
    P(f"| {mid} | {mname} | {anch} | {dte}（施工日 {rd}） | {ms_gate[mid]} |")
P("")
P("> 里程碑日期为**依赖闭包推导值**（锚点 WP 全部任务 ✅），实际以验收日门禁结果为准；任一锚点后移自动顺延后续里程碑。")
P("> **B3 与 B4 出现并行倒挂属正常**（同主图纸 §8 S5/S6 的表述）：`V-03` 装机实测依赖 QEMU 农场（`L-19`）")
P("> 与镜像 CI（`M-13`），而 `M-17` 首启 bootstrap 只依赖桌面镜像（`M-15`）——两条链相互独立，")
P("> B4 先达成**不代表桌面已验收**：桌面验收在 B4 之后的 `V-04`（E2-01/E2-04）与 `GT-RT-SMOKE` 门禁完成。")
P("")
P("### 8.1 实验矩阵（0.0.2 启用子集）")
P("")
P("| 实验 | 名称 | 判定阈值 | 判据来源 | 执行 WP/任务 | 门禁 |")
P("|---|---|---|---|---|---|")
P("| E1-01 | 镜像制品 sha256 校验 | 校验 100% 通过 | M-13 镜像 CI 验收 | V-02 | GT-RT-BOOT |")
P("| E1-02 | UEFI/BIOS 双固件冷启动 | 双固件启动成功，串口无 kernel panic | NFR-P-005 | V-02 | GT-RT-BOOT |")
P("| E1-03 | systemd-analyze 冷启动关键链 | 全系统 <30s，边缘 <10s | NFR-P-005 | V-02 | GT-RT-BOOT |")
P("| E1-04 | kickstart 全自动装机实测 | 裸机/QEMU 各 3 连测成功率 100% | M-03 验收 | V-03 | GT-RT-BOOT |")
P("| E2-01 | UKUI 会话登录链实测 | lightdm/greeter/会话三级登录成功 | R1 验收 | V-04 | GT-RT-SMOKE |")
P("| E2-04 | 核心服务 active 全量校验 | 关键 systemd 单元 100% active | NFR-P-005 | V-04 | GT-RT-SMOKE |")
P("")
P("**0.0.2 未启用实验及原因**（诚实降级，禁止伪造证据）：")
P("")
P("| 实验 | 未启用原因 | 补齐版本 |")
P("|---|---|---|")
P("| E1-05 ostree 原子升级与回滚 | OTA 通道（M-16）不在范围 | 0.1.x |")
P("| E2-02 AgentsIPC 吞吐冒烟 | E2E 编排（J-08）不在范围；0.0.2 由 V-02 的冷启动日志间接观察 | 0.1.x（引入 J-08） |")
P("| E2-03 Agent 工作流首跑 | ecosystem 验收不在范围 | 0.1.x |")
P("| E3-01~04 调度/SMP/NUMA | 调度轨（A-12~A-22）与 O-07 不在范围 | 0.1.x |")
P("| E4-01 capability 未授权拒绝复验 | 执行 WP V-07 与前置 J-15（渗透套件）不在范围；0.0.2 仅以 B-03 的 KUnit 用例做拒绝对照 | 0.1.x |")
P("| E4-02/03/04 国密/attestation/渗透 | GT-BGM/GT-BCC 与 J-15 不在范围 | 0.1.x |")
P("| E5-01~04 Soak/chaos/MTTR/断电恢复 | V-05/V-06/V-10 不在范围 | 0.1.x |")
P("| E6-01~04 内存/KV-cache/批处理/Token 能效 | O-07/O-08 不在范围 | 0.1.x |")
P("")
P("### 8.2 运行态门禁（GT-RT-*）")
P("")
P("| 门禁 | 前置实验 | 解锁 | 判定 |")
P("|---|---|---|---|")
P("| GT-RT-BOOT | E1-01/02/03/04 | V-03（装机实测） | 全 PASS 或 BLOCKED 登记在册方可解锁 |")
P("| GT-RT-SMOKE | E2-01/04 | M-17 首启收口与 B4 里程碑 | 全 PASS 方可判桌面就绪 |")
P("| GT-RT-PASS | E1/E2 全域重放 | V-11 总判定（B5） | 四态台账闭合 |")
P("")
P("## 9. 质量门禁（0.0.2 强制）")
P("")
P("| 编号 | 门禁 | 判据 | 工具 / 落点 | 阻断级别 |")
P("|---|---|---|---|---|")
P("| QG-01 | 代码重复率 < 3% | 任意模块新提交重复率 ≤ 3% | jscpd / PMD-CPD / 自研 dup-scan；CI job | 阻断合入 |")
P("| QG-02 | 圈复杂度 < 2.5 | 单函数圈复杂度 ≤ 2.5 | lizard / pmccabe；CI job | 阻断合入 |")
P("| QG-03 | **严禁桩函数/桩实现** | 源码内不出现 `TODO`/`FIXME`/`stub`/`skeleton`/占位返回 | `grep` 门禁 + 人工复核（TD-01 须消除） | 阻断合入 |")
P("| QG-04 | 文件头注释规范 | OS-STD-STY-007：SPDX 首行 + ≤20 行模块描述 + 直接 include；**文件头可用中文**，代码区内非必要不注释 | checkpatch 定制规则（L-11） | 阻断合入 |")
P("| QG-05 | 50 规范锚点 | OS-IRON-001~016；OS-STD-CODE-001/010/012/014/016/017/022/026/030/032；OS-BAN-004/005 | `tools/validate-ssot.py` + checkpatch | 阻断合入 |")
P("| QG-06 | ALK 铁律（OS-IRON-003） | 只新增文件、不改主线；diff 限定在 airy/ 新文件与号段接线点 | `ci-airy.yml` 路径触发 + 人工复核 | 阻断合入 |")
P("| QG-07 | DoD 四项 + D5 运行证据 | §2.5 五项全部齐备 | 任务卡勾选 + 证据包 | 阻断验收 |")
P("| QG-08 | 单任务 100~200 行 | 每任务净增 LOC ∈ [100, 200] | 生成器脚本断言 | 阻断拆分 |")
P("| QG-09 | 依赖双向对称 | 前驱⇄后继逐边互逆；无环 | 生成器脚本断言 | 阻断排程 |")
P("| QG-10 | 提交信息规范 | `subsystem: summary` 祈使句、正文 ≤75 列、Fixes/Link 不拆行、DCO 双轨落款 | `submitting-patches.rst` 对照（L-21 前手工复核） | 阻断合入 |")
P("")
P("**7 层自动化验证体系**（继承 `50-engineering-standards` §5）：静态分析 → 单元测试（KUnit/pytest/QtTest）")
P("→ 集成测试 → ABI 检查 → 契约三路编译 → 镜像装机 → 运行态实验（模块 V）。0.0.2 逐层启用，")
P("**CI 矩阵保留 3 架构 × 3 配置定义**，其中仅 x86_64 为 0.0.2 放行架构，arm64/riscv 保持「编译不阻断」。")
P("")
P("## 10. GitHub 流水线与叶子仓 releases")
P("")
P("### 10.1 流水线矩阵（`.github/workflows/`，复用既有 9 个工作流，不新建）")
P("")
P("| 工作流 | 触发 | 作用 | 0.0.2 启用 |")
P("|---|---|---|---|")
P("| `ci-airy.yml` | `kernel/security/airy/**`、`kernel/kernel/superv/**`、`kernel/kernel/syscalls/**`、`kernel/kernel/corekern/**`、`kernel/kernel/log/**`、`kernel/kernel/ipc/**`、`kernel/include/uapi/linux/airymax/**`、`kernel/configs/**`、`kernel/arch/*/configs/airy_defconfig` | airy defconfig 校验，arch 矩阵 `[x86_64, arm64, riscv, loongarch]`；引 OS-STD-TOOL-160（checkpatch）/OS-STD-TOOL-081-CI（sparse）/IRON-3 | 启用（x86_64 阻断，其余告警） |")
P("| `ci-kernel.yml` | 内核主线改动 | 主线构建与测试 | 启用 |")
P("| `codegen-verify.yml` | `tools/codegen/**` | codegen 产物一致性 | 启用（L-01/L-04 门禁） |")
P("| `dsl-verify.yml` | `tools/dsl/**` | DSL 编译器 pytest（6 用例） | 启用（L-03/B-06 门禁） |")
P("| `sc-dual-ci.yml` | `[SC]` 契约头改动 | 三路编译 + 布局校验 | 启用（L-04/L-05 门禁） |")
P("| `ssot-validate.yml` | `ssot-registry.yaml` | SSOT 登记一致性 | 启用 |")
P("| `release.yml` | tag / 手动 | 叶子仓 releases 与制品 | 启用（§10.2） |")
P("| `nightly.yml` | 定时 | 夜间回归 | 启用（L-24） |")
P("| `mgmt-orchestrator.yml` | 管理仓聚合 | 跨叶子仓 CI 聚合（`tools/aggregate-subrepo-ci.py`、`tools/await-agentrt-ci.py`） | 启用（管理仓整体 CI 检验） |")
P("")
P("### 10.2 叶子仓 releases 发行矩阵（9 个 submodule）")
P("")
P("| 叶子仓 | 分支 | 0.0.2 发行物 | 承接 WP |")
P("|---|---|---|---|")
P("| `kernel` | `ALK-6.6-dev` | airy 内核补丁集 release（tag `v0.0.2-alk`） | L-12 / A-* |")
P("| `security` | `dev/hubs-01` | LSM/Capability 模块 release | B-01~B-06 |")
P("| `memory` | `dev/hubs-01` | （0.0.2 不发行，占位说明） | — |")
P("| `cognition` | `dev/hubs-01` | （0.0.2 不发行） | — |")
P("| `services` | `dev/hubs-01` | daemon 框架 release | K-01 |")
P("| `system` | `dev/hubs-01` | systemd 兼容单元 release | M-18 / M-24 |")
P("| `cloudnative` | `dev/hubs-01` | （0.0.2 不发行） | — |")
P("| `tests-linux` | `dev/hubs-01` | OS-ACC-RT 执行器与证据包测试 release | V-01 |")
P("| `distro` | `dev/hubs-01` | **AirymaxOS 0.0.2 镜像与 RPM 制品 release**（kickstart/comps/desktop slice/lockfile） | M-01~M-17 |")
P("")
P("**整体 CI 检验**：在 `agent-linux` 管理仓跑 `mgmt-orchestrator.yml`（聚合 9 叶子仓 CI 状态）+")
P("`ssot-validate.yml`（账本一致性）；任一叶子仓 release 失败则管理仓整体 CI 红。")
P("")
P("**托管策略**：**atomgit 为主托管平台（仅 SSH，禁用 HTTP）**；GitHub 为镜像，")
P("通过 MCP 与本地 key 驱动上述流水线。镜像方向单向（atomgit → GitHub），禁止反向写入。")
P("")
P("## 11. 技术债登记与消除清单")
P("")
P("| 编号 | 技术债 | 位置 | 现状（2026-10-14） | 消除任务 | 消除版本 |")
P("|---|---|---|---|---|---|")
P("| TD-01 | `run-smoke.sh` 四函数 skeleton 桩 | `distro/ci/run-smoke.sh` | `t1_tauri_window`/`t2_input_method`/`t3_pipewire`/`t4_cgroup_freeze` 均 `echo \"1..0 # skeleton — TODO\"`，与「严禁桩实现」冲突 | R1-04 / R1-05 / M-15 的真实检测任务替换；替换后接入 `distro/ci` | 0.0.2 |")
P("| TD-02 | `distro` 子模块 dirty | `agent-linux` `git status` | 仅 ` M distro` 未提交 | M-15 收口时一并提交并打 tag | 0.0.2 |")
P("| TD-03 | 账本版本与登记版本未对齐 | `ssot-registry.yaml` v0.2.8 | 未登记 0.0.2 方案 | L-31 收口时追加 `airymaxos_002_plan` 段 | 0.0.2 |")
P("| TD-04 | arm64/riscv/loongarch CI 仅编译不阻断 | `ci-airy.yml` 矩阵 | 0.0.2 只放行 x86_64 | A-31/A-36 接线任务（0.1.x）转阻断 | 0.1.x |")
P("| TD-05 | 无 Gateway 单入口 | 桌面链 | 0.0.2 直连后端 | G-09 + R1-06 全链 | 0.1.x |")
P("")
P("## 12. 风险与进度跟踪")
P("")
P("| 风险 | 现象 | 处置 |")
P("|---|---|---|")
P("| R-002-1 范围回涨 | 在范围 WP 实际 LOC 超 0.0.2 预算 >20% | 按主图纸 §1.2 原子化原则追加拆片（保持 100~200 约束），重跑 `bp_002_gen.py` |")
P("| R-002-2 降级边失守 | 被登记为「直接裁撤」的依赖（M-18←H-04、R1-06←G-09）在实现中出现对范围外符号的硬引用 | 生成器断言 + 编译期 `#include` 检查（首片必须只 include 在范围前驱头） |")
P("| R-002-3 主线漂移 | 上游 6.6 stable 更新 | 每验收日跑 L-05 ABI 检查 + L-06 OS-CHK |")
P("| R-002-4 装机介质差异 | 裸机 UEFI/BIOS 行为不一致 | E1-02 双固件各 3 连测；不一致则登记 BLOCKED 并附 QEMU 等效证据 |")
P("| R-002-5 UKUI 上游变更 | R1 适配层与 UKUI 主线不兼容 | R1 全部走适配层新文件（ALK 铁律），不动 UKUI 主线 |")
P("| R-002-6 桩残留 | TD-01 未在范围内消除 | QG-03 grep 门禁阻断；TD-01 列为 B4 里程碑前置 |")
P("")
P("**跟踪机制**：任务表逐行勾状态 → 每周对账「✅ 任务 LOC 和 vs 计划曲线」→ 每验收日出里程碑偏差报告；")
P("排程重算入口：`10-references/generators/bp_002_gen.py`（改 `SCOPE_WHITELIST` / `EDGE_REG` / `CUT_REASON` 后重跑），")
P("**账本永远由脚本产出、人工只改种子**。主图纸重算入口为同目录 `bp_seed.py` + `bp_gen.py`。")
P("")
P("---")
P("")
P(f"*0.0.2 版任务方案 v0.0.2 ｜ 由 `10-references/generators/bp_002_gen.py` 确定性生成（范围裁定、替换边登记、拆分、")
P(f"缩放沿用、拓扑排程、示例代码模板均经脚本断言校验；preds⇄succs 双向依赖逐边对称断言通过；")
P(f"旁路边 {len(bypass_edges)} 条全部在 §2.2 登记）｜ 0.0.2 净新增 {TOT_LOC:,} 行（纳入主图纸 {_inc_total:,} + V 模块 {_vloc:,}）")
P(f"｜ 每个任务示例代码遵循 50-engineering-standards（§3.1）。*")

out = os.path.normpath(os.path.join(_here, "..", "..", "0.0.2-极境OS任务方案.md"))
with open(out, "w", encoding="utf-8") as fh:
    fh.write("\n".join(L) + "\n")

print(f"OK  0.0.2: wps={NWP} tasks={NTASK} lanes={len(lanes002)} maxraw={maxraw} "
      f"caldays={maxcal} loc={TOT_LOC} bypass_edges={len(bypass_edges)}")
print(f"    span: {START.isoformat()} ~ {date_of(maxcal).isoformat()}")
print("    milestones:", " ".join(f"{r[0]}={r[3]}" for r in ms_rows))
print(f"    critical path: {len(CP)} tasks, {CP[0]} .. {CP[-1]}")
print(f"    written: {out} ({len(L)} lines)")
