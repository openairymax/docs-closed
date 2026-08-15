# DeepSeek Harness 源码级工程设计对标分析报告

> **报告编号**：REVIEW-AGENTRT-2026-08-14-B（源码级深入版）
> **报告类型**：标杆工程源码级对标分析（逐文件深读）
> **研究对象**：`deepseek-harness-master`（`dsh`，逐文件阅读 `packages/core/*`、`packages/shell/*`、`scripts/*` 源码）
> **对照对象**：`agentrt`（AirymaxRT 0.1.1，逐文件阅读 `atoms/*`、`cupolas/*`、`daemons/*` 源码）
> **产出目录**：`closed-docs/agentrt/00-reviews/_review_v4.3/`
> **审查日期**：2026-08-14
> **审查人**：SPHARX 工程标准组
> **前置报告**：本报告是 `deepseek-harness-philosophy-20260814.md`（架构级分析）的**源码级深化版**，两者互补：前一份回答「有哪些思想可吸取」，本份回答「这些思想在源码里如何实现、agentrt 如何等价落地」。

---

## 摘要

本报告对 deepseek-harness 的 `session`/`agent-loop`/`tools`/`scope`/`shell` 五大核心包与 `scripts/` 工程门禁做了**逐文件源码级阅读**，并对 agentrt 的 `atoms/corekern`/`coreloopthree`/`memory`/`syscall`/`taskflow` 与 `cupolas` 做了对应级阅读。

**源码级核心结论**：

1. agentrt 的 `memory_provider.h`（17 槽函数指针表 + `capabilities` 位图 + `set_active` 热切换）**已经是 DeepSeek capability seam 的 C 语言等价物**，但只覆盖 memory 一个能力域，且注册到「全局单例」而非「按 key 查找的 context」。
2. deepseek 的「单一真相源事件流」机制（`seq = log.length` 全局连续 + `surfaceOp` 投影 + `deriveMessages()` + `JSON.stringify` 逐字节断言「模型可见 ⟺ 已记录」）是 agentrt 最值得吸取、但当前**完全缺失**的机制。
3. deepseek 的「运行时 invariant companion」模式（每个 package 有 `invariant.ts`，注册到 `ctx.invariants` 做关系断言）是 agentrt 工程纪律中最值得补的一环——agentrt 有编译期 `_Static_assert`，但缺运行时关系不变量。
4. deepseek 的「每文件 100% 覆盖率门禁 + Agent Note + 字数控预算 + 机器可检查死链」四项工程纪律，是 agentrt 文档与测试体系当前最直接、收益最高的借鉴点。

---

## 一、源码级研究范围与方法

### 1.1 deepseek-harness 逐文件阅读清单（51 packages 中的核心）

| 包 | 已读文件 | 核心机制 |
|----|---------|---------|
| `core/session` | `types.ts` / `invariant.ts` / `surface.ts` / `chunk-rows.ts` / `repair.ts` / `json.ts` / `index.ts` | 单一真相源事件流 |
| `core/agent-loop` | `agent.ts` / `tool-calls.ts` / `invariant.ts` / `index.ts` | turn/step 状态机 |
| `core/tools` | `schema.ts` / `code-mode.ts` / `presentation.ts` / `json-schema.ts` / `index.ts` | 工具 schema DSL |
| `core/scope` | `store.ts` / `index.ts` / `invariant.ts` | per-agent 作用域 shadowing |
| `shell/*` | `shell`/`bash-local`/`bash-sandbox`/`tool-bash`/`shell-env` | capability seam 三角色 |
| `util/brand` / `llm` | `brand.ts` / `never.ts` | 品牌化 ID / 穷尽性 |
| `scripts/` | `run-gates.ts` / `verify-md-links.ts` / `verify-doc-budgets.ts` / `verify-agent-note-format.ts` | 工程门禁 |
| 根配置 | `vitest.config.ts` / `tsconfig.base.json` / `.oxlintrc.json` / `knip.json` | 覆盖率 / 类型安全 |

### 1.2 agentrt 逐文件阅读清单（~1285 源码文件中的核心）

| 模块 | 已读文件 | 核心机制 |
|------|---------|---------|
| `atoms/corekern` | `are_ipc.h` / `ipc.h` / `mem.h` / `arena.h` / `mempool.h` / `slab.h` / `tcache.h` / `refcount.c` | IPC + 四层内存 |
| `atoms/coreloopthree` | `loop.h` / `cognition.h` / `orchestrator.h` | 三循环 DAG |
| `atoms/memory` | `memory_provider.h` / `builtin_provider.c` | 可拔插 provider |
| `atoms/syscall` | `syscalls.h` / `syscall_table.c` / `airy_sandbox.h` | syscall 分发 + 保护环 |
| `atoms/taskflow` | `taskflow.h` / `pregel_engine.h` | Pregel DAG |
| `cupolas` | `cupolas.h` / `permission_engine.c` / `permission_rule.c` / `sanitizer_core.c` | RBAC + 净化 |

---

## 二、deepseek 的七项源码级核心机制（含签名）

### 2.1 单一真相源事件流（session 包）

```ts
// types.ts —— SessionEvent 是判别联合（discriminated union）
export type SessionEvent<T extends SessionEventType = SessionEventType> = {
  [K in SessionEventType]: { type: K; seq: number; time: number; data: SessionEventMap[K]; ignorable?: true }
  & (K extends SurfaceEventType ? { sourceEventSeqs?: number[]; surfaceOp?: SurfaceOp } : object)
}[T]

// index.ts —— seq = log.length 是全局连续性契约
append<T>(type, data, ...opts): SessionEvent<T> {
  const event = deepFreeze({ type, seq: this.log.length, time: Date.now(), data, ...surfaceMetadata })
  this.surfaceManager.validateNext(event)   // 先验证
  this.log.push(event)                       // 再提交
}

// surface.ts —— 派生视图：只有 surfaceOp 标记的事件进入模型历史
export function deriveEventMessage(event: SessionEvent): Message | null {
  switch (event.type) {
    case 'user/message': return event.data
    case 'assistant/message': return event.data.message.content.length === 0 ? null : event.data.message
    case 'tool/result': return event.data.message
    default: return null   // chunk / 边界 / 日志-only 事件投影为 null
  }
}
```

**关键机制**：`Session.log` 是 append-only 单一真相源；`surfaceOp` 标记（`'append'` 或 `{op:'replace',start,end}`）决定哪些事件进入 `surface.nodes`（有序 seq 数组）；`deriveMessages()` 只对该数组做投影，非 surface 事件（chunk、turn/start 等）天然不进模型历史。

### 2.2 「模型可见 ⟺ 已记录」运行时断言（agent-loop/invariant.ts）

```ts
// 核心：发往 LLM 的 messages 必须与从日志派生的历史逐字节相等
const expected = session.deriveMessages()
if (JSON.stringify(options.messages) !== JSON.stringify(expected)) {
  fail('llm request diverges from the dispatch-time durable derivation (log-reconstruction desync)')
}
```

这是**运行时强制**（不是约定）：任何 `llm/stream` 请求，其 `messages` 数组必须等于 `session.deriveMessages()` 的 JSON 序列化。违反即中止请求。

### 2.3 turn/step 生命周期状态机（agent-loop/agent.ts）

```ts
type Phase =
  | { kind: 'idle'; lastTurn: number }
  | { kind: 'maintenance'; abort: AbortController; lastTurn: number; wakeRequested: boolean }
  | { kind: 'running'; abort: AbortController; turn: number; step: number; wakeRequested: boolean }
```

`turn()` 方法：`turn/start` → 循环内 `agent/pre-step` waterfall（决定 enter/reject）→ `step/start` → `user/message` → `assistant/chunk*` → `assistant/message` → `tool/call` → `tool/result` → `step/end` → … → `turn/end`（finally 无条件写入）。

### 2.4 capability seam 三角色（shell 包）

```ts
// Service Definition：抽象类（非 interface），构造时自注册
export abstract class ShellExecutor extends Service {
  constructor(ctx: Context) { super(ctx, 'shell') }   // 运行时自注册为 ctx.shell
  get sandboxMode(): SandboxMode | undefined { return undefined }  // 默认成员
  abstract resolve(request: ShellExecRequest): ShellExecSpec
  abstract run(spec: ShellExecSpec): Promise<ShellRunResult>
  abstract start(spec: ShellExecSpec): ShellProcess
}

// Provider：继承抽象类即完成注册
export class LocalBashExecutor extends ShellExecutor {
  static inject = ['subprocess']   // 声明式依赖注入
}
export class SandboxBashExecutor extends LocalBashExecutor {
  static override inject = ['subprocess', 'sandbox', 'sandboxPolicy']
}

// Consumer：声明式注入 + 注册工具
export const inject = ['tools', 'shell', 'systemPrompt', 'shellEnv']
```

**关键**：抽象类（而非 interface）用于承载运行时自注册 `super(ctx,'shell')` + 默认成员 + 重复服务约束；Provider 分层（`bash-local` 提供进程机制，`bash-sandbox` 叠加沙箱策略）。

### 2.5 scope shadowing（scope/store.ts）

```ts
// 最具体优先：chainLayers 返回「最远祖先在前、exact scope 在后」
// merge 从 global 开始逐层 set，后写覆盖先写 → 最近 scope 最终生效
merge(scope) {
  for (const layer of this.chainLayers(scope))
    for (const [name, value] of layer.entries())
      merged.set(name, value)   // 同名时更近的 scope 覆盖
}
```

### 2.6 品牌化 ID + 穷尽性（util/brand + llm/never）

```ts
// Branded：零运行时成本的编译期名义类型
declare const BRAND: unique symbol
export type Branded<B extends string> = string & { readonly [BRAND]: B }
const CallId = (id: string) => id as CallId   // 边界显式构造

// assertNever：closed union 穷尽性
export function assertNever(value: never, context?: string): never {
  throw new Error(`unreachable variant: ${JSON.stringify(value)}`)
}
```

`CallId` / `JobId` / `MessageId` 即使运行时都是 `string`，类型层面互不可赋值，杜绝裸 string 混用不同语义 id。

### 2.7 每文件 100% 覆盖率门禁（vitest.config.ts）

```ts
coverage: {
  provider: 'v8',
  thresholds: {
    perFile: true,      // 关键：逐文件，防高覆盖大文件补贴裸文件
    statements: 100, branches: 100, functions: 100, lines: 100,
  },
}
```

配套：自定义 Istanbul 报告器打印未覆盖位置的 `path:line:col`；「未覆盖行优先视为死代码应删除，而非补测试」。

---

## 三、agentrt 的对应源码级机制（含签名）

### 3.1 三循环 DAG 编排（coreloopthree）

```c
// cognition.h —— 意图 → DAG plan（节点 + depends_on）
typedef struct airy_task_node {
    char *task_node_handler_name;     // 处理器名（工具/Agent 名）
    char **task_node_depends_on;      // 依赖边
    size_t task_node_depends_count;
} airy_task_node_t;
typedef struct airy_task_plan {
    airy_task_node_t **task_plan_nodes;   // DAG 节点
    size_t task_plan_node_count;
} airy_task_plan_t;

// 三大可插拔策略（函数指针表 + destroy）
struct airy_plan_strategy { airy_plan_func_t plan; airy_plan_destroy_t destroy; void *data; };
struct airy_coordinator_strategy { ... };
struct airy_dispatching_strategy { ... };

// orchestrator.h —— Phase 0-4 串行管线
typedef enum { DECOMPOSITION, PLANNING, GENERATION, CRITIQUE, VERIFICATION, AUDIT, ALIGNMENT } orch_phase_t;
```

### 3.2 四层内存分配器（corekern）

| 分配器 | 机制 | 关键签名 |
|--------|------|---------|
| `arena` | bump pointer O(1)，整体 reset，mark/reset_to 回滚 | `airy_arena_mark` / `airy_arena_reset_to` |
| `mempool` | 两级池（普通+紧急），IPC 预留 32MB | `airy_mempool_set_emergency(bool)` |
| `slab` | per-CPU freelist（无锁）+ 全局 partial 链 | `airy_slab_create(&cfg)` |
| `tcache` | `_Thread_local` 本地缓存 + 批量获取/归还 | `airy_tcache_create(&cfg, global_alloc, global_free)` |

### 3.3 memory provider 可拔插（memory）

```c
typedef struct airy_memory_provider {
    const char *name; const char *version;
    airy_memory_capabilities_t capabilities;   // 能力位图 l1~l4/forgetting/faiss
    void *impl;
    struct airy_memory_provider *sync_target;   // 双向同步目标
    // 17 槽函数指针表
    airy_err_t (*init)(...); void (*destroy)(...);
    airy_err_t (*write_raw)(...); (*query)(...); (*retrieve)(...);
    airy_err_t (*evolve)(...); (*forget)(...); (*stats)(...);
    airy_err_t (*mount)(...); (*health_check)(...);
    airy_err_t (*sync_push)(...); (*sync_pull)(...);
} airy_memory_provider_t;

airy_err_t airy_memory_provider_set_active(airy_memory_provider_t*);  // 运行时热切换
```

### 3.4 IPC 128 字节定长头（corekern/are_ipc.h）

```c
#pragma pack(push, 1)
typedef struct are_ipc_message_header {
    uint32_t magic;          // 0: 0x41524531 "ARE1"
    uint16_t version; uint16_t msg_type; uint32_t protocol;
    uint64_t msg_id;         // 请求-响应匹配
    uint64_t trace_id;       // 分布式追踪（全链路）
    uint64_t correlation_id; // 请求-响应关联
    char source[32]; char target[32];
    uint32_t payload_len; uint32_t flags;
    uint64_t timestamp_ns; uint32_t checksum;   // CRC32
    uint32_t reserved; uint32_t _abi_pad;       // 填充至 128
} are_ipc_message_header_t;
#pragma pack(pop)
_Static_assert(sizeof(are_ipc_message_header_t) == 128, ...);
_Static_assert(offsetof(are_ipc_message_header_t, checksum) == 116, ...);
```

### 3.5 RBAC 权限引擎（cupolas）

```c
// priority 降序插入链表 + match 时 best_priority 严格递增（同优先级不覆盖）
static int rule_manager_match(...) {
    if (rule->priority <= best_priority) continue;  // 跳过已不可能是更优的规则
    best_priority = rule->priority; result = rule->allow;
}
```

---

## 四、源码级逐机制对比（10 组）

### 对比 1：单一真相源事件流

| 维度 | deepseek | agentrt |
|------|----------|---------|
| 真相源 | `Session.log` append-only，`seq = log.length` 全局连续 | 无统一事件流；记忆/审计/认知状态分三条独立流 |
| 派生视图 | `surfaceOp` 标记 → `surface.nodes` → `deriveMessages()` | `airy_feedback_callback_t` 三级反馈 + `trace_id` 贯穿 + checkpoint |
| 一致性保证 | `JSON.stringify(messages) === JSON.stringify(deriveMessages())` 运行时断言 | `_Static_assert` 锁 IPC 偏移 + CRC32（传输层，非语义层） |
| 回放/fork | fork/resume/replay 全从日志派生 | checkpoint 恢复（`airy_loop_restore_task`） |

**差距**：agentrt 有传输层的完整性保证（CRC32）+ 追溯（trace_id）+ 恢复（checkpoint），但**缺少「append-only 单一真相源 + 派生视图」的语义层模型**。认知循环产生的状态散落在 memory/审计/遥测三条流，无法从单一日志重建模型上下文。

### 对比 2：capability seam 三角色

| 维度 | deepseek | agentrt |
|------|----------|---------|
| Service Definition | `ShellExecutor` 抽象类，`super(ctx,'shell')` 自注册 | `airy_memory_provider_t`（17 槽 vtable） |
| Provider | `LocalBashExecutor` / `SandboxBashExecutor` 继承 | `builtin_provider` / `memoryrovol` |
| Consumer | `tool-bash` 声明式 `inject` | daemons 直接调用 provider |
| 注册目标 | 按 key 查找的 context（`ctx.shell`） | 全局单例 `g_active_provider` |
| 热切换 | 换 provider 即换实现 | `set_active` 热切换 |

**差距**：agentrt 的 memory provider 已是 seam 的 C 等价物，但**只覆盖 memory 一个域**（LLM/tool/storage/sandbox 未统一抽象），且注册到「全局单例」而非「按 key 的 context」。这意味着 agentrt 无法像 deepseek 那样「换一个 provider 就换掉整个产品行为」（如指向远程沙箱同时移动 Bash/PTY/LSP）。

### 对比 3：编排模型（turn flow vs DAG）

| 维度 | deepseek | agentrt |
|------|----------|---------|
| 粒度 | 线性 turn/step 列表 | DAG 节点（`task_node` + `depends_on`） |
| 扩展点 | waterfall 事件（`agent/pre-step`/`agent/request`/`agent/request-error`） | 三大策略（plan/coordinator/dispatch 函数指针表） |
| 自纠 | verifier/critic | orchestrator critique loop（acceptance 0.7 / auto_correct 0.5 双阈值） |

**结论**：agentrt 的 DAG 编排天然支持并行/条件分支（强于 deepseek 的线性 turn），且三大策略与 waterfall 事件在「可插拔」上殊途同归。双方在「机制/策略分离」上方法论一致，无需互相迁移。

### 对比 4：运行时不变量

| 维度 | deepseek | agentrt |
|------|----------|---------|
| 机制 | 每 package 有 `invariant.ts`，注册到 `ctx.invariants` | `_Static_assert`（编译期）+ RBAC priority 排序 + sanitizer 分级 |
| 范围 | 关系不变量（seq 严格递增、turn/step 嵌套、工具管线单调顺序、模型可见⟺已记录） | 编译期 ABI 不变量 + 运行时权限/净化 |
| 强制方式 | 运行时 `fail()` 中止 | `_Static_assert` 编译失败 + fail-closed 沙箱 |

**差距**：agentrt 有编译期断言（锁 IPC 偏移、SYS_MAX 哨兵）和 fail-closed 沙箱，但**缺少「运行时关系不变量」的系统化机制**——例如「认知循环的 task_plan 必须与提交的 DAG 一致」「记忆写入必须能追溯到某次认知事件」这类跨模块关系，目前靠约定而非运行时强制。

### 对比 5：类型安全

| 维度 | deepseek | agentrt |
|------|----------|---------|
| 机制 | `Branded<B>`（零成本名义类型）+ `assertNever` + discriminant tags | C11 `_Atomic` + `_Static_assert` + 不透明句柄 |
| 防裸 id 混用 | `CallId` vs `JobId` vs `MessageId` 类型层面不可互赋 | `trace_id`/`correlation_id`/`msg_id` 都是 `uint64_t`，可互赋 |

**差距**：agentrt 的 IPC 头有三个 id（`msg_id`/`trace_id`/`correlation_id`），但都是裸 `uint64_t`，类型层面无法防止混用。C 语言可用「不透明结构体 typedef」模拟 Branded（如 `typedef struct { uint64_t v; } airy_trace_id_t;`），但会损失部分零成本特性（需权衡）。

### 对比 6：工具 schema 组装

| 维度 | deepseek | agentrt |
|------|----------|---------|
| 机制 | `defineTool` DSL → JSON Schema 编译 + `validateArgs` + `presentation`（generic/terminal/diff） | syscall 23 个 + skill 管理 |
| 渲染意图 | `card: 'generic'|'terminal'|'diff'` 是设计的一部分 | daemons 输出未分离「渲染意图」 |

**差距**：deepseek 的「工具 UI 渲染意图是设计的一部分」（`presentation.ts`）值得借鉴——agentrt 的 daemons 输出目前未区分「数据」与「渲染意图」，导致上层 UI 需自行判断如何渲染。

### 对比 7：scope shadowing（per-agent 作用域）

| 维度 | deepseek | agentrt |
|------|----------|---------|
| 机制 | `ScopeKey=object` + `scopeParents` WeakMap + `ScopedLayers`（最具体优先） | 无 per-agent 作用域注册机制 |

**差距**：deepseek 的 scope 机制（per-agent 工具/prompt/变量的 shadowing，最具体优先）在 agentrt 中无对应。agentrt 的多 Agent 场景（`airy_agent_spawn`）目前是全局注册，缺少「per-agent 能力集」的作用域隔离。这是多智能体协作的关键能力。

### 对比 8：工程纪律（覆盖率 / Agent Note / 文档工程）

| 维度 | deepseek | agentrt |
|------|----------|---------|
| 覆盖率 | 每文件 100%（`perFile: true`）+ 未覆盖位置报告器 | ASan/LSan/UBSan + 测试套件，无覆盖率门禁 |
| 决策记录 | Agent Note 强制（非平凡变更同 PR 附决策记录，机器校验格式） | 无（靠 git log + 文档） |
| 文档预算 | 字数控预算（`verify-doc-budgets` 9 个 standing docs） | 无 |
| 死链检测 | `verify-md-links` 机器检查 + `#fragment` anchor 校验 | 无（既往审查反复发现陈旧引用） |

**差距**：这是 agentrt 当前最直接、收益最高的借鉴点（尤其死链检测 + 文档预算，直接根治既往审查反复发现的「陈旧引用」「跨文档不一致」顽疾）。

### 对比 9：双语文档 i18n

| 维度 | deepseek | agentrt |
|------|----------|---------|
| 机制 | 三文件配对（`foo.md`+`foo.zh.md`+`foo.i18n.yaml` 存双侧 blob hash）+ `verify-translation-pairing` 门禁 | README.md + README_zh.md 双语，无一致性门禁 |

**差距**：agentrt 有双语文档，但无「成对更新一致性」门禁。deepseek 的「yaml 存双侧 blob hash + 失配时最小补丁对齐」机制值得借鉴。

### 对比 10：子进程/沙箱安全

| 维度 | deepseek | agentrt |
|------|----------|---------|
| 机制 | `bash-sandbox` provider（Landlock/bwrap）+ `shell-env`（受管 DSH_* 变量）+ 防御模式（scrubbed env、0700 临时文件） | cupolas workbench（进程/容器隔离）+ syscall 4 级保护环 + `fork+execvp`（不经 shell） |

**结论**：双方在沙箱安全上都做得较完善（deepseek 用 Landlock/bwrap，agentrt 用 workbench + 保护环 + 不经 shell 的 execvp），方法论趋同，无需迁移。

---

## 五、可吸取的工程设计思想（源码级证据 + C 语言等价落地）

### 吸取点 1（最高价值）：单一真相源事件流 + 「模型可见 ⟺ 已记录」

**deepseek 源码证据**：`Session.log` append-only + `seq=log.length` + `surfaceOp` 投影 + `deriveMessages()` + `invariant.ts` 的 `JSON.stringify` 逐字节断言。

**agentrt 现状**：有 `trace_id`/`checkpoint`/三级反馈，但认知状态/记忆/审计分三条流，无法从单一日志重建。

**C 语言等价落地建议（1.0.1 重点）**：
- 在 `coreloopthree` 引入 append-only 事件流：`typedef struct airy_session_event { uint64_t seq; airy_event_type_t type; ... }`，`seq` 全局连续。
- `heapstore` 持久化该流；`memory` 检索、`audit` 追踪、遥测皆从该流派生。
- 用运行时断言（而非约定）保证「进入 LLM 的消息必须能从事件流重建」，等价于 deepseek 的 invariant。

### 吸取点 2（高价值）：capability seam 三角色推广

**deepseek 源码证据**：`ShellExecutor` 抽象类自注册 + Provider 继承 + Consumer `inject` + `declare module` 类型注入。

**agentrt 现状**：`memory_provider.h` 已是 seam 的 C 等价物，但只覆盖 memory 一个域。

**C 语言等价落地建议（1.0.1）**：
- 提炼一条架构元规则：「能力 = Service Definition（vtable）+ Provider（实现）+ Consumer（调用者）三角色」。
- 将 `memory_provider` 的 vtable 模式推广到 LLM（`llm_provider_t`）、tool（`tool_provider_t`）、storage（`storage_provider_t`）、sandbox（`sandbox_provider_t`）。
- 关键差异：agentrt 的 provider 目前注册到「全局单例」，应演进为「按 key 查找的服务注册表」（C 语言用 hash 表 + 字符串 key 实现），才能支持「换 provider 换整个产品行为」。

### 吸取点 3（高价值）：运行时 invariant companion 模式

**deepseek 源码证据**：每 package 有 `invariant.ts`，注册到 `ctx.invariants`，做关系断言（seq 严格递增、turn/step 嵌套、工具管线单调顺序、模型可见⟺已记录）。

**agentrt 现状**：有编译期 `_Static_assert`，无运行时关系不变量。

**C 语言等价落地建议（1.0.1）**：
- 在 `commons` 引入 `airy_invariant_register(fn)` 注册机制，daemons/atoms 启动时注册关系不变量断言。
- 典型不变量：「task_plan 的 depends_on 无环」「记忆写入可追溯到认知事件」「IPC 响应 msg_id 匹配请求」。
- 等价于 deepseek 的「运行时 invariant companion」，用 `#ifndef NDEBUG` 控制开销。

### 吸取点 4（高价值）：每文件 100% 覆盖率门禁 + Agent Note

**deepseek 源码证据**：`vitest.config.ts` 的 `perFile: true` + 100% 阈值 + 自定义未覆盖位置报告器；`verify-agent-note-format.ts` 机器校验 Agent Note 格式。

**agentrt 现状**：ASan/LSan/UBSan + 测试套件，无覆盖率门禁，无决策记录机制。

**C 语言等价落地建议（1.0.1）**：
- 引入 `gcov`/`llvm-cov` 的每文件覆盖率门禁（CMake `ENABLE_COVERAGE` 已存在，可加 `--fail-under` 逻辑）。
- 引入 Agent Note 机制：非平凡变更附决策记录，归入 `closed-docs/agentrt/`，机器校验格式。

### 吸取点 5（高价值）：文档分层工程 + 死链检测 + 字数控预算

**deepseek 源码证据**：`verify-md-links.ts`（mdast 解析 + GitHub slug 算法 + `#fragment` 校验）、`verify-doc-budgets.ts`（`wc -w` 语义 + BAD/MISS/OVER 三失败）、`doc-budgets.manifest.json`（9 个 standing docs 的 ceiling）。

**agentrt 现状**：文档体系庞大（docs/AirymaxOS ~153 + closed-docs），既往审查反复发现陈旧引用/跨文档不一致。

**C 语言落地建议（0.1.1 即可，收益立竿见影）**：
- 建立「one home per fact」原则 + slop 清单（反冗余审计）。
- 引入机器可检查死链 CI（可用脚本扫描 `.md` 的相对链接 + `#fragment`）。
- 对易膨胀的 standing docs 设字数控预算。

### 吸取点 6（中高价值）：per-agent 作用域（scope shadowing）

**deepseek 源码证据**：`ScopeKey=object` + `scopeParents` WeakMap + `ScopedLayers` 最具体优先 shadowing。

**agentrt 现状**：多 Agent 场景（`airy_agent_spawn`）是全局注册，无 per-agent 能力集隔离。

**C 语言等价落地建议（1.0.1）**：
- 在 agent 管理引入 per-agent 能力集（工具/prompt/变量的 shadowing），等价于 deepseek 的 scope。
- 这是多智能体协作（`coreloopthree` 的 `multi_agent_collaboration.h` 已提及）的关键能力。

### 吸取点 7（中高价值）：工具渲染意图分离 + 品牌化 ID

**deepseek 源码证据**：`presentation.ts` 的 `card: 'generic'|'terminal'|'diff'`；`Branded<B>` 防止裸 string 混用。

**agentrt 现状**：daemons 输出未分离渲染意图；IPC 三个 id 都是裸 `uint64_t`。

**C 语言等价落地建议（1.0.1）**：
- daemons 输出区分「数据」与「渲染意图」（`airy_render_kind_t`）。
- 对 `trace_id`/`correlation_id`/`msg_id` 用不透明结构体 typedef 模拟 Branded（权衡零成本特性）。

---

## 六、可吸取的产品哲学（5 条，源码级支撑）

1. **可组合性优先于单一实现**：deepseek 的「换 provider 换整个产品行为」（`bash-local` → `bash-sandbox` 换沙箱）体现了组合优先。agentrt 应强化「平台 = 可组合原语的组合」。

2. **单一真相源**：deepseek 的 `Session.log` 是唯一真相源，其余全派生。agentrt 应确立「会话事件流」为单一真相源。

3. **配置即组合**：deepseek 的 profile/bundle/patch 三层声明式组合 + `--dump-config` 可观测。agentrt 的 daemon 组合应向声明式演进。

4. **诚实的产品立场**：deepseek 明确「开发者预览 + 未来破坏兼容」+「基础优先于爆炸半径」。agentrt 0.1.1 奠基版本应诚实声明无兼容承诺。

5. **文档即契约 + 机器可检查**：deepseek 的 JSDoc 契约 + `verify-md-links`/`verify-doc-budgets` 机器门禁。agentrt 应强化「文档与代码同 PR 更新 + 文档契约机器可检查」。

---

## 七、优先级与落地路径

| 优先级 | 吸取点 | 落地周期 | 具体动作 |
|--------|--------|---------|---------|
| **P0** | 吸取点 5：文档分层工程 + 死链检测 | 0.1.1 | 建「one home per fact」+ slop 清单 + 死链 CI + 字数控预算 |
| **P0** | 产品哲学 4：预发布立场声明 | 0.1.1 | 工程标准声明「奠基期无兼容承诺」 |
| **P1** | 吸取点 1：单一真相源事件流 | 1.0.1 | coreloopthree 输出 append-only 事件流，heapstore 持久化 |
| **P1** | 吸取点 2：capability seam 推广 | 1.0.1 | 提炼架构元规则 + 推广 vtable 到 LLM/tool/storage/sandbox |
| **P1** | 吸取点 3：运行时 invariant | 1.0.1 | commons 引入 invariant 注册机制 |
| **P1** | 吸取点 4：覆盖率门禁 + Agent Note | 1.0.1 | gcov 每文件门禁 + Agent Note 机制 |
| **P2** | 吸取点 6：per-agent scope | 1.0.1 | agent 管理引入 per-agent 能力集 |
| **P2** | 吸取点 7：渲染意图 + 品牌化 ID | 1.0.1 | daemons 分离渲染意图 + id 不透明 typedef |

---

## 八、结论

1. **源码级验证了上一份报告的结论**：agentrt 与 deepseek 在「机制/策略分离」「微核心最小化」「内生安全」「可拔插 provider」上方法论趋同，但 deepseek 在「单一真相源事件流」「capability seam 三角色」「运行时 invariant」「工程纪律极致化」「文档分层工程」五个维度上有更系统化、更可执行的范式。

2. **最关键的三个源码级差距**：
   - **单一真相源事件流缺失**（deepseek 有 `Session.log` + `deriveMessages()` + 运行时断言；agentrt 认知/记忆/审计分三条流）。
   - **capability seam 未推广**（agentrt 的 `memory_provider.h` 已是 seam 的 C 等价物，但只覆盖 memory 一个域）。
   - **运行时 invariant 缺失**（deepseek 每 package 有 `invariant.ts`；agentrt 只有编译期 `_Static_assert`）。

3. **最直接、收益最高的借鉴点**：文档分层工程（死链检测 + 字数控预算 + one home per fact）——直接根治 agentrt 既往审查反复发现的「陈旧引用」「跨文档不一致」顽疾，0.1.1 即可落地。

4. **边界明确**：本报告的 C 语言等价落地建议均为「抽象层面的等价」，不可机械迁移 deepseek 的 TS 类型系统（如 `Branded<B>`、`declare module` 声明合并），需用 C 的不透明结构体、函数指针表、hash 表注册等原语等价实现。

---

*报告完*
