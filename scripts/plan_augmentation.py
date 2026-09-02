#!/usr/bin/env python
"""Create SignNet-1M augmentation jobs from a JSONL clip manifest."""

from __future__ import annotations

import argparse
import hashlib
import random
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


DEFAULT_SUFFIX = {
    "render_fixed_viewpoint": "fixed_viewpoint_video.mp4",
    "render_dynamic_viewpoint": "dynamic_viewpoint_video.mp4",
    "render_cross_identity": "cross_identity_video.mp4",
}


def planned_output(clip_id: str, mode: str, suffix: str, level_name: str | None = None) -> str:
    """Relative output path, laid out exactly like the public release.

    Fixed-viewpoint renders are grouped by level at the top of the tree, so a
    locally produced tree is interchangeable with a downloaded one:

        level01/<clip_id>/render_fixed_viewpoint/<clip_id>/<clip_id>_fixed_viewpoint_video.mp4
    """

    path = Path(level_name) if level_name else Path(".")
    return str(path / clip_id / mode / clip_id / f"{clip_id}_{suffix}")


def sample_level_pose(clip_id: str, level: dict, seed: int) -> dict:
    """Draw yaw / pitch / zoom for one (clip, level) pair.

    The draw is uniform inside the level envelope and seeded by the clip id, so
    the same manifest and config always expand to the same jobs. A level may
    instead pin explicit yaw / pitch / zoom values, in which case they are used
    as given.
    """

    if "yaw" in level or "pitch" in level or "zoom" in level:
        return {
            "yaw": float(level.get("yaw", 0.0)),
            "pitch": float(level.get("pitch", 0.0)),
            "zoom": float(level.get("zoom", 1.0)),
            "seed": seed,
        }

    digest = hashlib.md5(f"{seed}:{clip_id}:{level['name']}".encode("utf-8")).hexdigest()
    clip_seed = int(digest[:16], 16)
    rng = random.Random(clip_seed)
    yaw_max = float(level["yaw_abs_max"])
    pitch_max = float(level["pitch_abs_max"])
    return {
        "yaw": rng.uniform(-yaw_max, yaw_max),
        "pitch": rng.uniform(-pitch_max, pitch_max),
        "zoom": rng.uniform(float(level["zoom_min"]), float(level["zoom_max"])),
        "seed": clip_seed,
    }


def main() -> None:
    args = parse_args()
    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    rows = list(read_jsonl(args.manifest))
    jobs = []

    if "fixed_viewpoint" in args.modes:
        fixed = config["render_axes"]["fixed_viewpoint"]
        suffix = fixed.get("output_suffix", DEFAULT_SUFFIX["render_fixed_viewpoint"])
        base_seed = int(fixed.get("seed", 42))
        for row in rows:
            for level in fixed["levels"]:
                pose = sample_level_pose(row["clip_id"], level, base_seed)
                jobs.append(
                    {
                        "clip_id": row["clip_id"],
                        "mode": "fixed_viewpoint",
                        "tracked_dir": row["tracked_dir"],
                        "level": level["name"],
                        "seed": pose["seed"],
                        "yaw": pose["yaw"],
                        "pitch": pose["pitch"],
                        "zoom": pose["zoom"],
                        "output_video": planned_output(
                            row["clip_id"], "render_fixed_viewpoint", suffix, level["name"]
                        ),
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
                    "output_video": planned_output(
                        row["clip_id"],
                        "render_dynamic_viewpoint",
                        dyn.get("output_suffix", DEFAULT_SUFFIX["render_dynamic_viewpoint"]),
                    ),
                }
            )

    if "cross_identity" in args.modes:
        cross = config["render_axes"]["cross_identity"]
        for row in rows:
            if not row.get("source_identity_dir"):
                continue
            jobs.append(
                {
                    "clip_id": row["clip_id"],
                    "mode": "cross_identity",
                    "tracked_dir": row["tracked_dir"],
                    "source_identity_dir": row["source_identity_dir"],
                    "keep_source_camera": cross["keep_source_camera"],
                    "output_video": planned_output(
                        row["clip_id"],
                        "render_cross_identity",
                        cross.get("output_suffix", DEFAULT_SUFFIX["render_cross_identity"]),
                    ),
                }
            )

    count = write_jsonl(args.output, jobs)
    print(f"Wrote {count} jobs to {args.output}")


if __name__ == "__main__":
    main()
