import pytest
from PySide6.QtWidgets import QApplication
import sys
import os

# Import main UI class
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ui'))
from ui.main import SimageUIMain

@pytest.fixture(scope="module")
def app():
    return QApplication([])

def test_ui_tabs_exist(app):
    win = SimageUIMain()
    tab_names = [win.tabs.tabText(i) for i in range(win.tabs.count())]
    # Should include all enabled tabs
    assert "Gallery & Search" in tab_names
    assert "Tag Images" in tab_names
    # The following tabs may be present if implemented
    for name in ["Edit Images", "Batch Processing", "Settings", "Full Image Viewer"]:
        # If the tab is present, it should be enabled
        if name in tab_names:
            assert win.tabs.isTabEnabled(tab_names.index(name))

def test_drag_and_drop_sets_input_dir(app):
    win = SimageUIMain()
    # Simulate drop event
    class DummyEvent:
        def mimeData(self):
            class DummyMime:
                def hasUrls(self): return True
                def urls(self):
                    class DummyUrl:
                        def toLocalFile(self):
                            return os.getcwd()  # Use current dir as test
                    return [DummyUrl()]
            return DummyMime()
        def acceptProposedAction(self): pass
    win.dropEvent(DummyEvent())
    assert hasattr(win, 'input_dir')
    assert win.input_dir == os.getcwd()

def test_run_pipeline_button(app):
    from PySide6.QtWidgets import QPushButton
    win = SimageUIMain()
    btn = win.findChild(QPushButton, "runPipelineButton")
    assert btn is not None
