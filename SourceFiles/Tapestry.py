from .Template import template, component, cmax, tDict
from .Color import toRgba, color_rgba, color_rgb
from .Text import make_word
from .Canvas import Bucket, Pencil, Canvas
from .Meta import Updater, Registry, User_variables
from .FuncBundleBt import FunctionBundle
from .Mouse import Mouse
from .ComF import Lerp
from .Window import Window, Clock

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
            row.append(numpy.array(gridObject[y][x].toTuple()))
        numpyGrid.append(numpy.array(row))
    
    numpyGrid = numpy.array(numpyGrid)
    print(numpyGrid)

    print(path + "\{}".format(name) + ".png")
    cv2.imwrite(path + "\{}".format(name) + ".png", numpyGrid)

def load(path):
    
    prompt.load_prompt(None, (Window.winX / 2 - 250, Window.winY / 2 - 175), 500, 350, color_rgb(170, 170, 170), color_rgb(90, 30, 40))

    if ".png" not in path:
        bgra_content = cv2.imread(path + ".png", -1)
    else:
        bgra_content = cv2.imread(path, -1)

    if bgra_content is None:
        # Pop up Ideally
        print("Failed to load image")
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

BUILD = pygame.USEREVENT + 2
BUILD_EV = pygame.event.Event(BUILD)

LOAD = pygame.USEREVENT + 3
LOAD_EV = pygame.event.Event(LOAD)

LOAD_ID = 0
PROMPT_OVERRIDE = -1

NEWLAYER = pygame.USEREVENT + 4
NEWLAYER_EV = pygame.event.Event(NEWLAYER)

DELLAYER = pygame.USEREVENT + 5
DELLAYER_EV = pygame.event.Event(DELLAYER)

AUTOSAVE = pygame.USEREVENT + 6
AUTOSAVE_EV = pygame.event.Event(AUTOSAVE)

def bound(x, y):
    if x < y:
        return x
    return y

class text(component):
    def __init__(self, localPos, order, width, height, color, tcolor, text, textPos = (0, 0)) -> None:
        super().__init__(localPos, order, width, height, color)
        self.stats["tc"] = tcolor.toTuple()
        self.stats["txt"] = text
        self.stats["txtp"] = textPos
        
    def draw(self):
        super().draw()
        self.surf.blit(make_word(self.stats["txt"], self.stats["tc"]), self.stats["txtp"])

class button(component):
    def __init__(self, localPos, order, width, height, fcolor, color, tcolor, text, textPos = (0, 0)) -> None:
        super().__init__(localPos, order, width, height, color)
        self.stats["f"] = True
        self.stats["fc"] = fcolor.toTuple()
        self.stats["tc"] = tcolor.toTuple()
        self.stats["txt"] = text
        self.stats["txtp"] = textPos
        self.overlaySurf = pygame.Surface((self.stats["w"], self.stats["h"]), pygame.SRCALPHA, 32)
        self.icon = None
        self.master = None
        self.bound = None # (Older) See function_bundle class in FuncBundleBt.py
        self.attached = None # Newer version of bound (See <attach> method)

    def loadIcon(self, iconPath):
        self.icon = pygame.transform.scale(pygame.image.load(iconPath), (self.stats["w"], self.stats["h"]))

    def draw(self):
        super().draw()
        pygame.draw.rect(self.surf, self.stats["fc"], pygame.Rect(3, 3, self.stats["w"] - 6, self.stats["h"] - 6))
        self.surf.blit(make_word(self.stats["txt"], self.stats["tc"]), self.stats["txtp"])
        if self.icon != None:
            self.surf.blit(self.icon, (0, 0))
        if self.stats["f"]:
            self.highlight()

    def highlight(self):
        pygame.draw.rect(self.overlaySurf, (100, 100, 100, 100), pygame.Rect(5, 5, self.stats["w"] - 5, self.stats["h"] - 5))
        self.surf.blit(self.overlaySurf, (0, 0))

    def onClick(self):
        self.stats["f"] = not self.stats["f"]
        if self.attached is not None:
            print("attached call")
            self.attached()
        if self.bound != None and self.bound[0] == 1:
            FunctionBundle.operate(self, Mouse)
        self.draw()
        self.master.draw()

    def attach(self, func):
        "Attach a function <func> to button, the function will be called in the onClick method"
        self.attached = func


class toolBt(button):
    def __init__(self, localPos, order, width, height, fcolor, color, tcolor, tool, text = "", textPos=(0, 0)) -> None:
        super().__init__(localPos, order, width, height, fcolor, color, tcolor, text, textPos)
        self.bound_tool = tool

        if self.bound_tool == Pencil:
            self.stats["f"] = False

    def onClick(self):
        super().onClick()
        Mouse.tool = self.bound_tool

class visBt(button):
    def __init__(self, localPos, order, width, height, fcolor, color, tcolor, text = "", textPos=(0, 0)) -> None:
        super().__init__(localPos, order, width, height, fcolor, color, tcolor, text, textPos)

    def onClick(self):
        super().onClick()
        Mouse.state["visualM"] = not Mouse.state["visualM"]

class lyrBt(button):
    def __init__(self, localPos, order, width, height, fcolor, color, tcolor, text = "layer", textPos=(90, 12)) -> None:
        super().__init__(localPos, order, width, height, fcolor, color, tcolor, text, textPos)
        self.stats["f"] = True
        self.overlaySurf = pygame.Surface((self.stats["w"], self.stats["h"]), pygame.SRCALPHA, 32)

    def draw(self, lyr_stats):
        most = cmax(list(self.components.keys()))
        colors = list(lyr_stats.keys())
        colors.remove("all")
        x = 5
        for color in colors:
            if color == (0, 0, 0, 0):
                continue
            pygame.draw.rect(self.surf, color, pygame.Rect(x, (self.stats["h"] + 1) * (most + 1) + 5, 220, self.stats["h"]))
            x += (lyr_stats[color] / lyr_stats["all"]) * 220
        pygame.draw.rect(self.surf, self.stats["c"], pygame.Rect(x, (self.stats["h"] + 1) * (most + 1) + 5, 220, self.stats["h"]))
        self.surf.blit(make_word(self.stats["txt"], self.stats["tc"]), self.stats["txtp"])
        if self.stats["f"]:
            self.highlight()

    def onClick(self):
        self.stats["f"] = not self.stats["f"]
        Mouse.layer_selected = self.order

class newLBt(button):
    def __init__(self, localPos, order, width, height, fcolor, color, tcolor, text = "new", textPos=(0, 0)) -> None:
        super().__init__(localPos, order, width, height, fcolor, color, tcolor, text, textPos)

    def onClick(self):
        super().onClick()
        pygame.event.post(NEWLAYER_EV)

class delLBt(button):
    def __init__(self, localPos, order, width, height, fcolor, color, tcolor, text = "del", textPos=(0, 0)) -> None:
        super().__init__(localPos, order, width, height, fcolor, color, tcolor, text, textPos)

    def onClick(self):
        super().onClick()
        pygame.event.post(DELLAYER_EV)

class saveBt(button):
    def __init__(self, localPos, order, width, height, color, fcolor, tcolor, text = "save", textPos=(0, 0)) -> None:
        super().__init__(localPos, order, width, height, color, fcolor, tcolor, text, textPos)

    def onClick(self):
        super().onClick()
        pygame.event.post(BUILD_EV)

class exitBt(button):
    def __init__(self, localPos, order, width, height, fcolor, color, tcolor, text = "exit", textPos=(0, 0)) -> None:
        super().__init__(localPos, order, width, height, fcolor, color, tcolor, text, textPos)

    def onClick(self):
        pygame.quit()
        sys.exit()

class loadBt(button):
    def __init__(self, localPos, order, width, height, fcolor, color, tcolor, text = "load", textPos=(0, 0)) -> None:
        super().__init__(localPos, order, width, height, fcolor, color, tcolor, text, textPos)

    def onClick(self):
        super().onClick()
        pygame.event.post(LOAD_EV)

class rollBt(button):
    def __init__(self, localPos, order, width, height, fcolor, color, tcolor, text = "", textPos=(0, 0)) -> None:
        super().__init__(localPos, order, width, height, fcolor, color, tcolor, text, textPos)
        self.toggle = False
        self.isLerping = False
        self.complete = 0
        self.start = None
        self.end = None
        Updater.Add(self)

    def onClick(self):
        super().onClick()
        self.isLerping = True
        x, y = self.master.master.position
        match self.toggle:
            case False:
                self.start = y
                self.end = y - 150
            case True:
                self.start = y
                self.end = y + 150
        self.toggle = not self.toggle
        self.draw()
        self.master.draw()

    def Update(self):
        # Called once per frame
        if self.complete >= 1 or not self.isLerping:
            return
        self.complete += 1/30 # If time is added deltaTime can be used
        x, y = self.master.master.position
        y = Lerp(self.start, self.end, self.complete)
        self.master.master.position = (x, y)
        self.draw()
        self.master.draw()
        if self.complete >= 1:
            self.complete = 0
            self.isLerping = False
            if self.toggle:
                self.loadIcon("Icons\Down.png")
            if not self.toggle:
                self.loadIcon("Icons\Go.png")
            self.draw()
            self.master.draw()

class frameBt(button):
    def __init__(self, localPos, order, width, height, fcolor, color, tcolor, text = "", textPos=(0, 0)) -> None:
        super().__init__(localPos, order, width, height, fcolor, color, tcolor, text, textPos)

    def onClick(self):
        super().onClick()
        print(Registry.Read("Canvas").create_frame())

class popupBt(button):
    def __init__(self, localPos, order, width, height, fcolor, color, tcolor, text = "", textPos=(0, 0)) -> None:
        super().__init__(localPos, order, width, height, fcolor, color, tcolor, text, textPos)
        self.speed = 1/30
        self.complete = 0
        self.toggle = False
        self.isLerping = False
        self.subject: template = None  # With stats["w"] and stats["h"]
        self.internal = (0, 0, 0, 0)
        self.component_buffer = []
        Updater.Add(self)

    def SetValues(self, subject: template, values: tuple[int, int, int, int]):
        self.subject = subject

        x_o, y_o, x_f, y_f = values
        self.internal = values
        for component_ in self.subject.components.values():
            w, h = component_.stats["w"], component_.stats["h"]
            self.component_buffer.append((w, h, w * x_f/x_o, h * y_f/y_o))

        self.switch_start_end()

    def switch_start_end(self):
        x_o, y_o, x_f, y_f = self.internal
        self.internal = (x_f, y_f, x_o, y_o)

        for i, buffer in enumerate(self.component_buffer):
            x_o, y_o, x_f, y_f = buffer
            self.component_buffer[i] = x_f, y_f, x_o, y_o

    def onClick(self):
        super().onClick()
        match self.toggle:
            case False:
                self.subject.toggle = True
            case True:
                pass
        self.switch_start_end()
        self.toggle = not self.toggle
        self.isLerping = True
        self.complete = 0

    def update_surf(self, component_like: component):
        component_like.renew_surf()
        component_like.surf.fill(component_like.stats["c"])
        component_like.draw()

    def Update(self):
        # Called once per frame
        if not self.isLerping:
            return
        self.complete += self.speed
        
        x_o, y_o, x_f, y_f = self.internal
        self.subject.stats["w"] = Lerp(x_o, x_f, self.complete)
        self.subject.stats["h"] = Lerp(y_o, y_f, self.complete)
        self.subject.renew_surf()

        for index, component_ in enumerate(self.subject.components.values()):
            x_o, y_o, x_f, y_f = self.component_buffer[index]
            component_.stats["w"] = Lerp(x_o, x_f, self.complete)
            component_.stats["h"] = Lerp(y_o, y_f, self.complete)
            self.update_surf(component_)

        if self.complete >= 1:
            self.isLerping = False
            if not self.toggle:
                self.subject.toggle = False

class textBt(button):
    def __init__(self, localPos, order, width, height, fcolor, color, tcolor, text = "", textPos=(0, 0)) -> None:
        super().__init__(localPos, order, width, height, fcolor, color, tcolor, text, textPos)
        Updater.Add(self)
        self.toggle = False
        self.backspace_timer = 0

    def onClick(self):
        super().onClick()
        print(self.stats["txt"])
        if self.toggle:
            pygame.key.stop_text_input()
            if self.bound != None:
                FunctionBundle.operate(self, self)
        if not self.toggle:
            pygame.key.start_text_input()
        self.toggle = not self.toggle

    def Update(self):
        if self.toggle:
            if self.backspace_timer > 0:
                self.backspace_timer -= 1
            if pygame.key.get_pressed()[pygame.K_BACKSPACE] and self.backspace_timer == 0:
                self.backspace_timer = 6
                self.stats["txt"] = self.stats["txt"][:len(self.stats["txt"]) - 1]
                Registry.Write("Char", "")
                self.draw()
                self.master.draw()
                return
            if Registry.Read("Char") != "":
                self.stats["txt"] += Registry.Read("Char")
                Registry.Write("Char", "")
                self.draw()
                self.master.draw()


class pallete(component):
    def __init__(self, localPos, order, width, height, color) -> None:
        super().__init__(localPos, order, width, height, color)
        self.iconSize = 30
        self.primary = {}

    def draw(self):
        super().draw()
        maximal = max(list(self.primary.keys()))
        rows = (self.iconSize * len(list(self.primary.keys()))) // (self.stats["w"] + 20) + 1
        columns = (self.stats["w"] - 20) // self.iconSize
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
    def __init__(self, localPos, order, width, height, color, Canvas_lDict: dict) -> None:
        super().__init__(localPos, order, width, height, color)
        self.stats["lyrBh"] = 25
        self.stats["lyrBw"] = 215
        self.lDict = Canvas_lDict
        self.build(Canvas_lDict)

    def build(self, Canvas_lDict):
        for lyr_key in list(Canvas_lDict.keys()):
            self.new_layer()

    def update(self, Canvas_lDict, tool):
        for lyr_key in list(Canvas_lDict.keys()):
            self.components[lyr_key] = lyrBt((5, (self.stats["lyrBh"] + 1) * lyr_key + 5), lyr_key, self.stats["lyrBw"], self.stats["lyrBh"], color_rgb(150, 150, 150), color_rgb(150, 150, 150), color_rgb(200, 200, 200), textPos=(90, 10))
            if tool.layer_selected == lyr_key:
                self.components[lyr_key].stats["f"] = False
        self.draw()

    def del_layer(self, tool):
        del self.components[tool.layer_selected]
        keys = list(self.components.keys())
        for key in keys:
            if key > tool.layer_selected:
                self.components[key - 1] = self.components[key]
                del self.components[key]
        tool.layer_selected -= 1

    def new_layer(self):
        most = cmax(list(self.components.keys()))
        self.components[most + 1] = lyrBt((5, (self.stats["lyrBh"] + 1) * (most + 1) + 5), most + 1, self.stats["lyrBw"], self.stats["lyrBh"], color_rgb(150, 150, 150), color_rgb(150, 150, 150), color_rgb(200, 200, 200), textPos=(90, 10))

    def draw(self):
        self.surf.fill(self.stats["c"])
        highest = cmax(list(self.components.keys()))
        for index in range(highest + 1):
            self.components[index].draw(self.lDict[index].stats)
            self.surf.blit(self.components[index].surf, self.components[index].localPos)
        for index in range(-1, min(list(self.components.keys())) - 1, -1):
            self.components[index].draw()
            self.surf.blit(self.components[index].surf, self.components[index].localPos)

class settings(template):
    def __init__(self, position, master_w, width, master_h, height, color, frame_color) -> None:
        super().__init__(position, master_w, width, master_h, height, color, frame_color)
        self.toggle = False
        self.new_component((0, 0), width, height, color_rgb(150, 150, 150))
        Registry.Write("Settings", self)

class prompt(template):
    def __init__(self, position, master_w, width, master_h, height, color, frame_color, \
                 buttons_text_tuples: list[tuple[button, text]], attached_functions, constructor,
                   id, override = PROMPT_OVERRIDE):
        constructor()
        super().__init__(position, master_w, width, master_h, height, color, frame_color, override)
        button_space = self.new_component((0, 0), width, height, color_rgb(150, 150, 150))
        self.isAlive = True
        for button, text in buttons_text_tuples:
            if button is not None:            
                button_space.link_component(button)
            if text is not None:
                button_space.link_component(text)
        self.attached_functions = attached_functions

        self.info_buffer = []
        self.identifier = id # To allow for custom manipulation

    def prompt_loop(self):
        while self.isAlive:
            Mouse.update(tDict)
            self.handle_events()

            self.display(Window.screen)
            pygame.display.update()
            Clock.tick(Window.framerate)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.contains(Mouse.position):
                    print(Mouse.position)
                    continue
                self.onClick()

    def retrieve(self):
        return (self.info_buffer, self.identifier)

    def kill(self):
        del tDict[-1]
        self.isAlive = False

    # Specific prompts
    def load_prompt(self, postition, width, height, color, frame_color):
        buttons_text_tuples = []
        attached_functions = []

        def CloseFn():
            self.kill()

        def LoadFn():
            pass

        CloseBt = button((10, height - 40), 0, 90, 30, color_rgb(70, 70, 70), color_rgb(120, 120, 120), color_rgb(200, 200, 200), "close", (11, 10))
        CloseBt.attach(CloseFn)
        buttons_text_tuples.append((CloseBt, None))

        LoadBt = button((width - 100, height - 40), 1, 90, 30, color_rgb(70, 70, 70), color_rgb(120, 120, 120), color_rgb(200, 200, 200), "load", (11, 10))
        LoadBt.attach(LoadFn)
        buttons_text_tuples.append((LoadBt, None))

        #_____Graphics_for_directories_____
        #_____FIX_TO_RELATIVE_PATH______#
        def display_directory_items(directory_path: str = "./Gallery") -> None:
            # Draws the contents of directory at <directory_path> on Propmt component
            def fileBtFn():
                return self.stats["txt"] 
            with os.scandir(directory_path) as folder:
                for i, item in enumerate(list(os.scandir(directory_path))):
                    if item.name.startswith('.') or not item.is_file():
                        continue
                    fileBt = button((10, 50 + i * 40), i + 2, 300, 30, color_rgb(70, 70, 70), color_rgb(120, 120, 120), color_rgb(200, 200, 200), \
                                                    item.name, (11, 10))
                    fileBt.attach(fileBtFn)
                    buttons_text_tuples.append((fileBt, None))
                    
        attached_functions.append(display_directory_items)

        Prompt = prompt(postition, Window.winX, width, Window.winY, height, color, frame_color, \
                        buttons_text_tuples, attached_functions, display_directory_items, LOAD_ID)
        self = Prompt
        Prompt.selected_path = None
        Prompt.prompt_loop()