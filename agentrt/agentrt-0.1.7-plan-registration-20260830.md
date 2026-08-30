# agentrt-0.1.7 版本改进方案——vtable 策略化 + 生态开放完整落地

> **方案编号**：PLAN-AGENTRT-0.1.7-20260830
> **方案类型**：语义级重构 + 生态开放完整落地（0.1.6 拆出范围 + 历史研究收敛）
> **登记日期**：2026-08-30
> **登记人**：Decheng Li（lidecheng@spharx.cn）
> **状态**：登记待评（提前规划稿——0.1.6y 系列完成后实施）
> **依据**：PLAN-AGENTRT-0.1.6-20260828-R2（范围声明 0.1.7 拆出项）+ 0.1.6 实证/裁决报告（P0-2a / P0-4 / P0-5）+ 插件研究 14 条清单（`00-reviews/_review_v4.4/agentrt-plugin-system-critical-devprep-20260828.md`）+ 依赖精简量化研究（已归档 `_archive_0.1.6/`，结论：不执行）

---

## 摘要

0.1.7 是 0.1.6 之后的**语义级重构版本**：将 0.1.6 物理就位的机制层升级为**机制-策略分离**的可插拔架构（vtable 策略化），并完成**生态开放的完整落地**（插件机制全量 + provider 化注册表 + 依赖图调度）。

0.1.6（已交付）完成的是"减法收敛 + 生态 SSoT 收敛 + 发布链路"，其红线声明明确将语义级改造拆出：**0.1.7 不做减法，只做机制策略分离与开放能力落地**。

## 版本路线（前置）

| 版本 | 定位 | 状态 |
|------|------|------|
| 0.1.6d / 0.1.6e | 0.1.6 正式发布（六架构 + libssl.so.3 纯净链路） | ✅ 已发布 |
| **0.1.6y 系列（4~5 个小版本）** | 修复性/制品性小版本：①airymaxrt LD_LIBRARY_PATH 隔离（系统 curl 被包内旧 libcurl 劫持，树莓派实测 symbol lookup error）；②release `latest` 标签维护（`download/latest/install.sh` 未跟随新 release）；③riscv32 等制品补齐；④doctor 运行库完整性继续加固；⑤发布基础设施零星修复 | 🔜 前置阶段 |
| **0.1.7（本方案）** | vtable 策略化 + 生态开放完整落地 | 本方案 |

> **边界**：0.1.6y 系列只承载修复与制品，**禁止混入 0.1.7 语义级变更**；0.1.7 在 0.1.6y 系列冻结后启动。

---

## 一、范围声明（V-1 ~ V-4 + 补充）

| # | 范围项 | 内容 | 0.1.6 前置状态 |
|---|--------|------|---------------|
| **V-1** | **五认知机制 vtable 策略化** | 每个认知机制（GCCP/GRAD/蓝图调度/双思考/任务大厅）暴露 `airy_*_strategy_t` vtable，机制间仅经 vtable 交互；各机制独立测试套件；换策略验证"改一不影响其他" | 0.1.6 已完成物理聚合（P0-6），公共接口不变 |
| **V-2** | **能力插槽推广四域 + 统一注册表** | `airy_*_provider_t` vtable 推广 llm/tool/storage/sandbox 四域；统一注册表（provider 化） | 0.1.6 已确认注册表基座（commons/utils/ext，P1-3）就绪 |
| **V-3** | **完整插件机制** | disposer 纪律、生命周期状态机、Capability Seam 三元组织等（插件研究 14 条清单完整落地） | 0.1.6 已落地插件子集（P1-5：离线 validator/双清单/规则库管线/SessionStart 注入） |
| **V-4** | **daemon 启动依赖图调度接入** | 18 daemon 启动顺序由统一依赖图机制调度（复用 commons 子域声明机制） | 0.1.6 已落地依赖图最小机制（P1-2，airy_depgraph 33 子域 DAG），仅 commons 子域接入 |
| **V-5**（补充） | **分配器统一接口收敛** | corekern arena/tcache 与 commons 门面统一接口（P0-5 裁决遗留）：以公共宏面为唯一接口，corekern 原语下沉或 commons 纯包装，二选一 | 0.1.6 P0-5 裁决：假重复保留两套；统一接口收敛列为 0.1.7+ 可选 |
| **V-6**（补充） | **taskflow 状态序列化收敛** | loop_dag `airy_loop_dag_status` 状态串映射并入 taskflow 状态枚举序列化（P0-2a 遗留观察） | 0.1.6 P0-2a 实证：loop_dag 为薄壳，状态映射待收敛 |

---

## 二、设计要点

### 2.1 V-1 五认知机制 vtable 策略化

**目标**：机制（结构、生命周期、调度协调）稳定在底座；策略（认知行为）以可插拔 vtable 表达，任一策略改动不影响其他模块。

```
机制（稳定）                     策略（可插拔）
──────────────────────        ──────────────────────
airy_gccp_strategy_t    ←──   gccp_default_strategy / gccp_eco_strategy ...
airy_grad_strategy_t    ←──   grad_default_strategy ...
airy_roadmap_strategy_t ←──   roadmap_default_strategy ...
airy_think_strategy_t   ←──   dual_think_strategy ...
airy_work_hall_strategy_t ←── work_hall_default_strategy ...
```

**设计约束**：
1. 每个机制暴露的 vtable 是**该机制对外交互的唯一通道**（机制间不得直接调用对方内部 API）；
2. 默认策略 = 0.1.6 现有行为（回归基线），出厂注册为 `*_default_strategy`；
3. 策略注册走 `commons/utils/ext` 能力注册表（`airy_cap_slot`，0.1.6 P1-3 已就绪）；
4. 每个机制独立测试套件：默认策略回归 + 替换策略的"改一不影响其他"验证。

**验证方式**：
- 机制 A 换策略后，机制 B/C/D/E 的全部测试不变绿通过；
- 换策略前后，核心链路（GCCP→GRAD→蓝图→执行→任务大厅）socket 行为回归。

### 2.2 V-2 能力插槽推广四域 + 统一注册表

**目标**：llm/tool/storage/sandbox 四域统一 `airy_*_provider_t` vtable + 统一注册表。

| 域 | vtable | 0.1.6 现状 | 0.1.7 动作 |
|----|--------|-----------|-----------|
| llm | `airy_llm_provider_t` | llm_d providers 同构 static 函数收敛为 provider.c（0.1.6 已做） | 推广 vtable 注册 |
| tool | `airy_tool_provider_t` | tool_d BUILTIN_TOOL_SCHEMAS 同步点已收（S-6） | provider 化 |
| storage | `airy_storage_provider_t` | heapstore 数据面 | provider 化 |
| sandbox | `airy_sandbox_provider_t` | 沙箱去 docker 化（0.1.2 完成） | provider 化 |

**约束**：四域 provider 化后，能力调用链路全量回归；注册表单一权威（`commons/utils/ext`）。

### 2.3 V-3 完整插件机制

在 0.1.6 插件子集（离线 validator / 双清单 / 规则库管线 / SessionStart 注入）基础上，完整落地插件研究 14 条清单：

| 借鉴点 | 落地位置 | 说明 |
|--------|---------|------|
| disposer 纪律 | plugins 运行时 | 资源释放确定性（分配/释放配对纪律） |
| 生命周期状态机 | plugin_d | DISCOVERED → VALIDATED → LOADED → INITIALIZED → RUNNING → DISPOSED，非法迁移拒绝 |
| Capability Seam 三元组织 | plugins 加载器 | capability（能力声明）/ seam（接入点）/ plugin（实现体）三层分离 |
| 双清单（运行时/发布） | skills/plugins | 0.1.6 已落地，补齐 schema 校验闭环 |
| 会话级上下文注入 | hook_d | SessionStart 通道（0.1.6 P1-5 已落地，0.1.7 完整化） |

### 2.4 V-4 daemon 启动依赖图调度接入

**目标**：18 daemon 启动顺序由统一依赖图机制调度（复用 airy_depgraph 的 DAG + 拓扑排序）。

- 各 daemon 声明启动依赖（如 `llm_d` → 无依赖；`gateway_d` → 依赖 cjson/microhttpd/websockets 对应能力；`market_d` → 依赖 sched_d）；
- 启动器按拓扑序拉起，环检测 fail-closed（复用 0.1.6 P1-2 机制）；
- 与现有"并行拉起 + wait_all_socks"的启动体验保持兼容（依赖就绪即启动，无依赖冲突时行为不变）。

### 2.5 V-5 分配器统一接口收敛（可选，评估后定）

P0-5 裁决遗留：corekern arena/tcache（内核原语）与 commons 门面（AIRY_MALLOC 族）接口不统一。0.1.7 评估两条路径：
- A：corekern 原语下沉为公共底层，commons 门面纯包装（统一 API 面含 stats/contains/calloc）；
- B：维持两套分层（文档化边界），仅收敛死面候选（corekern arena/tcache/refcount、commons memory_debug）。

> 实施前置：依赖环评估（atoms→commons 单向，方向明确）；不做则维持现状。

### 2.6 V-6 taskflow 状态序列化收敛（低风险）

loop_dag `airy_loop_dag_status` 的状态串映射并入 taskflow 状态枚举序列化能力，loop_dag 薄壳更薄。

---

## 三、实施路线

| 阶段 | 内容 | 验证 |
|------|------|------|
| **M0** | vtable 基础设施：`airy_strategy_t` 基座 + 注册表接入（commons/utils/ext）+ 默认策略登记 | 编译 + 注册表单测 |
| **M1** | V-1 五机制逐个 vtable 化（每机制独立提交 + 独立测试套件） | 全量 ctest + 18 daemon 冒烟 + 换策略验证 |
| **M2** | V-2 四域 provider 化（llm → tool → storage → sandbox） | 能力调用链路回归 |
| **M3** | V-3 完整插件机制（生命周期状态机 + disposer + Capability Seam） | 插件生命周期测试 + 非法迁移拒绝测试 |
| **M4** | V-4 daemon 启动依赖图调度接入 | 18 daemon 依赖拓扑 + 冒烟 |
| **M5** | V-5/V-6（可选）分配器接口收敛 + taskflow 状态序列化 | 分配器单测 + taskflow 回归 |

**阶段红线**：每个 M 阶段独立可验证、可回滚；V-1 的每个机制 vtable 化单独提交（bisect 友好）。

---

## 四、验收标准（草案）

1. 五认知机制各自可独立换策略，互不影响（独立测试套件全绿）；
2. 四域能力插槽统一注册表，provider 化改造后能力调用链路回归通过；
3. 插件全生命周期状态机 + disposer 纪律测试通过（非法迁移 fail-closed）；
4. daemon 启动依赖图调度接入，18 daemon 冒烟通过（依赖序正确、无环）；
5. （可选）分配器统一接口收敛评估完成并落地 / 或维持分层的文档化决策；
6. loop_dag 状态串映射收敛入 taskflow，无行为变化；
7. 0.1.7 制品发布（复用 0.1.6e 构建台 + 发布链路）。

---

## 五、风险与约束

| 风险 | 缓解 |
|------|------|
| vtable 化回归风险高（73k 行引擎语义改造） | 默认策略 = 0.1.6 行为（回归基线）；分机制独立提交 + 独立测试套件；可单机制回滚 |
| 机制间经 vtable 交互后引入间接层性能损耗 | vtable 调用为直接函数指针（零额外间接）；关键路径基准对比 |
| provider 化破坏既有能力调用链 | 每域 provider 化后全量回归；注册表 fail-closed |
| 插件全生命周期引入状态管理复杂度 | 状态机显式枚举 + 非法迁移拒绝测试 |
| 依赖图调度改变启动时序引入竞态 | 拓扑序 + 现有 wait_all_socks 兼容；无依赖冲突时行为不变 |
| 范围蔓延（混入修复性改动） | 修复性改动一律归 0.1.6y 系列；0.1.7 只做语义级/开放能力 |

**红线**：不砍 corekern/commons；不新增 daemon；纯 C；[SC] 字节冻结；一个技术点一个权威源；机制稳定、策略可插拔。

---

## 六、与既有文档的衔接

| 文档 | 衔接 |
|------|------|
| `agentrt-0.1.6-improvement-plan-20260828.md`（R2） | 0.1.7 范围 = R2 拆出项（vtable 策略化 + 能力插槽 + 完整插件 + 依赖图调度） |
| `_archive_0.1.6/agentrt-0.1.6-P0-2a-dag-empirical-gate-20260829.md` | 遗留观察 V-6（taskflow 状态序列化） |
| `_archive_0.1.6/agentrt-0.1.6-P0-5-allocator-verdict-20260830.md` | 遗留 V-5（分配器统一接口收敛） |
| `_archive_0.1.6/agentrt-dependency-slimming-list-20260828.md` | 用户决定不执行（构建时间收益≈0 的量化结论），0.1.7 不纳入 |
| `00-reviews/_review_v4.4/agentrt-plugin-system-critical-devprep-20260828.md` | V-3 完整插件机制依据（14 条清单） |

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. | agentrt-0.1.7 方案（提前规划稿） | 2026-08-30
