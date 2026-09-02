# SignNet-1M — dataset reference

Everything you need to download, read and filter the released data. For the pipeline code see the
[README](../README.md); for the paper and the benchmark tables see
[signnet.chatsign.ai](https://signnet.chatsign.ai/).

- [Overview](#overview)
- [Release roadmap](#release-roadmap)
- [Google Drive layout](#google-drive-layout)
- [How2Sign 10× subset](#how2sign-10-subset)
- [Downloading and verifying](#downloading-and-verifying)
- [Reading clips without extracting](#reading-clips-without-extracting)
- [`params/` reference](#params-reference)
- [Difficulty ladder](#difficulty-ladder)
- [Filtering recipes](#filtering-recipes)
- [Known issues](#known-issues)
- [Splits](#splits)
- [Licensing and source corpus terms](#licensing-and-source-corpus-terms)
- [Data card](#data-card)
- [Citing the source corpora](#citing-the-source-corpora)
- [Changelog](#changelog)

## Overview

SignNet-1M is ~1M augmented clips (2,058 hours, ~10K signer identities including synthetic ones)
derived from seven source corpora across three sign languages, at a mean clip length of 7.41 s.
Every clip is a re-render of a source clip along one or more augmentation axes: novel viewpoint via
3DGS, background replacement and signer substitution via diffusion, and post-rendering capture
artifacts.

| Language | Share | Clips | Source corpora |
|---|---|---|---|
| ASL | 70% | ~700K | How2Sign, OpenASL, YouTube-ASL, ASL50K |
| CSL | 20% | ~200K | CSL-Daily, CSL-News |
| DGS | 10% | ~100K | Phoenix14T |

Per-corpus source statistics and current release status are in the
[README's dataset table](../README.md#dataset).

## Release roadmap

| When | Contents | Status |
|---|---|---|
| 2026.06 | Demo samples (viewpoint + identity-swap) and this reference code | Done |
| 2026.08 | How2Sign 10× viewpoint subset — 350,530 clips | Done |
| 2026.09 | Phoenix14T (DGS) and CSL-Daily subsets, packaged per level like How2Sign | Planned |
| 2026.10 | Full dataset plus generation, translation and evaluation code | Planned |

## Google Drive layout

Root folder **`sign-1m-data`**:
[`1Wc43peMNvbkyQ_VGgqi9vdYjA_0Fc3HX`](https://drive.google.com/drive/folders/1Wc43peMNvbkyQ_VGgqi9vdYjA_0Fc3HX)

```text
sign-1m-data/
├── demo/
│   ├── viewpoint-aug/          # how2sign · phoenix · csl-daily
│   └── identity-swap-aug/      # how2sign · phoenix · csl-daily
└── released/
    └── h2s/                    # 1KkESAcJLqdPNNe8msInT8rDxEKIOZIHu
        ├── level01.zip … level10.zip
        ├── params.tar.gz
        ├── SHA256SUMS
        └── README.md
```

`demo/` holds a handful of clips per corpus for eyeballing render quality before committing to a
134 GiB download. `released/` holds the full subsets.

## How2Sign 10× subset

Published 2026-08-24.

| | |
|---|---|
| Clips | **350,530** mp4 = 35,053 source clips × 10 levels |
| Resolution | 512×512, H.264 (sources are 1280×720) |
| Frame rate | preserved per clip — 23.976 / 24 / 30 / 50 / 60 fps all occur |
| Frame count | preserved exactly per clip |
| Size | 134 GiB across ten zips, 13–15 GiB each (they shrink as level rises) |
| Avatars | 10 — `man001`, `man002`, `women001`, `p01_eastasian_male_young`, `p02_southasian_female_young`, `p03_black_male_middle`, `p06_middleeastern_male_young`, `p08_white_male_young`, `p10_eastasian_female_middle`, `p12_white_female_young` |

Each clip was re-rendered onto a different avatar at each of ten escalating view-difficulty levels,
using a real 3D camera move on the tracked SMPL-X pose — not a 2D warp. **Avatar assignment is
randomised per batch, so a level is not tied to one avatar**: `level05` is not "the `man002` level".

Path inside every zip, where `<stem>` is the How2Sign clip id (e.g. `1l6MC-9BQa0_15-5-rgb_front`):

```text
level{01..10}/<stem>/render_fixed_viewpoint/<stem>/<stem>_fixed_viewpoint_video.mp4
```

## Downloading and verifying

The ten level zips are independent — download only the levels you need. Extracting several into the
same directory reconstructs the full tree; paths never collide.

```bash
sha256sum -c SHA256SUMS      # verify the zips you downloaded
unzip level01.zip -d h2s/    # repeat per level
```

`params.tar.gz` is small (26 MB) and worth taking even if you only want one level — it is how you
filter without touching the video.

## Reading clips without extracting

The mp4 inside the zips are **stored, not deflated** (`zip -0`), deliberately: a clip can be read
straight out of the zip at full speed, so you can train off the archives and never materialise
350,530 files on a quota-limited filesystem.

```python
import zipfile
import torch

class H2SLevel(torch.utils.data.Dataset):
    """Reads clips straight out of one level zip."""

    def __init__(self, zip_path, stems, level="level05"):
        self.zip_path = zip_path
        self.stems = stems
        self.level = level
        self._zf = None                       # never open in __init__

    def __len__(self):
        return len(self.stems)

    def __getitem__(self, i):
        if self._zf is None:                  # one handle per worker process
            self._zf = zipfile.ZipFile(self.zip_path)
        stem = self.stems[i]
        name = (f"{self.level}/{stem}/render_fixed_viewpoint/"
                f"{stem}/{stem}_fixed_viewpoint_video.mp4")
        return self._zf.read(name)            # raw mp4 bytes
```

A `ZipFile` handle is **not** safe to share across processes — open it lazily in `__getitem__` (as
above) or in `worker_init_fn`, never before the fork.

## `params/` reference

`params.tar.gz` unpacks to `params/task_0000.jsonl … task_0999.jsonl`, **350,590 rows**, one JSON
object per (clip, level).

The row count exceeds the 350,530 delivered videos by exactly 60: the six unrenderable clips
(below) still get a row at each of the ten levels, with `"status": "failed"` and no camera fields.
**Filter on `status == "success"` before aggregating.**

| Field | Type | Meaning |
|---|---|---|
| `video_name` | str | How2Sign clip id (`<stem>`) |
| `difficulty` | str | `level01` … `level10` |
| `seed` | int | RNG seed for this (clip, level) draw |
| `template` | str | avatar id used for this render |
| `yaw`, `pitch` | float | camera offset actually applied, **radians** |
| `zoom` | float | zoom factor actually applied |
| `sampled_yaw`, `sampled_pitch`, `sampled_zoom` | float | the raw draw, before the in-frame guard |
| `guard_shrink` | float | ≤1.0; how much the draw was pulled back to keep the signer in frame |
| `n_frames` | int | frame count, matches the mp4 |
| `fps` | float | frame rate, matches the mp4 |
| `edge_hit_frames` | int | frames where the subject touched the frame border |
| `max_edge_px` | int | largest border incursion, pixels |
| `render_time` | float | seconds |
| `status` | str | `success` for every delivered clip |
| `output_dir` | str | render path on the production cluster (not meaningful locally) |

## Difficulty ladder

Difficulty rises monotonically and linearly. Per level, yaw / pitch / zoom are drawn uniformly from
an envelope that widens with the level, then pulled back slightly by an in-frame guard
(`guard_shrink`, mean 0.983–0.989).

| Level | Clips | mean \|yaw\| | max \|yaw\| | mean \|pitch\| | max \|pitch\| | zoom range | clips with edge hits |
|---|---|---|---|---|---|---|---|
| `level01` | 35,053 | 4.2° | 8.6° | 2.8° | 5.7° | 0.95–1.10 | 1,517 (4.3%) |
| `level02` | 35,053 | 5.4° | 10.9° | 3.8° | 7.6° | 0.94–1.14 | 1,274 (3.6%) |
| `level03` | 35,053 | 6.6° | 13.3° | 4.7° | 9.5° | 0.94–1.19 | 1,156 (3.3%) |
| `level04` | 35,053 | 7.7° | 15.7° | 5.7° | 11.5° | 0.93–1.23 | 983 (2.8%) |
| `level05` | 35,053 | 9.0° | 18.0° | 6.6° | 13.4° | 0.93–1.28 | 922 (2.6%) |
| `level06` | 35,053 | 10.0° | 20.4° | 7.6° | 15.3° | 0.92–1.32 | 931 (2.7%) |
| `level07` | 35,053 | 11.3° | 22.7° | 8.5° | 17.2° | 0.92–1.37 | 834 (2.4%) |
| `level08` | 35,053 | 12.4° | 25.1° | 9.5° | 19.1° | 0.91–1.41 | 787 (2.2%) |
| `level09` | 35,053 | 13.6° | 27.4° | 10.3° | 21.0° | 0.91–1.46 | 814 (2.3%) |
| `level10` | 35,053 | 14.7° | 29.8° | 11.4° | 22.9° | 0.90–1.50 | 812 (2.3%) |

In radians the envelope is exactly linear: `|yaw| ≤ 0.15 → 0.52`, `|pitch| ≤ 0.10 → 0.40`, zoom
`[0.95, 1.10] → [0.90, 1.50]`. This is what
[`configs/signnet_augmentation.yaml`](../configs/signnet_augmentation.yaml) encodes, so the planner
reproduces the released ladder. The paper states the ladder as |yaw| up to 30° and |pitch| up to 25°;
the shipped data reaches 29.8° and 22.9°.

Note that **edge hits get *less* frequent as difficulty rises** (4.3% at `level01` → 2.3% at
`level10`), which is the opposite of what you would expect from the augmentation — see below.

## Filtering recipes

```python
import glob, json
import pandas as pd

rows = [json.loads(l) for f in glob.glob("params/task_*.jsonl") for l in open(f)]
df = pd.DataFrame(rows)
df = df[df.status == "success"]                        # drop the 60 failed rows

usable = df[(df.n_frames >= 25) & (df.edge_hit_frames == 0)]
stems  = sorted(usable[usable.difficulty == "level05"].video_name)
```

- `n_frames >= 25` drops ~4.2% of rows (1,477 distinct clips have sub-second renders; the shortest
  is 5 frames).
- `edge_hit_frames == 0` drops 2.9% of rows.
- Both filters are level-dependent — apply them per level, or intersect across levels if you need
  the same clip set at every difficulty.

## Known issues

**Six clips of 35,059 are absent by design (0.017%).** Their SMPL-X packs contain NaN in
`head_crop/M_c2o`, so rendering fails deterministically at every level; retrying cannot help. Their
`params` rows exist with `status: failed`.

| Source video | Missing clips |
|---|---|
| `aUBQCNegrYc` | `_2-1`, `_3-1`, `_4-1` |
| `bjQrRezhvQU` | `_20-1`, `_24-1` |
| `bEAy71HZC9M` | `_7-1` |

Upstream, 70 of the 35,129 How2Sign source clips failed SMPL-X extraction, so:
35,053 delivered + 6 unrenderable = 35,059 extracted, and 35,059 + 70 = 35,129 sources. Nothing is
unaccounted for. When quoting a completeness ratio, be explicit about which denominator you mean.

**~6.5% of How2Sign stems begin with `-`** (2,292 of them, some with `--`). Anything passing a stem
as a command-line argument needs a guard (`cp -- "$f"`, `--flag=value` rather than `--flag value`),
and anything sorting or comparing stem lists must set `LC_ALL=C` on both sides or the orderings
silently disagree — which, for sharded processing, silently changes which clips each shard sees.

**`edge_hit_frames` is recorded but not acted on.** 2.9% of rows (10,030) have the signer touching
the frame border at least once; 22.1% of clips are affected at one level or more. The worst case is
364 of 681 frames. It gets *less* common as difficulty rises, and the affected rows cluster at
near-zero yaw/pitch with zoom ≈ 1.0 — which points at tightly framed source footage rather than at
the augmentation. Filter it yourself if hands leaving frame matters for your task.

**Very short clips are not filtered.** How2Sign sentence segmentation produces some very short
clips; the shortest render is 5 frames and the median is 126. Filter on `n_frames`.

**Picture quality was reviewed by sampling.** 29 clips of 350,530 were inspected by eye (the full
difficulty ladder, the worst `edge_hit_frames` cases, and dash-prefixed stems). Frame counts, frame
rates and codecs were verified programmatically for all 350,530.

## Splits

SignNet-1M uses 8:1:1 train/val/test **at the source-clip level**. All ten levels of a clip belong
to the same split. If you build your own splits, split on `video_name`, never on the
`(video_name, difficulty)` pair, or the same signer performing the same sentence will appear in both
train and test.

For the How2Sign subset you can also reuse How2Sign's official train/val/test lists directly: the
`<stem>` is the original How2Sign clip id.

## Licensing and source corpus terms

The augmented renders we distribute are licensed **CC BY-NC 4.0**. They are derivative works, so the
source corpus's own terms continue to apply and take precedence where they are more restrictive.
Obtaining augmented clips from us grants you no rights to the underlying corpus.

| Corpus | License / terms | Access |
|---|---|---|
| How2Sign | CC BY-NC 4.0 | [how2sign.github.io](https://how2sign.github.io/) |
| Phoenix14T | CC BY-NC-SA 3.0 | [RWTH-PHOENIX-Weather 2014 T](https://www-i6.informatik.rwth-aachen.de/~koller/RWTH-PHOENIX-2014-T/) |
| OpenASL | CC BY-NC-ND 4.0 | [github.com/chevalierNoir/OpenASL](https://github.com/chevalierNoir/OpenASL) |
| YouTube-ASL | video ids + captions only; YouTube's Terms of Service govern the videos | [google-research/youtube_asl](https://github.com/google-research/google-research/tree/master/youtube_asl) |
| CSL-Daily | Research use only; requires a release agreement signed by full-time staff | [ustc-slr.github.io](https://ustc-slr.github.io/datasets/2021_csl_daily/) |
| CSL-News | CC BY-NC 4.0 | [huggingface.co/datasets/ZechengLi19/CSL-News](https://huggingface.co/datasets/ZechengLi19/CSL-News) |
| ASL50K | Commercially licensed; obtained under license and **not redistributable** | — |

Note the consequences: augmented Phoenix14T renders carry a ShareAlike obligation, OpenASL is
NoDerivatives upstream, and CSL-Daily requires you to hold your own signed agreement. If you need
commercial use of any of this, none of these licenses give it to you.

## Data card

**Intended use.** Non-commercial research on sign language understanding — translation, recognition
— and on robustness to viewpoint, background and signer-identity shift.

**Out of scope.** Any commercial deployment; impersonating a signer; asserting that a real person
produced an utterance they did not; attempting to re-identify signers in the source corpora; safety-
or rights-critical interpreting without a qualified human interpreter.

**Provenance.** Every clip is a re-render of a public or licensed source corpus clip. No new signing
was recorded for SignNet-1M. Synthetic avatars replace the original signer's appearance in
cross-identity renders; the underlying motion and linguistic content come from the source clip.

**Synthetic identities.** The ~10K signer-identity count includes synthetic identities. An avatar is
not a person and its demographic labelling (as encoded in avatar ids such as
`p03_black_male_middle`) is a rendering attribute, not a claim about any human signer.

**Known biases and limits.** 70% of clips are ASL and hours are dominated by CSL-News; several
source corpora have very few distinct signers (Phoenix14T has 9, How2Sign 11), so signer diversity
in the augmented data comes largely from synthetic avatars rather than from real signing variation.
Domains are narrow (weather bulletins, instructional video, news). Robustness gains measured on this
data should not be assumed to transfer to under-represented signing populations or to conversational
signing.

**Maintenance.** Subsets ship incrementally (see the roadmap); this file is updated with each drop
and the changelog below records what changed.

## Citing the source corpora

```bibtex
@inproceedings{duarte2021how2sign,
  author    = {Duarte, Amanda and Palaskar, Shruti and Ventura, Lucas and Ghadiyaram, Deepti
               and DeHaan, Kenneth and Metze, Florian and Torres, Jordi and Giro-i-Nieto, Xavier},
  title     = {How2Sign: A Large-Scale Multimodal Dataset for Continuous American Sign Language},
  booktitle = {CVPR},
  pages     = {2735--2744},
  year      = {2021}
}

@inproceedings{camgoz2018neural,
  author    = {Camgoz, Necati Cihan and Hadfield, Simon and Koller, Oscar and Ney, Hermann
               and Bowden, Richard},
  title     = {Neural Sign Language Translation},
  booktitle = {CVPR},
  pages     = {7784--7793},
  year      = {2018}
}

@inproceedings{shi2022openasl,
  author    = {Shi, Bowen and Brentari, Diane and Shakhnarovich, Gregory and Livescu, Karen},
  title     = {Open-Domain Sign Language Translation Learned from Online Video},
  booktitle = {EMNLP},
  pages     = {6365--6379},
  year      = {2022}
}

@inproceedings{uthus2023youtubeasl,
  author    = {Uthus, David and Tanzer, Garrett and Georg, Manfred},
  title     = {{YouTube-ASL}: A Large-Scale, Open-Domain {American Sign Language}--{English}
               Parallel Corpus},
  booktitle = {NeurIPS},
  year      = {2023}
}

@inproceedings{zhou2021signbt,
  author    = {Zhou, Hao and Zhou, Wengang and Qi, Weizhen and Pu, Junfu and Li, Houqiang},
  title     = {Improving Sign Language Translation With Monolingual Data by Sign Back-Translation},
  booktitle = {CVPR},
  pages     = {1316--1325},
  year      = {2021}
}

@inproceedings{li2025unisign,
  author    = {Li, Zecheng and Zhou, Wengang and Zhao, Weichao and Wu, Kepeng and Hu, Hezhen
               and Li, Houqiang},
  title     = {Uni-Sign: Toward Unified Sign Language Understanding at Scale},
  booktitle = {ICLR},
  year      = {2025}
}
```

Phoenix14T is `camgoz2018neural`; CSL-Daily is `zhou2021signbt`; CSL-News was introduced with
Uni-Sign (`li2025unisign`).

## Changelog

- **2026-08-24** — How2Sign 10× viewpoint subset: 350,530 clips, ten level zips, `params.tar.gz`,
  `SHA256SUMS`.
- **2026-06** — Demo samples for How2Sign, Phoenix14T and CSL-Daily (viewpoint and identity-swap).
