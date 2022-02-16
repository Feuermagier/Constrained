use crate::primitive::Point;

#[derive(serde::Serialize, serde::Deserialize)]
pub(crate) enum Constraint {
  PointsMatch {
    first: usize,
    second: usize,
    #[serde(rename = "firstPoint")]
    first_point: RectPoint,
    #[serde(rename = "secondPoint")]
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

impl From<Constraint> for constrained_core::Constraint {
  fn from(constraint: Constraint) -> Self {
    match constraint {
      Constraint::PointsMatch {
        first,
        second,
        first_point,
        second_point,
      } => Self::PointsMatch {
        first,
        second,
        first_point: first_point.into(),
        second_point: second_point.into(),
      },
      Constraint::PointFixed {
        rect,
        point,
        target,
      } => Self::PointFixed {
        rect,
        point: point.into(),
        target: target.into(),
      },
      Constraint::WidthFixed { rect, width } => Self::WidthFixed { rect, width },
      Constraint::HeightFixed { rect, height } => Self::HeightFixed { rect, height },
    }
  }
}

#[derive(serde::Serialize, serde::Deserialize)]
pub enum RectPoint {
  TopLeft,
  TopRight,
  BottomLeft,
  BottomRight,
}

impl From<RectPoint> for constrained_core::RectPoint {
  fn from(point: RectPoint) -> Self {
    match point {
      RectPoint::TopLeft => Self::TopLeft,
      RectPoint::TopRight => Self::TopRight,
      RectPoint::BottomLeft => Self::BottomLeft,
      RectPoint::BottomRight => Self::BottomRight,
    }
  }
}
