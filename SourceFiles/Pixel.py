from .Color import color_rgb, color_rgba
import numpy

class pixel:
    def __init__(self, x: int, y: int, color: color_rgba) -> None:
        self.x = x
        self.y = y
        self.color = color

    def toRawColor(self):
        return numpy.array([self.color.b, self.color.g, self.color.r, self.color.a])