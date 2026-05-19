"""
Cybersecurity AI Skills Unified - Base Adapter
================================================
跨平台AI Agent适配器抽象基类，定义统一的技能调用接口规范。

所有平台适配器 (Flocks/Trae/Claude Code/Cursor/DeepSeek V4) 均继承此基类，
遵循统一的接口契约，确保技能跨平台复用性。

Author: Unified Security Skills Team
License: MIT
Version: 1.0.0-pre
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class SkillExecutionMode(str, Enum):
    """技能执行模式"""
    SYNC = "sync"           # 同步执行，等待结果
    ASYNC = "async"         # 异步执行，返回任务ID
    STREAM = "stream"       # 流式执行，逐步输出
    BATCH = "batch"         # 批量执行多个技能


class SkillStatus(str, Enum):
    """技能执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class SkillMetadata:
    """技能元数据 (对应 unified-skill.schema.json)"""
    name: str
    description: str
    domain: str = "cybersecurity"
    subdomain: str = ""
    mitre_attack: List[str] = field(default_factory=list)
    nist_csf: List[str] = field(default_factory=list)
    mitre_atlas: List[str] = field(default_factory=list)
    mitre_d3fend: List[str] = field(default_factory=list)
    nist_ai_rmf: List[str] = field(default_factory=list)
    cn_standard: List[str] = field(default_factory=list)
    iso_27001: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    difficulty: str = "★★★☆☆"
    author: str = ""
    license: str = "MIT"
    source_repos: List[str] = field(default_factory=list)
    estimated_tokens: int = 0
    execution_time: str = "medium"
    requires_tools: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    optimized_for: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    name_cn: str = ""
    category_cn: str = ""
    difficulty_cn: str = ""
    tags_cn: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SkillMetadata":
        """从字典构建元数据对象"""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            domain=data.get("domain", "cybersecurity"),
            subdomain=data.get("subdomain", ""),
            mitre_attack=data.get("mitre_attack", []),
            nist_csf=data.get("nist_csf", []),
            mitre_atlas=data.get("mitre_atlas", []),
            mitre_d3fend=data.get("mitre_d3fend", []),
            nist_ai_rmf=data.get("nist_ai_rmf", []),
            cn_standard=data.get("cn_standard", []),
            iso_27001=data.get("iso_27001", []),
            version=data.get("version", "1.0.0"),
            difficulty=data.get("difficulty", "★★★☆☆"),
            author=data.get("author", ""),
            license=data.get("license", "MIT"),
            source_repos=data.get("source_repos", []),
            estimated_tokens=data.get("estimated_tokens", 0),
            execution_time=data.get("execution_time", "medium"),
            requires_tools=data.get("requires_tools", []),
            platforms=data.get("platforms", []),
            optimized_for=data.get("optimized_for", []),
            tags=data.get("tags", []),
            name_cn=data.get("name_cn", ""),
            category_cn=data.get("category_cn", ""),
            difficulty_cn=data.get("difficulty_cn", ""),
            tags_cn=data.get("tags_cn", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "subdomain": self.subdomain,
            "mitre_attack": self.mitre_attack,
            "nist_csf": self.nist_csf,
            "mitre_atlas": self.mitre_atlas,
            "mitre_d3fend": self.mitre_d3fend,
            "nist_ai_rmf": self.nist_ai_rmf,
            "cn_standard": self.cn_standard,
            "iso_27001": self.iso_27001,
            "version": self.version,
            "difficulty": self.difficulty,
            "author": self.author,
            "license": self.license,
            "source_repos": self.source_repos,
            "estimated_tokens": self.estimated_tokens,
            "execution_time": self.execution_time,
            "requires_tools": self.requires_tools,
            "platforms": self.platforms,
            "optimized_for": self.optimized_for,
            "tags": self.tags,
            "name_cn": self.name_cn,
            "category_cn": self.category_cn,
            "difficulty_cn": self.difficulty_cn,
            "tags_cn": self.tags_cn,
        }


@dataclass
class SkillExecutionContext:
    """技能执行上下文"""
    skill_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    mode: SkillExecutionMode = SkillExecutionMode.SYNC
    timeout_seconds: int = 300
    max_retries: int = 3
    trace_id: Optional[str] = None
    metadata: Optional[SkillMetadata] = None


@dataclass
class SkillExecutionResult:
    """技能执行结果"""
    skill_name: str
    status: SkillStatus
    output: Any = None
    error: Optional[str] = None
    execution_time_ms: int = 0
    tokens_used: int = 0
    trace_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_name": self.skill_name,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "tokens_used": self.tokens_used,
            "trace_id": self.trace_id,
            "metadata": self.metadata,
        }


@dataclass
class SkillSearchQuery:
    """技能搜索查询"""
    keyword: str = ""
    domain: Optional[str] = None
    subdomain: Optional[str] = None
    mitre_attack: Optional[str] = None
    nist_csf: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    difficulty_max: Optional[int] = None
    platforms: List[str] = field(default_factory=list)
    limit: int = 20
    offset: int = 0


class BaseSkillAdapter(ABC):
    """
    安全技能适配器抽象基类

    所有平台适配器必须实现以下接口方法:
    - list_skills: 列出可用技能
    - search_skills: 搜索技能
    - get_skill: 获取单个技能详情
    - execute_skill: 执行技能
    - validate_skill: 验证技能格式
    """
    
    PLATFORM_NAME: str = "base"
    PLATFORM_VERSION: str = "1.0.0"
    SUPPORTED_MODES: List[SkillExecutionMode] = [
        SkillExecutionMode.SYNC,
    ]

    def __init__(self, skill_repo_path: str, config: Optional[Dict[str, Any]] = None):
        """
        初始化适配器

        Args:
            skill_repo_path: 技能仓库根路径
            config: 平台特定配置
        """
        self.skill_repo_path = skill_repo_path
        self.config = config or {}
        self._skill_index: Dict[str, SkillMetadata] = {}
        self._initialized = False
        logger.info(f"[{self.PLATFORM_NAME}] Adapter initialized at {skill_repo_path}")

    @abstractmethod
    def initialize(self) -> bool:
        """
        初始化适配器: 加载技能索引、验证环境、建立连接

        Returns:
            bool: 初始化是否成功
        """
        ...

    @abstractmethod
    def list_skills(
        self,
        subdomain: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[SkillMetadata]:
        """
        列出可用技能

        Args:
            subdomain: 按子领域过滤
            limit: 返回数量上限
            offset: 分页偏移

        Returns:
            List[SkillMetadata]: 技能元数据列表
        """
        ...

    @abstractmethod
    def search_skills(self, query: SkillSearchQuery) -> List[SkillMetadata]:
        """
        按条件搜索技能

        Args:
            query: 搜索查询对象

        Returns:
            List[SkillMetadata]: 匹配的技能元数据列表
        """
        ...

    @abstractmethod
    def get_skill(self, skill_name: str) -> Optional[SkillMetadata]:
        """
        获取单个技能完整元数据

        Args:
            skill_name: 技能唯一标识符

        Returns:
            Optional[SkillMetadata]: 技能元数据，未找到返回None
        """
        ...

    @abstractmethod
    def load_skill_content(self, skill_name: str) -> Optional[str]:
        """
        加载技能完整内容 (Markdown body)

        Args:
            skill_name: 技能唯一标识符

        Returns:
            Optional[str]: 技能完整Markdown内容
        """
        ...

    @abstractmethod
    def execute_skill(
        self,
        context: SkillExecutionContext,
    ) -> SkillExecutionResult:
        """
        执行技能

        Args:
            context: 执行上下文，包含技能名、参数、执行模式

        Returns:
            SkillExecutionResult: 执行结果
        """
        ...

    def execute_skill_batch(
        self,
        contexts: List[SkillExecutionContext],
        parallel: bool = False,
    ) -> List[SkillExecutionResult]:
        """
        批量执行多个技能

        Args:
            contexts: 执行上下文列表
            parallel: 是否并行执行

        Returns:
            List[SkillExecutionResult]: 执行结果列表
        """
        results = []
        for ctx in contexts:
            result = self.execute_skill(ctx)
            results.append(result)
        return results

    def validate_skill(self, skill_name: str) -> Dict[str, Any]:
        """
        验证技能格式是否符合统一Schema

        Args:
            skill_name: 技能唯一标识符

        Returns:
            Dict: 验证结果 {"valid": bool, "errors": [...], "warnings": [...]}
        """
        metadata = self.get_skill(skill_name)
        if not metadata:
            return {"valid": False, "errors": [f"Skill '{skill_name}' not found"], "warnings": []}
        
        errors, warnings = [], []
        
        if not metadata.name:
            errors.append("name is required")
        if not metadata.description or len(metadata.description) < 20:
            errors.append("description must be at least 20 characters")
        if not metadata.subdomain:
            errors.append("subdomain is required")
        if not metadata.tags:
            warnings.append("No tags specified — reduces AI agent discoverability")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def health_check(self) -> Dict[str, Any]:
        """
        平台连接健康检查

        Returns:
            Dict: {"healthy": bool, "platform": str, "details": {...}}
        """
        return {
            "healthy": self._initialized,
            "platform": self.PLATFORM_NAME,
            "version": self.PLATFORM_VERSION,
            "supported_modes": [m.value for m in self.SUPPORTED_MODES],
            "skill_count": len(self._skill_index),
        }

    def __repr__(self) -> str:
        return f"<{self.PLATFORM_NAME}Adapter(v{self.PLATFORM_VERSION}) skills={len(self._skill_index)}>"
