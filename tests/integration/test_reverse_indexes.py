import json

import pytest

import flote
from flote.elaboration.builder import SemanticalError
from flote.testbench import TestBench as FloteTestBench


def _get_bus_bits(tb: FloteTestBench, bus_id: str) -> str:
    return tb.component.buses[bus_id].value.get_vcd_repr()


def test_netlist_marks_descending_msb() -> None:
    code = """
    comp Test {
        in bit[-8] a;
        out bit y = a[1];
    }
    """
    netlist = flote.get_netlist(code)
    data = json.loads(netlist)
    busses = {bus["id"]: bus for bus in data["component"]["buses"]}

    assert busses["a"]["msb_descending"] is True
    assert busses["y"]["msb_descending"] is False


def test_out_of_bounds_index_on_descending_bus() -> None:
    code = """
    comp Test {
        in bit[-8] a;
        out bit y = a[8];
    }
    """
    with pytest.raises(SemanticalError, match="out of bounds"):
        flote.get_netlist(code)


def test_invalid_slice_order_on_descending_bus() -> None:
    code = """
    comp Test {
        in bit[-8] a;
        out bit[2] y = a[1:2];
    }
    """
    with pytest.raises(SemanticalError, match="descending buses"):
        flote.get_netlist(code)


def test_reverse_index_value() -> None:
    code = """
    comp Test {
        in bit[-8] a;
        out bit y = a[1];
    }
    """
    tb = flote.elaborate(code)
    tb.update({"a": "00000010"})

    assert _get_bus_bits(tb, "y") == "1"


def test_reverse_slice_value() -> None:
    code = """
    comp Test {
        in bit[-8] a;
        out bit[2] y = a[2:1];
    }
    """
    tb = flote.elaborate(code)
    tb.update({"a": "00000100"})

    assert _get_bus_bits(tb, "y") == "10"
