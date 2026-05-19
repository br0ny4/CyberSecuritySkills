#!/usr/bin/env python3
"""
性能基准测试 — Benchmark Suite
===================================
对 DeepSeek V4 优化器、技能索引系统、适配器接口进行性能基准测试。

指标:
  - 技能扫描吞吐量 (skills/sec)
  - 单技能加载延迟 (ms)
  - 批量搜索响应时间 (ms)
  - Token 节省率 (%)
  - 缓存命中率 (%)
  - 重试恢复时间 (ms)

用法:
  python scripts/benchmark.py --iterations 100
  python scripts/benchmark.py --quick      # 快速测试 (10 iterations)

Author: Unified Security Skills Team
License: MIT
"""

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from adapters.deepseek_v4.optimizer import (
    DeepSeekSkillOptimizer,
    DeepSeekOptimizationConfig,
    OptimizationStrategy,
)
from integration.skill_router import SkillRouter, RouteIntent
from integration.prompt_builder import PromptBuilder

# 模拟技能数据
SAMPLE_SKILLS = [
    {
        "name": f"cybersecurity-skill-{i:04d}",
        "description": f"Security skill #{i} for penetration testing and vulnerability assessment",
        "subdomain": ["digital-forensics", "threat-hunting", "incident-response",
                       "cloud-security", "malware-analysis"][i % 5],
        "difficulty": "★★★☆☆",
        "mitre_attack": [f"T{1000 + i % 50:04d}"],
        "tags": ["security", "test"],
        "estimated_tokens": 1500 + (i % 3) * 500,
    }
    for i in range(500)
]

SAMPLE_CONTENT = """---
name: test-skill
description: Test skill for benchmarking
domain: cybersecurity
subdomain: digital-forensics
---
## Workflow
### Step 1: Initial Scan
Run the following commands to perform initial system scan:
```bash
vol -f memory.raw windows.pslist
vol -f memory.raw windows.psscan
```
### Step 2: Network Analysis
Analyze network connections:
```bash
vol -f memory.raw windows.netscan | grep ESTABLISHED
```
### Step 3: Malware Detection
Scan with YARA rules:
```bash
vol -f memory.raw yarascan --yara-file /opt/rules/malware.yar
```
## Verification
- Confirm process list anomalies
- Verify network connection patterns
- Validate YARA matches
## Output Format
```json
{"findings": [], "status": "complete"}
```
""" * 5  # 增大到 ~2500 tokens 模拟真实技能


class Benchmark:
    """性能基准测试"""

    def __init__(self, iterations: int = 100):
        self.iterations = iterations
        self.results: Dict[str, Any] = {}

    def run_all(self) -> Dict[str, Any]:
        print(f"🏃 性能基准测试开始 ({self.iterations} iterations)...\n")
        self._bench_skill_scan()
        self._bench_skill_load()
        self._bench_skill_compress()
        self._bench_skill_search()
        self._bench_cache_performance()
        self._bench_router_performance()
        self._bench_prompt_builder()
        self._print_summary()
        return self.results

    def _bench_skill_scan(self):
        """测试技能扫描吞吐量"""
        optimizer = DeepSeekSkillOptimizer()
        start = time.perf_counter()
        for i in range(self.iterations):
            tokens = optimizer.estimate_skill_tokens(SAMPLE_CONTENT)
        elapsed = time.perf_counter() - start
        rate = self.iterations / elapsed
        self.results["token_estimation"] = {
            "ops_per_sec": round(rate, 1),
            "avg_ms": round(elapsed / self.iterations * 1000, 2),
        }
        print(f"  📊 Token估算: {rate:.0f} ops/sec ({elapsed/self.iterations*1000:.2f}ms avg)")

    def _bench_skill_load(self):
        """测试技能压缩性能"""
        optimizer = DeepSeekSkillOptimizer()
        strategies = list(OptimizationStrategy)

        for strat in strategies:
            start = time.perf_counter()
            for _ in range(self.iterations):
                optimizer.compress_skill_for_context(SAMPLE_CONTENT, strat)
            elapsed = time.perf_counter() - start
            self.results[f"compress_{strat.value}"] = {
                "ops_per_sec": round(self.iterations / elapsed, 1),
                "avg_ms": round(elapsed / self.iterations * 1000, 2),
            }

        print(f"  📦 压缩性能 (avg ms):")
        for strat in strategies:
            key = f"compress_{strat.value}"
            print(f"     {strat.value}: {self.results[key]['avg_ms']}ms")

    def _bench_skill_compress(self):
        """测试 Token 节省率"""
        optimizer = DeepSeekSkillOptimizer()
        original_tokens = optimizer.estimate_skill_tokens(SAMPLE_CONTENT)

        for strat in list(OptimizationStrategy):
            compressed = optimizer.compress_skill_for_context(SAMPLE_CONTENT, strat)
            compressed_tokens = optimizer.estimate_skill_tokens(compressed)
            saved = original_tokens - compressed_tokens
            rate = saved / original_tokens * 100 if original_tokens > 0 else 0
            self.results[f"token_save_{strat.value}"] = {
                "original": original_tokens,
                "compressed": compressed_tokens,
                "saved": saved,
                "saved_pct": round(rate, 1),
            }

        print(f"  💰 Token 节省率:")
        for strat in list(OptimizationStrategy):
            key = f"token_save_{strat.value}"
            print(f"     {strat.value}: {self.results[key]['saved_pct']}% ({self.results[key]['compressed']} tokens)")

    def _bench_skill_search(self):
        """测试搜索性能"""
        optimizer = DeepSeekSkillOptimizer()
        # 模拟 754 skill index
        skill_names = [f"skill-{i:04d}" for i in range(self.iterations * 7)]

        start = time.perf_counter()
        all_metas = SAMPLE_SKILLS[:min(len(skill_names), 500)]
        plan = optimizer.progressive_load_plan(skill_names, all_metas)
        elapsed = time.perf_counter() - start

        self.results["search_progressive"] = {
            "total_skills": len(skill_names),
            "batches": len(plan),
            "batch_sizes": [len(b) for b in plan],
            "total_ms": round(elapsed * 1000, 2),
        }
        print(f"  🔍 渐进式加载: {len(skill_names)} skills → {len(plan)} batches ({elapsed*1000:.2f}ms)")

    def _bench_cache_performance(self):
        """测试缓存性能"""
        optimizer = DeepSeekSkillOptimizer()
        optimizer.clear_cache()

        # 填充缓存
        for i in range(min(self.iterations, 500)):
            optimizer.set_cached_skill(f"skill-{i:04d}", {"data": f"content-{i}"})

        # 测试命中率
        hits = 0
        misses = 0
        start = time.perf_counter()
        for i in range(self.iterations):
            # 80% 命中, 20% 未命中
            if i % 5 != 0:
                result = optimizer.get_cached_skill(f"skill-{i % 500:04d}")
                if result:
                    hits += 1
                else:
                    misses += 1
            else:
                result = optimizer.get_cached_skill(f"skill-new-{i:04d}")
                misses += 1
        elapsed = time.perf_counter() - start

        self.results["cache"] = {
            "hits": hits,
            "misses": misses,
            "hit_rate": round(hits / self.iterations * 100, 1),
            "lookup_ms": round(elapsed / self.iterations * 1000, 3),
        }
        print(f"  🗄️  缓存: {self.results['cache']['hit_rate']}% 命中率, {self.results['cache']['lookup_ms']}ms/lookup")

    def _bench_router_performance(self):
        """测试路由性能"""
        router = SkillRouter()
        queries = [
            "内存取证分析",
            "ransomware incident response",
            "云安全合规审计 等保2.0",
            "漏洞扫描和利用",
            "威胁情报分析 APT",
            "工控安全 SCADA",
            "零信任架构实施",
            "API安全测试",
            "钓鱼邮件防护",
            "容器安全 Kubernetes",
        ]

        start = time.perf_counter()
        for q in queries[:self.iterations % 10 + 1]:
            intent = router.parse_intent(q)
            domains = router.extract_subdomains(q)
            decision = router.decide(q, [])
        elapsed = time.perf_counter() - start

        rounds = min(self.iterations, 10)
        self.results["router"] = {
            "queries_per_sec": round(rounds / elapsed, 1) if elapsed > 0 else 0,
            "avg_ms": round(elapsed / rounds * 1000, 2) if rounds > 0 else 0,
        }
        print(f"  🧭 路由: {self.results['router']['avg_ms']}ms/query")

    def _bench_prompt_builder(self):
        """测试 Prompt 构建性能"""
        from adapters.base.adapter_base import SkillMetadata

        metas = [
            SkillMetadata(
                name=f"skill-{i:04d}",
                description=f"Security skill {i}",
                subdomain="digital-forensics",
                difficulty="★★★☆☆",
                mitre_attack=["T1003"],
                estimated_tokens=2000,
            )
            for i in range(5)
        ]

        builder = PromptBuilder()
        start = time.perf_counter()
        for _ in range(min(self.iterations, 50)):
            builder.build_system_prompt(metas)
        elapsed = time.perf_counter() - start

        rounds = min(self.iterations, 50)
        self.results["prompt_build"] = {
            "prompts_per_sec": round(rounds / elapsed, 1) if elapsed > 0 else 0,
            "avg_ms": round(elapsed / rounds * 1000, 2) if rounds > 0 else 0,
        }
        print(f"  📝 Prompt构建: {self.results['prompt_build']['avg_ms']}ms/prompt")

    def _print_summary(self):
        print(f"\n{'='*60}")
        print(f"  ✅ 基准测试完成")
        print(f"{'='*60}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="性能基准测试")
    parser.add_argument("--iterations", "-n", type=int, default=100, help="迭代次数 (default: 100)")
    parser.add_argument("--quick", "-q", action="store_true", help="快速测试 (10 iterations)")
    parser.add_argument("--output", "-o", help="输出 JSON 结果文件")
    args = parser.parse_args()

    iterations = 10 if args.quick else args.iterations
    bench = Benchmark(iterations=iterations)
    results = bench.run_all()

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))
        print(f"\n结果已保存: {output_path}")


if __name__ == "__main__":
    main()
