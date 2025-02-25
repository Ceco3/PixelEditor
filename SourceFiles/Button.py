from .Template import component, template, sub
from .Text import make_word
from .Mouse import Mouse
from .ComF import cmax, Lerp, Clamp
from .Meta import Updater, Registry
from . import Settings
from .Canvas import canvas, switch_canvas

# Forbidden Imports:
# Prompt, Tapestry

import pygame


class icon(component):
    def __init__(self, localPos, order, width, height, path, icon_pos = (0, 0), color_override = None) -> None:
        if color_override == None:
            colors = Settings.Get("User", ["Designs", Settings.Get("User", "Design"), "Icon"])
        else:
            colors = color_override
        super().__init__(localPos, order, width, height, colors)
        self.stats["fc"] = colors[1]
        self.stats["ip"] = icon_pos
        self.icon_surf = pygame.image.load(path).convert_alpha()
        self.stats["ogxy"] = (self.icon_surf.get_width(), self.icon_surf.get_height())
        self.icon_surf = pygame.transform.scale(self.icon_surf, (width, height))
        self.draw()

    def onClick(self, localMousePos):
        return

    def draw(self):
        super().draw()
        self.surf.blit(self.icon_surf, self.stats["ip"])
    
    def change(self, path: str):
        self.icon_surf = pygame.image.load(path).convert_alpha()
        self.stats["ogxy"] = (self.icon_surf.get_width(), self.icon_surf.get_height())
        self.icon_surf = pygame.transform.scale(self.icon_surf, (self.stats['w'], self.stats['h']))
        self.draw()

class text(component):
    def __init__(self, localPos, order, width, height, text, textPos = (0, 0), color_override = None) -> None:
        if color_override == None:
            colors = Settings.Get("User", ["Designs", Settings.Get("User", "Design"), "Text"])
        else:
            colors = color_override
        super().__init__(localPos, order, width, height, colors)
        self.stats["tc"] = colors[1]
        self.stats["txt"] = text
        self.stats["txtp"] = textPos
        self.txt_surf = make_word(self.stats["txt"], self.stats["tc"])

    def onClick(self, localMousePos):
        return
        
    def draw(self):
        super().draw()
        self.surf.blit(self.txt_surf, self.stats["txtp"])
    
    def change(self, text: str):
        self.stats["txt"] = text
        self.txt_surf = make_word(self.stats["txt"], self.stats["tc"])
        self.draw()




class button(component):
    def __init__(self, localPos: tuple[int, int], order, width, height, text = "", textPos = (0, 0), color_override = None, attachFn = None) -> None:
        colors = self.get_colors(color_override)
        super().__init__(localPos, order, width, height, colors)
        self.stats["f"] = True
        self.stats["fc"] = colors[1]
        self.stats["tc"] = colors[2]
        if text is not None:
            self.stats["txt"] = text
        if textPos is not None:
            self.stats["txtp"] = textPos
        self.overlaySurf = pygame.Surface((self.stats["w"], self.stats["h"]), pygame.SRCALPHA, 32)
        self.text_surf = None
        self.icon = None
        self.master: component = None
        self.attached = attachFn # Newer version of bound (See <attach> method)
        if text is not None:
            self.text_surf = make_word(self.stats["txt"], self.stats["tc"])

    def loadIcon(self, iconPath, dim: tuple[int, int] | None = None):
        if dim is None:
            dim = (self.stats['w'], self.stats['h'])
        if '\\' in iconPath or '/' in iconPath:
            self.icon = pygame.transform.scale(pygame.image.load(iconPath).convert_alpha(), dim)
        else:
            self.icon = pygame.transform.scale(pygame.image.load("Icons\\" + iconPath).convert_alpha(), dim)
        # Maybe add a setting for default icon folder that may be changed (not too important)

    def draw(self):
        super().draw()
        pygame.draw.rect(self.surf, self.stats["fc"], pygame.Rect(3, 3, self.stats["w"] - 6, self.stats["h"] - 6))
        if self.text_surf is not None:
            self.surf.blit(self.text_surf, self.stats["txtp"])
        if self.icon is not None:
            self.surf.blit(self.icon, (0, 0))
        if self.stats["f"]:
            self.highlight()

    def get_colors(self, color_override):
        if color_override == None:
            return Settings.Get("User", ["Designs", Settings.Get("User", "Design"), "Button"])
        return color_override

    def highlight(self):
        pygame.draw.rect(self.overlaySurf, (100, 100, 100, 100), pygame.Rect(5, 5, self.stats["w"] - 5, self.stats["h"] - 5))
        self.surf.blit(self.overlaySurf, (0, 0))

    def onClick(self, localMousePos):
        self.isClicked = True
        break_click_loop = False
        self.stats["f"] = not self.stats["f"]
        if self.attached is not None:
            break_click_loop = self.attached(self)
        self.draw()
        self.master.draw()
        return break_click_loop
    
    def onRelease(self):
        self.isClicked = False

    def attach(self, func):
        "Attach a function <func> to button, the function will be called in the onClick method"
        self.attached = func


class toolBt(button):
    def __init__(self, localPos, order, width, height, tool, text = "", textPos=(0, 0), color_override = None) -> None:
        super().__init__(localPos, order, width, height, text, textPos, self.get_colors(color_override))
        self.bound_tool = tool

    def onClick(self, localMousePos):
        super().onClick(localMousePos)
        Mouse.tool = self.bound_tool

class lyrBt(button):
    def __init__(self, localPos, order, width, height, text = "layer", textPos=(90, 12), color_override = None) -> None:
        super().__init__(localPos, order, width, height, text, textPos, self.get_colors(color_override))
        self.stats["f"] = True
        self.overlaySurf = pygame.Surface((self.stats["w"], self.stats["h"]), pygame.SRCALPHA, 32)

    def draw(self, color_data):
        most = cmax(list(self.components.keys()))
        x = 5
        for color in color_data:
            if color == (0, 0, 0, 0) or color == "size":
                continue
            pygame.draw.rect(self.surf, color, pygame.Rect(x, (self.stats["h"] + 1) * (most + 1) + 5, 220, self.stats["h"]))
            x += (color_data[color] / color_data["size"]) * 220
        pygame.draw.rect(self.surf, self.stats["c"], pygame.Rect(x, (self.stats["h"] + 1) * (most + 1) + 5, 220, self.stats["h"]))
        self.surf.blit(self.text_surf, self.stats["txtp"])
        if self.stats["f"]:
            self.highlight()

    def onClick(self, localMousePos):
        self.stats["f"] = not self.stats["f"]
        Mouse.layer_selected = self.order

class knob(button):
    def __init__(self, localPos, order, width, height, text="", textPos=(0, 0), color_override=None, attachFn=None):
        super().__init__(localPos, order, width, height, text, textPos, color_override, attachFn)
        Updater.Add(self)
        self.loadIcon("Knob.png", (30, 30))
        self.range: tuple[int, int] = (0, 1)
        self.value: float = 0.5

    def Update(self):
        if not self.isClicked:
            return
        
        if self.master.master.__class__ == template:
            transformed_mouse_pos = sub(sub(sub(Mouse.position, self.localPos), self.master.localPos), self.master.master.position)
        
        x, _ = transformed_mouse_pos
        self.value = Clamp(0, 1, x / self.stats['w'])
        self.draw()
        self.master.draw()

    def draw(self):
        self.surf.fill(self.master.stats['c'])
        pygame.draw.rect(self.surf, self.stats['fc'], pygame.Rect(10, self.stats['h'] / 2 + 3, self.stats['w'], 5))
        self.surf.blit(self.icon, (self.stats['w'] * self.value - self.icon.width // 2, 5))

class frmBt(button):
    def __init__(self, localPos, order, width, height, uid, bound_canvas, text="", textPos=(0, 0), color_override=None, attachFn=None):
        Updater.Add(self)
        super().__init__(localPos, order, width, height, text, textPos, color_override, attachFn)
        self.uid = uid
        self.bound_canvas: canvas = bound_canvas
        self.y_diff: int = 0
        self.og_pos = self.localPos

    def update_alpha(self):
        _, og_y = self.og_pos
        _, c_y = self.localPos
        new_alpha = (1 - 0.01 * (c_y - og_y)) * 255
        self.surf.set_alpha(Clamp(40, 255, new_alpha))

    def Update(self):
        if not self.isClicked:
            return

        x_o, y_o = self.localPos
        transformed_mouse_pos = sub(sub(Mouse.position, self.master.localPos), self.master.master.position)
        m_x, m_y = transformed_mouse_pos

        _, og_y = self.og_pos
        y_f = Clamp(og_y, og_y + 100, m_y - self.y_diff)
        self.localPos = x_o, y_f
        self.update_alpha()
        self.draw()
        self.master.draw()
    
    def onClick(self, localMousePos):
        super().onClick(localMousePos)
        _, y_o = self.localPos
        _, m_y = localMousePos
        self.y_diff = m_y - y_o

    def onRelease(self):
        super().onRelease()
        _, c_y = self.localPos
        _, og_y = self.og_pos
        if c_y - 65 > og_y:
            self.master.remove_frame(self.uid)
            self.draw()
            self.master.draw()
            return True
        self.localPos = self.og_pos
        switch_canvas(self.bound_canvas)
        self.update_alpha()
        self.draw()
        self.master.draw()
    
    def draw(self):
        super().draw()
        self.surf.blit(pygame.transform.scale(self.bound_canvas.surf, (self.stats['w'], self.stats['h'])), (0, 0))

class rollBt(button):
    def __init__(self, localPos, order, width, height, text = "", textPos=(0, 0), color_override = None) -> None:
        super().__init__(localPos, order, width, height, text, textPos, self.get_colors(color_override))
        self.toggle = False
        self.isLerping = False
        self.complete = 0
        self.start = None
        self.end = None
        Updater.Add(self)

    def onClick(self, localMousePos):
        super().onClick(localMousePos)
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

class popupBt(button):
    def __init__(self, localPos, order, width, height, text = "", textPos=(0, 0), color_override = None) -> None:
        super().__init__(localPos, order, width, height, text, textPos, self.get_colors(color_override))
        self.speed = 1/30
        self.complete = 0
        self.toggle = False
        self.isLerping = False
        self.subject: template = None  # With stats["w"] and stats["h"]
        self.internal = (0, 0, 0, 0)
        self.component_buffer = []
        Updater.Add(self)

    def SetValues(self, subject: template, values: tuple[int, int, int, int]):
        self.subject: template = subject

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

    def onClick(self, localMousePos):
        self.isClicked = True
        self.stats["f"] = not self.stats["f"]
        left, _, right = Mouse.state["LWR"]
        if left and Registry.Read("Settings") != self.subject and self.attached is None:
            self.subject.components[0].components[self.subject.selected_bt].onClick(localMousePos)
            return
        if left and self.attached is not None:
            self.attached(self)
            self.draw()
            self.master.draw()
            return
        if not self.toggle or self.attached is not None:
            self.subject.toggle = True
        self.switch_start_end()
        self.toggle = not self.toggle
        self.isLerping = True
        self.complete = 0
        self.draw()
        self.master.draw()

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

class selectBt(button):
    def __init__(self, localPos, order, width, height, text="", textPos=(0, 0), color_override=None, attachFn=None):
        super().__init__(localPos, order, width, height, text, textPos, color_override, attachFn)
        Updater.Add(self)
        self.toggle = False
        self.subject: template | None = None
        self.initial_size: tuple[int, int] | None = None
        self.final_size: tuple[int, int] | None = None
        self.isLerping = False
        self.isClosing = False
        self.lerpSpeed = 1 / 30
        self.complete = 0

    def Update(self):
        if not self.isLerping:
            return
        
        self.complete += self.lerpSpeed # Change to use timeDelta
        if self.complete > 1:
            self.complete = 1

        if not self.isClosing:
            x_f, y_f = self.final_size
            x_o, y_o = self.initial_size
        if self.isClosing:
            x_f, y_f = self.initial_size
            x_o, y_o = self.final_size

        self.subject.stats['w'] = Lerp(x_o, x_f, self.complete)
        self.subject.stats['h'] = Lerp(y_o, y_f, self.complete)

        if self.subject.stats['w'] == x_f and self.subject.stats['h'] == y_f:
            self.isLerping = False
            self.complete = 0
            if self.isClosing:
                self.subject.toggle = False
                self.isClosing = False
            else:
                self.isClosing = True
        
        self.subject.renew_surf()

    def Bind(self, subject: template, dimensions: tuple[int, int, int, int]):
        self.subject = subject
        x_o, y_o, x_f, y_f = dimensions
        self.initial_size = (x_o, y_o)
        self.final_size = (x_f, y_f)
    
    def onClick(self, localMousePos):
        self.isClicked = True
        self.stats["f"] = not self.stats["f"]

        left, _, right = Mouse.state["LWR"]
        if right:
            self.isLerping = True
            if not self.isClosing:
                self.subject.toggle = True
        
        if left:
            self.toggle = not self.toggle
            self.subject.components[0].components[self.subject.selected_bt].onClick(localMousePos)
            if self.attached is not None:
                self.attached(self)
        
        self.draw()
        self.master.draw()




class sliderBt(button):
    def __init__(self, localPos, order, width, height, horizontal = False, color_override = None):
        super().__init__(localPos, order, width, height, None, None, None, color_override)
        Updater.Add(self)
        self.sensitivity = 1
        self.horizontal = horizontal
        self.last_frame_pos = self.localPos[self.aux()]
        self.difference = 0

    def draw(self):
        super().draw()

    def aux(self) -> int:
        if self.horizontal:
            return 0
        return 1

    def onClick(self, localMousePos):
        x_o, y_o = self.localPos
        if self.master.master.__class__ == component:
            transformed_mouse_pos = sub(sub(Mouse.position, self.master.localPos), self.master.master.localPos)
        if self.master.master.__class__ == template:
            transformed_mouse_pos = sub(sub(Mouse.position, self.master.localPos), self.master.master.position)

        if self.horizontal:
            self.difference = transformed_mouse_pos[0] - x_o
        else:
            self.difference = transformed_mouse_pos[1] - y_o
        self.stats["f"] = True
        self.isClicked = True

    def onRelease(self):
        self.stats["f"] = False
        self.draw()
        self.master.draw()
        return super().onRelease()

    def Update(self):
        if self.isClicked:
            if self.master.master.__class__ == component:
                transformed_mouse_pos = sub(sub(Mouse.position, self.master.localPos), self.master.master.localPos)
            if self.master.master.__class__ == template:
                transformed_mouse_pos = sub(sub(Mouse.position, self.master.localPos), self.master.master.position)
            x_o, y_o = self.localPos
            if self.horizontal:
                self.localPos = (transformed_mouse_pos[0] - self.difference, y_o)
            else:
                self.localPos = (x_o, transformed_mouse_pos[1] - self.difference)
            self.master.cutoff += (self.localPos[self.aux()] - self.last_frame_pos) * self.sensitivity
            self.last_frame_pos = self.localPos[self.aux()]
            self.draw()
            self.master.draw()
            if self.master.master.__class__ == component:
                self.master.master.draw()

class textBt(button):
    def __init__(self, localPos, order, width, height, text = "", textPos=(0, 0), color_override = None) -> None:
        super().__init__(localPos, order, width, height, text, textPos, self.get_colors(color_override))
        Updater.Add(self)
        self.toggle = False
        self.backspace_timer = 0

        self.text_surf = make_word(self.stats["txt"], self.stats["tc"])
        self.draw()

    def onClick(self, localMousePos):
        self.stats["f"] = not self.stats["f"]
        if self.toggle:
            pygame.key.stop_text_input()
            if self.attached is not None:
                self.attached(self)
        if not self.toggle:
            pygame.key.start_text_input()
        self.draw()
        self.master.draw()
        self.toggle = not self.toggle

    def Update(self):
        if self.toggle:
            if self.backspace_timer > 0:
                self.backspace_timer -= 1
            if pygame.key.get_pressed()[pygame.K_BACKSPACE] and self.backspace_timer == 0:
                self.backspace_timer = 6
                self.stats["txt"] = self.stats["txt"][:len(self.stats["txt"]) - 1]
                Registry.Write("Char", "")
                self.text_surf = make_word(self.stats["txt"], self.stats["tc"]) # Performance crusher
                self.draw()
                self.master.draw()
                return
            if Registry.Read("Char") != "":
                self.stats["txt"] += Registry.Read("Char")
                Registry.Write("Char", "")
                self.text_surf = make_word(self.stats["txt"], self.stats["tc"]) # Performance crusher
                self.draw()
                self.master.draw()

class toggleBt(button):
    def __init__(self, localPos, order, width, height, text="", textPos=(0, 0), color_override=None, attachFn=None):
        super().__init__(localPos, order, width, height, text, textPos, color_override, attachFn)
        self.toggle = False
        