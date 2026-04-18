# AgentOS 详细问题清单 v13.0.0

> **版本**: 13.0.0-生产级穷尽问题追踪与团队分工版
> **日期**: 2026-04-19
> **状态**: ⚠️ **68+处桩函数待清除** + **Phase 2-4完全缺失** + **测试覆盖率0%** + **双思考系统仅40-50%**
> **核心理念**: 穷尽式逐文件审查，绝不流于形式！**扫描范围必须覆盖全项目！严禁任何桩函数！**
> **关联文档**: [主报告v22.0](./AgentOS全面修复与改进报告07.md) | [规范手册v12.0](./AgentOS工程规范化标准手册07.md) | [看板v13.0](./AgentOS三团队任务进度看板07.md) | [桩函数穷尽检查报告](./AgentOS桩函数穷尽检查报告.md) | [可行性评估报告](./AgentOS三大设计文档全面可行性评估报告.md) | [深度推理分析](./AgentOS三大设计文档深度推理分析报告.md)

---

## 📋 目录

1. [问题总览与统计](#问题总览与统计)
2. [🔴 STUB类: 桩函数/简化实现违规(SEC-017)](#stub类桩函数简化实现违规)
3. [🔴 DS类: 双思考系统核心功能缺失](#ds类双思考系统核心功能缺失)
4. [🟠 MR类: MemoryRovol实现差距](#mr类memoryrovol实现差距)
5. [🟡 HIST类: 历史遗留问题](#hist类历史遗留问题)
6. [🟡 TGT类: 设计目标偏差](#tgt类设计目标偏差)
7. [🟢 PROTO类: 协议系统已知限制](#proto类协议系统已知限制)
8. [模块级问题分布](#模块级问题分布)
9. [团队分工矩阵](#团队分工矩阵)
10. [修复优先级与依赖关系](#修复优先级与依赖关系)
11. [安全漏洞清单](#安全漏洞清单)
12. [修复历史记录](#修复历史记录)

---

## 问题总览与统计

### 📊 六类问题统计摘要（截至2026-04-19 穷尽全源码审查后）

| 问题类别 | 问题数 | P0致命 | P1严重 | P2中等 | P3低 | 已修复 | 负责团队 |
|----------|--------|--------|--------|--------|------|--------|----------|
| **STUB: 桩函数违规** | 5 | 3 | 2 | 0 | 0 | ❌ 0/5 | 团队A |
| **DS: 双思考系统** | 8 | 2 | 4 | 2 | 0 | ❌ 0/8 | 团队A |
| **MR: MemoryRovol** | 7 | 0 | 3 | 3 | 1 | ❌ 0/7 | 团队A |
| **HIST: 历史遗留** | 8 | 1 | 3 | 3 | 1 | 🔶 2/8 | 全团队 |
| **TGT: 设计目标偏差** | 3 | 0 | 0 | 3 | 0 | ❌ 0/3 | 全团队 |
| **PROTO: 协议限制** | 5 | 0 | 0 | 3 | 2 | ❌ 0/5 | 团队B |
| **总计** | **36** | **6** | **12** | **14** | **4** | **2/36** | - |

### 📊 按严重程度统计

| 严重程度 | 数量 | 占比 | 问题ID列表 | 目标状态 |
|----------|------|------|-----------|----------|
| **🔴 P0 致命** | **6** | 17% | STUB-01/02/03, DS-001/008, HIST-005 | 必须清零 |
| **🟠 P1 严重** | **12** | 33% | STUB-04/05, DS-002/003/006/007, MR-001/002/004, HIST-002/003/008 | <3 |
| **🟡 P2 中等** | **14** | 39% | DS-004/005, MR-003/005/006, HIST-001/004/006/007, TGT-001/002/003, PROTO-001/003/004 | <10 |
| **🟢 P3 低** | **4** | 11% | MR-007, PROTO-002/005, HIST-007(部分) | 可接受 |

### 📊 按负责团队统计

| 团队 | 负责问题数 | P0 | P1 | P2 | P3 | 工作量估算 |
|------|-----------|-----|-----|-----|-----|-----------|
| **团队A(核心内核)** | 20 | 5 | 8 | 5 | 2 | ~14周 |
| **团队B(安全服务)** | 5 | 0 | 0 | 3 | 2 | ~4周 |
| **团队C(守护网关)** | 0 | 0 | 0 | 0 | 0 | 已清零(daemon范围) |
| **全团队协同** | 11 | 1 | 4 | 6 | 0 | ~8周 |

### 🎯 关键成就与核心问题

```
✅ 编译100%通过（连续17轮验证）
✅ 安全漏洞6个全部修复（CVSS 5.5-9.8）
✅ 团队C daemon/gateway桩函数清零（30→0）
✅ 协议系统186项测试100%通过

🔴🔴🔴 核心阻塞问题：
   1. 68+桩函数违规(STUB-01~05) → 核心功能(LLM/向量存储/ML)完全不可用
   2. 双思考系统Phase 2-4完全缺失(DS-001~008) → 核心理论优势未实现
   3. MemoryRovol L3/L4实现不完整(MR-001~007) → 因果链/规则注入不可用
   4. 测试覆盖率0%(HIST-005) → 无法验证任何功能正确性
   5. 设计目标偏差(TGT-001~003) → 准确率99%不可达，实际85-90%
```

---

## STUB类: 桩函数/简化实现违规

> **来源**: [AgentOS桩函数穷尽检查报告](./AgentOS桩函数穷尽检查报告.md)
> **核心原则**: SEC-017严禁任何桩函数！编译通过≠功能正常！

### STUB-01: curl_stub.h - 完整假libcurl API头文件 🔴 P0致命

| 属性 | 值 |
|------|-----|
| **问题ID** | STUB-01 |
| **文件路径** | `agentos/atoms/memoryrovol/include/curl_stub.h` |
| **桩函数数量** | 25个 |
| **严重程度** | 🔴 P0 致命 |
| **负责团队** | 团队A (memoryrovol) |
| **影响功能** | LLM客户端(llm_client.c)完全不可用 → 整个双思考系统无法调用LLM |
| **当前状态** | ❌ 待清除 |

#### 详细代码

```c
/* curl_stub.h - 完整的假libcurl API */
typedef void CURL;                                    // 假类型定义
typedef int CURLcode;                                 // 假类型定义
typedef struct curl_slist { } curl_slist_t;            // 空结构体

#define CURLE_OK 0
#define CURLE_FAILED_INIT 2

static inline CURL* curl_easy_init(void) { return NULL; }
static inline CURLcode curl_easy_setopt(CURL *curl, ...) { return CURLE_FAILED_INIT; }
static inline CURLcode curl_easy_perform(CURL *curl) { return CURLE_FAILED_INIT; }
static inline void curl_easy_cleanup(CURL *curl) { (void)curl; }
static inline char* curl_easy_strerror(CURLcode code) { return "stub error"; }
// ... 还有20个类似的假函数
```

#### 影响链路

```
llm_client.c 初始化时:
  #ifdef AGENTOS_HAS_CURL
    #include <curl/curl.h>     // ← 真实libcurl
  #else
    #include "curl_stub.h"     // ← 假API！(当系统没装libcurl时走这里)
  #endif

结果:
  curl = curl_easy_init();     // 返回 NULL (来自stub)
  if (!curl) {
    // 进入"degraded mode"(STUB-04)
    service->initialized = 1; // 标记为已初始化！
    *out_service = service;   // 返回成功！
    return AGENTOS_SUCCESS;   // 但实际上什么都没做！
  }
```

#### 清除方案

| 方案 | 描述 | 优点 | 缺点 | 推荐度 |
|------|------|------|------|--------|
| **A: 安装libcurl-dev** | 确保AGENTOS_HAS_CURL定义，使用真实API | 彻底解决，功能完整 | 增加构建依赖 | ⭐⭐⭐⭐⭐ |
| B: 移除LLM功能 | 如果不需要LLM，移除llm_client.c | 简化系统 | 丧失核心功能 | ⭐ |
| **禁止** | 保留curl_stub.h作为生产代码 | - | 违反SEC-017 | ❌ |

#### 验收标准

- `find agentos/ -name "*stub*.h"` 返回0
- `cmake --build . -j$(nproc)` 编译0错误
- `llm_client_create()` 返回真正可用的LLM服务
- 端到端测试：LLM调用返回真实响应

---

### STUB-02: sqlite3_stub.h - 完整假SQLite3 API头文件 🔴 P0致命

| 属性 | 值 |
|------|-----|
| **问题ID** | STUB-02 |
| **文件路径** | `agentos/atoms/memoryrovol/include/sqlite3_stub.h` |
| **桩函数数量** | 30+个 |
| **严重程度** | 🔴 P0 致命 |
| **负责团队** | 团队A (memoryrovol) |
| **影响功能** | 向量存储(vector_store.c)完全不可用 → MemoryRovol L2检索不可用 |
| **当前状态** | ❌ 待清除 |

#### 详细代码

```c
/* sqlite3_stub.h - 完整的假SQLite3 API */
typedef struct sqlite3 sqlite3;

#define SQLITE_OK 0
#define SQLITE_ERROR 1
#define SQLITE_NOMEM 7

static inline int sqlite3_open(const char *filename, sqlite3 **ppDb) {
    return SQLITE_NOMEM;  // 永远内存不足
}
static inline int sqlite3_exec(sqlite3*, const char*, ...) {
    return SQLITE_ERROR;  // 永远执行失败
}
static inline int sqlite3_prepare_v2(...) { return SQLITE_ERROR; }
static inline int sqlite3_step(sqlite3_stmt*) { return SQLITE_ERROR; }
static inline const char* sqlite3_errmsg(sqlite3*) { return "stub error"; }
// ... 还有26+个类似的假函数
```

#### 影响链路

```
vector_store.c 使用向量数据库时:
  #ifdef AGENTOS_HAS_SQLITE3
    #include <sqlite3.h>         // ← 真实SQLite3
  #else
    #include "sqlite3_stub.h"    // ← 假API！
  #endif

结果:
  rc = sqlite3_open(db_path, &db);  // 返回 SQLITE_NOMEM
  // 向量存储功能完全不可用，但可能被上层静默忽略
```

#### 清除方案

| 方案 | 描述 | 优点 | 缺点 | 推荐度 |
|------|------|------|------|--------|
| **A: 安装sqlite3-dev** | 使用真实SQLite3 API | 彻底解决 | 增加构建依赖 | ⭐⭐⭐⭐⭐ |
| B: 纯内存实现 | 改用内存哈希表替代SQLite | 无外部依赖 | 持久化缺失 | ⭐⭐⭐ |
| **禁止** | 保留sqlite3_stub.h | - | 违反SEC-017 | ❌ |

#### 验收标准

- `find agentos/ -name "*stub*.h"` 返回0
- `sqlite3_open()` 成功创建数据库文件
- 向量存储CRUD操作端到端可用

---

### STUB-03: ml_planner.c - PHASE2-IMPLEMENTED ML推理管道 🔴 P0致命

| 属性 | 值 |
|------|-----|
| **问题ID** | STUB-03 |
| **文件路径** | `agentos/atoms/coreloopthree/src/cognition/planner/ml_planner.c` |
| **涉及行号** | 68-88, 184-197 |
| **桩函数数量** | 1处(多行逻辑) |
| **严重程度** | 🔴 P0 致命 |
| **负责团队** | 团队A (coreloopthree) |
| **影响功能** | ML规划器永远无法进行真实ML推理 → 双思考系统Phase 1规划能力缺失 |
| **当前状态** | ❌ 待实现 |

#### 详细代码

```c
/* ml_planner.c:68-88 - 模型初始化 */
static agentos_error_t ml_planner_init(ml_planner_t* planner, const config_t* cfg) {
    ml_planner_data_t* data = calloc(1, sizeof(ml_planner_data_t));
    if (!data) return AGENTOS_ERR_NO_MEMORY;

    /* PHASE2-IMPLEMENTED: ML model initialization with placeholder */
    data->model = NULL;              // ← 模型永远不被加载！
    data->fallback_mode = true;       // ← 永远标记为fallback模式！

    planner->data = data;
    return AGENTOS_SUCCESS;           // 返回成功，但模型是空的
}

/* ml_planner.c:184-194 - 推理管道 */
static agentos_error_t ml_planner_inference(ml_planner_t* planner, ...) {
    ml_planner_data_t* data = planner->data;

    if (data->model && !data->fallback_mode) {
        /* PHASE2-IMPLEMENTED: ML inference pipeline stub */
        AGENTOS_LOG_DEBUG("ML planner: executing inference pipeline (placeholder)");
        // ← 就这一行日志？没有真正的ML推理算法！
    }

    // 总是走到这里
    return ml_planner_fallback_plan(intent, out_plan);  // ← 永远用启发式替代
}
```

#### 问题分析

- `data->model` 永远是NULL（初始化时就设为NULL）
- `data->fallback_mode` 永远是true
- if条件永远不进入真正的ML推理分支
- 整个ML规划器的"ML"部分是假的，实际只是启发式规则引擎

#### 清除方案

| 方案 | 描述 | 工作量 | 推荐度 |
|------|------|--------|--------|
| **A: 实现真实ML推理管道** | 加载预训练模型+特征提取+推理+输出解码 | 4-6周 | ⭐⭐⭐⭐⭐ |
| B: 连接外部ML服务 | 通过HTTP API调用外部ML推理服务 | 2-3周 | ⭐⭐⭐⭐ |
| C: 集成本地7B模型 | 使用ONNX Runtime加载Phi-3/Qwen2.5 | 3-4周 | ⭐⭐⭐⭐ |

#### 验收标准

- `data->model` 不再是NULL
- `data->fallback_mode` 初始为false
- ML推理管道产生与fallback不同的输出
- 端到端测试：ML规划器能根据任务特征选择最优策略

---

### STUB-04: llm_client.c - Degraded Mode返回假数据 🟠 P1严重

| 属性 | 值 |
|------|-----|
| **问题ID** | STUB-04 |
| **文件路径** | `agentos/atoms/memoryrovol/src/llm_client.c` |
| **涉及行号** | 149-158, 185-201, 271-276 |
| **桩函数数量** | 12处(含cJSON桩) |
| **严重程度** | 🟠 P1 严重 |
| **负责团队** | 团队A (memoryrovol) |
| **影响功能** | LLM客户端在无libcurl时假装成功 → 上层基于假数据做决策 |
| **当前状态** | ❌ 待修复 |
| **依赖** | 依赖STUB-01的修复 |

#### 详细代码

```c
/* llm_client.c:149-158 - 初始化时的degraded mode */
agentos_error_t llm_client_create(/* ... */) {
    llm_service_t* service = calloc(1, sizeof(llm_service_t));
    if (!service) return AGENTOS_ERR_NO_MEMORY;

    CURL* curl = curl_easy_init();  // 来自curl_stub.h，返回NULL

    if (!curl) {  // ← 总是进入这个分支
        service->initialized = 1;     // 假装初始化成功
        *out_service = service;       // 返回service对象
        return AGENTOS_SUCCESS;       // 返回成功！（但LLM功能不可用）
    }
}

/* llm_client.c:185-201 - 调用LLM时的degraded mode */
agentos_error_t llm_client_chat(llm_service_t* svc, ...) {
    if (!svc->curl_handle) {  // ← 总是true
        resp->text = AGENTOS_STRDUP("LLM service unavailable (degraded mode)");
        resp->status = 200;     // 假HTTP状态码
        resp->finish_reason = "stop";
        return AGENTOS_SUCCESS;  // 返回成功！但数据是假的
    }
}
```

#### 额外问题: cJSON桩实现

```c
#ifdef AGENTOS_HAS_CJSON
#include <cjson/cJSON.h>
#else
typedef struct cJSON { ... } cJSON;  // 假类型定义
static inline cJSON* cJSON_CreateObject(void) { return NULL; }  // 永远返回NULL
// ... 12个cJSON函数全是桩
#endif
```

#### 清除方案

1. 安装libcurl-dev后，degraded mode分支永远不会进入
2. 但仍需修改：当libcurl不可用时，应返回`AGENTOS_ERR_NOT_AVAILABLE`而非假SUCCESS
3. 安装cjson-dev，确保`AGENTOS_HAS_CJSON`定义
4. 涉及7个文件的cJSON条件桩全部需要处理

#### 验收标准

- 无libcurl时返回明确错误码`AGENTOS_ERR_NOT_AVAILABLE`
- 有libcurl时LLM调用返回真实响应
- cJSON使用真实库而非桩实现

---

### STUB-05: config_service.c - Simplified Version硬编码 🟠 P1严重

| 属性 | 值 |
|------|-----|
| **问题ID** | STUB-05 |
| **文件路径** | `agentos/commons/utils/config_unified/src/config_service.c` |
| **涉及行号** | 900-916 |
| **桩函数数量** | 1处 |
| **严重程度** | 🟠 P1 严重 |
| **负责团队** | 团队A (commons) |
| **影响功能** | 配置版本比较功能不可用 → 配置升级检测不可靠 |
| **当前状态** | ❌ 待实现 |

#### 详细代码

```c
config_error_t config_version_diff(config_manager_t* manager,
                                const char* version1,
                                const char* version2,
                                char* diff,
                                size_t diff_size) {
    (void)manager;
    (void)version1;
    (void)version2;  // ← 所有参数被忽略！

    if (diff && diff_size > 0) {
        const char* msg = "Version diff not implemented in simplified version";
        size_t len = strlen(msg);
        if (len >= diff_size) len = diff_size - 1;
        memcpy(diff, msg, len);
        diff[len] = '\0';
        return len;
    }
    return 0;
}
```

#### 清除方案

1. 实现真实语义化版本比较（SemVer解析：major.minor.patch）
2. 实现字段级别diff（新增/删除/修改的配置项）
3. 输出结构化的差异报告

#### 验收标准

- `config_version_diff("1.0.0", "1.1.0", ...)` 返回有意义的差异
- 不再返回"simplified version"字符串

---

## DS类: 双思考系统核心功能缺失

> **来源**: [双思考系统全方位设计01.md](../../.vscode/双思考系统全方位设计01.md) + [第5轮战略级深度验证报告](./历史档案/检查报告/AgentOS第5轮战略级深度验证报告.md) + [三大设计文档深度推理分析报告](./AgentOS三大设计文档深度推理分析报告.md)
> **核心原则**: 双思考系统是AgentOS区别于其他Agent框架的核心理论优势，必须完整实现！

### 双思考系统五阶段实现状态总览

| Phase | 功能名称 | 实现度 | 状态 | 对应问题ID | 关键缺失 |
|-------|---------|--------|------|-----------|----------|
| **Phase 0** | 指令拆解(S1) | 85% | ✅ 基本完整 | DS-007 | 缺MemoryRovol L3交互 |
| **Phase 1** | 规划(S2+S1预验证) | 75% | ✅ 部分实现 | DS-006 | DAG计划不完整，缺审计委员会 |
| **Phase 2** | 流式批判循环 | **0%** | ❌ **未实现** | DS-001 | 无token级实时验证代码 |
| **Phase 3** | 审计委员会 | **0%** | ❌ 未实现 | DS-002/003 | 缺辩论机制和漂移检测 |
| **Phase 4** | 目标对齐 | **0%** | ❌ 未实现 | DS-004/005 | 完全未实现 |
| **全局** | 流程编排器 | **0%** | ❌ 未实现 | DS-008 | Phase 0-4串联调度不存在 |

### DS-001: 流式批判循环 🔴 P0致命

| 属性 | 值 |
|------|-----|
| **问题ID** | DS-001 |
| **所属Phase** | Phase 2 |
| **严重程度** | 🔴 P0 致命 |
| **负责团队** | 团队A |
| **影响** | 整个双思考系统失去核心价值，无法实现token级实时错误拦截 |
| **实现难度** | ⭐⭐⭐⭐⭐ (最高) |
| **当前状态** | ❌ 完全未实现 |

#### 设计要求（来自双思考系统设计文档）

```
S2每15 token生成后:
  1. S1实时阅读token块，检测不合理
  2. 合理? → 继续
  3. 不合理 → S2局部修正(仅重写错误块)
  4. 专业S1交叉验证修正结果
  5. 修正失败3次 → 记录错误+请求人工介入
```

#### 设计文档中的Python伪代码

```python
def streaming_critique(prompt, s2, s1, s1_expert, memory):
    full_output = []
    buffer = []
    token_count = 0
    step = 0

    for token in s2.stream(prompt):
        buffer.append(token)
        token_count += 1
        full_output.append(token)

        if token_count % 15 == 0 or token in ['.', '!', '?', '\n', ';']:
            chunk = ''.join(buffer)
            is_ok, critique = s1.check(chunk, context=prompt, history=full_output)
            if not is_ok:
                correction_attempts = 0
                while correction_attempts < 3:
                    corrected = s2.correct(chunk, critique, context=prompt)
                    if s1_expert.verify(corrected, chunk, critique):
                        buffer = [corrected]
                        full_output[-len(chunk):] = list(corrected)
                        break
                    correction_attempts += 1
                else:
                    memory.store_error(chunk, critique)
                    raise TaskError("Unresolvable error in reasoning")
            yield ''.join(buffer)
            buffer = []
            token_count = 0
            step += 1

            if step % 10 == 0:
                similar_context = memory.retrieve_similar(''.join(full_output[-300:]))
                if similar_context:
                    s2.inject_context(similar_context)
```

#### 需要实现的C代码模块

| 模块 | 功能 | 预估代码量 | 依赖 |
|------|------|-----------|------|
| `streaming_critique.c` | 流式批判主循环 | 500+行 | STUB-01/04(需真实LLM) |
| `s1_validator.c` | S1快速验证器 | 300+行 | MR-002(L4规则注入) |
| `s2_corrector.c` | S2局部修正器 | 300+行 | STUB-01(需真实LLM) |
| `s1_expert.c` | 专业S1交叉验证 | 200+行 | 领域模型集成 |
| `critique_buffer.c` | Token缓冲区管理 | 150+行 | 无 |

#### 三方案对比（来自主报告v22.0）

| 方案 | 描述 | 延迟 | 准确率贡献 | 推荐度 |
|------|------|------|-----------|--------|
| **A: 异步流水线** | S2持续生成→后台批量检查→延迟修正 | 500-2000ms | +10% | ⭐⭐⭐ |
| **B: 本地轻量S1** | 使用7B参数本地模型(Phi-3/Qwen2.5) | 50-100ms | +12% | ⭐⭐⭐⭐ |
| **C: 混合检查策略** | 前100token不检查→中间30-50token检查→关键节点强制检查 | 100-300ms | +15% | ⭐⭐⭐⭐⭐ |

#### 实施前置条件

1. ✅ STUB-01必须先清除（需要真实LLM调用能力）
2. ✅ STUB-04必须先修复（需要LLM返回真实数据）
3. ⚠️ 需要先进行PoC验证（方案C优先）

---

### DS-002: 子任务审计委员会 🟠 P1严重

| 属性 | 值 |
|------|-----|
| **问题ID** | DS-002 |
| **所属Phase** | Phase 3 |
| **严重程度** | 🟠 P1 严重 |
| **负责团队** | 团队A |
| **影响** | 无法对子任务结果进行交叉验证，错误可能在子任务间传播 |
| **实现难度** | ⭐⭐⭐⭐ |
| **当前状态** | ❌ 完全未实现 |

#### 设计要求

```
每个子任务完成后:
  1. S2总结子任务结果
  2. S1+专业S1交叉验证（两个模型独立验证）
  3. 若结论一致 → 通过
  4. 若不一致 → 启动辩论（最多2轮，审计委员会仲裁）
  5. 记录到MemoryRovol L1/L2
```

#### 需要实现的C代码模块

| 模块 | 功能 | 预估代码量 |
|------|------|-----------|
| `audit_committee.c` | 审计委员会主逻辑 | 400+行 |
| `debate_engine.c` | 多模型辩论引擎 | 300+行 |
| `arbitrator.c` | 仲裁器（替代当前简单权重选择） | 200+行 |

#### 与DS-006的关系

当前`arbiter.c`只有简单权重选择（~50行），DS-002需要将其替换为真正的交叉验证+辩论+仲裁机制。

---

### DS-003: 任务漂移检测 🟠 P1严重

| 属性 | 值 |
|------|-----|
| **问题ID** | DS-003 |
| **所属Phase** | Phase 3 |
| **严重程度** | 🟠 P1 严重 |
| **负责团队** | 团队A |
| **影响** | 无法检测子任务执行是否偏离原始目标 |
| **实现难度** | ⭐⭐⭐ |
| **当前状态** | ❌ 完全未实现 |

#### 设计要求

```
子任务完成后:
  1. 将子任务结果与原始目标对比
  2. 计算语义相似度
  3. 相似度 < 阈值(0.7) → 触发重新规划
  4. 记录漂移事件到MemoryRovol L1
```

#### 依赖

- MR-001: 需要L3因果链编码支持目标追溯
- DS-001: 需要流式批判提供token级验证

---

### DS-004: 目标对齐检查 🟡 P2中等

| 属性 | 值 |
|------|-----|
| **问题ID** | DS-004 |
| **所属Phase** | Phase 4 |
| **严重程度** | 🟡 P2 中等 |
| **负责团队** | 团队A |
| **影响** | 无法防止长期任务发生目标漂移 |
| **实现难度** | ⭐⭐⭐ |
| **当前状态** | ❌ 完全未实现 |

#### 设计要求

```python
def alignment_check(memory, s2, original_goal, last_hour_tokens):
    tokens = memory.get_tokens(last_hour_tokens)
    summary = s2.summarize(tokens)
    similarity = compute_semantic_similarity(summary, original_goal)
    if similarity < 0.7:
        return False, summary  # 触发重新规划
    return True, summary
```

---

### DS-005: 定期进度摘要 🟡 P2中等

| 属性 | 值 |
|------|-----|
| **问题ID** | DS-005 |
| **所属Phase** | Phase 4 |
| **严重程度** | 🟡 P2 中等 |
| **负责团队** | 团队A |
| **影响** | 无法生成任务进度摘要供目标对齐使用 |
| **实现难度** | ⭐⭐⭐ |
| **当前状态** | ❌ 完全未实现 |

#### 设计要求

- S2每小时生成进度摘要
- 摘要写入MemoryRovol L2
- 摘要供DS-004目标对齐检查使用

---

### DS-006: dual_model.c深度不足 🟠 P1严重

| 属性 | 值 |
|------|-----|
| **问题ID** | DS-006 |
| **所属Phase** | Phase 1 |
| **严重程度** | 🟠 P1 严重 |
| **负责团队** | 团队A |
| **影响** | 双模型只是简单权重选择，非真正交叉验证 |
| **实现难度** | ⭐⭐⭐⭐ |
| **当前状态** | ❌ 需重写 |

#### 当前实现问题（第5轮验证报告确认）

```c
// arbiter.c 的"仲裁"逻辑：
static double arbiter_weighted_vote(arbiter_t* arbiter, model_output_t** outputs, int count) {
    double total_weight = 0;
    double result = 0;
    for (int i = 0; i < count; i++) {
        result += outputs[i]->value * outputs[i]->confidence;  // 简单加权平均
        total_weight += outputs[i]->confidence;
    }
    return result / total_weight;  // ← 这不是"交叉验证"，这是"加权平均"！
}
```

#### 需要替换为

1. 两个独立模型推理
2. 结果对比和冲突检测
3. 置信度评估和不确定性量化
4. 多数投票/加权投票/专家仲裁三级机制

---

### DS-007: intent_parser.c智能不足 🟠 P1严重

| 属性 | 值 |
|------|-----|
| **问题ID** | DS-007 |
| **所属Phase** | Phase 0 |
| **严重程度** | 🟠 P1 严重 |
| **负责团队** | 团队A |
| **影响** | 意图解析只是关键词匹配，无法处理复杂或模糊指令 |
| **实现难度** | ⭐⭐⭐ |
| **当前状态** | ❌ 需增强 |

#### 当前实现问题

```c
// intent_parser.c 的"语义理解"（实际是关键词匹配）：
static intent_t intent_parse(const char* input) {
    if (strstr(input, "写代码") || strstr(input, "开发")) {
        return INTENT_CODE_GENERATION;
    }
    if (strstr(input, "查询") || strstr(input, "搜索")) {
        return INTENT_SEARCH;
    }
    return INTENT_UNKNOWN;
}
```

#### 需要增强为

1. LLM驱动的真正语义理解（依赖STUB-01/04修复）
2. 上下文感知的多轮对话能力
3. 歧义消解机制
4. 与MemoryRovol L3交互，检索相似历史意图

---

### DS-008: orchestrator流程编排器 🔴 P0致命

| 属性 | 值 |
|------|-----|
| **问题ID** | DS-008 |
| **所属Phase** | 全局 |
| **严重程度** | 🔴 P0 致命 |
| **负责团队** | 团队A |
| **影响** | Phase 0-4串联调度完全不存在，各Phase无法协同工作 |
| **实现难度** | ⭐⭐⭐⭐ |
| **当前状态** | ❌ 完全未实现 |

#### 设计要求

```
orchestrator流程:
  用户指令 → Phase 0(指令拆解) → Phase 1(规划) → Phase 2(流式批判执行)
                                                    ↓
                                              Phase 3(审计委员会)
                                                    ↓
                                              Phase 4(目标对齐)
                                                    ↓
                                              完成或重新规划
```

#### 需要实现的C代码模块

| 模块 | 功能 | 预估代码量 |
|------|------|-----------|
| `orchestrator.c` | 主流程编排 | 600+行 |
| `phase_manager.c` | Phase状态管理 | 200+行 |
| `transition_rules.c` | Phase转换规则 | 150+行 |

#### 依赖

- DS-001~007全部需要先有基础实现
- MR-004: 分时推理与记忆交换机制

---

## MR类: MemoryRovol实现差距

> **来源**: [emoryRovol独立突破上下文窗口限制的可行性.md](../../.vscode/emoryRovol独立突破上下文窗口限制的可行性.md) + [突破长上下文瓶颈.md](../../.vscode/突破长上下文瓶颈.md) + [三大设计文档全面可行性评估报告](./AgentOS三大设计文档全面可行性评估报告.md)

### MemoryRovol四层实现状态总览

| Layer | 功能 | 实现度 | 状态 | 对应问题ID | 关键缺失 |
|-------|------|--------|------|-----------|----------|
| **L1** | 原始卷(全量存储) | 95% | ✅ 基本完整 | MR-007 | 大规模分片存储 |
| **L2** | 特征层(语义向量+BM25) | 90% | ✅ 基本完整 | MR-005 | 动态索引更新 |
| **L3** | 结构层(绑定算子编码因果链) | 70% | ⚠️ 需增强 | MR-001/006 | 多元因果+图查询优化 |
| **L4** | 模式层(持久同调挖掘规则) | 65% | ⚠️ 需增强 | MR-002/003 | 规则注入+质量保证 |
| **全局** | 分时推理与记忆交换 | 0% | ❌ 未实现 | MR-004 | 核心机制完全缺失 |

### MR-001: 因果链编码不完整 🟠 P1严重

| 属性 | 值 |
|------|-----|
| **问题ID** | MR-001 |
| **所属Layer** | L3 |
| **严重程度** | 🟠 P1 严重 |
| **负责团队** | 团队A |
| **影响** | 绑定算子只支持二元关系，无法编码多元因果关系 → 跨子任务逻辑连续性无法保证 |
| **实现难度** | ⭐⭐⭐⭐ |
| **当前状态** | ❌ 需增强 |

#### 当前实现

- `binder.c`(1302行): 绑定算子只支持二元关系(A→B)
- `graph.c`(17606行): 图结构完整但因果链表达能力有限
- `relation.c`(6939行): 关系编码基本可用

#### 需要增强

1. 支持多元因果关系(A+B→C, A→B|C条件因果)
2. 时序因果链编码(事件序列+时间戳)
3. 因果强度量化(置信度+证据链)
4. 结合知识图谱嵌入技术(TransE/RotatE)

---

### MR-002: 规则注入机制 🟠 P1严重

| 属性 | 值 |
|------|-----|
| **问题ID** | MR-002 |
| **所属Layer** | L4 |
| **严重程度** | 🟠 P1 严重 |
| **负责团队** | 团队A |
| **影响** | L4规则无法自动注入S1/S2提示词 → "越用越聪明"无法实现 |
| **实现难度** | ⭐⭐⭐ |
| **当前状态** | ❌ 需实现 |

#### 设计要求

```json
{
  "pattern": "假设前提未验证",
  "trigger": "S2 生成 'assuming that' 或 'given that' 后",
  "action": "S1 强制检查前提是否在记忆中有依据",
  "confidence": 0.95
}
```

#### 需要实现

1. 规则→提示词自动转换引擎
2. 规则触发条件匹配器
3. 规则优先级和冲突解决
4. 规则效果追踪和A/B测试

---

### MR-003: 规则质量保证 🟡 P2中等

| 属性 | 值 |
|------|-----|
| **问题ID** | MR-003 |
| **所属Layer** | L4 |
| **严重程度** | 🟡 P2 中等 |
| **负责团队** | 团队A |
| **影响** | L4规则可能产生有害规则，缺少质量保证机制 |
| **实现难度** | ⭐⭐⭐ |
| **当前状态** | ❌ 需实现 |

#### 需要实现

1. 人工标注机制（初期主要依赖）
2. A/B测试反馈机制
3. 规则权限级别（只读/可修改/需审批）
4. 规则效果评估指标

---

### MR-004: 分时推理与记忆交换 🟠 P1严重

| 属性 | 值 |
|------|-----|
| **问题ID** | MR-004 |
| **所属Layer** | 全局 |
| **严重程度** | 🟠 P1 严重（核心机制完全缺失） |
| **负责团队** | 团队A |
| **影响** | 核心机制"虚拟内存"类比未实现 → 无法支撑1000小时超长任务 |
| **实现难度** | ⭐⭐⭐⭐⭐ (最高) |
| **当前状态** | ❌ 完全未实现 |

#### 设计要求（来自突破长上下文瓶颈文档）

```
分时推理 + 记忆交换:
  窗口 = RAM (有限容量，当前推理上下文)
  MemoryRovol = 磁盘 (近乎无限，永久存储)
  检索算法 = MMU (决定何时换入/换出)

流程:
  1. 任务切片: 1000小时 → 大量子任务
  2. 每次只处理一个子任务: 加载上下文 + 检索相关历史
  3. 子任务完成: 关键结果写入MemoryRovol
  4. 下一个子任务: 检索上一子任务摘要(L2) + 相关规则(L4)
  5. 目标对齐: 定期从L1加载完整历史，生成进度摘要
```

#### 需要实现的C代码模块

| 模块 | 功能 | 预估代码量 |
|------|------|-----------|
| `memory_exchange.c` | 记忆交换管理器 | 500+行 |
| `context_window.c` | 上下文窗口管理 | 300+行 |
| `task_slicer.c` | 任务切片器 | 200+行 |
| `swap_strategy.c` | 换入换出策略 | 250+行 |

---

### MR-005: 动态索引更新 🟡 P2中等

| 属性 | 值 |
|------|-----|
| **问题ID** | MR-005 |
| **所属Layer** | L2 |
| **严重程度** | 🟡 P2 中等 |
| **负责团队** | 团队A |
| **影响** | 缺少动态索引更新策略 → 新写入的记忆可能无法被及时检索 |
| **实现难度** | ⭐⭐ |
| **当前状态** | ❌ 需实现 |

---

### MR-006: 图查询优化 🟡 P2中等

| 属性 | 值 |
|------|-----|
| **问题ID** | MR-006 |
| **所属Layer** | L3 |
| **严重程度** | 🟡 P2 中等 |
| **负责团队** | 团队A |
| **影响** | 大规模图路径查询算法未优化 → 因果链检索延迟高 |
| **实现难度** | ⭐⭐⭐ |
| **当前状态** | ❌ 需优化 |

---

### MR-007: 分片存储优化 🟢 P3低

| 属性 | 值 |
|------|-----|
| **问题ID** | MR-007 |
| **所属Layer** | L1 |
| **严重程度** | 🟢 P3 低 |
| **负责团队** | 团队A |
| **影响** | 大规模数据分片存储需优化 → 影响存储效率 |
| **实现难度** | ⭐⭐ |
| **当前状态** | ❌ 需优化 |

---

## HIST类: 历史遗留问题

> **来源**: [08次-项目全面检查与初始目标评估报告](./历史档案/检查报告/20260410-08次-项目全面检查与初始目标评估报告.md) + [第5轮战略级深度验证报告](./历史档案/检查报告/AgentOS第5轮战略级深度验证报告.md)

### HIST-001: 777个TODO/FIXME注释 🟡 P2中等

| 属性 | 值 |
|------|-----|
| **问题ID** | HIST-001 |
| **来源** | 08次报告 |
| **严重程度** | 🟡 P2 中等 |
| **负责团队** | 全团队 |
| **当前状态** | 🔶 部分已清理(777→~61) |
| **影响** | 大量待完成/待修复标记，表明代码成熟度不足 |

#### 清理方案

1. 按模块分配给各团队
2. 每个TODO分类为：已实现(删除)、待实现(创建Issue)、过时(删除)
3. CI扫描：`grep -r "TODO\|FIXME" agentos/ --include="*.c" | wc -l` 必须<50

---

### HIST-002: 197个不安全字符串函数调用 🟠 P1严重

| 属性 | 值 |
|------|-----|
| **问题ID** | HIST-002 |
| **来源** | 08次报告 |
| **严重程度** | 🟠 P1 严重 |
| **负责团队** | 团队A(主要) + 团队B(辅助) |
| **当前状态** | 🔶 部分已修复 |
| **影响** | `strcpy`/`gets`/`scanf`/`strcat`等使用存在缓冲区溢出风险 |

#### 修复方案

| 不安全函数 | 安全替代 | 示例 |
|-----------|---------|------|
| `strcpy(dst, src)` | `strncpy(dst, src, sizeof(dst)-1)` | 限制复制长度 |
| `gets(buf)` | `fgets(buf, sizeof(buf), stdin)` | 限制读取长度 |
| `sprintf(buf, ...)` | `snprintf(buf, sizeof(buf), ...)` | 限制格式化长度 |
| `strcat(dst, src)` | `strncat(dst, src, sizeof(dst)-strlen(dst)-1)` | 限制追加长度 |

---

### HIST-003: 智能体动态团队组建自动化不足(30%) 🟠 P1严重

| 属性 | 值 |
|------|-----|
| **问题ID** | HIST-003 |
| **来源** | 08次报告 + 第5轮验证 |
| **严重程度** | 🟠 P1 严重 |
| **负责团队** | 团队B |
| **当前状态** | ⚠️ market_d基础设施在，但自动匹配/解散逻辑不足 |
| **影响** | 无法实现"从角色市场匹配专业Agent→组建临时团队→协同工作→自动解散" |

#### 已实现 vs 未实现

| 功能 | 状态 | 说明 |
|------|------|------|
| Agent注册表(CRUD) | ✅ | agent_registry.c完整 |
| 技能注册 | ✅ | skill_registry.c完整 |
| 基于技能的匹配 | ⚠️ | 基础匹配算法 |
| 团队创建接口 | ✅ | market_service_impl.c |
| **自动解散机制** | ❌ | 缺少生命周期管理 |
| **进度同步** | ❌ | 团队成员间缺乏实时同步 |
| **冲突解决** | ❌ | 多Agent协作资源冲突 |
| **动态调整** | ❌ | 运行时添加/移除成员 |

---

### HIST-004: 自然语言交互界面缺失 🟡 P2中等

| 属性 | 值 |
|------|-----|
| **问题ID** | HIST-004 |
| **来源** | 08次报告 + 第5轮验证 |
| **严重程度** | 🟡 P2 中等 |
| **负责团队** | 团队B |
| **当前状态** | ❌ 未开始 |
| **影响** | 缺少端到端自然语言界面，用户无法用自然语言指挥智能体 |

---

### HIST-005: 测试覆盖率0% 🔴 P0致命

| 属性 | 值 |
|------|-----|
| **问题ID** | HIST-005 |
| **来源** | 第5轮验证 |
| **严重程度** | 🔴 P0 致命 |
| **负责团队** | 全团队 |
| **当前状态** | ❌ 未开始 |
| **影响** | 无法验证任何功能正确性，所有"可用性"声明无法证实 |

#### 实施方案

| 阶段 | 目标覆盖率 | 时间 | 框架 |
|------|-----------|------|------|
| 第一阶段 | ≥50% | 2周 | CMake CTest + Criterion |
| 第二阶段 | ≥70% | 4周 | 增加集成测试 |
| 第三阶段 | ≥80% | 6周 | 增加端到端测试 |

---

### HIST-006: 设备驱动层(Interfaces)几乎空白 🟡 P2中等

| 属性 | 值 |
|------|-----|
| **问题ID** | HIST-006 |
| **来源** | 第5轮验证 |
| **严重程度** | 🟡 P2 中等 |
| **负责团队** | 团队B |
| **当前状态** | ❌ 仅1个头文件 |
| **影响** | 无法真正称为"操作系统" |

---

### HIST-007: 开发者工具链不完整 🟡 P2中等

| 属性 | 值 |
|------|-----|
| **问题ID** | HIST-007 |
| **来源** | 第5轮验证 |
| **严重程度** | 🟡 P2 中等 |
| **负责团队** | 团队B |
| **当前状态** | ⚠️ CLI增强版已有，但缺IDE/调试器/性能分析器 |
| **影响** | 开发者体验不足 |

---

### HIST-008: 双模型只是权重选择非真正推理 🔴 P1严重

| 属性 | 值 |
|------|-----|
| **问题ID** | HIST-008 |
| **来源** | 第5轮验证 |
| **严重程度** | 🟠 P1 严重 |
| **负责团队** | 团队A |
| **当前状态** | ❌ 同DS-006 |
| **影响** | 核心理论优势未实现 |

> **注意**: HIST-008与DS-006是同一问题的不同视角。HIST-008从历史遗留角度描述，DS-006从双思考系统设计角度描述。修复DS-006即修复HIST-008。

---

## TGT类: 设计目标偏差

> **来源**: [三大设计文档深度推理分析报告](./AgentOS三大设计文档深度推理分析报告.md) + [三大设计文档全面可行性评估报告](./AgentOS三大设计文档全面可行性评估报告.md)

### TGT-001: 准确率99%不可达 🟡 P2中等

| 属性 | 值 |
|------|-----|
| **问题ID** | TGT-001 |
| **设计目标** | 99%任务完成准确率 |
| **实际评估** | 85-90% |
| **差距** | -9~-14% |
| **严重程度** | 🟡 P2 中等 |
| **负责团队** | 全团队 |

#### 原因分析

设计文档使用简单加法计算准确率：
```
70% + 15% + 10% + 10% + 8% + 5% = 118% > 99%  ← 错误！
```

正确计算应使用概率乘法：
```
准确率 = 1 - (1-0.70) × (1-0.15) × (1-0.10) × (1-0.10) × (1-0.08) × (1-0.05) = 83%
```

#### 修正建议

- 调整目标为85-90%范围
- 85-90%仍具有实用价值
- 增加人工审核环节作为兜底

---

### TGT-002: 成本$0.75/h低估 🟡 P2中等

| 属性 | 值 |
|------|-----|
| **问题ID** | TGT-002 |
| **设计目标** | $0.75/h |
| **实际评估** | $1.5-2.5/h |
| **差距** | +100%~+233% |
| **严重程度** | 🟡 P2 中等 |
| **负责团队** | 全团队 |

#### 原因分析

设计文档只计算输出token成本($752)，忽略了：
- 输入token成本（占30-40%）
- API调用固定开销
- 修正重试成本
- S1检查成本

#### 修正建议

- 调整为$2.0/h初期目标
- 通过智能缓存和成本控制逐步降低

---

### TGT-003: 工期6个月低估 🟡 P2中等

| 属性 | 值 |
|------|-----|
| **问题ID** | TGT-003 |
| **设计目标** | 6个月 |
| **实际评估** | 9-12个月 |
| **差距** | +50%~+100% |
| **严重程度** | 🟡 P2 中等 |
| **负责团队** | 全团队 |

#### 修正建议

- 调整为9-12个月
- 采用渐进式交付策略
- 基础版3个月、增强版7个月、生产版12个月

---

## PROTO类: 协议系统已知限制

> **来源**: [AgentOS协议系统生态兼容性验证报告](./历史档案/检查报告/AgentOS协议系统生态兼容性验证报告.md) + [战略实施方案](./历史档案/改进计划/AgentOS_战略实施方案：全行业兼容与%20openJiuwen%20技术借鉴.md)

### PROTO-001: OpenJiuwen尚无WebSocket传输 🟡 P2中等

| 属性 | 值 |
|------|-----|
| **问题ID** | PROTO-001 |
| **严重程度** | 🟡 P2 中等 |
| **负责团队** | 团队B |
| **当前状态** | ⚠️ 当前仅TCP |
| **影响** | 实时双向通信受限 |

---

### PROTO-002: A2A共识投票为模拟实现 🟢 P3低

| 属性 | 值 |
|------|-----|
| **问题ID** | PROTO-002 |
| **严重程度** | 🟢 P3 低 |
| **负责团队** | 团队B |
| **当前状态** | ⚠️ 生产环境需真实分布式共识 |
| **影响** | 多Agent协作可靠性受限 |

---

### PROTO-003: OpenAI响应为模拟(mock) 🟡 P2中等

| 属性 | 值 |
|------|-----|
| **问题ID** | PROTO-003 |
| **严重程度** | 🟡 P2 中等 |
| **负责团队** | 团队A(需真实LLM后端) + 团队B(协议层) |
| **当前状态** | ⚠️ 需要真实LLM后端集成 |
| **影响** | OpenAI协议适配器无法返回真实响应 |
| **依赖** | STUB-01/04修复后才能解决 |

---

### PROTO-004: 无持久连接池 🟡 P2中等

| 属性 | 值 |
|------|-----|
| **问题ID** | PROTO-004 |
| **严重程度** | 🟡 P2 中等 |
| **负责团队** | 团队B |
| **当前状态** | ⚠️ 每次流式创建新连接 |
| **影响** | 连接建立开销大，延迟高 |

---

### PROTO-005: 统计仅在内存中 🟢 P3低

| 属性 | 值 |
|------|-----|
| **问题ID** | PROTO-005 |
| **严重程度** | 🟢 P3 低 |
| **负责团队** | 团队B |
| **当前状态** | ⚠️ 需要持久化指标存储 |
| **影响** | 重启后统计数据丢失 |

---

## 模块级问题分布

### 模块A: corekern (微内核核心)

**文件数**: 29 | **问题总数**: 0致命+1低 | **负责团队**: 团队A ✅

| 问题ID | 文件 | 行号 | 描述 | 严重程度 | 状态 |
|--------|------|------|------|----------|------|
| CK-L1 | sync.c | #if 0块 | 死代码（被条件编译禁用） | 🟢 低 | 📝 记录 |

**结论**: 代码质量优秀，仅1项低优先级死代码

---

### 模块B: coreloopthree (认知循环三层)

**文件数**: 53 | **问题总数**: 8致命+92非致命 | **负责团队**: 团队A ⚠️

#### 致命级问题

| 问题ID | 文件 | 描述 | 严重程度 | 状态 |
|--------|------|------|----------|------|
| STUB-03 | ml_planner.c | PHASE2-IMPLEMENTED ML推理管道 | 🔴 P0 | ❌ 待实现 |
| DS-006 | dual_model.c | 简单权重选择非真正交叉验证 | 🟠 P1 | ❌ 需重写 |
| DS-007 | intent_parser.c | 关键词匹配非语义理解 | 🟠 P1 | ❌ 需增强 |
| DS-008 | (新建) | orchestrator流程编排器不存在 | 🔴 P0 | ❌ 需创建 |

#### 非致命问题分布

| 子目录 | 文件数 | P1高 | P2中 | P3低 | 典型问题 |
|--------|--------|------|------|------|----------|
| cognition/planner/ | 8 | 2 | 5 | 3 | ml_planner.c fallback逻辑 |
| cognition/executor/ | 6 | 1 | 4 | 2 | 任务队列满处理策略 |
| cognition/memory/ | 5 | 1 | 3 | 3 | 短期记忆容量硬编码 |
| cognition/perception/ | 7 | 2 | 4 | 3 | 传感器数据边界检查 |
| cognition/learning/ | 4 | 1 | 2 | 2 | ML模型加载失败回退 |
| execution/units/ | 12 | 3 | 6 | 5 | file.c路径处理(已修复NULL保护) |
| execution/scheduler/ | 5 | 2 | 3 | 2 | 任务优先级动态调整 |
| execution/monitor/ | 4 | 1 | 3 | 2 | 执行超时检测精度 |
| execution/resource/ | 3 | 1 | 2 | 2 | 资源池扩容策略 |
| coordination/sync/ | 6 | 1 | 4 | 3 | 多Agent同步锁粒度 |
| coordination/conflict/ | 4 | 2 | 3 | 1 | 冲突检测算法优化 |
| coordination/negotiate/ | 5 | 1 | 3 | 2 | 谈判协议超时处理 |
| coordination/allocate/ | 4 | 1 | 2 | 3 | 资源分配公平性 |

---

### 模块C: memoryrovol (四层记忆系统)

**文件数**: 76 | **问题总数**: 3致命+40非致命 | **负责团队**: 团队A ⚠️

#### 致命级问题

| 问题ID | 文件 | 描述 | 严重程度 | 状态 |
|--------|------|------|----------|------|
| STUB-01 | include/curl_stub.h | 25个假CURL函数 | 🔴 P0 | ❌ 待清除 |
| STUB-02 | include/sqlite3_stub.h | 30+个假SQLite3函数 | 🔴 P0 | ❌ 待清除 |
| STUB-04 | src/llm_client.c | 12处degraded mode假SUCCESS | 🟠 P1 | ❌ 待修复 |
| MR-001 | src/l3/binder.c | 因果链编码不完整 | 🟠 P1 | ❌ 需增强 |
| MR-004 | (新建) | 分时推理与记忆交换未实现 | 🔴 P1 | ❌ 需创建 |

#### 非致命问题分布

| 子系统 | 问题数 | 主要问题 | 严重程度 |
|--------|--------|----------|----------|
| L1 原始记忆层(l1_raw/) | 12 | 边界检查/错误码/日志/性能 | P1-P3 |
| L2 上下文记忆层(l2_context/) | 10 | 并发访问/TTL/序列化/配置 | P1-P3 |
| L3 语义记忆层(l3_semantic/) | 9 | 向量计算/相似度阈值/索引 | P1-P3 |
| L4 模式记忆层(l4_pattern/) | 9 | 模式识别/学习速率/泛化/压缩 | P1-P3 |

---

### 模块D: syscall (系统调用层)

**文件数**: 18 | **问题总数**: 0 | **负责团队**: 团队A ✅

**结论**: 参数验证完善，资源管理规范，STRDUP 30处100%有NULL保护

---

### 模块E: cupolas (安全穹顶)

**文件数**: 82 | **问题总数**: 12非致命 | **负责团队**: 团队B ✅

| 问题ID | 文件 | 描述 | 严重程度 | 状态 |
|--------|------|------|----------|------|
| CUP-2 | vault_manager.c | 密钥轮换间隔可配置化 | 🟡 中 | ⏳ 待优化 |
| CUP-3 | audit_logger.c | 日志格式标准化 | 🟢 低 | ⏳ 待优化 |
| CUP-4~12 | 多处 | 小改进项 | 🟢 低-中 | ⏳ 排队 |

---

### 模块F: daemon (守护进程服务)

**文件数**: 150+ | **问题总数**: ~130非致命 | **负责团队**: 团队C ✅

| 子系统 | 问题数 | 主要问题 | 严重程度 |
|--------|--------|----------|----------|
| svc_common.c | ~50 | NULL检查/内存泄漏/错误处理 | P1-P2 |
| monit_d | 15 | 监控指标采集精度 | P2 |
| llm_d | 20 | LLM调用超时/重试 | P2 |
| tool_d | 18 | 工具注册/发现机制 | P2 |
| gateway_d | 12 | 请求路由效率 | P2 |
| market_d | 8 | 服务发布/订阅一致性 | P2 |
| sched_d | 7 | 任务调度算法优化 | P2 |

---

### 模块G: gateway (统一网关)

**文件数**: ~20 | **问题总数**: 8非致命 | **负责团队**: 团队C ✅

| 问题ID | 文件 | 描述 | 严重程度 | 状态 |
|--------|------|------|----------|------|
| GW-1 | protocol_bridge.c | LangChain适配器<50% | 🟠 P1 | ⏳ 开发中 |
| GW-2 | protocol_bridge.c | AutoGen适配器<50% | 🟠 P1 | ⏳ 开发中 |
| GW-3 | api.c | 连接池大小硬编码 | 🟡 P2 | ⏳ 待优化 |
| GW-4~8 | 多处 | 小改进项 | 🟡 P2-P3 | ⏳ 排队 |

---

### 模块H: heapstore (运行时数据存储)

**文件数**: ~30 | **问题总数**: 20非致命 | **负责团队**: 团队B ✅

| 子系统 | 问题数 | 主要问题 | 严重程度 |
|--------|--------|----------|----------|
| kernel/ipc/ | 5 | Binder/Channels效率 | P1-P2 |
| kernel/memory/ | 6 | 索引/元数据一致性 | P2 |
| services/ | 4 | 服务发现机制 | P2 |
| models/ | 3 | 模型版本管理 | P3 |
| logs/traces/db/ | 2 | 运行时数据膨胀 | P3 |

---

### 模块I: toolkit/protocols/interfaces (SDK与协议)

**文件数**: ~100+ | **问题总数**: 50非致命 | **负责团队**: 团队B ✅

| 组件 | 问题数 | 状态 |
|------|--------|------|
| Python SDK | 15 | ✅ 清洁 |
| Go SDK | 10 | ✅ 基本完成 |
| Rust SDK | 15 | ✅ 基本完成 |
| TypeScript SDK | 10 | ✅ 基本完成 |
| 协议适配器 | 25 | ⚠️ 5项已知限制(PROTO-001~005) |

---

## 团队分工矩阵

### 团队A - 核心内核组 (20个问题)

| 优先级 | 问题ID | 描述 | 预估工时 | 依赖 | 阶段 |
|--------|--------|------|----------|------|------|
| 🔴 P0 | STUB-01 | curl_stub.h清除 | 8h | 无 | 第一阶段 |
| 🔴 P0 | STUB-02 | sqlite3_stub.h清除 | 8h | 无 | 第一阶段 |
| 🔴 P0 | STUB-03 | ml_planner.c实现 | 40h | STUB-01 | 第一阶段 |
| 🟠 P1 | STUB-04 | llm_client.c修复 | 16h | STUB-01 | 第一阶段 |
| 🟠 P1 | STUB-05 | config_service.c实现 | 8h | 无 | 第一阶段 |
| 🔴 P0 | DS-001 | 流式批判循环 | 80h | STUB-01/04 | 第二阶段 |
| 🟠 P1 | DS-002 | 审计委员会 | 40h | DS-001 | 第二阶段 |
| 🟠 P1 | DS-003 | 任务漂移检测 | 24h | MR-001 | 第二阶段 |
| 🟡 P2 | DS-004 | 目标对齐检查 | 24h | DS-001/MR-004 | 第三阶段 |
| 🟡 P2 | DS-005 | 定期进度摘要 | 16h | DS-001 | 第三阶段 |
| 🟠 P1 | DS-006 | dual_model.c重写 | 40h | STUB-01 | 第二阶段 |
| 🟠 P1 | DS-007 | intent_parser.c增强 | 24h | STUB-01 | 第二阶段 |
| 🔴 P0 | DS-008 | orchestrator创建 | 60h | DS-001~007 | 第三阶段 |
| 🟠 P1 | MR-001 | 因果链编码增强 | 40h | 无 | 第二阶段 |
| 🟠 P1 | MR-002 | 规则注入机制 | 24h | MR-001 | 第二阶段 |
| 🟡 P2 | MR-003 | 规则质量保证 | 16h | MR-002 | 第三阶段 |
| 🟠 P1 | MR-004 | 分时推理与记忆交换 | 60h | MR-001/002 | 第二阶段 |
| 🟡 P2 | MR-005 | 动态索引更新 | 8h | 无 | 第三阶段 |
| 🟡 P2 | MR-006 | 图查询优化 | 16h | MR-001 | 第三阶段 |
| 🟢 P3 | MR-007 | 分片存储优化 | 8h | 无 | 第三阶段 |

**团队A总工时**: ~560小时 (~14周)

### 团队B - 安全与服务组 (5个问题)

| 优先级 | 问题ID | 描述 | 预估工时 | 依赖 | 阶段 |
|--------|--------|------|----------|------|------|
| 🟡 P2 | PROTO-001 | OpenJiuwen WebSocket | 16h | 无 | 第二阶段 |
| 🟢 P3 | PROTO-002 | A2A真实分布式共识 | 40h | 无 | 第三阶段 |
| 🟡 P2 | PROTO-003 | OpenAI真实LLM后端 | 24h | STUB-01 | 第二阶段 |
| 🟡 P2 | PROTO-004 | 持久连接池 | 16h | 无 | 第二阶段 |
| 🟢 P3 | PROTO-005 | 统计持久化 | 8h | 无 | 第三阶段 |

**团队B额外任务**（来自HIST类）:

| 优先级 | 问题ID | 描述 | 预估工时 | 阶段 |
|--------|--------|------|----------|------|
| 🟠 P1 | HIST-003 | 智能体团队组建自动化 | 40h | 第二阶段 |
| 🟡 P2 | HIST-004 | 自然语言交互界面 | 60h | 第三阶段 |
| 🟡 P2 | HIST-006 | 设备驱动层扩充 | 40h | 第三阶段 |
| 🟡 P2 | HIST-007 | 开发者工具链 | 40h | 第三阶段 |

**团队B总工时**: ~284小时 (~7周)

### 团队C - 守护进程与网关组 (0个核心问题)

团队C已清零daemon/gateway范围的桩函数，当前主要任务为：

| 优先级 | 任务 | 描述 | 预估工时 | 阶段 |
|--------|------|------|----------|------|
| 🟠 P1 | daemon非致命问题 | svc_common.c NULL检查等~130个 | 60h | 持续 |
| 🟠 P1 | 集成测试套件 | 建立端到端测试框架 | 40h | 第一阶段 |
| 🟡 P2 | LangChain适配器 | <50%→>90% | 16h | 第二阶段 |
| 🟡 P2 | AutoGen适配器 | <50%→>90% | 16h | 第二阶段 |

**团队C总工时**: ~132小时 (~3.5周)

### 全团队协同任务

| 优先级 | 问题ID | 描述 | 预估工时 | 阶段 |
|--------|--------|------|----------|------|
| 🟡 P2 | HIST-001 | TODO/FIXME清理 | 24h | 持续 |
| 🟠 P1 | HIST-002 | 不安全字符串函数修复 | 40h | 第一阶段 |
| 🔴 P0 | HIST-005 | 测试覆盖率0%→50%+ | 80h | 第一阶段 |
| 🟠 P1 | HIST-008 | 同DS-006 | - | - |
| 🟡 P2 | TGT-001 | 准确率目标调整 | 4h | 第一阶段 |
| 🟡 P2 | TGT-002 | 成本目标调整 | 4h | 第一阶段 |
| 🟡 P2 | TGT-003 | 工期目标调整 | 4h | 第一阶段 |

---

## 修复优先级与依赖关系

### 依赖关系图

```
STUB-01(curl) ──→ STUB-04(llm_client) ──→ DS-001(流式批判) ──→ DS-002(审计委员会)
     │                                          │
     │                                          ├──→ DS-006(dual_model重写)
     │                                          ├──→ DS-007(intent_parser增强)
     │                                          └──→ DS-004(目标对齐)
     │
STUB-02(sqlite3) ──→ MR-005(动态索引) ──→ MR-004(分时推理)
                                              │
STUB-03(ml_planner) ──→ DS-008(orchestrator) ←─┘
                          │
MR-001(因果链) ──────────→ DS-003(漂移检测)
     │
MR-001 ──→ MR-002(规则注入) ──→ MR-003(规则质量)
                                      │
                                 DS-001(流式批判需要L4规则)
```

### 关键路径

```
STUB-01 → STUB-04 → DS-001 → DS-002 → DS-008
   │                              │
   └──→ DS-006 ──────────────────→│
   └──→ DS-007 ──────────────────→│
                                   │
MR-001 → MR-002 → DS-001 ───────→│
MR-001 → DS-003 ─────────────────→│
```

**关键路径长度**: STUB-01 → STUB-04 → DS-001 → DS-008 = 约16周

---

## 安全漏洞清单

### 🔴 已修复的安全漏洞

| 漏洞ID | 类型 | CVSS | 影响文件 | 修复状态 |
|--------|------|------|----------|----------|
| SEC-VUL-01 | 命令注入 | 9.8 | daemon_security.c | ✅ 已修复 |
| SEC-VUL-02 | 路径遍历 | 7.5 | file.c | ✅ 已修复 |
| SEC-VUL-03 | SQL注入 | 8.1 | heapstore DB层 | ✅ 已修复 |
| SEC-VUL-04 | 缓冲区溢出 | 9.1 | 多处字符串处理 | ✅ 已修复 |
| SEC-VUL-05 | SSRF | 7.0 | gateway URL处理 | ✅ 已修复 |
| SEC-VUL-06 | 信息泄露 | 5.5 | 日志敏感信息 | ✅ 已修复 |

**总计**: 6个安全漏洞全部修复 ✅

---

## 修复历史记录

### 时间线（2026-04-15 至 2026-04-19）

```
04-15 09:00 ──► Round 1-5: coreloopthree 11致命问题修复
04-16 10:00 ──► Round 6-10: memoryrovol 3致命 + 6安全漏洞修复
04-17 09:00 ──► Round 11-15: corekern+syscall深度审计，0新问题
04-17 20:40 ──► 🎉 团队C历史性突破: BUILD_DAEMON=ON达成
04-17 21:30 ──► 🔥 SEC-017桩函数清除里程碑(daemon/gateway: 30→0)
04-17 23:00 ──► 🚀 Phase 2完成: P0内存安全+P1线程安全加固
04-18 08:21 ──► Round 17: STRDUP最终全扫描(30处100%NULL保护)
04-18 14:00 ──► 🔴🔴🔴 全模块穷尽扫描发现68+桩函数违规(团队A)
04-19         ──► v13.0问题清单: 整合6类36+问题，建立团队分工矩阵
```

### 量化成果

| 指标 | 初始值 | 当前值 | 改善 |
|------|--------|--------|------|
| 致命问题(daemon/gateway) | 48 | 0 | -100% ✅ |
| 桩函数(daemon/gateway) | 30 | 0 | -100% ✅ |
| 🔴新发现桩函数(团队A) | 0 | 68+ | ❌ 新增 |
| 编译错误数 | 18 | 0 | -100% ✅ |
| 安全漏洞数 | 6 | 0 | -100% ✅ |
| 编译成功率 | ~65% | 100% | +35% ✅ |
| 团队C评级 | 2.8/10 | 9.3/10 | +6.5 🎉 |
| 团队A评级 | 8.5/10 | 7.5/10 | -1.0 ⚠️ |
| 整体评级 | 2.8/10 | 6.5/10 | +3.7 |

---

> **维护说明**: 本文档是AgentOS项目的**详细问题追踪清单**，每个问题都有唯一ID、负责团队、修复方案和验收标准。所有数据必须来自实际代码审查和历史文档，严禁凭空捏造。
>
> **最后更新**: 2026-04-19 (v13.0.0 生产级穷尽问题追踪与团队分工版)
>
> **下次计划更新**: 2026-04-26 (或重大事件触发时立即更新)