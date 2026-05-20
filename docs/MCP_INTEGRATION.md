# 🔌 CyberSecuritySkills — 网络安全工具 MCP 集成指南

> **MCP (Model Context Protocol)**: Anthropic 开源的 AI Agent 工具调用标准协议  
> **目标**: 让 AI Agent 通过 MCP 直接操控 BurpSuite、IDA Pro、Ghidra 等安全工具  
> **更新时间**: 2026-05-20

---

## 一、MCP 协议简述

MCP 是 AI Agent 的 "USB-C 接口"——一套标准协议，让任何 AI Agent (Claude Code / Cursor / Trae / Flocks / DeepSeek V4) 以统一方式调用外部工具。

```
AI Agent (Claude Code / Cursor / Trae ...)
    │
    ▼  MCP Protocol (JSON-RPC over stdio/SSE/Streamable HTTP)
    │
    ├── IDA Pro MCP ──── 逆向分析 (反编译/反汇编/XRef/调试)
    ├── BurpSuite MCP ─── Web渗透 (代理/扫描/日志/漏洞检测)
    ├── Ghidra MCP ────── 逆向分析 (开源替代)
    ├── Nmap MCP ──────── 端口扫描/服务发现
    ├── Wireshark MCP ─── 网络抓包/流量分析
    ├── Metasploit MCP ── 漏洞利用框架
    ├── Volatility MCP ── 内存取证
    ├── Shodan MCP ────── 网络空间搜索
    ├── VirusTotal MCP ── 恶意文件检测
    └── sqlmap MCP ────── SQL注入自动化
```

---

## 二、已确认的网络安全 MCP 服务器

### 🥇 Tier 1 — 生产级 (已有成熟实现)

| 工具 | GitHub 仓库 | Stars | 许可证 | MCP 传输 | 关键能力 |
|------|-------------|-------|--------|----------|----------|
| **IDA Pro** | [mrexodia/ida-pro-mcp](https://github.com/mrexodia/ida-pro-mcp) | 高活跃 | MIT | stdio / SSE / Streamable HTTP | 反编译 / 反汇编 / XRef / 调试 / 内存读写 / 结构体 / 栈帧 |
| **BurpSuite** | [X3r0K/BurpSuite-MCP-Server](https://github.com/X3r0K/BurpSuite-MCP-Server) | 1.4K | MIT | HTTP REST → SSE | 代理拦截 / 主动扫描 / 漏洞检测(SQLi/XSS/SSRF等9类) / 流量分析 |
| **Shodan** | [BurtTheCoder/Shodan-MCP](https://github.com/BurtTheCoder/Shodan-MCP) | 186 | MIT | stdio | IP查询 / 设备搜索 / DNS查询 / CVE查询 / CPE查询 |

### 🥈 Tier 2 — 社区验证 (腾讯云 MCP 广场收录)

| 工具 | 来源 | 能力 |
|------|------|------|
| **VirusTotal MCP** | 腾讯云 MCP 广场 | 文件/URL/Hash 多引擎扫描 / 恶意软件检测 |
| **Threat Intel MCP** (Shodan+VT) | 腾讯云 MCP 广场 | 集成Shodan+VirusTotal的综合威胁情报分析平台 |

### 🥉 Tier 3 — MCP 封装模板 (本项目提供的工具包装器)

以下工具尚无公开 MCP 实现，本项目提供标准化的 MCP 封装配置模板：

| 工具 | 封装方式 | 模板文件 |
|------|----------|----------|
| **Ghidra** | Python Bridge (ghidra_bridge) → MCP stdio | `mcp/configs/ghidra-mcp.json` |
| **Nmap** | CLI wrapper (python-nmap) → MCP stdio | `mcp/configs/nmap-mcp.json` |
| **Wireshark/tshark** | CLI wrapper (tshark + pyshark) → MCP stdio | `mcp/configs/wireshark-mcp.json` |
| **Metasploit** | RPC API (msfrpc) → MCP stdio | `mcp/configs/metasploit-mcp.json` |
| **Volatility3** | Python API → MCP stdio | `mcp/configs/volatility-mcp.json` |
| **sqlmap** | CLI wrapper → MCP stdio | `mcp/configs/sqlmap-mcp.json` |
| **Binary Ninja** | Python API → MCP stdio | `mcp/configs/binaryninja-mcp.json` |

---

## 三、工具 MCP 配置速查

### 3.1 IDA Pro MCP — 逆向工程 AI 副驾驶

**安装 (Claude Code)**:
```bash
claude plugin marketplace add mrexodia/claude-marketplace
claude plugin install ida-pro-mcp@mrexodia
```

**核心工具**: `decompile` / `disasm` / `xrefs_to` / `callees` / `lookup_funcs` / `int_convert` / `set_comments` / `patch_asm` / `get_bytes` / `stack_frame` / `read_struct` / `dbg_*`

**调试器扩展** (需 `?ext=dbg`):
`dbg_start` / `dbg_continue` / `dbg_step_into` / `dbg_add_bp` / `dbg_regs` / `dbg_stacktrace` / `dbg_read` / `dbg_write`

**Headless 模式** (无需 GUI):
```bash
uv run idalib-mcp --host 127.0.0.1 --port 8745 path/to/binary.exe
```

---

### 3.2 BurpSuite MCP — Web 渗透 AI 副驾驶

**安装**:
```bash
git clone https://github.com/X3r0K/BurpSuite-MCP-Server.git
cd BurpSuite-MCP-Server && pip install -r requirements.txt
python main.py  # → http://localhost:8000
```

**核心能力**:

| 模块 | 端点 | 能力 |
|------|------|------|
| 🔄 代理 | `/proxy/intercept` | 拦截/修改 HTTP/HTTPS 流量 |
| 🔍 扫描 | `/scanner/start` | 主动/被动扫描, SQLi/XSS/SSRF 等9类漏洞 |
| 📝 日志 | `/logger/logs` | HTTP流量日志, 高级过滤与搜索 |
| 🎯 漏洞 | `/logger/vulnerabilities` | 实时漏洞检测 + 严重性分析 |

**Claude Code / Cursor 集成**:
```json
{
  "mcpServers": {
    "burpsuite": {
      "command": "python",
      "args": ["main.py"],
      "cwd": "/path/to/BurpSuite-MCP-Server",
      "env": {
        "BURP_API_KEY": "your_key",
        "BURP_PROXY_PORT": "8080",
        "MCP_SERVER_PORT": "8000"
      }
    }
  }
}
```

---

### 3.3 Shodan MCP — 网络空间搜索引擎

**安装**:
```bash
git clone https://github.com/BurtTheCoder/Shodan-MCP.git
cd Shodan-MCP && pip install -r requirements.txt
```

**配置** (`.cursor/mcp.json` 或 `claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "shodan": {
      "command": "python",
      "args": ["shodan_mcp.py"],
      "env": { "SHODAN_API_KEY": "your_key" }
    }
  }
}
```

**核心工具**: IP查询 / 设备搜索 / DNS解析 / CVE数据库查询 / CPE产品查询

---

### 3.4 Ghidra MCP — 开源逆向分析 (本项目封装)

Ghidra 尚无官方 MCP，但可通过 `ghidra_bridge` (Python) 封装。

**封装方案** (`mcp/scripts/ghidra_mcp_server.py`):
```python
# 核心思路: ghidra_bridge 提供 Python API → MCP tools
# 支持的 MCP 工具:
#   - ghidra_decompile(addr)      → 反编译函数
#   - ghidra_disassemble(addr)    → 反汇编
#   - ghidra_xrefs(addr)          → 交叉引用
#   - ghidra_search(pattern)      → 字节搜索
#   - ghidra_rename(addr, name)   → 重命名
#   - ghidra_set_type(addr, type)  → 设置类型
```

**安装与启动**:
```bash
pip install ghidra-bridge mcp
# 先在 Ghidra 中运行 ghidra_bridge 服务端
# 然后:
python mcp/scripts/ghidra_mcp_server.py
```

---

### 3.5 Nmap MCP — 端口扫描 (本项目封装)

```python
# 封装 python-nmap + MCP
# MCP 工具:
#   - nmap_scan(target, ports, args)    → 端口扫描
#   - nmap_os_detect(target)            → 操作系统检测
#   - nmap_service_detect(target, port) → 服务版本检测
#   - nmap_vuln_scan(target)            → NSE 漏洞脚本扫描
```

**Claude Code 配置**:
```json
{
  "mcpServers": {
    "nmap": {
      "command": "python",
      "args": ["mcp/scripts/nmap_mcp_server.py"],
      "cwd": "/path/to/CyberSecuritySkills"
    }
  }
}
```

---

### 3.6 Wireshark MCP — 网络流量分析 (本项目封装)

```python
# 封装 tshark (Wireshark CLI) + MCP
# MCP 工具:
#   - tshark_capture(interface, filter, count)
#   - tshark_read(pcap_file, filter)
#   - tshark_stats(pcap_file)
#   - tshark_follow_stream(pcap_file, stream_id)
```

---

### 3.7 Metasploit MCP — 漏洞利用 (本项目封装)

```python
# 封装 msfrpc (Metasploit RPC API) + MCP
# MCP 工具:
#   - msf_search(query)           → 搜索模块
#   - msf_exploit(module, target) → 执行漏洞利用
#   - msf_sessions()              → 列出会话
#   - msf_payloads()              → 列出载荷
```

---

### 3.8 Volatility3 MCP — 内存取证 (本项目封装)

```python
# 封装 volatility3 Python API + MCP
# MCP 工具:
#   - vol_pslist(memdump)      → 进程列表
#   - vol_netscan(memdump)     → 网络连接
#   - vol_malfind(memdump)     → 恶意代码检测
#   - vol_dumpfiles(memdump, pid) → 提取文件
#   - vol_yara(memdump, rules) → YARA 扫描
```

---

## 四、MCP 发现与注册

### mcp-registry.json — 统一 MCP 注册清单

项目提供 `mcp/mcp-registry.json`，记录所有已收录的网络安全 MCP 服务器，供 Agent 自动发现。

### 从 Awesome MCP 列表发现新 MCP

- [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) — 收录 5000+ MCP 服务器
- [appscodelove/awesome-mcp-security](https://github.com/appscodelove/awesome-mcp-security) — 安全专项 MCP 列表
- 腾讯云 [MCP 广场](https://cloud.tencent.com/developer/mcp) — 安全扫描 + 收录

---

## 五、与 CyberSecuritySkills 的集成

所有 MCP 配置可与项目 Skills 无缝配合：

```
用户: "分析这个内存转储文件"
  ↓
Agent 加载 CyberSecuritySkills → performing-memory-forensics-with-volatility3
  ↓
Agent 调用 Volatility3 MCP → vol_pslist / vol_malfind / vol_yara
  ↓
Agent 按 Skill Workflow 逐步执行 → 生成取证报告
```

```
用户: "对 example.com 做 Web 渗透测试"
  ↓
Agent 加载: 信息搜集 → 漏洞扫描 → 漏洞利用
  ↓
  ├── Shodan MCP: 网络资产发现
  ├── Nmap MCP: 端口扫描
  ├── BurpSuite MCP: Web扫描 + 漏洞检测
  └── sqlmap MCP: SQL注入自动化
  ↓
Agent 按 PTES 流程生成渗透测试报告
```

---

> **下一步**: 查看 `mcp/configs/` 获取各工具的具体配置模板  
> **贡献**: 发现新的安全 MCP 服务器，提交 Issue 或 PR 到 `mcp/mcp-registry.json`
