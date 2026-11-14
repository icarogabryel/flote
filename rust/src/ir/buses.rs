use crate::ir::expression::ExpressionDto;
use pyo3::FromPyObject;

#[derive(Debug, Clone, FromPyObject)]
pub struct BitBusDto {
    pub identifier: String,
    pub dimension: usize,
    pub msb_descending: bool,
    pub assignment: Option<ExpressionDto>,
    pub value: String,
    pub influence_list: Vec<String>,
}
