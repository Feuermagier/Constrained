use autograd::{
    ndarray::array,
    optimizers::{self, Adam},
    prelude::Optimizer,
    tensor_ops,
    variable::{GetVariableTensor, NamespaceTrait, VariableID},
    Context, Tensor, VariableEnvironment,
};

use crate::{solve::Solver, Constraint, Diagram, Point, RectPoint, SolverStatus};

pub struct AdamSolver {
    diagram: Diagram,
    steps_per_optimize: u32,
    target_loss: f32,
    env: VariableEnvironment<'static, f32>,
    opt_rects: Vec<OptRect>,
    optimizer: Adam<f32>,
    cached_loss: f32,
}

impl AdamSolver {
    pub fn new(diagram: Diagram, steps_per_optimize: u32, target_loss: f32) -> Self {
        let mut env = VariableEnvironment::new();

        let mut opt_rects = Vec::new();
        for rect in diagram.rects.iter() {
            // Fix values using a different namespace than the one that is used for var_id_list for Adam
            opt_rects.push(OptRect {
                top_left: env.set(array!(rect.top_left.x(), rect.top_left.y())),
                width: env.set(array![rect.width]),
                height: env.set(array![rect.height]),
            });
        }

        let optimizer = Adam::default("adam", env.default_namespace().current_var_ids(), &mut env);

        Self {
            diagram,
            steps_per_optimize,
            target_loss,
            env,
            opt_rects,
            optimizer,
            cached_loss: f32::INFINITY,
        }
    }
}

impl Solver for AdamSolver {
    fn optimize(&mut self) -> SolverStatus {
        // Do solver steps
        for _ in 0..self.steps_per_optimize {
            if self.cached_loss < self.target_loss {
                break;
            }

            self.env.run(|ctx| {
                self.cached_loss = do_optimizer_step(
                    ctx,
                    &self.opt_rects,
                    &self.diagram.constraints,
                    &self.optimizer,
                );
            });
        }

        // Update the diagram
        self.env.run(|ctx| {
            for (i, opt_rect) in self.opt_rects.iter().enumerate() {
                let rect = &mut self.diagram.rects[i];

                let top_left = ctx.variable(opt_rect.top_left).eval(ctx).unwrap();
                let width = ctx.variable(opt_rect.width).eval(ctx).unwrap();
                let height = ctx.variable(opt_rect.height).eval(ctx).unwrap();
                rect.top_left = Point(top_left[0], top_left[1]);
                rect.width = width[0];
                rect.height = height[0];
            }
        });

        SolverStatus {
            loss: self.cached_loss,
        }
    }

    fn diagram(&self) -> &Diagram {
        &self.diagram
    }
}

fn do_optimizer_step<'c>(
    ctx: &'c Context<f32>,
    opt_rects: &[OptRect],
    constraints: &[Constraint],
    optimizer: &Adam<f32>,
) -> f32 {
    let mut loss = tensor_ops::zeros(&[1], ctx);
    for constraint in constraints {
        match constraint {
            Constraint::PointsMatch {
                first,
                second,
                first_point,
                second_point,
            } => {
                let a = get_point(ctx, &opt_rects, *first, *first_point);
                let b = get_point(ctx, &opt_rects, *second, *second_point);

                loss = loss + tensor_ops::square(a - b).reduce_sum(&[0], false);
            }
            Constraint::PointFixed {
                rect,
                point,
                target,
            } => {
                let current = get_point(ctx, &opt_rects, *rect, *point);
                let target = tensor_ops::convert_to_tensor(array!(target.x(), target.y()), ctx);
                loss = loss + tensor_ops::square(current - target).reduce_sum(&[0], false);
            }
            Constraint::WidthFixed { rect, width } => {
                let rect = &opt_rects[*rect];
                loss = loss
                    + tensor_ops::square(
                        ctx.variable(rect.width)
                            - tensor_ops::convert_to_tensor(array![*width], ctx),
                    );
            }
            Constraint::HeightFixed { rect, height } => {
                let rect = &opt_rects[*rect];
                loss = loss
                    + tensor_ops::square(
                        ctx.variable(rect.height)
                            - tensor_ops::convert_to_tensor(array![*height], ctx),
                    );
            }
        }
    }
    let namespace = ctx.default_namespace();
    let (vars, grads) = optimizers::grad_helper(&[loss], &namespace);

    let update_op = optimizer.get_update_op(&vars, &grads, ctx);
    let results = ctx.evaluator().push(loss).push(update_op).run();

    results[0].as_ref().unwrap()[0]
}

fn get_point<'c>(
    ctx: &'c Context<f32>,
    rects: &[OptRect],
    rect: usize,
    point: RectPoint,
) -> Tensor<'c, f32> {
    let rect = &rects[rect];
    let tl = ctx.variable(rect.top_left);
    match point {
        RectPoint::TopLeft => tl,
        RectPoint::TopRight => {
            tl + autograd::tensor_ops::concat(
                &[
                    ctx.variable(rect.width),
                    tensor_ops::convert_to_tensor(array![0f32], ctx),
                ],
                0,
            )
        }

        RectPoint::BottomLeft => {
            tl + autograd::tensor_ops::concat(
                &[
                    tensor_ops::convert_to_tensor(array![0f32], ctx),
                    ctx.variable(rect.height),
                ],
                0,
            )
        }
        RectPoint::BottomRight => {
            tl + autograd::tensor_ops::concat(
                &[ctx.variable(rect.width), ctx.variable(rect.height)],
                0,
            )
        }
    }
}

#[derive(Debug)]
struct OptRect {
    top_left: VariableID,
    width: VariableID,
    height: VariableID,
}
