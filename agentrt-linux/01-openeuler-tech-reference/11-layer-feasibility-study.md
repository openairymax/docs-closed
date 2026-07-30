Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# LAYER 方案可行性论证（vanilla 6.6.145 + openEuler 硬件适配层）

> **保密级别**: SPHARX Ltd 内部参考，**闭源不公开**
> **版本**: 1.0.0
> **最后更新**: 2026-07-30
> **适用范围**: AirymaxOS 架构委员会 + 内核开发组
> **前置文档**: [10-olk66-vanilla-diff.md](10-olk66-vanilla-diff.md)（OLK-6.6 与 vanilla 差异对比 SSoT）

---

## 0. 方案概述

**LAYER 方案**：以 vanilla linux-stable 6.6.145 为唯一核心基线（IRON-7），在其上叠加**复用openEuler的硬件适配能力**形成的国产硬件驱动层。驱动层与 agentrt-linux 微内核化改造补丁正交，仅触及 `drivers/`、`arch/` 硬件适配，不触及调度/安全/IPC/内存核心子系统。

```
ALK-6.6 = vanilla 6.6.145 (IRON-7 基线)
         + openEuler 硬件适配层（LAYER，架构可选）
         + agentrt-linux 微内核化改造补丁（≤ 2 万行）
```

本文档从**技术、维护、法律、工程**四个维度论证此方案可行性。

---

## 1. 技术可行性

### 1.1 正交性验证（核心论据）

LAYER 方案的技术基石是"驱动层与核心子系统正交"。根据 [10-olk66-vanilla-diff.md](10-olk66-vanilla-diff.md) 的逐文件差异分析，此正交性已验证：

| 子系统 | openEuler 修改 | LAYER 处置 | 正交性 |
|--------|---------------|-----------|--------|
| `kernel/sched/`（grid/bpf_sched/soft_domain/smt_qos） | 有 | **排除**（与 sched_tac 冲突） | ✓ 不提取 |
| `security/`（74 文件 LSM/capability/landlock） | 有 | **排除**（Airymax 用 vanilla + airy_lsm） | ✓ 不提取 |
| `drivers/`（NIC/PMU/cpufreq/总线/检测） | 有 | **提取** | ✓ 纯硬件驱动 |
| `arch/sw_64/`（申威架构，352 文件） | 有 | **完整导入** | ✓ vanilla 不含 |
| `Makefile.oever`（版本系统） | 有 | **排除** | ✓ 构建系统隔离 |
| KABI 标记（239 头文件） | 有 | **剥离** | ✓ 头文件洁净 |

**结论**：openEuler 对核心子系统（调度/安全）的修改被完全排除，提取的仅是纯硬件驱动与架构代码。驱动代码通过标准 Linux 驱动模型（device/driver/bus）接入，与核心子系统通过既定接口交互，不改变核心子系统行为。

### 1.2 驱动独立编译可行性

LAYER 提取的驱动均为标准 Linux 内核模块，依赖关系清晰：

| 驱动类 | 依赖 | 是否触及核心子系统 |
|--------|------|-------------------|
| hns3/hinic3 NIC | `CONFIG_NET_VENDOR_HISILICON` | 否（标准 netdev 接口） |
| 海思/阿里 PMU | `CONFIG_PERF_EVENTS` | 否（标准 perf 接口） |
| sunway-cpufreq | `CONFIG_CPU_FREQ` | 否（标准 cpufreq 接口） |
| cpuinspect | `CONFIG_SYSFS && 64BIT` | 否（标准 sysfs 接口） |
| ROH/UB | `CONFIG_ARM64` | 否（鲲鹏专用总线） |
| Vendor Hooks | `CONFIG_TRACEPOINTS` | 需甄别（仅保留硬件相关钩子） |

**风险点**：`drivers/hooks/` 的 Vendor Hooks 是 openEuler 原创的 tracepoint 钩子框架，部分钩子可能触及核心调度/安全路径。提取时需逐个甄别，仅保留硬件相关钩子，排除触及 `kernel/sched/` 或 `security/` 的钩子。

### 1.3 版本对齐验证

| 维度 | vanilla | OLK-6.6 | 对齐情况 |
|------|---------|---------|---------|
| 基线版本 | 6.6.145 | 6.6.0 + backport | OLK-6.6 最新 tip `4e4aa165b` 已 backport 6.6.143-6.6.144 LTS 补丁 |
| LTS 支持窗口 | 2027-12（延长后） | 跟随 openEuler 24.03 LTS SP 节奏 | 覆盖 AirymaxOS 1.x.x 全生命周期 |
| 架构覆盖 | 22 架构 | +sw_64（申威） | sw_64 由 LAYER 补充 |

**关键发现**：openEuler 24.03 LTS 当前内核版本为 `kernel-6.6.0-145.0.8.135`（安全公告 openEuler-BA-2026-1011 确认），与 AirymaxOS 选择的 vanilla 6.6.145 在 `6.6.0-145` 段完全对齐。这意味着 openEuler 的硬件适配补丁天然适用于 6.6.145 基线，无需版本迁移。

### 1.4 sched_ext 事实确认

经 [10-olk66-vanilla-diff.md §5.2](10-olk66-vanilla-diff.md) 验证：OLK-6.6 与 vanilla 6.6.145 **均不含 sched_ext**（sched_ext 于 Linux 6.12 合入主线）。因此 LAYER 方案不存在 sched_ext 与 sched_tac 的冲突风险。

### 1.5 技术可行性结论

**可行**。正交性已逐文件验证，驱动独立编译依赖清晰，版本天然对齐，无 sched_ext 冲突。唯一需注意的是 `drivers/hooks/` 的逐个甄别。

---

## 2. 维护可行性

### 2.1 上游同步策略

LAYER 方案涉及三个上游源，同步策略各异：

| 上游源 | 同步频率 | 同步方式 | 冲突风险 |
|--------|---------|---------|---------|
| vanilla linux-stable 6.6.y | 每月（LTS 补丁） | fast-forward merge 到 ALK-6.6-upstream | 极低（纯基线更新） |
| openEuler OLK-6.6 | 每季度（SP 版本） | cherry-pick 硬件驱动补丁到 `patches/hw-vendor/` | 低（驱动代码与核心子系统正交） |
| agentrt-linux 自有补丁 | 持续 | ALK-6.6-dev 分支开发 | 无（自有代码） |

**关键优势**：由于 ALK 采用"只新增文件"策略（微内核化改造补丁不修改 Linux 主线源码），且 LAYER 驱动补丁仅触及 `drivers/`、`arch/`，三者合并冲突概率极低。唯一潜在冲突点在 `MAINTAINERS`、`Makefile`、`Kconfig` 等顶层文件。

### 2.2 vanilla LTS 升级时的驱动层迁移

当 vanilla 6.6.y 发布新的 LTS 补丁时：

1. `ALK-6.6-upstream` fast-forward 到新版本（纯基线更新，无冲突）
2. `ALK-6.6` merge `ALK-6.6-upstream`（生成 merge commit，自有补丁保留）
3. LAYER 驱动补丁无需迁移——LTS 补丁主要修复 bug/安全漏洞，不改变驱动接口
4. 若 LTS 补丁触及驱动接口（极罕见），对应驱动补丁需同步更新

**风险评估**：Linux LTS 补丁触及 `drivers/` 接口变更的概率 <5%（基于历史 LTS 补丁统计）。即便触及，由于驱动代码独立，修复成本可控。

### 2.3 openEuler 上游跟踪

openEuler 24.03 LTS 的维护节奏：
- **SP1**（2024-12）：24.03 LTS 增强版
- **SP2**（2025-06预期）：持续硬件适配更新
- **SP3/SP4**：后续维护

AirymaxOS 跟踪 openEuler SP 版本的硬件驱动增量，通过 `git diff` 识别新增/修改的驱动文件，cherry-pick 到 `patches/hw-vendor/`。

**维护成本估算**：每季度约 2-5 人日（diff 分析 + cherry-pick + 编译验证）。

### 2.4 长期演进（6.6 → 7.1 迁移）

当 AirymaxOS 从 1.x.x（6.6 LTS）升级到 2.x.x（Linux 7.1）时：

| 迁移项 | 难度 | 说明 |
|--------|------|------|
| 微内核化改造补丁 | 中 | 需适配 7.1 API 变更（folio/buffer_head 等） |
| LAYER 驱动层 | 低 | 驱动接口在 7.1 仍兼容；openEuler 也会发布 7.1 基线版本 |
| [SC] 共享契约层 | 低 | UAPI 头文件跨版本稳定 |

**结论**：LAYER 驱动层在版本迁移中风险最低，因为 openEuler 会同步发布新内核基线的驱动适配。

### 2.5 维护可行性结论

**可行**。三上游同步策略清晰，冲突概率低，维护成本可控（每季度 2-5 人日）。长期演进时 LAYER 驱动层风险最低。

---

## 3. 法律可行性

### 3.1 许可证兼容性

| 组件 | 许可证 | 兼容性 |
|------|--------|--------|
| Linux 内核（vanilla） | GPL-2.0 | 基线 |
| openEuler OLK-6.6 | GPL-2.0（与 Linux 内核一致） | ✓ 完全兼容 |
| AirymaxOS [SC] 头文件 | GPL-2.0-only WITH Linux-syscall-note | ✓ syscall-note 允许用户态引用 |
| AirymaxOS 微内核化改造补丁 | GPL-2.0（内核态代码） | ✓ 与基线一致 |

**法律依据**：
- openEuler 内核托管于 OpenAtom Foundation，使用 GPL-2.0 许可证（与 Linux 内核上游一致）
- GPL-2.0 允许复用、修改、分发，条件是：(1) 保持相同许可证 (2) 公开修改后的源码 (3) 标注变更说明
- AirymaxOS 作为 GPL-2.0 衍生作品，发布时须公开全部源码（含微内核化改造补丁 + LAYER 驱动补丁）

### 3.2 合规要求

AirymaxOS 复用 openEuler 硬件适配能力时须满足：

1. **版权声明保留**：所有 openEuler 驱动文件的 `Copyright (c) Huawei Technologies Co., Ltd` 等原始版权声明必须保留
2. **变更标注**：对 openEuler 驱动文件的任何修改须在文件头或 commit message 中标注
3. **SPDX 标识**：所有文件保持 `// SPDX-License-Identifier: GPL-2.0` 标识
4. **源码公开**：AirymaxOS 发布时，LAYER 驱动补丁须与微内核化改造补丁一同公开（GPL-2.0 强 copyleft 要求）
5. **Signed-off-by**：cherry-pick openEuler 补丁时保留原始 `Signed-off-by` 链，AirymaxOS 提交者追加自己的 `Signed-off-by`（DCO 认证）

### 3.3 闭源与开源边界

| 内容 | 开源/闭源 | 依据 |
|------|----------|------|
| "复用openEuler的硬件适配能力"表述 | **开源** | BAN-INTERNAL-002 硬件适配语境豁免（新政策） |
| LAYER 提取的驱动源码 | **开源**（GPL-2.0 要求） | 发布时必须公开 |
| 驱动提取的逐文件差异数据 | **闭源** | BAN-INTERNAL-002（内部参考，非 GPL 强制要求） |
| 微内核化改造补丁源码 | **开源** | GPL-2.0 要求 |

### 3.4 法律可行性结论

**可行**。openEuler 与 Linux 内核同为 GPL-2.0，许可证完全兼容。合规要求明确（版权保留/变更标注/源码公开/DCO 认证），无法律障碍。

---

## 4. 工程可行性

### 4.1 提取流程

LAYER 驱动补丁的提取流程（已部分落地于 [10-olk66-vanilla-diff.md](10-olk66-vanilla-diff.md)）：

```
1. git diff linux-stable/linux-6.6.y openeuler/OLK-6.6 -- <驱动路径>
2. 生成补丁文件 → patches/hw-vendor/{x86,arm64,sw_64}/
3. 剥离 KABI 标记（__KABI_* 宏、.gen.o 引用）
4. 剥离 Makefile.oever 依赖
5. 编译验证（make openeuler_defconfig + 驱动模块编译）
6. 存入 configs/euler_hw_{x86,arm64,sw64}.config（CONFIG 碎片）
```

### 4.2 构建系统复用

根据编译烧录方案调研（详见 [12-build-and-flash-strategy.md](12-build-and-flash-strategy.md)），AirymaxOS 构建系统全面复用 openEuler：

| 构建环节 | 复用 openEuler 能力 | AirymaxOS 适配 |
|---------|-------------------|---------------|
| defconfig | `openeuler_defconfig` 作为底座 | 叠加 `configs/defconfig{-agent,-embedded}` fragment |
| RPM 打包 | `kernel.spec` 模板 + 5 包拆分规则 | 改名 `airy-kernel.spec` |
| 镜像构建 | imageTailor（服务器）/ Yocto（嵌入式） | `custom/cfg_airymax/` 配置 |
| CI/CD | OBS（Open Build Service） | `AirymaxOS:Factory` 项目 |
| 安装部署 | Anaconda + Kickstart | 改 ks.cfg + 品牌 |

**关键优势**：6.6.0-145 版本天然对齐，无需 fork openEuler 构建工具链，采用"叠加层 + 配置覆盖"模式。

### 4.3 测试策略

| 测试层 | 方法 | 覆盖 |
|--------|------|------|
| 驱动编译测试 | `make M=drivers/<vendor>` 模块编译 | 所有 LAYER 驱动 |
| 架构编译测试 | `make openeuler_defconfig` + 全量编译 | x86/arm64/sw_64 |
| 硬件兼容测试 | 目标硬件实机启动 + 驱动加载 | 鲲鹏/飞腾/海光/申威 |
| 核心子系统纯净性 | `git diff --stat` 验证不触及 kernel/sched/ security/ | 正交性保障 |
| 回归测试 | KUnit + kselftest + LTP | 微内核化改造无回归 |

### 4.4 工程可行性结论

**可行**。提取流程已部分落地，构建系统全面复用 openEuler（叠加层模式），测试策略覆盖编译/硬件/纯净性/回归四维度。

---

## 5. 风险与缓解

| # | 风险 | 等级 | 缓解措施 |
|---|------|------|---------|
| 1 | `drivers/hooks/` Vendor Hooks 触及核心路径 | 中 | 逐个甄别，仅保留硬件相关钩子，排除触及 sched/security 的钩子 |
| 2 | openEuler SP 版本引入与 sched_tac 冲突的调度驱动 | 低 | 每季度 diff 审查，冲突项排除 |
| 3 | KABI 标记剥离不彻底导致头文件污染 | 低 | CI 门禁：`grep -r '__KABI' include/` 零命中 |
| 4 | LTS 补丁触及驱动接口 | 低 | 驱动代码独立，修复成本可控 |
| 5 | GPL-2.0 合规疏漏 | 低 | CI 门禁：SPDX 标识检查 + Signed-off-by 链验证 |
| 6 | openEuler 上游停止 OLK-6.6 维护 | 低 | 24.03 LTS 支持至 2029+，且有 atomgit/gitee 多镜像 |

---

## 6. 结论

| 维度 | 结论 | 信心 |
|------|------|------|
| 技术可行性 | **可行**——正交性逐文件验证，版本天然对齐 | 高 |
| 维护可行性 | **可行**——三上游同步清晰，每季度 2-5 人日 | 高 |
| 法律可行性 | **可行**——GPL-2.0 完全兼容，合规要求明确 | 高 |
| 工程可行性 | **可行**——提取流程落地，构建系统复用 openEuler | 高 |

**总体结论**：LAYER 方案（vanilla 6.6.145 + 复用openEuler的硬件适配能力）在技术、维护、法律、工程四维度均**可行**，建议正式采纳为 AirymaxOS 1.x.x 系列的硬件适配方案。

---

## 7. 引用

1. [10-olk66-vanilla-diff.md](10-olk66-vanilla-diff.md) — OLK-6.6 与 vanilla 6.6.145 差异对比 SSoT
2. openEuler 24.03 LTS 安全公告 openEuler-BA-2026-1011（kernel-6.6.0-145 版本确认）
3. Linux 6.6 LTS 支持延长至 2027-12（kernel.org 公告）
4. GPL-2.0 许可证全文（https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt）
5. openEuler OpenAtom Foundation 治理文档（https://www.openeuler.org/zh/）
