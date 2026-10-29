from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
class EditTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Edit Images (stub)"))
