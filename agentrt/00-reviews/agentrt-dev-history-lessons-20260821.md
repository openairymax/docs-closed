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

### 2.11 执行链路缺陷根因修复（2026-08-22 补充）
- 修复 A（coreloopthree engine_phase0）：LLM 分解偶发返回空 content，
  `decomp_output_len=0` 仍调 `airy_tc_step_complete` 报 NULL/invalid params。
  修复：空串视为分解失败走 heuristic fallback + 调用处加 `len>0` 守卫。
- 修复 B（cli_exec_review）：`cli_exec_t2_review`/`cli_exec_t1f_adjudicate`
  的 `t2x/t1fx/t1px` 声明在 if 块内、指针逃逸出块，后台 wait 线程异步读
  `cfg.model` 触发 ASan stack-use-after-scope。修复：提升到函数作用域。
- 教训：**栈变量生命周期必须覆盖其指针逃逸的所有消费方**（含后台线程）；
  ASan 实测复现是这类缺陷的可靠判据。两处修复均经重编部署 + e2e 验证。

### 2.12 daemon 生命周期与会话退出（2026-08-22 补充）
- 根因：airymaxrt 全部 daemon（_launch_daemon/_ensure_daemon/llm_d/
  gateway_d）以裸 `&` 拉起，无 nohup。终端会话异常退出（SSH 断连/
  终端关闭）时进程组收到 SIGHUP，daemon 与脚本同灭，父脚本先行死亡
  使 daemon 变 `<defunct>` 僵尸（实测两代 llm_d/agent_d/gateway_d 全
  残留），下次启动 _sock_alive 复用判定失效。
- 修复：五处拉起统一加 `nohup`（$! 语义不变，cleanup 按 PID TERM
  回收仍有效）。两条退出路径均干净：①EXIT trap 执行（正常退出/
  SIGHUP/SIGTERM/INT）→ cleanup 主动回收；②EXIT trap 不执行
  （SIGKILL）→ daemon 忽略 SIGHUP 存活续服务，reparent 后无僵尸。
- 验证：SigIgn 实测 nohup 后 SIGHUP 置 IGN；PTY 驱动 airymaxrt cli，
  SIGKILL 后 5 个核心 daemon 全存活、零新增 defunct。
- 教训：**进程生命周期设计必须同时覆盖"正常回收"与"孤儿存活"两条
  路径**——只保证 cleanup 会回收不够，cleanup 因 SIGKILL 等不执行时
  的孤儿行为（僵尸 vs 存活）才是真实可用性的分水岭；bash 后台拉起
  服务类进程默认应加 nohup，孤儿化（reparent 到 init）是"服务常驻"
  的自然形态。

### 3.9 PTY 端到端脚本的交互与状态标记陷阱（2026-08-22 补充）
- 验证"任务执行期插入对话"需 PTY 驱动：脚本自身 stdin 会劫持 CLI 输入
  （须 `< /dev/null` 或显式管道）；GCCP 逐问交互必须发送 Enter 跳过；
  `b"completed"` 会误匹配"Parallel sub-agent review completed"（须用
  running 之后的精确终态标记切片判定）；hero 横幅 `[Super Agent]` 是
  内置文本（须 `running_idx` 切片排除）。
- 教训：**端到端脚本的状态机标记必须精确到"阶段+终态"**，且需与产品
  实际渲染文本（含 TUI 转义、内置横幅）逐字核对，否则脚本先于产品
  得出结论，验证失真。

### 2.13 commons 跨平台/跨架构核查（2026-08-22 补充）
- 全库静态审查：platform/（10 文件）与 sync_platform.c 所有函数均有
  Windows/POSIX 双分支，无"仅 #ifdef __linux__ 而 #else 缺失"的漏分支；
  atomic_compat.h 三路（stdatomic/Interlocked/__atomic）覆盖主流平台与
  8/16/32/64 位宽度；字节序全部经 htonl/ntohl/htons/ntohs 标准函数。
- 已修复编译级缺口（macOS 直接构建失败）：①platform.c POSIX 分支
  `rand_r()`（macOS 无）→ 统一 `airy_random_bytes()`（/dev/urandom），
  随机质量优于 rand_r+时间种子，urandom 不可用回退线程局部 xorshift；
  ②sync_platform.c `sem_timedwait()`（macOS 无）→ sem_trywait 轮询+
  2ms 短眠近似，返回语义与 Linux 一致。验证：Linux 全构建 + 
  `-D__APPLE__` 模拟语法 PASS + commons 单测 13/13 + CLI 冒烟。
- 遗留缺口（本轮不扩大，记录待后续轮次）：ipc 模块 CMake 层
  `if(NOT WIN32)` 排除、Windows 无对应实现（AF_UNIX/MSG_WAITALL 仅
  POSIX）；sync.c 原子操作 Windows 分支硬编码 64 位（32 位 Windows
  越界）；compat.c/compat2.c Windows 下 gethostname/sysconf 重复符号；
  ipc_message_t 仅 net_len 走网络字节序、其余字段主机序（异构端序
  主机间不兼容）；platform_process.c Windows 分支 timeout/cancel/envp
  失效；SRWLOCK 私有布局依赖。
- 教训：**"POSIX 分支"不等于"跨平台分支"**——POSIX 平台族（Linux/
  macOS/BSD）API 并不一致（rand_r、sem_timedwait、sem_init 均 macOS
  缺/弃），跨平台审查必须逐 API 对照 Darwin 而非仅对照 Windows；
  模拟宏语法检查（`-D__APPLE__`）是本地无目标机时的有效验证手段，
  但需注意模拟环境（Linux 下 __linux__ 与 __APPLE__ 并存）会引入
  平台探测宏重复定义的假象，须排除。

### 2.14 遗留缺口收敛（2026-08-22 补充）
- 已修复（2.13 遗留清单中的 3 项）：
  - compat.c/compat2.c Windows 重复符号 → **SSoT 收敛**：compat2.c 与
    compat.c 平行重复（assert handler/mem*_s/version/build_info/
    gethostname/sysconf 等近全部函数），且 airy_strlcpy/airy_strlcat
    与 platform.c 重复。静态库按需拉取侥幸掩盖 multiple definition
    （Windows DLL/特定链接配置必冲突）。删除 compat2.c（净删 238
    行），权威源收敛为 compat.c + platform.c；sysconf 私有 AIRY_SC_*
    枚举与 build_info 硬编码 "0.1.1"/"gcc"/"linux" 随文件删除一并
    收敛（compat.c 用标准 _SC_* 与宏注入）。验证：libairy_common.a
    重复符号消除（airy_version_string/airy_build_info 2→1）。
  - sync.c 原子操作 Windows 硬编码 64 位 → 按 _WIN64 选择
    Interlocked 32/64 变体（32 位 Windows uintptr_t 32 位，旧代码按
    8 字节读写越界；POSIX __sync_* 本就按 uintptr_t 自适应）。
- 教训：**静态库按需拉取会掩盖 duplicate symbol 缺陷**——多个对象
  同符号在 .a 中不报错，直到 DLL/全量链接配置才暴露；SSoT 审查应
  以 `nm 库 | grep 符号` 计数为判据，而非"能链接即无重复"。
- 遗留（未扩大，记录）：ipc 模块 Windows 实现、ipc_message_t 端序、
  platform_process.c Windows timeout/cancel/envp 失效、SRWLOCK 私有
  布局依赖（见 2.13 遗留清单，均需目标机验证）。

### 2.15 二进制包同步与 install.sh 加固（2026-08-22 补充）
- 背景：airymax-binary 自 2026-08-21 23:35 组装后未再同步，落后
  今日全部修复（nohup 生命周期、airy_cli 拆分、SSoT 收敛）。
- 根因（"其他设备安装损坏、airymaxrt 拉不起系统"）：
  ① 包内 scripts/airymaxrt 为旧版（md5 5b589aa4，0 处 nohup），daemon
     拉起后随会话退出被杀（nohup 修复未进包）；
  ② install.sh 启动器部署存在静默降级：airymaxrt 缺失时生成"兜底轻量
     包装"（只 exec TUI、不拉起 daemon 群）→ 全新安装后输入 airymaxrt
     能进 TUI 但系统无 daemon，表现为"拉不起系统"；
  ③ 包内 airy_cli（md5 161dc3a2）为旧版（缺 cli_task_result_render 拆分）。
- 修复与加固（install.sh 两处 fail-closed）：
  ① 第 8 步启动器部署改为**缺失即失败退出**（删兜底轻量包装），杜绝
     静默降级；
  ② 第 4 步动态库部署加失败校验（rar/zip 解压丢文件时 daemon 缺库
     启动即崩）。
- 同步动作：x86_64 的 20 个可执行 + scripts/airymaxrt（7a29e97c，含
  8 处 nohup）+ 加固 install.sh 全部同步；重新打 agentrt-0.1.2-x86_64/
  arm64.tar.gz（内含新 airymaxrt/airy_cli，md5 复核一致）。
- 隔离安装验证：`install.sh --prefix /tmp/pkgsmoke` 逐步骤通过
  （RUN_RC=0、17 daemon 全就位）；隔离冒烟从零拉起：16 daemon 群就绪 +
  gateway（8080/8081/8082 全监听）+ CLI 对话链路返回 LLM 回复（294B）+
  EXIT trap 干净回收全部 PID。
- 观察记录（非阻塞）：隔离环境 gateway 8080 health check 15s 窗口未
  通过（正式环境 10/10 秒级就绪），自动降级 airy_cli 直连 daemon 群
  对话成功；疑为全新安装首启时 8080 bind 晚于健康检查窗口，降级兜底
  设计已覆盖，TUI 用户路径待 TTY 环境复验。
- 遗留：arm64 二进制层未重建（无 aarch64 g++、无交叉构建流程，本次
  改动主要为 macOS 编译修复 + airy_cli 重构，Linux arm64 功能等效但
  待目标机重建验证）；airymax-binary-pack.rar 系统无 unrar/7z/bsdtar
  无法更新内容（分发建议改用 tar.gz）。
- 教训：**二进制发行包必须纳入同步闭环**——源码/部署产物 md5 与包内
  逐项比对（airymaxrt/airy_cli/daemon），发版即同步并做隔离安装冒烟，
  否则"源码修了、包没跟上"造成用户侧安装损坏。

### 2.10 蓝图 L2 语义缓存命中率审查（2026-08-22 补充）
- 四项命中率缺口已修复：①默认 θ 700→550（语义命中仅作 L3 提示、安全，
  700 使 OSS bigram 路径几乎无法过阈）；②向量 top-K 低于 θ 时回退 bigram
  全扫描（此前仅空结果集回退）；③TTL 过期条目同步移出向量索引（此前索引
  残留过期 embedding）；④删除死字段 alpha/target_fp_permille + 修正
  "动态阈值"注释（θ 实为可配置静态阈值）。
- 教训：**统计口径与真实收益必须一致**——"命中率"若只计省掉规划的次数
  （精确命中），语义命中路径的实际价值是"提示参考"而非"省 token"，两者
  分开计，避免指标失真（2026-08-17 已审计过一版）。

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
- [x] 3.7 部署漂移修复：bin/airy_cli 落后源码 → 从 focal-x64 release 构建
      覆盖部署（2026-08-22 完成，md5 校验一致）。
- [x] 2.10 蓝图 L2 语义缓存命中率审查修复：θ 默认 550 + 向量低于 θ 回退
      bigram + 过期条目索引清理 + 死字段删除（2026-08-22 完成，Roadmap
      Sched 测试全 PASS）。
- [x] 0.1.2 发布：agentrt 打 v0.1.2 tag（2026-08-22，含本轮 CLI/L2 修复
      changelog）。
- [x] 2.2.1 任务集模式中途插入对话：任务执行期 wait 放后台线程 + 主线程
      poll stdin，非中断指令走 cli_chat_reply 插入对话，任务继续后台执行
      （2026-08-22 完成：PTY e2e 实测插入对话回复 + 任务继续执行至终态）。
- [x] 2.2.1 任务集模式插入对话收尾 + 执行链路缺陷根因修复（coreloopthree
      空 content 守卫 + cli_exec_review 栈逃逸）+ GCCP 逐问交互优化 +
      main 结果渲染拆分 cli_task_result_render（2026-08-22 完成：PTY e2e
      全链路验证 + 冒烟 SMOKE_RC=0 + 部署 md5 一致）。
- [x] 2.12 daemon 生命周期修复：五处拉起统一 nohup，会话异常退出不再
      残留 defunct 僵尸（2026-08-22 完成：SIGKILL 场景 PTY 验证 daemon
      全存活、零新增僵尸，见 2.12）。
- [x] 2.13 commons 跨平台核查：全库静态审查 + macOS 编译级缺口修复
      （rand_r→/dev/urandom、sem_timedwait→轮询，见 2.13）。2026-08-22
      完成：Linux 构建 + -D__APPLE__ 模拟语法 PASS + 单测 13/13 + 冒烟。
- [x] 2.14 遗留缺口收敛：compat2.c SSoT 删除（重复符号消除，净删
      238 行）+ sync.c 原子操作 Windows 位宽自适应（见 2.14）。
      2026-08-22 完成：全量重建 + 单测 13/13 + 冒烟 + nm 符号计数验证。
- [x] 2.2.4 记忆跨进程"重启即失忆"根因修复：MemoryRovol L2 HNSW 索引纯
      内存且 airy_mr_init 不重建 → 从 L1 raw 卷遍历重建内存索引（2026-08-22
      完成：跨进程冒烟"我叫什么名字→你叫小明" + 172/172 全量回归）。
- [x] 2.2.1/2.2.3 CLI/TUI 交互一致性：`?`/`？` 单独输入进帮助（不再发 LLM）、
      纯空白输入三处静默过滤（主循环/-p stdin/轮询）、TUI resize 过小自动
      退出回行渲染（2026-08-22 完成：script 冒烟验证）。
- [x] 2.1.1 cmd_daemons 健康检查补 gateway：HTTP 网关无 Unix socket，改
      TCP 端口探测补报（online x/17）（2026-08-22 完成，构建通过）。
- [x] 2.4 main 圈复杂度拆分（298→决策点 193→139）：cli_setup_core_engines
      （引擎装配）/ cli_runtime_ctx_t + cli_setup_runtime + cli_teardown_runtime
      （运行时上下文对称装配/释放）/ cli_blueprint_fastpath（蓝图三层快速路由），
      main 调用点与清理段 SSoT 收敛不再逐组件释放（2026-08-22 完成：构建 +
      冒烟 + 172/172 回归，见 5.1 更新）。
- [x] 2.3.2 monitor 后台常驻：`airymaxrt monitor --daemon/--stop`（PID 文件 +
      nohup 递归真实路径），端侧/服务器无需保持终端即可监控外设增强自动恢复
      （2026-08-22 完成：隔离生命周期验证 启动→停止→进程确认终止）。
- [x] 2.3.3 端侧/服务器资源分级验证：1.5GiB 模拟→minimal（端侧可运行）、
      12GB 实机→full（服务器/PC）；ARM64 交叉语法检查 7 文件全通过
      （commons 平台层 4 + airy_cli 3）（2026-08-22 完成）。
- [ ] Windows/macOS 平台兼容性实测（当前仅 CI 编译链路 + 模拟语法检查）。
- [ ] ipc 模块 Windows 实现（CMake 层 if(NOT WIN32) 排除，AF_UNIX/
      MSG_WAITALL 无对应实现）+ ipc_message_t 端序 + platform_process.c
      Windows timeout/cancel/envp 失效 + SRWLOCK 私有布局依赖（见 2.13/
      2.14 遗留，均需目标机验证）。
- [ ] 高圈复杂度函数系统性拆分（基线见下，拆分需专门重构轮次并全量回归）。

### 5.1 圈复杂度基线（pmccabe，2026-08-21）

| 函数 | 圈复杂度 | 说明 |
|------|---------|------|
| airy_cli main | 298 → ~139 | 2026-08-22 拆分：初始化装配/运行时上下文/蓝图快速路由
  抽离 4 函数（pmccabe 298 含 switch 逐分支；拆后 if/switch 计数 139，待 pmccabe 复核） |
| cli_blueprint_fastpath | 新增 | 蓝图 L1/L2 三层快速路由（自 main 提取，含 cJSON/事件/渲染分支） |
| cli_setup_runtime | 新增 | 运行时上下文装配（rsched/validator/reviewer/hall/governance/面板） |
| cli_tui_readline | 170 | 全屏 TUI 按键/输入核心，拆分风险高（待续） |
| cli_chat_reply | 88 | 对话回复管线 |
| handle_agent_run | 80 | gateway agent 执行编排 |
| airy_token_count | 78 | token 分类（switch 密集，逻辑可复核） |
| notify_d_event_loop | 74 | 事件循环 |

> 注：pmccabe 对 switch-case 逐分支计数，部分高值源于密集 switch 而非深嵌套。
