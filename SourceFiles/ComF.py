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

def pair_sum(*tuples):
    x, y = 0, 0
    for tpl in tuples:
        a, b = tpl
        x += a
        y += b
    return (x, y)