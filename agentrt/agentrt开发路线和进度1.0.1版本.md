Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

<!-- SPDX-License-Identifier: AGPL-3.0-or-later OR Apache-2.0 -->
<!-- 保密级别：SPHARX Ltd 内部参考，闭源不公开 -->
<!-- 版本：1.0 | 日期：2026-07-15 -->

# AgentRT 开发路线和进度 1.0.1 版本

> **文档定位**：agentrt 1.0.1 版本开发路线图、发行评估、多仓集成方案与发布策略。
> **保密级别**：SPHARX Ltd 内部参考，**闭源不公开**。
> **适用版本**：AgentRT v0.1.1（奠基版本）→ v1.0.1（正式生产版本）
> **SPDX-License-Identifier**：AGPL-3.0-or-later OR Apache-2.0。

---

## 1. 执行摘要

### 1.1 版本定位

| 版本 | 定位 | 状态 | 评分 |
|------|------|------|------|
| v0.1.0 | 初始原型 | 已归档 | 65/C+ |
| **v0.1.1** | **唯一奠基版本**（奠基 + 38 仓拆分 + 生产就绪） | **进行中** | **~81/B**（v4.0+v5.0 修正后） |
| v1.0.1 | 正式生产版本（零例外 + 全部 BAN 规则 strict 模式） | 未启动 | — |

> **IRON-7 硬约束**：0.1.1 之后直接过渡到 1.0.1，**禁止 0.1.2/0.2.0/0.3.0/1.0.0** 任何中间过渡版本。

### 1.2 核心结论

> **agentrt 当前不具备直接发行 1.0.1 版本的条件。**
>
> 1.0.1 的前提是 0.1.1 奠基版本全面完成（149 项验收标准全部通过），当前 0.1.1 完成度约 70%，仍有 ~1,000h 工作量待完成。预估 1.0.1 开发可在 0.1.1 完成后启动，额外需要 ~800h 工作量。

### 1.3 当前项目水平评估

基于 v1.0→v4.0 四轮审查-修正循环和 v5.0 追加修复的综合评估：

| 维度 | 评分 | 说明 |
|------|------|------|
| 架构设计 | 85/B+ | 微内核+分层+SSoT 设计哲学清晰，CoreLoopThree/MemoryRovol/Cupolas 原创性强 |
| 工程实现 | 78/B- | 31.8 万行真实实现（非桩），但存在 335 处 return 1、83 个不规范头文件守卫 |
| 代码质量 | 80/B | 875 文件仅 1 TODO/0 FIXME/0 HACK，但 P0-2 源码工程标准 ~46h 改造未完成 |
| 跨平台兼容 | 85/B+ | Linux/macOS/Windows 三平台真实支持，C11 标准，GCC/Clang/MSVC 兼容 |
| 安全工程 | 82/B | 毒化 30+ 危险函数 + 4 重 sanitizer + cupolas 安全穹顶 + 安全编译选项 |
| 文档体系 | 76/B | 85 个开源文档 + 262KB 工程标准手册，但 SSoT 矛盾和 FAISS/HNSW 矛盾已修复 |
| 生态准备 | 45/D | 5 个 integrations + 3 个 standards，无第三方贡献者，CI/CD 薄弱 |
| 生产验证 | 0/F | 无任何生产部署案例 |
| **综合** | **~81/B** | **具备底座雏形，距离行业标准底座仍有显著差距** |

---

## 2. 1.0.1 发行评估

### 2.1 1.0.1 发行前置条件

| # | 前置条件 | 当前状态 | 阻塞项 |
|---|---------|---------|--------|
| 1 | 0.1.1 奠基版本全面完成 | ~70% | 见 §3.1 |
| 2 | 149 项验收标准全部通过 | ~105/149 | SP01-SP37 验收标准未启动 |
| 3 | 38 仓 git 拆分完成 | 未启动 | 5 处跨层编译耦合未解耦 |
| 4 | 生产就绪 6 项硬门禁通过 | 未启动 | CI/CD/SBOM/Soak/安全审计均未启动 |
| 5 | API 冻结（语义化版本） | 未达到 | 技术债未清零（cupolas 错误码/return 1/头文件守卫） |
| 6 | 性能基准建立 | 未启动 | 无公开 benchmark |
| 7 | 生产验证案例 | 无 | 无任何部署案例 |

### 2.2 1.0.1 发行判定

> **判定：1.0.1 当前不可发行。**
>
> 原因：
> 1. 0.1.1 奠基版本未完成（~70%），149 项验收标准仅 ~105 项通过
> 2. 38 仓拆分未执行，5 处跨层编译耦合阻碍拆分
> 3. 生产就绪 6 项硬门禁（CI/CD/SBOM/三平台打包/72h Soak/安全审计）均未启动
> 4. API 未冻结，存在已知技术债（cupolas 错误码碰撞已修复但 return 1/头文件守卫未清理）
> 5. 无性能基准和生产验证案例

### 2.3 1.0.1 与 0.1.1 的关系

| 维度 | 0.1.1（奠基版本） | 1.0.1（正式生产） |
|------|------------------|------------------|
| **目标** | 奠基 + 38 仓拆分 + 生产就绪 | 正式生产 + 零例外 |
| **BAN 规则** | 允许部分 P2 豁免 | **全部 strict 模式，零豁免** |
| **AirymaxOS** | 仅创建仓库占位 | **实际开发启动** |
| **taskflow pregel** | max_workers=1 串行降级 | **多 worker 启用** |
| **CCN>100 函数** | ≤5 | **≤2** |
| **CCN>50 函数** | ≤30 | **≤10** |
| **最高 CCN** | ≤100 | **≤50** |
| **API 稳定性** | 允许调整 | **冻结，语义化版本** |
| **Soak Test** | 72h（发布前） | **72h（每次发布）+ 7 天 canary** |

---

## 3. 0.1.1 当前进度与剩余工作

### 3.1 0.1.1 三大支柱完成度

| 支柱 | 工作项数 | 工时 | 完成度 | 剩余工时 |
|------|---------|------|--------|---------|
| 支柱 1：奠基（W01-W30） | 30 项 | ~1,620h | ~80% | ~324h |
| 支柱 2：38 仓拆分（SP01-SP31） | 31 项 | ~572h | ~5% | ~543h |
| 支柱 3：生产就绪（SP32-SP37） | 6 项 | ~240h | ~0% | ~240h |
| **合计** | **67 项** | **~2,432h** | **~57%** | **~1,107h** |

### 3.2 支柱 1 剩余工作（~324h）

| # | 工作项 | 工时 | 优先级 | 说明 |
|---|--------|------|--------|------|
| W-1 | 源码工程标准全量重构（P0-2） | ~46h | P0 | 833 文件 4 空格→Tab/typedef 清理/错误宏统一/装饰符移除 |
| W-2 | 5 处跨层编译耦合解耦 | ~80h | P0 | coreloopthree 反向编译 daemon 9 文件 + cupolas 源码 |
| W-3 | manager 子系统 3 阻塞项修复 | ~40h | P0 | sanitizer 硬引用 + 8 硬编码路径 + 无构建系统 |
| W-4 | cupolas dynamic_policy/zero_trust 实现 | ~30h | P1 | 当前仅头文件，未实现 |
| W-5 | memoryrovol 集成或占位规范化 | ~20h | P1 | 当前为空壳占位 |
| W-6 | CCN 长尾治理（426 函数 >15） | ~50h | P1 | 98 FAIL + 328 WARN |
| W-7 | 335 处 return 1 统一到错误码体系 | ~20h | P1 | 全仓库渐进式清理 |
| W-8 | 83 个不规范头文件守卫修复 | ~8h | P1 | 统一为 AIRY_RT_* 前缀 |
| W-9 | sync_compat.h include 顺序依赖修复 | ~5h | P1 | 消除 #ifndef AIRY_RT_PLATFORM_H 屏蔽问题 |
| W-10 | CTest 注册密度提升 | ~10h | P2 | 46 注册 vs 1537 测试函数 |
| W-11 | 日志系统完整度提升（62%→85%） | ~15h | P2 | LOG-21~25 待实现 |

### 3.3 支柱 2 剩余工作（~543h）

38 仓拆分方案（1 伞仓 + 5 管理仓 + 29 叶子仓 + 3 顶层仓）：

| 阶段 | 工作内容 | 工时 | 依赖 |
|------|---------|------|------|
| 阶段 0 | 改名（单仓内，已完成） | — | — |
| 阶段 1 | 立即可拆的 8 仓（6 SDK + ecosystem，零跨层耦合） | ~80h | 无 |
| 阶段 2 | 解耦 5 处跨层编译耦合 | ~200h | W-2 完成 |
| 阶段 3 | C 层拆分 + 伞仓组装 | ~263h | 阶段 2 完成 |

### 3.4 支柱 3 剩余工作（~240h）

| # | 工作项 | 工时 | 说明 |
|---|--------|------|------|
| SP-32 | CI/CD 全仓流水线 | ~60h | 跨平台 CI 矩阵（Linux/macOS/Windows × GCC/Clang/MSVC） |
| SP-33 | SBOM 生成（CycloneDX + cosign） | ~30h | 软件物料清单自动化 |
| SP-34 | 三平台二进制打包 | ~50h | ZIP/NSIS(TGZ/DEB for Unix, NSIS for Win) |
| SP-35 | 72h Soak Test | ~40h | 发布前 72 小时持续压力测试 |
| SP-36 | 安全审计 | ~40h | 第三方安全扫描 + 渗透测试 |
| SP-37 | 149 项验收标准全量通过 | ~20h | 验收标准 ACC-SP01~SP12 |

---

## 4. 多仓集成方案

### 4.1 38 仓结构

```
airymaxhub/                        # 1 伞仓（git superproject）
├── agentrt/                       # 管理仓 1（agentrt 核心运行时）
│   ├── atoms/                     # 叶子仓（微内核原语）
│   ├── commons/                   # 叶子仓（共享工具库）
│   ├── cupolas/                   # 叶子仓（安全穹顶）
│   ├── daemons/                   # 叶子仓（12 个 daemon 服务）
│   ├── gateway/                   # 叶子仓（API 网关）
│   ├── heapstore/                 # 叶子仓（堆存储）
│   └── protocols/                 # 叶子仓（协议实现）
├── agent-linux/                 # 管理仓 2（AirymaxOS，1.0.1 启动开发）
├── sdk/                           # 管理仓 3（SDK 包，6 语言）
│   ├── sdk-python/                # 叶子仓
│   ├── sdk-go/                    # 叶子仓
│   ├── sdk-rust/                  # 叶子仓
│   ├── sdk-typescript/            # 叶子仓
│   ├── sdk-java/                  # 叶子仓
│   └── sdk-cpp/                   # 叶子仓
├── ecosystem/                     # 管理仓 4（生态工具）
├── products/                      # 管理仓 5（产品定义）
├── docs/                          # 顶层仓 1（开源文档）
├── docs-closed/                   # 顶层仓 2（闭源文档）
└── devtools/                      # 顶层仓 3（开发工具）
```

### 4.2 Git Submodule 管理策略

```yaml
# .gitmodules 结构
[submodule "agentrt"]
    path = agentrt
    url = ../agentrt.git
    branch = main

# 管理仓内部用 submodule 管理叶子仓
# agentrt/.gitmodules
[submodule "atoms"]
    path = atoms
    url = ../agentrt-atoms.git
    branch = main
```

**关键规则**：
1. 伞仓只直接管理 5 个管理仓 + 3 个顶层仓
2. 管理仓管理各自的叶子仓
3. 所有 submodule 跟踪 `main` 分支
4. 使用 `git submodule update --remote --merge` 同步上游变更
5. 发布时使用 `git submodule update --init --recursive` 锁定特定 commit

### 4.3 跨仓依赖管理

```
依赖方向（单向向下）：
commons（叶子，无外部依赖）
  ↑
atoms（微内核原语，依赖 commons）
  ↑
cupolas / heapstore / protocols（中间层，依赖 commons + atoms）
  ↑
daemons / gateway（应用层，依赖所有底层）

SDK（独立，零 C 编译依赖，纯 HTTP 协议调用）
```

**集成验证**：
- **连接线测试**（12 条 C-L 连接线）：`devtools/tests/integration/c/`
- **协议测试**：跨仓 IPC 消息头逐字节一致性验证
- **构建测试**：每个叶子仓可独立 `cmake -B build && cmake --build build`

### 4.4 构建系统集成

```cmake
# 伞仓顶层 CMakeLists.txt
add_subdirectory(agentrt)        # 核心运行时
add_subdirectory(agent-linux)  # Linux 加速路径（可选）
add_subdirectory(sdk)            # SDK（纯 HTTP，不依赖 C）
add_subdirectory(ecosystem)      # 生态工具
add_subdirectory(products)       # 产品定义

# agentrt 管理仓 CMakeLists.txt
add_subdirectory(atoms)
add_subdirectory(commons)
add_subdirectory(cupolas)
add_subdirectory(daemons)
add_subdirectory(gateway)
add_subdirectory(heapstore)
add_subdirectory(protocols)

# 聚合目标
add_custom_target(agentrt-all
    DEPENDS atoms commons cupolas daemons gateway heapstore protocols
)
```

---

## 5. 发布方案

### 5.1 发布流水线

```
开发分支 (develop)
    ↓ [PR + CI 全量检查]
主分支 (main)
    ↓ [标签 v0.1.1-rc1]
RC 阶段
    ↓ [72h Soak Test + 安全审计]
正式标签 (v0.1.1)
    ↓ [SBOM 生成 + 三平台打包]
发布
    ↓ [GitHub Release + 文档发布]
公告
```

### 5.2 CI/CD 矩阵

| 平台 | 编译器 | 架构 | CI Job |
|------|--------|------|--------|
| Ubuntu 22.04 | GCC 12 | x86_64 | `linux-gcc-x64` |
| Ubuntu 22.04 | Clang 15 | x86_64 | `linux-clang-x64` |
| Ubuntu 22.04 | GCC 12 | aarch64 | `linux-gcc-arm64` |
| macOS 13 | Clang 15 | x86_64 | `macos-clang-x64` |
| macOS 14 | Clang 15 | arm64 | `macos-clang-arm64` |
| Windows Server 2022 | MSVC 19 | x86_64 | `windows-msvc-x64` |

**CI 检查项**：
1. 编译（`-Werror` + sanitizer：ASan/LSan/UBSan）
2. 静态分析（clang-tidy + cppcheck + lizard CCN）
3. 单元测试（ctest 全量，覆盖率 ≥85% 关键模块）
4. 集成测试（12 条 C-L 连接线）
5. BAN 规则扫描（361 项 + IRON 10 项）
6. SPDX 许可证扫描
7. 连接线验证 + 协议测试

### 5.3 SBOM 生成

```bash
# CycloneDX SBOM
cyclonedx-py --output-format json --output-file sbom.json

# cosign 签名
cosign sign-blob --key cosign.key sbom.json

# 附带到 Release
gh release create v0.1.1 sbom.json sbom.json.sig
```

### 5.4 三平台二进制打包

| 平台 | 格式 | 包名 |
|------|------|------|
| Linux x86_64 | .tar.gz + .deb | `agentrt-0.1.1-linux-x64.tar.gz` |
| Linux aarch64 | .tar.gz + .deb | `agentrt-0.1.1-linux-arm64.tar.gz` |
| macOS x86_64 | .tar.gz | `agentrt-0.1.1-macos-x64.tar.gz` |
| macOS arm64 | .tar.gz | `agentrt-0.1.1-macos-arm64.tar.gz` |
| Windows x86_64 | .zip + .exe (NSIS) | `agentrt-0.1.1-windows-x64.zip` |

### 5.5 72h Soak Test

```
阶段 1（0-24h）：基础负载
  - 12 个 daemon 全部启动
  - 持续发送 IPC 消息（1000 msg/s）
  - 内存泄漏检测（每 4h 采样）

阶段 2（24-48h）：峰值负载
  - 模拟 100 并发 Agent 会话
  - LLM 调用模拟（mock provider）
  - MemoryRovol 读写压力

阶段 3（48-72h）：异常恢复
  - 随机 kill daemon 进程
  - 网络分区模拟
  - 磁盘满模拟
  - 验证自动恢复能力
```

---

## 6. 1.0.1 开发路线图

### 6.1 1.0.1 新增工作项

| # | 工作项 | 工时 | 依赖 | 说明 |
|---|--------|------|------|------|
| R-1 | AirymaxOS（agent-linux）实际开发 | ~400h | 0.1.1 完成 | 8 子仓微内核设计 + openEuler 参考 |
| R-2 | taskflow pregel_engine 多 worker 启用 | ~40h | 0.1.1 完成 | 从 max_workers=1 升级为并行执行 |
| R-3 | API 冻结 + 语义化版本 | ~30h | W-1~W-11 完成 | 公开 ABI 锁定，不再允许破坏性变更 |
| R-4 | 性能基准建立 | ~80h | API 冻结 | 对标 langchain/autogen，公开 benchmark |
| R-5 | 生产验证试点 | ~100h | 性能基准 | 至少 1 个真实 Agent 团队场景部署 |
| R-6 | CI/CD 矩阵完善 | ~50h | SP-32 完成 | 跨平台 CI 矩阵 + 自动化回归 |
| R-7 | 生态扩展 | ~60h | API 冻结 | 第三方 Agent 提供商入驻 market_d |
| R-8 | 标准化推进 | ~40h | API 冻结 | MCP/A2A 标准推广 + ARE Standards 发布 |
| **合计** | | **~800h** | | |

### 6.2 时间线预估

```
0.1.1 完成预估（剩余 ~1,107h）
├── 支柱 1 剩余：~324h
├── 支柱 2 剩余：~543h
└── 支柱 3 剩余：~240h

1.0.1 开发预估（~800h）
├── R-1~R-3（基础）：~470h
├── R-4~R-5（验证）：~180h
└── R-6~R-8（生态）：~150h

总计：~1,907h
```

### 6.3 1.0.1 验收标准（新增）

| 编号 | 验收项 | 标准 |
|------|--------|------|
| ACC-1.0.1-01 | AirymaxOS 8 子仓 | 全部可独立编译 |
| ACC-1.0.1-02 | taskflow 多 worker | 并行执行性能 ≥ 2x 串行 |
| ACC-1.0.1-03 | API 冻结 | 公开 ABI 0 破坏性变更 |
| ACC-1.0.1-04 | 性能基准 | 公开 benchmark 报告 |
| ACC-1.0.1-05 | 生产验证 | ≥1 个真实部署案例 |
| ACC-1.0.1-06 | CCN>100 函数 | ≤2 |
| ACC-1.0.1-07 | CCN>50 函数 | ≤10 |
| ACC-1.0.1-08 | 最高 CCN | ≤50 |
| ACC-1.0.1-09 | BAN 规则 | 全部 strict 模式，零豁免 |
| ACC-1.0.1-10 | Soak Test | 72h + 7 天 canary |

---

## 7. v5.0 修复记录（2026-07-15）

本次审查修复中发现并修复的问题：

| # | 问题 | 级别 | 修复内容 |
|---|------|------|---------|
| F-1 | cupolas 错误码碰撞（-16~-20 与 POSIX 码） | P0 | 5 个值迁移至 -718~-726 cupolas 专属段 |
| F-2 | 错误码 SSoT 矛盾（9 文档） | P0 | 统一为 TERMINOLOGY.md 权威源 |
| F-3 | FAISS vs HNSW 矛盾（9+ 文档） | P0 | 统一为 HNSW（对齐 TERMINOLOGY.md） |
| F-4 | contracts 交叉引用全部断链 | P0 | 修复为 NN-前缀文件名 |
| F-5 | 三级路径断链（5 处） | P1 | 修复为二级路径 |
| F-6 | AgentRT-build PascalCase | P1 | 改为 agentrt-build |
| F-7 | Dockerfile 仓库地址大小写 | P1 | AgentRT → agentrt |
| F-8 | malloc/free 违规代码示例 | P1 | 替换为 AIRY_MALLOC/AIRY_FREE |
| F-9 | 章节编号重复（02-coreloopthree.md） | P1 | 重新编号 |
| F-10 | 工程标准手册内部矛盾 | P1 | 修复 airy_ 改名矛盾/BAN 编号冲突/ACC 数量/agentos 路径/Soak 时长 |
| F-11 | triple_coordinator.c.bak 残留 | P2 | 删除 |
| F-12 | doxygen-guide/algorithms 标题错误 | P2 | 修正 |

---

## 8. 行业标准底座条件评估

### 8.1 agentrt 成为行业标准底座的条件矩阵

| # | 条件 | 当前状态 | 差距 | 达成路径 |
|---|------|---------|------|---------|
| 1 | **架构成熟度** | 85/B+ | 微内核+分层+SSoT 设计清晰 | 0.1.1 完成后达标 |
| 2 | **API 稳定性** | 未冻结 | 技术债未清零 | 1.0.1 API 冻结 |
| 3 | **跨平台兼容** | 85/B+ | 三平台真实支持 | 已达标 |
| 4 | **安全工程** | 82/B | 毒化函数+sanitizer+cupolas | 0.1.1 完成后达标 |
| 5 | **性能基准** | 无 | 无公开 benchmark | 1.0.1 建立 |
| 6 | **生产验证** | 无 | 无部署案例 | 1.0.1 试点 |
| 7 | **生态规模** | 45/D | 5 integrations | 1.0.1 扩展 |
| 8 | **CI/CD** | 薄弱 | workflow 几乎为空 | 0.1.1 SP-32 |
| 9 | **文档体系** | 76/B | SSoT 矛盾已修复 | 0.1.1 完成后达标 |
| 10 | **标准化** | 内部规则 | BAN/IRON 未获行业认可 | 1.0.1 推进 MCP/A2A |

### 8.2 与成熟运行时对比

| 维度 | AgentRT v0.1.1 | JVM | containerd | 差距评估 |
|------|----------------|-----|------------|---------|
| 版本成熟度 | 0.1.1（奠基版） | 30+ 年 | 10+ 年 | **巨大** |
| 代码规模 | 31.8 万行 | ~100 万行 | ~15 万行 | 可接受 |
| 生态规模 | 5 integrations | 百万级 Maven | OCI 生态 | **巨大** |
| 生产验证 | 0 案例 | 海量 | 海量 | **缺失** |
| API 稳定性 | 未冻结 | JEP 流程 | OCI 标准 | **未达标** |
| 性能基准 | 无 | JIT 基准 | 容器密度基准 | **缺失** |
| 标准化 | 内部 BAN/IRON | JLS/JVMS | OCI/LSB | **未获认可** |

### 8.3 结论

> **agentrt 具备成为 AI Agent 运行时行业标准底座的"雏形"，但距离 JVM/containerd 级别的成熟度仍有显著差距。**
>
> **核心优势**：架构设计成熟（微内核+CoreLoopThree+MemoryRovol+Cupolas），31.8 万行真实实现，跨平台三平台支持，安全工程深度。
>
> **核心差距**：无生产验证、API 未冻结、无性能基准、生态规模小、CI/CD 薄弱。
>
> **达成路径**：0.1.1 完成（奠基+拆分+生产就绪）→ 1.0.1（API 冻结+性能基准+生产验证+生态扩展）→ 持续迭代（标准化推进+生态网络效应）。
>
> **定位类比**：在架构野心层面，"JVM for AI Agents, containerd for Agent containers" 的类比合理；在生态地位层面，agentrt 目前是"0.1 版本的底座候选"，而非"既成底座"。

---

## 9. v5.0 修正后评分轨迹

| 版本阶段 | 综合评分 | 级别 | 变化 | 主要原因 |
|---------|---------|------|------|---------|
| v1.0（初始审查） | 65 | C+ | — | 10 项 P0 + 14 项 P1 |
| v2.0（修正后） | 72 | B- | +7 | 9/10 P0 修正 |
| v2.1（五维度模型） | 49 | F | -23 | P0 修复率 0%（不同评分模型） |
| v3.0（修正后） | ~76 | B | +27 | 10 P0 清零，但引入副作用 |
| v4.0（复审） | 68 | C+ | -8 | v3.0 修正引入编译破坏性副作用 |
| v4.0（修正后） | ~80 | B | +12 | 编译破坏修复 + SSoT 收敛 |
| v4.0（补充修正后） | ~81 | B | +1 | cupolas 枚举完整同步 + types.h SSoT 修复 |
| **v5.0（本次修正后）** | **~83** | **B+** | **+2** | cupolas 安全码迁移 + 文档 SSoT 修复 + FAISS 统一 + 手册矛盾修复 |

---

> **文档结束**。agentrt 1.0.1 版本开发路线和进度评估完成。当前项目处于 0.1.1 奠基阶段（~70% 完成度），1.0.1 发行需在 0.1.1 全面完成后启动，预估额外 ~800h 工作量。
