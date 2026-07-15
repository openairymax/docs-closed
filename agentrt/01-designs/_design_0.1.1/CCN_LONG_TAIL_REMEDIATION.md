# CCN 长尾治理计划（Cyclomatic Complexity Long-Tail Remediation）

> **文档编号**: DOC-CCN-LTR-0.1.1  
> **创建日期**: 2026-07-11  
> **版本**: v1.2  
> **状态**: 生效  
> **依赖**: lizard v1.23.0 CCN 分析结果  
> **关联**: P0.19 高 CCN 函数拆分（第一档 + 第二档 + BLOCK 全部完成）+ 拆分后单元测试补齐  

---

## 1. 执行摘要

### 1.1 当前状态

P0.19 第一档（CCN > 100，5 函数）、第二档（CCN 50~99，8 函数）以及 BLOCK 级别（CCN > 50，5 函数 B01-B05）已全部完成拆分，核心路径（atoms/coreloopthree + corekern）CCN 全部 ≤ 15。P0.19.7 拆分后单元测试补齐已完成（18 函数全覆盖，B05 新建 27 用例，其余 17 函数已有现有测试覆盖）。

全项目 CCN 审计（lizard v1.23.0，2026-07-11，修正重复计数后）结果：

| 严重级别 | CCN 范围 | 函数数量 | 状态 |
|----------|----------|---------|------|
| **BLOCK** | > 50 | 0 | ✅ 已全部治理（B01-B05） |
| **FAIL** | 26 ~ 50 | 98 | 待治理 |
| **WARN** | 16 ~ 25 | 328 | 待治理 |
| **PASS** | ≤ 15 | ~1,200+ | 已完成 |
| **合计** | | **426** (CCN > 15) | |

> **注**：此前文档记录为 872（662 WARN + 200 FAIL + 5 BLOCK 已治理），系 lizard 输出解析
> bug 导致重复计数（主函数列表 + Warning 汇总部分的违规函数被各计一次）。
> P0.19.6 修复 `complexity-check.sh` 后实际为 426（328 WARN + 98 FAIL + 0 BLOCK）。

### 1.2 P0.19 已完成成果

| 档位 | 函数数 | 原始 CCN 范围 | 拆分后 CCN | 拆分辅助函数 |
|------|--------|-------------|-----------|-------------|
| 第一档 | 5 | 132 ~ 252 | 全部 ≤ 15 | 48 个 |
| 第二档 | 8 | 53 ~ 79 | 全部 ≤ 15 | 72 个 |
| BLOCK（B01-B05） | 5 | 53 ~ 77 | 全部 ≤ 15 | 36 个 |
| **合计** | **18** | | | **156 个** |

---

## 2. BLOCK 级别函数清单（CCN > 50）

> 优先级：P0 — 必须在 0.1.1 内完成治理  
> **状态：✅ 已全部完成（2026-07-11）**

| # | 函数名 | 原 CCN | 拆分后 CCN | NLOC | 文件路径 | 状态 |
|---|--------|-------|-----------|------|----------|------|
| B01 | `cupolas_vault_import` | 77 | 8 | 323 | `cupolas/src/security/cupolas_vault.c` | ✅ |
| B02 | `match_endpoint_extract` | 63 | 15 | 137 | `protocols/core/router/src/protocol_router.c` | ✅ |
| B03 | `svc_load_model_config_yaml` | 56 | 11 | 174 | `daemons/llm_d/src/service.c` | ✅ |
| B04 | `apply_single_rule` | 54 | 10 | 95 | `daemons/common/src/input_validator.c` | ✅ |
| B05 | `mcp_v1_route_request` | 53 | 13 | 118 | `protocols/standards/mcp/src/mcp_v1_adapter.c` | ✅ |

**治理策略**：采用上下文结构体 + 阶段处理器模式（与 P0.19 第一/二档相同方法），目标 CCN ≤ 15。  
**实际工时**：~12h（2.4h/函数，含验证）  
**附带修复**：B05 期间发现并修复 5 项预先存在的问题：
- `counter.c` 中 `agentrt_token_model_type_t` 拼写错误 → `agentrt_token_model_t`
- `config_source.c` 缺失的 `yaml_parse_mapping` 前向声明
- `thinking_chain.h/.c` 新增 `agentrt_tc_chain_find_step` 实现以解决 `test_cl3_loop` 链接失败
- `cupolas_vault.c` `vi_import_text_format` 添加 `__attribute__((unused))` 抑制条件编译路径产生的死代码警告
- `triple_coordinator.c` `tc3_coordinator_execute` 入口添加 `!out_output || !out_output_len` NULL 检查，并清理 `tc3_exec_init` 中误校验 `*out_output` 解引用值的冗余参数（修复 `test_tc3_null_params` SEGV）

**P0.19.7 B05 测试期间发现并修复的 3 项 `mcp_v1_handle_prompts_get` 预存 bug**：
- **类型混淆**：`messages[i].content`（`mcp_content_t*`）被强转为 `const char*` 传入 `json_string_escape`，读取垃圾内存。修复为正确访问 `messages[i].content[0].text`，并对 NULL/空数组做防御性检查。
- **双重引号**：`json_string_escape` 返回值已含外层引号，格式串 `\"%s\"` 又添加一层，导致响应中 text 字段显示为四重引号。修复为使用 `%s`（与 tools/call 序列化方式一致）。
- **内存泄漏**：handler 返回的 `messages` 数组及其内部 content 在序列化完成后从未释放，ASan 报告 9736 bytes leaked in 71 allocations。修复为在函数返回前和 `!buf` 错误路径中均添加完整的 messages 清理代码。

---

## 3. FAIL 级别函数清单（CCN 26 ~ 50）

> 优先级：P1 — 建议在 0.1.1 内完成高优先级模块，其余纳入 v1.0.1

### 3.1 按模块分布

| 模块 | 函数数 | 最高 CCN | 代表函数 |
|------|--------|---------|----------|
| atoms/coreloopthree | 72 | 49 | `tc3_llm_s1_expert`(49), `agentrt_browser_fill_form`(49) |
| commons/utils | 38 | 42 | `yaml_parse_mapping`(42), `parse_json_value`(40) |
| cupolas/src | 28 | 50 | `cupolas_process_spawn`(50) |
| daemons/llm_d | 14 | 50 | `auth_jwt_verify_token`(50) |
| daemons/common | 12 | 50 | `safety_guard_bridge_check`(50) |
| daemons/tool_d | 8 | 50 | `safety_guard_bridge_check`(50) |
| protocols/ | 10 | 44 | 多个 40+ |
| 其他 | 18 | 48 | |

### 3.2 Top 20 FAIL 函数（CCN 降序）

| # | 函数名 | CCN | NLOC | 文件路径 |
|---|--------|-----|------|----------|
| F01 | `cupolas_process_spawn` | 50 | 112 | `cupolas/src/workbench/workbench_process_core.c` |
| F02 | `auth_jwt_verify_token` | 50 | 222 | `daemons/common/src/svc_auth.c` |
| F03 | `safety_guard_bridge_check` | 50 | 167 | `daemons/tool_d/src/safety_guard_bridge.c` |
| F04 | `tc3_llm_s1_expert` | 49 | 155 | `atoms/coreloopthree/src/cognition/critique/tc3_llm_callbacks.c` |
| F05 | `agentrt_browser_fill_form` | 49 | 130 | `atoms/coreloopthree/src/execution/units/browser.c` |
| F06 | `channel_ws_handle_message` | 48 | 181 | `daemons/channel_d/src/channel_ws.c` |
| F07 | `agentrt_gateway_handle_request` | 47 | 95 | `gateway/src/gateway_handler.c` |
| F08 | `agentrt_browser_execute_script` | 46 | 253 | `atoms/coreloopthree/src/execution/units/browser.c` |
| F09 | `agentrt_cognition_process` | 45 | 71 | (已拆分，此为遗留或新变体) |
| F10 | `heapstore_compact_l0` | 44 | 136 | `heapstore/kernel/src/compaction.c` |
| F11 | `agentrt_syscall_dispatch` | 43 | 215 | `atoms/syscall/src/syscall_dispatch.c` |
| F12 | `yaml_parse_mapping` | 42 | 632 | `commons/utils/config_unified/src/config_source.c` |
| F13 | `mcp_integration_execute` | 41 | 137 | `protocols/integrations/mcp/src/mcp_integration.c` |
| F14 | `parse_json_value` | 40 | 610 | `commons/utils/config_unified/src/config_source.c` |
| F15 | `parse_ini_simple` | 40 | 581 | `commons/utils/config_unified/src/config_source.c` |
| F16 | `agentrt_memory_rovol_promote` | 39 | 136 | `atoms/memory/src/memory_rovol.c` |
| F17 | `agentrt_browser_navigate` | 39 | 129 | `atoms/coreloopthree/src/execution/units/browser.c` |
| F18 | `agentrt_llm_stream_process` | 38 | 146 | `daemons/llm_d/src/llm_stream.c` |
| F19 | `agentrt_tool_execute_internal` | 37 | 259 | `daemons/tool_d/src/tool_executor.c` |
| F20 | `agentrt_gateway_websocket_upgrade` | 36 | 157 | `gateway/src/gateway_ws.c` |

---

## 4. WARN 级别函数清单（CCN 16 ~ 25）

> 优先级：P2 — 纳入 v1.0.1 路线图，持续增量治理

### 4.1 按模块分布

| 模块 | 函数数 | 说明 |
|------|--------|------|
| atoms/coreloopthree | 158 | 最大模块，主要为 cognition/execution 路径 |
| commons/utils | 116 | config_unified、observability 等工具库 |
| cupolas/src | 60 | 安全/workbench 模块 |
| daemons/llm_d | 46 | LLM 服务守护进程 |
| daemons/common | 28 | 公共守护进程逻辑 |
| 其他 | 254 | 分散在各子模块 |

### 4.2 治理策略

WARN 级别函数数量庞大（328），不宜一次性全量拆分。采用**增量治理**策略：

1. **热路径优先**：优先治理高频调用路径上的函数
2. **修改即治理**：任何修改 WARN 级别函数的 PR 必须同时将其 CCN 降至 ≤ 15
3. **CI 门禁**：新增函数 CCN > 15 即拒绝（P0.19.6 CI 阈值集成）

---

## 5. 治理路线图

### 5.1 Phase 1: 0.1.1 收尾（当前）

| 任务 | 范围 | 工时 | 负责人 | 状态 |
|------|------|------|--------|------|
| P0.19.6 CI 阈值集成 | 新增 `complexity-check.sh`，集成到 quality-gate.sh | 4h（实际） | C | ✅ |
| P0.19.7 拆分后单元测试 | 为 18 个已拆分函数补齐测试 | 18h | A + C | ✅ |
| P0.19.8 本文档 | 长尾治理计划文档化 | 2h | A | ✅ |
| B01-B05 BLOCK 治理 | 5 个 CCN > 50 函数 | 12h（实际） | A | ✅ |

**Phase 1 实际剩余**: 0h（P0.19 全部完成）

> **P0.19.7 完成说明（2026-07-11）**：
> - B05 `mcp_v1_route_request` 为 18 个已拆分函数中唯一无现有测试文件的函数，新建 `protocols/tests/test_mcp_v1_adapter.c`（27 用例，覆盖全部 9 条路由路径 + NULL 参数 + 边界条件 + JSON 字段提取鲁棒性）。
> - 其余 17 个已拆分函数经审计确认已有现有测试文件覆盖（如 `test_browser.c`、`test_cognition.c`、`test_parallel_dispatcher.c`、`test_protocol_router.c`、`test_input_validator.c` 等）。
> - 测试期间在 `mcp_v1_handle_prompts_get` 中发现并修复 3 项预存 bug（详见 §2 附带修复清单）。
> - 验证结果：27/27 通过，退出码 0，无 ASan 泄漏；全项目 ctest 108/108 通过。

### 5.2 Phase 2: v1.0.1 M1-M2（开发早期）

| 优先级 | 模块 | 函数数 | 工时 |
|--------|------|--------|------|
| P1-高 | atoms/coreloopthree FAIL 级别 | 72 | ~144h |
| P1-高 | daemons/ FAIL 级别（llm_d/common/tool_d） | 34 | ~68h |
| P1-中 | cupolas/src FAIL 级别 | 28 | ~56h |
| P1-中 | protocols/ FAIL 级别 | 10 | ~20h |

**Phase 2 合计**: ~288h（约 7 周，2 人并行）

### 5.3 Phase 3: v1.0.1 M3-M5（开发中期）

| 优先级 | 模块 | 函数数 | 工时 |
|--------|------|--------|------|
| P2-高 | commons/utils FAIL 级别 | 38 | ~76h |
| P2-高 | atoms/coreloopthree WARN 热路径 | ~50 | ~50h |
| P2-中 | 其他 FAIL 级别 | 18 | ~36h |

**Phase 3 合计**: ~162h

### 5.4 Phase 4: v1.0.1 M6+ 及后续版本

| 优先级 | 范围 | 函数数 | 策略 |
|--------|------|--------|------|
| P2-低 | WARN 级别长尾 | ~612 | 增量治理 + 修改即治理 |

---

## 6. 治理方法论

### 6.1 拆分模式（继承自 P0.19 第一/二档实战经验）

1. **上下文结构体模式**：将函数内局部状态集中到 `ctx` 结构体，辅助函数通过指针共享
2. **阶段处理器模式**：将复杂流程按阶段拆分为独立 handler 函数
3. **命令处理器模式**：将大型 switch/if-else 拆分为函数指针数组调度
4. **依赖构建器模式**：将嵌套依赖关系构建逻辑提取为独立辅助函数

### 6.2 验收标准

- 目标函数 CCN ≤ 15（lizard v1.23.0）
- 所有辅助函数 CCN ≤ 15
- 拆分前后行为一致（黄金输出对比）
- 单元测试覆盖率 ≥ 80%（拆分函数）
- 无 `goto` 跨函数（消除 cleanup_nodes 标签）

### 6.3 CI 门禁规则

| 阈值 | 行为 | 说明 |
|------|------|------|
| CCN ≤ 15 | ✅ 通过 | 目标状态 |
| CCN 16 ~ 25 | ⚠️ 警告 | 允许合入但记录技术债 |
| CCN 26 ~ 50 | ❌ 拒绝 | 必须拆分或提供豁免说明 |
| CCN > 50 | 🚫 阻断 | 绝对禁止新增 |

### 6.4 P0.19.6 CI 阈值集成（✅ 已完成）

**脚本**: `devtools/scripts/ci/pipeline/validate/complexity-check.sh`
**集成**: `devtools/scripts/ci/pipeline/validate/quality-gate.sh` Gate 6

**两种运行模式**:

| 模式 | 命令 | 用途 | 退出码 |
|------|------|------|--------|
| 全量扫描 | `complexity-check.sh` | 开发者手动查看整体 CCN 状态 | 0 PASS / 2 WARN / 1 FAIL+BLOCK |
| 增量检测 | `complexity-check.sh --incremental` | CI 门禁，仅检查新增函数 | 0 PASS / 2 WARN / 1 FAIL+BLOCK |

**增量检测工作原理**:
1. 遍历 `SCAN_DIRS`，对每个目录找到其 git 仓库根（支持嵌套子模块）
2. 在每个仓库内运行 `git diff` 获取变更文件
3. 对每个变更文件，获取基础版本（`CCN_BASE_REF`，默认 `HEAD`）的函数名集合
4. 对当前版本运行 lizard，只报告**基础版本中不存在**的违规函数（即新增函数）
5. 已存在的 FAIL 函数在长尾治理计划中跟踪，不阻塞 PR

**环境变量**:
- `CCN_BASE_REF`: 增量模式基础引用（默认 `HEAD`；CI 环境设为 `origin/main`）

**修复的 bug**:
- lizard 输出含主函数列表 + Warning 汇总两部分，后者重复列出违规函数 → 用 `awk '/!!!! Warnings/{exit}'` 分割
- lizard 不支持 stdin 读取（`lizard -` 返回 "0 file analyzed"）→ 改用临时文件
- `awk -F'@' '{print $1}'` 保留了 NLOC/CCN/token 等前缀 → 改用 `awk '{print $6}' | cut -d'@' -f1`

**全量扫描结果（2026-07-11，修正后）**: 0 BLOCK, 98 FAIL, 328 WARN, 426 total

---

## 7. 附录

### 7.1 P0.19 已完成拆分函数清单（共 18 个）

#### 第一档（CCN > 100）

| 函数 | 原始 CCN | 拆分后 CCN | 辅助函数 |
|------|---------|-----------|----------|
| `browser_execute` | 252 | 12 | 18 |
| `agentrt_cognition_process` | 243 | 11 | 13 |
| `execute_single_phase` | 218 | 10 | 6 |
| `parse_value` | 132 | 11 | 5 |
| `yaml_parse_value` | 124 | 10 | 6 |

#### 第二档（CCN 50 ~ 99）

| 函数 | 原始 CCN | 拆分后 CCN | 辅助函数 |
|------|---------|-----------|----------|
| `tc3_coordinator_execute` | 79 | 11 | 11 |
| `agentrt_scheduler_resolve_dependencies` | 68 | 10 | 7 |
| `dual_coordinate` | 64 | 10 | 7 |
| `ml_planner_rule_based_plan` | 63 | 7 | 14 |
| `reflective_plan` | 60 | 10 | 8 |
| `agentrt_parallel_dispatcher_dispatch` | 60 | 13 | 7 |
| `agentrt_yaml_validate` | 57 | 11 | 10 |
| `tc3_llm_s1_verify` | 53 | 12 | 6 |

#### BLOCK 级别（CCN > 50，B01-B05）

| 函数 | 原始 CCN | 拆分后 CCN | 辅助函数 | 拆分模式 |
|------|---------|-----------|----------|----------|
| `cupolas_vault_import` | 77 | 8 | 9 | 上下文结构体 + 二进制/文本格式分发 |
| `match_endpoint_extract` | 63 | 15 | 6 | URL 模式匹配阶段拆分（brace/wildcard/trailing） |
| `svc_load_model_config_yaml` | 56 | 11 | 7 | YAML 事件分发器 + provider 聚合 |
| `apply_single_rule` | 54 | 10 | 8 | 命令处理器模式 + 通用错误设置（va_list） |
| `mcp_v1_route_request` | 53 | 13 | 7 | 路由分发器 + JSON 字段提取统一辅助 |

### 7.2 全项目 CCN 统计快照（2026-07-11）

```
分析工具: lizard v1.23.0
分析范围: agentrt/ (全部 .c 文件)
总函数数: ~2,100
CCN ≤ 15:  ~1,674 (79.7%)
CCN 16-25: 328 (15.6%)
CCN 26-50: 98 (4.7%)
CCN > 50:   0 (0.0%)
CCN > 15 合计: 426 (20.3%)
```

### 7.3 最需关注的模块（按 CCN > 15 函数数排序）

1. atoms/coreloopthree — 230 函数（执行引擎核心路径）
2. commons/utils — 154 函数（配置/可观测性工具库）
3. cupolas/src — 88 函数（安全/workbench）
4. daemons/llm_d — 60 函数（LLM 服务）
5. daemons/common — 40 函数（公共守护进程）

---

> **文档维护**: 每次 CCN 治理 Sprint 结束后更新本文档统计数据。  
> **P0.19 完成状态**: Phase 1 全部完成（P0.19.1~P0.19.8 + B01-B05），0.1.1 CCN 治理收尾。  
> **下次审计**: v1.0.1 M1 启动前（约 2026-08）。  
> **关联文档**: `03-detailed-task-list.md` (P0.19), `02-tech-improvement-plan-v3.0.md`