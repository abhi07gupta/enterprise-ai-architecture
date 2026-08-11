from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import ScenarioError, analyze_scenario


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze a synthetic autonomous-network incident")
    parser.add_argument("scenario", type=Path, help="path to a scenario JSON file")
    parser.add_argument("--compact", action="store_true", help="emit one-line JSON")
    args = parser.parse_args(argv)
    try:
        scenario = json.loads(args.scenario.read_text(encoding="utf-8"))
        report = analyze_scenario(scenario).to_dict()
    except (OSError, json.JSONDecodeError, ScenarioError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=None if args.compact else 2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
