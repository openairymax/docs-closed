# AgentOS 桩函数穷尽检查报告 v1.0.0

> **版本**: 1.0.0-真实验证+全模块扫描版
> **日期**: 2026-04-18
> **检查范围**: 全部 agentos/ 目录（排除 tests/ 和 benchmark/）
> **扫描时间**: 2026-04-18 11:00 CST
> **扫描方式**: 穷尽式逐模式grep + 人工逐文件验证
> **结论**: ❌ **SEC-017 严重违规！之前声称"0桩函数"是错误的！**

---

## 🚨 执行摘要

| 指标 | 之前声称 | **实际发现** | 差异 |
|------|----------|------------|------|
| 生产代码桩函数数 | **0** | **13+处** | 🔴 **+13** |
| stub头文件 | **0** | **2个** | 🔴 **+2** |
| 条件编译桩引用 | **0** | **10个文件** | 🔴 **+10** |
| PHASE2-IMPLEMENTED标记 | **0** | **1个** | 🔴 **+1** |
| degraded mode降级 | **0** | **1个文件(5处)** | 🔴 **+5** |
| SEC-017合规状态 | ✅ 100% | ❌ **严重违规** | 🔴 **不合规** |

---

## 🔴 发现的桩函数清单（按严重程度排序）

### P0-致命: 完整stub头文件（2个）

#### STUB-01: `curl_stub.h` (memoryrovol/include/)

**文件路径**: `agentos/atoms/memoryrovol/include/curl_stub.h`

**问题类型**: 完整的 libcurl API 桩头文件

**影响范围**: 所有 CURL 操作变为空操作

**桩函数数量**: **25个** (CURLcode, CURL*, curl_easy_*, curl_slist_* 等)

**典型代码**:
```c
/* 所有函数都返回错误或空值 */
typedef void CURL;
typedef int CURLcode;

#define CURLE_OK 0
#define CURLE_FAILED_INIT 2

static inline CURL* curl_easy_init(void) { return NULL; }
static inline CURLcode curl_easy_setopt(CURL *curl, CURLoption option, ...) { return CURLE_FAILED_INIT; }
static inline CURLcode curl_easy_perform(CURL *curl) { return CURLE_FAILED_INIT; }
static inline void curl_easy_cleanup(CURL *curl) { (void)curl; }
// ... 还有22个类似函数
```

**被引用位置**: 
- `agentos/atoms/memoryrovol/src/llm_client.c:26` (#ifdef else 分支)

**触发条件**: 当 `AGENTOS_HAS_CURL` 未定义时激活

**影响**: LLM客户端完全无法工作（HTTP请求全部失败）

---

#### STUB-02: `sqlite3_stub.h` (memoryrovol/include/)

**文件路径**: `agentos/atoms/memoryrovol/include/sqlite3_stub.h`

**问题类型**: 完整的 SQLite3 API 桩头文件

**影响范围**: 所有数据库操作返回错误

**桩函数数量**: **30+个** (sqlite3*, SQLITE_*, 回调函数等)

**典型代码**:
```c
/* 所有函数都返回错误 */
typedef struct sqlite3 sqlite3;
#define SQLITE_OK 0
#define SQLITE_ERROR 1
#define SQLITE_NOMEM 7

static inline int sqlite3_open(const char *filename, sqlite3 **ppDb) { return SQLITE_NOMEM; }
static inline int sqlite3_exec(sqlite3*, const char*, ...){ return SQLITE_ERROR; }
static inline int sqlite3_prepare_v2(...){ return SQLITE_ERROR; }
static inline int sqlite3_step(sqlite3_stmt*){ return SQLITE_ERROR; }
static inline const char* sqlite3_errmsg(sqlite3*){ return "stub error"; }
// ... 还有26+个类似函数
```

**被引用位置**: 
- `agentos/atoms/memoryrovol/src/vector_store.c:26` (#ifdef else 分支)

**触发条件**: 当 `AGENTOS_HAS_SQLITE3` 未定义时激活

**影响**: 向量存储完全无法工作（数据库操作全部失败）

---

### P0-致命: PHASE2-IMPLEMENTED 标记桩（1个）

#### STUB-03: ML推理管道桩 (ml_planner.c)

**文件路径**: `agentos/atoms/coreloopthree/src/cognition/planner/ml_planner.c`

**行号**: 68-88, 184-194

**问题类型**: 明确标注为"PHASE2-IMPLEMENTED"的ML推理桩

**影响**: ML规划器永远走fallback路径，无法进行真正的机器学习推理

**代码证据**:
```c
/* Line 68-88: ML模型初始化桩 */
    /* PHASE2-IMPLEMENTED: ML model initialization with placeholder
     * Current implementation uses a lightweight placeholder that can be
     * replaced with actual model loading when ML runtime is available.
     */
    data->model = NULL;  // ← 永远是NULL！
    data->fallback_mode = true;  // ← 永远是fallback模式！
    // ...
    data->fallback_mode = true;  // ← 再次确认fallback
    
/* Line 184-194: ML推理管道桩 */
    if (data->model->predict && data->model->handle) {
        /* PHASE2-IMPLEMENTED: ML inference pipeline stub
         * Current implementation provides a framework for future ML integration.
         * When full ML runtime is available, this section will implement:
         *
         * 1. Extract features from intent (type, complexity, context)
         * 2. Run model predict() to get task decomposition
         * 3. Decode model output into agentos_task_plan_t structure
         * 4. Validate plan feasibility
         */
        AGENTOS_LOG_DEBUG("ML planner: executing inference pipeline (placeholder)");
        // ← 只有一行日志！没有任何真实ML推理代码！
    }

    /* Fallback if model predict is not yet implemented */
    return ml_planner_fallback_plan(intent, out_plan);  // ← 永远走这里！
```

**关键问题**: 
- `data->model` 永远是 NULL（第213行初始化时设为NULL且从未真正加载模型）
- `data->fallback_mode` 永远是 true
- 推理管道只有一行日志，没有特征提取、模型调用、结果解码
- 函数始终返回 `ml_planner_fallback_plan()` 结果

**影响**: 整个ML规划功能是假的，声称支持但实际完全未实现

---

### P1-高: 条件编译降级模式桩（1个文件，5处）

#### STUB-04: LLM客户端降级模式 (llm_client.c)

**文件路径**: `agentos/atoms/memoryrovol/src/llm_client.c`

**行号**: 149-158, 185-201, 271-276

**问题类型**: 使用curl_stub + cJSON桩实现的降级模式

**影响**: 无CURL依赖时LLM功能完全失效

**代码证据**:
```c
/* Line 149-158: 创建服务时的降级 */
    CURL* curl = curl_easy_init();  // 如果没有CURL库，这返回NULL（来自curl_stub.h）
    if (!curl) {
        AGENTOS_LOG_WARN("CURL initialization failed - running in degraded mode");
        service->curl = NULL;
        service->initialized = 1;  // ← 仍然标记为"已初始化"！
        *out_service = service;
        AGENTOS_LOG_INFO("LLM service created in degraded mode (model: %s)", ...);
        return AGENTOS_SUCCESS;  // ← 返回成功，但实际功能不可用！
    }

/* Line 185-201: LLM调用的降级响应 */
    if (!service->curl) {
        AGENTOS_LOG_WARN("LLM complete attempted in degraded mode (no CURL support)");
        resp->text = AGENTOS_STRDUP("LLM service unavailable (degraded mode)");  // ← 返回假数据！
        // ...
        return AGENTOS_SUCCESS;  // ← 返回成功，但数据是假的！
    }

/* Line 271-276: LLM service_call 的降级 */
    if (!service->curl) {
        AGENTOS_LOG_WARN("LLM service call attempted in degraded mode");
        *out_response = AGENTOS_STRDUP("LLM service unavailable (running in degraded mode)");
        return *out_response ? AGENTOS_SUCCESS : AGENTOS_ENOMEM;  // ← 返回假数据！
    }
```

**额外问题**: cJSON 桩实现（第30-63行）：
```c
#ifdef AGENTOS_HAS_CJSON
#include <cjson/cJSON.h>
#else
typedef struct cJSON { ... } cJSON;  // 假类型定义

static inline cJSON* cJSON_CreateObject(void) { return NULL; }  // 永远返回NULL
static inline char* cJSON_PrintUnformatted(const cJSON* item) { (void)item; return NULL; }
// ... 12个cJSON函数全是桩
#endif
```

**影响**: 
- LLM客户端在无依赖时静默降级，返回假数据和假成功状态
- 调用者无法区分真假响应
- 可能导致上层逻辑基于假数据做决策

---

### P1-高: 简化实现桩（1个）

#### STUB-05: config_service 版本比较桩 (config_service.c)

**文件路径**: `agentos/commons/utils/config_unified/src/config_service.c`

**行号**: 900-916

**问题类型**: 函数体只返回固定字符串，不做实际比较

**影响**: 配置版本比较功能完全无效

**代码证据**:
```c
config_error_t config_version_diff(config_manager_t* manager,
                                const char* version1,
                                const char* version2,
                                char* diff,
                                size_t diff_size) {
    // 简化实现：实际应比较两个版本的差异
    (void)manager;
    (void)version1;
    (void)version2;  // ← 所有参数被忽略！
    
    if (diff && diff_size > 0) {
        const char* msg = "Version diff not implemented in simplified version";  // ← 硬编码假数据
        size_t len = strlen(msg);
        if (len >= diff_size) len = diff_size - 1;
        memcpy(diff, msg, len);  // ← 复制固定字符串到输出
        diff[len] = '\0';
        return len;
    }
    
    return 0;  // ← 总是返回成功
}
```

**影响**: 版本管理功能形同虚设，配置升级检测不可靠

---

## 📊 统计汇总

### 桩函数分布按模块

| 模块 | 桩函数类型 | 数量 | 严重程度 | 文件 |
|------|-----------|------|----------|------|
| **memoryrovol/** | stub头文件 | 2 | P0 致命 | curl_stub.h, sqlite3_stub.h |
| **memoryrovol/** | 条件编译降级 | 5处 | P1 高 | llm_client.c |
| **memoryrovol/** | cJSON条件桩 | 12函数 | P1 高 | llm_client.c (+6其他文件) |
| **coreloopthree/** | PHASE2-IMPLEMENTED | 1 | P0 致命 | ml_planner.c |
| **commons/** | 简化实现 | 1 | P1 高 | config_service.c |
| **总计** | | **~20+处** | | **5个文件** |

### 触发条件分析

| 触发条件 | 影响文件 | 影响 |
|----------|----------|------|
| `AGENTOS_HAS_CURL` 未定义 | llm_client.c | LLM功能完全失效 |
| `AGENTOS_HAS_SQLITE3` 未定义 | vector_store.c | 向量存储完全失效 |
| `AGENTOS_HAS_CJSON` 未定义 | 7个文件 | JSON解析完全失效 |
| 模型文件不存在 | ml_planner.c | ML规划始终走fallback |
| 始终 | config_service.c | 版本比较返回假数据 |

---

## ⚠️ 与之前声明的矛盾

### 之前的虚假声明（v13.0/v14.0 报告）

```bash
# 之前声称的验证命令和结果：
$ grep -ri "stub\|STUB\|not implemented\|malloc(1)" \
       cupolas/ daemon/ gateway/ --include="*.c"
# → 团队C范围生产代码 **0 桩函数 + 0 malloc(1)** 🎯
```

### 实际问题

1. **扫描范围太窄**: 只扫描了 `cupolas/ daemon/ gateway/` 三个目录
   - 遗漏了 `memoryrovol/`, `coreloopthree/`, `commons/` 等核心模块
   
2. **遗漏了stub头文件**: 没有搜索 `*_stub.h` 文件
   
3. **遗漏了条件编译桩**: 没有搜索 `#ifdef.*else` 分支中的桩实现
   
4. **遗漏了PHASE2标记**: 没有搜索 `PHASE.*IMPLEMENTED` 关键词
   
5. **遗漏了degraded模式**: 没有识别"降级模式"作为桩函数的一种形式

---

## 🔧 修复建议

### 立即修复（P0）

1. **删除或替换 stub 头文件**
   - `curl_stub.h`: 要么强制依赖 libcurl，要么移除 LLM 功能
   - `sqlite3_stub.h`: 要么强制依赖 SQLite3，要么移除向量存储功能

2. **实现真实的 ML 推理管道**
   - `ml_planner.c`: 替换 fallback 为真实模型加载和推理
   - 或者明确标注该功能为"实验性/未完成"

### 短期修复（P1）

3. **消除降级模式的假成功返回**
   - `llm_client.c`: 降级时应返回错误码而非 SUCCESS
   - 或者在编译时强制要求所有依赖

4. **实现 config_version_diff 真实逻辑**
   - `config_service.c`: 实现真正的版本比较算法

### 长期改进

5. **建立全面的 CI 扫描规则**
   ```bash
   # 新增扫描项：
   find . -name "*stub*.h" -not -path "*/tests/*"  # 必须为0
   grep -r "PHASE.*IMPLEMENTED" --include="*.c"       # 必须为0
   grep -r "degraded mode" --include="*.c"            # 必须为0
   grep -r "simplified version" --include="*.c"      # 必须为0
   ```

---

## 📝 结论

**AgentOS 项目当前 SEC-017 合规状态: ❌ 严重违规**

之前声称的"0桩函数"是**错误的**，原因是：
1. 扫描范围不全（仅扫描3个目录，遗漏核心模块）
2. 扫描模式不全（遗漏多种桩函数模式）
3. 验证不严格（接受了"降级模式"作为正常行为）

**实际桩函数数量**: **20+处**（5个生产文件受影响）

**修复优先级**: 
- P0 (立即): 2个stub头文件 + 1个PHASE2桩 = **阻塞真实运行**
- P1 (本周): 5处降级模式 + 1个简化实现 = **影响数据可靠性**

---

> **本报告基于2026-04-18 11:00 CST的实际穷尽扫描，所有发现均可复现。**
>
> **关联文档**: [主报告v14.0](./AgentOS全面修复与改进报告07.md) | [规范手册v8.0](./AgentOS工程规范化标准手册07.md) | [看板v8.0](./AgentOS三团队任务进度看板07.md)
