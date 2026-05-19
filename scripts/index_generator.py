#!/usr/bin/env python3
"""
统一索引生成器 — Unified Index Generator
============================================
从双源仓库 (Hi-FullHouse + Anthropic Cybersecurity Skills) 生成统一 index.json。

功能:
  - 双源增量合并 + 智能去重
  - 自动技能文件扫描与校验
  - 输出统一 index.json (按41领域分组)
  - 差异化报告 (A有B无 / B有A无 / 重复项)

用法:
  python index_generator.py --source-a <CyberSecurity-Skills路径> --source-b <Anthropic-Cybersecurity-Skills路径>
  python index_generator.py --validate  # 仅校验
  python index_generator.py --report    # 生成差异化报告

Author: Unified Security Skills Team
License: MIT
"""

import argparse
import difflib
import json
import logging
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UNIFIED_INDEX_PATH = PROJECT_ROOT / "index.json"
SCHEMA_PATH = PROJECT_ROOT / "schema" / "unified-skill.schema.json"


# ============ 41 领域定义 ============

DOMAINS = {
    # 红队
    "reconnaissance": {"cn": "信息搜集", "quadrant": "offensive", "order": 1},
    "vulnerability-scanning": {"cn": "漏洞扫描", "quadrant": "offensive", "order": 2},
    "exploitation": {"cn": "漏洞利用", "quadrant": "offensive", "order": 3},
    "privilege-escalation": {"cn": "权限提升", "quadrant": "offensive", "order": 4},
    "post-exploitation": {"cn": "后渗透", "quadrant": "offensive", "order": 5},
    "lateral-movement": {"cn": "横向移动", "quadrant": "offensive", "order": 6},
    "persistence": {"cn": "持久化", "quadrant": "offensive", "order": 7},
    "covering-tracks": {"cn": "痕迹清除", "quadrant": "offensive", "order": 8},
    "social-engineering": {"cn": "社会工程学", "quadrant": "offensive", "order": 9},
    "wireless-security": {"cn": "无线安全", "quadrant": "offensive", "order": 10},
    "mobile-security": {"cn": "移动安全", "quadrant": "offensive", "order": 11},
    "reverse-engineering": {"cn": "逆向工程", "quadrant": "offensive", "order": 12},
    "penetration-testing": {"cn": "渗透测试", "quadrant": "offensive", "order": 13},
    "red-blue-team": {"cn": "红蓝对抗", "quadrant": "offensive", "order": 14},
    # 蓝队
    "threat-hunting": {"cn": "威胁狩猎", "quadrant": "defensive", "order": 15},
    "threat-intelligence": {"cn": "威胁情报", "quadrant": "defensive", "order": 16},
    "incident-response": {"cn": "应急响应", "quadrant": "defensive", "order": 17},
    "digital-forensics": {"cn": "数字取证", "quadrant": "defensive", "order": 18},
    "soc-operations": {"cn": "SOC运营", "quadrant": "defensive", "order": 19},
    "endpoint-security": {"cn": "端点安全", "quadrant": "defensive", "order": 20},
    "ransomware-defense": {"cn": "勒索软件防御", "quadrant": "defensive", "order": 21},
    "malware-analysis": {"cn": "恶意软件分析", "quadrant": "defensive", "order": 22},
    "network-security": {"cn": "网络安全", "quadrant": "defensive", "order": 23},
    "deception-technology": {"cn": "欺骗防御", "quadrant": "defensive", "order": 24},
    "phishing-defense": {"cn": "钓鱼防御", "quadrant": "defensive", "order": 25},
    "reporting": {"cn": "报告撰写", "quadrant": "defensive", "order": 26},
    "vulnerability-management": {"cn": "漏洞管理", "quadrant": "defensive", "order": 27},
    "security-operations": {"cn": "安全运营", "quadrant": "defensive", "order": 28},
    # 基础设施
    "cloud-security": {"cn": "云安全", "quadrant": "infrastructure", "order": 29},
    "container-security": {"cn": "容器安全", "quadrant": "infrastructure", "order": 30},
    "api-security": {"cn": "API安全", "quadrant": "infrastructure", "order": 31},
    "code-audit": {"cn": "代码审计", "quadrant": "infrastructure", "order": 32},
    "supply-chain-security": {"cn": "供应链安全", "quadrant": "infrastructure", "order": 33},
    "os-security": {"cn": "操作系统安全", "quadrant": "infrastructure", "order": 34},
    "iam": {"cn": "身份访问管理", "quadrant": "infrastructure", "order": 35},
    "cryptography-pki": {"cn": "密码学与PKI", "quadrant": "infrastructure", "order": 36},
    "zero-trust": {"cn": "零信任架构", "quadrant": "infrastructure", "order": 37},
    # 新兴
    "llm-security": {"cn": "大模型安全", "quadrant": "emerging", "order": 38},
    "ics-ot-security": {"cn": "工控安全", "quadrant": "emerging", "order": 39},
    "blockchain-web3-security": {"cn": "区块链安全", "quadrant": "emerging", "order": 40},
    "iot-security": {"cn": "物联网安全", "quadrant": "emerging", "order": 41},
}


def parse_source_a(repo_path: Path) -> List[Dict[str, Any]]:
    """解析 Hi-FullHouse/CyberSecurity-Skills 格式"""
    skills = []
    index_path = repo_path / "index.json"
    if not index_path.exists():
        logger.warning(f"Source A index.json not found at {index_path}")
        return skills

    with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for mod in data.get("modules", []):
        subdomain_en = mod.get("name_en", "").lower().replace(" ", "-")
        for skill in mod.get("skills", []):
            name = _to_kebab(skill.get("file", "").replace(".md", ""))
            unified = {
                "name": name,
                "description": skill.get("name", ""),
                "domain": "cybersecurity",
                "subdomain": _normalize_subdomain(subdomain_en),
                "difficulty": skill.get("difficulty", "★★★☆☆"),
                "name_cn": skill.get("name", ""),
                "category_cn": mod.get("name_cn", ""),
                "difficulty_cn": skill.get("difficulty", ""),
                "source_repos": ["Hi-FullHouse/CyberSecurity-Skills"],
                "version": "1.0.0",
                "license": "MIT",
                "tags": _extract_tags(skill.get("name", "")),
                "tags_cn": [skill.get("name", "")],
                "platforms": ["all"],
            }
            skills.append(unified)
    return skills


def parse_source_b(repo_path: Path) -> List[Dict[str, Any]]:
    """解析 mukul975/Anthropic-Cybersecurity-Skills 格式"""
    skills = []
    index_path = repo_path / "index.json"
    if not index_path.exists():
        logger.warning(f"Source B index.json not found at {index_path}")
        # 扫描 skills/ 目录
        skill_dir = repo_path / "skills"
        if skill_dir.exists():
            for skill_md in skill_dir.glob("*/SKILL.md"):
                fm = _parse_frontmatter(skill_md)
                if fm:
                    skills.append(fm)
        return skills

    with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for entry in data.get("skills", []):
        unified = {
            "name": entry.get("name", ""),
            "description": entry.get("description", ""),
            "domain": entry.get("domain", "cybersecurity"),
            "subdomain": _normalize_subdomain(entry.get("subdomain", "")),
            "mitre_attack": entry.get("mitre_attack", []) if isinstance(entry.get("mitre_attack"), list) else [],
            "nist_csf": entry.get("nist_csf", []),
            "mitre_atlas": entry.get("atlas_techniques", []),
            "mitre_d3fend": entry.get("d3fend_techniques", []),
            "nist_ai_rmf": entry.get("nist_ai_rmf", []),
            "difficulty": _estimate_difficulty(entry),
            "version": entry.get("version", "1.0.0"),
            "author": entry.get("author", "mukul975"),
            "license": entry.get("license", "Apache-2.0"),
            "source_repos": ["mukul975/Anthropic-Cybersecurity-Skills"],
            "tags": entry.get("tags", []),
            "tags_cn": [],
            "platforms": ["all"],
            "name_cn": "",
            "category_cn": DOMAINS.get(_normalize_subdomain(entry.get("subdomain", "")), {}).get("cn", ""),
        }
        skills.append(unified)
    return skills


def merge_skills(skills_a: List[Dict], skills_b: List[Dict]) -> Tuple[List[Dict], Dict]:
    """合并双源技能，智能去重"""
    merged = {}
    stats = {"total_a": len(skills_a), "total_b": len(skills_b),
             "duplicates": 0, "merged": 0, "a_only": 0, "b_only": 0}

    # 第一遍: 按 name 精确匹配
    b_by_name = {s["name"]: s for s in skills_b}
    for sa in skills_a:
        name = sa["name"]
        if name in b_by_name:
            sb = b_by_name[name]
            merged[name] = _merge_two(sa, sb)
            stats["duplicates"] += 1
        else:
            merged[name] = sa
            stats["a_only"] += 1

    # 第二遍: 语义相似度匹配（剩余B源技能）
    b_remaining = [s for s in skills_b if s["name"] not in merged]
    a_names = list(merged.keys())

    for sb in b_remaining:
        matched = False
        for aname in a_names:
            sim = difflib.SequenceMatcher(None, aname, sb["name"]).ratio()
            if sim > 0.75:
                merged[aname] = _merge_two(merged[aname], sb)
                stats["duplicates"] += 1
                matched = True
                break
        if not matched:
            merged[sb["name"]] = sb
            stats["b_only"] += 1

    stats["merged"] = len(merged)

    # 去重后按41领域分组
    by_domain: Dict[str, List[Dict]] = {}
    for name, skill in merged.items():
        sd = skill.get("subdomain", "other")
        by_domain.setdefault(sd, []).append(skill)

    # 构造 index.json 结构
    modules = []
    global_id = 0
    for sd_key in sorted(by_domain, key=lambda k: DOMAINS.get(k, {}).get("order", 99)):
        domain_info = DOMAINS.get(sd_key, {"cn": sd_key, "quadrant": "other", "order": 99})
        skills_list = sorted(by_domain[sd_key], key=lambda s: s["name"])
        global_id += 1
        modules.append({
            "id": global_id,
            "name_cn": domain_info["cn"],
            "name_en": sd_key.replace("-", " ").title(),
            "quadrant": domain_info["quadrant"],
            "skill_count": len(skills_list),
            "skills": [
                {
                    "name": s["name"],
                    "description": s["description"],
                    "difficulty": s["difficulty"],
                    "subdomain": s["subdomain"],
                    "mitre_attack": s.get("mitre_attack", []),
                    "nist_csf": s.get("nist_csf", []),
                    "tags": s.get("tags", []),
                    "name_cn": s.get("name_cn", ""),
                    "tags_cn": s.get("tags_cn", []),
                }
                for s in skills_list
            ],
        })

    index_data = {
        "$schema": "./schema/unified-skill.schema.json",
        "meta": {
            "title": "CyberSecurity AI Skills Unified — 统一索引",
            "description": "全门类网络安全AI技能统一索引 — 41领域",
            "version": "1.0.0",
            "total_skills": stats["merged"],
            "total_modules": len(modules),
            "last_updated": str(date.today()),
        },
        "merge_stats": stats,
        "modules": modules,
    }

    return index_data["modules"], stats


def _merge_two(sa: Dict, sb: Dict) -> Dict:
    """合并两个技能条目: A源中文字段优先, B源框架映射优先"""
    result = {**sa, **sb}
    result["name"] = sa.get("name") or sb.get("name", "")
    result["source_repos"] = list(set(sa.get("source_repos", []) + sb.get("source_repos", [])))
    result["platforms"] = list(set(sa.get("platforms", []) + sb.get("platforms", [])))
    result["tags"] = list(set(sa.get("tags", []) + sb.get("tags", [])))
    result["name_cn"] = sa.get("name_cn") or sb.get("name_cn", "")
    result["tags_cn"] = list(set(sa.get("tags_cn", []) + sb.get("tags_cn", [])))
    return result


def validate_index(index_data: Dict) -> Dict[str, Any]:
    """验证生成的 index.json"""
    errors = []
    warnings = []

    meta = index_data.get("meta", {})
    actual = meta.get("total_skills", 0)
    counted = sum(m.get("skill_count", 0) for m in index_data.get("modules", []))

    if actual != counted:
        errors.append(f"total_skills ({actual}) != sum of module skill_counts ({counted})")

    names_seen = set()
    for mod in index_data.get("modules", []):
        for skill in mod.get("skills", []):
            name = skill.get("name", "")
            if not name:
                errors.append(f"模块 '{mod.get('name_cn')}' 中技能缺少 name")
            elif name in names_seen:
                errors.append(f"重复技能名称: {name}")
            else:
                names_seen.add(name)

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


def _normalize_subdomain(sub: str) -> str:
    """标准化子领域名称"""
    mapping = {
        "iot": "iot-security",
        "ics": "ics-ot-security",
        "ot": "ics-ot-security",
        "llm": "llm-security",
        "web application security": "exploitation",
        "web-application-security": "exploitation",
        "penetration testing": "penetration-testing",
        "red teaming": "red-blue-team",
        "red-teaming": "red-blue-team",
        "devsecops": "security-operations",
        "compliance": "governance-compliance",
        "compliance & governance": "governance-compliance",
        "governance": "governance-compliance",
        "security audit": "security-operations",
    }
    sub_lower = sub.lower().replace(" ", "-")
    return mapping.get(sub_lower, sub_lower)


def _to_kebab(text: str) -> str:
    result = []
    for c in text:
        if c.isalnum():
            result.append(c.lower())
        elif c in " -_":
            result.append("-")
    return "".join(result).strip("-")


def _extract_tags(text: str) -> List[str]:
    """从中文描述提取英文标签"""
    # 简化版: 提取关键词
    keywords = ["scan", "injection", "exploit", "forensics", "linux", "windows",
                "web", "network", "mobile", "cloud", "api", "xss", "sql", "ssrf",
                "privilege", "persistence", "lateral", "phishing", "ransomware"]
    return [k for k in keywords if k.lower() in text.lower()]


def _estimate_difficulty(entry: Dict) -> str:
    """估算难度"""
    tags = entry.get("tags", [])
    name = entry.get("name", "")
    # 粗略估算
    advanced_keywords = ["apt", "rootkit", "bootkit", "red-team", "exploitation", "reverse"]
    for kw in advanced_keywords:
        if kw in name.lower() or kw in str(tags).lower():
            return "★★★★★"
    return "★★★☆☆"


def _parse_frontmatter(md_file: Path) -> Optional[Dict]:
    """解析 SKILL.md 的 YAML frontmatter"""
    try:
        import yaml
        content = md_file.read_text(encoding="utf-8")
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm = yaml.safe_load(parts[1]) or {}
                return fm
    except Exception:
        pass
    return None


def generate_report(modules: List[Dict], stats: Dict) -> str:
    """生成差异化报告"""
    lines = [
        "# 技能合并差异化报告",
        f"## 统计概览",
        f"- A 源 (Hi-FullHouse): {stats['total_a']} 技能",
        f"- B 源 (Anthropic): {stats['total_b']} 技能",
        f"- 重复合并: {stats['duplicates']} 对",
        f"- A 独有: {stats['a_only']}",
        f"- B 独有: {stats['b_only']}",
        f"- 合并总计: {stats['merged']} 技能",
        "",
        "## 领域分布",
    ]
    for mod in sorted(modules, key=lambda m: m["id"]):
        lines.append(f"- {mod['name_cn']} ({mod['name_en']}): {mod['skill_count']} 技能")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="统一技能索引生成器")
    parser.add_argument("--source-a", help="Hi-FullHouse/CyberSecurity-Skills 仓库路径")
    parser.add_argument("--source-b", help="mukul975/Anthropic-Cybersecurity-Skills 仓库路径")
    parser.add_argument("--output", "-o", default=str(UNIFIED_INDEX_PATH), help="输出路径")
    parser.add_argument("--validate", action="store_true", help="仅验证已有 index.json")
    parser.add_argument("--report", action="store_true", help="生成差异化报告")
    args = parser.parse_args()

    if args.validate:
        if UNIFIED_INDEX_PATH.exists():
            with open(UNIFIED_INDEX_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            result = validate_index(data)
            status = "✅ 通过" if result["valid"] else "❌ 失败"
            print(f"验证结果: {status}")
            for e in result["errors"]:
                print(f"  错误: {e}")
            for w in result["warnings"]:
                print(f"  警告: {w}")
            sys.exit(0 if result["valid"] else 1)
        else:
            print("index.json 不存在")
            sys.exit(1)

    if not args.source_a or not args.source_b:
        print("错误: 需要同时指定 --source-a 和 --source-b")
        sys.exit(1)

    repo_a = Path(args.source_a)
    repo_b = Path(args.source_b)

    if not repo_a.exists():
        print(f"错误: Source A 路径不存在: {repo_a}")
        sys.exit(1)
    if not repo_b.exists():
        print(f"错误: Source B 路径不存在: {repo_b}")
        sys.exit(1)

    logger.info("解析 Source A (Hi-FullHouse)...")
    skills_a = parse_source_a(repo_a)

    logger.info("解析 Source B (Anthropic Cybersecurity)...")
    skills_b = parse_source_b(repo_b)

    logger.info(f"A: {len(skills_a)} 技能, B: {len(skills_b)} 技能")

    modules, stats = merge_skills(skills_a, skills_b)

    # 构建 index.json
    index_data = {
        "$schema": "./schema/unified-skill.schema.json",
        "meta": {
            "title": "CyberSecurity AI Skills Unified Index",
            "description": "全门类网络安全AI技能统一索引 — 融合双源仓库",
            "version": "1.0.0",
            "total_skills": stats["merged"],
            "total_modules": len(modules),
            "last_updated": str(date.today()),
            "frameworks": [
                "MITRE ATT&CK v18", "NIST CSF 2.0", "MITRE ATLAS v5.4",
                "MITRE D3FEND v1.3", "NIST AI RMF 1.0", "等保2.0", "ISO 27001:2022"
            ],
        },
        "merge_stats": stats,
        "modules": modules,
    }

    # 验证
    val_result = validate_index(index_data)
    if not val_result["valid"]:
        logger.error("索引验证失败!")
        for e in val_result["errors"]:
            logger.error(f"  {e}")
        sys.exit(1)

    # 写入
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ 统一索引已生成: {output_path}")
    logger.info(f"   总技能: {stats['merged']} | 模块: {len(modules)}")
    logger.info(f"   重复合并: {stats['duplicates']} | A独有: {stats['a_only']} | B独有: {stats['b_only']}")

    if args.report:
        report = generate_report(modules, stats)
        report_path = output_path.parent / "MERGE_REPORT.md"
        report_path.write_text(report, encoding="utf-8")
        logger.info(f"   差异报告: {report_path}")


if __name__ == "__main__":
    main()
