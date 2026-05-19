# 📋 全门类网络安全AI技能整合项目 — 长周期迭代计划

> **版本**: v1.0.0-pre  
> **开始日期**: 2026-05-19  
> **预计总周期**: 6个月 (2026年5月 → 2026年11月)  
> **迭代模式**: 4阶段 × 15里程碑, 每阶段2-6周

---

## 总览

| 阶段 | 时间窗口 | 核心目标 | 里程碑数 |
|------|----------|----------|----------|
| **Phase 1: 基建** | Week 1-2 | 统一Schema + 全量技能标准化整理 | M1-M3 |
| **Phase 2: 适配** | Week 3-6 | 平台适配器开发 + 接口体系 | M4-M8 |
| **Phase 3: 优化** | Week 7-10 | DeepSeek V4专项优化 + 完备性验证 | M9-M12 |
| **Phase 4: 发布** | Week 11-16 | 合规打磨 + 生态适配 + 官方推荐 | M13-M15 |

---

## Phase 1: 基础设施与标准化 (Week 1-2) 🏗️

### M1: 仓库搭建与项目初始化 [P0] 
**目标**: 完成项目骨架搭建、源仓库深度分析

- [x] **分析 Hi-FullHouse/CyberSecurity-Skills (195技能/39领域)**
  - [x] 解析 index.json 结构、Schema规范
  - [x] 分析 skill_query.py 查询API设计
  - [x] 提取 agent-manifest.json 集成机制
  - [x] 统计中英文技能覆盖差异

- [x] **分析 mukul975/Anthropic-Cybersecurity-Skills (754技能/26领域)**
  - [x] 解析 agentskills.io 标准 SKILL.md 格式
  - [x] 分析 MITRE ATT&CK / NIST CSF / ATLAS / D3FEND / AI RMF 五重框架映射
  - [x] 评估渐进式发现机制 (~30 tokens/skill frontmatter扫描)
  - [x] 分析 .claude-plugin 目录结构和集成方式

- [x] **初始化项目仓库**
  - [x] 创建标准Python包结构
  - [x] 建立 schema/ adapters/ integration/ scripts/ tests/ docs/ 目录
  - [x] 编写 README.md 项目总览

- [ ] 编写 CONTRIBUTING.md 与 CODE_OF_CONDUCT.md
- [ ] 配置 GitHub Actions CI/CD (.github/workflows/ci.yml)
- [ ] 设置 pre-commit hooks (yaml lint, json schema validate, markdown lint)

**预计产出**: 完整的项目骨架 + 源仓库分析报告  
**责任人**: 项目架构师  
**预计工时**: 3天

---

### M2: 统一Schema设计与索引系统 [P0] 
**目标**: 融合两源仓库格式规范，定义跨平台统一技能Schema

- [x] **设计 unified-skill.schema.json**
  - [x] 合并 agentskills.io 字段 + Hi-FullHouse 中文字段
  - [x] 支持 7 重框架映射 (ATT&CK, NIST CSF, ATLAS, D3FEND, AI RMF, 等保2.0, ISO 27001)
  - [x] 添加 AI Agent 优化字段 (estimated_tokens, execution_time, platforms)
  - [x] 中英双语字段双轨 (name_cn, category_cn, difficulty_cn, tags_cn)

- [ ] **设计 agent-manifest.schema.json**
  - [ ] 定义 Agent 平台注册格式
  - [ ] 支持 capabilities 声明 (list/search/execute/validate)
  - [ ] 多平台标识 (trae, flocks, claude-code, cursor, deepseek-v4)

- [ ] **构建跨框架映射表 (crosswalk.json)**
  - [ ] ATT&CK v18 ↔ NIST CSF 2.0 双向映射
  - [ ] ATT&CK v18 ↔ ATLAS v5.4 A/ML对照
  - [ ] ATT&CK v18 ↔ D3FEND v1.3 攻防映射
  - [ ] 等保2.0 ↔ ISO 27001:2022 Annex A

- [ ] **编写 index_generator.py — 统一索引生成器**
  - [ ] 双源仓库增量合并 (去重逻辑)
  - [ ] 自动技能文件扫描与校验
  - [ ] 输出统一 index.json (按41领域分组)
  - [ ] 差异化报告 (A有B无 / B有A无 / 重复)

- [ ] 编写 migration_tools.py — 技能格式迁移工具
- [ ] 编写 5 个示例技能文件 (每领域1个，验证Schema)

**预计产出**: 统一Schema v1.0.0 + 索引生成器  
**责任人**: 标准化工程师  
**预计工时**: 4天

---

### M3: 全量技能标准化整理 [P0] 
**目标**: 完成全部900+技能的格式统一与索引

- [ ] 迁移 Hi-FullHouse 源 (195技能 → 统一格式)
  - [ ] 添加 YAML frontmatter 缺失字段
  - [ ] 补充 MITRE ATT&CK 映射
  - [ ] 统一 Section 标题 (中英双语)
  - [ ] 补充 estimated_tokens / execution_time / requires_tools

- [ ] 迁移 Anthropic Cybersecurity Skills 源 (754技能 → 统一格式)
  - [ ] 添加中文字段 (name_cn, category_cn, difficulty_cn, tags_cn)
  - [ ] 补充 等保2.0 / ISO 27001 映射
  - [ ] 统一 Section 结构

- [ ] 去重与冲突解决
  - [ ] 基于 name 字段精确去重
  - [ ] 基于描述语义相似度 (>85%) 人工审核
  - [ ] 冲突字段优先级规则 (A源中文字段优先, B源框架映射优先)

- [ ] 生成统一 index.json (预计 800-850 去重后技能)
- [ ] 生成 skills-inventory.csv (全量技能清单)
- [ ] 运行 `python skill_query.py validate` 全量验证

**预计产出**: 统一索引 v1.0.0 (800+ 技能)  
**责任人**: 数据工程师 + 安全研究员  
**预计工时**: 5天 (含人工审核)

---

## Phase 2: 平台适配开发 (Week 3-6) 🔌

### M4: 适配器抽象基类 [P0] 
**目标**: 定义统一的适配器接口契约

- [x] **实现 adapter_base.py**
  - [x] SkillMetadata 数据类 (映射 unified-skill.schema.json)
  - [x] SkillExecutionContext 执行上下文
  - [x] SkillExecutionResult 执行结果
  - [x] SkillSearchQuery 搜索查询
  - [x] BaseSkillAdapter 抽象基类 (6个抽象方法)
  - [x] SkillExecutionMode 枚举 (sync/async/stream/batch)
  - [x] SkillStatus 枚举 (pending/running/completed/failed/cancelled/timeout)

- [ ] 单元测试: test_adapter_base.py (覆盖率 >90%)
- [ ] 接口文档: docs/ADAPTER_INTERFACE.md

**预计产出**: 适配器接口契约 v1.0.0  
**责任人**: 平台工程师  
**预计工时**: 2天

---

### M5: Trae IDE 适配器 [P0] 
**目标**: 原生支持字节跳动 Trae IDE 技能调用

- [x] 实现 TraeAdapter (继承 BaseSkillAdapter)
- [x] .trae/skills/ 目录自动生成
- [x] agent-manifest.json 自动生成
- [ ] SKILL.md 自动同步到 .trae/skills/
- [ ] Trae MCP 集成配置生成
- [ ] 中文关键词搜索优化 (jieba分词)
- [ ] 集成测试: 在 Trae IDE 中验证技能加载

**预计产出**: TraeAdapter v1.0.0  
**责任人**: IDE集成工程师  
**预计工时**: 3天

---

### M6: Flocks 适配器 [P0] 
**目标**: 原生支持微步 Flocks AI Agent 框架

- [x] 实现 FlocksAdapter (继承 BaseSkillAdapter)
- [x] .flocks.yaml 配置文件生成
- [x] 技能 YAML 格式转换 (SKILL.md → flocks-skill.yaml)
- [x] 批量编排支持 (最多10技能并行)
- [ ] safeskill.cn 安全检测前兼容
- [ ] Flocks MCP 协议集成
- [ ] 集成测试: 在 Flocks 框架中验证

**预计产出**: FlocksAdapter v1.0.0  
**责任人**: 框架集成工程师  
**预计工时**: 3天

---

### M7: Claude Code / Cursor 适配器 [P0] 
**目标**: 原生支持 Claude Code 和 Cursor IDE

- [x] 实现 ClaudeCodeAdapter
- [x] .claude-plugin/plugin.json 配置生成
- [x] 实现 CursorAdapter
- [x] .cursor/skills.json 注册清单
- [ ] Claude Code `npx skills add` 一键安装验证
- [ ] Cursor `.cursorrules` 配置模板
- [ ] 集成测试: 双平台端到端验证

**预计产出**: ClaudeCodeAdapter + CursorAdapter v1.0.0  
**责任人**: IDE集成工程师  
**预计工时**: 3天

---

### M8: 统一接口层 CAUI [P0] 
**目标**: 构建跨Agent统一接口体系

- [x] 实现 UnifiedSkillInterface (统一入口)
- [x] 实现 AgentRegistry (Agent注册与发现)
- [x] 自动平台检测 (auto_detect)
- [x] 技能链顺序执行 (execute_chain)
- [ ] 实现 SkillRouter (智能路由引擎)
- [ ] 实现 PromptBuilder (跨平台Prompt构建器)
- [ ] 集成测试: 5平台统一接口端到端验证
- [ ] 性能基准测试 (benchmark.py)

**预计产出**: CAUI v1.0.0 (Cross-Agent Unified Interface)  
**责任人**: 系统架构师  
**预计工时**: 4天

---

## Phase 3: DeepSeek V4 专项优化 (Week 7-10) 🚀

### M9: DeepSeek V4 适配器 [P0] 
**目标**: 针对 DeepSeek V4 Pro/Flash 的专用适配

- [x] 实现 DeepSeekV4Adapter
- [x] OpenAI 兼容 API 调用
- [x] Function Calling 工具定义自动生成
- [ ] 1M Context 窗口利用策略
  - [ ] 全量技能预加载 (Pro版: 754技能frontmatter ~22K tokens)
  - [ ] 上下文窗口动态管理
- [ ] 流式输出支持 (SSE)
- [ ] 集成测试: V4 Pro + V4 Flash 端到端

**预计产出**: DeepSeekV4Adapter v1.0.0  
**责任人**: AI工程师  
**预计工时**: 4天

---

### M10: DeepSeek V4 性能优化器 [P0] 
**目标**: 专项性能优化 — Token管理、稳定性、成本控制

- [x] 实现 DeepSeekSkillOptimizer
- [x] Token 预算管理 (TokenBudget)
- [x] 渐进式加载策略 (3波: top-5完整, next-7压缩, 剩余frontmatter)
- [x] 技能内容压缩 (4策略: accuracy/speed/cost/balanced)
- [x] Function Calling 去重
- [x] 指数退避重试机制
- [x] LRU 缓存层
- [ ] 本地部署支持 (vLLM/TGI/llama.cpp)
- [ ] Flash版极致压缩 (cost模式: -60% tokens)
- [ ] 性能基准测试
  - [ ] 754技能批量扫描耗时 (目标: <5s)
  - [ ] 单技能执行延迟 (目标: <3s average)
  - [ ] Token节省率 (目标: >40% vs 无优化)
- [ ] 稳定性压测 (1000次连续调用)

**预计产出**: DeepSeekOptimizer v1.0.0 + Benchmark Report  
**责任人**: AI工程师 + 性能工程师  
**预计工时**: 5天

---

### M11: 功能完备性验证 [P1] 
**目标**: 全量技能功能验证 + 跨平台兼容性测试

- [ ] 编写自动化测试套件
  - [ ] test_adapters.py — 5平台适配器单元测试
  - [ ] test_integration.py — CAUI 接口测试
  - [ ] test_deepseek_optimizer.py — 优化器测试
  - [ ] test_compliance.py — 合规性检查

- [ ] 跨平台兼容性矩阵验证
  | 平台 | 技能搜索 | 技能加载 | 技能执行 | 错误处理 |
  |------|----------|----------|----------|----------|
  | Trae | □ | □ | □ | □ |
  | Flocks | □ | □ | □ | □ |
  | Claude Code | □ | □ | □ | □ |
  | Cursor | □ | □ | □ | □ |
  | DeepSeek V4 | □ | □ | □ | □ |

- [ ] 边界条件测试
  - [ ] 空技能仓库
  - [ ] 技能文件损坏
  - [ ] 超大技能内容 (>5000 tokens)
  - [ ] API超时 / 限流 / 500错误

**预计产出**: 测试报告 + 兼容性矩阵  
**责任人**: QA工程师  
**预计工时**: 4天

---

### M12: 安全与合规打磨 [P1] 
**目标**: 完成合规性审查、安全审计

- [ ] 编写合规性自动检查工具 (compliance_checker.py)
  - [ ] Schema 合法性验证
  - [ ] 必填字段完整性检查
  - [ ] 框架映射一致性检查
  - [ ] 许可证兼容性检查 (MIT + Apache-2.0)

- [ ] 安全审计
  - [ ] 技能文件注入风险检查
  - [ ] API Key 泄露检查
  - [ ] 命令注入风险审查
  - [ ] 依赖库漏洞扫描 (pip-audit)

- [ ] 合规文档编写
  - [ ] COMPLIANCE_REPORT.md — 合规性报告
  - [ ] SECURITY.md — 安全策略
  - [ ] 数据隐私影响评估 (DPIA 简版)

- [ ] 许可证合规
  - [ ] 确认 MIT (A源) + Apache-2.0 (B源) 兼容性
  - [ ] 第三方依赖许可证审核

**预计产出**: Compliance Report v1.0 + Security Audit Report  
**责任人**: 安全合规工程师  
**预计工时**: 3天

---

## Phase 4: 发布与生态推广 (Week 11-16) 🚀

### M13: 版本发布 v1.0.0 [P0] 
**目标**: 首个正式版本发布

- [ ] 版本冻结与代码审查
- [ ] CHANGELOG.md 编写 (按 Semantic Versioning)
- [ ] Git Tag: v1.0.0
- [ ] GitHub Release 创建
  - [ ] Release Notes
  - [ ] 预编译 artifact (index.json, schema JSON, 适配器 wheel包)
- [ ] PyPI 发布 (pip install cybersecurity-ai-skills-unified)
- [ ] 文档站部署 (GitHub Pages)
- [ ] 演示视频 / 快速入门指南

**预计产出**: GitHub Release v1.0.0  
**责任人**: 发布经理  
**预计工时**: 2天

---

### M14: 生态适配调试 [P1] 
**目标**: 推动项目入选主流 Agent 官方推荐列表

- [ ] **Flocks 官方推荐列表入选**
  - [ ] 符合 Flocks Skill 开发规范
  - [ ] 通过 safeskill.cn 安全检测
  - [ ] 提交 Flocks skill registry PR
  - [ ] 编写 Flocks 集成文档

- [ ] **Trae Skill Marketplace 提交**
  - [ ] 符合 Trae Skill 规范 (15项检查清单)
  - [ ] 创建 Trae Skill 配置 (trae-skill.json)
  - [ ] 提交 Marketplace PR

- [ ] **agentskills.io 注册**
  - [ ] 注册到 agentskills.io 公开目录
  - [ ] 提供 npm 安装方式 (`npx skills add`)

- [ ] **Awesome List 收录**
  - [ ] awesome-cybersecurity
  - [ ] awesome-ai-agents
  - [ ] awesome-security

- [ ] 社区推广
  - [ ] 知乎/公众号技术文章
  - [ ] GitHub Discussion 活跃维护
  - [ ] 加入 Flocks 社区 / Trae 开发者社区

**预计产出**: 5+ 生态平台收录  
**责任人**: 社区运营 + 开发者关系  
**预计工时**: 持续进行

---

### M15: 持续迭代规划 v1.1 → v2.0 [P2] 
**目标**: 制定后续3个版本的路线图

#### v1.1.0 (预计 2026-07)
- [ ] 支持 GitHub Copilot 适配器
- [ ] 支持 OpenAI Codex CLI 适配器
- [ ] 支持 Gemini CLI 适配器
- [ ] 新增 50+ 技能 (社区贡献)
- [ ] ATT&CK v19 映射更新

#### v1.2.0 (预计 2026-08)
- [ ] Web UI 技能浏览器 (React)
- [ ] 技能执行可视化 (实时进度 + 结果展示)
- [ ] CLI 工具 (`cs-skills search/list/execute`)
- [ ] VS Code 扩展
- [ ] 新增 100+ 技能
- [ ] 国际化 (英文为主, 中文为辅 → 中英双语完整)

#### v2.0.0 (预计 2026-11)
- [ ] MCP Server 实现 (标准 Model Context Protocol)
- [ ] 技能市场 (Skill Marketplace) — 社区贡献 + 审核
- [ ] 技能编排引擎 (DAG 工作流)
- [ ] AI 自适应技能推荐 (基于历史执行日志)
- [ ] 企业版功能 (RBAC, 审计日志, SSO)
- [ ] 目标: 2000+ 技能, 10+ 平台, 5000+ GitHub Stars

**预计产出**: Roadmap v1.1-v2.0  
**责任人**: 产品经理  
**预计工时**: 1天

---

## 优先级说明

| 优先级 | 含义 | 典型任务 |
|--------|------|----------|
| **P0** | 必须完成, 阻塞发布 | 统一Schema, 适配器, 索引生成 |
| **P1** | 高优先级, 影响质量 | 测试, 合规, 生态适配 |
| **P2** | 期望完成, 可延后 | 后续版本规划, 社区推广 |

---

## 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| 两源仓库技能去重准确率不足 | 高 | 中 | 人工审核 + 语义去重算法 |
| Flocks/Trae API 变化 | 中 | 低 | 适配器层隔离, 关注上游更新 |
| DeepSeek V4 API 不稳定 | 中 | 中 | 重试机制 + 降级策略 |
| 社区贡献质量参差 | 低 | 高 | CI自动验证 + PR Review |
| 许可证兼容性问题 | 高 | 低 | 提前法律审查 |

---

> **最后更新**: 2026-05-19  
> **下次评审**: 每2周一次 (周一站会)
