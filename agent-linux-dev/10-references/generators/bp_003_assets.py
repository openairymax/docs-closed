# -*- coding: utf-8 -*-
"""AirymaxOS 0.0.3 存量抵扣基线快照（ASSET_BASELINE）。

账本生成器曾在**工作树**上实测证据仓的文件桶规模。工作树只增不减，同一份种子
重放得到的抵扣额会随证据仓继续开发而变大，已发布账本的 B0 锚点（`L-05`/`A-11`）
被整包剔除，生成器在里程碑断言处失败（TD-06）。本模块把账本首发时刻的实测值
冻结成数据，生成器只读快照，账本因此可确定性重放。

基线（2026-10-15 账本首发时刻的证据仓）：
  agent-linux  db9a9fc31e8bb43a1e9877f413c13e982d01a283
  kernel       52bf9cf94225ab5d5756354b097860194b330e20

桶口径（路径相对 agent-linux，行数按 `wc -l` 统计）：
  K-syscalls      kernel/kernel/syscalls/*.{c,h}
  K-superv        kernel/kernel/superv/*.{c,h}
  K-corekern      kernel/kernel/corekern/*.{c,h}（排除 ipc/ 子目录）
  K-corekern-ipc  kernel/kernel/corekern/ipc/*.{c,h}
  K-ipc           kernel/kernel/ipc/*.{c,h}
  K-sec           kernel/security/airy/*.{c,h}
  K-init          kernel/init/airy*.c
  K-uapi          kernel/include/uapi/linux/airymax/**
  T-codegen       tools/codegen/*.py
  T-dsl           tools/dsl/*.py
  T-tricomp       tools/sc-tri-compile/*.py
  T-abi           tools/abi-check/*.py
  T-workflow      .github/workflows/**
  T-defconfig     kernel/arch/**/airy_defconfig
  K-AIRYHDR       kernel/include/airymax/**
  K-LOG           kernel/kernel/log/*.{c,h}
  T-TOOLSROOT     tools/*.py（根目录）
  K-VENDORCFG     kernel/configs/**

改写本文件等于重新发布一次账本，属于显式动作；日常开发提交不得触碰这些数值。
"""

BASELINE_AGENT_LINUX = "db9a9fc31e8bb43a1e9877f413c13e982d01a283"
BASELINE_KERNEL = "52bf9cf94225ab5d5756354b097860194b330e20"
BASELINE_DATE = "2026-10-15"

# 桶 id -> (文件数, 行数)
MAPPED = {
    "K-syscalls": (3, 564),
    "K-superv": (4, 173),
    "K-corekern": (18, 1233),
    "K-corekern-ipc": (6, 1221),
    "K-ipc": (3, 203),
    "K-sec": (12, 2357),
    "K-init": (1, 28),
    "K-uapi": (18, 2463),
    "T-codegen": (15, 4701),
    "T-dsl": (12, 2137),
    "T-tricomp": (3, 1348),
    "T-abi": (3, 1347),
    "T-workflow": (11, 1164),
    "T-defconfig": (5, 786),
}

UNMAPPED = {
    "K-AIRYHDR": (2, 78),
    "K-LOG": (3, 526),
    "T-TOOLSROOT": (43, 11940),
    "K-VENDORCFG": (7, 18509),
}

MAPPED_TOTAL = (114, 19725)
UNMAPPED_TOTAL = (55, 31053)
