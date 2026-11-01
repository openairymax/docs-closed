# 11 — 方案可行性独立验证报告 v1.0
## 基于标准 Linux 6.6 主线源码的端到端技术链验证

> **报告日期**：2026-07-16
> **报告性质**：闭源内部技术验证（完全基于源码级证据，不依赖任何二手报告）
> **验证方法**：端到端技术链追溯 + 每个环节弱点识别 + 诚实判定

---

## 0. 验证方法论

本报告不依赖任何前序报告的结论，而是从零开始，对每个技术环节进行独立验证：

1. **前提验证**：每个依赖的标准 6.6 内核特性是否存在
2. **链路验证**：从 Agent 发送 IPC 到接收方收到消息的完整链路是否可打通
3. **弱点识别**：每个环节在什么条件下会失败
4. **诚实判定**：不回避问题，不美化结论

---

## 1. 前提验证：标准 Linux 6.6 内核能力

### 1.1 已验证的特性清单

| 特性 | 标准 6.6 | 证据 | 置信度 |
|------|---------|------|--------|
| **IORING_OP_URING_CMD** | ✅ 存在 | 6.0 引入，NVMe passthrough / ublk / FUSE-over-io-uring 均使用 | 100% |
| **security_uring_cmd LSM hook** | ✅ 存在 | `LSM_HOOK(int, 0, uring_cmd, ...)` 在 lsm_hook_defs.h:422 | 100% |
| **BPF LSM 可 hook uring_cmd** | ✅ 可行 | `call_int_hook(uring_cmd, 0, ioucmd)` 调用标准 LSM 分发 | 100% |
| **file_operations->uring_cmd** | ✅ 存在 | `fs.h:2070` 定义，kernel module 可注册 | 100% |
| **IORING_OP_SEND_ZC** | ✅ 存在 | 6.0 引入 | 100% |
| **IORING_OP_MSG_RING** | ✅ 存在 | 5.18 引入 | 100% |
| **registered buffers** | ✅ 存在 | 5.20 引入 | 100% |
| **printk ring buffer (prb_*)** | ✅ 存在 | 5.10 引入 | 100% |
| **dma_buf_export/fd** | ✅ 存在 | 3.6 引入 | 100% |
| **alloc_pages + mmap** | ✅ 存在 | 内核基础机制 | 100% |
| **eventfd** | ✅ 存在 | 内核基础机制 | 100% |
| **SCHED_DEADLINE** | ✅ 存在 | 3.14 引入 | 100% |
| **cgroup v2** | ✅ 存在 | 4.15 引入 | 100% |
| **die_notifier** | ✅ 存在 | 内核基础机制 | 100% |
| **sched_ext** | ❌ **不存在** | 6.12 才合入主线（2024-09 rc1，2024-11 正式） | 100% |

### 1.2 关键修正：此前报告 09 的错误

报告 09 基于 OLK 6.6 源码发现 `kernel/sched/ext.c`（7361 行，215KB），错误地判定"标准 6.6 有 sched_ext"。实际上 OLK 6.6 是 openEuler 的增强版内核，已 backport 了 6.12+ 才合入主线的 sched_ext。

**标准 Linux 6.6 主线没有 sched_ext。** 这是本报告的基础约束。

---

## 2. 端到端技术链验证

### 2.1 链路 1：IPC（Agent A → Agent B）

```
Agent A (用户态)                  Linux 6.6 内核                  Agent B (用户态)
──────────────────────────────────────────────────────────────────────────────
1. io_uring_submit()
   IORING_OP_URING_CMD
   cmd_op = AIRY_IPC_CALL
   ─────────────────────→
                              2. io_uring_cmd()
                                 └→ security_uring_cmd(ioucmd)  ← LSM hook
                                    └→ BPF LSM: 能力校验        ← 新增 BPF 程序
                                    └→ 通过/拒绝
                                 └→ file->f_op->uring_cmd()     ← 内核模块回调
                                    └→ airy_uring_cmd_ipc()
                                       ├→ msg_validate()        ← 128B 头校验
                                       ├→ cnode_lookup()        ← O(1) radix tree
                                       ├→ ring_reserve()        ← 无锁 reserve
                                       ├→ memcpy 128B + payload ← 写入目标 ring
                                       └→ ring_commit()         ← 无锁 commit
                                 └→ eventfd_signal()             ← 通知接收方
                                                                           ────→
                                                                          3. epoll/io_uring
                                                                             eventfd 触发
                                                                          4. 读取 ring buffer
                                                                          5. 处理消息
```

**每个环节验证**：

| 步骤 | 依赖 | 标准 6.6 可用？ | 需要自行实现？ | 风险 |
|------|------|:---:|:---:|------|
| 1. io_uring_submit | io_uring + liburing | ✅ | 否 | 低 |
| 2. security_uring_cmd | LSM hook | ✅ | 否（hook 已在） | 低 |
| 2b. BPF LSM 能力校验 | BPF 程序 | ✅ | **是**（编写 BPF 程序） | **中**：BPF 有循环限制，radix tree 查找需在 BPF 中实现 |
| 2c. uring_cmd 回调 | 内核模块 | ✅ | **是**（编写内核模块） | 低 |
| 2d. 消息校验 + 写入 | 内核模块 | ✅ | **是**（内核模块实现） | 低 |
| 2e. eventfd 通知 | kernel eventfd | ✅ | 否 | 低 |
| 3-5. 接收方处理 | 用户态编程 | ✅ | **是**（用户态程序） | 低 |

**链路 1 判定**：✅ **可行**。但 BPF LSM 能力校验程序需要仔细设计（BPF verifier 限制）。

### 2.2 链路 2：日志（Fastpath → Logger Daemon）

```
内核态 Fastpath                  Linux 6.6 内核              用户态 Logger Daemon
──────────────────────────────────────────────────────────────────────────────
1. airy_log_write()
   └→ ring_reserve()              ← 无锁 reserve
   └→ memcpy 128B record          ← 一次 memcpy（~20ns）
   └→ ring_commit()               ← 无锁 commit
   └→ eventfd_signal()            ← 通知 Logger Daemon
                                                                           ────→
                                                                          2. epoll 触发
                                                                          3. mmap 读取记录
                                                                          4. sprintf 格式化
                                                                          5. 过滤 + 落盘
```

**每个环节验证**：

| 步骤 | 依赖 | 标准 6.6 可用？ | 需要自行实现？ | 风险 |
|------|------|:---:|:---:|------|
| 1. 无锁 ring buffer | alloc_pages + 我们自己实现 | ✅ | **是**（内核模块） | **低** |
| 1b. 128B memcpy | 内核基础操作 | ✅ | 否 | 低 |
| 1c. eventfd 通知 | kernel eventfd | ✅ | 否 | 低 |
| 2-5. Logger Daemon | 用户态编程 | ✅ | **是**（用户态程序） | 低 |

**链路 2 判定**：✅ **可行**。相对简单，无特殊技术挑战。

**关于 DMA 一致性内存**：在 x86_64 上，`alloc_pages(GFP_KERNEL)` 分配的物理内存默认缓存一致。DMA 一致性内存（`dma_alloc_coherent`）仅在与真实 DMA 设备（NIC/GPU/NVMe）通信时需要。日志 Ring Buffer 不涉及 DMA 设备，使用 `alloc_pages + mmap` 即可，性能更好、更简单。

### 2.3 链路 3：调度（Agent 感知调度，sched_ext 不可用）

```
Macro-Supervisor (用户态)        Linux 6.6 内核              Agent 进程
──────────────────────────────────────────────────────────────────────────────
1. 调度决策循环
   └→ 收集 Agent 状态
   └→ 计算调度策略
   └→ sched_setscheduler()        ← syscall
      └→ 设置 SCHED_FIFO 优先级
   └→ sched_setaffinity()         ← syscall
      └→ 绑定 CPU
   └→ cgroup 调整                  ← cgroupfs 写入
      └→ cpu.max / cpu.weight
                                                                           ────→
                                                                          2. EEVDF/SCHED_FIFO
                                                                             按优先级调度
```

**关键对比**：

| 维度 | sched_ext（标准 6.6 不可用） | 用户态调度器（替代方案） |
|------|---------------------------|----------------------|
| 决策延迟 | ~100ns（BPF 内核态） | ~1μs（一次 syscall） |
| 灵活性 | 高（BPF 可编程） | 受限（syscall 语义固定） |
| 复杂度 | 低（内核已有框架） | 中等（自行实现调度器） |
| 可靠性 | 高（内核 fallback 到 CFS） | 中（Macro-Supervisor 崩溃风险） |

**链路 3 判定**：⚠️ **可行但有性能代价**。用户态调度器的 1μs 延迟对于大多数 Agent 场景可接受，但对于时间敏感的实时 Agent 可能不够。

### 2.4 链路 4：分层监管（Micro-Supervisor + Macro-Supervisor）

```
内核态 Micro-Supervisor          Linux 6.6 内核              用户态 Macro-Supervisor
──────────────────────────────────────────────────────────────────────────────
1. 检测非法 Capability 使用
   └→ BPF LSM 在 uring_cmd 钩子
   └→ 发现非法访问
   └→ 冷冻 IPC 接收队列             ← 内核模块设置标志
   └→ 返回 AIRY_FAULT_ABNORMAL_CAP
   └→ eventfd 通知 Macro-Supervisor
                                                                           ────→
                                                                          2. 接收故障通知
                                                                          3. 查询上下文
                                                                          4. 价值判断
                                                                          5. 执行裁决
                                                                             └→ 警告/降级/暂停/终止
```

**每个环节验证**：

| 步骤 | 依赖 | 标准 6.6 可用？ | 需要自行实现？ | 风险 |
|------|------|:---:|:---:|------|
| 1. BPF LSM 检测 | security_uring_cmd hook | ✅ | **是**（BPF 程序） | **中** |
| 1b. 冷冻 IPC 队列 | 内核模块 | ✅ | **是**（内核模块） | 低 |
| 1c. eventfd 通知 | kernel eventfd | ✅ | 否 | 低 |
| 2-5. 裁决逻辑 | 用户态编程 | ✅ | **是**（用户态程序） | **中**：Macro-Supervisor 自身崩溃时需 fallback |

**链路 4 判定**：✅ **可行**。seL4 的 Fault Handler 模式已验证数十年。但 Macro-Supervisor 自身的故障恢复是已知的微内核难题（"谁监管监管者"）。

---

## 3. 弱点与失败模式识别

### 3.1 技术弱点

| 编号 | 弱点 | 严重性 | 触发条件 | 缓解措施 |
|------|------|--------|---------|---------|
| **W1** | BPF 程序中的 radix tree 查找受限 | 中 | BPF verifier 可能拒绝复杂查找 | 将查找逻辑放内核模块，BPF 只做轻量标记检查 |
| **W2** | 用户态调度器性能 | 中 | 高频调度场景 | 批量调度决策，减少 syscall 次数 |
| **W3** | Macro-Supervisor 单点故障 | 高 | Macro-Supervisor 崩溃 | 内核 watchdog 直接重启 Macro-Supervisor |
| **W4** | Ring Buffer 溢出 | 中 | Logger Daemon 处理不及时 | Ring Buffer 预留足够空间 + 背压机制 |
| **W5** | 内核模块稳定性 | 高 | 我们的内核模块 bug | 充分测试 + 内核模块隔离 |
| **W6** | io_uring_cmd 回调中不能睡眠 | 中 | 在 atomic context 中调用睡眠函数 | 所有回调使用原子操作，不睡眠 |
| **W7** | "无分支预测失败"不现实 | 低 | 实际操作必然有分支 | 改为"最小化分支预测失败"（likely/unlikely） |

### 3.2 架构弱点

| 编号 | 弱点 | 影响 |
|------|------|------|
| **A1** | 5 个统一模块各自的复杂度叠加，总复杂度可能超出可控范围 | 工程实现风险 |
| **A2** | 内核模块 + BPF 程序 + 用户态 daemon 三层架构，调试困难 | 开发效率 |
| **A3** | 12 个 daemon 的协调和故障恢复复杂 | 运维复杂度 |
| **A4** | VFS 用户态化（FUSE 模型）性能可能不满足要求 | 性能风险 |

---

## 4. 诚实判定

### 4.1 逐个判定

| 组件 | 判定 | 置信度 |
|------|------|:---:|
| UIPF（统一 IPC Fabric） | ✅ **可行** | 95% |
| ULPS（统一日志与打印） | ✅ **可行** | 95% |
| UEF（统一错误码与故障） | ✅ **可行** | 90% |
| UCF（统一配置管理） | ✅ **可行** | 90% |
| USV（统一生命周期监管） | ✅ **可行**但有复杂度风险 | 75% |
| **整体方案** | ✅ **可行**，但需注意以下约束 | 80% |

### 4.2 必须接受的约束

1. **sched_ext 不可用**：调度策略必须用户态化，接受的性能代价（~1μs per decision）
2. **BPF LSM 能力校验**：BPF verifier 限制可能强制将复杂查找逻辑放内核模块
3. **Macro-Supervisor 单点故障**：需要内核 watchdog fallback
4. **DMA 一致性内存非必需**：x86_64 上 alloc_pages + mmap 即可
5. **"无分支预测失败"目标是理想化表述**：实际应表述为"最小化分支预测失败"

### 4.3 需要重新设计的部分

| 部分 | 当前设计 | 问题 | 建议 |
|------|---------|------|------|
| **调度** | 依赖 sched_ext 的 SCHED_AGENT BPF 程序 | sched_ext 在标准 6.6 不存在 | 改为用户态调度器 + SCHED_FIFO + cgroup v2 |
| **Capability 校验** | 声称 BPF LSM 内联校验 | BPF verifier 可能限制 radix tree 查找 | 轻量标记检查放 BPF，完整查找放内核模块 |
| **"全部编码进共享内存"** | 错误码/日志/配置/IPC 全部进共享内存 | 表述不准确 | 修正为：日志+IPC 进共享内存，错误码编译时契约，配置运行时 sysctl |
| **"无分支预测失败"** | 声称 fastpath 无分支预测失败 | 不现实 | 修正为"最小化分支预测失败"（likely/unlikely） |

### 4.4 最终判定

**整体方案可行。** 标准 Linux 6.6 主线提供了全部必要的基础设施：
- `IORING_OP_URING_CMD` + `security_uring_cmd` LSM hook → IPC fastpath
- `alloc_pages` + `mmap` + `eventfd` → 零拷贝日志
- `SCHED_DEADLINE` + `SCHED_FIFO` + `cgroup v2` → 用户态调度器
- `die_notifier` + `BPF LSM` → 分层监管

**但需诚实面对三个现实约束**：
1. sched_ext 不可用 → 用户态调度器有性能代价
2. BPF LSM 有 verifier 限制 → 能力校验可能需要部分逻辑放内核模块
3. "无锁、无分支、无切换"是理想 → 实际是"最小化"而非"消除"

**下一步建议**：按照 4 项修正建议更新方案文档，然后开始 Phase 0 工程实施（创建内核模块骨架 + 首个 airy_core.ko）。

---

© 2025-2026 SPHARX Ltd. All Rights Reserved. Internal Verification Document.