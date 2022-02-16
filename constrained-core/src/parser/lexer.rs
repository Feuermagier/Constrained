use std::ops::Range;

use logos::Logos;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Token {
    LParen,
    RParen,
    Semicolon,
    Var,
    ConstraintEquals,
    Or,
    Plus,
    Minus,
    Mul,
    Div,
    Literal(i32),
    Identifier(String),
    Newline,
    Eof
}

#[derive(Debug, logos::Logos, PartialEq)]
enum LogosToken {
    #[token(";")]
    Semicolon,

    #[token("var")]
    Var,

    #[token("=")]
    ConstraintEquals,

    #[token("(")]
    LParen,

    #[token(")")]
    RParen,

    #[token("|")]
    Or,

    #[token("+")]
    Plus,

    #[token("-")]
    Minus,

    #[token("*")]
    Mul,

    #[token("/")]
    Div,

    #[regex("[0-9]+", |lex| lex.slice().parse())]
    Literal(i32),

    #[regex("[A-z_][A-z0-9_]*", |lex| lex.slice().to_string())]
    Identifier(String),

    #[token("\n")]
    Newline,

    #[error]
    #[regex(r"[ \t]+", logos::skip)]
    Error,
}

pub struct Lexer<'s> {
    lexer: logos::Lexer<'s, LogosToken>,
    next_token: Token
}

impl<'s> Lexer<'s> {
    pub fn new(content: &'s str) -> Result<Self, LexerError> {
        let lexer = LogosToken::lexer(content);
        let mut lexer = Lexer {
            lexer,
            next_token: Token::Eof
        };

        lexer.next()?;
        Ok(lexer)
    }

    pub fn next(&mut self) -> Result<Token, LexerError> {
        let next_token = if let Some(token) = self.lexer.next() {
            match token {
                LogosToken::Semicolon => Token::Semicolon,
                LogosToken::Var => Token::Var,
                LogosToken::ConstraintEquals => Token::ConstraintEquals,
                LogosToken::Or => Token::Or,
                LogosToken::Plus => Token::Plus,
                LogosToken::Minus => Token::Minus,
                LogosToken::Mul => Token::Mul,
                LogosToken::Div => Token::Div,
                LogosToken::Literal(lit) => Token::Literal(lit),
                LogosToken::Identifier(name) => Token::Identifier(name),
                LogosToken::LParen => Token::LParen,
                LogosToken::RParen => Token::RParen,
                LogosToken::Newline => Token::Newline,
                LogosToken::Error => return Err(LexerError::UnexpectedCharacter),
            }
        } else {
            Token::Eof
        };
        Ok(std::mem::replace(&mut self.next_token, next_token))
    }

    pub fn peek(&mut self) -> Result<&Token, LexerError> {
        Ok(&self.next_token)
    }

    pub fn expect(&mut self, token: Token) -> Result<(), LexerError> {
        let span = self.lexer.span();
        let next_token = self.next()?;
        if next_token == token {
            Ok(())
        } else {
            Err(LexerError::UnexpectedToken(token, next_token, span))
        }
    }

    pub fn expect_identifier(&mut self) -> Result<String, LexerError> {
        let span = self.lexer.span();
        let next_token = self.next()?;
        match next_token {
            Token::Identifier(name) => Ok(name),
            _ => Err(LexerError::UnexpectedToken(Token::Identifier(String::new()), next_token, span))
        }
    }
}

#[derive(Debug, thiserror::Error)]
pub enum LexerError {
    #[error("Unexpected character")]
    UnexpectedCharacter,

    #[error("Unexpected token: expected {0:?}, got {:?}")]
    UnexpectedToken(Token, Token, Range<usize>)
}