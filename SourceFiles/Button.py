from .Template import component, template, sub
from .Text import make_word
from .Mouse import Mouse
from .ComF import cmax, Lerp
from .Color import color_rgb, color_rgba
from .Meta import Updater, Registry
from . import Settings

# Forbidden Imports:
# Prompt, Tapestry

import sys
import pygame

BUILD = pygame.USEREVENT + 2
BUILD_EV = pygame.event.Event(BUILD)

LOAD = pygame.USEREVENT + 3
LOAD_EV = pygame.event.Event(LOAD)

NEWLAYER = pygame.USEREVENT + 4
NEWLAYER_EV = pygame.event.Event(NEWLAYER)

DELLAYER = pygame.USEREVENT + 5
DELLAYER_EV = pygame.event.Event(DELLAYER)

class icon(component):
    def __init__(self, localPos, order, width, height, path, icon_pos = (0, 0), color_override = None) -> None:
        if color_override == None:
            colors = Settings.Get("User", ["Designs", Settings.Get("User", "Design"), "Icon"])
        else:
            colors = color_override
        super().__init__(localPos, order, width, height, colors)
        self.stats["fc"] = colors[1]
        self.stats["ip"] = icon_pos
        self.icon_surf = pygame.transform.scale(pygame.image.load(path).convert_alpha(), (width, height))
        self.draw()

    def onClick(self, localMousePos):
        return

    def draw(self):
        super().draw()
        self.surf.blit(self.icon_surf, self.stats["ip"])

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



class button(component):
    def __init__(self, localPos, order, width, height, text, textPos = (0, 0), color_override = None) -> None:
        if color_override == None:
            colors = Settings.Get("User", ["Designs", Settings.Get("User", "Design"), "Button"])
        else:
            colors = color_override
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
        self.attached = None # Newer version of bound (See <attach> method)
        if text is not None:
            self.text_surf = make_word(self.stats["txt"], self.stats["tc"])

    def loadIcon(self, iconPath):
        self.icon = pygame.transform.scale(pygame.image.load(iconPath).convert_alpha(), (self.stats["w"], self.stats["h"]))

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
        print("rnd bt clicked")
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
        colors = self.get_colors(color_override)
        super().__init__(localPos, order, width, height, text, textPos, colors)
        self.bound_tool = tool

    def onClick(self, localMousePos):
        super().onClick(localMousePos)
        Mouse.tool = self.bound_tool

class visBt(button):
    def __init__(self, localPos, order, width, height, text = "", textPos=(0, 0), color_override = None) -> None:
        colors = self.get_colors(color_override)
        super().__init__(localPos, order, width, height, text, textPos, colors)

    def onClick(self, localMousePos):
        super().onClick(localMousePos)
        Mouse.state["visualM"] = not Mouse.state["visualM"]

class lyrBt(button):
    def __init__(self, localPos, order, width, height, text = "layer", textPos=(90, 12), color_override = None) -> None:
        colors = self.get_colors(color_override)
        super().__init__(localPos, order, width, height, text, textPos, colors)
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

class newLBt(button):
    def __init__(self, localPos, order, width, height, text = "new", textPos=(0, 0), color_override = None) -> None:
        colors = self.get_colors(color_override)
        super().__init__(localPos, order, width, height, text, textPos, colors)

    def onClick(self, localMousePos):
        super().onClick(localMousePos)
        pygame.event.post(NEWLAYER_EV)

class delLBt(button):
    def __init__(self, localPos, order, width, height, text = "del", textPos=(0, 0), color_override = None) -> None:
        colors = self.get_colors(color_override)
        super().__init__(localPos, order, width, height, text, textPos, colors)

    def onClick(self, localMousePos):
        super().onClick(localMousePos)
        pygame.event.post(DELLAYER_EV)

class saveBt(button):
    def __init__(self, localPos, order, width, height, text = "save", textPos=(0, 0), color_override = None) -> None:
        colors = self.get_colors(color_override)
        super().__init__(localPos, order, width, height, text, textPos, colors)

    def onClick(self, localMousePos):
        super().onClick(localMousePos)
        pygame.event.post(BUILD_EV)

class exitBt(button):
    def __init__(self, localPos, order, width, height, text = "exit", textPos=(0, 0), color_override = None) -> None:
        colors = self.get_colors(color_override)
        super().__init__(localPos, order, width, height, text, textPos, colors)

    def onClick(self, localMousePos):
        pygame.quit()
        sys.exit()

class loadBt(button):
    def __init__(self, localPos, order, width, height, text = "load", textPos=(0, 0), color_override = None) -> None:
        colors = self.get_colors(color_override)
        super().__init__(localPos, order, width, height, text, textPos, colors)

    def onClick(self, localMousePos):
        super().onClick(localMousePos)
        pygame.event.post(LOAD_EV)

class rollBt(button):
    def __init__(self, localPos, order, width, height, text = "", textPos=(0, 0), color_override = None) -> None:
        colors = self.get_colors(color_override)
        super().__init__(localPos, order, width, height, text, textPos, colors)
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

class frameBt(button):
    def __init__(self, localPos, order, width, height, text = "", textPos=(0, 0), color_override = None) -> None:
        colors = self.get_colors(color_override)
        super().__init__(localPos, order, width, height, text, textPos, colors)

    def onClick(self, localMousePos):
        super().onClick(localMousePos)
        print(Registry.Read("Canvas").create_frame())

class popupBt(button):
    def __init__(self, localPos, order, width, height, text = "", textPos=(0, 0), color_override = None) -> None:
        colors = self.get_colors(color_override)
        super().__init__(localPos, order, width, height, text, textPos, colors)
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

    def onClick(self, localMousePos):
        super().onClick(localMousePos)
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

class sliderBt(button):
    def __init__(self, localPos, order, width, height, fcolor, color, horizontal = False):
        super().__init__(localPos, order, width, height, None, None, None)
        Updater.Add(self)
        self.sensitivity = 1
        self.horizontal = horizontal
        self.last_frame_pos = self.localPos[self.aux()]
        self.difference = 0

    def aux(self) -> int:
        if self.horizontal:
            return 0
        return 1

    def onClick(self, localMousePos):
        x_o, y_o = self.localPos
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

class textBt(button):
    def __init__(self, localPos, order, width, height, text = "", textPos=(0, 0), color_override = None) -> None:
        if color_override == None:
            colors = Settings.Get("User", ["Designs", Settings.Get("User", "Design"), "TextButton"])
        else:
            colors = color_override
        super().__init__(localPos, order, width, height, text, textPos, colors)
        Updater.Add(self)
        self.toggle = False
        self.backspace_timer = 0

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
