from dataclasses import dataclass
from pathlib import Path
import re


@dataclass(slots=True)
class DocumentPaths:
    excel_path: Path
    pdf_path: Path


DOCUMENT_TYPE_PREFIXES = {
    "Rechnung": "RE",
    "Lieferauftrag": "LS",
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
    safe_document_number = _safe_filename_part(document_number)
    parts = [_safe_filename_part(document_date)]
    if not _already_has_document_prefix(safe_document_number, prefix):
        parts.append(prefix)
    parts.extend([safe_document_number, _safe_filename_part(customer_name)])
    filename_stem = "_".join(parts)
    excel_path = customer_folder / f"{filename_stem}.xlsx"
    return DocumentPaths(excel_path=excel_path, pdf_path=excel_path.with_suffix(".pdf"))


def _already_has_document_prefix(document_number: str, prefix: str) -> bool:
    normalized = document_number.upper()
    return normalized == prefix or normalized.startswith(f"{prefix}_") or normalized.startswith(f"{prefix}-")


def _safe_filename_part(value: str) -> str:
    safe = value.replace("/", "-").replace("\\", "-")
    safe = re.sub(r'[<>:"|?*\x00-\x1f]+', " ", safe)
    safe = "_".join(part for part in safe.replace(".", " ").split() if part).strip(". ")
    if not safe:
        return "ohne_angabe"
    if safe.upper() in {"CON", "PRN", "AUX", "NUL", *(f"COM{number}" for number in range(1, 10)), *(f"LPT{number}" for number in range(1, 10))}:
        return f"{safe}_"
    return safe
