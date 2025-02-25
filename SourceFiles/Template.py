from .Mouse import Mouse
from .ComF import cmax, pair_mul, pair_div
from .Window import Window
from . import Settings
from . import Constants

import pygame

tDict: dict[int, 'template'] = {}
# -1 is reserved for propmts

def sub(first: tuple, second: tuple):
    return (first[0] - second[0], first[1] - second[1])

def SwitchIn_tDict(key_1, key_2):
    x = tDict[key_2]
    tDict[key_2] = tDict[key_1]
    tDict[key_1] = x


class component:
    def __init__(self, localPos, order, width, height, color_override = None, type_id = Constants.GENERIC) -> None:
        self.localPos = localPos
        self.order = order
        self.isClicked = False
        self.surf: pygame.Surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        colors = self.get_colors(color_override)
        self.stats = {
            "w" : width,
            "h" : height,
            "c" : colors[0],
            "s" : False, # I dont know what this is anymore, maybe shade? or show?
            "t" : type_id
        }
        self.components: dict[int, component] = {}
        self.master = None

    def renew_surf(self):
        self.surf = pygame.Surface((self.stats["w"], self.stats["h"]), pygame.SRCALPHA, 32)

    def new_component(self, localPos, width, height, color_override = None):
        colors = self.get_colors(color_override)
        keys = list(self.components.keys())
        new_component_order = cmax(keys) + 1
        self.components[new_component_order] = component(localPos, new_component_order, width, height, colors)
        self.components[new_component_order].master = self
        self.components[new_component_order].draw()

    def link_component(self, Component: 'component'):
        self.components[Component.order] = Component
        Component.master = self
        self.draw()

    def link_multi(self, *args: 'component'):
        for arg in args:
            self.link_component(arg)

    def contains(self, position):
        "<position> is in local coordinates"
        if position[0] < self.localPos[0] + 2 or position[0] >  self.localPos[0] + self.stats["w"] - 2:
            return False
        if position[1] < self.localPos[1] + 2 or position[1] >  self.localPos[1] + self.stats["h"] - 2:
            return False
        return True

    def onClick(self, localMousePos):
        self.isClicked = True
        for Component in self.components.values():
            if not Component.contains(localMousePos):
                continue
            if Component.onClick(sub(localMousePos , Component.localPos)): # Calls onClicks + checks if
                break                            # the cycle should break (some buttons can alter <self.components>)

    def onRelease(self):
        self.isClicked = False
        for Component in self.components.values():
            if not Component.isClicked:
                continue
            if Component.onRelease() == True: # Same thing as in onClick
                break

    def draw(self):
        self.surf.fill(self.stats["c"])
        for Component in self.components.values():
            Component.draw()
            self.surf.blit(Component.surf, Component.localPos)

    def get_colors(self, color_override):
        if color_override == None:
            return Settings.Get("User", ["Designs", Settings.Get("User", "Design"), "Panel"])
        return color_override


class slide_panel(component):
    def __init__(self, localPos, order, width, height, big_width, big_height, sliderBt, horizontal = False, color_override = None):
        # Make sure <sliderBt> has order 0 (see <draw> method)
        super().__init__(localPos, order, width, height, color_override)
        self.big_width = big_width
        self.big_height = big_height
        self.cutoff = 0
        self.horizontal = horizontal
        self.slider = sliderBt
        self.link_component(sliderBt)
        sliderBt.draw()

    def adjust(self, localPos: tuple[int, int]) -> tuple[int, int]:
        # Adjusts <localPos> by <self.cutoff>
        x_o, y_o = localPos
        if self.horizontal:
            return (x_o - self.cutoff, y_o)
        return (x_o, y_o - self.cutoff)

    def adjust_plus(self, localPos: tuple[int, int]) -> tuple[int, int]:
        x_o, y_o = localPos
        if self.horizontal:
            return (x_o + self.cutoff, y_o)
        return (x_o, y_o + self.cutoff)

    def draw(self):
        self.surf.fill(self.stats['c'])
        for Component in self.components.values(): # Todo: implement culling
            Component.draw()
            if Component.order == 0:
                self.surf.blit(Component.surf, Component.localPos)
                continue
            self.surf.blit(Component.surf, self.adjust(Component.localPos))

    def clean(self):
        "deletes all components but the slider"
        for order in list(self.components.keys()):
            if order == 0:
                continue
            del self.components[order]

    def onClick(self, localMousePos):
        return super().onClick(self.adjust_plus(localMousePos))


class template:
    def __init__(self, layout_uname: str | None, width, height,
                tDict_override = None, color_override = None, type_id = Constants.GENERIC) -> None:
        self.toggle = Settings.Get("Layout", [layout_uname, "toggle"])
        if tDict_override is None:
            tDict_override = cmax(list(tDict.keys())) + 1
        tDict[tDict_override] = self
        self.order = tDict_override
        self.position: tuple[int, int] = pair_mul(pair_div(Settings.Get("Layout", [layout_uname, "position"]), 100), Window.res)
        self.isClicked = False
        self.surf = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        colors = self.get_colors(color_override)
        self.stats = {
            "w" : width,
            "h" : height,
            "c" : colors[0],
            "fc" : colors[1],
            "lyun" : layout_uname,
            "te" : False, # terminateOnExit
            "t" : type_id,
        }
        self.components: dict[int, component] = {}

    def renew_surf(self):
        self.surf = pygame.Surface((self.stats["w"], self.stats["h"]), pygame.SRCALPHA, 32)

    def new_component(self, localPos, width, height, color_override = None):
        keys = list(self.components.keys())
        new_component_order = cmax(keys) + 1
        self.components[new_component_order] = component(localPos, new_component_order, width, height, component.get_colors(None, color_override))
        self.components[new_component_order].master = self
        self.components[new_component_order].draw()
        return self.components[new_component_order]

    def link_component(self, Component: component):
        self.components[Component.order] = Component
        Component.master = self
        Component.draw()

    def link_multi(self, *args: 'component'):
        for arg in args:
            self.link_component(arg)

    def contains(self, position):
        if position[0] < self.position[0] + 2 or position[0] >  self.position[0] + self.stats["w"] - 2:
            return False
        if position[1] < self.position[1] + 2 or position[1] >  self.position[1] + self.stats["h"] - 2:
            return False
        return True
    
    def onClick(self):
        self.isClicked = True
        for Component in self.components.values():
            if not Component.contains(sub(Mouse.position , self.position)):
                continue
            Component.onClick(sub( sub(Mouse.position , self.position) , Component.localPos))

    def onRelease(self):
        self.isClicked = False
        for Component in self.components.values():
            if not Component.isClicked:
                continue
            Component.onRelease()
    
    def get_colors(self, color_override):
        if color_override == None:
            return Settings.Get("User", ["Designs", Settings.Get("User", "Design"), "Template"])
        return color_override

    def display(self, master_surf: pygame.Surface):
        # self.surf.fill(self.stats["c"])

        highest = cmax(list(self.components.keys())) + 1
        for index in range(highest):
            # self.components[index].draw()
            self.surf.blit(self.components[index].surf, self.components[index].localPos)

        pygame.draw.rect(master_surf, self.stats["fc"], pygame.Rect(self.position[0] - 5, self.position[1] - 5, self.stats["w"] + 10, self.stats["h"] + 10))
        pygame.draw.rect(master_surf, self.stats["c"], pygame.Rect(self.position[0], self.position[1], self.stats["w"], self.stats["h"]))
        master_surf.blit(self.surf, self.position)