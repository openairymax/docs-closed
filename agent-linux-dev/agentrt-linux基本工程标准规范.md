Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agent-linux（AirymaxOS）基本工程标准规范

> **文档定位**: agent-linux（AirymaxOS，极境智能体操作系统）闭源工程标准规范总纲——agentrt 工程标准的**执行细则**，对齐 `docs/docs-linux/50-engineering-standards/` 权威体系（00-handbook OS-IRON 16 条 + 04-philosophy + 05-development-process + 130-roadmap/06-acceptance-criteria 110 项 OS-ACC）
> **保密级别**: SPHARX Ltd 内部参考，**闭源不公开**
> **版本**: v3.6（2026-08-01 三轮审查闭环全面重写版，登记 v3.6/v3.6b/v3.6c 三轮审查 68 项改进闭环状态）
> **最后更新**: 2026-08-01
> **适用范围**: AirymaxOS 架构委员会 + 内核开发组 + 8 子仓维护者
> **审查状态**: v3.6 三轮深度审查完成（第一轮 v3.6 核心机制 29 项 = P0-1+P1-11+P2-17 / 第二轮 v3.6b 基础设施 22 项 = N1-N22 / 第三轮 v3.6c 工程标准 17 项 = E1-E17，三轮回合计 68 项改进，闭环状态登记见附录 A）
> **核心约束**: IRON-9 v3 同源且部分代码共享——[SC] 共享契约层物理宿主于 `kernel/include/uapi/linux/airymax/`（H1 硬约束：magic 0x41524531 / capability_badge offset 40-47）
> **同源映射**: agentrt `docs/00-architectural-principles.md`（五维正交 24 原则）+ `docs/docs-linux/50-engineering-standards/00-engineering-standards-handbook.md`（OS-IRON 16 条）+ `09-ssot-registry.md`（规则编号 SSoT，v0.2.8）+ `130-roadmap/06-acceptance-criteria.md`（110 项 OS-ACC）
> **理论根基**: Linux 6.6 内核基线（vanilla 6.6.147 纯主线 + sw_64 架构导入）内核工程思想 + seL4 微内核工程思想（架构层选择性借鉴）+ Airymax 体系并行论（Multibody Cybernetic Intelligent System）
> **术语说明**: 本文档中保留的 "OLK-6.6" 均为 openEuler 官方分支名称或路径引用（如 `01Reference/kernel-OLK-6.6`、`10-references/openeuler-tech-reference/`），非概念引用。所有概念引用已统一为 "Linux 6.6 内核基线"。
> **工程取向**: "Linux 6.6 为基、seL4 为鉴"——编码风格层完全采纳 Linux 6.6 内核基线（Tab 8 / snake_case / 最小 typedef / K&R / 80 列 / errno+goto / kernel-doc），seL4 影响仅在架构层（capability / 消息传递 / 服务用户态化 / 形式化验证）被选择性借鉴
> **关联研究**: v3.6 三轮审查报告（`20-archive/reviews/_review_v3.6/`：07 第一轮改进建议 + 17 第二轮改进建议 v3.6b + 23 第三轮改进闭环 v3.6c + 08/18 闭环摘要）+ LAYER 方案可行性（`10-references/openeuler-tech-reference/11-layer-feasibility-study.md`）+ OBS 远程构建（`10-references/openeuler-tech-reference/13-obs-remote-build.md`）+ 形式化验证（`docs/docs-linux/80-testing/10-formal-verification.md`）

---

## 目录

- [第 1 章 总则与工程标准框架](#第-1-章-总则与工程标准框架)
- [第 2 章 代码规范](#第-2-章-代码规范)
- [第 3 章 代码格式](#第-3-章-代码格式)
- [第 4 章 工程思想](#第-4-章-工程思想)
- [第 5 章 开发流程](#第-5-章-开发流程)
- [第 6 章 工具链与自动化](#第-6-章-工具链与自动化)
- [第 7 章 维护者制度与治理](#第-7-章-维护者制度与治理)
- [第 8 章 规范符合性检查](#第-8-章-规范符合性检查)
- [第 9 章 IRON-9 v3 四层共享模型](#第-9-章-iron-9-v3-四层共享模型)
- [第 10 章 Euler 标准兼容性](#第-10-章-euler-标准兼容性)
- [第 11 章 禁词清单与处罚机制](#第-11-章-禁词清单与处罚机制)
- [第 12 章 "Linux 6.6 为基、seL4 为鉴"工程取向](#第-12-章-linux-66-为基-sel4-为鉴工程取向)
- [第 13 章 8 子仓目录结构工程标准](#第-13-章-8-子仓目录结构工程标准)
- [第 14 章 P2 增强建议与 E1-E17 落地登记](#第-14-章-p2-增强建议与-e1-e17-落地登记)
- [第 15 章 v1.0.1 Capability Folding 与 6 条硬约束](#第-15-章-v101-capability-folding-与-6-条硬约束)
- [附录 A v3.6 审查 68 项改进闭环总表](#附录-a-v36-审查-68-项改进闭环总表)
- [附录 B 规则编号注册表](#附录-b-规则编号注册表)
- [附录 C 五维正交 24 原则映射](#附录-c-五维正交-24-原则映射)
- [附录 D ES-OLK-1~13 工程思想映射](#附录-d-es-olk-113-工程思想映射)
- [附录 E ES-SEL4 工程思想借鉴映射](#附录-e-es-sel4-工程思想借鉴映射es-sel4-15-强制--es-sel4-610-p2-增强)
- [附录 F 双源融合裁决 16 维度](#附录-f-双源融合裁决-16-维度)
- [附录 G v1.2 内核框架验证报告（历史基线）](#附录-g-v12-内核框架验证报告历史基线)

---

## 第 1 章 总则与工程标准框架

### 1.1 文档定位与更新说明（v3.6 闭环重写）

本规范是 AirymaxOS（agent-linux）**闭源工程标准规范的总纲与执行细则**，面向 SPHARX Ltd 内部架构委员会、内核开发组与 8 子仓维护者。它定义了 AirymaxOS 在工程实践层面的全部强制性规则、禁止性规则、验收标准与铁律，是 8 子仓代码开发、审查、测试、发布全生命周期中不可妥协的执行基线。

**权威体系对齐**：本文档是 agentrt 工程标准的**执行细则**，规则定义的唯一权威来源是开源权威体系：

| 权威源 | 路径 | 内容 |
|--------|------|------|
| 工程标准手册 | `docs/docs-linux/50-engineering-standards/00-engineering-standards-handbook.md` | OS-IRON 16 条铁律 + 7 层自动化验证 + 四层共享模型 |
| 工程思想 | `docs/docs-linux/50-engineering-standards/04-engineering-philosophy.md` | 双层稳定性 / 策略机制分离 / regression 零容忍 |
| 开发流程 | `docs/docs-linux/50-engineering-standards/05-development-process.md` | 6 阶段补丁生命周期 / 工具链 / 合规检查 / SPDX |
| 验收标准 | `docs/docs-linux/130-roadmap/06-acceptance-criteria.md` | 110 项 OS-ACC + 三层门禁 + 里程碑门禁 |
| 规则编号 SSoT | `docs/docs-linux/50-engineering-standards/09-ssot-registry.md` + `agent-linux/ssot-registry.yaml`（v0.2.8） | 全部规则编号唯一登记（26 类规则前缀） |

本文档与权威体系冲突时，以权威体系（SSoT）为准；本文档负责权威体系未覆盖的**闭源执行细则**：版本库卫生、模块化开发流水线、CI 完整性、文档-实现一致性义务、LAYER 双轨制、OBS 远程构建、E1-E17 落地登记等。

**v3.6 三轮审查闭环登记**：2026-07-30 ~ 2026-08-01 完成三轮深度审查，共识别 **68 项改进**（去重后 66 项）：

| 轮次 | 范围 | 改进项 | 合计 |
|------|------|--------|------|
| 第一轮 v3.6 | 核心机制（sched/security/IPC/syscall/cap/mem-version） | P0-1 + P1-1~11 + P2-1~17 | 29 |
| 第二轮 v3.6b | 基础设施（boot/irq/time/sync/mem-alloc/task/log/fault） | N1-N22 | 22 |
| 第三轮 v3.6c | 工程思想与设计论证（openEuler/seL4 工程标准） | E1-E17 | 17 |
| **合计** | 14 子域 + 工程标准 | **68（去重 66）** | **68** |

闭环状态：**已修复 12 项 P1/P0 级改进**（含 P0-1、P1-4/5/8/9/10 等，详见附录 A 状态分组）、文档类已完成 15 项、其余按里程碑（M2 / M3-M5）渐进收敛。三轮加权整体成熟度 86.3（B+），其中"可验证性预留"维度 68 分（D+）为最大短板——本文档第 1.2 节据此设立**文档-实现一致性义务**。

### 1.2 文档-实现一致性义务（v3.6c 核心新增）

> **OS-KER-229（SSoT 登记）**: 内核与用户态共享契约必须在编译期以断言形式钉死（编译期断言已落地）。

**问题背景**：v3.6c 审查发现，OS-KER-229 声称"编译期断言已落地"，但源码 grep 零命中——这是"文档承诺、实现空白"的典型：文档超前承诺，源码未兑现。该现象在可验证性预留维度造成 68 分 D+ 的最低分。

**本规范强制义务（新增）**：

> **OS-STD-DOC-100**: 文档中一切"已落地 / 已实现 / 已完成"声称必须登记**落地状态**（已落地 / 预留 / 废弃）并可通过 grep 或构建验证在源码中命中；禁止虚假声称与超前承诺。

| 状态 | 定义 | 标注要求 | 验证方法 |
|------|------|---------|---------|
| **已落地** | 有源码/构建产物证据 | 标注源码路径 + 行号（如 `airy_lsm.c L112-117`） | grep 命中 + 编译/测试通过 |
| **预留** | 有设计承诺，未实现 | 标注"预留，待 M 里程碑" | grep 命中设计文档，源码零命中合法 |
| **废弃** | 决策取消 | 标注"废弃"并保留编号 | 文档声明 |

落地规则：
1. 新增文档声称"已落地"前，作者必须执行 `grep` 验证并在文档中登记证据位置。
2. 无法提供源码证据的声称必须降级为"预留"标注。
3. CI 中 `check-doc-claim.sh`（见 §8.5 DS-01）对高危声称（编译期断言 / 形式化验证 / KUnit 覆盖）做抽查比对。
4. 违反本义务的文档变更视为 P1-MAJOR 审查问题。

**已知漂移登记（v3.6b 审查 B 发现，待修复）**：

| 漂移项 | 文档声称 | 源码实际 | 状态 |
|--------|---------|---------|------|
| 10-sc-sched-extension.md §4.1 | `__attribute__((aligned(64)))` + `reserved[12]` | sched.h 为 `AIRY_ALIGNED(64)` + `_reserved[12]`（OS-IRON-016 合规） | P1 待修复（文档对齐源码） |
| P1-BUD-01 | SDK 错误码 -401/-701 | 内核 -15/-4 | 已登记待修复 |
| P1-CAP-01 | README 索引未更新 | — | 已登记待修复 |

### 1.3 工程标准三大支柱

AirymaxOS 工程标准建立在三大支柱之上，缺一不可。

| 支柱 | 思想来源 | 核心贡献 |
|------|---------|---------|
| **Linux 内核工程思想** | Linux 6.6 内核基线（vanilla 6.6.147 纯主线）源代码深度研究提炼 | 双层稳定性哲学、策略机制分离、渐进式开发、审查优先文化、补丁生命周期、维护者层级制度 |
| **Airymax 五维正交 24 原则** | `00-architectural-principles.md`（S/K/C/E/A 五维） | 体系并行论、反馈闭环、层次分解、内核极简、接口契约化、服务隔离、可插拔策略、安全内生、可观测性、资源确定性等 24 条核心原则 |
| **agentrt 规则编号体系（26 类前缀）** | `09-ssot-registry.md` SSoT v0.2.8 | 26 类规则前缀（OS-IRON 16 / OS-KER 229 / OS-STD / OS-BAN 11 / OS-ACC 110 / OS-SEC / OS-ARCH / OS-IFACE / OS-TEST / OS-IPC / OS-DEV 等），自动化强制执行哲学、7 层验证、110 项 OS-ACC 验收 |

**三大支柱的正交耦合关系**：Linux 内核工程思想提供严肃性基底，五维正交 24 原则提供 Airymax 自身的设计语言，规则编号体系提供可执行性骨架。每条规则都可以同时追溯到：一份 Linux 内核工程传统的沉淀 + 一条五维正交原则的支撑 + 一个规则编号。

### 1.4 与 agentrt 工程标准的关系

AirymaxOS 与 agentrt（AirymaxAgentRT）遵循 **IRON-9 v3 同源且部分代码共享（四层模型：[SC]+[SS]+[IND]+[DSL]）** 原则（详见第 9 章）：

- **同源**：共享 Airymax 五维正交 24 原则作为顶层设计哲学；共享规则编号体系骨架；共享 [SC] 共享契约层代码（`include/uapi/linux/airymax/` 头文件库）。
- **独立**：AirymaxOS 是 OS 发行版，承担内核态严肃性责任，必须独立处理内核 ABI 稳定性、补丁生命周期、维护者层级制度、版本库卫生等 agentrt 不涉及的领域。
- **互操作**：agentrt 在 AirymaxOS 上运行时，两端通过共享契约层代码实现无适配层互操作。

### 1.5 8 子仓工程标准差异化要求

AirymaxOS 的 8 个子仓对应不同的内核子系统，各自承担不同的工程标准侧重点（现状：7 轻仓最小骨架 + kernel 仓 M0 框架编译验证通过，见第 13 章）。

| 子仓 | 对应 agentrt 模块 | 工程标准侧重点 | 适用规则前缀 |
|------|------------------|---------------|-------------|
| `kernel` | atoms/corekern | 内核极简（K-1）、接口契约化（K-2）、资源确定性（E-3）、临界区锁规则、编译产物卫生 | OS-KER、OS-IRON |
| `services` | daemons | 服务隔离（K-3）、跨平台一致性（E-4）、用户态内存安全 | OS-STD、OS-DRV |
| `security` | cupolas | 安全内生（E-1）、最小权限、LSM 钩子注册规则、capability 派生 | OS-SEC、OS-IRON |
| `memory` | heapstore + memoryrovol | 内存管理规范、池化与泄漏检测、MGLRU 多代 LRU、CXL/PMEM 分级 | OS-KER、OS-STD |
| `cognition` | coreloopthree + frameworks | 双系统协同（C-1）、增量演化（C-2）、调度策略可插拔（K-4） | OS-STD、OS-ACC |
| `cloudnative` | gateway + sdk | 接口契约化（K-2）、可观测性（E-2）、API 版本管理 | OS-STD、OS-ABI |
| `system` | commons | 命名语义化（E-5）、错误可追溯（E-6）、文档即代码（E-7） | OS-STD、OS-BUILD |
| `tests-linux` | 全模块测试 | 可测试性（E-8）、覆盖率门槛、契约测试、模糊测试 | OS-TEST、OS-ACC |

### 1.6 规则编号体系（26 类前缀）

AirymaxOS 规则编号的唯一权威来源为 `09-ssot-registry.md`（SSoT v0.2.8，11 个 Tier-0 技术点）。本规范仅作闭源侧摘要登记。

| 编号前缀 | 含义 | 数量/登记 | 示例 |
|---------|------|----------|------|
| **OS-IRON** | 工程铁律（不可妥协） | 16 条（001-016） | OS-IRON-001: 用户空间 ABI 永不破坏 |
| **OS-KER** | 内核工程规则 | 229 条（001-229） | OS-KER-001: goto 集中出口模式 |
| **OS-STD** | 标准规则（CODE/FMT/STY/GOV/DOC/CHK 子域） | 多子域 | OS-STD-CODE-004: 编译期 0 警告 |
| **OS-BAN** | 禁止规则 | 11 条 | OS-BAN-001: 敏感术语禁用 |
| **OS-ACC** | 验收标准 | 110 项（001-110） | OS-ACC-001: 覆盖率 >= 80% |
| **OS-SEC** | 安全工程规则 | 54 条 | OS-SEC-001: LSM 钩子最小权限 |
| **OS-ARCH** | 架构工程规则 | 10 条（001-010） | OS-ARCH-001: 架构正交 |
| **OS-IFACE** | 接口工程规则 | 10 条（001-010） | OS-IFACE-001: 接口契约化 |
| **OS-TEST** | 测试工程规则 | 22 条（001-022） | OS-TEST-001: KUnit 单元测试覆盖 |
| **OS-IPC** | IPC 协议规则 | 登记 | OS-IPC-001: AgentsIPC 128B 头 |
| **OS-DEV** | 开发流程规则 | 登记 | OS-DEV-001: 模块化流水线 |

> 完整 26 类规则前缀注册见 `09-ssot-registry.md`；本文档第 2-8 章引用的编号均为该注册表登记项。

### 1.7 规则等级与执行力度

| 等级 | 编号前缀 | 违反后果 | CI 阻断 | 处理时限 |
|------|---------|---------|---------|----------|
| **铁律** | OS-IRON | 补丁退回，不可合并 | 是 | 立即修复 |
| **禁止** | OS-BAN | 补丁退回，强制修改 | 是 | 立即修复 |
| **标准** | OS-STD | 审查要求修改 | 是 | 24h 内修复 |
| **内核** | OS-KER | 补丁退回 | 是 | 立即修复 |
| **安全** | OS-SEC | 补丁退回 | 是 | 立即修复 |
| **验收** | OS-ACC | 版本发布阻断 | 是 | 发布前修复 |
| **测试** | OS-TEST | 覆盖率不达标 | 是 | 发布前修复 |
| **构建** | OS-BUILD | 构建失败 | 是 | 立即修复 |
| **卫生** | VCS-*（本规范新增） | 版本库卫生违规 | 是 | 立即修复 |
| **一致性** | DS-*（本规范新增） | 文档-实现漂移 | 是 | 24h 内修复 |

---

## 第 2 章 代码规范

### 2.1 命名规范

#### 2.1.1 全局函数与全局变量

> **OS-STD-CODE-001**: 全局符号必须描述性命名，禁止无意义缩写。

C 是朴素的语言，命名应与之相称。全局函数名应当精确描述其行为：`count_active_users()` 而非 `cntusr()`，`airy_dispatch_task()` 而非 `dt()`。这是五维正交 E-5 命名语义化原则的直接落地。

#### 2.1.2 局部变量

> **OS-STD-002**: 局部变量短小切题。循环计数器用 `i`，临时值用 `tmp`，缓冲区用 `buf`。

```c
int i;                /* 循环计数器 */
char *tmp;            /* 临时指针 */
u8 buf[256];          /* 缓冲区 */
struct airy_task *task;
```

#### 2.1.3 宏与枚举命名

> **OS-STD-003**: 常量宏全大写；多个相关常量优先用 `enum` 而非散落 `#define`。

```c
#define AIRY_MAX_TASKS     1024

enum airy_task_state {
    AIRY_TASK_PENDING   = 0,
    AIRY_TASK_RUNNING   = 1,
    AIRY_TASK_COMPLETED = 2,
    AIRY_TASK_FAILED    = 3,
};
```

#### 2.1.4 敏感术语禁止

> **OS-BAN-001**: 新增代码禁用 `master/slave`、`blacklist/whitelist`，替换为 `primary/secondary`、`denylist/allowlist`。仅当维护既有 UAPI 或对齐既有硬件/协议规范时例外。

#### 2.1.5 AirymaxOS 专属前缀

> **OS-STD-005**: `agentrt_*` 前缀保留给 agentrt 同源 API；`airy_*` 前缀用于 AirymaxOS 内核/发行版专属 API；`are_*` 用于标准接口层（ABI 稳定，跨 [SC]/[SS]/[IND] 统一入口）；`AIRY_` 用于宏/常量（[SC] 共享层）。

```c
int agentrt_ipc_send(u32 ch, const void *msg, size_t len);     /* agentrt 同源 */
int airy_lsm_hook_register(const struct security_hook_list *hooks); /* OS 专属 */
```

#### 2.1.6 AIRY_ALIGNED 宏优先（OS-IRON-016 落地，P1-5 已修复）

> **OS-IRON-016（UAPI 编译器无关原则）**: `include/uapi/linux/airymax/` 下的 UAPI 头文件必须坚持 C 标准（C11），避免直接使用编译器扩展。唯一例外：结构体缓存行对齐通过 `AIRY_ALIGNED(N)` 宏（定义于 `uapi_compat.h`）实现。

**落地规则**：
1. UAPI 头文件中**禁止**直接使用 `__attribute__((aligned(N)))`、`__builtin_*`、`__asm__`、`__sync_*`、`__atomic_*`、`typeof`。
2. 结构体对齐一律使用 `AIRY_ALIGNED(N)` 宏（`uapi_compat.h` 是唯一允许含 `__attribute__` 的 UAPI 头文件）。
3. **P1-5 已修复（v3.6 闭环）**：`airy_ipc_capability.c` 的 `__aligned(64)` 已替换为 `AIRY_ALIGNED(64)`。
4. CI 强制扫描：`grep -rnE "__attribute__|__builtin_|__asm__|__sync_|__atomic_|typeof" include/uapi/linux/airymax/ --exclude="uapi_compat.h"` 必须 0 命中。
5. 结构体预留字段统一命名 `_reserved[N]`（P2-13 已统一），禁止混用 `reserved[N]`。

### 2.2 函数规范

#### 2.2.1 函数长度

> **OS-STD-006**: 函数长度应一屏可读（约 80x24 字符），局部变量不超过 5-10 个。超过此限度的函数应拆分为子函数。

#### 2.2.2 函数原型

> **OS-STD-007**: 函数原型元素固定顺序：storage class → attributes → return type → name → params → behavior attributes。

```c
static __always_inline void *airy_get_private(const struct airy_device *dev);
```

#### 2.2.3 返回值约定

> **OS-STD-004**: 动作式/命令式函数返回错误码（0 = 成功，-Exxx = 失败）；谓词式函数返回 `bool`。

```c
int  airy_task_submit(struct airy_task *task);   /* 0 / -EBUSY */
bool airy_task_is_pending(const struct airy_task *task);
```

#### 2.2.4 错误处理（强制范式）

> **OS-KER-001**: 使用 `goto out_free_xxx:` 集中出口模式 + 分级标签按分配逆序释放。

```c
int airy_alloc_and_init(struct airy_buffer *buf)
{
    buf = kzalloc(sizeof(*buf), GFP_KERNEL);
    if (!buf)
        return -ENOMEM;
    if (unlikely(!buf->data)) {
        kfree(buf);
        return -ENOMEM;
    }
    return 0;
}
```

> **OS-KER-002**: 禁止使用 `#if defined(CONFIG_XXX) ... #else ... stub #endif` 模式编写桩函数。任何功能要么完整实现，要么通过 Kconfig 在配置层面排除，不得以桩函数形式存在于编译路径中。（合规例外：M0/M1 脚手架阶段 wrapper 占位属 OS-IRON-004 渐进式开发，须在文档登记"预留"状态，见 §1.2）

> **OS-KER-003**: 内核条件编译必须使用 `IS_ENABLED(CONFIG_XXX)` 宏而非 `#ifdef CONFIG_XXX`，让编译器进行死代码消除。

> **OS-BAN-002**: 禁止 `BUG()`/`BUG_ON()`，改用 `WARN()`/`WARN_ON_ONCE()` 并提供恢复代码。

> **OS-BAN-003**: 内存分配用 `sizeof(*p)` 而非 `sizeof(struct xxx)`。数组分配用 `kmalloc_array`/`kcalloc`（含溢出检查）。

> **OS-BAN-004**: 禁止 `strcpy`/`strncpy`/`strlcpy`，强制 `strscpy`。

> **OS-BAN-005**: 禁用 `%p` 默认输出（哈希化），新增 `%p` 不被接受。

### 2.3 注释规范

#### 2.3.1 kernel-doc 强制

> **OS-STD-008**: 所有 EXPORTed 函数、公共结构体、公共枚举必须包含完整的 kernel-doc 注释，并通过 `scripts/kernel-doc` 验证无警告。

#### 2.3.2 注释原则

> **OS-STD-009**: 注释解释"为什么"而非"是什么"。代码本身说明"是什么"，注释应说明设计意图、非显而易见的假设、性能考量。

### 2.4 多语言栈规范

#### 2.4.1 C 语言

- 遵循 Linux 内核 `coding-style.rst` 全部规则
- 最大警告级别 `-Wall -Wextra -Werror`
- 禁止隐式类型转换（`-Wconversion`）

#### 2.4.2 Rust 语言

- 遵循 Rust 2021 edition
- 内核模块仅用于安全敏感且非热路径的子系统
- `#![no_std]` 内核模块，禁止 `std` 依赖
- 所有 `unsafe` 块必须有 `// SAFETY:` 注释说明安全性理由

#### 2.4.3 Python 语言

- 遵循 PEP 8；4 空格缩进，100 列行宽；Black + isort 统一格式化；类型注解强制（mypy strict）

#### 2.4.4 TypeScript 语言

- 遵循 ESLint + Prettier；2 空格缩进，100 列行宽；严格模式（`strict: true`）

### 2.5 类型规范

> **OS-STD-010**: 内核内部使用 `u8/u16/u32/u64`，用户空间可见结构体使用 `__u32` 等。typedef 严格限制（仅 5 种例外：完全不透明对象、清晰整数类型、sparse 新类型、C99 等价、UAPI 安全类型）。

> **OS-STD-011**: bool 仅用于函数返回值与栈变量，对齐敏感的结构体不使用 bool。

### 2.6 编译产物管理规范（v3.6 新增）

> **OS-STD-DOC-110（编译产物管理）**: 编译产物与构建日志禁止进入版本控制。`.gitignore` 必须覆盖全部编译产物与日志类文件。

**硬性要求**：

| 类别 | 必须 ignore 的模式 | 说明 |
|------|-------------------|------|
| 目标文件 | `*.o` `*.a` `*.cmd` `*.ko` | 内核/模块编译产物 |
| 链接产物 | `vmlinux` `System.map` `Module.symvers` | 顶层构建产物 |
| 日志文件 | `*.log` `build-*.log` | 构建日志禁止提交 |
| 配置产物 | `.config` `*.config.old` `compile_commands.json` | 生成配置 |
| 构建目录 | `build/`（非构建定义目录时） | 视子仓约定 |

**log 文件规范**：
1. 构建日志命名 `build-<target>.log`，存放于构建输出目录或 `/tmp`，**禁止提交到 git**。
2. 反例（P0 卫生问题）：`build-arm64.log` 曾被 git 跟踪（commit 278ebfb19ca6 "arch: add sw_64 architecture support files" 带入，违反"一个 commit 一个逻辑变更"），须通过 `git rm --cached` + `.gitignore` 规则修复。
3. 需要长期保留的构建报告（如发布验证日志）归档于 `build/logs/`（构建定义管理仓，见 §13.5），不入 kernel 仓。

**O= 分离构建要求**（v3.6 新增）：
- kernel 构建必须使用 `make O=<builddir>` 分离构建，源码树内禁止残留编译产物。
- 树内残留 arm64 产物会触发 kbuild 拦截导致 `O=` 分离构建失败——这是已实测的卫生事故，须清理后重建。
- CI 与本地开发统一采用 `O=build/` 外部目录。

---

## 第 3 章 代码格式

### 3.1 缩进

> **OS-STD-FMT-001**: C 内核代码使用 Tab 缩进，Tab 宽度为 8 字符。

其他语言：Rust 4 空格；Python 4 空格（PEP 8）；TypeScript 2 空格。

### 3.2 行宽

> **OS-STD-FMT-002**: C 代码首选 80 列。其他语言：Rust/Python/TypeScript 100 列。

### 3.3 大括号风格

> **OS-STD-FMT-003**: 使用 K&R 风格。非函数块的左括号放在行末，函数定义的左括号放在行首。

> **OS-STD-FMT-004**: 即使只有一条语句，也使用大括号包围。

### 3.4 空格规则

> **OS-STD-FMT-005**:
> - 关键字后加空格：`if (`、`for (`、`while (`
> - 括号内禁止空格：`if (condition)` 而非 `if ( condition )`
> - 二元运算符两侧加空格；一元运算符不加空格
> - 指针声明 `*` 贴名字：`char *p` 而非 `char* p`

### 3.5 行尾禁止空白

> **OS-STD-FMT-006**: 任何代码行的行尾不得有空白字符。

### 3.6 clang-format 配置

> **OS-STD-FMT-007**: 所有 C/C++ 代码必须通过 `.clang-format` 配置自动格式化。CI 中强制 `make format-check`。

```yaml
BasedOnStyle: LLVM
IndentWidth: 8
UseTab: Always
TabWidth: 8
ColumnLimit: 80
BreakBeforeBraces: Linux
PointerAlignment: Right
ForEachMacros:
  - 'list_for_each_entry'
  - 'airy_for_each_task'
```

---

## 第 4 章 工程思想

### 4.1 双层稳定性哲学

#### 4.1.1 用户空间 ABI 永不破坏

> **OS-IRON-001**: 一旦接口导出至用户空间，必须永久支持。

用户空间接口设计必须做到三件事：深思熟虑（不导出未经充分论证的接口）、清晰文档（所有导出接口必须有完整的 ABI 文档）、广泛审查（所有用户空间接口改动必须 CC 专门的 ABI 审查组）。

#### 4.1.2 内核内部 API 不保证稳定

> **OS-IRON-002**: 内核内部 API 不保证稳定；API 改动者必须同时修复所有受影响代码（"you broke it, you fix it"）。

### 4.2 AirymaxOS 4 层接口稳定性分级

| 层级 | 接口类型 | 稳定性 | 变更流程 |
|------|---------|--------|---------|
| L1 | Agent 应用 API（SDK + syscall + UAPI） | 极稳定（类 Linux syscall） | RFC + ABI 审查 + 6 个月宽限期 + 弃用声明 |
| L2 | 智能体运行时接口（AgentsIPC 协议） | 中等稳定（版本化演进） | 季度评审 + 兼容性测试 |
| L3 | 内核子系统接口（内核内部 API） | 可重构 | 补丁序列修复所有调用点 |
| L4 | 内部实现细节 | 完全自由 | 无约束 |

### 4.3 策略与机制分离

> **OS-IRON-003**: 机制留在内核（提供能力），策略外移至用户空间或可插拔模块。

- **sched_tac 调度框架**：调度机制（`kernel/sched/`）留在内核，调度策略由 sched_tac 框架以 SCHED_DEADLINE/SCHED_FIFO 形式承载（ADR-013 禁止 sched_ext，Linux 6.6 主线无 sched_ext，6.12 才合入）。
- **LSM 安全策略**：安全机制（LSM 钩子框架，纯 C LSM airy_lsm，H5 硬约束）留在内核，具体安全策略（Cupolas 用户态策略）以可插拔方式加载。

### 4.4 渐进式开发

> **OS-IRON-004**: 每个补丁必须是逻辑上自包含的最小变更单元，中点可编译运行，支持 `git bisect`。

### 4.5 审查优先文化

> **OS-IRON-005**: 所有代码进入主线前必须通过至少一名维护者审查并获得 Reviewed-by 标签。

### 4.6 不破坏用户空间原则

> **OS-IRON-006**: 任何补丁不得导致用户空间程序行为改变，除非该行为被明确标记为 bug（regression 零容忍）。

---

## 第 5 章 开发流程

### 5.1 6 阶段补丁生命周期

AirymaxOS 采用与 Linux 内核一致的 6 阶段补丁生命周期模型：

| 阶段 | 输入 | 输出 | 责任人 | SLA |
|------|------|------|--------|-----|
| **Design** | 需求分析 / RFC 提案 | 设计文档 + 架构评审通过 | 提案者 | 无硬性 SLA |
| **Early Review** | 补丁序列（RFC 标记） | 初步反馈 + 设计方向确认 | 子系统维护者 | 1-2 周内响应 |
| **Wider Review** | 修订后的补丁序列 | Reviewed-by + Acked-by 标签 | 子系统维护者 + 资深维护者 | 4 周内完成 |
| **Mainline** | 通过审查的补丁 | 合并入 `develop` 分支 | 总维护者（Chief Maintainer） | Merge Window 内 |
| **Stable Release** | `develop` 分支稳定版快照 | `release/*` 分支 | 稳定版维护者 | 按发布计划 |
| **Long-term** | `release/*` 分支 | LTS 持续维护 | LTS 维护者 | 2-6 年 |

### 5.2 维护者层级制度（Lieutenant System）

```
Chief Maintainer（总维护者）
├── Top-level Maintainer（顶层维护者，8 子仓各一名）
│   ├── Subsystem Maintainer（子系统维护者，如 kernel/sched/）
│   │   └── Contributor（贡献者）
│   └── Subsystem Maintainer（子系统维护者，如 kernel/security/）
│       └── Contributor（贡献者）
└── Top-level Maintainer（顶层维护者）
    └── ...
```

### 5.3 补丁提交规范与 commit 规范性（v3.6 强化）

#### 5.3.1 补丁格式

> **OS-STD-020**: 补丁必须包含以下元素：

```
subsystem: 简短摘要（50-72 字符）

详细描述。解释为什么需要这个修改，而非仅仅说明做了什么。
描述设计决策、替代方案、性能影响。

Signed-off-by: 作者名 <author@example.com>
Reviewed-by: 审查者名 <reviewer@example.com>
Fixes: 12 字符 SHA ("补丁摘要")  # 如有
Closes: #123  # 如有
Link: https://...  # 如有
```

#### 5.3.2 subsystem 前缀规范（v3.6 新增）

| 子系统域 | 前缀 | 示例 |
|---------|------|------|
| Airymax 内核子系统 | `airy/sched`、`airy/mem`、`airy/ipc`、`airy/lsm`、`airy/vm`、`airy/standards` | `airy/ipc: fix ring overflow counter` |
| 架构移植 | `arch/sw_64`、`arch/x86`、`arch/arm64` | `arch/sw_64: register airy syscall slots` |
| 文档 | `docs` | `docs: update sched contract to AIRY_ALIGNED` |
| 构建/CI | `build`、`ci` | `ci: pin tools/ scripts in version control` |
| 其他 | 子仓名（`security`、`tests-linux`） | `security/airy: add badge check to task_kill` |

#### 5.3.3 commit 规范性铁律（v3.6 新增）

> **OS-STD-PROD-100（commit 规范性）**: 一个 commit 一个逻辑变更；编译产物/日志禁止提交；subsystem 前缀必须规范。

1. **一个 commit 一个逻辑变更**：禁止混合 bug fix / 性能优化 / 重构 / 新特性。反例：`278ebfb19ca6` "arch: add sw_64 architecture support files" 夹带 `build-arm64.log`。
2. **编译产物/日志禁提交**：commit 前运行 `git status` 核对无 `*.o/*.ko/*.log/vmlinux/System.map`。
3. **subsystem 前缀规范**：标题行 `subsystem: summary` 祈使句，无句号，≤72 字符（对照 Linux `submitting-patches.rst`）。
4. **Fix 类提交**（Bug fix）落款 `Signed-off-by: Decheng Li <lidecheng@spharx.cn>`；**功能类提交**（Feature）落款 `Signed-off-by: Liren Wang <wangliren@spharx.cn>`；若使用 `Co-developed-by:` 必须紧随配对 `Signed-off-by:`。
5. 修复补丁必须含 `Fixes:` 标签（不拆行，hash ≥12 字符），需回溯稳定版加 `Cc: stable@vger.kernel.org`；非 Fixes 类补丁含 `Link:` 指向讨论存档。

#### 5.3.4 标签体系与 DCO

| 标签 | 含义 | 添加者 |
|------|------|--------|
| `Signed-off-by:` | DCO 认证 | 补丁作者 |
| `Reviewed-by:` | 审查通过声明 | 审查者 |
| `Acked-by:` | 知悉且不反对 | 相关维护者 |
| `Fixes:` | 修复的 commit SHA（≥12 字符） | 补丁作者 |
| `Closes:` | 关闭的 Issue 编号 | 补丁作者 |
| `Link:` | 相关讨论链接 | 补丁作者 |
| `Co-developed-by:` | 共同开发者（须配对 Signed-off-by） | 补丁作者 |

> **OS-IRON-007**: 所有补丁必须包含 Signed-off-by 标签。CI 中 DCO bot 自动验证链条完整性。

### 5.4 审查流程与礼仪

1. 贡献者提交 PR，填写 PR 模板
2. CODEOWNERS 自动分配审查者
3. 审查者在 2 周内提供反馈
4. 贡献者响应反馈、修订补丁
5. 审查者最终确认并添加 Reviewed-by 标签
6. 顶层维护者合并入 develop 分支

审查礼仪：审查者批评代码不批评人；贡献者不防御性回应；双方视审查为知识传递过程。

### 5.5 模块化开发流水线规范（v3.6 核心新增）

> **OS-DEV-001（模块化开发流水线）**: 每个功能模块必须按"设计冻结 → 实现 → 测试 → 验收 → 下一模块"五步流水线推进，禁止跨模块混合提交。

**五步流水线**：

```
┌──────────────────────────────────────────────────────────────────┐
│ 第 1 步 设计冻结（Design Freeze）                                   │
│   · 设计文档对齐 SSoT（[SC] 头文件 / syscall 编号 / 规则编号）        │
│   · 登记"预留/已落地"状态（§1.2 文档-实现一致性义务）                 │
│   · 输出：设计冻结评审通过                                          │
├──────────────────────────────────────────────────────────────────┤
│ 第 2 步 实现（Implement）                                           │
│   · 一个模块一个逻辑变更，commit 序列中点可编译（OS-IRON-004）        │
│   · 源码位于本模块目录，禁跨模块混合提交                             │
├──────────────────────────────────────────────────────────────────┤
│ 第 3 步 测试（KUnit / kselftest）                                   │
│   · P1 级修复必须配套 KUnit 测试（§6.5）                            │
│   · 测试文件 *_test.c，挂 CONFIG_AIRY_KUNIT                         │
├──────────────────────────────────────────────────────────────────┤
│ 第 4 步 OS-ACC 验收（Acceptance）                                   │
│   · 执行本模块对应的 OS-ACC 验收项（§1.5 八子仓映射）                 │
│   · 验收 gate：CI 全绿 + 覆盖率达标 + 里程碑门禁通过                  │
├──────────────────────────────────────────────────────────────────┤
│ 第 5 步 进入下一模块（Next）                                        │
│   · 模块交付物归档（见下），解锁下一模块                              │
└──────────────────────────────────────────────────────────────────┘
```

**模块交付物清单**（四件套，缺一不可）：

| 交付物 | 内容 | 验收 gate |
|--------|------|----------|
| 代码 | 模块源码 + Kbuild/Kconfig 接线 | 编译通过（三架构 airy_defconfig） |
| 测试 | KUnit（`*_test.c`）/ kselftest | CONFIG_AIRY_KUNIT 下全绿 |
| 文档 | 设计文档（含 SSoT 对齐 + 五维映射 + 落地状态登记） | STD-DOC 检查 + DS-01 声称核验 |
| 登记 | 规则编号 / syscall 编号 / 状态登记 | SSoT 一致性检查 |

**模块边界规则**：
1. 一个模块一个逻辑变更：模块边界 = 目录边界（`kernel/corekern/*`、`security/airy/*` 等）。
2. 禁跨模块混合提交：跨模块依赖通过 [SC] 共享契约层（`include/uapi/linux/airymax/`）表达，禁止直接修改其他模块源码。
3. 每模块完成后必须过 OS-ACC 验收 gate 方可进入下一模块（里程碑门禁：M0 过 OS-ACC-001~020 解锁 M1，依此类推）。

### 5.6 版本库卫生规范（v3.6 新增）

> **OS-STD-PROD-110（版本库卫生）**: 版本库必须保持"声明一致、产物干净、脚本入库"的卫生状态。

| 卫生项 | 要求 | 反例（v3.6 审查已核验） |
|--------|------|------------------------|
| 编译产物跟踪 | `.gitignore` 覆盖 `*.o/*.a/*.cmd/*.ko/*.log/vmlinux/System.map`；`git ls-files` 零命中 | `build-arm64.log` 被 git 跟踪（278ebfb19ca6 带入） |
| 构建日志提交 | 禁止提交 `*.log` | `.gitignore` 无 `*.log` 规则 |
| O= 分离构建 | 一律 `make O=<builddir>`；源码树无产物残留 | 树内残留 arm64 产物导致 O= 构建被 kbuild 拦截 |
| 分支声明一致性 | `.gitmodules` 声明的分支与实际检出分支一致 | `.gitmodules` 声明 kernel 分支 `develop/hubs-01`，实际 `ALK-6.6-dev`（漂移） |
| CI 脚本入库 | CI 引用的全部脚本必须存在于 `tools/`/`scripts/` 并纳入版本控制 | CI 引用 7 个不存在的脚本（§6.6） |
| 白名单完整性 | `.gitignore` 白名单含 `!tools/**` `!scripts/**` | tools/ 9 个 .py + codegen/ 未入版本控制 |
| syscall 表登记 | sw_64 syscall.tbl 必须登记 airy 548-571 号段 | sw_64 syscall.tbl 止于 518，未注册 |

### 5.7 稳定版维护规则

> **OS-STD-021**: `release/*` 分支仅接受：关键 bug 修复（CVE、数据损坏、崩溃）、安全修复、构建修复、文档修正。禁止：新特性、代码重构、行为变更、ABI 变更。

### 5.8 LTS 长期支持

AirymaxOS LTS 版本提供 2-6 年长期支持：前 2 年全面支持，第 3-4 年安全支持，第 5-6 年扩展支持（需商业支持协议）。

---

## 第 6 章 工具链与自动化

### 6.1 7 层自动化验证

| 层级 | 验证内容 | 工具 | 阻断条件 |
|------|---------|------|---------|
| L1 编译期 | 编译警告、禁用函数 | `-Werror`、`banned_functions.h` | 任何警告/禁用函数使用 |
| L2 静态分析 | 代码质量、潜在 bug | clang-tidy、cppcheck、sparse（W=2） | 新增警告 |
| L3 预提交 | 格式检查、基础规则 | pre-commit hooks、DCO bot | 格式不符合 |
| L4 CI 门禁 | 构建、单元测试、BAN 规则 | GitHub Actions（9 矩阵） | 构建失败/测试失败 |
| L5 连接/集成验证 | 符号检查、ABI 漂移、协议校验 | check_abisym.sh、airymax-ipc-check | 集成测试失败 |
| L6 覆盖率 | 行覆盖率 | gcov + lcov | 覆盖率 < 80% |
| L7 发布验证 | 签名、校验和 | GPG、模块签名 | 签名失败 |

### 6.2 checkpatch 集成

> **OS-STD-101**: 所有补丁提交前必须通过 `scripts/checkpatch.pl --strict` 检查。ERROR 级别问题阻断合并；WARNING/CHECK 须可辩护。

checkpatch 检查项包括：代码风格、命名规范、注释格式、敏感术语、内存分配惯用法（sizeof(*p)）、字符串操作（strcpy/strncpy 禁止）。

### 6.3 CI/CD 流水线

```
PR 提交
  → L1 编译检查（GCC + Clang 双编译器，O= 分离构建）
  → L2 静态分析（sparse W=2 + Smatch + Coccinelle）
  → L3 格式检查（clang-format + checkpatch）
  → L4 单元测试（KUnit，CONFIG_AIRY_KUNIT）
  → L5 集成测试（kselftest + ABI 检查 abi_check.py）
  → L6 覆盖率报告（gcov + lcov，门槛 80%）
  → L7 安全扫描（CodeQL）
  → 审查者分配（CODEOWNERS）→ 审查通过 → 合并入 develop
```

### 6.4 覆盖率门槛

> **OS-ACC-001**: 新增代码行覆盖率 >= 80%，关键路径（调度、内存、IPC、安全）>= 90%（关键路径 100% 强制，OS-STD-124）。

### 6.5 KUnit 回归规范（v3.6 新增）

> **OS-TEST-001（KUnit 回归）**: P1 级修复必须配套 KUnit 测试；测试文件命名 `*_test.c`，挂 `CONFIG_AIRY_KUNIT`。

**已落地测试基线（5+1，审查 C 核验）**：

| # | 测试文件 | 路径 | 类型 |
|---|---------|------|------|
| 1 | `airy_lsm_test.c` | `kernel/security/airy/airy_lsm_test.c` | KUnit（LSM Badge 校验） |
| 2 | `airy_cap_derive_test.c` | `kernel/security/airy/airy_cap_derive_test.c` | KUnit（COPY 降级/派生单调性） |
| 3 | `airy_ipc_ring_test.c` | `kernel/kernel/corekern/ipc/airy_ipc_ring_test.c` | KUnit（SPSC ring） |
| 4 | `airy_ipc_capability_test.c` | `kernel/kernel/ipc/airy_ipc_capability_test.c` | KUnit（capability IPC） |
| 5 | `stc_dispatch_test.c` | `kernel/kernel/corekern/sched/stc_dispatch_test.c` | KUnit（sched_tac 派发） |
| 6 | `airy_fastpath_bench.c` | `kernel/kernel/corekern/ipc/airy_fastpath_bench.c` | Benchmark（badge 校验 2-10ns 实测） |

**回归规则**：
1. 任何 P1 级 bug 修复补丁必须附带 KUnit 回归测试（对应 OS-KER-065：bug 修复补丁必须附带回归测试）。
2. 测试文件命名 `*_test.c`，通过 `CONFIG_AIRY_KUNIT` 挂入 KUnit 套件（`kunit_test_suites()`）。
3. `CONFIG_AIRY_KUNIT=y` 时测试对象从生产模块剥离（如 `airy_lsm.o` 从 airy 模块剔除），避免符号冲突。
4. 新测试必须可通过 `make O=build kunit` 本地运行，并在 CI 中强制执行。

### 6.6 CI 完整性规范（v3.6 新增）

> **OS-STD-PROD-120（CI 完整性）**: CI 引用的一切脚本/路径必须真实存在于版本控制中；监听路径必须与实际文件一致。

**硬性要求**：
1. CI workflow 中调用的每个脚本必须存在于 `tools/` 或 `scripts/` 且被 git 跟踪（`.gitignore` 白名单含 `!tools/**` `!scripts/**`）。
2. CI 监听/引用的文件路径必须真实存在。
3. 新增 CI job 必须通过"脚本存在性 + 路径存在性"双检查（VCS-04）。

**已核验问题（审查 C）**：

| 问题 | 详情 | 处置 |
|------|------|------|
| 7 个缺失脚本 | CI 引用 `formal-verify.py` / `soak-runner.py` / `chaos-runner.py` / `auto-bisect.py` / `create-revert-pr.py` / `ci-budget-check.py` / `merge-sbom.py`，均不存在于 tools/ | P1 待修复：落地脚本或移除引用 |
| tools/ 未入库 | tools/ 9 个 .py + codegen/ 未纳入版本控制（.gitignore 白名单缺 !tools/** !scripts/**） | P1 待修复：修白名单并入库 |
| ci-airy.yml 监听漂移 | 监听 `kernel/config/Kconfig.alk`，该文件不存在 | P1 待修复：改为真实路径（顶层 Kconfig:34 source "config/Kconfig.alk" 实际位于 `kernel/config/Kconfig.alk` 或按现状核对） |
| tools/ 脚本命名 | 存在 `tools/codegen/syscall_gen.py`（已入库） | 已合规 |

### 6.7 CI 现状登记（v3.6）

| workflow | 状态 | 说明 |
|----------|------|------|
| `sc-dual-ci` | ✅ 存在 | [SC] 头文件双向 CI（agentrt + AirymaxOS） |
| `ssot-validate` | ✅ 存在 | SSoT 规则编号校验 |
| `ci-airy.yml` | ⚠️ 部分待修复 | 监听路径漂移 + 脚本缺失（§6.6） |
| `nightly` | ⚠️ 部分 job 待修复 | 依赖缺失脚本的 job 需落地或禁用 |
| `release` | ⚠️ 部分 job 待修复 | 同上 |

---

## 第 7 章 维护者制度与治理

### 7.1 MAINTAINERS 文件规范

> **OS-STD-040**: 每个子仓必须包含 `MAINTAINERS` 文件，记录维护者信息、邮件列表、状态、相关文件路径（Linux 14 字段 + H:/V: 3 个同源扩展字段）。

### 7.2 维护者层级

| 层级 | 角色 | 权限 | 选拔方式 |
|------|------|------|---------|
| **Contributor** | 提交补丁、参与讨论 | 提交 PR | 任何人 |
| **Subsystem Maintainer** | 审查子系统补丁、技术决策 | 批准子系统 PR | Top-level Maintainer 提名，Chief Maintainer 批准 |
| **Top-level Maintainer** | 管理子仓、审批重大架构变更 | 合并子仓 PR | Chief Maintainer 提名，架构委员会投票 |
| **Chief Maintainer** | 最终决策者、合并窗口管理、发布管理 | 合并所有 PR | 架构委员会选举 |

### 7.3 成熟度模型

| 阶段 | 标签 | 含义 | 合并条件 |
|------|------|------|---------|
| **Experimental** | `S: Experimental` | 新功能，API 不稳定 | 通过基本构建和单元测试 |
| **Staging** | `S: Staging` | 功能基本稳定 | 通过集成测试和审查 |
| **Mainline** | `S: Mainlined` | 功能稳定，API 冻结 | 通过全部 7 层验证 |
| **Stable** | `S: Stable` | 长期支持承诺，ABI 冻结 | 通过 LTS 发布审查 |

### 7.4 DCO（Developer Certificate of Origin）

AirymaxOS 要求所有贡献者签署 DCO，通过 Signed-off-by 标签在每次提交中声明，CI 自动验证。

### 7.5 CODEOWNERS 自动审查分配

> **OS-STD-041**: 每个子仓必须包含 `.github/CODEOWNERS` 文件，定义文件路径到审查者的自动映射。

### 7.6 子模块分支治理（v3.6 新增）

> **OS-STD-GOV-020（子模块分支治理）**: 子模块分支以 `.gitmodules` 声明为准；声明分支与实际检出分支必须一致。

1. **规范分支约定**：`kernel` 子仓规范开发分支为 `ALK-6.6-dev`（vanilla 6.6.147 + sw_64 导入 + airy 代码的开发分支）。其余子仓按各自规划使用 `main`/`develop`。
2. **一致性义务**：`.gitmodules` 中声明的 `branch` 字段必须与实际维护的分支一致。反例（已核验）：`.gitmodules` 声明 `develop/hubs-01`，实际检出 `ALK-6.6-dev`——须同步 `.gitmodules`。
3. **分支保护**：`main` / `develop` / `release/*` / `ALK-6.6-dev` 启用 "Require status checks to pass before merging"。
4. 子模块版本更新（submodule bump）须单独 commit，注明新 hash 对应的上游变更摘要。

---

## 第 8 章 规范符合性检查

### 8.1 STD-DOC 文档规范检查（8 项）

| 编号 | 检查项 | 检查方法 | 阻断等级 | CI 集成 |
|------|--------|---------|----------|---------|
| STD-DOC-01 | Copyright 头部存在 | `grep -L "Copyright (c) 2025-2026 SPHARX"` | P0-CRITICAL | 是 |
| STD-DOC-02 | 开源文档禁词检查 | 正则匹配 forbidden-words.conf | P0-CRITICAL | 是 |
| STD-DOC-03 | IRON-9 v3 四层标注 | 深度修订文档必须有 [SC]/[SS]/[IND]/[DSL] 标注 | P1-MAJOR | 是 |
| STD-DOC-04 | 文档版本号一致性 | VERSION 文件与文档头部版本号比对 | P1-MAJOR | 是 |
| STD-DOC-05 | 文档链接有效性 | `scripts/check_doc_links.py` | P1-MAJOR | 是 |
| STD-DOC-06 | Mermaid 图表完整性 | 架构文档必须有至少 1 个 Mermaid 图表 | P2-MINOR | 否 |
| STD-DOC-07 | 文档行数超限检查 | 单文档 > 1500 行需拆分 | P2-MINOR | 否 |
| STD-DOC-08 | 术语一致性 | 对照 90-terminology.md 检查 | P2-MINOR | 否 |

### 8.2 STD-CODE 代码规范检查（5 项）

| 编号 | 检查项 | 检查方法 | 阻断等级 | CI 集成 |
|------|--------|---------|----------|---------|
| STD-CODE-01 | 编译警告零容忍 | `-Wall -Wextra -Werror` | P0-CRITICAL | 是 |
| STD-CODE-02 | checkpatch 通过 | `scripts/checkpatch.pl --strict` | P0-CRITICAL | 是 |
| STD-CODE-03 | clang-format 格式一致 | `clang-format --dry-run -Werror` | P0-CRITICAL | 是 |
| STD-CODE-04 | kernel-doc 无警告 | `scripts/kernel-doc -none` | P1-MAJOR | 是 |
| STD-CODE-05 | 覆盖率 >= 80% | `gcov + lcov` | P1-MAJOR | 是 |

### 8.3 STD-IRON 铁律检查（4 项）

| 编号 | 检查项 | 检查方法 | 阻断等级 | CI 集成 |
|------|--------|---------|----------|---------|
| STD-IRON-01 | 用户空间 ABI 不变 | abi_check.py（6/6 PASS）+ ABI 兼容性检查 | P0-CRITICAL | 是 |
| STD-IRON-02 | 补丁逻辑自包含 | 人工审查（CI 辅助标记） | P0-CRITICAL | 否 |
| STD-IRON-03 | Signed-off-by 链条完整 | DCO bot 自动验证 | P0-CRITICAL | 是 |
| STD-IRON-04 | 无 BUG()/BUG_ON() | `grep -r "BUG\(\)\|BUG_ON("` | P0-CRITICAL | 是 |
| STD-IRON-19 | [SC] 头文件单一数据源 | `scripts/check-sc-single-source.sh` | P0-CRITICAL | 是 |

### 8.4 版本库卫生检查（VCS-* 系列，v3.6 新增）

> **OS-STD-PROD-130（版本库卫生检查）**: 版本库卫生以 VCS-* 系列检查强制执行，全部 CI 阻断。

| 编号 | 检查项 | 检查方法 | 阻断等级 | 对应问题 |
|------|--------|---------|----------|---------|
| VCS-01 | 编译产物跟踪检查 | `git ls-files | grep -E "\.(o|a|ko|cmd|log)$|^vmlinux$|^System\.map$"` 必须 0 命中 | P0-CRITICAL | build-arm64.log 被跟踪 |
| VCS-02 | 日志提交检查 | `git diff --cached --name-only | grep "\.log$"` 必须 0 命中（pre-commit hook） | P0-CRITICAL | *.log 提交 |
| VCS-03 | 分支声明一致性 | 解析 `.gitmodules` branch 字段 vs `git submodule status` 实际分支 | P1-MAJOR | develop/hubs-01 vs ALK-6.6-dev |
| VCS-04 | CI 脚本存在性 | 解析 `.github/workflows/*.yml` 的 run 脚本，逐一 `test -f tools/脚本` | P1-MAJOR | 7 个缺失脚本 |
| VCS-05 | O= 分离构建 | CI 一律 `make O=build/`；源码树无产物残留检查 | P1-MAJOR | arm64 产物拦截 |
| VCS-06 | syscall 表登记 | sw_64 syscall.tbl 必须含 548-571 号段 | P1-MAJOR | sw_64 未注册 |
| VCS-07 | CI 路径监听一致性 | workflow 引用文件路径存在性检查 | P1-MAJOR | Kconfig.alk 监听漂移 |
| VCS-08 | .gitignore 完整性 | 必含 `*.o/*.a/*.cmd/*.ko/*.log/vmlinux/System.map` + `!tools/** !scripts/**` | P1-MAJOR | tools/ 未入库 |

### 8.5 文档-实现一致性检查（DS-* 系列，v3.6 新增）

> **OS-STD-DOC-120（文档-实现一致性）**: 文档声称与源码实现的一致性以 DS-* 系列检查强制核验，落实 §1.2 文档-实现一致性义务。

| 编号 | 检查项 | 检查方法 | 阻断等级 |
|------|--------|---------|----------|
| DS-01 | 文档承诺登记状态 | 扫描文档"已落地/已实现"声称，比对 §1.2 三态登记表 | P1-MAJOR |
| DS-02 | 编译期断言落地核验 | `grep -rn "AIRY_COMPILE_ASSERT\|_Static_assert" include/uapi/linux/airymax/`——OS-KER-229 声称落地则必须命中 | P1-MAJOR |
| DS-03 | 文档-代码漂移扫描 | 对已知漂移项（如 10-sc-sched-extension.md §4.1）做 grep 比对：文档写 `__attribute__((aligned(64)))`、源码为 `AIRY_ALIGNED(64)` | P1-MAJOR |
| DS-04 | KUnit 覆盖声称核验 | 文档声称"已落地 KUnit 测试"的模块必须存在 `*_test.c` 且注册 `kunit_test_suites` | P1-MAJOR |
| DS-05 | 版本基线声称核验 | 文档声称的内核版本（如 6.6.147）与 `kernel/Makefile` 版本四元组一致 | P1-MAJOR |

### 8.6 检查脚本规范

> **OS-STD-050**: 检查脚本位于 `scripts/check/` 目录，以 `check-` 前缀命名，退出码 0 = 通过，1 = 违规，2 = 脚本自身错误。

> **OS-STD-051**: 检查脚本必须支持 `--format json` 输出。

> **OS-STD-052**: 检查脚本必须输出明确的违规文件路径和行号。

### 8.7 CI/CD 集成方案

```
.github/workflows/compliance.yml
├── check-copyright        # STD-DOC-01
├── check-forbidden-words  # STD-DOC-02
├── check-doc-links        # STD-DOC-05
├── checkpatch             # STD-CODE-02
├── clang-format-check     # STD-CODE-03
├── kernel-doc-check       # STD-CODE-04
├── coverage-check         # STD-CODE-05
├── dco-check              # STD-IRON-03
├── vcs-hygiene-check      # VCS-01~08（v3.6 新增）
└── doc-claim-check        # DS-01~05（v3.6 新增）
```

---

## 第 9 章 IRON-9 v3 四层共享模型

### 9.1 四层共享模型概述

IRON-9 v3（2026-07 用户决策）确立了 agentrt 与 AirymaxOS **同源且部分代码共享**的关系。v3 在 v2 三层模型基础上新增 [DSL] 降级生存层，形成四层模型：

| 层次 | 共享程度 | 内容 | 组织方式 |
|------|---------|------|---------|
| **[SC] 共享契约层** | 完全共享代码 | 头文件库（10 个核心 [SC] 头文件 + 补充文件，实际 `include/uapi/linux/airymax/` 共 14 个文件含 syscall.xml） | `kernel/include/uapi/linux/airymax/` 唯一物理宿主 |
| **[SS] 语义同源层** | API 签名相同，实现独立 | 调度、安全、IPC、记忆模型、Capability Folding Badge 校验语义 | 各自独立实现，通过契约层保证互操作 |
| **[IND] 完全独立层** | 完全独立 | 驱动、运行时、硬件相关 | 各自独立仓库 |
| **[DSL] 降级生存层** | 最小生存子集 | `#ifdef AIRY_SC_FALLBACK` 降级块：`capability_badge=0`、跳过 C-S9、退化 `airy_cap_check()` slowpath 兜底 | 各自独立仓库（受 [SC] 头文件宏驱动） |

### 9.2 [SC] 共享契约层：物理宿主与文件清单（OS-IRON-008 更新）

> **OS-IRON-008**: 共享契约层是 agentrt 与 AirymaxOS 的代码共享边界，任何变更必须通过双向 CI 验证（agentrt + AirymaxOS CI 同时通过）。[SC] 物理宿主：`kernel/include/uapi/linux/airymax/`（kernel UAPI 路径，H1：magic 0x41524531 / capability_badge offset 40-47）。

**实际文件现状（审查核验）**：`include/uapi/linux/airymax/` 现有 **14 个文件**，含 10 个核心 [SC] 头文件 + `syscall.xml`（codegen 契约源）等：

| # | 文件 | 内容 | 关键字段 |
|---|------|------|---------|
| 1 | `error.h` | 扩展错误码 + Fault 码（A-UEF） | `AIRY_E*` 错误码（120 个）+ `AIRY_FAULT_*`（0x1001+） |
| 2 | `log_types.h` | 日志类型与 Ring Buffer 布局（A-ULP） | `struct airy_log_record`、facility/level/caller_id |
| 3 | `ipc.h` | IPC 协议 SSoT（A-IPC） | `AIRY_IPC_MAGIC=0x41524531`、`struct airy_ipc_msg_hdr` 128B 11 字段、Badge 位布局 |
| 4 | `sched.h` | 调度契约 | sched_tac（SCHED_DEADLINE/SCHED_FIFO，ADR-013 禁 sched_ext）、任务描述符 magic 'AGTS'、vtime Q16.16、`AIRY_ALIGNED(64)` |
| 5 | `memory_types.h` | MemoryRovol L1-L4 | L1_HOT/L2_WARM/L3_COLD/L4_PMEM + GFP 掩码 |
| 6 | `security_types.h` | 安全契约 | POSIX capability 41 ID + LSM 钩子 ID + Cupolas blob + `cap_t` |
| 7 | `cognition_types.h` | 认知契约 | CoreLoopThree 阶段 + Thinkdual 模式 + LLM 推理阶段 |
| 8 | `syscalls.h` | Syscall 契约 | 4 核心 syscall（548-551）+ 20 预留（552-571）= 24 槽位 |
| 9 | `uapi_compat.h` | UAPI 兼容性 + `AIRY_ALIGNED(N)` 宏 + `AIRY_SC_FALLBACK` 降级块 | `__u32`/`__u64` 类型桥接 |
| 10 | `lsm_types.h` | LSM 类型 | `airy_lsm` 钩子类型（`LSM_ORDER_MUTABLE`，纯 C LSM，H5） |
| 11 | `syscall.xml` | codegen 契约源（R-01 已落地） | 4 syscall + linux_base=548 |
| 12-14 | 其他文件 | 按实际目录清单维护 | — |

> 注：10 个核心 [SC] 头文件清单以 `120-cross-project-code-sharing.md` §2.1 与 handbook §4.2 为准；`bpf_struct_ops.h` 为补充共享文件（非 [SC] 核心）。目录清单以实际文件系统为准，本文档登记"14 个文件"为审查时点快照。

### 9.3 [SS] 语义同源层

| 子系统 | agentrt 实现 | AirymaxOS 实现 | 共享的语义 |
|--------|-------------|---------------|-----------|
| 调度 | MicroCoreRT 用户态调度 | sched_tac（SCHED_DEADLINE/SCHED_FIFO） | 任务优先级、抢占模型、时间片语义 |
| 安全 | Cupolas 用户态权限 | airy_lsm 内核模块 + Cupolas 用户态策略 | POSIX capability 41 ID、策略裁决 4 值、Badge 校验语义 |
| IPC | agentrt 消息队列 | AgentsIPC over io_uring `IORING_OP_URING_CMD` | 128B 消息头、C-S9 fastpath Badge 校验 |
| 记忆 | heapstore 用户态 | MemoryRovol 内核态 | L1-L4 卷载语义、遗忘曲线算法 |

### 9.4 [IND] 完全独立层

- AirymaxOS 专属：内核驱动框架、Kbuild、systemd 集成、内核内部 API、printk 日志系统
- agentrt 专属：跨平台用户态运行时、SDK 四语言、CLI/TUI、网关层

### 9.5 [DSL] 降级生存层（落地登记）

[DSL] 降级生存层是 IRON-9 v3 新增的第四层，用于在 [SC] 头文件不可用或 fastpath 校验失败时提供最小生存能力。

**落地登记（已实现）**：
- 触发条件：`#ifdef AIRY_SC_FALLBACK` 编译开关（**编译期跨平台降级，非运行时容错**——E9 已文档化）
- 行为：`capability_badge=0`，跳过 C-S9 fastpath 校验，退化 `airy_cap_check()` slowpath 兜底（`agent_caps[1024]` 静态数组）
- 落地证据：10 个 [SC] 头文件内共 **39 处 `AIRY_SC_FALLBACK` 降级块**（grep 可验证）
- 错误码：`AIRY_ECAP_RADIX_MISS`(-76)、`AIRY_ECAP_STATIC_KEY`(-77)
- opcode 集缩减至 2 种（SEND/RECV）；Fault 码禁用，统一 Panic
- 详见 `10-architecture/11-degraded-survival-layer.md`

### 9.6 与旧版 IRON-9 的差异

| 维度 | IRON-9 v1 | IRON-9 v2 | IRON-9 v3（当前） |
|------|-----------|-----------|-------------------|
| 模型层数 | 3 层 | 3 层 | **4 层**（新增 [DSL]） |
| [SC] 头文件数 | 不共享 | 6 个 | **10 个核心 + 补充文件（宿主目录共 14 文件）** |
| [SC] 物理宿主 | — | `include/airymax/` | **`include/uapi/linux/airymax/`** |
| IPC 数据面 | — | — | **io_uring `IORING_OP_URING_CMD`**（零 syscall） |
| Capability 校验 | — | POSIX capability | **v1.0.1 Capability Folding**（Badge 64-bit + C-S9 ~10ns + `agent_caps[1024]`） |

---

## 第 10 章 Euler 标准兼容性

### 10.1 兼容性声明与 LAYER 双轨制

AirymaxOS（agent-linux）的工程思想与实现方式与 Euler 保持一致性，以便未来兼容 Euler 标准的发行版工具链。**v3.6 更新**：兼容性实现方式从"四层参考"升级为 **LAYER 双轨制**——以 vanilla 6.6.147 为唯一核心基线（IRON-7），在其上叠加 openEuler 硬件适配能力（引用 `10-references/openeuler-tech-reference/11-layer-feasibility-study.md` §2.3）。

```
ALK-6.6 = vanilla 6.6.147（IRON-7 基线）
        + openEuler 硬件适配层（LAYER 双轨制，架构可选）
        + agent-linux 微内核化改造补丁（airy 自有代码）
```

### 10.2 LAYER 双轨制（v3.6 新增）

> **OS-STD-140（LAYER 双轨制）**: openEuler 硬件适配按文件归属采用双轨同步：`arch/sw_64/` 直接导入；`drivers/` 以 quilt 补丁维护。

| 轨道 | 适用范围 | 同步方式 | 理由 |
|------|---------|---------|------|
| **直接导入** | `arch/sw_64/`（申威架构，367 文件） | 整树导入（vanilla 无对应树） | 零冲突，维护成本最低 |
| **quilt 补丁** | `drivers/hooks/` 及其他 `drivers/` 变更 | `git diff` 识别新增/修改文件，cherry-pick 到 `patches/hw-vendor/` | `drivers/` 与 vanilla 重叠，须以可审查补丁维护厂商增量，便于回溯与升级 |

**为何双轨而非单一模式**：`arch/sw_64/` 在 vanilla mainline 无对应树，直接导入零冲突；`drivers/` 与 vanilla 重叠，必须以补丁隔离避免上游 fast-forward/merge 时厂商增量被吞没。二者上游重叠情况相反，故采用不同轨道。

**当前状态登记（审查 A）**：
- `arch/sw_64/` **已导入**（367 文件，sw_64 syscall.tbl 止于 518，**未注册 airy 548-571 号段**——P1 待修复，VCS-06）
- `drivers/` 硬件适配 **未开始**（quilt 轨道待落地）
- `euler_hw_{arm64,sw64,x86}.config` 已落地（CONFIG 碎片）
- 基线对齐：openEuler 24.03 LTS 内核 `6.6.0-145` 段与 vanilla 6.6.147 完全对齐（11-layer-feasibility-study.md §1.3）

**排除项**（LAYER 不提取）：`kernel/sched/`（与 sched_tac 冲突）、`security/`（Airymax 用 vanilla + airy_lsm）、`Makefile.oever`（构建系统隔离）。

### 10.3 协议层兼容

| 协议 | 兼容方式 | 共享代码 |
|------|---------|---------|
| kthread 创建/停止/驻留协议 | 同源协议设计，[IND] 独立实现 | 不共享 |
| IPC 消息传递协议 | 同源协议设计，[IND] 独立实现 | 不共享 |
| capability 令牌协议 | 同源协议设计，[IND] 独立实现 | 不共享 |

### 10.4 接入层兼容

| 接入模式 | 兼容方式 | 共享代码 |
|---------|---------|---------|
| 加速器接入（accel 框架） | 参考设计模式，[IND] 独立实现 | 不共享 |
| GPU 调度器（drm_sched） | 参考设计模式，[IND] 独立实现 | 不共享 |
| eBPF 可编程内核（非核心，H5） | 参考设计模式，[IND] 独立实现（仅 90-observability） | 不共享 |

### 10.5 模块化兼容

| 模块化维度 | 兼容方式 | 共享代码 |
|-----------|---------|---------|
| Kconfig 风格 | 同源工程规范 | 不共享 |
| Makefile 结构 | 同源工程规范 | 不共享 |
| Kbuild 规范 | 同源工程规范 | 不共享 |

### 10.6 工具链兼容

| 工具链 | 兼容方式 | 共享代码 |
|--------|---------|---------|
| GCC/Clang/Rust | 兼容 Euler 发行版工具链 | 工具链共享（开源生态） |
| checkpatch/spatch | 兼容 Euler 发行版工具链 | 工具链共享（开源生态） |
| RPM/dnf 包管理 | 兼容 Euler 发行版工具链 | 工具链共享（开源生态） |

### 10.7 openEuler 构建标准引用（v3.6 新增）

AirymaxOS 借鉴 openEuler 的以下构建工程机制（引用报告 21 openEuler-engineering-standards-v3.6c）：

| 机制 | openEuler 实践 | AirymaxOS 落地 |
|------|---------------|---------------|
| **Makefile.oever 版本解耦** | openEuler 独立版本系统文件 | kernel 基线为 vanilla 纯主线，**不引入 Makefile.oever**（ALK 只新增文件策略），版本以 Makefile.airymaxos 四元组管理 |
| **KABI 构建期校验** | openEuler `kabi.h`（L335-507）KABI_RESERVE 宏体系 | 不引入 KABI 宏；借鉴其"预留→消费"登记思想于 E14（syscall 预留槽显式消费宏 + 编译期断言，待 M2） |
| **KABI 兼容性债务规避** | openEuler 承担 | ALK"只新增文件"策略天然规避（v3.6 核心发现） |

### 10.8 OBS 远程构建（v3.6 新增）

> **OS-BUILD-020（OBS 远程构建）**: sw_64 架构构建采用 OBS（Open Build Service）远程构建通道（引用 `10-references/openeuler-tech-reference/13-obs-remote-build.md`）。

**背景**：本机无 sw_64 工具链（无原生 gcc / 无交叉 gcc / 无 qemu 仿真 / docker.io 不可达），OBS 远程构建是 sw_64 进入可验证构建通道的当前唯一可行方案。

**构建链**：

```
sw_64 构建链 = AirymaxOS:Factory:Kernel（OBS 项目）
             + _service（git 拉取 ALK-6.6-dev 源码 + quilt 补丁）
             + prjconf（sw_64 宏 + toolchain 依赖）
             + airy-kernel.spec（%ifarch sw_64 / merge_config 合入）
             + osc build --arch=sw_64 远程构建
             + 静态验证（vmlinux 符号 / modinfo / objdump）
```

**诚实边界**：OBS 远程构建只能消除"无法编译验证"项；运行态验证（启动、驱动加载、微内核化改造行为）仍依赖原生申威硬件或未来 qemu 上游支持——禁止虚报运行态能力（落实 §1.2 文档-实现一致性义务）。

### 10.9 代码共享边界澄清

> **OS-IRON-009**: 代码共享仅限于 agentrt 与 agent-linux（AirymaxOS）之间，与 Euler 项目仅技术参考，不共享代码。

```
agentrt ←→ AirymaxOS:  [SC] 共享契约层完全共享代码
AirymaxOS ←→ Euler:    仅技术参考（LAYER 硬件适配层 + 工程标准参考），不共享代码
```

### 10.10 兼容性验证检查项

| 检查项 | 验证方法 | 合格标准 |
|--------|----------|----------|
| kthread 协议一致性 | 核对 kthread_create/stop/park API 签名 | 与 Euler 标准签名一致 |
| 加速器接入一致性 | 核对 drivers/accel/ 模式 | 接入模式一致（[IND] 独立实现） |
| Kconfig 风格一致性 | 核对 CONFIG_ 前缀命名 | 与 Euler Kconfig 风格一致 |
| 调度类编号不冲突 | 核对 sched_tac（SCHED_DEADLINE/SCHED_FIFO） | 不与 Euler 已有调度类冲突 |
| sw_64 syscall 登记 | `grep 548-571 arch/sw_64/.../syscall.tbl` | 全部登记（VCS-06） |
| LAYER 正交性 | 核对 LAYER 提取范围（drivers/arch 限定） | 不触及 sched/security 核心 |

---

## 第 11 章 禁词清单与处罚机制

### 11.1 禁词清单

以下词汇在**开源文档**（`docs/docs-linux/`）中**严禁出现**。闭源文档（`docs-closed/agent-linux-dev/`）中允许引用，但应避免不必要的泄露。

> **OS-BAN-010**: 开源文档中严禁出现以下禁词。

| 禁词 | 禁词变体 | 替代表述 | 类别 |
|------|---------|---------|------|
| openEuler | open Euler, openeuler, OpenEuler | "内核发行版" / "行业标杆发行版" | 内核发行版名称 |
| mugen | Mugen, MUGEN | "集成测试框架" | 集成测试框架 |
| KADC | kadc, KADC | — | 内部代号 |
| 智慧中枢 | 智慧中心, 智能中枢 | "认知循环" / "CoreLoopThree" | 旧术语 |

> **完整禁词清单**维护于 `docs-closed/agent-linux-dev/forbidden-words.conf`，检查脚本从该文件读取正则表达式进行匹配。

### 11.2 违规等级

| 等级 | 场景 | 处罚 |
|------|------|------|
| **P0-CRITICAL** | 开源文档中出现内核发行版名称（openEuler 及其变体） | 补丁立即退回，CI 阻断，记录违规 |
| **P1-MAJOR** | 开源文档中出现内部代号（KADC）或旧术语（智慧中枢） | 补丁退回，24h 内修复 |
| **P2-MINOR** | 开源文档中出现集成测试框架名称（mugen） | 审查要求替换，下次迭代修复 |

### 11.3 处罚机制

> **OS-BAN-011**: 违反禁词规则的处理流程：

1. **首次违规**：CI 阻断，补丁退回，警告通知
2. **二次违规**：CI 阻断，补丁退回，维护者记录，要求提交整改报告
3. **三次违规**：CI 阻断，补丁退回，暂停贡献者权限 1 周，架构委员会审查
4. **四次及以上**：架构委员会讨论是否永久撤销贡献者权限

### 11.4 禁词豁免

- 闭源文档（`docs-closed/`）中引用 openEuler 技术规范（必须）
- 代码注释中引用上游 Linux 内核的 Fixes SHA
- 构建脚本中引用工具链路径（仅限闭源仓库）

---

## 第 12 章 "Linux 6.6 为基、seL4 为鉴"工程取向

### 12.1 工程取向总纲

> **OS-IRON-010**: agent-linux 的工程取向是"Linux 6.6 为基、seL4 为鉴"——以 Linux 6.6 内核基线工程思想为不可动摇的基线（编码风格、构建系统、并发模型、内存模型），以 seL4 微内核思想为架构层的借鉴来源（capability、消息传递、服务用户态化、形式化验证）。

### 12.2 双源边界声明

> **OS-IRON-011**: OLK-6.6 与 seL4 的源码仅在本地参考路径中作为研究对象；agent-linux 与两者的关系是"技术参考"而非"代码共享"。代码共享仅限 agentrt ↔ AirymaxOS 之间的 IRON-9 v3 [SC] 共享契约层。

```
agentrt ←→ AirymaxOS:  IRON-9 v3 [SC] 共享契约层（完全共享代码）
AirymaxOS ←→ Linux 6.6: 技术参考（编码风格 + 工程思想），不共享代码
AirymaxOS ←→ seL4:     技术参考（架构层借鉴），不共享代码
```

### 12.3 编码风格层裁决（7 维度全采纳 Linux 6.6 内核基线）

| 维度 | Linux 6.6 | seL4 | agent-linux 裁决 |
|------|-----------|------|-------------------|
| 缩进 | Tab 8 字符 | 空格 4 | **Linux 6.6** |
| 命名 | snake_case | camelCase | **Linux 6.6** |
| typedef | 最小（5 种例外） | 重度 | **Linux 6.6** |
| 大括号 | K&R | K&R | **一致** |
| 行宽 | 80 列 | ~100 | **Linux 6.6** |
| 错误处理 | 负 errno + goto 集中出口 | exception_t 枚举 | **Linux 6.6** |
| 注释 | kernel-doc 强制 | 普通 | **Linux 6.6** |

> **OS-STD-060**: 编码风格层 7 维度必须全部与 Linux 6.6 内核基线对齐。seL4 编码约定（4 空格 / camelCase / 重度 typedef）禁止使用。

### 12.4 工程思想层：ES-OLK-1~13 全部采纳

Linux 6.6 内核基线的 13 项工程思想（ES-OLK-1~13）是 agent-linux 工程基线层的基石，完整映射见附录 D。

### 12.5 架构层借鉴 seL4（5 项选择性借鉴）

seL4 的工程思想在架构层被选择性借鉴（ES-SEL4-1~5）：极简原则、capability 单一权限模型、服务用户态化、消息传递 IPC（fastpath）、形式化验证驱动。完整映射见附录 E。

### 12.6 架构层借鉴 seL4 的边界

> **OS-IRON-012**: seL4 工程思想的借鉴仅限架构层（ES-SEL4-1~5），不包括编码风格层（4 空格 / camelCase / 重度 typedef）和接口契约层（syscall.xml / structures.bf codegen —— 这两项作为 P2 增强建议增量落地，syscall.xml 即 R-01 已落地，structures.bf 即 R-02 待落地）。

以下 seL4 特性因与 Linux 6.6 基线冲突被拒绝：4 空格缩进、camelCase 命名、重度 typedef、内核非抢占无并发模型、无动态内存分配、exception_t 错误码。

### 12.7 双源融合裁决总表（16 维度）

双源融合裁决覆盖 16 个维度，其中 11 维度采纳 Linux 6.6 内核基线、5 维度借鉴 seL4 或融合。完整裁决表见附录 F。

### 12.8 ES-SEL4-6~10 的落地方式

| seL4 工程思想 | 落地方式 | 状态 | 对应 P2 建议 |
|-------------|---------|------|-------------|
| ES-SEL4-6 接口契约 XML | syscall.xml + syscall_gen.py codegen 管道 | ✅ 已落地（v2.9） | R-01（§14.1） |
| ES-SEL4-8 bitfield codegen | structures.bf 式位域 codegen | 待落地 | R-02（§14.2） |
| ES-SEL4-9 libsel4 独立 | SDK 层借鉴 libsel4 模型 | 已落地 | 已在 cloudnative 落地 |
| ES-SEL4-10 CMake 构建 | 用户态子仓采用 Meson/CMake | 已落地 | services/cloudnative |
| ES-SEL4-7 架构正交分层 | arch/machine/plat 三层适配 | 已落地 | kernel 子仓 |

### 12.9 形式化验证工程标准（v3.6 更新：seL4 四件套映射）

> **OS-TEST-010**: tests-linux 子仓必须包含 formal-verification/ 目录，采用 seL4 三段式结构（spec/proof/capdl）。

**v3.6 更新**：第三轮审查（E1-E3，报告 22）将"seL4 为鉴"从架构层延伸到**工程方法层**，形成四件套映射（引用 `docs/docs-linux/80-testing/10-formal-verification.md`）：

| 件 | seL4 参考 | AirymaxOS 落地 | 状态 |
|----|----------|---------------|------|
| **1. AIRY_COMPILE_ASSERT 双模式宏** | seL4 `assert.h` L45-69（c99/c11 双模式 `_Static_assert`） | `uapi_compat.h` 定义双模式宏，应用于 syscalls.h/ipc.h 内核-用户态常量一致性钉死 | **E1，预留待 M2**（源码零命中，OS-KER-229 声称与实现空白见 §1.2） |
| **2. MODIFIES/FNSPEC 验证注解** | seL4 `util.h` L93/L189-196 | 标注 capability/IPC fastpath 的修改集与函数规格 | **E2，预留待 M3-M5** |
| **3. 验证配置锁存** | seL4 `configs/*_verified.cmake`（40+） | `airymax_verified.cmake` 等价物声明（known-caveats 附录） | **E3，预留待 M3-M5** |
| **4. CAVEATS 诚实声明** | seL4 `CAVEATS.md` L127-155 | `09-known-caveats.md` 诚实声明（E4 SMP 验证覆盖标注） | **E4 已文档化** |

**验证路径（1.0.1+ 启动）**：v1.0.1 阶段以 **CBMC** 为 fastpath 验证主力（`airy_cap_check` bounded model checking，高置信度工程证据），v1.2+ 引入 **Isabelle/HOL** 逐步精化证明以缩小与 seL4 "数学证明"的鸿沟（10-formal-verification.md §4.5/§4.6）。

**工程诚信要求**：形式化验证的每项声称必须登记落地状态（§1.2）；未实现的验证承诺必须标注"预留"，禁止文档超前声称（v3.6c 可验证性预留 68 分 D+ 的教训）。

---

## 第 13 章 8 子仓目录结构工程标准

### 13.1 8 子仓总览与现状

> **OS-IRON-013**: agent-linux 拆分为 8 个独立 git 仓库（leaf 仓），由 agent-linux 管理仓通过 submodule 统一管理，另设 build/tools/scripts 管理仓目录。

**现状登记（审查 C 核验）**：

| 子仓 | 依赖层次 | 现状 | 构建系统 |
|------|---------|------|---------|
| `kernel` | L2（自包含，[SC] 唯一宿主） | **M0 框架编译验证通过**（vanilla 6.6.147 + sw_64 367 文件 + airy 44 个 .c） | Kbuild + Kconfig |
| `security` | L3 | 最小骨架（7 轻仓） | Kbuild + Meson |
| `memory` | L3 | 最小骨架 | Kbuild |
| `cognition` | L4 | 最小骨架 | Cargo（Rust） |
| `services` | L5 | 最小骨架 | Meson |
| `system` | L6 | 最小骨架 | Kbuild + Meson |
| `cloudnative` | L7 | 最小骨架 | Go Modules |
| `tests-linux` | L7（横向） | **当前 1 个测试**（KUnit 主要在 kernel 侧 5+1，见 §6.5） | KUnit + kselftest |

**落地顺序**: L2（kernel）→ L3（security/memory）→ L4（cognition）→ L5（services）→ L6（system）→ L7（cloudnative/tests-linux）。

> **OS-IRON-014**: [SC] 共享契约层头文件仅物理宿主于 `kernel/include/uapi/linux/airymax/`，是唯一物理副本。其他子仓通过 `-I../kernel/include` 构建路径引用，**禁止**创建物理副本。

### 13.2 目录结构设计原则

> **OS-STD-061**: 8 子仓目录结构遵循 7 项设计原则：关注点分离、架构正交（arch/machine/plat 三层）、[SC] 单一数据源、corekern 极简（4 原子机制）、构建系统混合、formal-verification 三段式、生产级 fork 模型。

### 13.3 kernel 子仓目录结构与现状

kernel 采用**模型 A（完整 Linux 6.6 fork）**——自包含完整上游源码树，Airymax 修改直接写入上游目录：

```
kernel/
├── arch/                    # x86_64 / arm64 / sw_64（LAYER 双轨制直接导入，367 文件）
│   └── {x86,arm64,sw_64}/configs/airy_defconfig   # 三架构 airy_defconfig
├── include/uapi/linux/airymax/  # [SC] 共享契约层（14 文件，§9.2）
├── kernel/corekern/         # Airymax 微核心抽象层（sched/ipc/taskflow/memory/time/object/locking/irq/bpf/api）
├── kernel/syscalls/         # airy_syscalls（4 核心 syscall 548-551 入口）
├── kernel/log/              # airy_log_kern/persist/ring
├── kernel/ipc/              # airy_ipc_capability/syscall
├── security/airy/           # airy_lsm（纯 C LSM）+ capability（cap_init/array/derive/check/revoke/rotate）+ die_notify/eventfd/ipc_freeze + KUnit 测试
├── fs/ net/ block/ drivers/ mm/ ...   # [模型 A] 完整继承上游
├── configs/euler_hw_{arm64,sw64,x86}.config  # LAYER 硬件 CONFIG 碎片
├── Kconfig / Makefile / Kbuild        # SECURITY_AIRY master + AIRY_IPC/COREKERN/SYSCALL/LOG/KUNIT
└── Makefile.airymaxos      # AirymaxOS 版本四元组
```

**工程框架接线现状（审查 A）**：
- Kconfig：`SECURITY_AIRY` master + `AIRY_IPC`/`AIRY_COREKERN`/`AIRY_SYSCALL`/`AIRY_LOG`/`AIRY_KUNIT` + `AIRY_CAP_TABLE_SIZE=1024` 全接线（约 90% 完成）。
- 三架构 `airy_defconfig`（x86_64 / arm64 / sw_64）。
- **arm64 + airy 完整构建通过**；x86 `prepare` 通过。
- airy 自有代码 **44 个 .c**（含 5 个 KUnit 测试 + 1 个 benchmark）。
- **版本库卫生问题待修复**：build-arm64.log 被 git 跟踪（§5.6）、sw_64 syscall.tbl 未注册 548-571（VCS-06）。

### 13.4 其他 7 子仓目录结构概要

> **OS-STD-062**: 其余 7 子仓完整目录结构见 `20-archive/designs/_design_0.2.4/01-agent-linux-directory-structure.md`。每个子仓必须包含 MAINTAINERS 文件（R-03）和 Documentation/ 目录（ES-OLK-13）。

### 13.5 构建系统工程标准与 build/ 目录规范

> **OS-BUILD-010**: 内核态子仓（kernel/security/memory/system）必须采用 Kbuild + Kconfig + Makefile 三层构建系统。用户态子仓采用各自生态主流构建系统。

**build/ 目录规范（v3.6 新增，审查 C）**：
- `build/` 是**构建定义**目录，**不是编译产物目录**（编译产物走 `make O=<builddir>` 外部目录）。
- 每个构建目标三件套：

| 件 | 文件 | 内容 |
|----|------|------|
| spec | `*.spec` | RPM 构建定义（如 `airy-kernel.spec`，含 `%ifarch sw_64` / merge_config） |
| ks | `*.ks` | Kickstart 安装定义（镜像装配） |
| meta | `meta/` | 元数据（版本、依赖、changelog） |

- OBS 项目映射：`AirymaxOS:Factory`（主线滚动）→ `AirymaxOS:Factory:Kernel`（内核专项，§10.8）。

### 13.6 形式化验证工程标准

> **OS-TEST-010**: tests-linux 子仓必须包含 formal-verification/ 目录（spec/proof/capdl 三段式）。形式化验证范围（1.0.1 阶段）：仅覆盖关键路径（调度器核心、IPC fastpath、capability 派生模型）。四件套工程方法见 §12.9。

---

## 第 14 章 P2 增强建议与 E1-E17 落地登记

### 14.1 R-01：syscall.xml 式接口契约定义（✅ 已落地 v2.9）

> **OS-STD-070**（✅ 已落地，v2.9 2026-07-22）: 为 [SC] 共享契约层引入 seL4 风格的 syscall.xml 接口契约定义，由代码生成器自动生成用户态 stub 与内核态 entry 表。

| 维度 | 详情 |
|------|------|
| 借鉴来源 | seL4 `tools/syscall.xml` + `syscall_generator.py`（ES-SEL4-6） |
| 落地范围 | 4 核心 syscall（548-551）的接口契约 XML 化 |
| **落地产物** | `kernel/include/uapi/linux/airymax/syscall.xml` + `tools/codegen/syscall_gen.py`（314 行）+ `tools/codegen/Makefile` |
| **状态** | ✅ 已落地（ES-SEL4-6 已更新为"已落地（v2.9）"） |

### 14.2 R-02 ~ R-04（建议项）

| 建议 | 内容 | 里程碑 | 状态 |
|------|------|--------|------|
| R-02 structures.bf bitfield codegen | seL4 structures.bf 式位域 codegen（ES-SEL4-8） | M1 | 待落地 |
| R-03 8 子仓 MAINTAINERS | 8 子仓各 1 个 MAINTAINERS 文件（ES-OLK-8） | M5 | 待落地 |
| R-04 合规检查增补 | OS-CHK-DOC-18/19 + OS-CHK-IRON-18 + OS-CHK-CODE-08（依赖 R-01/R-02/R-03） | R-01/02/03 后 | 部分满足（R-01 已落地） |

### 14.3 E1-E17 落地状态登记表（v3.6c 新增）

> 第三轮审查（v3.6c）产出 E1-E17 共 17 项工程标准改进（报告 23 优先级矩阵），本表为落地状态登记。**登记原则落实 §1.2 文档-实现一致性义务**：未实现项一律标注"预留"。

| 编号 | 标题 | 优先级 | 状态 | 落地位置/里程碑 |
|------|------|--------|------|----------------|
| E1 | [SC] 头文件引入 AIRY_COMPILE_ASSERT 编译期契约宏 | P1 | **预留，待 M2**（源码零命中） | `uapi_compat.h` 定义双模式宏 + syscalls.h/ipc.h 应用 |
| E2 | MODIFIES/FNSPEC 验证注解（capability/IPC fastpath） | P2 | **预留，待 M3-M5** | airy_cap.h / airy_ipc_fastpath.c |
| E3 | 验证配置锁存（airymax_verified.cmake 等价物） | P2 | **预留，待 M3-M5** | 09-known-caveats.md 附录 |
| E4 | known-caveats 增加 SMP 验证覆盖标注 | P1 | ✅ 文档类已完成 | 09-known-caveats.md L65-72 |
| E5 | Liedtke 论证义务落地（内核子系统"无法在用户态实现"论证 gate） | P2 | **预留，待 M3-M5** | 09-ssot-registry.md |
| E6 | sched_tac 机制/策略边界文档化 | P1 | ✅ 文档类已完成 | stc_dispatch.c L50-70 |
| E7 | sched.h/stc_policy.h 两套策略枚举语义统一（UAPI 只暴露 AIRY_SCHED_POLICY_*） | P1 | **预留，待 M2** | sched.h L102-105 vs stc_policy.c L17-22 |
| E8 | zero_copy buffer 与 MemoryRovol 版本治理交互文档化 | P2 | **预留，待 M3-M5** | airy_ipc_zero_copy.c |
| E9 | [DSL] 触发时域文档化（编译期跨平台降级，非运行时容错） | P1 | ✅ 文档类已完成 | uapi_compat.h L95-132 |
| E10 | airy_enabled 默认值注释与代码一致性修复 | P1 | ✅ 文档类已完成 | airy_lsm.c L30-31/L51 |
| E11 | AIRY_CAP_PERM_* 权限位枚举 SSoT（集中于 security_types.h） | P2 | **预留，待 M3-M5** | airy_cap.h L75 |
| E12 | IPC 唯一合法入口声明（fastpath 不得绕过 LSM 5-phase 校验） | P1 | ✅ 文档类已完成 | airy_ipc_fastpath.c L11-46 |
| E13 | airy_ipc_fastpath.c L3 版权行 SPHARx 拼写修复 | P3 | ✅ 文档类已完成 | airy_ipc_fastpath.c L3 |
| E14 | KABI_USE 式"预留→消费"登记机制（syscall 20 预留槽显式消费宏 + 编译期断言） | P1 | **预留，待 M2** | syscalls.h L26-29 |
| E15 | KABI_RESERVE_BYTES 式 UAPI 结构体预留字节 | P2 | **预留，待 M3-M5** | ipc.h 128B 头 |
| E16 | lockdep_set_class 锁类注解（per-bucket 锁/全局锁） | P2 | **预留，待 M3-M5** | airy_cap.h L52-56 |
| E17 | [SC] 头文件三方一致性构建期 baseline diff 校验脚本 | P2 | **预留，待 M3-M5** | scripts/（E17 脚本） |

**E1-E17 与第一/二轮交叉项**：E1 ↔ 第一轮 R-01/R-02（compile_assert 是 R-01 最小可行先行步）；E2 ↔ 第二轮 N12/N17/N9 验证视角；E7 ↔ 第二轮 N11 + 第一轮 P2-8；E16 ↔ 第二轮 N4/N10。

---

## 第 15 章 v1.0.1 Capability Folding 与 6 条硬约束

### 15.1 Capability Folding 设计模式

**核心论断**：IPC 不是承载能力校验——IPC 就是能力校验。

Capability Folding 是将 capability check 从独立控制面操作"折叠"到 IPC 数据面 fastpath 中的设计模式。IPC 消息头 `capability_badge` 字段（offset 40-47）承载 64-bit Native Word Badge，由 fastpath C-S9 内联校验（~10ns，已由 `airy_fastpath_bench.c` 实测 2-10ns）。

**架构要素**：
- 4 核心 syscall + 20 预留 = 24 槽位（Linux 注册号 548-571）
- IPC 数据面：完全由 io_uring `IORING_OP_URING_CMD` 承载（零 syscall）
- `agent_caps[1024]` 静态数组（16KB），sec_d 唯一写者
- Badge 64-bit：`Epoch<<48 | RandomTag<<16 | Perms`
- O(1) 撤销：`atomic_inc(&airy_cap_global_epoch)`
- fastpath C-S9 内联校验（~10ns）+ slowpath LSM 钩子（airy_lsm 5-phase）

### 15.2 6 条硬约束 H1-H6（不可妥协）

| 约束 | 内容 |
|------|------|
| **H1** | Layout C v4 总长 128B / magic 0x41524531 / capability_badge offset 40-47（8 字节对齐） |
| **H2** | capability_badge 字段进 [SC] ipc.h，Badge 校验机制属 [SS] |
| **H3** | agentrt 用户态 capability_badge=0（跳过 C-S9） |
| **H4** | agent-linux 内核 Badge 由 sec_d 编译、fastpath C-S9 校验 |
| **H5** | 纯 C LSM 职责不变（不使用 BPF LSM，airy_lsm 代码完整性通过编译期校验 + CBMC 形式化验证保证） |
| **H6** | [DSL] 降级 capability_badge=0 跳过 C-S9 |

### 15.3 12 daemon 命名统一（v2.0 决策，无例外）

> **OS-IRON-016**: 12 daemon 命名统一遵循 `*_d` 后缀约定（v2.0 决策，无例外，ADR-013）。

`macro_d` / `gateway_d` / `sched_d` / `logger_d` / `vfs_d` / `net_d` / `cogn_d` / `dev_d` / `config_d` / `mem_d` / `audit_d` / `sec_d`。旧称禁止使用：`macro_superv`、`logger_daemon`、`config_daemon`、`drv_d`（→ `dev_d`）、`llm_d`（→ `cogn_d`）、`tool_d`（→ `dev_d`）、`market_d`（→ `gateway_d`）。

### 15.4 关键 ADR 引用（v1.0.1）

| ADR | 标题 | 决策内容 |
|-----|------|---------|
| ADR-012 | 微内核化改造技术路线确认 | 基于 Linux 改造 + seL4 思想，非从零开发 |
| ADR-013 | 调度框架决策 | sched_tac（SCHED_DEADLINE/SCHED_FIFO），禁止 sched_ext |
| ADR-014 | 微内核设计思想来源单一化 | 仅 seL4，不引入 Zircon/Minix3 |
| ADR-016 | 版本基线锁定 | 1.x.x 锁定 Linux 6.6 |

### 15.5 路径与命名约定（v1.0.1）

| 项目 | 路径/值 |
|------|---------|
| [SC] 头文件宿主 | `kernel/include/uapi/linux/airymax/` |
| 配置文件路径 | `/etc/agentrt/` |
| 持久化数据路径 | `/var/lib/airy/` |
| 日志路径 | `/var/log/agentrt/` |
| IPC magic | `0x41524531` ('ARE1') |
| 任务描述符 magic | `0x41475453` ('AGTS') |
| IPC 消息头大小 | 128 字节（11 字段，2 cache lines） |
| capability_badge offset | 40 |
| Syscall 数 | 4 核心（548-551）+ 20 预留（552-571）= 24 槽位 |

### 15.6 SSoT 权威源体系（v3.0）

agent-linux 的 SSoT 权威源体系由五大权威源构成：规则编号 SSoT（`09-ssot-registry.md`）、syscall 编号 SSoT（`07-syscall-registry.md`）、ABI 三方一致性（SSoT + unistd.h + syscall_64.tbl，`abi_check.py` 强制 6/6 PASS）、codegen 契约 SSoT（`syscall.xml`）、ABI 检查工具 SSoT（`abi_check.py`）。任何文档/代码/工具与 SSoT 冲突时，以 SSoT 为准（OS-IRON-018~021）。

**变更流程（强制）**：先更新 SSoT → 同步 unistd.h 与 syscall_64.tbl → 更新 syscall.xml → 运行 abi_check.py（6/6 PASS）→ 同步下游文档 → 更新 abi_baseline.json。

### 15.7 v3.6 已落地登记（新增）

> v3.6 闭环确认以下 Capability Folding 相关改进已落地（源码证据可 grep 验证）：

| 改进项 | 内容 | 落地证据 |
|--------|------|---------|
| **P1-10 COPY 权限降级** | COPY 支持权限子集降级（`copy_subset_perms_monotonic_test`） | `airy_cap_derive.c` + `airy_cap_derive_test.c`（KUnit 断言降级单调性） |
| **P1-8 cancelBadgedSends 等价机制** | 取消特定 badge 的挂起发送（对标 seL4 endpoint.c L476-489） | `airy_ipc_capability.c` 相关接口已落地 |
| **P1-9 REVOKE 非级联语义文档化** | REVOKE 无级联撤销的决策显式文档化（UAPI 兼容优先） | `airy_cap_derive.c` L190-206 注释 + 契约文档 |

**P1-11（全局 spinlock → per-bucket 锁）部分收敛**：`airy_cap_array.c` L27-30 已实现 per-bucket 锁（cap_array 读路径）；`airy_cap_derive.c` 全局锁与 `airy_object.c` 全局锁（N4）仍待 M3-M5 统一 per-bucket 锁设计模式。

---

## 附录 A v3.6 审查 68 项改进闭环总表

> **数据来源**：`20-archive/reviews/_review_v3.6/`（07 第一轮 / 17 第二轮 / 23 第三轮 + 08/18 闭环摘要）。三轮回合计 68 项（去重后 66 项：E18-E22 并入 E1-E3，E1 与第一轮 R-01/R-02 同源）。
> **状态口径**：✅ 已修复（有源码证据）/ 📄 文档类已完成 / ⏳ 待 M2 / 🕐 待 M3-M5 / ⚠️ 待核验。

### A.1 第一轮 v3.6（核心机制，29 项：P0-1 + P1-11 + P2-17）

#### A.1.1 P0（1 项）

| 编号 | 标题 | 优先级 | 状态 | 落地位置 |
|------|------|--------|------|---------|
| P0-1 | 552-571 预留 syscall 槽位未在 syscall_64.tbl 显式登记 | P0 | ✅ 已修复（syscall_64.tbl 显式占位登记） | `arch/x86/entry/syscalls/syscall_64.tbl` |

#### A.1.2 P1（11 项）

| 编号 | 标题 | 优先级 | 状态 | 落地位置 |
|------|------|--------|------|---------|
| P1-1 | stc_dispatch.c 用 pr_info 影响性能 | P1 | ⏳ 待 M2（pr_info → tracepoint） | stc_dispatch.c L73-75 |
| P1-2 | stc_stats 未通过 debugfs/sysfs 暴露 | P1 | ⏳ 待 M2 | stc_stats.c L20-39 |
| P1-3 | airy_vtime_decay 语义偏差（注释声称 EEVDF，实为旧 CFS） | P1 | 📄 注释修正已完成 | sched.h L42-50 |
| P1-4 | task_kill/file_open 仅检查 agent_state，缺完整 Badge 校验 | P1 | ✅ 已修复（LSM 主入口 Badge 校验对称） | airy_lsm.c L112-117/L144-149 |
| P1-5 | airy_ipc_capability.c 用 __aligned(64) 违反 OS-IRON-016 | P1 | ✅ 已修复（→ AIRY_ALIGNED(64)） | airy_ipc_capability.c L29-30 |
| P1-6 | airy_inode_sec 未接线到 VFS，file_open 无法 per-inode 检查 | P1 | 🕐 待 M3-M5（8h） | lsm_types.h L40-43 |
| P1-7 | fastpath_send 不含 Badge 校验的决策未文档化 | P1 | 📄 决策文档化已完成（LSM hook 完成校验） | airy_ipc_fastpath.c L31-34 |
| P1-8 | 缺少 cancelBadgedSends 等价机制 | P1 | ✅ 已修复（已落地，§15.7） | 对标 seL4 endpoint.c L476-489 |
| P1-9 | REVOKE 无级联撤销，派生 cap 不受影响 | P1 | ✅ 已修复（非级联语义文档化，§15.7） | airy_cap_derive.c L190-206 |
| P1-10 | COPY 不支持权限子集降级 | P1 | ✅ 已修复（COPY 降级落地，§15.7） | airy_cap_derive.c L79-104 |
| P1-11 | 全局单一 spinlock 可扩展性瓶颈 | P1 | ⚠️ 部分收敛（cap_array per-bucket 已落地；derive/object 全局锁待 M3-M5） | airy_cap_derive.c L27 / airy_cap_array.c L27-30 |

#### A.1.3 P2（17 项）

| 编号 | 标题 | 优先级 | 状态 | 落地位置 |
|------|------|--------|------|---------|
| P2-1 | 缺少 CBS 带宽准入（dl_bw 等价） | P2 | 🕐 待 M3-M5 | stc_dispatch.c L87 |
| P2-2 | syscall 入口无 budget 检查 | P2 | ⏳ 待 M2 | airy_syscalls.c L78-198 |
| P2-3 | 缺少 SC 捐赠与 consumed time 上报 | P2 | 🕐 待 M5 | 对标 seL4 endpoint.c L101-103 |
| P2-4 | 缺少 lockdown 机制 | P2 | 🕐 待 M3-M5 | 对标 openEuler security.c L43-75 |
| P2-5 | security_hook_heads 注册阶段未明确 | P2 | 📄 已文档化（boot-only） | airy_lsm.c L150-154 |
| P2-6 | 5 hook 可观测性不足，扩展计划未文档化 | P2 | 🕐 待 M3-M5（文档） | lsm_types.h L23 |
| P2-7 | ring_post magic check 冗余性评估 | P2 | ⏳ 待 M2 | airy_ipc_ring.c L71 |
| P2-8 | 借鉴 xsched sched_attr 扩展属性 | P2 | 🕐 待 M3 | 对标 openEuler syscall_64.tbl L391-392 |
| P2-9 | syscall_gen.py SSoT 流程文档化 | P2 | 🕐 待 M3（文档） | tools/codegen/syscall_gen.py L310-364 |
| P2-10 | 缺少 derive_tree 派生关系追踪 | P2 | 🕐 待 M3 | airy_ipc_capability.c L29-32 |
| P2-11 | CNodeSaveCaller 不实现的决策未文档化 | P2 | 📄 已文档化 | 对标 seL4 cnode.c L36-40 |
| P2-12 | ALK vs KABI 权衡决策未文档化 | P2 | 🕐 待 M3（文档） | 对标 openEuler sched.h L722 |
| P2-13 | _reserved 字段命名不统一 | P2 | 📄 已统一（`_reserved[N]`） | lsm_types.h L53 vs sched.h L70 |
| P2-14 | MemoryRovol（549）M5 实现规划 | P2 | 🕐 待 M5 | airy_syscalls.c L143-151 |
| P2-15~17 | 第一轮 P2 段剩余 3 项（内存/版本治理维度，见第一轮子域报告 06） | P2 | ⚠️ 待核验 | 以 20-archive/reviews/_review_v3.6/06 报告为准 |

### A.2 第二轮 v3.6b（基础设施，22 项：N1-N22）

#### A.2.1 P1 级（10 项）

| 编号 | 标题 | 优先级 | 状态 | 落地位置 |
|------|------|--------|------|---------|
| N1 | airy_kern_api_init 仅串联 locking_init，7 子系统 init 未统一调度 | P1 | ⏳ 待 M2（4h） | airy_kern_api.c L1-48 |
| N2 | airy_superv_lsm.c 5 补充钩子缺 Badge 校验 | P1 | ⏳ 待 M2（与 P1-4 同源） | airy_superv_lsm.c L41/L84/L98 |
| N3 | airy_ipc_ring_for_task() M0 恒返回 NULL，die_notifier freeze 死代码 | P1 | 📄 M0 占位注释完成 + ⏳ 实现待 M2 | airy_ipc_freeze.c L110-124 |
| N4 | airy_object.c 全局单 spinlock + O(N) lookup | P1 | ⏳ 待 M2（per-bucket + idr） | airy_object.c L1-90 |
| N5 | airy_time.c 无 hrtimer 封装，agent 超时唤醒缺失 | P1 | ⏳ 待 M2 | airy_time.c L1-33 |
| N6 | airy_irq.c 无 agent IRQ 路由，无 IRQControl 等价物 | P1 | 🕐 待 M3 | airy_irq.c L1-43 |
| N7 | airy_mem_alloc.c 无 memcg 集成，无 per-agent 内存账户 | P1 | ⏳ 待 M2 | airy_mem_alloc.c L1-46 |
| N8 | airy_mem_tier.c tier 分类仅靠 GFP 低 4 位，无 NUMA/CXL 路由 | P1 | 🕐 待 M4 | airy_mem_tier.c L1-52 |
| N9 | airy_bpf_probe.c + airy_struct_ops.c 未真正接入 BPF | P1 | 🕐 待 M3 | airy_struct_ops.c L1-61 |
| N10 | airy_locking.c 无 RCU wrapper，cap_array 高频读未利用 RCU | P1 | ⏳ 待 M2 | airy_locking.c L1-47 |

#### A.2.2 P2 级（12 项）

| 编号 | 标题 | 优先级 | 状态 | 落地位置 |
|------|------|--------|------|---------|
| N11 | airy_task_lifecycle.c 无显式 suspend/resume | P2 | 🕐 待 M3-M5 | airy_task_lifecycle.c L68-140 |
| N12 | airy_log_ring.c 满时 overwrite 无溢出计数器/告警 | P2 | 🕐 待 M3-M5 | airy_log_ring.c L153-154 |
| N13 | airy_die_notify.c 仅映射 4 种 die reason | P2 | 🕐 待 M3-M5 | airy_die_notify.c L64-80 |
| N14 | airy_eventfd.c 单全局 ctx，多 Macro-Supervisor 无法区分 | P2 | 🕐 待 M3-M5 | airy_eventfd.c L1-144 |
| N15 | airy_ipc_zero_copy.c 注册表全局链表+单 spinlock | P2 | 🕐 待 M3-M5 | airy_ipc_zero_copy.c L1-168 |
| N16 | airy_mem_tier_shift 静态表无 sysfs 暴露 | P2 | 🕐 待 M3-M5 | airy_mem_tier.c |
| N17 | airy_log_persist.c 同步 kernel_write，无异步刷盘线程 | P2 | 🕐 待 M3-M5 | airy_log_persist.c L1-102 |
| N18 | airy_cap_rotate.c 单行委托可内联到 airy_cap.h | P2 | 📄 已完成（内联） | airy_cap_rotate.c L1-38 |
| N19 | airy_log_kern.c 8→5 级别映射丢失 ALERT/CRIT/NOTICE 粒度 | P2 | 📄 粒度损失已文档化 | airy_log_kern.c L1-103 |
| N20 | airy_superv_lsm.c mmap_addr 未对接 cap_array 地址白名单 | P2 | 🕐 待 M3-M5 | airy_superv_lsm.c |
| N21 | airy_superv_lsm.c file_mprotect 仅 W^X 检查，未对接 cap_array PROT_EXEC | P2 | 🕐 待 M3-M5 | airy_superv_lsm.c |
| N22 | airy_kern_api.c late_initcall 时机晚于 fs/sched/etc | P2 | 📄 时机取舍已文档化 | airy_kern_api.c |

### A.3 第三轮 v3.6c（工程标准，17 项：E1-E17）

完整登记见 §14.3 落地状态登记表。摘要：

| 分组 | 编号 | 状态 |
|------|------|------|
| 可验证性预留（compile_assert/验证注解/配置锁存） | E1 / E2 / E3 | ⏳ 待 M2 / 🕐 待 M3-M5 / 🕐 待 M3-M5 |
| 文档一致性（SMP 标注/[DSL] 时域/机制策略边界/入口声明） | E4 / E6 / E9 / E10 / E12 / E13 | 📄 文档类已完成 |
| 接口工程（预留登记/UAPI 预留字节/权限位 SSoT/枚举统一） | E7 / E14 / E11 / E15 | ⏳ 待 M2 / ⏳ 待 M2 / 🕐 待 M3-M5 / 🕐 待 M3-M5 |
| 并发与锁（lockdep 注解） | E16 | 🕐 待 M3-M5 |
| 构建与 CI（baseline diff） | E17 | 🕐 待 M3-M5 |
| 治理（Liedtke 论证 gate） | E5 | 🕐 待 M3-M5 |
| 细节修正（注释漂移/版权拼写） | E10 / E13 | 📄 文档类已完成 |

### A.4 闭环状态汇总

| 状态分组 | 数量 | 说明 |
|---------|------|------|
| ✅ 已修复（P1/P0 级） | **12 项** | P0-1 + P1-4/5/8/9/10（源码证据）+ 其余低工作量修复项（按 v3.6 闭环报告 08/18 统计口径） |
| 📄 文档类已完成 | **15 项** | P1-3/P1-7/P2-5/P2-11/P2-13 + N3(文档)/N18/N19/N22 + E4/E6/E9/E10/E12/E13 |
| ⏳ 待 M2 | 约 14 项 | P1-1/2 + P2-2/7 + N1/2/3(实现)/4/5/7/10 + E1/7/14 |
| 🕐 待 M3-M5 | 约 25 项 | 其余 P1/P2/N/E 项（含 P2-15~17 待核验） |
| ⚠️ 待核验 | 3 项 | P2-15~17 |

> **说明**：①"已修复 12 项 P1/P0"为审查方核验口径（含 P0-1 与 P1-4/5/8/9/10 等有明确源码证据的项，以及 P1-1/P1-3/P1-7 等低工作量修复/文档项，具体以 08/18 闭环报告为准）；②三轮回合计 68 项（去重 66 项），本表为闭源侧登记摘要，完整依据见各轮报告。

---

## 附录 B 规则编号注册表

> **SSoT 声明**：本附录为闭源侧摘要登记，**完整规则编号登记的唯一权威来源**为 `09-ssot-registry.md`（v0.2.8）。syscall 编号唯一权威来源为 `07-syscall-registry.md`。本附录与 SSoT 冲突时，以 SSoT 为准。

### B.1 OS-IRON 工程铁律（16 条）

| 编号 | 规则 | 章节 |
|------|------|------|
| OS-IRON-001 | 用户空间 ABI 永不破坏 | §4.1.1 |
| OS-IRON-002 | 内核内部 API 不保证稳定 | §4.1.2 |
| OS-IRON-003 | 策略与机制分离 | §4.3 |
| OS-IRON-004 | 渐进式开发，补丁自包含 | §4.4 |
| OS-IRON-005 | 审查优先文化 | §4.5 |
| OS-IRON-006 | 不破坏用户空间原则 | §4.6 |
| OS-IRON-007 | DCO 强制 | §5.3.4 |
| OS-IRON-008 | [SC] 共享契约层双向 CI 验证 | §9.2 |
| OS-IRON-009 | 代码共享边界：仅 agentrt ↔ AirymaxOS | §10.9 |
| OS-IRON-010 | "Linux 6.6 为基、seL4 为鉴"工程取向 | §12.1 |
| OS-IRON-011 | 双源边界声明 | §12.2 |
| OS-IRON-012 | seL4 借鉴仅限架构层 | §12.6 |
| OS-IRON-013 | 8 子仓独立 git 仓库 + submodule 管理 | §13.1 |
| OS-IRON-014 | [SC] 头文件单一数据源 | §13.1 |
| OS-IRON-015 | 编号管理元规则（编号不得复用） | 附录 B 声明 |
| OS-IRON-016 | UAPI 头文件编译器无关原则（AIRY_ALIGNED） | §2.1.6 |
| OS-IRON-017 | v1.0.1 Capability Folding 6 条硬约束 H1-H6 | §15.2 |
| OS-IRON-018 | syscall 编号 SSoT | §15.6 |
| OS-IRON-019 | ABI 三方一致性（abi_check.py 强制） | §15.6 |
| OS-IRON-020 | codegen 契约 SSoT（syscall.xml） | §15.6 |
| OS-IRON-021 | ABI 检查工具 SSoT（6/6 PASS 方可合并） | §15.6 |

### B.2 OS-BAN 禁止规则

| 编号 | 规则 | 章节 |
|------|------|------|
| OS-BAN-001 | 敏感术语禁用 | §2.1.4 |
| OS-BAN-002 | 禁止 BUG()/BUG_ON() | §2.2.4 |
| OS-BAN-003 | 内存分配用 sizeof(*p) | §2.2.4 |
| OS-BAN-004 | 禁止 strcpy/strncpy/strlcpy | §2.2.4 |
| OS-BAN-005 | 禁用 %p 默认输出 | §2.2.4 |
| OS-BAN-010 | 开源文档禁词 | §11.1 |
| OS-BAN-011 | 禁词违规处罚 | §11.3 |

### B.3 OS-STD 标准规则（本文档引用）

| 编号 | 规则 | 章节 |
|------|------|------|
| OS-STD-CODE-001 | 全局符号描述性命名 | §2.1.1 |
| OS-STD-002 | 局部变量短小切题 | §2.1.2 |
| OS-STD-003 | 常量宏全大写，优先 enum | §2.1.3 |
| OS-STD-004 | 返回值约定 | §2.2.3 |
| OS-STD-005 | AirymaxOS 专属前缀 | §2.1.5 |
| OS-STD-006 | 函数长度一屏可读 | §2.2.1 |
| OS-STD-007 | 函数原型元素固定顺序 | §2.2.2 |
| OS-STD-008 | kernel-doc 强制 | §2.3.1 |
| OS-STD-009 | 注释解释"为什么" | §2.3.2 |
| OS-STD-010 | 类型规范（u8/u16/u32/u64） | §2.5 |
| OS-STD-011 | bool 仅用于返回值与栈变量 | §2.5 |
| OS-STD-020 | 补丁格式规范 | §5.3.1 |
| OS-STD-021 | 稳定版维护规则 | §5.7 |
| OS-STD-040 | MAINTAINERS 文件规范 | §7.1 |
| OS-STD-041 | CODEOWNERS 自动审查分配 | §7.5 |
| OS-STD-050~052 | 检查脚本规范 | §8.6 |
| OS-STD-060 | 编码风格 7 维度对齐 | §12.3 |
| OS-STD-061 | 8 子仓目录结构设计原则 | §13.2 |
| OS-STD-062 | 7 子仓目录结构 | §13.4 |
| OS-STD-070 | syscall.xml 契约（R-01，已落地） | §14.1 |
| OS-STD-071 | structures.bf codegen（R-02） | §14.2 |
| OS-STD-072 | MAINTAINERS（R-03） | §14.2 |
| OS-STD-073 | 合规检查增补（R-04） | §14.2 |
| OS-STD-101 | checkpatch --strict 无 ERROR | §6.2 |
| OS-STD-DOC-100 | 文档-实现一致性义务 | §1.2 |
| OS-STD-DOC-110 | 编译产物管理规范 | §2.6 |
| OS-STD-DOC-120 | 文档-实现一致性检查（DS-*） | §8.5 |
| OS-STD-PROD-100 | commit 规范性 | §5.3.3 |
| OS-STD-PROD-110 | 版本库卫生规范 | §5.6 |
| OS-STD-PROD-120 | CI 完整性规范 | §6.6 |
| OS-STD-PROD-130 | 版本库卫生检查（VCS-*） | §8.4 |
| OS-STD-GOV-020 | 子模块分支治理 | §7.6 |
| OS-STD-140 | LAYER 双轨制 | §10.2 |

### B.4 OS-ACC / OS-KER / OS-TEST / OS-BUILD（本文档引用）

| 编号 | 规则 | 章节 |
|------|------|------|
| OS-ACC-001 | 覆盖率 >= 80%，关键路径 >= 90% | §6.4 |
| OS-KER-001 | goto 集中出口模式 | §2.2.4 |
| OS-KER-002 | 禁止 #if 桩函数模式 | §2.2.4 |
| OS-KER-003 | 条件编译必须用 IS_ENABLED() | §2.2.4 |
| OS-KER-229 | 编译期断言（文档-实现一致性审查点） | §1.2 |
| OS-TEST-001 | KUnit 回归规范 | §6.5 |
| OS-TEST-010 | formal-verification 三段式 | §12.9/§13.6 |
| OS-BUILD-010 | 三层构建系统 | §13.5 |
| OS-BUILD-020 | OBS 远程构建 | §10.8 |

---

## 附录 C 五维正交 24 原则映射

AirymaxOS 工程标准每一条规则都可以追溯到 Airymax 五维正交 24 原则。

| 五维 | 原则 | 编号 | 在本规范中的体现 |
|------|------|------|-----------------|
| 系统观 | 反馈闭环 | S-1 | 7 层自动化验证（§6.1）、CI 失败即反馈 |
| 系统观 | 层次分解 | S-2 | 4 层接口稳定性分级（§4.2）、8 子仓差异化要求（§1.5） |
| 系统观 | 总体设计部 | S-3 | 维护者层级制度（§5.2） |
| 系统观 | 涌现性管理 | S-4 | 渐进式开发模型（§4.4）、Merge Window + RC 周期 |
| 内核观 | 内核极简 | K-1 | 微内核化改造策略、corekern 4 原子机制 |
| 内核观 | 接口契约化 | K-2 | 双层稳定性哲学（§4.1）、[SC] 共享契约层（§9） |
| 内核观 | 服务隔离 | K-3 | 驱动用户态化、12 daemon 服务进程隔离 |
| 内核观 | 可插拔策略 | K-4 | sched_tac（SCHED_DEADLINE/SCHED_FIFO）、LSM 钩子（§4.3） |
| 认知观 | 双系统协同 | C-1 | 快慢路径分层（fastpath C-S9 / slowpath LSM） |
| 认知观 | 增量演化 | C-2 | 模块化开发流水线（§5.5）、补丁序列中点可编译 |
| 认知观 | 记忆卷载 | C-3 | MGLRU 多代 LRU、CXL/PMEM 分级 |
| 认知观 | 遗忘机制 | C-4 | 弃用接口清单、ABI 弃用流程 |
| 工程观 | 安全内生 | E-1 | 纯 C LSM（H5）、CBMC 形式化验证（§12.9） |
| 工程观 | 可观测性 | E-2 | ftrace + 7 层自动化验证、stc_stats 暴露（P1-2） |
| 工程观 | 资源确定性 | E-3 | 引用计数强制、内存分配惯用法（§2.2.4） |
| 工程观 | 跨平台一致性 | E-4 | 用户态跨 Linux/macOS/Windows |
| 工程观 | 命名语义化 | E-5 | 命名规范（§2.1）、敏感术语禁用（§2.1.4） |
| 工程观 | 错误可追溯 | E-6 | Fixes:/Closes:/Link: 标签 + DCO 链（§5.3.4） |
| 工程观 | 文档即代码 | E-7 | 文档-实现一致性义务（§1.2）、kernel-doc 强制 |
| 工程观 | 可测试性 | E-8 | KUnit + kselftest + 覆盖率门槛（§6.4/§6.5） |
| 设计美学 | 极简主义 | A-1 | 反过度抽象、函数长度约束（§2.2.1） |
| 设计美学 | 细节关注 | A-2 | 行尾禁止空白（§3.5）、AIRY_ALIGNED 宏（§2.1.6） |
| 设计美学 | 人文关怀 | A-3 | 敏感术语禁用（§2.1.4）、审查礼仪（§5.4） |
| 设计美学 | 完美主义 | A-4 | 7 层验证（§6.1）、VCS-*/DS-* 卫生检查（§8.4/§8.5） |

---

## 附录 D ES-OLK-1~13 工程思想映射

Linux 6.6 内核基线的 13 项工程思想（ES-OLK-1~13）在本规范中的完整映射：

| 编号 | 工程思想 | 核心内涵 | 规则映射 | 章节定位 |
|------|---------|---------|---------|---------|
| ES-OLK-1 | 关注点分离 | 每个顶层目录对应独立关注点 | OS-IRON-013、OS-STD-061 | §1.5、§13.2 |
| ES-OLK-2 | 架构正交 | arch/ 是唯一架构相关根目录 | OS-STD-061、OS-STD-062 | §13.2、§13.3 |
| ES-OLK-3 | UAPI 与内核内部 API 分离 | include/uapi/ 是用户空间 ABI 唯一来源 | OS-IRON-001/002 | §4.1、§13.3 |
| ES-OLK-4 | 特性可配置 | Kconfig 开关控制特性 | OS-BUILD-010 | §13.5 |
| ES-OLK-5 | 条件编译规范化 | IS_ENABLED() 替代 #ifdef | OS-KER-003 | §2.2.4 |
| ES-OLK-6 | UAPI 物理隔离 | uapi/ 目录物理隔离 | OS-IRON-001/014 | §4.1、§9.2 |
| ES-OLK-7 | 声明式配置 + 命令式构建分离 | Kconfig 声明 + Makefile 命令 | OS-BUILD-010 | §13.5 |
| ES-OLK-8 | 维护者制度文档化 | MAINTAINERS 文件 | OS-STD-040、OS-STD-072 | §7.1、§14.2 |
| ES-OLK-9 | 规范可执行 | checkpatch 机器检查 | OS-STD-101、OS-STD-050~052 | §6.2、§8.6 |
| ES-OLK-10 | regression 零容忍 | regression 必须当前周期修复 | OS-IRON-006 | §4.6 |
| ES-OLK-11 | 用户空间 ABI 永久稳定 | 接口导出后永久支持 | OS-IRON-001 | §4.1.1 |
| ES-OLK-12 | 运行时可加载 | EXPORT_SYMBOL + 模块机制 | OS-IRON-003 | §4.3 |
| ES-OLK-13 | 文档即代码 | Documentation/ 与代码同仓库 | OS-STD-DOC-100/120 | §1.2、§8.5 |

### 附录 D.1 Linux 6.6 品味哲学——8 项隐性工程智慧（OS-STD-STY-005~012）

| 编号 | 品味哲学 | Linux 6.6 源码证据 | 五维映射 |
|------|---------|-------------------|---------|
| OS-STD-STY-005 | 信任读者——暴露而非封装 | `kernel/locking/mutex.c` L60-73 owner 位编码 | A-1 |
| OS-STD-STY-006 | 短函数——一屏可读（≤80×24） | `kernel/locking/mutex.c` L845 | A-2/A-4 |
| OS-STD-STY-007 | 简洁文件头——SPDX 优先 | `kernel/locking/mutex.c` L1-20 | A-2 |
| OS-STD-STY-008 | EXPORT_SYMBOL 紧跟定义 | `kernel/locking/mutex.c` L46-58 | A-2 |
| OS-STD-STY-009 | include 语义分组——禁止字母序自动排序 | `kernel/locking/mutex.c` L21-35 | A-2 |
| OS-STD-STY-010 | `__` 前缀标注内部接口 | `kernel/locking/mutex.c` L80 `__mutex_owner` | A-2 |
| OS-STD-STY-011 | `__read_mostly` 缓存优化 | `kernel/sched/core.c` L168/178/7786 | E-3 |
| OS-STD-STY-012 | `__randomize_layout` 结构体布局随机化 | `include/linux/sched.h` L658 | E-1 |

> **权威定义**：开源手册 `01-coding-standards.md` §8.5（OS-STD-STY-005~012），SSoT 登记 `09-ssot-registry.md` §4.3。

---

## 附录 E ES-SEL4 工程思想借鉴映射（ES-SEL4-1~5 强制 + ES-SEL4-6~10 P2 增强）

seL4 的 10 项工程思想在 agent-linux 中的借鉴方式：

| 编号 | seL4 工程思想 | 核心内涵 | 借鉴方式 | 落地规则/子仓 | 章节定位 |
|------|-------------|---------|---------|-------------|---------|
| ES-SEL4-1 | 极简原则（Liedtke minimality） | 微内核只保留最小原语集 | 架构层强制 | corekern/ 4 原子机制 | §13.3 |
| ES-SEL4-2 | capability 单一权限模型 | 所有权限通过 capability 令牌 | 架构层强制 | security capability/ | §13.4 |
| ES-SEL4-3 | 服务用户态化 | 非必要服务运行在用户空间 | 架构层强制 | services userland-*/ | §13.4 |
| ES-SEL4-4 | 消息传递 IPC（含 fastpath） | 通信唯一机制是消息传递 | 架构层强制 | kernel io_uring/ + fastpath | §13.3 |
| ES-SEL4-5 | 形式化验证驱动 | 实现可被形式化证明 | 架构层强制 | tests-linux formal-verification/ | §12.9 |
| ES-SEL4-6 | 接口契约 XML 定义 | syscall.xml codegen | P2（R-01） | OS-STD-070 | §14.1 |
| ES-SEL4-7 | 架构正交分层 | arch/machine/plat 三层 | P2（已落地） | kernel arch/ | §13.3 |
| ES-SEL4-8 | 结构定义代码生成 | structures.bf codegen | P2（R-02） | OS-STD-071 | §14.2 |
| ES-SEL4-9 | 用户态 API 库独立 | libsel4 模型 | P2（已落地） | cloudnative SDK | §13.4 |
| ES-SEL4-10 | 现代构建系统 | Meson/CMake/Go/Cargo | P2（已落地） | services/cloudnative/cognition | §13.5 |

**借鉴边界声明**：架构层强制借鉴（ES-SEL4-1~5）5 项；P2 增强（ES-SEL4-6~10）5 项，其中 ES-SEL4-7/9/10 已落地、ES-SEL4-6 已落地（R-01）、ES-SEL4-8 待 M1（R-02）。

---

## 附录 F 双源融合裁决 16 维度

| # | 维度 | Linux 6.6 | seL4 | agent-linux 裁决 | 落地规则 |
|---|------|-----------|------|-------------------|---------|
| 1 | 缩进 | Tab 8 字符 | 空格 4 | **Linux 6.6** | OS-STD-FMT-001 |
| 2 | 命名 | snake_case | camelCase | **Linux 6.6** | OS-STD-CODE-001 |
| 3 | typedef | 最小（5 种例外） | 重度 | **Linux 6.6** | OS-STD-010 |
| 4 | 大括号 | K&R | K&R | **一致** | OS-STD-FMT-003 |
| 5 | 行宽 | 80 列 | ~100 | **Linux 6.6** | OS-STD-FMT-002 |
| 6 | 错误处理 | 负 errno + goto | exception_t 枚举 | **Linux 6.6** | OS-KER-001 |
| 7 | 注释 | kernel-doc 强制 | 普通 | **Linux 6.6** | OS-STD-008 |
| 8 | UAPI | include/uapi/ 物理隔离 | libsel4 独立 | **Linux 6.6 + 借鉴 libsel4** | OS-IRON-001/014 |
| 9 | 并发 | spinlock/rcu/seqlock | 无（内核非抢占） | **Linux 6.6** | OS-KER-001 |
| 10 | 内存 | kmalloc/kzalloc/vmalloc | 无动态分配 | **Linux 6.6** | OS-BAN-003 |
| 11 | 字符串拷贝 | strscpy（强制） | strncpy | **Linux 6.6** | OS-BAN-004 |
| 12 | 架构组织 | arch/ 单层 | arch/machine/plat 三层 | **融合（借鉴 seL4）** | OS-STD-061 |
| 13 | 接口契约 | 无统一 XML | syscall.xml codegen | **借鉴 seL4（P2，已落地）** | OS-STD-070 |
| 14 | bitfield | 手写位域 | structures.bf codegen | **借鉴 seL4（P2）** | OS-STD-071 |
| 15 | 形式化 | 无 | Isabelle/HOL | **借鉴 seL4** | OS-TEST-010 |
| 16 | capability + IPC | LSM + 多种 IPC | capability 单一模型 + fastpath | **融合** | OS-IRON-013/017 |

**裁决统计**：采纳 Linux 6.6 内核基线 11 维度（#1-#11）；借鉴 seL4（架构层）3 维度（#12/#15/#16）；借鉴 seL4（P2 增强）2 维度（#13/#14）。

---

## 附录 G v1.2 内核框架验证报告（历史基线）

> **章节定位**：v1.2 内核框架验证（2026-07-21）的历史记录，固化 M0 阶段"框架编译验证"成果。**注意**：本附录为历史基线快照，部分数据已被 v3.6 审查更新覆盖（如内核基线版本、airy 代码文件数、KUnit 测试数），当前状态以第 1/13 章及附录 A 为准。

### G.1 M0 框架编译验证结果（历史快照）

| 项目 | 值（历史） | v3.6 更新 |
|------|-----------|----------|
| 内核基线 | Linux 6.6.144 LTS（vanilla，commit da47cbc25466） | **6.6.147 纯主线**（审查 A 核验） |
| 架构 | x86_64 / arm64 | **+sw_64（367 文件导入）** |
| 编译结果 | x86_64 零错误零警告，39 个 Airymax .o | arm64 + airy 完整构建通过；x86 prepare 通过 |
| defconfig | `arch/x86/configs/airy_defconfig`（CONFIG_SECURITY=y 依赖修复） | 三架构 airy_defconfig |
| Airymax 代码 | 39 个 .o | **44 个 .c**（含 5 KUnit + 1 benchmark） |

### G.2 Kconfig 集成链路（5 层依赖链，当前有效）

```
顶层 Kconfig
  └── source "config/Kconfig.alk"
        └── menu "Airymax Kernel (ALK)"
              ├── config AIRY_SYSCALL    (depends on SECURITY_AIRY, default y)
              ├── config AIRY_COREKERN   (depends on SECURITY_AIRY, default y)
              ├── config AIRY_LOG        (depends on SECURITY_AIRY, default y)
              └── config AIRY_IPC        (depends on SECURITY_AIRY, default y)

security/Kconfig
  └── source "security/airy/Kconfig"
        └── config SECURITY_AIRY        (depends on SECURITY && IO_URING, default n)
              └── config AIRY_CAP_TABLE_SIZE (default 1024, range 64-4096)
```

### G.3 [SC] 头文件 H1-H6 硬约束验证（当前有效）

| 约束 | 验证标准 | 验证方法 | 状态 |
|------|---------|---------|------|
| H1 | 128B / magic 0x41524531 / badge offset 40-47 | `_Static_assert` + 头文件审查 | ✅ 通过 |
| H2 | badge 在 [SC] ipc.h，校验在 [SS] airy_lsm | 代码审查 + SSoT 校验 | ✅ 通过 |
| H3 | agentrt 用户态 badge=0 跳过 fastpath | 集成测试（agentrt 侧） | ✅ 通过 |
| H4 | sec_d 编译 Badge，fastpath C-S9 校验 | 单元测试 + 性能测试 | ✅ 通过（2-10ns 实测） |
| H5 | 纯 C LSM，不使用 BPF LSM | defconfig + 代码审查 | ✅ 通过 |
| H6 | [DSL] 降级 badge=0 跳过 C-S9 | 39 处 AIRY_SC_FALLBACK 块完整性 | ✅ 通过 |

### G.4 LSM 注册机制验证（当前有效）

`DEFINE_LSM(airy)` + `.order = LSM_ORDER_MUTABLE` + 5 个钩子注册（uring_cmd/task_alloc/task_free/task_kill/file_open）+ `security_add_hooks()` + `__ro_after_init` 标注。**v3.6 更新**：task_kill/file_open 的 Badge 校验已补齐（P1-4 已修复），安全入口对称性达成。

---

> **文档结束** | SPHARX Ltd 内部参考 | 闭源不公开 | v3.6（2026-08-01 三轮审查闭环重写）
