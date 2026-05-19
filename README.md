# 🔒 CyberSecurity AI Skills Unified — 全门类网络安全AI技能统一集成平台

> **The Unified Cross-Agent Cybersecurity Skill Framework for AI Agents**
>
> 融合 Hi-FullHouse/CyberSecurity-Skills (195技能/39领域) 与 mukul975/Anthropic-Cybersecurity-Skills (754技能/26领域)
> 
> **总计覆盖: 41+ 安全领域 | 900+ AI可调用技能 | 5+ 框架映射 | 6+ AI Agent 平台原生支持**

---

## 📋 项目概述

本项目整合全球两大网络安全AI技能开源仓库的最佳实践，构建一套**全门类、跨平台、标准化**的网络安全AI技能统一集成平台。覆盖从渗透测试、威胁检测、应急响应到安全审计、云安全、工控安全等全部网络安全细分场景，确保技能可在 **Trae**、**Flocks**、**Claude Code**、**Cursor**、**DeepSeek V4** 等主流AI Agent平台中无缝调用。

### 五大核心目标

| # | 目标 | 交付物 |
|---|------|--------|
| 1 | 全量技能标准化整理 | 统一Schema + 全门类技能目录 + 索引系统 |
| 2 | 多平台适配开发 | Flocks/Trae/Claude Code/Cursor 适配器 |
| 3 | 统一接口体系 | Cross-Agent Unified Interface (CAUI) |
| 4 | DeepSeek V4专项优化 | 调用稳定性 + 执行效率 + 成本优化 |
| 5 | 长周期迭代规划 | 4阶段15里程碑 TODO + 版本发布计划 |

---

## 🗺️ 技能覆盖全景 (41大领域)

### 🔴 红队/攻击面 (Offensive — 14 领域)

| ID | 领域 | 来源 | 技能数 | 对标框架 |
|----|------|------|--------|----------|
| 01 | 信息搜集 Reconnaissance | A+B | 25+ | PTES / ATT&CK TA0043 |
| 02 | 漏洞扫描 Vulnerability Scanning | A+B | 20+ | PTES / ATT&CK TA0043 |
| 03 | 漏洞利用 Exploitation | A+B | 30+ | PTES / ATT&CK TA0002 |
| 04 | 权限提升 Privilege Escalation | A+B | 15+ | ATT&CK TA0004 |
| 05 | 后渗透 Post-Exploitation | A+B | 15+ | PTES |
| 06 | 横向移动 Lateral Movement | A+B | 15+ | ATT&CK TA0008 |
| 07 | 持久化 Persistence | A+B | 20+ | ATT&CK TA0003 |
| 08 | 痕迹清除 Covering Tracks | A+B | 10+ | ATT&CK TA0005 |
| 09 | 社会工程学 Social Engineering | A+B | 20+ | ATT&CK TA0001 |
| 10 | 无线安全 Wireless Security | A | 5+ | PTES |
| 11 | 移动安全 Mobile Security | A+B | 15+ | OWASP MSTG |
| 12 | 逆向工程 Reverse Engineering | A+B | 18+ | ATT&CK TA0002 |
| 13 | 渗透测试 Pentesting | B | 23+ | PTES / OWASP |
| 14 | 红蓝对抗 Red/Blue Team | A+B | 30+ | ATT&CK Enterprise |

### 🔵 蓝队/防御面 (Defensive — 14 领域)

| ID | 领域 | 来源 | 技能数 | 对标框架 |
|----|------|------|--------|----------|
| 15 | 威胁检测与狩猎 Threat Hunting | B | 55+ | ATT&CK / D3FEND |
| 16 | 威胁情报 Threat Intelligence | A+B | 55+ | STIX/TAXII |
| 17 | 应急响应 Incident Response | A+B | 32+ | NIST SP 800-61 |
| 18 | 数字取证 Digital Forensics | A+B | 42+ | NIST SP 800-86 |
| 19 | SOC运营 SOC Operations | A+B | 37+ | NIST CSF DE/RS |
| 20 | 端点安全 Endpoint Security | A+B | 21+ | D3FEND |
| 21 | 勒索软件防御 Ransomware Defense | A+B | 10+ | ATT&CK TA0040 |
| 22 | 恶意软件分析 Malware Analysis | B | 39+ | ATT&CK |
| 23 | 网络流量分析 Network Traffic Analysis | B | 40+ | D3FEND D3-NTA |
| 24 | 欺骗防御 Deception Technology | B | 2+ | D3FEND |
| 25 | 钓鱼防御 Phishing Defense | B | 16+ | ATT&CK T1566 |
| 26 | 报告撰写 Reporting | A | 5+ | PTES |
| 27 | 漏洞管理 Vulnerability Management | A+B | 31+ | NIST CSF ID.RA |
| 28 | 安全运营 Security Operations | B | 36+ | NIST CSF |

### 🟢 基础设施/平台安全 (Infrastructure — 9 领域)

| ID | 领域 | 来源 | 技能数 | 对标框架 |
|----|------|------|--------|----------|
| 29 | 云安全 Cloud Security | A+B | 68+ | CIS Benchmarks |
| 30 | 容器安全 Container Security | A+B | 34+ | CIS K8s Benchmarks |
| 31 | API安全 API Security | A+B | 31+ | OWASP API Top 10 |
| 32 | 代码审计 Code Audit | A | 9+ | OWASP |
| 33 | 供应链安全 Supply Chain Security | A+B | 5+ | SLSA / SSDF |
| 34 | 操作系统安全 OS Security | A | 6+ | CIS Benchmarks |
| 35 | 身份访问管理 IAM | A+B | 39+ | NIST CSF PR.AA |
| 36 | 密码学与PKI Cryptography & PKI | A+B | 17+ | NIST SP 800-175B |
| 37 | 零信任架构 Zero Trust | A+B | 16+ | CISA ZTMM |

### 🟣 新兴/专项安全 (Emerging — 5 领域)

| ID | 领域 | 来源 | 技能数 | 对标框架 |
|----|------|------|--------|----------|
| 38 | 大模型安全 LLM Security | A | 10+ | OWASP Top 10 for LLM / MITRE ATLAS |
| 39 | 工控安全 ICS/OT Security | A+B | 34+ | IEC 62443 |
| 40 | 区块链/Web3安全 Blockchain Security | A | 6+ | SCSVS |
| 41 | 物联网安全 IoT Security | A | 6+ | OWASP IoT Top 10 |

---

## 🏗️ 项目架构

```
cybersecurity-ai-skills-unified/
│
├── README.md                          # 项目总览（本文件）
├── PROJECT_PLAN.md                    # 项目总体规划
├── SKILLS_INVENTORY.md                # 全门类技能清单（900+条目）
├── TODO.md                            # 长周期迭代计划（4阶段15里程碑）
├── CHANGELOG.md                       # 版本变更记录
├── LICENSE                            # MIT License
│
├── schema/                            # 统一标准化层
│   ├── unified-skill.schema.json      # 统一技能Schema定义
│   ├── agent-manifest.schema.json     # Agent集成Manifest Schema
│   └── crosswalk.json                 # 框架交叉映射表
│
├── adapters/                          # 平台适配层
│   ├── base/
│   │   ├── __init__.py
│   │   └── adapter_base.py           # 适配器抽象基类
│   ├── flocks/
│   │   ├── __init__.py
│   │   └── flocks_adapter.py         # Flocks 适配器
│   ├── trae/
│   │   ├── __init__.py
│   │   └── trae_adapter.py           # Trae IDE 适配器
│   ├── claude_code/
│   │   ├── __init__.py
│   │   └── claude_code_adapter.py    # Claude Code 适配器
│   ├── cursor/
│   │   ├── __init__.py
│   │   └── cursor_adapter.py         # Cursor IDE 适配器
│   └── deepseek_v4/
│       ├── __init__.py
│       ├── optimizer.py              # DeepSeek V4 性能优化器
│       └── deepseek_adapter.py       # DeepSeek V4 专用适配
│
├── integration/                       # 统一接口层
│   ├── __init__.py
│   ├── unified_interface.py          # CAUI 统一接口核心
│   ├── agent_registry.py             # Agent注册与发现中心
│   ├── skill_router.py               # 智能路由引擎
│   └── prompt_builder.py             # 跨平台Prompt构建器
│
├── scripts/                           # 工具脚本
│   ├── migration_tools.py            # 技能迁移工具 (A→统一, B→统一)
│   ├── index_generator.py            # 索引自动生成工具
│   ├── compliance_checker.py         # 合规性自动检查
│   └── benchmark.py                  # 性能基准测试
│
├── tests/                             # 测试套件
│   ├── test_adapters.py
│   ├── test_integration.py
│   ├── test_deepseek_optimizer.py
│   └── test_compliance.py
│
└── docs/                              # 文档
    ├── CONTRIBUTING.md
    ├── COMPLIANCE_REPORT.md
    └── ECOSYSTEM_CHECKLIST.md
```

---

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/your-org/cybersecurity-ai-skills-unified.git
cd cybersecurity-ai-skills-unified
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 生成统一索引
```bash
python scripts/index_generator.py --source-a ../CyberSecurity-Skills --source-b ../Anthropic-Cybersecurity-Skills
```

### 4. 在目标Agent中使用

**Trae / Cursor:**
```json
{
  "skills": [{
    "name": "cybersecurity-unified",
    "path": "/path/to/cybersecurity-ai-skills-unified",
    "manifest": "schema/agent-manifest.schema.json"
  }]
}
```

**Claude Code:**
```bash
npx skills add your-org/cybersecurity-ai-skills-unified
```

**Flocks:**
```bash
flocks skill install cybersecurity-unified --source local --path /path/to/repo
```

**DeepSeek V4 (API直接调用):**
```python
from adapters.deepseek_v4.deepseek_adapter import DeepSeekSkillAdapter

adapter = DeepSeekSkillAdapter(
    skill_repo_path="/path/to/repo",
    optimize_for="accuracy",  # or "speed", "cost"
    max_context=1_000_000      # V4 supports 1M context
)

result = adapter.execute_skill(
    skill_name="performing-memory-forensics-with-volatility3",
    context={"memory_dump": "/cases/case-001/memory.raw"}
)
```

---

## 🎯 五重框架映射

本项目全面映射五大国际安全框架，确保技能在执行时自动关联合规要求：

| 框架 | 版本 | 映射技能数 | 覆盖度 |
|------|------|-----------|--------|
| **MITRE ATT&CK** | v18 | 800+ | 14/14 Tactics |
| **NIST CSF 2.0** | 2.0 | 700+ | 6/6 Functions |
| **MITRE ATLAS** | v5.4 | 120+ | 16/16 Tactics |
| **MITRE D3FEND** | v1.3 | 300+ | 7/7 Categories |
| **NIST AI RMF** | 1.0 | 100+ | 4/4 Functions |
| **等级保护 2.0** | GB/T 22239 | 400+ | 全类别 |
| **ISO 27001:2022** | 2022 | 500+ | Annex A |

---

## 📊 技能标准化格式 (Unified)

每个技能文件基于 `agentskills.io` 开放标准，融合两个源仓库的最佳实践：

```yaml
---
# ===== 统一技能Schema =====
name: skill-name-in-kebab-case            # 唯一标识符 [必填]
description: >-                            # 技能描述 (AI Agent 发现用) [必填]
  详细描述此技能的用途、适用场景和关键能力，包含关键词以优化搜索匹配。
domain: cybersecurity                      # 领域分类 [必填]
subdomain: digital-forensics               # 子领域 [必填]

# ===== 多框架映射 =====
mitre_attack: [T1003, T1040]              # MITRE ATT&CK技术
nist csf: [DE.CM-01, RS.AN-03]           # NIST CSF 2.0
mitre_atlas: [AML.T0047]                  # MITRE ATLAS (AI安全)
mitre_d3fend: [D3-MA, D3-PSMD]           # MITRE D3FEND (防御)
nist_ai_rmf: [MEASURE-2.6]               # NIST AI RMF
cn_standard: [等保2.0-安全计算环境]       # 国内合规标准

# ===== 元数据 =====
version: "1.0.0"                           # 语义化版本
difficulty: "★★★☆"                        # 难度 1-5星 (中英双轨)
author: unified-team                       # 作者
license: MIT                               # 许可证
source_repos:                              # 来源追溯
  - Hi-FullHouse/CyberSecurity-Skills
  - mukul975/Anthropic-Cybersecurity-Skills

# ===== AI Agent 优化 =====
estimated_tokens: 1800                     # 预估Token消耗
execution_time: "medium"                   # short/medium/long
requires_tools: [volatility3, yara]       # 依赖工具
platforms: [all]                           # 适配平台
optimized_for: [deepseek-v4, claude]      # 专项优化目标

# ===== 中文字段 (国内Agent适配) =====
name_cn: Volatility3内存取证分析
category_cn: 数字取证
difficulty_cn: ★★★★
tags_cn: [取证, 内存分析, Volatility3, 应急响应]
---

# {技能中文标题} / {Skill English Title}

## 📋 概述 / Overview
技能核心定义、适用场景、前置条件

## 🎯 使用时机 / When to Use
AI Agent 触发条件：何时应自动激活此技能

## 🔧 前置条件 / Prerequisites
运行时依赖、工具版本、访问权限

## 📐 工作流程 / Workflow
逐步执行指南 (含命令示例)
### Step 1: ...
### Step 2: ...
...

## ✅ 验证方法 / Verification
如何确认技能执行成功

## 🔍 输出格式 / Output Format
预期产出的数据结构和报告模板

## 🛠️ 工具链 / Tools & Systems
推荐工具与替代方案

## 📚 参考资源 / References
外部链接、标准文档、相关CVE
```

---

## 🤝 贡献

本项目遵守 [Contributor Covenant 行为准则](CODE_OF_CONDUCT.md)。欢迎通过 Issue 和 PR 贡献。

### 贡献技能流程
1. Fork 本仓库
2. 按照统一 Schema 编写技能文件
3. 运行 `python scripts/index_generator.py --validate` 验证格式
4. 提交 PR 并 @reviewers

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。
上游仓库分别基于 MIT (Hi-FullHouse/CyberSecurity-Skills) 和 Apache-2.0 (mukul975/Anthropic-Cybersecurity-Skills)。

---

> **Powered by Unified Cybersecurity AI Skills Framework · v1.0.0-pre**
