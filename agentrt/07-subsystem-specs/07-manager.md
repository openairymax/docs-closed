# Manager 子系统边界文档

> **版本**: v1.0.0 | **日期**: 2026-06-18 | **团队**: B
> **代码路径**: `ecosystem/manager/`

## 1. 职责边界

### 核心职责

| 职责 | 说明 |
|------|------|
| 配置中心化管理 | 全系统配置的唯一真相源（Single Source of Truth），统一管理内核、模型、安全、日志、Agent、Skill、工具服务等所有模块的配置定义 |
| JSON Schema 驱动校验 | 基于 11 个 JSON Schema 文件（约 272 项校验规则）的三级校验：语法校验 → Schema 校验 → 语义校验 |
| 三层配置覆盖 | 支持 Base（基础设施）→ Environment（环境差异）→ Runtime（动态调整）三层配置合并，高优先级覆盖低优先级 |
| 配置热重载 | 基于文件监控的配置变更实时生效，支持 SIGHUP 信号触发，30 秒轮询间隔 |
| 配置版本控制 | Git 后端的配置版本管理，支持自动提交、分支管理、最多 100 个版本保留 |
| 配置回滚 | 支持最多 10 步回滚，自动回滚条件（加载失败、验证失败、启动失败），需要确认 |
| 配置漂移检测 | 基于 SHA-256 哈希的文件完整性校验，三级严重程度（INFO/WARNING/CRITICAL），敏感文件变更自动标记为 CRITICAL |
| 审计日志 | 7 种动作类型（LOAD/RELOAD/CHANGE/ROLLBACK/VALIDATE/EXPORT/IMPORT），3 种操作者类型（user/system/ci_cd），SHA-256 校验和，支持关联 ID 和工单号 |
| 配置加密 | AES-256-GCM 加密敏感字段（API Key、密码、密钥），支持 env/file/vault 三种密钥来源 |
| 配置导入导出 | 支持 YAML/JSON 格式，导入时 Schema 验证，排除敏感字段，支持 replace/merge/deep_merge 三种合并策略 |
| 配置差异对比 | YAML/JSON 配置文件的结构化深度比较，支持单文件和批量目录比较，彩色输出和 JSON 报告 |
| Schema 同步检查 | Manager 11 Schema 与 agentrt.yaml 的双向一致性检查，检测字段不一致、Schema 漂移和缺失配置 |
| 多实例配置同步 | 基于 Redis 的配置同步机制（可选），支持 last_write_wins 冲突解决策略 |
| 性能基准测试 | TaskManager/SessionManager/MemoryManager/SkillManager 四大模块的性能基准测试框架 |

### 非职责（明确排除）

- 不负责配置的运行时执行（运行时的配置消费者负责）
- 不负责 Agent 的实际调度与执行（由 OpenLab 负责）
- 不负责数据持久化存储（由 heapstore/Checkpoint 负责）
- 不负责网络通信协议（由 protocols 层负责）
- 不负责服务发现与注册（由 tool_d 守护进程负责）

## 2. 公共接口

### 核心文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| `schema_diff.py` | Python CLI | Manager Schema 与 agentrt.yaml 双向一致性检查 |
| `tools/config_diff.py` | Python CLI | 配置文件差异对比工具 |
| `tools/drift_detector.py` | Python CLI | 配置漂移检测（基线创建/检测/报告） |
| `tools/config_version_cleanup.py` | Python CLI | 配置版本历史清理（按天数/版本数） |
| `tools/audit_log_generator.py` | Python CLI | 审计日志生成器（测试用） |
| `benchmark/benchmark_manager.py` | Python CLI | Manager 模块性能基准测试 |

### 关键 API 签名

```python
# === Schema Diff (schema_diff.py) ===
class SchemaDiffer:
    def __init__(self, airy_root: Optional[str] = None)
    def run(self) -> DiffReport

# === Config Diff (tools/config_diff.py) ===
def compare_configs(file1: str, file2: str) -> DiffResult
def load_config_file(filepath: str) -> Tuple[Optional[Dict], Optional[str]]

# === Drift Detector (tools/drift_detector.py) ===
class ConfigDriftDetector:
    def __init__(self, config_dir: Path, baseline_dir: Optional[Path] = None, verbose: bool = False)
    def create_baseline(self) -> Path
    def detect_drift(self) -> DriftReport
    def export_report_json(self, report: DriftReport, output_path: Path) -> None
    def export_report_markdown(self, report: DriftReport, output_path: Path) -> None

# === Audit Log Generator (tools/audit_log_generator.py) ===
class AuditLogGenerator:
    def __init__(self, config_dir: Path)
    def generate_entry(self, action, config_file, operator_type, environment, reason, include_changes) -> AuditLogEntry
    def generate_batch(self, count: int = 10, environment: str = "production") -> List[AuditLogEntry]
    def export_to_json(self, entries: List[AuditLogEntry], output_path: Path) -> None

# === Version Cleanup (tools/config_version_cleanup.py) ===
class ConfigVersionCleanup:
    def __init__(self, history_dir: str, dry_run: bool = False, verbose: bool = False)
    def cleanup(self, retention_days, max_versions, compress_after) -> CleanupResult

# === Benchmark (benchmark/benchmark_manager.py) ===
class PerformanceBenchmark:
    def measure(self, name: str, func: Callable, iterations: int, warmup: int) -> BenchmarkResult
    def print_summary(self) -> None
    def save_results(self, filepath: str) -> None
```

### CLI 命令

```bash
# Schema 同步检查
python -m ecosystem.manager.schema_diff --report --check
python -m ecosystem.manager.schema_diff --json

# 配置差异对比
python manager/tools/config_diff.py file1.yaml file2.yaml
python manager/tools/config_diff.py --dir ./config --baseline ./baseline

# 配置漂移检测
python manager/tools/drift_detector.py --action both --output drift_report.json
python manager/tools/drift_detector.py --action detect --verbose

# 版本历史清理
python manager/tools/config_version_cleanup.py --days 90
python manager/tools/config_version_cleanup.py --max-versions 100

# 审计日志生成
python manager/tools/audit_log_generator.py --count 10 --output audit.json

# 性能基准测试
python manager/benchmark/benchmark_manager.py --iterations 1000
```

### 错误码

| 错误码 | 说明 |
|--------|------|
| 退出码 0 | 操作成功，Schema 一致 |
| 退出码 1 | Schema 漂移检测到错误 |
| 退出码 2 | 运行时错误 |
| `SCHEMA_VIOLATION` | Schema 验证失败 |
| `FileNotFoundError` | 配置文件不存在 |
| `RuntimeError` | 基线不存在或目录不存在 |

## 3. 依赖关系

### 内部依赖

| 依赖模块 | 用途 |
|----------|------|
| `agentrt.yaml` | AgentRT 主配置文件，Schema 同步检查的目标 |
| `agentrt.modules.task.manager` | 任务管理器（基准测试） |
| `agentrt.modules.session.manager` | 会话管理器（基准测试） |
| `agentrt.modules.memory.manager` | 记忆管理器（基准测试） |
| `agentrt.modules.skill.manager` | 技能管理器（基准测试） |

### 运行时依赖

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | ≥ 3.10 | 脚本运行环境 |
| PyYAML | — | YAML 配置解析 |
| jsonschema | — | JSON Schema 校验 |
| pytest | — | 测试框架 |

### 被依赖方

| 消费模块 | 使用接口 |
|----------|----------|
| 全系统所有模块 | Manager 提供的配置定义、校验和分发 |
| CI/CD 流水线 | `schema_diff --json --check` 用于配置一致性检查 |
| 运维团队 | `drift_detector.py`、`config_diff.py` 用于配置变更审计 |
| heapstore/Checkpoint | 通过 Manager 获取 `root_path`、`log_retention_days` 等配置 |

## 4. 配置参数

Manager 自身管理配置（`manager_management.yaml`）：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `hot_reload.enabled` | `bool` | `true` | 启用热更新 |
| `hot_reload.check_interval_sec` | `int` | `30` | 配置文件检查间隔（秒） |
| `hot_reload.reload_signal` | `string` | `SIGHUP` | 信号触发重载 |
| `version_control.enabled` | `bool` | `true` | 启用版本控制 |
| `version_control.backend` | `string` | `git` | 后端类型（git/file/database） |
| `version_control.git.auto_commit` | `bool` | `true` | 自动提交 |
| `version_control.file.max_versions` | `int` | `100` | 最大版本数 |
| `rollback.enabled` | `bool` | `true` | 启用回滚 |
| `rollback.max_steps` | `int` | `10` | 最大回滚步数 |
| `rollback.auto_rollback.on_load_failure` | `bool` | `true` | 加载失败自动回滚 |
| `rollback.auto_rollback.on_validation_failure` | `bool` | `true` | 验证失败自动回滚 |
| `validation.validate_on_startup` | `bool` | `true` | 启动时验证 |
| `validation.validate_on_reload` | `bool` | `true` | 热更新时验证 |
| `audit.enabled` | `bool` | `true` | 启用审计 |
| `audit.retention_days` | `int` | `90` | 审计日志保留天数 |
| `encryption.enabled` | `bool` | `true` | 启用加密 |
| `encryption.algorithm` | `string` | `aes-256-gcm` | 加密算法 |
| `encryption.key_source` | `string` | `env` | 密钥来源（env/file/vault） |
| `import_export.merge_strategy` | `string` | `deep_merge` | 导入合并策略 |
| `sync.enabled` | `bool` | `false` | 启用多实例同步 |
| `sync.backend` | `string` | `redis` | 同步后端 |
| `sync.interval_sec` | `int` | `60` | 同步间隔（秒） |

## 5. 跨团队接口合约

### 合约文件

| 合约 | 文件 | 说明 |
|------|------|------|
| Schema 元数据 | `schema/_metadata.schema.json` | Schema 文件自身的版本与依赖定义 |
| 内核配置 Schema | `schema/kernel-settings.schema.json` | 内核级配置（内存/调度/并发限制） |
| 模型配置 Schema | `schema/model.schema.json` | 模型配置（Provider/参数/上下文窗口） |
| 安全策略 Schema | `schema/security-policy.schema.json` | 安全配置（认证/授权/沙箱隔离） |
| 日志配置 Schema | `schema/logging.schema.json` | 日志配置（级别/格式/输出目标） |
| Agent 注册 Schema | `schema/agent-registry.schema.json` | Agent 配置定义与管理 |
| 技能注册 Schema | `schema/skill-registry.schema.json` | 技能配置与管理 |
| 工具服务 Schema | `schema/tool-service.schema.json` | tool_d 守护进程配置 |
| 配置管理 Schema | `schema/config-management.schema.json` | Manager 自身管理配置 |
| 审计日志 Schema | `schema/config-audit-log.schema.json` | 配置变更审计日志规范 |
| 清洗器规则 Schema | `schema/sanitizer-rules.schema.json` | 输入清洗规则（XSS/SQL 注入） |
| Schema 同步检查 | `schema_diff.py` | Manager Schema ↔ agentrt.yaml 双向一致性合约 |

### 测试接口

| 测试文件 | 覆盖范围 |
|----------|----------|
| `tests/README.md` | 测试套件文档（测试脚本计划中） |
| `benchmark/benchmark_manager.py` | TaskManager/SessionManager/MemoryManager/SkillManager 性能基准 |

## 6. 文件所有权

```
@owner: team-B
```

## 7. 变更记录

| 版本 | 日期 | 变更 | 作者 |
|------|------|------|------|
| v1.0.0 | 2026-06-18 | 初始版本，基于 Manager 代码分析创建 | team-B |