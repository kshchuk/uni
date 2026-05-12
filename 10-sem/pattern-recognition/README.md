# Thermal USB camera — capture notes (`thermal_stream.py`)

Cross-platform live viewer (**macOS / Windows / Linux**) for a **USB Video Class (UVC)** infrared thermal camera. Typical hardware matches **Topdon TC001–class / InfiRay P2–family** modules (generic OEM enclosure).

---

## Camera characteristics

| Property | Value |
|----------|--------|
| **USB identity** | Vendor ID **0x0BDA** (Realtek), Product ID **0x5840** — bridge/controller commonly found on compact thermal modules |
| **OS-reported name** | Enumerates as **“USB Camera”** (generic string); not model-specific |
| **Transport** | USB 2.0 High-Speed (subject to hub/cable quality) |
| **Sensor resolution** | **256 × 192** thermal pixels |
| **Supported streaming modes** (native, UVC) | **`256 × 192`** @ **25 fps** and **`256 × 384`** @ **25 fps**, **`uyvy422`** pixel format |
| **Frame layout at 256 × 384** | **Rows 0–191**: pseudo‑colour / grayscale thermal image for display<br>**Rows 192–383**: auxiliary band often carrying **per-pixel temperature‑related data** (encoding varies by firmware; not decoded to °C in this script by default) |
| **Typical panel geometry** | Two stacked **256 × 192** panels in the taller mode |

> **Why FFmpeg, not OpenCV?** OpenCV's capture backends (AVFoundation / MSMF / V4L2) often **cannot** request these native modes and fall back to the laptop's built-in webcam. This tool drives FFmpeg directly with explicit **resolution, frame rate, and `uyvy422`**, so the correct mode is selected.

---

## Platform support

| OS | FFmpeg backend | Device id form | Listing |
|----|----------------|----------------|---------|
| **macOS** | `avfoundation` | numeric index, e.g. `0` | `ffmpeg -f avfoundation -list_devices true -i ""` |
| **Windows** | `dshow` | friendly name, e.g. `USB Camera` | `ffmpeg -f dshow -list_devices true -i dummy` |
| **Linux** | `v4l2` | path, e.g. `/dev/video0` | `ls /dev/video*` (and `/sys/class/video4linux/<dev>/name`) |

Backend is auto-detected from `platform.system()`; override with `--backend {avfoundation,dshow,v4l2}`.

---

## Requirements

- **FFmpeg** with the right backend compiled in:
  - macOS: `brew install ffmpeg`
  - Linux (Debian/Ubuntu): `sudo apt install ffmpeg`
  - Windows: `winget install Gyan.FFmpeg` (or download a release build) and ensure `ffmpeg` is on `PATH`.
- **Python 3.9+** with packages from `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```
- **Camera permission**:
  - macOS: System Settings → Privacy & Security → Camera (allow your terminal/Cursor).
  - Linux: user must be in the `video` group (`sudo usermod -aG video $USER`, then re-login).
  - Windows: Settings → Privacy → Camera → allow desktop apps.

---

## Usage

```bash
python3 thermal_stream.py --list                    # list capture devices on this OS
python3 thermal_stream.py                           # default: thermal image only (256×192)
python3 thermal_stream.py --mode full               # full frame (256×384)
python3 thermal_stream.py --mode temp               # bottom half only (temperature-data band)

# Force a specific device
python3 thermal_stream.py --device 1                # macOS:   numeric index
python3 thermal_stream.py --device "USB Camera"     # Windows: friendly name
python3 thermal_stream.py --device /dev/video2      # Linux:   V4L2 path

# Override backend (rarely needed)
python3 thermal_stream.py --backend v4l2

# Recording / appearance
python3 thermal_stream.py --mode full --record out.mp4
python3 thermal_stream.py --colormap turbo --scale 4
python3 thermal_stream.py --no-window --record out.mp4    # headless capture
```

**Keyboard:** `q` / `Esc` quit · `1`–`7` change colormap · `s` save PNG snapshot.

---

## Behaviour notes

- **Device id** can change when you unplug/replug; use `--list` then `--device`.
- **Autodetection** matches names containing `USB Camera`, `UVC Camera`, `InfiRay`, `Topdon`, or `0bda:5840`, while excluding obvious built‑in cameras (MacBook, FaceTime, Integrated, HD Webcam, …).
- If the preview is **uniform black**, check the camera permission for your app and try the OS's native viewer first (QuickTime on macOS, Camera app on Windows, `cheese`/`guvcview` on Linux).
- **WSL2 caveat:** USB cameras are not exposed to WSL by default; you'd need [`usbipd-win`](https://github.com/dorssel/usbipd-win) and a kernel with V4L2 USB support. Running natively (Windows or Linux) is simpler.
- **Headless Linux:** with no `DISPLAY`, use `--no-window --record out.mp4`.

---

## License / disclaimer

Hardware behaviour depends on firmware and vendor. This README describes observations for the device class used with this script; your unit may differ slightly.
