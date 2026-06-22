/**
 * @file contract_A_C.h
 * @brief 团队A（核心引擎）↔ 团队C（基础设施）接口合约
 *
 * 本合约定义了团队A的C核心引擎向团队C的测试/CI/部署基础设施
 * 暴露的接口契约。团队C的所有集成测试、CI验证和部署脚本必须
 * 基于此合约编写，团队A必须保证合约中所有接口的ABI稳定性。
 *
 * @contract_version 1.0.0
 * @teams team-A, team-C
 * @owner team-A (接口定义方), team-C (接口消费方)
 * @frozen 2026-06-14
 *
 * 合约包含：
 *   1. Daemon 测试注入点（Testing Injection Points）
 *   2. Prometheus 指标命名规范与数据结构
 *   3. IPC Bus 测试 Hooks（消息注入/拦截/监控）
 *   4. 健康检查端点定义
 *   5. 错误码映射表（A 错误码 → C 测试断言期望）
 *   6. 时序约束（启动/就绪/心跳/超时）
 */

#ifndef CONTRACT_A_C_H
#define CONTRACT_A_C_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ================================================================
 * 合约版本号（semver: MAJOR.MINOR.PATCH → 0x00MAJORMINORPATCH）
 * ================================================================ */
#define CONTRACT_A_C_VERSION 0x00010000  /* v1.0.0 */

/* ================================================================
 * 第1节：Daemon 测试注入点
 *
 * 团队A 向 团队C 暴露的测试注入接口，用于集成测试中
 * 模拟故障、注入延迟、控制行为。
 *
 * 时序约束：
 *   - 所有 inject_* 函数仅在 AGENTOS_TEST_MODE 编译宏启用时可用
 *   - 生产构建中，这些函数必须编译为 no-op（返回 AGENTOS_ERR_NOT_SUPPORTED）
 *   - 注入操作必须在 daemon 启动后、首次请求前完成
 * ================================================================ */

/**
 * @brief 测试模式标识 —— 团队C 通过环境变量 AGENTOS_TEST_MODE=1 启用
 *
 * 团队A 承诺：当 AGENTOS_TEST_MODE=1 时，所有 *_test_* 注入点可用。
 * 团队C 承诺：仅在 CI 测试环境中设置此变量，生产环境绝不设置。
 */
#define AGENTOS_TEST_MODE_ENV "AGENTOS_TEST_MODE"

/* ── Orchestrator 测试注入 ── */

/**
 * @brief 注入 Orchestrator 管道执行延迟
 * @param delay_ms 每个管道步骤额外延迟（毫秒），0 表示清除注入
 * @contract 团队A 承诺：inject 后下一次 orchestrator_execute_pipeline() 生效
 */
void orch_test_inject_delay(uint32_t delay_ms);

/**
 * @brief 注入 Orchestrator 管道步骤失败
 * @param phase      目标阶段（ORCH_PHASE_*）
 * @param error_code 注入的错误码
 * @param fail_count 失败次数（0 = 清除注入，N = 连续失败 N 次后恢复）
 * @contract 团队A 承诺：第 fail_count 次调用对应 phase 时返回 error_code
 */
void orch_test_inject_phase_failure(int phase, int error_code, uint32_t fail_count);

/* ── Checkpoint 测试注入 ── */

/**
 * @brief 注入 Checkpoint 保存失败
 * @param fail_count 连续保存失败次数（0 = 清除注入）
 * @contract 团队A 承诺：agentos_checkpoint_save() 在 fail_count 次内返回 AGENTOS_ERR_IO
 */
void checkpoint_test_inject_save_failure(uint32_t fail_count);

/**
 * @brief 注入 Checkpoint 恢复失败
 * @param task_id     目标 task_id，NULL 表示所有 task
 * @param fail_count  连续恢复失败次数（0 = 清除注入）
 * @contract 团队A 承诺：agentos_checkpoint_restore() 在 fail_count 次内返回 AGENTOS_ERR_NOT_FOUND
 */
void checkpoint_test_inject_restore_failure(const char *task_id, uint32_t fail_count);

/* ── ServiceDiscovery 测试注入 ── */

/**
 * @brief 注入服务健康状态变更
 * @param service_name 服务名称
 * @param instance_id  实例 ID
 * @param healthy      目标健康状态
 * @contract 团队A 承诺：注入后下一次心跳周期触发 SD_EVENT_HEALTH_CHANGE 事件
 */
void sd_test_inject_health_change(const char *service_name, const char *instance_id, bool healthy);

/**
 * @brief 注入服务实例过期
 * @param service_name 服务名称
 * @param instance_id  实例 ID
 * @contract 团队A 承诺：注入后立即触发 SD_EVENT_EXPIRED，模拟心跳超时
 */
void sd_test_inject_expiration(const char *service_name, const char *instance_id);

/* ── SafetyGuard 测试注入 ── */

/**
 * @brief 注入 SafetyGuard 守卫决策覆盖
 * @param guard_type    守卫类型（SAFETY_GUARD_*）
 * @param forced_decision 强制决策（SAFETY_DECISION_*）
 * @contract 团队A 承诺：注入后该类型守卫始终返回 forced_decision
 *          团队C 承诺：测试结束后调用 safety_test_reset_injections()
 */
void safety_test_inject_guard_decision(int guard_type, int forced_decision);

/**
 * @brief 清除所有 SafetyGuard 测试注入
 */
void safety_test_reset_injections(void);

/* ================================================================
 * 第2节：Prometheus 指标命名规范
 *
 * 团队A 承诺：所有 daemon 暴露的 Prometheus 指标遵循以下命名规范。
 * 团队C 承诺：CI 中通过正则验证指标命名合规性。
 *
 * 命名格式: agentos_{subsystem}_{metric_name}_{unit}
 * 标签规范: 每个指标至少包含 daemon="<name>" 标签
 * ================================================================ */

/* ── 必需指标名称常量（团队C 在集成测试中验证这些指标存在）── */

/* Gauge: 各 daemon 常驻内存 (bytes) */
#define METRIC_MEMORY_RSS_BYTES       "agentos_memory_rss_bytes"

/* Gauge: 堆内存使用量 (bytes) */
#define METRIC_MEMORY_HEAP_BYTES      "agentos_memory_heap_bytes"

/* Gauge: 内存池使用率 (0.0~1.0) */
#define METRIC_MEMORY_POOL_UTIL       "agentos_memory_pool_utilization"

/* Counter: OOM 事件计数（标签: level=NORMAL|WARNING|DEGRADED|CRITICAL|FATAL） */
#define METRIC_OOM_EVENTS_TOTAL       "agentos_oom_events_total"

/* Counter: 累计分配字节数 */
#define METRIC_MEMORY_ALLOC_BYTES     "agentos_memory_alloc_bytes_total"

/* Counter: 累计释放字节数 */
#define METRIC_MEMORY_FREE_BYTES      "agentos_memory_free_bytes_total"

/* Gauge: 当前内存压力级别 (0~4) */
#define METRIC_MEMORY_PRESSURE_LEVEL  "agentos_memory_pressure_level"

/* Histogram: 认知阶段延迟 (ms) */
#define METRIC_COGNITION_LATENCY_MS   "agentos_cognition_latency_ms"

/* Histogram: LLM 请求延迟 (ms) */
#define METRIC_LLM_REQUEST_DURATION   "agentos_llm_request_duration_ms"

/* Counter: LLM 累计费用 (USD) */
#define METRIC_LLM_COST_USD_TOTAL     "agentos_llm_cost_usd_total"

/* Counter: 工具调用次数 */
#define METRIC_TOOL_CALL_TOTAL        "agentos_tool_call_total"

/* Counter: 记忆操作次数 */
#define METRIC_MEMORY_OPS_TOTAL       "agentos_memory_operations_total"

/* Gauge: 连接线健康状态 (0=down, 1=up) */
#define METRIC_CONNECTION_HEALTH      "agentos_connection_health"

/* Counter: daemon 重启次数 */
#define METRIC_DAEMON_RESTART_TOTAL   "agentos_daemon_restart_total"

/* Gauge: Error Budget 剩余百分比 */
#define METRIC_ERROR_BUDGET_REMAINING "agentos_error_budget_remaining"

/* ── 指标标签规范 ── */

/**
 * @brief 必需标签列表
 *
 * 团队A 承诺：所有指标至少包含以下标签中的 daemon。
 * 团队C 承诺：CI 中验证 /metrics 端点的每个指标都包含 daemon 标签。
 */
#define METRIC_REQUIRED_LABEL_DAEMON  "daemon"
#define METRIC_LABEL_AGENT_ID         "agent_id"
#define METRIC_LABEL_PROVIDER         "provider"
#define METRIC_LABEL_MODEL            "model"
#define METRIC_LABEL_TOOL_NAME        "tool_name"
#define METRIC_LABEL_STATUS           "status"
#define METRIC_LABEL_LAYER            "layer"
#define METRIC_LABEL_OPERATION        "operation"
#define METRIC_LABEL_HOOK_NAME        "hook_name"
#define METRIC_LABEL_EVENT            "event"
#define METRIC_LABEL_CONNECTION_ID    "connection_id"
#define METRIC_LABEL_ERROR_CATEGORY   "error_category"

/* ================================================================
 * 第3节：IPC Bus 测试 Hooks
 *
 * 团队A 向 团队C 暴露的 IPC Bus 测试接口，
 * 用于集成测试中注入消息、监控消息流、验证路由正确性。
 * ================================================================ */

/**
 * @brief IPC Bus 消息拦截回调类型
 * @param msg      被拦截的消息（只读，回调内不可修改或释放）
 * @param user_data 用户数据
 *
 * @contract 团队A 承诺：回调在 IPC Bus 消息分发前同步调用
 *          团队C 承诺：回调内不执行阻塞操作（> 10ms）
 */
typedef void (*ipc_test_intercept_cb_t)(const void *msg, void *user_data);

/**
 * @brief 注册 IPC Bus 消息拦截器（仅测试模式）
 * @param target_service 目标服务名，NULL 表示拦截所有
 * @param msg_type       消息类型过滤，0xFF 表示所有类型
 * @param callback       拦截回调
 * @param user_data      用户数据
 * @return 0 成功，非0失败
 *
 * @contract 团队A 承诺：拦截器在消息路由前调用，可观察但不可修改消息
 *          团队C 承诺：测试结束后调用 ipc_test_clear_interceptors()
 */
int ipc_test_register_interceptor(const char *target_service, uint8_t msg_type,
                                  ipc_test_intercept_cb_t callback, void *user_data);

/**
 * @brief 清除所有 IPC Bus 测试拦截器
 */
void ipc_test_clear_interceptors(void);

/**
 * @brief 获取 IPC Bus 消息队列深度
 * @param service_name 服务名
 * @return 当前队列消息数，-1 表示服务不存在
 *
 * @contract 团队A 承诺：此函数在测试和生产模式下均可用
 *          团队C 承诺：用于背压控制测试的队列深度断言
 */
int ipc_test_get_queue_depth(const char *service_name);

/**
 * @brief 获取 IPC Bus 累计统计
 * @param service_name   服务名
 * @param out_sent       累计发送消息数
 * @param out_received   累计接收消息数
 * @param out_dropped    累计丢弃消息数
 * @return 0 成功，非0失败
 */
int ipc_test_get_stats(const char *service_name, uint64_t *out_sent,
                       uint64_t *out_received, uint64_t *out_dropped);

/* ================================================================
 * 第4节：健康检查端点定义
 *
 * 团队A 承诺：每个 daemon 暴露以下 HTTP 端点。
 * 团队C 承诺：CI 中通过 docker-compose 健康检查验证这些端点。
 * ================================================================ */

/**
 * @brief 健康检查端点路径常量
 *
 * 团队A 承诺：
 *   - GET /healthz → 200 OK (liveness: 进程存活)
 *   - GET /readyz  → 200 OK (readiness: 可接受请求)
 *   - GET /metrics → 200 OK (Prometheus 文本格式指标)
 *
 * 团队C 承诺：
 *   - docker-compose 中 healthcheck.test 使用 curl 验证 /healthz
 *   - CI 中验证 /metrics 输出包含 agentos_ 前缀指标
 */
#define HEALTH_ENDPOINT_LIVENESS  "/healthz"
#define HEALTH_ENDPOINT_READINESS "/readyz"
#define HEALTH_ENDPOINT_METRICS  "/metrics"

/* ================================================================
 * 第5节：错误码映射表
 *
 * 团队A 的 C 核心引擎错误码 → 团队C 测试断言期望映射。
 * 团队C 承诺：集成测试中仅使用此映射表中的错误码进行断言，
 *           不依赖未列出的错误码值。
 * 团队A 承诺：此映射表中的错误码值在 v1.x 生命周期内不变。
 *
 * 错误码分段规划（权威来源：commons/utils/error/include/error.h）：
 *   -1 ~ -99:      通用基础错误
 *   -100 ~ -199:   系统与平台错误
 *   -200 ~ -299:   内核层错误
 *   -300 ~ -399:   服务层错误
 *   -400 ~ -499:   LLM/AI 服务错误
 *   -500 ~ -599:   执行/工具错误
 *   -600 ~ -699:   记忆/存储错误
 *   -700 ~ -799:   安全/沙箱错误
 *   -800 ~ -899:   协调/规划错误
 * ================================================================ */

/* ── 通用基础错误 ── */
#define CONTRACT_ERR_OK                    0        /* 成功 */
#define CONTRACT_ERR_INVALID_PARAM         (-2)     /* 参数无效 */
#define CONTRACT_ERR_NULL_POINTER          (-3)     /* 空指针 */
#define CONTRACT_ERR_OUT_OF_MEMORY         (-4)     /* 内存不足 */
#define CONTRACT_ERR_BUFFER_TOO_SMALL      (-5)     /* 缓冲区过小 */
#define CONTRACT_ERR_NOT_FOUND             (-6)     /* 资源未找到 */
#define CONTRACT_ERR_ALREADY_EXISTS        (-7)     /* 资源已存在 */
#define CONTRACT_ERR_TIMEOUT               (-8)     /* 操作超时 */
#define CONTRACT_ERR_NOT_SUPPORTED         (-9)     /* 操作不支持 */
#define CONTRACT_ERR_PERMISSION_DENIED     (-10)    /* 权限不足 */
#define CONTRACT_ERR_IO                    (-11)    /* I/O 错误 */
#define CONTRACT_ERR_PARSE_ERROR           (-12)    /* 解析错误 */
#define CONTRACT_ERR_STATE_ERROR           (-13)    /* 状态错误 */
#define CONTRACT_ERR_CANCELED              (-16)    /* 操作已取消 */
#define CONTRACT_ERR_BUSY                  (-17)    /* 资源忙碌 */
#define CONTRACT_ERR_WOULD_BLOCK           (-18)    /* 非阻塞模式下需重试 */
#define CONTRACT_ERR_NOT_IMPLEMENTED       (-30)    /* 未实现 */
#define CONTRACT_ERR_FAIL                  (-31)    /* 通用失败 */

/* ── 系统与平台错误 ── */
#define CONTRACT_ERR_SYS_NOT_INIT          (-101)   /* 系统未初始化 */
#define CONTRACT_ERR_SYS_RESOURCE          (-102)   /* 系统资源不足 */
#define CONTRACT_ERR_SYS_DEADLOCK          (-103)   /* 死锁检测 */
#define CONTRACT_ERR_SYS_FILE              (-112)   /* 文件系统错误 */

/* ── 内核层错误 ── */
#define CONTRACT_ERR_KERN_IPC              (-201)   /* IPC 通信错误 */
#define CONTRACT_ERR_KERN_TASK             (-202)   /* 任务管理错误 */
#define CONTRACT_ERR_KERN_MEM              (-205)   /* 内核内存错误 */

/* ── 服务层错误 ── */
#define CONTRACT_ERR_SVC_NOT_READY         (-301)   /* 服务未就绪 */
#define CONTRACT_ERR_SVC_STOPPED           (-303)   /* 服务已停止 */
#define CONTRACT_ERR_SVC_CONFIG            (-304)   /* 配置错误 */
#define CONTRACT_ERR_SVC_HEALTH            (-306)   /* 健康检查失败 */

/* ── LLM/AI 服务错误 ── */
#define CONTRACT_ERR_LLM_NO_PROVIDER       (-401)   /* 无 LLM 提供商 */
#define CONTRACT_ERR_LLM_RATE_LIMIT        (-403)   /* LLM 速率限制 */
#define CONTRACT_ERR_LLM_AUTH_FAIL         (-406)   /* LLM 认证失败 */

/* ── 执行/工具错误 ── */
#define CONTRACT_ERR_EXEC_NOT_FOUND        (-501)   /* 工具未找到 */
#define CONTRACT_ERR_EXEC_TIMEOUT          (-503)   /* 执行超时 */
#define CONTRACT_ERR_EXEC_SANDBOX          (-505)   /* 沙箱违规 */

/* ── 记忆/存储错误 ── */
#define CONTRACT_ERR_MEM_WRITE             (-601)   /* 记忆写入失败 */
#define CONTRACT_ERR_MEM_READ              (-602)   /* 记忆读取失败 */
#define CONTRACT_ERR_MEM_FULL              (-605)   /* 记忆存储已满 */
#define CONTRACT_ERR_MEM_CORRUPT           (-606)   /* 记忆数据损坏 */

/* ── 安全/沙箱错误 ── */
#define CONTRACT_ERR_SEC_VIOLATION         (-701)   /* 安全违规 */
#define CONTRACT_ERR_SEC_SANITIZE          (-702)   /* 输入净化失败 */
#define CONTRACT_ERR_SEC_QUOTA             (-706)   /* 配额超限 */

/**
 * @brief 错误码 → 测试断言类别映射
 *
 * 团队C 在集成测试中使用此枚举对错误码分类断言，
 * 而非直接断言具体数值（数值可能随版本微调）。
 */
typedef enum {
    CONTRACT_ERR_CATEGORY_OK = 0,           /* 成功类（code == 0） */
    CONTRACT_ERR_CATEGORY_TRANSIENT,        /* 瞬态错误（可重试：TIMEOUT, BUSY, WOULD_BLOCK） */
    CONTRACT_ERR_CATEGORY_PERMANENT,        /* 永久错误（不可重试：INVALID_PARAM, NOT_FOUND） */
    CONTRACT_ERR_CATEGORY_RESOURCE,         /* 资源错误（OOM, FULL, QUOTA） */
    CONTRACT_ERR_CATEGORY_SECURITY,         /* 安全错误（VIOLATION, SANITIZE, PERMISSION） */
    CONTRACT_ERR_CATEGORY_INTERNAL          /* 内部错误（FAIL, STATE_ERROR, CORRUPT） */
} contract_err_category_t;

/**
 * @brief 将错误码映射为断言类别
 * @param code 团队A 返回的错误码
 * @return 断言类别
 *
 * @contract 团队C 承诺：测试断言使用此函数分类，而非硬编码数值比较
 */
static inline contract_err_category_t contract_err_category(int code) {
    if (code == 0) return CONTRACT_ERR_CATEGORY_OK;
    switch (code) {
    case -8:   case -17:  case -18:  case -403:
        return CONTRACT_ERR_CATEGORY_TRANSIENT;
    case -2:   case -3:   case -5:   case -6:   case -7:
    case -9:   case -10:  case -30:  case -501:
        return CONTRACT_ERR_CATEGORY_PERMANENT;
    case -4:   case -102:  case -605:  case -706:
        return CONTRACT_ERR_CATEGORY_RESOURCE;
    case -701:  case -702:  case -705:
        return CONTRACT_ERR_CATEGORY_SECURITY;
    default:
        return CONTRACT_ERR_CATEGORY_INTERNAL;
    }
}

/* ================================================================
 * 第6节：时序约束
 *
 * 定义团队A 各 daemon 的启动、就绪、心跳和超时时序约束。
 * 团队C 承诺：CI 中基于此时序约束编写超时断言和等待逻辑。
 * 团队A 承诺：daemon 行为符合此时序约束，否则视为 Bug。
 * ================================================================ */

/* ── 启动时序 ── */

/** Daemon 从 exec() 到 /healthz 200 OK 的最大时间（毫秒） */
#define CONTRACT_STARTUP_TIMEOUT_MS          30000   /* 30s */

/** Daemon 从 /healthz 200 到 /readyz 200 的最大时间（毫秒） */
#define CONTRACT_READINESS_TIMEOUT_MS        60000   /* 60s */

/** 所有 daemon 串行启动的总超时（毫秒） */
#define CONTRACT_FULL_STARTUP_TIMEOUT_MS     180000  /* 180s = 3min */

/* ── 心跳时序 ── */

/** Daemon 心跳间隔（毫秒） */
#define CONTRACT_HEARTBEAT_INTERVAL_MS       5000    /* 5s */

/** 心跳超时阈值（毫秒），超过此时间未收到心跳视为不健康 */
#define CONTRACT_HEARTBEAT_TIMEOUT_MS        15000   /* 15s = 3 * interval */

/** 服务发现注册超时（毫秒） */
#define CONTRACT_SD_REGISTER_TIMEOUT_MS      10000   /* 10s */

/* ── 请求超时 ── */

/** 单次 IPC 请求-响应超时（毫秒） */
#define CONTRACT_IPC_REQUEST_TIMEOUT_MS      5000    /* 5s */

/** LLM 请求超时（毫秒） */
#define CONTRACT_LLM_REQUEST_TIMEOUT_MS      120000  /* 120s */

/** 工具执行超时（毫秒） */
#define CONTRACT_TOOL_EXEC_TIMEOUT_MS        30000   /* 30s */

/** 记忆查询超时（毫秒） */
#define CONTRACT_MEMORY_QUERY_TIMEOUT_MS     10000   /* 10s */

/* ── 优雅关闭 ── */

/** SIGTERM 后优雅关闭的最大时间（毫秒），超时则 SIGKILL */
#define CONTRACT_GRACEFUL_SHUTDOWN_MS        10000   /* 10s */

/** Checkpoint 保存超时（毫秒） */
#define CONTRACT_CHECKPOINT_SAVE_TIMEOUT_MS  5000    /* 5s */

/* ── 背压与重试 ── */

/** IPC 队列最大深度（超过此值触发背压） */
#define CONTRACT_IPC_QUEUE_BACKPRESSURE      1024

/** IPC 队列满时丢弃阈值 */
#define CONTRACT_IPC_QUEUE_DROP_THRESHOLD    2048

/** 默认重试间隔基数（毫秒），实际间隔 = base * 2^attempt */
#define CONTRACT_RETRY_BACKOFF_BASE_MS       100

/** 最大重试次数 */
#define CONTRACT_RETRY_MAX_ATTEMPTS          3

/* ── Soak Test 分层时序 ── */

/** L1 PR 级 Soak Test 持续时间（秒） */
#define CONTRACT_SOAK_L1_DURATION_SEC        (4 * 3600)   /* 4h */

/** L2 周级 Soak Test 持续时间（秒） */
#define CONTRACT_SOAK_L2_DURATION_SEC        (24 * 3600)  /* 24h */

/** L3 发布前 Soak Test 持续时间（秒） */
#define CONTRACT_SOAK_L3_DURATION_SEC        (72 * 3600)  /* 72h */

#ifdef __cplusplus
}
#endif

#endif /* CONTRACT_A_C_H */