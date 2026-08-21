# AgentRT 近 15 轮开发复盘（2026-08-21）

> 本文为工程内部复盘记录，存放于 closed-docs（非开源），供后续开发参考。
> 覆盖范围：glibc 低基线重建、硬件自适应、CLI/TUI 交互优化、跨架构打包、
> commons 统一基础库强化、代码质量与体积控制等阶段。

## 1. 任务背景与时间线

| 阶段 | 目标 | 结果 |
|------|------|------|
| 树莓派 Pi4 可运行性评估 | 2GB 内存/16GB 储存端侧运行 | 确定 minimal 画像方案 |
| glibc 低基线重建（b1–b8） | 二进制包广谱兼容 Linux 发行版 | 完成：ubuntu:20.04（glibc 2.31）双架构 |
| 2.3.2 硬件自适应（d1） | 二进制安装自动识别/裁剪/监控恢复 | 完成：airymaxrt profile/monitor |
| 2.2.1 CLI 交互优化（d2） | /help 按类别分组 | 完成：会话/系统/资源/安全 |
| 2.1.1 功能接线验证（d3） | 全部 daemon 在线且可用 | 完成：16/16 在线，/info /tools 返回真实数据 |
| 2.4 代码质量/体积（d4） | 清理冗余、控制体积 | 完成：构建产物 6.8G→1.8G |
| 2.3.1 commons 强化（d5） | 跨平台抽象沉淀 | 完成：airy_localtime_r + 碎片收敛 |

## 2. 成功经验

### 2.1 构建基线与运行基线必须显式绑定
- 用最低目标发行版容器构建，并用 `readelf` 逐符号验证 `GLIBC_*` 版本上限
  （x86_64 要求 ≤2.30、arm64 同基线），不能只看"构建成功"。
- 产物覆盖：Ubuntu 20.04+/Debian 11+/Pi OS Bullseye+（2020 年后系统）。

### 2.2 依赖版本差异的根因处理
- cJSON 1.7.10（20.04）缺 `cJSON_GetNumberValue` → 源码编译 1.7.18。
- OpenSSL 1.1.1（20.04，EOL + 头文件 poison）→ 源码编译 3.0.17 到 /usr/local；
  系统 libcurl 依赖 libssl.so.1.1、新库依赖 libssl.so.3，按 soname 并存。
- glibc<2.34 的 shm_open/shm_unlink 在 librt → `airy_platform_libs` INTERFACE 库
  统一链接（glibc≥2.34 时 librt 为空，链接无副作用）。

### 2.3 静态库符号污染的系统性修复
- OSS 构建把 license.c 的 OpenSSL 符号打进静态库，导致下游 Rust TUI 静态链接
  未定义符号。根因是 `AIRY_USE_OPENSSL` 无条件定义。
- 修复：仅 `NOT MEMORYROVOL_OSS` 且 OpenSSL 存在时定义宏；RSA 公钥数组同步
  移入守卫。验证：`nm` 检查符号数为 0。

### 2.4 跨架构构建的成本控制
- QEMU arm64 下 crates.io 下载超时 → 复用 x86 构建机 cargo registry 缓存 +
  `--offline` 构建。
- 公共头文件（如 platform.h）变更会引发大范围重编，改动前需评估成本。

### 2.5 交互与自适应设计
- `/help` 按类别分组，避免 26 条命令平铺淹没关键入口。
- 硬件画像持久化到 `$AIRY_HOME/config/profile.env`；monitor 区分显式/auto
  画像，auto 自动恢复，显式仅提示一次（`_HINTED` 去重），避免骚扰。

### 2.6 流式输出通道分离（2026-08-21 补充）
- `airy_cli -p` 模式的 stderr 重定向策略按消费方区分：**stderr 为 TTY（人类
  终端使用）时重定向到日志文件**，trace 行与 ERROR 日志不再与答案视觉混叠；
  仅当 stderr 被管道/脚本消费（非 TTY）时保留直连，供脚本读取 trace 进度。
- 复用既有 `isatty(STDERR_FILENO)` 一次探测，无额外状态，交互/管道两场景
  行为都正确（交互模式原逻辑不变，`-p` 终端场景新增）。

### 2.7 错误码按场景语义映射（2026-08-21 补充）
- `cli_chat_err_desc()`：聊天场景的 NOT_FOUND 明确指向"llm_d 未运行"并给出
  可执行提示，而非通用"目标不存在"；其余错误沿用通用映射，避免多义码误导。
- 原则：同一错误码在不同业务场景下应有场景化文案，通用映射只作兜底。

### 2.8 status 状态判据：socket 可连接优于进程名匹配（2026-08-22 补充）
- `airymaxrt status` 原用 `pgrep -x 'llm_d|think_d|...'` 判 daemon 群状态，容器/
  其他实例（smoke-home/bin、arm64-smoke/bin）的同名进程被误算为本实例运行中，
  出现「status 显示运行中但 gateway 离线、llm.sock 未就绪」的矛盾。
- 改进：daemon 群状态以关键 socket 可连接为权威判据（`_sock_alive` 含
  health_check 往返），只查核心链路 llm/think/agent/tool 四根 socket。
- 教训：**任何"运行中"判据必须能区分实例**；进程名匹配天然无法区分同名
  多实例，socket 路径（本实例专属 RUNTIME_DIR）才是唯一真相源。

### 2.9 启动前 stale pid 清理（2026-08-22 补充）
- 冷启动后 `run/` 残留 17 个 `.pid` 文件（bootstrap 时代 daemon 退出未清，
  0.1.2 并行拉起版自身不写 pid 文件），干扰 run 目录观感且误导诊断。
- 改进：拉起前统一清理——pid 无对应存活进程（`kill -0` 判据）即删，存活
  进程的 pid 文件保留。
- 教训：迁移启动器时，旧产物（pid 文件、socket、日志）也要一并迁移清理，
  否则"新逻辑 + 旧残留"叠加出难以归因的现场。

## 3. 失败教训

### 3.1 QEMU 跨架构环境的网络与性能瓶颈
- 教训：先在容器内验证 registry 可用性再全量构建；`transfer too slow` 超时
  需配置 `http.low-speed-limit=1`。
- 改进：所有跨架构构建先做小步验证（依赖下载、单目标编译）。

### 3.2 monitor 逻辑缺陷（不会自动恢复）
- 初版比较两次 `assess_hardware` 结果，minimal 状态永不触发升级。
- 根因：比较对象错误（应对比「当前生效画像」而非两次探测结果）。
- 改进：引入 `AIRYRT_PROFILE_RAW` 区分显式/auto，修正比较基准。

### 3.3 docker cp 权限陷阱
- 容器 root 创建的目录（arm64-pkg-focal）宿主 docker cp 报
  `RemoveAll: permission denied`。
- 改进：容器内 cp（root 可写）再同步到宿主导出的包目录。

### 3.4 动态库收集路径过滤
- 首次收集把 `ldd` 输出路径当 soname 过滤出错，导致 MISSING。
- 改进：`awk "/=>/{print \$3} !/=>/{print \$1}"` 处理后再 `find` 定位并
  `cp -L`，47 个库全齐（含 libcrypto/ssl 1.1+3 并存）。

### 3.5 过时注释技术债
- CI riscv64 注释仍写 "ubuntu:24.04"，容器实际已是 20.04。
- 改进：注释与实现同步修订，扫描时纳入检查。

### 3.6 跨容器共享构建目录的缓存污染（2026-08-21 补充）
- arm64 与 x64 两个容器**共享同一构建目录**（bind mount），在 arm64 容器中
  执行 `cmake -DOPENSSL_*` 会改写共享的 CMakeCache，把 OpenSSL 库路径指向
  arm64 容器内的 `/usr/local/lib`，导致 x64 容器重建时报
  `No rule to make target '/usr/local/lib/libssl.so'`。
- 教训：多架构容器共享构建树时，**修改缓存变量前必须先确认执行容器与
  目标产物架构一致**；用 `uname -m` 与 `file <现有产物>` 交叉验证。
- 改进：切回正确容器（x64）重新 `cmake -DOPENSSL_*` 指回 `/usr/local/lib64` 后
  即恢复，成本约 1 分钟；后续若继续共用构建树，应将 CMakeCache 按架构分目录。

### 3.7 部署漂移：bin/ 二进制落后源码（2026-08-22 补充）
- `bin/airy_cli` 为 8/20 旧版（12MB debug 构建），不含新提交的
  `cli_parse_args`/流式思考进度逻辑，导致前端行为与源码不一致，排查半天
  才定位到"代码改了但跑的不是它"。
- 教训：**边开发边测试必须打到同一部署位**。源码改完需同步部署（源码区外
  构建产物覆盖 .airymaxrt 部署位），否则一切实测都作用于旧二进制，结论
  全部失真。修复后从 focal-x64 构建目录覆盖部署（1MB release 版）。
- 改进：验证前先 `file`/比对版本，确认二进制与源码 HEAD 一致。

### 3.8 意图分类：场景描述动词误判为命令（2026-08-22 补充）
- `cli_classify_heuristic` 的 task_marks 用 `strstr` 全串匹配，"运行"命中
  "请帮我分析一下：一个 8GB 内存的树莓派上**运行**容器化数据库…" 中的
  "运行"（场景描述），把纯咨询"分析/比较"问题误路由进任务管线（GCCP
  四问 + 执行计划 + 跑任务），正是用户抱怨的"简单对话随意进入任务集"。
- 根因：命令动词与场景描述动词（运行/测试/检查/启动/停止）未区分；分析/
  比较/评估类咨询词缺失，咨询语义先被"命令"短路。
- 改进：分析/比较类咨询词入 consult 层（含"产物变更强动词"例外：含
  实现/修复/开发/构建/创建/部署/重构/迁移/安装/配置/删除/更新/下载/
  编写/生成/集成/改造时仍判 task）；场景动词需无描述性语境（"上运行"/
  "性能测试"/"安全检查"等）才计 task。
- 教训：**关键词分类必须区分"动词的语义角色"**——同一动词可能是命令
  （"运行这个脚本"）也可能是场景修饰（"在树莓派上运行"），全串 strstr
  必然误判；咨询词表要完整覆盖分析/比较/评估类。

## 4. 工程原则沉淀

1. **SSoT（单一真相源）**：跨平台能力统一沉淀到 commons，调用点收敛到统一
   API（如 `airy_sleep_ms`、`airy_localtime_r`），消灭 `#ifdef _WIN32` 碎片。
2. **「除了核心，一切都是服务」**：12+ 能力 daemon 化，airymaxrt 按画像补齐，
   gateway 降级不影响核心。
3. **严禁桩函数**：网络工具等真实实现由 tool_d 提供，CLI 只做协议编排。
4. **源码区零构建**：所有构建/集成/验证均在源码区外（.airymaxrt 容器）。
5. **边开发边测试**：每次改动双架构（x86_64 + arm64）重编 + 冒烟 + 诊断检查。

## 5. 后续改进方向

- [x] 2.1.1 全部 daemon 方法级 RPC 全功能验证：x86_64/arm64 双架构 34/34 方法
      PASS + gateway HTTP 健康（2026-08-21 完成）。
- [x] 2.2.2 CLI/TUI 终端能力自动评估与切换：TERM=dumb/屏幕过小自动降级 CLI、
      TUI 异常退出自动续接 CLI（2026-08-21 完成）。
- [x] 2.3.1 RISC-V 位宽修复：platform.h 位宽判定从架构枚举改为
      UINTPTR_MAX==UINT64_MAX（riscv64 此前被判 32 位）（2026-08-21 完成）。
- [x] 2.3.1 RISC-V 实际运行验证：qemu-riscv64 用户态模拟 + docker
      --platform=linux/riscv64，真实编译 commons（platform/sync/memory/logger）
      并运行通过：`platform=Linux bits=64 sizeof(void*)=8`，位宽修复在
      riscv64 上实测生效（2026-08-21 完成）。
- [x] 2.2.1 CLI 交互深审：-p 模式 stderr 按 TTY/管道分离 + 聊天错误场景化
      文案（2026-08-21 完成，双场景实测）。
- [x] 2.4 main 参数解析抽离：cli_parse_args 独立函数，main 圈复杂度下降
      （2026-08-21 完成，重编 + 冒烟通过）。
- [x] 2.1.1 status 判据修复：daemon 群状态改 socket 权威判据（弃 pgrep 进程名
      匹配），修复"显示运行中但网关离线"矛盾（2026-08-22 完成，冷启动实测）。
- [x] 2.1.1 启动 stale pid 清理：拉起前 kill -0 判存活统一清理 run/*.pid
      （2026-08-22 完成，run/ 残留 17→0）。
- [x] 2.2.1 意图分类修复：分析/比较/评估类咨询词入 consult 层 + 场景描述
      动词（运行/测试/检查/启动/停止）语境判定，"请帮我分析…运行…比较…"
      不再误入任务集（2026-08-22 完成：单测 44/44 + CLI 端到端实测，见 3.8）。
- [ ] Windows/macOS 平台兼容性实测（当前仅 CI 编译链路）。
- [ ] 高圈复杂度函数系统性拆分（基线见下，拆分需专门重构轮次并全量回归）。

### 5.1 圈复杂度基线（pmccabe，2026-08-21）

| 函数 | 圈复杂度 | 说明 |
|------|---------|------|
| airy_cli main | 298 | CLI 主入口（初始化 DAG + 事件循环），需按阶段抽离 |
| cli_tui_readline | 170 | 全屏 TUI 按键/输入核心，拆分风险高 |
| cli_chat_reply | 88 | 对话回复管线 |
| handle_agent_run | 80 | gateway agent 执行编排 |
| airy_token_count | 78 | token 分类（switch 密集，逻辑可复核） |
| notify_d_event_loop | 74 | 事件循环 |

> 注：pmccabe 对 switch-case 逐分支计数，部分高值源于密集 switch 而非深嵌套。
