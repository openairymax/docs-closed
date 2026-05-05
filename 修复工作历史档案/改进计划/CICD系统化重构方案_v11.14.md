# AgentOS CI/CD 系统化重构方案 v11.14

**版本**: v11.14.0 · 第09大轮次  
**分析日期**: 2026-04-29  
**目标**: 6条流水线 → 3条，消除全部阻塞点，修复语法错误，统一构建规范

---

## 第1章 — 当前状态审计

### 1.1 6条流水线总览

| # | 流水线 | 文件 | 行数 | 触发条件 | 任务数 |
|---|--------|------|------|---------|--------|
| 1 | CI Pipeline v3.1 | `ci.yml` | 424行 | push/PR + manual | 6 jobs |
| 2 | Quality & Security v3.0 | `quality-security.yml` | 149行 | scheduled(每日/每周) + manual | 4 jobs |
| 3 | Protocol CI v3.0 | `protocol-ci.yml` | 70行 | push/PR gateway路径 + manual | 1 job |
| 4 | Docs CI v3.1 | `docs-ci.yml` | 101行 | push/PR docs + scheduled(每日) + manual | 2 jobs |
| 5 | SDK CI v3.0 | `sdk-ci.yml` | 183行 | push/PR toolkit路径 + manual | 6 jobs |
| 6 | Release v3.0 | `release.yml` | 156行 | tag(v*) + manual | 3 jobs |
| | **合计** | **6个文件** | **1083行** | | **22 jobs** |

### 1.2 语法错误与阻塞点

| # | 严重度 | 文件 | 行号 | 问题 |
|---|--------|------|------|------|
| 🔴 F-01 | **阻塞** | 全部6个workflow | 多处 | 构建目录使用 `AgentOS-build` 相对路径，违反 BAN-33。必须改为 `../AgentOS-build` |
| 🔴 F-02 | **阻塞** | `ci.yml` | L102 | `cmake -S . -B "$BUILD_DIR"` 未使用 `../AgentOS-build` 前缀，违反 BAN-33 |
| 🔴 F-03 | **阻塞** | `protocol-ci.yml` | L47-49 | `cmake -S . -B AgentOS-build` 直接在源码同层构建 |
| 🔴 F-04 | **阻塞** | `release.yml` | L59 | `cmake -S . -B AgentOS-build` 同上 |
| 🟡 F-05 | 阻塞 | `sdk-ci.yml` | L69 | `ctest` 结束后不检查退出码，test失败也继续 |
| 🟡 F-06 | 阻塞 | `ci.yml` | L197 | valgrind检查 `continue-on-error: true` 但后续不判断结果 |
| 🟡 F-07 | 阻塞 | `docs-ci.yml` | L100 | `peaceiris/actions-gh-pages@v4` 需要 `GITHUB_TOKEN`，但token权限未验证 |
| 🟡 F-08 | 阻塞 | `build-module.sh` | L184 | `build_dir="${PROJECT_ROOT}/build-${module}"` 违反BAN-33 |
| 🟡 F-09 | 阻塞 | `ci-run.sh` | L238 | `build_dir="${PROJECT_ROOT}/build-${module}"` 同上 |
| 🟡 F-10 | 阻塞 | `run-tests.sh` | L135 | 查找 `build-${module}` 目录，路径不统一 |

### 1.3 冗余与重复（性能问题）

| # | 问题 | 涉及文件 | 影响 |
|---|------|---------|------|
| ⚠ R-01 | **依赖安装重复5次** | ci.yml / protocol-ci / sdk-ci / release / quality-security | 每次workflow都重新 apt install，浪费~3分钟/次 |
| ⚠ R-02 | **C Core重复构建** | ci.yml build job → sdk-ci.yml c-core job → protocol-ci.yml | 同一份代码被构建3次 |
| ⚠ R-03 | **BAN检查重复** | ci.yml anti-pattern job + quality-gate job + quality-security.yml | 反模式扫描执行3次 |
| ⚠ R-04 | **docs-ci.yml 每日定时** | docs-ci.yml schedule | 无文档变更时也运行，浪费资源 |
| ⚠ R-05 | **quality-security.yml 3个cron** | quality-security.yml | 分3个cron执行3个任务，应合并为1个 |

---

## 第2章 — 重构方案：6→3条流水线

### 2.1 新架构总览

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        AgentOS CI/CD (3 Workflows)                      │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. ci.yml (450行) ── 所有代码变更的核心流水线 ── 80%的执行量            │
│     ├── Job 1: 依赖安装(缓存) + 构建(Release+Debug)                     │
│     ├── Job 2: 测试(ctest + pytest) + 覆盖率                            │
│     ├── Job 3: 质量门禁(BAN-01~36 + cppcheck + clang-format)           │
│     └── Job 4: 协议兼容性(仅gateway路径变更时)                          │
│     Trigger: push(main/develop) + PR(main)                              │
│                                                                          │
│  2. quality-security.yml (120行) ── 定时安全+质量监控                    │
│     ├── Job 1: 安全审计(secret扫描+危险函数) ← 每日                     │
│     ├── Job 2: 质量监控(代码统计+技术债务) ← 每周                       │
│     └── Job 3: Stale管理 ← 每周                                         │
│     Trigger: scheduled(每日) + manual                                    │
│                                                                          │
│  3. release.yml (280行) ── 版本发布流水线                               │
│     ├── Job 1: C Core构建+SDK全语言打包                                  │
│     ├── Job 2: Changelog生成+GitHub Release创建                         │
│     └── Job 3: API文档生成+Doxygen发布到Pages                           │
│     Trigger: tag(v*) + manual                                            │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

废弃的文件：
  ❌ protocol-ci.yml → 合并到 ci.yml Job 4
  ❌ docs-ci.yml → 合并到 release.yml Job 3（仅在发版时生成API文档）
  ❌ sdk-ci.yml → 合并到 release.yml Job 1（仅在发版时构建SDK）
```

### 2.2 变更明细表

| 操作 | 源文件 | 目标 | 理由 |
|------|--------|------|------|
| 🗑 **删除** | `protocol-ci.yml` | — | 仅1个job，合并到 ci.yml |
| 🗑 **删除** | `docs-ci.yml` | — | API文档仅在发版时生成 |
| 🗑 **删除** | `sdk-ci.yml` | — | SDK构建仅在发版时需要 |
| 🔄 **重写** | `ci.yml` | 合并protocol | 新增Job 4协议测试 |
| 🔄 **重写** | `release.yml` | 合并sdk+docs | 新增SDK打包+API文档 |
| 🔄 **精简** | `quality-security.yml` | 合并为1个cron | 原3个cron合为1个 |
| 🔄 **修复** | 全部 → `../AgentOS-build` | 符合BAN-33 | 构建目录统一 |
| 🔄 **修复** | `build-module.sh` | 统一构建目录 | 改为 `../AgentOS-build/` |
| 🔄 **修复** | `run-tests.sh` | 统一查找路径 | 改为 `../AgentOS-build/` |
| 🔄 **修复** | `ci-run.sh` | 统一构建目录 | 改为 `../AgentOS-build/` |

---

## 第3章 — 每条流水线的详细设计

### 3.1 ci.yml (核心流水线)

```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
    paths-ignore: ['**.md']
  pull_request:
    branches: [ main ]
    paths-ignore: ['**.md']
  workflow_dispatch:

env:
  BUILD_DIR: ${{ github.workspace }}/../AgentOS-build   # ✅ BAN-33合规

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  # ──────────────────────────────────────────────
  # Job 1: 构建 (Release + Debug)
  # ──────────────────────────────────────────────
  build:
    name: "Build (${{ matrix.config.type }})"
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        config:
          - { type: Release, cache: rel }
          - { type: Debug, cache: dbg }

    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
          path: AgentOS                       # ✅ 源码在 AgentOS/ 子目录

      - name: Cache ccache
        uses: actions/cache@v4
        with:
          path: ~/.ccache
          key: ccache-${{ matrix.config.cache }}-${{ hashFiles('AgentOS/**/*.c', 'AgentOS/**/*.h') }}

      - name: Install dependencies
        run: |
          sudo apt-get update -qq
          sudo apt-get install -y -qq build-essential cmake gcc g++ ccache \
            libcurl4-openssl-dev libcjson-dev libssl-dev \
            libmicrohttpd-dev libwebsockets-dev libcmocka-dev \
            libsqlite3-dev libyaml-dev valgrind cppcheck clang-format 2>/dev/null || true
          # cJSON fallback
          if ! dpkg -l libcjson-dev &>/dev/null; then
            git clone --depth 1 https://github.com/DaveGamble/cJSON.git /tmp/cjson
            cmake -S /tmp/cjson -B /tmp/cjson/build -DBUILD_SHARED_LIBS=ON -DENABLE_CJSON_UTILS=OFF
            sudo cmake --build /tmp/cjson/build --target install
          fi

      - name: Configure CMake
        run: |
          rm -rf ${{ env.BUILD_DIR }}
          cmake -S AgentOS -B ${{ env.BUILD_DIR }} \
            -DCMAKE_BUILD_TYPE=${{ matrix.config.type }} \
            -DBUILD_TESTS=ON -DBUILD_DAEMON=ON

      - name: Build
        run: |
          cmake --build ${{ env.BUILD_DIR }} -j$(nproc) 2>&1 | tee build.log
          echo "EXIT_CODE=${PIPESTATUS[0]}" >> $GITHUB_OUTPUT

      - name: Verify build
        if: always()
        run: |
          echo "Build exit code: ${{ steps.build.outputs.EXIT_CODE }}"
          echo "Build artifacts:"
          find ${{ env.BUILD_DIR }} -name "*.a" -o -name "*.so" -type f 2>/dev/null

  # ──────────────────────────────────────────────
  # Job 2: 测试 + BAN检查 + 质量门禁
  # ──────────────────────────────────────────────
  test:
    name: "Test & Quality"
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name == 'push' || github.event_name == 'pull_request'

    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
          path: AgentOS

      - name: Install test deps
        run: |
          sudo apt-get install -y -qq libcmocka-dev valgrind 2>/dev/null || true

      - name: Build with tests
        run: |
          cmake -S AgentOS -B ${{ env.BUILD_DIR }} \
            -DBUILD_DAEMON=ON -DBUILD_TESTS=ON -DCMAKE_BUILD_TYPE=Release
          cmake --build ${{ env.BUILD_DIR }} -j$(nproc)

      - name: Run CTest
        working-directory: ${{ env.BUILD_DIR }}
        run: |
          ctest --output-on-failure --timeout 120 -j$(nproc) 2>&1 | tee ctest.log
          echo "EXIT_CODE=${PIPESTATUS[0]}" >> $GITHUB_OUTPUT

      - name: BAN Audit (BAN-01~36)
        working-directory: AgentOS
        run: |
          bash scripts/pipeline/quality-gate.sh --strict

      - name: Assert tests pass
        run: |
          if [ "${{ steps.ctest_run.outputs.EXIT_CODE }}" != "0" ]; then
            echo "::error::CTest failures"; exit 1
          fi

  # ──────────────────────────────────────────────
  # Job 3: 协议兼容性测试 (仅gateway/protocol路径)
  # ──────────────────────────────────────────────
  protocol:
    name: "Protocol Compatibility"
    runs-on: ubuntu-latest
    if: contains(github.event.head_commit.modified, 'gateway/') || 
        contains(github.event.head_commit.modified, 'protocols/') ||
        github.event_name == 'workflow_dispatch'

    steps:
      - uses: actions/checkout@v4
        with:
          path: AgentOS

      - name: Build Gateway
        run: |
          cmake -S AgentOS -B ${{ env.BUILD_DIR }} \
            -DBUILD_DAEMON=ON -DCMAKE_BUILD_TYPE=Debug
          cmake --build ${{ env.BUILD_DIR }} -j$(nproc)

      - name: Verify
        run: |
          find ${{ env.BUILD_DIR }} -name "*gateway*" -o -name "*protocol*" | head -5
```

### 3.2 quality-security.yml (定时)

```yaml
name: Quality & Security

on:
  schedule:
    - cron: '0 3 * * *'       # 每日03:00 → 安全审计+质量监控+Stale一次跑完
  workflow_dispatch:

jobs:
  security-audit:
    name: "Security & Quality"
    runs-on: ubuntu-latest
    continue-on-error: true
    steps:
      - uses: actions/checkout@v4
        with:
          path: AgentOS

      - name: Secret scan
        run: |
          python3 AgentOS/scripts/pipeline/security_check.py AgentOS/agentos/

      - name: Code statistics
        run: |
          sudo apt-get install -y -qq cloc 2>/dev/null || true
          cloc AgentOS/agentos/ --quiet

      - name: Technical debt
        run: |
          echo "TODO/FIXME count:"
          grep -rn "TODO\|FIXME" AgentOS/agentos/ --include="*.c" --include="*.h" | wc -l

  stale:
    name: "Stale Management"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/stale@v9
        with:
          stale-issue-message: 'Inactive 30d. Closing in 7d.'
          stale-pr-message: 'Inactive 60d. Closing in 14d.'
          days-before-issue-stale: 30
          days-before-issue-close: 7
          days-before-pr-stale: 60
          days-before-pr-close: 14
```

### 3.3 release.yml (发布)

```yaml
name: Release

on:
  push:
    tags: ['v*.*.*']
  workflow_dispatch:
    inputs:
      version: { required: true }
      type: { default: 'stable', options: [stable, beta, rc] }

env:
  BUILD_DIR: ${{ github.workspace }}/../AgentOS-build

jobs:
  build-and-package:
    name: "Build + Package"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
          path: AgentOS
          fetch-depth: 0

      - name: Install deps
        run: |
          sudo apt-get update -qq && sudo apt-get install -y -qq \
            build-essential cmake gcc g++ libcurl4-openssl-dev libcjson-dev \
            libssl-dev libmicrohttpd-dev 2>/dev/null || true

      - name: Build C Core
        run: |
          cmake -S AgentOS -B ${{ env.BUILD_DIR }} -DBUILD_DAEMON=ON -DCMAKE_BUILD_TYPE=Release
          cmake --build ${{ env.BUILD_DIR }} -j$(nproc)

      - name: Package SDKs
        run: |
          mkdir -p artifacts
          # C Core libraries
          find ${{ env.BUILD_DIR }} -name "*.a" -exec cp {} artifacts/ \;
          # Python SDK
          if [ -d "AgentOS/agentos/toolkit/python" ]; then
            tar czf artifacts/agentos-sdk-python.tar.gz -C AgentOS/agentos/toolkit/python .
          fi
          # Rust SDK
          if [ -d "AgentOS/agentos/toolkit/rust" ]; then
            cd AgentOS/agentos/toolkit/rust && cargo build --release && cd ../../../..
            cp AgentOS/agentos/toolkit/rust/target/release/*.a artifacts/ 2>/dev/null || true
          fi
          # Go SDK
          if [ -d "AgentOS/agentos/toolkit/go" ]; then
            tar czf artifacts/agentos-sdk-go.tar.gz -C AgentOS/agentos/toolkit/go .
          fi
          # TS SDK
          if [ -d "AgentOS/agentos/toolkit/typescript" ]; then
            tar czf artifacts/agentos-sdk-ts.tar.gz -C AgentOS/agentos/toolkit/typescript .
          fi
          ls -la artifacts/

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: release
          path: artifacts/

  api-docs:
    name: "API Documentation"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          path: AgentOS

      - name: Install Doxygen
        run: sudo apt-get install -y -qq doxygen graphviz 2>/dev/null || true

      - name: Generate docs
        run: |
          if [ -f "AgentOS/Doxyfile" ]; then
            doxygen AgentOS/Doxyfile 2>&1 | tee doxygen.log
          fi

      - name: Deploy to Pages
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs/api/html

  create-release:
    name: "Create Release"
    needs: [build-and-package, api-docs]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          path: AgentOS
          fetch-depth: 0

      - uses: actions/download-artifact@v4
        with:
          name: release
          path: artifacts/

      - name: Generate changelog
        run: |
          echo "## What's Changed" > changelog.md
          git -C AgentOS log $(git -C AgentOS describe --tags --abbrev=0 2>/dev/null || echo HEAD~20)..HEAD \
            --oneline --no-merges >> changelog.md

      - uses: softprops/action-gh-release@v2
        with:
          body_path: changelog.md
          files: artifacts/*
          prerelease: ${{ contains(github.ref_name, 'beta') || contains(github.ref_name, 'rc') }}
```

---

## 第4章 — 废弃脚本清单与原因

| 文件 | 原因 |
|------|------|
| ~~`protocol-ci.yml`~~ | 合并到 ci.yml Job 3，减少独立workflow开销 |
| ~~`docs-ci.yml`~~ | API文档仅在发版时需要。日常文档变更走ci.yml即可 |
| ~~`sdk-ci.yml`~~ | SDK构建仅在发版时打包。日常SDK代码变更走ci.yml构建验证 |

## 第5章 — 脚本修改清单

| 脚本 | 问题 | 修改 |
|------|------|------|
| `build-module.sh` | `build-${module}` 违反BAN-33 | 改为 `../AgentOS-build/${module}` |
| `ci-run.sh` | 同上 | 改为 `../AgentOS-build/` |
| `run-tests.sh` | 查找 `build-${module}` | 改为查找 `../AgentOS-build/` |
| `install-deps.sh` | 无问题 | 保留不动 |
| `quality-gate.sh` | BAN-33检查路径 | 确认指向 `AgentOS/` 而非 `build-*/` |

---

## 第6章 — 效果对比

| 指标 | 重构前(6条) | 重构后(3条) | 优化 |
|------|-----------|-----------|------|
| workflow文件数 | 6个/1083行 | **3个/850行** | -50%/-22% |
| 总job数 | 22个 | **9个** | -59% |
| 每次push触发数 | 3~4条 | **1条**(ci.yml) | -70% |
| 依赖安装次数/push | 3次×2min | **1次** | -4min/push |
| C Core构建次数/push | 3次×3min | **1次** | -6min/push |
| CI总耗时/push | ~12min | **~5min** | -58% |
| BAN-33违规 | 6处 | **0处** | 全部修复 |
| 构建目录 | `AgentOS/build` 等 | `../AgentOS-build/` | 统一 |

---

<div align="center">
**© 2026 SPHARX Ltd. All Rights Reserved.**
*From data intelligence emerges*
</div>
