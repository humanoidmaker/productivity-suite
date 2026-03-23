from __future__ import annotations
"""Export spreadsheet active sheet to CSV."""

import csv
import io


def export_csv(meta: dict, sheet_name: str | None = None) -> str:
    """Export a single sheet to CSV string."""
    sheets = meta.get("sheets", [])
    if not sheets:
        return ""

    target_sheet = sheet_name or sheets[0].get("name", "Sheet1")
    cells = meta.get("cells", {}).get(target_sheet, {})

    if not cells:
        return ""

    # Find max row and col
    max_row = 0
    max_col = 0
    for ref in cells:
        # Parse cell ref like "A1", "B10"
        import re
        m = re.match(r"([A-Z]+)(\d+)", ref)
        if m:
            col_letters, row_num = m.groups()
            from app.formulas.cell_reference import col_letter_to_index
            col = col_letter_to_index(col_letters)
            row = int(row_num) - 1
            max_row = max(max_row, row)
            max_col = max(max_col, col)

    # Build grid
    output = io.StringIO()
    writer = csv.writer(output)

    for r in range(max_row + 1):
        row_data = []
        for c in range(max_col + 1):
            from app.formulas.cell_reference import col_index_to_letter
            ref = f"{col_index_to_letter(c)}{r + 1}"
            cell_data = cells.get(ref)
            if isinstance(cell_data, dict):
                row_data.append(cell_data.get("value", ""))
            else:
                row_data.append(cell_data if cell_data is not None else "")
        writer.writerow(row_data)

    return output.getvalue()
