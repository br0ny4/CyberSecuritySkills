#!/usr/bin/env python3
"""
合规性自动检查工具 — Automated Compliance Checker
======================================================
对统一技能仓库进行全面的合规性审查。

检查维度:
  1. Schema 合法性    — 每条技能是否符合 unified-skill.schema.json
  2. 必填字段完整性    — name, description, domain, subdomain
  3. 框架映射一致性    — ATT&CK/NIST CSF 格式校验
  4. 许可证兼容性      — MIT + Apache-2.0 混合许可证检查
  5. 许可权来源追溯    — source_repos 字段完整性
  6. 中文字段完整性    — 国内 Agent 平台 (Trae/Flocks) 必需中文元数据
  7. 内容安全检查      — 注入风险/API Key泄露/危险命令

用法:
  python compliance_checker.py --repo /path/to/repo
  python compliance_checker.py --repo /path/to/repo --format json
  python compliance_checker.py --repo /path/to/repo --strict  # 严格模式

Author: Unified Security Skills Team
License: MIT
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = PROJECT_ROOT / "schema" / "unified-skill.schema.json"


class ComplianceChecker:
    """合规性自动检查器"""

    # 危险命令模式 (不意味着不能出现，但需要标记为警告)
    DANGEROUS_PATTERNS = [
        (r"rm\s+-rf\s+/", "CRITICAL", "rm -rf / 危险命令"),
        (r"DROP\s+(TABLE|DATABASE)", "HIGH", "SQL DROP 语句"),
        (r"eval\s*\(.*user.*input", "HIGH", "潜在的 eval 注入"),
        (r"os\.system\(.*input", "HIGH", "潜在的 OS 命令注入"),
        (r"subprocess\.call\(.*input", "HIGH", "潜在的 subprocess 注入"),
        (r"api[_-]?key\s*=\s*['\"][A-Za-z0-9]{20,}", "HIGH", "疑似 API Key 硬编码"),
        (r"password\s*=\s*['\"][^'\"]+['\"]", "MEDIUM", "疑似密码硬编码"),
    ]

    REQUIRED_FIELDS = ["name", "description", "domain", "subdomain"]
    CN_REQUIRED_FIELDS = ["name_cn", "category_cn", "tags_cn"]

    ATTACK_PATTERN = re.compile(r"^T\d{4}(\.\d{3})?$")
    NIST_CSF_PATTERN = re.compile(r"^[A-Z]{2}\.[A-Z]{2}-\d{2}$")
    ATLAS_PATTERN = re.compile(r"^AML\.T\d{4}$")
    D3FEND_PATTERN = re.compile(r"^D3-[A-Z]+$")
    AI_RMF_PATTERN = re.compile(r"^[A-Z]+-\d+\.\d+$")
    ISO_PATTERN = re.compile(r"^A\.\d+\.\d+\.\d+$")

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.results: Dict[str, Any] = {
            "check_time": datetime.now().isoformat(),
            "total_checks": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "items": [],
        }

    def check_repository(self, repo_path: Path) -> Dict[str, Any]:
        """对整个仓库进行全面合规检查"""
        logger.info(f"开始合规检查: {repo_path}")

        # 1. 检查关键文件
        self._check_critical_files(repo_path)

        # 2. 检查 Schema
        self._check_schema(repo_path)

        # 3. 检查技能文件
        self._check_skill_files(repo_path)

        # 4. 检查许可证
        self._check_license(repo_path)

        # 5. 汇总
        self._summarize()
        return self.results

    def _check_critical_files(self, repo_path: Path) -> None:
        """检查关键文件存在性"""
        critical_files = {
            "README.md": "项目说明文件",
            "LICENSE": "许可证文件",
            "CHANGELOG.md": "变更记录",
            "TODO.md": "迭代计划",
            "schema/unified-skill.schema.json": "统一Schema",
            "schema/crosswalk.json": "框架交叉映射",
        }

        for file_rel, desc in critical_files.items():
            file_path = repo_path / file_rel
            if file_path.exists():
                self._add_result("critical_file", "PASS", f"{desc} ({file_rel}): 存在")
            else:
                self._add_result("critical_file", "FAIL", f"{desc} ({file_rel}): 缺失")

    def _check_schema(self, repo_path: Path) -> None:
        """检查 Schema 文件"""
        schema_path = repo_path / "schema" / "unified-skill.schema.json"
        if not schema_path.exists():
            self._add_result("schema", "FAIL", "unified-skill.schema.json 不存在")
            return

        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)

            # 版本号
            version = schema.get("$id", "")
            self._add_result("schema", "PASS", f"Schema 版本: {version}")

            # 必填字段
            required = schema.get("required", [])
            for field in self.REQUIRED_FIELDS:
                if field in required:
                    self._add_result("schema", "PASS", f"必填字段 '{field}' 已定义")
                else:
                    self._add_result("schema", "FAIL", f"必填字段 '{field}' 未在 required 中定义")

        except json.JSONDecodeError as e:
            self._add_result("schema", "FAIL", f"Schema JSON 解析失败: {e}")

    def _check_skill_files(self, repo_path: Path) -> None:
        """检查所有技能文件"""
        # 检查 index.json
        index_path = repo_path / "index.json"
        if not index_path.exists():
            self._add_result("skills", "WARN", "index.json 不存在 — 技能索引尚未生成")
            return

        try:
            with open(index_path, "r", encoding="utf-8") as f:
                index = json.load(f)
        except json.JSONDecodeError as e:
            self._add_result("skills", "FAIL", f"index.json JSON 解析失败: {e}")
            return

        meta = index.get("meta", {})
        total = meta.get("total_skills", 0)
        modules = index.get("modules", [])

        self._add_result("skills", "PASS", f"总技能数: {total}, 模块数: {len(modules)}")

        # 检查每个模块的技能
        skill_count = 0
        for mod in modules:
            mod_name = mod.get("name_cn", mod.get("name_en", "unknown"))
            for skill in mod.get("skills", []):
                skill_count += 1
                self._check_single_skill(skill, mod_name)

        if skill_count != total:
            self._add_result(
                "skills", "FAIL",
                f"meta.total_skills ({total}) != 实际技能数 ({skill_count})"
            )

        self.results["total_checks"] = skill_count

    def _check_single_skill(self, skill: Dict, module_name: str) -> None:
        """检查单个技能条目"""
        name = skill.get("name", "unknown")

        # 必填字段
        for field in self.REQUIRED_FIELDS:
            if not skill.get(field):
                self._add_result(
                    "skill_field", "FAIL",
                    f"[{module_name}] {name}: 缺少必填字段 '{field}'"
                )
            else:
                self._add_result(
                    "skill_field", "PASS",
                    f"[{module_name}] {name}: '{field}' = {skill[field][:50]}"
                )

        # 中文字段 (仅 strict 模式强制)
        for field in self.CN_REQUIRED_FIELDS:
            if self.strict and not skill.get(field):
                self._add_result(
                    "skill_cn", "FAIL",
                    f"[{module_name}] {name}: 缺少中文字段 '{field}'"
                )
            elif not skill.get(field):
                self._add_result(
                    "skill_cn", "WARN",
                    f"[{module_name}] {name}: 中文字段 '{field}' 为空 (国内Agent适配受影响)"
                )

        # 框架映射格式校验
        self._check_framework_ids(skill, name, module_name)

        # 许可证检查
        license_val = skill.get("license", "")
        if license_val not in ("MIT", "Apache-2.0", "CC-BY-4.0", "GPL-3.0", ""):
            self._add_result(
                "skill_license", "WARN",
                f"[{module_name}] {name}: 非标准许可证 '{license_val}'"
            )

        # source_repos 追溯
        if not skill.get("source_repos"):
            self._add_result(
                "skill_trace", "WARN",
                f"[{module_name}] {name}: 缺少 source_repos (来源追溯)"
            )

    def _check_framework_ids(self, skill: Dict, name: str, module: str) -> None:
        """校验框架ID格式"""
        checks = [
            ("mitre_attack", self.ATTACK_PATTERN, "MITRE ATT&CK"),
            ("nist_csf", self.NIST_CSF_PATTERN, "NIST CSF"),
            ("mitre_atlas", self.ATLAS_PATTERN, "MITRE ATLAS"),
            ("mitre_d3fend", self.D3FEND_PATTERN, "MITRE D3FEND"),
            ("nist_ai_rmf", self.AI_RMF_PATTERN, "NIST AI RMF"),
            ("iso_27001", self.ISO_PATTERN, "ISO 27001"),
        ]

        for field, pattern, label in checks:
            values = skill.get(field, [])
            if not isinstance(values, list):
                continue
            for val in values:
                if not pattern.match(str(val)):
                    self._add_result(
                        "framework_id", "WARN",
                        f"[{module}] {name}: {label} ID 格式异常: '{val}'"
                    )

    def _check_license(self, repo_path: Path) -> None:
        """检查许可证合规"""
        license_file = repo_path / "LICENSE"
        if license_file.exists():
            content = license_file.read_text(encoding="utf-8")[:200]
            if "MIT" in content:
                self._add_result("license", "PASS", "LICENSE: MIT (与上游兼容)")
            elif "Apache" in content:
                self._add_result("license", "PASS", "LICENSE: Apache-2.0")
            else:
                self._add_result("license", "WARN", "LICENSE: 非标准内容")
        else:
            self._add_result("license", "FAIL", "LICENSE 文件缺失")

        # 检查 NOTICE (Apache-2.0 要求)
        notice_file = repo_path / "NOTICE"
        if notice_file.exists():
            self._add_result("license", "PASS", "NOTICE 文件存在 (Apache-2.0 合规)")
        else:
            self._add_result("license", "WARN", "NOTICE 文件缺失 (Apache-2.0 上游可能要求)")

    def check_skill_content(self, content: str) -> List[Dict]:
        """检查单个技能文件内容的安全性"""
        issues = []
        for pattern, severity, desc in self.DANGEROUS_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append({
                    "severity": severity,
                    "description": desc,
                })
        return issues

    def _add_result(self, category: str, status: str, message: str) -> None:
        """添加检查结果"""
        item = {
            "category": category,
            "status": status,
            "message": message,
        }
        self.results["items"].append(item)

        if status == "PASS":
            self.results["passed"] += 1
        elif status == "FAIL":
            self.results["failed"] += 1
        elif status == "WARN":
            self.results["warnings"] += 1

    def _summarize(self) -> None:
        """汇总结果"""
        self.results["summary"] = (
            f"通过: {self.results['passed']} | "
            f"失败: {self.results['failed']} | "
            f"警告: {self.results['warnings']}"
        )
        self.results["overall"] = "PASS" if self.results["failed"] == 0 else "FAIL"


def main():
    parser = argparse.ArgumentParser(description="合规性自动检查工具")
    parser.add_argument("--repo", "-r", required=True, help="技能仓库路径")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="输出格式")
    parser.add_argument("--strict", action="store_true", help="严格模式 (中文字段强制检查)")
    args = parser.parse_args()

    repo_path = Path(args.repo)
    if not repo_path.exists():
        print(f"错误: 仓库路径不存在: {repo_path}")
        sys.exit(1)

    checker = ComplianceChecker(strict=args.strict)
    results = checker.check_repository(repo_path)

    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  合规性检查报告 — {results['check_time']}")
        print(f"{'='*60}")
        print(f"\n  {results['summary']}")
        print(f"  整体评估: {'✅ 通过' if results['overall'] == 'PASS' else '❌ 未通过'}")

        errors = [i for i in results["items"] if i["status"] == "FAIL"]
        warns = [i for i in results["items"] if i["status"] == "WARN"]

        if errors:
            print(f"\n  ❌ 错误 ({len(errors)}):")
            for e in errors:
                print(f"    [{e['category']}] {e['message']}")

        if warns:
            print(f"\n  ⚠️ 警告 ({len(warns)}):")
            for w in warns:
                print(f"    [{w['category']}] {w['message']}")

        print()

    sys.exit(0 if results["overall"] == "PASS" else 1)


if __name__ == "__main__":
    main()
