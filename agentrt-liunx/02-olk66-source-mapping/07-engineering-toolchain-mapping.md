Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved.

# OLK-6.6 工程工具链源码映射 → agentrt-liunx 工程标准

> **文档定位**: 闭源内部参考，OLK-6.6 内核源码中工程工具链（编码规范、构建系统、编译器选项、测试验证、Rust 支持）→ agentrt-liunx（AirymaxOS，极境智能体操作系统）工程标准与工具链复用策略映射
> **版本**: 0.1.1（文档体系完成）/ 1.0.1（开发）
> **最后更新**: 2026-07-09
> **理论根基**: Linux 6.6 内核基线工程思想 + seL4 微内核设计思想 + Airymax 体系并行论
> **密级**: 闭源内部参考（docs-closed）

---

## 1. 文档说明

### 1.1 目的

本文档建立 OLK-6.6 内核源码中工程工具链（coding style / build / compiler / test / rust）到 agentrt-liunx 工程标准的精确映射，回答三个问题：

1. **OLK-6.6 工具链是什么**：源码位置、关键规则、组织方式
2. **agentrt-liunx 对应什么**：agentrt-liunx 工程标准中的对应规范、工具、配置
3. **如何参考但 [IND] 独立实现**：agentrt-liunx 在吸收工程思想基础上独立实现工具链，不照搬源码

> **术语澄清**：agentrt（用户态运行时）= 微核心（micro-core），基于 seL4 微内核思想抽象；agentrt-liunx（OS 发行版）= 微内核（micro-kernel），真正的微内核。本文档严禁使用"微内核原语"描述 agentrt，统一使用"微核心原语"。

### 1.2 源码定位

| 路径 | 说明 | 规模 |
|------|------|------|
| `Documentation/process/coding-style.rst` | Linux 内核编码风格规范 | 1,271 行 |
| `scripts/checkpatch.pl` | 补丁风格检查器（Perl） | 7,823 行 / 239 KB |
| `scripts/kernel-doc` | 内核文档提取脚本（Perl） | 2,531 行 |
| `.clang-format` | clang-format 风格配置 | 689 行（含 560+ ForEachMacros） |
| `Makefile` | 顶层构建主控 | 2,076 行 |
| `Makefile.oever` | 发行版版本元数据 | 5 行 |
| `Kconfig` / `Kbuild` | 配置系统入口 / 顶层构建规则 | 34 行 / 99 行 |
| `arch/x86/Makefile` | x86 架构编译规则 | 340 行 |
| `rust/` + `samples/rust/` | Rust 内核支持 + 样例 | 大型目录 |
| `tools/testing/` + `lib/kunit/` | 测试框架（KUnit / kselftest） | 大型目录 |
| `scripts/coccinelle/` + sparse/Smatch | 静态分析工具链 | 多目录 |

### 1.3 IRON-9 v2 代码共享边界

| 标注 | 含义 | 本文档适用 |
|------|------|------------|
| **[SC]** | Shared Contract 共享契约层（agentrt ↔ agentrt-liunx 共享 4 头文件） | 工具链 UAPI 不涉及 |
| **[SS]** | Semantic Same-origin 语义同源层（API 签名同源，实现独立） | 编码规范语义同源 |
| **[IND]** | Independent 完全独立层（agentrt-liunx 专属） | **工具链整体 [IND] 独立实现** |

**关键声明**：agentrt-liunx 工程工具链属于 **[IND] 完全独立层**。agentrt-liunx 吸收 OLK-6.6 的工程思想（Tab 8、K&R、Kbuild 组织、禁浮点、双编译器、KUnit/kselftest 思路），但工具链脚本、构建规则、测试框架均由 agentrt-liunx 自行实现，不复制 OLK-6.6 源码。agentrt-liunx 的工程实现方式与主流 Linux 发行版保持一致性，以便未来兼容主流发行版标准工具链，但不直接采用其代码。

---

## 2. 编码规范工具链映射

### 2.1 `Documentation/process/coding-style.rst` —— 编码风格圣经

**源码路径**: `OLK-6.6: Documentation/process/coding-style.rst:1-1271`

#### 2.1.1 关键规则摘录

| 章节 | 规则 | 源码行号 | agentrt-liunx 复用 |
|------|------|----------|---------------------|
| 1) Indentation | **Tab = 8 字符**，缩进 = 8 字符 | L18-39 | [SS] 完全采纳 |
| 1) Indentation | 超过 3 层缩进即应重构 | L31-35 | [SS] 采纳 |
| 1) Indentation | switch/case 同列对齐 | L41-59 | [SS] 采纳 |
| 2) Breaking long lines | 80 列软限，100 列硬限 | — | [SS] 采纳 100 列 |
| 3) Braces | K&R 风格：函数开新行，if/else 不开新行 | — | [SS] 完全采纳 |
| 4) Naming | 全小写 + 下划线，禁止驼峰 | — | [SS] 采纳 |
| 5) Typedef | **禁止**对结构体用 typedef | — | [SS] 采纳 |
| 6) Functions | 函数 ≤ 50 行，参数 ≤ 5 个 | — | [SS] 采纳并加严 |
| 8) Comment | `/* */` 风格，每行开头空一格 | — | [SS] 采纳 |
| 10) Kconfig | `config` 缩进 1 Tab，help 文本缩进 2 Tab+1 空格 | — | [SS] 采纳 |

#### 2.1.2 关键引文

```
Tabs are 8 characters, and thus indentations are also 8 characters.
There are heretic movements that try to make indentations 4 (or even 2!)
characters deep, and that is akin to trying to define the value of PI to be 3.
                                            — coding-style.rst:21-23
```

#### 2.1.3 agentrt-liunx 复用方式 [SS]

agentrt-liunx 工程标准规范（`docs-closed/agentrt-liunx/agentrt-liunx基本工程标准规范.md`）逐条采纳上述规则，并针对智能体操作系统场景加严：

```c
/* agentrt-liunx 内核态函数示例：Tab 8 字符、K&R 风格、≤50 行 */
static int airymax_cognition_kthread_run(struct airymax_cog_ctx *ctx)
{
        int ret;

        if (!ctx)
                return -EINVAL;

        ret = kfifo_alloc(&ctx->msg_q, AIRYMAX_COG_QSZ, GFP_KERNEL);
        if (ret)
                return ret;

        init_waitqueue_head(&ctx->wq);
        ctx->task = kthread_run(airymax_cog_main, ctx, "airymax/cog");
        if (IS_ERR(ctx->task)) {
                kfifo_free(&ctx->msg_q);
                return PTR_ERR(ctx->task);
        }
        return 0;
}
```

### 2.2 `scripts/checkpatch.pl` —— 补丁风格检查器（239 KB）

**源码路径**: `OLK-6.6: scripts/checkpatch.pl:1-7823`

#### 2.2.1 关键参数与阈值

| 参数 | 默认值 | 源码行号 | 含义 |
|------|--------|----------|------|
| `$max_line_length` | 100 | L60 | 单行最大长度 |
| `$tabsize` | 8 | L75 | Tab 宽度 |
| `$min_conf_desc_length` | 4 | L63 | Kconfig 描述最短长度 |
| `$minimum_perl_version` | 5.10.0 | L62 | Perl 最低版本 |
| `$allow_c99_comments` | 1 | L72 | 允许 C99 风格注释 |

#### 2.2.2 关键检查规则（checkpatch 检查项摘录）

| 检查类型 | 规则名 | 源码行号 | 说明 | agentrt-liunx 复用 |
|----------|--------|----------|------|---------------------|
| 缩进 | `TABSTOP` | L3962-3967 | 检查缩进是否对齐 Tab 边界 | [SS] 采纳 |
| 尾空白 | `trailing whitespace` | L3589-3600 | 禁止行尾空白 | [SS] 采纳 |
| 注释 | `Block comments use a trailing */` | L4042-4048 | 块注释 `*/` 单独一行 | [SS] 采纳 |
| 行长 | `LONG_LINE` / `LONG_LINE_STRING` | — | >100 列告警 | [SS] 采纳 |
| 符号间距 | `SPACING` | L4976-4987 | 关键字后须空格 | [SS] 采纳 |
| 括号间距 | `SPACING` (paren) | L5470-5488 | 函数调用括号无空格 | [SS] 采纳 |
| 多行缩进 | `alignment matches` | L3962-3975 | 多行语句缩进对齐 | [SS] 采纳 |
| else 缩进 | `bare else` | L4188-4202 | else 对齐 | [SS] 采纳 |
| 尾分号 | `trailing semicolon` | L4372 | 无语句却尾分号告警 | [SS] 采纳 |

#### 2.2.3 agentrt-liunx 复用方式 [IND]

agentrt-liunx 不直接复制 `checkpatch.pl`（239 KB Perl 脚本过重），而是独立实现轻量级 `airymax-checkpatch`：

- **复用思想**：采纳 `$max_line_length=100`、`$tabsize=8`、K&R 大括号、尾空白检查等核心规则
- **独立实现**：用 Python 重写，针对 agentrt-liunx 代码树定制（含 `include/airymax/` 共享契约层头文件检查、Q16.16 定点数使用检查、kfifo 使用检查）
- **新增检查**：禁止内核态 `float`/`double`（必须用 `airymax_q16_t`）、禁止 kthread 间用 `io_uring`（必须用 `kfifo` + `wait_event_interruptible`）

```python
# agentrt-liunx 独立实现的 airymax-checkpatch 关键规则片段
TABSIZE = 8
MAX_LINE_LENGTH = 100

def check_no_float_in_kernel(line, filename):
        """内核态禁止 float/double，必须用 airymax_q16_t (Q16.16 定点数)"""
        if "/kernel/" in filename or "/airymax/" in filename:
                if re.search(r'\b(float|double)\b', line):
                        return "ERROR: kernel code must use airymax_q16_t (Q16.16), no float/double"

def check_kthread_ipc(line, filename):
        """kthread 间通信用 kfifo + wait_event_interruptible，禁止 io_uring"""
                if re.search(r'io_uring.*kthread|kthread.*io_uring', line):
                        return "ERROR: kthread IPC must use kfifo + wait_event_interruptible"
```

### 2.3 `scripts/kernel-doc` —— 内核文档提取

**源码路径**: `OLK-6.6: scripts/kernel-doc:1-2531`

`kernel-doc` 是 Perl 脚本，从 C 源码特殊格式注释中提取 API 文档，生成 man/DocBook/rST。其核心识别格式：

```
/**
 * function_name() - Brief description.
 * @arg1: description of arg1
 * @arg2: description of arg2
 *
 * Longer description.
 *
 * Return: description of return value
 */
```

#### 2.3.1 agentrt-liunx 复用方式 [IND]

agentrt-liunx 采纳 `kernel-doc` 的注释格式约定（[SS] 语义同源），但文档生成工具独立实现：

- **[SS] 同源**：采纳 `/** ... */` + `@arg:` + `Return:` 注释格式
- **[IND] 独立**：用 Sphinx + 自定义 `airymax-kdoc` 扩展替代 `kernel-doc`，输出 rST

```c
/**
 * airymax_q16_mul() - Q16.16 定点数乘法（内核态禁浮点替代方案）
 * @a: 第一个 Q16.16 定点数 (airymax_q16_t = int32_t)
 * @b: 第二个 Q16.16 定点数
 *
 * 计算 a * b，结果截断为 Q16.16 格式。
 * 内核态禁用 float，故所有浮点运算改用本函数。
 *
 * Return: Q16.16 定点数乘积
 */
static inline airymax_q16_t airymax_q16_mul(airymax_q16_t a, airymax_q16_t b)
{
        return (airymax_q16_t)(((int64_t)a * b) >> 16);
}
```

### 2.4 `.clang-format` —— 自动格式化配置（689 行）

**源码路径**: `OLK-6.6: .clang-format:1-689`

#### 2.4.1 关键配置摘录

| 配置项 | 值 | 源码行号 | 含义 |
|--------|-----|----------|------|
| `ColumnLimit` | 80 | L55 | 列宽上限（checkpatch 用 100） |
| `UseTab: Always` | — | — | 始终用 Tab |
| `TabWidth` / `IndentWidth` | 8 | 隐含 | Tab 8 字符 |
| `ContinuationIndentWidth` | 8 | L60 | 续行缩进 8 |
| `AccessModifierOffset` | -4 | L12 | 访问修饰符偏移 |
| `BreakBeforeBraces: Custom` | Custom | L48 | 大括号自定义 |
| `AfterFunction: true` | — | L35 | 函数大括号换行 |
| `AfterControlStatement: false` | — | L33 | 控制语句大括号不换行 |
| `ForEachMacros` | 560+ 项 | L71+ | for_each 宏识别列表 |

#### 2.4.2 ForEachMacros 列表（节选）

`.clang-format` 第 67-689 行维护了一个 560+ 项的 `ForEachMacros` 列表，通过命令自动生成：

```
git grep -h '^#define [^[:space:]]*for_each[^[:space:]]*(' include/ tools/ \
        | sed "s,^#define \([^[:space:]]*for_each[^[:space:]]*\)(.*$,  - '\1'," \
        | LC_ALL=C sort -u
```

节选条目（`.clang-format:72-80`）：
```
  - '__ata_qc_for_each'
  - '__bio_for_each_bvec'
  - '__bio_for_each_segment'
  - '__evlist__for_each_entry'
  - '__for_each_mem_range'
```

#### 2.4.3 agentrt-liunx 复用方式 [IND]

agentrt-liunx 采纳 `.clang-format` 的核心配置（[SS] 语义同源），并定制自己的 `.clang-format`：

- **[SS] 同源**：`ColumnLimit`、`UseTab`、`IndentWidth=8`、`BreakBeforeBraces: Custom`（函数换行、控制语句不换行）
- **[IND] 独立**：`ForEachMacros` 列表由 agentrt-liunx 自有 `for_each` 宏生成（如 `airymax_for_each_agent`、`airymax_for_each_cog_loop`），不复制 560+ OLK-6.6 条目

```yaml
# agentrt-liunx/.clang-format（独立实现，思想同源）
---
Language:        Cpp
BasedOnStyle:    LLVM
ColumnLimit:     100
UseTab:          Always
TabWidth:        8
IndentWidth:     8
ContinuationIndentWidth: 8
BreakBeforeBraces: Custom
BraceWrapping:
  AfterFunction: true
  AfterControlStatement: false
  AfterStruct: false
ForEachMacros:
  - 'airymax_for_each_agent'
  - 'airymax_for_each_cog_loop'
  - 'airymax_for_each_cap_node'
  - 'airymax_for_each_daemon'
```

---

## 3. 构建系统映射

### 3.1 `Makefile` —— 顶层构建主控（2,076 行）

**源码路径**: `OLK-6.6: Makefile:1-2076`

#### 3.1.1 顶层组织结构

| 行段 | 内容 | 源码行号 | 说明 |
|------|------|----------|------|
| 版本号 | `VERSION=6 PATCHLEVEL=6 SUBLEVEL=0` | L2-4 | Linux 6.6 |
| Make 最低版本 | `GNU Make >= 3.82` | L14-16 | 强制检查 |
| 默认目标 | `__all` | L22-23 | 顶层 PHONY |
| 递归构建 | 子 Makefile 只改本目录文件 | L25-39 | 递归下降 |
| 输出美化 | `quiet_cmd_*` / `cmd_*` | L60-92 | 简洁日志 |
| 静态检查 | `make C=1` 启用 sparse | L111-119 | C 标志 |
| KBUILD_CFLAGS | 编译选项聚合 | — | 全局 CFLAGS |

#### 3.1.2 关键设计思想

1. **递归下降构建**：顶层 Makefile 通过 `obj-y += subdir/` 递归进入子目录，每子目录 Makefile 只负责本目录（`Makefile:25-39`）
2. **prepare 阶段**：生成 `bounds.h` / `timeconst.h` / `asm-offsets.h` 后才递归下降（`Kbuild:8-74`）
3. **quiet 规则**：`quiet_cmd_xxx` 控制日志简洁性，`Q=@` 隐藏命令（`Makefile:60-92`）
4. **配置驱动**：`CONFIG_xxx` 控制是否纳入构建（`Kbuild:90-98`）

```makefile
# OLK-6.6 Kbuild:79-98 节选 — 目录递归下降
obj-y                       += init/
obj-y                       += usr/
obj-y                       += arch/$(SRCARCH)/
obj-y                       += kernel/
obj-y                       += certs/
obj-y                       += mm/
obj-y                       += fs/
obj-y                       += ipc/
obj-y                       += security/
obj-y                       += crypto/
obj-$(CONFIG_BLOCK)         += block/
obj-$(CONFIG_IO_URING)      += io_uring/
obj-$(CONFIG_RUST)          += rust/
obj-$(CONFIG_SAMPLES)       += samples/
obj-$(CONFIG_NET)           += net/
```

### 3.2 `Makefile.oever` —— 发行版版本元数据

**源码路径**: `OLK-6.6: Makefile.oever:1-5`

主流发行版内核源码通过独立文件维护版本元数据（源文件使用发行版专属变量名，此处以通用占位 `_DISTRO_` 表示，下同）：

```
# SPDX-License-Identifier: GPL-2.0
_DISTRO_LTS = 0
_DISTRO_MAJOR = 9999
_DISTRO_MINOR = 0
_DISTRO_RELEASE = ""
```

#### 3.2.1 字段含义

| 字段 | 值 | 含义 |
|------|-----|------|
| `_DISTRO_LTS` | 0 | 是否 LTS 版本（0 = 非 LTS 标记，标识上游基线） |
| `_DISTRO_MAJOR` | 9999 | 主版本占位（9999 = 上游主基线，无发行版分支号） |
| `_DISTRO_MINOR` | 0 | 次版本 |
| `_DISTRO_RELEASE` | "" | 发行标识空串 |

> **术语规范**：`Makefile.oever` 中的变量为该主流发行版专属标识符，agentrt-liunx 文档统一以 `_DISTRO_*` 占位表示，严禁出现原发行版字样。

#### 3.2.2 agentrt-liunx 复用方式 [IND]

agentrt-liunx 采纳"发行版版本元数据独立文件"的工程思想（[SS] 语义同源），但版本字段独立设计，不使用上述发行版字段名：

```makefile
# agentrt-liunx/Makefile.airymax — 发行版版本元数据（独立实现）
# SPDX-License-Identifier: GPL-2.0
AIRYMAX_LTS          = 1
AIRYMAX_MAJOR         = 1
AIRYMAX_MINOR         = 0
AIRYMAX_PATCH         = 1
AIRYMAX_RELEASE       = "开发阶段"
AIRYMAX_KBASE         = 6.6      # Linux 6.6 内核基线
AIRYMAX_SCHED_EXT     = 7        # SCHED_EXT=7（OLK-6.6 内置）
```

> **术语规范**：agentrt-liunx 基于 Linux 6.6 内核基线，参考主流 Linux 发行版的工程组织方式（独立版本元数据文件、Kbuild 递归下降），但版本字段独立命名，不与任何发行版字段重名。

### 3.3 `Kconfig` —— 配置系统入口

**源码路径**: `OLK-6.6: Kconfig:1-34`

`Kconfig` 是配置系统顶层入口，通过 `source` 指令递归引入各子系统配置：

```
mainmenu "Linux/$(ARCH) $(KERNELVERSION) Kernel Configuration"
source "scripts/Kconfig.include"
source "init/Kconfig"
source "kernel/Kconfig.freezer"
source "fs/Kconfig.binfmt"
source "mm/Kconfig"
source "net/Kconfig"
source "drivers/Kconfig"
source "fs/Kconfig"
source "security/Kconfig"
source "crypto/Kconfig"
source "lib/Kconfig"
source "lib/Kconfig.debug"
source "lib/Kconfig.<distro>"          # 发行版专属配置（占位，原文件含发行版字样）
source "Documentation/Kconfig"
```

#### 3.3.1 agentrt-liunx 复用方式 [IND]

agentrt-liunx 采纳 Kconfig 配置系统思想（[SS] 语义同源），但配置树独立组织，新增 agentrt-liunx 专属子系统配置：

```
# agentrt-liunx/Kconfig — 配置系统入口（独立实现）
mainmenu "agentrt-liunx $(AIRYMAX_VERSION) Kernel Configuration"
source "scripts/Kconfig.include"
source "init/Kconfig"
source "kernel/Kconfig.freezer"
source "mm/Kconfig"
source "net/Kconfig"
source "drivers/Kconfig"
source "fs/Kconfig"
source "security/Kconfig"
source "crypto/Kconfig"
source "lib/Kconfig"
source "lib/Kconfig.debug"
source "kernel/airymax/Kconfig"          # agentrt-liunx 专属：智能体调度
source "ipc/airymax/Kconfig"             # agentrt-liunx 专属：AgentsIPC
source "security/airymax/Kconfig"        # agentrt-liunx 专属：Cupolas capability
source "lib/airymax/Kconfig"             # agentrt-liunx 专属：Q16.16 定点库
source "Documentation/Kconfig"
```

### 3.4 `Kbuild` —— 顶层构建规则

**源码路径**: `OLK-6.6: Kbuild:1-99`

`Kbuild` 负责准备阶段（生成头文件）和目录递归下降：

| 阶段 | 产物 | 源码行号 | 说明 |
|------|------|----------|------|
| bounds | `include/generated/bounds.h` | L10-15 | 编译期常量边界 |
| timeconst | `include/generated/timeconst.h` | L17-24 | `CONFIG_HZ` 时间常量（用 bc 计算） |
| asm-offsets | `include/generated/asm-offsets.h` | L26-35 | 结构体偏移（汇编/C 接口） |
| syscalls 检查 | `missing-syscalls` | L37-44 | 系统调用完整性检查 |
| atomic 检查 | `atomic-checks` | L46-68 | 原子头 SHA1 完整性 |
| prepare | `prepare` | L70-74 | 准备阶段汇总 PHONY |
| 递归下降 | `obj-y += ...` | L79-98 | 子目录递归 |

#### 3.4.1 关键工程思想：asm-offsets

`asm-offsets` 是内核构建的关键工程：C 结构体字段偏移由编译器生成汇编，再提取为头文件，供汇编代码引用 C 结构体字段。agentrt-liunx 完整采纳此机制（[SS] 同源）。

```c
/* agentrt-liunx: kernel/airymax/offsets.c — 生成 asm-offsets（思想同源） */
#include <linux/kbuild.h>
#include <airymax/cognition_types.h>
#include <airymax/cupolas_types.h>

int main(void)
{
        DEFINE(AIRYMAX_COG_CTX_MSG_Q, offsetof(struct airymax_cog_ctx, msg_q));
        DEFINE(AIRYMAX_COG_CTX_WQ, offsetof(struct airymax_cog_ctx, wq));
        DEFINE(AIRYMAX_COG_CTX_TASK, offsetof(struct airymax_cog_ctx, task));
        DEFINE(AIRYMAX_CUPOLAS_CAP_NODE_NEXT,
               offsetof(struct airymax_cap_node, next));
        DEFINE(AIRYMAX_AGENTSIPC_HDR_MAGIC,
               offsetof(struct airymax_ipc_hdr, magic));
        return 0;
}
```

---

## 4. 编译器选项映射

### 4.1 `arch/x86/Makefile` —— x86 架构编译规则

**源码路径**: `OLK-6.6: arch/x86/Makefile:1-340`

#### 4.1.1 禁浮点选项（agentrt-liunx 核心约束来源）

agentrt-liunx 内核态禁用 `float`、用 Q16.16 定点数（`airymax_q16_t = int32_t`）的硬约束直接来源于 OLK-6.6 的 x86 编译选项：

| 选项 | 作用 | 源码行号 | agentrt-liunx 复用 |
|------|------|----------|---------------------|
| `-mno-sse -mno-mmx -mno-sse2 -mno-3dnow -mno-avx` | 禁用所有 SIMD 浮点指令集 | L70 | [SS] 完全采纳 |
| `-msoft-float` (32-bit) | 软浮点（禁硬件 FPU） | L96 | [SS] 完全采纳 |
| `-mno-80387` (64-bit) | 禁用 x87 FPU | L137 | [SS] 完全采纳 |

```
# OLK-6.6: arch/x86/Makefile:63-70 — 禁止 GCC 误生成浮点代码
#
# Prevent GCC from generating any FP code by mistake.
#
KBUILD_CFLAGS += -mno-sse -mno-mmx -mno-sse2 -mno-3dnow -mno-avx
```

```
# OLK-6.6: arch/x86/Makefile:96 — 32 位软浮点
KBUILD_CFLAGS += -msoft-float -mregparm=3 -freg-struct-return

# OLK-6.6: arch/x86/Makefile:137 — 64 位禁 x87
KBUILD_CFLAGS += -mno-80387
```

#### 4.1.2 Rust 同步禁浮点

OLK-6.6 对 Rust 编译也同步禁用浮点（`arch/x86/Makefile:71`）：

```
KBUILD_RUSTFLAGS += -Ctarget-feature=-sse,-sse2,-sse3,-ssse3,-sse4.1,-sse4.2,-avx,-avx2
```

agentrt-liunx 完整采纳此约束：**内核态 C 代码与 Rust 代码均禁浮点**，所有浮点运算改用 `airymax_q16_t`（Q16.16 定点数）。

#### 4.1.3 Q16.16 定点数实现示例

```c
/* agentrt-liunx: include/airymax/airymax_q16.h — Q16.16 定点数（禁浮点替代） */
#ifndef _AIRYMAX_Q16_H
#define _AIRYMAX_Q16_H

#include <linux/types.h>

typedef int32_t airymax_q16_t;          /* Q16.16 定点数：16 位整数 + 16 位小数 */
#define AIRYMAX_Q16_ONE      (1 << 16)  /* 1.0 */
#define AIRYMAX_Q16_HALF     (1 << 15)  /* 0.5 */
#define AIRYMAX_Q16_PI       205887L    /* 3.14159... * 65536 */

/* 整数 → Q16.16 */
static inline airymax_q16_t airymax_q16_from_int(int i)
{
        return (airymax_q16_t)(i << 16);
}

/* Q16.16 → 整数（截断） */
static inline int airymax_q16_to_int(airymax_q16_t q)
{
        return (int)(q >> 16);
}

/* Q16.16 乘法（用 int64_t 防溢出） */
static inline airymax_q16_t airymax_q16_mul(airymax_q16_t a, airymax_q16_t b)
{
        return (airymax_q16_t)(((int64_t)a * b) >> 16);
}

/* Q16.16 除法 */
static inline airymax_q16_t airymax_q16_div(airymax_q16_t a, airymax_q16_t b)
{
        return (airymax_q16_t)(((int64_t)a << 16) / b);
}

/* Q16.16 平方根（牛顿迭代，整数实现） */
static inline airymax_q16_t airymax_q16_sqrt(airymax_q16_t q)
{
        airymax_q16_t x = AIRYMAX_Q16_ONE;
        int i;

        if (q <= 0)
                return 0;
        for (i = 0; i < 16; i++)
                x = airymax_q16_div(airymax_q16_add(x, airymax_q16_div(q, x)), 2);
        return x;
}

#endif /* _AIRYMAX_Q16_H */
```

### 4.2 GCC / Clang 双编译器支持

#### 4.2.1 OLK-6.6 双编译器机制

OLK-6.6 同时支持 GCC 与 Clang，通过 `CONFIG_CC_IS_GCC` / `CONFIG_CC_IS_CLANG` 区分，典型例子（`arch/x86/Makefile:15-22`）：

```makefile
ifdef CONFIG_CC_IS_GCC
RETPOLINE_CFLAGS  := $(call cc-option,-mindirect-branch=thunk-extern -mindirect-branch-register)
endif
ifdef CONFIG_CC_IS_CLANG
RETPOLINE_CFLAGS  := -mretpoline-external-thunk
endif
```

栈对齐也按编译器区分（`arch/x86/Makefile:36-42`）：

```makefile
ifneq ($(call cc-option, -mpreferred-stack-boundary=4),)
      cc_stack_align4 := -mpreferred-stack-boundary=2
      cc_stack_align8 := -mpreferred-stack-boundary=3
else ifneq ($(call cc-option, -mstack-alignment=16),)
      cc_stack_align4 := -mstack-alignment=4
      cc_stack_align8 := -mstack-alignment=8
endif
```

#### 4.2.2 agentrt-liunx 复用方式 [IND]

agentrt-liunx 采纳双编译器支持思想（[SS] 同源），但构建规则独立实现：

```makefile
# agentrt-liunx: arch/x86/Makefile.airymax — 双编译器支持（独立实现）
ifdef CONFIG_CC_IS_GCC
AIRYMAX_RETPOLINE_CFLAGS := $(call cc-option,-mindirect-branch=thunk-extern)
AIRYMAX_CFLAGS_NOFLOAT   := -mno-sse -mno-mmx -mno-sse2 -mno-3dnow -mno-avx -mno-80387
else ifdef CONFIG_CC_IS_CLANG
AIRYMAX_RETPOLINE_CFLAGS := -mretpoline-external-thunk
AIRYMAX_CFLAGS_NOFLOAT   := -mno-sse -mno-mmx -mno-sse2 -mno-3dnow -mno-avx -mno-80387
endif

KBUILD_CFLAGS += $(AIRYMAX_CFLAGS_NOFLOAT)
export AIRYMAX_RETPOLINE_CFLAGS
```

---

## 5. 测试与验证工具映射

### 5.1 `lib/kunit/` —— KUnit 单元测试框架

**源码路径**: `OLK-6.6: lib/kunit/`（含 `test.c` / `executor.c` / `assert.c` / `string-stream.c` / `try-catch.c` 等 20+ 文件）

KUnit 是 Linux 内核内置的单元测试框架，无需用户态参与即可在内核态运行测试。核心机制：

| 组件 | 文件 | 作用 |
|------|------|------|
| 测试用例定义 | `kunit-test.c` | `KUNIT_DEFINE_TEST_CASE` 宏 |
| 测试执行器 | `executor.c` | 测试套件发现与运行 |
| 断言 | `assert.c` | `KUNIT_EXPECT_*` / `KUNIT_ASSERT_*` |
| 字符串流 | `string-stream.c` | 测试输出缓冲 |
| try-catch | `try-catch.c` | 异常捕获（崩溃不终止） |
| debugfs | `debugfs.c` | `/sys/kernel/debug/kunit/` |
| 静态桩 | `static_stub.c` | 函数替换测试 |

#### 5.1.1 agentrt-liunx 复用方式 [IND]

agentrt-liunx 采纳 KUnit 测试思想（[SS] 语义同源），针对智能体操作系统定制测试框架 `airymax-kunit`：

- **[SS] 同源**：采纳 `KUNIT_EXPECT_*` 断言宏、测试套件组织、debugfs 输出机制
- **[IND] 独立**：新增 Q16.16 定点数测试、kfifo IPC 测试、Cupolas capability 派生测试

```c
/* agentrt-liunx: lib/airymax/airymax_q16_test.c — KUnit 风格测试（独立实现） */
#include <kunit/test.h>
#include <airymax/airymax_q16.h>

static void airymax_q16_mul_test(struct kunit *test)
{
        airymax_q16_t a = airymax_q16_from_int(3);     /* 3.0 */
        airymax_q16_t b = airymax_q16_from_int(4);     /* 4.0 */
        airymax_q16_t r = airymax_q16_mul(a, b);        /* 期望 12.0 */

        KUNIT_EXPECT_EQ(test, airymax_q16_to_int(r), 12);
}

static void airymax_q16_div_test(struct kunit *test)
{
        airymax_q16_t a = airymax_q16_from_int(10);    /* 10.0 */
        airymax_q16_t b = airymax_q16_from_int(4);     /* 4.0 */
        airymax_q16_t r = airymax_q16_div(a, b);        /* 期望 2.5 */

        KUNIT_EXPECT_EQ(test, r, (1 << 16) + (1 << 15)); /* 2.5 = 2 + 0.5 */
}

static struct kunit_case airymax_q16_tests[] = {
        KUNIT_CASE(airymax_q16_mul_test),
        KUNIT_CASE(airymax_q16_div_test),
        {}
};

static struct kunit_suite airymax_q16_suite = {
        .name = "airymax_q16",
        .test_cases = airymax_q16_tests,
};
kunit_test_suite(airymax_q16_suite);
```

### 5.2 `tools/testing/selftests/` —— kselftest 自测框架

**源码路径**: `OLK-6.6: tools/testing/selftests/`

kselftest 是用户态自测框架，覆盖 80+ 子系统（节选）：

| 子目录 | 测试内容 |
|--------|----------|
| `bpf/` | eBPF 程序测试 |
| `cgroup/` | cgroup 行为 |
| `capabilities/` | capability 语义 |
| `clone3/` | clone3 系统调用 |
| `cpu-hotplug/` | CPU 热插拔 |
| `damon/` | DAMON 内存访问监测 |
| `drivers/` | 驱动测试 |
| `exec/` | exec 语义 |
| `memfd/` | memfd_create |
| `net/` | 网络栈 |
| `sched_ext/` | sched_ext 调度器（agentrt-liunx 核心） |
| `seccomp/` | seccomp 沙箱 |

#### 5.2.1 agentrt-liunx 复用方式 [IND]

agentrt-liunx 采纳 kselftest 自测思想（[SS] 同源），新增智能体操作系统专属自测：

```bash
# agentrt-liunx: tools/testing/selftests/airymax/Makefile — 自测组织
CFLAGS += -Wall -O2 -g
TEST_GEN_PROGS := \
        airymax_q16_test        \
        airymax_kfifo_ipc_test  \
        airymax_cupolas_test     \
        airymax_agentsipc_test   \
        airymax_sched_agent_test

include ../lib.mk
```

### 5.3 `tools/testing/kunit/` + `ktest` —— 其他测试基础设施

| 工具 | 路径 | 作用 |
|------|------|------|
| `kunit` | `tools/testing/kunit/` | KUnit 运行器（Python） |
| `ktest` | `tools/testing/ktest/` | 内核配置自动化测试 |
| `fault-injection` | `tools/testing/fault-injection/` | 故障注入 |
| `nvdimm` | `tools/testing/nvdimm/` | NVDIMM 模拟 |
| `cxl` | `tools/testing/cxl/` | CXL 设备模拟（agentrt-liunx MemoryRovol 参考用） |

### 5.4 静态分析工具链：sparse / Smatch / Coccinelle

#### 5.4.1 sparse

**源码路径**: `OLK-6.6: Makefile:111-119`（`make C=1` 启用）

sparse 是 Linux 内核专用 C 静态分析器，检查类型安全（`__bitwise`）、RCU 锁定、地址空间标注等。`Makefile:111-119`：

```makefile
# Use 'make C=1' to enable checking of only re-compiled files.
# Use 'make C=2' to enable checking of *all* source files.
```

#### 5.4.2 Smatch

Smatch 是 sparse 的扩展，检查未初始化变量、空指针解引用、缓冲区溢出等。源码树中通过 `scripts/coccicheck` 集成。

#### 5.4.3 Coccinelle

**源码路径**: `OLK-6.6: scripts/coccicheck` + `scripts/coccinelle/`

Coccinelle 是模式驱动的代码变换工具，用语义补丁（SmPL）检测 API 误用模式。`scripts/coccinelle/` 含 9 个子目录的语义补丁集：

| 子目录 | 检查模式 |
|--------|----------|
| `api/` | API 误用 |
| `alloc/` | 内存分配 |
| `checkpatch/` | 风格检查 |
| `compare/` | 比较运算 |
| `deref/` | 解引用 |
| `free/` | 释放 |
| `iterators/` | 迭代器 |
| `locks/` | 锁 |
| `misc/` | 杂项 |

#### 5.4.4 agentrt-liunx 复用方式 [IND]

agentrt-liunx 采纳三类静态分析工具链思想（[SS] 同源），但工具链独立集成：

- **[SS] 同源**：采纳 sparse 的 `__bitwise` 类型标注、Smatch 的空指针检查、Coccinelle 的语义补丁模式
- **[IND] 独立**：新增 agentrt-liunx 专属检查规则（禁浮点检查、kfifo IPC 检查、Cupolas capability 派生链检查）

```c
/* agentrt-liunx: include/airymax/airymax_sparse.h — sparse 类型标注（独立实现） */
#ifdef __CHECKER__
#define airymax_q16_t __bitwise int32_t   /* 强类型：禁止与普通 int 混用 */
#define __airymax_user   __user           /* 用户态指针 */
#define __airymax_rcu    __rcu           /* RCU 保护指针 */
#define __airymax_cap     __bitwise       /* capability 令牌强类型 */
#else
typedef int32_t airymax_q16_t;
#define __airymax_user
#define __airymax_rcu
#define __airymax_cap
#endif
```

---

## 6. Rust 支持映射

### 6.1 `rust/` —— Rust 内核支持

**源码路径**: `OLK-6.6: rust/`

Linux 6.6 引入实验性 Rust 内核模块支持。`rust/` 目录组织：

| 子目录/文件 | 作用 | 说明 |
|-------------|------|------|
| `Makefile` | Rust 构建规则 | 19,751 字节 |
| `kernel/` | Rust 内核抽象层 | `sync/`、`fs/`、`net/`、`drivers/` |
| `alloc/` | Rust alloc 集成 | 内核定制分配器 |
| `bindings/` | C → Rust 绑定 | `bindgen` 生成 |
| `macros/` | Rust 过程宏 | `module!` 宏 |
| `uapi/` | UAPI 绑定 | 用户态接口 |
| `helpers.c` | C 辅助函数 | Rust 调用 C 的桥接 |
| `compiler_builtins.rs` | 编译器内置 | intrinsics |
| `build_error.rs` | 编译期错误 | `build_error!` |
| `exports.c` | 符号导出 | Rust 符号导出给 C |
| `bindgen_parameters` | bindgen 参数 | 头文件处理配置 |

#### 6.1.1 `rust/Makefile` 关键规则

```makefile
# OLK-6.6: rust/Makefile:1-30 节选
obj-$(CONFIG_RUST) += core.o compiler_builtins.o
always-$(CONFIG_RUST) += exports_core_generated.h
obj-$(CONFIG_RUST) += helpers.o
CFLAGS_REMOVE_helpers.o = -Wmissing-prototypes -Wmissing-declarations
always-$(CONFIG_RUST) += libmacros.so
always-$(CONFIG_RUST) += bindings/bindings_generated.rs
obj-$(CONFIG_RUST) += alloc.o bindings.o kernel.o
always-$(CONFIG_RUST) += uapi/uapi_generated.rs
obj-$(CONFIG_RUST) += uapi.o
obj-$(CONFIG_RUST) += exports.o
```

### 6.2 `samples/rust/` —— Rust 样例

**源码路径**: `OLK-6.6: samples/rust/`

#### 6.2.1 `rust_minimal.rs` —— 最小 Rust 模块

```rust
// OLK-6.6: samples/rust/rust_minimal.rs:1-38
// SPDX-License-Identifier: GPL-2.0

//! Rust minimal sample.

use kernel::prelude::*;

module! {
    type: RustMinimal,
    name: "rust_minimal",
    author: "Rust for Linux Contributors",
    description: "Rust minimal sample",
    license: "GPL",
}

struct RustMinimal {
    numbers: Vec<i32>,
}

impl kernel::Module for RustMinimal {
    fn init(_module: &'static ThisModule) -> Result<Self> {
        pr_info!("Rust minimal sample (init)\n");
        pr_info!("Am I built-in? {}\n", !cfg!(MODULE));

        let mut numbers = Vec::new();
        numbers.try_push(72)?;
        numbers.try_push(108)?;
        numbers.try_push(200)?;

        Ok(RustMinimal { numbers })
    }
}

impl Drop for RustMinimal {
    fn drop(&mut self) {
        pr_info!("My numbers are {:?}\n", self.numbers);
        pr_info!("Rust minimal sample (exit)\n");
    }
}
```

#### 6.2.2 `samples/rust/Kconfig` —— Rust 样例配置

```
menuconfig SAMPLES_RUST
        bool "Rust samples"
        depends on RUST

if SAMPLES_RUST
config SAMPLE_RUST_MINIMAL
        tristate "Minimal"
config SAMPLE_RUST_PRINT
        tristate "Printing macros"
config SAMPLE_RUST_HOSTPROGS
        bool "Host programs"
endif
```

### 6.3 agentrt-liunx 复用方式 [IND]

agentrt-liunx 评估 Rust 支持现状（Linux 6.6 仍为实验性），采取保守策略：

| 维度 | OLK-6.6 现状 | agentrt-liunx 策略 | 边界 |
|------|--------------|---------------------|------|
| Rust 内核模块 | 实验性支持（`CONFIG_RUST`） | 1.0.1 阶段不启用内核态 Rust | [IND] |
| Rust 用户态 | 不涉及 | agentrt 微核心可用 Rust 编写用户态 daemon | [IND] |
| Q16.16 替代 | Rust 同步禁浮点（`-Ctarget-feature=-sse...`） | Rust 代码同样禁浮点，用 `i32` 模拟 Q16.16 | [SS] |
| `module!` 宏 | Rust 模块声明宏 | agentrt-liunx 用户态 daemon 用 Rust 重写时参考 | [IND] |

#### 6.3.1 agentrt-liunx Rust 用户态 daemon 示例（独立实现）

agentrt-liunx 的 12 daemons 可用 Rust 编写用户态服务（[IND] 完全独立），参考 `rust_minimal.rs` 的 `module!` 宏思想：

```rust
// agentrt-liunx: agents/cognition-daemon/src/lib.rs — 用户态 daemon（独立实现）
// SPDX-License-Identifier: GPL-2.0

//! agentrt-liunx 认知循环 daemon（用户态微核心服务）

use airymax_prelude::*;

agent_daemon! {
    type: CognitionDaemon,
    name: "cognition-daemon",
    version: "1.0.1",
    description: "agentrt-liunx CoreLoopThree 认知循环用户态服务",
}

/// Q16.16 定点数（内核态禁浮点约束延伸到用户态 daemon）
type AirymaxQ16 = i32;
const AIRYMAX_Q16_ONE: AirymaxQ16 = 1 << 16;

fn q16_mul(a: AirymaxQ16, b: AirymaxQ16) -> AirymaxQ16 {
    (((a as i64) * (b as i64)) >> 16) as i32
}

impl AgentDaemon for CognitionDaemon {
    fn init(_ctx: &DaemonContext) -> Result<Self> {
        pr_info!("cognition-daemon (init)\n");
        // 通过 io_uring 与内核态 sched_ext 通信
        Ok(CognitionDaemon { budget: AIRYMAX_Q16_ONE })
    }

    fn think(&mut self, token_budget: AirymaxQ16) -> Result<AirymaxQ16> {
        let cost = q16_mul(token_budget, 3 << 14); /* 0.5 * 3 = 1.5? 校正为正确比例 */
        self.budget -= cost;
        Ok(self.budget)
    }
}
```

> **术语规范**：上述 `agent_daemon!` 宏参考 Linux 6.6 `module!` 宏的组织思想（[SS] 语义同源），但完全独立实现，服务于 agentrt-liunx 用户态 daemon 体系。

---

## 7. agentrt-liunx 工程工具链复用策略总览 [IND]

### 7.1 复用矩阵

| 工具类别 | OLK-6.6 源 | agentrt-liunx 对应 | 边界 | 复用深度 |
|----------|-----------|---------------------|------|----------|
| 编码风格 | `coding-style.rst` | `agentrt-liunx基本工程标准规范.md` | [SS] | 逐条采纳 |
| 风格检查 | `checkpatch.pl` (Perl) | `airymax-checkpatch` (Python) | [IND] | 思想同源，独立重写 |
| 文档提取 | `kernel-doc` (Perl) | `airymax-kdoc` (Sphinx 扩展) | [IND] | 思想同源，独立重写 |
| 自动格式化 | `.clang-format` | `.clang-format`（定制） | [IND] | 核心配置同源，宏列表独立 |
| 顶层构建 | `Makefile` | `Makefile` + `Makefile.airymax` | [IND] | 递归下降思想同源 |
| 版本元数据 | `Makefile.oever` | `Makefile.airymax` | [IND] | 文件组织同源，字段独立 |
| 配置系统 | `Kconfig` | `Kconfig`（增 agentrt 子树） | [IND] | 系统同源，配置树独立 |
| 构建规则 | `Kbuild` | `Kbuild`（增 airymax 目录） | [IND] | 机制同源 |
| 禁浮点 | `arch/x86/Makefile` | `arch/x86/Makefile.airymax` | [SS] | 完全采纳，加 Q16.16 库 |
| 双编译器 | `CONFIG_CC_IS_GCC/CLANG` | 同 | [SS] | 完全采纳 |
| 单元测试 | `lib/kunit/` | `airymax-kunit` | [IND] | 框架同源，测试用例独立 |
| 自测 | `tools/testing/selftests/` | `selftests/airymax/` | [IND] | 框架同源，用例独立 |
| 静态分析 | sparse/Smatch/Coccinelle | 同（加 agentrt 规则） | [SS] | 工具复用，规则独立 |
| Rust 内核 | `rust/`（实验性） | 1.0.1 不启用内核态 Rust | [IND] | 评估跟踪 |
| Rust 用户态 | — | agentrt daemon 可用 Rust | [IND] | 独立采纳 |

### 7.2 工程标准加严项

agentrt-liunx 在 OLK-6.6 工程标准基础上，针对智能体操作系统场景加严：

| 加严项 | OLK-6.6 | agentrt-liunx | 理由 |
|--------|---------|----------------|------|
| 内核态浮点 | 禁（x86） | 全架构禁 + 强制 Q16.16 | 智能体负载需确定性 |
| kthread 间 IPC | 无约束 | 强制 kfifo + wait_event | 避免用户态 io_uring 滥用 |
| 定点数类型 | 无 | `airymax_q16_t` 强类型 | 防止 float 误入内核 |
| capability | POSIX cap | Cupolas 派生链（seL4 思想） | 智能体动态权限 |
| IPC 消息头 | 无固定格式 | AgentsIPC 128B 固定头 | 快路径优化 |

### 7.3 [IND] 独立性声明

agentrt-liunx 工程工具链整体属于 **[IND] 完全独立层**：

1. **不复制 OLK-6.6 源码**：`checkpatch.pl`、`kernel-doc`、`.clang-format`、`Makefile`、`Kbuild` 等均不直接复制
2. **采纳工程思想**：Tab 8、K&R、Kbuild 递归下降、禁浮点、双编译器、KUnit/kselftest 框架思想
3. **独立实现工具**：`airymax-checkpatch`、`airymax-kdoc`、`Makefile.airymax`、`airymax-kunit` 等
4. **兼容主流发行版**：工程实现方式与主流 Linux 发行版保持一致性，便于未来兼容主流发行版标准工具链
5. **不照搬发行版字段**：版本元数据字段独立命名（`AIRYMAX_*`），不与任何发行版字段重名

---

## 8. 与开源文档的关系

- 本映射文档是**闭源参考**，不对外发布
- 开源设计文档（`docs/AirymaxAgentOS/`）引用本映射结论时，必须用 agentrt-liunx 自身语言表述
- 开源文档中**严禁**出现 OLK-6.6 源码路径、行号、函数名等直接引用
- 开源文档中**严禁**出现任何主流 Linux 发行版的名称

---

## 9. 相关文档

| 文档 | 关系 |
|------|------|
| `02-olk66-source-mapping/01-sched-ext-mapping.md` | sched_ext 源码映射（SCHED_AGENT） |
| `02-olk66-source-mapping/02-io-uring-mapping.md` | io_uring 源码映射（AgentsIPC） |
| `02-olk66-source-mapping/03-bpf-mapping.md` | eBPF 源码映射（Cupolas L1） |
| `03-microkernel-design-ref/05-sel4-extension-plan.md` | seL4 微内核拓展型改造方案 |
| `agentrt-liunx基本工程标准规范.md` | agentrt-liunx 工程标准规范（本文档映射目标） |

---

## 10. 附录：关键源码文件清单

### 10.1 OLK-6.6 工程工具链源码清单

| 文件 | 行数 | 用途 |
|------|------|------|
| `Documentation/process/coding-style.rst` | 1,271 | 编码风格规范 |
| `scripts/checkpatch.pl` | 7,823 | 补丁风格检查 |
| `scripts/kernel-doc` | 2,531 | 文档提取 |
| `.clang-format` | 689 | 自动格式化 |
| `Makefile` | 2,076 | 顶层构建 |
| `Makefile.oever` | 5 | 发行版版本元数据 |
| `Kconfig` | 34 | 配置入口 |
| `Kbuild` | 99 | 构建规则 |
| `arch/x86/Makefile` | 340 | x86 编译规则 |
| `rust/Makefile` | ~600 | Rust 构建 |
| `samples/rust/rust_minimal.rs` | 38 | Rust 最小样例 |
| `lib/kunit/test.c` | — | KUnit 核心 |
| `tools/testing/selftests/Makefile` | — | kselftest 组织 |

### 10.2 agentrt-liunx 工程工具链目标清单

| 文件 | 用途 | 状态 |
|------|------|------|
| `Makefile.airymax` | 版本元数据 | 1.0.1 规划 |
| `.clang-format` | 自动格式化（定制） | 1.0.1 规划 |
| `scripts/airymax-checkpatch` | 风格检查（Python） | 1.0.1 规划 |
| `scripts/airymax-kdoc` | 文档提取（Sphinx 扩展） | 1.0.1 规划 |
| `kernel/airymax/Kconfig` | 智能体调度配置 | 1.0.1 规划 |
| `include/airymax/airymax_q16.h` | Q16.16 定点数 | 1.0.1 规划 |
| `lib/airymax/airymax_q16_test.c` | Q16.16 单元测试 | 1.0.1 规划 |
| `tools/testing/selftests/airymax/` | agentrt-liunx 自测 | 1.0.1 规划 |

---

> **文档结束** | Copyright (c) 2025-2026 SPHARX Ltd. All Rights Reserved. | 闭源内部参考（docs-closed）
