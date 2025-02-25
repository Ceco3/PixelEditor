import pygame
from .Color import color_rgba
from .Constants import SELECTION

class mouse:
    def __init__(self) -> None:
        self.position = None
        self.color = color_rgba(0, 1, 0, 255)
        self.tool = None
        self.layer_selected = 1
        self.frame_uid = 0
        self.pix_width = 1
        self.state = {
            "isDown" : False,
            "LWR" : (False, False, False),
            "visualM" : False,
        }
        self.occupation = []
        self.ignore_except: int | None = None

    def update(self, tDict):
        self.position = pygame.mouse.get_pos()

        self.ignore_except = None
        self.occupation = []
        most = max(list(tDict.keys()))
        for index in range(most + 1):
            if not tDict[index].contains(self.position) or not tDict[index].toggle:
                continue
            self.occupation.append(tDict[index])
            if tDict[index].const_id == SELECTION:
                self.ignore_except = SELECTION


Mouse = mouse()