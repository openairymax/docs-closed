Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agent-linux 深层一致性审查报告 v3.1

> **审查日期**：2026-07-23\
> **审查范围**：`docs/AirymaxOS/` 全部文档 + `agent-linux/kernel/` 代码 + `docs-closed/agent-linux/` 闭源文档\
> **审查方法**：SSoT 权威源逐行交叉验证 + 代码-文档双向比对\
> **前序版本**：v3.0 深层一致性审查（02-deep-consistency-audit-v3.0.md）

---

## 审查摘要

| 严重级别 | 数量 | 说明 |
|---------|------|------|
| **P0** | 5 | 直接违反 SSoT 权威或 IRON 硬约束 |
| **P1** | 3 | 文档间不一致，需在 M1 前修复 |
| **已确认正确** | 7 | 经过验证的一致项 |

---

## P0 级问题

### P0-019：07-syscall-registry.md（SSoT）中 REGISTER_BPF opcode 与 H5 直接冲突

**证据**：

[07-syscall-registry.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/140-application-development/07-syscall-registry.md) 是 syscall 编号的 **SSoT**（L4-8 声称为唯一权威源），其中：

- L66：`550 | AIRY_SYS_SCHED_CTL | 控制原语 | sched_tac 调度策略配置 | SET_POLICY / GET_POLICY / REGISTER_BPF / GET_LATENCY / SET_PRIORITY / GET_VTIME / YIELD`
- L110：同上
- L183：`AIRY_SCHED_REGISTER_BPF | 注册 eBPF 调度器 | 注册 eBPF 调度器程序 | airy_sys_sched_register_bpf（0.1.1 编号 574）`
- L370：`#define AIRY_SCHED_REGISTER_BPF 0x03`

**冲突**：

- [H5](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md#L392-398) 明确规定：airy_lsm 是纯 C 实现，禁止依赖 `BPF_SYSCALL` / `BPF_JIT` / `DEBUG_INFO_BTF`
- [sched_tac](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md#L332) 明确：使用 SCHED_DEADLINE/SCHED_FIFO/EEVDF，**不使用 sched_ext**
- [00-alk-kernel-overview.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md#L76-84) 列出 5 条不使用 sched_ext 的理由
- `AIRY_SCHED_REGISTER_BPF` 语义为"注册 eBPF 调度器"，与 sched_tac 的纯 C 调度选型直接矛盾

**影响**：syscall 编号 SSoT 中出现与核心架构约束（H5）冲突的 opcode 定义，任何引用本 SSoT 的实现都可能错误地引入 BPF 调度路径。

**修复建议**：将 `AIRY_SCHED_REGISTER_BPF` 重命名为 `AIRY_SCHED_SET_BUDGET`（设置调度预算），语义从"注册 eBPF 调度器"改为"sched_d 通过 syscall 注入调度预算参数"，对齐 [09-kernel-agent-supervisor.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/09-kernel-agent-supervisor.md#L116-123) 的 `SCHED_SET_BUDGET` 子命令。

同时修复 contracts.md L639 的 REGISTER_BPF 引用。

---

### P0-020：Agent 8 态生命周期三重不一致

**证据**：

三个文档对 Agent 8 态给出完全不同的定义：

| 文档 | 8 态名 | 行号 |
|------|--------|------|
| [10-sc-sched-extension.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/10-sc-sched-extension.md)（SSoT） | INACTIVE / SPAWNING / READY / RUNNING / BLOCKED / STOPPING / STOPPED / DEAD | L56-85 |
| [00-alk-kernel-overview.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md) | REGISTERED / CONFIGURED / RUNNING / PAUSING / PAUSED / SUSPENDED / TERMINATING / TERMINATED | L336-345 |
| [09-kernel-agent-supervisor.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/09-kernel-agent-supervisor.md) | CREATED / READY / RUNNING / STOPPED / DEAD（5 态，PAUSED/DEGRADED/TERMINATED 为子态） | L103-106 |

**SSoT 权威声明**：
- [10-sc-sched-extension.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/10-sc-sched-extension.md#L14) 声明为 "Agent 8 态生命周期枚举...以本文件为唯一权威定义"
- [09-ssot-registry.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/09-ssot-registry.md#L167) §1.7 技术点 #11 登记：Agent 8 态 -> 权威源 [01-agent-lifecycle.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/140-application-development/01-agent-lifecycle.md)，物理宿主 [SC] `cognition_types.h`

**冲突**：
- 00-alk-kernel-overview.md 声称为 "ALK-6.6 内核总体架构的唯一权威定义文档"（L5），但其 Agent 状态与 SSoT 完全不符
- 09-kernel-agent-supervisor.md 声称 "对齐 10-sc-sched-extension.md"（L100），但实际使用 5 态+子态模型，与 SSoT 的 8 态完全不同
- 多处文档引用不同状态名，如 [80-testing/08-agent-contract-testing.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/80-testing/08-agent-contract-testing.md#L28) 使用 INACTIVE/SPAWNING/READY/RUNNING/BLOCKED/STOPPING/STOPPED/DEAD（正确），而 [150-cloudnative/02-containerd-shim.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/150-cloudnative/02-containerd-shim.md#L250) 使用 TERMINATING（错误）

**影响**：Agent 生命周期是 A-ULS 模块的核心契约，三重不一致将导致内核态 Micro-Supervisor、用户态 Macro-Supervisor、K8s containerd-shim 三端对 Agent 状态机理解不一致，引发调度错误、冻结遗漏、级联故障。

**修复建议**：
1. 以 [10-sc-sched-extension.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/10-sc-sched-extension.md) 的 8 态（INACTIVE/SPAWNING/READY/RUNNING/BLOCKED/STOPPING/STOPPED/DEAD）为唯一权威
2. 重写 [00-alk-kernel-overview.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md#L320-348) §7.2 章节
3. 修正 [09-kernel-agent-supervisor.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/09-kernel-agent-supervisor.md#L100-114) §1.5，使其与 SSoT 一致（或明确标注为调度视角的简化视图）
4. 全局扫描所有文档中的 Agent 状态名，确保无一例外

---

### P0-021：00-alk-kernel-overview.md §9.1 LSM_ORDER_FIRST 错误

**证据**：

[00-alk-kernel-overview.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md#L384)：

```
| **L3** | **capability（airy_lsm）** | **seL4 风格 + POSIX，纯 C** | **LSM_ORDER_FIRST** |
```

**冲突**：

[01-lsm-framework.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/110-security/01-lsm-framework.md#L18)（LSM 框架 SSoT）明确：

> OLK 6.6 `include/linux/lsm_hooks.h:113` 注释明确 `LSM_ORDER_FIRST` "This is only for capabilities."——**airy_lsm 不使用 `LSM_ORDER_FIRST`**，改用 `LSM_ORDER_MUTABLE`

[09-kernel-agent-supervisor.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/09-kernel-agent-supervisor.md#L160) 代码：

```c
DEFINE_LSM(airy) = {
    .name = "airy",
    .order = LSM_ORDER_MUTABLE,   /* v1.0.1: LSM_ORDER_MUTABLE + CONFIG_LSM 首位 */
};
```

[20-modules/01-kernel.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/01-kernel.md#L494)：

> `LSM_ORDER_FIRST` 仅用于 capabilities（早期启动阶段）

**影响**：如果按照 00-alk-kernel-overview.md 的实现，airy_lsm 将使用 `LSM_ORDER_FIRST`——这会与 OLK 6.6 的 `capability` 模块冲突，因为 `LSM_ORDER_FIRST` 是 capabilities 独占的，且 OLK 6.6 注释明确禁止其他模块使用。

**修复建议**：将 L384 的 `LSM_ORDER_FIRST` 改为 `LSM_ORDER_MUTABLE`（通过 `CONFIG_LSM` 置于 `capability` 之后第一位）。

---

### P0-022：00-alk-kernel-overview.md §9.1 eBPF 签名 L4 安全层与 H5 冲突

**证据**：

[00-alk-kernel-overview.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md#L385)：

```
| L4     | 模块签名                      | eBPF 签名                 | 独立                    |
```

**冲突**：

- 同一文档 §9.2（L390-398）明确 H5 硬约束：禁止依赖 `BPF_SYSCALL` / `BPF_JIT` / `DEBUG_INFO_BTF`
- 如果 L4 安全层是 "eBPF 签名"，则引入了 BPF 依赖，违反 H5
- 在 v3.1 eBPF 深层残留清除中，[03-security.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/03-security.md) 的 "eBPF 签名验证" 已被改为 "纯 C LSM 编译期校验 + CBMC 形式化验证"

**影响**：SSoT 级文档中保留 eBPF 签名安全层，与 H5 硬约束直接矛盾。

**修复建议**：将 L4 改为：

```
| L4     | 代码完整性验证                  | 编译期校验 + CBMC 形式化验证（H5） | 独立                    |
```

---

### P0-023：00-alk-kernel-overview.md 声明为 SSoT 但多处内容与 SSoT 源矛盾

**证据**：

[00-alk-kernel-overview.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md#L5) 声明：

> "ALK-6.6 内核总体架构的唯一权威定义文档"

但以下内容与真正的 SSoT 源矛盾：

| 主题 | 00-alk-kernel-overview.md 内容 | 实际 SSoT | 问题 |
|------|-------------------------------|-----------|------|
| Agent 8 态 | REGISTERED/CONFIGURED/...（L336-345） | 10-sc-sched-extension.md: INACTIVE/SPAWNING/... | P0-020 |
| LSM 排序 | LSM_ORDER_FIRST（L384） | 01-lsm-framework.md: LSM_ORDER_MUTABLE | P0-021 |
| 安全层 L4 | eBPF 签名（L385） | H5: 纯 C LSM + CBMC | P0-022 |
| REGISTER_BPF | 未直接提及，但引用 07-syscall-registry.md | 07-syscall-registry.md 含 REGISTER_BPF | P0-019 |

**影响**：00-alk-kernel-overview.md 是 ALK-6.6 的入口文档，其错误会被所有子文档引用传播。

**修复建议**：完成 P0-020/P0-021/P0-022 修复后，在 00-alk-kernel-overview.md 的 SSoT 声明中增加免责声明：本文件是 ALK-6.6 物理形态与改造范围的唯一权威，但 Agent 状态机、LSM 排序、安全层等子主题的细节以各自 SSoT 为准。

---

## P1 级问题

### P1-03：contracts.md 残留 REGISTER_BPF 引用

**证据**：

[contracts.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/20-contracts/contracts.md#L639)：

```
| 550 | `airy_sys_sched_ctl`（REGISTER_BPF） | 注册 sched_tac 用户态调度策略 | `ops_fd`（struct airy_sched_ops 描述符 fd）、`ops`（struct airy_sched_ops 指针） |
```

**影响**：与 P0-019 同源，contracts.md 作为 API 契约文档也应同步修复。

**修复建议**：与 P0-019 一同修复，将 `REGISTER_BPF` 改为 `SET_BUDGET`。

---

### P1-04：IRON-9 v3 §10.1 [SS] 层描述含 "struct_ops"

**证据**：

[00-alk-kernel-overview.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md#L420)：

```
| **\[SS] 语义同源层**  | 高层 API 语义同源      | sched_tac / io_uring / struct_ops 等 30+ 项 | 各自独立实现 |
```

**分析**：`struct_ops` 是 BPF 基础设施的一部分（`BPF struct_ops`），虽然在可观测性上下文（非核心架构）中可以使用，但放在 [SS] 语义同源层中作为核心列举项不够精确。

**修复建议**：将 `struct_ops` 从 [SS] 核心列举中移除，或标注为 "可观测性（非核心架构，H5 约束）"。

---

### P1-05：09-kernel-agent-supervisor.md §1.5 声称对齐 SSoT 但不对齐

**证据**：

[09-kernel-agent-supervisor.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/09-kernel-agent-supervisor.md#L100)：

```
**Agent 8 态生命周期与 sched_tac 集成**（对齐 10-sc-sched-extension.md）
```

但随后使用的状态模型（L103-106）是 CREATED/READY/RUNNING/STOPPED/DEAD 5 态+子态，与 SSoT 的 INACTIVE/SPAWNING/READY/RUNNING/BLOCKED/STOPPING/STOPPED/DEAD 8 态不一致。

**修复建议**：
- 方案 A：将 §1.5 明确标注为 "Micro-Supervisor 调度视角的简化视图（5 主态 + 3 子态）"，并在开头引用 SSoT 的完整 8 态定义
- 方案 B：直接改为 8 态模型，与 SSoT 完全对齐

---

## 已确认正确（7 项）

### 正确项 1：syscall 编号 548-551 三方一致
- [07-syscall-registry.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/140-application-development/07-syscall-registry.md)（SSoT）：548-551 ✅
- [unistd.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/asm-generic/unistd.h#L833-840)：`__NR_airy_sys_call 548` 等 ✅
- [syscall_64.tbl](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/arch/x86/entry/syscalls/syscall_64.tbl#L384-387)：548-551 ✅
- [00-alk-kernel-overview.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md#L96)：4 核心 syscall（548-551）✅

### 正确项 2：airy_superv_lsm.c 重命名一致性
- [kernel/superv/airy_superv_init.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/superv/airy_superv_init.c)：已重命名 ✅
- [kernel/superv/Kbuild](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/superv/Kbuild#L11)：`airy_superv_init.o` ✅
- [security/airy/airy_superv_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_superv_lsm.c#L9)：引用 `kernel/superv/airy_superv_init.c` ✅
- [00-alk-kernel-overview.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md#L130)：`airy_superv_init.c` ✅
- [07-directory-structure.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/07-directory-structure.md#L549-554)：5 个文件全部 `_superv` 后缀 ✅

### 正确项 3：H5 纯 C LSM 核心约束一致性
- [00-alk-kernel-overview.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md#L389-398) §9.2：H5 硬约束清晰 ✅
- [01-lsm-framework.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/110-security/01-lsm-framework.md#L18)：LSM_ORDER_MUTABLE 正确 ✅
- [09-kernel-agent-supervisor.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/09-kernel-agent-supervisor.md#L160)：DEFINE_LSM LSM_ORDER_MUTABLE ✅
- [03-security.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/03-security.md)：eBPF kfunc 已全部清除 ✅

### 正确项 4：sched_ext 禁止声明一致性
- [00-alk-kernel-overview.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md#L76-84) §2.3：5 条不使用理由 ✅
- [00-alk-kernel-overview.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md#L332)：明确 "非 sched_ext" ✅
- 文档中 sched_ext 误用 0 残留 ✅

### 正确项 5：Capability Folding 架构一致性
- [00-alk-kernel-overview.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md#L188-211) §4：4 核心 syscall + io_uring 数据面 ✅
- [07-syscall-registry.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/140-application-development/07-syscall-registry.md#L38-39) §1.4：v1.0.1 Capability Folding 架构约束 ✅
- [09-kernel-agent-supervisor.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/09-kernel-agent-supervisor.md#L16-19)：fastpath C-S9 + slowpath LSM 分工 ✅

### 正确项 6：IPC magic 值一致性
- [00-alk-kernel-overview.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md#L298)：IPC magic `0x41524531` / 任务描述符 `0x41475453` ✅
- [09-ssot-registry.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/09-ssot-registry.md#L159)：Tier 0 登记 ✅

### 正确项 7：Badge 撤销 O(1) atomic_inc 一致性
- [00-alk-kernel-overview.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md#L272-278) §5.4：1 行 atomic_inc ✅
- [09-kernel-agent-supervisor.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/20-modules/09-kernel-agent-supervisor.md#L16-19)：Badge 撤销解耦 atomic_inc ✅

---

## SSoT 权威评估

### SSoT 权威源体系现状

| SSoT 源 | 权威级别 | 当前状态 | 问题 |
|---------|---------|---------|------|
| [07-syscall-registry.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/140-application-development/07-syscall-registry.md) | Tier 0 | 编号 548-551 正确，但 REGISTER_BPF 与 H5 冲突 | P0-019 |
| [09-ssot-registry.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/09-ssot-registry.md) | Tier 0 | 规则编号 SSoT 正确 | 无 |
| [10-sc-sched-extension.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/30-interfaces/10-sc-sched-extension.md) | Tier 1 | Agent 8 态 SSoT 正确 | 无 |
| [01-lsm-framework.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/110-security/01-lsm-framework.md) | Tier 1 | LSM 排序 SSoT 正确 | 无 |
| [00-alk-kernel-overview.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/00-alk-kernel-overview.md) | Tier 1 | 声明为 ALK-6.6 总体架构 SSoT，但 4 处与子 SSoT 矛盾 | P0-020~023 |

### SSoT 权威性评分

| 维度 | 评分 | 说明 |
|------|------|------|
| syscall 编号一致性 | 9/10 | 548-551 三方一致，但 REGISTER_BPF 语义冲突（-1） |
| Agent 状态机一致性 | 4/10 | 三重不一致，SSoT 正确但 2 份文档不同（-6） |
| H5 纯 C LSM 一致性 | 8/10 | 核心约束一致，但 00-alk-kernel-overview.md LSM_ORDER/L4 各 1 处错误（-2） |
| sched_tac 选型一致性 | 10/10 | 所有文档一致声明不使用 sched_ext |
| code-doc 一致性 | 10/10 | unistd.h/syscall_64.tbl 与 SSoT 一致 |
| **综合** | **8.2/10** | |

---

## 变更历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v3.1 | 2026-07-23 | 初始版本：识别 5 个 P0 + 3 个 P1 + 7 个已确认正确项 |

---

*审查遵循 OS-IRON-005（审查优先文化）与 OS-STD-GOV-001（SSoT 绝对权威原则）。*