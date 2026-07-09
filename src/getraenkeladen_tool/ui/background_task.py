"""Kleine, UI-sichere Ausführung langer Arbeiten im Hintergrund.

`BackgroundTask(parent).start(operation, on_success=..., on_error=..., on_finished=...)`
führt `operation` in einem eigenen ``QThread`` aus. Die optionalen Callbacks
werden über Qt-Signale wieder im Thread des ``BackgroundTask`` aufgerufen und
dürfen deshalb Widgets verändern. Ergebnisse müssen reine Werte oder DTOs
sein; ORM-Instanzen dürfen die Thread-Grenze nicht passieren.
"""

from collections.abc import Callable
from weakref import ref

from PySide6.QtCore import QObject, QThread, Signal, Slot


class _TaskWorker(QObject):
    succeeded = Signal(object)
    failed = Signal(object)
    finished = Signal()

    def __init__(self, operation: Callable[[], object]) -> None:
        super().__init__()
        self._operation = operation

    @Slot()
    def run(self) -> None:
        try:
            self.succeeded.emit(self._operation())
        except Exception as exc:
            self.failed.emit(exc)
        finally:
            self.finished.emit()


class BackgroundTask(QObject):
    """Run exactly one callable in a worker thread at a time.

    ``start`` returns ``False`` while a previous callable is still running.
    This keeps calling panels from accidentally starting duplicate imports or
    duplicate document work. The returned result is deliberately untyped:
    callers decide on a small, non-ORM transfer object for their workflow.
    """

    succeeded = Signal(object)
    failed = Signal(object)
    finished = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._thread: QThread | None = None
        self._worker: _TaskWorker | None = None
        self._on_success: Callable[[object], None] | None = None
        self._on_error: Callable[[Exception], None] | None = None
        self._on_finished: Callable[[], None] | None = None
        self._is_shutdown = False
        if parent is not None:
            task_ref = ref(self)

            def shutdown_owned_task(*_args) -> None:
                task = task_ref()
                if task is not None:
                    task.shutdown()

            self._owner_destroyed_callback = shutdown_owned_task
            parent.destroyed.connect(shutdown_owned_task)

    @property
    def is_running(self) -> bool:
        return self._thread is not None

    def start(
        self,
        operation: Callable[[], object],
        *,
        on_success: Callable[[object], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
        on_finished: Callable[[], None] | None = None,
    ) -> bool:
        """Start ``operation`` and deliver its outcome in this object's thread."""
        if self._is_shutdown or self.is_running:
            return False

        self._on_success = on_success
        self._on_error = on_error
        self._on_finished = on_finished
        self._thread = QThread(self)
        self._worker = _TaskWorker(operation)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.succeeded.connect(self._deliver_success)
        self._worker.failed.connect(self._deliver_error)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._finish)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()
        return True

    @Slot()
    def shutdown(self) -> None:
        """Finish active work before the owning widget is destroyed.

        Excel and PDF writes are intentionally not interrupted. Waiting here
        prevents Qt from destroying a still-running ``QThread`` when a panel
        or the application is closed.
        """
        thread = getattr(self, "_thread", None)
        self._is_shutdown = True
        if thread is None:
            return
        self._on_success = None
        self._on_error = None
        self._on_finished = None
        thread.quit()
        thread.wait()
        self._thread = None
        self._worker = None

    @Slot(object)
    def _deliver_success(self, result: object) -> None:
        on_success = getattr(self, "_on_success", None)
        if on_success is not None:
            on_success(result)
        self.succeeded.emit(result)

    @Slot(object)
    def _deliver_error(self, error: Exception) -> None:
        on_error = getattr(self, "_on_error", None)
        if on_error is not None:
            on_error(error)
        self.failed.emit(error)

    @Slot()
    def _finish(self) -> None:
        if self.sender() is not getattr(self, "_thread", None):
            return
        self._thread = None
        self._worker = None
        on_finished = self._on_finished
        self._on_success = None
        self._on_error = None
        self._on_finished = None
        if on_finished is not None:
            on_finished()
        self.finished.emit()
