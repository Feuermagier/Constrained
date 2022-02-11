pub mod solve;
pub mod ast;

#[derive(Debug)]
pub enum Constraint {
    PointsMatch {
        first: usize,
        second: usize,
        first_point: RectPoint,
        second_point: RectPoint,
    },
    PointFixed {
        rect: usize,
        point: RectPoint,
        target: Point,
    },
    WidthFixed {
        rect: usize,
        width: f32,
    },
    HeightFixed {
        rect: usize,
        height: f32,
    },
}

#[derive(Debug, Clone, Copy)]
pub enum RectPoint {
    TopLeft,
    TopRight,
    BottomLeft,
    BottomRight,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Point(pub f32, pub f32);

impl Point {
    pub fn x(self) -> f32 {
        self.0
    }

    pub fn y(self) -> f32 {
        self.1
    }
}

#[derive(Debug)]
pub struct Rect {
    pub top_left: Point,
    pub width: f32,
    pub height: f32,
}

#[derive(Debug)]
pub struct Diagram {
    pub rects: Vec<Rect>,
    pub constraints: Vec<Constraint>
}
pub struct SolverStatus {
    pub loss: f32,
}
