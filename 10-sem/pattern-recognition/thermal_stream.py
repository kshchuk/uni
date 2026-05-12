#!/usr/bin/env python3
"""
Live preview from a UVC thermal camera (Topdon TC001 / InfiRay P2 class).

Cross-platform: macOS (AVFoundation), Windows (DirectShow), Linux (V4L2).

Why ffmpeg and not OpenCV?
  * The camera enumerates as a generic "USB Camera" (VID 0x0BDA / PID 0x5840) and
    only supports two native modes in uyvy422:  256x192@25 and 256x384@25.
  * OpenCV's capture backends often cannot negotiate that mode and silently
    fall through to the built-in laptop camera — the preview then shows your face.
  * Device ordering can also change on reconnect, so matching by NAME is more
    reliable than a fixed index.

The 256x384 layout produced by these cameras is:
    rows   0..191 : thermal image (Y channel = displayable thermal grayscale)
    rows 192..383 : per-pixel temperature data (16-bit; format depends on model)

Three capture modes:
    display  native 256x192 -- thermal image only (fastest)
    full     native 256x384 -- thermal image + temperature data stacked
    temp     native 256x384, show only the bottom 256x192 (temperature data half)

Usage:
    python3 thermal_stream.py                       # default --mode display
    python3 thermal_stream.py --mode full
    python3 thermal_stream.py --mode temp
    python3 thermal_stream.py --list                # show capture devices
    python3 thermal_stream.py --device 1            # macOS:  numeric index
    python3 thermal_stream.py --device "USB Camera" # Windows: friendly name
    python3 thermal_stream.py --device /dev/video0  # Linux:  V4L2 path
    python3 thermal_stream.py --mode full --record out.mp4
    python3 thermal_stream.py --colormap turbo --scale 4
    python3 thermal_stream.py --backend v4l2        # force backend

Keys:  q / Esc  quit    1..7  cycle colormap    s  save snapshot PNG
"""

from __future__ import annotations

import argparse
import glob
import os
import platform
import re
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime
from typing import Optional

import cv2
import numpy as np

THERMAL_W = 256
THERMAL_PANEL_H = 192
THERMAL_FPS = 25
THERMAL_PIXFMT = "uyvy422"

MODES: dict[str, dict] = {
    "display": {"capture_h": 192, "slice": slice(0, 192), "label": "thermal display"},
    "full":    {"capture_h": 384, "slice": slice(0, 384), "label": "full (thermal + temp)"},
    "temp":    {"capture_h": 384, "slice": slice(192, 384), "label": "temperature data only"},
}

THERMAL_NAME_RE = re.compile(r"USB Camera|UVC Camera|InfiRay|Topdon|0bda[:_]5840", re.IGNORECASE)
EXCLUDE_RE = re.compile(
    r"MacBook|FaceTime|Desk View|Capture screen|Integrated|Built-?in|HD Webcam",
    re.IGNORECASE,
)

COLORMAPS = [
    ("inferno", cv2.COLORMAP_INFERNO),
    ("magma", cv2.COLORMAP_MAGMA),
    ("plasma", cv2.COLORMAP_PLASMA),
    ("jet", cv2.COLORMAP_JET),
    ("hot", cv2.COLORMAP_HOT),
    ("viridis", cv2.COLORMAP_VIRIDIS),
    ("turbo", cv2.COLORMAP_TURBO),
]

IS_WINDOWS = platform.system() == "Windows"


# --------------------------------------------------------------------------- #
# Backend abstraction
# --------------------------------------------------------------------------- #

def detect_backend() -> str:
    sysname = platform.system()
    if sysname == "Darwin":
        return "avfoundation"
    if sysname == "Windows":
        return "dshow"
    if sysname == "Linux":
        return "v4l2"
    raise RuntimeError(f"Unsupported OS: {sysname}")


def list_devices(backend: str) -> list[tuple[str, str]]:
    """Return [(id, name), ...] where id is whatever ffmpeg expects for that backend."""
    if backend == "avfoundation":
        return _list_avfoundation()
    if backend == "dshow":
        return _list_dshow()
    if backend == "v4l2":
        return _list_v4l2()
    raise ValueError(f"unknown backend: {backend}")


def _ffmpeg_list(backend_flag: str, dummy: str = "") -> str:
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-f", backend_flag, "-list_devices", "true", "-i", dummy],
        capture_output=True,
        text=True,
    )
    return proc.stderr


def _list_avfoundation() -> list[tuple[str, str]]:
    out = _ffmpeg_list("avfoundation", "")
    devices: list[tuple[str, str]] = []
    in_video = False
    for line in out.splitlines():
        if "AVFoundation video devices" in line:
            in_video = True
            continue
        if "AVFoundation audio devices" in line:
            in_video = False
            continue
        if not in_video:
            continue
        m = re.search(r"\[(\d+)\]\s+(.+)$", line)
        if m:
            devices.append((m.group(1), m.group(2).strip()))
    return devices


def _list_dshow() -> list[tuple[str, str]]:
    out = _ffmpeg_list("dshow", "dummy")
    devices: list[tuple[str, str]] = []
    in_video = False
    for line in out.splitlines():
        low = line.lower()
        if "directshow video devices" in low:
            in_video = True
            continue
        if "directshow audio devices" in low:
            in_video = False
            continue
        if not in_video:
            continue
        if "alternative name" in low:
            continue
        m = re.search(r'\[dshow[^\]]*\]\s*"([^"]+)"', line)
        if m and "(audio)" not in line.lower():
            devices.append((m.group(1), m.group(1)))
    return devices


def _list_v4l2() -> list[tuple[str, str]]:
    devices: list[tuple[str, str]] = []
    for dev in sorted(glob.glob("/dev/video*")):
        name_file = f"/sys/class/video4linux/{os.path.basename(dev)}/name"
        try:
            with open(name_file) as f:
                name = f.read().strip()
        except OSError:
            name = "(unknown)"
        devices.append((dev, name))
    return devices


def is_thermal_candidate(name: str) -> bool:
    return bool(THERMAL_NAME_RE.search(name)) and not EXCLUDE_RE.search(name)


def find_thermal_id(devices: list[tuple[str, str]]) -> Optional[str]:
    for dev_id, name in devices:
        if is_thermal_candidate(name):
            return dev_id
    return None


def build_ffmpeg_input(backend: str, dev_id: str) -> list[str]:
    """The ffmpeg arguments needed to open the given device on this backend."""
    if backend == "avfoundation":
        return ["-f", "avfoundation", "-i", dev_id]
    if backend == "dshow":
        return ["-f", "dshow", "-i", f"video={dev_id}"]
    if backend == "v4l2":
        return ["-f", "v4l2", "-i", dev_id]
    raise ValueError(f"unknown backend: {backend}")


# --------------------------------------------------------------------------- #
# Capture pipeline
# --------------------------------------------------------------------------- #

def open_ffmpeg_pipe(backend: str, dev_id: str, capture_h: int) -> subprocess.Popen:
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-framerate", str(THERMAL_FPS),
        "-video_size", f"{THERMAL_W}x{capture_h}",
        "-pixel_format", THERMAL_PIXFMT,
        *build_ffmpeg_input(backend, dev_id),
        "-f", "rawvideo",
        "-pix_fmt", "bgr24",
        "-",
    ]
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=THERMAL_W * capture_h * 3 * 4,
    )


def shutdown_proc(proc: subprocess.Popen) -> None:
    """Stop ffmpeg cleanly (so muxers flush) on every OS."""
    try:
        if IS_WINDOWS:
            proc.terminate()
        else:
            proc.send_signal(signal.SIGINT)
        proc.wait(timeout=2)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Thermal camera live stream (cross-platform: ffmpeg + OpenCV)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--list", action="store_true", help="List capture devices and exit")
    p.add_argument(
        "--backend",
        choices=["avfoundation", "dshow", "v4l2"],
        default=None,
        help="Capture backend (default: auto-detect from OS)",
    )
    p.add_argument(
        "--device",
        default=None,
        help="Device id (macOS index, Windows friendly name, Linux /dev/videoN)",
    )
    p.add_argument(
        "--mode",
        choices=list(MODES.keys()),
        default="display",
        help="display=256x192 thermal, full=256x384 thermal+temp, temp=256x192 temp-data only",
    )
    p.add_argument("--colormap", default="inferno", choices=[n for n, _ in COLORMAPS])
    p.add_argument("--scale", type=int, default=3, help="Display upscale factor")
    p.add_argument("--record", metavar="PATH", help="Write the colorized stream to a video file (e.g. out.mp4)")
    p.add_argument("--no-window", action="store_true", help="Do not open a preview window (useful with --record)")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if shutil.which("ffmpeg") is None:
        hint = {
            "Darwin": "brew install ffmpeg",
            "Linux": "sudo apt install ffmpeg   # or your distro's equivalent",
            "Windows": "winget install Gyan.FFmpeg   (or download a release build)",
        }.get(platform.system(), "install ffmpeg from https://ffmpeg.org/")
        print(f"ffmpeg not found in PATH. Install with:  {hint}", file=sys.stderr)
        return 2

    backend = args.backend or detect_backend()
    print(f"Backend: {backend}  (OS: {platform.system()})")

    devices = list_devices(backend)
    if args.list:
        print(f"Capture devices ({backend}):")
        if not devices:
            print("  (none found)")
        for dev_id, name in devices:
            tag = "  <-- thermal candidate" if is_thermal_candidate(name) else ""
            print(f"  [{dev_id}] {name}{tag}")
        return 0

    if args.device is not None:
        dev_id = args.device
    else:
        dev_id = find_thermal_id(devices)
        if dev_id is None:
            print("Could not autodetect the thermal camera.", file=sys.stderr)
            print("Available devices:", file=sys.stderr)
            for did, name in devices:
                print(f"  [{did}] {name}", file=sys.stderr)
            print("\nReconnect the camera, then re-run, or pass --device <id>.", file=sys.stderr)
            return 1

    mode_cfg = MODES[args.mode]
    capture_h: int = mode_cfg["capture_h"]
    crop: slice = mode_cfg["slice"]
    out_h = (crop.stop - crop.start)

    chosen_name = next((n for i, n in devices if i == dev_id), str(dev_id))
    print(
        f"Opening thermal device [{dev_id}] '{chosen_name}' "
        f"at {THERMAL_W}x{capture_h}@{THERMAL_FPS} ({THERMAL_PIXFMT})  "
        f"mode={args.mode} ({mode_cfg['label']})  display={THERMAL_W}x{out_h}"
    )

    proc = open_ffmpeg_pipe(backend, dev_id, capture_h)
    assert proc.stdout is not None and proc.stderr is not None

    frame_bytes = THERMAL_W * capture_h * 3
    cmap_idx = next(i for i, (n, _) in enumerate(COLORMAPS) if n == args.colormap)
    win = f"Thermal [{args.mode}] — q/Esc quit, 1..7 colormap, s snapshot"
    show = not args.no_window
    if show:
        cv2.namedWindow(win, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(win, THERMAL_W * args.scale, out_h * args.scale)

    writer = None
    if args.record:
        rec_w = THERMAL_W * args.scale
        rec_h = out_h * args.scale
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(args.record, fourcc, THERMAL_FPS, (rec_w, rec_h))
        if not writer.isOpened():
            print(f"Could not open writer for {args.record}", file=sys.stderr)
            writer = None

    n_frames = 0
    t0 = time.time()
    try:
        while True:
            buf = proc.stdout.read(frame_bytes)
            if len(buf) < frame_bytes:
                err = proc.stderr.read().decode(errors="ignore").strip()
                if err:
                    print(f"ffmpeg ended: {err}", file=sys.stderr)
                else:
                    print("ffmpeg stream ended.", file=sys.stderr)
                break

            frame = np.frombuffer(buf, dtype=np.uint8).reshape(capture_h, THERMAL_W, 3)
            view = frame[crop, :, :]

            gray = cv2.cvtColor(view, cv2.COLOR_BGR2GRAY)
            colored = cv2.applyColorMap(gray, COLORMAPS[cmap_idx][1])

            big = cv2.resize(
                colored,
                (THERMAL_W * args.scale, out_h * args.scale),
                interpolation=cv2.INTER_CUBIC,
            )

            n_frames += 1
            if n_frames % 25 == 0:
                fps = n_frames / max(time.time() - t0, 1e-6)
                if show:
                    cv2.setWindowTitle(
                        win,
                        f"Thermal [{args.mode}] — {fps:0.1f} fps  cmap={COLORMAPS[cmap_idx][0]}",
                    )

            if writer is not None:
                writer.write(big)

            if show:
                cv2.imshow(win, big)
                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), 27):
                    break
                if ord("1") <= key <= ord(str(len(COLORMAPS))):
                    cmap_idx = key - ord("1")
                    print(f"colormap -> {COLORMAPS[cmap_idx][0]}")
                if key == ord("s"):
                    fname = f"thermal_{args.mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    cv2.imwrite(fname, big)
                    print(f"saved {fname}")
    except KeyboardInterrupt:
        pass
    finally:
        shutdown_proc(proc)
        if writer is not None:
            writer.release()
        if show:
            cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
