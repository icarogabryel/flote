use std::collections::HashMap;

mod buses;
mod component;
pub mod ir;

pub use buses::BitBus;
pub use component::Component;
pub use ir::{
    BinaryOperationDto, BitBusDto, ComponentDto, ConcDto, ConstDto, ExpressionDto, RefDto,
    UnaryOperationDto,
};

use pyo3::prelude::*;

#[pyfunction]
fn render(component_dto: ComponentDto) -> PyResult<()> {
    let mut buses = HashMap::new();

    for bus_dto in component_dto.buses {
        let bus = BitBus {
            id: bus_dto.identifier.clone(),
            assignment: bus_dto.assignment,
            value: bus_dto.value,
            influence_list: bus_dto.influence_list,
            msb_descending: bus_dto.msb_descending,
        };
        buses.insert(bus_dto.identifier, bus);
    }

    let component = Component {
        id: component_dto.id_,
        buses,
    };

    println!("{component:#?}");
    Ok(())
}

#[pymodule]
fn rust_simulation(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(render, m)?)?;
    Ok(())
}
