# CoreLoopThree 子系统边界文档

> **版本**: v1.0.0 | **日期**: 2026-06-18 | **团队**: A（核心引擎）
> **代码路径**: `agentrt/atoms/coreloopthree/`

---

## 1. 职责边界

CoreLoopThree 是 AgentRT 的核心 AI 代理循环引擎，实现认知（cognition）→ 执行（execution）→ 记忆（memory）三层认知循环。它负责将用户输入理解、规划为任务 DAG，执行并记录结果，形成完整的 think-act-remember 闭环。

### 核心职责

| 模块 | 职责 | 源文件/头文件 |
|------|------|--------|
| **主循环** | 三层循环编排（认知→执行→记忆），任务提交/等待/取消，引擎生命周期管理，持久化长任务支持 | `include/loop.h`, `src/loop.c` |
| **认知引擎** | 意图解析、任务规划（DAG）、策略接口（规划/协同/调度）、LLM 服务注入、流式回调、工具服务桥接 | `include/cognition.h`, `src/cognition/` |
| **执行引擎** | 任务调度执行、执行单元注册、任务状态管理（PENDING→RUNNING→SUCCEEDED/FAILED）、补偿事务、结果查询 | `include/execution.h`, `src/execution/` |
| **记忆引擎** | 记忆写入/查询/检索、记忆挂载（mount）、记忆进化（模式挖掘）、重要性评分、上下文关联 | `include/memory.h`, `src/memory/` |
| **Prompt 加载器** | YAML 模板加载/缓存/热重载、变量渲染（{var}替换）、JSON Schema 输出校验 | `include/prompt_loader.h`, `src/prompt_loader.c` |
| **元认知** | 多维度自评估（相关性/准确性/完整性/一致性/清晰度）、错误检测与纠正、置信度校准、持久学习 | `src/cognition/foundation/metacognition.h` |
| **置信度校准器** | 多维度偏差校准、指数衰减算法、校准因子更新、收敛检测 | `src/cognition/critique/confidence_calibrator.h` |
| **认知进化** | 经验记忆积累、策略进化、跨领域知识迁移、认知层级跃迁（感知→反应→学习→推理→创造） | `include/cognitive_evolution.h` |
| **意图解析器** | 用户输入意图提取、自定义规则添加、意图分类与置信度评分 | `include/cognition.h`（intent_parser 部分） |
| **配置加载器** | agentrt.yaml 加载/解析、配置热重载（文件监听）、全局配置访问、环境变量覆盖 | `include/config_loader.h`, `src/config_loader.c` |
| **编排器适配器** | Orchestrator → CoreLoopThree 桥接，流水线执行、并行实例管理、进度回调 | `include/orch_adapter.h`, `src/orch_adapter.c` |
| **检查点适配器** | 长任务状态持久化、崩溃恢复、增量保存、快照管理 | `include/checkpoint_adapter.h`, `src/checkpoint_adapter.c` |
| **MemoryRovol 桥接** | MemoryRovol 记忆卷载提供商切换（builtin ↔ MemoryRovol） | `include/memoryrovol_bridge.h`, `src/memory/memoryrovol_bridge.c` |

### 非职责（明确排除）

- 不负责底层内存分配/释放/泄漏检测（属于 corekern + commons/memory）
- 不负责安全守卫/内容过滤/权限裁决（属于 Cupolas）
- 不负责网络协议处理/网关（属于 gateway_d）
- 不负责 LLM 推理执行（属于 llm_d，CoreLoopThree 通过 LLM 服务注入调用）
- 不负责工具调用具体实现（属于 tool_d，CoreLoopThree 通过工具服务注入调用）
- 不负责持久化存储格式（属于 HeapStore）
- 不负责编排流水线定义（属于 Orchestrator，CoreLoopThree 通过 orch_adapter 执行）
- 不负责 YAML 解析底层实现（属于 yaml_minimal / cupolas 共享）

---

## 2. 公共接口

### 2.1 头文件清单

| 头文件 | 用途 | 公开 API 数量 |
|--------|------|:---:|
| `include/loop.h` | 三层核心循环主接口：创建/销毁/运行/停止/提交/等待 | 10 |
| `include/cognition.h` | 认知引擎：创建/销毁/处理/策略设置/服务注入/统计/健康检查 | 20+ |
| `include/execution.h` | 执行引擎：创建/销毁/注册/提交/查询/等待/取消/补偿事务 | 18+ |
| `include/memory.h` | 记忆引擎：创建/销毁/写入/查询/获取/挂载/进化/健康检查 | 12+ |
| `include/prompt_loader.h` | Prompt 模板加载/渲染/校验/缓存管理 | 11 |
| `include/config_loader.h` | 配置文件加载/热重载/全局配置访问 | 8 |
| `include/orch_adapter.h` | Orchestrator 编排器适配器 | 12+ |
| `include/checkpoint_adapter.h` | 检查点持久化适配器 | 12+ |
| `include/cognitive_evolution.h` | 认知进化系统 | 12+ |
| `include/compensation.h` | 补偿事务管理器 | 5 |
| `include/memoryrovol_bridge.h` | MemoryRovol 桥接 | 5+ |
| `include/llm_svc_adapter.h` | LLM 服务适配器 | 5+ |
| `include/tool_svc_adapter.h` | 工具服务适配器 | 5+ |
| `include/agent_registry.h` | Agent 注册表 | 5+ |
| `include/browser.h` | 浏览器工具接口 | 5+ |
| `include/error_utils.h` | 错误处理工具 | 3+ |
| `include/id_utils.h` | ID 生成工具 | 3+ |
| `include/multi_agent_collaboration.h` | 多智能体协作 | 5+ |
| `include/yaml_loader.h` | YAML 配置解析器 | 5+ |

### 2.2 关键 API 签名

```c
// ==================== 主循环 ====================
AIRY_API airy_err_t airy_loop_create(const airy_loop_config_t *manager,
                                                airy_core_loop_t **out_loop);
AIRY_API void airy_loop_destroy(airy_core_loop_t *loop);
AIRY_API airy_err_t airy_loop_run(airy_core_loop_t *loop);
AIRY_API void airy_loop_stop(airy_core_loop_t *loop);
AIRY_API airy_err_t airy_loop_submit(airy_core_loop_t *loop, const char *input,
                                                size_t input_len, char **out_task_id);
AIRY_API airy_err_t airy_loop_wait(airy_core_loop_t *loop, const char *task_id,
                                              uint32_t timeout_ms, char **out_result,
                                              size_t *out_result_len);
AIRY_API void airy_loop_get_engines(airy_core_loop_t *loop,
                                          airy_cognition_engine_t **out_cognition,
                                          airy_execution_engine_t **out_execution,
                                          airy_memory_engine_t **out_memory);
AIRY_API airy_err_t airy_loop_submit_persistent(airy_core_loop_t *loop,
                                                           const char *input, size_t input_len,
                                                           const char *session_id,
                                                           char **out_task_id);
AIRY_API airy_err_t airy_loop_restore_task(airy_core_loop_t *loop,
                                                      const char *task_id,
                                                      char **out_restored_task_id);
AIRY_API airy_err_t airy_loop_list_checkpoints(airy_core_loop_t *loop,
                                                          char ***out_task_ids, size_t *out_count);

// ==================== 认知引擎 ====================
AIRY_API airy_err_t airy_cognition_create_take(airy_plan_strategy_t *plan_strategy,
                                                          airy_coordinator_strategy_t *coord_strategy,
                                                          airy_dispatching_strategy_t *disp_strategy,
                                                          airy_cognition_engine_t **out_engine);
AIRY_API airy_err_t airy_cognition_create_ex_take(
    const airy_cognition_config_t *manager, airy_plan_strategy_t *plan_strategy,
    airy_coordinator_strategy_t *coord_strategy, airy_dispatching_strategy_t *disp_strategy,
    airy_cognition_engine_t **out_engine);
AIRY_API void airy_cognition_destroy(airy_cognition_engine_t *engine);
AIRY_API airy_err_t airy_cognition_process(airy_cognition_engine_t *engine,
                                                      const char *input, size_t input_len,
                                                      airy_task_plan_t **out_plan);
AIRY_API void airy_cognition_set_llm_service(airy_cognition_engine_t *engine,
                                                    llm_service_t *llm_svc);
AIRY_API void airy_cognition_set_tool_service(airy_cognition_engine_t *engine,
                                                     tool_service_t *tool_svc);
AIRY_API void airy_cognition_set_memory(airy_cognition_engine_t *engine,
                                              airy_memory_engine_t *memory);
AIRY_API void airy_cognition_set_memory_provider(airy_cognition_engine_t *engine,
                                                       airy_memory_provider_t *provider);
AIRY_API airy_err_t airy_cognition_health_check(airy_cognition_engine_t *engine,
                                                           char **out_json);

// ==================== 执行引擎 ====================
AIRY_API airy_err_t airy_execution_create(uint32_t max_concurrency,
                                                     airy_execution_engine_t **out_engine);
AIRY_API void airy_execution_destroy(airy_execution_engine_t *engine);
AIRY_API airy_err_t airy_execution_register_unit(airy_execution_engine_t *engine,
                                                            const char *name,
                                                            airy_execution_unit_t unit);
AIRY_API airy_err_t airy_execution_submit(airy_execution_engine_t *engine,
                                                     const airy_task_t *task,
                                                     char **out_task_id);
AIRY_API airy_err_t airy_execution_query(airy_execution_engine_t *engine,
                                                    const char *task_id,
                                                    airy_task_status_t *out_status);
AIRY_API airy_err_t airy_execution_wait(airy_execution_engine_t *engine,
                                                   const char *task_id, uint32_t timeout_ms,
                                                   airy_task_t **out_result);
AIRY_API airy_err_t airy_execution_cancel(airy_execution_engine_t *engine,
                                                     const char *task_id);

// ==================== 记忆引擎 ====================
AIRY_API airy_err_t airy_memory_create(const char *config_path,
                                                  airy_memory_engine_t **out_engine);
AIRY_API void airy_memory_destroy(airy_memory_engine_t *engine);
AIRY_API airy_err_t airy_memory_write(airy_memory_engine_t *engine,
                                                 const airy_memory_record_t *record,
                                                 char **out_record_id);
AIRY_API airy_err_t airy_memory_query(airy_memory_engine_t *engine,
                                                 const airy_memory_query_t *query,
                                                 airy_memory_result_ext_t **out_result);
AIRY_API airy_err_t airy_memory_evolve(airy_memory_engine_t *engine, int force);

// ==================== Prompt 加载器 ====================
int airy_prompt_loader_init(const airy_prompt_loader_config_t *config);
void airy_prompt_loader_shutdown(void);
int airy_prompt_template_load(const char *template_path,
                                  airy_prompt_template_t **out_template);
int airy_prompt_render(const airy_prompt_template_t *template,
                           const airy_prompt_variable_t *variables,
                           size_t variable_count,
                           airy_prompt_rendered_t **out_rendered);
int airy_prompt_validate_output(const airy_prompt_template_t *template,
                                    const char *output_json, size_t output_len,
                                    char **out_error);

// ==================== 元认知 ====================
AIRY_API airy_err_t airy_mc_create(airy_metacognition_t **out_mc);
AIRY_API void airy_mc_destroy(airy_metacognition_t *mc);
AIRY_API airy_err_t airy_mc_evaluate_step(airy_metacognition_t *mc,
                                                     airy_thinking_step_t *step,
                                                     const char *context, size_t context_len,
                                                     mc_evaluation_result_t *out_result);
AIRY_API float airy_mc_calibrate_confidence(airy_metacognition_t *mc,
                                                  float raw_confidence);
AIRY_API airy_err_t airy_mc_feedback(airy_metacognition_t *mc,
                                                float predicted_confidence, int was_correct);
AIRY_API airy_err_t airy_mc_apply_correction(
    airy_metacognition_t *mc, airy_thinking_step_t *step,
    const mc_evaluation_result_t *eval,
    airy_err_t (*corrector_fn)(const char *input, size_t input_len, char **output,
                                    size_t *output_len, void *user_data),
    void *corrector_user_data);

// ==================== 置信度校准器 ====================
confidence_calibrator_t *confidence_calibrator_create(double decay_factor);
void confidence_calibrator_destroy(confidence_calibrator_t *calibrator);
double confidence_calibrator_calibrate(confidence_calibrator_t *calibrator, double raw_score,
                                       cc_dimension_t dimension);
void confidence_calibrator_update(confidence_calibrator_t *calibrator, double actual_accuracy,
                                  double predicted_confidence, cc_dimension_t dimension);

// ==================== 认知进化 ====================
cog_evolution_t *cog_evolution_create(cog_level_t initial_level);
void cog_evolution_destroy(cog_evolution_t *evo);
int cog_evolution_record_experience(cog_evolution_t *evo, const cog_experience_t *experience);
int cog_evolution_extract_patterns(cog_evolution_t *evo, size_t *pattern_count);
int cog_evolution_evolve_strategies(cog_evolution_t *evo, size_t *strategy_count);
int cog_evolution_select_strategy(cog_evolution_t *evo, const char *domain,
                                  const char *context_json, cog_strategy_t **strategy);
int cog_evolution_transfer_knowledge(cog_evolution_t *evo, const char *source_domain,
                                     const char *target_domain, cog_knowledge_t **knowledge);
cog_level_t cog_evolution_get_level(cog_evolution_t *evo);

// ==================== 配置加载器 ====================
int airy_config_load_yaml(const char *yaml_path, airy_yaml_config_t *config);
const airy_yaml_config_t *airy_config_get_global(void);
int airy_config_on_reload(airy_config_reload_cb_t callback, void *user_data);
int airy_config_watch_start(const char *yaml_path, uint32_t interval_ms);
void airy_config_watch_stop(void);
int airy_config_reload(const char *yaml_path);
int airy_config_init(const char *yaml_path);

// ==================== 编排器适配器 ====================
orch_adapter_t *orch_adapter_create(orchestrator_t *orch, const orch_adapter_config_t *config);
void orch_adapter_destroy(orch_adapter_t *adapter);
int orch_adapter_set_llm_service(orch_adapter_t *adapter, void *llm_svc_adapter);
int orch_adapter_set_tool_service(orch_adapter_t *adapter, void *tool_svc_adapter);
int orch_adapter_execute_pipeline(orch_adapter_t *adapter, orch_pipeline_t *pipeline,
                                  const char *input, orch_result_t **out_results,
                                  size_t *out_count);

// ==================== 检查点适配器 ====================
checkpoint_adapter_t *checkpoint_adapter_create(const checkpoint_adapter_config_t *config);
void checkpoint_adapter_destroy(checkpoint_adapter_t *adapter);
int checkpoint_adapter_save(checkpoint_adapter_t *adapter, const char *task_id,
                            const char *session_id, uint64_t sequence_num,
                            const checkpoint_snapshot_t *snapshot);
int checkpoint_adapter_restore(checkpoint_adapter_t *adapter, const char *task_id,
                               checkpoint_snapshot_t **out_snapshot);
```

### 2.3 错误码（来自 corekern `error.h`）

| 错误码 | 含义 |
|--------|------|
| `AIRY_SUCCESS` (0) | 成功 |
| `AIRY_EINVAL` | 无效参数 |
| `AIRY_ENOMEM` | 内存不足 |
| `AIRY_ENOTINIT` | 未初始化 |
| `AIRY_EEXIST` | 已存在 |
| `AIRY_EBUSY` | 资源忙 |
| `AIRY_ENOENT` | 不存在 |
| `AIRY_EALREADY` | 已完成/已操作 |
| `AIRY_ERR_TIMEOUT` | 超时 |
| `AIRY_ERR_NOT_FOUND` | 未找到 |
| `AIRY_ERR_PERMISSION_DENIED` | 权限拒绝 |

---

## 3. 依赖关系

### 3.1 内部依赖（编译时）

```
agentrt/atoms/coreloopthree/
  ├── agentrt/atoms/corekern/     — airy_rt.h, error.h, 任务调度, 内存分配, IPC
  ├── agentrt/commons/            — airy_types.h, types.h, 基础类型定义
  ├── agentrt/cupolas/src/        — yaml_minimal.h（YAML 解析共享）
  ├── agentrt/daemon/common/      — checkpoint.h, orchestrator.h（检查点、编排器接口）
  ├── agentrt/atoms/memory/       — memory_provider 接口（MemoryRovol 桥接）
  ├── include/llm_service.h        — LLM 服务接口（llm_d 注入）
  ├── include/tool_service.h       — 工具服务接口（tool_d 注入）
  └── 标准 C 库                    — stddef.h, stdint.h, stdbool.h
```

### 3.2 运行时依赖

| 依赖 | 类型 | 说明 |
|------|------|------|
| POSIX 线程 (libpthread) | 系统 | 多线程认知/执行/记忆并行处理 |
| 文件系统 | 系统 | YAML 模板加载、配置读取、检查点存储 |
| 系统时钟 | 系统 | 超时管理、时间戳、统计间隔 |

### 3.3 被依赖方

| 消费者 | 使用接口 | 说明 |
|--------|---------|------|
| Orchestrator | `orch_adapter_*` | 编排器通过适配器创建和执行 CoreLoopThree 实例 |
| gateway_d | `airy_loop_submit/wait` | 网关通过循环接口提交用户任务 |
| market_d | `airy_loop_submit` | 市场通过循环接口提交任务 |
| 测试框架 | `airy_loop_*`, `airy_cognition_*`, `airy_execution_*`, `airy_memory_*` | 单元测试和集成测试 |

---

## 4. 配置参数

### 4.1 主循环配置 (`airy_loop_config_t`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `loop_config_cognition_threads` | uint32_t | — | 认知层线程数 |
| `loop_config_execution_threads` | uint32_t | — | 行动层线程数 |
| `loop_config_memory_threads` | uint32_t | — | 记忆层线程数 |
| `loop_config_max_queued_tasks` | uint32_t | — | 最大排队任务数 |
| `loop_config_stats_interval_ms` | uint32_t | 0 | 统计输出间隔（0=不输出） |
| `loop_config_memory_query_limit` | size_t | 5 | 记忆检索上限 |
| `loop_config_task_timeout_ms` | uint32_t | 30000 | 任务执行超时（ms） |
| `loop_config_memory_importance` | float | 0.7 | 记忆重要性权重 |
| `loop_config_checkpoint_enabled` | uint32_t | 0 | 检查点启用标志 |
| `loop_config_checkpoint_path` | char[256] | — | 检查点存储路径 |
| `loop_config_checkpoint_interval_ms` | uint32_t | 30000 | 检查点保存间隔（ms） |

### 4.2 认知引擎配置 (`airy_cognition_config_t`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `cognition_default_timeout_ms` | uint32_t | — | 默认任务超时（ms） |
| `cognition_max_retries` | uint32_t | — | 最大重试次数 |
| `feedback_callback` | 函数指针 | NULL | 反馈回调函数 |
| `feedback_user_data` | void* | NULL | 反馈回调用户数据 |

### 4.3 Prompt 加载器配置 (`airy_prompt_loader_config_t`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `template_dir` | char[512] | `ecosystem/prompts/templates/` | 模板目录 |
| `enable_cache` | bool | — | 是否启用缓存 |
| `cache_max_entries` | size_t | 128 | 缓存最大条目数 |
| `enable_schema_validation` | bool | — | 是否启用 Schema 校验 |

### 4.4 检查点适配器配置 (`checkpoint_adapter_config_t`)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `storage_path` | const char* | `/var/lib/agentrt/checkpoints` | 检查点存储路径 |
| `save_interval_turns` | uint32_t | 10 | 每 N 轮保存一次 |
| `save_interval_ms` | uint32_t | 30000 | 每 N 毫秒保存一次 |
| `enable_incremental_save` | bool | — | 是否启用增量保存 |
| `enable_compression` | bool | — | 是否启用压缩 |
| `max_checkpoints_per_task` | uint32_t | 0（无限制） | 每任务最大检查点数 |
| `max_age_seconds` | uint64_t | 0（永不过期） | 最大保留时间 |

### 4.5 元认知配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|:---:|------|
| `acceptance_threshold` | float | 0.7 | 可接受性阈值 |
| `auto_correct_threshold` | float | 0.5 | 自动修正阈值 |
| `enable_confidence_calibration` | int | — | 启用置信度校准 |
| `enable_learning` | int | — | 启用自适应学习 |
| `MC_MAX_HISTORY_RECORDS` | size_t | 256 | 评估历史最大记录数 |
| `MC_CALIBRATION_WINDOW` | size_t | 32 | 置信度校准滑动窗口 |
| `MC_MAX_PATTERNS` | size_t | 32 | 最大错误模式数 |

---

## 5. 跨团队接口合约

### 5.1 合约文件

- `contracts/contract_A_C_coreloopthree.h` — 团队A（CoreLoopThree）与团队C（测试/质量）的接口合约

### 5.2 测试接口

| 函数 | 用途 | 消费者 |
|------|------|--------|
| `airy_loop_get_engines()` | 获取内部引擎指针（用于注入测试） | 测试 |
| `airy_cognition_stats()` | 获取认知引擎统计信息 | 测试/监控 |
| `airy_cognition_health_check()` | 获取认知引擎健康状态（JSON） | 测试/监控 |
| `airy_execution_health_check()` | 获取执行引擎健康状态（JSON） | 测试/监控 |
| `airy_memory_health_check()` | 获取记忆引擎健康状态（JSON） | 测试/监控 |
| `airy_intent_parser_stats()` | 获取意图解析器统计 | 测试 |
| `airy_intent_parser_reset_stats()` | 重置意图解析器统计 | 测试 |
| `airy_intent_parser_health_check()` | 获取意图解析器健康状态 | 测试 |
| `airy_mc_stats()` | 获取元认知统计信息（JSON） | 测试/监控 |
| `airy_mc_get_history()` | 获取评估历史记录 | 测试 |
| `airy_mc_reset()` | 重置校准器和历史 | 测试 |
| `confidence_calibrator_get_bias()` | 获取维度偏差 | 测试 |
| `confidence_calibrator_check_convergence()` | 检查校准收敛 | 测试 |
| `airy_prompt_cache_stats()` | 获取模板缓存统计 | 测试/监控 |
| `orch_adapter_get_stats()` | 获取编排器适配器统计 | 测试/监控 |
| `checkpoint_adapter_get_stats()` | 获取检查点适配器统计 | 测试/监控 |
| `cog_evolution_get_fitness()` | 获取认知进化适应度 | 测试 |

---

## 6. 文件所有权

```
@owner: team-A
```

所有 `agentrt/atoms/coreloopthree/` 下的文件归属于团队A。团队C 仅可修改 `tests/` 目录下的测试文件。

---

## 7. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0.0 | 2026-06-18 | 初始版本，基于 AgentRT v0.1.1 代码现状 |