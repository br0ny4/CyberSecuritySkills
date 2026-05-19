"""
DeepSeek V4 专项性能优化器
============================
针对 DeepSeek V4 (Pro/Flash) 的专项优化模块，涵盖:
  1. Function Calling 稳定性增强
  2. 1M Context 窗口利用策略
  3. Token 消耗优化与成本控制
  4. 批量技能加载与渐进式发现
  5. 重试与退避机制

DeepSeek V4 核心特性:
  - 1M token 上下文窗口 (Pro版本)
  - Function Calling (兼容 OpenAI 工具调用格式)
  - 极低成本 (Flash: ¥0.1/1M input tokens)
  - 开源权重 (支持本地部署)

Author: Unified Security Skills Team
License: MIT
Version: 1.0.0-pre
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from functools import lru_cache

logger = logging.getLogger(__name__)


class DeepSeekModel(str, Enum):
    """DeepSeek V4 模型版本"""
    V4_PRO = "deepseek-v4-pro"           # Pro版: 最高精度, 1M context
    V4_FLASH = "deepseek-v4-flash"       # Flash版: 快速推理, 极低成本
    V4_LOCAL = "deepseek-v4-local"       # 本地部署版


class OptimizationStrategy(str, Enum):
    """优化策略"""
    ACCURACY = "accuracy"     # 精度优先: 完整加载技能内容
    SPEED = "speed"           # 速度优先: 精简Prompt，跳过非关键验证
    COST = "cost"             # 成本优先: 最小化Token消耗，渐进式加载
    BALANCED = "balanced"     # 平衡策略: 自适应选择


@dataclass
class TokenBudget:
    """Token 预算管理"""
    total: int = 200_000          # 总预算 (V4 Flash推荐)
    system_prompt: int = 5000     # System Prompt保留
    skills_index: int = 3000      # 技能索引(扫描全部技能frontmatter)
    skill_content: int = 150_000   # 技能内容(当前上下文中的技能)
    tool_definitions: int = 10_000 # 工具定义
    safety_margin: int = 32_000    # 安全余量
    
    @property
    def available_for_skills(self) -> int:
        return self.total - self.system_prompt - self.tool_definitions - self.safety_margin


@dataclass
class DeepSeekOptimizationConfig:
    """DeepSeek V4 优化配置"""
    model: DeepSeekModel = DeepSeekModel.V4_FLASH
    strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    token_budget: TokenBudget = field(default_factory=TokenBudget)
    
    # Function Calling 稳定性
    enable_tool_choice_auto: bool = True
    max_function_calls_per_turn: int = 8
    function_call_timeout_seconds: int = 30
    
    # 重试策略
    max_retries: int = 3
    base_delay_ms: int = 1000
    max_delay_ms: int = 30000
    backoff_multiplier: float = 2.0
    retry_on_errors: List[str] = field(default_factory=lambda: [
        "rate_limit",
        "server_error",
        "timeout",
        "context_length_exceeded",
    ])
    
    # 渐进式加载
    progressive_loading: bool = True
    frontmatter_scan_batch_size: int = 100
    max_skills_in_context: int = 15
    
    # 缓存
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600
    
    # 本地部署优化
    local_batch_size: int = 4
    local_max_concurrent: int = 2


class DeepSeekSkillOptimizer:
    """
    DeepSeek V4 技能调用专项优化器

    核心优化维度:
    1. Token管理: 渐进式加载 → 先扫描754个frontmatter (30 tokens/个 = 22K)，再加载top-12匹配技能
    2. Function Calling: 自动tool_choice、结构化输出、调用去重
    3. 上下文压缩: 技能内容动态剪枝 (去掉命令示例，保留流程和验证逻辑)
    4. 重试机制: 指数退避 + 错误分类重试
    5. 缓存层: LRU缓存技能元数据与转换结果
    """

    def __init__(self, config: Optional[DeepSeekOptimizationConfig] = None):
        self.config = config or DeepSeekOptimizationConfig()
        self._skill_cache: Dict[str, Dict[str, Any]] = {}
        self._stats = {
            "total_calls": 0,
            "total_tokens_saved": 0,
            "total_retries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
        logger.info(f"[DeepSeekV4] Optimizer initialized | model={self.config.model.value} "
                     f"| strategy={self.config.strategy.value}")

    # ============ Token 优化 ============

    def estimate_skill_tokens(self, skill_content: str) -> int:
        """
        估算技能内容的Token消耗
        粗略算法: 英文 ~1.3 tokens/word, 代码 ~1.0 tokens/word
        对于中文: ~1.5-2 tokens/char (deepseek tokenizer)
        """
        if not skill_content:
            return 0
        english_words = len(skill_content.split())
        chinese_chars = sum(1 for c in skill_content if '\u4e00' <= c <= '\u9fff')
        code_blocks = skill_content.count('```') // 2
        return int(english_words * 1.3 + chinese_chars * 1.8 + code_blocks * 50)

    def compress_skill_for_context(
        self, skill_content: str, strategy: Optional[OptimizationStrategy] = None
    ) -> str:
        """
        按策略压缩技能内容以适配上下文窗口

        accuracy: 保留所有内容
        speed: 保留 Workflow + Verification，去掉示例和参考
        cost: 仅保留 Workflow 核心步骤
        balanced: 保留 Workflow + Key Concepts 表格，剪枝代码块中的注释
        """
        strategy = strategy or self.config.strategy
        
        if strategy == OptimizationStrategy.ACCURACY:
            return skill_content

        sections = self._parse_skill_sections(skill_content)

        if strategy == OptimizationStrategy.SPEED:
            keep = ["Workflow", "Verification"]
            compressed = "\n\n".join(sections.get(k, "") for k in keep if k in sections)
            return compressed

        elif strategy == OptimizationStrategy.COST:
            workflow = sections.get("Workflow", skill_content)
            lines = workflow.split("\n")
            core_lines = [l for l in lines if not l.strip().startswith("#")]
            return "\n".join(core_lines[:200])  

        elif strategy == OptimizationStrategy.BALANCED:
            keep = ["Workflow", "Key Concepts", "Verification", "Output Format"]
            parts = []
            for k in keep:
                if k in sections:
                    content = sections[k]
                    lines = content.split("\n")
                    trimmed = [l for l in lines if not l.strip().startswith("//") and not l.strip().startswith("# 示例")]
                    parts.append("\n".join(trimmed))
            return "\n\n".join(parts)

        return skill_content

    def _parse_skill_sections(self, content: str) -> Dict[str, str]:
        """解析技能Markdown的各部分内容"""
        sections = {}
        current_section = "preamble"
        current_content = []
        
        for line in content.split("\n"):
            if line.startswith("## ") and not line.startswith("### "):
                if current_content:
                    sections[current_section] = "\n".join(current_content)
                current_section = line[3:].strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_content:
            sections[current_section] = "\n".join(current_content)
        
        return sections

    def progressive_load_plan(
        self, skill_names: List[str], skill_metadatas: List[Dict[str, Any]]
    ) -> List[List[str]]:
        """
        渐进式加载计划: 将技能分批加载，避免超出上下文窗口
        第一波: top-5 最相关技能 (完整加载)
        第二波: next-7 (压缩加载, speed策略)
        第三波: remaining (仅frontmatter)
        """
        batch1 = skill_names[:5]
        batch2 = skill_names[5:12] if len(skill_names) > 5 else []
        batch3 = skill_names[12:] if len(skill_names) > 12 else []
        return [batch1, batch2, batch3]

    # ============ Function Calling 稳定性 ============

    def build_tool_definitions(
        self, skill_metadatas: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        构建 DeepSeek V4 Function Calling 的 tools 参数
        使用 OpenAI 兼容格式，但针对 DeepSeek 做了优化:
        - 每个tool的description限制在1024字符以内 (V4最佳实践)
        - 参数定义采用严格的JSON Schema
        - 避免循环引用和复杂嵌套
        """
        tools = []
        for meta in skill_metadatas[:self.config.max_skills_in_context]:
            tool = {
                "type": "function",
                "function": {
                    "name": f"execute_{meta['name']}",
                    "description": meta.get("description", "")[:1024],
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "skill_name": {
                                "type": "string",
                                "enum": [meta["name"]],
                                "description": "The skill identifier to execute"
                            },
                            "context": {
                                "type": "object",
                                "description": "Execution context parameters for this skill"
                            }
                        },
                        "required": ["skill_name"],
                    }
                }
            }
            tools.append(tool)
        return tools

    def deduplicate_function_calls(
        self, calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        去重消除模型可能产生的重复函数调用
        DeepSeek V4 在长上下文中偶有重复调用问题
        """
        seen = set()
        unique = []
        for call in calls:
            call_hash = hashlib.md5(
                json.dumps(call, sort_keys=True).encode()
            ).hexdigest()
            if call_hash not in seen:
                seen.add(call_hash)
                unique.append(call)
        return unique

    def validate_tool_call(
        self, tool_call: Dict[str, Any], valid_tools: List[str]
    ) -> bool:
        """验证模型返回的tool_call是否有效"""
        func_name = tool_call.get("function", {}).get("name", "")
        if func_name not in valid_tools:
            logger.warning(f"[DeepSeekV4] Invalid tool call: {func_name}")
            return False
        return True

    # ============ 重试机制 ============

    def retry_with_backoff(
        self,
        func: Callable,
        *args,
        is_retryable: Optional[Callable[[Exception], bool]] = None,
        **kwargs,
    ) -> Any:
        """
        指数退避重试机制

        Args:
            func: 要重试的函数
            is_retryable: 判断异常是否可重试
            *args, **kwargs: 传递给func的参数

        Returns:
            func的返回值

        Raises:
            最后一次重试的异常
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                last_exception = e
                
                if attempt == self.config.max_retries:
                    break
                
                if is_retryable and not is_retryable(e):
                    raise
                
                delay = min(
                    self.config.base_delay_ms * (self.config.backoff_multiplier ** attempt),
                    self.config.max_delay_ms,
                ) / 1000.0
                
                self._stats["total_retries"] += 1
                logger.warning(
                    f"[DeepSeekV4] Retry {attempt + 1}/{self.config.max_retries} "
                    f"after {delay:.1f}s | error: {e}"
                )
                time.sleep(delay)
        
        raise last_exception

    # ============ 缓存层 ============

    def get_cached_skill(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """获取缓存的技能数据"""
        if not self.config.enable_cache:
            return None
        
        cached = self._skill_cache.get(skill_name)
        if cached:
            self._stats["cache_hits"] += 1
            logger.debug(f"[DeepSeekV4] Cache hit: {skill_name}")
        else:
            self._stats["cache_misses"] += 1
        return cached

    def set_cached_skill(self, skill_name: str, data: Dict[str, Any]) -> None:
        """缓存技能数据"""
        if self.config.enable_cache:
            self._skill_cache[skill_name] = {
                "data": data,
                "timestamp": time.time(),
            }

    def clear_cache(self) -> None:
        """清空缓存"""
        self._skill_cache.clear()
        self._stats["cache_hits"] = 0
        self._stats["cache_misses"] = 0

    # ============ 统计与监控 ============

    def get_stats(self) -> Dict[str, Any]:
        """获取优化器运行统计"""
        return {
            **self._stats,
            "cache_size": len(self._skill_cache),
            "strategy": self.config.strategy.value,
            "model": self.config.model.value,
        }

    def reset_stats(self) -> None:
        """重置统计计数器"""
        self._stats = {
            "total_calls": 0,
            "total_tokens_saved": 0,
            "total_retries": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
