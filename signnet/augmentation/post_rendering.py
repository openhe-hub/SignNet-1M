"""Deterministic post-rendering video augmentations for SignNet-1M."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


AUGMENTATIONS = {
    0: {"type": "geo", "name": "center_crop_80", "crop_frac": 0.80},
    1: {"type": "geo", "name": "center_crop_90", "crop_frac": 0.90},
    2: {"type": "geo", "name": "corner_crop_tl", "crop_frac": 0.85, "corner": "tl"},
    3: {"type": "geo", "name": "corner_crop_tr", "crop_frac": 0.85, "corner": "tr"},
    4: {"type": "geo", "name": "corner_crop_bl", "crop_frac": 0.85, "corner": "bl"},
    5: {"type": "geo", "name": "corner_crop_br", "crop_frac": 0.85, "corner": "br"},
    6: {"type": "geo", "name": "rotate_p5", "angle": 5.0},
    7: {"type": "geo", "name": "rotate_n5", "angle": -5.0},
    8: {"type": "geo", "name": "rotate_p10", "angle": 10.0},
    9: {"type": "geo", "name": "rotate_n10", "angle": -10.0},
    10: {"type": "geo", "name": "perspective_left", "direction": "left", "strength": 0.10},
    11: {"type": "geo", "name": "perspective_right", "direction": "right", "strength": 0.10},
    12: {"type": "color", "name": "brightness_up", "brightness": 40.0},
    13: {"type": "color", "name": "brightness_down", "brightness": -40.0},
    14: {"type": "color", "name": "contrast_up", "contrast": 1.5},
    15: {"type": "color", "name": "contrast_down", "contrast": 0.6},
    16: {"type": "color", "name": "saturation_up", "saturation": 1.8},
    17: {"type": "color", "name": "saturation_down", "saturation": 0.3},
    18: {"type": "color", "name": "grayscale", "grayscale": True},
    19: {"type": "color", "name": "hue_shift_p20", "hue_shift": 20},
    20: {"type": "color", "name": "hue_shift_n20", "hue_shift": -20},
    21: {"type": "color", "name": "gamma_up", "gamma": 1.5},
    22: {"type": "color", "name": "gamma_down", "gamma": 0.6},
    23: {"type": "color", "name": "jitter_warm", "r_scale": 1.15, "b_scale": 0.85},
    24: {"type": "color", "name": "jitter_cool", "r_scale": 0.85, "b_scale": 1.15},
}

TEMPORAL_AUGMENTATIONS = {
    0: {"name": "speed_0.5x", "mode": "speed", "speed": 0.5},
    1: {"name": "speed_0.75x", "mode": "speed", "speed": 0.75},
    2: {"name": "speed_1.25x", "mode": "speed", "speed": 1.25},
    3: {"name": "speed_1.5x", "mode": "speed", "speed": 1.5},
    4: {"name": "speed_2.0x", "mode": "speed", "speed": 2.0},
    5: {"name": "subsample_0.5fps", "mode": "subsample", "step": 2},
    6: {"name": "subsample_0.33fps", "mode": "subsample", "step": 3},
}


@dataclass(frozen=True)
class VideoAugmentationResult:
    input_path: str
    output_path: str
    aug_id: int
    aug_name: str
    aug_type: str


def _hash_to_index(key: str, modulo: int) -> int:
    return int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16) % modulo


def pick_aug(video_name: str, seed: int = 42) -> int:
    """Map a video id to one spatial/color transform deterministically."""

    return _hash_to_index(f"{seed}:post:{video_name}", len(AUGMENTATIONS))


def pick_temporal_aug(video_name: str, seed: int = 42) -> int:
    """Map a video id to one temporal transform deterministically."""

    return _hash_to_index(f"{seed}:temporal:{video_name}", len(TEMPORAL_AUGMENTATIONS))


def apply_geo_aug(frame: np.ndarray, aug_id: int) -> np.ndarray:
    """Apply one geometric augmentation to a BGR uint8 frame."""

    cfg = AUGMENTATIONS[aug_id]
    if cfg["type"] != "geo":
        raise ValueError(f"aug_id {aug_id} is not geometric")

    height, width = frame.shape[:2]
    name = cfg["name"]

    if "crop" in name:
        frac = cfg["crop_frac"]
        crop_h, crop_w = int(height * frac), int(width * frac)
        if "center" in name:
            y0 = (height - crop_h) // 2
            x0 = (width - crop_w) // 2
        else:
            corner = cfg["corner"]
            y0 = 0 if corner in ("tl", "tr") else height - crop_h
            x0 = 0 if corner in ("tl", "bl") else width - crop_w
        cropped = frame[y0 : y0 + crop_h, x0 : x0 + crop_w]
        return cv2.resize(cropped, (width, height), interpolation=cv2.INTER_LINEAR)

    if "rotate" in name:
        matrix = cv2.getRotationMatrix2D((width / 2, height / 2), cfg["angle"], 1.0)
        return cv2.warpAffine(
            frame,
            matrix,
            (width, height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT_101,
        )

    if "perspective" in name:
        dx = int(width * cfg["strength"])
        src = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
        if cfg["direction"] == "left":
            dst = np.float32([[dx, 0], [width, 0], [dx, height], [width, height]])
        else:
            dst = np.float32([[0, 0], [width - dx, 0], [0, height], [width - dx, height]])
        matrix = cv2.getPerspectiveTransform(src, dst)
        return cv2.warpPerspective(
            frame,
            matrix,
            (width, height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT_101,
        )

    raise ValueError(f"Unknown geometric augmentation: {name}")


def apply_color_aug(frame_bgr: np.ndarray, aug_id: int) -> np.ndarray:
    """Apply one photometric augmentation to a BGR uint8 frame."""

    cfg = AUGMENTATIONS[aug_id]
    if cfg["type"] != "color":
        raise ValueError(f"aug_id {aug_id} is not photometric")

    name = cfg["name"]
    frame = frame_bgr.astype(np.float32)

    if "brightness" in name:
        frame = frame + cfg["brightness"]
    elif "contrast" in name:
        mean = frame.mean()
        frame = cfg["contrast"] * (frame - mean) + mean
    elif "saturation" in name:
        hls = cv2.cvtColor(np.clip(frame, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HLS)
        hls = hls.astype(np.float32)
        hls[:, :, 2] = np.clip(hls[:, :, 2] * cfg["saturation"], 0, 255)
        return cv2.cvtColor(hls.astype(np.uint8), cv2.COLOR_HLS2BGR)
    elif "grayscale" in name:
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR).astype(np.float32)
    elif "hue" in name:
        hsv = cv2.cvtColor(np.clip(frame, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV)
        hsv = hsv.astype(np.int32)
        hsv[:, :, 0] = (hsv[:, :, 0] + cfg["hue_shift"]) % 180
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    elif "gamma" in name:
        frame = (np.clip(frame / 255.0, 0, 1) ** cfg["gamma"]) * 255.0
    elif "jitter" in name:
        frame[:, :, 2] = frame[:, :, 2] * cfg["r_scale"]
        frame[:, :, 0] = frame[:, :, 0] * cfg["b_scale"]
    else:
        raise ValueError(f"Unknown photometric augmentation: {name}")

    return np.clip(frame, 0, 255).astype(np.uint8)


def augment_video(input_path: str | os.PathLike, output_path: str | os.PathLike, aug_id: int) -> VideoAugmentationResult:
    """Read an MP4, apply one spatial/color augmentation, and write an MP4."""

    input_path = str(input_path)
    output_path = str(output_path)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    capture = cv2.VideoCapture(input_path)
    if not capture.isOpened():
        raise RuntimeError(f"Cannot open video: {input_path}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

    cfg = AUGMENTATIONS[aug_id]
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        if cfg["type"] == "geo":
            frame = apply_geo_aug(frame, aug_id)
        else:
            frame = apply_color_aug(frame, aug_id)
        writer.write(frame)

    capture.release()
    writer.release()
    return VideoAugmentationResult(input_path, output_path, aug_id, cfg["name"], cfg["type"])


def _apply_speed_change(frames: list[np.ndarray], speed: float) -> list[np.ndarray]:
    n_in = len(frames)
    n_out = max(1, round(n_in / speed))
    return [frames[min(round(i * speed), n_in - 1)] for i in range(n_out)]


def _apply_subsample(frames: list[np.ndarray], step: int, input_fps: float) -> tuple[list[np.ndarray], float]:
    return frames[::step], input_fps / step


def temporal_augment_video(
    input_path: str | os.PathLike,
    output_path: str | os.PathLike,
    aug_id: int,
) -> VideoAugmentationResult:
    """Read an MP4, apply one temporal augmentation, and write an MP4."""

    input_path = str(input_path)
    output_path = str(output_path)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    cfg = TEMPORAL_AUGMENTATIONS[aug_id]
    capture = cv2.VideoCapture(input_path)
    if not capture.isOpened():
        raise RuntimeError(f"Cannot open video: {input_path}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    frames = []
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        frames.append(frame)
    capture.release()

    if not frames:
        raise RuntimeError(f"No frames in video: {input_path}")

    out_fps = fps
    if cfg["mode"] == "speed":
        out_frames = _apply_speed_change(frames, cfg["speed"])
    elif cfg["mode"] == "subsample":
        out_frames, out_fps = _apply_subsample(frames, cfg["step"], fps)
    else:
        raise ValueError(f"Unknown temporal mode: {cfg['mode']}")

    writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), out_fps, (width, height))
    for frame in out_frames:
        writer.write(frame)
    writer.release()

    return VideoAugmentationResult(input_path, output_path, aug_id, cfg["name"], "temporal")
