# CyberSecurity AI Skills Unified — 项目总体规划

## 项目愿景
构建**全球最完整的网络安全AI技能统一集成平台**，让任何AI Agent (Trae/Flocks/Claude Code/Cursor/DeepSeek V4) 都能像资深安全分析师一样执行专业安全任务。

## 项目范围

### 技能覆盖 (41领域)
| 象限 | 领域数 | 关键场景 |
|------|--------|----------|
| 🔴 红队/攻击面 | 14 | 渗透测试、漏洞利用、权限提升、红蓝对抗 |
| 🔵 蓝队/防御面 | 14 | 威胁狩猎、应急响应、数字取证、SOC运营 |
| 🟢 基础设施安全 | 9 | 云安全、容器安全、API安全、零信任 |
| 🟣 新兴专项安全 | 4 | 大模型安全、工控安全、区块链、物联网 |

### 平台支持 (6+)
- Trae (字节跳动)
- Flocks (微步开源)
- Claude Code (Anthropic)
- Cursor (Anysphere)
- DeepSeek V4 (DeepSeek)
- (计划) GitHub Copilot / OpenAI Codex CLI / Gemini CLI

### 框架映射 (7重)
MITRE ATT&CK v18 · NIST CSF 2.0 · MITRE ATLAS v5.4 · MITRE D3FEND v1.3 · NIST AI RMF 1.0 · 等保2.0 · ISO 27001:2022

## 关键里程碑
- [x] 2026-05-19: 项目启动 + 源仓库深度分析
- [ ] 2026-06-02: Phase 1 完成 → 统一Schema + 全量技能标准化
- [ ] 2026-06-30: Phase 2 完成 → 6平台适配器 + CAUI统一接口
- [ ] 2026-07-28: Phase 3 完成 → DeepSeek V4优化 + 完备性验证
- [ ] 2026-08-25: Phase 4 完成 → v1.0.0 正式发布 + 生态推广

## 技术栈
- Python 3.10+ (核心)
- JSON Schema (数据验证)
- YAML (Flocks适配)
- OpenAI SDK (DeepSeek V4 API)
- GitHub Actions (CI/CD)

## 团队
- 项目架构师 ×1
- 平台工程师 ×2 (Trae/Flocks + Claude Code/Cursor)
- AI工程师 ×2 (DeepSeek V4 + 优化器)
- 安全研究员 ×2 (技能审核 + 框架映射)
- QA工程师 ×1 (测试 + 合规)
- 社区运营 ×1 (文档 + 推广)
