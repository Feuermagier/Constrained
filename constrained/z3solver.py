from numbers import Real
from typing import Union

from constrained.core import Solution, SolverError
from .ast import ConstraintVisitor, Value, ValueVisitor, Var, Negation, Sum, Difference, Product, Quotient, Constraint, Equal, LessThan, LessThanEqual, GreaterThan, GreaterThanEqual, Min, Max
import z3

class Z3ValueVisitor(ValueVisitor):
    def visit_real(self, value: Real):
        return z3.RealVal(value)

    def visit_var(self, value: Var):
        if hasattr(value, "_z3_var"):
            return value._z3_var
        else:
            return z3.Real(value.id)
    
    def visit_negation(self, value: Negation):
        return -self.dispatch(value.value)

    def visit_sum(self, value: Sum):
        return self.dispatch(value.lhs) + self.dispatch(value.rhs)

    def visit_difference(self, value: Difference):
        return self.dispatch(value.lhs) - self.dispatch(value.rhs)

    def visit_product(self, value: Product):
        return self.dispatch(value.lhs) * self.dispatch(value.rhs)

    def visit_quotient(self, value: Quotient):
        return self.dispatch(value.lhs) / self.dispatch(value.rhs)

class Z3ConstraintVisitor(ConstraintVisitor):
    def visit_equal(self, constraint: Equal):
        return 

def _value_to_z3(value: Union[Value, Real]):
    if isinstance(value, Real):
        return z3.RealVal(value)
    elif isinstance(value, Value):
        if hasattr(value, "_z3_var"):
            return value._z3_var
        if isinstance(value, Var):
            var = z3.Real(value.id)
        elif isinstance(value, Negation):
            var = -_value_to_z3(value.value)
        elif isinstance(value, Sum):
            var = _value_to_z3(value.lhs) + _value_to_z3(value.rhs)
        elif isinstance(value, Difference):
            var = _value_to_z3(value.lhs) - _value_to_z3(value.rhs)
        elif isinstance(value, Product):
            var = _value_to_z3(value.lhs) * _value_to_z3(value.rhs)
        elif isinstance(value, Quotient):
            var = _value_to_z3(value.lhs) / _value_to_z3(value.rhs)
        else:
            raise TypeError(f"Unknown type {type(value)} for a value")

        value._z3_var = var
        return var
    else:
        raise TypeError(f"Unknown type {type(value)} for a value")

def _constraint_to_z3(value: Union[Constraint, Value, Real]):
    if isinstance(value, bool):
        return [value]
    elif isinstance(value, Equal):
        return [_value_to_z3(value.lhs) == _value_to_z3(value.rhs)]
    elif isinstance(value, LessThan):
        return [_value_to_z3(value.lhs) < _value_to_z3(value.rhs)]
    elif isinstance(value, GreaterThan):
        return [_value_to_z3(value.lhs) > _value_to_z3(value.rhs)]
    elif isinstance(value, LessThanEqual):
        return [_value_to_z3(value.lhs) <= _value_to_z3(value.rhs)]
    elif isinstance(value, GreaterThanEqual):
        return [_value_to_z3(value.lhs) >= _value_to_z3(value.rhs)]
    elif isinstance(value, Min):
        lhs = _value_to_z3(value.lhs)
        rhss = [_value_to_z3(rhs) for rhs in value.values]
        constraints = [lhs <= rhs for rhs in rhss]
        constraints.append(z3.Or([lhs == rhs for rhs in rhss]))
        return constraints
    elif isinstance(value, Max):
        lhs = _value_to_z3(value.lhs)
        rhss = [_value_to_z3(rhs) for rhs in value.values]
        constraints = [lhs >= rhs for rhs in rhss]
        constraints.append(z3.Or([lhs == rhs for rhs in rhss]))
        return constraints
    else:
        raise TypeError(f"Unknown type {type(value)} for a constraint")

def solve_with_z3(canvas):
    solver = z3.Solver()
    constraints = []
    for c in canvas.root.constraints:
        if c is not True:
            constraints.extend(_constraint_to_z3(c))
            
    solver.add(constraints)

    if solver.check() != z3.sat:
        raise SolverError(f"Z3 wasn't able to solve the canvas. Reason: {solver.check()}. Check your constraints and try again.")

    print(f"Solved {len(canvas.root.constraints)} constraints in {solver.statistics().time}s")

    model = solver.model()
    return Z3Solution(model)

class Z3Solution(Solution):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def value_of(self, var):
        return _value_of_z3(_value_to_z3(var), self.model)
        

def _value_of_z3(value, model):
    if isinstance(value, z3.RatNumRef):
        return float(value.numerator_as_long()) / float(value.denominator_as_long())
    elif isinstance(value, z3.AlgebraicNumRef):
        return value.approx(20)
    elif isinstance(value, z3.ArithRef):
        return _value_of_z3(model.evaluate(value), model)