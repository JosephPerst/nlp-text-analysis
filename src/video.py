"""Minimal frame -> MP4 writer that pipes raw RGBA frames into ffmpeg.

Repeated frames (holds) are written by re-sending the same bytes, so a chart
state is only rendered once no matter how long it stays on screen.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import numpy as np

FPS = 30


class Mp4Writer:
    def __init__(self, path: str | Path, width: int, height: int, fps: int = FPS):
        if shutil.which("ffmpeg") is None:
            raise RuntimeError("ffmpeg not found on PATH; install it to export MP4s")
        self.size = (width, height)
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{width}x{height}", "-r", str(fps),
            "-i", "-",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
            "-movflags", "+faststart",
            str(path),
        ]
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    def write(self, frame: np.ndarray, repeat: int = 1) -> None:
        h, w = frame.shape[:2]
        if (w, h) != self.size:
            raise ValueError(f"frame is {w}x{h}, expected {self.size[0]}x{self.size[1]}")
        data = np.ascontiguousarray(frame).tobytes()
        for _ in range(repeat):
            self.proc.stdin.write(data)

    def close(self) -> None:
        self.proc.stdin.close()
        if self.proc.wait() != 0:
            raise RuntimeError("ffmpeg failed")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def ease(t: float) -> float:
    """Smoothstep easing for fades."""
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)
