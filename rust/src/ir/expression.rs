use pyo3::{FromPyObject, PyAny, PyResult};
use pyo3::types::PyAnyMethods;

#[derive(Debug, Clone, FromPyObject)]
pub struct RefDto {
    pub bus: String,
    pub slice_begin: Option<usize>,
    pub slice_end: Option<usize>,
}

#[derive(Debug, Clone, FromPyObject)]
pub struct ConcDto {
    pub exprs: Vec<ExpressionDto>,
}

#[derive(Debug, Clone, FromPyObject)]
pub struct ConstDto {
    pub value: String,
}

#[derive(Debug, Clone, FromPyObject)]
pub struct UnaryOperationDto {
    pub expr: ExpressionDto,
}

#[derive(Debug, Clone, FromPyObject)]
pub struct BinaryOperationDto {
    pub l_expr: ExpressionDto,
    pub r_expr: ExpressionDto,
    pub operation: String,
}

#[derive(Debug, Clone)]
pub enum ExpressionDto {
    Ref(RefDto),
    Conc(ConcDto),
    Const(ConstDto),
    Not(Box<UnaryOperationDto>),
    And(Box<BinaryOperationDto>),
    Or(Box<BinaryOperationDto>),
    Xor(Box<BinaryOperationDto>),
    Nand(Box<BinaryOperationDto>),
    Nor(Box<BinaryOperationDto>),
    Xnor(Box<BinaryOperationDto>),
}

impl<'py> FromPyObject<'py> for ExpressionDto {
    fn extract_bound(object: &pyo3::Bound<'py, PyAny>) -> PyResult<Self> {
        if let Ok(value) = object.extract::<RefDto>() {
            return Ok(Self::Ref(value));
        }
        if let Ok(value) = object.extract::<ConcDto>() {
            return Ok(Self::Conc(value));
        }
        if let Ok(value) = object.extract::<ConstDto>() {
            return Ok(Self::Const(value));
        }
        if let Ok(value) = object.extract::<UnaryOperationDto>() {
            return Ok(Self::Not(Box::new(value)));
        }
        if let Ok(value) = object.extract::<BinaryOperationDto>() {
            let operation = value.operation.as_str();
            return match operation {
                "and" => Ok(Self::And(Box::new(value))),
                "or" => Ok(Self::Or(Box::new(value))),
                "xor" => Ok(Self::Xor(Box::new(value))),
                "nand" => Ok(Self::Nand(Box::new(value))),
                "nor" => Ok(Self::Nor(Box::new(value))),
                "xnor" => Ok(Self::Xnor(Box::new(value))),
                _ => Err(pyo3::exceptions::PyTypeError::new_err(format!(
                    "Unsupported binary operation: {operation}"
                ))),
            };
        }

        Err(pyo3::exceptions::PyTypeError::new_err(
            "Unsupported expression DTO",
        ))
    }
}
