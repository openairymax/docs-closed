// SPDX-FileCopyrightText: 2026 SPHARX Ltd.
// SPDX-License-Identifier: Apache-2.0
/**
 * @file contract_B_C.h
 * @brief 跨团队接口合约：团队B（生态 + SDK）↔ 团队C（基础设施）
 *
 * 本合约固化团队B 与团队C 之间的三类基础设施约定：
 *   - CLI 退出码规范（agentrt CLI 命令的退出码定义）
 *   - SDK 测试 harness 接口
 *   - Docker 健康检查端点
 *
 * 团队C 在 CI/CD 流水线与容器编排中依赖本合约的稳定标识。
 * 任何退出码或端点变更必须先升级本合约版本号。
 *
 * 参考实现：
 *   - sdk/cli/src/main.rs（agentrt CLI 入口）
 *   - sdk/cli/src/commands/ （各命令实现 .rs 文件）
 *   - sdk/python/agentos/exceptions.py（错误码体系）
 *   - deploy/docker/Dockerfile（HEALTHCHECK 定义）
 *   - deploy/docker/docker-compose.test.yml（健康检查配置）
 *
 * @owner team-B, team-C
 * @version 1.0.0
 * @see P0.14 跨团队合约任务
 */

#ifndef AGENTRT_CONTRACT_B_C_H
#define AGENTRT_CONTRACT_B_C_H
#pragma once

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ================================================================
 * 合约版本
 * ================================================================ */

/** 团队B ↔ 团队C 合约版本（语义化版本） */
#define CONTRACT_B_C_VERSION "1.0.0"

/** 版本数值，用于运行时比较 */
#define CONTRACT_B_C_VERSION_MAJOR 1
#define CONTRACT_B_C_VERSION_MINOR 0
#define CONTRACT_B_C_VERSION_PATCH 0

/* ================================================================
 * CLI 退出码规范
 *
 * agentrt CLI（Rust，团队B）必须使用以下退出码。
 * 团队C 的 CI/CD 脚本与 systemd 单元根据退出码判断故障类型。
 *
 * 规范遵循 BSD/Sysexits.h 惯例：
 *   0       成功
 *   1       通用失败
 *   2       命令行参数错误
 *   64-78   sysexits.h 标准错误
 *   80-99   AgentRT 自定义错误
 * ================================================================ */

/** CLI 退出码枚举 */
typedef enum contract_bc_exit_code {
    CONTRACT_BC_EXIT_SUCCESS           = 0,  /**< 成功 */
    CONTRACT_BC_EXIT_GENERIC_ERROR     = 1,  /**< 通用失败 */
    CONTRACT_BC_EXIT_USAGE_ERROR       = 2,  /**< 命令行参数错误 */

    /* sysexits.h 标准错误码（64-78） */
    CONTRACT_BC_EXIT_DATA_ERROR        = 65, /**< 数据错误（配置文件损坏） */
    CONTRACT_BC_EXIT_NO_INPUT          = 66, /**< 输入文件不存在 */
    CONTRACT_BC_EXIT_NO_USER           = 67, /**< 用户不存在 */
    CONTRACT_BC_EXIT_NO_HOST           = 68, /**< 主机不存在 */
    CONTRACT_BC_EXIT_UNAVAILABLE       = 69, /**< 服务不可用 */
    CONTRACT_BC_EXIT_SOFTWARE          = 70, /**< 内部软件错误 */
    CONTRACT_BC_EXIT_OS_ERROR          = 71, /**< 系统错误 */
    CONTRACT_BC_EXIT_OS_FILE           = 72, /**< 系统文件错误 */
    CONTRACT_BC_EXIT_CANT_CREATE       = 73, /**< 无法创建输出 */
    CONTRACT_BC_EXIT_IO_ERROR          = 74, /**< I/O 错误 */
    CONTRACT_BC_EXIT_TEMP_FAIL         = 75, /**< 临时故障 */
    CONTRACT_BC_EXIT_PROTOCOL          = 76, /**< 协议错误 */
    CONTRACT_BC_EXIT_NO_PERM           = 77, /**< 权限不足 */
    CONTRACT_BC_EXIT_CONFIG            = 78, /**< 配置错误 */

    /* AgentRT 自定义错误码（80-99） */
    CONTRACT_BC_EXIT_GATEWAY_UNREACHABLE = 80, /**< Gateway 不可达 */
    CONTRACT_BC_EXIT_GATEWAY_TIMEOUT     = 81, /**< Gateway 超时 */
    CONTRACT_BC_EXIT_AUTH_FAILED         = 82, /**< 认证失败 */
    CONTRACT_BC_EXIT_RATE_LIMITED        = 83, /**< 被限流 */
    CONTRACT_BC_EXIT_AGENT_NOT_FOUND     = 84, /**< Agent 未找到 */
    CONTRACT_BC_EXIT_AGENT_RUN_FAILED    = 85, /**< Agent 运行失败 */
    CONTRACT_BC_EXIT_MARKET_INSTALL_FAIL = 86, /**< 市场安装失败 */
    CONTRACT_BC_EXIT_DB_MIGRATION_FAIL   = 87, /**< 数据库迁移失败 */
    CONTRACT_BC_EXIT_DEPLOY_FAIL         = 88  /**< 部署失败 */
} contract_bc_exit_code_t;

/** 退出码总数（用于团队C 的测试覆盖统计） */
#define CONTRACT_BC_EXIT_CODE_COUNT 28

/**
 * @brief CLI 命令名称（团队C 的测试矩阵依赖此列表）
 *
 * 团队B 的 agentrt CLI 必须实现以下命令。
 * 团队C 为每个命令编写集成测试。
 */
#define CONTRACT_BC_CMD_INIT    "init"     /**< agentrt init — 项目初始化 */
#define CONTRACT_BC_CMD_CREATE  "create"   /**< agentrt create — 创建组件 */
#define CONTRACT_BC_CMD_RUN     "run"      /**< agentrt run — 运行 Agent */
#define CONTRACT_BC_CMD_CONFIG  "config"   /**< agentrt config — 配置管理 */
#define CONTRACT_BC_CMD_LLM     "llm"      /**< agentrt llm — LLM 管理 */
#define CONTRACT_BC_CMD_PROMPT  "prompt"   /**< agentrt prompt — 模板管理 */
#define CONTRACT_BC_CMD_MARKET  "market"   /**< agentrt market — 市场操作 */
#define CONTRACT_BC_CMD_DEPLOY  "deploy"   /**< agentrt deploy — 部署操作 */
#define CONTRACT_BC_CMD_DB      "db"       /**< agentrt db — 数据库迁移 */

/** 需要运行 Gateway 的命令标记（团队C 据此决定是否启动 Gateway） */
#define CONTRACT_BC_CMD_REQUIRES_GATEWAY(cmd) \
    ((cmd) != CONTRACT_BC_CMD_INIT && (cmd) != CONTRACT_BC_CMD_CREATE)

/* ================================================================
 * SDK 测试 Harness 接口
 *
 * 团队C 通过此接口驱动 SDK（Python/Rust/Go/TypeScript）的集成测试。
 * Harness 提供统一的测试夹具管理、断言与报告。
 *
 * 时序约束：
 *   1. 团队C 启动测试环境（docker-compose up）
 *   2. Harness 连接 Gateway，等待健康检查通过
 *   3. 执行测试用例（submit_task / query_memory / ...）
 *   4. 收集结果与指标
 *   5. 清理测试数据
 * ================================================================ */

/** SDK 测试 Harness 默认超时（秒） */
#define CONTRACT_BC_HARNESS_DEFAULT_TIMEOUT_SEC 30

/** Harness 最大并发测试数 */
#define CONTRACT_BC_HARNESS_MAX_CONCURRENT 16

/** Harness 测试名称最大长度 */
#define CONTRACT_BC_HARNESS_TEST_NAME_MAX 128

/** Harness 报告路径环境变量 */
#define CONTRACT_BC_HARNESS_REPORT_ENV "AGENTRT_TEST_REPORT_PATH"

/** Harness 测试模式环境变量（与 contract_A_C.h 对齐） */
#define CONTRACT_BC_HARNESS_TEST_MODE_ENV "AGENTOS_TEST_MODE"

/**
 * @brief SDK 测试 Harness 状态
 */
typedef enum contract_bc_harness_state {
    CONTRACT_BC_HARNESS_IDLE      = 0, /**< 空闲 */
    CONTRACT_BC_HARNESS_SETUP     = 1, /**< 初始化中 */
    CONTRACT_BC_HARNESS_RUNNING   = 2, /**< 运行中 */
    CONTRACT_BC_HARNESS_TEARDOWN  = 3, /**< 清理中 */
    CONTRACT_BC_HARNESS_COMPLETED = 4, /**< 已完成 */
    CONTRACT_BC_HARNESS_FAILED    = 5  /**< 失败 */
} contract_bc_harness_state_t;

/**
 * @brief SDK 测试 Harness 配置
 *
 * 团队C 初始化 Harness 时传入此结构。
 */
typedef struct contract_bc_harness_config {
    const char *gateway_url;        /**< Gateway URL（默认 http://localhost:8080） */
    const char *report_path;        /**< 报告输出路径 */
    uint32_t    timeout_sec;        /**< 单测试超时（秒） */
    uint32_t    max_concurrent;     /**< 最大并发数 */
    uint8_t     enable_metrics;     /**< 是否采集指标 */
    uint8_t     enable_tracing;     /**< 是否采集追踪 */
    uint8_t     reserved[2];        /**< 对齐保留 */
} contract_bc_harness_config_t;

/**
 * @brief SDK 测试结果
 */
typedef struct contract_bc_harness_result {
    char     test_name[CONTRACT_BC_HARNESS_TEST_NAME_MAX]; /**< 测试名称 */
    int32_t  exit_code;             /**< 退出码（contract_bc_exit_code_t） */
    uint64_t duration_ms;           /**< 执行时长（毫秒） */
    uint32_t assertions_total;      /**< 断言总数 */
    uint32_t assertions_passed;     /**< 通过断言数 */
    uint32_t assertions_failed;     /**< 失败断言数 */
} contract_bc_harness_result_t;

/* ================================================================
 * Docker 健康检查端点
 *
 * 团队B 的所有 daemon 必须暴露以下健康检查端点。
 * 团队C 的 Dockerfile HEALTHCHECK 与 docker-compose healthcheck 依赖此端点。
 *
 * 时序约束：
 *   1. daemon 启动后监听 AGENTOS_SERVICE_PORT
 *   2. Docker 每 5-15 秒探测 /healthz
 *   3. 连续 5 次失败标记容器 unhealthy
 *   4. start_period 内的失败不计入
 * ================================================================ */

/** 健康检查端点路径 */
#define CONTRACT_BC_HEALTH_ENDPOINT "/healthz"

/** 就绪检查端点路径 */
#define CONTRACT_BC_READY_ENDPOINT "/readyz"

/** 指标端点路径（Prometheus 采集） */
#define CONTRACT_BC_METRICS_ENDPOINT "/metrics"

/** 默认服务端口环境变量 */
#define CONTRACT_BC_SERVICE_PORT_ENV "AGENTOS_SERVICE_PORT"

/** 默认指标端口环境变量 */
#define CONTRACT_BC_METRICS_PORT_ENV "AGENTOS_METRICS_PORT"

/** 默认 HTTP 端口 */
#define CONTRACT_BC_DEFAULT_HTTP_PORT 8080

/** 默认 WebSocket 端口 */
#define CONTRACT_BC_DEFAULT_WS_PORT 8081

/** 默认指标端口 */
#define CONTRACT_BC_DEFAULT_METRICS_PORT 9090

/** 健康检查默认间隔（秒） */
#define CONTRACT_BC_HEALTH_INTERVAL_SEC 5

/** 健康检查默认超时（秒） */
#define CONTRACT_BC_HEALTH_TIMEOUT_SEC 3

/** 健康检查默认重试次数 */
#define CONTRACT_BC_HEALTH_RETRIES 5

/** 健康检查启动宽限期（秒） */
#define CONTRACT_BC_HEALTH_START_PERIOD_SEC 15

/**
 * @brief 健康检查响应状态
 *
 * 团队B 的 daemon 必须返回此结构（JSON 格式）。
 */
typedef struct contract_bc_health_response {
    const char *status;       /**< "healthy" / "degraded" / "unhealthy" */
    const char *service;      /**< 服务名（如 "gateway_d"） */
    const char *version;      /**< 服务版本 */
    uint64_t    uptime_sec;   /**< 运行时长（秒） */
    uint32_t    reserved;     /**< 对齐保留 */
} contract_bc_health_response_t;

/**
 * @brief 标准 daemon 服务名（团队C 的 docker-compose 依赖）
 *
 * 团队B 的镜像必须按此命名服务。
 */
#define CONTRACT_BC_SERVICE_GATEWAY_D    "gateway_d"
#define CONTRACT_BC_SERVICE_LLM_D        "llm_d"
#define CONTRACT_BC_SERVICE_TOOL_D       "tool_d"
#define CONTRACT_BC_SERVICE_MARKET_D     "market_d"
#define CONTRACT_BC_SERVICE_SCHED_D      "sched_d"
#define CONTRACT_BC_SERVICE_CHANNEL_D    "channel_d"
#define CONTRACT_BC_SERVICE_MONIT_D      "monit_d"
#define CONTRACT_BC_SERVICE_OBSERVE_D    "observe_d"
#define CONTRACT_BC_SERVICE_HOOK_D       "hook_d"
#define CONTRACT_BC_SERVICE_PLUGIN_D     "plugin_d"
#define CONTRACT_BC_SERVICE_INFO_D       "info_d"
#define CONTRACT_BC_SERVICE_NOTIFY_D     "notify_d"
#define CONTRACT_BC_SERVICE_COREKERN     "corekern"
#define CONTRACT_BC_SERVICE_CORELOOPTHREE "coreloopthree"
#define CONTRACT_BC_SERVICE_MEMORY       "memory"
#define CONTRACT_BC_SERVICE_TASKFLOW     "taskflow"

/* ================================================================
 * 编译期验证（#if 0 块，不参与编译，仅作文档与示例）
 * ================================================================ */
#if 0
/* 退出码范围校验 */
static_assert(CONTRACT_BC_EXIT_SUCCESS == 0, "success must be 0");
static_assert(CONTRACT_BC_EXIT_GATEWAY_UNREACHABLE >= 80,
              "custom exit codes must be >= 80");

/* Harness 配置大小校验 */
static_assert(sizeof(contract_bc_harness_config_t) > 0,
              "harness config must be non-empty");

/* 健康检查端点校验 */
static_assert(sizeof(CONTRACT_BC_HEALTH_ENDPOINT) > 0,
              "health endpoint must be non-empty");

/* 团队C 集成示例（伪代码）：
 *
 *   # Bash CI 脚本
 *   agentrt run "test prompt"
 *   rc=$?
 *   if [ $rc -eq $CONTRACT_BC_EXIT_GATEWAY_UNREACHABLE ]; then
 *       echo "Gateway down, starting..."
 *       docker-compose up -d gateway_d
 *   fi
 *
 *   # Python 测试 Harness
 *   harness = TestHarness(config={
 *       "gateway_url": "http://localhost:8080",
 *       "timeout_sec": 30
 *   })
 *   result = harness.run_test("test_agent_run")
 *   assert result.exit_code == CONTRACT_BC_EXIT_SUCCESS
 *
 *   # Docker 健康检查
 *   wget -qO- http://localhost:8080/healthz
 */
#endif

#ifdef __cplusplus
}
#endif

#endif /* AGENTRT_CONTRACT_B_C_H */
