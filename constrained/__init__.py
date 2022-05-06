from .ast import Var, VarPlaceholder, Point, PointPlaceholder
from .core import element, Canvas, Style
from .primitive import Group, Rect, Text, Circle, Arrow
from .z3solver import solve_with_z3
from .svg import SVGRenderer


def solve(canvas, solver="Z3", renderer="SVG"):
    solution = solve_with_z3(canvas)
    renderer = SVGRenderer(canvas)
    canvas.root._draw(solution, renderer)
    return renderer