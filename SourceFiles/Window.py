import pygame

class window:
    def __init__(self, winX = 1536, winY = 800, framerate = 60) -> None:
        self.framerate = framerate
        self.winX = pygame.display.Info().current_w
        self.winY = pygame.display.Info().current_h
        self.res = (self.winX, self.winY)
        self.isFullScreen = False
        self.res_pre_fullscreen: tuple[int, int] = (self.winX, self.winY)
        self.machine_res = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.screen = pygame.display.set_mode(self.machine_res, pygame.DOUBLEBUF | pygame.RESIZABLE, 32)
        pygame.display.set_caption("Pixel Editor")
        pygame.display.set_icon(pygame.image.load("Icons/Brush.png").convert_alpha())
    
    def resize(self):
        if self.isFullScreen:
            return

    def toggle_fullscreen(self):
        if self.isFullScreen:
            self.screen = pygame.display.set_mode(self.res_pre_fullscreen, pygame.DOUBLEBUF | pygame.RESIZABLE, 32)
        
        if not self.isFullScreen:
            self.res_pre_fullscreen = (self.screen.get_width(), self.screen.get_height())
            self.screen = pygame.display.set_mode(self.machine_res, pygame.DOUBLEBUF | pygame.RESIZABLE | pygame.FULLSCREEN, 32)
        
        self.isFullScreen = not self.isFullScreen

Window = window()

Clock = pygame.time.Clock()
