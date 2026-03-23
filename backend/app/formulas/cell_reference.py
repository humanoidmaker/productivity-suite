from __future__ import annotations
"""
Cell reference parsing and manipulation.

Supports: A1, $A$1, A$1, $A1, AA1, Sheet2!A1, A1:B10
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CellRef:
    col: int           # 0-indexed (A=0, B=1, ..., Z=25, AA=26)
    row: int           # 0-indexed
    col_absolute: bool = False
    row_absolute: bool = False
    sheet: str | None = None

    def to_string(self) -> str:
        prefix = f"{self.sheet}!" if self.sheet else ""
        col_str = ("$" if self.col_absolute else "") + col_index_to_letter(self.col)
        row_str = ("$" if self.row_absolute else "") + str(self.row + 1)
        return f"{prefix}{col_str}{row_str}"

    def offset(self, d_row: int, d_col: int) -> CellRef:
        new_row = self.row if self.row_absolute else self.row + d_row
        new_col = self.col if self.col_absolute else self.col + d_col
        if new_row < 0 or new_col < 0:
            raise ValueError(f"Reference shifted out of bounds: row={new_row}, col={new_col}")
        return CellRef(col=new_col, row=new_row, col_absolute=self.col_absolute, row_absolute=self.row_absolute, sheet=self.sheet)


@dataclass(frozen=True)
class RangeRef:
    start: CellRef
    end: CellRef
    sheet: str | None = None

    def to_string(self) -> str:
        prefix = f"{self.sheet}!" if self.sheet else ""
        return f"{prefix}{self.start.to_string()}{':' + self.end.to_string()}"

    def cells(self) -> list[CellRef]:
        """Expand range to list of individual cell refs."""
        result = []
        sheet = self.sheet or self.start.sheet
        min_row = min(self.start.row, self.end.row)
        max_row = max(self.start.row, self.end.row)
        min_col = min(self.start.col, self.end.col)
        max_col = max(self.start.col, self.end.col)
        for r in range(min_row, max_row + 1):
            for c in range(min_col, max_col + 1):
                result.append(CellRef(col=c, row=r, sheet=sheet))
        return result


# ── Column letter <-> index conversion ──

def col_letter_to_index(letters: str) -> int:
    """Convert column letters to 0-based index. A=0, B=1, ..., Z=25, AA=26, AB=27"""
    result = 0
    for ch in letters.upper():
        result = result * 26 + (ord(ch) - ord('A') + 1)
    return result - 1


def col_index_to_letter(index: int) -> str:
    """Convert 0-based column index to letters. 0=A, 1=B, 25=Z, 26=AA"""
    if index < 0:
        raise ValueError(f"Column index must be >= 0, got {index}")
    result = ""
    idx = index + 1  # 1-based for the math
    while idx > 0:
        idx, remainder = divmod(idx - 1, 26)
        result = chr(ord('A') + remainder) + result
    return result


# ── Parsing ──

# Regex: optional sheet name + !, optional $ before col letters, col letters, optional $ before row digits, row digits
_CELL_RE = re.compile(
    r"^(?:([A-Za-z_][\w]*)!)?"   # optional sheet name with !
    r"(\$?)([A-Za-z]{1,3})"      # optional $ + column letters
    r"(\$?)(\d{1,7})$"           # optional $ + row number
)

_RANGE_RE = re.compile(
    r"^(?:([A-Za-z_][\w]*)!)?"   # optional sheet name
    r"(\$?)([A-Za-z]{1,3})(\$?)(\d{1,7})"  # start cell
    r":(\$?)([A-Za-z]{1,3})(\$?)(\d{1,7})$"  # end cell
)


def parse_cell_ref(text: str) -> CellRef:
    """Parse a cell reference string like 'A1', '$B$2', 'Sheet1!C3'."""
    m = _CELL_RE.match(text.strip())
    if not m:
        raise ValueError(f"Invalid cell reference: {text}")

    sheet = m.group(1)
    col_abs = m.group(2) == "$"
    col_letters = m.group(3)
    row_abs = m.group(4) == "$"
    row_num = int(m.group(5))

    if row_num < 1:
        raise ValueError(f"Row must be >= 1, got {row_num} in '{text}'")

    return CellRef(
        col=col_letter_to_index(col_letters),
        row=row_num - 1,  # convert to 0-based
        col_absolute=col_abs,
        row_absolute=row_abs,
        sheet=sheet,
    )


def parse_range_ref(text: str) -> RangeRef:
    """Parse a range reference like 'A1:B10', 'Sheet2!A1:C3'."""
    m = _RANGE_RE.match(text.strip())
    if not m:
        raise ValueError(f"Invalid range reference: {text}")

    sheet = m.group(1)
    start = CellRef(
        col=col_letter_to_index(m.group(3)),
        row=int(m.group(5)) - 1,
        col_absolute=m.group(2) == "$",
        row_absolute=m.group(4) == "$",
        sheet=sheet,
    )
    end = CellRef(
        col=col_letter_to_index(m.group(7)),
        row=int(m.group(9)) - 1,
        col_absolute=m.group(6) == "$",
        row_absolute=m.group(8) == "$",
        sheet=sheet,
    )
    return RangeRef(start=start, end=end, sheet=sheet)


def is_cell_ref(text: str) -> bool:
    return _CELL_RE.match(text.strip()) is not None


def is_range_ref(text: str) -> bool:
    return _RANGE_RE.match(text.strip()) is not None
