import pygame
import sys

from SourceFiles.Canvas import Canvas, Pencil, Bucket
from SourceFiles.Color import color_rgba, color_rgb
from SourceFiles.Tapestry import pallete, layer_mngr, saveBt, exitBt, loadBt, newLBt, delLBt, toolBt, visBt, rollBt, frameBt, button, \
     textBt, BUILD, build, LOAD, load, NEWLAYER, DELLAYER, settings, popupBt, text, AUTOSAVE, AUTOSAVE_EV, BUILD_EV, prompt
from SourceFiles.Template import template, component, tDict, SwitchIn_tDict
from SourceFiles.Meta import Updater, Registry, User_variables
from SourceFiles.FuncBundleBt import FunctionBundle
from SourceFiles.Mouse import Mouse
from SourceFiles.Window import Window, Clock
from SourceFiles import Settings
from SourceFiles.Settings import settings_object_dict

#____Palletes_____#
BasicPL = pallete([10, 10], 0, 230, 250, color_rgb(170, 170, 170))
BasicPL.new_color(color_rgba(155, 55, 100, 255))
BasicPL.new_color(color_rgba(50, 155, 100, 255))
BasicPL.new_color(color_rgba(100, 50, 155, 255))
BasicPL.new_color(color_rgba(200, 150, 55, 255))
BasicPL.new_color(color_rgba(150, 100, 40, 255))
BasicPL.new_color(color_rgba(100, 50, 0, 255))
BasicPL.new_color(color_rgba(0, 150, 255, 255))
BasicPL.new_color(color_rgba(100, 0, 50, 255))
BasicPL.new_color(color_rgba(120, 150, 90, 255))
BasicPL.new_color(color_rgba(205, 0, 255, 155))
BasicPL.new_color(color_rgba(220, 210, 220, 255))
BasicPL.new_color(color_rgba(150, 140, 150, 255))
BasicPL.new_color(color_rgba(0, 1, 0, 255))
BasicPL.new_color(color_rgba(230, 20, 55, 255))


Registry.Write("Char", "")



click = pygame.USEREVENT + 1
click_ev = pygame.event.Event(click)

#___SETTINGS___#
Settings_ = settings((400, 150), Window.winX, 150, Window.winY, 60, color_rgb(120, 120, 120), color_rgb(70, 70, 70))
NameBt = textBt((10, 10), 0, 400, 30, color_rgb(80, 80, 80), color_rgb(70, 70, 70), color_rgb(200, 200, 200), textPos = (11, 10))
FunctionBundle.bind(NameBt, 0, 0)
NameTxt = text((420, 10), 1, 150, 30, color_rgb(150, 150, 150), color_rgb(70, 70, 70), "project title", textPos = (0, 10))
SaveDirBt = textBt((10, 50), 2, 400, 30, color_rgb(80, 80, 80), color_rgb(70, 70, 70), color_rgb(200, 200, 200), textPos = (11, 10))
SaveDirTxt = text((420, 50), 3, 150, 30, color_rgb(150, 150, 150), color_rgb(70, 70, 70), "save directory", textPos = (0, 10))
FunctionBundle.bind(SaveDirBt, 0, 1)
Settings_.components[0].link_component(NameBt)
Settings_.components[0].link_component(NameTxt)
Settings_.components[0].link_component(SaveDirBt)
Settings_.components[0].link_component(SaveDirTxt)

#___CANVAS___#
LyrM = layer_mngr([10, 310], 1, 230, 200, color_rgb(170, 170, 170), Canvas.lDict)
Registry.Write("LayerManager", LyrM)
SaveBt = saveBt((10, 10), 0, 60, 30, color_rgb(80, 80, 80), color_rgb(30, 30, 30), color_rgb(200, 200, 200), textPos = (11, 10))
ExitBt = exitBt((80, 10), 1, 60, 30, color_rgb(80, 80, 80), color_rgb(30, 30, 30), color_rgb(200, 200, 200), textPos = (11, 10))
LoadBt = loadBt((10, 55), 2, 60, 30, color_rgb(80, 80, 80), color_rgb(30, 30, 30), color_rgb(200, 200, 200), textPos = (11, 10))
NewLBt = newLBt((10, 160), -1, 60, 30, color_rgb(80, 80, 80), color_rgb(30, 30, 30), color_rgb(200, 200, 200), textPos = (15, 10))
DelLBt = delLBt((80, 160), -2, 60, 30, color_rgb(80, 80, 80), color_rgb(30, 30, 30), color_rgb(200, 200, 200), textPos = (15, 10))

Attelier = template((Window.winX - 300, 50), Window.winX, 250, Window.winY, 600, color_rgb(150, 150, 150), color_rgb(70, 70, 70))
Attelier.link_component(BasicPL)
Attelier.link_component(LyrM)
Attelier.components[LyrM.order].link_component(NewLBt)
Attelier.components[LyrM.order].link_component(DelLBt)

Garage = template((50, 50), Window.winX, 300, Window.winY, 600, color_rgb(150, 150, 150), color_rgb(70, 70, 70))
BucketBt = toolBt((10, 10), 0, 50, 50, color_rgb(60, 60, 60), color_rgb(100, 100, 100), color_rgb(0, 0, 0), Bucket)
BucketBt.loadIcon("Icons\Bucket.png")
PencilBt = toolBt((70, 10), 1, 50, 50, color_rgb(60, 60, 60), color_rgb(100, 100, 100), color_rgb(0, 0, 0), Pencil)
PencilBt.loadIcon("Icons\Pencil.png")
VisBt = visBt((130, 10), 2, 50, 50, color_rgb(60, 60, 60), color_rgb(100, 100, 100), color_rgb(0, 0, 0))
VisBt.loadIcon("Icons\VISION.png")
ReflectBt = button((10, 70), 3, 50, 50, color_rgb(60, 60, 60), color_rgb(100, 100, 100), color_rgb(0, 0, 0), "")
ReflectBt.loadIcon("Icons\Reflect.png")
FunctionBundle.bind(ReflectBt, 1, 3)

Garage.new_component((10, 10), 280, 300, color_rgb(170, 170, 170))
Garage.components[0].link_component(BucketBt)
Garage.components[0].link_component(PencilBt)
Garage.components[0].link_component(VisBt)
Garage.components[0].link_component(ReflectBt)

Polish = template((450, 20), Window.winX, 700, Window.winY, 100, color_rgb(150, 150, 150), color_rgb(70, 70, 70))
Polish.new_component((0, 0), 200, 100, color_rgb(150, 150, 150))
Polish.components[0].link_component(SaveBt)
Polish.components[0].link_component(ExitBt)
Polish.components[0].link_component(LoadBt)
OptionsSlide: component = Polish.new_component((500, 0), 200, 100, color_rgb(150, 150, 150))
StngsBt = popupBt((150, 10), 0, 40, 40, color_rgb(80, 80, 80), color_rgb(30, 30, 30), color_rgb(200, 200, 200))
StngsBt.SetValues(Settings_, (150, 60, 770, 400))
StngsBt.loadIcon("Icons\Settings.png")
OptionsSlide.link_component(StngsBt)

Animator = template((40, 720), Window.winX, 1460, Window.winY, 300, color_rgb(150, 150, 150), color_rgb(70, 70, 70))
RollBt = rollBt((10, 10), 0, 40, 40, color_rgb(80, 80, 80), color_rgb(30, 30, 30), color_rgb(200, 200, 200))
RollBt.loadIcon("Icons\Go.png")
FrameBt = frameBt((10, 60), 1, 40, 40, color_rgb(80, 80, 80), color_rgb(30, 30, 30), color_rgb(200, 200, 200))
FrameBt.loadIcon("Icons\Add.png")
Control: component = Animator.new_component((0, 0), 300, 100, color_rgb(120, 120, 120))
Control.link_component(RollBt)
Control.link_component(FrameBt)

#___Order_tDict_Here___#
SwitchIn_tDict(1, 4)


#___InitStuff___#
Mouse.tool = Pencil
pygame.time.set_timer(AUTOSAVE_EV, Settings.Get("User", "AutoSave"))

# Remove at will
# Canvas.lDict[1].change_pixel((-14, -1), color_rgba(200, 100, 150, 255))

#___MAINLOOP___#
while True:
    Mouse.update(tDict)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == click:
            most = max(list(tDict.keys()))
            for index in range(most + 1):
                if not tDict[index].contains(Mouse.position) or not tDict[index].toggle:
                    continue
                tDict[index].onClick()
        if event.type == BUILD:
            build(Canvas.lDict[Mouse.layer_selected].grid, Settings.Get("User", "Paths")["SaveDir"], User_variables.Get("imageName"))
            Settings.Set("Project", "Canvas", Canvas.get_raw())
        if event.type == LOAD:
            Canvas.lDict[Mouse.layer_selected].grid = load(Settings.Get("User", "Paths")["LoadDir"])
            Canvas.lDict[Mouse.layer_selected].draw()
            LyrM.draw()
        if event.type == AUTOSAVE:
            # Debug Tool || pygame.event.post(BUILD_EV)
            Settings.Set("Project", "Canvas", Canvas.get_raw())
            Settings.save_specified_settings("Project")
        if event.type == NEWLAYER:
            Mouse.layer_selected = Canvas.new_layer()
            LyrM.update(Canvas.lDict, Mouse)
        if event.type == DELLAYER:
            Canvas.del_layer(Mouse.layer_selected)
            LyrM.del_layer(Mouse)
            LyrM.update(Canvas.lDict, Mouse)
        if event.type == pygame.MOUSEBUTTONDOWN:
            Mouse.state["isDown"] = True
            Mouse.state["LWR"] = pygame.mouse.get_pressed()
            pygame.event.post(click_ev)
        if event.type == pygame.MOUSEBUTTONUP:
            Mouse.state["isDown"] = False
            Mouse.state["LWR"] = (False, False, False)
        if event.type == pygame.TEXTINPUT:
            Registry.Write("Char", event.text)


    Window.screen.fill((150, 150, 150))

    if Mouse.state["visualM"]:
        Canvas.draw_with_tool(LyrM, tDict, Window.screen)
    if not Mouse.state["visualM"]:
        Canvas.draw_with_tool(LyrM)

    Canvas.lDict[Mouse.layer_selected].draw()
    for index in range(max(list(tDict.keys())) + 1):
        if not tDict[index].toggle:
            continue
        tDict[index].display(Window.screen)

    Updater.Update()

    pygame.display.update()

    Clock.tick(Window.framerate)