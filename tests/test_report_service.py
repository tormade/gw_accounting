from pathlib import Path

from getraenkeladen_tool.schemas import CustomerCreate, DocumentCreate, DocumentLineItem
from getraenkeladen_tool.services.customer_service import create_customer
from getraenkeladen_tool.services.document_service import create_document
from getraenkeladen_tool.services.report_service import (
    export_daily_deliveries_csv,
    export_due_contacts_csv,
    export_open_items_csv,
    get_dashboard_summary,
    list_daily_deliveries,
    list_due_contacts,
    list_open_items,
    mark_open_item_paid,
)


def test_list_open_items_and_mark_payment_received(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(
            name="Cafe Nord",
            folder_path=str(tmp_path / "Kunden" / "Cafe Nord"),
            payment_method="Ueberweisung",
        ),
    )
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Rechnung",
            document_number="RG-1004",
            line_items=[
                DocumentLineItem(
                    name="Wasser 0,7",
                    quantity=3,
                    unit_price_cents=1299,
                    deposit_cents=330,
                )
            ],
        ),
    )

    open_items = list_open_items(session)
    assert len(open_items) == 1
    assert open_items[0].customer_name == "Cafe Nord"
    assert open_items[0].document_number == "RG-1004"
    assert open_items[0].amount_cents == 4887
    assert open_items[0].status == "offen"

    paid_item = mark_open_item_paid(session, open_items[0].id)

    assert paid_item.status == "bezahlt"
    assert list_open_items(session) == []


def test_list_due_contacts_filters_by_target_date(session, tmp_path: Path):
    due_customer = create_customer(
        session,
        CustomerCreate(
            name="Hotel Blau",
            folder_path=str(tmp_path / "Kunden" / "Hotel Blau"),
            next_contact_date="2026-06-21",
        ),
    )
    create_customer(
        session,
        CustomerCreate(
            name="Spaeter Kunde",
            folder_path=str(tmp_path / "Kunden" / "Spaeter Kunde"),
            next_contact_date="2026-06-22",
        ),
    )

    due_contacts = list_due_contacts(session, target_date="2026-06-21")

    assert due_contacts == [due_customer]


def test_list_daily_deliveries_filters_by_delivery_date_and_slot(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(
            name="Gasthof Sued",
            folder_path=str(tmp_path / "Kunden" / "Gasthof Sued"),
        ),
    )
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Lieferschein",
            document_number="LS-2001",
            delivery_date="2026-06-21",
            delivery_slot="vormittag",
            line_items=[
                DocumentLineItem(
                    name="Apfelschorle",
                    quantity=5,
                    unit_price_cents=1499,
                    deposit_cents=330,
                )
            ],
        ),
    )

    deliveries = list_daily_deliveries(session, target_date="2026-06-21")

    assert len(deliveries) == 1
    assert deliveries[0].customer.name == "Gasthof Sued"
    assert deliveries[0].document_number == "LS-2001"
    assert deliveries[0].delivery_slot == "vormittag"


def test_list_daily_deliveries_excludes_invoices_with_delivery_date(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(
            name="Cafe Nord",
            folder_path=str(tmp_path / "Kunden" / "Cafe Nord"),
        ),
    )
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Rechnung",
            document_number="RG-1007",
            delivery_date="2026-06-21",
            delivery_slot="vormittag",
            line_items=[
                DocumentLineItem(
                    name="Wasser 0,7",
                    quantity=1,
                    unit_price_cents=1299,
                    deposit_cents=330,
                )
            ],
        ),
    )

    assert list_daily_deliveries(session, target_date="2026-06-21") == []


def test_export_open_items_csv_writes_payment_overview(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(
            name="Cafe Nord",
            folder_path=str(tmp_path / "Kunden" / "Cafe Nord"),
            payment_method="SEPA",
        ),
    )
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Rechnung",
            document_number="RG-1005",
            line_items=[
                DocumentLineItem(
                    name="Wasser 0,7",
                    quantity=2,
                    unit_price_cents=1299,
                    deposit_cents=330,
                )
            ],
        ),
    )

    output_path = export_open_items_csv(session, tmp_path / "offene_posten.csv")

    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8").splitlines() == [
        "Kunde;Rechnungsnr.;Rechnungsdatum;Faelligkeit;Zahlart;Betrag EUR;Status",
        "Cafe Nord;RG-1005;;;SEPA;32,58;offen",
    ]


def test_export_open_items_csv_includes_due_date_for_bank_transfer(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(
            name="Ueberweisung Kunde",
            folder_path=str(tmp_path / "Kunden" / "Ueberweisung Kunde"),
            payment_method="Ueberweisung",
        ),
    )
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Rechnung",
            document_number="RG-UE-1",
            delivery_date="2026-06-24",
            line_items=[DocumentLineItem(name="Wasser", quantity=1, unit_price_cents=1000)],
        ),
    )

    output_path = export_open_items_csv(session, tmp_path / "offene_posten.csv")

    assert output_path.read_text(encoding="utf-8").splitlines() == [
        "Kunde;Rechnungsnr.;Rechnungsdatum;Faelligkeit;Zahlart;Betrag EUR;Status",
        "Ueberweisung Kunde;RG-UE-1;2026-06-24;2026-07-01;Ueberweisung;10,00;offen",
    ]


def test_export_daily_deliveries_csv_includes_customer_notes(session, tmp_path: Path):
    customer = create_customer(
        session,
        CustomerCreate(
            name="Gasthof Sued",
            folder_path=str(tmp_path / "Kunden" / "Gasthof Sued"),
            address="Dorfstr. 1",
            delivery_notes="Hofeinfahrt nutzen",
            opening_hours="ab 9 Uhr",
        ),
    )
    create_document(
        session,
        DocumentCreate(
            customer_id=customer.id,
            document_type="Lieferschein",
            document_number="LS-2002",
            delivery_date="2026-06-21",
            delivery_slot="vormittag",
            line_items=[
                DocumentLineItem(
                    name="Apfelschorle",
                    quantity=4,
                    unit_price_cents=1499,
                    deposit_cents=330,
                )
            ],
        ),
    )

    output_path = export_daily_deliveries_csv(session, "2026-06-21", tmp_path / "lieferliste.csv")

    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8").splitlines() == [
        "Datum;Zeitfenster;Belegnr.;Kunde;Adresse;Hinweise;Oeffnungszeiten",
        "2026-06-21;vormittag;LS-2002;Gasthof Sued;Dorfstr. 1;Hofeinfahrt nutzen;ab 9 Uhr",
    ]


def test_export_due_contacts_csv_writes_contact_request_list(session, tmp_path: Path):
    create_customer(
        session,
        CustomerCreate(
            name="Hotel Blau",
            folder_path=str(tmp_path / "Kunden" / "Hotel Blau"),
            contact_email="bestellung@hotel-blau.test",
            next_contact_date="2026-06-21",
            delivery_notes="Bestellung per Mail anfragen",
        ),
    )

    output_path = export_due_contacts_csv(session, "2026-06-21", tmp_path / "kontakte.csv")

    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8").splitlines() == [
        "Kontakttermin;Kunde;E-Mail;Hinweise",
        "2026-06-21;Hotel Blau;bestellung@hotel-blau.test;Bestellung per Mail anfragen",
    ]


def test_dashboard_summary_counts_daily_work(session, tmp_path: Path):
    delivery_customer = create_customer(
        session,
        CustomerCreate(
            name="Gasthof Sued",
            folder_path=str(tmp_path / "Kunden" / "Gasthof Sued"),
            next_contact_date="2026-06-21",
        ),
    )
    invoice_customer = create_customer(
        session,
        CustomerCreate(
            name="Cafe Nord",
            folder_path=str(tmp_path / "Kunden" / "Cafe Nord"),
            payment_method="SEPA",
        ),
    )
    create_document(
        session,
        DocumentCreate(
            customer_id=delivery_customer.id,
            document_type="Lieferschein",
            document_number="LS-3001",
            delivery_date="2026-06-21",
            delivery_slot="vormittag",
            line_items=[DocumentLineItem(name="Wasser", quantity=1, unit_price_cents=1000)],
        ),
    )
    create_document(
        session,
        DocumentCreate(
            customer_id=invoice_customer.id,
            document_type="Rechnung",
            document_number="RG-3001",
            line_items=[DocumentLineItem(name="Limo", quantity=2, unit_price_cents=1200)],
        ),
    )

    summary = get_dashboard_summary(session, "2026-06-21")

    assert summary.delivery_count == 1
    assert summary.open_item_count == 1
    assert summary.due_contact_count == 1
    assert summary.next_steps == (
        "Lieferliste fuer 2026-06-21 pruefen.",
        "Offene Posten kontrollieren und Zahlungseingaenge markieren.",
        "Faellige Kundenkontakte abarbeiten.",
    )
