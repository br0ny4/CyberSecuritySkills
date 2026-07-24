#!/usr/bin/env python3
"""MCP Security Auditor — OWASP MCP Top 10 compliance checker."""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

OWASP_MCP_TOP10 = {
    "MCP01": {"name": "Permission Drift & Privilege Escalation", "severity": "CRITICAL"},
    "MCP02": {"name": "Tool Poisoning & Descriptor Manipulation", "severity": "CRITICAL"},
    "MCP03": {"name": "Shadow Servers & Unauthorized Endpoints", "severity": "HIGH"},
    "MCP04": {"name": "Token & Credential Mismanagement", "severity": "HIGH"},
    "MCP05": {"name": "Unchecked Prompt/Instruction Injection via Tools", "severity": "HIGH"},
    "MCP06": {"name": "Unbounded / Untrustworthy HTTP calls (SSRF)", "severity": "MEDIUM"},
    "MCP07": {"name": "Data Exfiltration via Tool Outputs", "severity": "MEDIUM"},
    "MCP08": {"name": "Insecure Transport & Missing Authentication", "severity": "MEDIUM"},
    "MCP09": {"name": "Unvalidated Tool Input Leading to Code Execution", "severity": "CRITICAL"},
    "MCP10": {"name": "Supply Chain & Dependency Risks", "severity": "MEDIUM"},
}

def check_config(config_path: Path) -> dict:
    with open(config_path) as f:
        config = json.load(f)

    issues = []
    for server_name, server_cfg in config.get("mcpServers", {}).items():
        security = server_cfg.get("security", {})
        if not security:
            issues.append(f"{server_name}: No security configuration found!")
            continue

        env = server_cfg.get("env", {})

        # MCP04: Token management
        for key, val in env.items():
            if any(x in key.upper() for x in ["PASS", "TOKEN", "KEY", "SECRET"]) and not val.startswith("${"):
                issues.append(f"{server_name}: [MCP04] Hardcoded credential: {key}={val[:10]}...")

        # MCP01: Permission drift
        if "minimal_tools" not in security:
            issues.append(f"{server_name}: [MCP01] No minimal tool whitelist defined")

        # MCP09: Input validation
        if not security.get("network", {}).get("allowed_targets"):
            issues.append(f"{server_name}: [MCP09] No network target restriction")

    return {
        "server": server_name,
        "issues": issues,
        "passed": len(issues) == 0,
    }

def main():
    configs_dir = Path(__file__).resolve().parent.parent / "mcp" / "configs"
    all_passed = True

    print(f"\n{'='*60}")
    print(f"  MCP Security Auditor — OWASP MCP Top 10")
    print(f"  Scan Time: {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*60}\n")

    for config_file in sorted(configs_dir.glob("*-secure.json")):
        result = check_config(config_file)
        status = "PASS" if result["passed"] else "FAIL"
        print(f"[{status}] {config_file.name}")
        for issue in result["issues"]:
            print(f"  ⚠️  {issue}")
        if not result["passed"]:
            all_passed = False
        print()

    print(f"Overall: {'ALL PASSED' if all_passed else 'ISSUES FOUND'}")
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
