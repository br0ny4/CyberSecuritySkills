"""
Cursor IDE 技能适配器
=======================
为 Anysphere Cursor IDE 提供原生技能调用支持。

Cursor Skills:
  - 基于 .cursor/skills/ 目录自动发现
  - 与 Claude Code / Trae 兼容的 SKILL.md 格式
  - 支持多模型切换 (Claude / GPT / DeepSeek V4)
  - agentskills.io 开放标准

Author: Unified Security Skills Team
License: MIT
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from adapters.base.adapter_base import (
    BaseSkillAdapter,
    SkillExecutionContext,
    SkillExecutionResult,
    SkillExecutionMode,
    SkillMetadata,
    SkillSearchQuery,
    SkillStatus,
)

logger = logging.getLogger(__name__)


class CursorAdapter(BaseSkillAdapter):
    """Cursor IDE 技能适配器"""

    PLATFORM_NAME = "cursor"
    PLATFORM_VERSION = "1.0.0"
    SUPPORTED_MODES = [
        SkillExecutionMode.SYNC,
        SkillExecutionMode.STREAM,
    ]

    def __init__(self, skill_repo_path: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(skill_repo_path, config)
        self._cursor_dir = Path(skill_repo_path) / ".cursor"
        self._cursor_skills_dir = self._cursor_dir / "skills"

    def initialize(self) -> bool:
        """初始化: 加载索引 + 生成 Cursor 配置"""
        try:
            self._load_skills_index()
            self._generate_cursor_config()
            self._initialized = True
            logger.info(f"[Cursor] Initialized | {len(self._skill_index)} skills")
            return True
        except Exception as e:
            logger.error(f"[Cursor] Initialization failed: {e}")
            return False

    def _load_skills_index(self) -> None:
        """加载技能索引"""
        repo = Path(self.skill_repo_path)
        index_path = repo / "index.json"
        
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if "skills" in data:
                for entry in data["skills"]:
                    meta = SkillMetadata.from_dict(entry)
                    self._skill_index[meta.name] = meta
            elif "modules" in data:
                for mod in data["modules"]:
                    subdomain = mod.get("name_en", "").lower().replace(" ", "-")
                    for skill in mod.get("skills", []):
                        name = skill.get("file", "").replace(".md", "").lower().replace(" ", "-")
                        meta = SkillMetadata(
                            name=name,
                            description=skill.get("name", ""),
                            subdomain=subdomain,
                            difficulty=skill.get("difficulty", "★★★☆☆"),
                            name_cn=skill.get("name", ""),
                            category_cn=mod.get("name_cn", ""),
                        )
                        self._skill_index[name] = meta

    def _generate_cursor_config(self) -> None:
        """生成 Cursor IDE 配置文件"""
        self._cursor_dir.mkdir(parents=True, exist_ok=True)
        self._cursor_skills_dir.mkdir(parents=True, exist_ok=True)
        
        # .cursor/skills.json - 技能注册清单
        skills_registry = {
            "version": "1.0.0",
            "name": "CyberSecuritySkills",
            "description": "全门类网络安全AI技能统一集成平台",
            "skill_count": len(self._skill_index),
            "domains": list(set(m.subdomain for m in self._skill_index.values())),
            "skills": [
                {
                    "name": meta.name,
                    "description": meta.description[:200],
                    "subdomain": meta.subdomain,
                    "difficulty": meta.difficulty,
                }
                for meta in list(self._skill_index.values())[:100]
            ],
        }
        
        registry_path = self._cursor_dir / "skills.json"
        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(skills_registry, f, ensure_ascii=False, indent=2)
        
        logger.info("[Cursor] .cursor/skills.json generated")

    def list_skills(
        self, subdomain: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> List[SkillMetadata]:
        skills = list(self._skill_index.values())
        if subdomain:
            skills = [s for s in skills if s.subdomain == subdomain]
        return skills[offset:offset + limit]

    def search_skills(self, query: SkillSearchQuery) -> List[SkillMetadata]:
        results = []
        kw = query.keyword.lower() if query.keyword else ""
        for meta in self._skill_index.values():
            score = 0
            if kw:
                if kw in meta.name.lower():
                    score += 10
                if kw in meta.description.lower():
                    score += 8
                if meta.name_cn and kw in meta.name_cn:
                    score += 10
                if meta.tags_cn and any(kw in t for t in meta.tags_cn):
                    score += 8
                if any(kw in t.lower() for t in meta.tags):
                    score += 5
            if score > 0 or not kw:
                results.append((score, meta))
        results.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in results[:query.limit]]

    def get_skill(self, skill_name: str) -> Optional[SkillMetadata]:
        return self._skill_index.get(skill_name)

    def load_skill_content(self, skill_name: str) -> Optional[str]:
        repo = Path(self.skill_repo_path)
        for md_file in repo.rglob("*.md"):
            if skill_name.lower() in md_file.stem.lower():
                return md_file.read_text(encoding="utf-8")
        return None

    def execute_skill(
        self, context: SkillExecutionContext
    ) -> SkillExecutionResult:
        """在 Cursor IDE 中执行技能"""
        import time
        start = time.time()
        
        metadata = self.get_skill(context.skill_name)
        if not metadata:
            return SkillExecutionResult(
                skill_name=context.skill_name,
                status=SkillStatus.FAILED,
                error=f"Skill not found: {context.skill_name}",
            )
        
        content = self.load_skill_content(context.skill_name)
        
        elapsed_ms = int((time.time() - start) * 1000)
        
        output = f"## {metadata.name_cn or context.skill_name}\n\n"
        output += f"**Domain**: {metadata.category_cn or metadata.subdomain}\n"
        output += f"**Difficulty**: {metadata.difficulty}\n\n"
        if content:
            output += content
        
        return SkillExecutionResult(
            skill_name=context.skill_name,
            status=SkillStatus.COMPLETED,
            output=output,
            execution_time_ms=elapsed_ms,
            tokens_used=metadata.estimated_tokens,
            trace_id=context.trace_id,
        )
