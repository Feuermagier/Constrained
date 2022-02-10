#[derive(serde::Serialize, serde::Deserialize, Clone, Copy)]
pub(crate) struct Point {
  x: f32,
  y: f32,
}

impl From<Point> for constrained_core::Point {
  fn from(point: Point) -> Self {
    Self(point.x, point.y)
  }
}

impl From<constrained_core::Point> for Point {
  fn from(point: constrained_core::Point) -> Self {
    Self {
      x: point.x(),
      y: point.y(),
    }
  }
}

#[derive(serde::Serialize, serde::Deserialize)]
pub(crate) struct Rect {
  #[serde(rename = "topLeft")]
  top_left: Point,
  width: f32,
  height: f32,
}

impl From<Rect> for constrained_core::Rect {
  fn from(rect: Rect) -> Self {
    Self {
      top_left: rect.top_left.into(),
      width: rect.width,
      height: rect.height,
    }
  }
}

impl From<&constrained_core::Rect> for Rect {
  fn from(rect: &constrained_core::Rect) -> Self {
    Self {
      top_left: rect.top_left.into(),
      width: rect.width,
      height: rect.height,
    }
  }
}
