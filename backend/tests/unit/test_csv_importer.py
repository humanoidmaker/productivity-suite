"""Tests for CSV importer."""
from app.importer.csv_importer import import_csv, _auto_type


class TestAutoType:
    def test_integer(self):
        assert _auto_type("42") == 42

    def test_float(self):
        assert _auto_type("3.14") == 3.14

    def test_boolean_true(self):
        assert _auto_type("TRUE") is True

    def test_boolean_false(self):
        assert _auto_type("FALSE") is False

    def test_string(self):
        assert _auto_type("hello") == "hello"


class TestCsvImport:
    def test_basic_csv(self):
        data = b"Name,Age\nAlice,30\nBob,25"
        result = import_csv(data)
        assert result["sheets"][0]["name"] == "Sheet1"
        cells = result["cells"]["Sheet1"]
        assert cells["A1"]["value"] == "Name"
        assert cells["B2"]["value"] == 30  # Alice's age
        assert cells["B3"]["value"] == 25  # Bob's age

    def test_empty_csv(self):
        result = import_csv(b"")
        assert result["cells"]["Sheet1"] == {}

    def test_numeric_detection(self):
        data = b"val\n42\n3.14\ntext"
        result = import_csv(data)
        cells = result["cells"]["Sheet1"]
        assert cells["A2"]["value"] == 42
        assert cells["A3"]["value"] == 3.14
        assert cells["A4"]["value"] == "text"

    def test_utf8_bom(self):
        data = b"\xef\xbb\xbfName\nAlice"
        result = import_csv(data)
        cells = result["cells"]["Sheet1"]
        assert cells["A1"]["value"] == "Name"
