# AgentRT 0.1.1 全修发行计划（Release Full Remediation Plan）

> **文档编号**: DOC-RFRP-0.1.1  
> **创建日期**: 2026-07-11  
> **版本**: v1.0  
> **状态**: 生效  
> **决策**: 2026-07-11 用户选择**方案 B（稳妥：全修后发行）**——先修全部 P0+P1+P2，再发行 0.1.1  
> **依赖**: 三源深度研读（① agentrt 7 子仓 ~318.6K LOC 源码逐仓审查 ② docs/AirymaxRT 85 篇设计与规范文档约束提取 ③ docs-closed/agentrt 95 份历史档案逐项修复状态追踪）  
> **关联**: [01-repo-split-proposal.md](01-repo-split-proposal.md) / [02-tech-improvement-plan-v3.0.md](02-tech-improvement-plan-v3.0.md) / [03-detailed-task-list.md](03-detailed-task-list.md) / [CCN_LONG_TAIL_REMEDIATION.md](CCN_LONG_TAIL_REMEDIATION.md) / [_review_0.1.1/01-license-audit-report.md](../_review_0.1.1/01-license-audit-report.md)  
> **权威契约基准**: [docs/AirymaxRT/10-architecture/06-iron9-shared-model.md](../../docs/AirymaxRT/10-architecture/06-iron9-shared-model.md)（IRON-9 v2）  
> **SPDX-License-Identifier**: AGPL-3.0-or-later OR Apache-2.0  
> **Copyright**: (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

---

## 1. 执行摘要

### 1.1 决策背景

2026-07-11 完成对 agentrt 0.1.1 发行就绪度的三源深度评估。评估结论：**功能层面已达"奠基版本"标准**（~318.6K LOC 真实实现、0 生产 TODO/FIXME、149 测试文件、桩函数已清除、BAN 禁令落地、strict compliance 毒化机制健全），但**工程契约层面未达发行标准**，识别出 **8 项 P0 阻断 + 9 项 P1 严重 + 8 项 P2 中等**共 25 项必修问题。

用户决策采用**方案 B（全修后发行）**：在 0.1.1 内修复全部 P0+P1+P2，再发行。本计划是该方案的工程化执行文档。

### 1.2 就绪度基线（修复前）

| 维度 | 状态 | 关键证据 |
|---|---|---|
| 功能实现层 | ✅ 达标 | 318.6K LOC 真实实现，0 桩，149 测试 |
| 命名/术语层（代码） | ✅ 达标 | `agentos_`/`SCHED_AGENT` 宏/`150-cloud-native` 零残留 |
| 命名/术语层（文档/产物） | ❌ 未达标 | README_zh/CONTRIBUTING/Desktop crate/Docker backup.sh 残留 |
| 许可证层 | ✅ 达标 | 866 文件 SPDX 双许可证 |
| **工程契约层** | ❌ **未达标** | [SC] 6 头文件缺失、任务 magic 零落地、MAC_MAX_AGENTS 4 处不一致 |
| **版本一致性** | ❌ **未达标** | CHANGELOG 无 0.1.1 条目，多份子文档仍 0.1.0 |
| **跨平台 CI** | ❌ **未达标** | 仅 ubuntu-latest，无 macOS/Windows 矩阵 |

### 1.3 方案 B 全修范围

本计划覆盖 25 项问题的完整修复方案，每项包含：根因分析、三源证据、详细修复步骤、涉及文件清单、工作量估算、验收标准、依赖与协同关系。

| 严重度 | 数量 | 工作量估算 | 修复阶段 |
|---|---|---|---|
| P0 致命 | 8 项 | 34~75h | Week 1（核心契约层）+ Week 2（文档/版本） |
| P1 严重 | 9 项 | 22~40h | Week 2（命名/CI）+ Week 3（测试/migrations） |
| P2 中等 | 8 项 | 10~16h | Week 3（buffer） |
| **合计** | **25 项** | **66~131h（中位 ~90h）** | **~2.5 周**（按 40h/周）或 ~1.5 周（按 60h/周高强度） |

### 1.4 总体路线图

```
Week 1 (Day 1-7)  : P0 核心契约层（[SC] 6 头文件 + 任务 magic + MAC_MAX_AGENTS + IPC magic 收敛）
Week 2 (Day 8-14) : P0 文档/版本 + P1 命名/产物/CI（agentos_ 改名收尾 + 版本号统一 + build 清理 + 跨平台 CI）
Week 3 (Day 15-18): P1 测试/migrations + P2 全部 + 全量验收
```

---

## 2. P0 致命问题修复方案（8 项）

> 优先级：P0 — **必须在 0.1.1 发行前修复**，任一未修即阻断发行。

### P0-01: [SC] 共享契约层 6 头文件完全缺失 ⭐ 最大阻断

**问题描述**：IRON-9 v2 声明的 6 个 `include/airymax/*.h` 物理共享头文件全部不存在，`include/airymax/` 目录本身不存在。agentrt 代码 0 处 `#include <airymax/*.h>`，而是各子仓自行重新定义类型。文档（docs/AirymaxOS/10-architecture/01-system-architecture.md:256-257 等）大量引用这些头文件，形成"文档承诺 vs 实现悬空"的系统性脱节。

**三源证据**：
- 源码 agent #1（P0-2/P0-4）：`find -name 'bpf_struct_ops.h'` 等均空；`include/airymax/` 不存在
- 历史 agent #3（NF-01, f 项）：6 头文件均不存在，agentrt 与 agentrt-linux 两端都未创建
- 规范 agent #2（ARCH-SC01）：[06-iron9-shared-model.md](../../docs/AirymaxRT/10-architecture/06-iron9-shared-model.md) 声明 6 头文件逐字节共享

**根因分析**：0.1.1 奠基阶段聚焦于各子仓功能实现，未将跨态契约层物理化。[SC] 头文件设计需同时满足 agentrt（用户态 C）与 agentrt-linux（内核态 C，1.0.1 阶段）双端约束，设计权衡未完成即进入实现。

**修复步骤**：

1. **物理宿主决策**（详见 §5 专项设计）：物理宿主定在 `agentrt/commons/include/airymax/`（用户态先行落地，1.0.1 阶段 agentrt-linux 通过 `-I$(agentrt_src)/commons/include` 引用）
2. **创建目录与 6 头文件**：
   - `agentrt/commons/include/airymax/bpf_struct_ops.h` — struct_ops 状态机 + common_value
   - `agentrt/commons/include/airymax/memory_types.h` — MemoryRovol L1-L4 数据结构 + GFP 掩码语义 + PMEM 持久化接口
   - `agentrt/commons/include/airymax/security_types.h` — POSIX capability 38 ID 枚举 + LSM 钩子 254 ID 枚举 + Cupolas blob 布局 + capability 派生模型 + Vault backend 抽象 + 策略裁决结果 4 值枚举
   - `agentrt/commons/include/airymax/cognition_types.h` — CoreLoopThree 阶段枚举（PERCEPTION/THINKING/ACTION）+ Thinkdual 模式枚举 + LLM 推理阶段枚举 + CoreLoopThree 上下文结构 + Token 能效指标结构 + GPU/NPU 能力描述符
   - `agentrt/commons/include/airymax/sched.h` — SCHED_EXT 调度类编号约束 + 任务描述符（magic 0x41475453 'AGTS'）+ vtime 类型与衰减公式 + 优先级范围 0-139 + AIRYMAX_SLICE_DFL（20ms）+ **MAC_MAX_AGENTS=1024 SSoT**
   - `agentrt/commons/include/airymax/ipc.h` — IPC magic（0x41524531 'ARE1'）+ 128B 消息头结构（`airymax_ipc_msg_hdr_t`）+ SQE/CQE 操作码与标志位
3. **内容来源**：以 [06-iron9-shared-model.md](../../docs/AirymaxRT/10-architecture/06-iron9-shared-model.md) §3.1-§3.5 的字段定义为蓝本，逐字段物理化为 C 结构体
4. **类型规范**（IRON-9 §4.1-5）：
   - 类型前缀统一 `__u32`/`__u16`/`__u64`（内核风格，用户态通过 `<stdint.h>` 别名兼容）
   - 函数前缀统一 `airymax_`
   - 禁止 `float`/`double`，改用 Q16.16 定点数（`__s32` 高 16 位整数 + 低 16 位小数）
   - 结构体使用 `#pragma pack(push,1)` + `_Static_assert(sizeof(struct) == N)` 保证布局冻结
5. **agentrt 侧引用改造**：将 `are_ipc.h` 中的 `are_ipc_message_header_t` 改为 `#include <airymax/ipc.h>` 后 `typedef airymax_ipc_msg_hdr_t are_ipc_message_header_t`（兼容别名，过渡期保留）；同理处理 task.h、memory_types 等
6. **error.h 第 7 头文件澄清**（见 P0-06 / §5.4）：明确 error.h 是否属于 [SC] 层。若属于则改为 7 头文件并更新所有引用文档；若不属于则修正 [06-iron9-shared-model.md](../../docs/AirymaxRT/10-architecture/06-iron9-shared-model.md) §3.1 line 213 + 映射表 line 327 的标注

**涉及文件**：
- 新建：`agentrt/commons/include/airymax/{bpf_struct_ops,memory_types,security_types,cognition_types,sched,ipc}.h`（6 文件）
- 修改：`agentrt/atoms/corekern/include/are_ipc.h`、`task.h`、`agentrt/commons/include/agentrt_types.h`（改 #include）
- 修改：`agentrt/commons/CMakeLists.txt`（增加 `target_include_directories(agentrt_common PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)`)
- 文档：`docs/AirymaxRT/10-architecture/06-iron9-shared-model.md`（澄清 6 vs 7）

**工作量估算**：16~40h（6 头文件设计 12~24h + 引用改造 4~12h + 验证 4h）

**验收标准**：
- ACC-RFRP-01: `find agentrt -path '*/airymax/*.h' | wc -l` ≥ 6
- ACC-RFRP-02: `grep -rn '#include <airymax/' agentrt --include=*.{c,h}` ≥ 3（至少 ipc.h/sched.h 被引用）
- ACC-RFRP-03: `_Static_assert(sizeof(airymax_ipc_msg_hdr_t) == 128)` 编译通过
- ACC-RFRP-04: `agentrt/` 全量编译零错误（`cmake --build build --target agentrt-all`）
- ACC-RFRP-05: 6 头文件均含 `SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0`

**依赖与协同**：
- 阻塞 P0-02（任务 magic 依赖 sched.h）、P0-03（MAC_MAX_AGENTS SSoT 依赖 sched.h）、P0-05（IPC 头布局依赖 ipc.h）
- 与 agentrt-linux 协同：1.0.1 阶段 agentrt-linux 通过 `-I` 引用 agentrt 的头文件，0.1.1 阶段无需 agentrt-linux 配合

---

### P0-02: 任务描述符 magic 0x41475453('AGTS') 完全缺失

**问题描述**：IRON-9 §3.3 要求任务描述符 magic 必须为 `AIRYMAX_TASK_MAGIC (0x41475453)`，但全 agentrt 源码 `grep '0x41475453\|AGTS'` = 0 命中。任务提交路径未做完整性校验。

**三源证据**：
- 源码 agent #1（P0-3）：零命中
- 历史 agent #3（NF-11, h 项）：代码 0 命中，仅文档约定
- 规范 agent #2（ARCH-SC02）：magic 应为 0x41475453

**根因分析**：任务描述符结构未定义，依赖的 [SC] sched.h 头文件本身不存在（P0-01）。

**修复步骤**：

1. 在 `agentrt/commons/include/airymax/sched.h`（P0-01 创建）中定义：
   ```c
   #define AIRYMAX_TASK_MAGIC 0x41475453u  /* 'AGTS' */
   
   typedef struct __attribute__((packed)) airymax_task_desc {
       __u32 magic;           /* AIRYMAX_TASK_MAGIC */
       __u32 task_id;
       __u32 parent_task_id;
       __u32 agent_id;
       __u64 vtime;           /* 虚拟时间（Q16.16 衰减后） */
       __u16 priority;       /* 0-139 */
       __u16 state;          /* TASK_STATE_* */
       __u32 flags;
       __u64 create_time_ns;
       __u64 deadline_ns;
       __u32 cpu_affinity;
       __u32 reserved[3];
   } airymax_task_desc_t;
   _Static_assert(sizeof(airymax_task_desc_t) == 64, "task desc must be 64 bytes");
   ```
2. 在任务提交路径（`atoms/corekern/src/task.c` 或对应文件）的 `task_create`/`task_submit` 入口设置 `desc->magic = AIRYMAX_TASK_MAGIC`
3. 在任务调度入口（`atoms/corekern/src/scheduler_core.c`）校验 `if (desc->magic != AIRYMAX_TASK_MAGIC) return -AGENTRT_EINVAL`
4. 在 `daemons/sched_d/src/sched_service_impl.c` 任务接收路径同步校验

**涉及文件**：
- 新建/修改：`agentrt/commons/include/airymax/sched.h`（P0-01）
- 修改：`agentrt/atoms/corekern/src/task.c`、`scheduler_core.c`、`daemons/sched_d/src/sched_service_impl.c`

**工作量估算**：4~8h（结构定义 2h + 设置/校验点 2~4h + 测试 2h）

**验收标准**：
- ACC-RFRP-06: `grep -rn 'AIRYMAX_TASK_MAGIC\|0x41475453' agentrt --include=*.{c,h}` ≥ 3
- ACC-RFRP-07: 任务提交测试覆盖 magic 校验（错误 magic 返回 EINVAL）

**依赖**：P0-01（sched.h 必须先存在）

---

### P0-03: MAC_MAX_AGENTS 4 处不一致（调度服务硬上限仅 128！）⭐ 真实功能缺陷

**问题描述**：智能体调度数量硬上限在 4 处分散硬编码且值不一致，**调度服务硬上限仅 128，低于契约 1024 达 8 倍**——这是真实功能 bug，不仅是契约违规。

**三源证据**：
- 源码 agent #1（P0-6 / P1-7）独家发现：
  - `atoms/coreloopthree/src/cognition/ext/multi_agent_collaboration.c:19` = 1024 ✅
  - `daemons/sched_d/src/sched_service_impl.c:20` = **128** ❌
  - `daemons/sched_d/src/strategies/weighted.c:20` = 256 ❌
  - `daemons/market_d/src/market_service_impl.c:32` = 256 ❌
- 规范 agent #2（ARCH-V04）：要求 1024，基准测试验证到 1000 并发

**根因分析**：各子仓独立实现时各自定义局部常量，无 SSoT 头统一。

**修复步骤**：

1. 在 `agentrt/commons/include/airymax/sched.h`（P0-01 创建）中定义 SSoT：
   ```c
   #define MAC_MAX_AGENTS 1024  /* 智能体调度数量硬上限，基准测试验证到 1000 并发 */
   ```
2. 删除 4 处分散硬编码：
   - `atoms/coreloopthree/src/cognition/ext/multi_agent_collaboration.c:19` 删除局部 `#define MAC_MAX_AGENTS 1024`，改 `#include <airymax/sched.h>`
   - `daemons/sched_d/src/sched_service_impl.c:20` 删除 `#define MAX_AGENTS 128`，改 `#include <airymax/sched.h>` 并将代码中 `MAX_AGENTS` 改为 `MAC_MAX_AGENTS`
   - `daemons/sched_d/src/strategies/weighted.c:20` 同上（256 → MAC_MAX_AGENTS）
   - `daemons/market_d/src/market_service_impl.c:32` 同上（256 → MAC_MAX_AGENTS）
3. 全量 grep 确认无残留：`grep -rn '\bMAX_AGENTS\b\|#define MAC_MAX_AGENTS' agentrt --include=*.{c,h}` 仅命中 `airymax/sched.h` 一处定义

**涉及文件**：
- 修改：`agentrt/commons/include/airymax/sched.h`（P0-01）
- 修改：4 处分散定义文件

**工作量估算**：2~4h（SSoT 定义 0.5h + 4 处改造 1~2h + grep 验证 0.5h）

**验收标准**：
- ACC-RFRP-08: `grep -rn '#define MAC_MAX_AGENTS\|#define MAX_AGENTS' agentrt --include=*.{c,h}` = 0（SSoT 头外无定义）
- ACC-RFRP-09: `grep -rn 'MAC_MAX_AGENTS' agentrt --include=*.{c,h}` ≥ 5（1 定义 + ≥4 引用）
- ACC-RFRP-10: sched_d 服务可注册 ≥ 1000 个 agent（功能测试）

**依赖**：P0-01（sched.h 必须先存在）

---

### P0-04: 版本号严重不一致

**问题描述**：README/CMake = 0.1.1，但 CHANGELOG.md 最新条目为 `[v0.1.0] - 2026-05-29`，**全文件 0 处提到 0.1.1**。commons/utils/*/README.md 全部标记 v0.1.0；gateway/deploy/k8s/deployment.yaml 标 `version: "0.1.0"`。发行元数据完整性缺失。

**三源证据**：
- 源码 agent #1（P0-1）独家发现

**根因分析**：0.1.1 版本号在 CMake/README badge 已更新，但 CHANGELOG 条目与子仓 README/k8s yaml 未同步。

**修复步骤**：

1. **补 CHANGELOG v0.1.1 条目**：在 `agentrt/CHANGELOG.md` 顶部新增：
   ```markdown
   ## [v0.1.1] - 2026-07-XX
   
   ### 奠基版本（Foundation Release）
   
   ### Added
   - IRON-9 v2 [SC] 共享契约层 6 头文件（airymax/{bpf_struct_ops,memory_types,security_types,cognition_types,sched,ipc}.h）
   - 任务描述符 magic 0x41475453 ('AGTS') 完整性校验
   - MAC_MAX_AGENTS=1024 SSoT 统一
   - 跨平台 CI 矩阵（macOS/Windows）
   
   ### Changed
   - agentos_→agentrt_ 改名彻底完成（含产物层 Desktop crate + Docker scripts）
   - IPC magic 收敛至单一 0x41524531 ('ARE1')
   - heapstore migrations 重写为 SQLite 兼容语法
   - protocols 测试覆盖提升
   
   ### Fixed
   - 调度服务 MAX_AGENTS 从 128 修正为 1024（低于契约 8 倍的功能 bug）
   - 文档错误码值对齐 SSoT
   - 文档许可证冲突修正（MIT/GPL-3.0-only → 双许可证）
   - taskflow_graph_partition 实现真实分区
   
   ### Removed
   - build/ 目录 BAN-33 残留
   - AGENTRT_ERROR_SCHED_AGENT_* 废弃别名
   ```
2. **同步 commons/utils/*/README.md**：30+ 子目录 README 的 `**版本**: v0.1.0` → `v0.1.1`（可用 sed 批量：`find agentrt/commons/utils -name 'README.md' -exec sed -i 's/v0\.1\.0/v0.1.1/g' {} +`）
3. **同步 k8s yaml**：`gateway/deploy/k8s/deployment.yaml` 的 `version: "0.1.0"` → `0.1.1`
4. **全量验证**：`grep -rn 'v0\.1\.0\|0\.1\.0' agentrt --include=*.{md,yaml,yml,json,toml} | grep -v CHANGELOG | grep -v 'v0.1.0.*\[v0.1.1\]'` 应仅命中 CHANGELOG 历史条目

**涉及文件**：
- 修改：`agentrt/CHANGELOG.md`（新增 v0.1.1 条目）
- 修改：`agentrt/commons/utils/*/README.md`（30+ 文件）
- 修改：`agentrt/gateway/deploy/k8s/deployment.yaml`

**工作量估算**：2~4h（CHANGELOG 1h + 批量 sed 0.5h + 验证 1h）

**验收标准**：
- ACC-RFRP-11: `grep -c '0\.1\.1' agentrt/CHANGELOG.md` ≥ 3
- ACC-RFRP-12: `grep -rn 'version.*0\.1\.0' agentrt --include=*.{yaml,yml,toml}` = 0
- ACC-RFRP-13: `grep -rn 'v0\.1\.0' agentrt/commons/utils/*/README.md` = 0

**依赖**：无（可与 P0-01/02/03 并行）

---

### P0-05: IPC 4 套不兼容 magic 并存 + 128B 头布局与 SSoT 冲突

**问题描述**：存在 4 套不兼容 IPC magic：
- `are_ipc.h:57` `ARE_IPC_MAGIC 0x41524531`（'ARE1'，corekern 层，符合契约）✅
- `commons/utils/ipc/include/ipc_common.h:74` `IPC_MAGIC 0x49504300`（'IPC\0'，应用层）❌
- `commons/include/agentrt_types.h:138` 注释 `0x414F5350`（'AOSP'，疑似 Android Open Source Project 误植）❌
- `daemons/common/include/ipc_service_bus.h:86` `IPC_BUS_MESSAGE_MAGIC 0x49534200`（'ISB'）❌

且 agentrt 的 `are_ipc_message_header_t` 128B 字段布局与 IRON-9 §3.2 SSoT 完全不同（字段顺序、偏移、命名均不一致）。

**三源证据**：
- 源码 agent #1（P1-5/P1-6）：4 magic + 布局冲突
- 历史 agent #3（NF-02, g/i 项）：4 套不兼容 magic 并存

**根因分析**：各层（corekern / commons / daemon）独立定义 IPC 头，无 [SC] ipc.h 收敛。

**修复步骤**：

1. **收敛 magic**（依赖 P0-01 ipc.h）：
   - `commons/utils/ipc/include/ipc_common.h:74`：`#define IPC_MAGIC 0x49504300` → `#define IPC_MAGIC AIRYMAX_IPC_MAGIC`（即 `0x41524531`，从 `<airymax/ipc.h>` 引入）
   - `commons/include/agentrt_types.h:138`：删除 `0x414F5350` 注释，改为引用 `#include <airymax/ipc.h>`
   - `daemons/common/include/ipc_service_bus.h:86`：`#define IPC_BUS_MESSAGE_MAGIC 0x49534200` → `#define IPC_BUS_MESSAGE_MAGIC AIRYMAX_IPC_MAGIC`
2. **布局对齐**：将 `are_ipc_message_header_t` 字段顺序对齐 IRON-9 §3.2 SSoT：
   ```c
   /* SSoT 布局（来自 airymax/ipc.h） */
   typedef struct __attribute__((packed)) airymax_ipc_msg_hdr {
       __u32 magic;          /* 0x41524531 'ARE1', offset 0 */
       __u16 version;        /* offset 4 */
       __u16 flags;          /* offset 6 */
       __u64 trace_id;       /* offset 8 */
       __u64 timestamp_ns;   /* offset 16 */
       __u32 src_task;       /* offset 24 */
       __u32 dst_task;       /* offset 28 */
       __u32 payload_len;    /* offset 32 */
       __u32 checksum;       /* offset 36 */
       __u8  reserved[84];   /* offset 40, padding to 128 */
   } airymax_ipc_msg_hdr_t;
   _Static_assert(sizeof(airymax_ipc_msg_hdr_t) == 128, "IPC header must be 128 bytes");
   ```
   - 注意：SSoT 布局与当前 agentrt `are_ipc_message_header_t`（含 source[32]/target[32]/correlation_id 等）不同，需评估兼容性。若改布局会破坏现有 daemon 间通信，则**显式声明分层**：
     - L1 corekern IPC 用 `airymax_ipc_msg_hdr_t`（SSoT，跨 agentrt↔agentrt-linux）
     - L2 daemon-IPC 用 `are_ipc_message_header_t`（agentrt 独有 [IND] 层，magic 统一为 0x41524531 但布局不同）
     - 在 [06-iron9-shared-model.md](../../docs/AirymaxRT/10-architecture/06-iron9-shared-model.md) 明确此分层
3. **命名对齐**：`are_ipc_message_header_t` 保留为 L2 别名，但 `airymax_ipc_msg_hdr_t` 为 SSoT 主名
4. **验证**：全量 grep 确认仅 1 个 magic 值：`grep -rn '0x49504300\|0x414F5350\|0x49534200' agentrt --include=*.{c,h}` = 0

**涉及文件**：
- 修改：`agentrt/commons/utils/ipc/include/ipc_common.h:74`
- 修改：`agentrt/commons/include/agentrt_types.h:138`
- 修改：`agentrt/daemons/common/include/ipc_service_bus.h:86`
- 修改：`agentrt/atoms/corekern/include/are_ipc.h`（对齐 SSoT 或声明 [IND] 分层）
- 文档：`docs/AirymaxRT/10-architecture/06-iron9-shared-model.md`（声明分层）

**工作量估算**：4~8h（magic 收敛 1h + 布局决策 2~4h + 改造 1~2h + 验证 1h）

**验收标准**：
- ACC-RFRP-14: `grep -rn '0x49504300\|0x414F5350\|0x49534200' agentrt --include=*.{c,h}` = 0
- ACC-RFRP-15: `grep -rn 'AIRYMAX_IPC_MAGIC\|0x41524531' agentrt --include=*.{c,h}` ≥ 4（1 定义 + ≥3 引用）
- ACC-RFRP-16: `_Static_assert(sizeof(airymax_ipc_msg_hdr_t) == 128)` 编译通过

**依赖**：P0-01（ipc.h 必须先存在）

---

### P0-06: 文档错误码值错误 + Cupolas 3 套并行错误码系统

**问题描述**：
- `docs/AirymaxRT/50-specifications/10-contracts/06-glossary-index.md`：AGENTRT_EINVAL=-2（应为 -1），全部错误码值与 SSoT 不一致
- `docs/AirymaxRT/50-specifications/10-contracts/03-protocol-contract.md §5.3.1`：使用 `free()` 而非 `agentrt_sys_free()`
- `docs/AirymaxRT/50-specifications/40-error-code/README.md`：Cupolas 存在 3 套并行错误码系统（commons/cupolas enum/cupolas 本地 #define）
- `docs/AirymaxRT/50-specifications/70-project-erp/04-resource-management-table.md §4.1`：明确要求"始终使用 malloc()/calloc()/realloc()"，直接违反 BAN

**三源证据**：
- 规范 agent #2（F-P0-01/02/03/05）独家发现

**根因分析**：文档编写时未对齐 SSoT 错误码权威源 `agentrt/commons/utils/error/include/error.h`，且 Cupolas 模块在演进中遗留多套错误码定义。

**修复步骤**：

1. **glossary-index.md 错误码值对齐**：以 [02-error-code-reference.md](../../docs/AirymaxRT/50-specifications/70-project-erp/02-error-code-reference.md) 为 SSoT，修正 `06-glossary-index.md` 中所有错误码值（EINVAL=-1, ENOMEM=-2, ETIMEOUT=-11, EBUSY=-9 等）
2. **protocol-contract.md 移除 free()**：将 `§5.3.1` 代码示例中 `free(ptr)` → `MEMORY_FREE_SAFE(ptr)` 或 `agentrt_sys_free(ptr)`
3. **Cupolas 错误码统一**：
   - 审查 `agentrt/cupolas/include/cupolas.h` 的 `cupolas_OK`/`cupolas_ERROR_UNKNOWN` 等小写前缀别名（源码 agent #1 P2-8）
   - 统一为 `#include "error.h"` 后 `#define cupolas_OK AGENTRT_OK` 等兼容别名，或删除别名直接用 AGENTRT_E*
   - 删除 cupolas 本地 `#define` 重定义
4. **resource-management-table.md §4.1 修正**：将"始终使用 malloc()/calloc()/realloc()" → "始终使用 AGENTRT_MALLOC/AGENTRT_CALLOC/AGENTRT_REALLOC"；"使用 free() 后置 NULL" → "使用 MEMORY_FREE_SAFE(&ptr)"
5. **验证**：`grep -rn '\bfree(' docs/AirymaxRT/50-specifications/10-contracts/03-protocol-contract.md` = 0

**涉及文件**：
- 修改：`docs/AirymaxRT/50-specifications/10-contracts/06-glossary-index.md`
- 修改：`docs/AirymaxRT/50-specifications/10-contracts/03-protocol-contract.md`
- 修改：`docs/AirymaxRT/50-specifications/40-error-code/README.md`
- 修改：`docs/AirymaxRT/50-specifications/70-project-erp/04-resource-management-table.md`
- 修改：`agentrt/cupolas/include/cupolas.h`（cupolas_OK 等别名）

**工作量估算**：4~8h（glossary 对齐 1~2h + protocol-contract 0.5h + Cupolas 统一 2~4h + resource-table 0.5h + 验证 1h）

**验收标准**：
- ACC-RFRP-17: `grep -n 'AGENTRT_EINVAL' docs/AirymaxRT/50-specifications/10-contracts/06-glossary-index.md` 值 = -1
- ACC-RFRP-18: `grep -rn '\bfree(' docs/AirymaxRT/50-specifications/10-contracts/03-protocol-contract.md` = 0
- ACC-RFRP-19: `grep -rn '#define.*ERROR' agentrt/cupolas/include/cupolas.h | grep -v '#include'` ≤ 2（仅兼容别名）

**依赖**：无

---

### P0-07: 文档许可证冲突（MIT / GPL-3.0-only）

**问题描述**：
- `docs/AirymaxRT/50-specifications/70-project-erp/01-sbom.md`：内部组件许可证列为 MIT，与项目双许可证 AGPL-3.0-or-later OR Apache-2.0 冲突
- `docs/AirymaxRT/50-specifications/30-coding-standard/04-config-audit-log.md`：使用 `SPDX-License-Identifier: GPL-3.0-only`

**三源证据**：
- 规范 agent #2（F-P0-04, F-P1-01）独家发现

**根因分析**：文档编写时许可证字段未对齐项目双许可证决策（2026-07-04 用户决策统一为 AGPL v3 + Apache 2.0）。

**修复步骤**：

1. `01-sbom.md`：内部组件许可证 `MIT` → `AGPL-3.0-or-later OR Apache-2.0`（SBOM 示例 JSON 中所有 `licenseConcluded`/`licenseDeclared` 字段）
2. `04-config-audit-log.md`：文件头 `SPDX-License-Identifier: GPL-3.0-only` → `SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0`
3. 全量验证：`grep -rn 'GPL-3.0-only\|licenseConcluded.*MIT\|licenseDeclared.*MIT' docs/AirymaxRT/` = 0

**涉及文件**：
- 修改：`docs/AirymaxRT/50-specifications/70-project-erp/01-sbom.md`
- 修改：`docs/AirymaxRT/50-specifications/30-coding-standard/04-config-audit-log.md`

**工作量估算**：0.5h

**验收标准**：
- ACC-RFRP-20: `grep -rn 'GPL-3.0-only' docs/AirymaxRT/` = 0
- ACC-RFRP-21: `grep -rn 'licenseConcluded.*"MIT"\|licenseDeclared.*"MIT"' docs/AirymaxRT/` = 0

**依赖**：无

---

### P0-08: docs-closed/02-corekern.md 仍用 agentos_ 命名 + 称 CoreKern 为"微内核"

**问题描述**：
- `docs-closed/agentrt/07-subsystem-specs/02-corekern.md` 仍使用 `agentos_error_t`/`AGENTOS_API`/`agentos/atoms/corekern/` 命名
- 同文档称"CoreKern 是 AgentRT 的微内核"，违反命名规范（应为"微核心" MicroCoreRT）

**三源证据**：
- 规范 agent #2（E-P01/E-P02, F-P0-06）独家发现

**根因分析**：docs-closed 闭源文档在 agentos_→agentrt_ 改名时未同步更新。

**修复步骤**：

1. 全文 `agentos_` → `agentrt_` 替换
2. 全文 `AGENTOS_API` → `AGENTRT_API` 替换
3. 全文 `agentos/atoms/corekern/` → `agentrt/atoms/corekern/` 替换
4. "CoreKern 是 AgentRT 的微内核" → "CoreKern 是 AgentRT 的微核心（MicroCoreRT）"
5. 验证：`grep -rn 'agentos_\|AGENTOS_API\|微内核' docs-closed/agentrt/07-subsystem-specs/02-corekern.md` = 0（注意"微内核"仅在该文档误用，agentrt-linux 的微内核表述是合法的，此处仅修 agentrt 文档）

**涉及文件**：
- 修改：`docs-closed/agentrt/07-subsystem-specs/02-corekern.md`

**工作量估算**：1~2h

**验收标准**：
- ACC-RFRP-22: `grep -rn 'agentos_\|AGENTOS_API' docs-closed/agentrt/07-subsystem-specs/02-corekern.md` = 0
- ACC-RFRP-23: `grep -n '微内核' docs-closed/agentrt/07-subsystem-specs/02-corekern.md` = 0

**依赖**：无

---

## 3. P1 严重问题修复方案（9 项）

> 优先级：P1 — **强烈建议发行前修复**，方案 B 全修范围。

### P1-09: README_zh.md badge URL 仍指向 agentos

**问题**：`agentrt/README_zh.md` badge URL 为 `https://atomgit.com/openairymax/agentos`（应为 `agentrt`）。

**修复**：badge URL `agentos` → `agentrt`。

**涉及文件**：`agentrt/README_zh.md`

**工作量**：0.5h | **验收**：`grep 'agentos' agentrt/README_zh.md` = 0

---

### P1-10: CONTRIBUTING.md 大量 agentos 残留

**问题**：`agentrt/CONTRIBUTING.md` 第 17 行 "agentos/ 核心系统层"、第 45 行 `git clone https://atomgit.com/openairymax/agentos.git`、第 319-321 行 Issues 链接全部指向 `agentos`。

**修复**：全文 `agentos` → `agentrt`（注意保留 §4 约定 E1 关于"agentrt 管理仓 git 远端名沿用 agentos.git"的合法说明，那是历史保留决策）。

**涉及文件**：`agentrt/CONTRIBUTING.md`

**工作量**：1h | **验收**：`grep -n 'agentos' agentrt/CONTRIBUTING.md | grep -v 'E1\|历史保留\|agentos.git'` = 0

---

### P1-11: Desktop crate 仍名 airymax-agentos / agentos_desktop_lib

**问题**：`products/desktop/src-tauri/Cargo.toml:2,11` crate 名仍为 `airymax-agentos` / `agentos_desktop_lib`；`src/main.rs:6` `agentos_desktop_lib::run()`；`src/cli.rs:17,28,40,41` `agentos_cli_path`/`detect_agentos_cli`。

**修复**：
1. `Cargo.toml`: `name = "airymax-agentos"` → `"airymax-agentrt"`；`name = "agentos_desktop_lib"` → `"agentrt_desktop_lib"`
2. `main.rs`: `agentos_desktop_lib::run()` → `agentrt_desktop_lib::run()`
3. `cli.rs`: `agentos_cli_path` → `agentrt_cli_path`；`detect_agentos_cli` → `detect_agentrt_cli`
4. 验证 Rust 编译：`cargo build` 在 `products/desktop/src-tauri/` 通过

**涉及文件**：`products/desktop/src-tauri/Cargo.toml` + `main.rs` + `cli.rs` + 其他引用文件

**工作量**：2~4h | **验收**：`grep -rn 'agentos' products/desktop/src-tauri/ --include=*.{rs,toml}` = 0

---

### P1-12: Docker backup.sh 大量 agentos_ 残留

**问题**：`products/docker/scripts/backup.sh` 行 209/274/276/358/384 含 `agentos_prod_`/`agentos_version`/`agentos_${ENVIRONMENT}`。

**修复**：全文 `agentos_` → `agentrt_`（变量名、卷前缀、归档名）。

**涉及文件**：`products/docker/scripts/backup.sh`

**工作量**：1h | **验收**：`grep -n 'agentos' products/docker/scripts/backup.sh` = 0

---

### P1-13: agentrt/build/ 残留 BAN-33

**问题**：`agentrt/build/` 目录存在（CMakeCache.txt 14KB + CMakeFiles 子目录，420K）。CMake 检测逻辑会 FATAL_ERROR 阻止新构建，但残留物本身违反"源码树内无构建产物"原则。

**修复**：
1. 删除 `agentrt/build/` 目录
2. 验证 `.gitignore` 覆盖（`agentrt/.gitignore` 应含 `build/`；若无需补）
3. 验证 CMake BAN-33 检测仍正常工作

**涉及文件**：删除 `agentrt/build/`；可能修改 `agentrt/.gitignore`

**工作量**：0.5h | **验收**：`ls agentrt/build/ 2>&1` = "No such file or directory"

**依赖**：无

---

### P1-14: CI 跨平台矩阵缺失

**问题**：7 个子仓的 `.github/workflows/ci.yml` 全部 `runs-on: ubuntu-latest`，无 macOS/Windows 矩阵。README 宣称支持 Linux/macOS/Windows 三平台用户态，CI 不覆盖即违反 ARCH-E01 跨平台承诺。

**修复**：
1. 为每个子仓的 `ci.yml` 增加 matrix 策略：
   ```yaml
   strategy:
     fail-fast: false
     matrix:
       os: [ubuntu-latest, macos-latest, windows-latest]
   runs-on: ${{ matrix.os }}
   ```
2. Windows 适配：安装 mingw / msvc build tools；条件安装 cJSON/libsqlite3 等依赖
3. macOS 适配：`brew install cmake cJSON sqlite3` 等
4. 验证至少 atoms + commons 在三平台 CI 通过

**涉及文件**：7 子仓 `.github/workflows/ci.yml`

**工作量**：4~8h | **验收**：CI 在三平台均绿色

**依赖**：P1-13（build 清理后才能验证）

---

### P1-15: heapstore migrations SQL PostgreSQL 语法不兼容 SQLite

**问题**：`heapstore/migrations/V001_initial_schema.sql` 使用 PostgreSQL 语法（`gen_random_uuid()` / `JSONB` / `TIMESTAMPTZ` / `ON DELETE CASCADE` / `UUID` 类型），但实际后端是 SQLite（不支持这些）。当前 migrations 实际不可执行。

**修复**：
1. `gen_random_uuid()` → `lower(hex(randomblob(16)))` 模拟
2. `JSONB` → `JSON`
3. `TIMESTAMPTZ` → `TEXT`（ISO 8601 字符串）
4. `UUID` 类型 → `TEXT`
5. `ON DELETE CASCADE` 保留但添加 `PRAGMA foreign_keys=ON;` 到 migration 开头
6. 验证 `heapstore_migration.c` 实际执行 migration 成功
7. 或：明确声明 migrations 是 PostgreSQL/未来后端用（当前 SQLite 后端不走 migration 路径），并在文档标注

**涉及文件**：`agentrt/heapstore/migrations/V001_initial_schema.sql` + `V002_*.sql`

**工作量**：4~8h | **验收**：migration 在 SQLite 后端实际执行成功

---

### P1-16: protocols 测试覆盖严重不足（14%）

**问题**：protocols 21K LOC 仅 3 个测试文件（test_agntcy_acp / test_china_eco_crypto / test_openclaw_adapter），覆盖 12 个子模块中的 3 个。standards（5555 LOC，4 子模块）和 integrations（6542 LOC，5 子模块）几乎无测试。

**修复**：
1. 补充至少 7 个测试（每个 standard/integration 子模块至少 1 个）：
   - `test_a2a_adapter.c`
   - `test_mcp_adapter.c`
   - `test_openai_adapter.c`
   - `test_openjiuwen_adapter.c`
   - `test_claude_adapter.c`
   - `test_langchain_framework.c`
   - `test_autogen_framework.c`
2. 每个测试覆盖：适配器初始化 + 协议转换 + 错误处理 + 边界用例
3. 验证 `ctest --test-dir build -R protocol` 全绿

**涉及文件**：`agentrt/protocols/tests/`（新建 7 文件）

**工作量**：8~16h | **验收**：protocols 测试文件数 ≥ 10，ctest 全绿

---

### P1-17: 文档引用禁止版本号（v0.2.0/v0.3.0/v1.0.0）

**问题**：
- `docs/AirymaxRT/50-specifications/20-are-standards/README.md` 和 `60-ipc/README.md` 标准化路线图引用 v0.2.0/v0.3.0/v1.0.0 版本，违反 IRON-8（禁止 0.1.2/0.2.0/0.3.0/1.0.0 中间版本，0.1.1→1.0.1 直接过渡）
- `50-specifications/30-coding-standard/11-naming-conventions.md:482` `@since v0.2.0`

**修复**：
1. ARE Standards 路线图调整为 `v0.1.1 → v1.0.1` 路径
2. `11-naming-conventions.md:482` `@since v0.2.0` → `@since v1.0.1`
3. 全量验证：`grep -rn 'v0\.1\.2\|v0\.2\.0\|v0\.3\.0\|v1\.0\.0' docs/AirymaxRT/` = 0

**涉及文件**：`docs/AirymaxRT/50-specifications/20-are-standards/README.md` + `60-ipc/README.md` + `30-coding-standard/11-naming-conventions.md`

**工作量**：1h | **验收**：`grep -rn 'v0\.1\.2\|v0\.2\.0\|v0\.3\.0\|v1\.0\.0' docs/AirymaxRT/` = 0

---

## 4. P2 中等问题修复方案（8 项）

> 优先级：P2 — **方案 B 全修范围，建议在 Week 3 buffer 内完成**。

### P2-18: 聚合目标 agentrt-all 补全 daemons/gateway/heapstore

**问题**：`agentrt-all` 仅 DEPENDS atoms/commons/cupolas，未含 daemons/gateway/heapstore。

**修复**：`agentrt/CMakeLists.txt` 的 `add_custom_target(agentrt-all DEPENDS ...)` 增加 `agentrt_daemons agentrt_gateway agentrt_heapstore`。

**涉及文件**：`agentrt/CMakeLists.txt` | **工作量**：0.5h

---

### P2-19: taskflow 文档与源码不同步

**问题**：`docs/AirymaxRT/60-guides/26-coreloopthree-dag-integration.md:255` 仍称 `taskflow_engine_load_workflow_json()` 是桩函数违反 IRON-2，但源码 `taskflow_advanced.c:294` 已修复为 cJSON 真解析 + ENOTSUP 降级。

**修复**：`§5.3` 更新为"`taskflow_engine_load_workflow_json()` 在 cJSON 可用时实现真正的 JSON 解析；cJSON 不可用时返回 ENOTSUP（非桩函数，IRON-2 合规）。W18 集成推荐使用 `taskflow_engine_register_workflow()`（结构体方式）以避免 cJSON 依赖。"

**涉及文件**：`docs/AirymaxRT/60-guides/26-coreloopthree-dag-integration.md` | **工作量**：0.5h

---

### P2-20: daemon 数量文档不一致（10 vs 12）+ 命名空间列表冲突

**问题**：
- `50-specifications/30-coding-standard/11-naming-conventions.md §7.2` 仅列 10 个 daemon（缺 hook_d/plugin_d）
- `10-architecture/01-system-architecture.md` 称"10 个核心用户态服务"
- `50-specifications/80-rpc-api/README.md` 与 `50-specifications/README.md §5` 列出完全不同的 12 个命名空间

**修复**：
1. 统一为 12 个 daemon（ARCH-CORE08）：gateway_d、llm_d、tool_d、market_d、sched_d、monit_d、channel_d、observe_d、notify_d、info_d、hook_d、plugin_d
2. 命名空间列表以 `80-rpc-api/README.md` 为准：llm./tool./sched./market./monit./gateway./hook./channel./notify./observe./info./plugin.
3. `50-specifications/README.md §5` 对齐

**涉及文件**：3 文档 | **工作量**：1h

---

### P2-21: syscall.md 错误码正值与负 errno 冲突

**问题**：`10-architecture/05-syscall.md` 系统调用错误码使用正值（1001, 1002），与 IRON-9 负 errno（-22）和 syscall-api-contract（-1）冲突。

**修复**：`05-syscall.md` 错误码改为负 errno 体系（对齐 [02-error-code-reference.md](../../docs/AirymaxRT/50-specifications/70-project-erp/02-error-code-reference.md) SSoT）。

**涉及文件**：`docs/AirymaxRT/10-architecture/05-syscall.md` | **工作量**：1h

---

### P2-22: OpenStandards README 5 处断裂路径

**问题**：`docs/OpenStandards/README.md:50,229,230,231,232` 引用 `docs/AirymaxAgentOS/50-engineering-standards/`，实际目录为 `docs/AirymaxOS/`。

**修复**：`AirymaxAgentOS` → `AirymaxOS`（5 处）。

**涉及文件**：`docs/OpenStandards/README.md` | **工作量**：0.5h

---

### P2-23: taskflow_graph_partition 实质仍桩

**问题**：`agentrt/atoms/taskflow/src/taskflow_core.c:1115-1131` `taskflow_graph_partition` 计算 `partition = vid % count; (void)partition;` 丢弃结果，未写入 vertex。

**修复**：
1. 在 `graph_vertex_t` 增加 `int partition_id` 字段（或复用 `user_data`）
2. 将 `partition` 写入 `vertex->partition_id`
3. 移除 `(void)partition;`
4. 补充测试验证分区结果

**涉及文件**：`agentrt/atoms/taskflow/src/taskflow_core.c` + `include/taskflow.h` | **工作量**：2~4h

---

### P2-24: Windows 下 MCP 适配器整体禁用

**问题**：`protocols/CMakeLists.txt` Windows 下 `PROTOCOLS_ENABLE_MCP OFF`（"MCP requires cJSON/unistd.h"），但 cJSON 在 Windows 可用，仅 unistd.h 是 POSIX。应改用条件编译而非整体禁用。

**修复**：
1. 拆分 MCP 适配器：cJSON 部分（跨平台）+ Unix socket 部分（POSIX 条件编译）
2. Windows 下仅禁用 Unix socket 路径，保留 cJSON 路径
3. `CMakeLists.txt` 调整条件

**涉及文件**：`agentrt/protocols/standards/mcp/` + `CMakeLists.txt` | **工作量**：2~4h

---

### P2-25: 测试 system() + 文档 fprintf

**问题**：
- `daemons/common/tests/test_checkpoint.c:37` + `channel_d/tests/test_channel_e2e.c:47` 调用 `system()`（仅测试，但应防 shell 注入）
- `50-specifications/50-integration/01-integration-standard.md §8.1` 代码示例用 `fprintf(stderr, ...)`

**修复**：
1. 测试 `system()` → `fork/exec` 或 `posix_spawn`
2. 文档示例 `fprintf` → `log_write` 或 `AGENTRT_LOG_ERROR`

**涉及文件**：2 测试 + 1 文档 | **工作量**：2h

---

## 5. [SC] 共享契约层专项设计（方案 B 关键难点）

### 5.1 物理宿主决策

**决策**：物理宿主定在 `agentrt/commons/include/airymax/`（用户态先行落地）。

**理由**：
1. 0.1.1 阶段 agentrt 已存在，agentrt-linux 尚未到 1.0.1
2. agentrt 是用户态组件，头文件先在用户态落地不影响 agentrt-linux 1.0.1 阶段引用
3. 1.0.1 阶段 agentrt-linux 通过 `-I$(agentrt_src)/commons/include` 引用，或迁移至 `agentrt-linux/kernel/include/airymax/`（届时再决策）
4. 避免 0.1.1 阶段阻塞于 agentrt-linux 协同

**CMake 集成**：
```cmake
# agentrt/commons/CMakeLists.txt
target_include_directories(agentrt_common PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include  # 含 airymax/ 子目录
)
```

**引用方式**（agentrt 各子仓）：
```c
#include <airymax/ipc.h>      /* [SC] 共享契约层 */
#include <airymax/sched.h>
```

### 5.2 与 agentrt-linux 协同方案

| 阶段 | agentrt | agentrt-linux |
|---|---|---|
| 0.1.1 | 物理宿主，6 头文件落地 | 不涉及（1.0.1 才需要） |
| 1.0.1 | 物理宿主不变 | 通过 `-I` 引用 agentrt 的 `commons/include/airymax/`，或迁移至 `agentrt-linux/kernel/include/airymax/`（届时决策） |

**协同约束**（0.1.1 阶段需在文档声明）：
- 6 头文件内容修改需同时满足 agentrt（用户态 C）与 agentrt-linux（内核态 C）约束
- [SC] 头文件禁止使用 float（IRON-9 §3，因内核态不支持浮点）
- 类型前缀 `__u32`/`__u16`（内核风格，用户态通过 `<stdint.h>` 别名兼容）

### 5.3 6 头文件内容设计概要

| 头文件 | 核心内容 | 估算行数 |
|---|---|---|
| `bpf_struct_ops.h` | struct_ops 状态机 + common_value | ~80 |
| `memory_types.h` | MemoryRovol L1-L4 数据结构 + GFP 掩码 + PMEM 接口 | ~150 |
| `security_types.h` | capability 38 ID + LSM 254 ID + Cupolas blob + 派生模型 + Vault backend + 裁决 4 值 | ~250 |
| `cognition_types.h` | CoreLoopThree 阶段枚举 + Thinkdual + LLM 阶段 + 上下文 + Token 能效 + GPU/NPU 描述符 | ~180 |
| `sched.h` | SCHED_EXT=7 约束 + 任务描述符（magic 0x41475453）+ vtime + 优先级 0-139 + SLICE_DFL + **MAC_MAX_AGENTS=1024** | ~120 |
| `ipc.h` | IPC magic 0x41524531 + 128B 消息头 + SQE/CQE 操作码 | ~140 |
| **合计** | | **~920 行** |

### 5.4 error.h 第 7 头文件澄清

**问题**：[06-iron9-shared-model.md](../../docs/AirymaxRT/10-architecture/06-iron9-shared-model.md) §3.1 line 213 + 映射表 line 327 将 `error.h` 也标注为 [SC]，但"6 个"声明矛盾。

**决策建议**：**error.h 不属于 [SC] 层**。理由：
1. error.h 是 agentrt 用户态独有的错误码定义（AGENTRT_E*），agentrt-linux 内核态有独立的内核错误码体系（-EINVAL 等）
2. 两端错误码不共享，agentrt-linux 通过 IPC 返回值映射
3. 修正 [06-iron9-shared-model.md](../../docs/AirymaxRT/10-architecture/06-iron9-shared-model.md) §3.1 + 映射表，移除 error.h 的 [SC] 标注，明确"6 个 [SC] 头文件"

**备选**：若用户决策 error.h 属于 [SC]，则改为 7 头文件并更新所有引用文档（handbook/README/08-compliance-checklist/40-integration 等）。

---

## 6. 治理路线图

### 6.1 Week 1 (Day 1-7): P0 核心契约层

| Day | 任务 | 工时 | 负责人 | 交付 |
|---|---|---|---|---|
| 1-3 | P0-01 [SC] 6 头文件设计与实现 | 16~24h | A | 6 头文件落地 + CMake 集成 |
| 4 | P0-02 任务描述符 magic | 4~6h | A | sched.h + task.c 校验 |
| 4 | P0-03 MAC_MAX_AGENTS 统一 | 2~3h | B | 4 处硬编码删除 |
| 5-6 | P0-05 IPC magic 收敛 + 布局决策 | 4~6h | A | 4 magic 统一 + 布局对齐 |
| 7 | P0-01/02/03/05 集成验证 | 4h | A+B | 全量编译通过 |

**Week 1 交付**：[SC] 契约层落地，P0-01/02/03/05 全部 ACC 通过。

### 6.2 Week 2 (Day 8-14): P0 文档/版本 + P1 命名/产物/CI

| Day | 任务 | 工时 | 负责人 | 交付 |
|---|---|---|---|---|
| 8 | P0-04 版本号统一 | 2~3h | B | CHANGELOG + 子 README + k8s yaml |
| 8 | P0-06 文档错误码修正 | 2~4h | A | glossary + protocol + cupolas + resource-table |
| 8 | P0-07 文档许可证冲突 | 0.5h | B | sbom + config-audit-log |
| 8 | P0-08 docs-closed corekern | 1~2h | B | 02-corekern.md 改名 |
| 9 | P1-09/10/11/12 agentos_ 改名收尾 | 4~6h | B | README_zh + CONTRIBUTING + Desktop + Docker |
| 9 | P1-13 build 清理 | 0.5h | B | build/ 删除 |
| 10-11 | P1-14 CI 跨平台矩阵 | 4~6h | B | 7 子仓 ci.yml 三平台 |
| 12-13 | P0-06 Cupolas 错误码统一（剩余） | 2~4h | A | cupolas.h 别名清理 |

**Week 2 交付**：P0 全部 8 项 + P1 命名/产物/CI 全部完成。

### 6.3 Week 3 (Day 15-18): P1 测试/migrations + P2 全部 + 验收

| Day | 任务 | 工时 | 负责人 | 交付 |
|---|---|---|---|---|
| 15-16 | P1-15 heapstore migrations | 4~6h | A | SQLite 兼容 |
| 15-17 | P1-16 protocols 测试补充 | 8~12h | A | 7 新测试 |
| 17 | P1-17 文档禁止版本号 | 1h | B | v0.2.0 等清零 |
| 17 | P2-18~22 文档一致性 | 3h | B | 聚合目标 + daemon 数量 + syscall + 路径 |
| 18 | P2-23 taskflow partition | 2~3h | A | 真实分区 |
| 18 | P2-24/25 Windows MCP + system() | 4h | A+B | 条件编译 + fork/exec |
| 18 | 全量验收 | 4h | A+B | ACC-RFRP-01~25 全通过 |

**Week 3 交付**：P1 全部 + P2 全部 + 全量验收通过 → 发行就绪。

---

## 7. 验收标准汇总（ACC-RFRP-01 ~ ACC-RFRP-25）

| 编号 | 验收项 | 对应问题 | 验证命令/方法 |
|---|---|---|---|
| ACC-RFRP-01 | [SC] 6 头文件存在 | P0-01 | `find agentrt -path '*/airymax/*.h' \| wc -l` ≥ 6 |
| ACC-RFRP-02 | agentrt 引用 [SC] 头文件 | P0-01 | `grep -rn '#include <airymax/' agentrt --include=*.{c,h}` ≥ 3 |
| ACC-RFRP-03 | IPC 头 128 字节断言 | P0-01 | `_Static_assert(sizeof(airymax_ipc_msg_hdr_t) == 128)` 编译通过 |
| ACC-RFRP-04 | 全量编译零错误 | P0-01 | `cmake --build build --target agentrt-all` 通过 |
| ACC-RFRP-05 | [SC] 头文件 SPDX | P0-01 | 6 文件均含 SPDX-License-Identifier |
| ACC-RFRP-06 | 任务 magic 引用 | P0-02 | `grep -rn 'AIRYMAX_TASK_MAGIC\|0x41475453' agentrt --include=*.{c,h}` ≥ 3 |
| ACC-RFRP-07 | 任务 magic 校验测试 | P0-02 | 错误 magic 返回 EINVAL 测试通过 |
| ACC-RFRP-08 | MAX_AGENTS 无分散定义 | P0-03 | `grep -rn '#define MAC_MAX_AGENTS\|#define MAX_AGENTS' agentrt --include=*.{c,h}` = 0 |
| ACC-RFRP-09 | MAC_MAX_AGENTS 引用 ≥5 | P0-03 | `grep -rn 'MAC_MAX_AGENTS' agentrt --include=*.{c,h}` ≥ 5 |
| ACC-RFRP-10 | 调度服务 ≥1000 agent | P0-03 | 功能测试注册 ≥1000 agent |
| ACC-RFRP-11 | CHANGELOG 含 0.1.1 | P0-04 | `grep -c '0\.1\.1' agentrt/CHANGELOG.md` ≥ 3 |
| ACC-RFRP-12 | yaml 无 0.1.0 | P0-04 | `grep -rn 'version.*0\.1\.0' agentrt --include=*.{yaml,yml,toml}` = 0 |
| ACC-RFRP-13 | utils README 无 0.1.0 | P0-04 | `grep -rn 'v0\.1\.0' agentrt/commons/utils/*/README.md` = 0 |
| ACC-RFRP-14 | IPC 旧 magic 清零 | P0-05 | `grep -rn '0x49504300\|0x414F5350\|0x49534200' agentrt --include=*.{c,h}` = 0 |
| ACC-RFRP-15 | IPC 新 magic 引用 ≥4 | P0-05 | `grep -rn 'AIRYMAX_IPC_MAGIC\|0x41524531' agentrt --include=*.{c,h}` ≥ 4 |
| ACC-RFRP-16 | IPC 头 128B 断言 | P0-05 | 同 ACC-RFRP-03 |
| ACC-RFRP-17 | glossary EINVAL=-1 | P0-06 | `grep 'AGENTRT_EINVAL' 06-glossary-index.md` 值=-1 |
| ACC-RFRP-18 | protocol-contract 无 free() | P0-06 | `grep -rn '\bfree(' 03-protocol-contract.md` = 0 |
| ACC-RFRP-19 | cupolas 无本地错误码重定义 | P0-06 | `grep -rn '#define.*ERROR' cupolas.h \| grep -v '#include'` ≤ 2 |
| ACC-RFRP-20 | 文档无 GPL-3.0-only | P0-07 | `grep -rn 'GPL-3.0-only' docs/AirymaxRT/` = 0 |
| ACC-RFRP-21 | SBOM 无 MIT 内部组件 | P0-07 | `grep -rn 'licenseConcluded.*"MIT"\|licenseDeclared.*"MIT"' docs/AirymaxRT/` = 0 |
| ACC-RFRP-22 | corekern.md 无 agentos_ | P0-08 | `grep -rn 'agentos_\|AGENTOS_API' 02-corekern.md` = 0 |
| ACC-RFRP-23 | corekern.md 无"微内核"误用 | P0-08 | `grep -n '微内核' 02-corekern.md` = 0 |
| ACC-RFRP-24 | 产物层无 agentos | P1-09~12 | `grep -rn 'agentos' agentrt/README_zh.md agentrt/CONTRIBUTING.md products/desktop/src-tauri/ products/docker/scripts/backup.sh` = 0（排除 E1 合法说明） |
| ACC-RFRP-25 | CI 三平台绿色 | P1-14 | 7 子仓 CI 在 ubuntu/macos/windows 均通过 |

**补充验收**（P1/P2 项）：
- ACC-RFRP-26: build/ 目录不存在（P1-13）
- ACC-RFRP-27: heapstore migration 在 SQLite 执行成功（P1-15）
- ACC-RFRP-28: protocols 测试文件数 ≥ 10（P1-16）
- ACC-RFRP-29: 文档无禁止版本号（P1-17）：`grep -rn 'v0\.1\.2\|v0\.2\.0\|v0\.3\.0\|v1\.0\.0' docs/AirymaxRT/` = 0
- ACC-RFRP-30: taskflow partition 写入结果（P2-23）

---

## 8. 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|---|---|---|---|
| [SC] 头文件设计与 agentrt-linux 1.0.1 需求冲突 | 中 | 高 | 0.1.1 阶段先以 agentrt 用户态约束设计，1.0.1 阶段如有冲突再迭代（头文件版本化） |
| IPC 布局对齐破坏现有 daemon 间通信 | 中 | 高 | 采用分层策略（L1 SSoT + L2 [IND]），magic 统一但布局可不同，文档明确声明 |
| Cupolas 错误码统一破坏向后兼容 | 低 | 中 | 保留兼容别名（`#define cupolas_OK AGENTRT_OK`），标记 deprecated |
| CI 跨平台在 Windows 失败 | 高 | 中 | Week 2 预留 buffer，优先保证 atoms/commons 三平台通过，其他子仓可降级为 Linux-only 并加 TODO |
| protocols 测试补充工作量超估 | 中 | 低 | 优先补 standards（a2a/mcp），integrations 可降级为 P2 |

---

## 9. 附录

### 9.1 关键文件路径索引

**P0 修复目标**：
- [agentrt/CMakeLists.txt](file:///home/spharx/SpharxWorks/OpenAirymax/agentrt/CMakeLists.txt) — 顶层版本号 + 聚合目标
- [agentrt/CHANGELOG.md](file:///home/spharx/SpharxWorks/OpenAirymax/agentrt/CHANGELOG.md) — 缺 v0.1.1 条目
- [agentrt/commons/include/airymax/](file:///home/spharx/SpharxWorks/OpenAirymax/agentrt/commons/include/airymax/) — 新建 [SC] 6 头文件
- [agentrt/atoms/corekern/include/are_ipc.h](file:///home/spharx/SpharxWorks/OpenAirymax/agentrt/atoms/corekern/include/are_ipc.h) — IPC 头对齐
- [agentrt/daemons/sched_d/src/sched_service_impl.c](file:///home/spharx/SpharxWorks/OpenAirymax/agentrt/daemons/sched_d/src/sched_service_impl.c#L20) — MAX_AGENTS=128
- [agentrt/commons/utils/ipc/include/ipc_common.h](file:///home/spharx/SpharxWorks/OpenAirymax/agentrt/commons/utils/ipc/include/ipc_common.h#L74) — IPC_MAGIC
- [agentrt/commons/include/agentrt_types.h](file:///home/spharx/SpharxWorks/OpenAirymax/agentrt/commons/include/agentrt_types.h#L138) — AOSP magic 注释
- [agentrt/heapstore/migrations/V001_initial_schema.sql](file:///home/spharx/SpharxWorks/OpenAirymax/agentrt/heapstore/migrations/V001_initial_schema.sql) — PostgreSQL 语法
- [docs/AirymaxRT/10-architecture/06-iron9-shared-model.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxRT/10-architecture/06-iron9-shared-model.md) — IRON-9 v2 权威契约基准
- [docs-closed/agentrt/07-subsystem-specs/02-corekern.md](file:///home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt/07-subsystem-specs/02-corekern.md) — agentos_ 残留

**P1 修复目标**：
- [agentrt/README_zh.md](file:///home/spharx/SpharxWorks/OpenAirymax/agentrt/README_zh.md) — badge URL
- [agentrt/CONTRIBUTING.md](file:///home/spharx/SpharxWorks/OpenAirymax/agentrt/CONTRIBUTING.md) — agentos 残留
- [products/desktop/src-tauri/Cargo.toml](file:///home/spharx/SpharxWorks/OpenAirymax/products/desktop/src-tauri/Cargo.toml) — crate 名
- [products/docker/scripts/backup.sh](file:///home/spharx/SpharxWorks/OpenAirymax/products/docker/scripts/backup.sh) — agentos_prod_ 残留
- [agentrt/gateway/deploy/k8s/deployment.yaml](file:///home/spharx/SpharxWorks/OpenAirymax/agentrt/gateway/deploy/k8s/deployment.yaml) — version 0.1.0
- [agentrt/atoms/.github/workflows/ci.yml](file:///home/spharx/SpharxWorks/OpenAirymax/agentrt/atoms/.github/workflows/ci.yml) — CI 矩阵（7 子仓同理）

### 9.2 三源报告交叉引用表

| 问题 | 源码 agent #1 | 规范 agent #2 | 历史 agent #3 |
|---|---|---|---|
| [SC] 6 头文件缺失 | P0-2/P0-4 | ARCH-SC01 | NF-01 (f 项) |
| 任务 magic 缺失 | P0-3 | ARCH-SC02 | NF-11 (h 项) |
| MAC_MAX_AGENTS 不一致 | P0-6/P1-7 | ARCH-V04 | — |
| 版本号不一致 | P0-1 | — | — |
| IPC 4 magic 并存 | P1-5/P1-6 | ARCH-SC02 | NF-02 (g/i 项) |
| 文档错误码错误 | — | F-P0-01/02/03/05 | — |
| 文档许可证冲突 | — | F-P0-04/F-P1-01 | — |
| docs-closed agentos_ | — | E-P01/F-P0-06 | — |
| agentos_ 产物层 | — | — | NF-05/NF-06 (a 项) |
| build/ BAN-33 | P1-3 | — | — |
| CI 跨平台 | P1-4 | ARCH-E01 | — |
| heapstore migrations | P1-10 | — | — |
| protocols 测试 | P1-11 | — | — |
| taskflow partition | — | — | NF-07 (n 项 BUG #6) |

### 9.3 工作量汇总表

| 严重度 | 项数 | 工作量（中位） | 工作量（范围） |
|---|---|---|---|
| P0 | 8 | ~50h | 34~75h |
| P1 | 9 | ~30h | 22~40h |
| P2 | 8 | ~13h | 10~16h |
| **合计** | **25** | **~93h** | **66~131h** |

**时间换算**：
- 40h/周（单人全职）：~2.3 周
- 60h/周（单人高强度）：~1.5 周
- 2 人并行 40h/周：~1.2 周

---

## 10. 变更历史

| 日期 | 版本 | 变更 | 作者 |
|---|---|---|---|
| 2026-07-11 | v1.0 | 初版创建，方案 B 全修发行计划 | SPHARX Ltd. - Airymax Team |

---

<div align="center">

**© 2025-2026 SPHARX Ltd.** | 本文档以 AGPL v3 + Apache 2.0 双许可证发布（SPDX: AGPL-3.0-or-later OR Apache-2.0）。

</div>
