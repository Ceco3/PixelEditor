def toRgba(tup):
    return color_rgba(tup[0], tup[1], tup[2], tup[3])

def clampC(num):
    if num > 255:
        num = 255
    return num

def cycleC(num):
    return num % 255

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
    
    def __add__(self, color: 'color_rgba'):
        return color_rgba(cycleC(self.r + color.r), cycleC(self.g + color.g),
                          cycleC(self.b + color.b), clampC(self.a + color.a))