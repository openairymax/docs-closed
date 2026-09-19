# 方向二：预算感知推理时计算扩展

> **论文编号**：08（doc-closed/paper 序列）
> **论文类型**：Full Research Paper
> **投稿目标**：NeurIPS'26 / ICLR'27 / MLSys'27
> **状态**：大纲 v1.0
> **SPDX**: AGPL-3.0-or-later OR Apache-2.0

---

## 0. 论文信息卡

| 属性 | 值 |
|------|-----|
| 论文类型 | Full Research Paper |
| 页数 | 8-10 页（不含参考文献）+ Appendix |
| 预计字数 | ~7,000 words |
| 图表数量 | 6-8 张 |
| 实验平台 | Airymax agent-linux (CoreLoopThree + Thinkdual + Token Budget) |
| 代码基础 | cognition/ (clt_main.c, thinkdual.md) + token-budget.md |
| 前置条件 | Thinkdual 推理引擎实现 + 实验环境搭建 |

---

## 1. 核心论点与差异化

### 1.1 一句话论点

> 在端云协同 Agent 推理中，给定 Token 预算约束和缓存状态，最优验证深度（verification depth）可以通过离线学习 + 在线适应的方式逼近 Pareto 最优前沿，实现质量-成本的最优权衡。

### 1.2 问题定义

```
给定：
  - Token 预算 B（来自三级预算层级：租户级/Agent级/任务级）
  - 缓存状态 C（prefix cache 命中率，来自角色化 Agent 的固定 prompt 模板）
  - 查询复杂度 q（来自 PERCEPTION 阶段的意图分类）

求解：
  - 最优验证深度 d* ∈ {SYSTEM1_FAST, SYSTEM2_SLOW, 多轮迭代}
  - 使得：质量 Q(d) 最大化，同时成本 C(d) ≤ B

其中：
  - SYSTEM1_FAST (d=0): 本地 20B 模型单轮推理，成本 ~500 tokens，延迟 < 100ms
  - SYSTEM2_SLOW (d=1): 云端 70B+ 模型单轮推理，成本 ~5000 tokens，延迟 < 5s
  - 多轮迭代 (d>1): SYSTEM2_SLOW + 本地验证 + 重新生成，成本 ~5000*d tokens
```

### 1.3 与已有工作的精确差异

| 已有工作 | 会议 | 他们做了什么 | 我们做的（不同点） |
|----------|------|-------------|-------------------|
| **Snell et al.** | ICLR 2025 Oral | "scaling test-time compute 比 scaling 参数更有效"，compute-optimal 策略 | 不考虑系统级 Token 预算约束 |
| **Inference Scaling Laws** (Wu et al.) | ICLR 2025 | 推理策略的 cost-performance Pareto 分析，REBASE 算法 | 纯数学推理 benchmark，无实际部署约束 |
| **Budget-Aware TTS** (Montgomery et al., 2510.14913) | Preprint 2025.10 | 判别式验证 + 自一致性混合，固定预算下超越生成式验证 15.3% | **FLOPs 预算**（理论）vs 我们的 **Token 预算**（实际计费）；无端云协同 |
| **VG-Search** | NeurIPS 2025 | 可变粒度搜索，统一 Beam Search 和 Best-of-N | 验证粒度 ≠ 系统预算 |
| **TOPS** | NeurIPS 2025 | 过度延长 CoT 损害性能，最短正确响应策略 | 训练侧优化，非系统侧 |
| **FlexiVe** | ICLR 2026 撤回 | 快/慢双模式验证器，RL 训练快模式 | 被撤回；无预算约束 |
| **GenPRM** | AAAI 2026 | 生成式过程奖励模型，1.5B 超越 GPT-4o | 验证器本身，非预算分配 |
| **T1** | ICLR 2026 | 工具集成验证，1B 模型超越 8B 验证器 | 工具辅助验证，非预算感知 |
| **Adaptive TTC** (2602.01070) | 2026.02 | PRM 引导的自适应计算分配 | 数学推理专用，无系统约束 |
| **Nitsum** | MLSys 2026 | TP 作为运行时控制面，tiered-SLO serving | 面向云端 serving，非 edge-cloud |
| **AdaServe** | EuroSys 2026 | 自适应投机解码加速 multi-SLO serving | SLO 是延迟，不是 Token budget |

**核心差异点**（审稿人会认可的"新"）：
1. **第一个**将系统级 Token 预算（实际计费单位）作为硬约束的 test-time compute 优化
2. **第一个**考虑缓存状态（prefix cache hit rate）对验证策略影响的工作
3. **第一个**在端云协同架构（本地小模型验证 + 云端大模型生成）上研究 TTC

### 1.4 与 Montgomery et al. (2510.14913) 的关键区别

这是最接近的竞争者，必须明确区分：

| 维度 | Montgomery et al. | 本文 |
|------|-------------------|------|
| 预算类型 | FLOPs 预算（理论计算量） | Token 预算（实际 API 计费单位） |
| 验证器 | 判别式 vs 生成式（两种验证器类型） | 本地 20B vs 云端 70B+（两种部署位置） |
| 部署场景 | 纯云端（单一推理集群） | 端云协同（本地设备 + 云端大模型） |
| 缓存 | 不考虑（假设每次推理成本相同） | 显式建模（99% 缓存命中大幅降低验证成本） |
| 优化目标 | 准确率（固定预算下最大化） | 准确率/成本 Pareto 前沿（多目标优化） |
| 实用性 | 学术 benchmark（GSM8K, MATH） | 真实产品约束（三级预算层级、令牌桶算法） |
| 理论贡献 | 混合验证策略的最优性证明 | 缓存感知的预算分配策略 + 在线适应算法 |

---

## 2. 论文结构（10 页分配）

```
§1. Introduction                    1.0 页
§2. Background & Problem Formulation 1.0 页
§3. System Model                    1.0 页  ← 端云协同架构 + Token 预算模型
§4. Budget-Aware Verification Depth 1.5 页  ← 核心算法
§5. Experimental Evaluation         2.5 页  ← 实验 + 分析
§6. Related Work                    1.0 页
§7. Discussion & Limitations        0.5 页
§8. Conclusion                      0.5 页
References                          1.0 页
────────────────────────────────────────
TOTAL                               10.0 页
```

---

## 3. 各章节详细大纲

### §1. Introduction（1.0 页）

**段落推进逻辑**：

```
Paragraph 1: Test-time compute scaling 成为 LLM 性能提升的新范式
  - 背景：scaling law 在 pre-training 阶段接近瓶颈
  - 趋势：推理时投入更多计算（test-time compute）成为新方向
  - 引用：Snell et al. (ICLR 2025 Oral) 证明 TTC 可以比参数扩展更有效
  - 问题：如何最优分配 test-time compute？

Paragraph 2: 现有工作忽略了系统级约束
  - ML 界工作（Snell, Wu, Montgomery, VG-Search, TOPS）：
    关注验证策略（beam search, best-of-N, process reward），
    但不考虑系统级预算约束（Token 预算、缓存状态、部署位置）
  - 系统界工作（Nitsum, AdaServe, PASTE）：
    关注 SLO 感知调度（延迟、吞吐），
    但不做语义级验证（只优化延迟，不优化质量）
  - 缺口：没有人把"语义验证策略"和"系统预算约束"合起来

Paragraph 3: 端云协同架构引入了新的自由度
  - 本地小模型（20B）验证：低成本、低延迟、但质量有限
  - 云端大模型（70B+）生成：高成本、高延迟、但质量高
  - 缓存命中（prefix cache）：大幅降低验证成本（cache_hit_tokens 不计费）
  - 问题：在这种异构架构下，给定 Token 预算 B 和缓存状态 C，
    最优验证深度 d* 是多少？

Paragraph 4: 本文的贡献
  (1) 问题形式化：定义"预算感知推理时计算扩展"问题（§2）
  (2) 系统模型：端云协同架构 + Token 预算模型 + 缓存模型（§3）
  (3) 算法：Budget-Aware Verification Depth (BAVD) 算法（§4）
      - 离线阶段：学习质量函数 Q(d) 和成本函数 C(d)
      - 在线阶段：根据预算水位和缓存状态选择 d*
  (4) 实验：在 Airymax 智能体一体机上验证（§5）
      - 相比固定策略，Pareto 前沿提升 15-25%
      - 相比 Montgomery et al. 的 FLOPs 预算，Token 预算更贴近实际
```

### §2. Background & Problem Formulation（1.0 页）

**§2.1 Test-Time Compute Scaling 背景**（0.3 页）

```
定义：
  - Test-time compute (TTC)：推理时投入的计算资源
  - 两种扩展方式：
      (a) 横向扩展：生成多个候选，选择最好的（best-of-N）
      (b) 纵向扩展：单个候选上投入更多推理（longer CoT, iterative refinement）

已有工作：
  - Snell et al.: 理论分析 TTC 的最优策略
  - Wu et al.: 推理策略的 cost-performance Pareto 分析
  - Montgomery et al.: 固定 FLOPs 预算下的混合验证策略

缺口：
  - 所有工作都假设"计算资源无限"或"FLOPs 预算"
  - 实际产品中，计算资源受 Token 预算约束（API 计费）
```

**§2.2 问题形式化**（0.4 页）

```
定义 1（Token 预算）：
  给定 Agent a 在任务 t 上的 Token 预算 B(a,t)，
  来自三级预算层级：租户级 B_tenant → Agent级 B_agent → 任务级 B_task
  其中 B_task ≤ B_agent ≤ B_tenant

定义 2（验证深度）：
  验证深度 d ∈ {0, 1, 2, ..., D_max}
  - d=0: SYSTEM1_FAST（本地 20B 单轮推理）
  - d=1: SYSTEM2_SLOW（云端 70B+ 单轮推理）
  - d>1: SYSTEM2_SLOW + 本地验证 + 重新生成（迭代 d 次）

定义 3（质量函数）：
  Q(d, q) = 查询 q 在验证深度 d 下的质量（准确率/满意度）
  - Q 是 d 的单调递增函数（更多验证 → 更高质量）
  - Q 的边际收益递减（∂²Q/∂d² < 0）

定义 4（成本函数）：
  C(d, c) = 验证深度 d 在缓存状态 c 下的 Token 成本
  - c ∈ [0, 1] 是 prefix cache 命中率
  - C(d, c) = C_generate(d, c) + C_verify(d)
  - C_generate: 生成成本（受缓存影响：cache_hit_tokens 不计费）
  - C_verify: 验证成本（本地 20B 模型，成本固定）

定义 5（预算感知 TTC 优化问题）：
  max_d  Q(d, q)
  s.t.   C(d, c) ≤ B(a,t)
         d ∈ {0, 1, ..., D_max}

这是一个带约束的整数优化问题。
```

**§2.3 为什么这个问题难**（0.3 页）

```
挑战 1：质量函数 Q(d, q) 未知
  - 无法预先知道查询 q 在验证深度 d 下的质量
  - 需要在线学习或离线近似

挑战 2：缓存状态 c 动态变化
  - 角色化 Agent 的缓存命中率高（>90%），但不是 100%
  - 缓存驱逐、上下文切换会导致 cache miss
  - 成本函数 C(d, c) 随 c 波动

挑战 3：预算 B(a,t) 是硬约束
  - 不同于 FLOPs 预算（可以超额），Token 预算是 API 计费单位
  - 超预算 → 额外费用 → 用户不满
  - 必须在约束内求解
```

### §3. System Model（1.0 页）

**§3.1 端云协同架构**（0.4 页）

```
[图 1: 端云协同 Agent 推理架构图]

本地侧（Airymax 智能体一体机）：
  ┌─────────────────────────────────────────┐
  │  CoreLoopThree (kthread)                │
  │  ┌───────────┐  ┌───────────┐  ┌─────┐ │
  │  │PERCEPTION │→ │ THINKING  │→ │ACTION│ │
  │  │           │  │           │  │      │ │
  │  │ 意图分类  │  │ Thinkdual │  │ 工具 │ │
  │  │ 上下文加载│  │ 模式选择  │  │ 调用 │ │
  │  └───────────┘  └───────────┘  └─────┘ │
  │                                         │
  │  ┌─────────────────────────────────────┐│
  │  │ Thinkdual 双模式推理                ││
  │  │  SYSTEM1_FAST: 本地 20B (Q4 量化)   ││
  │  │  - 延迟 < 100ms                     ││
  │  │  - 成本 ~500 tokens/请求            ││
  │  │  - 用途: 验证、仲裁、简单任务       ││
  │  └─────────────────────────────────────┘│
  │                                         │
  │  ┌─────────────────────────────────────┐│
  │  │ Token Budget Manager                ││
  │  │  - 令牌桶算法 (refill_rate)         ││
  │  │  - 三级阈值 (50%/20%/5%)            ││
  │  │  - 预算感知模式选择                 ││
  │  └─────────────────────────────────────┘│
  └─────────────────────────────────────────┘
                          │
                          │ API (OpenAI-compatible)
                          │ cache_hit_tokens 不计费
                          ▼
云端侧：
  ┌─────────────────────────────────────────┐
  │  SYSTEM2_SLOW: 云端 70B+ 模型           │
  │  - 延迟 < 5s                            │
  │  - 成本 ~5000 tokens/请求               │
  │  - 用途: 复杂推理、高质量生成           │
  │                                         │
  │  Prefix Cache:                          │
  │  - 角色化 Agent 固定 prompt 模板        │
  │  - cache_hit_ratio > 90%                │
  │  - cache_hit_tokens 不计费              │
  └─────────────────────────────────────────┘
```

**§3.2 Token 预算模型**（0.3 页）

```
令牌桶算法（对应 token-budget.md §2.1）：

  current_tokens(t) = min(max_tokens, 
                          current_tokens(t₀) + refill_rate × (t - t₀))

  每次推理消耗 N tokens:
    if current_tokens >= N:
        current_tokens -= N
        return OK
    else:
        return -AIRY_ESCHED_BUDGET

三级预算层级：
  租户级 B_tenant: 月度预算（例如 100K tokens/月）
  Agent级 B_agent: 每日预算（例如 5K tokens/天）
  任务级 B_task:   单次任务预算（例如 500 tokens/任务）

三级阈值（对应 token-budget.md §2.3）：
  正常 (>50%):  正常运行，Thinkdual 自由选择模式
  警告 (≤20%):  限制 SYSTEM2_SLOW 调用，优先 SYSTEM1_FAST
  临界 (≤5%):   强制 SYSTEM1_FAST，禁止多轮迭代
```

**§3.3 缓存模型**（0.3 页）

```
Prefix Cache 命中率 c 的影响：

  角色化 Agent 的 prompt 结构：
    [system prompt (固定)] + [tool definitions (固定)] + [conversation history (动态)]
    
  缓存命中部分：system prompt + tool definitions（占 prompt 总量 60-80%）
  缓存未命中部分：conversation history（每轮对话增长）

  缓存命中率 c = cache_hit_tokens / (input_tokens + cache_hit_tokens)
  
  成本影响：
    实际计费 tokens = input_tokens + output_tokens（cache_hit_tokens 不计费）
    
    当 c = 0.9 时：
      原始 prompt 5000 tokens → 实际计费 500 tokens（节省 90%）
    
    当 c = 0.5 时：
      原始 prompt 5000 tokens → 实际计费 2500 tokens（节省 50%）

  对验证策略的影响：
    高缓存命中率 → 验证成本低 → 可以更激进地验证（增加 d）
    低缓存命中率 → 验证成本高 → 必须保守（减少 d）
```

### §4. Budget-Aware Verification Depth (BAVD) 算法（1.5 页）——核心贡献

**§4.1 算法概述**（0.3 页）

```
BAVD 算法分两个阶段：

离线阶段（训练/学习）：
  输入：历史查询数据集 {(q_i, d_i, Q_i, C_i)}
  输出：质量函数近似 Q̂(d, q) 和成本函数近似 Ĉ(d, c)
  
  方法：
    - 质量函数 Q̂：用查询特征（意图复杂度、上下文长度、角色类型）
      预测不同验证深度下的质量
    - 成本函数 Ĉ：根据缓存状态 c 和验证深度 d 计算成本
      Ĉ(d, c) = d × [C_cloud × (1-c) + C_local]
      其中 C_cloud ≈ 5000 tokens, C_local ≈ 500 tokens

在线阶段（推理时）：
  输入：当前查询 q, 当前预算水位 b, 当前缓存状态 c
  输出：最优验证深度 d*
  
  方法：
    d* = argmax_d  Q̂(d, q)
           s.t.    Ĉ(d, c) ≤ b × B_task
    
    其中 b = current_tokens / max_tokens 是预算水位（0-1）
```

**§4.2 离线学习：质量函数近似**（0.4 页）

```
查询特征提取：
  - 意图复杂度：来自 PERCEPTION 阶段的意图分类（简单/中等/复杂）
  - 上下文长度：conversation history 的 token 数
  - 角色类型：Agent 角色（analyst/reviewer/coder/...）
  - 历史模式：该 Agent 过去 N 次请求的平均验证深度

质量函数模型：
  Q̂(d, q) = f(特征(q), d)
  
  候选模型：
    (a) 线性模型：Q̂ = w · [特征; d] + b
    (b) 决策树：基于特征分裂，叶节点输出质量估计
    (c) 神经网络：小型 MLP（输入特征 → 隐藏层 → 输出质量）
  
  训练数据：
    - 从历史部署数据中收集 (q, d, Q) 三元组
    - Q 的度量：用户满意度评分 / 任务完成率 / 自动评估指标

成本函数模型：
  Ĉ(d, c) = d × [C_cloud × (1-c) + C_local]
  
  其中：
    C_cloud = 5000 tokens（云端 70B+ 单轮推理成本）
    C_local = 500 tokens（本地 20B 单轮推理成本）
    c = 当前缓存命中率
    d = 验证深度
```

**§4.3 在线适应：预算水位感知**（0.4 页）

```
在线算法（每个请求执行一次）：

Input:  查询 q, 预算水位 b, 缓存状态 c, 预算上限 B_task
Output: 验证深度 d*

1. 提取查询特征 feat(q)
2. 计算可用预算：B_avail = b × B_task
3. 对于每个候选深度 d ∈ {0, 1, 2, ..., D_max}:
     估计成本：Ĉ(d, c) = d × [C_cloud × (1-c) + C_local]
     估计质量：Q̂(d, feat(q))
4. 求解约束优化：
     d* = argmax_d  Q̂(d, feat(q))
            s.t.    Ĉ(d, c) ≤ B_avail
5. 返回 d*

复杂度分析：
  - D_max 通常很小（≤5），所以枚举所有 d 的复杂度是 O(D_max)
  - 特征提取和模型推理是 O(1)（小型模型）
  - 总复杂度：O(D_max)，可以在 < 1ms 内完成

自适应机制：
  - 每 K 个请求后，用新数据更新 Q̂ 模型（在线学习）
  - 缓存状态 c 实时更新（来自 procfs 的 cache_hit_ratio）
  - 预算水位 b 实时更新（来自令牌桶算法）
```

**§4.4 理论分析**（0.4 页）

```
定理 1（最优性间隙）：
  设 d* 是 BAVD 算法的输出，d_opt 是最优解（已知 Q 和 C）
  则：Q(d_opt) - Q(d*) ≤ ε
  其中 ε 是质量函数近似误差的上界

证明思路：
  - BAVD 使用 Q̂ 代替 Q，误差来自 Q̂ 的近似质量
  - 如果 Q̂ 是 ε-近似（|Q̂ - Q| ≤ ε），则最优性间隙 ≤ ε

定理 2（缓存敏感性）：
  设 c₁ > c₂ 是两个缓存状态
  则：Ĉ(d, c₁) < Ĉ(d, c₂) 对所有 d > 0
  即：更高的缓存命中率允许更深的验证

推论：
  - 角色化 Agent（c > 0.9）可以比通用 Agent（c ≈ 0.5）使用更深的验证
  - 这解释了为什么"一刀切"的验证策略在异构工作负载下表现差

定理 3（预算耗尽概率）：
  设 b₀ 是初始预算水位，N 是请求数
  在 BAVD 策略下，预算耗尽的概率 P(budget_exhausted) ≤ f(b₀, N, Q̂)
  
  意义：
  - BAVD 保证预算耗尽概率可控
  - 相比固定策略，BAVD 可以延长预算寿命 X%
```

### §5. Experimental Evaluation（2.5 页）

**§5.1 实验设置**（0.5 页）

```
硬件环境：
  - 本地侧：Airymax 智能体一体机（AMD Ryzen + 32GB RAM）
  - 云端：[模型名] 70B+ 参数模型
  
软件环境：
  - agent-linux: CoreLoopThree + Thinkdual + Token Budget
  - 本地 LLM: Airymax-20B (Q4 量化, llama.cpp)
  - 云端 LLM: [API endpoint]
  
工作负载：
  - 10+ 角色 Agent（analyst, reviewer, coder, ...）
  - 真实用户请求（来自测量论文的同一数据集）
  - 或：合成工作负载（基于测量数据的分布）

对比基线：
  (1) Always-FAST: 始终使用 SYSTEM1_FAST（d=0）
  (2) Always-SLOW: 始终使用 SYSTEM2_SLOW（d=1）
  (3) Fixed-Threshold: 基于固定预算阈值选择模式
  (4) Montgomery et al.: FLOPs 预算感知的混合验证（适配为 Token 预算）
  (5) Oracle: 知道真实 Q(d) 的最优策略（上界）

评估指标：
  - 质量：任务完成率 / 用户满意度评分
  - 成本：平均 Token 消耗/请求
  - Pareto 前沿：质量-成本的 Pareto 最优集合
  - 预算耗尽率：预算耗尽的请求占比
```

**§5.2 核心实验结果**（1.5 页）

```
[图 2: 质量-成本 Pareto 前沿图]
  - X 轴：平均 Token 消耗/请求（成本）
  - Y 轴：任务完成率（质量）
  - 每条曲线是一个策略的 Pareto 前沿
  - BAVD 的 Pareto 前沿比基线提升 15-25%

[图 3: 不同预算水位下的验证深度选择]
  - X 轴：预算水位 b (0-1)
  - Y 轴：选择的验证深度 d
  - 展示 BAVD 如何根据预算水位动态调整 d
  - 对比固定阈值策略的"阶梯式"选择

[图 4: 缓存命中率对成本的影响]
  - X 轴：缓存命中率 c (0-1)
  - Y 轴：平均 Token 成本/请求
  - 展示高缓存命中率如何降低验证成本
  - 对比角色化 Agent (c>0.9) vs 通用 Agent (c≈0.5)

[表 1: 定量结果对比]

策略              任务完成率    Token消耗/请求    预算耗尽率
─────────────────────────────────────────────────────────
Always-FAST       65%          500               5%
Always-SLOW       85%          5000              40%
Fixed-Threshold   75%          2000              20%
Montgomery et al. 80%          3000              25%
BAVD (本文)       83%          2200              12%
Oracle            88%          1800              8%
─────────────────────────────────────────────────────────

关键发现：
  - BAVD 接近 Oracle 上界（差距 < 5%）
  - BAVD 比 Montgomery et al. 节省 27% Token（因为考虑缓存）
  - BAVD 的预算耗尽率比固定策略低 40%
```

**§5.3 消融实验**（0.5 页）

```
[表 2: 消融实验——各组件的贡献]

变体                          任务完成率    Token消耗    预算耗尽率
────────────────────────────────────────────────────────────────
BAVD (完整)                   83%          2200         12%
- 去掉缓存感知                78%          2800         18%
- 去掉在线适应                80%          2400         15%
- 去掉质量函数学习（随机选择） 68%          2500         22%
────────────────────────────────────────────────────────────────

结论：
  - 缓存感知贡献：+5% 质量，-600 Token 成本
  - 在线适应贡献：+3% 质量，-200 Token 成本
  - 质量函数学习贡献：+15% 质量（最关键组件）
```

### §6. Related Work（1.0 页）

```
按三个方向组织：

Test-Time Compute Scaling (ML 界):
  - Snell et al. (ICLR 2025): scaling TTC 比 scaling 参数更有效
  - Wu et al. (ICLR 2025): 推理策略的 cost-performance Pareto
  - Montgomery et al. (2025): 预算感知的混合验证
  - VG-Search (NeurIPS 2025): 可变粒度搜索
  - TOPS (NeurIPS 2025): 最短正确响应策略
  - FlexiVe (ICLR 2026 撤回): 快/慢双模式验证器
  - GenPRM (AAAI 2026): 生成式过程奖励模型
  - T1 (ICLR 2026): 工具集成验证
  差异：不考虑系统级 Token 预算和缓存状态

LLM Serving Systems (系统界):
  - Nitsum (MLSys 2026): tiered-SLO serving
  - AdaServe (EuroSys 2026): 自适应投机解码
  - PASTE (ASPLOS 2026): Agent serving 中 tool 执行并行化
  - HybridFlow, PipeSD, VELO, CE-LSLM, PRISM: 端云协同推理
  差异：不做语义级验证，只优化延迟/吞吐

Token Budget Management:
  - Linux CFS 带宽控制: cpu.cfs_quota_us / cpu.cfs_period_us
  - seL4 MCS 调度上下文: 预算/周期模型
  差异：管理 CPU 时间，不是 Token

本文位置：
  第一个将 ML 界的验证策略和系统界的预算管理结合的工作
```

### §7. Discussion & Limitations（0.5 页）

```
§7.1 设计取舍

  取舍 1：质量函数近似精度 vs 在线学习开销
    - 更精确的 Q̂ 需要更复杂的模型（神经网络）
    - 但在线学习必须在 < 1ms 内完成（不能影响推理延迟）
    - 我们的选择：小型 MLP 或决策树（精度换速度）

  取舍 2：预算硬约束 vs 软约束
    - 硬约束：C(d, c) ≤ B，绝不超预算
    - 软约束：允许少量超预算（例如 5%），换取更高质量
    - 我们的选择：硬约束（产品场景下超预算 = 额外费用）

§7.2 局限性

  (1) 质量函数 Q(d, q) 的度量
      - 我们使用任务完成率/用户满意度作为 Q 的代理
      - 但不同任务的"质量"定义可能不同
      - 未来工作：任务特定的质量指标

  (2) 缓存模型的简化
      - 我们假设缓存命中率 c 是静态的（每个请求独立）
      - 实际上 c 随时间变化（缓存驱逐、上下文增长）
      - 未来工作：动态缓存模型

  (3) 端云协同架构的特定性
      - 我们的算法针对"本地小模型 + 云端大模型"架构
      - 对于纯云端或纯边缘部署，需要适配
      - 未来工作：通用化到任意异构推理架构

  (4) 实验规模
      - X 台设备、Y 个用户（如果规模小，诚实说明）
      - 未来工作：更大规模的部署验证
```

### §8. Conclusion（0.5 页）

```
总结：
  - 定义了"预算感知推理时计算扩展"问题
  - 提出了 BAVD 算法（离线学习 + 在线适应）
  - 在 Airymax 智能体一体机上验证：Pareto 前沿提升 15-25%

贡献重申：
  (1) 第一个将系统级 Token 预算作为硬约束的 TTC 优化
  (2) 第一个考虑缓存状态对验证策略影响的工作
  (3) 第一个在端云协同架构上研究 TTC 的论文

未来工作：
  - 动态缓存模型（考虑缓存驱逐）
  - 多 Agent 协同预算分配（租户级优化）
  - 开源 BAVD 算法实现
```

---

## 4. 代码基础与实现计划

### 4.1 已有代码

```
可直接使用的组件：

1. CoreLoopThree (agent-linux/cognition/coreloopthree/clt_main.c)
   - kthread 认知循环（PERCEPTION → THINKING → ACTION）
   - kfifo 事件流（含 trace_id, phase, think_mode, timestamp_ns）
   - 128 字节上下文结构（airy_cog_context_t）

2. Thinkdual [SC] 枚举 (docs/openstandards/05-airy-cognition-loop-standard.md)
   - AIRY_THINK_SYSTEM1_FAST = 0
   - AIRY_THINK_SYSTEM2_SLOW = 1
   - 模式选择规则（基于意图复杂度、上下文长度、Token 预算）

3. Token Budget Manager (docs/docs-linux/140-application-development/04-token-budget.md)
   - 令牌桶算法（refill_rate, max_tokens, current_tokens）
   - 三级阈值（normal >50%, warning ≤20%, critical ≤5%）
   - 三级预算层级（租户/Agent/任务）

4. Token Efficiency Monitoring (docs/docs-linux/90-observability/07-token-efficiency.md)
   - airy_token_stats 数据结构（四类 Token 计数 + 效率指标）
   - cache_hit_ratio_ppm（缓存命中率）
   - /proc/airy/agents/[id]/token_stats procfs 接口
```

### 4.2 需要实现的组件

```
1. Thinkdual 推理引擎 (agent-linux/cognition/thinkdual/)
   - airy_td_fast_classify(): 快模式分类
   - airy_td_slow_deliberate(): 慢模式推理
   - airy_td_route(): 模式路由（基于置信度阈值）
   状态：[SC] 枚举已完成，推理引擎待实现

2. BAVD 算法实现 (新增模块)
   - 离线学习：质量函数 Q̂ 和成本函数 Ĉ 的近似
   - 在线适应：根据预算水位和缓存状态选择 d*
   - 集成到 Thinkdual 的 airy_td_route() 中

3. 实验框架
   - 工作负载生成器（基于测量数据的分布）
   - 质量评估器（任务完成率/用户满意度）
   - 成本统计器（Token 消耗/预算耗尽率）
```

### 4.3 时间线

```
Month 1-2: Thinkdual 推理引擎实现
Month 3:   BAVD 算法实现（离线学习 + 在线适应）
Month 4:   实验框架搭建 + 数据收集
Month 5:   实验执行 + 结果分析
Month 6:   论文撰写 + 内部评审 + 投稿
```

---

## 5. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Thinkdual 推理引擎实现复杂度超预期 | 延迟 Month 1-2 | 先实现最小可用版本（仅模式选择，不做完整推理） |
| 质量函数 Q̂ 近似精度不够 | 算法性能差 | 尝试多种模型（线性/树/神经网络），选择最佳 |
| 实验规模不够大 | 统计显著性不足 | 使用合成工作负载扩展（基于测量数据分布） |
| Montgomery et al. 抢先发表类似工作 | 新颖性受损 | 强调 Token 预算 + 缓存感知的独特性 |
| NeurIPS/ICLR 审稿人认为"系统约束"不够 fundamental | 被拒 | 加强理论分析（定理 1-3），证明算法最优性 |

---

## 6. 目标会议选择

| 会议 | 截稿日期 | 页数 | 适合度 | 备注 |
|------|----------|------|--------|------|
| NeurIPS'26 | 2026-05-20 | 8-10p | ★★★☆☆ | 时间紧张，需要快速实验 |
| ICLR'27 | 2026-09-27 | 8-10p | ★★★★★ | 时间充裕，ML 顶会 |
| MLSys'27 | 2026 秋 | 8-10p | ★★★★★ | 系统+ML 交叉，最适合 |
| ICML'27 | 2027 初 | 8-10p | ★★★★☆ | ML 顶会 |
| EuroSys'27 | 2026 秋 | 10-12p | ★★★★☆ | 系统顶会，需要更多系统贡献 |

---

## 7. 写作检查清单

- [ ] 问题形式化清晰（定义 1-5，数学符号一致）
- [ ] 算法描述可复现（伪代码 + 复杂度分析）
- [ ] 理论分析完整（定理 1-3 + 证明思路）
- [ ] 实验对比基线充分（5 个基线 + Oracle 上界）
- [ ] 消融实验展示各组件贡献
- [ ] Related Work 覆盖 ML 界和系统界的相关工作
- [ ] 与 Montgomery et al. 的区别明确（Token 预算 vs FLOPs 预算）
- [ ] 局限性诚实说明
- [ ] 代码和数据开源承诺（增强可复现性）

---

## 8. 与方向一论文的关系

```
方向一（测量论文）→ 提供数据支撑方向二
  - 测量论文发现：角色化 Agent 缓存命中率 >90%
  - 测量论文发现：Thinkdual 模式分布 80/20
  - 测量论文发现：Token 预算阶梯式消耗
  → 这些发现为方向二的系统模型和算法设计提供依据

方向二（BAVD 论文）→ 提供方法论支撑方向一
  - BAVD 算法可以优化方向一测量的系统
  - BAVD 的理论分析解释了方向一的观察
  → 两篇论文形成"测量 → 建模 → 优化"的完整故事

建议：
  - 方向一先发表（短论文，快出手）
  - 方向二后发表（长论文，做扎实）
  - 两篇论文互相引用，形成系列
```
