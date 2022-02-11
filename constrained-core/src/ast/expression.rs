use std::ops::{Add, Sub, Mul, Div, Neg};

use super::VarId;

#[derive(Debug)]
pub struct Expression(Box<ExpressionType>);

impl Expression {
    pub fn var(id: VarId) -> Self {
        Self(Box::new(ExpressionType::Var(id)))
    }

    pub fn constant(value: f32) -> Self {
        Self(Box::new(ExpressionType::Constant(value)))
    }

    pub(crate) fn ty(&self) -> &ExpressionType {
        &self.0
    }
}

impl Neg for Expression {
    type Output = Expression;

    fn neg(self) -> Self::Output {
        Self(Box::new(ExpressionType::Negation(self)))
    }
}

impl Add<Expression> for Expression {
    type Output = Expression;

    fn add(self, rhs: Expression) -> Self::Output {
        Self(Box::new(ExpressionType::Sum(self, rhs)))
    }
}

impl Sub<Expression> for Expression {
    type Output = Expression;

    fn sub(self, rhs: Expression) -> Self::Output {
        Self(Box::new(ExpressionType::Difference(self, rhs)))
    }
}

impl Mul<Expression> for Expression {
    type Output = Expression;

    fn mul(self, rhs: Expression) -> Self::Output {
        Self(Box::new(ExpressionType::Product(self, rhs)))
    }
}

impl Div<Expression> for Expression {
    type Output = Expression;

    fn div(self, rhs: Expression) -> Self::Output {
        Self(Box::new(ExpressionType::Fraction(self, rhs)))
    }
}

#[derive(Debug)]
pub(crate) enum ExpressionType {
    Var(VarId),
    Negation(Expression),
    Sum(Expression,Expression),
    Difference(Expression,Expression),
    Product(Expression,Expression),
    Fraction(Expression,Expression),
    Constant(f32),
}