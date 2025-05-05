import math

from .ComF import Clamp

def toRgba(tup):
    return color_rgba(tup[0], tup[1], tup[2], tup[3])

def clampC(num):
    if num > 255:
        num = 255
    return num

def cycleC(num):
    return num % 255

RE3 = 3**(1/255)
LOGE32 = math.log(2, RE3)

class color_rgb:
    def __init__(self, r = 0, g = 0, b = 0) -> None:
        self.r = r
        self.g = g
        self.b = b

    def shade(self, val: float):
        'Colors Values will be floats during the process! Be sure to correct it afterwards!'
        # <val> == 0: pitch black, <val> == 0.5: unchanged, <val> == 1: blinding white
        
        # transform <val> to [0, 2]
        val *= 2

        # Good Formula shouldnt need Clamp, find better (or you cant)
        self.r = Clamp(0, 255, (1 + (1 - self.r/LOGE32)*(val**2 - 2*val))*math.log(val + 1, RE3))
        self.g = Clamp(0, 255, (1 + (1 - self.g/LOGE32)*(val**2 - 2*val))*math.log(val + 1, RE3))
        self.b = Clamp(0, 255, (1 + (1 - self.b/LOGE32)*(val**2 - 2*val))*math.log(val + 1, RE3))

    def correct(self):
        self.r = int(self.r)
        self.g = int(self.g)
        self.b = int(self.b)
        self.a = int(self.a)

    def toTuple(self):
        return (self.r, self.g, self.b)

    def show(self):
        print("----Color----")
        print(self.__dict__)

class color_rgba(color_rgb):
    def __init__(self, r = 0, g = 0, b = 0, a = 0) -> None:
        super().__init__(r, g, b)
        self.a = a

    def copy(self):
        return color_rgba(self.r, self.g, self.b, self.a)

    def toTuple(self):
        return (self.r, self.g, self.b, self.a)
    
    def toBGRA(self) -> 'color_rgba':
        return color_rgba(self.b, self.g, self.r, self.a)
    
    def __add__(self, color: 'color_rgba'):
        return color_rgba(cycleC(self.r + color.r), cycleC(self.g + color.g),
                          cycleC(self.b + color.b), clampC(self.a + color.a))