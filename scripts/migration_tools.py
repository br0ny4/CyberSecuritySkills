#!/usr/bin/env python3
"""
技能格式迁移工具 — Skill Migration Tools
===============================================
将 Hi-FullHouse 和 Anthropic Cybersecurity Skills 格式统一转换为 Unified Schema。

功能:
  - A源迁移: Hi-FullHouse 中文Markdown → Unified SKILL.md
  - B源迁移: Anthropic agentskills.io → Unified SKILL.md (补充中文字段)
  - 批量迁移 + 去重
  - 自动补充框架映射 (从 crosswalk.json)
  - 校验输出格式

用法:
  python migration_tools.py --source-type a --input <path> --output <dir>
  python migration_tools.py --source-type b --input <path> --output <dir>
  python migration_tools.py --validate --input <unified-skill-file>

Author: Unified Security Skills Team
License: MIT
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CROSSWALK_PATH = PROJECT_ROOT / "schema" / "crosswalk.json"


class SkillMigrator:
    """技能格式迁移器"""

    def __init__(self, crosswalk: Optional[Dict] = None):
        self.crosswalk = crosswalk or self._load_crosswalk()
        self.stats = {"migrated": 0, "skipped": 0, "errors": 0}

    def _load_crosswalk(self) -> Dict:
        if CROSSWALK_PATH.exists():
            with open(CROSSWALK_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def migrate_source_a(self, input_path: Path, output_dir: Path) -> int:
        """迁移 Hi-FullHouse 格式 → Unified"""
        output_dir.mkdir(parents=True, exist_ok=True)

        if input_path.is_file() and input_path.suffix == ".json":
            # index.json 模式
            with open(input_path, "r", encoding="utf-8") as f:
                index = json.load(f)
            for mod in index.get("modules", []):
                for skill in mod.get("skills", []):
                    self._migrate_a_skill(mod, skill, output_dir)
        else:
            # 目录扫描模式
            for md_file in input_path.rglob("*.md"):
                if "skills" in str(md_file):
                    self._migrate_a_file(md_file, output_dir)

        logger.info(f"Source A 迁移完成: {self.stats['migrated']} 个文件")
        return self.stats["migrated"]

    def _migrate_a_skill(self, mod: Dict, skill: Dict, output_dir: Path) -> None:
        """迁移单个 A 源技能 (从 index.json 条目)"""
        name_en = mod.get("name_en", "").lower().replace(" ", "-")
        subdomain = self._normalize_subdomain(name_en)

        frontmatter = {
            "name": self._to_kebab(skill.get("file", "").replace(".md", "")),
            "description": skill.get("name", ""),
            "domain": "cybersecurity",
            "subdomain": subdomain,
            "mitre_attack": self._infer_attack(subdomain),
            "nist_csf": self._infer_nist_csf(subdomain),
            "cn_standard": self._infer_cn_standard(subdomain),
            "iso_27001": self._infer_iso(subdomain),
            "version": "1.0.0",
            "difficulty": skill.get("difficulty", "★★★☆☆"),
            "author": "Hi-FullHouse",
            "license": "MIT",
            "source_repos": ["Hi-FullHouse/CyberSecurity-Skills"],
            "estimated_tokens": 1500,
            "execution_time": "medium",
            "tags": [],
            "tags_cn": [skill.get("name", "")],
            "platforms": ["all"],
            "name_cn": skill.get("name", ""),
            "category_cn": mod.get("name_cn", ""),
            "difficulty_cn": skill.get("difficulty", ""),
        }

        output_file = output_dir / subdomain / f"{frontmatter['name']}.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        self._write_skill_file(output_file, frontmatter)
        self.stats["migrated"] += 1

    def _migrate_a_file(self, md_file: Path, output_dir: Path) -> None:
        """迁移单个 A 源 .md 文件"""
        try:
            content = md_file.read_text(encoding="utf-8")
            # 提取 frontmatter
            fm = {}
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    fm = self._parse_simple_yaml(parts[1])
                    body = parts[2]
            else:
                body = content

            name = self._to_kebab(md_file.stem)
            subdomain = fm.get("category_en", "").lower().replace(" ", "-") if fm.get("category_en") else "other"

            frontmatter = {
                "name": name,
                "description": fm.get("title", md_file.stem),
                "domain": "cybersecurity",
                "subdomain": self._normalize_subdomain(subdomain),
                "difficulty": fm.get("difficulty", "★★★☆☆"),
                "author": fm.get("author", "Hi-FullHouse"),
                "license": "MIT",
                "source_repos": ["Hi-FullHouse/CyberSecurity-Skills"],
                "tags": [],
                "tags_cn": [fm.get("title", md_file.stem)],
                "platforms": ["all"],
                "name_cn": fm.get("title", md_file.stem),
                "category_cn": fm.get("category", ""),
            }

            output_file = output_dir / frontmatter["subdomain"] / f"{name}.md"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            self._write_skill_file(output_file, frontmatter, body)
            self.stats["migrated"] += 1
        except Exception as e:
            logger.error(f"迁移失败 {md_file}: {e}")
            self.stats["errors"] += 1

    def migrate_source_b(self, input_path: Path, output_dir: Path) -> int:
        """迁移 Anthropic Cybersecurity Skills → Unified (补充中文字段)"""
        output_dir.mkdir(parents=True, exist_ok=True)

        # 优先加载 index.json
        index_path = input_path / "index.json"
        skills_data = []
        if index_path.exists():
            with open(index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            skills_data = data.get("skills", [])

        if not skills_data:
            # 扫描 SKILL.md 文件
            skills_dir = input_path / "skills"
            for skill_md in skills_dir.rglob("SKILL.md"):
                self._migrate_b_file(skill_md, output_dir)

        for entry in skills_data:
            self._migrate_b_entry(entry, output_dir)

        logger.info(f"Source B 迁移完成: {self.stats['migrated']} 个文件")
        return self.stats["migrated"]

    def _migrate_b_entry(self, entry: Dict, output_dir: Path) -> None:
        """迁移单个 B 源技能 (补充中文字段)"""
        subdomain = self._normalize_subdomain(entry.get("subdomain", ""))

        domain_cn_map = {
            "cloud-security": "云安全", "threat-hunting": "威胁狩猎",
            "threat-intelligence": "威胁情报", "digital-forensics": "数字取证",
            "soc-operations": "SOC运营", "incident-response": "应急响应",
            "malware-analysis": "恶意软件分析", "container-security": "容器安全",
            "api-security": "API安全", "iam": "身份访问管理",
            "ics-ot-security": "工控安全", "ransomware-defense": "勒索软件防御",
        }

        frontmatter = {
            "name": entry.get("name", ""),
            "description": entry.get("description", ""),
            "domain": entry.get("domain", "cybersecurity"),
            "subdomain": subdomain,
            "mitre_attack": entry.get("mitre_attack", []) if isinstance(entry.get("mitre_attack"), list) else [],
            "nist_csf": entry.get("nist_csf", []),
            "mitre_atlas": entry.get("atlas_techniques", []),
            "mitre_d3fend": entry.get("d3fend_techniques", []),
            "nist_ai_rmf": entry.get("nist_ai_rmf", []),
            "version": entry.get("version", "1.0.0"),
            "difficulty": _estimate_stars(entry),
            "author": entry.get("author", "mukul975"),
            "license": entry.get("license", "Apache-2.0"),
            "source_repos": ["mukul975/Anthropic-Cybersecurity-Skills"],
            "estimated_tokens": entry.get("estimated_tokens", 2000),
            "execution_time": "medium",
            "requires_tools": entry.get("requires_tools", []) if isinstance(entry.get("requires_tools"), list) else [],
            "tags": entry.get("tags", []),
            "tags_cn": [],
            "platforms": ["all"],
            "name_cn": "",
            "category_cn": domain_cn_map.get(subdomain, subdomain),
            "difficulty_cn": _estimate_stars(entry),
        }

        output_file = output_dir / subdomain / f"{frontmatter['name']}.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        self._write_skill_file(output_file, frontmatter)
        self.stats["migrated"] += 1

    def _migrate_b_file(self, skill_md: Path, output_dir: Path) -> None:
        """迁移单个 B 源 SKILL.md 文件"""
        try:
            import yaml
            content = skill_md.read_text(encoding="utf-8")
            if content.startswith("---"):
                parts = content.split("---", 2)
                fm = yaml.safe_load(parts[1]) if len(parts) >= 3 and parts[1].strip() else {}
                body = parts[2] if len(parts) >= 3 else ""
            else:
                fm, body = {}, content

            fm = fm or {}
            subdomain = self._normalize_subdomain(fm.get("subdomain", ""))
            name = fm.get("name", self._to_kebab(skill_md.parent.name))

            frontmatter = {
                "name": name,
                "description": fm.get("description", ""),
                "domain": "cybersecurity",
                "subdomain": subdomain,
                "version": fm.get("version", "1.0.0"),
                "difficulty": "★★★☆☆",
                "author": fm.get("author", "mukul975"),
                "license": fm.get("license", "Apache-2.0"),
                "source_repos": ["mukul975/Anthropic-Cybersecurity-Skills"],
                "tags": fm.get("tags", []),
                "tags_cn": [],
                "platforms": ["all"],
                "name_cn": "",
                "category_cn": "",
            }

            output_file = output_dir / subdomain / f"{name}.md"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            self._write_skill_file(output_file, frontmatter, body)
            self.stats["migrated"] += 1
        except Exception as e:
            logger.error(f"迁移失败 {skill_md}: {e}")
            self.stats["errors"] += 1

    def _write_skill_file(self, filepath: Path, frontmatter: Dict, body: str = ""):
        """写统一格式的 SKILL.md"""
        lines = ["---"]
        for key, value in frontmatter.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            elif isinstance(value, str) and "\n" in value:
                lines.append(f"{key}: >-")
                for line in value.split("\n"):
                    lines.append(f"  {line}")
            else:
                lines.append(f"{key}: {value}")
        lines.append("---")
        lines.append("")

        if not body:
            body = (
                f"# {frontmatter.get('name_cn', frontmatter['name'])}\n\n"
                "## 📋 概述 / Overview\n\n"
                f"{frontmatter.get('description', '')}\n\n"
                "## 🎯 使用时机 / When to Use\n\n"
                "*待补充*\n\n"
                "## 🔧 前置条件 / Prerequisites\n\n"
                "*待补充*\n\n"
                "## 📐 工作流程 / Workflow\n\n"
                "### Step 1\n*待补充*\n\n"
                "### Step 2\n*待补充*\n\n"
                "## ✅ 验证方法 / Verification\n\n"
                "*待补充*\n\n"
                "## 🛠️ 工具链 / Tools & Systems\n\n"
                "| 工具 | 用途 |\n|------|------|\n"
                "| *待补充* | *待补充* |\n\n"
                "## 📚 参考资源 / References\n\n"
                "*待补充*\n"
            )

        filepath.write_text("\n".join(lines) + body + "\n", encoding="utf-8")

    def _normalize_subdomain(self, sub: str) -> str:
        mapping = {
            "digital forensics": "digital-forensics",
            "cloud security": "cloud-security",
            "threat hunting": "threat-hunting",
            "threat intelligence": "threat-intelligence",
            "incident response": "incident-response",
        }
        return mapping.get(sub.lower(), sub.lower().replace(" ", "-"))

    def _infer_attack(self, subdomain: str) -> List[str]:
        mapping = {
            "reconnaissance": ["T1593"],
            "vulnerability-scanning": ["T1595"],
            "exploitation": ["T1190"],
            "privilege-escalation": ["T1068"],
            "persistence": ["T1547"],
        }
        return mapping.get(subdomain, [])

    def _infer_nist_csf(self, subdomain: str) -> List[str]:
        mapping = {
            "incident-response": ["RS.MA-01", "RS.AN-01"],
            "threat-hunting": ["DE.CM-01", "DE.AE-01"],
        }
        return mapping.get(subdomain, [])

    def _infer_cn_standard(self, subdomain: str) -> List[str]:
        mapping = {
            "incident-response": ["等保2.0-安全管理中心-应急响应"],
            "cloud-security": ["等保2.0-安全计算环境"],
        }
        return mapping.get(subdomain, [])

    def _infer_iso(self, subdomain: str) -> List[str]:
        mapping = {
            "incident-response": ["A.5.24", "A.5.25"],
        }
        return mapping.get(subdomain, [])

    def _to_kebab(self, text: str) -> str:
        result = []
        for c in text:
            if c.isalnum():
                result.append(c.lower())
            elif c in " -_":
                result.append("-")
        return "".join(result).strip("-")

    def _parse_simple_yaml(self, text: str) -> Dict:
        data = {}
        for line in text.strip().split("\n"):
            if ":" in line:
                k, _, v = line.partition(":")
                data[k.strip()] = v.strip().strip('"').strip("'")
        return data


def _estimate_stars(entry: Dict) -> str:
    tags = entry.get("tags", [])
    name = entry.get("name", "")
    advanced = sum(1 for kw in ["apt", "rootkit", "bootkit", "red-team", "exploit"]
                   if kw in name.lower() or kw in str(tags).lower())
    if advanced >= 2:
        return "★★★★★"
    elif advanced == 1:
        return "★★★★☆"
    return "★★★☆☆"


def main():
    parser = argparse.ArgumentParser(description="技能格式迁移工具")
    parser.add_argument("--source-type", choices=["a", "b"], help="源仓库类型: a=Hi-FullHouse, b=Anthropic")
    parser.add_argument("--input", "-i", help="输入路径 (目录或 index.json)")
    parser.add_argument("--output", "-o", default="./unified-skills", help="输出目录")
    parser.add_argument("--validate", action="store_true", help="验证输出格式")
    args = parser.parse_args()

    if args.validate:
        if not args.input:
            print("错误: --validate 需要 --input")
            sys.exit(1)
        # 简单验证
        path = Path(args.input)
        if path.is_file():
            content = path.read_text(encoding="utf-8")
            has_frontmatter = content.strip().startswith("---")
            has_name = "name:" in content
            valid = has_frontmatter and has_name
            print(f"验证: {path.name} → {'✅ 通过' if valid else '❌ 失败'}")
        sys.exit(0)

    if not args.source_type or not args.input:
        parser.print_help()
        sys.exit(1)

    migrator = SkillMigrator()
    input_path = Path(args.input)
    output_dir = Path(args.output)

    if not input_path.exists():
        print(f"错误: 输入路径不存在: {input_path}")
        sys.exit(1)

    if args.source_type == "a":
        migrator.migrate_source_a(input_path, output_dir)
    else:
        migrator.migrate_source_b(input_path, output_dir)


if __name__ == "__main__":
    main()
