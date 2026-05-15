#!/usr/bin/env python3
"""Print CGWindowNumber for the supervisor window (for screencapture -l)."""
from __future__ import annotations

import sys


def main() -> int:
    title_part = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        import Quartz
    except ImportError:
        return 1

    opts = (
        Quartz.kCGWindowListOptionOnScreenOnly
        | Quartz.kCGWindowListExcludeDesktopElements
    )
    for win in Quartz.CGWindowListCopyWindowInfo(opts, Quartz.kCGNullWindowID):
        if win.get("kCGWindowOwnerName") != "supervisor":
            continue
        name = win.get("kCGWindowName") or ""
        if title_part and title_part not in name:
            continue
        layer = win.get("kCGWindowLayer", 0)
        if layer != 0:
            continue
        print(int(win["kCGWindowNumber"]))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
