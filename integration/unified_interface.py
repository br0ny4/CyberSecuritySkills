"""
Cross-Agent Unified Interface (CAUI) — 跨Agent统一接口核心
=============================================================
为所有支持的AI Agent平台提供统一的技能调用接口。

核心设计原则:
  1. 一次编写，到处运行 (Write Once, Run Anywhere)
  2. 平台差异封装在适配器中，接口层保持透明
  3. 自动平台发现与智能路由
  4. 统一的错误处理与遥测

支持的 Agent 平台:
  - Trae (字节跳动)
  - Flocks (微步开源)
  - Claude Code (Anthropic)
  - Cursor (Anysphere)
  - DeepSeek V4
  - GitHub Copilot
  - OpenAI Codex CLI
  - Gemini CLI

Author: Unified Security Skills Team
License: MIT
Version: 1.0.0-pre
"""

import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

from adapters.base.adapter_base import (
    BaseSkillAdapter,
    SkillExecutionContext,
    SkillExecutionMode,
    SkillExecutionResult,
    SkillMetadata,
    SkillSearchQuery,
    SkillStatus,
)

logger = logging.getLogger(__name__)


class AgentPlatform(str, Enum):
    """支持的AI Agent平台"""
    TRAE = "trae"
    FLOCKS = "flocks"
    CLAUDE_CODE = "claude-code"
    CURSOR = "cursor"
    DEEPSEEK_V4 = "deepseek-v4"
    DEEPSEEK_V4_LOCAL = "deepseek-v4-local"
    COPILOT = "copilot"
    CODEX_CLI = "codex-cli"
    GEMINI_CLI = "gemini-cli"
    GENERIC = "generic"


@dataclass
class PlatformCapabilities:
    """平台能力描述"""
    platform: AgentPlatform
    supports_streaming: bool = False
    supports_batch: bool = False
    supports_async: bool = False
    max_skills_per_call: int = 1
    requires_skill_registration: bool = True
    native_skill_format: str = "markdown"  # markdown | yaml | json


PLATFORM_CAPABILITIES = {
    AgentPlatform.TRAE: PlatformCapabilities(
        platform=AgentPlatform.TRAE,
        supports_streaming=True,
        supports_batch=False,
        max_skills_per_call=1,
        requires_skill_registration=True,
        native_skill_format="markdown",
    ),
    AgentPlatform.FLOCKS: PlatformCapabilities(
        platform=AgentPlatform.FLOCKS,
        supports_streaming=True,
        supports_batch=True,
        supports_async=True,
        max_skills_per_call=10,
        requires_skill_registration=True,
        native_skill_format="yaml",
    ),
    AgentPlatform.CLAUDE_CODE: PlatformCapabilities(
        platform=AgentPlatform.CLAUDE_CODE,
        supports_streaming=True,
        supports_batch=False,
        max_skills_per_call=1,
        requires_skill_registration=False,
        native_skill_format="markdown",
    ),
    AgentPlatform.CURSOR: PlatformCapabilities(
        platform=AgentPlatform.CURSOR,
        supports_streaming=True,
        supports_batch=False,
        max_skills_per_call=1,
        requires_skill_registration=True,
        native_skill_format="markdown",
    ),
    AgentPlatform.DEEPSEEK_V4: PlatformCapabilities(
        platform=AgentPlatform.DEEPSEEK_V4,
        supports_streaming=True,
        supports_batch=True,
        supports_async=True,
        max_skills_per_call=15,
        requires_skill_registration=False,
        native_skill_format="markdown",
    ),
}


class UnifiedSkillInterface:
    """
    跨Agent统一技能接口 (CAUI)

    使用示例:
    ```python
    # 自动检测平台
    interface = UnifiedSkillInterface.auto_detect(skill_repo_path="/path/to/repo")

    # 或指定平台
    interface = UnifiedSkillInterface(
        skill_repo_path="/path/to/repo",
        platform=AgentPlatform.DEEPSEEK_V4,
        deepseek_api_key="sk-xxx"
    )

    # 搜索技能
    skills = interface.search("ransomware analysis")

    # 执行技能
    result = interface.execute(
        skill_name="analyzing-ransomware-encryption-mechanisms",
        params={"target_file": "/samples/ransomware.exe"}
    )
    ```
    """

    def __init__(
        self,
        skill_repo_path: str,
        platform: AgentPlatform = AgentPlatform.GENERIC,
        config: Optional[Dict[str, Any]] = None,
        **platform_kwargs,
    ):
        self.skill_repo_path = skill_repo_path
        self.platform = platform
        self.config = config or {}
        self._adapter: Optional[BaseSkillAdapter] = None
        self._capabilities = PLATFORM_CAPABILITIES.get(platform)
        
        # 初始化适配器
        self._init_adapter(platform_kwargs)

    def _init_adapter(self, platform_kwargs: Dict[str, Any]) -> None:
        """根据平台类型初始化对应适配器"""
        platform_map = {
            AgentPlatform.DEEPSEEK_V4: self._init_deepseek_v4,
            AgentPlatform.DEEPSEEK_V4_LOCAL: self._init_deepseek_v4_local,
            AgentPlatform.TRAE: self._init_trae,
            AgentPlatform.FLOCKS: self._init_flocks,
            AgentPlatform.CLAUDE_CODE: self._init_claude_code,
            AgentPlatform.CURSOR: self._init_cursor,
            AgentPlatform.GENERIC: self._init_generic,
        }
        
        init_func = platform_map.get(self.platform)
        if init_func:
            init_func(platform_kwargs)
        
        if self._adapter:
            self._adapter.initialize()
            logger.info(f"[CAUI] Platform={self.platform.value} | Ready")

    def _init_deepseek_v4(self, kwargs: Dict[str, Any]) -> None:
        from adapters.deepseek_v4.deepseek_adapter import DeepSeekV4Adapter
        self._adapter = DeepSeekV4Adapter(
            skill_repo_path=self.skill_repo_path,
            config=self.config,
            api_key=kwargs.get("deepseek_api_key"),
            base_url=kwargs.get("deepseek_base_url"),
            model=kwargs.get("deepseek_model", "deepseek-v4-flash"),
        )

    def _init_deepseek_v4_local(self, kwargs: Dict[str, Any]) -> None:
        from adapters.deepseek_v4.deepseek_adapter import DeepSeekV4LocalAdapter
        self._adapter = DeepSeekV4LocalAdapter(
            skill_repo_path=self.skill_repo_path,
            config=self.config,
            local_url=kwargs.get("local_url", "http://localhost:8000/v1"),
        )

    def _init_trae(self, kwargs: Dict[str, Any]) -> None:
        from adapters.trae.trae_adapter import TraeAdapter
        self._adapter = TraeAdapter(
            skill_repo_path=self.skill_repo_path,
            config=self.config,
        )

    def _init_flocks(self, kwargs: Dict[str, Any]) -> None:
        from adapters.flocks.flocks_adapter import FlocksAdapter
        self._adapter = FlocksAdapter(
            skill_repo_path=self.skill_repo_path,
            config=self.config,
            flocks_endpoint=kwargs.get("flocks_endpoint"),
        )

    def _init_claude_code(self, kwargs: Dict[str, Any]) -> None:
        from adapters.claude_code.claude_code_adapter import ClaudeCodeAdapter
        self._adapter = ClaudeCodeAdapter(
            skill_repo_path=self.skill_repo_path,
            config=self.config,
        )

    def _init_cursor(self, kwargs: Dict[str, Any]) -> None:
        from adapters.cursor.cursor_adapter import CursorAdapter
        self._adapter = CursorAdapter(
            skill_repo_path=self.skill_repo_path,
            config=self.config,
        )

    def _init_generic(self, kwargs: Dict[str, Any]) -> None:
        from adapters.base.adapter_base import BaseSkillAdapter
        
        class GenericAdapter(BaseSkillAdapter):
            PLATFORM_NAME = "generic"
            def initialize(self) -> bool:
                self._initialized = True
                return True
            def list_skills(self, **kwargs):
                return list(self._skill_index.values())
            def search_skills(self, query: SkillSearchQuery):
                return []
            def get_skill(self, skill_name: str):
                return self._skill_index.get(skill_name)
            def load_skill_content(self, skill_name: str):
                return ""
            def execute_skill(self, context: SkillExecutionContext):
                return SkillExecutionResult(
                    skill_name=context.skill_name,
                    status=SkillStatus.COMPLETED,
                    output="Generic adapter — no execution backend",
                )
        
        self._adapter = GenericAdapter(self.skill_repo_path)

    @classmethod
    def auto_detect(
        cls, skill_repo_path: str, **kwargs
    ) -> "UnifiedSkillInterface":
        """自动检测运行环境并选择最佳适配器"""
        import os
        
        # 1. 检测 DeepSeek V4
        if os.environ.get("DEEPSEEK_API_KEY"):
            logger.info("[CAUI] Auto-detected: DeepSeek V4")
            return cls(skill_repo_path, AgentPlatform.DEEPSEEK_V4, **kwargs)
        
        # 2. 检测 Trae IDE
        if os.environ.get("TRAE_ACTIVE") or os.path.exists("/.trae/"):
            logger.info("[CAUI] Auto-detected: Trae IDE")
            return cls(skill_repo_path, AgentPlatform.TRAE, **kwargs)
        
        # 3. 检测 Cursor
        if os.environ.get("CURSOR_ACTIVE") or os.path.exists("/.cursor/"):
            logger.info("[CAUI] Auto-detected: Cursor IDE")
            return cls(skill_repo_path, AgentPlatform.CURSOR, **kwargs)
        
        # 4. 检测 Claude Code
        if os.environ.get("ANTHROPIC_API_KEY"):
            logger.info("[CAUI] Auto-detected: Claude Code")
            return cls(skill_repo_path, AgentPlatform.CLAUDE_CODE, **kwargs)
        
        # 5. Default: Generic
        logger.info("[CAUI] No specific platform detected — using Generic adapter")
        return cls(skill_repo_path, AgentPlatform.GENERIC, **kwargs)

    # ============ 统一查询接口 ============

    def search(
        self,
        keyword: str = "",
        subdomain: Optional[str] = None,
        mitre_attack: Optional[str] = None,
        difficulty_max: Optional[int] = None,
        limit: int = 20,
    ) -> List[SkillMetadata]:
        """统一技能搜索"""
        query = SkillSearchQuery(
            keyword=keyword,
            subdomain=subdomain,
            mitre_attack=mitre_attack,
            difficulty_max=difficulty_max,
            limit=limit,
        )
        return self._adapter.search_skills(query)

    def list_domains(self) -> List[str]:
        """列出所有安全领域"""
        domains = set()
        for meta in self._adapter.list_skills(limit=999):
            domains.add(meta.subdomain)
        return sorted(domains)

    def get_skill_detail(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """获取技能完整详情"""
        meta = self._adapter.get_skill(skill_name)
        if not meta:
            return None
        content = self._adapter.load_skill_content(skill_name)
        return {
            "metadata": meta.to_dict(),
            "content": content,
        }

    # ============ 统一执行接口 ============

    def execute(
        self,
        skill_name: str,
        params: Optional[Dict[str, Any]] = None,
        mode: SkillExecutionMode = SkillExecutionMode.SYNC,
        timeout_seconds: int = 300,
    ) -> SkillExecutionResult:
        """统一技能执行"""
        context = SkillExecutionContext(
            skill_name=skill_name,
            parameters=params or {},
            mode=mode,
            timeout_seconds=timeout_seconds,
        )
        return self._adapter.execute_skill(context)

    def execute_chain(
        self,
        skill_chain: List[Dict[str, Any]],
        on_step_complete: Optional[Callable] = None,
    ) -> List[SkillExecutionResult]:
        """执行技能链 (顺序执行)"""
        results = []
        for i, step in enumerate(skill_chain):
            skill_name = step["skill_name"]
            params = step.get("params", {})
            
            result = self.execute(skill_name, params)
            results.append(result)
            
            if on_step_complete:
                on_step_complete(i, result)
            
            if result.status == SkillStatus.FAILED:
                logger.warning(
                    f"[CAUI] Chain aborted at step {i}: {skill_name} failed"
                )
                break
        
        return results

    # ============ 元数据接口 ============

    def health(self) -> Dict[str, Any]:
        """健康检查"""
        adapter_health = self._adapter.health_check() if self._adapter else {}
        return {
            "platform": self.platform.value,
            "adapter": adapter_health,
            "capabilities": {
                "streaming": self._capabilities.supports_streaming if self._capabilities else False,
                "batch": self._capabilities.supports_batch if self._capabilities else False,
                "async": self._capabilities.supports_async if self._capabilities else False,
            },
            "skill_repo_path": self.skill_repo_path,
        }

    def get_deepseek_stats(self) -> Optional[Dict[str, Any]]:
        """获取 DeepSeek V4 优化统计（仅当使用 DeepSeek 适配器时）"""
        if hasattr(self._adapter, "optimizer"):
            return self._adapter.optimizer.get_stats()
        return None

    def __repr__(self) -> str:
        return f"<UnifiedSkillInterface platform={self.platform.value}>"


# ============ Agent Registry (Agent注册与发现) ============

class AgentRegistry:
    """
    多Agent注册与发现中心

    管理多个Agent平台的适配器实例，支持:
    - Agent 注册与注销
    - 跨Agent技能路由
    - 负载均衡 (基于平台能力和负载)
    """

    def __init__(self):
        self._agents: Dict[str, UnifiedSkillInterface] = {}
        self._routing_rules: List[Dict[str, Any]] = []

    def register(
        self,
        agent_id: str,
        interface: UnifiedSkillInterface,
        priority: int = 10,
    ) -> None:
        """注册一个Agent"""
        self._agents[agent_id] = interface
        logger.info(f"[Registry] Registered agent: {agent_id} ({interface.platform.value})")

    def unregister(self, agent_id: str) -> None:
        """注销一个Agent"""
        self._agents.pop(agent_id, None)
        logger.info(f"[Registry] Unregistered agent: {agent_id}")

    def list_agents(self) -> List[Dict[str, Any]]:
        """列出所有已注册Agent"""
        return [
            {
                "id": agent_id,
                "platform": interface.platform.value,
                "healthy": interface._adapter._initialized if interface._adapter else False,
            }
            for agent_id, interface in self._agents.items()
        ]

    def route_skill(
        self,
        skill_name: str,
        preferred_platform: Optional[AgentPlatform] = None,
    ) -> Optional[UnifiedSkillInterface]:
        """智能路由: 为技能选择最佳Agent"""
        if preferred_platform:
            for agent_id, interface in self._agents.items():
                if interface.platform == preferred_platform:
                    return interface
        
        # 默认选择第一个健康的Agent
        for interface in self._agents.values():
            if interface._adapter and interface._adapter._initialized:
                return interface
        
        return None

    def execute_on_best(
        self,
        skill_name: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> SkillExecutionResult:
        """自动选择最佳Agent执行技能"""
        interface = self.route_skill(skill_name)
        if not interface:
            return SkillExecutionResult(
                skill_name=skill_name,
                status=SkillStatus.FAILED,
                error="No available agent registered",
            )
        return interface.execute(skill_name, params)
