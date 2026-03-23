from __future__ import annotations
"""Import CSV to internal spreadsheet format."""

import csv
import io

from app.formulas.cell_reference import col_index_to_letter


def import_csv(data: bytes, delimiter: str = ",", has_header: bool = True) -> dict:
    """Convert CSV bytes to internal spreadsheet meta dict."""
    text = data.decode("utf-8-sig", errors="replace")  # Handle BOM
    reader = csv.reader(io.StringIO(text), delimiter=delimiter)

    cells = {}
    max_col = 0

    for row_idx, row in enumerate(reader):
        for col_idx, value in enumerate(row):
            if value.strip():
                ref = f"{col_index_to_letter(col_idx)}{row_idx + 1}"
                # Auto-detect type
                parsed = _auto_type(value.strip())
                cells[ref] = {"value": parsed}
                max_col = max(max_col, col_idx)

    return {
        "sheets": [{"name": "Sheet1", "index": 0, "visible": True, "color": None}],
        "cells": {"Sheet1": cells},
    }


def _auto_type(value: str):
    """Try to convert string value to appropriate Python type."""
    # Boolean
    if value.upper() in ("TRUE", "FALSE"):
        return value.upper() == "TRUE"
    # Integer
    try:
        v = int(value)
        return v
    except ValueError:
        pass
    # Float
    try:
        v = float(value)
        return v
    except ValueError:
        pass
    # Date patterns — keep as string for now
    return value
