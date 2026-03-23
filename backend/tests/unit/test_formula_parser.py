"""Tests for formula tokenizer and parser."""
import pytest
from app.formulas.parser import (
    FormulaParseError, parse_formula,
    NumberNode, StringNode, BooleanNode, CellRefNode, RangeRefNode,
    BinaryOpNode, UnaryOpNode, FunctionCallNode,
)


class TestFormulaParser:
    def test_simple_number(self):
        node = parse_formula("42")
        assert isinstance(node, NumberNode) and node.value == 42.0

    def test_simple_expression(self):
        node = parse_formula("1+2")
        assert isinstance(node, BinaryOpNode)
        assert node.op == "+"
        assert isinstance(node.left, NumberNode) and node.left.value == 1.0
        assert isinstance(node.right, NumberNode) and node.right.value == 2.0

    def test_cell_reference(self):
        node = parse_formula("A1")
        assert isinstance(node, CellRefNode) and node.ref == "A1"

    def test_range_reference(self):
        node = parse_formula("A1:B10")
        assert isinstance(node, RangeRefNode) and node.ref == "A1:B10"

    def test_function_call(self):
        node = parse_formula("SUM(A1:A10)")
        assert isinstance(node, FunctionCallNode)
        assert node.name == "SUM"
        assert len(node.args) == 1
        assert isinstance(node.args[0], RangeRefNode)

    def test_nested_functions(self):
        node = parse_formula("IF(A1>0, SUM(B1:B10), 0)")
        assert isinstance(node, FunctionCallNode)
        assert node.name == "IF"
        assert len(node.args) == 3

    def test_string_literal(self):
        node = parse_formula('"hello"')
        assert isinstance(node, StringNode) and node.value == "hello"

    def test_negative_number(self):
        node = parse_formula("-5")
        assert isinstance(node, UnaryOpNode)
        assert node.op == "-"

    def test_percentage(self):
        node = parse_formula("10%")
        assert isinstance(node, BinaryOpNode)
        assert node.op == "/"
        assert isinstance(node.left, NumberNode) and node.left.value == 10.0

    def test_operator_precedence(self):
        # 1+2*3 should be 1+(2*3)=7, not (1+2)*3=9
        node = parse_formula("1+2*3")
        assert isinstance(node, BinaryOpNode) and node.op == "+"
        assert isinstance(node.right, BinaryOpNode) and node.right.op == "*"

    def test_parentheses(self):
        node = parse_formula("(1+2)*3")
        assert isinstance(node, BinaryOpNode) and node.op == "*"
        assert isinstance(node.left, BinaryOpNode) and node.left.op == "+"

    def test_comparison_operator(self):
        node = parse_formula("A1>=10")
        assert isinstance(node, BinaryOpNode) and node.op == ">="

    def test_string_concat(self):
        node = parse_formula('"hello"&" "&"world"')
        assert isinstance(node, BinaryOpNode) and node.op == "&"

    def test_cross_sheet_reference(self):
        node = parse_formula("Sheet2!A1")
        assert isinstance(node, CellRefNode) and node.ref == "Sheet2!A1"

    def test_absolute_reference(self):
        node = parse_formula("$A$1")
        assert isinstance(node, CellRefNode) and node.ref == "$A$1"

    def test_empty_formula_raises(self):
        with pytest.raises(FormulaParseError):
            parse_formula("")

    def test_leading_equals(self):
        node = parse_formula("=1+2")
        assert isinstance(node, BinaryOpNode)

    def test_boolean_true(self):
        node = parse_formula("TRUE")
        assert isinstance(node, BooleanNode) and node.value is True

    def test_boolean_false(self):
        node = parse_formula("FALSE")
        assert isinstance(node, BooleanNode) and node.value is False
