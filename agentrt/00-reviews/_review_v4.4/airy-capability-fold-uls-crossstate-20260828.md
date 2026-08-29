# agentrt-linux Capability 模型 / Capability Folding / A-ULS 跨态复用研究报告

> **报告编号**：REVIEW-AGENTRT-2026-08-28-CAPULS
> **报告类型**：跨态复用研究（内核态设计 → 用户态插件系统）
> **研究对象**：agentrt-linux（AirymaxOS）三大设计——Capability 模型（`03-capability-model.md`）、Capability Folding（`02-ipc-protocol.md` + `07-ipc-fastpath.md`）、A-ULS 统一生命周期管理（`09-kernel-agent-supervisor.md` + `10-user-supervisor-daemon.md`）
> **对照对象**：agentrt 用户态插件系统设计（统一扩展机制 + gateway 统一能力网关 + 插件生命周期）
> **核心问题**：这三设计有可借鉴/可复用之处吗？"依赖图自动决定加载顺序"是否真重要？
> **产出目录**：`docs-closed/agentrt/00-reviews/_review_v4.4/`
> **审查日期**：2026-08-28
> **状态**：开发准备研究

---

## 摘要

**结论一：有大量可复用之处，而且是"同源跨态复用"——不是外部借鉴。** Capability 模型 / Capability Folding / A-ULS 都是 agentrt-linux（自家内核态）的设计，agentrt 复用它们完全符合 IRON-9「同源且部分代码共享」与 SSoT「[SS] 语义同源层」的既定框架，**无任何抄袭顾虑**。可复用的是"模式层"（权限位图、epoch 撤销、校验链分层、自举、单写者多读者、双 Supervisor、生命周期状态机、心跳分级），不可复用的是"物理机制层"（io_uring fastpath、kfifo、READ_ONCE、Badge 位布局——H3 明文 agentrt badge 恒为 0）。

**结论二：依赖图自动决定加载顺序——你的判断是对的，而且比 agentrt-linux 自己的 A-ULS 更超前。** 深度核查发现：agentrt-linux 的 A-ULS（Macro-Supervisor）自身用的就是**手写依赖顺序**（`daemons[]` 数组 + §2.3 文档化顺序）；agentrt 用户态 airymaxrt 启动器同样手写 `_launch_daemon` 序列 + `WAIT_SOCKS` 手工等待。**三个参考对象里只有 dsh 真正实现了"依赖声明 → 自动解析加载顺序"**。而 agentrt 的 `WAIT_SOCKS` 机制（等 socket 就绪）恰恰就是"依赖就绪等待"的雏形——升级路径清晰：daemon manifest 声明 `depends_on` → 启动器拓扑排序（Kahn）+ 环检测 → 与 WAIT_SOCKS 融合。且 v4.3「先能跑再抽象」的前置条件已满足（0.1.5 生产安装已验证 18 daemon 启动），**现在正是落地时机**。

---

## 一、研究输入与现状核对

| 对象 | 权威文档 | 关键状态警示 |
|------|---------|-------------|
| Capability 模型 | `docs/AirymaxOS/110-security/03-capability-model.md`（2368 行） | **设计契约超前于实现**：§2.6 核实 `kernel/security/airy/capability.c` 不存在，opcode→required_perms 映射待 M2 |
| Capability Folding | `docs/AirymaxOS/30-interfaces/02-ipc-protocol.md`（1261 行）+ `07-ipc-fastpath.md`（1514 行） | **fastpath 实际仅 91 行**（`airy_ipc_fastpath_send()` = frozen 门 + 委托 ring_post），C-S0~C-S12 校验链为设计稿（§5.2 L382） |
| A-ULS | `09-kernel-agent-supervisor.md`（788 行）+ `10-user-supervisor-daemon.md`（1533 行） | Micro-Supervisor（内核冷酷执法）已设计；Macro-Supervisor（用户温情裁决）含 systemd 拉起/心跳/裁决全流程 |
| agentrt 用户态现状 | `plugin_d/`（plugin_permission.c 16 项权限）、`gateway_d/`（16 命名空间白名单）、`cupolas/safety_guard.h`、`airymaxrt` 启动器 | plugin_d 权限**加载时一次裁决、运行时不再校验**；守卫 V2 API 被 `AIRY_ENABLE_V2_API` 宏门控；启动顺序手写 |

> **重要前提**：本次研究评估的是 agentrt-linux 的**设计契约**的可复用性（设计层面跨态复用的价值），而非已验证实现的复用。

---

## 二、Capability 模型：可复用性评估

### 2.1 机制要点（提炼）

- **cap_t 即 token**：64-bit 不透明令牌，无句柄索引；CNode 槽位 `aligned(64)` + refcount + expires_ns。
- **capability_badge 64-bit Native Word**：`Epoch(16) | RandomTag(32) | Perms(16)`，物理载体在 [SC] `ipc.h` offset 40-47。
- **Perms 16-bit 权限位图**：7 个有效位（SEND/RECV/DERIVE/KILL/FILE_OPEN/ROTATE/SUPERVISE），bits 7-15 必须为零；**严格包含语义** `(perms & required) == required`（超集允许）。
- **1 opcode → 1 required_perms**：SEND_BATCH/CANCEL 复用 SEND；CAP_REQUEST/CAP_RESPONSE → 0（自举无需权限）；非法 opcode → 0xFFFF。
- **撤销 = 代际失效**：per-agent epoch bump（`airy_cap_epoch_bump` 一行 atomic_inc），沿 MDB 派生树递归级联；旧 Badge 因 Epoch 不匹配失效，可恢复（重新 mint）。
- **CAP_REQUEST 自举**：无凭证请求凭证，**且仅允许发往 sec_d**。
- **单写者多读者**：`agent_caps[1024]` 静态数组，sec_d 唯一写者，fastpath READ_ONCE 零锁读。
- **令牌 7 态**：CREATED→ACTIVE/DERIVED/USED/TRANSFERRED/REVOKED/EXPIRED/DENIED。

### 2.2 可复用（模式层，跨态移植）

| 机制 | 落到 agentrt 的形态 | 价值 |
|------|--------------------|------|
| **16-bit 权限位图** | agentrt plugin_d **恰好有 16 项权限**（file_read/file_write/.../audit_trigger）→ 直接映射 `uint16_t cap_bits`，字符串比较（strcmp 链）改位掩码检查 | 高：改动小（`plugin_permission.c` 映射表位索引化），测试全保留 |
| **opcode→required_perms 严格包含** | gateway `<daemon>.<method>` 白名单升级为"方法→所需能力位"映射表，`(bits & required)==required` | 高：比现白名单更细粒度 |
| **per-subject epoch 撤销** | 插件配置/版本更新时 bump per-plugin epoch，旧凭证自动失效 | 高：补"运行时撤销"空白 |
| **CAP_REQUEST 自举** | 插件 install 时经 plugin_d→cupolas_d 申请能力清单，"无凭证仅可向授权方请求" | 中 |
| **校验链分层（廉价在前）** | gateway 派发链：方法白名单（O(1)）→ 身份 → 能力位 → 业务 | 高：性能安全兼顾 |
| **单写者多读者缓存** | plugin_d 持有能力表唯一写者；其他 daemon 只读快照（C11 atomic/pthread_rwlock 读锁） | 中：避免每次调用跨 daemon 查询 |
| **级联撤销（MDB 树思想）** | 插件 A 依赖 B 的能力，A 撤销时 B 的受限能力同步失效 | 低：先记思想，单层撤销够用 |
| **审计联动** | 连续权限失败 → cupolas_d 冻结该插件调用（emergency_stop 已有） | 中 |

### 2.3 不可照搬（物理机制层）

| 机制 | 原因 |
|------|------|
| Badge 位布局（offset 40-47） | **H3 硬约束：agentrt 用户态 capability_badge 恒为 0**；且 `src_task` 用户态可伪造，RandomTag 防伪锚点不成立 |
| io_uring / kfifo / READ_ONCE / RCU | Linux 内核专属原语；用户态需 C11 atomics 等价（语义级别不同） |
| `agent_caps[1024]` 静态数组 | 依赖内核私有内存 + `src_task` 不可伪造 |
| syscall 12→4 | 用户态无 syscall 收敛问题；对应物是"统一经 gateway 派发"（已落地） |

> **关键差距（agentrt 现状）**：plugin_d 权限是"加载时一次裁决，运行时不再校验"——缺 Capability 模型的核心："凭证随调用携带、每次调用校验、可撤销"。守卫 V2 API 还被宏门控。这是本次研究最有价值的落地点。

---

## 三、Capability Folding：可复用性评估

### 3.1 机制要点

- **核心论断**："IPC 不是承载能力校验——IPC 就是能力校验"。把 capability check 从独立控制面 syscall **折叠进 IPC 数据面 fastpath** 单次 64-bit 比对（~10ns）。
- **校验链 C-S0~C-S12**：廉价在前（frozen→magic→opcode→payload_len→hdr_size→同CPU→kfifo满→reclaim→in_task→**C-S9 Badge**→flags→preempt→CRC32）。C-S9 内部三子查：EPOCH→RANDTAG→PERMS（顺序固定）。
- **接收方不重复校验**（C-R1~R5）：通过 C-S9 的消息已具备合法能力。
- **syscall 12→4**：权限传递走数据面（CAP_CARRY + fastpath）、查询走 sysctl、自举走 opcode、仅"编译/撤销/策略/装载"4 类特权操作保留 syscall 且仅限 sec_d。
- **数据结构隔离三原则**：能力数据 / 投递缓冲 / 通信原语三个独立内存区域，更新路径独立、失败域独立。

### 3.2 对 agentrt 用户态的意义（印证 + 边界）

**印证**（支持 gateway 统一能力网关方向）：
1. "校验折叠进唯一调用路径"是 agentrt-linux 自己的核心决策（§12.5.3：fastpath C-S9 是唯一执行点）。agentrt gateway 统一派发 = 用户态的"唯一调用路径"，把能力校验折叠进 gateway 派发链与 Folding **同构**。
2. `<daemon>.<method>` = 用户态 opcode，required_perms 映射可直接落地。
3. CAP_REQUEST 仅限 sec_d → 用户态"能力申请仅限 cupolas_d"。
4. 数据结构隔离三原则 → 能力表唯一写者（cupolas_d）+ 只读消费者（gateway 派发路径）用读写锁/原子快照。

**边界**（必须遵守）：
1. **H3 硬约束**：Badge 位布局不能进 agentrt。统一入口应实现为**用户态能力令牌**（语义同源 [SS]、物理独立 [IND]），不复制 Badge 位。
2. **"IPC 就是能力校验"前提在用户态不成立**：用户态 socket 可被绕过（daemon 直连、dlopen 内存内调用）。统一入口必须靠**架构约束强制执行**（禁直连 daemon socket）。
3. **gateway 单点故障**：不能做成无缓存无状态单点。应保留"离线缓存校验 + Reconciliation"（插件已获能力在 gateway 恢复前仍可裁决）。

### 3.3 用户态最小落地（Capability Folding 用户态镜像）

```
gateway 派发链（对应 C-S0~C-S12）：
  ① 方法白名单（O(1) 表查，fail-closed）      ← C-S0/S-S1 级
  ② 调用者身份校验（进程身份 + SO_PEERCRED）  ← C-S9 的 src_task 锚点替代
  ③ 能力位检查 (bits & required)==required     ← C-S9.PERMS 用户态版
  ④ 插件 epoch 校验（撤销即时生效）            ← C-S9.EPOCH 用户态版
  ⑤ 业务派发 + 事件流埋点
```

---

## 四、A-ULS 统一生命周期管理：可复用性评估

### 4.1 机制要点

- **双 Supervisor 模型**：Micro-Supervisor（内核态，冷酷执法：检测→冻结→通知，借鉴 seL4 handleFault）+ Macro-Supervisor（用户态，温情裁决：通知→查询上下文→裁决：警告/降级/暂停/终止）。
- **Agent 8 态生命周期**：INACTIVE→SPAWNING→READY→RUNNING→BLOCKED→STOPPING→STOPPED→DEAD，与 Linux 进程状态天然映射，sched_d 联动调度预算冻结/恢复。
- **心跳检查三档**：进程存活（kill -0，1s/3 次失败重启）、心跳消息（eventfd，5s/15s 降级）、响应探测（ping，10s/30s 终止）。
- **sec_d 故障恢复**：Snapshot + WAL 两阶段恢复（§4.7）。
- **依赖顺序**：§2.2 `daemons[]` 数组手写顺序 + §2.3 文档化依赖链（logger→config→mem→sec→cogn→其余）。

### 4.2 可复用（模式层）

| 机制 | 落到 agentrt 插件系统 |
|------|----------------------|
| **双 Supervisor 模型** | plugin_d/cupolas_d = "冷酷校验"（契约/权限 fail-closed）；开发者/配置 = "温情扩展"（策略）。机制/策略分离在生命周期域的落地 |
| **8 态生命周期 → 插件状态机** | `airy_ext_state`：REGISTERED→ENABLED→ACTIVE→FAILED→DISABLED→REMOVED，与 Agent 8 态同构（跨态同一套语义，[SS] 层共享） |
| **心跳三档检查** | 插件健康检查：进程存活（kill -0）→ 心跳（IPC ping）→ 响应（业务探测），分级处置（重启/降级/停用） |
| **裁决策略矩阵**（警告/降级/暂停/终止） | 插件故障处置：告警/降级（限流降权）/暂停（冻结调用）/移除 |
| **Snapshot + WAL 恢复** | 插件能力表/注册表持久化：全量快照 + 变更 WAL，恢复后对账（与 Capability 模型的对账合并） |
| **systemd 单元管理** | 插件生命周期由 plugin_d 承载（复用 daemon 生命周期管理），不新造 |

### 4.3 重要发现：A-ULS 自身也用"手写依赖顺序"

Macro-Supervisor 拉起 12 daemon 的方式是：
```c
static const struct daemon_spec daemons[] = {   /* §2.2：手写数组，顺序即启动顺序 */
    { "logger_d", ... }, { "config_d", ... }, { "mem_d", ... },
    { "sec_d", ... }, { "cogn_d", ... }, /* ... */
};
/* §2.3：依赖链是"文档化"的，不是"可执行"的：
 * logger → config → mem → sec → cogn → 其余
 */
```

**这意味着：agentrt-linux 自己的 A-ULS 也没有实现"依赖图自动解析"**——依赖顺序靠数组顺序 + 文档约定保证。这是本报告对用户主张最有冲击力的证据。

---

## 五、深度回应："依赖图自动决定加载顺序"（你的主张）

### 5.1 三个参考对象的现状对照

| 对象 | 加载顺序机制 | 是否自动 |
|------|-------------|---------|
| **dsh（Cordis）** | 插件 `inject: ['tools']` 声明依赖，Fiber `_refresh()` 等依赖服务就绪才激活 | ✅ **自动**（依赖图驱动） |
| **agentrt-linux A-ULS** | `daemons[]` 手写数组顺序 + §2.3 文档化依赖链 | ❌ 手写 + 文档 |
| **agentrt 用户态 airymaxrt** | `_launch_daemon` 手写调用序列 + `WAIT_SOCKS=('名称|socket路径')` 手工等待就绪 | ❌ 手写 + 手工等待 |

**三个对象里只有 dsh 真正实现了自动依赖解析。** 你的判断指向了 agentrt（用户态）和 agentrt-linux（内核态）共同的真实短板。

### 5.2 为什么它重要（现状痛点）

1. **airymaxrt 启动器**：每个新 daemon 要手写一行 `_launch_daemon` + 手写 `WAIT_SOCKS` 登记 + 手动排入启动序列——**依赖关系隐式**，加 daemon 改脚本，顺序错乱难以排查。
2. **A-ULS**：`daemons[]` 数组顺序即启动顺序，但依赖链只写在注释/文档里——**顺序与依赖脱节**，改顺序要人肉核对文档。
3. **dsh 证明可行**：`inject` 声明 + 依赖图驱动加载，插件作者只声明"我要什么"，框架负责"什么时候给我"——心智负担大幅降低，且天然环检测、天然可并行（无依赖的插件并发激活）。

### 5.3 关键洞察：agentrt 已有雏形——`WAIT_SOCKS` 就是"依赖就绪等待"

airymaxrt 的 `WAIT_SOCKS=('llm_d|$RUNTIME_DIR/llm.sock')` + `wait_all_socks` 已经实现了"**等依赖的 socket 就绪**"——这在语义上就是 dsh `inject`（等依赖服务就绪）的**跨进程等价物**。缺的只是：
- 依赖关系从"脚本里手写"提升为"**manifest 声明**"；
- 启动顺序从"人肉排列"提升为"**拓扑排序自动计算**"。

### 5.4 轻量落地路径（不引入完整 DI 容器）

```yaml
# 每个 daemon / 插件的 manifest 新增字段（airy_dep_contract 落地）
depends_on:
  - llm_d
  - mem_d
```

```
启动器流程：
① 扫描全部 manifest → 收集 depends_on 依赖边
② 构建依赖 DAG → Kahn 拓扑排序 → 环检测（有环即 fail，报环路径）
③ 无依赖的 daemon 并发拉起（现有并行逻辑保留）
④ 有依赖的按拓扑序：依赖的 socket 就绪（现有 WAIT_SOCKS 机制）才拉起
```

- **改动量小**：`WAIT_SOCKS` 机制保留，只是从"手写登记"变为"从 manifest 生成"；
- **收益大**：加 daemon 不用改启动脚本、依赖关系可机器校验、环检测提前暴露配置错误、启动可观测（谁等谁一目了然）；
- **边界**：不是完整 DI 容器（不注入配置/不生命周期委托），只是"依赖声明 + 拓扑排序 + 就绪等待"——对 daemon 架构足够，不过度设计。

### 5.5 我的判断

**你的主张成立，且时机已到。** v4.3 把"服务按 key 查找 + 依赖注入"判为 P2 后置，理由是"先手写启动顺序跑通，再抽象"——**现在 0.1.5 已验证 18 daemon 生产安装启动，'先能跑'前提已满足**。轻量拓扑排序版本（manifest 声明 + Kahn + WAIT_SOCKS 融合）成本低、收益直接，应提前到 P1 落地，不必等完整服务注册表（P2）。

---

## 六、综合融入方案（三设计 → 插件系统贡献点，agentrt 命名）

| 三设计贡献 | agentrt 命名落地 | 优先级 |
|-----------|-----------------|--------|
| 16-bit 权限位图 + 严格包含语义 | `plugin_permission` 升级：字符串 → `uint16_t cap_bits` + `(bits & required)==required` | P0 |
| 调用路径能力校验（Folding 用户态镜像） | gateway 派发链注入能力检查点（方法白名单→身份→能力位→epoch） | P0 |
| per-subject epoch 撤销 | 插件 `airy_ext_epoch`：更新/卸载 bump，旧凭证即时失效 | P1 |
| 单写者多读者缓存 | plugin_d 能力表唯一写者 + 只读快照 | P1 |
| 双 Supervisor 模型 | plugin_d/cupolas_d 冷酷校验 + 开发者温情扩展（机制/策略分离） | P1 |
| 8 态生命周期 → 插件状态机 | `airy_ext_state`（REGISTERED/ENABLED/ACTIVE/FAILED/DISABLED/REMOVED） | P1 |
| 心跳三档 + 裁决策略矩阵 | 插件健康检查（kill-0/心跳/响应）+ 处置（告警/降级/暂停/移除） | P1 |
| **依赖声明 + 拓扑排序** | manifest `depends_on` + Kahn 排序 + 环检测 + WAIT_SOCKS 融合 | **P1（提前）** |
| 离线缓存校验 + Reconciliation | 能力表对账 + 控制面离线期间缓存裁决 | P2 |
| Snapshot + WAL 恢复 | 插件注册表/能力表持久化两阶段恢复 | P2 |

**命名红线**：以上全部为 agentrt 自身命名（`airy_*` / `cap_bits` / `airy_ext_state` / `depends_on`），与 agentrt-linux 同源（[SS] 语义同源层），不引入外部术语。

---

## 七、结论

1. **有大量可复用之处**：Capability 模型的权限位图/epoch 撤销/校验链分层/自举/单写者多读者、Capability Folding 的"校验折叠进唯一调用路径"、A-ULS 的双 Supervisor/8 态生命周期/心跳分级——全部可跨态复用到 agentrt 插件系统。且这是**同源复用**（IRON-9 [SS] 层），无抄袭顾虑。
2. **最值得先做**：plugin_d 权限从"加载时一次裁决"升级为"16-bit 位图 + 每次调用校验 + epoch 可撤销"——这是 Capability 模型 + Folding 在用户态的最小落地，也是 gateway 统一能力网关的地基。
3. **你的依赖图主张成立且时机成熟**：三个参考对象中仅 dsh 实现了自动依赖解析；agentrt 的 WAIT_SOCKS 已是雏形；升级为"manifest depends_on + 拓扑排序 + 环检测"成本低收益高，应从 P2 提前到 P1。
4. **不可照搬的边界**：Badge 位布局（H3）、io_uring/kfifo/RCU 等内核原语、用户态"IPC 即校验"前提（需架构约束强制唯一路径）。

---

## 附：证据来源索引

- Capability 模型：`docs/AirymaxOS/110-security/03-capability-model.md`（cap_t/CNode §2.1、Badge 位布局 §2.5、opcode→perms §2.6.1-2.6.4、派生操作 §3、syscall 12→4 §9、令牌生命周期 §5、H1-H6 §12.5、K9-1 缺陷 §15.2）
- Capability Folding：`docs/AirymaxOS/30-interfaces/02-ipc-protocol.md`（Badge 模型/H1-H6 §2.6）、`07-ipc-fastpath.md`（C-S0~C-S12 §3.1、fastpath 91 行现状 §5.2、CBMC 规划态 §10）
- 数据面自治：`docs/AirymaxOS/110-security/04-ipc-data-plane-autonomy.md`（Ring 解耦 §2、离线缓存 §3、Reconciliation §4）
- A-ULS：`docs/AirymaxOS/20-modules/09-kernel-agent-supervisor.md`（Micro-Supervisor 全篇）、`10-user-supervisor-daemon.md`（systemd 拉起 §2.1、daemons[] 数组 §2.2、依赖顺序 §2.3、心跳 §3、Snapshot+WAL §4.7、裁决矩阵 §5）
- Unify Design：`docs/AirymaxOS/10-architecture/10-unify-design.md`（五模块 §2、四大领域 §3、A-ULS §7、A-IPC §8、SSoT 声明 §10）
- agentrt 现状：`agent-workload/agentrt/daemons/plugin_d/`（plugin_permission.c 16 权限）、`daemons/gateway_d/`（命名空间白名单）、`cupolas/include/safety_guard.h`（V2 宏门控）、`sdk/tui/scripts/airymaxrt`（_launch_daemon + WAIT_SOCKS）
- 外部对照：dsh `vendor/cordis/src/fiber.ts`（inject 依赖等待）、`docs/capability-seams.md`
- 历史决策：`_review_v4.3/`（0.1.2-unify-plan：依赖注入 P2 后置；reversal-slimming：先能跑再抽象）
