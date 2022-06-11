from abc import ABC, abstractmethod
from numbers import Integral, Real
from typing import List

from constrained.ast import Var

def _check_and_replace(value):
    if isinstance(value, Real):
        return AutogradConstant(value)
    elif isinstance(value, AutogradNode):
        return value
    else:
        raise TypeError(f"Invalid type {type(value)}")

def maximum(values):
    values = [_check_and_replace(value) for value in values]
    return AutogradMaximum(values)

def minimum(values):
    values = [_check_and_replace(value) for value in values]
    return AutogradMinimum(values)

class AutogradNode(ABC):
    def __init__(self):
        super().__init__()
        self.value = 0

    @abstractmethod
    def forward(self):
        pass

    @abstractmethod
    def backward(self, dout: float = 1):
        pass

    @abstractmethod
    def step(self, size: Real):
        pass

    def __neg__(self):
        return AutogradNegation(self)

    def __add__(self, other):
        return AutogradSum(self, _check_and_replace(other))

    def __radd__(self, other):
        return AutogradSum(_check_and_replace(other), self)

    def __sub__(self, other):
        return AutogradDifference(self, _check_and_replace(other))

    def __rsub__(self, other):
        return AutogradDifference(_check_and_replace(other), self)

    def __mul__(self, other):
        return AutogradProduct(self, _check_and_replace(other))

    def __rmul__(self, other):
        return AutogradProduct(_check_and_replace(other), self)

    def __truediv__(self, other):
        return AutogradQuotient(self, _check_and_replace(other))

    def __rtruediv__(self, other):
        return AutogradQuotient(_check_and_replace(other), self)

    def __pow__(self, exp):
        return AutogradMonom(self, exp)

class AutogradConstant(AutogradNode):
    def __init__(self, value: Real):
        self.value = value

    def forward(self):
        return self.value

    def backward(self, dout: float = 1):
        pass

    def step(self, size: Real):
        pass

class AutogradVar(AutogradNode):
    def __init__(self, value: Real, clip=10):
        self.value = value
        self.grad = 0
        self.clip = clip

    def forward(self):
        return self.value

    def backward(self, dout: float = 1):
        self.grad += dout

    def step(self, size: Real):
        if self.grad > self.clip:
            self.grad = self.clip
        elif self.grad < -self.clip:
            self.grad = -self.clip
        self.value -= size * self.grad
        self.grad = 0

class AutogradNegation(AutogradNode):
    def __init__(self, target: AutogradNode):
        super().__init__()
        self.target = target

    def forward(self):
        self.value = -self.target.forward()
        return self.value

    def backward(self, dout: float = 1):
        self.target.backward(-dout)

    def step(self, size: Real):
        self.target.step(size)

class AutogradSum(AutogradNode):
    def __init__(self, lhs: AutogradNode, rhs: AutogradNode):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs

    def forward(self):
        self.value = self.lhs.forward() + self.rhs.forward()
        return self.value

    def backward(self, dout: float = 1):
        self.lhs.backward(dout)
        self.rhs.backward(dout)

    def step(self, size: Real):
        self.lhs.step(size)
        self.rhs.step(size)

class AutogradDifference(AutogradNode):
    def __init__(self, lhs: AutogradNode, rhs: AutogradNode):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs

    def forward(self):
        self.value = self.lhs.forward() - self.rhs.forward()
        return self.value

    def backward(self, dout: float = 1):
        self.lhs.backward(dout)
        self.rhs.backward(-dout)

    def step(self, size: Real):
        self.lhs.step(size)
        self.rhs.step(size)

class AutogradProduct(AutogradNode):
    def __init__(self, lhs: AutogradNode, rhs: AutogradNode):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs

    def forward(self):
        self.value = self.lhs.forward() * self.rhs.forward()
        return self.value

    def backward(self, dout: float = 1):
        self.lhs.backward(dout * self.rhs.value)
        self.rhs.backward(dout * self.lhs.value)

    def step(self, size: Real):
        self.lhs.step(size)
        self.rhs.step(size)

class AutogradQuotient(AutogradNode):
    def __init__(self, lhs: AutogradNode, rhs: AutogradNode):
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs

    def forward(self):
        self.value = self.lhs.forward() / self.rhs.forward()
        return self.value

    def backward(self, dout: float = 1):
        self.lhs.backward(dout / self.rhs.value)
        self.rhs.backward(dout * self.lhs.value / self.rhs.value**2)

    def step(self, size: Real):
        self.lhs.step(size)
        self.rhs.step(size)

class AutogradMonom(AutogradNode):
    def __init__(self, target: AutogradNode, exponent: Integral):
        super().__init__()
        if exponent == 0:
            raise ValueError("exponent must not be zero")
        self.target = target
        self.exponent = exponent

    def forward(self):
        self.value = self.target.forward()**self.exponent
        return self.value

    def backward(self, dout: float = 1):
        self.target.backward(dout * self.exponent * self.target.value**(self.exponent - 1))

    def step(self, size: Real):
        self.target.step(size)

class AutogradMinimum(AutogradNode):
    def __init__(self, values: List[AutogradNode]):
        super().__init__()
        if values == []:
            raise ValueError("values must not be empty")
        self.values = values
        self.idx = 0

    def forward(self):
        self.value = float("inf")
        for (i, value) in enumerate(self.values):
            v = value.forward()
            if v < self.value:
                self.value = v
                self.idx = i
        return self.value

    def backward(self, dout: float = 1):
        self.values[self.idx].backward(dout)

    def step(self, size: Real):
        for value in self.values:
            value.step(size)

class AutogradMaximum(AutogradNode):
    def __init__(self, values: List[AutogradNode]):
        super().__init__()
        if values == []:
            raise ValueError("values must not be empty")
        self.values = values
        self.idx = 0

    def forward(self):
        self.value = float("-inf")
        for (i, value) in enumerate(self.values):
            v = value.forward()
            if v > self.value:
                self.value = v
                self.idx = i
        return self.value

    def backward(self, dout: float = 1):
        self.values[self.idx].backward(dout)

    def step(self, size: Real):
        for value in self.values:
            value.step(size)