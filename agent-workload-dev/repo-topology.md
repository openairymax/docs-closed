# Airymax 仓库层级组织与 Git 约定（repo-topology）

> 状态：2026-09-03 确立（0.1.9 发布前分支拓扑收口）。
> 适用：openairymax 组织全部仓库（atomgit SSoT + GitHub/Gitee 镜像）。

## 1. 克隆树（工作区层级）

```
spharxworks/                  ← 顶层父仓（remote: openairymax/spharxworks；模块名历史为 OpenAirymax）
├── airymaxhub/               ← 伞仓（remote: openairymax/airymaxhub；聚合全部开源仓）
│   ├── agent-linux/          ← 内核/驱动仓
│   ├── agent-workload/       ← 运行时工作负载聚合仓
│   │   ├── agentrt/          ← AgentRT 机制核单仓（内含 atoms/commons/daemons/
│   │   │                        gateway/heapstore/protocols 六个叶子仓）
│   │   ├── products/         ← 策略模块聚合仓（memoryrovol/cupolas 子模块 +
│   │   │                        lang_gateway 内联模块）
│   │   ├── ecosystem/        ← 生态仓（manager/skills/markets…）
│   │   └── sdk/              ← SDK 聚合仓（console/tui/desktop/docker/
│   │                            sdk-rust/sdk-python/sdk-go/sdk-typescript 八个叶子仓）
│   ├── tools/                ← CI/质量门禁/发布脚本仓
│   └── docs/                 ← 公开文档仓（docs/AirymaxRT 等）
│       └── docs-closed/      ← 闭源工程文档仓（**docs 的子模块**，不是伞仓直接
│                                子模块；本文件所在；sync-mirror SKIP）
├── spharxtools/              ← 独立工具仓（模块名历史为 SpharxTools）
├── works-engineering/        ← 构建打包台（源码区外，不入仓；流程 SSoT 在
│                                airymaxhub/tools/scripts/ci/release）
└── sync-upstream/            ← 上游同步脚本区
```

层级深度：父仓 → 伞仓 → agent-workload → agentrt/sdk → 叶子仓（5 级）。
全部以 **gitlink（commit hash 钉死）** 聚合；构建/CI 取钉住 hash，与分支名无关。

## 2. 分支约定

| 仓类 | 开发分支 | main 语义 |
|---|---|---|
| 聚合/上层仓（spharxworks、airymaxhub、agent-workload、agentrt、sdk、products、ecosystem、tools、docs、docs-closed、developbuild、agent-linux） | **main** 直开 | 持续集成主线 |
| 叶子仓（atoms、commons、cupolas、daemons、gateway、heapstore、protocols、console、tui、desktop、docker、sdk-rust、sdk-python、sdk-go、sdk-typescript） | **dev/hubs-01**（标准开发分支） | **发布快照**：每次 release 时快进/合并同步一次，日常不更新 |

- 叶子仓禁止直接在 main 上提交；main 只接受发布期同步（快进优先，分叉用 merge）。
- 历史上 atoms/cli 的 main 曾含 atomgit MR 自动合并提交（`!N merge develop into main`），
  已于 2026-09-03 调和：merge 并入 dev/hubs-01 后 main 快进同 tip，main=发布快照单点一致。

## 3. 发布快照同步操作（每次 release 执行一次）

1. 叶子仓（11 仓纯落后）：`git push origin dev/hubs-01:main`（快进，零新提交）。
2. 叶子仓（分叉时）：`git merge origin/main` 于 dev/hubs-01（merge-tree 预检冲突 →
   零冲突方可），推送 dev/hubs-01 + main；若 tip 变化须同步升级 gitlink 钉住 hash。
3. gitlink 逐级 bump：叶子 → agentrt/sdk → agent-workload → airymaxhub → spharxworks。
4. 验证：`git submodule status` 全空间前缀、各仓 `origin/main..HEAD` 为空。

## 4. 子模块要点

- **闭源子模块**（docs-closed、developbuild）：在 sync-mirror SKIP_LIST 内，无公网
  镜像；本地以 SSH URL 注册（2026-09-03 已 `git submodule init` 正式注册，此前为
  手动检出未注册态，`submodule status` 显示 `-`）。
- **模块名与路径名**允许不一致（git 机制）：如 spharxworks 内模块名 `OpenAirymax`
  对应路径 airymaxhub、`SpharxTools` 对应 spharxtools；airymaxhub 内 docs-closed
  的历史 gitdir 名为 `doc-closed`（早期命名残留，不改动不阻塞）。
- `.gitmodules` URL 风格：公开仓用相对 URL（`../<repo>.git`，随镜像自适应）；
  闭源仓用绝对 SSH URL（`git@atomgit.com:openairymax/<repo>.git`）。
- 定向检出（CI/release）：`bash airymaxhub/.github/scripts/init-submodules.sh <子树>`
  （不可全量 `submodules:true`——agent-linux 含 ~2.5GB kernel 且闭源子模块在 GitHub
  不存在）。

## 5. 2026-09-03 收口记录

- 叶子仓 origin/main 曾全面滞后 dev/hubs-01（daemons 183、atoms 114、commons
  101、tui 98…）：11 仓快进同步至 dev/hubs-01 tip（哈希不变，gitlink 不动）。
- atoms（`6bb49e7`，merge main 独有 6 个 MR 提交）、cli（`9c018a2`，1 个 MR 提交）
  零冲突调和，gitlink 随 agentrt `acd22cfce` / sdk `3bba94b` 升级，链至伞仓 `45471b2`。
- 父仓 spharxworks gitlink bump 至伞仓最新并推送（`fa0790a`）；works-engineering/
  README.md 明确不入父仓（.gitignore）。
- 伞仓 4 子模块（agent-linux/agent-workload/docs/tools）全部正式注册，`submodule
  status` 无 `-`/`+` 异常；`docs-closed` 是 **`docs` 仓的子模块**（不是伞仓直接子
  模块），随 `docs` gitlink 一起升级。

## 6. 2026-10-07 分支命名收口记录

- **事实**：§2 原记「叶子仓标准开发分支 = `develop/hubs-01`」，但实测全部叶子仓
  （分组清单见 §2）远端**仅存在**
  `dev/hubs-01` 与 `main`，**不存在** `develop/hubs-01`（`distro` 例外：两分支并存，
  `origin/HEAD → develop/hubs-01`）。
- **影响**：`.gitmodules` 声明的 `develop/hubs-01` 为不存在分支，`git submodule
  update --remote` 必然失败；违反 `agentrt-linux基本工程标准规范.md` VCS-03
  「`.gitmodules` 声明分支须与实际检出分支一致」。
- **裁定**：**以实际为准**，全部统一为 `dev/hubs-01`（含 `ecosystem/agents` 由 `main`
  改 `dev/hubs-01`；`agent-linux/kernel` 声明 `ALK-6.6-dev` 与实际一致，不动）。
- **落点**：`agentrt 4beebb84e`、`sdk c241a71`、`products 5a75759`、`ecosystem 4fb7f46`、
  `agent-linux f55229f` 五仓 `.gitmodules` 收口；gitlink 逐级 bump 至 `agent-workload
  ab7eba6` → `airymaxhub 2abcf98`。
- **零构建影响**：§1 明确「构建/CI 取钉住 hash，与分支名无关」，故本次为纯元数据订正。

## 7. 2026-10-09 机制/策略分离收口记录

- **背景**：贯彻「机制/策略分离」，`products` 由「产品交付聚合」重定位为
  **策略模块聚合路径**：`memoryrovol`（submodule，L5 专有） + `cupolas`
  （submodule，L3 开源安全框架） + `lang_gateway`（in-tree 内联模块，非 submodule）。
- **迁移**：两个客户端——`desktop`（Tauri 桌面客户端）与 `docker`（容器交付资产）
  ——由 `products/` 移出，落于 `sdk/`（面向用户的交互组件与交付载体归 SDK 聚合）。
- **metadata 变更**：`products/.gitmodules` 4 条 → **2 条**（memoryrovol、cupolas）；
  `sdk/.gitmodules` 6 条 → **8 条**（新增 desktop、docker）。两 leaf 的 gitlink 逐字
  沿用原值（`desktop df7c14c7…`、`docker 9dd8fc17…`），零内容改动。
- **同步面**：`sync-mirror.sh` 以 `.gitmodules` 动态 BFS 解析（种子含 sdk/products），
  `init-submodules.sh` 以 `clone_sibling` 定向检出——二者逻辑均不受迁移影响。
- **零构建影响**：迁移仅改聚合层级与元数据；构建/CI 取钉住 hash，不受影响。
