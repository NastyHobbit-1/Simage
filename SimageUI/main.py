"""
SimageUI main entrypoint.
A fast, multi-tab image pipeline UI for the Simage project.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget
from PySide6.QtCore import Qt

from ui_gallery import GalleryTab
#from ui_edit import EditTab
#from ui_batch import BatchTab
#from ui_settings import SettingsTab
#from ui_viewer import ViewerTab

class SimageUIMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simage UI Pipeline")
        self.resize(1200, 800)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.setTabsClosable(False)
        self.tabs.setMovable(True)
        self.tabs.addTab(GalleryTab(self), "Gallery/Search")
        #self.tabs.addTab(EditTab(self), "Edit")
        #self.tabs.addTab(BatchTab(self), "Batch")
        #self.tabs.addTab(SettingsTab(self), "Settings")
        #self.tabs.addTab(ViewerTab(self), "Full Viewer")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SimageUIMain()
    win.show()
    sys.exit(app.exec())
