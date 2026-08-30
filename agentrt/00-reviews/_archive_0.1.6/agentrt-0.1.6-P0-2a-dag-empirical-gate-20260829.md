# agentrt-0.1.6 P0-2a DAG 收敛实证门报告

> **归档状态**：已归档（ARCHIVED 2026-08-30）
> **归档原因**：0.1.6 P0-2a 实证门已完成并裁决（分支 B 薄壳已满足，无收敛动作可做）
> **归档执行**：Decheng Li（lidecheng@spharx.cn）

> **报告编号**：EMP-AGENTRT-0.1.6-P0-2a-20260829
> **实证对象**：`atoms/coreloopthree/src/loop/loop_dag.c` vs `atoms/taskflow/src/graph_engine.c`
> **依据方案**：PLAN-AGENTRT-0.1.6-20260828-R2（决策 1：两套 DAG 收敛前先 diff 证伪）
> **实证日期**：2026-08-29
> **实证人**：Decheng Li（lidecheng@spharx.cn）
> **结论**：**不存在两套 DAG 重复实现**。`loop_dag.c` 是 taskflow 引擎的 100% 薄封装适配层；`graph_engine.c` 是唯一图数据结构引擎。分支 A（删除）不适用，分支 B（薄壳）已满足。

---

## 1. 实证范围与方法

对照 R2 决策 1 的假设（"两套 DAG 是否真重复：coreloopthree `loop_dag.c` 与 taskflow `graph_engine` 的功能对比缺失"），本次逐文件、逐接口实证：

| 文件 | 定位 | 行数 |
|------|------|------|
| `atoms/coreloopthree/src/loop/loop_dag.c` | coreloopthree DAG 接入层 | 268 |
| `atoms/coreloopthree/src/adapter/plan_to_dag.c` | 计划 → taskflow 工作流转换 | ~141 |
| `atoms/taskflow/src/graph_engine.c` + traverse/checkpoint/persist | 图数据结构引擎 | — |
| `atoms/taskflow/src/taskflow_advanced*.c` / `taskflow_engine` | 工作流执行引擎 | — |

方法：全量阅读 `loop_dag.c` 函数体，统计其对外部引擎的调用；搜索 coreloopthree 全仓是否含自建图数据结构（邻接表/顶点/边/拓扑）。

## 2. loop_dag.c 逐函数实证

`loop_dag.c` 共 8 个导出函数，**全部为 taskflow 引擎的薄包装**，无一行自建图/调度/状态机逻辑：

| 导出函数 | 实现 = 对 taskflow 的调用 | 自建逻辑 |
|---------|---------------------------|---------|
| `airy_loop_dag_register_handler` | `taskflow_engine_register_handler` | 无 |
| `airy_loop_dag_set_progress_callback` | `taskflow_engine_set_progress_callback` | 无 |
| `airy_loop_dag_set_cancel_flag` | `taskflow_engine_set_cancel_flag` | 无 |
| `airy_loop_submit_dag` | `taskflow_engine_register_workflow` + `taskflow_engine_start`（含失败清理 `taskflow_engine_unregister_workflow`） | 无 |
| `airy_loop_dag_wait` | `taskflow_engine_get_execution` + `taskflow_engine_run_to_completion_timeout` | 无（仅状态判断 + 结果拷贝） |
| `airy_loop_dag_status` | `taskflow_engine_get_execution`（状态/进度读取） | 无（仅状态串映射） |
| `airy_loop_dag_cancel` | `taskflow_engine_cancel` | 无 |
| （持有）`loop->taskflow_engine` | 由 `loop_create` 创建、`loop_destroy` 销毁 | — |

> **架构事实**：CoreLoopThree 持有 `taskflow_engine_t*`，通过上述 airy_loop_dag_* API 消费 taskflow 工作流执行能力。loop_dag.c 的作用是 API 形态适配（airy_* 命名 + 错误码映射），非功能实现。

## 3. 能力 diff（loop_dag vs graph_engine）

| 能力维度 | loop_dag.c（coreloopthree） | graph_engine（taskflow） | 判定 |
|---------|----------------------------|--------------------------|------|
| 图数据结构（顶点/边/加载/保存） | 无 | ✅ `graph_engine_load/save` | 唯一权威在 taskflow |
| 图遍历（BFS/DFS/环检测） | 无 | ✅ `graph_engine_traverse` 等 | 唯一权威在 taskflow |
| 图持久化/检查点 | 无 | ✅ `graph_engine_persist` / `graph_engine_checkpoint` | 唯一权威在 taskflow |
| 工作流执行（register/start/wait/cancel） | 无（仅转发） | ✅ taskflow_engine 系列 | 唯一权威在 taskflow |
| 状态模型（PENDING/READY/RUNNING/...） | 无（仅读取映射） | ✅ `taskflow_state_t` | 唯一权威在 taskflow |
| 计划 → 工作流转换 | `plan_to_dag.c` 填充 `taskflow_workflow_t` 结构 | — | 数据转换，非图引擎 |

**功能面交集为 0**：loop_dag.c 不含 graph_engine 任何能力，graph_engine 不含 airy_loop_dag 的 API 形态。二者不是"同一套的重复实现"，而是**不同层次**（图原语 / 工作流执行 / 适配层）。

## 4. coreloopthree 全仓自建图扫描

| 关键词 | 命中文件 | 性质 |
|--------|---------|------|
| `graph_node/adjacency/graph_edge` | `src/work_hall/work_hall_sched.c`、`src/orchestrator/orchestrator_phase_llm.c` | 均为对 taskflow/loop_dag API 的**调用**（`airy_loop_submit_dag` 等），非自建图 |
| `dag` | `src/loop/loop_dag.c`、`src/adapter/plan_to_dag.c`、`include/loop.h`、`include/plan_to_dag.h` | 全部消费 taskflow 类型（`taskflow_workflow_t`/`taskflow_node_t`/`taskflow_edge_t`） |

**结论：coreloopthree 无第二套图引擎实现。**

## 5. 实证门裁决

- **分支 A（删除 loop_dag.c，coreloopthree 改消费 taskflow 接口）**：❌ **不适用**。loop_dag.c 不是重复实现而是适配层；删除后 coreloopthree 需直接暴露 taskflow 内部 API，破坏 `airy_loop_dag_*` 公共接口形态，且无任何代码量收益。
- **分支 B（loop_dag 独有能力下沉 taskflow + loop_dag 改薄壳）**：✅ **已满足**。loop_dag.c 本就是薄壳；`plan_to_dag.c` 的数据转换逻辑属 coreloopthree 认知层职责（计划 → 工作流），下沉 taskflow 反而破坏分层。

**最终处置**：保留现状（loop_dag 薄壳 + plan_to_dag 转换 + taskflow 唯一引擎权威）。R2 决策 1 的"两套 DAG 收敛"任务经实证确认**无收敛动作可做**，P0-2b 标记为"实证后无操作"。此为实证门设计的正向结果——避免了对非重复代码的误删。

## 6. 遗留观察（非本 P0 范围）

- `plan_to_dag.c`（141 行）是"计划 → taskflow 工作流"的唯一转换入口，未来可补充独立单测（当前无直接单测，仅经 taskflow 测试间接覆盖）。
- `loop_dag.c` 的 `airy_loop_dag_status` 状态串映射可并入 taskflow 状态枚举的序列化能力（属 0.1.7 vtable 策略化范围，不在 0.1.6 执行）。

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. | P0-2a DAG 实证门报告 | 2026-08-29
