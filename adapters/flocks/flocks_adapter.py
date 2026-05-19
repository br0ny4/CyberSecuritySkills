"""
Flocks (微步开源) 技能适配器
===============================
为微步开源的 Flocks AI Agent 框架提供原生技能调用支持。

Flocks 特性:
  - 微步在线开源的轻量级 AI Agent 框架
  - 支持多 Skill 批量执行与编排
  - YAML 格式的技能定义
  - MCP 协议原生支持
  - 中文环境深度优化
  - safeskill.cn 安全检测集成

Flocks Skill 集成方式:
  - flocks skill install <repo_url>
  - 或本地路径引入: flocks skill install --source local --path /path/to/repo
  - 技能注册通过 agent-manifest.json 或 .flocks.yaml

Author: Unified Security Skills Team
License: MIT
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

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


class FlocksAdapter(BaseSkillAdapter):
    """
    Flocks 技能适配器

    支持:
      - 技能注册到 Flocks
      - YAML 格式技能转换 (SKILL.md → flocks-skill.yaml)
      - 批量技能编排 (Flocks 支持最多10个技能并行)
      - .flocks.yaml 配置文件生成
      - safeskill.cn 安全检测前兼容
    """

    PLATFORM_NAME = "flocks"
    PLATFORM_VERSION = "1.0.0"
    SUPPORTED_MODES = [
        SkillExecutionMode.SYNC,
        SkillExecutionMode.ASYNC,
        SkillExecutionMode.BATCH,
        SkillExecutionMode.STREAM,
    ]

    def __init__(
        self,
        skill_repo_path: str,
        config: Optional[Dict[str, Any]] = None,
        flocks_endpoint: Optional[str] = None,
    ):
        super().__init__(skill_repo_path, config)
        self.flocks_endpoint = flocks_endpoint or os.environ.get(
            "FLOCKS_ENDPOINT", "http://localhost:8080"
        )
        self._flocks_config_path = Path(skill_repo_path) / ".flocks.yaml"
        self._yaml_skills_dir = Path(skill_repo_path) / "flocks-skills"

    def initialize(self) -> bool:
        """初始化: 加载索引 + 生成 Flocks 配置 + 转换 YAML 技能"""
        try:
            self._load_unified_index()
            
            if not self._skill_index:
                self._scan_markdown_skills()
            
            # 生成 Flocks 配置文件
            self._generate_flocks_config()
            
            # 转换为 Flocks YAML 格式
            self._convert_skills_to_yaml()
            
            self._initialized = True
            logger.info(
                f"[Flocks] Initialized | {len(self._skill_index)} skills "
                f"| YAML skills in flocks-skills/ | Config: .flocks.yaml"
            )
            return True
        except Exception as e:
            logger.error(f"[Flocks] Initialization failed: {e}")
            return False

    def _load_unified_index(self) -> None:
        """加载统一索引"""
        repo = Path(self.skill_repo_path)
        index_path = repo / "index.json"
        if not index_path.exists():
            index_path = repo / "agent-manifest.json"
        
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if "modules" in data:
                for mod in data["modules"]:
                    for skill in mod.get("skills", []):
                        name = self._to_kebab(skill.get("file", "").replace(".md", ""))
                        meta = SkillMetadata(
                            name=name,
                            description=skill.get("name", ""),
                            subdomain=mod.get("name_en", "").lower().replace(" ", "-"),
                            difficulty=skill.get("difficulty", "★★★☆☆"),
                            name_cn=skill.get("name", ""),
                            category_cn=mod.get("name_cn", ""),
                            difficulty_cn=skill.get("difficulty", ""),
                            platforms=["flocks", "trae", "claude-code"],
                        )
                        self._skill_index[name] = meta
            elif "skills" in data:
                for entry in data["skills"]:
                    meta = SkillMetadata.from_dict(entry)
                    self._skill_index[meta.name] = meta

    def _scan_markdown_skills(self) -> None:
        """扫描目录结构中的 SKILL.md 文件"""
        repo = Path(self.skill_repo_path)
        for md_file in repo.rglob("SKILL.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        fm_data = yaml.safe_load(parts[1]) or {}
                        meta = SkillMetadata.from_dict(fm_data)
                        self._skill_index[meta.name] = meta
            except Exception:
                continue

    def _generate_flocks_config(self) -> None:
        """生成 .flocks.yaml 配置文件"""
        config = {
            "version": "1.0",
            "name": "CyberSecuritySkills",
            "description": "全门类网络安全AI技能统一集成平台 - Flocks适配",
            "skills": {
                "source": "local",
                "path": "./flocks-skills/",
                "count": len(self._skill_index),
            },
            "domains": list(set(
                m.subdomain for m in self._skill_index.values()
            )),
            "frameworks": {
                "mitre_attack": "v18",
                "nist_csf": "2.0",
                "mitre_atlas": "v5.4",
                "mitre_d3fend": "v1.3",
                "nist_ai_rmf": "1.0",
                "cn_standard": "等保2.0",
            },
            "capabilities": {
                "batch_execution": True,
                "async_execution": True,
                "max_concurrent_skills": 10,
            },
            "compatibility": {
                "trae": True,
                "claude_code": True,
                "cursor": True,
                "deepseek_v4": True,
            },
        }
        
        with open(self._flocks_config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        logger.info("[Flocks] .flocks.yaml generated")

    def _convert_skills_to_yaml(self) -> None:
        """
        将统一格式的技能转换为 Flocks 原生 YAML 格式
        
        Flocks 期望的技能格式:
        ```yaml
        name: skill-name
        description: ...
        category: cybersecurity
        subcategory: digital-forensics
        workflow:
          - step: 1
            action: ...
            command: ...
          - step: 2
            ...
        verification: ...
        ```
        """
        self._yaml_skills_dir.mkdir(parents=True, exist_ok=True)
        
        for skill_name, meta in self._skill_index.items():
            flocks_skill = {
                "name": skill_name,
                "display_name": meta.name_cn or skill_name,
                "description": meta.description,
                "category": "cybersecurity",
                "subcategory": meta.subdomain,
                "difficulty": meta.difficulty,
                "difficulty_level": meta.difficulty.count("★"),
                "tags": meta.tags,
                "tags_cn": meta.tags_cn,
                "frameworks": {
                    "mitre_attack": meta.mitre_attack,
                    "nist_csf": meta.nist_csf,
                    "mitre_atlas": meta.mitre_atlas,
                    "mitre_d3fend": meta.mitre_d3fend,
                    "cn_standard": meta.cn_standard,
                },
                "execution": {
                    "estimated_time": meta.execution_time,
                    "requires_tools": meta.requires_tools,
                    "estimated_tokens": meta.estimated_tokens,
                },
                "version": meta.version,
                "author": meta.author,
                "license": meta.license,
                "source_repos": meta.source_repos,
            }
            
            yaml_path = self._yaml_skills_dir / f"{skill_name}.yaml"
            with open(yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(flocks_skill, f, allow_unicode=True, default_flow_style=False)

        logger.info(f"[Flocks] {len(self._skill_index)} skills converted to YAML")

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
                if meta.tags_cn and any(kw in t for t in meta.tags_cn):
                    score += 8
                if any(kw in t.lower() for t in meta.tags):
                    score += 3
            if query.subdomain and meta.subdomain != query.subdomain:
                continue
            if query.difficulty_max:
                diff_stars = meta.difficulty.count("★")
                if diff_stars > query.difficulty_max:
                    continue
            if score > 0 or not kw:
                results.append((score, meta))
        results.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in results[:query.limit]]

    def get_skill(self, skill_name: str) -> Optional[SkillMetadata]:
        return self._skill_index.get(skill_name)

    def load_skill_content(self, skill_name: str) -> Optional[str]:
        """优先返回 Flocks YAML 格式，其次返回 Markdown"""
        yaml_path = self._yaml_skills_dir / f"{skill_name}.yaml"
        if yaml_path.exists():
            return yaml_path.read_text(encoding="utf-8")
        
        repo = Path(self.skill_repo_path)
        for md_file in repo.rglob("*"):
            if md_file.is_file() and skill_name.lower() in md_file.stem.lower():
                return md_file.read_text(encoding="utf-8")
        return None

    def execute_skill(
        self, context: SkillExecutionContext
    ) -> SkillExecutionResult:
        """
        在 Flocks 框架中执行技能

        Flocks 支持:
        - 同步/异步执行
        - 批量编排 (最多10个技能并行)
        - 流式输出
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
        
        elapsed_ms = int((time.time() - start) * 1000)
        
        # 构建 Flocks-compatible 输出
        output = {
            "skill": context.skill_name,
            "metadata": metadata.to_dict(),
            "execution_mode": context.mode.value,
            "result": "READY",  # Flocks 框架接管实际执行
            "message": (
                f"Skill '{metadata.name_cn or context.skill_name}' loaded. "
                f"Flocks framework will execute the workflow."
            ),
        }
        
        return SkillExecutionResult(
            skill_name=context.skill_name,
            status=SkillStatus.COMPLETED,
            output=json.dumps(output, ensure_ascii=False, indent=2),
            execution_time_ms=elapsed_ms,
            trace_id=context.trace_id,
        )

    def execute_skill_batch(
        self, contexts: List[SkillExecutionContext], parallel: bool = False
    ) -> List[SkillExecutionResult]:
        """
        Flocks 批量执行 (最多10个技能，支持并行)
        """
        if len(contexts) > 10:
            logger.warning(f"[Flocks] Batch limited to 10 skills, got {len(contexts)}")
            contexts = contexts[:10]
        
        return super().execute_skill_batch(contexts, parallel=parallel)

    def health_check(self) -> Dict[str, Any]:
        """健康检查: 包含 Flocks 特有信息"""
        base = super().health_check()
        base["flocks_specific"] = {
            "yaml_skills_count": len(list(self._yaml_skills_dir.glob("*.yaml"))) if self._yaml_skills_dir.exists() else 0,
            "flocks_config_exists": self._flocks_config_path.exists(),
            "endpoint": self.flocks_endpoint,
        }
        return base

    @staticmethod
    def _to_kebab(text: str) -> str:
        """转换为 kebab-case"""
        result = []
        for c in text:
            if c.isalnum():
                result.append(c.lower())
            elif c in " -_":
                result.append("-")
        return "".join(result).strip("-")
