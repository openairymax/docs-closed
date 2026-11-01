SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 04 — syscall 注册与 codegen 深度对比：openEuler/seL4 vs Airymax

> 文档定位：Airymax agent-linux v3.6 评审报告第 04 篇，聚焦 syscall 注册机制、KABI 保留槽策略、扩展调度 syscall 设计、SYSCALL_DEFINE 规范、codegen 工具链与 budget 入口检查六个维度，对照 openEuler OLK-6.6 与 seL4-master 实现进行深度对比。
>
> 对比基准：
> - openEuler OLK-6.6（`/home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/`）
> - seL4-master（`/home/spharx/SpharxWorks/.engineer-reference/seL4-master/`）
> - Airymax agent-linux v3.6（`/home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/`）
>
> 最后更新：2026-07-30
>
> 方法论：基于已验证证据清单（行号、文件路径、宏定义均经 grep/逐行读取确认）进行静态对比分析。不编造未验证的行号或实现细节。改进建议标注优先级（P0/P1/P2），每条建议包含现状、参考、建议、风险评估四要素。

## 1. 概述

syscall 是用户态进入内核的唯一受控入口，其注册机制、编号管理、参数校验、codegen 流程直接决定内核的安全基线与可演进性。Airymax agent-linux v3.6 在 M1 阶段已搭建 4 个核心 syscall（548-551）的脚手架，并引入 `syscall_gen.py` 实现 SSoT（Single Source of Truth）codegen 流程。本报告对照 openEuler OLK-6.6 的 KABI 保留槽机制与 seL4 的 MCS budget 检查机制，识别 Airymax 当前实现的差距与改进路径。

## 2. syscall 注册机制对比

### 2.1 openEuler：手工 tbl + KABI 保留槽

openEuler 在 [syscall_64.tbl](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/arch/x86/entry/syscalls/syscall_64.tbl#L346) 中采用手工维护的表格注册方式，并显式管理 KABI 保留槽：

```
# L346: # don't use numbers 387 through 423, add new calls after the last 'common' entry
# L349-351: io_uring_setup/io_uring_enter/io_uring_register (425-427)
# L368-370: landlock_create_rulesets/add_rule/restrict_self (444-446)
# L379-390: kabi_reserved455 ~ kabi_reserved466 (12 个 KABI 保留槽, sys_ni_syscall)
# L391-392: xsched_setattr/xsched_getattr (467/468)
```

关键设计：**保留槽显式登记为 `sys_ni_syscall`**。在 [syscall_64.tbl L379-390](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/arch/x86/entry/syscalls/syscall_64.tbl#L379) 中，`kabi_reserved455` 至 `kabi_reserved466` 均指向 `sys_ni_syscall`，该占位符由 [kernel/sys_ni.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sys_ni.c) 的 `cond_syscall` 宏生成，返回 `-ENOSYS`。此机制确保保留编号不会被其他子系统误占用，且在 kabi 白皮书中有据可查。

### 2.2 Airymax：syscall.xml SSoT → syscall_gen.py 自动生成

Airymax 采用契约驱动的 codegen 流程。契约源为 [syscall.xml](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/syscall.xml)，由 [syscall_gen.py](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/tools/codegen/syscall_gen.py) 解析后生成 UAPI 头文件与 syscall_64.tbl 片段。

当前已提交的 [syscall_64.tbl L379-392](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/arch/x86/entry/syscalls/syscall_64.tbl#L379) 中，Airymax 段如下：

```
# L379: # Airymax syscalls (548-551)
# L380: # v1.0.1: 统一使用 548 起始，避开 x86_64 x32 历史遗留区域（512-547）
# L384: 548 common  airy_sys_call           sys_airy_sys_call
# L385: 549 common  airy_sys_rovol_ctl              sys_airy_sys_rovol_ctl
# L386: 550 common  airy_sys_sched_ctl              sys_airy_sys_sched_ctl
# L387: 551 common  airy_sys_clt_notify             sys_airy_sys_clt_notify
# L392: # Do not add new syscalls to this range. Numbers 548 and above are available
```

548 起始的选择依据来自 openEuler [syscall_64.tbl L394-398](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/arch/x86/entry/syscalls/syscall_64.tbl#L394) 的 x32 历史区域注释："Numbers 548 and above are available for non-x32 use"，避开 x32 历史遗留的 512-547 区域。

### 2.3 关键差异

| 维度 | openEuler | Airymax |
|------|-----------|---------|
| 注册方式 | 手工维护 tbl | syscall.xml → syscall_gen.py 自动生成 |
| 保留槽登记 | 显式 `sys_ni_syscall` | 552-571 未在 tbl 显式登记 |
| 编号基线 | 多段历史区域 | 统一 548 起始 |
| SSoT | tbl 本身即为源 | syscall.xml 为唯一源 |
| CI 校验 | 无 codegen 一致性检查 | check_mode/check_tbl_mode 强制校验 |

## 3. KABI 保留槽策略对比

### 3.1 openEuler 的显式保留槽模式

openEuler 在 [syscall_64.tbl L379-390](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/arch/x86/entry/syscalls/syscall_64.tbl#L379) 显式登记 12 个 KABI 保留槽：

```
455 common  kabi_reserved455  sys_ni_syscall
...
466 common  kabi_reserved466  sys_ni_syscall
```

`sys_ni_syscall` 通过 `cond_syscall` 宏定义为返回 `-ENOSYS` 的占位函数。此设计有三个优势：(1) 编号被内核构建系统正式占用，第三方补丁无法在该槽位注册新 syscall；(2) `/proc/kallsyms` 中可见保留槽符号，便于 kabi 审计；(3) 用户态探测保留槽返回 `-ENOSYS` 而非 `-ENOSYS` 之外的异常，行为可预期。

### 3.2 Airymax 的隐式保留槽模式

Airymax 在 [syscalls.h L27-29](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/syscalls.h#L27) 定义了保留槽范围：

```c
#define AIRY_SYS_RESERVED_BASE  552
#define AIRY_SYS_RESERVED_END   571
#define AIRY_SYS_SLOTS_MAX     24
```

但当前 [syscall_64.tbl](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/arch/x86/entry/syscalls/syscall_64.tbl#L379) 中 552-571 编号**未显式登记为 `sys_ni_syscall`**，仅以注释 `# Do not add new syscalls to this range` 进行软约束。这是与 openEuler KABI 机制最显著的差距。

### 3.3 风险分析

未显式登记的保留槽存在以下风险：(1) 第三方驱动或内核子系统可在 tbl 中注册 552-571 编号的 syscall，与 Airymax UAPI 契约冲突；(2) 用户态探测保留槽时，由于无对应 `sys_ni_syscall` 占位，可能触发 `sys_unknown_syscall` 路径而非返回 `-ENOSYS`；(3) kabi 审计时缺乏符号级证据。

## 4. 扩展调度 syscall 设计对比

### 4.1 openEuler xsched：sched_attr 结构化扩展

openEuler 在 [syscall_64.tbl L391-392](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/arch/x86/entry/syscalls/syscall_64.tbl#L391) 注册了两个扩展调度 syscall：

```
467  common  xsched_setattr  sys_xsched_setattr
468  common  xsched_getattr  sys_xsched_getattr
```

xsched 采用 `sched_attr` 结构化参数扩展，复用现有调度属性框架，参数语义清晰、可扩展字段。set/get 配对设计便于读写调度策略。

### 4.2 Airymax airy_sys_sched_ctl：cap dispatch 模式

Airymax 在 [airy_syscalls.c L164-176](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/syscalls/airy_syscalls.c#L164) 实现 `airy_sys_sched_ctl`：

```c
SYSCALL_DEFINE3(airy_sys_sched_ctl, __u32, op,
                const char __user *, cgroup_path,
                const char __user *, policy)
```

采用 `op` 操作码 dispatch + 字符串参数（cgroup_path、policy）。当前 M1 阶段在 L169/L171 做参数 null check 后返回 `-ENOSYS`。与 xsched 相比，参数非结构化，扩展依赖 op 编号而非字段，类型检查较弱。

### 4.3 设计权衡

| 维度 | openEuler xsched | Airymax airy_sys_sched_ctl |
|------|------------------|----------------------------|
| 参数模型 | sched_attr 结构 | op + 字符串 |
| 类型检查 | 强（结构体字段） | 弱（字符串需 copy_from_user） |
| 扩展方式 | 增加结构体字段 | 增加 op 编号 |
| set/get 配对 | 是 | 单一 ctl 入口 |
| cap 鉴权 | 无显式 cap | 隐含 cap dispatch |

Airymax 的 cap dispatch 模型预留了能力鉴权入口，但参数结构化程度不足，M2 实现真实逻辑时建议引入结构化参数。

## 5. SYSCALL_DEFINE 规范对比

### 5.1 openEuler 宏定义基线

openEuler 在 [syscalls.h L214-261](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/syscalls.h#L214) 定义 SYSCALL_DEFINE 宏族，提供：(1) 参数类型检查；(2) `access_ok` 用户态指针校验；(3) 参数审计 hook；(4) 与 ftrace/strace 集成的元数据。

### 5.2 Airymax 合规性

Airymax 在 [airy_syscalls.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/syscalls/airy_syscalls.c) 的 4 个核心 syscall 均使用 SYSCALL_DEFINE 宏，符合 openEuler 规范：

- [L78](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/syscalls/airy_syscalls.c#L78): `SYSCALL_DEFINE2(airy_sys_call, cap_t, cap, const struct airy_ipc_msg_hdr __user *, msg)`
- [L143](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/syscalls/airy_syscalls.c#L143): `SYSCALL_DEFINE3(airy_sys_rovol_ctl, __u32, op, __u32, pid, __u64, arg)`
- [L164](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/syscalls/airy_syscalls.c#L164): `SYSCALL_DEFINE3(airy_sys_sched_ctl, ...)`
- [L189](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/syscalls/airy_syscalls.c#L189): `SYSCALL_DEFINE2(airy_sys_clt_notify, int, task_id, __u32, phase)`

参数校验已部分落地：`airy_sys_call` 在 [L84](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/syscalls/airy_syscalls.c#L84) 做 null check，[L92](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/syscalls/airy_syscalls.c#L92) 做 cap==NULL check，[L96](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/syscalls/airy_syscalls.c#L96) 做 copy_from_user，[L100](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/syscalls/airy_syscalls.c#L100) 做 magic check。此合规性良好，无需改进。

## 6. codegen 工具链对比

### 6.1 seL4 syscall_stub_gen.py：用户态 stub 生成

seL4 在 [syscall_stub_gen.py](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/libsel4/tools/syscall_stub_gen.py) 提供 codegen 工具，从 XML 接口定义生成用户态 syscall stub。该工具聚焦用户态绑定层，不涉及内核注册表生成。

### 6.2 Airymax syscall_gen.py：内核 UAPI + tbl 片段 + CI 校验

Airymax 的 [syscall_gen.py](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/tools/codegen/syscall_gen.py) 是更完整的 SSoT codegen 工具链：

- [L4-20](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/tools/codegen/syscall_gen.py#L4): 注释明确 R-01 SSoT 契约源职责
- [L28](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/tools/codegen/syscall_gen.py#L28): `GENERATOR_VERSION = "1.0.1"` 版本锁定
- [L34-35](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/tools/codegen/syscall_gen.py#L34): DEFAULT_INPUT=syscall.xml / DEFAULT_OUTPUT=syscall.h
- [L38-122](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/tools/codegen/syscall_gen.py#L38): `parse_xml()` 解析 version/core_count/reserved_count/total_slots/linux_base
- [L57](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/tools/codegen/syscall_gen.py#L57): `linux_base` 默认 548
- [L125-257](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/tools/codegen/syscall_gen.py#L125): `render_c_header()` 生成 SPDX 头部、include guard、AIRY_SYS_IDX_* 内部索引、__NR_airy_sys_* 注册号、预留槽宏、函数原型
- [L260-285](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/tools/codegen/syscall_gen.py#L260): `render_syscall_tbl()` 生成 syscall_64.tbl Airymax 段
- [L310-339](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/tools/codegen/syscall_gen.py#L310): `check_mode()` 用 difflib 校验生成内容与已提交文件一致性
- [L342-364](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/tools/codegen/syscall_gen.py#L342): `check_tbl_mode()` 校验 syscall_64.tbl Airymax 段一致性

关键优势：**CI 一致性校验**。`check_mode`/`check_tbl_mode` 确保已提交的 `syscalls.h` 与 `syscall_64.tbl` 始终与 `syscall.xml` 契约同步，防止手工篡改引入漂移。这是 seL4 与 openEuler 均缺失的能力——seL4 仅生成 stub 不校验内核侧，openEuler 完全手工无 SSoT。

### 6.3 DSL 降级机制

Airymax 在 [syscalls.h L31-53](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/syscalls.h#L31) 提供 [DSL] 降级块：仅 4 core 可用，reserved 标记 -1。此机制支持精简部署场景，openEuler/seL4 无对应设计。

## 7. budget 入口检查对比

### 7.1 seL4 MCS_DO_IF_BUDGET

seL4 在 [syscall.h L19-30](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/api/syscall.h#L19) 定义 `MCS_DO_IF_BUDGET` 宏：

```c
// L19-30: MCS_DO_IF_BUDGET 宏
// updateTimestamp + checkBudgetRestart
```

在 [syscall.c L74-95](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/api/syscall.c#L74) 的 `handleInterruptEntry` 中，MCS 在中断入口**先 checkBudget**，确保 budget 耗尽时立即切换，避免超时执行。此设计是 seL4 实时性保证的核心。

### 7.2 Airymax 当前无 budget 检查

Airymax 在 [airy_syscalls.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/syscalls/airy_syscalls.c) 的 syscall 入口（L78/L143/L164/L189）**无 budget check**。当前 M1 阶段全部返回 `-ENOSYS`，无真实执行逻辑，因此无 budget 超支风险。但 M2 实现真实调度逻辑后，若 airy_sys_sched_ctl 等 syscall 涉及长时操作，需引入 budget 入口检查以符合 agentrt 实时性要求。

## 8. 改进建议

### [P0] 552-571 预留槽位显式登记为 sys_ni_syscall

**现状**：[syscall_64.tbl L379-392](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/arch/x86/entry/syscalls/syscall_64.tbl#L379) 中 552-571 编号未显式登记，仅注释 `# Do not add new syscalls to this range` 进行软约束。UAPI 头文件 [syscalls.h L27-28](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/syscalls.h#L27) 定义了 RESERVED_BASE/END 但 tbl 未落地。

**参考**：openEuler [syscall_64.tbl L379-390](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/arch/x86/entry/syscalls/syscall_64.tbl#L379) 的 `kabi_reserved455` ~ `kabi_reserved466` 显式登记为 `sys_ni_syscall` 模式。

**建议**：在 [syscall_gen.py L260-285](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/tools/codegen/syscall_gen.py#L260) 的 `render_syscall_tbl()` 中，为 552-571 预留槽生成显式 tbl 条目：

```
552 common  airy_reserved_552  sys_ni_syscall
553 common  airy_reserved_553  sys_ni_syscall
...
571 common  airy_reserved_571  sys_ni_syscall
```

并依赖 `cond_syscall` 宏（openEuler [kernel/sys_ni.c](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/kernel/sys_ni.c) 模式）生成 `-ENOSYS` 占位符。此变更应在 syscall.xml 契约中声明 reserved 槽的 sys_ni_syscall 语义，保持 SSoT。

**风险评估**：低风险。`sys_ni_syscall` 是内核既有占位符，不引入新依赖。需确认 `check_tbl_mode` CI 校验同步更新，否则会因 tbl 内容变更触发 CI 失败（这是预期行为，恰恰证明 CI 生效）。

### [P1] syscall 入口增加 budget 检查

**现状**：[airy_syscalls.c L78/L143/L164/L189](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/syscalls/airy_syscalls.c#L78) 的 4 个 syscall 入口无 budget check。M1 阶段全部返回 `-ENOSYS`，无超支风险。

**参考**：seL4 [syscall.h L19-30](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/api/syscall.h#L19) 的 `MCS_DO_IF_BUDGET` 宏，结合 [syscall.c L74-95](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/api/syscall.c#L74) 的 `handleInterruptEntry` 中断入口 checkBudget 模式。

**建议**：M2 实现真实逻辑时，在 `airy_sys_sched_ctl` 与 `airy_sys_call` 的 opcode switch 分支前增加 budget 检查宏（如 `AIRY_DO_IF_BUDGET`），检查当前 cap 的 budget 余量，不足时返回 `-EAGAIN` 或触发 budget 切换。具体宏定义可参考 seL4 的 `updateTimestamp + checkBudgetRestart` 两段式设计。

**风险评估**：中风险。budget 检查依赖 cap 子系统的 budget 账户结构，M1 阶段尚未实现。过早引入可能导致编译依赖问题，需与 cap 子系统 M2 进度对齐。建议作为 M2 的入口改造任务跟踪。

### [P2] airy_sys_sched_ctl 引入结构化参数

**现状**：[airy_syscalls.c L164-176](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/syscalls/airy_syscalls.c#L164) 使用 `op + cgroup_path + policy` 字符串参数，类型检查弱，扩展依赖 op 编号。

**参考**：openEuler [syscall_64.tbl L391-392](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/arch/x86/entry/syscalls/syscall_64.tbl#L391) 的 `xsched_setattr`/`xsched_getattr` 采用 `sched_attr` 结构化扩展，set/get 配对。

**建议**：定义 `airy_sched_attr` 结构体（包含 policy、cgroup_path_len、cgroup_path_buf、优先级、budget 限额等字段），将 `airy_sys_sched_ctl` 拆分为 `airy_sys_sched_setattr`/`airy_sys_sched_getattr` 配对 syscall（占用 552-571 预留槽中的 2 个），或保持单入口但参数改为结构体指针 + size。结构体字段经 syscall_gen.py 从 syscall.xml 生成，保持 SSoT。

**风险评估**：中风险。变更 UAPI 参数模型会破坏现有用户态契约，需在 v3.7 或 v4.0 窗口完成。若 552-571 预留槽已按 P0 建议显式登记为 sys_ni_syscall，则新增 set/get 配对需先释放 2 个保留槽，需更新 syscall.xml 契约并重跑 codegen。

### [P2] 文档化 R-01 SSoT 流程

**现状**：[syscall_gen.py L4-20](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/tools/codegen/syscall_gen.py#L4) 注释提及 R-01 SSoT，[L310-364](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/tools/codegen/syscall_gen.py#L310) 的 `check_mode`/`check_tbl_mode` CI 校验已落地，但流程未文档化。

**参考**：seL4 [syscall_stub_gen.py](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/libsel4/tools/syscall_stub_gen.py) 虽无 CI 校验，但工具用法在 seL4 文档中有明确说明。

**建议**：在 `docs-closed/agent-linux-dev/` 下补充 R-01 SSoT 流程文档，明确：(1) syscall.xml 为唯一契约源；(2) 修改 syscall 必须先改 xml 再跑 `syscall_gen.py --generate`；(3) CI 通过 `--check`/`--check-tbl` 模式校验生成物一致性；(4) 禁止手工编辑生成的 syscalls.h 与 tbl Airymax 段。

**风险评估**：极低风险。纯文档变更，无代码影响。

## 9. 综合评估

Airymax agent-linux v3.6 的 syscall 注册与 codegen 设计在 SSoT 与 CI 一致性校验方面**领先** openEuler 与 seL4：syscall.xml 契约源 + syscall_gen.py codegen + check_mode/check_tbl_mode CI 校验形成闭环，杜绝了手工维护的漂移风险。SYSCALL_DEFINE 规范全面合规。

主要差距集中在两点：(1) **保留槽未显式登记**（P0），与 openEuler KABI 机制相比存在编号被误占用风险；(2) **入口无 budget 检查**（P1），与 seL4 MCS 相比缺少实时性保证，需在 M2 调度逻辑落地时补齐。

次要改进（P2）涉及参数结构化与流程文档化，可在 v3.7/v4.0 演进窗口规划。总体而言，Airymax syscall 子系统在 M1 阶段的脚手架质量良好，codegen 工具链设计具有前瞻性，建议优先推进 P0 的保留槽显式登记，消除编号管理风险。
