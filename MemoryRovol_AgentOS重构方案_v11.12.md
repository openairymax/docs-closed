# MemoryRovol × AgentOS 内存子系统重构方案 v11.12

**版本**: v11.12.0-第09大轮次·开源底座+商业增强  
**核心架构**: 将 MemoryRovol 全部源码移出 AgentOS，AgentOS 内置免费开源内存子系统  
**日期**: 2026-04-29

---

> **核心设计哲学**：
> AgentOS 提供业界标准的**免费开源内存能力**（L1+L2 基础版），任何人都可以编译运行。
> MemoryRovol 是**企业级增强插件**，提供 L3+L4+遗忘引擎等高级功能，需付费购买预编译库。
> 用户不付费→ AgentOS 功能完整可用的基本记忆系统。付费→ 解锁全功能记忆增强。

---

## 第1章 — 架构概览

### 1.1 "三明治"架构

```
┌─────────────────────────────────────────────────────────────────┐
│  CoreLoopThree (认知循环)                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  记忆引擎 (engine.c) — 不变的抽象层                        │  │
│  │  agentos_memory_create() → agentos_memory_write() → ...   │  │
│  └───────────────────────┬───────────────────────────────────┘  │
│                          │ 通过统一接口调用                       │
│                          ▼                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  内存提供商接口层 (memory_provider.h) ⭐ 新增               │  │
│  │  定义所有内存操作的回调函数指针表                            │  │
│  └──────────────┬─────────────────────────┬───────────────────┘  │
│                 │                          │                      │
│                 ▼                          ▼                      │
│  ┌────────────────────────┐  ┌────────────────────────────┐     │
│  │  AgentOS 内置提供商    │  │  MemoryRovol 商业插件     │     │
│  │  (agentos/atoms/memory)│  │  (外部预编译库)            │     │
│  │  • L1 文件存储         │  │  • L1 异步存储引擎        │     │
│  │  • L2 简单向量索引     │  │  • L2 FAISS 向量索引      │     │
│  │  • 基础检索            │  │  • L3 知识图谱            │     │
│  │  ❌ L3知识图谱❌       │  │  • L4 模式挖掘            │     │
│  │  ❌ L4模式挖掘❌       │  │  • 遗忘引擎               │     │
│  │  ❌ 遗忘引擎❌         │  │  • DS-004 LLM             │     │
│  │  开源 / 免费用          │  │  闭源 / 需购买 License    │     │
│  └────────────────────────┘  └────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 核心设计原则

| 原则 | 说明 |
|------|------|
| **🔌 提供商模式** | 内存操作通过 `agentos_memory_provider_t` 结构体（函数指针表）调用，运行时决定使用哪个提供商 |
| **📦 源码完全分离** | AgentOS `atoms/memory/` 目录不含任何 MemoryRovol 源码。MemoryRovol 源码仅在独立仓库 |
| **🆓 默认可用** | 默认使用 AgentOS 内置提供商——零依赖、零配置、零费用即可拥有完整基础记忆能力 |
| **🚀 即插即增强** | 链接 MemoryRovol `.a`/`.lib` 后自动检测并启用——不修改任何 AgentOS 代码 |
| **🔒 源码零泄露** | MemoryRovol 的 L3/L4/遗忘引擎等高级算法不会以任何形式出现在 AgentOS 开源仓库中 |

### 1.3 文件布局变更

```
AgentOS (变更后)                                MemoryRovol (独立仓库)
─────────────────────────                      ────────────────────────
agentos/atoms/
├── memory/            ← 新增: 内置提供商       src/
│   ├── include/                                ├── agentos_provider.c ← 新增
│   │   ├── memory_provider.h  ← 接口定义        ├── license.c
│   │   └── builtin_provider.h                   ├── memoryrovol.c
│   ├── src/                                     ├── layer1_raw/
│   │   ├── builtin_storage.c                    ├── layer2_feature/
│   │   ├── builtin_index.c                      ├── layer3_structure/
│   │   └── builtin_retrieval.c                  ├── layer4_pattern/
│   └── CMakeLists.txt                           ├── forgetting/
│                                                 ├── retrieval/
├── coreloopthree/src/memory/                     ├── llm_client.c
│   ├── engine.c          ← 不变(接口调整)        └── ...
│   ├── memory_provider.c ← 新增: 提供商选择
│   └── rov_ffi.h         ← 删除(移到MemoryRovol)
│
├── CMakeLists.txt         ← 删除 add_subdirectory(memoryrovol)
│
└── syscall/src/
    └── memory.c           ← 调整为使用 provider 接口

[moved] agentos/atoms/memoryrovol/  ← 整个目录删除！
```

---

## 第2章 — 提供商接口定义

### 2.1 统一内存提供商接口

```c
// agentos/atoms/memory/include/memory_provider.h
// AgentOS 内存提供商接口（函数指针表）

#ifndef AGENTOS_MEMORY_PROVIDER_H
#define AGENTOS_MEMORY_PROVIDER_H

#include "agentos.h"
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/** @brief 内存提供商类型 */
typedef enum {
    MEMORY_PROVIDER_BUILTIN = 0,  /**< AgentOS 内置（免费/开源） */
    MEMORY_PROVIDER_MEMORYROVOL = 1, /**< MemoryRovol（商业/预编译） */
    MEMORY_PROVIDER_CUSTOM = 2    /**< 用户自定义 */
} agentos_memory_provider_type_t;

/** @brief 内存提供商操作表（函数指针结构体） */
typedef struct agentos_memory_provider {
    agentos_memory_provider_type_t type;
    const char* name;
    const char* version;

    /* 生命周期 */
    void*   (*create)(void);
    void    (*destroy)(void* handle);
    int     (*init)(const void* config, void** out_handle);

    /* 核心操作 */
    int (*write_raw)(void* handle, const void* data, size_t len,
                     const char* metadata, char** out_record_id);
    int (*get_raw)(void* handle, const char* record_id,
                   void** out_data, size_t* out_len);
    int (*delete_raw)(void* handle, const char* record_id);
    int (*query)(void* handle, const char* query, uint32_t limit,
                 char*** out_ids, float** out_scores, size_t* out_count);
    int (*add_memory)(void* handle, const char* content, size_t len);
    int (*retrieve)(void* handle, const char* query, size_t max_results,
                    agentos_memory_t** out_results, size_t* out_count);
    int (*mount)(void* handle, const char* record_id, const char* context);
    int (*evolve)(void* handle, int force);
    int (*forget)(void* handle);
    int (*stats)(void* handle, char** out_json);
    int (*health_check)(void* handle, char** out_json);

    /* 能力标记 */
    struct {
        unsigned int has_l3_knowledge_graph : 1;
        unsigned int has_l4_pattern_mining  : 1;
        unsigned int has_forgetting_engine  : 1;
        unsigned int has_attractor_network  : 1;
        unsigned int has_llm_client         : 1;
        unsigned int has_faiss_index        : 1;
        unsigned int has_async_storage      : 1;
    } capabilities;
} agentos_memory_provider_t;

/** @brief 获取当前激活的内存提供商 */
const agentos_memory_provider_t* agentos_memory_get_provider(void);

/** @brief 注册一个自定义内存提供商（插件机制） */
int agentos_memory_register_provider(const agentos_memory_provider_t* provider);

/** @brief 设置激活的提供商 */
int agentos_memory_set_provider(const agentos_memory_provider_t* provider);

#ifdef __cplusplus
}
#endif

#endif /* AGENTOS_MEMORY_PROVIDER_H */
```

### 2.2 内置提供商能力说明（免费版）

```c
// AgentOS 内置提供商能力标记
static const agentos_memory_provider_t g_builtin_provider = {
    .type = MEMORY_PROVIDER_BUILTIN,
    .name = "AgentOS Built-in Memory",
    .version = "1.0.0",
    .create = builtin_create,
    .destroy = builtin_destroy,
    .init = builtin_init,
    .write_raw = builtin_write_raw,
    .get_raw = builtin_get_raw,
    .delete_raw = builtin_delete_raw,
    .query = builtin_query,
    .add_memory = builtin_add_memory,
    .retrieve = builtin_retrieve,
    .mount = builtin_mount,
    .evolve = builtin_evolve,
    .forget = builtin_forget,
    .stats = builtin_stats,
    .health_check = builtin_health_check,
    .capabilities = {
        .has_l3_knowledge_graph = 0,  // ❌ 无 L3
        .has_l4_pattern_mining  = 0,  // ❌ 无 L4
        .has_forgetting_engine  = 0,  // ❌ 无遗忘引擎
        .has_attractor_network  = 0,  // ❌ 无吸引子网络
        .has_llm_client         = 0,  // ❌ 无 LLM 客户端
        .has_faiss_index        = 0,  // ❌ 无 FAISS
        .has_async_storage      = 0,  // ❌ 无异步存储
    }
};
```

### 2.3 MemoryRovol 提供商能力说明（商业版）

```c
// MemoryRovol 注册时覆盖的能力标记
static const agentos_memory_provider_t g_memoryrovol_provider = {
    .type = MEMORY_PROVIDER_MEMORYROVOL,
    .name = "MemoryRovol Pro",
    .version = "1.0.0",
    // ... 所有函数指针指向 MemoryRovol 实现
    .capabilities = {
        .has_l3_knowledge_graph = 1,  // ✅ L3 知识图谱
        .has_l4_pattern_mining  = 1,  // ✅ L4 模式挖掘
        .has_forgetting_engine  = 1,  // ✅ 遗忘引擎
        .has_attractor_network  = 1,  // ✅ 吸引子网络
        .has_llm_client         = 1,  // ✅ DS-004 双思维
        .has_faiss_index        = 1,  // ✅ FAISS 索引
        .has_async_storage      = 1,  // ✅ 异步存储引擎
    }
};
```

---

## 第3章 — AgentOS 内置内存子系统（免费开源）

### 3.1 功能范围

| 功能 | 内置版 | MemoryRovol 版 |
|------|--------|----------------|
| **L1 原始存储** | ✅ 文件系统存储 | ✅ 异步引擎+分片+压缩 |
| **L1 元数据** | ✅ SQLite 索引 | ✅ SQLite + 高级元数据 |
| **L2 向量索引** | ✅ 简单内存哈希索引（O(n)检索） | ✅ FAISS (IVF/HNSW) |
| **L2 向量持久化** | ✅ JSON 文件持久化 | ✅ SQLite 向量存储 |
| **L2 嵌入** | ✅ 基础 TF-IDF/text 特征 | ✅ OpenAI/DeepSeek 嵌入 |
| **L2 检索** | ✅ 关键词+简单相似度 | ✅ 混合检索+重排序 |
| **L3 知识图谱** | ❌ | ✅ 绑定算子+GNN |
| **L4 模式挖掘** | ❌ | ✅ 持久同调+HDBSCAN |
| **遗忘引擎** | ❌ | ✅ 艾宾浩斯+多策略 |
| **吸引子网络** | ❌ | ✅ 完整迭代检索 |
| **DS-004 LLM** | ❌ | ✅ S2+S1 双思维 |
| **高级异步存储** | ❌ | ✅ 线程池+批量写入 |

### 3.2 内置提供商实现概要

```
agentos/atoms/memory/src/
├── builtin_provider.c       ← 提供商结构体注册
├── builtin_storage.c        ← L1 文件存储（简化版，无依赖）
├── builtin_index.c          ← L2 内存哈希索引（自实现，无FAISS依赖）
├── builtin_retrieval.c      ← 基础关键词+余弦相似度检索
└── builtin_utils.c          ← 公共工具（ID生成、JSON序列化）
```

关键简化设计——无外部依赖：

```c
// builtin_index.c
// 自实现的简单向量索引（不使用 FAISS）
// 适合 1 万条以下的小规模场景

typedef struct {
    char* id;
    float* vector;
    size_t dim;
    char* text_snippet;
} builtin_index_entry_t;

typedef struct {
    builtin_index_entry_t* entries;
    size_t count;
    size_t capacity;
    agentos_mutex_t* lock;
} builtin_index_t;

// 检索：O(n) 线性扫描余弦相似度
static int builtin_index_search(builtin_index_t* idx,
                                 const float* query, size_t dim,
                                 uint32_t limit,
                                 char*** out_ids, float** out_scores,
                                 size_t* out_count) {
    // 计算所有条目的余弦相似度
    // 用堆排序取 top-k
    // 返回结果
}
```

### 3.3 能力检测与降级

```c
// engine.c — 统一入口，根据提供商能力自动降级

agentos_error_t agentos_memory_evolve(
    agentos_memory_engine_t* engine, int force) {
    if (!engine) return AGENTOS_EINVAL;

    const agentos_memory_provider_t* provider = engine->provider;

    // 检查提供商是否支持 evolve
    if (!provider->evolve) {
        AGENTOS_LOG_DEBUG("memory: evolve not supported by current provider");
        return AGENTOS_SUCCESS;  // 静默跳过，不报错
    }

    // 检查是否有高级 evolve 能力 (L3+L4)
    if (!provider->capabilities.has_l3_knowledge_graph &&
        !provider->capabilities.has_l4_pattern_mining) {
        AGENTOS_LOG_DEBUG("memory: basic provider, evolve is no-op");
        return AGENTOS_SUCCESS;
    }

    return provider->evolve(engine->provider_handle, force);
}
```

---

## 第4章 — MemoryRovol 作为外部插件

### 4.1 插件注册机制

MemoryRovol 预编译库通过初始化函数向 AgentOS 注册自身：

```c
// memoryrovol_provider.c — 在 MemoryRovol 独立仓库中
// 编译到 libmemoryrovol.a 中

#include "memoryrovol.h"
#include "agentos_memory_provider.h"  // AgentOS 提供的接口头文件

// MemoryRovol 的提供商包装器
static void* memoryrovol_create(void) {
    return agentos_memoryrov_create();
}

static void memoryrovol_destroy(void* handle) {
    agentos_memoryrov_destroy((agentos_memoryrov_handle_t*)handle);
}

// ... 所有包装函数

// 在加载时自动注册（__attribute__((constructor))）
static void __attribute__((constructor)) memoryrovol_register(void) {
    agentos_memory_provider_t provider = {
        .type = MEMORY_PROVIDER_MEMORYROVOL,
        .name = "MemoryRovol",
        .version = "1.0.0",
        .create = memoryrovol_create,
        .destroy = memoryrovol_destroy,
        .write_raw = memoryrovol_write_raw_wrapper,
        // ... 所有函数注册
        .capabilities = {
            .has_l3_knowledge_graph = 1,
            .has_l4_pattern_mining = 1,
            .has_forgetting_engine = 1,
            .has_attractor_network = 1,
            .has_llm_client = 1,
            .has_faiss_index = 1,
            .has_async_storage = 0,  // License 控制
        }
    };

    agentos_memory_register_provider(&provider);
    agentos_memory_set_provider(&provider);
}
```

### 4.2 AgentOS 端检测插件是否存在

```c
// coreloopthree/src/memory/memory_provider.c
// 运行时检测 MemoryRovol 插件

#include "memory_provider.h"

static const agentos_memory_provider_t* g_active_provider = NULL;

// 默认使用内置提供商
static const agentos_memory_provider_t* g_builtin_provider_ptr = NULL;

void agentos_memory_init_providers(void) {
    // 1. 注册内置提供商
    static agentos_memory_provider_t builtin = { ... };
    g_builtin_provider_ptr = &builtin;
    agentos_memory_register_provider(&builtin);

    // 2. 尝试检查是否已有外部插件注册
    //    （MemoryRovol 的 constructor 应该已经执行过了）
    if (!g_active_provider) {
        // 没有外部插件 → 使用内置
        g_active_provider = g_builtin_provider_ptr;
        AGENTOS_LOG_INFO("memory: using built-in provider (free)");
    } else {
        AGENTOS_LOG_INFO("memory: using %s (%s)",
                        g_active_provider->name,
                        g_active_provider->type == MEMORY_PROVIDER_MEMORYROVOL
                            ? "commercial license" : "custom");
    }
}

const agentos_memory_provider_t* agentos_memory_get_provider(void) {
    return g_active_provider;
}
```

### 4.3 用户使用流程

```
场景 A：免费用户（使用内置提供商）
┌──────────────────────────────────────────────┐
│ cmake -B build                                │
│ cmake --build build                            │
│                                                │
│ AgentOS 启动日志：                               │
│ [INFO] memory: using built-in provider (free)   │
│ [INFO] memory: L1 + L2 ready for use           │
│                                                │
│ ✅ 所有基础功能正常                              │
│ ✅ 写入、检索、存储                              │
│ ❌ 无 L3 知识图谱                               │
│ ❌ 无 L4 模式挖掘                               │
└──────────────────────────────────────────────┘

场景 B：付费用户（使用 MemoryRovol 插件）
┌──────────────────────────────────────────────┐
│ wget https://spharx.cn/memoryrovol-pro.a      │
│ cmake -B build \                              │
│   -DMEMORYROVOL_PRO_LIB=/path/to/lib.a \      │
│   -DMEMORYROVOL_PRO_LIC=license.lic           │
│ cmake --build build                            │
│                                                │
│ AgentOS 启动日志：                               │
│ [INFO] memory: using MemoryRovol (commercial)  │
│ [INFO] memory: L3 knowledge graph enabled     │
│ [INFO] memory: L4 pattern mining enabled      │
│                                                │
│ ✅ 全功能解锁                                   │
│ ✅ L3 知识图谱                                  │
│ ✅ L4 模式挖掘                                  │
│ ✅ 遗忘引擎 + 吸引子网络                          │
└──────────────────────────────────────────────┘
```

---

## 第5章 — 全量迁移方案（53个文件逐一处理）

### 5.1 文件操作清单

| # | 文件路径 | 操作 | 变更说明 |
|---|---------|------|---------|
| **模块1：内存核心集成（4个文件）** |
| 1 | `atoms/coreloopthree/src/memory/engine.c` | 🔄 **重写** | 从固定调用 memoryrov_* 改为通过 provider 接口调用 |
| 2 | `atoms/coreloopthree/src/memory/rov_ffi.h` | 🗑️ **删除** | 移到 MemoryRovol 仓库 |
| 3 | `atoms/coreloopthree/src/memory/memory_provider.c` | 🆕 **新建** | 提供商选择逻辑 + 注册管理 |
| 4 | `atoms/coreloopthree/src/memory/memory_service.c` | 🔄 **调整** | 调用 `engine->provider->write_raw` |
| **模块2：系统调用（2个文件）** |
| 5 | `atoms/syscall/src/memory.c` | 🔄 **调整** | 从直接调用 memoryrov_* 改为通过 `agentos_memory_get_provider()` |
| 6 | `atoms/syscall/src/syscall_entry.c` | 🔄 **调整** | 移除 `#include "memoryrovol.h"` |
| **模块3：Daemon Orchestrator（2个文件）** |
| 7 | `daemon/common/src/orchestrator.c` | 🔄 **重写** | 70行~400行共11处 memoryrov_* 调用全部改为 provider 接口 |
| 8 | `daemon/common/CMakeLists.txt` | 🔄 **调整** | 移除 `agentos_memoryrovol` 链接 + `includes/memoryrovol` 路径 |
| **模块4：Heapstore（2个文件）** |
| 9 | `heapstore/src/heapstore_integration.c` | 🔄 **调整** | 改为通过 provider 接口 |
| 10 | `heapstore/include/heapstore_integration.h` | 🔄 **调整** | 更新类型引用 |
| **模块5：Cognition（2个文件）** |
| 11 | `atoms/coreloopthree/src/cognition/planner/reflective.c` | 🔄 **调整** | 移除相对路径 `#include "../../../../memoryrovol/include/llm_client.h"` |
| 12 | `atoms/coreloopthree/src/cognition/CMakeLists.txt` | 🔄 **调整** | 移除 `memoryrovol/include` 路径 + `agentos_memoryrovol` 链接 |
| **模块6：构建系统（4个文件）** |
| 13 | `atoms/CMakeLists.txt` | 🔄 **调整** | 删除 memoryrovol 的 include 路径、add_subdirectory、install |
| 14 | `atoms/atoms/memory/CMakeLists.txt` | 🆕 **新建** | 内置提供商构建配置 |
| 15 | `atoms/coreloopthree/CMakeLists.txt` | 🔄 **调整** | 移除 `memoryrovol/src` 路径 + `agentos_memoryrovol` 链接 |
| 16 | `agentos/CMakeLists.txt` | 🔄 **调整** | 确保新 atoms/memory 被编译 |
| **模块7：测试文件（10个文件）** |
| 17 | `atoms/coreloopthree/tests/unit/test_cl3_stubs.c` | 🗑️ **删除** | 不再需要 memoryrov FFI stubs（改用 provider 模式） |
| 18 | `atoms/coreloopthree/tests/CMakeLists.txt` | 🔄 **调整** | 移除 memoryrovol 相关 |
| 19-22 | `tests/unit/atoms/memoryrovol/*` | 🗑️ **删除** | 整个测试目录移到 MemoryRovol 仓库 |
| 23 | `atoms/memoryrovol/tests/*` | 🗑️ **删除** | 整个测试目录移到 MemoryRovol 仓库 |
| **模块8：脚本和配置（3个文件）** |
| 24 | `.clangd` | 🔄 **调整** | 移除 `-Iagentos/atoms/memoryrovol/include` |
| 25 | `scripts/pipeline/security_regression.sh` | 🔄 **调整** | 移除 memoryrovol 路径 |
| 26 | `scripts/pipeline/quality-gate.sh` | 🔄 **调整** | 移除 memoryrovol 路径 |
| **模块9：文档和README（8个文件）** |
| 27-34 | `README.md`, `atoms/README.md`, 等 | 🔄 **调整** | 更新路径描述 |
| **模块10：MemoryRovol 源码（~19个文件）** |
| 35-53 | `atoms/memoryrovol/*` | 🗑️ **全部删除** | 所有源码移到 MemoryRovol 独立仓库 |

### 5.2 engine.c 核心变更（示例）

```c
// engine.c (重写后)
// 改为通过 provider 接口调用

#include "memory_provider.h"

struct agentos_memory_engine {
    const agentos_memory_provider_t* provider;  // ← 新增
    void* provider_handle;                       // ← 新增（原rov_handle）
    agentos_mutex_t* lock;
    char* config_path;
};

agentos_error_t agentos_memory_create(
    const char* config_path,
    agentos_memory_engine_t** out_engine) {

    agentos_memory_engine_t* engine = AGENTOS_CALLOC(1, sizeof(*engine));

    // 获取当前激活的提供商
    engine->provider = agentos_memory_get_provider();
    if (!engine->provider || !engine->provider->create) {
        AGENTOS_FREE(engine);
        return AGENTOS_ENOTINIT;
    }

    // 通过提供商创建实例
    engine->provider_handle = engine->provider->create();
    if (!engine->provider_handle) {
        // 降级：尝试内置提供商
        engine->provider = get_builtin_provider();
        engine->provider_handle = engine->provider->create();
        if (!engine->provider_handle) {
            AGENTOS_FREE(engine);
            return AGENTOS_ENOMEM;
        }
        AGENTOS_LOG_WARN("memory: falling back to built-in provider");
    }

    engine->lock = agentos_mutex_create();
    *out_engine = engine;
    return AGENTOS_SUCCESS;
}

agentos_error_t agentos_memory_write(
    agentos_memory_engine_t* engine,
    const agentos_memory_record_t* record,
    char** out_record_id) {

    if (!engine || !engine->provider || !engine->provider->write_raw)
        return AGENTOS_EINVAL;

    char metadata[1024];
    snprintf(metadata, sizeof(metadata), ...);

    agentos_mutex_lock(engine->lock);
    agentos_error_t err = engine->provider->write_raw(
        engine->provider_handle,
        record->memory_record_data,
        record->memory_record_data_len,
        metadata,
        out_record_id);
    agentos_mutex_unlock(engine->lock);

    return err;
}
```

### 5.3 移除 memoryrovol/ 目录后的目录树

```
agentos/atoms/  (变更后)
├── CMakeLists.txt           ← 删除 add_subdirectory(memoryrovol)
├── corekern/
├── coreloopthree/
├── memory/                  ← ✨ 新增：内置内存提供商
│   ├── CMakeLists.txt
│   ├── include/
│   │   └── memory_provider.h
│   └── src/
│       ├── builtin_provider.c
│       ├── builtin_storage.c
│       ├── builtin_index.c
│       └── builtin_retrieval.c
├── syscall/
└── taskflow/

🗑️ memoryrovol/  ← 完全删除
```

---

## 第6章 — CMake 双模式构建（更新版）

### 6.1 新的 CMake 选项

```cmake
# agentos/atoms/CMakeLists.txt
cmake_minimum_required(VERSION 3.20)
project(agentos-kernel VERSION 1.0.0.6 LANGUAGES C CXX)

# MemoryRovol 集成选项
option(MEMORYROVOL_ENABLE "Enable MemoryRovol commercial provider" OFF)

if(MEMORYROVOL_ENABLE)
    # 要求用户指定预编译库路径
    if(NOT DEFINED MEMORYROVOL_LIB_PATH)
        message(FATAL_ERROR "MEMORYROVOL_ENABLE requires MEMORYROVOL_LIB_PATH")
    endif()

    # 导入预编译库
    add_library(agentos_memoryrovol STATIC IMPORTED)
    set_target_properties(agentos_memoryrovol PROPERTIES
        IMPORTED_LOCATION "${MEMORYROVOL_LIB_PATH}")
    
    # MemoryRovol 头文件（仅有接口头文件，无源码）
    target_include_directories(agentos_memoryrovol INTERFACE
        "${MEMORYROVOL_INCLUDE_PATH}")

    message(STATUS "MemoryRovol commercial provider enabled: ${MEMORYROVOL_LIB_PATH}")
else()
    # 编译内置提供商（默认）
    add_subdirectory(memory)
    message(STATUS "MemoryRovol disabled, using built-in provider (free)")
endif()

# 始终编译核心模块
add_subdirectory(corekern)
add_subdirectory(coreloopthree)
add_subdirectory(syscall)
add_subdirectory(taskflow)
```

### 6.2 三种构建模式对照

| 模式 | CMake 命令 | 内存提供商 | 适用场景 |
|------|-----------|-----------|---------|
| **1. 纯开源** | `cmake -B build` | AgentOS 内置（免费版） | 开源社区、评估试用 |
| **2. MemoryRovol Pro** | `cmake -B build -DMEMORYROVOL_ENABLE=ON -DMEMORYROVOL_LIB_PATH=/path/to/pro.a` | MemoryRovol Pro（L1+L2+L3） | 小型商业项目 |
| **3. MemoryRovol Enterprise** | `cmake -B build -DMEMORYROVOL_ENABLE=ON -DMEMORYROVOL_LIB_PATH=/path/to/ent.a` | MemoryRovol Enterprise（L1+L2+L3+L4+遗忘） | 大型企业部署 |

---

## 第7章 — 与之前方案的对比

| 维度 | v11.9 (原始) | v11.11 (闭源全控) | **v11.12 (新方案)** |
|------|-------------|-----------------|-------------------|
| **源码在AgentOS中** | ❌ 部分在AgentOS | ❌ 全部在独立仓库 | **✅ 全部移出AgentOS** |
| **用户不付费能否使用** | ❌ 不能 | ❌ 试用（100条） | **✅ AgentOS内置免费版完整可用** |
| **MemeoryRovol调用方式** | CMake subdirectory | 链接预编译库 | **提供商接口模式（可拔插）** |
| **L3/L4是否在AgentOS源码** | ❌ 否 | ❌ 否 | **✅ 从根本上确保不带入AgentOS** |
| **免费版能力** | 基于license.lic | Trial:100条14天 | **AgentOS内置：文件存储+简单检索** |
| **是否需要license.lic** | 总是需要 | 总是需要 | **免费版不需要，商业版才需要** |
| **对AgentOS代码侵入性** | 高 | 中 | **低（通过接口解耦）** |
| **用户使用门槛** | 高（需license.lic） | 高（需license.lic） | **低（零配置开箱即用）** |

---

## 第8章 — 更新任务清单

### 新增任务

| 编号 | 任务 | 工时 | 说明 |
|------|------|------|------|
| **R-09-01-5** | 🔴 **AgentOS 内置内存子系统实现** | **24h** | 新模块：内置提供商 + 文件存储 + 哈希索引 + 基础检索 |
| **R-09-01-6** | 🔴 **53个依赖文件修改/删除** | **16h** | engine.c重写、orchestrator.c改造、CMake调整、脚本清理 |
| **R-09-01-7** | 🔴 **MemoryRovol 提供商适配器** | **8h** | 在MemoryRovol仓库中实现agentos_provider.c，通过constructor自动注册 |
| **R-09-01-8** | 🟡 **集成测试** | **8h** | 三种模式端到端：纯内置/MemoryRovol Pro/MemoryRovol Enterprise |

### 删除的任务

| 原任务 | 原因 |
|--------|------|
| R-09-01-1 (CMake双模式) | 被取代：改为更简洁的 `MEMORYROVOL_ENABLE`（新增R-09-01-5/6） |
| R-09-01-4 (License签发服务) | 保留但降优先级：集成测试中验证即可 |

---

## 第9章 — 执行路线图

| 阶段 | 时间 | 任务 | 交付物 |
|------|------|------|--------|
| **P1 接口定义** | 第1-2天 | `memory_provider.h` 接口设计 + 评审 | 接口文档 + C头文件 |
| **P2 内置提供商** | 第3-5天 | `builtin_storage.c` + `builtin_index.c` + `builtin_retrieval.c` | 可编译的内置内存模块 |
| **P3 迁移改造** | 第6-8天 | engine.c重写 + orchestrator.c改造 + syscall调整 | 53个文件全部就绪 |
| **P4 清理删除** | 第9天 | 删除 `atoms/memoryrovol/` 整个目录 + 清理测试/脚本/文档 | AgentOS 零 MemoryRovol 源码 |
| **P5 MemoryRovol 适配** | 第10-11天 | `agentos_provider.c` constructor 注册 + License 验证 | MemoryRovol 预编译库 |
| **P6 集成测试** | 第12天 | 3种构建模式端到端验证 | CI 全部绿色 |

---

<div align="center">

**© 2026 SPHARX Ltd. All Rights Reserved.**

*From data intelligence emerges*

</div>
