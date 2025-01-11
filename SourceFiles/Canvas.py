from .Color import color_rgba, color_rgb
from .Template import template, cmax
from .Meta import Registry
from .Window import Window
from .Mouse import Mouse
from . import Settings
import pygame

# Forbidden Imports:
# Tapestry

import copy

class layer:
    def __init__(self, order, width, pix_w, height, pix_h) -> None:
        self.order = order
        self.width = width
        self.height = height
        self.pix_w = pix_w
        self.pix_h = pix_h
        self.name = "Layer " + str(order)
        self.grid: list[list[color_rgba]] = []
        self.surf = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.stats = {}
        self.color_data: dict[tuple, int] = { # This does not work for the 0 layer
            "size": pix_w * pix_h,
            (0, 0, 0, 0): pix_w * pix_h
        }
        self.build()

    def get_raw(self) -> dict[int, list[tuple[int, int, int, int]]]:
        res = {}
        i = 0
        for row in self.grid:
            res[i] = []
            j = 0
            for pixel in row:
                res[i].append(pixel.toTuple())
                j += 1
            i += 1
        return res

    def build(self):
        for _ in range(self.pix_h):
            arr = []
            for _ in range(self.pix_w):
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

    def change_pixel(self, pixelPos, newColor: color_rgba):
        "PixelPos is in (x, y) form x,y are ints"
        x, y = pixelPos
        oldColor: color_rgba = self.grid[y][x]
        self.color_data[oldColor.toTuple()] -= 1
        if newColor.toTuple() not in self.color_data:
            self.color_data[newColor.toTuple()] = 0
        self.color_data[newColor.toTuple()] += 1
        self.grid[y][x] = newColor
        # self.draw()

    def show(self):
        for i in range(self.pix_h):
            for j in range(self.pix_w):
                self.grid[i][j].show()


class canvas(template):
    def __init__(self, position, screen_w, width, screen_h, height, pix_dim, override = None) -> None:
        super().__init__(position, screen_w, width, screen_h, height, override, color_override=[[0, 0, 0], [50, 50, 50]])
        self.pix_w = pix_dim[0]
        self.pix_h = pix_dim[1]
        self.lDict: dict[int, layer] = {}

        Registry.Write("Canvas", self)

        self.new_layer()
        self.lDict[0].build_background()

        self.new_layer()

    def get_raw(self) -> dict[str, list[list[tuple[int, int, int, int]]]]:
        "keys are strings for compatibility with json"
        res = {}
        for key_, layer_ in self.lDict.items():
            if key_ == 0:
                continue
            res[key_] = layer_.get_raw()
        return res

    def new_layer(self):
        keys = list(self.lDict.keys())
        new_layer_order = cmax(keys) + 1
        self.lDict[new_layer_order] = layer(new_layer_order, self.stats['w'], self.pix_w, self.stats['h'], self.pix_h)
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
            self.lDict[Mouse.layer_selected].change_pixel(self.transform(Mouse.position), color_rgba())
            lyr_mngr.update()
            return

        if Mouse.state["visualM"]:
            Mouse.tool.onUseVisual(self.transform(Mouse.position), tDict, screen)
        else:
            Mouse.tool.onUse(self.transform(Mouse.position), tDict, screen)
        #self.lDict[mouse.layer_selected].change_pixel(self.transform(mouse.position), mouse.color)
        lyr_mngr.update()

Canvas = canvas((Window.winX / 3 + 50, Window.winY / 4 - 30), Window.winX, 500, Window.winY, 500, \
                Settings.Get("Project", "CanvasMeta"))



def aux_rescale_x(Layer: layer, new_pix_w: int, isGreater: bool) -> None:
    for row_idx in range(len(Layer.grid)):
        for _ in range(abs(new_pix_w - Layer.pix_w)):
            if not isGreater:
                Layer.grid[row_idx].append(color_rgba(0, 0, 0, 0))
                continue
            Layer.grid[row_idx].pop()

def rescale_canvas(position: list[int], screen_w, width, screen_h, height, pix_dim: list[int]):
    global Canvas
    pix_w, pix_h = pix_dim

    for layer in Canvas.lDict.values():
        if layer.pix_w < pix_w:
            aux_rescale_x(layer, pix_w, False)
        if layer.pix_w > pix_w:
            aux_rescale_x(layer, pix_w, True)
        if layer.pix_h < pix_h:
            for _ in range(pix_h - layer.pix_h):
                row = []
                for _ in range(pix_w):
                    row.append(color_rgba(0, 0, 0, 0))
                layer.grid.append(row)
        if layer.pix_h > pix_h:
            for _ in range(abs(pix_h - layer.pix_h)):
                layer.grid.pop()
        layer.pix_w = pix_w
        layer.pix_h = pix_h
        layer.surf.fill((0, 0, 0))
        layer.draw()
    
    Canvas.lDict[0].pix_w = pix_w
    Canvas.lDict[0].pix_h = pix_h
    Canvas.lDict[0].build_background()

    Canvas.pix_w = pix_w
    Canvas.pix_h = pix_h

#___________________Canvas_Attach_Functions___________________#

def Reflect(BtObject, horizontal: bool):
    for Layer in Canvas.lDict.values():
        if Layer.order == 0:
            continue

        if horizontal:
            new_grid = []
            for i in range(Layer.pix_h):
                arr = []
                for j in range(Layer.pix_w):
                    arr.append(Layer.grid[i][-j - 1])
                new_grid.append(arr)
        
            Layer.grid = new_grid
            Layer.draw()

        if not horizontal:
            new_grid = []
            for i in range(Layer.pix_w):
                arr = []
                for j in range(Layer.pix_h):
                    arr.append(Layer.grid[i][-j - 1])
                new_grid.append(arr)
        
            Layer.grid = new_grid
            Layer.draw()
    
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