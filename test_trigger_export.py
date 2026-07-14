from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, QTimer
from pathlib import Path
import sys

app = QApplication(sys.argv)
view = QWebEngineView()
# avoid importing app.py (some PySide6 installs lack QWebEngineDownloadItem symbol)
html = Path(__file__).resolve().parent.joinpath('led-pixelmap-tool_121.html')
print('Loading', html)
view.load(QUrl.fromLocalFile(html.as_posix()))

def on_load(ok):
    if ok:
        print('Page loaded — triggering exportScaledPNG()')
        view.page().runJavaScript('exportScaledPNG();')
        # wait a bit for downloads to complete then quit
        QTimer.singleShot(8000, app.quit)
    else:
        print('Failed to load page')
        app.quit()

view.loadFinished.connect(on_load)
view.show()
app.exec()
print('Done')
