SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 19 — 工程思想论证总论：极境内核设计哲学 vs openEuler vs seL4（第三轮）

> **文档定位**：agent-linux 内核设计深度对比研究 · 第三轮 · 总论
> **对比基准**：openEuler kernel-OLK-6.6 · seL4-master · Airymax agent-linux（极境内核）
> **最后更新**：2026-08-01
> **方法论**：逐字节阅读三项目源码与工程文档，所有引用标注文件路径+行号，严禁编造
> **与前序关系**：第一轮（v3.6）核心机制对比、第二轮（v3.6b）基础设施对比，本轮（第三轮）聚焦**工程思想深层次论证**——极境内核设计哲学从何而来、论证是否自洽、与 openEuler/seL4 工程思想的对齐与偏差

---

## 0. 摘要

极境内核（agent-linux）的设计定位是"对 Linux 6.6 进行 seL4 思想借鉴的微内核化改造"（[README](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/README.md) L32-36）。本轮从工程思想层面论证该定位：对比 Linux（openEuler 载体）的"社区驱动 + 双层稳定性"工程思想、seL4 的"为可验证性而设计"工程思想、极境内核的"双源融合"工程思想。核心论证结论：极境内核的工程思想体系（16 条 OS-IRON 铁律）在哲学层面与 Linux 传统对齐良好、在工程标准层面与 openEuler KABI/UAPI 实践一致，但在**可验证性预留**层面与 seL4 存在实质差距——验证注解、编译期契约、验证配置锁存三类机制缺失。本报告确立第三轮论证坐标系，后续报告 20-22 分别展开设计方案论证、openEuler 工程标准研究、seL4 工程思想研究。

---

## 1. 三方工程思想对比基准

### 1.1 Linux/openEuler：社区驱动的双层稳定性

Linux 工程思想的三大支柱在 openEuler OLK-6.6 源码树中可逐字节核验：

**支柱 1：UAPI 永不破坏，内部 API 不承诺稳定。**

- [stable-api-nonsense.rst](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/Documentation/process/stable-api-nonsense.rst) L10-11：*"Linux does not have a binary kernel interface, nor does it have a stable kernel interface"*——内核**内部**接口。
- 同文档 L13-23：内核到用户空间的 syscall 接口 *"very stable over time, and will not break"*。
- 双层稳定性的边界（UAPI 稳定 / kABI 不承诺）是 Linux 工程契约的核心，openEuler 在此基础上**增加 KABI 预留机制**（[kabi.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/kabi.h) L365 `KABI_EXTEND`、L439 `KABI_RESERVE`、L443 `KABI_USE`），将"稳定性靠预留而非承诺"工程化。

**支柱 2：一个补丁一个逻辑变更，commit message 机器可解析。**

- [submitting-patches.rst](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/Documentation/process/submitting-patches.rst) L81：*"Solve only one problem per patch"*。
- L146-151：`Fixes:` 标签须 12 字符 hash、不拆行、豁免 75 列规则——承诺必须结构化，供脚本/stable 团队消费。

**支柱 3：工具固化标准，工程师判断优先。**

- [checkpatch.pl](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/scripts/checkpatch.pl) L21 版本 0.32，L30 `chk_signoff = 1` 强制 Signed-off-by 检查。
- [checkpatch.rst](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/Documentation/dev-tools/checkpatch.rst) L11-13：*"Checkpatch is not always right. Your judgement takes precedence."*

### 1.2 seL4：为可验证性而设计

seL4 工程思想与 Linux 根本对立，体现在四个机制：

**机制 1：验证范围诚实声明。**

- [CAVEATS.md](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/CAVEATS.md) L52-53：*"This proof covers the functional behaviour of the C code of the kernel. It does not cover machine code, compiler, linker, boot code, cache or TLB management."*
- L129-130：SMP *"currently without formal verification"*——宁可承认未验证，也不宣称已验证。

**机制 2：SSoT 单一来源，生成物禁止手改。**

- [invocation_header_gen.py](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/tools/invocation_header_gen.py) L30-34：新增 invocation 改 `libsel4/include/interfaces/sel4.xml`，不是改生成文件。
- [syscall_header_gen.py](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/tools/syscall_header_gen.py) L22-25：新增 syscall 改 `syscall.xml`。

**机制 3：编译期契约强制。**

- [assert.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/assert.h) L45-69：`compile_assert` 双模式宏（验证构建用 typedef 数组、正常构建用 `_Static_assert`）——为 C parser 兼容而设计。
- [faults.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/api/faults.c) L20-26：7 个 compile_assert 把内核内部枚举与 libsel4 用户态常量数值一致性在编译期钉死。

**机制 4：验证配置锁存。**

- `configs/` 目录 40+ 个 `*_verified.cmake`：证明在什么配置下成立是一等公民。
- [proof.yml](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/.github/workflows/proof.yml) L12-35：CRefine 证明进 CI，proof-test label 触发——证明与 PR 同步回归。

### 1.3 极境内核（agent-linux）：双源融合

极境内核工程思想体系的核心文档是 [04-engineering-philosophy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/04-engineering-philosophy.md)，其三大支柱（L73-83）：

| 支柱 | 来源 | 在本项目中的体现 |
|------|------|------------------|
| Linux 6.6 内核基线工程思想 | Linux 6.6 源码深度研究 | 双层稳定性、渐进式开发、regression 不可接受、审查优先、不破坏用户空间 |
| Airymax 五维正交 24 原则 | `00-architectural-principles.md` | 每条工程思想映射到至少一条五维原则 |
| agentrt 17 类规则编号体系 | agentrt 工程标准 v29.0 | 核心铁律赋予 OS-IRON / OS-KER 编号 |

**关键论证点**：极境内核的工程思想明确承认"Linux 为基、seL4 为鉴"（OS-IRON-010，L628），且编码为 16 条 OS-IRON 铁律（SSoT [09-ssot-registry.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/09-ssot-registry.md) §2）。这一定位意味着：

- **对齐 Linux 的部分**（UAPI 永不破坏 OS-IRON-001、内部 API 不保证稳定 OS-IRON-002）已通过 [04-engineering-philosophy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/04-engineering-philosophy.md) L102-128 充分论证，与 openEuler/Linux 传统完全一致。
- **借鉴 seL4 的部分**（capability 单一模型、SSoT、形式化验证预留）在架构文档 [03-microkernel-strategy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) L65-107 有详细映射，但**工程标准层面对 seL4 的落地存在三类缺口**（详见 §3）。

---

## 2. 工程思想论证：极境内核设计哲学的七个自洽性检查

### 2.1 检查 1：双层稳定性哲学 vs Linux 传统——自洽

极境内核将 Linux 双层稳定性扩展为 4 层接口稳定性分级（[04-engineering-philosophy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/04-engineering-philosophy.md) L130-161）：

| 层级 | 接口类型 | 稳定性承诺 |
|------|----------|-----------|
| L1 | Agent 应用 API（SDK + syscall + UAPI） | 极稳定（类 Linux syscall） |
| L2 | 智能体运行时接口（AgentsIPC 协议、MicroCoreRT 契约） | 中等稳定（版本化演进） |
| L3 | 内核子系统接口（内核内部 API） | 可重构（you broke it, you fix it） |
| L4 | 内部实现细节（私有函数、static） | 完全自由 |

**论证结论**：自洽。L1 对应 Linux UAPI 稳定承诺，L3 对应 Linux 内部 API 不承诺，L2/L4 是极境内核针对 Agent 运行时的新增细分。UAPI 编译器无关原则（OS-IRON-016，[04-engineering-philosophy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/04-engineering-philosophy.md) L165-203）进一步强化了 L1——UAPI 头文件坚持 C11 标准、禁止编译器扩展（唯一例外 `AIRY_ALIGNED` 宏定义于 [uapi_compat.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/uapi_compat.h) L71-85）。此设计借鉴 seL4 的编译器无关理念（[assert.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/assert.h) L45-51 注释），但落地方式（三路类型桥 + AIRY_ALIGNED 宏）比 seL4 更实用。

### 2.2 检查 2：策略与机制分离——自洽但有边界模糊

极境内核继承"机制留内核、策略外移"（OS-IRON-003，[04-engineering-philosophy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/04-engineering-philosophy.md) L208-252）。sched_tac 是其极端范式：整个 CPU 调度策略可在用户空间定义（L232-234）。

**论证结论**：哲学自洽，但存在一个边界模糊点。极境内核的 [stc_dispatch.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/corekern/sched/stc_dispatch.c) L13-16 实际执行 `sched_setattr()` 将策略映射到 SCHED_DEADLINE/SCHED_FIFO/SCHED_NORMAL——这仍是**内核调度机制**，策略选择（DEADLINE vs EEVDF）发生在内核态函数内（L50-70 `stc_policy_to_linux`）。"用户态调度器"实际是用户态通过 `AIRY_SYS_SCHED_CTL`（syscall 550）间接影响内核态映射，并非完整的用户态调度器。这与 seL4 的"内核零策略"（所有调度决策在 user-level）仍有距离，需要文档明确"内核态策略映射函数是机制还是策略"。

### 2.3 检查 3：Capability 单一模型 vs seL4——模型对齐但实现路径不同

seL4 的核心设计决策是 capability 单一安全模型（[03-microkernel-strategy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) L65-66）。极境内核的落地是 [airy_lsm.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_lsm.c) 的纯 C LSM + `agent_caps[]` 静态数组 + 64-bit Badge folding（[ipc.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/ipc.h) L51-64：Epoch<<48 | RandomTag<<16 | Perms）。

**论证结论**：模型对齐（不可伪造、最小权限、递归撤销、IPC 传递、审计追踪），但实现路径不同——seL4 用 CNode 树形寻址 + MDB 派生树（[cspace.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/cspace.c) L126-192 `resolveAddressBits`），极境内核用固定 1024 槽数组 + per-bucket 锁（[airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap.h) L52-56）。固定数组在 1024 上限内更简单高效（fastpath badge 校验 ~10ns），但牺牲了 seL4 CNode 的无限扩展性与树形隔离。这是"在 Linux 6.6 内嵌 capability"约束下的合理权衡，但需在 known-caveats 中明确 1024 上限的扩展边界。

### 2.4 检查 4：Liedtke 极简原则的适用性——需要语境化

[03-microkernel-strategy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) L37-41 引用 Liedtke 原则：*"A concept is tolerated inside the microkernel only if moving it outside the kernel would prevent the implementation of the system's required functionality."* 并量化 seL4 内核核心 ~1.44 万行 C（L43）。

**论证结论**：极境内核的诠释（L55-61）是"5-10 万行预算 + 每新增子系统需论证无法在用户态安全实现"。这个预算本身是务实的（Linux 6.6 改造无法降到 1.44 万行），但**论证义务的落地机制缺失**——文档要求"每新增子系统需论证"，却没有对应的 review gate 或登记表来强制该论证。建议在 09-ssot-registry.md 增加"新增内核子系统论证登记"规则。

### 2.5 检查 5：形式化验证预留——最薄弱的环节

[03-microkernel-strategy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) L99-107 预留了 seL4 的验证注解机制（MODIFIES/FNSPEC/GHOSTUPD/DONT_TRANSLATE），[09-known-caveats.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/09-known-caveats.md) L39-42 规划了验证路径（IPC Fastpath 不变量、Rust Kani、编译期断言）。

**论证结论**：**文档承诺与实现现状存在显著差距**：

1. **验证注解未落地**：grep 全部 airy_*.c 与 corekern/*.c，无一处 `/** MODIFIES */`、`/** FNSPEC */` 等验证注解（seL4 在 [util.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/util.h) L93/L137-140/L189-196/L306 有完整实例）。文档宣称"1.0.1 阶段引入"（[03-microkernel-strategy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) L103-104），但源码零落地。
2. **编译期契约缺失**：grep `BUILD_BUG_ON`/`static_assert`/`_Static_assert` 于全部 airy_*.c、corekern/*.c、log/*.c——**零命中**。seL4 用 compile_assert 在编译期钉死内核-用户态常量一致性（[faults.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/api/faults.c) L20-26），极境内核的 [uapi_compat.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/uapi_compat.h) 与 [syscalls.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/syscalls.h) L8-12 声称"三方一致性（ABI 铁律）"，但一致性靠 CI 脚本而非编译期断言保障。seL4 模式的 `AIRY_COMPILE_ASSERT` 宏（在 [SC] 头文件里定义，UAPI 侧用 C11 `_Static_assert`、内核侧用 typedef 数组）应作为 P1 项落地。
3. **验证配置锁存缺失**：seL4 用 `configs/*_verified.cmake` 锁存"证明在什么配置下成立"。极境内核无等价物——即使未来实现验证，也无机制防止配置漂移使证明失效。

### 2.6 检查 6：诚实声明传统——已借鉴但可深化

[09-known-caveats.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/09-known-caveats.md) L5-11 明确参照 seL4 CAVEATS.md 建立已知限制集中登记。L48-59 声明验证不覆盖范围（机器码/链接器/boot/缓存/TLB/固件）。

**论证结论**：诚实声明传统已建立，是正面亮点。但 seL4 的 CAVEATS.md 更进一步——逐架构标注验证矩阵（AArch32 全属性/AArch64 仅完整性/RISC-V 部分/x86 未验证，[03-microkernel-strategy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) L90-97）。极境内核的 [09-known-caveats.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/09-known-caveats.md) L65-72 有架构验证矩阵（x86_64 编译验证 + KUnit/arm64 编译验证/riscv64 设计级），但**未标注 SMP 验证状态**——seL4 明确声明 SMP 未验证（CAVEATS.md L129-130），极境内核的 SMP 语义（多核 lock-free ring、per-bucket 锁）应在 known-caveats 中明确标注验证覆盖。

### 2.7 检查 7：UAPI 稳定性 vs KABI 预留——可借鉴 openEuler

极境内核的 syscall 编号设计（[syscalls.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/syscalls.h) L20-29：4 核心 548-551 + 20 预留 552-571）体现了 openEuler KABI 预留思想（预留槽位 → 事后 KABI_USE 消费）。第一轮 P0-1 已指出 syscall_64.tbl 未显式登记 552-571 预留槽。

**论证结论**：预留思想正确，与 openEuler [kabi.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/kabi.h) L439 `KABI_RESERVE`/L443 `KABI_USE` 同构。但 openEuler 的 KABI 体系有三层防护（宏双面展开 + genksyms 隐藏 + 编译期 size/align 断言，[kabi.h](file:///home/spharx/SpharxWorks/.engineer-reference/kernel-OLK-6.6/include/linux/kabi.h) L380-390），极境内核的 24 槽 syscall 预留目前只有"编号规划"一层。建议在 syscall 层引入"登记 + 编译期断言 + CI 三方一致性"三层防护。

---

## 3. 工程思想对比表：三类机制的对齐与缺口

| 机制 | openEuler/Linux | seL4 | 极境内核 | 对齐状态 |
|------|----------------|------|----------|---------|
| UAPI 稳定性 | syscall 永不破坏 + KABI 预留 | libsel4 独立 + syscall.xml | OS-IRON-001 + 4 层分级 + 24 槽预留 | ✅ 对齐 Linux，预留同构 openEuler |
| 内部 API 策略 | 不承诺稳定，you break you fix | 内核极简，无内部 API 负担 | OS-IRON-002 + L3/L4 分级 | ✅ 对齐 Linux |
| 代码风格 | checkpatch + coding-style.rst | 注释即规范（无独立文档） | Linux 风格采纳（[03-microkernel-strategy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) L502-512） | ✅ 明确决策 |
| 提交规范 | submitting-patches.rst 全流程 | TSC + DCO | OS-KER-067/068（Fixes/DCO） | ✅ 对齐 Linux |
| 治理 | MAINTAINERS + get_maintainer | TSC 集中 + proof-test 门禁 | MAINTAINERS + 工程规范委员会 | ✅ 对齐 Linux |
| SSoT 单一来源 | 无（头文件手写） | XML/.bf codegen | [SC] 10 头文件 + CI 双向校验 | ⚠️ 部分对齐（有契约层，无 codegen） |
| 编译期契约 | BUILD_BUG_ON 零散 | compile_assert 系统化 | **零命中** | ❌ 缺口（P1） |
| 验证注解 | 无 | MODIFIES/FNSPEC/GHOSTUPD | **零落地** | ❌ 缺口（P2） |
| 验证配置锁存 | 无 | configs/*_verified.cmake | **无等价物** | ❌ 缺口（P2） |
| 诚实声明 | 无等价文档 | CAVEATS.md | known-caveats.md | ✅ 已借鉴（可深化 SMP 标注） |

---

## 4. 改进点清单（第三轮新增视角）

> 注意：本节改进点与前两轮（v3.6 的 P0-1、P1-x；v3.6b 的 N1-N22）编号独立，属第三轮工程思想视角，编号 E1 起。

| 编号 | 标题 | 优先级 | 现状位置 | 参考 | 工作量 |
|------|------|--------|----------|------|--------|
| E1 | [SC] 头文件引入 AIRY_COMPILE_ASSERT 编译期契约宏（内核-用户态常量一致性编译期钉死） | P1 | [uapi_compat.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/uapi_compat.h)、[syscalls.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/syscalls.h) L8-12 | seL4 [assert.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/assert.h) L45-69、[faults.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/api/faults.c) L20-26 | 4h |
| E2 | 验证注解机制落地：为 capability fastpath 与 IPC fastpath 添加 MODIFIES/FNSPEC 注释标注 | P2 | [airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap.h) L75-90、[airy_ipc_fastpath.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/corekern/ipc/airy_ipc_fastpath.c) | seL4 [util.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/util.h) L93/L189-196 | 8h |
| E3 | 验证配置锁存：新增 airymax_verified.cmake 风格配置声明（验证适用的平台/配置/特性组合） | P2 | 新增 [09-known-caveats.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/09-known-caveats.md) 附录 | seL4 `configs/*_verified.cmake`（40+ 文件） | 2h |
| E4 | known-caveats 增加 SMP 验证覆盖标注（多核 lock-free ring、per-bucket 锁） | P1 | [09-known-caveats.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/09-known-caveats.md) L65-72 | seL4 [CAVEATS.md](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/CAVEATS.md) L127-155 | 1h(文档) |
| E5 | Liedtke 论证义务落地：新增"新增内核子系统论证登记"规则（无法在用户态安全实现的论证 gate） | P2 | [09-ssot-registry.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/50-engineering-standards/09-ssot-registry.md) | Linux 无等价物；seL4 极简天然满足 | 2h(文档) |
| E6 | sched_tac 机制/策略边界文档化：明确 stc_policy_to_linux 映射是机制还是策略 | P1 | [stc_dispatch.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/corekern/sched/stc_dispatch.c) L50-70 | seL4 内核零策略 | 1h(文档) |

---

## 4. 小结

极境内核的工程思想定位"Linux 为基、seL4 为鉴"（OS-IRON-010）在哲学层面自洽：双层稳定性、策略与机制分离、capability 模型、诚实声明均与参考项目对齐。七个自洽性检查中，五个通过（2.1/2.2/2.3/2.6/2.7），两个暴露缺口（2.4 论证义务缺失、2.5 可验证性预留差距最大）。核心论证结论：**极境内核的工程思想体系在"工程标准"层面对齐 Linux/openEuler 优秀，但在"可验证性预留"层面对齐 seL4 不足**——编译期契约（E1）、验证注解（E2）、验证配置锁存（E3）三类机制缺失，是第三轮最值得优先补齐的工程思想差距。E1 与 E4 建议在 M2 前收敛，E2/E3 建议 M3-M5 落地。

> 后续报告：[20 设计方案深层次论证](20-design-argumentation-v3.6c.md) · [21 openEuler 工程标准研究](21-openEuler-engineering-standards-v3.6c.md) · [22 seL4 工程思想研究](22-seL4-engineering-thought-v3.6c.md) · 23 第三轮改进建议与闭环（该报告已于 v3.6c 归档清理中移除，结论并入 [08 闭环总结](08-closure-summary-v3.6.md)）
