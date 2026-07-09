Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# Linux 7.1 内核技术检索报告 — agentrt-linux 2.x.x 前瞻性设计输入

> **检索日期**：2026-07-09 ｜ **报告版本**：v1.0
> **信息基线**：kernel.org 官方发布表 + kernelnewbies.org/Linux_7.1 + LWN + Phoronix + Linux Journal（多方交叉验证）
> **适用对象**：agentrt-linux 2.x.x 版本前瞻性预留设计

---

## 1. 摘要与关键结论（TL;DR）

1. **Linux 7.1 已发布且为当前 stable**：Linus Torvalds 于 **2026-06-14** 发布 7.1.0，截至 2026-07-04 已迭代至 **7.1.3**；mainline 已推进至 **7.2-rc2**（2026-07-06）。
2. **Linux 7.0 已 EOL**：7.0 于 2026-04-12 发布，2026-06-27 EOL（仅维护约 2.5 个月，符合非 LTS 常规节奏）。
3. **版本编号 6.x → 7.x 的原因**：纯美学，与 Linus"指与趾计数"惯例相关——x.19 即终止该主版本，下一个直接跳 (x+1).0。**无任何架构性断裂**。6.19 是 6.x 末版（2026-02-08）。
4. **7.1 不是 LTS**。当前 LTS 链：6.18（至 2028-12）、6.12（至 2028-12）、**6.6（至 2027-12）**、6.1（至 2027-12）、5.15/5.10（至 2026-12）。agentrt-linux 当前基线 6.6 仍在 LTS 窗口内，但仅剩约 1 年 5 个月。
5. **对 agentrt-linux 2.x.x 最有价值的 7.1 能力**（按优先级）：① sched_ext cgroup 子调度器（直接服务于 per-cgroup 策略）；② BPF-powered io_uring + ublk zero-copy（服务于 I/O 路径）；③ clone3 三个新 flag + FSMOUNT_NAMESPACE + empty mntns（极大简化容器化）；④ Landlock UNIX socket hook（强化沙箱）；⑤ swap table phase III + hrtimer 重写（性能与实时性基础）。
6. **对 agentrt-linux 2.x.x 最具冲突性的变化**：① IPv6 不可再编译为模块（破坏嵌入式 defconfig 习惯）；② UDP-Lite / ISDN / AX.25 / hamradio / 486 子架构整体移除（140k+ 行）；③ Rust 工具链要求提升至 1.85 + bindgen 0.71.1；④ 7.2 将引入 Clang 17 最低要求与 Cache-Aware Scheduling。

---

## 2. Linux 7.1 发布状态（权威确认）

### 2.1 当前 kernel.org 官方状态（2026-07-09 实测）

| 通道 | 版本 | 发布日期 | 状态 |
|---|---|---|---|
| mainline | **7.2-rc2** | 2026-07-06 | 开发中 |
| stable | **7.1.3** | 2026-07-04 | 当前 stable |
| stable（EOL） | 7.0.14 | 2026-06-27 | 已 EOL |
| longterm | 6.18.38 | 2026-07-04 | LTS 至 2028-12 |
| longterm | 6.12.95 | 2026-07-04 | LTS 至 2028-12 |
| longterm | **6.6.144** | 2026-07-04 | **LTS 至 2027-12** |
| longterm | 6.1.177 | 2026-07-04 | LTS 至 2027-12 |
| longterm | 5.15.211 / 5.10.260 | 2026-07-04 | LTS 至 2026-12 |

来源：https://www.kernel.org/

### 2.2 关键日期确认

- **Linux 6.19**（6.x 末版）：2026-02-08 发布，2026-04-22 EOL。
- **Linux 7.0**：2026-04-12 发布；2026-06-27 EOL。
- **Linux 7.1**：2026-06-14 发布。
- **Linux 7.2**：merge window 2026-06-15 开启，stable 目标 2026-08 下旬。

### 2.3 版本编号规则（为何 6.x → 7.x）

Linus 在 6.19 公告中明确：

> "很多人已经察觉，我开始被大数字搞混了（手指和脚趾快数不过来了），所以下一个内核就叫 7.0。"

规则（自 3.x 起一致）：
- 每个主版本做到 **x.19** 结束（6.1→6.19 共 13 个小版本，约 3.5 年）
- 下一个直接跳 **(x+1).0**，**无技术性断裂**，纯"美学/计数"动机
- 历史轨迹：3.19→4.0、4.20→5.0、5.19→6.0、6.19→7.0

**重要澄清**：检索过程中发现 CSDN 一篇博客声称"Linux 7.0 引入 AI Subsystem Framework (AISF)、Pluggable Scheduler、Unified Device Model、Kbuild 2.0"等。这些**与 kernelnewbies/LWN/kernel.org/Phoronix 等权威源完全不符**，判定为 AI 生成的不实内容，**本报告不采纳**。

---

## 3. Linux 7.x 系列关键特性（对比 Linux 6.6 LTS）

### 3.1 调度器（Scheduler）

| 特性 | 引入版本 | 状态 |
|---|---|---|
| EEVDF 取代 CFS | 6.6 | 已稳定 |
| EEVDF 重大增强（避免优先级反转、proxy execution） | **7.0** | 已确认 |
| sched_ext（BPF 可编程调度类）主线化 | 6.12 | 已稳定 |
| **sched_ext cgroup 子调度器（初始）** | **7.1** | 已确认 |
| PREEMPT_LAZY 默认启用 | **7.0** | 已确认 |
| PREEMPT_RT 完全主线化 | 6.12 | 已稳定 |
| hrtimer 子系统重写（sched 可无损耗用高精度定时器） | **7.1** | 已确认 |
| SCX_ENQ_IMMED、DSQ reenqueue 重构、verifier-time kfunc 过滤 | **7.1** | 已确认 |
| Proxy Execution：Simple Donor Migration（部分合入） | **7.1** | 已确认（未完成） |
| Cache-Aware Scheduling（CONFIG_SCHED_CACHE） | 7.2（merge window） | 推测/预期 |

**对 agentrt-linux 的关键意义**：v0.2.0 审查文档验证项明确要求"`SCHED_AGENT` define 出现次数 = 0"，即**不自定义调度类、复用 sched_ext**。7.1 的 cgroup 子调度器使"per-cgroup 不同调度策略"成为可能，正好契合安全分级 + 容器隔离需求。

### 3.2 内存管理（MM）

| 特性 | 引入版本 | 状态 |
|---|---|---|
| MGLRU（Multi-Gen LRU）主线 | 6.1 | 已稳定 |
| MGLRU reclaim loop + dirty folio 优化（MongoDB +27.6%） | 7.1 周期 patch | 已确认 |
| **swap table phase I** | 6.18 | 已确认 |
| **swap table phase II** | **7.0** | 已确认 |
| **swap table phase III：移除 swap_map（节省 ~30% swap 元数据内存，1TB swap 省 256MB）** | **7.1** | 已确认 |
| THP 优化（GPU/CPU 共享内存对齐 2MB，DRM 映射提速 ~2x） | **7.0** | 已确认 |
| folio 体系持续深化（NTFS、ublk 等全面采用） | 7.0/7.1 | 已确认 |
| DAMON 智能内存监控持续增强 | 7.1 | 已确认 |
| CXL 内存分层、tiered memory migration（MIGRC 减少 TLB flush 94%） | 6.x 持续 | 部分进 7.1 |
| Arm MPAM（Memory Partitioning and Monitoring）暴露给用户态 | **7.1** | 已确认 |

### 3.3 eBPF / BPF

| 特性 | 引入版本 | 状态 |
|---|---|---|
| bpf_struct_ops 主线化 | 5.13+ | 已稳定 |
| bpf_struct_ops 演进（shadow vars、null args、多程序、模块内使用） | 6.x 持续 | 已稳定 |
| **BPF-powered io_uring（io_uring struct_ops，主调度循环可被 BPF 替换）** | **7.1** | 已确认 |
| BPF verifier 栈活跃性分析重写（大幅加速验证） | **7.1** | 已确认 |
| io_uring BPF 过滤（IORING_REGISTER_BPF_FILTER，classic BPF） | **7.0** | 已确认 |
| io_uring 零拷贝接收（IORING_OP_RECV_ZC，+37.8%~41.4%） | 6.15 / 7.0 完备 | 已确认 |

### 3.4 io_uring / 块层

| 特性 | 引入版本 | 状态 |
|---|---|---|
| **ublk 共享内存零拷贝 I/O（vm_insert_page，消除两次 memcpy）** | **7.1** | 已确认 |
| ublk Batch I/O Dispatch（syscall 开销 O(N)→O(N/32)） | **7.1** | 已确认 |
| T10 Protection Information 上移到文件系统层 | **7.1** | 已确认 |
| Btrfs shutdown ioctl 转正 | **7.1** | 已确认 |
| SED-OPAL 单用户模式增强 | **7.1** | 已确认 |
| networking HW queue leasing（容器原生 AF_XDP） | **7.1** | 已确认 |

### 3.5 文件系统

| 特性 | 引入版本 | 状态 |
|---|---|---|
| Bcachefs 主线化 | 6.7 | 已稳定 |
| **ntfsplus（全新 NTFS 重写，4 线程写比 ntfs3 快 35~110%）** | **7.1** | 已确认 |
| XFS 自愈（xfs_healer + XFS_IOC_HEALTH_MONITOR ioctl） | **7.0** | 已确认 |
| nullfs（不可变伪 FS） | **7.0** | 已确认 |
| Btrfs remap tree（实验性） | **7.0** | 已确认 |
| FSMOUNT_NAMESPACE / CLONE_EMPTY_MNTNS / UNSHARE_EMPTY_MNTNS | **7.1** | 已确认 |
| move_mount 支持 MOVE_MOUNT_BENEATH 直达 rootfs | **7.1** | 已确认 |

### 3.6 安全（LSM / Landlock / capability / crypto）

| 特性 | 引入版本 | 状态 |
|---|---|---|
| **Landlock 新增 UNIX domain socket pathname 访问权** | **7.1** | 已确认 |
| LSM hook 扩展到 overlay FS | **7.1** | 已确认 |
| /proc/PID/mem 默认权限收紧 | **7.1** | 已确认 |
| user.* xattr 支持 socket | **7.1** | 已确认 |
| **后量子密码 ML-DSA 集成到内核模块签名** | **7.0** | 已确认 |
| NTSYNC 驱动（Windows 游戏 Wine/Proton 同步原语） | **7.0** | 已确认 |
| Rust 正式"去实验"标签（permanent） | **7.0** | 已确认 |
| rv（runtime verification）Hybrid Automata 监视器 | **7.1** | 已确认 |
| KHO（kexec handover）+ liveupdate | **7.1** | 已确认 |

### 3.7 实时（Real-time）

| 特性 | 引入版本 | 状态 |
|---|---|---|
| PREEMPT_RT 完全主线化 | 6.12 | 已稳定 |
| PREEMPT_LAZY 与 PREEMPT_RCU 分离 | 6.13+ | 已稳定 |
| **PREEMPT_LAZY 默认启用** | **7.0** | 已确认 |
| 中断线程化成为 7.0 基础能力 | **7.0** | 已确认 |
| hrtimer 重写 | **7.1** | 已确认 |

### 3.8 AI / ML / NPU / GPU 调度

> **关键澄清**：主线 Linux 7.0/7.1 **没有**"AI Subsystem Framework"、"内核级 AI 预测引擎"、"NPU 调度类"等。AI 在 7.0/7.1 中的体现是**间接**的：

| 真实特性 | 引入版本 | 状态 |
|---|---|---|
| accel 子系统（drivers/accel/，major 261，DRM 衍生） | 6.2+ | 已稳定 |
| AMD NPU（amdxdna 驱动，XDNA 空间+时间混合调度） | 6.10+ 持续 | 已稳定 |
| DRM-RAS（GPU/accel 错误计数与可靠性数据暴露用户态） | **7.1** | 已确认 |
| AI 辅助 bug 查找（"new normal"） | **7.0** | 已确认（流程而非特性） |
| 键盘新增 3 个 AI agent 专用键 HID 编码 | **7.0** | 已确认 |

**对 agentrt-linux 的关键意义**：agentrt-linux 作为"AgentOS"若需 NPU/GPU 调度能力，应基于 accel 子系统 + DRM-RAS 构建用户态策略层，而非期待内核有"AI 调度类"。

### 3.9 架构支持

| 架构 | 7.0/7.1 关键变化 |
|---|---|
| x86 | Intel FRED 7.1 默认启用（替代 IDT）；486 子架构 7.1 移除；Intel Nova Lake 支持 |
| AMD | Zen 5 ERAPS（KVM）、Zen 6 性能事件、amd-pstate 动态性能偏好（7.1） |
| ARM64 | KVM 受保护虚拟化、虚拟 GIC v5、MPAM 暴露用户态、Arm 9.6 LSUI 加速 futex |
| RISC-V | 持续扩展（Qualcomm/Tenstorrent/ESWIN 新 SoC）；Rust 交叉编译支持 |
| LoongArch | 龙芯 3C6000 多核优化 |

---

## 4. Linux 6.6 → 7.1 迁移路径

### 4.1 已确认的 Breaking Changes

| 变化 | 版本 | 影响 |
|---|---|---|
| **IPv6 不可再编译为模块** | 7.1 | 嵌入式 defconfig 习惯破坏 |
| **UDP-Lite 协议移除** | 7.1 | 语音/多媒体/部分 IoT 栈受影响 |
| **486 子架构移除**（M486/M486SX/ELAN） | 7.1 | 140k+ 行代码删除 |
| **ISDN / AX.25 / CAIF / Bluetooth CMTP / hamradio 整体移除** | 7.1 | 旧协议栈用户需迁移 |
| 大量旧 Ethernet 驱动移除 | 7.1 | 旧 NIC 失支持 |
| buffer_head 逐步被 folio 取代 | 7.0/7.1 | out-of-tree 驱动需迁移 |
| inode->i_ino 类型 unsigned long → u64 | 7.1 | out-of-tree FS 驱动需适配 |
| Rust 工具链最低要求 **Rust 1.85 + bindgen 0.71.1** | 7.1 | 构建 Rust 内核代码需升级工具链 |
| kernel-doc 工具重写（C tokenizer 取代正则） | 7.1 | 文档构建流程变化 |
| 7.2 预期：最低 LLVM/Clang 由 15 升至 17 | 7.2 | 推测/已 merge |

### 4.2 新增稳定 ABI / 系统调用

| 新 ABI | 版本 | 价值 |
|---|---|---|
| clone3: CLONE_AUTOREAP（子进程退出自动 reap） | 7.1 | 简化进程生命周期管理 |
| clone3: CLONE_NNP（clone 时设 no_new_privs） | 7.1 | 安全加固 |
| clone3: CLONE_PIDFD_AUTOKILL（pidfd 关闭即杀子进程） | 7.1 | 容器/agent 生命周期绑定 |
| clone3: CLONE_EMPTY_MNTNS / unshare: UNSHARE_EMPTY_MNTNS | 7.1 | 单步创建空 mount namespace |
| fsmount: FSMOUNT_NAMESPACE | 7.1 | 单步挂载+新 mnt namespace |
| move_mount: MOVE_MOUNT_BENEATH | 7.1 | 免 pivot_root 切换 rootfs |
| io_uring struct_ops（BPF 控制主循环） | 7.1 | 可编程 I/O 调度 |
| XFS_IOC_HEALTH_MONITOR | 7.0 | XFS 健康监控 fd |
| fserror API（统一 I/O 错误经 fsnotify 上报） | 7.0 | 标准化错误上报 |

---

## 5. Linux 7.1 LTS 状态

### 5.1 权威结论

**Linux 7.1 不是 LTS。** 当前（2026-07-09）kernel.org 的 longterm 通道不包含任何 7.x 版本。LTS 选取惯例为"年末假期季发布"（6.18=2025-11、6.12=2024-11、6.6=2023-10）。7.1 发布于 2026-06，**不符合 LTS 选取时机**。

来源：https://www.kernel.org/category/releases.html

### 5.2 当前 LTS 全景与 EOL

| LTS | EOL | 与 agentrt-linux 关系 |
|---|---|---|
| 6.18 | 2028-12 | 候选升级目标（已稳定 7 个月） |
| 6.12 | 2028-12 | PREEMPT_RT/sched_ext 主线化的首个 LTS |
| **6.6** | **2027-12** | **agentrt-linux 当前基线，剩余 ~17 个月** |
| 6.1 | 2027-12 | Debian 12 基线 |
| 5.15 / 5.10 | 2026-12 | **5 个月内 EOL** |

### 5.3 推测：下一个 7.x LTS

按惯例，下一个 LTS 极可能为 **2026 年 11-12 月发布的 7.x**（按 9-10 周节奏：7.2≈8 月、7.3≈10 月、7.4≈12 月 / 7.5≈2027-02）。**最可能候选：7.4 或 7.5**。此为基于历史的推测，非官方确认。

---

## 6. 对 agentrt-linux 2.x.x 的影响

### 6.1 可简化 agentrt-linux 实现的 7.1 特性

| 7.1 特性 | 对应 agentrt-linux 模块 | 简化点 |
|---|---|---|
| sched_ext cgroup 子调度器 | security（安全分级）+ kernel（调度） | per-cgroup 调度策略无需自定义 SCHED_AGENT |
| clone3 CLONE_AUTOREAP/CLONE_NNP/CLONE_PIDFD_AUTOKILL | services（进程/容器管理） | agent 生命周期与 pidfd 绑定、自动 reap |
| FSMOUNT_NAMESPACE + CLONE_EMPTY_MNTNS + MOVE_MOUNT_BENEATH | services（容器） | 单步构造容器 mount 树，免 pivot_root |
| BPF-powered io_uring + ublk zero-copy | kernel（I/O 路径） | 用户态块设备性能追平内核驱动 |
| Landlock UNIX socket hook + user.* xattr on socket | security（沙箱）+ kernel（IPC） | IPC 端点可标注协议，eBPF 选择性抓包 |
| swap table phase III | kernel（内存） | 1TB swap 省 256MB 元数据内存 |
| hrtimer 重写 | kernel（实时性） | 调度器可无损耗用高精度定时器 |
| fserror + XFS 自愈 | services（FS） | 标准化 I/O 错误上报，XFS 挂载态自愈 |
| PREEMPT_LAZY 默认 + PREEMPT_RT 主线化 | kernel（实时） | 无需单独 RT 补丁树 |
| KHO + liveupdate | services（无停机升级） | kexec 保留状态，契合"无停机升级"诉求 |

### 6.2 可能与 agentrt-linux 设计冲突的 7.1 特性

| 冲突点 | 风险 | 缓解 |
|---|---|---|
| IPv6 不可编译为模块 | OLK-6.6 习惯的 `CONFIG_IPV6=m` 失效 | 迁移前做 defconfig 审计，强制 `CONFIG_IPV6=y` |
| UDP-Lite 移除 | 若用 UDP-Lite 做低开销传输需迁移 | 改用标准 UDP 或 io_uring zero-copy recv |
| 486/ISDN/AX.25 移除 | 旧硬件/旧协议支持丢失 | 评估目标硬件清单 |
| buffer_head → folio 迁移 | out-of-tree 驱动需重写 | 提前迁移自定义块驱动 |
| inode->i_ino 类型变更 | 自定义 FS 驱动需适配 u64 | 编译期静态检查 |
| Rust 1.85 + bindgen 0.71.1 | 构建 Rust 内核代码工具链升级 | 锁定工具链版本，CI 门禁 |
| 7.2 Clang 17 | 构建 LLVM 工具链升级 | 提前规划工具链基线 |
| 7.0 EEVDF proxy execution | 锁持有者行为变化可能影响实时性基准 | 重测实时性指标 |

### 6.3 迁移路径建议（基于 IRON 规则）

遵循 v0.2.0 的 IRON 规则（不引入未实现功能、不简化、不设计桩）——所有预留必须以"运行时能力探测 + 条件降级"实现：

1. **短期（2.x.x）**：保持 6.6 LTS 基线，但将 7.1 的关键 ABI（clone3 三 flag、FSMOUNT_NAMESPACE、Landlock socket hook、io_uring struct_ops）作为"前瞻性接口"在接口契约中预留（即设计兼容层，运行时探测内核版本能力）。
2. **中期（3.x.x）**：评估升级至 6.18 LTS（PREEMPT_RT/sched_ext 主线化，2028-12 EOL，过渡平稳）或 7.4/7.5 LTS（待 2026 末确认）。
3. **长期（4.x.x）**：全面拥抱 7.x，启用 sched_ext cgroup 子调度器、BPF-powered io_uring、ublk zero-copy 等作为一等公民。

---

## 7. agentrt-linux 2.x.x 前瞻性预留设计具体建议（10 条）

> 原则：遵循 IRON 规则——所有预留必须以"运行时能力探测 + 条件降级"实现，而非"假设未来内核一定有"。

1. **调度类复用 sched_ext，禁用 SCHED_AGENT 自定义类**。在调度接口契约中，将"调度策略"抽象为 BPF struct_ops 接口；当 7.1 cgroup 子调度器可用时启用 per-cgroup 策略，否则降级为单 sched_ext 实例。预留 `airymax_sched_ext_ops` 结构体，但**不在 2.x.x 默认启用** cgroup 子调度器（避免依赖未稳定 ABI）。

2. **进程生命周期 API 全面 pidfd 化**。进程/容器管理统一使用 pidfd + clone3；接口层预留 `CLONE_AUTOREAP | CLONE_NNP | CLONE_PIDFD_AUTOKILL` 三个 flag 的运行时探测（通过 `syscall(__NR_clone3, ...)` 返回 `EINVAL` 判定）。2.x.x 在 6.6 上降级为现有 pidfd 语义。

3. **容器 mount 树构造抽象为 `airymax_mount_ns_create()` 接口**。内部按内核能力分级：7.1 用 `FSMOUNT_NAMESPACE | CLONE_EMPTY_MNTNS` 单步完成；6.6 降级为 `open_tree(OPEN_TREE_NAMESPACE)` + `pivot_root`。容器 C 契约需预留"mount namespace 构造策略"枚举。

4. **io_uring + ublk 作为 I/O 一等公民**。在块 I/O 接口中，预留 `AIRYMAX_IO_URING_BPF` 与 `AIRYMAX_IO_UBLK_ZC` 两个能力位；策略裁决可通过 BPF struct_ops 注入 io_uring 主循环（7.1）。2.x.x 在 6.6 上降级为标准 io_uring（无 BPF 主循环）。zero-copy recv 在 6.15+ 可用，6.6 降级为标准 recv。

5. **Landlock 沙箱覆盖 UNIX socket**。沙箱策略层预留 `AIRYMAX_LANDLOCK_SOCKET` 能力位；当 7.1 socket hook 可用时启用 pathname UNIX socket 访问控制，否则仅覆盖文件系统。同时利用 7.1 的 `user.* xattr on socket` 实现 IPC 协议标注，协议注册表应预留 socket xattr 查询接口。

6. **后量子密码预留**。模块签名链预留 ML-DSA（FIPS 204）算法支持；7.0 已集成 ML-DSA 到内核模块签名，2.x.x 在 6.6 上降级为传统 RSA/ECDSA，但证书与签名格式应预留 PQ 混合签名扩展位。

7. **PREEMPT 模型运行时选择**。Kconfig 默认 `CONFIG_PREEMPT_LAZY=y`（对齐 7.0 默认），同时保留 `CONFIG_PREEMPT_FULL` 与 `CONFIG_PREEMPT_RT` 选项给工控/车载场景。在文档中明确三档抢占模型与 <10ms 实时响应目标的对应关系。

8. **NPU/GPU 调度基于 accel 子系统，不期待内核 AI 调度类**。agentrt-linux 的 NPU 调度能力应通过 `drivers/accel/` + DRM-RAS（7.1）构建用户态策略层，内核仅暴露 accel 设备的 sysfs/debugfs 接口。明确文档化"主线无 AI 调度类"，避免社区误导。

9. **构建工具链基线锁定与渐进升级**。工程标准应明确：2.x.x 锁定 Rust 1.85 + bindgen 0.71.1（7.1 基线）、Clang/LLVM 15（6.6/6.18 基线）；3.x.x 预留 Clang 17（7.2 基线）。checkpatch 规则映射需对齐 7.1 的 kernel-doc C tokenizer 重写带来的注释规范变化。

10. **版本能力探测框架**。在公共库层实现 `airymax_kernel_cap_query(cap_id)` 框架，集中管理所有 7.1/7.0/6.18/6.12/6.6 的能力探测（clone3 flags、FSMOUNT_NAMESPACE、Landlock socket hook、io_uring struct_ops、ublk zero-copy、ML-DSA、FRED、sched_ext cgroup sub-sched、PREEMPT_LAZY、KHO/liveupdate 等）。每个能力点配 `since` 标签与运行时探测函数 + 降级路径。这是 2.x.x 前瞻性预留的**总入口**，避免散落各模块的 `#ifdef` 污染。

---

## 8. 参考来源汇总

1. https://www.kernel.org/ — 官方版本与 LTS 状态
2. https://kernelnewbies.org/Linux_7.1 — 7.1 权威特性清单
3. https://kernelnewbies.org/Linux_7.0 — 7.0 权威特性清单
4. https://lwn.net/Articles/1067250/ — LWN 7.1 merge window
5. https://lwn.net/Articles/1067330/ — Linus 7.0 发布公告
6. https://lore.kernel.org/lkml/CAHk-=wi4BF4bMhZNZ1tqs+FFV4OuZRe3ZqdWB+LxRLmRweUzQw@mail.gmail.com/T/#u — Linus 7.1 发布公告
7. https://lwn.net/Articles/1059673/ — clone3 新 flag 详解
8. https://lwn.net/Articles/1062286/ — BPF comes to io_uring
9. https://lwn.net/Articles/1057102/ — swap_map 终结
10. https://lwn.net/Articles/972710/ — sched_ext 主线化
11. https://www.kernel.org/doc/html/latest/core-api/real-time/theory.rst.txt — PREEMPT_RT 官方文档
12. https://www.kernel.org/doc/html/v6.15/_sources/accel/introduction.rst.txt — accel 子系统官方文档
13. https://www.phoronix.com/news/Linux-7.1-Released — Phoronix 7.1 综述
14. https://www.linuxjournal.com/content/linux-kernel-71-officially-released-new-ntfs-driver-intel-fred-and-major-code-cleanup — Linux Journal 7.1（明确非 LTS）
15. https://linuxiac.com/linux-kernel-7-1-released-with-rewritten-ntfs-support/ — linuxiac 7.1
16. https://www.linuxteck.com/linux-kernel-7-1-release/ — 7.1 详解
17. https://eosl.date/eol/product/linux/ — LTS EOL 跟踪
18. https://www.techveda.live/2026/06/20/linux-7-1-and-7-2-three-changes-embedded-teams-should-plan-for/ — 嵌入式迁移影响
19. https://debugpointnews.com/linux-kernel-7-1-removes-major-legacy-ethernet-and-isdn-driver/ — 移除清单
20. https://byteiota.com/linux-7-iouring-bpf-filtering-zero-copy-developer-guide/ — io_uring BPF 过滤
21. https://xenospectrum.com/linux-kernel-7-0-release-rust-xfs-self-healing/ — 7.0 Rust 正式化
22. https://www.indiekings.com/2026/04/linux-70-released-rust-official-xfs.html — 7.0 特性综述

---

## 9. 结论

Linux 7.1 已于 2026-06-14 发布并稳定迭代（当前 7.1.3），但**不是 LTS**。agentrt-linux 当前基线 6.6 LTS 仍可用至 2027-12，时间窗口约 17 个月。建议 2.x.x **不立即迁移内核基线**，而是按本报告第七章 10 条建议进行"运行时能力探测 + 条件降级"式的前瞻性预留，重点复用 sched_ext（不自定义 SCHED_AGENT）、clone3 新 flag、FSMOUNT_NAMESPACE、io_uring struct_ops、Landlock socket hook、ublk zero-copy 等 7.1 能力。3.x.x 评估升级至 6.18 LTS 或 7.4/7.5 LTS（待 2026 末确认）。所有预留必须遵循 IRON 规则——可探测、可降级、不引入未实现功能、不留桩。

---

> **文档结束** | Linux 7.1 内核技术检索报告 v1.0 | 2026-07-09

Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
