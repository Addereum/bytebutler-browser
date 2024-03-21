import sys
import requests
import json
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *


class BookmarkButton(QToolButton):
    def __init__(self, name, url):
        super().__init__()
        self.name = name
        self.url = url
        self.initUI()

    def initUI(self):
        favicon = self.get_favicon(self.url)
        if favicon:
            pixmap = QPixmap()
            pixmap.loadFromData(favicon)
            self.setIcon(QIcon(pixmap.scaledToWidth(16)))
        else:
            self.setIcon(QIcon())
        self.setText(self.name)
        self.clicked.connect(self.navigate_to_bookmark)

    def navigate_to_bookmark(self):
        self.parent().parent().browser.setUrl(QUrl(self.url))

    def get_favicon(self, url):
        try:
            response = requests.get(f"{url}/favicon.ico")
            if response.status_code == 200:
                return response.content
        except Exception as e:
            print("Failed to fetch favicon:", e)
        return None


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.bookmarks_file = "bookmarks.json"

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl('https://google.com'))
        self.setCentralWidget(self.browser)
        self.showMaximized()

        # Navbar
        navbar = QToolBar()
        navbar.setStyleSheet("QToolBar { background-color: #f0f0f0; border: none; }"
                             "QToolBar::separator { width: 20px; }"
                             "QLineEdit { border: 1px solid #ccc; border-radius: 3px; padding: 5px; }")
        self.addToolBar(navbar)

        # Back button
        back_icon = self.style().standardIcon(QStyle.SP_ArrowBack)
        back_btn = QAction(back_icon, 'Back', self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)

        # Forward button
        forward_icon = self.style().standardIcon(QStyle.SP_ArrowForward)
        forward_btn = QAction(forward_icon, 'Forward', self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)

        # Reload button
        reload_icon = self.style().standardIcon(QStyle.SP_BrowserReload)
        reload_btn = QAction(reload_icon, 'Reload', self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)

        # Home button
        home_icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        home_btn = QAction(home_icon, 'Home', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        # Add Bookmark button
        add_bookmark_icon = self.style().standardIcon(QStyle.SP_DialogSaveButton)
        add_bookmark_btn = QAction(add_bookmark_icon, "Add Bookmark", self)
        add_bookmark_btn.triggered.connect(self.add_bookmark)
        navbar.addAction(add_bookmark_btn)

        # Bookmark buttons
        self.bookmarks = self.load_bookmarks()
        self.bookmark_bar = QToolBar()
        self.bookmark_bar.setStyleSheet("QToolBar { background-color: #f0f0f0; border: none; }")
        self.addToolBar(Qt.BottomToolBarArea, self.bookmark_bar)
        self.update_bookmarks()

        self.browser.urlChanged.connect(self.update_url)
        app.aboutToQuit.connect(self.save_bookmarks)

    def navigate_home(self):
        self.browser.setUrl(QUrl('https://google.com'))

    def navigate_to_url(self):
        url = self.url_bar.text()
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())

    def add_bookmark(self):
        url = self.browser.url().toString()
        name, ok = QInputDialog.getText(self, "Add Bookmark", "Enter bookmark name:")
        if ok and name:
            self.bookmarks[name] = url
            self.update_bookmarks()

    def update_bookmarks(self):
        self.bookmark_bar.clear()
        for name, url in self.bookmarks.items():
            bookmark_button = BookmarkButton(name, url)
            self.bookmark_bar.addWidget(bookmark_button)

    def save_bookmarks(self):
        with open(self.bookmarks_file, 'w') as f:
            json.dump(self.bookmarks, f)

    def load_bookmarks(self):
        try:
            with open(self.bookmarks_file, 'r') as f:
                data = f.read()
                if data:
                    return json.loads(data)
                else:
                    return {}
        except FileNotFoundError:
            return {}
        except json.decoder.JSONDecodeError:
            print("Error loading bookmarks: Invalid JSON data")
            return {}


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    QApplication.setApplicationName('Bytebutler')

    window = MainWindow()
    window.setWindowTitle("Bytebutler")
    window.show()

    sys.exit(app.exec_())
