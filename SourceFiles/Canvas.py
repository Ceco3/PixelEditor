from .Color import color_rgba, color_rgb
from .Template import template, cmax, tDict
from .Meta import Registry, Updater
from .Window import Window
from .Mouse import Mouse
from . import Settings

# Forbidden Imports:
# Tapestry

import pygame
import copy

class layer:
    def __init__(self, order, width, pix_w, height, pix_h, master: 'canvas') -> None:
        Updater.Add(self)
        self.order = order
        self.width = width
        self.height = height
        self.pix_w = pix_w
        self.pix_h = pix_h
        self.master = master
        self.name = "Layer " + str(order)
        self.grid: list[list[color_rgba]] = []
        self.surf = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.stats = {
            'bw' : False
        }
        self.color_data: dict[tuple, int] = { # This does not work for the 0 layer
            "size": pix_w * pix_h,
            (0, 0, 0, 0): pix_w * pix_h
        }
        self.lasso_volume: set[tuple[int, int]] = set()
        self.build()

    def Update(self):
        "Expensive O(n^2)"
        # Find better implementation?
        if Mouse.tool != Lasso or not Lasso.isUsed or Mouse.layer_selected != self.order:
            return
        
        o_x, o_y = Lasso.origin
        w, h = Lasso.dimensions
        for l_y in range(o_y, o_y + h):
            for l_x in range(o_x, o_x + w):
                self.lasso_volume.add((l_x, l_y))

    def get_raw(self) -> dict[int, list[tuple[int, int, int, int]]]:
        "Expensive O(n^2)"
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
                if self.stats['bw'] or self.master.stats['bw']:
                    color = self.grid[y][x].copy()
                    grayScale = int(color.r * 0.299 + color.g * 0.587 + color.b * 0.114)
                    color.r = grayScale; color.g = grayScale; color.b = grayScale
                elif (x, y) in self.lasso_volume:
                    color = self.grid[y][x] + Lasso.select_volume_color
                else:
                    color = self.grid[y][x]
                pygame.draw.rect(self.surf, color.toTuple(), pygame.Rect(x * self.width / self.pix_w, y * self.height / self.pix_h,
                                                                                self.width / self.pix_w, self.height / self.pix_h))

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

    def reload_color_data(self):
        "Expensive O(n^2)"

        self.color_data = {
            "size" : self.pix_w * self.pix_h
        }

        for y in range(self.pix_h):
            for x in range(self.pix_w):
                color_xy = self.grid[y][x].toTuple()
                if color_xy not in self.color_data:
                    self.color_data[color_xy] = 0
                self.color_data[color_xy] += 1

    # Debug
    def show(self):
        for i in range(self.pix_h):
            for j in range(self.pix_w):
                self.grid[i][j].show()


class canvas(template):
    def __init__(self, layout_uname: str, width, height, pix_dim,
                  tDict_override = None, color_override = None) -> None:
        super().__init__(layout_uname, width, height, tDict_override, color_override=[[0, 0, 0], [50, 50, 50]])
        self.pix_w = pix_dim[0]
        self.pix_h = pix_dim[1]
        self.stats['bw'] = False # Black and White
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
        self.lDict[new_layer_order] = layer(new_layer_order, self.stats['w'], self.pix_w, self.stats['h'], self.pix_h, self)
        self.lDict[new_layer_order].draw()
        return new_layer_order

    def del_layer(self, layer_order):
        del self.lDict[layer_order]
        keys = list(self.lDict.keys())
        for key in keys:
            if key > layer_order:
                self.lDict[key - 1] = self.lDict[key]
                del self.lDict[key]

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

        if Mouse.state["visualM"]:
            Mouse.tool.onUseVisual(self.transform(Mouse.position), tDict, screen)
        else:
            Mouse.tool.onUse(self.transform(Mouse.position), tDict, screen)
        #self.lDict[mouse.layer_selected].change_pixel(self.transform(mouse.position), mouse.color)
        lyr_mngr.update()

Canvas = canvas("Canvas", 500, 500, Settings.Get("Project", "CanvasMeta"))


def new_canvas(position: tuple[int, int], width, height, pix_dim: tuple[int, int], tDict_override = None, color_override = None):
    global Canvas
    Canvas = canvas(position, width, height, pix_dim, tDict_override, color_override)

def switch_canvas(new_canvas: canvas):
    global Canvas
    Canvas = new_canvas
    tDict[0] = Canvas

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
            for i in range(Layer.pix_h):
                arr = []
                for j in range(Layer.pix_w):
                    arr.append(Layer.grid[-i - 1][j])
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
        if Mouse.pix_width == 1:
            if Mouse.state["LWR"][2]:
                Canvas.lDict[Mouse.layer_selected].change_pixel(transformed_position, color_rgba())
                return
            Canvas.lDict[Mouse.layer_selected].change_pixel(transformed_position, Mouse.color)
            return

        x_i, y_i = transformed_position
        x_o, y_o = x_i - Mouse.pix_width // 2, y_i - Mouse.pix_width // 2
        for d_x in range(Mouse.pix_width):
            for d_y in range(Mouse.pix_width):
                if x_o + d_x < 0 or x_o + d_x >= Canvas.pix_w:
                    continue
                if y_o + d_y < 0 or y_o + d_y >= Canvas.pix_h:
                    continue
                if Mouse.state["LWR"][2]:
                    Canvas.lDict[Mouse.layer_selected].change_pixel((x_o + d_x, y_o + d_y), color_rgba())
                    continue
                Canvas.lDict[Mouse.layer_selected].change_pixel((x_o + d_x, y_o + d_y), Mouse.color)

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
            Canvas.lDict[Mouse.layer_selected].draw()
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

class lasso(tool):
    def __init__(self):
        Updater.Add(self)
        super().__init__()
        self.origin: tuple[int, int] = ()
        self.dimensions:tuple[int, int] = ()
        self.isUsed: bool = False
        self.select_volume_color = color_rgba(60, 60, 60, 60)

    def onUse(self, transformed_position, tDict = None, screen = None):
        if Mouse.state["LWR"][2]:
            self.isUsed = False
            self.origin = ()
            self.dimensions = ()
            return
        self.isUsed = True
        self.origin = transformed_position
        self.dimensions = transformed_position
    
    def Update(self):
        if not self.isUsed:
            return
        
        m_x, m_y = Canvas.transform(Mouse.position)
        o_x, o_y = self.origin
        self.dimensions = (m_x - o_x, m_y - o_y)

Lasso = lasso()