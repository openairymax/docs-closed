SPDX-License-Identifier: GPL-2.0-only
Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 22 — seL4 工程标准与工程思想研究（第三轮）

> **文档定位**：agent-linux 内核设计深度对比研究 · 第三轮 · seL4 工程思想研究
> **研究主体**：seL4-master（`/home/spharx/SpharxWorks/.engineer-reference/seL4-master`）
> **最后更新**：2026-08-01
> **方法论**：逐字节阅读源码与工程文档，所有引用标注文件路径+行号，严禁编造
> **研究目的**：提炼 seL4（唯一通过完整形式化验证的 OS 内核）的工程标准与工程思想，为极境内核"seL4 为鉴"（OS-IRON-010/012）提供深度参照

---

## 0. 摘要

seL4 工程体系的核心特征是"**为可验证性而设计**"——SSoT 代码生成、验证注解内嵌源码、编译期断言双模式、验证配置锁存、验证范围诚实声明，构成与 Linux"社区驱动 + 运行测试"完全不同的工程范式。核心研究结论：seL4 的工程思想对极境内核最具借鉴价值的三个机制是 (1) **compile_assert 双模式宏**（内核-用户态常量一致性编译期钉死）、(2) **验证注解内嵌源码**（MODIFIES/FNSPEC/GHOSTUPD/DONT_TRANSLATE）、(3) **验证配置锁存 + CAVEATS 诚实声明**。三者构成极境内核"可验证性预留"（报告 19 E2/E3）的直接模板。

---

## 1. 形式化验证工程思想

### 1.1 验证范围诚实声明（CAVEATS.md）

[CAVEATS.md](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/CAVEATS.md)（258 行）是 seL4 工程诚实性的核心文档：

| 声明 | 行号 | 内容 |
|------|------|------|
| 证明覆盖范围 | L52-55 | *"This proof covers the functional behaviour of the C code of the kernel. It does not cover machine code, compiler, linker, boot code, cache or TLB management."* |
| AArch32 | L57-59 | 全属性验证（功能正确性）+ 无标准 C 缺陷（buffer overrun/NULL 解引用） |
| AArch32/RISC-V 额外 | L61-68 | integrity/confidentiality/intransitive non-interference |
| AArch64 | L74-80 | 仅 integrity；confidentiality/non-interference "are in progress" |
| Verified Configurations | L85-97 | *"The proofs are generally sensitive to changes in configuration parameters, and will break if these are changed."* |
| Real Time | L99-105 | 默认配置有少量不可抢占长内核操作 |
| MCS | L107-126 | 正式验证 "currently still in progress" |
| SMP | L127-155 | *"currently without formal verification"*（L129-130）；*"standard C implementation defects are possible and not excluded"*（L154-155） |
| 静态多内核过渡 | L157-171 | static multi-kernel 更接近顺序证明模型 |
| 地址空间复用 | L173-190 | 承认 capability 残留权威（cache maintenance/unmap） |
| x86 信息流 | L222-239 | timing channel 漏洞；Meltdown/Spectre 有缓解，Zenbleed/Inception 无 |

**工程思想金句 1**：验证范围诚实声明——宁可承认未验证（SMP/MCS/x86 时序通道），也不宣称已验证。**"未验证配置不享有已验证配置的缺陷排除保证"**（L154-155 反证）是 seL4 工程诚信的极致体现。

### 1.2 验证注解内嵌源码

验证注解以注释形式与源码共生，被 C parser/Isabelle 消费：

| 注解 | 位置 | 内容 |
|------|------|------|
| `/** MODIFIES: */` | [util.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/util.h) L93 | 标注函数副作用范围 |
| `/** FNSPEC StrictC'__unreachable_spec */` | util.h L94-96 | HOL 规范 |
| `MODIFIES + FNSPEC halt_spec` | util.h L137-140 | halt() 函数规范 |
| `MODIFIES + DONT_TRANSLATE + FNSPEC clzl_spec` | util.h L189-196 | 编译器内建不可验证，DONT_TRANSLATE 隐藏函数体、FNSPEC 公理化行为 |
| `clzll/ctzl/ctzll_spec` | util.h L214-243 | 内建函数公理化 |
| `/** DONT_TRANSLATE */` | util.h L306 | popcountl |
| `/** GHOSTUPD: "(\<acute>levelBits > 0, id)" */` | [cspace.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/cspace.c) L181 | resolveAddressBits 循环 ghost state 更新 |
| `/** DONT_TRANSLATE */` | [c_traps.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/arch/arm/64/c_traps.c) L18 | restore_user_context（汇编恢复用户上下文） |

**工程思想金句 2**：验证不是外部附加物，而是与源码共存的"文档化契约"。编译器内建（clzl 等）用 DONT_TRANSLATE 对证明隐藏、用 FNSPEC 公理化——"证明对象与不可验证物隔离"的工程手法。

### 1.3 验证配置锁存

- `configs/`：40+ 个 `*_verified.cmake`（如 `configs/AARCH64_tx1_verified.cmake`）——"哪个平台、什么配置下证明成立"锁存为文件。
- [proof.yml](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/.github/workflows/proof.yml) L12-35：CRefine/SimplExportAndRefine 进 CI，用 `proof-test` label 触发（L17-20）——证明与 PR 同步回归。
- 其他 CI：`cparser.yml`（C parser 兼容）、`xml_lint.yml`（XML SSoT 合法性）、`sel4test-sim.yml`/`sel4test-deploy.yml`（功能测试）。

**工程思想金句 3**：配置漂移即证明失效——"证明在什么配置下成立"是一等公民，验证配置锁存使证明可复现、可回归。

---

## 2. 代码生成工程（SSoT）

### 2.1 SSoT 工具链

[tools/](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/tools/) 实际工具（11 个 py）：`umm.py`/`condition.py`/`bitfield_gen.py`/`circular_includes.py`/`invocation_header_gen.py`/`syscall_header_gen.py`/`lex.py`/`hardware_gen.py`/`reciprocal.py`/`invocation_json_gen.py`/`config_gen.py`。

[CMakeLists.txt](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/CMakeLists.txt) L32-40 将全部 codegen 工具登记为构建依赖（`RequireTool(CPP_GEN_PATH cpp_gen.sh)` 等 9 个）。

### 2.2 SSoT 铁证（生成物禁止手改）

| SSoT 源 | 生成物自述 | 行号 |
|---------|-----------|------|
| `libsel4/include/interfaces/sel4.xml` | [invocation_header_gen.py](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/tools/invocation_header_gen.py) L30-34：*"To add an invocation call number, edit libsel4/include/interfaces/sel4.xml."* | 新增 invocation 改 XML 不是改生成文件 |
| `libsel4/include/api/syscall.xml` | [syscall_header_gen.py](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/tools/syscall_header_gen.py) L22-25：*"To add a system call number, edit kernel/libsel4/include/api/syscall.xml"* | 新增 syscall 改 XML |
| 25 个 `.bf` 文件 | [bitfield_gen.py](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/tools/bitfield_gen.py) L9-14：生成 C + Isabelle/HOL 规范 + 正确性证明；L36：*"The C standard leaves C bitfields too underspecified"*——.bf 语言存在的理由 | 位布局改 .bf |
| syscall SSoT 链 | [syscall.xml](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/libsel4/include/api/syscall.xml) L9-37：api-master（8 个 syscall）/api-mcs（11 个） | syscall 编号单一来源，配 syscall.xsd schema |

**工程思想金句 4**：SSoT 单一来源，生成物禁止手改——接口改 XML、syscall 改 syscall.xml、位布局改 .bf；C 代码与 Isabelle 证明均由 bitfield_gen.py 生成且自带无 UB 证明（[bitfield_gen.md](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/tools/bitfield_gen.md) L10-31）。

**与极境内核的对比**：极境内核的 [SC] 10 头文件是"单一物理宿主 + CI 双向校验"（OS-IRON-008/014），但**无 codegen**——[SC] 头文件手写，一致性靠 CI 脚本而非代码生成。第一轮 R-01/R-02 曾建议引入 syscall.xml 式契约 + structures.bf 式 bitfield codegen（[03-microkernel-strategy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) L340-379），但未落地。seL4 的 SSoT 是"改动单一来源 → 生成双端代码"，极境内核是"维护单一宿主 → CI 比对双端"，后者更轻但存在人为编辑漂移风险。

---

## 3. 编译期断言工程

### 3.1 compile_assert 双模式宏

[assert.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/assert.h) L45-69：

```c
#ifdef CONFIG_VERIFICATION_BUILD
#define compile_assert(name, expr) \
        typedef int __assert_failed_##name[(expr) ? 1 : -1] UNUSED;   /* L63-64 */
#define unverified_compile_assert(name, expr)
#else
#define compile_assert(name, expr) _Static_assert(expr, #name);        /* L67 */
#define unverified_compile_assert(name, expr) compile_assert(name, expr)
#endif
```

设计缘由（L45-61 注释）：(1) 内核内部不依赖用户态头文件；(2) `_Static_assert` 是 c11 特性而内核用 c99；(3) **C parser 不理解 `_Static_assert`，验证构建必须退回 typedef 数组技巧**。

### 3.2 使用实例

- [faults.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/api/faults.c) L20-26：7 个 compile_assert——内核内部枚举与 libsel4 用户态常量的数值一致性编译期强制（L19 注释 "consistency with libsel4"）。
- [boot.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/boot.c) L273-276：`compile_assert(root_cnode_size_valid, ...)`；L294-297：`num_domains_valid`/`num_priorities_valid`——配置约束编译期校验。

**工程思想金句 5**：一个宏两套实现服务两套工具链（gcc/clang 与 C parser）——"验证工具链友好"的定制断言。内核-用户态接口契约的一致性不是靠约定，而是靠编译期钉死。

**与极境内核的对比**：极境内核 grep `BUILD_BUG_ON`/`static_assert` 于全部 airy 代码**零命中**（报告 19 E1 已指出）。seL4 用 compile_assert 在编译期钉死内核-用户态常量一致性（[faults.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/api/faults.c) L20-26），极境内核的 [SC] 一致性（[syscalls.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/syscalls.h) L8-12 三方一致声明）靠 CI 脚本。**建议在 [SC] uapi_compat.h 定义 AIRY_COMPILE_ASSERT 双模式宏**（内核侧 typedef 数组/用户态侧 C11 _Static_assert），为 magic/枚举/常量一致性提供编译期强制。

---

## 4. 错误处理工程

### 4.1 decode/invoke 分离 + 结构化错误码

- [failures.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/api/failures.h) L16-23：`enum exception { EXCEPTION_NONE, EXCEPTION_FAULT, EXCEPTION_LOOKUP_FAULT, EXCEPTION_SYSCALL_ERROR, EXCEPTION_PREEMPTED }`——一个 word 承载五种控制流结果。
- L27-37：`struct syscall_error`（invalidArgumentNumber/invalidCapNumber/rangeErrorMin/Max/memoryLeft/failedLookupWasSource/type）——**结构化错误码**，携带参数序号支持用户态精确重试。
- L12-13 注释：*"These datatypes differ markedly from haskell"*——承认 C 实现与 Haskell 原型（l4v）的差异映射。

### 4.2 decode 返回 syscall_error_t 模式

[tcb.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/tcb.c)（grep 核实 50 处错误赋值）：

- `checkPrio` L32：L43-45 `current_syscall_error.type = seL4_RangeError; ...rangeErrorMin/Max = mcp`。
- `decodeSetAffinity` L497：L504 TruncatedMessage、L513 IllegalOperation。
- `decodeSetBreakpoint` L586：L607-668 连续 `seL4_InvalidArgument + invalidArgumentNumber = N`——**错误精确到第几个参数**。

**工程思想金句 6**：decode（校验 + 翻译成错误码）与 invoke（执行）分离，错误精确到参数序号——错误处理本身可证明、可测试。

**与极境内核的对比**：极境内核采用 Linux 的 errno + goto 风格（[03-microkernel-strategy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) L511），错误码统一为 `AIRY_E*`（[SC] error.h，A-UEF 模块）。两者是"结构化错误码 + 参数序号" vs "errno + 上下文"的取舍——极境内核的 [A-UEF] 统一错误码方向正确，但缺少 seL4 的"错误精确到参数序号"能力（如 capability 校验失败时返回具体是第几个参数/哪个权限位）。可在 airy_cap_badge_ok 的错误码上补充细分（[airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap.h) L75-90 已有 -AIRY_ECAP_EPOCH/-AIRY_ECAP_MISSING 等细分，方向已对齐）。

---

## 5. 最小化 TCB 工程思想（Liedtke minimality）

### 5.1 内核核心规模

- [src/object/](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/)：11 个文件（cnode/endpoint/notification/tcb/untyped/reply/schedcontext/schedcontrol/interrupt/domain/objecttype）。
- [src/kernel/](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/)：6 个文件（thread/cspace/boot/faulthandler/stack/sporadic）。
- 架构无关内核核心 = src/object(11) + src/kernel(6) + src/api(2) + src/model(3) + src/smp(2) + src/fastpath(1) + 顶层(4) = **29 个 C 文件**。
- 对象类型头文件 13 个（include/object/）。

### 5.2 cap 是唯一安全模型

[cap.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/object/cap.h) + `structures_64.bf` L7-43（capType 5 bits 判别）——内核只提供 12 种对象的 capability 操作，安全属性（integrity/confidentiality）全部建立在这一模型上（CAVEATS L61-68）。

**工程思想金句 7**：最小化 TCB（Liedtke minimality）——小到可以被证明。架构无关内核核心仅 29 个 C 文件、12 种对象、单一 big kernel lock（[lock.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/smp/lock.h) L50 `big_kernel_lock`，CLH FIFO 锁 L22-48，cache-line 对齐防伪共享 L30/L38）。

**与极境内核的对比**：极境内核 4,600+ 行 airy 专属代码（第二轮统计）远大于 seL4 内核核心，但这是"Linux 6.6 改造"与"从零微内核"的本质差异——极境内核的目标不是"小到可证明"，而是"在 Linux 6.6 上叠加可审计的 Agent 运行时"。Liedtke 原则的适用边界已在报告 19 检查 4 论证（需论证义务 gate）。

---

## 6. CNode capability 工程

### 6.1 7+ 种 CNode 操作

[cnode.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/cnode.c)（约 840 行）：

| 操作 | decode 行号 | invoke 行号 |
|------|-------------|-------------|
| CNodeCopy | L116 | — |
| CNodeMint | L136 | — |
| CNodeMove | L157 | invokeCNodeMove L343 |
| CNodeMutate | L163 | — |
| CNodeRevoke | L195 | invokeCNodeRevoke L315 |
| CNodeDelete | L200 | invokeCNodeDelete L320 |
| CNodeSaveCaller | L206 | invokeCNodeSaveCaller L364 |
| CNodeCancelBadgedSends | L218 | invokeCNodeCancelBadgedSends L325 |
| CNodeRotate | L232 | invokeCNodeRotate L350 |

核心原语收敛：`cteInsert` L410、`cteMove` L445、`capSwapForDelete` L475、`cteSwap` L489、`cteRevoke` L528、`cteDelete` L552、`cteDeleteOne` L726、`insertNewCap` L745、`ensureEmptySlot` L836——**每个原语对应抽象规范中一个操作**（可验证性：原语即证明单元）。

### 6.2 CNode 树形寻址

[cspace.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/cspace.c) `resolveAddressBits` L126-192：L142 起循环取 radixBits/guardBits/levelBits（L143-145），guard 匹配（L157-162）、深度检查（L164-169）、`offset = (capptr >> ...) & MASK(radixBits)`（L171-172）、沿 CNode 指针链下钻（L183-191）。

**与极境内核的对比**：极境内核用固定 1024 槽数组 + per-bucket 锁（[airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap.h) L52-56），seL4 用 CNode 树形寻址。固定数组在 1024 上限内 fastpath 更快（O(1) badge 校验 vs 树形逐级），但无无限扩展与树形隔离（报告 20 检查 3 已论证为合理权衡）。

---

## 7. SMP/并发工程

### 7.1 CLH 队列锁（big kernel lock）

[lock.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/smp/lock.h)：

- L19-21：CLH lock = "FIFO lock for machines with coherent caches"（1993 年论文）。
- L22-48：`clh_req_state_t`/`clh_req_t`/`clh_node_t`/`clh_lock_t`（全部 `ALIGN(L1_CACHE_LINE_SIZE)` L30/L38——cache-line 对齐防伪共享）。
- L50：`extern clh_lock_t big_kernel_lock`——**单一全局大内核锁**（比细粒度锁更接近顺序证明模型）。
- L59-87 `clh_lock_acquire`（`__atomic_exchange_n` 入队 L67）；L89-100 `clh_lock_release`。
- L107-137：`NODE_LOCK(_irqPath)`/`NODE_UNLOCK`/`NODE_LOCK_IF`/`NODE_UNLOCK_IF_HELD` 宏；非 SMP 时全部为空宏（L127-132，单核零开销）。

### 7.2 NODE_STATE 宏

[statedata.h](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/include/model/statedata.h) L123-125：`#define NODE_STATE(_state) NODE_STATE_ON_CORE(_state, getCurrentCPUIndex())`；per-core 状态成员 L58-92（ksReadyQueues/ksCurThread/ksIdleThread/ksSchedulerAction/MCS ksConsumed 等）。

**工程思想金句 8**：SMP 明确"未验证"（CAVEATS L129-130），单一 big kernel lock 是"为可验证性牺牲细粒度并发"的工程决策——正确性优先于可扩展性。

**与极境内核的对比**：极境内核使用 Linux 原生锁 + per-bucket 锁（[airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap.h) L52-56）+ lock-free ring（第二轮正面发现），并发模型远复杂于 seL4 的 big kernel lock。这使极境内核在并发性能上领先，但可验证性复杂度也相应更高——需要在 known-caveats 明确 SMP 验证覆盖（报告 19 E4）。

---

## 8. Boot 工程（capability 传递）

[boot.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/kernel/boot.c)：

- `create_root_cnode` L278-291：L281-285 创建 root CNode cap，L288 `write_slot(SLOT_PTR(rootserver.cnode, seL4_CapInitThreadCNode), cap)`——root CNode 自引用起始。
- `populate_bi_frame` L350-372：填充 `seL4_BootInfo`（nodeID/numNodes/ipcBuffer/initThreadCNodeSizeBits），L371 `slot_pos_cur = seL4_NumInitialCaps`。
- `provide_cap` L374-385：从 slot_pos_cur 起顺序写入初始 caps。
- `create_initial_thread` L496-564：L513 注释 *"initialise TCB (corresponds directly to abstract specification)"*；L514-528 三次 `cteInsert` 把 root CNode/VSpace/IPC buffer caps 装入 TCB 的 tcbCTable/tcbVTable/tcbBuffer。
- `create_untypeds` L790。

**工程思想金句 9**：boot 是"用 capability 操作构造 capability 世界"的过程——与 Linux boot 的"直接操作物理内存/页表"哲学相反，seL4 从第一行代码起就通过已验证原语工作。

**与极境内核的对比**：极境内核保留 Linux 的 initramfs/systemd 启动模型，在 capability 层引入等效机制（[03-microkernel-strategy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) L175-182：systemd unit + capability 初始化守护进程）。这是务实选择——Linux 启动链不能重写为 cteInsert 风格。

---

## 9. 测试工程与 CI 分层

- 构建系统：顶层 [CMakeLists.txt](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/CMakeLists.txt) L7 `cmake_minimum_required(VERSION 3.16.0)`（无 Makefile）。
- sel4test 是独立仓库（本仓库无 tests 目录），CI 引用：`.github/workflows/sel4test-sim.yml`、`sel4test-deploy.yml`。
- CI 分层（.github/workflows/）：`compilation-checks.yml`（编译）、`proof.yml`（证明）、`cparser.yml`（C parser 兼容）、`xml_lint.yml`（XML SSoT 校验）、`hw-tests.yml`（硬件测试）、`preprocess-deploy.yml`（预处理部署给 l4v）。
- syscall 分发：[syscall.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/api/syscall.c) `handleSyscall` L557-662（SysSend L563/SysCall L580/SysRecv L588/SysYield L648）。

**工程思想金句 10**：CI 分层（编译/证明/XML 校验/硬件测试）——每个层次的工程质量由专门 CI job 保障，证明与功能测试分离。

---

## 10. 编码规范与许可

- 无 `.clang-format`（glob 无结果）；有 `.cmake-format.yaml` 与 `.reuse/dep5`（REUSE 许可合规清单）——许可合规由工具链强制。
- GPL-2.0-only（内核）/ BSD-2-Clause（libsel4 用户态）双许可——内核与用户接口许可边界清晰。
- 类型系统分层：`basic_types.h` → `types.h`（word_t）→ `api/types.h`（seL4_ 用户态类型）→ `object/structures.h`（L12 include `arch/object/structures_gen.h`）。
- 编码风格要点文档化在代码注释中（util.h L28-37 ul 后缀、L48-63 ULL 时间常量防 32 位溢出）——**seL4 无独立 coding-style 文件**，与 Linux 不同。

---

## 11. 架构分层工程

- 分层：arch → machine → plat → model（无独立 mode 目录，32/64 位通过 include 路径实现零复制）。
- 统一架构钩子：[objecttype.c](file:///home/spharx/SpharxWorks/.engineer-reference/seL4-master/src/object/objecttype.c) L636-639 `if (isArchCap(cap)) return Arch_decodeInvocation(...)`——架构差异收敛到 Arch_ 前缀函数族。
- 验证视角的分层价值：CAVEATS L15-50 的验证矩阵按 arch+plat 划分——**分层即验证矩阵的物理承载**。

**与极境内核的对比**：极境内核借鉴 seL4 的 arch/machine/plat 三层架构（[03-microkernel-strategy.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/03-microkernel-strategy.md) L432），但实际内核树仍为 Linux 的 arch/ 单目录——架构层改造尚未落地（M2-M5 规划）。

---

## 12. 对极境内核的借鉴结论

### 12.1 seL4 工程思想 10 条金句

1. **验证范围诚实声明**——SMP "without formal verification"（CAVEATS L129-130）也要明示。
2. **capability 是唯一安全模型**——12 种对象、.bf 精确定义（structures_64.bf L7-43）。
3. **SSoT 单一来源，生成物禁止手改**——改 XML/.bf，C + Isabelle 证明由工具生成。
4. **验证注解是代码的公民**——MODIFIES/FNSPEC/DONT_TRANSLATE/GHOSTUPD 以注释共生（util.h L93-306）。
5. **验证配置锁存**——configs/*_verified.cmake（40+）+ proof.yml 的 proof-test label。
6. **最小化 TCB（Liedtke minimality）**——29 个核心 C 文件、12 种对象、单一 big kernel lock。
7. **机制与策略分离**——内核只提供机制（cteInsert/cteMove/cteRevoke），策略全部 user-level。
8. **decode/invoke 分离 + 编译期契约**——错误精确到参数序号（tcb.c L607-668）；枚举一致性 compile_assert 钉死（faults.c L20-26）。
9. **boot 用 cap 操作构造 cap 世界**——与 Linux 直接操作物理内存哲学相反（boot.c L496-564）。
10. **CI 分层 + 许可工具链强制**——编译/证明/XML/硬件测试分离，REUSE dep5 强制许可合规。

### 12.2 极境内核可借鉴项（补充第三轮改进清单）

| 编号 | 借鉴点 | 极境内核落点 |
|------|--------|-------------|
| E18 | compile_assert 双模式宏（AIRY_COMPILE_ASSERT） | [uapi_compat.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/uapi_compat.h) 定义内核侧 typedef 数组/用户态侧 C11 _Static_assert（与 E1 合并） |
| E19 | 验证注解（MODIFIES/FNSPEC）用于 capability/IPC fastpath | [airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap.h) L75-90 badge_ok + [airy_ipc_fastpath.c](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/kernel/corekern/ipc/airy_ipc_fastpath.c)（与 E2 合并） |
| E20 | 验证配置锁存（airymax_verified.cmake 等价物） | 新增，声明验证适用的平台/配置/特性组合（与 E3 合并） |
| E21 | 错误码精确到"参数/权限位"细分 | [airy_cap.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/security/airy/airy_cap.h) L75-90 已细分（EPOCH/MISSING/RANDTAG/PERM），需在 [SC] error.h 集中登记错误码语义（A-UEF） |
| E22 | 内核-用户态常量一致性编译期钉死 | [syscalls.h](file:///home/spharx/SpharxWorks/airymaxhub/agent-linux/kernel/include/uapi/linux/airymax/syscalls.h) L20-29 的 548-571 编号 + magic（0x41475453/0x41524531）加 compile_assert（与 E1 合并） |

### 12.3 正面确认

极境内核已在多个维度对齐 seL4 思想：capability 单一安全模型（ADR-004）、机制与策略分离（OS-IRON-003）、解码/调用分离模式（airy_cap_check.c 5-phase）、编译期断言理念（OS-KER-229 声称已落地但源码零命中——需核实）、known-caveats 诚实声明（[09-known-caveats.md](file:///home/spharx/SpharxWorks/airymaxhub/docs/AirymaxOS/10-architecture/09-known-caveats.md) L5-11）。核心差距是"可验证性预留"机制（E18-E22）未在源码层落地——文档有承诺、实现有空白。

---

## 13. 小结

seL4 工程思想的核心是"为可验证性而设计"的完整闭环：SSoT codegen 消除手写漂移 → 编译期契约钉死一致性 → 验证注解内嵌源码 → 验证配置锁存 → CAVEATS 诚实声明。极境内核"seL4 为鉴"（OS-IRON-010/012）的方向正确，但对 seL4 的借鉴停留在架构文档层（capability 模型、机制策略分离、decode/invoke），**未延伸到工程标准层**（compile_assert、验证注解、验证配置锁存）。第三轮 E18-E22 与报告 19 的 E1-E3 合并后，极境内核的"可验证性预留"改进共 5 项，其中 E1/E18（compile_assert）建议 M2 前落地，其余 M3-M5。这是极境内核从"借鉴 seL4 思想"迈向"借鉴 seL4 工程方法"的关键一步。
