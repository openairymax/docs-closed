Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# agent-linux v6.0 全量验证性审查报告
> **文档定位**：v1.1 基线锁定后的新一轮全量验证性审查，覆盖 v3.5 → v4.0 → v4.1 → v4.2 → v4.3 → v5.0 → v6.0 完整审查链\
> **文档版本**：v6.0\
> **最后更新**：2026-07-27\
> **上级文档**：[19-closure-report-v5.0.md](19-closure-report-v5.0.md)\
> **审查方法**：6 路并行子代理独立深度扫描 + 主代理 byte-level Read/Grep/RunCommand 验证\
> **验证标准**：发现新问题、确认 v5.0 闭环稳定性、识别子代理误报

---

## 1. 执行摘要

### 1.1 本轮审查范围

基于用户指令"所有文档锁定 v1.1；继续进行一次全量审查任务"，本轮为 v1.1 锁定后的验证性审查：

| 任务 | 内容 | 方法 |
|------|------|------|
| v5.0 闭环稳定性验证 | 确认 v5.0 的 143 修复点无回归 | 6 子代理 + 主代理 byte-level |
| 新问题发现 | 识别 v5.0 未覆盖的盲区 | 6 路并行深度扫描 |
| 子代理误报识别 | 区分真实问题与误报 | 主代理 RunCommand 验证 |

### 1.2 本轮发现汇总

| 严重性 | 数量 | 说明 |
|--------|------|------|
| A 类（实际缺陷） | 20 大类 | 主要集中在 codegen 漂移、文档版本号违规、子仓 README 残留 |
| B 类（改进建议） | 5 | 格式统一、风格一致性 |
| 误报 | 1 | N-3 错误码分层设计为合理设计 |

### 1.3 关键结论

**⚠️ 本轮发现 20 类 A 类新问题。v5.0 闭环声明过早。**

v5.0 闭环报告的"0 残留错误"结论基于过窄的 grep 验证模式，漏检了：
1. 子仓 README 中的 "6+2 set" 残留（grep 模式 `6+2 headers` 漏检 `6+2 set`）
2. 约 50+ 个文档仍使用 0.1.1 版本号（未纳入闭环验证范围）
3. codegen 生成器与已提交产物的漂移（未运行 `syscall_gen.py --check`）
4. CI 引用的 6 个工具脚本缺失（未验证 CI 步骤引用的文件存在性）
5. docs/AirymaxRT/ 旧文档目录未纳入审查范围

## 2. A 类问题详情（20 类）

### 2.1 #A-1: codegen 生成器与已提交 syscall.h 严重不一致（CI 必失败）

**严重性**：A 类（高）\
**子代理**：3 + 4\
**验证方法**：`python3 tools/codegen/syscall_gen.py --check`（exit code 1）

**问题**：已提交的 `syscall.h` 与生成器 `syscall_gen.py` 输出存在多处差异：

| 差异点 | 已提交文件（手工修改） | 生成器输出 |
|--------|----------------------|----------|
| include guard | `AIRY_SYSCALL_GEN_H` | `AIRY_SYSCALLS_H` |
| 内部索引宏 | `AIRY_SYS_IDX_*`（v4.0 修复命名空间冲突） | `AIRY_SYS_*`（未更新） |
| 注释块 | 5 行注释解释命名空间分离 | 仅 1 行简单注释 |
| 函数原型 | 跨 2 行 | 单行 |

**重定义风险**：生成器输出 `#define AIRY_SYS_CALL 0`，而 [SC] `syscalls.h:20` 定义 `#define AIRY_SYS_CALL 548`。若重新生成并提交，两文件同时被包含会重定义冲突。

**违反规则**：
- `06-codegen-pipeline.md:22-23` 目标 2 "CI diff 检查：`make codegen` 输出与仓库已提交文件 diff 必须为空"
- `06-codegen-pipeline.md:35` "禁止手工修改生成代码"

**修复方案**：更新 `syscall_gen.py` 使其输出与已提交 `syscall.h`（含 `AIRY_SYS_IDX_*` 前缀、`AIRY_SYSCALL_GEN_H` guard）逐字节一致。

### 2.2 #A-2: 04-ipc-versioning.md 消息头布局未与 SSoT Layout C v4 对齐

**严重性**：A 类（高）\
**子代理**：2\
**验证方法**：Read L90-150

**问题**：`160-compatibility/04-ipc-versioning.md` 仍引用旧版 Layout C v1 布局：

| 位置 | 错误内容 | SSoT 正确内容 |
|------|---------|-------------|
| L97 | `reserved[84]` | `reserved[72]` |
| L98 | 字段顺序缺 `capability_badge` 与 `crc32` | 应含 11 字段 |
| L116 | "共 9 字段" | 应为 11 字段 |
| L136 | `reserved[84]`（offset 44, 84 bytes） | `reserved[72]`（offset 56, 72 bytes） |
| L275-277 | 兼容矩阵 reserved 拆分为 84B | 应为 72B |

**SSoT 权威源**：`02-ipc-protocol.md:96, 111, 179`、`120-cross-project-code-sharing.md:424` 均定义 `reserved[72]` @ offset 56，含 `capability_badge` @ offset 40 + `crc32` @ offset 52。

### 2.3 #A-3: 04-ipc-versioning.md 协议基线版本号自相矛盾

**严重性**：A 类（中）\
**子代理**：2\
**验证方法**：Read L7, L356

**问题**：
- L7："7 个 opcode 自 **v1.1** 起稳定"
- L356："7 个操作码自 **v1.0.1** 起保持稳定"

文档版本号 `v1.0.1` 与协议基线 `v1.1` 是不同概念，此处指协议基线，应统一为 `v1.1`。

### 2.4 #A-4: docs/AirymaxRT/10-architecture/06-iron9-shared-model.md 整篇文档过时

**严重性**：A 类（高）\
**子代理**：5\
**验证方法**：Grep + Read

**问题**：该文档（与 docs/AirymaxOS/ 同名文件不同步）存在多处严重过时：

| 位置 | 错误内容 | 正确内容 |
|------|---------|---------|
| L56 | `kernel/include/airymax/` | `kernel/include/uapi/linux/airymax/` |
| L67 | "LSM 钩子 **252** ID 枚举" | 250 ID |
| L69 | "SCHED_EXT 调度类编号" | 不使用 sched_ext |
| L71 | "12 核心 + 12 预留 = 24 槽位" | 4 核心 + 20 预留 |
| L162-172 | §3.4 SCHED_EXT 调度类编号整节 | 应删除 |
| L175-179 | `MAC_MAX_AGENTS` | `AIRY_CAP_MAX_AGENTS` |
| L206 | "LSM 钩子数量：**252** 个" | 250 个 |
| L230 | "error.h 尚未创建" | 已存在 |

**建议**：整篇重写或删除，对齐 docs/AirymaxOS/10-architecture/06-iron9-shared-model.md。

### 2.5 #A-5: 约 50+ 个文档仍使用 0.1.1 版本号（违反 IRON-8）

**严重性**：A 类（高）\
**子代理**：2\
**验证方法**：`grep -rn "^> \*\*文档版本\*\*：0\.1\.1"`（50 匹配）

**问题**：按 IRON-8 铁律，所有文档版本号应统一为 v1.0.1，但以下目录的 50+ 文档仍为 0.1.1：

| 目录 | 数量 |
|------|------|
| 50-engineering-standards/ | 18 |
| 130-roadmap/ | 6 |
| 180-i18n/ | 5 |
| 150-cloudnative/ | 5 |
| 10-architecture/ | 4 |
| 160-compatibility/ | 3 |
| 170-performance/ | 4 |
| 30-interfaces/ | 2 |
| 80-testing/ | 2 |
| 120-development-process/ | 2 |
| 60-driver-model/ | 2 |
| 90-observability/ | 2 |
| 110-security/ | 1 |
| 140-application-development/ | 1 |

### 2.6 #A-6: 4 个文档使用非标准 "1.0.1-fix" 版本号（违反 IRON-8）

**严重性**：A 类（中）\
**子代理**：2\
**验证方法**：`grep -rn "1\.0\.1-fix"`

**问题**：以下文档的"文档版本"字段使用非标准 `1.0.1-fix` 或 `v1.0.1-fix`：

| 文件 | 行号 |
|------|------|
| `170-performance/02-memory-performance.md` | L5 |
| `20-modules/04-memory.md` | L6 |
| `20-modules/05-cognition.md` | L6 |
| `40-dataflows/02-memory-flow.md` | L5 |

`1.0.1-fix` 既非 `v1.0.1` 也非历史版本号，属非标准中间过渡版本，违反 IRON-8。

### 2.7 #A-7: CI 引用 6 个不存在的工具脚本

**严重性**：A 类（高）\
**子代理**：3\
**验证方法**：Glob + Read

**问题**：CI 工作流引用了 6 个不存在的工具脚本，对应 CI 步骤会直接失败：

| 缺失脚本 | 引用位置 |
|----------|----------|
| `tools/kunit-tap-diff.py` | `ci-kernel.yml:94` |
| `tools/parse-tap.py` | `ci-kernel.yml:99` |
| `tools/create-agentrt-mirror-pr.py` | `sc-dual-ci.yml:80` |
| `tools/await-agentrt-ci.py` | `sc-dual-ci.yml:89` |
| `tools/aggregate-subrepo-ci.py` | `mgmt-orchestrator.yml:98` |
| `tools/check-copyright.py` | `mgmt-orchestrator.yml:113` |

### 2.8 #A-8: CI 未调用 abi_check.py（6/6 PASS 未强制）

**严重性**：A 类（高）\
**子代理**：3\
**验证方法**：`grep -rn 'abi_check\|abi-check' .github/workflows/`（0 匹配）

**问题**：`tools/abi-check/abi_check.py:562-584` 注册 6 项检查，`--check` 输出 "ABI CHECK: PASS (6/6 checks)"，但**没有任何 CI 工作流调用 abi_check.py**。OS-IRON-001（用户空间 ABI 永不破坏）的 6/6 强制能力存在但 CI 未触发。

### 2.9 #A-9: CI 未调用 codegen check（漂移未被拦截）

**严重性**：A 类（高）\
**子代理**：3\
**验证方法**：`grep -rn 'codegen\|syscall_gen' .github/workflows/`（0 匹配）

**问题**：CI 未运行 codegen check，导致 #A-1 的 codegen 漂移未被 CI 拦截。

### 2.10 #A-10: checkpatch.pl 路径错误 + ci-kernel.yml make 命令缺 working-directory

**严重性**：A 类（中）\
**子代理**：3\
**验证方法**：Read ci-kernel.yml

**问题**：
1. `ci-kernel.yml:80` 调用 `scripts/checkpatch.pl`，但实际位置是 `kernel/scripts/checkpatch.pl`
2. `ci-kernel.yml:62-63` 在仓库根运行 `make defconfig`，但内核 Makefile 在 `kernel/` 子目录，CI 缺 `working-directory: kernel`

### 2.11 #A-11: syscall.xml 仍含 AIRY_CAP_INVOKE 字段

**严重性**：A 类（中）\
**子代理**：4\
**验证方法**：Read syscall.xml L45

**问题**：`syscall.xml:45` 仍包含 `<capability_required>AIRY_CAP_INVOKE</capability_required>`，但 `06-codegen-pipeline.md` P0-E2/P0-19 修复说明声称已移除（虚构 capability，cap 作为参数传入而非前置条件）。

### 2.12 #A-12: syscall_64.tbl Airymax 段非 codegen 生成

**严重性**：A 类（中）\
**子代理**：4\
**验证方法**：Read syscall_64.tbl L378-388

**问题**：`syscall_64.tbl:378-388` Airymax 段含手写中文注释，但 `06-codegen-pipeline.md:173` 声明 `syscall_gen.py` 应生成 syscall 表条目。实际 `syscall_gen.py` 仅生成 C 头文件，无生成 `syscall_64.tbl` 的逻辑。

### 2.13 #A-13: syscalls.h 未标注 "v1.1 唯一基线，v4.3 锁定"

**严重性**：A 类（低）\
**子代理**：4\
**验证方法**：Read syscalls.h 全文

**问题**：`syscalls.h` 全文 54 行，仅 L8 提到 "v1.0.1 起始编号统一为 548"，无 v1.1 或 v4.3 的基线标注。v1.1 IPC 协议基线锁定声明在 [SC] 头文件层未落地。

### 2.14 #A-14: devtools test_error.c 错误码值与权威源严重不一致

**严重性**：A 类（中）\
**子代理**：5\
**验证方法**：Read test_error.c L51-54

**问题**：`devtools/tests/unit/commons/unit/test_error.c` 断言使用已废弃的旧错误码值：

| 测试断言 | 权威源 error.h | 状态 |
|----------|---------------|------|
| L51: `AIRY_ERR_UNKNOWN == -1` | L53: `AIRY_ERR_UNKNOWN (-99)` | ❌ |
| L52: `AIRY_ERR_INVALID_PARAM == -2` | L139: `AIRY_ERR_INVALID_PARAM (-36)` | ❌ |
| L54: `AIRY_ERR_OUT_OF_MEMORY == -4` | L145: `AIRY_ERR_OUT_OF_MEMORY (-59)` | ❌ |

测试还使用 `airy_strerror`/`airy_error_t`/`AIRY_ERROR_RETURN` 等已不存在的符号（权威源为 `airy_err_str`/`airy_err_t`/`AIRY_ERROR`）。CMakeLists.txt 已禁用但代码残留仍违规。

### 2.15 #A-15: 子仓 README 6 处 "6+2 set" 违规残留

**严重性**：A 类（中）\
**子代理**：5\
**验证方法**：`grep -rn "6+2 set" --include="*.md"`

**问题**：v4.2/v5.0 闭环报告的 grep 模式 `6+2 headers` 漏检了 `6+2 set`，导致 6 处违规残留：

| 文件 | 行号 |
|------|------|
| `agent-linux/security/README.md` | L64 |
| `agent-linux/security/.github/README.md` | L30 |
| `agent-linux/cognition/README.md` | L67 |
| `agent-linux/cognition/.github/README.md` | L30 |
| `agent-linux/memory/README.md` | L65 |
| `agent-linux/memory/.github/README.md` | L30 |

### 2.16 #A-16: 子仓 README 6 处 kernel/include/airymax/ 错误路径

**严重性**：A 类（中）\
**子代理**：5\
**验证方法**：`grep -rn "kernel/include/airymax/" --include="*.md"`

**问题**：以下子仓 README 错误地把 [SC] header 物理宿主说成 `kernel/include/airymax/`，实际应为 `kernel/include/uapi/linux/airymax/`：

| 文件 | 行号 |
|------|------|
| `agent-linux/security/README.md` | L32 |
| `agent-linux/security/.github/README.md` | L38 |
| `agent-linux/cognition/README.md` | L34 |
| `agent-linux/cognition/.github/README.md` | L40 |
| `agent-linux/memory/README.md` | L33 |
| `agent-linux/memory/.github/README.md` | L38 |

### 2.17 #A-17: agent-linux README 多处 sched_ext 活动使用

**严重性**：A 类（中）\
**子代理**：5\
**验证方法**：Grep

**问题**：`agent-linux/README.md` 和 `README_zh.md` 中有 8 处 sched_ext 活动使用（违反"不使用 sched_ext"原则）：

| 文件 | 行号 | 内容 |
|------|------|------|
| `README.md` | L50, L87, L111, L122 | "sched_ext sub-scheduler" 等 |
| `README_zh.md` | L50, L87, L146, L157 | 同上中文版 |

### 2.18 #A-18: cognition/services README sched_ext 活动使用

**严重性**：A 类（中）\
**子代理**：5\
**验证方法**：Grep

**问题**：

| 文件 | 行号 |
|------|------|
| `cognition/README.md` | L87 |
| `cognition/README_zh.md` | L49 |
| `services/README.md` | L80 |
| `services/README_zh.md` | L49 |

### 2.19 #A-19: 06-io-uring-hardening.md 虚构 AIRY_VERDICT_PAUSE/TERMINATE

**严重性**：A 类（中）\
**子代理**：5\
**验证方法**：Read L381

**问题**：`docs/AirymaxOS/110-security/06-io-uring-hardening.md:381` 使用虚构的 `AIRY_VERDICT_PAUSE` 与 `AIRY_VERDICT_TERMINATE`。权威源 `security_types.h:76-79` 仅定义 4 值枚举 `ALLOW/DENY/AUDIT/COMPLAIN`，不存在 PAUSE/TERMINATE。

### 2.20 #A-20: 07-system.md schedTac 驼峰式不一致

**严重性**：A 类（低）\
**子代理**：5\
**验证方法**：Read L402

**问题**：`docs/AirymaxOS/20-modules/07-system.md:402` 使用 "schedTac"（驼峰式），与全仓其他位置的 "sched_tac"（下划线式）不一致。

## 3. B 类问题详情（5 类）

### 3.1 #B-1: commons 侧 10/11 文件末尾缺换行符

**严重性**：B 类（低）\
**子代理**：1\
**验证方法**：`od -c` 字节级验证

**问题**：commons 侧 10 个 [SC] 头文件末尾缺换行符（ipc.h 除外）。kernel 侧已统一有换行符。

### 3.2 #B-2: 版本协商机制表述用词不统一

**严重性**：B 类（低）\
**子代理**：2

**问题**：
- `04-ipc-versioning.md:7`：v2.0+ 演进预留
- `02-ipc-protocol.md:7, 21`：v2.0+ 预留

建议统一为 "v2.0+ 预留"。

### 3.3 #B-3: corekern/ 5 个子目录 Kbuild 使用非聚合模式

**严重性**：B 类（低）\
**子代理**：6

**问题**：`corekern/{ipc,sched,bpf,taskflow,memory}/Kbuild` 使用 `obj-y += a.o b.o ...` 直接列文件，而非 `obj-y += module.o` + `module-y :=` 聚合模式，与 `kernel/ipc/`、`kernel/log/` 风格不一致。

### 3.4 #B-4: syscall_64.tbl L387 格式与其他三行不一致

**严重性**：B 类（低）\
**子代理**：4

**问题**：L384-386 使用 2 个 tab 对齐，L387 仅 1 个 tab。

### 3.5 #B-5: v5.0 closure report L155 UAF 警告路径描述误导

**严重性**：B 类（低）\
**子代理**：6

**问题**：v5.0 closure report L155 声称 "security/airy/airy_lsm/airy_lsm.c: UAF 警告 | ✅ L7-24"，但该路径是已被删除的旧 `airy_ind` 模块路径，当前生产文件 `kernel/security/airy/airy_lsm.c` 的 L7-24 是版权信息和 #include，无 UAF 警告。

## 4. 子代理误报确认（1 项）

### 4.1 误报 #1: airy_ipc_fastpath.c -EAGAIN vs -AIRY_EIPC_FROZEN

**子代理 6 报告**：`corekern/ipc/airy_ipc_fastpath.c:28` 使用 `-EAGAIN`（-35），而 `airy_ipc_freeze.c:88` 使用 `-AIRY_EIPC_FROZEN`（-53），两个 fastpath 路径对同一 frozen 状态返回不同错误码。

**主代理验证**：
- `airy_ipc_fastpath_send`（corekern/ipc/）是 IPC 传输层 hot path，使用 POSIX `-EAGAIN` 表示"ring 暂时不可用，调用者可重试"
- `airy_ipc_fastpath_check`（security/airy/）是安全检查层，使用 `-AIRY_EIPC_FROZEN`（-53）表示"ring 被冻结（A-ULS 控制）"
- `airy_cap_check.c:49` 也使用 `-AIRY_EIPC_FROZEN`，这是 capability 检查层

**结论**：**误报**。两者是不同层级的检查，使用不同错误码是合理的分层设计：
- 传输层（corekern）：POSIX 错误码，调用者可重试
- 安全层（security/airy）：Airy 专属错误码，表示策略性冻结

## 5. v5.0 闭环稳定性验证

### 5.1 v5.0 修复点稳定性（143 点全部无回归）

| v5.0 修复项 | 本轮验证 | 状态 |
|------------|---------|------|
| IPC v1.0/v1.1 双轨制 → v1.1 唯一基线锁定 | 6 子代理 + 主代理 grep | ✅ 无回归 |
| 04-ipc-versioning.md v1.0 残留引用清理 | Read L90-150 | ✅ 无回归（但发现新问题 #A-2） |
| [SC] 10 头文件字节级一致性 | 子代理 1 逐行对比 | ✅ 无回归 |
| 错误码空间分离（AIRY_ERR_* vs AIRY_EIPC_*） | 子代理 5 grep | ✅ 无回归 |
| Codegen SSoT 链四方一致性 | 子代理 4 验证 | ✅ 编号一致（但发现生成器漂移 #A-1） |
| 内核代码完整性 | 子代理 6 验证 | ✅ 无回归 |
| magic 值统一 | 子代理 5 grep | ✅ 无回归 |

### 5.2 v5.0 闭环声明准确性评估

| v5.0 声明 | 实际情况 | 评估 |
|----------|---------|------|
| "0 残留错误" | 发现 20 类 A 类新问题 | ❌ 过早闭环 |
| "v1.1 基线锁定完成" | 主协议文档已锁定，但 syscalls.h 未标注 | ⚠️ 部分完成 |
| "M0 设计阶段就绪" | 存在 codegen 漂移、CI 缺失等阻塞项 | ❌ 未就绪 |

**根因分析**：v5.0 闭环验证存在 3 个盲区：
1. **grep 模式过窄**：`6+2 headers` 漏检 `6+2 set`
2. **验证范围不全**：子仓 README、docs/AirymaxRT/、CI 工作流引用文件存在性未纳入
3. **未运行可执行验证**：未运行 `syscall_gen.py --check`、`abi_check.py --check`

## 6. 整体成熟度评估

| 维度 | v5.0 | v6.0 | 变化 | 说明 |
|------|------|------|------|------|
| 三大设计支柱 | 88 | 85 | -3 | docs/AirymaxRT 旧文档过时暴露 |
| IRON 工程铁律执行 | 94 | 78 | -16 | 50+ 文档 0.1.1 版本号 + 1.0.1-fix 违规 |
| 内核哲学 | 86 | 86 | 0 | 稳定 |
| ALK 分支管理 | 82 | 82 | 0 | 稳定 |
| 8 子仓边界与依赖 | 82 | 75 | -7 | 子仓 README 违规残留 |
| 项目阶段明确性 | 88 | 80 | -8 | codegen 漂移 + CI 缺失 |
| CI/测试基础设施 | 82 | 65 | -17 | 6 个工具脚本缺失 + abi_check 未集成 |
| **加权总分** | **88（B+）** | **78（B+）** | **-10** | |

v6.0 下降 10 分原因：
- v5.0 闭环声明基于过窄验证，本轮发现 20 类新问题
- CI 基础设施缺失严重（6 个脚本缺失 + 2 个检查未集成）
- 文档版本号违规系统性（50+ 文档）

## 7. 修复优先级建议

### 7.1 P0 阻塞项（必须在 M0 闭环前修复）

| # | 问题 | 修复方案 | 工作量 |
|---|------|---------|--------|
| A-1 | codegen 生成器漂移 | 更新 syscall_gen.py 输出 AIRY_SYS_IDX_* + AIRY_SYSCALL_GEN_H | 中 |
| A-7 | CI 引用 6 个缺失脚本 | 创建脚本或移除 CI 步骤 | 中 |
| A-8 | CI 未调用 abi_check.py | 在 ci-kernel.yml 添加 abi_check 步骤 | 小 |
| A-9 | CI 未调用 codegen check | 在 ci-kernel.yml 添加 codegen --check 步骤 | 小 |
| A-10 | checkpatch.pl 路径错误 | 修正为 kernel/scripts/checkpatch.pl + 添加 working-directory | 小 |

### 7.2 P1 重要项（M0 阶段修复）

| # | 问题 | 修复方案 |
|---|------|---------|
| A-2 | 04-ipc-versioning.md 布局过期 | 更新为 Layout C v4（reserved[72] + capability_badge + crc32） |
| A-4 | docs/AirymaxRT 旧文档过时 | 整篇重写或删除 |
| A-5 | 50+ 文档 0.1.1 版本号 | 批量升级为 v1.0.1 |
| A-6 | 4 文档 1.0.1-fix 版本号 | 改为 v1.0.1 |
| A-11 | syscall.xml AIRY_CAP_INVOKE | 移除该字段 |
| A-14 | test_error.c 错误码过时 | 更新断言或删除文件 |
| A-15 | 子仓 README 6+2 set | 改为 "10 [SC] core headers" |
| A-16 | 子仓 README 错误路径 | 改为 kernel/include/uapi/linux/airymax/ |
| A-17 | README sched_ext 活动使用 | 改为"不使用 sched_ext" |
| A-18 | cognition/services README sched_ext | 同上 |

### 7.3 P2 改进项（M1 阶段修复）

| # | 问题 | 修复方案 |
|---|------|---------|
| A-3 | 04-ipc-versioning.md 版本号矛盾 | 统一为 v1.1 |
| A-12 | syscall_64.tbl 非codegen生成 | 扩展 syscall_gen.py 生成 tbl |
| A-13 | syscalls.h 未标注 v1.1 | 添加注释 |
| A-19 | 虚构 AIRY_VERDICT_PAUSE/TERMINATE | 改为 AIRY_VERDICT_COMPLAIN |
| A-20 | schedTac 驼峰式 | 改为 sched_tac |
| B-1~B-5 | 格式/风格问题 | 按建议修复 |

## 8. 验证矩阵

### 8.1 子代理发现 vs 主代理验证

| 子代理 | 发现总数 | 主代理确认 | 误报 |
|--------|---------|----------|------|
| 1（[SC] 头文件） | 1 | 1（B-1） | 0 |
| 2（设计文档） | 5 | 5（A-2~A-6, B-2） | 0 |
| 3（CI/构建） | 6 | 6（A-1, A-7~A-10） | 0 |
| 4（Codegen 链） | 5 | 5（A-1, A-11~A-13, B-4） | 0 |
| 5（跨文件引用） | 19 | 19（A-4, A-14~A-20） | 0 |
| 6（内核代码） | 3 | 2（B-3, B-5） | 1（N-3 误报） |
| **总计** | **39** | **38** | **1** |

### 8.2 关键值验证（全部通过）

| 验证项 | 预期值 | 实际值 | 状态 |
|--------|--------|--------|------|
| AIRY_IPC_MAGIC | 0x41524531 | 0x41524531u | ✅ |
| AIRY_TASK_MAGIC | 0x41475453 | 0x41475453u | ✅ |
| AIRY_IPC_HDR_SIZE | 128 | 128 | ✅ |
| AIRY_EIPC_FROZEN | -53 | -53（error.h:61） | ✅ |
| AIRY_EIPC_FLAGS | -46 | -46（error.h:54） | ✅ |
| AIRY_ECAP_FROZEN | -82 | -82（error.h:80） | ✅ |
| Syscall 548-551 | 548-551 | 548-551（syscalls.h:20-23） | ✅ |
| CI 矩阵配置数 | 31 | 31（ci-kernel.yml:22） | ✅ |
| [SC] 头文件数 | 10 | 10（sc-dual-ci.yml:34） | ✅ |
| 子模块数 | 8 | 8（mgmt-orchestrator.yml:32） | ✅ |

## 9. 审查链完整文件清单

| 阶段 | 文件 | 描述 |
|------|------|------|
| v3.5 | 00-13 | 初始系统性审查 + 修复实施 |
| v4.0 | 14-systematic-reverification-v4.0.md | 系统性终极复核 |
| v4.1 | 15-closure-report-v4.1.md | v4.0 修复闭环确认 |
| v4.2 | 16-closure-report-v4.2.md | 第二轮审查闭环确认 |
| v4.3 | 17-closure-report-v4.3.md | AIRY_ERR_* 值碰撞修复 + 闭环 |
| v4.3 | 18-migration-plan-v4.3.md | 6 项待决策事项迁移计划 |
| v5.0 | 19-closure-report-v5.0.md | v1.1 基线锁定 + 闭环声明（过早） |
| v6.0 | 20-closure-report-v6.0.md（本报告） | 验证性审查，发现 v5.0 盲区 |

## 10. 最终结论

### 10.1 闭环状态

**⚠️ v5.0 闭环声明过早。本轮发现 20 类 A 类新问题。**

v5.0 的"0 残留错误"结论基于过窄的验证模式，漏检了：
- 子仓 README 中的 "6+2 set" 残留
- 50+ 文档的 0.1.1 版本号违规
- codegen 生成器漂移
- CI 引用的 6 个缺失脚本
- docs/AirymaxRT/ 旧文档未纳入审查

### 10.2 成熟度评估

**v6.0 评分：78/100（B+）**（较 v5.0 的 88 分下降 10 分）

下降原因不是回归，而是 v5.0 未覆盖的盲区被本轮发现。这反映了验证性审查的价值：每一轮审查都会暴露前一轮的盲区。

### 10.3 M0 设计阶段就绪度

**❌ M0 设计阶段未就绪。**

阻塞项：
1. codegen 生成器漂移（A-1）会导致 CI 失败
2. CI 引用 6 个缺失脚本（A-7）会导致 CI 失败
3. CI 未集成 abi_check 和 codegen check（A-8, A-9）
4. 50+ 文档版本号违规（A-5, A-6）违反 IRON-8

### 10.4 建议

1. **立即修复 P0 阻塞项**（A-1, A-7~A-10）：使 CI 可运行
2. **批量修复 P1 重要项**：文档版本号统一、子仓 README 清理
3. **扩展闭环验证模式**：
   - 运行 `syscall_gen.py --check` 和 `abi_check.py --check`
   - 验证 CI 步骤引用的文件存在性
   - 将子仓 README 和 docs/AirymaxRT/ 纳入审查范围
4. **v7.0 审查**：修复完成后进行新一轮验证性审查

---

*v6.0 全量验证性审查报告完毕。v5.0 闭环声明过早，本轮发现 20 类 A 类新问题，建议修复 P0 阻塞项后进入 v7.0 审查。*
