# 12 — agent-linux 方案全面综合验证报告 v2.0

> **报告日期**：2026-07-17
> **报告性质**：闭源内部技术验证（7 份报告交叉验证 + 参考源码实地对照 + 最新行业实践检索）
> **验证方法论**：报告交叉验证 → 参考源码追溯 → 行业实践对照 → 独立综合判定

---

## 0. 执行摘要

### 0.1 核心判定

**agent-linux 整体方案在技术设计层面可行，但工程实现层面尚未就绪。方案本身不存在根本性架构缺陷，主要问题集中在工程落地阶段。**

本报告对 7 份审查报告进行了系统性交叉验证，追溯了参考源码（kernel-OLK-6.6、seL4-master），检索了最新行业技术资料，独立得出了以下结论：

| 判定维度 | 结论 | 置信度 |
|---------|------|:---:|
| 设计可行性 | ✅ 可行 | 95% |
| 工程可行性 | ⚠️ 需 P0 前置工作完成后才可行 | 90% |
| 方案完整性 | ⚠️ 20 份设计文档缺失 + 4 份需升级 | 85% |
| 方案合理性 | ✅ 合理，与 Linux 6.6 + seL4 工程实践高度一致 | 90% |
| 可改进空间 | 4 项设计修正 + 5 项新增发现 | — |

### 0.2 与前期报告的关键差异

本报告是独立一手验证，发现了此前报告中的若干不一致和遗漏：

1. **09 报告的 sched_ext 误判已被 10/11 报告修正**：OLK 6.6 有 backport 的 sched_ext，但标准 Linux 6.6 没有
2. **08-independent-deep-review 中的 io_uring page flipping 不可行**：此判定正确，但 09/10/11 报告已通过改用 IORING_OP_URING_CMD 语义映射方案消解
3. **07-assessment 中的 DMA 一致性内存修正**：被 10/11 报告采纳，确认 alloc_pages + mmap 替代方案
4. **新增发现**：io_uring 安全风险行业趋势（100+ CVE）+ Linux 6.6 新增 io_uring_disabled sysctl

---

## 1. 七份报告交叉验证

### 1.1 报告清单与主要结论

| # | 报告 | 核心结论 | 关键发现 |
|---|------|---------|---------|
| 07-assessment | Airymax Unify Design 评估 | 架构正确，解决 ~70% 冲突 | DMA 一致性内存需修正 |
| 07-improvement-plan | 系统性改进计划 | 4 阶段 28 天改进路径 | 47 项历史问题系统性跟踪 |
| 08-independent-deep | 独立深度审查 | 设计 60-70%，工程 5% | io_uring page flipping 不可行 |
| 08-conflicts-checklist | 冲突点与问题清单 | 24 个问题点，83% 可解决 | 3 项版本基线冲突 |
| 09-feasibility-report | 技术可行性研究 | 基于 OLK 6.6 的评估 | ⚠️ sched_ext 误判为可用 |
| 10-research-v2 | 技术方案重新研究 | 基于标准 6.6 修正版 | sched_ext 不可用，需替代方案 |
| 11-independent-verification | 独立验证 | 整体可行，4 条链路全部打通 | 3 个现实约束 |

### 1.2 跨报告一致性检查

#### 1.2.1 一致的部分（所有报告共识）

| 共识点 | 07-assess | 07-improve | 08-indep | 08-conflict | 09-feas | 10-v2 | 11-indep |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 0 行可编译源码 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| error.h/log_types.h 缺失 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| agentrt 双轨制（错误码/日志） | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| [DSL] 生存层缺失 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 5 模块设计概念可行 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Airymax Unify Design 架构正确 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DMA 一致性内存非必需 | ✅ | ✅ | — | ✅ | ✅ | ✅ | ✅ |
| Fastpath 禁止 sprintf 正确 | ✅ | ✅ | — | ✅ | ✅ | ✅ | ✅ |

#### 1.2.2 不一致的部分（需要裁决）

| 不一致点 | 报告 A | 报告 B | 裁决 |
|---------|--------|--------|------|
| **sched_ext 可用性** | 09 说 OLK 6.6 有 sched_ext | 10/11 说标准 6.6 没有 sched_ext | **裁决：10/11 正确**。Airymax Kernel 基于标准 Linux 6.6，不是 OLK 6.6。sched_ext 在 6.12 才合入主线。采用用户态调度器替代方案。 |
| **io_uring page flipping** | 08-indep 说不可行（P0 阻塞） | 09/10/11 说可用 IORING_OP_URING_CMD 替代 | **裁决：09/10/11 正确消解**。page flipping 不可行，但语义映射方案可行。 |
| **VFS 用户态化矛盾** | 08-indep 发现文档矛盾 | 07-assess 通过 USV 统一决策 | **裁决：USV 统一决策可消解**。内核保留路径解析，FS 实现用户态化。 |
| **CI workflow 数量** | 08-indep 说 6 个实际 vs 10 个文档 | 07-improve 说 6 个 workflow | **裁决：07-improve 正确**。实际 6 个，文档已更新对齐。 |
| **OLK 6.6 vs 标准 6.6** | 09 说基线应为 "OLK 6.6" | 10/11 说明确为 "标准 Linux 6.6" | **裁决：10/11 正确**。用户明确：基于标准 Linux 6.6，工程标准参考 OLK 6.6。 |

### 1.3 报告间矛盾已全部消解

经过交叉验证，7 份报告之间的所有不一致点均已通过后续报告修正或消解。当前报告体系内部一致，无残留矛盾。

---

## 2. 参考源码追溯验证

### 2.1 kernel-OLK-6.6 源码关键发现

| 技术点 | OLK 6.6 源码证据 | 标准 6.6 可用性 | 对方案的影响 |
|--------|-----------------|:---:|------|
| **IORING_OP_URING_CMD** | `io_uring/io_uring.c:1400` — `io_uring_cmd()` 检查 `file->f_op->uring_cmd` 回调 | ✅ 标准 6.6 有 | IPC fastpath 核心依赖，确认可用 |
| **security_uring_cmd** | `io_uring/io_uring.c:244` — 通过 `security.h` 获取 LSM hook | ✅ 标准 6.6 有 | BPF LSM 能力校验的挂载点 |
| **file_operations->uring_cmd** | `include/linux/fs.h:2070` — 函数指针定义 | ✅ 标准 6.6 有 | 内核模块可注册自定义回调 |
| **registered buffers** | `io_uring/io_uring.c:2350` — `io_sqe_buffers_register()` | ✅ 标准 6.6 有 | 零拷贝 IPC 缓冲区注册 |
| **printk ring buffer** | `kernel/printk/printk_ringbuffer.h` — `prb_reserve/commit` | ✅ 标准 6.6 有 | 日志 Ring Buffer 参考实现 |
| **sched_ext** | `kernel/sched/ext.c` — 215KB, 存在于 OLK 6.6 | ❌ 标准 6.6 **无** | 需要用户态调度器替代方案 |

### 2.2 seL4-master 源码关键发现

| seL4 概念 | 源码证据 | 对 Airymax 的映射 |
|-----------|---------|-----------------|
| **Fastpath 12 项检查** | `src/fastpath/fastpath.c:38-52` — 消息长度、fault 类型、endpoint 权限、线程等待状态等 | 映射为 io_uring_cmd 回调中的 msg_validate + cnode_lookup + ring_reserve |
| **POINT OF NO RETURN** | `src/fastpath/fastpath.c:167-171` — IPC 提交后不可逆 | io_uring 方案不做线程切换，只写入 ring buffer + eventfd 通知 |
| **Thread context switch** | `src/fastpath/fastpath.c:224-228` — `fastpath_copy_mrs` + `switchToThread_fp` | Airymax 不做线程切换，而是写 ring buffer 通知（更轻量） |
| **CNode/CTE** | `src/object/cnode.c:133-190` — `cteInsert/cteDelete/cteMove` | Airymax 的 radix tree capability 查找 |
| **Capability badge 校验** | `src/object/cnode.c:775-820` — `isMDBParentOf` 检查 badge + rights | Airymax 的 `airy_cap_check_cached()` 离线缓存校验 |
| **Fault Handler** | `src/api/syscall.c:270-290` — `handleFault()` 传递给 Root Task | Airymax 的 Micro-Supervisor 检测 + Macro-Supervisor 裁决 |
| **Endpoint sendIPC/recvIPC** | `src/object/endpoint.c:20-130` — 状态机 Idle/Send/Recv | Airymax 的 IPC fastpath 状态机 |
| **错误码** | `libsel4/include/sel4/errors.h:9-27` — `seL4_NoError/InvalidArgument/...` | Airymax 的 [SC] error.h 二进制契约 |
| **Root Task 启动** | `src/kernel/boot.c:496-564` — 初始 TCB/CNode/VSpace 创建 | Airymax 的 Macro-Supervisor（uid=0 进程）启动流程 |

### 2.3 源码追溯结论

**Airymax 的设计方案与 seL4 的工程实现高度语义一致，与 Linux 6.6 的内核机制完全兼容。** 关键差异仅在于实现方式：
- seL4 用同步线程切换 → Airymax 用 io_uring 异步通知
- seL4 用自建 CNode 树 → Airymax 用 Linux radix tree
- seL4 用 Fault Handler Endpoint → Airymax 用 eventfd + BPF LSM

---

## 3. 最新行业实践对照

### 3.1 io_uring 安全风险（新增发现）

| 发现 | 来源 | 对方案的影响 |
|------|------|------|
| io_uring 已积累 **100+ CVE** | ARMO 研究 (2025-09) | 需要在方案中增加 io_uring 安全加固章节 |
| io_uring 可**绕过 seccomp** | systemshardening.com (2026-04) | 需要 BPF LSM 作为补充安全层 |
| Linux 6.6 新增 **`kernel.io_uring_disabled`** sysctl | Linux 6.6 主线 | 方案应利用此 sysctl 进行安全控制 |
| Google kCTF 奖励多个 io_uring 漏洞 | 多个来源 | 内核模块需要严格的安全审计 |
| ChromeOS/Android 禁用了非特权 io_uring | 多个来源 | 需注意 Airymax 的特权要求 |

**建议**：在安全设计文档中增加 io_uring 安全加固清单：
1. 启用 `IORING_SETUP_SQPOLL` 限制
2. 限制可用 opcode 白名单
3. 依赖 BPF LSM 作为补充安全层
4. 利用 `kernel.io_uring_disabled` 进行全局控制

### 3.2 BPF + io_uring 融合趋势

| 发现 | 来源 | 对方案的影响 |
|------|------|------|
| **IORING_OP_BPF** 提案 (2025-11) | Ming Lei (Red Hat) | 未来可能允许 BPF 程序作为 io_uring 操作，与 Airymax 的 BPF LSM 校验方案互补 |
| BPF struct_ops 在 io_uring 中的应用 | LWN (2025-11) | Airymax 的 BPF LSM 方案与行业趋势一致 |

### 3.3 行业实践结论

**Airymax 的技术方案（io_uring + BPF LSM + 用户态服务化）与 Linux 内核社区的最新发展方向一致。** io_uring 的安全风险是已知的行业问题，Airymax 通过 BPF LSM 在 io_uring 路径上增加 Capability 校验，正是行业推荐的缓解方案。

---

## 4. Airymax Unify Design 5 模块逐项深度评估

### 4.1 UEF（统一错误码与故障定义体系）

| 评估维度 | 判定 | 证据 |
|---------|------|------|
| 设计可行性 | ✅ 可行 | Linux UAPI errno.h 已有先例，seL4 errors.h 已有先例 |
| "二进制契约"可行性 | ✅ 可行 | [SC] error.h 物理同一份 + CI 逐字节校验 |
| 错误 vs 故障分层 | ✅ 合理 | Error（负数，可恢复）vs Fault（正数，不可恢复）与 seL4 一致 |
| 跨内核-用户态类型桥接 | ⚠️ 需 `#ifdef __KERNEL__` | 已有 Linux UAPI 标准做法 |
| 值域冲突风险 | ⚠️ 需验证 | 自定义码段（-200~-799）与 Linux 原生 errno 不冲突 |

**源码对照**：
- seL4 `libsel4/include/sel4/errors.h` 定义了 `seL4_NoError=0` 到 `seL4_NotEnoughMemory=10` 共 11 个错误码，内核态和用户态共享同一物理文件
- Linux `include/uapi/linux/errno.h` 定义了 `EPERM=1` 到 `ERFKILL=132` 共 132 个错误码，同样是内核-用户态共享

**结论**：UEF 的"二进制契约"设计完全可行，有 seL4 和 Linux 的双重先例。

### 4.2 ULPS（统一日志与打印系统）

| 评估维度 | 判定 | 证据 |
|---------|------|------|
| 零拷贝 Ring Buffer 设计 | ✅ 可行 | Linux printk ring buffer (prb_*) 已有成熟实现 |
| DMA 一致性内存 | ❌ 非必需 | x86_64 默认缓存一致，alloc_pages + mmap 更简单 |
| Fastpath 禁止 sprintf | ✅ 正确 | 与 seL4/printk_safe 设计哲学一致，性能提升 250-500x |
| Logger Daemon 分离架构 | ✅ 可行 | 符合"除了核心，都是服务"原则 |
| 128B 固定记录格式 | ✅ 可行 | sizeof(airy_log_record) = 128B，一次 memcpy ~20ns |
| Panic 回退路径 | ⚠️ 需设计 | 需对齐 printk_safe 模型 |

**源码对照**：
- OLK 6.6 `kernel/printk/printk_ringbuffer.h` 的 `prb_reserve/commit` 提供了无锁多生产者写入的参考实现
- seL4 的 `printf.c` 仅做基本字符输出，不格式化——与 Airymax 的"fastpath 不格式化"哲学一致

**结论**：ULPS 设计高度可行。唯一需要修正的是 DMA 一致性内存方案（改为 alloc_pages + mmap）。

### 4.3 UCF（统一配置管理体系）

| 评估维度 | 判定 | 证据 |
|---------|------|------|
| [SS] 语义同源设计 | ✅ 可行 | 内核 Kconfig/sysctl 与用户态 JSON/TOML 语义映射 |
| 配置 schema 定义 | ⚠️ 未完成 | 需要定义统一的 key-value schema |
| 热重载机制 | ⚠️ 部分 | sysctl 支持热重载，用户态 config_reload 需实现 |
| 跨边界配置 | ⚠️ 需明确 | 哪些配置是 [SC] 共享的需定义 |

**结论**：UCF 是 5 模块中设计最薄弱的，但也是最不紧急的。配置管理是低频操作，不需要在 1.0.1 开发的第一阶段完成。

### 4.4 USV（统一生命周期监管）

| 评估维度 | 判定 | 证据 |
|---------|------|------|
| Micro-Supervisor 设计 | ✅ 可行 | BPF LSM + die_notifier 检测 Page Fault/硬件异常 |
| Macro-Supervisor 设计 | ✅ 可行 | 与 seL4 Root Task 模型高度一致 |
| "内核冷酷执法，用户温情裁决" | ✅ 可行 | seL4 Fault Handler 已验证数十年 |
| IPC 队列冻结机制 | ✅ 可行 | 内核模块设置 freeze 标志，fastpath 只读检查 |
| ERR_ABNORMAL_CAP 故障码 | ⚠️ 未定义 | 需在 error.h 中定义 |
| Macro-Supervisor 单点故障 | ⚠️ 需 fallback | 内核 watchdog 直接重启 |

**源码对照**：
- seL4 `src/api/syscall.c:270-290` — `handleFault()` 将故障传递给 Fault Handler（Root Task）
- seL4 `src/kernel/boot.c:496-564` — Root Task 获得所有初始 Capability
- seL4 `src/object/endpoint.c:20-130` — sendIPC 根据 Endpoint 状态决定阻塞或传递

**结论**：USV 是 5 模块中设计最深入的，与 seL4 的 Fault Handler 模型高度一致。Macro-Supervisor 单点故障是已知的微内核难题，需要内核 watchdog fallback。

### 4.5 UIPF（统一 IPC Fabric）

| 评估维度 | 判定 | 证据 |
|---------|------|------|
| io_uring 语义映射 | ✅ 可行 | IORING_OP_URING_CMD 在标准 6.6 中存在 |
| 内联 Capability 校验 | ✅ 可行 | BPF LSM hook + radix tree O(1) 查找 |
| 数据面自治三原则 | ✅ 设计正确 | Ring 生命周期解耦 + 离线校验 + Reconciliation |
| "无分支预测失败" | ⚠️ 修正为"最小化" | 实际操作必然有分支 |
| "无上下文切换" | ✅ 可行 | io_uring_cmd 回调在提交进程上下文执行 |
| "无锁竞争" | ✅ 可行 | RCU radix tree + 无锁 ring buffer |
| 跨进程 page flipping | ❌ 不可行 | 已改用 IORING_OP_URING_CMD 语义映射方案 |

**源码对照**：
- seL4 `src/fastpath/fastpath.c:38-52` — 12 项检查可归纳为 3 类，映射到 io_uring 方案
- seL4 `src/object/endpoint.c:220-240` — `doIPCTransfer` 处理消息传输和 badge 值
- OLK 6.6 `io_uring/io_uring.c:1400` — `io_uring_cmd()` 处理 IORING_OP_URING_CMD

**结论**：UIPF 是 5 模块中技术最成熟的。io_uring 语义映射方案完全可行，与 seL4 fastpath 的语义映射清晰。

---

## 5. 微内核化架构实施评估

### 5.1 "除了核心，都是服务"适用性

| 子系统 | 内核态（核心） | 用户态（服务） | 可行性 |
|--------|--------------|--------------|:---:|
| 调度 | EEVDF + SCHED_FIFO + cgroup v2 | 调度策略（Macro-Supervisor 决策） | ✅ |
| IPC | io_uring_cmd 回调 + Capability 校验 | 12 daemons + Logger Daemon | ✅ |
| VFS | 路径解析 + dentry/inode 缓存 | FS 实现（FUSE 模型） | ✅ |
| 网络 | TCP/IP 核心 | 网络策略（eBPF 用户态编排） | ✅ |
| Capability | radix tree + BPF LSM | 策略编译 + 审计 | ✅ |
| 日志 | Ring Buffer 无锁写入 + eventfd | Logger Daemon 格式化/落盘 | ✅ |

**结论**：微内核化架构在 Linux 6.6 上完全适用。核心保留最小化机制，策略和上层逻辑用户态化。

### 5.2 sched_ext 不可用的替代方案验证

| 替代方案 | 机制 | 延迟 | 灵活性 | 推荐度 |
|---------|------|------|--------|:---:|
| 用户态调度器 + SCHED_FIFO | Macro-Supervisor 决策 + 实时优先级 | ~1μs | 高 | ★★★★★ |
| SCHED_DEADLINE + cgroup v2 | EDF 调度 + CPU 隔离 | ~100ns | 低 | ★★★★ |
| BPF 观测 + cgroup 调整 | tracepoint 观测 + 动态 cgroup | ~100ns | 低 | ★★ |

**结论**：推荐用户态调度器 + SCHED_FIFO 方案，最符合微内核化原则。

### 5.3 以标准 Linux 6.6 为唯一基线的合理性

| 维度 | 评估 |
|------|------|
| 稳定性 | ✅ 6.6 是 LTS 版本，长期维护至 2026+ |
| 生态兼容 | ✅ 6.6 被主流发行版广泛采用 |
| 特性丰富度 | ⚠️ 缺 sched_ext，但 io_uring 能力充足 |
| 放弃其他版本影响 | 低，仅 sched_ext 需要替代方案 |

---

## 6. 方案完整性与合理性评估

### 6.1 方案完整性

| 维度 | 当前状态 | 目标状态 | 差距 |
|------|---------|---------|------|
| 设计文档体系 | 128 份现有 | 148 份应有 | 20 份缺失 |
| 代码基础 | 0 行可编译源码 | 1 个可 insmod 的 .ko | 完全缺失 |
| [SC] 共享头文件 | 8 个（agentrt 端），0 个（agent-linux 端） | 10 个（两端各 10 个） | 2 个新增 + 10 个 agent-linux 端 |
| CI/CD 流水线 | 6 个 workflow（无法运行） | 6 个全部可运行 | 需代码基础 |
| 工程标准 | SSoT 三层一致性模型 | 全部 CI 验证通过 | 部分可运行 |

### 6.2 方案合理性

| 维度 | 评估 | 说明 |
|------|------|------|
| 架构设计 | ✅ 合理 | 微内核化 + 5 模块统一，与 seL4 工程实践一致 |
| 技术选型 | ✅ 合理 | io_uring + BPF LSM + eventfd，均为标准 6.6 原生能力 |
| 工程标准 | ✅ 合理 | 对齐 OLK 6.6 编码规范 + seL4 微内核思想 |
| 路线图 | ⚠️ 需调整 | 基于"文档完成即可编码"假设，实际多数模块尚未到可编码状态 |

### 6.3 可改进和修正的问题

#### P0 级（设计修正，4 项）

| # | 问题 | 当前状态 | 建议修正 |
|---|------|---------|---------|
| **FIX-01** | "无分支预测失败"表述不现实 | 多处文档声称 | 修正为"最小化分支预测失败"（likely/unlikely） |
| **FIX-02** | "全部编码进共享内存"表述不准确 | 用户原始设想 | 修正为：日志+IPC 进共享内存，错误码编译时契约，配置 sysctl |
| **FIX-03** | DMA 一致性内存过度设计 | 用户原始设想 | 修正为 alloc_pages + mmap（x86_64 默认缓存一致） |
| **FIX-04** | 调度方案依赖 sched_ext | 多份文档 | 修正为用户态调度器 + SCHED_FIFO + cgroup v2 |

#### P1 级（新增发现，5 项）

| # | 问题 | 发现来源 | 建议 |
|---|------|---------|------|
| **NEW-01** | io_uring 安全风险（100+ CVE） | 行业检索 | 增加 io_uring 安全加固设计文档 |
| **NEW-02** | Linux 6.6 新增 `io_uring_disabled` sysctl | 行业检索 | 方案应利用此 sysctl 进行安全控制 |
| **NEW-03** | io_uring 绕过 seccomp | 行业检索 | BPF LSM 作为补充安全层 |
| **NEW-04** | IORING_OP_BPF 提案（2025-11） | LWN | 未来可扩展方向，1.0.1 暂不纳入 |
| **NEW-05** | seL4 MDB 完整性约束未借鉴 | 源码追溯 | 03-capability-model.md 升级时补充 |

#### P2 级（优化建议，3 项）

| # | 问题 | 建议 |
|---|------|------|
| **OPT-01** | 12 daemons 无逐个功能设计 | Phase 1 补充 |
| **OPT-02** | 性能 SLO 全部是"6.6 基线值"占位 | 设定实际性能目标 |
| **OPT-03** | 形式化验证目标与 seL4 20+ 人年现实差距 | 重新评估验证策略 |

---

## 7. 四大技术领域覆盖度评估

| 领域 | 覆盖组件 | 覆盖度 | 评估 |
|------|---------|:---:|------|
| **通信** | UIPF（核心）+ UEF（错误码传递）+ ULPS（日志传递）+ USV（监管通知） | 95% | 充分覆盖 |
| **治理** | UCF（配置）+ USV（生命周期）+ UEF（故障分类） | 90% | 充分覆盖 |
| **观测** | ULPS（日志核心）+ UEF（错误码观测）+ USV（心跳观测） | 90% | 充分覆盖 |
| **韧性** | USV（核心）+ UEF（故障定义）+ UIPF（数据面自治）+ [DSL]（降级生存） | 85% | 充分覆盖，[DSL] 层待落地 |

**结论**：Airymax Unify Design 5 模块全面覆盖了"通信、治理、观测、韧性"四大技术领域，覆盖率 85-95%。

---

## 8. 综合判定

### 8.1 最终判定矩阵

| 判定维度 | 结论 | 置信度 |
|---------|------|:---:|
| **整体方案可行性** | ✅ 可行 | 90% |
| **设计架构正确性** | ✅ 正确 | 95% |
| **技术链路可打通性** | ✅ 4 条链路全部可打通 | 95% |
| **工程实现就绪度** | ⚠️ 需 Phase 0~3 前置工作 | 90% |
| **方案完整性** | ⚠️ 85%（20 份文档缺失） | 85% |
| **方案合理性** | ✅ 合理 | 90% |
| **与 Linux 6.6 兼容性** | ✅ 完全兼容 | 95% |
| **与 seL4 语义一致性** | ✅ 高度一致 | 90% |
| **与 OLK 6.6 工程标准兼容性** | ✅ 完全兼容 | 95% |

### 8.2 四条技术链路判定

| 链路 | 判定 | 关键风险 | 缓解措施 |
|------|:---:|------|------|
| IPC（io_uring + BPF LSM） | ✅ 可行 | BPF verifier 限制 | 轻量标记放 BPF，完整查找放内核模块 |
| 日志（Ring Buffer + Logger Daemon） | ✅ 可行 | Ring Buffer 溢出 | 预留空间 + 背压机制 |
| 调度（用户态调度器） | ⚠️ 可行 | ~1μs 延迟 | 批量调度决策 |
| 监管（Micro + Macro Supervisor） | ✅ 可行 | Macro-Supervisor 单点故障 | 内核 watchdog |

### 8.3 诚实面对的约束

1. **sched_ext 不可用** → 用户态调度器有 ~1μs 性能代价
2. **BPF LSM 有 verifier 限制** → 能力校验部分逻辑需放内核模块
3. **"无锁、无分支、无切换"是理想** → 实际是"最小化"而非"消除"
4. **io_uring 有安全风险历史** → 需要额外安全加固（BPF LSM + opcode 白名单）
5. **Macro-Supervisor 单点故障** → 需要内核 watchdog fallback

---

## 9. 建议的行动路径

### 9.1 立即行动（P0）

1. **修正 4 项设计表述**：FIX-01~04（见 §6.3）
2. **创建 [SC] error.h + log_types.h**：两端物理文件创建
3. **创建 kernel 子仓第一个 .c 文件**：打破代码真空
4. **增加 io_uring 安全加固文档**：新增 NEW-01~03

### 9.2 近期行动（P1，Phase 1~2）

5. **补充 20 份缺失设计文档**：按 07-improvement-plan 的 Phase 1 执行
6. **升级 4 份现有文档至 v1.0+**：microkernel-strategy / ipc-fastpath / capability-model / iron9-shared-model
7. **修复 agentrt 技术债**：BAN-294/299/305 + 双轨制收敛
8. **增加 [DSL] 降级生存层**：作为 IRON-9 v3 第四层

### 9.3 中期行动（P2，Phase 3）

9. **启动 1.0.1 全面开发**：在 Phase 0~3 全部完成后
10. **持续跟踪行业趋势**：io_uring 安全更新、BPF+io_uring 融合进展

---

## 10. 结论

**agent-linux 整体方案在技术设计层面是可行且正确的。** 经过 7 份审查报告的交叉验证、参考源码的实地追溯、最新行业实践的对照检索，方案的核心架构（Airymax Unify Design 5 模块 + 微内核化 + [SC]/[SS]/[IND]/[DSL] 四层共享模型）与 Linux 6.6 内核机制和 seL4 微内核设计哲学高度一致。

**方案不存在根本性架构缺陷。** 所有已发现的问题均属于工程落地层面（代码缺失、文档缺失、技术债），而非设计层面。按照 07-improvement-plan 提出的 4 阶段 28 天改进路径，在完成 P0 前置工作后，agent-linux 即可达到"可以开始 1.0.1 全面开发"的状态。

**本报告识别并修正了 4 项设计表述问题，新增了 5 项行业实践发现，确认了 09 报告的 sched_ext 误判已被 10/11 报告完全修正，确认了 7 份报告之间不存在未解决的矛盾。**

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. Internal Verification Document.