Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agent-linux v3.0 P0/P1 完整回归测试计划

> **文档定位**：agent-linux（AirymaxOS）v2.9 + v3.0 P0 系统性修复后的完整回归测试计划，覆盖全部 P0 项（4 项）+ P1 项（2 项）+ GAP 项（2 项）+ v3.0 深度残留修复验证，供手动验证执行
> **报告版本**：v3.0
> **生成日期**：2026-07-23
> **上游报告**：[`_review_v2.8/00-full-doc-audit-v2.8.md`](../_review_v2.8/00-full-doc-audit-v2.8.md)（问题发现）→ [`_review_v2.9/00-p0-fix-report-v2.9.md`](../_review_v2.9/00-p0-fix-report-v2.9.md)（首轮修复）→ [`00-p0-fix-report-v3.0.md`](./00-p0-fix-report-v3.0.md)（深度残留修复）
> **测试原则**：每一项修复必须有可执行的手动验证步骤 + 明确的通过/失败判定标准 + 证据留存要求

---

## 目录

- [1. 测试总览](#1-测试总览)
- [2. 测试环境准备](#2-测试环境准备)
- [3. P0-014: syscall 编号一致性回归测试](#3-p0-014-syscall-编号一致性回归测试)
- [4. P0-016: v0.2.8 版本号清除回归测试](#4-p0-016-v028-版本号清除回归测试)
- [5. P0-017: codegen 管道功能回归测试](#5-p0-017-codegen-管道功能回归测试)
- [6. P0-018: ABI 检查工具回归测试](#6-p0-018-abi-检查工具回归测试)
- [7. P1-01: superv/ 同名文件不同内容](#7-p1-01-superv-同名文件不同内容)
- [8. P1-02: airy_sys_ipc_register_ring 命名一致性](#8-p1-02-airy_sys_ipc_register_ring-命名一致性)
- [9. GAP-01: ~260 补丁维护成本验证](#9-gap-01-260-补丁维护成本验证)
- [10. GAP-02: fastpath 可观测性验证](#10-gap-02-fastpath-可观测性验证)
- [11. v3.0 深度残留修复验证](#11-v30-深度残留修复验证)
- [12. 整体一致性验证](#12-整体一致性验证)
- [13. 测试结果汇总模板](#13-测试结果汇总模板)
- [14. 通过/失败判定标准](#14-通过失败判定标准)

---

## 1. 测试总览

### 1.1 测试范围

| 类别 | 项目数 | 优先级 | 来源 |
|------|--------|--------|------|
| P0 项 | 4 | 阻断 | v2.8 审查报告确认真实 |
| P1 项 | 2 | 阻断（M1 前修复） | v1.2 内核框架验证发现 |
| GAP 项 | 2 | 非阻断 | v2.8 确认（GAP-01 真实 + GAP-02 部分真实） |
| v3.0 深度残留 | 2 文档 | 阻断 | v3.0 验证阶段新发现 |
| 整体一致性 | 7 维度 | 阻断 | v2.9/v3.0 验证框架 |
| **合计** | **17 项** | | |

### 1.2 测试策略

1. **ABI 三方一致性**：SSoT 文档 / `unistd.h` / `syscall_64.tbl` 三方编号必须完全一致
2. **文档扫描**：全量 Grep 扫描 `docs/AirymaxOS/` 确保无旧编号残留
3. **工具可执行**：codegen 与 ABI 检查工具必须实际运行并产出预期结果
4. **交叉验证**：op-dispatch 映射表必须在 SSoT 和下游文档中一致
5. **证据留存**：每项测试必须记录命令输出或文件内容作为证据

### 1.3 修复历史链路

```
v2.8 审查（问题发现）
  ├─ P0-014 syscall 编号三套矛盾模型
  ├─ P0-016 4 份 v0.2.8 文档违反 IRON-8
  ├─ P0-017 codegen 管道缺失
  └─ P0-018 ABI 检查工具缺失
       │
       ▼
v2.9 修复（首轮系统性修复）
  ├─ SSoT 完全重写（07-syscall-registry.md 914 行）
  ├─ 18 份文档修改
  ├─ 6 份工具文件新增
  └─ 2 份代码文件修改（unistd.h + syscall_64.tbl）
       │
       ▼
v3.0 修复（深度残留修复）
  ├─ 05-syscall-semantic-mapping.md 2 处（L147 + L260-262）
  └─ 04-token-budget.md 11 处（§8 系统性重写 + 分散引用）
       │
       ▼
v3.0 回归测试（本计划）
```

---

## 2. 测试环境准备

### 2.1 工作目录

```bash
cd /home/spharx/SpharxWorks/airymaxhub
```

### 2.2 关键路径

| 用途 | 路径 |
|------|------|
| 开源文档根 | `docs/AirymaxOS/` |
| SSoT syscall 注册表 | `docs/AirymaxOS/140-application-development/07-syscall-registry.md` |
| 内核 UAPI 头文件 | `agent-linux/kernel/include/uapi/asm-generic/unistd.h` |
| 内核 syscall 表 | `agent-linux/kernel/arch/x86/entry/syscalls/syscall_64.tbl` |
| codegen 契约源 | `agent-linux/kernel/include/uapi/linux/airymax/syscall.xml` |
| codegen 生成器 | `agent-linux/tools/codegen/syscall_gen.py` |
| ABI 检查工具 | `agent-linux/tools/abi-check/abi_check.py` |
| ABI 基线 | `agent-linux/tools/abi-check/abi_baseline.json` |

### 2.3 工具依赖

- Python 3.8+（运行 codegen 和 ABI 检查工具）
- ripgrep / grep（文档扫描）
- Git（版本对比）

---

## 3. P0-014: syscall 编号一致性回归测试

### 3.1 测试目标

验证 v1.0.1 Capability Folding 统一模型（4 核心 syscall 548-551 + op-dispatch + io_uring 数据面）在 SSoT 文档、内核代码、下游文档三方完全一致，无任何旧编号残留。

### 3.2 测试用例 TC-014-01: ABI 三方编号一致性

**验证点**：SSoT / unistd.h / syscall_64.tbl 三方编号完全一致。

**步骤**：

1. 读取 SSoT 文档的编号定义：

```bash
grep -n "548\|549\|550\|551" docs/AirymaxOS/140-application-development/07-syscall-registry.md | head -20
```

**预期输出**：包含 4 个核心 syscall 编号：
- `548 airy_sys_call`
- `549 airy_sys_rovol_ctl`
- `550 airy_sys_sched_ctl`
- `551 airy_sys_clt_notify`

2. 读取 unistd.h 编号定义：

```bash
grep -n "airy_sys" agent-linux/kernel/include/uapi/asm-generic/unistd.h
```

**预期输出**：L826-843 区域包含 4 行 `#define __NR_airy_sys_*` 定义，编号 548-551。

3. 读取 syscall_64.tbl 编号定义：

```bash
grep -n "airy_sys" agent-linux/kernel/arch/x86/entry/syscalls/syscall_64.tbl
```

**预期输出**：L378-387 区域包含 4 行 syscall 入口，编号 548-551。

**通过标准**：三方编号完全一致（548/549/550/551），无任何 454-457 / 512-535 / 512-631 残留。

**证据留存**：将三方 grep 输出粘贴到测试结果记录。

### 3.3 测试用例 TC-014-02: 旧编号残留扫描（512-547, 600-619）

**验证点**：`docs/AirymaxOS/` 全目录无旧 0.1.1 编号残留。

**步骤**：

```bash
grep -rnE "#(5(1[2-7]|2[0-9]|3[0-9]|4[0-7])|6(0[0-9]|1[0-9]))\b" docs/AirymaxOS/ | grep -i "airy_sys\|syscall" | head -30
```

**预期输出**：无任何匹配行（0 个残留）。

**注意**：此 Grep 模式排除了 548-551 的正确编号，只匹配 512-547 和 600-619 的旧编号段。

**通过标准**：输出为空或仅匹配无关内容（如端口号、行号等非 syscall 引用）。

### 3.4 测试用例 TC-014-03: 454-457 编号残留扫描

**验证点**：全仓库无 454-457 旧 x86 编号残留。

**步骤**：

```bash
grep -rn "454-457\|453-456" docs/AirymaxOS/ docs-closed/agent-linux/ agent-linux/kernel/include/ agent-linux/kernel/arch/
```

**预期输出**：无任何匹配行。

**通过标准**：输出为空。

### 3.5 测试用例 TC-014-04: op-dispatch 映射表交叉验证

**验证点**：SSoT 的 op-dispatch 映射表与下游文档引用一致。

**步骤**：

1. 读取 SSoT §4 op-dispatch 映射表：

```bash
grep -n "COMPILE_BADGE\|REVOKE_BADGE\|SNAPSHOT\|RESTORE\|MIGRATE\|TIER_SET\|SET_POLICY\|YIELD\|GET_LATENCY\|PHASE_NOTIFY\|REGISTER_KTHREAD" docs/AirymaxOS/140-application-development/07-syscall-registry.md | head -30
```

2. 验证下游文档引用一致：

```bash
grep -rn "airy_sys_call(COMPILE_BADGE)\|airy_sys_rovol_ctl(SNAPSHOT)\|airy_sys_sched_ctl(SET_POLICY)\|airy_sys_clt_notify(PHASE_NOTIFY)" docs/AirymaxOS/ | wc -l
```

**预期输出**：步骤 2 的计数 > 0（至少有多处下游引用）。

**通过标准**：op-dispatch 名称在 SSoT 和下游文档中完全匹配。

### 3.6 测试用例 TC-014-05: v3.0 深度残留修复验证（05-syscall-semantic-mapping.md）

**验证点**：v3.0 修复的 2 处残留已生效。

**步骤**：

1. 验证 L147 已修复：

```bash
sed -n '145,150p' docs/AirymaxOS/30-interfaces/05-syscall-semantic-mapping.md
```

**预期输出**：L147 包含 `#551 airy_sys_clt_notify(AIRY_CLT_WASM_LOAD_MODULE) + #551 airy_sys_clt_notify(AIRY_CLT_PHASE_NOTIFY)`，无 `#614 airy_sys_wasm_load_module`。

2. 验证 L260-262 已修复：

```bash
sed -n '258,265p' docs/AirymaxOS/30-interfaces/05-syscall-semantic-mapping.md
```

**预期输出**：L260-262 包含 `#551/#551/#550` + op-dispatch 名称，无 `#613/#614/#615`。

**通过标准**：2 处均为 v1.0.1 编号 + op-dispatch 形式。

### 3.7 测试用例 TC-014-06: v3.0 深度残留修复验证（04-token-budget.md §8）

**验证点**：v3.0 修复的 11 处残留已生效。

**步骤**：

1. 验证 §8 状态机引用：

```bash
grep -n "airy_sys_sched_ctl(SET_POLICY)\|airy_sys_sched_ctl(AIRY_SCHED_SET_POLICY)" docs/AirymaxOS/140-application-development/04-token-budget.md | head -10
```

**预期输出**：包含 `airy_sys_sched_ctl(SET_POLICY)` 或 `airy_sys_sched_ctl(AIRY_SCHED_SET_POLICY)`，无 `airy_sys_task_set_budget` / `airy_sys_task_get_budget`。

2. 验证 §8.2/§8.3 函数原型：

```bash
grep -n "airy_sys_sched_ctl(op" docs/AirymaxOS/140-application-development/04-token-budget.md | head -10
```

**预期输出**：函数原型为 `airy_sys_sched_ctl(op, agent_id, arg)` 形式。

3. 验证无旧独立 syscall 编号：

```bash
grep -n "523\|524" docs/AirymaxOS/140-application-development/04-token-budget.md | grep -i "task_set_budget\|task_get_budget"
```

**预期输出**：无匹配（0 个残留）。

**通过标准**：§8 全部使用 `airy_sys_sched_ctl` + op-dispatch 形式，无 523/524 旧编号。

---

## 4. P0-016: v0.2.8 版本号清除回归测试

### 4.1 测试目标

验证 `docs/AirymaxOS/` 目录下无任何 `0.2.8` 版本号残留（违反 IRON-8 铁律）。

### 4.2 测试用例 TC-016-01: v0.2.8 版本号全量扫描

**步骤**：

```bash
grep -rn "文档版本.*0\.2\.8\|version.*0\.2\.8\|v0\.2\.8" docs/AirymaxOS/ | head -20
```

**预期输出**：无任何匹配行（0 个残留）。

**通过标准**：输出为空。

### 4.3 测试用例 TC-016-02: 4 份目标文档版本号验证

**验证点**：v2.8 报告确认的 4 份 v0.2.8 文档已全部升级到 v1.0.1。

**步骤**：

1. codegen-pipeline.md：

```bash
grep -n "版本\|version" docs/AirymaxOS/30-interfaces/06-codegen-pipeline.md | head -5
```

**预期输出**：版本为 `v1.0.1`，无 `0.2.8`。

2. threat-model.md：

```bash
sed -n '5,8p' docs/AirymaxOS/10-architecture/08-threat-model.md
```

**预期输出**：L6 版本为 `v1.0.1`。

3. ci-cd-pipeline.md：

```bash
sed -n '4,7p' docs/AirymaxOS/70-build-system/03-ci-cd-pipeline.md
```

**预期输出**：L5 版本为 `v1.0.1`。

4. sbom-generation.md：

```bash
sed -n '4,7p' docs/AirymaxOS/190-distribution/06-sbom-generation.md
```

**预期输出**：L5 版本为 `v1.0.1`。

**通过标准**：4 份文档版本号均为 v1.0.1。

---

## 5. P0-017: codegen 管道功能回归测试

### 5.1 测试目标

验证 codegen 管道（syscall.xml → syscall_gen.py → C UAPI 头文件）功能完整可用。

### 5.2 测试用例 TC-017-01: syscall.xml 契约源完整性

**步骤**：

1. 验证文件存在：

```bash
ls -la agent-linux/kernel/include/uapi/linux/airymax/syscall.xml
```

**预期输出**：文件存在，大小 > 0。

2. 验证 4 个 syscall 元素：

```bash
grep -c "<syscall " agent-linux/kernel/include/uapi/linux/airymax/syscall.xml
```

**预期输出**：`4`。

3. 验证 linux_base 属性：

```bash
grep "linux_base" agent-linux/kernel/include/uapi/linux/airymax/syscall.xml
```

**预期输出**：`linux_base="548"`。

4. 验证 4 个 syscall 名称：

```bash
grep "<syscall " agent-linux/kernel/include/uapi/linux/airymax/syscall.xml
```

**预期输出**：包含 `airy_sys_call` / `airy_sys_rovol_ctl` / `airy_sys_sched_ctl` / `airy_sys_clt_notify`。

**通过标准**：4 项全部匹配。

### 5.3 测试用例 TC-017-02: syscall_gen.py 生成器可执行性

**步骤**：

1. 验证文件存在：

```bash
ls -la agent-linux/tools/codegen/syscall_gen.py
```

**预期输出**：文件存在。

2. 验证 Python 语法正确：

```bash
python3 -c "import ast; ast.parse(open('agent-linux/tools/codegen/syscall_gen.py').read()); print('syntax OK')"
```

**预期输出**：`syntax OK`。

3. 验证 --check 模式（契约校验）：

```bash
cd agent-linux/tools/codegen && python3 syscall_gen.py --check ../../kernel/include/uapi/linux/airymax/syscall.xml 2>&1 | tail -20
```

**预期输出**：输出校验通过信息，无错误。

**通过标准**：语法正确 + --check 模式运行无错误。

### 5.4 测试用例 TC-017-03: Makefile 构建入口

**步骤**：

1. 验证文件存在：

```bash
ls -la agent-linux/tools/codegen/Makefile
```

**预期输出**：文件存在。

2. 验证 Makefile 语法（dry-run）：

```bash
cd agent-linux/tools/codegen && make -n 2>&1 | head -10
```

**预期输出**：输出预期的构建命令（不实际执行），无语法错误。

**通过标准**：Makefile 语法正确。

### 5.5 测试用例 TC-017-04: 生成输出验证

**步骤**：

1. 执行生成：

```bash
cd agent-linux/tools/codegen && python3 syscall_gen.py --input ../../kernel/include/uapi/linux/airymax/syscall.xml --output /tmp/airy_syscalls_generated.h 2>&1
```

**预期输出**：生成成功，无错误。

2. 验证生成内容包含 4 个 syscall：

```bash
grep -c "__NR_airy_sys" /tmp/airy_syscalls_generated.h
```

**预期输出**：`4`（或更多，含预留槽）。

3. 验证编号正确：

```bash
grep "548\|549\|550\|551" /tmp/airy_syscalls_generated.h
```

**预期输出**：包含 548/549/550/551。

**通过标准**：生成内容包含正确的 4 个 syscall 编号。

---

## 6. P0-018: ABI 检查工具回归测试

### 6.1 测试目标

验证 ABI 检查工具（abi_check.py）可执行，且 6 项检查全部 PASS。

### 6.2 测试用例 TC-018-01: abi_check.py 可执行性

**步骤**：

1. 验证文件存在：

```bash
ls -la agent-linux/tools/abi-check/abi_check.py agent-linux/tools/abi-check/abi_baseline.json agent-linux/tools/abi-check/README.md
```

**预期输出**：3 个文件均存在。

2. 验证 Python 语法：

```bash
python3 -c "import ast; ast.parse(open('agent-linux/tools/abi-check/abi_check.py').read()); print('syntax OK')"
```

**预期输出**：`syntax OK`。

### 6.3 测试用例 TC-018-02: ABI 三方一致性检查（6/6 PASS）

**步骤**：

1. 执行 ABI 检查：

```bash
cd agent-linux/tools/abi-check && python3 abi_check.py 2>&1
```

**预期输出**：输出 6 项检查结果，全部为 `PASS`：
- SSoT syscall 编号一致性
- unistd.h 编号一致性
- syscall_64.tbl 编号一致性
- syscall.xml 契约一致性
- 预留槽位一致性
- op-dispatch 映射完整性

2. 验证退出码：

```bash
cd agent-linux/tools/abi-check && python3 abi_check.py > /dev/null 2>&1; echo "exit code: $?"
```

**预期输出**：`exit code: 0`。

**通过标准**：6/6 PASS + 退出码 0。

### 6.4 测试用例 TC-018-03: ABI 基线快照验证

**步骤**：

1. 验证基线文件包含 548-551：

```bash
grep "548\|549\|550\|551" agent-linux/tools/abi-check/abi_baseline.json
```

**预期输出**：包含 4 个核心 syscall 编号。

2. 验证基线文件无旧编号：

```bash
grep "454\|455\|456\|457\|512\|513\|514" agent-linux/tools/abi-check/abi_baseline.json | grep -v "548\|549\|550\|551"
```

**预期输出**：无匹配（0 个旧编号残留）。

**通过标准**：基线文件仅包含 548-551 正确编号。

---

## 7. P1-01: superv/ 同名文件不同内容

### 7.1 问题描述

v1.2 内核框架验证发现 `security/airy/` 与 `kernel/superv/` 存在 4 个同名但内容不同的源文件，违反 OS-STD-001"全局符号必须描述性命名"原则。

### 7.2 测试用例 TC-P1-01: 同名文件识别

**步骤**：

1. 列出 security/airy/ 的 .c 文件：

```bash
ls agent-linux/kernel/security/airy/*.c 2>/dev/null || echo "目录不存在或无 .c 文件"
```

2. 列出 kernel/superv/ 的 .c 文件：

```bash
ls agent-linux/kernel/kernel/superv/*.c 2>/dev/null || echo "目录不存在或无 .c 文件"
```

3. 识别同名文件：

```bash
comm -12 <(ls agent-linux/kernel/security/airy/*.c 2>/dev/null | xargs -n1 basename | sort) <(ls agent-linux/kernel/kernel/superv/*.c 2>/dev/null | xargs -n1 basename | sort)
```

**预期输出**：输出 4 个同名文件（或空，若 M1 阶段已重命名）：
- `airy_cap_check.c`
- `airy_die_notify.c`
- `airy_eventfd.c`
- `airy_ipc_freeze.c`

**通过标准**：
- 若输出为空（已重命名）：PASS
- 若输出 4 个文件（未重命名）：记录为"M1 待修复"（P1 项允许 M1 阶段修复）

### 7.3 测试用例 TC-P1-01-02: 重命名方案验证（M1 修复后）

**注**：此测试用例在 M1 阶段 `kernel/superv/` 下文件加 `_superv` 后缀后执行。

**步骤**：

1. 验证 kernel/superv/ 下文件已加后缀：

```bash
ls agent-linux/kernel/kernel/superv/*_superv.c 2>/dev/null
```

**预期输出**：包含 4 个带 `_superv` 后缀的文件。

**通过标准**：4 个文件均已重命名。

---

## 8. P1-02: airy_sys_ipc_register_ring 命名一致性

### 8.1 问题描述

v2.9 修复将 `airy_sys_ipc_register_ring` 等 0.1.1 独立 syscall 改为 io_uring cmd_op（v1.0.1 无独立 syscall），需验证文档中无旧命名残留。

### 8.2 测试用例 TC-P1-02: airy_sys_ipc_register_ring 残留扫描

**步骤**：

1. 扫描 docs/AirymaxOS/ 中的旧命名：

```bash
grep -rn "airy_sys_ipc_register_ring\|airy_sys_ipc_send\|airy_sys_ipc_recv" docs/AirymaxOS/ | grep -v "0\.1\.1\|历史\|migration\|附录\|Appendix\|deprecated\|废弃" | head -20
```

**预期输出**：无匹配（或仅出现在历史迁移映射表中，已通过 grep -v 排除）。

2. 验证 io_uring cmd_op 形式已使用：

```bash
grep -rn "IORING_OP_URING_CMD\|cmd_op=IPC_SEND\|cmd_op=IPC_RECV\|cmd_op=IPC_REGISTER_RING" docs/AirymaxOS/ | head -10
```

**预期输出**：至少有多处匹配。

**通过标准**：无旧独立 syscall 命名残留（排除历史迁移映射表）。

---

## 9. GAP-01: ~260 补丁维护成本验证

### 9.1 问题描述

v2.8 确认 GAP-01 真实：agent-linux 基于 Linux 6.6，有 ~260 个专属补丁，在 6.6→7.1 迁移时需重新适配，存在长期可维护性风险。

### 9.2 测试用例 TC-GAP-01: 补丁追踪文档完整性

**步骤**：

1. 验证补丁追踪文档存在：

```bash
ls -la docs/AirymaxOS/190-distribution/03-upstream-tracking.md 2>/dev/null || echo "文件不存在"
```

**预期输出**：文件存在。

2. 验证 §6.1 有 ~260 补丁的量化分析：

```bash
grep -n "260\|补丁\|patch" docs/AirymaxOS/190-distribution/03-upstream-tracking.md | head -10
```

**预期输出**：包含补丁数量量化分析。

3. 验证有迁移计划：

```bash
grep -n "迁移\|migration\|6\.6.*7\.1\|升级" docs/AirymaxOS/190-distribution/03-upstream-tracking.md | head -10
```

**预期输出**：包含 6.6→7.1 迁移计划。

**通过标准**：补丁追踪文档完整，包含量化分析和迁移计划。

**注**：GAP-01 为非阻断项，此项测试仅验证文档完整性，不要求补丁已迁移。

---

## 10. GAP-02: fastpath 可观测性验证

### 10.1 问题描述

v2.8 确认 GAP-02 部分真实：C-S9 fastpath 内联 Badge 校验（~10ns）的内部子检查点无独立 tracepoint，但这是**设计意图**（性能考虑），入口/出口有 tracepoint，失败时完全可观测。

### 10.2 测试用例 TC-GAP-02: fastpath 可观测性设计验证

**步骤**：

1. 验证入口/出口 tracepoint 设计：

```bash
grep -rn "trace_airy_ipc_fastpath\|tracepoint.*fastpath\|airy_ipc_fastpath_entry\|airy_ipc_fastpath_exit" docs/AirymaxOS/ | head -10
```

**预期输出**：包含入口/出口 tracepoint 设计。

2. 验证 C-S9 内联校验的设计意图说明：

```bash
grep -rn "C-S9\|inline.*badge\|内联.*校验\|设计意图\|performance.*consider" docs/AirymaxOS/ | grep -i "fastpath\|badge\|10ns" | head -10
```

**预期输出**：包含 C-S9 内联校验的设计意图说明（性能考虑）。

3. 验证失败路径可观测：

```bash
grep -rn "badge.*fail\|capability.*denied\|AIRY_E_CAP\|trace.*deny" docs/AirymaxOS/ | head -10
```

**预期输出**：包含失败路径的 tracepoint/error 设计。

**通过标准**：入口/出口有 tracepoint + C-S9 设计意图已文档化 + 失败路径可观测。

**注**：GAP-02 为设计意图（非缺陷），此项测试仅验证设计文档完整性。

---

## 11. v3.0 深度残留修复验证

### 11.1 测试目标

v3.0 修复了 v2.9 声称已修复但实际未生效的 2 份文档 13 处残留，需独立验证。

### 11.2 测试用例 TC-V30-01: 05-syscall-semantic-mapping.md 完整验证

**步骤**：

1. 扫描全文旧编号：

```bash
grep -nE "#(5(1[2-7]|2[0-9]|3[0-9]|4[0-7])|6(0[0-9]|1[0-9]))\b" docs/AirymaxOS/30-interfaces/05-syscall-semantic-mapping.md | grep -i "airy_sys\|syscall" | head -10
```

**预期输出**：无匹配（0 个旧编号残留）。

2. 验证 L147 特定修复：

```bash
sed -n '147p' docs/AirymaxOS/30-interfaces/05-syscall-semantic-mapping.md
```

**预期输出**：包含 `#551 airy_sys_clt_notify(AIRY_CLT_WASM_LOAD_MODULE)`，无 `#614`。

3. 验证 L260-262 特定修复：

```bash
sed -n '258,264p' docs/AirymaxOS/30-interfaces/05-syscall-semantic-mapping.md
```

**预期输出**：包含 `#551/#551/#550` + op-dispatch 名称，无 `#613/#614/#615`。

**通过标准**：3 项全部匹配。

### 11.3 测试用例 TC-V30-02: 04-token-budget.md §8 完整验证

**步骤**：

1. 扫描 §8 旧编号：

```bash
sed -n '380,560p' docs/AirymaxOS/140-application-development/04-token-budget.md | grep -nE "5[0-9][0-9]|6[0-1][0-9]" | grep -i "task_set_budget\|task_get_budget\|task_resume\|task_pause" | head -10
```

**预期输出**：无匹配（0 个旧独立 syscall 残留）。

2. 验证 §8.2 函数原型：

```bash
sed -n '505,535p' docs/AirymaxOS/140-application-development/04-token-budget.md
```

**预期输出**：函数原型为 `airy_sys_sched_ctl(op, agent_id, arg)` 形式，无 `airy_sys_task_set_budget`。

3. 验证 §8.3 函数原型：

```bash
sed -n '530,555p' docs/AirymaxOS/140-application-development/04-token-budget.md
```

**预期输出**：函数原型为 `airy_sys_sched_ctl(op, agent_id, arg)` 形式。

4. 验证性能表引用：

```bash
sed -n '710,715p' docs/AirymaxOS/140-application-development/04-token-budget.md
```

**预期输出**：包含 `airy_sys_sched_ctl(SET_POLICY/GET_LATENCY)`，无旧独立 syscall。

**通过标准**：4 项全部匹配。

---

## 12. 整体一致性验证

### 12.1 测试目标

执行 v2.9/v3.0 的 7 维度一致性验证框架，确保整体方案一致。

### 12.2 测试用例 TC-OC-01: 7 维度一致性验证

| 维度 | 验证方法 | 通过标准 |
|------|---------|---------|
| 1. SSoT 内部一致性 | `07-syscall-registry.md` 内无矛盾编号 | 4 核心 + 20 预留，无旧模型残留 |
| 2. ABI 三方一致性 | `abi_check.py` 6/6 PASS | 退出码 0 |
| 3. 文档扫描一致性 | `grep -rnE` 旧编号扫描 | 0 个残留 |
| 4. op-dispatch 一致性 | SSoT §4 映射表与下游引用交叉验证 | 名称完全匹配 |
| 5. IRON-8 版本一致性 | `grep "0\.2\.8"` 扫描 | 0 个 v0.2.8 残留 |
| 6. codegen 契约一致性 | `syscall.xml` 与 SSoT 编号一致 | linux_base=548 + 4 syscall |
| 7. v3.0 残留修复一致性 | 2 份文档 13 处修复验证 | 全部已生效 |

**步骤**：依次执行 TC-014-01 到 TC-V30-02，记录每项结果。

**通过标准**：7 维度全部 PASS。

### 12.3 测试用例 TC-OC-02: 闭源文档一致性验证

**验证点**：两份闭源文档（工程标准规范 + 开发路线和进度）无旧编号残留。

**步骤**：

1. 扫描工程标准规范：

```bash
grep -n "512-535\|454-457\|453-456\|458-477" docs-closed/agent-linux/agent-linux基本工程标准规范.md
```

**预期输出**：无匹配（0 个旧编号残留）。

2. 扫描开发路线和进度：

```bash
grep -n "512-535\|454-457\|453-456\|458-477" docs-closed/agent-linux/agent-linux开发路线和进度.md
```

**预期输出**：无匹配（0 个旧编号残留）。

3. 验证 R-01 状态已更新：

```bash
grep -n "R-01\|syscall.xml" docs-closed/agent-linux/agent-linux基本工程标准规范.md | head -10
```

**预期输出**：R-01 标注为"已落地"（非"待落地"）。

**通过标准**：3 项全部匹配。

---

## 13. 测试结果汇总模板

### 13.1 测试结果记录表

| 测试用例 ID | 测试项 | 结果 | 证据 | 备注 |
|------------|--------|------|------|------|
| TC-014-01 | ABI 三方编号一致性 | ☐ PASS ☐ FAIL | | |
| TC-014-02 | 旧编号残留扫描（512-547, 600-619） | ☐ PASS ☐ FAIL | | |
| TC-014-03 | 454-457 编号残留扫描 | ☐ PASS ☐ FAIL | | |
| TC-014-04 | op-dispatch 映射表交叉验证 | ☐ PASS ☐ FAIL | | |
| TC-014-05 | v3.0 修复验证（05-syscall-semantic-mapping） | ☐ PASS ☐ FAIL | | |
| TC-014-06 | v3.0 修复验证（04-token-budget §8） | ☐ PASS ☐ FAIL | | |
| TC-016-01 | v0.2.8 版本号全量扫描 | ☐ PASS ☐ FAIL | | |
| TC-016-02 | 4 份目标文档版本号验证 | ☐ PASS ☐ FAIL | | |
| TC-017-01 | syscall.xml 契约源完整性 | ☐ PASS ☐ FAIL | | |
| TC-017-02 | syscall_gen.py 生成器可执行性 | ☐ PASS ☐ FAIL | | |
| TC-017-03 | Makefile 构建入口 | ☐ PASS ☐ FAIL | | |
| TC-017-04 | 生成输出验证 | ☐ PASS ☐ FAIL | | |
| TC-018-01 | abi_check.py 可执行性 | ☐ PASS ☐ FAIL | | |
| TC-018-02 | ABI 三方一致性检查（6/6 PASS） | ☐ PASS ☐ FAIL | | |
| TC-018-03 | ABI 基线快照验证 | ☐ PASS ☐ FAIL | | |
| TC-P1-01 | superv/ 同名文件识别 | ☐ PASS ☐ M1 待修复 | | |
| TC-P1-02 | airy_sys_ipc_register_ring 残留扫描 | ☐ PASS ☐ FAIL | | |
| TC-GAP-01 | 补丁追踪文档完整性 | ☐ PASS ☐ FAIL | | 非阻断 |
| TC-GAP-02 | fastpath 可观测性设计验证 | ☐ PASS ☐ FAIL | | 非阻断 |
| TC-V30-01 | 05-syscall-semantic-mapping 完整验证 | ☐ PASS ☐ FAIL | | |
| TC-V30-02 | 04-token-budget §8 完整验证 | ☐ PASS ☐ FAIL | | |
| TC-OC-01 | 7 维度一致性验证 | ☐ PASS ☐ FAIL | | |
| TC-OC-02 | 闭源文档一致性验证 | ☐ PASS ☐ FAIL | | |

### 13.2 测试统计

| 类别 | 总数 | PASS | FAIL | 待修复 |
|------|------|------|------|--------|
| P0 项 | 14 | | | |
| P1 项 | 2 | | | |
| GAP 项 | 2 | | | |
| v3.0 残留 | 2 | | | |
| 整体一致性 | 2 | | | |
| **合计** | **22** | | | |

---

## 14. 通过/失败判定标准

### 14.1 总体判定

- **全部 PASS**：v3.0 修复完整有效，方案一致性验证通过，可进入 M1 阶段
- **P0 项有 FAIL**：必须修复后重新测试，阻断 M1
- **P1 项有 FAIL**：允许记入 M1 修复清单，不阻断当前验证
- **GAP 项有 FAIL**：非阻断，记录为后续改进项

### 14.2 阻断项（必须 PASS）

| 测试用例 | 阻断原因 |
|---------|---------|
| TC-014-01 ~ TC-014-06 | P0-014 syscall 编号一致性是 ABI 稳定性基础 |
| TC-016-01 ~ TC-016-02 | P0-016 IRON-8 铁律违反 |
| TC-017-01 ~ TC-017-04 | P0-017 codegen 管道是接口契约基础 |
| TC-018-02 | P0-018 ABI 检查工具是 CI 强制执行基础 |
| TC-V30-01 ~ TC-V30-02 | v3.0 深度残留修复有效性 |
| TC-OC-01 | 7 维度整体一致性 |

### 14.3 非阻断项（允许延期）

| 测试用例 | 延期原因 |
|---------|---------|
| TC-P1-01 | superv/ 同名文件允许 M1 阶段修复 |
| TC-P1-02 | 命名一致性可在 M1 阶段补全 |
| TC-GAP-01 | 补丁迁移是长期工作 |
| TC-GAP-02 | fastpath 可观测性是设计意图 |

### 14.4 测试执行记录

- **执行人**：_______________
- **执行日期**：_______________
- **总体结果**：☐ 全部 PASS ☐ P0 PASS + P1 待修复 ☐ P0 有 FAIL（阻断）
- **签名**：_______________

---

## 附录 A: 快速验证脚本

以下脚本可一次性执行全部 P0 阻断项验证：

```bash
#!/bin/bash
# v3.0 P0 快速验证脚本
set -e
cd /home/spharx/SpharxWorks/airymaxhub

echo "=== TC-014-01: ABI 三方编号一致性 ==="
echo "[SSoT]"; grep -c "548\|549\|550\|551" docs/AirymaxOS/140-application-development/07-syscall-registry.md
echo "[unistd.h]"; grep -c "airy_sys" agent-linux/kernel/include/uapi/asm-generic/unistd.h
echo "[syscall_64.tbl]"; grep -c "airy_sys" agent-linux/kernel/arch/x86/entry/syscalls/syscall_64.tbl

echo "=== TC-014-02: 旧编号残留扫描 ==="
COUNT=$(grep -rnE "#(5(1[2-7]|2[0-9]|3[0-9]|4[0-7])|6(0[0-9]|1[0-9]))\b" docs/AirymaxOS/ | grep -i "airy_sys\|syscall" | wc -l)
echo "旧编号残留数: $COUNT (预期: 0)"

echo "=== TC-016-01: v0.2.8 残留扫描 ==="
COUNT=$(grep -rn "0\.2\.8" docs/AirymaxOS/ | wc -l)
echo "v0.2.8 残留数: $COUNT (预期: 0)"

echo "=== TC-018-02: ABI 检查工具 ==="
cd agent-linux/tools/abi-check && python3 abi_check.py 2>&1 | tail -10

echo "=== 验证完成 ==="
```

---

*本测试计划基于 v2.8 审查报告 + v2.9 修复报告 + v3.0 深度残留修复报告编制，覆盖全部 P0/P1 项，供手动验证执行。*
