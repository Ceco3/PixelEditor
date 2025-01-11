from .Template import template, component, tDict, slide_panel
from .Color import toRgba, color_rgba, color_rgb
from .Canvas import Canvas
from .Meta import Registry
from .Mouse import Mouse
from .ComF import cmax, validate_string
from .Window import Window
from .Button import lyrBt, button, textBt
from .Prompt import prompt
from . import Settings

import cv2, numpy
import pygame

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
    
    ret_info, _ = prompt.load_prompt(None, (Window.winX / 2 - 250, Window.winY / 2 - 175), 500, 350)
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

def load_frame(frame_uid):
    bgra_content = cv2.imread(Settings.Get("User", ["Paths", "FrameBuffer"]) + frame_uid)

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
    def __init__(self, localPos, order, width, height) -> None:
        super().__init__(localPos, order, width, height)
        self.iconSize = 30
        self.primary = {}

    def draw(self):
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

    def save_pallete(self):
        pass

    def load_pallete(self):
        pass

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

class color_picker(component):
    def __init__(self, localPos, order, width, height, bound_pallete: pallete, color_override=None):
        super().__init__(localPos, order, width, height, color_override)
        self.prewiev = [0, 0, 0, 255]
        self.bound_pallete = bound_pallete
        r_butt = textBt((100, 10), 0, 30, 30, "0", (3, 10))
        r_butt.attach(self.repaint_prewiev)
        g_butt = textBt((100, 50), 1, 30, 30, "0", (3, 10))
        g_butt.attach(self.repaint_prewiev)
        b_butt = textBt((100, 90), 2, 30, 30, "0", (3, 10))
        b_butt.attach(self.repaint_prewiev)

        def pick_color(BtObject):
            bound_pallete.new_color(toRgba(self.prewiev))
        pick_button = button((20, 45), 4, 40, 40, attachFn=pick_color)

        self.link_multi(r_butt, g_butt, b_butt, pick_button)
    
    def draw(self):
        super().draw()
        self.bound_pallete.draw()
        pygame.draw.rect(self.surf, [100, 100, 100], pygame.Rect(15, 40, 50, 50))
        pygame.draw.rect(self.surf, self.prewiev, pygame.Rect(20, 45, 40, 40))

    def repaint_prewiev(self, BtObject):
        color = [0, 0, 0, 255]
        for color_button in self.components.values():
            if color_button.order == 4:
                continue
            color[color_button.order] = int(color_button.stats["txt"])
        self.prewiev = color

class layer_mngr(component):
    def __init__(self, localPos, order, width, height) -> None:
        super().__init__(localPos, order, width, height)
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
        color_override = [[150, 150, 150], [150, 150, 150], [200, 200, 200]]
        self.components[most + 1] = lyrBt((5, (self.stats["lyrBh"] + 1) * (most) + 5), most + 1, self.stats["lyrBw"], self.stats["lyrBh"],
                                           textPos=(90, 10), color_override=color_override)

    def draw(self):
        self.surf.fill(self.stats["c"])
        for component in self.components.values():
            if component.order < 0:
                component.draw()
                self.surf.blit(component.surf, component.localPos)
            if component.order > 0:
                component.draw(Canvas.lDict[component.order].color_data)
                self.surf.blit(component.surf, component.localPos)

class frame_mngr(slide_panel):
    def __init__(self, localPos, order, width, height, big_width, big_height, sliderBt, horizontal=False, color_override=None):
        super().__init__(localPos, order, width, height, big_width, big_height, sliderBt, horizontal, color_override)
        self.frame_buff = []

    def add_frame(self, uid: str):
        self.frame_buff.append(uid)

    def play(self):
        pass

class settings(template):
    def __init__(self, position, master_w, width, master_h, height) -> None:
        super().__init__(position, master_w, width, master_h, height)
        self.toggle = False
        self.new_component((0, 0), width, height)
        Registry.Write("Settings", self)

I_SHAPE = 0
DASH_SHAPE = 1

class selection(template):
    def __init__(self, position, master_w, master_h, button_fns: list[button], button_dim: int,
                 shape = I_SHAPE, tDict_override=None, color_override=None):
        if shape == I_SHAPE:
            width = button_dim + (1/6) * button_dim * 2 + 10
            height = len(button_fns) * button_dim + (1/6) * button_dim * (len(button_fns) + 1) + 10
        if shape == DASH_SHAPE:
            height = button_dim + (1/6) * button_dim * 2 + 10
            width = len(button_fns) * button_dim + (1/6) * button_dim * (len(button_fns) + 1) + 10
        super().__init__(position, master_w, width, master_h, height, tDict_override, color_override)
        self.shape = shape
        self.button_dim = button_dim
        self.toggle = False
        self.new_component((0, 0), width, height)
        self.populate(button_fns)
    
    def populate(self, button_fns: list[button]):
        if self.shape == I_SHAPE:
            gap = (1/6) * self.button_dim
            i = 0
            for function in button_fns:
                Button = button((5 + gap, 5 + gap + i * (self.button_dim + gap)), i, self.button_dim, self.button_dim,
                                attachFn=function)
                self.components[0].link_component(Button)
        if self.shape == DASH_SHAPE:
            pass