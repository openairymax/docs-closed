# Orchestrator 子系统边界文档

> **版本**: v1.0.0 | **日期**: 2026-06-18 | **团队**: A（流程编排）
> **代码路径**: `agentrt/daemons/common/`（`orchestrator.h` / `orchestrator.c`）

---

## 1. 职责边界

Orchestrator 是 AgentRT 的流程编排器，负责多 Agent 协作任务的全生命周期管理。它实现 4 大多智能体协作模式中的 **Orchestrator 模式**：将复杂任务分解为子任务，按阶段管线串行执行，汇聚结果并进行质量评估与修正。

### 核心职责

| 模块 | 职责 | 源文件 |
|------|------|--------|
| **编排器核心** | 编排器实例创建/销毁，配置管理，任务表维护，进度回调，统计计数 | `src/orchestrator.c` |
| **管线执行引擎** | Phase 0-6 串行执行管线，子任务分发，结果聚合，超时控制，重试机制 | `src/orchestrator.c` |
| **Phase 0: 任务分解** | 将输入任务分解为子任务列表，支持认知引擎优先/LLM 回退双路径 | `src/orchestrator.c` |
| **Phase 1: 计划制定** | 基于分解结果生成执行计划，声明步骤依赖关系 | `src/orchestrator.c` |
| **Phase 2: 内容生成** | 执行计划生成最终输出，支持 T2 流式生成 + T1-F 快速验证循环 | `src/orchestrator.c` |
| **Phase 3: 批判评估** | S1 元认知多轮批判循环，评估输出质量，自动修正或升级 | `src/orchestrator.c` |
| **Phase 4: 验证** | T1-F 快速验证代理评分，不通过时自动修正 | `src/orchestrator.c` |
| **Phase 5: 审计** | T1-P 专家审计代理检查正确性、完整性、安全性 | `src/orchestrator.c` |
| **Phase 6: 对齐** | 多维度对齐评分（逻辑/事实/目标），漂移检测，历史趋势追踪 | `src/orchestrator.c` |
| **管线定义** | 自定义管线创建/步骤添加/条件执行，支持串行/并行/条件/循环/自适应五种策略 | `src/orchestrator.c` |
| **认知引擎集成** | 集成 CoreLoopThree 认知引擎用于任务分解和生成增强 | `src/orchestrator.c` |
| **Memory Provider 集成** | 记忆查询/写入/检索/演化，为各阶段提供上下文增强 | `src/orchestrator.c` |
| **元认知集成** | 批判评估循环，错误模式检测，置信度校准，自动修正策略 | `src/orchestrator.c` |
| **熔断器集成** | 三态熔断器（关闭→开启→半开），失败计数，超时记录，自动恢复 | `src/orchestrator.c` |
| **LLM 服务调用** | 通过 IPC Service Bus 向 llm_d 发送 LLM 请求，支持系统角色提示词 | `src/orchestrator.c` |
| **任务控制** | 单个任务取消/全部取消，任务状态查询，结果获取 | `src/orchestrator.c` |

### 非职责（明确排除）

- LLM 推理执行（属于 llm_d）
- 工具调用执行（属于 tool_d）
- Agent 能力发现与注册（属于 Market Daemon）
- 安全守卫/内容过滤（属于 Cupolas）
- 底层内存管理/任务调度（属于 CoreKern）
- 认知引擎核心实现（属于 CoreLoopThree atoms）
- 持久化存储（属于 HeapStore / Memory Provider）
- 配置管理基础设施（属于 commons + config_manager）

---

## 2. 公共接口

### 2.1 头文件清单

| 头文件 | 用途 | 公开 API 数量 |
|--------|------|:---:|
| `orchestrator.h` | 编排器核心 API（生命周期、管线、执行、进度回调、查询、控制） | 20 |

### 2.2 关键 API 签名

```c
// 生命周期
orchestrator_t *orchestrator_create(const orch_config_t *config);
void orchestrator_destroy(orchestrator_t *orch);

// 管线操作
orch_pipeline_t *orchestrator_pipeline_create(orchestrator_t *orch, const char *name);
void orchestrator_pipeline_destroy(orch_pipeline_t *pipeline);
int orchestrator_pipeline_add_step(orch_pipeline_t *pipeline, const orch_pipeline_step_t *step);

// 执行
int orchestrator_execute(orchestrator_t *orch, const char *input,
                         orch_result_t **out_results, size_t *out_count);
int orchestrator_execute_pipeline(orchestrator_t *orch, orch_pipeline_t *pipeline,
                                  const char *input, orch_result_t **out_results,
                                  size_t *out_count);
int orchestrator_execute_phase(orchestrator_t *orch, orch_phase_t phase,
                               const char *input, orch_result_t **out_result);

// 进度回调
void orchestrator_set_progress_callback(orchestrator_t *orch,
                                        orch_progress_cb_t callback, void *user_data);

// C-L06: 认知引擎服务注入
void orchestrator_set_cognition_llm_service(orchestrator_t *orch, llm_service_t *llm_svc);
void orchestrator_set_cognition_tool_service(orchestrator_t *orch, tool_service_t *tool_svc);

// 查询
orch_task_status_t orchestrator_get_task_status(orchestrator_t *orch, const char *task_id);
orch_result_t *orchestrator_get_result(orchestrator_t *orch, const char *task_id);
void orchestrator_result_free(orch_result_t *result);
uint32_t orchestrator_active_count(orchestrator_t *orch);

// 控制
int orchestrator_cancel(orchestrator_t *orch, const char *task_id);
int orchestrator_cancel_all(orchestrator_t *orch);

// 全局清理
void orchestrator_global_cleanup(void);

// 默认配置
static inline void orch_config_get_defaults(orch_config_t *cfg);
```

### 2.3 核心数据结构

```c
// 编排阶段枚举
typedef enum {
    ORCH_PHASE_DECOMPOSITION = 0,  // 任务分解
    ORCH_PHASE_PLANNING      = 1,  // 计划制定
    ORCH_PHASE_GENERATION    = 2,  // 内容生成
    ORCH_PHASE_CRITIQUE      = 3,  // 批判评估
    ORCH_PHASE_VERIFICATION  = 4,  // 验证
    ORCH_PHASE_AUDIT         = 5,  // 审计
    ORCH_PHASE_ALIGNMENT     = 6,  // 对齐
    ORCH_PHASE_MAX
} orch_phase_t;

// 任务状态
typedef enum {
    ORCH_TASK_PENDING, ORCH_TASK_RUNNING, ORCH_TASK_COMPLETED,
    ORCH_TASK_FAILED, ORCH_TASK_CANCELLED, ORCH_TASK_TIMEOUT
} orch_task_status_t;

// 编排策略
typedef enum {
    ORCH_STRATEGY_SEQUENTIAL,   // 串行
    ORCH_STRATEGY_PARALLEL,     // 并行
    ORCH_STRATEGY_CONDITIONAL,  // 条件
    ORCH_STRATEGY_LOOP,         // 循环
    ORCH_STRATEGY_ADAPTIVE      // 自适应
} orch_strategy_t;

// 编排器配置
typedef struct {
    uint32_t max_subtasks;               // 最大子任务数 (默认16)
    uint32_t timeout_ms;                 // 超时(ms) (默认60000)
    uint32_t max_retries;                // 最大重试次数 (默认3)
    uint32_t retry_delay_ms;             // 重试延迟(ms) (默认100)
    orch_strategy_t default_strategy;    // 默认策略 (默认SEQUENTIAL)
    bool enable_thinking_chain;          // 启用思考链追踪
    bool enable_metacognition;           // 启用元认知
    bool enable_circuit_breaker;         // 启用熔断器
    bool enable_critique_loop;           // 启用批判循环
    uint32_t critique_max_rounds;        // 最大批判轮次 (默认3)
    float critique_acceptance_threshold; // 接受阈值 (默认0.7)
    float critique_auto_correct_threshold; // 自动修正阈值 (默认0.5)
} orch_config_t;

// 任务结果
typedef struct {
    char *task_id;              // 任务ID
    char *output;               // 输出内容
    size_t output_len;          // 输出长度
    orch_task_status_t status;  // 任务状态
    int error_code;             // 错误码
    uint32_t duration_ms;       // 执行耗时(ms)
    char *thinking_chain_id;    // 思考链ID
} orch_result_t;

// 管线步骤
typedef struct {
    orch_phase_t phase;                // 阶段
    const char *agent_id;              // Agent ID
    const char *skill_id;              // Skill ID
    const char *input;                 // 输入
    orch_strategy_t strategy;          // 策略
    uint32_t timeout_ms;               // 超时
    orch_condition_fn_t condition_fn;  // 条件函数
    void *condition_data;              // 条件数据
} orch_pipeline_step_t;
```

### 2.4 错误码

| 错误码 | 值 | 含义 |
|--------|:---:|------|
| `0` | 0 | 成功 |
| `AIRY_ERR_INVALID_PARAM` | — | 无效参数 |
| `AIRY_ERR_OUT_OF_MEMORY` | — | 内存不足 |
| `AIRY_ERR_DAEMON_INIT_FAILED` | — | 初始化失败 |
| `AIRY_ERR_OVERFLOW` | — | 任务表/步骤表已满 |
| `AIRY_ERR_UNKNOWN` | — | 未知错误 |
| `AIRY_ERR_SVC_BUSY` | — | 服务忙（熔断器拒绝） |
| `AIRY_ERR_LLM_PROVIDER_FAIL` | — | LLM 服务调用失败 |
| `AIRY_ERR_KERN_TASK` | — | 阶段执行失败 |
| `AIRY_ERR_NOT_FOUND` | — | 任务未找到 |
| `-1` | — | 阶段执行失败（LLM 不可用） |
| `-2` | — | 熔断器拒绝 |
| `-3` | — | 超时 |
| `-4` | — | 批判升级（ESCALATE） |
| `-5` | — | 批判未通过 |

---

## 3. 依赖关系

### 3.1 内部依赖（编译时）

```
orchestrator (svc_common 静态库)
  ├── airy_common (commons 统一基础库)
  │     ├── utils/memory/    — memory_compat.h, memory_provider.h
  │     ├── utils/error/     — error.h, error_types.h
  │     ├── utils/logging/   — logging_compat.h
  │     ├── utils/string/    — string_compat.h, safe_string_utils.h
  │     ├── utils/sync/      — atomic_compat.h, 互斥锁
  │     ├── utils/types/     — airy_types.h
  │     └── platform/        — platform.h
  ├── daemon common 组件
  │     ├── svc_common.h     — 服务框架
  │     ├── svc_logger.h     — 统一日志
  │     ├── ipc_service_bus.h — IPC 服务总线（LLM 调用）
  │     ├── circuit_breaker.h — 熔断器
  │     ├── thread_pool.h    — 线程池
  │     ├── daemon_defaults.h — 默认值常量
  │     └── safe_string_utils.h — 安全字符串
  ├── CoreLoopThree atoms
  │     ├── cognition.h      — 认知引擎（任务分解/生成增强）
  │     ├── metacognition.h  — 元认知（批判评估）
  │     ├── confidence_calibrator.h — 置信度校准
  │     ├── memory_provider.h — 记忆提供者
  │     └── llm_service.h / tool_service.h — 服务句柄类型
  └── 标准库
        ├── math.h           — 浮点运算
        ├── stdio.h / stdlib.h / string.h — 标准 C 库
        └── time.h           — 时间戳
```

### 3.2 运行时依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| POSIX 线程 (libpthread) | 系统 | 线程池、互斥锁 |
| nanosleep | 系统 | 重试延迟 |
| llm_d (IPC Service Bus) | 进程间 | 所有阶段的 LLM 推理调用 |
| Memory Provider | 进程内 | 上下文查询、记忆写入、检索、演化 |
| Cognition Engine | 进程内 | 任务分解增强、生成增强 |
| Metacognition Engine | 进程内 | 批判评估、错误模式检测 |
| Confidence Calibrator | 进程内 | 置信度校准 |

### 3.3 被依赖方

| 消费者 | 使用接口 | 说明 |
|--------|---------|------|
| gateway_d | `orchestrator_execute` | API 网关将用户请求路由到编排器 |
| CoreLoopThree | `orchestrator_set_cognition_llm_service` | 认知引擎通过 C-L06 连接线注入 LLM 服务 |
| tool_d | `orchestrator_set_cognition_tool_service` | 工具执行器通过 C-L06 连接线注入工具服务 |
| 所有 daemon | `orchestrator_global_cleanup` | 进程退出时清理全局互斥锁 |

---

## 4. 配置参数

### 4.1 编排器配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `max_subtasks` | uint32_t | 16 | 最大子任务数 |
| `timeout_ms` | uint32_t | 60000 | 单阶段超时(ms) |
| `max_retries` | uint32_t | 3 | 最大重试次数 |
| `retry_delay_ms` | uint32_t | 100 | 重试延迟(ms) |
| `default_strategy` | orch_strategy_t | SEQUENTIAL | 默认编排策略 |
| `enable_thinking_chain` | bool | true | 启用思考链追踪 |
| `enable_metacognition` | bool | true | 启用元认知 |
| `enable_circuit_breaker` | bool | true | 启用熔断器 |
| `enable_critique_loop` | bool | true | 启用批判循环 |
| `critique_max_rounds` | uint32_t | 3 | 最大批判轮次 |
| `critique_acceptance_threshold` | float | 0.7 | 批判接受阈值 |
| `critique_auto_correct_threshold` | float | 0.5 | 自动修正阈值 |

### 4.2 内部容量限制

| 参数 | 值 | 说明 |
|------|:---:|------|
| `ORCH_MAX_TASKS` | 64 | 任务表最大容量 |
| `ORCH_MAX_STEPS` | 32 | 管线最大步骤数 |
| `ORCH_ID_LEN` | 48 | 任务/思考链 ID 最大长度 |
| `ORCH_VERIFY_MAX_ROUNDS` | 3 | 生成验证最大轮次 |
| `ORCH_VERIFY_THRESHOLD` | 0.7 | 验证通过阈值 |
| `ORCH_ALIGN_HISTORY_SIZE` | 8 | 对齐历史窗口大小 |

### 4.3 线程池配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `min_threads` | uint32_t | 2 | 最小线程数 |
| `max_threads` | uint32_t | 8 | 最大线程数 |
| `queue_size` | uint32_t | 64 | 任务队列大小 |
| `idle_timeout_ms` | uint32_t | 30000 | 线程空闲超时(ms) |

### 4.4 熔断器配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `failure_threshold` | uint32_t | 5 | 失败阈值（触发熔断） |
| `half_open_max_calls` | uint32_t | 2 | 半开状态最大探测调用数 |
| `timeout_ms` | uint32_t | 30000 | 熔断超时(ms) |

---

## 5. 跨团队接口合约

### 5.1 合约文件

- `contracts/contract_A_B.h` — 团队A(Orchestrator) 与 团队B(Market Daemon) 的接口合约（Agent 发现与选择）
- `contracts/contract_A_C.h` — 团队A(Orchestrator) 与 团队C(测试/质量) 的接口合约

### 5.2 测试接口

| 函数 | 用途 | 消费者 |
|------|------|--------|
| `orchestrator_create()` | 创建编排器实例 | 单元测试 |
| `orchestrator_execute()` | 执行完整编排管线 | 集成测试 |
| `orchestrator_execute_phase()` | 执行单个阶段 | 单元测试 |
| `orchestrator_get_task_status()` | 查询任务状态 | 测试/监控 |
| `orchestrator_get_result()` | 获取任务结果 | 测试 |
| `orchestrator_active_count()` | 获取活跃任务数 | 测试/监控 |
| `orchestrator_cancel_all()` | 取消所有任务 | 测试清理 |
| `orch_config_get_defaults()` | 获取默认配置 | 测试 |

### 5.3 回调类型（供消费者实现）

| 回调 | 签名 | 用途 |
|------|------|------|
| `orch_progress_cb_t` | `void(orch_phase_t, orch_task_status_t, const char*, void*)` | 进度回调，每个阶段状态变更时触发 |
| `orch_condition_fn_t` | `bool(const char*, void*)` | 条件函数，用于管线步骤的条件执行 |

---

## 6. 文件所有权

```
@owner: team-A
```

所有 `agentrt/daemons/common/include/orchestrator.h` 和 `agentrt/daemons/common/src/orchestrator.c` 归属于团队A。编排器作为 `svc_common` 静态库的一部分编译，被所有守护进程链接使用。

### 执行管线

```
orchestrator_execute()
  │
  ├── Phase 0: DECOMPOSITION  ── 认知引擎优先 → LLM 回退
  ├── Phase 1: PLANNING       ── LLM 计划生成
  ├── Phase 2: GENERATION     ── T2 流式生成 + T1-F 验证修正循环
  ├── Phase 3: CRITIQUE       ── S1 元认知多轮批判 + 自动修正
  ├── Phase 4: VERIFICATION   ── T1-F 快速验证 + 自动修正
  ├── Phase 5: AUDIT          ── T1-P 专家审计
  └── Phase 6: ALIGNMENT      ── 多维度对齐评分 + 漂移检测
```

---

## 7. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0.0 | 2026-06-18 | 初始版本，基于 v0.1.0 代码现状 |