#!/usr/bin/env python3
"""
测试套件 — Test Suite
========================
覆盖: 适配器接口、统一接口层(CAUI)、DeepSeek 优化器、合规检查

运行:
  python -m pytest tests/ -v

Author: Unified Security Skills Team
License: MIT
"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# 将项目根加入路径
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from adapters.base.adapter_base import (
    BaseSkillAdapter,
    SkillExecutionContext,
    SkillExecutionMode,
    SkillExecutionResult,
    SkillMetadata,
    SkillSearchQuery,
    SkillStatus,
)
from adapters.deepseek_v4.optimizer import (
    DeepSeekSkillOptimizer,
    DeepSeekOptimizationConfig,
    OptimizationStrategy,
    TokenBudget,
)
from integration.skill_router import SkillRouter, RouteIntent, PlatformPreference, RoutingDecision
from integration.prompt_builder import PromptBuilder, PromptConfig


class TestSkillMetadata(unittest.TestCase):
    """测试 SkillMetadata 数据类"""

    def test_from_dict(self):
        data = {
            "name": "test-skill",
            "description": "A test skill for unit testing",
            "domain": "cybersecurity",
            "subdomain": "digital-forensics",
            "mitre_attack": ["T1003"],
            "nist_csf": ["DE.CM-01"],
            "difficulty": "★★★★☆",
            "tags": ["forensics", "test"],
        }
        meta = SkillMetadata.from_dict(data)

        self.assertEqual(meta.name, "test-skill")
        self.assertEqual(meta.subdomain, "digital-forensics")
        self.assertEqual(meta.mitre_attack, ["T1003"])
        self.assertEqual(meta.difficulty, "★★★★☆")

    def test_to_dict_roundtrip(self):
        meta = SkillMetadata(
            name="roundtrip-test",
            description="Testing serialization",
            subdomain="threat-hunting",
            difficulty="★★★☆☆",
            tags=["hunting"],
        )
        data = meta.to_dict()
        restored = SkillMetadata.from_dict(data)
        self.assertEqual(meta.name, restored.name)
        self.assertEqual(meta.subdomain, restored.subdomain)


class TestSkillExecutionContext(unittest.TestCase):
    """测试执行上下文"""

    def test_default_values(self):
        ctx = SkillExecutionContext(skill_name="test-skill")
        self.assertEqual(ctx.skill_name, "test-skill")
        self.assertEqual(ctx.mode, SkillExecutionMode.SYNC)
        self.assertEqual(ctx.timeout_seconds, 300)
        self.assertEqual(ctx.max_retries, 3)

    def test_with_params(self):
        ctx = SkillExecutionContext(
            skill_name="test-skill",
            parameters={"target": "192.168.1.1"},
            mode=SkillExecutionMode.STREAM,
            timeout_seconds=120,
        )
        self.assertEqual(ctx.parameters["target"], "192.168.1.1")
        self.assertEqual(ctx.mode, SkillExecutionMode.STREAM)


class TestSkillExecutionResult(unittest.TestCase):
    """测试执行结果"""

    def test_success_result(self):
        result = SkillExecutionResult(
            skill_name="test",
            status=SkillStatus.COMPLETED,
            output="Analysis complete",
            execution_time_ms=1500,
            tokens_used=500,
        )
        d = result.to_dict()
        self.assertEqual(d["status"], "completed")
        self.assertEqual(d["output"], "Analysis complete")

    def test_failed_result(self):
        result = SkillExecutionResult(
            skill_name="test",
            status=SkillStatus.FAILED,
            error="Connection timeout",
        )
        self.assertEqual(result.status, SkillStatus.FAILED)
        self.assertEqual(result.error, "Connection timeout")


class TestDeepSeekOptimizer(unittest.TestCase):
    """测试 DeepSeek V4 优化器"""

    def setUp(self):
        self.optimizer = DeepSeekSkillOptimizer()

    def test_estimate_tokens(self):
        content = "This is a sample skill content with approximately twenty words for token estimation testing."
        tokens = self.optimizer.estimate_skill_tokens(content)
        self.assertGreater(tokens, 0)
        self.assertLess(tokens, 50)

    def test_compress_skill_accuracy_mode(self):
        content = """## Workflow
Step 1: Do X
Step 2: Do Y
## Verification
Check result Z
## Tools
Tool A, Tool B"""
        result = self.optimizer.compress_skill_for_context(content, OptimizationStrategy.ACCURACY)
        self.assertEqual(result, content)

    def test_compress_skill_cost_mode(self):
        content = "## Workflow\nStep 1: Run command\nStep 2: Analyze output\n# Comment\n"
        result = self.optimizer.compress_skill_for_context(content, OptimizationStrategy.COST)
        self.assertIn("Step 1:", result)
        self.assertIn("Step 2:", result)

    def test_parse_skill_sections(self):
        content = "## Workflow\nw1\nw2\n## Verification\nv1\nv2\n## Tools\nt1"
        sections = self.optimizer._parse_skill_sections(content)
        self.assertIn("Workflow", sections)
        self.assertIn("Verification", sections)

    def test_deduplicate_function_calls(self):
        calls = [
            {"function": {"name": "skill_a"}},
            {"function": {"name": "skill_a"}},
            {"function": {"name": "skill_b"}},
        ]
        unique = self.optimizer.deduplicate_function_calls(calls)
        self.assertEqual(len(unique), 2)

    def test_cache(self):
        self.optimizer.set_cached_skill("test", {"key": "value"})
        cached = self.optimizer.get_cached_skill("test")
        self.assertIsNotNone(cached)
        self.assertEqual(cached["data"]["key"], "value")

        stats = self.optimizer.get_stats()
        self.assertEqual(stats["cache_hits"], 1)

    def test_build_tool_definitions(self):
        metas = [
            {"name": "skill-a", "description": "Skill A description"},
            {"name": "skill-b", "description": "Skill B description"},
        ]
        tools = self.optimizer.build_tool_definitions(metas)
        self.assertEqual(len(tools), 2)
        self.assertEqual(tools[0]["function"]["name"], "execute_skill-a")

    def test_progressive_load_plan(self):
        skills = [f"skill-{i}" for i in range(20)]
        metas = [{"name": s} for s in skills]
        plan = self.optimizer.progressive_load_plan(skills, metas)
        self.assertEqual(len(plan), 3)
        self.assertEqual(len(plan[0]), 5)   # top-5
        self.assertEqual(len(plan[1]), 7)   # next-7
        self.assertEqual(len(plan[2]), 8)   # remaining 8


class TestSkillRouter(unittest.TestCase):
    """测试智能路由引擎"""

    def setUp(self):
        self.router = SkillRouter()

    def test_parse_intent_search(self):
        intent = self.router.parse_intent("搜索内存取证相关技能")
        self.assertEqual(intent, RouteIntent.SEARCH)

        intent = self.router.parse_intent("find ransomware analysis skills")
        self.assertEqual(intent, RouteIntent.SEARCH)

    def test_parse_intent_execute(self):
        intent = self.router.parse_intent("执行勒索软件分析")
        self.assertEqual(intent, RouteIntent.EXECUTE)

    def test_parse_intent_compliance(self):
        intent = self.router.parse_intent("检查等保2.0合规性")
        self.assertEqual(intent, RouteIntent.COMPLIANCE)

    def test_parse_intent_chain(self):
        intent = self.router.parse_intent("执行渗透测试完整流程")
        self.assertEqual(intent, RouteIntent.CHAIN)

    def test_extract_subdomains(self):
        domains = self.router.extract_subdomains("针对勒索软件的应急响应和内存取证")
        self.assertIn("ransomware-defense", domains)
        self.assertIn("incident-response", domains)
        self.assertIn("digital-forensics", domains)

    def test_extract_english(self):
        domains = self.router.extract_subdomains("malware analysis and cloud forensics")
        self.assertIn("malware-analysis", domains)
        self.assertIn("cloud-security", domains)

    def test_route_platform_compliance(self):
        platform = self.router.route_platform(RouteIntent.COMPLIANCE, ["governance-compliance"])
        self.assertEqual(platform, PlatformPreference.FLOCKS)

    def test_route_platform_batch(self):
        platform = self.router.route_platform(RouteIntent.BATCH, [])
        self.assertEqual(platform, PlatformPreference.FLOCKS)

    def test_rank_skills(self):
        skills = [
            SkillMetadata(name="s1", description="memory forensics", subdomain="digital-forensics",
                         difficulty="★★★★☆", tags=["forensics", "volatility"], estimated_tokens=2000),
            SkillMetadata(name="s2", description="web scanner", subdomain="vulnerability-scanning",
                         difficulty="★★☆☆☆", tags=["scan", "web"], estimated_tokens=1500),
            SkillMetadata(name="s3", description="cloud audit", subdomain="cloud-security",
                         difficulty="★★★☆☆", tags=["cloud", "aws"], estimated_tokens=2500,
                         mitre_attack=["T1003"], nist_csf=["DE.CM-01"]),
        ]
        ranked = self.router.rank_skills(skills, "内存取证分析 volatility", RouteIntent.EXECUTE)
        self.assertGreaterEqual(len(ranked), 1)
        # s1 应该是 top 匹配
        self.assertEqual(ranked[0][0].name, "s1")

    def test_decide(self):
        skills = [
            SkillMetadata(name="ransomware-analysis", description="Analyze ransomware",
                         subdomain="ransomware-defense", difficulty="★★★★☆",
                         tags=["ransomware"], estimated_tokens=2000),
        ]
        decision = self.router.decide("分析勒索软件", skills)
        self.assertIn("ransomware-analysis", decision.selected_skills)
        self.assertGreater(decision.confidence, 0.0)


class TestPromptBuilder(unittest.TestCase):
    """测试 Prompt 构建器"""

    def setUp(self):
        self.builder = PromptBuilder()

    def test_build_system_prompt(self):
        metas = [
            SkillMetadata(
                name="test-skill",
                description="Test skill",
                subdomain="digital-forensics",
                difficulty="★★★☆☆",
                mitre_attack=["T1003"],
            ),
        ]
        prompt = self.builder.build_system_prompt(metas)
        self.assertIn("test-skill", prompt)
        self.assertIn("T1003", prompt)
        self.assertIn("Execution Rules", prompt)

    def test_build_trae_prompt(self):
        metas = [
            SkillMetadata(
                name="test-skill",
                description="Test",
                subdomain="incident-response",
                difficulty="★★★★☆",
                name_cn="测试技能",
                category_cn="应急响应",
            ),
        ]
        prompt = self.builder.build_trae_prompt(metas, {})
        self.assertIn("Trae IDE", prompt)

    def test_build_deepseek_prompt_json(self):
        metas = [SkillMetadata(name="test", description="Test", subdomain="threat-hunting",
                               difficulty="★★★☆☆")]
        prompt = self.builder.build_deepseek_v4_prompt(metas, {}, json_output=True)
        self.assertIn("JSON", prompt)

    def test_build_flocks_prompt(self):
        metas = [SkillMetadata(name="test", description="Test", subdomain="soc-operations",
                               difficulty="★★☆☆☆")]
        prompt = self.builder.build_flocks_prompt(metas, {})
        self.assertIn("Flocks", prompt)


if __name__ == "__main__":
    unittest.main()
