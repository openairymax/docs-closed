# 20 小时微基准测试方案

> **目标**：为 HotOS 2027 position paper 提供 IPC 延迟/吞吐的实证数据
> **对比对象**：agentrt L1+L2 IPC (用户态，真实代码) vs io_uring (真实运行) vs UDS (真实运行) vs seL4 (已发表数据)
> **测试机**：当前 Linux 工作站（Intel i7-12700K, 32GB RAM, Linux 6.5, gcc/cmake/make 可用）
> **前置条件确认**：agentrt 源码可用 ✅，seL4 源码可用但无构建环境 ✅，io_uring 需安装 liburing ✅，UDS 直接用

---

## 实验设计总览

### 三个层面的测试

```
测试 A：裸消息延迟（核心指标）
  发送方 → 接收方 → 响应发送方（一次往返）
  对比：agentrt vs io_uring vs UDS vs seL4(已发表)
  
测试 B：capability 开销
  agentrt 带 sandbox check vs 不带（测量 5 级流水线增加多少延迟）
  
测试 C：协议多路复用开销
  agentrt L2 头校验（magic + CRC32）的 CPU 开销
```

### seL4 数据来源

因为我们没有 seL4 运行时环境，seL4 的 IPC 延迟数据引用已发表文献：

| 来源 | IPC Call 延迟 | 配置 |
|------|-------------|------|
| seL4 whitepaper (Klein et al., 2009) | ~150 cycles (~75ns @ 2GHz) | ARM, fastpath |
| seL4 performance doc | ~500 cycles (~250ns) | x86, fastpath |
| L4Linux (Härtig et al., 1997) | ~5μs | L4IPC on x86 |
| seL4 MCS kernel | ~1.2μs cross-core IPC | x86_64 |

**论文中会诚实标注"seL4 数据来自已发表文献"**，这是 HotOS position paper 可接受的惯例。

---

## 20 小时具体分配

### Hour 1-2：环境搭建

```bash
# 1. 检出 agentrt 源码
ls /home/spharx/SpharxWorks/airymaxhub/agentrt/  # ✅ 已有

# 2. 安装 liburing（io_uring 用户态库）
apt-get install -y liburing-dev

# 3. 验证环境
gcc --version && cmake --version

# 4. 构建 agentrt（仅 IPC 相关模块）
cd /home/spharx/SpharxWorks/airymaxhub
cmake -B ../agentrt-bench -DCMAKE_BUILD_TYPE=Release agentrt/
cmake --build ../agentrt-bench --target agentrt-corekern -j$(nproc)
```

**验收标准**：`test_ipc` 和 `test_are_ipc` 编译通过并能运行。

---

### Hour 3-8：agentrt IPC 基准测试（核心实验）

#### 测试工具：一个新的 ping-pong 基准（~200 LOC）

```c
// bench_agentrt_ipc.c — 需要编写，以下为伪代码结构
// gcc -o bench_ipc bench_ipc.c -I agentrt/atoms/corekern/include/ \
//     -L ../agentrt-bench/atoms/corekern/ -lairy_corekern -lpthread

#include "ipc.h"
#include "are_ipc.h"
#include <time.h>

static uint64_t now_ns() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

// 测试 1: L1 binder raw 往返延迟（不含 L2 头）
// 发送方: airy_ipc_call(channel, msg, response, &size, timeout_ms)
// 接收方: 回调直接 echo

// 测试 2: L1 + L2 完整往返延迟
// 创建 are_ipc_message_t → 初始化 L2 头 → 
// 作为 data 传入 L1 airy_kernel_ipc_message_t →
// 发送 → 接收 → 校验 CRC32 → echo → 返回

// 测试 3: 带 sandbox 检查的往返（模拟 capability check）
// 在发送前调用 airy_sandbox_invoke(...) 再进行 send

// 测试配置:
// payload 大小: 0, 64, 256, 1024, 4096 bytes
// 每次运行 10000 次往返
// 输出: P50, P90, P99, P99.9, mean, min, max
```

**测试矩阵**（3 组 × 5 种 payload = 15 个数据点）：

| Test ID | L1 binder | L2 header | Sandbox check | Payload |
|---------|-----------|-----------|---------------|---------|
| 1a | ✅ | ❌ | ❌ | 0B |
| 1b | ✅ | ❌ | ❌ | 256B |
| 1c | ✅ | ❌ | ❌ | 4096B |
| 2a | ✅ | ✅ | ❌ | 0B |
| 2b | ✅ | ✅ | ❌ | 256B |
| 2c | ✅ | ✅ | ❌ | 4096B |
| 3a | ✅ | ✅ | ✅ | 0B |
| 3b | ✅ | ✅ | ✅ | 256B |
| 3c | ✅ | ✅ | ✅ | 4096B |

**预计每数据点时间**：~15 分钟（编译 + 运行 + 结果记录），共 ~3 小时。

---

### Hour 9-12：io_uring 基准测试

```bash
# 安装 liburing
apt-get install -y liburing-dev pkg-config
```

```c
// bench_io_uring_pingpong.c — 需要编写
// 创建一个 ring，两个线程共享同一个 ring fd
// 提交 SQE（操作码：IORING_OP_NOP 或 IORING_OP_WRITE 到 pipe）
// 测量 SQE提交 → CQE 完成的往返时间

// 测试配置（与 agentrt 测试对齐）：
// - 无 payload（NOP 模式）
// - 128B payload
// - 1KB payload
// 每次运行 10000 次
// 使用 SQPOLL + DEFER_TASKRUN 两个模式分别测
```

**io_uring 测试矩阵**：

| Test ID | 模式 | Payload | 说明 |
|---------|------|---------|------|
| 4a | 非 SQPOLL | 0B | 裸 io_uring 往返 |
| 4b | 非 SQPOLL | 128B | 小消息 |
| 4c | 非 SQPOLL | 4096B | 大消息 |
| 4d | SQPOLL | 0B | 零 syscall 模式 |
| 4e | SQPOLL | 128B | 零 syscall 小消息 |
| 4f | SQPOLL | 4096B | 零 syscall 大消息 |

---

### Hour 13-14：Unix Domain Socket 基准测试

```c
// bench_uds_pingpong.c
// AF_UNIX SOCK_STREAM，两个线程通过 socketpair 通信
// 发送 → 接收 → echo → 测量往返时间

// 测试配置：
// payload 0B, 128B, 4096B
// 每次 10000 次往返
// 使用 send()/recv() 和 write()/read() 两种模式分别测试
```

作为"baseline（最低公共分母）"纳入论文——表明"如果不在乎安全性，最低的 IPC 延迟是多少"。

---

### Hour 15-16：数据整理 + 绘图准备

输出格式：

```
# agentrt IPC ping-pong latency (L1+L2, 128B payload, 10000 samples)
min:      1.2 μs
mean:     2.8 μs
P50:      2.1 μs
P90:      4.5 μs
P99:      8.3 μs
P99.9:   15.7 μs
max:     42.1 μs

# io_uring ping-pong latency (no SQPOLL, 128B, 10000 samples)
... (实际运行后填充)
```

绘图：

```
图 1：四个系统的 P50/P99 延迟对比柱状图
  x 轴：agentrt | io_uring | UDS | seL4(文献)
  y 轴：延迟 μs（log scale）
  两组柱：P50 | P99

图 2：agentrt 三个层次的延迟分解
  L1 only | L1+L2 | L1+L2+sandbox
  堆叠柱状图，展示每一层的开销
```

---

### Hour 17：论文图生成

```bash
# 使用 Python matplotlib 生成论文图
pip install matplotlib numpy

python3 plot_results.py latency_results.csv
# 输出：fig1_latency_comparison.png, fig2_agentrt_breakdown.png
```

---

### Hour 18-20：缓冲（处理意外问题）

- 编译问题导致测试失败
- 内核版本不支持某些特性
- 重新运行波动大的测试
- 补充额外的 payload 大小

---

## 预期结果（基于设计分析）

| 系统 | 128B payload P50 | 128B payload P99 | 说明 |
|------|-----------------|-----------------|------|
| agentrt L1 only | ~1.5μs | ~5μs | 裸 binder 往返 |
| agentrt L1+L2 | ~3μs | ~10μs | 含 L2 头初始化 + CRC32 |
| agentrt L1+L2+sandbox | ~5μs | ~15μs | 含 permission check |
| io_uring (非SQPOLL) | ~2μs | ~8μs | 有 syscall 开销 |
| io_uring (SQPOLL) | ~1μs | ~4μs | 零 syscall |
| UDS | ~4μs | ~15μs | AF_UNIX socketpair |
| seL4 (文献) | ~0.25μs | ~1μs | 纯微内核 IPC，最轻量 |

**论文的核心论点数据支撑**：

> "Agentrt IPC 在 L1+L2+sandbox 模式下延迟约 5μs，比纯 io_uring 慢 2.5x，但不带任何安全保护。
> 如果要在 io_uring 上加 capability check，需要额外 1 次往返（seL4 模式），实际延迟变成 ~3μs + 3μs = ~6μs。
> 因此 agentrt 的"capability folding"策略（一次往返完成安全+通信）在等效安全水平下优于 io_uring+cap_separate。"

---

## 需要编写的代码清单

| 文件 | LOC | 工时 | 难度 |
|------|-----|------|------|
| `bench_agentrt_ipc.c` | ~300 | 3h | 中（需理解 binder.c API） |
| `bench_io_uring_pingpong.c` | ~200 | 1h | 低（liburing API 标准） |
| `bench_uds_pingpong.c` | ~100 | 0.5h | 低（socket 基础） |
| `plot_results.py` | ~100 | 0.5h | 低（matplotlib 模板） |
| `run_all.sh` | ~50 | 0.5h | 低（shell 脚本） |

---

## 论文中对实验部分的诚实声明

> "All agentrt IPC benchmarks were measured on an Intel i7-12700K (32GB RAM, Linux 6.5) 
> with 10,000 iterations per data point. seL4 IPC latency is cited from published literature 
> (Klein et al., 2009; seL4 performance documentation) as we do not have a seL4 build 
> environment available. io_uring benchmarks use liburing-2.4. The benchmark code is 
> available at [GitHub link]."
