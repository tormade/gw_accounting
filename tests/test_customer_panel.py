from getraenkeladen_tool.models import Customer
from getraenkeladen_tool.schemas import CustomerCreate
from getraenkeladen_tool.services.customer_service import create_customer


def _app():
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


def _imported_customer(session):
    return create_customer(
        session,
        CustomerCreate(
            name="Cafe Nord",
            folder_path="Kunden/Cafe Nord",
            address="Hauptstraße 4",
            phone="089 123456",
            contact_name="Mia Muster",
            contact_email="mia@cafe-nord.de",
            payment_method="SEPA",
            next_contact_date="2026-07-15",
            delivery_notes="Hintereingang verwenden",
            opening_hours="Mo-Fr 08:00-16:00",
            internal_notes="Rechnung immer per E-Mail senden",
        ),
    )


def _load_customer_into_panel(session, customer):
    from getraenkeladen_tool.ui.customer_panel import CustomerPanel

    panel = CustomerPanel(session_factory=lambda: session)
    panel.show_customers([customer])
    panel.customers_table.selectRow(0)
    panel.load_selected_customer()
    return panel


def test_customer_panel_shows_imported_details_in_a_collapsible_section(session):
    _app()
    customer = _imported_customer(session)

    panel = _load_customer_into_panel(session, customer)

    assert panel.additional_details_button.text() == "Weitere Kundendaten"
    assert panel.additional_details_button.isCheckable()
    assert not panel.additional_details_content.isHidden()
    assert panel.phone.text() == "089 123456"
    assert panel.contact_name.text() == "Mia Muster"
    assert panel.contact_email.text() == "mia@cafe-nord.de"
    assert panel.payment_method.text() == "SEPA"
    assert panel.opening_hours.text() == "Mo-Fr 08:00-16:00"
    assert panel.internal_notes.text() == "Rechnung immer per E-Mail senden"


def test_customer_panel_does_not_cap_the_expanded_customer_form_height():
    from pathlib import Path

    source = Path("src/getraenkeladen_tool/ui/customer_panel.py").read_text(encoding="utf-8")

    assert "edit_box.setMaximumHeight" not in source


def test_customer_panel_preserves_imported_details_when_saving_an_edit(session):
    _app()
    customer = _imported_customer(session)
    panel = _load_customer_into_panel(session, customer)

    panel.address.setText("Hauptstraße 6")
    panel.phone.setText("089 654321")
    panel.save_customer()

    session.expire_all()
    stored = session.get(Customer, customer.id)
    assert stored is not None
    assert stored.address == "Hauptstraße 6"
    assert stored.phone == "089 654321"
    assert stored.contact_name == "Mia Muster"
    assert stored.contact_email == "mia@cafe-nord.de"
    assert stored.payment_method == "SEPA"
    assert stored.opening_hours == "Mo-Fr 08:00-16:00"
    assert stored.internal_notes == "Rechnung immer per E-Mail senden"


def test_customer_panel_discard_restores_all_loaded_customer_details(session):
    _app()
    customer = _imported_customer(session)
    panel = _load_customer_into_panel(session, customer)

    panel.phone.setText("089 999999")
    panel.contact_name.setText("Andere Ansprechperson")
    panel.contact_email.setText("andere@example.test")
    panel.payment_method.setText("Überweisung")
    panel.opening_hours.setText("geschlossen")
    panel.internal_notes.setText("nicht behalten")
    panel.discard_changes()

    assert panel.phone.text() == "089 123456"
    assert panel.contact_name.text() == "Mia Muster"
    assert panel.contact_email.text() == "mia@cafe-nord.de"
    assert panel.payment_method.text() == "SEPA"
    assert panel.opening_hours.text() == "Mo-Fr 08:00-16:00"
    assert panel.internal_notes.text() == "Rechnung immer per E-Mail senden"
