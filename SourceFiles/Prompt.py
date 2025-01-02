from .Template import template, slide_panel, tDict
from .Color import color_rgb, color_rgba
from .Mouse import Mouse
from .Button import button, text, icon, sliderBt
from .Window import Window, Clock

import pygame
import sys, os

#Prompt Id's
LOAD_ID = 0
ERROR_ID = 1
PROMPT_OVERRIDE = -1

class prompt(template):
    def __init__(self, position, master_w, width, master_h, height, color, frame_color,
                 buttons_text_tuples: list[tuple[button, text]], attached_functions, constructor,
                 id, override = PROMPT_OVERRIDE):
        super().__init__(position, master_w, width, master_h, height, color, frame_color, override)
        self.panel = self.new_component((0, 0), width, height, color_rgb(150, 150, 150))
        self.isAlive = True
        self.Bt_Tx_tuples = buttons_text_tuples
        self.populate_panel()
        self.attached_functions = attached_functions

        self.info_buffer = []
        self.identifier = id # To allow for custom manipulation
        if constructor is not None:
            constructor(self)


    def prompt_loop(self):
        while self.isAlive:
            Mouse.update(tDict)
            self.handle_events()

            self.display(Window.screen)
            pygame.display.update()
            Clock.tick(Window.framerate)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.contains(Mouse.position):
                    continue
                Mouse.state["LWR"] = pygame.mouse.get_pressed()
                self.onClick()

    def retrieve(self):
        return(self.info_buffer, self.identifier)

    def kill(self):
        del tDict[-1]
        self.isAlive = False

    def populate_panel(self): # (populate_component? I wanna push for this new name kinda)
        for button, text in self.Bt_Tx_tuples:
            if button is not None:            
                self.panel.link_component(button)
            if text is not None:
                self.panel.link_component(text)

    #___________________Specific prompts_____________________#
    #                                                        #
    #________________________________________________________#

    #____________________Load_Prompt_________________________#
    def load_prompt(self, postition, width, height, color, frame_color):
        buttons_text_tuples = []
        attached_functions = []

        def CloseFn(BtObject: button):
            Prompt.kill()

        def LoadFn(BtObject: button):
            if Prompt.info_buffer != []:
                Prompt.kill()
                Prompt.doRetrieve = True

        def rootBtFn(BtObject: button):
            left, _, right = Mouse.state["LWR"]
            if right:
                for bt_or_tx in self.slide_panel.components:
                    del bt_or_tx
                self.currLoadDir = "."
                self.attached_functions[0](self) # Calls load_prompt_graphics (this method)
                return True # The panel.component dict was changed from inside the onClick for-loop,
                            # So we have to signal it to break the cycle (Implement other soln?)

        CloseBt = button((10, height - 40), 0, 90, 30, color_rgb(70, 70, 70), color_rgb(120, 120, 120), color_rgb(200, 200, 200), "close", (11, 10))
        CloseBt.attach(CloseFn)
        buttons_text_tuples.append((CloseBt, None))

        LoadBt = button((width - 100, height - 40), 1, 90, 30, color_rgb(70, 70, 70), color_rgb(120, 120, 120), color_rgb(200, 200, 200), "load", (11, 10))
        LoadBt.attach(LoadFn)
        buttons_text_tuples.append((LoadBt, None))

        directoryBt = button((10, 10), 2, 300, 30, color_rgb(70, 70, 70), color_rgb(120, 120, 120), color_rgb(200, 200, 200),
                                "Gallery", (11, 10))
        directoryBt.attach(rootBtFn)
        buttons_text_tuples.append((directoryBt, None))
                    
        attached_functions.append(prompt.load_prompt_graphics)

        Prompt = prompt(postition, Window.winX, width, Window.winY, height, color, frame_color, \
                        buttons_text_tuples, attached_functions, prompt.load_constructor, LOAD_ID)
        Prompt.prompt_loop()
        if Prompt.doRetrieve:
            return Prompt.retrieve()
        return (None, Prompt.identifier)

    def load_constructor(self):
        self.doRetrieve = False
        self.currLoadDir: str = "./Gallery"
        slider = sliderBt((10, 10), 0, 16, 50, color_rgb(150, 150, 150), color_rgb(70, 70, 70))
        SlidePanel = slide_panel((0, 50), 3, self.stats['w'], self.stats['h'] - 100, self.stats['w'], (self.stats['h']),
                                  color_rgb(150, 150, 150), slider)
        self.slide_panel = SlidePanel
        self.panel.link_component(self.slide_panel)
        self.load_prompt_graphics()

    #___Graphics_for_<load_prompt>____#
    def load_prompt_graphics(self):
        # Reads contents of directory at relative <self.currLoadDir> and builds self.Bt_Tx_tuples (button_text_tuples)
        # self.Bt_Tx_tuples is assumed to already contain <close> and <proceed> (in this case called "load") buttons
        # Furthermore the buttons need have orders 1, 2 respectively
        # At this point self refers to the prompt
        def fileBtFn(BtObject: button):
            if self.info_buffer == []:
                self.info_buffer.append(self.currLoadDir + "\{}".format(BtObject.stats["txt"]))
            else:
                self.info_buffer[0] = self.currLoadDir + "\{}".format(BtObject.stats["txt"])

        def dirBtFn(BtObject: button):
            print("dirBtFn")
            left, _, right = Mouse.state["LWR"]
            if left:
                for bt_or_tx in self.slide_panel.components:
                    del bt_or_tx
                self.currLoadDir = self.currLoadDir + "/" + BtObject.stats["txt"]
                self.attached_functions[0](self)
                return True


        with os.scandir(self.currLoadDir) as _:
            invalid_files_cntr = 0
            for i, item in enumerate(list(os.scandir(self.currLoadDir))):
                if item.name.startswith('.'):
                    invalid_files_cntr += 1
                    continue
                fileBt = button((50, 20 + (i - invalid_files_cntr) * 40), i * 2 - invalid_files_cntr * 2 + 1, 300, 30,
                                color_rgb(70, 70, 70), color_rgb(120, 120, 120), color_rgb(200, 200, 200),
                                                item.name, (11, 10))
                if item.is_file():
                    fileBt.attach(fileBtFn)
                    if ".png" in item.name:
                        iconPath = "./Icons/VISION.png"
                    elif ".py" in item.name:
                        iconPath = "./Icons/Python.png"
                    elif ".json" in item.name:
                        iconPath = "./Icons/Jason.png"
                    else:
                        iconPath = "./Icons/Empty.png"
                if item.is_dir():
                    fileBt.attach(dirBtFn)
                    iconPath = "./Icons/Directory.png"
                fileIcon = icon((50 + 310, 20 + (i - invalid_files_cntr) * 40), i * 2 - invalid_files_cntr * 2 + 2, 30, 30,
                                color_rgb(150, 150, 150), color_rgb(120, 120, 120), iconPath)
                self.slide_panel.link_multi(fileBt, fileIcon)
            self.panel.draw()

    #______________________Error_Prompt_______________________#
    def error_prompt(self, position, width, height, color, fcolor, error_message = "error occured"):
        Bt_Tx_tuples = []
        attached_functions = []

        def OkBtFn(BtObject: button):
            Prompt.kill()

        OkBt = button((width - 70, height - 40), 0, 60, 30, color_rgb(70, 70, 70), color_rgb(120, 120, 120), color_rgb(200, 200, 200), \
                      "ok", (11, 10))
        OkBt.attach(OkBtFn)

        ErrorTx = text((-150 + width // 2 ,-30 + height // 2), 1, 300, 30, color, color_rgb(70, 70, 70), error_message, (11, 10))

        Bt_Tx_tuples.append((OkBt, ErrorTx))

        Prompt = prompt(position, Window.winX, width, Window.winY, height, color, fcolor, \
                        Bt_Tx_tuples, attached_functions, None, ERROR_ID)
        Prompt.prompt_loop()
