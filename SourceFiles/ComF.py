import os

def Lerp(a: float, b: float, c: float) -> float:
    "c indicates how done you are"
    return a + (b - a) * c

def cmax(list_):
    if list_ == []:
        return -1
    return max(list_)