from .core import *


@element
def inset(inner, outer, padding_x=VarPlaceholder(), padding_y=VarPlaceholder()):
    return [
        padding_x >= 0,
        padding_y >= 0,
        inner.bounds.left == outer.bounds.left + padding_x,
        inner.bounds.right == outer.bounds.right - padding_x,
        inner.bounds.top == outer.bounds.top + padding_y,
        inner.bounds.bottom == outer.bounds.bottom - padding_y
    ]


@element
def centered_between(element, left, right):
    dist = (right.bounds.left - left.bounds.right)
    return [dist >= 0, element.bounds.center.x == left.bounds.right + dist]

@element
def distributed_horizontally(elements: list, spacing=VarPlaceholder()):
    """Distributes the elements on the horizontal axis with the distance given by spacing (spacing >= 0)"""
    constraints = [spacing >= 0]
    constraints += [elements[i].bounds.right + spacing ==
                    elements[i + 1].bounds.left for i in range(0, len(elements) - 1)]
    return constraints

@element
def distributed_vertically(elements: list, spacing=VarPlaceholder()):
    """Distributes the elements on the vertical axis with the distance given by spacing (spacing >= 0)"""
    constraints = [spacing >= 0]
    constraints += [elements[i].bounds.bottom + spacing ==
                    elements[i + 1].bounds.top for i in range(0, len(elements) - 1)]
    return constraints

@element
def aligned_horizontally(elements: list, align: str = "center", y=VarPlaceholder()):
    """Constrains the y-coordinate of the point of the elements given by align to the value given by y.
    align must be either 'center' (default), 'top' or 'bottom'
    """
    if align == "center":
        return [e.bounds.center.y == y for e in elements]
    elif align == "top":
        return [e.bounds.top == y for e in elements]
    elif align == "bottom":
        return [e.bounds.bottom == y for e in elements]
    else:
        raise ValueError("align must either be 'center', 'top' or 'bottom'")

@element
def aligned_vertically(elements: list, align: str = "center", x=VarPlaceholder()):
    """Constrains the x-coordinate of the points of the elements given by align to the value given by y.
    align must be either 'center' (default), 'left' or 'right'
    """
    if align == "center":
        return [e.bounds.center.x == x for e in elements]
    elif align == "left":
        return [e.bounds.left == x for e in elements]
    elif align == "right":
        return [e.bounds.right == x for e in elements]
    else:
        raise ValueError("align must either be 'center', 'left' or 'right'")
