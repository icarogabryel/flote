use std::fmt;
use std::fmt::{Display, Debug};

/// Trait para objetos que podem ser convertidos para representação VCD
pub trait VcdValue {
    fn get_vcd_repr(&self) -> String;
}

/// Representa um valor de bus no circuito
pub trait BusValueTrait: VcdValue + Clone + Debug {
    fn get_default() -> Self where Self: Sized;
}

/// Implementação para valores de bit bus
#[derive(Debug, Clone, PartialEq)]
pub struct BitBusValue {
    pub raw_value: Vec<bool>,
}

impl BitBusValue {
    pub fn new(value: Option<Vec<bool>>) -> Self {
        match value {
            Some(v) => BitBusValue { raw_value: v },
            None => BitBusValue::get_default(),
        }
    }

    pub fn from_string(value: &str) -> Result<Self, String> {
        let bits: Result<Vec<bool>, _> = value
            .chars()
            .map(|c| match c {
                '0' => Ok(false),
                '1' => Ok(true),
                _ => Err(format!("Invalid character '{}' in bit string", c)),
            })
            .collect();

        match bits {
            Ok(raw_value) => Ok(BitBusValue { raw_value }),
            Err(e) => Err(e),
        }
    }

    // Operadores bit a bit
    pub fn invert(&self) -> BitBusValue {
        BitBusValue {
            raw_value: self.raw_value.iter().map(|&bit| !bit).collect(),
        }
    }

    pub fn and(&self, other: &BitBusValue) -> BitBusValue {
        BitBusValue {
            raw_value: self.raw_value
                .iter()
                .zip(&other.raw_value)
                .map(|(&a, &b)| a && b)
                .collect(),
        }
    }

    pub fn or(&self, other: &BitBusValue) -> BitBusValue {
        BitBusValue {
            raw_value: self.raw_value
                .iter()
                .zip(&other.raw_value)
                .map(|(&a, &b)| a || b)
                .collect(),
        }
    }

    pub fn xor(&self, other: &BitBusValue) -> BitBusValue {
        BitBusValue {
            raw_value: self.raw_value
                .iter()
                .zip(&other.raw_value)
                .map(|(&a, &b)| a ^ b)
                .collect(),
        }
    }
}

impl BusValueTrait for BitBusValue {
    fn get_default() -> Self {
        BitBusValue {
            raw_value: vec![false],
        }
    }
}

impl VcdValue for BitBusValue {
    fn get_vcd_repr(&self) -> String {
        self.raw_value
            .iter()
            .map(|&bit| if bit { '1' } else { '0' })
            .collect()
    }
}

impl Display for BitBusValue {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let bit_string: String = self.raw_value
            .iter()
            .map(|&bit| if bit { '1' } else { '0' })
            .collect();
        write!(f, "{}", bit_string)
    }
}

/// Representa um bus no circuito
pub trait BusTrait {
    type Value: BusValueTrait;

    fn get_id(&self) -> &Option<String>;
    fn set_id(&mut self, id: String);
    fn get_value(&self) -> &Self::Value;
    fn set_value(&mut self, value: Self::Value);
    fn get_valid_values(&self) -> Vec<String>;
    fn insert_value(&mut self, value: &str) -> Result<(), String>;
}

/// Implementação de BitBus
#[derive(Debug, Clone)]
pub struct BitBus {
    pub id: Option<String>,
    pub value: BitBusValue,
    pub influence_list: Vec<usize>, // Indices para evitar problemas de ownership
}

impl BitBus {
    pub fn new() -> Self {
        BitBus {
            id: None,
            value: BitBusValue::get_default(),
            influence_list: Vec::new(),
        }
    }

    pub fn set_dimension(&mut self, dimension: usize) {
        self.value = BitBusValue {
            raw_value: vec![false; dimension],
        };
    }
}

impl BusTrait for BitBus {
    type Value = BitBusValue;

    fn get_id(&self) -> &Option<String> {
        &self.id
    }

    fn set_id(&mut self, id: String) {
        self.id = Some(id);
    }

    fn get_value(&self) -> &Self::Value {
        &self.value
    }

    fn set_value(&mut self, value: Self::Value) {
        self.value = value;
    }

    fn get_valid_values(&self) -> Vec<String> {
        vec!["[01]+".to_string()]
    }

    fn insert_value(&mut self, value: &str) -> Result<(), String> {
        // Validação do formato
        if !value.chars().all(|c| c == '0' || c == '1') {
            return Err(format!(
                "Invalid value \"{}\". Valid values are: {:?}",
                value, self.get_valid_values()
            ));
        }

        // Validação do tamanho
        if value.len() != self.value.raw_value.len() {
            return Err(format!(
                "Invalid value \"{}\". The value must have {} bits.",
                value, self.value.raw_value.len()
            ));
        }

        // Remove aspas se presentes (como no Python)
        let clean_value = value.trim_matches('"');

        // Converte string para BitBusValue
        match BitBusValue::from_string(clean_value) {
            Ok(new_value) => {
                self.value = new_value;
                Ok(())
            }
            Err(e) => Err(e),
        }
    }
}

impl Display for BitBus {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "id: {:?} IL: {:?} Value: {}",
            self.id, self.influence_list, self.value
        )
    }
}

/// Erro de simulação
#[derive(Debug, Clone)]
pub struct SimulationError {
    pub message: String,
}

impl SimulationError {
    pub fn new(message: String) -> Self {
        SimulationError { message }
    }
}

impl Display for SimulationError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.message)
    }
}

impl std::error::Error for SimulationError {}
