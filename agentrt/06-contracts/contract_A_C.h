// SPDX-FileCopyrightText: 2026 SPHARX Ltd.
// SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0
/**
 * @file contract_A_C.h
 * @brief 跨团队接口合约：团队A（核心引擎 C）↔ 团队C（基础设施）
 *
 * 本合约固化团队A 与团队C 之间的三类基础设施约定：
 *   - daemon 测试注入点（团队C 测试团队A 的 daemon）
 *   - Prometheus metrics 命名规范（14 项必需指标）
 *   - IPC Bus 测试 hooks
 *
 * 团队C 在集成测试与生产监控中依赖本合约的稳定标识。
 * 任何指标名或注入点变更必须先升级本合约版本号。
 *
 * 参考实现：
 *   - agentrt/daemon/common/include/unified_metrics.h
 *   - agentrt/daemon/common/include/ipc_service_bus.h
 *   - agentrt/daemon/common/include/daemon_security.h
 *   - agentrt/daemon/common/include/svc_common.h
 *   - tests/integration/c/test_c_link_*.c
 *
 * @owner team-A, team-C
 * @version 1.0.0
 * @see P0.14 跨团队合约任务
 */

#ifndef AGENTRT_CONTRACT_A_C_H
#define AGENTRT_CONTRACT_A_C_H
#pragma once

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ================================================================
 * 合约版本
 * ================================================================ */

/** 团队A ↔ 团队C 合约版本（语义化版本） */
#define CONTRACT_A_C_VERSION "1.0.0"

/** 版本数值，用于运行时比较 */
#define CONTRACT_A_C_VERSION_MAJOR 1
#define CONTRACT_A_C_VERSION_MINOR 0
#define CONTRACT_A_C_VERSION_PATCH 0

/* ================================================================
 * Daemon 测试注入点
 *
 * 团队C 在集成测试中通过以下注入点控制团队A 的 daemon 行为。
 * 注入点通过环境变量启用，生产环境必须关闭。
 *
 * 时序约束：
 *   1. 团队C 设置 AIRY_TEST_MODE=1 启用注入
 *   2. daemon 启动时检测环境变量，注册测试钩子
 *   3. 测试用例通过 IPC 注入故障/延迟/断言
 *   4. 测试结束清理注入状态
 * ================================================================ */

/** 测试模式环境变量名 */
#define CONTRACT_AC_TEST_MODE_ENV "AIRY_TEST_MODE"

/** 测试模式启用值 */
#define CONTRACT_AC_TEST_MODE_ENABLED "1"

/** 测试模式禁用值（生产默认） */
#define CONTRACT_AC_TEST_MODE_DISABLED "0"

/** 测试注入点最大数量 */
#define CONTRACT_AC_MAX_INJECTION_POINTS 32

/** 测试注入点名称最大长度 */
#define CONTRACT_AC_INJECTION_NAME_MAX 64

/**
 * @brief 测试注入点类型
 *
 * 团队C 通过此枚举选择注入的故障类型。
 */
typedef enum contract_ac_injection_type {
    CONTRACT_AC_INJECT_FAULT      = 0, /**< 注入故障返回错误码 */
    CONTRACT_AC_INJECT_DELAY      = 1, /**< 注入延迟（毫秒） */
    CONTRACT_AC_INJECT_ASSERT     = 2, /**< 注入断言检查 */
    CONTRACT_AC_INJECT_OVERRIDE   = 3, /**< 覆盖返回值 */
    CONTRACT_AC_INJECT_DROP       = 4  /**< 丢弃请求（模拟超时） */
} contract_ac_injection_type_t;

/**
 * @brief 测试注入点描述
 *
 * 团队A 在 daemon 关键路径注册此结构，团队C 通过名称查找并激活。
 */
typedef struct contract_ac_injection_point {
    char name[CONTRACT_AC_INJECTION_NAME_MAX]; /**< 注入点名称（唯一） */
    contract_ac_injection_type_t type;         /**< 注入类型 */
    const char *daemon_name;                   /**< 所属 daemon（如 "llm_d"） */
    const char *description;                   /**< 注入点说明 */
    uint32_t    reserved;                      /**< 对齐保留 */
} contract_ac_injection_point_t;

/**
 * @brief 标准 daemon 测试注入点名称
 *
 * 团队A 必须在每个 daemon 中注册以下注入点（如适用）。
 * 团队C 的集成测试依赖这些名称。
 */
#define CONTRACT_AC_INJ_DAEMON_INIT     "daemon.init"      /**< daemon 初始化注入 */
#define CONTRACT_AC_INJ_DAEMON_SHUTDOWN "daemon.shutdown"  /**< daemon 关闭注入 */
#define CONTRACT_AC_INJ_IPC_REQUEST     "ipc.request"      /**< IPC 请求处理注入 */
#define CONTRACT_AC_INJ_IPC_RESPONSE    "ipc.response"     /**< IPC 响应处理注入 */
#define CONTRACT_AC_INJ_CONFIG_RELOAD   "config.reload"    /**< 配置重载注入 */
#define CONTRACT_AC_INJ_HEALTH_CHECK    "health.check"     /**< 健康检查注入 */

/* ================================================================
 * Prometheus Metrics 命名规范（14 项必需指标）
 *
 * 团队A 的所有 daemon 必须通过 unified_metrics.h 注册以下 14 项指标。
 * 团队C 的 Prometheus 采集配置（deploy/docker/monitoring/prometheus.yml）
 * 与 Grafana 仪表板依赖这些指标名。
 *
 * 命名规范：airy_<daemon>_<metric>_<unit>
 *   - 前缀统一为 airy_
 *   - daemon 名小写下划线
 *   - 单位后缀（seconds/bytes/total）
 * ================================================================ */

/** 指标前缀（所有指标必须以此开头） */
#define CONTRACT_AC_METRIC_PREFIX "airy_"

/** 指标名称最大长度（与 UM_METRIC_NAME_LEN 对齐） */
#define CONTRACT_AC_METRIC_NAME_MAX 128

/** 指标帮助文本最大长度 */
#define CONTRACT_AC_METRIC_HELP_MAX 256

/** 必需指标数量 */
#define CONTRACT_AC_REQUIRED_METRICS_COUNT 14

/**
 * @brief 14 项必需 Prometheus 指标名
 *
 * 团队A 的每个 daemon 必须注册这些指标（如适用）。
 * 团队C 的告警规则（alerts.yml）基于这些指标名编写。
 */
#define CONTRACT_AC_METRIC_REQUESTS_TOTAL       "airy_requests_total"        /**< 请求总数（Counter） */
#define CONTRACT_AC_METRIC_REQUEST_DURATION     "airy_request_duration_seconds" /**< 请求耗时（Histogram） */
#define CONTRACT_AC_METRIC_ERRORS_TOTAL         "airy_errors_total"          /**< 错误总数（Counter） */
#define CONTRACT_AC_METRIC_ACTIVE_CONNECTIONS   "airy_active_connections"    /**< 活跃连接数（Gauge） */
#define CONTRACT_AC_METRIC_MEMORY_USAGE_BYTES   "airy_memory_usage_bytes"    /**< 内存使用（Gauge） */
#define CONTRACT_AC_METRIC_CPU_USAGE            "airy_cpu_usage_ratio"       /**< CPU 使用率（Gauge） */
#define CONTRACT_AC_METRIC_UPTIME_SECONDS       "airy_uptime_seconds"        /**< 运行时长（Gauge） */
#define CONTRACT_AC_METRIC_QUEUE_DEPTH          "airy_queue_depth"           /**< 队列深度（Gauge） */
#define CONTRACT_AC_METRIC_IPC_LATENCY          "airy_ipc_latency_seconds"   /**< IPC 延迟（Histogram） */
#define CONTRACT_AC_METRIC_GC_PAUSE_SECONDS     "airy_gc_pause_seconds"      /**< GC 暂停（Histogram） */
#define CONTRACT_AC_METRIC_FILE_DESCRIPTORS     "airy_file_descriptors"      /**< 文件描述符数（Gauge） */
#define CONTRACT_AC_METRIC_GOROUTINE_COUNT      "airy_goroutine_count"       /**< 协程/线程数（Gauge） */
#define CONTRACT_AC_METRIC_CACHE_HIT_RATIO      "airy_cache_hit_ratio"       /**< 缓存命中率（Gauge） */
#define CONTRACT_AC_METRIC_CIRCUIT_BREAKER_STATE "airy_circuit_breaker_state" /**< 熔断器状态（Gauge） */

/**
 * @brief 指标类型枚举（与 um_metric_type_t 对齐）
 */
typedef enum contract_ac_metric_type {
    CONTRACT_AC_METRIC_COUNTER   = 0, /**< Counter：单调递增 */
    CONTRACT_AC_METRIC_GAUGE     = 1, /**< Gauge：可增可减 */
    CONTRACT_AC_METRIC_HISTOGRAM = 2, /**< Histogram：分布统计 */
    CONTRACT_AC_METRIC_SUMMARY   = 3  /**< Summary：分位数统计 */
} contract_ac_metric_type_t;

/**
 * @brief 指标描述符
 *
 * 团队A 通过 unified_metrics.h 注册指标时必须填写此结构。
 */
typedef struct contract_ac_metric_def {
    char name[CONTRACT_AC_METRIC_NAME_MAX];       /**< 指标名 */
    char help[CONTRACT_AC_METRIC_HELP_MAX];       /**< 帮助文本 */
    contract_ac_metric_type_t type;               /**< 指标类型 */
    char labels[256];                             /**< 标签（逗号分隔） */
} contract_ac_metric_def_t;

/* ================================================================
 * IPC Bus 测试 Hooks
 *
 * 团队C 通过以下 hooks 拦截 IPC Bus 消息，验证 daemon 间通信正确性。
 * Hooks 仅在测试模式下激活，生产环境编译期排除。
 *
 * 时序约束：
 *   1. 团队C 注册 hook 回调
 *   2. IPC Bus 收发消息时调用 hook
 *   3. hook 可修改消息（注入故障）或仅观察
 *   4. hook 返回 0 放行，非 0 阻断
 * ================================================================ */

/** IPC Bus 消息魔数（与 IPC_BUS_MESSAGE_MAGIC 对齐） */
#define CONTRACT_AC_IPC_BUS_MAGIC 0x49534200U

/** IPC Bus 消息版本（与 IPC_BUS_MESSAGE_VERSION 对齐） */
#define CONTRACT_AC_IPC_BUS_VERSION 1

/** IPC Bus 最大服务数（与 IPC_BUS_MAX_SERVICES 对齐） */
#define CONTRACT_AC_IPC_BUS_MAX_SERVICES 64

/** IPC Bus 最大通道数（与 IPC_BUS_MAX_CHANNELS 对齐） */
#define CONTRACT_AC_IPC_BUS_MAX_CHANNELS 32

/** IPC Bus 最大消息大小（与 IPC_BUS_MAX_MESSAGE_SIZE 对齐） */
#define CONTRACT_AC_IPC_BUS_MAX_MESSAGE_SIZE (512 * 1024)

/** IPC Bus 默认超时（毫秒，与 IPC_BUS_DEFAULT_TIMEOUT_MS 对齐） */
#define CONTRACT_AC_IPC_BUS_DEFAULT_TIMEOUT_MS 5000

/** IPC Bus 最大重试次数（与 IPC_BUS_MAX_RETRIES 对齐） */
#define CONTRACT_AC_IPC_BUS_MAX_RETRIES 3

/** IPC Bus 服务 ID 长度（与 IPC_BUS_SERVICE_ID_LEN 对齐） */
#define CONTRACT_AC_IPC_BUS_SERVICE_ID_LEN 64

/**
 * @brief IPC Bus 消息类型（与 ipc_bus_msg_type_t 对齐）
 */
typedef enum contract_ac_ipc_msg_type {
    CONTRACT_AC_IPC_MSG_REQUEST      = 0, /**< 请求 */
    CONTRACT_AC_IPC_MSG_RESPONSE     = 1, /**< 响应 */
    CONTRACT_AC_IPC_MSG_NOTIFICATION = 2, /**< 通知 */
    CONTRACT_AC_IPC_MSG_BROADCAST    = 3, /**< 广播 */
    CONTRACT_AC_IPC_MSG_HEARTBEAT    = 4, /**< 心跳 */
    CONTRACT_AC_IPC_MSG_DISCOVERY    = 5, /**< 发现 */
    CONTRACT_AC_IPC_MSG_CONTROL      = 6  /**< 控制 */
} contract_ac_ipc_msg_type_t;

/**
 * @brief IPC Bus 消息头（与 ipc_bus_message_header_t 对齐）
 *
 * 团队C 的测试 hook 通过此头识别消息来源与目标。
 */
typedef struct contract_ac_ipc_msg_header {
    uint32_t magic;                          /**< 魔数 CONTRACT_AC_IPC_BUS_MAGIC */
    uint32_t version;                        /**< 版本 CONTRACT_AC_IPC_BUS_VERSION */
    contract_ac_ipc_msg_type_t msg_type;     /**< 消息类型 */
    uint32_t protocol;                       /**< 协议类型（ipc_bus_proto_t） */
    uint64_t msg_id;                         /**< 消息 ID */
    uint64_t correlation_id;                 /**< 关联 ID（请求-响应配对） */
    char     source[CONTRACT_AC_IPC_BUS_SERVICE_ID_LEN]; /**< 源服务 */
    char     target[CONTRACT_AC_IPC_BUS_SERVICE_ID_LEN]; /**< 目标服务 */
    uint32_t payload_len;                    /**< 负载长度 */
    uint32_t flags;                          /**< 标志位 */
    uint64_t timestamp;                      /**< 时间戳 */
    uint32_t checksum;                       /**< 校验和 */
    uint8_t  reserved[16];                   /**< 保留字段 */
} contract_ac_ipc_msg_header_t;

/**
 * @brief IPC Bus 测试 hook 回调签名
 *
 * 团队C 注册此回调拦截 IPC 消息。
 * @param header 消息头（BORROW，回调内只读）
 * @param payload 消息负载（BORROW，回调内只读）
 * @param payload_size 负载大小
 * @param user_data 团队C 注册时传入的用户数据
 * @return 0 放行消息，非 0 阻断并返回错误
 */
typedef int (*contract_ac_ipc_hook_t)(const contract_ac_ipc_msg_header_t *header,
                                      const void *payload,
                                      size_t payload_size,
                                      void *user_data);

/* ================================================================
 * 编译期验证（#if 0 块，不参与编译，仅作文档与示例）
 * ================================================================ */
#if 0
/* 注入点结构大小校验 */
static_assert(sizeof(contract_ac_injection_point_t) > 0,
              "injection point must be non-empty");

/* 指标描述符大小校验 */
static_assert(sizeof(contract_ac_metric_def_t) > 0,
              "metric def must be non-empty");

/* IPC 消息头大小校验：64 + 64 + 8*2 + 4*5 + 16 = 188 字节（取决于对齐） */
static_assert(sizeof(contract_ac_ipc_msg_header_t) >= 100,
              "IPC header too small");

/* 团队C 集成示例（伪代码）：
 *
 *   // C 测试用例注册 IPC hook
 *   contract_ac_ipc_hook_t hook = my_test_hook;
 *   ipc_bus_register_test_hook("llm_d", hook, test_ctx);
 *
 *   // Python 测试用例验证指标
 *   metrics = prometheus_client.fetch(CONTRACT_AC_METRIC_REQUESTS_TOTAL)
 *   assert metrics > 0
 *
 *   // 注入故障测试
 *   daemon_inject(CONTRACT_AC_INJ_IPC_REQUEST,
 *                 CONTRACT_AC_INJECT_DELAY, 100);
 */
#endif

#ifdef __cplusplus
}
#endif

#endif /* AGENTRT_CONTRACT_A_C_H */
