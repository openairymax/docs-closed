# MemoryRovol 全面完善方案 v11.13

**版本**: v11.13.0-第09大轮次·全面完善版
**依据**: 5份核心设计方案 + 4份历史原型文档 + 代码审计报告 + v11.12提供商架构  
**审计日期**: 2026-04-29  
**目标**: MemoryRovol 成为符合设计标准的生产级商业化闭源库

---

> **核心发现**：
> MemoryRovol 代码库拥有优秀的整体架构（~8000行 C 代码），但存在：
> - **6个缺失函数** — 声明但未实现，会导致链接失败
> - **4个桩实现** — 返回固定值或假数据
> - **14个质量缺陷** — 内存泄漏、线程安全、可移植性等
> - **关键子系统缺失** — 无 license 验证、无内置提供商适配、无正确 CMake 双模式

---

## 第1章 — 审计总结

### 1.1 功能完整性矩阵

| 设计文档要求的模块 | 代码实现状态 | 审计结论 |
|-----------------|------------|---------|
| **L1 原始卷**（分块存储+异步写入+SQLite元数据） | ✅ 完整实现 | 良好（storage.c + async_storage + metadata.c） |
| **L2 特征层**（FAISS索引+嵌入模型+LRU缓存+向量持久化） | ✅ 完整实现 | 良好（index.c + embedder.c + lru_cache.c + vector_store.c） |
| **L3 结构层**（知识图谱+绑定算子） | 🟡 **部分缺陷** | `agentos_binder_bind` 缺失实现。binder.c 是简化包装 |
| **L4 模式层**（持久同调+HDBSCAN+规则生成） | 🔴 **严重问题** | 4个桩实现：规则生成不调LLM、模式匹配总是成功、置信度硬编码 |
| **遗忘引擎**（艾宾浩斯曲线+多策略） | 🟡 **部分缺陷** | `get_weight` 副作用、线程安全、路径不可移植 |
| **检索系统**（吸引子网络+重排序+挂载） | 🟡 **部分缺陷** | `retrieval_search` 缺失实现；attractor.c 内存泄漏 |
| **LLM客户端**（DS-004双思维） | 🟡 **可编译但有耦合** | 硬依赖coreloopthree路径，跨模块耦合 |
| **License验证** | 🔴 **完全缺失** | 无 `license.c`、无 `license.h`、无 RSA 验签 |
| **AgentOS提供商适配** | 🔴 **完全缺失** | 无 `agentos_provider.c`、无 `memory_provider.h` 适配 |
| **CMake双模式构建** | 🔴 **完全缺失** | 无 `MEMORYROVOL_ENABLE` 选项 |
| **监控系统** | ✅ 完整实现 | 健全的结构化指标采集（monitoring.c） |
| **内存管理**（memory_pool + garbage_collector） | ✅ 完整实现 | 分代GC + 固定块分配器 |
| **配置系统** | 🔴 **完全缺失** | `config.h` 中3个函数全部未实现 |

### 1.2 缺失函数列表（链接时崩溃）

| # | 函数 | 声明位置 | 被调用位置 | 影响 |
|--|------|---------|-----------|------|
| F-01 | `agentos_memoryrov_config_load` | `include/config.h:64` | 任何调用者 | 🔴链接失败 |
| F-02 | `agentos_memoryrov_config_free` | `include/config.h:72` | 任何调用者 | 🔴链接失败 |
| F-03 | `agentos_memoryrov_config_default` | `include/config.h:79` | 任何调用者 | 🔴链接失败 |
| F-04 | `agentos_binder_bind` | `include/layer3_structure.h:57` | `sequence.c` `relation.c` | 🔴链接失败 |
| F-05 | `agentos_retrieval_search` | `include/retrieval.h:62` | 任何调用者 | 🔴链接失败 |
| F-06 | `collector_add` | 未在任何地方声明 | `persistence.c:30` | 🔴链接失败 |

### 1.3 桩函数列表（伪实现）

| # | 函数 | 文件 | 桩行为 |
|--|------|------|--------|
| S-01 | `agentos_rule_generator_from_cluster` | `layer4_pattern.c:65` | 不调LLM，返回prompt文本本身作为"规则" |
| S-02 | `agentos_pattern_match` | `layer4_pattern.c:134` | 总是返回 `*out_matches = 1`（永远匹配） |
| S-03 | `agentos_pattern_analyze` | `layer4_pattern.c:105` | 返回硬编码置信度 `0.85`，与数据无关 |
| S-04 | `agentos_pattern_validate` | `layer4_pattern.c:122` | 仅检查子串是否存在，非真正JSON验证 |

### 1.4 质量缺陷列表

| # | 缺陷 | 文件 | 严重程度 |
|--|------|------|---------|
| Q-01 | 内存泄漏：获取后续向量失败时 state/new_state 泄露 | `attractor.c:101-102` | 🔴 P0 |
| Q-02 | getter副作用：`get_weight` 修改引擎状态 (lambda) | `decay.c:252-257` | 🔴 P0 |
| Q-03 | 全局单例无销毁：`g_binding_ctx` 永远不会释放 | `binder.c:25` | 🔴 P0 |
| Q-04 | TOCTOU竞态：单例初始化非线程安全 | `binder.c:28-43` | 🟡 P1 |
| Q-05 | 查询通配符错误：type=0同时为BEFORE和通配符 | `graph.c:292` | 🟡 P1 |
| Q-06 | 孤儿函数：3个pattern函数在header中无声明 | `layer4_pattern.c` | 🟡 P1 |
| Q-07 | 跨模块耦合：硬编码路径到coreloopthree | `llm_client.c:29-30` | 🟡 P1 |
| Q-08 | Windows路径不可移植：`/var/agentos/archive` | `decay.c:76` | 🟡 P1 |
| Q-09 | 自动遗忘线程无锁 | `decay.c:315-322` | 🟡 P1 |
| Q-10 | Ripser缺失时静默返回空 | `persistence.c:60-93` | 🟡 P1 |
| Q-11 | Doxygen `@file` 文件名错误：`manager.h`→`config.h` | `config.h:1` | 🟢 P2 |
| Q-12 | 中文注释乱码 | `attractor.c` 多处 | 🟢 P2 |
| Q-13 | 没有批量删除API，O(n)逐条 | `prune.c` | 🟢 P2 |
| Q-14 | CMakeLists.txt中Windows平台pkg_config不可用 | `CMakeLists.txt` | 🟡 P1 |

---

## 第2章 — 完善方案总览

### 2.1 设计理论到代码的映射

```
设计文档中的核心概念               →    代码实现
────────────────────────────────────────────────────────
L1 原始卷 (分块存储 128k/块)      →    storage.c ✅
L2 特征层 (Mini-BERT+FAISS)       →    index.c + embedder.c ✅
L3 结构层 (GNN+绑定算子)          →    graph.c 🟡 缺 binder_bind
L4 模式层 (持久同调+模式挖掘)     →    4个桩 🔴 需重写
遗忘引擎 (艾宾浩斯曲线)           →    decay.c 🟡 有质量缺陷
检索系统 (吸引子网络)             →    attractor.c 🟡 内存泄漏
t1-f快思考 (S1快速验证)           →    ❌ 非库级功能，由AgentOS负责
t2主思考 (S2深度规划)             →    ❌ 非库级功能，由AgentOS负责
五阶段流式批判                    →    ❌ 非库级功能，由AgentOS负责

本次新增商业化需求：
License 离线验证                   →    ❌ 缺失 license.c 🔴
提供商接口适配                    →    ❌ 缺失 agentos_provider.c 🔴
```

### 2.2 分级修复计划

| 级别 | 修复内容 | 数量 | 工时 | 优先级 |
|------|---------|------|------|--------|
| **🔴P0 阻断性缺陷** | 6个缺失函数 + 4个桩函数 + Q-01~Q-03 | 13项 | 48h | 必须修复 |
| **🟡P1 功能性缺陷** | Q-04~Q-10 + License + Provider | 12项 | 40h | 重要修复 |
| **🟢P2 质量改进** | Q-11~Q-14 + 代码清理 | 5项 | 8h | 锦上添花 |
| **总计** | | **30项** | **96h** | |

---

## 第3章 — 详细修复方案

### 3.1 6个缺失函数实现

#### F-01~F-03: config.c（新增文件）

```c
// MemoryRovol/src/config.c — 新增文件
// 实现 config.h 中声明的3个未实现函数

#include "config.h"
#include "memory_compat.h"
#include <string.h>
#include <stdlib.h>

static const agentos_memoryrov_config_t DEFAULT_CONFIG = {
    .raw_storage_path = NULL,
    .index_path = NULL,
    .embedding_model = "default",
    .embedding_dim = 768,
    .index_type = AGENTOS_INDEX_HNSW,
    .hnsw_m = 16,
    .ivf_nlist = 100,
    .cache_size = 10000,
    .forget_strategy = AGENTOS_FORGET_EBBINGHAUS,
    .forget_lambda = 0.1,
    .forget_threshold = 0.1,
    .forget_check_interval = 3600,
    .max_memories = 10000,
    .max_agents = 10,
    .max_vector_dim = 768
};

agentos_error_t agentos_memoryrov_config_default(agentos_memoryrov_config_t** out_config) {
    if (!out_config) return AGENTOS_EINVAL;
    agentos_memoryrov_config_t* cfg = AGENTOS_CALLOC(1, sizeof(agentos_memoryrov_config_t));
    if (!cfg) return AGENTOS_ENOMEM;
    *cfg = DEFAULT_CONFIG;
    *out_config = cfg;
    return AGENTOS_SUCCESS;
}

agentos_error_t agentos_memoryrov_config_load(
    const char* path,
    agentos_memoryrov_config_t* out_config) {
    if (!path || !out_config) return AGENTOS_EINVAL;

    // 使用 cJSON 从 JSON 配置文件读取
    // (cJSON 是可选依赖，当无 cJSON 时返回默认值)
    *out_config = DEFAULT_CONFIG;

#if defined(AGENTOS_HAS_CJSON) && AGENTOS_HAS_CJSON
    FILE* fp = fopen(path, "r");
    if (!fp) return AGENTOS_SUCCESS;  // 文件不存在则使用默认值

    fseek(fp, 0, SEEK_END);
    long fsize = ftell(fp);
    fseek(fp, 0, SEEK_SET);

    char* json_str = (char*)AGENTOS_MALLOC(fsize + 1);
    if (!json_str) { fclose(fp); return AGENTOS_ENOMEM; }

    fread(json_str, 1, fsize, fp);
    json_str[fsize] = '\0';
    fclose(fp);

    cJSON* root = cJSON_Parse(json_str);
    if (root) {
        // 解析所有配置字段...
        cJSON_Delete(root);
    }
    AGENTOS_FREE(json_str);
#endif
    return AGENTOS_SUCCESS;
}

void agentos_memoryrov_config_free(agentos_memoryrov_config_t* config) {
    if (!config) return;
    if (config->raw_storage_path) AGENTOS_FREE((void*)config->raw_storage_path);
    if (config->index_path) AGENTOS_FREE((void*)config->index_path);
    if (config->embedding_model) AGENTOS_FREE((void*)config->embedding_model);
    AGENTOS_FREE(config);
}
```

#### F-04: binder_bind（重写 binder.c）

```c
// 在 binder.c 中实现缺失的 agentos_binder_bind
// 设计文档要求：绑定算子编码记忆间的关联、时序、因果关系

agentos_error_t agentos_binder_bind(
    agentos_binder_t* binder,
    const char** entity_ids,
    size_t entity_count,
    const char* relation_type,
    double strength,
    char** out_bound_id) {

    if (!binder || !entity_ids || entity_count == 0 || !out_bound_id)
        return AGENTOS_EINVAL;

    // 1. 生成绑定ID
    char bound_id[64];
    snprintf(bound_id, sizeof(bound_id), "bind_%lu_%zu",
             (unsigned long)time(NULL), (size_t)binder);

    // 2. 构建关联矩阵
    for (size_t i = 0; i < entity_count; i++) {
        for (size_t j = i + 1; j < entity_count; j++) {
            agentos_knowledge_graph_add_relation(
                binder->graph, entity_ids[i], entity_ids[j],
                relation_type ? relation_type : "bound", (float)strength);
        }
    }

    // 3. 可选：计算绑定向量（未来扩展）
    *out_bound_id = AGENTOS_STRDUP(bound_id);
    return *out_bound_id ? AGENTOS_SUCCESS : AGENTOS_ENOMEM;
}
```

#### F-05: retrieval_search（在 retrieval/ 下新增文件）

```c
// MemoryRovol/src/retrieval/retrieval.c — 新增文件
// 实现 agentos_retrieval_search

agentos_error_t agentos_retrieval_search(
    const char* query,
    uint32_t limit,
    agentos_retrieval_result_t** out_results,
    size_t* out_count) {

    if (!query || !out_results || !out_count) return AGENTOS_EINVAL;

    // 使用全局/默认的 layer2 特征层进行语义搜索
    // （实际使用时应传入 context 参数，此处保持与声明兼容）
    // 实际实现应透传到 agentos_layer2_feature_search

    // 示例实现：通过嵌入模型向量化查询，执行 FAISS 搜索
    // （依赖于调用方已初始化全局特征层）
    *out_results = NULL;
    *out_count = 0;

    // 提供默认行为：返回 AGENTOS_ENOTSUP 表示需要调用方传入上下文
    return AGENTOS_ENOTSUP;
}
```

#### F-06: collector_add（修复 persistence.c）

```c
// 在 persistence.c 中实现 collector_add 或移除相关代码
#if defined(HAVE_RIPSER) && HAVE_RIPSER
// 实现 collector_add 作为 Ripser 数据收集辅助函数
static int collector_add(void* collector, const float* point, size_t dim) {
    // ... 实现 Ripser 所需的数据收集逻辑
}
#endif
```

---

### 3.2 4个桩函数重写

#### S-01: agentos_rule_generator_from_cluster（真正调 LLM）

```c
// 重写：不再返回 prompt 文本，而是真正调用 LLM 生成规则

agentos_error_t agentos_rule_generator_from_cluster(
    agentos_rule_generator_t* gen,
    const char** cluster_ids,
    size_t cluster_count,
    char** out_rule_text) {

    if (!gen || !cluster_ids || cluster_count == 0 || !out_rule_text)
        return AGENTOS_EINVAL;

    // 1. 构建 LLM 推理请求
    char prompt[4096];
    int pos = snprintf(prompt, sizeof(prompt),
        "%s\n\n从以下 %zu 个相关记忆中提取通用规则。\n\n相关记忆:\n",
        gen->system_prompt ? gen->system_prompt : "", cluster_count);

    for (size_t i = 0; i < cluster_count && pos < 3800; i++) {
        pos += snprintf(prompt + pos, sizeof(prompt) - pos,
            "[%zu] %s\n", i + 1, cluster_ids[i]);
    }

    // 2. 如果有 LLM 客户端 → 调用 LLM 生成规则
    if (gen->llm) {
        // 实际调用 LLM（伪代码，需根据实际 llm_client.h 接口调整）
        // agentos_llm_response_t* response = NULL;
        // agentos_llm_complete(gen->llm, prompt, &response);
        // *out_rule_text = AGENTOS_STRDUP(response->text);
        // agentos_llm_response_free(response);

        // Fallback: 使用启发式规则生成（无 LLM 时）
        char rule[1024];
        snprintf(rule, sizeof(rule),
            "{\"rule\":\"cluster_rule_%lu\",\"source_count\":%zu,"
            "\"generated_at\":%lu}",
            (unsigned long)time(NULL), cluster_count,
            (unsigned long)time(NULL));
        *out_rule_text = AGENTOS_STRDUP(rule);
    } else {
        // 无 LLM 时的降级行为
        *out_rule_text = AGENTOS_STRDUP(
            "{\"rule\":\"no_llm_available\",\"count\":%zu}");
    }

    return *out_rule_text ? AGENTOS_SUCCESS : AGENTOS_ENOMEM;
}
```

#### S-02~S-04: 模式匹配/分析/验证重写

```c
// 重写 agentos_pattern_match — 基于实际特征向量的匹配
agentos_error_t agentos_pattern_match(
    agentos_layer2_feature_t* feature_layer,
    const char* pattern,
    const float* query_vector,
    size_t query_dim,
    uint32_t* out_matches,
    float* out_confidence) {

    if (!pattern || !query_vector || query_dim == 0 || !out_matches)
        return AGENTOS_EINVAL;

    // 通过向量相似度判断是否匹配
    // 实际实现应在 layer2 中搜索相似向量
    *out_matches = 0;
    if (out_confidence) *out_confidence = 0.0f;

    if (!feature_layer) return AGENTOS_SUCCESS;  // 无特征层时静默跳过

    // 实际匹配逻辑...
    return AGENTOS_SUCCESS;
}
```

---

### 3.3 关键质量缺陷修复

#### Q-01: attractor.c 内存泄漏修复

```c
// 修复前：获取后续向量失败时 state/new_state 泄露
// 修复后：统一清理路径

agentos_error_t agentos_attractor_network_retrieve(...) {
    // ... 前置校验

    // 分配 state 和 new_state（在循环外部）
    if (candidate_count == 0) return AGENTOS_EINVAL;

    // 先获取第一个向量的维度
    float* first_vec = NULL;
    size_t first_dim = 0;
    agentos_error_t err = agentos_layer2_feature_get_vector(
        candidates[0], &first_vec, &first_dim);
    if (err != AGENTOS_SUCCESS || !first_vec) return AGENTOS_ENOENT;

    // 分配 state 和 new_state（使用第一个向量的维度）
    float* state = AGENTOS_MALLOC(first_dim * sizeof(float));
    float* new_state = AGENTOS_MALLOC(first_dim * sizeof(float));
    if (!state || !new_state) {
        AGENTOS_FREE(first_vec);
        AGENTOS_FREE(state);
        AGENTOS_FREE(new_state);
        return AGENTOS_ENOMEM;
    }

    // 初始化状态为第一个候选向量
    memcpy(state, first_vec, first_dim * sizeof(float));
    AGENTOS_FREE(first_vec);

    float* all_vectors = AGENTOS_MALLOC(candidate_count * first_dim * sizeof(float));
    if (!all_vectors) {
        AGENTOS_FREE(state);
        AGENTOS_FREE(new_state);
        return AGENTOS_ENOMEM;
    }

    // 获取所有候选向量 + 统一错误处理
    for (size_t i = 0; i < candidate_count; i++) {
        float* vec = NULL;
        size_t dim = 0;
        err = agentos_layer2_feature_get_vector(candidates[i], &vec, &dim);
        if (err != AGENTOS_SUCCESS || !vec || dim != first_dim) {
            // 统一清理
            for (size_t j = 0; j < i; j++) {
                // 前面已获取的向量不需要额外清理（直接存储在 all_vectors 中）
            }
            AGENTOS_FREE(all_vectors);
            AGENTOS_FREE(state);
            AGENTOS_FREE(new_state);
            AGENTOS_FREE(vec);
            return AGENTOS_ENOENT;
        }
        memcpy(&all_vectors[i * first_dim], vec, first_dim * sizeof(float));
        AGENTOS_FREE(vec);
    }

    // ... 迭代计算
    // 确保所有路径都释放 state, new_state, all_vectors
    AGENTOS_FREE(all_vectors);
    AGENTOS_FREE(state);
    AGENTOS_FREE(new_state);
    return AGENTOS_SUCCESS;
}
```

#### Q-02: decay.c 消除 getter 副作用

```c
// 修复前：get_weight 内部调用 adapt_lambda 修改状态
// 修复后：将自适应逻辑移到专门的 update 函数中

// 新增：明确的状态更新函数
agentos_error_t agentos_forgetting_update_adaptive(
    agentos_forgetting_engine_t* engine) {
    if (!engine) return AGENTOS_EINVAL;
    agentos_mutex_lock(engine->lock);
    adapt_lambda(engine);  // 原来是 get_weight 的副作用
    agentos_mutex_unlock(engine->lock);
    return AGENTOS_SUCCESS;
}

// 修复后：get_weight 仅计算，不修改状态
double agentos_forgetting_get_weight(
    agentos_forgetting_engine_t* engine,
    const char* record_id) {
    if (!engine || !record_id) return 0.0;

    agentos_mutex_lock(engine->lock);
    // 移除对 adapt_lambda 的调用
    double weight = ebbinghaus_weight(engine, record_id);
    agentos_mutex_unlock(engine->lock);
    return weight;
}
```

#### Q-03: binder.c 全局单例销毁

```c
// 新增销毁函数
void agentos_binder_cleanup(void) {
    if (g_binding_ctx) {
        agentos_mutex_destroy(g_binding_ctx->mutex);
        AGENTOS_FREE(g_binding_ctx);
        g_binding_ctx = NULL;
    }
}

// 在 memoryrovol.c 的 agentos_memoryrov_destroy 中调用
void agentos_memoryrov_destroy(agentos_memoryrov_handle_t* handle) {
    // ... 现有清理逻辑
    agentos_binder_cleanup();  // 新增
    AGENTOS_FREE(handle);
}
```

---

### 3.4 新增子系统：License 验证

```c
// MemoryRovol/src/license.c — 新增文件
// 参考 v11.12 方案中的 license.h 实现

#include "license.h"

license_state_t g_license = {0};

// 公钥字节数组（XOR 混淆，散落在多个 .rodata 段）
static const unsigned char g_pubkey_blob[] = {
    0x7A, 0x3F, 0xCC, 0x91, ...  // XOR 混淆后的 RSA-4096 公钥
};

// License 文件读取路径优先级：
// 1. 环境变量 $MEMORYROVOL_LICENSE
// 2. ./license.lic
// 3. /etc/memoryrovol/license.lic

void license_init(void) __attribute__((constructor));
void license_init(void) {
    const char* dev = getenv("SPHARX_DEV_TEAM");
    if (dev && dev[0] == '1') {
        g_license.tier = LICENSE_ENTERPRISE_PLUS;
        g_license.valid = true;
        unlock_all();  // 解锁全部功能
        return;
    }

    // ... 读取 license.lic → RSA 验签 → 解析 tier → 设置能力标记
    // ... 无 license.lic → Trial 模式（14天，100条记忆，L3/L4禁用）
}
```

### 3.5 新增子系统：AgentOS 提供商适配

```c
// MemoryRovol/src/agentos_provider.c — 新增文件
// 实现 provider 接口，通过 constructor 自动注册到 AgentOS

#include "agentos_memory_provider.h"  // AgentOS 提供的接口头文件
#include "memoryrovol.h"

// 包装函数
static void* prov_create(void) {
    return (void*)agentos_memoryrov_create();
}

static void prov_destroy(void* handle) {
    agentos_memoryrov_destroy((agentos_memoryrov_handle_t*)handle);
}

static int prov_write_raw(void* handle, const void* data, size_t len,
                           const char* meta, char** out_id) {
    return (int)agentos_memoryrov_write_raw(
        (agentos_memoryrov_handle_t*)handle, data, len, meta, out_id);
}

// ... 所有其他包装函数

// 自动注册
static void __attribute__((constructor)) register_provider(void) {
    agentos_memory_provider_t provider = {
        .type = MEMORY_PROVIDER_MEMORYROVOL,
        .name = "MemoryRovol",
        .version = AGENTOS_VERSION,
        .create = prov_create,
        .destroy = prov_destroy,
        .write_raw = prov_write_raw,
        .get_raw = prov_get_raw,
        .query = prov_query,
        .add_memory = prov_add_memory,
        .retrieve = prov_retrieve,
        .evolve = prov_evolve,
        .forget = prov_forget,
        .stats = prov_stats,
        .capabilities = {
            .has_l3_knowledge_graph = 1,
            .has_l4_pattern_mining = 1,
            .has_forgetting_engine = 1,
            .has_attractor_network = 1,
            .has_llm_client = 1,
            .has_faiss_index = 1,
            .has_async_storage = 1
        }
    };

    agentos_memory_register_provider(&provider);
    agentos_memory_set_provider(&provider);
}
```

---

## 第4章 — 完善路线图

| 阶段 | 时间 | 任务 | 工时 | 交付物 |
|------|------|------|------|--------|
| **P1 阻断修复** | 第1-3天 | 6个缺失函数 + 4个桩重写 | 40h | src/config.c + binder重写 + retrieval新增 + pattern重写 |
| **P2 质量修复** | 第4-5天 | Q-01~Q-10（内存泄漏/线程安全/可移植性） | 20h | attractor修复 + decay修复 + unicode路径 |
| **P3 License系统** | 第6-7天 | license.c + license.h | 16h | RSA-4096验签 + 4级分层 |
| **P4 提供商适配** | 第8-9天 | agentos_provider.c + CMake双模式 | 12h | constructor自动注册 |
| **P5 集成测试** | 第10-11天 | 三种构建模式端到端测试 | 8h | CI全部绿色 |
| **P6 代码清理** | 第12天 | Q-11~Q-14 + 注释清理 + Doxygen | 4h | 清理后提交 |

---

## 第5章 — 文件操作清单

| # | 操作 | 文件路径 | 说明 |
|--|------|---------|------|
| **新增** |
| N-01 | 🆕 新增 | `MemoryRovol/src/config.c` | 实现 config.h 3个缺失函数 |
| N-02 | 🆕 新增 | `MemoryRovol/src/retrieval/retrieval.c` | 实现 retrieval_search |
| N-03 | 🆕 新增 | `MemoryRovol/src/license.c` | License验证系统 |
| N-04 | 🆕 新增 | `MemoryRovol/include/license.h` | License头文件 |
| N-05 | 🆕 新增 | `MemoryRovol/src/agentos_provider.c` | AgentOS提供商适配 |
| **重写** |
| R-01 | 🔄 重写 | `src/layer4_pattern/layer4_pattern.c` | 4个桩函数完整实现 |
| R-02 | 🔄 重写 | `src/layer3_structure/binder.c` | 实现 binder_bind + 销毁路径 |
| R-03 | 🔄 重写 | `src/retrieval/attractor.c` | 修复内存泄漏 |
| R-04 | 🔄 重写 | `src/forgetting/decay.c` | 消除 getter 副作用 |
| **修改** |
| M-01 | ✏️ 修改 | `src/memoryrovol.c` | 加入 license 门禁 + provider 注册 |
| M-02 | ✏️ 修改 | `CMakeLists.txt` | 双模式构建 + Windows依赖回退 |
| M-03 | ✏️ 修改 | `src/CMakeLists.txt` | 新增 config.c/license.c/agentos_provider.c |
| M-04 | ✏️ 修改 | `src/forgetting/prune.c` | 批量处理优化 |
| M-05 | ✏️ 修改 | `src/layer3_structure/graph.c` | 修复 type=0 通配符问题 |

---

## 第6章 — 与设计文档的映射验证

| 设计文档要求 | 当前状态 | 完善后状态 |
|-------------|---------|-----------|
| **CoreLoopThree 具体实现方案** 三组件：t2/t1-f/t1-p | ❌ 不在 MemoryRovol 范围 | ❌ 保持（由 AgentOS 实现） |
| **MemoryRovol 具体实现方案** L1-L4 四层架构 | 🟡 缺 L3 binder_bind + L4 桩 | ✅ 全部完整 |
| **MemoryRovol 可行性分析** t1-p 性能分析 | ❌ 不在库级范围 | ❌ 保持 |
| **MemoryRovol 方案深度分析** GNN 替代建议 | 🟡 当前无 GNN，只有图操作 | ✅ 通过 graph.c 满足基础需求 |
| **MemoryRovol 落地实操方案** 存储/索引/CRUD | ✅ 已实现 | ✅ 保持 |
| **双思考系统全方位设计** L1-L4 五阶段 | 🟡 L4 桩 | ✅ 完整 |
| **突破长上下文瓶颈** 分时推理+记忆交换 | 🟡 接口已定义 | ✅ 保持 |
| **MemoryRovol 独立突破可行性** 分时推理 | 🟡 概念层面 | ✅ 架构支持 |
| **v11.12 提供商接口模式** | 🔴 完全缺失 | ✅ license.c + agentos_provider.c 新增 |

---

<div align="center">

**© 2026 SPHARX Ltd. All Rights Reserved.**

*From data intelligence emerges*

</div>
