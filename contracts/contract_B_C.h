/*
 * contract_B_C.h - Team B (Ecosystem/SDK) ↔ Team C (CI/CD/Infrastructure) 接口合约
 *
 * 本合约定义生态/SDK 层与基础设施/CI/CD 层之间的所有跨团队接口。
 * 任何变更必须 bump 版本号并通知所有相关团队。
 *
 * 版本: v1.0.0 | 涉及团队: B+C | 创建日期: 2026-06-17
 *
 * Copyright (c) 2026 SPHARX Ltd. All Rights Reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef AGENTOS_CONTRACT_B_C_H
#define AGENTOS_CONTRACT_B_C_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ======================================================================
 * 1. 版本号
 * ====================================================================== */
#define CONTRACT_B_C_VERSION_MAJOR 1
#define CONTRACT_B_C_VERSION_MINOR 0
#define CONTRACT_B_C_VERSION_PATCH 0

/* ======================================================================
 * 2. CLI 退出码规范（同 contract_A_B.h §7，此为 Team C 验证侧）
 * ====================================================================== */

/**
 * @brief CLI 退出码 — Team C CI 集成测试验证
 * @details Team B 的 CLI 实现这些退出码，Team C 的 CI 测试验证
 */
#define B_C_CLI_EXIT_SUCCESS          0
#define B_C_CLI_EXIT_ERROR            1
#define B_C_CLI_EXIT_CONFIG_ERROR     2
#define B_C_CLI_EXIT_NETWORK_ERROR    3
#define B_C_CLI_EXIT_TIMEOUT          4
#define B_C_CLI_EXIT_PERMISSION       5
#define B_C_CLI_EXIT_INVALID_INPUT    6
#define B_C_CLI_EXIT_DAEMON_ERROR     7
#define B_C_CLI_EXIT_CANCELLED        8
#define B_C_CLI_EXIT_PANIC            9

/* ======================================================================
 * 3. SDK 测试 Harness 接口
 * ====================================================================== */

/**
 * @brief 测试结果结构
 * @details Team B 的 SDK 测试输出此结构，Team C 的 CI 解析
 */
typedef struct {
    const char *sdk_name;        /**< SDK 名称: "python" | "rust" | "go" | "typescript" */
    const char *sdk_version;     /**< SDK 版本号 */
    int total_tests;             /**< 总测试数 */
    int passed_tests;            /**< 通过测试数 */
    int failed_tests;            /**< 失败测试数 */
    int skipped_tests;           /**< 跳过测试数 */
    double duration_sec;         /**< 测试耗时（秒） */
    const char *output_path;     /**< JUnit XML 输出路径 */
} sdk_test_result_t;

/**
 * @brief 编译验证结果
 * @details Team C 的 CI 验证四种 SDK 均可编译/导入
 */
typedef struct {
    const char *sdk_name;
    bool build_success;          /**< 编译是否成功 */
    const char *build_command;   /**< 编译命令 */
    const char *build_log;       /**< 编译日志路径 */
    double duration_sec;
} sdk_build_result_t;

/** 四语言 SDK 标识 */
#define B_C_SDK_PYTHON     "python"
#define B_C_SDK_RUST       "rust"
#define B_C_SDK_GO         "go"
#define B_C_SDK_TYPESCRIPT "typescript"

/* ======================================================================
 * 4. Docker 健康检查端点
 * ====================================================================== */

/**
 * @brief 健康检查端点规范
 * @details Team B 的 ecosystem 服务暴露这些端点，Team C 的 Docker Compose 检查
 */
#define B_C_HEALTH_CHECK_ENDPOINT  "/api/v1/health"
#define B_C_HEALTH_CHECK_TIMEOUT   5      /**< 健康检查超时（秒） */
#define B_C_HEALTH_CHECK_INTERVAL  10     /**< 健康检查间隔（秒） */
#define B_C_HEALTH_CHECK_RETRIES   3      /**< 最大重试次数 */

/**
 * @brief 健康检查响应格式
 */
typedef struct {
    bool healthy;                /**< 服务是否健康 */
    const char *service_name;    /**< 服务名称 */
    const char *version;         /**< 版本号 */
    double uptime_sec;           /**< 运行时间（秒） */
    const char *timestamp;       /**< 检查时间戳 ISO 8601 */
} health_check_response_t;

/* ======================================================================
 * 5. TUI 测试自动化接口
 * ====================================================================== */

/**
 * @brief TUI 面板标识
 * @details Team C 的 TUI 自动化测试通过按键切换面板
 */
typedef enum {
    B_C_TUI_PANEL_CHAT,     /**< F1: Chat 面板 */
    B_C_TUI_PANEL_CONFIG,   /**< F2: Config 面板 */
    B_C_TUI_PANEL_LOGS,     /**< F3: Logs 面板 */
    B_C_TUI_PANEL_MEMORY,   /**< F4: Memory 面板 */
    B_C_TUI_PANEL_PLUGINS,  /**< F5: Plugins 面板 */
    B_C_TUI_PANEL_COUNT
} b_c_tui_panel_t;

/**
 * @brief TUI 状态栏指标
 * @details Team C 的测试验证状态栏显示正确
 */
typedef struct {
    int current_turn;            /**< 当前轮次 */
    int total_tokens;            /**< 累计 Token 数 */
    double cost_usd;             /**< 累计费用（美元） */
    double elapsed_sec;          /**< 已用时间（秒） */
} b_c_tui_status_t;

/* ======================================================================
 * 6. Prompt 调优评测数据集接口
 * ====================================================================== */

/**
 * @brief Prompt 评测指标
 * @details Team B 的 tuner 输出这些指标，Team C 的评测数据集验证
 */
typedef struct {
    const char *prompt_name;     /**< Prompt 模板名称 */
    const char *prompt_version;  /**< 版本号 */
    double precision;            /**< 精确率 */
    double recall;               /**< 召回率 */
    double f1_score;             /**< F1 分数 */
    double hallucination_rate;   /**< 幻觉率 */
    double latency_p50_ms;       /**< P50 延迟（毫秒） */
    double latency_p99_ms;       /**< P99 延迟（毫秒） */
    int total_samples;           /**< 总样本数 */
} prompt_eval_metrics_t;

/** 实体提取精度最低阈值 */
#define B_C_ENTITY_EXTRACT_MIN_PRECISION 0.85

/** A/B 测试结果 */
typedef struct {
    const char *baseline_version;    /**< 基线版本 */
    const char *candidate_version;   /**< 候选版本 */
    double p_value;                  /**< 统计显著性 p 值 */
    double effect_size;              /**< 效应量 */
    const char *winner;              /**< 胜出者: "baseline" | "candidate" | "tie" */
    const char *recommendation;      /**< 推荐说明 */
} prompt_ab_test_result_t;

/* ======================================================================
 * 7. CI/CD 质量门禁接口
 * ====================================================================== */

/**
 * @brief 质量门禁检查项
 * @details Team C 的 CI pipeline 检查这些项，Team B 确保通过
 */
typedef enum {
    B_C_GATE_PYTHON_TEST,       /**< Python 测试全部通过 */
    B_C_GATE_RUST_BUILD,        /**< Rust 编译通过 */
    B_C_GATE_GO_BUILD,          /**< Go 编译通过 */
    B_C_GATE_TS_BUILD,          /**< TypeScript 编译通过 */
    B_C_GATE_BAN_PYTHON,        /**< Python BAN 规则零违规 */
    B_C_GATE_BAN_RUST,          /**< Rust BAN 规则零违规 */
    B_C_GATE_COUNT
} b_c_quality_gate_t;

/** 质量门禁结果 */
typedef struct {
    b_c_quality_gate_t gate;
    bool passed;
    const char *details;         /**< 通过/失败详情 */
    const char *fix_command;     /**< 修复命令（如适用） */
} b_c_gate_result_t;

/* ======================================================================
 * 8. QuickStart 脚本合约
 * ====================================================================== */

/**
 * @brief QuickStart 验证标准
 * @details Team B 提供 QuickStart 脚本，Team C 的 CI 验证
 */
#define B_C_QUICKSTART_SCRIPT    "scripts/quickstart.sh"
#define B_C_QUICKSTART_TIMEOUT   300  /**< 5 分钟超时 */
#define B_C_QUICKSTART_EXPECTED_OUTPUT "AgentRT is ready"

/* ======================================================================
 * 9. 示例项目测试接口
 * ====================================================================== */

/** 示例项目列表 */
#define B_C_EXAMPLE_HELLO_AGENT           "hello-agent"
#define B_C_EXAMPLE_WEATHER_AGENT         "weather-agent"
#define B_C_EXAMPLE_CODE_REVIEW_AGENT     "code-review-agent"
#define B_C_EXAMPLE_RESEARCH_AGENT        "research-agent"
#define B_C_EXAMPLE_CUSTOMER_SUPPORT      "customer-support-agent"
#define B_C_EXAMPLE_PLUGIN_DEMO           "plugin-demo"
#define B_C_EXAMPLE_PROMPT_TUNER          "prompt-tuner-demo"
#define B_C_EXAMPLE_MULTI_AGENT_DEBATE    "multi-agent-debate"
#define B_C_EXAMPLE_A2A_CHAT             "a2a-chat"
#define B_C_EXAMPLE_MCP_TOOL_SERVER       "mcp-tool-server"

/** 示例项目验证结果 */
typedef struct {
    const char *example_name;
    bool has_readme;             /**< 是否有 README.md */
    bool has_config;             /**< 是否有 config.yaml */
    bool runs_successfully;      /**< 是否能运行 */
    const char *error_message;   /**< 错误信息（如有） */
} b_c_example_validation_t;

#ifdef __cplusplus
}
#endif

#endif /* AGENTOS_CONTRACT_B_C_H */