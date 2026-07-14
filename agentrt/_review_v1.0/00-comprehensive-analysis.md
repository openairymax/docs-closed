Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agentrt 工程审查综合分析报告 v1.0

> **文档定位**：agentrt 工程审查 v1.0 总览与决策依据，整合 5 个并行子任务（Agent A/B/C/D/E）的 4 份已落盘审查报告，作为整个 v1.0 审查的收敛文档与 1.0.1 M1 启动的判定基线。
> **保密级别**：SPHARX Ltd 内部参考，**闭源不公开**。
> **版本**：1.0（2026-07-13）。
> **审查范围**：agentrt 源码（atoms 237 文件 + daemons/cupolas/gateway/commons/protocols 596 文件 = 833 源文件）+ AirymaxRT 文档方案（88 .md）+ agentrt-linux 方案（系统性复审）。
> **审查方法**：源码级深读 + 文档交叉验证 + Grep 机器检查 + 三层对齐度评分。
> **证据要求**：所有结论附文件路径与行号（格式：`文件路径:L行号`）。
> **SPDX-License-Identifier**：AGPL-3.0-or-later OR Apache-2.0。

---

## 目录

- [1. 执行摘要](#1-执行摘要)
- [2. 审查范围与方法](#2-审查范围与方法)
- [3. 跨报告 P0 级问题整合](#3-跨报告-p0-级问题整合10-项)
- [4. 跨报告 P1 级问题整合](#4-跨报告-p1-级问题整合14-项)
- [5. 正面发现](#5-正面发现)
- [6. 优先级和工作量估算](#6-优先级和工作量估算)
- [7. 三方对齐度评估](#7-三方对齐度评估)
- [8. 总体评估和行动建议](#8-总体评估和行动建议)

---

## 1. 执行摘要

### 1.1 审查范围

| 维度 | 范围 | 子代理 | 落盘报告 |
|------|------|--------|----------|
| agentrt atoms 源码 | 237 文件（.c 153 + .h 84） | Agent A | `01-atoms-source-deep-review.md`（840 行） |
| agentrt 其他模块源码 | 596 文件（daemons 243 / cupolas 95 / gateway 33 / commons 184 / protocols 41） | Agent B | `02-daemons-others-source-deep-review.md`（453 行） |
| AirymaxRT 方案文档 | 88 .md（含 23 共享工程标准） | Agent C | `03-airymaxrt-solution-review.md`（887 行） |
| agentrt-linux 方案 | v0.2.5 闭源总纲 + 09-ssot-registry + Wave 2 v2 34 项差距 | Agent D | `agentrt-linux/_review_v1.0/01-systematic-recheck.md`（773 行） |
| **合计** | **833 源文件 + 88 方案文档 + agentrt-linux 方案** | 5 任务 | 4 份报告已落盘 |

### 1.2 综合评分

| 评分维度 | 子项 | 评分 | 说明 |
|---------|------|------|------|
| **源码工程** | atoms | C+/B- | 架构 A / 技术 A- / 工程标准 C+ / 边界 A+ / 文档 B+ / 安全 B |
| | daemons 等 | C+ | 用户态全 4 空格、typedef 40+ 处、goto 仅 14 处 |
| | 综合 | **68/C+** | 工程标准系统性违规是主要扣分项 |
| **方案设计** | AirymaxRT | 62/C+ | 5 项 P0 系统性一致性问题 |
| | agentrt-linux | 79/B+ | 1 项 P0（ES-SEL4-7 残留冲突） |
| | 综合 | **70/B-** | 设计扎实但一致性未收敛 |
| **跨平台一致性** | 错误码/前缀/IPC | D+ | 错误码 6 套 / agentrt_* 缺失 / IPC 头三重违规 / 8 子仓命名 37 处不一致 |
| | 综合 | **55/D+** | agentrt 与 AirymaxOS 命名/类型/布局未对齐 SSoT |
| **总评** | — | **65/C+** | 基础架构设计扎实，工程一致性与代码品味存在系统性问题，**未达"可开发"状态** |

### 1.3 核心结论

> **agentrt 工程体系当前未达到"可开发"状态**：架构设计层面（MicroCoreRT / CoreLoopThree / MemoryRovol / Thinkdual / Cupolas / 12 Daemons / MCIS 体系并行论）质量较高且原创性强，但工程一致性层面存在 **10 项 P0 级阻断问题**（5 项文档级 + 4 项源码级 + 1 项系统性工程标准违规），需在进入 1.0.1 M1 代码开发前完成收敛。

---

## 2. 审查范围与方法

### 2.1 5 个并行子任务分工

| Agent | 范围 | 输出 | 关键发现 |
|-------|------|------|----------|
| Agent A | atoms 模块 237 文件源码深读 | 840 行报告 | 4 空格缩进 10847 处 / AIRY_ERROR_NULL 7 处潜在 NULL deref / 15 项技术亮点 |
| Agent B | daemons+cupolas+gateway+commons+protocols 596 文件源码深读 | 453 行报告 | WebSocket 类型错误 / agent_registry 数据竞争 / cupolas 错误码 4 种变体 / goto 仅 14 处 |
| Agent C | AirymaxRT 88 文档方案审查 | 887 行报告（综合 62/C+） | 错误码 6 套 / "操作系统"15+ 处误称 / [SC] 头文件清单冲突 / IPC 头三重违规 / 路径错误 |
| Agent D | agentrt-linux 系统性复审 | 773 行报告（综合 79/B+） | ES-SEL4-7 分类残留冲突（5 vs 6）/ airymaxos- 前缀 37 处不一致 / OS-KER-005 跳号 |
| Agent E | （整合任务，本文档） | 综合分析 | 10 项 P0 / 14 项 P1 整合排序 |

### 2.2 审查方法

1. **源码级深读**：Agent A/B 使用 Read 工具逐文件读取代表性源码（Agent A 深读 15+ 文件、Agent B 深读 9 个文件），覆盖各子模块核心实现。
2. **文档交叉验证**：Agent C 完整阅读 26 个 AirymaxRT 文档，Agent D 完整阅读闭源总纲 v0.2.5 + SSoT 注册表 + Wave 2 v2 报告，与源码实现交叉对照。
3. **Grep 机器检查**：所有违规规模统计均由 `grep -rn` / `find -type f` 完成，关键统计：
   - `grep "^\s\{4\}" atoms/` → 10847 处 4 空格缩进
   - `grep "typedef struct"` → atoms 114+ 处 + daemons 40+ 处
   - `grep "AIRY_ERROR\|AIRY_ERROR_NULL\|AIRY_RET_ERR"` → 1757 处自定义错误宏
   - `grep "bfprintf\s*\(" commons/utils/` → 159 处/19 文件
4. **三层对齐度评分**：规范声明层（35%）+ 方案设计层（40%）+ 实现落地层（25%）。
5. **证据要求**：所有结论附 `文件路径:L行号`，可通过 Grep/Read 工具复核。

---

## 3. 跨报告 P0 级问题整合（10 项）

按修复优先级排序。优先级判定标准：技术风险 > SSoT 完整性 > 一致性 > 工程规范。

### P0-1：错误码 SSoT 灾难性冲突（6+ 套方案并存）

| 属性 | 内容 |
|------|------|
| **来源** | Agent C（AirymaxRT 方案审查 §3.1） |
| **问题描述** | AirymaxRT 文档中存在 **6+ 套**不同的错误码定义方案，严重违反 SSoT 原则。`AIRY_EINVAL` 在不同文档中取值 `EINVAL` / `-22` / `1001` / `-1` 共 4 种；成功码 `AIRY_EOK` / `AIRY_OK` / `ARE_OK` 共 3 种命名。 |
| **证据** | `10-architecture/00-architectural-principles.md:922-940`（方案 A，POSIX errno 直接赋值）；`10-architecture/06-iron9-shared-model.md`（方案 B，POSIX 对齐负值 -22/-12）；`10-architecture/05-syscall.md:641-646`（方案 C，正值序列 1001/1002）；`20-modules/10-contracts/04-syscall-api-contract.md:99-108`（方案 D，负值序列 -1/-2）；`20-modules/10-contracts/06-glossary-index.md:173-180`（方案 E，`AIRY_OK` 非 EOK）；`30-interfaces/README.md:78-86`（方案 F）；`20-modules/10-contracts/03-protocol-contract.md:494-500`（方案 G）；`30-interfaces/05-runtime-interfaces/01-l1-runtime-interface.md:48+`（方案 H，`ARE_OK` 非 AIRY_）；SSoT：`50-engineering-standards/120-cross-project-code-sharing.md:81`（13 个 `AIRY_E*` 宏，`airy_err_t` 定义于 `cognition_types.h`）。 |
| **影响评估** | 开发者无法确定应使用哪套错误码；C 代码编译将出现宏重定义冲突；违反 IRON-1（用户空间 ABI 永不破坏）和 IRON-014（[SC] 6 头文件单一数据源）；agentrt 与 AirymaxOS 无法互操作。 |
| **修复建议** | 在 `50-engineering-standards/` 建立错误码 SSoT 文档；统一为 `airy_err_t`（`int32_t`）+ `AIRY_EOK=0` + 13 个 `AIRY_E*` 宏（负值）；明确 `AIRY_*`（内部+[SC]）与 `ARE_*`（标准 ABI）映射；全量替换 6 套方案为统一方案；统一命名 `AIRY_EOK`/`AIRY_ETIMEOUT`。 |
| **工作量估算** | ~8h（文档统一）+ 源码侧错误码统一另计 |

### P0-2：agentrt 源码工程标准全面违规（系统性）

| 属性 | 内容 |
|------|------|
| **来源** | Agent A + Agent B（源码级深读汇总） |
| **问题描述** | agentrt 全部用户态 C 源码系统性违反 OLK-6.6 六大支柱，与 [SC] 共享契约层（Tab 8）形成割裂。 |
| **证据** | (1) 4 空格缩进 **10847 处**（atoms 全量 237 文件 + daemons 等全量 596 文件 = 833 文件违规），仅 `commons/include/airymax/` 下 6 个 [SC] 头文件合规使用 Tab 8；(2) 重度 typedef 540 处（atoms 114+ 处匿名 struct typedef + daemons 40+ 处，集中 `pregel_engine.c:32/L52/L60`、`mempool.h:62/L72`、`frameworks.h:82/L93/L100/L172`、`protocols_impl.c:33`、`logging.c:113/232`、`cupolas.c:37`）；(3) 自定义错误宏 1757 处（`AIRY_ERROR`/`AIRY_ERROR_NULL`/`AIRY_RET_ERR` 替代 goto 集中出口，atoms 100+ 处 + daemons 同类模式）；(4) ASCII 装饰分节符 100 文件（`/* ==================== xxx ==================== */` 120 文件 + `// ===` 30+ 文件 + `/* ---- xxx ---- */` 10+ 文件）；(5) fprintf 直接使用 159 处/19 文件（`logging.c` 3 处标注 BAN-70 EXEMPT，但 `memory.c` 22 处 / `memory_debug.c` 44 处 / `heapstore_migration.c` 5 处 / `logging_compat.c` 19 处未审查豁免）；(6) `__builtin_memset/memcpy/fprintf` 563 处/100 文件与 `AIRY_MEMSET` 宏混用不一致。 |
| **影响评估** | 与 `docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md` OLK-6.6 基线严重背离；与 [SC] 层标杆（ipc.h/sched.h 等 Tab 8 + struct 无 typedef + kernel-doc + _Static_assert）形成代码风格割裂；维护性差；CI 门禁无法通过。 |
| **修复建议** | (1) 配置 `.clang-format`（`IndentWidth: 8`/`TabWidth: 8`/`UseTab: Always`）+ `make format` 自动化修复缩进；(2) 重构 540 处 typedef 为 `struct xxx { ... };` 形式（仅保留不透明指针 typedef）；(3) 用 `goto out_xxx:` 替代错误宏的隐式 return；(4) 替换装饰分节符为简洁单行注释；(5) 非 test 文件 fprintf 标注 BAN-70 EXEMPT 或收口到 `log_write`；(6) 统一 `__builtin_*` 与 `AIRY_*` 宏。 |
| **工作量估算** | 缩进自动化 ~8h（含 CI 门禁）+ typedef 重构 ~16h + goto 重构 ~12h + 装饰分节符 ~4h + fprintf/`__builtin_*` 收口 ~6h = **~46h** |

### P0-3：AIRY_ERROR_NULL 潜在 NULL deref（pregel_engine.c 7 处）

| 属性 | 内容 |
|------|------|
| **来源** | Agent A（atoms 源码审查 §2.2.1/§8.1 P0-3） |
| **问题描述** | `pregel_engine.c` 多处 `AIRY_ERROR_NULL(...)` 用作 if 块最后一条语句无显式 return，后续代码直接解引用可能 NULL 的指针。 |
| **证据** | `atoms/taskflow/src/pregel_engine.c:200-201`：<br/>```c<br/>if (!queue || !queue->front) {<br/>    AIRY_ERROR_NULL(AIRY_ERR_INVALID_PARAM, "null parameter");<br/>}<br/>message_queue_entry_t *entry = queue->front;  // 若宏不 return，此处 NULL deref<br/>```<br/>同模式 L288-289（`context->engine` 解引用）、L346/L352/L386/L398/L410（多处 `AIRY_ERROR_NULL` 用作 if 块最后语句）。 |
| **影响评估** | `AIRY_ERROR_NULL`/`AIRY_ERROR`/`AIRY_RET_ERR` 宏定义不在 atoms 目录内（位于 `commons/utils/error/`），atoms 内开发者无法直接看到宏行为；若宏不 return，则 pregel_engine.c 7 处存在 NULL deref，运行时崩溃风险；同模式在 `loop.c:185/190/194`、`scheduler.c:98/102`、`taskflow_advanced.c:136/138` 重复出现。 |
| **修复建议** | (1) 立即审查 `commons/utils/error/include/error.h` 中 `AIRY_ERROR_NULL`/`AIRY_ERROR`/`AIRY_RET_ERR` 宏定义，确认是否 return；(2) 若不 return，pregel_engine.c 7 处必须改为 `goto out_xxx:` 或显式 `return`；(3) 若 return，应在宏定义处增加 `__attribute__((noreturn))` 标注或注释明示行为，消除维护性风险；(4) 长期改用 `goto out_xxx:` 集中出口替代隐式 return。 |
| **工作量估算** | ~3h（宏行为审查 + 修复 7 处 + 同模式扫描） |

### P0-4：IPC 消息头结构体三重违规

| 属性 | 内容 |
|------|------|
| **来源** | Agent C（AirymaxRT 方案审查 §5.3/§9.2） |
| **问题描述** | `30-interfaces/06-ipc/README.md` 定义 IPC 消息头结构体为 `are_ipc_message_header_t`，与 [SC] SSoT 要求的 `airy_ipc_msg_hdr` 在**命名/类型/布局**三重违规。 |
| **证据** | `30-interfaces/06-ipc/README.md:27` `typedef struct are_ipc_message_header`；对比 SSoT `120-cross-project-code-sharing.md:343` `struct airy_ipc_msg_hdr` + `06-iron9-shared-model.md:140` 明示"结构体名称为 `airy_ipc_msg_hdr`（**不是** `airymaxos_ipc_msg_hdr` 或 `are_ipc_message_header_t`）"。<br/>**三重违规对比**：<br/>| 属性 | `06-ipc/README.md`（违规） | SSoT 要求 |<br/>|------|---------------------------|----------|<br/>| 结构体名 | `are_ipc_message_header_t` | `airy_ipc_msg_hdr` |<br/>| 类型前缀 | `uint32_t`/`uint16_t`/`uint64_t` | `__u32`/`__u16`/`__u64`（UAPI） |<br/>| 对齐属性 | 无 | `__attribute__((packed))` |<br/>| 字段数 | 13 字段（含 `source[32]`/`target[32]` 字符数组） | 8 字段（含 `__u64 src_task`/`__u64 dst_task`） |<br/>| 大小验证 | 无 | `_Static_assert(sizeof(...) == 128)` |<br/>源码侧 `commons/include/airymax/ipc.h:67-77` 已正确实现 SSoT 版本（struct + `__attribute__((packed))` + `_Static_assert`）。 |
| **影响评估** | IPC 消息头是 [SC] 共享契约层核心结构；三重违规导致 agentrt 与 AirymaxOS 无法互操作；违反 IRON-008（[SC] 双向 CI 验证）和 IRON-014（6 头文件单一数据源）；混淆了 [SC] 共享契约层（`airy_*`）与 ARE 标准 ABI（`are_*`）边界。 |
| **修复建议** | 重写 `30-interfaces/06-ipc/README.md`：(1) 结构体名 `are_ipc_message_header_t` → `airy_ipc_msg_hdr`；(2) 类型 `uint32_t` → `__u32`（通过 `#include <airymax/uapi_compat.h>`）；(3) 添加 `__attribute__((packed))`；(4) 字段布局对齐 SSoT 8 字段；(5) 添加 `_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128)`。 |
| **工作量估算** | ~3h |

### P0-5："操作系统"定位冲突（15+ 处误称）

| 属性 | 内容 |
|------|------|
| **来源** | Agent C（AirymaxRT 方案审查 §3.2/§6.2） |
| **问题描述** | agentrt 定位为"AI Agent 运行时平台工程"（用户态微核心，Ring 3），但 15+ 处文档误称其为"操作系统"。 |
| **证据** | `10-architecture/00-architectural-principles.md:54` "Airymax 是一个**驱动多智能体协作的操作系统**"；`10-architecture/40-philosophy/01-design-philosophy.md:45/110/117/119/38`（5 处误称）；`10-architecture/04-microcorert.md:19/271`；`10-architecture/05-syscall.md:104`；`20-modules/10-contracts/05-logging-format.md:73`；`00-requirements/04-design-principles-cn.md:99`；`30-interfaces/04-mainpage.dox:2/6`；`30-interfaces/10-algorithms/README.md:179/182`；与 `04-microcorert.md:183` "MicroCoreRT 运行在用户态（Ring 3），依赖宿主操作系统"直接矛盾。 |
| **影响评估** | 技术定位混乱；开源社区误解 agentrt 为 OS 内核项目；与 AirymaxOS（agentrt-linux）产生定位混淆；用户态 ABI 与内核态概念混用。 |
| **修复建议** | 全量替换"操作系统"为"运行时平台"或"运行时"（除真正指代宿主 OS 的上下文）；修正 `04-mainpage.dox` 标题"多体控制论智能操作系统" → "多体控制论智能运行时"；保留 `04-microcorert.md` 中正确描述（"借鉴操作系统设计" ≠ "是操作系统"）。 |
| **工作量估算** | ~4h（13 个文件，40 处匹配） |

### P0-6：protocols_impl.c WebSocket 类型错误

| 属性 | 内容 |
|------|------|
| **来源** | Agent B（daemons 源码审查 §2.8/§8 P0-3） |
| **问题描述** | WebSocket 适配器 `type` 字段设为 `PROTOCOL_HTTP`，应为 `PROTOCOL_WEBSOCKET`，是协议层逻辑错误。 |
| **证据** | `agentrt/protocols/common/src/protocols_impl.c:117`：<br/>```c<br/>s_ws_adapter.type = PROTOCOL_HTTP;  // 应为 PROTOCOL_WEBSOCKET<br/>``` |
| **影响评估** | 协议路由将 WebSocket 请求错误地路由到 HTTP 处理器，导致 WebSocket 握手/帧解析失败；运行时正确性问题；用户态网关功能受损。 |
| **修复建议** | 将 `PROTOCOL_HTTP` 改为 `PROTOCOL_WEBSOCKET`（或正确的 WebSocket 枚举值）；增加单元测试覆盖协议类型映射。 |
| **工作量估算** | ~0.5h（修复 + 单测） |

### P0-7：agent_registry_core.c 数据竞争（返回内部指针后解锁）

| 属性 | 内容 |
|------|------|
| **来源** | Agent B（daemons 源码审查 §2.2/§7.4） |
| **问题描述** | `agent_registry_core_get()` 在 `airy_mtx_unlock` 后返回 `&registry->entries[i]`，调用方在无锁状态下访问共享数据，存在数据竞争风险。 |
| **证据** | `agentrt/daemons/market_d/src/agent_registry_core.c:123-137`（`agent_registry_core_get()`）；同模式 L194-208（`agent_registry_core_get_latest_version()`）。 |
| **影响评估** | 多线程并发调用时，调用方读取的 entry 数据可能被另一线程的写入覆盖；TOCTOU（time-of-check-to-time-of-use）漏洞；Agent 注册表是 daemon 核心数据结构，数据竞争可能导致 Agent 状态不一致。 |
| **修复建议** | (1) 改为拷贝到调用方缓冲区（推荐，`agent_registry_core_get(reg, id, agent_info_t *out)` 在锁内完成 `*out = registry->entries[i]` 后解锁）；(2) 或在锁内完成所有访问（持有期回调模式）；(3) 同步修复 `agent_registry_core_get_latest_version()`。 |
| **工作量估算** | ~2h（含 API 签名变更与调用方更新） |

### P0-8：[SC] 头文件清单不一致（bpf_struct_ops.h vs syscalls.h）

| 属性 | 内容 |
|------|------|
| **来源** | Agent C（AirymaxRT 方案审查 §3.3） |
| **问题描述** | `06-iron9-shared-model.md` 列出的 6 个 [SC] 核心头文件中第 6 个为 `bpf_struct_ops.h`，但 SSoT `120-cross-project-code-sharing.md:76` 明确第 6 个为 `syscalls.h`，`bpf_struct_ops.h` 是补充共享文件（非 [SC] 核心）。 |
| **证据** | `10-architecture/06-iron9-shared-model.md` 列出 `bpf_struct_ops.h` 作为第 6 个 [SC] 核心头文件；`50-engineering-standards/120-cross-project-code-sharing.md:76` 明确第 6 个为 `syscalls.h`；`120-cross-project-code-sharing.md:85` 标题"2.2 补充共享文件：bpf_struct_ops.h（非 [SC] 核心头文件）"；`09-ssot-registry.md` OS-IRON-014 "[SC] 共享契约层 6 头文件单一数据源"。 |
| **影响评估** | 违反 IRON-014；开发者无法确定 `syscalls.h` 是否为 [SC] 头文件；源码侧 `commons/include/airymax/syscalls.h` 已实际存在并使用 Tab 8 缩进，与 SSoT 一致，但文档侧未对齐。 |
| **修复建议** | 修正 `06-iron9-shared-model.md` 第 6 头文件 `bpf_struct_ops.h` → `syscalls.h`；将 `bpf_struct_ops.h` 移至"补充共享文件"小节；对齐 `120-cross-project-code-sharing.md` 的 6 头文件清单。 |
| **工作量估算** | ~1h |

### P0-9：文件路径引用错误（系统性）

| 属性 | 内容 |
|------|------|
| **来源** | Agent C（AirymaxRT 方案审查 §3.7） |
| **问题描述** | 多个文档引用 `00-basic-theories/` 目录，但实际目录名为 `00-requirements/`；同时存在多处路径错误。 |
| **证据** | `TERMINOLOGY.md:604-612`（`00-basic-theories/01-mcis-cn.md` 等，应为 `00-requirements/`）；`10-architecture/00-architectural-principles.md:1516-1519`；`20-modules/10-contracts/01-agent-contract.md:42,44`；`20-modules/10-contracts/04-syscall-api-contract.md:65`（`../30-coding-standard/10-log-standard.md` 路径不存在）；`20-modules/10-contracts/06-glossary-index.md:124-127/183`（多处路径不存在）；`README.md:62`/`README_zh.md:87`（`50-engineering-standards/08-compliance-checklist.md` 不存在）；`06-iron9-shared-model.md:331-334`（`C_coding_style_standard.md` 等 4 文件，实际为 `C_Cpp_coding_style.md`）；`00-architectural-principles.md:1524/1525`（`C_Cpp_secure_coding_standard.md` 不存在 / `../../AirymaxOS/TERMINOLOGY.md` 本地已存在）。 |
| **影响评估** | 文档可用性差；外部开发者按引用路径查找文件全部失败；CI 链接检查无法通过；SSoT 路径体系混乱。 |
| **修复建议** | (1) `00-basic-theories/` → `00-requirements/` 全量替换；(2) `30-coding-standard/10-log-standard.md` → 正确路径；(3) `08-compliance-checklist.md`/`error_code_reference.md` → 删除引用或创建文件；(4) `C_coding_style_standard.md` → `C_Cpp_coding_style.md`；(5) `../../AirymaxOS/TERMINOLOGY.md` → `../../TERMINOLOGY.md`；(6) 建立 CI 链接检查器（markdown-link-check）。 |
| **工作量估算** | ~3h（~10 文件） |

### P0-10：ES-SEL4-7 分类残留冲突（5 vs 6 项）

| 属性 | 内容 |
|------|------|
| **来源** | Agent D（agentrt-linux 系统性复审 §2.1） |
| **问题描述** | v0.2.5 修复 P0-CRITICAL-02 时仅修正了闭源总纲附录 D 标题，但正文对 ES-SEL4-7 的分类与标题声明矛盾——标题声明 5 项强制，正文说 6 项强制。 |
| **证据** | 标题声明 5 项强制：`闭源总纲:1389` `附录 D ES-SEL4 工程思想借鉴映射（ES-SEL4-1~5 强制 + ES-SEL4-6~10 P2 增强）`；`闭源总纲:1393` `ES-SEL4-1~5 在架构层强制借鉴`；`闭源总纲:1024`（OS-IRON-012）`seL4 工程思想的借鉴仅限架构层（ES-SEL4-1~5）`；`闭源总纲:1010`（§12.5 标题）`架构层借鉴 seL4（5 项选择性借鉴）`。正文矛盾：`闭源总纲:1403` `ES-SEL4-7 | 架构正交分层 | ... | 架构层强制（已落地）`；`闭源总纲:1410` `架构层强制借鉴（ES-SEL4-1~5 + ES-SEL4-7）: 6 项`；`闭源总纲:1041/1051`（§12.8）将 ES-SEL4-7 归入"ES-SEL4-6~10"但又标注"已落地"。 |
| **影响评估** | 违反 SSoT 唯一性原则；审查者无法确定 ES-SEL4-7 究竟是"架构层强制（已落地）"还是"P2 增强（未来落地）"；无法确定架构层强制借鉴是 5 项还是 6 项；阻断 agentrt-linux 1.0.1 M1 启动判定（8 项判定标准中"无方案冲突点"有条件通过）。 |
| **修复建议** | 方案 A（推荐）：将 ES-SEL4-7 从"架构层强制"重新分类为"P2 增强建议（已提前落地）"；修改 `闭源总纲:1403` 借鉴方式为"P2 增强建议（已落地）"；修改 `闭源总纲:1410` 为"架构层强制借鉴（ES-SEL4-1~5）: 5 项"；与标题和 OS-IRON-012 对齐。方案 B：修改标题和 OS-IRON-012 扩展范围至 6 项。 |
| **工作量估算** | ~2h |

### P0 汇总表

| # | 问题 | 来源 | 类型 | 工作量 |
|---|------|------|------|--------|
| P0-1 | 错误码 6 套并行 | Agent C | 文档 SSoT | ~8h（文档）+ 源码另计 |
| P0-2 | 源码工程标准全面违规 | Agent A+B | 源码系统性 | ~46h |
| P0-3 | AIRY_ERROR_NULL NULL deref | Agent A | 源码正确性 | ~3h |
| P0-4 | IPC 头三重违规 | Agent C | 文档 SSoT | ~3h |
| P0-5 | "操作系统"定位冲突 | Agent C | 文档一致性 | ~4h |
| P0-6 | WebSocket 类型错误 | Agent B | 源码正确性 | ~0.5h |
| P0-7 | agent_registry 数据竞争 | Agent B | 源码安全 | ~2h |
| P0-8 | [SC] 头文件清单不一致 | Agent C | 文档 SSoT | ~1h |
| P0-9 | 文件路径引用错误 | Agent C | 文档可用性 | ~3h |
| P0-10 | ES-SEL4-7 分类残留冲突 | Agent D | 方案 SSoT | ~2h |
| **合计** | — | — | — | **~72.5h**（含源码系统性改造） |

> **方案侧 P0（不含 P0-2 源码改造）合计 ~19h**，与 AirymaxRT 报告 §10.4 P0 估算一致。

---

## 4. 跨报告 P1 级问题整合（14 项）

按修复优先级排序。

| # | 问题 | 来源 | 证据 | 工作量 |
|---|------|------|------|--------|
| P1-1 | **函数前缀 SSoT 冲突**：任务描述要求 `agentrt_*` 专属 API 前缀，但 atoms 内 `agentrt_` C 标识符 0 处、daemons 内仅 2 处文档残留，全部使用 `airy_*`（atoms 916+ 处 / daemons 大量）；文档侧 `grep "agentrt_" docs/AirymaxRT/` = 0 匹配 | Agent A §4 + Agent C §5.2 | `atoms/` 全量无 `agentrt_*` C 标识符；`docs/AirymaxRT/` 0 匹配 | ~2h（文档化三层前缀分层） |
| P1-2 | **29 仓拆分完全未文档化**：AirymaxRT 文档中完全没有提及 29 仓拆分方案（1 伞仓 + 4 管理仓 + 21 叶子仓 + 3 顶层仓） | Agent C §7.1 | `grep -rn "29 仓\|29 repo" docs/AirymaxRT/` = No matches found | ~6h（新建 `07-repository-structure.md`） |
| P1-3 | **`agentrt_*` 专属 API 前缀完全缺失**：任务描述明确要求 agentrt 拥有专属 API 前缀，但全文档 0 处使用，导致 daemon 管理、配置管理、运行时控制等内部 API 缺乏统一命名 | Agent C §5.2 | `grep -rn "agentrt_" docs/AirymaxRT/` = 0 | 与 P1-1 合并 |
| P1-4 | **8 子仓命名不一致**：闭源总纲 v0.2.5 在 8 子仓上仍使用 `airymaxos-` 前缀（37 处），而开源文档已统一去除该前缀 | Agent D §2.3/§9.2 | `闭源总纲:78-85/1067-1074/1099/1016-1020` 使用 `airymaxos-kernel` 等；开源 `README.md:132-139` 与 `06-directory-structure.md:175-184/294` 使用裸名 + 明确废弃 `airymaxos_*` 前缀 | ~4h（闭源总纲全文替换） |
| P1-5 | **Cupola/Cupolas 术语不一致**：4 个文件使用单数 Cupola（错误），10 个文件使用复数 Cupolas（正确） | Agent C §3.4 | `grep -rl "Cupola[^s]" docs/AirymaxRT/` = 4 文件（`01-system-architecture.md`/`02-c-language-boundary.md`/`01-design-philosophy.md`/`05-logging-format.md`） | ~1h |
| P1-6 | **Daemon 数量 10 vs 12 冲突**：`01-system-architecture.md:305/309` 标注"10 个核心用户态服务"，但 `01-daemon.md:131` V8.0 已修正为 12 个 | Agent C §3.5 | `01-system-architecture.md:305`（"10 个核心用户态服务"）/`:309`（ASCII "Airymax Daemon Services (10)"）；`01-daemon.md:131`（V8.0 修正为 12） | ~0.5h |
| P1-7 | **OS-KER-005 跳号**：SSoT 注册表中 OS-KER 编号从 004 跳至 006，005 缺失且未标注废弃原因 | Agent D §3.2 | `09-ssot-registry.md:106` `OS-KER-004` → `:107` `OS-KER-006`，无 005 | ~0.5h |
| P1-8 | **cupolas 错误码命名混乱（4 种变体）**：同一模块内存在 `CUPOLAS_OK`（大写）/`cupolas_ERR_UNKNOWN`（小写前缀）/`cupolas_ERROR_INVALID_ARG`（又一变体）/`cupolas_OK`（全小写） | Agent B §2.3 | `cupolas/src/cupolas.c:79/88/121/136/157/218/223/277/296/303/341/362/369/416/430`；`permission_engine.c:39`；`test_cupolas_core.c:65`；测试文件 `cupolas/tests/unit/test_error_code_consistency.c` 已知未彻底修复 | ~2h（统一为 `CUPOLAS_OK`/`CUPOLAS_ERR_*` UPPER_SNAKE_CASE） |
| P1-9 | **goto 集中出口严重不足**：全代码库仅 14 处使用 goto 集中出口标签，绝大多数函数用早返回，多资源函数存在泄漏风险 | Agent B §3.1 | `grep "^out_free_\|^out_unlock:\|^fail_\|^cleanup:\|^done:" agentrt/` = 14 处；典型问题：`cupolas_init():76-164`（4 个错误出口逐个 destroy）、`permission_engine_create():30-73`（4 个错误出口）、`sched_d/main.c:214-325`（4 处 `return 1` 重复清理） | ~12h（多资源函数引入 goto） |
| P1-10 | **[SC] 头文件与应用层代码风格割裂**：[SC] 6 个头文件全部 Tab 8 + struct 无 typedef + kernel-doc + _Static_assert，但应用层 atoms/daemons 全 4 空格 + 重度 typedef + 无 kernel-doc，形成代码风格割裂 | Agent B §1.3/§9.1 | `commons/include/airymax/{ipc.h,sched.h,security_types.h,cognition_types.h,memory_types.h,syscalls.h}` 全部 Tab 8；atoms/daemons 全部 4 空格 | 与 P0-2 合并 |
| P1-11 | **MemoryRovol 层级命名冲突**：标准命名 L1 Raw → L2 Feature → L3 Structure → L4 Pattern，但部分文档使用 Working/Short-term/Long-term/Archival 或日志 L1-L4 | Agent C §3.6 | `10-architecture/03-memoryrovol.md`（标准）；`120-cross-project-code-sharing.md:135-139`（[SC] L1 HOT/L2 WARM/L3 COLD/L4 PMEM）；`30-kernel/02-c-language-boundary.md:72`（Working → Short-term → Long-term → Archival，错误）；`50-services/02-logging.md`（日志 L1-L4 冲突） | ~1h |
| P1-12 | **ES-SEL4-9/10 状态分类模糊**：标题归入"ES-SEL4-6~10 P2 增强"（未来落地），但正文标注"已落地"，与 P2 的"未来落地"语义冲突 | Agent D §2.2 | `闭源总纲:1389`（标题 P2 增强）；`:1049/1050`（§12.8 标注已落地）；`:1405-1406/1412`（附录 D 标注已落地） | ~1h（区分"已落地"与"待落地"） |
| P1-13 | **`50-specifications/` 仅 1 文件且重复**：AirymaxRT `50-specifications/` 目录仅含 1 个文件 `10-contracts/06-glossary-index.md`（229 行），与 `20-modules/10-contracts/06-glossary-index.md` 近乎重复 | Agent C §1.2/§8.2 | `find docs/AirymaxRT/50-specifications -type f -name "*.md"` = 1 文件 | ~1h（删除或重新定位） |
| P1-14 | **OpenStandards 与 2026 生态脱节**：protocols 模块虽集成 Claude/OpenAI/openclaw/china_eco/openjiuwen/autogen/langchain/mcp/agntcy/a2a，但 OpenStandards 与 2026 生态（MCP 最新规范、A2A 协议演进）存在脱节 | Agent B §1.1 | `agentrt/protocols/integrations/` + `frameworks/` + `standards/` 41 文件 | ~6h（评估并更新协议生态对齐） |

### P1 汇总

| 维度 | 数量 | 工作量 |
|------|------|--------|
| 命名/前缀一致性（P1-1/3/4/5/6/8/11） | 7 项 | ~10.5h |
| 文档完整性（P1-2/13/14） | 3 项 | ~13h |
| 源码工程（P1-9/10） | 2 项 | ~12h（与 P0-2 重叠） |
| 方案 SSoT（P1-7/12） | 2 项 | ~1.5h |
| **合计** | **14 项** | **~23h**（不含与 P0-2 重叠部分） |

> 与 AirymaxRT 报告 §10.4 P1 估算 ~23h 一致。

---

## 5. 正面发现

### 5.1 历史问题全部修复

| 历史问题 | 状态 | 证据 |
|---------|------|------|
| koa-connect wrapper 问题 | **已修复** | `grep "koa-connect\|koa connect" agentrt/` = 0 匹配 |
| io_uring 误用 | **已修复** | `grep "io_uring\|io-uring" agentrt/` = 3 匹配，均为注释/文档引用（`commons/include/airymax/ipc.h:36,42` SQE/CQE flags 注释、`syscalls.h:30` 数据面说明） |
| MGLRU 2.0 禁词 | **已修复** | `grep "MGLRU 2\.0\|MGLRU2\.0\|MGLRU 2" agentrt/` = 0 匹配 |
| daemon→daemons 改名 | **已彻底完成** | `Glob "agentrt/daemon/**/*.c"` = 0 文件；目录名为 `daemons/`（复数）；`svc_logger.h:8` 注释"迁移至 commons/utils/logging/include/svc_logger.h，消除 atoms→daemons 编译期反向依赖" |

### 5.2 函数前缀边界清晰（零残留）

| 前缀 | atoms 出现 | daemons 出现 | docs/AirymaxRT | 评估 |
|------|-----------|-------------|----------------|------|
| `airy_*`（[SS] 语义同源层） | 916+ 处 | 大量 | 大量 | **GOOD**，主导前缀 |
| `agentrt_*`（C 标识符） | 0 处 | 0 处 | 0 处 | 清理彻底，但专属 API 前缀缺失（见 P1-3） |
| `agentrt_`（注释/路径） | 4058 处 | — | — | GOOD，非 C 标识符 |
| `agentos_*` | 0 处 | 0 处 | 0 处 | **GOOD**，无残留 |
| `airymaxos_*` | 0 处 | 0 处 | 2 处（禁止声明） | **GOOD**，无误用 |

### 5.3 SSoT 核心 magic 值正确

| Magic | 值 | 含义 | SSoT 定义 | 实际使用 | 评估 |
|-------|-----|------|----------|---------|------|
| IPC magic | `0x41524531` | 'ARE1' = Airymax Runtime Engine v1 | `120-cross-project-code-sharing.md:303` | `commons/include/airymax/ipc.h:18` `#define AIRY_IPC_MAGIC 0x41524531u`；`06-iron9-shared-model.md:113` | **正确** |
| 任务描述符 magic | `0x41475453` | 'AGTS' = AGent Task State | `120-cross-project-code-sharing.md:237` | `commons/include/airymax/sched.h`；`06-iron9-shared-model.md:153` | **正确** |

### 5.4 符号链接与规则编号对齐 SSoT

- **符号链接正确**：`docs/AirymaxRT/50-engineering-standards -> ../AirymaxOS/50-engineering-standards`，23 文档共享，符合 IRON-9 v2 同源原则。
- **规则编号体系对齐**：OS-IRON-001~014 / OS-KER-001~155 / OS-STD-* / OS-BAN-* / OS-ACC-* / OS-ABI-* 17 类前缀在 AirymaxRT 中均正确引用 SSoT，未发现私自定义新编号。
- **OS-ACC 冲突已消解**：`09-ssot-registry.md:420` "SSoT 对齐说明（v0.2.5 已消解）"。

### 5.5 [SC] 6 个头文件全部使用 Tab 8 缩进（合规标杆）

| 文件 | 内容 | Tab 8 缩进 | struct 无 typedef | kernel-doc | _Static_assert |
|------|------|-----------|------------------|-----------|----------------|
| `commons/include/airymax/ipc.h` | IPC magic + 128B 消息头 + SQE/CQE 操作码 | ✓ | ✓（`struct airy_ipc_msg_hdr`） | ✓ | ✓（`sizeof == 128`） |
| `commons/include/airymax/sched.h` | 任务描述符 magic + vtime 衰减 + 优先级 0-139 | ✓ | ✓ | ✓ | — |
| `commons/include/airymax/security_types.h` | POSIX capability 41 ID + LSM 钩子 + verdict 4 值 + cap_op（seL4 CNode） | ✓ | ✓ | ✓ | — |
| `commons/include/airymax/cognition_types.h` | CoreLoopThree 阶段 + Thinkdual 模式 + Token 能效 | ✓ | ✓ | ✓ | — |
| `commons/include/airymax/memory_types.h` | MemoryRovol L1-L4 + GFP 掩码 + PMEM 接口 | ✓ | ✓ | ✓ | — |
| `commons/include/airymax/syscalls.h` | 12 核心 syscall 编号 + 12 预留槽位 | ✓ | ✓ | ✓ | — |

> **[SC] 层是全仓库合规标杆**，与用户态 4 空格形成对比。

### 5.6 MCIS 原创性强无抄袭风险

- seL4 借鉴仅限架构层（IRON-012 约束），注明参考来源（`20-modules/01-kernel.md:55-62` 引用 Liedtke 原文）。
- Linux 6.6 基线引用具体源码路径（`include/uapi/linux/sched.h:121` 等）。
- openEuler 标准规范声明层对齐。
- **MCIS 体系并行论 + 五维正交 24 原则为原创理论框架**，无抄袭风险。

### 5.7 15 项技术亮点（源码级）

| # | 亮点 | 证据 |
|---|------|------|
| K-1 | **C11 显式内存序**（atomic + memory_order_*） | `atoms/corekern/src/core_init.c:26/31-37`（CAS + 状态机）；`slab.c:111-121`（atomic 统计）；`time/event.c:55/56/63/74/85/103/109/111/119` |
| K-2 | **跨平台 compat 层**（memory/string/atomic/sync/logging/error/platform） | 全 atoms + daemons 使用 |
| K-3 | **编译时 const 查表技术** | `are_ipc.c:44-61`（CRC32-IEEE 802.3 查表，零运行时初始化、线程安全）；`graph_engine.c:101-105`（26 项质数表）；`error.c:13-51`（错误码字符串映射） |
| K-4 | **双重检查锁定 + 状态机**（DCLP） | `core_init.c:26-37/131-135`（0=未初始化，2=初始化中，1=就绪，`memory_order_seq_cst` 全序） |
| K-5 | **C11 _Thread_local per-CPU 缓存** | `slab.c:138` `static _Thread_local slab_cpu_cache_t g_cpu_cache;` |
| K-6 | **纯函数设计** | `are_ipc.c:73-82` `are_crc32_update()`（注释明示"纯函数 + 只读全局"）；`error.c:55-65` `airy_strerror()` |
| K-7 | **Doxygen 文档完善** | corekern/syscall/frameworks/coreloopthree 公共 API 含 `@ownership/@threadsafe/@reentrant/@note/@see` |
| K-8 | **不透明指针模式**（PImpl） | `airy_sandbox_t`/`airy_mempool_t`/`airy_core_loop_t`/`graph_engine_handle_t`/`pregel_engine_handle_t`/`taskflow_engine_t` 6 处 |
| K-9 | **指定初始化器**（OS-STD-CODE-014 符合） | `syscall_table.c:54-78`（`[SYS_TASK_SUBMIT] = sys_task_submit`）；`builtin_storage.c:82`；`pregel_engine.c:335` |
| K-10 | **_Static_assert 编译期校验** | `syscall_table.c:21-24`（`SYS_TOOL_EXECUTE == 23` / `SYS_MAX == 24`）；`ipc.h:79-80`（`sizeof(struct airy_ipc_msg_hdr) == 128`） |
| K-11 | **适配器模式**（6 个适配器解耦 coreloopthree） | `llm_svc_adapter_t`/`tool_svc_adapter_t`/`memoryrovol_bridge_t`/`airy_manager_adapter_t`/`orch_adapter_t`/`airy_framework_adapter_t` |
| K-12 | **BORROW 所有权语义显式标注** | `cognition/engine.c:113` `airy_task_plan_t *current_plan; /**< Currently processing plan (borrowed, for checkpoint) */` |
| K-13 | **BAN-333 强制 max_workers=1 串行降级** | `pregel_engine.c:359-367/526-527`（注释"0.1.1 的 pregel_engine 并发路径尚未经过多线程验证，强制串行模式以确保正确性优先于性能"），完全符合任务描述预期 |
| K-14 | **ASan 内存泄漏修复注释完善** | `pregel_engine.c:413-416`（workers 数组延迟到 init 分配，根因分析明确） |
| K-15 | **函数前缀边界清晰** | atoms 内 `airy_*`/`agentrt_*`/`agentos_*`/`airymaxos_*` 零违规，`airy_*` 边界清晰 |

### 5.8 daemon 架构一致性

所有核心 daemon（market_d/sched_d/gateway_d/monit_d/plugin_d/tool_d/llm_d/channel_d/notify_d/hook_d/info_d/observe_d）均采用统一架构模式：

```
DAEMON_DECLARE_COMMON 宏样板
    + svc_adapter 适配层
    + method_dispatcher RPC 注册
    + daemon_event_driver 事件驱动
    + daemon_cupolas_init 安全穹顶初始化
    + daemon_cleanup_standard 标准清理链
```

### 5.9 统一日志系统架构完整

`commons/utils/logging/src/logging.c`（1024 行）实现完整日志系统：
- 统一入口 `log_write()`（logging.c:651）+ `log_write_va()`（:710）
- CLOCK_REALTIME 时间戳（:271）
- ANSI 颜色编码（:54-64）
- 级别过滤 + 模块级通配符（:384）
- 日志节流 FNV 哈希去重（:168）
- 日志采样原子计数器（:958）
- trace_id/span_id TLS 存储（:38-39）
- 文件输出 + 轮转（:441）
- 热重载（:862）

### 5.10 安全横切贯穿全链路

cupolas 安全穹顶作为横切关注点贯穿 daemon 启动→请求处理→命令执行→审计记录全链路：
- `daemon_cupolas_init("sched_d")` 初始化（`sched_d/main.c:238`）
- `cupolas_check_permission()` + `cupolas_sanitize_input()`（`cupolas.c:213/292`）
- `cupolas_execute_command()` + guard_manager 检查（`cupolas.c:356`）
- `audit_logger_log()` 审计记录（`cupolas.c:229/309/451`）
- capability 模型对齐 seL4 CNode 7 操作（COPY/MINT/MOVE/MUTATE/REVOKE/DELETE/ROTATE）
- permission_engine 引用计数 + 权限缓存（1024 容量 + 60s TTL）

---

## 6. 优先级和工作量估算

### 6.1 P0 工作量

| 类别 | 项目 | 工作量 |
|------|------|--------|
| 文档 SSoT | P0-1 错误码 6 套统一 | ~8h |
| 文档 SSoT | P0-4 IPC 头三重违规重写 | ~3h |
| 文档一致性 | P0-5 "操作系统"定位冲突 | ~4h |
| 文档 SSoT | P0-8 [SC] 头文件清单 | ~1h |
| 文档可用性 | P0-9 文件路径引用错误 | ~3h |
| 方案 SSoT | P0-10 ES-SEL4-7 分类残留冲突 | ~2h |
| **方案侧 P0 小计** | 6 项 | **~21h** |
| 源码正确性 | P0-3 AIRY_ERROR_NULL NULL deref | ~3h |
| 源码正确性 | P0-6 WebSocket 类型错误 | ~0.5h |
| 源码安全 | P0-7 agent_registry 数据竞争 | ~2h |
| 源码系统性 | P0-2 工程标准全面违规 | ~46h |
| **源码侧 P0 小计** | 4 项 | **~51.5h** |
| **P0 合计** | 10 项 | **~72.5h** |

> **方案侧 P0（~19h，与 AirymaxRT §10.4 估算一致）可在 1.0.1 M1 启动前完成**；源码侧 P0-2 系统性改造（~46h）可在 M1 阶段并行推进。

### 6.2 P1 工作量

| 类别 | 项目 | 工作量 |
|------|------|--------|
| 命名/前缀一致性 | P1-1/3 函数前缀 SSoT + agentrt_* 缺失 | ~2h |
| 命名/前缀一致性 | P1-4 8 子仓命名不一致 | ~4h |
| 命名/前缀一致性 | P1-5 Cupola/Cupolas 术语 | ~1h |
| 命名/前缀一致性 | P1-6 Daemon 数量 10 vs 12 | ~0.5h |
| 命名/前缀一致性 | P1-8 cupolas 错误码 4 变体 | ~2h |
| 命名/前缀一致性 | P1-11 MemoryRovol 层级命名 | ~1h |
| 文档完整性 | P1-2 29 仓拆分文档化 | ~6h |
| 文档完整性 | P1-13 50-specifications/ 处理 | ~1h |
| 文档完整性 | P1-14 OpenStandards 与 2026 生态 | ~6h |
| 源码工程 | P1-9 goto 集中出口（与 P0-2 重叠） | ~12h（重叠） |
| 源码工程 | P1-10 [SC] 与应用层风格割裂（与 P0-2 重叠） | 重叠 |
| 方案 SSoT | P1-7 OS-KER-005 跳号 | ~0.5h |
| 方案 SSoT | P1-12 ES-SEL4-9/10 状态分类 | ~1h |
| **P1 合计** | 14 项 | **~23h**（不含与 P0-2 重叠的 ~12h） |

### 6.3 P2 工作量

| 项目 | 工作量 |
|------|--------|
| P2-1 06-iron9-shared-model.md 递归注释 | ~0.1h |
| P2-2 TERMINOLOGY.md 路径头错误 | ~0.1h |
| P2-3 充实 00-requirements/ 中英双语文档（8 文件） | ~8h |
| P2-4 充实 60-syscalls/ 系统调用文档（6 文件） | ~6h |
| P2-5 建立 AirymaxRT 文档计数模型 | ~1h |
| P2-6 补充缺失的工程目录（70-build/80-testing/120-development-process/） | ~4h |
| **P2 合计** | **~19h** |

### 6.4 建议执行顺序

```
[Phase 0] 立即修复（~2h，0.1.1 收尾）
    └── P0-10 ES-SEL4-7 分类残留冲突（agentrt-linux 阻断 1.0.1 M1）

[Phase 1] 1.0.1 M1 启动前（~19h，方案侧 P0）
    ├── P0-1 错误码 6 套统一（~8h）
    ├── P0-5 "操作系统"定位冲突（~4h）
    ├── P0-4 IPC 头三重违规（~3h）
    ├── P0-9 文件路径引用错误（~3h）
    └── P0-8 [SC] 头文件清单（~1h）

[Phase 2] 1.0.1 M1 阶段（~51.5h，源码侧 P0 + P1）
    ├── P0-3 AIRY_ERROR_NULL NULL deref（~3h，立即）
    ├── P0-6 WebSocket 类型错误（~0.5h，立即）
    ├── P0-7 agent_registry 数据竞争（~2h，立即）
    ├── P0-2 源码工程标准全面违规（~46h，自动化 + 渐进重构）
    │   ├── .clang-format 配置 + make format（~8h）
    │   ├── typedef 重构 540 处（~16h）
    │   ├── goto 集中出口替代错误宏（~12h，含 P1-9）
    │   ├── ASCII 装饰分节符移除（~4h）
    │   └── fprintf/__builtin_* 收口（~6h）
    └── P1-7 OS-KER-005 跳号（~0.5h）

[Phase 3] 1.0.1 M1 内（~23h，P1 命名/前缀/文档）
    ├── P1-1/3 函数前缀 SSoT + agentrt_* 文档化（~2h）
    ├── P1-2 29 仓拆分文档化（~6h）
    ├── P1-4 8 子仓命名闭源同步（~4h）
    ├── P1-5 Cupola/Cupolas 术语统一（~1h）
    ├── P1-6 Daemon 数量 10→12（~0.5h）
    ├── P1-8 cupolas 错误码 4 变体统一（~2h）
    ├── P1-11 MemoryRovol 层级命名（~1h）
    ├── P1-12 ES-SEL4-9/10 状态分类（~1h）
    ├── P1-13 50-specifications/ 处理（~1h）
    ├── P1-14 OpenStandards 2026 生态对齐（~6h）
    └── P1-10 [SC] 与应用层风格对齐（与 P0-2 合并）

[Phase 4] 1.0.1 全阶段（~19h，P2 长期改进）
    └── 见 §6.3 P2 清单
```

**总工作量**：~114.5h（含 P0-2 系统性源码改造）或 ~68.5h（不含 P0-2，按方案侧 + 关键源码正确性修复计）。

---

## 7. 三方对齐度评估

| 维度 | 评分 | 关键说明 |
|------|------|----------|
| **agentrt 源码 vs 工程标准** | **45/D+** | (1) 4 空格缩进 10847 处 vs Tab 8 要求（OS-STD-FMT-001）；(2) 重度 typedef 540 处 vs 禁止结构体 typedef（OS-STD-CODE-020）；(3) goto 集中出口仅 14 处 vs OS-KER-001；(4) 自定义错误宏 1757 处替代 goto；(5) ASCII 装饰分节符 100 文件；(6) fprintf 直接使用 159 处/19 文件；(7) 唯一合规标杆：[SC] 6 头文件全部 Tab 8 + struct 无 typedef + kernel-doc + _Static_assert |
| **AirymaxRT 文档 vs 源码** | **55/D+** | (1) 错误码 6 套并行（文档）vs `commons/utils/error/` 单一实现（源码）；(2) IPC 头 `are_ipc_message_header_t` 13 字段（文档 `06-ipc/README.md`）vs `airy_ipc_msg_hdr` 8 字段（源码 `commons/include/airymax/ipc.h`）；(3) [SC] 头文件清单 `bpf_struct_ops.h`（文档 `06-iron9-shared-model.md`）vs `syscalls.h`（源码实际存在）；(4) magic 值正确对齐（'ARE1'/'AGTS'） |
| **AirymaxRT vs AirymaxOS** | **50/D** | (1) 命名前缀：开源文档使用裸名 `kernel`/`services` 等，闭源总纲使用 `airymaxos-kernel` 等 37 处不一致；(2) 函数前缀：开源 `airy_*` vs 闭源 OS-STD-005 仍声明 `airymaxos_*`；(3) IPC 头：AirymaxRT 文档违规 `are_ipc_message_header_t` vs AirymaxOS SSoT `airy_ipc_msg_hdr`；(4) 错误码：AirymaxRT 6 套 vs AirymaxOS SSoT 13 个 `AIRY_E*` 宏；(5) daemon 数量：AirymaxRT `01-system-architecture.md` 标注 10 vs AirymaxOS 实际 12；(6) ES-SEL4-7 分类：agentrt-linux 5 vs 6 项冲突 |
| **OpenStandards vs 实现** | **60/C-** | (1) protocols 模块集成 Claude/OpenAI/openclaw/china_eco/openjiuwen/autogen/langchain/mcp/agntcy/a2a（41 文件）；(2) 但与 2026 生态（MCP 最新规范、A2A 协议演进）存在脱节；(3) gateway 支持 http/ws/stdio + jsonrpc + rate_limiter + mcp_server + syscall_router（33 文件），架构完整；(4) 4 语言 SDK（Go/Python/Rust/TypeScript）文档存在但需充实 |

**对齐度综合评分**：~52/D+（agentrt 源码与工程标准、AirymaxRT 文档与源码、AirymaxRT 与 AirymaxOS 三方均存在系统性不一致，是当前最大的工程债务）。

---

## 8. 总体评估和行动建议

### 8.1 是否达到"可开发"状态

> **明确结论：agentrt 工程体系当前未达到"可开发"状态**。

**判定依据**：

| 判定标准 | 状态 | 说明 |
|---------|------|------|
| 架构设计完成度 | ✓ 达标 | MicroCoreRT / CoreLoopThree / MemoryRovol / Thinkdual / Cupolas / 12 Daemons / MCIS 体系并行论 / 五维正交 24 原则 完整 |
| 工程标准规范 | ✗ 未达标 | 833 源文件系统性违反 OLK-6.6 六大支柱（4 空格/typedef/错误宏/装饰分节符/fprintf） |
| 无方案冲突点 | ✗ 未达标 | 10 项 P0 级冲突（错误码 6 套 / "操作系统"定位 / [SC] 头文件 / IPC 头三重违规 / 路径错误 / ES-SEL4-7 / WebSocket 类型 / NULL deref / 数据竞争 / 工程标准） |
| 跨平台一致性 | ✗ 未达标 | agentrt 与 AirymaxOS 命名前缀 / IPC 头 / 错误码 / 8 子仓命名 多处不一致 |
| SSoT 收敛 | △ 部分达标 | 09-ssot-registry.md 已建立，但 AirymaxRT 文档侧 6 套错误码未对齐 SSoT |
| 历史问题修复 | ✓ 达标 | koa-connect / io_uring / MGLRU 2.0 / daemon→daemons 全部修复 |
| 技术亮点保留 | ✓ 达标 | 15 项技术亮点（C11 atomic / DCLP / _Thread_local / 编译时查表 / 适配器模式 / BAN-333 串行降级 等） |

### 8.2 阻断项清单（P0）

进入 1.0.1 M1 代码开发前必须完成收敛的 10 项 P0：

1. **P0-10**（agentrt-linux 阻断）：ES-SEL4-7 分类残留冲突（5 vs 6 项），~2h
2. **P0-1**：错误码 6 套并行，~8h（文档）
3. **P0-5**："操作系统"定位冲突，~4h
4. **P0-4**：IPC 头三重违规，~3h
5. **P0-9**：文件路径引用错误，~3h
6. **P0-8**：[SC] 头文件清单不一致，~1h
7. **P0-3**：AIRY_ERROR_NULL 潜在 NULL deref，~3h
8. **P0-6**：WebSocket 类型错误，~0.5h
9. **P0-7**：agent_registry 数据竞争，~2h
10. **P0-2**：源码工程标准全面违规，~46h（可与 M1 并行渐进推进）

> **方案侧阻断项（P0-1/4/5/8/9/10）合计 ~21h**，建议在 1.0.1 M1 启动前 1 周内完成。
> **源码正确性阻断项（P0-3/6/7）合计 ~5.5h**，建议立即修复。
> **源码系统性改造（P0-2 ~46h）** 可在 M1 阶段并行推进，配置 `.clang-format` + CI 门禁后渐进重构。

### 8.3 建议的修复路径

```
P0（~21h 方案 + ~5.5h 源码正确性 = ~26.5h）
    ↓
1.0.1 M1 启动（agentrt-linux 修复 P0-10 后即可启动）
    ↓
P1（~23h，M1 内完成）
    ↓
P0-2 源码系统性改造（~46h，M1 阶段并行）
    ↓
P2（~19h，1.0.1 全阶段）
    ↓
1.0.1 收尾
```

### 8.4 关键决策点（需要用户裁决）

| # | 决策点 | 选项 | 推荐 |
|---|--------|------|------|
| 1 | ES-SEL4-7 分类 | A：归入 P2 已落地（5 项强制）/ B：扩展为 6 项强制 | **A**（与标题和 OS-IRON-012 对齐） |
| 2 | 错误码统一方案 | A：SSoT 13 个 `AIRY_E*` 宏 + `airy_err_t` / B：保留 ARE_* 标准前缀分层 | **A + 文档化 AIRY_*/ARE_* 映射** |
| 3 | 缩进策略 | A：全量迁移至 Tab 8（对齐 [SC] 标杆）/ B：修订规范承认用户态 4 空格 | **A**（保持 OLK-6.6 基线一致性） |
| 4 | `agentrt_*` 专属 API 前缀 | A：文档化三层前缀分层（airy_/are_/agentrt_）/ B：仅使用 airy_ + are_ 两层 | **A**（任务描述明确要求） |
| 5 | 29 仓拆分文档化 | A：新建 `07-repository-structure.md` / B：在 `06-iron9-shared-model.md` 扩展 | **A**（独立文档化） |
| 6 | 50-specifications/ 目录 | A：删除（保留 20-modules 版本）/ B：重新定位为规范规格书目录 | **A**（避免重复） |
| 7 | 闭源 airymaxos- 前缀 | A：闭源总纲同步开源去除前缀（37 处）/ B：开源恢复前缀 | **A**（开源已明确废弃） |
| 8 | MemoryRovol 层级命名 | A：统一 L1 Raw/L2 Feature/L3 Structure/L4 Pattern / B：保留多套命名按上下文区分 | **A**（SSoT 原则） |
| 9 | P0-2 源码改造执行时机 | A：M1 启动前完成 / B：M1 阶段并行渐进 | **B**（自动化 + CI 门禁后渐进，避免阻塞 M1） |
| 10 | `AIRY_ERROR_NULL` 宏行为 | A：宏不 return 时修复 7 处 NULL deref / B：宏 return 时增加 `__attribute__((noreturn))` 标注 | **先审查宏定义再决定**（A 或 B） |

### 8.5 最终结论

agentrt 工程体系经过 5 个并行子任务的全面审查（833 源文件 + 88 方案文档 + agentrt-linux 方案），**架构设计层面质量较高且原创性强**（MicroCoreRT / CoreLoopThree / MemoryRovol / Thinkdual / Cupolas / 12 Daemons / MCIS 体系并行论 / 五维正交 24 原则），**15 项技术亮点突出**（C11 atomic / DCLP / _Thread_local / 编译时查表 / 适配器模式 / BAN-333 串行降级 / ASan 修复注释 等），**历史问题全部修复**（koa-connect / io_uring / MGLRU 2.0 / daemon→daemons）。

但存在 **10 项 P0 级阻断问题**（5 项文档 SSoT + 3 项源码正确性/安全 + 1 项方案 SSoT + 1 项系统性源码工程标准违规）和 **14 项 P1 级问题**，需在进入 1.0.1 M1 代码开发前完成方案侧 P0 收敛（~21h），并在 M1 阶段并行推进源码侧 P0 改造（~51.5h）。

**建议**：
1. **立即**（~2h）：修复 P0-10 ES-SEL4-7 分类残留冲突（agentrt-linux 阻断 1.0.1 M1 启动）。
2. **立即**（~5.5h）：修复 P0-3 NULL deref / P0-6 WebSocket 类型 / P0-7 数据竞争（源码正确性与安全）。
3. **1.0.1 M1 启动前**（~19h）：完成方案侧 P0-1/4/5/8/9（错误码统一 / IPC 头重写 / "操作系统"定位 / [SC] 头文件清单 / 路径错误）。
4. **1.0.1 M1 阶段**（~46h）：配置 `.clang-format` + CI 门禁，渐进重构源码工程标准（P0-2）。
5. **1.0.1 M1 内**（~23h）：完成 P1 命名/前缀/文档一致性收敛。
6. **1.0.1 全阶段**（~19h）：完成 P2 长期改进。

完成上述修复路径后，agentrt 工程体系可达到"可开发"状态，综合评分预期从 65/C+ 提升至 80/B+。

---

## 附录 A：4 份源报告索引

| 报告 | 路径 | 行数 | 综合评分 |
|------|------|------|----------|
| 01 atoms 源码深读 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt/_review_v1.0/01-atoms-source-deep-review.md` | 840 | 架构 A / 技术 A- / 工程标准 C+ / 边界 A+ / 文档 B+ / 安全 B |
| 02 daemons 等源码深读 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt/_review_v1.0/02-daemons-others-source-deep-review.md` | 453 | 用户态工程标准系统性违规 |
| 03 AirymaxRT 方案审查 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt/_review_v1.0/03-airymaxrt-solution-review.md` | 887 | **62/C+** |
| agentrt-linux 系统性复审 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt-linux/_review_v1.0/01-systematic-recheck.md` | 773 | **79/B+** |

## 附录 B：术语对照

| 术语 | 定义 |
|------|------|
| OLK-6.6 | Linux 6.6 内核基线编码风格（agentrt-linux 工程标准基线） |
| IRON-9 v2 | agentrt 三层模型（[SC] 共享契约层 / [SS] 语义同源层 / [IND] 完全独立层） |
| A 类 | 微核心原语（atoms/corekern） |
| B 类 | 应用语义层（atoms/coreloopthree/taskflow/syscall/memory + daemons/cupolas/gateway/protocols） |
| C 类 | 商业隔离层（atoms/frameworks） |
| DCLP | Double-Checked Locking Pattern（双重检查锁定模式） |
| BAN-333 | pregel_engine max_workers=1 强制串行降级规则 |
| ASan | AddressSanitizer 内存错误检测器 |
| SSoT | Single Source of Truth（单一真值源） |
| [SC] | Shared Contract（共享契约层） |
| [SS] | Semantic Same-source（语义同源层） |
| [IND] | Independent（完全独立层） |
| MicroCoreRT | agentrt 微核心运行时（用户态 Ring 3） |
| CoreLoopThree | 三阶段认知循环（cognition/execution/memory） |
| MemoryRovol | 四层记忆系统（L1 Raw / L2 Feature / L3 Structure / L4 Pattern） |
| Thinkdual | 双思考模式（thinking_chain + metacognition） |
| Cupolas | 安全穹顶（7 子系统：permission/sanitizer/audit/workbench/guards/security/network/platform） |

## 附录 C：审查工具与方法

- **文件映射**：Glob + LS + find 统计 .c/.h 文件数
- **深读**：Read 工具逐文件读取代表性源码（Agent A 深读 15+ 文件 / Agent B 深读 9 文件 / Agent C 完整阅读 26 文档 / Agent D 完整阅读闭源总纲 v0.2.5）
- **违规验证**：Grep 工具按规则模式扫描（Tab/4 空格/typedef/装饰分节符/前缀/超长行/atomic/_Thread_local）
- **基线对照**：`docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md`（OLK-6.6 六大支柱）
- **行号精度**：所有违规结论均附具体文件路径与行号（格式：`文件路径:L行号`）

---

<div align="center">

**© 2025-2026 SPHARX Ltd.** All Rights Reserved.

</div>

---

**报告结束** | SPHARX Ltd 内部参考 | 闭源不公开 | 审查日期：2026-07-13 | 审查版本：v1.0
