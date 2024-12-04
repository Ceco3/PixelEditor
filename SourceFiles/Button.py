from .Template import component, template
from .Text import make_word
from .Mouse import Mouse
from .ComF import cmax, Lerp
from .Color import color_rgb, color_rgba
from .Meta import Updater, Registry

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
    def __init__(self, localPos, order, width, height, color, fcolor: color_rgb, path, icon_pos = (0, 0)) -> None:
        super().__init__(localPos, order, width, height, color)
        self.stats["fc"] = fcolor.toTuple()
        self.stats["ip"] = icon_pos
        self.icon_surf = pygame.transform.scale(pygame.image.load(path).convert_alpha(), (width, height))

    def onClick(self):
        pass

    def draw(self):
        super().draw()
        self.surf.blit(self.icon_surf, self.stats["ip"])

class text(component):
    def __init__(self, localPos, order, width, height, color, tcolor, text, textPos = (0, 0)) -> None:
        super().__init__(localPos, order, width, height, color)
        self.stats["tc"] = tcolor.toTuple()
        self.stats["txt"] = text
        self.stats["txtp"] = textPos
        self.txt_surf = make_word(self.stats["txt"], self.stats["tc"])

    def onClick(self):
        return
        
    def draw(self):
        super().draw()
        self.surf.blit(self.txt_surf, self.stats["txtp"])



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
        self.attached = None # Newer version of bound (See <attach> method)

    def loadIcon(self, iconPath):
        self.icon = pygame.transform.scale(pygame.image.load(iconPath).convert_alpha(), (self.stats["w"], self.stats["h"]))

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
        break_click_loop = False
        self.stats["f"] = not self.stats["f"]
        if self.attached is not None:
            break_click_loop = self.attached(self)
        self.draw()
        self.master.draw()
        return break_click_loop

    def attach(self, func):
        "Attach a function <func> to button, the function will be called in the onClick method"
        self.attached = func


class toolBt(button):
    def __init__(self, localPos, order, width, height, fcolor, color, tcolor, tool, text = "", textPos=(0, 0)) -> None:
        super().__init__(localPos, order, width, height, fcolor, color, tcolor, text, textPos)
        self.bound_tool = tool

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
        if self.toggle:
            pygame.key.stop_text_input()
            if self.attached is not None:
                self.attached(self)
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