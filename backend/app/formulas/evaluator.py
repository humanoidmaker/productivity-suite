from __future__ import annotations
"""
Formula evaluator: walks AST nodes and computes results.

Requires a CellDataProvider to resolve cell references.
"""

from typing import Any, Protocol

from app.formulas.cell_reference import CellRef, RangeRef, parse_cell_ref, parse_range_ref
from app.formulas.functions import (
    ALL_ERRORS,
    ERR_DIV0,
    ERR_NAME,
    ERR_REF,
    ERR_VALUE,
    FUNCTIONS,
    is_error,
    is_number,
    to_number,
    to_string,
)
from app.formulas.parser import (
    ASTNode,
    BinaryOpNode,
    BooleanNode,
    CellRefNode,
    ErrorNode,
    FunctionCallNode,
    NumberNode,
    RangeRefNode,
    StringNode,
    UnaryOpNode,
)


class CellDataProvider(Protocol):
    """Interface for providing cell data to the evaluator."""

    def get_cell_value(self, ref: CellRef) -> Any:
        """Return the evaluated value of a cell."""
        ...

    def get_range_values(self, range_ref: RangeRef) -> list[Any]:
        """Return a flat list of values for a range."""
        ...

    def get_range_2d(self, range_ref: RangeRef) -> list[list[Any]]:
        """Return a 2D list of values for a range (for VLOOKUP, INDEX, etc.)."""
        ...


class FormulaEvaluator:
    def __init__(self, provider: CellDataProvider, current_sheet: str | None = None):
        self.provider = provider
        self.current_sheet = current_sheet

    def evaluate(self, node: ASTNode) -> Any:
        if isinstance(node, NumberNode):
            return node.value

        if isinstance(node, StringNode):
            return node.value

        if isinstance(node, BooleanNode):
            return node.value

        if isinstance(node, ErrorNode):
            return node.message

        if isinstance(node, CellRefNode):
            return self._eval_cell_ref(node)

        if isinstance(node, RangeRefNode):
            return self._eval_range_ref(node)

        if isinstance(node, UnaryOpNode):
            return self._eval_unary(node)

        if isinstance(node, BinaryOpNode):
            return self._eval_binary(node)

        if isinstance(node, FunctionCallNode):
            return self._eval_function(node)

        return ERR_VALUE

    def _eval_cell_ref(self, node: CellRefNode) -> Any:
        try:
            ref = parse_cell_ref(node.ref)
            if ref.sheet is None and self.current_sheet:
                ref = CellRef(col=ref.col, row=ref.row, col_absolute=ref.col_absolute, row_absolute=ref.row_absolute, sheet=self.current_sheet)
            return self.provider.get_cell_value(ref)
        except ValueError:
            return ERR_REF

    def _eval_range_ref(self, node: RangeRefNode) -> list[Any]:
        try:
            range_ref = parse_range_ref(node.ref)
            return self.provider.get_range_values(range_ref)
        except ValueError:
            return [ERR_REF]

    def _eval_unary(self, node: UnaryOpNode) -> Any:
        val = self.evaluate(node.operand)
        if is_error(val):
            return val
        if node.op == "-":
            n = to_number(val)
            return -float(n) if is_number(n) else ERR_VALUE
        return val  # unary +

    def _eval_binary(self, node: BinaryOpNode) -> Any:
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)

        # Propagate errors
        if is_error(left):
            return left
        if is_error(right):
            return right

        op = node.op

        # String concatenation
        if op == "&":
            return to_string(left) + to_string(right)

        # Comparison operators
        if op in ("=", "<>", "<", ">", "<=", ">="):
            return self._compare(left, right, op)

        # Arithmetic
        ln = to_number(left)
        rn = to_number(right)
        if is_error(ln):
            return ln
        if is_error(rn):
            return rn

        if op == "+":
            return float(ln) + float(rn)
        if op == "-":
            return float(ln) - float(rn)
        if op == "*":
            return float(ln) * float(rn)
        if op == "/":
            if float(rn) == 0:
                return ERR_DIV0
            return float(ln) / float(rn)
        if op == "^":
            try:
                return float(ln) ** float(rn)
            except (OverflowError, ValueError):
                return "#NUM!"

        return ERR_VALUE

    def _compare(self, left: Any, right: Any, op: str) -> bool:
        # Normalize for comparison
        if is_number(left) and is_number(right):
            l, r = float(left), float(right)
        elif isinstance(left, str) and isinstance(right, str):
            l, r = left.lower(), right.lower()  # type: ignore
        else:
            l, r = to_string(left), to_string(right)  # type: ignore

        if op == "=":
            return l == r
        if op == "<>":
            return l != r
        if op == "<":
            return l < r  # type: ignore
        if op == ">":
            return l > r  # type: ignore
        if op == "<=":
            return l <= r  # type: ignore
        if op == ">=":
            return l >= r  # type: ignore
        return False

    def _eval_function(self, node: FunctionCallNode) -> Any:
        fn = FUNCTIONS.get(node.name)
        if fn is None:
            return ERR_NAME

        # Special handling for functions that need range data as 2D arrays
        needs_2d = node.name in ("VLOOKUP", "HLOOKUP", "INDEX")

        args: list[Any] = []
        for arg_node in node.args:
            if needs_2d and isinstance(arg_node, RangeRefNode):
                try:
                    range_ref = parse_range_ref(arg_node.ref)
                    args.append(self.provider.get_range_2d(range_ref))
                except ValueError:
                    args.append(ERR_REF)
            else:
                args.append(self.evaluate(arg_node))

        return fn(args)


class DictCellProvider:
    """Simple dict-based cell provider for testing and standalone evaluation."""

    def __init__(self, data: dict[str, Any] | None = None):
        """
        data: dict mapping cell ref strings to values.
        e.g. {"A1": 10, "B1": 20, "Sheet2!A1": "hello"}
        """
        self.data: dict[str, Any] = data or {}

    def get_cell_value(self, ref: CellRef) -> Any:
        key = ref.to_string()
        # Try with sheet prefix, then without
        if key in self.data:
            return self.data[key]
        # Try without sheet
        no_sheet = CellRef(col=ref.col, row=ref.row, col_absolute=ref.col_absolute, row_absolute=ref.row_absolute).to_string()
        if no_sheet in self.data:
            return self.data[no_sheet]
        return None  # empty cell

    def get_range_values(self, range_ref: RangeRef) -> list[Any]:
        cells = range_ref.cells()
        return [self.get_cell_value(c) for c in cells]

    def get_range_2d(self, range_ref: RangeRef) -> list[list[Any]]:
        min_row = min(range_ref.start.row, range_ref.end.row)
        max_row = max(range_ref.start.row, range_ref.end.row)
        min_col = min(range_ref.start.col, range_ref.end.col)
        max_col = max(range_ref.start.col, range_ref.end.col)
        result = []
        for r in range(min_row, max_row + 1):
            row = []
            for c in range(min_col, max_col + 1):
                ref = CellRef(col=c, row=r, sheet=range_ref.sheet)
                row.append(self.get_cell_value(ref))
            result.append(row)
        return result


def evaluate_formula(formula: str, data: dict[str, Any] | None = None, sheet: str | None = None) -> Any:
    """Convenience: parse and evaluate a formula with a dict of cell data."""
    from app.formulas.parser import parse_formula
    ast = parse_formula(formula)
    provider = DictCellProvider(data)
    evaluator = FormulaEvaluator(provider, current_sheet=sheet)
    return evaluator.evaluate(ast)
