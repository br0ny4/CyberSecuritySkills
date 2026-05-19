# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-pre] — 2026-05-19

### Project Initiation
- 深度分析两源仓库: Hi-FullHouse/CyberSecurity-Skills (195技能, 39领域) 与 mukul975/Anthropic-Cybersecurity-Skills (754技能, 26领域)
- 设计 41领域 × 4象限 技能覆盖全景
- 制定 4阶段15里程碑 长周期迭代计划

### Added
- **统一 Schema**: `unified-skill.schema.json` — 融合 agentskills.io 标准 + 国内Agent平台规范
- **适配器抽象基类**: `adapters/base/adapter_base.py` — 6个平台适配器的统一接口契约
- **TraeAdapter**: `adapters/trae/trae_adapter.py` — 字节跳动 Trae IDE 原生适配
- **FlocksAdapter**: `adapters/flocks/flocks_adapter.py` — 微步 Flocks 框架原生适配
- **ClaudeCodeAdapter**: `adapters/claude_code/claude_code_adapter.py` — Anthropic Claude Code 适配
- **CursorAdapter**: `adapters/cursor/cursor_adapter.py` — Anysphere Cursor IDE 适配
- **DeepSeekV4Adapter**: `adapters/deepseek_v4/deepseek_adapter.py` — DeepSeek V4 API 专用适配
- **DeepSeekSkillOptimizer**: `adapters/deepseek_v4/optimizer.py` — V4 性能优化器 (Token管理、重试、缓存、压缩)
- **CAUI 统一接口**: `integration/unified_interface.py` — Cross-Agent Unified Interface + AgentRegistry

### Documentation
- `README.md` — 项目总览 + 41领域全景 + 快速开始
- `PROJECT_PLAN.md` — 项目总体规划与里程碑
- `TODO.md` — 4阶段15里程碑详细迭代计划
- `docs/COMPLIANCE_REPORT.md` — 合规性审查与生态适配清单

---

## [Unreleased]

### Planned for v1.0.0
- 全量技能标准化整理 (800+ 技能, 统一格式)
- 统一索引生成器 (index_generator.py)
- 技能迁移工具 (migration_tools.py)
- 自动化测试套件 (test_adapters.py, test_integration.py, test_deepseek_optimizer.py, test_compliance.py)
- 合规性自动检查 (compliance_checker.py)
- GitHub Actions CI/CD
- CONTRIBUTING.md / CODE_OF_CONDUCT.md / NOTICE

### Planned for v1.1.0
- GitHub Copilot 适配器
- OpenAI Codex CLI 适配器
- Gemini CLI 适配器
- 50+ 新技能
- ATT&CK v19 映射更新

### Planned for v1.2.0
- Web UI 技能浏览器
- CLI 工具 (cs-skills)
- VS Code 扩展
- 100+ 新技能

### Planned for v2.0.0
- MCP Server 实现
- 技能市场 (Skill Marketplace)
- AI 自适应技能推荐
- 企业版功能
