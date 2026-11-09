import json
from typing import Any, cast

import pytest

from flote.elaboration.builder import Builder, SemanticalError
from flote.elaboration.parser import Parser
from flote.elaboration.scanner import Scanner


def build_netlist(code: str) -> dict[str, Any]:
    ast = Parser(Scanner(code).token_stream).ast
    return cast(dict[str, Any], json.loads(Builder(ast).netlist))


def busses_by_id(netlist: dict[str, Any]) -> dict[str, Any]:
    return {bus["id"]: bus for bus in netlist["component"]["buses"]}


def test_builds_netlist_with_assignments_and_influence_lists() -> None:
    netlist = build_netlist(
        """
        comp Test {
            in bit a, b;
            out bit y;

            y = a and b;
        }
        """
    )

    assert netlist["component"]["id"] == "Test"

    busses = busses_by_id(netlist)
    assert list(busses) == ["a", "b", "y"]
    assert busses["a"]["assignment"] is None
    assert busses["a"]["influence_list"] == ["y"]
    assert busses["b"]["assignment"] is None
    assert busses["b"]["influence_list"] == ["y"]
    assert busses["y"]["assignment"] == {
        "type": "and",
        "args": {
            "l_expr": {
                "type": "ref",
                "args": {"id": "a", "slice_begin": None, "slice_end": None},
            },
            "r_expr": {
                "type": "ref",
                "args": {"id": "b", "slice_begin": None, "slice_end": None},
            },
        },
    }
    assert busses["y"]["influence_list"] == []


def test_builds_dimensions_slices_and_concatenations() -> None:
    netlist = build_netlist(
        """
        comp Test {
            in bit[-4] a;
            out bit[6] y;

            y = <a[3:2], a[0]>;
        }
        """
    )

    busses = busses_by_id(netlist)
    assert busses["a"]["value"] == [False, False, False, False]
    assert busses["a"]["msb_descending"] is True
    assert busses["a"]["influence_list"] == ["y"]
    assert busses["y"]["value"] == [False, False, False, False, False, False]
    assert busses["y"]["assignment"] == {
        "type": "conc",
        "args": {
            "exprs": [
                {
                    "type": "ref",
                    "args": {"id": "a", "slice_begin": 3, "slice_end": 2},
                },
                {
                    "type": "ref",
                    "args": {"id": "a", "slice_begin": None, "slice_end": None},
                },
            ]
        },
    }


def test_builds_main_component_with_subcomponent_busses() -> None:
    netlist = build_netlist(
        """
        comp AndGate {
            in bit a, b;
            out bit y;

            y = a and b;
        }

        main comp Top {
            in bit a, b;
            out bit y;
            sub AndGate as gate;

            gate.a = a;
            gate.b = b;
            y = gate.y;
        }
        """
    )

    assert netlist["component"]["id"] == "Top"

    busses = busses_by_id(netlist)
    assert list(busses) == ["gate.a", "gate.b", "gate.y", "a", "b", "y"]
    assert busses["gate.a"]["assignment"] == {
        "type": "ref",
        "args": {"id": "a", "slice_begin": None, "slice_end": None},
    }
    assert busses["gate.b"]["assignment"] == {
        "type": "ref",
        "args": {"id": "b", "slice_begin": None, "slice_end": None},
    }
    assert busses["gate.y"]["assignment"]["type"] == "and"
    assert busses["y"]["assignment"] == {
        "type": "ref",
        "args": {"id": "gate.y", "slice_begin": None, "slice_end": None},
    }


def test_builds_components_that_are_not_used_by_main_component() -> None:
    ast = Parser(
        Scanner(
            """
            comp Unused {
                in bit a;
                out bit y;

                y = a;
            }

            main comp Top {
                out bit y = "1";
            }
            """
        ).token_stream
    ).ast

    builder = Builder(ast)

    assert set(builder.components) == {"Unused", "Top"}


@pytest.mark.parametrize(
    ("code", "message"),
    [
        ("comp Test { in bit a = b; }", "cannot be assigned"),
        (
            "comp Test { bit a; bit a; }",
            "has already been declared",
        ),
        (
            "comp Test { in bit a; a = a; }",
            "Input Buses of top level",
        ),
        (
            "comp Test { bit a; a = a; a = a; }",
            'Identifier "a" already assigned',
        ),
        (
            "comp Test { in bit[2] a; bit y; y = a; }",
            "Assignment size",
        ),
        (
            "comp Test { in bit[-3] a; bit[2] y; y = a[1:2]; }",
            "begin index must be equal or greater",
        ),
        (
            "comp Test { sub Missing; }",
            '"Missing" has not been declared',
        ),
        (
            "comp Child { in bit a; } "
            "main comp Top { sub Child as child; bit y; y = child.a; }",
            "cannot be referenced from the higher level component",
        ),
    ],
)
def test_raises_semantical_error_for_invalid_designs(code: str, message: str) -> None:
    with pytest.raises(SemanticalError, match=message):
        build_netlist(code)


def test_raises_assertion_error_for_undeclared_bus_reference() -> None:
    with pytest.raises(AssertionError, match='Bus reference "a" has not been declared'):
        build_netlist("comp Test { out bit y; y = a; }")
