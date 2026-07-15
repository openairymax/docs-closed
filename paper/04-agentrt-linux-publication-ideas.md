# agentrt-linux 论文方向全量分析

> **范围**：agentrt-linux 独有内容（不包括 agentrt 用户态部分）
> **文档基础**：AirymaxOS 公开设计文档（130+）+ 闭源审查报告（_review_0.9.0 6 份）+ 闭源分析报告（_analysis_0.3.0 7 份）+ 闭源研究报告（_research_0.2.5/0.3.1）
> **代码状态**：设计文档 v0.9.0，审查评分 80/B（可开发状态），C 代码在 M1 阶段（2026-07-13 启动）
> **核心参考**：闭源 `_analysis_0.3.0/03b-tech-decision-linux-based.md`（5-feature 微内核化改造矩阵）、`_review_0.9.0/02-sel4-engineering-thought-analysis.md`（54 项 ES-SEL4 分析）
> **SPDX**: AGPL-3.0-or-later OR Apache-2.0

---

## 0. 重要免责声明

agentrt-linux **当前（2026-07）没有一行 C 代码**。以下所有论文方向都是基于设计文档的分析。这意味着：

- 可以投 **HotOS / APSys / PLOS**（接收 position paper / work-in-progress）
- 不能投 **OSDI / SOSP / EuroSys / ATC**（要求完整的系统实现 + 实验数据）
- 如果等到 agentrt-linux 代码写完（1.0.1，~2026-11），才能补充实验数据

---

## 论文方向 1：增量式微内核化改造方法论

**核心问题**：微内核操作系统历史上只有两条路——(a) 从零写微内核（seL4, Fuchsia, QNX），或 (b) 在微内核上跑 Linux 作为用户进程（L4Linux, MkLinux）。agentrt-linux 走出了一条**第三条路**？

**答案**：**是也不是**——严格来说这条路不是人类历史上第一次走。

**类似尝试的历史先例**：
- **FUSE (2004)**：把文件系统搬到用户态
- **UIO (2006)**：把驱动搬到用户态
- **VFIO (2012)**：把设备直通搬到用户态
- **AF_XDP (2018)**：把网络数据面搬到用户态
- **Google Snap (2016)**：用户态网络栈
- **rump kernels (2010)**：NetBSD 驱动在用户态复用

每个单独看都不是首创。但 agentrt-linux 的区别在于：
1. **不是为了性能而是为了安全**：之前所有用户态化都是为了性能或灵活性。agentrt-linux 是为了给 AI Agent 一个 capability 安全模型
2. **系统性而非单个子系统**：不是只把文件系统搬到用户态，而是调度（sched_ext）+ 通信（io_uring）+ 安全（eBPF LSM）+ 内存（CXL）**同时** 用户态化
3. **同源协同设计**：用户态的 agentrt 和内核态的 agentrt-linux 通过 [SC] 头文件双向共享，这是以前没有的

**文档依据**：`_analysis_0.3.0/03b-tech-decision-linux-based.md` 的 5-feature 微内核化改造矩阵：

```
Linux 6.6 原生特性 → 微内核化的功能等价物
──────────────────────────────────────────────
sched_ext (6.12+)   → 用户态调度策略（约等于 seL4 的调度器用户态化）
io_uring (5.1+)     → 零拷贝 IPC + 用户态服务通信（约等于 seL4 的 IPC）
eBPF (3.18+)        → 可编程内核扩展 + LSMs + struct_ops（约等于 seL4 的系统调用）
Landlock (5.13+)    → 用户态沙箱（约等于 seL4 的地址空间隔离）
userfaultfd (4.3+)  → 用户态页面管理（约等于 seL4 的内存管理）
```

**发表建议**：

| 目标 | 类型 | 概率 | 需要 |
|------|------|------|------|
| APSys 2027 | Short paper (6p) | ~45% | 不需要代码，设计分析就够了 |
| IEEE Software | Experience report | ~60% | 工程方法论，审稿人喜欢这类案例 |
| **不推荐 EuroSys/OSDI** | - | <5% | 没有实现数据和 benchmark |

**核心叙事**：这不是一篇"我们做了个新系统"的论文。这是一篇 **"我们分析了 5 个 Linux 原生功能，证明了它们加起来可以取代一个微内核"** 的论文。审稿人的兴趣点在于：这种"增量化"替代方法的效果如何——不需要重写 31 万个驱动，只需要把 sched_ext/io_uring/eBPF/Landlock/userfaultfd 组合起来，就能达到类 seL4 的安全隔离水平。

---

## 论文方向 2：seL4 ↔ Linux 工程思想的双源融合裁决

**核心贡献**：这不是技术贡献，而是 **方法论和方法论文献**的贡献。

agentrt-linux 在 `_review_0.9.0/02-sel4-engineering-thought-analysis.md` 中做了一个很系统的事：
1. 完整研读了 seL4 源码（54 项 ES-SEL4）
2. 完整研读了 Linux OLK-6.6 源码（13 项 ES-OLK）
3. 用 16 维度的双源融合裁决矩阵，逐项决定"取哪一边"

**具体的裁决结果**：

```
编码风格层 7 维度：全部采纳 Linux（Tab 8, snake_case, 最小 typedef...）
架构层 5 项：借鉴 seL4（capability, IPC, 形式化验证...）
seL4 的编码约定：完全拒绝（4 空格, camelCase, 重度 typedef）
```

这种"我不是从零做，我是从两个现有的大项目里各取一部分"的方法论，在软件工程社区是受欢迎的。ICSE-SEIP 和 IEEE Software 喜欢这类文章。

**文档依据**：`_review_0.9.0/02-sel4-engineering-thought-analysis.md` §2-3，闭源总纲 §12.5 "双源融合裁决 16 维度"。

| 维度 | Linux 6.6 | seL4 | agentrt-linux 裁决 |
|------|-----------|------|-------------------|
| 缩进 | Tab 8 | 4 空格 | Tab 8（采纳 Linux） |
| 命名 | snake_case | camelCase | snake_case（采纳 Linux） |
| typedef | 最小 | 重度 | 最小（采纳 Linux） |
| 错误处理 | errno + goto | exception_t | errno + goto（采纳 Linux） |
| 系统调用 | ~400 | 7-11 | ≤ 24（采纳 seL4 极简主义） |
| 安全模型 | DAC/MAC/LSM 混合 | 纯 capability | capability + POSIX 混合（取两边的交集） |

---

## 论文方向 3：Q16.16 定点数调度

**隐藏的亮点**：agentrt-linux 的调度设计（`02-ipc-protocol.md` §2.4 和 `06-airy-scheduling-standard.md`）要求 vtime 使用 Q16.16 定点数，**禁止 float**，因为内核态不支持浮点运算。

```
vtime_new = vtime_old + runtime * weight >> 16
```

这看起来是一个很小的技术细节，但在 Agent 调度场​​景下有一个被忽略的研究问题：**Q16.16 定点数在加权公平队列（WFQ）中的累积误差如何影响 Agent 的调度公平性？**

CFS/EEVDF 使用完全相同的加权公平队列概念，但在用户态使用 float，在内核态使用定点数。两者的精度不同——在长达数小时的 Agent 认知循环中，定点数的量子化误差会累积，可能导致 Agent 之间的调度不公平。

**如果 agentrt-linux 能做一个实验**：比较 Q16.16 vs float32 vs float64 在 1024 个 Agent、72 小时持续运行中的 vtime 漂移——这可以是一篇短论文（APSys, LCTES）。

---

## 论文方向 4：形式化验证的边界诚实声明

**核心贡献**：agentrt-linux 的 `CAVEATS.md`（在 `_analysis_0.3.0/04-microkernel-source-sel4-only.md` 中有对应讨论）声明了哪些验证了、哪些没验证。在学术界，很少有项目诚实声明"我们没有做全量形式化验证"。

agentrt-linux 的验证策略是：
- 不做全量 Isabelle/HOL 证明（因为基于 Linux 改造的复杂度不允许）
- 使用 CBMC 做关键路径的有界验证（IPC fastpath, capability 派生）
- TLA+ 做并发协议验证（CNode 派生链的并发正确性）
- 其余部分用 KUnit + kselftest + 动态分析（KASAN/KCSAN/lockdep）

这个 "honest-scoped formal verification" 理念本身有讨论价值。

**发表建议**：
| 目标 | 类型 | 概率 |
|------|------|------|
| PLOS (Programming Languages and Operating Systems) | Position paper | ~50% |
| IEEE Security & Privacy workshop | Short paper | ~40% |

---

## 论文方向 5：8 子系统 L2-L7 层次依赖模型

**文档依据**：`agentrt-linux开发路线和进度.md` §8.2 的 8 子仓依赖关系图——kernel(L2) → security/memory(L3) → cognition(L4) → services(L5) → system(L6) → cloudnative/tests-linux(L7)。

这不是一篇高影响力论文的方向。这是一个**工程管理实践**——在 8 个子系统之间建立显式的层次依赖模型，要求每个子系统的开发者只能依赖直接下层。这在 OS 工程中是一种严格的层次纪律，但在学术界没有太高的发表价值（IEEE Software 可能有兴趣，但顶会不会接受）。

---

## 综合发表路线图

| # | 方向 | 代码依赖 | 会议 | 概率 | 工时 |
|---|------|---------|------|------|------|
| **A** | seL4 ↔ io_uring 映射（优先级最高） | ❌ 不需要（设计就够） | HotOS 2027 | ~50% | 2-3 周 |
| **B** | 增量式微内核化改造方法论 | ❌ 不需要 | APSys 2027 | ~45% | 2-3 周 |
| **C** | 双源融合裁决方法论 | ❌ 不需要 | ICSE-SEIP 2027 | ~60% | 1 周写作 |
| **D** | Q16.16 定点调度误差分析 | ❌ 不需要（跑模拟器） | LCTES 2027 | ~40% | 3-4 周 |
| **E** | 诚实声明形式化验证边界 | ❌ 不需要 | PLOS 2027 | ~50% | 1-2 周 |

---

## 一句话回答

**agentrt-linux 里最有发表价值的是"seL4 语义在 io_uring 上的结构化映射"和"基于 Linux 的增量式微内核化改造方法论"**——两个都不需要实际代码，有设计文档就能写 position paper。但要冲刺顶会，必须等到 1.0.1 代码写完、跑出 benchmark 数据。
