# MemoryRovol 商业化重构方案 v11.11

**版本**: v11.11.0-第09大轮次·闭源严控版  
**核心变更**: 废弃 v11.10 "源码限速"方案 → 改为"单二进制+License全控"闭源架构  
**日期**: 2026-04-29

---

> **v11.10 回顾与修正**：
> - ❌ v11.10 提出"社区版源码开放+限速"——**违背了源码不泄露的要求**
> - ❌ v11.10 的"社区版全功能"思路——**过宽松，开发者有全功能可用就无需购买**
> - ✅ v11.11 改为：**无源码分发，单预编译库，License 控制一切，试用期极严**

---

## 第1章 — 核心架构原则

### 1.1 三项铁律

| 铁律 | 说明 | 强制方式 |
|------|------|---------|
| **🔒 零源码分发** | MemoryRovol 只交付 `.a`/`.lib` + C 头文件 + `license.lic` | 无源码仓库，仅 CI 产物分发 |
| **🔑 License 全控** | 一个二进制 = 所有层级，License 文件决定启用哪些功能 | `__attribute__((constructor))` 在 main() 前初始化 license 状态 |
| **⚖️ 按需付费** | 试用/Pro/Enterprise/Enterprise+ 四级，严格功能隔离 | 编译时预埋门禁点，License 解锁 |

### 1.2 关键技术路线

```
                    MemoryRovol 商业化分发模型

┌─────────────────────────────────────────────────────────────────────┐
│                         Spharx 官网 CDN                              │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Trial 版      │  │ Pro 版       │  │ Enterprise   │               │
│  │ 14天试用      │  │ 永久许可     │  │ 年付许可     │               │
│  │ 100条记忆     │  │ 1万条记忆    │  │ 无限记忆     │               │
│  │ L1+L2 仅    │  │ L1+L2+L3    │  │ 全功能       │               │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘               │
│         │                 │                 │                        │
│         ▼                 ▼                 ▼                        │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │             同一预编译库 `libmemoryrovol.a`                       │ │
│  │             （OLLVM混淆 + strip -s + 字符串加密）                 │ │
│  │             所有分级代码都在同一个二进制中                           │ │
│  │             运行时根据 `license.lic` 决定开放哪些功能               │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│         │                 │                 │                        │
│         ▼                 ▼                 ▼                        │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │             License 签发系统 (Spharx License Server)              │ │
│  │             生成 RSA-4096 签名 → license.lic                      │ │
│  │             用户购买后通过邮箱/下载获取                            │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 第2章 — 分层定义（四级限制体系）

### 2.1 层级总表

| 维度 | Trial（试用） | Pro（个人/小团队） | Enterprise（企业） | Enterprise+（高阶） |
|------|-------------|-------------------|-------------------|-------------------|
| **定价** | **免费** | **$299/年** | **$2,990/年** | **$15,000+/年** |
| **有效期限** | 14天（硬限制） | 1年（可续费） | 1年（可续费） | 永久（源码审计级） |
| **L1 原始卷** | ✅ 最多100条 | ✅ 全功能 | ✅ 全功能 | ✅ 全功能 |
| **L2 特征层** | ✅ 最多100向量 | ✅ 全功能 | ✅ 全功能 | ✅ 全功能 |
| **L3 结构层** | ❌ 禁用 | ✅ ≤1,000 实体 | ✅ 全功能 | ✅ 全功能 |
| **L4 模式层** | ❌ 禁用 | ❌ 禁用 | ✅ 全功能 | ✅ 全功能 |
| **遗忘引擎** | ❌ 禁用 | ✅ 基础（艾宾浩斯） | ✅ 全策略 | ✅ 全策略+定制 |
| **吸引子检索** | ❌ 禁用 | ✅ 基础检索 | ✅ 完整检索 | ✅ 完整检索+定制 |
| **LLM 客户端** | ❌ 禁用 | ✅ 基础(S2) | ✅ DS-004全链路 | ✅ 全链路+定制 |
| **最大 Agent 数** | 1 | 10 | 无限 | 无限 |
| **向量维度上限** | 128 | 768 | 1536 | 无限制 |
| **人工延迟** | **3秒/操作** | 无 | 无 | 无 |
| **技术支持** | 社区 | 邮件(48h) | 专属(8h) | SLA定制 |
| **私有化构建** | ❌ | ❌ | ✅ | ✅ |
| **源码审计权** | ❌ | ❌ | ❌ | ✅ |

### 2.2 定价策略逻辑

| 层级 | 定价 | 目标用户群 | 年收入目标 |
|------|------|-----------|-----------|
| Trial | $0 | 开发者评估、集成测试 | — |
| Pro | $299/年 | 独立开发者、开源项目 | 2000用户 → $600K |
| Enterprise | $2,990/年 | 中小企业、商业产品 | 300用户 → $900K |
| Enterprise+ | $15,000+/年 | 大企业、嵌入式场景 | 30用户 → $450K |
| **合计** | | | **~$2M/年** |

### 2.3 Trial 版的核心设计思路

**Trial 不是"轻量版"，而是"试用装"**：

```
Trial 版的使用体验（故意设计的"痛感"）：
┌─────────────────────────────────────────────────┐
│ 创建引擎 ✓  —— 编译通过、API 可调用          │
│ 写入10条记忆 ✓                                 │
│ 写入100条 ✓   —— 到达 L1 上限！              │
│ 再次写入 ❌   "Trial: memory limit reached"    │
│                                                │
│ 调用 L3 ❌    "Trial: L3 disabled"             │
│ 调用 L4 ❌    "Trial: L4 disabled"             │
│                                                │
│ 每次调用延迟 3秒 —— 故意慢                     │
│                                                │
│ 14天后 ❌    "Trial expired. Purchase at..."   │
└─────────────────────────────────────────────────┘
```

**设计原则**：让开发者可以验证编译集成没问题、API 接口能调通，但无法做任何实际工作。真正的价值需要购买才能体验。

---

## 第3章 — 技术实现方案

### 3.1 单二进制 + License 全控架构

**核心思想**：所有分级代码编译到同一个静态库中，运行时通过 `license.lic` 决定开放层级。

```c
// ==================== license.h ====================
// MemoryRovol License 验证系统
// 编译到 libmemoryrovol.a 中，无源码分发

typedef enum {
    LICENSE_TRIAL = 0,       // 14天试用
    LICENSE_PRO = 1,         // Pro
    LICENSE_ENTERPRISE = 2,  // Enterprise
    LICENSE_ENTERPRISE_PLUS = 3 // Enterprise+
} license_tier_t;

typedef struct {
    license_tier_t tier;
    uint32_t max_memories;
    uint32_t max_agents;
    uint16_t max_vector_dim;
    bool l3_enabled;
    bool l4_enabled;
    bool forgetting_enabled;
    bool attractor_enabled;
    bool llm_client_enabled;
    uint32_t artificial_delay_ms;   // 试用版人工延迟
    uint32_t trial_days_remaining;  // 试用剩余天数
    time_t expiry;                  // 过期时间
    bool valid;                     // License 是否有效
} license_state_t;

// 全局 License 状态（编译时初始化，运行时只读）
extern license_state_t g_license;

// 自动初始化（main() 之前执行）
void license_init(void) __attribute__((constructor));
```

```c
// ==================== license.c ====================
// 编译到 libmemoryrovol.a 中

#include "license.h"

license_state_t g_license = {0};

// RSA-4096 公钥（字节数组，禁止字符串明文）
// 由 keygen.py 生成，编译时嵌入
static const unsigned char g_rsa_pubkey[] = {
    0x30, 0x82, 0x02, 0x0a, 0x02, 0x02, 0x01, 0x01, ...
    // 共 526 字节 RSA-4096 公钥 DER 格式
    // 生成方式：openssl rsa -pubout -outform DER
};

void license_init(void) {
    // 1. 环境变量检查：SPHARX_DEV_TEAM=1 → 无条件解锁全部（开发团队内部用）
    const char* dev_mode = getenv("SPHARX_DEV_TEAM");
    if (dev_mode && dev_mode[0] == '1') {
        g_license.tier = LICENSE_ENTERPRISE_PLUS;
        g_license.valid = true;
        g_license.l3_enabled = true;
        g_license.l4_enabled = true;
        g_license.forgetting_enabled = true;
        g_license.max_memories = UINT32_MAX;
        // ... 全部解锁
        return;
    }

    // 2. 尝试读取 license.lic 文件
    //    环境变量 MEMORYROVOL_LICENSE → 自定义路径
    //    fallback → /etc/memoryrovol/license.lic
    //    fallback → ./license.lic
    
    // 3. 验证 RSA-4096 签名
    //    - 从文件中读取 JSON payload
    //    - 提取 signature Base64 → 解码
    //    - RSA_verify(NID_sha256, payload, sig)
    
    // 4. 验证过期时间
    //    if (expiry < time(NULL)) → g_license.valid = false
    
    // 5. 填充 g_license 状态
    
    // 6. 如果找不到 license.lic → 启用 Trial 模式（14天）
    //    - 首次运行时在 ~/.memoryrovol/trial_start 写入时间戳
    //    - 每次启动检查是否超过14天
}
```

### 3.2 五种限制机制（编译到二进制中）

#### 限制1 — 功能门禁（硬限制）

```c
// memoryrovol.c — 所有 L3/L4/遗忘引擎入口点
// 预埋门禁检查，License 不允许时直接返回 AGENTOS_ELICENSE

agentos_error_t agentos_knowledge_graph_create(...) {
    if (!g_license.l3_enabled) {
        AGENTOS_LOG_WARN("[MemoryRovol] L3 requires Pro license. "
                        "Visit https://spharx.cn/memoryrovol");
        return AGENTOS_ELICENSE;
    }
    // ... 正常逻辑
}

agentos_error_t agentos_rule_generator_create(...) {
    if (!g_license.l4_enabled) {
        AGENTOS_LOG_WARN("[MemoryRovol] L4 requires Enterprise license. "
                        "Visit https://spharx.cn/memoryrovol");
        return AGENTOS_ELICENSE;
    }
    // ... 正常逻辑
}
```

#### 限制2 — 容量门禁（硬上限）

```c
// engine.c — 写入记忆时检查容量限制

agentos_error_t agentos_memoryrov_add_memory(handle, content, len) {
    // 检查当前记忆总数
    size_t current_count = get_current_memory_count(handle);
    if (current_count >= g_license.max_memories) {
        AGENTOS_LOG_WARN("[MemoryRovol] Memory limit reached (%u/%u). "
                        "Upgrade at https://spharx.cn/memoryrovol",
                        current_count, g_license.max_memories);
        return AGENTOS_ELIMIT;
    }
    // ... 正常写入逻辑
}
```

#### 限制3 — 向量维度上限

```c
// 创建嵌入模型时校验
agentos_error_t agentos_embedder_create(config, ...) {
    if (config->dimension > g_license.max_vector_dim) {
        return AGENTOS_ELIMIT;  // Trial 最高128维
    }
}
```

#### 限制4 — 使用期限

```c
// 所有 API 入口统一检查
#define LICENSE_CHECK_EXPIRY() \
    do { \
        if (!g_license.valid) { \
            AGENTOS_LOG_WARN("[MemoryRovol] License expired. " \
                            "Renew at https://spharx.cn/memoryrovol"); \
            return AGENTOS_ELICENSE; \
        } \
    } while(0)
```

#### 限制5 — 人工延迟（Trial 版）

```c
// Trial 版：每次操作插入 3 秒延迟
#define LICENSE_APPLY_DELAY() \
    do { \
        if (g_license.artificial_delay_ms > 0) { \
            agentos_sleep_ms(g_license.artificial_delay_ms); \
        } \
    } while(0)

// 在 memoryrovol.c 中每个 API 入口调用
agentos_error_t agentos_memoryrov_add_memory(...) {
    LICENSE_CHECK_EXPIRY();
    LICENSE_APPLY_DELAY();  // Trial 版：+3秒
    ...
}
```

### 3.3 预编译与混淆策略

| 步骤 | 工具/方法 | 说明 |
|------|----------|------|
| **1. 编译** | GCC/Clang O2 | Release 编译，开启 LTO |
| **2. 混淆** | OLLVM | 启用控制流平坦化 + 虚假分支 + 指令替换 |
| **3. 字符串加密** | 自定义脚本 | 所有 "AGENTOS_ELICENSE" "license.lic" 等关键字符串运行时解密 |
| **4. 符号剥离** | `strip -s` | 仅保留 `agentos_memoryrov_init` `agentos_memoryrov_create` 等 ~5 个必要导出符号 |
| **5. 哈希校验** | 编译时嵌入 | 库自身 SHA-256 哈希，防止被篡改 |
| **6. 代码签名** | 可选 | Windows：Authenticode；macOS：notarization |

### 3.4 License.lic 文件格式

```json
{
    "version": 2,
    "tier": "pro",
    "issue_date": "2026-05-01",
    "expiry_date": "2027-05-01",
    "features": {
        "max_memories": 10000,
        "max_agents": 10,
        "max_vector_dim": 768,
        "max_entities": 1000,
        "l3_enabled": true,
        "l4_enabled": false,
        "forgetting_enabled": true,
        "attractor_enabled": true,
        "llm_enabled": true,
        "llm_model": "s2_generation"
    },
    "customer": {
        "name": "SPHARX Inc.",
        "email": "dev@spharx.cn"
    },
    "signature": "RSA-4096-BASE64..."
}
```

---

## 第4章 — 防破解与安全加固

### 4.1 破解路径分析与防御

| 破解方式 | 难度 | 防御措施 |
|---------|------|---------|
| 伪造 license.lic | 🔴 极高 | RSA-4096 离线签名，无私钥不可伪造 |
| 修改系统时间绕过试用期 | 🟡 中 | 记录首次运行时间到 `~/.memoryrovol/` 目录，检测时间倒流 |
| 反编译绕过门禁 | 🔴 极高 | OLLVM 控制流平坦化使反编译后逻辑面目全非 |
| 替换返回值 | 🟡 中 | `AGENTOS_ELICENSE` 不返回明文"ELICENSE"，与 ENOMEM/EINVAL 混合混淆 |
| 调试器动态修改内存 | 🟡 中 | 运行时校验 g_license 结构体 CRC，检测到篡改立即 abort |
| 提取公钥替换为自签名 | 🟡 高 | 公钥字节数组散落在多个 `.rodata` 段，通过 XOR 混淆后拼接 |
| 克隆已激活的 license.lic | 🟡 中 | License 中包含 `machine_id` 哈希（可选绑定机器） |

### 4.2 核心安全机制

```c
// 防篡改校验 — 每次关键操作前校验 g_license 完整性
static bool verify_license_integrity(void) {
    // CRC32 校验 g_license 结构体字段
    uint32_t crc = crc32_compute(&g_license, offsetof(license_state_t, crc_checksum));
    if (crc != g_license.crc_checksum) {
        // 检测到内存篡改 → 立即终止
        abort();
    }
    return true;
}

// 时间倒流检测
static bool detect_time_tampering(void) {
    const char* state_dir = getenv("MEMORYROVOL_STATE_DIR");
    if (!state_dir) state_dir = "~/.memoryrovol";
    
    char path[512];
    snprintf(path, sizeof(path), "%s/first_run", state_dir);
    
    FILE* f = fopen(path, "r");
    if (!f) {
        // 首次运行：记录时间
        f = fopen(path, "w");
        if (f) {
            fprintf(f, "%lu", (unsigned long)time(NULL));
            fclose(f);
        }
        return true;
    }
    
    unsigned long first_run;
    fscanf(f, "%lu", &first_run);
    fclose(f);
    
    // 如果系统时间比首次运行时间还早 → 时间倒流
    if ((unsigned long)time(NULL) < first_run - 86400) {
        return false;  // 检测到时间篡改
    }
    return true;
}
```

---

## 第5章 — AgentOS 集成架构（无源码依赖）

### 5.1 AgentOS 侧的集成方式

AgentOS 本身完全开源（Apache-2.0），通过 CMake 双模式构建接入 MemoryRovol。

**源码模式**（内部开发）：`add_subdirectory(memoryrovol)` → 从源码编译全功能
**预编译模式**（外部用户）：链接 `libmemoryrovol.a` + 加载 `license.lic`

```cmake
# agentos/atoms/CMakeLists.txt
option(MEMORYROVOL_SOURCE "Build MemoryRovol from source" ON)

if(MEMORYROVOL_SOURCE)
    # 源码模式：仅开发团队使用
    add_definitions(-DSPHARX_DEV_TEAM=1)
    add_subdirectory(memoryrovol)
else()
    # 预编译模式：外部用户使用
    # 用户需自行下载 libmemoryrovol.a + memoryrovol.h + 购买 license.lic
    find_library(MEMORYROVOL_LIB memoryrovol
        PATHS "${MEMORYROVOL_PATH}/lib"
        REQUIRED)
    
    add_library(agentos_memoryrovol STATIC IMPORTED)
    set_target_properties(agentos_memoryrovol PROPERTIES
        IMPORTED_LOCATION "${MEMORYROVOL_LIB}")
    
    target_include_directories(agentos_memoryrovol INTERFACE
        "${MEMORYROVOL_PATH}/include")
endif()
```

### 5.2 无源码情况下的降级机制

即使未加载 MemoryRovol（无 `.a` 文件或无 `license.lic`），AgentOS 不应崩溃：

```c
// engine.c — 降级 Fallback
agentos_error_t agentos_memory_create(..., out_engine) {
    agentos_memory_engine_t* engine = AGENTOS_CALLOC(1, sizeof(*engine));
    
    // 尝试加载 MemoryRovol
    engine->rov_handle = agentos_memoryrov_create();
    
    if (!engine->rov_handle) {
        // MemoryRovol 未安装或 License 无效
        // 降级到 L1+L2 Fallback 实现
        // （AgentOS 内置 L1+L2 简化版，仅用于基础兼容）
        AGENTOS_LOG_WARN("MemoryRovol not available, using fallback memory");
        return fallback_init(out_engine);  // L1+L2 基础功能
    }
    
    // MemoryRovol 正常加载 → 全功能
    *out_engine = engine;
    return AGENTOS_SUCCESS;
}
```

---

## 第6章 — 更新第09轮任务清单

### 任务拆分调整

| 编号 | 任务 | 工时 | 变更 |
|------|------|------|------|
| R-09-01-1 | CMake 双模式构建 | 6h | ✅ 保留 |
| **R-09-01-2** | **License 离线验证系统** | **12h** | ⬆️ 从8h→12h。新增：四级分层验证、CRC 防篡改、时间倒流检测 |
| **R-09-01-3** | **License 签发服务端** | **8h** | **新增**：RSA-4096 签名 API、试用版自动签发 |
| **R-09-01-4** | **预编译流水线** | **8h** | ⬆️ 从6h→8h。新增：OLLVM 混淆、字符串加密、多平台矩阵 |
| ~~R-09-01-4~~ | ~~社区版限速~~ | ~~8h~~ | ❌ **已废弃** — 不再开放源码 |

### 新增工程规范

```markdown
### BAN-25 — 禁止二进制中存在明文关键字符串
> 所有 License 相关字符串（"license.lic"、"AGENTOS_ELICENSE"、"SPHARX_DEV_TEAM" 等）
> 必须在编译时通过 XOR 加密或运行时动态拼接，禁止以明文形式出现在 `.rodata` 段。

### BAN-26 — 禁止 Trial 版绕过任何限制
> Trial 版禁止提供以下操作：
> - 任何 L3/L4 功能调用（即使降级返回空数据也不允许）
> - 超过 100 条记忆的写入
> - 超过 128 维向量的索引
> 违反即构成 BAN-26 违规。

### BAN-27 — License 状态必须全局可验证
> `g_license` 结构体必须：
> 1. 包含 CRC 校验字段
> 2. 在每个公共 API 入口调用 `verify_license_integrity()`
> 3. 检测到篡改时调用 `abort()` 而非静默降级

### REQ-16 — License 过期/缺失提示要求
> 当 License 过期或缺失时，必须：
> 1. 通过 `AGENTOS_LOG_WARN` 输出购买链接
> 2. 返回 `AGENTOS_ELICENSE` 错误码
> 3. 不泄露任何 License 验证内部逻辑细节
```

---

## 第7章 — 与 v11.9/v11.10 的关键差异对比

| 维度 | v11.9（原始） | v11.10（已废弃） | **v11.11（最终）** |
|------|-------------|----------------|-------------------|
| **源码分发** | 封闭 | ❌ 开放社区版 | **🔒 完全封闭** |
| **分发形式** | 预编译库 | 预编译库 + 源码 | **预编译库** |
| **Trial 版** | 无 | 全功能限速 | **极严试用（100条14天）** |
| **限速方式** | License 硬封禁 | 编译期限速 | **运行时 License 控制** |
| **L3/L4 试用** | 无 | 可用(限速) | **❌ 完全禁用** |
| **功能分层** | 2层(L1-L2/L3-L4) | 2层 | **4层(Trial/Pro/Enterprise/+)** |
| **防破解** | 基础 | 基础 | **强化（CRC/时间检测/OLLVM）** |
| **定价** | 未定义 | $299/$2,990 | **$299/$2,990/$15,000+** |
| **AgentOS 降级** | 未定义 | 基础 fallback | **明确 L1+L2 Fallback** |

---

## 第8章 — 执行路线图

| 阶段 | 时间 | 任务 | 交付物 |
|------|------|------|--------|
| **P0 构建系统** | 第1-2天 | CMake 双模式 + `SPHARX_DEV_TEAM` | `option(MEMORYROVOL_SOURCE)` |
| **P1 License 核心** | 第3-6天 | `license.c` 完整实现 | RSA-4096 + CRC + 时间检测 |
| **P2 门禁埋点** | 第7-9天 | L3/L4/容量/延迟 全部 12 个门禁 | 完整的门禁检查链 |
| **P3 预编译流水线** | 第10-12天 | CI + OLLVM + strip + 发布 | 全平台 `.a`/`.lib` |
| **P4 License 服务端** | 第13-14天 | 签发 API + 购买页面 | license.spharx.cn |
| **P5 AgentOS 集成测试** | 第15天 | 双模式端到端验证 | CI 绿色通过 |

---

<div align="center">

**© 2026 SPHARX Ltd. All Rights Reserved.**

*From data intelligence emerges*

</div>
