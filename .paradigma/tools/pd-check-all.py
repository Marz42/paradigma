#!/usr/bin/env python3
"""Run all Paradigma quality-gate checks in sequence.

Equivalent to the Update Phase command sequence:
  pd-lint-okf.py --strict
  pd-check-links.py
  pd-sync-index.py --check
  pd-check-hot-size.py

Stops on the first failure unless --keep-going is passed.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / ".paradigma" / "tools"

STEPS = [
    ("lint", "pd-lint-okf.py", ["--strict"]),
    ("links", "pd-check-links.py", []),
    ("index", "pd-sync-index.py", ["--check"]),
    ("hot-size", "pd-check-hot-size.py", []),
]


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Run all Paradigma quality-gate checks.")
    parser.add_argument("--keep-going", action="store_true", help="run all steps even after a failure")
    args = parser.parse_args()

    failures = 0
    for name, script, extra_args in STEPS:
        print(f"--- {name} ({script}) ---")
        cmd = [sys.executable, str(TOOLS / script)] + extra_args
        result = subprocess.run(cmd, cwd=str(ROOT))
        if result.returncode != 0:
            failures += 1
            print(f"  FAILED (exit {result.returncode})")
            if not args.keep_going:
                print(f"\n{failures}/{len(STEPS)} check(s) failed (stopped early).")
                return 1
        else:
            print(f"  OK")
        print()

    if failures:
        print(f"{failures}/{len(STEPS)} check(s) failed.")
        return 1
    print(f"All {len(STEPS)} checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
