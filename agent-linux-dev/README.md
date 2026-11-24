Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agent-linux（AirymaxOS）技术参考与历史归档

> **文档定位**: agent-linux 内部机密文档总索引（设计依据 + 历史归档 + 逐版本任务方案）
> **版本**: v2.0.0（2026-11-01 目录整合：7 个散目录归并为 `10-references/` 与 `20-archive/`）
> **最后更新**: 2026-11-01
> **主要读者**: agent-linux 架构委员会 + 内核开发组

---

## 1. 文档定位与说明

本目录存放 agent-linux（AirymaxOS）的**内部机密文档**，用于梳理设计来源、工程依据与历史决策：

1. **梳理设计来源**：openEuler 社区的技术规范、OLK-6.6 内核源码、微内核实现（seL4/Zircon/Minix3）、
   行业最新理论，是 AirymaxOS 设计的重要参考。这些依据集中登记在 `10-references/`，便于溯源。
2. **消化吸收后再落地**：对参考来源必须经过消化吸收，转化为 AirymaxOS 自身的设计表达，
   不在正式设计文档中直接照搬。
3. **正式设计文档分层**：面向用户的正式设计文档位于 `docs/docs-linux/`，使用 AirymaxOS 自身语言表述；
   本目录作为参考依据与规范溯源，两者保持分层。
4. **历史可追溯**：逐版本的评审报告与目录结构设计属于**已归档的历史记录**，集中在 `20-archive/`，
   只读不改写（除非修正失效路径），不作为当前设计的规范依据。

---

## 2. 目录结构

```
docs-closed/agent-linux-dev/
├── README.md                                    # 本文件 — 总索引
│
├── 10-references/                               # 设计依据（参考来源 + 账本生成器）
│   ├── README.md                                # 索引与方法论
│   ├── openeuler-tech-reference/                # openEuler 技术规范参考（14 篇）
│   │   ├── README.md
│   │   ├── 01-scheduler-spec.md                 # 调度器（EEVDF + sched_ext）
│   │   ├── 02-io-uring-spec.md                  # io_uring 异步 I/O
│   │   ├── 03-ebpf-spec.md                      # eBPF 可编程扩展
│   │   ├── 04-memory-spec.md                    # 内存管理（MGLRU + CXL）
│   │   ├── 05-security-spec.md                  # 安全子系统（LSM + capability）
│   │   ├── 06-ipc-spec.md                       # IPC 子系统
│   │   ├── 07-rust-support-spec.md              # Rust 内核模块支持
│   │   ├── 08-coding-standard-spec.md           # 编码规范与工程标准对照
│   │   ├── 09-cognition-spec.md                 # 认知 kthread 工程规范
│   │   ├── 10-olk66-vanilla-diff.md             # OLK-6.6 与 vanilla 差异（LAYER 依据）
│   │   ├── 11-layer-feasibility-study.md        # LAYER 方案可行性论证
│   │   ├── 12-build-and-flash-strategy.md       # 编译与烧录策略
│   │   └── 13-obs-remote-build.md               # sw_64 OBS 远程构建
│   ├── olk66-source-mapping/                    # OLK-6.6 源码 → AirymaxOS 概念映射（8 篇）
│   │   ├── README.md
│   │   ├── 01-sched-ext-mapping.md              # sched_ext → SCHED_AGENT
│   │   ├── 02-io-uring-mapping.md               # io_uring → AgentsIPC
│   │   ├── 03-bpf-mapping.md                    # eBPF → 可编程扩展
│   │   ├── 04-mm-mapping.md                     # mm → MemoryRovol
│   │   ├── 05-security-mapping.md               # security → Cupolas
│   │   ├── 06-cognition-mapping.md              # kthread/accel/drm_sched → CoreLoopThree
│   │   └── 07-engineering-toolchain-mapping.md  # 工程工具链（含 Rust 支持）→ 工程标准
│   ├── microkernel-design-ref/                  # 微内核设计参考（6 篇）
│   │   ├── README.md
│   │   ├── 01-sel4-reference.md                 # seL4
│   │   ├── 02-zircon-reference.md               # Zircon
│   │   ├── 03-minix3-reference.md               # Minix3
│   │   ├── 04-microkernel-strategy.md           # 微内核化改造策略对照
│   │   └── 05-sel4-extension-plan.md            # seL4 拓展型改造方案
│   ├── industry-best-practices/                  # 行业最新理论与最佳实践（4 篇）
│   │   ├── README.md
│   │   ├── 01-latest-theory.md                  # 最新微内核 / OS 理论
│   │   ├── 02-best-practices.md                 # 行业最佳实践汇总
│   │   └── 03-airymaxos-synthesis.md            # 技术方案综合（Euler + 理论 → AirymaxOS）
│   └── generators/                              # 任务账本生成器（8 个脚本）
│       ├── bp_seed.py                           # 种子：WP / LOC / 依赖边
│       ├── bp_gen.py                            # 引擎：闭包 / 拓扑排程 / 渲染
│       ├── bp_002_gen.py                        # 0.0.2 方案生成
│       ├── bp_003_gen.py                        # 0.0.3 方案生成
│       ├── bp_003_assets.py                     # 0.0.3 存量抵扣基线快照
│       ├── bp_004_seed.py                       # 0.0.4 种子：WP / LOC / 依赖边 / 模块与泳道
│       ├── bp_004_prose.py                      # 0.0.4 散文：§0~§4、§9~§19（含四份专项方案内嵌）
│       └── bp_004_gen.py                        # 0.0.4 引擎：DEBT / 里程碑 / 排程 / 断言 / 表格发射
│
├── 20-archive/                                  # 历史归档（只读）
│   ├── README.md                                # 索引
│   ├── reviews/                                 # 逐版本评审（36 个轮次，157 篇）
│   │   ├── _analysis_0.3.0/                     # 阶段性分析
│   │   ├── _research_0.2.1/ _research_0.2.5/ _research_0.3.1/
│   │   ├── _review_0.1.1/ … _review_0.9.0/      # 0.x 系列
│   │   ├── _review_v1.0/ _review_v1.9/
│   │   ├── _review_v2.0/ … _review_v2.9/
│   │   └── _review_v3.0/ … _review_v3.6/
│   └── designs/                                 # 目录结构设计（4 篇）
│       ├── _design_0.2.1/01-agent-linux-directory-structure.md
│       ├── _design_0.2.2/01-directory-structure-optimization.md
│       ├── _design_0.2.3/01-agent-linux-directory-structure.md
│       └── _design_0.2.4/01-agent-linux-directory-structure.md
│
├── 0.0.2-极境OS任务方案.md                       # 0.0.2 版施工账本（生成器产出）
├── 0.0.3-极境OS任务方案.md                       # 0.0.3 版施工账本（生成器产出 + §13~§16 收尾整合）
├── 0.0.4-极境OS任务方案.md                       # 0.0.4 版施工账本（生成器产出；§16~§19 内嵌四份专项方案全文）
├── AirymaxOS-终端验证命令墙.md                   # 终端验证命令速查
├── 提交信息治理册.md                             # 三端提交信息扫描结果与历史改写窗口
├── agentrt-linux基本工程标准规范.md              # 工程标准规范（OS-STD 编号体系）
├── agentrt-linux开发路线和进度.md                # 主图纸（开发路线与进度）
└── agentrt-linux验收实验任务卡草案.md            # 验收实验任务卡
```

> **命名约定**：`10-` / `20-` 前缀为目录分层序号（依据类 → 归档类），
> 子目录名不带数字前缀，避免出现 `10-references/01-xxx` 的双层编号。

---

## 3. 使用规范

### 3.1 何时参考本目录

AirymaxOS 开源设计文档（`docs/docs-linux/`）的编写和修订流程（三段式）：

1. **先参考 openEuler**：查阅 `10-references/openeuler-tech-reference/` 中对应子系统的技术规范
2. **再参考行业最新理论**：查阅 `10-references/industry-best-practices/` 中的最新理论和最佳实践
3. **最后形成 AirymaxOS 技术方案**：综合前两者，形成 AirymaxOS 自己的技术方案，
   写入 `docs/docs-linux/`，使用 AirymaxOS 自身语言，不直接引用 openEuler

需要源码级溯源时，查阅 `10-references/olk66-source-mapping/`；
需要微内核实现对照时，查阅 `10-references/microkernel-design-ref/`。

### 3.2 参考文档与正式设计文档分层规范

| 规则 | 说明 |
|------|------|
| **BAN-INTERNAL-001** | 外部技术规范的直接参考与溯源记录集中在 `docs-closed/agent-linux-dev/10-references/` 维护 |
| **BAN-INTERNAL-002** | 正式设计文档 `docs/docs-linux/` 以 AirymaxOS 自身语言表述，不直接照搬 "openEuler" 等来源描述 |
| **BAN-INTERNAL-003** | 参考文档中的外部内容必须经过**消化吸收**后，才能体现在正式设计文档中 |
| **BAN-INTERNAL-004** | 本目录定位为设计溯源与规范依据，面向用户的对外交付以 `docs/docs-linux/` 正式设计文档为准 |
| **BAN-INTERNAL-005** | 正式设计文档中的技术方案表述必须用 **AirymaxOS 自身语言**，不能是 openEuler 的直接翻译 |

### 3.3 IRON-9 v2 代码共享原则下的参考方式

IRON-9 v2（同源且部分代码共享）下，外部技术规范参考方式：

1. **共享契约层**（`include/airymax/`）：参考 openEuler 的 UAPI 接口设计规范，但不直接复制 openEuler 代码
2. **语义同源层**：参考 openEuler 的子系统实现思路（如 sched_ext 调度策略、io_uring 零拷贝机制），
   形成 AirymaxOS 自己的实现方案
3. **完全独立层**：AirymaxOS 专属机制（systemd 集成、Kbuild）独立设计，不参考 openEuler 对应实现

### 3.4 任务账本纪律

`0.0.x-极境OS任务方案.md` 一律由 `10-references/generators/` 下的脚本确定性产出：

```
bp_seed.py（改 WP / LOC / 依赖边） → bp_gen.py（引擎） → bp_00x_gen.py（版本方案）
输出：agent-linux-dev/0.0.x-极境OS任务方案.md
```

**账本永远由脚本产出，人工只改种子。** 手工修改账本会在下一次重算中丢失。

---

## 4. 与正式设计文档的关系

| 维度 | 内部参考与归档（本目录） | 正式设计文档（`docs/docs-linux/`） |
|------|------------------------------|--------------------------------------|
| 定位 | 设计溯源、规范依据、历史记录 | 面向用户的交付（AGPL v3 + Apache 2.0） |
| openEuler 引用 | 直接参考与溯源记录 | 消化吸收后以 AirymaxOS 自身语言表述 |
| 技术深度 | 深度技术规范（源码级） | 设计方案级（架构 + 接口 + 数据流） |
| 编写语言 | 中文为主 | 中文为主 |
| 版本同步 | 与正式设计文档同步更新 | 与内部参考同步更新 |

---

## 5. 文档清单（2026-11-01 目录整合后实测）

| 目录 | 文件数 | 行数 | 定位 |
|------|--------|------|------|
| `10-references/openeuler-tech-reference/` | 14 | 10,447 | openEuler 技术规范参考 |
| `10-references/olk66-source-mapping/` | 8 | 6,079 | OLK-6.6 源码映射 |
| `10-references/microkernel-design-ref/` | 6 | 2,114 | 微内核设计参考 |
| `10-references/industry-best-practices/` | 4 | 915 | 行业最新理论与最佳实践 |
| `10-references/generators/`（Python） | 5 | 4,051 | 任务账本生成器 |
| `20-archive/reviews/` | 157 | 72,016 | 逐版本评审归档 |
| `20-archive/designs/` | 4 | 5,657 | 目录结构设计归档 |
| 根级方案与规范 | 12 | — | 逐版本任务方案 + 工程标准 + 主图纸 |

> 行数为 2026-11-01 整合时的实测值，随文档修订自然变化；文件数为权威计数。

---

## 6. 相关文档

- 开源设计文档：`docs/docs-linux/README.md`（19 模块三层体系）
- 工程标准规范：`docs/docs-linux/50-engineering-standards/README.md`（IRON-9 v2 定义）
- Airymax 架构原则：`docs/00-architectural-principles.md`（五维正交 24 原则）
- agentrt 工程标准：`docs-closed/0.1.1工程标准规范手册.md`（17 类规则编号体系）

---

> **文档结束** | AgentRT 开源维护团队
