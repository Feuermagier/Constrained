
from abc import ABC
from typing import List, Union
import numbers


def _check_and_replace_value(value):
    if not isinstance(value, Value) and not isinstance(value, numbers.Real):
        raise TypeError(f"{value} is neither a Value nor a valid numeric type")

    if isinstance(value, VarPlaceholder):
        raise ValueError(
            f"{value} is a placeholder (e.g. 'ast.VarPlaceholder()') and can therefore not be used in a constraint. You can create a fresh ast.Var using ast.var(<x>)")
    else:
        return value


def _check_and_replace_constraint(value):
    if not isinstance(value, Constraint):
        raise TypeError(f"{value} is not a Constraint")

    return value

############################# Values #############################

def var(x):
    if isinstance(x, numbers.Real):
        return x
    elif isinstance(x, VarPlaceholder):
        return Var()
    elif isinstance(x, Value):
        return x
    else:
        raise TypeError(f"{type(x)} cannot be converted to Var")

class Value(ABC):
    def __neg__(self):
        return Negation(self)

    def __add__(self, other):
        return Sum(self, other)

    def __radd__(self, other):
        return Sum(other, self)

    def __sub__(self, other):
        return Difference(self, other)

    def __rsub__(self, other):
        return Difference(other, self)

    def __mul__(self, other):
        return Product(self, other)

    def __rmul__(self, other):
        return Product(other, self)

    def __truediv__(self, other):
        return Quotient(self, other)

    def __rtruediv__(self, other):
        return Quotient(other, self)

    def __eq__(self, other):
        return Equal(self, other)

    def __ne__(self, other):
        return Unequal(self, other)

    def __lt__(self, other):
        return LessThan(self, other)

    def __le__(self, other):
        return LessThanEqual(self, other)

    def __gt__(self, other):
        return GreaterThan(self, other)

    def __ge__(self, other):
        return GreaterThanEqual(self, other)

    def __repr__(self):
        return str(self)


class Var(Value):
    _var_counter = 0

    def __init__(self, name=None):
        self.id = Var._var_counter
        Var._var_counter += 1
        if name is None:
            self.name = "$" + str(self.id)
        else:
            self.name = name

    def __str__(self):
        return str(self.name)

    def __eq__(self, other):
        if not isinstance(other, Var):
            raise TypeError(f"Cannot compare a Var and a {type(other)}")


class VarPlaceholder(Value):
    def __init__(self):
        super().__init__()

class Negation(Value):
    def __init__(self, value: Value):
        super().__init__()
        self.value = _check_and_replace_value(value)

    def __str__(self):
        return "-" + str(self.value)


class BinaryOp(Value):
    def __init__(self, lhs: Value, rhs: Value):
        super().__init__()
        self.lhs = _check_and_replace_value(lhs)
        self.rhs = _check_and_replace_value(rhs)


class Sum(BinaryOp):
    def __init__(self, lhs: Value, rhs: Value):
        super().__init__(lhs, rhs)

    def __str__(self):
        return f"{self.lhs} + {self.rhs}"


class Difference(BinaryOp):
    def __init__(self, lhs: Value, rhs: Value):
        super().__init__(lhs, rhs)

    def __str__(self):
        return f"{self.lhs} - {self.rhs}"


class Product(BinaryOp):
    def __init__(self, lhs: Value, rhs: Value):
        super().__init__(lhs, rhs)

    def __str__(self):
        return f"({self.lhs}) * ({self.rhs})"


class Quotient(BinaryOp):
    def __init__(self, lhs: Value, rhs: Value):
        super().__init__(lhs, rhs)

    def __str__(self):
        return f"({self.lhs}) / ({self.rhs})"


class Equality(BinaryOp):
    def __init__(self, lhs: Value, rhs: Value):
        super().__init__(lhs, rhs)

    def __str__(self):
        return f"({self.lhs}) / ({self.rhs})"

############################# Constraints #############################


class Constraint:
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return str(self)


class BinaryPrimitiveConstraint(Constraint):
    def __init__(self, lhs: 'Value', rhs: 'Value'):
        self.lhs = _check_and_replace_value(lhs)
        self.rhs = _check_and_replace_value(rhs)


class Equal(BinaryPrimitiveConstraint):
    def __init__(self, lhs: 'Value', rhs: 'Value'):
        super().__init__(lhs, rhs)

    def __str__(self):
        return str(self.lhs) + " == " + str(self.rhs)


class Unequal(BinaryPrimitiveConstraint):
    def __init__(self, lhs: 'Value', rhs: 'Value'):
        super().__init__(lhs, rhs)

    def __str__(self):
        return str(self.lhs) + " != " + str(self.rhs)


class LessThan(BinaryPrimitiveConstraint):
    def __init__(self, lhs: 'Value', rhs: 'Value'):
        super().__init__(lhs, rhs)

    def __str__(self):
        return str(self.lhs) + " < " + str(self.rhs)


class LessThanEqual(BinaryPrimitiveConstraint):
    def __init__(self, lhs: 'Value', rhs: 'Value'):
        super().__init__(lhs, rhs)

    def __str__(self):
        return str(self.lhs) + " <= " + str(self.rhs)


class GreaterThan(BinaryPrimitiveConstraint):
    def __init__(self, lhs: 'Value', rhs: 'Value'):
        super().__init__(lhs, rhs)

    def __str__(self):
        return str(self.lhs) + " > " + str(self.rhs)


class GreaterThanEqual(BinaryPrimitiveConstraint):
    def __init__(self, lhs: 'Value', rhs: 'Value'):
        super().__init__(lhs, rhs)

    def __str__(self):
        return str(self.lhs) + " >= " + str(self.rhs)


class FunctionConstraint(Constraint):
    def __init__(self, lhs: 'Value', values: 'list[Value]', name: str):
        super().__init__()
        self.lhs = _check_and_replace_value(lhs)
        self.values = [_check_and_replace_value(value) for value in values]
        self.name = name

    def __str__(self):
        return str(self.lhs) + " = " + self.name + "(" + ", ".join([str(x) for x in self.values]) + ")"


class Min(FunctionConstraint):
    def __init__(self, lhs: 'Value', values: 'list[Value]'):
        super().__init__(lhs, values, "min")


class Max(FunctionConstraint):
    def __init__(self, lhs: 'Value', values: 'list[Value]'):
        super().__init__(lhs, values, "max")

############################# Point #############################

def point(x):
    if isinstance(x, tuple) and len(x) == 2 and isinstance(x[0], numbers.Real) and isinstance(x[1], numbers.Real):
        return Point(x[0], x[1])
    elif isinstance(x, PointPlaceholder):
        return Point()
    elif isinstance(x, Point):
        return x
    else:
        raise TypeError(f"{type(x)} cannot be converted to Point")

class Point:
    def __init__(self, x=VarPlaceholder(), y=VarPlaceholder()):
        self.x, self.y = var(x), var(y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return [self.x == other.x, self.y == other.y]

    def _value(self, solution):
        return solution[self.x], solution[self.y]


class PointPlaceholder:

    def __eq__(self, other):
        if isinstance(other, Point) or isinstance(other, PointPlaceholder):
            raise ValueError(
                "This is a placeholder and can therefore not be used in a constraint. You can create a fresh point usint ast.point(<x>)")
        else:
            raise TypeError(f"Cannot compare to a type(other)")
