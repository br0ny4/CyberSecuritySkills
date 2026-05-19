"""
跨平台Prompt构建器 — Cross-Platform Prompt Builder
=========================================================
为不同 AI Agent 平台生成结构化系统提示词。

支持平台:
  - Trae: 中英双语, 强调中文安全术语
  - Flocks: YAML 原生格式
  - Claude Code: agentskills.io 标准格式
  - Cursor: Markdown + .cursorrules
  - DeepSeek V4: Function Calling + JSON 输出

Author: Unified Security Skills Team
License: MIT
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from adapters.base.adapter_base import SkillMetadata

logger = logging.getLogger(__name__)


@dataclass
class PromptConfig:
    """Prompt 构建配置"""
    platform: str = "generic"
    language: str = "zh-CN"          # zh-CN | en-US | bilingual
    max_system_prompt_tokens: int = 5000
    include_framework_mappings: bool = True
    include_tool_definitions: bool = False
    output_format: str = "markdown"  # markdown | json | yaml | text
    verbose: bool = False
    extra_instructions: str = ""


class PromptBuilder:
    """
    跨平台 Prompt 构建器

    为不同平台生成适配的系统提示词，确保技能指令在不同模型中
    都能被正确理解和执行。
    """

    PLATFORM_TEMPLATES = {
        "trae": {
            "system_prefix": (
                "你是一名由 Trae IDE 驱动的网络安全 AI 分析师。\n"
                "你已加载以下专业技能，请严格按 Workflow 逐步执行。\n"
                "对于中文输入，请以中文回复。对于英文输入，请以英文回复。\n"
            ),
            "skill_format": "markdown",
            "chinese_emphasis": True,
        },
        "flocks": {
            "system_prefix": (
                "You are a cybersecurity AI agent powered by the Flocks framework.\n"
                "You have been assigned the following skill to execute.\n"
                "Follow the workflow precisely and report each step's result.\n"
            ),
            "skill_format": "yaml",
            "chinese_emphasis": True,
        },
        "claude-code": {
            "system_prefix": (
                "You are a cybersecurity expert AI agent operating within Claude Code.\n"
                "You have access to structured security skills following the agentskills.io standard.\n"
                "Execute the loaded skill workflow methodically and verify each step.\n"
            ),
            "skill_format": "markdown",
            "chinese_emphasis": False,
        },
        "cursor": {
            "system_prefix": (
                "You are a security-focused AI agent running in Cursor IDE.\n"
                "The following cybersecurity skill has been loaded into your context.\n"
                "Execute it step-by-step and return structured results.\n"
            ),
            "skill_format": "markdown",
            "chinese_emphasis": False,
        },
        "deepseek-v4": {
            "system_prefix": (
                "你是一个由 DeepSeek V4 驱动的网络安全 AI 分析引擎。\n"
                "目标：执行以下专业技能的工作流，输出结构化的 JSON 结果。\n"
                "规则：逐步骤执行，不跳过验证步骤，不假设未确认的结果。\n"
            ),
            "skill_format": "function-calling",
            "chinese_emphasis": True,
            "json_output": True,
        },
        "generic": {
            "system_prefix": (
                "You are a cybersecurity AI agent.\n"
                "Execute the loaded skill workflow and return the results.\n"
            ),
            "skill_format": "markdown",
            "chinese_emphasis": False,
        },
    }

    def __init__(self, config: Optional[PromptConfig] = None):
        self.config = config or PromptConfig()

    def build_system_prompt(
        self,
        skill_metadatas: List[SkillMetadata],
        skill_contents: Optional[Dict[str, str]] = None,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        构建完整的系统提示词

        Args:
            skill_metadatas: 技能元数据列表
            skill_contents: {skill_name: content} 技能完整内容映射
            user_context: 用户提供的额外上下文

        Returns:
            str: 完整的系统提示词
        """
        template = self.PLATFORM_TEMPLATES.get(
            self.config.platform, self.PLATFORM_TEMPLATES["generic"]
        )

        parts = [template["system_prefix"]]

        # 技能加载
        parts.append(self._build_skills_section(skill_metadatas, skill_contents, template))

        # 框架映射
        if self.config.include_framework_mappings:
            parts.append(self._build_framework_section(skill_metadatas))

        # 执行规则
        parts.append(self._build_rules_section(template))

        # 输出格式
        parts.append(self._build_output_section(template))

        # 额外指令
        if self.config.extra_instructions:
            parts.append(self.config.extra_instructions)

        return "\n\n".join(parts)

    def _build_skills_section(
        self,
        metas: List[SkillMetadata],
        contents: Optional[Dict[str, str]],
        template: Dict,
    ) -> str:
        """构建技能加载部分"""
        lines = ["## 已加载技能 / Loaded Skills", ""]

        for i, meta in enumerate(metas, 1):
            display_name = meta.name_cn or meta.name
            lines.append(f"### Skill {i}: {display_name}")
            lines.append(f"- **Name**: `{meta.name}`")
            lines.append(f"- **Domain**: {meta.subdomain}")
            lines.append(f"- **Difficulty**: {meta.difficulty}")
            if meta.mitre_attack:
                lines.append(f"- **ATT&CK**: {', '.join(meta.mitre_attack[:5])}")
            if meta.nist_csf:
                lines.append(f"- **NIST CSF**: {', '.join(meta.nist_csf[:5])}")
            lines.append("")

            # 加载完整内容
            if contents and meta.name in contents:
                if self.config.verbose:
                    lines.append(contents[meta.name])
                else:
                    # 精简模式: 仅 Workflow
                    content = contents[meta.name]
                    workflow = self._extract_workflow(content)
                    if workflow:
                        lines.append(f"```\n{workflow}\n```")
                lines.append("")

        return "\n".join(lines)

    def _build_framework_section(self, metas: List[SkillMetadata]) -> str:
        """构建框架映射部分"""
        all_attack = set()
        all_csf = set()
        all_d3fend = set()

        for meta in metas:
            all_attack.update(meta.mitre_attack)
            all_csf.update(meta.nist_csf)
            all_d3fend.update(meta.mitre_d3fend)

        lines = ["## 框架映射 / Framework Mappings", ""]
        if all_attack:
            lines.append(f"- **MITRE ATT&CK**: {', '.join(sorted(all_attack)[:10])}")
        if all_csf:
            lines.append(f"- **NIST CSF 2.0**: {', '.join(sorted(all_csf)[:10])}")
        if all_d3fend:
            lines.append(f"- **MITRE D3FEND**: {', '.join(sorted(all_d3fend)[:10])}")
        lines.append("")
        return "\n".join(lines)

    def _build_rules_section(self, template: Dict) -> str:
        """构建执行规则部分"""
        rules = [
            "## 执行规则 / Execution Rules",
            "",
            "1. **严格按 Workflow 步骤执行** — 不要跳过任何步骤",
            "2. **每步结果验证** — 使用 Verification 部分的方法确认",
            "3. **不假设结果** — 如果工具调用失败, 报告错误而非推测",
            "4. **结构化输出** — 按 Output Format 部分指定格式返回",
            "5. **安全约束** — 仅在合法授权范围内执行操作",
        ]

        if template.get("json_output"):
            rules.append("6. **JSON 输出** — 所有结果以 JSON 格式返回")

        if template.get("chinese_emphasis"):
            rules.append("7. **中文优先** — 分析和建议以中文呈现")

        return "\n".join(rules)

    def _build_output_section(self, template: Dict) -> str:
        """构建输出格式部分"""
        fmt = self.config.output_format

        if fmt == "json":
            return (
                "## 输出格式 / Output Format\n\n"
                "以 JSON 格式返回结果:\n"
                "```json\n"
                "{\n"
                '  "skill": "<skill_name>",\n'
                '  "status": "completed|failed|partial",\n'
                '  "findings": [],\n'
                '  "recommendations": [],\n'
                '  "execution_summary": "<brief summary>"\n'
                "}\n"
                "```"
            )
        elif fmt == "yaml":
            return (
                "## 输出格式 / Output Format\n\n"
                "以 YAML 格式返回结果:\n"
                "```yaml\n"
                "skill: <skill_name>\n"
                "status: completed\n"
                "findings: []\n"
                "recommendations: []\n"
                "```"
            )
        else:
            return (
                "## 输出格式 / Output Format\n\n"
                "以 Markdown 格式返回, 包含以下部分:\n"
                "- **执行摘要**\n"
                "- **发现 (Findings)**\n"
                "- **建议 (Recommendations)**\n"
                "- **验证状态 (Verification Status)**"
            )

    def _extract_workflow(self, content: str) -> str:
        """从技能内容中提取 Workflow 部分"""
        lines = content.split("\n")
        in_workflow = False
        workflow_lines = []

        for line in lines:
            if "## " in line and ("Workflow" in line or "工作流程" in line):
                in_workflow = True
                continue
            if in_workflow and "## " in line and "Workflow" not in line and "工作流程" not in line:
                break
            if in_workflow:
                workflow_lines.append(line)

        return "\n".join(workflow_lines[:50]) if workflow_lines else ""

    def build_trae_prompt(
        self, metas: List[SkillMetadata], contents: Dict[str, str]
    ) -> str:
        """为 Trae IDE 构建专用 Prompt"""
        self.config.platform = "trae"
        self.config.language = "zh-CN"
        self.config.output_format = "markdown"
        return self.build_system_prompt(metas, contents)

    def build_deepseek_v4_prompt(
        self,
        metas: List[SkillMetadata],
        contents: Dict[str, str],
        json_output: bool = True,
    ) -> str:
        """为 DeepSeek V4 构建专用 Prompt (JSON 输出 + Function Calling)"""
        self.config.platform = "deepseek-v4"
        self.config.output_format = "json" if json_output else "markdown"
        self.config.include_tool_definitions = True
        return self.build_system_prompt(metas, contents)

    def build_flocks_prompt(
        self, metas: List[SkillMetadata], contents: Dict[str, str]
    ) -> str:
        """为 Flocks 构建专用 Prompt"""
        self.config.platform = "flocks"
        self.config.output_format = "yaml"
        return self.build_system_prompt(metas, contents)
