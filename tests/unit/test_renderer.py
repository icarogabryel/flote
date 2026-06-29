import json

import pytest

from flote.simulation import eval_nodes
from flote.simulation.buses import BitBus, BitBusValue
from flote.simulation.renderer import Renderer


def render_component(ir: dict):
    return Renderer(json.dumps(ir)).component


def bit_bus(
    id_: str,
    value: list[bool] | None = None,
    assignment: dict | None = None,
    influence_list: list[str] | None = None,
    msb_descending: bool = False,
) -> dict:
    return {
        "id": id_,
        "type": "bit_bus",
        "value": [False] if value is None else value,
        "msb_descending": msb_descending,
        "assignment": assignment,
        "influence_list": [] if influence_list is None else influence_list,
    }


def ref(id_: str, slice_begin: int | None = None, slice_end: int | None = None) -> dict:
    return {
        "type": "ref",
        "args": {
            "id": id_,
            "slice_begin": slice_begin,
            "slice_end": slice_end,
        },
    }


def const(value: list[bool]) -> dict:
    return {"type": "const", "args": {"value": value}}


def test_renders_component_busses_values_and_influence_lists():
    component = render_component(
        {
            "component": {
                "id": "Test",
                "busses": [
                    bit_bus("a", [True, False], influence_list=["y"]),
                    bit_bus("y", [False, False], msb_descending=True),
                ],
            }
        }
    )

    assert component.id_ == "Test"
    assert list(component.buses) == ["a", "y"]
    assert isinstance(component.buses["a"], BitBus)
    assert component.buses["a"].value == BitBusValue([True, False])
    assert component.buses["a"].msb_descending is False
    assert component.buses["a"].influence_list == [component.buses["y"]]
    assert component.buses["y"].value == BitBusValue([False, False])
    assert component.buses["y"].msb_descending is True


def test_renders_ref_assignment_and_updates_component_values():
    component = render_component(
        {
            "component": {
                "id": "Test",
                "busses": [
                    bit_bus("a", influence_list=["y"]),
                    bit_bus("y", assignment=ref("a")),
                ],
            }
        }
    )

    y = component.buses["y"]
    assert isinstance(y.assignment, eval_nodes.Ref)
    assert y.assignment.bus is component.buses["a"]

    component.update_signals({"a": "1"})

    assert component.buses["y"].value.get_vcd_repr() == "1"


@pytest.mark.parametrize(
    ("expr_type", "expected"),
    [
        ("and", "00"),
        ("or", "11"),
        ("xor", "11"),
        ("nand", "11"),
        ("nor", "00"),
        ("xnor", "00"),
    ],
)
def test_renders_binary_operation_assignments(expr_type: str, expected: str):
    component = render_component(
        {
            "component": {
                "id": "Test",
                "busses": [
                    bit_bus("a", [True, False], influence_list=["y"]),
                    bit_bus("b", [False, True], influence_list=["y"]),
                    bit_bus(
                        "y",
                        [False, False],
                        assignment={
                            "type": expr_type,
                            "args": {"l_expr": ref("a"), "r_expr": ref("b")},
                        },
                    ),
                ],
            }
        }
    )

    component.buses["y"].assign()

    assert component.buses["y"].value.get_vcd_repr() == expected


def test_renders_not_concatenation_constants_and_slices():
    component = render_component(
        {
            "component": {
                "id": "Test",
                "busses": [
                    bit_bus(
                        "a",
                        [True, False, True, False],
                        influence_list=["y"],
                    ),
                    bit_bus(
                        "y",
                        [False, False, False, False],
                        assignment={
                            "type": "conc",
                            "args": {
                                "exprs": [
                                    {
                                        "type": "not",
                                        "args": {"expr": ref("a", 0, 1)},
                                    },
                                    const([True, False]),
                                ]
                            },
                        },
                    ),
                ],
            }
        }
    )

    component.buses["y"].assign()

    assert component.buses["y"].value.get_vcd_repr() == "0110"


def test_renders_descending_msb_slices():
    component = render_component(
        {
            "component": {
                "id": "Test",
                "busses": [
                    bit_bus(
                        "a",
                        [False, False, True, False],
                        influence_list=["y"],
                        msb_descending=True,
                    ),
                    bit_bus(
                        "y",
                        [False, False],
                        assignment=ref("a", 1, 0),
                    ),
                ],
            }
        }
    )

    component.buses["y"].assign()

    assert component.buses["y"].value.get_vcd_repr() == "10"


@pytest.mark.parametrize(
    ("bus", "message"),
    [
        ({"id": "a", "type": "word_bus", "value": []}, "Invalid IR"),
        (bit_bus("a", assignment={"type": "missing", "args": {}}), "Unknown"),
    ],
)
def test_rejects_invalid_ir(bus: dict, message: str):
    with pytest.raises(AssertionError, match=message):
        render_component({"component": {"id": "Test", "busses": [bus]}})
