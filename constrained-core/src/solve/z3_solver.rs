use std::ops::{Add, Div, Mul, Neg, Sub};

use crate::{ast::{ConstrainedAst, Constraint, Expression, VarId}, diagram::VarValues};

pub fn solve(ast: &ConstrainedAst) -> Result<VarValues, Z3SolverError> {
    let config = z3::Config::new();
    let ctx = z3::Context::new(&config);

    let vars = ast
        .vars
        .iter()
        .map(|var| z3::ast::Real::new_const(&ctx, var.name.as_str()))
        .collect::<Vec<_>>();

    let solver = z3::Solver::new(&ctx);

    for constraint in &ast.constraints {
        solver.assert(&handle_constraint(constraint, &ctx, &vars));
    }

    if solver.check() != z3::SatResult::Sat {
        return Err(Z3SolverError::NotSolvable);
    }

    let values = if let Some(model) = solver.get_model() {
        let mut values = VarValues::from_ast(ast);
        for (i, var) in vars.iter().enumerate() {
            let val = model.eval(var, false).unwrap();
            values.assign_value(VarId::from_index(i), real_to_f32(&ctx, &val))
        }
        Ok(values)
    } else {
        Err(Z3SolverError::NotSolvable)
    };

    values
}

fn handle_constraint<'c>(
    constraint: &Constraint,
    ctx: &'c z3::Context,
    vars: &Vec<z3::ast::Real<'c>>,
) -> z3::ast::Bool<'c> {
    match constraint {
        Constraint::Equal(lhs, rhs) => z3::ast::Ast::_eq(
            &handle_expression(lhs, ctx, vars),
            &handle_expression(rhs, ctx, vars),
        ),
        Constraint::Less(lhs, rhs) => {
            handle_expression(lhs, ctx, vars).lt(&handle_expression(rhs, ctx, vars))
        }
        Constraint::LessEqual(lhs, rhs) => {
            handle_expression(lhs, ctx, vars).le(&handle_expression(rhs, ctx, vars))
        }
        Constraint::Greater(lhs, rhs) => {
            handle_expression(lhs, ctx, vars).gt(&handle_expression(rhs, ctx, vars))
        }
        Constraint::GreaterEqual(lhs, rhs) => {
            handle_expression(lhs, ctx, vars).ge(&handle_expression(rhs, ctx, vars))
        }
        Constraint::Or(lhs, rhs) => z3::ast::Bool::or(
            ctx,
            &[
                &handle_constraint(lhs, ctx, vars),
                &handle_constraint(rhs, ctx, vars),
            ],
        ),
    }
}

fn handle_expression<'c>(
    expression: &Expression,
    ctx: &'c z3::Context,
    vars: &Vec<z3::ast::Real<'c>>,
) -> z3::ast::Real<'c> {
    match expression.ty() {
        crate::ast::expression::ExpressionType::Var(var) => vars[var.index()].clone(),
        crate::ast::expression::ExpressionType::Negation(expr) => {
            handle_expression(expr, ctx, vars).neg()
        }
        crate::ast::expression::ExpressionType::Sum(lhs, rhs) => {
            handle_expression(lhs, ctx, vars).add(handle_expression(rhs, ctx, vars))
        }
        crate::ast::expression::ExpressionType::Difference(lhs, rhs) => {
            handle_expression(lhs, ctx, vars).sub(handle_expression(rhs, ctx, vars))
        }
        crate::ast::expression::ExpressionType::Product(lhs, rhs) => {
            handle_expression(lhs, ctx, vars).mul(handle_expression(rhs, ctx, vars))
        }
        crate::ast::expression::ExpressionType::Fraction(lhs, rhs) => {
            handle_expression(lhs, ctx, vars).div(handle_expression(rhs, ctx, vars))
        }
        crate::ast::expression::ExpressionType::Constant(num, den) => {
            z3::ast::Real::from_real(ctx, *num, *den)
        }
    }
}

fn real_to_f32<'c>(ctx: &'c z3::Context, real: &z3::ast::Real) -> f32 {
    if let Some((num, den)) = real.as_real() {
        num as f32 / den as f32
    } else {
        real_to_f32(ctx, &real.approx(ctx, 10))
        /*
        let string = real.decimal_string(ctx, 10);
        string
            .replace("?", "")
            .parse()
            .expect(&format!("Unable to parse value '{}' of Z3 real", string))
            */
    }
}

#[derive(Debug, thiserror::Error)]
pub enum Z3SolverError {
    #[error("The diagram cannot be solved :(")]
    NotSolvable
}