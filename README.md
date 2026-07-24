# CyberSecuritySkills — 全门类网络安全 AI 技能统一集成平台

> **The Unified Cross-Agent Cybersecurity Skill Framework for AI Agents**
>
> 融合 7 大源仓库 | 41+ 安全领域 | 800+ AI 可调用技能 | 8 重框架映射 | 11+ MCP 工具集成 | 6+ AI Agent 平台原生支持 | CS4 安全扫描引擎

---

## 项目概述

本项目整合 GitHub 上高质量网络安全 AI 技能仓库，构建一套**全门类、跨平台、标准化**的网络安全 AI 技能统一集成平台。项目定位是 **"AI Agent 安全技能标准制定者"**，占据 AI Agent + 网络安全 + MCP 协议三大技术浪潮交汇点。

### 五大核心目标

| # | 目标 | 交付物 |
|---|------|--------|
| 1 | 全量技能标准化整理 | 统一 Schema + 全门类技能目录 + 索引系统 |
| 2 | 多平台适配开发 | Trae / Flocks / Claude Code / Cursor / DeepSeek V4 适配器 |
| 3 | 统一接口体系 | Cross-Agent Unified Interface (CAUI) |
| 4 | 技能安全可信体系 | CS4 安全扫描引擎 + 技能信任分级 |
| 5 | 长周期迭代 + 生态推广 | 4 阶段 18 周迭代计划 + Flocks / Trae / Agensi 官方推荐 |

---

## 外部源仓库 (7 库融合)

| # | 仓库 | Stars | 技能贡献 | 许可证 |
|---|------|-------|----------|--------|
| 1 | [Hi-FullHouse/CyberSecurity-Skills](https://github.com/Hi-FullHouse/CyberSecurity-Skills) | - | 195 技能 / 39 领域 | MIT |
| 2 | [mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills) | - | 754 技能 / 26 领域 / 5 框架映射 | Apache-2.0 |
| 3 | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 42K+ | +1 安全硬核技能 / 安全审计 Agent | MIT |
| 4 | [vercel-labs/deepsec](https://github.com/vercel-labs/deepsec) | 新项目 | +1 Agent 漏洞扫描管线 | Apache-2.0 |
| 5 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 49K+ | +2 安全插件 (CVE + AI 防御) | MIT |
| 6 | [SkillsMP.com](https://skillsmp.com/categories/security) | 38K 安全技能 | 持续发现新技能 (聚合平台) | 各仓库 |
| 7 | [SkillStore.io](https://skillstore.io/zh-hans) | 安全审核 | 安全审查通过的技能 (可信源) | 各仓库 |

> 详细源分析：[docs/SOURCE_CATALOG.md](docs/SOURCE_CATALOG.md) | 版权声明：[NOTICE.md](NOTICE.md)

---

## 技能覆盖全景 (41 大领域)

### 红队/攻击面 (14 领域) · 蓝队/防御面 (14 领域)

| ID | 领域 | 技能数 | 对标框架 |
|----|------|--------|----------|
| 01 | 信息搜集 Reconnaissance | 25+ | PTES / ATT&CK TA0043 |
| 02 | 漏洞扫描 Vulnerability Scanning | 20+ | PTES / ATT&CK TA0043 |
| 03 | 漏洞利用 Exploitation | 30+ | PTES / ATT&CK TA0002 |
| 04 | 权限提升 Privilege Escalation | 15+ | ATT&CK TA0004 |
| 05 | 后渗透 Post-Exploitation | 15+ | PTES |
| 06 | 横向移动 Lateral Movement | 15+ | ATT&CK TA0008 |
| 07 | 持久化 Persistence | 20+ | ATT&CK TA0003 |
| 08 | 痕迹清除 Covering Tracks | 10+ | ATT&CK TA0005 |
| 09 | 社会工程学 Social Engineering | 20+ | ATT&CK TA0001 |
| 10 | 无线安全 Wireless Security | 5+ | PTES |
| 11 | 移动安全 Mobile Security | 15+ | OWASP MSTG |
| 12 | 逆向工程 Reverse Engineering | 18+ | ATT&CK TA0002 |
| 13 | 渗透测试 Pentesting | 23+ | PTES / OWASP |
| 14 | 红蓝对抗 Red/Blue Team | 30+ | ATT&CK Enterprise |
| 15 | 威胁检测与狩猎 Threat Hunting | 55+ | ATT&CK / D3FEND |
| 16 | 威胁情报 Threat Intelligence | 55+ | STIX/TAXII |
| 17 | 应急响应 Incident Response | 32+ | NIST SP 800-61 |
| 18 | 数字取证 Digital Forensics | 42+ | NIST SP 800-86 |
| 19 | SOC 运营 SOC Operations | 37+ | NIST CSF DE/RS |
| 20 | 端点安全 Endpoint Security | 21+ | D3FEND |
| 21 | 勒索软件防御 Ransomware Defense | 10+ | ATT&CK TA0040 |
| 22 | 恶意软件分析 Malware Analysis | 39+ | ATT&CK |
| 23 | 网络安全 Network Security | 40+ | D3FEND D3-NTA |
| 24 | 欺骗防御 Deception Technology | 2+ | D3FEND |
| 25 | 钓鱼防御 Phishing Defense | 16+ | ATT&CK T1566 |
| 26 | 报告撰写 Reporting | 5+ | PTES |
| 27 | 漏洞管理 Vulnerability Management | 31+ | NIST CSF ID.RA |
| 28 | 安全运营 Security Operations | 36+ | NIST CSF |

### 基础设施安全 (9 领域) · 新兴专项安全 (5 领域)

| ID | 领域 | 技能数 | 对标框架 |
|----|------|--------|----------|
| 29 | 云安全 Cloud Security | 68+ | CIS Benchmarks |
| 30 | 容器安全 Container Security | 34+ | CIS K8s Benchmarks |
| 31 | API 安全 API Security | 31+ | OWASP API Top 10 |
| 32 | 代码审计 Code Audit | 9+ | OWASP |
| 33 | 供应链安全 Supply Chain Security | 5+ | SLSA / SSDF |
| 34 | 操作系统安全 OS Security | 6+ | CIS Benchmarks |
| 35 | 身份访问管理 IAM | 39+ | NIST CSF PR.AA |
| 36 | 密码学与 PKI Cryptography & PKI | 17+ | NIST SP 800-175B |
| 37 | 零信任架构 Zero Trust | 16+ | CISA ZTMM |
| 38 | 大模型安全 LLM Security | 10+ | OWASP LLM Top 10 / MITRE ATLAS |
| 39 | 工控安全 ICS/OT Security | 34+ | IEC 62443 |
| 40 | 区块链/Web3 安全 Blockchain Security | 6+ | SCSVS |
| 41 | 物联网安全 IoT Security | 6+ | OWASP IoT Top 10 |

---

## 八重框架映射

| 框架 | 版本 | 覆盖 | 说明 |
|------|------|------|------|
| **MITRE ATT&CK** | v19.1 | 14/14 Tactics | 企业攻击矩阵全覆盖 |
| **NIST CSF 2.0** | 2.0 | 6/6 Functions | 网络安全框架 |
| **MITRE ATLAS** | v5.4 | 16/16 Tactics | AI 系统攻击矩阵 |
| **MITRE D3FEND** | v1.3 | 7/7 Categories | 防御对策知识库 |
| **MITRE F3 (Fight Fraud)** | v1.1 | 8/8 Tactics | **新增** — 金融反欺诈矩阵, 94 技能映射 |
| **NIST AI RMF** | 1.0 | 4/4 Functions | AI 风险管理框架 |
| **等级保护 2.0** | GB/T 22239 | 全类别 | 中国网络安全合规 |
| **ISO 27001:2022** | 2022 | Annex A | 国际信息安全管理 |

> 框架映射表：[schema/crosswalk.json](schema/crosswalk.json)

---

## CS4 安全扫描引擎

**CyberSecuritySkills Safety Scan (CS4)** 是项目自研的零依赖技能安全扫描引擎，为所有 800+ 技能提供安全可信保障。

### 7 点安全扫描

| # | 扫描项 | 说明 |
|---|--------|------|
| 1 | **Prompt 注入检测** | 170+ 模式库, 覆盖中英文注入变体 |
| 2 | **危险命令模式** | `rm -rf`, `DROP TABLE`, `curl \| bash` 等 25+ 模式 |
| 3 | **硬编码密钥检测** | API Key, Token, 密码, AWS/GitHub 密钥 |
| 4 | **混淆代码检测** | Base64, Hex, ROT13 等编码识别 |
| 5 | **网络外连检测** | 可疑 URL, 隧道服务, Webhook 地址 |
| 6 | **OWASP LLM Top 10** | LLM01-LLM10 全量合规检查 |
| 7 | **技能信任分级** | Verified / Caution / Restricted 三级 |

### 技能信任分级

| 级别 | 图标 | 含义 |
|------|------|------|
| **Verified** | 🟢 | 通过全部 7 项扫描, 可安全使用 |
| **Caution** | 🟡 | 包含攻击性内容, 仅限授权场景使用 |
| **Restricted** | 🔴 | 发现高危风险, 需人工审核 |

### 使用方式

```bash
python scanners/cs4_scan.py --all                          # 扫描全量技能
python scanners/cs4_scan.py --file path/to/SKILL.md         # 单文件扫描
python scanners/cs4_scan.py --dir skills/exploitation/      # 目录扫描
python scanners/cs4_scan.py --all --output reports/report.json  # 生成报告
```

---

## 项目架构

```
CyberSecuritySkills/
├── README.md                          # 项目总览 (本文件)
├── PROJECT_PLAN.md                    # 项目总体规划
├── SKILLS_INVENTORY.md                # 全门类技能清单 (800+ 条目)
├── TODO.md                            # 迭代开发计划
├── CHANGELOG.md                       # 版本变更记录
├── NOTICE.md                          # 第三方版权声明
├── CONTRIBUTING.md                    # 参与贡献规范
├── CODE_OF_CONDUCT.md                 # 行为准则
├── LICENSE                            # MIT 许可证
│
├── docs/
│   ├── SOURCE_CATALOG.md              # 外部源仓库目录 (7 源分析)
│   ├── COMPLIANCE_REPORT.md           # 合规性审查与生态适配清单
│   ├── MCP_INTEGRATION.md             # MCP 工具集成完整指南
│   └── ITERATION_PLAN_V1.md           # v2.0.0 迭代更新方案
│
├── schema/
│   ├── unified-skill.schema.json      # 统一技能 Schema (8 重框架映射)
│   ├── agent-manifest.schema.json     # Agent 集成 Manifest Schema
│   └── crosswalk.json                 # 框架交叉映射表 (v19.1 + F3)
│
├── scanners/
│   ├── __init__.py                    # CS4 扫描引擎入口
│   └── cs4_scan.py                    # CS4 安全扫描核心引擎
│
├── adapters/
│   ├── base/adapter_base.py           # 适配器抽象基类
│   ├── trae/trae_adapter.py           # Trae IDE 适配器
│   ├── flocks/flocks_adapter.py       # Flocks 适配器 (YAML + 批量)
│   ├── claude_code/                   # Claude Code 适配器
│   ├── cursor/cursor_adapter.py       # Cursor IDE 适配器
│   └── deepseek_v4/                   # DeepSeek V4 适配器 + 优化器
│
├── integration/
│   ├── unified_interface.py           # CAUI 统一接口 + AgentRegistry
│   ├── skill_router.py                # 智能路由引擎
│   └── prompt_builder.py              # 跨平台 Prompt 构建器
│
├── mcp/
│   ├── mcp-registry.json              # MCP 工具注册清单
│   ├── configs/                       # MCP 安全配置模板
│   │   ├── nmap-mcp.json
│   │   ├── nmap-mcp-secure.json       # 安全增强版
│   │   ├── sqlmap-mcp-secure.json
│   │   ├── metasploit-mcp-secure.json
│   │   └── ...
│   └── scripts/
│       ├── ghidra_mcp_server.py
│       └── mcp_security_auditor.py    # OWASP MCP Top 10 审计
│
├── scripts/
│   ├── index_generator.py             # 统一索引生成器
│   ├── migration_tools.py             # 技能格式迁移工具
│   ├── compliance_checker.py          # 合规性自动检查
│   └── benchmark.py                   # 性能基准测试
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                     # CI: 测试 + CS4 扫描 + Lint
│   │   └── commitlint.yml             # Commit Message 校验
│   └── PULL_REQUEST_TEMPLATE.md       # PR 模板
│
├── .commitlintrc.json                 # Conventional Commits 配置
└── tests/
    └── test_integration.py            # 单元与集成测试
```

---

## 快速开始

### 环境要求

- Python 3.10+
- Git 2.30+
- (可选) Ollama 用于本地模型测试
- (可选) DeepSeek V4 API Key 用于 DeepSeek 适配器

### 安装

```bash
git clone https://github.com/br0ny4/CyberSecuritySkills.git
cd CyberSecuritySkills
pip install -r requirements.txt
```

### Claude Code

```bash
npx skills add br0ny4/CyberSecuritySkills
```

### Trae / Cursor

```json
{
  "skills": [{
    "name": "cybersecurity-unified",
    "path": "/path/to/CyberSecuritySkills",
    "manifest": "schema/agent-manifest.schema.json"
  }]
}
```

### Flocks

```bash
flocks skill install cybersecurity-unified --source local --path /path/to/CyberSecuritySkills
```

### DeepSeek V4 (API 直接调用)

```python
from adapters.deepseek_v4.deepseek_adapter import DeepSeekV4Adapter

adapter = DeepSeekV4Adapter(
    skill_repo_path="/path/to/CyberSecuritySkills",
    api_key="sk-xxx",
    model="deepseek-v4-flash"
)
result = adapter.execute_skill(
    skill_name="performing-memory-forensics-with-volatility3",
    context={"memory_dump": "/cases/case-001/memory.raw"}
)
```

### 技能安全扫描

```bash
python scanners/cs4_scan.py --all
```

---

## MCP 工具集成 (11+ 安全工具)

让 AI Agent 通过 MCP 协议直接操控 BurpSuite、IDA Pro、Ghidra 等安全工具。

| Tier | 工具 | MCP 仓库 | 安全配置 | 状态 |
|------|------|----------|----------|------|
| 🥇 | **IDA Pro** | [mrexodia/ida-pro-mcp](https://github.com/mrexodia/ida-pro-mcp) | ✅ | 生产级 |
| 🥇 | **BurpSuite** | [X3r0K/BurpSuite-MCP-Server](https://github.com/X3r0K/BurpSuite-MCP-Server) | ✅ | 1.4K+ |
| 🥇 | **Shodan** | [BurtTheCoder/Shodan-MCP](https://github.com/BurtTheCoder/Shodan-MCP) | ✅ | 已验证 |
| 🥈 | **VirusTotal** | 腾讯云 MCP 广场 | ✅ | 已验证 |
| 🥉 | **Ghidra / Nmap / Wireshark / Metasploit / Volatility3 / sqlmap / Binary Ninja** | 本项目封装 | ✅ 安全配置升级 | 配置模板 |

### MCP 安全纵深防御

所有 MCP 配置模板均已升级，新增安全层：
- **最小权限工具白名单**: 仅暴露技能需要的 MCP tool
- **输入参数沙箱校验**: 路径 / 命令 / 网络访问范围限制
- **操作审计日志**: 工具调用全链路追踪
- **OWASP MCP Top 10 合规**: 自动审计脚本

```bash
python mcp/scripts/mcp_security_auditor.py
```

完整 MCP 集成指南：[docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md)
MCP 注册清单：[mcp/mcp-registry.json](mcp/mcp-registry.json)

---

## 新增安全技能亮点 (v1.0.0-pre Iteration #3)

### 来自 addyosmani/agent-skills
- **OWASP Top 10 全防**: SQL 注入→参数化查询 / XSS→DOMPurify / 认证→bcrypt+Session / 访问控制→逐端点权限验证 / 安全配置→Helmet+CSP+CORS
- **三级安全边界**: Always Do (无条件) / Ask First (需审批) / Never Do (绝对禁止)
- **npm audit 分类决策树**: Critical→立即修复 / Moderate→下版本 / Low→定期
- **安全审计 Agent 角色**: 漏洞检测 + 威胁建模 + OWASP 全面评估

### 来自 vercel-labs/deepsec
- **全代码仓 Agent 漏洞扫描管线**: scan→process→triage→revalidate→export
- **PR Diff 增量审查**: `process --diff` 只审查变更代码
- **分布式执行**: Vercel Sandbox 微 VM 并发扫描大型代码库

### 来自 ruvnet/ruflo
- **CVE 实时扫描**: 代码库 vs CVE 数据库匹配
- **AiDefence**: Prompt 注入拦截 + PII 检测 + 内容安全扫描 (AI Agent 自身安全)
- **路径遍历防护**: 输入校验 + 目录遍历检测

---

## 开发与部署

### 本地开发

```bash
pip install -r requirements.txt
pip install pytest pytest-cov ruff

pytest tests/ --cov=. -v                    # 运行测试
python scanners/cs4_scan.py --all           # 安全扫描
python scripts/compliance_checker.py        # Schema 验证
ruff check .                                # Lint
```

### CI/CD (GitHub Actions)

项目配置了完整的 CI 流程：

| Workflow | 触发条件 | 内容 |
|----------|----------|------|
| **CI** (`ci.yml`) | push / PR to main | Python 3.10/11/12 测试 + CS4 安全扫描 + Lint |
| **Commit Lint** (`commitlint.yml`) | PR | Conventional Commits 格式校验 |

### Commit 规范

```
<type>(<scope>): <description>

Type: feat | fix | docs | style | refactor | perf | test | build | ci | chore | revert | security
Scope: scanner | mcp | adapter | framework | schema | integration | docs | ci | deps | skills

示例:
  feat(scanner): add CS4 prompt injection detection patterns
  fix(mcp): resolve nmap sandbox parameter validation
  security(adapter): patch command injection in trae adapter
```

---

## 参与贡献

本项目遵守 [Contributor Covenant 行为准则](CODE_OF_CONDUCT.md)。欢迎通过 Issue 和 PR 贡献。

### 贡献流程

1. Fork 项目, Clone 到本地
2. 从 `develop` 分支创建 `feature/*` 分支
3. 编写代码 + 测试
4. 运行验证：
   ```bash
   pytest tests/ --cov=. -v
   python scanners/cs4_scan.py --file your-file
   ruff check .
   ```
5. 使用标准 Commit 格式提交, Push 到 Fork
6. 向 `develop` 分支提交 PR (使用 [PR 模板](.github/PULL_REQUEST_TEMPLATE.md))

### 贡献新技能仓库

1. 在 Issue 中提交候选 GitHub 仓库 URL
2. 说明安全领域覆盖和技能格式
3. 审核通过后纳入 [SOURCE_CATALOG.md](docs/SOURCE_CATALOG.md)
4. 运行 `python scripts/index_generator.py` 生成统一索引
5. 运行 `python scanners/cs4_scan.py --all` 完成安全扫描

完整贡献规范：[CONTRIBUTING.md](CONTRIBUTING.md)

---

## 迭代路线

项目按照 [ITERATION_PLAN_V1.md](docs/ITERATION_PLAN_V1.md) 执行分阶段迭代：

| 阶段 | 版本 | 内容 | 时间 |
|------|------|------|------|
| **Phase A** | v1.1.0 | CS4 安全扫描 + MCP 安全升级 + 框架更新 | 4 周 |
| **Phase B** | v1.2.0 | 10 平台适配器 + CLI 工具 + 技能迁移 | 4 周 |
| **Phase C** | v2.0.0-beta | Agent Swarm 编排 + Web UI + VS Code 扩展 | 6 周 |
| **Phase D** | v2.0.0 | PyPI 发布 + Awesome List + 社区推广 | 4 周 |

---

## 常见问题 (FAQ)

### Q: 技能中包含攻击性内容, 如何安全使用?
A: 所有技能均已通过 CS4 安全扫描并标注信任分级。🟡 Caution / 🔴 Restricted 技能仅限授权安全测试使用。MCP 安全配置中的 `execution_policy: ask_first` 会在执行前要求用户确认。

### Q: 如何在不同 AI Agent 平台间切换?
A: 项目提供 6 个平台的适配器 (Trae / Flocks / Claude Code / Cursor / DeepSeek V4 / Ollama 本地), 使用 CAUI 统一接口即可切换。更多平台 (Codex CLI / Gemini CLI) 将在 v1.2.0 支持。

### Q: 如何贡献我的安全技能?
A: 参见 [CONTRIBUTING.md](CONTRIBUTING.md) 的 "Adding New Skills" 部分。技能需符合 [统一 Schema](schema/unified-skill.schema.json)，并通过 CS4 安全扫描。

### Q: CS4 扫描误报了怎么办?
A: 误报率目标 <15%。如遇误报，请提交 Issue 附带被误报的文件路径和具体匹配项，我们会调整规则库。

### Q: 支持哪些 Python 版本?
A: Python 3.10、3.11、3.12 均通过 CI 测试。

---

## 许可证

本项目基于 [MIT License](LICENSE) 开源。

上游仓库许可证：
- MIT: Hi-FullHouse/CyberSecurity-Skills, addyosmani/agent-skills, ruvnet/ruflo
- Apache-2.0: mukul975/Anthropic-Cybersecurity-Skills, vercel-labs/deepsec

版权声明详见 [NOTICE.md](NOTICE.md)。

---

> **Powered by CyberSecuritySkills · v1.1.0 · [ITERATION_PLAN_V1.md](docs/ITERATION_PLAN_V1.md)**
