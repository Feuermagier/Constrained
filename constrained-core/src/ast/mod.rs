use std::collections::HashMap;

use crate::paint::Painter;

pub use self::expression::Expression;
use self::object::Object;

pub mod builtin;
pub mod expression;
pub mod object;

pub struct VariableEnvironment {
    vars: Vec<Var>,
}

impl VariableEnvironment {
    pub fn create_var(&mut self, name: String) -> VarId {
        let id = VarId(self.vars.len());
        self.vars.push(Var { name });
        id
    }
}

pub struct SolvedVars {
    values: Vec<f32>,
}

impl SolvedVars {
    pub fn from_var_env(env: &VariableEnvironment) -> Self {
        Self {
            values: vec![0.0; env.vars.len()],
        }
    }

    pub(crate) fn assign_value(&mut self, id: VarId, value: f32) {
        self.values[id.index()] = value;
    }

    pub fn get_value(&self, id: VarId) -> f32 {
        self.values[id.index()]
    }
}

#[derive(Debug)]
pub struct ConstrainedAst {
    pub(crate) vars: Vec<Var>,
    pub(crate) constraints: Vec<Constraint>,
}

impl ConstrainedAst {
    pub fn new() -> Self {
        Self {
            vars: Vec::new(),
            constraints: Vec::new(),
        }
    }

    pub fn create_var(&mut self, name: String) -> VarId {
        let id = VarId(self.vars.len());
        self.vars.push(Var { name });
        id
    }

    pub fn add_constraint(&mut self, constraint: Constraint) {
        self.constraints.push(constraint);
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct VarId(usize);

impl VarId {
    pub(crate) fn index(self) -> usize {
        self.0
    }

    /// Make sure that the index is valid!
    pub(crate) fn from_index(index: usize) -> Self {
        Self(index)
    }
}

#[derive(Debug)]
pub enum Constraint {
    Or(Box<Constraint>, Box<Constraint>),
    Equal(Expression, Expression),
    Less(Expression, Expression),
    LessEqual(Expression, Expression),
    Greater(Expression, Expression),
    GreaterEqual(Expression, Expression),
}

#[derive(Debug)]
pub(crate) struct Var {
    pub name: String,
}
