"""
Fast, virtualized thumbnail grid widget for SimageUI.
"""

from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap
import os
from image_scanner import ensure_thumbnails_for_folder

class ThumbnailGrid(QWidget):
    image_selected = Signal(str, str)  # (image_path, thumb_path)

    def __init__(self, parent=None, folder=None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.layout.setSpacing(4)
        self.layout.setContentsMargins(0,0,0,0)
        self.thumbs = []
        self.folder = folder or os.getcwd()
        self.load_thumbnails(self.folder)

    def load_thumbnails(self, folder):
        # Clear old
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.thumbs = ensure_thumbnails_for_folder(folder)
        cols = 8
        for i, thumb_path in enumerate(self.thumbs):
            label = QLabel()
            label.setFixedSize(128, 128)
            label.setStyleSheet("background: #222; border: 1px solid #888;")
            label.setAlignment(Qt.AlignCenter)
            if os.path.exists(thumb_path):
                pix = QPixmap(thumb_path)
                label.setPixmap(pix.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                label.setText("?")
            label.mousePressEvent = self._make_select_handler(i)
            self.layout.addWidget(label, i // cols, i % cols)

    def _make_select_handler(self, idx):
        def handler(event):
            if 0 <= idx < len(self.thumbs):
                img_path = self.thumbs[idx].replace('.thumbnails', '').replace('\\', os.sep).replace('/', os.sep)
                self.image_selected.emit(img_path, self.thumbs[idx])
        return handler

    def sizeHint(self):
        return QSize(1024, 600)
