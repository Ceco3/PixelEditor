from .Template import template, component, tDict
from .Color import toRgba, color_rgba, color_rgb
from .Canvas import Canvas
from .Meta import Registry
from .Mouse import Mouse
from .ComF import cmax, ClampMin
from .Window import Window
from .Button import lyrBt
from .Prompt import prompt

import cv2, numpy
import pygame
import sys, os

def build(gridObject: list[list[color_rgba]], path, name) -> None:
    "Builds the image (as specified by Project settings)"
    height = len(gridObject)
    width = len(gridObject[0])

    numpyGrid = []

    for y in range(height):
        row = []
        for x in range(width):
            row.append(numpy.array(gridObject[y][x].toBGRA().toTuple()))
        numpyGrid.append(numpy.array(row))
    
    numpyGrid = numpy.array(numpyGrid)

    cv2.imwrite(path + "\{}".format(name) + ".png", numpyGrid)

def load():
    
    ret_info, _ = prompt.load_prompt(None, (Window.winX / 2 - 250, Window.winY / 2 - 175), 500, 350, color_rgb(170, 170, 170), color_rgb(90, 30, 40))
    if ret_info is None:
        # Pop up Ideally
        return Canvas.lDict[Mouse.layer_selected].grid
    path = ret_info[0]

    if ".png" not in path:
        bgra_content = cv2.imread(path + ".png", -1)
    else:
        bgra_content = cv2.imread(path, -1)

    if bgra_content is None:
        # Pop up Ideally
        return Canvas.lDict[Mouse.layer_selected].grid

    gridObject = []

    height = len(bgra_content)
    width = len(bgra_content[0])

    for y in range(height):
        row = []
        for x in range(width):
            row.append(color_rgba(bgra_content[y][x][2], bgra_content[y][x][1], bgra_content[y][x][0], bgra_content[y][x][3]))
        gridObject.append(row)

    return gridObject

AUTOSAVE = pygame.USEREVENT + 6
AUTOSAVE_EV = pygame.event.Event(AUTOSAVE)

def bound(x, y):
    if x < y:
        return x
    return y

class pallete(component):
    def __init__(self, localPos, order, width, height, color) -> None:
        super().__init__(localPos, order, width, height, color)
        self.iconSize = 30
        self.primary = {}

    def draw(self):
        cntr = 0
        super().draw()
        maximal = max(list(self.primary.keys()))
        columns = (self.stats["w"] - 20) // self.iconSize
        rows = len(self.primary) // columns + 1
        for y in range(rows):
            for x in range(columns):
                if x + columns * y > maximal:
                    return
                pygame.draw.rect(self.surf, self.primary[x + columns * y], pygame.Rect(self.iconSize * x + 10, self.iconSize * y + 10, self.iconSize, self.iconSize))

    def new_color(self, color):
        keys = list(self.primary.keys())
        new_color_order = cmax(keys) + 1
        self.primary[new_color_order] = color.toTuple()

    def onClick(self, localMousePos):
        columns = bound(len(list(self.primary.keys())) , (self.stats["w"] - 20) // self.iconSize)
        x = localMousePos[0] - 10
        y = localMousePos[1] - 10
        x = x - x % self.iconSize
        y = y - y % self.iconSize
        x //= self.iconSize
        y //= self.iconSize
        try:
            Mouse.color = toRgba(self.primary[x + columns * y])
        except:
            pass

class layer_mngr(component):
    def __init__(self, localPos, order, width, height, color) -> None:
        super().__init__(localPos, order, width, height, color)
        self.stats["lyrBh"] = 25
        self.stats["lyrBw"] = 215
        self.build()

    def build(self):
        for lyr_key in Canvas.lDict:
            self.new_layer()

    def update(self):
        for lyr_key in Canvas.lDict:
            if lyr_key not in self.components:
                self.new_layer()
            if Mouse.layer_selected == lyr_key:
                self.components[lyr_key].stats["f"] = False
        self.draw()

    def del_layer(self):
        del self.components[Mouse.layer_selected]
        keys = list(self.components.keys())
        for key in keys:
            if key > Mouse.layer_selected:
                self.components[key - 1] = self.components[key]
                del self.components[key]
        Mouse.layer_selected -= 1      # Think about where to move <layer_selected> more
        if Mouse.layer_selected == 0:
            Mouse.layer_selected = 1

    def new_layer(self):
        most = cmax(list(self.components.keys()))
        self.components[most + 1] = lyrBt((5, (self.stats["lyrBh"] + 1) * (most) + 5), most + 1, self.stats["lyrBw"], self.stats["lyrBh"],
                                           color_rgb(150, 150, 150), color_rgb(150, 150, 150), color_rgb(200, 200, 200), textPos=(90, 10))

    def draw(self):
        self.surf.fill(self.stats["c"])
        for component in self.components.values():
            if component.order < 0:
                component.draw()
                self.surf.blit(component.surf, component.localPos)
            if component.order > 0:
                component.draw(Canvas.lDict[component.order].color_data)
                self.surf.blit(component.surf, component.localPos)

class settings(template):
    def __init__(self, position, master_w, width, master_h, height, color, frame_color) -> None:
        super().__init__(position, master_w, width, master_h, height, color, frame_color)
        self.toggle = False
        self.new_component((0, 0), width, height, color_rgb(150, 150, 150))
        Registry.Write("Settings", self)
