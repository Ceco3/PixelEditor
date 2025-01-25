from .Color import color_rgba
from .Mouse import Mouse
from . import Canvas
from . import Settings
from .Meta import Registry

import numpy, cv2
import os

def build(gridObject: list[list[color_rgba]], path, name: str) -> bool:
    "Builds the image (as specified by Project settings)"
    height = len(gridObject)
    width = len(gridObject[0])
    if path == '':
        Settings.load_specified_setting("User")
        path = Settings.Get("User", ["Paths", "SaveDir"])

    numpyGrid = []

    for y in range(height):
        row = []
        for x in range(width):
            row.append(numpy.array(gridObject[y][x].toBGRA().toTuple()))
        numpyGrid.append(numpy.array(row))
    
    numpyGrid = numpy.array(numpyGrid)

    return cv2.imwrite(path + "\{}".format(name) + ".png", numpyGrid)

def build_canvas() -> bool:
    return build(Canvas.Canvas.lDict[Mouse.layer_selected].grid, Settings.Get("User", ["Paths", "SaveDir"]), Settings.Get("Project", "Name"))
    Settings.Set("Project", "Canvas", Canvas.Canvas.get_raw())

def build_anim(name: str, path = None) -> bool:
    "Builds all the frames currently in your frame manager as a folder"
    FrmM = Registry.Read("FrameManager")

    if path is None:
        Settings.load_specified_setting("User")
        path = Settings.Get("User", ["Paths", "SaveDir"]) 
    path += "\\" + name
    if not os.path.exists(path):
        os.makedirs(path)

    for Component in FrmM.components.values():
        if Component.order == 0: # Component is the slider button
            continue
        foremost_layer = max(Component.bound_canvas.lDict)
        build(Component.bound_canvas.lDict[foremost_layer].grid, path, str(Component.uid))