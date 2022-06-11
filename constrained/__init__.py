from constrained.diff.diffsolver import solve_with_gradient_descent
from .ast import Var, VarPlaceholder, Point, PointPlaceholder
from .core import element, Canvas, Style
from .primitive import Group, Rect, Text, Circle, Arrow
from .z3solver import solve_with_z3
from .svg import SVGRenderer

def solve(canvas, solver="z3", renderer="SVG", solver_config={}):
    if solver == "z3":
        return _z3_solve(canvas, renderer, solver_config)
    elif solver == "gd":
        return _gd_solve(canvas, renderer, solver_config)
    else:
        raise ValueError(f"Unknown solver '{solver}'")

def _z3_solve(canvas, renderer, config):
    solution = solve_with_z3(canvas)
    renderer = SVGRenderer(canvas)
    canvas.root._draw(solution, renderer)
    return renderer

def _gd_solve(canvas, renderer, config):
    try:
        import IPython
        from constrained.widget import ConstrainedWidget
        w = ConstrainedWidget()
        def callback(step, loss, solution):
            if step % 100 == 0:
                renderer = SVGRenderer(canvas)
                canvas.root._draw(solution, renderer)
                w.svg = renderer._repr_svg_()
        IPython.display.display(w)
    except Exception as e:
        print(e)
        callback = None
    solution = solve_with_gradient_descent(canvas, step_callback=callback)
    renderer = SVGRenderer(canvas)
    canvas.root._draw(solution, renderer)

    if callback is not None:
        IPython.display.clear_output(wait=True)
    return renderer