"""Small Qt wrapper for long-running, parameterless application operations."""

from collections.abc import Callable

from PySide6.QtCore import QObject, QThread, Signal, Slot


class _TaskWorker(QObject):
    succeeded = Signal(object)
    failed = Signal(Exception)
    finished = Signal()

    def __init__(self, operation: Callable[[], object]) -> None:
        super().__init__()
        self._operation = operation

    @Slot()
    def run(self) -> None:
        try:
            self.succeeded.emit(self._operation())
        except Exception as error:
            self.failed.emit(error)
        finally:
            self.finished.emit()


class BackgroundTask(QObject):
    """Run a function off the GUI thread and expose its outcome as Qt signals."""

    succeeded = Signal(object)
    failed = Signal(Exception)
    finished = Signal()

    def __init__(self, operation: Callable[[], object], parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._thread = QThread(self)
        self._worker = _TaskWorker(operation)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.succeeded.connect(self.succeeded)
        self._worker.failed.connect(self.failed)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self.finished)

    def start(self) -> None:
        self._thread.start()
