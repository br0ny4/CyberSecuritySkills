# 📚 CyberSecuritySkills — 外部技能仓库源目录

> **最后更新**: 2026-05-19  
> **已接入仓库**: 7 个 | **可发现技能总数**: 800+ (去重后)  
> **发现平台**: 3 个 (SkillsMP.com / SkillStore.io / agentskills.me)

---

## 一、已接入的核心源仓库 (Direct Integration)

### 👑 Tier 1 — 全量深度融合 (技能文件直接纳入统一索引)

| # | 仓库 | ⭐ Stars | 技能数 | 领域 | 许可证 | 接入状态 |
|---|------|---------|--------|------|--------|----------|
| 1 | [Hi-FullHouse/CyberSecurity-Skills](https://github.com/Hi-FullHouse/CyberSecurity-Skills) | - | 195 | 39领域 (PTES + 拓展) | MIT | ✅ 已接入 |
| 2 | [mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills) | - | 754 | 26领域 + 5框架映射 | Apache-2.0 | ✅ 已接入 |

### 🥇 Tier 2 — 精选安全技能补充 (提取安全专项技能纳入)

| # | 仓库 | ⭐ Stars | 新增技能 | 安全覆盖 | 许可证 | 接入状态 |
|---|------|---------|----------|----------|--------|----------|
| 3 | [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | ~42K | +1 安全硬核技能 + 安全审计Agent + 安全检查清单 | OWASP Top 10 / Auth / 密钥管理 / 依赖审计 / CSP / 速率限制 | MIT | ✅ 本次接入 |
| 4 | [vercel-labs/deepsec](https://github.com/vercel-labs/deepsec) | - | +1 Agent漏洞扫描管线 | 全代码仓漏洞扫描 / CVE检测 / 正则匹配器库 / PR Diff审查 | Apache-2.0 | ✅ 本次接入 |
| 5 | [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | ~49K | +2 安全插件 (security-audit + aidefence) | CVE扫描 / 输入校验 / 路径遍历防护 / Prompt注入拦截 / PII检测 | MIT | ✅ 本次接入 |

### 🥈 Tier 3 — 技能发现平台 (持续监控新技能来源)

| # | 平台 | 安全技能数 | 价值 | 接入方式 |
|---|------|-----------|------|----------|
| 6 | [SkillsMP.com/categories/security](https://skillsmp.com/categories/security) | 38,340 | GitHub全量Agent Skills聚合，Security子类收录最广 | 定期爬取新增安全技能 |
| 7 | [SkillStore.io](https://skillstore.io/zh-hans) — Security & Compliance | 若干 (安全审核通过) | 经安全审计的技能市场，唯一可信来源 | 定期同步审核通过的技能 |

---

## 二、各仓库接入详情

### 3. addyosmani/agent-skills → 提取安全专项

**仓库规模**: 23个生命周期技能 + 3个Agent角色 + 4个参考清单  
**提取内容**:
- `skills/security-and-hardening/SKILL.md` → **安全加固技能** (349行，OWASP Top 10全覆盖)
- `agents/security-auditor.md` → **安全审计Agent角色** (漏洞检测 + 威胁建模)
- `references/security-checklist.md` → **安全检查清单** (Pre-commit + Auth + 输入校验)

**安全技能覆盖**:
| 领域 | 内容 |
|------|------|
| 注入防御 (A1) | SQL注入 / NoSQL注入 / OS命令注入 — 参数化查询 + ORM |
| 认证失效 (A2) | bcrypt/scrypt/argon2 密码哈希 / Session管理 / httpOnly+secure+samesite |
| XSS (A3) | DOMPurify / 框架自动转义 / CSP头 |
| 访问控制 (A4) | 每端点权限检查 / 资源所有权验证 |
| 安全配置 (A5) | Helmet / CSP / CORS / 安全头 |
| 敏感数据 (A6) | 响应脱敏 / 环境变量密钥管理 / PII加密 |
| 速率限制 | express-rate-limit → 通用100req/15min + 认证10req/15min |
| 文件上传安全 | MIME校验 / 大小限制 / Magic Bytes |
| npm audit分类 | Critical→立即修复 / Moderate→下版本 / Low→定期排查 |

**Three-Tier Boundary System (三级安全边界)**:
1. Always Do — 无条件执行的安全措施
2. Ask First — 需人工审批的操作
3. Never Do — 绝对禁止的行为

---

### 4. vercel-labs/deepsec → 提取漏洞扫描管线

**类型**: Agent驱动的全代码仓安全扫描工具 (非纯技能)  
**提取内容**:
- `SKILL.md` → Agent引导文件 (描述扫描流程)
- Pipeline: `scan → process → triage → revalidate → export`
- Regex Matcher库: 项目特定漏洞模式匹配规则
- PR Diff模式: `process --diff` 增量代码安全审查

**技能化改造方案**:
将 deepsec 的扫描方法论抽象为独立技能:
```
skills/automated-vuln-scanning/
├── SKILL.md          ← 自动化漏洞扫描技能 (基于 deepsec 方法论)
├── references/
│   └── matcher-patterns.md  ← 常见漏洞正则匹配模式库
└── scripts/
    └── scan_runner.py ← 扫描管线调度脚本
```

**安全价值**: 提供 Production-grade 的自动化代码安全审计能力，弥补现有技能库在"大规模代码库全量扫描"方面的空白。

---

### 5. ruvnet/ruflo → 提取安全插件

**仓库规模**: 100+ Agent / 32插件 / 314 MCP工具  
**提取内容**:
| 插件 | 安全能力 | 集成方式 |
|------|----------|----------|
| `ruflo-security-audit` | 代码漏洞扫描 + CVE数据库查询 | 抽象为安全审计技能模板 |
| `ruflo-aidefence` | Prompt注入拦截 / PII检测 / 内容安全扫描 | 抽象为AI安全防护技能 |

**安全价值**: [AiDefence](https://github.com/ruvnet/ruflo/blob/main/plugins/ruflo-aidefence/README.md) 专注于 AI Agent 自身安全——Prompt注入检测、PII泄露防护——与大模型安全 (LLM Security) 领域高度互补。

---

## 三、技能发现平台集成策略

### SkillsMP.com (38,340 安全技能)

**集成方式**: 周期性同步脚本
```python
# scripts/sync_skillsmp.py (待开发)
# 1. 定期抓取 skillsmp.com/categories/security 新技能
# 2. 按 star/下载量排序，筛选 top-50
# 3. 自动解析 SKILL.md frontmatter
# 4. 生成差异报告 → 人工审核 → 纳入索引
```

### SkillStore.io (安全审核技能)

**集成方式**: 周期性同步
```python
# 1. 同步 skillstore.io "Security & Compliance" 类目
# 2. 仅纳入 safety_rating >= "Safe" 的技能
# 3. 追溯 GitHub 源仓库
# 4. 补充中文元数据
```

---

## 四、技能去重与融合策略

### 去重规则
1. **name 字段精确匹配** → 自动合并 (B源框架映射优先, A源中文字段优先)
2. **语义相似度 >75%** → 标记为候选重复, 人工审核
3. **同领域同功能** → 保留内容更完整的版本, 另一版本作为 `source_repos` 引用

### 融合优先级
```
技能内容权威性: 官方框架映射(B) > 社区实践(C) > 自动生成
中文本地化:     国内Agent适配(A) 优先
平台兼容性:     agentskills.io 标准格式优先
```

---

## 五、后续发现清单 (Watchlist)

| 来源 | 潜力 | 关注原因 |
|------|------|----------|
| `browserbase/skills` — `safe-browser` / `ui-test` | 中 | Web安全测试 (域白名单 + 对抗性UI测试) |
| `0x8506/vibe-security` (SkillStore审核) | 高 | 专注SQLi/XSS多语言检测+自动修复 |
| `JackyST0/awesome-agent-skills` | 高 | Agent技能精选列表，持续发现新安全技能 |
| `mattpocock/skills` (86K⭐) | 低 | 工程方法论参考，非安全专项 |
| `anthropics/skills` (96K⭐) | 参考 | 官方Spec，非技能来源 |

---

> **下次更新**: 随每次 Phase 迭代同步更新  
> **贡献新源**: 通过 Issue 提交仓库 URL → 审核 → 纳入
