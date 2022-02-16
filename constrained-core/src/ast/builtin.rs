use super::object::{Attribute, PrimitiveType, Type, TypeContext};

pub fn register_builtins(type_ctx: &mut TypeContext) {}

fn register_rect(type_ctx: &mut TypeContext) {
    type_ctx.register(Type::new(
        "Rect".to_string(),
        vec![Attribute::new(
            "top_left".to_string(),
            PrimitiveType::Vector,
        )],
        Box::new(|rect| vec![]),
        Box::new(|rect, vars, painter| {}),
    ))
}
