from numbers import Real
from typing import Union

from constrained.core import Solution, SolverError
from constrained.diff.autograd import AutogradConstant, AutogradVar, minimum, maximum
from ..ast import Value, Var, Negation, Sum, Difference, Product, Quotient, Constraint, Equal, LessThan, LessThanEqual, GreaterThan, GreaterThanEqual, Min, Max


def _create_graph(value: Union[Value, Real]):
    if isinstance(value, Real):
        return AutogradConstant(value)
    elif isinstance(value, Value):
        if hasattr(value, "_autograd_var"):
            return value._autograd_var
        elif isinstance(value, Var):
            var = AutogradVar(0)
        elif isinstance(value, Negation):
            var = -_create_graph(value.value)
        elif isinstance(value, Sum):
            var = _create_graph(value.lhs) + _create_graph(value.rhs)
        elif isinstance(value, Difference):
            var = _create_graph(value.lhs) - _create_graph(value.rhs)
        elif isinstance(value, Product):
            var = _create_graph(value.lhs) * _create_graph(value.rhs)
        elif isinstance(value, Quotient):
            var = _create_graph(value.lhs) / _create_graph(value.rhs)
        else:
            raise TypeError(f"Unknown type {type(value)} for a value")

        value._autograd_var = var
        return var
    else:
        raise TypeError(f"Unknown type {type(value)} for a value")

def _constraint_to_loss(value: Union[Constraint, Value, Real]):
    if isinstance(value, bool):
        if not value:
            raise ValueError("Constraint is always false")
    elif isinstance(value, Equal):
        return equals_loss(_create_graph(value.lhs), _create_graph(value.rhs))
    elif isinstance(value, LessThan):
        return less_than_loss(_create_graph(value.lhs), _create_graph(value.rhs))
    elif isinstance(value, GreaterThan):
        return less_than_loss(_create_graph(value.rhs), _create_graph(value.lhs))
    elif isinstance(value, LessThanEqual):
        return less_than_loss(_create_graph(value.lhs), _create_graph(value.rhs))
    elif isinstance(value, GreaterThanEqual):
        return less_than_loss(_create_graph(value.rhs), _create_graph(value.lhs))
    elif isinstance(value, Min):
        lhs = _create_graph(value.lhs)
        rhss = [_create_graph(rhs) for rhs in value.values]
        return equals_loss(lhs, minimum(rhss))
    elif isinstance(value, Max):
        lhs = _create_graph(value.lhs)
        rhss = [_create_graph(rhs) for rhs in value.values]
        return equals_loss(lhs, maximum(rhss))
    else:
        raise TypeError(f"Unknown type {type(value)} for a constraint")

def solve_with_gradient_descent(canvas, step_size=0.05, steps=10000, step_callback=None, delta=0.01, patience=50):
    constraints = []
    for constraint in canvas.root.constraints:
        if constraint is False:
            raise ValueError("Unsolvable: Constraints contain explicit 'false'")
        elif constraint is not True:
            constraints.append(constraint)

    loss = sum([_constraint_to_loss(constraint) for constraint in constraints])

    last_loss = float("inf")
    stop_counter = 0
    for i in range(steps):
        step_loss = loss.forward()
        loss.backward()
        loss.step(step_size)
        if step_callback is not None:
            step_callback(i, step_loss, GradientDescentSolution())
        
        if step_loss > last_loss - delta:
            stop_counter += 1
        else:
            stop_counter = 0
        if stop_counter >= patience:
            break
        last_loss = step_loss

    return GradientDescentSolution()

def less_than_loss(lhs, rhs):
    return maximum([lhs - rhs, 0])

def equals_loss(lhs, rhs):
    return (lhs - rhs)**2

class GradientDescentSolution(Solution):
    def __init__(self):
        super().__init__()

    def value_of(self, var):
        return _create_graph(var).forward()