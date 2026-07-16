# 01 — agentrt-linux 代码真空审计报告

> **审计日期**：2026-07-16
> **审计方法**：Glob 全仓库递归扫描 .c / .h / .yaml / Makefile / Kconfig
> **结论**：**agentrt-linux 仓库包含 0 行可编译源码，8 子仓全部为 README-only 空壳。**

---

## 1. 审计范围

| 仓库 | 路径 |
|------|------|
| agentrt-linux 根目录 | `/home/spharx/SpharxWorks/airymaxhub/agentrt-linux/` |
| kernel 子仓 | `agentrt-linux/kernel/` |
| services 子仓 | `agentrt-linux/services/` |
| security 子仓 | `agentrt-linux/security/` |
| cognition 子仓 | `agentrt-linux/cognition/` |
| memory 子仓 | `agentrt-linux/memory/` |
| system 子仓 | `agentrt-linux/system/` |
| cloudnative 子仓 | `agentrt-linux/cloudnative/` |
| tests-linux 子仓 | `agentrt-linux/tests-linux/` |

---

## 2. 文件统计

### 2.1 按文件类型

| 文件类型 | 数量 | 代表性文件 |
|---------|------|-----------|
| .md 文档 | 128+ | 8 子仓 README.md + .github README.md + 根目录文档 |
| .yaml 配置 | 1 | ssot-registry.yaml |
| .yml CI | 6 | ci-kernel.yml, sc-dual-ci.yml, ssot-validate.yml 等 |
| .c 源文件 | **0** | — |
| .h 头文件 | **0** | — |
| Makefile | 1 | 仅根目录空 Makefile |
| Kconfig | **0** | — |
| Kbuild | **0** | — |

### 2.2 按子仓

| 子仓 | README.md | README_zh.md | .github/README.md | .c/.h | 实际功能 |
|------|-----------|-------------|-------------------|-------|---------|
| kernel | 有 | 有 | 有 | **0** | 空壳 |
| services | 有 | 有 | 有 | **0** | 空壳 |
| security | 有 | 有 | 有 | **0** | 空壳 |
| cognition | 有 | 有 | 有 | **0** | 空壳 |
| memory | 有 | 有 | 有 | **0** | 空壳 |
| system | 有 | 有 | 有 | **0** | 空壳 |
| cloudnative | 有 | 有 | 有 | **0** | 空壳 |
| tests-linux | 有 | 有 | 有 | **0** | 空壳 |

---

## 3. 对比：agentrt 仓库（对照）

| 文件类型 | agentrt | agentrt-linux |
|---------|---------|---------------|
| .c 源文件 | 200+ | **0** |
| .h 头文件 | 200+ | **0** |
| 构建系统 | CMakeLists（可编译成功） | 仅 1 个空 Makefile |
| [SC] 共享头文件 | commons/include/airymax/ (8 文件) | **0**（协议要求存在于 kernel/include/） |
| 测试 | 大量 test_*.c + benchmark_*.c | **0** |
| 可编译产物 | agentrt-all 构建成功 (d12 验证) | **不可编译** |

---

## 4. CI 无法运行分析

agentrt-linux 有 6 个 CI workflow 文件：

| Workflow | 设计意图 | 实际状态 |
|----------|---------|---------|
| ci-kernel.yml | 编译内核模块 + KUnit 测试 | **无法运行**（无 .c 文件） |
| sc-dual-ci.yml | 两端 [SC] 头文件逐字节对齐验证 | **无法验证**（agentrt-linux 端无头文件） |
| ssot-validate.yml | SSoT 注册表一致性检查 | **部分可运行**（仅 ssot-registry.yaml） |
| nightly.yml | 夜间构建和性能回归 | **无法运行**（无代码） |
| release.yml | 发布构建 | **无法运行**（无可交付物） |
| mgmt-orchestrator.yml | 管理编排 | **未知** |

---

## 5. 关键后果

### 5.1 docs/AirymaxOS 文档引用的代码全部不存在

以下文档引用了"源码地址"或"数据结构定义"，但对应的 .c/.h 文件全部缺失：

| 文档 | 引用的代码 | 存在？ |
|------|-----------|--------|
| 03-microkernel-strategy.md | kernel/ 子仓 IPC/capability/调度原语 | 否 |
| 03-capability-model.md | `struct airy_cnode`（完整 93 字节定义） | 否 |
| 07-ipc-fastpath.md | 8 状态 × 4 操作码快速路径 C 实现 | 否 |
| 01-syscalls.md | syscall 注册表 C 实现 | 否 |
| 02-services.md | 12 daemon C 实现 | 否 |
| 20-modules/*.md | 全部 8 子仓源码 | 否 |

### 5.2 [SC] 共享契约层物理缺失

IRON-9 v2 规定 [SC] 共享头文件的物理宿主为 `agentrt-linux/kernel/include/airymax/`，由 agentrt 通过 `-I` 路径引用。当前：

- agentrt 端有 8 个 [SC] 头文件（`commons/include/airymax/`）
- agentrt-linux 端有 **0** 个（`kernel/include/airymax/` 目录不存在）

这意味着 [SC] 共享契约的"逐字节相同"验证**无从进行**——只有一端有文件，diff 没有意义。

### 5.3 无法进行任何内核态测试

Linux 内核开发的起点是"一个可以 insmod 的 .ko 模块"。从 0 到 1 的内核模块开发需要：

1. 1 个 .c 文件（最少 `module_init()` + `module_exit()`）
2. 1 个 Makefile（`obj-m` 定义）
3. 1 个 Kconfig 条目（如果需要配置选项）

agentrt-linux 三项全部缺失，无法进行任何一个内核态开发流程的最小闭环。

---

## 6. 建议

1. **立即创建 kernel/ 子仓的第一个 .c 文件**：哪怕只是一个空壳内核模块（`airy_core.c`，包含 `module_init`/`module_exit` 和 `MODULE_LICENSE`）
2. **创建 kernel/ 子仓的 Makefile + Kconfig**：使其可被 `make M=agentrt-linux/kernel modules` 编译
3. **在 CI (ci-kernel.yml) 中验证**：`make modules` 成功 + `insmod airy_core.ko` 成功
4. **创建 kernel/include/airymax/ 目录**：作为 [SC] 共享头文件的物理宿主

只有完成了第 1 步，"0 行源码"才能变成"1 行源码"——这是从文档体系到工程体系的第一个质变点。
