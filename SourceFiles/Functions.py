from .Button import button, toggleBt
from .Mouse import Mouse
from . import Canvas
from .Canvas import Reflect
from . import Settings
from .AvalandiaSupp import save_avalandia_data
from .Meta import Registry
from .BootF import build_anim
from .Prompt import prompt
from .Window import Window

import sys, os
import pygame

# An Intermediate file that can utilize many modules
#
# Don't import outside of main

# found in tapestry
#BUILD = pygame.USEREVENT + 2
#BUILD_EV = pygame.event.Event(BUILD)

# found in tapestry
#LOAD = pygame.USEREVENT + 3
#LOAD_EV = pygame.event.Event(LOAD)

NEWLAYER = pygame.USEREVENT + 4
NEWLAYER_EV = pygame.event.Event(NEWLAYER)

DELLAYER = pygame.USEREVENT + 5
DELLAYER_EV = pygame.event.Event(DELLAYER)

PLAYANIM = pygame.USEREVENT + 7
PLAYANIM_EV = pygame.event.Event(PLAYANIM)

#________________Button_Functions____________________#
def VisBtFn(BtObject: button):
    Mouse.state["visualM"] = not Mouse.state["visualM"]

def NewLBtFn(BtObject: button):
    pygame.event.post(NEWLAYER_EV)

def DelLBtFn(BtObject: button):
    pygame.event.post(DELLAYER_EV)

#def SaveBtFn(BtObject: button):
#    pygame.event.post(BUILD_EV)

#def LoadBtFn(BtObject: button):
#    pygame.event.post(LOAD_EV)

def ExitBtFn(BtObject: button):
    pygame.quit()
    sys.exit()

def SaveStngsBtFn(BtObject: button):
    Settings.save_specified_setting('Project')

def PlusFrmBtFn(BtObject: button):
    Settings.Set('Project', 'Canvas', Canvas.Canvas.get_raw())
    Settings.save_specified_setting('Project')
    Registry.Read('FrameManager').add_frame()

def PlayBtFn(BtObject: toggleBt):
    FrmM = Registry.Read('FrameManager')
    if len(FrmM.components) == 1: # Only slider
        prompt.error_prompt(None, (-150 + Window.winX // 2, -75 + Window.winY // 2), 300, 150, 'no animation frames created')
        return
    play_speed = FrmM.play_speed
    BtObject.toggle = not BtObject.toggle
    # print(BtObject.toggle * int((1 / play_speed) * 1000))
    pygame.time.set_timer(PLAYANIM_EV, BtObject.toggle * int((1 / play_speed) * 1000))
    if BtObject.toggle:
        BtObject.loadIcon('Stop.png')
    else:
        BtObject.loadIcon('Play.png')

def SetSpeedMetaFn(value: int):
    'Returns a function'
    FrmM = Registry.Read('FrameManager')
    
    def SetSpeedFn(BtObject: button):
        FrmM.play_speed = value
    
    return SetSpeedFn

def SaveAnimBtFn(BtObject: button):
    build_anim(Settings.Get('Project', 'Name'), Settings.Get('User', ['Paths', 'SaveDir']))

def ReflectX(BtObject: button):
    BtObject.master.master.selected_bt = BtObject.order
    Reflect(BtObject, True)

def ReflectY(BtObject: button):
    BtObject.master.master.selected_bt = BtObject.order
    Reflect(BtObject, False)

def AvalanadiaBtFn(BtObject: button):
    save_avalandia_data()