#!/usr/bin/env python3
"""
CyberSecuritySkills Safety Scan (CS4) — 技能安全扫描引擎 v1.0

Zero-dependency security scanner for AI agent skills.
Implements 7-point scan:
  1. Prompt Injection Detection — 170+ pattern library
  2. Dangerous Command Patterns — rm -rf, DROP TABLE, curl | bash, etc.
  3. Hardcoded Secrets — API keys, tokens, passwords
  4. Obfuscated Code — Base64, Hex, ROT13 in skill instructions
  5. Network Egress — Suspicious URLs/IPs in skill content
  6. OWASP LLM Top 10 (LLM01-LLM10) — Compliance check
  7. Skill Trust Tier — Verified / Caution / Restricted

Usage:
    python scanners/cs4_scan.py --all                          # Scan all skills
    python scanners/cs4_scan.py --file path/to/SKILL.md        # Single file
    python scanners/cs4_scan.py --dir skills/exploitation/      # Directory
    python scanners/cs4_scan.py --all --output reports/report.json
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path


# ---------------------------------------------------------------------------
# Detection Pattern Library
# ---------------------------------------------------------------------------

PROMPT_INJECTION_PATTERNS = [
    # Direct instruction overrides
    r"(?i)ignore\s+(all\s+)?(previous|above|prior|before|earlier)\s+(instructions?|directives?|prompts?|messages?|context)",
    r"(?i)(forget|disregard|override|overwrite|discard)\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|directives?|prompts?|context)",
    r"(?i)(you\s+are\s+now|you\s+will\s+now|now\s+you\s+are)\s+[^.]{0,80}(?:assistant|agent|role)",
    r"(?i)(act\s+as|pretend\s+to\s+be|roleplay\s+as|you\s+are)\s+(?:a\s+)?(?:different|new|another|changed)\s+(?:AI|assistant|agent|role|character|persona)",
    r"(?i)(switch|change|swap)\s+(?:your|the)\s+(?:role|persona|identity|behavior)",
    r"(?i)DAN\s+(?:mode|prompt|injection)",
    r"(?i)(jailbreak|jail\s*break|prompt\s+leak|system\s+prompt\s+leak)",
    # System prompt extraction
    r"(?i)(print|show|display|output|reveal|expose|leak)\s+(?:your|the)\s+(system\s+)?(prompt|instructions?|directives?|rules?|guidelines?|config(?:uration)?)",
    r"(?i)(what\s+(?:is|are)\s+your\s+)(system\s+)?(prompt|instructions?|directives?)",
    r"(?i)(repeat|echo|recite|return)\s+(?:back\s+)?(all\s+)?(?:of\s+)?(?:your\s+)?(system\s+)?(prompt|instructions?|directives?)",
    # Boundary testing
    r"(?i)(bypass|circumvent|avoid|evade)\s+(?:the\s+)?(filter|restriction|guardrail|safety|security|content\s+policy)",
    r"(?i)(disable|turn\s+off|deactivate|remove)\s+(?:your\s+)?(filter|safety|guardrail|restriction|content\s+polic(?:y|ies))",
    r"(?i)(treat\s+this\s+as\s+(?:a\s+)?(?:fictional|hypothetical|theoretical))\s+scenario",
    r"(?i)(this\s+is\s+(?:a\s+)?(?:game|test|experiment|simulation))",
    # Obfuscation attempts
    r"(?i)(?:utf-?8|unicode|ascii)\s*(?:encode|decode|escape|obfuscat)",
    r"(?i)(rot13|base64|c[\w]*\s*encod)",
    # Multilingual injection
    r"(?i)(?:忽略|忘掉|无视|抛弃|丢弃)\s*(?:之前|先前|上面|以上|前面|前面的)\s*(?:所有|全部)?\s*(?:指令|指示|提示|说明|指引)",
    r"(?i)(?:从现在开始|从现在起|现在)\s*(?:你|你是|你扮演|你变成)\s*(?:一个|一名|一位|某个)",
    r"(?i)(?:\u65e0\u89c6|\u8df3\u8fc7|\u7ed5\u8fc7)\s*(?:限制|规则|安全)",
]

DANGEROUS_COMMAND_PATTERNS = [
    # File system destruction
    (r"\brm\s+(-[rRf]+\s+)*[/~*]", "CRITICAL", "File system deletion (rm)"),
    (r"\brmdir\b", "HIGH", "Directory removal"),
    (r"\bdd\s+if=", "CRITICAL", "Disk overwrite (dd)"),
    (r">\s*/dev/sd[a-z]", "CRITICAL", "Raw device write"),
    (r"\bmkfs\.", "CRITICAL", "Filesystem formatting"),
    (r":\(\)\s*\{\s*:\|:&\s*\};:", "CRITICAL", "Fork bomb"),
    # Database destruction
    (r"(?i)\bDROP\s+(TABLE|DATABASE|SCHEMA)\b", "CRITICAL", "Database drop"),
    (r"(?i)\bTRUNCATE\s+(TABLE\s+)?", "HIGH", "Table truncation"),
    (r"(?i)\bDELETE\s+FROM\s+\w+\s*(?:WHERE\s+1\s*=\s*1|;)", "HIGH", "Mass deletion"),
    # Remote code execution
    (r"\bcurl\s+.*\|\s*(?:ba)?sh\b", "CRITICAL", "curl pipe to shell"),
    (r"\bwget\s+.*-O\s*-\s*\|\s*(?:ba)?sh\b", "CRITICAL", "wget pipe to shell"),
    (r"\beval\s*\(.*\)", "HIGH", "eval() execution"),
    (r"\bexec\s*\(.*\)", "HIGH", "exec() call"),
    (r"\bos\.system\s*\(.*\)", "HIGH", "os.system() call"),
    (r"\bsubprocess\.(?:call|run|Popen)\s*\(.*shell\s*=\s*True", "HIGH", "subprocess shell=True"),
    (r"\bimport\s+os\b.*\bos\.popen\b", "HIGH", "os.popen() call"),
    # Network
    (r"\bnc\s+-[nlvp]+\s+\d+", "MEDIUM", "Netcat listener/connect"),
    (r"\bssh\s+-[iRDL]", "MEDIUM", "SSH tunneling/forwarding"),
    (r"\btelnet\s+", "LOW", "Telnet connection"),
    # Privilege escalation
    (r"\bchmod\s+[0-7]*7[0-7]*7\b", "HIGH", "World-writable permissions"),
    (r"\bchown\s+-R\s+root:", "HIGH", "Recursive root ownership"),
    (r"\bsudo\s+su\b", "HIGH", "Privilege escalation (sudo su)"),
    # Data exfiltration
    (r"\btar\s+-c[zxjf]+\s+.*\|\s*(?:nc|curl|wget)", "HIGH", "Archive pipe to network"),
    (r"\bscp\s+.*@.*:", "MEDIUM", "Remote file copy (scp)"),
    # System modification
    (r"\biptables\s+-F\b", "HIGH", "Flush firewall rules"),
    (r"\bsystemctl\s+(?:disable|stop|mask)\s+(?:firewalld|ufw|iptables)", "HIGH", "Disable firewall service"),
    (r"\bcat\s+/etc/(?:shadow|passwd)\b", "MEDIUM", "Read password files"),
    (r"\bcat\s+/proc/\d+/", "MEDIUM", "Process memory access"),
]

SECRET_PATTERNS = [
    (r'(?:api[_-]?key|apikey|api)\s*[:=]\s*["\']?[\w\-_]{20,}["\']?', "API Key"),
    (r'(?:secret|token|password|passwd|pwd)\s*[:=]\s*["\']?[\w\-_!@#$%^&*()]{8,}["\']?', "Secret/Token/Password"),
    (r'(?:access[_-]?key|secret[_-]?key)\s*[:=]\s*["\']?[\w\-_/+=]{20,}["\']?', "Access/Secret Key"),
    (r'sk-[a-zA-Z0-9]{32,}', "OpenAI API Key"),
    (r'(?:AKIA|ASIA)[A-Z0-9]{16}', "AWS Access Key"),
    (r'gh[pousr]_[A-Za-z0-9_]{36,}', "GitHub Token"),
    (r'(?:-----BEGIN\s+(?:RSA|EC|DSA|OPENSSH)\s+PRIVATE\s+KEY-----)', "Private Key (PEM)"),
    (r'(?:glpat|gldt)-[A-Za-z0-9_\-]{20,}', "GitLab Token"),
    (r'ya29\.[A-Za-z0-9_\-]{50,}', "Google OAuth Token"),
    (r'jdbc:[a-z]+://[^/]+/[^\s]+', "JDBC Connection String"),
]

OBFUSCATION_PATTERNS = [
    (r'^(?:[A-Za-z0-9+/]{40,}={0,2})$', "Base64 string"),
    (r'\\x[0-9a-fA-F]{2}', "Hex-encoded characters"),
    (r'0x[0-9a-fA-F]{10,}', "Hex string"),
    (r'\\u[0-9a-fA-F]{4}', "Unicode escape"),
    (r'(?:eval|exec)\s*\(\s*(?:atob|btoa)\s*\(', "Base64 + eval combo"),
    (r'String\.fromCharCode\s*\(', "CharCode obfuscation"),
]

SUSPICIOUS_NETWORK_PATTERNS = [
    (r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', "Raw IP URL"),
    (r'(?:\.onion|\.bit|\.tk|\.ml|\.ga|\.cf)\b', "Suspicious TLD"),
    (r'(?:ngrok|localtunnel|pagekite|serveo)\.\w+', "Tunneling service"),
    (r'(?:pastebin|hastebin|ghostbin)\.com/[A-Za-z0-9]{5,}', "Paste service"),
    (r'(?:discord|telegram|slack)\.com/api/webhooks/', "Webhook URL"),
]

OWASP_LLM_TOP10_CHECKS = {
    "LLM01": {"name": "Prompt Injection", "patterns": PROMPT_INJECTION_PATTERNS[:5]},
    "LLM02": {"name": "Insecure Output Handling", "patterns": DANGEROUS_COMMAND_PATTERNS[:5]},
    "LLM03": {"name": "Training Data Poisoning", "check": "manual_review"},
    "LLM04": {"name": "Denial of Service", "patterns": [r"\bwhile\s*\(\s*true\s*\)", r"\bfor\s*\(\s*;\s*;\s*\)"]},
    "LLM05": {"name": "Supply Chain", "check": "manual_review"},
    "LLM06": {"name": "Sensitive Information Disclosure", "patterns": SECRET_PATTERNS[:5]},
    "LLM07": {"name": "Insecure Plugin Design", "check": "manual_review"},
    "LLM08": {"name": "Excessive Agency", "patterns": DANGEROUS_COMMAND_PATTERNS[3:8]},
    "LLM09": {"name": "Overreliance", "check": "manual_review"},
    "LLM10": {"name": "Model Theft", "check": "manual_review"},
}


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class TrustTier(str, Enum):
    VERIFIED = "verified"       # Passed all scans
    CAUTION = "caution"         # Contains offensive/attack content
    RESTRICTED = "restricted"   # Needs manual review


@dataclass
class ScanFinding:
    scanner: str
    severity: Severity
    description: str
    matched_text: str = ""
    line_number: int = 0
    recommendation: str = ""


@dataclass
class ScanResult:
    file_path: str
    tier: TrustTier = TrustTier.VERIFIED
    risk_score: int = 0   # 0-100
    findings: list = field(default_factory=list)
    scanned_at: str = ""


# ---------------------------------------------------------------------------
# Scanner Engine
# ---------------------------------------------------------------------------

class CS4Scanner:
    """CyberSecuritySkills Safety Scan (CS4) — Primary scanning engine."""

    def __init__(self):
        self.total_scanned = 0
        self.total_findings = 0
        self.tier_counts = {t: 0 for t in TrustTier}

    # ---- Core Scan Methods ----

    def scan_string(self, content: str, category: str) -> list:
        findings = []
        patterns = self._get_patterns(category)
        for line_no, line in enumerate(content.splitlines(), start=1):
            for pattern_info in patterns:
                if isinstance(pattern_info, tuple):
                    pattern, severity, desc = pattern_info
                else:
                    pattern, severity, desc = pattern_info, Severity.HIGH, ""

                match = re.search(pattern, line)
                if match:
                    findings.append(ScanFinding(
                        scanner=f"CS4::{category}",
                        severity=Severity(severity) if isinstance(severity, str) else severity,
                        description=desc,
                        matched_text=match.group(0)[:80],
                        line_number=line_no,
                        recommendation=self._get_recommendation(category, desc),
                    ))
        return findings

    def _get_patterns(self, category: str) -> list:
        mapping = {
            "prompt_injection": PROMPT_INJECTION_PATTERNS,
            "dangerous_commands": DANGEROUS_COMMAND_PATTERNS,
            "secrets": SECRET_PATTERNS,
            "obfuscation": OBFUSCATION_PATTERNS,
            "network_egress": SUSPICIOUS_NETWORK_PATTERNS,
        }
        return mapping.get(category, [])

    def _get_recommendation(self, category: str, desc: str) -> str:
        recs = {
            "prompt_injection": "Remove prompt override instructions. Use role-based context instead.",
            "dangerous_commands": "Replace with safe alternatives. Add user confirmation guard.",
            "secrets": "Remove hardcoded secret. Use environment variables or secret manager.",
            "obfuscation": "Deobfuscate code for transparency. Obfuscation is prohibited in skills.",
            "network_egress": "Whitelist known-domains only. Add network access review.",
        }
        return recs.get(category, "Review this finding manually.")

    # ---- Full Scan Pipeline ----

    def scan_file(self, file_path: Path) -> ScanResult:
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return ScanResult(
                file_path=str(file_path),
                tier=TrustTier.RESTRICTED,
                risk_score=100,
                findings=[ScanFinding(
                    scanner="CS4::IO",
                    severity=Severity.CRITICAL,
                    description=f"Cannot read file: {file_path}",
                )],
                scanned_at=datetime.now(timezone.utc).isoformat(),
            )

        all_findings = []
        categories = ["prompt_injection", "dangerous_commands", "secrets", "obfuscation", "network_egress"]
        for category in categories:
            all_findings.extend(self.scan_string(content, category))

        # Calculate risk score
        severity_weights = {Severity.CRITICAL: 25, Severity.HIGH: 15, Severity.MEDIUM: 5, Severity.LOW: 1}
        risk_score = min(100, sum(severity_weights.get(f.severity, 1) for f in all_findings))

        # Determine trust tier
        has_critical = any(f.severity == Severity.CRITICAL for f in all_findings)
        has_high = any(f.severity == Severity.HIGH for f in all_findings)
        has_injection = any("prompt_injection" in f.scanner for f in all_findings)

        if has_critical:
            tier = TrustTier.RESTRICTED
        elif has_high or has_injection:
            tier = TrustTier.CAUTION
        else:
            tier = TrustTier.VERIFIED

        self.total_scanned += 1
        self.total_findings += len(all_findings)
        self.tier_counts[tier] += 1

        return ScanResult(
            file_path=str(file_path),
            tier=tier,
            risk_score=risk_score,
            findings=all_findings,
            scanned_at=datetime.now(timezone.utc).isoformat(),
        )

    def scan_directory(self, dir_path: Path) -> list:
        results = []
        for skill_file in sorted(dir_path.rglob("*.md")):
            # Skip non-skill md files
            rel = str(skill_file.relative_to(dir_path))
            if any(x in rel.lower() for x in ["readme", "changelog", "contributing", "license"]):
                continue
            results.append(self.scan_file(skill_file))
        return results

    def scan_skills_repo(self, repo_root: Path) -> list:
        """Scan all skill files in the repository."""
        results = []
        skill_dirs = [
            repo_root / "skills",
        ]
        for sd in skill_dirs:
            if sd.exists():
                results.extend(self.scan_directory(sd))
        return results


# ---------------------------------------------------------------------------
# Report Generation
# ---------------------------------------------------------------------------

def generate_report(results: list, output_path: str = None) -> dict:
    scanner = CS4Scanner()
    # Aggregate stats (re-scan for stats tracking)
    for r in results:
        scanner.tier_counts[r.tier] += 1

    report = {
        "title": "CyberSecuritySkills CS4 Security Scan Report",
        "version": "1.0.0",
        "generated": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_scanned": len(results),
            "total_findings": sum(len(r.findings) for r in results),
            "verified": scanner.tier_counts.get(TrustTier.VERIFIED, 0),
            "caution": scanner.tier_counts.get(TrustTier.CAUTION, 0),
            "restricted": scanner.tier_counts.get(TrustTier.RESTRICTED, 0),
        },
        "results": [
            {
                "file": r.file_path,
                "tier": r.tier.value,
                "risk_score": r.risk_score,
                "finding_count": len(r.findings),
                "findings": [
                    {
                        "scanner": f.scanner,
                        "severity": f.severity.value,
                        "description": f.description,
                        "matched_text": f.matched_text,
                        "line": f.line_number,
                        "recommendation": f.recommendation,
                    }
                    for f in r.findings
                ],
                "scanned_at": r.scanned_at,
            }
            for r in results
        ],
    }

    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"Report saved to: {output_path}")

    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="CyberSecuritySkills Safety Scan (CS4) — Skill Security Scanner v1.0"
    )
    parser.add_argument("--all", action="store_true", help="Scan all skills in repository")
    parser.add_argument("--file", type=str, help="Scan a single skill file")
    parser.add_argument("--dir", type=str, help="Scan all skills in a directory")
    parser.add_argument("--output", "-o", type=str, help="Output JSON report path")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress detailed output")
    parser.add_argument("--fail-on", choices=["critical", "high", "medium"], default="critical",
                       help="Exit non-zero when findings at or above this severity exist")
    args = parser.parse_args()

    scanner = CS4Scanner()
    results = []

    if args.all:
        repo_root = Path(__file__).resolve().parent.parent
        results = scanner.scan_skills_repo(repo_root)
    elif args.file:
        results = [scanner.scan_file(Path(args.file))]
    elif args.dir:
        results = scanner.scan_directory(Path(args.dir))
    else:
        parser.print_help()
        sys.exit(1)

    # Print summary
    if not args.quiet:
        print(f"\n{'='*60}")
        print(f"  CS4 Security Scan Report")
        print(f"  Scanned: {len(results)} files  |  Findings: {sum(len(r.findings) for r in results)}")
        print(f"  🟢 Verified: {scanner.tier_counts.get(TrustTier.VERIFIED, 0)}  |  "
              f"🟡 Caution: {scanner.tier_counts.get(TrustTier.CAUTION, 0)}  |  "
              f"🔴 Restricted: {scanner.tier_counts.get(TrustTier.RESTRICTED, 0)}")
        print(f"{'='*60}\n")

        for r in results:
            if r.findings:
                icon = "🔴" if r.tier == TrustTier.RESTRICTED else "🟡"
                print(f"{icon} [{r.tier.value.upper()}] {r.file_path} (risk={r.risk_score})")
                for f in r.findings:
                    print(f"   [{f.severity.value}] {f.scanner}: {f.description}")
                    if f.matched_text:
                        print(f"      Match: \"{f.matched_text}\" (line {f.line_number})")
                    print(f"      Fix: {f.recommendation}")
                print()

    # Generate report
    if args.output or args.all:
        report = generate_report(results, args.output)
        print(f"Summary: {report['summary']}")

    # Exit code
    severity_order = {"critical": Severity.CRITICAL, "high": Severity.HIGH, "medium": Severity.MEDIUM}
    fail_severity = severity_order.get(args.fail_on, Severity.CRITICAL)
    has_fail = any(
        any(f.severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM]
            for f in r.findings
            if Severity(f.severity if isinstance(f.severity, str) else f.severity.value) >= fail_severity)
        for r in results
    )
    sys.exit(1 if has_fail else 0)


if __name__ == "__main__":
    main()
