"""Backend-agnostic 3DGS render orchestration for SignNet-1M."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from tqdm import tqdm

from .camera import CameraSchedule, make_dynamic_camera_schedule, make_fixed_camera_schedule
from .metadata import append_jsonl


class SignNetRenderBackend(Protocol):
    """Protocol expected by the public SignNet render orchestrator."""

    def load_motion_clip(self, tracked_dir: str):
        """Load tracked target motion and return a backend-specific clip object."""

    def load_source_identity(self, tracked_dir: str):
        """Load source identity data used for cross-identity rendering."""

    def estimate_base_radius(self, motion_clip) -> float:
        """Return the input camera radius used to scale viewpoint schedules."""

    def num_frames(self, motion_clip) -> int:
        """Return the number of frames in a tracked motion clip."""

    def render_clip(self, motion_clip, output_video: str, camera_schedule: CameraSchedule | None = None) -> None:
        """Render a self-identity or viewpoint-augmented clip."""

    def render_cross_identity(
        self,
        source_identity,
        motion_clip,
        output_video: str,
        camera_schedule: CameraSchedule | None = None,
        keep_source_camera: bool = False,
    ) -> None:
        """Render source identity driven by target motion."""


@dataclass(frozen=True)
class RenderJob:
    clip_id: str
    mode: str
    tracked_dir: str
    output_video: str
    source_identity_dir: str | None = None
    yaw: float = 0.0
    pitch: float = 0.0
    zoom: float = 1.0
    dyn_yaw_range: float = 0.35
    dyn_pitch_range: float = 0.30
    dyn_zoom_range: float = 0.0
    dyn_freq: int = 1
    keep_source_camera: bool = False


def build_camera_schedule(job: RenderJob, backend: SignNetRenderBackend, motion_clip) -> CameraSchedule | None:
    if job.mode not in {"fixed_viewpoint", "dynamic_viewpoint", "cross_identity"}:
        raise ValueError(f"Unsupported render mode: {job.mode}")

    if job.mode == "cross_identity" and job.yaw == 0.0 and job.pitch == 0.0 and job.zoom == 1.0:
        return None

    num_frames = backend.num_frames(motion_clip)
    base_radius = backend.estimate_base_radius(motion_clip)
    if job.mode == "dynamic_viewpoint":
        return make_dynamic_camera_schedule(
            num_frames=num_frames,
            yaw_range=job.dyn_yaw_range,
            pitch_range=job.dyn_pitch_range,
            zoom_range=job.dyn_zoom_range,
            freq=job.dyn_freq,
            base_radius=base_radius,
        )

    return make_fixed_camera_schedule(
        num_frames=num_frames,
        yaw=job.yaw,
        pitch=job.pitch,
        zoom=job.zoom,
        base_radius=base_radius,
    )


def run_render_jobs(
    jobs: list[RenderJob],
    backend: SignNetRenderBackend,
    output_root: str | Path,
    metadata_path: str | Path,
) -> None:
    """Execute SignNet render jobs and write one metadata row per output."""

    output_root = Path(output_root)
    for job in tqdm(jobs, desc="render", unit="clip"):
        output_video = output_root / job.output_video
        output_video.parent.mkdir(parents=True, exist_ok=True)
        motion_clip = backend.load_motion_clip(job.tracked_dir)
        camera_schedule = build_camera_schedule(job, backend, motion_clip)

        if job.mode == "cross_identity":
            if not job.source_identity_dir:
                raise ValueError(f"cross_identity job missing source_identity_dir: {job.clip_id}")
            source_identity = backend.load_source_identity(job.source_identity_dir)
            backend.render_cross_identity(
                source_identity=source_identity,
                motion_clip=motion_clip,
                output_video=str(output_video),
                camera_schedule=camera_schedule,
                keep_source_camera=job.keep_source_camera,
            )
        else:
            backend.render_clip(motion_clip=motion_clip, output_video=str(output_video), camera_schedule=camera_schedule)

        append_jsonl(
            metadata_path,
            {
                "clip_id": job.clip_id,
                "mode": job.mode,
                "tracked_dir": job.tracked_dir,
                "source_identity_dir": job.source_identity_dir,
                "output_video": str(output_video),
                "camera_mode": camera_schedule.mode if camera_schedule else "source_camera",
                "num_camera_poses": len(camera_schedule.poses) if camera_schedule else 0,
            },
        )
