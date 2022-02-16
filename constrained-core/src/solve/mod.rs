pub mod grad_solver;
pub mod z3_solver;

use crate::{SolverStatus, Diagram};

pub trait Solver {
    /// Returns the new loss after this optimization (or 0 if this optimizer has no concept of a loss)
    /// optimize may either solve the entire diagram (i.e. using a SMT solver) or do a 
    /// few steps of the solver (i.e. in case of a gradient descent-based solver)
    fn optimize(&mut self) -> SolverStatus;

    fn diagram(&self) -> &Diagram;
}