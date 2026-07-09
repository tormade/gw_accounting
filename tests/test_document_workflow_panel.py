from pathlib import Path
from types import SimpleNamespace

import pytest


def _app():
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


def test_document_workflow_offers_visible_change_order_action_after_selection(monkeypatch):
    _app()
    from getraenkeladen_tool.ui.document_workflow_panel import DeliveryNotePanel

    selected_order = SimpleNamespace(
        id=17,
        order_number="BEST-17",
        customer=SimpleNamespace(name="Cafe Nord"),
        delivery_date="2026-07-09",
        lines=[SimpleNamespace(product_name="Wasser", quantity=2, unit_price_cents=700, deposit_cents=330)],
        deposit_returns=[SimpleNamespace(name="Pfand 3,10 EUR", quantity=1, deposit_cents=310)],
    )
    monkeypatch.setattr(
        "getraenkeladen_tool.ui.document_workflow_panel.get_order",
        lambda _session, _order_id: selected_order,
    )

    panel = DeliveryNotePanel(session_factory=None)
    panel.session_factory = lambda: SimpleNamespace(close=lambda: None)

    panel.select_order(selected_order.id)

    assert panel.current_order_id == selected_order.id
    assert panel.order_box.isHidden() is True
    assert panel.change_order_button.isHidden() is False
    assert panel.lines_table.rowCount() == 1
    assert panel.returns_table.rowCount() == 1

    panel.reset_order_selection()

    assert panel.current_order_id is None
    assert panel.order_box.isHidden() is False
    assert panel.change_order_button.isHidden() is True
    assert panel.order_summary.text() == "Noch keine Bestellung ausgewählt."
    assert panel.lines_table.rowCount() == 0
    assert panel.returns_table.rowCount() == 0
    assert panel.total_label.text() == "Gesamtsumme: 0,00 EUR"


def test_document_workflow_uses_shared_background_task_for_generation():
    source = Path("src/getraenkeladen_tool/ui/document_workflow_panel.py").read_text(encoding="utf-8")

    assert "from .background_task import BackgroundTask" in source
    assert "self._document_task.start(" in source
    assert "def _set_document_creation_running" in source
    assert "def _create_document_in_background" in source


def test_document_background_operation_returns_a_primitive_result(monkeypatch):
    from getraenkeladen_tool.ui.document_workflow_panel import (
        DocumentCreationRequest,
        _create_document_in_background,
    )

    session = SimpleNamespace(closed=False)
    session.close = lambda: setattr(session, "closed", True)
    monkeypatch.setattr(
        "getraenkeladen_tool.ui.document_workflow_panel.verify_document_assets",
        lambda _session, _document_id, expected_assets: SimpleNamespace(ok=expected_assets == {"excel", "pdf"}),
    )
    request = DocumentCreationRequest(
        order_id=17,
        document_number="LS-17",
        line_items=(),
        deposit_returns=(),
        delivery_fee_enabled=False,
        note=None,
        assets=frozenset({"excel", "pdf"}),
    )

    result = _create_document_in_background(
        lambda: session,
        lambda _session, _request: SimpleNamespace(
            id=23,
            document_number="LS-17",
            excel_path="/tmp/LS-17.xlsx",
            pdf_path="/tmp/LS-17.pdf",
        ),
        request,
    )

    assert result.document_id == 23
    assert result.document_number == "LS-17"
    assert result.excel_path == "/tmp/LS-17.xlsx"
    assert result.pdf_path == "/tmp/LS-17.pdf"
    assert session.closed is True


def test_document_background_operation_fails_when_expected_assets_are_missing(monkeypatch):
    from getraenkeladen_tool.ui.document_workflow_panel import (
        DocumentCreationRequest,
        _create_document_in_background,
    )

    session = SimpleNamespace(closed=False)
    session.close = lambda: setattr(session, "closed", True)
    monkeypatch.setattr(
        "getraenkeladen_tool.ui.document_workflow_panel.verify_document_assets",
        lambda _session, _document_id, expected_assets: SimpleNamespace(
            ok=False,
            checks=(SimpleNamespace(ok=False, message="PDF-Datei vorhanden."),),
        ),
    )
    request = DocumentCreationRequest(
        order_id=17,
        document_number="LS-17",
        line_items=(),
        deposit_returns=(),
        delivery_fee_enabled=False,
        note=None,
        assets=frozenset({"pdf"}),
    )

    with pytest.raises(RuntimeError, match="Belegprüfung fehlgeschlagen.*PDF-Datei"):
        _create_document_in_background(
            lambda: session,
            lambda _session, _request: SimpleNamespace(
                id=23,
                document_number="LS-17",
                excel_path="/tmp/LS-17.xlsx",
                pdf_path="/tmp/LS-17.pdf",
            ),
            request,
        )

    assert session.closed is True
