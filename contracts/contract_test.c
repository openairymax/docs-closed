/**
 * @file contract_test.c
 * @brief 合约文件编译验证测试
 *
 * 本文件的唯一目的是验证 contract_A_B.h 和 contract_A_C.h
 * 能够正确编译，且所有类型定义、宏定义、inline 函数
 * 语义正确。
 *
 * 编译命令：
 *   gcc -std=c11 -Wall -Wextra -Werror -c contract_test.c -o contract_test.o
 *
 * @note 本文件不链接任何团队A或团队B的实现，仅验证合约头文件的
 *       类型完整性和宏定义正确性。
 */

#include "contract_A_B.h"
#include "contract_A_C.h"
#include "contract_B_C.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

/* ================================================================
 * contract_A_B.h 编译验证
 * ================================================================ */

/* ── 第1节：IPC 消息格式 ── */

static void test_ipc_types(void) {
    /* Level 1: 内核级 IPC */
    agentos_kernel_ipc_message_t kmsg;
    kmsg.code = IPC_KERNEL_CODE_DATA;
    kmsg.data = NULL;
    kmsg.size = 0;
    kmsg.fd = -1;
    kmsg.msg_id = 0;
    (void)kmsg;

    /* Level 2: 应用级 IPC */
    agentos_ipc_header_t hdr;
    hdr.magic = AGENTOS_IPC_MAGIC;
    hdr.version = 1;
    hdr.type = AGENTOS_IPC_MSG_REQUEST;
    hdr.flags = 0;
    hdr.msg_id = 1;
    hdr.correlation_id = 0;
    memset(hdr.source, 0, sizeof(hdr.source));
    memset(hdr.target, 0, sizeof(hdr.target));
    hdr.payload_len = 0;
    hdr.checksum = 0;
    hdr.timestamp = 0;
    (void)hdr;

    agentos_ipc_message_t msg;
    msg.header = hdr;
    msg.payload = NULL;
    msg.payload_size = 0;
    (void)msg;

    /* Level 3: 通道配置 */
    agentos_ipc_config_t cfg;
    cfg.type = AGENTOS_IPC_SOCKET;
    cfg.name = "test_channel";
    cfg.buffer_size = 4096;
    cfg.max_message_size = 65536;
    cfg.timeout_ms = 5000;
    cfg.nonblocking = false;
    (void)cfg;

    /* 验证魔数 */
    assert(AGENTOS_IPC_MAGIC == 0x414F5350);

    /* 验证消息类型枚举值 */
    assert(AGENTOS_IPC_MSG_DATA == 0);
    assert(AGENTOS_IPC_MSG_REQUEST == 1);
    assert(AGENTOS_IPC_MSG_RESPONSE == 2);
}

/* ── 第2节：网关 API ── */

static void test_gateway_types(void) {
    gateway_type_t types[] = {GATEWAY_TYPE_HTTP, GATEWAY_TYPE_WS, GATEWAY_TYPE_STDIO};
    (void)types;

    gateway_error_t errs[] = {
        GATEWAY_SUCCESS, GATEWAY_ERROR_INVALID, GATEWAY_ERROR_MEMORY,
        GATEWAY_ERROR_IO, GATEWAY_ERROR_TIMEOUT, GATEWAY_ERROR_CLOSED,
        GATEWAY_ERROR_PROTOCOL
    };
    (void)errs;

    gateway_endpoint_request_t req;
    req.method = "POST";
    req.path = GATEWAY_ROUTE_JSONRPC;
    req.body = "{}";
    req.body_len = 2;
    req.user_data = NULL;
    (void)req;

    gateway_endpoint_response_t resp;
    resp.status_code = 200;
    resp.content_type = "application/json";
    resp.body = NULL;
    resp.body_len = 0;
    (void)resp;

    /* 验证路由路径常量 */
    assert(strcmp(GATEWAY_ROUTE_JSONRPC, "/") == 0);
    assert(strcmp(GATEWAY_ROUTE_HEALTH, "/healthz") == 0);
    assert(strcmp(GATEWAY_ROUTE_READY, "/readyz") == 0);
    assert(strcmp(GATEWAY_ROUTE_METRICS, "/metrics") == 0);

    /* 验证 JSON-RPC 错误码 */
    assert(JSONRPC_PARSE_ERROR == -32700);
    assert(JSONRPC_METHOD_NOT_FOUND == -32601);
}

/* ── 第3节：协议路由表 ── */

static void test_protocol_types(void) {
    agentos_protocol_type_t protos[] = {
        AGENTOS_PROTOCOL_JSONRPC, AGENTOS_PROTOCOL_MCP,
        AGENTOS_PROTOCOL_A2A, AGENTOS_PROTOCOL_OPENAI,
        AGENTOS_PROTOCOL_OPENJIUWEN, AGENTOS_PROTOCOL_CLAUDE,
        AGENTOS_PROTOCOL_CHINA_ECO, AGENTOS_PROTOCOL_AGNTCY,
        AGENTOS_PROTOCOL_OPENCLAW
    };
    (void)protos;

    assert(AGENTOS_PROTOCOL_COUNT == 9);

    message_direction_t dirs[] = {
        DIRECTION_REQUEST, DIRECTION_RESPONSE,
        DIRECTION_NOTIFICATION, DIRECTION_ERROR
    };
    (void)dirs;

    /* 验证能力标志 */
    assert(PROTO_CAP_SYNC_REQUEST == 0x0001);
    assert(PROTO_CAP_STREAMING == 0x0002);
    assert(PROTO_CAP_TOOL_CALLING == 0x00020000);

    unified_message_t umsg;
    memset(&umsg, 0, sizeof(umsg));
    umsg.protocol = AGENTOS_PROTOCOL_JSONRPC;
    umsg.direction = DIRECTION_REQUEST;
    (void)umsg;

    protocol_rule_t rule;
    rule.source_protocol = AGENTOS_PROTOCOL_OPENAI;
    rule.target_protocol = AGENTOS_PROTOCOL_JSONRPC;
    rule.source_endpoint = "/v1/chat/completions";
    rule.target_endpoint = "/";
    rule.priority = 100;
    rule.transformer_context = NULL;
    (void)rule;

    route_decision_t decision;
    decision.adapter_name = "jsonrpc";
    decision.target_protocol = AGENTOS_PROTOCOL_JSONRPC;
    decision.confidence = 95;
    decision.needs_transformation = true;
    decision.transformer_name = "openai_to_jsonrpc";
    (void)decision;
}

/* ── 第4节：内存布局 ── */

static void test_memory_types(void) {
    agentos_memory_capabilities_t caps;
    memset(&caps, 0, sizeof(caps));
    caps.l1_raw = 1;
    caps.l2_feature = 1;
    caps.l3_structure = 1;
    caps.l4_pattern = 1;
    caps.faiss = 1;
    (void)caps;

    agentos_memory_stats_t stats;
    memset(&stats, 0, sizeof(stats));
    stats.total_records = 100;
    stats.index_utilization = 0.75;
    (void)stats;

    agentos_memory_query_result_t result;
    result.record_ids = NULL;
    result.scores = NULL;
    result.count = 0;
    (void)result;

    agentos_memoryrov_config_t mr_cfg;
    memset(&mr_cfg, 0, sizeof(mr_cfg));
    mr_cfg.raw_storage_path = "/tmp/memrov/l1";
    mr_cfg.index_path = "/tmp/memrov/l2";
    mr_cfg.embedding_dim = 768;
    mr_cfg.index_type = 2; /* hnsw */
    (void)mr_cfg;
}

/* ── 第5节：配置 Schema ── */

static void test_config_types(void) {
    config_value_type_t types[] = {
        CONFIG_TYPE_NULL, CONFIG_TYPE_BOOL, CONFIG_TYPE_INT,
        CONFIG_TYPE_INT64, CONFIG_TYPE_DOUBLE, CONFIG_TYPE_STRING,
        CONFIG_TYPE_ARRAY, CONFIG_TYPE_OBJECT, CONFIG_TYPE_BINARY
    };
    (void)types;

    config_error_t errs[] = {
        CONFIG_SUCCESS, CONFIG_ERROR_INVALID_ARG, CONFIG_ERROR_NOT_FOUND,
        CONFIG_ERROR_TYPE_MISMATCH, CONFIG_ERROR_OUT_OF_MEMORY,
        CONFIG_ERROR_PARSE, CONFIG_ERROR_VALIDATION, CONFIG_ERROR_LOCKED
    };
    (void)errs;

    config_source_type_t sources[] = {
        CONFIG_SOURCE_FILE, CONFIG_SOURCE_ENV, CONFIG_SOURCE_ARGS,
        CONFIG_SOURCE_MEMORY, CONFIG_SOURCE_NETWORK, CONFIG_SOURCE_DATABASE
    };
    (void)sources;
}

/* ── 第6节：Hook 系统 ── */

static void test_hook_types(void) {
    /* 验证 Hook 回调类型可声明 */
    agentos_checkpoint_hook_fn cp_hook = NULL;
    agentos_feedback_callback_t fb_cb = NULL;
    am_alert_callback_t alert_cb = NULL;
    (void)cp_hook;
    (void)fb_cb;
    (void)alert_cb;
}

/* ── 第7节：错误码映射 ── */

static void test_error_mapping(void) {
    /* 成功 */
    assert(contract_sdk_err_from_c(0) == CONTRACT_SDK_ERR_OK);

    /* 通用错误 */
    assert(contract_sdk_err_from_c(-2) == CONTRACT_SDK_ERR_INVALID);
    assert(contract_sdk_err_from_c(-8) == CONTRACT_SDK_ERR_INVALID);

    /* 系统错误 */
    assert(contract_sdk_err_from_c(-101) == CONTRACT_SDK_ERR_SYSTEM);

    /* 内核错误 */
    assert(contract_sdk_err_from_c(-201) == CONTRACT_SDK_ERR_KERNEL);

    /* 服务错误 */
    assert(contract_sdk_err_from_c(-301) == CONTRACT_SDK_ERR_SERVICE);

    /* LLM 错误 */
    assert(contract_sdk_err_from_c(-401) == CONTRACT_SDK_ERR_LLM);
    assert(contract_sdk_err_from_c(-403) == CONTRACT_SDK_ERR_LLM);

    /* 执行错误 */
    assert(contract_sdk_err_from_c(-501) == CONTRACT_SDK_ERR_EXECUTION);

    /* 记忆错误 */
    assert(contract_sdk_err_from_c(-601) == CONTRACT_SDK_ERR_MEMORY);

    /* 安全错误 */
    assert(contract_sdk_err_from_c(-701) == CONTRACT_SDK_ERR_SECURITY);

    /* 协调错误 */
    assert(contract_sdk_err_from_c(-801) == CONTRACT_SDK_ERR_COORDINATION);
}

/* ── 第8节：时序约束 ── */

static void test_timing_constraints(void) {
    /* 验证时序约束常量存在且合理 */
    assert(CONTRACT_FFI_CALL_TIMEOUT_MS == 5000);
    assert(CONTRACT_IPC_SEND_TIMEOUT_MS == 3000);
    assert(CONTRACT_IPC_CALL_TIMEOUT_MS == 10000);
    assert(CONTRACT_HTTP_CONNECT_TIMEOUT_MS == 5000);
    assert(CONTRACT_HTTP_READ_TIMEOUT_MS == 30000);
    assert(CONTRACT_WS_PING_INTERVAL_MS == 30000);
    assert(CONTRACT_MEMORY_WRITE_TIMEOUT_MS == 5000);
    assert(CONTRACT_MEMORY_QUERY_TIMEOUT_MS == 10000);
    assert(CONTRACT_MEMORY_EVOLVE_TIMEOUT_MS == 60000);
    assert(CONTRACT_SDK_RETRY_MAX_ATTEMPTS == 3);
}

/* ================================================================
 * contract_A_C.h 编译验证
 * ================================================================ */

static void test_ac_error_mapping(void) {
    /* 验证错误码分类映射 */
    assert(contract_err_category(0) == CONTRACT_ERR_CATEGORY_OK);
    assert(contract_err_category(-8) == CONTRACT_ERR_CATEGORY_TRANSIENT);
    assert(contract_err_category(-17) == CONTRACT_ERR_CATEGORY_TRANSIENT);
    assert(contract_err_category(-2) == CONTRACT_ERR_CATEGORY_PERMANENT);
    assert(contract_err_category(-4) == CONTRACT_ERR_CATEGORY_RESOURCE);
    assert(contract_err_category(-701) == CONTRACT_ERR_CATEGORY_SECURITY);
    assert(contract_err_category(-31) == CONTRACT_ERR_CATEGORY_INTERNAL);
}

static void test_ac_metrics(void) {
    /* 验证指标名称常量 */
    assert(strcmp(METRIC_MEMORY_RSS_BYTES, "agentos_memory_rss_bytes") == 0);
    assert(strcmp(METRIC_OOM_EVENTS_TOTAL, "agentos_oom_events_total") == 0);
    assert(strcmp(METRIC_CONNECTION_HEALTH, "agentos_connection_health") == 0);
    assert(strcmp(METRIC_ERROR_BUDGET_REMAINING, "agentos_error_budget_remaining") == 0);
}

static void test_ac_health_endpoints(void) {
    assert(strcmp(HEALTH_ENDPOINT_LIVENESS, "/healthz") == 0);
    assert(strcmp(HEALTH_ENDPOINT_READINESS, "/readyz") == 0);
    assert(strcmp(HEALTH_ENDPOINT_METRICS, "/metrics") == 0);
}

static void test_ac_timing_constraints(void) {
    assert(CONTRACT_STARTUP_TIMEOUT_MS == 30000);
    assert(CONTRACT_READINESS_TIMEOUT_MS == 60000);
    assert(CONTRACT_HEARTBEAT_INTERVAL_MS == 5000);
    assert(CONTRACT_HEARTBEAT_TIMEOUT_MS == 15000);
    assert(CONTRACT_GRACEFUL_SHUTDOWN_MS == 10000);
    assert(CONTRACT_IPC_QUEUE_BACKPRESSURE == 1024);
    assert(CONTRACT_RETRY_MAX_ATTEMPTS == 3);
    assert(CONTRACT_SOAK_L1_DURATION_SEC == 4 * 3600);
    assert(CONTRACT_SOAK_L2_DURATION_SEC == 24 * 3600);
    assert(CONTRACT_SOAK_L3_DURATION_SEC == 72 * 3600);
}

static void test_ac_contract_version(void) {
    assert(CONTRACT_A_C_VERSION == 0x00010000);
    assert(CONTRACT_A_B_VERSION == 0x00010000);
}

/* ================================================================
 * contract_B_C.h 编译验证
 * ================================================================ */

static void test_bc_cli_exit_codes(void) {
    /* 验证 CLI 退出码枚举值 */
    assert(CLI_EXIT_SUCCESS == 0);
    assert(CLI_EXIT_GENERAL_ERROR == 1);
    assert(CLI_EXIT_INVALID_ARGS == 2);
    assert(CLI_EXIT_CONFIG_ERROR == 3);
    assert(CLI_EXIT_NETWORK_ERROR == 4);
    assert(CLI_EXIT_TIMEOUT == 6);
    assert(CLI_EXIT_DAEMON_UNREACHABLE == 7);
    assert(CLI_EXIT_SIGNAL_INTERRUPT == 130);
    assert(CLI_EXIT_SIGNAL_TERM == 143);
    assert(CLI_EXIT_UNKNOWN == 255);

    /* 验证退出码字符串映射 */
    assert(strcmp(cli_exit_code_str(CLI_EXIT_SUCCESS), "SUCCESS") == 0);
    assert(strcmp(cli_exit_code_str(CLI_EXIT_TIMEOUT), "TIMEOUT") == 0);
    assert(strcmp(cli_exit_code_str(CLI_EXIT_DAEMON_UNREACHABLE), "DAEMON_UNREACHABLE") == 0);

    /* 验证可重试判断 */
    assert(cli_exit_is_retryable(CLI_EXIT_TIMEOUT) == true);
    assert(cli_exit_is_retryable(CLI_EXIT_NETWORK_ERROR) == true);
    assert(cli_exit_is_retryable(CLI_EXIT_DAEMON_UNREACHABLE) == true);
    assert(cli_exit_is_retryable(CLI_EXIT_RATE_LIMITED) == true);
    assert(cli_exit_is_retryable(CLI_EXIT_SUCCESS) == false);
    assert(cli_exit_is_retryable(CLI_EXIT_INVALID_ARGS) == false);
    assert(cli_exit_is_retryable(CLI_EXIT_CONFIG_ERROR) == false);
}

static void test_bc_sdk_types(void) {
    /* 验证 SDK 语言枚举 */
    assert(SDK_LANG_PYTHON == 0);
    assert(SDK_LANG_RUST == 1);
    assert(SDK_LANG_GO == 2);
    assert(SDK_LANG_TYPESCRIPT == 3);
    assert(SDK_LANG_COUNT == 4);

    /* 验证语言名称映射 */
    assert(strcmp(sdk_lang_name(SDK_LANG_PYTHON), "python") == 0);
    assert(strcmp(sdk_lang_name(SDK_LANG_RUST), "rust") == 0);
    assert(strcmp(sdk_lang_name(SDK_LANG_GO), "go") == 0);
    assert(strcmp(sdk_lang_name(SDK_LANG_TYPESCRIPT), "typescript") == 0);
    assert(strcmp(sdk_lang_name((sdk_lang_t)99), "unknown") == 0);

    /* 验证测试状态枚举 */
    assert(TEST_STATUS_PASS == 0);
    assert(TEST_STATUS_FAIL == 1);
    assert(TEST_STATUS_SKIP == 2);
    assert(TEST_STATUS_ERROR == 3);
    assert(TEST_STATUS_TIMEOUT == 4);

    /* 验证测试结果结构体可声明 */
    sdk_test_result_t result;
    memset(&result, 0, sizeof(result));
    result.status = TEST_STATUS_PASS;
    result.duration_ms = 1.5;
    (void)result;

    sdk_test_harness_result_t harness;
    memset(&harness, 0, sizeof(harness));
    harness.language = SDK_LANG_PYTHON;
    harness.total_duration_ms = 100.0;
    (void)harness;

    /* 验证测试超时常量 */
    assert(CONTRACT_TEST_DEFAULT_TIMEOUT_SEC == 600);
    assert(CONTRACT_TEST_UNIT_TIMEOUT_SEC == 120);
    assert(CONTRACT_TEST_INTEGRATION_TIMEOUT_SEC == 1800);
    assert(CONTRACT_TEST_E2E_TIMEOUT_SEC == 3600);
}

static void test_bc_version_matrix(void) {
    sdk_version_info_t info;
    info.language = SDK_LANG_RUST;
    info.major = 0;
    info.minor = 1;
    info.patch = 0;
    (void)info;

    /* 验证最低版本常量存在 */
    assert(CONTRACT_SDK_PYTHON_MIN_MAJOR == 0);
    assert(CONTRACT_SDK_RUST_MIN_MINOR == 1);
    assert(CONTRACT_SDK_GO_MIN_PATCH == 0);
    assert(CONTRACT_SDK_TS_MIN_MAJOR == 0);
}

static void test_bc_docker_contract(void) {
    /* 验证 Docker 镜像名称常量 */
    assert(strcmp(DOCKER_IMAGE_GATEWAY, "agentrt/gateway") == 0);
    assert(strcmp(DOCKER_IMAGE_COREKERN, "agentrt/corekern") == 0);
    assert(strcmp(DOCKER_IMAGE_CLI, "agentrt/cli") == 0);
    assert(strcmp(DOCKER_IMAGE_SDK_PYTHON, "agentrt/sdk-python") == 0);

    /* 验证端口常量 */
    assert(CONTRACT_PORT_GATEWAY == 8080);
    assert(CONTRACT_PORT_COREKERN == 9001);
    assert(CONTRACT_PORT_LLM_D == 9002);
    assert(CONTRACT_PORT_CUPOLAS == 9004);

    /* 验证容器资源限制 */
    assert(CONTRACT_CONTAINER_MEMORY_LIMIT_MB_GATEWAY == 512);
    assert(CONTRACT_CONTAINER_MEMORY_LIMIT_MB_COREKERN == 2048);

    /* 验证健康检查配置结构 */
    container_health_config_t health;
    health.port = 8080;
    health.health_path = "/healthz";
    health.ready_path = "/readyz";
    health.metrics_path = "/metrics";
    health.interval_sec = 30;
    health.timeout_sec = 5;
    health.retries = 3;
    health.start_period_sec = 60;
    (void)health;
}

static void test_bc_ci_artifacts(void) {
    /* 验证 CI 产物目录常量 */
    assert(strcmp(CI_ARTIFACT_DIR_BUILDS, "artifacts/builds") == 0);
    assert(strcmp(CI_ARTIFACT_DIR_TESTS, "artifacts/tests") == 0);
    assert(strcmp(CI_ARTIFACT_DIR_COVERAGE, "artifacts/coverage") == 0);
    assert(strcmp(CI_ARTIFACT_DIR_BENCHMARKS, "artifacts/benchmarks") == 0);
    assert(strcmp(CI_ARTIFACT_DIR_SECURITY, "artifacts/security") == 0);
    assert(strcmp(CI_ARTIFACT_DIR_DOCS, "artifacts/docs") == 0);
}

static void test_bc_coverage_thresholds(void) {
    /* 验证覆盖率阈值常量 */
    assert(CONTRACT_COVERAGE_C_LINE_MIN == 80.0);
    assert(CONTRACT_COVERAGE_C_BRANCH_MIN == 70.0);
    assert(CONTRACT_COVERAGE_C_FUNC_MIN == 85.0);

    assert(CONTRACT_COVERAGE_PYTHON_LINE_MIN == 90.0);
    assert(CONTRACT_COVERAGE_PYTHON_BRANCH_MIN == 80.0);

    assert(CONTRACT_COVERAGE_RUST_LINE_MIN == 85.0);
    assert(CONTRACT_COVERAGE_RUST_BRANCH_MIN == 75.0);

    assert(CONTRACT_COVERAGE_GO_LINE_MIN == 85.0);
    assert(CONTRACT_COVERAGE_GO_BRANCH_MIN == 75.0);

    assert(CONTRACT_COVERAGE_TS_LINE_MIN == 90.0);
    assert(CONTRACT_COVERAGE_TS_BRANCH_MIN == 80.0);

    /* 覆盖率下降容限 */
    assert(CONTRACT_COVERAGE_DROP_LINE_MAX == 2.0);
    assert(CONTRACT_COVERAGE_DROP_BRANCH_MAX == 3.0);
}

static void test_bc_deploy_env(void) {
    /* 验证部署环境变量 */
    assert(strcmp(ENV_DEPLOY_ENV, "AGENTOS_DEPLOY_ENV") == 0);
    assert(strcmp(ENV_CONFIG_PATH, "AGENTOS_CONFIG_PATH") == 0);
    assert(strcmp(ENV_LOG_LEVEL, "AGENTOS_LOG_LEVEL") == 0);
    assert(strcmp(ENV_LLM_API_KEY, "AGENTOS_LLM_API_KEY") == 0);
    assert(strcmp(ENV_MAX_MEMORY_MB, "AGENTOS_MAX_MEMORY_MB") == 0);

    /* 验证部署环境枚举 */
    assert(DEPLOY_UNKNOWN == 0);
    assert(DEPLOY_DEV == 1);
    assert(DEPLOY_STAGING == 2);
    assert(DEPLOY_PRODUCTION == 3);

    /* 验证环境解析 */
    assert(deploy_env_from_string(DEPLOY_ENV_PRODUCTION) == DEPLOY_PRODUCTION);
    assert(deploy_env_from_string(DEPLOY_ENV_STAGING) == DEPLOY_STAGING);
    assert(deploy_env_from_string(DEPLOY_ENV_DEV) == DEPLOY_DEV);
    assert(deploy_env_from_string("unknown") == DEPLOY_DEV); /* 未知→dev */
    assert(deploy_env_from_string(NULL) == DEPLOY_DEV);      /* NULL→dev */

    /* 验证默认值 */
    assert(strcmp(DEFAULT_CONFIG_PATH, "/etc/agentrt/agentos.yaml") == 0);
    assert(strcmp(DEFAULT_LOG_LEVEL, "INFO") == 0);
    assert(strcmp(DEFAULT_LOG_PATH, "/var/log/agentrt") == 0);
    assert(strcmp(DEFAULT_DATA_PATH, "/var/lib/agentrt") == 0);
}

static void test_bc_version_utils(void) {
    /* 验证版本解析 */
    uint32_t major, minor, patch;
    assert(version_parse("0.1.1", &major, &minor, &patch) == 0);
    assert(major == 0 && minor == 1 && patch == 1);

    assert(version_parse("1.2.3", &major, &minor, &patch) == 0);
    assert(major == 1 && minor == 2 && patch == 3);

    assert(version_parse(NULL, &major, &minor, &patch) == -1);
    assert(version_parse("invalid", &major, &minor, &patch) == -1);

    /* 验证预发布版本判断 */
    assert(version_is_prerelease("0.1.1-alpha") == true);
    assert(version_is_prerelease("0.1.1-rc.1") == true);
    assert(version_is_prerelease("0.0.0-dev") == true);
    assert(version_is_prerelease("0.1.1") == false);
    assert(version_is_prerelease(NULL) == true);

    /* 验证版本兼容性 */
    assert(version_is_compatible(0, 1, 0, 1) == true);
    assert(version_is_compatible(0, 1, 0, 2) == false);
    assert(version_is_compatible(1, 0, 1, 0) == true);
    assert(version_is_compatible(1, 0, 0, 1) == false);

    /* 验证 CI 版本环境变量 */
    assert(strcmp(ENV_CI_VERSION, "AGENTOS_VERSION") == 0);
    assert(strcmp(VERSION_FILE_PATH, "VERSION") == 0);
    assert(strcmp(DEFAULT_VERSION, "0.0.0-dev") == 0);
}

/* ================================================================
 * 主测试入口
 * ================================================================ */

int main(void) {
    printf("=== contract_A_B.h 编译验证 ===\n");

    test_ipc_types();        printf("  [PASS] 第1节: IPC 消息格式\n");
    test_gateway_types();    printf("  [PASS] 第2节: 网关 API\n");
    test_protocol_types();   printf("  [PASS] 第3节: 协议路由表\n");
    test_memory_types();     printf("  [PASS] 第4节: 内存布局\n");
    test_config_types();     printf("  [PASS] 第5节: 配置 Schema\n");
    test_hook_types();       printf("  [PASS] 第6节: Hook 系统\n");
    test_error_mapping();    printf("  [PASS] 第7节: 错误码映射\n");
    test_timing_constraints(); printf("  [PASS] 第8节: 时序约束\n");

    printf("\n=== contract_A_C.h 编译验证 ===\n");

    test_ac_error_mapping();     printf("  [PASS] 第5节: 错误码映射\n");
    test_ac_metrics();           printf("  [PASS] 第2节: Prometheus 指标\n");
    test_ac_health_endpoints();  printf("  [PASS] 第4节: 健康检查端点\n");
    test_ac_timing_constraints(); printf("  [PASS] 第6节: 时序约束\n");
    test_ac_contract_version();  printf("  [PASS] 合约版本号\n");

    printf("\n=== contract_B_C.h 编译验证 ===\n");

    test_bc_cli_exit_codes();     printf("  [PASS] 第1节: CLI/TUI 退出码\n");
    test_bc_sdk_types();          printf("  [PASS] 第2节: SDK 测试 Harness\n");
    test_bc_version_matrix();     printf("  [PASS] 第3节: 版本兼容矩阵\n");
    test_bc_docker_contract();    printf("  [PASS] 第4节: Docker 容器契约\n");
    test_bc_ci_artifacts();       printf("  [PASS] 第5节: CI 产物命名\n");
    test_bc_coverage_thresholds(); printf("  [PASS] 第6节: 覆盖率阈值\n");
    test_bc_deploy_env();         printf("  [PASS] 第7节: 部署环境变量\n");
    test_bc_version_utils();      printf("  [PASS] 第8节: 版本号工具\n");

    printf("\n=== 所有合约编译验证通过 ===\n");
    return 0;
}
