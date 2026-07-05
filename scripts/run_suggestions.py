#!/usr/bin/env python3
"""Run skillctl `suggest` over the example corpus' test prompts and write a summary.

Regenerates eval/example-rules/{suggest-output.json,suggest-summary.md} — a quick,
human-readable sanity check that the deterministic matcher fires sensible rules and
bundles for realistic prompts. Build the corpus first:
    python scripts/gen_example_corpus.py && skillctl build eval/example-rules/.skillctl/rules
"""

import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "eval" / "example-rules"


def main() -> None:
    prompts = [p.strip() for p in (BASE / "test_prompts.txt").read_text().splitlines() if p.strip()]
    results = {}
    md_lines = ["# Suggestion Summary\n"]
    env = {**os.environ, "SKILLCTL_HOME": str(BASE / ".skillctl")}

    for p in prompts:
        res = subprocess.run(
            [sys.executable, "-m", "skillctl._cli", "suggest", "--json", p],
            env=env, capture_output=True, text=True,
        )
        try:
            data = json.loads(res.stdout)
        except json.JSONDecodeError:
            continue
        results[p] = data
        top_bundle = data["bundles"][0]["name"] if data.get("bundles") else "None"
        md_lines.append(f"## Prompt: {p}")
        md_lines.append(f"- **Top bundle**: {top_bundle}")
        md_lines.append("- **Top 3 rules**:")
        for i, r in enumerate(data.get("rules", [])[:3], 1):
            md_lines.append(f"  {i}. `{r['id']}` (tier {r['tier']}, triggers: {', '.join(r['triggers'])})")
        md_lines.append("")

    (BASE / "suggest-output.json").write_text(json.dumps(results, indent=2))
    (BASE / "suggest-summary.md").write_text("\n".join(md_lines))
    print(f"Wrote suggestions for {len(results)} prompts → {BASE}")


if __name__ == "__main__":
    main()
