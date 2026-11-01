Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agent-linux（AirymaxOS）系统性全面审查报告 v2.1

> **文档定位**： agent-linux（AirymaxOS，极境智能体操作系统）整体方案 v2.1 系统性复审——在 v1.0（综合评分 80/B）基础上的第三轮深化审查，聚焦"v1.0 问题修复验证 + 内部冲突 + 技术点唯一性 + openEuler 实践 + seL4 吸收 + 开发就绪度 + 细节完成度"七大维度。\
> **保密级别**： SPHARX Ltd 内部参考，**闭源不公开**\
> **版本**： 2.1（2026-07-13）\
> **审查范围**： `/docs/AirymaxOS/`（开源设计文档）+ `/docs-closed/agent-linux-dev/`（闭源工程文档）\
> **审查方法**： 源文档逐行重读 + Grep 机器检查 + 闭源/开源交叉验证 + 字节级累加验证\
> **证据要求**： 所有结论附 `文件路径:行号` 证据\
> **SPDX-License-Identifier**： AGPL-3.0-or-later OR Apache-2.0

---

## 目录

- [1. 执行摘要（v1.0 vs v2.1 评分对比表）](#1-执行摘要v10-vs-v21-评分对比表)
- [2. v1.0 问题修复验证（4 P0 + 5 P1 + 5 P2 逐项验证）](#2-v10-问题修复验证4-p0--5-p1--5-p2-逐项验证)
- [3. 内部冲突检查](#3-内部冲突检查)
- [4. 技术点标准唯一性验证](#4-技术点标准唯一性验证)
- [5. openEuler 工程实践评估](#5-openeuler-工程实践评估)
- [6. seL4 工程思想吸收评估](#6-sel4-工程思想吸收评估)
- [7. 开发就绪度评估](#7-开发就绪度评估)
- [8. 技术细节完成度检查](#8-技术细节完成度检查)
- [9. 综合评分与改进建议](#9-综合评分与改进建议)

---

## 1. 执行摘要（v1.0 vs v2.1 评分对比表）

### 1.1 评分对比

| 评分维度 | v1.0 | v2.1 | 变化 | 主要原因 |
|---------|------|------|------|---------|
| 内部冲突 | 78 | **62** | -16 | 4 项 P0 冲突全部未修复，5 项 P1 冲突全部未修复 |
| 技术点唯一性 | 85 | **68** | -17 | 128B 消息头实际 112B、syscall 数量 12 vs 10、IPC 操作码 3 套不兼容 |
| openEuler 工程实践 | 78 | **80** | +2 | OLK-6.6 源码映射文档含代码示例，Makefile/Kconfig 扩展到位 |
| seL4 工程思想 | 82 | **80** | -2 | 三态机/doReplyTransfer/Fastpath/MCS 排除均到位，但 ES-SEL4-7 分类冲突仍在 |
| 开发就绪度 | 78 | **62** | -16 | 3 项 P0 阻塞性缺陷（IPC 头布局/syscall 数量/操作码碎片化） |
| 细节完成度 | 75 | **68** | -7 | Euler API 兼容性缺失、里程碑命名不一致、io_uring 互斥标志问题 |
| **综合评分** | **80/B** | **70/C+** | **-10** | 核心技术契约层存在系统性 SSoT 违反 |

### 1.2 核心结论

agent-linux 整体方案经 v2.1 系统性复审，**综合评分从 80/B 降至 70/C+**。v1.0 识别的 **4 项 P0-CRITICAL 问题全部未修复**，**5 项 P1-MAJOR 问题全部未修复**，**5 项 P2-MINOR 问题中 3 项未修复、2 项部分修复**。方案在 IPC 协议契约、syscall 编号体系、子仓命名规范三大核心技术点存在系统性 SSoT 违反，**不具备直接启动全面开发的条件**。

**与 v1.0 的根本差异**：v1.0 评分为 80/B 时假定 v1.0 问题已被识别并待修复；v2.1 验证发现这些问题在 v1.0→v2.1 迭代中**未被处置**，因此实际就绪度显著低于 v1.0 评估。

---

## 2. v1.0 问题修复验证（4 P0 + 5 P1 + 5 P2 逐项验证）

### 2.1 P0-CRITICAL 问题验证

#### P0-1：IPC 消息头布局互不兼容 —— **未修复（严重）**

**v1.0 描述**：contracts.md 定义 version/type/payload_len/flags/src_pid/dst_pid 字段，SSoT Layout C 定义 opcode/flags/trace_id/timestamp_ns/src_task/dst_task 字段。contracts.md 总大小仅 112 字节却声称 128B。

**v2.1 验证**：

**SSoT Layout C 定义**（`50-engineering-standards/120-cross-project-code-sharing.md:343-353`）：
```c
struct airy_ipc_msg_hdr {
    __u32  magic;         /* offset 0, 4 bytes */
    __u16  opcode;        /* offset 4, 2 bytes */
    __u16  flags;         /* offset 6, 2 bytes */
    __u64  trace_id;      /* offset 8, 8 bytes */
    __u64  timestamp_ns;  /* offset 16, 8 bytes */
    __u64  src_task;      /* offset 24, 8 bytes */
    __u64  dst_task;      /* offset 32, 8 bytes */
    __u32  payload_len;   /* offset 40, 4 bytes */
    __u8   reserved[84];  /* offset 44, 84 bytes */
};  /* 总计 = 4+2+2+8+8+8+8+4+84 = 128 bytes ✓ */
```
静态断言 `_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128, ...)` 正确（line 355-356）。

**contracts.md 实际字段表**（`50-engineering-standards/20-contracts/contracts.md:49-57`）：

| 字段 | 偏移 | 长度 | 累加 |
|------|------|------|------|
| magic | 0 | 4 | 4 |
| version | 4 | 2 | 6 |
| type | 6 | 2 | 8 |
| payload_len | 8 | 4 | 12 |
| flags | 12 | 4 | 16 |
| src_pid | 16 | 4 | 20 |
| dst_pid | 20 | 4 | 24 |
| trace_id | 24 | 8 | 32 |
| timestamp_ns | 32 | 8 | 40 |
| reserved | 40 | 72 | **112** |

**总大小 = 4+2+2+4+4+4+4+8+8+72 = 112 字节**，但文档声称 128B。**字段集完全不兼容**：contracts.md 使用 version/type/src_pid/dst_pid（旧布局），SSoT 使用 opcode/src_task/dst_task（新布局）。

**contracts.md 内部自相矛盾**：
- `contracts.md:42`（SSoT 声明）：声明"字段顺序为 magic/opcode/flags/trace_id/timestamp_ns/src_task/dst_task/payload_len/reserved[84]"——与 SSoT Layout C 一致
- `contracts.md:49-57`（字段语义表）：实际使用 magic/version/type/payload_len/flags/src_pid/dst_pid/trace_id/timestamp_ns/reserved[72]——与 SSoT Layout C 不兼容
- `contracts.md:87-88`（mermaid 图）：使用 src_pid/dst_pid
- `contracts.md:108`（图注）："src/dst_pid 标识通信双方"

**结论**：contracts.md 存在**文件内部自相矛盾**（line 42 声明 SSoT 布局，lines 49-57 使用旧布局），且与 SSoT Layout C 不兼容。总大小 112 字节而非 128 字节。**P0-1 未修复**。

---

#### P0-2：syscall 数量自相矛盾 —— **未修复**

**v1.0 描述**：01-kernel.md §1.5 声称"从 12 缩减到 10"，但 §1.3 和 §10.1.7 均显示 12 个核心 syscall。

**v2.1 验证**：

- `20-modules/01-kernel.md:99`（§1.3）：`agent-linux 目标：12 核心 + 12 预留 = 24 槽位`
- `20-modules/01-kernel.md:101-115`（§1.3）：列出编号 0-11 共 **12 个**核心 syscall
- `20-modules/01-kernel.md:117`：`airy_sys_reply 完齐 seL4 master 模式 8 个 activity syscall`
- `20-modules/01-kernel.md:463`（§5.5）：`将 syscall 数量从 12 缩减到 10` ← **矛盾点**
- `20-modules/01-kernel.md:786`（§10.1.7）：`12 核心 + 12 预留 = 24 槽位`

**冲突本质**：§1.3 明确列出 12 个核心 syscall（编号 0-11），§10.1.7 确认 12 核心，但 §5.5 声称"从 12 缩减到 10"。capability invocation 统一入口（`airy_sys_call`）确实消除了独立 syscall 的需求，但实际 syscall 数量仍为 12（`airy_sys_call` 本身就是 12 个之一），不存在"缩减到 10"的情况。

**结论**：**P0-2 未修复**。`01-kernel.md:463` 的"从 12 缩减到 10"与 §1.3（12 核心）和 §10.1.7（12 核心 + 12 预留）直接矛盾。

---

#### P0-3：子仓库命名系统性矛盾 —— **未修复**

**v1.0 描述**：闭源文档仍使用 `airymaxos-kernel`/`airymaxos-services` 等带前缀名称，开源文档一致使用 `kernel`/`services` 等无前缀名称。BAN-360 甚至禁止不使用前缀。

**v2.1 验证**：

**开源文档**（已统一去除前缀）：
- `10-architecture/06-directory-structure.md:175-184`：8 子仓映射表使用裸名（kernel / services / security / memory / cognition / cloudnative / system / tests-linux）
- `10-architecture/06-directory-structure.md:294`：`禁止前缀：airymaxos_*（已废弃，详见 project_memory）`

**闭源文档**（仍大量使用前缀）：
- Grep 统计：`docs-closed/agent-linux-dev/` 下 `airymaxos-` 出现 **401 处**，分布在 37 个文件
- `agent-linux基本工程标准规范.md`：37 处（主权威文档）
- `agent-linux开发路线和进度.md`：4 处
- `README.md`：1 处
- 各参考/设计/审查目录：分布在 34 个历史文件中

**BAN-360 验证**：
- Grep `BAN-360` 在整个 `OpenAirymax/` 目录：**无匹配**
- `09-ssot-registry.md:396-411`（第 5 章 OS-BAN 禁止规则）：列出 OS-BAN-001~011，**无 BAN-360**
- `10-architecture/04-engineering-baseline.md:31`：引用 `BAN-361`（基线锁定相关），非 BAN-360
- **BAN-360 已不存在**于当前文档体系中（已删除或重编号），但闭源文档仍使用 `airymaxos-` 前缀

**结论**：**P0-3 未修复**。BAN-360 本身已不存在（该规则被移除），但闭源文档仍有 401 处 `airymaxos-` 前缀，与开源文档裸名命名不一致。

---

#### P0-4：IPC 操作码碎片化 —— **未修复（严重）**

**v1.0 描述**：SSoT 定义 4 个操作码，02-services.md 定义 5 个，04-ipc-versioning.md 定义 11 个，性能/可观测性文档又定义不同的操作码。

**v2.1 验证**：

**SSoT 权威定义**（`120-cross-project-code-sharing.md:309-313`）—— 4 个操作码：
```
AIRY_IPC_OP_SEND       = 0
AIRY_IPC_OP_RECV       = 1
AIRY_IPC_OP_SEND_BATCH = 2
AIRY_IPC_OP_CANCEL     = 3
```

**02-services.md 定义**（`20-modules/02-services.md:317`）—— 5 个操作码（不兼容）：
```
AIRY_IPC_OP_* 宏（NOP / SEND / RECV / MSG_RING / SEND_ZC）
```
- 多出 NOP、MSG_RING、SEND_ZC，缺少 SEND_BATCH、CANCEL
- 与 SSoT 编号不兼容

**04-ipc-versioning.md 定义**（`160-compatibility/04-ipc-versioning.md:353-365` §8.1）—— 11 个操作码（完全不兼容）：

| 操作码 | 名称 | 值 |
|--------|------|----|
| AIRY_IPC_OP_NOP | v1.0 | 0x00 |
| AIRY_IPC_OP_HANDSHAKE | v1.0 | 0x01 |
| AIRY_IPC_OP_AGENT_CREATE | v1.0 | 0x10 |
| AIRY_IPC_OP_AGENT_DESTROY | v1.0 | 0x11 |
| AIRY_IPC_OP_ROVOL_MOUNT | v1.0 | 0x20 |
| AIRY_IPC_OP_ROVOL_UMOUNT | v1.0 | 0x21 |
| AIRY_IPC_OP_TOKEN_BUDGET | v1.0 | 0x30 |
| AIRY_IPC_OP_EVENT_SUBSCRIBE | v1.1 | 0x40 |
| AIRY_IPC_OP_EVENT_UNSUBSCRIBE | v1.1 | 0x41 |
| AIRY_IPC_OP_BATCH_SUBMIT | v1.2 | 0x50 |
| AIRY_IPC_OP_RELIABLE_SEND | v2.0 | 0x60 |

- SSoT 中 `SEND=0`，但 ipc-versioning.md 中 `NOP=0x00`、`HANDSHAKE=0x01`，编号完全不兼容
- ipc-versioning.md 还引用不存在的 `hdr->version` 字段（`04-ipc-versioning.md:88,383`），而 SSoT Layout C 无 version 字段
- ipc-versioning.md 定义 `AIRY_IPC_CQE_F_UNSUPPORTED` 标志（line 381），但 SSoT 仅定义 `AIRY_IPC_CQE_F_BUFFER/MORE/NOTIF`

**其他文档使用 SSoT 4 操作码**（一致）：
- `20-modules/01-kernel.md:746`：`AIRY_IPC_OP_SEND/RECV/SEND_BATCH/CANCEL`（4 个，与 SSoT 一致）
- `170-performance/03-ipc-performance.md:283`：使用 `AIRY_IPC_OP_SEND`
- `140-application-development/07-syscall-registry.md:781`：使用 `AIRY_IPC_OP_SEND`

**结论**：**P0-4 未修复（严重）**。存在 3 套互不兼容的操作码定义：SSoT（4 个，值 0-3）、services.md（5 个，名称不同）、ipc-versioning.md（11 个，值 0x00-0x60）。操作码编号互相冲突（如 SSoT SEND=0 vs ipc-versioning.md NOP=0x00）。

---

### 2.2 P1-MAJOR 问题验证

#### P1-1：双重宏命名 —— **未修复**

**v1.0 描述**：AIRY_IPC_HDR_SZ vs AIRY_IPC_MSG_HDR_SIZE 双重命名。

**v2.1 验证**（Grep 全 `docs/AirymaxOS/` 范围）：

**`AIRY_IPC_HDR_SZ`**（7 处）：
- `120-cross-project-code-sharing.md:306`：`#define AIRY_IPC_HDR_SZ 128`（SSoT 权威定义）
- `01-coding-standards.md:2969`：`#define AIRY_IPC_HDR_SZ 128`
- `20-modules/01-kernel.md:743,939`
- `10-coding-style/C_Cpp_coding_style.md:1323`
- `100-operations/02-configuration.md:561,566`

**`AIRY_IPC_MSG_HDR_SIZE`**（12 处）：
- `30-interfaces/02-ipc-protocol.md:36`：`#define AIRY_IPC_MSG_HDR_SIZE 128`
- `30-interfaces/04-coding-standard.md:138,169`
- `10-architecture/02-five-dimensional-principles.md:360`
- `40-dataflows/03-ipc-flow.md:798,858`
- `50-engineering-standards/40-integration/integration.md:364`
- `10-coding-style/Rust_coding_style.md:126`
- `20-modules/02-services.md:315`
- `10-coding-style/C_Cpp_coding_style.md:185,605`

**文件内部矛盾**：`C_Cpp_coding_style.md` 同时使用 `AIRY_IPC_HDR_SZ`（line 1323）和 `AIRY_IPC_MSG_HDR_SIZE`（lines 185, 605），同一文件内宏命名不统一。

**结论**：**P1-1 未修复**。两个宏在 19 处并存，SSoT 使用 `AIRY_IPC_HDR_SZ`（短名），但多数接口/数据流文档使用 `AIRY_IPC_MSG_HDR_SIZE`（长名）。

---

#### P1-2：字段命名不一致（src_task vs src_pid） —— **未修复**

**v1.0 描述**：字段命名不一致（src_task vs src_pid）。

**v2.1 验证**（Grep 全 `docs/AirymaxOS/` 范围）：

**`src_task` / `dst_task`**（SSoT 布局，23 处）：
- `30-interfaces/02-ipc-protocol.md:64-65,85-86,400,471`：消息头结构体使用 src_task/dst_task ✓
- `120-cross-project-code-sharing.md:349-350`：SSoT 定义 ✓
- `160-compatibility/04-ipc-versioning.md:97`：SSoT 声明 ✓
- `20-modules/02-services.md:320`、`01-coding-standards.md:2978-2997`、`Rust_coding_style.md:907-908`、`03-ipc-performance.md:287-288`、`01-deployment.md:568`

**`src_pid` / `dst_pid`**（旧布局，28 处）：
- `50-engineering-standards/20-contracts/contracts.md:53-54,87-88,108,222,224,228,287,292,297,300,333,340`：contracts.md 全文使用 src_pid/dst_pid
- `30-interfaces/02-ipc-protocol.md:278,280,308,328,329,483`：API 函数签名使用 dst_pid/src_pid
- `160-compatibility/04-ipc-versioning.md:269-270`：版本兼容矩阵使用 src_pid/dst_pid
- `40-dataflows/03-ipc-flow.md:185,570,571,745,746`：IPC 数据流使用 src_pid/dst_pid
- `170-performance/03-ipc-performance.md:635`：性能代码使用 src_pid

**文件内部矛盾**（3 个文件）：
1. `02-ipc-protocol.md`：消息头结构体用 src_task（line 64），API 函数用 dst_pid（line 280）——同一文件内两种命名
2. `04-ipc-versioning.md`：SSoT 声明用 src_task（line 97），兼容矩阵用 src_pid（line 269）——同一文件内两种命名
3. `03-ipc-performance.md`：消息填充用 src_task（line 287），权限校验用 src_pid（line 635）——同一文件内两种命名

**类型不一致**：SSoT 定义 src_task/dst_task 为 `__u64`（8 字节），但 contracts.md 定义 src_pid/dst_pid 为 `uint32_t`（4 字节）。不仅命名不同，类型宽度也不同。

**结论**：**P1-2 未修复**。src_task/dst_task（SSoT）与 src_pid/dst_pid（旧布局）在 51 处并存，3 个文件存在内部矛盾，且类型宽度不一致（u64 vs u32）。

---

#### P1-3：services.md 数量不匹配 —— **未修复**

**v1.0 描述**：标题 15+，实际 20。

**v2.1 验证**：

- `20-modules/02-services.md:322`（§6.2 标题）：`### 6.2 [SS] 语义同源层——15+ 项 API 映射`
- `20-modules/02-services.md:326`（§6.2.1）：`12 daemons 语义同源（12 项）` → 列出 12 个 daemon
- `20-modules/02-services.md:343`（§6.2.2）：`io_uring IPC 通信原语同源（8 项）` → 列出 8 个原语
- 实际总数 = 12 + 8 = **20 项**

标题声明"15+"，实际为 20 项。"15+"在语义上不错误（20 ≥ 15），但作为工程规范文档，应精确标注"20 项"而非模糊的"15+"。

**结论**：**P1-3 未修复**。标题仍为"15+"，实际 20 项。

---

#### P1-4：contracts.md 112→128 字节 —— **未修复**

**v1.0 描述**：contracts.md 消息头仅 112 字节，非 128 字节。

**v2.1 验证**：

已在 P0-1 中详细验证。contracts.md 字段表（lines 49-57）累加：

```
magic(4) + version(2) + type(2) + payload_len(4) + flags(4) 
+ src_pid(4) + dst_pid(4) + trace_id(8) + timestamp_ns(8) + reserved(72) 
= 112 字节
```

文档多处声称 128B（line 16, 29, 42, 108），但字段实际累加为 112 字节。差距 16 字节源于：
- 旧布局 reserved 为 72 字节，SSoT 新布局 reserved 为 84 字节（差 12 字节）
- 旧布局 src_pid+dst_pid 各 4 字节共 8 字节，SSoT src_task+dst_task 各 8 字节共 16 字节（差 8 字节）
- 旧布局无 opcode 字段，SSoT 有 opcode 2 字节（但旧布局有 version+type 共 4 字节 vs SSoT opcode+flags 共 4 字节，此部分持平）
- 净差异 = 12 + 8 = 20 字节，但旧布局比新布局少 16 字节（112 vs 128），因字段排列不同

**结论**：**P1-4 未修复**。contracts.md 字段累加为 112 字节，非 128 字节。

---

#### P1-5：控制平面数量误导（7 vs 12） —— **未修复**

**v1.0 描述**：01-kernel.md §6.6 控制平面数量误导（7 vs 12）。

**v2.1 验证**：

- `20-modules/01-kernel.md:160`：`IPC 数据流（控制面）| 8 个 IPC 原语 syscall（Call/Send/Recv/NBSend/NBRecv/ReplyRecv/Yield/Reply）` → **8 个**
- `20-modules/01-kernel.md:477`（§6.1）：`控制面 | ... | 7 个 IPC 原语 syscall` → **7 个**
- `20-modules/01-kernel.md:555`（§6.6）：`控制面（7 个 IPC 原语 syscall）` → **7 个**
- `20-modules/01-kernel.md:786`（§10.1.7）：`8 IPC 原语 + 3 控制原语 + 1 通知原语` → **8 个**
- `20-modules/01-kernel.md:787`（§10.1.7）：`编号 0-6 ... 7 个 IPC 原语` → **7 个**（不含 Reply）
- `20-modules/01-kernel.md:789`（§10.1.7）：`编号 10-11 ... 1 个 IPC 原语 + 1 个通知原语` → Reply 单独计数

**冲突本质**：IPC 原语实际为 8 个（Call/Send/Recv/NBSend/NBRecv/ReplyRecv/Yield/Reply），但 §6.1 和 §6.6 声称 7 个（将 Reply 编号 10 单独列出不计入 0-6 的 7 个）。§1.3 和 §10.1.7 总计确认 8 个。这是同一文档内的数量矛盾。

**结论**：**P1-5 未修复**。§6.1（line 477）和 §6.6（line 555）声称 7 个 IPC 原语，但 §1.3（line 160）和 §10.1.7（line 786）确认 8 个。

---

### 2.3 P2-MINOR 问题验证

#### P2-1：io_uring SETUP 标志表列出互斥标志为"必须启用" —— **未修复**

**v1.0 描述**：io_uring SETUP 标志表列出互斥标志为"必须启用"。

**v2.1 验证**（`40-dataflows/03-ipc-flow.md:131-159` §2.5）：

- Line 141：`COOP_TASKRUN | 5.19 | ✅ | 避免任务上下文异步切换 | 与 DEFER_TASKRUN 二选一`
- Line 146：`DEFER_TASKRUN | 6.0 | ✅ | task_work 延迟到 enter 执行 | OS-IPC-003`
- Line 155（启用策略）：`必须启用（12 项）：... COOP_TASKRUN ... DEFER_TASKRUN ...`

**冲突**：COOP_TASKRUN 与 DEFER_TASKRUN 互斥（line 141 明确标注"二选一"），但两者均被列入"必须启用"的 12 项清单（line 155）。不可能同时启用两个互斥标志。

**结论**：**P2-1 未修复**。互斥标志 COOP_TASKRUN 和 DEFER_TASKRUN 同时列入"必须启用"清单。

---

#### P2-2：ES-OLK 映射缺乏具体代码示例 —— **部分修复**

**v1.0 描述**：ES-OLK 映射缺乏具体代码示例。

**v2.1 验证**：

- 闭源总纲 `agent-linux基本工程标准规范.md:990-1008`（§12.4）：ES-OLK-1~13 表格列出工程思想、核心内涵、在规范中的体现，但**无内联代码示例**
- `docs-closed/agent-linux-dev/10-references/olk66-source-mapping/` 目录含 7 个映射文档：
  - `01-sched-ext-mapping.md`：含源码路径、Kconfig 配置示例、数据结构映射
  - `02-io-uring-mapping.md`、`03-bpf-mapping.md` 等：提供 OLK-6.6 源码到 AirymaxOS 设计的映射
- 映射文档使用 IRON-9 v2 三层标注（[SC]/[SS]/[IND]），含源码行数和路径

**改进**：OLK-6.6 源码映射文档已建立，包含代码路径和配置示例。
**不足**：映射文档不直接引用 ES-OLK-1~13 编号（Grep `ES-OLK` 在 `10-references/olk66-source-mapping/` 无匹配），ES-OLK 编号与源码映射之间的追溯链断裂。

**结论**：**P2-2 部分修复**。源码映射文档已含代码示例，但 ES-OLK 编号未在映射文档中引用，追溯链不完整。

---

#### P2-3：seL4 借鉴仅限架构层的约束在 contracts.md 中被违反 —— **部分修复**

**v1.0 描述**：seL4 借鉴仅限架构层的约束在 contracts.md 中被违反。

**v2.1 验证**：

- `agent-linux基本工程标准规范.md:1024`（OS-IRON-012）：`seL4 工程思想的借鉴仅限架构层（ES-SEL4-1~5），不包括编码风格层（4 空格 / camelCase / 重度 typedef）和接口契约层`
- contracts.md 已在 line 42 添加 SSoT 声明，将 IPC 消息头布局指向 SSoT Layout C，不再就地重定义
- 但 contracts.md lines 49-57 的字段表仍使用旧布局（version/type/src_pid/dst_pid），这些字段命名借鉴了 seL4 的接口契约层概念（PID 模型），而非架构层的 task 模型

**改进**：contracts.md line 42 已添加 SSoT 声明，形式上向架构层约束对齐。
**不足**：字段表（lines 49-57）仍使用旧布局，实际内容未对齐 SSoT，seL4 借鉴的边界约束在内容层面仍被违反。

**结论**：**P2-3 部分修复**。形式上已添加 SSoT 声明，但字段表内容仍违反约束。

---

#### P2-4：各模块里程碑命名约定不一致 —— **未修复**

**v1.0 描述**：各模块里程碑命名约定不一致。

**v2.1 验证**（Grep `20-modules/` 里程碑标题）：

| 文件 | 里程碑范围 | 项数 |
|------|----------|------|
| `01-kernel.md:33,898` | M1-M6 | 6 |
| `02-services.md:26,477` | M1-M6 | 6 |
| `04-memory.md:26,521` | M0-M8 | 9 |
| `05-cognition.md:26` | M0-M8 | 9 |
| `07-system.md:26,486` | M1-M6 | 6 |
| `08-tests.md:26,527` | M1-M6 | 6 |
| `20-modules/README.md:291` | M0-M8 | 9 |

**冲突**：部分模块使用 M1-M6（6 项），部分使用 M0-M8（9 项），`README.md` 声明 M0-M8（9 项）。命名范围不一致，审查者无法确定统一里程碑体系是 6 项还是 9 项。

**结论**：**P2-4 未修复**。3 个模块使用 M1-M6，3 个模块使用 M0-M8，README 使用 M0-M8。

---

#### P2-5：03-ipc-flow.md 引用不存在的 src_pid/dst_pid —— **未修复**

**v1.0 描述**：03-ipc-flow.md 引用不存在的 src_pid/dst_pid。

**v2.1 验证**（Grep `40-dataflows/03-ipc-flow.md`）：

- Line 185：`| src_pid / dst_pid | agent-linux 扩展（io_uring 无此字段） | [IND] 独立扩展 |`
- Line 570：`| 1 | 本地提交 | 超节点 1 | 写入 SQE（dst_pid 跨节点） | < 2μs |`
- Line 571：`| 2 | 路由判断 | 内核 | 检查 dst_pid 所属节点 | < 1μs |`
- Line 745：`"src_pid": 1234,`
- Line 746：`"dst_pid": 5678,`

SSoT Layout C 消息头定义 `src_task`/`dst_task`（`__u64`），无 `src_pid`/`dst_pid` 字段。03-ipc-flow.md 引用了 SSoT 中不存在的字段名。

**结论**：**P2-5 未修复**。03-ipc-flow.md 在 5 处引用 src_pid/dst_pid，这些字段在 SSoT Layout C 中不存在。

---

### 2.4 v1.0 问题修复验证汇总

| 编号 | 问题 | 等级 | v2.1 状态 | 证据 |
|------|------|------|----------|------|
| P0-1 | IPC 消息头布局互不兼容 | P0 | **未修复** | §2.1 P0-1 |
| P0-2 | syscall 数量自相矛盾（12 vs 10） | P0 | **未修复** | §2.1 P0-2 |
| P0-3 | 子仓库命名系统性矛盾 | P0 | **未修复** | §2.1 P0-3 |
| P0-4 | IPC 操作码碎片化（4/5/11 套） | P0 | **未修复** | §2.1 P0-4 |
| P1-1 | 双重宏命名 | P1 | **未修复** | §2.2 P1-1 |
| P1-2 | 字段命名不一致（src_task vs src_pid） | P1 | **未修复** | §2.2 P1-2 |
| P1-3 | services.md 数量不匹配（15+ vs 20） | P1 | **未修复** | §2.2 P1-3 |
| P1-4 | contracts.md 112→128 字节 | P1 | **未修复** | §2.2 P1-4 |
| P1-5 | 控制平面数量误导（7 vs 8） | P1 | **未修复** | §2.2 P1-5 |
| P2-1 | io_uring 互斥标志列为"必须启用" | P2 | **未修复** | §2.3 P2-1 |
| P2-2 | ES-OLK 映射缺乏代码示例 | P2 | **部分修复** | §2.3 P2-2 |
| P2-3 | seL4 约束在 contracts.md 被违反 | P2 | **部分修复** | §2.3 P2-3 |
| P2-4 | 里程碑命名约定不一致 | P2 | **未修复** | §2.3 P2-4 |
| P2-5 | 03-ipc-flow.md 引用不存在字段 | P2 | **未修复** | §2.3 P2-5 |

**汇总**：14 项问题中 **0 项已修复**、**2 项部分修复**、**12 项未修复**。

---

## 3. 内部冲突检查

### 3.1 IPC 协议层系统性冲突（P0 级，新发现深化）

**冲突全景**：IPC 协议在消息头布局、字段命名、操作码、宏命名、标志位 5 个维度存在系统性冲突。

| 冲突维度 | SSoT 权威定义 | 冲突文档 | 冲突详情 |
|---------|-------------|---------|---------|
| 消息头布局 | 128B, 9 字段（Layout C） | contracts.md | 112B, 10 字段（旧布局） |
| 字段命名 | src_task/dst_task（u64） | contracts.md, 03-ipc-flow.md, 02-ipc-protocol.md (API) | src_pid/dst_pid（u32） |
| 操作码 | 4 个（SEND/RECV/SEND_BATCH/CANCEL, 值 0-3） | services.md, 04-ipc-versioning.md | 5 个 / 11 个（值 0x00-0x60） |
| 宏命名 | AIRY_IPC_HDR_SZ | 02-ipc-protocol.md, 03-ipc-flow.md 等 | AIRY_IPC_MSG_HDR_SIZE |
| 标志位 | AIRY_IPC_F_NOWAIT/SIGNAL, AIRY_IPC_CQE_F_BUFFER/MORE/NOTIF | contracts.md, 04-ipc-versioning.md | AIRY_IPC_FLAG_ZEROCOPY/CAP_CARRY/COMPRESS/ENCRYPT/URGENT/NOREPLY, AIRY_IPC_CQE_F_UNSUPPORTED |

**新发现**：
1. `04-ipc-versioning.md:88,383` 引用 `hdr->version` 字段，但 SSoT Layout C **无 version 字段**（已被 opcode 替代）
2. `04-ipc-versioning.md:727` 声明"version 字段"为 [SC] 共享契约，但 SSoT 无此字段
3. contracts.md 使用 `AIRY_IPC_FLAG_*` 标志前缀（line 63-68），SSoT 使用 `AIRY_IPC_F_*` 前缀（line 317-318）——标志位命名前缀也不一致

### 3.2 syscall 体系冲突（P0 级，延续）

- §1.3: 12 核心 syscall（编号 0-11）
- §5.5: "从 12 缩减到 10"
- §6.1/§6.6: 7 个 IPC 原语
- §10.1.7: 8 IPC 原语 + 3 控制原语 + 1 通知原语 = 12

**三重冲突**：12 vs 10 vs 7（IPC 原语 7 vs 8）。

### 3.3 子仓命名冲突（P0 级，延续）

- 开源文档：裸名（kernel, services, ...）
- 闭源文档：`airymaxos-` 前缀（401 处）
- 函数前缀：开源使用 `airy_*`，闭源 OS-STD-005（`agent-linux基本工程标准规范.md:167`）仍声明 `airymaxos_*`

### 3.4 内部冲突检查小结

| 冲突类别 | 等级 | 状态 | 影响范围 |
|---------|------|------|---------|
| IPC 消息头布局（112B vs 128B） | P0 | 未修复 | contracts.md 全文 + ipc-versioning.md version 字段 |
| IPC 操作码（4/5/11 套） | P0 | 未修复 | services.md + ipc-versioning.md |
| IPC 字段命名（src_task vs src_pid） | P0 | 未修复 | 6+ 文件 51 处 |
| syscall 数量（12 vs 10 vs 7） | P0 | 未修复 | 01-kernel.md §1.3/§5.5/§6.1/§6.6/§10.1.7 |
| 子仓命名（裸名 vs airymaxos-） | P0 | 未修复 | 闭源 401 处 vs 开源裸名 |
| 宏命名（HDR_SZ vs MSG_HDR_SIZE） | P1 | 未修复 | 19 处 |
| 标志位命名（F_* vs FLAG_*） | P1 | 新发现 | contracts.md vs SSoT |
| 控制平面 IPC 原语数（7 vs 8） | P1 | 未修复 | 01-kernel.md §6.1/§6.6 vs §1.3/§10.1.7 |
| 里程碑范围（M1-M6 vs M0-M8） | P2 | 未修复 | 6 个模块文件 |

---

## 4. 技术点标准唯一性验证

### 4.1 IPC magic 值（0x41524531 'ARE1'） —— **唯一 ✓**

- SSoT 权威定义：`120-cross-project-code-sharing.md:302-303`：`#define AIRY_IPC_MAGIC 0x41524531u`
- contracts.md:48：`魔数 0x41524531（'ARE1'）`——一致
- 02-ipc-protocol.md、02-services.md、01-kernel.md 等：均引用 0x41524531——一致
- `09-ssot-registry.md` §3 登记——一致

**结论**：IPC magic 值在全部文档中唯一且一致。

### 4.2 任务 magic 值（0x41475453 'AGTS'） —— **唯一 ✓**

- SSoT 权威定义：`120-cross-project-code-sharing.md:236-237`：`#define AIRY_TASK_MAGIC 0x41475453u`
- 09-ssot-registry.md §3 登记——一致
- 与 IPC magic 区分明确（'AGTS' ≠ 'ARE1'）

**结论**：任务 magic 值唯一且一致。

### 4.3 128B 消息头布局 —— **不唯一 ✗**

- SSoT（`120-cross-project-code-sharing.md:343-356`）：128B，9 字段，`_Static_assert` 验证 ✓
- contracts.md（lines 49-57）：112B，10 字段，无静态断言 ✗
- 02-ipc-protocol.md（lines 60-76）：128B，9 字段，与 SSoT 一致 ✓
- 04-ipc-versioning.md（line 97）：SSoT 声明一致 ✓，但 lines 88/383 引用 version 字段 ✗
- 03-ipc-flow.md（line 798）：`AIRY_IPC_MSG_HDR_SIZE 128` ✓，但 lines 185/570-571/745-746 使用 src_pid/dst_pid ✗

**结论**：128B 消息头布局**不唯一**。SSoT 和 02-ipc-protocol.md 正确，但 contracts.md 使用 112B 旧布局，04-ipc-versioning.md 引用不存在的 version 字段，03-ipc-flow.md 使用旧字段名。

### 4.4 12 核心 syscall + 12 预留槽位 —— **不唯一 ✗**

- §1.3（`01-kernel.md:99-115`）：12 核心 + 12 预留 = 24 槽位 ✓
- §10.1.7（`01-kernel.md:786`）：12 核心 + 12 预留 = 24 槽位 ✓
- §5.5（`01-kernel.md:463`）："从 12 缩减到 10" ✗
- §6.1/§6.6：7 个 IPC 原语（应为 8） ✗
- `120-cross-project-code-sharing.md:369-378`：12 核心 + 12 预留 = 24 槽位 ✓

**结论**：syscall 数量**不唯一**。多处确认 12 核心，但 §5.5 声称 10，§6.1/§6.6 声称 7 个 IPC 原语（实际 8）。

### 4.5 8 子仓边界 —— **唯一 ✓**

- `10-architecture/06-directory-structure.md:175-184`：8 子仓映射表（kernel / services / security / memory / cognition / cloudnative / system / tests-linux）
- `10-architecture/05-adrs.md:37`：ADR-003 确认 8 子仓划分
- `20-modules/` 下 8 个模块文档（01-kernel ~ 08-tests）——一致
- 依赖层次（`06-directory-structure.md:189-199`）：kernel(L2) → services/security/memory(L3) → cognition(L4) → cloudnative(L5) → system(L6) → tests-linux(L7)

**结论**：8 子仓边界唯一且一致（开源文档内）。闭源文档使用 `airymaxos-` 前缀为命名差异，不影响边界定义。

### 4.6 IRON-9 v2 [SC]/[SS]/[IND] 三层模型 —— **唯一 ✓**

- `120-cross-project-code-sharing.md:43-51`：三层定义清晰
  - [SC] 共享契约层：6 个头文件，完全共享代码，`include/airymax/`
  - [SS] 语义同源层：高层 API 语义同源，签名独立演进
  - [IND] 完全独立层：完全独立实现
- [SC] 6 头文件清单（`120-cross-project-code-sharing.md:65-85`）：memory_types.h / security_types.h / cognition_types.h / sched.h / ipc.h / syscalls.h
- 补充共享文件 bpf_struct_ops.h（非 [SC] 核心头文件）——明确定位
- 单一数据源约束（OS-IRON-014）：[SC] 头文件仅物理宿主于 `kernel/include/airymax/`

**结论**：IRON-9 v2 三层模型唯一且定义清晰。

### 4.7 技术点唯一性验证小结

| 技术点 | 唯一性 | 备注 |
|--------|--------|------|
| IPC magic 0x41524531 | ✓ 唯一 | 全文一致 |
| 任务 magic 0x41475453 | ✓ 唯一 | 全文一致 |
| 128B 消息头布局 | ✗ 不唯一 | contracts.md 112B + version 字段引用 |
| 12 核心 syscall + 12 预留 | ✗ 不唯一 | §5.5 声称 10，§6.1/6.6 声称 7 IPC 原语 |
| 8 子仓边界 | ✓ 唯一 | 开源文档一致 |
| IRON-9 v2 三层模型 | ✓ 唯一 | 定义清晰 |

**6 项技术点中 4 项唯一、2 项不唯一**。不唯一的 2 项（128B 消息头、12 syscall）均为核心技术契约。

---

## 5. openEuler 工程实践评估

### 5.1 ES-OLK-1~13 工程思想映射

**映射完整性**（`agent-linux基本工程标准规范.md:990-1008` §12.4）：

| 编号 | 工程思想 | 落地规则 | 代码示例 |
|------|---------|---------|---------|
| ES-OLK-1 | 关注点分离 | §1.4 8 子仓差异化 | ✓ OLK-6.6 顶层目录 |
| ES-OLK-2 | 架构正交 | §13.3 arch/machine/plat | ✓ arch/{x86,arm64,riscv}/ |
| ES-OLK-3 | UAPI 分离 | §4.1 双层稳定性 | ✓ include/uapi/ |
| ES-OLK-4 | 策略机制分离 | sched_ext BPF 可插拔 | ✓ kernel/sched/ext.c |
| ES-OLK-5 | 条件编译规范化 | IS_ENABLED() | ✓ |
| ES-OLK-6 | UAPI 物理隔离 | include/uapi/ 独立 | ✓ |
| ES-OLK-7 | 声明式+命令式分离 | Kconfig + Makefile | ✓ |
| ES-OLK-8 | 维护者制度文档化 | MAINTAINERS | ✓ |
| ES-OLK-9 | 规范可执行 | checkpatch.pl | ✓ |
| ES-OLK-10 | regression 零容忍 | OS-IRON-006 | ✓ |
| ES-OLK-11 | 用户空间 ABI 永久稳定 | OS-IRON-001 | ✓ |
| ES-OLK-12 | 运行时可加载 | EXPORT_SYMBOL | ✓ |
| ES-OLK-13 | 文档即代码 | Documentation/ | ✓ |

**OLK-6.6 源码映射文档**（`docs-closed/agent-linux-dev/10-references/olk66-source-mapping/`）：
- 7 个映射文档覆盖 sched_ext / io_uring / BPF / MM / security / cognition / engineering-toolchain
- 含源码路径、行数、Kconfig 配置、数据结构映射
- 使用 IRON-9 v2 三层标注

**不足**：映射文档不引用 ES-OLK-1~13 编号（Grep 无匹配），ES-OLK 编号与源码映射之间追溯链断裂。

### 5.2 Makefile/Kconfig openEuler 特有实践

- `70-build-system/README.md:23`：`Makefile.airymaxos`（filechk 版本注入）
- `70-build-system/README.md:24,83`：`Kconfig.airymaxos`（通用型配置聚合点）
- `70-build-system/01-kbuild-system.md:5`：`Makefile.airymaxos` 供应商扩展
- `09-ssot-registry.md:140-142`：OS-KER-027 `Kconfig.airymaxos 仅聚合跨子系统特性` / OS-KER-029 `airymaxos-base.config 变更经评审`

**注意**：项目使用 `Makefile.airymaxos` / `Kconfig.airymaxos`（AirymaxOS 品牌命名），而非 `Makefile.oever` / `Kconfig.openeuler`（openEuler 品牌命名）。模式借鉴 openEuler 供应商扩展实践，但使用自有品牌。

### 5.3 MAINTAINERS / checkpatch / kernel-doc 对齐

- **MAINTAINERS**：`120-development-process/02-maintainer-hierarchy.md` 详述维护者层级制度，对齐 Linux 6.6 MAINTAINERS 文件与 Lieutenant System
- **checkpatch**：`30-interfaces/04-coding-standard.md:528`：`checkpatch.pl（Linux 6.6 内核基线）` 作为内核审查工具
- **kernel-doc**：`30-interfaces/01-syscalls.md:154`：`遵循 Linux 内核编码规范（Tab=8, snake_case, kernel-doc 注释）`
- **六大编码支柱**：Tab 8（OS-FMT-001）/ K&R（OS-FMT-003）/ 最小 typedef（OS-STD-010）/ goto 集中出口（OS-KER-001）/ kernel-doc（OS-STD-008）/ 80 列（OS-FMT-002）——均在闭源总纲中定义

**不足**：OS-FMT-001~007 未在 SSoT 注册表登记（v2.0 已发现，仍未修复）。

### 5.4 openEuler 工程实践评估小结

**评分**：80/B

- ES-OLK-1~13 映射完整（13/13 项有落地规则 + 源码映射文档含代码示例）
- Makefile.airymaxos / Kconfig.airymaxos 供应商扩展到位
- MAINTAINERS / checkpatch / kernel-doc 全部对齐
- 六大编码支柱定义完整

**不足**：
- ES-OLK 编号未在源码映射文档中引用（追溯链断裂）
- OS-FMT-001~007 未在 SSoT 注册表登记

---

## 6. seL4 工程思想吸收评估

### 6.1 ES-SEL4-01~05 架构层强制借鉴

| 编号 | seL4 工程思想 | 落地证据 | 源码引用 |
|------|-------------|---------|---------|
| ES-SEL4-01 | Liedtke 极简原则 | `01-kernel.md:55-62` 引用 Liedtke 原文；`03-microkernel-strategy.md:37` | seL4 ~1.44 万行 |
| ES-SEL4-02 | capability 单一权限模型 | `03-microkernel-strategy.md:65`；`03-security.md` | `seL4-master/src/object/cnode.c` 7 CNode 操作 |
| ES-SEL4-03 | 服务用户态化 | `02-services.md:117`（ADR-014）；`03-microkernel-strategy.md` | seL4 用户态服务架构 |
| ES-SEL4-04 | 消息传递 IPC（含 fastpath） | `03-microkernel-strategy.md:288-301`；`01-kernel.md:535-538` | `seL4-master/src/object/endpoint.c` / `src/fastpath/fastpath.c` |
| ES-SEL4-05 | 形式化验证驱动 | `03-microkernel-strategy.md`；ADR-014 | seL4 proof/ Isabelle/HOL |

### 6.2 Endpoint 三态机（EPState_Idle/Send/Recv）

- `30-interfaces/02-ipc-protocol.md:336`：`参考 seL4 Endpoint 状态机（ADR-014，源码证据 include/object/structures.h:36-41：EPState_Idle/EPState_Send/EPState_Recv）`
- 命名严格对齐 seL4：状态名描述"端点所处的语义态"而非"线程等待态"，不带 Waiting 后缀
- agent-linux IPC 端点 3 个状态由内核维护，用户态不可直接观测

**结论**：三态机对齐 seL4 ✓

### 6.3 Reply 原子性（doReplyTransfer 临界区）

- `30-interfaces/02-ipc-protocol.md:354-388`（§4.8）：详述 Reply 原子性
- Line 359：`seL4 master 模式：doReplyTransfer() 内部先 setThreadState(blocked, ts_idle) 再 sendIPC()`
- Line 363-379：agent-linux 借鉴 doReplyTransfer 模式，通过自旋锁 + 临界区串行实现
- Line 379：`串行两步：写入回复 + 恢复接收方上下文（对齐 doReplyTransfer 两步模式）`
- Line 388：`seL4 Reply 原子性通过"TCB 内嵌 caller slot + doReplyTransfer 临界区串行 + 形式化验证"三重保证；agent-linux 通过"自旋锁 + 临界区串行"保证（非形式化验证）`

**结论**：doReplyTransfer 临界区串行模式已借鉴并文档化 ✓

### 6.4 Fastpath POINT OF NO RETURN 语义

- `10-architecture/03-microkernel-strategy.md:288-301`（§4.3）：详述 Fastpath 设计
- Line 290：`seL4 的 IPC Fastpath 是性能关键路径（ES-SEL4-13），核心哲学是 POINT OF NO RETURN`
- Line 295：`所有检查通过后 → 原子提交（POINT OF NO RETURN）`
- `01-kernel.md:535-538`：Fastpath 模式借鉴，12 项前置检查 + 不可逆提交
- `01-kernel.md:536`：`io_uring 的零拷贝优化是独立的零拷贝优化，与 seL4 Fastpath 语义不同——两者同名但不同义，禁止混用`

**结论**：POINT OF NO RETURN 语义已吸收，且与 io_uring 零拷贝语义区分明确 ✓

### 6.5 MCS 模式排除的合理性

- `30-interfaces/01-syscalls.md:135-140`：
  - seL4 master 模式：8 个 API syscall（Call/ReplyRecv/Send/NBSend/Recv/NBRecv/Reply/Yield）
  - seL4 MCS 模式：11 个 API syscall
  - `agent-linux 采用 master 模式 8 个 IPC 原语...不引入 MCS 模式（agent 场景不需要 MCS 的 reply_t 对象与 schedcontext 模型，由 airy_ep->lock 临界区串行执行保证原子性）`
- `01-kernel.md:117`：`airy_sys_reply 完齐 seL4 master 模式 8 个 activity syscall（不引入 MCS 模式）`

**结论**：MCS 模式排除有明确的技术理由（agent 场景不需要 reply_t/schedcontext），通过临界区串行保证原子性 ✓

### 6.6 seL4 工程思想吸收评估小结

**评分**：80/B

- ES-SEL4-01~05 架构层强制借鉴均有 seL4 源码级证据 ✓
- Endpoint 三态机对齐 seL4 ✓
- doReplyTransfer 临界区串行模式已借鉴 ✓
- Fastpath POINT OF NO RETURN 语义已吸收 ✓
- MCS 模式排除有合理技术理由 ✓

**不足**：
- ES-SEL4-7 分类残留冲突（v1.0/v2.0 已发现，仍未修复）
- seL4 深度借鉴 C-C01~C-C09 待 1.0.1 M1 落地

---

## 7. 开发就绪度评估

### 7.1 8 项判定标准验证

| # | 判定标准 | 状态 | 证据/阻塞原因 |
|---|---------|------|-------------|
| 1 | 8 子仓接口定义 | ✅ 通过 | `06-directory-structure.md:175-184` 8 子仓映射 + 依赖层次 |
| 2 | 12 syscall 定义 | ⚠️ **有条件通过** | §1.3 定义 12 核心 ✓，但 §5.5 声称 10 ✗ |
| 3 | 4 数据流定义 | ✅ 通过 | `01-kernel.md:155-163` 调度/IPC/eBPF/记忆卷载 4 大数据流 |
| 4 | 14 ADR 定义 | ✅ 通过 | `05-adrs.md:35-48` ADR-001~014 全部 Accepted |
| 5 | IPC 协议契约 | ❌ **不通过** | 消息头布局冲突（112B vs 128B）+ 操作码碎片化（4/5/11 套） |
| 6 | 字段命名统一 | ❌ **不通过** | src_task vs src_pid 在 51 处并存 |
| 7 | 宏命名统一 | ❌ **不通过** | AIRY_IPC_HDR_SZ vs AIRY_IPC_MSG_HDR_SIZE 在 19 处并存 |
| 8 | 子仓命名统一 | ❌ **不通过** | 闭源 401 处 airymaxos- 前缀 vs 开源裸名 |

### 7.2 阻塞性缺陷

**3 项 P0 级阻塞性缺陷**：

1. **IPC 消息头布局冲突**（P0-1）：contracts.md 定义 112B 旧布局，SSoT 定义 128B 新布局。两者字段集不兼容（version/type/src_pid/dst_pid vs opcode/src_task/dst_task）。在布局未统一前，无法实现 IPC 协议。

2. **IPC 操作码碎片化**（P0-4）：3 套互不兼容的操作码（SSoT 4 个 / services.md 5 个 / ipc-versioning.md 11 个），编号互相冲突（SEND=0 vs NOP=0x00）。在操作码未收敛前，无法实现 IPC 操作码分发。

3. **syscall 数量矛盾**（P0-2）：§1.3 定义 12 核心，§5.5 声称 10。在数量未统一前，无法确定 syscall 编号体系的权威定义。

### 7.3 开发就绪度评估小结

**判定**：**不通过**——8 项判定标准中 3 项通过、1 项有条件通过、4 项不通过。存在 3 项 P0 级阻塞性缺陷。

**评分**：62/C

**建议**：修复 3 项 P0 级阻塞性缺陷（IPC 头布局统一 / IPC 操作码收敛 / syscall 数量统一）后，方可启动 1.0.1 M1 代码开发。

---

## 8. 技术细节完成度检查

### 8.1 sched_ext 向前移植

- `10-architecture/04-engineering-baseline.md:55`：`增强基线（1.x.x）| Linux 6.6 LTS + sched_ext forward-port（主线 6.12+）| AI 原生能力增强（sched_ext 向前移植）`
- `04-engineering-baseline.md:71`：`sched_ext（SCHED_AGENT）| agent-linux 内核增强 | 主线 6.12+ | kernel 用户态调度`
- `04-engineering-baseline.md:75`：`对于主线 6.12+ 才稳定但 agent-linux 1.0.1 必需的特性（如 sched_ext），采用 agent-linux 内核增强策略引入`
- `30-interfaces/01-syscalls.md:385`：`sched_ext（agent-linux 内核增强，主线 6.12+）`

**结论**：sched_ext 向前移植策略已明确文档化 ✓（Linux 6.6 基线 + sched_ext forward-port from 6.12+）

### 8.2 Euler API 兼容性

- Grep `Euler API|euler.*api|EulerAPI|欧拉.*API` 在 `docs/AirymaxOS/`：**无匹配**

**结论**：Euler API 兼容性**未文档化** ✗。这是一个技术细节缺口——方案未说明与 openEuler Euler API 的兼容性策略。

### 8.3 Rust 驱动规范

- `01-kernel.md:49`：`Rust 安全驱动 [IND]：依托 Linux 6.6 中 Rust 实验性支持（持续演进中），构建安全驱动开发框架`
- `50-project-erp/project_erp.md:1233`：`引入 Rust 进行驱动和核心组件开发，提升内存安全性`
- `50-project-erp/project_erp.md:1262`：`第四阶段：Rust 运行时初始化，加载 Rust 编写的驱动`
- `09-ssot-registry.md:277`：`OS-KER-144 | Rust 仅用于安全敏感非热路径 | OS-KER-048`

**结论**：Rust 驱动**已提及但规范不完整** ⚠️。有方向性描述（安全驱动框架 + 非热路径约束），但缺少详细的 Rust 驱动开发规范（API 约定 / 安全边界 / 构建集成 / 测试框架）。

### 8.4 Wasm 集成

- `10-architecture/05-adrs.md:42`：ADR-008 `Wasm 3.0 沙箱运行时（cognition frameworks）`——Accepted
- `30-interfaces/04-coding-standard.md:367`：`Agent 代码默认运行在 Wasm 3.0 沙箱（详见 20-modules/05-cognition.md 第 4.3 节）`
- `30-interfaces/03-sdk-api.md:36`：`沙箱 | Wasm 3.0 runtime | 沙箱内 Agent，安全隔离`
- `30-interfaces/README.md:61`：`cognition | AIRY_SYS_CLT_* / WASM_* | CoreLoopThree 阶段通知`
- `10-architecture/04-engineering-baseline.md:193`：`cognition 实现超节点沙箱，支持 Agent 快速冷启动，与 Wasm 3.0 沙箱运行时集成（ADR-008）`

**结论**：Wasm 3.0 集成已文档化 ✓（沙箱运行时 + ADR-008 + capability 受限 + seccomp 过滤）

### 8.5 跨节点 IPC

- `30-interfaces/02-ipc-protocol.md:121`：`agent-linux 部署形态为分布式 agent 集群，IPC 消息在多机间传递`
- `02-ipc-protocol.md:424`：`NFR-P-002c | 跨节点 IPC | > 1M msg/s（4 节点）| 超节点 OS 跨节点 IPC`
- `02-ipc-protocol.md:432`：`CXL 跨节点共享: 跨节点 IPC 通过 CXL 3.0 内存池化共享 ring，减少网络往返`
- `40-dataflows/03-ipc-flow.md:570-571`：跨节点 IPC 路由判断（检查 dst_pid 所属节点）

**结论**：跨节点 IPC 已文档化 ✓（CXL 3.0 内存池化 + 分布式 agent 集群 + 性能指标 > 1M msg/s）

### 8.6 技术细节完成度检查小结

| 技术细节 | 状态 | 备注 |
|---------|------|------|
| sched_ext 向前移植 | ✅ 完成 | Linux 6.6 + forward-port 6.12+ 策略明确 |
| Euler API 兼容性 | ❌ 缺失 | 完全未文档化 |
| Rust 驱动规范 | ⚠️ 不完整 | 有方向，缺详细规范 |
| Wasm 集成 | ✅ 完成 | ADR-008 + 沙箱 + capability + seccomp |
| 跨节点 IPC | ✅ 完成 | CXL 3.0 + 性能指标 + 路由机制 |

**评分**：68/B-

---

## 9. 综合评分与改进建议

### 9.1 综合评分

| 评分维度 | v1.0 | v2.1 | 变化 | 权重参考 |
|---------|------|------|------|---------|
| 内部冲突 | 78 | **62** | -16 | 4 P0 + 5 P1 全部未修复 |
| 技术点唯一性 | 85 | **68** | -17 | 128B 消息头/syscall 数量/操作码不唯一 |
| openEuler 工程实践 | 78 | **80** | +2 | OLK-6.6 映射文档含代码示例 |
| seL4 工程思想 | 82 | **80** | -2 | 三态机/Fastpath/MCS 到位，ES-SEL4-7 残留 |
| 开发就绪度 | 78 | **62** | -16 | 3 项 P0 阻塞性缺陷 |
| 细节完成度 | 75 | **68** | -7 | Euler API 缺失 + 里程碑不一致 |
| **综合评分** | **80/B** | **70/C+** | **-10** | 核心技术契约层系统性 SSoT 违反 |

### 9.2 评分调整说明

**综合评分从 80/B 降至 70/C+ 的核心原因**：

1. **内部冲突 -16 分**：v1.0 识别的 4 项 P0 冲突（IPC 头布局 / syscall 数量 / 子仓命名 / IPC 操作码）全部未修复，且 P0-4 操作码碎片化比 v1.0 描述更严重（3 套互不兼容，编号冲突）。

2. **技术点唯一性 -17 分**：6 项核心技术点中 2 项不唯一（128B 消息头实际 112B、syscall 数量 12 vs 10），均为 IPC 协议和 syscall 编号体系的基石。

3. **开发就绪度 -16 分**：8 项判定标准中 4 项不通过（IPC 契约 / 字段命名 / 宏命名 / 子仓命名），3 项 P0 级阻塞性缺陷阻断开发启动。

### 9.3 待修复问题清单（按优先级）

#### P0 级（阻断开发启动，必须立即修复）

| # | 问题 | 修复方案 | 工作量 | 证据 |
|---|------|---------|--------|------|
| 1 | IPC 消息头布局冲突（112B vs 128B） | contracts.md 字段表（lines 49-57）和 mermaid 图（lines 72-106）全文替换为 SSoT Layout C 布局；删除 version/type/src_pid/dst_pid，改用 opcode/src_task/dst_task；reserved 从 72B 改为 84B | ~4h | §2.1 P0-1 |
| 2 | IPC 操作码碎片化（4/5/11 套） | services.md line 317 改为 SSoT 4 操作码；ipc-versioning.md §8.1 全表重构为 SSoT 4 操作码 + 版本化扩展机制；删除不存在的 AIRY_IPC_OP_HANDSHAKE 等 | ~6h | §2.1 P0-4 |
| 3 | syscall 数量矛盾（12 vs 10） | 01-kernel.md line 463 "从 12 缩减到 10" 修改为"保持 12 核心 syscall（capability invocation 统一入口消除独立 syscall 需求，但 airy_sys_call 本身为 12 核心之一）" | ~0.5h | §2.1 P0-2 |
| 4 | 子仓命名矛盾（airymaxos- 401 处） | 闭源权威文档（agent-linux基本工程标准规范.md 37 处 + 开发路线 4 处 + README 1 处）全文替换 airymaxos- → 裸名 | ~6h | §2.1 P0-3 |

#### P1 级（1.0.1 M1 阶段修复）

| # | 问题 | 修复方案 | 工作量 | 证据 |
|---|------|---------|--------|------|
| 5 | 双重宏命名 | 全文统一为 SSoT 的 `AIRY_IPC_HDR_SZ`（12 处 AIRY_IPC_MSG_HDR_SIZE 替换） | ~2h | §2.2 P1-1 |
| 6 | 字段命名不一致 | 全文统一为 SSoT 的 `src_task`/`dst_task`（28 处 src_pid/dst_pid 替换，注意类型 u32→u64） | ~4h | §2.2 P1-2 |
| 7 | services.md 数量 | 标题"15+"修改为"20" | ~0.1h | §2.2 P1-3 |
| 8 | 控制平面数量 | §6.1 line 477 和 §6.6 line 555 "7 个"修改为"8 个" | ~0.1h | §2.2 P1-5 |
| 9 | ipc-versioning.md version 字段 | 删除 hdr->version 引用（lines 88,383,727），版本协商改为基于 opcode 扩展 | ~2h | §3.1 |

#### P2 级（增量修复）

| # | 问题 | 修复方案 | 工作量 | 证据 |
|---|------|---------|--------|------|
| 10 | io_uring 互斥标志 | 从"必须启用"清单中移除 COOP_TASKRUN 或 DEFER_TASKRUN 之一，标注"二选一" | ~0.5h | §2.3 P2-1 |
| 11 | ES-OLK 编号追溯 | 在源码映射文档中添加 ES-OLK-1~13 编号引用 | ~2h | §2.3 P2-2 |
| 12 | 里程碑命名统一 | 全部模块统一为 M0-M8（9 项），与 README 一致 | ~1h | §2.3 P2-4 |
| 13 | 03-ipc-flow.md 字段引用 | src_pid/dst_pid 替换为 src_task/dst_task（5 处） | ~0.5h | §2.3 P2-5 |
| 14 | Euler API 兼容性 | 新增 Euler API 兼容性策略文档 | ~4h | §8.2 |
| 15 | Rust 驱动规范 | 补充详细的 Rust 驱动开发规范 | ~8h | §8.3 |

### 9.4 改进建议

#### 立即（P0 修复，~16.5h）

1. **统一 IPC 消息头布局**——contracts.md 字段表全文替换为 SSoT Layout C。这是最核心的修复，影响 IPC 协议正确性。
2. **收敛 IPC 操作码**——将 services.md 和 ipc-versioning.md 的操作码定义统一到 SSoT 的 4 个（SEND/RECV/SEND_BATCH/CANCEL），版本化扩展通过 reserved 字段或新 opcode 编号实现。
3. **统一 syscall 数量**——删除 §5.5 的"从 12 缩减到 10"描述。
4. **统一子仓命名**——闭源权威文档全文替换 airymaxos- → 裸名。

#### 短期（P1 修复，~8.2h）

5. **统一宏命名**——全文使用 `AIRY_IPC_HDR_SZ`。
6. **统一字段命名**——全文使用 `src_task`/`dst_task`（u64），注意类型宽度变更。
7. **修正数量标注**——services.md "15+"→"20"，§6.1/§6.6 "7 个"→"8 个"。
8. **删除 version 字段引用**——ipc-versioning.md 全部 version 字段引用改为基于 opcode 的版本协商。

#### 中期（P2 修复 + 技术细节补充，~16h）

9. **修复 io_uring 互斥标志**——COOP_TASKRUN / DEFER_TASKRUN 二选一。
10. **统一里程碑命名**——全部模块使用 M0-M8。
11. **补充 Euler API 兼容性**——新增文档说明与 openEuler Euler API 的兼容策略。
12. **补充 Rust 驱动规范**——API 约定 / 安全边界 / 构建集成 / 测试框架。

### 9.5 最终结论

agent-linux（AirymaxOS）整体方案经 v2.1 系统性复审，**综合评分 70/C+**，较 v1.0 的 80/B 下降 10 分。核心原因是 v1.0 识别的 4 项 P0-CRITICAL 问题（IPC 消息头布局 / syscall 数量 / 子仓命名 / IPC 操作码）在 v1.0→v2.1 迭代中**全部未修复**，且 IPC 操作码碎片化比 v1.0 描述更为严重（3 套互不兼容的操作码定义，编号互相冲突）。

**核心优势**（维持）：
- IRON-9 v2 三层共享模型定义清晰，6 个 [SC] 头文件单一数据源
- IPC magic（0x41524531）和任务 magic（0x41475453）全文唯一
- 8 子仓边界定义清晰（开源文档内）
- 14 ADR 全部 Accepted
- seL4 工程思想吸收到位（三态机 / doReplyTransfer / Fastpath / MCS 排除）
- openEuler 工程实践对齐（ES-OLK-1~13 + 六大编码支柱 + MAINTAINERS/checkpatch/kernel-doc）
- sched_ext 向前移植策略明确

**阻塞性缺陷**（3 项 P0）：
- IPC 消息头布局 112B vs 128B 冲突
- IPC 操作码 3 套互不兼容
- syscall 数量 12 vs 10 矛盾

**建议**：修复 4 项 P0 级问题（~16.5h）后，综合评分可恢复至 ~78/B+；继续修复 5 项 P1 级问题（~8.2h）后，可恢复至 ~82/B，达到可启动开发状态。

---

> **报告结束** | SPHARX Ltd 内部参考 | 闭源不公开 | 审查日期：2026-07-13 | 审查版本：v2.1
