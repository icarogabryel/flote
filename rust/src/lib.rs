use pyo3::prelude::*;

#[pymodule]
fn rust_simulation(_m: &Bound<'_, PyModule>) -> PyResult<()> {
    Ok(())
}
