// SPDX-FileCopyrightText: 2026 SPHARX Ltd.
// SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0
/**
 * @file contract_A_B.h
 * @brief 跨团队接口合约：团队A（核心引擎 C）↔ 团队B（生态 + SDK）
 *
 * 本合约固化团队A 与团队B 之间的四条关键连接线（C-L01 / C-L03 / C-L11 / C-L12）
 * 的二进制布局、消息格式与时序约束。任何一方修改实现前必须先升级本合约版本号，
 * 并通过 contracts/contract_test.c 编译验证。
 *
 * 连接线清单：
 *   - C-L01: Manager (Python, 团队B) → CoreLoopThree (C, 团队A) 配置消息
 *   - C-L03: market_d (C, 团队A) → OpenLab Markets (Python, 团队B) HTTP API
 *   - C-L11: gateway_d (C, 团队A) → gateway 协议路由表（团队B 维护路由配置）
 *   - C-L12: CoreLoopThree (C, 团队A) → MemoryRovol 内存提供商接口（团队B 集成）
 *
 * 参考实现：
 *   - agentrt/atoms/coreloopthree/include/manager_adapter.h
 *   - agentrt/daemon/market_d/include/market_service.h
 *   - agentrt/daemon/gateway_d/include/gateway_forward.h
 *   - agentrt/atoms/memory/src/memory_provider.h
 *   - agentrt/atoms/coreloopthree/include/memoryrovol_bridge.h
 *
 * @owner team-A, team-B
 * @version 1.0.0
 * @see P0.14 跨团队合约任务
 */

#ifndef AGENTRT_CONTRACT_A_B_H
#define AGENTRT_CONTRACT_A_B_H
#pragma once

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ================================================================
 * 合约版本
 * ================================================================ */

/** 团队A ↔ 团队B 合约版本（语义化版本） */
#define CONTRACT_A_B_VERSION "1.0.0"

/** 版本数值，用于运行时比较 */
#define CONTRACT_A_B_VERSION_MAJOR 1
#define CONTRACT_A_B_VERSION_MINOR 0
#define CONTRACT_A_B_VERSION_PATCH 0

/* ================================================================
 * C-L01: Manager → CoreLoopThree 配置消息格式
 *
 * 时序约束：
 *   1. Manager 生成/修改 agentrt.yaml
 *   2. Manager 调用 manager_adapter_reload() 触发热重载
 *   3. config_loader 检测文件变更 → yaml_loader 解析
 *   4. 回调通知 CoreLoopThree 更新运行时配置
 *
 * 团队A 负责：CoreLoopThree 侧的配置消费与回调注册
 * 团队B 负责：Manager 侧的配置生成与 reload 触发
 * ================================================================ */

/** C-L01: 配置消息魔数，用于跨进程校验 */
#define CONTRACT_CL01_MAGIC 0x4C30314DU /* "L01M" */

/** C-L01: 配置消息版本 */
#define CONTRACT_CL01_VERSION 1

/** C-L01: 配置路径最大长度（与 manager_adapter 内部 g_config_path[256] 对齐） */
#define CONTRACT_CL01_CONFIG_PATH_MAX 256

/** C-L01: 热重载回调最大数量（与 AIRY_MAX_RELOAD_CALLBACKS 对齐） */
#define CONTRACT_CL01_MAX_RELOAD_CALLBACKS 32

/** C-L01: 默认配置文件路径 */
#define CONTRACT_CL01_DEFAULT_CONFIG_PATH "./configs/agentrt.yaml"

/** C-L01: 默认配置监听间隔（毫秒，与 AIRY_CONFIG_WATCH_INTERVAL_MS 对齐） */
#define CONTRACT_CL01_WATCH_INTERVAL_MS 1000

/**
 * @brief C-L01: Manager → CoreLoopThree 配置消息头
 *
 * Manager 通过此消息头通知 CoreLoopThree 配置已变更。
 * 二进制布局必须保持稳定，跨团队不得随意修改字段顺序与类型。
 */
typedef struct contract_cl01_config_msg {
    uint32_t magic;       /**< 魔数 CONTRACT_CL01_MAGIC */
    uint32_t version;     /**< 消息版本 CONTRACT_CL01_VERSION */
    uint64_t timestamp;   /**< 配置变更时间戳（Unix 毫秒） */
    uint32_t config_size; /**< 配置内容字节数（不含本头） */
    uint32_t reserved;    /**< 8 字节对齐保留 */
    char config_path[CONTRACT_CL01_CONFIG_PATH_MAX]; /**< 配置文件路径 */
} contract_cl01_config_msg_t;

/**
 * @brief C-L01: 配置变更回调签名
 *
 * 团队A 在 CoreLoopThree 中注册此回调，团队B 的 Manager 触发重载后调用。
 * @param old_path 旧配置路径（BORROW，回调内不可修改）
 * @param new_path 新配置路径（BORROW，回调内不可修改）
 * @param user_data 团队A 注册时传入的用户数据
 */
typedef void (*contract_cl01_config_change_cb_t)(const char *old_path,
                                                 const char *new_path,
                                                 void *user_data);

/* ================================================================
 * C-L03: market_d → OpenLab Markets HTTP API 定义
 *
 * 时序约束：
 *   1. OpenLab Markets (Python, 团队B) 通过 Unix Socket / TCP 调用 market_d
 *   2. market_d (C, 团队A) 处理注册/搜索/安装请求
 *   3. 响应通过 JSON-RPC 2.0 返回
 *
 * 团队A 负责：market_d 守护进程的 RPC 方法实现
 * 团队B 负责：OpenLab Markets 客户端与 HTTP 端点映射
 * ================================================================ */

/** C-L03: market_d 默认 Unix Socket 路径 */
#define CONTRACT_CL03_DEFAULT_SOCKET_PATH "/var/run/agentrt/market.sock"

/** C-L03: market_d 默认 TCP 端口 */
#define CONTRACT_CL03_DEFAULT_TCP_PORT 8082

/** C-L03: market_d 默认 TCP 主机 */
#define CONTRACT_CL03_DEFAULT_TCP_HOST "127.0.0.1"

/** C-L03: 默认请求超时（秒） */
#define CONTRACT_CL03_DEFAULT_TIMEOUT_SEC 10

/** C-L03: 最大缓冲区大小 */
#define CONTRACT_CL03_MAX_BUFFER 65536

/** C-L03: Agent ID 最大长度 */
#define CONTRACT_CL03_AGENT_ID_MAX 128

/** C-L03: Agent 名称最大长度 */
#define CONTRACT_CL03_AGENT_NAME_MAX 128

/** C-L03: 版本字符串最大长度 */
#define CONTRACT_CL03_VERSION_MAX 32

/** C-L03: HTTP API 基础路径 */
#define CONTRACT_CL03_API_BASE "/api/v1/market"

/**
 * @brief C-L03: HTTP 端点定义（market_d 暴露给 OpenLab Markets）
 *
 * 团队B 的 MarketClient 必须严格按此表构造 HTTP 请求。
 */
#define CONTRACT_CL03_EP_REGISTER_AGENT  CONTRACT_CL03_API_BASE "/register"  /* POST: 注册 Agent */
#define CONTRACT_CL03_EP_SEARCH_AGENTS   CONTRACT_CL03_API_BASE "/search"    /* GET:  搜索 Agent */
#define CONTRACT_CL03_EP_INSTALL_AGENT   CONTRACT_CL03_API_BASE "/install"   /* POST: 安装 Agent */
#define CONTRACT_CL03_EP_PUBLISH         CONTRACT_CL03_API_BASE "/publish"   /* POST: 发布到市场 */
#define CONTRACT_CL03_EP_HEALTH          CONTRACT_CL03_API_BASE "/health"    /* GET:  健康检查 */

/**
 * @brief C-L03: market_d 错误码（与 market_service.h / main.c 对齐）
 *
 * 团队B 的 errors.py 必须与此表保持一致。
 */
#define CONTRACT_CL03_ERR_INVALID_PARAM  (-1000)
#define CONTRACT_CL03_ERR_OUT_OF_MEMORY  (-1001)
#define CONTRACT_CL03_ERR_NOT_FOUND      (-1002)
#define CONTRACT_CL03_ERR_ALREADY_EXISTS (-1003)
#define CONTRACT_CL03_ERR_INSTALL_FAIL   (-1004)

/**
 * @brief C-L03: Agent 信息结构（与 agent_info_t 字段对齐）
 *
 * 团队B 的 AgentInfo dataclass 必须与此结构字段一一对应。
 * 注意：C 端使用 char* 指针（堆分配），Python 端使用 str。
 */
typedef struct contract_cl03_agent_info {
    char    agent_id[CONTRACT_CL03_AGENT_ID_MAX];   /**< Agent ID */
    char    name[CONTRACT_CL03_AGENT_NAME_MAX];      /**< Agent 名称 */
    char    version[CONTRACT_CL03_VERSION_MAX];      /**< 版本 */
    char    description[256];                        /**< 描述 */
    int32_t type;                                    /**< Agent 类型（agent_type_t） */
    int32_t status;                                  /**< Agent 状态（agent_status_t） */
    char    author[64];                              /**< 作者 */
    char    repository[256];                         /**< 仓库地址 */
    char    dependencies[256];                       /**< 依赖项 */
    float   rating;                                  /**< 评分 */
    uint32_t download_count;                         /**< 下载次数 */
    uint64_t last_updated;                           /**< 最后更新时间 */
} contract_cl03_agent_info_t;

/* ================================================================
 * C-L11: gateway_d → gateway 协议路由表
 *
 * 时序约束：
 *   1. 外部 HTTP 请求到达 gateway（团队B 维护协议转换层）
 *   2. gateway 调用 gateway_d 的 gw_forward_request()
 *   3. gateway_d 根据协议类型路由到目标 daemon
 *   4. 响应原路返回
 *
 * 团队A 负责：gateway_d 的转发实现（gw_forward_*）
 * 团队B 负责：gateway 协议转换层与路由配置注入
 * ================================================================ */

/** C-L11: 转发协议类型数量（与 GW_FWD_PROTO_COUNT 对齐） */
#define CONTRACT_CL11_PROTO_COUNT 4

/** C-L11: 默认请求超时（毫秒） */
#define CONTRACT_CL11_DEFAULT_TIMEOUT_MS 30000

/**
 * @brief C-L11: 协议类型枚举（与 gw_fwd_proto_t 对齐）
 *
 * 团队B 的路由配置必须使用此枚举值。
 */
typedef enum contract_cl11_proto {
    CONTRACT_CL11_PROTO_A2A    = 0, /**< A2A Agent-to-Agent 协议 */
    CONTRACT_CL11_PROTO_MCP    = 1, /**< MCP Model Context Protocol */
    CONTRACT_CL11_PROTO_OPENAI = 2, /**< OpenAI 兼容 API */
    CONTRACT_CL11_PROTO_JSONRPC = 3 /**< JSON-RPC 通用协议 */
} contract_cl11_proto_t;

/**
 * @brief C-L11: 协议路由表项
 *
 * 每种协议映射到一个目标 daemon 与 IPC 通道。
 * 团队B 通过此表配置 gateway 的路由策略。
 */
typedef struct contract_cl11_route_entry {
    contract_cl11_proto_t proto;     /**< 协议类型 */
    const char *target_daemon;       /**< 目标 daemon 名称 */
    const char *ipc_channel;         /**< IPC 通道名称 */
    uint32_t    timeout_ms;          /**< 该协议超时（毫秒） */
} contract_cl11_route_entry_t;

/**
 * @brief C-L11: 默认路由表（与 GW_FORWARD_CONFIG_DEFAULTS 对齐）
 *
 * 团队B 必须按此表配置 gateway 路由：
 *   A2A     → sched_d  (channel "a2a")
 *   MCP     → tool_d   (channel "mcp")
 *   OpenAI  → llm_d    (channel "llm")
 *   JSONRPC → sched_d  (channel "sched")
 */
static const contract_cl11_route_entry_t
    CONTRACT_CL11_DEFAULT_ROUTES[CONTRACT_CL11_PROTO_COUNT] = {
        {CONTRACT_CL11_PROTO_A2A, "sched_d", "a2a", CONTRACT_CL11_DEFAULT_TIMEOUT_MS},
        {CONTRACT_CL11_PROTO_MCP, "tool_d", "mcp", CONTRACT_CL11_DEFAULT_TIMEOUT_MS},
        {CONTRACT_CL11_PROTO_OPENAI, "llm_d", "llm", CONTRACT_CL11_DEFAULT_TIMEOUT_MS},
        {CONTRACT_CL11_PROTO_JSONRPC, "sched_d", "sched", CONTRACT_CL11_DEFAULT_TIMEOUT_MS},
};

/* ================================================================
 * C-L12: CoreLoopThree → MemoryRovol 内存布局
 *
 * 时序约束：
 *   1. CoreLoopThree (团队A) 通过 airy_memory_provider_t 接口访问记忆
 *   2. MemoryRovol (团队B 集成) 实现同一接口，作为商业提供商
 *   3. 桥接层 memoryrovol_bridge 在构建时选择内置/MemoryRovol/混合模式
 *
 * 团队A 负责：airy_memory_provider_t 接口定义与消费
 * 团队B 负责：MemoryRovol 提供商实现与构建集成
 * ================================================================ */

/** C-L12: 提供商名称最大长度（与 provider_name[64] 对齐） */
#define CONTRACT_CL12_PROVIDER_NAME_MAX 64

/** C-L12: 提供商版本最大长度（与 provider_version[32] 对齐） */
#define CONTRACT_CL12_PROVIDER_VERSION_MAX 32

/** C-L12: 内置提供商名称 */
#define CONTRACT_CL12_BUILTIN_NAME "builtin"

/** C-L12: MemoryRovol 提供商名称 */
#define CONTRACT_CL12_MEMORYROVOL_NAME "MemoryRovol"

/** C-L12: MemoryRovol 提供商版本 */
#define CONTRACT_CL12_MEMORYROVOL_VERSION "2.0.0"

/** C-L12: 默认存储路径 */
#define CONTRACT_CL12_DEFAULT_STORAGE_PATH "/var/lib/agentrt/memoryrovol"

/** C-L12: 默认查询结果数量上限 */
#define CONTRACT_CL12_DEFAULT_QUERY_LIMIT 10

/** C-L12: 默认同步间隔（毫秒） */
#define CONTRACT_CL12_DEFAULT_SYNC_INTERVAL_MS 5000

/**
 * @brief C-L12: 提供商能力标记（与 airy_memory_capabilities_t 对齐）
 *
 * 团队B 的 MemoryRovol 实现必须填充此结构。
 * 内置提供商仅支持 L1+L2，MemoryRovol 支持 L1-L4 全功能。
 */
typedef struct contract_cl12_capabilities {
    uint8_t l1_raw;          /**< L1 原始存储 */
    uint8_t l2_feature;      /**< L2 特征提取/向量索引 */
    uint8_t l3_structure;    /**< L3 结构绑定/知识图谱 */
    uint8_t l4_pattern;      /**< L4 模式识别 */
    uint8_t forgetting;      /**< 遗忘引擎 */
    uint8_t attractor;       /**< 吸引子网络 */
    uint8_t persistence;     /**< 持久同调 */
    uint8_t faiss;           /**< FAISS 加速索引 */
    uint8_t async_ops;       /**< 异步操作 */
    uint8_t llm_integration; /**< LLM 集成 */
    uint8_t reserved[5];     /**< 保留字段（必须置零） */
} contract_cl12_capabilities_t;

/**
 * @brief C-L12: 内存统计信息（与 airy_memory_stats_t 对齐）
 *
 * 团队A 通过此结构查询提供商运行时状态。
 */
typedef struct contract_cl12_memory_stats {
    uint64_t total_records;       /**< 总记录数 */
    uint64_t total_bytes;         /**< 总字节数 */
    uint64_t l1_count;            /**< L1 记录数 */
    uint64_t l2_indexed;          /**< L2 已索引数 */
    uint64_t l3_relations;        /**< L3 关系数 */
    uint64_t l4_patterns;         /**< L4 模式数 */
    double   index_utilization;   /**< 索引利用率 */
    char     provider_name[CONTRACT_CL12_PROVIDER_NAME_MAX];    /**< 提供商名称 */
    char     provider_version[CONTRACT_CL12_PROVIDER_VERSION_MAX]; /**< 提供商版本 */
} contract_cl12_memory_stats_t;

/**
 * @brief C-L12: 提供商类型枚举（与 mrb_provider_type_t 对齐）
 */
typedef enum contract_cl12_provider_type {
    CONTRACT_CL12_PROVIDER_BUILTIN    = 0, /**< 内置免费提供商 */
    CONTRACT_CL12_PROVIDER_MEMORYROVOL = 1, /**< MemoryRovol 商业提供商 */
    CONTRACT_CL12_PROVIDER_HYBRID     = 2, /**< 混合模式 */
    CONTRACT_CL12_PROVIDER_AUTO       = 3  /**< 自动选择 */
} contract_cl12_provider_type_t;

/* ================================================================
 * 编译期验证（#if 0 块，不参与编译，仅作文档与示例）
 * ================================================================ */
#if 0
/* C-L01 配置消息大小校验：256 + 24 = 280 字节 */
static_assert(sizeof(contract_cl01_config_msg_t) == 280,
              "C-L01 config message size mismatch");

/* C-L03 Agent 信息结构校验 */
static_assert(sizeof(contract_cl03_agent_info_t) > 0,
              "C-L03 agent_info must be non-empty");

/* C-L11 默认路由表项数校验 */
static_assert(sizeof(CONTRACT_CL11_DEFAULT_ROUTES) /
                  sizeof(CONTRACT_CL11_DEFAULT_ROUTES[0]) ==
              CONTRACT_CL11_PROTO_COUNT,
              "C-L11 default routes count mismatch");

/* C-L12 能力标记大小校验：15 字节（10 + 5 保留） */
static_assert(sizeof(contract_cl12_capabilities_t) == 15,
              "C-L12 capabilities size mismatch");

/* C-L12 统计结构校验 */
static_assert(sizeof(contract_cl12_memory_stats_t) > 0,
              "C-L12 memory_stats must be non-empty");

/* 团队B 集成示例（伪代码）：
 *
 *   // Python 侧 MarketClient 构造 HTTP 请求
 *   client.post(CONTRACT_CL03_EP_REGISTER_AGENT, agent_info_json)
 *
 *   // Rust 侧 GatewayClient 转发
 *   gateway.forward(CONTRACT_CL11_PROTO_OPENAI, method, path, body)
 *
 *   // C 侧 MemoryRovol 填充能力标记
 *   caps.l1_raw = 1; caps.l2_feature = 1;
 *   caps.l3_structure = 1; caps.l4_pattern = 1;
 */
#endif

#ifdef __cplusplus
}
#endif

#endif /* AGENTRT_CONTRACT_A_B_H */
