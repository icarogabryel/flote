use crate::ir::buses::BitBusDto;
use pyo3::FromPyObject;

#[derive(Debug, Clone, FromPyObject)]
pub struct ComponentDto {
    pub id_: String,
    pub buses: Vec<BitBusDto>,
}
