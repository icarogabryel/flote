import json

import pytest

import flote
from flote.elaboration.builder import SemanticalError


def _has_rust_backend() -> bool:
    try:
        from flote.simulation.fpga import Renderer as _RustRenderer  # noqa: F401
    except ImportError:
        return False
    return True


def _get_bus_bits(tb, bus_id: str) -> str:
    comp = tb.component
    if hasattr(comp, "busses"):
        return comp.busses[bus_id]
    return comp.buses[bus_id].get_vcd_repr()


def test_netlist_marks_descending_msb():
    code = """
    comp Test {
        in bit[-8] a;
        out bit y = a[1];
    }
    """
    netlist = flote.get_netlist(code)
    data = json.loads(netlist)
    busses = {bus["id"]: bus for bus in data["component"]["busses"]}

    assert busses["a"]["msb_descending"] is True
    assert busses["y"]["msb_descending"] is False


def test_out_of_bounds_index_on_descending_bus():
    code = """
    comp Test {
        in bit[-8] a;
        out bit y = a[8];
    }
    """
    with pytest.raises(SemanticalError, match="out of bounds"):
        flote.get_netlist(code)


def test_invalid_slice_order_on_descending_bus():
    code = """
    comp Test {
        in bit[-8] a;
        out bit[2] y = a[0:1];
    }
    """
    with pytest.raises(SemanticalError, match="descending buses"):
        flote.get_netlist(code)


@pytest.mark.parametrize("rust_backend", [False, True])
def test_reverse_index_value(rust_backend: bool):
    if rust_backend and not _has_rust_backend():
        pytest.skip("Rust backend not available")

    code = """
    comp Test {
        in bit[-8] a;
        out bit y = a[1];
    }
    """
    tb = flote.elaborate(code, rust_backend=rust_backend)
    tb.update({"a": "00000010"})

    assert _get_bus_bits(tb, "y") == "1"


@pytest.mark.parametrize("rust_backend", [False, True])
def test_reverse_slice_value(rust_backend: bool):
    if rust_backend and not _has_rust_backend():
        pytest.skip("Rust backend not available")

    code = """
    comp Test {
        in bit[-8] a;
        out bit[2] y = a[1:0];
    }
    """
    tb = flote.elaborate(code, rust_backend=rust_backend)
    tb.update({"a": "00000010"})

    assert _get_bus_bits(tb, "y") == "10"
