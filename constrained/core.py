from abc import ABC, abstractmethod
from io import BytesIO
from numbers import Real

from .ast import Value, Var, VarPlaceholder, Point, PointPlaceholder, var, point

from functools import wraps

global var_counter
var_counter = 0

"""
def num(value):
    global var_counter

    if value is None:
        value = z3.Real(var_counter)
        var_counter += 1
    elif isinstance(value, float) or isinstance(value, int):
        value = z3.RealVal(value)
    return value

def _value_of(value, model):
    if isinstance(value, float) or isinstance(value, int):
        return value
    elif isinstance(value, z3.RatNumRef):
        return float(value.numerator_as_long()) / float(value.denominator_as_long())
    elif isinstance(value, z3.AlgebraicNumRef):
        return _value_of(value.approx(20), model)
    elif isinstance(value, z3.ArithRef):
        return _value_of(model.evaluate(value), model)
    else:
        raise ValueError(f"{value} (type {type(value)} could not be evaluated")
"""

def element(func):
    @wraps(func)
    def element_wrapper(*args, **kwargs):
        original_defaults = func.__defaults__
        if func.__defaults__ is not None:
            defaults = []
            for default in func.__defaults__:
                if isinstance(default, VarPlaceholder):
                    defaults.append(var(default))
                elif isinstance(default, PointPlaceholder):
                    defaults.append(point(default))
                else:
                    defaults.append(default)
            func.__defaults__ = tuple(defaults)
        #args = [arg + 1 if isinstance(arg, Real) else arg for arg in args]
        #kwargs = dict([(name, val + 1) if isinstance(val, Real) else (name, val) for (name, val) in kwargs.items()])
        return_value = func(*args, **kwargs)
        func.__defaults__ = original_defaults
        return return_value
    return element_wrapper


class LineSegment:
    def __init__(self, start=PointPlaceholder(), end=PointPlaceholder()):
        self.start, self.end = point(start), point(end)

    def at(self, t: float):
        return self.start + Point(t * (self.end.x - self.start.x), t * (self.end.y - self.start.y))

    def __eq__(self, other):
        return (self.start == other.start) + (self.end == other.end)


class Bounds:
    def __init__(self, top_left=PointPlaceholder(), width=VarPlaceholder(), height=VarPlaceholder()):
        self.top_left, self.width, self.height = point(top_left), var(width), var(height)

    @property
    def top_right(self) -> Point:
        return self.top_left + Point(self.width, 0)

    @property
    def bottom_left(self) -> Point:
        return self.top_left + Point(0, self.height)

    @property
    def bottom_right(self) -> Point:
        return self.top_left + Point(self.width, self.height)

    @property
    def center(self) -> Point:
        return self.top_left + Point(self.width / 2, self.height / 2)

    @property
    def left_edge(self) -> LineSegment:
        return LineSegment(self.top_left, self.bottom_left)

    @property
    def top_edge(self) -> LineSegment:
        return LineSegment(self.top_left, self.top_right)

    @property
    def right_edge(self) -> LineSegment:
        return LineSegment(self.top_right, self.bottom_right)

    @property
    def bottom_edge(self) -> LineSegment:
        return LineSegment(self.bottom_left, self.bottom_right)

    @property
    def top(self):
        return self.top_left.y

    @property
    def bottom(self):
        return self.top_left.y + self.height

    @property
    def left(self):
        return self.top_left.x

    @property
    def right(self):
        return self.top_left.x + self.width


class Style:
    def __init__(self, **kwargs):
        self.fill = kwargs.get("fill", None)
        if self.fill is None:
            self.fill = "#ffffff"
            self.fill_opacity = 0
        else:
            self.fill_opacity = kwargs.get("fill-opacity", 1)
        self.outline = kwargs.get("outline", "black")
        if self.outline is None:
            self.outline = "#ffffff"
            self.outline_opacity = 0
        else:
            self.outline_opacity = kwargs.get("outline-opacity", 1)
        self.font = kwargs.get("font", "sans-serif")
        self.fontsize = kwargs.get("fontsize", 14)
        self.bold = kwargs.get("bold", False)
        self.italic = kwargs.get("italic", False)


class Canvas:
    def __init__(self, width, height, root):
        self.width, self.height = width, height
        self.root = root

    """
    def show(self):
        solver = z3.Solver()
        if False in self.root.constraints:
            print(f"Unsolvable (reason: constraints contain false)")
            return None
        solver.add([e for e in self.root.constraints if e is not True])

        if solver.check() != z3.sat:
            print(f"Unsolvable (reason: solver: {solver.check()})")
            return None

        print(
            f"Solved {len(self.root.constraints)} constraints in {solver.statistics().time}s")
        model = solver.model()

        img = Image.new("RGBA", (self.width,
                        self.height), (255, 255, 255, 255))
        ctx = ImageDraw.Draw(img)

        self.root._draw(ctx, model)

        return img
    """

class SolverError(Exception):
    pass

class Solution(ABC):
    @abstractmethod
    def value_of(self, var):
        pass

    def __getitem__(self, var):
        if isinstance(var, Real):
            return var
        elif isinstance(var, Value):
            return self.value_of(var)
        elif isinstance(var, Point):
            return self.value_of(var.x), self.value_of(var.y)
        else:
            raise TypeError(f"Can only get the assignment of a Value, a Point or a number, but not of a {type(var)}")

class Renderer(ABC):
    @abstractmethod
    def line(self, start_x, start_y, end_x, end_y, style):
        pass

    @abstractmethod
    def rectangle(self, tl_x, tl_y, width, height, style):
        pass

    @abstractmethod
    def circle(self, center_x, center_y, radius, style):
        pass

    @abstractmethod
    def text(self, tl_x, tl_y, text, style):
        pass