# SignNet-1M Reference Code

This directory contains the public reference implementation for the ECCV 2026
SignNet-1M augmentation pipeline.

SignNet-1M augments sign-language videos along four release axes:

- 3DGS viewpoint synthesis: fixed yaw, pitch, zoom, and dynamic camera orbits.
- Cross-identity reenactment: source signer appearance driven by target motion.
- Post-rendering augmentation: deterministic geometric, photometric, temporal,
  and capture-degradation transforms.
- Background replacement: planned for a follow-up code release after packaging
  the background-editing dependencies and model checkpoints.

The code here is intentionally scoped to the reproducible SignNet-1M pipeline
logic: camera schedules, render orchestration, deterministic post-rendering
augmentations, metadata writing, and sanity checks. Large datasets, trained
weights, tracking assets, 3DGS backend internals, and background-editing weights
are not included in this directory.

## Layout

```text
codebase/
  configs/
    signnet_augmentation.yaml       # Paper-facing augmentation axes and defaults
  scripts/
    plan_augmentation.py            # Expand a clip manifest into planned jobs
    run_post_rendering.py           # Apply deterministic video augmentations
    run_render_backend.py           # Drive a compatible 3DGS avatar backend
  signnet/
    augmentation/
      camera.py                     # Fixed and dynamic camera pose schedules
      post_rendering.py             # OpenCV post-rendering transforms
      render_pipeline.py            # Backend-agnostic render orchestration
      metadata.py                   # JSONL metadata helpers
    evaluation/
      check_release_metadata.py     # Validate generated metadata tables
```

## Installation

Create an environment with Python 3.10+ and install the lightweight public
dependencies:

```bash
pip install -e ./codebase
pip install opencv-python numpy tqdm pyyaml
```

The 3DGS render step also requires a compatible avatar backend that can load
tracked clips and render a frame from a camera packet. Place that backend outside
this repository and point the CLI to its adapter module.

## Input Contract

The public scripts expect a clip manifest in JSONL format:

```json
{"clip_id": "clip_000001", "tracked_dir": "/path/to/tracked/clip_000001"}
{"clip_id": "clip_000002", "tracked_dir": "/path/to/tracked/clip_000002"}
```

For cross-identity jobs, add a source identity directory:

```json
{"clip_id": "clip_000003", "tracked_dir": "/path/to/motion", "source_identity_dir": "/path/to/source_identity"}
```

Rendered videos are written in the same nested format used by the paper
experiments:

```text
<output_root>/<clip_id>/render_fixed_viewpoint/<clip_id>/<clip_id>_fixed_viewpoint_video.mp4
```

## 1. Plan Augmentation Jobs

```bash
python codebase/scripts/plan_augmentation.py \
  --manifest data/manifests/train.jsonl \
  --config codebase/configs/signnet_augmentation.yaml \
  --output outputs/signnet_jobs.jsonl
```

The planner records the factor axis, severity level, deterministic camera
parameters, and output path for each planned sample.

## 2. Render Viewpoint or Identity Variants

Use a compatible backend adapter module that exposes:

```python
def create_backend(model_path: str, device: str):
    ...
```

The returned object must implement the protocol documented in
`signnet/augmentation/render_pipeline.py`.

```bash
python codebase/scripts/run_render_backend.py \
  --jobs outputs/signnet_jobs.jsonl \
  --backend-module my_backend.signnet_adapter \
  --model-path /path/to/avatar/model \
  --output-root outputs/rendered \
  --device cuda:0
```

Supported render modes are `fixed_viewpoint`, `dynamic_viewpoint`, and
`cross_identity`.

## 3. Apply Post-Rendering Augmentations

```bash
python codebase/scripts/run_post_rendering.py \
  --input-root outputs/rendered \
  --output-root outputs/post_rendered \
  --num-tasks 8 \
  --task-id 0 \
  --mode spatial_color
```

Temporal augmentations use the same command with `--mode temporal`.

Each output includes JSONL metadata with the selected transform, severity, seed,
and source path, so the Orig/Zero-shot/Trained protocols can be reconstructed
from release artifacts.

## Release Scope

Included now:

- deterministic 3D viewpoint camera schedules;
- fixed-viewpoint, dynamic-viewpoint, and cross-identity render orchestration;
- deterministic post-rendering augmentation code;
- paper-facing augmentation configuration;
- job and metadata validation utilities.

Planned release:

- background replacement implementation and model packaging;
- pretrained backend checkpoints where redistribution is permitted;
- additional dataset-specific manifests and evaluation harnesses.

## Citation

If you use this code, please cite the SignNet-1M ECCV 2026 paper and the
underlying third-party methods named in the paper.
