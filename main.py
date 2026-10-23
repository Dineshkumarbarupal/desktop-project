"""WindowPilot: a small Windows desktop window controller using Win32 APIs."""
from __future__ import annotations
import ctypes
import platform
from ctypes import wintypes
import eel

if platform.system() == "Windows":
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = wintypes.BOOL
    user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user32.GetWindowTextLengthW.restype = ctypes.c_int
    user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowTextW.restype = ctypes.c_int
    user32.IsWindow.argtypes = [wintypes.HWND]
    user32.IsWindow.restype = wintypes.BOOL
    user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.ShowWindow.restype = wintypes.BOOL
    user32.SetForegroundWindow.argtypes = [wintypes.HWND]
    user32.SetForegroundWindow.restype = wintypes.BOOL
    user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    user32.PostMessageW.restype = wintypes.BOOL
    user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user32.GetWindowRect.restype = wintypes.BOOL
    user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
    user32.SetWindowPos.restype = wintypes.BOOL

def _require_windows():
    if platform.system() != "Windows":
        raise RuntimeError("WindowPilot requires Windows because it uses the Win32 API.")

def _valid_hwnd(hwnd: int):
    _require_windows()
    handle = wintypes.HWND(int(hwnd))
    if not user32.IsWindow(handle):
        raise ValueError("That window no longer exists. Refresh the window list.")
    return handle

@eel.expose
def get_windows():
    """Return visible top-level windows with a title and current bounds."""
    _require_windows()
    windows = []
    @EnumWindowsProc
    def callback(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
        title_buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, title_buffer, length + 1)
        title = title_buffer.value.strip()
        if not title:
            return True
        rect = wintypes.RECT()
        bounds = {"x": 0, "y": 0, "width": 0, "height": 0}
        if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            bounds = {"x": int(rect.left), "y": int(rect.top),
                      "width": int(rect.right - rect.left), "height": int(rect.bottom - rect.top)}
        windows.append({"hwnd": int(hwnd), "title": title, **bounds})
        return True
    user32.EnumWindows(callback, 0)
    windows.sort(key=lambda item: item["title"].casefold())
    return {"ok": True, "windows": windows}

@eel.expose
def control_window(hwnd: int, action: str):
    """Apply a standard, user-requested action to a selected window."""
    try:
        handle = _valid_hwnd(hwnd)
        actions = {"minimize": 6, "maximize": 3, "restore": 9}
        if action in actions:
            user32.ShowWindow(handle, actions[action])
        elif action == "focus":
            user32.ShowWindow(handle, 9)
            user32.SetForegroundWindow(handle)
        elif action == "close":
            # Ask the application to close normally; never force-terminate it.
            user32.PostMessageW(handle, 0x0010, 0, 0)  # WM_CLOSE
        else:
            return {"ok": False, "error": "Unsupported action."}
        return {"ok": True, "message": "Action '" + action + "' sent."}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

@eel.expose
def move_resize_window(hwnd: int, x: int, y: int, width: int, height: int):
    """Move/resize a selected window using SetWindowPos."""
    try:
        handle = _valid_hwnd(hwnd)
        x, y, width, height = int(x), int(y), int(width), int(height)
        if width < 100 or height < 80 or width > 10000 or height > 10000:
            return {"ok": False, "error": "Width must be 100–10000 and height 80–10000."}
        ok = user32.SetWindowPos(handle, None, x, y, width, height, 0x0004 | 0x0010)
        if not ok:
            return {"ok": False, "error": "Windows could not move/resize this window."}
        return {"ok": True, "message": "Window position and size updated."}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

if __name__ == "__main__":
    eel.init("web")
    eel.start("index.html", size=(1120, 760), min_size=(850, 600))
