from PIL import ImageFont

from .core import *
from .ast import Min, Max, Var, VarPlaceholder, Point, PointPlaceholder, point, var


class Group:
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

    def _draw(self, ctx, model):
        for obj in self.objects:
            obj._draw(ctx, model)

    def _svg(self, ctx, model):
        for obj in self.objects:
            obj._svg(ctx, model)


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


class Rect:
    def __init__(self, top_left = PointPlaceholder(), width = VarPlaceholder(), height = VarPlaceholder(), **kwargs):
        self.top_left = point(top_left)
        self.width = var(width)
        self.height = var(height)
        self.style = kwargs.get("style", Style())

        self.bounds = Bounds(self.top_left, self.width, self.height)
        self.constraints = [self.width > 0, self.height > 0]

    def _draw(self, ctx, model):
        x0, y0 = self.top_left._value(model)

        width = _value_of(self.width, model)
        height = _value_of(self.height, model)

        ctx.rectangle([(x0, y0), (x0 + width, y0 + height)],
                      outline=self.style.outline, fill=self.style.fill)

    def _svg(self, ctx, model):
        x0, y0 = self.top_left._value(model)

        width = _value_of(self.width, model)
        height = _value_of(self.height, model)
        ctx.add(ctx.rectangle(insert=(x0, y0), size=(width, height)))


class Circle:
    def __init__(self, center=PointPlaceholder(), radius=VarPlaceholder(), **kwargs):
        self.center = point(center)
        self.radius = var(radius)
        self.bounds = Bounds(
            self.center - Point(self.radius, self.radius), 2 * self.radius, 2 * self.radius)
        self.constraints = [self.radius > 0]
        self.style = kwargs.get("style", Style())

    def _draw(self, ctx, model):
        cx, cy = self.center._value(model)
        radius = _value_of(self.radius, model)

        ctx.ellipse([(cx - radius, cy - radius),
                    (cx + radius, cy + radius)], outline=self.style.outline, fill=self.style.fill)

    def _svg(self, ctx, model):
        cx, cy = self.center._value(model)
        radius = _value_of(self.radius, model)
        ctx.circle(center=(cx, cy), r=radius)


class Arrow:
    def __init__(self, **kwargs):
        self.start = point(kwargs.get("start", None))
        self.end = point(kwargs.get("end", None))
        self.bounds = Bounds(self.start, self.end.x -
                             self.start.x, self.end.y - self.end.y)
        self.constraints = []
        self.style = kwargs.get("style", Style())

    def _draw(self, ctx, model):
        x0, y0 = self.start._value(model)
        x1, y1 = self.end._value(model)

        ctx.line([(x0, y0), (x1, y1)], fill=self.style.fill)

    def _svg(self, ctx, model):
        x0, y0 = self.start._value(model)
        x1, y1 = self.end._value(model)
        ctx.polyline([(x0, y0), (x1, y1)])


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
