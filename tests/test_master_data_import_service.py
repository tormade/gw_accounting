from datetime import datetime

from openpyxl import Workbook

from getraenkeladen_tool.models import Customer, Product
from getraenkeladen_tool.schemas import CustomerCreate, ProductCreate
from getraenkeladen_tool.services.customer_service import archive_customer, create_customer
from getraenkeladen_tool.services.master_data_import_service import import_master_data_from_folder, preview_master_data_from_folder
from getraenkeladen_tool.services.product_service import create_product, deactivate_product


def test_import_master_data_reads_excel_sources_without_modifying_files(session, tmp_path):
    input_dir = tmp_path / "Input"
    input_dir.mkdir()
    article_file = input_dir / "Artikel Liste Preise.xlsx"
    customer_file = input_dir / "Lieferkunden Liste.xlsx"
    _write_article_file(article_file, [["Wasser 12x1,0 PET", 12, 1, 5.11, 4.8, 10.3]])
    _write_customer_file(
        customer_file,
        [
            [
                1,
                "Metzgerei Karl",
                datetime(2026, 6, 22),
                "",
                12,
                datetime(2026, 7, 20),
                4,
                "Moosburger Str.",
                "55",
                "85406",
                "Zolling",
                "08167 9890720",
                "0151 11574740",
                "info@metzgerei-karl.de",
                "rechnung@metzgerei-karl.de",
                "Frau Karl",
                "bis13Uhr und ab 15 Uhr",
                "alle 2 Wochen",
                "x",
            ]
        ],
    )
    article_mtime = article_file.stat().st_mtime_ns
    customer_mtime = customer_file.stat().st_mtime_ns

    result = import_master_data_from_folder(session, input_dir)

    assert result.products_created == 1
    assert result.customers_created == 1
    assert article_file.stat().st_mtime_ns == article_mtime
    assert customer_file.stat().st_mtime_ns == customer_mtime

    product = result.products[0]
    assert product.name == "Wasser 12x1,0 PET"
    assert product.standard_price_cents == 1030
    assert product.default_deposit_cents == 480

    customer = result.customers[0]
    assert customer.name == "Metzgerei Karl"
    assert customer.address == "Moosburger Str. 55, 85406 Zolling"
    assert customer.next_contact_date == "2026-07-20"
    assert customer.contact_email == "info@metzgerei-karl.de"
    assert customer.payment_method is None
    assert "bis13Uhr" in customer.delivery_notes


def test_import_updates_existing_records_but_keeps_archived_status_and_tracks_changes(session, tmp_path):
    input_dir = tmp_path / "Input"
    input_dir.mkdir()
    _write_article_file(input_dir / "Artikel Liste Preise.xlsx", [["Cola 20x0,5", 20, 0.5, 8.0, 3.1, 15.5]])
    _write_customer_file(
        input_dir / "Lieferkunden Liste.xlsx",
        [
            [
                2,
                "Cafe Nord",
                datetime(2026, 6, 1),
                "",
                "",
                datetime(2026, 7, 1),
                4,
                "Neue Str.",
                "7",
                "85354",
                "Freising",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ]
        ],
    )
    customer = create_customer(
        session,
        CustomerCreate(name="Cafe Nord", folder_path="Kunden/Cafe Nord", address="Alte Str. 1, 85354 Freising"),
    )
    product = create_product(session, ProductCreate(name="Cola 20x0,5", unit="Kiste", standard_price_cents=1499))
    archive_customer(session, customer.id)
    deactivate_product(session, product.id)

    result = import_master_data_from_folder(session, input_dir)

    assert result.customers_updated == 1
    assert result.products_updated == 1
    assert result.customers[0].is_active is False
    assert result.products[0].is_active is False

    address_changes = [change for change in result.changes if change.entity_type == "customer" and change.field_name == "address"]
    price_changes = [change for change in result.changes if change.entity_type == "product" and change.field_name == "standard_price_cents"]
    assert address_changes[0].old_value == "Alte Str. 1, 85354 Freising"
    assert address_changes[0].new_value == "Neue Str. 7, 85354 Freising"
    assert price_changes[0].old_value == "1499"
    assert price_changes[0].new_value == "1550"


def test_preview_master_data_reports_changes_without_writing_to_database(session, tmp_path):
    input_dir = tmp_path / "Input"
    input_dir.mkdir()
    _write_article_file(input_dir / "Artikel Liste Preise.xlsx", [["Cola 20x0,5", 20, 0.5, 8.0, 3.1, 15.5]])
    _write_customer_file(
        input_dir / "Lieferkunden Liste.xlsx",
        [
            [
                2,
                "Cafe Nord",
                datetime(2026, 6, 1),
                "",
                "",
                datetime(2026, 7, 1),
                4,
                "Neue Str.",
                "7",
                "85354",
                "Freising",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ]
        ],
    )
    create_customer(
        session,
        CustomerCreate(name="Cafe Nord", folder_path="Kunden/Cafe Nord", address="Alte Str. 1, 85354 Freising"),
    )

    preview = preview_master_data_from_folder(session, input_dir)

    assert preview.summary_text == "1 Produkt neu, 0 Produkte aktualisiert, 0 Kunden neu, 1 Kunden aktualisiert, 0 Zeilen unklar."
    assert [(item.entity_type, item.action, item.name) for item in preview.items] == [
        ("product", "create", "Cola 20x0,5"),
        ("customer", "update", "Cafe Nord"),
    ]
    assert session.query(Product).count() == 0
    assert session.query(Customer).one().address == "Alte Str. 1, 85354 Freising"


def test_preview_master_data_exposes_safety_groups_for_confirmation(session, tmp_path):
    input_dir = tmp_path / "Input"
    input_dir.mkdir()
    _write_article_file(input_dir / "Artikel Liste Preise.xlsx", [["Cola 20x0,5", 20, 0.5, 8.0, 3.1, 15.5], ["", 20, 0.5, 8.0, 3.1, 15.5]])
    _write_customer_file(
        input_dir / "Lieferkunden Liste.xlsx",
        [
            [
                2,
                "Cafe Nord",
                datetime(2026, 6, 1),
                "",
                "",
                datetime(2026, 7, 1),
                4,
                "Neue Str.",
                "7",
                "85354",
                "Freising",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
            ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
        ],
    )
    create_customer(
        session,
        CustomerCreate(name="Cafe Nord", folder_path="Kunden/Cafe Nord", address="Alte Str. 1, 85354 Freising"),
    )

    preview = preview_master_data_from_folder(session, input_dir)

    assert preview.safety_groups == {
        "neu": 1,
        "geaendert": 1,
        "unsicher": 0,
        "uebersprungen": 2,
    }
    assert "Neu: 1" in preview.safety_report_text
    assert "Geaendert: 1" in preview.safety_report_text
    assert "Uebersprungen: 2" in preview.safety_report_text


def _write_article_file(path, rows):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Tabelle1"
    sheet.append(
        [
            "Prudukt Bezeichnung",
            "Fl.",
            "Menge",
            "Re.-Preis",
            "EK 2",
            "H&F",
            "Abschlag",
            "Netto EK",
            "Pfand",
            "Pf. Fl.",
            "Laden VK",
            "Fl. Laden",
            "Netto VK",
            "Erlös €",
            "Erlös %",
            "Liefer Preis",
        ]
    )
    for row in rows:
        name, bottles, amount, invoice_price, deposit, delivery_price = row
        sheet.append([name, bottles, amount, invoice_price, "", "", "", "", deposit, "", "", "", "", "", "", delivery_price])
    workbook.save(path)


def _write_customer_file(path, rows):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Tabelle1"
    sheet.append(
        [
            "Priorität",
            "Name",
            "Lieferung",
            "Druck",
            "Menge",
            "nächster Kontakt",
            "Rhythmus",
            "Straße",
            "Hausnummer",
            "PLZ",
            "Ort",
            "Festnetz ",
            "Handy",
            "e-mail (Kontakt)",
            "e-mail (Re Versand)",
            "Ansprechpartner",
            "Bemerkungen",
            "ABO ",
            "Vormittag",
        ]
    )
    for row in rows:
        sheet.append(row)
    workbook.save(path)
