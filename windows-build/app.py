from pathlib import Path
import sys
import re
import os
import json
import ctypes
import logging
from logging.handlers import RotatingFileHandler

from PySide6.QtCore import QCoreApplication, QUrl, Qt, QTimer, QStandardPaths, Signal, QEvent
from PySide6.QtWebEngineCore import QWebEngineSettings
# QWebEngineDownloadItem may be missing in some PySide6 builds; import flexibly
try:
    from PySide6.QtWebEngineCore import QWebEngineDownloadItem
except Exception:
    QWebEngineDownloadItem = None
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QAction, QColor, QIcon, QPixmap, QGuiApplication, QShortcut, QKeySequence
import base64
import shutil
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMessageBox, QWidget, QVBoxLayout
import threading
import time
import datetime


LOGGER = logging.getLogger("upscale")


RENDER_MODES = ("stable", "gpu", "software")


def get_downloads_dir() -> Path:
    """Resolve a writable Downloads path across macOS/Windows/Linux."""
    locations = QStandardPaths.standardLocations(QStandardPaths.DownloadLocation)
    if locations:
        candidate = Path(locations[0])
        if candidate.exists():
            return candidate
    fallback = Path.home() / "Downloads"
    return fallback if fallback.exists() else Path.home()


def sanitize_path_component(value: str, fallback: str = "export") -> str:
    """Normalize folder/file name parts so they are valid on Windows too."""
    cleaned = (value or "").strip()
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", cleaned)
    cleaned = cleaned.strip(". ")
    return cleaned or fallback


def _config_file_path() -> Path:
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "UPScale" / "config.json"
    return Path.home() / ".upscale-config.json"


def load_config() -> dict:
    cfg_path = _config_file_path()
    try:
        if cfg_path.exists():
            data = json.loads(cfg_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        LOGGER.exception("Failed to read config")
    return {}


def save_config(cfg: dict) -> bool:
    cfg_path = _config_file_path()
    try:
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        cfg_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
        return True
    except Exception:
        LOGGER.exception("Failed to write config")
        return False


def load_render_mode() -> str:
    env_mode = os.environ.get("UPSCALE_WINDOWS_RENDER_MODE", "").strip().lower()
    if env_mode in RENDER_MODES:
        return env_mode

    cfg = load_config()
    cfg_mode = str(cfg.get("windows_render_mode", "")).strip().lower()
    if cfg_mode in RENDER_MODES:
        return cfg_mode
    return "stable"


def save_render_mode(mode: str) -> bool:
    normalized = (mode or "").strip().lower()
    if normalized not in RENDER_MODES:
        return False

    cfg = load_config()
    cfg["windows_render_mode"] = normalized
    return save_config(cfg)


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def mark_run_started(mode: str) -> None:
    cfg = load_config()
    cfg["last_run_clean"] = False
    cfg["last_run_mode"] = mode
    cfg["last_started_utc"] = _utc_now_iso()
    save_config(cfg)


def mark_run_clean_exit(mode: str) -> None:
    cfg = load_config()
    cfg["last_run_clean"] = True
    cfg["last_run_mode"] = mode
    cfg["last_exited_utc"] = _utc_now_iso()
    save_config(cfg)


def resolve_startup_render_mode() -> str:
    env_mode = os.environ.get("UPSCALE_WINDOWS_RENDER_MODE", "").strip().lower()
    if env_mode in RENDER_MODES:
        return env_mode

    cfg = load_config()
    mode = str(cfg.get("windows_render_mode", "stable")).strip().lower()
    if mode not in RENDER_MODES:
        mode = "stable"

    # Auto-fallback: if previous GPU run ended unclean, start in stable mode.
    if mode == "gpu" and cfg.get("last_run_mode") == "gpu" and cfg.get("last_run_clean") is False:
        mode = "stable"
        cfg["windows_render_mode"] = "stable"
        cfg["last_auto_fallback_utc"] = _utc_now_iso()
        save_config(cfg)
        LOGGER.warning("Detected unclean GPU shutdown, auto-fallback to stable mode")
    return mode


def configure_windows_rendering() -> None:
    """Set stable WebEngine rendering defaults for Windows builds."""
    if not sys.platform.startswith("win"):
        return

    mode = resolve_startup_render_mode()
    os.environ["UPSCALE_WINDOWS_RENDER_MODE"] = mode

    flag_set = {
        flag
        for flag in os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "").split()
        if flag.strip()
    }
    if mode in {"stable", "software"}:
        flag_set.update(
            {
                "--disable-direct-composition",
                "--disable-features=CanvasOopRasterization",
                "--disable-zero-copy",
            }
        )
    if mode == "software":
        flag_set.add("--disable-gpu")
        QCoreApplication.setAttribute(Qt.AA_UseSoftwareOpenGL, True)

    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(sorted(flag_set))


def _log_file_path() -> Path:
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "UPScale" / "logs" / "upscale.log"
    return Path.home() / "Library" / "Logs" / "UPScale" / "upscale.log"


def setup_logging() -> Path:
    log_path = _log_file_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if not LOGGER.handlers:
        LOGGER.setLevel(logging.INFO)
        handler = RotatingFileHandler(log_path, maxBytes=512 * 1024, backupCount=3, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        LOGGER.addHandler(handler)

    def _handle_uncaught(exc_type, exc_value, exc_tb):
        LOGGER.exception("Uncaught exception", exc_info=(exc_type, exc_value, exc_tb))

    sys.excepthook = _handle_uncaught
    return log_path


def resource_path(*parts: str) -> Path:
    base_dir = getattr(sys, "_MEIPASS", None)
    if base_dir:
        return Path(base_dir).joinpath(*parts)
    return Path(__file__).resolve().parent.joinpath(*parts)


def find_html_file() -> Path:
    downloads_html = get_downloads_dir() / "led-pixelmap-tool_121.html"
    candidates = [
        resource_path("led-pixelmap-tool_121.html"),
        Path(__file__).resolve().parent / "led-pixelmap-tool_121.html",
        Path(__file__).resolve().parent.parent / "led-pixelmap-tool_121.html",
        downloads_html,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "Kon led-pixelmap-tool_121.html niet vinden. Plaats het naast deze map of in je Downloads-map."
    )


_MAC_OBJC = None


def _mac_objc():
    """Lazily load the Objective-C runtime via ctypes (no pyobjc dependency)."""
    global _MAC_OBJC
    if _MAC_OBJC is None:
        lib = ctypes.cdll.LoadLibrary("/usr/lib/libobjc.dylib")
        lib.sel_registerName.restype = ctypes.c_void_p
        lib.sel_registerName.argtypes = [ctypes.c_char_p]

        def _sel(name: str):
            return lib.sel_registerName(name.encode())

        def _msg(restype, *argtypes):
            return ctypes.CFUNCTYPE(restype, *argtypes)(("objc_msgSend", lib))

        _MAC_OBJC = (_sel, _msg)
    return _MAC_OBJC


def macos_cover_menu_bar(widget, level: int = 1000) -> bool:
    """Raise a Qt window above the macOS menu bar/Dock on its display.

    A borderless window sized to ``screen.geometry()`` still sits *below* the
    menu bar that macOS draws on the active display. Raising the NSWindow level
    above ``NSMainMenuWindowLevel`` (24) makes the output truly cover the screen
    without triggering the native fullscreen animation (no Space switch).
    """
    if not sys.platform.startswith("darwin"):
        return False
    try:
        sel, msg = _mac_objc()
        nsview = ctypes.c_void_p(int(widget.winId()))
        if not nsview:
            return False
        nswindow = msg(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)(nsview, sel("window"))
        if not nswindow:
            return False
        msg(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long)(nswindow, sel("setLevel:"), int(level))
        return True
    except Exception:
        LOGGER.exception("macos_cover_menu_bar failed")
        return False


class LiveOutputWindow(QWidget):
    """Frameless window that shows the Live Output (?live=1 page) full-screen on a chosen monitor.

    A borderless window sized to the exact screen geometry is used instead of the
    native fullscreen API, so macOS does not switch Spaces and the signal keeps running.
    On macOS the window level is raised so it also covers the menu bar and Dock.
    Pressing Esc asks the app to close the output.
    """

    closeRequested = Signal()

    def __init__(self, url: QUrl, parent=None) -> None:
        super().__init__(None)
        self.setWindowTitle("UPScale Live Output")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setStyleSheet("background:#000;")
        self._screen_index = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.view = QWebEngineView(self)
        self.view.page().setBackgroundColor(QColor("#000000"))
        layout.addWidget(self.view)
        self.view.setUrl(url)

        # Esc closes the output regardless of which child widget has focus.
        try:
            shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
            shortcut.setContext(Qt.WindowShortcut)
            shortcut.setAutoRepeat(False)
            shortcut.activated.connect(self.closeRequested.emit)
            self._escape_shortcut = shortcut
        except Exception:
            self._escape_shortcut = None

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Escape:
            self.closeRequested.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    def show_on_screen(self, screen_index: int = 0, fullscreen: bool = False) -> None:
        screens = QGuiApplication.screens()
        if not screens:
            self.showFullScreen()
            return
        try:
            idx = int(screen_index)
        except Exception:
            idx = 0
        if idx < 0 or idx >= len(screens):
            idx = 0
        self._screen_index = idx
        screen = screens[idx]
        geo = screen.geometry()
        # Show first so a native window handle exists, then explicitly assign the
        # window to the target screen. On macOS a borderless window can otherwise
        # stay on the primary display when only its geometry is set.
        self.setGeometry(geo)
        if not self.isVisible():
            self.show()
        try:
            handle = self.windowHandle()
            if handle is not None and handle.screen() is not screen:
                handle.setScreen(screen)
        except Exception:
            pass
        self.setGeometry(geo)
        if fullscreen:
            self.setWindowState(Qt.WindowNoState)
            self.showFullScreen()
        self.raise_()
        self.activateWindow()
        # Cover the menu bar/Dock on macOS (borderless windows sit below them).
        macos_cover_menu_bar(self)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._render_mode_actions = {}
        self.session_name = "Untitled Project"
        self.setWindowTitle(f"UPScale — {self.session_name}")
        self.resize(1600, 1000)

        self._setup_menu_bar()

        self.web_view = QWebEngineView(self)
        self.web_view.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.web_view.page().setBackgroundColor(QColor("#0e1113"))
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, False)
        self.web_view.page().profile().downloadRequested.connect(self.on_download_requested)
        self.setCentralWidget(self.web_view)

        html_path = find_html_file()
        self._html_path = html_path
        self._live_window = None
        self.web_view.setUrl(QUrl.fromLocalFile(html_path.as_posix()))
        # if requested via environment, trigger an automatic export after the page loads
        self.web_view.page().loadFinished.connect(self._on_page_load_finished)
        # setup a QWebChannel bridge so JS can ask Python to save files directly
        try:
            self._bridge = self._make_bridge()
            channel = QWebChannel(self.web_view.page())
            channel.registerObject('py', self._bridge)
            self.web_view.page().setWebChannel(channel)
            LOGGER.info("QWebChannel registered")
        except Exception as e:
            LOGGER.exception("QWebChannel setup failed: %s", e)
            self._bridge = None

        self._setup_screen_listeners()

        # Polling title less often avoids UI hitches on lower-end systems.
        self._title_update_timer = None
        self._setup_title_polling()

        # Keep the legacy group thread optional; it can contend with active downloads.
        if os.environ.get("UPSCALE_ENABLE_BACKGROUND_GROUPER") == "1":
            try:
                t = threading.Thread(target=self._group_exported_files, daemon=True)
                t.start()
                LOGGER.info("Background export grouper enabled")
            except Exception:
                LOGGER.exception("Failed to start background export grouper")

    def eventFilter(self, obj, event) -> bool:
        # Fallback: close the live output with Esc when it is the active window,
        # even if a child web view swallows the key event.
        try:
            if (
                event.type() == QEvent.Type.KeyPress
                and event.key() == Qt.Key_Escape
                and self._live_window is not None
                and self._live_window.isActiveWindow()
            ):
                self._close_live_window()
                return True
        except Exception:
            LOGGER.exception("eventFilter failed")
        return super().eventFilter(obj, event)

    def on_download_requested(self, download: QWebEngineDownloadItem) -> None:
        downloads_dir = get_downloads_dir()

        suggested = download.suggestedFileName()

        # If the filename starts with projectname-1-1.png or projectname-scaled-output.png,
        # create a folder UPScale-export-projectname in Downloads and store the file inside
        try:
            if suggested and '-' in suggested:
                # Check if this is an export file (ends with -1-1.png or -scaled-output.png)
                if suggested.endswith('-1-1.png'):
                    project_name = sanitize_path_component(suggested[:-8])  # Remove '-1-1.png'
                    folder_name = f"UPScale-export-{project_name}"
                    target_dir = downloads_dir / folder_name
                    target_dir.mkdir(parents=True, exist_ok=True)
                    target = target_dir / suggested
                elif suggested.endswith('-scaled-output.png'):
                    project_name = sanitize_path_component(suggested[:-18])  # Remove '-scaled-output.png'
                    folder_name = f"UPScale-export-{project_name}"
                    target_dir = downloads_dir / folder_name
                    target_dir.mkdir(parents=True, exist_ok=True)
                    target = target_dir / suggested
                else:
                    target = downloads_dir / suggested
            else:
                target = downloads_dir / suggested
        except Exception:
            target = downloads_dir / (suggested or 'download')

        # accept the download (let the engine write to the default Downloads)
        try:
            download.accept()
        except Exception:
            try:
                # some bindings expect accept(path)
                download.accept(target.as_posix())
            except Exception:
                pass

        # in case the engine wrote the file into Downloads (default behavior),
        # start a robust mover that waits for the file to appear, ensures it's
        # fully written (stable size over multiple checks), then moves it.
        try:
            import threading, time, shutil

            def mover(src_dir, filename, dest_path, project_name=None):
                src = Path(src_dir) / filename
                # wait up to 60s for the file to appear and stabilize
                last_size = -1
                stable_count = 0
                waited = 0.0
                while waited < 60.0:
                    if src.exists():
                        try:
                            size = src.stat().st_size
                        except Exception:
                            size = -1
                        if size == last_size and size > 0:
                            stable_count += 1
                        else:
                            stable_count = 0
                        last_size = size
                        # require 3 consecutive stable checks (1.5s)
                        if stable_count >= 3:
                            try:
                                shutil.move(str(src), str(dest_path))
                            except Exception:
                                # if move fails, attempt a copy+unlink as fallback
                                try:
                                    shutil.copy2(str(src), str(dest_path))
                                    src.unlink()
                                except Exception:
                                    pass
                            break
                    time.sleep(0.5)
                    waited += 0.5

                # after moving this file, try to gather any other matching files immediately
                if project_name:
                    try:
                        target_dir = downloads_dir / f'UPScale-export-{project_name}'
                        target_dir.mkdir(parents=True, exist_ok=True)
                        # Match files with format: PROJECTNAME-*.png
                        pattern = re.compile(f'^{re.escape(project_name)}-.*\\.(png|jpg|jpeg)$', re.IGNORECASE)
                        for p in Path(src_dir).iterdir():
                            if p.is_file() and pattern.match(p.name):
                                tgt = target_dir / p.name
                                if p.exists() and str(tgt) != str(p):  # Don't move to itself
                                    try:
                                        shutil.move(str(p), str(tgt))
                                    except Exception:
                                        try:
                                            shutil.copy2(str(p), str(tgt))
                                            p.unlink()
                                        except Exception:
                                            pass
                    except Exception:
                        pass

            # Extract project name from filename
            project_val = None
            if target.name.endswith('-1-1.png'):
                project_val = sanitize_path_component(target.name[:-8])  # Remove '-1-1.png'
            elif target.name.endswith('-scaled-output.png'):
                project_val = sanitize_path_component(target.name[:-18])  # Remove '-scaled-output.png'

            t = threading.Thread(target=mover, args=(downloads_dir.as_posix(), target.name, target, project_val))
            t.daemon = True
            t.start()
        except Exception:
            pass

    def _setup_title_polling(self) -> None:
        """Poll JavaScript every 2s to check if the project name has changed."""
        self._title_update_timer = QTimer(self)
        self._title_update_timer.timeout.connect(self._poll_title_from_js)
        self._title_update_timer.start(2000)

    def _poll_title_from_js(self) -> None:
        """Query JavaScript for the current project name and update window title if changed."""
        try:
            # Ask JavaScript for the current title (with error handling)
            self.web_view.page().runJavaScript(
                """
                (function() {
                    try {
                        return typeof lastSavedFilename !== 'undefined' && lastSavedFilename ? lastSavedFilename : 'Untitled Project';
                    } catch(e) {
                        return 'Untitled Project';
                    }
                })()
                """,
                lambda result: self._update_title_from_js(result)
            )
        except Exception:
            pass

    def _update_title_from_js(self, project_name) -> None:
        """Update the window title based on JavaScript result."""
        try:
            clean_name = str(project_name).replace('.json', '').replace('.JSON', '').strip() if project_name else 'Untitled Project'
            new_title = f"UPScale — {clean_name}"
            if self.windowTitle() != new_title:
                self.setWindowTitle(new_title)
        except Exception:
            pass

    def _setup_menu_bar(self) -> None:
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("Bestand")
        reload_action = file_menu.addAction("Herlaad")
        reload_action.triggered.connect(self._reload_page)
        file_menu.addSeparator()
        quit_action = file_menu.addAction("Sluiten")
        quit_action.triggered.connect(self.close)

        # Resolume-style Output menu: pick the video output the scaled output is routed to.
        output_menu = menu_bar.addMenu("Output")
        output_menu.aboutToShow.connect(self._rebuild_output_menu)
        self._output_menu = output_menu

        settings_menu = menu_bar.addMenu("Instellingen")
        render_menu = settings_menu.addMenu("Windows render modus")

        options = [
            ("stable", "Stabiel (aanbevolen)"),
            ("gpu", "GPU (snelst)"),
            ("software", "Software (meest compatibel)"),
        ]
        active_mode = load_render_mode()
        for mode, label in options:
            action = QAction(label, self)
            action.setCheckable(True)
            action.setChecked(mode == active_mode)
            action.triggered.connect(lambda checked, m=mode: self._set_render_mode(m))
            render_menu.addAction(action)
            self._render_mode_actions[mode] = action

    def _rebuild_output_menu(self) -> None:
        """List the connected video outputs; selecting one routes the scaled output there."""
        menu = getattr(self, "_output_menu", None)
        if menu is None:
            return
        menu.clear()
        screens = QGuiApplication.screens()
        primary = QGuiApplication.primaryScreen()
        active_idx = getattr(self._live_window, "_screen_index", -1) if self._live_window is not None else -1
        if not screens:
            empty = menu.addAction("Geen beeldschermen gevonden")
            empty.setEnabled(False)
        for i, screen in enumerate(screens):
            g = screen.geometry()
            name = screen.name() or f"Display {i + 1}"
            label = f"Display {i + 1} — {name} ({g.width()}×{g.height()})"
            if primary is not None and screen is primary:
                label += " · primair"
            if self._live_window is not None and i == active_idx:
                label = "● " + label
            action = menu.addAction(label)
            action.setCheckable(True)
            action.setChecked(self._live_window is not None and i == active_idx)
            action.triggered.connect(lambda checked=False, idx=i: self._route_output(idx))
        menu.addSeparator()
        close_action = menu.addAction("Live output sluiten")
        close_action.setEnabled(self._live_window is not None)
        close_action.triggered.connect(self._close_live_window)
        refresh_action = menu.addAction("Schermen verversen")
        refresh_action.triggered.connect(self._notify_screens_changed)

    def _route_output(self, screen_index: int) -> None:
        """Route the scaled output (Live Output window) to the given video output."""
        self._open_live_window(screen_index)

    def _set_render_mode(self, mode: str) -> None:
        if mode not in RENDER_MODES:
            return
        if not save_render_mode(mode):
            QMessageBox.warning(self, "UPScale", "Kon render modus niet opslaan.")
            return

        for key, action in self._render_mode_actions.items():
            action.blockSignals(True)
            action.setChecked(key == mode)
            action.blockSignals(False)

        QMessageBox.information(
            self,
            "UPScale",
            "Render modus opgeslagen. Herstart de app om de wijziging toe te passen.",
        )

    def _reload_page(self) -> None:
        if self.web_view.url().isValid():
            self.web_view.reload()

    # ---- live output (second screen) ----
    def _list_screens(self) -> str:
        """Return the available screens as a JSON string for the JS screen picker."""
        try:
            primary = QGuiApplication.primaryScreen()
            result = []
            for i, screen in enumerate(QGuiApplication.screens()):
                g = screen.geometry()
                result.append({
                    "index": i,
                    "name": screen.name() or f"Scherm {i + 1}",
                    "w": g.width(),
                    "h": g.height(),
                    "primary": bool(primary is not None and screen is primary),
                })
            return json.dumps(result)
        except Exception:
            LOGGER.exception("list_screens failed")
            return "[]"

    def _notify_live_state(self, is_open: bool, screen_index: int = None) -> None:
        try:
            screens = self._list_screens()
            payload = "{screens: " + screens
            if screen_index is not None:
                try:
                    payload += ", screenIndex: " + str(int(screen_index))
                except Exception:
                    pass
            payload += "}"
            js = (
                "typeof onLiveNativeState==='function' && onLiveNativeState("
                + ("true" if is_open else "false")
                + ", " + payload + ")"
            )
            self.web_view.page().runJavaScript(js)
        except Exception:
            LOGGER.exception("notify_live_state failed")

    def _notify_screens_changed(self) -> None:
        """Push the current list of connected displays to the screen picker."""
        try:
            screens = self._list_screens()
            js = "typeof onLiveScreensChanged==='function' && onLiveScreensChanged(" + screens + ");"
            self.web_view.page().runJavaScript(js)
        except Exception:
            LOGGER.exception("notify_screens_changed failed")

    def _on_screen_added(self, *_args) -> None:
        self._notify_screens_changed()

    def _on_screen_removed(self, *_args) -> None:
        self._notify_screens_changed()
        # keep an open output window on a valid monitor if its screen went away
        try:
            if self._live_window is not None:
                screens = QGuiApplication.screens()
                idx = self._live_window._screen_index
                if not screens or idx >= len(screens):
                    self._live_window.show_on_screen(0)
        except Exception:
            LOGGER.exception("screen removed handling failed")

    def _setup_screen_listeners(self) -> None:
        try:
            app = QApplication.instance()
            if app is None:
                return
            app.screenAdded.connect(self._on_screen_added)
            app.screenRemoved.connect(self._on_screen_removed)
            LOGGER.info("Screen change listeners registered")
        except Exception:
            LOGGER.exception("screen listener setup failed")

    def _open_live_window(self, screen_index: int = 0) -> bool:
        try:
            html_path = getattr(self, "_html_path", None) or find_html_file()
            url = QUrl.fromLocalFile(Path(html_path).as_posix())
            url.setQuery("live=1")
            if self._live_window is None:
                self._live_window = LiveOutputWindow(url, self)
                try:
                    self._live_window.closeRequested.connect(self._close_live_window)
                except Exception:
                    LOGGER.exception("connect closeRequested failed")
            else:
                current = self._live_window.view.url()
                if current.isEmpty() or "live=1" not in current.query():
                    self._live_window.view.setUrl(url)
            try:
                idx = int(screen_index)
            except Exception:
                idx = 0
            self._live_window.show_on_screen(idx)
            self._notify_live_state(True, idx)
            LOGGER.info("Live output window opened on screen %s", idx)
            return True
        except Exception:
            LOGGER.exception("open_live_window failed")
            return False

    def _move_live_window(self, screen_index: int = 0) -> bool:
        if self._live_window is None:
            return False
        try:
            self._live_window.show_on_screen(int(screen_index))
            return True
        except Exception:
            LOGGER.exception("move_live_window failed")
            return False

    def _close_live_window(self) -> bool:
        try:
            if self._live_window is not None:
                try:
                    self._live_window.view.setUrl(QUrl("about:blank"))
                except Exception:
                    pass
                self._live_window.close()
                self._live_window = None
            self._notify_live_state(False)
            return True
        except Exception:
            LOGGER.exception("close_live_window failed")
            return False

    def _on_page_load_finished(self, ok: bool) -> None:
        if not ok:
            return
        # Initialize with default session name
        try:
            self.web_view.page().runJavaScript('updateHeaderTitle();')
        except Exception:
            pass
        # auto-trigger export for testing when environment variable is set
        if os.environ.get('UPSCAPE_AUTO_EXPORT') == '1':
            try:
                self.web_view.page().runJavaScript('exportScaledPNG();')
            except Exception:
                pass

    def _make_bridge(self):
        downloads_dir = get_downloads_dir()
        main_window = self

        class Bridge(QObject):
            @Slot(str, result=str)
            def set_session_name(self, name: str) -> str:
                """Update the app window title with the session name."""
                try:
                    clean_name = name.replace('.json', '').replace('.JSON', '').strip() if name else None
                    main_window.session_name = clean_name
                    # Always update title if we have a name (even default names like "Untitled Project")
                    if clean_name:
                        new_title = f"UPScale — {clean_name}"
                        main_window.setWindowTitle(new_title)
                        return "ok"
                    else:
                        main_window.setWindowTitle("UPScale")
                        return "ok"
                except Exception as e:
                    LOGGER.exception("set_session_name error: %s", e)
                    return "error"

            @Slot(str, str, result=bool)
            def prepare_export(self, timestamp: str, project_name: str) -> bool:
                """Create the UPScale-export-<project_name>-<timestamp> folder in Downloads ahead of export."""
                try:
                    if not timestamp or not re.match(r'^\d{8}_\d{6}$', timestamp):
                        return False
                    # Clean project name for folder
                    clean_project = project_name.replace('.json', '').replace('.JSON', '').strip() if project_name else 'export'
                    clean_project = sanitize_path_component(clean_project, fallback='export')
                    folder_name = f"UPScale-export-{clean_project}-{timestamp}"
                    target_dir = downloads_dir / folder_name
                    target_dir.mkdir(parents=True, exist_ok=True)
                    LOGGER.info("prepare_export created %s", target_dir)
                    return True
                except Exception as e:
                    LOGGER.exception("prepare_export failed: %s", e)
                    return False

            @Slot(str, str, result=bool)
            def save_file(self, filename: str, b64data: str) -> bool:
                try:
                    data = base64.b64decode(b64data)
                    # Parse filename format: PROJECTNAME-1-1.png or PROJECTNAME-scaled-output.png
                    # Extract project name by removing the file type suffix
                    target = downloads_dir / filename
                    
                    if '-' in filename:
                        # Check if filename ends with -1-1.png or -scaled-output.png
                        if filename.endswith('-1-1.png'):
                            project_name = sanitize_path_component(filename[:-8])  # Remove '-1-1.png'
                        elif filename.endswith('-scaled-output.png'):
                            project_name = sanitize_path_component(filename[:-18])  # Remove '-scaled-output.png'
                        else:
                            project_name = sanitize_path_component(filename.rsplit('.', 1)[0])  # Fallback: remove extension
                        
                        if project_name:
                            folder_name = f"UPScale-export-{project_name}"
                            target_dir = downloads_dir / folder_name
                            target_dir.mkdir(parents=True, exist_ok=True)
                            target = target_dir / filename
                            LOGGER.info("save_file target folder %s", folder_name)
                    
                    LOGGER.info("save_file writing %s", target)
                    with open(target, 'wb') as f:
                        f.write(data)
                    LOGGER.info("save_file wrote %s", target)
                    return True
                except Exception:
                    LOGGER.exception("save_file failed")
                    return False

            @Slot(result=str)
            def list_screens(self) -> str:
                return main_window._list_screens()

            @Slot(int, result=bool)
            def open_live_window(self, screen_index: int = 0) -> bool:
                return main_window._open_live_window(screen_index)

            @Slot(int, result=bool)
            def move_live_window(self, screen_index: int = 0) -> bool:
                return main_window._move_live_window(screen_index)

            @Slot(result=bool)
            def close_live_window(self) -> bool:
                return main_window._close_live_window()

        return Bridge()

    def _group_exported_files(self):
        downloads_dir = get_downloads_dir()
        # Match: projectname-1-1.png or projectname-scaled-output.png
        pattern = re.compile(r'^(.+?)-(1-1|scaled-output)\.(png|jpg|jpeg)$', re.IGNORECASE)
        while True:
            try:
                if downloads_dir.exists():
                    files = [p for p in downloads_dir.iterdir() if p.is_file()]
                    groups = {}
                    for p in files:
                        m = pattern.match(p.name)
                        if m:
                            project_name = m.group(1)
                            project_name = sanitize_path_component(project_name)
                            groups.setdefault(project_name, []).append((p, project_name))
                    
                    for project_name, items in groups.items():
                        if not items:
                            continue
                        target_dir = downloads_dir / f'UPScale-export-{project_name}'
                        target_dir.mkdir(parents=True, exist_ok=True)
                        for src, _ in items:
                            try:
                                dest = target_dir / src.name
                                if src.exists():
                                    shutil.move(str(src), str(dest))
                            except Exception:
                                continue
                time.sleep(2.0)
            except Exception:
                time.sleep(3.0)


def main() -> int:
    log_path = setup_logging()
    LOGGER.info("Starting UPScale")
    configure_windows_rendering()
    active_render_mode = os.environ.get("UPSCALE_WINDOWS_RENDER_MODE", "stable")
    LOGGER.info("Windows render mode: %s", active_render_mode)
    if sys.platform.startswith("win"):
        mark_run_started(active_render_mode)
    app = QApplication(sys.argv)
    app.setApplicationName("UPScale")
    # Set application icon to a large square PNG if available to avoid
    # visible padding/white margins in the dock icon.
    try:
        candidates = [
            resource_path('icon_fullbleed.iconset', 'icon_512x512.png'),
            resource_path('icon_fullbleed.iconset', 'icon_1024x1024.png'),
            resource_path('icon.iconset', 'icon_512x512.png'),
            resource_path('app.icns'),
        ]
        for c in candidates:
            if Path(c).exists():
                if str(c).lower().endswith('.png'):
                    try:
                        pix = QPixmap(str(c))
                        if not pix.isNull():
                            size = 512
                            pix = pix.scaled(size, size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                            app.setWindowIcon(QIcon(pix))
                            break
                    except Exception:
                        continue
                else:
                    try:
                        app.setWindowIcon(QIcon(str(c)))
                        break
                    except Exception:
                        continue
    except Exception:
        pass
    LOGGER.info("Application log file: %s", log_path)

    window = MainWindow()
    window.show()
    try:
        # ensure window uses same icon
        icon = app.windowIcon()
        if not icon.isNull():
            window.setWindowIcon(icon)
    except Exception:
        pass
    if sys.platform.startswith("win"):
        app.aboutToQuit.connect(lambda: mark_run_clean_exit(active_render_mode))
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
