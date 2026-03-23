"""Tests for dependency graph and circular reference detection."""
import pytest
from app.formulas.cell_reference import CellRef
from app.formulas.dependency_graph import DependencyGraph, CircularReferenceError, extract_references


class TestExtractReferences:
    def test_simple_ref(self):
        refs = extract_references("=A1+1")
        assert CellRef(col=0, row=0) in refs

    def test_range_ref(self):
        refs = extract_references("=SUM(A1:A10)")
        assert len(refs) == 10  # A1 through A10

    def test_no_refs(self):
        refs = extract_references("=1+2")
        assert len(refs) == 0


class TestDependencyGraph:
    def test_simple_dependency(self):
        g = DependencyGraph()
        b1 = CellRef(col=1, row=0)  # B1
        g.set_formula(b1, "=A1+1")
        deps = g.depends_on[b1]
        assert CellRef(col=0, row=0) in deps  # B1 depends on A1

    def test_chain_dependency(self):
        g = DependencyGraph()
        b1 = CellRef(col=1, row=0)  # B1
        c1 = CellRef(col=2, row=0)  # C1
        g.set_formula(b1, "=A1+1")
        g.set_formula(c1, "=B1+1")

        # C1 depends on B1
        assert b1 in g.depends_on[c1]
        # B1 is depended on by C1
        assert c1 in g.depended_by[b1]

    def test_range_dependency(self):
        g = DependencyGraph()
        b1 = CellRef(col=1, row=0)
        g.set_formula(b1, "=SUM(A1:A10)")
        assert len(g.depends_on[b1]) == 10

    def test_topological_sort(self):
        g = DependencyGraph()
        a1 = CellRef(col=0, row=0)
        b1 = CellRef(col=1, row=0)
        c1 = CellRef(col=2, row=0)
        g.set_formula(b1, "=A1+1")
        g.set_formula(c1, "=B1+1")
        order = g.topological_sort({a1, b1, c1})
        # a1 should come before b1, b1 before c1
        assert order.index(a1) < order.index(b1)
        assert order.index(b1) < order.index(c1)

    def test_circular_direct(self):
        g = DependencyGraph()
        a1 = CellRef(col=0, row=0)
        b1 = CellRef(col=1, row=0)
        g.set_formula(a1, "=B1")
        g.set_formula(b1, "=A1")
        cycle = g.detect_circular(b1)
        assert cycle is not None

    def test_circular_indirect(self):
        g = DependencyGraph()
        a1 = CellRef(col=0, row=0)
        b1 = CellRef(col=1, row=0)
        c1 = CellRef(col=2, row=0)
        g.set_formula(a1, "=C1")
        g.set_formula(b1, "=A1")
        g.set_formula(c1, "=B1")
        cycle = g.detect_circular(c1)
        assert cycle is not None

    def test_self_reference(self):
        g = DependencyGraph()
        a1 = CellRef(col=0, row=0)
        g.set_formula(a1, "=A1+1")
        cycle = g.detect_circular(a1)
        assert cycle is not None

    def test_remove_dependency(self):
        g = DependencyGraph()
        b1 = CellRef(col=1, row=0)
        g.set_formula(b1, "=A1+1")
        assert len(g.depends_on[b1]) == 1
        g.remove_cell(b1)
        assert b1 not in g.depends_on

    def test_recalculation_order(self):
        g = DependencyGraph()
        a1 = CellRef(col=0, row=0)
        b1 = CellRef(col=1, row=0)
        c1 = CellRef(col=2, row=0)
        g.set_formula(b1, "=A1*2")
        g.set_formula(c1, "=B1+1")
        order = g.get_recalculation_order(a1)
        assert b1 in order
        assert c1 in order
        assert order.index(b1) < order.index(c1)

    def test_topological_sort_circular_raises(self):
        g = DependencyGraph()
        a1 = CellRef(col=0, row=0)
        b1 = CellRef(col=1, row=0)
        g.set_formula(a1, "=B1")
        g.set_formula(b1, "=A1")
        with pytest.raises(CircularReferenceError):
            g.topological_sort({a1, b1})
