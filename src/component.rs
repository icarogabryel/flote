use crate::busses::{BitBus, BitBusValue, BusTrait, BusValueTrait};
use crate::expr_nodes::Evaluator;
use std::collections::{HashMap, VecDeque};
use std::fmt::{Display, Debug};

/// Representa um componente no circuito
#[derive(Debug, Clone)]
pub struct Component {
    pub id: String,
    pub busses: HashMap<String, BitBus>,
    pub assignments: HashMap<String, Box<dyn Evaluator>>, // Separamos assignments para evitar problemas de thread safety
}

impl Component {
    pub fn new(id: String) -> Self {
        Component {
            id,
            busses: HashMap::new(),
            assignments: HashMap::new(),
        }
    }

    /// Retorna os valores do componente como um dicionário
    pub fn get_values(&self) -> HashMap<String, String> {
        self.busses
            .iter()
            .map(|(name, bus)| (name.clone(), bus.value.to_string()))
            .collect()
    }

    /// Estabiliza os bits do componente
    pub fn stabilize(&mut self) {
        let mut queue: VecDeque<String> = self.busses.keys().cloned().collect();

        while let Some(bus_id) = queue.pop_front() {
            if let Some(assignment) = self.assignments.get(&bus_id) {
                // Avalia a expressão
                let new_value = assignment.evaluate(&self.busses);

                // Verifica se houve mudança
                let previous_value = self.busses.get(&bus_id)
                    .map(|bus| bus.value.clone())
                    .unwrap_or_else(|| BitBusValue::get_default());

                // Coleta os índices de influência antes da mutação
                let influence_indices: Vec<usize> = self.busses.get(&bus_id)
                    .map(|bus| bus.influence_list.clone())
                    .unwrap_or_default();

                // Atualiza o valor
                if let Some(bus_mut) = self.busses.get_mut(&bus_id) {
                    bus_mut.value = new_value.clone();

                    // Se houve mudança, adiciona os buses influenciados à fila
                    if previous_value != new_value {
                        // Agora usa os índices coletados anteriormente
                        for &influenced_idx in &influence_indices {
                            // Convertemos o índice de volta para ID do bus
                            if let Some((influenced_id, _)) = self.busses.iter().nth(influenced_idx) {
                                let influenced_id = influenced_id.clone();
                                if !queue.contains(&influenced_id) {
                                    queue.push_back(influenced_id);
                                }
                            }
                        }
                    }
                }
            }
        }
    }    /// Atualiza os sinais com novos valores e estabiliza
    pub fn update_signals(&mut self, new_values: HashMap<String, String>) -> Result<(), String> {
        // Atualiza os valores
        for (id, new_value) in new_values {
            if let Some(bus) = self.busses.get_mut(&id) {
                bus.insert_value(&new_value)?;
            }
        }

        // Estabiliza o circuito
        self.stabilize();

        Ok(())
    }

    /// Adiciona um bus ao componente
    pub fn add_bus(&mut self, id: String, mut bus: BitBus) {
        bus.set_id(id.clone());
        self.busses.insert(id, bus);
    }

    /// Define uma atribuição para um bus
    pub fn set_assignment(&mut self, bus_id: String, assignment: Box<dyn Evaluator>) {
        self.assignments.insert(bus_id, assignment);
    }

    /// Adiciona um bus à lista de influência de outro bus
    pub fn add_influence(&mut self, influencer_id: &str, influenced_id: &str) -> Result<(), String> {
        // Encontra o índice do bus influenciado
        let influenced_idx = self.busses
            .keys()
            .enumerate()
            .find(|(_, id)| *id == influenced_id)
            .map(|(idx, _)| idx)
            .ok_or_else(|| format!("Bus '{}' not found", influenced_id))?;

        // Adiciona o índice à lista de influência do bus influenciador
        if let Some(influencer_bus) = self.busses.get_mut(influencer_id) {
            if !influencer_bus.influence_list.contains(&influenced_idx) {
                influencer_bus.influence_list.push(influenced_idx);
            }
            Ok(())
        } else {
            Err(format!("Bus '{}' not found", influencer_id))
        }
    }

    /// Cria um novo bus e o adiciona ao componente
    pub fn create_bus(&mut self, id: String, dimension: usize) {
        let mut bus = BitBus::new();
        bus.set_dimension(dimension);
        self.add_bus(id, bus);
    }

    /// Obtém o valor de um bus específico
    pub fn get_bus_value(&self, bus_id: &str) -> Option<String> {
        self.busses.get(bus_id).map(|bus| bus.value.to_string())
    }

    /// Define o valor de um bus específico
    pub fn set_bus_value(&mut self, bus_id: String, value: String) -> Result<(), String> {
        if let Some(bus) = self.busses.get_mut(&bus_id) {
            bus.insert_value(&value)
        } else {
            Err(format!("Bus '{}' not found", bus_id))
        }
    }
}

impl Display for Component {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let mut result = String::new();
        for (bus_id, bus) in &self.busses {
            result.push_str(&format!("{}: {} {:?}\n", bus_id, bus, bus.influence_list));
        }
        write!(f, "{}", result)
    }
}
