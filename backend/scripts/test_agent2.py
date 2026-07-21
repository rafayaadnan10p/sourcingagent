r"""
Quick terminal test for Agent 2 — relevance scoring.

Runs Agent 1 to get search strings, then websearch to get results,
then Agent 2 to score and rank them. Full end-to-end pipeline test
(no database required).

Usage (from backend/ folder):
    .\.venv\Scripts\python.exe scripts\test_agent2.py
    .\.venv\Scripts\python.exe scripts\test_agent2.py --platform linkedin
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.search_string_agent import generate_search_strings
from app.services.websearch import run_searches
from app.agents.relevance_agent import score_results

SAMPLE_JD = """
Role: Sr QA Engineer (SDET)
Level: L3 — Lead | Experience: 5–8 years | Location: Islamabad, Pakistan (Onsite)

You own the test strategy and quality bar for the AIX platform. You design the SDET
framework, author cross-layer E2E tests, and set quality gates for release.

Required: Strong Python (pytest), platform-level test framework design, contract testing
(Pact), performance testing (k6/Locust/JMeter), Kubernetes-native testing, CI/CD gates.

Nice to have: LLM/agent eval, chaos engineering, security testing (DAST/SAST).
""".strip()


def main():
    parser = argparse.ArgumentParser(description="Full pipeline test (no DB)")
    parser.add_argument(
        "--platform", default="linkedin",
        choices=["all", "linkedin", "github", "upwork", "fiverr", "behance"],
    )
    args = parser.parse_args()

    print("=== Step 1: Generating search strings ===")
    search_strings = generate_search_strings(SAMPLE_JD, platform_scope=args.platform)
    print(f"Got {len(search_strings)} search string(s)")
    for s in search_strings:
        print(f"  • [{s['label']}] {s['query'][:80]}...")

    print("\n=== Step 2: Running web searches ===")
    queries = [s["query"] for s in search_strings]
    results = run_searches(queries)
    print(f"Got {len(results)} result(s) from Serper")

    print("\n=== Step 3: Scoring relevance ===")
    ranked = score_results(SAMPLE_JD, results)
    print(f"Scored and ranked {len(ranked)} result(s)\n")

    print("── Top 10 Shortlist ──────────────────────────────────────────────────")
    shortlist = [r for r in ranked if r.get("final_rank") is not None]
    for r in shortlist:
        print(f"  #{r['final_rank']:2d}  [{r['relevance_score']:.1f}/10]  {r['title']}")
        print(f"        {r['url']}")
        print(f"        {r['relevance_reasoning']}")
        print()

    print("── Raw JSON ──────────────────────────────────────────────────────────")
    print(json.dumps(shortlist, indent=2))


if __name__ == "__main__":
    main()
