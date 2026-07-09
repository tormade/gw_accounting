import os
import threading
import time


def _app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


def _wait_until(predicate, timeout_seconds: float = 2.0) -> None:
    app = _app()
    deadline = time.monotonic() + timeout_seconds
    while not predicate() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.005)
    app.processEvents()
    assert predicate()


def test_background_task_runs_work_off_the_ui_thread_and_reports_the_result():
    from getraenkeladen_tool.ui.background_task import BackgroundTask

    _app()
    ui_thread = threading.get_ident()
    worker_threads: list[int] = []
    callbacks: list[tuple[str, int]] = []
    task = BackgroundTask()

    assert task.start(
        lambda: worker_threads.append(threading.get_ident()) or "fertig",
        on_success=lambda result: callbacks.append((result, threading.get_ident())),
    ) is True

    _wait_until(lambda: bool(callbacks) and not task.is_running)

    assert worker_threads != [ui_thread]
    assert callbacks == [("fertig", ui_thread)]


def test_background_task_reports_errors_and_returns_to_idle_state():
    from getraenkeladen_tool.ui.background_task import BackgroundTask

    _app()
    errors: list[Exception] = []
    task = BackgroundTask()

    assert task.start(
        lambda: (_ for _ in ()).throw(ValueError("Arbeitsdatei fehlt")),
        on_error=errors.append,
    ) is True

    _wait_until(lambda: bool(errors) and not task.is_running)

    assert len(errors) == 1
    assert isinstance(errors[0], ValueError)
    assert str(errors[0]) == "Arbeitsdatei fehlt"


def test_background_task_refuses_a_second_start_while_the_first_is_running():
    from getraenkeladen_tool.ui.background_task import BackgroundTask

    _app()
    release = threading.Event()
    finished: list[bool] = []
    task = BackgroundTask()

    assert task.start(lambda: release.wait(1), on_finished=lambda: finished.append(True)) is True
    assert task.start(lambda: None) is False
    release.set()
    _wait_until(lambda: finished and not task.is_running)


def test_background_task_shutdown_waits_for_running_work_and_returns_to_idle():
    from getraenkeladen_tool.ui.background_task import BackgroundTask

    _app()
    started = threading.Event()
    release = threading.Event()
    task = BackgroundTask()

    assert task.start(lambda: started.set() or release.wait(1)) is True
    _wait_until(started.is_set)
    timer = threading.Timer(0.05, release.set)
    timer.start()

    task.shutdown()
    timer.join()

    assert task.is_running is False

    assert task.start(lambda: "nicht mehr starten") is False


def test_background_task_can_be_reused_after_a_normal_finish():
    from getraenkeladen_tool.ui.background_task import BackgroundTask

    _app()
    results: list[str] = []
    task = BackgroundTask()

    assert task.start(lambda: "eins", on_success=results.append) is True
    _wait_until(lambda: results == ["eins"] and not task.is_running)
    assert task.start(lambda: "zwei", on_success=results.append) is True
    _wait_until(lambda: results == ["eins", "zwei"] and not task.is_running)
