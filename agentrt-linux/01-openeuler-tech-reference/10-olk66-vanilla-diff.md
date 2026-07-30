Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# OLK-6.6 与 vanilla 6.6.145 差异对比（SSoT）

> **保密级别**: SPHARX Ltd 内部参考，**闭源不公开**
> **版本**: 1.0.0
> **最后更新**: 2026-07-30
> **适用范围**: AirymaxOS 架构委员会 + 内核开发组
> **数据来源**: `openeuler/OLK-6.6`（gitee.com/openeuler/kernel，shallow fetch）对比 `linux-stable/linux-6.6.y`（kernel.org 6.6.145）
> **上游 tip**: `5078a3a23a1e` ("update README.")

---

## 1. 对比方法与基线

| 维度 | vanilla | OLK-6.6 |
|------|---------|---------|
| 仓库 | git.kernel.org/linux-stable | gitee.com/openeuler/kernel |
| 分支 | linux-6.6.y | OLK-6.6 |
| 版本 | 6.6.145 | 6.6.0 + openEuler backport |
| 版本标记 | — | `Makefile.oever`: OPENEULER_LTS=0, MAJOR=9999, MINOR=0 |
| Airymax remote | `linux-stable` | `openeuler`（本次新增） |

**对比命令**：`git diff --stat linux-stable/linux-6.6.y openeuler/OLK-6.6`

**注意**：OLK-6.6 基于 6.6.0，Airymax vanilla 为 6.6.145。两者无共同祖先（OLK shallow fetch），故 `git diff` 为树对树直比，差异含 145 个稳定版补丁的回溯差距 + openEuler 增量。本文档聚焦 **openEuler 增量**。

---

## 2. 总体差异规模

```
12,083 files changed, 1,496,524 insertions(+), 184,042 deletions(-)
```

差异来源分解：

| 来源 | 说明 | 处置 |
|------|------|------|
| openEuler 硬件驱动层 | sw_64 架构 + 厂商驱动（鲲鹏/海思/华为/申威/阿里） | **LAYER 方案提取** |
| openEuler 调度增量 | grid/ QoS + bpf_sched + soft_domain + smt_qos | **排除**（与 sched_tac 冲突） |
| openEuler security/ | 74 文件修改（LSM/capability/landlock） | **排除**（Airymax 用 vanilla + airy_lsm） |
| openEuler 构建系统 | Makefile.oever + KABI 宏 | **排除**（Makefile.oever）/ **剥离**（KABI 标记） |
| 6.6.0→6.6.145 稳定版差距 | 145 个稳定版补丁的回溯差异 | 无关（vanilla 已含） |

---

## 3. 架构差异（arch/）

### 3.1 OLK 独有架构

| 架构 | 说明 | 规模 | 处置 |
|------|------|------|------|
| `arch/sw_64/` | 申威 SW_64（Sunway） | 352 文件, +54,093 行 | **LAYER 导入**（vanilla 不含此架构） |

### 3.2 vanilla 已含架构（22 个）

alpha, arc, arm, arm64, csky, hexagon, ia64, loongarch, m68k, microblaze, mips, nios2, openrisc, parisc, powerpc, riscv, s390, sh, sparc, um, x86, xtensa

OLK 与 vanilla 在这些架构上的差异为 openEuler 厂商增强（Kunpeng/Phytium/Hygon 等），分布在 `arch/{arm64,x86}/` 下，需按 LAYER 方案逐目录甄别提取。

### 3.3 openEuler defconfig

| 架构 | defconfig | 处置 |
|------|-----------|------|
| x86 | `arch/x86/configs/openeuler_defconfig` | 参考（提取硬件 CONFIG 碎片） |
| arm64 | `arch/arm64/configs/openeuler_defconfig` | 参考（提取硬件 CONFIG 碎片） |
| sw_64 | `arch/sw_64/configs/openeuler_defconfig` | 随 sw_64 架构导入 |

> **注意**：loongarch 无 openeuler_defconfig（OLK-6.6 对 loongarch 支持较弱）。

---

## 4. 驱动差异（drivers/）

### 4.1 OLK 独有顶层驱动目录（8 个）

| 目录 | 性质 | Kconfig 摘要 | 依赖 | 处置 |
|------|------|-------------|------|------|
| `drivers/cpuinspect/` | openEuler 原创 | CPU Inspect（SDC 早期检测框架） | SYSFS && 64BIT | **LAYER 提取**（跨厂商） |
| `drivers/hooks/` | openEuler 原创 | Vendor Hooks（tracepoint 钩子，DECLARE_HOOK/DECLARE_RESTRICTED_HOOK） | TRACEPOINTS | **LAYER 提取**（厂商模块挂载基础） |
| `drivers/roh/` | openEuler 原创 | ROH（RDMA over HMEM） | ARM64 + NET_VENDOR_HISILICON | **LAYER 提取**（鲲鹏） |
| `drivers/ub/` | openEuler 原创 | UB（UnifiedBus） | ARM64 | **LAYER 提取**（鲲鹏） |
| `drivers/xcu/` | openEuler 原创 | 无 Kconfig（Makefile-only） | — | **LAYER 提取**（待评估） |
| `drivers/arm/` | 主线回溯 | ARM SB PSCI（mainline 6.10+） | — | 可选回溯（非 openEuler 原创） |
| `drivers/coda/` | 版本差异 | 旧网络文件系统 | — | 不提取 |
| `drivers/fwctl/` | 主线回溯 | fwctl（mainline 6.9+） | — | 可选回溯（非 openEuler 原创） |

### 4.2 既有目录下的厂商驱动

| 路径 | 厂商 | 硬件 | 规模 | 处置 |
|------|------|------|------|------|
| `drivers/net/ethernet/hisilicon/` | 海思/鲲鹏 | hns3/hns/hibmcge/hip04/hisi_femac/hix5hd2 | 363 文件, +148,628/-22,609 行（含 huawei） | **LAYER 提取** |
| `drivers/net/ethernet/huawei/` | 华为 | hinic3 | （含于上） | **LAYER 提取** |
| `drivers/perf/hisilicon/` | 海思/鲲鹏 | PMU（ummu_pmu 等） | 26 文件, +5,406/-881 行（含 alibaba） | **LAYER 提取** |
| `drivers/perf/alibaba_uncore_drw_pmu.c` | 阿里 | DRW PMU | （含于上） | **LAYER 提取** |
| `drivers/cpufreq/sunway-cpufreq.c` | 申威 | SW_64 频率调节 | 单文件 | **随 sw_64 架构导入** |

### 4.3 提取边界

**提取**：纯硬件驱动（NIC/PMU/cpufreq/总线/检测），不触及调度/安全/内存核心子系统。

**不提取**：
- `drivers/hooks/` 中的 tracepoint 钩子若触及核心调度/安全路径，需逐个甄别（仅保留硬件相关钩子）
- 任何依赖 `kernel/sched/grid/` 或 openEuler security/ 修改的驱动

---

## 5. 调度差异（kernel/sched/）—— 排除

### 5.1 OLK 调度增量

| 文件/目录 | 说明 | 处置 |
|-----------|------|------|
| `kernel/sched/grid/` | QoS 网格调度（Makefile/internal.h/power.c/qos.c/stat.c） | **排除**（与 sched_tac 冲突） |
| `kernel/sched/bpf_sched.c` | BPF 调度辅助 | **排除**（H5 纯 C 约束） |
| `kernel/sched/soft_domain.c` | 软域调度 | **排除** |
| `kernel/sched/sparsemask.h` | 稀疏位图工具 | **排除**（随 grid 使用） |
| `kernel/sched/smt_qos.c` | SMT QoS | **排除**（与 sched_tac 冲突） |

### 5.2 sched_ext 真实状态（一致性修正）

> **重要发现**：OLK-6.6 **不含** sched_ext。

| 检查项 | 结果 |
|--------|------|
| `kernel/sched/ext.c` 存在？ | **否**（`git show openeuler/OLK-6.6:kernel/sched/ext.c` → path does not exist） |
| `CONFIG_SCHED_EXT` in Kconfig？ | **否** |
| `kernel/sched/Makefile` 含 `ext.o`？ | **否** |
| `openeuler_defconfig` 含 `CONFIG_SCHED_EXT`？ | **否** |

**结论**：sched_ext 于 Linux 6.12 合入主线，6.6 LTS（vanilla 与 OLK-6.6）均不含。既有文档 `00-alk-kernel-overview.md` §2.2 item 3 称"OLK 6.6 backport 了 sched_ext"为**事实错误**，已在 P1-6 修正。

> **工程师参考目录警告**：`/home/spharx/.engineer-reference/kernel-OLK-6.6/` 工作树含 `kernel/sched/ext.c`，但其 `.git` remote 指向 `atomgit.com:openairymax/spharxworks.git`（非 openEuler），该工作树已被修改/污染，**不可作为 OLK-6.6 权威源**。权威源为 `openeuler/OLK-6.6` git ref。

---

## 6. 安全差异（security/）—— 排除

```
74 files changed, 2,839 insertions(+), 1,491 deletions(-)
```

OLK-6.6 修改 security/（LSM 框架、commoncap、landlock、yama 等）。Airymax 采用 vanilla security + `airy_lsm`（纯 C LSM），**不提取**任何 OLK security/ 修改。

---

## 7. 构建系统与 KABI —— 排除/剥离

### 7.1 Makefile.oever

openEuler 版本系统（OPENEULER_LTS/MAJOR/MINOR/RELEASE），注入 `OPENEULER_VERSION_CODE` 宏。**不提取**（Airymax 用 airy_defconfig + configs/defconfig{,-agent,-embedded}）。

### 7.2 KABI 标记

| 检查项 | 结果 |
|--------|------|
| `include/**/*.h` 含 KABI 标记 | 239 文件 |
| `.gen.o` KABI 占位符 | 0（OLK-6.6 未用旧式 .gen.o 机制） |

**处置**：提取硬件驱动补丁时，**剥离** KABI 标记（`__KABI_*` 宏、`.gen.o` 引用），保持 vanilla 头文件洁净。

---

## 8. LAYER 方案提取清单（汇总）

### 8.1 完整导入

| 项 | 路径 | 规模 |
|----|------|------|
| 申威架构 | `arch/sw_64/` | 352 文件, +54,093 行 |

### 8.2 驱动补丁提取（存入 `patches/euler/{x86,arm64,sw_64}/`）

| 厂商 | 硬件 | 源路径 | 目标架构 |
|------|------|--------|----------|
| 海思/鲲鹏 | hns3/hns NIC | `drivers/net/ethernet/hisilicon/` | arm64 |
| 华为 | hinic3 NIC | `drivers/net/ethernet/huawei/` | arm64, x86 |
| 海思/鲲鹏 | PMU | `drivers/perf/hisilicon/` | arm64 |
| 阿里 | DRW PMU | `drivers/perf/alibaba_uncore_drw_pmu.c` | x86, arm64 |
| 申威 | cpufreq | `drivers/cpufreq/sunway-cpufreq.c` | sw_64 |
| 跨厂商 | CPU SDC 检测 | `drivers/cpuinspect/` | x86, arm64 |
| 跨厂商 | Vendor Hooks | `drivers/hooks/`（仅硬件相关） | x86, arm64, sw_64 |
| 鲲鹏 | RDMA over HMEM | `drivers/roh/` | arm64 |
| 鲲鹏 | UnifiedBus | `drivers/ub/` | arm64 |
| 申威 | XCU | `drivers/xcu/` | sw_64 |

### 8.3 CONFIG 碎片（存入 `configs/euler_hw_{x86,arm64,sw64}.config`）

从 `arch/{x86,arm64,sw_64}/configs/openeuler_defconfig` 提取硬件相关 CONFIG 行，剔除调度/安全/调试项。

### 8.4 排除清单

| 项 | 原因 |
|----|------|
| `kernel/sched/grid/` + bpf_sched + soft_domain + smt_qos + sparsemask | 与 sched_tac 冲突 |
| `security/` 全部修改 | Airymax 用 vanilla + airy_lsm |
| `Makefile.oever` | Airymax 自有构建配置 |
| KABI 标记（239 头文件） | 保持 vanilla 头文件洁净 |
| `drivers/arm/`, `drivers/coda/`, `drivers/fwctl/` | 主线回溯，非 openEuler 原创（可选独立回溯） |

---

## 9. 一致性声明

1. **权威源**：本文档差异数据以 `openeuler/OLK-6.6` 与 `linux-stable/linux-6.6.y` 的 git diff 为唯一权威。工程师参考目录工作树已污染，不作权威源。
2. **sched_ext 事实**：OLK-6.6 与 vanilla 6.6.145 均不含 sched_ext（6.12 合入主线）。既有文档相关表述已在 P1-6 修正。
3. **BAN-INTERNAL-002**：本文档为闭源参考，不进入开源 `docs/AirymaxOS/`。开源架构文档以中性术语（"国产硬件驱动层"）引用，详见 `00-alk-kernel-overview.md` §3.1 与 [README.md 参考声明](../../docs/AirymaxOS/README.md)。
4. **IRON-7**：vanilla linux-stable 6.6.145 为唯一基线（v1.0.1），Euler 驱动层为硬件适配附加层，不改变核心子系统基线纯净性。
