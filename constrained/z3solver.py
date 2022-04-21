from numbers import Real
from typing import Union
from .ast import Value, Var, Negation, Sum, Difference, Product, Quotient, Constraint, Equal, Unequal, LessThan, LessThanEqual, GreaterThan, GreaterThanEqual, Min, Max
import z3

def to_z3(value: Union[Constraint, Value, Real]):
    if isinstance(value, bool):
        return value
    elif isinstance(value, Real):
        return z3.RealVal(value)
    elif isinstance(value, Var):
        return z3.Real(value.name)
    elif isinstance(value, Negation):
        return -to_z3(value.value)
    elif isinstance(value, Sum):
        return to_z3(value.lhs) + to_z3(value.rhs)
    elif isinstance(value, Difference):
        return to_z3(value.lhs) - to_z3(value.rhs)
    elif isinstance(value, Product):
        return to_z3(value.lhs) * to_z3(value.rhs)
    elif isinstance(value, Quotient):
        return to_z3(value.lhs) / to_z3(value.rhs)
    elif isinstance(value, Equal):
        return to_z3(value.lhs) == to_z3(value.rhs)
    elif isinstance(value, Unequal):
        return to_z3(value.lhs) != to_z3(value.rhs)
    elif isinstance(value, LessThan):
        return to_z3(value.lhs) < to_z3(value.rhs)
    elif isinstance(value, GreaterThan):
        return to_z3(value.lhs) > to_z3(value.rhs)
    elif isinstance(value, LessThanEqual):
        return to_z3(value.lhs) <= to_z3(value.rhs)
    elif isinstance(value, GreaterThanEqual):
        return to_z3(value.lhs) >= to_z3(value.rhs)
    elif isinstance(value, Min):
        lhs = to_z3(value.lhs)
        rhss = [to_z3(rhs) for rhs in value.values]
        constraints = [lhs <= rhs for rhs in rhss]
        constraints.append(z3.Or([lhs == rhs for rhs in rhss]))
        return constraints
    elif isinstance(value, Max):
        lhs = to_z3(value.lhs)
        rhss = [to_z3(rhs) for rhs in value.values]
        constraints = [lhs >= rhs for rhs in rhss]
        constraints.append(z3.Or([lhs == rhs for rhs in rhss]))
        return constraints
    else:
        raise TypeError(f"Unknown type {type(value)}")