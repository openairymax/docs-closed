Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# v0.2.3 目录结构设计基于 openEuler/seL4 最佳实践的审查报告

> **文档定位**: 基于 OLK-6.6（openEuler 内核基线）与 seL4-master 实际源代码目录结构的直接测绘证据，对 [`01-designs/_design_0.2.3/01-agentrt-linux-directory-structure.md`](../../01-designs/_design_0.2.3/01-agentrt-linux-directory-structure.md)（1503 行）进行的目录结构最佳实践审查。
> **保密级别**: SPHARX Ltd 内部参考，**闭源不公开**
> **版本**: 0.2.3-review-01
> **最后更新**: 2026-07-09
> **审查范围**: 全文 10 章（第 2 章管理仓 + 第 3-10 章 8 子仓）+ 附录 A/B/C
> **质量要求**: 绝对严谨、严格、严肃——每一项发现均附直接源代码证据引用，经得起第三方独立推敲
> **审查方法**: (1) OLK-6.6 源代码穷尽式 `ls` 测绘作为"Linux 6.6 为基"对照；(2) seL4-master 源代码穷尽式 `ls` 测绘作为"seL4 为鉴"对照；(3) 逐章逐节比对 v0.2.3 设计文档与双源对照，识别偏差并分级
> **结论摘要**: 12 项发现（3 P0 架构级 + 5 P1 重要 + 4 P2 改进），其中 **P0-DIR-01（kernel/ 上游继承模型未声明）是当前 v0.2.3 最根本的未决架构问题**，必须在 1.0.1 M0 目录骨架创建前显式裁决

---

## 目录

- [第 1 章 审查依据与证据基线](#第-1-章-审查依据与证据基线)
- [第 2 章 P0 架构级发现（3 项）](#第-2-章-p0-架构级发现3-项)
- [第 3 章 P1 重要发现（5 项）](#第-3-章-p1-重要发现5-项)
- [第 4 章 P2 改进建议（4 项）](#第-4-章-p2-改进建议4-项)
- [第 5 章 整体评估与裁决建议](#第-5-章-整体评估与裁决建议)
- [附录 A：发现汇总矩阵](#附录-a发现汇总矩阵)

---

## 第 1 章 审查依据与证据基线

### 1.1 双源对照基线（本轮直接测绘复核）

| 证据编号 | 对照维度 | OLK-6.6 实测 | seL4-master 实测 | 复现命令 |
|---------|---------|-------------|------------------|---------|
| EV-R01 | 顶层目录数 | **28 目录**（含 fs/net/block/drivers/mm/security/sound/certs/ipc/usr/virt 等核心子系统） | — | `ls 01Reference/kernel-OLK-6.6/` |
| EV-R02 | mm/ 顶层结构 | **20+ 扁平 .c 文件**（backing-dev.c/compaction.c/cma.c/etmem.c/dynamic_pool.c 等核心实现） + damon/ 子目录 | — | `ls 01Reference/kernel-OLK-6.6/mm/*.c` |
| EV-R03 | security/ 结构 | **12 个扁平 LSM 顶层目录**（apparmor/bpf/integrity/keys/landlock/loadpin/lockdown/safesetid/selinux/smack/tomoyo/yama），无 lsm/ 包装层 | — | `ls -d 01Reference/kernel-OLK-6.6/security/*/` |
| EV-R04 | src/object/ 文件 | — | **11 文件**（cnode/domain/endpoint/interrupt/notification/objecttype/reply/schedcontext/schedcontrol/tcb/untyped） | `ls 01Reference/seL4-master/src/object/` |
| EV-R05 | tools/testing/ 结构 | **11 子目录**（crypto/cxl/fault-injection/ktest/kunit/memblock/nvdimm/radix-tree/scatterlist/selftests/vsock） | — | `ls -d 01Reference/kernel-OLK-6.6/tools/testing/*/` |
| EV-R06 | arch/x86/ 子目录 | **26 子目录**（含 coco/kvm/pci/platform/power/tools 等核心架构子目录） | — | 已在 v0.2.3 EV-09 引用 |
| EV-R07 | libsel4/ 分层 | — | **四级 include 分层**（arch_include/include/mode_include/sel4_arch_include/sel4_plat_include）+ src/ + tools/ | 已在 v0.2.3 EV-06 引用 |

### 1.2 v0.2.3 设计文档当前结构概览

| 子仓 | v0.2.3 设计的核心子目录 | 对照来源 |
|------|----------------------|---------|
| kernel/ | arch/{x86,arm64,riscv}/ + include/{uapi,airymax}/ + corekern/{10 子目录} + init/ + lib/ + machine/ + crypto/ + io_uring/ + patches/ + Documentation/ + scripts/ + tests/ | OLK-6.6 + seL4 |
| services/ | meson.build + 12 daemons + userland-{vfs,net,drivers}/ + ipc/ + systemd/ | seL4 服务用户态化 |
| security/ | capability/ + lsm/{agent_lsm,common}/ + cupolas/ + sandbox/ + confidential-compute/ + zero-trust/ + ebpf-verify/ | OLK-6.6 + seL4 |
| memory/ | memoryrovol/ + cxl/ + pmem/ + mglru/ + vfs-persist-kern/ | OLK-6.6 mm/ |
| cognition/ | coreloopthree/ + thinkdual/ + wasm-runtime/ + llm-scheduler/ + compute-accel/ + token-efficiency/ + super-node-cog-snapshot/ + embodied-io/ | Airymax 同源 |
| cloudnative/ | kubernetes/ + containerd-shim/ + oci/ + cni/ + agentctl/ + observability/ + dpu-ipu/ + super-node-os/ + sdk/ | 现代云原生 |
| system/ | init-system/ + package-manager/ + config/ + shell/ + base-libs/ + monitoring/ + devstation/ | OLK-6.6 init/ + systemd |
| tests-linux/ | unit/ + integration/ + formal-verification/ + soak/ + chaos/ + benchmark/ + observability-verify/ + tools/ + configs/ | OLK-6.6 + seL4 |

---

## 第 2 章 P0 架构级发现（3 项）

### P0-DIR-01: kernel/ 子仓的"上游内核继承模型"未显式声明

**严重级别**: P0（架构级根本问题，1.0.1 M0 目录骨架前必须裁决）

**发现证据**:

v0.2.3 `kernel/` 子仓（§3.2）的顶层子目录为：`arch/` + `include/` + `corekern/` + `init/` + `lib/` + `machine/` + `crypto/` + `io_uring/` + `patches/` + `Documentation/` + `scripts/` + `tests/`（共 12 个）。

对照 OLK-6.6 顶层 28 个目录（EV-R01），v0.2.3 kernel/ **缺失以下核心子系统**：
- `fs/`（文件系统层）
- `net/`（网络协议栈）
- `block/`（块设备层）
- `drivers/`（设备驱动）
- `mm/`（核心内存管理——伙伴系统/SLUB/compaction 等）
- `security/`（LSM 框架）
- `sound/`、`certs/`、`ipc/`、`samples/`、`usr/`、`virt/`（其他核心子系统）

这缺失的 12 个目录是 Linux 内核运行的**不可缺失的基础设施**。v0.2.3 全文未显式声明 kernel/ 与这些上游子系统的关系模型。

**问题本质——两种互斥的架构模型**:

| 模型 | 含义 | 后果 |
|------|------|------|
| **模型 A：完整内核源码树** | kernel/ 含完整 Linux 6.6 源码 + Airymax 补丁 | 子仓体积巨大（~1.2GB），与上游同步困难，但构建自包含 |
| **模型 B：补丁叠加模型** | kernel/ 仅 Airymax 专属代码 + patches/ 上游修改 diff，完整 Linux 6.6 基线作为外部构建依赖 | 子仓精简，上游同步仅需 rebase patches/，但构建需引用外部基线源码树 |

v0.2.3 的 `patches/` 目录存在（§3.2 注释"对上游 Linux 内核的修改 diff"）暗示采用**模型 B**，但全文未显式声明，且未说明构建时如何引用上游 Linux 6.6 基线源码树（`KBUILD_EXT`? 独立 source tree? 符号链接?）。

**影响**:
1. **构建不可执行**：若选模型 B 但未声明上游基线路径，则 `make` 时 `#include <linux/sched.h>` 等核心头文件无处解析，corekern/ 无法编译。
2. **目录骨架无法创建**：1.0.1 M0 阶段需创建空目录骨架，但不知是否应在 kernel/ 下创建 fs/net/block/drivers/mm/security 等空目录（模型 A）还是不创建（模型 B）。
3. **CI 不可定义**：CI 流水线需知上游基线源码树位置才能构建，未声明则 CI 设计无法落地。
4. **依赖层次 L2 定义模糊**：§11.2 称 kernel 是 L2"依赖 L1（Linux 6.6 基线）"，但"依赖"在模型 B 下是构建期外部引用，在模型 A 下是子仓内源码——两种依赖语义完全不同。

**修正建议**:

在 §3.1 设计依据中新增"上游内核继承模型"显式声明，推荐**模型 B（补丁叠加模型）**并完整定义引用机制：

```markdown
#### 3.1.1 上游内核继承模型（模型 B：补丁叠加模型）

kernel/ 子仓采用"补丁叠加模型"：仅含 Airymax 专属内核代码 + 对上游 Linux 6.6（OLK-6.6）的修改 diff，
完整 Linux 6.6 基线源码树作为外部构建依赖，不在子仓内物理存储。

**构建期引用机制**:
- 上游基线路径通过环境变量 `AIRYMAX_KERNEL_BASE=/path/to/kernel-OLK-6.6` 声明
- kernel/ 子仓 Makefile 通过 `-I$(AIRYMAX_KERNEL_BASE)/include` 引用上游头文件
- patches/ 目录的 diff 在构建前 `patch -p1` 应用到上游基线源码树

**子仓内容边界**:
- 物理存储：仅 arch/{x86,arm64,riscv}/ 的 Airymax 扩展 + corekern/ + patches/ + [SC] 头文件
- 不物理存储：fs/ net/ block/ drivers/ mm/ security/ sound/ certs/ 等上游核心子系统（由基线源码树提供）

**CI 构建**: CI 流水线在构建前 git clone OLK-6.6 基线 + apply patches/ + 构建 kernel/ 子仓
```

**验证方式**: 在 §3.2 目录结构注释中标注"上游继承"vs"Airymax 专属"，使审查者一眼区分。

---

### P0-DIR-02: memory/ 子仓与 kernel/corekern/memory/ + 上游 mm/ 的三方边界冲突

**严重级别**: P0（边界冲突将导致编译期符号冲突与运行期初始化顺序问题）

**发现证据**:

内存管理实现当前分散在三处，边界未显式声明：

| 位置 | v0.2.3 当前内容 | 职责 |
|------|----------------|------|
| (1) `kernel/corekern/memory/` | 仅 `page_alloc.h` 接口（DIR-P1-04 修正） | 内核核心内存接口声明 |
| (2) `memory/` 子仓 | memoryrovol/ + cxl/ + pmem/ + mglru/ + vfs-persist-kern/ | Airymax 专属内存扩展 |
| (3) OLK-6.6 `mm/` 顶层 | backing-dev.c / compaction.c / cma.c / etmem.c / dynamic_pool.c 等 20+ 核心 .c（EV-R02） | 伙伴系统/SLUB/compaction/CMA 等核心实现 |

**冲突点**:
- **MemoryRovol L1-L4 与上游 mm/ 的衔接**：[SC] memory_types.h 定义 MemoryRovol L1-L4 数据结构，但 L1（基础页管理）如何与上游 `mm/page_alloc.c` 的伙伴系统衔接？是 hooks 钩子还是直接修改上游？
- **vfs-persist-kern/ 与上游 fs/ 的关系**：memory/vfs-persist-kern/backends/ 的内核态持久化后端如何挂载到上游 fs/ 层？若 kernel/ 采用模型 B（P0-DIR-01），上游 fs/ 在基线源码树，vfs-persist-kern/ 在 memory 子仓，两者如何编译期链接？
- **mglru/ 与上游 mm/damon/ 的关系**：v0.2.3 memory/mglru/ 是 Airymax 增强还是替代上游 mm/damon/？（注：v0.2.3 附录 C 已删除 damon 引用，但 mglru/ 子目录仍存在，未说明与上游 MGLRU 多代 LRU 的关系）

**影响**:
1. **编译期符号冲突**：若 memory 子仓与上游 mm/ 都定义 `page_alloc` 相关符号，链接期冲突。
2. **运行期初始化顺序**：memoryrovol/ 的 L1-L4 初始化需在伙伴系统之后，但未声明 initcall 优先级。
3. **依赖层次 L3 模糊**：§11.2 称 memory 是 L3"依赖 L2 kernel [SC] 头文件"，但 memoryrovol/ 实际依赖上游 mm/ 的伙伴系统接口，不仅是 [SC] 头文件。

**修正建议**:

在 §6.1 新增"内存管理三方边界声明"：

```markdown
#### 6.1.1 内存管理三方边界声明

AirymaxOS 内存管理由三方协作，边界如下：

| 方 | 位置 | 内容 | 上游关系 |
|----|------|------|---------|
| 上游 mm/ | OLK-6.6 基线源码树 `mm/` | 伙伴系统/SLUB/compaction/CMA 等核心实现（20+ .c） | 完整继承，仅在 patches/mm/ 放修改 diff |
| kernel/corekern/memory/ | kernel 子仓 | 仅 page_alloc.h 接口声明（[SC] memory_types.h 引用） | 不含实现，对齐 seL4 极简原则 |
| memory 子仓 | memory/{memoryrovol,cxl,pmem,mglru,vfs-persist-kern} | Airymax 专属内存扩展 | 通过 hooks/钩子接入上游 mm/，不重复实现 |

**MemoryRovol L1-L4 与上游 mm/ 的衔接**:
- L1（基础页管理）→ 复用上游 mm/page_alloc.c 伙伴系统，patches/mm/ 放 Airymax 增强补丁
- L2-L4（分级内存）→ memory 子仓 memoryrovol/ 实现，通过 hooks/ 接入上游 mm/ 的 page migration 接口

**vfs-persist-kern/ 与上游 fs/ 的关系**:
- 持久化后端接口在 memory 子仓声明
- 实现通过 patches/fs/ 修改上游 fs/ 层挂载点（模型 B）
```

---

### P0-DIR-03: security/ 子仓的 LSM 组织方式偏离 OLK-6.6 扁平模型 + 缺失 integrity/keys/

**严重级别**: P0（LSM 组织方式偏离 + 安全基础设施缺失）

**发现证据**:

v0.2.3 `security/` 子仓（§5）结构：`capability/` + `lsm/{agent_lsm,common}/` + `cupolas/{rules,policy,sanitize,audit}/` + `sandbox/{landlock,seccomp}/` + `confidential-compute/{sgx,sev-snp,tdx}/` + `zero-trust/` + `ebpf-verify/`。

对照 OLK-6.6 `security/`（EV-R03）：**12 个扁平 LSM 顶层目录**，无 `lsm/` 包装层：
`apparmor/` `bpf/` `integrity/` `keys/` `landlock/` `loadpin/` `lockdown/` `safesetid/` `selinux/` `smack/` `tomoyo/` `yama/`

**两个偏差**:

**偏差 1：lsm/ 包装层偏离 OLK-6.6 扁平模型**

v0.2.3 用 `lsm/{agent_lsm,common}/` 包装 Airymax 专属 LSM，但 OLK-6.6 每个 LSM 是 security/ 顶层平级目录（如 security/selinux/、security/landlock/）。包装层不符合上游惯例。

**偏差 2：缺失 security/integrity/ 和 security/keys/**

OLK-6.6 的 `security/integrity/`（完整性度量架构 IMA/EVM）和 `security/keys/`（密钥管理 keyring）是**安全基础设施**，承载完整性度量和密钥生命周期管理。v0.2.3 security/ 子仓缺失这两个目录，但 AirymaxOS 作为内核发行版，完整性度量和密钥管理是安全加固（M4 里程碑）的核心组件。

**影响**:
1. **LSM 注册机制混淆**：若 kernel/ 采用模型 B（P0-DIR-01），上游 LSM 框架（security/ 下 12 个 LSM）由基线继承，Airymax 专属 agent_lsm 应通过 patches/security/ 注册到上游 LSM 链表，而非用 lsm/ 包装层重新组织。
2. **完整性度量缺失**：无 security/integrity/ 声明，则 IMA/EVM 完整性度量方案在 AirymaxOS 中位置不明。
3. **密钥管理缺失**：无 security/keys/ 声明，则 keyring 密钥生命周期管理方案位置不明。

**修正建议**:

采用方案 A（推荐，对齐 OLK-6.6 扁平模型）：

```markdown
security/
├── agent_lsm/              # Airymax 专属 LSM（从 lsm/agent_lsm/ 提升，对齐 OLK-6.6 扁平模型）
├── common/                 # LSM 公共框架代码（从 lsm/common/ 提升）
├── integrity/              # 完整性度量架构（IMA/EVM）[NEW，声明继承上游 + Airymax 扩展]
│   └── README.md           # 说明：上游 security/integrity/ 完整继承，Airymax 扩展在 patches/security/integrity/
├── keys/                   # 密钥管理 keyring [NEW，同上]
│   └── README.md
├── capability/             # capability 派生模型（seL4 借鉴，保留）
├── cupolas/                # Airymax Cupolas 安全框架（保留）
├── sandbox/                # 沙箱（landlock + seccomp，保留）
├── confidential-compute/   # 机密计算（sgx/sev-snp/tdx，保留）
├── zero-trust/             # 零信任（保留）
└── ebpf-verify/            # eBPF 验证（保留）
```

或方案 B（保留 lsm/ 包装但说明理由）：
- 在 §5 说明"Airymax 不复用上游 LSM 实现，故用 lsm/ 聚合 Airymax 专属 LSM 模块；上游 12 个 LSM 由基线源码树 security/ 继承"
- 但仍需新增 integrity/ 和 keys/ 声明

**推荐方案 A**，理由：对齐 ES-OLK-2 架构正交原则（OLK-6.6 每策略一目录），且避免 lsm/ 包装层增加路径深度。

---

## 第 3 章 P1 重要发现（5 项）

### P1-DIR-01: corekern/object/ 仅 4 文件 vs seL4 11 文件，未说明取舍依据

**发现证据**:

v0.2.3 `kernel/corekern/object/`（DIR-P1-05 新增）仅含 4 文件：`cnode.c` + `tcb.c` + `endpoint.c` + `notification.c`。

对照 seL4 `src/object/`（EV-R04）有 **11 文件**：cnode.c / domain.c / endpoint.c / interrupt.c / notification.c / objecttype.c / reply.c / schedcontext.c / schedcontrol.c / tcb.c / untyped.c。

**缺失 7 文件及推测的取舍理由（v0.2.3 未声明）**:

| seL4 文件 | seL4 用途 | 推测取舍 | v0.2.3 是否声明 |
|----------|----------|---------|----------------|
| domain.c | 域隔离调度 | Airymax 用 namespace 替代？ | ❌ 未声明 |
| interrupt.c | 中断对象管理 | 移入 corekern/irq/（已有）？ | ❌ 未声明 |
| objecttype.c | 对象类型注册 | Airymax 用 [SC] type 头替代？ | ❌ 未声明 |
| reply.c | MCS reply 对象 | Airymax 是否采用 MCS？ | ❌ 未声明 |
| schedcontext.c | 调度上下文 | 移入 corekern/sched/（已有）？ | ❌ 未声明 |
| schedcontrol.c | 调度控制 | 移入 corekern/sched/（已有）？ | ❌ 未声明 |
| untyped.c | 未类型化内存对象 | 移入 corekern/memory/（仅 page_alloc.h）？ | ❌ 未声明 |

**影响**: seL4 的对象模型是其 capability 系统的核心，schedcontext/schedcontrol 是调度上下文管理，untyped 是内存对象管理。缺失说明会让审查者无法判断 Airymax 内核对象模型是否完整。

**修正建议**: 在 §3.3 corekern/object/ 说明中，新增"seL4 src/object/ 对象模型取舍矩阵"，逐项列出 7 个缺失文件的去向与理由。

---

### P1-DIR-02: tests-linux/ 未对齐 OLK-6.6 tools/testing/ 的 11 子目录结构

**发现证据**:

v0.2.3 `tests-linux/`（§10.2）用 9 个目录组织：`unit/` + `integration/` + `formal-verification/` + `soak/` + `chaos/` + `benchmark/` + `observability-verify/` + `tools/` + `configs/`。

对照 OLK-6.6 `tools/testing/`（EV-R05）有 **11 子目录**：`crypto/` `cxl/` `fault-injection/` `ktest/` `kunit/` `memblock/` `nvdimm/` `radix-tree/` `scatterlist/` `selftests/` `vsock/`。

**关键缺失**:
- `kunit/`：KUnit 内核单元测试框架（OLK-6.6 标准单元测试基础设施）
- `selftests/`：kselftest 内核自测框架（OLK-6.6 标准回归测试基础设施）

**影响**:
1. AirymaxOS 作为内核发行版，应复用上游 KUnit/kselftest 框架，而非完全自建 unit/ 测试组织。
2. v0.2.3 tests-linux/unit/ 按"kernel_unit/services_unit/..."分子目录组织，但 OLK-6.6 kselftest 按"子系统/测试用例"组织（如 selftests/sched/、selftests/mm/），两者粒度不同。
3. 缺失 fault-injection/（故障注入测试），OLK-6.6 有独立框架。

**修正建议**:

在 §10.2 调整 tests-linux/ 组织，对齐 OLK-6.6 + 保留 Airymax 专属：

```markdown
tests-linux/
├── kunit/                   # [NEW] 对齐 OLK-6.6 tools/testing/kunit/（KUnit 内核单元测试）
│   ├── sched/               # 按子系统组织（对齐 kselftest 惯例）
│   ├── ipc/
│   ├── memory/
│   └── security/
├── selftests/               # [NEW] 对齐 OLK-6.6 tools/testing/selftests/（kselftest 回归测试）
│   ├── sched/
│   ├── mm/
│   └── ...
├── fault-injection/         # [NEW] 对齐 OLK-6.6 tools/testing/fault-injection/
├── integration/             # 保留（跨子仓集成，Airymax 专属）
├── formal-verification/     # 保留（seL4 借鉴）
├── soak/                    # 保留（云原生，Airymax 专属）
├── chaos/                   # 保留（云原生，Airymax 专属）
├── benchmark/               # 保留（性能基准，Airymax 专属）
├── observability-verify/    # 保留（eBPF 验证，Airymax 专属）
├── tools/                   # 保留
└── configs/                 # 保留
```

并删除原 `unit/`（内容迁入 kunit/），在 §10.3 说明"unit/ 迁入 kunit/ 对齐上游 KUnit 框架"。

---

### P1-DIR-03: cloudnative/sdk/ 未体现附录 A 声称的 libsel4 四级 include 分层

**发现证据**:

v0.2.3 附录 A 称 cloudnative sdk/ "借鉴 seL4 libsel4 四级 include 分层（arch_include/include/mode_include/sel4_arch_include/sel4_plat_include，EV-06）"。

但 §8 cloudnative/sdk/ 实际结构为 `python/` + `rust/` + `go/` + `typescript/`（按语言组织），**未体现四级 include 分层**。

**影响**: 附录 A 声明与实际目录结构不符，违反"每一处目录设计决策均附直接源代码证据引用"的质量要求。

**修正建议**:

采用方案 A（推荐，修正声明）：
- 修正附录 A 声明为："cloudnative sdk/ 借鉴 seL4 libsel4 **独立 API 库**思想（libsel4 独立于 src/，sdk/ 独立于各子仓），非四级 include 分层。sdk/ 按**目标语言**组织，符合 SDK 多语言生态惯例。"
- 理由：四级 include 分层（arch_include/ + mode_include/ 等）是 seL4 针对 C 头文件跨架构/跨模式复用的特殊设计，不适用于 Go/Rust/Python/TS 等现代语言 SDK。

或方案 B（强制对齐）：在 sdk/<lang>/ 内部新增 arch/ + plat/ 分层——但不推荐，破坏语言生态惯例。

---

### P1-DIR-04: services/ userland-{vfs,net,drivers}/ 与上游 fs/drivers/ 的关系未说明

**发现证据**:

v0.2.3 `services/` 子仓（§4）含 `userland-vfs/` + `userland-net/` + `userland-drivers/`（借鉴 seL4 ES-SEL4-3 服务用户态化）。

但 OLK-6.6 的 `fs/` 和 `drivers/` 是**内核态实现**（顶层目录，EV-R01）。若 kernel/ 采用模型 B（P0-DIR-01），上游 fs/drivers 在内核态基线源码树，Airymax userland-vfs/userland-drivers 在用户态 services 子仓，两者如何协作未说明。

**影响**:
- userland-vfs/ 是通过 FUSE 接入上游 fs/，还是完全替代上游 fs/？
- userland-net/ 是通过 AF_UNIX/socket 接入上游 net/，还是完全替代？
- userland-drivers/ 是通过 VFIO/UIO 接入上游 drivers/，还是完全替代？

**修正建议**:

在 §4 services/ 说明中新增"用户态服务与上游内核 fs/drivers 的关系"声明：

```markdown
#### 4.1.1 用户态服务与上游内核子系统的关系

AirymaxOS 用户态服务（userland-vfs/net/drivers）通过标准接口接入上游内核子系统，不替代上游实现：

| 用户态服务 | 接入机制 | 上游内核子系统 | 关系 |
|-----------|---------|---------------|------|
| userland-vfs/ | FUSE + 新增 syscall | fs/ | Airymax 专属增强，不替代上游 fs/ |
| userland-net/ | AF_UNIX + socket | net/ | Airymax 专属增强，不替代上游 net/ |
| userland-drivers/ | VFIO + UIO | drivers/ | Airymax 专属增强，不替代上游 drivers/ |
```

---

### P1-DIR-05: kernel/arch/<arch>/ 内容边界未声明（含与 OLK-6.6 arch/x86/ 26 子目录的差距）

**发现证据**:

v0.2.3 `kernel/arch/x86/` 含 9 项：`Kbuild/` + `Kconfig/` + `configs/` + `include/` + `kernel/` + `mm/` + `entry/` + `machine/` + `boot/` + `lib/`。

对照 OLK-6.6 `arch/x86/`（EV-R06）有 **26 子目录**，v0.2.3 缺失：`coco/`（机密计算）、`crypto/`、`events/`、`hyperv/`、`ia32/`、`kvm/`（虚拟化）、`pci/`、`platform/`、`power/`、`purgatory/`、`ras/`、`realmode/`、`tools/`、`um/`、`video/`、`virt/`、`xen/` 等 17 个核心架构子目录。

**影响**:
- 若 kernel/ 采用模型 B（P0-DIR-01），arch/<arch>/ 只需 Airymax 专属架构代码，上游 arch/x86/ 由基线继承——但 v0.2.3 未声明此边界。
- 若未声明，审查者无法判断 arch/x86/ 是否应补全 kvm/pci/platform 等子目录。

**修正建议**:

在 §3.2 明确声明 arch/<arch>/ 的内容边界为"Airymax 专属架构扩展 + patches/arch/"：

```markdown
#### 3.2.1 arch/<arch>/ 内容边界声明

arch/<arch>/ 仅含 Airymax 专属架构扩展代码，上游 arch/x86/ 的 26 子目录（含 kvm/pci/platform/power 等）
由 OLK-6.6 基线源码树继承（模型 B）。Airymax 对上游 arch/ 的修改在 patches/arch/ 中。

arch/<arch>/ 内容：
- entry/：Airymax 专属系统调用/中断入口
- machine/：Airymax 专属机器原语（capdl/fpu/...）
- kernel/：Airymax 专属内核执行逻辑扩展
- mm/：Airymax 专属内存管理架构扩展
- configs/：Airymax defconfig
- include/：Airymax 架构相关头文件
- boot/、lib/：Airymax 专属引导与库
```

---

## 第 4 章 P2 改进建议（4 项）

### P2-DIR-01: kernel/patches/ 命名空间未分子系统

**发现**: v0.2.3 `kernel/patches/` 平铺所有上游修改 diff，但 OLK-6.6 的补丁通常按子系统组织。

**建议**: patches/ 内按子系统分子目录，对齐上游补丁组织惯例：
```
patches/
├── mm/          # 内存管理修改（对应上游 mm/）
├── sched/       # 调度器修改（对应上游 kernel/sched/）
├── ipc/         # IPC 修改（对应上游 ipc/）
├── security/    # 安全修改（对应上游 security/）
├── arch/        # 架构修改（对应上游 arch/）
└── core/        # 核心内核修改（对应上游 kernel/）
```
**优先级**: P2，1.0.1 M0 目录骨架时落地。

---

### P2-DIR-02: system/devstation/ 与 cognition/ 的 AI 能力重叠

**发现**: v0.2.3 `system/devstation/` 含 `ai_assistant.c` + `ai_plugins/`，与 `cognition/` 的 LLM 推理能力（llm-scheduler/）重叠。

**建议**: 在 §9.3 明确边界：
- `system/devstation/` = 开发者工具集成（CLI + 工具链集成），AI 能力通过 IPC 调用 `cognition/llm-scheduler/`
- `cognition/llm-scheduler/` = LLM 推理核心（所有 LLM 调用的单一入口）
- devstation/ 不自建 LLM 推理，仅作为 cognition/ 的前端消费者

**优先级**: P2，边界声明即可，不需目录调整。

---

### P2-DIR-03: cognition/compute-accel/ 与 cloudnative/dpu-ipu/ 的硬件加速边界

**发现**: v0.2.3 `cognition/compute-accel/`（算力加速调度）与 `cloudnative/dpu-ipu/`（DPU/IPU 卸载）都涉及硬件加速，职责边界需澄清。

**建议**: 在 §7 + §8 明确边界：
- `cognition/compute-accel/` = GPU/NPU 算力调度策略（聚焦 AI 推理任务的 GPU/NPU 调度）
- `cloudnative/dpu-ipu/` = DPU/IPU 网络/存储卸载（聚焦基础设施层硬件卸载）
- 两者通过 [SC] cognition_types.h 的 GPU/NPU 能力描述符区分

**优先级**: P2，边界声明即可。

---

### P2-DIR-04: 缺失顶层 tools/ 管理目录

**发现**: OLK-6.6 有顶层 `tools/`（含 testing/scripts/build/perf 等），v0.2.3 管理仓 agentrt-linux/ 无顶层 tools/，测试在 tests-linux/，脚本在各子仓 scripts/。

**建议**: 在管理仓 agentrt-linux/ 新增 `tools/` 软链接或声明，聚合跨子仓工具（如 `tools/checkpatch-airymax.sh` 引用各子仓 scripts/ 的检查脚本）。或在 §2 声明"tools/ 分散在各子仓 scripts/，不设顶层聚合"。

**优先级**: P2，声明即可，1.0.1 M0 决定。

---

## 第 5 章 整体评估与裁决建议

### 5.1 v0.2.3 目录结构成熟度评估

| 维度 | 评估 | 依据 |
|------|------|------|
| 双源证据严谨性 | ✅ 优秀（100/100） | EV-01~EV-11 直接证据索引完整，复现命令清晰 |
| 8 子仓顶层划分 | ✅ 优秀（95/100） | L2-L7 依赖层次清晰，对齐 ES-OLK-1 关注点分离 |
| kernel/ 架构模型 | ⚠️ 未决（70/100） | P0-DIR-01 上游继承模型未声明，是当前最根本问题 |
| memory/ 边界 | ⚠️ 冲突（75/100） | P0-DIR-02 三方边界未显式声明 |
| security/ 组织 | ⚠️ 偏离（80/100） | P0-DIR-03 lsm/ 包装偏离 + 缺失 integrity/keys/ |
| corekern/ 极简 | ✅ 良好（85/100） | P1-DIR-01 object/ 取舍依据未声明 |
| tests-linux/ 对齐 | ⚠️ 部分（80/100） | P1-DIR-02 缺失 kunit/selftests 对齐 |
| 跨子仓一致性 | ✅ 优秀（95/100） | §11 约束清晰，[SC] 单一数据源修正到位 |

**综合成熟度**: **85/100（B+，有条件 Go）**

相对 v0.2.1 的提升显著（双源证据 + L2-L7 层次 + [SC] 单一数据源修正），但 P0-DIR-01 的上游继承模型未声明是阻塞性问题，必须在 1.0.1 M0 目录骨架创建前裁决。

### 5.2 裁决建议

#### 建议 1：立即裁决 P0-DIR-01（上游内核继承模型）

**推荐采用模型 B（补丁叠加模型）**，理由：
1. 符合 AirymaxOS 定位（"智能体操作系统"研究项目，非完整 Linux 发行版 fork）
2. 子仓精简，上游同步仅需 rebase patches/
3. 对齐 seL4 同源独立性原则（Airymax 专属代码与上游基线物理分离）
4. 工程标准规范 §13.1 的 L2 定义（kernel 依赖 L1 Linux 6.6 基线）在模型 B 下语义清晰

裁决后需在 v0.2.3 §3.1 + §6.1 + §5 + §4 同步声明模型 B 的引用机制与边界。

#### 建议 2：v0.2.4 修正版产出

基于本审查 12 项发现，建议产出 v0.2.4 修正版：
- 修正 3 项 P0（P0-DIR-01/02/03）
- 修正 5 项 P1（P1-DIR-01~05）
- 明确 4 项 P2（P2-DIR-01~04，声明或目录调整）

#### 建议 3：1.0.1 M0 目录骨架前的阻断项

以下 3 项必须在 1.0.1 M0 目录骨架创建前解决（阻断项）：
1. P0-DIR-01：裁决上游继承模型（否则不知创建哪些空目录）
2. P0-DIR-02：声明 memory 三方边界（否则 memoryrovol/ 编译依赖不明）
3. P0-DIR-03：决定 security/ 组织方式（否则 security/ 骨架结构不明）

P1/P2 项可在 M0 阶段并行修正，不阻断目录骨架创建。

---

## 附录 A：发现汇总矩阵

| 编号 | 级别 | 子仓 | 问题摘要 | 修正方式 | 阻断 M0 |
|------|------|------|---------|---------|---------|
| P0-DIR-01 | P0 | kernel | 上游内核继承模型未声明 | §3.1 新增模型 B 声明 | ✅ 是 |
| P0-DIR-02 | P0 | memory | 三方边界冲突（corekern/memory + memory 子仓 + 上游 mm/） | §6.1 新增三方边界声明 | ✅ 是 |
| P0-DIR-03 | P0 | security | lsm/ 包装偏离 OLK-6.6 + 缺失 integrity/keys/ | §5 调整为扁平模型 + 新增 integrity/keys/ | ✅ 是 |
| P1-DIR-01 | P1 | kernel | corekern/object/ 4 vs 11 文件取舍未声明 | §3.3 新增取舍矩阵 | ❌ 否 |
| P1-DIR-02 | P1 | tests-linux | 未对齐 OLK-6.6 tools/testing/ 11 子目录 | §10.2 新增 kunit/selftests/fault-injection | ❌ 否 |
| P1-DIR-03 | P1 | cloudnative | sdk/ 未体现附录 A 声称的 libsel4 四级分层 | 修正附录 A 声明 | ❌ 否 |
| P1-DIR-04 | P1 | services | userland-{vfs,net,drivers}/ 与上游 fs/drivers 关系未说明 | §4 新增接入机制声明 | ❌ 否 |
| P1-DIR-05 | P1 | kernel | arch/<arch>/ 内容边界未声明（vs OLK-6.6 26 子目录） | §3.2 新增边界声明 | ❌ 否 |
| P2-DIR-01 | P2 | kernel | patches/ 未分子系统 | patches/{mm,sched,ipc,security,arch,core}/ | ❌ 否 |
| P2-DIR-02 | P2 | system/cognition | devstation/ 与 cognition/ AI 能力重叠 | §9.3 边界声明 | ❌ 否 |
| P2-DIR-03 | P2 | cognition/cloudnative | compute-accel/ 与 dpu-ipu/ 硬件加速边界 | §7+§8 边界声明 | ❌ 否 |
| P2-DIR-04 | P2 | 管理仓 | 缺失顶层 tools/ 管理目录 | §2 声明或新增 tools/ | ❌ 否 |

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
