Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 00 — agentrt-linux v2.6 判定二次深化验证报告 v2.7

> **审查日期**：2026-07-22
> **审查目标**：对 v2.6 报告中的每一项判定进行再次实证验证（"对所有的问题，都要慎重进行再次验证。历史教训。"）
> **审查方法**：亲自 Grep/Read/RunCommand 验证，不完全依赖子代理
> **上一版本**：v2.6（2026-07-22）
> **核心原则**：v2.4 产生 6 项误判的教训——验证必须严谨，不能随意判定

---

## 1. 执行摘要

### 1.1 核心发现

v2.7 深化验证发现 **v2.6 报告存在 3 项误判**，同时确认 **4 项真实问题**。

| 维度 | v2.6 判定 | v2.7 验证结果 |
|------|----------|-------------|
| P0-014 syscall 编号不一致 | ❌ 真实问题 | ✅ **确认真实**——unistd.h 453-456 / syscall_64.tbl 454-457 |
| P0-016 4份v0.2.8文档 | ❌ 真实问题 | ✅ **确认真实**——threat-model/ci-cd-pipeline/sbom-generation/codegen-pipeline |
| P0-017 codegen缺失 | ❌ 真实问题 | ✅ **确认真实**——tools/codegen/ 不存在 |
| P0-018 ABI工具缺失 | ❌ 真实问题 | ✅ **确认真实**——无ABI白名单/检查脚本 |
| P0-019 LSM加载顺序未文档化 | ❌ 真实问题 | ❌ **误判**——01-lsm-framework.md §4 + 07-airy-lsm-design.md §2.2 已详细文档化 |
| GAP-05 sec_d单点故障无恢复 | ⚠️ 部分真实 | ❌ **误判**——10-user-supervisor-daemon.md §4.5 有完整崩溃恢复设计 |
| GAP-02 fastpath不可观测 | ⚠️ 部分真实 | ⚠️ **部分误判**——IPC入口/出口有tracepoint，C-S9内部待确认 |
| v2.4的6项误判 | ✅ 误判 | ✅ **全部确认**——CI存在/decode-invoke/MCS/CI矩阵/禁union/三项全缺 |

### 1.2 误判根因分析

v2.6 产生 3 项误判的根因与 v2.4 相同——**设计文档搜索不充分**：

1. **P0-019**：v2.6 声称"LSM加载顺序未文档化"，但 `01-lsm-framework.md` §4.1-4.3 和 `07-airy-lsm-design.md` §2.2 有详细文档
2. **GAP-05**：v2.6 声称"sec_d无崩溃恢复设计"，但 `10-user-supervisor-daemon.md` §4.5 有完整的5阶段恢复流程
3. **GAP-02**：v2.6 声称"fastpath不可观测"过于绝对，`90-observability/` 有9个文档设计了tracepoint

**历史教训再次验证**：每一轮审查都可能产生新的误判，必须逐项实证验证。

---

## 2. v2.6 判定逐项验证

### 2.1 P0-014 syscall 编号不一致 — ✅ 确认真实

**验证方法**：亲自读取 `unistd.h` 和 `syscall_64.tbl`

**证据**：

`include/uapi/asm-generic/unistd.h` L827-837：
```c
#define __NR_airy_sys_call 453
__SYSCALL(__NR_airy_sys_call, sys_airy_sys_call)
#define __NR_airy_sys_rovol_ctl 454
...
#define __NR_syscalls 457
```

`arch/x86/entry/syscalls/syscall_64.tbl` L378-381：
```
454	common	airy_sys_call		sys_airy_sys_call
455	common	airy_sys_rovol_ctl	sys_airy_sys_rovol_ctl
456	common	airy_sys_sched_ctl	sys_airy_sys_sched_ctl
457	common	airy_sys_clt_notify	sys_airy_sys_clt_notify
```

**关键发现**：`unistd.h`（通用，用于arm64/riscv等）用 453-456，`syscall_64.tbl`（x86专用）用 454-457。这意味着 **x86 与其他架构的 syscall 编号不一致**——比 v2.6 描述的"三处不一致"更严重。

**结论**：P0-014 真实，优先级最高。

### 2.2 P0-016 4份v0.2.8文档 — ✅ 确认真实

**验证方法**：`grep -rh "文档版本" docs/AirymaxOS/ | sort | uniq -c`

**证据**：
- 97 份文档：v1.0.1 ✅
- 81 份文档：0.1.1（阶段快照，需确认）
- **4 份文档：0.2.8 ❌ 违反 IRON-8**

4 份 v0.2.8 文档：
1. `10-architecture/08-threat-model.md`
2. `70-build-system/03-ci-cd-pipeline.md`
3. `190-distribution/06-sbom-generation.md`
4. `30-interfaces/06-codegen-pipeline.md`

**结论**：P0-016 真实，4 份文档需升级到 v1.0.1。

### 2.3 P0-017 codegen缺失 — ✅ 确认真实

**验证方法**：`find agentrt-linux -type d -name "codegen"` + `find -name "syscall_gen.py"` + `find -name "*.bf"`

**证据**：三个命令均无输出——`tools/codegen/` 目录、`syscall_gen.py`、`.bf` 文件全部不存在。

**结论**：P0-017 真实，codegen 管道实现为零。

### 2.4 P0-018 ABI工具缺失 — ✅ 确认真实

**验证方法**：`find -name "*abi*whitelist*" -o -name "*check_abi*" -o -name "*kabi*"`（排除上游文件）

**证据**：无 Airymax 专用 ABI 白名单或检查脚本。

**结论**：P0-018 真实，ABI 检查工具不存在。

### 2.5 P0-019 LSM加载顺序未文档化 — ❌ v2.6 误判！

**验证方法**：`grep -rln "load_order\|加载顺序\|LSM_ORDER\|互操作" docs/AirymaxOS/`

**证据 1**：`110-security/01-lsm-framework.md` 详细文档化了 LSM 加载顺序：
- §4.1：`chosen_lsm_order` / `builtin_lsm_order` 机制
- §4.2：`ordered_lsm_parse()` 排序解析流程（FIRST → chosen → builtin → LAST）
- §4.3：排他对齐（`LSM_FLAG_EXCLUSIVE`——SELinux/AppArmor/Smack 互斥，airy 不打 EXCLUSIVE 可共存）
- §5.1：两阶段初始化（early_security_init + security_init）
- §5.2：blob 缓存创建 + `report_lsm_order()` 输出最终顺序
- §5.3：LSM 模块生命周期状态机

**证据 2**：`110-security/07-airy-lsm-design.md` §2.2 详细文档化了 airy LSM 的加载顺序：
- "v1.0.1 修正：airy 不使用 LSM_ORDER_FIRST，改用 LSM_ORDER_MUTABLE"
- `CONFIG_LSM` 默认值：`"landlock,lockdown,yama,loadpin,safesetid,airy,selinux,..."`
- 执行顺序表格：0 capability(FIRST) / 1 airy(MUTABLE,CONFIG_LSM首位) / 2 landlock / ... / 5 integrity(LAST)
- "airy 不打 EXCLUSIVE 标记，可与任何 major LSM 共存"

**证据 3**：代码 `security/airy/airy_lsm.c` L7 注释 + L150 `DEFINE_LSM(airy)`：
```c
// L7: Registers with DEFINE_LSM(airy) at LSM_ORDER_MUTABLE.
// L150: DEFINE_LSM(airy) = { .order = LSM_ORDER_MUTABLE, ... }
```

**结论**：**P0-019 撤销**——LSM 加载顺序/互操作在 2 份设计文档 + 代码中都有详细定义。v2.6 产生此误判的根因是未充分搜索 `110-security/` 目录。

### 2.6 v2.4 的 6 项误判 — ✅ 全部确认

**验证方法**：亲自 Grep/Read 验证每一项

| v2.4 误判 | v2.7 验证 | 证据 |
|----------|----------|------|
| CI不存在 | ✅ 确认误判 | `agentrt-linux/.github/workflows/` 有7个文件，ci-kernel.yml有32configs矩阵 |
| decode/invoke未实现 | ✅ 确认误判 | `01-syscalls.md` L114 `airy_decode_and_invoke()` + `07-ipc-fastpath.md` L453 `airy_ipc_validate()` |
| MCS未实现 | ✅ 确认误判 | `10-sc-sched-extension.md` §5 L248-292 完整MCS映射（scBudget→sched_runtime等） |
| CI矩阵缺失 | ✅ 确认误判 | ci-kernel.yml: 4架构×4配置×2编译器 |
| 禁union未遵循 | ✅ 确认误判 | `grep union security/airy/` 无匹配 |
| 三项全缺 | ✅ 确认部分误判 | CI已存在，仅codegen/ABI缺失 |

---

## 3. v2.6 第三方风险评估修正

### 3.1 GAP-05 sec_d 单点故障 — ❌ v2.6 误判！

**v2.6 判定**："sec_d 单点故障无高可用/崩溃恢复设计"

**v2.7 验证**：`20-modules/10-user-supervisor-daemon.md` §4.5 有**完整的 sec_d 崩溃恢复设计**：

| 设计要素 | 文档位置 | 内容 |
|----------|---------|------|
| 崩溃检测 | §4.5.1 L370-372 | systemd `Restart=always` + `WatchdogSec=` |
| H4 降级 | §4.5.2 L380-382 | sec_d崩溃**不影响已有IPC**（agent_caps[]是内核静态数组），仅影响新Badge编译/撤销 |
| 5阶段恢复 | §4.5.3 L392-425 | 崩溃→检测→重启→加载持久化状态→Epoch自增+全量重编译 |
| 状态持久化 | L425 | agent_caps[]关键字段持久化到 `/var/lib/airy/sec_d_state.json` |
| Reconciliation | §4.5.5 L569 | sec_d重启后与Macro-Supervisor执行Reconciliation |
| 性能指标 | L587-592 | 重启<1s，新Badge中断<2s |
| 单点故障fallback | L14 | "内核watchdog直接重启 + 全局Epoch撤销" |

**结论**：**GAP-05 撤销**——sec_d 有完整的高可用/崩溃恢复设计。v2.6 产生此误判的根因是未搜索 `20-modules/` 目录。

### 3.2 GAP-02 fastpath 不可观测 — ⚠️ 部分误判

**v2.6 判定**："fastpath 内联校验不可观测"

**v2.7 验证**：`90-observability/` 目录有 9 个文档，设计了 IPC fastpath 的可观测性：

| 可观测性层次 | 证据 | 覆盖范围 |
|-------------|------|---------|
| IPC入口/出口tracepoint | `90-observability/README.md` L18: "tracepoint覆盖IPC fastpath入口" | ✅ 覆盖 |
| airy_ipc_send/recv事件 | `08-agent-tracing.md` L104-105 + `05-debugfs-tracefs.md` L738 | ✅ 已定义 |
| io_uring_cmd观测 | `README.md` L54: "IPC fastpath tracepoint观测io_uring_cmd入口/出口" | ✅ 覆盖 |
| Ring Buffer写入延迟 | `README.md` L54: "Ring Buffer写入延迟" | ✅ 覆盖 |
| C-S9 Badge校验内部 | 未找到专门的tracepoint | ⚠️ 待确认 |

**修正**：v2.6 的"fastpath不可观测"过于绝对。实际情况是：
- IPC fastpath **入口/出口** 有 tracepoint ✅
- C-S9 Badge 校验**内部每一步**（EPOCH/RANDTAG/PERMS）的可观测性待确认 ⚠️

**结论**：**GAP-02 降级**——从"fastpath不可观测"降为"C-S9内部级别可观测性待确认"。

### 3.3 其他第三方风险验证

| GAP | v2.6 判定 | v2.7 验证 |
|-----|----------|----------|
| GAP-01 ~260补丁维护 | ⚠️ 部分真实 | ✅ 确认（03-upstream-tracking.md §6.1 自报~260补丁） |
| GAP-03 buffer生命周期 | ⚠️ 部分真实 | ✅ 确认（无显式生命周期状态机） |
| GAP-04 cap撤销与资源释放 | ⚠️ 部分真实 | ✅ 确认（cap撤销不与资源释放挂钩） |
| GAP-06 1024槽位扩展 | ⚠️ 部分真实 | ✅ 确认（无扩展路径设计预留） |
| GAP-07 io_uring CVE追踪 | ⚠️ 低风险 | ✅ 确认（无CVE追踪清单） |
| GAP-08 纯C vs BPF对比 | ⚠️ 低风险 | ✅ 确认（无完整对比文档） |

---

## 4. 修正后的真实问题清单

### 4.1 确认真实的 P0 问题（4 项，从 v2.6 的 5 项减少）

| # | 问题 | v2.6 判定 | v2.7 验证 |
|---|------|----------|----------|
| P0-014 | syscall 编号三处不一致 | 真实 | ✅ **确认真实** |
| P0-016 | 4份v0.2.8文档需升级 | 真实 | ✅ **确认真实** |
| P0-017 | codegen 管道实现缺失 | 真实 | ✅ **确认真实** |
| P0-018 | ABI 检查工具缺失 | 真实 | ✅ **确认真实** |
| ~~P0-019~~ | ~~LSM加载顺序未文档化~~ | 真实 | ❌ **撤销（误判）** |

### 4.2 修正后的 GAP 清单（6 项，从 v2.6 的 8 项减少）

| # | gap | v2.6 判定 | v2.7 验证 |
|---|-----|----------|----------|
| GAP-01 | ~260补丁维护成本 | 部分真实 | ✅ 确认 |
| GAP-02 | fastpath可观测性 | 部分真实 | ⚠️ **降级**（入口/出口有tracepoint，C-S9内部待确认） |
| GAP-03 | buffer生命周期 | 部分真实 | ✅ 确认 |
| GAP-04 | cap撤销与资源释放 | 部分真实 | ✅ 确认 |
| GAP-06 | 1024槽位扩展 | 部分真实 | ✅ 确认 |
| GAP-07 | io_uring CVE追踪 | 低风险 | ✅ 确认 |
| GAP-08 | 纯C vs BPF对比 | 低风险 | ✅ 确认 |
| ~~GAP-05~~ | ~~sec_d单点故障~~ | 部分真实 | ❌ **撤销（误判）** |

---

## 5. 误判历史统计

### 5.1 各轮次误判统计

| 轮次 | 误判数 | 误判类型 | 根因 |
|------|--------|---------|------|
| v2.2及之前 | 0 | — | 基于"0行代码"事实 |
| v2.3 | 2 | 过度乐观 | "30+文档统一"/"IRON-8已满足" |
| v2.4 | 6 | 设计文档搜索不充分 | CI/decode-invoke/MCS/CI矩阵/禁union/三项全缺 |
| v2.5 | 0 | — | 纠正了v2.4全部误判 |
| v2.6 | 3 | 设计文档搜索不充分 | P0-019 LSM/GAP-05 sec_d/GAP-02 fastpath |
| v2.7 | 0（待定） | — | 纠正了v2.6全部误判 |

### 5.2 误判模式

**核心模式**：每一轮"综合评估"报告都倾向于产生误判，根因是**设计文档搜索不充分**。

- v2.4 检查了 `kernel/.github/` 而非 `agentrt-linux/.github/`
- v2.6 声称"LSM加载顺序未文档化"但未搜索 `110-security/`
- v2.6 声称"sec_d无崩溃恢复"但未搜索 `20-modules/`
- v2.6 声称"fastpath不可观测"但未搜索 `90-observability/`

**教训**：每一项"缺失"判定都必须先执行 `grep -rln <关键词> docs/AirymaxOS/` 确认设计文档中是否已有定义。

---

## 6. 审查结论

### 6.1 总体判定

经 v2.7 深化验证，v2.6 报告的 3 项误判已全部纠正：

1. **P0-019 撤销**——LSM 加载顺序在 `01-lsm-framework.md` §4 + `07-airy-lsm-design.md` §2.2 已详细文档化
2. **GAP-05 撤销**——sec_d 崩溃恢复在 `10-user-supervisor-daemon.md` §4.5 有完整5阶段设计
3. **GAP-02 降级**——IPC fastpath 入口/出口有 tracepoint，仅 C-S9 内部级别待确认

### 6.2 修正后的 M1 前置工作

**4 项 P0**（从 v2.6 的 5 项减少）：
1. P0-014: 修正 syscall 编号三处不一致
2. P0-016: 升级 4 份 v0.2.8 文档到 v1.0.1
3. P0-017: 创建 codegen 基础框架
4. P0-018: 创建 ABI 检查工具

**6 项 GAP**（从 v2.6 的 8 项减少）：
1. GAP-01: ~260补丁维护成本量化
2. GAP-02: C-S9 内部级别可观测性（降级）
3. GAP-03: registered buffer 生命周期状态机
4. GAP-04: cap撤销与资源释放关联
5. GAP-06: 1024槽位扩展路径预留
6. GAP-07/08: io_uring CVE追踪 + 纯C vs BPF对比文档

### 6.3 验证方法论确认

v2.7 的每项判定均通过**亲自 Grep/Read/RunCommand** 验证，不完全依赖子代理。这确保了"对所有的问题，都要慎重进行再次验证"的原则得到落实。

---

## 附录 A：v2.7 验证命令清单

| 验证项 | 命令 | 结果 |
|--------|------|------|
| P0-014 | `grep -n airy_sys unistd.h` + `grep -n airy syscall_64.tbl` | 453-456 vs 454-457 |
| P0-016 | `grep -rh "文档版本" docs/AirymaxOS/ \| sort \| uniq -c` | 4份v0.2.8 |
| P0-017 | `find -type d -name codegen` + `find -name syscall_gen.py` | 无输出 |
| P0-018 | `find -name "*abi*whitelist*"` | 无输出 |
| P0-019 | `grep -rln "LSM_ORDER\|加载顺序" docs/AirymaxOS/110-security/` | 01-lsm-framework.md + 07-airy-lsm-design.md |
| GAP-05 | `grep -rn "sec_d.*crash\|sec_d.*restart\|sec_d.*恢复"` | 10-user-supervisor-daemon.md §4.5 |
| GAP-02 | `grep -rn "tracepoint\|airy_ipc.*trace" docs/AirymaxOS/90-observability/` | 9个文档 + airy_ipc_send/recv |
| v2.4误判#1 | `ls agentrt-linux/.github/workflows/` | 7个workflow文件 |
| v2.4误判#2 | `grep decode_and_invoke 01-syscalls.md` | L114 完整函数 |
| v2.4误判#3 | `grep MCS 10-sc-sched-extension.md` | §5 完整映射 |
| v2.4误判#5 | `grep union security/airy/` | 无匹配 |

---

> **文档结束** | agentrt-linux v2.7 深化验证报告
> 核心原则：对所有的问题，都要慎重进行再次验证。历史教训。
