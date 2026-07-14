from pathlib import Path
import sys
import re
import os

from PySide6.QtCore import QUrl, Qt
from PySide6.QtWebEngineCore import QWebEngineSettings
# QWebEngineDownloadItem may be missing in some PySide6 builds; import flexibly
try:
    from PySide6.QtWebEngineCore import QWebEngineDownloadItem
except Exception:
    QWebEngineDownloadItem = None
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QIcon, QPixmap
import base64
import shutil
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar
import threading
import time
import datetime


def resource_path(*parts: str) -> Path:
    base_dir = getattr(sys, "_MEIPASS", None)
    if base_dir:
        return Path(base_dir).joinpath(*parts)
    return Path(__file__).resolve().parent.joinpath(*parts)


def find_html_file() -> Path:
    candidates = [
        resource_path("led-pixelmap-tool_121.html"),
        Path(__file__).resolve().parent / "led-pixelmap-tool_121.html",
        Path(__file__).resolve().parent.parent / "led-pixelmap-tool_121.html",
        Path("/Users/kevinveen/Downloads/led-pixelmap-tool_121.html"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "Kon led-pixelmap-tool_121.html niet vinden. Plaats het naast deze map of in Downloads."
    )


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.session_name = "Untitled Project"
        self.setWindowTitle(f"UPScale — {self.session_name}")
        self.resize(1600, 1000)

        self._setup_menu_bar()

        self.web_view = QWebEngineView(self)
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        self.web_view.page().profile().downloadRequested.connect(self.on_download_requested)
        self.setCentralWidget(self.web_view)

        html_path = find_html_file()
        self.web_view.setUrl(QUrl.fromLocalFile(html_path.as_posix()))
        # if requested via environment, trigger an automatic export after the page loads
        self.web_view.page().loadFinished.connect(self._on_page_load_finished)
        # setup a QWebChannel bridge so JS can ask Python to save files directly
        try:
            self._bridge = self._make_bridge()
            channel = QWebChannel(self.web_view.page())
            channel.registerObject('py', self._bridge)
            self.web_view.page().setWebChannel(channel)
            print("[UPScale] QWebChannel registered successfully with Bridge object")
        except Exception as e:
            print(f"[UPScale] QWebChannel setup failed: {e}")
            import traceback
            traceback.print_exc()
            self._bridge = None
        
        # Poll JavaScript for title updates every 500ms
        self._title_update_timer = None
        self._setup_title_polling()

        # start background grouping thread that moves timestamp-prefixed exports
        try:
            t = threading.Thread(target=self._group_exported_files, daemon=True)
            t.start()
        except Exception:
            pass

    def on_download_requested(self, download: QWebEngineDownloadItem) -> None:
        downloads_dir = Path.home() / 'Downloads'
        if not downloads_dir.exists():
            downloads_dir = Path.home()

        suggested = download.suggestedFileName()

        # If the filename starts with projectname-1-1.png or projectname-scaled-output.png,
        # create a folder UPScale-export-projectname in Downloads and store the file inside
        try:
            if suggested and '-' in suggested:
                # Check if this is an export file (ends with -1-1.png or -scaled-output.png)
                if suggested.endswith('-1-1.png'):
                    project_name = suggested[:-8]  # Remove '-1-1.png'
                    folder_name = f"UPScale-export-{project_name}"
                    target_dir = downloads_dir / folder_name
                    target_dir.mkdir(parents=True, exist_ok=True)
                    target = target_dir / suggested
                elif suggested.endswith('-scaled-output.png'):
                    project_name = suggested[:-18]  # Remove '-scaled-output.png'
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
                project_val = target.name[:-8]  # Remove '-1-1.png'
            elif target.name.endswith('-scaled-output.png'):
                project_val = target.name[:-18]  # Remove '-scaled-output.png'

            t = threading.Thread(target=mover, args=(downloads_dir.as_posix(), target.name, target, project_val))
            t.daemon = True
            t.start()
        except Exception:
            pass

    def _setup_title_polling(self) -> None:
        """Poll JavaScript every 500ms to check if the project name has changed."""
        from PySide6.QtCore import QTimer
        self._title_update_timer = QTimer(self)
        self._title_update_timer.timeout.connect(self._poll_title_from_js)
        self._title_update_timer.start(500)  # Poll every 500ms

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
                print(f"[Poll] Window title updated to: {new_title}")
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

    def _reload_page(self) -> None:
        if self.web_view.url().isValid():
            self.web_view.reload()

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
        downloads_dir = Path.home() / 'Downloads'
        main_window = self

        class Bridge(QObject):
            @Slot(str, result=str)
            def set_session_name(self, name: str) -> str:
                """Update the app window title with the session name."""
                print(f"[Python] set_session_name called with: '{name}'")
                try:
                    clean_name = name.replace('.json', '').replace('.JSON', '').strip() if name else None
                    print(f"[Python] clean_name: '{clean_name}'")
                    main_window.session_name = clean_name
                    # Always update title if we have a name (even default names like "Untitled Project")
                    if clean_name:
                        new_title = f"UPScale — {clean_name}"
                        main_window.setWindowTitle(new_title)
                        print(f"[Python] Window title updated to: {new_title}")
                        return "ok"
                    else:
                        main_window.setWindowTitle("UPScale")
                        print("[Python] Window title reset to: UPScale")
                        return "ok"
                except Exception as e:
                    print(f"[Python] set_session_name error: {e}")
                    import traceback
                    traceback.print_exc()
                    return "error"

            @Slot(str, str, result=bool)
            def prepare_export(self, timestamp: str, project_name: str) -> bool:
                """Create the UPScale-export-<project_name>-<timestamp> folder in Downloads ahead of export."""
                try:
                    if not timestamp or not re.match(r'^\d{8}_\d{6}$', timestamp):
                        return False
                    # Clean project name for folder
                    clean_project = project_name.replace('.json', '').replace('.JSON', '').strip() if project_name else 'export'
                    folder_name = f"UPScale-export-{clean_project}-{timestamp}"
                    target_dir = downloads_dir / folder_name
                    target_dir.mkdir(parents=True, exist_ok=True)
                    print(f"[UPScale] prepare_export: created {target_dir}")
                    return True
                except Exception as e:
                    print("[UPScale] prepare_export failed:", e)
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
                            project_name = filename[:-8]  # Remove '-1-1.png'
                        elif filename.endswith('-scaled-output.png'):
                            project_name = filename[:-18]  # Remove '-scaled-output.png'
                        else:
                            project_name = filename.rsplit('.', 1)[0]  # Fallback: remove extension
                        
                        if project_name:
                            folder_name = f"UPScale-export-{project_name}"
                            target_dir = downloads_dir / folder_name
                            target_dir.mkdir(parents=True, exist_ok=True)
                            target = target_dir / filename
                            print(f"[UPScale] save_file folder: {folder_name}")
                    
                    print(f"[UPScale] save_file -> writing {target}")
                    with open(target, 'wb') as f:
                        f.write(data)
                    print(f"[UPScale] save_file -> wrote {target}")
                    return True
                except Exception:
                    import traceback
                    traceback.print_exc()
                    return False

        return Bridge()

    def _group_exported_files(self):
        downloads_dir = Path.home() / 'Downloads'
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

    window = MainWindow()
    window.show()
    try:
        # ensure window uses same icon
        icon = app.windowIcon()
        if not icon.isNull():
            window.setWindowIcon(icon)
    except Exception:
        pass
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
