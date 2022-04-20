from numbers import Real
from typing import Union
from .ast import Value, Variable, Negation, Sum, Difference, Product, Quotient, Constraint, And, Or, Equal, Unequal, LessThan, LessThanEqual, GreaterThan, GreaterThanEqual
import z3

def to_z3(value: Union[Constraint, Value, Real]):
    if isinstance(value, Real):
        return z3.RealVal(value)
    elif isinstance(value, Variable):
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
    elif isinstance(value, Or):
        return z3.Or([to_z3(c) for c in value.constraints])
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
    else:
        raise TypeError(f"Unknown type {type(value)}")