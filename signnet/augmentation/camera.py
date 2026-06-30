"""Camera schedules used for SignNet-1M viewpoint augmentation."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi, sin

import numpy as np


@dataclass(frozen=True)
class CameraPose:
    frame_index: int
    yaw: float
    pitch: float
    zoom: float
    radius: float
    origin: tuple[float, float, float]
    look_at: tuple[float, float, float]


@dataclass(frozen=True)
class CameraSchedule:
    mode: str
    poses: tuple[CameraPose, ...]


def _camera_origin(yaw: float, pitch: float, radius: float) -> tuple[float, float, float]:
    horizontal = pi / 2 + yaw
    vertical = pi / 2 - 0.05 + pitch
    phi = vertical
    return (
        radius * sin(phi) * cos(pi - horizontal),
        radius * cos(phi),
        radius * sin(phi) * sin(pi - horizontal),
    )


def make_fixed_camera_schedule(
    num_frames: int,
    yaw: float = 0.0,
    pitch: float = 0.0,
    zoom: float = 1.0,
    base_radius: float = 1.0,
    look_at: tuple[float, float, float] = (0.0, 0.75, 0.0),
) -> CameraSchedule:
    """Create a static camera schedule for a full clip."""

    radius = base_radius * zoom
    origin = _camera_origin(yaw, pitch, radius)
    poses = tuple(
        CameraPose(i, yaw=yaw, pitch=pitch, zoom=zoom, radius=radius, origin=origin, look_at=look_at)
        for i in range(num_frames)
    )
    return CameraSchedule(mode="fixed_viewpoint", poses=poses)


def make_dynamic_camera_schedule(
    num_frames: int,
    yaw_range: float = 0.35,
    pitch_range: float = 0.30,
    zoom_range: float = 0.0,
    freq: int = 1,
    base_radius: float = 1.0,
    look_at: tuple[float, float, float] = (0.0, 0.75, 0.0),
) -> CameraSchedule:
    """Create the sinusoidal camera orbit used for dynamic viewpoint shifts."""

    poses = []
    for frame_index in range(num_frames):
        phase = 2 * np.pi * freq * frame_index / max(num_frames, 1)
        yaw = yaw_range * sin(phase)
        pitch = pitch_range * cos(phase)
        zoom = 1.0 + zoom_range * sin(phase)
        radius = base_radius * zoom
        poses.append(
            CameraPose(
                frame_index=frame_index,
                yaw=yaw,
                pitch=pitch,
                zoom=zoom,
                radius=radius,
                origin=_camera_origin(yaw, pitch, radius),
                look_at=look_at,
            )
        )
    return CameraSchedule(mode="dynamic_viewpoint", poses=tuple(poses))
