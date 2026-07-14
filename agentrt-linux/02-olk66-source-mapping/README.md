Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# OLK-6.6 源码映射

> **保密级别**: SPHARX Ltd 内部参考，**闭源不公开**
> **版本**: 0.1.1
> **最后更新**: 2026-07-07
> **源码基线**: Linux 6.6 内核源码

---

## 1. 本目录定位

本目录建立 **OLK-6.6 内核源码 → AirymaxOS 设计概念** 的精确映射。每份映射文档回答三个问题：

1. **OLK-6.6 源码中是什么**：源码位置、核心数据结构、关键函数、设计模式
2. **AirymaxOS 中对应什么**：AirymaxOS 设计文档中的对应概念、模块、接口
3. **如何参考但不照搬**：AirymaxOS 在参考基础上做了哪些差异化设计（基于微内核思想 + IRON-9 v2 代码共享边界）

---

## 2. 文档清单

| 文档 | OLK-6.6 源码 | AirymaxOS 对应 | 优先级 |
|------|-------------|---------------|--------|
| `01-sched-ext-mapping.md` | `kernel/sched/ext.c` + `include/linux/sched/ext.h` | SCHED_AGENT BPF 策略 + MicroCoreRT 调度语义 | P0 |
| `02-io-uring-mapping.md` | `io_uring/io_uring.c` + `include/uapi/linux/io_uring.h` | AgentsIPC IPC 传输 + io_uring OP 扩展 | P0 |
| `03-bpf-mapping.md` | `kernel/bpf/core.c` + `kernel/bpf/syscall.c` | eBPF 可观测探针 + Cupolas L1 规则层 | P0 |
| `04-mm-mapping.md` | `mm/mmap.c` + `mm/vmscan.c` + `include/linux/mm.h` | MemoryRovol L1-L4 记忆卷载 | P1 |
| `05-security-mapping.md` | `security/security.c` + `security/landlock/` + `security/capability.c` | Cupolas 安全策略可插拔 + capability | P0 |

---

## 3. 映射原则

### 3.1 源码引用规范

映射文档引用 OLK-6.6 源码时使用以下格式：

```
OLK-6.6: kernel/sched/ext.c:1234  — sched_bpf_dispatch()
```

- 路径相对于 Linux 6.6 内核源码
- 行号尽量精确（允许 ±20 行误差，因版本微调）
- 函数/结构体名用 `code` 标记

### 3.2 差异化设计声明

每个映射文档必须包含 **"AirymaxOS 差异化设计"** 章节，明确说明 AirymaxOS 在参考 OLK-6.6 基础上做了哪些不同的设计决策，以及为什么（基于微内核思想 / IRON-9 v2 / 智能体工作负载适配）。

### 3.3 IRON-9 v2 代码共享边界

映射文档必须标注每个参考点的 IRON-9 v2 层次：

| 层次 | 标注 | 含义 |
|------|------|------|
| 共享契约层 | `[SC]` | AirymaxOS 与 agentrt 共享此接口契约（如 IPC 消息头） |
| 语义同源层 | `[SS]` | API 签名同源，实现独立（如调度语义） |
| 完全独立层 | `[IND]` | AirymaxOS 专属，不与 agentrt 共享 |

---

## 4. 与开源文档的关系

- 映射文档是**闭源参考**，不对外发布
- 开源设计文档（`docs/AirymaxOS/`）引用映射结论时，必须用 AirymaxOS 自身语言表述（BAN-INTERNAL-005）
- 开源文档中**严禁**出现 OLK-6.6 源码路径、行号、函数名等直接引用

---

> **文档结束** | SPHARX Ltd 内部参考 | 闭源不公开
