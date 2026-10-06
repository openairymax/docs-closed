# Cupolas 子系统边界文档

> **版本**: v1.0.0 | **日期**: 2026-06-18 | **团队**: A（核心引擎）
> **代码路径**: `agentrt/cupolas/`

---

## 1. 职责边界

Cupolas 是 AgentRT 的安全穹顶模块，为所有 Agent 操作提供统一的安全防护层。它实现权限裁决、输入净化、审计日志、虚拟工位隔离、安全守卫链、代码签名验证、密钥保险库、网络安全和运行时保护等全方位安全能力。

**设计原则**：默认安全（Security by Default）、最小权限（Least Privilege）、纵深防御（Defense in Depth）、高性能（缓存 + 异步写入）。

### 核心职责

| 模块 | 职责 | 源文件/头文件 |
|------|------|--------|
| **权限裁决引擎** | 基于规则的访问控制（RBAC），支持 glob 资源匹配、规则优先级排序、缓存加速、动态规则加载/重载 | `src/permission/permission.c`, `permission.h` |
| **权限缓存** | 权限查询结果缓存，减少重复规则评估开销，命中率统计 | `src/permission/permission_cache.c`, `permission_cache.h` |
| **权限规则** | 规则数据结构定义与序列化，支持 allow/deny/priority | `src/permission/permission_rule.c`, `permission_rule.h` |
| **输入净化器** | 注入攻击防护（SQL/HTML/Shell/Path），白名单优先策略，自定义规则支持，安全级别分级 | `src/sanitizer/sanitizer_core.c`, `sanitizer.h` |
| **净化规则缓存** | 净化规则编译缓存，加速重复输入检查 | `src/sanitizer/sanitizer_cache.c`, `sanitizer_cache.h` |
| **净化规则引擎** | 规则加载/管理/编译，支持正则表达式匹配 | `src/sanitizer/sanitizer_rules.c`, `sanitizer_rules.h` |
| **审计日志** | 操作追踪与合规记录，异步队列写入，日志轮转（rotator），溢出保护（overflow） | `src/audit/audit_logger.c`, `audit.h` |
| **审计队列** | 异步审计条目缓冲队列，背压处理 | `src/audit/audit_queue.c`, `audit_queue.h` |
| **审计轮转器** | 日志文件按大小/时间轮转，自动清理过期日志 | `src/audit/audit_rotator.c`, `audit_rotator.h` |
| **审计溢出保护** | 审计缓冲区溢出时的安全降级策略 | `src/audit/audit_overflow.c`, `audit_overflow.h` |
| **虚拟工位** | 隔离执行环境，进程级别资源限制（CPU/内存/磁盘/网络），容器化隔离 | `src/workbench/workbench.c`, `workbench.h` |
| **工位容器** | 容器化隔离执行，命名空间隔离 | `src/workbench/workbench_container.c`, `workbench_container.h` |
| **工位限制** | 细粒度资源配额控制（CPU/内存/IO/网络） | `src/workbench/workbench_limits.c`, `workbench_limits.h` |
| **工位进程核心** | 进程创建/管理/信号处理/退出码收集 | `src/workbench/workbench_process_core.c`, `workbench_process.h` |
| **安全守卫框架** | 事件驱动守卫链执行，可组合守卫（规则/模型/行为/启发式），优先级调度，同步/异步检测 | `src/guards/guard_core.c`, `guard_core.h` |
| **守卫集成** | 守卫框架与现有 Cupolas 模块的非侵入式集成 | `src/guards/guard_integration.c`, `guard_integration.h` |
| **SafetyGuard（V2）** | 细粒度安全守卫框架，守卫链模式、策略协调器、动态策略更新、资源配额控制、紧急停止 | `include/safety_guard.h` |
| **动态策略引擎（V2）** | 运行时策略加载、版本管理、冲突检测与解决、策略热更新、合规性验证 | `include/dynamic_policy_engine.h` |
| **零信任集成（V2）** | 零信任架构集成，持续验证、最小权限、微分段 | `include/zero_trust_integration.h` |
| **代码签名验证** | 可执行代码签名校验、证书链验证、篡改检测 | `src/security/cupolas_signature.h` |
| **密钥保险库** | 安全凭证存储，加解密，密钥生命周期管理 | `src/security/cupolas_vault.h` |
| **权限声明** | 应用级权限声明与验证（entitlements） | `src/security/cupolas_entitlements.h` |
| **运行时保护** | seccomp/CFI 运行时安全策略 | `src/security/cupolas_runtime_protection.h` |
| **网络安全** | TLS 证书验证、DNS 安全、HTTP 安全头、网络过滤 | `src/security/network/` 各文件 |
| **熔断器** | 服务熔断模式（CLOSED→OPEN→HALF_OPEN），失败快速拒绝，自动恢复，熔断器注册表 | `src/circuit_breaker.c`, `circuit_breaker.h` |
| **错误处理** | 统一错误码定义（含模块级错误码），错误码转换函数，向后兼容别名 | `src/security/cupolas_error.c`, `cupolas_error.h` |
| **监控与指标** | 安全事件监控、性能指标收集、统计上报 | `src/cupolas_monitoring.c`, `src/cupolas_metrics.c` |
| **配置管理** | 安全策略配置解析（平台路径系统解析 permission_rules.yaml/审计目录） | `src/cupolas.c`（内部配置），`commons/platform/include/platform_paths.h` |
| **内存池/Slab** | Cupolas 内部高性能内存管理（独立于 corekern） | `src/mempool.c`, `src/slab.c` |

### 非职责（明确排除）

- 不负责 AI/LLM 推理逻辑（属于 CoreLoopThree）
- 不负责任务调度与执行（属于 CoreLoopThree 的 execution 引擎）
- 不负责底层内存分配框架（属于 corekern + commons/memory）
- 不负责网络协议处理（属于 gateway_d）
- 不负责工具调用具体实现（属于 tool_d）
- 不负责持久化存储（属于 HeapStore）
- 不负责 LLM 模型推理（属于 llm_d）
- 不负责 Prompt 模板管理（属于 CoreLoopThree 的 prompt_loader）

---

## 2. 公共接口

### 2.1 头文件清单

| 头文件 | 用途 | 公开 API 数量 |
|--------|------|:---:|
| `include/cupolas.h` | 模块主入口：初始化/清理、权限检查、输入净化、命令执行、审计刷新 | 9 |
| `include/safety_guard.h` | SafetyGuard V2 框架：守卫注册/注销、守卫链检查、策略管理、资源配额、审计追踪、紧急停止 | 20+（V2 API） |
| `include/dynamic_policy_engine.h` | 动态策略引擎：规则增删改、策略评估、冲突检测/解决、版本管理、合规验证 | 12+（V2 API） |
| `include/zero_trust_integration.h` | 零信任架构集成 | 5+（V2 API） |
| `src/guards/guard_core.h` | 守卫核心框架：守卫管理器创建/销毁、守卫注册/注销、同步/异步检测、规则更新、统计 | 18+ |
| `src/guards/guard_integration.h` | 守卫框架与 Cupolas 集成 | 5+ |
| `src/sanitizer/sanitizer.h` | 输入净化器：创建/销毁、净化/安全检查、HTML/SQL/Shell/Path 转义、规则管理 | 12 |
| `src/permission/permission.h` | 权限引擎：创建/销毁、权限检查、引用计数、规则增删、缓存管理、统计 | 10 |
| `src/permission/permission_engine.h` | 权限引擎内部结构 | — |
| `src/permission/permission_cache.h` | 权限缓存内部结构 | — |
| `src/permission/permission_rule.h` | 权限规则内部结构 | — |
| `src/audit/audit.h` | 审计日志：创建/销毁、事件记录、刷新、查询 | 8+ |
| `src/audit/audit_queue.h` | 审计队列内部结构 | — |
| `src/circuit_breaker.h` | 熔断器：创建/销毁、调用/状态查询、成功/失败记录、统计、注册表 | 18+ |
| `src/security/cupolas_error.h` | 统一错误码：5 类模块级错误码 + 双向转换函数 + 兼容别名 | 20+ |
| `src/security/cupolas_signature.h` | 代码签名验证 | 5+ |
| `src/security/cupolas_vault.h` | 密钥保险库 | 5+ |
| `src/security/cupolas_entitlements.h` | 权限声明验证 | 5+ |
| `src/security/cupolas_runtime_protection.h` | 运行时保护 | 5+ |
| `src/security/cupolas_network_security.h` | 网络安全入口 | — |
| `src/security/network/` | 网络过滤、TLS、DNS、HTTP 安全 | 12+ |
| `src/workbench/workbench.h` | 虚拟工位：创建/销毁、执行命令、资源限制、状态查询 | 10+ |
| `src/workbench/workbench_limits.h` | 工位资源限制 | 5+ |
| `src/workbench/workbench_container.h` | 工位容器化 | 5+ |
| `src/workbench/workbench_process.h` | 工位进程管理 | 5+ |
| `src/cupolas_metrics.h` | 安全指标收集 | 5+ |
| `src/cupolas_monitoring.h` | 安全事件监控 | 5+ |

### 2.2 关键 API 签名

```c
// ==================== 模块生命周期 ====================
int cupolas_init(const char *config_path, airy_err_t *error);
void cupolas_cleanup(void);
const char *cupolas_version(void);

// ==================== 权限管理 ====================
int cupolas_check_permission(const char *agent_id, const char *action,
                             const char *resource, const char *context);
int cupolas_add_permission_rule(const char *agent_id, const char *action,
                                const char *resource, int allow, int priority);
void cupolas_clear_permission_cache(void);

// ==================== 权限引擎（底层 API） ====================
permission_engine_t *permission_engine_create(const char *rules_path);
void permission_engine_destroy(permission_engine_t *engine);
permission_engine_t *permission_engine_ref(permission_engine_t *engine);
void permission_engine_unref(permission_engine_t *engine);
int permission_engine_check(permission_engine_t *engine, const char *agent_id,
                            const char *action, const char *resource, const char *context);
int permission_engine_reload(permission_engine_t *engine);
void permission_engine_clear_cache(permission_engine_t *engine);
int permission_engine_add_rule(permission_engine_t *engine, const char *agent_id,
                               const char *action, const char *resource, int allow, int priority);
size_t permission_engine_rule_count(permission_engine_t *engine);
void permission_engine_cache_stats(permission_engine_t *engine, uint64_t *hit_count,
                                   uint64_t *miss_count);

// ==================== 输入净化 ====================
int cupolas_sanitize_input(const char *input, char *output, size_t output_size);
sanitizer_t *sanitizer_create(const char *rules_path);
void sanitizer_destroy(sanitizer_t *sanitizer);
sanitize_result_t sanitizer_sanitize(sanitizer_t *sanitizer, const char *input,
                                     char *output, size_t output_size,
                                     const sanitize_context_t *ctx);
bool sanitizer_is_safe(sanitizer_t *sanitizer, const char *input,
                       const sanitize_context_t *ctx);
int sanitizer_escape_html(const char *input, char *output, size_t output_size);
int sanitizer_escape_sql(const char *input, char *output, size_t output_size);
int sanitizer_escape_shell(const char *input, char *output, size_t output_size);
int sanitizer_escape_path(const char *input, char *output, size_t output_size);
void sanitizer_default_context(sanitize_context_t *ctx);
int sanitizer_add_rule(sanitizer_t *sanitizer, const char *pattern,
                       const char *replacement);
void sanitizer_clear_rules(sanitizer_t *sanitizer);

// ==================== 命令执行（虚拟工位） ====================
int cupolas_execute_command(const char *command, char *const argv[], int *exit_code,
                            char *stdout_buf, size_t stdout_size, char *stderr_buf,
                            size_t stderr_size);

// ==================== 审计日志 ====================
void cupolas_flush_audit_log(void);

// ==================== 安全守卫框架 ====================
// 守卫管理器
guard_manager_t *guard_manager_create(const guard_manager_config_t *config);
void guard_manager_destroy(guard_manager_t *manager);
int guard_manager_register_guard(guard_manager_t *manager, guard_t *guard);
int guard_manager_unregister_guard(guard_manager_t *manager, guard_id_t guard_id);
guard_t *guard_manager_find_guard_by_name(guard_manager_t *manager, const char *name);
int guard_manager_check_sync(guard_manager_t *manager, const guard_context_t *context,
                             guard_result_t *results, size_t max_results,
                             size_t *actual_results);
uint64_t guard_manager_check_async(guard_manager_t *manager,
                                   const guard_context_t *context,
                                   void (*callback)(uint64_t request_id,
                                                    const guard_result_t *results,
                                                    size_t count, void *user_data),
                                   void *user_data);
int guard_manager_get_stats(guard_manager_t *manager, guard_stats_t *stats);

// 守卫实例
guard_t *guard_create(const char *name, const char *description, guard_type_t type,
                      const guard_ops_t *ops);
void guard_destroy(guard_t *guard);
int guard_init(guard_t *guard, const guard_config_t *config);
int guard_check(guard_t *guard, const guard_context_t *context, guard_result_t *result);
int guard_enable(guard_t *guard);
int guard_disable(guard_t *guard);
int guard_update_rules(guard_t *guard, const guard_rule_t *rules, size_t count);
int guard_get_stats(guard_t *guard, guard_stats_t *stats);

// ==================== SafetyGuard V2（可选，需定义 AIRY_ENABLE_V2_API） ====================
safety_guard_context_t *safety_guard_create(void);
void safety_guard_destroy(safety_guard_context_t *ctx);
int safety_guard_register_guard(safety_guard_context_t *ctx,
                                const safety_guard_descriptor_t *descriptor,
                                safety_guard_check_fn check_fn, void *user_data);
safety_decision_t safety_guard_check(safety_guard_context_t *ctx,
                                     const safety_event_t *event, safety_result_t *result);
safety_decision_t safety_guard_check_chain(safety_guard_context_t *ctx,
                                           const safety_event_t *event,
                                           safety_result_t **results, size_t *result_count);
int safety_guard_add_policy(safety_guard_context_t *ctx, const safety_policy_t *policy);
int safety_guard_remove_policy(safety_guard_context_t *ctx, const char *policy_id);
int safety_guard_update_policy(safety_guard_context_t *ctx, const char *policy_id,
                               const char *new_rules_json);
int safety_guard_load_policies(safety_guard_context_t *ctx, const char *policies_json);
int safety_guard_resolve_conflict(safety_guard_context_t *ctx, const char *policy_a_id,
                                  const char *policy_b_id, safety_decision_t *resolved);
int safety_guard_set_quota(safety_guard_context_t *ctx, const char *resource_id,
                           int64_t limit, uint64_t reset_interval_ms);
int safety_guard_check_quota(safety_guard_context_t *ctx, const char *resource_id,
                             int64_t requested, bool *allowed);
int safety_guard_consume_quota(safety_guard_context_t *ctx, const char *resource_id,
                               int64_t amount);
int safety_guard_emergency_stop(safety_guard_context_t *ctx, const char *reason);
int safety_guard_emergency_release(safety_guard_context_t *ctx);

// ==================== 熔断器 ====================
circuit_breaker_t *circuit_breaker_create(const circuit_breaker_config_t *config);
void circuit_breaker_destroy(circuit_breaker_t *breaker);
int circuit_breaker_call(circuit_breaker_t *breaker, int (*func)(void *arg),
                         void *arg, uint32_t timeout_ms);
bool circuit_breaker_is_available(circuit_breaker_t *breaker);
circuit_state_t circuit_breaker_get_state(circuit_breaker_t *breaker);
void circuit_breaker_record_success(circuit_breaker_t *breaker);
void circuit_breaker_record_failure(circuit_breaker_t *breaker);
void circuit_breaker_record_timeout(circuit_breaker_t *breaker);
void circuit_breaker_reset(circuit_breaker_t *breaker);
void circuit_breaker_get_stats(circuit_breaker_t *breaker, circuit_breaker_stats_t *stats);
circuit_breaker_registry_t *circuit_breaker_registry_create(void);
int circuit_breaker_registry_register(circuit_breaker_registry_t *registry,
                                      const char *name, circuit_breaker_t *breaker);
circuit_breaker_t *circuit_breaker_registry_get(circuit_breaker_registry_t *registry,
                                                const char *name);

// ==================== 错误处理 ====================
const char *cupolas_error_string(cupolas_error_t error);
cupolas_error_t cupolas_error_from_sig(cupolas_sig_error_t sig_error);
cupolas_error_t cupolas_error_from_ent(cupolas_ent_error_t ent_error);
cupolas_error_t cupolas_error_from_vault(cupolas_vault_error_t vault_error);
cupolas_error_t cupolas_error_from_net(cupolas_net_error_t net_error);
cupolas_error_t cupolas_error_from_runtime(cupolas_runtime_error_t runtime_error);
```

### 2.3 错误码

#### 统一错误码

| 错误码 | 值 | 含义 |
|--------|:---:|------|
| `cupolas_ERR_OK` | 0 | 成功 |
| `cupolas_ERR_UNKNOWN` | -1 | 未知错误 |
| `cupolas_ERR_INVALID_PARAM` | -2 | 无效参数 |
| `cupolas_ERR_NULL_POINTER` | -3 | 空指针 |
| `cupolas_ERR_OUT_OF_MEMORY` | -4 | 内存不足 |
| `cupolas_ERR_BUFFER_TOO_SMALL` | -5 | 缓冲区太小 |
| `cupolas_ERR_NOT_FOUND` | -6 | 未找到 |
| `cupolas_ERR_ALREADY_EXISTS` | -7 | 已存在 |
| `cupolas_ERR_TIMEOUT` | -8 | 超时 |
| `cupolas_ERR_NOT_SUPPORTED` | -9 | 不支持 |
| `cupolas_ERR_PERMISSION_DENIED` | -10 | 权限拒绝 |
| `cupolas_ERR_IO` | -11 | IO 错误 |
| `cupolas_ERR_STATE_ERROR` | -13 | 状态错误 |
| `cupolas_ERR_OVERFLOW` | -14 | 溢出 |
| `cupolas_ERR_TRY_AGAIN` | -15 | 请重试 |
| `cupolas_ERR_AUTH_FAILED` | -16 | 认证失败 |
| `cupolas_ERR_CERT_INVALID` | -17 | 证书无效 |
| `cupolas_ERR_CERT_EXPIRED` | -18 | 证书过期 |
| `cupolas_ERR_SIGNATURE_INVALID` | -19 | 签名无效 |
| `cupolas_ERR_TAMPERED` | -20 | 被篡改 |

#### 模块级错误码

| 模块 | 错误码前缀 | 示例 |
|------|-----------|------|
| 代码签名 | `cupolas_SIG_ERR_*` | INVALID, EXPIRED, REVOKED, UNTRUSTED, TAMPERED |
| 权限声明 | `cupolas_ENT_ERR_*` | INVALID, SIGNATURE_INVALID, EXPIRED, DENIED |
| 密钥保险库 | `cupolas_VAULT_ERR_*` | LOCKED, ACCESS_DENIED, CORRUPT, DECRYPT_FAILED |
| 网络安全 | `cupolas_NET_ERR_*` | CERT_INVALID, CERT_EXPIRED, HOST_MISMATCH, DENIED |
| 运行时保护 | `cupolas_RUNTIME_ERR_*` | VIOLATION, COMPROMISED, NOT_SUPPORTED |

#### 安全守卫决策类型

| 决策 | 含义 |
|------|------|
| `SAFETY_DECISION_ALLOW` | 允许操作 |
| `SAFETY_DECISION_DENY` | 拒绝操作 |
| `SAFETY_DECISION_CONDITIONAL` | 条件允许 |
| `SAFETY_DECISION_DEFER` | 延迟决策 |
| `SAFETY_DECISION_ABORT` | 中止操作 |

---

## 3. 依赖关系

### 3.1 内部依赖（编译时）

```
agentrt/cupolas/
  ├── agentrt/atoms/corekern/     — airy_rt.h, error.h, airy_err_t
  ├── agentrt/commons/            — airy_types.h, 基础类型定义
  │   ├── utils/error/            — error.h（统一错误码）
  │   └── utils/                  — 通用工具
  ├── 标准 C 库                   — stddef.h, stdint.h, stdbool.h, stdatomic.h
  └── POSIX 头文件                — pthread.h, unistd.h, sys/stat.h, signal.h
```

### 3.2 运行时依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| POSIX 线程 (libpthread) | 系统 | 审计日志异步写入、守卫并发检测 |
| 文件系统 | 系统 | 规则文件加载、审计日志持久化、保险库存储 |
| 系统时钟 | 系统 | 时间戳、超时检测、令牌桶重置 |
| OpenSSL / 加密库 | 系统 | 证书验证、签名校验、密钥加密 |
| 命名空间（Linux） | 系统 | 虚拟工位容器化隔离 |
| seccomp（Linux） | 系统 | 运行时系统调用过滤 |

### 3.3 被依赖方

| 消费者 | 使用接口 | 说明 |
|--------|---------|------|
| CoreLoopThree | `cupolas_check_permission`, `cupolas_sanitize_input`, `guard_manager_check_sync` | 认知循环中每步操作前进行安全检查 |
| gateway_d | `cupolas_sanitize_input`, `cupolas_check_permission` | 网关请求输入净化和权限校验 |
| llm_d | `cupolas_sanitize_input`, `cupolas_check_permission` | LLM 输入/输出内容过滤 |
| tool_d | `cupolas_execute_command`, `cupolas_check_permission` | 工具执行隔离和权限控制 |
| Orchestrator | `cupolas_check_permission`, `guard_manager_check_sync` | 编排流水线步骤安全校验 |
| 所有 daemon | `cupolas_flush_audit_log` | 审计日志同步刷新 |
| 测试框架 | 所有公开 API | 单元测试和集成测试 |

---

## 4. 配置参数

### 4.1 权限引擎配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `rules_path` | const char* | NULL | 规则文件路径（YAML 格式） |
| 缓存命中率阈值 | float | 0.85 | 低于此值触发缓存重建 |

### 4.2 净化器配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `rules_path` | const char* | NULL | 净化规则文件路径 |
| `max_length` | size_t | — | 输入最大长度限制 |
| `allow_html` | bool | false | 允许 HTML |
| `allow_sql` | bool | false | 允许 SQL |
| `allow_shell` | bool | false | 允许 Shell 命令 |
| `allow_path` | bool | false | 允许路径遍历 |

### 4.3 净化级别 (`sanitize_level_t`)

| 级别 | 说明 |
|------|------|
| `SANITIZE_LEVEL_NONE` | 不净化 |
| `SANITIZE_LEVEL_LOW` | 基础净化（特殊字符转义） |
| `SANITIZE_LEVEL_MEDIUM` | 中等净化（基础 + 模式匹配） |
| `SANITIZE_LEVEL_HIGH` | 严格净化（白名单模式） |
| `SANITIZE_LEVEL_MAX` | 最高净化（全部拒绝） |

### 4.4 守卫管理器配置 (`guard_manager_config_t`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `max_guards` | size_t | — | 最大守卫数量 |
| `max_pending_checks` | size_t | — | 最大待处理检测数 |
| `enable_priority_scheduling` | bool | — | 是否启用优先级调度 |
| `enable_result_caching` | bool | — | 是否启用结果缓存 |
| `cache_ttl_seconds` | size_t | — | 缓存 TTL（秒） |
| `default_timeout_ms` | uint32_t | — | 默认超时（ms） |

### 4.5 守卫配置 (`guard_config_t`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `guard_type` | enum | — | 守卫类型（规则/模型/行为/启发式/外部/复合/自定义） |
| `priority` | enum | — | 优先级（LOWEST→CRITICAL） |
| `max_rules` | size_t | — | 最大规则数 |
| `enable_logging` | bool | — | 是否启用日志 |
| `enable_metrics` | bool | — | 是否启用指标收集 |
| `cache_size` | size_t | — | 缓存大小 |
| `timeout_ms` | uint32_t | — | 检测超时（ms） |

### 4.6 熔断器配置 (`circuit_breaker_config_t`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `failure_threshold` | uint32_t | — | 失败阈值（触发 OPEN） |
| `success_threshold` | uint32_t | — | 成功阈值（触发 CLOSED 恢复） |
| `timeout_ms` | uint32_t | — | OPEN→HALF_OPEN 超时 |
| `half_open_max_calls` | uint32_t | — | HALF_OPEN 状态最大探测调用数 |
| `failure_rate_threshold` | double | — | 失败率阈值 |

### 4.7 SafetyGuard V2 常量

| 常量 | 值 | 说明 |
|------|:---:|------|
| `SAFETY_MAX_GUARDS` | 64 | 最大守卫数 |
| `SAFETY_MAX_POLICIES` | 128 | 最大策略数 |
| `SAFETY_MAX_RESOURCES` | 256 | 最大资源数 |
| `SAFETY_MAX_AUDIT_ENTRIES` | 10000 | 最大审计条目数 |

---

## 5. 跨团队接口合约

### 5.1 合约文件

- `contracts/contract_A_C_cupolas.h` — 团队A（Cupolas）与团队C（测试/质量）的接口合约

### 5.2 测试接口

| 函数 | 用途 | 消费者 |
|------|------|--------|
| `cupolas_version()` | 获取版本信息 | 测试 |
| `permission_engine_rule_count()` | 获取规则数量 | 测试 |
| `permission_engine_cache_stats()` | 获取缓存命中/未命中统计 | 测试/监控 |
| `permission_engine_clear_cache()` | 清除权限缓存 | 测试 |
| `permission_engine_reload()` | 重载规则文件 | 测试 |
| `sanitizer_default_context()` | 获取默认净化上下文 | 测试 |
| `sanitizer_is_safe()` | 检查输入是否安全 | 测试 |
| `sanitizer_clear_rules()` | 清除自定义规则 | 测试 |
| `guard_manager_get_stats()` | 获取守卫管理器统计 | 测试/监控 |
| `guard_manager_reset_stats()` | 重置守卫管理器统计 | 测试 |
| `guard_get_stats()` | 获取单个守卫统计 | 测试/监控 |
| `guard_reset_stats()` | 重置单个守卫统计 | 测试 |
| `guard_self_test()` | 守卫自检 | 测试 |
| `circuit_breaker_get_stats()` | 获取熔断器统计 | 测试/监控 |
| `circuit_breaker_get_state()` | 获取熔断器当前状态 | 测试/监控 |
| `circuit_breaker_reset_stats()` | 重置熔断器统计 | 测试 |
| `cupolas_error_string()` | 获取错误码描述字符串 | 测试 |
| `safety_guard_get_guard_count()` | 获取守卫数量（V2） | 测试 |
| `safety_guard_get_policy_count()` | 获取策略数量（V2） | 测试 |
| `safety_guard_get_audit_count()` | 获取审计条目数（V2） | 测试 |
| `safety_guard_query_audit()` | 查询审计记录（V2） | 测试/监控 |
| `dpolicy_engine_get_rule_count()` | 获取动态策略规则数（V2） | 测试 |
| `dpolicy_engine_get_version_count()` | 获取版本数（V2） | 测试 |

---

## 6. 文件所有权

```
@owner: team-A
```

所有 `agentrt/cupolas/` 下的文件归属于团队A。团队C 仅可修改 `tests/` 目录下的测试文件。

---

## 7. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0.0 | 2026-06-18 | 初始版本，基于 AgentRT v0.1.1 代码现状 |