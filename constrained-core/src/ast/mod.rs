pub use self::expression::Expression;

pub mod expression;

#[derive(Debug)]
pub struct Ast {
    pub(crate) vars: Vec<Var>,
    pub(crate) constraints: Vec<Constraint>,
    next_anonymous: u32,
}

impl Ast {
    pub fn create_var(&mut self, name: String, expression: Expression) -> VarId {
        self.add_var(Var {
            name: VarName::Named(name),
            expression,
        })
    }

    pub fn create_anonymous(&mut self, expression: Expression) -> VarId {
        self.next_anonymous += 1;
        self.add_var(Var {
            name: VarName::Anonymous(self.next_anonymous - 1),
            expression,
        })
    }

    pub fn add_constrained(&mut self, constraint: Constraint) {
        self.constraints.push(constraint);
    }

    fn add_var(&mut self, var: Var) -> VarId {
        let id = VarId(self.vars.len());
        self.vars.push(var);
        id
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct VarId(usize);

impl VarId {
    pub(crate) fn index(self) -> usize {
        self.0
    }
}

#[derive(Debug)]
pub(crate) enum VarName {
    Named(String),
    Anonymous(u32),
}

#[derive(Debug)]
pub enum Constraint {
    Or(Box<Constraint>, Box<Constraint>),
    Equal(Expression, Expression),
    Less(Expression, Expression),
    LessEqual(Expression, Expression),
    Greater(Expression),
    GreaterEqual(Expression),
}

#[derive(Debug)]
pub(crate) struct Var {
    pub name: VarName,
    pub expression: Expression,
}
