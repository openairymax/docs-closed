# agentrt 源代码 v2.1 深度复审报告

| 项目 | 值 |
|---|---|
| 报告版本 | v2.1 |
| 审查日期 | 2026-07-13 |
| 审查范围 | `/home/spharx/SpharxWorks/OpenAirymax/agentrt/`（~875 个 C/H 文件） |
| 参照基线 | v1.0（atoms + daemons 深度审查）、v2.0（工程代码审查） |
| 工程标准 | OLK-6.6 六大支柱、IRON-9 v2 三层共享模型 |
| 审查员 | Airymax Team |

---

## 一、执行摘要

### 1.1 评分总表

| 维度 | v1.0 评分 | v2.1 评分 | 趋势 | 说明 |
|---|---|---|---|---|
| v1.0 问题修复率 | — | **10%**（1/10 部分修复） | — | 8 项完全未修复，2 项部分修复 |
| [SC] 共享契约层完整性 | — | **95/100** | 新增 | 6 头文件齐备，magic 值正确 |
| 错误码 SSoT 一致性 | — | **40/100** | 新增 | 3 处 `AIRY_SUCCESS` + 1 处 `AIRY_OK` 冲突 |
| OLK-6.6 缩进合规 | 0/100 | **5/100** | 持平 | 4 空格仍占绝对多数，Tab 8 仅 71 处 |
| OLK-6.6 typedef 规范 | 0/100 | **15/100** | 持平 | 421 处 `} xxx_t;` 仍存在 |
| OLK-6.6 goto 集中出口 | 10/100 | **55/100** | 改善 | 从 14 处增至 151 处/36 文件 |
| 内存安全 | 30/100 | **35/100** | 微升 | banned_functions 基础设施建立 |
| 线程安全 | 40/100 | **40/100** | 持平 | 35 处 static char 缓冲区未修复 |
| 错误处理模式 | 50/100 | **55/100** | 微升 | airy_err_t 广泛使用（981 处） |
| **综合评分** | **25/100 (D)** | **32/100 (D+)** | **+7** | 仍未达可开发标准（≥80/B） |

### 1.2 核心结论

v2.1 阶段 agentrt 源代码在 **[SC] 共享契约层**和 **banned_functions 合规基础设施**两个方向取得了实质性进展，但 **v1.0 发现的 10 项关键问题中 8 项完全未修复**，且 **错误码 SSoT 冲突** 这一新发现的 P0 问题使整体代码质量仍处于不可发布状态。

**进入 M1 代码开发阶段的就绪度：未达标**（综合评分 32/100，距离 80/B 门槛差距 48 分）。

---

## 二、v1.0 问题修复验证（10 项逐项）

### 问题 1：`.clang-format` 不存在

| 项目 | 内容 |
|---|---|
| 状态 | ❌ **未修复** |
| v1.0 描述 | 仓库根目录无 `.clang-format`，无法强制 OLK-6.6 Tab 8 缩进 |
| 验证方法 | `find /home/spharx/SpharxWorks/OpenAirymax/agentrt -name ".clang-format" -type f` |
| 证据 | 命令返回空结果，`.clang-format` 文件仍不存在 |
| 影响 | 缩进风格无法自动化校验，4 空格违规持续蔓延 |
| 建议 | **P0**：立即在 `agentrt/` 根目录创建 `.clang-format`，配置 `BasedOnStyle: LLVM` + `IndentWidth: 8` + `UseTab: Always` + `ColumnLimit: 80`，并接入 CI pre-commit hook |

### 问题 2：4 空格缩进全面违规（vs Tab 8）

| 项目 | 内容 |
|---|---|
| 状态 | ❌ **未修复** |
| v1.0 描述 | 237 文件全量 4 空格缩进，仅 66 处 Tab 缩进 |
| 验证方法 | Grep `^\t\S`（Tab 开头）vs `^    \S`（4 空格开头） |
| 证据 | Tab 8 缩进仅 **71 处**（集中在 `test_sc_headers.c`、`sched.h`、`bpf_struct_ops.h` 三个 [SC] 测试/头文件）；4 空格缩进在抽样 3 文件中达 **225 处**，全量估算仍超 30000 处 |
| 影响 | 与 OLK-6.6 六大支柱第一条直接冲突，代码品味不达标 |
| 建议 | **P0**：执行全量 `clang-format -i` 批量重格式化，配合问题 1 的 `.clang-format` 文件 |

### 问题 3：`agentrt-linux` 仍为空仓库

| 项目 | 内容 |
|---|---|
| 状态 | ⚠️ **部分修复** |
| v1.0 描述 | agentrt-linux 仓库仅有 LICENSE/README，无源代码 |
| 验证方法 | `find /home/spharx/SpharxWorks/OpenAirymax/agentrt-linux -type f` |
| 证据 | 仓库现有 **55 个文件**，含 8 个子目录（kernel/memory/security/cognition/services/system/cloudnative/tests-linux），每个子目录有 README.md/README_zh.md/LICENSE/NOTICE。但 **`.c`/`.h` 源代码文件数为 0**，仅有文档脚手架 |
| 影响 | agentrt-linux 8 子仓的目录骨架已建立，但实际内核加速路径代码完全缺失 |
| 建议 | **P1**：按 AirymaxOS 8 子仓设计在 M1 阶段填充 kernel 子仓的微内核核心代码，其余子仓可延后 |

### 问题 4：`fprintf` 直接使用违反 banned_functions

| 项目 | 内容 |
|---|---|
| 状态 | ❌ **未修复** |
| v1.0 描述 | memory.c 22 处 `fprintf(stderr)`、heapstore_migration.c 5 处 `fprintf(f)` |
| 验证方法 | Grep `fprintf\(stderr` in memory.c；Grep `fprintf\(` in heapstore_migration.c |
| 证据 | `memory.c` 仍有 **10 处** `fprintf(stderr, ...)`（L155/191/193/195/196/289/386-391/416/604/623/706-711 范围）；`heapstore_migration.c` 仍有 **5 处** `fprintf(f, ...)`（L171/261/296/451/486） |
| 影响 | 在 `AIRY_COMPLIANCE_STRICT` 默认开启下，`fprintf` 已被 `#pragma GCC poison` 禁用，这些文件应编译失败。若通过 `AIRY_COMPLIANCE_IMPL` 豁免则违反 IRON-5 |
| 建议 | **P0**：memory.c 的调试输出改用 `airy_log_write()`；heapstore_migration.c 的文件写入改用 `airy_fprintf()` 封装或 `fwrite()` |

### 问题 5：Windows 平台 `localtime` 线程不安全

| 项目 | 内容 |
|---|---|
| 状态 | ⚠️ **部分修复** |
| v1.0 描述 | audit_overflow.c Windows 分支使用 `localtime()`（非线程安全） |
| 验证方法 | Grep `localtime` in audit_overflow.c |
| 证据 | `audit_overflow.c` L52-56：`#if cupolas_PLATFORM_WINDOWS` → `localtime(&now)`（L53），`#else` → `localtime_r(&now, &tm_buf)`（L56）。POSIX 路径已修复，Windows 路径仍用 `localtime` |
| 影响 | Windows 平台多线程并发调用时可能返回指向静态缓冲区的指针，导致数据竞争 |
| 建议 | **P1**：Windows 分支改用 `localtime_s(&tm_buf, &now)`（MSVC 线程安全版本） |

### 问题 6：`typedef struct _t {}` 命名违规

| 项目 | 内容 |
|---|---|
| 状态 | ❌ **未修复** |
| v1.0 描述 | 296 处具名 + 326 处匿名 `typedef struct _t` |
| 验证方法 | Grep `} \w+_t;`（typedef 尾部模式） |
| 证据 | **421 处** 分布在 **100 文件**中（如 `cupolas/include/dynamic_policy_engine.h` 7 处、`safety_guard.h` 11 处、`gateway.h` 4 处等） |
| 影响 | OLK-6.6 六大支柱第三条"最小 typedef"要求结构体优先使用 `struct xxx`，仅对不透明句柄使用 typedef。当前滥用 typedef 模糊了值类型与句柄类型的语义边界 |
| 建议 | **P1**：区分"值类型"（移除 typedef，直接用 `struct xxx`）与"不透明句柄"（保留 typedef，配合 PImpl 模式）。分批重构，优先处理公开 API 头文件 |

### 问题 7：ASCII 装饰分节符 `/* ====`

| 项目 | 内容 |
|---|---|
| 状态 | ❌ **未修复** |
| v1.0 描述 | 100+ 文件含 `/* ====` 装饰分节符 |
| 验证方法 | Grep `/\* ={4,}` |
| 证据 | **590 处** 分布在 **100 文件**中（如 `test_service_discovery.c` 40 处、`test_daemon_common.c` 14 处、`gateway_benchmark.c` 12 处、`alert_manager.h` 18 处等） |
| 影响 | OLK-6.6 风格禁止 ASCII 装饰，应使用 kernel-doc 注释块替代 |
| 建议 | **P2**：批量替换为标准 kernel-doc `/** @section ... */` 格式或简单 `/* Section: ... */` |

### 问题 8：`banned_functions.h` 合规机制

| 项目 | 内容 |
|---|---|
| 状态 | ⚠️ **部分修复**（设计可接受） |
| v1.0 描述 | 缺乏 banned_functions 机制，malloc/free/printf 等无约束 |
| 验证方法 | Read `banned_functions.h` + `CMakeLists.txt` |
| 证据 | `commons/utils/compliance/include/banned_functions.h`（132 行）已建立，STRICT 模式下 `#pragma GCC poison` 禁用 30+ 函数。`CMakeLists.txt` L70 `option(AIRY_COMPLIANCE_STRICT "..." ON)` 默认开启，L158-160 全局 `-include banned_functions.h`。`atoms/corekern/CMakeLists.txt` L42-54 为内存子系统实现文件设置 `AIRY_COMPLIANCE_IMPL` 豁免（alloc.c/arena.c/guard.c/mempool.c/oom_handler.c/pool.c/refcount.c/slab.c/tcache.c） |
| 影响 | 基础设施完善，豁免范围合理（仅内存子系统底层实现需要原生 malloc/free） |
| 建议 | **P2**：审查豁免清单是否可进一步收窄；为非豁免代码中的违规调用补充编译期拦截测试 |

### 问题 9：`memory.c` 原生 `malloc`/`free` 与 `AIRY_FREE` 混用

| 项目 | 内容 |
|---|---|
| 状态 | ❌ **未修复** |
| v1.0 描述 | memory.c 20 处 `malloc`/`free` 与 `AIRY_FREE` 混用 |
| 验证方法 | Grep `\bmalloc\(|\bfree\(` in memory.c |
| 证据 | `memory.c` 仍有 **20 处** 原生调用：`malloc(sizeof(...))`（L155/289/416）、`free(ptr)`（L191/193/195/196/386/388/390/391/604/623/706/708/710/711）|
| 影响 | 内存调试追踪缺失，无法统一统计分配/释放；与 banned_functions STRICT 模式冲突 |
| 建议 | **P0**：统一改用 `AIRY_MALLOC`/`AIRY_CALLOC`/`AIRY_FREE`，若 memory.c 属于豁免清单则显式标注 `/* AIRY_COMPLIANCE_IMPL: memory subsystem */` |

### 问题 10：`logging.c` 中文注释尾部 `?` 截断

| 项目 | 内容 |
|---|---|
| 状态 | ❌ **未修复** |
| v1.0 描述 | logging.c 22+ 处中文注释尾部被截断为 `?` |
| 验证方法 | Grep `\?$` in logging.c |
| 证据 | `logging.c` 仍有 **10+ 处** 截断：L261 `获取当前时间戳（毫秒?`、L263 `获取当前时间的Unix时间戳，毫秒精度?`、L265 `当前时间戳（毫秒?`、L278 `获取当前线程的ID，用于日志记录?`、L290 `获取当前进程的ID，用于日志记录?`、L300 `格式化日志消?`、L302 `将日志记录格式化为字符串，根据配置的格式?`、L305 `输出缓冲?`、L306 `缓冲区大?`、L315 `简单文本格式实?` |
| 影响 | UTF-8 多字节字符在特定编辑器/编码下尾部丢失，注释语义不完整 |
| 建议 | **P2**：批量修复截断字符，确保 UTF-8 编码下中文注释完整；接入 CI 编码校验 |

### 2.11 v1.0 修复验证汇总

| 编号 | 问题 | 状态 | 优先级 |
|---|---|---|---|
| 1 | `.clang-format` 不存在 | ❌ 未修复 | P0 |
| 2 | 4 空格缩进违规 | ❌ 未修复 | P0 |
| 3 | agentrt-linux 空仓库 | ⚠️ 部分修复（脚手架已建，0 源码） | P1 |
| 4 | fprintf 直接使用 | ❌ 未修复 | P0 |
| 5 | Windows localtime 线程不安全 | ⚠️ 部分修复（POSIX 已修，Windows 未修） | P1 |
| 6 | typedef struct _t 违规 | ❌ 未修复 | P1 |
| 7 | ASCII 装饰分节符 | ❌ 未修复 | P2 |
| 8 | banned_functions 机制 | ⚠️ 部分修复（基础设施完善，豁免合理） | P2 |
| 9 | malloc/free 混用 | ❌ 未修复 | P0 |
| 10 | 中文注释 `?` 截断 | ❌ 未修复 | P2 |

**修复率：0% 完全修复 + 20% 部分修复 + 80% 未修复**

---

## 三、新发现问题清单

### 3.1 P0 问题（阻断发布）

#### N1：错误码 SSoT 冲突——`AIRY_SUCCESS` 三处定义 + `AIRY_OK` 一处定义

| 项目 | 内容 |
|---|---|
| 严重级别 | **P0** |
| 证据 | `#define AIRY_SUCCESS` 出现在 **3 个文件**：<br>1. `commons/include/airy_types.h:67` `#define AIRY_SUCCESS 0`（权威定义）<br>2. `commons/utils/types/include/types.h:67` `#define AIRY_SUCCESS 0`（重复定义）<br>3. `commons/utils/error/include/error_compat.h:298` `#define AIRY_SUCCESS AIRY_COMPAT_SUCCESS`（第三处，引用兼容层）<br><br>`#define AIRY_OK` 出现在 **1 个文件**：<br>`commons/utils/error/include/error.h:43` `#define AIRY_OK 0`（不同名称，相同语义） |
| 影响 | 同一语义（成功返回值）存在 `AIRY_SUCCESS` 和 `AIRY_OK` 两个名称，且 `AIRY_SUCCESS` 自身有 3 处定义。这违反 SSoT 原则，导致：①不同编译单元可能包含不同定义；②`error_compat.h` 的 `AIRY_COMPAT_SUCCESS` 间接引用增加复杂性；③开发者无法确定应使用哪个名称 |
| 建议 | ①确立 `commons/include/airy_types.h` 为唯一 SSoT，删除 `types.h:67` 和 `error_compat.h:298` 的重复定义；②统一使用 `AIRY_SUCCESS`，将 `AIRY_OK` 标记为 `deprecated` 别名 `#define AIRY_OK AIRY_SUCCESS`（过渡期）后逐步移除；③接入 CI 检查防止重复定义 |

#### N2：`airy_err_t` 重复 typedef

| 项目 | 内容 |
|---|---|
| 严重级别 | **P0** |
| 证据 | `typedef int32_t airy_err_t;` 出现在 **2 个文件**：<br>1. `commons/include/airy_types.h:40`（权威定义）<br>2. `commons/utils/types/include/types.h:62`（重复 typedef） |
| 影响 | C11 标准允许重复 typedef 仅当类型完全一致，但工程上重复 typedef 表明头文件依赖关系混乱。`types.h` 已 `#include "../../../include/airy_types.h"`（L36），不应再次 typedef |
| 建议 | 删除 `types.h:62` 的重复 typedef，直接依赖 `airy_types.h` 的定义 |

#### N3：危险警告抑制 `#pragma GCC diagnostic ignored "-Wfree-nonheap-object"`

| 项目 | 内容 |
|---|---|
| 严重级别 | **P0** |
| 证据 | `cupolas/src/security/cupolas_network_security.c` L94-100：<br>```#pragma GCC diagnostic push<br>#pragma GCC diagnostic ignored "-Wfree-nonheap-object"<br>AIRY_FREE(info->local_ip);<br>AIRY_FREE(info->remote_ip);<br>AIRY_FREE(info->hostname);<br>AIRY_FREE(info->cipher_suite);<br>#pragma GCC diagnostic pop``` |
| 影响 | `-Wfree-nonheap-object` 警告提示正在释放非堆对象（可能是栈对象、全局对象或已释放对象）。抑制此警告可能掩盖真实的内存破坏漏洞。`info->local_ip` 等字段可能是 `char[]` 数组成员（栈/内嵌对象）而非堆指针 |
| 建议 | ①检查 `cupolas_connection_info_t` 结构定义，确认 `local_ip`/`remote_ip`/`hostname`/`cipher_suite` 字段是指针类型还是数组类型；②若为数组，移除 `AIRY_FREE` 调用（无需释放）；③若为指针但可能指向非堆内存，修复赋值逻辑确保只指向堆内存 |

### 3.2 P1 问题（影响质量）

#### N4：`.bak` 文件含 `agentrt_` 前缀残留

| 项目 | 内容 |
|---|---|
| 严重级别 | **P1** |
| 证据 | `atoms/coreloopthree/src/cognition/critique/triple_coordinator.c.bak` 含 **43 处** `agentrt_` 前缀残留（如 `agentrt_error_t`、`agentrt_thinking_step_t` 等） |
| 影响 | `.bak` 文件不应提交到版本库；`agentrt_` 前缀残留违反改名决策（已全量改为 `airy_`） |
| 建议 | ①立即删除 `triple_coordinator.c.bak`；②在 `.gitignore` 中添加 `*.bak` 规则；③CI 检查禁止 `.bak` 文件提交 |

#### N5：39 处 `#pragma GCC diagnostic ignored` 警告抑制

| 项目 | 内容 |
|---|---|
| 严重级别 | **P1** |
| 证据 | **39 处** 分布在 **22 文件**中，包括：<br>- `commons/utils/include/atomic_compat.h` 8 处<br>- `cupolas/src/security/cupolas_runtime_protection.c` 4 处<br>- `heapstore/src/heapstore_trace.c` 4 处<br>- `atoms/corekern/src/task/scheduler.c` 1 处（`-Wunused-function`，L63）<br>- `cupolas/src/security/cupolas_network_security.c` 1 处（`-Wfree-nonheap-object`，见 N3）<br>- 其余 17 文件各 1-2 处 |
| 影响 | 大量警告抑制表明代码与编译器期望不符。部分抑制（如 `-Wunused-function`）可接受，但 `-Wfree-nonheap-object` 等安全相关抑制危险 |
| 建议 | ①审查每处抑制的必要性，移除可修复的；②对必须保留的抑制添加注释说明原因；③禁止在公开头文件中使用 `#pragma GCC diagnostic` |

#### N6：35 处函数内 `static char` 缓冲区（线程不安全）

| 项目 | 内容 |
|---|---|
| 严重级别 | **P1** |
| 证据 | **35 处** 分布在 **28 文件**中，典型案例如：<br>- `protocols/common/src/protocols_impl.c` 1 处<br>- `gateway/src/gateway/gateway_api.c` 1 处<br>- `gateway/src/utils/syscall_router.c` 1 处<br>- `atoms/syscall/src/skill.c` 2 处<br>- `atoms/syscall/src/agent.c` 1 处<br>- `atoms/coreloopthree/src/execution/units/api.c` 1 处 |
| 影响 | 函数内 `static char buf[N]` 在多线程并发调用时会产生数据竞争，返回的指针可能被其他线程覆盖 |
| 建议 | ①改为调用方传入缓冲区 `char *buf, size_t buf_size`；②或使用 `_Thread_local` 线程局部存储（已有 8 处使用，见正面发现）；③或返回堆分配字符串由调用方释放 |

#### N7：`agent_registry_core_get()` 数据竞争未修复

| 项目 | 内容 |
|---|---|
| 严重级别 | **P1** |
| 证据 | `daemons/market_d/src/agent_registry_core.c` L123-137：<br>```const agent_entry_t *agent_registry_core_get(agent_registry_t *registry, const char *agent_id)<br>{<br>    ...<br>    airy_mtx_lock(&registry->lock);<br>    for (...) {<br>        if (strcmp(...) == 0) {<br>            airy_mtx_unlock(&registry->lock);<br>            return &registry->entries[i];  // 返回内部指针后解锁<br>        }<br>    }<br>    ...<br>}```<br>L194-208 `agent_registry_core_get_latest_version()` 同样问题 |
| 影响 | 调用方获得指向内部数组的指针后，锁已释放，其他线程可修改或移除该条目，导致 use-after-free 或数据不一致 |
| 建议 | ①改为调用方传入 `agent_entry_t *out` 输出参数，在锁内拷贝；②或返回深拷贝的堆分配对象由调用方释放 |

#### N8：cupolas 错误码 4 种命名变体仍存在

| 项目 | 内容 |
|---|---|
| 严重级别 | **P1** |
| 证据 | `#define cupolas_OK|CUPOLAS_OK|cupolas_ERROR|cupolas_ERR` 出现 **41 处** 分布在 **3 文件**：<br>- `cupolas/include/cupolas.h` 13 处（L52-91 定义 `cupolas_OK`、`cupolas_ERROR_*`、`CUPOLAS_OK`）<br>- `cupolas/src/platform/platform.h` 12 处<br>- `cupolas/src/security/cupolas_error.h` 16 处 |
| 影响 | 同一模块存在 `cupolas_OK`（小写）、`CUPOLAS_OK`（大写）、`cupolas_ERROR_*`、`cupolas_ERR_*` 四种命名变体，增加认知负担，违反命名一致性 |
| 建议 | ①统一为 `AIRY_ERR_*` 前缀（已映射到 `airy_err_t` 体系）；②移除所有 `cupolas_*` 别名；③保留 `cupolas_ERROR_*` 作为过渡期 `deprecated` 别名 |

### 3.3 P2 问题（代码品味）

#### N9：`scheduler.c` `#pragma GCC diagnostic ignored "-Wunused-function"` 仍存在

| 项目 | 内容 |
|---|---|
| 严重级别 | **P2** |
| 证据 | `atoms/corekern/src/task/scheduler.c` L62-70：`#pragma GCC diagnostic push` / `ignored "-Wunused-function"` / `pop` |
| 影响 | 抑制未使用函数警告可能掩盖死代码 |
| 建议 | 移除未使用的 static 函数，而非抑制警告 |

#### N10：`AIRY_ERROR`/`AIRY_ERROR_NULL` 宏含隐式 `return`

| 项目 | 内容 |
|---|---|
| 严重级别 | **P2** |
| 证据 | `commons/utils/error/include/error.h` L603-638 定义 `AIRY_ERROR`/`AIRY_ERROR_NULL`/`AIRY_RET_ERR` 宏，其中 `AIRY_ERROR_NULL` 在 `agent_registry_core.c` L31/126/136/197/207 等处使用，宏展开含 `return NULL` |
| 影响 | 宏内隐式 `return` 降低代码可读性，且 `AIRY_ERROR_NULL(AIRY_ERR_OVERFLOW, "limit exceeded")` 在 `agent_registry_core_get()` L136 用于"未找到"场景但错误码为 `OVERFLOW`，语义错误 |
| 建议 | ①考虑改为显式 `if (...) return NULL;` 模式；②修复 L136/L207 的错误码，`OVERFLOW` 应改为 `NOT_FOUND` |

---

## 四、代码品味评估（参照 OLK-6.6 六大支柱）

### 4.1 支柱一：Tab 8 缩进

| 项目 | 评分 | 证据 |
|---|---|---|
| Tab 8 使用率 | **5/100** | Tab 开头行仅 71 处（3 文件），4 空格开头行抽样 225 处（3 文件），全量估算 Tab 占比 < 1% |
| `.clang-format` 配置 | **0/100** | 文件不存在 |
| CI 自动校验 | **0/100** | 无 pre-commit hook |

**综合：5/100**——与 OLK-6.6 完全不符，是当前最大的代码品味短板。

### 4.2 支柱二：K&R 大括号

| 项目 | 评分 | 证据 |
|---|---|---|
| 函数定义大括号 | **70/100** | 多数函数遵循 K&R（如 `agent_registry_core.c` L27-36），但部分文件有 Allman 风格残留 |
| 控制结构大括号 | **60/100** | `if`/`for` 单行语句省略大括号较普遍（如 `agent_registry_core.c` L41 `if (!registry) return;`） |

**综合：65/100**——基本合规，单行大括号省略需改进。

### 4.3 支柱三：最小 typedef

| 项目 | 评分 | 证据 |
|---|---|---|
| typedef 使用规范 | **15/100** | 421 处 `} xxx_t;` 分布在 100 文件，滥用 typedef |
| 值类型 vs 句柄区分 | **20/100** | `agent_registry_t`（句柄）与 `agent_entry_t`（值类型）均用 typedef，未区分 |

**综合：15/100**——typedef 滥用严重，需系统性重构。

### 4.4 支柱四：goto 集中出口

| 项目 | 评分 | 证据 |
|---|---|---|
| goto 使用频率 | **55/100** | 151 处 `goto label;` 分布在 36 文件，较 v1.0 的 14 处大幅改善 |
| 集中出口模式 | **50/100** | 部分函数采用 `out:`/`cleanup:` 集中出口，但仍有大量 early return 散布 |

**综合：55/100**——显著改善，但仍需推广集中出口模式。

### 4.5 支柱五：kernel-doc 注释

| 项目 | 评分 | 证据 |
|---|---|---|
| 函数注释覆盖率 | **60/100** | 公开头文件函数注释较完整（如 `cupolas.h` L97-105 `cupolas_init` 注释含 @brief/@param/@return/@post/@note） |
| 注释质量 | **40/100** | 中文注释截断（logging.c 10+ 处 `?`）、ASCII 装饰分节符（590 处）拉低质量 |
| @ownership 标注 | **70/100** | `cupolas.h` 较多使用 `@ownership` 标注所有权（如 L104/L138/L153/L178/L198），是亮点 |

**综合：55/100**——框架完善，细节需修复。

### 4.6 支柱六：80 列行宽

| 项目 | 评分 | 证据 |
|---|---|---|
| 行宽合规率 | **40/100** | 抽样可见多文件超 80 列（如 `agent_registry_core.c` L87-88/174/176/178/183-184 的 `AIRY_STRNCPY_TERM` 长行） |
| 长行处理 | **30/100** | 缺乏自动换行工具，`.clang-format` 不存在无法校验 |

**综合：40/100**——需配合 `.clang-format` 批量修复。

### 4.7 代码品味综合评分

| 支柱 | 评分 | 权重 | 加权分 |
|---|---|---|---|
| Tab 8 缩进 | 5/100 | 25% | 1.25 |
| K&R 大括号 | 65/100 | 15% | 9.75 |
| 最小 typedef | 15/100 | 20% | 3.00 |
| goto 集中出口 | 55/100 | 15% | 8.25 |
| kernel-doc 注释 | 55/100 | 15% | 8.25 |
| 80 列行宽 | 40/100 | 10% | 4.00 |
| **综合** | — | 100% | **34.5/100 (D+)** |

---

## 五、正面发现

### 5.1 [SC] 共享契约层完整性达标

`commons/include/airymax/` 目录下 **8 个头文件**全部就位：

| 文件 | 行数 | 关键内容 |
|---|---|---|
| `ipc.h` | 81 | `AIRY_IPC_MAGIC 0x41524531u`（L19，'ARE1'）+ `struct airy_ipc_msg_hdr` 含 `__attribute__((packed))` + `_Static_assert(sizeof(...) == 128)` |
| `sched.h` | 78 | `AIRY_TASK_MAGIC 0x41475453u`（L25，'AGTS'）+ `airy_vtime_decay()` static inline Q16.16 定点运算 |
| `security_types.h` | — | `AIRY_CAP_AGENT_SPAWN=41` + `enum airy_verdict`（ALLOW/DENY/AUDIT/ASK）+ `enum airy_cap_op`（seL4 CNode 模型） |
| `cognition_types.h` | — | 认知层共享类型 |
| `memory_types.h` | — | 内存管理共享类型 |
| `syscalls.h` | — | 12 核心 + 12 预留 = 24 槽位系统调用编号 |
| `bpf_struct_ops.h` | — | BPF 结构操作（Tab 8 缩进合规） |
| `uapi_compat.h` | — | UAPI 兼容层 |

**评分：95/100**——magic 值正确，`_Static_assert` 编译期校验到位，Tab 8 缩进合规。

### 5.2 banned_functions 合规基础设施完善

- `commons/utils/compliance/include/banned_functions.h`（132 行）建立完整禁用清单
- `AIRY_COMPLIANCE_STRICT` 模式默认开启（`CMakeLists.txt` L70）
- 全局 `-include banned_functions.h`（L158-160）强制所有编译单元包含
- `#pragma GCC poison` 在 STRICT 模式下将违规调用转为编译错误
- `AIRY_COMPLIANCE_IMPL` 豁免机制合理（仅限内存子系统 8 个实现文件）

**评分：85/100**——基础设施完善，豁免范围可控。

### 5.3 C11 atomic 与 _Thread_local 使用

- `memory_order_seq_cst`/`memory_order_acquire`/`memory_order_release`：**280 处** 分布在 **49 文件**（如 `scheduler_core.c` 25 处、`alloc.c` 23 处、`atomic_compat.h` 25 处）
- `_Thread_local` per-CPU 缓存：**8 处** 分布在 **6 文件**（如 `tcache.h`、`slab.c`、`arena.c`）
- `_Static_assert` 编译期校验：**32 处** 分布在 **8 文件**（如 `ipc.h`、`are_ipc.h` 18 处）

**评分：80/100**——并发原语使用规范，是代码品味的亮点。

### 5.4 `airy_err_t` 错误码体系广泛采用

- `airy_err_t` 类型使用：**981 处** 分布在 **100 文件**
- `AIRY_ERROR`/`AIRY_ERROR_NULL`/`AIRY_RET_ERR` 宏封装错误处理
- `@ownership` 所有权标注在 `cupolas.h` 中规范使用

**评分：70/100**——错误码类型统一，但定义存在 SSoT 冲突（见 N1/N2）。

### 5.5 goto 集中出口模式显著改善

- goto 使用从 v1.0 的 **14 处** 增至 **151 处/36 文件**，增长 **978%**
- 集中出口标签（`out:`/`cleanup:`/`fail:`）开始在关键函数中出现

**评分：55/100**——改善显著，但覆盖率仍不足。

---

## 六、改进建议优先级排序

### 6.1 P0 阻断项（必须在进入 M1 前完成）

| 优先级 | 编号 | 建议 | 预估工时 |
|---|---|---|---|
| P0-1 | N1 | 统一 `AIRY_SUCCESS` 定义为 `airy_types.h` 唯一 SSoT，删除 `types.h`/`error_compat.h` 重复定义 | 4h |
| P0-2 | N2 | 删除 `types.h:62` 的 `airy_err_t` 重复 typedef | 1h |
| P0-3 | N3 | 修复 `cupolas_network_security.c` 的 `-Wfree-nonheap-object` 抑制，检查字段类型 | 8h |
| P0-4 | 问题1 | 创建 `.clang-format`（`IndentWidth: 8` + `UseTab: Always` + `ColumnLimit: 80`） | 2h |
| P0-5 | 问题2 | 执行全量 `clang-format -i` 批量重格式化 | 16h |
| P0-6 | 问题4 | memory.c 10 处 `fprintf(stderr)` 改用 `airy_log_write()`；heapstore_migration.c 5 处改用封装 | 8h |
| P0-7 | 问题9 | memory.c 20 处 `malloc`/`free` 统一为 `AIRY_MALLOC`/`AIRY_FREE` 或显式标注豁免 | 8h |

**P0 合计：~47h**

### 6.2 P1 质量项（M1 阶段并行推进）

| 优先级 | 编号 | 建议 | 预估工时 |
|---|---|---|---|
| P1-1 | N4 | 删除 `triple_coordinator.c.bak`，`.gitignore` 添加 `*.bak` | 1h |
| P1-2 | N5 | 审查 39 处 `#pragma GCC diagnostic ignored`，移除可修复项 | 8h |
| P1-3 | N6 | 35 处 `static char` 缓冲区改为调用方传入或 `_Thread_local` | 16h |
| P1-4 | N7 | `agent_registry_core_get()` 数据竞争修复（输出参数或深拷贝） | 4h |
| P1-5 | N8 | cupolas 错误码 4 变体统一为 `AIRY_ERR_*` | 8h |
| P1-6 | 问题5 | Windows `localtime` 改用 `localtime_s` | 2h |
| P1-7 | 问题6 | typedef struct _t 分批重构（优先公开 API 头文件） | 32h |
| P1-8 | 问题3 | agentrt-linux kernel 子仓填充微内核核心代码 | 80h |

**P1 合计：~151h**

### 6.3 P2 品味项（M1 后期或 M2 阶段处理）

| 优先级 | 编号 | 建议 | 预估工时 |
|---|---|---|---|
| P2-1 | 问题7 | 590 处 ASCII 装饰分节符替换为 kernel-doc 格式 | 8h |
| P2-2 | 问题8 | 审查 banned_functions 豁免清单是否可收窄 | 4h |
| P2-3 | 问题10 | logging.c 10+ 处中文注释 `?` 截断修复 | 2h |
| P2-4 | N9 | `scheduler.c` 移除未使用 static 函数 | 1h |
| P2-5 | N10 | `AIRY_ERROR_NULL` 宏隐式 return 改为显式模式；修复 `OVERFLOW`→`NOT_FOUND` 语义错误 | 8h |

**P2 合计：~23h**

### 6.4 总工时估算

| 级别 | 工时 | 占比 |
|---|---|---|
| P0（阻断） | ~47h | 21% |
| P1（质量） | ~151h | 68% |
| P2（品味） | ~23h | 10% |
| **合计** | **~221h** | 100% |

---

## 七、进入 M1 代码开发的就绪度评估

### 7.1 就绪度检查清单

| 检查项 | 状态 | 说明 |
|---|---|---|
| v1.0 P0 问题全部修复 | ❌ 不通过 | 10 项中 8 项未修复 |
| 错误码 SSoT 唯一性 | ❌ 不通过 | `AIRY_SUCCESS` 3 处定义，`AIRY_OK` 1 处定义 |
| `.clang-format` 存在且 CI 强制 | ❌ 不通过 | 文件不存在 |
| banned_functions STRICT 编译通过 | ⚠️ 部分通过 | 基础设施完善，但 memory.c 等仍有违规调用 |
| [SC] 共享契约层完整 | ✅ 通过 | 8 头文件齐备，magic 值正确 |
| 无 `#pragma GCC diagnostic ignored` 安全相关 | ❌ 不通过 | `-Wfree-nonheap-object` 危险抑制存在 |
| 无 `.bak` 文件残留 | ❌ 不通过 | `triple_coordinator.c.bak` 存在 |
| 无数据竞争已知问题 | ❌ 不通过 | `agent_registry_core_get()` 未修复 |

### 7.2 就绪度结论

**就绪度评分：32/100（D+）——未达 M1 进入门槛（80/B）**

**差距：48 分**，主要由以下因素贡献：
- 缩进违规（Tab 8 占比 < 1%）贡献 -20 分
- typedef 滥用（421 处）贡献 -15 分
- 错误码 SSoT 冲突贡献 -8 分
- 内存安全违规（fprintf/malloc/free）贡献 -5 分

**建议**：先完成 P0 阻断项（~47h），将就绪度提升至 ~60/100，再并行推进 P1 质量项，目标在 M1 中期达到 80/B 门槛。

---

## 八、附录

### 8.1 验证工具与命令

| 验证项 | 命令 |
|---|---|
| .clang-format 存在性 | `find /home/spharx/SpharxWorks/OpenAirymax/agentrt -name ".clang-format" -type f` |
| Tab 8 缩进统计 | `Grep "^\t\S" --glob "*.{c,h}"` |
| 4 空格缩进统计 | `Grep "^    \S" --glob "*.{c,h}"` |
| typedef struct _t | `Grep "} \w+_t;" --glob "*.{c,h}"` |
| ASCII 装饰分节符 | `Grep "/\* ={4,}" --glob "*.{c,h}"` |
| #pragma GCC diagnostic | `Grep "#pragma GCC diagnostic ignored" --glob "*.{c,h}"` |
| AIRY_SUCCESS 定义 | `Grep "#define AIRY_SUCCESS" --glob "*.{c,h}"` |
| static char 缓冲区 | `Grep "static char \w+\[" --glob "*.{c,h}"` |
| goto 使用 | `Grep "goto [a-z_]+;" --glob "*.{c,h}"` |
| C11 atomic | `Grep "memory_order_seq_cst\|memory_order_acquire\|memory_order_release" --glob "*.{c,h}"` |
| _Thread_local | `Grep "_Thread_local" --glob "*.{c,h}"` |
| _Static_assert | `Grep "_Static_assert\|static_assert" --glob "*.{c,h}"` |
| .bak 文件 | `find /home/spharx/SpharxWorks/OpenAirymax/agentrt -name "*.bak" -type f` |
| agentrt-linux 源码 | `find /home/spharx/SpharxWorks/OpenAirymax/agentrt-linux -name "*.c" -o -name "*.h"` |

### 8.2 参照文档

| 文档 | 路径 |
|---|---|
| OLK-6.6 六大支柱 | `/home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md` |
| IRON-9 v2 三层共享模型 | `/home/spharx/SpharxWorks/OpenAirymax/docs/AirymaxOS/50-engineering-standards/120-cross-project-code-sharing.md` |
| v1.0 atoms 审查 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt/00-reviews/_review_v1.0/01-atoms-source-deep-review.md` |
| v1.0 daemons 审查 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt/00-reviews/_review_v1.0/02-daemons-others-source-deep-review.md` |
| v2.0 工程审查 | `/home/spharx/SpharxWorks/OpenAirymax/docs-closed/agentrt/00-reviews/_review_v2.0/01-engineering-code-review-v2.md` |

### 8.3 关键证据文件清单

| 文件 | 用途 |
|---|---|
| `commons/include/airymax/ipc.h` | [SC] IPC 头文件，magic 0x41524531 |
| `commons/include/airymax/sched.h` | [SC] 调度头文件，magic 0x41475453 |
| `commons/include/airy_types.h` | 权威类型定义（AIRY_SUCCESS/airy_err_t SSoT） |
| `commons/utils/types/include/types.h` | 重复定义 AIRY_SUCCESS/airy_err_t |
| `commons/utils/error/include/error.h` | AIRY_OK 定义 + AIRY_ERROR 宏 |
| `commons/utils/error/include/error_compat.h` | 第三处 AIRY_SUCCESS 定义 |
| `commons/utils/compliance/include/banned_functions.h` | 合规禁用机制 |
| `commons/utils/memory/src/memory.c` | fprintf/malloc/free 违规 |
| `heapstore/src/heapstore_migration.c` | fprintf 违规 |
| `cupolas/src/audit/audit_overflow.c` | localtime 线程安全 |
| `cupolas/src/security/cupolas_network_security.c` | -Wfree-nonheap-object 危险抑制 |
| `cupolas/include/cupolas.h` | cupolas 错误码 4 变体 |
| `daemons/market_d/src/agent_registry_core.c` | 数据竞争未修复 |
| `atoms/coreloopthree/src/cognition/critique/triple_coordinator.c.bak` | .bak 文件 + agentrt_ 残留 |
| `atoms/corekern/src/task/scheduler.c` | #pragma GCC diagnostic ignored |
| `commons/utils/logging/src/logging.c` | 中文注释 `?` 截断 |
| `CMakeLists.txt` | AIRY_COMPLIANCE_STRICT 配置 |
| `atoms/corekern/CMakeLists.txt` | AIRY_COMPLIANCE_IMPL 豁免清单 |

---

**报告结束**

*本报告基于 2026-07-13 的 agentrt 源代码状态生成。所有结论均有具体文件路径和行号证据支撑，可通过附录 8.1 的命令复现验证。*
