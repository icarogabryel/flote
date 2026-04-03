use pyo3::prelude::*;

#[pymodule]
fn fpga(_m: &Bound<'_, PyModule>) -> PyResult<()> {
    Ok(())
}
