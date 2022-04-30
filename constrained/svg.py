from constrained.core import Renderer
import drawSvg as draw

class SVGRenderer(Renderer):
    def __init__(self, canvas):
        self.svg = draw.Drawing(canvas.width, canvas.height, origin="center")

    def line(self, start_x, start_y, end_x, end_y):
        self.svg.append(draw.Line(start_x, start_y, end_x, end_y))
    
    def rectangle(self, tl_x, tl_y, width, height):
        self.svg.append(draw.Rectangle(tl_x, tl_y, width, height))

    def circle(self, center_x, center_y, radius):
        self.svg.append(draw.Circle(center_x, center_y, radius, fill="#eeee00"))