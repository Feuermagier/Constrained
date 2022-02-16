use std::{collections::HashMap, rc::Rc};

use crate::paint::Painter;

use super::{Constraint, SolvedVars, VarId, VariableEnvironment};

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Value {
    Constant(f32),
    Variable(VarId),
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Primitive {
    Number(VarId),
    Vector(VarId, VarId),
}

pub struct Object {
    ty: Rc<Type>,
    attributes: HashMap<String, Primitive>,
}

impl Object {
    pub fn from_type(ty: Rc<Type>, var_env: VariableEnvironment) -> Self {
        let attributes = HashMap::with_capacity(ty.attributes.len());
        for attr in &ty.attributes {
            let value = match attr.ty {
                PrimitiveType::Number => Primitive::Number(var_env.create_var(attr.name.clone())),
                PrimitiveType::Vector => Primitive::Vector(
                    var_env.create_var(attr.name + ".x"),
                    var_env.create_var(attr.name + ".y"),
                ),
            };
            attributes.insert(attr.name.clone(), value);
        }
        Self { ty, attributes }
    }

    pub fn get_attribute(&self, name: &str) -> Result<Primitive, TypeError> {
        self.attributes
            .get(name)
            .copied()
            .ok_or_else(|| TypeError::UnknownAttriute(name.to_string()))
    }
}

pub type TypeConstraintCreator = Box<dyn Fn(&Object) -> Vec<Constraint>>;
pub type TypePainter = Box<dyn Fn(&Object, &SolvedVars, &mut dyn Painter)>;

pub enum PrimitiveType {
    Number,
    Vector,
}

pub struct Attribute {
    name: String,
    ty: PrimitiveType,
}

impl Attribute {
    pub fn new(name: String, ty: PrimitiveType) -> Self {
        Self { name, ty }
    }
}

pub struct Type {
    name: String,
    attributes: Vec<Attribute>,
    constraints: TypeConstraintCreator,
    painter: TypePainter,
}

impl Type {
    pub fn new(
        name: String,
        attributes: Vec<Attribute>,
        constraints: TypeConstraintCreator,
        painter: TypePainter,
    ) -> Self {
        Self {
            name,
            attributes,
            constraints,
            painter,
        }
    }
}

pub struct TypeContext {
    types: HashMap<String, Rc<Type>>,
}

impl TypeContext {
    pub fn new() -> Self {
        Self {
            types: HashMap::new(),
        }
    }

    pub fn register(&mut self, ty: Type) {
        self.types.insert(ty.name.clone(), Rc::new(ty));
    }

    pub fn find_type(&self, name: &str) -> Result<Rc<Type>, TypeError> {
        Ok(Rc::clone(
            self.types
                .get(name)
                .ok_or_else(|| TypeError::UnknownType(name.to_string()))?,
        ))
    }
}

#[derive(Debug, thiserror::Error)]
pub enum TypeError {
    #[error("Unknown type {0}")]
    UnknownType(String),

    #[error("Unknown attribute {0}")]
    UnknownAttriute(String),

    #[error("Attribute {0} is a number, so a vector cannot be assigned to it")]
    AssignedVectorToNumber(String),

    #[error("Attribute {0} is a vector, so a number cannot be assigned to it")]
    AssignedNumberToVector(String),
}
