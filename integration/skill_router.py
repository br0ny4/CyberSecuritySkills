"""
智能路由引擎 — Skill Router
===============================
基于上下文感知的跨Agent技能路由引擎，根据查询意图、平台能力和技能元数据
自动选择最优技能和最佳执行平台。

路由策略:
  1. 语义匹配 → 基于关键词 + 子领域权重
  2. 平台能力 → 根据平台 max_skills / supports_batch 调整
  3. 成本优化 → DeepSeek V4 Flash 优先 (低成本), Pro 用于精确任务
  4. 合规路由 → 等保2.0 场景自动路由到国内平台 (Flocks/Trae)

Author: Unified Security Skills Team
License: MIT
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from adapters.base.adapter_base import SkillMetadata, SkillSearchQuery

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CROSSWALK_PATH = PROJECT_ROOT / "schema" / "crosswalk.json"


class RouteIntent(str, Enum):
    """路由意图"""
    SEARCH = "search"               # 技能搜索
    EXECUTE = "execute"             # 单技能执行
    BATCH = "batch"                # 批量执行
    CHAIN = "chain"                # 技能链
    REPORT = "report"              # 报告生成
    COMPLIANCE = "compliance"      # 合规检查


class PlatformPreference(str, Enum):
    """平台偏好"""
    BEST_AVAILABLE = "best"        # 自动选择最佳
    DEEPSEEK_V4 = "deepseek-v4"
    TRAE = "trae"
    FLOCKS = "flocks"
    CLAUDE_CODE = "claude-code"
    CURSOR = "cursor"


@dataclass
class RoutingDecision:
    """路由决策结果"""
    intent: RouteIntent
    selected_skills: List[str]
    target_platform: PlatformPreference
    confidence: float  # 0.0 - 1.0
    reasoning: str
    estimated_tokens: int = 0
    estimated_cost_cny: float = 0.0
    alternatives: List[Tuple[str, float]] = field(default_factory=list)


class SkillRouter:
    """
    技能智能路由器

    核心功能:
      - 上下文感知的意图解析
      - 基于框架映射的领域自动匹配
      - 多平台负载均衡与成本优化
      - 合规场景自动路由 (等保/ISO)
    """

    # 关键词→子领域映射
    KEYWORD_MAP = {
        "渗透": ["penetration-testing", "exploitation", "reconnaissance"],
        "漏洞": ["vulnerability-scanning", "exploitation", "vulnerability-management"],
        "应急": ["incident-response"],
        "响应": ["incident-response"],
        "取证": ["digital-forensics"],
        "流量": ["network-security", "malware-analysis"],
        "钓鱼": ["phishing-defense", "social-engineering"],
        "勒索": ["ransomware-defense"],
        "云": ["cloud-security"],
        "容器": ["container-security"],
        "kubernetes": ["container-security"],
        "K8s": ["container-security"],
        "API": ["api-security"],
        "LLM": ["llm-security"],
        "大模型": ["llm-security"],
        "AI安全": ["llm-security"],
        "工控": ["ics-ot-security"],
        "SCADA": ["ics-ot-security"],
        "区块链": ["blockchain-web3-security"],
        "Web3": ["blockchain-web3-security"],
        "供应链": ["supply-chain-security"],
        "等保": ["security-audit", "governance-compliance"],
        "合规": ["governance-compliance"],
        "ISO27001": ["governance-compliance"],
        "零信任": ["zero-trust"],
        "IAM": ["iam"],
        "身份": ["iam"],
        "密码": ["cryptography-pki"],
        "TLS": ["cryptography-pki"],
        "Windows提权": ["privilege-escalation"],
        "Linux提权": ["privilege-escalation"],
        "内存": ["digital-forensics", "malware-analysis"],
        "volatility": ["digital-forensics"],
        "CobaltStrike": ["malware-analysis", "threat-intelligence"],
        "横向移动": ["lateral-movement"],
        "持久化": ["persistence"],
        "红队": ["red-blue-team"],
        "蓝队": ["red-blue-team"],
        "威胁情报": ["threat-intelligence"],
        "SOC": ["soc-operations"],
    }

    # ATT&CK 技术→子领域映射
    ATTACK_TECHNIQUE_MAP = {
        "T1003": ["digital-forensics", "credential-access"],
        "T1059": ["threat-hunting"],
        "T1566": ["phishing-defense"],
        "T1486": ["ransomware-defense"],
        "T1190": ["exploitation"],
        "T1595": ["vulnerability-scanning"],
        "T1590": ["reconnaissance"],
    }

    # 合规→平台路由
    COMPLIANCE_PLATFORM_MAP = {
        "等保": [PlatformPreference.FLOCKS, PlatformPreference.TRAE],
        "等级保护": [PlatformPreference.FLOCKS, PlatformPreference.TRAE],
        "ISO27001": [PlatformPreference.FLOCKS],
    }

    def __init__(self, crosswalk: Optional[Dict] = None):
        self.crosswalk = crosswalk or self._load_crosswalk()

    def _load_crosswalk(self) -> Dict:
        if CROSSWALK_PATH.exists():
            with open(CROSSWALK_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def parse_intent(self, query: str) -> RouteIntent:
        """
        意图解析: 从用户查询中识别技能调用意图

        规则:
        - "搜索/查找/有哪些/列出" → SEARCH
        - "执行/运行/做" → EXECUTE
        - "批量/全部" → BATCH
        - "流程/链" → CHAIN
        - "报告/总结" → REPORT
        - "合规/等保/审计" → COMPLIANCE
        """
        query_lower = query.lower()

        if any(w in query_lower for w in ["合规", "等保", "iso27001", "审计", "audit"]):
            return RouteIntent.COMPLIANCE
        if any(w in query_lower for w in ["报告", "总结", "导出", "report", "summary"]):
            return RouteIntent.REPORT
        if any(w in query_lower for w in ["流程", "链", "chain", "pipeline", "workflow"]):
            return RouteIntent.CHAIN
        if any(w in query_lower for w in ["批量", "全部", "batch", "all"]):
            return RouteIntent.BATCH
        if any(w in query_lower for w in ["搜索", "查找", "找", "有哪些", "列出", "search", "find", "list"]):
            return RouteIntent.SEARCH
        return RouteIntent.EXECUTE

    def extract_subdomains(self, query: str) -> List[str]:
        """从查询中提取子领域"""
        found = set()
        query_lower = query.lower()

        for keyword, domains in self.KEYWORD_MAP.items():
            if keyword.lower() in query_lower:
                found.update(domains)

        # ATT&CK 技术匹配
        for tech, domains in self.ATTACK_TECHNIQUE_MAP.items():
            if tech in query.upper():
                found.update(domains)

        # 英文关键词
        en_matches = {
            "forensic": "digital-forensics", "malware": "malware-analysis",
            "ransomware": "ransomware-defense", "cloud": "cloud-security",
            "incident": "incident-response", "threat": "threat-hunting",
            "pentest": "penetration-testing", "red team": "red-blue-team",
        }
        for en_kw, domain in en_matches.items():
            if en_kw in query_lower:
                found.add(domain)

        return list(found) if found else []

    def route_platform(self, intent: RouteIntent, subdomains: List[str]) -> PlatformPreference:
        """
        平台路由: 根据意图和子领域选择最佳平台

        策略:
        - COMPLIANCE + 等保 → Flocks/Trae (国内平台)
        - BATCH → Flocks (支持10并行) or DeepSeek V4
        - CHAIN → DeepSeek V4 Pro (精确执行)
        - 默认 → DeepSeek V4 Flash (成本最优)
        """

        # 合规路由
        if intent == RouteIntent.COMPLIANCE:
            return PlatformPreference.FLOCKS

        # 批量执行 → Flocks
        if intent == RouteIntent.BATCH:
            return PlatformPreference.FLOCKS

        # 高精度需求 → V4 Pro
        precise_domains = {"exploitation", "reverse-engineering", "malware-analysis", "digital-forensics"}
        if subdomains and any(d in precise_domains for d in subdomains):
            return PlatformPreference.DEEPSEEK_V4

        # 默认
        if intent == RouteIntent.SEARCH:
            return PlatformPreference.DEEPSEEK_V4
        return PlatformPreference.DEEPSEEK_V4

    def rank_skills(
        self,
        skills: List[SkillMetadata],
        query: str,
        intent: RouteIntent,
        limit: int = 10,
    ) -> List[Tuple[SkillMetadata, float]]:
        """
        技能排序: 多维度加权评分

        维度:
        - 领域匹配度 (40%)
        - 关键词匹配度 (30%)
        - 难度适配 (15%)
        - 框架覆盖度 (10%)
        - Token效率 (5%)
        """
        subdomains = self.extract_subdomains(query)
        query_lower = query.lower()
        scored: List[Tuple[SkillMetadata, float]] = []

        for meta in skills:
            score = 0.0

            # 领域匹配
            if meta.subdomain in subdomains:
                score += 40

            # 关键词匹配
            kw_score = 0
            if any(kw in query_lower for kw in (meta.name_cn or "").lower().split()):
                kw_score += 15
            if meta.description and any(w in query_lower for w in meta.description.lower().split()):
                kw_score += 10
            if meta.tags and any(w in query_lower for w in meta.tags):
                kw_score += 5
            if meta.tags_cn and any(w in query_lower for w in meta.tags_cn):
                kw_score += 5
            score += min(kw_score, 30)

            # 难度适配
            stars = meta.difficulty.count("★")
            if intent == RouteIntent.EXECUTE and stars >= 3:
                score += 10  # 执行场景偏好3-5星
            elif intent == RouteIntent.SEARCH:
                score += 5  # 搜索不区分难度

            # 框架覆盖度
            framework_count = len(meta.mitre_attack) + len(meta.nist_csf) + len(meta.mitre_atlas)
            score += min(framework_count * 2, 10)

            # Token效率 (低token消耗的技能得分更高)
            if meta.estimated_tokens > 0:
                score += min(5000 / meta.estimated_tokens, 5)

            scored.append((meta, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:limit]

    def decide(
        self,
        query: str,
        available_skills: List[SkillMetadata],
        preferred_platform: Optional[PlatformPreference] = None,
        limit: int = 5,
    ) -> RoutingDecision:
        """
        综合路由决策

        Args:
            query: 用户查询
            available_skills: 可用技能列表
            preferred_platform: 用户偏好的平台
            limit: 最大返回技能数

        Returns:
            RoutingDecision: 包含选中的技能、平台、置信度
        """
        intent = self.parse_intent(query)
        subdomains = self.extract_subdomains(query)

        # 平台选择
        platform = preferred_platform or self.route_platform(intent, subdomains)

        # 技能排序
        ranked = self.rank_skills(available_skills, query, intent, limit)

        if not ranked:
            return RoutingDecision(
                intent=intent,
                selected_skills=[],
                target_platform=platform,
                confidence=0.0,
                reasoning=f"未找到匹配 '{query}' 的技能",
            )

        selected_names = [m.name for m, _ in ranked]
        top_score = ranked[0][1]
        confidence = min(top_score / 60.0, 1.0) if top_score > 0 else 0.1

        # Token + 成本估算
        total_tokens = sum(m.estimated_tokens for m, _ in ranked if m.estimated_tokens)
        cost_per_1m_input = 0.1  # DeepSeek V4 Flash: ¥0.1/1M input
        estimated_cost = total_tokens / 1_000_000 * cost_per_1m_input

        alt_platforms = list(PlatformPreference)
        alt_platforms.remove(platform)
        alternatives = [(p.value, confidence * 0.7) for p in alt_platforms[:3]]

        reasons = []
        if subdomains:
            reasons.append(f"领域匹配: {', '.join(subdomains[:3])}")
        reasons.append(f"Top技能: {selected_names[0]}")
        reasons.append(f"平台: {platform.value}")

        return RoutingDecision(
            intent=intent,
            selected_skills=selected_names,
            target_platform=platform,
            confidence=round(confidence, 3),
            reasoning="; ".join(reasons),
            estimated_tokens=total_tokens,
            estimated_cost_cny=round(estimated_cost, 4),
            alternatives=alternatives,
        )
