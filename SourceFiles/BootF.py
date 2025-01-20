from .Color import color_rgba
from .Mouse import Mouse
from .Canvas import Canvas
from . import Settings

import numpy, cv2
import os

def build(gridObject: list[list[color_rgba]], path, name: str) -> None:
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

    cv2.imwrite(path + "\{}".format(name) + ".png", numpyGrid)

def build_canvas(send_to_frame_buffer = False, frame_uid = None):
    if not send_to_frame_buffer:
        build(Canvas.lDict[Mouse.layer_selected].grid, Settings.Get("User", ["Paths", "SaveDir"]), Settings.Get("Project", "Name"))
    if send_to_frame_buffer:
        if frame_uid is None:
            name = len(os.listdir(Settings.Get("User", ["Paths", "FrameBuffer"])))
        if frame_uid is not None:
            name = frame_uid
        build(Canvas.lDict[Mouse.layer_selected].grid, Settings.Get("User", ["Paths", "FrameBuffer"]), name)
    Settings.Set("Project", "Canvas", Canvas.get_raw())

def load_frame(frame_uid: int) -> list[list[color_rgba]]:
    bgra_content = cv2.imread(Settings.Get("User", ["Paths", "FrameBuffer"]) + "\\" + str(frame_uid) + ".png", -1)

    if bgra_content is None:
        # Pop up Ideally
        return Canvas.lDict[Mouse.layer_selected].grid
    
    gridObject = []

    height = len(bgra_content)
    width = len(bgra_content[0])

    for y in range(height):
        row = []
        for x in range(width):
            row.append(color_rgba(int(bgra_content[y][x][2]), int(bgra_content[y][x][1]), int(bgra_content[y][x][0]), int(bgra_content[y][x][3])))
        gridObject.append(row)

    return gridObject