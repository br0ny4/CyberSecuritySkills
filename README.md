# 🔒 CyberSecuritySkills — 全门类网络安全AI技能统一集成平台

> **The Unified Cross-Agent Cybersecurity Skill Framework for AI Agents**
>
> 融合 7 大源仓库 | 41+ 安全领域 | 800+ AI可调用技能 | 7重框架映射 | 11+ MCP 工具集成 | 6+ AI Agent 平台原生支持

---

## 📋 项目概述

本项目整合 GitHub 上高质量网络安全 AI 技能仓库，构建一套**全门类、跨平台、标准化**的网络安全AI技能统一集成平台。

### 五大核心目标

| # | 目标 | 交付物 |
|---|------|--------|
| 1 | 全量技能标准化整理 | 统一Schema + 全门类技能目录 + 索引系统 |
| 2 | 多平台适配开发 | Flocks/Trae/Claude Code/Cursor/DeepSeek V4 适配器 |
| 3 | 统一接口体系 | Cross-Agent Unified Interface (CAUI) |
| 4 | DeepSeek V4专项优化 | 调用稳定性 + 执行效率 + 成本优化 |
| 5 | 长周期迭代 + 生态推广 | 4阶段15里程碑 + Flocks/Trae官方推荐 |

---

## 🌐 外部源仓库 (7库融合)

| # | 仓库 | Stars | 技能贡献 | 许可证 |
|---|------|-------|----------|--------|
| 1 | [Hi-FullHouse/CyberSecurity-Skills](https://github.com/Hi-FullHouse/CyberSecurity-Skills) | - | 195技能 / 39领域 | MIT |
| 2 | [mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills) | - | 754技能 / 26领域 / 5框架映射 | Apache-2.0 |
| 3 | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 42K⭐ | +1 安全硬核技能 / 安全审计Agent | MIT |
| 4 | [vercel-labs/deepsec](https://github.com/vercel-labs/deepsec) | 新项目 | +1 Agent漏洞扫描管线 | Apache-2.0 |
| 5 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 49K⭐ | +2 安全插件 (CVE + AI防御) | MIT |
| 6 | [SkillsMP.com](https://skillsmp.com/categories/security) | 38K安全技能 | 持续发现新技能 (聚合平台) | 各仓库 |
| 7 | [SkillStore.io](https://skillstore.io/zh-hans) | 安全审核 | 安全审查通过的技能 (可信源) | 各仓库 |

> 📖 详细源分析: [docs/SOURCE_CATALOG.md](docs/SOURCE_CATALOG.md)

---

## 🗺️ 技能覆盖全景 (41大领域)

### 🔴 红队/攻击面 (14 领域) · 🔵 蓝队/防御面 (14 领域)

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
| 19 | SOC运营 SOC Operations | 37+ | NIST CSF DE/RS |
| 20 | 端点安全 Endpoint Security | 21+ | D3FEND |
| 21 | 勒索软件防御 Ransomware Defense | 10+ | ATT&CK TA0040 |
| 22 | 恶意软件分析 Malware Analysis | 39+ | ATT&CK |
| 23 | 网络安全 Network Security | 40+ | D3FEND D3-NTA |
| 24 | 欺骗防御 Deception Technology | 2+ | D3FEND |
| 25 | 钓鱼防御 Phishing Defense | 16+ | ATT&CK T1566 |
| 26 | 报告撰写 Reporting | 5+ | PTES |
| 27 | 漏洞管理 Vulnerability Management | 31+ | NIST CSF ID.RA |
| 28 | 安全运营 Security Operations | 36+ | NIST CSF |

### 🟢 基础设施安全 (9 领域) · 🟣 新兴专项安全 (5 领域)

| ID | 领域 | 技能数 | 对标框架 |
|----|------|--------|----------|
| 29 | 云安全 Cloud Security | 68+ | CIS Benchmarks |
| 30 | 容器安全 Container Security | 34+ | CIS K8s Benchmarks |
| 31 | API安全 API Security | 31+ | OWASP API Top 10 |
| 32 | 代码审计 Code Audit | 9+ | OWASP |
| 33 | 供应链安全 Supply Chain Security | 5+ | SLSA / SSDF |
| 34 | 操作系统安全 OS Security | 6+ | CIS Benchmarks |
| 35 | 身份访问管理 IAM | 39+ | NIST CSF PR.AA |
| 36 | 密码学与PKI Cryptography & PKI | 17+ | NIST SP 800-175B |
| 37 | 零信任架构 Zero Trust | 16+ | CISA ZTMM |
| 38 | 大模型安全 LLM Security | 10+ | OWASP Top 10 for LLM / MITRE ATLAS |
| 39 | 工控安全 ICS/OT Security | 34+ | IEC 62443 |
| 40 | 区块链/Web3安全 Blockchain Security | 6+ | SCSVS |
| 41 | 物联网安全 IoT Security | 6+ | OWASP IoT Top 10 |

---

## 🏗️ 项目架构

```
CyberSecuritySkills/
├── README.md                          # 项目总览 (本文件)
├── PROJECT_PLAN.md                    # 项目总体规划
├── SKILLS_INVENTORY.md                # 全门类技能清单 (800+条目)
├── TODO.md                            # 4阶段15里程碑迭代计划
├── CHANGELOG.md                       # 版本变更记录
│
├── docs/
│   ├── SOURCE_CATALOG.md              # 外部源仓库目录 (7源分析)
│   └── COMPLIANCE_REPORT.md           # 合规性审查与生态适配清单
│
├── schema/
│   ├── unified-skill.schema.json      # 统一技能Schema (7重框架映射)
│   ├── agent-manifest.schema.json     # Agent集成Manifest Schema
│   └── crosswalk.json                 # 框架交叉映射表
│
├── adapters/
│   ├── base/adapter_base.py           # 适配器抽象基类
│   ├── trae/trae_adapter.py           # Trae IDE 适配器
│   ├── flocks/flocks_adapter.py       # Flocks 适配器 (YAML+批量)
│   ├── claude_code/                   # Claude Code 适配器
│   ├── cursor/cursor_adapter.py       # Cursor IDE 适配器
│   └── deepseek_v4/                   # DeepSeek V4 适配器 + 优化器
│
├── integration/
│   ├── unified_interface.py           # CAUI统一接口 + AgentRegistry
│   ├── skill_router.py                # 智能路由引擎
│   └── prompt_builder.py              # 跨平台Prompt构建器
│
├── scripts/
│   ├── index_generator.py             # 统一索引生成器
│   ├── migration_tools.py             # 技能格式迁移工具
│   ├── compliance_checker.py          # 合规性自动检查
│   └── benchmark.py                   # 性能基准测试
│
└── tests/
    └── test_integration.py            # 28项单元测试
```

---

## 🚀 快速开始

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

### DeepSeek V4 (API直接调用)
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

---

## 🎯 七重框架映射

| 框架 | 版本 | 覆盖 |
|------|------|------|
| **MITRE ATT&CK** | v18 | 14/14 Tactics |
| **NIST CSF 2.0** | 2.0 | 6/6 Functions |
| **MITRE ATLAS** | v5.4 | 16/16 Tactics |
| **MITRE D3FEND** | v1.3 | 7/7 Categories |
| **NIST AI RMF** | 1.0 | 4/4 Functions |
| **等级保护 2.0** | GB/T 22239 | 全类别 |
| **ISO 27001:2022** | 2022 | Annex A |

---

## 📊 新增安全技能亮点 (v1.0.0-pre Iteration #3)

### 来自 addyosmani/agent-skills
- **OWASP Top 10 全防**: SQL注入→参数化查询 / XSS→DOMPurify / 认证→bcrypt+Session / 访问控制→逐端点权限验证 / 安全配置→Helmet+CSP+CORS
- **三级安全边界**: Always Do (无条件) / Ask First (需审批) / Never Do (绝对禁止)
- **npm audit 分类决策树**: Critical→立即修复 / Moderate→下版本 / Low→定期
- **安全审计Agent角色**: 漏洞检测 + 威胁建模 + OWASP 全面评估

### 来自 vercel-labs/deepsec
- **全代码仓Agent漏洞扫描管线**: scan→process→triage→revalidate→export
- **PR Diff增量审查**: `process --diff` 只审查变更代码
- **分布式执行**: Vercel Sandbox微VM并发扫描大型代码库

### 来自 ruvnet/ruflo
- **CVE实时扫描**: 代码库 vs CVE数据库匹配
- **AiDefence**: Prompt注入拦截 + PII检测 + 内容安全扫描 (AI Agent自身安全)
- **路径遍历防护**: 输入校验 + 目录遍历检测

---

## 🤝 贡献

本项目遵守 [Contributor Covenant 行为准则](CODE_OF_CONDUCT.md)。欢迎通过 Issue 和 PR 贡献。

### 贡献新技能仓库
1. 在 Issue 中提交候选 GitHub 仓库 URL
2. 说明安全领域覆盖和技能格式
3. 审核通过后纳入 [SOURCE_CATALOG.md](docs/SOURCE_CATALOG.md)
4. 运行 `python scripts/index_generator.py` 生成统一索引

---

## 🔌 MCP 工具集成 (11+ 安全工具 MCP)

让 AI Agent 通过 MCP 协议直接操控 BurpSuite、IDA Pro、Ghidra 等安全工具。

| Tier | 工具 | MCP 仓库 | 状态 |
|------|------|----------|------|
| 🥇 | **IDA Pro** | [mrexodia/ida-pro-mcp](https://github.com/mrexodia/ida-pro-mcp) | ✅ 生产级 |
| 🥇 | **BurpSuite** | [X3r0K/BurpSuite-MCP-Server](https://github.com/X3r0K/BurpSuite-MCP-Server) | ✅ 1.4K⭐ |
| 🥇 | **Shodan** | [BurtTheCoder/Shodan-MCP](https://github.com/BurtTheCoder/Shodan-MCP) | ✅ 已验证 |
| 🥈 | **VirusTotal** | 腾讯云MCP广场 | ✅ 已验证 |
| 🥉 | **Ghidra / Nmap / Wireshark / Metasploit / Volatility3 / sqlmap / Binary Ninja** | 本项目封装 | ✅ 配置模板 |

📖 完整 MCP 集成指南: [docs/MCP_INTEGRATION.md](docs/MCP_INTEGRATION.md)  
📋 MCP 注册清单: [mcp/mcp-registry.json](mcp/mcp-registry.json)

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

上游仓库许可证:
- MIT: Hi-FullHouse/CyberSecurity-Skills, addyosmani/agent-skills, ruvnet/ruflo
- Apache-2.0: mukul975/Anthropic-Cybersecurity-Skills, vercel-labs/deepsec

---

> **Powered by CyberSecuritySkills · v1.0.0-pre · [SOURCE_CATALOG.md](docs/SOURCE_CATALOG.md)**
