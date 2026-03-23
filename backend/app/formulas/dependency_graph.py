from __future__ import annotations
"""
Dependency graph for spreadsheet cells.

Tracks which cells depend on which, detects circular references,
and provides topological sort for correct recalculation order.
"""

from collections import defaultdict
from dataclasses import dataclass, field

from app.formulas.cell_reference import CellRef, RangeRef, parse_cell_ref, parse_range_ref
from app.formulas.parser import (
    ASTNode,
    BinaryOpNode,
    CellRefNode,
    FunctionCallNode,
    RangeRefNode,
    UnaryOpNode,
    parse_formula,
)


def extract_references(formula: str) -> set[CellRef]:
    """Extract all cell references from a formula string."""
    try:
        ast = parse_formula(formula)
    except Exception:
        return set()
    return _extract_from_node(ast)


def _extract_from_node(node: ASTNode) -> set[CellRef]:
    refs: set[CellRef] = set()

    if isinstance(node, CellRefNode):
        try:
            refs.add(parse_cell_ref(node.ref))
        except ValueError:
            pass

    elif isinstance(node, RangeRefNode):
        try:
            range_ref = parse_range_ref(node.ref)
            refs.update(range_ref.cells())
        except ValueError:
            pass

    elif isinstance(node, BinaryOpNode):
        refs.update(_extract_from_node(node.left))
        refs.update(_extract_from_node(node.right))

    elif isinstance(node, UnaryOpNode):
        refs.update(_extract_from_node(node.operand))

    elif isinstance(node, FunctionCallNode):
        for arg in node.args:
            refs.update(_extract_from_node(arg))

    return refs


class CircularReferenceError(Exception):
    def __init__(self, cells: list[CellRef]):
        self.cells = cells
        super().__init__(f"Circular reference detected: {' -> '.join(c.to_string() for c in cells)}")


class DependencyGraph:
    """
    Directed graph: edge from A to B means "B depends on A" (if A changes, recalculate B).

    - depends_on[cell] = set of cells that `cell` references in its formula
    - depended_by[cell] = set of cells whose formulas reference `cell`
    """

    def __init__(self):
        # cell → set of cells it references
        self.depends_on: dict[CellRef, set[CellRef]] = defaultdict(set)
        # cell → set of cells that reference it
        self.depended_by: dict[CellRef, set[CellRef]] = defaultdict(set)

    def set_formula(self, cell: CellRef, formula: str) -> None:
        """Update the dependency graph when a cell's formula changes."""
        # Remove old dependencies
        self.remove_cell(cell)

        # Extract new references
        new_deps = extract_references(formula)
        self.depends_on[cell] = new_deps

        for dep in new_deps:
            self.depended_by[dep].add(cell)

    def remove_cell(self, cell: CellRef) -> None:
        """Remove a cell from the graph (when its formula is cleared)."""
        old_deps = self.depends_on.pop(cell, set())
        for dep in old_deps:
            self.depended_by[dep].discard(cell)

    def get_dependents(self, cell: CellRef) -> set[CellRef]:
        """Get all cells that directly depend on the given cell."""
        return self.depended_by.get(cell, set())

    def get_all_dependents(self, cell: CellRef) -> set[CellRef]:
        """Get all cells that directly or transitively depend on the given cell."""
        result: set[CellRef] = set()
        stack = list(self.get_dependents(cell))
        while stack:
            c = stack.pop()
            if c not in result:
                result.add(c)
                stack.extend(self.get_dependents(c))
        return result

    def detect_circular(self, cell: CellRef) -> list[CellRef] | None:
        """
        Check if setting `cell`'s current dependencies creates a cycle.
        Returns the cycle path if found, None otherwise.
        """
        visited: set[CellRef] = set()
        path: list[CellRef] = []

        def dfs(current: CellRef) -> bool:
            if current in visited:
                # Found cycle — extract cycle from path
                if current in path:
                    idx = path.index(current)
                    return True
                return False
            visited.add(current)
            path.append(current)
            for dep in self.depends_on.get(current, set()):
                if dep == cell:
                    path.append(dep)
                    return True
                if dfs(dep):
                    return True
            path.pop()
            return False

        # Check if any of cell's dependencies eventually lead back to cell
        for dep in self.depends_on.get(cell, set()):
            if dep == cell:
                return [cell, cell]  # self-reference
            visited.clear()
            path.clear()
            path.append(cell)
            if dfs(dep):
                return path

        return None

    def topological_sort(self, cells: set[CellRef] | None = None) -> list[CellRef]:
        """
        Return cells in topological order (dependencies first).
        If cells is None, sorts all cells in the graph.
        Raises CircularReferenceError if a cycle is detected.
        """
        target_cells = cells if cells is not None else set(self.depends_on.keys())

        # Kahn's algorithm
        in_degree: dict[CellRef, int] = defaultdict(int)
        for cell in target_cells:
            if cell not in in_degree:
                in_degree[cell] = 0
            for dep in self.depends_on.get(cell, set()):
                if dep in target_cells:
                    in_degree[cell] += 1

        queue: list[CellRef] = [c for c in target_cells if in_degree[c] == 0]
        result: list[CellRef] = []

        while queue:
            cell = queue.pop(0)
            result.append(cell)
            for dependent in self.depended_by.get(cell, set()):
                if dependent in target_cells:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

        if len(result) != len(target_cells):
            # Cycle detected
            remaining = target_cells - set(result)
            raise CircularReferenceError(list(remaining))

        return result

    def get_recalculation_order(self, changed_cell: CellRef) -> list[CellRef]:
        """
        Given that `changed_cell` has been modified, return all cells that need
        recalculation, in the correct order (dependencies first).
        """
        affected = self.get_all_dependents(changed_cell)
        if not affected:
            return []
        return self.topological_sort(affected)
