import os

def Lerp(a: float, b: float, c: float) -> float:
    "c indicates how done you are"
    return a + (b - a) * c

def Clamp(min: float, max: float, preffered: float) -> float:
    if min > preffered:
        return min
    if max < preffered:
        return max
    return preffered

def ClampMin(min: int, preffered: int) -> int:
    if preffered < min:
        return min
    return preffered

def cmax(list_):
    if list_ == []:
        return -1
    return max(list_)

DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def validate_string(input: str) -> bool:
    """Checks if <input> is a valid base-10 string
        representation of an int"""
    if len(input) == 0:
        return False
    for char in input:
        if char not in DIGITS:
            return False
    if input[0] == '0':
        return False
    
    return True

def digit_num(num: int) -> int:
    res = 0
    while num > 0:
        num //= 10
        res += 1
    
    return res

def img_preview_txt(dims: tuple[int, int]) -> str:
    x, y = dims
    digits_in_x = digit_num(x)
    digits_in_y = digit_num(y)

    res = "x$"
    res += str(x)
    res += " " * (2 - digits_in_x)

    res += "y$"
    res += str(y)
    res += " " * (2 - digits_in_y)

    return res


def pair_sum(*tuples) -> tuple:
    x, y = 0, 0
    for tpl in tuples:
        a, b = tpl
        x += a
        y += b
    return (x, y)

def pair_mul(*tuples) -> tuple:
    x, y = 1, 1
    for tpl in tuples:
        a, b = tpl
        x *= a
        y *= b
    return (x, y)

def pair_div(tpl: tuple[float, float], k: int) -> tuple[float, float]:
    x, y = tpl
    return (x / k, y / k)

def pair_div_vec(tpl1: tuple[float, float], tpl2: tuple[float, float]):
    x1, y1 = tpl1
    x2, y2 = tpl2
    return (x1 / x2, y1 / y2)