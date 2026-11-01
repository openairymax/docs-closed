# agentrt atoms 模块源代码深度审查报告 v1.0

> **审查范围**：`/home/spharx/SpharxWorks/OpenAirymax/agentrt/atoms/` 全量源代码
> **审查基线**：`docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md`（OLK-6.6 六大支柱）
> **审查日期**：2026-07-13
> **审查者**：Airymax 工程审查专家（agentrt 子代理）
> **审查版本**：atoms 模块当前 HEAD（含 P3.18/P3.21/P0.20.6/P0.20.7 等迭代标记）

---

## 1. 模块结构概览

### 1.1 文件统计

| 子模块 | .c 文件 | .h 文件 | 合计 | 语义分类 | 职责 |
|--------|---------|---------|------|----------|------|
| corekern | 30 | 19 | 49 | A 类 | 微核心原语（mem/task/ipc/time/observability） |
| coreloopthree | 91 | 49 | 140 | B 类 | 三阶段认知循环（cognition/execution/hook/memory） |
| taskflow | 11 | 7 | 18 | B 类 | 任务流引擎（graph/pregel/advanced/core） |
| syscall | 16 | 6 | 22 | B 类 | 系统调用层（sandbox/syscall_table/agent/skill） |
| memoryrovol | 0 | 1 | 1 | B 类 | 记忆卷载（仅 force_includes 头） |
| memory | 4 | 1 | 5 | B 类 | 内置存储与 provider（builtin_*） |
| frameworks | 1 | 1 | 2 | C 类 | 外部 AI 框架适配器桥接层 |
| **合计** | **153** | **84** | **237** | — | — |

### 1.2 子模块清单

- `atoms/corekern/` — 微核心原语（A 类）
  - `src/mem/`：arena/slab/mempool/tcache/pool/alloc/guard/refcount/oom_handler
  - `src/task/`：scheduler（core/platform/posix/windows）/thread
  - `src/ipc/`：are_ipc/buffer/binder
  - `src/time/`：clock/timer/event
  - `src/observability/`、`src/core_init.c`、`src/error.c`
  - `include/`：airy_rt.h / error.h / mem.h / task.h / ipc.h / mempool.h / slab.h / arena.h / tcache.h / refcount.h / oom_handler.h / observability.h / are_ipc.h / airy_time.h / platform_core.h / stdatomic.h / export.h
- `atoms/coreloopthree/` — 三阶段认知循环（B 类，最大子模块）
  - `src/cognition/`：engine / foundation（semantic_unit/metacognition/thinking_chain）/ planner（reactive/reflective/hierarchical/ml_planner/llm_client）/ critique（stream_critic/triple_coordinator/confidence_calibrator/tc3_llm_callbacks）/ coordinator（arbiter/weighted/majority/dual_model）/ dispatch（delegate/parallel_dispatcher）/ dispatcher（round_robin/weighted/priority/ml_based）/ intent（intent_parser/classifier/entity_extractor/utils）/ context/context_processor / ext（cognitive_evolution/multi_agent_collaboration）/ llm_svc_adapter
  - `src/execution/`：engine / core（registry/trace）/ units（api/browser/code/db/file/shell/tool/weighted）/ transaction/compensation / tool_svc_adapter
  - `src/hook/`：hook_executor / hook_registry / hook_builtin_handlers / hook_metrics_handler / hook_audit_handler / hook_trace_handler / hook_interceptor / hook_timeout / service
  - `src/memory/`：engine / memory_service / memoryrovol_bridge
  - `src/`：loop / orchestrator / manager_adapter / orch_adapter / config_loader / yaml_loader / prompt_loader / checkpoint_adapter / memoryrovol_bridge / ops_injection / utils（error_utils/id_utils）
- `atoms/taskflow/` — 任务流引擎（B 类）
  - `src/`：graph_engine / pregel_engine / taskflow_core / taskflow_advanced / taskflow_execution_unit / workflow_patterns
  - `include/`：taskflow.h / taskflow_types.h / taskflow_advanced.h / taskflow_integration.h / graph_engine.h / pregel_engine.h / workflow_patterns.h
- `atoms/syscall/` — 系统调用层（B 类）
  - `src/`：syscall_table / syscall_entry / sandbox / sandbox_permission / sandbox_quota / sandbox_utils / rate_limiter / circuit_breaker / telemetry / session / agent / skill / task / memory
  - `include/`：syscalls.h / airy_sandbox.h
- `atoms/memoryrovol/` — 记忆卷载（仅头文件 `airy_mr_force_includes.h`，实现在 coreloopthree/src/memory/）
- `atoms/memory/` — 内置记忆 provider（builtin_storage/builtin_index/builtin_provider/builtin_retrieval）
- `atoms/frameworks/` — 外部 AI 框架适配器桥接层（C 类，airy_frameworks.c/h）

---

## 2. 代表性文件深读记录

### 2.1 corekern 微核心原语

#### 2.1.1 `corekern/include/airy_rt.h`（统一入口头文件，96 行）

**技术亮点**：
- L13-14：`#ifndef AIRY_RT_H` 标准 include guard
- L22-24：API 版本声明 `AIRY_CORE_API_VERSION_MAJOR/MINOR/PATCH`（语义版本管理）
- L58-60/L92-94：`extern "C"` 边界完整
- L62-90：`airy_init()` / `airy_shutdown()` 公共 API，含完整 Doxygen 注释（@ownership/@threadsafe/@reentrant/@note/@see）

**违规**：
- L36-56：使用 `#include "export.h"` 等内联注释，4 空格缩进
- 文件头 Doxygen 使用 `@file/@brief` 而非 kernel-doc `@file/@brief/@return` 规范

#### 2.1.2 `corekern/include/error.h`（错误码头文件，83 行）

**违规**：
- L58：ASCII 装饰分节符 `/* ==================== 日志宏定义 ==================== */`（违规：装饰性分节符）
- L20/L23：相对路径硬编码 `#include "../../../commons/include/airy_types.h"` 与 `#include "../../../commons/utils/error/include/error.h"`（脆弱的相对路径，应通过 -I 配置）

#### 2.1.3 `corekern/src/error.c`（错误码查表，65 行）

**违规**：
- L13-65：**全文件 4 空格缩进**（违反 OS-STD-FMT-001 Tab 8）
- L13-51：`error_strings[]` 表使用行内对齐空格而非 Tab，每行注释 `/* 0  */` 等
- L55：`const char *airy_strerror(airy_err_t err)` 函数定义开括号在新行 — 符合 K&R，但缩进为 4 空格

**技术亮点**：
- 编译时 const 查表技术（`static const char *error_strings[]`）
- L60：边界检查 `err > ERR_BEGIN || err <= -(airy_err_t)ERROR_COUNT`
- L63-64：NULL 安全 `return s ? s : "Unknown error";`

#### 2.1.4 `corekern/src/core_init.c`（内核入口点，164 行）

**违规**：
- L26-164：全文件 4 空格缩进
- L41/L49/L62/L70/L78/L86/L100：`/* ---- 1. 内存分配器 ---- */` 等装饰性注释

**技术亮点（重要）**：
- L26：`static atomic_long g_core_initialized = 0;` — C11 atomic
- L31-37：**双重检查锁定机制（DCLP）+ 状态机**（0=未初始化，2=初始化中，1=就绪）：
  ```c
  if (!atomic_compare_exchange_strong_explicit(&g_core_initialized, &expected, 2,
                                               memory_order_seq_cst, memory_order_seq_cst)) {
      if (expected == 2) {
          while (atomic_load_explicit(&g_core_initialized, memory_order_seq_cst) == 2) {}
      }
      return AIRY_SUCCESS;
  }
  ```
  使用 `memory_order_seq_cst` 保证全序，CAS 原子推进状态。**优秀实现**。
- L115-126：`goto` 集中出口模式（cleanup_ipc/cleanup_task/cleanup_oom/cleanup_mem/fail）— 标签按分配逆序释放，符合 OS-KER-001/004
- L132-135：`airy_shutdown()` 同样使用 CAS 守护幂等性
- L86-98：heapstore 失败降级（非致命，warn 后继续）— 优雅降级设计

#### 2.1.5 `corekern/include/task.h`（任务调度接口，1-150 行）

**违规**：
- L45-51：`typedef enum { ... } airy_task_state_t;`（枚举 typedef — 边界，OS-STD-CODE-020 主要禁止 struct/pointer typedef）
- L56-61：`typedef struct { const char *name; ... } airy_thread_attr_t;`（**匿名 struct typedef**，违反 OS-STD-CODE-020）
- L63：`/* ==================== 任务调度核心接口 ==================== */` ASCII 装饰分节符
- 全文件 4 空格缩进

**技术亮点**：
- L36-40：`AIRY_TASK_PRIORITY_MIN/LOW/NORMAL/HIGH/MAX` 常量宏
- L66-90：公共 API 含 `@ownership/@threadsafe/@reentrant/@see` 完整 Doxygen

#### 2.1.6 `corekern/src/mem/slab.c`（Slab 分配器，1-150 行）

**违规**：
- L35-37/L51-53/L128-130/L140-142：`/* ===...=== */` ASCII 装饰分节符（4 处）
- L61-69：`typedef struct slab_page { ... } slab_page_t;`（struct typedef）
- L74-76：`typedef struct slab_freelist_node { ... } slab_freelist_node_t;`（struct typedef）
- L84-88：`typedef struct { slab_freelist_node_t *head; ... } slab_cpu_cache_t;`（**匿名 struct typedef**）
- L103/L123/L124：`bool enable_stats;` / `bool initialized;` / `bool destroyed;` — **bool 用作 struct 成员**（违反 OS-STD-011）
- 全文件 4 空格缩进

**技术亮点（重要）**：
- L33：`#include <stdatomic.h>` — C11 原子头
- L111-121：`atomic_uint_fast64_t` / `atomic_uint` 用于统计计数 — C11 显式内存序
- L138：`static _Thread_local slab_cpu_cache_t g_cpu_cache;` — **C11 thread-local per-CPU 缓存**
- L40-49：`SLAB_CPU_FREELIST_MAX=64` / `SLAB_BATCH_RETURN_SIZE=16` / `SLAB_CACHE_LINE_ALIGN=64` — cache line 对齐常量
- L147-149：`align_to_cache_line()` cache line 对齐辅助函数
- L93-126：`struct airy_slab` 主结构（不透明，无 typedef）
- 设计：per-CPU freelist（无锁）+ 全局 partial 链（持锁）+ 构造/析构回调 + 位图分配跟踪

#### 2.1.7 `corekern/include/mempool.h`（紧急预留内存池，206 行）

**违规**：
- L34-36/L47-49/L99-101：ASCII 装饰分节符
- L54-57：`typedef enum { ... } airy_mempool_mode_t;`（enum typedef，边界）
- L62-67：`typedef struct { ... } airy_mempool_config_t;`（**匿名 struct typedef**）
- L72-92：`typedef struct { ... } airy_mempool_stats_t;`（**匿名 struct typedef**）
- L66/L91：`bool enable_stats;` / `bool emergency_mode;` — bool 用作 struct 成员
- 全文件 4 空格缩进

**技术亮点**：
- L97：`typedef struct airy_mempool airy_mempool_t;` — **不透明指针 typedef**（OS-STD-CODE-020 例外 (a) 允许）
- L113-116：Doxygen 示例使用指定初始化器（`= { .name = "ipc_mempool", ... }`）
- L39：`AIRY_MEMPOOL_IPC_EMERGENCY_RESERVE_MB 32` — IPC 紧急预留 32MB
- 设计：普通池 + 紧急池双级分配，OOM 时切换紧急模式

#### 2.1.8 `corekern/src/ipc/are_ipc.c`（ARE L2 IPC + CRC32，1-150 行）

**违规**：
- L34-36/L84-86：ASCII 装饰分节符
- L45-60：CRC32 查表每行 16 个 hex 值，**单行 211 列**（严重违反 OS-STD-FMT-002）
- 全文件 4 空格缩进

**技术亮点（重要）**：
- L44-61：**编译时 const CRC32 查表技术**（256 项，IEEE 802.3 多项式 0xEDB88320，zlib/PNG 兼容，零运行时初始化、无线程安全问题）
- L73-82：`are_crc32_update()` **纯函数**，注释明示"纯函数 + 只读全局"
- L109/L149：`__builtin_memset` / `__builtin_memcpy` 替代标准库（绕开 libc 毒化）
- L123/L128：`__builtin_strncpy` 显式绕开 strncpy 毒化（OS-BAN-004 适配）
- L96-106：枚举范围校验（防御性编程）
- L132：`header->timestamp_ns = airy_time_realtime_ns();` — CLOCK_REALTIME 纳秒时间戳

#### 2.1.9 `corekern/include/export.h`（符号导出管理，49 行）

**违规**：
- L21/L35：ASCII 装饰分节符

**技术亮点**：
- L23-33：跨平台符号导出（Windows `__declspec(dllexport/dllimport)` vs GCC/Clang `__attribute__((visibility("default")))`）
- L37-43：`AIRY_INTERNAL` 内部符号标记（visibility hidden）
- L11：声明"这是 AIRY_API 的唯一权威定义源" — SSoT 单一真值源

#### 2.1.10 `corekern/src/task/scheduler.c`（任务调度器，1-120 行）

**违规**：
- L52/L86：ASCII 装饰分节符
- L62-70：`#pragma GCC diagnostic push/ignored "-Wunused-function"/pop` — **抑制警告**（违反 OS-STD-CODE-004 零警告门禁精神）
- L98/L102：`AIRY_ERROR(AIRY_EINVAL, "...");` 用作 if 块最后一条语句，无显式 return — **控制流不透明**（AIRY_ERROR 行为不可见）
- 全文件 4 空格缩进

**技术亮点**：
- L24-26：三层架构（核心层 + 适配器接口 + 平台适配器），消除 Windows/POSIX 重复
- L40-46：跨平台原子操作通过 `atomic_compat.h` 统一
- L31-32/L48：`memory_compat.h` / `string_compat.h` / `error_compat.h` 跨平台 compat 层

### 2.2 taskflow 任务流引擎

#### 2.2.1 `taskflow/src/pregel_engine.c`（Pregel 超步引擎，1186 行）

**违规**：
- L27/L108/L341：`// ===...===` ASCII 装饰分节符（3 处）
- L32-40：`typedef struct { vertex_id_t vertex_id; ... } pregel_vertex_state_t;`（**匿名 struct typedef**）
- L43-49：`typedef struct message_queue_entry_s { ... } message_queue_entry_t;`（struct typedef）
- L52-57：`typedef struct { ... } message_queue_t;`（**匿名 struct typedef**）
- L60-65：`typedef struct { ... } worker_context_t;`（**匿名 struct typedef**）
- L36/L37/L103-106：`bool active;` / `bool vote_to_halt;` / `bool initialized;` / `bool running;` / `bool paused;` — bool 用作 struct 成员
- L200-201/L288-289/L346-347/L352-353/L386-387/L398-399/L410-411：**`AIRY_ERROR_NULL(...)` 用作 if 块最后语句无 return** — 后续代码直接解引用可能 NULL 的指针（**潜在 NULL deref**，严重隐患）
  ```c
  if (!queue || !queue->front) {
      AIRY_ERROR_NULL(AIRY_ERR_INVALID_PARAM, "null parameter");
  }
  message_queue_entry_t *entry = queue->front;  // 若 AIRY_ERROR_NULL 不 return，此处 NULL deref
  ```
- L132/L161-162/L176 等：`(message_queue_t *)AIRY_CALLOC(...)` — **冗余 void* 强制转换**（违反 OS-BAN-003）
- L286：`worker_context_t *context = (worker_context_t *)arg;` — 冗余 void* 转换
- 全文件 4 空格缩进
- L8/L132/L155/L222/L242 等：46 处超 80 列

**技术亮点（重要）**：
- L359-367/L526-527：**BAN-333 强制 max_workers=1 串行降级**（明确注释"0.1.1 的 pregel_engine 并发路径尚未经过多线程验证，强制串行模式以确保正确性优先于性能"）— **符合任务描述预期**
- L413-416：ASan 检测到的 12 处 32B 内存泄漏修复注释（workers 数组延迟到 init 分配）
- L522-524：`airy_mtx_init` / `airy_cond_init` 跨平台同步原语
- L585-602：线程创建失败回滚（started_count < worker_count 时清理已启动线程）
- L852：`static uint64_t next_checkpoint_id = 1;` — 函数内 static 检查点 ID 生成器
- L335：`struct timespec ts = {.tv_nsec = 10000000};` — 指定初始化器
- L854-867：检查点 snapshot 序列化（superstep + active_vertices + vertex_states）
- 设计：消息队列（FIFO）+ 顶点状态机（active/vote_to_halt）+ 检查点（环形缓冲 16 上限）+ 超步回调（start_func/end_func/compute_func）

#### 2.2.2 `taskflow/src/graph_engine.c`（图引擎，1-200 行）

**违规**：
- L19/L75：`// ===...===` ASCII 装饰分节符
- L24-28/L31-35/L38-42/L45-49：4 处 `typedef struct xxx_s { ... } xxx_t;`（struct typedef）
- L72：`bool initialized;` — bool 用作 struct 成员
- 全文件 4 空格缩进

**技术亮点**：
- L80-95：FNV-1a 哈希算法
- L98-114：质数表查表（`static const size_t primes[]`）— 编译时 const 查表技术
- L101-105：26 项质数表，覆盖 53 到 1610612741
- L113：`return capacity * 2 + 1;` 回退方案
- L124-139：通用哈希表销毁（函数指针回调 `free_entry`）
- L168-181：链式哈希查找顶点索引

#### 2.2.3 `taskflow/src/taskflow_advanced.c`（高级工作流引擎，1-150 行）

**违规**：
- L25-29/L31-34/L36-42：3 处 `typedef struct { ... } xxx_t;`（**匿名 struct typedef**）
- L73：`if (!engine) return NULL;` — **单行多语句**（可读性差）
- L136/L138：`AIRY_ERROR(...)` / `AIRY_RET_ERR(...)` 用作 if 块最后语句无 return — 控制流不透明
- L146：`AIRY_STRNCPY_TERM(...)` 缩进丢失（行首无缩进）
- 全文件 4 空格缩进

**技术亮点**：
- L14-22：条件编译 cJSON 适配（`AIRY_TASKFLOW_HAVE_CJSON`），不可用时返回 ENOTSUP（显式不支持，非桩函数）
- L44-48：ODR 违反修复注释（struct tag 改为 `taskflow_adv_engine_s`，与 `taskflow_engine_s` 分离）
- L49-63：`struct taskflow_adv_engine_s` 主结构（11 字段，与 taskflow_engine_s 30+ 字段分离）
- L65-68：`generate_id()` 内联 ID 生成器
- L132-149：handler 注册（重复名覆盖，溢出检查）

#### 2.2.4 `taskflow/include/taskflow_advanced.h`（高级工作流引擎接口，1-80 行）

**违规**：
- L53-63/L68-78：`typedef enum { ... } taskflow_node_type_t;` / `taskflow_state_t;`（enum typedef，边界）
- 全文件 4 空格缩进

**技术亮点**：
- L11-19：模块级 Doxygen 文档（7 项核心设计：DAG/条件分支/并行汇聚/子工作流/循环迭代/错误恢复/检查点）
- L20-22：`@since 0.1.0` / `@see atoms/taskflow` 版本与跨引用
- L36-48：常量宏（`TASKFLOW_MAX_NODES=1024` / `TASKFLOW_MAX_EDGES=4096` / `TASKFLOW_MAX_SUBFLOWS=64` / `TASKFLOW_MAX_CHECKPOINTS=256` / `TASKFLOW_MAX_PARALLEL=32`）

#### 2.2.5 `taskflow/include/graph_engine.h`（图引擎接口，1-80 行）

**违规**：
- L20/L29：`// ===...===` ASCII 装饰分节符
- L27：`typedef struct graph_engine_s *graph_engine_handle_t;` — **指针 typedef**（边界，opaque handle 模式可视为 OS-STD-CODE-020 例外 (a)）
- 全文件 4 空格缩进

**技术亮点**：
- L27：不透明句柄模式（`graph_engine_handle_t`）
- L24-26：`@brief 图引擎句柄（不透明类型）` — 显式标注不透明
- L33-79：完整 Doxygen 公共 API 注释

### 2.3 syscall 系统调用层

#### 2.3.1 `syscall/src/syscall_table.c`（系统调用分发表，88 行）

**违规**：
- L28：注释含编码错误 `/* 函数声明（实现位?syscall_entry.c?*/`（? 应为「于」）
- L83：`return (void *)(intptr_t)AIRY_EINVAL;` — 强制转换错误码为指针（设计味道差，但合法）
- 全文件 4 空格缩进
- L14/L16/L19/L22 等：4 处超 80 列

**技术亮点（重要）**：
- L21-24：**`_Static_assert` 编译期校验**（`SYS_TOOL_EXECUTE == 23` / `SYS_MAX == 24`）— 错误早暴露，零运行期隐患
- L54-78：**指定初始化器**（`[SYS_TASK_SUBMIT] = sys_task_submit`）— 符合 OS-STD-CODE-014
- L80-87：`airy_syscall_invoke()` 边界检查 + 分发
- L14-16：注释明示 SSoT 单一真值源（"消除 syscall_table.c / test_syscalls.c / test_syscall_extended.c 三处重复定义"）
- L26：`typedef void *(*syscall_func_t)(void **args, int argc);` — 函数指针 typedef（OS-STD-CODE-020 例外允许）

#### 2.3.2 `syscall/include/syscalls.h`（系统调用接口，335 行）

**违规**：
- L30/L43/L81/L124/L178/L195/L231/L266/L323：**9 处** `/* ==================== xxx ==================== */` ASCII 装饰分节符
- L129-135：`typedef enum { ... } session_persist_status_t;`（enum typedef，边界）
- L313-321：`typedef struct { const char *executable; ... } tool_execute_args_t;`（**匿名 struct typedef**）
- L105：`AIRY_API airy_err_t airy_sys_memory_search(..., float **out_scores, ...)` — **超 80 列**
- L175：`AIRY_API airy_err_t airy_sys_session_get_persist_status(...)` — 超 80 列
- 全文件 4 空格缩进

**技术亮点**：
- L13-15：API 版本声明（MAJOR.MINOR.PATCH）
- L269-303：`airy_syscall_num_t` 公共枚举（SSoT 单一真值源），值约定注释（"从 1 开始连续递增，SYS_MAX 为哨兵值，在 SYS_MAX 之前追加新项即可扩展，不得在中间插入"）
- L301：`SYS_TOOL_EXECUTE, /**< P3.18 (ACC-DT27): tool_d 经 sandbox 执行工具 = 23 */`
- L305-321：`tool_execute_args_t` 完整 Doxygen 含生命周期说明
- L36-264：22 个公共 syscall API 全部含 Doxygen 注释

#### 2.3.3 `syscall/include/airy_sandbox.h`（安全沙箱公共 API，165 行）

**违规**：
- L43/L69/L84/L115/L132：5 处 ASCII 装饰分节符
- L51：`typedef struct airy_sandbox airy_sandbox_t;`（opaque 指针 typedef，OS-STD-CODE-020 例外 (a) 允许）
- L63-67：`typedef enum { ... } permission_type_t;`（enum typedef，边界）
- 全文件 4 空格缩进

**技术亮点**：
- L8-30：详细模块级 Doxygen（含典型用法代码示例 + fail-closed 原则说明 + 线程安全声明）
- L46-50：不透明句柄模式 + 实现位置注释
- L54-62：`permission_type_t` 三值枚举（ALLOW/DENY/ASK），DENY 优先级最高
- L148-156：`airy_sandbox_invoke()` 执行流程文档化（状态检查 → permission_check → quota_check → syscall_invoke → audit_log → 性能统计）
- L156：`@note fail-closed 原则：sandbox 为 NULL 时调用方必须拒绝执行` — 显式安全契约

### 2.4 coreloopthree 三阶段认知循环

#### 2.4.1 `coreloopthree/src/loop.c`（主循环实现，1-200 行）

**违规**：
- L168：`/* ==================== 辅助函数实现 - 用于降低圈复杂度 ==================== */` ASCII 装饰分节符
- L152：`__builtin_memset(manager, 0, sizeof(airy_loop_config_t));` — 替代标准 memset（绕开 libc）
- L185/L190/L194：`AIRY_ERROR(AIRY_EINVAL, "...");` 用作 if 块最后语句无 return — 控制流不透明
- 全文件 4 空格缩进
- L55/L62/L65-67 等：**255 处超 80 列**（最多 117 列于 L62）

**技术亮点（重要）**：
- L44-100：`struct airy_core_loop` 主结构（不透明，无 typedef），含 20+ 字段
- L49-51：`atomic_int running;` / `atomic_int stop_requested;` / `atomic_int task_pending;` — C11 atomic 状态标志
- L56：`airy_arena_t *arena;` — P1.19.4 Arena 分配器（请求路径短生命周期分配）
- L59/L72/L75/L78/L81：5 个适配器字段（llm_adapter/tool_adapter/memory_bridge/manager_adapter/orch_adapter）— **清晰的适配器模式**
- L65-68：`fallback_plan_strat` BORROW 语义注释（"engine destroy 时不销毁此对象，由 loop 在 cleanup/destroy 时显式调用 strat->destroy()"）— **明确所有权语义**
- L99：`taskflow_engine_t *taskflow_engine;` — **W18: taskflow_advanced DAG 工作流引擎集成**（双引擎协同：scheduler A 类 + taskflow_advanced B 类）
- L103-110：辅助函数前向声明（validate_loop_parameters/allocate_loop_memory/initialize_loop_resources/create_loop_engines/cleanup_loop_resources/free_loop_memory）— **降低圈复杂度的函数拆分**
- L150-166：`init_default_config()` 默认配置初始化
- L176-199：`validate_loop_parameters()` 参数校验（线程数 ≤1024 / max_queued_tasks 范围 / stats_interval_ms ≤1 小时）

#### 2.4.2 `coreloopthree/src/cognition/engine.c`（认知引擎核心，1-220 行）

**违规**：
- 全文件 4 空格缩进
- L88/L90：`float meta_acceptance_threshold;` / `float align_history[8];` — float 用作 struct 成员（用户态可接受，但应注意）

**技术亮点（重要）**：
- L64-122：`struct airy_cognition_engine` 主结构（不透明，无 typedef），20+ 字段
- L84：`int enable_dual_thinking;` — **用 int 而非 bool 作 struct 成员**（符合 OS-STD-011）
- L110/L113：`int checkpoint_enabled;` / `int llm_stream_enabled;` — 同样用 int 替代 bool（符合规范）
- L65-69：3 个策略字段（plan_strat/fallback_plan_strat/coord_strat/disp_strat）— 策略模式
- L70-71：`void *context; void (*context_destroy)(void *);` — 用户上下文 + 析构回调（RAII 思想）
- L81-82：`airy_thinking_chain_t *chain;` / `airy_metacognition_t *meta;` — Thinkdual 双思考集成
- L95：`sc_stream_critic_t *stream_critic;` — 流式批判器
- L97-107：5 个 C-Lxx 适配器字段（llm_svc/llm_adapter/tool_svc/tool_adapter/memory_provider）— 模块解耦
- L113：`airy_task_plan_t *current_plan; /**< Currently processing plan (borrowed, for checkpoint) */` — **BORROW 语义显式标注**
- L124-131：`trigger_feedback()` 反馈回调
- L139-180：`cognition_provider_write()` 含 ON_MEMORY_EVOLVE hook 触发（ABORT 跳过 / RETRY 降级为 CONTINUE）
- L183-190：`airy_cognition_create_take()` 所有权转移语义（_take 后缀）
- L193-219：`airy_cognition_create_ex_take()` 含配置 + 策略注入
- 设计：5 阶段认知处理管线（Phase 0 指令拆解 → Phase 1 规划 → Phase 2 执行-验证循环 → Phase 3 审计 → Phase 4 目标对齐）

#### 2.4.3 `coreloopthree/include/loop.h`（主循环接口，1-100 行）

**违规**：
- L42-58：`typedef struct airy_loop_config { ... } airy_loop_config_t;`（struct typedef，有 tag，边界）
- L34-37：4 处 `typedef struct xxx xxx_t;`（opaque 指针 typedef，例外 (a) 允许）
- 全文件 4 空格缩进

**技术亮点**：
- L42-58：`airy_loop_config_t` 配置结构体，**全部用 uint32_t/size_t 替代 bool**（符合 OS-STD-011）
- L51-53：3 个策略指针字段（plan/coord/disp_strategy）
- L62-84：完整 Doxygen（@param[in]/[out]/@ownership/@threadsafe/@reentrant/@see）
- L24：`#include "taskflow_advanced.h"` — 显式集成 taskflow_advanced

### 2.5 memoryrovol 记忆卷载

#### 2.5.1 `memoryrovol/src/airy_mr_force_includes.h`（强制包含头，14 行）

**违规**：
- 全文件 4 空格缩进

**技术亮点**：
- L6-7：统一 commons 路径（`memory_compat.h` + `platform.h`）
- L9-12：`AIRY_USE_SCHEDULER_THREAD_IMPL` 条件前向声明 `airy_thread_create/join`

### 2.6 memory 内置存储

#### 2.6.1 `memory/src/builtin_storage.c`（内置存储实现，1-100 行）

**违规**：
- L63-70/L72-78：2 处 `typedef struct xxx { ... } xxx_t;`（struct typedef，有 tag，边界）
- L77：`void *lock;` — 不透明锁指针（OK）
- 全文件 4 空格缩进

**技术亮点（重要）**：
- L21-56：**跨平台 mkdir 与 secure_random 实现**（Windows `_mkdir` + `rand_s` / POSIX `mkdir` + `/dev/urandom`）
- L29/L45：`rand_s(&val)` / `read(fd, &val, sizeof(val))` — 安全随机数源
- L33/L53：fallback 路径（`time(NULL) ^ ((size_t)&val >> 4)`）— 优雅降级
- L82：`char tmp[AIRY_MAX_PATH_LEN] = {0};` — 指定初始化器
- L84-91：`ensure_dir()` 路径逐级创建（处理 `/` 和 `\\` 双分隔符）
- L94-98：`generate_record_id()` 格式 `rec-{timestamp}-{random_hex}`
- L60：`AIRY_MAX_RECORDS 1000000` — 容量上限

### 2.7 frameworks 外部框架适配器

#### 2.7.1 `frameworks/include/airy_frameworks.h`（外部 AI 框架适配器接口，310 行）

**违规**：
- L35/L42/L55/L69/L80/L91/L107/L170/L183/L229/L289：**11 处** ASCII 装饰分节符
- L57-67/L71-78：`typedef enum { ... } airy_fw_capability_t;` / `airy_fw_state_t;`（enum typedef，边界）
- L82-89：`typedef struct { ... } airy_fw_config_t;`（**匿名 struct typedef**）
- L86-87：`bool enable_metrics;` / `bool enable_tracing;` — bool 用作 struct 成员
- L93-98/L100-105/L172-181：3 处 **匿名 struct typedef**
- L115-168：`typedef struct airy_framework_adapter_s { ... } airy_framework_adapter_t;`（struct typedef，有 tag，边界）
- 全文件 4 空格缩进

**技术亮点**：
- L8-22：详细模块级 Doxygen（"Airymax 作为行业底座连接外部 AI 框架的桥梁"，支持 LangChain/AutoGPT/CrewAI/Semantic Kernel/LlamaIndex 等）
- L13-17：设计原则（薄层注册表 + 函数指针回调 + 线程安全 + 不持有外部状态）
- L57-67：能力位掩码枚举（8 位：cognition/execution/memory/planning/protocol/safety/streaming/multi_agent）
- L115-168：**适配器接口**（函数指针表：init/start/stop/destroy/health_check/process_request）— 经典 adapter 模式
- L116-119：元信息字段（name/version/capabilities）
- L190-304：完整公共 API（registry_init/shutdown/register/unregister/find/list + create_instance/start/stop/destroy/health_check/get_info/process_request + 工具函数）

---

## 3. 工程标准违规统计表

### 3.1 按 OLK-6.6 六大支柱分类

| 规则编号 | 规则内容 | 严重度 | 违规类型 | 违规模数 | 证据示例 |
|----------|----------|--------|----------|----------|----------|
| OS-STD-FMT-001 | Tab 8 字符缩进 | ERROR | 4 空格缩进 | 237 文件全量违规（~10847 处） | 全 atoms 目录 0 文件使用 Tab |
| OS-STD-FMT-002 | 80 列行宽硬上限 | WARN | 超长行 | 5901 行 | loop.c L62=117 列 / are_ipc.c L45=211 列 |
| OS-STD-FMT-003/009 | K&R 大括号 | WARN | 函数大括号 | 极少违规 | 大多数函数定义开括号在新行（符合） |
| OS-STD-CODE-020 | 禁止结构体 typedef | WARN | 匿名 struct typedef | 114+ 处 | pregel_engine.c L32/L52/L60；mempool.h L62/L72；frameworks.h L82/L93/L100/L172 |
| OS-STD-011 | bool 仅用于返回值与栈变量 | WARN | bool 用作 struct 成员 | 30+ 处 | slab.c L103/L123/L124；mempool.h L66/L91；frameworks.h L86/L87；pregel_engine.c L36/L37/L103-106 |
| OS-KER-001 | goto 集中出口 | ERROR | 自定义宏替代 goto | 100+ 处 | AIRY_ERROR/AIRY_ERROR_NULL/AIRY_RET_ERR 替代 goto out_xxx |
| OS-STD-CODE-004 | 零警告门禁 | ERROR | #pragma 抑制警告 | 1 处 | scheduler.c L62-70 `#pragma GCC diagnostic ignored "-Wunused-function"` |
| OS-BAN-003 | sizeof(*p) + 禁 void* 强转 | WARN | 冗余 void* 转换 | 20+ 处 | pregel_engine.c L132/L161/L286/L350 等 `(message_queue_t *)AIRY_CALLOC(...)` |
| OS-STD-CODE-012 | kernel-doc | WARN | 注释不完整 | 部分公共 API | graph_engine.h 部分函数缺 @return/@threadsafe |
| OS-STD-CODE-014 | 指定初始化器 | ERROR | 位置初始化器 | 0 处违规（全部符合） | syscall_table.c L54-78 全部指定初始化器 |

### 3.2 装饰性分节符违规

| 模式 | 文件数 | 典型文件 |
|------|--------|----------|
| `/* ==================== xxx ==================== */` | 120 文件 | syscalls.h（9 处）、airy_frameworks.h（11 处）、loop.c、error.h、export.h |
| `// ================================================================` | 30+ 文件 | slab.c、mempool.h、are_ipc.c、graph_engine.c、pregel_engine.c |
| `/* ---- xxx ---- */` | 10+ 文件 | core_init.c（7 处） |

### 3.3 控制流不透明违规（AIRY_ERROR 宏滥用）

| 文件 | 行号 | 风险 |
|------|------|------|
| pregel_engine.c | L200-201 | `AIRY_ERROR_NULL(...)` 后直接 `queue->front` 解引用（潜在 NULL deref） |
| pregel_engine.c | L288-289 | `AIRY_ERROR_NULL(...)` 后直接 `context->engine` 解引用 |
| pregel_engine.c | L346/L352/L386/L398/L410 | 多处 `AIRY_ERROR_NULL(...)` 用作 if 块最后语句 |
| loop.c | L185/L190/L194 | `AIRY_ERROR(...)` 用作 if 块最后语句无 return |
| scheduler.c | L98/L102 | `AIRY_ERROR(...)` 用作 if 块最后语句无 return |
| taskflow_advanced.c | L136/L138 | `AIRY_ERROR(...)` / `AIRY_RET_ERR(...)` 控制流不透明 |

> **注**：`AIRY_ERROR` / `AIRY_ERROR_NULL` / `AIRY_RET_ERR` 宏定义不在 atoms 目录内（位于 commons/utils/error/），atoms 内开发者无法直接看到宏行为，存在维护性风险。若宏不 return，则 pregel_engine.c 多处存在 NULL deref。

---

## 4. 函数前缀边界分析

### 4.1 前缀使用统计

| 前缀 | 出现次数（atoms 内） | 文件数 | 用途 | 评估 |
|------|---------------------|--------|------|------|
| `airy_*`（C 标识符） | 916+ 处 | 20+ 文件 | agentrt 同源 API（[SS] 语义同源层） | GOOD，主导前缀 |
| `agentrt_*`（C 标识符） | **0 处** | 0 文件 | — | GOOD，无 C 标识符使用 |
| `agentrt_`（含注释/路径） | 4058 处 | 100 文件 | 仅注释、文件路径、项目名引用 | GOOD，非 C 标识符 |
| `agentos_*` | **0 处** | 0 文件 | — | GOOD，无残留 |
| `airymaxos_*` | **0 处** | 0 文件 | — | GOOD，无残留（此前缀仅用于 AirymaxOS） |

### 4.2 边界清晰度评估

| 边界 | 评估 | 说明 |
|------|------|------|
| `airy_*` vs `agentrt_*` C 标识符 | **清晰** | atoms 内无 `agentrt_*` 函数/类型标识符，全部使用 `airy_*` |
| `airy_*` 子模块命名空间 | **清晰** | corekern 用 `airy_*`（如 `airy_init`/`airy_task_init`/`airy_ipc_init`）；taskflow 用 `taskflow_*`/`graph_engine_*`/`pregel_engine_*`；syscall 用 `airy_sys_*`/`airy_sandbox_*`；frameworks 用 `airy_fw_*` |
| 模块内函数前缀 | **清晰** | 各子模块有独立命名空间（`are_ipc_*` for ARE IPC、`taskflow_*` for taskflow、`graph_engine_*` for graph 等） |

### 4.3 函数命名空间清单

| 子模块 | 函数前缀 | 示例 |
|--------|----------|------|
| corekern 核心 | `airy_` | `airy_init` / `airy_shutdown` / `airy_strerror` |
| corekern mem | `airy_mem_` / `airy_mempool_` / `airy_slab_` / `airy_arena_` | `airy_mem_init` / `airy_mempool_create` |
| corekern task | `airy_task_` | `airy_task_init` / `airy_task_self` / `airy_task_sleep` |
| corekern ipc | `airy_ipc_` / `are_ipc_` / `are_crc32_` | `airy_ipc_init` / `are_ipc_header_init` |
| corekern time | `airy_time_` | `airy_time_eventloop_init` / `airy_time_realtime_ns` |
| corekern oom | `airy_oom_` | `airy_oom_init` / `airy_oom_config_apply` |
| coreloopthree | `airy_loop_` / `airy_cognition_` / `airy_execution_` / `airy_memory_` | `airy_loop_create` / `airy_cognition_create_take` |
| taskflow | `taskflow_engine_*` / `graph_engine_*` / `pregel_engine_*` | `taskflow_engine_create` / `pregel_engine_init` |
| syscall | `airy_syscalls_` / `airy_sys_` / `airy_sandbox_` / `airy_syscall_` | `airy_syscalls_init` / `airy_sys_task_submit` / `airy_sandbox_invoke` |
| memory | `builtin_storage_*` / `builtin_provider_*` | `builtin_storage_create` |
| frameworks | `airy_fw_` | `airy_fw_registry_init` / `airy_fw_register_adapter` |

---

## 5. 技术亮点清单

### 5.1 C11 显式内存序（atomic 操作）

| 文件 | 行号 | 用法 |
|------|------|------|
| core_init.c | L26/L31-37/L111/L125/L132 | `atomic_long` + `atomic_compare_exchange_strong_explicit` + `memory_order_seq_cst`（双重检查锁定 + 状态机） |
| slab.c | L111-121 | `atomic_uint_fast64_t` / `atomic_uint` 用于统计计数 |
| time/event.c | L55/L56/L63/L74/L85/L103/L109/L111/L119 | `atomic_load_explicit` / `atomic_store_explicit` + `memory_order_acquire` / `memory_order_seq_cst` |
| syscall/session.c | L223/L239 | `atomic_compare_exchange_strong_ptr` + `atomic_fetch_add_explicit` |
| syscall/agent.c | L50/L280 | 同上 |
| syscall/skill.c | L99/L1463 | 同上 |

### 5.2 跨平台 compat 层

| compat 头 | 用途 | 使用文件 |
|-----------|------|----------|
| `memory_compat.h` | AIRY_MALLOC/CALLOC/REALLOC/FREE 跨平台封装 | 全 atoms |
| `string_compat.h` | 字符串操作跨平台 | 全 atoms |
| `atomic_compat.h` | 原子操作跨平台 | corekern/coreloopthree |
| `sync_compat.h` | 同步原语跨平台 | corekern/mem |
| `logging_compat.h` | 日志跨平台（彩色 + CLOCK_REALTIME） | 全 atoms |
| `error_compat.h` | 错误码跨平台 | 全 atoms |
| `platform.h` | 线程/锁/条件变量跨平台 | 全 atoms |
| `compat.h` | 通用兼容 | scheduler.c |
| `check.h` | CHECK_NULL 等检查宏 | loop.c |

### 5.3 编译时 const 查表技术

| 文件 | 行号 | 表内容 | 用途 |
|------|------|--------|------|
| are_ipc.c | L44-61 | `static const uint32_t g_crc32_table[256]` | CRC32-IEEE 802.3 查表（零运行时初始化、线程安全） |
| graph_engine.c | L101-105 | `static const size_t primes[]`（26 项） | 哈希表大小选择（减少冲突） |
| error.c | L13-51 | `static const char *error_strings[]` | 错误码到字符串映射 |

### 5.4 双重检查锁定机制（DCLP）

| 文件 | 行号 | 实现 |
|------|------|------|
| core_init.c | L26-37/L131-135 | `atomic_compare_exchange_strong_explicit` + 状态机（0=未初始化，2=初始化中，1=就绪）+ 自旋等待 |

### 5.5 纯函数设计

| 文件 | 行号 | 函数 | 说明 |
|------|------|------|------|
| are_ipc.c | L73-82 | `are_crc32_update()` | 注释明示"纯函数 + 只读全局" |
| error.c | L55-65 | `airy_strerror()` | 无副作用，纯查表 |

### 5.6 Doxygen 文档完善度

| 模块 | 完善度 | 示例 |
|------|--------|------|
| corekern 公共 API | 高 | `airy_init()` 含 @ownership/@threadsafe/@reentrant/@note/@see |
| syscall 公共 API | 高 | `airy_sandbox_invoke()` 含 @param/@return/@details/@note |
| frameworks 公共 API | 高 | `airy_fw_register_adapter()` 含 @param/@return/@details |
| taskflow 公共 API | 中 | `graph_engine_create()` 等部分函数缺 @return/@threadsafe |
| coreloopthree 公共 API | 高 | `airy_loop_create()` 含 @ownership/@threadsafe/@reentrant/@see |

### 5.7 不透明指针模式（PImpl）

| 类型 | 文件 | 模式 |
|------|------|------|
| `airy_sandbox_t` | airy_sandbox.h L51 | `typedef struct airy_sandbox airy_sandbox_t;` |
| `airy_mempool_t` | mempool.h L97 | `typedef struct airy_mempool airy_mempool_t;` |
| `airy_core_loop_t` | loop.h L34 | `typedef struct airy_core_loop airy_core_loop_t;` |
| `graph_engine_handle_t` | graph_engine.h L27 | `typedef struct graph_engine_s *graph_engine_handle_t;` |
| `pregel_engine_handle_t` | pregel_engine.h | 同上 |
| `taskflow_engine_t` | taskflow_advanced.h | 同上 |

### 5.8 指定初始化器（OS-STD-CODE-014 符合）

| 文件 | 行号 | 示例 |
|------|------|------|
| syscall_table.c | L54-78 | `[SYS_TASK_SUBMIT] = sys_task_submit, ...` |
| builtin_storage.c | L82 | `char tmp[AIRY_MAX_PATH_LEN] = {0};` |
| pregel_engine.c | L335 | `struct timespec ts = {.tv_nsec = 10000000};` |

### 5.9 编译期校验（_Static_assert）

| 文件 | 行号 | 校验内容 |
|------|------|----------|
| syscall_table.c | L21-24 | `SYS_TOOL_EXECUTE == 23` / `SYS_MAX == 24` |

### 5.10 C11 _Thread_local per-CPU 缓存

| 文件 | 行号 | 用法 |
|------|------|------|
| slab.c | L138 | `static _Thread_local slab_cpu_cache_t g_cpu_cache;` |

### 5.11 适配器模式（跨模块解耦）

| 适配器 | 文件 | 用途 |
|--------|------|------|
| `llm_svc_adapter_t` | coreloopthree | C-L02: llm_d → CoreLoopThree LLM 请求 IPC |
| `tool_svc_adapter_t` | coreloopthree | C-L04: tool_d → CoreLoopThree 工具执行 IPC |
| `memoryrovol_bridge_t` | coreloopthree | C-L12: MemoryRovol → CoreLoopThree 内存提供商桥接 |
| `airy_manager_adapter_t` | coreloopthree | C-L01: Manager → CoreLoopThree 配置管理 |
| `orch_adapter_t` | coreloopthree | C-L06: Orchestrator → CoreLoopThree 编排 |
| `airy_framework_adapter_t` | frameworks | 外部 AI 框架适配器（LangChain/AutoGPT 等） |

---

## 6. atoms 语义分类评估

### 6.1 A/B/C 三类语义分类清晰度

| 分类 | 模块 | 子模块 | 评估 |
|------|------|--------|------|
| A 类（微核心原语） | corekern | mem/task/ipc/time/observability/error/core_init | **清晰**：全部为底层原语，无业务语义 |
| B 类（应用语义层） | coreloopthree | cognition/execution/hook/memory/loop/orchestrator | **清晰**：三阶段认知循环业务逻辑 |
| B 类（应用语义层） | taskflow | graph_engine/pregel_engine/taskflow_advanced/workflow_patterns | **清晰**：任务流编排业务逻辑 |
| B 类（应用语义层） | syscall | sandbox/syscall_table/agent/skill/session/task/memory/telemetry | **清晰**：系统调用业务封装 |
| B 类（应用语义层） | memory | builtin_storage/builtin_index/builtin_provider/builtin_retrieval | **清晰**：内置记忆 provider 实现 |
| C 类（商业隔离层） | frameworks | airy_frameworks | **清晰**：外部 AI 框架桥接（LangChain 等商业生态） |
| 待定 | memoryrovol | airy_mr_force_includes.h（仅头） | **待澄清**：memoryrovol 实现散布在 coreloopthree/src/memory/，本身仅 force_includes 头，语义分类不明确 |

### 6.2 分类边界完整性

- **A 类边界**：corekern 仅依赖 commons（utils/platform/include），不依赖 B 类模块 — **边界清晰**
- **B 类边界**：coreloopthree 依赖 corekern（A 类）+ taskflow（B 类）+ memoryrovol_bridge — **依赖方向正确**（B → A）
- **C 类边界**：frameworks 仅提供适配器接口，不持有 A/B 类内部状态 — **边界清晰**

### 6.3 IRON-9 v2 层级标注

| 文件 | IRON-9 标注 | 示例 |
|------|-------------|------|
| cognition/engine.c | C-L01/C-L02/C-L04/C-L07/C-L09/C-L12 | L39/L43/L47/L50/L53/L56/L148/L163 |
| loop.c | C-L01/C-L02/C-L04/C-L06/C-L12 | L58/L71/L74/L77/L81 |
| taskflow_advanced.c | P0.18.2/P3.21 | L19/L44 |

> **评估**：IRON-9 v2 层级标注在 coreloopthree 中**完善**，但 corekern/taskflow/syscall 中**缺失**，建议补充。

---

## 7. taskflow 模块评估

### 7.1 双引擎层级符合性

| 引擎 | 类别 | 职责 | 评估 |
|------|------|------|------|
| scheduler（corekern/src/task/scheduler*.c） | A 类原语 | 线程管理、任务调度原语 | **符合历史决策** |
| taskflow_core.c | B 类编排 | 基础任务流 | **符合** |
| graph_engine.c | B 类编排 | 图存储与遍历（DAG） | **符合** |
| pregel_engine.c | B 类编排 | Pregel 超步计算模型 | **符合** |
| taskflow_advanced.c | B 类编排 | DAG 工作流（条件分支/并行汇聚/子工作流/循环/检查点） | **符合** |
| workflow_patterns.c | B 类编排 | 工作流模式（factory） | **符合** |

### 7.2 pregel_engine max_workers=1 强制降级（BAN-333）

**确认实现**：

| 文件 | 行号 | 代码 |
|------|------|------|
| pregel_engine.c | L359-367 | `if (engine->config.max_workers == 0) { engine->config.max_workers = 1; } else if (engine->config.max_workers > 1) { engine->config.max_workers = 1; // 强制降级 }` |
| pregel_engine.c | L526-527 | `/* BAN-333: 0.1.1 强制 max_workers=1 串行降级，默认 1 */ size_t num_workers = e->config.max_workers > 0 ? e->config.max_workers : 1;` |

**注释说明**（L359-362）：
> BAN-333: 0.1.1 强制 pregel_engine max_workers=1 串行降级。
> 默认 1 个工作线程；若调用方传入 >1 则强制降级为 1。
> 0.1.1 的 pregel_engine 并发路径尚未经过多线程验证，
> 强制串行模式以确保正确性优先于性能。

**评估**：**完全符合任务描述预期**。强制串行模式确保正确性优先于性能，0.1.1 版本的并发路径尚未验证。

### 7.3 双引擎协同方案

**协同点**：`coreloopthree/src/loop.c` L99
```c
/* W18: taskflow_advanced DAG 工作流引擎（用于复杂工作流编排） */
taskflow_engine_t *taskflow_engine;
```

**协同模式**：
- **scheduler（A 类原语）**：提供线程创建/调度原语（`airy_thread_create`/`airy_task_*`）
- **taskflow_advanced（B 类编排）**：在 loop 中作为字段嵌入，处理复杂工作流编排（DAG/条件分支/并行汇聚）
- **集成方式**：`loop.c` 通过 `taskflow_engine_t *taskflow_engine` 字段持有 taskflow_advanced 引擎，在主循环中调用 taskflow API

**评估**：**协同方案清晰**，A 类提供原语，B 类在其上构建编排，符合分层架构原则。

### 7.4 ASan 内存泄漏修复

**修复点**：`pregel_engine.c` L413-416
```c
/* workers 数组延迟到 pregel_engine_init 中分配。
 * 原实现在此处预分配 workers，随后 pregel_engine_init (L536) 会再次分配并覆盖指针，
 * 导致此处分配的 32 字节内存泄漏（ASan 检测到的 12 处 32B 泄漏根因）。
 * CALLOC 已将 workers 清零为 NULL，destroy 会对 NULL 安全跳过。 */
```

**评估**：**ASan 修复注释完善**，根因分析与修复方案明确。

---

## 8. 改进建议（按优先级分级）

### 8.1 P0（Critical，阻断发布）

| 编号 | 建议 | 影响范围 | 工作量估算 |
|------|------|----------|------------|
| P0-1 | **全量替换 4 空格缩进为 Tab 8 字符**：配置 `.clang-format`（`IndentWidth: 8` / `TabWidth: 8` / `UseTab: Always`），运行 `make format` 自动化 | 237 文件全量 | 大（自动化可降低） |
| P0-2 | **修复 5901 处 80+ 列超长行**：按"对齐到开括号"风格折行，禁止折断用户可见字符串 | 全 atoms | 大 |
| P0-3 | **审查 AIRY_ERROR_NULL/AIRY_ERROR/AIRY_RET_ERR 宏行为**：确认宏是否 `return`。若不 return，pregel_engine.c L200-201/L288-289 等存在 NULL deref 风险，需立即修复 | pregel_engine.c / loop.c / scheduler.c / taskflow_advanced.c | 中 |

### 8.2 P1（High，下个迭代修复）

| 编号 | 建议 | 影响范围 | 工作量估算 |
|------|------|----------|------------|
| P1-1 | **移除 120 文件中的 ASCII 装饰分节符**：替换为简洁的单行注释（如 `/* 内存管理 */`）或删除 | 120 文件 | 中 |
| P1-2 | **重构 114+ 处匿名 struct typedef 为 `struct xxx { ... };` 形式**：OS-STD-CODE-020 要求结构体以 `struct foo` 形式声明与使用 | mempool.h / frameworks.h / pregel_engine.c / slab.c / taskflow_advanced.c 等 | 大 |
| P1-3 | **替换结构体中的 bool 字段为 uint8_t 或位域**：OS-STD-011 要求 bool 仅用于返回值与栈变量。slab.c/mempool.h/frameworks.h/pregel_engine.c 等需修改 | 30+ 处 | 中 |
| P1-4 | **移除 #pragma diagnostic 警告抑制**：scheduler.c L62-70 用 `__attribute__((used))` 替代 `#pragma GCC diagnostic ignored "-Wunused-function"`，或将未使用函数删除 | scheduler.c | 小 |
| P1-5 | **统一错误处理为 goto 集中出口**：用 `goto out_xxx:` 替代 AIRY_ERROR/AIRY_ERROR_NULL/AIRY_RET_ERR 宏的隐式 return，使控制流显式可见 | 100+ 处 | 大 |
| P1-6 | **补充 corekern/taskflow/syscall 的 IRON-9 v2 层级标注**：参照 coreloopthree 的 C-Lxx 标注模式 | corekern / taskflow / syscall 公共头 | 中 |

### 8.3 P2（Medium，长期改进）

| 编号 | 建议 | 影响范围 | 工作量估算 |
|------|------|----------|------------|
| P2-1 | **完善公共 API 的 kernel-doc 注释**：graph_engine 系列函数补充 @return/@threadsafe/@reentrant | graph_engine.h / pregel_engine.h / taskflow_advanced.h | 中 |
| P2-2 | **移除冗余 void* 强制转换**：pregel_engine.c 等 20+ 处 `(message_queue_t *)AIRY_CALLOC(...)` 改为 `AIRY_CALLOC(...)`（C 自动转换） | pregel_engine.c 等 | 小 |
| P2-3 | **将相对路径 `#include "../../../commons/..."` 改为 -I 配置**：error.h L20/L23、task.h L25/L27 等改为 `#include <airy_types.h>` 形式 | corekern 公共头 | 小 |
| P2-4 | **修复 syscall_table.c L28 注释编码错误**：`/* 函数声明（实现位?syscall_entry.c?*/` 中 `?` 应为「于」 | syscall_table.c | 极小 |
| P2-5 | **明确 memoryrovol 模块语义分类**：当前仅含 force_includes 头，实现散布在 coreloopthree/src/memory/。建议在 README 中明确"memoryrovol 为契约层，实现在 coreloopthree/memory" | memoryrovol/README.md | 小 |
| P2-6 | **统一函数定义开括号位置**：少数函数（如 `if (!engine) return NULL;` 单行）拆分为多行，提升可读性 | taskflow_advanced.c L73 等 | 小 |
| P2-7 | **CRC32 查表折行处理**：are_ipc.c L45-60 每行 16 个 hex 值（211 列）应折为每行 8 个值（约 105 列，仍超 80 但可接受为查表例外，或改用脚本生成） | are_ipc.c | 小 |

### 8.4 保持的技术亮点（应保留）

| 编号 | 亮点 | 评估 |
|------|------|------|
| K-1 | C11 显式内存序（atomic + memory_order_*） | **优秀**，继续保留 |
| K-2 | 跨平台 compat 层（memory/string/atomic/sync/logging/error/platform） | **优秀**，继续保留 |
| K-3 | 编译时 const 查表技术（CRC32 / primes / error_strings） | **优秀**，继续保留 |
| K-4 | 双重检查锁定 + 状态机（core_init.c） | **优秀**，继续保留 |
| K-5 | _Thread_local per-CPU 缓存（slab.c） | **优秀**，继续保留 |
| K-6 | 纯函数设计（are_crc32_update / airy_strerror） | **优秀**，继续保留 |
| K-7 | Doxygen 文档完善（公共 API 含 @ownership/@threadsafe/@reentrant） | **优秀**，继续保留 |
| K-8 | 不透明指针模式（PImpl） | **优秀**，继续保留 |
| K-9 | 指定初始化器（syscall_table.c 等） | **优秀**，继续保留 |
| K-10 | _Static_assert 编译期校验（syscall_table.c） | **优秀**，继续保留 |
| K-11 | 适配器模式（6 个适配器解耦 coreloopthree） | **优秀**，继续保留 |
| K-12 | BORROW 所有权语义显式标注 | **优秀**，继续保留 |
| K-13 | pregel_engine max_workers=1 强制串行（BAN-333） | **优秀**，正确性优先于性能 |
| K-14 | ASan 内存泄漏修复注释 | **优秀**，根因分析完善 |
| K-15 | 函数前缀边界清晰（airy_* / agentrt_* / agentos_* / airymaxos_*） | **优秀**，零违规 |

---

## 9. 审查结论

### 9.1 总体评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 架构设计 | A | A/B/C 三类语义清晰，分层正确，适配器模式解耦优秀 |
| 技术实现 | A- | C11 atomic / 编译时查表 / DCLP / _Thread_local 等技术亮点突出 |
| 工程标准合规 | C+ | Tab 缩进 / 80 列 / typedef / bool / 装饰分节符 等违规普遍 |
| 函数前缀边界 | A+ | 零 `agentrt_*`/`agentos_*`/`airymaxos_*` C 标识符，`airy_*` 边界清晰 |
| 文档完善度 | B+ | Doxygen 公共 API 完善，但 IRON-9 v2 标注在部分模块缺失 |
| 安全性 | B | sandbox 三层拦截（permission/quota/audit）设计优秀，但 AIRY_ERROR_NULL 控制流不透明存在 NULL deref 风险 |

### 9.2 关键风险

1. **P0-3（NULL deref 风险）**：pregel_engine.c 多处 `AIRY_ERROR_NULL(...)` 后直接解引用指针，若宏不 return 则存在 NULL deref。**需立即审查宏定义**。
2. **P0-1（缩进违规）**：237 文件全量 4 空格缩进，与 OLK-6.6 基线（Tab 8）严重背离。需 `.clang-format` 自动化修复。
3. **P1-5（控制流不透明）**：AIRY_ERROR 系列宏替代 goto 集中出口，使错误处理路径不可见，维护性差。

### 9.3 优先行动项

1. **立即**（P0）：审查 AIRY_ERROR_NULL 宏定义，确认是否 return；若不 return，修复 pregel_engine.c NULL deref
2. **本迭代**（P0-P1）：配置 `.clang-format`，自动化修复缩进与 80 列违规
3. **下迭代**（P1）：移除装饰分节符，重构匿名 struct typedef，统一 goto 错误处理
4. **长期**（P2）：完善 kernel-doc，补充 IRON-9 v2 标注，明确 memoryrovol 语义分类

---

## 附录 A：审查工具与方法

- **文件映射**：Glob + LS + find 统计 .c/.h 文件数
- **深读**：Read 工具逐文件读取代表性源码（15+ 文件）
- **违规验证**：Grep 工具按规则模式扫描（Tab/4 空格/typedef/装饰分节符/前缀/超长行/atomic/_Thread_local）
- **基线对照**：`docs/AirymaxOS/50-engineering-standards/10-coding-style/C_Cpp_coding_style.md`（OLK-6.6 六大支柱）
- **行号精度**：所有违规结论均附具体文件路径与行号

## 附录 B：未深读但已扫描的文件清单

以下文件已通过 Grep 扫描验证违规规模，但未逐一深读：
- corekern/src/mem/arena.c / mempool.c / tcache.c / pool.c / alloc.c / guard.c / refcount.c / oom_handler.c
- corekern/src/task/thread.c / scheduler_core.c / scheduler_posix.c / scheduler_windows.c / scheduler_platform.c
- corekern/src/ipc/buffer.c / binder.c
- corekern/src/time/clock.c / timer.c
- corekern/src/observability/observability.c
- coreloopthree/src/cognition/*（30+ 文件）
- coreloopthree/src/execution/*（10+ 文件）
- coreloopthree/src/hook/*（9 文件）
- coreloopthree/src/memory/*（3 文件）
- syscall/src/sandbox.c / sandbox_permission.c / sandbox_quota.c / sandbox_utils.c / rate_limiter.c / circuit_breaker.c / telemetry.c / session.c / agent.c / skill.c / task.c / memory.c / syscall_entry.c
- taskflow/src/taskflow_core.c / taskflow_execution_unit.c / workflow_patterns.c
- memory/src/builtin_index.c / builtin_provider.c / builtin_retrieval.c
- frameworks/src/airy_frameworks.c

## 附录 C：术语对照

| 术语 | 定义 |
|------|------|
| OLK-6.6 | Linux 6.6 内核基线编码风格（agent-linux 工程标准基线） |
| IRON-9 v2 | agentrt 三层模型（[SC] 共享契约层 / [SS] 语义同源层 / [IND] 完全独立层） |
| A 类 | 微核心原语（corekern） |
| B 类 | 应用语义层（coreloopthree/taskflow/syscall/memory） |
| C 类 | 商业隔离层（frameworks） |
| DCLP | Double-Checked Locking Pattern（双重检查锁定模式） |
| BAN-333 | pregel_engine max_workers=1 强制串行降级规则 |
| ASan | AddressSanitizer 内存错误检测器 |
| SSoT | Single Source of Truth（单一真值源） |

---

**报告结束**

> 本报告所有结论均有具体文件路径与行号证据支撑，可通过 Grep/Read 工具复核。
> 审查基线版本：atoms 模块当前 HEAD（含 P3.18/P3.21/P0.20.6/P0.20.7 等迭代标记）。
> 审查日期：2026-07-13。
