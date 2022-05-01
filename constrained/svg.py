from constrained.core import Renderer
import drawSvg as draw

class SVGRenderer(Renderer):
    def __init__(self, canvas):
        self.svg = draw.Drawing(canvas.width, canvas.height, origin=(0, 0))

    def line(self, start_x, start_y, end_x, end_y, style):
        self.svg.append(draw.Line(start_x, start_y, end_x, end_y, stroke=style.outline))
    
    def rectangle(self, tl_x, tl_y, width, height, style):
        self.svg.append(draw.Rectangle(tl_x, tl_y, width, height, stroke=style.outline, fill=style.fill))

    def circle(self, center_x, center_y, radius, style):
        self.svg.append(draw.Circle(center_x, center_y, radius, stroke=style.outline, fill=style.fill))