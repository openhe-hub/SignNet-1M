#!/usr/bin/env python
"""Apply deterministic SignNet-1M post-rendering augmentations."""

from __future__ import annotations

import argparse
import traceback
from pathlib import Path

from tqdm import tqdm

from signnet.augmentation.metadata import append_jsonl
from signnet.augmentation.post_rendering import (
    AUGMENTATIONS,
    TEMPORAL_AUGMENTATIONS,
    augment_video,
    pick_aug,
    pick_temporal_aug,
    temporal_augment_video,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", required=True, help="Root containing rendered MP4 files.")
    parser.add_argument("--output-root", required=True, help="Root for augmented MP4 files.")
    parser.add_argument("--num-tasks", type=int, required=True, help="Total number of parallel shards.")
    parser.add_argument("--task-id", type=int, required=True, help="Current shard id, zero based.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--mode", choices=["spatial_color", "temporal"], default="spatial_color")
    parser.add_argument("--metadata-name", default=None)
    return parser.parse_args()


def output_path(input_root: Path, output_root: Path, video_path: Path) -> Path:
    return output_root / video_path.relative_to(input_root)


def main() -> None:
    args = parse_args()
    input_root = Path(args.input_root)
    output_root = Path(args.output_root)
    videos = sorted(input_root.rglob("*.mp4"))
    shard = videos[args.task_id :: args.num_tasks]
    metadata_name = args.metadata_name or f"{args.mode}_params.jsonl"
    metadata_path = output_root / metadata_name

    processed = skipped = errors = 0
    for video_path in tqdm(shard, desc=f"task-{args.task_id}", unit="video"):
        out_path = output_path(input_root, output_root, video_path)
        clip_key = str(video_path.relative_to(input_root))
        if out_path.exists():
            skipped += 1
            continue
        try:
            if args.mode == "spatial_color":
                aug_id = pick_aug(clip_key, seed=args.seed)
                result = augment_video(video_path, out_path, aug_id)
                aug_name = AUGMENTATIONS[aug_id]["name"]
            else:
                aug_id = pick_temporal_aug(clip_key, seed=args.seed)
                result = temporal_augment_video(video_path, out_path, aug_id)
                aug_name = TEMPORAL_AUGMENTATIONS[aug_id]["name"]
            append_jsonl(
                metadata_path,
                {
                    "input_video": str(video_path),
                    "output_video": str(out_path),
                    "mode": args.mode,
                    "aug_id": result.aug_id,
                    "aug_name": aug_name,
                    "seed": args.seed,
                    "task_id": args.task_id,
                },
            )
            processed += 1
        except Exception as exc:
            print(f"[ERROR] {video_path}: {exc}", flush=True)
            traceback.print_exc()
            errors += 1

    print(f"Processed={processed} skipped={skipped} errors={errors}")


if __name__ == "__main__":
    main()
