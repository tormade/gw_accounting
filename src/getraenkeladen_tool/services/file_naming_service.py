from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class DocumentPaths:
    excel_path: Path
    pdf_path: Path


DOCUMENT_TYPE_PREFIXES = {
    "Rechnung": "RE",
    "Lieferschein": "LS",
}


def build_document_paths(
    customer_folder: Path,
    document_type: str,
    document_number: str,
    customer_name: str,
    document_date: str,
) -> DocumentPaths:
    prefix = DOCUMENT_TYPE_PREFIXES[document_type]
    filename_stem = "_".join(
        [
            _safe_filename_part(document_date),
            prefix,
            _safe_filename_part(document_number),
            _safe_filename_part(customer_name),
        ]
    )
    excel_path = customer_folder / f"{filename_stem}.xlsx"
    return DocumentPaths(excel_path=excel_path, pdf_path=excel_path.with_suffix(".pdf"))


def _safe_filename_part(value: str) -> str:
    safe = value.strip().replace("/", "-").replace("\\", "-")
    safe = "_".join(part for part in safe.replace(".", " ").split() if part)
    return safe or "ohne_angabe"
