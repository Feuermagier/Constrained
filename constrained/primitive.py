from PIL import ImageFont

from .core import *
from .ast import Min, Max, Var, VarPlaceholder, Point, PointPlaceholder, point, var

class Primitive(ABC):
    @abstractmethod
    def _draw(self, solution: Solution, renderer: Renderer):
        pass

class Group(Primitive):
    def __init__(self, objects, constraints):
        self.objects = objects
        self.constraints = _flatten_constraints(constraints)
        for object in objects:
            self.constraints += object.constraints

        self.bounds = Bounds()
        self.constraints.append(
            Min(self.bounds.left, [o.bounds.left for o in objects]))
        self.constraints.append(
            Min(self.bounds.top, [o.bounds.top for o in objects]))
        self.constraints.append(
            Max(self.bounds.right, [o.bounds.right for o in objects]))
        self.constraints.append(
            Max(self.bounds.bottom, [o.bounds.bottom for o in objects]))

    def _draw(self, solution, renderer):
        for obj in self.objects:
            obj._draw(solution, renderer)

def _flatten_constraints(constraints):
    result = []
    for c in constraints:
        if isinstance(c, bool):
            continue
        elif isinstance(c, list):
            result.extend(_flatten_constraints(c))
        else:
            result.append(c)
    return result

class Rect(Primitive):
    def __init__(self, top_left = PointPlaceholder(), width = VarPlaceholder(), height = VarPlaceholder(), **kwargs):
        super().__init__()
        self.top_left = point(top_left)
        self.width = var(width)
        self.height = var(height)
        self.style = kwargs.get("style", Style())

        self.bounds = Bounds(self.top_left, self.width, self.height)
        self.constraints = [self.width > 0, self.height > 0]

    def _draw(self, solution, renderer):
        x0, y0 = solution[self.top_left]
        width = solution[self.width]
        height = solution[self.height]
        renderer.rectangle(x0, y0, width, height)


class Circle(Primitive):
    def __init__(self, center=PointPlaceholder(), radius=VarPlaceholder(), **kwargs):
        super().__init__()
        self.center = point(center)
        self.radius = var(radius)
        self.bounds = Bounds(
            self.center - Point(self.radius, self.radius), 2 * self.radius, 2 * self.radius)
        self.constraints = [self.radius > 0]
        self.style = kwargs.get("style", Style())

    def _draw(self, solution, renderer):
        cx, cy = solution[self.center]
        radius = solution[self.radius]
        renderer.circle(cx, cy, radius)


class Arrow(Primitive):
    def __init__(self, **kwargs):
        super().__init__()
        self.start = point(kwargs.get("start", None))
        self.end = point(kwargs.get("end", None))
        self.bounds = Bounds(self.start, self.end.x -
                             self.start.x, self.end.y - self.end.y)
        self.constraints = []
        self.style = kwargs.get("style", Style())

    def _draw(self, solution, renderer):
        x0, y0 = solution[self.start]
        x1, y1 = solution[self.end]

        renderer.line(x0, y0, x1, y1)


class Text:
    def __init__(self, text: str, **kwargs):
        self.top_left = point(kwargs.get("top_left", None))
        self.style = kwargs.get("style", Style())
        self.text = text
        width, height = _load_font(
            self.style.font, self.style.font_size).getsize_multiline(text)
        self.bounds = Bounds(self.top_left, width, height)
        self.constraints = []

    def _draw(self, ctx, model):
        x0, y0 = self.top_left._value(model)
        ctx.text((x0, y0), self.text, fill=self.style.fill,
                 font=_load_font(self.style.font, self.style.font_size))

    def _svg(self, ctx, model):
        x0, y0 = self.top_left._value(model)
        ctx.text(self.text, insert=(x0, y0))


def _load_font(font: str, font_size: int):
    if font is None:
        font = ImageFont.truetype(
            "fonts/open-sans/OpenSans-Regular.ttf", font_size)
    else:
        font = ImageFont.truetype(font, font_size)
    return font
