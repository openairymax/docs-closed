Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# openEuler 技术规范参考

> **保密级别**: SPHARX Ltd 内部参考，**闭源不公开**
> **版本**: 0.2.0
> **最后更新**: 2026-07-30
> **适用范围**: AirymaxOS 架构委员会 + 内核开发组

---

## 1. 本目录定位

本目录存放对 openEuler（OLK-6.6 内核基线）技术规范的**深度参考文档**。openEuler 社区在 Linux 6.6 基线上沉淀了大量企业级内核工程实践，对 AirymaxOS 的以下设计具有直接参考价值：

1. **调度器**：EEVDF + sched_ext 可插拔调度框架
2. **异步 I/O**：io_uring 零拷贝异步 I/O 机制
3. **可编程扩展**：eBPF 内核可编程子系统
4. **内存管理**：MGLRU 多代 LRU + CXL 内存扩展
5. **安全子系统**：LSM 框架 + Landlock + capability
6. **IPC 子系统**：消息队列、共享内存、信号量
7. **Rust 内核支持**：Rust 内核模块编译与安全抽象
8. **编码规范与工程标准**：openEuler 编码规范对照

---

## 2. 文档清单

| 文档 | 主题 | OLK-6.6 源码位置 | AirymaxOS 对应模块 |
|------|------|------------------|-------------------|
| `01-scheduler-spec.md` | 调度器技术规范（EEVDF + sched_ext） | `kernel/sched/ext.c`、`kernel/sched/fair.c` | 40-dataflows/04-scheduling-flow、MicroCoreRT |
| `02-io-uring-spec.md` | io_uring 异步 I/O 规范 | `io_uring/io_uring.c`、`include/uapi/linux/io_uring.h` | 40-dataflows/03-ipc-flow、AgentsIPC |
| `03-ebpf-spec.md` | eBPF 可编程扩展规范 | `kernel/bpf/core.c`、`include/linux/bpf.h` | 90-observability/02-ebpf-probes |
| `04-memory-mgmt-spec.md` | 内存管理规范（MGLRU + CXL） | `mm/mmap.c`、`mm/vmscan.c` | 40-dataflows/02-memory-flow、MemoryRovol |
| `05-security-spec.md` | 安全子系统规范（LSM + capability） | `security/security.c`、`security/landlock/` | 110-security、Cupolas |
| `06-ipc-spec.md` | IPC 子系统规范 | `ipc/msg.c`、`ipc/mqueue.c` | 30-interfaces/02-ipc-protocol |
| `07-rust-support-spec.md` | Rust 内核模块支持规范 | `rust/`、`Documentation/rust/` | 70-build-system、多语言支持 |
| `08-coding-standard-spec.md` | 编码规范与工程标准对照 | `Documentation/process/coding-style.rst` | 50-engineering-standards |
| `10-olk66-vanilla-diff.md` | OLK-6.6 与 vanilla 6.6.144 差异对比（LAYER 方案依据） | `openeuler/OLK-6.6` git ref | 10-architecture/00-alk-kernel-overview |
| `11-layer-feasibility-study.md` | LAYER 方案可行性论证（技术/维护/法律/工程四维度） | `openeuler/OLK-6.6` git ref | 10-architecture/00-alk-kernel-overview |
| `12-build-and-flash-strategy.md` | 编译与烧录策略（全面复用 openEuler 构建体系） | openEuler 24.03 LTS 构建工具链 | 10-architecture/00-alk-kernel-overview |

---

## 3. 使用规范

1. **先参考本目录**：修订开源设计文档前，先查阅对应子系统的 openEuler 技术规范参考
2. **消化吸收**：openEuler 内容必须经过消化吸收，转化为 AirymaxOS 自身技术语言
3. **隔离铁律**：开源文档（`docs/docs-linux/`）中严禁出现 openEuler 描述（BAN-INTERNAL-002）
4. **不对外发布**：本目录所有文档不包含在开源 LICENSE 范围内（BAN-INTERNAL-004）

---

## 4. IRON-9 v2 下的参考边界

| 层次 | 参考方式 | 说明 |
|------|---------|------|
| 共享契约层 | 参考 openEuler UAPI 设计规范 | 不直接复制代码，仅参考接口设计思想 |
| 语义同源层 | 参考 openEuler 子系统实现思路 | 形成 AirymaxOS 自己的实现方案 |
| 完全独立层 | 不参考 openEuler 对应实现 | AirymaxOS 专属机制独立设计 |

---

> **文档结束** | SPHARX Ltd 内部参考 | 闭源不公开
