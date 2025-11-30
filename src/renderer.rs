use crate::busses::{BitBus, BitBusValue, BusValueTrait, BusTrait};
use crate::component::Component;
use crate::expr_nodes::{Evaluator, BusRef, Const, Not, And, Or, Xor, Nand, Nor, Xnor};
use serde_json::{Value, from_str};
use std::collections::HashMap;

/// Renderizador que converte JSON IR para objetos Rust
#[derive(Debug)]
pub struct Renderer {
    pub ir: String,
    pub buffer_bus_dict: HashMap<String, BitBus>,
    pub component: Option<Component>,
}

impl Renderer {
    pub fn new(ir: String) -> Self {
        let mut renderer = Renderer {
            ir,
            buffer_bus_dict: HashMap::new(),
            component: None,
        };

        // Renderiza o componente na criação
        match renderer.render() {
            Ok(component) => renderer.component = Some(component),
            Err(_) => {} // Mantém component como None em caso de erro
        }

        renderer
    }

    /// Renderiza uma expressão a partir do JSON IR
    pub fn render_expr(&mut self, j_expr: &Value) -> Result<Box<dyn Evaluator>, String> {
        let expr_type = j_expr.get("type")
            .and_then(|v| v.as_str())
            .ok_or("Missing or invalid 'type' field")?;

        match expr_type {
            "const" => {
                let value = j_expr.get("args")
                    .and_then(|args| args.get("value"))
                    .ok_or("Missing 'value' in const expression")?;

                let bit_value = match value {
                    Value::Array(arr) => {
                        let bits: Vec<bool> = arr.iter()
                            .map(|v| v.as_bool().unwrap_or(false))
                            .collect();
                        BitBusValue::new(Some(bits))
                    },
                    Value::String(s) => {
                        BitBusValue::from_string(s)
                            .map_err(|e| format!("Invalid const value: {}", e))?
                    },
                    _ => return Err("Invalid const value type".to_string()),
                };

                Ok(Box::new(Const::new(bit_value)))
            },

            "bus_ref" => {
                let bus_id = j_expr.get("args")
                    .and_then(|args| args.get("id"))
                    .and_then(|v| v.as_str())
                    .ok_or("Missing 'id' in bus_ref expression")?;

                Ok(Box::new(BusRef::new(bus_id.to_string())))
            },

            "not" => {
                let expr_json = j_expr.get("args")
                    .and_then(|args| args.get("expr"))
                    .ok_or("Missing 'expr' in not expression")?;

                let expr = self.render_expr(expr_json)?;
                Ok(Box::new(Not::new(expr)))
            },

            "and" => {
                let args = j_expr.get("args").ok_or("Missing 'args' in and expression")?;
                let l_expr = self.render_expr(args.get("l_expr").ok_or("Missing 'l_expr'")?)?;
                let r_expr = self.render_expr(args.get("r_expr").ok_or("Missing 'r_expr'")?)?;
                Ok(Box::new(And::new(l_expr, r_expr)))
            },

            "or" => {
                let args = j_expr.get("args").ok_or("Missing 'args' in or expression")?;
                let l_expr = self.render_expr(args.get("l_expr").ok_or("Missing 'l_expr'")?)?;
                let r_expr = self.render_expr(args.get("r_expr").ok_or("Missing 'r_expr'")?)?;
                Ok(Box::new(Or::new(l_expr, r_expr)))
            },

            "xor" => {
                let args = j_expr.get("args").ok_or("Missing 'args' in xor expression")?;
                let l_expr = self.render_expr(args.get("l_expr").ok_or("Missing 'l_expr'")?)?;
                let r_expr = self.render_expr(args.get("r_expr").ok_or("Missing 'r_expr'")?)?;
                Ok(Box::new(Xor::new(l_expr, r_expr)))
            },

            "nand" => {
                let args = j_expr.get("args").ok_or("Missing 'args' in nand expression")?;
                let l_expr = self.render_expr(args.get("l_expr").ok_or("Missing 'l_expr'")?)?;
                let r_expr = self.render_expr(args.get("r_expr").ok_or("Missing 'r_expr'")?)?;
                Ok(Box::new(Nand::new(l_expr, r_expr)))
            },

            "nor" => {
                let args = j_expr.get("args").ok_or("Missing 'args' in nor expression")?;
                let l_expr = self.render_expr(args.get("l_expr").ok_or("Missing 'l_expr'")?)?;
                let r_expr = self.render_expr(args.get("r_expr").ok_or("Missing 'r_expr'")?)?;
                Ok(Box::new(Nor::new(l_expr, r_expr)))
            },

            "xnor" => {
                let args = j_expr.get("args").ok_or("Missing 'args' in xnor expression")?;
                let l_expr = self.render_expr(args.get("l_expr").ok_or("Missing 'l_expr'")?)?;
                let r_expr = self.render_expr(args.get("r_expr").ok_or("Missing 'r_expr'")?)?;
                Ok(Box::new(Xnor::new(l_expr, r_expr)))
            },

            _ => Err(format!("Unknown expression type: {}", expr_type)),
        }
    }

    /// Renderiza um circuito completo a partir do JSON IR
    pub fn render(&mut self) -> Result<Component, String> {
        // Parse do JSON IR
        let j_ir: Value = from_str(&self.ir)
            .map_err(|e| format!("Failed to parse IR JSON: {}", e))?;

        let j_component = j_ir.get("component")
            .ok_or("Missing 'component' in IR")?;

        let j_component_id = j_component.get("id")
            .and_then(|v| v.as_str())
            .ok_or("Missing or invalid 'id' in component")?;

        let mut component = Component::new(j_component_id.to_string());

        let j_busses = j_component.get("busses")
            .and_then(|v| v.as_array())
            .ok_or("Missing or invalid 'busses' array")?;

        // Primeira passada: criar todos os buses
        for j_bus in j_busses {
            let bus_id = j_bus.get("id")
                .and_then(|v| v.as_str())
                .ok_or("Missing 'id' in bus")?;

            let mut bit_bus = BitBus::new();
            bit_bus.set_id(bus_id.to_string());

            // Define o valor inicial
            if let Some(value) = j_bus.get("value") {
                let bit_value = match value {
                    Value::Array(arr) => {
                        let bits: Vec<bool> = arr.iter()
                            .map(|v| v.as_bool().unwrap_or(false))
                            .collect();
                        BitBusValue::new(Some(bits))
                    },
                    Value::String(s) => {
                        BitBusValue::from_string(s)
                            .unwrap_or_else(|_| BitBusValue::get_default())
                    },
                    _ => BitBusValue::get_default(),
                };
                bit_bus.value = bit_value;
            }

            self.buffer_bus_dict.insert(bus_id.to_string(), bit_bus.clone());
            component.add_bus(bus_id.to_string(), bit_bus);
        }

        // Segunda passada: definir assignments e influence lists
        for j_bus in j_busses {
            let bus_id = j_bus.get("id")
                .and_then(|v| v.as_str())
                .ok_or("Missing 'id' in bus")?;

            // Processa assignment se existir
            if let Some(assignment_json) = j_bus.get("assignment") {
                if !assignment_json.is_null() {
                    let assignment = self.render_expr(assignment_json)?;
                    component.set_assignment(bus_id.to_string(), assignment);
                }
            }

            // Processa influence list se existir
            if let Some(influence_list) = j_bus.get("influence_list").and_then(|v| v.as_array()) {
                for influenced_bus_value in influence_list {
                    if let Some(influenced_bus_id) = influenced_bus_value.as_str() {
                        component.add_influence(bus_id, influenced_bus_id)
                            .map_err(|e| format!("Failed to add influence: {}", e))?;
                    }
                }
            }
        }

        Ok(component)
    }

    /// Obtém uma referência ao componente renderizado
    pub fn get_component(&self) -> Option<&Component> {
        self.component.as_ref()
    }

    /// Obtém uma referência mutável ao componente renderizado
    pub fn get_component_mut(&mut self) -> Option<&mut Component> {
        self.component.as_mut()
    }
}
