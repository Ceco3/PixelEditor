import pygame
from .Color import color_rgba

class mouse:
    def __init__(self) -> None:
        self.position = None
        self.color = color_rgba(0, 1, 0, 255)
        self.tool = None
        self.layer_selected: int = 1
        self.layerBtHeld: int | None = None
        self.frame_uid = 0
        self.thickness = 1
        self.brightness = 0.5 # 0 Pitch Black, 1 Blinding White
        self.state = {
            "isDown" : False,
            "LWR" : (False, False, False),
            "visualM" : False,
        }
        self.occupation = []

    def update(self, tDict):
        self.position = pygame.mouse.get_pos()

        self.occupation = []
        most = max(list(tDict.keys()))
        for index in range(most + 1):
            if not tDict[index].contains(self.position) or not tDict[index].toggle:
                continue
            self.occupation.append(tDict[index])

Mouse = mouse()