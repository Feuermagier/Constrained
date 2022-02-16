use crate::ast::{ConstrainedAst, VarId};

pub struct VarValues {
    values: Vec<f32>
}

impl VarValues {
    pub fn from_ast(ast: &ConstrainedAst) -> Self {
        Self {
            values: vec![0.0; ast.vars.len()],
        }
    }

    pub(crate) fn assign_value(&mut self, id: VarId, value: f32) {
        self.values[id.index()] = value;
    }

    pub fn get_value(&self, id: VarId) -> f32 {
        self.values[id.index()]
    }
}