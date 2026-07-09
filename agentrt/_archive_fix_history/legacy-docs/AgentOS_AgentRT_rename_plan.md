# AgentOS → AgentRT 系统性改名方案

> **归档标记**: 本文档已于 2026-07-01 归档至 `DocsClosed/修复工作历史档案/旧版文档/`。改名方案已执行完成（P0.1~P0.12 全部 ✅），详见 [0.1.1详细任务清单.md](../../0.1.1详细任务清单.md) Phase 0。归档原因为方案已落地，保留作为历史参考。

> **版本**: v1.0 | **日期**: 2026-06-17 | **状态**: 已归档（方案已执行完成）
>
> **对齐文档**: [0.1.1技术全面改进方案v2.6.md](0.1.1技术全面改进方案v2.6.md) §3.3 (改名影响完整分析)、§3.4 (独立子仓库处理策略)
> **决策依据**: 方案§2.1 决策一 — "外层 `AgentOS/` → `AgentRT`，内层 `agentos/` 不变"

---

## 第一章：核心命名规则

### 1.1 三层命名体系

| 层级 | 名称 | 示例 | 改否 |
|:----:|------|------|:---:|
| **L0: 项目名/产品品牌** | `AgentRT` | CMake `project(AgentRT)`、README 标题、"AgentRT CLI" | ✅ 已改 |
| **L1: 内层模块名/命名空间** | `agentos` | 目录 `agentos/`、宏 `AGENTOS_MALLOC`、前缀 `agentos_core_*` | ❌ 保留 |
| **L2: 旧称（历史上下文）** | `AgentOS` | 历史文档中的 "AgentOS (现 AgentRT)" | 仅历史引用 |

### 1.2 不可违背原则

1. **`agentos/` 目录名、`AGENTOS_*` 宏、`agentos_*` 函数前缀保持不变。** 这是 "AgentOS" 作为智能体原生操作系统品牌名的内层保留。
2. **所有 `#include` 路径指向 `agentos/` 的保持不变。** 因为路径反映的是文件系统结构，不是项目名。
3. **Docker 容器名、卷名、网络名等运维标识符 `agentos-*` 保持不变。** 运维连续性优先。
4. **Git 历史保护：目录移动必须用 `git mv`。** 确保 `git log --follow` 可追踪历史。

---

## 第二章：当前状态评估

### 2.1 已完成的项目

| 项目 | 状态 | 说明 |
|------|:---:|------|
| 外层目录名 | ✅ 已完成 | `AgentOS/` → `AgentRT/` (路径已改为 `AgentRT/`) |
| CMake 根项目名 | ✅ 已完成 | `project(AgentRT VERSION 0.1.0)` |
| `.gitignore` 头部注释 | ✅ 已完成 | "AgentRT .gitignore" |

### 2.2 仍需处理的项目（按优先级排序）

| 优先级 | 区域 | 范围 | 文件数 | 类型 |
|:------:|------|------|:------:|------|
| **P0** | CMake 安装/打包名 | `agentos/atoms/CMakeLists.txt` 等 | 3 行 | 构建系统 |
| **P0** | CI 工作流名称 | `.github/workflows/*.yml` | 约 4 | CI/CD |
| **P0** | 旧构建目录清理 | 工作区级别的 `AgentOS-*` 目录 | 2 个 | 目录清理 |
| **P1** | Python 包名 | `pyproject.toml` | 1 | SDK |
| **P1** | Rust SDK 包名 | `sdk/rust/Cargo.toml` | 1 | SDK |
| **P1** | Go SDK 模块名 | `sdk/go/go.mod` | 1 | SDK |
| **P1** | SDK 源代码字符串引用 | Rust/Go/Python 源文件注释、文档 | 80+ | SDK |
| **P2** | README 品牌名 | 所有 `README.md` 中 "AgentOS" | 80+ | 文档 |
| **P2** | C/H 源码注释/版权 | `agentos/` 内头文件版权声明 | 50+ | 注释 |
| **P3** | Python scripts 入口名 | `pyproject.toml` `[tool.poetry.scripts]` | 4 | SDK |
| **P3** | Docs/DocsClosed 子仓库 | 跨子仓库文档品牌引用 | 100+ | 文档 |

### 2.3 无需修改的部分

| 项目 | 原因 |
|------|------|
| `agentos/` 目录名 | 内层品牌名保留 |
| `AGENTOS_MALLOC`/`AGENTOS_FREE` 等宏 | 代码前缀命名空间 |
| `AGENTOS_E*` 错误码宏 | 错误码体系前缀 |
| `agentos_core_*` 函数前缀 | 与目录路径一致 |
| `#include "agentos/..."` 路径 | 反映文件系统结构 |
| Docker 容器名 `agentos-*` | 运维连续性 |
| API 路由 `/api/v1/agentos/` | 后端路由规则，与项目名无关 |

---

## 第三章：分步骤执行计划

### 步骤 1：清理旧构建目录

```bash
# 删除旧名称构建目录
rm -rf /home/spharx/SpharxWorks/AgentOS-build
rm -rf /home/spharx/SpharxWorks/AgentOS-rust-target

# 删除源码区内的本地缓存/构建产物
cd /home/spharx/SpharxWorks/OpenAirymax/AgentRT
rm -rf .pytest_cache .ruff_cache build ci-artifacts contracts logs output temp
```

### 步骤 2：CMake 构建系统改名

**文件**: `agentos/atoms/CMakeLists.txt`

| 位置 | 当前内容 | 修改为 |
|------|---------|--------|
| L89 | `write_basic_package_version_file("${CMAKE_CURRENT_BINARY_DIR}/AgentOSConfigVersion.cmake"` | `...AgentRTConfigVersion.cmake` |
| L93 | `configure_package_config_file(... "${CMAKE_CURRENT_BINARY_DIR}/AgentOSConfig.cmake"` | `...AgentRTConfig.cmake` |
| L94 | `DESTINATION lib/cmake/AgentOS` | `DESTINATION lib/cmake/AgentRT` |

### 步骤 3：CI 工作流改名

扫描 `.github/workflows/` 目录，将所有 `name: AgentOS CI` 改为 `name: AgentRT CI`，`group: agentos-ci-*` 改为 `group: agentrt-ci-*`。

### 步骤 4：Python 包名改名

**文件**: `pyproject.toml`

| 行 | 当前内容 | 修改为 |
|----|---------|--------|
| L2 | `name = "agentos"` | `name = "agentrt"` |
| L4 | `description = "AgentOS - 智能体操作系统核心引擎...` | `description = "AgentRT - Agent Runtime Platform"` |
| L5 | `authors = ["Spharx AgentOS Team"]` | `authors = ["Spharx AgentRT Team"]` |
| L9 | `repository = "https://gitee.com/spharx/agentos"` | `repository = "https://gitee.com/spharx/agentrt"` |
| L10 | `documentation = "https://docs.spharx.cn/agentos"` | `documentation = "https://docs.spharx.cn/agentrt"` |
| L106-109 | `agentos-init`, `agentos-docs` 等入口点 | 改为 `agentrt-init`, `agentrt-docs` 等 |

**注意**: `[tool.coverage.run] source = ["agentos"]` → 保留不变（反映源码目录名）。

### 步骤 5：Rust SDK 包名改名

**文件**: `sdk/rust/Cargo.toml`

| 行 | 当前内容 | 修改为 |
|----|---------|--------|
| L2 | `name = "agentos-rs"` | `name = "agentrt-rs"` |
| L5 | `description = "AgentOS Rust SDK - 与 Go SDK 保持一致的模块化结构"` | `description = "AgentRT Rust SDK"` |
| L6 | `homepage = "https://github.com/spharx/agentos"` | `homepage = "https://github.com/spharx/agentrt"` |
| L7 | `repository = "https://github.com/spharx/agentos"` | `repository = "https://github.com/spharx/agentrt"` |
| L9 | `authors = ["Spharx AgentOS Team"]` | `authors = ["Spharx AgentRT Team"]` |

Rust 源文件还需处理：

```bash
# 源文件注释/文档字符串替换（不改标识符）
sed -i 's/AgentOS Rust SDK/AgentRT Rust SDK/g' sdk/rust/src/*.rs
sed -i 's/AgentOS SDK/AgentRT SDK/g' sdk/rust/src/*.rs
# 注意: AgentOSError 等类型名保留不变（内层命名空间）
```

### 步骤 6：Go SDK 模块名改名

**文件**: `sdk/go/go.mod`

```diff
- module github.com/spharx/agentos/sdk/go
+ module github.com/spharx/agentrt/sdk/go
```

**文件**: `sdk/go/agentos/errors.go` 等

- 包目录名 `agentos/` → 根据情况决定是否改名（若包路径与命名相关则改，若仅反映目录结构则保留）
- 类型名 `AgentOSError` → 保留不变（内层代码前缀）

### 步骤 7：README 及文档品牌名批量替换

```bash
find agentos/ -name 'README.md' -exec sed -i 's/AgentOS/AgentRT/g' {} \;
```

仅替换标题级/品牌级引用，不替换代码示例中的 `agentos` 小写路径。

### 步骤 8：C/H 源文件注释/版权同步清理

```bash
# 版权声明
find agentos/ -name '*.c' -o -name '*.h' | xargs sed -i 's/Copyright.*AgentOS/Copyright 2026 SPHARX Ltd. AgentRT/g'
# 注释中的品牌引用
find agentos/ -name '*.c' -o -name '*.h' | xargs sed -i 's/\bAgentOS\b/AgentRT/g'
```

**注意**: 跳过包含 `AGENTOS_` 宏的行和包含 `agentos/` 路径的行（大小写敏感匹配）。

### 步骤 9：跨子仓库同步处理

| 子仓库 | 处理内容 | 预计工时 |
|--------|---------|:-------:|
| `Desktop/` | `tauri.conf.json` 的 `productName` 改为 "Airymax AgentRT"；TSX UI 文案改为 "AgentRT" | ~1h |
| `Docker/` | Grafana 仪表盘标题 "AgentOS" → "AgentRT"；Dockerfile COPY 路径更新 | ~0.5h |
| `Docs/` | 所有文档标题级 "AgentOS" → "AgentRT" | ~2h |
| `MemoryRovol/` | 日志前缀 `[AgentOS]` → `[AgentRT]`；CMake 注释 | ~0.5h |
| `DocsClosed/` | 与 Docs 同步：品牌引用 "AgentOS" → "AgentRT"（旧称保留说明） | ~0.5h |

### 步骤 10：验证编译（验收）

```bash
# C/C++ 编译验证
cmake -B build
cmake --build build

# Rust SDK 编译
cd sdk/rust && cargo build

# Go SDK 编译
cd sdk/go && go build ./...

# Python 包安装
pip install -e .
python -c "import agentrt"  # 验证新包名
```

---

## 第四章：验收标准（ACC-S06 细化）

| 编号 | 验收项 | 验证方式 |
|:----:|-------|---------|
| ACC-S06-01 | 外层 `AgentOS/` → `AgentRT/` 目录名已改 | `ls -d AgentRT*` |
| ACC-S06-02 | CMake `project(AgentRT)` 正确 | `grep 'project(AgentRT' CMakeLists.txt` |
| ACC-S06-03 | CI workflow 名称已更新 | `grep -r 'name:.*AgentRT' .github/` |
| ACC-S06-04 | CPack 包名已改 | `grep CPACK_PACKAGE_NAME CMakeLists.txt` |
| ACC-S06-05 | Python 包名 `agentrt` 可安装 | `pip show agentrt` |
| ACC-S06-06 | Rust SDK 包名 `agentrt-rs` | `cargo search agentrt-rs` |
| ACC-S06-07 | Go SDK 模块路径 `agentrt/sdk/go` | `grep 'module.*agentrt/sdk/go' sdk/go/go.mod` |
| ACC-S06-08 | 旧构建目录 `AgentOS-build`/`AgentOS-rust-target` 已删除 | `ls /home/spharx/SpharxWorks/AgentOS* 2>&1` 无结果 |
| ACC-S06-09 | 内层 `agentos/` 目录名保留不变 | `ls -d agentos/` 存在 |
| ACC-S06-10 | 代码标识符 `AGENTOS_*` 保留不变 | `grep -r 'AGENTOS_MALLOC\|AGENTOS_FREE' | wc -l` > 0 |

---

## 第五章：风险与回滚

### 5.1 风险清单

| 风险 | 影响 | 概率 | 缓解措施 |
|------|:----:|:----:|---------|
| CI 流水线中断 | 高 | 中 | 先验证 CI workflow 改名的正确性，快照备份原文件 |
| SDK 发布混乱 | 中 | 低 | npm/crates.io/pyPI 同时保留新旧两个包名，设置重定向 |
| Docker 运维中断 | 高 | 低 | 容器名不变，仅改 Grafana 显示名 |
| 跨子仓库不同步 | 中 | 中 | 按 §3.4.4 时序图执行，逐仓库验证 |

### 5.2 回滚策略

**步骤 1**: 已删除的目录在回收站有备份 → 恢复即可。
**步骤 2**: 已修改的 CMakeLists.txt → `git checkout -- <file>` 恢复。
**步骤 3**: SDK 包名回滚 → 回退 pyproject.toml/Cargo.toml/go.mod 的提交。
**步骤 4**: 全量验证 → `cmake --build build` 确认编译通过。

---

## 附录 A：扫描命令汇总

```bash
# 1. 查找所有包含 "AgentOS" 的文件（排除 .git 和二进制）
grep -r --include='*.c' --include='*.h' --include='*.py' --include='*.rs' --include='*.go' \
    --include='*.toml' --include='*.yaml' --include='*.yml' --include='*.md' \
    -l 'AgentOS' /home/spharx/SpharxWorks/OpenAirymax/AgentRT/ | grep -v '.git/'

# 2. 查找 CMake 文件中的 "AgentOS"（构建系统相关）
grep -r --include='CMakeLists.txt' --include='*.cmake' -n 'AgentOS' \
    /home/spharx/SpharxWorks/OpenAirymax/AgentRT/

# 3. 查找 SDK 包配置中的 "agentos"（小写，包名相关）
grep -r --include='Cargo.toml' --include='go.mod' --include='pyproject.toml' \
    --include='package.json' 'agentos' /home/spharx/SpharxWorks/OpenAirymax/AgentRT/
```