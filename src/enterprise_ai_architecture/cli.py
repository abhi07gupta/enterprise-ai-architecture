from __future__ import annotations

import argparse
import json
from pathlib import Path

from .assessment import assess


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and assess an Enterprise AI Decision Canvas")
    parser.add_argument("canvas", type=Path, help="path to a JSON decision canvas")
    parser.add_argument("--compact", action="store_true", help="emit one-line JSON")
    args = parser.parse_args(argv)
    try:
        canvas = json.loads(args.canvas.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    result = assess(canvas).to_dict()
    print(json.dumps(result, indent=None if args.compact else 2, sort_keys=True))
    return 2 if result["blockers"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
