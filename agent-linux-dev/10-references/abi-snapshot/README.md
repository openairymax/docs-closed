# [SC] UAPI 字节级快照（K-03）

> 施工图纸：`0.0.5-极境OS任务方案.md` §6.5 K-03、§13.4 F-04。
> 证据等级：E2（仓库实测，`python3 ci/gates/abi-snapshot.py --check`）。

## 1. 这份快照回答什么

`kernel/include/uapi/linux/airymax/` 是用户态唯一可见的内核契约面。它回答不了
「结构体在第几个字节」，也不该回答——那是 `tools/sc-tri-compile` 的事。它只回答
一个问题：**这次提交有没有让用户态看到的头文件发生变化**。

因此判定分两层，缺一不可：

| 层 | 判据 | 为什么单靠另一层不够 |
|---|---|---|
| 集合面 | 受检目录下 `.h` 的集合与登记集合逐条相同 | 只比摘要时，新增或改名的头文件在快照里没有条目，逐条比对仍会通过 |
| 字节面 | 每个文件的 sha256 与登记摘要相同 | 只比集合时，内容改动完全不可见 |

一条注释的改动不会破坏结构兼容，但它改变了发布物料，必须走一次显式刷新与评审。
这就是「任一变更即判负」的理由：不是禁止改，而是禁止**静默**改。

## 2. 真值放在哪，为什么

真值文件是 `tools/abi-check/contract/uapi_headers.sha256`，与消费它的工具同仓。

- 本仓（docs）是权威设计的宿主，但 CI 跑在源码仓，GitHub 镜像不检出本仓；
  摘要若只放这里，门禁在云端无法判定，等于没有门禁。
- 两处各放一份摘要则会出现两份真值，迟早漂移。所以本目录只登记**手续与分工**，
  不复制摘要。

## 3. 三层读点分工（互不替代）

| 读点 | 工具 | 回答的问题 |
|---|---|---|
| 编号面 | `tools/abi-check` | syscall 编号、预留槽与派生契约快照是否与 SSoT 一致 |
| 布局面 | `tools/sc-tri-compile` | 结构体偏移在 3+2 条编译路径上是否一致 |
| 字节面 | `ci/gates/abi-snapshot.py` | 用户态看到的头文件有没有任何字节变化 |

三层都通过，才谈得上「头文件既没改坏、也没改 unnoticed」。

## 4. 当前登记范围（15 份 `.h`）

```text
bpf_struct_ops.h   cognition_types.h  error.h            ipc.h
log_types.h        lsm_types.h        memory_types.h     sched.h
security_types.h   structures_32_gen.h structures_64_gen.h superv.h
syscall_gen.h      syscalls.h         uapi_compat.h
```

其中 `structures_32_gen.h`、`structures_64_gen.h`、`syscall_gen.h`、`ipc.h`
由生成器产出。把它们一并登记是有意的：生成器的输出漂移与手改头文件同样危险，
都必须落在一次可评审的改动里。

## 5. 刷新手续

1. 在源码仓根执行 `python3 ci/gates/abi-snapshot.py --update`。
2. 逐条审阅输出中的「新增 / 缺失 / 变更」，为每一条写下结论：兼容、还是破坏性，
   破坏性是否已按 MAJOR 规则处置。
3. 头文件与快照放进同一个提交；提交信息点名 UAPI 变更，不要夹带无关改动。
4. CI 只跑 `--check`，不回写。快照在 CI 上被改写等于门禁失效。

退出码：`0` 一致；`1` 漂移或快照缺失（判负）；`5` 参数或环境不合法（输入错误，
含坏快照）。`--update` 遇到坏快照同样以 `5` 退出且不改写文件——坏输入不许被
「自动修复」成看似正常的快照。

## 6. 门禁与触发面

| 项 | 值 |
|---|---|
| 门禁编号 | `OS-BUILD-UAPI-SNAPSHOT` |
| 注册表 | `agent-linux/tools/os-chk/gates.yaml`（v1.11.0 起） |
| 执行器 | `python3 ci/gates/abi-snapshot.py --check` |
| CI 入口 | `ci/ci.sh python-verify --kind oschk`（os-chk-verify） |
| 触发面 | `kernel` gitlink 指针变化、`ci/**`、`tools/**`、`.github/workflows/**` |
| 回归 | `bash ci/tests/test_abi_snapshot.sh`（17 条断言） |

`kernel` 是子模块指针，UAPI 改动只会在源码仓提升指针时进入 diff，这与「头文件
与快照同批提交」的手续天然对齐。

## 7. 变更历史

| 日期 | 变更 | 理由 |
|---|---|---|
| 2026-11-20 | 建立基线，登记 15 份 | K-03 首片；此后每次 UAPI 改动必须在此留一行 |
