"""Tests for cell reference parsing and manipulation."""
import pytest
from app.formulas.cell_reference import (
    CellRef, RangeRef, col_index_to_letter, col_letter_to_index,
    parse_cell_ref, parse_range_ref,
)


class TestColConversion:
    def test_a_to_0(self):
        assert col_letter_to_index("A") == 0

    def test_z_to_25(self):
        assert col_letter_to_index("Z") == 25

    def test_aa_to_26(self):
        assert col_letter_to_index("AA") == 26

    def test_ab_to_27(self):
        assert col_letter_to_index("AB") == 27

    def test_0_to_a(self):
        assert col_index_to_letter(0) == "A"

    def test_25_to_z(self):
        assert col_index_to_letter(25) == "Z"

    def test_26_to_aa(self):
        assert col_index_to_letter(26) == "AA"

    def test_negative_index_raises(self):
        with pytest.raises(ValueError):
            col_index_to_letter(-1)


class TestParseCellRef:
    def test_simple_a1(self):
        ref = parse_cell_ref("A1")
        assert ref.col == 0
        assert ref.row == 0
        assert not ref.col_absolute
        assert not ref.row_absolute
        assert ref.sheet is None

    def test_absolute_dollar_a_dollar_1(self):
        ref = parse_cell_ref("$A$1")
        assert ref.col == 0
        assert ref.row == 0
        assert ref.col_absolute
        assert ref.row_absolute

    def test_mixed_a_dollar_1(self):
        ref = parse_cell_ref("A$1")
        assert not ref.col_absolute
        assert ref.row_absolute

    def test_mixed_dollar_a_1(self):
        ref = parse_cell_ref("$A1")
        assert ref.col_absolute
        assert not ref.row_absolute

    def test_aa1_col_26(self):
        ref = parse_cell_ref("AA1")
        assert ref.col == 26

    def test_with_sheet(self):
        ref = parse_cell_ref("Sheet2!A1")
        assert ref.sheet == "Sheet2"
        assert ref.col == 0
        assert ref.row == 0

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            parse_cell_ref("invalid")

    def test_to_string_roundtrip(self):
        ref = parse_cell_ref("$B$5")
        assert ref.to_string() == "$B$5"

    def test_to_string_aa1(self):
        ref = CellRef(col=26, row=0)
        assert ref.to_string() == "AA1"


class TestParseRangeRef:
    def test_simple_range(self):
        rng = parse_range_ref("A1:B10")
        assert rng.start.col == 0 and rng.start.row == 0
        assert rng.end.col == 1 and rng.end.row == 9

    def test_with_sheet(self):
        rng = parse_range_ref("Sheet2!A1:C3")
        assert rng.sheet == "Sheet2"

    def test_cells_expansion(self):
        rng = parse_range_ref("A1:B2")
        cells = rng.cells()
        assert len(cells) == 4  # A1, B1, A2, B2

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            parse_range_ref("invalid")


class TestCellRefOffset:
    def test_offset_relative(self):
        ref = CellRef(col=0, row=0)
        shifted = ref.offset(1, 1)
        assert shifted.col == 1 and shifted.row == 1

    def test_offset_absolute_not_shifted(self):
        ref = CellRef(col=0, row=0, col_absolute=True, row_absolute=True)
        shifted = ref.offset(5, 5)
        assert shifted.col == 0 and shifted.row == 0

    def test_offset_negative_raises(self):
        ref = CellRef(col=0, row=0)
        with pytest.raises(ValueError):
            ref.offset(-1, 0)
