# agentrt 源代码深度审查报告 v1.0

> **审查范围**：`agentrt/daemons`、`agentrt/cupolas`、`agentrt/gateway`、`agentrt/commons`、`agentrt/protocols`
> **审查日期**：2026-07-13
> **审查依据**：`docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md`（含 Part I-IV）
> **审查方法**：Glob 结构映射 + 代表性源文件深读 + Grep 全局违规扫描
> **审查结论等级**：P0（阻断）/ P1（高优先级）/ P2（中优先级）

---

## 1. 各模块结构概览

### 1.1 文件统计

| 模块 | .c 文件 | .h 文件 | 合计 | 说明 |
|------|---------|---------|------|------|
| daemons | 157 | 86 | 243 | 含 market_d/sched_d/gateway_d/monit_d/plugin_d/tool_d/llm_d/channel_d/notify_d/hook_d/info_d/observe_d/common |
| cupolas | 55 | 40 | 95 | 含 permission/sanitizer/audit/workbench/guards/security/network/platform |
| gateway | 17 | 16 | 33 | 含 gateway(http/ws/stdio) + utils(jsonrpc/rate_limiter/mcp_server/syscall_router) |
| commons | 84 | 100 | 184 | 含 utils(memory/sync/io/string/logging/error/config/observability/token/cost/cache/ipc/sd/platform/...) + platform + include/airymax([SC]层) |
| protocols | 22 | 19 | 41 | 含 integrations(claude/openai/openclaw/china_eco/openjiuwen) + frameworks(autogen/langchain) + standards(mcp/agntcy/a2a) + core + common |
| **合计** | **335** | **261** | **596** | |

### 1.2 daemon 子模块清单（daemons/）

| daemon | 职责 | main.c 存在 | svc_adapter 模式 |
|--------|------|-------------|------------------|
| market_d | Agent 市场（注册表/技能/安装器/发布者） | 是 | 是（market_svc_adapter） |
| sched_d | 调度服务（round_robin/priority/weighted/ml_based） | 是 | 是（sched_svc_adapter） |
| gateway_d | 网关守护进程（MCP/A2A/OpenAI兼容/protocol_router） | 是 | 是（gateway_svc_adapter） |
| monit_d | 监控（metrics/tracing/alert/logging/prometheus） | 是 | 是（monit_svc_adapter） |
| plugin_d | 插件（发现/权限/服务） | 是 | - |
| tool_d | 工具执行（注册表/执行器/验证器/缓存/审批/沙箱桥接） | 是 | 是（tool_svc_adapter） |
| llm_d | LLM 路由（round_robin/least_latency/cost_aware/quality_first） + providers(openai/anthropic/google/deepseek/local) | 是 | 是（llm_svc_adapter） |
| channel_d | 通道服务 | 是 | - |
| notify_d | 通知服务 | 是 | - |
| hook_d | 钩子服务 | 是 | - |
| info_d | 信息查询 | 是 | - |
| observe_d | 观测服务 | 是 | - |
| common | daemon 公共库（IPC/事件驱动/安全/降级/平台扩展/线程池/...） | - | - |

**架构一致性**：所有核心 daemon 均采用统一架构模式 —— `DAEMON_DECLARE_COMMON` 宏样板 + `svc_adapter` 适配层 + `method_dispatcher` RPC 注册 + `daemon_event_driver` 事件驱动 + `daemon_cupolas_init` 安全穹顶初始化。daemon→daemons 改名已彻底完成（见 §5.4）。

### 1.3 [SC] 共享契约层（commons/include/airymax/）

6 个 [SC] 层头文件全部就位，且**正确使用 Tab 8 缩进**（与用户态 4 空格形成对比）：

| 文件 | 内容 | Tab 8 缩进 |
|------|------|-----------|
| `ipc.h` | IPC magic 0x41524531 'ARE1' + 128B 消息头 + SQE/CQE 操作码 | 是 |
| `sched.h` | 任务描述符 magic 0x41475453 'AGTS' + vtime 衰减 + 优先级 0-139 | 是 |
| `security_types.h` | POSIX capability 41 ID + LSM 钩子 ID + verdict 4 值 + cap_op(seL4 CNode) | 是 |
| `cognition_types.h` | CoreLoopThree 阶段 + Thinkdual 模式 + Token 能效 | 是 |
| `memory_types.h` | MemoryRovol L1-L4 + GFP 掩码 + PMEM 接口 | 是 |
| `syscalls.h` | 12 核心 syscall 编号 + 12 预留槽位 | 是 |

---

## 2. 代表性文件深读记录

### 2.1 daemons/sched_d/src/main.c（326 行）

**文件路径**：`/home/spharx/SpharxWorks/OpenAirymax/agentrt/daemons/sched_d/src/main.c`

| 行号 | 违规类型 | 规则 | 证据 |
|------|----------|------|------|
| 52-75 | 4 空格缩进 | OS-STD-FMT-001 | `static void handle_register_agent(...)` 函数体使用 4 空格而非 Tab 8 |
| 92-93 | 缩进不一致 | OS-STD-FMT-001 | `AIRY_STRNCPY_TERM(info.agent_id, aid, sizeof(info.agent_id));` 顶格无缩进，下一行 4 空格 |
| 96-97 | 缩进不一致 | OS-STD-FMT-001 | `AIRY_STRNCPY_TERM(...)` 顶格，`(info.agent_name)[...]` 4 空格 |
| 134-135, 139-140 | 同上 | OS-STD-FMT-001 | `AIRY_STRNCPY_TERM` 顶格无缩进 |
| 160-161 | 行宽 >80 列 | OS-STD-FMT-002 | `SVC_LOG_INFO("Task scheduled: %s -> Agent: %s (Confidence: %.2f)", task.task_id,` 超 80 列 |
| 214-325 | 无 goto 集中出口 | OS-KER-001 | `main()` 函数有 4 处 `return 1` 错误出口，每处重复 `airy_mtx_destroy`/`airy_sock_cleanup`/`destroy_service` 清理，未用 goto 集中出口 |
| 243-248 | 指定初始化器 | OS-STD-CODE-014 | 正确使用 `.strategy = SCHED_STRATEGY_ROUND_ROBIN` 指定初始化器（合规） |

**正面**：使用 `SVC_LOG_INFO`/`SVC_LOG_ERROR` 统一日志宏（非 fprintf）；使用 `AIRY_ERR_*` 错误码；`daemon_cupolas_init("sched_d")` 集成安全穹顶；`daemon_cleanup_standard` 标准清理链。

### 2.2 daemons/market_d/src/agent_registry_core.c（244 行）

**文件路径**：`/home/spharx/SpharxWorks/OpenAirymax/agentrt/daemons/market_d/src/agent_registry_core.c`

| 行号 | 违规类型 | 规则 | 证据 |
|------|----------|------|------|
| 全文 | 4 空格缩进 | OS-STD-FMT-001 | 所有函数体 4 空格缩进 |
| 87-88, 174-179, 183-185 | 顶格无缩进 | OS-STD-FMT-001 | `AIRY_STRNCPY_TERM(entry->id, reg->id, sizeof(entry->id));` 顶格 |
| 19-25 | 结构体无 typedef | OS-STD-CODE-020 | `struct agent_registry { ... };` 正确使用 struct（合规） |
| 29 | void* 强制转换 | OS-BAN-003 | `(agent_registry_t *)AIRY_CALLOC(1, sizeof(agent_registry_t))` —— 对 void* 返回值多余 cast |
| 86, 173 | `__builtin_memset` | 一致性 | 应使用 `AIRY_MEMSET` 平台宏 |
| 123-137 | 返回内部指针后解锁 | OS-SEC-019 | `agent_registry_core_get()` 在 `airy_mtx_unlock` 后返回 `&registry->entries[i]`，调用方在无锁状态下访问共享数据，存在数据竞争风险 |
| 194-208 | 同上 | OS-SEC-019 | `agent_registry_core_get_latest_version()` 同样返回内部指针后解锁 |
| 102-121 | 无 goto 集中出口 | OS-KER-001 | `agent_registry_core_remove()` 有提前 return，但单锁场景影响较小 |
| 183 | 行宽 >80 列 | OS-STD-FMT-002 | `AIRY_STRNCPY_TERM(registry->entries[i].latest_version, version->version, sizeof(registry->entries[i].latest_version));` 远超 80 列 |

### 2.3 cupolas/src/cupolas.c（467 行）

**文件路径**：`/home/spharx/SpharxWorks/OpenAirymax/agentrt/cupolas/src/cupolas.c`

| 行号 | 违规类型 | 规则 | 证据 |
|------|----------|------|------|
| 全文 | 4 空格缩进 | OS-STD-FMT-001 | 所有函数体 4 空格缩进 |
| 37-40 | 结构体 typedef | OS-STD-CODE-020 | `typedef struct { char permission_rules_path[...]; ... } cupolas_internal_config_t;` 禁止结构体 typedef |
| 65-74 | 匿名 struct + 指定初始化 | OS-STD-CODE-014 | `static struct { int initialized; ... } g_cupolas = {0};` 匿名 struct 合规（无 typedef） |
| 79, 163 | `CUPOLAS_OK` 大写 | OS-STD-CODE-031 | 枚举常量大写（合规） |
| 88, 121, 136, 157, 218, 223, 277, 296, 303, 341, 362, 369, 416, 430 | `cupolas_ERR_*` 小写 | OS-STD-CODE-031 | `cupolas_ERR_UNKNOWN`、`cupolas_ERR_OUT_OF_MEMORY`、`cupolas_ERR_INVALID_PARAM`、`cupolas_ERR_STATE_ERROR`、`cupolas_ERR_PERMISSION_DENIED`、`cupolas_ERROR_INVALID_ARG` —— 枚举常量混用大小写，违反 UPPER_SNAKE_CASE |
| 76-164 | 无 goto 集中出口 | OS-KER-001 | `cupolas_init()` 有 4 个错误出口，每个重复 `cupolas_mutex_unlock` + 逐个 destroy 已分配资源，未用 goto 集中出口，易遗漏 |
| 48-54 | `snprintf` 直接使用 | 一致性 | 可接受，但应考虑统一到平台宏 |
| 233-267, 314-351, 372-421 | 安全横切 | OS-SEC-021 | permission_check/sanitize_input/execute_command 均集成 guard_manager 安全卫士检查 —— 安全横切关注点实现良好 |

**cupolas 错误码命名混乱详证**：同一模块内存在 4 种命名变体：
- `CUPOLAS_OK`（大写，cupolas.c:79）
- `cupolas_ERR_UNKNOWN`（小写前缀，cupolas.c:88）
- `cupolas_ERROR_INVALID_ARG`（又一变体，cupolas.c:341）
- `cupolas_OK`（全小写，permission_engine.c:39, test_cupolas_core.c:65）

测试文件 `cupolas/tests/unit/test_error_code_consistency.c` 专门验证此问题，说明团队已知悉但未彻底修复。

### 2.4 cupolas/src/permission/permission_engine.c（深读前 120 行）

**文件路径**：`/home/spharx/SpharxWorks/OpenAirymax/agentrt/cupolas/src/permission/permission_engine.c`

| 行号 | 违规类型 | 规则 | 证据 |
|------|----------|------|------|
| 全文 | 4 空格缩进 | OS-STD-FMT-001 | 4 空格缩进 |
| 33 | void* 强制转换 | OS-BAN-003 | `(permission_engine_t *)cupolas_mem_alloc(sizeof(permission_engine_t))` |
| 37 | `__builtin_memset` | 一致性 | 应使用 `AIRY_MEMSET` 或 `cupolas_memset_s` |
| 39 | `cupolas_OK` 小写 | OS-STD-CODE-031 | `cupolas_rwlock_init(&engine->rwlock) != cupolas_OK` —— 小写枚举常量 |
| 30-73 | goto 缺失 | OS-KER-001 | `permission_engine_create()` 有 4 个错误出口逐个 destroy，未用 goto 集中出口 |
| 88-114 | 引用计数 | OS-KER-128 | 正确使用引用计数（`cupolas_atomic_sub32`），合规 |
| 8-13 | Doxygen 注释 | OS-STD-CODE-012 | 使用 `@file`/`@brief`/`@author` Doxygen 风格（用户态可接受，非内核态 kernel-doc） |

### 2.5 gateway/src/gateway/gateway_api.c（151 行）

**文件路径**：`/home/spharx/SpharxWorks/OpenAirymax/agentrt/gateway/src/gateway/gateway_api.c`

| 行号 | 违规类型 | 规则 | 证据 |
|------|----------|------|------|
| 全文 | 4 空格缩进 | OS-STD-FMT-001 | 4 空格缩进 |
| 36-41 | 匿名 struct | - | `static struct { uint64_t total_connections; ... } g_gateway_stats = {0, 0, 0, false};` 合规（无 typedef） |
| 59, 73, 84, 85, 114-148 | `AIRY_CHECK` 宏 | OS-KER-001 | 使用 `AIRY_CHECK(gw != NULL, AIRY_ERR_NULL_POINTER, ...)` 宏做参数校验并提前返回（可接受的早返回模式） |
| 100-107 | 静态缓冲区非线程安全 | OS-SEC-019 | `static char buf[256];` 在 `gateway_get_stats()` 中使用，多线程并发调用会数据竞争 |
| 102-103 | 字符串折断 | OS-STD-FMT-002 | `"...active_"` `"connections..."` 用户可见 JSON 字符串折断为两行 |
| 21-34 | 不透明句柄 typedef | OS-STD-CODE-020 | `gateway_t *` 返回类型 —— 若为不透明指针类型（(a)类）则允许；需确认头文件定义 |
| 89-98 | 可观测性 | E-2 | cJSON 路径输出 status/uptime/connections 指标，但未集成 trace_id/span_id |

**gateway 可观测性评估**：k8s deployment.yaml 配置了 prometheus `/metrics` 路径和 metrics 端口（`gateway/deploy/k8s/deployment.yaml:32,57,197`），部署层可观测性就位。但 `gateway_api.c` 代码层未集成 OpenTelemetry trace_id。

### 2.6 gateway/src/utils/jsonrpc.c（467 行）

**文件路径**：`/home/spharx/SpharxWorks/OpenAirymax/agentrt/gateway/src/utils/jsonrpc.c`

| 行号 | 违规类型 | 规则 | 证据 |
|------|----------|------|------|
| 全文 | 4 空格缩进 | OS-STD-FMT-001 | 4 空格缩进 |
| 43, 46, 50, 57 | 魔数错误码 | OS-STD-CODE-030 | `AIRY_ERROR(-2, "jsonrpc field is not a string")`、`AIRY_ERROR(-3, "jsonrpc version is not 2.0")` —— 裸魔数 -2/-3 作错误码 |
| 269 | 魔数错误码 | OS-STD-CODE-030 | `AIRY_ERROR(-3, "batch exceeds max size")` |
| 281 | 魔数返回值 | OS-STD-CODE-030 | `return has_invalid ? -4 : 0;` |
| 331-341 | switch 魔数 | OS-STD-CODE-030 | `case -3:` / `case -2:` 魔数分支 |
| 357 | 下划线前缀变量 | 命名约定 | `int _resp_parsed_ok = 0;` —— C 标准保留 `_` 开头标识符 |
| 289-401 | 函数过长 | OS-KER-015 | `jsonrpc_process_batch()` 约 110 行，超过一屏 24 行限制 |
| 全文 | 无 kernel-doc | OS-STD-CODE-012 | 公共函数 `jsonrpc_create_success_response` 等无 kernel-doc 注释 |

### 2.7 commons/utils/logging/src/logging.c（1024 行）

**文件路径**：`/home/spharx/SpharxWorks/OpenAirymax/agentrt/commons/utils/logging/src/logging.c`

| 行号 | 违规类型 | 规则 | 证据 |
|------|----------|------|------|
| 全文 | 4 空格缩进 | OS-STD-FMT-001 | 4 空格缩进 |
| 113-117 | 结构体 typedef | OS-STD-CODE-020 | `typedef struct { uint64_t hash_key; ... } throttle_bucket_t;` |
| 232-251 | 结构体 typedef | OS-STD-CODE-020 | `typedef struct { log_config_t manager; ... } logging_state_t;` |
| 234 | 成员命名不当 | OS-STD-CODE-001 | `log_config_t manager;` —— 成员名 `manager` 语义不清，应为 `config` |
| 203-204, 218-219 | `__builtin_fprintf` | 日志规范 | `__builtin_fprintf(stderr, "[THROTTLE] ...")` —— 标注 `BAN-70 EXEMPT` 但仍是 fprintf |
| 267-273 | CLOCK_REALTIME | 日志规范 | `clock_gettime(CLOCK_REALTIME, &ts)` —— 正确使用 CLOCK_REALTIME（合规） |
| 54-64 | ANSI 颜色 | 日志规范 | `ANSI_RED`/`ANSI_GREEN`/`ANSI_YELLOW` 等 —— 正确使用 ANSI 颜色编码（合规） |
| 700, 746 | `fwrite` 控制台输出 | 日志规范 | `fwrite(formatted_buffer, 1, formatted_len, stream)` —— 日志实现机制，可接受 |
| 816 | 行宽 >80 列 | OS-STD-FMT-002 | `AIRY_STRNCPY_TERM(g_logging_state.module_levels[...].pattern, module_pattern, sizeof(...));` 远超 80 列 |
| 930 | 行宽 >80 列 | OS-STD-FMT-002 | `__builtin_fprintf(stderr, "[LOGGING] Config reloaded from '%s' (%d changes applied)\n", config_path,` 超 80 列 |
| 868 | `fopen` 直接使用 | 一致性 | `FILE *fp = fopen(config_path, "r");` 无 BAN-70 EXEMPT 标注 |
| 231, 253, 261, 278, 287, 302, 307, 315 | 注释乱码 | OS-STD-CODE-010 | `日志系统全局状?`、`状?*/`、`默认配置初始?` 等 —— 中文注释尾部被截断为 `?` |
| 651-708 | `log_write` 实现 | 日志规范 | 统一日志入口 `log_write()` 存在，含级别过滤/节流/采样/trace_id/span_id（合规） |

### 2.8 protocols/common/src/protocols_impl.c（216 行）

**文件路径**：`/home/spharx/SpharxWorks/OpenAirymax/agentrt/protocols/common/src/protocols_impl.c`

| 行号 | 违规类型 | 规则 | 证据 |
|------|----------|------|------|
| 全文 | 4 空格缩进 | OS-STD-FMT-001 | 4 空格缩进 |
| 33-36 | 结构体 typedef | OS-STD-CODE-020 | `typedef struct protocol_manager_s { ... } protocol_manager_s;` —— typedef 到同名 `_s` 后缀，冗余且违反命名约定 |
| 40-41 | void* 强制转换 | OS-BAN-003 | `struct protocol_manager_s *mgr = AIRY_CALLOC(1, sizeof(struct protocol_manager_s)); return (protocol_manager_handle_t)mgr;` |
| 48, 62, 77, 94 | 不透明句柄 cast | OS-STD-CODE-020 | `(struct protocol_manager_s *)manager` 反复 cast 不透明句柄 |
| 12 | 全局错误串非线程安全 | OS-SEC-019 | `static char s_last_error[512] = {0};` —— 全局错误缓冲区，多线程竞争 |
| 117 | 逻辑错误 | 正确性 | `s_ws_adapter.type = PROTOCOL_HTTP;` —— WebSocket 适配器类型设为 PROTOCOL_HTTP，应为 PROTOCOL_WEBSOCKET |
| 全文 | 无 kernel-doc | OS-STD-CODE-012 | 公共函数无 kernel-doc |

### 2.9 commons/include/airymax/ipc.h（[SC] 共享契约层，81 行）

**文件路径**：`/home/spharx/SpharxWorks/OpenAirymax/agentrt/commons/include/airymax/ipc.h`

| 行号 | 合规项 | 规则 | 证据 |
|------|--------|------|------|
| 19, 26-30, 33-34, 37-49, 67-77 | Tab 8 缩进 | OS-STD-FMT-001 | 正确使用 Tab 8 缩进（合规） |
| 18 | IPC magic | - | `#define AIRY_IPC_MAGIC 0x41524531u` —— 'ARE1' magic 正确定义 |
| 67-77 | 结构体无 typedef | OS-STD-CODE-020 | `struct airy_ipc_msg_hdr { __u32 magic; ... } __attribute__((packed));` 正确使用 struct（合规） |
| 79-80 | _Static_assert | - | `_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128, ...)` 编译期断言（合规） |
| 51-66 | kernel-doc | OS-STD-CODE-012 | `struct airy_ipc_msg_hdr` 有完整 kernel-doc 注释（合规） |

**[SC] 层是全仓库的合规标杆**：ipc.h/sched.h/security_types.h 均严格遵循 Tab 8 + struct 无 typedef + kernel-doc + _Static_assert。

---

## 3. 工程标准违规统计表

### 3.1 全局违规扫描结果

| 规则 | 扫描方式 | 命中数 | 严重度 | 说明 |
|------|----------|--------|--------|------|
| OS-STD-FMT-001 Tab 8 缩进 | 深读 9 个文件 | 9/9 文件违规 | ERROR | 用户态全部使用 4 空格；仅 [SC] 层 6 个头文件合规 |
| OS-STD-CODE-020 禁止结构体 typedef | `grep "^\s*typedef struct \{"` | 40+ 处 | WARN | 集中在 protocols/、daemons/gateway_d/、commons/tests/、cupolas/、logging.c |
| OS-KER-001 goto 集中出口 | `grep "^out_free_\|^out_unlock:\|^fail_\|^cleanup:\|^done:"` | 14 处/全仓库 | ERROR | 绝大多数函数用早返回，多资源函数存在泄漏风险 |
| OS-STD-FMT-002 80 列行宽 | 深读发现 | 多处 | WARN | logging.c:816/930、agent_registry_core.c:183、sched_d main.c:160 等 |
| OS-STD-CODE-012 kernel-doc | 深读 9 个文件 | 多数缺失 | WARN | 用户态公共函数普遍缺失 kernel-doc；[SC] 层合规 |
| OS-STD-CODE-031 枚举 UPPER_SNAKE | Grep cupolas 错误码 | 4 种变体混用 | WARN | cupolas_OK/cupolas_ERR_*/CUPOLAS_OK/cupolas_ERROR_* |
| OS-STD-CODE-030 错误码约定 | 深读 jsonrpc.c | 6 处魔数 | WARN | -2/-3/-4 裸魔数错误码 |
| OS-BAN-003 sizeof(*p) + void* cast | 深读 | 多处 void* cast | WARN | agent_registry_core.c:29、permission_engine.c:33、protocols_impl.c:41 |
| fprintf 直接使用 | `grep "\bfprintf\s*\("` | 159 处/19 文件 | WARN | 含 test 文件（可接受）+ memory.c(22)/memory_debug.c(44)/logging_compat.c(19) 需审查 BAN-70 豁免 |
| __builtin_memset/memcpy/fprintf | `grep` | 563 处/100 文件 | 一致性 | 与 AIRY_MEMSET/AIRY_MEMCPY 宏混用，不统一 |

### 3.2 按模块违规分布

| 模块 | Tab8 违规 | typedef 违规 | goto 缺失 | kernel-doc 缺失 | 其他 |
|------|-----------|-------------|-----------|----------------|------|
| daemons | 是（全文 4 空格） | gateway_d 多处 | sched_d main.c | 是 | 缩进不一致（顶格 AIRY_STRNCPY_TERM） |
| cupolas | 是 | cupolas.c:37 | cupolas_init/permission_engine_create | 部分 Doxygen | 错误码 4 种命名变体 |
| gateway | 是 | - | - | 是 | 静态缓冲区非线程安全；JSON 字符串折断 |
| commons | 是 | logging.c:113/232 | - | 部分 | 注释乱码；fopen 无豁免标注 |
| protocols | 是 | protocols_impl.c:33 + 多个 adapter.h | - | 是 | 全局错误串非线程安全；WS 类型错误 |

---

## 4. 函数前缀分析

### 4.1 前缀扫描结果

| 前缀 | 出现次数 | 位置 | 评估 |
|------|----------|------|------|
| `agentrt_` | 2 | 仅 `cupolas/src/mainpage.dox`（文档） | 合规：源码中 0 残留，agentrt 作为平台名不作为函数前缀 |
| `agentos_` | 0 | - | 合规：无残留 |
| `airymaxos_` | 0 | - | 合规：无残留 |
| `airy_` | 大量 | 全仓库 | 合规：[SS] 语义同源层主前缀 |
| `cupolas_` | 大量 | cupolas/ 模块 | 合规：安全穹顶模块前缀 |
| `daemon_` | 大量 | daemons/common/ | 合规：daemon 框架函数前缀 |
| `gateway_`/`gw_` | 大量 | gateway/ | 合规：网关模块前缀 |
| `protocol_` | 大量 | protocols/ | 合规：协议层前缀 |
| `log_` | 大量 | commons/logging | 合规：日志系统前缀 |

**结论**：函数前缀边界清晰，`agentos_`/`airymaxos_` 历史残留为 0（合规）。`agentrt_` 仅在文档中出现，源码中统一使用 `airy_`（[SS]层）和模块专属前缀（`cupolas_`/`gateway_`/`daemon_`/`protocol_`/`log_`），符合 OS-STD-CODE-005 前缀隔离规范。

---

## 5. 历史问题修复验证

### 5.1 koa-connect wrapper 问题

| 检查项 | 结果 |
|--------|------|
| `grep "koa-connect\|koa connect"` 全仓库 | 0 匹配 |
| 结论 | **已修复**：无 koa-connect wrapper 残留，网关使用原生实现 |

### 5.2 io_uring 误用问题

| 检查项 | 结果 |
|--------|------|
| `grep "io_uring\|io-uring"` agentrt/ | 3 匹配，均为注释/文档 |
| 位置 | `commons/include/airymax/ipc.h:36,42`（SQE/CQE flags 注释）、`commons/include/airymax/syscalls.h:30`（数据面说明） |
| 结论 | **已修复**：io_uring 仅作为 IPC 数据面机制在 [SC] 契约层文档化引用，无误用 |

### 5.3 MGLRU 2.0 禁词

| 检查项 | 结果 |
|--------|------|
| `grep "MGLRU 2\.0\|MGLRU2\.0\|MGLRU 2"` 全仓库 | 0 匹配 |
| 结论 | **已修复**：禁词 "MGLRU 2.0" 已清除 |

### 5.4 daemon→daemons 改名

| 检查项 | 结果 |
|--------|------|
| `Glob "agentrt/daemon/**/*.c"` | 0 文件 |
| 目录名 | `agentrt/daemons/`（复数） |
| `svc_logger.h:8` 注释 | "迁移至 commons/utils/logging/include/svc_logger.h，消除 atoms→daemons 编译期反向依赖" —— 已使用 daemons |
| 结论 | **已彻底完成**：无 `daemon/` 单数目录残留，全部迁移至 `daemons/` |

---

## 6. 日志系统评估

### 6.1 统一日志系统架构

**核心实现**：`/home/spharx/SpharxWorks/OpenAirymax/agentrt/commons/utils/logging/src/logging.c`

| 评估项 | 状态 | 证据 |
|--------|------|------|
| 统一日志入口 | 合规 | `log_write()` (logging.c:651) + `log_write_va()` (logging.c:710) |
| CLOCK_REALTIME 时间戳 | 合规 | `clock_gettime(CLOCK_REALTIME, &ts)` (logging.c:271) |
| ANSI 颜色编码 | 合规 | `ANSI_RED`/`ANSI_GREEN`/`ANSI_YELLOW`/`ANSI_BLUE`/`ANSI_MAGENTA` (logging.c:54-64) |
| 级别过滤 | 合规 | `should_log()` (logging.c:384) + 模块级通配符过滤 |
| 日志节流 | 合规 | `throttle_should_suppress()` (logging.c:168) + FNV 哈希去重 |
| 日志采样 | 合规 | `log_should_sample()` (logging.c:958) + 原子计数器 |
| trace_id/span_id | 合规 | TLS 存储 `g_tls_trace_id`/`g_tls_span_id` (logging.c:38-39) |
| 文件输出 + 轮转 | 合规 | `log_file_write()` + `log_file_rotate_if_needed()` (logging.c:441) |
| 热重载 | 合规 | `log_reload_config()` (logging.c:862) |

### 6.2 fprintf 直接使用评估

| 文件 | fprintf 次数 | BAN-70 豁免 | 评估 |
|------|-------------|-------------|------|
| logging.c | `__builtin_fprintf` 3 处 | 是（标注 `BAN-70 EXEMPT`） | 可接受：日志模块诊断通知 |
| logging_compat.c | 19 处 | 需核查 | 需确认是否为兼容层包装 |
| memory.c | 22 处 | 需核查 | 需确认是否为内存调试输出 |
| memory_debug.c | 44 处 | 需核查 | 调试模块，可能合理 |
| service_logging.c | 1 处 | 需核查 | 需确认 |
| heapstore_migration.c | 5 处 | 需核查 | 需确认 |
| test 文件（11 个） | 共 61 处 | N/A | 测试代码可接受 |

**结论**：统一日志系统 `log_write` 架构完整，正确使用 CLOCK_REALTIME + ANSI 颜色。但 `__builtin_fprintf`/`fprintf` 在非日志模块（memory.c/memory_debug.c/heapstore_migration.c）仍有直接使用，部分未标注 BAN-70 EXEMPT，需统一收口到 `log_write` 或显式标注豁免。

### 6.3 SVC_LOG 宏层

daemons 模块通过 `SVC_LOG_INFO`/`SVC_LOG_ERROR` 宏（定义于 `commons/utils/logging/include/svc_logger.h`）统一调用 `log_write`，未直接使用 fprintf —— 合规。

---

## 7. 安全横切评估

### 7.1 capability 模型实现

| 评估项 | 状态 | 证据 |
|--------|------|------|
| [SC] 契约层定义 | 合规 | `security_types.h` 定义 `AIRY_CAP_AGENT_SPAWN=41`/`AIRY_CAP_GPU_SCHED=42`/`AIRY_CAP_NPU_ACCESS=43` + `enum airy_cap_op`（seL4 CNode 模型：COPY/MINT/MOVE/MUTATE/REVOKE/DELETE/ROTATE） |
| LSM 钩子 ID | 合规 | `security_types.h:28-29` 定义 `AIRY_LSM_HOOK_TASK_CREATE=0`/`AIRY_LSM_HOOK_IPC_SEND=1`（252 总数，子集） |
| verdict 4 值 | 合规 | `enum airy_verdict { ALLOW/DENY/AUDIT/ASK }` (security_types.h:32-37) |
| 用户态 capability 检查 | 合规 | `cupolas_entitlements_check_capability()` (cupolas_entitlements.c:660) |
| 用户态 LSM 实现 | N/A | cupolas（用户态）不实现 LSM 钩子 —— LSM 是内核态概念，由 agent-linux 实现，架构正确 |

### 7.2 安全横切关注点贯穿

| 数据流阶段 | 安全检查 | 证据 |
|-----------|----------|------|
| daemon 启动 | `daemon_cupolas_init("sched_d")` 初始化 permission_engine + sanitizer + audit_logger | sched_d/main.c:238 |
| RPC 方法注册 | method_dispatcher 注册前无显式权限检查 | sched_d/main.c:300-303（潜在缺口） |
| 请求处理 | `cupolas_check_permission()` + `cupolas_sanitize_input()` | cupolas.c:213/292 |
| 命令执行 | `cupolas_execute_command()` + guard_manager 检查 | cupolas.c:356 |
| Agent 注册 | 参数校验 + `AIRY_STRNCPY_TERM` 安全拷贝 | sched_d/main.c:85-93 |
| 工具执行 | `safety_guard_bridge` + `tool_approval` | tool_d/include/safety_guard_bridge.h, tool_approval.h |
| 审计日志 | `audit_logger_log()` 记录 permission/sanitizer/workbench 事件 | cupolas.c:229/309/451 |

**安全横切评估**：cupolas 安全穹顶作为横切关注点贯穿 daemon 启动→请求处理→命令执行→审计记录全链路。guard_manager 安全卫士在 permission_check/sanitize_input/execute_command 三个关键点做风险等级评估（MEDIUM/HIGH/CRITICAL）并执行 BLOCK/ISOLATE/TERMINATE 动作。

### 7.3 最小权限原则

| 评估项 | 状态 | 证据 |
|--------|------|------|
| capability 令牌模型 | 合规 | seL4 CNode 模型（COPY/MINT/MOVE/REVOKE），capability 不可伪造 |
| permission_engine 规则优先级 | 合规 | `permission_engine_add_rule(agent_id, action, resource, allow, priority)` 支持优先级 |
| 权限缓存 | 合规 | `cache_manager_create(1024, 60000)` —— 1024 容量 + 60s TTL |
| 引用计数 | 合规 | `permission_engine_ref()`/`permission_engine_destroy()` 原子引用计数 |
| 审计追踪 | 合规 | 所有权限裁决记录审计日志 |

### 7.4 安全风险点

| 风险 | 位置 | 严重度 | 说明 |
|------|------|--------|------|
| 返回内部指针后解锁 | agent_registry_core.c:123-137/194-208 | P1 | `agent_registry_core_get()` 返回 `&entries[i]` 后才 `airy_mtx_unlock`，调用方无锁访问共享数据 |
| 全局错误串非线程安全 | protocols_impl.c:12 | P2 | `static char s_last_error[512]` 多线程竞争 |
| 静态统计缓冲区非线程安全 | gateway_api.c:100 | P2 | `static char buf[256]` 在 `gateway_get_stats()` 中 |
| RPC 方法注册无权限校验 | sched_d/main.c:300-303 | P2 | method_dispatcher_register 未校验调用方权限 |

---

## 8. 改进建议

### P0（阻断级）

| 编号 | 问题 | 建议 | 影响范围 |
|------|------|------|----------|
| P0-1 | 用户态 C 代码全部使用 4 空格缩进，违反 OS-STD-FMT-001 | 全量迁移至 Tab 8 缩进（对齐 [SC] 层标杆）；建议配置 `.clang-format` + `make format-check` CI 门禁 | daemons/cupolas/gateway/commons/protocols 全部用户态 .c/.h |
| P0-2 | `typedef struct { ... } xxx_t;` 大量违规（40+ 处） | 全量改为 `struct xxx { ... };`，使用 `struct xxx` 引用；仅保留不透明句柄 typedef | protocols/、daemons/gateway_d/、cupolas.c:37、logging.c:113/232、protocols_impl.c:33 |
| P0-3 | `protocols_impl.c:117` WebSocket 适配器类型错误 | `s_ws_adapter.type = PROTOCOL_HTTP` 改为 `PROTOCOL_WEBSOCKET`（或正确枚举值） | protocols/common/src/protocols_impl.c:117 |
| P0-4 | `agent_registry_core_get()` 返回内部指针后解锁，数据竞争 | 改为拷贝到调用方缓冲区，或在锁内完成所有访问 | daemons/market_d/src/agent_registry_core.c:123-137, 194-208 |

### P1（高优先级）

| 编号 | 问题 | 建议 | 影响范围 |
|------|------|------|----------|
| P1-1 | goto 集中出口仅 14 处，多资源函数用早返回易泄漏 | 对 `cupolas_init()`/`permission_engine_create()`/`sched_d main()` 等多资源分配函数引入 goto 集中出口标签 | cupolas.c:76-164、permission_engine.c:30-73、sched_d/main.c:214-325 |
| P1-2 | cupolas 错误码 4 种命名变体混用 | 统一为 `CUPOLAS_OK`/`CUPOLAS_ERR_*` UPPER_SNAKE_CASE；消除 `cupolas_OK`/`cupolas_ERROR_*` | cupolas/ 全模块（参考 test_error_code_consistency.c 已知问题） |
| P1-3 | jsonrpc.c 使用 -2/-3/-4 魔数错误码 | 定义 `JSONRPC_ERR_INVALID_FIELD`/`JSONRPC_ERR_BAD_VERSION` 等命名常量 | gateway/src/utils/jsonrpc.c:43,46,269,281,331-341 |
| P1-4 | 公共函数普遍缺失 kernel-doc | 为 `gateway_*`/`jsonrpc_*`/`protocol_*`/`cupolas_*` 公共 API 补充 kernel-doc 注释 | gateway/、protocols/、cupolas/ |
| P1-5 | `__builtin_memset`/`__builtin_memcpy`/`__builtin_fprintf` 563 处与 `AIRY_MEMSET` 宏混用 | 统一到 `AIRY_MEMSET`/`AIRY_MEMCPY`/`AIRY_FPRINTF` 平台宏，或统一允许 `__builtin_*` 并更新规范 | 100 个文件 |
| P1-6 | 非 test 文件直接使用 fprintf 未标注 BAN-70 豁免 | memory.c(22)/memory_debug.c(44)/heapstore_migration.c(5)/logging_compat.c(19) 审查并标注豁免或改用 `log_write` | commons/utils/memory/、heapstore/、logging/ |
| P1-7 | logging.c 注释乱码（中文尾部 `?`） | 修复 `logging.c:231,253,261,278,287,302,307,315` 等行注释编码 | commons/utils/logging/src/logging.c |

### P2（中优先级）

| 编号 | 问题 | 建议 | 影响范围 |
|------|------|------|----------|
| P2-1 | 多处行宽超 80 列 | 折行对齐到开括号 | logging.c:816/930、agent_registry_core.c:183、sched_d/main.c:160 |
| P2-2 | void* 返回值多余 cast | 移除 `(type *)AIRY_CALLOC(...)` 的 cast | agent_registry_core.c:29、permission_engine.c:33、protocols_impl.c:41 |
| P2-3 | `jsonrpc_process_batch()` 约 110 行过长 | 拆分为 batch_validate/handle/build_response 等 helper | gateway/src/utils/jsonrpc.c:289-401 |
| P2-4 | `protocols_impl.c:12` 全局错误串非线程安全 | 改为线程局部存储或返回错误码 | protocols/common/src/protocols_impl.c:12 |
| P2-5 | `gateway_api.c:100` 静态缓冲区非线程安全 | 改为调用方传入缓冲区或动态分配 | gateway/src/gateway/gateway_api.c:100-107 |
| P2-6 | `gateway_api.c:102-103` JSON 字符串折断 | 合并为单行或使用 snprintf 拼接 | gateway/src/gateway/gateway_api.c:102-103 |
| P2-7 | `logging.c:234` 成员名 `manager` 语义不清 | 重命名为 `config` | commons/utils/logging/src/logging.c:234 |
| P2-8 | `jsonrpc.c:357` `_resp_parsed_ok` 下划线前缀 | 重命名为 `resp_parsed_ok` | gateway/src/utils/jsonrpc.c:357 |
| P2-9 | RPC 方法注册无权限校验 | 在 method_dispatcher_register 增加 capability 检查钩子 | daemons/sched_d/src/main.c:300-303 |
| P2-10 | gateway 代码层未集成 trace_id | 在 gateway_api.c 请求处理中注入 trace_id/span_id | gateway/src/gateway/gateway_api.c |

---

## 9. 审查总结

### 9.1 合规亮点

1. **[SC] 共享契约层是合规标杆**：`commons/include/airymax/` 下 6 个头文件严格遵循 Tab 8 + struct 无 typedef + kernel-doc + _Static_assert + IRON-9 v2 标注。
2. **IPC magic 'ARE1' (0x41524531) 和任务 magic 'AGTS' (0x41475453) 正确定义并收敛至 [SC] SSoT**，全仓库统一引用。
3. **历史问题全部修复**：koa-connect(0)、io_uring 误用(仅合法引用)、MGLRU 2.0(0)、daemon→daemons(彻底)。
4. **函数前缀零残留**：`agentos_`/`airymaxos_` 为 0，`agentrt_` 仅文档出现。
5. **统一日志系统架构完整**：log_write + CLOCK_REALTIME + ANSI 颜色 + 节流/采样/trace_id/轮转/热重载。
6. **安全横切贯穿全链路**：cupolas 在 daemon 启动→请求处理→命令执行→审计记录四阶段均集成，guard_manager 做风险分级。
7. **daemon 架构一致**：所有核心 daemon 统一使用 DAEMON_DECLARE_COMMON + svc_adapter + method_dispatcher + event_driver + cupolas_init 模式。

### 9.2 核心问题

1. **Tab 8 缩进是最大系统性违规**：用户态全部 4 空格，与 [SC] 层 Tab 8 形成割裂。需全量迁移或修订规范承认用户态 4 空格。
2. **typedef struct 泛滥**：40+ 处，集中在 protocols/ 和 daemons/gateway_d/。
3. **goto 集中出口严重不足**：仅 14 处，多资源分配函数存在泄漏风险。
4. **cupolas 错误码命名混乱**：4 种变体，已知技术债未消除。
5. **__builtin_* 与 AIRY_* 宏混用**：563 处不一致。

### 9.3 风险评估

| 风险类别 | 等级 | 说明 |
|----------|------|------|
| 安全（数据竞争） | 中 | agent_registry_core 返回内部指针后解锁；全局错误串/静态缓冲区非线程安全 |
| 正确性 | 高 | protocols_impl.c WebSocket 类型错误（P0-3） |
| 可维护性 | 中 | typedef 泛滥 + 错误码混乱 + __builtin_ 不一致 |
| 工程标准合规 | 低 | Tab 8 / goto / kernel-doc 系统性违规 |

---

**审查人**：工程审查专家（GLM-5.2 subagent）
**审查工具**：Glob / Grep / Read / Shell
**证据基准**：所有结论附文件绝对路径 + 行号，可通过 Grep/Read 复核
