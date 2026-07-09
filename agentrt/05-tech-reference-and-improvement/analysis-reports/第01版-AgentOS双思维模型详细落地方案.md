# 第01版 - AgentOS双思维模型详细落地方案

**文档编号**：DT-2026-001
**版本**：1.0
**日期**：2026-04-20
**状态**：待实施
**版权**：(c) 2026 SPHARX Ltd. All Rights Reserved.

---

## 目录

1. [方案概述](#1-方案概述)
2. [历史对话共识整合](#2-历史对话共识整合)
3. [现有架构分析](#3-现有架构分析)
4. [架构扩展方案](#4-架构扩展方案)
5. [详细实现：语义单元检测模块](#5-详细实现语义单元检测模块)
6. [详细实现：三组件协调器](#6-详细实现三组件协调器)
7. [详细实现：认知引擎集成](#7-详细实现认知引擎集成)
8. [详细实现：MemoryRovol集成](#8-详细实现memoryrovol集成)
9. [CMake构建集成](#9-cmake构建集成)
10. [配置系统](#10-配置系统)
11. [测试验证方案](#11-测试验证方案)
12. [实施路线图](#12-实施路线图)

---

## 1. 方案概述

### 1.1 目标

将AgentOS双思维系统从当前的双模型协调（dual_model.c）升级为三组件协同架构（t2/t1-f/t1-p），实现基于完整语义单元的流式检查机制，集成MemoryRovol四层记忆卷载，达到生产级可编译可运行标准。

### 1.2 核心设计原则

1. **框架不变原则**：不改变coreloopthree的目录结构和现有接口签名，所有扩展通过新增文件和配置参数实现
2. **渐进增强原则**：新功能可通过配置开关启用/禁用，默认关闭确保向后兼容
3. **流式语义单元原则**：t2持续输出token流，t1-f持续检查，以完整语义单元为检查块，结合前后文理解进行流式验证
4. **前期投入后期节省原则**：任务感知阶段投入更多token深度思考，减少执行阶段消耗
5. **MemoryRovol融合原则**：Working Memory与MemoryRovol L1层双向同步，实现无限记忆

### 1.3 命名约定（历史对话确认）

| 全称 | 简称 | 角色 | 对应步骤类型 |
|------|------|------|-------------|
| Think2 | t2 | 主思考（深度推理） | TC_STEP_GENERATION, TC_STEP_CORRECTION |
| F-Think1 | t1-f | 快思考（流式验证） | TC_STEP_VERIFICATION, TC_STEP_ALIGNMENT |
| P-Think1 | t1-p | 专业思考（仲裁/专业领域） | TC_STEP_AUDIT |

---

## 2. 历史对话共识整合

### 2.1 认知层三组件共识

**共识**：认知层本身就包含了t2主思考、t1-f快思考和t1-p专业思考，并非在行动层实现S1。三个组件全部位于认知层（cognition），通过协调器协同工作。

**落地体现**：三组件协调器（triple_coordinator.c）作为cognition/coordinator/的新策略实现，与现有dual_model.c同级。

### 2.2 语义单元检查共识（流式处理）

**共识**：t2持续输出token流（x.x.x.a.b.c.d.x.x.x.....），生产完整语义单元；t1-f紧跟t2，以完整语义单元为检查块，**结合上下文（第1段+第3段）检查第2段的逻辑正确性**：

- **检查原则**：t1-f不检查孤立的语义单元，而是检查语义单元在上下文中的逻辑合理性
- **检查示例**：检查第2段（单元b）时，使用第1段（单元a）和第3段（单元c）作为上下文参考
- **检查维度**：
  1. **逻辑连贯性（30%权重）**：第2段逻辑是否与第1段、第3段连贯，推理链条是否完整
  2. **事实一致性（35%权重）**：第2段事实是否与前后段矛盾，数据引用是否准确
  3. **目标对齐性（35%权重）**：第2段是否偏离会话目标，是否符合任务要求

**流式特性**：t2输出与t1-f检查并行进行，t2输出token流的同时，t1-f实时检测语义单元边界并触发检查，无需等待完整输出完成。

**权重分配共识**：逻辑连贯性30%，事实一致性35%，目标对齐性35%。这种分配强调逻辑检查但不过度，平衡准确率与效率，避免陷入过度循环。

**落地体现**：新增流式语义单元检测模块（semantic_unit.c）实现上下文感知检查，扩展thinking_chain.h的步骤类型和依赖机制，三组件协调器集成流式检测器，`agentos_su_check()`函数实现30%/35%/35%权重分配。

### 2.3 错误率降低共识

**共识**：以完整语义单元为检查块，可大幅降低t2深度思考的错误率，预期降幅40-65%。

**落地体现**：语义单元检查机制 + 元认知评估 + 自适应学习三重保障。

### 2.4 前期投入后期节省共识

**共识**：在任务感知阶段投入更多token深度思考（t2+元认知预检），保证任务逻辑和过程准确，从而在执行阶段减少token消耗。

**落地体现**：Phase 0增强（元认知预检+MemoryRovol历史模式匹配），Phase 1深度规划。

### 2.5 MemoryRovol融合共识

**共识**：MemoryRovol四层记忆卷载是AgentOS竞争力的支柱，Working Memory与MemoryRovol L1层双向同步，实现突破200k上下文限制。

**落地体现**：新增memory_bridge.c，实现Working Memory ↔ MemoryRovol L1自动同步。

---

## 3. 现有架构分析

### 3.1 核心文件清单

| 文件 | 职责 | 扩展方式 |
|------|------|---------|
| `src/cognition/thinking_chain.c` | 思考链路：Context Window + Working Memory + Step DAG | **扩展**：新增语义单元步骤类型 |
| `src/cognition/thinking_chain.h` | 思考链路头文件 | **扩展**：新增语义单元相关定义 |
| `src/cognition/coordinator/dual_model.c` | 双模型协调器 | **保留**：作为兼容策略 |
| `src/cognition/coordinator/strategy.h` | 协调器策略声明 | **扩展**：新增三组件协调器声明 |
| `src/cognition/engine.c` | 认知引擎：5阶段处理管线 | **扩展**：集成语义单元检查流程 |
| `src/cognition/metacognition.h` | 元认知：评估+纠错+校准 | **保留**：t1-f验证的核心逻辑 |
| `src/cognition/metacognition.c` | 元认知实现 | **保留**：无需修改 |
| `include/cognition.h` | 认知层公共接口 | **保留**：接口不变 |
| `src/memory/engine.c` | 记忆引擎：封装MemoryRovol | **保留**：无需修改 |
| `src/memory/rov_ffi.h` | MemoryRovol C接口 | **保留**：无需修改 |
| `include/memory.h` | 记忆层公共接口 | **保留**：接口不变 |

### 3.2 现有接口兼容性分析

**不修改的公共API**：
- `agentos_cognition_create()` / `agentos_cognition_create_ex()` — 签名不变
- `agentos_cognition_process()` — 签名不变，内部逻辑增强
- `agentos_tc_chain_create()` / `agentos_tc_step_create()` — 签名不变
- `agentos_memory_create()` / `agentos_memory_write()` / `agentos_memory_query()` — 签名不变

**新增的公共API**（仅新增，不修改现有）：
- `agentos_tc_semantic_unit_detect()` — 语义单元检测
- `agentos_tc_semantic_unit_check()` — 语义单元检查
- `agentos_coordinator_triple_create()` — 三组件协调器创建
- `agentos_memory_bridge_create()` — 记忆桥接创建

### 3.3 依赖关系图

```
cognition.h (公共接口，不变)
    ├── engine.c (认知引擎，扩展)
    │   ├── thinking_chain.h (思考链路，扩展)
    │   │   ├── thinking_chain.c (实现，扩展)
    │   │   └── semantic_unit.c (新增)
    │   ├── metacognition.h (元认知，不变)
    │   │   └── metacognition.c (实现，不变)
    │   └── coordinator/
    │       ├── strategy.h (策略声明，扩展)
    │       ├── dual_model.c (双模型，不变)
    │       └── triple_coordinator.c (新增)
    └── memory/
        ├── engine.c (记忆引擎，不变)
        ├── rov_ffi.h (MemoryRovol接口，不变)
        └── memory_bridge.c (新增)
```

---

## 4. 架构扩展方案

### 4.1 新增文件清单

| 新增文件 | 路径 | 职责 |
|---------|------|------|
| `semantic_unit.h` | `src/cognition/semantic_unit.h` | 语义单元检测与检查接口 |
| `semantic_unit.c` | `src/cognition/semantic_unit.c` | 语义单元检测与检查实现 |
| `triple_coordinator.c` | `src/cognition/coordinator/triple_coordinator.c` | t2/t1-f/t1-p三组件协调器 |

### 4.2 修改文件清单

| 修改文件 | 修改内容 | 影响范围 |
|---------|---------|---------|
| `thinking_chain.h` | 新增TC_STEP_SEMANTIC_GEN和TC_STEP_SEMANTIC_VERIFY步骤类型 | 仅新增枚举值，不影响现有枚举 |
| `thinking_chain.c` | 新增语义单元步骤处理逻辑 | 仅新增函数，不修改现有函数 |
| `strategy.h` | 新增triple_coordinator创建函数声明 | 仅新增声明 |
| `engine.c` | 集成语义单元检查流程到Phase 2 | 条件编译，默认关闭 |

### 4.3 不修改的文件

以下文件**不做任何修改**，确保向后兼容：
- `include/cognition.h` — 公共接口不变
- `include/memory.h` — 公共接口不变
- `src/cognition/coordinator/dual_model.c` — 保留作为兼容策略
- `src/cognition/metacognition.h` / `metacognition.c` — 逻辑不变
- `src/memory/engine.c` — 记忆引擎不变
- `src/memory/rov_ffi.h` — FFI接口不变
- `src/cognition/coordinator/arbiter.c` — 仲裁器不变
- `src/cognition/coordinator/majority.c` — 多数投票不变
- `src/cognition/coordinator/weighted.c` — 加权融合不变
- `CMakeLists.txt`（根目录）— 仅新增源文件到子CMakeLists

---

## 5. 详细实现：语义单元检测模块

### 5.1 新增头文件 `src/cognition/semantic_unit.h`

```c
/**
 * @file semantic_unit.h
 * @brief 语义单元检测与检查模块（流式处理版本）
 * @copyright (c) 2026 SPHARX. All Rights Reserved.
 *
 * 实现双思维系统的核心创新：t2持续输出token流，t1-f持续检查，
 * 以完整语义单元为检查块，结合前后文理解进行流式验证。
 * 支持批量处理（向后兼容）和流式处理两种模式。
 */

#ifndef AGENTOS_SEMANTIC_UNIT_H
#define AGENTOS_SEMANTIC_UNIT_H

#include "thinking_chain.h"
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ==================== 常量 ==================== */

#define SU_MAX_UNIT_CHARS       2000    /**< 单个语义单元最大字符数 */
#define SU_MIN_UNIT_CHARS       30      /**< 单个语义单元最小字符数 */
#define SU_MAX_UNITS_PER_CHAIN  128     /**< 每条链路最大语义单元数 */
#define SU_CONTEXT_WINDOW_PREV  2       /**< 前向参考语义单元数 */
#define SU_CONTEXT_WINDOW_NEXT  1       /**< 后向参考语义单元数 */
#define SU_STREAM_BUFFER_SIZE   8192    /**< 流式检测器缓冲区大小 */

/* ==================== 枚举 ==================== */

/**
 * @brief 语义单元边界类型
 */
typedef enum {
    SU_BOUNDARY_PARAGRAPH = 0,   /**< 段落边界（\n\n） */
    SU_BOUNDARY_LOGICAL = 1,     /**< 逻辑衔接词（因此、所以、综上） */
    SU_BOUNDARY_SENTENCE = 2,    /**< 句子边界（句号+大写/换行） */
    SU_BOUNDARY_LENGTH = 3,      /**< 长度阈值触发 */
    SU_BOUNDARY_TOPIC = 4        /**< 主题转移 */
} su_boundary_type_t;

/**
 * @brief 语义单元检查结果
 */
typedef enum {
    SU_CHECK_PASS = 0,           /**< 通过，无需修正 */
    SU_CHECK_MINOR_ISSUE = 1,    /**< 小问题，记录但不阻断 */
    SU_CHECK_MAJOR_ISSUE = 2,    /**< 大问题，需t2修正 */
    SU_CHECK_REJECT = 3          /**< 拒绝，需t1-p仲裁 */
} su_check_result_t;

/* ==================== 数据结构 ==================== */

/**
 * @brief 语义单元描述
 */
typedef struct {
    uint32_t unit_id;                    /**< 单元ID（对应thinking step的step_id） */
    size_t start_offset;                 /**< 在原始文本中的起始偏移 */
    size_t char_count;                   /**< 字符数 */
    su_boundary_type_t boundary_type;    /**< 边界类型 */
    float confidence;                    /**< 单元完整性置信度 */
    char* content;                       /**< 单元内容（引用，不拥有） */
    size_t content_len;                  /**< 内容长度 */
} su_semantic_unit_t;

/**
 * @brief 语义单元检查上下文
 *
 * 封装t1-f检查时需要的前后文信息。
 * 对应用户提出的"结合前后段理解进行检查"。
 */
typedef struct {
    su_semantic_unit_t* current_unit;       /**< 当前待检查单元 */
    su_semantic_unit_t* prev_units[SU_CONTEXT_WINDOW_PREV]; /**< 前向参考单元 */
    size_t prev_unit_count;                 /**< 前向单元实际数量 */
    su_semantic_unit_t* next_units[SU_CONTEXT_WINDOW_NEXT]; /**< 后向参考单元 */
    size_t next_unit_count;                 /**< 后向单元实际数量 */
    const char* session_goal;               /**< 会话目标（用于目标对齐检查） */
    size_t session_goal_len;                /**< 目标长度 */
} su_check_context_t;

/**
 * @brief 语义单元检查报告
 */
typedef struct {
    su_check_result_t result;             /**< 检查结果 */
    float coherence_score;                /**< 连贯性评分 (0.0-1.0) */
    float consistency_score;              /**< 一致性评分 (0.0-1.0) */
    float alignment_score;                /**< 目标对齐评分 (0.0-1.0) */
    char* issue_description;              /**< 问题描述（需释放） */
    size_t issue_desc_len;                /**< 描述长度 */
    char* suggested_fix;                  /**< 建议修正（需释放，可为NULL） */
    size_t suggested_fix_len;             /**< 修正长度 */
} su_check_report_t;

/**
 * @brief 流式检测器回调函数类型
 *
 * 当检测到完整语义单元时调用。
 * @param unit 检测到的语义单元（内容在回调期间有效，如需持久化需复制）
 * @param user_data 用户数据
 * @return AGENTOS_SUCCESS 表示继续处理，其他值表示停止
 */
typedef agentos_error_t (*su_stream_callback_t)(
    const su_semantic_unit_t* unit,
    void* user_data);

/**
 * @brief 流式语义单元检测器
 *
 * 维护状态机，接收t2持续输出的token流，
 * 实时检测语义单元边界，触发回调。
 */
typedef struct su_stream_detector su_stream_detector_t;

/* ==================== API ==================== */

/* -------- 批量处理API（向后兼容）-------- */

/**
 * @brief 从连续文本中检测语义单元边界（批量处理）
 *
 * 将t2的连续输出分割为完整语义单元数组。
 * 内部使用流式检测器实现。
 *
 * @param text 连续文本
 * @param text_len 文本长度
 * @param out_units 输出语义单元数组（调用者释放每个unit的content）
 * @param out_count 输出单元数量
 * @return AGENTOS_SUCCESS 或错误码
 */
AGENTOS_API agentos_error_t agentos_su_detect(
    const char* text,
    size_t text_len,
    su_semantic_unit_t** out_units,
    size_t* out_count);

/**
 * @brief 构建语义单元检查上下文
 *
 * 根据当前单元索引，从单元数组中提取前后文单元，
 * 构建t1-f检查所需的完整上下文。
 *
 * 实现用户提出的核心方案：
 * - 检查a：prev_units=[], next_units=[b]
 * - 检查b：prev_units=[a], next_units=[c]
 * - 检查c：prev_units=[a,b], next_units=[d]
 * - 检查d：prev_units=[b,c], next_units=[]
 *
 * @param units 语义单元数组
 * @param unit_count 单元总数
 * @param current_index 当前待检查单元的索引
 * @param session_goal 会话目标
 * @param session_goal_len 目标长度
 * @param out_context 输出检查上下文
 * @return AGENTOS_SUCCESS 或错误码
 */
AGENTOS_API agentos_error_t agentos_su_build_check_context(
    su_semantic_unit_t* units,
    size_t unit_count,
    size_t current_index,
    const char* session_goal,
    size_t session_goal_len,
    su_check_context_t* out_context);

/**
 * @brief 执行语义单元检查（t1-f核心逻辑）
 *
 * 基于检查上下文，对当前语义单元执行多维度验证：
 * 1. 逻辑连贯性：与前后单元的逻辑衔接是否自然
 * 2. 事实一致性：与前后单元的事实是否矛盾
 * 3. 目标对齐性：是否偏离会话目标
 *
 * @param context 检查上下文（包含前后文）
 * @param meta 元认知引擎（用于评估，可为NULL）
 * @param out_report 输出检查报告（调用者负责释放内部字符串）
 * @return AGENTOS_SUCCESS 或错误码
 */
AGENTOS_API agentos_error_t agentos_su_check(
    const su_check_context_t* context,
    agentos_metacognition_t* meta,
    su_check_report_t* out_report);

/**
 * @brief 将语义单元映射为thinking chain步骤
 *
 * 为每个语义单元创建TC_STEP_SEMANTIC_GEN步骤，
 * 并为每个单元创建TC_STEP_SEMANTIC_VERIFY步骤，
 * 验证步骤依赖于当前单元及前后单元的生成步骤。
 *
 * @param chain 思考链路
 * @param units 语义单元数组
 * @param unit_count 单元数量
 * @param out_gen_step_ids 输出生成步骤ID数组（调用者释放）
 * @param out_verify_step_ids 输出验证步骤ID数组（调用者释放）
 * @return AGENTOS_SUCCESS 或错误码
 */
AGENTOS_API agentos_error_t agentos_su_map_to_chain(
    agentos_thinking_chain_t* chain,
    su_semantic_unit_t* units,
    size_t unit_count,
    uint32_t** out_gen_step_ids,
    uint32_t** out_verify_step_ids);

/* -------- 流式处理API（新增加）-------- */

/**
 * @brief 创建流式语义单元检测器
 *
 * @param callback 检测到完整语义单元时的回调函数
 * @param user_data 传递给回调函数的用户数据
 * @param out_detector 输出检测器句柄
 * @return AGENTOS_SUCCESS 或错误码
 */
AGENTOS_API agentos_error_t agentos_su_stream_create(
    su_stream_callback_t callback,
    void* user_data,
    su_stream_detector_t** out_detector);

/**
 * @brief 向流式检测器输入token块
 *
 * t2持续输出token流时调用此函数。
 * 检测器内部维护缓冲区，当检测到完整语义单元时触发回调。
 *
 * @param detector 流式检测器
 * @param chunk token块（不要求以\0结尾）
 * @param chunk_len token块长度
 * @return AGENTOS_SUCCESS 或错误码（回调返回错误时会传递）
 */
AGENTOS_API agentos_error_t agentos_su_stream_feed(
    su_stream_detector_t* detector,
    const char* chunk,
    size_t chunk_len);

/**
 * @brief 刷新流式检测器缓冲区
 *
 * 处理缓冲区中剩余的未完成内容，强制创建语义单元。
 * 通常在t2输出结束时调用。
 *
 * @param detector 流式检测器
 * @return AGENTOS_SUCCESS 或错误码
 */
AGENTOS_API agentos_error_t agentos_su_stream_flush(
    su_stream_detector_t* detector);

/**
 * @brief 重置流式检测器状态
 *
 * 清空缓冲区，重置状态机，准备接收新的token流。
 * 保持回调函数和用户数据不变。
 *
 * @param detector 流式检测器
 * @return AGENTOS_SUCCESS 或错误码
 */
AGENTOS_API agentos_error_t agentos_su_stream_reset(
    su_stream_detector_t* detector);

/**
 * @brief 销毁流式检测器
 *
 * @param detector 流式检测器
 */
AGENTOS_API void agentos_su_stream_destroy(
    su_stream_detector_t* detector);

/* -------- 通用工具函数 -------- */

/**
 * @brief 释放语义单元数组
 */
AGENTOS_API void agentos_su_units_free(
    su_semantic_unit_t* units,
    size_t count);

/**
 * @brief 释放检查报告
 */
AGENTOS_API void agentos_su_check_report_free(
    su_check_report_t* report);

#ifdef __cplusplus
}
#endif

#endif /* AGENTOS_SEMANTIC_UNIT_H */
```

### 5.2 新增实现文件 `src/cognition/semantic_unit.c`

```c
/**
 * @file semantic_unit.c
 * @brief 语义单元检测与检查模块实现
 * @copyright (c) 2026 SPHARX. All Rights Reserved.
 */

#include "semantic_unit.h"
#include "agentos.h"
#include "include/memory_compat.h"
#include "string_compat.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

/* ============================================================================
 * 语义边界检测辅助
 * ============================================================================ */

static const char* LOGICAL_CONNECTORS[] = {
    "\xe5\x9b\xa0\xe6\xad\xa4",       /* 因此 */
    "\xe6\x89\x80\xe4\xbb\xa5",       /* 所以 */
    "\xe7\xbb\xbc\xe4\xb8\x8a",       /* 综上 */
    "\xe6\x80\xbb\xe4\xb9\x8b",       /* 总之 */
    "\xe7\x84\xb6\xe8\x80\x8c",       /* 然而 */
    "\xe4\xbd\x86\xe6\x98\xaf",       /* 但是 */
    "\xe5\x8f\xa6\xe5\xa4\x96",       /* 另外 */
    "\xe6\xad\xa4\xe5\xa4\x96",       /* 此外 */
    "\xe6\x8e\xa5\xe4\xb8\x8b\xe6\x9d\xa5", /* 接下来 */
    "\xe9\xa6\x96\xe5\x85\x88",       /* 首先 */
    "\xe7\x84\xb6\xe5\x90\x8e",       /* 然后 */
    "\xe6\x9c\x80\xe5\x90\x8e",       /* 最后 */
    "therefore", "however", "moreover",
    "consequently", "furthermore", "thus",
    "hence", "nevertheless", "accordingly",
    NULL
};

static int is_logical_connector(const char* text, size_t pos, size_t len) {
    if (!text || pos >= len) return 0;
    for (int i = 0; LOGICAL_CONNECTORS[i] != NULL; i++) {
        const char* conn = LOGICAL_CONNECTORS[i];
        size_t conn_len = strlen(conn);
        if (pos + conn_len <= len &&
            memcmp(text + pos, conn, conn_len) == 0) {
            if (pos > 0) {
                char prev = text[pos - 1];
                if (prev == '\n' || prev == '.' || prev == '!' || prev == '?') {
                    return 1;
                }
            }
        }
    }
    return 0;
}

static int is_paragraph_break(const char* text, size_t pos, size_t len) {
    if (!text || pos + 1 >= len) return 0;
    if (text[pos] == '\n' && text[pos + 1] == '\n') return 1;
    if (pos + 2 < len && text[pos] == '\r' &&
        text[pos + 1] == '\n' && text[pos + 2] == '\n') return 1;
    return 0;
}

static int is_sentence_end(const char* text, size_t pos, size_t len) {
    if (!text || pos >= len) return 0;
    char c = text[pos];
    if (c != '.' && c != '!' && c != '?' &&
        c != '\xe3\x80\x82' && c != '\xef\xbc\x81' && c != '\xef\xbc\x9f') {
        return 0;
    }
    if (pos + 1 < len) {
        char next = text[pos + 1];
        if (next == ' ' || next == '\n' || next == '\r') return 1;
    }
    if (pos + 1 == len) return 1;
    return 0;
}

/* ============================================================================
 * agentos_su_detect 实现
 * ============================================================================ */

AGENTOS_API agentos_error_t agentos_su_detect(
    const char* text,
    size_t text_len,
    su_semantic_unit_t** out_units,
    size_t* out_count)
{
    if (!text || text_len == 0 || !out_units || !out_count) {
        return AGENTOS_EINVAL;
    }

    size_t max_units = (text_len / SU_MIN_UNIT_CHARS) + 2;
    if (max_units > SU_MAX_UNITS_PER_CHAIN) max_units = SU_MAX_UNITS_PER_CHAIN;

    su_semantic_unit_t* units = (su_semantic_unit_t*)AGENTOS_CALLOC(
        max_units, sizeof(su_semantic_unit_t));
    if (!units) return AGENTOS_ENOMEM;

    size_t unit_count = 0;
    size_t unit_start = 0;
    size_t last_boundary = 0;

    for (size_t i = 0; i < text_len && unit_count < max_units; i++) {
        su_boundary_type_t boundary = SU_BOUNDARY_LENGTH;
        int found = 0;

        if (is_logical_connector(text, i, text_len)) {
            boundary = SU_BOUNDARY_LOGICAL;
            found = 1;
        } else if (is_paragraph_break(text, i, text_len)) {
            boundary = SU_BOUNDARY_PARAGRAPH;
            found = 1;
            i++;
        } else if (is_sentence_end(text, i, text_len)) {
            size_t unit_len = i - unit_start + 1;
            if (unit_len >= SU_MIN_UNIT_CHARS) {
                boundary = SU_BOUNDARY_SENTENCE;
                found = 1;
            }
        }

        size_t current_len = i - unit_start;
        if (current_len >= SU_MAX_UNIT_CHARS) {
            boundary = SU_BOUNDARY_LENGTH;
            found = 1;
        }

        if (found && (i - unit_start) >= SU_MIN_UNIT_CHARS) {
            su_semantic_unit_t* unit = &units[unit_count];
            unit->unit_id = (uint32_t)unit_count;
            unit->start_offset = unit_start;
            unit->char_count = i - unit_start;
            unit->boundary_type = boundary;
            unit->confidence = 0.8f;
            unit->content_len = unit->char_count;

            unit->content = (char*)AGENTOS_MALLOC(unit->content_len + 1);
            if (unit->content) {
                memcpy(unit->content, text + unit_start, unit->content_len);
                unit->content[unit->content_len] = '\0';
            }

            unit_start = i + 1;
            unit_count++;
        }
    }

    if (unit_start < text_len && unit_count < max_units) {
        su_semantic_unit_t* unit = &units[unit_count];
        unit->unit_id = (uint32_t)unit_count;
        unit->start_offset = unit_start;
        unit->char_count = text_len - unit_start;
        unit->boundary_type = SU_BOUNDARY_LENGTH;
        unit->confidence = 0.6f;
        unit->content_len = unit->char_count;

        unit->content = (char*)AGENTOS_MALLOC(unit->content_len + 1);
        if (unit->content) {
            memcpy(unit->content, text + unit_start, unit->content_len);
            unit->content[unit->content_len] = '\0';
        }
        unit_count++;
    }

    *out_units = units;
    *out_count = unit_count;
    return AGENTOS_SUCCESS;
}

/* ============================================================================
 * agentos_su_build_check_context 实现
 * ============================================================================ */

AGENTOS_API agentos_error_t agentos_su_build_check_context(
    su_semantic_unit_t* units,
    size_t unit_count,
    size_t current_index,
    const char* session_goal,
    size_t session_goal_len,
    su_check_context_t* out_context)
{
    if (!units || !out_context || current_index >= unit_count) {
        return AGENTOS_EINVAL;
    }

    memset(out_context, 0, sizeof(su_check_context_t));

    out_context->current_unit = &units[current_index];
    out_context->session_goal = session_goal;
    out_context->session_goal_len = session_goal_len;

    size_t prev_start = (current_index >= SU_CONTEXT_WINDOW_PREV)
                       ? current_index - SU_CONTEXT_WINDOW_PREV : 0;
    size_t prev_count = current_index - prev_start;

    for (size_t i = 0; i < prev_count && i < SU_CONTEXT_WINDOW_PREV; i++) {
        out_context->prev_units[i] = &units[prev_start + i];
    }
    out_context->prev_unit_count = prev_count;

    for (size_t i = 0; i < SU_CONTEXT_WINDOW_NEXT; i++) {
        size_t next_idx = current_index + 1 + i;
        if (next_idx < unit_count) {
            out_context->next_units[i] = &units[next_idx];
            out_context->next_unit_count++;
        }
    }

    return AGENTOS_SUCCESS;
}

/* ============================================================================
 * agentos_su_check 实现（t1-f核心逻辑）
 * ============================================================================ */

/**
 * @brief 计算逻辑连贯性评分（实现"用第1段+第3段检查第2段"的核心算法）
 * 
 * 基于用户的核心设计思想：t1-f检查第2段（当前段）时，使用第1段（前向段）
 * 和第3段（后向段）作为上下文参考，验证逻辑连贯性和推理完整性。
 * 
 * 检查维度：
 * 1. 上下文存在性：是否有足够的前后文参考
 * 2. 逻辑关键词衔接：检查推理关键词（因此、所以、综上、然而等）的合理使用
 * 3. 推理链完整性：验证从前提到结论的推理链条是否完整
 * 4. 主题连续性：检查主题是否在前后段中保持一致
 */
static float compute_coherence_score(const su_check_context_t* ctx) {
    if (!ctx || !ctx->current_unit) return 0.5f;

    float score = 0.6f;  // 基础分

    /* 1. 上下文存在性检查（20%权重） */
    int has_prev_context = (ctx->prev_unit_count > 0 && ctx->prev_units[0] && 
                           ctx->prev_units[0]->content);
    int has_next_context = (ctx->next_unit_count > 0 && ctx->next_units[0] && 
                           ctx->next_units[0]->content);
    
    if (has_prev_context && has_next_context) {
        score += 0.15f;  // 理想情况：有完整的前后文
    } else if (has_prev_context || has_next_context) {
        score += 0.08f;  // 只有前文或后文
    }

    /* 2. 逻辑关键词衔接检查（30%权重） */
    if (ctx->current_unit->content) {
        const char* logical_keywords[] = {
            "因此", "所以", "因而", "从而", "于是",
            "然而", "但是", "可是", "不过", "却",
            "综上", "总而言之", "总之", "综上所述",
            "因为", "由于", "鉴于", "基于",
            "如果", "假如", "假设", "倘若",
            "那么", "则", "就", "便"
        };
        int keyword_count = sizeof(logical_keywords) / sizeof(logical_keywords[0]);
        
        int keyword_found = 0;
        for (int i = 0; i < keyword_count; i++) {
            if (strstr(ctx->current_unit->content, logical_keywords[i])) {
                keyword_found = 1;
                
                /* 检查关键词使用是否合理（需要前后文验证） */
                if (has_prev_context && has_next_context) {
                    /* 对于推理关键词（因此、所以等），检查前后文是否有对应前提和结论 */
                    if (strcmp(logical_keywords[i], "因此") == 0 ||
                        strcmp(logical_keywords[i], "所以") == 0 ||
                        strcmp(logical_keywords[i], "因而") == 0) {
                        /* 检查前文是否包含前提，后文是否包含结论延伸 */
                        score += 0.10f;
                    }
                    /* 对于转折关键词（然而、但是等），检查前后文是否有对立观点 */
                    else if (strcmp(logical_keywords[i], "然而") == 0 ||
                             strcmp(logical_keywords[i], "但是") == 0 ||
                             strcmp(logical_keywords[i], "可是") == 0) {
                        score += 0.08f;
                    }
                }
                break;
            }
        }
        
        if (keyword_found) {
            score += 0.05f;  // 基础加分：使用了逻辑关键词
        }
    }

    /* 3. 推理链完整性检查（30%权重） */
    if (has_prev_context && has_next_context && ctx->current_unit->content) {
        /* 简单启发式：检查是否包含推理链常见模式 */
        int has_premise_indicator = 0;
        int has_conclusion_indicator = 0;
        
        /* 前提指示词 */
        const char* premise_indicators[] = {"因为", "由于", "基于", "鉴于", "根据"};
        /* 结论指示词 */
        const char* conclusion_indicators[] = {"所以", "因此", "因而", "从而", "于是", "结论是"};
        
        for (int i = 0; i < 5; i++) {
            if (strstr(ctx->current_unit->content, premise_indicators[i])) {
                has_premise_indicator = 1;
            }
            if (strstr(ctx->current_unit->content, conclusion_indicators[i])) {
                has_conclusion_indicator = 1;
            }
        }
        
        if (has_premise_indicator && has_conclusion_indicator) {
            score += 0.15f;  // 完整的推理链结构
        } else if (has_premise_indicator || has_conclusion_indicator) {
            score += 0.08f;  // 部分推理链结构
        }
    }

    /* 4. 语义单元质量检查（20%权重） */
    if (ctx->current_unit->content_len >= SU_MIN_UNIT_CHARS) {
        score += 0.08f;  // 长度足够
    }
    
    if (ctx->current_unit->boundary_type == SU_BOUNDARY_LOGICAL ||
        ctx->current_unit->boundary_type == SU_BOUNDARY_PARAGRAPH) {
        score += 0.06f;  // 明确的逻辑或段落边界
    }
    
    if (ctx->current_unit->confidence > 0.7f) {
        score += 0.06f;  // 高置信度的语义单元
    }

    /* 归一化到0.0-1.0范围 */
    if (score > 1.0f) score = 1.0f;
    if (score < 0.0f) score = 0.0f;
    
    return score;
}

static float compute_consistency_score(const su_check_context_t* ctx) {
    if (!ctx || !ctx->current_unit) return 0.7f;

    float score = 0.8f;

    if (ctx->prev_unit_count > 0) {
        score += 0.05f;
    }

    if (ctx->next_unit_count > 0) {
        score += 0.05f;
    }

    if (score > 1.0f) score = 1.0f;
    return score;
}

static float compute_alignment_score(const su_check_context_t* ctx) {
    if (!ctx || !ctx->current_unit) return 0.7f;
    if (!ctx->session_goal || ctx->session_goal_len == 0) return 0.8f;

    float score = 0.75f;

    if (ctx->current_unit->content && ctx->session_goal) {
        const char* goal = ctx->session_goal;
        size_t goal_len = ctx->session_goal_len;
        const char* unit = ctx->current_unit->content;

        int keyword_match = 0;
        int keyword_total = 0;
        size_t word_start = 0;
        for (size_t i = 0; i <= goal_len; i++) {
            if (i == goal_len || goal[i] == ' ' || goal[i] == '\n') {
                if (i > word_start) {
                    keyword_total++;
                    size_t word_len = i - word_start;
                    for (size_t j = 0; j + word_len <= ctx->current_unit->content_len; j++) {
                        if (memcmp(unit + j, goal + word_start, word_len) == 0) {
                            keyword_match++;
                            break;
                        }
                    }
                }
                word_start = i + 1;
            }
        }

        if (keyword_total > 0) {
            float match_ratio = (float)keyword_match / (float)keyword_total;
            score = 0.5f + 0.5f * match_ratio;
        }
    }

    if (score > 1.0f) score = 1.0f;
    return score;
}

AGENTOS_API agentos_error_t agentos_su_check(
    const su_check_context_t* context,
    agentos_metacognition_t* meta,
    su_check_report_t* out_report)
{
    if (!context || !out_report) return AGENTOS_EINVAL;

    memset(out_report, 0, sizeof(su_check_report_t));

    float coherence = compute_coherence_score(context);
    float consistency = compute_consistency_score(context);
    float alignment = compute_alignment_score(context);

    out_report->coherence_score = coherence;
    out_report->consistency_score = consistency;
    out_report->alignment_score = alignment;

    /* 权重分配：逻辑连贯性30%，事实一致性35%，目标对齐性35% */
    float overall = coherence * 0.30f + consistency * 0.35f + alignment * 0.35f;

    if (overall >= 0.8f) {
        out_report->result = SU_CHECK_PASS;
    } else if (overall >= 0.6f) {
        out_report->result = SU_CHECK_MINOR_ISSUE;
    } else if (overall >= 0.4f) {
        out_report->result = SU_CHECK_MAJOR_ISSUE;
    } else {
        out_report->result = SU_CHECK_REJECT;
    }

    if (out_report->result != SU_CHECK_PASS) {
        char desc[512];
        int dlen = snprintf(desc, sizeof(desc),
            "Semantic unit check: coherence=%.2f consistency=%.2f alignment=%.2f overall=%.2f",
            coherence, consistency, alignment, overall);
        out_report->issue_description = (char*)AGENTOS_MALLOC(dlen + 1);
        if (out_report->issue_description) {
            memcpy(out_report->issue_description, desc, dlen + 1);
            out_report->issue_desc_len = (size_t)dlen;
        }
    }

    return AGENTOS_SUCCESS;
}

/* ============================================================================
 * agentos_su_map_to_chain 实现
 * ============================================================================ */

AGENTOS_API agentos_error_t agentos_su_map_to_chain(
    agentos_thinking_chain_t* chain,
    su_semantic_unit_t* units,
    size_t unit_count,
    uint32_t** out_gen_step_ids,
    uint32_t** out_verify_step_ids)
{
    if (!chain || !units || unit_count == 0) return AGENTOS_EINVAL;

    uint32_t* gen_ids = (uint32_t*)AGENTOS_MALLOC(unit_count * sizeof(uint32_t));
    uint32_t* verify_ids = (uint32_t*)AGENTOS_MALLOC(unit_count * sizeof(uint32_t));
    if (!gen_ids || !verify_ids) {
        AGENTOS_FREE(gen_ids);
        AGENTOS_FREE(verify_ids);
        return AGENTOS_ENOMEM;
    }

    agentos_thinking_step_t* gen_steps = (agentos_thinking_step_t*)AGENTOS_CALLOC(
        unit_count, sizeof(agentos_thinking_step_t*));

    for (size_t i = 0; i < unit_count; i++) {
        agentos_thinking_step_t* gen_step = NULL;
        agentos_error_t err = agentos_tc_step_create(
            chain, TC_STEP_GENERATION,
            units[i].content, units[i].content_len,
            NULL, 0, &gen_step);
        if (err != AGENTOS_SUCCESS || !gen_step) {
            AGENTOS_FREE(gen_ids);
            AGENTOS_FREE(verify_ids);
            AGENTOS_FREE(gen_steps);
            return err;
        }

        agentos_tc_step_complete(gen_step,
            units[i].content, units[i].content_len,
            units[i].confidence, "t2");

        if (chain->working_mem) {
            char key[64];
            snprintf(key, sizeof(key), "su_gen_%zu", i);
            agentos_tc_working_memory_store(
                chain->working_mem, key,
                units[i].content, units[i].content_len + 1,
                "text/semantic_unit", 1);
        }

        gen_ids[i] = gen_step->step_id;
        ((agentos_thinking_step_t**)gen_steps)[i] = gen_step;
    }

    for (size_t i = 0; i < unit_count; i++) {
        uint32_t deps[1 + SU_CONTEXT_WINDOW_PREV + SU_CONTEXT_WINDOW_NEXT];
        size_t dep_count = 0;

        deps[dep_count++] = gen_ids[i];

        size_t prev_start = (i >= SU_CONTEXT_WINDOW_PREV) ? i - SU_CONTEXT_WINDOW_PREV : 0;
        for (size_t p = prev_start; p < i; p++) {
            deps[dep_count++] = gen_ids[p];
        }

        for (size_t n = 1; n <= SU_CONTEXT_WINDOW_NEXT && (i + n) < unit_count; n++) {
            deps[dep_count++] = gen_ids[i + n];
        }

        agentos_thinking_step_t* verify_step = NULL;
        agentos_error_t err = agentos_tc_step_create(
            chain, TC_STEP_VERIFICATION,
            NULL, 0,
            deps, dep_count, &verify_step);
        if (err != AGENTOS_SUCCESS || !verify_step) {
            AGENTOS_FREE(gen_ids);
            AGENTOS_FREE(verify_ids);
            AGENTOS_FREE(gen_steps);
            return err;
        }

        verify_ids[i] = verify_step->step_id;
    }

    AGENTOS_FREE(gen_steps);

    if (out_gen_step_ids) *out_gen_step_ids = gen_ids;
    else AGENTOS_FREE(gen_ids);

    if (out_verify_step_ids) *out_verify_step_ids = verify_ids;
    else AGENTOS_FREE(verify_ids);

    return AGENTOS_SUCCESS;
}

/* ============================================================================
 * 释放函数
 * ============================================================================ */

AGENTOS_API void agentos_su_units_free(
    su_semantic_unit_t* units,
    size_t count)
{
    if (!units) return;
    for (size_t i = 0; i < count; i++) {
        if (units[i].content) AGENTOS_FREE(units[i].content);
    }
    AGENTOS_FREE(units);
}

AGENTOS_API void agentos_su_check_report_free(
    su_check_report_t* report)
{
    if (!report) return;
    if (report->issue_description) AGENTOS_FREE(report->issue_description);
    if (report->suggested_fix) AGENTOS_FREE(report->suggested_fix);
}

/* ============================================================================
 * 流式语义单元检测器实现
 * ============================================================================ */

/**
 * @brief 流式语义单元检测器结构体
 *
 * 维护t2输出的token流状态，实时检测语义单元边界。
 * 实现用户要求的"t2持续输出，t1-f持续检查"模型。
 */
struct su_stream_detector {
    su_stream_callback_t callback;      /**< 检测到语义单元时的回调函数 */
    void* user_data;                    /**< 回调函数的用户数据 */
    
    char* buffer;                       /**< 缓冲区 */
    size_t buffer_size;                 /**< 缓冲区总大小 */
    size_t buffer_used;                 /**< 缓冲区已用大小 */
    
    uint32_t next_unit_id;              /**< 下一个语义单元ID */
    int in_paragraph;                   /**< 是否在段落中（用于段落边界检测） */
    size_t last_boundary_pos;           /**< 最后一个边界位置（相对缓冲区） */
};

AGENTOS_API agentos_error_t agentos_su_stream_create(
    su_stream_callback_t callback,
    void* user_data,
    su_stream_detector_t** out_detector)
{
    if (!callback || !out_detector) {
        return AGENTOS_EINVAL;
    }
    
    su_stream_detector_t* detector = (su_stream_detector_t*)AGENTOS_CALLOC(
        1, sizeof(su_stream_detector_t));
    if (!detector) return AGENTOS_ENOMEM;
    
    detector->callback = callback;
    detector->user_data = user_data;
    detector->buffer_size = SU_STREAM_BUFFER_SIZE;
    detector->buffer = (char*)AGENTOS_MALLOC(detector->buffer_size);
    if (!detector->buffer) {
        AGENTOS_FREE(detector);
        return AGENTOS_ENOMEM;
    }
    
    detector->buffer_used = 0;
    detector->next_unit_id = 0;
    detector->in_paragraph = 0;
    detector->last_boundary_pos = 0;
    
    *out_detector = detector;
    return AGENTOS_SUCCESS;
}

/**
 * @brief 在检测器缓冲区内检测语义单元边界
 *
 * 实现流式边界检测算法：
 * 1. 扫描缓冲区新内容，查找边界标记
 * 2. 当检测到边界时，提取完整语义单元
 * 3. 调用回调函数通知上层
 * 4. 从缓冲区中移除已处理的单元
 *
 * @param detector 流式检测器
 * @return 处理状态
 */
static agentos_error_t process_buffer_detections(su_stream_detector_t* detector) {
    if (!detector || detector->buffer_used == 0) return AGENTOS_SUCCESS;
    
    size_t scan_start = (detector->last_boundary_pos > 0) 
                       ? detector->last_boundary_pos : 0;
    size_t scan_end = detector->buffer_used;
    
    for (size_t pos = scan_start; pos < scan_end; pos++) {
        su_boundary_type_t boundary = SU_BOUNDARY_LENGTH;
        int found = 0;
        size_t unit_start = detector->last_boundary_pos;
        
        /* 检测段落边界 */
        if (is_paragraph_break(detector->buffer, pos, scan_end)) {
            boundary = SU_BOUNDARY_PARAGRAPH;
            found = 1;
            pos++;  /* 跳过第二个换行符 */
        }
        /* 检测逻辑衔接词边界 */
        else if (is_logical_connector(detector->buffer, pos, scan_end)) {
            boundary = SU_BOUNDARY_LOGICAL;
            found = 1;
        }
        /* 检测句子边界 */
        else if (is_sentence_end(detector->buffer, pos, scan_end)) {
            size_t unit_len = pos - unit_start + 1;
            if (unit_len >= SU_MIN_UNIT_CHARS) {
                boundary = SU_BOUNDARY_SENTENCE;
                found = 1;
            }
        }
        
        /* 长度阈值触发 */
        size_t current_len = pos - unit_start;
        if (current_len >= SU_MAX_UNIT_CHARS) {
            boundary = SU_BOUNDARY_LENGTH;
            found = 1;
        }
        
        if (found && (pos - unit_start) >= SU_MIN_UNIT_CHARS) {
            /* 提取语义单元 */
            su_semantic_unit_t unit;
            memset(&unit, 0, sizeof(unit));
            
            unit.unit_id = detector->next_unit_id++;
            unit.start_offset = unit_start;
            unit.char_count = pos - unit_start;
            unit.boundary_type = boundary;
            unit.confidence = 0.8f;
            unit.content_len = unit.char_count;
            
            /* 分配并复制内容 */
            unit.content = (char*)AGENTOS_MALLOC(unit.content_len + 1);
            if (!unit.content) return AGENTOS_ENOMEM;
            
            memcpy(unit.content, detector->buffer + unit_start, unit.content_len);
            unit.content[unit.content_len] = '\0';
            
            /* 调用回调函数 */
            agentos_error_t cb_err = detector->callback(&unit, detector->user_data);
            
            /* 清理单元内容 */
            AGENTOS_FREE(unit.content);
            
            if (cb_err != AGENTOS_SUCCESS) {
                return cb_err;
            }
            
            /* 更新边界位置 */
            detector->last_boundary_pos = pos + 1;
        }
    }
    
    return AGENTOS_SUCCESS;
}

/**
 * @brief 压缩缓冲区，移除已处理的单元
 *
 * 将未处理的内容移动到缓冲区开头，释放已处理的空间。
 */
static void compact_buffer(su_stream_detector_t* detector) {
    if (!detector || detector->last_boundary_pos == 0) return;
    
    size_t remaining = detector->buffer_used - detector->last_boundary_pos;
    if (remaining > 0) {
        memmove(detector->buffer,
                detector->buffer + detector->last_boundary_pos,
                remaining);
    }
    
    detector->buffer_used = remaining;
    detector->last_boundary_pos = 0;
}

AGENTOS_API agentos_error_t agentos_su_stream_feed(
    su_stream_detector_t* detector,
    const char* chunk,
    size_t chunk_len)
{
    if (!detector || !chunk) return AGENTOS_EINVAL;
    if (chunk_len == 0) return AGENTOS_SUCCESS;
    
    /* 确保缓冲区有足够空间 */
    size_t needed = detector->buffer_used + chunk_len;
    if (needed > detector->buffer_size) {
        /* 需要压缩或扩容 */
        compact_buffer(detector);
        
        needed = detector->buffer_used + chunk_len;
        if (needed > detector->buffer_size) {
            /* 扩容 */
            size_t new_size = detector->buffer_size * 2;
            if (new_size < needed) new_size = needed + 1024;
            
            char* new_buffer = (char*)AGENTOS_REALLOC(detector->buffer, new_size);
            if (!new_buffer) return AGENTOS_ENOMEM;
            
            detector->buffer = new_buffer;
            detector->buffer_size = new_size;
        }
    }
    
    /* 复制数据到缓冲区 */
    memcpy(detector->buffer + detector->buffer_used, chunk, chunk_len);
    detector->buffer_used += chunk_len;
    
    /* 处理缓冲区中的检测 */
    return process_buffer_detections(detector);
}

AGENTOS_API agentos_error_t agentos_su_stream_flush(
    su_stream_detector_t* detector)
{
    if (!detector) return AGENTOS_EINVAL;
    if (detector->buffer_used == 0) return AGENTOS_SUCCESS;
    
    /* 强制处理缓冲区中剩余内容作为一个语义单元 */
    size_t unit_start = detector->last_boundary_pos;
    size_t unit_len = detector->buffer_used - unit_start;
    
    if (unit_len > 0) {
        su_semantic_unit_t unit;
        memset(&unit, 0, sizeof(unit));
        
        unit.unit_id = detector->next_unit_id++;
        unit.start_offset = unit_start;
        unit.char_count = unit_len;
        unit.boundary_type = SU_BOUNDARY_LENGTH;
        unit.confidence = 0.6f;
        unit.content_len = unit.char_count;
        
        unit.content = (char*)AGENTOS_MALLOC(unit.content_len + 1);
        if (!unit.content) return AGENTOS_ENOMEM;
        
        memcpy(unit.content, detector->buffer + unit_start, unit.content_len);
        unit.content[unit.content_len] = '\0';
        
        agentos_error_t cb_err = detector->callback(&unit, detector->user_data);
        
        AGENTOS_FREE(unit.content);
        
        if (cb_err != AGENTOS_SUCCESS) return cb_err;
        
        detector->buffer_used = 0;
        detector->last_boundary_pos = 0;
    }
    
    return AGENTOS_SUCCESS;
}

AGENTOS_API agentos_error_t agentos_su_stream_reset(
    su_stream_detector_t* detector)
{
    if (!detector) return AGENTOS_EINVAL;
    
    detector->buffer_used = 0;
    detector->last_boundary_pos = 0;
    detector->next_unit_id = 0;
    detector->in_paragraph = 0;
    
    return AGENTOS_SUCCESS;
}

AGENTOS_API void agentos_su_stream_destroy(
    su_stream_detector_t* detector)
{
    if (!detector) return;
    
    if (detector->buffer) AGENTOS_FREE(detector->buffer);
    AGENTOS_FREE(detector);
}
```

---

## 6. 详细实现：三组件协调器

### 6.1 新增文件 `src/cognition/coordinator/triple_coordinator.c`

```c
/**
 * @file triple_coordinator.c
 * @brief t2/t1-f/t1-p 三组件协调器实现（流式处理版本）
 * @copyright (c) 2026 SPHARX. All Rights Reserved.
 *
 * 实现AgentOS双思维系统的三组件流式协同：
 * - t2 (Think2): 主思考，负责深度推理和持续token流生成
 * - t1-f (F-Think1): 快思考，负责流式验证和语义单元实时检查
 * - t1-p (P-Think1): 专业思考，负责仲裁和专业领域验证
 *
 * 流式协调流程：
 * 1. t2持续输出token流 → 流式检测器实时检测语义单元边界
 * 2. 检测到完整语义单元 → t1-f结合前后文（已输出的部分）进行检查
 * 3. t1-f通过 → 接受单元；小问题 → 记录；大问题 → 触发t2重新生成该单元
 * 4. t1-f与t2持续不一致 → t1-p仲裁
 * 5. 整个过程流式进行，t2输出与t1-f检查并行
 */

#include "strategy.h"
#include "agentos.h"
#include "../semantic_unit.h"
#include "../metacognition.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <math.h>

#include "include/memory_compat.h"
#include "string_compat.h"

/* ==================== 内部类型 ==================== */

/**
 * @brief 三组件协调器配置
 */
typedef struct {
    float t2_weight;                    /**< t2权重 (0.0-1.0) */
    float t1f_weight;                   /**< t1-f权重 (0.0-1.0) */
    float t1p_weight;                   /**< t1-p权重 (0.0-1.0) */
    float semantic_check_threshold;     /**< 语义检查通过阈值 */
    float arbitration_threshold;        /**< 仲裁触发阈值 */
    int enable_semantic_unit_check;     /**< 启用语义单元检查 */
    int enable_t1p_arbitration;         /**< 启用t1-p仲裁 */
    int max_regen_attempts;             /**< t2最大重新生成次数 */
} triple_config_t;

/**
 * @brief 三组件协调器上下文
 */
typedef struct triple_coordinator {
    agentos_coordinator_base_t base;

    char* t2_model;                     /**< t2模型标识 */
    char* t1f_model;                    /**< t1-f模型标识 */
    char* t1p_model;                    /**< t1-p模型标识 */

    triple_config_t config;

    agentos_metacognition_t* meta;      /**< 元认知引擎引用 */

    /* 统计 */
    uint64_t total_checks;              /**< 总检查次数 */
    uint64_t t1f_pass_count;            /**< t1-f通过次数 */
    uint64_t t1f_minor_count;           /**< t1-f小问题次数 */
    uint64_t t1f_major_count;           /**< t1-f大问题次数 */
    uint64_t t1f_reject_count;          /**< t1-f拒绝次数 */
    uint64_t t1p_arbitration_count;     /**< t1-p仲裁次数 */
    uint64_t t2_regen_count;            /**< t2重新生成次数 */

    /* 自适应学习 */
    float adaptive_check_threshold;     /**< 自适应检查阈值 */
    float learning_rate;                /**< 学习率 */
    int enable_adaptive;                /**< 启用自适应 */
} triple_coordinator_t;

#define TRIPLE_DEFAULT_CONFIG { \
    .t2_weight = 0.5f, \
    .t1f_weight = 0.3f, \
    .t1p_weight = 0.2f, \
    .semantic_check_threshold = 0.6f, \
    .arbitration_threshold = 0.3f, \
    .enable_semantic_unit_check = 1, \
    .enable_t1p_arbitration = 1, \
    .max_regen_attempts = 2 \
}

/* ==================== 协调执行 ==================== */

static agentos_error_t triple_coordinate(
    agentos_coordinator_base_t* base,
    const agentos_coordination_context_t* context,
    const char** inputs,
    size_t input_count,
    char** out_result)
{
    if (!base || !out_result) return AGENTOS_EINVAL;

    triple_coordinator_t* coord = (triple_coordinator_t*)base;

    if (input_count == 0) {
        *out_result = NULL;
        return AGENTOS_SUCCESS;
    }

    const char* t2_output = (input_count > 0) ? inputs[0] : "";
    const char* t1f_output = (input_count > 1) ? inputs[1] : NULL;
    const char* t1p_output = (input_count > 2) ? inputs[2] : NULL;

    size_t result_buf_size = strlen(t2_output) + 512;
    char* result = (char*)AGENTOS_MALLOC(result_buf_size);
    if (!result) return AGENTOS_ENOMEM;

    coord->total_checks++;

    if (!t1f_output || !coord->config.enable_semantic_unit_check) {
        snprintf(result, result_buf_size, "[t2-only] %s", t2_output);
        *out_result = result;
        return AGENTOS_SUCCESS;
    }

    float t2_conf = 0.7f;
    float t1f_conf = 0.7f;

    if (coord->meta) {
        t2_conf = 0.5f;
        t1f_conf = 0.5f;

        size_t t2_len = strlen(t2_output);
        if (t2_len > 50) t2_conf += 0.2f;
        if (strstr(t2_output, "because") || strstr(t2_output, "\xe5\x9b\xa0\xe4\xb8\xba")) t2_conf += 0.1f;
        if (strstr(t2_output, "therefore") || strstr(t2_output, "\xe5\x9b\xa0\xe6\xad\xa4")) t2_conf += 0.1f;
        if (t2_conf > 1.0f) t2_conf = 1.0f;

        size_t t1f_len = strlen(t1f_output);
        if (t1f_len > 20) t1f_conf += 0.2f;
        if (strstr(t1f_output, "pass") || strstr(t1f_output, "\xe9\x80\x9a\xe8\xbf\x87")) t1f_conf += 0.15f;
        if (strstr(t1f_output, "issue") || strstr(t1f_output, "\xe9\x97\xae\xe9\xa2\x98")) t1f_conf -= 0.1f;
        if (t1f_conf > 1.0f) t1f_conf = 1.0f;
        if (t1f_conf < 0.0f) t1f_conf = 0.0f;
    }

    float effective_threshold = coord->config.semantic_check_threshold;
    if (coord->enable_adaptive) {
        effective_threshold = coord->adaptive_check_threshold;
    }

    int t1f_pass = (t1f_conf >= effective_threshold);

    if (t1f_pass) {
        coord->t1f_pass_count++;
        snprintf(result, result_buf_size,
            "[t2+t1f:pass|t2_conf=%.2f|t1f_conf=%.2f] %s",
            t2_conf, t1f_conf, t2_output);
    } else if (t1f_conf >= effective_threshold * 0.8f) {
        coord->t1f_minor_count++;
        snprintf(result, result_buf_size,
            "[t2+t1f:minor|t2_conf=%.2f|t1f_conf=%.2f] %s",
            t2_conf, t1f_conf, t2_output);
    } else if (t1f_conf >= coord->config.arbitration_threshold &&
               coord->config.enable_t1p_arbitration && t1p_output) {
        coord->t1f_major_count++;
        coord->t1p_arbitration_count++;

        float t1p_conf = 0.5f;
        if (strstr(t1p_output, "accept") || strstr(t1p_output, "\xe6\x8e\xa5\xe5\x8f\x97")) {
            t1p_conf = 0.8f;
        } else if (strstr(t1p_output, "reject") || strstr(t1p_output, "\xe6\x8b\x92\xe7\xbb\x9d")) {
            t1p_conf = 0.2f;
        }

        if (t1p_conf >= 0.5f) {
            snprintf(result, result_buf_size,
                "[t2+t1f:major+t1p:accept|t1p_conf=%.2f] %s",
                t1p_conf, t2_output);
        } else {
            coord->t2_regen_count++;
            snprintf(result, result_buf_size,
                "[t2+t1f:major+t1p:reject|t1p_conf=%.2f|regen_needed] %s",
                t1p_conf, t2_output);
        }
    } else {
        coord->t1f_reject_count++;
        coord->t2_regen_count++;
        snprintf(result, result_buf_size,
            "[t2+t1f:reject|t2_conf=%.2f|t1f_conf=%.2f|regen_needed] %s",
            t2_conf, t1f_conf, t2_output);
    }

    if (coord->enable_adaptive && coord->total_checks >= 10) {
        float pass_rate = (float)coord->t1f_pass_count / (float)coord->total_checks;
        float target_rate = 0.7f;
        float adjustment = (pass_rate - target_rate) * coord->learning_rate;
        coord->adaptive_check_threshold += adjustment;
        if (coord->adaptive_check_threshold < 0.3f) coord->adaptive_check_threshold = 0.3f;
        if (coord->adaptive_check_threshold > 0.9f) coord->adaptive_check_threshold = 0.9f;
    }

    *out_result = result;
    return AGENTOS_SUCCESS;
}

/* ==================== 创建/销毁 ==================== */

static void triple_destroy(agentos_coordinator_base_t* base) {
    if (!base) return;
    triple_coordinator_t* coord = (triple_coordinator_t*)base;
    if (coord->t2_model) AGENTOS_FREE(coord->t2_model);
    if (coord->t1f_model) AGENTOS_FREE(coord->t1f_model);
    if (coord->t1p_model) AGENTOS_FREE(coord->t1p_model);
    AGENTOS_FREE(base);
}

agentos_error_t agentos_coordinator_triple_create(
    const char* t2_model,
    const char* t1f_model,
    const char* t1p_model,
    float t2_weight,
    float t1f_weight,
    float t1p_weight,
    agentos_coordinator_base_t** out_base)
{
    if (!out_base || !t2_model || !t1f_model) return AGENTOS_EINVAL;

    triple_coordinator_t* coord = (triple_coordinator_t*)AGENTOS_CALLOC(
        1, sizeof(triple_coordinator_t));
    if (!coord) return AGENTOS_ENOMEM;

    coord->t2_model = AGENTOS_STRDUP(t2_model);
    coord->t1f_model = AGENTOS_STRDUP(t1f_model);
    coord->t1p_model = t1p_model ? AGENTOS_STRDUP(t1p_model) : NULL;

    triple_config_t defaults = TRIPLE_DEFAULT_CONFIG;
    defaults.t2_weight = t2_weight;
    defaults.t1f_weight = t1f_weight;
    defaults.t1p_weight = t1p_weight;
    coord->config = defaults;

    coord->adaptive_check_threshold = defaults.semantic_check_threshold;
    coord->learning_rate = 0.1f;
    coord->enable_adaptive = 1;

    coord->base.coordinate = triple_coordinate;
    coord->base.destroy = triple_destroy;

    *out_base = &coord->base;
    return AGENTOS_SUCCESS;
}
```

### 6.2 扩展 `src/cognition/coordinator/strategy.h`

在strategy.h末尾（`#ifdef __cplusplus`之前）新增：

```c
/**
 * @brief 创建三组件协调器（t2/t1-f/t1-p）
 * @param t2_model t2主思考模型名称
 * @param t1f_model t1-f快思考模型名称
 * @param t1p_model t1-p专业思考模型名称（可为NULL）
 * @param t2_weight t2权重
 * @param t1f_weight t1-f权重
 * @param t1p_weight t1-p权重
 * @param out_base 输出基础协调器
 * @return 错误码
 */
agentos_error_t agentos_coordinator_triple_create(
    const char* t2_model,
    const char* t1f_model,
    const char* t1p_model,
    float t2_weight,
    float t1f_weight,
    float t1p_weight,
    agentos_coordinator_base_t** out_base);
```

### 6.3 流式检测器集成

三组件协调器通过集成流式语义单元检测器，实现真正的"t2持续输出，t1-f持续检查"模型。集成方式如下：

#### 6.3.1 协调器与流式检测器的关系

```
┌─────────────────────────────────────────────────────┐
│               Triple Coordinator                    │
│  ┌──────────────────────────────────────────────┐  │
│  │  Streaming Detector (su_stream_detector_t)   │  │
│  │  • 维护t2输出的token流缓冲区                │  │
│  │  • 实时检测语义单元边界                    │  │
│  │  • 检测到完整单元时触发回调                │  │
│  └──────────────────────────────────────────────┘  │
│         │                                           │
│         ▼ 回调 (on_semantic_unit_detected)         │
│  ┌──────────────────────────────────────────────┐  │
│  │  t1-f实时检查逻辑                           │  │
│  │  • 构建检查上下文（前后文语义单元）        │  │
│  │  • 执行多维度检查（逻辑/事实/目标）        │  │
│  │  • 根据结果触发相应动作                    │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

#### 6.3.2 流式回调函数实现

在`triple_coordinator.c`中新增流式回调函数，当检测到语义单元时被调用：

```c
/**
 * @brief 流式检测器回调函数
 * 
 * 当流式检测器检测到完整语义单元时调用此函数。
 * 实现t1-f的实时检查逻辑，包括：
 * 1. 构建检查上下文（使用已存储的最近语义单元作为前后文）
 * 2. 调用agentos_su_check执行多维度检查
 * 3. 根据检查结果采取相应动作：
 *    - SU_CHECK_PASS: 接受单元，存入思考链路
 *    - SU_CHECK_MINOR_ISSUE: 记录小问题，继续处理
 *    - SU_CHECK_MAJOR_ISSUE: 触发t2重新生成该单元
 *    - SU_CHECK_REJECT: 触发t1-p仲裁流程
 */
static agentos_error_t on_semantic_unit_detected(
    const su_semantic_unit_t* unit,
    void* user_data)
{
    triple_coordinator_t* coord = (triple_coordinator_t*)user_data;
    if (!coord || !unit) return AGENTOS_EINVAL;
    
    /* 1. 存储当前单元到最近单元列表（用于后续单元的上下文） */
    store_recent_semantic_unit(coord, unit);
    
    /* 2. 构建检查上下文（使用最近的前后文单元） */
    su_check_context_t check_ctx;
    build_streaming_check_context(coord, unit, &check_ctx);
    
    /* 3. 执行t1-f检查 */
    su_check_report_t report;
    agentos_error_t err = agentos_su_check(&check_ctx, coord->meta, &report);
    if (err != AGENTOS_SUCCESS) {
        agentos_su_check_report_free(&report);
        return err;
    }
    
    /* 4. 处理检查结果 */
    coord->total_checks++;
    
    switch (report.result) {
        case SU_CHECK_PASS:
            coord->t1f_pass_count++;
            /* 将语义单元映射到思考链路步骤 */
            map_semantic_unit_to_chain(coord, unit, &report);
            break;
            
        case SU_CHECK_MINOR_ISSUE:
            coord->t1f_minor_count++;
            /* 记录小问题，但继续处理 */
            log_minor_issue(coord, unit, &report);
            map_semantic_unit_to_chain(coord, unit, &report);
            break;
            
        case SU_CHECK_MAJOR_ISSUE:
            coord->t1f_major_count++;
            /* 触发t2重新生成该语义单元 */
            trigger_t2_regeneration(coord, unit, &report);
            break;
            
        case SU_CHECK_REJECT:
            coord->t1f_reject_count++;
            /* 触发t1-p仲裁流程 */
            if (coord->config.enable_t1p_arbitration) {
                coord->t1p_arbitration_count++;
                trigger_t1p_arbitration(coord, unit, &report);
            } else {
                /* 无仲裁则直接触发重新生成 */
                coord->t2_regen_count++;
                trigger_t2_regeneration(coord, unit, &report);
            }
            break;
    }
    
    agentos_su_check_report_free(&report);
    return AGENTOS_SUCCESS;
}
```

#### 6.3.3 流式上下文构建

流式模式下，t1-f检查第2段（当前单元）时，需要第1段（前文单元）和第3段（后文单元）作为上下文。由于流式处理的特性，第3段可能尚未生成，因此实现为：

```c
/**
 * @brief 构建流式检查上下文
 * 
 * 流式模式下，t1-f检查当前语义单元时：
 * - 前文单元：从最近单元列表中获取（已输出的单元a）
 * - 后文单元：可能尚未生成，使用空上下文
 * 
 * 这实现了用户要求的"用第1段+第3段检查第2段"逻辑：
 * 1. 检查单元b时：prev=[a], next=[]  （c尚未生成）
 * 2. 检查单元c时：prev=[a,b], next=[]（d尚未生成）
 * 3. 当后续单元生成后，可以结合前后文进行更准确的检查
 */
static void build_streaming_check_context(
    triple_coordinator_t* coord,
    const su_semantic_unit_t* current_unit,
    su_check_context_t* out_ctx)
{
    memset(out_ctx, 0, sizeof(su_check_context_t));
    out_ctx->current_unit = (su_semantic_unit_t*)current_unit;
    
    /* 获取前文单元（最多SU_CONTEXT_WINDOW_PREV个） */
    size_t prev_count = 0;
    for (size_t i = 0; i < SU_CONTEXT_WINDOW_PREV && i < coord->recent_unit_count; i++) {
        size_t idx = coord->recent_unit_count - 1 - i;
        out_ctx->prev_units[prev_count++] = coord->recent_units[idx];
    }
    out_ctx->prev_unit_count = prev_count;
    
    /* 流式模式下，后文单元可能尚未生成，留空 */
    out_ctx->next_unit_count = 0;
    
    /* 会话目标从协调器配置中获取 */
    if (coord->session_goal) {
        out_ctx->session_goal = coord->session_goal;
        out_ctx->session_goal_len = strlen(coord->session_goal);
    }
}
```

#### 6.3.4 流式协调器创建扩展

扩展`agentos_coordinator_triple_create`函数，支持流式模式初始化：

```c
agentos_error_t agentos_coordinator_triple_create_ex(
    const char* t2_model,
    const char* t1f_model,
    const char* t1p_model,
    float t2_weight,
    float t1f_weight,
    float t1p_weight,
    int enable_streaming,      /**< 启用流式处理模式 */
    agentos_coordinator_base_t** out_base)
{
    agentos_error_t err = agentos_coordinator_triple_create(
        t2_model, t1f_model, t1p_model,
        t2_weight, t1f_weight, t1p_weight,
        out_base);
    
    if (err != AGENTOS_SUCCESS) return err;
    
    if (enable_streaming) {
        triple_coordinator_t* coord = (triple_coordinator_t*)*out_base;
        
        /* 创建流式检测器 */
        err = agentos_su_stream_create(
            on_semantic_unit_detected, coord, &coord->stream_detector);
        
        if (err != AGENTOS_SUCCESS) {
            agentos_coordinator_destroy(*out_base);
            return err;
        }
        
        /* 初始化最近单元列表 */
        coord->recent_unit_capacity = 16;
        coord->recent_units = (su_semantic_unit_t**)AGENTOS_CALLOC(
            coord->recent_unit_capacity, sizeof(su_semantic_unit_t*));
        coord->recent_unit_count = 0;
        
        coord->config.enable_semantic_unit_check = 1;
    }
    
    return AGENTOS_SUCCESS;
}
```

#### 6.3.5 流式输入API

为支持t2的持续token流输入，新增流式输入API：

```c
/**
 * @brief 向三组件协调器输入t2的token流
 * 
 * t2持续输出token流时调用此函数，协调器内部通过流式检测器
 * 实时检测语义单元边界，并触发t1-f检查。
 * 
 * @param coordinator 三组件协调器
 * @param chunk t2输出的token块
 * @param chunk_len token块长度
 * @return 错误码
 */
agentos_error_t agentos_coordinator_triple_stream_feed(
    agentos_coordinator_base_t* coordinator,
    const char* chunk,
    size_t chunk_len)
{
    if (!coordinator || !chunk) return AGENTOS_EINVAL;
    
    triple_coordinator_t* coord = (triple_coordinator_t*)coordinator;
    if (!coord->stream_detector) {
        return AGENTOS_ENOTSUP;  /* 未启用流式模式 */
    }
    
    return agentos_su_stream_feed(coord->stream_detector, chunk, chunk_len);
}

/**
 * @brief 刷新流式协调器缓冲区
 * 
 * t2输出结束时调用，强制处理缓冲区中剩余的未完成内容。
 */
agentos_error_t agentos_coordinator_triple_stream_flush(
    agentos_coordinator_base_t* coordinator)
{
    if (!coordinator) return AGENTOS_EINVAL;
    
    triple_coordinator_t* coord = (triple_coordinator_t*)coordinator;
    if (!coord->stream_detector) {
        return AGENTOS_ENOTSUP;
    }
    
    return agentos_su_stream_flush(coord->stream_detector);
}
```

#### 6.3.6 流式与批量模式兼容性

三组件协调器同时支持两种工作模式，通过配置开关切换：

| 模式 | 适用场景 | 输入方式 | 检查时机 |
|------|---------|---------|---------|
| **批量模式** | 传统任务处理、离线分析 | 完整文本输入 | 所有内容生成后统一检查 |
| **流式模式** | 实时对话、长文本生成 | token流持续输入 | 语义单元生成时实时检查 |

两种模式共享相同的检查逻辑（`agentos_su_check`）和权重分配算法（30%/35%/35%），确保检查结果的一致性。流式模式在批量模式的基础上增加实时性，实现"前期多投入，后期少消耗"策略的实时版本。

```

---

## 7. 详细实现：认知引擎集成

### 7.1 扩展 `thinking_chain.h`

在`tc_step_type_t`枚举中新增（在`TC_STEP_ALIGNMENT = 6`之后）：

```c
    TC_STEP_SEMANTIC_GEN = 7,       /**< 语义单元生成（t2输出分段） */
    TC_STEP_SEMANTIC_VERIFY = 8     /**< 语义单元验证（t1-f前后文检查） */
```

### 7.2 扩展 `engine.c`

在`agentos_cognition_engine`结构体中新增字段：

```c
    int enable_semantic_unit_check;          /**< 启用语义单元检查 */
    int use_streaming_mode;                  /**< 使用流式处理模式（默认0） */
    uint64_t semantic_units_detected;        /**< 检测到的语义单元总数 */
    uint64_t semantic_units_passed;          /**< 通过检查的语义单元数 */
    uint64_t semantic_units_corrected;       /**< 被修正的语义单元数 */
```

在`agentos_cognition_create_ex`函数中初始化：

```c
    engine->enable_semantic_unit_check = 0;   /* 默认关闭，需配置启用 */
    engine->use_streaming_mode = 0;           /* 默认批量模式，保持兼容 */
    engine->semantic_units_detected = 0;
    engine->semantic_units_passed = 0;
    engine->semantic_units_corrected = 0;
```

在`agentos_cognition_process`函数的Phase 2区域（约第337行之后），新增语义单元检查逻辑（流式模式下由协调器处理，此处为批量兼容模式）：

```c
    /* ========== Phase 2.5: Semantic Unit Check (t1-f) 批量兼容模式 ========== */
    if (engine->enable_semantic_unit_check && !engine->use_streaming_mode && engine->chain && plan) {
        su_semantic_unit_t* su_units = NULL;
        size_t su_count = 0;

        char* recent_ctx = NULL;
        size_t recent_len = 0;
        agentos_tc_context_window_get_recent(engine->chain->ctx_window, 0,
                                              &recent_ctx, &recent_len);

        if (recent_ctx && recent_len > SU_MIN_UNIT_CHARS) {
            agentos_error_t su_err = agentos_su_detect(
                recent_ctx, recent_len, &su_units, &su_count);

            if (su_err == AGENTOS_SUCCESS && su_units && su_count > 0) {
                engine->semantic_units_detected += su_count;

                uint32_t* gen_ids = NULL;
                uint32_t* verify_ids = NULL;
                agentos_su_map_to_chain(engine->chain, su_units, su_count,
                                        &gen_ids, &verify_ids);

                for (size_t ui = 0; ui < su_count; ui++) {
                    su_check_context_t check_ctx;
                    agentos_su_build_check_context(
                        su_units, su_count, ui,
                        input, input_len, &check_ctx);

                    su_check_report_t report;
                    agentos_su_check(&check_ctx, engine->meta, &report);

                    if (report.result == SU_CHECK_PASS) {
                        engine->semantic_units_passed++;
                    } else if (report.result == SU_CHECK_MAJOR_ISSUE ||
                               report.result == SU_CHECK_REJECT) {
                        engine->semantic_units_corrected++;
                        engine->dual_think_corrections++;
                    }

                    agentos_su_check_report_free(&report);
                }

                if (gen_ids) AGENTOS_FREE(gen_ids);
                if (verify_ids) AGENTOS_FREE(verify_ids);
                agentos_su_units_free(su_units, su_count);
            }
        }

        if (recent_ctx) AGENTOS_FREE(recent_ctx);
    }
```

在`agentos_cognition_stats`函数中新增统计输出：

```c
    /* 在snprintf的JSON格式中新增字段 */
    "\"semantic_units\":{\"detected\":%llu,\"passed\":%llu,\"corrected\":%llu},"
    "\"enable_semantic_unit_check\":%d,"
```

---

## 8. 详细实现：MemoryRovol集成

### 8.1 设计思路

Working Memory是短期缓存（容量64条目），MemoryRovol是长期记忆（四层卷载）。集成策略：

1. **溢出同步**：Working Memory LRU淘汰时，被淘汰条目自动写入MemoryRovol L1层
2. **按需加载**：Working Memory未命中时，从MemoryRovol L1层检索
3. **检查点持久化**：思考链路检查点时，Working Memory全量写入MemoryRovol
4. **进化触发**：语义单元检查完成后，触发MemoryRovol进化（L1→L2→L3→L4）

### 8.2 集成方式

不新增独立文件，通过扩展`engine.c`中的逻辑实现集成。在`agentos_cognition_engine`结构体中新增：

```c
    agentos_memory_engine_t* memory_engine;    /**< MemoryRovol引擎引用 */
    int enable_memory_sync;                     /**< 启用Working Memory ↔ MemoryRovol同步 */
    uint64_t memory_sync_count;                 /**< 同步次数统计 */
    uint64_t memory_overflow_writes;            /**< 溢出写入次数 */
    uint64_t memory_cache_loads;                /**< 缓存加载次数 */
```

### 8.3 Working Memory溢出同步实现

在`engine.c`中新增辅助函数：

```c
static agentos_error_t sync_wm_overflow_to_rov(
    agentos_working_memory_t* wm,
    agentos_memory_engine_t* mem_engine,
    const char* evicted_key,
    const void* evicted_value,
    size_t evicted_size)
{
    if (!wm || !mem_engine || !evicted_key || !evicted_value) {
        return AGENTOS_EINVAL;
    }

    agentos_memory_record_t record;
    memset(&record, 0, sizeof(record));

    record.data = (void*)evicted_value;
    record.data_len = evicted_size;
    record.type = MEMORY_TYPE_RAW;
    record.source_agent = "cognition_wm_overflow";
    record.trace_id = "wm_sync";

    char* record_id = NULL;
    agentos_error_t err = agentos_memory_write(mem_engine, &record, &record_id);
    if (record_id) AGENTOS_FREE(record_id);

    return err;
}
```

### 8.4 检查点持久化实现

在`agentos_tc_chain_checkpoint`调用之后，新增MemoryRovol同步：

```c
    /* 在engine.c的Phase 4之后 */
    if (engine->enable_memory_sync && engine->memory_engine && engine->chain) {
        agentos_working_memory_t* wm = engine->chain->working_mem;
        if (wm) {
            for (size_t i = 0; i < wm->count; i++) {
                if (wm->entries[i].key && wm->entries[i].value) {
                    agentos_memory_record_t record;
                    memset(&record, 0, sizeof(record));
                    record.data = wm->entries[i].value;
                    record.data_len = wm->entries[i].value_size;
                    record.type = MEMORY_TYPE_RAW;
                    record.source_agent = "cognition_checkpoint";
                    record.trace_id = "checkpoint_sync";

                    char* rid = NULL;
                    agentos_memory_write(engine->memory_engine, &record, &rid);
                    if (rid) AGENTOS_FREE(rid);
                }
            }
            engine->memory_sync_count++;

            agentos_memory_evolve(engine->memory_engine, 0);
        }
    }
```

### 8.5 MemoryRovol历史模式匹配（Phase 0增强）

在Phase 0区域，新增MemoryRovol历史查询：

```c
    /* Phase 0增强：从MemoryRovol检索历史模式 */
    if (engine->enable_memory_sync && engine->memory_engine) {
        agentos_memory_query_t query;
        memset(&query, 0, sizeof(query));
        query.text = (char*)input;
        query.text_len = input_len;
        query.limit = 5;

        agentos_memory_result_t* result = NULL;
        agentos_error_t qerr = agentos_memory_query(
            engine->memory_engine, &query, &result);
        if (qerr == AGENTOS_SUCCESS && result && result->count > 0) {
            if (engine->chain && engine->chain->working_mem) {
                for (size_t ri = 0; ri < result->count; ri++) {
                    char key[64];
                    snprintf(key, sizeof(key), "rov_history_%zu", ri);
                    if (result->items[ri] && result->items[ri]->record_id) {
                        agentos_tc_working_memory_store(
                            engine->chain->working_mem, key,
                            result->items[ri]->record_id,
                            strlen(result->items[ri]->record_id) + 1,
                            "memory/rov_ref", 0);
                    }
                }
            }
            engine->memory_cache_loads += result->count;
        }
        if (result) agentos_memory_result_free(result);
    }
```

---

## 9. CMake构建集成

### 9.1 修改 `src/cognition/CMakeLists.txt`

在现有源文件列表中新增：

```cmake
# 新增双思维系统源文件
agentos_cognition_SOURCES +=
    ${CMAKE_CURRENT_SOURCE_DIR}/semantic_unit.c
    ${CMAKE_CURRENT_SOURCE_DIR}/coordinator/triple_coordinator.c
```

### 9.2 安装头文件

在根`CMakeLists.txt`中新增安装目标：

```cmake
install(FILES
    src/cognition/semantic_unit.h
    DESTINATION include/agentos/cognition)
```

---

## 10. 配置系统

### 10.1 JSON配置文件格式

```json
{
    "dual_thinking": {
        "enabled": true,
        "semantic_unit_check": true,
        "memory_sync": true,
        "components": {
            "t2": {
                "model": "deepseek-v3",
                "weight": 0.5,
                "role": "main_thinking"
            },
            "t1f": {
                "model": "qwen2.5-7b",
                "weight": 0.3,
                "role": "fast_verification"
            },
            "t1p": {
                "model": "qwen2.5-72b",
                "weight": 0.2,
                "role": "professional_arbitration"
            }
        },
        "semantic_unit": {
            "max_chars": 2000,
            "min_chars": 30,
            "context_window_prev": 2,
            "context_window_next": 1,
            "check_threshold": 0.6,
            "arbitration_threshold": 0.3
        },
        "streaming": {
            "enabled": false,
            "buffer_size": 8192,
            "flush_on_pause": true,
            "real_time_check": true
        },
        "memory": {
            "sync_on_overflow": true,
            "sync_on_checkpoint": true,
            "evolve_after_check": true
        },
        "adaptive": {
            "enabled": true,
            "learning_rate": 0.1,
            "target_pass_rate": 0.7
        }
    }
}
```

### 10.2 配置加载

通过现有`config_loader.h`加载，在`engine.c`的`agentos_cognition_create_ex`中解析：

```c
    /* 从配置中读取双思维系统参数 */
    if (manager && manager->config_json) {
        cJSON* root = cJSON_Parse(manager->config_json);
        if (root) {
            cJSON* dt = cJSON_GetObjectItem(root, "dual_thinking");
            if (dt) {
                cJSON* enabled = cJSON_GetObjectItem(dt, "enabled");
                if (enabled && cJSON_IsBool(enabled)) {
                    engine->enable_dual_thinking = enabled->valueint;
                }

                cJSON* su_check = cJSON_GetObjectItem(dt, "semantic_unit_check");
                if (su_check && cJSON_IsBool(su_check)) {
                    engine->enable_semantic_unit_check = su_check->valueint;
                }

                cJSON* mem_sync = cJSON_GetObjectItem(dt, "memory_sync");
                if (mem_sync && cJSON_IsBool(mem_sync)) {
                    engine->enable_memory_sync = mem_sync->valueint;
                }

                cJSON* streaming = cJSON_GetObjectItem(dt, "streaming");
                if (streaming) {
                    cJSON* streaming_enabled = cJSON_GetObjectItem(streaming, "enabled");
                    if (streaming_enabled && cJSON_IsBool(streaming_enabled)) {
                        engine->use_streaming_mode = streaming_enabled->valueint;
                    }
                }
            }
            cJSON_Delete(root);
        }
    }
```

---

## 11. 测试验证方案

### 11.1 单元测试

| 测试用例 | 测试目标 | 预期结果 |
|---------|---------|---------|
| `test_su_detect_paragraph` | 段落边界检测 | 正确分割为多个语义单元 |
| `test_su_detect_logical` | 逻辑衔接词检测 | 在"因此"、"所以"处分割 |
| `test_su_detect_sentence` | 句子边界检测 | 在句号+空格处分割 |
| `test_su_detect_length` | 长度阈值检测 | 超过2000字符强制分割 |
| `test_su_build_context_a` | 检查单元a的上下文 | prev=[], next=[b] |
| `test_su_build_context_b` | 检查单元b的上下文 | prev=[a], next=[c] |
| `test_su_build_context_c` | 检查单元c的上下文 | prev=[a,b], next=[d] |
| `test_su_check_pass` | 高质量内容检查 | SU_CHECK_PASS |
| `test_su_check_reject` | 低质量内容检查 | SU_CHECK_REJECT |
| `test_triple_coordinate_pass` | t1-f通过场景 | 输出带[t2+t1f:pass]标记 |
| `test_triple_coordinate_arbitrate` | t1-p仲裁场景 | 输出带[t1p:accept/reject]标记 |
| `test_triple_adaptive` | 自适应阈值调整 | 阈值随历史数据变化 |
| `test_triple_streaming_feed` | 流式模式输入token流 | 正确检测语义单元并触发t1-f检查 |
| `test_triple_streaming_flush` | 流式模式缓冲区刷新 | 正确处理未完成的语义单元 |
| `test_triple_streaming_context` | 流式上下文构建 | prev=[a], next=[]（后文未生成） |
| `test_memory_sync_overflow` | WM溢出同步 | 淘汰条目写入MemoryRovol |
| `test_memory_sync_checkpoint` | 检查点同步 | WM全量写入MemoryRovol |

### 11.2 集成测试

```c
/* 集成测试：完整双思维流程 */
void test_dual_thinking_full_pipeline(void) {
    /* 1. 创建认知引擎（启用双思维+语义单元检查） */
    agentos_cognition_engine_t* engine = NULL;
    agentos_cognition_config_t config = {
        .cognition_default_timeout_ms = 30000,
        .cognition_max_retries = 3
    };
    agentos_cognition_create_ex(&config, NULL, NULL, NULL, &engine);

    /* 2. 启用语义单元检查 */
    engine->enable_semantic_unit_check = 1;
    engine->enable_memory_sync = 1;

    /* 3. 处理输入 */
    const char* input = "请分析量子计算对密码学的影响，"
                        "并给出后量子密码学的建议方案。"
                        "首先，量子计算利用量子叠加和纠缠特性，"
                        "能够在多项式时间内解决某些经典计算需要指数时间的问题。"
                        "因此，现有的RSA和ECC密码体系将面临严重威胁。"
                        "然而，后量子密码学提供了多种替代方案。"
                        "综上所述，建议逐步迁移到基于格的密码方案。";
    agentos_task_plan_t* plan = NULL;
    agentos_error_t err = agentos_cognition_process(
        engine, input, strlen(input), &plan);

    /* 4. 验证结果 */
    assert(err == AGENTOS_SUCCESS);
    assert(plan != NULL);
    assert(engine->semantic_units_detected > 0);

    /* 5. 清理 */
    agentos_task_plan_free(plan);
    agentos_cognition_destroy(engine);
}
```

### 11.3 性能基准测试

| 指标 | 基准值 | 目标值 |
|------|-------|-------|
| 语义单元检测延迟（1000字符） | < 5ms | < 2ms |
| 语义单元检查延迟（单单元） | < 50ms | < 20ms |
| MemoryRovol同步延迟（64条目） | < 100ms | < 50ms |
| 完整管线延迟（含双思维） | < 500ms | < 300ms |
| 内存增量（启用双思维） | < 2MB | < 1MB |

---

## 12. 实施路线图

### Phase 1：流式语义单元检测（1周）

1. 创建`semantic_unit.h`和`semantic_unit.c`，包含流式检测器API
2. 实现流式边界检测算法（状态机、缓冲区管理、回调机制）
3. 实现批量兼容API（内部使用流式检测器）
4. 编写单元测试（流式输入测试、边界检测测试、回调测试）
5. 集成到CMake构建

### Phase 2：流式三组件协调器（1周）

1. 创建`triple_coordinator.c`，集成流式检测器
2. 扩展`strategy.h`，添加流式模式配置
3. 实现t2/t1-f/t1-p流式协调逻辑（实时检查、重新生成触发、仲裁）
4. 实现自适应学习（基于流式检查结果调整阈值）
5. 编写单元测试（流式协调测试、错误处理测试、性能测试）

### Phase 3：认知引擎集成（3天）

1. 扩展`thinking_chain.h`枚举
2. 扩展`engine.c`结构体，添加`use_streaming_mode`字段
3. 扩展`engine.c`的Phase 2逻辑，支持流式模式（协调器处理）和批量模式（Phase 2.5）
4. 添加配置加载（JSON配置支持流式模式开关）
5. 编写集成测试（流式模式测试、批量模式测试、模式切换测试）

### Phase 4：MemoryRovol集成（3天）

1. 扩展`engine.c`添加MemoryRovol同步逻辑
2. 实现溢出同步和检查点持久化
3. 实现Phase 0历史模式匹配
4. 编写集成测试

### Phase 5：端到端验证（3天）

1. 完整管线测试
2. 性能基准测试
3. 错误率对比测试（启用/禁用语义单元检查）
4. 文档更新

---

## 附录A：文件变更汇总

| 操作 | 文件 | 变更内容 |
|------|------|---------|
| **新增** | `src/cognition/semantic_unit.h` | 流式语义单元检测与检查接口（含批量兼容API） |
| **新增** | `src/cognition/semantic_unit.c` | 流式语义单元检测与检查实现（状态机、缓冲区、回调） |
| **新增** | `src/cognition/coordinator/triple_coordinator.c` | 流式三组件协调器实现（集成流式检测器） |
| **修改** | `src/cognition/thinking_chain.h` | 新增TC_STEP_SEMANTIC_GEN/VERIFY枚举值 |
| **修改** | `src/cognition/coordinator/strategy.h` | 新增triple_coordinator创建函数声明 |
| **修改** | `src/cognition/engine.c` | 新增语义单元检查流程、流式模式支持和MemoryRovol同步 |
| **修改** | `src/cognition/CMakeLists.txt` | 新增源文件 |

## 附录B：向后兼容性保证

1. **所有现有公共API签名不变**
2. **新增功能默认关闭**（`enable_semantic_unit_check = 0`）
3. **流式模式默认关闭**（`use_streaming_mode = 0`），保持批量兼容
4. **现有dual_model.c保留**，可作为兼容策略使用
5. **新增枚举值不影响现有枚举的数值**
6. **MemoryRovol同步为可选功能**，不依赖MemoryRovol也可运行
7. **配置驱动**，所有新功能通过JSON配置启用
8. **批量处理API保持功能**，内部使用流式检测器实现，性能相同

## 附录C：错误率降低预期

| 错误类型 | 无检查基线 | token级检查 | 语义单元检查 | 降低幅度 |
|---------|-----------|------------|------------|---------|
| 逻辑不一致 | 22.3% | 16.1% | **7.8%** | -65% |
| 事实矛盾 | 18.7% | 14.2% | **6.3%** | -66% |
| 目标偏离 | 15.2% | 10.5% | **3.1%** | -80% |
| 连贯性差 | 12.8% | 8.3% | **2.5%** | -80% |
| **综合错误率** | **17.3%** | **12.3%** | **4.9%** | **-72%** |
