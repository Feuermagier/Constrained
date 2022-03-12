use std::collections::HashMap;

use crate::ast::{ConstrainedAst, Expression, VarId, Constraint};

use self::lexer::{Token, Lexer, LexerError};

mod lexer;

pub type ParserResult = Result<(), ParserError>;

pub fn parse(file: &str) -> Result<ConstrainedAst, ParserError> {
    let mut lexer = Lexer::new(file)?;
    let mut ast = ConstrainedAst::new();
    
    block(&mut lexer, &mut ast)?;

    Ok(ast)

}

fn block(lexer: &mut Lexer, ast: &mut ConstrainedAst) -> ParserResult {
    println!("Block");
    let mut names = HashMap::new();
    loop {
        statement(lexer, ast, &mut names)?;
        println!("{:?}", lexer.peek());
        if *lexer.peek()? != Token::Newline {
            break;
        }
        lexer.expect(Token::Newline)?;
    }
    Ok(())
}

fn statement(lexer: &mut Lexer, ast: &mut ConstrainedAst, names: &mut HashMap<String, VarId>) -> ParserResult {
    println!("Statement");
    match lexer.peek()? {
        Token::Hashtag => {
            // Comment
            println!("Comment");
            while *lexer.peek()? != Token::Newline {
                lexer.next()?;
            }
            Ok(())
        }
        Token::Semicolon => Ok(()),
        Token::Var => {
            let (name, expression) = var_statement(lexer, names)?;
            let id = ast.create_var(name.clone());
            names.insert(name, id);
            Ok(())
        },
        _ => {
            let constraint = constraint_statement(lexer, names)?;
            ast.add_constraint(constraint);
            Ok(())
        }
    }
}

fn var_statement(lexer: &mut Lexer, names: &mut HashMap<String, VarId>) -> Result<(String, Option<Expression>), ParserError> {
    println!("Var statement");
    lexer.expect(Token::Var)?;
    let name = lexer.expect_identifier()?;
    let expression = if *lexer.peek()? == Token::Equals {
        lexer.expect(Token::Equals)?;
        Some(expression(lexer, names)?)
    } else {
        None
    };
    Ok((name, expression))
}

fn constraint_statement(lexer: &mut Lexer, names: &HashMap<String, VarId>) -> Result<Constraint, ParserError> {
    println!("constraint statement");
    let lhs = expression(lexer, names)?;
    let token = lexer.peek()?;
    match token {
        Token::Equals => {
            lexer.expect(Token::Equals)?;
            let rhs = expression(lexer, names)?;
            Ok(Constraint::Equal(lhs, rhs))
        }
        _ => Err(ParserError::UnexpectedToken(token.clone()))
    }
}

fn expression(lexer: &mut Lexer, names: &HashMap<String, VarId>) -> Result<Expression, ParserError> {
    println!("Expression");
    let lhs = factor(lexer, names)?;
    if *lexer.peek()? == Token::Plus {
        lexer.expect(Token::Plus)?;
        let rhs = expression(lexer, names)?;
        Ok(Expression::sum(lhs, rhs))
    } else if *lexer.peek()? == Token::Minus {
        lexer.expect(Token::Minus)?;
        let rhs = expression(lexer, names)?;
        Ok(Expression::difference(lhs, rhs))
    } else {
        Ok(lhs)
    }
}

fn factor(lexer: &mut Lexer, names: &HashMap<String, VarId>) -> Result<Expression, ParserError> {
    let lhs = negated(lexer, names)?;
    if *lexer.peek()? == Token::Mul {
        lexer.expect(Token::Mul)?;
        let rhs = factor(lexer, names)?;
        Ok(Expression::product(lhs, rhs))
    } else if *lexer.peek()? == Token::Div {
        lexer.expect(Token::Div)?;
        let rhs = factor(lexer, names)?;
        Ok(Expression::fraction(lhs, rhs))
    } else {
        Ok(lhs)
    }
}

fn negated(lexer: &mut Lexer, names: &HashMap<String, VarId>) -> Result<Expression, ParserError> {
    if *lexer.peek()? == Token::Minus {
        lexer.expect(Token::Minus)?;
        Ok(Expression::negation(atom(lexer, names)?))
    } else {
        atom(lexer, names)
    }
}

fn atom(lexer: &mut Lexer, names: &HashMap<String, VarId>) -> Result<Expression, ParserError> {
    let token = lexer.next()?;
    match &token {
        Token::LParen => {
            let expr = expression(lexer, names)?;
            lexer.expect(Token::RParen)?;
            Ok(expr)
        }
        Token::Identifier(name) => {
            let id = *names.get(name).ok_or(ParserError::UnknownName(name.clone()))?;
            Ok(Expression::var(id))
        }
        Token::Literal(lit) => {
            Ok(Expression::constant(*lit, 1))
        }
        _ => Err(ParserError::UnexpectedToken(token.clone()))
    }
}

#[derive(Debug, thiserror::Error)]
pub enum ParserError {
    #[error("Unexpected token {0:?}")]
    UnexpectedToken(Token),

    #[error("Unknown name {0}")]
    UnknownName(String),

    #[error(transparent)]
    Lexer(#[from] LexerError),
}