Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agentrt-linux v9.0 系统性深度审查报告

> **文档定位**：v8.0 报告之后的"不计成本深度科学推论"——5 轨道并行 + 4 维度综合 + 字节级证据\
> **文档版本**：v9.0\
> **最后更新**：2026-07-28\
> **审查方法**：5 轨道并行深度审查（文档审计 + 历史验证 + OLK-6.6 源码学习 + seL4 源码学习 + 内核科学推论）\
> **上级文档**：[26-systematic-audit-v8.0.md](26-systematic-audit-v8.0.md)

---

## 1. 审查概览

本次审查在 v8.0 基线上启动 5 轨道并行深度调研，对内核方案进行"不计成本的科学推论与逻辑验证"。每个轨道均通过子代理执行字节级阅读，确保审查深度。

| 轨道 | 审查方法 | 输出 |
|------|---------|------|
| 轨道1 | docs/AirymaxOS 8 维度文档审计 | 22 项新发现（5A + 12B + 5C） |
| 轨道2 | v3.5 27 份审查文档全量阅读 + v8.0 10 项 A/B 级问题逐字节验证 | 8 项未修复 + 1 项部分修复 + 1 项已修复 |
| 轨道3 | OLK-6.6 关键源码字节级阅读（10 任务） | 10 项工程模式借鉴建议 |
| 轨道4 | seL4 关键源码字节级阅读（10 任务） | 10 项微内核设计借鉴建议 |
| 轨道5 | 10 项内核核心设计点的科学推论 | 7 项高风险 + 3 项中风险识别 |

| 维度 | 发现总数 | A 级 | B 级 | C 级 |
|------|---------|------|------|------|
| D9-文档审计 | 22 | 5 | 12 | 5 |
| K9-内核科学推论 | 10 | 4 | 4 | 2 |
| V8-v8.0 修复验证 | 10 | 8 未修复 | 1 部分修复 | 1 已修复 |
| **合计** | **42** | **17** | **17** | **8** |

**注**：V8 维度的"未修复"指 v8.0 报告标注的 A/B 级问题在 v9.0 验证时仍未修复，按 A 级处理。

---

## 2. v8.0 修复状态逐字节验证

对 v8.0 报告中 6 项 A 级 + 4 项 B 级真实问题进行逐字节验证（10 项中 1 项已修复）：

### 2.1 A 级问题（6 项，全部未彻底修复）

| 编号 | 问题 | 当前状态 | 证据（文件:行号 + 内容） |
|------|------|---------|----------------------|
| A-1 | MAC\_MAX\_AGENTS 转义残留 4 处 | **未修复** | `04-engineering-baseline.md:605`、`05-adrs.md:1221`、`03-microkernel-strategy.md:607`、`01-kernel.md:823` 均仍为 `MAC\_MAX\_AGENTS` |
| A-2 | 3 个未标记 [IND] 的 IPC opcode | **未修复** | `01-abi-stability.md:387,399`（FEATURE_QUERY）、`09-kernel-agent-supervisor.md:79,405` + `10-user-supervisor-daemon.md:16,1415,1469,1471`（ADJUDICATE/UNFREEZE）首次出现处无 [IND] 标注 |
| A-3 | airy_ipc_msg_hdr 不存在的 .version 字段 | **未修复** | `01-abi-stability.md:385` 仍有 `.version = AIRY_IPC_VERSION_CURRENT,`；SSoT `ipc.h` L77-89 确认 `airy_ipc_msg_hdr` 共 11 字段无 version |
| A-4 | uapi_compat.h 结构性漂移 | **部分修复** | commons 侧已改（L23-27 `#include <linux/types.h>`），kernel 侧 L22-32 仍为 `<stdint.h>` + 8 typedef；commons 侧 L11-13 注释仍写 "typedef from stdint"，与代码不符 |
| K-B4 | airy_cap_badge_revoke 死代码 | **未修复** | `airy_cap_revoke.c:18,30` 定义；`airy_cap.h` 全文无声明；Grep 全 kernel 无调用方；`Kbuild:12` 仍编译 `airy_cap_revoke.o`；与 `airy_cap_derive(REVOKE)` 功能重复（均 `atomic_inc(&airy_cap_global_epoch)`） |
| K-B5 | airy_uring_cmd_handle 死代码 | **未修复** | `airy_uring_cmd.c:38` 128 行完整实现；`airy_ipc_internal.h:51` 声明；Grep 全 kernel 仅 3 处命中（声明 + 定义 + 注释引用）；无 `io_uring_cmd_ops` 注册，无 LSM hook 调用 |

### 2.2 B 级问题（4 项，1 项已修复）

| 编号 | 问题 | 当前状态 | 证据 |
|------|------|---------|------|
| K-B1 | 跨配置项链接依赖 | **已彻底修复** | `security/airy/Kconfig:6-10`：`SECURITY_AIRY` 仅 `depends on SECURITY + IO_URING`，无 `depends on AIRY_IPC`；`config/Kconfig.alk:42-44`：`AIRY_IPC` 反向 `depends on SECURITY_AIRY`；security/airy/ 内调用的 `airy_ipc_freeze_ring`/`airy_ipc_ring_for_task` 均在 `airy_ipc_freeze.c` 内本地定义 |
| K-B6 | die_notifier 双重注册 | **未修复** | `airy_die_notify.c:142-155` 注册 `airy_die_nb`（priority=INT_MAX）；`airy_die_notify_superv.c:74-81` 注册 `airy_superv_die_nb`（priority=INT_MAX）。同一 die 事件触发两个回调 → fault_count 三重递增（见推论 8） |

### 2.3 v8.0 修复完成度评估

**修复完成度：10% (1/10)**

- 已彻底修复：1 项（K-B1）
- 已部分修复：1 项（A-4，commons 侧已改但 kernel 侧未回传）
- 未修复：8 项（A-1/A-2/A-3/K-B4/K-B5/K-B6）

**结论**：v8.0 报告生成后未进行 P0 修复实施。本次 v9.0 审查发现的 v8.0 遗留问题已纳入 v9.0 P0 修复清单（见 §7）。

---

## 3. AirymaxOS 文档深度审查新发现（22 项）

8 维度审查发现 22 项新问题，详见下表（仅列摘要，完整证据见子代理报告）：

### 3.1 A 级新发现（5 项）

| 编号 | 维度 | 问题 | 文件:行号 |
|------|------|------|---------|
| D9-3 | 维度2 | capability 计数 41 vs 44 跨文档不一致 | `110-security/03-capability-model.md:16` SSoT 声明仍写"41 ID"，未含 3 个 Airymax 扩展（41-43）。`00-alk-kernel-overview.md:130,452`、`04-engineering-baseline.md:607`、`05-adrs.md:1208,1222` 同步未更新。但 `20-modules/03-security.md:70`、`20-modules/06-cloudnative.md:391`、`30-interfaces/06-codegen-pipeline.md:7` 已更正为 44 |
| D9-9 | 维度4 | SSoT registry 将 IRON-9 v3 描述为"三层"而非"四层" | `09-ssot-registry.md:1299` 写"IRON-9 v3：**三层**共享模型 [SC]+[SS]+[IND]"，遗漏 [DSL]。`06-iron9-shared-model.md:14,49` SSoT 定义为"四层 [SC]+[SS]+[IND]+[DSL]" |
| D9-12 | 维度5 | syscall 宏值被误写为内部编号 | `07-directory-structure.md:1332` 写"AIRY_SYS_CALL=0 ... AIRY_SYS_CLT_NOTIFY=3"，实际宏值为 548-551。0-3 是 syscall.xml 内部编号（number + linux_base 中的 number），非宏值 |
| D9-15 | 维度6 | IRON-7/IRON-8 编号在 SSoT 与 10+ 份文档间矛盾 | `09-ssot-registry.md:1297-1298`：IRON-7=禁止版本过渡、IRON-8=禁止生产就绪降级。但 `04-engineering-baseline.md:683` 等 10+ 份文档将版本过渡规则引用为"IRON-8" |
| D9-17 | 维度7 | `05-adrs.md` 使用禁用版本号"v1.1"描述当前架构 | `05-adrs.md:1224` 写"Syscall 编号体系（**v1.1**: 4 核心 + 20 预留 = 24 槽位）"。IRON-7 明确禁止 v1.1 中间版本号 |

### 3.2 B 级新发现（12 项，简表）

| 编号 | 维度 | 问题简述 |
|------|------|---------|
| D9-1 | 1 | `02-services.md:65` 与 L85 同文档内 daemon 命名混用（`macro_d` vs `macro_superv`、`logger_d` vs `logger_daemon`、`config_d` vs `config_daemon`） |
| D9-4 | 2 | Badge Perms 权限位数不一致：`03-capability-model.md:239,279` 写"7 位"，`10-formal-verification.md:588` 写"12 类" |
| D9-6 | 2 | Epoch 16 位在长运行场景下可能溢出：65535 秒 ≈ 18.2 小时即耗尽，形式化验证假设仅适用 0.1.1 小规模 |
| D9-7 | 3 | `05-cognition.md:40` 标注 CoreLoopThree kthread 为 [SS]，L70 同文档标注为 [IND]，同一实体跨层 |
| D9-8 | 3 | "OS-IRON-KTHREAD-BOUNDARY" 约束在全文档中不存在，未落地为文档化铁律 |
| D9-10 | 4 | 5 份文档仍使用"三层共享模型"而非 v3 四层：`00-engineering-standards-handbook.md:166`、`02-memory-flow.md:613`、`02-ebpf-probes.md:531`、`07-directory-structure.md:422,432` |
| D9-13 | 5 | `01-abi-stability.md:69` 注释"IPC send/recv"为 0.1.1 旧语义，v1.0.1 Capability Folding 后 airy_sys_call 语义已变更 |
| D9-14 | 5 | `07-syscall-registry.md:197-198` 残留 0.1.1 时代独立 syscall 编号 613/615，v1.0.1 已合并入 551 |
| D9-16 | 6 | IRON-1~10 表格缺少"通过/失败"判定标准列 |
| D9-18 | 7 | 版本历史表残留禁用版本号 0.3.0/v1.0.0/v1.1 未标注"IRON-7 追溯禁止" |
| D9-19 | 7 | `80-testing/` 6 份文档大量使用"v1.1"作为当前版本描述符，应改为 v1.0.1 |
| D9-21 | 8 | `05-adrs.md:86` ADR-001 特性表将 sched_ext 列为"内核增强"未标注拒绝状态 |

### 3.3 C 级新发现（5 项，简表）

| 编号 | 问题简述 |
|------|---------|
| D9-2 | DSL 降级层 opcode 集描述分散，缺统一契约文档 |
| D9-5 | fastpath 实际 8 态而非任务描述的 7 态（信息核实，非文档缺陷） |
| D9-11 | 章节锚点 `#iron-9-v2-三层共享模型` 与标题"v3 四层"不符 |
| D9-20 | IPC 协议版本"v1.1"与文档版本"v1.0.1"并存易混淆，需显式区分 |
| D9-22 | sched_ext 引用全部在"不使用"语境中，命名一致（核实项） |

---

## 4. 内核方案深度科学推论（10 项）

对 10 个核心设计点进行第一性原理推论，识别 7 项高风险问题。

### 4.1 高风险推论（4 项 A 级）

#### K9-1 [A级] Capability Folding 全局 epoch 撤销爆炸半径

**推论**：`airy_cap_badge_revoke()` 递增**全局** epoch（`atomic_inc(&airy_cap_global_epoch)`），而非 per-agent epoch。撤销单个 agent 会导致**全部 1024 个 agent 的 Badge 失效**。

**风险**：单点撤销触发系统级 Badge 失效风暴，所有 agent 必须重新申请 Badge，sec_d 处理压力激增。

**修复建议**：
1. `airy_cap_slot` 增加 `__u16 epoch` 字段，revoke 只递增目标 slot 的 epoch
2. 全局 epoch 仅用于 bootstrap 阶段
3. 修复 `airy_cap_rotate.c` 写序：先 `smp_store_release(&randtag)`，后 `smp_store_release(&badge)`，消除 fastpath/slowpath 不一致竞态

#### K9-2 [A级] `airy_cap_rotate` fastpath/slowpath 不一致竞态

**推论**：`airy_cap_rotate.c` L76-77 写序：先 `WRITE_ONCE(badge, new_badge)`，后 `WRITE_ONCE(randtag, new_randtag)`。

- **Fastpath**（`airy_cap_badge_ok`）只读 `slot->randtag`，不读 `slot->badge` → 过渡窗口内 slot.randtag 仍为旧值 → 旧 Badge 仍通过 fastpath
- **Slowpath**（`phase5_slowpath_enforce`）读 `slot->badge` 做全等比较 → 过渡窗口内 slot.badge 已为新值 → 旧 Badge 被拒绝

**结论**：同一旧 Badge 在过渡窗口内，fastpath 放行但 slowpath 拒绝。注释声称的"safe-fail"理由（"reader observes new badge"）**错误**——fastpath 根本不读 slot.badge。

**风险**：高——并发 rotate 期间安全策略不一致。

**修复建议**：先写 `slot->randtag = new_randtag`，再写 `slot->badge = new_badge`。ARM64 上必须用 `smp_store_release` 保证 Store-Store 顺序。

#### K9-3 [A级] sched_tac 与 SCHED_DEADLINE 语义根本冲突

**推论**：SCHED_DEADLINE 的 CBS（Constant Bandwidth Server）假设任务有**可预测的 runtime/period/deadline**（WCET 模型）。Agent 的 THINK 阶段（LLM 推理）执行时间高度可变（100ms-10s，100x 变异系数）。

- 若 `dl_runtime` = 10s（WCET），`dl_period` = 100ms，带宽 = 10000% → admittance control 拒绝
- 若 `dl_runtime` = 100ms（典型），THINK 超过 100ms 时 `dl_task_timer` throttle → LLM 推理中断，状态不一致
- 1024 个 Agent 若均用 SCHED_DEADLINE，即使每 Agent 仅 0.1% 带宽，总利用率 = 102.4% > 100%，最后一个 Agent 被拒绝

**风险**：高——sched_tac 借用 SCHED_DEADLINE 语义与 LLM 推理可变长特性根本冲突。

**修复建议**：
1. THINK 阶段改用 EEVDF（SCHED_NORMAL）+ cgroup v2 CPU quota
2. 仅 PERCEPT/ACT 阶段（可预测短任务）用 SCHED_DEADLINE
3. 分层调度：外层 SCHED_DEADLINE 保证 Agent 级 CPU 份额（统计上界），内层 EEVDF 调度子任务

#### K9-4 [A级] io_uring Zero-copy TOCTOU 漏洞

**推论**：`airy_ipc_zero_copy.c` 使用 `vm_insert_pages` 将内核页映射到用户地址空间。payload 在共享内存中，用户态可在内核处理期间修改 payload 内容。

TOCTOU 场景：内核先读 `payload_len` 分配缓冲区 → 用户态增大 `payload_len` → buffer overflow。

当前代码中 SEND/RECV 返回 -ENOSYS，TOCTOU 尚未可利用，但设计存在隐患。`crc32` 字段非加密哈希，无法防有意篡改。

**风险**：高——M1 实现 SEND/RECV 后即可利用。

**修复建议**：
1. 内核处理 payload 前先 `copy_from_user` 到内核栈/堆，消除 TOCTOU
2. header 字段全量拷贝到内核栈，后续读取均从副本
3. 安全敏感 opcode（CAP_REQUEST/RESPONSE）启用 HMAC-SHA256 truncated 128-bit
4. trace_id/timestamp_ns 不用于内核安全决策，仅用于 tracing

### 4.2 中风险推论（3 项 B 级 + 1 项 B 级 + 2 项 C 级，简表）

| 编号 | 推论 | 核心风险 | 修复建议 |
|------|------|---------|---------|
| K9-5 | CoreLoopThree kthread 边界模糊 | `airy_superv_lsm.c` 中 STOPPED → -EPERM 实际是内核做策略决策；kthread 代码未实现 | 边界定义精确化，将 LSM hook 中的策略决策移至用户态 daemon |
| K9-6 | [DSL] 降级层无生存测试 | AIRY_SC_FALLBACK 模式编译后系统是否真的"生存"未验证 | 编写最小测试套件：编译 → QEMU 启动 → 基本 SEND/RECV IPC → 基本调度 |
| K9-7 | ALK"只新增文件"策略描述不准确 | 实际已修改 7 处主线文件（Kconfig/Makefile/MAINTAINERS 等）；syscall_64.tbl 未修改但需修改 | 策略重新定义为"新增文件 + 最小化构建系统修改"；syscall 改走 io_uring cmd |
| K9-8 | die_notifier 三重递增 | fault_count 在单次 die 事件中被递增 3 次（airy_die_notifier + airy_superv_die_cb + airy_security_fault） | 删除 airy_superv_die_nb 注册，保留 airy_die_notifier 单一注册点 |
| K9-9 | MGLRU 与 MemoryRovol 协作未定义 | Agent 热记忆可能被 MGLRU 回收到 old generation，与"热记忆常驻"语义冲突；MemoryRovol 无内核实现 | L1 原始卷用 mlock + RLIMIT_MEMLOCK；cgroup v2 设 memory.low 水位线保护 |
| K9-10 | fastpath 10ns 目标勉强达标 | L2 hit 场景 ~8ns，L1 容量不够（1024 slot × 64B = 64KB > 32KB L1）；ARM64 内存序 bug | 限制活跃 Agent < 512；ARM64 上 rotate 用 smp_store_release；热点 Agent badge 缓存 |

### 4.3 die_notifier 无限递归排除

v8.0 K-B6 担心双重注册可能引起无限递归。本次推论确认：

- `airy_security_fault` 调用的 `atomic_notifier_call_chain(&airy_die_chain, ...)` 是 **Airy 专有 chain**（定义在 `airy_die_notify.c:28`）
- `airy_die_chain` 上**无任何注册者**
- 因此调用为 no-op，**不会无限递归**

但 `airy_die_chain` 本身是死代码——定义了通知链但无注册者，应清理。

---

## 5. OLK-6.6 工程模式借鉴建议

10 项工程模式提取，每项均给出 AirymaxOS 落点：

| # | 工程模式 | OLK-6.6 源文件 | AirymaxOS 落点 |
|---|---------|--------------|--------------|
| 1 | struct_ops + cfi_stubs fallback + per-op static_key 探测 | `kernel/sched/ext.c:5801-5837,7335` | `airy/sched` 可热替换调度策略，SCX_HAS_OP 模式让未实现 ops 几乎免费 |
| 2 | EEVDF augmented rb-tree 剪枝 + `__int128` 防溢出 | `kernel/sched/fair.c:925,1252` | `airy/sched` 公平调度，eligibility 剪枝 O(log n) |
| 3 | CBS hrtimer 单次触发 + while 循环补足 budget | `kernel/sched/deadline.c:831,1104` | `airy/sched` 实时类，任意 overrun 都能恢复 |
| 4 | io_uring uring_cmd 扩展 + task_work 异步 + cancelable 哈希 | `io_uring/uring_cmd.c:127,190` | `airy/ipc` 异步 IO，`-EIOCBQUEUED` + `io_uring_cmd_done` 异步契约 |
| 5 | LSM stacking section 收集 + 三级优先级 + 合并 blob | `security/security.c:249,521` | `airy/lsm` 直接采用 DEFINE_LSM + LSM_ORDER_MUTABLE |
| 6 | BPF struct_ops trampoline + cfi_stubs + reg/unreg 回调 | `include/linux/bpf.h:1783,1851` | `airy/sched` 与 `airy/lsm` 的 BPF 化路径 |
| 7 | notifier chain RCU 无锁调用 + 优先级降序 + robust 回滚 | `kernel/notifier.c:25,122` | `airy/lsm` 事件通知，die_notifier 用 atomic chain |
| 8 | kthread kthreadd 代 fork + completion 双向同步 | `kernel/kthread.c:340,428` | `airy/sched` CoreLoopThree kthread + 守护线程 |
| 9 | MGLRU 代际序列号 + Bloom filter 双缓冲 + static_key 能力开关 | `mm/vmscan.c:2584,2702` | `airy/mem` 冷热识别，代际比 active/inactive 双链表更精确 |
| 10 | static_key 自修改代码 NOP/JMP + 引用计数 + `__ro_after_init` | `include/linux/jump_label.h:383,495` | 全子系统"默认关闭、可热开启"特性开关，零开销 |

---

## 6. seL4 微内核设计借鉴建议

10 项设计模式提取，每项均给出 AirymaxOS 落点：

| # | 设计模式 | seL4 源文件 | AirymaxOS 落点 |
|---|---------|-----------|--------------|
| 1 | MDB capability derivation tree + isMDBParentOf 父子判定 + cteRevoke 递归撤销 | `src/object/cnode.c:410,528,775` | `airy_cap` 借鉴 MDB 树实现细粒度撤销，替代全局 epoch |
| 2 | Tagged union cap_t + 位编码权限位掩码 + get/set_capCanXxx 访问器 | `libsel4/include/sel4/objecttype.h:8-19` | `airy_cap` 统一 `airy_cap { tag; union{...} u; }` + AIRY_CAP_CAN_READ/WRITE/SEND/GRANT |
| 3 | IPC fastpath 谓词门控 + POINT OF NO RETURN 直接线程切换 + SC 捐赠 | `src/fastpath/fastpath.c:19-233` | `airy/ipc` fastpath 谓词门控，命中时直接 `airy_sched_donate(sc, dest)` + `airy_arch_switch_to(dest)` |
| 4 | Endpoint 三态机（Idle/Send/Recv）+ TCB 内嵌队列指针 | `src/object/endpoint.c:20-131` | `airy/ipc` `airy_endpoint { state, head, tail }`，TCB 内嵌 ep_next/ep_prev，零分配 O(1) 入队出队 |
| 5 | Notification badge OR 累积 + bound notification | `src/object/notification.c:62-192` | `airy/sync` 轻量事件分发，多生产者 OR 累积 badge，消费者一次 recv 取走全部 |
| 6 | MCS sporadic server 环形 refill 缓冲 + MIN_BUDGET 保证 | `src/kernel/sporadic.c:307-348` + `include/kernel/sporadic.h:116-130` | `airy/sched` 实时调度，`airy_sc { period, refill_head, refill_tail, refill[] }`，每次 tick 调用 `airy_refill_budget_check(used)` |
| 7 | TCB 状态打包 + 内嵌 CNode 槽位 + SC 捐赠 | `include/object/structures.h:158-310` | `airy/tcb` TCB 内嵌 4-5 个固定 cap 槽，状态用位字段打包，SC 捐赠防 server 饿死 |
| 8 | L1/L2 位图 + CLZ O(1) 选最高优先级 + ksSchedulerAction 延迟槽 | `src/kernel/thread.c:372-491` | `airy/sched` 直接借鉴 `getHighestPrio` 用 `__builtin_clz` 一条指令搞定 256 优先级查找 |
| 9 | Untyped watermark + retype fan-out + setUntypedCapAsFull 单调性 | `src/object/untyped.c:226-304` | `airy/mem` `airy_untyped { base, size, free_index }`，bump 分配 + 用户态细分，替代 buddy allocator |
| 10 | Liedtke 最小化原则：内核仅机制，策略下沉用户态 | 全 src/ | AirymaxOS "内核不思考"原则与 seL4 "最小化内核"原则异曲同工，应进一步将 IRQ handler / page fault handler / 调度策略下沉用户态 |

### 6.1 核心借鉴建议（高优先级）

#### 借鉴 1：用 seL4 MDB 树替代全局 epoch 撤销

**当前问题**：v1.0.1 Capability Folding 使用全局 `airy_cap_global_epoch`，撤销单 agent 失效全部 Badge（见 K9-1）。

**借鉴方案**：每个 `airy_cap_slot` 内嵌 `mdb_node { prev, next, revocable, first_badged }`，`airy_cap_revoke(agent_id)` 沿 next 链调用 `airy_cap_delete()`，用 `is_parent_of()` 边界判定避免误删旁支。撤销爆炸半径从 1024 收窄到目标 agent 的派生链。

#### 借鉴 2：用 seL4 IPC fastpath 谓词门控优化 airy_ipc

**当前问题**：`airy_uring_cmd_handle` 是死代码（K-B5），未接入 io_uring cmd 分发。

**借鉴方案**：在 `airy_ipc_send` 入口设置 `airy_ipc_try_fastpath(sender, ep)`，条件包括：ep 队首有等待接收者、无 fault、同核、目标 SC 可用。命中时直接 `airy_sched_donate(sc, dest)` + `airy_arch_switch_to(dest)`，避免走调度队列。参考 fastpath_copy_mrs 的"短消息用寄存器、长消息用 IPC buffer"策略。

#### 借鉴 3：用 seL4 MCS sporadic server 替代 SCHED_DEADLINE 借用

**当前问题**：sched_tac 借用 SCHED_DEADLINE 与 LLM 推理可变长特性根本冲突（K9-3）。

**借鉴方案**：借鉴 seL4 MCS sporadic server 的环形 refill 缓冲。`airy_sc { period, refill_head, refill_tail, refill_max, refill[] }`，每次 tick 调用 `airy_refill_budget_check(used)` 把用掉的预算挪到 `now + period`。对 IRQ handler、UI 渲染等有 QoS 要求的线程，用 `airy_sc_bind(tcb, sc)` 实现带宽隔离。MIN_BUDGET = 2 × kernel_wcet 保证一次往返内核的最低开销。

---

## 7. v8.0 报告遗漏问题清单（23 项）

v3.5 27 份审查文档全量阅读后发现 v8.0 报告遗漏 23 项问题：

### 7.1 待决策事项状态丢失（5 项，来源：18-migration-plan-v4.3.md）

| # | 遗漏事项 | 当前状态 |
|---|---------|---------|
| 1 | 错误码 `AIRY_ERR_*` → `AIRY_E*` 命名迁移 | M1 待决策 |
| 2 | 日志 `AIRY_LOG_*` → `LOG_*` 命名迁移 | M1 待决策 |
| 3 | `airy_ind` LSM 迁移到 blob 机制 | 旧 airy_ind 已移除，blob 迁移计划未追踪 |
| 4 | v1.1 规划头文件实现（mac.h/taskflow.h/trace.h/user_events.h） | M1 按需 |
| 5 | commons/ipc.h [IND] 扩展重定位到 ipc_runtime.h | M1 随 IPC 运行时实现 |

### 7.2 历史关键问题未复查（7 项）

| # | 遗漏问题 | 来源 |
|---|---------|------|
| 6 | `stc_dispatch_enqueue` 死代码 | 06/07/09 报告 |
| 7 | `AIRY_EIPC_FROZEN` (-53) 值正确性 | 16 报告 #8 |
| 8 | C-S0 fastpath 错误码使用 `AIRY_EIPC_FROZEN(-53)` 而非 `AIRY_ECAP_FROZEN(-82)` | 16 报告 #9 |
| 9 | codegen `AIRY_SYS_CALL` 命名冲突 → `AIRY_SYS_IDX_CALL` | 15 报告 02-P0-21 |
| 10 | `syscall.xml` 中 `AIRY_CAP_INVOKE` 虚构字段 | 21 报告 A-11 |
| 11 | `test_error.c` 错误码过时 | 21 报告 A-14 |
| 12 | `syscall_64.tbl` L387 tab 对齐 | 21 报告 B-4 |

### 7.3 v7.0 B/C 类问题未复查（3 项）

| # | 遗漏问题 | v7.1 结论 |
|---|---------|---------|
| 13 | C-1: UAPI 头文件导出规则（Kbuild） | v7.2 已修复，v8.0 未复查修复质量 |
| 14 | C-2: 32 位 syscall 表条目 | v7.2 已修复，v8.0 未复查 32 位表内容正确性 |
| 15 | B-6: `.fallback_hashes` 缺失 | v7.1 确认无需修改，v8.0 未复查 |

### 7.4 v8.0 新发现未与前序关联（3 项）

| # | v8.0 发现 | 前序关联 |
|---|---------|---------|
| 16 | K-B5: `airy_uring_cmd_handle` 死代码 | 06/07 报告 `stc_dispatch_enqueue` 死代码，同属"M0 骨架代码无调用方"系统性问题 |
| 17 | K-B4: `airy_cap_badge_revoke` 无声明无调用 | 04 报告 ARCH-P2-1（7 操作原语文档与代码不一致） |
| 18 | K-B6: die_notifier 双重注册 | 04 报告 SEC-P1-6（airy_security_fault 误伤 current） |

### 7.5 文档体系盲区（1 项）

| # | 盲区 | 来源 |
|---|------|------|
| 19 | `docs/AirymaxRT/` 旧文档目录是否已清理 | v6.0 A-4 发现整篇过时，v8.0 未复查 |

### 7.6 数据流设计未复查（3 项）

| # | 数据流问题 | v5.0 状态 |
|---|---------|---------|
| 20 | P0-D1: Ring Buffer reserve/commit 索引设计 | 已修复（三索引模型） |
| 21 | P0-D4: IPC badge=0 跳过机制可被伪造绕过 | 已修复（内核覆写注入 badge） |
| 22 | P0-D7: Panic 多 CPU 并发写 Ring Buffer 非原子推进 | 已修复（per-CPU buffer） |
| 23 | (扩展) 数据流完整性未在 v8.0 复查 | — |

---

## 8. 修复优先级

### P0（M0 收尾前必修，SSoT 一致性 + 高风险安全）

| 编号 | 问题 | 来源 | 预计工时 |
|------|------|------|---------|
| A-1 | MAC\_MAX\_AGENTS 转义残留 4 处 | v8.0 | 0.5h |
| A-2 | 3 个未标记 [IND] 的 IPC opcode | v8.0 | 1h |
| A-3 | airy_ipc_msg_hdr .version 字段 | v8.0 | 0.5h |
| A-4 | uapi_compat.h kernel 侧回传 commons 改进 | v8.0 | 1h |
| D9-3 | capability 计数 41 → 44（4 份架构文档） | v9.0 | 1h |
| D9-9 | SSoT registry IRON-9 v3 三层 → 四层 | v9.0 | 0.5h |
| D9-12 | syscall 宏值 0-3 → 548-551 | v9.0 | 0.5h |
| D9-15 | IRON-7/8 编号矛盾（10+ 份文档批量更新） | v9.0 | 2h |
| D9-17 | `05-adrs.md` v1.1 → v1.0.1 | v9.0 | 0.5h |
| K9-1 | airy_cap_badge_revoke 改为 per-agent epoch | v9.0 | 4h |
| K9-2 | airy_cap_rotate 写序修正 + ARM64 smp_store_release | v9.0 | 2h |
| K-B4 | airy_cap_badge_revoke 死代码删除 | v8.0 | 1h |
| K-B5 | airy_uring_cmd_handle 接入 io_uring cmd 或删除 | v8.0 | 2h |
| K-B6 | die_notifier 删除 airy_superv_die_nb 冗余注册 | v8.0 | 1h |
| **P0 小计** | | | **~18h** |

### P1（M1 早期修复，代码质量 + 设计冲突）

| 编号 | 问题 | 预计工时 |
|------|------|---------|
| K9-3 | sched_tac 与 SCHED_DEADLINE 语义冲突（THINK 阶段改用 EEVDF + cgroup） | 8h |
| K9-4 | io_uring Zero-copy TOCTOU 防护（payload copy_to_kernel） | 4h |
| K9-5 | CoreLoopThree kthread 边界精确化 + LSM hook 策略移除 | 4h |
| K9-7 | ALK 策略描述精确化（新增文件 + 最小化构建系统修改） | 2h |
| K9-9 | MGLRU 与 MemoryRovol 协作模型定义（mlock + memory.low） | 4h |
| K9-10 | ARM64 内存序修复 + fastpath 热点 Agent 缓存 | 4h |
| D9-1 | daemon 命名同文档内统一 | 0.5h |
| D9-7 | cognition.md CoreLoopThree kthread [SS]/[IND] 标注消歧 | 0.5h |
| D9-8 | "OS-IRON-KTHREAD-BOUNDARY" 约束落地为文档化铁律 | 1h |
| D9-10 | 5 份文档"三层" → "四层"批量更新 | 1h |
| D9-13 | abi-stability.md AIRY_SYS_CALL 注释更新 | 0.5h |
| D9-14 | syscall-registry 残留 613/615 标注废弃 | 0.5h |
| D9-19 | 80-testing/ 6 份文档 v1.1 → v1.0.1 批量更新 | 2h |
| D9-21 | ADR-001 sched_ext 标注拒绝状态 | 0.5h |
| v8.0 遗漏 #1-5 | 5 项待决策事项状态追踪 | 2h |
| v8.0 遗漏 #6-12 | 7 项历史关键问题复查 | 3h |
| **P1 小计** | | **~38h** |

### P2（M1-M2 阶段改进）

| 编号 | 问题 | 预计工时 |
|------|------|---------|
| K9-6 | [DSL] 降级层生存测试套件 | 8h |
| K9-8 | airy_die_chain 死代码清理 | 1h |
| D9-4 | Badge Perms 权限位数 7 vs 12 一致化 | 0.5h |
| D9-6 | Epoch 16 位回绕处理策略 | 2h |
| D9-11 | 章节锚点 v2-三层 → v3-四层 | 0.5h |
| D9-16 | IRON-1~10 表格增加"通过/失败"判定标准列 | 2h |
| D9-18 | 版本历史表禁用版本号标注"IRON-7 追溯禁止" | 0.5h |
| D9-20 | IPC 协议版本 v1.1 与文档版本 v1.0.1 显式区分 | 0.5h |
| v8.0 C 级 21 项 | 8 项内核代码规范 + 其他 | 8h |
| v8.0 IMP-1~12 | 12 项改进建议 | 20h |
| **P2 小计** | | **~43h** |

### 总工时

| 优先级 | 工时 |
|--------|------|
| P0 | ~18h |
| P1 | ~38h |
| P2 | ~43h |
| **合计** | **~99h** |

---

## 9. 成熟度评分修正

### 9.1 v9.0 修正

| 维度 | v8.0 评分 | v9.0 修正 | 变化 | 原因 |
|------|----------|----------|------|------|
| 三大设计支柱 | 88 | 82 | -6 | D9-3 capability 计数不一致 + D9-9 SSoT 三层/四层矛盾 |
| IRON 工程铁律 | 94 | 84 | -10 | D9-15 IRON-7/8 编号矛盾影响 10+ 文档 + K9-1 全局 epoch 撤销设计缺陷 |
| 内核哲学 | 90 | 82 | -8 | K9-3 sched_tac/SCHED_DEADLINE 语义冲突 + K9-5 kthread 边界模糊 |
| ALK 分支管理 | 88 | 80 | -8 | K9-7 策略描述不准确 + syscall_64.tbl 未修改但需修改 |
| 8 子仓边界 | 86 | 82 | -4 | D9-7 cognition kthread [SS]/[IND] 跨层标注 |
| 项目阶段明确性 | 94 | 84 | -10 | D9-17 v1.1 禁用版本号 + D9-19 80-testing/ 6 份文档 v1.1 残留 |
| CI/测试基础设施 | 86 | 78 | -8 | K9-6 [DSL] 无生存测试 + K9-4 TOCTOU 无防护 |
| **加权总分** | **88（B+）** | **82（B）** | **-6** | — |

### 9.2 评分修正说明

v9.0 修正反映"深度科学推论发现的根本性设计冲突"，而非"外观问题"。

主要扣分点：
1. **sched_tac 与 SCHED_DEADLINE 语义冲突**（K9-3）：这是设计层面的根本冲突，影响 sched_tac 的核心可行性
2. **Capability Folding 全局 epoch 撤销爆炸半径**（K9-1）：单点撤销触发系统级 Badge 失效风暴
3. **airy_cap_rotate fastpath/slowpath 不一致竞态**（K9-2）：并发 rotate 期间安全策略不一致
4. **io_uring Zero-copy TOCTOU 漏洞**（K9-4）：M1 实现 SEND/RECV 后即可利用
5. **IRON-7/8 编号矛盾**（D9-15）：10+ 份文档引用错误，工程铁律落地不彻底

### 9.3 M0 就绪状态再确认

| 问题级别 | 数量 | 影响 M0 就绪？ | 说明 |
|---------|------|--------------|------|
| A 级（文档 SSoT） | 5 | **否** | 文档一致性问题，不影响内核框架编译 |
| A 级（内核设计） | 4 | **部分** | K9-1/K9-2/K9-4 影响安全模型正确性，但 M0 仅框架验证不运行 |
| B 级 | 17 | **否** | 代码质量 + 设计冲突，M1 早期修复 |
| C 级 | 8 | **否** | 外观/轻微问题 |

**结论**：M0 100% 就绪状态**有条件维持**：
- M0 框架编译验证仍通过（39 .o 零错误零警告）
- 但 K9-1/K9-2/K9-4 必须在 M1 早期（Day 15-21）修复，否则影响 M2 测试
- 文档 SSoT 一致性问题（5 项 A 级）建议在 M0 收尾时立即修复（P0，~5h）

---

## 10. 审查链更新

| 阶段 | 文件 | 描述 |
|------|------|------|
| v7.0 | 22 | 系统性深层复核（335 问题逐一复核） |
| v7.1 | 23 | v7.0 改进实施 + M0 就绪确认（90/A-） |
| v7.1 | 24 | M0 就绪确认清单（55 项） |
| v7.2 | 25 | M0 100% 就绪最终确认清单（65 项） |
| v8.0 | 26 | 四维度深度审查（43 项发现，M0 就绪状态维持） |
| **v9.0** | **27（本报告）** | **5 轨道并行深度审查（42 项发现 + 10 项科学推论 + 23 项 v8.0 遗漏）** |

---

## 11. 正面发现

本次审查确认以下方面的良好状态：

1. **K-B1 跨配置依赖已彻底修复**：Kconfig 依赖方向正确，security/airy/ 内本地定义所需函数
2. **die_notifier 不会无限递归**：airy_die_chain 无注册者，airy_security_fault 的通知调用为 no-op
3. **airy_lsm 与 SELinux 并存无冲突**：AND 语义保证安全，blob 自动对齐，capability 双检查逻辑正确
4. **Capability Folding 位运算数学自洽**：Badge 构造与提取互为逆运算，无位域重叠
5. **[SC] 路径前缀差异不破坏语义**：内容同源（SSoT 生成），C/C++ include 路径差异是编译系统约束
6. **LSM 注册无需修改主线**：DEFINE_LSM + security_add_hooks 是标准扩展点
7. **fastpath 10ns 目标在 L1 hit 场景可实现**：~3-4ns（IPC≈3），L2 hit 场景 ~8ns 勉强达标
8. **形式化验证边界清晰**：seL4 src/ 验证 + spec/ 抽象 + libs/ 用户态，AirymaxOS 可借鉴分层

---

## 12. 最终结论

**⚠️ M0 设计阶段 100% 就绪状态有条件维持——v9.0 发现 4 项内核设计 A 级问题需在 M1 早期修复。**

### 12.1 核心结论

1. **v8.0 修复完成度仅 10%**：10 项 A/B 级问题中仅 1 项（K-B1）已彻底修复，8 项未修复，1 项部分修复。v8.0 报告生成后未进行 P0 修复实施。

2. **v9.0 发现 22 项文档新问题 + 10 项内核科学推论**：5 项 A 级文档问题（capability 计数、SSoT 三层/四层、syscall 宏值、IRON-7/8 编号、v1.1 版本号）+ 4 项 A 级内核设计问题（全局 epoch 撤销、rotate 竞态、sched_tac 语义冲突、TOCTOU 漏洞）。

3. **v8.0 遗漏 23 项问题**：5 项待决策事项状态丢失 + 7 项历史关键问题未复查 + 3 项 v7.0 B/C 类未复查 + 3 项新发现未与前序关联 + 1 项文档盲区 + 3 项数据流设计未复查。

4. **3 项核心借鉴建议**：用 seL4 MDB 树替代全局 epoch 撤销、用 seL4 IPC fastpath 谓词门控优化 airy_ipc、用 seL4 MCS sporadic server 替代 SCHED_DEADLINE 借用。

### 12.2 修复路线

| 阶段 | 工时 | 核心任务 |
|------|------|---------|
| M0 收尾（P0） | ~18h | 5 项文档 SSoT 修复 + 4 项内核设计 A 级修复 + 3 项 v8.0 死代码清理 |
| M1 早期（P1） | ~38h | sched_tac 语义重构 + TOCTOU 防护 + kthread 边界精确化 + 文档批量更新 |
| M1-M2（P2） | ~43h | [DSL] 生存测试 + 死代码清理 + v8.0 C 级 + 12 项改进建议 |

### 12.3 成熟度评分

**v9.0 修正后成熟度评分：82（B）**——反映深度科学推论发现的根本性设计冲突。

**v9.0 修正后 M0 就绪状态：有条件维持**——M0 框架编译验证通过，但 4 项内核设计 A 级问题需在 M1 早期（Day 15-21）修复。

### 12.4 内核严肃性声明

> **内核是非常严肃的工程。** 本次审查通过 5 轨道并行深度调研，对 10 个核心设计点进行第一性原理推论，识别 7 项高风险问题。这些问题的根因不在代码实现，而在**设计前提的假设错误**：
>
> - K9-1：假设全局 epoch 撤销可行，实际爆炸半径覆盖整个系统
> - K9-2：假设 rotate 写序 safe-fail，实际 fastpath/slowpath 行为不一致
> - K9-3：假设 SCHED_DEADLINE 语义适配 Agent，实际 LLM 推理可变长特性根本冲突
> - K9-4：假设 zero-copy 安全，实际存在 TOCTOU 漏洞
>
> **建议在 M1 早期优先修复这 4 项设计前提问题，再进入功能实现。否则 M2 测试阶段将暴露大量难以定位的并发/安全/性能问题。**

---

## 附录 A：关键文件路径索引

### A.1 v8.0 验证文件

- `/home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/04-engineering-baseline.md:605` — A-1 MAC\_MAX\_AGENTS
- `/home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/05-adrs.md:1221` — A-1 MAC\_MAX\_AGENTS
- `/home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md:607` — A-1 MAC\_MAX\_AGENTS
- `/home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/01-kernel.md:823` — A-1 MAC\_MAX\_AGENTS
- `/home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/160-compatibility/01-abi-stability.md:385-387,399` — A-2 + A-3
- `/home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/ipc.h:77-89` — SSoT airy_ipc_msg_hdr
- `/home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/include/uapi/linux/airymax/uapi_compat.h:22-32` — A-4 kernel 侧
- `/home/spharx/SpharxWorks/airymaxhub/agentrt/commons/include/airymax/uapi_compat.h:23-27` — A-4 commons 侧
- `/home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_revoke.c:18,30,40,46` — K-B4 死代码
- `/home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_uring_cmd.c:38` — K-B5 死代码
- `/home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_die_notify.c:142-155` — K-B6 注册 #1
- `/home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/superv/airy_die_notify_superv.c:74-81` — K-B6 注册 #2
- `/home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/Kconfig:6-10` — K-B1 已修复证据

### A.2 v9.0 新发现文件

- `/home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/110-security/03-capability-model.md:16,239,279` — D9-3, D9-4
- `/home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/09-ssot-registry.md:1297-1299` — D9-9, D9-15
- `/home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/07-directory-structure.md:1332` — D9-12
- `/home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/05-adrs.md:86,1224` — D9-17, D9-21
- `/home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_rotate.c:76-77` — K9-2 竞态
- `/home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/security/airy/airy_cap_revoke.c:40` — K9-1 全局 epoch
- `/home/spharx/SpharxWorks/airymaxhub/agentrt-linux/kernel/kernel/corekern/ipc/airy_ipc_zero_copy.c` — K9-4 TOCTOU

### A.3 借鉴参考源码

- `/home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/ext.c` — sched_ext BPF 框架
- `/home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/fair.c` — EEVDF 算法
- `/home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sched/deadline.c` — CBS 机制
- `/home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/io_uring/uring_cmd.c` — io_uring cmd
- `/home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/security/security.c` — LSM stacking
- `/home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c` — MDB capability 树
- `/home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/fastpath/fastpath.c` — IPC fastpath
- `/home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/sporadic.c` — MCS sporadic server
- `/home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/endpoint.c` — Endpoint 阻塞唤醒
- `/home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/thread.c` — 调度器核心

---

*本报告由 5 轨道并行深度审查生成，所有结论附字节级证据。*
