# 02 — [SC] 共享契约层头文件完整性审计

> **审计日期**：2026-07-16
> **审计基线**：IRON-9 v2 [SC] 6+2 共享头文件定义
> **审计方法**：逐文件 Glob 扫描 + 源码内容审查 + 跨仓库对比

---

## 1. [SC] 共享头文件清单

IRON-9 v2 (06-iron9-shared-model.md) 定义了 6+2 共享头文件：

| # | 文件名 | agentrt 端 (commons/include/airymax/) | agentrt-linux 端 (kernel/include/airymax/) | 状态 |
|---|--------|--------------------------------------|------------------------------------------|------|
| 1 | ipc.h | 存在 (82 行) | **不存在** | [SC] 仅一端 |
| 2 | sched.h | 存在 (79 行) | **不存在** | [SC] 仅一端 |
| 3 | memory_types.h | 存在 | **不存在** | [SC] 仅一端 |
| 4 | security_types.h | 存在 | **不存在** | [SC] 仅一端 |
| 5 | cognition_types.h | 存在 | **不存在** | [SC] 仅一端 |
| 6 | syscalls.h | 存在 | **不存在** | [SC] 仅一端 |
| 7 | error.h | **不存在** | **不存在** | **两端都不存在** |
| 8 | bpf_struct_ops.h | 存在 | **不存在** | [SC] 仅一端 |
| +1 | log_types.h | **不存在** | **不存在** | **未列入 IRON-9 v2** |

**结论**：8 个 [SC] 头文件中，仅 agentrt 端存在 7 个（不含 error.h）。agentrt-linux 端 0 个。error.h 和 log_types.h 两端都不存在——这些是 5 模块统一方案的核心文件。

---

## 2. 关键发现

### 2.1 error.h 不存在

5 模块统一方案的核心文件。当前错误码分散在：

| 文件 | 定义 | 数量 |
|------|------|------|
| agentrt/commons/include/airy_types.h | AIRY_E* POSIX 码 | 30 个 |
| agentrt/commons/utils/error/include/error.h | AIRY_ERR_* 扩展码 | ~90 个 |

两种错误码体系并存，值域冲突已部分迁移（AIRY_ERR_* 部分码从 -2~-17 迁移至 -40~-50），但未完全收敛。统一方案要求创建 `include/airymax/error.h` 作为 [SC] SSoT，两端通过 `#include <airymax/error.h>` 引用同一份文件。

### 2.2 log_types.h 不存在

统一日志+打印系统的核心文件。当前 agentrt 有三条日志管线：

| 管线 | 定义文件 | 宏 |
|------|---------|-----|
| LOG_* | logging.h | LOG_DEBUG/INFO/WARN/ERROR/FATAL |
| AIRY_LOG_* | logger.h (通过 logging_compat.h 桥接) | AIRY_LOG_DEBUG/INFO/WARN/ERROR/FATAL |
| airy_print_* | airy_print.h (已委托 log_write) | airy_print_ok/no/info/warn/error/fatal/debug/section |

统一方案要求创建 `include/airymax/log_types.h`，定义 `struct airy_log_record` (128B) + 5 级别枚举 + Linux printk 8 级 → Airymax 5 级映射表。

### 2.3 uapi_compat.h 类型桥接不完整

当前 `uapi_compat.h` 用 `#ifdef __linux__` 桥接：

```c
#ifdef __linux__
#include <linux/types.h>  /* 用户态：Linux 系统已有 __u32 定义 */
#else
typedef uint32_t __u32;   /* 非 Linux：自建 kernel-style 类型 */
#endif
```

**问题**：当 agentrt-linux 内核编译时，`__linux__` 为真但上下文是 `__KERNEL__`，内核态应该 `#include <linux/types.h>`（从内核源码树路径），而用户态应该从 `/usr/include/linux/types.h` 获取。`#ifdef __linux__` 无法区分这两种场景——在内核交叉编译环境中可能导致类型冲突。

正确的做法（参考 Linux UAPI 标准）：

```c
#ifdef __KERNEL__
  #include <linux/types.h>         /* 内核态：从内核源码树 */
#elif defined(__linux__)
  #include <linux/types.h>         /* Linux 用户态：从系统头文件 */
#else
  #include <stdint.h>              /* 非 Linux：自建类型 */
  typedef uint32_t __u32;
  /* ... */
#endif
```

**此问题未暴露**是因为 agentrt-linux 没有内核代码，从未触发 `__KERNEL__` 路径。

### 2.4 ipc.h 缺少 capability 相关字段

`struct airy_ipc_msg_hdr` 当前 128B 布局：

| 字段 | offset | 大小 |
|------|--------|------|
| magic | 0 | 4 |
| opcode | 4 | 2 |
| flags | 6 | 2 |
| trace_id | 8 | 8 |
| timestamp_ns | 16 | 8 |
| src_task | 24 | 8 |
| dst_task | 32 | 8 |
| payload_len | 40 | 4 |
| reserved | 44 | **84** |

`reserved[84]` 是 84 字节的保留区。IPC 数据面自治方案需要在此区域增加 `capability_badge` 字段（8 字节）、`cap_expires_ns`（8 字节）和 `ring_id`（4 字节），使数据面操作可以进行离线 capability 缓存校验。当前 reserved 字段有 84 字节充足空间。

### 2.5 sched.h 缺少 Agent 生命周期状态枚举

`sched.h` 当前仅定义了任务调度相关类型：

- `AIRY_TASK_MAGIC` (0x41475453 'AGTS')
- `airy_vtime_t` (Q16.16 固定点)
- `struct airy_task_desc` (调度参数)
- 优先级/调度片/权重常量

缺少 Supervisor 三层模型需要的 `enum airy_agent_state`：
- REGISTERED(0) / CONFIGURED(1) / RUNNING(2) / PAUSING(3) / PAUSED(4) / SUSPENDED(5) / TERMINATING(6) / TERMINATED(7)

缺少 Supervisor 事件枚举：
- HEARTBEAT_LOST / OOM_KILL / CAP_VIOLATION / PHASE_TIMEOUT / BUDGET_EXHAUST

---

## 3. [SC] 双向 CI 验证不可行

`sc-dual-ci.yml` 的核心逻辑是：

```yaml
# 伪代码
diff agentrt-linux/include/airymax/$file agentrt/commons/include/airymax/$file
# 必须逐字节相同
```

当前问题：
1. agentrt-linux 端 0 个文件 → diff 失败（没有左侧文件）
2. error.h / log_types.h 两端都不存在 → 无法 diff
3. 即使 CI 设定为 "agentrt 端为权威源，复制到 agentrt-linux"，也无法验证 agentrt-linux 端的内核代码是否正确使用了这些头文件

---

## 4. 建议

1. **创建 `agentrt-linux/kernel/include/airymax/` 目录**，从 agentrt 端复制现有 7 个 [SC] 头文件
2. **创建 error.h**：基于 5 模块统一方案设计，定义统一的 AIRY_E* 错误码
3. **创建 log_types.h**：基于 Ring Buffer + Logger Daemon 方案设计
4. **修复 uapi_compat.h**：增加 `#ifdef __KERNEL__` 路径
5. **扩展 ipc.h**：增加 capability_badge / cap_expires_ns / ring_id 字段
6. **扩展 sched.h**：增加 Agent 生命周期状态枚举
7. **启用 sc-dual-ci**：在两端均存在头文件后，CI 可验证逐字节一致性
