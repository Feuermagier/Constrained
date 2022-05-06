from PIL import ImageFont

from .core import *
from .ast import Min, Max, Var, VarPlaceholder, Point, PointPlaceholder, point, var

class Primitive(ABC):
    @abstractmethod
    def _draw(self, solution: Solution, renderer: Renderer):
        pass

class Group(Primitive):
    def __init__(self, objects, constraints, padding_left=0, padding_right=0, padding_top=0, padding_bottom=0, draw_box=False):
        self.objects = objects
        self.draw_box = draw_box
        self.padding_left = var(padding_left)
        self.padding_right = var(padding_right)
        self.padding_top = var(padding_top)
        self.padding_bottom = var(padding_bottom)

        self.constraints = _flatten_constraints(constraints)
        for object in objects:
            self.constraints += object.constraints

        self.bounds = Bounds()
        self.constraints.append(
            Min(self.bounds.left + self.padding_left, [o.bounds.left for o in objects]))
        self.constraints.append(
            Min(self.bounds.top + self.padding_top, [o.bounds.top for o in objects]))
        self.constraints.append(
            Max(self.bounds.right - self.padding_right, [o.bounds.right for o in objects]))
        self.constraints.append(
            Max(self.bounds.bottom - self.padding_bottom, [o.bounds.bottom for o in objects]))

    def _draw(self, solution, renderer):
        for obj in self.objects:
            obj._draw(solution, renderer)
        if self.draw_box:
            x0, y0 = solution[self.bounds.top_left]
            width, height = solution[self.bounds.width], solution[self.bounds.height]
            renderer.rectangle(x0, y0, width, height, Style(fill=None, outline="red"))

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
        renderer.rectangle(x0, y0, width, height, self.style)


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
        renderer.circle(cx, cy, radius, self.style)


class Arrow(Primitive):
    def __init__(self, start=PointPlaceholder(), end=PointPlaceholder(), **kwargs):
        super().__init__()
        self.start = point(start)
        self.end = point(end)
        self.bounds = Bounds(self.start, self.end.x -
                             self.start.x, self.end.y - self.end.y)
        self.constraints = []
        self.style = kwargs.get("style", Style())

    def _draw(self, solution, renderer):
        x0, y0 = solution[self.start]
        x1, y1 = solution[self.end]

        renderer.line(x0, y0, x1, y1, self.style)


class Text:
    def __init__(self, text: str, top_left=PointPlaceholder(), width=VarPlaceholder(), height=VarPlaceholder(), **kwargs):
        self.top_left = point(top_left)
        self.width, self.height = var(width), var(height)
        self.style = kwargs.get("style", Style())
        self.text = text
        self.bounds = Bounds(self.top_left, self.width, self.height)
        self.constraints = []

        if kwargs.get("fit", True):
            measured_width, measured_height = _measure_text(text, self.style.font, self.style.bold, self.style.italic, self.style.fontsize)
            self.constraints.append(self.width == measured_width)
            self.constraints.append(self.height == measured_height)

    def _draw(self, solution, renderer):
        x0, y0 = solution[self.top_left]
        renderer.text(x0, y0, self.text, self.style)


# See https://blog.mathieu-leplatre.info/text-extents-with-python-cairo.html
def _measure_text(text: str, font: str, bold: bool, italic: bool, size: int):
    try:
        import cairo
    except Exception:
        raise Exception("PyCairo is required to measure the size of text.")
    surface = cairo.SVGSurface(None, 1280, 200)
    ctx = cairo.Context(surface)
    ctx.select_font_face(font, cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    xbearing, ybearing, width, height, xadvance, yadvance = ctx.text_extents(text)
    return width, height

"""
def _load_font(font: str, font_size: int):
    if font is None:
        font = ImageFont.truetype(
            "fonts/open-sans/OpenSans-Regular.ttf", font_size)
    else:
        font = ImageFont.truetype(font, font_size)
    return font
"""