from .Template import template, component, tDict, slide_panel
from .Color import toRgba, color_rgba, color_rgb
from . import Canvas
from .Canvas import rescale_canvas, new_canvas, switch_canvas, Bucket, Pencil, Lasso
from .Meta import Registry, Updater
from .Mouse import Mouse
from .ComF import cmax, validate_string, pair_sum, pair_div_vec, pair_mul
from .Window import Window
from .Button import lyrBt, button, knob, sliderBt, frmBt, textBt, toolBt, selectBt, popupBt
from . import Settings
from . import Constants
from .AvalandiaSupp import save_avalandia_data
from .Prompt import prompt
from .Constants import SELECTION

from itertools import takewhile
import cv2
import pygame, sys

AUTOSAVE = pygame.USEREVENT + 6
AUTOSAVE_EV = pygame.event.Event(AUTOSAVE)

def load_img(path) -> list[list[color_rgba]]:
    if ".png" not in path:
        path += ".png"
    bgra_content = cv2.imread(path, -1)

    if bgra_content is None:
        # Pop up Ideally
        return Canvas.Canvas.lDict[Mouse.layer_selected].grid

    gridObject = []

    height = len(bgra_content)
    width = len(bgra_content[0])

    for y in range(height):
        row = []
        for x in range(width):
            row.append(color_rgba(int(bgra_content[y][x][2]), int(bgra_content[y][x][1]), int(bgra_content[y][x][0]), int(bgra_content[y][x][3])))
        gridObject.append(row)

    rescale_canvas((Window.winX / 3 + 50, Window.winY / 4 - 30), Window.winX, 500, Window.winY, 500, [width, height])
    name = list(takewhile(lambda x: x != "\\" and x != "/", path[::-1]))
    name.reverse()
    name = ''.join(name)
    name = name.replace(".png", '')
    Settings.Set("Project", "Name", name)

    return gridObject

def load_anim():
    pass

def load():
    ret_info, _ = prompt.load_prompt(None, (Window.winX / 2 - 250, Window.winY / 2 - 175), 500, 350)

    if ret_info is None:
        # Pop up Ideally
        return Canvas.Canvas.lDict[Mouse.layer_selected].grid
    path: str = ret_info[0]

    Canvas.Canvas.lDict[Mouse.layer_selected].grid = load_img(path)
    Canvas.Canvas.lDict[Mouse.layer_selected].reload_color_data()
    Canvas.Canvas.lDict[Mouse.layer_selected].draw()


def load_pallete(name: str, localPos: tuple[int, int], order: int, width, height) -> 'pallete':
    raw_pallete = Settings.Get("Palletes", name)
    Pallete: pallete = pallete((0, 0), 0, 230, 150)
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
        self.primary: dict[int, color_rgba] = {}

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

    def get_raw(self) -> list[tuple[int, int, int, int]]:
        raw = []
        for color in self.primary.values():
            raw.append(color.toTuple())

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
    def __init__(self, localPos, order, width, height, bound_pallete_path: list[str], color_override=None):
        super().__init__(localPos, order, width, height, color_override)
        Updater.Add(self)
        self.prewiev = [0, 0, 0, 255]
        self.bound_pallete: pallete = Settings.Get("Layout", bound_pallete_path)
        r_knob = knob((100, 10), 0, 100, 30)
        g_knob = knob((100, 50), 1, 100, 30)
        b_knob = knob((100, 90), 2, 100, 30)

        def pick_color(BtObject):
            new_color = toRgba(self.prewiev)
            self.bound_pallete.new_color(new_color)
            Mouse.color = new_color
        pick_button = button((20, 45), 4, 40, 40, attachFn=pick_color)

        self.link_multi(r_knob, g_knob, b_knob, pick_button)
        self.repaint_prewiev()
    
    def Update(self):
        for knob in self.components.values():
            if knob.isClicked:
                self.repaint_prewiev()

    def draw(self):
        super().draw()
        self.bound_pallete.draw()
        pygame.draw.rect(self.surf, [100, 100, 100], pygame.Rect(15, 40, 50, 50))
        pygame.draw.rect(self.surf, self.prewiev, pygame.Rect(20, 45, 40, 40))

    def repaint_prewiev(self):
        color = [0, 0, 0, 255]
        for color_knob in self.components.values():
            if color_knob.order == 4:
                continue
            color[color_knob.order] = int(color_knob.value * 255)
        self.prewiev = color

def NewLBtFn(BtObject: button):
    Mouse.layer_selected = Canvas.Canvas.new_layer()
    BtObject.master.update()

def DelLBtFn(BtObject: button):
    if len(Canvas.Canvas.lDict) == 2:
        prompt.error_prompt(None, (-150 + Window.winX // 2, -75 + Window.winY // 2), 300, 150, "cant delete layer")
        return
    Canvas.Canvas.del_layer(Mouse.layer_selected)
    BtObject.master.del_layer()
    BtObject.master.update()

class layer_mngr(component):
    def __init__(self, localPos, order, width, height) -> None:
        super().__init__(localPos, order, width, height)
        self.stats["lyrBh"] = 25
        self.stats["lyrBw"] = 215
        self.build()

        NewLBt = button((10, 160), -1, 60, 30, "new", textPos = (15, 10), attachFn=NewLBtFn)
        DelLBt = button((80, 160), -2, 60, 30, "del", textPos = (15, 10), attachFn=DelLBtFn)      
        self.link_multi(NewLBt, DelLBt)

    def build(self):
        for lyr_key in Canvas.Canvas.lDict:
            self.new_layer()

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
        self.components[most + 1] = lyrBt((5, (self.stats["lyrBh"] + 1) * (most) + 5), most + 1, self.stats["lyrBw"], self.stats["lyrBh"],
                                           textPos=(90, 10), color_override=color_override)

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
        self.play_speed: float = 15 # FPS

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

    def add_frame(self):
        # build_canvas(True, self.last_id + 1)
        FrameBt = frmBt((15 + self.pic_size * self.last_id + 15 * self.last_id - self.cutoff, 10),
                         self.last_id + 1, self.pic_size, self.pic_size, self.last_id + 1, Canvas.Canvas)
        new_canvas(Canvas.Canvas.position, Canvas.Canvas.stats['w'], Canvas.Canvas.stats['h'],
                    (Canvas.Canvas.pix_w, Canvas.Canvas.pix_h), Canvas.Canvas.order)
        self.link_component(FrameBt)
        self.last_id += 1

    def play(self):
        self.curr_frame = (self.curr_frame + 1) % (len(self.components))
        if self.curr_frame == 0:
            self.curr_frame += 1
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

def AvalanadiaBtFn(BtObject: button):
    save_avalandia_data()

class tool_panel(component):
    def __init__(self, localPos, order, width, height, color_override=None, type_id=Constants.TOOLS):
        super().__init__(localPos, order, width, height, color_override, type_id)
        Garage_Colors = [[100, 100, 100], [60, 60, 60], [0, 0, 0]]

        BucketBt = toolBt((10, 10), 0, 50, 50, Bucket, color_override=Garage_Colors)
        BucketBt.loadIcon("Bucket.png")
        PencilBt = toolBt((70, 10), 1, 50, 50, Pencil, color_override=Garage_Colors)
        PencilBt.loadIcon("Brush.png")
        VisBt = selectBt((130, 10), 2, 50, 50, color_override=Garage_Colors)
        VisBt.loadIcon("VISION.png")
        AvaBt = button((10, 130), 4, 50, 50, attachFn=AvalanadiaBtFn)
        AvaBt.loadIcon("Avalandia.png")
        ReflectBt = selectBt((10, 70), 3, 50, 50, color_override=Garage_Colors)
        ReflectBt.loadIcon("Reflect.png")
        LassoBt = toolBt((190, 10), 5, 50, 50, Lasso, color_override=Garage_Colors)
        LassoBt.loadIcon("Lasso.png")

        self.link_multi(BucketBt, PencilBt, VisBt, AvaBt, ReflectBt, LassoBt)

def ExitBtFn(BtObject: button):
    for Template in tDict.values():
        if Template.stats["te"]: # TerminateOnExit
            Settings.Del("Layout", Template.stats["lyun"])
    pygame.quit()
    sys.exit()

def LoadBtFn(BtObject: button):
    pygame.event.post(Constants.LOAD_EV)

class options_panel(component):
    def __init__(self, localPos, order, width, height, color_override=None, type_id=Constants.GENERIC):
        super().__init__(localPos, order, width, height, color_override, type_id)

I_SHAPE = 0
DASH_SHAPE = 1

class selection(template):
    # selection position is set on <selectionBt.Bind()>
    def __init__(self, layout_uname: str | None, button_fns: list[button], button_icon_paths: list[str], button_dim: int,
                 shape = I_SHAPE, tDict_override=None, color_override=None):
        if shape == I_SHAPE:
            width = button_dim + (1/6) * button_dim * 2 + 10
            height = len(button_fns) * button_dim + (1/6) * button_dim * (len(button_fns) + 1) + 10
        if shape == DASH_SHAPE:
            height = button_dim + (1/6) * button_dim * 2 + 10
            width = len(button_fns) * button_dim + (1/6) * button_dim * (len(button_fns) + 1) + 10
        super().__init__(layout_uname, width, height, tDict_override, color_override, SELECTION)
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

    def calculate_position(self, BtObject: button, xy_diff: tuple[int, int]) -> tuple[int, int]:
        "<xy_diff> is absolute pixel size"
        return pair_mul(pair_div_vec(pair_sum(BtObject.localPos, BtObject.master.localPos, BtObject.master.master.position, xy_diff), Window.res), (100, 100))

class pallete_selector(template):
    def __init__(self, position, master_w, width, master_h, height, tDict_override=None, color_override=None):
        super().__init__(position, master_w, width, master_h, height, tDict_override, color_override)
        self.pallete_num: int = len(Settings.Get("Palletes", None))
        slider = sliderBt((10, 10), 0, 10, 50)
        self.slide_panel = slide_panel((0, 0), 0, width, height, width, height, slider)

    def display(self, master_surf: pygame.Surface):
        pass

FILE_M = 0
PROJECT_M = 1
WINDOW_M = 2

class menu(template):
    def __init__(self, layout_uname: str, width, height,
                 tDict_override=None, color_override=None, const_id=None):
        super().__init__(layout_uname, width, height, tDict_override, color_override, const_id)
        self.menu_selected: int = FILE_M
        self.select_m_panel: component = component((0, 0), 0, width // 5, height)
        self.content_m_panel: component = component((width // 5 + 10, 0), 1, 4 * width // 5 - 10, height)
        self.link_multi(self.select_m_panel, self.content_m_panel)

        File_mBt = textBt((0, 0), FILE_M, self.select_m_panel.stats['w'], 30, "file", (4, 11))
        Project_mBt = textBt((0, 30), PROJECT_M, self.select_m_panel.stats['w'], 30, "project", (4, 11))
        Window_mBt = textBt((0, 60), WINDOW_M, self.select_m_panel.stats['w'], 30, "window", (4, 11))

        self.select_m_panel.link_multi(File_mBt, Project_mBt, Window_mBt)