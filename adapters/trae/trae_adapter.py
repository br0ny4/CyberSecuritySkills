"""
Trae IDE 技能适配器
====================
为字节跳动 Trae IDE 提供原生技能调用支持。

Trae Skill 规范:
  - 基于 agentskills.io 开放标准
  - SKILL.md 文件: YAML frontmatter + Markdown body
  - 技能注册: 通过 .trae/skills/ 目录或配置文件引入
  - 支持 MCP (Model Context Protocol) 集成

Trae 特性:
  - 与 Claude Code 兼容的 skills 格式
  - 内置 MCP Server/Client 架构
  - 支持多模型切换 (DeepSeek V4 / Claude / GPT)
  - 中文原生优化

Author: Unified Security Skills Team
License: MIT
"""

import json
import logging
import os
import shutil
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


class TraeAdapter(BaseSkillAdapter):
    """
    Trae IDE 技能适配器

    支持:
      - 技能注册到 .trae/skills/
      - agent-manifest.json 生成
      - MCP 服务器配置自动生成
      - Trae 特有的 skills 目录结构
    """

    PLATFORM_NAME = "trae"
    PLATFORM_VERSION = "1.0.0"
    SUPPORTED_MODES = [
        SkillExecutionMode.SYNC,
        SkillExecutionMode.STREAM,
    ]

    def __init__(self, skill_repo_path: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(skill_repo_path, config)
        self._trae_skills_dir = Path(skill_repo_path) / ".trae" / "skills"
        self._manifest_path = Path(skill_repo_path) / "agent-manifest.json"

    def initialize(self) -> bool:
        """初始化: 加载技能索引 + 生成 Trae 集成配置"""
        try:
            # 加载索引
            self._load_manifest_index()
            
            # 确保 .trae/skills/ 目录存在
            self._trae_skills_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成 Trae 专用配置
            self._generate_trae_config()
            
            self._initialized = True
            logger.info(
                f"[Trae] Initialized | {len(self._skill_index)} skills "
                f"| .trae/skills/ ready"
            )
            return True
        except Exception as e:
            logger.error(f"[Trae] Initialization failed: {e}")
            return False

    def _load_manifest_index(self) -> None:
        """从 agent-manifest.json 或 index.json 加载索引"""
        repo = Path(self.skill_repo_path)
        
        for index_file in ["index.json", "agent-manifest.json"]:
            index_path = repo / index_file
            if index_path.exists():
                with open(index_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                if "modules" in data:
                    for mod in data["modules"]:
                        for skill in mod.get("skills", []):
                            name = skill.get("file", "").replace(".md", "").replace(" ", "-").lower()
                            meta = SkillMetadata(
                                name=name,
                                description=skill.get("name", ""),
                                subdomain=mod.get("name_en", "").lower().replace(" ", "-"),
                                difficulty=skill.get("difficulty", "★★★☆☆"),
                                name_cn=skill.get("name", ""),
                                category_cn=mod.get("name_cn", ""),
                                difficulty_cn=skill.get("difficulty", ""),
                            )
                            self._skill_index[name] = meta
                
                elif "skills" in data:
                    for entry in data["skills"]:
                        meta = SkillMetadata.from_dict(entry)
                        self._skill_index[meta.name] = meta
                break

    def _generate_trae_config(self) -> None:
        """生成 Trae IDE 专用配置文件"""
        # 1. agent-manifest.json
        manifest = {
            "$schema": "./schema/agent-manifest.schema.json",
            "agent_manifest_version": "1.1.0",
            "project": {
                "name": "cybersecurity-ai-skills-unified",
                "description": "全门类网络安全AI技能统一集成平台",
                "total_skills": len(self._skill_index),
                "language": "zh-CN",
            },
            "agent_integration": {
                "entry_point": "index.json",
                "schema": "schema/unified-skill.schema.json",
                "trae_skills_dir": ".trae/skills/",
            },
            "capabilities": {
                "list_skills": {
                    "description": "列出所有网络安全技能",
                },
                "search_skills": {
                    "description": "按关键词/领域/ATT&CK技术搜索技能",
                },
                "execute_skill": {
                    "description": "执行指定技能的工作流",
                },
            },
            "platforms": ["trae", "claude-code", "cursor", "flocks", "deepseek-v4"],
        }
        
        with open(self._manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        
        # 2. .trae/skills/README.md
        readme = self._trae_skills_dir / "README.md"
        readme.write_text(
            "# CyberSecurity AI Skills Unified — Trae Integration\n\n"
            "本目录包含适配 Trae IDE 的网络安全AI技能文件。\n\n"
            "## 使用方式\n\n"
            f"共 {len(self._skill_index)} 个网络安全技能可用。\n\n"
            "在 Trae 对话中，Agent 会自动发现并加载相关技能。\n\n"
            "## 技能格式\n\n"
            "所有技能文件遵循 `agentskills.io` 开放标准，支持 YAML frontmatter + Markdown。\n",
            encoding="utf-8",
        )
        
        logger.info("[Trae] Config files generated")

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
                    score += 5
                if meta.name_cn and kw in meta.name_cn:
                    score += 10
                if any(kw in t.lower() for t in meta.tags):
                    score += 3
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
        """
        在 Trae 中执行技能

        Trae 的技能执行通过以下方式:
        1. Agent 加载 SKILL.md 内容到上下文
        2. Agent 按 Workflow 逐步执行
        3. 结果返回给用户

        本适配器提供标准化的上下文注入和执行跟踪。
        """
        import time
        
        start = time.time()
        
        metadata = self.get_skill(context.skill_name)
        if not metadata:
            return SkillExecutionResult(
                skill_name=context.skill_name,
                status=SkillStatus.FAILED,
                error=f"Skill '{context.skill_name}' not found",
            )
        
        content = self.load_skill_content(context.skill_name)
        if not content:
            return SkillExecutionResult(
                skill_name=context.skill_name,
                status=SkillStatus.FAILED,
                error=f"Skill content not found for '{context.skill_name}'",
            )
        
        elapsed_ms = int((time.time() - start) * 1000)
        
        # 构建 Trae-compatible 输出 (Markdown格式，便于渲染)
        sections = content.split("## ")
        workflow_section = ""
        for sec in sections:
            if sec.startswith("工作流程") or sec.startswith("Workflow"):
                workflow_section = sec
                break
        
        output = f"**技能**: {metadata.name_cn or metadata.name}\n"
        output += f"**领域**: {metadata.category_cn or metadata.subdomain}\n"
        output += f"**难度**: {metadata.difficulty}\n\n"
        output += f"---\n\n"
        output += f"## 工作流程 / Workflow\n{workflow_section}"
        
        return SkillExecutionResult(
            skill_name=context.skill_name,
            status=SkillStatus.COMPLETED,
            output=output,
            execution_time_ms=elapsed_ms,
            trace_id=context.trace_id,
        )
