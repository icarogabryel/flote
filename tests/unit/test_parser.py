import pytest

from flote.elaboration import ast_nodes
from flote.elaboration.parser import Parser, SyntacticalError
from flote.elaboration.scanner import Scanner


def parse(code: str) -> ast_nodes.Module:
    return Parser(Scanner(code).token_stream).ast


def only_component(code: str) -> ast_nodes.Component:
    module = parse(code)
    assert len(module.components) == 1
    return module.components[0]


def ref_name(expr: ast_nodes.ExpressionElement) -> str:
    assert isinstance(expr, ast_nodes.Reference)
    return expr.id_.full_id


def test_parses_main_component_and_additional_components() -> None:
    module = parse(
        """main comp Top {}
        comp Child {}
        """
    )

    assert len(module.components) == 2
    assert module.components[0].is_main is True
    assert module.components[0].identifier.value == "Top"
    assert module.components[1].is_main is False
    assert module.components[1].identifier.value == "Child"


def test_parses_declarations_with_connections_dimensions_and_multiple_ids() -> None:
    comp = only_component(
        """comp Test {
            in bit[8] a, b;
            out bit[-4] y;
            bit internal;
        }
        """
    )

    assert len(comp.statements) == 4

    first, second, third, fourth = comp.statements
    assert all(isinstance(stmt, ast_nodes.Declaration) for stmt in comp.statements)

    assert isinstance(first, ast_nodes.Declaration)
    assert first.connection == ast_nodes.Connection.INPUT
    assert first.identifier.value == "a"
    assert first.dimension is not None
    assert first.dimension.size == 8
    assert first.dimension.msb == ast_nodes.Msb.ASCENDING

    assert isinstance(second, ast_nodes.Declaration)
    assert second.connection == ast_nodes.Connection.INPUT
    assert second.identifier.value == "b"
    assert second.dimension is not None
    assert second.dimension.size == 8
    assert second.dimension.msb == ast_nodes.Msb.ASCENDING

    assert isinstance(third, ast_nodes.Declaration)
    assert third.connection == ast_nodes.Connection.OUTPUT
    assert third.identifier.value == "y"
    assert third.dimension is not None
    assert third.dimension.size == 4
    assert third.dimension.msb == ast_nodes.Msb.DESCENDING

    assert isinstance(fourth, ast_nodes.Declaration)
    assert fourth.connection == ast_nodes.Connection.INTERNAL
    assert fourth.identifier.value == "internal"
    assert fourth.dimension is None


def test_parses_declaration_with_assignment_expression() -> None:
    comp = only_component(
        """comp Test {
            out bit y = "1";
        }
        """
    )

    declaration = comp.statements[0]
    assert isinstance(declaration, ast_nodes.Declaration)
    assert declaration.connection == ast_nodes.Connection.OUTPUT
    assert declaration.identifier.value == "y"
    assert isinstance(declaration.assignment_expression, ast_nodes.BitField)
    assert declaration.assignment_expression.value == "1"


def test_parses_assignments_to_identifiers_and_members() -> None:
    comp = only_component(
        """comp Test {
            a = b;
            child.input = a;
        }
        """
    )

    first, second = comp.statements
    assert isinstance(first, ast_nodes.Assignment)
    assert first.destiny.full_id == "a"
    assert ref_name(first.expr) == "b"

    assert isinstance(second, ast_nodes.Assignment)
    assert isinstance(second.destiny, ast_nodes.MemberAccess)
    assert second.destiny.full_id == "child.input"
    assert ref_name(second.expr) == "a"


def test_parses_references_with_indexes_slices_and_members() -> None:
    comp = only_component(
        """
        comp Test {
            bit a = bus[3];
            bit b = bus[3:1];
            bit c = child.output[0];
        }
        """
    )

    assert isinstance(comp.statements[0], ast_nodes.Declaration)
    single_index = comp.statements[0].assignment_expression
    assert isinstance(single_index, ast_nodes.Reference)
    assert ref_name(single_index) == "bus"
    assert isinstance(single_index, ast_nodes.Reference)
    assert single_index.range_begin == 3
    assert single_index.range_end is None

    assert isinstance(comp.statements[1], ast_nodes.Declaration)
    slice_ = comp.statements[1].assignment_expression
    assert isinstance(slice_, ast_nodes.Reference)
    assert ref_name(slice_) == "bus"
    assert isinstance(slice_, ast_nodes.Reference)
    assert slice_.range_begin == 3
    assert slice_.range_end == 1

    assert isinstance(comp.statements[2], ast_nodes.Declaration)
    member_index = comp.statements[2].assignment_expression
    assert isinstance(member_index, ast_nodes.Reference)
    assert ref_name(member_index) == "child.output"
    assert isinstance(member_index, ast_nodes.Reference)
    assert member_index.range_begin == 0
    assert member_index.range_end is None


def test_parses_subcomponent_instances_with_default_and_explicit_aliases() -> None:
    comp = only_component(
        """
        comp Test {
            sub AndGate;
            sub OrGate as gate;
        }
        """
    )

    first, second = comp.statements
    assert isinstance(first, ast_nodes.Instance)
    assert first.identifier == "AndGate"
    assert first.alias is None

    assert isinstance(second, ast_nodes.Instance)
    assert second.identifier == "OrGate"
    assert second.alias == "gate"


def test_parses_expression_precedence() -> None:
    comp = only_component(
        """
        comp Test {
            y = a or b xor c and d;
        }
        """
    )

    assert isinstance(comp.statements[0], ast_nodes.Assignment)
    expr = comp.statements[0].expr
    assert isinstance(expr, ast_nodes.OrOp)
    assert isinstance(expr.l_expr, ast_nodes.Reference)
    assert ref_name(expr.l_expr) == "a"

    assert isinstance(expr.r_expr, ast_nodes.XorOp)
    assert isinstance(expr.r_expr.l_expr, ast_nodes.Reference)
    assert ref_name(expr.r_expr.l_expr) == "b"

    assert isinstance(expr.r_expr.r_expr, ast_nodes.AndOp)
    assert isinstance(expr.r_expr.r_expr.l_expr, ast_nodes.Reference)
    assert ref_name(expr.r_expr.r_expr.l_expr) == "c"
    assert isinstance(expr.r_expr.r_expr.r_expr, ast_nodes.Reference)
    assert ref_name(expr.r_expr.r_expr.r_expr) == "d"


def test_parses_parentheses_not_and_concatenation() -> None:
    comp = only_component(
        """
        comp Test {
            y = <not a, (b or c), "10">;
        }
        """
    )

    assert isinstance(comp.statements[0], ast_nodes.Assignment)
    expr = comp.statements[0].expr
    assert isinstance(expr, ast_nodes.Concatenation)
    assert len(expr.expressions) == 3

    assert isinstance(expr.expressions[0], ast_nodes.NotOp)
    assert isinstance(expr.expressions[0].expr, ast_nodes.Reference)
    assert ref_name(expr.expressions[0].expr) == "a"

    assert isinstance(expr.expressions[1], ast_nodes.OrOp)
    assert isinstance(expr.expressions[1].l_expr, ast_nodes.Reference)
    assert ref_name(expr.expressions[1].l_expr) == "b"
    assert isinstance(expr.expressions[1].r_expr, ast_nodes.Reference)
    assert ref_name(expr.expressions[1].r_expr) == "c"

    assert isinstance(expr.expressions[2], ast_nodes.BitField)
    assert expr.expressions[2].value == "10"


@pytest.mark.parametrize(
    ("code", "message"),
    [
        ("comp Test { bit a }", 'Expected "semicolon"'),
        ("comp Test { bit[0] a; }", "Dimension size must be positive"),
        ("comp Test { y = ; }", "Expected primary"),
        ("comp Test { sub ; }", 'Expected "id"'),
    ],
)
def test_raises_syntactical_error_for_invalid_syntax(code: str, message: str) -> None:
    with pytest.raises(SyntacticalError, match=message):
        parse(code)
