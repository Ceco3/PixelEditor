from .Mouse import Mouse
from .ComF import cmax
from .Color import color_rgb

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
    def __init__(self, localPos, order, width, height, color: color_rgb) -> None:
        self.localPos = localPos
        self.order = order
        self.isClicked = False
        self.surf = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.stats = {
            "w" : width,
            "h" : height,
            "c" : color.toTuple(),
            "s" : False
        }
        self.components: dict[int, component] = {}
        self.master = None

    def renew_surf(self):
        self.surf = pygame.Surface((self.stats["w"], self.stats["h"]), pygame.SRCALPHA, 32)

    def new_component(self, localPos, width, height, color):
        keys = list(self.components.keys())
        new_component_order = cmax(keys) + 1
        self.components[new_component_order] = component(localPos, new_component_order, width, height, color)
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

    def onClick(self, localMousePos): # <localMousePos> was used back when Mouse wasn't easily accesible (consider removing it)
        self.isClicked = True
        highest = cmax(list(self.components.keys()))
        for index in range(min(list(self.components.keys())), highest + 1):
            if not self.components[index].contains(localMousePos):
                continue
            if self.components[index].onClick(): # Calls onClicks + checks if
                break                            # the cycle should break (some buttons can alter <self.components>)

    def onRelease(self):
        self.isClicked = False
        for Component in self.components.values():
            if not Component.isClicked:
                continue
            Component.onRelease()

    def draw(self):
        self.surf.fill(self.stats["c"])
        highest = cmax(list(self.components.keys()))
        for index in range(highest + 1):
            self.components[index].draw()
            self.surf.blit(self.components[index].surf, self.components[index].localPos)


class template:
    def __init__(self, position, master_w, width, master_h, height, color, frame_color, tDict_override = None) -> None:
        self.toggle = True
        if tDict_override is None:
            tDict[cmax(list(tDict.keys())) + 1] = self
        else:
            tDict[tDict_override] = self
        self.position = position
        self.isClicked = False
        self.surf = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.stats = {
            "mw" : master_w,
            "w" : width,
            "mh" : master_h,
            "h" : height,
            "c" : color.toTuple(),
            "fc" : frame_color.toTuple(),
        }
        self.components: dict[int, component] = {}

    def renew_surf(self):
        self.surf = pygame.Surface((self.stats["w"], self.stats["h"]), pygame.SRCALPHA, 32)

    def new_component(self, localPos, width, height, color):
        keys = list(self.components.keys())
        new_component_order = cmax(keys) + 1
        self.components[new_component_order] = component(localPos, new_component_order, width, height, color)
        self.components[new_component_order].master = self
        self.components[new_component_order].draw()
        return self.components[new_component_order]

    def link_component(self, Component: component):
        self.components[Component.order] = Component
        Component.master = self
        Component.draw()

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
    
    def display(self, master_surf: pygame.Surface):
        # self.surf.fill(self.stats["c"])

        highest = cmax(list(self.components.keys())) + 1
        for index in range(highest):
            # self.components[index].draw()
            self.surf.blit(self.components[index].surf, self.components[index].localPos)

        pygame.draw.rect(master_surf, self.stats["fc"], pygame.Rect(self.position[0] - 5, self.position[1] - 5, self.stats["w"] + 10, self.stats["h"] + 10))
        pygame.draw.rect(master_surf, self.stats["c"], pygame.Rect(self.position[0], self.position[1], self.stats["w"], self.stats["h"]))
        master_surf.blit(self.surf, self.position)