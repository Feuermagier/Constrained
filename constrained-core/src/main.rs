use std::ops::Add;

use constrained_core::{
    solve::{grad_solver::AdamSolver, Solver, z3_solver},
    Constraint, Diagram, Point, Rect, RectPoint,
};
use z3::ast::Ast;
use constrained_core::parser::parse;

fn main() {
    let file = std::fs::read_to_string("diagram.cst").unwrap();
    let ast = parse(&file).unwrap();
    dbg!(&ast);

    let solver = z3_solver::solve(&ast);

    return;

    z3_test();
    return;

    let diagram = Diagram {
        rects: vec![
            Rect {
                top_left: Point(0f32, 0f32),
                width: 1f32,
                height: 1f32,
            },
            Rect {
                top_left: Point(0f32, 0f32),
                width: 1f32,
                height: 1f32,
            },
        ],
        constraints: vec![
            Constraint::PointsMatch {
                first: 0,
                second: 1,
                first_point: RectPoint::BottomRight,
                second_point: RectPoint::TopLeft,
            },
            Constraint::PointFixed {
                rect: 0,
                point: RectPoint::TopLeft,
                target: Point(0f32, 0f32),
            },
            Constraint::WidthFixed {
                rect: 0,
                width: 1f32,
            },
            Constraint::HeightFixed {
                rect: 0,
                height: 1f32,
            },
        ],
    };

    let mut solver = AdamSolver::new(diagram, 3000, 0.01f32);
    let status = solver.optimize();

    println!("Final loss: {}", status.loss);
    render(solver.diagram(), "boxes.svg");
}

fn render(diagram: &Diagram, path: &str) {
    let mut document = svg::Document::new().set("viewBox", (0, 0, 5, 5));
    for rect in &diagram.rects {
        let svg_rect = svg::node::element::Rectangle::new()
            .set("x", rect.top_left.x())
            .set("y", rect.top_left.y())
            .set("width", rect.width)
            .set("height", rect.height);
        document = document.add(svg_rect);
    }
    svg::save(path, &document).unwrap();
}

fn z3_test() {
    let config = z3::Config::new();
    let ctx = z3::Context::new(&config);

    let a = z3::ast::Real::new_const(&ctx, "a");
    let b = z3::ast::Real::new_const(&ctx, "b");

    let solver = z3::Solver::new(&ctx);

    solver.assert(&(&a).add(&b)._eq(&b));
    solver.assert(&(&b)._eq(&z3::ast::Real::from_real(&ctx, 2, 1)));
    dbg!(solver.check());
    dbg!(solver.get_model());
}
