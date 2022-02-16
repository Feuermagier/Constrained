from PIL import Image, ImageDraw
import z3

global var_counter
var_counter = 0


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


class Point:
    def __init__(self, x=None, y=None):
        self.x, self.y = num(x), num(y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return [self.x == other.x, self.y == other.y]

    def _value(self, model):
        return _value_of(self.x, model), _value_of(self.y, model)


def point(value) -> Point:
    if isinstance(value, Point):
        return value
    elif value is None:
        return Point(None, None)
    else:
        x, y = value
        return Point(x, y)


class LineSegment:
    def __init__(self, start=None, end=None):
        self.start, self.end = point(start), point(end)

    def at(self, t: float):
        return self.start + Point(t * (self.end.x - self.start.x), t * (self.end.y - self.start.y))

    def __eq__(self, other):
        return (self.start == other.start) + (self.end == other.end)


class Bounds:
    def __init__(self, top_left, width, height):
        self.top_left, self.width, self.height = top_left, width, height

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
        self.outline = kwargs.get("outline", (0, 0, 0))
        self.font = kwargs.get("font", None)
        self.font_size = kwargs.get("font_size", 13)

class Canvas:
    def __init__(self, width, height, root):
        self.width, self.height = width, height
        self.root = root

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