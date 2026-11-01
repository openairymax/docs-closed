Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# 微内核设计参考

> **版本**: 0.1.1
> **最后更新**: 2026-07-07
> **理论基础**: seL4 / Zircon / Minix3 / L4

---

## 1. 本目录定位

本目录存放微内核设计思想的深度参考文档，为 AirymaxOS 的微内核化改造策略提供理论支撑。AirymaxOS 不是从零开发微内核，而是基于 Linux 6.6 内核基线进行微内核化改造——这一策略需要深度理解三代微内核的设计精髓。

---

## 2. 文档清单

| 文档 | 主题 | 参考来源 | AirymaxOS 对应 |
|------|------|---------|---------------|
| `01-sel4-reference.md` | seL4 微内核设计参考 | seL4 形式化验证 + capability | Cupolas capability + tests-linux 形式化验证 |
| `02-zircon-reference.md` | Zircon 微内核设计参考 | Zircon handle/channel/VMO | AgentsIPC 消息传递 + MemoryRovol VMO 抽象 |
| `03-minix3-reference.md` | Minix3 微内核设计参考 | Minix3 用户态服务 + 自愈 | services 用户态服务化 |
| `04-microkernel-strategy.md` | AirymaxOS 微内核化改造策略对照 | 上述三者 + Liedtke minimality | 10-architecture/03-microkernel-strategy（开源） |
| `05-sel4-extension-plan.md` | seL4 拓展型改造方案（四大工程思想 → agent-linux 微内核化） | seL4 `src/`、`libsel4/`、`include/`、`tools/`、`manual/` | 10-architecture/03-microkernel-strategy（开源）+ 微内核化实施路线 |

---

## 3. 三代微内核演进脉络

| 代 | 代表 | 核心贡献 | IPC 性能 | AirymaxOS 借鉴点 |
|----|------|---------|---------|------------------|
| 第一代 | Mach (1986) | 验证微内核可行性 | 慢（性能损失 67%） | 教训：IPC 性能是生命线 |
| 第二代 | L4 / QNX | Liedtke 精简 IPC，寄存器传递 | 比 Mach 快 20 倍 | Liedtke minimality principle |
| 第三代 | seL4 / Zircon | 安全优先，capability，形式化验证 | 接近原生性能 | capability + 形式化验证 |

---

## 4. Liedtke Minimality Principle

> "A concept is tolerated inside the microkernel only if moving it outside the kernel, i.e., permitting competing implementations, would prevent the implementation of the system's required functionality."

**核心思想**：微内核应该尽可能小，任何可以在用户态实现的功能都不应该在内核态。

AirymaxOS 落地：MicroCoreRT 极简内核只保留 IPC、内存、任务、时间四个原子机制（K-1 内核极简原则）。

---

## 5. 与正式设计文档的关系

- `04-microkernel-strategy.md` 是 `docs/docs-linux/10-architecture/03-microkernel-strategy.md` 的深化参考版
- 本目录参考版可引用具体微内核源码与论文细节，正式设计文档以 AirymaxOS 自身语言表述
- seL4/Zircon/Minix3 名称在正式设计文档中可保留（公开学术资料）；其源码级实现细节参考集中于本目录维护

---

> **文档结束** | AgentRT 开源维护团队
