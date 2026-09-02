<div align="center">

<h1>SignNet-1M</h1>

<h3>Large-Scale Multilingual Sign Language Video Dataset<br>with Downstream Benchmarks</h3>

<p>
  Zhewen He<sup>1</sup>&nbsp;&nbsp; Junyi Hu<sup>1</sup>&nbsp;&nbsp; Haomian Huang<sup>1</sup>&nbsp;&nbsp;
  Zhenhua Li<sup>1,2</sup>&nbsp;&nbsp; Yu-Shen Liu<sup>3</sup>&nbsp;&nbsp; Yi Fang<sup>1,2</sup>
</p>

<p>
  <sup>1</sup>New York University Abu Dhabi&nbsp;&nbsp;
  <sup>2</sup>ChatSign Technology&nbsp;&nbsp;
  <sup>3</sup>Tsinghua University
</p>

<h4>ECCV 2026</h4>

<p>
  <a href="https://arxiv.org/abs/2606.24361"><img src="https://img.shields.io/badge/arXiv-2606.24361-b31b1b?style=flat-square" alt="arXiv"></a>
  <a href="https://signnet.chatsign.ai/"><img src="https://img.shields.io/badge/Project%20Page-signnet.chatsign.ai-1f8acb?style=flat-square" alt="Project Page"></a>
  <a href="https://drive.google.com/drive/folders/1Wc43peMNvbkyQ_VGgqi9vdYjA_0Fc3HX"><img src="https://img.shields.io/badge/Dataset-Google%20Drive-4285F4?style=flat-square" alt="Dataset"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/Code-MIT-yellow?style=flat-square" alt="Code license: MIT"></a>
  <a href="https://creativecommons.org/licenses/by-nc/4.0/"><img src="https://img.shields.io/badge/Data-CC%20BY--NC%204.0-lightgrey?style=flat-square" alt="Data license: CC BY-NC 4.0"></a>
</p>

<img src="https://raw.githubusercontent.com/openhe-hub/SignNet-1M/main/assets/teaser.png" alt="SignNet-1M augmentation pipeline: background replacement, tracking, 3DGS novel-view and cross-reenactment branches, and post-rendering augmentation" width="100%">

</div>

## TL;DR

**SignNet-1M** is a ~1M-clip augmented sign language corpus spanning ASL, CSL and DGS, built by
re-rendering seven source corpora along three axes — novel viewpoint (3DGS), background and signer
identity (diffusion), and post-rendering capture artifacts — paired with a robustness benchmark that
measures how far models fall under each shift and how much of the gap augmented training recovers.

**This repository is the reference implementation of that augmentation pipeline** — camera
schedules, render orchestration, deterministic post-rendering transforms, metadata and validation.
It does not contain the videos.

> **Available to download today:** the **How2Sign 10× viewpoint subset** — 350,530 clips, 134 GiB,
> ten difficulty levels with per-clip render parameters and checksums. See [Dataset](#dataset).

<details>
<summary><b>Abstract</b></summary>

Sign language models are typically trained on datasets captured under constrained conditions, with
limited viewpoint, background, and signer-identity diversity, leading to poor robustness under
real-world distribution shifts. We introduce **SignNet-1M**, a large-scale augmented dataset
spanning ASL, CSL, and German Sign Language (DGS). SignNet-1M synthesizes realistic variations along
three axes: (i) *novel-view* rendering (rotation and zoom) via 3D Gaussian Splatting (3DGS),
(ii) *scene/identity* editing via diffusion models for background replacement and signer
substitution while preserving sign motion and linguistic content, and (iii) *post-rendering*
augmentations that emulate capture and compression artifacts (e.g., geometric transforms,
photometric shifts, mild temporal resampling, and compression) to better match in-the-wild
recordings. Beyond data release, we provide a unified benchmark suite across downstream tasks
(e.g., translation and recognition) and ablations that isolate each augmentation component.
Experiments across backbones show that training with SignNet-1M consistently improves generalization
under cross-view, cross-background, cross-identity, and post-rendering shifts, while maintaining
strong in-distribution performance. The dataset, released augmentation components, metadata, and
benchmark resources are available at https://signnet.chatsign.ai/.

</details>

## News

- **2026-08-24** — How2Sign 10× viewpoint subset released: 350,530 clips across ten difficulty
  levels, with per-clip render parameters and SHA-256 checksums.
- **2026-06** — Demo samples (viewpoint and identity-swap renders for How2Sign, Phoenix14T,
  CSL-Daily) on Google Drive, and this reference code released.
- **2026-06** — SignNet-1M accepted to **ECCV 2026**.
- **Next:** Phoenix14T (DGS) and CSL-Daily subsets (2026.09) → full release with generation,
  translation and evaluation code (2026.10).

## Dataset

The dataset is released **subset by subset** on Google Drive, not all at once. This table is the
authoritative map from the paper's corpora to what you can actually download.

| Source corpus | Lang | Source clips | Hours | Signers | Augmented clips released | Status | Download |
|---|---|---|---|---|---|---|---|
| [How2Sign](https://how2sign.github.io/) | ASL | 35.00K | 80 | 11 | **350,530** (35,053 × 10 levels) | **Released** 2026-08-24 | [Drive · 134 GiB](https://drive.google.com/drive/folders/1KkESAcJLqdPNNe8msInT8rDxEKIOZIHu) |
| [Phoenix14T](https://www-i6.informatik.rwth-aachen.de/~koller/RWTH-PHOENIX-2014-T/) | DGS | 8.26K | 11 | 9 | — | Planned 2026.09 | [demo samples](https://drive.google.com/drive/folders/1Wc43peMNvbkyQ_VGgqi9vdYjA_0Fc3HX) |
| [CSL-Daily](https://ustc-slr.github.io/datasets/2021_csl_daily/) | CSL | 20.65K | 23 | ~10 | — | Planned 2026.09 | [demo samples](https://drive.google.com/drive/folders/1Wc43peMNvbkyQ_VGgqi9vdYjA_0Fc3HX) |
| [OpenASL](https://github.com/chevalierNoir/OpenASL) | ASL | 98.42K | 288 | ~220 | — | Planned 2026.10 | — |
| [YouTube-ASL](https://github.com/google-research/google-research/tree/master/youtube_asl) | ASL | 610.19K | 984 | ~2.5K | — | Planned 2026.10 | — |
| [CSL-News](https://huggingface.co/datasets/ZechengLi19/CSL-News) | CSL | 751.32K | 1,985 | ~20 | — | Planned 2026.10 | — |
| ASL50K | ASL | — | — | — | — | Not redistributable | — |
| **SignNet-1M (total)** | ASL/CSL/DGS | — | **2,058** | **~10K** | **~1M** planned | How2Sign live | [Drive root](https://drive.google.com/drive/folders/1Wc43peMNvbkyQ_VGgqi9vdYjA_0Fc3HX) |

The corpus rows are the **source candidate pool**, and SignNet-1M is a curated subsample of it —
that is why the rows sum past SignNet-1M's own totals. ASL50K is the seventh corpus counted in the
paper; it is commercially licensed, so it carries no statistics here and its renders are not
redistributable. The ~10K signer count includes synthetic identities produced by cross-identity
reenactment.

**Language composition:** ASL 70% (~700K clips) · CSL 20% (~200K) · DGS 10% (~100K). Mean clip
length 7.41 s. Splits are 8:1:1 **at the source-clip level**, so every augmented variant of a clip
lands in the same split — do not re-split at the clip-variant level or you will leak.

### What is in the release today

```text
sign-1m-data/                    # Drive root
├── demo/
│   ├── viewpoint-aug/           # how2sign · phoenix · csl-daily
│   └── identity-swap-aug/       # how2sign · phoenix · csl-daily
└── released/
    └── h2s/                     # How2Sign 10x viewpoint augmentation
        ├── level01.zip … level10.zip    # 134 GiB total, 13–15 GiB each
        ├── params.tar.gz                # 26 MB, per-clip render parameters
        ├── SHA256SUMS
        └── README.md
```

350,530 mp4 = all 35,053 renderable How2Sign clips × 10 avatars / view-difficulty levels, 512×512
H.264, each clip keeping its source frame rate and frame count. Levels are independent — **download
only the ones you need**; extracting several into one directory reconstructs the tree.

```bash
sha256sum -c SHA256SUMS          # verify before unzipping
unzip level01.zip -d h2s/        # path never collides across levels
```

Path inside every zip, where `<stem>` is the How2Sign clip id:

```text
level{01..10}/<stem>/render_fixed_viewpoint/<stem>/<stem>_fixed_viewpoint_video.mp4
```

The mp4 are **stored uncompressed** (`zip -0`) on purpose, so a clip can be read straight out of the
zip without extracting anything — keep one handle per worker:

```python
import zipfile

class H2SLevel(torch.utils.data.Dataset):
    def __init__(self, zip_path, stems, level="level05"):
        self.zip_path, self.stems, self.level, self._zf = zip_path, stems, level, None

    def __getitem__(self, i):
        if self._zf is None:                      # open lazily, once per worker
            self._zf = zipfile.ZipFile(self.zip_path)
        stem = self.stems[i]
        name = f"{self.level}/{stem}/render_fixed_viewpoint/{stem}/{stem}_fixed_viewpoint_video.mp4"
        return self._zf.read(name)                # raw mp4 bytes, decode as you like
```

Full field reference, the per-level difficulty ladder, filtering recipes and every known caveat live
in **[docs/DATASET.md](docs/DATASET.md)**.

## Installation

```bash
git clone https://github.com/openhe-hub/SignNet-1M.git
cd SignNet-1M
pip install -e .          # Python 3.10+; pulls numpy, opencv-python, pyyaml, tqdm
```

The render step additionally needs a **3DGS avatar backend**, which is not shipped here: it must be
able to load a tracked clip and render a frame from a camera packet. Place it outside this
repository and point the CLI at an adapter module exposing `create_backend(model_path, device)`,
satisfying the `SignNetRenderBackend` protocol in
[`signnet/augmentation/render_pipeline.py`](signnet/augmentation/render_pipeline.py). The paper used
[GUAVA](https://arxiv.org/abs/2505.03351) with [EHM-Tracker](https://github.com/Pixel-Talk/EHM-Tracker)
SMPL-X/FLAME tracking.

## Usage

### 0. Input contract

A clip manifest in JSONL, one object per line:

```json
{"clip_id": "clip_000001", "tracked_dir": "/path/to/tracked/clip_000001"}
{"clip_id": "clip_000002", "tracked_dir": "/path/to/tracked/clip_000002", "source_identity_dir": "/path/to/source_identity"}
```

`source_identity_dir` is required only for cross-identity jobs; rows without it are skipped for that
mode.

### 1. Plan the jobs

```bash
python scripts/plan_augmentation.py \
  --manifest data/manifests/train.jsonl \
  --config configs/signnet_augmentation.yaml \
  --output outputs/signnet_jobs.jsonl \
  --modes fixed_viewpoint dynamic_viewpoint cross_identity   # default: all three
```

For each clip and level the planner draws yaw / pitch / zoom uniformly from that level's envelope,
seeded by `(seed, clip_id, level)` — the same manifest and config always expand to the same jobs,
and the draw is recorded in the job row. Planned outputs follow the released layout:

```text
level01/<clip_id>/render_fixed_viewpoint/<clip_id>/<clip_id>_fixed_viewpoint_video.mp4
<clip_id>/render_dynamic_viewpoint/<clip_id>/<clip_id>_dynamic_viewpoint_video.mp4
<clip_id>/render_cross_identity/<clip_id>/<clip_id>_cross_identity_video.mp4
```

### 2. Render

```bash
python scripts/run_render_backend.py \
  --jobs outputs/signnet_jobs.jsonl \
  --backend-module my_backend.signnet_adapter \
  --model-path /path/to/avatar/model \
  --output-root outputs/rendered \
  --metadata outputs/rendered/render_metadata.jsonl \   # optional
  --device cuda:0                                       # default cuda:0
```

### 3. Post-rendering augmentation

```bash
python scripts/run_post_rendering.py \
  --input-root outputs/rendered \
  --output-root outputs/post_rendered \
  --num-tasks 8 --task-id 0 \
  --mode spatial_color \        # or: temporal
  --seed 42
```

Shards are `sorted(videos)[task_id::num_tasks]`. Run every `--task-id` from `0` to `--num-tasks - 1`,
and **set `LC_ALL=C` for all of them** — about 6.5% of How2Sign stems begin with `-`, and a locale
that sorts them differently silently changes shard membership. Keep `--output-root` outside
`--input-root`, or a second run will re-ingest its own outputs.

### 4. Validate the metadata

```bash
python signnet/evaluation/check_release_metadata.py \
  --metadata outputs/rendered/render_metadata.jsonl \
  --kind render \          # or: post
  --check-files            # also assert every referenced video exists
```

Exits `2` on missing required fields, `3` on missing files.

## Augmentation axes

| Axis | Mode | What it does | Determinism |
|---|---|---|---|
| Novel view — static | `fixed_viewpoint` | 10-level yaw / pitch / zoom ladder, a real 3D camera move on the tracked pose | seeded by `(seed, clip_id, level)` |
| Novel view — dynamic | `dynamic_viewpoint` | sinusoidal camera orbit across the clip | fixed by config |
| Identity | `cross_identity` | source signer appearance driven by target motion | fixed by config |
| Post-rendering | `spatial_color` | 25 geometric + photometric transforms (ids 0–24) | `md5(f"{seed}:post:{video_name}")` |
| Post-rendering | `temporal` | 7 speed / subsample transforms | `md5(f"{seed}:temporal:{video_name}")` |
| Background | — | diffusion scene editing (FlowPortal + IC-Light) | **not in this repo** — planned release |

The `fixed_viewpoint` ladder in [`configs/signnet_augmentation.yaml`](configs/signnet_augmentation.yaml)
is the one used for the public How2Sign release; its envelope was recovered from the released
`params/` and is documented per level in [docs/DATASET.md](docs/DATASET.md#difficulty-ladder).

## Repository layout

```text
SignNet-1M/
├── assets/teaser.png
├── configs/
│   └── signnet_augmentation.yaml          # augmentation axes; the released 10-level ladder
├── docs/
│   └── DATASET.md                         # dataset spec, params reference, caveats, licenses
├── scripts/
│   ├── plan_augmentation.py               # manifest -> planned jobs
│   ├── run_render_backend.py              # drive a 3DGS avatar backend over the jobs
│   └── run_post_rendering.py              # deterministic post-rendering transforms
└── signnet/
    ├── augmentation/
    │   ├── camera.py                      # fixed and dynamic camera pose schedules
    │   ├── post_rendering.py              # OpenCV transforms + deterministic selection
    │   ├── render_pipeline.py             # backend protocol and render orchestration
    │   └── metadata.py                    # JSONL helpers
    └── evaluation/
        └── check_release_metadata.py      # validate generated metadata tables
```

## Release scope and reproducibility

**In this repository:** camera schedules, render orchestration, the released difficulty ladder,
deterministic post-rendering augmentations, metadata writing and validation.

**Not in this repository:** the 3DGS avatar backend internals and weights, SMPL-X/FLAME tracking
assets, background-editing models, and the source corpus videos — none are ours to redistribute.

Consequently this repo reproduces the **augmentation** of the paper given tracked clips and a
compatible backend; it does not by itself reproduce the benchmark tables, which additionally require
the source corpora, the tracking stage and the downstream model training code (planned for the
2026.10 release). Generating the full ~1M-clip dataset cost roughly 12K GPU-hours.

## Known issues

- **6 of 35,059 How2Sign clips are absent by design** — their SMPL-X packs contain NaN and fail
  deterministically at every level. Ids are listed in [docs/DATASET.md](docs/DATASET.md#known-issues).
- **~6.5% of How2Sign stems begin with `-`** — pass them as `--flag=value`, guard with `cp --`, and
  set `LC_ALL=C` whenever you sort or shard over them.
- **`edge_hit_frames` is recorded but not filtered** — 2.9% of released rows have the signer touching
  the frame border; filter from `params/` if it matters to you.
- **Very short clips are not filtered** — How2Sign sentence segmentation produces clips as short as
  5 frames; filter on `n_frames`.
- **Picture quality was reviewed on a sample**, not exhaustively (29 clips of 350,530).
- Post-rendering writes with the `mp4v` fourcc, so its outputs are not bit-comparable to the H.264
  release renders.

## Citation

```bibtex
@inproceedings{he2026signnet1m,
  title     = {SignNet-1M: Large-Scale Multilingual Sign Language Video
               Dataset with Downstream Benchmarks},
  author    = {He, Zhewen and Hu, Junyi and Huang, Haomian and Li, Zhenhua
               and Liu, Yu-Shen and Fang, Yi},
  booktitle = {European Conference on Computer Vision (ECCV)},
  year      = {2026}
}
```

If you use an augmented subset, please **also cite the source corpus it derives from** — BibTeX for
all of them is in [docs/DATASET.md](docs/DATASET.md#citing-the-source-corpora).

## License

- **Code** in this repository: [MIT](LICENSE).
- **Augmented data** on Google Drive: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).

**The source corpora keep their own terms, and those terms govern.** The augmented clips are
derivative works: obtaining them from us does not grant you rights to the underlying corpus, and
several corpora require a separate signed agreement before you may use even the originals. Per-corpus
licenses and access procedures are tabulated in
[docs/DATASET.md](docs/DATASET.md#licensing-and-source-corpus-terms). Where a corpus is more
restrictive than CC BY-NC 4.0, the corpus wins.

## Intended use and limitations

SignNet-1M is released for **non-commercial research** on sign language understanding and on
robustness to viewpoint, background and identity shift. The renders contain **synthetic signer
identities**: an avatar in a clip is not a real person signing that content, and the clips must not
be used to impersonate any signer, to claim a real person produced an utterance, or to attempt
re-identification of signers in the source corpora. Augmented data inherits the demographic and
domain skew of its sources — the corpus is 70% ASL, hours are dominated by CSL-News, and several
corpora have very few signers — so gains measured here do not automatically transfer to
under-represented signing populations.

## Acknowledgements

We thank the authors of How2Sign, OpenASL, YouTube-ASL, Phoenix14T, CSL-Daily and CSL-News for
releasing the source corpora, and the authors of [GUAVA](https://arxiv.org/abs/2505.03351),
[EHM-Tracker](https://github.com/Pixel-Talk/EHM-Tracker), [SMPL-X](https://smpl-x.is.tue.mpg.de/),
FlowPortal and IC-Light, on which the pipeline builds.

This work was partially supported by ChatSign Technology, Ltd., the NYUAD Center for
Interdisciplinary Data Science & AI (CIDSAI), funded by Tamkeen under the NYUAD Research Institute
Award CG016, and the NYUAD Center for Interacting Urban Networks (CITIES), funded by Tamkeen under
the NYUAD Research Institute Award CG001.

## Contact

Questions about the code or the data: open an issue, or email
[zh3510@nyu.edu](mailto:zh3510@nyu.edu) / [yf23@nyu.edu](mailto:yf23@nyu.edu).
