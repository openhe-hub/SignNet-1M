"""Augmentation utilities for the SignNet-1M release."""

from .camera import CameraSchedule, make_dynamic_camera_schedule, make_fixed_camera_schedule
from .post_rendering import (
    AUGMENTATIONS,
    TEMPORAL_AUGMENTATIONS,
    augment_video,
    pick_aug,
    pick_temporal_aug,
    temporal_augment_video,
)

__all__ = [
    "AUGMENTATIONS",
    "CameraSchedule",
    "TEMPORAL_AUGMENTATIONS",
    "augment_video",
    "make_dynamic_camera_schedule",
    "make_fixed_camera_schedule",
    "pick_aug",
    "pick_temporal_aug",
    "temporal_augment_video",
]
