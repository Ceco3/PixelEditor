from .Button import button, frmBt
from .Prompt import prompt
from .Mouse import Mouse
from .Canvas import Reflect, Canvas
from .ComF import pair_sum
from .Tapestry import build_canvas
from . import Settings
from .AvalandiaSupp import save_avalandia_data
from .Meta import Registry
from .BootF import load_frame

import sys, os
import pygame

# An Intermediate file that can utilize many modules
#
# Don't import outside of main

#_________________General_Functions__________________#
def clear_frames():
    files = os.listdir(Settings.Get("User", ["Paths", "FrameBuffer"]))
    for file in files:
        file_path = os.path.join(Settings.Get("User", ["Paths", "FrameBuffer"]), file)
        if os.path.isfile(file_path):
            os.remove(file_path)

BUILD = pygame.USEREVENT + 2
BUILD_EV = pygame.event.Event(BUILD)

LOAD = pygame.USEREVENT + 3
LOAD_EV = pygame.event.Event(LOAD)

NEWLAYER = pygame.USEREVENT + 4
NEWLAYER_EV = pygame.event.Event(NEWLAYER)

DELLAYER = pygame.USEREVENT + 5
DELLAYER_EV = pygame.event.Event(DELLAYER)


#________________Button_Functions____________________#
def VisBtFn(BtObject: button):
    Mouse.state["visualM"] = not Mouse.state["visualM"]

def NewLBtFn(BtObject: button):
    pygame.event.post(NEWLAYER_EV)

def DelLBtFn(BtObject: button):
    pygame.event.post(DELLAYER_EV)

def SaveBtFn(BtObject: button):
    pygame.event.post(BUILD_EV)

def LoadBtFn(BtObject: button):
    pygame.event.post(LOAD_EV)

def ExitBtFn(BtObject: button):
    clear_frames()
    pygame.quit()
    sys.exit()

def SaveStngsBtFn(BtObject: button):
    Settings.save_specified_setting("Project")

def PlusFrmBtFn(BtObject: button):
    Settings.Set("Project", "Canvas", Canvas.get_raw())
    Settings.save_specified_setting("Project")
    Registry.Read("FrameManager").add_frame()

def FrameBtFn(BtObject: button):
    build_canvas(True, Mouse.frame_uid)
    load_frame(BtObject.uid)

def ReflectX(BtObject: button):
    BtObject.master.master.selected_bt = BtObject.order
    Reflect(BtObject, True)

def ReflectY(BtObject: button):
    BtObject.master.master.selected_bt = BtObject.order
    Reflect(BtObject, False)

def AvalanadiaBtFn(BtObject: button):
    save_avalandia_data()