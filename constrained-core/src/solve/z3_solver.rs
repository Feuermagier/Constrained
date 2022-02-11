use std::ops::{Add, Neg};

use crate::ast::{Ast, Constraint, Expression, Var};

pub fn solve(ast: &Ast) {
    let config = z3::Config::new();
    let ctx = z3::Context::new(&config);

    let vars = ast
        .vars
        .iter()
        .map(|var| match &var.name {
            crate::ast::VarName::Named(name) => z3::ast::Real::new_const(&ctx, name.as_str()),
            crate::ast::VarName::Anonymous(id) => {
                z3::ast::Real::new_const(&ctx, format!("<{}>", *id))
            }
        })
        .collect::<Vec<_>>();
}

fn handle_constraint<'c>(
    constraint: &Constraint,
    ctx: &'c z3::Context,
    vars: &Vec<z3::ast::Real<'c>>,
) {
    match constraint {
        Constraint::Equal(lhs, rhs) => todo!(),
        Constraint::Less(_, _) => todo!(),
        Constraint::LessEqual(_, _) => todo!(),
        Constraint::Greater(_) => todo!(),
        Constraint::GreaterEqual(_) => todo!(),
        Constraint::Or(_, _) => todo!(),
    }
}

fn handle_expression<'c>(
    expression: &Expression,
    ctx: &'c z3::Context,
    vars: &Vec<z3::ast::Float<'c>>,
) -> z3::ast::Float<'c> {
    match expression.ty() {
        crate::ast::expression::ExpressionType::Var(var) => vars[var.index()].clone(),
        crate::ast::expression::ExpressionType::Negation(expr) => {
            handle_expression(expr, ctx, vars).neg()
        }
        crate::ast::expression::ExpressionType::Sum(lhs, rhs) => {
            handle_expression(lhs, ctx, vars).add(handle_expression(rhs, ctx, vars))
        }
        crate::ast::expression::ExpressionType::Difference(lhs, rhs) => {
            handle_expression(lhs, ctx, vars).add(handle_expression(rhs, ctx, vars))
        }
        crate::ast::expression::ExpressionType::Product(lhs, rhs) => todo!(),
        crate::ast::expression::ExpressionType::Fraction(lhs, rhs) => todo!(),
        crate::ast::expression::ExpressionType::Constant(value) => {
            let value = z3::ast::Float::from_f32(ctx, *value);
            z3::ast::Real::
        }
    }
}
