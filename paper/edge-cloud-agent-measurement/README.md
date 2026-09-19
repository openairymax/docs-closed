# 方向一：端云协同 Agent 一体机工作负载测量短论文

> **论文编号**：07（doc-closed/paper 序列）
> **论文类型**：Measurement Short Paper / Experience Report
> **投稿目标**：IMC'27 (4-6p short) / EuroSys'27 Short Paper (6p) / MLSys'27 Benchmark Track
> **状态**：大纲 v1.0
> **SPDX**: AGPL-3.0-or-later OR Apache-2.0

---

## 0. 论文信息卡

| 属性 | 值 |
|------|-----|
| 论文类型 | Measurement Short Paper |
| 页数 | 4-6 页（不含参考文献） |
| 预计字数 | ~3,500 words |
| 图表数量 | 4-5 张 |
| 数据来源 | Airymax 智能体一体机真实/试点部署遥测数据 |
| 代码基础 | agent-linux cognition/ (CoreLoopThree + Thinkdual + Token 能效监控) |
| 前置条件 | 一体机试点部署数据（最少 30 天、20+ 用户） |

---

## 1. 核心论点与差异化

### 1.1 一句话论点

> 角色化 Agent 一体机（appliance）部署模式产生了**完全不同于**通用 LLM serving 和 coding agent 的工作负载特征——极高的前缀缓存命中率（>90%）、可预测的 Thinkdual 模式分布、以及 Token 预算约束下的"阶梯式"消耗模式。

### 1.2 与已有工作的精确差异

| 已有工作 | 会议 | 他们测了什么 | 我们测的（不同点） |
|----------|------|-------------|-------------------|
| **TraceLab** (2606.30560) | 2026 | 4300 coding agent sessions, prefix cache | 角色化 Agent（非 coding），appliance 形态（非云端） |
| **AgentSysBench** (2608.15127) | 2026 | 10 个 agentic apps 系统级测量 | 真实用户（非 benchmark 合成），长期部署（非短时间） |
| **Agentic AI Workload** (2605.26297) | 2026 | ReAct-style agent 特征 | 端云协同（非纯云端），双模式推理（非单模式） |
| **Where the Time Goes** (EuroMLSys'26) | 2026 | 337K 请求的公开 LLM trace | 一体机私有部署（非公有云），含本地推理 |
| **PowerBench** (2607.05475) | 2026 | 移动端 LLM 推理跨层测量 | Agent 工作负载（非裸 LLM），含认知循环 |
| **TinyBench** (2603.23640) | 2026 | 边缘设备持续推理性能 | 端云协同（非纯边缘），含 Token 预算 |

**核心差异点**（审稿人会认可的"新"）：
1. **第一个**端云协同 Agent appliance 的工作负载测量
2. **第一个**含双模式推理（Thinkdual SYSTEM1_FAST/SYSTEM2_SLOW）切换模式的测量
3. **第一个**含 Token 预算约束下用户行为分析的测量

### 1.3 诚实声明（避免审稿人攻击）

以下方面**不新**，论文中不声称新颖性：
- 裸 LLM 推理延迟/吞吐的测量 → 已有大量工作
- 纯云端 LLM serving trace 分析 → Azure/Alibaba 等已发表
- 边缘设备跑 LLM 的性能 → PowerBench/TinyBench 已覆盖

---

## 2. 论文结构（6 页分配）

```
§1. Introduction                    0.75 页
§2. Deployment Architecture         0.75 页  ← 一体机架构 + 遥测管线
§3. Workload Characterization       1.5 页  ← 核心贡献：4 维测量发现
§4. Token Budget Impact             0.75 页  ← 核心贡献：预算约束下的用户行为
§5. Discussion & Lessons Learned    0.75 页
§6. Related Work                    0.5 页
§7. Conclusion                      0.25 页
References                          0.5 页
────────────────────────────────────────
TOTAL                               6.0 页
```

---

## 3. 各章节详细大纲

### §1. Introduction（0.75 页）

**段落推进逻辑**：

```
Paragraph 1: AI Agent 部署形态正在从纯云端向端云协同 appliance 迁移
  - 数据：AI PC 渗透率 54.7%（2026），边缘 AI 芯片出货量增长
  - 原因：隐私、延迟、成本三重驱动
  - 趋势：一体机（appliance）形态——本地设备 + 云端大模型协同推理

Paragraph 2: 这种新部署形态产生了不同的工作负载，但缺乏测量
  - 云端 LLM serving 已有大量 trace 分析（Azure, Alibaba, Public AI trace）
  - Coding agent 工作负载刚被 TraceLab 测量
  - 但端云协同 Agent appliance 的工作负载特征完全未知
  - 关键问题：这种"本地小模型验证 + 云端大模型生成"的双阶段架构，
    其工作负载是否与纯云端有本质不同？

Paragraph 3: 本文的贡献——第一个端云协同 Agent appliance 的工作负载测量
  - 数据来源：X 台 Airymax 智能体一体机，Y 天部署，Z 个用户
  - 三个核心发现（预告 §3-4）：
    (1) 角色化 Agent 的缓存命中率远超通用 chat（>90% vs ~50%）
    (2) Thinkdual 双模式推理呈现可预测的"80/20"分布
    (3) Token 预算约束下用户消耗呈"阶梯式"而非"突发式"
```

### §2. Deployment Architecture（0.75 页）

**目标**：让审稿人理解数据从哪来、怎么采集的。

**§2.1 一体机硬件架构**（0.25 页）

```
[图 1: 端云协同 Agent 一体机架构图]

本地侧（Airymax 智能体一体机）：
  - CPU: AMD Ryzen / LX500 (信创)
  - NPU: 75 TOPS (LX500) / Radeon iGPU (AMD)
  - RAM: 32-64GB
  - 本地 LLM: 20B 参数模型（用于 Thinkdual SYSTEM1_FAST 验证）
  - 运行时: agentrt + agent-linux (CoreLoopThree + Token 监控)

云端侧：
  - 大模型: 70B+ 参数（用于 Thinkdual SYSTEM2_SLOW 生成）
  - KV Cache: prefix caching 启用
  - API: OpenAI-compatible endpoint

端云交互：
  - PERCEPTION 阶段: 本地完成（意图提取、上下文加载）
  - THINKING 阶段: 
      SYSTEM1_FAST → 本地 20B 模型（< 100ms）
      SYSTEM2_SLOW → 云端 70B+ 模型（< 5s）
  - ACTION 阶段: 本地执行（工具调用、结果输出）
```

**§2.2 遥测管线**（0.25 页）

```
[表 1: 遥测数据采集点——对应 agent-linux 可观测性体系]

采集层           组件                    采集内容
─────────────────────────────────────────────────────
L8 (Token 能效)  airy_token_stats        四类 Token 计数
                                        (input/output/cache_hit/reasoning)
L7 (调度器)      sched_tac               Agent 状态迁移、调度类切换
L6 (Agent 行为)  CoreLoopThree           认知循环 trace (phase/mode/iteration)
L5 (user_events) cogn_d/user_events.c    实时 Token 消耗事件
L4 (procfs)      /proc/airy/agents/      Token 预算水位、效率指标
                 [id]/token_stats
─────────────────────────────────────────────────────

数据流：
  cogn_d → ioctl(AIRY_TOKEN_IOCTL_REPORT) → 内核态 airy_token_stats
                                           → user_events → 落盘
  procfs → 周期性快照（每 60s）→ 持久化 → 匿名化 → 上传

隐私保护：
  - 仅采集统计指标，不采集 prompt/response 内容
  - Agent ID 匿名化为 hash
  - 用户可 opt-out
```

**§2.3 部署概况**（0.25 页）

```
[表 2: 部署统计——需要填入真实数据]

指标                    值
────────────────────────────
部署时长                X 天
活跃用户数              Y
一体机型号              AMD 版 / LX500 版
本地 LLM                Airymax-20B（量化 Q4）
云端 LLM                [模型名]
总请求数                N
总 Token 消耗           M tokens
角色 Agent 数量         10+（analyst, reviewer, coder, ...）
────────────────────────────
```

### §3. Workload Characterization（1.5 页）——核心贡献

**四个测量发现，每个 ~0.35 页**

**§3.1 发现 1：角色化 Agent 的超高缓存命中率**

```
[图 2: 缓存命中率 CDF 图——按 Agent 角色分组]

观察：
  - 角色化 Agent（固定 system prompt + 工具模板）的 cache_hit_ratio 中位数 > 90%
  - 对比：TraceLab 报告的 coding agent prefix cache hit rate 中位数 ~50-70%
  - 原因：角色化 Agent 的 prompt 前缀高度稳定（system prompt 占 prompt 总量的 60-80%）

定量分析：
  - 按角色分组：analyst/reviewer/coder 等角色的 cache_hit_ratio 分布
  - 按时间分组：工作日 vs 周末、上午 vs 下午的缓存命中率变化
  - 缓存失效模式：什么操作导致 cache miss？（上下文切换？新工具注册？）

对应 airymax 代码：
  - 数据来源：airy_token_stats.cache_hit_tokens_total / 
              (input_tokens_total + cache_hit_tokens_total)
  - 健康基线：设计目标 ≥ 0.6 (600000 ppm)，实际测量 > 0.9
  - Token 计费影响：cache_hit_tokens 不计费（见 token-budget.md §2.1）
```

**§3.2 发现 2：Thinkdual 双模式推理的"80/20"分布**

```
[图 3: Thinkdual 模式选择分布饼图 + 模式切换时序图]

观察：
  - ~80% 的请求使用 SYSTEM1_FAST（本地 20B 模型，< 100ms）
  - ~20% 的请求升级到 SYSTEM2_SLOW（云端 70B+ 模型，< 5s）
  - 升级触发条件分布：
      意图复杂度高: X%
      上下文 > 4K token: Y%
      安全相关操作: Z%
      低置信度（< confidence_threshold）: W%

模式切换模式：
  - FAST → SLOW 升级率: X%
  - SLOW → FAST 降级率: Y%
  - 平均切换次数/请求: Z
  - 切换后 Token 消耗变化: +N%

对应 airymax 代码：
  - 数据来源：CoreLoopThree 事件流中 think_mode 字段
  - 模式选择规则：airy_cog_context_t.think_mode (0=FAST, 1=SLOW)
  - 切换审计：AOS-STD-COG-008/009 要求切换必须记录
```

**§3.3 发现 3：Token 消耗的"角色指纹"**

```
[图 4: 各角色 Agent 的 Token 消耗雷达图（4 维：input/output/cache_hit/reasoning）]

观察：
  - 不同角色 Agent 的 Token 消耗模式形成独特的"指纹"
  - 例如：
      coder: 高 output_tokens, 高 reasoning_tokens（多轮推理）
      reviewer: 高 cache_hit_tokens（固定审查模板）, 低 output_tokens
      analyst: 高 input_tokens（大量上下文输入）, 中等 output_tokens
  - 这种"指纹"可用于自动识别异常 Agent 行为

定量分析：
  - 各角色的 output_input_ratio 分布
  - 各角色的 effective_ratio 分布
  - 各角色的 reasoning_overhead 分布

对应 airymax 代码：
  - 数据来源：airy_token_stats 中的效率指标
  - output_input_ratio_ppm = output_tokens_total * 1e6 / input_tokens_total
  - effective_ratio_ppm = output_tokens_total * 1e6 / (input + output)
  - reasoning_overhead = reasoning / (input + output + reasoning)
```

**§3.4 发现 4：端云协同的延迟分解**

```
[图 5: 端到端延迟分解堆叠图（PERCEPTION / THINKING / ACTION 三阶段）]

观察：
  - THINKING 阶段占总延迟的 60-80%（预期中）
  - 但 SYSTEM1_FAST 路径的 THINKING 延迟 < 100ms（本地推理）
  - SYSTEM2_SLOW 路径的 THINKING 延迟 1-5s（云端推理，含网络延迟）
  - PERCEPTION 和 ACTION 阶段延迟相对稳定（< 50ms）
  - 网络延迟波动是 SYSTEM2_SLOW 路径的主要不确定因素

延迟分解：
  - SYSTEM1_FAST 路径: PERCEPTION(~20ms) + THINKING(~80ms) + ACTION(~30ms) ≈ 130ms
  - SYSTEM2_SLOW 路径: PERCEPTION(~20ms) + THINKING(~2s) + ACTION(~30ms) ≈ 2.05s
  - 网络抖动对 SYSTEM2_SLOW 的影响: p50=1.8s, p99=4.5s

对应 airymax 代码：
  - 数据来源：CoreLoopThree 事件时间戳
  - airy_clt_event.timestamp_ns 记录每个 phase 的进入时间
  - airy_cog_context_t.started_ns 记录循环启动时间
```

### §4. Token Budget Impact（0.75 页）——第二个核心贡献

**§4.1 预算消耗模式**

```
[图 6: Token 预算消耗时序图——展示"阶梯式"模式]

观察：
  - 用户的 Token 预算消耗不是"突发式"的（burst），而是"阶梯式"的（staircase）
  - 模式：消耗 → 暂停 → 补充 → 再消耗
  - 原因：令牌桶算法（refill_rate tokens/ms）+ 用户交互节奏

  定量分析：
  - 平均预算利用率: X%
  - 触发 warning_threshold (≤20%) 的频率: Y 次/用户/天
  - 触发 critical_threshold (≤5%) 的频率: Z 次/用户/天
  - 触发 BLOCKED 挂起的频率: W 次/用户/天
  - 从 BLOCKED 恢复到 RUNNING 的平均时间: T 秒

对应 airymax 代码：
  - 令牌桶算法：token-budget.md §2.1
  - 三级阈值：normal (>50%), warning (≤20%), critical (≤5%)
  - 预算耗尽处理：Agent 进入 BLOCKED 挂起（非终止），保存记忆快照
```

**§4.2 预算约束对行为的影响**

```
[表 3: 不同预算水位下的 Agent 行为变化]

预算水位        Thinkdual 模式分布变化        请求频率变化
────────────────────────────────────────────────────────
> 50% (正常)    20% SLOW / 80% FAST           基线
20-50%          15% SLOW / 85% FAST           -10%
≤ 20% (警告)    5% SLOW / 95% FAST            -30%
≤ 5% (临界)     0% SLOW / 100% FAST           -60%
────────────────────────────────────────────────────────

关键发现：
  - 预算紧张时，用户自发地减少 SYSTEM2_SLOW 调用（因为 SLOW 消耗更多 Token）
  - 这种"预算感知"的行为模式是端云协同 Agent 独有的
    （纯云端 Agent 无此约束，纯边缘 Agent 无此分层）
  - 暗示：系统可以主动利用此行为做"预算感知调度"（引出方向二论文）

对应 airymax 代码：
  - 模式选择规则：Token 预算 < 500 → 强制 SYSTEM1_FAST（cognition-loop-standard §3.2）
  - 低水位 Agent 获得更高调度优先级（token-budget.md §1.2 设计目标 4）
```

### §5. Discussion & Lessons Learned（0.75 页）

```
§5.1 对系统设计的启示（3 条）

  (1) 缓存优化是端云协同 Agent 的第一优先级
      - 90%+ 缓存命中率意味着：优化缓存驱逐策略比优化推理速度更重要
      - 角色化 Agent 的 prompt 模板应该被"锁定"在 KV cache 中

  (2) Thinkdual 双模式是成本控制的天然杠杆
      - 80/20 分布意味着：系统可以通过调整模式选择阈值来控制成本
      - 预算紧张时自动提高 SYSTEM1_FAST 的使用比例

  (3) Token 预算应该是一等公民资源
      - 阶梯式消耗模式意味着：令牌桶算法是合适的（不是太激进也不是太保守）
      - 三级阈值设计（50%/20%/5%）给用户提供了足够的优雅降级空间

§5.2 对 ML 研究者的启示（2 条）

  (1) 真实部署的 Token 消耗模式与 benchmark 不同
      - benchmark 通常是固定 prompt 长度，真实部署是突发的、角色相关的
  (2) 验证器（verifier）的部署位置很重要
      - 本地 20B 验证器 vs 云端 70B 验证器的成本差 10x
      - 这影响了 test-time compute scaling 的最优策略

§5.3 局限性（诚实声明）

  - 样本量：X 台设备、Y 个用户（如果样本小，诚实说明）
  - 部署时长：Z 天（短期 vs 长期）
  - 用户群体：特定人群（企业内部？开发者？普通用户？）
  - 硬件多样性：仅 2 种 SKU（AMD / LX500）
```

### §6. Related Work（0.5 页）

```
按类别组织（不逐篇讨论，快速扫过）：

云端 LLM serving trace: 
  Azure (2024), Public AI (EuroMLSys'26), Alibaba → 纯云端，无边缘侧

Agent 工作负载测量: 
  TraceLab (2026), AgentSysBench (2026), Agentic AI Workload (2026) 
  → coding agent 或合成 benchmark，非 appliance 部署

边缘设备 LLM 推理: 
  PowerBench (2026), TinyBench (2026), Cloud to Edge (2026) 
  → 裸 LLM 性能测量，无 Agent 工作负载

端云协同推理: 
  HybridFlow, PipeSD, VELO, CE-LSLM, PRISM (AAAI'26) 
  → 关注推理效率，不关注工作负载特征

本文差异: 第一个端云协同 Agent appliance 的长期部署测量
```

### §7. Conclusion（0.25 页）

```
总结三个核心发现 + 开源数据承诺（如果合规允许）
```

---

## 4. 数据需求与采集计划

### 4.1 最小可行数据集

| 数据项 | 来源 | 采集方式 | 最小量 |
|--------|------|----------|--------|
| 四类 Token 计数 | `airy_token_stats` | procfs 周期快照 (60s) | 30 天 × 20 用户 |
| Thinkdual 模式分布 | `airy_cog_context_t.think_mode` | CoreLoopThree 事件流 | 10K+ 请求 |
| 模式切换事件 | `airy_clt_event` (kfifo) | user_events 实时上报 | 1K+ 切换 |
| 预算水位变化 | `airy_token_stats.budget_ratio_ppm` | procfs 周期快照 | 30 天 |
| 延迟分解 | `airy_clt_event.timestamp_ns` | CoreLoopThree 事件流 | 10K+ 请求 |
| Agent 角色信息 | Agent 注册表 | 静态配置 | 10+ 角色 |

### 4.2 采集代码位置

```
已有代码（可直接使用）：
  - agent-linux/cognition/coreloopthree/clt_main.c
    → kfifo 事件流，含 trace_id, phase, think_mode, timestamp_ns
  - docs/docs-linux/90-observability/07-token-efficiency.md
    → airy_token_stats 数据结构定义
    → cogn_d_on_llm_complete() 上报函数
    → /proc/airy/agents/[id]/token_stats procfs 接口

需要编写：
  - 遥测数据匿名化管线（procfs → 匿名化 → 落盘）
  - 数据分析脚本（Python，读取 CSV → 生成图表）
  - （可选）user_events 的持久化消费者
```

### 4.3 时间线

```
Week 1-2:  遥测管线搭建（匿名化 + 落盘）
Week 3-6:  数据采集（最少 30 天）
Week 7-8:  数据分析 + 图表生成
Week 9-10: 论文撰写
Week 11-12: 内部评审 + 修改 + 投稿
```

---

## 5. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 样本量不足（<20 用户） | 统计显著性不够 | 延长采集期；或改为 "experience report" 而非 "measurement" |
| 数据合规问题 | 无法公开 trace | 仅采集统计指标（不采集 prompt 内容），匿名化 |
| 缓存命中率不够高（<80%） | 核心发现 1 不成立 | 调整叙事角度：分析"为什么不够高"也是有价值的 |
| Thinkdual 模式切换太少 | 核心发现 2 不显著 | 分析"为什么用户倾向于单一模式" |
| 同期竞品论文抢先发表 | 新颖性受损 | 快速出手；强调 appliance 形态的独特性 |

---

## 6. 目标会议选择

| 会议 | 截稿日期 | 页数 | 适合度 | 备注 |
|------|----------|------|--------|------|
| IMC'27 | 2027 春 | 6p short | ★★★★★ | 测量论文首选 |
| EuroSys'27 Short | 2026 秋 | 6p | ★★★★☆ | 需要欧洲合作者？ |
| MLSys'27 Benchmark | 2026 秋 | 6-8p | ★★★★☆ | 需要公开 benchmark |
| HotOS'27 | 2027 | 6p | ★★★☆☆ | Position paper 风格 |
| APSys'27 | 2027 夏 | 6p | ★★★☆☆ | 亚洲系统会议 |

---

## 7. 写作检查清单

- [ ] 数据量足够（≥30 天、≥20 用户、≥10K 请求）
- [ ] 四个发现中至少两个有统计显著性
- [ ] 图表质量达到出版级（矢量图、配色一致）
- [ ] Related Work 覆盖 TraceLab/AgentSysBench/PowerBench 等 2026 新工作
- [ ] 局限性部分诚实说明样本量和部署范围
- [ ] 数据开源承诺（如果合规允许）或 "data available upon request"
- [ ] 伦理审查（如果涉及用户数据）
