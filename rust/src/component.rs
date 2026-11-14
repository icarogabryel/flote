use std::collections::HashMap;

use crate::buses::BitBus;

#[derive(Debug, Clone)]
pub struct Component {
    pub id: String,
    pub buses: HashMap<String, BitBus>,
}
