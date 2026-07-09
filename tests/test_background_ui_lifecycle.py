import threading
import time
from types import SimpleNamespace


def _app():
    import os

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


def test_settings_preview_disables_and_reactivates_its_triggers(monkeypatch, tmp_path):
    import getraenkeladen_tool.ui.settings_panel as settings_module

    _app()
    panel = settings_module.SettingsPanel(session_factory=lambda: object())
    started = threading.Event()
    release = threading.Event()

    def preview_operation(_session_factory, _input_dir):
        started.set()
        release.wait(1)
        return object()

    monkeypatch.setattr(settings_module, "_preview_master_data_in_background", preview_operation)
    monkeypatch.setattr(panel, "_show_preview", lambda *_args, **_kwargs: None)

    panel._start_preview(tmp_path, confirm_import=False)
    _wait_until(started.is_set)

    assert panel.preview_master_data_button.isEnabled() is False
    assert panel.import_master_data_button.isEnabled() is False
    assert panel.input_folder.isReadOnly() is True

    release.set()
    _wait_until(lambda: not panel._preview_task.is_running)

    assert panel.preview_master_data_button.isEnabled() is True
    assert panel.import_master_data_button.isEnabled() is True
    assert panel.input_folder.isReadOnly() is False


def test_settings_preview_reactivates_after_background_error(monkeypatch, tmp_path):
    import getraenkeladen_tool.ui.settings_panel as settings_module

    _app()
    panel = settings_module.SettingsPanel(session_factory=lambda: object())
    monkeypatch.setattr(
        settings_module,
        "_preview_master_data_in_background",
        lambda _session_factory, _input_dir: (_ for _ in ()).throw(ValueError("Excel beschädigt")),
    )

    panel._start_preview(tmp_path, confirm_import=False)
    _wait_until(lambda: not panel._preview_task.is_running)

    assert panel.preview_master_data_button.isEnabled() is True
    assert panel.import_master_data_button.isEnabled() is True
    assert panel.status_label.text() == "Excel-Vorgang fehlgeschlagen: Excel beschädigt"


def test_customer_folder_reactivates_selection_after_background_load(monkeypatch):
    import getraenkeladen_tool.ui.customer_folder_panel as customer_folder_module

    _app()
    panel = customer_folder_module.CustomerFolderPanel(session_factory=None)
    panel.session_factory = lambda: object()
    started = threading.Event()
    release = threading.Event()

    def load_operation(_session_factory, _customer_id):
        started.set()
        release.wait(1)
        return object()

    monkeypatch.setattr(customer_folder_module, "_load_customer_context_in_background", load_operation)
    monkeypatch.setattr(panel, "_show_loaded_customer_context", lambda _result: None)

    panel._start_customer_loading(7)
    _wait_until(started.is_set)

    assert panel.customer_select.isEnabled() is False

    release.set()
    _wait_until(lambda: not panel._customer_load_task.is_running)

    assert panel.customer_select.isEnabled() is True


def test_customer_folder_does_not_reactivate_actions_for_a_stale_customer_after_load_error(
    monkeypatch,
    tmp_path,
):
    import getraenkeladen_tool.ui.customer_folder_panel as customer_folder_module

    _app()
    panel = customer_folder_module.CustomerFolderPanel(session_factory=None)
    old_snapshot = SimpleNamespace(
        customer=SimpleNamespace(id=1, name="Cafe Alt"),
        folder_path=tmp_path,
        folder_exists=True,
        files=[],
        orders=[],
    )
    panel.customer_select.set_items([("Cafe Alt", 1), ("Cafe Neu", 2)])
    panel.show_snapshot(old_snapshot, [])
    panel.customer_select.select_value(2)
    panel.session_factory = lambda: object()
    monkeypatch.setattr(
        customer_folder_module,
        "_load_customer_context_in_background",
        lambda _session_factory, _customer_id: (_ for _ in ()).throw(ValueError("Ordner nicht lesbar")),
    )
    monkeypatch.setattr(panel, "_show_customer_load_error", lambda _error: None)

    panel._start_customer_loading(2)
    _wait_until(lambda: not panel._customer_load_task.is_running)

    assert panel.current_customer_id is None
    assert panel.current_folder_path is None
    assert panel.new_order_button.isEnabled() is False
    assert panel.open_folder_button.isEnabled() is False


def test_document_creation_disables_and_reactivates_its_actions(monkeypatch):
    import getraenkeladen_tool.ui.document_workflow_panel as document_module

    _app()
    panel = document_module.DeliveryNotePanel(session_factory=None)
    panel.session_factory = lambda: object()
    started = threading.Event()
    release = threading.Event()

    def create_operation(*_args):
        started.set()
        release.wait(1)
        return object()

    monkeypatch.setattr(document_module, "_create_document_in_background", create_operation)
    monkeypatch.setattr(panel, "_handle_document_created", lambda _result, _asset_label: None)
    request = document_module.DocumentCreationRequest(
        order_id=17,
        document_number="LS-17",
        line_items=(),
        deposit_returns=(),
        delivery_fee_enabled=False,
        note=None,
        assets=frozenset({"excel", "pdf"}),
    )

    panel._start_document_creation(request, "Excel + PDF")
    _wait_until(started.is_set)

    assert panel.create_both_button.isEnabled() is False
    assert panel.change_order_button.isEnabled() is False

    release.set()
    _wait_until(lambda: not panel._document_task.is_running)

    assert panel.create_both_button.isEnabled() is True
    assert panel.change_order_button.isEnabled() is True
