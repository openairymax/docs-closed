/*
 * contract_A_B.h - Team A (C Core) ↔ Team B (Ecosystem/SDK) 接口合约
 *
 * 本合约定义 C 核心引擎与生态/SDK 层之间的所有跨团队接口。
 * 任何变更必须 bump 版本号并通知所有相关团队。
 *
 * 版本: v1.0.0 | 涉及团队: A+B | 创建日期: 2026-06-17
 *
 * Copyright (c) 2026 SPHARX Ltd. All Rights Reserved.
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef AGENTOS_CONTRACT_A_B_H
#define AGENTOS_CONTRACT_A_B_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ======================================================================
 * 1. 版本号
 * ====================================================================== */
#define CONTRACT_A_B_VERSION_MAJOR 1
#define CONTRACT_A_B_VERSION_MINOR 0
#define CONTRACT_A_B_VERSION_PATCH 0

/* ======================================================================
 * 2. C-L03: market_d → OpenLab Markets 接口
 * ====================================================================== */

/**
 * @brief market_d 服务端点定义
 * @details OpenLab Markets 通过 HTTP API 调用 market_d 的 JSON-RPC 端点
 *
 * Team B (ecosystem/openlab/markets/client/market_client.py) 实现：
 *   - POST /api/v1/market/register
 *   - GET  /api/v1/market/search
 *   - POST /api/v1/market/install
 *   - GET  /api/v1/market/health
 *
 * Team A (agentos/daemon/market_d/) 实现 C 侧 JSON-RPC handler
 */
#define MARKET_D_DEFAULT_SOCKET_PATH "/var/run/agentos/market.sock"
#define MARKET_D_DEFAULT_TCP_PORT    8082
#define MARKET_D_DEFAULT_TIMEOUT_SEC 10

/** market_d 错误码映射（C → Python 异常） */
typedef enum {
    MARKET_ERR_NONE            = 0,     /**< 无错误 */
    MARKET_ERR_INVALID_PARAM   = -32602, /**< 无效参数 → MarketValidationError */
    MARKET_ERR_AGENT_NOT_FOUND = -32001, /**< Agent 未找到 → MarketNotFoundError */
    MARKET_ERR_AGENT_EXISTS    = -32002, /**< Agent 已存在 → MarketAlreadyExistsError */
    MARKET_ERR_INSTALL_FAILED  = -32003, /**< 安装失败 → MarketInstallError */
    MARKET_ERR_CONNECTION      = -32004, /**< 连接失败 → MarketConnectionError */
    MARKET_ERR_PERMISSION      = -32005, /**< 权限不足 → MarketPermissionError */
} market_error_code_t;

/* ======================================================================
 * 3. C-L11: gateway_d → gateway 协议路由表
 * ====================================================================== */

/**
 * @brief 协议类型枚举
 * @details gateway_d 根据请求内容自动路由到对应协议处理器
 */
typedef enum {
    PROTOCOL_A2A,      /**< Agent-to-Agent 协议 */
    PROTOCOL_MCP,      /**< Model Context Protocol */
    PROTOCOL_OPENAI,   /**< OpenAI 兼容 API */
    PROTOCOL_JSON_RPC, /**< 内部 JSON-RPC 2.0 */
    PROTOCOL_COUNT
} protocol_type_t;

/**
 * @brief 协议路由入口
 * @details gateway_d 的协议路由表。Team B 的 CLI/TUI 通过 HTTP 调用 gateway
 */
typedef struct {
    protocol_type_t type;
    const char *path_prefix;     /**< URL 路径前缀，如 "/api/v1/a2a/" */
    const char *handler_name;    /**< C 侧 handler 函数名 */
    bool requires_auth;          /**< 是否需要认证 */
} protocol_route_entry_t;

/* ======================================================================
 * 4. C-L12: CoreLoopThree → MemoryRovol 内存布局
 * ====================================================================== */

/**
 * @brief 记忆提供商操作表
 * @details CoreLoopThree 通过此接口调用记忆层（内置或 MemoryRovol）
 */
typedef struct {
    int (*init)(const char *config_path);
    int (*shutdown)(void);
    int (*store)(const char *key, const void *data, size_t data_len);
    int (*query)(const char *query_text, void *results, size_t *results_len);
    int (*delete)(const char *key);
    int (*health)(void);
} memory_provider_ops_t;

/** 记忆构建模式 */
typedef enum {
    AGENTOS_MEMORY_BUILTIN,     /**< 内置模式（开源） */
    AGENTOS_MEMORY_MEMORYROVOL, /**< MemoryRovol 模式（商业） */
    AGENTOS_MEMORY_HYBRID       /**< 混合模式 */
} memory_build_mode_t;

/* ======================================================================
 * 5. Hook 系统事件类型（C-L05-HOOK 扩展）
 * ====================================================================== */

/**
 * @brief Hook 事件类型
 * @details Team B 的 Python/Rust Hook 实现监听这些事件
 */
typedef enum {
    HOOK_EVENT_AGENT_INIT,      /**< Agent 初始化 */
    HOOK_EVENT_AGENT_START,     /**< Agent 开始执行 */
    HOOK_EVENT_TOOL_CALL,       /**< 工具调用前（可拦截） */
    HOOK_EVENT_TOOL_RESULT,     /**< 工具调用后 */
    HOOK_EVENT_LLM_REQUEST,     /**< LLM 请求发送前 */
    HOOK_EVENT_LLM_RESPONSE,    /**< LLM 响应接收后 */
    HOOK_EVENT_LLM_ERROR,       /**< LLM 调用失败 */
    HOOK_EVENT_AGENT_STOP,      /**< Agent 停止 */
    HOOK_EVENT_AGENT_DESTROY,   /**< Agent 销毁 */
    HOOK_EVENT_COUNT
} hook_event_type_t;

/**
 * @brief Hook 类型
 * @details Team B 实现三种 Hook 模式
 */
typedef enum {
    AGENTOS_HOOK_TYPE_SHELL,    /**< Shell 脚本 Hook */
    AGENTOS_HOOK_TYPE_PYTHON,   /**< Python 脚本 Hook */
    AGENTOS_HOOK_TYPE_WEBHOOK,  /**< HTTP Webhook */
    AGENTOS_HOOK_TYPE_RUST,     /**< Rust 编译型 Hook */
} agentos_hook_type_t;

/** Hook 执行超时（秒） */
#define AGENTOS_HOOK_TIMEOUT_SEC 5

/* ======================================================================
 * 6. Plugin SDK Manifest 格式
 * ====================================================================== */

/**
 * @brief 四型插件类型
 * @details Team B 的 Python/Rust SDK 实现这四种插件基类
 */
typedef enum {
    AGENTOS_PLUGIN_TYPE_AGENT,  /**< AgentPlugin — 扩展智能体能力 */
    AGENTOS_PLUGIN_TYPE_TOOL,   /**< ToolPlugin — 提供自定义工具 */
    AGENTOS_PLUGIN_TYPE_HOOK,   /**< HookPlugin — 拦截生命周期事件 */
    AGENTOS_PLUGIN_TYPE_SKILL,  /**< SkillPlugin — 注册可复用技能 */
} agentos_plugin_type_t;

/* ======================================================================
 * 7. CLI 退出码规范
 * ====================================================================== */

/**
 * @brief CLI 退出码
 * @details Team B 的 CLI (sdk/cli/) 统一使用这些退出码
 * Team C 的 CI 集成测试检查这些退出码
 */
#define CLI_EXIT_SUCCESS          0   /**< 成功 */
#define CLI_EXIT_ERROR            1   /**< 通用错误 */
#define CLI_EXIT_CONFIG_ERROR     2   /**< 配置错误 */
#define CLI_EXIT_NETWORK_ERROR    3   /**< 网络/连接错误 */
#define CLI_EXIT_TIMEOUT          4   /**< 超时 */
#define CLI_EXIT_PERMISSION       5   /**< 权限不足 */
#define CLI_EXIT_INVALID_INPUT    6   /**< 无效输入 */
#define CLI_EXIT_DAEMON_ERROR     7   /**< 守护进程错误 */
#define CLI_EXIT_CANCELLED        8   /**< 用户取消 */
#define CLI_EXIT_PANIC            9   /**< 未预期 panic */

/* ======================================================================
 * 8. HTTP API 端点（gateway → CLI/TUI/SDK）
 * ====================================================================== */

/** Gateway 默认端口 */
#define GATEWAY_DEFAULT_PORT 8080

/** Gateway API 端点 */
#define GATEWAY_API_RUN_AGENT     "/api/v1/agent/run"
#define GATEWAY_API_AGENT_STATUS  "/api/v1/agent/status"
#define GATEWAY_API_CONFIG_GET    "/api/v1/config"
#define GATEWAY_API_CONFIG_RELOAD "/api/v1/config/reload"
#define GATEWAY_API_LLM_LIST      "/api/v1/llm/providers"
#define GATEWAY_API_LLM_TEST      "/api/v1/llm/test"
#define GATEWAY_API_LLM_COST      "/api/v1/llm/cost"
#define GATEWAY_API_MARKET_SEARCH "/api/v1/market/search"
#define GATEWAY_API_MARKET_INSTALL "/api/v1/market/install"
#define GATEWAY_API_HEALTH        "/api/v1/health"
#define GATEWAY_API_METRICS       "/metrics"

#ifdef __cplusplus
}
#endif

#endif /* AGENTOS_CONTRACT_A_B_H */