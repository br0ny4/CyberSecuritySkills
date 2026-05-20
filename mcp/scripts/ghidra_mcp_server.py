#!/usr/bin/env python3
"""
Ghidra MCP Server — Ghidra 逆向分析 AI Agent 集成
======================================================
通过 ghidra_bridge 将 Ghidra 的 Python API 封装为 MCP 工具。

前置条件:
  1. Ghidra 已安装并打开目标二进制文件
  2. 在 Ghidra 中运行 ghidra_bridge 服务端 (Script Manager → ghidra_bridge)
  3. pip install ghidra-bridge mcp

启动:
  python ghidra_mcp_server.py

MCP 工具列表:
  - ghidra_decompile(addr)      → 反编译函数为伪C代码
  - ghidra_disassemble(addr)    → 反汇编函数
  - ghidra_xrefs(addr)          → 获取交叉引用
  - ghidra_search(pattern)      → 搜索字节/字符串模式
  - ghidra_rename(addr, name)   → 重命名函数/变量
  - ghidra_set_type(addr, type) → 设置数据类型
  - ghidra_get_segments()       → 获取内存段信息
  - ghidra_get_imports()        → 获取导入函数列表
  - ghidra_get_exports()        → 获取导出函数列表
  - ghidra_list_functions()     → 列出所有函数
  - ghidra_get_strings()        → 获取字符串列表
  - ghidra_analyze_all()        → 运行自动分析

Author: CyberSecuritySkills Team
License: MIT
"""

import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

# 将项目根加入路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ghidra-mcp")

# ============ Ghidra Bridge 连接 ============

_ghidra = None

def get_ghidra():
    """延迟连接 Ghidra Bridge"""
    global _ghidra
    if _ghidra is None:
        try:
            import ghidra_bridge
            host = os.environ.get("GHIDRA_BRIDGE_HOST", "127.0.0.1")
            port = int(os.environ.get("GHIDRA_BRIDGE_PORT", "4768"))
            bridge = ghidra_bridge.GhidraBridge(
                namespace=globals(),
                host=host,
                port=port,
                interactive=False,
            )
            _ghidra = bridge.get_ghidra_api()
            logger.info(f"Connected to Ghidra Bridge at {host}:{port}")
        except Exception as e:
            logger.error(f"Failed to connect to Ghidra: {e}")
            logger.error("Ensure Ghidra is running with ghidra_bridge server")
            raise
    return _ghidra


# ============ MCP Server ============

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    logger.error("mcp package not installed. Run: pip install mcp")
    sys.exit(1)

server = Server("ghidra-mcp")


# ============ MCP 工具实现 ============

@server.tool()
async def ghidra_decompile(addr: str) -> str:
    """反编译指定地址的函数为伪C代码

    Args:
        addr: 函数地址 (hex格式, 如 0x401000 或 401000)
    """
    ghidra = get_ghidra()
    try:
        address = _parse_addr(addr)
        decomp = ghidra.getDecompiler()
        result = decomp.decompileFunction(
            ghidra.getFunctionAt(address),
            0,
            ghidra.getMonitor()
        )
        return result.getDecompiledFunction().getC()
    except Exception as e:
        return f"Error decompiling {addr}: {e}"


@server.tool()
async def ghidra_disassemble(addr: str) -> str:
    """反汇编指定地址的函数

    Args:
        addr: 函数地址 (hex格式)
    """
    ghidra = get_ghidra()
    try:
        address = _parse_addr(addr)
        func = ghidra.getFunctionAt(address)
        if not func:
            return f"No function found at {addr}"

        listing = ghidra.getCurrentProgram().getListing()
        instructions = listing.getInstructions(func.getBody(), True)

        lines = [f"Disassembly of {func.getName()} @ {addr}:"]
        for inst in instructions:
            lines.append(f"  {inst.getAddress()}: {inst.getMnemonicString()} {inst.getOperandRepresentationList(0)}")
        return "\n".join(lines[:500])
    except Exception as e:
        return f"Error disassembling {addr}: {e}"


@server.tool()
async def ghidra_xrefs(addr: str) -> str:
    """获取指定地址的交叉引用 (谁引用了这里/这里引用了谁)

    Args:
        addr: 地址 (hex格式)
    """
    ghidra = get_ghidra()
    try:
        address = _parse_addr(addr)
        refs = ghidra.getReferencesTo(address)

        lines = [f"XRefs to {addr}:"]
        for ref in refs:
            from_addr = ref.getFromAddress()
            lines.append(f"  ← {from_addr} ({ref.getReferenceType()})")

        refs_from = ghidra.getReferencesFrom(address)
        if refs_from:
            lines.append(f"\nXRefs from {addr}:")
            for ref in refs_from:
                to_addr = ref.getToAddress()
                lines.append(f"  → {to_addr} ({ref.getReferenceType()})")

        return "\n".join(lines[:200]) if len(lines) > 1 else f"No XRefs found for {addr}"
    except Exception as e:
        return f"Error getting XRefs for {addr}: {e}"


@server.tool()
async def ghidra_search(pattern: str, search_type: str = "bytes") -> str:
    """搜索字节或字符串

    Args:
        pattern: 搜索模式 (字节: "48 8B 05", 字符串: "password")
        search_type: "bytes" 或 "string"
    """
    ghidra = get_ghidra()
    try:
        results = []
        if search_type == "string":
            import re
            listing = ghidra.getCurrentProgram().getListing()
            data_iter = listing.getDefinedData(True)
            pattern_lower = pattern.lower()
            count = 0
            while data_iter.hasNext() and count < 100:
                data = data_iter.next()
                if data.hasStringValue():
                    val = str(data.getValue())
                    if pattern_lower in val.lower():
                        results.append(f"  {data.getAddress()}: {val}")
                        count += 1
        else:
            import re
            byte_pattern = _parse_bytes(pattern)
            mem = ghidra.getCurrentProgram().getMemory()
            addr_iter = mem.getLoadedAndInitializedAddressSet().getAddresses(True)
            count = 0
            while addr_iter.hasNext() and count < 100:
                addr = addr_iter.next()
                try:
                    mem_bytes = mem.getBytes(addr, len(byte_pattern))
                    if list(mem_bytes) == byte_pattern:
                        results.append(f"  {addr}: match")
                        count += 1
                except Exception:
                    continue

        return "\n".join(results) if results else f"No matches found for '{pattern}'"
    except Exception as e:
        return f"Error searching: {e}"


@server.tool()
async def ghidra_rename(addr: str, new_name: str) -> str:
    """重命名函数或变量

    Args:
        addr: 地址 (hex格式)
        new_name: 新名称
    """
    ghidra = get_ghidra()
    try:
        address = _parse_addr(addr)
        func = ghidra.getFunctionAt(address)
        if func:
            old_name = func.getName()
            func.setName(new_name, ghidra.getSourceType("USER_DEFINED"))
            return f"Renamed function @ {addr}: {old_name} → {new_name}"

        sym = ghidra.getSymbolAt(address)
        if sym:
            old_name = sym.getName()
            sym.setName(new_name, ghidra.getSourceType("USER_DEFINED"))
            return f"Renamed symbol @ {addr}: {old_name} → {new_name}"

        return f"No function or symbol found at {addr}"
    except Exception as e:
        return f"Error renaming at {addr}: {e}"


@server.tool()
async def ghidra_list_functions(filter: str = "") -> str:
    """列出所有函数

    Args:
        filter: 可选过滤关键词 (函数名)
    """
    ghidra = get_ghidra()
    try:
        fm = ghidra.getFunctionManager()
        funcs = fm.getFunctions(True)
        lines = []
        filter_lower = filter.lower()
        count = 0
        for func in funcs:
            name = func.getName()
            if filter_lower and filter_lower not in name.lower():
                continue
            addr = func.getEntryPoint()
            size = func.getBody().getNumAddresses()
            lines.append(f"  {addr}: {name} ({size} bytes)")
            count += 1
            if count >= 200:
                lines.append(f"  ... (showing first 200 of many)")
                break
        return "\n".join(lines) if lines else f"No functions found" + (f" matching '{filter}'" if filter else "")
    except Exception as e:
        return f"Error listing functions: {e}"


@server.tool()
async def ghidra_get_strings(filter: str = "") -> str:
    """获取程序中的字符串列表

    Args:
        filter: 可选过滤关键词
    """
    ghidra = get_ghidra()
    try:
        listing = ghidra.getCurrentProgram().getListing()
        data_iter = listing.getDefinedData(True)
        lines = []
        filter_lower = filter.lower()
        count = 0
        while data_iter.hasNext() and count < 200:
            data = data_iter.next()
            if data.hasStringValue():
                val = str(data.getValue())
                if filter_lower and filter_lower not in val.lower():
                    continue
                lines.append(f"  {data.getAddress()}: {val}")
                count += 1
        return "\n".join(lines) if lines else "No strings found"
    except Exception as e:
        return f"Error getting strings: {e}"


def _parse_addr(addr_str: str):
    """解析地址字符串"""
    ghidra = get_ghidra()
    addr_str = addr_str.strip()
    if addr_str.startswith("0x") or addr_str.startswith("0X"):
        addr_str = addr_str[2:]
    addr_int = int(addr_str, 16)
    return ghidra.getAddressFactory().getDefaultAddressSpace().getAddress(addr_int)


def _parse_bytes(pattern: str) -> list:
    """解析字节模式字符串 "48 8B 05" → [0x48, 0x8B, 0x05]"""
    return [int(b, 16) for b in pattern.strip().split()]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
