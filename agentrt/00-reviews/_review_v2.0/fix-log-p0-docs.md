Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
"From data intelligence emerges."

# P0 文档修正日志

> **修正范围**: `docs/AirymaxRT/` 开源文档
> **修正依据**: v2.0 工程审查报告（`01-engineering-code-review-v2.md` §5 P0 问题逐项验证）
> **修正日期**: 2026-07-13
> **修正人**: 极境工程与规范委员会
> **约束**: 仅修正 `docs/AirymaxRT/` 下文件；不修改 `docs/AirymaxOS/`、源代码、闭源文档

---

## P0-1 错误码 SSoT 统一

**问题**: 8 个文件存在 7+ 套不同错误码定义方案（正值/负值混用、`AIRY_OK`/`AIRY_EOK` 混用、`AIRY_ETIMEDOUT`/`AIRY_ETIMEOUT` 拼写不一致、enum/define 风格混用）。

**修正方案**: 统一为 `#define` 宏 + POSIX errno 负值；成功码统一为 `AIRY_EOK=0`；类型 `airy_err_t = int32_t`（定义于 `cognition_types.h`）；SSoT 权威位于 `include/airymax/error.h`（[SC] 共享契约层）。

**SSoT 错误码值**（对齐 POSIX errno 负值）:
```
AIRY_EOK=0, AIRY_EPERM=-1, AIRY_ENOENT=-2, AIRY_EIO=-5,
AIRY_EAGAIN=-11, AIRY_ENOMEM=-12, AIRY_EBUSY=-16, AIRY_EEXIST=-17,
AIRY_EINVAL=-22, AIRY_ENOSYS=-38, AIRY_ETIMEOUT=-110
```

**修正记录**:

| 文件:行号 | 修改前 → 修改后 | 验证结果 |
|----------|---------------|---------|
| `10-architecture/00-architectural-principles.md:~919-944` | `typedef enum` + POSIX errno 正值 → `#define` 宏 + POSIX errno 负值；添加 SSoT 声明 | OK — Grep 确认 `AIRY_EOK=0`、`AIRY_EINVAL=(-22)`、`airy_err_t` |
| `10-architecture/06-iron9-shared-model.md:~208-223` | 递归注释 `/* 成功（替代 AIRY_EOK） */` → `/* 成功 */`；添加 `airy_err_t` 类型定义和 `AIRY_ETIMEOUT=-110` | OK — Grep 确认 `AIRY_ETIMEOUT` 拼写统一 |
| `10-architecture/05-syscall.md:~636-668` | 正值序列 1001/1002/1003 → POSIX errno 负值；Airymax 专属错误码改为负值（-2001/-3001 等） | OK |
| `20-modules/10-contracts/04-syscall-api-contract.md:~90-110` | §1.3.1 错误码正值 → 负值 | OK |
| `20-modules/10-contracts/04-syscall-api-contract.md:~1297-1311` | §7.1 错误码正值 → 负值 | OK |
| `20-modules/10-contracts/06-glossary-index.md:~169-187` | `AIRY_OK` → `AIRY_EOK`；`AIRY_ETIMEDOUT` → `AIRY_ETIMEOUT` | OK |
| `30-interfaces/README.md:~74-88` | 错误码正值 → 负值 | OK |
| `20-modules/10-contracts/03-protocol-contract.md:~488-504,686-716,535-540,749-763` | 多处 `AIRY_OK` → `AIRY_EOK`；正值 → 负值 | OK |
| `30-interfaces/05-runtime-interfaces/01-l1-runtime-interface.md:~46-69` | 保留 `ARE_*` 前缀（标准 ABI）；添加 `ARE_* ↔ AIRY_*` 映射表；`are_error_t` 标注与 `airy_err_t` 等价 | OK |
| `30-interfaces/60-syscalls/04-skill.md:~634-647` | 错误码正值 → 负值 | OK |
| `30-interfaces/05-runtime-interfaces/03-l3-security-governance.md:~300-314,345-346` | `AIRY_ERR_*` → `AIRY_E*` | OK |
| `20-modules/10-contracts/05-logging-format.md:~299-301` | 错误码引用统一 | OK |
| `30-interfaces/60-syscalls/06-telemetry.md:~98` | 错误码引用统一 | OK |
| `TERMINOLOGY.md:~203-216` | `AIRY_OK` → `AIRY_EOK`；`AIRY_ETIMEDOUT` → `AIRY_ETIMEOUT`；添加 SSoT 声明 | OK |

---

## P0-4 IPC 消息头三重违规

**问题**: IPC 消息头存在三重违规——(1) 命名违规（`are_ipc_message_header_t` 而非 `airy_ipc_msg_hdr`）；(2) 类型违规（`uint32_t` 等 C 标准库类型而非 `__u32` 等 UAPI 类型）；(3) 布局违规（13 字段 + `aligned(64)` 而非 8 字段 + `__attribute__((packed))`）。

**修正方案**: 对齐 SSoT 源码 `agentrt/commons/include/airymax/ipc.h`，使用 `struct airy_ipc_msg_hdr`（128 字节，8 字段，`__attribute__((packed))`，`_Static_assert(sizeof(...) == 128)`）。

**修正记录**:

| 文件:行号 | 修改前 → 修改后 | 验证结果 |
|----------|---------------|---------|
| `30-interfaces/06-ipc/README.md:~24-100` | 结构体名 `are_ipc_message_header_t` → `struct airy_ipc_msg_hdr` | OK — Grep 确认 `airy_ipc_msg_hdr` |
| 同上 | 类型 `uint32_t/uint16_t/uint64_t` → `__u32/__u16/__u64/__u8` | OK — Grep 确认 UAPI 类型 |
| 同上 | 对齐 `aligned(64)` → `__attribute__((packed))` | OK — Grep 确认 `packed` |
| 同上 | 添加 `_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128)` | OK — Grep 确认 `_Static_assert` |
| 同上 | 字段数 13 → 8（magic/opcode/flags/trace_id/timestamp_ns/src_task/dst_task/payload_len/reserved[84]） | OK |
| 同上 | 添加迁移对应关系表 | OK |
| 同上 | 更新 §2.3 兼容性策略 | OK |

**SSoT 结构体定义**:
```c
struct airy_ipc_msg_hdr {
    __u32   magic;          /* offset 0,  'ARE1' (0x41524531) */
    __u16   opcode;         /* offset 4 */
    __u16   flags;          /* offset 6 */
    __u64   trace_id;       /* offset 8 */
    __u64   timestamp_ns;   /* offset 16 */
    __u64   src_task;       /* offset 24 */
    __u64   dst_task;       /* offset 32 */
    __u32   payload_len;    /* offset 40 */
    __u8    reserved[84];   /* offset 44, 84 bytes */
} __attribute__((packed));

_Static_assert(sizeof(struct airy_ipc_msg_hdr) == 128,
    "IPC message header must be exactly 128 bytes");
```

---

## P0-5 "操作系统"定位冲突

**问题**: 51 处/18 文件误称 agentrt 为"操作系统"。agentrt 的准确定位是 "AI Agent Runtime Platform Engineering"（AI Agent 运行时平台工程），对标 JVM/containerd 之于语言/容器的运行底座。MicroCoreRT 是用户态微核心（运行在 Ring 3，非操作系统内核）。

**修正方案**: 区分误称（agentrt 被称为 OS）与合法用法（指代宿主 OS、agentrt-linux/AirymaxOS 是真正的 OS、OS 概念借鉴、显式否定如"MicroCoreRT 不是操作系统内核"）。修正 17 处误称，保留 34 处合法用法。

**修正记录**（10 个文件，~17 处修正）:

| 文件:行号 | 修改前 → 修改后 | 验证结果 |
|----------|---------------|---------|
| `30-interfaces/04-mainpage.dox:2` | "操作系统" → "运行时平台" | OK — Grep 确认 "运行时平台" |
| `30-interfaces/04-mainpage.dox:6` | "操作系统" → "运行时平台" | OK |
| `10-architecture/00-architectural-principles.md:54` | agentrt 误称"操作系统" → "运行时平台" | OK |
| `00-requirements/04-design-principles-cn.md:14` | "操作系统" → "运行时平台" | OK |
| `00-requirements/04-design-principles-cn.md:99` | "操作系统" → "运行时平台" | OK |
| `10-architecture/04-microcorert.md:13` | "操作系统" → "运行时平台/微核心" | OK |
| `10-architecture/04-microcorert.md:19` | "操作系统" → "运行时平台/微核心" | OK |
| `10-architecture/04-microcorert.md:271` | "操作系统" → "运行时平台/微核心" | OK |
| `10-architecture/05-syscall.md:104` | "操作系统" → "运行时平台" | OK |
| `20-modules/10-contracts/05-logging-format.md:73` | "操作系统" → "运行时平台" | OK |
| `30-interfaces/10-algorithms/README.md:179` | "操作系统" → "运行时平台" | OK |
| `30-interfaces/10-algorithms/README.md:182` | "操作系统" → "运行时平台" | OK |
| `140-application-development/01-getting-started.md:127` | "操作系统" → "运行时平台" | OK |
| `10-architecture/40-philosophy/01-design-philosophy.md:45` | "操作系统" → "运行时平台" | OK |
| `10-architecture/40-philosophy/01-design-philosophy.md:110` | "操作系统" → "运行时平台（用户态微核心，非操作系统内核）" | OK |
| `10-architecture/40-philosophy/01-design-philosophy.md:117,119` | "操作系统" → "运行时" | OK |
| `TERMINOLOGY.md:320` | "操作系统" → "运行时内核抽象层（用户态微核心，非操作系统内核）" | OK |

**保留的合法用法**（34 处，未修改）:
- 指代宿主 OS（如"运行于操作系统之上"）
- 指代 agentrt-linux/AirymaxOS（真正的 OS）
- OS 概念借鉴（如"借鉴操作系统设计的经典智慧"）
- 显式否定（如"MicroCoreRT 不是操作系统内核"、"不运行在 ring 0"）

---

## P0-8 [SC] 头文件清单不一致

**问题**: `bpf_struct_ops.h` 被列为 [SC] 核心头文件 #1，而 `syscalls.h` 完全缺失。实际 SSoT 定义 6 个 [SC] 核心头文件，`bpf_struct_ops.h` 为补充共享文件（非核心头文件）。

**修正方案**: 对齐 `docs/AirymaxRT/50-engineering-standards/120-cross-project-code-sharing.md` §2.1 的 SSoT 清单。

**修正记录**:

| 文件:行号 | 修改前 → 修改后 | 验证结果 |
|----------|---------------|---------|
| `10-architecture/06-iron9-shared-model.md:64-75` | `bpf_struct_ops.h` 列为 #1，`syscalls.h` 缺失 → 6 个 [SC] 核心头文件正确排序：1.memory_types.h 2.security_types.h 3.cognition_types.h 4.sched.h 5.ipc.h 6.syscalls.h | OK — Grep 确认 `syscalls.h` 为 #6 |
| 同上 | `bpf_struct_ops.h` 无说明 → 添加"补充共享文件（非 [SC] 核心头文件）"说明，引用 `120-cross-project-code-sharing.md` §2.2 | OK — Grep 确认 `bpf_struct_ops.h` 为补充说明 |

---

## P0-9 文件路径引用错误

**问题**: 系统性引用不存在路径，共 44 行错误引用分布在 16 个文件中，分 5 类：
1. `00-basic-theories/` → 应为 `00-requirements/`（目录已重命名）
2. `30-coding-standard/` → 应为 `50-engineering-standards/10-coding-style/`（目录已迁移并重组）
3. `08-compliance-checklist.md` → 文件不存在（合规检查清单已合并入 `05-development-process.md` Part III）
4. `70-project-erp/` → 目录不存在（实际为 `50-engineering-standards/50-project-erp/`）
5. `DocsClosed/` → 应为 `docs-closed/`（大小写错误）

**文件名映射表**（`30-coding-standard/` → `50-engineering-standards/10-coding-style/`）:

| 旧文件名 | 新文件名 | 说明 |
|---------|---------|------|
| `10-log-standard.md` | `coding_conventions.md` (Part III 日志打印) | 日志打印规范合并入编码约定合集 |
| `01-c-coding-style.md` | `C_Cpp_coding_style.md` | C 风格规范合并入 C/C++ 合集 |
| `02-c-cpp-secure-coding.md` | `C_Cpp_coding_style.md` (Part IV 安全编码) | C/C++ 安全编码合并入合集 |
| `13-rust-coding-style.md` | `Rust_coding_style.md` | Rust 风格+安全合并 |
| `14-rust-secure-coding.md` | `Rust_coding_style.md` (Part II 安全编码) | Rust 安全编码合并入合集 |
| `06-go-coding-style.md` | `Go_coding_style.md` | Go 风格+安全合并 |
| `07-go-secure-coding.md` | `Go_coding_style.md` (Part II 安全编码) | Go 安全编码合并入合集 |
| `15-security-design.md` | `coding_conventions.md` (Part V 安全设计) | 安全设计合并入编码约定合集 |

**修正记录**（16 个文件，44 行修正）:

| 文件:行号 | 修改前 → 修改后 | 验证结果 |
|----------|---------------|---------|
| `TERMINOLOGY.md:604-607` | `00-basic-theories/0X-*.md` → `00-requirements/0X-*.md`（4 处） | OK |
| `20-modules/10-contracts/04-syscall-api-contract.md:65` | `../30-coding-standard/10-log-standard.md` → `../../50-engineering-standards/10-coding-style/coding_conventions.md` | OK |
| `20-modules/10-contracts/04-syscall-api-contract.md:1295` | `../70-project-erp/02-error-code-reference.md` → `../../50-engineering-standards/50-project-erp/project_erp.md` | OK |
| `20-modules/10-contracts/04-syscall-api-contract.md:1363` | `../30-coding-standard/10-log-standard.md` → `../../50-engineering-standards/10-coding-style/coding_conventions.md` | OK |
| `20-modules/10-contracts/04-syscall-api-contract.md:1370` | `../../00-basic-theories/04-design-principles-cn.md` → `../../00-requirements/04-design-principles-cn.md` | OK |
| `20-modules/10-contracts/06-glossary-index.md:124-127` | `../30-coding-standard/13-rust-coding-style.md` 等 4 处 → `../../50-engineering-standards/10-coding-style/Rust_coding_style.md` 等 | OK |
| `20-modules/10-contracts/06-glossary-index.md:164-165` | `../30-coding-standard/01-c-coding-style.md` 等 2 处 → `../../50-engineering-standards/10-coding-style/C_Cpp_coding_style.md` | OK |
| `20-modules/10-contracts/02-skill-contract.md:42-43` | `../../00-basic-theories/04-design-principles-cn.md` 等 2 处 → `../../00-requirements/` | OK |
| `20-modules/10-contracts/02-skill-contract.md:998-999` | `../30-coding-standard/02-c-cpp-secure-coding.md` 等 2 处 → `../../50-engineering-standards/10-coding-style/C_Cpp_coding_style.md` 和 `coding_conventions.md` | OK |
| `20-modules/10-contracts/02-skill-contract.md:1005-1006` | `../../00-basic-theories/0X-*.md` 2 处 → `../../00-requirements/` | OK |
| `20-modules/10-contracts/05-logging-format.md:952` | `../30-coding-standard/10-log-standard.md` → `../../50-engineering-standards/10-coding-style/coding_conventions.md` | OK |
| `20-modules/10-contracts/05-logging-format.md:960` | `../../00-basic-theories/04-design-principles-cn.md` → `../../00-requirements/04-design-principles-cn.md` | OK |
| `20-modules/10-contracts/03-protocol-contract.md:45` | `../30-coding-standard/10-log-standard.md` → `../../50-engineering-standards/10-coding-style/coding_conventions.md` | OK |
| `20-modules/10-contracts/03-protocol-contract.md:688` | `../70-project-erp/02-error-code-reference.md` → `../../50-engineering-standards/50-project-erp/project_erp.md` | OK |
| `20-modules/10-contracts/03-protocol-contract.md:869` | `../30-coding-standard/10-log-standard.md` → `../../50-engineering-standards/10-coding-style/coding_conventions.md` | OK |
| `20-modules/10-contracts/03-protocol-contract.md:876` | `../../00-basic-theories/04-design-principles-cn.md` → `../../00-requirements/04-design-principles-cn.md` | OK |
| `20-modules/10-contracts/01-agent-contract.md:42,44` | `../../00-basic-theories/02-cognition-design-cn.md` 2 处 → `../../00-requirements/02-cognition-design-cn.md` | OK |
| `20-modules/10-contracts/01-agent-contract.md:814-815` | `../30-coding-standard/02-c-cpp-secure-coding.md` 等 2 处 → `../../50-engineering-standards/10-coding-style/C_Cpp_coding_style.md` 和 `coding_conventions.md` | OK |
| `20-modules/10-contracts/01-agent-contract.md:821-822` | `../../00-basic-theories/0X-*.md` 2 处 → `../../00-requirements/` | OK |
| `README.md:62` | `50-engineering-standards/08-compliance-checklist.md` → `50-engineering-standards/05-development-process.md`（Part III 合规检查清单） | OK |
| `README_zh.md:87` | `50-engineering-standards/08-compliance-checklist.md` → `50-engineering-standards/05-development-process.md`（Part III 合规检查清单） | OK |
| `10-architecture/00-architectural-principles.md:1519-1522` | `00-basic-theories/0X-*.md` 4 处 → `../00-requirements/0X-*.md` | OK |
| `140-application-development/05-config-change-process.md:353` | `specifications/30-coding-standard/15-security-design.md` → `50-engineering-standards/10-coding-style/coding_conventions.md`（Part V 安全设计） | OK |
| `30-interfaces/05-runtime-interfaces/03-l3-security-governance.md:360` | `../70-project-erp/02-error-code-reference.md` → `../../50-engineering-standards/50-project-erp/project_erp.md` | OK |
| `30-interfaces/06-ipc/README.md:104` | `../../../DocsClosed/0.1.1详细任务清单.md` → `../../../docs-closed/0.1.1详细任务清单.md` | OK |
| `30-interfaces/07-rpc-api/README.md:82` | `../../../DocsClosed/0.1.1详细任务清单.md` → `../../../docs-closed/0.1.1详细任务清单.md` | OK |
| `30-interfaces/08-service-discovery/README.md:68` | `../../../DocsClosed/0.1.1详细任务清单.md` → `../../../docs-closed/0.1.1详细任务清单.md` | OK |
| `140-application-development/01-sdk/README.md:72` | `../../../DocsClosed/0.1.1详细任务清单.md` → `../../../docs-closed/0.1.1详细任务清单.md` | OK |

**验证结果**: Grep 搜索 `00-basic-theories|30-coding-standard|08-compliance-checklist|70-project-erp|DocsClosed` 在 `docs/AirymaxRT/` 下返回 **0 匹配**（修正前 44 行匹配）。

---

## 修正统计汇总

| P0 编号 | 问题 | 修正文件数 | 修正处数 | 验证状态 |
|---------|------|----------|---------|---------|
| P0-1 | 错误码 SSoT 统一 | 13 | ~30 | OK |
| P0-4 | IPC 消息头三重违规 | 1 | 7 | OK |
| P0-5 | "操作系统"定位冲突 | 10 | ~17 | OK |
| P0-8 | [SC] 头文件清单不一致 | 1 | 2 | OK |
| P0-9 | 文件路径引用错误 | 16 | 44 | OK |
| **合计** | | **41**（去重后 ~28 个唯一文件） | **~100** | **全部 OK** |

---

## 遗留说明

1. **`docs-closed/0.1.1详细任务清单.md` 文件**: P0-9 修正了 `DocsClosed/` → `docs-closed/` 的目录大小写，但该文件本身在 `docs-closed/` 下的具体位置未进一步验证（可能位于子目录）。此为引用方文档的路径修正，不涉及目标文件创建。

2. **P0-1 与源码差异**: 文档统一使用 POSIX errno 负值（`AIRY_EINVAL=-22` 等），源码 `airy_types.h` 实际使用不同值（-1, -2, -6）。因任务约束"不修改源码"，文档侧以 POSIX errno 负值为 SSoT。源码侧的对齐留待 1.0.1 M1 阶段处理。

3. **P0-5 合法用法保留**: 34 处"操作系统"合法用法（指代宿主 OS、agentrt-linux/AirymaxOS、OS 概念借鉴、显式否定）已保留，未修改。

4. **P0-9 文件名映射**: `30-coding-standard/` 下原有 16 份源文件已于 2026-07-13 合并为 5 份合并文档（`C_Cpp_coding_style.md` / `Rust_coding_style.md` / `Go_coding_style.md` / `scripting_coding_style.md` / `coding_conventions.md`），文档引用已全部更新为新文件名。

---

© 2025-2026 SPHARX Ltd. All Rights Reserved.
