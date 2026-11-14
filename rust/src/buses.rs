use crate::ir::expression::ExpressionDto;

#[derive(Debug, Clone)]
pub struct BitBus {
    pub id: String,
    pub assignment: Option<ExpressionDto>,
    pub value: String,
    pub influence_list: Vec<String>,
    pub msb_descending: bool,
}
