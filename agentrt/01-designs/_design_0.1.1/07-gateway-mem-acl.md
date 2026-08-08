Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.
"From data intelligence emerges."

# Gateway 记忆转发与 ACL 安全加固设计方案（Phase 3）
> **文档定位**：agentrt 用户态运行时「全量启动」接线 Phase 3——gateway mem.* 转发（G3）+ 协议层 ACL fail-closed 加固（R4）的**设计方案**\
> **文档状态**：✅ 已实施并验证（2026-08-06 完成 Phase 4 全量回归）\
> **最后更新**：2026-08-06\
> **上级文档**：[AgentRT 文档中心](../../README.md)\
> **关联文档**：[06-agent-gateway-wiring.md](../_design_0.1.1/06-agent-gateway-wiring.md)、[L2 服务协议 02-l2-service-protocol.md](../../../../docs/AirymaxRT/30-interfaces/05-runtime-interfaces/02-l2-service-protocol.md)

---

## 1. 背景与目标

### 1.1 现状（已确认的真问题）

Phase 2 已打通 MCP/OpenAI/A2A → 内部 daemon 三链路，但存在两处**安全与功能缺口**：

| 缺口 | 设计依据 | 现状 |
|------|---------|------|
| gateway → mem_d 记忆转发 | 06-agent-gateway-wiring.md G3：`mem.write/search/get/delete` → `gw_svc_call` 透传 | gateway 无任何 mem.* 方法；TUI 记忆走本地 JSONL（可用但双轨，R7）|
| 协议层 ACL fail-closed | 06-agent-gateway-wiring.md R4：外部请求不得直接触达 `shell_run` 等敏感工具（保持 approval 链）；`mem.*` 需鉴权 | `daemon_security` 的 ACL 表（`daemon_check_tool_permission`）存在但**零调用点**——所有工具执行无权限判定（fail-open 缺口）|

### 1.2 目标与架构原则

**目标**：gateway 暴露 mem.* 方法直连 mem_d；所有外部协议触发的工具执行过 ACL（fail-closed）；ACL 默认规则保证**不误拦正常请求**（fs_*/mem.* 放行），仅对敏感工具 `shell_run` 默认拒绝。

**架构原则（行业底座标准）**：

| 原则 | 行业参照 | 本项目落点 |
|------|---------|-----------|
| 安全是横切关注点 | Linux LSM / K8s RBAC：授权检查在请求路径统一执行 | ACL 检查收敛在 gateway 工具执行的两个唯一入口（`gw_execute_tool` / `gw_biz_tool_exec`），不散落 |
| fail-closed | 默认拒绝，显式授权 | `daemon_check_tool_permission` 无匹配规则即 DENY；默认规则显式注册 |
| 机制/策略分离（IRON-3） | 规则（策略）可配置，机制固定 | ACL 规则启动注册 + env 覆盖；检查机制固定 |
| 无隐藏瑕疵 | 不"先放行后补丁" | 同一工具入口统一过 ACL，无绕过路径（编排路径边界见 §6 R9）|

---

## 2. 数据流验证（模拟结论）

> 对运行中的真实 daemon 发起验证（`/tmp/airy_phase3_sim.py`），结论：**mem 转发链路通、ACL 规则设计不误拦正常请求**。

### 2.1 已验证链路

| 链路 | 验证方式 | 结果 |
|------|---------|------|
| gateway mem.write → mem_d | 直连 `$AIRY_RUNTIME_DIR/mem.sock` 调 write | ✅ 返回 record_id |
| mem.search → mem_d | 同上 | ✅ total=1（命中写入记录）|
| mem.get → mem_d | 同上 | ✅ 数据完整取回 |
| mem.delete → mem_d | 同上 | ✅ deleted=true |
| mem.count → mem_d | 同上 | ✅ count 正确 |
| ACL 工具判定 | 模拟 `daemon_check_tool_permission` fail-closed | ✅ fs_read/fs_write/fs_list ALLOW；shell_run DENY；未知工具 DENY |

### 2.2 ACL 不误拦验证

| 场景 | ACL 判定 | 结论 |
|------|---------|------|
| MCP tools/call fs_list | ALLOW | ✅ 正常请求不误拦 |
| MCP tools/call shell_run | DENY | ✅ 敏感工具默认拒绝 |
| JSON-RPC mem.write | ALLOW | ✅ 记忆业务不误拦 |

**无阻塞点**：mem 转发与 ACL 判定均可直接实施。

---

## 3. 接口设计

### 3.1 mem.* 转发（G3）

**对外暴露**（gateway JSON-RPC 方法，`<daemon>.<method>` 命名空间）：

| 外部方法 | 内部 mem_d 方法 | 参数透传 | 响应透传 |
|---------|---------------|---------|---------|
| `mem.write` | `write` | `{"data": str, "metadata": obj?}` | `{"record_id": str}` |
| `mem.search` | `search` | `{"query": str, "limit": int?}` | `{"results": [...], "total": n}` |
| `mem.get` | `get` | `{"record_id": str}` | `{"data": str, "length": n, "metadata": str?}` |
| `mem.delete` | `delete` | `{"record_id": str}` | `{"deleted": bool}` |
| `mem.count` | `count` | `{}` | `{"count": n}` |

**方法白名单（鉴权门控）**：仅透传上表 5 个标准方法，其他 `mem.*` 方法拒绝（`-32601 Method not found`）——防止任意方法穿透。

**env 门控**：`AIRY_GATEWAY_MEM_PUBLIC`（默认 `true`：内部记忆服务正常业务放行；生产环境可设 `false` 关闭外部 mem 访问，R7 TUI 本地 JSONL 不受影响）。

### 3.2 ACL fail-closed（R4）

**外部协议请求默认身份**：`external`（MCP/OpenAI/A2A/JSON-RPC 无 agent 上下文的请求统一身份；agent.run 编排路径的工具执行在 runner 内部，边界见 §6 R9）。

**默认规则（启动注册，main.c）**：

| agent_id | resource | allowed | 说明 |
|----------|----------|---------|------|
| external | fs_read | true | 基础工具（不误拦） |
| external | fs_write | true | 基础工具（不误拦） |
| external | fs_list | true | 基础工具（不误拦） |
| external | shell_run | **env 控制** | 敏感工具：默认 false（approval 链）；`AIRY_GATEWAY_ACL_ALLOW_SHELL=true` 显式放行 |

**检查点（两个唯一工具执行入口）**：
- `gw_execute_tool`（llm_d 直连工具循环，agent.run 无 agent 路径）
- `gw_biz_tool_exec`（MCP tools/call backend）

统一经 `daemon_check_tool_permission("external", tool_name, "execute")`——fail-closed，未注册规则即 DENY。

---

## 4. 文件与接口修改清单

| # | 文件 | 修改 | 接口 |
|---|------|------|------|
| M1 | `daemons/gateway_d/src/gateway_business_handler.c` | 新增 mem 转发 handler；新增 ACL 检查；两个工具执行入口加 ACL | `handle_mem_call()`（static）、`gw_acl_check_tool()`（static）|
| M2 | `daemons/gateway_d/src/gateway_business_handler.c` | `gateway_business_handle` 增加 `mem.` 方法分支 | 复用 `gw_svc_call` |
| M3 | `daemons/gateway_d/src/main.c` | 启动注册 ACL 默认规则 | `daemon_security_add_acl_rule()` |
| M4 | `daemons/gateway_d/CMakeLists.txt` | 链接 `cupolas`/`svc_common`（ACL 依赖，如未传递） | — |

**daemon 侧（mem_d/tool_d）零改动**：服务方法已注册可用，ACL 判定在 gateway 侧（协议边界）。

---

## 5. 实现步骤

1. **M1-M2：mem 转发**——`gateway_business_handle` 中 `strncmp(method, "mem.", 4) == 0` → 白名单校验 → `gw_svc_call(ctx->mem_sock_path, mem_d 方法, params, GW_TOOL_TIMEOUT_MS)` → 透传响应。
2. **M1：ACL 检查函数**——`gw_acl_check_tool(tool_name)` 封装 `daemon_check_tool_permission("external", tool_name, "execute")`，返回 0=允许。
3. **M1：接入执行入口**——`gw_execute_tool` 与 `gw_biz_tool_exec` 首行调用 `gw_acl_check_tool`，DENY 时返回错误文本 `"Permission denied: tool <name> not authorized"`（不伪造成功）。
4. **M3：默认规则注册**——`gateway_business_ctx_create` 后（daemon_security 已初始化）注册 fs_* 与 shell_run（env 控制）。
5. **验证**：curl mem.write/search/get/delete/count 端到端；MCP shell_run 被 ACL 拒绝、fs_list 正常；agent.run 无 agent 工具循环不回退。
6. **回归**：全量 ctest + cargo test + Phase 2 链路复验。

---

## 6. 潜在风险点

| # | 风险 | 说明与缓解 |
|---|------|-----------|
| R9 | agent.run 编排路径（agent_d → runner）的工具执行绕过 gateway ACL | runner 经 SyscallProxy 直连 tool_d，gateway ACL 管不到。边界：编排路径属于 agent 执行环境内部行为；严格闭环需 tool_d 层 ACL（Phase 3+ 增强，本文档标注不实施）|
| R10 | ACL 误拦正常请求 | 默认规则显式注册 fs_*/mem.* allow（§2.2 已验证）；未知工具 fail-closed DENY 属预期（新工具需显式授权）|
| R11 | `daemon_check_tool_permission` 依赖 security 初始化 | gateway_d 已 `daemon_cupolas_init`（启动日志确认 "Daemon security: initialized"）；M3 规则注册在其后，时序正确 |
| R12 | mem 转发透传安全 | 方法白名单 + `AIRY_GATEWAY_MEM_PUBLIC` 门控；透传 params/响应原样（mem_d 内部校验 data/record_id）|
| R13 | TUI 记忆双轨 | mem_d 作为运行时记忆（agent/外部），TUI 本地 JSONL 不迁移（R7）；关闭外部 mem 不影响 TUI |
| R14 | [SC] 同源约束（IRON-9） | 全部改动在 agentrt 内部；不触碰 [SC] 共享契约层；`mem.*` 遵循 02-l2-service-protocol.md 命名空间 |
| R15 | 透传响应 id 与请求不符（JSON-RPC 2.0 合规） | 实测发现：`gw_svc_call` 内部固定 id=1，mem_d 回显 id=1，透传后客户端响应 id 恒为 1，并发请求无法关联。已修复：`handle_mem_call` 解析响应后改写 id 为请求 id（string/number 均处理，无 id 置 null），实测 `"client-abc"`/`777` 均正确回显 |

---

## 7. 出口标准

1. `curl` JSON-RPC `mem.write`/`mem.search`/`mem.get`/`mem.delete`/`mem.count` 端到端返回 mem_d 真实结果（✅ 已实测，含 id 回显一致）。
2. MCP `tools/call shell_run` → `-32603 Permission denied`（默认配置）；`fs_list` 正常执行。（✅ 已实测：shell_run DENY、fs_list ALLOW、未知工具 fail-closed DENY）
3. 非法 `mem.*` 方法（如 `mem.drop`）→ `-32601 Method not found`。（✅ 已实测）
4. Phase 2 三链路（MCP/OpenAI/A2A）+ agent.run 两路径不回退。（✅ 已实测 42/42 通过）
5. 全量 ctest + cargo test 无回归。（✅ ctest 118/118、cargo test 57/57 通过）

---

## 8. 同源约束说明

- 全部改动位于 agentrt 仓库内（gateway_d），**不新增**与 agentrt-linux 的代码共享；
- 不触碰 [SC] 共享契约层 10 个头文件（`agentrt/commons/include/airymax/`）；
- 内部服务协议遵循既有 L2 服务协议 `mem.*` 命名空间；ACL 复用 daemon_security 既有机制（非新增安全子系统）。

---

*实施完成（2026-08-06）：mem.* 转发 + ACL fail-closed 上线，Phase 4 全量回归无回退（详见 §7 出口标准实测标注）。*
