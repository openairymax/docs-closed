# 蓝图调度与执行增强融合设计（Roadmap Sched & Execution Enhancement）

> **文档定位**：三级图纸调度系统融入 agentrt + 任务执行五项改进的统一设计
> **正式命名**：中文「蓝图调度」，英文 **Roadmap Sched**
> **最后更新**：2026-08-09
> **适用版本**：agentrt 0.1.1
> **关联文档**：《三级图纸调度系统》设计规范、GCCP（07-gccp.md）、GRAD（09-grad.md）、工作大厅（08-work-hall.md）

---

## 1. 概述

### 1.1 设计目标

将**三级图纸调度系统**（L1 状态记忆 / L2 语义缓存 / L3 全量重规划）作为 agentrt 认知层的**缓存调度前置层（蓝图调度 / Roadmap Sched）**落地，同时融合任务执行层的**五项改进**（异步可中断、产物验证、失败分级、分级重试、多方案权衡），并深化三层协同（执行结果回灌 L2、验证结果准入 L2、取消与 L1 联动），形成"缓存命中优先、全量规划兜底、执行质量增强、闭环回灌自进化"的统一运行时。

### 1.2 不可替换约束

- **GCCP（事实确认）与 GRAD（逻辑确认）作为主链绝对不可替换**，任何降级路径不得绕过。
- L3 内部采用**双事实确认闭环**：事实确认（GCCP-1）→ 多方案形成 → 确认方案 → 再次事实确认（GCCP-2）→ DAG 逻辑确认（GRAD）。
- 单计划收敛保留为默认主链：多方案仅对复杂任务启用，简单任务直接 GCCP-1 → GCCP-2 → GRAD。

### 1.3 设计原则

- **复用优先**：不重复造轮子，三级系统与执行改进全部复用 agentrt 现有组件（认知管线、工作大厅、mac_framework、记忆层、线程池）。
- **渐进式降级**：L1 失效→L2，L2 失效→L3；执行增强逐项可配置。
- **纯 C 核心**：新增组件保持纯 C，无外部运行时依赖（Embedding 经 llm_d 服务接入，非核心强制）。
- **闭环自进化**：执行结果经验证后回灌缓存，缓存质量随执行反馈持续提升。

---

## 2. 总体架构

```
用户指令
  │
  ▼
┌─────────────────────────────────────────────────────────┐
│ 蓝图调度（Roadmap Sched，coreloopthree/dispatch）        │
│  L1 状态机（零 Token）→ L2 语义缓存（低 Token）→ L3 五步序列 │
└────────────────────────┬────────────────────────────────┘
                         │ 未命中 → L3
┌────────────────────────▼────────────────────────────────┐
│ 五阶段认知管线（GCCP + GRAD，不可替换）                    │
│  五步序列：GCCP-1 → 多方案 → 确认 → GCCP-2 → GRAD 收敛     │
└────────────────────────┬────────────────────────────────┘
                         │ 收敛图纸 absorb（写 L2 + 更新 L1）
┌────────────────────────┬────────────────────────────────┐
│ 任务大厅（作战指挥中心，work_hall）                        │
│  认知层发布命令 → 执行层领取 → 产物回传 + 复核/终裁         │
│  ├─ 执行中图纸复核（改进6：门禁 + t2 复核 + t1-f 终裁）     │
│  └─ 工作区隔离（沙箱工作目录，DAG 并行分支独立操作）        │
└────────────────────────┬────────────────────────────────┘
                         │ cancel_token 贯穿
┌────────────────────────▼────────────────────────────────┐
│ 执行层（异步可中断）                                      │
│  agent_d（invoke 非阻塞） / tool_d（进程事件源）           │
│  ├─ 产物验证（确定性规则，L2 准入门槛）                    │
│  ├─ 失败分级（FATAL / RespondToModel / Normal）           │
│  └─ 分级重试（transient + 指数退避 + deadline）           │
└────────────────────────┬────────────────────────────────┘
                         │ progress_cb 事件流（完成/失败/取消/回灌）
┌────────────────────────▼────────────────────────────────┐
│ 记忆层（L1-L4：上下文 / 向量索引 / 结构 / 模式）            │
│  ├─ L2 语义缓存双写（内存热缓存 + memoryrovol 持久化）      │
│  └─ 经验提取（任务结果与过程 → L2 缓存 / L1 状态机 / mem_d） │
└─────────────────────────────────────────────────────────┘
```

**三层闭环**：执行结果（含验证与取消事件）经 `wh_progress_cb` 事件流回灌蓝图调度 → 更新 L2 缓存质量与 L1 状态机 → 后续同任务指令命中质量更高。

---

## 3. 蓝图调度（Roadmap Sched）模块

### 3.1 落点与文件

- **位置**：`atoms/coreloopthree/` 内新增 `dispatch/` 子模块，与 `cognition/`、`execution/`、`memory/` 平级。
- **文件**：
  - `atoms/coreloopthree/include/roadmap_sched.h`（公共接口）
  - `atoms/coreloopthree/src/dispatch/roadmap_sched.c`（三级路由）
  - `atoms/coreloopthree/src/dispatch/rs_state_machine.c`（L1 状态机）
  - `atoms/coreloopthree/src/dispatch/rs_semantic_cache.c`（L2 语义缓存）
- **接线**：在 `airy_cognition_process` 入口之前挂接（`airy_cli` / loop 层注入）；命中路径不进入 LLM 管线；`wh_progress_cb` 事件流注入（回灌钩子）。
  - **已落地（2026-08-09，P2）**：`airy_cli main.c` 认知入口之前挂接三级路由（4.0b）——L1 命中输出下一步（零 Token）、L2 命中输出建议（低 Token），均不进入 LLM 管线；仅 MISS_L3 进入五阶段认知管线。L3 收敛图纸经 `airy_roadmap_sched_absorb` 登记状态机（CLI 4.1.5）。`wh_progress_cb` → `wh_rs_feed_back` 已注入执行结果回灌与取消联动。

### 3.2 公共接口与数据结构

```c
typedef struct {
    char current_step[64];      /* 当前步骤 ID（对应 GRAD 图纸节点） */
    char next_step[64];         /* 下一步骤 ID */
    char phase[64];             /* 当前阶段名称 */
    char selected_plan[128];    /* 已选方案标识（多方案收敛后） */
    uint64_t t0;                /* 图纸生成时间戳（TTL 基准） */
    uint32_t ttl_days;          /* 图纸有效期，默认 7 */
    uint32_t theta_rs;          /* L2 相似度阈值 θ（千分比，动态调整） */
    bool enable_multi_plan;     /* 多方案开关（仅复杂任务） */
} airy_rs_config_t;

typedef struct airy_roadmap_sched airy_roadmap_sched_t;

airy_err_t airy_roadmap_sched_create(const airy_rs_config_t *cfg,
                                     airy_roadmap_sched_t **out);
airy_err_t airy_roadmap_sched_process(airy_roadmap_sched_t *d,
                                      const char *input, const char *ctx_json,
                                      char **out_json);
/* 吸收：收敛图纸 / 执行结果回灌（含产物验证结果与失败分级状态） */
airy_err_t airy_roadmap_sched_absorb(airy_roadmap_sched_t *d,
                                     const airy_task_plan_t *plan,
                                     const char *exec_id,
                                     const airy_rs_absorb_meta_t *meta);
/* 取消事件注入：L1 状态机回退联动 */
airy_err_t airy_roadmap_sched_on_cancel(airy_roadmap_sched_t *d,
                                        const char *exec_id,
                                        const char *node_id);
void airy_roadmap_sched_destroy(airy_roadmap_sched_t *d);
```

```c
/* 回灌元数据：执行结果 + 验证结果 + 失败分级，共同决定 L2 准入与 L1 联动 */
typedef struct {
    const char *node_id;        /* 图纸节点/步骤 ID */
    const char *output_json;    /* 执行输出（回灌内容） */
    airy_rs_result_t result;    /* FATAL / RESPOND_TO_MODEL / NORMAL_FAIL / SUCCESS */
    airy_rs_verify_t verify;    /* PASS / FAIL / LOW_CONF / SKIP（验证器输出） */
    bool transient;             /* NORMAL_FAIL 是否 transient（可重试） */
    bool canceled;              /* 是否 AbortedOutput / 节点取消 */
} airy_rs_absorb_meta_t;
```

### 3.3 L1 状态记忆（Fast Path）

- **状态来源**：工作大厅看板当前执行条目（execution state / progress）+ sched_d 任务状态机。
- **触发**：用户指令为确定性状态转移（"继续""确认""下一步"）。
- **校验**：`S_{k+1} ∈ Out(S_k)`（Out = GRAD 图纸节点边集）；不满足立即 `FALLBACK_TO_L3`（对应规范 §3.2）。
- **取消联动**：节点取消事件 → L1 沿图纸反向边回退到最近未完成前驱（见 §4.6 协同点 3）。
- **零 Token**：B 模型职责由确定性状态机替代（agentrt 无模型内建），响应为纯状态转移输出。

### 3.4 L2 语义缓存（Fast Semantic Cache）

- **检索**：**Embedding + 向量索引**（决策已定）。Embedding 经 `llm_d` 服务获取；向量索引复用 MemoryRovol L2 Feature（HNSW，`airy_mr_l2_create/add/get_vector`）+ 吸引子网络检索（`retrieval.h`）；llm_d 不可用时降级 L3。
- **存储**：**内存 + 持久化双写**（决策已定）——内存热缓存（commons/utils/cache `cache_t`，LRU/TTL）+ MemoryRovol L1/L2 持久化（重启恢复）。
- **条目**：key = 意图向量/指纹，value = 步骤/参数建议（图纸关键节点的"意图-步骤"映射）+ 验证元数据 + 结果状态。
- **准入门槛**：仅产物验证 PASS 且非 FATAL/取消的执行结果可写入（见 §4.6 协同点 2）。
- **阈值**：`sim(q,c) ≥ θ`，θ 动态调整 `θ_{t+1} = θ_t + α·(误判率 - 目标误判率)`（目标误判率 1%-2%）。
- **命中贡献**：L1 未命中场景的 ~15%。

### 3.5 L3 五步认知决策序列

L3 走完整五阶段认知管线，内部按五步序列执行（复用现有 GCCP/GRAD 协议与 mac_framework）：

| 步骤 | 主体 | 输入 | 输出 | 失败回退 |
|:---|:---|:---|:---|:---|
| ① GCCP-1 事实确认 | B 四问 + C 判据校验 | 用户指令 | 事实基准 G（目标/约束/Q5 判据） | 无回答 → 启发式降级 |
| ② 多方案形成 | A 生成者（mac group 并行评审） | 事实基准 G | 候选方案集 {P₁..Pₙ}（n=2~3） | LLM 不可用 → 单方案（退 GRAD 路径） |
| ③ 确认方案 | C 预筛 + 用户/B 终裁 | 候选方案集 | 选定方案 P* | 全否 → 回 ② 或回 ① |
| ④ GCCP-2 再次事实确认 | C + B | P* 与事实 G | 一致性裁定（G′ ⊆ G） | 漂移 → 回 ②（≤M 次）超限退保守单路径 |
| ⑤ GRAD 逻辑确认 | A 修正 + C 四验 + B 终裁 | P* | 收敛真实图纸 | 未收敛 ≤N 轮 → 回 ② |

- **双确认防漂移**：GCCP-1 锚定"做什么"，多方案只改"如何做"，GCCP-2 确保方案未改事实，GRAD E-04 图纸级再验一次（方案级+图纸级双保险）。
- **多方案并行评审**：复用 `mac_framework` group 协作——n 候选 → 组内并行评审 → 汇总评分 → 用户/B 终裁。
  - **已落地（P2，2026-08-09）**：`airy_roadmap_sched_multiplan_*` 七接口（begin/add_candidate/review/collect/adjudicate/status/end）——入队式保存事实基准 G + 原指令；`delegate_batch` 并行委派 n 候选 × N 评审人；按任务 ID 收集回执、逐方案平均分 + approve 判定；终裁支持用户/B 指定（user）或自动最高分（auto），全否 → `rejected_all`（回②/①）。mac_framework 无新增接口（group 复用）。

### 3.6 TTL 管理

- 图纸生成时间 `t0`，有效期 `ttl_days`（默认 7）；`t - t0 > ΔT` → 状态 `STALE`，L1/L2 命中无效，强制 L3。
- absorb 时重置 `t0`；执行结果回灌成功可顺延 TTL（活跃图纸）。
  - **已落地（P2）**：`absorb(SUCCESS+PASS)` 回灌时顺延 `t0`（有活跃图纸时视为图纸活跃）。

---

## 4. 执行层五项改进设计

### 4.1 改进 1：异步可中断执行模型（Codex parallel.rs 模式）

- **新增 `airy_cancel_token_t`**（`commons/utils/sync/cancel_token.h`）：原子 `cancelled` 标志 + 回调唤醒链，贯穿 taskflow → work_hall → sched_d executor → agent_d/tool_d。
- **agent_d**：invoke 从阻塞读管道改为 `select/poll` 非阻塞 + token 轮询；取消 → SIGTERM 子进程组 → 2s 优雅窗口 → SIGKILL，以 `AbortedOutput` 收尾（与超时 -2 区分）。
  - **实施状态（2026-08-09）**：service 层已落地（`agent_read_line_timeout_ex` select 200ms 轮询 + token 检查；`agent_kill_and_reap` SIGTERM→2s→SIGKILL；`AbortedOutput` JSON，`test_service.c` 取消用例验证）。
  - **取消下探（2026-08-10 完成）**：daemon RPC 层暴露 cancel 能力——`handle_invoke` 支持可选 `request_id` 参数并注册 invoke 会话（`agent_service_invoke_begin/end`，request_id → cancel_token 会话表）；新增 `agent.cancel` RPC 方法（按 request_id 取消会话 → service 层 token 轮询命中 → 优雅终止子进程 → AbortedOutput）；`agent_d` 开启 `concurrent_clients`（invoke 长请求不阻塞事件循环，cancel 请求可达）；调用方 `daemon_rpc_call_cancelable` 在等待响应期间短轮询取消令牌，命中时发送 `agent.cancel` 后返回 `AIRY_ERR_CANCELED`；`wh_agent_handler` 透传引擎取消令牌 + 生成唯一 request_id，节点取消 → Agent 调用取消下探（taskflow `taskflow_run_node` 感知取消返回非 0 时节点标记 CANCELED 而非 FAILED）。`test_invoke_session_cancel`/`test_invoke_session_capacity` 验证会话管理。
- **tool_d**：子进程退出经 `eventfd/pipe` 注册为事件源（复用 daemon_event_driver）；`exec->lock` 仅保护统计字段（取消全段持锁）；支持并行工具并发（RwLock 门控语义：并行工具 read 并发 / 互斥 write 串行）。
  - **实施状态（2026-08-09）**：`exec->lock` 仅保护统计字段 ✅；RwLock 并发门控（写者优先，read 并发 / write 串行）✅；失败分级四态 ✅。
  - **事件源驱动（2026-08-10 完成）**：`platform.c` `airy_process_run_capture_ex` 实现事件源驱动——子进程退出经管道 EOF 事件感知（select 阻塞监听，替代 1s 固定轮询）、`waitpid WNOHANG` 非阻塞回收（替代循环结束后的阻塞 waitpid）、超时判定精确到毫秒（单调时钟 deadline）、取消令牌短片轮询（100ms 片，命中返回 `AIRY_PROCESS_RC_CANCELED` -3）；`airy_process_run_capture` 保留原签名（内部调 ex，token=NULL）。`test_platform.c` 新增正常/超时/取消三用例验证。
- **taskflow**：`run_to_completion` 改事件驱动循环 + token 检查；`airy_loop_dag_wait` 支持超时参数（消除 loop.c L2032"超时留待后续版本"注释）。
  - **实施状态（2026-08-09）**：`run_to_completion_timeout` 事件驱动 + 取消令牌 ✅（RTC 超时/取消令牌测试）；`airy_loop_dag_wait(timeout_ms)` 透传 `run_to_completion_timeout` ✅；CLI SIGINT 经 `airy_loop_dag_set_cancel_flag` 挂接 ✅。
- **取消下探**：DAG 节点级取消 → 工具级（当前只能等同步返回后丢弃），且取消事件注入蓝图调度 L1 联动（§4.6 协同点 3）。
  - **实施状态（2026-08-09）**：协同点 3 已落地（CANCELED → `wh_progress_cb` → `on_cancel` → L1 反向边回退）；工具级取消下探维持现状（等同步返回后丢弃，agent_d/tool_d RPC 层未暴露取消）。
  - **实施状态（2026-08-10 更新）**：工具级取消下探已落地——agent_d 侧 RPC cancel（invoke 会话 + `agent.cancel` 方法，见上）；调用方侧 `daemon_rpc_call_cancelable` + `wh_agent_handler` 引擎令牌透传；taskflow 节点取消语义（CANCELED ≠ FAILED）。tool_d 执行器（executor → syscall → `airy_process_run_capture`）等待机制已事件源化，取消令牌接口（`run_capture_ex`）就绪，供上层按需接入。

### 4.2 改进 2：执行产物验证层（Claude 两阶段协议）

- **新增验证策略接口 `airy_artifact_validator_t`**（`atoms/coreloopthree/src/execution/validators/`，可插拔）。
- **确定性规则集**（零生成 Token）：① exit code 归因 ② 输出模式断言 ③ 产物存在性/格式检查 ④ diff 范围核对（实际改动 vs 节点声明）。
- **接入点**：sched_d `sched_dag_write_back_node` 之前 + 工作大厅 wait 返回前。
- **结果分级**：PASS → 正常回写；FAIL(确定性) → 节点验证失败（走分级重试或标注）；规则缺失 → SKIP。
- **与 L2 联动**：验证结果作为 L2 缓存准入门槛（§4.6 协同点 2）。
- LLM 验证作为可选扩展（配置开启，低置信度 LOW_CONF 丢弃）。

### 4.3 改进 3：失败分级回传语义（Codex Fatal/RespondToModel/普通）

- **工具结果三态**（tool_d `executor.c` 结果模型扩展）：

| 分级 | 含义 | 典型场景 | 行为 |
|:---|:---|:---|:---|
| `FATAL` | 致命 | 内存/安全层异常 | 终止任务（fail-closed） |
| `RESPOND_TO_MODEL` | 回传继续 | -1 启动失败、审批拒绝 | 结果回传上层，任务不终止 |
| `NORMAL_FAIL` | 普通失败 | >0 退出码、-2 超时 | 封装 `success:false` 回传 |

- **回传路径**：executor 结果 → taskflow/工作大厅 → 上层可见"失败+错误详情"，任务继续。
- **sched_d 语义调整**：普通失败不级联取消图（可配置），仅 FATAL 级联。
- **与 L2 联动**：执行结果分级随回灌元数据流入缓存（§4.6 协同点 1）。

### 4.4 改进 4：分级重试（Codex guardian 模式）

- **错误分类**：transient（超时/连接/负载/解析失败）vs permanent（语法错误/权限拒绝/缺失依赖）。
- **重试策略**：`max_retries` + 指数退避（`base×2^n`）+ 共享总 deadline + 熔断防重试风暴。
- **接入点**：
  - taskflow 节点已有 `max_retries/retry_delay_ms` 字段（默认 0）→ 激活 + 退避算法；
  - sched_d 节点：transient 失败置回 PENDING 重新入就绪集（保 DAG 语义）；
  - mac_framework 委派失败：transient 重试（复用 delegate_batch）。
- **与 L2 联动**：transient 重试期间缓存条目标记 PENDING，重试成功转 VALID（§4.6 协同点 1）。

### 4.5 改进 5：多方案架构权衡（Claude feature-dev 模式）

- 已融入 L3 五步序列（§3.5 步骤 ②③）：多方案形成 + 并行评审 + 用户选择。
- 复用 mac_framework group 协作与 GCCP-2 防漂移约束，**不触碰 GCCP+GRAD 主链**。

### 4.6 三层协同点（深化融合，已确认技术可行）

#### 协同点 1：失败分级/重试执行结果回灌 L2 缓存

- **钩子**：`wh_progress_cb`（work_hall.c L790-816）已透传 COMPLETED/FAILED/CANCELED → 注入 `airy_roadmap_sched_absorb`（携带 `airy_rs_absorb_meta_t`）。
- **回灌规则**：
  - `SUCCESS`（含 transient 重试后成功）→ 写入 L2（双写），顺延 TTL；
  - `NORMAL_FAIL(transient)` → 缓存条目标记 PENDING，重试成功转 VALID，最终失败失效；
  - `NORMAL_FAIL(permanent)` → 不写入，记录失败指纹（防同意图反复重规划）；
  - `RESPOND_TO_MODEL` → 记录"上层改道"信号，降低相关条目优先级；
  - `FATAL` / 取消 → 不回灌，失效相关 L2 条目。
- **可行性**：cache_t（LRU/TTL）支持任意 value 结构 + `airy_mr_l2_add` 支持向量写入；work_hall 回调钩子现成。

#### 协同点 2：产物验证作为 L2 缓存准入门槛

- **准入条件**：仅 `verify == PASS` 且 `result == SUCCESS`（非 FATAL/取消）的执行结果可写入 L2。
- **分级处理**：`FAIL(确定性)` → 不缓存 + 节点走分级重试；`LOW_CONF(LLM)` → 不缓存（防低质条目稀释命中率）；`SKIP`（无规则）→ 不缓存（宁缺毋滥）。
- **缓存条目元数据**：携带 validator 版本 + 验证时间；图纸 TTL 与验证结果联动（验证过期的条目优先失效）。
- **可行性**：验证器在 sched write_back 前执行（设计已定），验证结果可随 `airy_rs_absorb_meta_t` 传入 absorb 做准入判定，无架构变更。

#### 协同点 3：异步取消与 L1 状态机联动

- **取消事件传播**：`AbortedOutput` / 节点 CANCELED → `wh_progress_cb` → `airy_roadmap_sched_on_cancel`。
- **L1 回退规则**：沿 GRAD 图纸边集反向（`Out⁻¹(S_k)`）找到最近未完成前驱作为可恢复步骤 `current_step'`；入口节点被取消 → 状态机重置回 phase 起始并失效 L2 对应分支。
- **与分级重试结合**：取消的 transient 类节点允许"取消后恢复重跑"（状态机回退 + 节点重新入就绪集）。
- **可行性**：sched_d `cancel_dag` 已归一节点 CANCELED（L1659-1690）；GRAD 图纸边集由 dispatcher 持有，可计算前驱，无需架构变更。

**可行性结论（基于实码核对）**：

| 协同点 | 现成基础 | 结论 |
|:---|:---|:---|
| 结果回灌 L2 | `wh_progress_cb`（work_hall.c L790-816）+ `cache_t`（cache_common.h）+ `airy_mr_l2_add`（layer2_feature.h） | 可行，仅需 absorb 增加 meta 参数 |
| 验证准入 L2 | 验证器（新增）+ absorb 准入判定 | 可行，验证结果入 absorb meta |
| 取消联动 L1 | `sched_service_cancel_dag` 节点归一（L1659-1690）+ progress_cb 透传 CANCELED | 可行，需新增 on_cancel + 反向边回退算法 |

### 4.7 改进 6：执行中图纸复核回路（Mid-execution Blueprint Review）

> **决策（2026-08-09，随"任务大厅作战指挥中心 + 模型分层"决策修订）**：新增改进项。既有改进 1-5 与协同点 1-3 均为"执行前设计 / 执行后回灌"，**执行期间不存在语义复核图纸的回路**——DAG 提交后 taskflow/sched_d 按图纸机械推进，节点产物可能偏离图纸意图、或图纸在执行中暴露前置假设失效，均无法在执行中检出与修正。本改进补上这一环，对应"总监在执行中复核图纸、必要时改图"的管理语义。

- **问题**：节点产物语义偏差（产物不满足节点 I/O 契约 / 偏离目标 G）与图纸缺陷（E-04 目的漂移、前置失效）只能事后发现（改进 2 确定性验证 / 协同点 1 回灌），代价是整图重跑或用户手动介入。
- **执行体交付协议（Agent Delivery Protocol, ADP）**：执行体（worker）完成任务后的交付物 = **产物 + 自验证报告 + 变更清单**，形成"提交前自验证 → 提交"的标准交付协议（对齐 Codex Auto-review / CAID 自验证提交）：
  1. **确定性门禁（决策 G）**：执行体提交前运行确定性验证（validators：exit code / 产物存在 / 格式 / diff 范围）；**FAIL 阻断提交**，触发节点级重试或标注（复用改进 4 transient/permanent 分级）。
  2. **t2（A）语义复核**：产物交付认知层后，t2 对照图纸节点 I/O 契约与 GCCP 事实基准 G 复核；偏离 → 标记 `DRIFT`；图纸缺陷（E-04 目的漂移、前置失效）→ 判定图纸需修正。
  3. **t1-f（B）终裁**：B 结合 DRIFT 判定与 GRAD 四验报告做语境终裁（accept / reject）；reject → 走 t2 增量修正。
  4. **t2 增量修正**：DRIFT / 图纸错误时，A 按 GRAD 增量补丁协议（Δ patch，差分语义，未受影响节点不重绘）修正图纸；修正后经 GRAD 四验（C 确定性）+ B 终裁收敛，从受影响节点重新入就绪集（复用 sched_d PENDING 重入与取消恢复）。
- **模型分层（决策 D）**：复核管线复用认知层三模型——执行体（worker）主推理 **t1-p（C）**、复核 **t2（A）**、终裁 **t1-f（B）**；对应 Codex 层级模型选择（coordinator 强 + worker 快）与 CAID 中央管理者/工程师分工。
- **与既有机制分层**（避免重复，各司其职）：

| 阶段 | 机制 | 归属 |
|:---|:---|:---|
| 执行前 | GCCP 事实锁 + GRAD 四验收敛 + 多方案 | 认知管线（已落地） |
| **执行中** | **本改进：确定性门禁（执行体自验证）+ t2 语义复核 + t1-f 终裁 + t2 增量修正（图纸级 re-plan）** | **新增（P3）** |
| 执行后 | 确定性产物验证（改进 2）+ 结果回灌 L2 / 状态机（协同点 1/3） | 已落地 |

- **降级链**：LLM 不可用 → 仅确定性门禁（validators）→ 无复核（现状）；t2 不可用 → t1-f 复核判定（仅标记 DRIFT，不自动改图，交人工）；t1-f 不可用 → 采纳 t2 复核结论。
- **接线点**：`wh_progress_cb` 由"状态回灌"扩展为"产物语义复核钩子"；sched_d `write_back` 之前插入复核；图纸变更经新接口 `airy_rs_replan` 驱动 L1/L2 联动（状态机重登记 + 受影响 L2 条目失效）。
- **实施状态**：设计新增，P3 规划（未实施）；其中**确定性门禁（决策 G）随改进 2 验证器落地先行（P0）**。

### 4.8 决策记录（2026-08-09）

**决策 A：日常对话全部由 B 模型（t1-f）进行**

- 现状：`cli_chat_reply` 用 t2 生成回复、t1-f 验证默认关闭（`AIRY_CHAT_T1F_VERIFY=1` 才启用）；任务/对话分类用 provider 默认模型。
- 决策：日常对话（对话集）的**生成与任务/对话分流**全部由 B 模型（t1-f）承担；t2（A）仅保留规划/生成职责（L3 步骤 ② 多方案、⑤ GRAD 修正、改进 6 深度复核）。
- 落地：`cli_chat_reply` 生成模型 t2 → t1-f；`cli_llm_classify` 分类模型默认 → t1-f；废弃 `AIRY_CHAT_T1F_VERIFY` 的"t2 生成→t1-f 验证"路径。

**决策 B：模型配置三配置点（t2=A / t1-f=B / t1-p=C），云端/本地可选，用户开关，t1-f 最先激活**

- 三个配置点：`AIRY_MODEL_T2`（A，生成者，云端为主）、`AIRY_MODEL_T1F`（B，语境终裁者/日常对话，本地为主，**最先激活**）、`AIRY_MODEL_T1P`（C，逻辑验证者，本地为主）。
- 每个配置点既可用云端 API（provider `api_base` → 云服务），也可用本地（provider `api_base` → Ollama/vLLM）；具体开关由用户在配置环节决定（llm_d provider 注册 + `$AIRY_HOME/config/model.yaml` 用户覆盖）。
- 激活顺序：**t1-f（B）最先**——日常对话与任务/对话分流依赖 B；未配置 t1-f 时系统在配置环节（CLI 启动）给出激活提醒。
- 落地：CLI 启动时打印三配置点状态（已配置/未配置 + 云端/本地指示）。

**决策 C：任务大厅 = 作战指挥中心（Task Hall as Command Center）**

- 语义：任务大厅（work_hall）是任务执行的总指挥中心——**认知层在大厅发布任务命令**（收敛图纸 → DAG 提交）；**执行层领取任务**（执行体注册为工作者，经大厅派发/领取执行）；**记忆层从大厅的任务结果与过程提取经验**（产物/结果/决策链 → mem_d + L2 语义缓存 + L1 状态机）。
- 现状基础：work_hall 已有注册/看板/取消/等待 + ops 注入；roadmap_sched 回灌（`wh_progress_cb` → absorb）；mem_d 记忆持久化（执行体 input/output 写入）。缺**"命令发布/领取"显式语义**与**"过程经验"提取**（当前只回灌结果状态，不提取执行过程经验）。
- 落地（P1）：大厅增加任务命令模型（发布者=认知层、领取者=执行体、命令=图纸节点任务单）；执行体注册/领取协议；记忆层把执行过程（决策链、验证报告、失败模式）纳入经验提取。
- 对齐：Codex 中央管理者 + 异步委派 + CAID 结构化任务单；Claude Agent Teams 共享任务列表。
- **全流程可见性（Full Visibility，2026-08-09 深化）**：任务大厅是系统唯一事实源（类比 K8s etcd 对象存储 + events），全流程"文件化"共享——认知层从思考到发布图纸的决策过程、执行层全部任务的进度/结果/问题报告，均可被认知层、记忆层与用户读取：
  - **任务文件模型**：每个任务一份结构化 JSON（图纸 plan + 命令 + 进度 + 结果 + 问题报告 + 验证报告 + 决策链），存于大厅（内存 + 持久化），全系统可读；
  - **事件流升级**：`wh_progress_cb` 从"状态透传"升级为"全量事件发布"（产物摘要、问题详情、验证结果、失败模式），认知层据此做 t2 复核 / t1-f 终裁（改进 6），调度器据此做观测驱动调度（决策 F）；
  - **可观测性 API**：按任务/节点/时间维度查询全流程（决策链、报告），支撑认知层判断与记忆层经验提取；
  - **过程经验提取**：记忆层从"结果回灌"升级为"过程提取"——失败模式、验证报告、决策链 → L2 缓存 / mem_d，认知层决策支持随经验累积增强（闭环自进化）。
  - **控制论依据**：没有观测就没有控制（Wiener）——认知层决策（复核/修正/调度）的正确性以全流程可观测为前提；层次分解（图纸 DAG）+ 反馈执行（回灌/复核）构成闭环。

**决策 D：模型分层落地（复用认知层三模型）**

- 管线：执行体（worker）主推理 **t1-p（C）** → 产物交认知层 **t2（A）复核** → **t1-f（B）终裁**（对应 GRAD 三权分立：A 复核修正 / B 终裁 / C 干活+确定性四验）。
- 现状：执行体用独立默认客户端（openlab `make_llm_client` / Rust `OPENAI_BASE_URL`），未接入三模型。
- 落地（P0）：ecosystem agents 增加模型分层配置（worker 默认 `AIRY_MODEL_T1P`、复核 `AIRY_MODEL_T2`、终裁 `AIRY_MODEL_T1F`），经 llm_d provider 路由（本地 t1-p/t1-f + 云端 t2）。
- 对齐：Codex coordinator 强 + worker 快；Claude 每子 agent 模型覆盖。

**决策 E：工作区隔离（沙箱工作目录为主，git worktree 场景叠加）**

- **选型结论（2026-08-09）**：以**沙箱工作目录**为主，git 仓库场景叠加 git worktree 优化。
  - git worktree：版本化/冲突可解/可回滚，但强依赖 git、变更必须 commit，仅覆盖代码仓库类任务；
  - **沙箱工作目录**：不依赖 git（支撑任意任务类型，契合行业底座）、与 tool_d 沙箱基础设施同构、轻量；需自建文件级 diff / merge / 快照回滚语义；
  - **Codex PR 模式**：本质是"隔离执行 + 审查 + 合并"的治理流程（云端沙箱 + git PR）。对 agentrt 借鉴其**流程形态**（隔离 → 验证 → 审查 → 合并），而非依赖 git PR 本身；agentrt 以沙箱工作目录 + 文件级产物合并实现等价治理。
- 机制：DAG 并行分支的执行体在**独立沙箱工作目录**操作（互不干扰），产物经门禁 + 复核通过后 merge 到主工作区；冲突检测与报告。
- 实施状态：P1（中改：tool_d 工作区扩展 + work_hall/sched_d 执行语义）。

**决策 F：统一治理（并行度 + Token 预算，基于 GRAD R_total 公理 II）**

- GRAD 公理 II 的资源预算向量 `R_total` 从规划期扩展到**执行期**：全局 Token 预算 + 资源感知并发调度。
- **并行上限不设硬编码小上限**——支持成千上万执行体（员工）并行；实际并发由资源治理决定（工作区/沙箱配额、worker 数、Token 预算、CPU/IO），由统一调度器动态分配（类 K8s 调度语义）。
- 注：CAID 实证"4 个接近收益天花板"针对单 LLM 会话级子 agent 编排；agentrt 是平台级（独立进程执行体），并行受资源预算约束而非固定小上限。
- 治理点：全局 Token 预算（R_total 执行期投影）；并行上限 = min(资源预算派生上限，图纸可并行度)；预算耗尽 → 熔断退串行/降级；图级 deadline（改进 4 `retry_budget_ms` 扩展）。
- 实施状态：P1（统一治理配置 + 调度器扩展）。

**决策 G：验证门禁落地**

- `output_validator` 注入 CLI（`wh_cfg.output_validator`）；确定性门禁 **FAIL 阻断节点提交**，触发节点级重试或标注（复用改进 4 transient/permanent 分级）。
- 现状：validators 已接入 work_hall wait 但仅计数 + WARN，CLI 未注入。
- 实施状态：P0（小改）。

**决策 H：执行体嵌套委派（路线图 P3+）**

- 列入路线图（P3+）：执行体遇复杂子任务可 spawn 子执行体（Codex `spawn_agent` 等价物），走 **CAID 结构化委派**（图纸节点即任务单，JSON 交付），不引入自由对话协作。
- 前置：工作区隔离（决策 E）与模型分层（决策 D）落地后方可实施。

### 4.9 任务文件模型与分级可见性（Task File Model & Tiered Visibility）

> **决策（2026-08-09）**：任务大厅全流程可见性的具体数据模型。每任务一份结构化 JSON 文件族（图纸 + 命令 + 进度 + 结果 + 问题报告 + 验证报告 + 决策链），存于大厅（内存 + 持久化），全系统可读；多租户/多项目采用"全流程可见 + 按角色授权"分级可见，认知层全量观测权不变，仅防止底座层信息越权。

#### 4.9.1 命名规范（分类编号 + 时间戳）

```
{tenant_id}.{task_id}.{category}.{ts_utc}.{seq:04d}.json
```

- `tenant_id`：租户命名空间（单租户默认 `default`）
- `task_id`：任务 ID（如 `T0001`）
- `category`：文件类别枚举（见下表）
- `ts_utc`：UTC 时间戳 `YYYYMMDDTHHMMSSmmm`（排序友好，倒序即最新）
- `seq`：该类别的追加序号（4 位，append-only 事件溯源）

| category | 含义 | 写入方 |
|:---|:---|:---|
| `blueprint` | 图纸（GCCP 目标 + GRAD 收敛计划 + 四验报告） | 仅认知层 |
| `command` | 任务命令（图纸节点任务单：handler/输入/I/O 契约/deadline/模型层） | 仅认知层 |
| `progress` | 执行进度事件（状态/百分比/活动/耗时/Token） | 本任务执行体 |
| `result` | 节点/任务结果（output/exit_code/产物引用/自验证） | 本任务执行体 |
| `issue` | 问题报告（错误码/分级/transient/重试/建议） | 执行体 + 认知层 |
| `verify` | 验证报告（确定性门禁 + t2 语义复核 + t1-f 终裁） | 执行体（门禁）+ 认知层（复核/终裁） |
| `chain` | 决策链事件（GCCP/GRAD/回灌/复核/终裁的决策记录） | 仅认知层 |

示例：`default.T0001.verify.20260809T151233000.0001.json`

#### 4.9.2 公共头部（所有文件共享）

```json
{
  "file": {
    "id": "default.T0001.verify.20260809T151233000.0001",
    "category": "verify",
    "schema": "task-file-v1",
    "tenant_id": "default",
    "task_id": "T0001",
    "node_id": "S_03",
    "ts_utc": "2026-08-09T15:12:33.000Z",
    "seq": 1,
    "prev_file": "default.T0001.progress.20260809T151200000.0003",
    "checksum": "sha256:..."
  },
  "access": {
    "owner_role": "cognition",
    "write_roles": ["cognition"],
    "read_roles": ["cognition", "executor:T0001", "user:U0001"]
  },
  "content": {}
}
```

#### 4.9.3 七类文件 content 结构

**① blueprint（图纸，认知层发布）**

```json
{
  "goal": {"endpoint":"登录模块","start":"现有项目","bottleneck":"无三方登录","audience":"用户","verify":"单测+冒烟通过","confidence":0.9,"status":"CONFIRMED"},
  "plan": {
    "plan_id": "plan-8f3a",
    "nodes": [{"id":"S_01","role":"coding","inputs":[],"outputs":["requirements_spec"],"cost_time_ms":500,"cost_mem_mb":16,"invariant_guard":false}],
    "edges": [{"from":"S_01","to":"S_02"}],
    "entry": ["S_01"]
  },
  "grad": {"rounds": 2, "final_verify": "PASS", "diff_scope": ["S_03"]},
  "multiplan": {"enabled": false, "candidates": 0, "selected": null}
}
```

**② command（命令，认知层发布）**

```json
{
  "publisher": "cognition",
  "receiver": "executor:coding_rs_v1",
  "node_task": {
    "node_id": "S_03",
    "handler": "agent:coding",
    "input": "实现 auth 模块",
    "io_contract": {"inputs": ["requirements_spec"], "outputs": ["auth_module"]},
    "deadline_ms": 30000,
    "model_tier": "t1-p",
    "workspace": {"type": "sandbox_dir", "path": "...", "is_isolated": true}
  },
  "issued_at": "2026-08-09T15:12:33.000Z"
}
```

**③ progress（进度，执行体写，事件溯源）**

```json
{
  "node_id": "S_03",
  "status": "running",
  "progress": 0.45,
  "phase": "implementing",
  "activity": "编写 auth/session.ts",
  "metrics": {"elapsed_ms": 12300, "token_used": 4520},
  "event": "progress_update"
}
```

**④ result（结果，执行体写）**

```json
{
  "node_id": "S_03",
  "status": "completed",
  "output_json": "{\"module\":\"auth\"}",
  "exit_code": 0,
  "success": true,
  "metrics": {"elapsed_ms": 18500, "token_used": 8930},
  "artifact_refs": ["auth/session.ts"],
  "delivery": {"self_verify": "PASS", "change_list": ["auth/session.ts:+128"]}
}
```

**⑤ issue（问题报告，执行体/认知层写）**

```json
{
  "node_id": "S_03",
  "error_code": "AIRY_ERR_TIMEOUT",
  "message": "执行超时",
  "failure_class": "NORMAL_FAIL",
  "transient": true,
  "retry_count": 1,
  "max_retries": 3,
  "suggestion": "增大节点 timeout_ms",
  "context": {"trace": "..."}
}
```

**⑥ verify（验证报告，执行体写门禁 + 认知层写复核/终裁）**

```json
{
  "node_id": "S_03",
  "deterministic": {
    "validators": [{"rule":"exit_code","expect":0,"actual":0,"pass":true}],
    "gate": "PASS"
  },
  "semantic": {
    "reviewer": "t2",
    "drift": false,
    "drift_detail": null,
    "contract_ok": true
  },
  "adjudication": {
    "adjudicator": "t1-f",
    "verdict": "accept",
    "confidence": 0.85
  }
}
```

**⑦ chain（决策链，认知层写，事件溯源）**

```json
{
  "event": "grad_round",
  "round": 2,
  "actor": "t2",
  "action": "apply_patch",
  "data": {"patch": {}, "affected": ["S_03"]},
  "prev": "default.T0001.chain.20260809T150900000.0007"
}
```

#### 4.9.4 事件溯源语义（append-only）

- `progress` / `issue` / `chain` 为**事件流**：每事件一个文件（seq 递增），不覆盖——全流程历史可重放、可追溯；
- 检索最新：`task_id + category` 按 `ts_utc` 倒序取 seq 最大（大厅索引）；
- 任务结束时生成**聚合索引文件**（`category=result` 汇总 + `chain` 决策链索引），供认知层复盘与记忆层经验提取；
- 文件存于 `{AIRY_HOME}/hall/{tenant_id}/{task_id}/{category}/`，与源码树隔离（路径约束）。

#### 4.9.5 分级可见性（RBAC 权限矩阵 + 多租户隔离）

**角色**：`cognition`（认知层，系统级）/ `executor`（执行体，租户内）/ `user`（用户，授权范围）/ `admin`（管理）/ `auditor`（审计只读）。

| 角色 | blueprint | command | progress | result | issue | verify | chain |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| cognition | R/W | R/W | R 全量 | R 全量 | R/W | R/W | R/W |
| executor | R 本任务 | R 本任务 | R/W 本任务 | R/W 本任务 | R/W 本任务 | R 本任务 | R 本任务 |
| user | R 授权 | — | R 授权 | R 授权 | R 授权 | R 授权 | R 授权 |
| admin | R/W | R/W | R/W | R/W | R/W | R/W | R/W |
| auditor | R | R | R | R | R | R | R |

**多租户隔离示例**（租户 A / 租户 B）：

```
认知层（系统级 service）：跨租户全量读写（全量观测权）
  - 写 tenant_a 与 tenant_b 的 blueprint / command / chain
  - 读全部 progress / result / issue / verify 做复核与经验提取

执行体 executor:coding_rs_v1（租户 A worker）：
  - 读 tenant_a/T-A0001/command/*      （自己领取的任务命令）
  - 写 tenant_a/T-A0001/progress|result|issue  （本任务节点）
  - 读 tenant_a/T-A0001/verify         （本任务门禁/复核结果）
  - 对 tenant_b 与 tenant_a 其它任务：无任何访问权
  - 不能写 blueprint / command / chain（图纸与决策仅认知层）

用户 U-A0001（租户 A 项目成员）：只读授权任务的结果/验证/进度；不读 command 内部输入

admin：跨租户全量 R/W；auditor：全量只读 + 审计日志（所有读写留痕）
```

**隔离机制（三层）**：
1. **命名空间隔离**：存储路径按 `{tenant_id}/{task_id}/{category}/` 组织 + OS 权限；
2. **应用层 ACL**：读请求携带角色 + tenant_id + task_id，服务端校验文件头部 `access.write_roles / read_roles`（精确到角色与任务，执行体 `executor:{task_id}` 才可写本任务）；
3. **写权限单一来源**：`blueprint/command/chain` 仅 cognition 可写（图纸与决策只由认知层产生）；`progress/result/issue` 仅本任务执行体 + cognition 可写。

#### 4.9.6 控制论闭环

全流程可见性支撑：观测（任务文件族）→ 认知层决策（t2 复核 / t1-f 终裁 / t2 修正，改进 6）→ 执行（执行体领取命令）→ 反馈（progress/result/issue 事件流）→ 记忆层经验提取（失败模式/验证报告/决策链 → L2 缓存）→ 认知层决策支持增强。**层次分解（图纸 DAG）+ 反馈执行（事件回灌）构成完整闭环**。

#### 4.9.7 检索与回放（chain / verify 快速定位与决策重建）

**内存索引**（大厅常驻，写入时更新）：
- 主索引：`(task_id, category) → 有序文件表`（按 `ts_utc` 倒序），定位最新文件 O(1)；
- 辅助索引：`node_id → chain/verify 文件集`（节点视图）、`error_code → issue 文件集`（失败模式检索，经验提取用）；
- 热缓存：近期文件的 JSON 解析结果缓存（LRU，复用 `cache_t`）；全量历史落盘 `{AIRY_HOME}/hall/`。

**查询 API**（`airy_hall_query_*`）：
- `chain_list(task_id, t0, t1)`：决策链事件列表（按时间）；
- `chain_get(file_id | task_id+seq)`：单事件原文；
- `chain_replay(task_id)`：按 seq 顺序重放全量 chain 事件 → 重建决策时间线（GCCP → GRAD rounds → absorb → feed_back → 复核 → 终裁）；
- `verify_list/get(task_id, node_id)`：节点验证记录（门禁/复核/终裁三字段视图）；
- 跨任务过滤：`issue` 按 `error_code`、`verify` 按 `drift=true` 检索（记忆层经验提取 / 失败模式学习）。

**回放视图**：
- **决策链时间线**（chain）：事件流按时间排列——每事件含 actor（t2/t1-f/C 确定性）、action（apply_patch / adjudicate / absorb）、affected 节点，可逐轮查看图纸如何收敛；
- **节点验证视图**（verify）：按节点聚合——确定性门禁（gate）→ t2 语义复核（drift）→ t1-f 终裁（verdict），对应改进 6 复核管线；
- **关联视图**：`issue ↔ verify ↔ result` 通过 `node_id` 关联，一次回放可定位"问题 → 验证失败 → 结果"完整因果链。

**性能策略**：
- 单任务 chain/verify 文件数通常 < 100 → 索引直取 + 聚合快照（任务结束生成的 `chain` 索引与 `result` 汇总文件一次读入）即可毫秒级回放；
- 增量回放：`chain_replay(task_id, since_seq)` 只读某轮之后的增量（对应 GRAD 差分语义）；
- 跨任务/大范围检索走 L2 语义缓存与向量索引（MemoryRovol），不经文件系统扫描。

- **实施状态**：P1（任务文件模型 + 索引 + 可观测性 API + ACL + 回放视图）。

---

## 5. 组件接线与改动点

| 模块 | 改动 | 对应改进 |
|:---|:---|:---|
| atoms/coreloopthree | 新增 `dispatch/` 子模块（Roadmap Sched：L1 状态机 + L2 缓存 + 三级路由 + 回灌/取消联动）；cognition process 入口挂接；新增 `execution/validators/`；taskflow 事件驱动 + 超时 | 三级系统 / 改进1 / 改进2 / 三协同 |
| commons/utils/sync | 新增 `cancel_token.h/.c` | 改进1 |
| daemons/agent_d | invoke 非阻塞化（select/poll + token）——service 层已落地；**RPC 层已暴露 cancel**（invoke 会话 + `agent.cancel` 方法 + concurrent_clients，2026-08-10） | 改进1 |
| daemons/tool_d | 失败分级三态 + RwLock 并发门控 + 线程池并行——已落地；**子进程等待已事件源驱动**（`airy_process_run_capture_ex`：EOF 事件 + WNOHANG 回收 + 精确超时 + 取消令牌，2026-08-10） | 改进1 / 改进3 |
| daemons/sched_d | 失败分支语义（FATAL 才级联）+ transient 重试 + 产物验证挂接 | 改进3 / 改进4 / 改进2 |
| atoms/coreloopthree/mac | 多方案并行评审（group 复用，无新增接口） | 改进5 |
| atoms/coreloopthree/work_hall | `wh_progress_cb` 注入回灌事件流（progress_cb → Roadmap Sched） | 三协同 |
| atoms/coreloopthree/work_hall | 任务大厅作战指挥中心语义：命令发布/领取 + 过程经验回灌（P1） | 决策 C |
| atoms/coreloopthree/work_hall | 执行中图纸复核钩子（改进6：门禁 + t2 复核 + t1-f 终裁，P3） | 改进6 |
| atoms/coreloopthree | 工作区隔离：DAG 并行分支独立沙箱工作目录 + 产物 merge/冲突检测（P1） | 决策 E |
| atoms/coreloopthree | 统一治理：全局 Token 预算 + 资源感知并发调度（并行不设硬上限，P1） | 决策 F |
| tools/airy_cli | 对话集生成与任务/对话分流改用 B 模型（t1-f）；启动打印三配置点提醒 | 决策 A / 决策 B |
| tools/airy_cli | `output_validator` 注入 + FAIL 触发节点重试/标注（P0） | 决策 G |
| ecosystem/agents | 模型分层配置（worker=t1-p / 复核=t2 / 终裁=t1-f）+ 自验证门禁提交（P0） | 决策 D / 改进6 |
| atoms/coreloopthree/mac | 执行体嵌套委派（`spawn_agent` 等价物，CAID 结构化任务单，P3+） | 决策 H |
| MemoryRovol | L2 向量检索 + 持久化双写（Embedding 条目）+ 执行过程经验提取 | L2 / 协同点1 / 决策 C |

---

## 6. 分阶段实施计划

| 阶段 | 内容 | 验证 |
|:---|:---|:---|
| **P0** | Roadmap Sched 骨架（L1 状态机 + 三级路由 + TTL）+ 改进3 失败分级 + 改进4 分级重试 + 协同点1（回灌钩子） | 全量 ctest + 新增分级/重试/状态机/回灌用例 |
| **P1** | 改进1 异步可中断（cancel_token + agent_d/tool_d 非阻塞 + taskflow 事件驱动）+ L2 语义缓存（Embedding + 向量索引 + 双写）+ 协同点2（验证准入） | 新增取消/并发/超时/缓存/准入用例，ASan/TSan |
| **P2** | 改进2 产物验证（validators）+ L3 五步序列多方案（mac group 并行评审）+ 协同点3（取消与 L1 联动） | 新增验证/多方案/回退用例 |

**实施状态（2026-08-09）**：P0 ✅ / P1 ✅ / P2 ✅ 全部交付，全量 ctest 回归通过。

- **P2 改进2 产物验证**：`airy_artifact_validator_t`（可插拔接口）+ 确定性规则集（① exit code 归因 ② 输出模式断言 ③ 产物存在性/格式检查 ④ diff 范围核对）；接入 sched_d `sched_dag_write_back_node` 之前 + 工作大厅 wait 返回前；验证结果随 `airy_rs_absorb_meta_t` 流入 absorb 做 L2 准入判定（协同点 2）。
- **P2 L3 五步序列多方案**：`airy_roadmap_sched_multiplan_*` 七接口交付（见 §3.5），mac group 并行评审 + 汇总评分 + 终裁（协同点 5/改进 5）。
- **P2 协同点 3**：取消与 L1 联动——`on_cancel` 沿图纸反向边回退到最近未完成前驱；入口取消 → 状态机重置回入口（取消后恢复重跑）；同时失效该节点 L2 条目；取消事件经 `wh_progress_cb` 注入。
- **认知入口接线（§3.1/§3.5）**：`airy_cli` 认知入口之前挂接三级路由（L1/L2 命中不进入 LLM 管线），L3 收敛图纸 absorb 登记状态机；TTL 顺延（§3.6）已实现。

**回归基线**：全量 ctest（146/146 全绿，含 ASan/LSan）+ GCCP/GRAD 相关测试（gccp_workhall 等）明确不触碰。

**全功能接线盘点（2026-08-09）**：核心链路全面打通（实码核验）——三级路由（CLI 认知入口 L1/L2 短路）/ plan absorb / TTL 顺延 / 回灌链（`wh_progress_cb` → `wh_rs_feed_back` → absorb / on_cancel）/ L2 语义缓存（HNSW + bigram 降级 + JSON 双写持久化 + 失败指纹 + θ 调整 + PASS 准入）/ 多方案七接口 / 产物验证（sched_d write_back 前置 + work_hall wait）/ FATAL 级联 / transient 分级重试。

**暂缓项清零（2026-08-10）**：§4.1 两处暂缓项均已实现——① agent_d RPC 层暴露 cancel（invoke 会话 + `agent.cancel` 方法 + `concurrent_clients`，调用方 `daemon_rpc_call_cancelable` + `wh_agent_handler` 引擎令牌透传 + taskflow 节点 CANCELED 语义）；② tool_d 子进程等待事件源驱动（`airy_process_run_capture_ex`：EOF 事件感知 + WNOHANG 非阻塞回收 + 精确超时 + 取消令牌 -3）。全量 ctest 151/151 通过。

**新增设计（2026-08-09）**：改进 6 执行中图纸复核回路（§4.7，P3 规划，未实施）——执行期间的产物语义复核与图纸增量修正，补全"执行前设计 / 执行中复核 / 执行后回灌"三段闭环；决策 A/B（§4.8）——日常对话由 B 模型（t1-f）生成与分流、模型三配置点（t2=A / t1-f=B / t1-p=C，云端/本地可选，t1-f 最先激活），已随 CLI 落地。

**决策落地（2026-08-09 第二批）**：决策 C-H 已记录（§4.8）——任务大厅作战指挥中心（决策 C，P1）、模型分层管线 t1-p→t2→t1-f（决策 D，P0 配置）、工作区隔离沙箱工作目录（决策 E，P1）、统一治理 R_total 执行期扩展 + 并行不设硬上限（决策 F，P1）、验证门禁 CLI 注入（决策 G，P0）、嵌套委派 P3+ 路线图（决策 H）。实施顺序：**P0**（决策 D 模型分层配置、决策 G 门禁注入）→ **P1**（决策 C 大厅语义、决策 E 工作区隔离、决策 F 统一治理）→ **P3**（改进 6 完整复核回路、决策 H 嵌套委派）。

**实施进度（2026-08-09 第三批）**：
- ✅ **P0 全部完成**：决策 D（ecosystem agents 模型分层，worker 优先 `AIRY_MODEL_T1P`，Rust cargo check 通过）；决策 G（CLI 注入 `output_validator` + wait 后 FAIL 标注）。
- ✅ **P1 决策 C 核心完成**：任务文件模型 `hall_store`（§4.9 落地）——七类文件写入 + ACL 分级可见 + `list/get/replay` 检索回放；work_hall 挂接 progress/result/issue 事件写入（独立于 roadmap_sched）；CLI 注入 `$AIRY_HOME/data/agentrt/hall`；单测 31/31 全绿（ASan 无泄漏）。
- ⏳ **待实施**：P1 决策 F（统一治理）、P3 改进 6 完整复核回路、决策 H（嵌套委派）——均为架构级改动，设计已就绪（§4.8/§4.7），按阶段推进。

**实施进度（2026-08-09 第四批）**：
- ✅ **P1 决策 E 完成（工作区隔离，沙箱工作目录）**：
  - `workspace.h/.c` 新增（决策 E 机制层）：快照（主工作区 → 独立沙箱目录递归复制 + 快照基线 `.airy_baseline/`）、合并（三方判定：目标==基线→应用 / ==工作区→跳过 / 外部改动→冲突不覆盖，删除不传播）、降级开关 `AIRY_WORKSPACE_ISOLATION=0 → ENOTSUP`、execution_id 目录穿越防护、路径收敛 `$AIRY_HOME/data/agentrt/workspaces`；跨平台（POSIX dirent / Windows FindFirstFile）。
  - work_hall 挂接（节点执行边界）：`config.main_workspace_dir`（BORROW，NULL=不隔离保持现状）；节点执行前快照主工作区 → 独立沙箱目录，invoke 注入 `workspace_dir` + `workspace_mode=isolated`（独立 params 字段，向后兼容不污染 input）；执行成功 merge 回主工作区，冲突不覆盖并写 hall_store issue 事件（`WS_MERGE_CONFLICT`）；执行失败保留隔离区供审计。
  - CLI 挂接：`AIRY_WORKSPACE_MAIN_DIR` 显式指定时启用（默认保持现状）；`AIRY_WORKSPACE_ISOLATION=0` 可整体关闭。
  - 测试：`test_workspace` 19/19（生命周期/降级/快照/三方 merge 更新/冲突/新增应用/删除不传播，ASan 无泄漏）；`test_gccp_workhall` 9/9（新增决策 E 端到端：mock agent_d + 隔离注入断言 + 产物 merge 回主工作区断言）；全量 ctest 148/148 通过。
- ⏳ **待实施**：P3 改进 6 完整复核回路、决策 H（嵌套委派）。

**实施进度（2026-08-09 第五批）**：
- ✅ **P1 决策 F 完成（统一治理，GRAD R_total 执行期投影）**：
  - `governance.h/.c` 新增（决策 F 机制层）：Token 预算池（acquire 预扣 / settle 结算校正，记账式门禁非阻塞拒绝，低水位 THROTTLED / 扣尽 CIRCUIT_OPEN）、并发槽信号量（`airy_cond_timedwait` 100ms 分片轮询可超时）、图级 deadline（登记表 + 超时熔断计数）、派生容量 `min(硬上限, 空余槽位, 剩余预算可支撑并发)`、register/unregister 配对一体化（Token 预扣失败熔断拒绝 / 槽位失败全量回吐 / 登记失败回滚前两步；unregister 未登记 no-op 防误释放，`token_actual==0` 按 estimate 中性结算不回吐）。
  - work_hall 挂接（任务级门禁）：submit 成功后 `airy_governance_register(graph_id=exec_id, est=node_count*token_per_node)`；门禁拒绝（预算不足 BUSY / 槽位满 TIMEOUT）→ cancel 该执行并返回错误码；看板登记失败回滚治理登记；终态（completed/failed/canceled/skipped）`wh_progress_cb` 注销（Token 结算 + 槽位释放 + deadline 清除）。
  - **引擎同步执行适配**：taskflow 对单节点工作流在 submit 内同步执行完毕（终态 progress_cb 先于 register 触发 → unregister no-op），register 后立即探测终态并结算（settle-sync），防 slot/token 泄漏；多节点图 submit 返回仍 RUNNING，由终态回调正常注销。
  - CLI 挂接：`AIRY_GOV_TOKEN_BUDGET` / `AIRY_GOV_SLOTS` / `AIRY_GOV_MAX_CONCURRENT` / `AIRY_GOV_TOKEN_PER_NODE` / `AIRY_GOV_DEADLINE_MS` 环境变量注入；全部未配置（无预算且无槽位）→ 不启用治理，保持现状。
  - 测试：`test_governance` 43/43（生命周期/派生容量/Token 预算三态/预扣结算回吐补扣/并发槽超时/deadline 熔断/register-unregister 一体化/不设限默认 8 槽，ASan 无泄漏）；`test_gccp_workhall` 治理挂接 2 项新增（token 门禁：wf1/wf2 准入 + wf3 BUSY + 运行中 capacity=2 + 结算后容量恢复；并发槽门禁：槽满 TIMEOUT + 释放后重提交成功）——治理测试改用 2 节点串行 DAG（n1 同步 + n2 异步）提供真实运行中窗口；同时修复决策 E 遗留：mock agent socket 就绪等待（消除 spawn RPC 竞态偶发 FAIL）与 submit 失败路径 wf 完整释放（ASan LSan 347 字节泄漏）；全量 ctest **149/149** 通过。
- ⏳ **待实施**：决策 H（嵌套委派，P3+）。

**实施进度（2026-08-09 第六批）**：
- ✅ **P3 改进 6 完成（执行中图纸复核回路）**——补全"执行前设计 / 执行中复核 / 执行后回灌"三段闭环：
  - **复核管线 `execution_review.h/.c` 新增**（机制层）：ADP 交付物（产物 + 自验证报告 + 变更清单）→ 确定性门禁（决策 G 规则集 + 产物结构契约校验：输出非空/上限/输出签名键集 E-01）→ t2（A）语义复核（DRIFT 检测，委托注入）→ t1-f（B）终裁（accept/reject，委托注入）→ 判定 PASS/DRIFT/REJECT/SKIP；**降级链**：无语义委托 → 纯门禁（FAIL→REJECT，PASS→SKIP 保持现状）/ 仅 t1-f → 直接终裁 / t1-f 不可用 → 采纳 t2 结论；统计 pass/drift/reject/skip/degraded。
  - **replan 接口（L1/L2 联动）**：`airy_rs_sm_replan`（图纸修正：受影响节点校验 + 最上游定位 + current_step 回退到受影响节点最近前驱/入口重置，支持新图纸整图重登记）；`airy_roadmap_sched_replan`（L1 回退 + L2 缓存失效受影响节点 + **重入集输出**：受影响节点 + 直接后继，供上层重新入就绪集，复用 sched_d PENDING 重入与取消恢复）。
  - **work_hall 挂接**：`config.reviewer + config.blueprint`（BORROW，NULL=不启用）；wait 返回前对聚合产物运行复核（与改进 2 验证互补）→ verify 报告写 hall_store（决策 C）→ 复核结果回灌 roadmap_sched（L2 准入：PASS 可缓存 / DRIFT 不入 / REJECT 失效）→ DRIFT/REJECT 触发 replan 联动。
  - **依赖关系落地**：决策 E（复核输入含隔离区产物/变更清单；复核失败保留隔离区语义对齐）、决策 F（复核为认知层操作消耗 R_total；DRIFT 频发为治理可观测事件；修正后节点重入重新 register 治理）。
  - 测试：`test_execution_review` 新增（复核管线生命周期/确定性门禁四态/语义委托组合判定/降级链/统计/replan L1 回退 + L2 失效 + 重入集/新图纸重登记/work_hall 端到端 PASS+replan 联动，ASan 无泄漏）；顺带修复 `AIRY_STRNCPY_TERM` 宏对 dst 两次求值导致的 `buf[buf_n++]` 双递增（replan 重入集计数 bug）；全量 ctest **150/150**（cl3_execution 为既有并行偶发，串行稳定，与本次改动无关）。
- ⏳ **待实施**：决策 H（嵌套委派，P3+）。

**实施进度（2026-08-09 第七批）**：
- ✅ **P3 决策 H 完成（执行体嵌套委派，CAID 结构化委派）**——Codex `spawn_agent` 等价物：执行体遇复杂子任务可委派子执行体，**图纸节点即任务单**（子任务单 = 子 workflow / 子图纸，JSON 交付），不引入自由对话协作：
  - **委派器 `execution_delegate.h/.c` 新增**（机制层）：深度控制（max_depth 默认 2，防无限嵌套；超限 → AIRY_EPERM + `n_depth_rejected` 统计）+ 子 workflow 提交执行（`airy_execution_delegate_run`：submit → wait，子产物 JSON 交付）+ 统计（delegated / depth_rejected / failed）；同线程同步嵌套（taskflow 同步推进模型，父 handler → 子 handler 顺序执行，无死锁、无跨线程竞态）。
  - **work_hall 挂接**：`config.delegate`（BORROW，NULL=不启用）；新增 `airy_work_hall_delegate()` API（未启用 → AIRY_ENOTSUP）；新增节点 handler 路由 **`delegate:<sub_wf_id>`**（wh_register_handlers 自动接管，从 hall 注册表取子 workflow 副本委派执行，去重键改为 handler 全名）；子执行经 submit/wait 完整路径，**天然复用决策 F 治理登记与结算、改进6 复核钩子、决策 E 工作区隔离**。
  - **replan 委派映射**：`airy_rs_delegation_map_t`（child_node_ids → parent_node_ids）+ `airy_rs_replan_ctx_t.delegation`；`airy_roadmap_sched_replan` 新增**有效受影响集解析**：受影响节点在父图纸 → 原样保留；不在父图纸但命中映射 → 解析为委派者（父节点）回退（L1 回退 + L2 失效 + 重入集基于有效集，映射父节点须在父图纸）；无映射 → NOT_FOUND。**rs_state_machine.c 不侵入**（映射解析在 roadmap_sched 层完成）。
  - **修复（submit BORROW 语义落地）**：`airy_work_hall_submit` 内部深拷贝后提交引擎（taskflow 浅拷贝所有权契约）——修复委派路径 hall 注册表克隆（生命周期至 hall destroy < loop destroy）导致的 heap-use-after-free；`taskflow_engine_register_workflow` 同 id 重注册时释放旧副本字段（委派场景同 id 子 workflow 多次提交触发泄漏）；start 失败路径完整释放副本。各调用方（airy_cli / 既有测试）同步更新为完整释放。
  - 测试：`test_execution_delegate` 新增（生命周期/配置 max_depth 默认与显式/深度超限 EPERM + 统计/嵌套返回后 depth 归 0/work_hall API ENOTSUP 与直接委派/delegate handler 端到端子产物交付/replan 委派映射：子节点 → 父节点回退 + 重入集 + L2 失效 + 无映射/映射父节点不在图纸/无 delegation 字段 → NOT_FOUND，ASan 无泄漏）；全量 ctest **151/151** 通过。

---

## 7. 风险与约束

- **GCCP/GRAD 不可替换**：L3 主链为不可变约束；多方案仅发生在双 GCCP 之间。
- **IRON-1（禁止未实现功能设计）**：每阶段交付真实可运行代码，禁止桩函数/占位实现。
- **直接替换**（决策）：不留兼容路径，以全量测试 + 新增专项用例保障。
- **Embedding 依赖 llm_d**：不可用时 L2 降级 L3（渐进式降级，不影响正确性）。
- **缓存污染**：回灌/准入机制（协同点 1/2）防止失败与低质结果污染 L2，维持命中率。
- **纯 C 核心**：新增模块全部 C11，无外部运行时依赖。
- **路径约束**：运行时数据收敛 AIRY_HOME；交付物不暴露本地绝对路径。

---

## 8. 测试与验收

- Roadmap Sched：L1 命中/未命中、L2 阈值命中/未命中、TTL 过期、三级降级链、多方案收敛、回灌准入（PASS 入 / FAIL/LOW_CONF 不入）、取消回退（前驱步骤）。
- 执行改进：取消传播（工具级）、并发窗口、失败分级三态、transient 重试退避、产物验证 PASS/FAIL。
- 执行中图纸复核（改进 6，P3）：确定性门禁 FAIL 阻断、t2 复核 DRIFT、t1-f 终裁 reject、t2 增量修正后节点重入就绪集、L1/L2 联动失效。
- 对话集 B 模型（决策 A）：对话生成与任务/对话分流走 t1-f；`AIRY_CHAT_T1F_VERIFY` 废弃路径移除。
- 配置三配置点（决策 B）：三模型独立生效、云端/本地端点可选、未配置 t1-f 时启动提醒。
- 任务大厅作战指挥中心（决策 C）：认知层发布命令 → 执行体领取 → 产物/过程经验回灌记忆层。
- 模型分层（决策 D）：执行体主推理 t1-p、复核 t2、终裁 t1-f，三模型独立生效。
- 工作区隔离（决策 E）：DAG 并行分支独立沙箱工作目录、产物 merge、冲突检测。
- 统一治理（决策 F）：全局 Token 预算、资源感知并发调度（并行不设硬上限）、预算熔断。
- 全量回归：146 项 ctest 全绿 + 新增用例。
