# 📋 CyberSecuritySkills — 长周期迭代计划

> **版本**: v1.0.0-pre · **开始日期**: 2026-05-19  
> **迭代模式**: 4阶段 × 18里程碑, 每阶段2-6周

---

## 总览

| 阶段 | 时间窗口 | 核心目标 | 里程碑 | 新增源 |
|------|----------|----------|--------|--------|
| **Phase 1: 基建** | Week 1-2 | 统一Schema + 全量技能标准化 | M1-M3 | 源1+2 |
| **Phase 2: 适配** | Week 3-6 | 平台适配器 + 接口体系 | M4-M8 | — |
| **Phase 3: 拓展** | Week 7-10 | 外部源接入 + DeepSeek优化 + 完备性验证 | M9-M14 | 源3+4+5 |
| **Phase 4: 发布** | Week 11-16 | 合规打磨 + 生态适配 + 官方推荐 | M15-M18 | 源6+7 (持续) |

---

## Phase 1: 基础设施与标准化 (Week 1-2) 🏗️

### M1: 仓库搭建与项目初始化 [P0] ✅
- [x] 分析 Hi-FullHouse/CyberSecurity-Skills (195技能/39领域)
- [x] 分析 mukul975/Anthropic-Cybersecurity-Skills (754技能/26领域)
- [x] 初始化项目仓库结构
- [x] 编写 README.md 项目总览

### M2: 统一Schema设计与索引系统 [P0] ✅
- [x] 设计 unified-skill.schema.json (7重框架映射)
- [x] 设计 agent-manifest.schema.json
- [x] 构建 crosswalk.json 跨框架映射表
- [ ] 实现 index_generator.py 统一索引生成器 (框架已就绪, 待双源数据填充)

### M3: 全量技能标准化整理 [P0] 🔄
- [ ] 源1迁移: Hi-FullHouse → 统一格式 (195技能)
- [ ] 源2迁移: Anthropic Cybersecurity → 统一格式 (754技能)
- [ ] 去重与冲突解决
- [ ] 生成统一 index.json (预计 800+ 去重后技能)

---

## Phase 2: 平台适配开发 (Week 3-6) 🔌

### M4: 适配器抽象基类 [P0] ✅
- [x] adapter_base.py 接口契约
- [x] SkillMetadata / SkillExecutionContext / SkillExecutionResult
- [x] SkillSearchQuery / SkillExecutionMode / SkillStatus

### M5: Trae / Flocks 适配器 [P0] ✅
- [x] TraeAdapter (.trae/skills/ + agent-manifest.json)
- [x] FlocksAdapter (.flocks.yaml + YAML技能转换 + 批量编排)

### M6: Claude Code / Cursor 适配器 [P0] ✅
- [x] ClaudeCodeAdapter (.claude-plugin/plugin.json)
- [x] CursorAdapter (.cursor/skills.json)

### M7: DeepSeek V4 适配器 [P0] ✅
- [x] DeepSeekV4Adapter (API + Function Calling + 流式)
- [x] DeepSeekSkillOptimizer (Token管理/压缩/重试/缓存)

### M8: CAUI统一接口层 [P0] ✅
- [x] UnifiedSkillInterface (统一入口 + 自动平台检测)
- [x] AgentRegistry (多Agent注册发现)
- [x] SkillRouter (智能路由引擎)
- [x] PromptBuilder (跨平台Prompt构建器)

---

## Phase 3: 外部源拓展与深度优化 (Week 7-10) 🚀

### M9: 接入 addyosmani/agent-skills [P0] ✅
**源**: `github.com/addyosmani/agent-skills` (42K⭐, MIT)
- [x] 提取 security-and-hardening/SKILL.md (OWASP Top 10 全覆盖)
- [x] 提取 security-auditor agent persona
- [x] 提取 security-checklist.md 参考清单
- [x] 纳入 SOURCE_CATALOG.md
- [ ] 将技能转化为统一格式并编入索引

**技能化**: Three-Tier Boundary System → 独立安全技能模板

### M10: 接入 vercel-labs/deepsec [P0] ✅
**源**: `github.com/vercel-labs/deepsec` (Apache-2.0)
- [x] 提取 Agent 漏洞扫描管线方法论
- [x] 提取 Regex Matcher 模式库参考
- [x] 纳入 SOURCE_CATALOG.md
- [ ] 抽象为 automated-vuln-scanning 技能
- [ ] 构建 scan_runner.py 调度脚本

### M11: 接入 ruvnet/ruflo [P0] ✅
**源**: `github.com/ruvnet/ruflo` (49K⭐, MIT)
- [x] 提取 ruflo-security-audit 插件能力
- [x] 提取 ruflo-aidefence 插件能力 (Prompt注入/PII)
- [x] 纳入 SOURCE_CATALOG.md
- [ ] 抽象为 AI安全防护 + CVE扫描技能模板

### M12: 性能基准测试与优化 [P1]
- [ ] DeepSeek V4 1M Context 满载实测
- [ ] 754技能批量扫描耗时优化 (目标: <3s)
- [ ] Token 节省率验证 (目标: >40% vs 无优化)
- [ ] 稳定性压测 (1000次连续调用)

### M13: 功能完备性验证 [P1]
- [x] 28项单元测试全通过 ✅
- [ ] 跨平台兼容性矩阵 (Trae/Flocks/Claude/Cursor/DeepSeek V4)
- [ ] 边界条件测试 (空仓库/文件损坏/超大技能/API超时)

### M14: SkillsMP + SkillStore 持续发现 [P2]
- [ ] 编写 sync_skillsmp.py 周期同步脚本
- [ ] 编写 sync_skillstore.py 安全审核技能同步
- [ ] 首次同步 top-50 安全技能
- [ ] 建立月度同步机制

---

## Phase 4: 发布与生态推广 (Week 11-16) 🚀

### M15: 版本发布 v1.0.0 [P0]
- [ ] 版本冻结 + 代码审查
- [ ] CHANGELOG.md 最终版
- [ ] GitHub Release v1.0.0
- [ ] PyPI 发布

### M16: 生态适配调试 [P1]
- [ ] Flocks 官方推荐列表 PR 提交
- [ ] Trae Skill Marketplace 提交
- [ ] agentskills.io 注册
- [ ] Awesome List 收录 (awesome-cybersecurity / awesome-ai-agents)

### M17: 合规与安全打磨 [P1]
- [x] 合规性自动检查框架 (compliance_checker.py)
- [x] 合规性审查报告 (COMPLIANCE_REPORT.md)
- [ ] 安全审计 (pip-audit / bandit)
- [ ] safeskill.cn 安全检测提交
- [ ] NOTICE 文件 (Apache-2.0合规)

### M18: v1.1 → v2.0 路线图 [P2]

#### v1.1.0 (预计 2026-07)
- [ ] 接入 3-5 个社区推荐安全技能仓库
- [ ] SkillsMP 自动同步机制上线
- [ ] ATT&CK v19 映射更新
- [ ] GitHub Copilot / Codex CLI / Gemini CLI 适配器

#### v1.2.0 (预计 2026-08)
- [ ] Web UI 技能浏览器
- [ ] CLI 工具 (cs-skills)
- [ ] VS Code 扩展
- [ ] 100+ 新技能

#### v2.0.0 (预计 2026-11)
- [ ] MCP Server 实现
- [ ] 技能市场 (Skill Marketplace)
- [ ] AI 自适应技能推荐
- [ ] 目标: 2000+ 技能, 10+ 平台, 5000+ Stars

---

## 外部仓库接入路线图

| 批次 | 时间 | 仓库 | 技能数 | 接入状态 |
|------|------|------|--------|----------|
| **Batch 1** | Week 1 | Hi-FullHouse + Anthropic CS | 949 (原始) | ✅ 核心融合 |
| **Batch 2** | Week 7 | addyosmani/agent-skills | +1 高质量安全技能 | ✅ 已分析 |
| **Batch 2** | Week 7 | vercel-labs/deepsec | +1 漏洞扫描管线 | ✅ 已分析 |
| **Batch 2** | Week 7 | ruvnet/ruflo | +2 安全插件 | ✅ 已分析 |
| **Batch 3** | Week 10 | SkillsMP精选 | +50 (top安全) | ⏳ 待同步 |
| **Batch 3** | Week 10 | SkillStore审核 | +若干 (安全验证) | ⏳ 待同步 |
| **Batch 4** | Month 3 | browserbase/skills | +安全测试技能 | 📋 Watchlist |
| **Batch 4** | Month 3 | 其他社区推荐 | 待定 | 📋 Watchlist |

---

## 优先级说明

| 优先级 | 含义 | 典型任务 |
|--------|------|----------|
| **P0** | 必须完成, 阻塞发布 | 统一Schema, 适配器, 源接入 |
| **P1** | 高优先级, 影响质量 | 测试, 合规, 生态适配 |
| **P2** | 期望完成, 可延后 | 后续版本规划, 社区推广 |

---

> **最后更新**: 2026-05-19 · **下次评审**: 每2周一次
