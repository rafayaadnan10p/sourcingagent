r"""
Quick terminal test for websearch.py (Serper).

Usage (from backend/ folder):
    .\.venv\Scripts\python.exe scripts\test_websearch.py
    .\.venv\Scripts\python.exe scripts\test_websearch.py --query "site:linkedin.com/in Python developer"
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.websearch import run_searches

SAMPLE_QUERY = (
    'site:linkedin.com/in ("Sr QA Engineer" OR "SDET") AND Islamabad '
    'AND Python AND pytest AND "test frameworks"'
)


def main():
    parser = argparse.ArgumentParser(description="Test websearch module")
    parser.add_argument("--query", default=SAMPLE_QUERY, help="Search query to run")
    args = parser.parse_args()

    print(f"Query: {args.query}\n")
    print("Calling Serper API...\n")

    results = run_searches([args.query])

    print(f"Got {len(results)} result(s):\n")
    for r in results:
        print(f"  [{r['position']}] {r['title']}")
        print(f"       {r['url']}")
        print(f"       {r['snippet'][:120]}...")
        print()

    print("── Raw JSON ──────────────────────────────────────────────────────────")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
