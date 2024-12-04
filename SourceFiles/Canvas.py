from .Color import color_rgba, color_rgb
from .Template import template, cmax
from .Meta import Registry
from .Window import Window
from .Mouse import Mouse
from . import Settings
import pygame

import copy

class layer:
    def __init__(self, order, width, height, pix_w, pix_h) -> None:
        self.order = order
        self.width = width
        self.height = height
        self.pix_w = pix_w
        self.pix_h = pix_h
        self.name = "Layer " + str(order)
        self.grid: list[list[color_rgba]] = []
        self.surf = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.stats = {
            "all" : pix_h * pix_w
        }
        self.build()

    def updateStats(self):
        for index in list(self.stats.keys()):
            if index == "all":
                continue
            self.stats[index] = 0
        # Too Slow, keep track somewhere instead
        for y in range(self.pix_h):
            for x in range(self.pix_w):
                if self.grid[y][x].toTuple() not in list(self.stats.keys()):
                    self.stats[self.grid[y][x].toTuple()] = 1
                    continue
                self.stats[self.grid[y][x].toTuple()] += 1

    def build(self):
        for i in range(1, self.pix_h + 1):
            arr = []
            for j in range(1, self.pix_w + 1):
                arr.append(color_rgba(0, 0, 0, 0))
            self.grid.append(arr)

    def build_background(self):
        for i in range(self.pix_h):
            for j in range(self.pix_w):
                if (i + j) % 2:
                    self.grid[i][j] = color_rgba(200, 200, 200, 255)
                else:
                    self.grid[i][j] = color_rgba(155, 155, 155, 255)
        self.draw()

    def draw(self):
        for y in range(self.pix_h):
            for x in range(self.pix_w):
                pygame.draw.rect(self.surf, self.grid[y][x].toTuple(), pygame.Rect(x * self.width / self.pix_w, y * self.height / self.pix_h, self.width / self.pix_w, self.height / self.pix_h))
        # self.updateStats()

    def change_pixel(self, pixelPos, newColor: color_rgba, tDict = None, screen = None):
        "PixelPos is in (x, y) form x,y are ints"
        x, y = pixelPos
        self.grid[y][x] = newColor
        # self.draw()

    def show(self):
        for i in range(self.pix_h):
            for j in range(self.pix_w):
                self.grid[i][j].show()


class canvas(template):
    def __init__(self, position, screen_w, width, screen_h, height, pix_dim, override = None) -> None:
        super().__init__(position, screen_w, width, screen_h, height, color_rgb(0, 0, 0), color_rgb(50, 50, 50), override)
        self.pix_w = pix_dim[0]
        self.pix_h = pix_dim[1]
        self.lDict: dict[int, layer] = {}

        Registry.Write("Canvas", self)

        self.new_layer()
        self.lDict[0].build_background()

        self.new_layer()

    def get_raw(self) -> dict[str, list[list[color_rgba]]]:
        "keys are strings for compatibility with json"
        res = {}
        for key_, layer_ in self.lDict.items():
            if key_ == 0:
                continue
            res[key_] = layer_.grid
        return res

    def new_layer(self):
        keys = list(self.lDict.keys())
        new_layer_order = cmax(keys) + 1
        self.lDict[new_layer_order] = layer(new_layer_order, self.stats["w"], self.stats["h"], self.pix_w, self.pix_h)
        self.lDict[new_layer_order].draw()
        return new_layer_order

    def del_layer(self, layer_order):
        del self.lDict[layer_order]
        keys = list(self.lDict.keys())
        for key in keys:
            if key > layer_order:
                self.lDict[key - 1] = self.lDict[key]
                del self.lDict[key]

    def create_frame(self):
        returnDict = copy.deepcopy(self.lDict)
        del returnDict[0]
        return returnDict

    def display(self, screen: pygame.Surface):
        highest = max(list(self.lDict.keys()))
        for index in range(highest + 1):
            self.surf.blit(self.lDict[index].surf, (0, 0))
        pygame.draw.rect(screen, self.stats["fc"], pygame.Rect(self.position[0] - 5, self.position[1] - 5, self.stats["w"] + 10, self.stats["h"] + 10))
        screen.blit(self.surf, self.position)

    def transform(self, position):
        "Returns position in Canvas <Pixel> Space as (x, y)"
        return (int((position[0] - self.position[0]) / (self.stats["w"] / self.pix_w)), int((position[1] - self.position[1]) / (self.stats["h"] / self.pix_h)))

    def draw_with_tool(self, lyr_mngr, tDict = None, screen = None):
        if not Mouse.state["isDown"]:
            return

        if not self.contains(Mouse.position):
            return

        if len(Mouse.occupation) > 1:
            return

        if Mouse.state["LWR"][2]:
            self.lDict[Mouse.layer_selected].change_pixel(self.transform(Mouse.position), color_rgba(), tDict, screen)
            lyr_mngr.update(self.lDict, Mouse)
            return

        if Mouse.state["visualM"]:
            Mouse.tool.onUseVisual(self.transform(Mouse.position), tDict, screen)
        else:
            Mouse.tool.onUse(self.transform(Mouse.position), tDict, screen)
        #self.lDict[mouse.layer_selected].change_pixel(self.transform(mouse.position), mouse.color)
        lyr_mngr.update(self.lDict, Mouse)

Canvas = canvas((Window.winX / 3 + 50, Window.winY / 4 - 30), Window.winX, 500, Window.winY, 500, \
                Settings.Get("Project", "CanvasMeta"))

def rebuild_canvas(position: list[int], screen_w, width, screen_h, height, pix_dim: list[int]):
    print("rebuild called")
    Canvas = canvas(position, screen_w, width, screen_h, height, pix_dim, 0)
#___________________Canvas_Attach_Functions___________________#

def Reflect(BtObject):
    for layer_ in Canvas.lDict.keys():
        if layer_ == 0:
            continue
        if Canvas.lDict[layer_].pix_w % 2 == 1:
            new_grid = []
            for i in range(Canvas.lDict[layer_].pix_h):
                arr = []
                for j in range(Canvas.lDict[layer_].pix_w):
                    arr.append(Canvas.lDict[layer_].grid[i][-j - 1])
                new_grid.append(arr)
    
        Canvas.lDict[layer_].grid = new_grid
        Canvas.lDict[layer_].draw()
    
    Canvas.display(Window.screen)
#___________________________TOOLS_____________________________#


class tool:
    def __init__(self) -> None:
        pass

    def onUseVisual(self, transformed_position, tDict = None, screen = None):
        self.onUse(transformed_position)

class pencil(tool):
    def __init__(self) -> None:
        super().__init__()

    def onUse(self, transformed_position, tDict = None, screen = None):
        Canvas.lDict[Mouse.layer_selected].change_pixel(transformed_position, Mouse.color)

Pencil = pencil()

class bucket(tool):
    def __init__(self) -> None:
        super().__init__()

    def onUseVisual(self, gridPos, tDict, screen):
        gridOb: list[list[color_rgba]] = Canvas.lDict[Mouse.layer_selected].grid
        x, y = gridPos
        allowed_colors = [gridOb[y][x].toTuple()]

        inactive: list[tuple[int, int]] = []
        active: list[tuple[int, int]] = [gridPos]

        width: int = Canvas.lDict[Mouse.layer_selected].pix_w
        height: int = Canvas.lDict[Mouse.layer_selected].pix_h

        while active != []:
            x, y = active[0]
            inactive.append(active[0])
            
            Canvas.lDict[Mouse.layer_selected].change_pixel((x, y), Mouse.color)
            for index in range(max(list(tDict.keys())) + 1):
                if not tDict[index].toggle:
                    continue
                tDict[index].display(screen)
            Registry.Read("LayerManager").draw()
            pygame.display.update()

            for i in [-1, 1]:
                if y + i < 0 or y + i >= height:
                    continue
                if gridOb[y + i][x].toTuple() not in allowed_colors or (x, y + i) in inactive:
                    continue
                if (x, y + i) not in active:
                    active.append((x, y + i))
            for j in [-1, 1]:
                if x + j < 0 or x + j >= width:
                    continue
                if gridOb[y][x + j].toTuple() not in allowed_colors or (x + j, y) in inactive:
                    continue
                if (x + j, y) not in active:
                    active.append((x + j, y))
            active.pop(0)


    def onUse(self, gridPos, tDict = None, screen = None):
        gridOb: list[list[color_rgba]] = Canvas.lDict[Mouse.layer_selected].grid
        x, y = gridPos
        allowed_colors = [gridOb[y][x].toTuple()]

        inactive: list[tuple[int, int]] = []
        active: list[tuple[int, int]] = [gridPos]

        width: int = Canvas.lDict[Mouse.layer_selected].pix_w
        height: int = Canvas.lDict[Mouse.layer_selected].pix_h

        while active != []:
            x, y = active[0]
            inactive.append(active[0])
            Canvas.lDict[Mouse.layer_selected].change_pixel((x, y), Mouse.color)
            for i in [-1, 1]:
                if y + i < 0 or y + i >= height:
                    continue
                if gridOb[y + i][x].toTuple() not in allowed_colors or (x, y + i) in inactive:
                    continue
                if (x, y + i) not in active:
                    active.append((x, y + i))
            for j in [-1, 1]:
                if x + j < 0 or x + j >= width:
                    continue
                if gridOb[y][x + j].toTuple() not in allowed_colors or (x + j, y) in inactive:
                    continue
                if (x + j, y) not in active:
                    active.append((x + j, y))
            active.pop(0)

Bucket = bucket()