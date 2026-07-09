import pytest


def _dispose_widgets(*widgets):
    from PySide6.QtCore import QCoreApplication, QEvent

    for widget in widgets:
        widget.close()
        widget.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    _app().processEvents()


def _app():
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


def test_set_button_role_uses_a_semantic_dynamic_property():
    _app()
    from PySide6.QtWidgets import QPushButton
    from getraenkeladen_tool.ui.layouts import set_button_role

    button = QPushButton("Speichern")

    set_button_role(button, "primary")

    assert button.property("role") == "primary"


def test_set_button_role_rejects_unknown_roles():
    _app()
    from PySide6.QtWidgets import QPushButton
    from getraenkeladen_tool.ui.layouts import set_button_role

    with pytest.raises(ValueError, match="Unbekannte Button-Rolle"):
        set_button_role(QPushButton("Speichern"), "warning")


def test_theme_defines_all_semantic_button_roles():
    from getraenkeladen_tool.ui.theme import APP_STYLESHEET

    for role in ("primary", "secondary", "danger", "quiet"):
        assert f'QPushButton[role="{role}"]' in APP_STYLESHEET


def test_main_workflows_assign_roles_by_intent_instead_of_object_name():
    _app()
    from PySide6.QtWidgets import QPushButton
    from getraenkeladen_tool.ui.customer_folder_panel import CustomerFolderPanel
    from getraenkeladen_tool.ui.document_workflow_panel import DeliveryNotePanel
    from getraenkeladen_tool.ui.order_panel import OrderPanel
    from getraenkeladen_tool.ui.settings_panel import SettingsPanel

    customer_folder = CustomerFolderPanel(session_factory=None)
    document = DeliveryNotePanel(session_factory=None)
    order = OrderPanel(session_factory=None)
    settings = SettingsPanel(session_factory=None)

    try:
        assert customer_folder.new_order_button.property("role") == "primary"
        assert customer_folder.open_folder_button.property("role") == "quiet"
        assert document.create_both_button.property("role") == "primary"
        assert document.change_order_button.property("role") == "secondary"
        assert document.remove_line_button.property("role") == "danger"
        assert order.save_order_button.property("role") == "primary"
        assert order.remove_line_button.property("role") == "danger"
        assert settings.import_master_data_button.property("role") == "primary"
        assert settings.preview_master_data_button.property("role") == "secondary"
        for panel in (customer_folder, document, order, settings):
            primary_buttons = [
                button
                for button in panel.findChildren(QPushButton)
                if button.property("role") == "primary"
            ]
            assert len(primary_buttons) <= 1
    finally:
        _dispose_widgets(customer_folder, document, order, settings)


def test_every_application_push_button_has_a_semantic_role():
    _app()
    from PySide6.QtWidgets import QPushButton
    from getraenkeladen_tool.ui.main_window import MainWindow

    window = MainWindow(session_factory=None)
    try:
        unassigned = [
            (button.objectName(), button.text())
            for button in window.findChildren(QPushButton)
            if button.property("role") not in {"primary", "secondary", "danger", "quiet"}
        ]

        assert unassigned == []
    finally:
        _dispose_widgets(window)
