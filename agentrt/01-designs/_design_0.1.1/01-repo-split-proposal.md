AgentRT 仓库拆分完整方案
基于 5 轮深度源码精读（atoms 7 组件 / commons 20+ 子模块 / cupolas 7 子系统 / heapstore / protocols 五层 / gateway / daemon 12 进程 + svc_common 40+ 组件 / SDK 6 子项目 / ecosystem / scripts / deploy / tests）和 7 轮讨论结论。

一、项目现状
1.1 整体架构
AgentRT 是一个 Agent 运行时操作系统，采用微内核架构，自底向上分为：


Plain Text

SDK 层      Python / Go / Rust / TypeScript / CLI / TUI    （纯 HTTP 客户端，零 C 依赖）
              ↑ REST + JSON-RPC + MCP/A2A/OpenAI 兼容
Daemon 层    12 守护进程 + svc_common 40+ 组件              （真进程隔离，静态库共享）
              ↑ IPC Bus (Unix Socket / TCP / SHM)
Gateway 层   HTTP / WS / Stdio → JSON-RPC 2.0               （协议翻译，零业务逻辑）
              ↑
Protocols    A2A / MCP / ACP / OpenAI / Claude / OpenClaw    （五层协议栈）
Cupolas      安全穹顶（RBAC+ABAC+审计+沙箱+熔断+零信任）     （7 大子系统）
Heapstore    SQLite + 内存混合存储引擎                        （7 大存储引擎）
Atoms        微内核 7 组件（corekern/memory/coreloopthree/   （syscall C ABI 边界）
              syscall/taskflow/frameworks/memoryrovol）
Commons      平台抽象 + 20+ utils + agentos_types.h           （依赖图叶子节点）
1.2 依赖拓扑（基于 CMakeLists.txt 实际链接关系）

Plain Text

commons ←──────── 所有上层模块
   ↑
atoms (7 组件)         cupolas ←─── gateway (反向 include ⚠️)
   ↑                      ↑            ↑
   ├─ corekern (根)       │            │
   ├─ memory              │            │
   ├─ coreloopthree ──────┼────────────┘  ⚠️ 直接编译 daemon/common + daemon/hook_d + cupolas 源码
   ├─ syscall             │
   ├─ taskflow            │
   ├─ frameworks          │
   └─ memoryrovol (桥接)  │
                          │
heapstore ←─── corekern   │
   ↑                      │
protocols ────────────────┘  ⚠️ 直接编译 daemon/common/safe_string_utils.c
   ↑
gateway (依赖 protocols + atoms/memory + atoms/syscall)
   ↑
daemon (svc_common PUBLIC 传递 cupolas 给全部 12 进程)
   ├─ tool_d: ⚠️ 唯一 --whole-archive 链接 atoms 全栈
   └─ 其余 11 进程: 纯 IPC 与 atoms 解耦
   ↑
SDK (零 C 编译依赖，纯 HTTP)
1.3 五处跨层源码编译耦合（拆仓的真正阻碍）
#	耦合点	源文件归属	被编译进	修复难度
1	coreloopthree 编译 daemon/common/src/checkpoint.c + orchestrator.c	daemon 层	atoms 层	中
2	coreloopthree 编译 cupolas/src/yaml_minimal.c	cupolas 层	atoms 层	小
3	coreloopthree 编译 daemon/hook_d/src/{service,hook_executor,hook_registry,hook_interceptor,hook_timeout}.c	daemon 层	atoms 层	大
4	protocols 编译 daemon/common/src/safe_string_utils.c	daemon 层	protocols 层	小
5	cupolas 私有 include gateway/include，调用 gateway_register_endpoint()	gateway 层	cupolas 层（反向）	中
1.4 命名不一致
项目名为 AgentRT（CMakeLists.txt:6 project(AgentRT)），但内部标识符仍为 agentos_ 前缀，涉及 7 个层面：

源码目录 agentos/
CMake target agentos_common / agentos_atoms 等 15+ 个
运行时路径 /etc/agentos / AGENTOS_CONFIG_DIR
安装路径 include/agentos/
C 公开 ABI agentos_error_t / agentos_syscalls_init() 等（数千处）
C 宏 AGENTOS_API / AGENTOS_VERSION 等
SDK 包名 agentos(PyPI) / @agentos/sdk(npm) / agentrt-rs(crate) / github.com/spharx/agentrt/sdk/go
二、拆分原则
原则	说明
ABI 契约边界	以稳定的 C ABI（syscall 接口）和协议契约（IPC + JSON-RPC）作为仓库分界
依赖单向向下	下游不得反向依赖上游，必须先打破 5 处跨层耦合
发布节奏差异	稳定层（commons/atoms）与快变层（daemon/SDK）分离
先改名后拆分	改名在单仓内一次完成（验证成本最低），拆分变成纯机械搬移
先解耦后拆仓	C 层必须先修复跨层耦合才能独立成仓；SDK 层零耦合可立即可拆
原子化适度	atoms 内部 7 组件依赖链深，保持单仓；SDK 按语言拆分是最高性价比原子化
三、执行顺序（四阶段）

Plain Text

阶段 0：改名（单仓内完成，0.1.0 → 0.2.0）
   ↓
阶段 1：立即可拆的仓库（零跨层耦合，0.2.0 → 0.2.1）
   ↓
阶段 2：重构解耦 5 处跨层耦合（0.2.1 → 0.3.0）
   ↓
阶段 3：C 层仓库拆分 + 伞仓组装（0.3.0 → 1.0.0）
四、阶段 0：改名（先于拆分）
4.1 为什么先改名
理由	说明
验证成本最低	单仓单构建，改名后一次 ctest 即可全量验证；拆仓后需 16 仓各自验证 + 伞仓联调
git 历史可追踪	先改名是纯 rename commit，拆分是纯搬移 commit，git --follow 可正确追踪
兼容别名集中管理	单仓内建一份兼容别名头，拆分时随仓分发；拆仓后建需跨 16 仓协调
拆分变机械动作	改完名后拆分无语义变更，review 容易、冲突可控
4.2 分层改名策略
层	内容	策略
A 内部	目录 agentos/→agentrt/、CMake target agentos_*→agentrt_*、配置路径	直接改，不留兼容
B 公开 ABI	C 函数 agentos_*→agentrt_*、类型 agentos_error_t→agentrt_error_t、宏 AGENTOS_API→AGENTRT_API	改 + 生成兼容别名头（agentos_compat_aliases.h），0.3.0 删除
C SDK 包名	agentos→agentrt(PyPI) / @agentos/sdk→@agentrt/sdk(npm) / agentrt-rs 保持 / Go module path 更新	改 + 旧包留 re-export 一个版本
4.3 验证标准

Bash

# 改名后零残留检查
grep -rn '\bagentos_' --include='*.c' --include='*.h' --include='*.py' --include='*.go' --include='*.rs' --include='*.ts' . | grep -v 'compat_aliases' | wc -l
# 期望输出: 0
五、阶段 1：立即可拆的仓库（零跨层耦合）
以下 8 个仓库不涉及任何跨层源码编译耦合，在改名完成后可立即拆分。

5.1 SDK 仓库（6 个）
5.1.1 agentrt-sdk-python
维度	内容
源码	sdk/python/ 全部内容
包名	agentrt（PyPI），import agentrt
传输层	HTTP（requests/aiohttp）+ 可选 FFI（ctypes 运行时加载 libagentrt.so）
C 编译依赖	无（纯 Python 源码分发）
依赖	requests / aiohttp / urllib3 / asyncio-throttle / tiktoken
契约	REST API /api/v1/* + JSON-RPC /rpc，默认端口 18789
构建	pyproject.toml（已存在）
备注	syscall.py 的 FFI 是运行时 ctypes.CDLL 加载，非编译依赖；未加载时走 HTTP 兜底
5.1.2 agentrt-sdk-go
维度	内容
源码	sdk/go/ 全部内容
Module path	github.com/agentrt/sdk-go
传输层	纯 HTTP（net/http 标准库）
C 编译依赖	无（无 cgo，无 import "C"）
依赖	零外部依赖（纯 Go 标准库）
构建	go.mod（已存在，go 1.22）
5.1.3 agentrt-sdk-rust
维度	内容
源码	sdk/rust/ 全部内容
Crate 名	agentrt-rs（保持不变，use agentrt_rs::...）
传输层	纯 HTTP（reqwest）
C 编译依赖	无（无 bindgen，无 extern "C"）
依赖	reqwest / tokio / serde / serde_json / thiserror / async-trait / chrono / uuid
构建	Cargo.toml（已存在，edition 2021）
5.1.4 agentrt-sdk-typescript
维度	内容
源码	sdk/typescript/ 全部内容
npm 包名	@agentrt/sdk
传输层	纯 HTTP（axios + 内置 fetch）
C 编译依赖	无（无 node-gyp / node-addon-api / napi）
依赖	axios / ws（运行时）；typescript / jest / ts-jest（开发）
构建	package.json + tsconfig.json + jest.config.js（已存在）
5.1.5 agentrt-cli
维度	内容
源码	sdk/cli/ 全部内容
二进制名	agentrt
传输层	纯 HTTP（reqwest），默认 http://localhost:8080
C 编译依赖	无
SDK 依赖	不依赖 rust SDK crate（独立实现 GatewayClient）
依赖	clap / reqwest / tokio / serde / colored / indicatif
构建	Cargo.toml（已存在，edition 2021）
5.1.6 agentrt-tui
维度	内容
源码	sdk/tui/ 全部内容
二进制名	agentrt-tui
传输层	纯 HTTP（reqwest）
C 编译依赖	无
SDK 依赖	不依赖 rust SDK crate
依赖	ratatui / crossterm / reqwest / tokio
构建	Cargo.toml（已存在）
5.2 agentrt-ecosystem 仓
维度	内容
源码	ecosystem/openlab/ + ecosystem/prompts/ + ecosystem/hooks/ + ecosystem/examples/
不含	manager/（单独成仓）、skills/（硬依赖 sdk/python）
依赖	SDK 层（HTTP 调用），无 C 依赖
构建	openlab 有独立 pyproject.toml；其余为脚本/配置
备注	skills 因硬依赖 sdk/python/agentos/plugin_types.py，暂留 Python SDK 仓或后续处理
5.3 SDK 层拆分小结

Plain Text

agentrt-sdk-python   ──┐
agentrt-sdk-go       ──┤  零 C 依赖，零跨层耦合
agentrt-sdk-rust     ──┤  各自独立构建系统
agentrt-sdk-typescript ─┤  契约 = REST + JSON-RPC
agentrt-cli          ──┤  立即可拆
agentrt-tui          ──┘
agentrt-ecosystem    ──── 基本干净，立即可拆
六、阶段 2：重构解耦（C 层拆分的前提）
6.1 解耦优先级与方案
按「最小改动最大收益」排序：

解耦 #5：cupolas ← gateway（反向 include）
项	内容
问题	cupolas/CMakeLists.txt:173 私有 include gateway/include；cupolas_monitoring.c:24 调用 gateway_register_endpoint()
修复	提取 gateway_register_endpoint 为回调函数指针注入：cupolas 定义 typedef void (*endpoint_register_fn)(...)，daemon 启动时将 gateway 的函数指针注入 cupolas
工作量	中
解耦 #4：protocols ← daemon/common/safe_string_utils.c
项	内容
问题	protocols/CMakeLists.txt 直接编译 daemon/common/src/safe_string_utils.c
修复	将 safe_string_utils.c 移至 commons/utils/string/（安全字符串操作本就属于基础库）
工作量	小
解耦 #2：coreloopthree ← cupolas/yaml_minimal.c
项	内容
问题	coreloopthree 直接编译 cupolas/src/yaml_minimal.c
修复	将 yaml_minimal.c 移至 commons/utils/config_unified/（YAML 解析本就属于基础配置库）
工作量	小
解耦 #1：coreloopthree ← daemon/common/checkpoint.c + orchestrator.c
项	内容
问题	coreloopthree 直接编译 daemon/common/src/checkpoint.c + orchestrator.c
修复	将 checkpoint/orchestrator 的接口定义留在 atoms（checkpoint.h / orchestrator.h），实现有两种方案：(A) 移至 commons/utils/execution/；(B) 保留在 daemon/common，atoms 通过函数指针注入
推荐方案	(A)，因为 checkpoint/orchestrator 是通用执行框架，不属于 daemon 特有逻辑
工作量	中
解耦 #3：coreloopthree ← daemon/hook_d/*.c（最复杂）
项	内容
问题	coreloopthree 直接编译 daemon/hook_d/src/{service,hook_executor,hook_registry,hook_interceptor,hook_timeout}.c 共 5 个文件
修复	将 hook 的核心执行引擎（hook_registry + hook_interceptor + hook_timeout）提取为 atoms 层接口（atoms/coreloopthree/src/hooks/），daemon/hook_d 仅保留 daemon 生命周期管理和 IPC 入口
工作量	大
6.2 解耦后的依赖验证

Bash

# 验证 atoms 不再编译 daemon/cupolas 源码
grep -n 'daemon/' agentos/atoms/coreloopthree/CMakeLists.txt
grep -n 'cupolas/' agentos/atoms/coreloopthree/CMakeLists.txt
# 期望: 无匹配

# 验证 protocols 不再编译 daemon 源码
grep -n 'daemon/' agentos/protocols/CMakeLists.txt
# 期望: 无匹配

# 验证 cupolas 不再 include gateway
grep -n 'gateway' agentos/cupolas/CMakeLists.txt
# 期望: 无匹配

# 全量构建验证
cmake -B build && cmake --build build -j$(nproc) && ctest --test-dir build
七、阶段 3：C 层仓库拆分 + 伞仓组装
7.1 C 层仓库（7 个，解耦后拆分）
7.1.1 agentrt-commons
维度	内容
源码	agentos/commons/ 全部内容
CMake target	agentrt_common（静态库）
依赖	Threads、可选 YAML / cJSON
职责	跨平台 C11 抽象层（platform/）+ 20+ utils 子模块 + 类型权威源（agentrt_types.h）
核心子模块	platform/（含 export.h）、utils/atomic_compat.h、utils/memory/、utils/types/、utils/error/、utils/sync/、utils/logging/、utils/config_unified/
安装	lib/libagentrt_common.a + include/agentrt/{platform,utils/*}/
解耦后新增	safe_string_utils.c（从 protocols 迁入）、yaml_minimal.c（从 cupolas 迁入）、checkpoint.c + orchestrator.c（从 daemon/common 迁入）
版本节奏	超稳，半年改一次
7.1.2 agentrt-atoms
维度	内容
源码	agentos/atoms/ 全部 7 组件
CMake target	agentrt_core / agentrt_memory / agentrt_coreloopthree / agentrt_cognition / agentrt_execution / agentrt_syscall / agentrt_taskflow / agentrt_frameworks / agentrt_atoms(INTERFACE)
依赖	agentrt-commons（find_package）
组件	corekern（微内核核心）/ memory（可拔插记忆）/ coreloopthree（认知环+执行环+学习环）/ syscall（23 系统调用+沙箱）/ taskflow（Pregel+DAG）/ frameworks（适配器注册表）/ memoryrovol（外部桥接）
ABI 边界	syscalls.h + agentrt_sandbox.h（C ABI 导出，AGENTRT_API 宏标记）
内部依赖链	corekern → memory → coreloopthree → {syscall, taskflow} → frameworks
保持单仓理由	7 组件内部依赖链深（4 级版本耦合），拆成 5 仓的协调成本远大于收益
版本节奏	稳定（ABI 兼容期内不 break）
备注	memoryrovol 是纯 CMake 桥接层（无 .c 文件），定位外部 OpenAirymax/MemoryRovol 仓库
7.1.3 agentrt-cupolas
维度	内容
源码	agentos/cupolas/ 全部内容（解耦后不再 include gateway）
CMake target	agentrt_cupolas（静态库）
依赖	agentrt-commons、可选 OpenSSL
子系统	sanitizer / permission(RBAC+ABAC) / audit(SHA-256 哈希链) / workbench(cgroups) / safety_guard(V2) / dynamic_policy / zero_trust
安装	lib/libagentrt_cupolas.a + include/agentrt/cupolas/
解耦修改	删除 target_include_directories(... gateway/include)；cupolas_monitoring.c 改为回调注入
7.1.4 agentrt-heapstore
维度	内容
源码	agentos/heapstore/ 全部内容
CMake target	agentrt_heapstore（静态库）
依赖	agentrt-commons、可选 SQLite3（缺失降级为内存后端）
引擎	core / log / registry / trace / memory / token / batch（7 大存储引擎）
迁移	migrations/V001_initial_schema.sql + V002_add_tags_and_retry.sql
安装	lib/libagentrt_heapstore.a + include/agentrt/heapstore/
7.1.5 agentrt-protocols
维度	内容
源码	agentos/protocols/ 全部内容（解耦后不再编译 daemon 源码）
CMake target	agentrt_protocols（共享库，带 SOVERSION）
依赖	agentrt-commons、可选 cURL / cJSON
五层架构	Common（unified_protocol）/ Core（Router+Transformers+Registry+Extension）/ Standards（A2A+MCP+ACP）/ Integrations（OpenAI+Claude+OpenClaw+China Eco）/ Frameworks（LangChain+AutoGen）
定位	MCP/A2A/ACP/OpenAI 协议的最佳 C 参考实现（非另造标准）
安装	lib/libagentrt_protocols.so + include/agentrt/protocols/
平台限制	MCP 和 China Eco 在 Windows 上 OFF
7.1.6 agentrt-gateway
维度	内容
源码	agentos/gateway/ 全部内容
CMake target	agentrt_gateway（静态库）
依赖	agentrt-protocols + agentrt-commons + agentrt-atoms(memory) + cJSON（硬依赖）+ 可选 microhttpd / websockets / curl
实现	HTTP（libmicrohttpd）/ WS（libwebsockets）/ Stdio（REPL）三种网关，ops 虚表统一接口
核心模块	syscall_router（JSON-RPC → syscall 路由）/ jsonrpc（JSON-RPC 2.0）/ protocol_bridge（多协议自适应）/ rate_limiter / mcp_server
安装	lib/libagentrt_gateway.a + include/agentrt/gateway/
待修	include/gateway.h 与 src/gateway/gateway.h 同名冲突导致 test_gateway 被禁用
7.1.7 agentrt-daemon
维度	内容
源码	agentos/daemon/ 全部内容
依赖	agentrt-commons + agentrt-atoms + agentrt-cupolas + agentrt-heapstore + agentrt-protocols + agentrt-gateway
svc_common	40+ 组件静态库，PUBLIC 传递 cupolas 给全部 12 daemon
12 进程	gateway_d / llm_d / tool_d / sched_d / market_d / monit_d / channel_d / info_d / notify_d / observe_d / hook_d / plugin_d
进程隔离	真进程隔离（12 个独立可执行文件，svc_common 是 STATIC 库非 SHARED）
atoms 边界	11 个 daemon 纯 IPC；tool_d 唯一直接 ABI 链接（--whole-archive agentrt_coreloopthree）
紧耦合三元组	monit_d ↔ notify_d ↔ observe_d（可观测性子系统，不可拆分）
保持单仓理由	12 进程共享 svc_common 40+ 组件，svc_common 包含 llm_d/tool_d 头文件路径
7.2 agentrt-manager 仓（有条件拆分）
维度	内容
源码	ecosystem/manager/ 全部内容
职责	全项目配置管理中心 + JSON Schema 权威源（11 个 schema，272 项校验规则）
依赖	PyYAML + jsonschema + pytest（仅 3 个 Python 第三方库）
构建系统	需新建 pyproject.toml（当前不存在）
阻塞项	见 7.2.1
7.2.1 三个阻塞项（必须先解决）
阻塞	问题	解法
sanitizer 抑制文件	lsan-suppressions / valgrind-suppressions 被 CMakeLists.txt、Sanitizers.cmake、ci.yml、leak-detection.sh 硬引用	移至 daemon 仓或独立 agentrt-sanitizers 仓；manager 仅保留 sanitizer_rules.json
C 代码硬编码路径	8 处 daemon main.c 硬编码 agentos/manager/service/*/，其中 3 个配置文件实际不存在	改为 AGENTRT_CONFIG_DIR 环境变量驱动 + 补齐缺失配置
无构建系统	manager 目录下无 pyproject.toml	新建，声明包名 agentrt-manager + 依赖 + entry_points
7.2.2 跨模块内容归属
耦合点	归属	处理
sanitizer_rules.json 的 _owner.module = "cupolas"	内容定义归 cupolas	拆仓后所有权移交 manager，cupolas 通过 PR 协同
monitoring/ 目录服务 cupolas	cupolas 告警+Grafana	留在 manager（配置管理包含监控配置）
7.3 agentrt-devtools 仓
维度	内容
源码	scripts/（除 dev/cmake/ 5 个被 CMake 硬引用的模块） + deploy/ + tests/（integration/contract/security/benchmark 跨组件测试）
职责	CI 流水线、跨组件集成测试、契约测试、安全测试、基准测试、Docker/K8s/systemd 部署
依赖	全部仓库（仅测试场景）
备注	scripts/dev/cmake/ 下 5 个 CMake 模块（CompilerFlags / Sanitizers / Dependencies / Platform / Utils）被根 CMakeLists.txt 硬引用，必须随伞仓或 commons 仓分发
7.4 伞仓 agentrt（meta）
维度	内容
职责	顶层 CMakeLists.txt 编排 + CI 编排 + 全量集成验证
组装方式	CMake FetchContent（开发期）或 find_package（发布期）拉取各子仓指定版本
构建顺序	commons → atoms → cupolas → heapstore → protocols → gateway → daemon
内容	顶层 CMakeLists.txt + README.md + LICENSE + .github/workflows/ + scripts/dev/cmake/（5 个 CMake 模块）
八、完整仓库清单
8.1 总览

Plain Text

agentrt (伞仓)
│
├── C 层（阶段 3，解耦后拆分）
│   ├── agentrt-commons         平台抽象 + 20+ utils + 类型权威源
│   ├── agentrt-atoms           微内核 7 组件（syscall C ABI 边界）
│   ├── agentrt-cupolas         安全穹顶 7 子系统
│   ├── agentrt-heapstore       SQLite+内存混合存储引擎
│   ├── agentrt-protocols       五层协议栈（MCP/A2A/ACP 参考实现）
│   ├── agentrt-gateway         HTTP/WS/Stdio 协议网关
│   └── agentrt-daemon          12 守护进程 + svc_common 40+ 组件
│
├── SDK 层（阶段 1，立即可拆）
│   ├── agentrt-sdk-python      Python SDK（HTTP + 可选 FFI）
│   ├── agentrt-sdk-go          Go SDK（纯标准库）
│   ├── agentrt-sdk-rust        Rust SDK（reqwest）
│   ├── agentrt-sdk-typescript  TypeScript SDK（axios）
│   ├── agentrt-cli             命令行工具（clap + reqwest）
│   └── agentrt-tui             终端 UI（ratatui + reqwest）
│
├── 配置层（阶段 1-2，有条件拆分）
│   └── agentrt-manager         配置管理中心 + JSON Schema 权威源
│
├── 生态层（阶段 1，立即可拆）
│   └── agentrt-ecosystem       openlab + prompts + hooks + examples
│
└── 工程层（阶段 3）
    └── agentrt-devtools        CI + 跨组件测试 + 部署配置

合计: 17 个仓库（1 伞仓 + 16 子仓）
8.2 依赖关系图

Plain Text

                    agentrt (伞仓: FetchContent 编排)
                        │
        ┌───────────────┼───────────────────────────┐
        ▼               ▼                           ▼
  agentrt-devtools  agentrt-ecosystem         agentrt-manager
  (测试+部署)       (openlab+hooks)           (配置+Schema)
        │               │                           │
        │               ▼                           │
        │        SDK 层 (6 仓)                     │
        │     ┌───────┴───────┐                    │
        │     │ python/go/rust│                    │
        │     │ ts/cli/tui    │                    │
        │     └───────┬───────┘                    │
        │             │ HTTP                       │
        │             ▼                            │
        │     agentrt-daemon ◄─────────────────────┘ (配置消费)
        │             │
        │     ┌───────┴───────┐
        │     │ svc_common    │ (PUBLIC 传递 cupolas)
        │     │ 40+ 组件      │
        │     └───────┬───────┘
        │             │
        │     agentrt-gateway
        │             │
        │     agentrt-protocols
        │             │
        │     agentrt-cupolas
        │             │
        │     agentrt-heapstore
        │             │
        │     agentrt-atoms (7 组件)
        │             │
        │     agentrt-commons (叶子节点)
        │             │
        └─────────────┘ (全量集成测试)
8.3 各仓库发布节奏
仓库	节奏	稳定性	发版方式
agentrt-commons	超稳（半年）	最高	CMake package + 源码 tarball
agentrt-atoms	稳定（ABI 兼容期）	高	CMake package + 源码 tarball
agentrt-cupolas	稳定	高	CMake package
agentrt-heapstore	稳定	高	CMake package
agentrt-protocols	中速（月）	中	CMake package + 共享库
agentrt-gateway	中速	中	CMake package
agentrt-daemon	快速（周）	低	二进制 release
agentrt-sdk-python	快速	低	PyPI
agentrt-sdk-go	快速	低	Go module
agentrt-sdk-rust	快速	低	crates.io
agentrt-sdk-typescript	快速	低	npm
agentrt-cli	快速	低	Cargo + 二进制
agentrt-tui	快速	低	Cargo + 二进制
agentrt-manager	中速	中	PyPI
agentrt-ecosystem	快速	低	源码
agentrt-devtools	中速	中	源码
九、迁移路径时间线

Plain Text

0.1.0 (当前)
  │
  │  阶段 0：改名（单仓内）
  │  ├─ 目录 agentos/ → agentrt/
  │  ├─ CMake target agentos_* → agentrt_*
  │  ├─ C ABI agentos_* → agentrt_*（脚本批量 + 兼容别名头）
  │  ├─ 宏 AGENTOS_* → AGENTRT_*
  │  ├─ SDK 包名更新 + 旧包 re-export
  │  ├─ 全局 grep 零残留验证
  │  └─ ctest 全量通过
  │
0.2.0 (改名完成，单仓)
  │
  │  阶段 1：SDK + ecosystem 拆分（零耦合，立即可拆）
  │  ├─ 6 个 SDK 仓独立
  │  ├─ ecosystem 仓独立
  │  └─ 伞仓用 FetchContent 拉取验证
  │
0.2.1 (SDK 拆分完成)
  │
  │  阶段 2：重构解耦 5 处跨层耦合
  │  ├─ #5 cupolas↔gateway（回调注入）
  │  ├─ #4 protocols←safe_string_utils（移至 commons）
  │  ├─ #2 coreloopthree←yaml_minimal（移至 commons）
  │  ├─ #1 coreloopthree←checkpoint/orchestrator（移至 commons）
  │  └─ #3 coreloopthree←hook_d（提取 atoms 接口）
  │
  │  manager 阻塞项修复
  │  ├─ lsan/valgrind-suppressions 移至 daemon 侧
  │  ├─ 8 处 C 硬编码路径改为环境变量驱动
  │  └─ manager/pyproject.toml 新建
  │
0.3.0 (解耦完成，单仓)
  │
  │  阶段 3：C 层拆分 + 伞仓组装
  │  ├─ commons → agentrt-commons 仓
  │  ├─ atoms → agentrt-atoms 仓
  │  ├─ cupolas → agentrt-cupolas 仓
  │  ├─ heapstore → agentrt-heapstore 仓
  │  ├─ protocols → agentrt-protocols 仓
  │  ├─ gateway → agentrt-gateway 仓
  │  ├─ daemon → agentrt-daemon 仓
  │  ├─ manager → agentrt-manager 仓
  │  ├─ devtools → agentrt-devtools 仓
  │  └─ 删除兼容别名头
  │
1.0.0 (拆分完成 + 命名统一 + 接口清晰)
  │
  │  后续：开放标准（可选）
  │  ├─ 发布 AgentRT Kernel ABI 规范文档
  │  ├─ 发布 Memory Provider Interface 规范
  │  └─ 推动第三方独立实现
十、开放标准展望（v1.0 后）
拆仓是标准化的第一步——它强迫接口边界清晰化。v1.0 后可考虑将以下接口发布为开放规范：

标准化对象	内容	类比
AgentRT Kernel ABI	23 个 syscall 的语义规范（前置/后置条件/错误码/线程安全）	POSIX 之于操作系统
Memory Provider Interface	18 函数 vtable + 10 能力位	可拔插存储接口
Framework Adapter Interface	8 能力位 + 注册表协议	驱动适配模型
前提条件：

ABI 经实战验证（至少 v1.0）
有规范文档（不只是头文件）
有 compliance test suite
有第二个独立实现（否则只是产品文档，不是标准）
不适合标准化的：

协议层（MCP/A2A/ACP 已是外部标准，做参考实现即可）
配置管理（工程实践，非标准）
安全模型（需实战检验，太早）
十一、风险与对策
风险	严重度	对策
改名遗漏	高	脚本批量改 + 全局 grep 零残留检查 + ctest 兜底
解耦引入 bug	高	每解耦一处立即跑全量 ctest；解耦顺序从易到难
跨仓版本不匹配	中	伞仓 FetchContent 锁定 commit SHA；子仓语义化版本
tool_d 的 --whole-archive 链接	中	拆仓后 tool_d 必须在 CMakeLists 中 find_package(agentrt-atoms) 并保持 --whole-archive
daemon C 代码引用 manager 配置路径	中	统一改为 AGENTRT_CONFIG_DIR 环境变量
manager sanitizer 文件跨仓依赖	中	抑制文件移至 daemon 仓，manager 仅保留清洗规则
本地开发体验下降	低	提供 scripts/dev/setup-workspace.sh 一键 clone 全部子仓 + 配置 CMake
十二、关键决策记录
决策	选择	理由
先改名还是先拆分	先改名	验证成本最低、git 历史可追踪、拆分变机械动作
atoms 内部是否细分	保持单仓	7 组件 4 级依赖链，拆分协调成本 > 收益
daemon 内部是否细分	保持单仓	12 进程共享 svc_common 40+ 组件 + 跨进程头文件
SDK 按语言拆分	是，6 仓	零 C 依赖、各自独立构建系统、可独立发版
manager 独立成仓	有条件是	需先解决 3 个阻塞项（抑制文件/硬编码路径/构建系统）
protocols 是否做标准	否，做参考实现	MCP/A2A/ACP 已是外部标准，不另造
内核 ABI 是否做标准	v1.0 后	当前 v0.1 太早，需实战验证 + 规范文档 + 第二实现
