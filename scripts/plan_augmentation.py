#!/usr/bin/env python
"""Create SignNet-1M augmentation jobs from a JSONL clip manifest."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from signnet.augmentation.metadata import read_jsonl, write_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Input clip manifest JSONL.")
    parser.add_argument("--config", required=True, help="SignNet augmentation YAML.")
    parser.add_argument("--output", required=True, help="Output job JSONL.")
    parser.add_argument(
        "--modes",
        nargs="+",
        default=["fixed_viewpoint", "dynamic_viewpoint", "cross_identity"],
        choices=["fixed_viewpoint", "dynamic_viewpoint", "cross_identity"],
    )
    return parser.parse_args()


def planned_output(clip_id: str, mode: str, level_name: str | None = None) -> str:
    level_part = f"_{level_name}" if level_name else ""
    filename = f"{clip_id}{level_part}_video.mp4"
    return str(Path(clip_id) / mode / clip_id / filename)


def main() -> None:
    args = parse_args()
    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    rows = list(read_jsonl(args.manifest))
    jobs = []

    if "fixed_viewpoint" in args.modes:
        for row in rows:
            for level in config["render_axes"]["fixed_viewpoint"]["levels"]:
                jobs.append(
                    {
                        "clip_id": row["clip_id"],
                        "mode": "fixed_viewpoint",
                        "tracked_dir": row["tracked_dir"],
                        "level": level["name"],
                        "yaw": level["yaw"],
                        "pitch": level["pitch"],
                        "zoom": level["zoom"],
                        "output_video": planned_output(row["clip_id"], "render_fixed_viewpoint", level["name"]),
                    }
                )

    if "dynamic_viewpoint" in args.modes:
        dyn = config["render_axes"]["dynamic_viewpoint"]
        for row in rows:
            jobs.append(
                {
                    "clip_id": row["clip_id"],
                    "mode": "dynamic_viewpoint",
                    "tracked_dir": row["tracked_dir"],
                    "dyn_yaw_range": dyn["yaw_range"],
                    "dyn_pitch_range": dyn["pitch_range"],
                    "dyn_zoom_range": dyn["zoom_range"],
                    "dyn_freq": dyn["frequency"],
                    "output_video": planned_output(row["clip_id"], "render_dynamic_viewpoint"),
                }
            )

    if "cross_identity" in args.modes:
        for row in rows:
            if not row.get("source_identity_dir"):
                continue
            jobs.append(
                {
                    "clip_id": row["clip_id"],
                    "mode": "cross_identity",
                    "tracked_dir": row["tracked_dir"],
                    "source_identity_dir": row["source_identity_dir"],
                    "keep_source_camera": config["render_axes"]["cross_identity"]["keep_source_camera"],
                    "output_video": planned_output(row["clip_id"], "render_cross_identity"),
                }
            )

    count = write_jsonl(args.output, jobs)
    print(f"Wrote {count} jobs to {args.output}")


if __name__ == "__main__":
    main()
