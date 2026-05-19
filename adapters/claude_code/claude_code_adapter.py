"""
Claude Code 技能适配器
========================
为 Anthropic Claude Code 提供原生技能调用支持。

Claude Code Skills 机制:
  - npx skills add <repo> 一键安装
  - .claude-plugin/ 目录自动发现
  - SKILL.md 文件格式 (YAML frontmatter + Markdown)
  - 渐进式发现 (先扫30 tokens/技能的frontmatter，再加载完整内容)
  - agentskills.io 开放标准

Author: Unified Security Skills Team
License: MIT
"""

import json
import logging
from datetime import datetime
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


class ClaudeCodeAdapter(BaseSkillAdapter):
    """Claude Code 技能适配器"""

    PLATFORM_NAME = "claude-code"
    PLATFORM_VERSION = "1.0.0"
    SUPPORTED_MODES = [
        SkillExecutionMode.SYNC,
        SkillExecutionMode.STREAM,
    ]

    def __init__(self, skill_repo_path: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(skill_repo_path, config)
        self._claude_plugin_dir = Path(skill_repo_path) / ".claude-plugin"
        self._skills_base_dir = Path(skill_repo_path) / "skills"

    def initialize(self) -> bool:
        """初始化: 加载索引 + 生成 Claude Code 插件配置"""
        try:
            self._load_skills_index()
            self._generate_claude_plugin_config()
            self._initialized = True
            logger.info(f"[ClaudeCode] Initialized | {len(self._skill_index)} skills")
            return True
        except Exception as e:
            logger.error(f"[ClaudeCode] Initialization failed: {e}")
            return False

    def _load_skills_index(self) -> None:
        """加载技能索引 (支持统一格式和 agentskills.io 格式)"""
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
                        name = self._to_slug(skill.get("file", "").replace(".md", ""))
                        meta = SkillMetadata(
                            name=name,
                            description=skill.get("name", ""),
                            subdomain=subdomain,
                            difficulty=skill.get("difficulty", "★★★☆☆"),
                        )
                        self._skill_index[name] = meta

    def _generate_claude_plugin_config(self) -> None:
        """生成 .claude-plugin/ 配置"""
        self._claude_plugin_dir.mkdir(parents=True, exist_ok=True)
        
        plugin_config = {
            "name": "CyberSecuritySkills",
            "version": "1.0.0",
            "description": "全门类网络安全AI技能统一集成平台 — 900+ 安全技能",
            "author": "Unified Security Skills Team",
            "license": "MIT",
            "skills_count": len(self._skill_index),
            "domains": list(set(m.subdomain for m in self._skill_index.values())),
            "entry_point": "../index.json",
            "schema": "../schema/unified-skill.schema.json",
            "last_updated": datetime.now().isoformat(),
        }
        
        config_path = self._claude_plugin_dir / "plugin.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(plugin_config, f, ensure_ascii=False, indent=2)
        
        logger.info("[ClaudeCode] .claude-plugin/plugin.json generated")

    def list_skills(
        self, subdomain: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> List[SkillMetadata]:
        skills = list(self._skill_index.values())
        if subdomain:
            skills = [s for s in skills if s.subdomain == subdomain]
        return skills[offset:offset + limit]

    def search_skills(self, query: SkillSearchQuery) -> List[SkillMetadata]:
        """Claude Code 使用基于描述的语义匹配"""
        results = []
        kw = query.keyword.lower() if query.keyword else ""
        for meta in self._skill_index.values():
            score = 0
            if kw:
                if kw in meta.name.lower():
                    score += 10
                if kw in meta.description.lower():
                    score += 8
                if any(kw in t.lower() for t in meta.tags):
                    score += 5
                if meta.name_cn and kw in meta.name_cn:
                    score += 7
            if query.subdomain and meta.subdomain != query.subdomain:
                continue
            if query.mitre_attack:
                if query.mitre_attack not in meta.mitre_attack:
                    continue
            if score > 0 or not kw:
                results.append((score, meta))
        results.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in results[:query.limit]]

    def get_skill(self, skill_name: str) -> Optional[SkillMetadata]:
        return self._skill_index.get(skill_name)

    def load_skill_content(self, skill_name: str) -> Optional[str]:
        """加载技能内容 (Claude Code 格式)"""
        repo = Path(self.skill_repo_path)
        
        # 1. 尝试 skills/<name>/SKILL.md
        skill_dir = self._skills_base_dir / skill_name
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            return skill_md.read_text(encoding="utf-8")
        
        # 2. 全局搜索
        for md_file in repo.rglob("SKILL.md"):
            if skill_name.lower() in md_file.stem.lower() or skill_name.lower() in str(md_file).lower():
                return md_file.read_text(encoding="utf-8")
        
        return None

    def execute_skill(
        self, context: SkillExecutionContext
    ) -> SkillExecutionResult:
        """
        Claude Code 技能执行

        Claude Code 通过加载 SKILL.md 到 Agent 上下文来执行技能，
        由 Claude 模型按 Workflow 逐步执行并验证结果。
        """
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
        
        # Claude Code 原生格式输出
        output = f"## Loaded Skill: {context.skill_name}\n\n"
        if content:
            output += content
        else:
            output += f"*Skill metadata loaded, content will be fetched by Claude Code agent.*\n\n"
            output += f"**Domain**: {metadata.subdomain}\n"
            output += f"**Difficulty**: {metadata.difficulty}\n"
            output += f"**Tags**: {', '.join(metadata.tags) if metadata.tags else 'N/A'}\n"
        
        return SkillExecutionResult(
            skill_name=context.skill_name,
            status=SkillStatus.COMPLETED,
            output=output,
            execution_time_ms=elapsed_ms,
            tokens_used=metadata.estimated_tokens,
            trace_id=context.trace_id,
        )

    @staticmethod
    def _to_slug(text: str) -> str:
        result = []
        for c in text:
            if c.isalnum():
                result.append(c.lower())
            elif c in " -_./":
                result.append("-")
        return "".join(result).strip("-")
