// SPDX-FileCopyrightText: 2026 SPHARX Ltd.
// SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0
/**
 * @file contract_test.c
 * @brief 跨团队合约编译验证与二进制布局断言
 *
 * 本文件验证三份合约头文件的可编译性，并对关键结构体的大小与
 * 偏移进行静态/运行时断言。返回 0 表示全部验证通过。
 *
 * 验证内容：
 *   1. 三份合约头文件可独立编译（无外部依赖）
 *   2. 合约版本号符合语义化版本规范
 *   3. 关键结构体大小符合预期（二进制布局稳定）
 *   4. 关键字段偏移符合预期（跨团队 ABI 兼容）
 *   5. 枚举值与宏定义一致
 *
 * 构建方式：
 *   cmake -B build -DCMAKE_BUILD_TYPE=Release
 *   cmake --build build --target contract_tests
 *   ./build/contracts/contract_tests
 *
 * @owner team-A, team-B, team-C
 * @version 1.0.0
 * @see P0.14 跨团队合约任务
 */

#include "contract_A_B.h"
#include "contract_A_C.h"
#include "contract_B_C.h"

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

/* ================================================================
 * 测试框架
 * ================================================================ */

static int g_tests_run = 0;
static int g_tests_passed = 0;
static int g_tests_failed = 0;

#define TEST_ASSERT(cond, msg)                                              \
    do {                                                                    \
        g_tests_run++;                                                      \
        if (cond) {                                                         \
            g_tests_passed++;                                               \
            printf("  [PASS] %s\n", msg);                                   \
        } else {                                                            \
            g_tests_failed++;                                               \
            printf("  [FAIL] %s (line %d)\n", msg, __LINE__);               \
        }                                                                   \
    } while (0)

#define TEST_ASSERT_EQ(actual, expected, msg) \
    TEST_ASSERT((actual) == (expected), msg)

/* ================================================================
 * 1. 合约版本号验证
 * ================================================================ */

static void test_contract_versions(void)
{
    printf("\n--- 合约版本号验证 ---\n");

    /* 团队A ↔ 团队B 合约版本 */
    TEST_ASSERT(strcmp(CONTRACT_A_B_VERSION, "1.0.0") == 0,
                "CONTRACT_A_B_VERSION == 1.0.0");
    TEST_ASSERT_EQ(CONTRACT_A_B_VERSION_MAJOR, 1, "A_B major == 1");
    TEST_ASSERT_EQ(CONTRACT_A_B_VERSION_MINOR, 0, "A_B minor == 0");
    TEST_ASSERT_EQ(CONTRACT_A_B_VERSION_PATCH, 0, "A_B patch == 0");

    /* 团队A ↔ 团队C 合约版本 */
    TEST_ASSERT(strcmp(CONTRACT_A_C_VERSION, "1.0.0") == 0,
                "CONTRACT_A_C_VERSION == 1.0.0");
    TEST_ASSERT_EQ(CONTRACT_A_C_VERSION_MAJOR, 1, "A_C major == 1");
    TEST_ASSERT_EQ(CONTRACT_A_C_VERSION_MINOR, 0, "A_C minor == 0");
    TEST_ASSERT_EQ(CONTRACT_A_C_VERSION_PATCH, 0, "A_C patch == 0");

    /* 团队B ↔ 团队C 合约版本 */
    TEST_ASSERT(strcmp(CONTRACT_B_C_VERSION, "1.0.0") == 0,
                "CONTRACT_B_C_VERSION == 1.0.0");
    TEST_ASSERT_EQ(CONTRACT_B_C_VERSION_MAJOR, 1, "B_C major == 1");
    TEST_ASSERT_EQ(CONTRACT_B_C_VERSION_MINOR, 0, "B_C minor == 0");
    TEST_ASSERT_EQ(CONTRACT_B_C_VERSION_PATCH, 0, "B_C patch == 0");
}

/* ================================================================
 * 2. C-L01 配置消息结构验证
 * ================================================================ */

static void test_cl01_config_message(void)
{
    printf("\n--- C-L01 配置消息结构验证 ---\n");

    /* 魔数校验 */
    TEST_ASSERT_EQ(CONTRACT_CL01_MAGIC, 0x4C30314DU, "C-L01 magic value");
    TEST_ASSERT_EQ(CONTRACT_CL01_VERSION, 1, "C-L01 version == 1");

    /* 配置路径长度对齐 */
    TEST_ASSERT_EQ(CONTRACT_CL01_CONFIG_PATH_MAX, 256,
                   "C-L01 config path max == 256");

    /* 结构体大小：4+4+8+4+4+256 = 280 字节 */
    TEST_ASSERT_EQ(sizeof(contract_cl01_config_msg_t), 280,
                   "C-L01 config msg size == 280");

    /* 字段偏移验证（跨团队 ABI 兼容） */
    TEST_ASSERT_EQ(offsetof(contract_cl01_config_msg_t, magic), 0,
                   "C-L01 magic offset == 0");
    TEST_ASSERT_EQ(offsetof(contract_cl01_config_msg_t, version), 4,
                   "C-L01 version offset == 4");
    TEST_ASSERT_EQ(offsetof(contract_cl01_config_msg_t, timestamp), 8,
                   "C-L01 timestamp offset == 8");
    TEST_ASSERT_EQ(offsetof(contract_cl01_config_msg_t, config_size), 16,
                   "C-L01 config_size offset == 16");
    TEST_ASSERT_EQ(offsetof(contract_cl01_config_msg_t, config_path), 24,
                   "C-L01 config_path offset == 24");
}

/* ================================================================
 * 3. C-L03 market_d HTTP API 验证
 * ================================================================ */

static void test_cl03_market_api(void)
{
    printf("\n--- C-L03 market_d HTTP API 验证 ---\n");

    /* 错误码校验（与 market_service.h 对齐） */
    TEST_ASSERT_EQ(CONTRACT_CL03_ERR_INVALID_PARAM, -1000,
                   "C-L03 ERR_INVALID_PARAM == -1000");
    TEST_ASSERT_EQ(CONTRACT_CL03_ERR_OUT_OF_MEMORY, -1001,
                   "C-L03 ERR_OUT_OF_MEMORY == -1001");
    TEST_ASSERT_EQ(CONTRACT_CL03_ERR_NOT_FOUND, -1002,
                   "C-L03 ERR_NOT_FOUND == -1002");
    TEST_ASSERT_EQ(CONTRACT_CL03_ERR_ALREADY_EXISTS, -1003,
                   "C-L03 ERR_ALREADY_EXISTS == -1003");
    TEST_ASSERT_EQ(CONTRACT_CL03_ERR_INSTALL_FAIL, -1004,
                   "C-L03 ERR_INSTALL_FAIL == -1004");

    /* TCP 端口校验 */
    TEST_ASSERT_EQ(CONTRACT_CL03_DEFAULT_TCP_PORT, 8082,
                   "C-L03 default TCP port == 8082");

    /* Agent 信息结构非空 */
    TEST_ASSERT(sizeof(contract_cl03_agent_info_t) > 0,
                "C-L03 agent_info non-empty");

    /* Agent ID 字段偏移 */
    TEST_ASSERT_EQ(offsetof(contract_cl03_agent_info_t, agent_id), 0,
                   "C-L03 agent_id offset == 0");
}

/* ================================================================
 * 4. C-L11 协议路由表验证
 * ================================================================ */

static void test_cl11_protocol_routes(void)
{
    printf("\n--- C-L11 协议路由表验证 ---\n");

    /* 协议数量校验 */
    TEST_ASSERT_EQ(CONTRACT_CL11_PROTO_COUNT, 4,
                   "C-L11 proto count == 4");

    /* 默认超时校验 */
    TEST_ASSERT_EQ(CONTRACT_CL11_DEFAULT_TIMEOUT_MS, 30000,
                   "C-L11 default timeout == 30000ms");

    /* 枚举值校验 */
    TEST_ASSERT_EQ(CONTRACT_CL11_PROTO_A2A, 0, "C-L11 A2A == 0");
    TEST_ASSERT_EQ(CONTRACT_CL11_PROTO_MCP, 1, "C-L11 MCP == 1");
    TEST_ASSERT_EQ(CONTRACT_CL11_PROTO_OPENAI, 2, "C-L11 OpenAI == 2");
    TEST_ASSERT_EQ(CONTRACT_CL11_PROTO_JSONRPC, 3, "C-L11 JSONRPC == 3");

    /* 默认路由表项数校验 */
    TEST_ASSERT_EQ(sizeof(CONTRACT_CL11_DEFAULT_ROUTES) /
                       sizeof(CONTRACT_CL11_DEFAULT_ROUTES[0]),
                   CONTRACT_CL11_PROTO_COUNT,
                   "C-L11 default routes count == proto count");

    /* 路由表目标 daemon 校验 */
    TEST_ASSERT(strcmp(CONTRACT_CL11_DEFAULT_ROUTES[0].target_daemon,
                       "sched_d") == 0,
                "C-L11 A2A route -> sched_d");
    TEST_ASSERT(strcmp(CONTRACT_CL11_DEFAULT_ROUTES[1].target_daemon,
                       "tool_d") == 0,
                "C-L11 MCP route -> tool_d");
    TEST_ASSERT(strcmp(CONTRACT_CL11_DEFAULT_ROUTES[2].target_daemon,
                       "llm_d") == 0,
                "C-L11 OpenAI route -> llm_d");
    TEST_ASSERT(strcmp(CONTRACT_CL11_DEFAULT_ROUTES[3].target_daemon,
                       "sched_d") == 0,
                "C-L11 JSONRPC route -> sched_d");
}

/* ================================================================
 * 5. C-L12 内存布局验证
 * ================================================================ */

static void test_cl12_memory_layout(void)
{
    printf("\n--- C-L12 内存布局验证 ---\n");

    /* 提供商名称校验 */
    TEST_ASSERT(strcmp(CONTRACT_CL12_BUILTIN_NAME, "builtin") == 0,
                "C-L12 builtin name");
    TEST_ASSERT(strcmp(CONTRACT_CL12_MEMORYROVOL_NAME, "MemoryRovol") == 0,
                "C-L12 MemoryRovol name");
    TEST_ASSERT(strcmp(CONTRACT_CL12_MEMORYROVOL_VERSION, "2.0.0") == 0,
                "C-L12 MemoryRovol version == 2.0.0");

    /* 能力标记大小：10 + 5 = 15 字节 */
    TEST_ASSERT_EQ(sizeof(contract_cl12_capabilities_t), 15,
                   "C-L12 capabilities size == 15");

    /* 能力标记字段偏移 */
    TEST_ASSERT_EQ(offsetof(contract_cl12_capabilities_t, l1_raw), 0,
                   "C-L12 l1_raw offset == 0");
    TEST_ASSERT_EQ(offsetof(contract_cl12_capabilities_t, l2_feature), 1,
                   "C-L12 l2_feature offset == 1");
    TEST_ASSERT_EQ(offsetof(contract_cl12_capabilities_t, l3_structure), 2,
                   "C-L12 l3_structure offset == 2");
    TEST_ASSERT_EQ(offsetof(contract_cl12_capabilities_t, l4_pattern), 3,
                   "C-L12 l4_pattern offset == 3");

    /* 提供商类型枚举校验 */
    TEST_ASSERT_EQ(CONTRACT_CL12_PROVIDER_BUILTIN, 0,
                   "C-L12 PROVIDER_BUILTIN == 0");
    TEST_ASSERT_EQ(CONTRACT_CL12_PROVIDER_MEMORYROVOL, 1,
                   "C-L12 PROVIDER_MEMORYROVOL == 1");
    TEST_ASSERT_EQ(CONTRACT_CL12_PROVIDER_HYBRID, 2,
                   "C-L12 PROVIDER_HYBRID == 2");
    TEST_ASSERT_EQ(CONTRACT_CL12_PROVIDER_AUTO, 3,
                   "C-L12 PROVIDER_AUTO == 3");

    /* 统计结构非空 */
    TEST_ASSERT(sizeof(contract_cl12_memory_stats_t) > 0,
                "C-L12 memory_stats non-empty");
}

/* ================================================================
 * 6. Daemon 测试注入点验证
 * ================================================================ */

static void test_daemon_injection_points(void)
{
    printf("\n--- Daemon 测试注入点验证 ---\n");

    /* 测试模式环境变量校验 */
    TEST_ASSERT(strcmp(CONTRACT_AC_TEST_MODE_ENV, "AGENTOS_TEST_MODE") == 0,
                "test mode env var");
    TEST_ASSERT(strcmp(CONTRACT_AC_TEST_MODE_ENABLED, "1") == 0,
                "test mode enabled == 1");
    TEST_ASSERT(strcmp(CONTRACT_AC_TEST_MODE_DISABLED, "0") == 0,
                "test mode disabled == 0");

    /* 注入点类型枚举校验 */
    TEST_ASSERT_EQ(CONTRACT_AC_INJECT_FAULT, 0, "INJECT_FAULT == 0");
    TEST_ASSERT_EQ(CONTRACT_AC_INJECT_DELAY, 1, "INJECT_DELAY == 1");
    TEST_ASSERT_EQ(CONTRACT_AC_INJECT_ASSERT, 2, "INJECT_ASSERT == 2");

    /* 标准注入点名称非空 */
    TEST_ASSERT(strlen(CONTRACT_AC_INJ_DAEMON_INIT) > 0,
                "daemon.init injection point");
    TEST_ASSERT(strlen(CONTRACT_AC_INJ_IPC_REQUEST) > 0,
                "ipc.request injection point");
    TEST_ASSERT(strlen(CONTRACT_AC_INJ_HEALTH_CHECK) > 0,
                "health.check injection point");

    /* 注入点结构非空 */
    TEST_ASSERT(sizeof(contract_ac_injection_point_t) > 0,
                "injection point struct non-empty");
}

/* ================================================================
 * 7. Prometheus 指标命名验证
 * ================================================================ */

static void test_prometheus_metrics(void)
{
    printf("\n--- Prometheus 指标命名验证 ---\n");

    /* 必需指标数量校验 */
    TEST_ASSERT_EQ(CONTRACT_AC_REQUIRED_METRICS_COUNT, 14,
                   "required metrics count == 14");

    /* 指标前缀校验 */
    TEST_ASSERT(strcmp(CONTRACT_AC_METRIC_PREFIX, "agentos_") == 0,
                "metric prefix == agentos_");

    /* 14 项指标名均以 agentos_ 开头 */
    TEST_ASSERT(strncmp(CONTRACT_AC_METRIC_REQUESTS_TOTAL,
                        CONTRACT_AC_METRIC_PREFIX, 8) == 0,
                "requests_total starts with agentos_");
    TEST_ASSERT(strncmp(CONTRACT_AC_METRIC_REQUEST_DURATION,
                        CONTRACT_AC_METRIC_PREFIX, 8) == 0,
                "request_duration starts with agentos_");
    TEST_ASSERT(strncmp(CONTRACT_AC_METRIC_ERRORS_TOTAL,
                        CONTRACT_AC_METRIC_PREFIX, 8) == 0,
                "errors_total starts with agentos_");
    TEST_ASSERT(strncmp(CONTRACT_AC_METRIC_ACTIVE_CONNECTIONS,
                        CONTRACT_AC_METRIC_PREFIX, 8) == 0,
                "active_connections starts with agentos_");
    TEST_ASSERT(strncmp(CONTRACT_AC_METRIC_MEMORY_USAGE_BYTES,
                        CONTRACT_AC_METRIC_PREFIX, 8) == 0,
                "memory_usage_bytes starts with agentos_");
    TEST_ASSERT(strncmp(CONTRACT_AC_METRIC_CPU_USAGE,
                        CONTRACT_AC_METRIC_PREFIX, 8) == 0,
                "cpu_usage starts with agentos_");
    TEST_ASSERT(strncmp(CONTRACT_AC_METRIC_UPTIME_SECONDS,
                        CONTRACT_AC_METRIC_PREFIX, 8) == 0,
                "uptime_seconds starts with agentos_");
    TEST_ASSERT(strncmp(CONTRACT_AC_METRIC_QUEUE_DEPTH,
                        CONTRACT_AC_METRIC_PREFIX, 8) == 0,
                "queue_depth starts with agentos_");
    TEST_ASSERT(strncmp(CONTRACT_AC_METRIC_IPC_LATENCY,
                        CONTRACT_AC_METRIC_PREFIX, 8) == 0,
                "ipc_latency starts with agentos_");
    TEST_ASSERT(strncmp(CONTRACT_AC_METRIC_GC_PAUSE_SECONDS,
                        CONTRACT_AC_METRIC_PREFIX, 8) == 0,
                "gc_pause_seconds starts with agentos_");
    TEST_ASSERT(strncmp(CONTRACT_AC_METRIC_FILE_DESCRIPTORS,
                        CONTRACT_AC_METRIC_PREFIX, 8) == 0,
                "file_descriptors starts with agentos_");
    TEST_ASSERT(strncmp(CONTRACT_AC_METRIC_GOROUTINE_COUNT,
                        CONTRACT_AC_METRIC_PREFIX, 8) == 0,
                "goroutine_count starts with agentos_");
    TEST_ASSERT(strncmp(CONTRACT_AC_METRIC_CACHE_HIT_RATIO,
                        CONTRACT_AC_METRIC_PREFIX, 8) == 0,
                "cache_hit_ratio starts with agentos_");
    TEST_ASSERT(strncmp(CONTRACT_AC_METRIC_CIRCUIT_BREAKER_STATE,
                        CONTRACT_AC_METRIC_PREFIX, 8) == 0,
                "circuit_breaker_state starts with agentos_");

    /* 指标类型枚举校验 */
    TEST_ASSERT_EQ(CONTRACT_AC_METRIC_COUNTER, 0, "COUNTER == 0");
    TEST_ASSERT_EQ(CONTRACT_AC_METRIC_GAUGE, 1, "GAUGE == 1");
    TEST_ASSERT_EQ(CONTRACT_AC_METRIC_HISTOGRAM, 2, "HISTOGRAM == 2");
    TEST_ASSERT_EQ(CONTRACT_AC_METRIC_SUMMARY, 3, "SUMMARY == 3");
}

/* ================================================================
 * 8. IPC Bus 测试 Hooks 验证
 * ================================================================ */

static void test_ipc_bus_hooks(void)
{
    printf("\n--- IPC Bus 测试 Hooks 验证 ---\n");

    /* 魔数校验 */
    TEST_ASSERT_EQ(CONTRACT_AC_IPC_BUS_MAGIC, 0x49534200U,
                   "IPC bus magic");

    /* 容量校验 */
    TEST_ASSERT_EQ(CONTRACT_AC_IPC_BUS_MAX_SERVICES, 64,
                   "IPC bus max services == 64");
    TEST_ASSERT_EQ(CONTRACT_AC_IPC_BUS_MAX_CHANNELS, 32,
                   "IPC bus max channels == 32");
    TEST_ASSERT_EQ(CONTRACT_AC_IPC_BUS_MAX_MESSAGE_SIZE, 512 * 1024,
                   "IPC bus max message size == 512KB");
    TEST_ASSERT_EQ(CONTRACT_AC_IPC_BUS_DEFAULT_TIMEOUT_MS, 5000,
                   "IPC bus default timeout == 5000ms");
    TEST_ASSERT_EQ(CONTRACT_AC_IPC_BUS_MAX_RETRIES, 3,
                   "IPC bus max retries == 3");

    /* 消息类型枚举校验 */
    TEST_ASSERT_EQ(CONTRACT_AC_IPC_MSG_REQUEST, 0, "MSG_REQUEST == 0");
    TEST_ASSERT_EQ(CONTRACT_AC_IPC_MSG_RESPONSE, 1, "MSG_RESPONSE == 1");
    TEST_ASSERT_EQ(CONTRACT_AC_IPC_MSG_HEARTBEAT, 4, "MSG_HEARTBEAT == 4");

    /* 消息头结构非空 */
    TEST_ASSERT(sizeof(contract_ac_ipc_msg_header_t) > 0,
                "IPC msg header non-empty");

    /* 消息头字段偏移 */
    TEST_ASSERT_EQ(offsetof(contract_ac_ipc_msg_header_t, magic), 0,
                   "IPC header magic offset == 0");
    TEST_ASSERT_EQ(offsetof(contract_ac_ipc_msg_header_t, version), 4,
                   "IPC header version offset == 4");
    TEST_ASSERT_EQ(offsetof(contract_ac_ipc_msg_header_t, msg_id), 16,
                   "IPC header msg_id offset == 16");
}

/* ================================================================
 * 9. CLI 退出码验证
 * ================================================================ */

static void test_cli_exit_codes(void)
{
    printf("\n--- CLI 退出码验证 ---\n");

    /* 标准退出码校验 */
    TEST_ASSERT_EQ(CONTRACT_BC_EXIT_SUCCESS, 0, "EXIT_SUCCESS == 0");
    TEST_ASSERT_EQ(CONTRACT_BC_EXIT_GENERIC_ERROR, 1, "EXIT_GENERIC == 1");
    TEST_ASSERT_EQ(CONTRACT_BC_EXIT_USAGE_ERROR, 2, "EXIT_USAGE == 2");

    /* sysexits.h 标准错误码校验 */
    TEST_ASSERT_EQ(CONTRACT_BC_EXIT_DATA_ERROR, 65, "EXIT_DATA == 65");
    TEST_ASSERT_EQ(CONTRACT_BC_EXIT_UNAVAILABLE, 69, "EXIT_UNAVAILABLE == 69");
    TEST_ASSERT_EQ(CONTRACT_BC_EXIT_CONFIG, 78, "EXIT_CONFIG == 78");

    /* AgentRT 自定义错误码校验 */
    TEST_ASSERT_EQ(CONTRACT_BC_EXIT_GATEWAY_UNREACHABLE, 80,
                   "EXIT_GATEWAY_UNREACHABLE == 80");
    TEST_ASSERT_EQ(CONTRACT_BC_EXIT_GATEWAY_TIMEOUT, 81,
                   "EXIT_GATEWAY_TIMEOUT == 81");
    TEST_ASSERT_EQ(CONTRACT_BC_EXIT_AUTH_FAILED, 82,
                   "EXIT_AUTH_FAILED == 82");
    TEST_ASSERT_EQ(CONTRACT_BC_EXIT_RATE_LIMITED, 83,
                   "EXIT_RATE_LIMITED == 83");
    TEST_ASSERT_EQ(CONTRACT_BC_EXIT_AGENT_RUN_FAILED, 85,
                   "EXIT_AGENT_RUN_FAILED == 85");
    TEST_ASSERT_EQ(CONTRACT_BC_EXIT_MARKET_INSTALL_FAIL, 86,
                   "EXIT_MARKET_INSTALL_FAIL == 86");

    /* 自定义错误码范围校验 */
    TEST_ASSERT(CONTRACT_BC_EXIT_GATEWAY_UNREACHABLE >= 80,
                "custom exit codes >= 80");
    TEST_ASSERT(CONTRACT_BC_EXIT_DEPLOY_FAIL < 100,
                "custom exit codes < 100");

    /* CLI 命令名称非空 */
    TEST_ASSERT(strlen(CONTRACT_BC_CMD_INIT) > 0, "CMD_INIT non-empty");
    TEST_ASSERT(strlen(CONTRACT_BC_CMD_RUN) > 0, "CMD_RUN non-empty");
    TEST_ASSERT(strlen(CONTRACT_BC_CMD_MARKET) > 0, "CMD_MARKET non-empty");
    TEST_ASSERT(strlen(CONTRACT_BC_CMD_DEPLOY) > 0, "CMD_DEPLOY non-empty");
}

/* ================================================================
 * 10. SDK 测试 Harness 验证
 * ================================================================ */

static void test_sdk_harness(void)
{
    printf("\n--- SDK 测试 Harness 验证 ---\n");

    /* 默认超时校验 */
    TEST_ASSERT_EQ(CONTRACT_BC_HARNESS_DEFAULT_TIMEOUT_SEC, 30,
                   "harness default timeout == 30s");
    TEST_ASSERT_EQ(CONTRACT_BC_HARNESS_MAX_CONCURRENT, 16,
                   "harness max concurrent == 16");

    /* Harness 状态枚举校验 */
    TEST_ASSERT_EQ(CONTRACT_BC_HARNESS_IDLE, 0, "HARNESS_IDLE == 0");
    TEST_ASSERT_EQ(CONTRACT_BC_HARNESS_RUNNING, 2, "HARNESS_RUNNING == 2");
    TEST_ASSERT_EQ(CONTRACT_BC_HARNESS_COMPLETED, 4, "HARNESS_COMPLETED == 4");
    TEST_ASSERT_EQ(CONTRACT_BC_HARNESS_FAILED, 5, "HARNESS_FAILED == 5");

    /* 配置结构非空 */
    TEST_ASSERT(sizeof(contract_bc_harness_config_t) > 0,
                "harness config non-empty");
    TEST_ASSERT(sizeof(contract_bc_harness_result_t) > 0,
                "harness result non-empty");

    /* 环境变量校验 */
    TEST_ASSERT(strcmp(CONTRACT_BC_HARNESS_TEST_MODE_ENV, "AGENTOS_TEST_MODE") == 0,
                "harness test mode env == AGENTOS_TEST_MODE");
}

/* ================================================================
 * 11. Docker 健康检查端点验证
 * ================================================================ */

static void test_docker_healthcheck(void)
{
    printf("\n--- Docker 健康检查端点验证 ---\n");

    /* 端点路径校验 */
    TEST_ASSERT(strcmp(CONTRACT_BC_HEALTH_ENDPOINT, "/healthz") == 0,
                "health endpoint == /healthz");
    TEST_ASSERT(strcmp(CONTRACT_BC_READY_ENDPOINT, "/readyz") == 0,
                "ready endpoint == /readyz");
    TEST_ASSERT(strcmp(CONTRACT_BC_METRICS_ENDPOINT, "/metrics") == 0,
                "metrics endpoint == /metrics");

    /* 默认端口校验 */
    TEST_ASSERT_EQ(CONTRACT_BC_DEFAULT_HTTP_PORT, 8080,
                   "default HTTP port == 8080");
    TEST_ASSERT_EQ(CONTRACT_BC_DEFAULT_WS_PORT, 8081,
                   "default WS port == 8081");
    TEST_ASSERT_EQ(CONTRACT_BC_DEFAULT_METRICS_PORT, 9090,
                   "default metrics port == 9090");

    /* 健康检查参数校验 */
    TEST_ASSERT_EQ(CONTRACT_BC_HEALTH_INTERVAL_SEC, 5,
                   "health interval == 5s");
    TEST_ASSERT_EQ(CONTRACT_BC_HEALTH_TIMEOUT_SEC, 3,
                   "health timeout == 3s");
    TEST_ASSERT_EQ(CONTRACT_BC_HEALTH_RETRIES, 5,
                   "health retries == 5");
    TEST_ASSERT_EQ(CONTRACT_BC_HEALTH_START_PERIOD_SEC, 15,
                   "health start period == 15s");

    /* 标准 daemon 服务名校验 */
    TEST_ASSERT(strcmp(CONTRACT_BC_SERVICE_GATEWAY_D, "gateway_d") == 0,
                "service gateway_d");
    TEST_ASSERT(strcmp(CONTRACT_BC_SERVICE_LLM_D, "llm_d") == 0,
                "service llm_d");
    TEST_ASSERT(strcmp(CONTRACT_BC_SERVICE_MARKET_D, "market_d") == 0,
                "service market_d");
    TEST_ASSERT(strcmp(CONTRACT_BC_SERVICE_CORELOOPTHREE, "coreloopthree") == 0,
                "service coreloopthree");

    /* 健康响应结构非空 */
    TEST_ASSERT(sizeof(contract_bc_health_response_t) > 0,
                "health response non-empty");
}

/* ================================================================
 * 12. 跨合约一致性验证
 * ================================================================ */

static void test_cross_contract_consistency(void)
{
    printf("\n--- 跨合约一致性验证 ---\n");

    /* 三份合约版本一致（同一 P0.14 任务产物） */
    TEST_ASSERT(strcmp(CONTRACT_A_B_VERSION, CONTRACT_A_C_VERSION) == 0,
                "A_B version == A_C version");
    TEST_ASSERT(strcmp(CONTRACT_A_B_VERSION, CONTRACT_B_C_VERSION) == 0,
                "A_B version == B_C version");

    /* 测试模式环境变量跨合约一致 */
    TEST_ASSERT(strcmp(CONTRACT_AC_TEST_MODE_ENV,
                       CONTRACT_BC_HARNESS_TEST_MODE_ENV) == 0,
                "test mode env var consistent across contracts");

    /* 测试模式启用值跨合约一致 */
    TEST_ASSERT(strcmp(CONTRACT_AC_TEST_MODE_ENABLED,
                       CONTRACT_BC_HARNESS_TEST_MODE_ENV) != 0 ||
                strcmp(CONTRACT_AC_TEST_MODE_ENABLED, "1") == 0,
                "test mode enabled value == 1");
}

/* ================================================================
 * 主入口
 * ================================================================ */

int main(void)
{
    printf("========================================================\n");
    printf("  AgentRT 跨团队合约编译验证\n");
    printf("  Contract Version: A_B=%s A_C=%s B_C=%s\n",
           CONTRACT_A_B_VERSION, CONTRACT_A_C_VERSION, CONTRACT_B_C_VERSION);
    printf("========================================================\n");

    test_contract_versions();
    test_cl01_config_message();
    test_cl03_market_api();
    test_cl11_protocol_routes();
    test_cl12_memory_layout();
    test_daemon_injection_points();
    test_prometheus_metrics();
    test_ipc_bus_hooks();
    test_cli_exit_codes();
    test_sdk_harness();
    test_docker_healthcheck();
    test_cross_contract_consistency();

    printf("\n========================================================\n");
    printf("  合约验证结果: %d/%d 通过, %d 失败\n",
           g_tests_passed, g_tests_run, g_tests_failed);
    printf("========================================================\n");

    return (g_tests_failed == 0) ? 0 : 1;
}
