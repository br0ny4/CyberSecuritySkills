"""
DeepSeek V4 专用技能适配器
============================
集成 DeepSeekSkillOptimizer，提供完整的 DeepSeek V4 API 技能调用能力。

特性:
  - 自动 token_choice 策略 (auto/required/none)
  - 1M 上下文窗口的渐进式技能加载
  - Function Calling 稳定性保障
  - 指数退避重试 + 错误分类
  - 流式输出支持
  - 本地部署 (vLLM/TGI) 兼容

Author: Unified Security Skills Team
License: MIT
Version: 1.0.0-pre
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import field

from adapters.base.adapter_base import (
    BaseSkillAdapter,
    SkillExecutionContext,
    SkillExecutionResult,
    SkillExecutionMode,
    SkillMetadata,
    SkillSearchQuery,
    SkillStatus,
)
from adapters.deepseek_v4.optimizer import (
    DeepSeekSkillOptimizer,
    DeepSeekOptimizationConfig,
    DeepSeekModel,
    OptimizationStrategy,
)

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class DeepSeekV4Adapter(BaseSkillAdapter):
    """
    DeepSeek V4 技能适配器

    使用 OpenAI 兼容API调用 DeepSeek V4，支持:
    - deepseek-v4-pro    (高精度, 1M context)
    - deepseek-v4-flash  (快速, 低成本)
    - 本地部署 (自定义base_url)
    """

    PLATFORM_NAME = "deepseek-v4"
    PLATFORM_VERSION = "1.0.0"
    SUPPORTED_MODES = [
        SkillExecutionMode.SYNC,
        SkillExecutionMode.STREAM,
        SkillExecutionMode.BATCH,
    ]

    def __init__(
        self,
        skill_repo_path: str,
        config: Optional[Dict[str, Any]] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "deepseek-v4-flash",
    ):
        super().__init__(skill_repo_path, config)
        
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY", "")
        self.base_url = base_url or os.environ.get(
            "DEEPSEEK_BASE_URL", "https://api.deepseek.com"
        )
        self.model = model
        
        opt_config = DeepSeekOptimizationConfig(
            model=(
                DeepSeekModel.V4_PRO if "pro" in model
                else DeepSeekModel.V4_FLASH
            ),
            strategy=OptimizationStrategy.BALANCED,
        )
        self.optimizer = DeepSeekSkillOptimizer(opt_config)
        
        self._client: Optional[Any] = None
        self._skill_files: Dict[str, str] = {}  # name → file_path
        
        logger.info(
            f"[DeepSeekV4] Adapter created | model={model} | "
            f"base_url={base_url or 'default'}"
        )

    def initialize(self) -> bool:
        """初始化：建立API连接、加载技能索引"""
        if not HAS_OPENAI:
            logger.error("[DeepSeekV4] openai package not installed. Run: pip install openai")
            return False
        
        if not self.api_key:
            logger.error("[DeepSeekV4] DEEPSEEK_API_KEY not set")
            return False
        
        try:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
            
            # 验证连接
            self._client.models.list()
            
            # 加载技能索引
            self._load_skill_index()
            
            self._initialized = True
            logger.info(f"[DeepSeekV4] Initialized | {len(self._skill_index)} skills loaded")
            return True
            
        except Exception as e:
            logger.error(f"[DeepSeekV4] Initialization failed: {e}")
            return False

    def _load_skill_index(self) -> None:
        """从技能仓库加载技能索引"""
        repo = Path(self.skill_repo_path)
        
        # 优先使用统一索引
        index_file = repo / "index.json"
        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as f:
                index = json.load(f)
            
            if "skills" in index:
                for skill_entry in index["skills"]:
                    name = skill_entry.get("name", "")
                    meta = SkillMetadata.from_dict(skill_entry)
                    self._skill_index[name] = meta
                    skill_path = skill_entry.get("path", "")
                    if skill_path:
                        self._skill_files[name] = str(repo / skill_path / "SKILL.md")
        else:
            # Fallback: 扫描目录结构
            self._scan_directory_skills(repo)

    def _scan_directory_skills(self, repo: Path) -> None:
        """扫描目录结构发现技能文件"""
        import yaml
        try:
            import yaml
        except ImportError:
            # Fallback: 简单正则解析
            for md_file in repo.rglob("SKILL.md"):
                try:
                    with open(md_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    if content.startswith("---"):
                        _, frontmatter_str, _ = content.split("---", 2)
                        meta = self._parse_simple_frontmatter(frontmatter_str, str(md_file))
                        if meta:
                            self._skill_index[meta.name] = meta
                            self._skill_files[meta.name] = str(md_file)
                except Exception:
                    continue

    def _parse_simple_frontmatter(
        self, fm_str: str, file_path: str
    ) -> Optional[SkillMetadata]:
        """简化的YAML frontmatter解析"""
        data = {}
        for line in fm_str.strip().split("\n"):
            if ":" in line:
                key, _, val = line.partition(":")
                data[key.strip()] = val.strip().strip('"').strip("'")
        if "name" in data:
            return SkillMetadata.from_dict(data)
        return None

    def list_skills(
        self,
        subdomain: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[SkillMetadata]:
        """列出可用技能"""
        skills = list(self._skill_index.values())
        if subdomain:
            skills = [s for s in skills if s.subdomain == subdomain]
        return skills[offset:offset + limit]

    def search_skills(self, query: SkillSearchQuery) -> List[SkillMetadata]:
        """按条件搜索技能"""
        results = []
        kw = query.keyword.lower() if query.keyword else ""
        
        for meta in self._skill_index.values():
            score = 0
            
            if kw:
                if kw in meta.name.lower():
                    score += 10
                if kw in meta.description.lower():
                    score += 5
                if any(kw in t.lower() for t in meta.tags):
                    score += 3
                if meta.name_cn and kw in meta.name_cn:
                    score += 10
                if meta.tags_cn and any(kw in t for t in meta.tags_cn):
                    score += 3
            
            if query.subdomain and meta.subdomain != query.subdomain:
                continue
            if query.difficulty_max:
                diff_stars = meta.difficulty.count("★")
                if diff_stars > query.difficulty_max:
                    continue
            if query.platforms:
                if "all" not in meta.platforms:
                    if not any(p in meta.platforms for p in query.platforms):
                        continue
            
            if score > 0 or not kw:
                results.append((score, meta))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return [meta for _, meta in results[query.offset:query.offset + query.limit]]

    def get_skill(self, skill_name: str) -> Optional[SkillMetadata]:
        """获取单个技能元数据"""
        return self._skill_index.get(skill_name)

    def load_skill_content(self, skill_name: str) -> Optional[str]:
        """加载技能完整内容"""
        # 先检查缓存
        cached = self.optimizer.get_cached_skill(skill_name)
        if cached:
            return cached.get("data", {}).get("content")
        
        file_path = self._skill_files.get(skill_name)
        if not file_path:
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.optimizer.set_cached_skill(skill_name, {"content": content})
            return content
        except Exception as e:
            logger.error(f"[DeepSeekV4] Failed to load skill {skill_name}: {e}")
            return None

    def execute_skill(
        self, context: SkillExecutionContext
    ) -> SkillExecutionResult:
        """
        执行技能 — 通过 DeepSeek V4 API

        流程:
        1. 加载技能完整内容
        2. 按策略压缩/优化
        3. 构建系统提示词
        4. 调用 DeepSeek V4 API (with tool definitions)
        5. 解析响应并验证
        """
        if not self._initialized:
            return SkillExecutionResult(
                skill_name=context.skill_name,
                status=SkillStatus.FAILED,
                error="Adapter not initialized",
            )
        
        start_time = time.time()
        
        try:
            skill_content = self.load_skill_content(context.skill_name)
            if not skill_content:
                return SkillExecutionResult(
                    skill_name=context.skill_name,
                    status=SkillStatus.FAILED,
                    error=f"Skill '{context.skill_name}' not found",
                )
            
            metadata = self.get_skill(context.skill_name)
            
            # 按策略压缩
            optimized_content = self.optimizer.compress_skill_for_context(
                skill_content, self.optimizer.config.strategy
            )
            
            # 构建消息
            messages = self._build_system_message(optimized_content, metadata)
            messages.append({
                "role": "user",
                "content": json.dumps(context.parameters, ensure_ascii=False),
            })
            
            # 构建工具定义
            tools = self._build_tools(metadata)
            
            # 调用API
            def api_call():
                return self._client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools if tools else None,
                    tool_choice="auto" if tools else None,
                    temperature=0.1,
                    max_tokens=4096,
                    stream=False,
                )
            
            response = self.optimizer.retry_with_backoff(api_call)
            
            self.optimizer._stats["total_calls"] += 1
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            output = response.choices[0].message.content
            usage = getattr(response, "usage", None)
            tokens_used = usage.total_tokens if usage else 0
            
            return SkillExecutionResult(
                skill_name=context.skill_name,
                status=SkillStatus.COMPLETED,
                output=output,
                execution_time_ms=elapsed_ms,
                tokens_used=tokens_used,
                trace_id=context.trace_id,
            )
            
        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            logger.error(f"[DeepSeekV4] Skill execution failed: {context.skill_name} | {e}")
            return SkillExecutionResult(
                skill_name=context.skill_name,
                status=SkillStatus.FAILED,
                error=str(e),
                execution_time_ms=elapsed_ms,
                trace_id=context.trace_id,
            )

    def _build_system_message(
        self, skill_content: str, metadata: Optional[SkillMetadata]
    ) -> List[Dict[str, Any]]:
        """构建系统提示词（含技能内容）"""
        system_prompt = (
            "You are a cybersecurity AI agent powered by DeepSeek V4. "
            "You have been loaded with a specific cybersecurity skill. "
            "Execute the skill workflow step-by-step and return structured results.\n\n"
            f"## Active Skill: {metadata.name if metadata else 'unknown'}\n"
            "## Skill Instructions:\n\n"
            f"{skill_content}\n\n"
            "## Execution Rules:\n"
            "1. Follow the Workflow section precisely\n"
            "2. Use the tool definitions provided for external operations\n"
            "3. Validate results using the Verification section\n"
            "4. Format output as specified in Output Format\n"
        )
        return [{"role": "system", "content": system_prompt}]

    def _build_tools(
        self, metadata: Optional[SkillMetadata]
    ) -> Optional[List[Dict[str, Any]]]:
        """构建工具定义"""
        if not metadata or not metadata.requires_tools:
            return None
        
        tools = []
        for tool_name in metadata.requires_tools:
            tools.append({
                "type": "function",
                "function": {
                    "name": f"run_{tool_name}",
                    "description": f"Execute the {tool_name} tool for security operations",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": f"The {tool_name} command to execute"
                            }
                        },
                        "required": ["command"],
                    }
                }
            })
        return tools


# ============ 本地部署支持 ============

class DeepSeekV4LocalAdapter(DeepSeekV4Adapter):
    """
    DeepSeek V4 本地部署适配器
    支持 vLLM, TGI, llama.cpp 等推理框架
    """

    PLATFORM_NAME = "deepseek-v4-local"
    
    def __init__(
        self,
        skill_repo_path: str,
        config: Optional[Dict[str, Any]] = None,
        local_url: str = "http://localhost:8000/v1",
        model_name: str = "deepseek-ai/DeepSeek-V4",
    ):
        super().__init__(
            skill_repo_path=skill_repo_path,
            config=config,
            api_key="not-needed",
            base_url=local_url,
            model=model_name,
        )
        opt_config = DeepSeekOptimizationConfig(
            model=DeepSeekModel.V4_LOCAL,
            strategy=OptimizationStrategy.COST,
            token_budget=None,  # 本地无Token成本
            progressive_loading=False,  # 本地可全量加载
        )
        self.optimizer = DeepSeekSkillOptimizer(opt_config)

    def initialize(self) -> bool:
        """初始化本地部署适配器"""
        if not HAS_OPENAI:
            logger.error("[DeepSeekV4-Local] openai package not installed")
            return False
        
        try:
            self._client = OpenAI(
                api_key="not-needed",
                base_url=self.base_url,
            )
            self._client.models.list()
            self._load_skill_index()
            self._initialized = True
            return True
        except Exception as e:
            logger.warning(f"[DeepSeekV4-Local] Connection failed: {e}")
            logger.info("[DeepSeekV4-Local] Ensure vLLM/TGI is running on the specified URL")
            return False
