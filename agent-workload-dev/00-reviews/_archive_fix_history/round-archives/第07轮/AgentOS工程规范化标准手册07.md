# AgentOS 工程规范化标准手册 v13.4.0

> **版本**: 13.4.0-技术改进策略增强集成版（含**技术改进策略v2.0全面融入**+源码-产物分离规范BUILD-01~06+Git子模块管理+Desktop/Docs模块路径确认+BUILD-006违规案例强化+**🆕 基于技术改进策略的架构标准化扩展**+**🆕 P0级改进方案详细代码示例与验证标准(守护进程并发/MCP协议栈/API错误恢复)**）
> **日期**: 2026-04-21 17:15 (**技术改进策略v2.0全面融入+P0级改进方案详细代码示例与验证标准**)
> **状态**: 🔴 **BUILD-006 In-Source Build严重复发(550+污染物)** + **✅ 生产级标准已建立** + **✅ Round 18-20架构重构完成** + **✅ Out-of-Source Build强制实施** + **✅ Include路径标准化完成** + **✅ 模块独立与子模块化完成** + **🆕 技术改进策略: 10大改进方案标准化扩展** + **🆕 P0级改进方案: 守护进程并发/MCP协议栈/API错误恢复详细代码示例与验证标准**
> **核心理念**: 规范先行，质量为本！一切开发活动必须遵循本手册标准！**🆕 技术改进策略=生产级落地指南！**
> **适用范围**: AgentOS项目所有开发人员、CI/CD系统、代码审查者
> **关联文档**: [主报告v25.3](./AgentOS全面修复与改进报告07.md) | [问题清单v16.4](./AgentOS详细问题清单07.md) | [看板v15.2](./AgentOS三团队任务进度看板07.md) | [**技术改进策略v2.0**](./技术借鉴与改进/第02版-AgentOS技术改进策略和详细方案.md)

---

## 📋 目录

1. [总则与核心理念](#1-总则与核心理念)
2. [代码风格规范 (CODE-01 ~ CODE-10)](#2-代码风格规范)
3. [CMake构建规范 (CMAKE-01 ~ CMAKE-08)](#3-cmake构建规范)
4. [Git工作流规范 (GIT-01 ~ GIT-06)](#4-git工作流规范)
5. [安全编码规范 (SEC-01 ~ SEC-10)](#5-安全编码规范)
6. [测试规范 (TEST-01 ~ TEST-06)](#6-测试规范)
7. [文档规范 (DOC-01 ~ DOC-05)](#7-文档规范)
8. [API设计规范 (API-01 ~ API-05)](#8-api设计规范)
9. [错误处理规范 (ERR-01 ~ ERR-04)](#9-错误处理规范)
10. [性能优化规范 (PERF-01 ~ PERF-04)](#10-性能优化规范)
11. [部署规范 (DEPLOY-01 ~ DEPLOY-03)](#11-部署规范)
12. [🆕 源码-产物分离规范 (BUILD-01 ~ BUILD-06)](#12--源码-产物分离规范-build-01--build-06)
13. [附录](#13-附录)
14. [双思维系统三组件架构规范 🆕](#14-双思维系统三组件架构规范-)
15. [基于技术改进策略的架构标准化扩展 🆕](#15-基于技术改进策略的架构标准化扩展-)
   - 15.7 [**🆕 关键实现代码示例与验证标准**](#关键实现代码示例与验证标准)

---

## 1. 总则与核心理念

### 1.1 项目愿景

AgentOS致力于成为**行业基础设施水平**的AI Agent操作系统，对标Linux/PostgreSQL等开源项目的工程质量。

**核心目标**: 
- 🎯 编译100%通过，0 error, 0 warning
- 🎯 测试覆盖率≥80% (单元+集成+端到端)
- 🎯 安全评级≥8/10 (渗透测试通过)
- 🎯 性能达标 (启动<2s, 延迟<10ms, 并发1000+)
- 🎯 文档完整性≥95% (API文档+架构文档+运维手册)

### 1.2 核心原则

#### 🔴 P0: 绝对流于形式！

```
❌ 禁止:
- 使用桩函数(stub)代替真实实现
- 返回硬编码值或空操作
- TODO/FIXME注释后不跟进
- 复制粘贴代码不做适配

✅ 要求:
- 每个函数必须有完整的业务逻辑
- 所有边界条件必须处理
- 错误路径必须有明确的恢复策略
- 代码必须可测试、可维护、可扩展
```

#### 🟠 P1: 一切以成功编译、成功运行为最高目标！

```bash
# 开发流程必须遵循:
1. 写代码 → 2. 本地编译(L1) → 3. 静态分析(L2) → 
4. 单元测试(L3) → 5. 提交PR → 6. CI验证 → 7. Code Review → 8. Merge
```

#### 🟡 P2: 安全第一，零信任架构

- 所有外部输入必须验证和消毒
- 加密通信是默认选项，明文需要特殊审批
- 最小权限原则：每个组件只拥有必要的权限

#### 🟢 P3: 文档即代码，代码即文档

- API变更必须同步更新文档
- 架构决策必须记录在ADR (Architecture Decision Record) 中
- Commit message必须清晰描述变更内容

### 1.3 质量门禁 (Quality Gates)

| 阶段 | 通过标准 | 阻断标准 |
|------|----------|----------|
| **L1: 本地编译** | 0 error, <10 warning | ≥1 error 或 ≥50 warning |
| **L2: 静态分析** | 0 critical, 0 error | ≥1 critical |
| **L3: 单元测试** | 覆盖率≥80%, 100% pass | 覆盖率<60% 或 有失败用例 |
| **L4: 集成测试** | 所有关键场景通过 | 核心场景失败 |
| **L5: Code Review** | ≥1 approve, 0 request-change | 有request-change未解决 |
| **L6: 安全扫描** | 0 high/medium vulnerability | ≥1 high |

---

## 2. 代码风格规范 (CODE-01 ~ CODE-10)

### CODE-01: 文件命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| C源文件 | `module_name.c` | `agentos_core.c`, `memory_manager.c` |
| 头文件 | `module_name.h` | `agentos_core.h`, `protocol_router.h` |
| CMakeLists.txt | `CMakeLists.txt` | (固定名称) |
| 测试文件 | `test_module_name.c` | `test_memory_manager.c` |
| 配置文件 | `config_*.h` | `config_agentos.h` |

### CODE-02: 函数命名规范

```c
// ✅ 正确: 动词_名词格式，清晰表达意图
int agentos_init(agentos_config_t* config);
bool memory_allocate(size_t size, void** ptr);
error_t protocol_send_message(const message_t* msg);

// ❌ 错误: 缩写或模糊命名
int init(void* c);
void* alloc(size_t s);
int send(const void* m);
```

### CODE-03: 变量命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 局部变量 | `snake_case` | `int buffer_size;` |
| 全局变量 | `g_module_prefix_` | `g_agentos_config_;` |
| 静态变量 | `s_prefix_` | `static int s_instance_count_;` |
| 常量 | `UPPER_SNAKE_CASE` | `#define MAX_CONNECTIONS 1024` |
| 枚举/结构体 | `PREFIX_Name_T` | `typedef enum { ... } agentos_error_t;` |
| 宏函数 | `PREFIX_FUNC_NAME()` | `#define LOG_ERROR(msg) ...` |

### CODE-04: 注释规范

```c
/**
 * @brief 简短描述函数功能（一行）
 *
 * @详细描述函数的完整行为、算法逻辑、注意事项等。
 * 可以多行，详细说明输入输出的语义和约束条件。
 *
 * @param param1 参数1的说明
 * @param param2 参数2的说明
 * @return 返回值的说明（成功返回什么，失败返回什么）
 *
 * @note 注意事项（可选）
 * @warning 警告信息（如有）
 * @see 相关函数（可选）
 *
 * @code
 * // 使用示例（可选）
 * agentos_config_t config = { .log_level = LOG_INFO };
 * int ret = agentos_init(&config);
 * @endcode
 */
int example_function(int param1, const char* param2);

// 行内注释: 解释"为什么"，而不是"是什么"
int timeout = 5000;  // 5秒超时，基于网络延迟基准测试(2026-04-15)
                   // NOT: 超时时间
```

### CODE-05: 错误处理规范

```c
// ✅ 正确: 显式检查所有可能的错误
int ret = function_call();
if (ret != SUCCESS) {
    LOG_ERROR("Function failed with error code: %d", ret);
    return ret;  // 向上传播错误，不要吞掉
}

// ✅ 正确: 使用goto进行资源清理（Linux内核风格）
int complex_operation(void) {
    char* buffer = malloc(BUFFER_SIZE);
    if (!buffer) {
        return ERROR_OUT_OF_MEMORY;
    }
    
    FILE* file = fopen("data.txt", "r");
    if (!file) {
        free(buffer);  // 清理已分配的资源
        return ERROR_FILE_OPEN_FAILED;
    }
    
    // ... 业务逻辑 ...
    
cleanup:  // 统一清理标签
    if (file) fclose(file);
    free(buffer);
    return SUCCESS;
}

// ❌ 错误: 忽略返回值或使用assert
function_call();  // 未检查返回值
assert(ptr != NULL);  // 生产代码禁止使用assert
```

### CODE-06~CODE-10: 其他规范

(继承自v12.0，保持不变，包括：
- CODE-06: 内存管理规范 (禁止裸malloc/free)
- CODE-07: 并发编程规范 (锁的使用规则)
- CODE-08: 日志规范 (LOG_INFO/ERROR/WARN分级)
- CODE-09: 配置管理规范 (配置文件优先于硬编码)
- CODE-10: 兼容性规范 (POSIX/C99/C11标准))

---

## 3. CMake构建规范 (CMAKE-01 ~ CMAKE-08)

### CMAKE-01: Out-of-Source Build 强制要求 🔴🔴🔴

> **生效日期**: 2026-04-19 (Round 18-20架构重构后)
> **强制性**: 🔴 **必须遵守** - 所有构建操作必须在AgentOS-build/内执行
> **违规后果**: PR被拒绝，必须重新配置

#### 3.1.1 标准构建命令

```bash
# ✅ 正确的Out-of-Source Build方式
cmake -S /path/to/AgentOS \
     -B /path/to/AgentOS-build \
     -DBUILD_DAEMON=ON \
     -DBUILD_TESTS=ON \
     -DCMAKE_BUILD_TYPE=Release

cmake --build /path/to/AgentOS-build --config Release -j$(nproc)

# ❌ 禁止的In-Source Build方式
cd /path/to/AgentOS
cmake .                          # 严禁！会在源码目录生成构建产物
make                             # 严禁！
```

#### 3.1.2 CMakeLists.txt 输出路径配置

```cmake
# 所有模块必须使用 CMAKE_BINARY_DIR 作为输出根路径
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

# 禁止使用 CMAKE_SOURCE_DIR 或 CMAKE_CURRENT_SOURCE_DIR 作为输出路径
# ❌ 错误示例:
set(OUTPUT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/build)  # 严禁！
```

#### 3.1.3 多配置并行支持

```bash
# Debug配置 (用于开发调试)
cmake -S AgentOS -B AgentOS-build-debug -DCMAKE_BUILD_TYPE=Debug
cmake --build AgentOS-build-debug -j$(nprof)

# Release配置 (用于生产部署)
cmake -S AgentOS -B AgentOS-build-release -DCMAKE_BUILD_TYPE=Release
cmake --build AgentOS-build-release -j$(nprof)

# 两个配置互不干扰，可以同时存在！
```

---

### CMAKE-02: 目标定义规范

```cmake
# 库目标示例
add_library(agentos_common STATIC
    src/file1.c
    src/file2.c
)

target_include_directories(agentos_common PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/utils/include
    # ... 其他公共头文件路径
)

target_link_libraries(agentos_common PUBLIC
    pthread          # 系统库
    ${OPENSSL_LIBRARIES}  # 第三方库
)

# 可执行目标示例
add_executable(agentos-llm-d
    daemon/llm_d/main.c
    daemon/llm_d/handler.c
)

target_link_libraries(agentos-llm-d PRIVATE
    agentos_common      # 内部依赖
    agentos_protocols   # 内部依赖
)
```

---

### CMAKE-03~CMAKE-08: 其他构建规范

(继承自v12.0并增强，包括：
- CMAKE-03: 条件编译规范 (BUILD_DAEMON, BUILD_TESTS开关)
- CMAKE-04: 安装规则规范 (DESTINATION布局)
- CMAKE-05: 打包规范 (CPack配置)
- CMAKE-06: 测试集成规范 (CTest配置)
- CMAKE-07: 版本管理规范 (AGENTOS_VERSION_MAJOR/MINOR/PATCH)
- CMAKE-08: **全局Include路径规范** 🆕

#### CMAKE-08: 全局Include路径规范 🆕

> **来源**: Out-of-Source Build验证经验 (2026-04-19)
> **目的**: 解决跨模块头文件找不到的问题

```cmake
# 根CMakeLists.txt (必须在add_subdirectory之前)
include_directories(
    # commons基础路径 (所有模块都依赖commons)
    ${CMAKE_CURRENT_SOURCE_DIR}/agentos/commons
    
    # utils子目录 (compat文件所在)
    ${CMAKE_CURRENT_SOURCE_DIR}/agentos/commons/utils/include
    ${CMAKE_CURRENT_SOURCE_DIR}/agentos/commons/utils/memory/include
    ${CMAKE_CURRENT_SOURCE_DIR}/agentos/commons/utils/string/include
    ${CMAKE_CURRENT_SOURCE_DIR}/agentos/commons/utils/logging/include
    ${CMAKE_CURRENT_SOURCE_DIR}/agentos/commons/utils/error/include
    
    # 平台相关
    ${CMAKE_CURRENT_SOURCE_DIR}/agentos/commons/platform/include
    
    # atoms模块 (其他模块可能引用atoms的头文件)
    ${CMAKE_CURRENT_SOURCE_DIR}/agentos/atoms/corekern/include
    
    # protocols模块
    ${CMAKE_CURRENT_SOURCE_DIR}/agentos/protocols/include
    
    # daemon模块
    ${CMAKE_CURRENT_SOURCE_DIR}/agentos/daemon/common/include
    
    # gateway模块
    ${CMAKE_CURRENT_SOURCE_DIR}/agentos/gateway/src
)
```

**关键原则**:
1. **根目录统一配置**: 避免每个模块重复配置相同的路径
2. **PUBLIC + include_directories双重保障**: 即使某个模块忘记在target_include_directories中添加路径，全局include_directories也能兜底
3. **精确到子目录**: 只包含需要的子目录，避免污染命名空间

---

## 4. Git工作流规范 (GIT-01 ~ GIT-06)

### GIT-01: 分支策略

```
main (生产分支，受保护)
  ├── develop (开发分支)
  │   ├── feature/xxx (功能分支)
  │   ├── bugfix/xxx (修复分支)
  │   └── refactor/xxx (重构分支)
  └── release/x.x.x (发布分支)
```

### GIT-02: Commit Message规范

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type**: feat/fix/docs/refactor/test/style/chore/perf  
**Scope**: module-name (如: atoms/corekern, protocols/mcp)  
**Subject**: 50字符以内，祈使句，句号结尾  
**Body**: 详细说明what/why/how (可选)  
**Footer**: Closes #123, Reviewed-by: @name (可选)

**示例**:
```
feat(atoms): implement memory pool allocator for L1 cache layer

Add slab-based memory pool to optimize small object allocation.
This improves memory allocation performance by 40% for objects
smaller than 256 bytes.

- Implement slab_create(), slab_destroy(), slab_alloc(), slab_free()
- Add per-CPU cache to avoid lock contention
- Support automatic resize based on usage patterns

Performance benchmark results:
- Allocation latency: 120ns → 45ns (-62%)
- Memory fragmentation: 15% → 3% (-80%)

Closes #456
Reviewed-by: @team-a-leader
```

### GIT-03~GIT-06: 其他Git规范

(继承自v12.0，包括：
- GIT-03: .gitignore维护规范 (v9.0.0标准)
- GIT-04: PR/MR流程规范 (模板+checklist)
- GIT-05: Code Review规范 (至少1人approve)
- GIT-06: Tag发布规范 (语义化版本vX.Y.Z))

---

## 5. 安全编码规范 (SEC-01 ~ SEC-10)

### SEC-01: 输入验证

```c
// ✅ 正确: 验证所有外部输入
bool validate_config(const agentos_config_t* config) {
    if (!config) return false;
    if (config->max_connections <= 0 || config->max_connections > MAX_ALLOWED) {
        return false;
    }
    if (strlen(config->log_path) >= MAX_PATH_LEN) {
        return false;
    }
    return true;
}
```

### SEC-02~SEC-10: 其他安全规范

(继承自v12.0，包括：
- SEC-02: 内存安全 (缓冲区溢出防护)
- SEC-03: 加密通信 (TLS mandatory)
- SEC-04: 认证授权 (JWT/OAuth2)
- SEC-05: 日志脱敏 (密码/token不记录)
- SEC-06: 依赖安全 (定期更新第三方库)
- SEC-07: 错误信息泄露 (内部细节不暴露给用户)
- SEC-08: 资源限制 (DoS防护)
- SEC-09: 并发安全 (竞态条件)
- SEC-10: 审计日志 (关键操作留痕)

---

## 6. 测试规范 (TEST-01 ~ TEST-06)

### TEST-01: 单元测试规范

```c
// 文件: test_memory_pool.c
#include <ctest.h>
#include "memory_pool.h"

// 测试用例命名: test_<函数名>_<场景>
void test_slab_alloc_normal_case(void) {
    // Arrange: 准备测试环境
    slab_t* slab = slab_create(SLAB_SIZE_256, 0);
    ASSERT_NOT_NULL(slab);
    
    // Act: 执行被测操作
    void* ptr = slab_alloc(slab);
    
    // Assert: 验证结果
    ASSERT_NOT_NULL(ptr);
    ASSERT_EQ(slab->used_count, 1);
    
    // Cleanup: 释放资源
    slab_destroy(slab);
}
```

### TEST-02~TEST-06: 其他测试规范

(继承自v12.0并增强：
- TEST-02: 集成测试规范 (端到端场景)
- TEST-03: 性能测试规范 (benchmark对比)
- TEST-04: 模糊测试规范 (libfuzzer)
- TEST-05: 安全测试规范 (OWASP Top 10)
- TEST-06: **Build验证测试规范** 🆕)

#### TEST-06: Build验证测试规范 🆕

> **来源**: Out-of-Source Build验证经验
> **目的**: 确保每次提交都能成功Out-of-Source Build

```bash
#!/bin/bash
# scripts/verify_build.sh - Build验证脚本

set -e  # 遇错立即退出

echo "=== Step 1: 清理构建目录 ==="
rm -rf ../AgentOS-build/*
echo "✅ 清理完成"

echo "=== Step 2: 配置CMake ==="
cmake -S ../AgentOS -B ../AgentOS-build \
      -DBUILD_DAEMON=ON -DBUILD_TESTS=ON -DCMAKE_BUILD_TYPE=Release
echo "✅ CMake配置成功"

echo "=== Step 3: 编译 ===
cmake --build ../AgentOS-build --config Release -j$(nproc)
echo "✅ 编译成功"

echo "=== Step 4: 验证构建产物位置 ===
if [ ! -d "../AgentOS-build/agentos/lib" ]; then
    echo "❌ 错误: lib目录不存在"
    exit 1
fi
if [ ! -d "../AgentOS-build/agentos/bin" ]; then
    echo "❌ 错误: bin目录不存在"
    exit 1
fi
echo "✅ 构建产物位置正确"

echo "=== Step 5: 验证源码目录干净 ==="
ARTIFACT_COUNT=$(find ../AgentOS -name "*.o" -o -name "CMakeFiles" | wc -l)
if [ "$ARTIFACT_COUNT" -ne 0 ]; then
    echo "❌ 错误: 发现$ARTIFACT_COUNT个构建产物残留"
    find ../AgentOS -name "*.o" -o -name "CMakeFiles"
    exit 1
fi
echo "✅ 源码目录干净 (0个残留)"

echo ""
echo "========================================="
echo "🎉 Build验证全部通过!"
echo "========================================="
```

**CI集成**: 将此脚本加入CI流水线，每次PR自动运行

---

## 7~11. 其他规范章节

(继承自v12.0，保持不变，包括：
- 第7章: 文档规范 (DOC-01~DOC-05)
- 第8章: API设计规范 (API-01~API-05)
- 第9章: 错误处理规范 (ERR-01~ERR-04)
- 第10章: 性能优化规范 (PERF-01~PERF-04)
- 第11章: 部署规范 (DEPLOY-01~DEPLOY-03)

---

## 12. 🆕 源码-产物分离规范 (BUILD-01 ~ BUILD-05)

> **新增章节**: 2026-04-19 (Round 18-20架构重构 + Out-of-Source Build验证)
> **强制性**: 🔴 **所有团队成员必须严格遵守**
> **违规后果**: PR拒绝 + 团队通报

### BUILD-01: Out-of-Source Build 强制要求 🔴🔴🔴

#### 12.1.1 核心原则

```
┌─────────────────────────────────────────────────────┐
│                  AgentOS 项目布局                    │
│                                                     │
│  AgentOS/              AgentOS-build/                │
│  ├─ .gitignore         ├─ .gitignore               │
│  ├─ agentos/           ├─ CMakeCache.txt           │
│  │   ├─ atoms/         ├─ CMakeFiles/             │
│  │   ├─ commons/       ├─ agentos/lib/            │
│  │   ├─ protocols/     │   ├─ *.a                 │
│  │   ├─ daemon/        ├─ agentos/bin/            │
│  │   └─ gateway/       │   ├─ agentos-*           │
│  ├─ tests/            └─ compile_commands.json    │
│  └── scripts/                                          │
│                                                     │
│  ✅ 仅含人类编写代码    ✅ 仅含机器生成产物         │
│  ✅ Git版本控制         ❌ 不纳入Git追踪            │
└─────────────────────────────────────────────────────┘
```

#### 12.1.2 强制命令模板

```bash
# ===== 第一次构建 (初始化) =====
cd /home/spharx/SpharxWorks/OpenAirymax

# 配置 (指定源码和构建目录)
cmake -S AgentOS -B AgentOS-build \
      -DBUILD_DAEMON=ON \
      -DBUILD_TESTS=ON \
      -DCMAKE_BUILD_TYPE=Release

# 编译 (所有产物输出到AgentOS-build/)
cmake --build AgentOS-build --config Release -j$(nproc)

# ===== 后续增量构建 (修改代码后) =====
# 只需重新编译，不需要reconfigure (除非CMakeLists.txt改变)
cmake --build AgentOS-build --config Release -j$(nproc)

# ===== 切换配置 (Debug/Release) =====
# 创建新的构建目录
cmake -S AgentOS -B AgentOS-build-debug -DCMAKE_BUILD_TYPE=Debug
cmake --build AgentOS-build-debug -j$(nprof)

# ===== 完全清理 =====
rm -rf AgentOS-build/*
cmake -S AgentOS -B AgentOS-build  # 重新配置
```

#### 12.1.3 禁止事项清单

```bash
# ❌ 绝对禁止的操作:

# 1. In-Source Build
cd AgentOS && cmake .
cd AgentOS && make

# 2. 在源码目录生成任何构建产物
# (以下文件不应出现在AgentOS/内):
# - CMakeCache.txt
# - CMakeFiles/
# - Makefile (CMake生成的)
# - *.o, *.a, *.so
# - compile_commands.json

# 3. 手动修改AgentOS-build/内的文件
# (AgentOS-build/内的所有文件都是自动生成的，不应手动编辑)

# 4. 将AgentOS-build/加入Git追踪
git add AgentOS-build/  # ❌ 错误！

# 5. 在agentos/内创建build_*目录进行构建
cd agentos && mkdir build_main && cd build_main && cmake ..  # ❌ 严禁！
cd agentos && mkdir build_heapstore && cd build_heapstore && cmake ..  # ❌ 严禁！
```

#### 12.1.4 🚨 BUILD-006 真实违规案例 (2026-04-20)

> **事件**: 第7轮次Day 1中午,发现严重In-Source Build违规
> **影响**: 三团队被迫全面停工
> **教训**: 规范必须严格执行,不能仅停留在文档层面

**违规现场**:
```
AgentOS/agentos/build_main/        ← In-Source Build违规目录(14MB)
├── CMakeCache.txt                 ← 2026-04-20 12:32创建
├── 380个.o文件                    ← 目标文件
├── 20个.a静态库                   ← 库文件
├── 55个CMakeFiles目录             ← CMake中间文件
├── 55个Makefile                   ← CMake生成
└── compile_commands.json          ← 77KB

AgentOS/agentos/build_heapstore/   ← In-Source Build违规目录(13MB)
├── CMakeCache.txt                 ← 2026-04-20 11:57创建
├── 构建产物                       ← atoms/commons/cupolas/heapstore/protocols
└── lib/                           ← 静态库
```

**统计数据**:
- 总污染物: **550+个非预期构建产物**
- 总占用空间: **27MB+**
- 影响范围: **全团队停工**

**根因分析**:
1. 团队成员未阅读/理解BUILD-01 Out-of-Source Build规范
2. 习惯性地在源码目录内创建build_*/目录进行构建
3. 缺乏自动化检测机制

**纠正措施**:
```bash
# 立即清理
rm -rf agentos/build_main/
rm -rf agentos/build_heapstore/

# 正确做法 - 使用Out-of-Source Build
cd /home/spharx/SpharxWorks/OpenAirymax
cmake -S AgentOS -B AgentOS-build -DBUILD_DAEMON=ON
cmake --build AgentOS-build --config Release
```

**预防机制**:
- ✅ 添加.gitignore规则: `agentos/build_*/`
- ✅ CI检测脚本: `scripts/check_in_source_build.sh`
- ✅ 全员培训: 每日构建前确认使用AgentOS-build/目录

---

### BUILD-02: AgentOS-build/ 目录管理规范

#### 12.2.1 标准目录结构

```
AgentOS-build/                    # 独立构建输出目录（不纳入Git）
├── .gitignore                    # v1.0.0 - 完整排除规则
├── CMakeCache.txt                # CMake配置缓存
├── CMakeFiles/                   # CMake中间文件
│   ├── agentos_common.dir/       # 各目标的编译信息
│   ├── cupolas.dir/
│   └── ...
├── compile_commands.json         # IDE智能感知数据库
├── agentos/                      # 构建产物按模块组织
│   ├── lib/                     # 静态/动态库
│   │   ├── libagentos_common.a
│   │   ├── libcupolas.a
│   │   ├── libsvc_common.a
│   │   └── ...
│   └── bin/                     # 可执行文件
│       ├── agentos-llm-d
│       ├── agentos-tool-d
│       └── gateway_d
└── test_results/                 # 测试结果 (如果启用)
    └── *.xml
```

#### 12.2.2 .gitignore 配置 (v1.0.0)

```gitignore
# ============================================
# AgentOS Build Output Directory .gitignore
# Version: 1.0.0
# Last Updated: 2026-04-19
# Purpose: 排除所有CMake构建产物
# ============================================

# ----- CMake系统文件 -----
CMakeCache.txt
CMakeFiles/
cmake_install.cmake
CTestTestfile.cmake
CPackConfig.cmake
CPackSourceConfig.cmake
Makefile
*.cmake
CMakeScripts/

# ----- 编译中间文件 -----
*.o
*.obj
*.o.d
*.ii
*.suo
*.idb
*.pdb

# ----- 库文件 -----
*.a
*.so
*.so.*
*.dylib
*.dll
*.lib

# ----- 可执行文件 -----
agentos/daemon/*/agentos-*
agentos/daemon/gateway_d/gateway_d
*.exe
outapp

# ----- 库和二进制输出目录 -----
agentos/lib/
agentos/bin/

# ----- IDE文件 -----
compile_commands.json
.clangd
.idea/
.vscode/
*.swp
*.swo

# ----- 测试结果 -----
test_results/
Testing/
*.gcda
*.gcno
coverage.info

# ----- 日志和临时文件 -----
*.log
*.tmp
.DS_Store
Thumbs.db
```

#### 12.2.3 清理命令

```bash
# 快速清理 (保留CMakeCache.txt，加速后续构建)
cd AgentOS-build
find . -name "*.o" -delete
find . -name "CMakeFiles" -type d -exec rm -rf {} +
cmake --build . --target clean

# 完全清理 (删除所有内容，下次需重新configure)
cd ..
rm -rf AgentOS-build/*
cmake -S AgentOS -B AgentOS-build  # 重新配置
```

---

### BUILD-03: .gitignore 维护规范

#### 12.3.1 主仓库 .gitignore (v9.0.0 标准)

> **文件路径**: `/home/spharx/SpharxWorks/OpenAirymax/AgentOS/.gitignore`
> **规模**: 871行 / 23节分类

**关键规则节选**:
```gitignore
# ============================================
# Section 19: 外部构建目录隔离 (第104-106行)
# ============================================
AgentOS-build/

# ============================================
# Section 23: V9.0 强化防护 (第636-640行)
# ============================================
# 本地生成的分析报告
*检查报告*.md
*验证报告*.md
*分析报告*.md

# ============================================
# Section 21: 白名单例外 (第769-793行)
# ============================================
!tests/Makefile                              # Python测试框架
!scripts/deployment/docker/Makefile      # Docker工具
!Dockerfile*
!docker-compose*.yml                       # 容器化配置
!agentos/**/CMakeLists.txt                # 构建系统核心
!.gitignore                                  # 自身
```

#### 12.3.2 双保险机制

```
AgentOS/.gitignore          ← 排除 AgentOS-build/ 目录
        ↓
AgentOS-build/.gitignore   ← 排除所有构建产物
        ↓
Git追踪结果:              ← ✅ 完美
  - AgentOS/: 干净 (仅源码)
  - AgentOS-build/: 完全忽略
```

---

### BUILD-04: CI/CD 集成规范

#### 12.4.1 GitHub Actions 配置示例

```yaml
# .github/workflows/build.yml
name: AgentOS CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  BUILD_DIR: ${{ github.workspace }}/../AgentOS-build
  SOURCE_DIR: ${{ github.workspace }}/AgentOS

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        path: AgentOS
      
    - name: Configure CMake (Out-of-Source)
      run: |
        cmake -S AgentOS -B ${{ env.BUILD_DIR }} \
             -DBUILD_DAEMON=ON \
             -DBUILD_TESTS=ON \
             -DCMAKE_BUILD_TYPE=Release
    
    - name: Build
      run: |
        cmake --build ${{ env.BUILD_DIR }} --config Release -j$(nproc)
    
    - name: Run Tests
      working-directory: ${{ env.BUILD_DIR }}
      run: ctest --output-on-failure
    
    - name: Verify Build Artifacts
      run: |
        echo "=== Checking build output location ==="
        ls -lh ${{ env.BUILD_DIR }}/agentos/lib/*.a || echo "No .a files found"
        ls -lh ${{ env.BUILD_DIR }}/agentos/bin/* || echo "No binaries found"
        
        echo "=== Checking source directory cleanliness ==="
        ARTIFACTS=$(find AgentOS -name "*.o" -o -name "CMakeFiles" | wc -l)
        if [ "$ARTIFACTS" -gt 0 ]; then
          echo "❌ ERROR: Found $ARTIFACTS artifacts in source dir"
          find AgentOS -name "*.o" -o -name "CMakeFiles"
          exit 1
        fi
        echo "✅ Source directory is clean"
    
    - name: Upload Build Artifacts
      uses: actions/upload-artifact@v4
      with:
        name: build-output
        path: ${{ env.BUILD_DIR }}/agentos/
        retention-days: 7
```

#### 12.4.2 Docker容器化构建

```dockerfile
# docker/Dockerfile.build
FROM ubuntu:22.04 AS builder

RUN apt-get update && apt-get install -y \
    gcc g++ make cmake \
    libssl-dev libjson-c-dev

WORKDIR /build

# 复制源码
COPY AgentOS /source/AgentOS

# Out-of-Source Build
RUN cmake -S /source/AgentOS -B /build \
    -DBUILD_DAEMON=ON \
    -DCMAKE_BUILD_TYPE=Release && \
    cmake --build /build --config Release -j$(nprod)

# 生产镜像 (仅包含构建产物)
FROM ubuntu:22.22 AS runtime
RUN apt-get update && apt-get install -y \
    libssl3 ca-certificates

COPY --from=builder /build/agentos/ /opt/agentos/
ENV PATH="/opt/agentos/bin:${PATH}"

ENTRYPOINT ["agentos-daemon"]
```

---

### BUILD-05: 开发环境设置规范

#### 12.5.1 VSCode 配置

```jsonc
// .vscode/settings.json
{
  "cmake.buildDirectory": "${sourceDir}/../AgentOS-build",
  "cmake.configureArgs": [
    "-DBUILD_DAEMON=ON",
    "-DBUILD_TESTS=ON",
    "-DCMAKE_BUILD_TYPE=Release"
  ],
  "cmake.buildArgs": [
    "--config", "Release",
    "-j", "8"
  ],
  "C_Cpp.default.cStandard": "c11",
  "C_Cpp.default.cppStandard": "c++17"
}
```

#### 12.5.2 clangd 配置 (compile_commands.json)

```yaml
# .clangd
CompileFlags:
  Add:
    - "-I${workspaceFolder}/AgentOS/agentos/commons"
    - "-I${workspaceFolder}/AgentOS/agentos/atoms/corekern/include"
    - "-I${workspaceFolder}/AgentOS/agentos/protocols/include"
    - "-I${workspaceFolder}/AgentOS/agentos/daemon/common/include"
    - "-std=c11"
    -Wall
    -Wextra
    -Werror

CompilationDatabase: AgentOS-build/compile_commands.json
```

#### 12.5.3 JetBrains CLion/IDEA 配置

```
Settings → Build, Execution, Deployment → CMake:
  Build type: "Custom"
  Build directory: ../AgentOS-build
  CMake options: -DBUILD_DAEMON=ON -DBUILD_TESTS=ON
  Build output: ../AgentOS-build/agentos/bin/
```

---

### BUILD违规后果矩阵

| 违规等级 | 后果 | 示例 | 恢复措施 |
|----------|------|------|----------|
| **🔴 致命** | PR立即拒绝，必须修复 | In-Source Build | 重新配置至AgentOS-build/ |
| **🟠 严重** | 必须在合并前修复 | 源码目录有.o文件 | 清理并添加.gitignore规则 |
| **🟡 中等** | 应在下个Sprint修复 | IDE配置未指向AgentOS-build | 更新settings.json |
| **🟢 轻微** | 记录但不阻塞 | 文档中使用了旧路径 | 更新文档 |

---

### BUILD-06: Git子模块管理规范 🆕

> **建立时间**: 2026-04-19 (Round 18-20之后)
> **适用范围**: OpenAirymax主仓库及所有子模块
> **核心理念**: 模块独立开发，统一版本管理

#### 12.6.1 子模块架构

```
OpenAirymax/ (主仓库)
├── AgentOS/          (核心源码 - 独立Git仓库)
├── Desktop/          (桌面客户端 - Git子模块) 🆕
├── Docker/           (容器化部署 - Git子模块) 🆕
├── Docs/             (文档中心 - Git子模块) 🆕
├── Docs-closed/      (内部文档 - 主仓库管理)
└── .gitmodules       (子模块配置文件)
```

#### 12.6.2 子模块配置标准

**`.gitmodules` 文件格式**:
```ini
[submodule "Desktop"]
	path = Desktop
	url = git@atomgit.com:openairymax/desktop.git

[submodule "Docker"]
	path = Docker
	url = git@atomgit.com:openairymax/docker.git

[submodule "Docs"]
	path = Docs
	url = git@atomgit.com:openairymax/docs.git
```

#### 12.6.3 子模块操作规范

**初始化子模块** (首次克隆后):
```bash
cd OpenAirymax
git submodule update --init --recursive
# 或克隆时自动初始化:
git clone --recursive git@atomgit.com:openairymax/OpenAirymax.git
```

**更新子模块**:
```bash
# 更新所有子模块到最新版本
git submodule update --remote

# 更新指定子模块
cd Desktop
git pull origin main
cd ..
git add Desktop
git commit -m "update Desktop submodule to latest"
```

**在子模块中工作**:
```bash
cd Desktop
# 进行修改...
git commit -m "feature: new desktop functionality"
git push origin main

# 回到主仓库记录子模块变更
cd ..
git add Desktop
git commit -m "update Desktop to abc1234"
```

#### 12.6.4 路径迁移记录

| 模块 | 原路径 (已废弃) | 新路径 (当前) | 远程仓库 | 变更时间 |
|------|----------------|--------------|----------|----------|
| **Desktop** | `AgentOS/scripts/desktop-client` → `AgentOS/desktop` | `OpenAirymax/Desktop` | git@atomgit.com:openairymax/desktop.git | 2026-04-19 |
| **Docker** | `AgentOS/docker` | `OpenAirymax/Docker` | git@atomgit.com:openairymax/docker.git | 2026-04-19 |
| **Docs** | `AgentOS/docs` | `OpenAirymax/Docs` | git@atomgit.com:openairymax/docs.git | 2026-04-19 |

**⚠️ 重要提示**:
- 所有文档和代码中的旧路径引用必须更新为新路径
- TeamC负责Docker部署文档的路径更新
- 所有团队负责文档引用路径的更新
- 三个模块均已推送至远程仓库并可正常克隆

#### 12.6.5 子模块依赖关系

```
主仓库 (OpenAirymax)
    │
    ├── AgentOS (核心) ← 无依赖，被其他模块依赖
    │
    ├── Desktop (桌面客户端)
    │   └── 依赖: AgentOS库文件 + Docs/API文档
    │
    ├── Docker (容器化)
    │   └── 依赖: AgentOS构建产物 + Desktop可执行文件
    │
    └── Docs (文档)
        └── 依赖: 无 (独立维护)
```

#### 12.6.6 版本同步策略

| 场景 | 操作 | Commit Message格式 |
|------|------|-------------------|
| **发布主版本** | 更新所有子模块到稳定版 | `release: v1.0.0 sync submodules` |
| **功能开发** | 仅更新相关子模块 | `feat: update Desktop for new UI` |
| **Bug修复** | 修复特定子模块 | `fix: security patch in Docker` |
| **文档更新** | 更新Docs子模块 | `docs: API documentation update` |

**⚠️ 禁止事项**:
- ❌ 在主仓库中直接修改子模块文件（必须在子模块目录内操作）
- ❌ 提交子模块的未提交更改（必须先在子模块中commit）
- ❌ 忽略子模块更新（定期执行 `git submodule status` 检查）

---

## 13. 附录

### 附录A: 常用命令速查表

```bash
# === Out-of-Source Build 标准流程 ===

# 1. 配置
cmake -S AgentOS -B AgentOS-build \
      -DBUILD_DAEMON=ON \
      -DBUILD_TESTS=ON \
      -DCMAKE_BUILD_TYPE=Release

# 2. 编译
cmake --build AgentOS-build --config Release -j$(nproc)

# 3. 测试
cd AgentOS-build && ctest --output-on-failure

# 4. 安装 (可选)
cmake --install AgentOS-build --prefix /usr/local

# 5. 完全清理
rm -rf AgentOS-build/*
cmake -S AgentOS -B AgentOS-build

# === 验证命令 ===

# 检查Include路径残留
grep -r "#include <agentos/" --include="*.c" --include="*.h" AgentOS/
# 应返回: 0 matches

# 检查构建产物位置
ls AgentOS-build/agentos/lib/*.a
ls AgentOS-build/agentos/bin/*

# 检查源码目录干净
find AgentOS -name "*.o" -o -name "CMakeFiles"
# 应返回空

# 检查.gitignore是否生效
git check-ignore -v AgentOS-build/agentos/lib/test.a
# 应显示: .gitignore:... AgentOS-build/
```

### 附录B: 问题诊断FAQ

**Q1: 为什么我的修改没有触发重新编译？**
A: CMake会检测文件的时间戳。如果修改了头文件但没修改.c文件，可能不会触发重编译。解决方案: `touch` 对应的.c文件或执行 `cmake --build AgentOS-build/target_name`

**Q2: 如何切换Debug/Release模式？**
A: 创建不同的构建目录:
```bash
cmake -S AgentOS -B AgentOS-build-debug -DCMAKE_BUILD_TYPE=Debug
cmake --build AgentOS-build-debug -j$(nprof)
```

**Q3: compile_commands.json在哪里？**
A: 自动生成在 `AgentOS-build/compile_commands.json`
VSCode/clangd可以直接读取此文件提供智能感知

**Q4: 如何清理所有构建产物？**
A: 两步走:
```bash
rm -rf AgentOS-build/*                           # 删除构建目录内容
cmake -S AgentOS -B AgentOS-build -DBUILD_DAEMON=ON  # 重新配置
```

---

## 14. 双思维系统三组件架构规范 🆕

> **来源**: [第01版-AgentOS双思维模型详细落地方案](./技术借鉴与改进/第01版-AgentOS双思维模型详细落地方案.md)
> **适用模块**: atoms/coreloopthree (cognition子目录)
> **强制实施时间**: Week 2-4

### 14.1 架构设计原则

#### DS-PRIN-1: 三组件协同原则

**规则**: 所有双思考系统必须采用t2/t1-f/t1-p三组件架构，禁止使用旧的dual_model双组件架构。

```c
// ✅ 正确: 使用triple_coordinator
triple_coordinator_t* tc = triple_coordinator_create();
triple_coordinator_set_t2(tc, llm_model);
triple_coordinator_set_t1f(tc, fast_thinker);
triple_coordinator_set_t1p(tc, professional_thinker);
triple_coordinator_run(tc, input, &output);

// ❌ 错误: 使用旧的dual_model
dual_model_t* dm = dual_model_create();  // 已废弃
dual_model_run(dm, input, &output);      // 禁止使用
```

#### DS-PRIN-2: 流式处理原则

**规则**: t1-f必须以流式方式处理t2的token输出，不能等待完整响应。

```c
// ✅ 正确: 流式处理
while (t2_has_next_token(t2)) {
    token_t tok = t2_get_next_token(t2);
    semantic_unit_feed_token(detector, &tok);
    
    if (semantic_unit_is_complete(detector)) {
        // 立即处理完成的语义单元
        process_semantic_unit(semantic_unit_get_current(detector));
    }
}

// ❌ 错误: 批量处理
char* full_output = t2_generate_complete(t2, input);  // 禁止
t1_validate(t1, full_output);                           // 太晚了
```

#### DS-PRIN-3: MemoryRovol同步原则

**规则**: 每个语义单元处理后必须立即同步到MemoryRovol L1 Cache。

```c
// ✅ 正确: 实时同步
process_result_t result = process_semantic_unit(unit);
memoryrovol_write_l1(memory, &unit, &result);  // 立即写入

// ❌ 错误: 延迟同步
cache_results.push_back(result);               // 缓存到内存
// ... 很久之后 ...
memoryrovol_batch_write_l1(memory, cache_results);  // 禁止
```

### 14.2 API命名规范

#### DS-API-1: 语义单元检测API

| 函数名 | 用途 | 返回值 |
|--------|------|--------|
| `semantic_unit_init()` | 初始化检测器 | agentos_error_t |
| `semantic_unit_feed_token()` | 喂入token | agentos_error_t |
| `semantic_unit_is_complete()` | 检测是否完成 | bool |
| `semantic_unit_get_current()` | 获取当前单元 | semantic_unit_t* |
| `semantic_unit_destroy()` | 销毁检测器 | void |

**前缀规则**: 所有函数必须以`semantic_unit_`开头。

#### DS-API-2: 三组件协调API

| 函数名 | 用途 | 返回值 |
|--------|------|--------|
| `triple_coordinator_init()` | 初始化协调器 | agentos_error_t |
| `triple_coordinator_set_t2()` | 设置主思考器 | agentos_error_t |
| `triple_coordinator_set_t1f()` | 设置快思考器 | agentos_error_t |
| `triple_coordinator_set_t1p()` | 设置专业思考器 | agentos_error_t |
| `triple_coordinator_run()` | 运行协调流程 | agentos_error_t |
| `triple_coordinator_destroy()` | 销毁协调器 | void |

**前缀规则**: 所有函数必须以`triple_coordinator_`开头。

### 14.3 性能要求

#### DS-PERF-1: 延迟要求

| 组件 | 最大延迟 | 测试方法 |
|------|----------|----------|
| **t1-f边界检测** | <10ms per token | benchmark_latency |
| **首个语义单元** | <150ms from start | benchmark_first_unit |
| **t1-p仲裁决策** | <500ms per request | benchmark_arbitration |
| **MemoryRovol L1写入** | <1ms per unit | benchmark_l1_write |

**违规后果**: 超过延迟要求的实现必须优化或回退。

#### DS-PERF-2: 吞吐量要求

| 指标 | 最小值 | 目标值 |
|------|--------|--------|
| 语义单元检测吞吐 | >1000 units/s | >2000 units/s |
| 协调器整体吞吐 | >50 complete responses/min | >100/min |
| L1缓存读写QPS | >10000 ops/s | >50000 ops/s |

### 14.4 安全要求

#### DS-SEC-1: t1-f安全策略

**规则**: t1-f必须实现以下安全检查:

1. **注入检测**: 检测SQL注入、XSS、命令注入等攻击模式
2. **长度限制**: 单个语义单元最大长度 < 10KB
3. **格式验证**: JSON/XML/代码块格式合法性检查
4. **敏感词过滤**: 检测违禁词汇和敏感信息泄露

```c
// 安全检查示例
validation_result_t t1f_validate(semantic_unit_t* unit) {
    validation_result_t result = {0};
    
    // 1. 注入检测
    if (contains_injection_pattern(unit->content)) {
        result.is_valid = false;
        result.reason = "SECURITY: Injection pattern detected";
        return result;
    }
    
    // 2. 长度限制
    if (strlen(unit->content) > MAX_UNIT_SIZE) {
        result.is_valid = false;
        result.reason = "SIZE: Unit exceeds maximum length";
        return result;
    }
    
    // 3. 格式验证 (根据unit类型)
    if (!validate_format(unit)) {
        result.is_valid = false;
        result.reason = "FORMAT: Invalid format";
        return result;
    }
    
    result.is_valid = true;
    return result;
}
```

#### DS-SEC-2: t1-p仲裁协议

**规则**: t1-p仲裁必须遵循以下协议:

1. **请求格式**: 必须包含完整的语义单元+验证结果+上下文
2. **响应类型**: APPROVE / REJECT / MODIFY
3. **修改指令**: 如果是MODIFY，必须包含具体的修改建议
4. **日志记录**: 所有仲裁决策必须记录到审计日志

```c
typedef enum {
    ARBITRATION_APPROVE,   // 通过
    ARBITRATION_REJECT,    // 拒绝
    ARBITRATION_MODIFY     // 需要修改
} arbitration_decision_t;

typedef struct {
    semantic_unit_t* unit;           // 待仲裁的语义单元
    validation_result_t* t1f_result; // t1-f的验证结果
    memoryrovol_context_t* context;  // 从L1加载的上下文
} arbitration_request_t;

typedef struct {
    arbitration_decision_t decision; // 仲裁决定
    char* reason;                     // 决策原因
    char* modification;               // 修改建议(如果是MODIFY)
    uint64_t timestamp;              // 决策时间戳
} arbitration_response_t;
```

### 14.5 测试要求

#### DS-TEST-1: 单元测试覆盖率

| 模块 | 最低覆盖率 | 目标覆盖率 |
|------|-----------|-----------|
| semantic_unit.c | ≥90% | ≥95% |
| triple_coordinator.c | ≥85% | ≥90% |
| stream_validator.c | ≥80% | ≥85% |

**强制要求**: 所有新增代码必须有对应的单元测试。

#### DS-TEST-2: 集成测试场景

必须覆盖以下场景:

1. **正常流程**: t2→t1-f→t1-p→MemoryRovol 完整链路
2. **错误拦截**: t1-f检测到注入攻击并触发t1-p仲裁
3. **长对话**: >20轮对话的MemoryRovol L1/L2/L3分级存储
4. **并发压力**: 多个协调器实例同时运行
5. **错误恢复**: t2输出中断后的优雅降级

### 14.6 文档要求

#### DS-DOC-1: API文档

所有新增API必须包含Doxygen注释:

```c
/**
 * @brief 初始化语义单元检测器
 * 
 * 创建一个新的语义单元检测器实例。检测器会维护内部状态机
 * 用于识别token流中的语义单元边界。
 * 
 * @param[out] detector 指向待初始化的检测器指针
 * @return AGENTOS_SUCCESS 成功
 * @return AGENTOS_ENOMEM 内存分配失败
 * @return AGENTOS_EINVAL 参数无效
 * 
 * @note 检测器必须在使用后调用 semantic_unit_destroy() 销毁
 * @see semantic_unit_destroy()
 * @since v1.0.0 (双思维系统升级)
 * 
 * 示例用法:
 * @code
 * semantic_unit_detector_t detector;
 * agentos_error_t err = semantic_unit_init(&detector);
 * if (err == AGENTOS_SUCCESS) {
 *     // 使用检测器...
 *     semantic_unit_destroy(&detector);
 * }
 * @endcode
 */
agentos_error_t semantic_unit_init(semantic_unit_detector_t* detector);
```

#### DS-DOC-2: 设计文档

必须提供以下设计文档:

1. **架构图**: 三组件交互序列图(Mermaid/PlantUML)
2. **状态机图**: 语义单元检测状态转换图
3. **数据流图**: token流→语义单元→验证→仲裁→MemoryRovol
4. **性能基准**: 各组件延迟/吞吐量基线数据

---

## 15. 基于技术改进策略的架构标准化扩展 🆕

> **依据文档**: 《第02版-AgentOS技术改进策略和详细方案.md》（v2.0）
> **核心理念**: 将技术改进策略中的关键架构决策标准化，确保生产级落地的一致性和可维护性
> **适用阶段**: Phase 2-3 (核心能力深化、生态基础设施)
> **强制实施时间**: Week 3-4 (双思维系统落地后) + 后续轮次

### 15.1 MCP协议栈激活规范 (IMP-02)

#### ARCH-MCP-1: 协议栈分层架构标准

**标准要求**:
1. **协议适配层**: 必须实现MCP标准v1.0+，提供`mcp_adapter`模块
2. **消息转换层**: 统一消息格式转换，支持JSON-RPC over HTTP/WebSocket
3. **会话管理层**: 维护多客户端会话状态，支持并发连接

**API设计规范**:
```c
// mcp_adapter.h 核心API (示例)
agentos_error_t mcp_adapter_init(mcp_config_t* config);
agentos_error_t mcp_adapter_register_tool(const mcp_tool_t* tool);
agentos_error_t mcp_adapter_handle_request(const mcp_request_t* req, mcp_response_t* resp);
```

**测试要求**:
- 单元测试: 协议解析、错误处理、并发安全
- 集成测试: 与hermes-agent/openclaw等参考项目互操作
- 性能测试: 1000+并发连接，延迟<50ms

#### ARCH-MCP-2: 协议版本兼容性标准

**版本策略**:
- 主版本号变更: 破坏性变更，需迁移工具
- 次版本号变更: 功能增强，向后兼容
- 修订号变更: Bug修复，完全兼容

**兼容性矩阵**:
| AgentOS版本 | MCP标准版本 | 支持状态 |
|-------------|-------------|----------|
| v1.0.0+     | v1.0        | ✅ 完全支持 |
| v1.2.0+     | v1.1        | 🟡 部分支持 |
| v2.0.0+     | v2.0        | 🔴 规划中 |

### 15.2 UnifiedChannel统一通道层规范 (IMP-08)

#### ARCH-UCH-1: 通道抽象层标准

**架构原则**:
1. **统一接口**: 所有通信通道（HTTP、WebSocket、gRPC、IPC）实现统一抽象接口
2. **插件化扩展**: 支持动态加载通道实现插件
3. **负载均衡**: 内置多通道负载均衡和故障转移

**核心组件**:
```c
// unified_channel.h 核心抽象
typedef struct unified_channel_ops {
    agentos_error_t (*send)(unified_channel_t* ch, const void* data, size_t len);
    agentos_error_t (*recv)(unified_channel_t* ch, void* buffer, size_t* len);
    agentos_error_t (*connect)(unified_channel_t* ch, const char* endpoint);
    agentos_error_t (*disconnect)(unified_channel_t* ch);
} unified_channel_ops_t;
```

#### ARCH-UCH-2: 通道性能与安全标准

**性能指标**:
- 单通道吞吐量: ≥10,000 msg/sec
- 端到端延迟: ≤10ms (同进程), ≤100ms (跨网络)
- 连接建立时间: ≤500ms

**安全要求**:
- 必须支持TLS 1.3+加密
- 通道认证: OAuth2.0/JWT/API Key
- 访问控制: 基于角色的权限管理

### 15.3 PluginSDK插件框架规范 (IMP-10)

#### ARCH-PLG-1: 插件生命周期管理标准

**生命周期阶段**:
1. **发现**: 自动扫描插件目录，加载插件描述符
2. **加载**: 动态加载共享库，验证ABI兼容性
3. **初始化**: 调用插件初始化函数，注册功能
4. **运行**: 插件提供服务，处理请求
5. **卸载**: 优雅关闭，释放资源

**ABI兼容性标准**:
- 插件必须声明兼容的AgentOS版本范围
- 主程序向后兼容至少3个次版本
- 插件接口使用版本化命名空间

#### ARCH-PLG-2: 插件安全沙箱标准

**沙箱机制**:
1. **权限控制**: 插件必须声明所需权限（文件系统、网络、进程等）
2. **资源限制**: CPU、内存、线程数配额
3. **隔离执行**: 可选Docker容器/WASM沙箱隔离

**安全审查流程**:
- 所有插件必须通过静态代码分析
- 高风险插件需要人工安全审计
- 插件签名验证，防止篡改

### 15.4 守护进程并发升级规范 (IMP-01)

#### ARCH-DMN-1: 并发架构标准

**并发模型**:
- 主线程: 事件循环，I/O多路复用
- 工作线程池: CPU密集型任务
- 协程/纤程: 高并发I/O操作

**线程安全要求**:
- 全局状态必须使用互斥锁/读写锁保护
- 避免死锁: 使用锁层次结构或死锁检测
- 内存屏障: 多核处理器可见性保证

#### ARCH-DMN-2: 热升级标准

**零停机升级**:
1. **版本共存**: 新旧版本可并行运行
2. **连接迁移**: 客户端连接平滑迁移
3. **状态同步**: 运行时状态无损迁移

**回滚机制**:
- 自动健康检查，失败时自动回滚
- 版本标记，支持快速回退
- 配置兼容性验证

### 15.5 API错误恢复系统规范 (IMP-03)

#### ARCH-ERR-1: 错误分类与处理标准

**错误类别**:
- **可恢复错误**: 网络超时、临时资源不足 - 自动重试
- **不可恢复错误**: 配置错误、内存耗尽 - 优雅降级
- **致命错误**: 断言失败、内存损坏 - 立即终止

**恢复策略**:
- 指数退避重试（最大3次）
- 断路器模式（失败阈值50%）
- 降级服务（返回缓存/默认值）

#### ARCH-ERR-2: 错误传播与日志标准

**错误传播**:
- 使用错误码而非异常（C语言兼容）
- 错误链: 保留原始错误上下文
- 结构化错误信息: 错误码、描述、建议操作

**日志要求**:
- 错误日志必须包含请求ID、用户ID、时间戳
- 不同错误级别对应不同日志目标
- 生产环境错误日志聚合到集中式系统

### 15.6 实施时间线与依赖关系

| 规范编号 | 规范名称 | Phase | 依赖规范 | 实施团队 | 预计工时 |
|----------|----------|-------|----------|----------|----------|
| ARCH-MCP-1~2 | MCP协议栈激活规范 | Phase 2 | 双思维系统规范 | TeamB | 60h |
| ARCH-UCH-1~2 | UnifiedChannel统一通道层规范 | Phase 3 | MCP协议栈规范 | TeamB | 80h |
| ARCH-PLG-1~2 | PluginSDK插件框架规范 | Phase 3 | UnifiedChannel规范 | TeamC | 70h |
| ARCH-DMN-1~2 | 守护进程并发升级规范 | Phase 2 | 无 | TeamB | 40h |
| ARCH-ERR-1~2 | API错误恢复系统规范 | Phase 2 | 双思维系统规范 | TeamA | 30h |

**验收标准**:
- ✅ 规范文档完成并团队评审通过
- ✅ 参考实现完成并通过单元测试
- ✅ 集成到主代码库，通过CI/CD流水线
- ✅ 性能和安全指标达到标准要求

### 15.7 关键实现代码示例与验证标准 🆕

> **来源**: 技术改进策略v2.0（第5-7节）+ 参考项目(hermes-agent/openclaw)最佳实践
> **目标**: 为关键规范提供具体可落地的代码实现参考和量化验证方法
> **遵循原则**: CODE-01~CODE-10代码风格规范，API-01~API-05 API设计规范，ERR-01~ERR-04错误处理规范

#### 15.7.1 守护进程并发升级实现 (ARCH-DMN-1)

**问题**: 6个daemon的main循环为单线程同步accept-handle，并发处理能力<10 QPS

**解决方案**: 事件驱动+线程池混合模型 (hermes-agent架构)

**标准实现** (`agentos/daemon/common/daemon_event_loop.h`):

```c
// ==== CODE STYLE: CODE-03变量命名 + CODE-04注释规范 ====

/**
 * @brief 守护进程事件循环结构体
 * 
 * 实现非阻塞I/O多路复用+工作线程池混合模型，支持1000+并发连接。
 * 采用Linux epoll(推荐)/select/poll作为底层I/O多路复用机制。
 * 
 * @note 内存对齐优化，提高缓存局部性
 * @since v1.0.0 (守护进程并发升级)
 */
typedef struct daemon_event_loop {
    int epoll_fd;                       ///< epoll文件描述符 (Linux only)
    agentos_thread_pool_t* worker_pool; ///< 工作线程池 (CODE-07并发规范)
    int max_connections;                ///< 最大并发连接数
    int backlog_size;                   ///< listen() backlog大小
    agentos_atomic_int active_connections; ///< 活动连接原子计数器
} daemon_event_loop_t;

// ==== API DESIGN: API-01一致性 + API-02可发现性 ====

/**
 * @brief 创建守护进程事件循环
 * 
 * @param[in] max_connections 最大并发连接数 (建议: 1000)
 * @param[in] worker_threads 工作线程数 (建议: CPU核心数×2)
 * @param[out] out_loop 输出的事件循环指针
 * @return AGENTOS_SUCCESS 成功
 * @return AGENTOS_ENOMEM 内存分配失败
 * @return AGENTOS_EINVAL 参数无效
 * 
 * @see CODE-05错误处理规范
 */
AGENTOS_API agentos_error_t agentos_daemon_event_loop_create(
    int max_connections,
    int worker_threads,
    daemon_event_loop_t** out_loop);

/**
 * @brief 运行事件循环
 * 
 * @param[in] loop 事件循环实例
 * @param[in] server_fd 监听socket文件描述符
 * @return AGENTOS_SUCCESS 成功启动
 * @return AGENTOS_EPERM 权限不足
 * @return AGENTOS_ECONNREFUSED 连接拒绝
 */
AGENTOS_API agentos_error_t agentos_daemon_event_loop_run(
    daemon_event_loop_t* loop,
    int server_fd);
```

**验证标准** (PERF-01~PERF-04性能规范):
- ✅ **并发能力**: `ab -n 10000 -c 1000` 压测，QPS ≥ 1000 (原<10)
- ✅ **资源使用**: 内存占用 < 100MB (1000连接时)
- ✅ **稳定性**: 72小时连续运行，无内存泄漏 (valgrind验证)
- ✅ **错误恢复**: 连接异常断开恢复时间 < 100ms

#### 15.7.2 MCP协议栈激活实现 (ARCH-MCP-1)

**问题**: gateway_d中MCP/A2A/OpenAI协议栈受宏控制，默认未启用

**解决方案**: 协议路由器架构 (openclaw参考)

**协议路由器** (`agentos/daemon/gateway_d/src/protocol/protocol_router.h`):

```c
// ==== CODE STYLE: CODE-03枚举命名 + API-03一致性 ====

/**
 * @brief 协议路由器支持的协议类型
 * 
 * 遵循MCP v1.0标准，支持多协议并存和协议协商。
 */
typedef enum protocol_type {
    PROTOCOL_MCP = 0,     ///< MCP v1.0 (Model Context Protocol)
    PROTOCOL_A2A,         ///< A2A v0.3.0 (Agent-to-Agent)
    PROTOCOL_OPENAI,      ///< OpenAI API兼容模式
    PROTOCOL_CUSTOM       ///< 自定义协议扩展
} protocol_type_t;

/**
 * @brief 协议路由器结构体
 * 
 * 统一管理多协议适配器，提供协议自动协商和路由功能。
 * 遵循SEC-03加密通信规范，所有外部连接强制TLS。
 */
typedef struct protocol_router {
    mcp_server_t* mcp;           ///< MCP协议服务器实例
    a2a_handler_t* a2a;          ///< A2A协议处理器
    openai_compat_t* openai;     ///< OpenAI兼容层
    daemon_event_loop_t* event_loop; ///< 底层事件循环
    agentos_mutex_t lock;        ///< 线程安全锁 (SEC-09并发安全)
} protocol_router_t;

// ==== CMAKE CONFIG: CMAKE-03条件编译规范 ====

# CMake配置示例 (agentos/daemon/gateway_d/CMakeLists.txt)
option(AGENTOS_ENABLE_PROTOCOLS "Enable MCP/A2A/OpenAI protocol stack" ON)

if(AGENTOS_ENABLE_PROTOCOLS)
    # 编译定义
    target_compile_definitions(agentos_gateway_d 
        PRIVATE AGENTOS_HAS_PROTOCOLS=1)
    
    # 链接依赖
    target_link_libraries(agentos_gateway_d 
        PRIVATE agentos_protocols)
    
    # 源文件
    target_sources(agentos_gateway_d PRIVATE
        src/protocol/mcp_server.c
        src/protocol/mcp_transport_stdio.c
        src/protocol/mcp_transport_http.c
        src/protocol/a2a_handler.c
        src/protocol/openai_compat.c
        src/protocol/protocol_router.c
    )
endif()
```

**验证标准** (TEST-01~TEST-06测试规范):
- ✅ **协议兼容性**: 通过MCP官方兼容性测试套件所有用例
- ✅ **互操作性**: 与hermes-agent/openclaw等参考项目正常互操作
- ✅ **安全认证**: TLS 1.3强制启用，通信加密验证
- ✅ **性能指标**: 协议延迟 < 10ms (本地), < 100ms (远程)

#### 15.7.3 API错误恢复系统实现 (ARCH-ERR-1)

**问题**: llm_d仅简单重试，无结构化错误分类和恢复策略

**解决方案**: 借鉴hermes-agent error_classifier + 多凭证池

**错误分类枚举** (`agentos/daemon/llm_d/src/error_recovery.h`):

```c
// ==== ERROR HANDLING: ERR-01分类 + ERR-02恢复 ====

/**
 * @brief API失败恢复原因分类
 * 
 * 结构化错误分类，每个类别对应特定的恢复策略。
 * 遵循SEC-07错误信息泄露防护规范。
 */
typedef enum agentos_failover_reason {
    AGENTOS_FAILOVER_AUTH = 0,            ///< 401/403 认证失败
    AGENTOS_FAILOVER_BILLING,             ///< 402 额度不足
    AGENTOS_FAILOVER_RATE_LIMIT,          ///< 429 频率限制
    AGENTOS_FAILOVER_OVERLOADED,          ///< 503/529 服务过载
    AGENTOS_FAILOVER_CONTEXT_OVERFLOW,    ///< 上下文长度超过限制
    AGENTOS_FAILOVER_MODEL_NOT_FOUND,     ///< 404 模型不存在
    AGENTOS_FAILOVER_TIMEOUT,             ///< 请求超时
    AGENTOS_FAILOVER_NETWORK_ERROR,       ///< 网络错误
    AGENTOS_FAILOVER_UNKNOWN              ///< 未知错误
} agentos_failover_reason_t;

/**
 * @brief 错误恢复策略执行器
 * 
 * 根据错误原因执行相应的恢复策略：
 * 1. 指数退避重试 (ERR-02规范)
 * 2. 凭证自动切换
 * 3. 降级处理
 * 4. 告警上报
 */
typedef struct agentos_error_recovery {
    agentos_failover_reason_t last_reason; ///< 最后一次失败原因
    time_t last_failure_time;             ///< 最后一次失败时间
    int retry_count;                      ///< 重试次数 (ERR-02指数退避)
    agentos_credential_pool_t* cred_pool; ///< 多凭证池
} agentos_error_recovery_t;

/**
 * @brief 分类API错误
 * 
 * 根据HTTP状态码和错误响应体内容确定具体失败原因。
 * 
 * @param[in] http_status HTTP状态码
 * @param[in] error_body 错误响应体 (JSON格式)
 * @return 具体的失败原因
 * 
 * @note 遵循ERR-04错误传播规范，保留原始错误上下文
 */
AGENTOS_API agentos_failover_reason_t agentos_classify_api_error(
    int http_status,
    const char* error_body);
```

**验证标准** (ERR-03监控 + ERR-04日志):
- ✅ **恢复成功率**: 模拟各类API错误，恢复成功率 > 95%
- ✅ **凭证切换时间**: 自动切换凭证时间 < 100ms
- ✅ **降级可用性**: 主模型不可用时，降级服务可用性 > 99%
- ✅ **审计日志**: 所有错误恢复操作完整记录 (SEC-10审计日志)

**实施步骤**:
1. 实现`error_recovery.c/h` (错误分类与恢复策略)
2. 实现`credential_pool.c/h` (多凭证池管理)
3. 集成到`llm_d/main.c`主循环
4. 添加单元测试覆盖所有错误场景 (TEST-01规范)
5. 性能基准测试 (PERF-03规范)

---

## 📊 文档修订历史

| 版本 | 日期 | 作者 | 主要变更 |
|------|------|------|----------|
| v1.0 | 2026-04-15 | System | 初版创建 |
| v10.0 | 2026-04-17 | System | 加入CI/CD和安全规范 |
| v12.0 | 2026-04-19 09:00 | System | 全面生产级标准 |
| v13.0 | 2026-04-19 16:35 | System | 🆕 新增Ch12源码-产物分离规范(BUILD-01~05) |
| **v13.1** | 2026-04-20 09:00 | System | **🆕 BUILD-06子模块规范完善 + 路径迁移表增加远程仓库信息 + 第7轮次正式启动** |
| **v13.2** | 2026-04-20 15:30 | System | **🆕 BUILD-006问题发现并紧急修复，版本号更新至13.2.0** |
| **v13.3** | 2026-04-21 12:30 | System | **🆕 技术改进策略v2.0全面融入，新增第15章"基于技术改进策略的架构标准化扩展"** |
| **v13.4** | 2026-04-21 17:15 | System | **🆕 P0级改进方案详细代码示例与验证标准，新增第15.7章"关键实现代码示例与验证标准"，包含守护进程并发/MCP协议栈/API错误恢复的具体实现代码和量化验证指标** |

---

**🎯 下一步行动**:
1. ✅ **将本文档分发给三团队所有成员**
2. 🚀 **TeamA/B/C Leader组织团队学习BUILD-01~06规范**
3. ⚠️ **Week 1 Day 1: 全员首次使用Out-of-Source Build验证环境**
4. 📝 **建立反馈机制**: 收集规范执行中的问题和改进建议

---

*规范手册结束。共13章，涵盖从代码风格到部署的全生命周期标准。*
