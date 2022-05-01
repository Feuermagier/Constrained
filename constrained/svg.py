from constrained.core import Renderer
import svgwrite

class SVGRenderer(Renderer):
    def __init__(self, canvas):
        self.svg = svgwrite.Drawing(size=(canvas.width, canvas.height))

    def line(self, start_x, start_y, end_x, end_y, style):
        self.svg.add(self.svg.line((start_x, start_y), (end_x, end_y), stroke=style.outline))
    
    def rectangle(self, tl_x, tl_y, width, height, style):
        self.svg.add(self.svg.rect((tl_x, tl_y), (width, height), stroke=style.outline, stroke_opacity=style.outline_opacity, fill=style.fill, fill_opacity=style.fill_opacity))

    def circle(self, center_x, center_y, radius, style):
        self.svg.add(self.svg.circle((center_x, center_y), radius, stroke=style.outline, stroke_opacity=style.outline_opacity, fill=style.fill, fill_opacity=style.fill_opacity))

    def text(self, tl_x, tl_y, text, style):
        self.svg.add(self.svg.text(text=text, x=[tl_x], y=[tl_y], font_size=style.fontsize, font_family=style.font, dominant_baseline="hanging"))

    def as_svg(self):
        return self.svg.tostring()

    def _repr_svg_(self):
        return self.as_svg()