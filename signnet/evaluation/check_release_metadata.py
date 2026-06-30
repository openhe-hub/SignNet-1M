#!/usr/bin/env python
"""Validate SignNet-1M release metadata JSONL files."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from signnet.augmentation.metadata import read_jsonl


REQUIRED_BY_KIND = {
    "render": {"clip_id", "mode", "tracked_dir", "output_video"},
    "post": {"input_video", "output_video", "mode", "aug_id", "aug_name", "seed"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--kind", choices=sorted(REQUIRED_BY_KIND), required=True)
    parser.add_argument("--check-files", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    required = REQUIRED_BY_KIND[args.kind]
    rows = list(read_jsonl(args.metadata))
    missing = []
    modes = Counter()
    missing_files = []

    for index, row in enumerate(rows, start=1):
        absent = required - set(row)
        if absent:
            missing.append((index, sorted(absent)))
        if "mode" in row:
            modes[row["mode"]] += 1
        if args.check_files and row.get("output_video") and not Path(row["output_video"]).exists():
            missing_files.append(row["output_video"])

    print(f"rows={len(rows)}")
    print("modes=" + ", ".join(f"{k}:{v}" for k, v in sorted(modes.items())))

    if missing:
        for index, absent in missing[:20]:
            print(f"[MISSING] row={index} fields={absent}")
        raise SystemExit(2)
    if missing_files:
        for path in missing_files[:20]:
            print(f"[MISSING_FILE] {path}")
        raise SystemExit(3)


if __name__ == "__main__":
    main()
