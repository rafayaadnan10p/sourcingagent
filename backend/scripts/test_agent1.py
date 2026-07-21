r"""
Quick terminal test for Agent 1 — search string generation.

Usage (from backend/ folder):
    .\.venv\Scripts\python.exe scripts\test_agent1.py
    .\.venv\Scripts\python.exe scripts\test_agent1.py --platform linkedin
    .\.venv\Scripts\python.exe scripts\test_agent1.py --platform github

Paste your own JD text into SAMPLE_JD below, or pass --jd-file path/to/file.txt
"""

import sys
import json
import argparse
from pathlib import Path

# Make sure the backend/ root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.search_string_agent import generate_search_strings

# ── Sample JD (Sr QA Engineer / SDET) ─────────────────────────────────────────
SAMPLE_JD = """
Role: Sr QA Engineer (SDET)
Level: L3 — Lead
Experience: 5–8 years
Location: Islamabad, Pakistan (Onsite)

Role Summary:
You own the test strategy and quality bar for the AIX platform. You design the SDET framework
that every squad uses, author the cross-layer integration and end-to-end test suites, and set
the quality gates that code must pass before it is allowed into a release bundle.

Key Responsibilities:
- Test strategy — define the platform test pyramid (unit, integration, contract, E2E,
  performance, chaos, security)
- Automation framework — design and maintain the pytest-driven SDET framework
- End-to-end suites — author cross-layer E2E tests (ingest → ontology → agent → governance → audit)
- Contract testing — Pact or equivalent; gate merges on contract compatibility
- Performance testing — k6, Locust, JMeter against 200-concurrent-user target
- Quality gates — merge-gate and release-gate criteria in CI; flaky-test triage
- Agent evaluation — integrate model/agent eval suites into the release gate
- Team leadership — technically lead 1–2 QA engineers

Required Qualifications:
- 5–8 years in SDET or test-automation with platform-level ownership
- Strong Python — pytest, fixtures, parametrisation, plugins
- Experience designing test frameworks used by multiple teams
- Hands-on with contract testing (Pact, Spring Cloud Contract) and API testing (REST, GraphQL, gRPC)
- Performance testing with k6, Locust, JMeter, or Gatling
- Strong Kubernetes-native testing — ephemeral test environments, Helm-deployed stacks
- CI/CD pipeline integration — quality gates, flaky-test detection, reporting

Nice to Have:
- Experience testing LLM or agent systems
- Chaos engineering (Chaos Mesh, Litmus, Gremlin)
- Security testing (DAST, SAST, dependency scanning)
""".strip()


def main():
    parser = argparse.ArgumentParser(description="Test Agent 1 — search string generation")
    parser.add_argument(
        "--platform",
        default="linkedin",
        choices=["all", "linkedin", "github", "upwork", "fiverr", "behance"],
        help="Platform scope (default: linkedin)",
    )
    parser.add_argument(
        "--jd-file",
        default=None,
        help="Path to a plain-text file containing the JD (overrides built-in sample)",
    )
    args = parser.parse_args()

    jd_text = SAMPLE_JD
    if args.jd_file:
        jd_text = Path(args.jd_file).read_text(encoding="utf-8")
        print(f"Using JD from file: {args.jd_file}\n")
    else:
        print("Using built-in sample JD (Sr QA Engineer / SDET)\n")

    print(f"Platform scope: {args.platform}")
    print("Calling Agent 1... (this hits the OpenAI API)\n")

    results = generate_search_strings(jd_text, platform_scope=args.platform)

    print(f"Got {len(results)} search string(s):\n")
    for i, item in enumerate(results, 1):
        print(f"  [{i}] {item['label']}")
        print(f"       {item['query']}")
        print()

    # Also dump raw JSON so you can inspect the full structure
    print("── Raw JSON ──────────────────────────────────────────────────────────")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
