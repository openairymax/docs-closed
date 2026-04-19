# AgentOS 工程规范化标准手册 v13.0.0

> **版本**: 13.0.0-生产级标准全面规划版（含源码-产物分离规范BUILD-01~05）
> **日期**: 2026-04-19 16:35 (Out-of-Source Build验证通过后更新)
> **状态**: ⚠️ **生产级标准已建立** + **✅ Round 18-20架构重构完成** + **✅ Out-of-Source Build强制实施** + **✅ Include路径标准化完成**
> **核心理念**: 规范先行，质量为本！一切开发活动必须遵循本手册标准！
> **适用范围**: AgentOS项目所有开发人员、CI/CD系统、代码审查者
> **关联文档**: [主报告v23.1](./AgentOS全面修复与改进报告07.md) | [问题清单v14.0](./AgentOS详细问题清单07.md) | [看板v14.0](./AgentOS三团队任务进度看板07.md)

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
12. [🆕 源码-产物分离规范 (BUILD-01 ~ BUILD-05)](#12--源码-产物分离规范-build-01--build-05)
13. [附录](#13-附录)

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
```

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

## 📊 文档修订历史

| 版本 | 日期 | 作者 | 主要变更 |
|------|------|------|----------|
| v1.0 | 2026-04-15 | System | 初版创建 |
| v10.0 | 2026-04-17 | System | 加入CI/CD和安全规范 |
| v12.0 | 2026-04-19 09:00 | System | 全面生产级标准 |
| **v13.0** | 2026-04-19 16:35 | System | **🆕 新增Ch12源码-产物分离规范(BUILD-01~05)** |

---

**🎯 下一步行动**:
1. ✅ **将本文档分发给三团队所有成员**
2. 🚀 **TeamA/B/C Leader组织团队学习BUILD-01~05规范**
3. ⚠️ **Week 1 Day 1: 全员首次使用Out-of-Source Build验证环境**
4. 📝 **建立反馈机制**: 收集规范执行中的问题和改进建议

---

*规范手册结束。共13章，涵盖从代码风格到部署的全生命周期标准。*
