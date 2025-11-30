use crate::busses::{BitBusValue, BitBus, BusValueTrait};
use std::fmt::{Display, Debug};

/// Trait para objetos que podem ser avaliados (equivalente ao Evaluator do Python)
pub trait Evaluator: Send + Sync + Debug {
    fn evaluate(&self, busses: &std::collections::HashMap<String, BitBus>) -> BitBusValue;
    fn clone_box(&self) -> Box<dyn Evaluator>;
}

/// Referência a um bus
#[derive(Debug, Clone)]
pub struct BusRef {
    pub bus_id: String,
}

impl BusRef {
    pub fn new(bus_id: String) -> Self {
        BusRef { bus_id }
    }
}

impl Evaluator for BusRef {
    fn evaluate(&self, busses: &std::collections::HashMap<String, BitBus>) -> BitBusValue {
        match busses.get(&self.bus_id) {
            Some(bus) => bus.value.clone(),
            None => BitBusValue::get_default(),
        }
    }

    fn clone_box(&self) -> Box<dyn Evaluator> {
        Box::new(self.clone())
    }
}

impl Display for BusRef {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.bus_id)
    }
}

/// Constante
#[derive(Debug, Clone)]
pub struct Const {
    pub value: BitBusValue,
}

impl Const {
    pub fn new(value: BitBusValue) -> Self {
        Const { value }
    }
}

impl Evaluator for Const {
    fn evaluate(&self, _busses: &std::collections::HashMap<String, BitBus>) -> BitBusValue {
        self.value.clone()
    }

    fn clone_box(&self) -> Box<dyn Evaluator> {
        Box::new(self.clone())
    }
}

impl Display for Const {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Const({})", self.value)
    }
}

/// Operação unária
#[derive(Debug, Clone)]
pub struct UnaryOperation {
    pub expr: Box<dyn Evaluator>,
}

impl UnaryOperation {
    pub fn new(expr: Box<dyn Evaluator>) -> Self {
        UnaryOperation { expr }
    }
}

/// Operação binária
#[derive(Debug, Clone)]
pub struct BinaryOperation {
    pub l_expr: Box<dyn Evaluator>,
    pub r_expr: Box<dyn Evaluator>,
}

impl BinaryOperation {
    pub fn new(l_expr: Box<dyn Evaluator>, r_expr: Box<dyn Evaluator>) -> Self {
        BinaryOperation { l_expr, r_expr }
    }
}

/// Operação NOT
#[derive(Debug, Clone)]
pub struct Not {
    pub expr: Box<dyn Evaluator>,
}

impl Not {
    pub fn new(expr: Box<dyn Evaluator>) -> Self {
        Not { expr }
    }
}

impl Evaluator for Not {
    fn evaluate(&self, busses: &std::collections::HashMap<String, BitBus>) -> BitBusValue {
        let result = self.expr.evaluate(busses);
        result.invert()
    }

    fn clone_box(&self) -> Box<dyn Evaluator> {
        Box::new(self.clone())
    }
}

impl Display for Not {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Not <expr>")
    }
}

/// Operação AND
#[derive(Debug, Clone)]
pub struct And {
    pub l_expr: Box<dyn Evaluator>,
    pub r_expr: Box<dyn Evaluator>,
}

impl And {
    pub fn new(l_expr: Box<dyn Evaluator>, r_expr: Box<dyn Evaluator>) -> Self {
        And { l_expr, r_expr }
    }
}

impl Evaluator for And {
    fn evaluate(&self, busses: &std::collections::HashMap<String, BitBus>) -> BitBusValue {
        let left = self.l_expr.evaluate(busses);
        let right = self.r_expr.evaluate(busses);
        left.and(&right)
    }

    fn clone_box(&self) -> Box<dyn Evaluator> {
        Box::new(self.clone())
    }
}

impl Display for And {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "And <left> <right>")
    }
}/// Operação OR
#[derive(Debug, Clone)]
pub struct Or {
    pub l_expr: Box<dyn Evaluator>,
    pub r_expr: Box<dyn Evaluator>,
}

impl Or {
    pub fn new(l_expr: Box<dyn Evaluator>, r_expr: Box<dyn Evaluator>) -> Self {
        Or { l_expr, r_expr }
    }
}

impl Evaluator for Or {
    fn evaluate(&self, busses: &std::collections::HashMap<String, BitBus>) -> BitBusValue {
        let left = self.l_expr.evaluate(busses);
        let right = self.r_expr.evaluate(busses);
        left.or(&right)
    }

    fn clone_box(&self) -> Box<dyn Evaluator> {
        Box::new(self.clone())
    }
}

impl Display for Or {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Or <left> <right>")
    }
}/// Operação XOR
#[derive(Debug, Clone)]
pub struct Xor {
    pub l_expr: Box<dyn Evaluator>,
    pub r_expr: Box<dyn Evaluator>,
}

impl Xor {
    pub fn new(l_expr: Box<dyn Evaluator>, r_expr: Box<dyn Evaluator>) -> Self {
        Xor { l_expr, r_expr }
    }
}

impl Evaluator for Xor {
    fn evaluate(&self, busses: &std::collections::HashMap<String, BitBus>) -> BitBusValue {
        let left = self.l_expr.evaluate(busses);
        let right = self.r_expr.evaluate(busses);
        left.xor(&right)
    }

    fn clone_box(&self) -> Box<dyn Evaluator> {
        Box::new(self.clone())
    }
}

impl Display for Xor {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Xor <left> <right>")
    }
}/// Operação NAND
#[derive(Debug, Clone)]
pub struct Nand {
    pub l_expr: Box<dyn Evaluator>,
    pub r_expr: Box<dyn Evaluator>,
}

impl Nand {
    pub fn new(l_expr: Box<dyn Evaluator>, r_expr: Box<dyn Evaluator>) -> Self {
        Nand { l_expr, r_expr }
    }
}

impl Evaluator for Nand {
    fn evaluate(&self, busses: &std::collections::HashMap<String, BitBus>) -> BitBusValue {
        let left = self.l_expr.evaluate(busses);
        let right = self.r_expr.evaluate(busses);
        left.and(&right).invert()
    }

    fn clone_box(&self) -> Box<dyn Evaluator> {
        Box::new(self.clone())
    }
}

impl Display for Nand {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Nand <left> <right>")
    }
}/// Operação NOR
#[derive(Debug, Clone)]
pub struct Nor {
    pub l_expr: Box<dyn Evaluator>,
    pub r_expr: Box<dyn Evaluator>,
}

impl Nor {
    pub fn new(l_expr: Box<dyn Evaluator>, r_expr: Box<dyn Evaluator>) -> Self {
        Nor { l_expr, r_expr }
    }
}

impl Evaluator for Nor {
    fn evaluate(&self, busses: &std::collections::HashMap<String, BitBus>) -> BitBusValue {
        let left = self.l_expr.evaluate(busses);
        let right = self.r_expr.evaluate(busses);
        left.or(&right).invert()
    }

    fn clone_box(&self) -> Box<dyn Evaluator> {
        Box::new(self.clone())
    }
}

impl Display for Nor {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Nor <left> <right>")
    }
}/// Operação XNOR
#[derive(Debug, Clone)]
pub struct Xnor {
    pub l_expr: Box<dyn Evaluator>,
    pub r_expr: Box<dyn Evaluator>,
}

impl Xnor {
    pub fn new(l_expr: Box<dyn Evaluator>, r_expr: Box<dyn Evaluator>) -> Self {
        Xnor { l_expr, r_expr }
    }
}

impl Evaluator for Xnor {
    fn evaluate(&self, busses: &std::collections::HashMap<String, BitBus>) -> BitBusValue {
        let left = self.l_expr.evaluate(busses);
        let right = self.r_expr.evaluate(busses);
        left.xor(&right).invert()
    }

    fn clone_box(&self) -> Box<dyn Evaluator> {
        Box::new(self.clone())
    }
}

impl Display for Xnor {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Xnor <left> <right>")
    }
}// Implementação manual de Clone para Box<dyn Evaluator>
impl Clone for Box<dyn Evaluator> {
    fn clone(&self) -> Self {
        self.clone_box()
    }
}
