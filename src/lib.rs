use pyo3::prelude::*;
use pyo3::exceptions::{PyValueError, PyRuntimeError};
use std::collections::HashMap;

// Módulos internos
pub mod busses;
pub mod expr_nodes;
pub mod component;
pub mod renderer;

// Re-exports para facilitar o uso
use component::Component as RustComponent;
use renderer::Renderer as RustRenderer;

/// Wrapper PyClass para Component
#[pyclass(unsendable)]
pub struct Component {
    inner: RustComponent,
}

#[pymethods]
impl Component {
    #[new]
    fn new(id: String) -> Self {
        Component {
            inner: RustComponent::new(id),
        }
    }

    /// Cria um novo bus
    fn create_bus(&mut self, id: String, dimension: usize) {
        self.inner.create_bus(id, dimension);
    }

    /// Obtém o valor de um bus
    fn get_bus_value(&self, bus_id: String) -> Option<String> {
        self.inner.get_bus_value(&bus_id)
    }

    /// Define o valor de um bus
    fn set_bus_value(&mut self, bus_id: String, value: String) -> PyResult<()> {
        self.inner.set_bus_value(bus_id, value)
            .map_err(|e| PyValueError::new_err(e))
    }

    /// Retorna todos os valores como dicionário
    fn get_values(&self) -> HashMap<String, String> {
        self.inner.get_values()
    }

    /// Estabiliza o componente
    fn stabilize(&mut self) {
        self.inner.stabilize();
    }

    /// Atualiza sinais com novos valores
    fn update_signals(&mut self, new_values: HashMap<String, String>) -> PyResult<()> {
        self.inner.update_signals(new_values)
            .map_err(|e| PyRuntimeError::new_err(e))
    }

    /// Representação string do componente
    fn __str__(&self) -> String {
        format!("{}", self.inner)
    }

    fn __repr__(&self) -> String {
        self.__str__()
    }

    /// Propriedade busses (compatibilidade com Python)
    #[getter]
    fn get_busses(&self) -> PyResult<HashMap<String, String>> {
        // Retorna uma representação simplificada dos busses como strings
        let busses: HashMap<String, String> = self.inner.busses
            .iter()
            .map(|(id, bus)| (id.clone(), format!("{}", bus)))
            .collect();
        Ok(busses)
    }

    /// Propriedade id_ (compatibilidade com Python)
    #[getter]
    fn get_id_(&self) -> String {
        self.inner.id.clone()
    }
}

/// Wrapper PyClass para Renderer
#[pyclass(unsendable)]
pub struct Renderer {
    inner: RustRenderer,
}

#[pymethods]
impl Renderer {
    #[new]
    fn new(ir: String) -> PyResult<Self> {
        let mut inner = RustRenderer::new_empty(ir.clone());
        match inner.render() {
            Ok(component) => {
                inner.component = Some(component);
                Ok(Renderer { inner })
            },
            Err(e) => Err(PyRuntimeError::new_err(format!("Failed to render circuit: {}", e)))
        }
    }

    /// Renderiza uma expressão a partir de JSON
    fn render_expr(&mut self, j_expr: String) -> PyResult<String> {
        // Primeiro, parse do JSON string
        let json_value: serde_json::Value = serde_json::from_str(&j_expr)
            .map_err(|e| PyValueError::new_err(format!("Invalid JSON: {}", e)))?;

        // Renderiza a expressão
        match self.inner.render_expr(&json_value) {
            Ok(_expr) => {
                // Como não podemos retornar Box<dyn Evaluator> para Python,
                // retornamos uma representação string
                Ok(format!("Expression rendered successfully"))
            }
            Err(e) => Err(PyRuntimeError::new_err(e))
        }
    }

    /// Obtém referência ao componente renderizado
    #[getter]
    fn get_component(&self) -> PyResult<Component> {
        match self.inner.get_component() {
            Some(comp) => {
                // Clona o componente interno para criar um novo wrapper
                Ok(Component {
                    inner: comp.clone(),
                })
            }
            None => Err(PyRuntimeError::new_err("Component not available"))
        }
    }

    /// Representação string do renderer
    fn __str__(&self) -> String {
        format!("Renderer with IR length: {}", self.inner.ir.len())
    }

    fn __repr__(&self) -> String {
        self.__str__()
    }
}

/// Funções auxiliares para uso interno (não expostas ao Python)
impl Component {
    /// Acessa o componente Rust interno (para uso interno)
    pub fn inner(&self) -> &RustComponent {
        &self.inner
    }

    /// Acessa o componente Rust interno mutável (para uso interno)
    pub fn inner_mut(&mut self) -> &mut RustComponent {
        &mut self.inner
    }
}

impl Renderer {
    /// Acessa o renderer Rust interno (para uso interno)
    pub fn inner(&self) -> &RustRenderer {
        &self.inner
    }

    /// Acessa o renderer Rust interno mutável (para uso interno)
    pub fn inner_mut(&mut self) -> &mut RustRenderer {
        &mut self.inner
    }
}

/// Módulo Python
#[pymodule]
fn core(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Adiciona as classes principais
    m.add_class::<Component>()?;
    m.add_class::<Renderer>()?;

    // Adiciona informações do módulo
    m.add("__version__", "0.5.0")?;
    m.add("__author__", "Flote Rust Backend")?;

    Ok(())
}
