from PySide6.QtCore import QEventLoop
from PySide6.QtWidgets import QApplication

from getraenkeladen_tool.ui.background_task import BackgroundTask


def test_background_task_emits_function_result():
    QApplication.instance() or QApplication([])
    loop = QEventLoop()
    results = []
    task = BackgroundTask(lambda: "fertig")
    task.succeeded.connect(results.append)
    task.finished.connect(loop.quit)

    task.start()
    loop.exec()

    assert results == ["fertig"]
