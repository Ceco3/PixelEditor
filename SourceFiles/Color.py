def toRgba(tup):
    return color_rgba(tup[0], tup[1], tup[2], tup[3])

def maxA(num):
    if num > 255:
        num = 255
    return num

class color_rgb:
    def __init__(self, r = 0, g = 0, b = 0) -> None:
        self.r = r
        self.g = g
        self.b = b

    def toTuple(self):
        return (self.r, self.g, self.b)
    
    def show(self):
        print("----Color----")
        print(self.__dict__)

class color_rgba(color_rgb):
    def __init__(self, r = 0, g = 0, b = 0, a = 0) -> None:
        super().__init__(r, g, b)
        self.a = a

    def toTuple(self):
        return (self.r, self.g, self.b, self.a)
    
    def toBGRA(self) -> 'color_rgba':
        return color_rgba(self.b, self.g, self.r, self.a)
    
    def __add__(self, color):
        return color_rgba(self.r, self.g, self.b, maxA(self.a + color.a))