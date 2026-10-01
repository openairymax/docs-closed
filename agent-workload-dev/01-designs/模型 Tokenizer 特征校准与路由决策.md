# 模型 Tokenizer 特征校准与路由决策

## 1. 核心原则：避免一刀切

行业已验证的最佳实践是 **"信号驱动 + 多因子决策"**，而非单纯依赖 Tokenizer 系数做二元判断。

vLLM Semantic Router 的实践表明，路由决策应基于可组合的 **信号-决策-插件** 架构：

| 层次 | 职责 |
|------|------|
| 信号层 | 提取语言、任务类型、上下文长度、权限等多维度信号 |
| 决策层 | 通过 Boolean 决策树匹配最优路由 |
| 插件层 | 执行安全过滤、缓存、RAG 等操作 |

---

## 2. Tokenizer 特征获取：自动校准机制

### 2.1 校准触发时机

在系统里添加一个新模型（API Key + Endpoint）时，系统后台 **自动触发校准任务**，无需人工介入。

---

## 3. 行业已验证的最佳实践

### 3.1 语言检测先行

在生产系统中，在路由前先进行语言检测，避免昂贵的跨语言推理和 Token 膨胀。语言检测层应部署在 **API 网关或负载均衡器** 中，而非应用代码中。

### 3.2 置信度阈值管理

语言检测的置信度阈值需要根据场景配置：

| 阈值 | 策略 | 适用场景 |
|------|------|----------|
| 0.7+ | 严格路由 | 对语言判断要求高的场景 |
| 0.3+ | 软提示 | 容错性高的场景 |
| **0.85** | 生产推荐 | 生产环境建议值 |

### 3.3 代码/自然语言区分

避免将代码、JSON、配置文件误判为自然语言。生产环境的鲁棒实现需要增加字符比例检查：

| 非 ASCII 字符比例 | 判定 |
|-------------------|------|
| > 40% | 很可能是自然语言 |
| < 15% | 很可能是代码 |

### 3.4 短文本和混合语言处理

- **短文本（< 3 个字符）**：直接返回 `unknown`，触发回退逻辑
- **混合语言文本**（如 `"Hello 世界"`）：语言检测器可能判断错误，需在生产环境测试

### 3.5 路由决策的"软硬"分层

**硬规则（不可逾越）：**

- 安全合规：PII 过滤、越狱检测
- 文化/政策类任务：强制中文推理

**软规则（基于信号优化）：**

- Token 效率优化：基于 `lang_ratio` 切换推理语言
- 成本优化：简单任务路由到便宜模型

### 3.6 长期稳定性保障

- **定期重新校准**：模型版本升级后（如 GPT-4 → GPT-4o），Tokenizer 可能变化，需重新校准
- **可观测性**：记录每次路由决策的 `decision_reason`，便于回溯和优化
- **A/B 测试**：新路由策略上线前，先在小流量验证，对比推理质量和 Token 消耗

---

## 4. 完整校准与路由流程

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    1. 模型注册（一次性）                            │
│  管理员添加新模型 → 系统自动触发校准 → 计算 lang_ratio → 写入数据库  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    2. 每次请求（实时）                              │
│  用户输入 → 语言检测 → 任务分类 → 查询模型 Profile → 路由决策      │
│  → 输入转换 → 模型调用 → 输出解析 → 质量保障 → 返回用户            │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    3. 持续优化（周期性）                            │
│  监控路由决策分布 → 分析 Token 消耗 → 调整决策阈值 → 重新校准       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 5. 预期收益

| 维度 | 预期效果 |
|------|----------|
| Token 成本 | 混用环境下综合节省 25%~40% |
| 推理质量 | 文化/政策类任务无损，代码/数学类任务波动 < ±1% |
| 运维成本 | 新增模型零人工介入，自动校准 |
| 可观测性 | 全链路可追踪，决策可解释 |

---

## 6. 参考实现

```python
"""
模型 Tokenizer 特征校准与路由决策模块
包含: 自动校准(API + 本地) + 多因子路由决策 + 模型画像管理
"""

import json
import time
import sqlite3
from typing import Dict, Optional, Tuple, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum

# 可选依赖: pip install transformers openai
try:
    import openai
except ImportError:
    openai = None

try:
    from transformers import AutoTokenizer
except ImportError:
    AutoTokenizer = None


# ======================== 数据模型 ========================

class Language(Enum):
    ZH = "zh"
    EN = "en"
    UNKNOWN = "unknown"


class ModelFamily(Enum):
    GPT = "GPT"
    CLAUDE = "Claude"
    DEEPSEEK = "DeepSeek"
    QWEN = "Qwen"
    LLAMA = "Llama"
    MISTRAL = "Mistral"
    OTHER = "Other"


@dataclass
class ModelProfile:
    """模型画像 - 存储校准后的特征"""
    model_id: str
    provider: str              # openai | anthropic | deepseek | qwen | local
    family: str                # GPT | Claude | DeepSeek | Qwen | Llama | Other
    endpoint: str              # API URL 或 本地路径
    api_key: Optional[str] = None
    native_lang: str = "en"    # en | zh
    lang_ratio: float = 1.0    # 中文token数 / 英文token数 (>1说明中文更费token)
    calibrated_at: str = ""
    is_active: bool = True
    context_window: int = 8192
    extra_metadata: str = "{}"  # JSON扩展字段

    def to_dict(self) -> Dict:
        return asdict(self)


# ======================== 核心校准器 ========================

class ModelCalibrator:
    """
    模型Tokenizer特征校准器
    支持: API模型(通过usage字段) + 本地模型(通过transformers)
    """

    # 标准测试集: 字数严格对齐, 避开专有名词
    ZH_SAMPLE = "深度学习的核心是神经网络"
    EN_SAMPLE = "The core of deep learning is neural networks"

    # 备用测试集 (用于验证)
    ZH_SAMPLE_ALT = "人工智能正在改变世界"
    EN_SAMPLE_ALT = "Artificial intelligence is changing the world"

    def __init__(self, db_path: str = "model_profiles.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化SQLite数据库 (也可替换为PostgreSQL/MySQL)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_profiles (
                model_id TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                family TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                api_key TEXT,
                native_lang TEXT DEFAULT 'en',
                lang_ratio REAL DEFAULT 1.0,
                calibrated_at TEXT,
                is_active INTEGER DEFAULT 1,
                context_window INTEGER DEFAULT 8192,
                extra_metadata TEXT DEFAULT '{}'
            )
        """)
        conn.commit()
        conn.close()

    def save_profile(self, profile: ModelProfile) -> None:
        """保存或更新模型画像"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO model_profiles (
                model_id, provider, family, endpoint, api_key, native_lang,
                lang_ratio, calibrated_at, is_active, context_window, extra_metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile.model_id, profile.provider, profile.family, profile.endpoint,
            profile.api_key, profile.native_lang, profile.lang_ratio,
            profile.calibrated_at, 1 if profile.is_active else 0,
            profile.context_window, profile.extra_metadata
        ))
        conn.commit()
        conn.close()

    def load_profile(self, model_id: str) -> Optional[ModelProfile]:
        """加载模型画像"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM model_profiles WHERE model_id = ?", (model_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return ModelProfile(
                model_id=row['model_id'],
                provider=row['provider'],
                family=row['family'],
                endpoint=row['endpoint'],
                api_key=row['api_key'],
                native_lang=row['native_lang'],
                lang_ratio=row['lang_ratio'],
                calibrated_at=row['calibrated_at'],
                is_active=bool(row['is_active']),
                context_window=row['context_window'],
                extra_metadata=row['extra_metadata']
            )
        return None

    def list_active_models(self) -> List[str]:
        """列出所有活跃模型ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT model_id FROM model_profiles WHERE is_active = 1")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    # ==================== API模型校准 ====================

    def calibrate_api_model(
        self,
        model_id: str,
        provider: str,
        endpoint: str,
        api_key: str,
        family: str = "Other",
        timeout: int = 10
    ) -> ModelProfile:
        """
        通过API响应中的 usage.prompt_tokens 字段校准

        Args:
            model_id: 模型唯一标识, 如 "gpt-4o-2024-11-20"
            provider: 厂商, 如 "openai", "anthropic", "deepseek"
            endpoint: API Endpoint
            api_key: API密钥
            family: 模型家族

        Returns:
            校准后的 ModelProfile
        """
        if openai is None:
            raise ImportError("请安装 openai: pip install openai")

        # 初始化客户端
        client = openai.OpenAI(
            api_key=api_key,
            base_url=endpoint if endpoint != "https://api.openai.com/v1" else None
        )

        # 探测: 中文样本 (设置max_tokens=1, 几乎无输出成本)
        try:
            resp_zh = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": self.ZH_SAMPLE}],
                max_tokens=1,
                timeout=timeout
            )
            prompt_tokens_zh = resp_zh.usage.prompt_tokens
        except Exception as e:
            raise RuntimeError(f"中文探测失败: {e}")

        # 探测: 英文样本
        try:
            resp_en = client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": self.EN_SAMPLE}],
                max_tokens=1,
                timeout=timeout
            )
            prompt_tokens_en = resp_en.usage.prompt_tokens
        except Exception as e:
            raise RuntimeError(f"英文探测失败: {e}")

        # 计算系数
        ratio = prompt_tokens_zh / max(prompt_tokens_en, 1)
        ratio = round(ratio, 3)

        # 确定原生语言
        native_lang = self._determine_native_lang(family, provider, ratio)

        # 构建画像
        profile = ModelProfile(
            model_id=model_id,
            provider=provider,
            family=family,
            endpoint=endpoint,
            api_key=api_key,
            native_lang=native_lang,
            lang_ratio=ratio,
            calibrated_at=datetime.utcnow().isoformat() + "Z",
            is_active=True,
            context_window=self._get_context_window(family, model_id),
            extra_metadata=json.dumps({
                "zh_sample_tokens": prompt_tokens_zh,
                "en_sample_tokens": prompt_tokens_en,
                "calibration_method": "api_usage"
            })
        )

        self.save_profile(profile)
        return profile

    # ==================== 本地模型校准 ====================

    def calibrate_local_model(
        self,
        model_id: str,
        provider: str,
        local_path: str,
        family: str = "Other",
        use_fast: bool = True
    ) -> ModelProfile:
        """
        通过本地 transformers tokenizer 校准

        Args:
            model_id: 模型唯一标识
            provider: 固定为 "local"
            local_path: 本地模型路径或HuggingFace名称
            family: 模型家族

        Returns:
            校准后的 ModelProfile
        """
        if AutoTokenizer is None:
            raise ImportError("请安装 transformers: pip install transformers")

        # 加载tokenizer
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                local_path,
                use_fast=use_fast,
                trust_remote_code=True
            )
        except Exception as e:
            raise RuntimeError(f"加载tokenizer失败: {e}")

        # 计算token数量
        tokens_zh = len(tokenizer.encode(self.ZH_SAMPLE))
        tokens_en = len(tokenizer.encode(self.EN_SAMPLE))

        # 备用测试: 取平均值提高准确性
        tokens_zh_alt = len(tokenizer.encode(self.ZH_SAMPLE_ALT))
        tokens_en_alt = len(tokenizer.encode(self.EN_SAMPLE_ALT))

        avg_zh = (tokens_zh + tokens_zh_alt) / 2
        avg_en = (tokens_en + tokens_en_alt) / 2
        ratio = round(avg_zh / max(avg_en, 1), 3)

        # 确定原生语言
        native_lang = self._determine_native_lang(family, provider, ratio)

        profile = ModelProfile(
            model_id=model_id,
            provider=provider,
            family=family,
            endpoint=local_path,
            api_key=None,
            native_lang=native_lang,
            lang_ratio=ratio,
            calibrated_at=datetime.utcnow().isoformat() + "Z",
            is_active=True,
            context_window=self._get_context_window(family, model_id),
            extra_metadata=json.dumps({
                "zh_sample_tokens": tokens_zh,
                "en_sample_tokens": tokens_en,
                "zh_sample_alt_tokens": tokens_zh_alt,
                "en_sample_alt_tokens": tokens_en_alt,
                "calibration_method": "local_tokenizer"
            })
        )

        self.save_profile(profile)
        return profile

    # ==================== 辅助方法 ====================

    @classmethod
    def _determine_native_lang(cls, family: str, provider: str, ratio: float) -> str:
        """根据模型家族和比例推断原生语言"""
        family_lower = family.lower()
        provider_lower = provider.lower()

        # Qwen系列原生中文
        if "qwen" in family_lower or "qwen" in provider_lower:
            return "zh"
        # DeepSeek-V3原生中文, DeepSeek-R1中英混合但偏中文
        if "deepseek" in family_lower and "v3" in family_lower:
            return "zh"
        if "deepseek" in provider_lower:
            return "zh" if ratio < 1.3 else "en"
        # 其他默认英文
        return "en"

    @classmethod
    def _get_context_window(cls, family: str, model_id: str) -> int:
        """获取上下文窗口大小 (默认值, 可扩展)"""
        family_lower = family.lower()
        model_lower = model_id.lower()

        if "gpt-4" in model_lower and "turbo" in model_lower:
            return 128000
        if "gpt-4" in model_lower:
            return 8192
        if "gpt-3.5" in model_lower:
            return 16384
        if "claude-3" in model_lower:
            return 200000
        if "deepseek" in model_lower:
            return 128000
        if "qwen" in model_lower:
            return 128000 if "72b" in model_lower else 8192
        if "llama" in model_lower:
            return 128000 if "3" in model_lower else 4096
        return 8192

    @classmethod
    def quick_verify(cls, model_id: str, db_path: str = "model_profiles.db") -> Tuple[bool, str]:
        """
        快速验证校准是否过期 (建议每月重新校准)
        """
        calibrator = cls(db_path)
        profile = calibrator.load_profile(model_id)
        if not profile:
            return False, "模型不存在"

        cal_date = datetime.fromisoformat(profile.calibrated_at.replace('Z', '+00:00'))
        days_since = (datetime.utcnow() - cal_date).days

        if days_since > 30:
            return False, f"校准已过期 ({days_since}天前), 建议重新校准"
        return True, f"校准有效 ({days_since}天前)"


# ======================== 高级路由决策引擎 ========================

class UniversalRouter:
    """
    多因子路由决策引擎
    结合: 模型画像(lang_ratio) + 任务类型 + 输入语言 + 上下文长度
    避免一刀切
    """

    @dataclass
    class RouteContext:
        """路由上下文"""
        query: str
        history: List[Dict]
        model_profile: ModelProfile
        detected_lang: Language
        task_type: str  # code | math | culture | policy | qa | general
        history_tokens: int
        user_permission: str = "standard"

    @classmethod
    def decide(
        cls,
        ctx: "UniversalRouter.RouteContext"
    ) -> Dict[str, Any]:
        """
        执行路由决策, 返回推荐推理语言及原因

        Returns:
            {
                "reasoning_lang": "en" | "zh",
                "output_lang": "en" | "zh",
                "reason": "决策原因",
                "chain": ["决策链"]
            }
        """
        chain = []
        profile = ctx.model_profile
        ratio = profile.lang_ratio

        # -------- 规则1: 硬约束 (不可逾越) --------
        if ctx.task_type in ["culture", "policy"]:
            chain.append("hard_rule: culture/policy → force_zh")
            return {
                "reasoning_lang": "zh",
                "output_lang": "zh",
                "reason": "hard_rule_culture_policy",
                "chain": chain
            }

        # -------- 规则2: 模型原生能力优势 --------
        # Qwen/DeepSeek 在代码/数学任务上中文推理更优
        if ctx.task_type in ["code", "math"] and profile.family.lower() in ["qwen", "deepseek"]:
            chain.append("native_advantage: Qwen/DeepSeek + code/math → zh")
            return {
                "reasoning_lang": "zh",
                "output_lang": ctx.detected_lang.value if ctx.detected_lang != Language.UNKNOWN else "zh",
                "reason": "native_advantage_code_math",
                "chain": chain
            }

        # -------- 规则3: 输入语言对齐 --------
        # 用户英文输入 + 模型英文效率高 → 英文推理
        if ctx.detected_lang == Language.EN and ratio > 1.2:
            chain.append(f"input_en + ratio({ratio:.2f})>1.2 → en")
            return {
                "reasoning_lang": "en",
                "output_lang": "en",
                "reason": "input_en_efficient",
                "chain": chain
            }

        # 用户中文输入 + 模型中文效率高 → 中文推理
        if ctx.detected_lang == Language.ZH and ratio < 0.85:
            chain.append(f"input_zh + ratio({ratio:.2f})<0.85 → zh")
            return {
                "reasoning_lang": "zh",
                "output_lang": "zh",
                "reason": "input_zh_efficient",
                "chain": chain
            }

        # -------- 规则4: 上下文长度补偿 --------
        # 长上下文 (>2000 tokens) 时, 切换英文的边际收益更大
        if ctx.history_tokens > 2000 and ratio > 1.2:
            chain.append(f"long_context({ctx.history_tokens}) + ratio({ratio:.2f})>1.2 → en")
            return {
                "reasoning_lang": "en",
                "output_lang": ctx.detected_lang.value if ctx.detected_lang != Language.UNKNOWN else "zh",
                "reason": "long_context_efficient",
                "chain": chain
            }

        # -------- 规则5: 性价比阈值 (中庸区间) --------
        if ratio > 1.35:
            decision = "en"
            reason = f"lang_ratio_high_{ratio:.2f}"
            chain.append(f"ratio {ratio:.2f} > 1.35 → en")
        elif ratio < 0.85:
            decision = "zh"
            reason = f"lang_ratio_low_{ratio:.2f}"
            chain.append(f"ratio {ratio:.2f} < 0.85 → zh")
        else:
            # 0.85 ~ 1.35 区间 → 跟随模型原生语言
            decision = profile.native_lang
            reason = f"native_fallback_{profile.native_lang}"
            chain.append(f"ratio {ratio:.2f} in [0.85,1.35] → native({profile.native_lang})")

        # 输出语言: 默认跟随用户输入, 但英文输入用户期望英文回复
        output_lang = ctx.detected_lang.value if ctx.detected_lang != Language.UNKNOWN else "zh"
        if output_lang not in ["zh", "en"]:
            output_lang = "zh"

        return {
            "reasoning_lang": decision,
            "output_lang": output_lang,
            "reason": reason,
            "chain": chain
        }


# ======================== 完整的模型注册与路由集成 ========================

class ModelRegistryRouter:
    """
    模型注册与路由集成控制器
    流程: 添加模型 → 自动校准 → 存储画像 → 请求时路由决策
    """

    def __init__(self, db_path: str = "model_profiles.db"):
        self.calibrator = ModelCalibrator(db_path)
        self.db_path = db_path

    # ===== 注册新模型 =====

    def register_api_model(
        self,
        model_id: str,
        provider: str,
        endpoint: str,
        api_key: str,
        family: str = "Other"
    ) -> ModelProfile:
        """
        注册API模型: 触发自动校准, 保存画像

        这是管理员添加新模型时的唯一调用入口
        """
        print(f"[注册] 开始校准 API 模型: {model_id}")
        profile = self.calibrator.calibrate_api_model(
            model_id=model_id,
            provider=provider,
            endpoint=endpoint,
            api_key=api_key,
            family=family
        )
        print(f"[注册] 校准完成: lang_ratio={profile.lang_ratio}, native_lang={profile.native_lang}")
        return profile

    def register_local_model(
        self,
        model_id: str,
        local_path: str,
        family: str = "Other"
    ) -> ModelProfile:
        """
        注册本地模型: 触发自动校准, 保存画像
        """
        print(f"[注册] 开始校准本地模型: {model_id}")
        profile = self.calibrator.calibrate_local_model(
            model_id=model_id,
            provider="local",
            local_path=local_path,
            family=family
        )
        print(f"[注册] 校准完成: lang_ratio={profile.lang_ratio}, native_lang={profile.native_lang}")
        return profile

    # ===== 请求路由 =====

    def route(
        self,
        model_id: str,
        query: str,
        history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        对单次请求进行路由决策

        Returns:
            {
                "model_id": "gpt-4o",
                "reasoning_lang": "en",
                "output_lang": "zh",
                "reason": "lang_ratio_high_1.82",
                "chain": [...],
                "profile": ModelProfile
            }
        """
        history = history or []

        # 1. 加载模型画像
        profile = self.calibrator.load_profile(model_id)
        if not profile:
            raise ValueError(f"模型未注册: {model_id}")

        if not profile.is_active:
            raise ValueError(f"模型已停用: {model_id}")

        # 2. 提取信号 (复用方案一中的SignalExtractor)
        try:
            from typing import Tuple
            # 简单实现
            def detect_lang(text):
                chinese_ratio = sum(1 for c in text if '\u4e00' <= c <= '\u9fff') / max(len(text), 1)
                if chinese_ratio > 0.3:
                    return Language.ZH, chinese_ratio
                return Language.EN, 0.7
            lang, _ = detect_lang(query)
        except Exception:
            lang = Language.UNKNOWN

        # 3. 任务类型检测 (简化)
        task_type = "qa"
        if any(k in query for k in ["写代码", "实现", "def ", "function"]):
            task_type = "code"
        if any(k in query for k in ["计算", "方程", "导数", "积分"]):
            task_type = "math"
        if any(k in query for k in ["成语", "典故", "古诗", "诗词"]):
            task_type = "culture"
        if any(k in query for k in ["政策", "法规", "法律"]):
            task_type = "policy"

        # 4. 估算历史token
        history_tokens = 0
        for turn in history:
            content = turn.get('content', '')
            chinese_chars = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
            english_words = len(re.findall(r'[a-zA-Z]+', content))
            history_tokens += int(chinese_chars * 1.8 + english_words * 1.2)

        # 5. 执行路由决策
        ctx = UniversalRouter.RouteContext(
            query=query,
            history=history,
            model_profile=profile,
            detected_lang=lang,
            task_type=task_type,
            history_tokens=history_tokens
        )
        decision = UniversalRouter.decide(ctx)

        return {
            "model_id": model_id,
            "reasoning_lang": decision["reasoning_lang"],
            "output_lang": decision["output_lang"],
            "reason": decision["reason"],
            "chain": decision["chain"],
            "profile": profile
        }

    # ===== 运维工具 =====

    def verify_and_recalibrate(self, model_id: str) -> Tuple[bool, str]:
        """验证并触发重新校准 (建议每月执行)"""
        is_valid, msg = ModelCalibrator.quick_verify(model_id, self.db_path)
        if not is_valid:
            print(f"[运维] {msg}, 触发重新校准...")
            profile = self.calibrator.load_profile(model_id)
            if profile.provider == "local":
                self.register_local_model(model_id, profile.endpoint, profile.family)
            else:
                self.register_api_model(
                    model_id, profile.provider,
                    profile.endpoint, profile.api_key,
                    profile.family
                )
            return True, "重新校准完成"
        return is_valid, msg

    def get_statistics(self) -> Dict[str, Any]:
        """获取所有模型的路由统计"""
        model_ids = self.calibrator.list_active_models()
        stats = {
            "total_models": len(model_ids),
            "models": []
        }
        for mid in model_ids:
            profile = self.calibrator.load_profile(mid)
            if profile:
                stats["models"].append({
                    "model_id": mid,
                    "family": profile.family,
                    "lang_ratio": profile.lang_ratio,
                    "native_lang": profile.native_lang,
                    "recommendation": "en" if profile.lang_ratio > 1.35 else ("zh" if profile.lang_ratio < 0.85 else profile.native_lang)
                })
        return stats


# ======================== 使用示例 ========================

if __name__ == "__main__":
    import re  # 供route方法使用

    # 1. 创建注册路由控制器
    registry = ModelRegistryRouter("model_profiles.db")

    # 2. 注册一个新API模型 (管理员操作)
    # 实际调用时需提供真实API Key
    # profile = registry.register_api_model(
    #     model_id="gpt-4o-2024-11-20",
    #     provider="openai",
    #     endpoint="https://api.openai.com/v1",
    #     api_key="sk-xxxxx",
    #     family="GPT"
    # )

    # 注册本地模型 (示例)
    # profile = registry.register_local_model(
    #     model_id="qwen2.5-7b-local",
    #     local_path="Qwen/Qwen2.5-7B-Instruct",
    #     family="Qwen"
    # )

    # 3. 模拟: 插入一个测试画像用于演示
    test_profile = ModelProfile(
        model_id="gpt-4o-test",
        provider="openai",
        family="GPT",
        endpoint="https://api.openai.com/v1",
        api_key="sk-test",
        native_lang="en",
        lang_ratio=1.82,
        calibrated_at=datetime.utcnow().isoformat() + "Z",
        is_active=True
    )
    registry.calibrator.save_profile(test_profile)

    # 4. 执行路由决策
    result = registry.route(
        model_id="gpt-4o-test",
        query="请用中文解释梯度下降算法",
        history=[]
    )

    print("=" * 60)
    print("路由决策结果:")
    print(f"  模型: {result['model_id']}")
    print(f"  推荐推理语言: {result['reasoning_lang']}")
    print(f"  推荐输出语言: {result['output_lang']}")
    print(f"  决策原因: {result['reason']}")
    print(f"  决策链: {' → '.join(result['chain'])}")
    print(f"  lang_ratio: {result['profile'].lang_ratio}")
    print("=" * 60)

    # 5. 查看统计
    stats = registry.get_statistics()
    print(f"\n当前注册模型数: {stats['total_models']}")
    for m in stats['models']:
        print(f"  - {m['model_id']}: ratio={m['lang_ratio']}, 推荐推理语言={m['recommendation']}")
```
