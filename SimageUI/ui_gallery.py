"""
Gallery/Search tab for SimageUI.
Fast, scrollable, async thumbnail grid for large image sets.
"""


from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSplitter, QSizePolicy, QTextEdit, QFrame
from PySide6.QtCore import Qt
from thumbnail_grid import ThumbnailGrid

class GalleryTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)

        # Left: Thumbnail grid
        grid_widget = QWidget()
        grid_layout = QVBoxLayout(grid_widget)

        self.grid = ThumbnailGrid()
        self.grid.image_selected.connect(self.on_image_selected)
        grid_layout.addWidget(self.grid)
        grid_widget.setLayout(grid_layout)
        splitter.addWidget(grid_widget)
    def on_image_selected(self, img_path, thumb_path):
        from PySide6.QtGui import QPixmap
        import os
        # Show preview
        if os.path.exists(img_path):
            pix = QPixmap(img_path)
            self.image_preview.setPixmap(pix.scaled(
                self.image_preview.width(),
                self.image_preview.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation))
        else:
            self.image_preview.setText("Image not found")
        # Show info (basic for now)
        info = f"Path: {img_path}\nThumbnail: {thumb_path}"
        self.info_window.setPlainText(info)

        # Right: Side panel (image preview + info)
        side_panel = QWidget()
        side_layout = QVBoxLayout(side_panel)
        self.image_preview = QLabel("Select an image")
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setMinimumSize(256, 256)
        self.image_preview.setFrameShape(QFrame.Box)
        self.image_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        side_layout.addWidget(self.image_preview)

        self.info_window = QTextEdit()
        self.info_window.setReadOnly(True)
        self.info_window.setMinimumHeight(120)
        side_layout.addWidget(self.info_window)
        side_panel.setLayout(side_layout)
        splitter.addWidget(side_panel)

        splitter.setSizes([900, 300])
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
