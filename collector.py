"""
collector.py
Detects the active application and whether the user is idle.
Supports Windows, macOS, and Linux.
"""

import time
import platform
from pynput import mouse, keyboard


# ── Idle Detection ──────────────────────────────────────────────────────────

IDLE_THRESHOLD = 300  # seconds (5 minutes)
_last_activity = time.time()


def _on_activity(*args):
    """Reset the idle timer on any input event."""
    global _last_activity
    _last_activity = time.time()


# Listen for mouse and keyboard activity in the background
mouse.Listener(on_move=_on_activity, on_click=_on_activity).start()
keyboard.Listener(on_press=_on_activity).start()


def is_idle() -> bool:
    """Returns True if the user has been inactive beyond the threshold."""
    return (time.time() - _last_activity) > IDLE_THRESHOLD


# ── Active Window ───────────────────────────────────────────────────────────

def get_active_window() -> tuple[str, str]:
    """
    Returns (app_name, window_title) of the currently focused window.
    Falls back to ("unknown", "unknown") if detection fails.
    """
    os_name = platform.system()

    try:
        if os_name == "Windows":
            return _get_window_windows()
        elif os_name == "Darwin":
            return _get_window_mac()
        else:
            return _get_window_linux()
    except Exception:
        return "unknown", "unknown"


def _get_window_windows() -> tuple[str, str]:
    import win32gui
    import win32process
    import psutil

    hwnd = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(hwnd)
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    app = psutil.Process(pid).name().replace(".exe", "")
    return app, title


def _get_window_mac() -> tuple[str, str]:
    from AppKit import NSWorkspace
    app = NSWorkspace.sharedWorkspace().activeApplication()
    app_name = app["NSApplicationName"]
    title = app_name  # macOS doesn't expose window titles without accessibility APIs
    return app_name, title


def _get_window_linux() -> tuple[str, str]:
    import subprocess
    window_id = subprocess.check_output(["xdotool", "getactivewindow"]).strip()
    title = subprocess.check_output(["xdotool", "getwindowname", window_id]).decode().strip()
    app = subprocess.check_output(["xdotool", "getwindowclassname", window_id]).decode().strip()
    return app, title