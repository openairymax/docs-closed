# 05 — [DSL] 降级生存层设计缺陷报告

> **审计日期**：2026-07-16
> **审查范围**：近 10 轮对话中揭示的 IRON-9 v2 共享模型对"共享失败"场景的覆盖缺陷
> **核心问题**：IRON-9 v2 定义了 [SC]/[SS]/[IND] 三层，但只定义了"正常共享路径"，未定义"共享失败时的生存路径"。

---

## 1. 问题起源

近 10 轮对话的用户第 9 条消息指出了核心缺陷：

> "这份方案是'完美的架构设计文档'，但它脱离了 agent-linux 和 agentrt 的实际，缺少了让 Linux 内核模块稳定运行的'生存层'细节，定义了'共享什么'，但没有定义'当共享失败时，系统怎么活下来'"

---

## 2. 现有架构 vs 需要的架构

### 2.1 IRON-9 v2 当前定义

```
[SC]  Shared Contract Layer  — 物理同一份，逐字节相同
[SS]  Semantic Source Layer   — API 语义一致，签名独立
[IND] Independent Layer       — 完全独立演进
```

### 2.2 缺少的第四层

```
[DSL] Degraded Survival Layer — 共享失败时的最小可运行子集
```

[DSL] 层的核心原则：

1. **内核态永远不依赖用户态可用性**：用户态 daemon 挂了，内核必须继续运行
2. **用户态永远不假设内核态 [SC] 头文件版本一致**：降级使用本地定义
3. **[SC] 共享失败不导致系统不可用**：每个共享模块有独立降级路径
4. **[DSL] 是设计时的约束，不是运行时的 fallback**：降级路径必须在架构设计时定义，不能靠运行时 `#ifdef`

---

## 3. 逐模块降级分析

### 3.1 错误码 [SC] error.h

| 场景 | 是否覆盖 | 缺陷 |
|------|---------|------|
| [SC] 头文件版本不匹配 | **否** | 无 AIRY_SC_FALLBACK 块 |
| 内核编译时找不到 error.h | **否** | 无 Kconfig 回退选项 |
| 错误码值语义冲突 | **否** | 无哨兵值 AIRY_EUNKNOWN 降级策略 |

**需要的降级块结构**：

```c
/* error.h 底部 */
#ifdef AIRY_SC_FALLBACK
/*
 * [DSL] 降级生存块 —— 当 [SC] 共享契约验证失败时启用
 * 内核态回退到最小 POSIX errno 子集 (-1 ~ -38)
 * 用户态继续使用完整 AIRY_E* 集
 */
#undef  AIRY_ERR_COUNT
#define AIRY_ERR_COUNT  38
#define AIRY_SC_FALLBACK_ERRCODE  1
#endif
```

### 3.2 日志 [SC] log_types.h

| 场景 | 是否覆盖 | 缺陷 |
|------|---------|------|
| 内核找不到 log_types.h | **否** | printk 无回退路径设计 |
| Logger Daemon 挂了 | **否** | ring buffer 覆盖策略未定义 |
| Ring Buffer 内存未预留 | **否** | airy_klog_write 无回退到 printk 设计 |
| **内核 Panic** | **否** | Panic 路径禁用 ring buffer 的机制未设计 |

**Panic 回退路径**（对齐 Linux printk_safe）：

```
Panic 发生时：
1. airy_klog_panic_enter() → 设置 panic 上下文标志
2. 禁用 ring buffer 路径 → prb_reserve 需要锁
3. 回退到 printk() 原生 → 写入 Linux printk_ringbuffer（NMI-safe）
4. console 直接输出 → 串口/VGA
5. airy_log_reserved 区不受影响 → kdump 可导出
```

### 3.3 生命周期 [SC] sched.h

| 场景 | 是否覆盖 | 缺陷 |
|------|---------|------|
| [SC] 状态枚举版本不匹配 | **否** | 无 3 态降级（RUNNING/STOPPED/DEAD） |
| 内核 Agent 注册 syscall 失败 | **否** | 无普通进程模式降级 |
| L0 kthread Supervisor 死亡 | **否** | 无 L1 接管降级 |
| L1 daemon 死亡 | **否** | 无 L0 通过 PID 1 感知降级 |

**需要的降级策略**：

| Supervisor 层 | 正常模式 | 降级模式 | 降级触发条件 |
|--------------|---------|---------|------------|
| L0 kthread | 心跳检测 + 强制终止 | 无（系统不可用） | kthread 死亡 = 内核 panic |
| L1 daemon | SIGCHLD 监控 + 重启 | 降级为 L0 直接管理 | L1 死亡超过 3 个心跳周期 |
| L2 Agent | 完整 8 态管理 | 简化为 RUNNING/STOPPED | L0/L1 同时不可用 |

### 3.4 IPC [SC] ipc.h

| 场景 | 是否覆盖 | 缺陷 |
|------|---------|------|
| [SC] ipc.h magic 不匹配 | 部分 | fastpath 状态机覆盖了 magic 校验失败 → ERROR |
| io_uring 不可用（旧内核） | **否** | 无回退到 POSIX MQ 设计 |
| capability daemon 离线 | **否** | 无数据面离线校验降级（见 06 报告） |
| ring buffer 满或损坏 | 部分 | fastpath 有背压机制，但慢路径降级覆盖不完整 |

---

## 4. [DSL] 层统一框架设计

### 4.1 每个 [SC] 模块必须定义的降级信息

```c
/* [SC] 模块的降级信息块 */
struct airy_sc_fallback {
    const char *module_name;     /* "error" / "log_types" / "sched" / "ipc" */
    uint32_t    fallback_version; /* 降级块的版本号 */
    uint32_t    max_capability;   /* 降级模式下支持的最大能力 */
    const char *fallback_path;   /* 降级路径描述 */
};
```

### 4.2 运行时降级状态查询

```c
/* 通过 sysfs/procfs 查询当前降级状态 */
/* /sys/kernel/airymax/sc/fallback_status */
const struct airy_sc_fallback *airy_sc_get_fallback(const char *module_name);
bool airy_sc_is_degraded(const char *module_name);
```

### 4.3 [SC] CI 的降级验证

```
sc-dual-ci 的检查矩阵扩展：
1. 正常模式：两端逐字节相同 ✓
2. 降级模式：每端用 AIRY_SC_FALLBACK 编译 ✓
3. 降级模式 + 正常模式互操作：跨模式消息格式兼容 ✓
```

---

## 5. 建议

1. **在 IRON-9 v2 文档中新增 [DSL] 层定义**：作为第四层共享模型
2. **每个 [SC] 头文件底部增加 `#ifdef AIRY_SC_FALLBACK` 降级块**
3. **扩展 sc-dual-ci.yml**：增加降级模式编译测试
4. **编写 [DSL] 层设计文档**：定义降级原则、每模块降级路径、运行时查询接口
5. **内核 Kconfig 增加 `CONFIG_AIRY_SC_FALLBACK`**：控制降级行为
6. **设计 Panic 生存路径文档**：明确 printk 回退策略
