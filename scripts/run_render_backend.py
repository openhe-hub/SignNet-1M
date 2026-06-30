#!/usr/bin/env python
"""Run SignNet-1M render jobs with a compatible backend adapter."""

from __future__ import annotations

import argparse
import importlib

from signnet.augmentation.metadata import read_jsonl
from signnet.augmentation.render_pipeline import RenderJob, run_render_jobs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", required=True, help="Render jobs JSONL from plan_augmentation.py.")
    parser.add_argument("--backend-module", required=True, help="Module exposing create_backend(model_path, device).")
    parser.add_argument("--model-path", required=True, help="Path passed to the backend adapter.")
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--metadata", default=None)
    parser.add_argument("--device", default="cuda:0")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    module = importlib.import_module(args.backend_module)
    backend = module.create_backend(model_path=args.model_path, device=args.device)
    jobs = [RenderJob(**row) for row in read_jsonl(args.jobs)]
    metadata_path = args.metadata or f"{args.output_root}/render_metadata.jsonl"
    run_render_jobs(jobs=jobs, backend=backend, output_root=args.output_root, metadata_path=metadata_path)


if __name__ == "__main__":
    main()
