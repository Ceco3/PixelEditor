from .Template import template, component, tDict, slide_panel
from .Color import toRgba, color_rgba, color_rgb
from . import Canvas
from .Canvas import new_canvas, switch_canvas, Shader, canvas
from .Meta import Registry, Updater
from .Mouse import Mouse
from .ComF import cmax, validate_string, Clamp
from .Window import Window
from .Button import lyrBt, button, knob, sliderBt, frmBt, text
from . import Settings
from .Prompt import prompt

from itertools import takewhile
import cv2, os
import pygame

AUTOSAVE = pygame.USEREVENT + 6
AUTOSAVE_EV = pygame.event.Event(AUTOSAVE)

def load_img(path, target_canvas: canvas | None = None) -> list[list[color_rgba]]:
    if ".png" not in path:
        path += ".png"
    bgra_content = cv2.imread(path, -1)

    if target_canvas is None:
        target_canvas = Canvas.Canvas # Default

    if bgra_content is None:
        # Pop up Ideally
        return target_canvas.lDict[Mouse.layer_selected].grid

    gridObject = []

    height = len(bgra_content)
    width = len(bgra_content[0])

    for y in range(height):
        row = []
        for x in range(width):
            row.append(color_rgba(int(bgra_content[y][x][2]), int(bgra_content[y][x][1]), int(bgra_content[y][x][0]), int(bgra_content[y][x][3])))
        gridObject.append(row)

    target_canvas.rescale((Window.winX / 3 + 50, Window.winY / 4 - 30), Window.winX, 500, Window.winY, 500, [width, height])
    name = list(takewhile(lambda x: x != "\\" and x != "/", path[::-1]))
    name.reverse()
    name = ''.join(name)
    name = name.replace(".png", '')
    if target_canvas == Canvas.Canvas:
        Settings.Set("Project", "Name", name)

    return gridObject

def load_anim():
    pass

def load():
    ret_info, _ = prompt.load_prompt(None, (Window.winX / 2 - 250, Window.winY / 2 - 175), 500, 350)

    if ret_info is None:
        # Pop up Ideally
        return # Canvas.Canvas.lDict[Mouse.layer_selected].grid
    path: str = ret_info[0]        

    if len(ret_info) >= 3 and ret_info[2]: # LoadAnim
        FrameManager: frame_mngr = Registry.Read("FrameManager")
        for item in os.listdir(path):
            Canvas.Canvas.lDict[Mouse.layer_selected].grid = load_img(path + '/' + item)
            Canvas.Canvas.lDict[Mouse.layer_selected].reload_color_data()
            Canvas.Canvas.lDict[Mouse.layer_selected].draw()
            FrameManager.add_frame(False)

    else: # LoadImg
        Canvas.Canvas.lDict[Mouse.layer_selected].grid = load_img(path)
        Canvas.Canvas.lDict[Mouse.layer_selected].reload_color_data()
        Canvas.Canvas.lDict[Mouse.layer_selected].draw()

    if len(ret_info) >= 2 and ret_info[1]:
        Pallete: pallete = Registry.Read("Pallete")
        for color_tpl in Canvas.Canvas.lDict[Mouse.layer_selected].color_data:
            if isinstance(color_tpl, str):
                continue

            if color_tpl not in Pallete.primary and color_tpl != (0, 0, 0, 0):
                Pallete.new_color(color_rgba(*color_tpl))
        Pallete.draw()

def load_pallete(name: str) -> 'pallete':
    raw_pallete = Settings.Get("Palletes", name)
    Pallete = pallete((0, 0), 0, 230, 150)
    for color in raw_pallete:
        Pallete.new_color(toRgba(color))
    
    return Pallete

def bound(x, y):
    if x < y:
        return x
    return y

class pallete(component):
    def __init__(self, localPos, order, width, height) -> None:
        super().__init__(localPos, order, width, height)
        self.iconSize = 30
        self.primary: list[tuple[int, int, int, int]] = []

    def draw(self):
        super().draw()
        maximal = len(self.primary) - 1
        columns = (self.stats['w'] - 20) // self.iconSize
        rows = (len(self.primary) // columns) + 1
        for y in range(rows):
            for x in range(columns):
                if x + columns * y > maximal:
                    return
                pygame.draw.rect(self.surf, self.primary[x + columns * y], pygame.Rect(self.iconSize * x + 10, self.iconSize * y + 10, self.iconSize, self.iconSize))

    def new_color(self, color: color_rgba):
        self.primary.append(color.toTuple())

    def onClick(self, localMousePos):
        left, _, right = Mouse.state['LWR']
        columns = bound(len(self.primary) , (self.stats["w"] - 20) // self.iconSize)
        x = localMousePos[0] - 10
        y = localMousePos[1] - 10
        x = x - x % self.iconSize
        y = y - y % self.iconSize
        x //= self.iconSize
        y //= self.iconSize
        try:
            if left:
                Mouse.color = toRgba(self.primary[x + columns * y])
            if right:
                del self.primary[x + columns * y]
                self.draw()
        except:
            pass

class color_picker(component):
    def __init__(self, localPos, order, width, height, bound_pallete: pallete, color_override=None):
        super().__init__(localPos, order, width, height, color_override)
        Updater.Add(self)
        self.prewiev = [0, 0, 0, 255]
        self.bound_pallete = bound_pallete
        r_knob = knob((100, 10), 0, 100, 30)
        g_knob = knob((100, 50), 1, 100, 30)
        b_knob = knob((100, 90), 2, 100, 30)

        def pick_color(BtObject):
            if tuple(self.prewiev) in self.bound_pallete.primary:
                return  

            new_color = toRgba(self.prewiev)
            bound_pallete.new_color(new_color)
            Mouse.color = new_color
        pick_button = button((20, 45), 4, 40, 40, attachFn=pick_color)

        self.link_multi(r_knob, g_knob, b_knob, pick_button)
        self.repaint_preview()
    
    def Update(self):
        for knob in self.components.values():
            if knob.isClicked:
                self.repaint_preview()

    def draw(self):
        super().draw()
        self.bound_pallete.draw()
        pygame.draw.rect(self.surf, [100, 100, 100], pygame.Rect(15, 40, 50, 50))
        pygame.draw.rect(self.surf, self.prewiev, pygame.Rect(20, 45, 40, 40))

    def repaint_preview(self):
        color = [0, 0, 0, 255]
        for color_knob in self.components.values():
            if color_knob.order == 4:
                continue
            color[color_knob.order] = int(color_knob.value * 255)
        self.prewiev = color

class shade_picker(component):
    def __init__(self, localPos, order, width, height, color_override=None):
        super().__init__(localPos, order, width, height, color_override)
        Updater.Add(self)
        def resBtFn( _ ):
            self.components[2].reset()
            Mouse.brightness = 0.5
        resBt = button((10, 10), 0, 30, 30, attachFn=resBtFn)
        resBt.loadIcon('Repeat.png')
        def layBtFn( _ ):
            Shader.layers = not Shader.layers
        layBt = button((50, 10), 1, 30, 30, attachFn=layBtFn)
        layBt.loadIcon('Layers.png')
        brightness = knob((90, 5), 2, 100, 30)

        self.link_multi(resBt, layBt, brightness)

    def Update(self):
        if self.components[2].isClicked:
            Mouse.brightness = self.components[2].value

class thick_picker(component):
    def __init__(self, localPos, order, width, height, color_override=None):
        super().__init__(localPos, order, width, height, color_override)
        Updater.Add(self)
        def resBtFn( _ ):
            self.components[1].reset(0.1)
            Mouse.thickness = 1
        resBt = button((10, 10), 0, 30, 30, attachFn=resBtFn)
        resBt.loadIcon('Repeat.png')
        thickness = knob((50, 5), 1, 200, 30)
        thickness.value = 0.1

        self.link_multi(resBt, thickness)

    def Update(self):
        if self.components[1].isClicked:
            Mouse.thickness = int(self.components[1].value * 10)

class layer_mngr(component):
    def __init__(self, localPos, order, width, height) -> None:
        Updater.Add(self)
        super().__init__(localPos, order, width, height)
        self.stats["lyrBh"] = 25
        self.stats["lyrBw"] = 215
        self.build()

    def build(self):
        for lyr_key in Canvas.Canvas.lDict:
            self.new_layer()

    def Update(self):
        if Mouse.layerBtHeld is None:
            return

        selBt: lyrBt = self.components[Mouse.layerBtHeld]
        selBt.localPos = (5, Mouse.position[1] - self.localPos[1] - self.master.position[1] - selBt.heldOffset[1])
        _, y = selBt.localPos
        if y > (self.stats["lyrBh"] + 1) * (selBt.order - 1) + 5 and selBt.order != max(self.components.keys()):
            nextBt: lyrBt = self.components[selBt.order + 1]
            nextLyr = Canvas.Canvas.lDict[selBt.order + 1]
            self.components[selBt.order + 1] = selBt
            self.components[selBt.order] = nextBt
            Canvas.Canvas.lDict[selBt.order + 1] = Canvas.Canvas.lDict[selBt.order]
            Canvas.Canvas.lDict[selBt.order] = nextLyr
            nextBt.order -= 1
            selBt.order  += 1
            Mouse.layerBtHeld += 1

            nextBt.localPos = (5, (self.stats["lyrBh"] + 1) * (selBt.order - 2) + 5)

        if Clamp(0, self.stats['h'], y) < (self.stats["lyrBh"] + 1) * (selBt.order - 2) + 5 and selBt.order != 1:
            prevBt: lyrBt = self.components[selBt.order - 1]
            prevLyr = Canvas.Canvas.lDict[selBt.order - 1]
            self.components[selBt.order - 1] = selBt
            self.components[selBt.order] = prevBt
            Canvas.Canvas.lDict[selBt.order - 1] = Canvas.Canvas.lDict[selBt.order]
            Canvas.Canvas.lDict[selBt.order] = prevLyr
            prevBt.order += 1
            selBt.order  -= 1
            Mouse.layerBtHeld -= 1

            prevBt.localPos = (5, (self.stats["lyrBh"] + 1) * (selBt.order) + 5)
        
        selBt.draw(Canvas.Canvas.lDict[Mouse.layer_selected].color_data)
        self.draw()

    def update(self):
        for lyr_key in Canvas.Canvas.lDict:
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
        self.link_component(lyrBt((5, (self.stats["lyrBh"] + 1) * (most) + 5), most + 1, self.stats["lyrBw"], self.stats["lyrBh"],
                                           textPos=(90, 10), color_override=color_override))

    def draw(self):
        self.surf.fill(self.stats["c"])
        for component in self.components.values():
            if component.order < 0:
                component.draw()
                self.surf.blit(component.surf, component.localPos)
            if component.order > 0:
                component.draw(Canvas.Canvas.lDict[component.order].color_data)
                self.surf.blit(component.surf, component.localPos)

class frame_mngr(slide_panel):
    def __init__(self, localPos, order, width, height, big_width, big_height, sliderBt, horizontal=False, color_override=None):
        super().__init__(localPos, order, width, height, big_width, big_height, sliderBt, horizontal, color_override)
        self.curr_frame = 0
        self.pic_size = 90
        self.last_id = 0
        self.play_speed: float = 15 # FPS (this does not work)
        self.play_backwards = False

    def remove_frame(self, uid: int):
        self.components[uid] = None
        last_key = 0
        for key in self.components:
            if key > uid:
                self.components[key - 1] = self.components[key]
                self.components[key - 1].uid -= 1
                self.components[key - 1].order -= 1
                x_o, y_o = self.components[key].localPos
                self.components[key - 1].localPos = (x_o - self.pic_size - 15, y_o)
                self.components[key - 1].og_pos = (x_o - self.pic_size - 15, y_o)
            if self.components.get(key + 1) is None:
                last_key = key
        del self.components[last_key]
        self.last_id -= 1
        self.draw()

    def add_frame(self, copy_last: bool = True):
        # build_canvas(True, self.last_id + 1)
        FrameBt = frmBt((15 + self.pic_size * self.last_id + 15 * self.last_id - self.cutoff, 10),
                         self.last_id + 1, self.pic_size, self.pic_size, self.last_id + 1, Canvas.Canvas)
        new_canvas(Canvas.Canvas.position, Canvas.Canvas.stats['w'], Canvas.Canvas.stats['h'],
                    (Canvas.Canvas.pix_w, Canvas.Canvas.pix_h), Canvas.Canvas.order, copy_last=copy_last)
        self.link_component(FrameBt)
        self.last_id += 1

    def play(self):
        self.curr_frame = (self.curr_frame + (1 if not self.play_backwards else -1)) % (len(self.components))
        if self.curr_frame == 0 and not self.play_backwards:
            self.curr_frame += 1
        if self.curr_frame == len(self.components) - 1 and self.play_backwards:
            self.curr_frame -= 1
        switch_canvas(self.components[self.curr_frame].bound_canvas)

    def draw(self):
        self.surf.fill(self.stats['c'])
        for FrmBt in self.components.values():
            if not isinstance(FrmBt, frmBt):
                continue
            pygame.draw.rect(self.surf, self.master.stats['c'],
                              pygame.Rect(25 * (1 + self.cutoff / 800) + self.pic_size * (FrmBt.uid - 1) + 12 * (FrmBt.uid - 1) - self.cutoff, 5,
                                            self.pic_size, self.pic_size))
        # pygame.draw.rect(self.surf, [170, 50, 50], pygame.Rect())
        for Component in self.components.values(): # Todo: implement culling
                Component.draw()
                if Component.order == 0:
                    self.surf.blit(Component.surf, Component.localPos)
                    continue
                self.surf.blit(Component.surf, self.adjust(Component.localPos))

class lookup_mngr(component):
    def __init__(self, localPos, order, width, height, color_override=None):
        super().__init__(localPos, order, width, height, color_override)
        self.bound_canvas: canvas | None = canvas((0, 0), 140, 140, (1, 1), tDict_override=False)
        loadBt = button((self.stats['w'] - 70, 10), 0, 60, 30, 'load', (11, 10), attachFn=self.load_lookup)
        self.link_component(loadBt, False)

    def load_lookup(self, _ ):
        ret_info, _ = prompt.load_prompt(None, (Window.winX / 2 - 250, Window.winY / 2 - 175), 500, 350)
        if ret_info is None:
            # Pop up Ideally
            return # Canvas.Canvas.lDict[Mouse.layer_selected].grid
        path: str = ret_info[0]

        self.bound_canvas.lDict[Mouse.layer_selected].grid = load_img(path, self.bound_canvas)
        self.bound_canvas.lDict[Mouse.layer_selected].reload_color_data()
        self.bound_canvas.lDict[Mouse.layer_selected].draw()
        self.bound_canvas.display(Window.screen)
        self.draw()

    def draw(self):
        self.surf.fill(self.stats['c'])
        pygame.draw.rect(self.surf, self.master.stats['c'], pygame.Rect(10, 10, 140, 140))
        if self.bound_canvas is not None:
            self.surf.blit(pygame.transform.scale(self.bound_canvas.surf, (140, 140)), (10, 10))
        for Component in self.components.values(): # Todo: implement culling
            Component.draw()
            self.surf.blit(Component.surf, Component.localPos)

class radar(template):
    # Add some functionality for making this invisible as it is not always useful
    def __init__(self, position, master_w, width, master_h, height, tDict_override=None, color_override=None):
        super().__init__(position, master_w, width, master_h, height, tDict_override, color_override)
        Updater.Add(self)
        self.new_component((0, 0), self.stats['w'], self.stats['h'], color_override)
        xTxt = text((0, 0), 0, self.stats['w'] / 2, self.stats['h'], '0', (3, 10), color_override)
        yTxt = text((self.stats['w'] / 2, 0), 1, self.stats['w'] / 2, self.stats['h'], '0', (3, 10), color_override)
        self.components[0].link_multi(xTxt, yTxt)

    def Update(self):
        if len(Mouse.occupation) != 1 or Canvas.Canvas not in Mouse.occupation:
            return
        
        x, y = Canvas.Canvas.transform(Mouse.position)
        self.components[0].components[0].renew_txt(str(x))
        self.components[0].components[1].renew_txt(str(y))
        self.components[0].draw()

I_SHAPE = 0
DASH_SHAPE = 1

class selection(template):
    def __init__(self, position, master_w, master_h, button_fns: list[button], button_icon_paths: list[str], button_dim: int,
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
        self.selected_bt = 0
        self.new_component((0, 0), width, height)
        self.populate(button_fns, button_icon_paths)
    
    def populate(self, button_fns: list[button], button_icn_pths: list[str]):
        if self.shape == I_SHAPE:
            gap = (1/6) * self.button_dim
            for i, function in enumerate(button_fns):
                Button = button((5 + gap, 5 + gap + i * (self.button_dim + gap)), i, self.button_dim, self.button_dim,
                                attachFn=function)
                Button.loadIcon(button_icn_pths[i])
                self.components[0].link_component(Button)
        if self.shape == DASH_SHAPE:
            pass

class pallete_selector(template):
    def __init__(self, position, master_w, width, master_h, height, tDict_override=None, color_override=None):
        super().__init__(position, master_w, width, master_h, height, tDict_override, color_override)
        self.pallete_num: int = len(Settings.Get("Palletes", None))
        slider = sliderBt((10, 10), 0, 10, 50)
        self.slide_panel = slide_panel((0, 0), 0, width, height, width, height, slider)

    def display(self, master_surf: pygame.Surface):
        pass

BUILD = pygame.USEREVENT + 2
BUILD_EV = pygame.event.Event(BUILD)

LOAD = pygame.USEREVENT + 3
LOAD_EV = pygame.event.Event(LOAD)

class file(template):
    def __init__(self, position, master_w, width, master_h, height, tDict_override=None, color_override=None):
        super().__init__(position, master_w, width, master_h, height, tDict_override, color_override)
        self.toggle = False
        self.panel = component((0, 0), 0, self.stats['w'], self.stats['h'])
        self.saveBt: button = button((10, 10), 0, 60, 30, "save", textPos = (11, 10), attachFn=lambda _ : pygame.event.post(BUILD_EV))
        self.loadBt: button = button((10, 55), 1, 60, 30, "load", textPos = (11, 10), attachFn=lambda _ : pygame.event.post(LOAD_EV))
        self.clearBt: button = button((10, 100), 2, 60, 30, 'clear', textPos=(6, 10), attachFn=lambda _ : Canvas.Canvas.clear())
        
        def loadBackupBtFn( _ ):
            Canvas.Canvas.lDict[1].grid = [ [toRgba(row[j]) for j in range(len(row))] for i, row in Settings.Get('Project', ['Canvas', '1']).items()]
        self.loadBackupBt: button = button((10, 145), 3, 30, 30, attachFn=loadBackupBtFn)
        self.loadBackupBt.loadIcon('Confirm.png')
        self.ldBckpBtTxt: text = text((50, 145), 4, 170, 30, 'load backup', (11, 10))

        self.panel.link_multi(self.saveBt, self.loadBt, self.clearBt, self.loadBackupBt, self.ldBckpBtTxt)
        self.link_component(self.panel)