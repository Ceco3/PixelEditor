import pygame

class window:
    def __init__(self, winX = 1536, winY = 800, framerate = 60) -> None:
        self.winX = winX
        self.winY = winY
        self.framerate = framerate
        self.screen = pygame.display.set_mode((winX, winY), pygame.DOUBLEBUF, 32)
        pygame.display.set_caption("Pixel Editor")

Window = window()

Clock = pygame.time.Clock()
