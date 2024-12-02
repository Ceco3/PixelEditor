import os

def Lerp(a: float, b: float, c: float) -> float:
    "c indicates how done you are"
    return a + (b - a) * c