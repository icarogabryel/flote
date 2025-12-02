use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use std::collections::HashMap;
use std::sync::Mutex;

// Módulos internos
pub mod busses;
pub mod expr_nodes;
pub mod component;
pub mod renderer;

// Re-exports para facilitar o uso
use component::Component as RustComponent;
use renderer::Renderer as RustRenderer;

// Armazenamento global dos componentes Rust puros
// Usa Mutex para thread-safety
static COMPONENTS: Mutex<Option<HashMap<u64, RustComponent>>> = Mutex::new(None);
static NEXT_ID: Mutex<u64> = Mutex::new(0);

/// Inicializa o armazenamento global se necessário
fn init_storage() {
    let mut storage = COMPONENTS.lock().unwrap();
    if storage.is_none() {
        *storage = Some(HashMap::new());
    }
}

/// Gera um novo ID único
fn next_id() -> u64 {
    let mut id = NEXT_ID.lock().unwrap();
    let current = *id;
    *id += 1;
    current
}

/// Insere um componente no armazenamento global e retorna seu ID
fn store_component(comp: RustComponent) -> u64 {
    init_storage();
    let id = next_id();
    let mut storage = COMPONENTS.lock().unwrap();
    if let Some(ref mut map) = *storage {
        map.insert(id, comp);
    }
    id
}

/// Executa uma operação no componente pelo ID
fn with_component<F, R>(id: u64, f: F) -> Option<R>
where
    F: FnOnce(&mut RustComponent) -> R,
{
    let mut storage = COMPONENTS.lock().unwrap();
    if let Some(ref mut map) = *storage {
        if let Some(comp) = map.get_mut(&id) {
            return Some(f(comp));
        }
    }
    None
}

/// Wrapper PyClass LEVE - só guarda o ID do componente
/// O componente real fica no armazenamento global Rust
#[pyclass]
pub struct Component {
    handle: u64,
    component_id: String,
}

#[pymethods]
impl Component {
    /// Atualiza sinais com novos valores e estabiliza
    fn update_signals(&self, new_values: HashMap<String, String>) -> PyResult<()> {
        with_component(self.handle, |comp| {
            comp.update_signals(new_values)
        })
        .ok_or_else(|| PyRuntimeError::new_err("Component not found"))?
        .map_err(|e| PyRuntimeError::new_err(e))
    }

    /// Retorna todos os valores como dicionário
    fn get_values(&self) -> PyResult<HashMap<String, String>> {
        with_component(self.handle, |comp| comp.get_values())
            .ok_or_else(|| PyRuntimeError::new_err("Component not found"))
    }

    /// Atualiza e retorna valores em uma chamada
    fn update_and_get(&self, new_values: HashMap<String, String>) -> PyResult<HashMap<String, String>> {
        with_component(self.handle, |comp| {
            let result = comp.update_signals(new_values);
            (result, comp.get_values())
        })
        .ok_or_else(|| PyRuntimeError::new_err("Component not found"))
        .and_then(|(result, values)| {
            result.map_err(|e| PyRuntimeError::new_err(e))?;
            Ok(values)
        })
    }

    /// Propriedade busses - retorna Dict[str, str] com valores
    #[getter]
    fn get_busses(&self) -> PyResult<HashMap<String, String>> {
        self.get_values()
    }

    /// Propriedade id_
    #[getter]
    fn get_id_(&self) -> String {
        self.component_id.clone()
    }

    /// Representação string do componente
    fn __str__(&self) -> PyResult<String> {
        with_component(self.handle, |comp| format!("{}", comp))
            .ok_or_else(|| PyRuntimeError::new_err("Component not found"))
    }

    fn __repr__(&self) -> PyResult<String> {
        self.__str__()
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
        let mut inner = RustRenderer::new_empty(ir);
        match inner.render() {
            Ok(component) => {
                inner.component = Some(component);
                Ok(Renderer { inner })
            },
            Err(e) => Err(PyRuntimeError::new_err(format!("Failed to render circuit: {}", e)))
        }
    }

    /// Obtém o componente renderizado - move para armazenamento global
    #[getter]
    fn get_component(&mut self) -> PyResult<Component> {
        match self.inner.component.take() {
            Some(comp) => {
                let component_id = comp.id.clone();
                let handle = store_component(comp);
                Ok(Component { handle, component_id })
            },
            None => Err(PyRuntimeError::new_err("Component not available or already taken"))
        }
    }

    fn __str__(&self) -> String {
        format!("Renderer with IR length: {}", self.inner.ir.len())
    }

    fn __repr__(&self) -> String {
        self.__str__()
    }
}

/// Módulo Python
#[pymodule]
fn core(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Component>()?;
    m.add_class::<Renderer>()?;
    m.add("__version__", "0.5.0")?;
    Ok(())
}
