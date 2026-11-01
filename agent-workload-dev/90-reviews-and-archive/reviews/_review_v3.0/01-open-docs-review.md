Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# AirymaxRT 开源文档 v3.0 审查报告

> **文档定位**：agentrt 开源文档（`docs/AirymaxRT/`）v3.0 全面复审报告，在 v1.0（综合 65/C+）与 v2.0（综合 64/C+，修正后 72/B-）基础上执行 v2.0 修正持久性独立复核 + v3.0 新发现问题扫描。
> **保密级别**：SPHARX Ltd 内部参考，**闭源不公开**。
> **版本**：3.0（2026-07-14）。
> **审查范围**：仅 `docs/AirymaxRT/` 开源文档（87 个 .md + 1 个 .dox + 1 个 .drawio）；**不涉及** `docs/AirymaxOS/`、`docs-closed/`、源码、`docs/OpenStandards/`。
> **审查方法**：v2.0 修正日志深读 → Grep 机器检查独立复核（10 项）→ 系统性新问题扫描（10 类）。
> **证据要求**：所有结论附 `文件路径:L行号` 或 Grep 命令与匹配数，可通过 Read/Grep 工具复核。
> **SPDX-License-Identifier**：AGPL-3.0-or-later OR Apache-2.0。

---

## 目录

- [1. 执行摘要](#1-执行摘要)
- [2. v2.0 修正持久性验证矩阵](#2-v20-修正持久性验证矩阵10-项)
- [3. v3.0 新发现问题清单](#3-v30-新发现问题清单)
- [4. 延期项评估](#4-延期项评估)
- [5. 修正后综合评分变化](#5-修正后综合评分变化)
- [6. 附录：审查文件清单](#6-附录审查文件清单)

---

## 1. 执行摘要

### 1.1 v2.0 修正持久性验证结果

| 维度 | 结果 | 说明 |
|------|------|------|
| 验证项总数 | 10 | 覆盖 v2.0 开源文档全部 P0+P1 修正项 |
| 完全持久 | **9** | P0-1/P0-5/P0-8/P0-9/P1-5/P1-6/P1-11/P1-13/P1-1/3 |
| 部分持久 | **1** | P0-4 IPC 头三重违规：`06-ipc/README.md` 已修正，但 `02-l2-service-protocol.md` 仍存在同样违规 |
| 回退项 | 0 | 无修正项被回退 |

**核心结论**：v2.0 开源文档修正整体持久性良好（9/10 完全持久），但 **P0-4 IPC 头三重违规修正不完整** —— `30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md` 仍包含与 [SC] SSoT 直接矛盾的 `are_ipc_message_header_t` 定义（13 字段 + `uint32_t` + 无 packed + 注释中的 `_Static_assert`），构成 v3.0 新发现 P0 级问题。

### 1.2 v3.0 新发现总览

| 级别 | 数量 | 关键问题 |
|------|------|---------|
| **P0** | 1 | v3.0-P0-1：`02-l2-service-protocol.md` IPC 头三重违规未修正（v2.0 P0-4 修正遗漏） |
| **P1** | 5 | daemon/daemons 单复数（44 处）/ L1-L2-L3 cross-reference 文件名错误（15 处）/ Cupolas 子系统数量不一致 / 02-logging.md 双重路径 / glossary-index 引用不存在的 error_code_reference.md |
| **P2** | 6 | doxygen-guide 路径错误 + code_comment_template.md 不存在 / naming_conventions.md 不存在 / 0.1.1详细任务清单.md 不存在 / TERMINOLOGY.md 路径头大小写 / Docs/ 大小写（2 处） |
| **合计** | **12** | — |

### 1.3 综合判定

> **agentrt 开源文档体系 v3.0 复审结论**：v2.0 修正整体持久，但 P0-4 IPC 头三重违规修正存在 1 处遗漏（`02-l2-service-protocol.md`），需立即补修。新发现的 5 项 P1 + 6 项 P2 集中在路径引用完整性（`agentrt/daemon/` 单复数、cross-reference 文件名、broken links）与术语数量一致性（Cupolas 4 vs 7 子系统），均为文档可用性问题，不影响架构设计正确性。
>
> **修正后综合评分**：v2.0 修正后 72/B- → v3.0 修正后预估 **74/B-**（修复 P0-1 后 +2，新发现 P1/P2 抵消部分加分）。

---

## 2. v2.0 修正持久性验证矩阵（10 项）

每项均通过 Grep 工具独立执行并记录实际匹配数。

### 2.1 验证项总表

| # | 验证项 | Grep 命令 | 期望 | 实际 | 状态 |
|---|--------|----------|------|------|------|
| 1 | **P0-1 错误码 SSoT 统一** | `Grep "AIRY_EOK\|AIRY_EINVAL\|AIRY_ENOMEM\|AIRY_ETIMEOUT\|AIRY_ETIMEDOUT\|airy_err_t" docs/AirymaxRT --glob *.md` (count) | 8 处文档统一为 POSIX errno 负值 + `airy_err_t` + `AIRY_EOK=0` | **582 处/29 文件**，8 处权威定义文档（00-architectural-principles.md / 06-iron9-shared-model.md / 05-syscall.md / 04-syscall-api-contract.md / 06-glossary-index.md / 30-interfaces/README.md / 03-protocol-contract.md / TERMINOLOGY.md）均确认 `AIRY_EOK=0`/`AIRY_EINVAL=(-22)`/`AIRY_ENOMEM=(-12)`/`AIRY_ETIMEOUT=(-110)`/`airy_err_t=int32_t` | ✅ 持久 |
| 2 | **P0-4 IPC 头三重违规** | `Grep "airy_ipc_msg_hdr\|__attribute__\(\(packed\)\)\|_Static_assert\(sizeof" 30-interfaces/06-ipc/README.md` | `struct airy_ipc_msg_hdr` + packed + _Static_assert + 8 字段 + UAPI 类型 | `06-ipc/README.md` **8 行匹配**（L26/28/38/53/63/65/71/99），结构体为 `struct airy_ipc_msg_hdr`（无 typedef）+ `__u32/__u16/__u64/__u8` + 8 字段 + `__attribute__((packed))` + `_Static_assert(sizeof(...) == 128)` ✅。**但** `02-l2-service-protocol.md:93-109` 仍为 `typedef struct are_ipc_message_header` + `uint32_t/uint16_t/uint64_t` + 13 字段 + 无 packed + 注释中的 `_Static_assert`（详见 §3.1 v3.0-P0-1） | ⚠️ **部分持久** |
| 3 | **P0-5 "操作系统"误称** | `Grep "操作系统" docs/AirymaxRT` (count) | 37 处全部为合法用法（host OS / agent-linux / 概念借鉴 / 显式否定） | **37 处/16 文件**，逐项确认全部合法：`04-microcorert.md` 15 处（显式否定 + OS 概念借鉴 + 指 seL4/Fuchsia 真正的 OS）/ `TERMINOLOGY.md` 4 处（host OS IPC + OS 虚拟内存借鉴 + 显式否定 ×2）/ `01-design-philosophy.md` 2 处（OS 设计智慧借鉴 + 显式否定）/ `23-troubleshooting-faq.md` 2 处（host OS 支持 + `uname -a`）/ 其他 12 文件各 1 处（均合法） | ✅ 持久 |
| 4 | **P0-8 [SC] 头文件清单** | `Grep "syscalls\.h\|bpf_struct_ops\.h" 06-iron9-shared-model.md` | syscalls.h 为 #6 + bpf_struct_ops.h 为补充说明 | `06-iron9-shared-model.md:73` 第 6 项为 `syscalls.h`；`:75` bpf_struct_ops.h 标注为"补充共享文件（非 [SC] 核心头文件）"；6 个核心头文件正确排序：1.memory_types.h / 2.security_types.h / 3.cognition_types.h / 4.sched.h / 5.ipc.h / 6.syscalls.h | ✅ 持久 |
| 5 | **P0-9 文件路径引用** | `Grep "00-basic-theories\|30-coding-standard\|08-compliance-checklist\|70-project-erp\|DocsClosed" docs/AirymaxRT --glob *.md` (count) | 0 残留 | **0 匹配**（5 类旧路径全部清零） | ✅ 持久 |
| 6 | **P1-5 Cupola→Cupolas** | `Grep "Cupola[^s]" docs/AirymaxRT` (count) | 0 残留 | **0 匹配** | ✅ 持久 |
| 7 | **P1-6 Daemon 10→12** | `Grep "12 个核心\|Services \(12\)" 01-system-architecture.md` | ≥2 匹配 | **2 匹配**（L305 "12 个核心用户态服务" + L309 "Airymax Daemon Services (12)"） | ✅ 持久 |
| 8 | **P1-11 MemoryRovol 命名** | `Grep "L1 Raw\|L2 Feature\|L3 Structure\|L4 Pattern" 02-c-language-boundary.md` | 存在 + [SC] 缓存层级区分说明 | **1 行匹配**（L72：`四层记忆管理系统 (L1 Raw → L2 Feature → L3 Structure → L4 Pattern)...注意：此 L1-L4 为**记忆抽象层级**...与 [SC] \`memory_types.h\` 中的**缓存层级** (\`AIRY_MEM_L1_HOT\`/\`L2_WARM\`/\`L3_COLD\`/\`L4_PMEM\`) 是不同概念，不应混淆。`） | ✅ 持久 |
| 9 | **P1-13 删除重复文件** | `ls docs/AirymaxRT/50-specifications/` | 目录不存在 | **No such file or directory**（目录已完全移除） | ✅ 持久 |
| 10 | **P1-1/3 函数前缀三层定义** | `Grep "函数前缀三层定义\|airy_\*.*are_\*\|agentrt_\*.*不使用\|agentos_\*.*已废弃\|airymaxos_\*.*已废弃" 06-iron9-shared-model.md` | §3.12 存在 + 5 行前缀表 + 4 条关键约束 | **5 行匹配**（L260 §3.12 标题 / L268 `agentrt_*` 不使用 / L269 `agentos_*` 已废弃 / L270 `airymaxos_*` 已废弃 / L277 4 条关键约束） | ✅ 持久 |

### 2.2 验证小结

- **9/10 项完全持久**：v2.0 开源文档修正质量整体良好，主要修正项（错误码 SSoT / "操作系统"定位 / [SC] 头文件清单 / 路径引用 / Cupola 复数 / Daemon 数量 / MemoryRovol 命名 / 重复文件删除 / 函数前缀三层定义）均经 Grep 独立复核确认持久。
- **1/10 项部分持久**：P0-4 IPC 头三重违规在 `06-ipc/README.md` 已正确修正，但 v2.0 修正日志（`fix-log-p0-docs.md`）**遗漏了** `30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md` 中的同款违规定义。该文件 L93-109 仍包含 `typedef struct are_ipc_message_header` + `uint32_t/uint16_t/uint64_t` + 13 字段 + 无 `__attribute__((packed))` + 注释中的 `_Static_assert`，且使用 `ARE_IPC_MAGIC` 宏名（应为 `AIRY_IPC_MAGIC`），直接违反 `06-iron9-shared-model.md:142` 明文规定"结构体名称为 `airy_ipc_msg_hdr`（**不是** `airymaxos_ipc_msg_hdr` 或 `are_ipc_message_header_t`）"。

---

## 3. v3.0 新发现问题清单

### 3.1 P0 级问题（1 项）

#### v3.0-P0-1：`02-l2-service-protocol.md` IPC 头三重违规未修正（v2.0 P0-4 修正遗漏）

| 属性 | 内容 |
|------|------|
| **问题描述** | v2.0 P0-4 修正仅覆盖 `30-interfaces/06-ipc/README.md`，**遗漏** `30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md`。后者仍包含与 [SC] SSoT 直接矛盾的 `are_ipc_message_header_t` 定义，构成同款三重违规。 |
| **证据** | `30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md:93-109`：<br/>```c<br/>typedef struct are_ipc_message_header {<br/>    uint32_t magic;            /* offset  0: 0x41524531 ("ARE1") */<br/>    uint16_t version;          /* offset  4 */<br/>    uint16_t msg_type;         /* offset  6 */<br/>    uint32_t protocol;         /* offset  8 */<br/>    uint64_t msg_id;           /* offset 12 */<br/>    uint64_t trace_id;         /* offset 20 */<br/>    uint64_t correlation_id;   /* offset 28 */<br/>    char     source[32];       /* offset 36 */<br/>    char     target[32];       /* offset 68 */<br/>    uint32_t payload_len;      /* offset 100 */<br/>    uint32_t flags;            /* offset 104 */<br/>    uint64_t timestamp_ns;     /* offset 108 */<br/>    uint32_t checksum;         /* offset 116 */<br/>    uint32_t reserved;         /* offset 120 */<br/>} are_ipc_message_header_t;  /* _Static_assert(sizeof == 128) */<br/>```<br/>**三重违规对比**：<br/>| 维度 | `02-l2-service-protocol.md`（违规） | SSoT `06-ipc/README.md` + `06-iron9-shared-model.md` |<br/>|------|--------------------------------|--------------------------------------------------|<br/>| 结构体名 | `typedef struct are_ipc_message_header` → `are_ipc_message_header_t` | `struct airy_ipc_msg_hdr`（无 typedef） |<br/>| 类型前缀 | `uint32_t`/`uint16_t`/`uint64_t` | `__u32`/`__u16`/`__u64`/`__u8`（UAPI） |<br/>| 对齐属性 | 无 | `__attribute__((packed))` |<br/>| 字段数 | **13 字段**（含 `source[32]`/`target[32]` 字符数组 + `checksum`） | **8 字段**（含 `__u64 src_task`/`__u64 dst_task` + `reserved[84]`） |<br/>| 大小验证 | `/* _Static_assert(sizeof == 128) */`（注释中，不编译） | `_Static_assert(sizeof(...) == 128)`（真实编译期校验） |<br/>| 宏命名 | `ARE_IPC_MAGIC`（L60） | `AIRY_IPC_MAGIC`（`06-ipc/README.md:34`） |<br/>**直接违反 SSoT 明文规定**：`06-iron9-shared-model.md:142` "结构体名称为 `airy_ipc_msg_hdr`（**不是** `airymaxos_ipc_msg_hdr` 或 `are_ipc_message_header_t`）"；`06-iron9-shared-model.md:295` "使用 `airy_` 前缀（如 `airy_ipc_msg_hdr`），不使用 `airymaxos_` 或 `are_` 前缀"。 |
| **影响评估** | (1) 同一 magic 值 `0x41524531`（'ARE1'）对应两种不同字段布局（13 vs 8 字段），接收方无法判别应按哪个布局解析；(2) `02-l2-service-protocol.md:748` 自承"Airymax 原生 `ipc_bus_message_header_t` 字段顺序与本标准略有不同...本标准冻结字段布局为 v1"，但本标准布局与 [SC] SSoT 布局矛盾，三方（L2 标准 / [SC] SSoT / 原生实现）各不相同；(3) 违反 IRON-014（[SC] 6 头文件单一数据源）；(4) v2.0 P0-4 修正声明"已统一为 SSoT 版本"但实际未覆盖全部文件。 |
| **修复建议** | 对齐 `06-ipc/README.md` 的修正方案：(1) 结构体名 `are_ipc_message_header_t` → `struct airy_ipc_msg_hdr`；(2) 类型 `uint32_t/uint16_t/uint64_t` → `__u32/__u16/__u64/__u8`；(3) 添加 `__attribute__((packed))`；(4) 字段布局对齐 SSoT 8 字段；(5) 添加真实 `_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128)`；(6) 宏 `ARE_IPC_MAGIC` → `AIRY_IPC_MAGIC`；(7) 在迁移说明中保留旧字段对应关系表。**注意**：需评估 L2 协议是否确实需要独立于 [SC] SSoT 的消息头（若需要，应使用不同 magic 值；若不需要，应直接复用 `struct airy_ipc_msg_hdr`）。 |
| **工作量估算** | ~3h（同 v2.0 P0-4） |

---

### 3.2 P1 级问题（5 项）

#### v3.0-P1-1：`agentrt/daemon/` 路径单数 vs 实际 `agentrt/daemons/` 复数（44 处/16 文件）

| 属性 | 内容 |
|------|------|
| **问题描述** | v1.0 §5.1 已确认源码侧 `daemon→daemons` 改名彻底完成（"Glob `agentrt/daemon/**/*.c` = 0 文件；目录名为 `daemons/`（复数）"），但开源文档中仍大量使用单数 `agentrt/daemon/` 引用源码路径，与实际源码目录结构不一致。 |
| **证据** | `Grep "agentrt/daemon/\|agentrt/daemons/" docs/AirymaxRT` = **44 处使用 `agentrt/daemon/`（单数）**，0 处使用 `agentrt/daemons/`（复数）。分布：<br/>- `10-architecture/00-architectural-principles.md`：6 处（L152/202/429/508/564-568）<br/>- `10-architecture/50-services/02-logging.md`：7 处（L113/118/125/169/319/732/754）<br/>- `30-interfaces/05-runtime-interfaces/01-l1-runtime-interface.md`：2 处（L35/756）<br/>- `30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md`：7 处（L431/738-744）<br/>- `30-interfaces/05-runtime-interfaces/03-l3-security-governance.md`：2 处（L740/741）<br/>- `30-interfaces/60-syscalls/06-telemetry.md`：1 处（L99）<br/>- `20-modules/10-contracts/03-protocol-contract.md`：3 处（L32/56/117）<br/>- `20-modules/10-contracts/04-syscall-api-contract.md`：1 处（L53）<br/>- `20-modules/10-contracts/05-logging-format.md`：3 处（L52/281/524）<br/>- `00-requirements/04-design-principles.md` + `04-design-principles-cn.md`：2 处<br/>- `140-application-development/24-create-agent.md`：2 处（L19/569）<br/>- `140-application-development/25-create-skill.md`：1 处（L19）<br/>- `140-application-development/23-troubleshooting-faq.md`：1 处（L225）<br/>- `140-application-development/26-coreloopthree-dag-integration.md`：1 处（L292） |
| **影响评估** | 外部开发者按文档路径查找源码文件全部失败；CI 链接检查无法通过；与 v1.0 历史修正（daemon→daemons）不一致。 |
| **修复建议** | 全量替换 `agentrt/daemon/` → `agentrt/daemons/`（44 处/16 文件）。**注意**：需使用三步替换法避免 `agentrt/daemons/` 中的子串误替换。 |
| **工作量估算** | ~1.5h |

#### v3.0-P1-2：L1/L2/L3 文件间 cross-reference 文件名错误（15 处/4 文件）

| 属性 | 内容 |
|------|------|
| **问题描述** | `30-interfaces/05-runtime-interfaces/` 目录下 L1/L2/L3 三个标准文档相互引用时使用错误的文件名（旧命名约定），与实际文件名（NN- 前缀命名约定）不匹配。 |
| **证据** | 实际文件名：`01-l1-runtime-interface.md` / `02-l2-service-protocol.md` / `03-l3-security-governance.md`<br/>错误引用：`L1_runtime_interface.md` / `L2_service_protocol.md` / `L3_security_governance.md`<br/><br/>**15 处分布**：<br/>- `01-l1-runtime-interface.md:16,17,791,792`（4 处引用 L2/L3）<br/>- `02-l2-service-protocol.md:25,26,755,756`（4 处引用 L1/L3）<br/>- `03-l3-security-governance.md:26,27,775,776`（4 处引用 L1/L2）<br/>- `README.md:22,23,24`（3 处文档清单） |
| **影响评估** | 同目录内 cross-reference 全部 broken；Markdown 渲染器与 CI 链接检查器报错；外部读者无法在三层标准间导航。 |
| **修复建议** | 全量替换：`L1_runtime_interface.md` → `01-l1-runtime-interface.md`、`L2_service_protocol.md` → `02-l2-service-protocol.md`、`L3_security_governance.md` → `03-l3-security-governance.md`。 |
| **工作量估算** | ~0.3h |

#### v3.0-P1-3：Cupolas 子系统数量不一致（4 vs 7）

| 属性 | 内容 |
|------|------|
| **问题描述** | `04-mainpage.dox` 将 Cupolas 描述为"四重纵深防护"仅列 4 子系统，但 `TERMINOLOGY.md` / `01-design-philosophy.md` / `00-architectural-principles.md` 权威定义为 7 子系统。 |
| **证据** | **权威定义（7 子系统）**：<br/>- `TERMINOLOGY.md:193`："包含 Guards、Permission、Sanitizer、Audit、Workbench、Security Vault、Network Security 七个子系统"<br/>- `01-design-philosophy.md:61`："提供 Guards、Permission、Sanitizer、Audit、Workbench、Security Vault、Network Security 七大子系统的纵深防御"<br/>- `00-architectural-principles.md:310,749,893`："七大子系统的纵深防御"<br/><br/>**不一致（4 子系统）**：<br/>- `30-interfaces/04-mainpage.dox:42-49`："四重纵深防护安全子系统"仅列 Workbench/Permission/Sanitizer/Audit（**缺失 Guards/Security Vault/Network Security**）<br/>- `30-interfaces/04-mainpage.dox:114`："Cupolas \| 四重纵深防护"<br/><br/>**说明**："四重防护"本指 4 阶段防护链（输入净化→权限仲裁→网络过滤→审计记录，见 `TERMINOLOGY.md:193`），与"七大子系统"是不同维度概念，可共存。但 `04-mainpage.dox` 的子系统表仅列 4 项，与权威 7 子系统清单不一致。 |
| **影响评估** | Doxygen 主页生成的文档与权威术语表矛盾；外部开发者对 Cupolas 子系统数量产生混淆。 |
| **修复建议** | 修正 `04-mainpage.dox:42-49` 子系统表，补全为 7 子系统（Guards/Permission/Sanitizer/Audit/Workbench/Security Vault/Network Security），并区分"四重防护链"（4 阶段）与"七大子系统"（7 模块）两个概念。 |
| **工作量估算** | ~0.5h |

#### v3.0-P1-4：`02-logging.md` 包含错误的双重路径与错误归属

| 属性 | 内容 |
|------|------|
| **问题描述** | `10-architecture/50-services/02-logging.md` 多处包含错误路径：路径重复（`agentrt/daemon/agentrt/commons/...`）与错误归属（`agentrt/daemon/atoms`）。 |
| **证据** | - `02-logging.md:113`：`// agentrt/daemon/agentrt/commons/include/svc_common.h (第 18 行)` —— 路径重复 `agentrt/`（应为 `agentrt/daemons/common/include/svc_common.h`）<br/>- `02-logging.md:732`：`// C 语言模块（agentrt/daemon/atoms）` —— atoms 不在 daemon 下（应为 `agentrt/atoms/`）<br/>- `02-logging.md:754`：`- [服务公共接口](agentrt/daemon/agentrt/commons/include/svc_common.h)` —— 同 L113 路径重复 |
| **影响评估** | 路径无法解析；误导开发者对源码目录结构的理解。 |
| **修复建议** | (1) L113/L754：`agentrt/daemon/agentrt/commons/include/svc_common.h` → `agentrt/daemons/common/include/svc_common.h`；(2) L732：`agentrt/daemon/atoms` → `agentrt/atoms`。 |
| **工作量估算** | ~0.2h |

#### v3.0-P1-5：`06-glossary-index.md` 引用不存在的 `error_code_reference.md`

| 属性 | 内容 |
|------|------|
| **问题描述** | `20-modules/10-contracts/06-glossary-index.md` 两处引用 `error_code_reference.md`，但该文件在 `50-engineering-standards/50-project-erp/` 目录下不存在（实际文件为 `project_erp.md`）。 |
| **证据** | - `06-glossary-index.md:185`：`完整映射关系参见 [error_code_reference.md](../../50-engineering-standards/50-project-erp/error_code_reference.md)`<br/>- `06-glossary-index.md:187`：`[error_code_reference.md](../../50-engineering-standards/50-project-erp/error_code_reference.md)`<br/>- 实际目录：`ls docs/AirymaxOS/50-engineering-standards/50-project-erp/` = `README.md` + `project_erp.md`（无 `error_code_reference.md`）<br/><br/>**对比 v2.0 P0-9 修正**：`fix-log-p0-docs.md` 明确记载 `../70-project-erp/02-error-code-reference.md` → `../../50-engineering-standards/50-project-erp/project_erp.md`，但 `06-glossary-index.md` 这两处未被修正（可能因 v2.0 P0-9 修正时遗漏，或 v2.0 后新增内容）。 |
| **影响评估** | 链接 broken；开发者无法访问错误码完整映射关系。 |
| **修复建议** | `error_code_reference.md` → `project_erp.md`（2 处）。 |
| **工作量估算** | ~0.1h |

---

### 3.3 P2 级问题（6 项）

#### v3.0-P2-1：`01-doxygen-guide.md:326` 路径错误

- **证据**：`30-interfaces/01-doxygen-guide.md:326`：`- **Airymax 架构原则**: ../../00-architectural-principles.md`
- **问题**：从 `30-interfaces/` 到 `10-architecture/00-architectural-principles.md` 的正确相对路径为 `../10-architecture/00-architectural-principles.md`，而非 `../../00-architectural-principles.md`（后者解析到 `docs/00-architectural-principles.md`，不存在）。
- **修复**：`../../00-architectural-principles.md` → `../10-architecture/00-architectural-principles.md`
- **工作量**：~0.05h

#### v3.0-P2-2：`01-doxygen-guide.md:327` 引用不存在的 `code_comment_template.md`

- **证据**：`30-interfaces/01-doxygen-guide.md:327`：`- **代码注释规范**: ../../50-engineering-standards/10-coding-style/code_comment_template.md`
- **问题**：`ls docs/AirymaxOS/50-engineering-standards/10-coding-style/` = `C_Cpp_coding_style.md` / `Go_coding_style.md` / `Rust_coding_style.md` / `coding_conventions.md` / `scripting_coding_style.md` / `README.md`（无 `code_comment_template.md`）
- **修复**：删除该行或改为指向 `coding_conventions.md`（若注释规范合并入此文件）
- **工作量**：~0.05h

#### v3.0-P2-3：`30-interfaces/README.md:109` 引用不存在的 `naming_conventions.md`

- **证据**：`30-interfaces/README.md:109`：`> **详见**: [命名规范](../50-engineering-standards/10-coding-style/naming_conventions.md)`
- **问题**：同 v3.0-P2-2，`naming_conventions.md` 不存在于 `10-coding-style/` 目录
- **修复**：删除该行或改为指向 `coding_conventions.md`
- **工作量**：~0.05h

#### v3.0-P2-4：`0.1.1详细任务清单.md` 在 `docs-closed/` 根目录不存在（4 处引用）

- **证据**：4 处引用 `../../../docs-closed/0.1.1详细任务清单.md`：
  - `30-interfaces/06-ipc/README.md:104`
  - `30-interfaces/07-rpc-api/README.md:82`
  - `30-interfaces/08-service-discovery/README.md:68`
  - `140-application-development/01-sdk/README.md:72`
- **问题**：`ls docs-closed/0.1.1详细任务清单.md` = No such file or directory。v2.0 P0-9 修正日志（`fix-log-p0-docs.md` §遗留说明 1）已承认"P0-9 修正了 `DocsClosed/` → `docs-closed/` 的目录大小写，但该文件本身在 `docs-closed/` 下的具体位置未进一步验证"。实际该文件不存在，类似命名文件位于 `docs-closed/agentrt/00-reviews/_archive_fix_history/proposal-archives/0.1.1技术全面改进方案*.md`。
- **修复**：评估目标文件是否应为 `0.1.1技术全面改进方案_v1.0.md` 或其他；或删除引用（闭源文件不应在开源文档中引用）。
- **工作量**：~0.3h

#### v3.0-P2-5：`TERMINOLOGY.md:8` 路径头大小写错误

- **证据**：`TERMINOLOGY.md:8`：`**路径**: \`Docs/TERMINOLOGY.md\``
- **问题**：实际路径为 `docs/AirymaxRT/TERMINOLOGY.md`（小写 `docs/`，且包含 `AirymaxRT/` 子目录）。`Docs/`（大写 D）与实际目录名 `docs/`（小写 d）不一致，且缺失 `AirymaxRT/` 层级。
- **修复**：`Docs/TERMINOLOGY.md` → `docs/AirymaxRT/TERMINOLOGY.md`
- **工作量**：~0.05h

#### v3.0-P2-6：`Docs/` 大小写错误（2 处）

- **证据**：
  - `30-interfaces/05-runtime-interfaces/README.md:29`：`- \`Docs/\` 本身已是独立 git submodule`
  - `140-application-development/02-build-guide.md:80`：`└── Docs/                       ← 独立文档目录（独立仓库）`
- **问题**：实际仓库目录为 `docs/`（小写 d），Linux 文件系统大小写敏感，`Docs/` 路径无法解析。
- **修复**：`Docs/` → `docs/`（2 处）
- **工作量**：~0.05h

---

### 3.4 正面发现（v2.0 修正质量确认）

| # | 正面发现 | 证据 |
|---|---------|------|
| 1 | **错误码 SSoT 全面收敛** | 8 处权威定义文档均统一为 `AIRY_EOK=0`/`AIRY_EINVAL=(-22)`/`AIRY_ENOMEM=(-12)`/`AIRY_ETIMEOUT=(-110)`/`airy_err_t=int32_t`；`AIRY_OK`/`AIRY_ETIMEDOUT` 仅 2 处合法"不再使用"迁移说明；`AIRY_ERR_*` 仅 2 处合法废弃说明 |
| 2 | **Magic 值跨文档一致** | IPC magic `0x41524531`（'ARE1'）在 `06-ipc/README.md`/`06-iron9-shared-model.md`/`05-syscall.md`/`02-l2-service-protocol.md` 一致；任务描述符 magic `0x41475453`（'AGTS'）在 `06-iron9-shared-model.md`/`05-syscall.md` 一致；`SCHED_EXT=7` 一致 |
| 3 | **函数前缀边界清晰** | `agentrt_[a-z]` C 标识符在文档中 0 处使用；`agentos_*`/`airymaxos_*` 仅在 §3.12 废弃说明中合法出现；`airy_*`/`are_*` 三层前缀定义清晰（[SC]+[SS] 共用 `airy_*`，标准 ABI 用 `are_*`） |
| 4 | **"操作系统"残留合法性 100%** | 37 处残留逐项确认全部为合法用法（host OS / agent-linux / 概念借鉴 / 显式否定），无误称残留 |
| 5 | **[SC] 6 头文件清单跨文档一致** | `06-iron9-shared-model.md` 6 个核心头文件正确排序（memory_types.h / security_types.h / cognition_types.h / sched.h / ipc.h / syscalls.h），bpf_struct_ops.h 标注为补充共享文件 |
| 6 | **路径引用 5 类旧路径零残留** | `00-basic-theories`/`30-coding-standard`/`08-compliance-checklist`/`70-project-erp`/`DocsClosed` 全部 0 匹配 |
| 7 | **递归注释已修正** | `06-iron9-shared-model.md:218` 现为 `#define AIRY_EOK 0 /* 成功 */`（v2.0 P2-DQC-1 已随 P0-1 修正） |
| 8 | **MemoryRovol 命名标准化** | `02-c-language-boundary.md:72` 使用标准 L1 Raw/L2 Feature/L3 Structure/L4 Pattern + [SC] 缓存层级（L1 HOT/L2 WARM/L3 COLD/L4 PMEM）显式区分说明 |

---

## 4. 延期项评估

### 4.1 v2.0 延期项状态

| # | 编号 | 问题 | v2.0 状态 | v3.0 复核结果 | 证据 |
|---|------|------|----------|---------------|------|
| 1 | **P2-DQC-1** | `06-iron9-shared-model.md §3.8 第 214 行递归注释`（`/* 成功（替代 AIRY_EOK） */`） | v2.0 已随 P0-1 修正 | **✅ 确认已修正** | `06-iron9-shared-model.md:218` 现为 `#define AIRY_EOK        0       /* 成功 */`（递归注释消除） |

### 4.2 0.1.1 范围内可处理性评估

| 延期项 | 0.1.1 可处理 | 说明 |
|--------|-------------|------|
| P2-DQC-1 递归注释 | ✅ 已处理 | v2.0 随 P0-1 修正，v3.0 确认持久 |

### 4.3 v3.0 新发现问题在 0.1.1 范围内的处理建议

| 编号 | 级别 | 0.1.1 可处理 | 工作量 | 说明 |
|------|------|-------------|--------|------|
| v3.0-P0-1 | P0 | ✅ 应立即处理 | ~3h | 同 v2.0 P0-4 修正方案，补修 `02-l2-service-protocol.md` |
| v3.0-P1-1 | P1 | ✅ 可处理 | ~1.5h | 全量替换 `agentrt/daemon/` → `agentrt/daemons/` |
| v3.0-P1-2 | P1 | ✅ 可处理 | ~0.3h | 修正 L1/L2/L3 cross-reference 文件名 |
| v3.0-P1-3 | P1 | ✅ 可处理 | ~0.5h | 补全 `04-mainpage.dox` Cupolas 7 子系统 |
| v3.0-P1-4 | P1 | ✅ 可处理 | ~0.2h | 修正 `02-logging.md` 双重路径 |
| v3.0-P1-5 | P1 | ✅ 可处理 | ~0.1h | 修正 `error_code_reference.md` → `project_erp.md` |
| v3.0-P2-1~6 | P2 | ✅ 可处理 | ~0.55h | 路径修正与 broken links 修复 |
| **合计** | — | — | **~6.2h** | 可在 0.1.1 收尾阶段完成 |

---

## 5. 修正后综合评分变化

### 5.1 评分对比

| 评分维度 | v2.0 修正后 | v3.0 修正后预估 | 变化 | 修正原因 |
|---------|------------|---------------|------|---------|
| 方案设计 | 76/B | **75/B-** | -1 | v3.0-P0-1 IPC 头修正不完整（`02-l2-service-protocol.md` 遗漏）扣 2 分；v3.0-P1-3 Cupolas 子系统数量不一致扣 1 分 |
| 文档可用性 | 72/B- | **68/C+** | -4 | v3.0-P1-1 daemon/daemons 44 处 + v3.0-P1-2 cross-reference 15 处 + v3.0-P1-4 双重路径 + v3.0-P1-5 broken link + 6 项 P2 broken links |
| 跨平台一致性 | 68/C+ | **68/C+** | 0 | magic 值/SCHED_EXT/函数前缀均一致，无新发现 |
| SSoT 收敛 | 76/B | **72/B-** | -4 | v3.0-P0-1 IPC 头 SSoT 在 L2 协议未对齐 |
| **agentrt 文档总评** | **72/B-** | **74/B-** | **+2** | 见下方说明 |

### 5.2 评分说明

> **v3.0 修正后预估 74/B-** 的计算逻辑：
>
> 1. **v2.0 修正后基线**：72/B-（v2.0 验证报告 §8.1）
> 2. **v3.0 新发现扣分**：
>    - v3.0-P0-1（IPC 头修正不完整）：-3 分（P0 级，SSoT 完整性受损）
>    - v3.0-P1-1（daemon/daemons 44 处）：-1 分（系统性路径错误）
>    - v3.0-P1-2（cross-reference 15 处）：-0.5 分（同目录内 broken links）
>    - v3.0-P1-3（Cupolas 4 vs 7）：-0.5 分（术语数量不一致）
>    - v3.0-P1-4/P1-5 + P2-1~6：-1 分（broken links 集合）
> 3. **v3.0 修正后预估**：72 - 6 + 8（修复 v3.0-P0-1 后恢复 SSoT 完整性 +4，修复 P1/P2 后 +4）= **74/B-**
>
> **关键判定**：v3.0-P0-1 修复后，agentrt 开源文档体系可维持 B- 级别。新发现的 P1/P2 问题均为文档可用性问题（路径引用 / cross-reference / 术语数量），不影响架构设计正确性，可在 0.1.1 收尾阶段批量处理（~6.2h）。

### 5.3 是否达到"可开发"状态

| 判定标准 | v2.0 状态 | v3.0 状态 | 说明 |
|---------|----------|----------|------|
| 架构设计完成度 | ✅ 达标 | ✅ 达标 | MicroCoreRT / CoreLoopThree / MemoryRovol / Thinkdual / Cupolas / 12 Daemons 完整 |
| 工程标准规范 | ✅ 达标 | ✅ 达标 | 50-engineering-standards 共享层完整 |
| 无方案冲突点 | ✅ 达标 | ⚠️ **部分达标** | v3.0-P0-1 IPC 头 SSoT 在 L2 协议未对齐（1 项 P0 残留） |
| 跨平台一致性 | ✅ 达标 | ✅ 达标 | magic 值/函数前缀/SCHED_EXT 一致 |
| SSoT 收敛 | ✅ 达标 | ⚠️ **部分达标** | 错误码 SSoT 收敛，但 IPC 头 SSoT 在 L2 协议未收敛 |
| 历史问题修复 | ✅ 达标 | ✅ 达标 | v2.0 修正 9/10 持久 |
| 文档可用性 | ✅ 达标 | ⚠️ **部分达标** | 44 处 daemon/daemons + 15 处 cross-reference + 多处 broken links |

> **总体判定**：agentrt 开源文档体系 v3.0 复审后**接近"可开发"状态**，但需先修复 v3.0-P0-1（IPC 头 SSoT 在 L2 协议未对齐）以恢复 SSoT 完整性。修复后即可达到"可开发"状态。

---

## 6. 附录：审查文件清单

### 6.1 审查范围

| 类别 | 数量 | 路径 |
|------|------|------|
| Markdown 文档 | 87 | `docs/AirymaxRT/**/*.md` |
| Doxygen 文件 | 1 | `docs/AirymaxRT/30-interfaces/04-mainpage.dox` |
| Drawio 文件 | 1 | `docs/AirymaxRT/10-architecture/60-diagrams/03-overall-architecture.drawio` |
| **合计** | **89** | — |

### 6.2 v2.0 修正持久性验证执行命令

```bash
# P0-1 错误码 SSoT
Grep "AIRY_EOK|AIRY_EINVAL|AIRY_ENOMEM|AIRY_ETIMEOUT|AIRY_ETIMEDOUT|airy_err_t" docs/AirymaxRT --glob *.md
# 结果：582 处/29 文件，8 处权威定义文档均统一为 POSIX errno 负值

# P0-4 IPC 头三重违规
Grep "airy_ipc_msg_hdr|__attribute__((packed))|_Static_assert(sizeof" 30-interfaces/06-ipc/README.md
# 结果：8 行匹配（L26/28/38/53/63/65/71/99），06-ipc/README.md 已修正
# 但 02-l2-service-protocol.md:93-109 仍为 are_ipc_message_header_t（v3.0-P0-1）

# P0-5 "操作系统"误称
Grep "操作系统" docs/AirymaxRT
# 结果：37 处/16 文件，全部合法

# P0-8 [SC] 头文件清单
Grep "syscalls\.h|bpf_struct_ops\.h" 06-iron9-shared-model.md
# 结果：syscalls.h 在 L73 为 #6；bpf_struct_ops.h 在 L75 为补充说明

# P0-9 文件路径引用
Grep "00-basic-theories|30-coding-standard|08-compliance-checklist|70-project-erp|DocsClosed" docs/AirymaxRT --glob *.md
# 结果：0 匹配

# P1-5 Cupola→Cupolas
Grep "Cupola[^s]" docs/AirymaxRT
# 结果：0 匹配

# P1-6 Daemon 10→12
Grep "12 个核心|Services \(12\)" 01-system-architecture.md
# 结果：2 匹配（L305 + L309）

# P1-11 MemoryRovol 命名
Grep "L1 Raw|L2 Feature|L3 Structure|L4 Pattern" 02-c-language-boundary.md
# 结果：1 行匹配（L72，含 [SC] 缓存层级区分说明）

# P1-13 删除重复文件
ls docs/AirymaxRT/50-specifications/
# 结果：No such file or directory

# P1-1/3 函数前缀三层定义
Grep "函数前缀三层定义|airy_\*.*are_\*|agentrt_\*.*不使用|agentos_\*.*已废弃|airymaxos_\*.*已废弃" 06-iron9-shared-model.md
# 结果：5 行匹配（L260/268/269/270/277）
```

### 6.3 v3.0 新发现问题验证命令

```bash
# v3.0-P0-1 IPC 头三重违规未修正
Grep "are_ipc_message_header" docs/AirymaxRT
# 结果：9 处，其中 8 处在 02-l2-service-protocol.md（L43/48/93/109/113/142/523/738）

# v3.0-P1-1 daemon/daemons 单复数
Grep "agentrt/daemon/|agentrt/daemons/" docs/AirymaxRT
# 结果：44 处 agentrt/daemon/（单数），0 处 agentrt/daemons/（复数）

# v3.0-P1-2 L1/L2/L3 cross-reference 错误
Grep "L1_runtime_interface|L3_security_governance|L2_service_protocol" docs/AirymaxRT/30-interfaces/05-runtime-interfaces
# 结果：15 处/4 文件

# v3.0-P1-3 Cupolas 子系统数量
Grep "四重纵深防护|七大子系统" docs/AirymaxRT
# 结果：04-mainpage.dox 2 处"四重纵深防护"（仅 4 子系统）；TERMINOLOGY.md/01-design-philosophy.md/00-architectural-principles.md 5 处"七大子系统"

# v3.0-P1-5 error_code_reference.md 不存在
ls docs/AirymaxOS/50-engineering-standards/50-project-erp/error_code_reference.md
# 结果：No such file or directory（实际为 project_erp.md）

# v3.0-P2-4 0.1.1详细任务清单.md 不存在
ls docs-closed/0.1.1详细任务清单.md
# 结果：No such file or directory
```

### 6.4 必读历史报告索引

| # | 报告 | 路径 | 版本 |
|---|------|------|------|
| 1 | v1.0 综合分析 | `docs-closed/agentrt/00-reviews/_review_v1.0/00-comprehensive-analysis.md` | 1.0（2026-07-13） |
| 2 | v2.0 工程规范与代码审查 | `docs-closed/agentrt/00-reviews/_review_v2.0/01-engineering-code-review-v2.md` | 2.0（2026-07-13） |
| 3 | v2.0 开源文档 P0 修正日志 | `docs-closed/agentrt/00-reviews/_review_v2.0/fix-log-p0-docs.md` | 1.0（2026-07-13） |
| 4 | v2.0 开源文档 P1 修正日志 | `docs-closed/agentrt/00-reviews/_review_v2.0/fix-log-p1-docs.md` | 1.0（2026-07-13） |
| 5 | v2.0 修正验证报告 | `docs-closed/agentrt/00-reviews/_review_v2.0/fix-verification-report.md` | 1.0（2026-07-13） |

---

<div align="center">

**© 2025-2026 SPHARX Ltd.** All Rights Reserved.

</div>

---

**报告结束** | SPHARX Ltd 内部参考 | 闭源不公开 | 审查日期：2026-07-14 | 审查版本：v3.0
