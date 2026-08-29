# agentrt-0.1.6 P0-4 实证报告：tests 统一 ctest

- 日期：2026-08-29
- 范围：`agentrt` 全仓测试注册一致性审计
- 结论：**统一 ctest 已成立，无需代码改动；183/183 全通过**

## 一、审计方法

在外部构建工作区（源码区外）对 Release 构建树执行：

1. 枚举全仓 `tests/` 目录与 `add_subdirectory(tests)` / 内联 `add_test` 注册情况；
2. 对比构建产物 `bin/test_*` 与 `ctest -N` 注册测试；
3. 根级 `ctest -j4` 全量运行确认。

## 二、实证结果

| 检查项 | 结果 |
|--------|------|
| 根级统一入口 | 根 `CMakeLists.txt` 在 `add_subdirectory` 前 `enable_testing()`，183 个测试全部注册于单一 ctest |
| 测试目录覆盖 | 全仓 20+ 个 `tests/` 目录全部被对应 `CMakeLists.txt` 引用，无僵尸目录 |
| 注册方式 | 两种并存均被根 ctest 收集：(a) 独立 `tests/` 子目录 + `add_subdirectory(tests)`；(b) 内联 `add_test`（airy_cli/syscall/taskflow/channel_d/gateway/cupolas/protocols） |
| 二进制 ↔ 测试对应 | `bin/test_*` 全部有对应注册测试（测试名与二进制名存在 `test_` 前缀差异，非缺失） |
| 全量运行 | `ctest -j4`：183/183 通过 |

## 三、结论与决策

- **统一 ctest 目标已达成**：单一 `ctest` 入口覆盖全仓，无测试遗漏、无死目录、无"构建了但不运行"的测试二进制。
- **保留两种注册方式**：独立 `tests/` 子目录与内联 `add_test` 均为合理组织（测试贴近被测模块，模块可独立构建测试）。物理合并为单一 `tests/` 目录属反模式（测试与模块分离），不做。
- **不清理子目录 `enable_testing()`**：幂等无副作用，且保留各模块独立构建测试能力（SSoT：模块自身可验证）。
- 后续若新增模块，测试须注册到统一 ctest（根级 `ctest` 必须可见），此为硬性验收项。

## 四、验证命令

```bash
cmake --build <外部构建目录> -j4
cd <外部构建目录> && ctest -j4            # 183/183 通过
ctest -N | tail -1                        # Total Tests: 183
```
