"""Tests for formula evaluator."""
import pytest
from datetime import date
from app.formulas.evaluator import evaluate_formula


class TestFormulaEvaluator:
    def test_literal_number(self):
        assert evaluate_formula("42") == 42.0

    def test_arithmetic(self):
        assert evaluate_formula("10+5*2") == 20.0

    def test_cell_reference(self):
        assert evaluate_formula("A1", {"A1": 10}) == 10

    def test_range_sum(self):
        data = {"A1": 1, "A2": 2, "A3": 3}
        assert evaluate_formula("SUM(A1:A3)", data) == 6.0

    def test_if_true_branch(self):
        assert evaluate_formula('IF(1>0, "yes", "no")') == "yes"

    def test_if_false_branch(self):
        assert evaluate_formula('IF(1<0, "yes", "no")') == "no"

    def test_nested_if(self):
        data = {"A1": 15}
        result = evaluate_formula('IF(A1>10, IF(A1>20, "high", "mid"), "low")', data)
        assert result == "mid"

    def test_vlookup_match(self):
        data = {
            "A1": "apple", "B1": 1.50,
            "A2": "banana", "B2": 0.75,
            "A3": "cherry", "B3": 2.00,
        }
        result = evaluate_formula('VLOOKUP("banana", A1:B3, 2)', data)
        assert result == 0.75

    def test_vlookup_no_match(self):
        data = {"A1": "apple", "B1": 1}
        result = evaluate_formula('VLOOKUP("missing", A1:B1, 2)', data)
        assert result == "#N/A"

    def test_division_by_zero(self):
        assert evaluate_formula("1/0") == "#DIV/0!"

    def test_reference_error(self):
        # Evaluating a ref that doesn't exist returns None (empty cell)
        assert evaluate_formula("A1") is None

    def test_name_error(self):
        # Unknown function
        result = evaluate_formula("UNKNOWN()")
        # Parser should raise or evaluator should return #NAME?
        assert result == "#NAME?"

    def test_value_error(self):
        # "text" + 1
        result = evaluate_formula('"text"+1')
        assert result == "#VALUE!"

    def test_cross_sheet(self):
        data = {"Sheet2!A1": 42}
        assert evaluate_formula("Sheet2!A1", data) == 42

    def test_empty_cell_numeric(self):
        # Empty cell in arithmetic context → 0
        result = evaluate_formula("A1+1", {})
        # A1 is None, to_number(None) = 0, so 0+1=1
        assert result == 1.0

    def test_concatenate(self):
        result = evaluate_formula('CONCATENATE("Hello", " ", "World")')
        assert result == "Hello World"

    def test_date_function(self):
        result = evaluate_formula("DATE(2024,1,15)")
        assert result == date(2024, 1, 15)

    def test_round(self):
        result = evaluate_formula("ROUND(3.14159, 2)")
        assert result == 3.14

    def test_string_concat_operator(self):
        result = evaluate_formula('"A"&"B"')
        assert result == "AB"

    def test_comparison_equals(self):
        assert evaluate_formula("1=1") is True

    def test_comparison_not_equals(self):
        assert evaluate_formula("1<>2") is True

    def test_percentage(self):
        assert evaluate_formula("50%") == 0.5

    def test_power(self):
        assert evaluate_formula("2^3") == 8.0
