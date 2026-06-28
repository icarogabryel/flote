import json

import pytest

from flote.elaboration.builder import Builder, SemanticalError
from flote.elaboration.parser import Parser
from flote.elaboration.scanner import Scanner


def build_netlist(code: str) -> dict:
    ast = Parser(Scanner(code).token_stream).ast
    return json.loads(Builder(ast).netlist)


def busses_by_id(netlist: dict) -> dict:
    return {bus["id"]: bus for bus in netlist["component"]["busses"]}


def test_builds_netlist_with_assignments_and_influence_lists():
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


def test_builds_dimensions_slices_and_concatenations():
    netlist = build_netlist(
        """
        comp Test {
            in bit[-4] a;
            out bit[3] y;

            y = <a[3:2], a[0]>;
        }
        """
    )

    busses = busses_by_id(netlist)
    assert busses["a"]["value"] == [False, False, False, False]
    assert busses["a"]["msb_descending"] is True
    assert busses["a"]["influence_list"] == ["y"]
    assert busses["y"]["value"] == [False, False, False]
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
                    "args": {"id": "a", "slice_begin": 0, "slice_end": 0},
                },
            ]
        },
    }


def test_builds_main_component_with_subcomponent_busses():
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


@pytest.mark.parametrize(
    ("code", "message"),
    [
        ("comp Test { in bit a = b; }", "cannot be assigned"),
        ("comp Test { bit a; bit a; }", "has already been declared"),
        ("comp Test { out bit y; y = a; }", 'Bus reference "a" has not been declared'),
        ("comp Test { in bit a; a = a; }", "Input Buses of top level"),
        ("comp Test { bit a; a = a; a = a; }", 'Identifier "a" already assigned'),
        ("comp Test { in bit[2] a; bit y; y = a; }", "Assignment size"),
        (
            "comp Test { in bit[2] a; bit[2] y; y = a[1:0]; }",
            "end index must be equal or greater",
        ),
        ("comp Test { sub Missing; }", "Component 'Missing' not found"),
        (
            "comp Child { in bit a; } "
            "comp Top { sub Child as child; bit y; y = child.a; }",
            "cannot be referenced from the higher level component",
        ),
    ],
)
def test_raises_semantical_error_for_invalid_designs(code: str, message: str):
    with pytest.raises(SemanticalError, match=message):
        build_netlist(code)
