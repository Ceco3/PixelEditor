import pygame
import sys

from SourceFiles.Canvas import Canvas, Pencil, Bucket, rescale_canvas
from SourceFiles.Color import color_rgba, color_rgb
from SourceFiles.Tapestry import pallete, color_picker, layer_mngr, settings, AUTOSAVE, AUTOSAVE_EV, selection, load
from SourceFiles.Template import template, component, slide_panel, tDict, SwitchIn_tDict
from SourceFiles.Meta import Updater, Registry
from SourceFiles.Mouse import Mouse
from SourceFiles.Window import Window, Clock
from SourceFiles import Settings
from SourceFiles.Button import toolBt, rollBt, button, textBt, text, popupBt, sliderBt, icon
from SourceFiles.ComF import validate_string, pair_sum
from SourceFiles.Prompt import prompt
from SourceFiles.Functions import BUILD, LOAD, NEWLAYER, DELLAYER, SaveBtFn, ExitBtFn, SaveStngsBtFn, LoadBtFn, NewLBtFn, DelLBtFn, VisBtFn, \
    PlusFrmBtFn, ReflectX, ReflectY, build_canvas, AvalanadiaBtFn
                               

#____Palletes_____#
BasicPL = pallete([10, 10], 0, 230, 150)
BasicPL.new_color(color_rgba(155, 55, 100, 255))
BasicPL.new_color(color_rgba(50, 155, 100, 255))
BasicPL.new_color(color_rgba(100, 50, 155, 255))
BasicPL.new_color(color_rgba(200, 150, 55, 255))
BasicPL.new_color(color_rgba(150, 100, 40, 255))
BasicPL.new_color(color_rgba(100, 50, 0, 255))
BasicPL.new_color(color_rgba(0, 150, 255, 255))
BasicPL.new_color(color_rgba(100, 0, 50, 255))
BasicPL.new_color(color_rgba(120, 150, 90, 255))
BasicPL.new_color(color_rgba(205, 0, 255, 255))
BasicPL.new_color(color_rgba(220, 210, 220, 255))
BasicPL.new_color(color_rgba(150, 140, 150, 255))
BasicPL.new_color(color_rgba(0, 1, 0, 255))
BasicPL.new_color(color_rgba(230, 20, 55, 255))
BasicPL.new_color(color_rgba(10, 150, 40, 255))

Color_picker = color_picker((10, 170), 1, 230, 130, BasicPL)

Registry.Write("Char", "")



#___SETTINGS___#
Settings_ = settings((400, 150), Window.winX, 150, Window.winY, 60)
NameBt = textBt((10, 10), 0, 400, 30, textPos = (11, 10))
def NameBtFn(NameBt: button):
    Settings.Set("Project", "Name", NameBt.stats["txt"])
NameBt.attach(NameBtFn)
NameTxt = text((420, 10), 1, 150, 30, "project title", textPos = (0, 10))
SaveDirBt = textBt((10, 50), 2, 400, 30, textPos = (11, 10))
SaveDirTxt = text((420, 50), 3, 150, 30, "save directory", textPos = (0, 10))
def SaveDirBtFn(SaveDirBt: button):
    Settings.Set("User", ["Paths", "SaveDir"], SaveDirBt.stats["txt"])
SaveDirBt.attach(SaveDirBtFn)
CanvasXBt = textBt((10, 90), 4, 30, 30, textPos = (7, 10))
CanvasXBtTxt = text((50, 90), 5, 150, 30, "canvas width", textPos = (0, 10))
CanvasYBt = textBt((10, 130), 6, 30, 30, textPos = (7, 10))
CanvasYBtTxt = text((50, 130), 7, 150, 30, "canvas height", textPos = (0, 10))
# These two functions are almost exactly the same (you might wanna do something about it) ((or you can't))
def CanvasXBtFn(CanvasXBt: textBt):
    dimensions = Settings.Get("Project", "CanvasMeta")
    if not validate_string(CanvasXBt.stats["txt"]):
        prompt.error_prompt(None, (-150 + Window.winX // 2, -75 + Window.winY // 2), 300, 150, "select valid size")
        return
    dimensions[0] = int(CanvasXBt.stats["txt"])
    Settings.Set("Project", "CanvasMeta", dimensions)
    rescale_canvas((Window.winX / 3 + 50, Window.winY / 4 - 30), Window.winX, 500, Window.winY, 500, dimensions)
def CanvasYBtFn(CanvasYBt: textBt):
    dimensions = Settings.Get("Project", "CanvasMeta")
    if not validate_string(CanvasYBt.stats["txt"]):
        prompt.error_prompt(None, (-150 + Window.winX // 2, -75 + Window.winY // 2), 300, 150, "select valid size")
        return
    dimensions[1] = int(CanvasYBt.stats["txt"])
    Settings.Set("Project", "CanvasMeta", dimensions)
    rescale_canvas((Window.winX / 3 + 50, Window.winY / 4 - 30), Window.winX, 500, Window.winY, 500, dimensions)
CanvasXBt.attach(CanvasXBtFn)
CanvasYBt.attach(CanvasYBtFn)
SaveStngsBt = button((720, 370), 8, 60, 30, "save", (11, 10), attachFn=SaveStngsBtFn)
Settings_.components[0].link_multi(NameBt, NameTxt, SaveDirBt, SaveDirTxt, CanvasXBt, CanvasXBtTxt,
                                   CanvasYBt, CanvasYBtTxt, SaveStngsBt)


#___CANVAS___#
LyrM = layer_mngr([10, 310], 2, 230, 200)
Registry.Write("LayerManager", LyrM)
SaveBt = button((10, 10), 0, 60, 30, "save", textPos = (11, 10), attachFn=SaveBtFn)
ExitBt = button((80, 10), 1, 60, 30, "exit",textPos = (11, 10), attachFn=ExitBtFn)
LoadBt = button((10, 55), 2, 60, 30, "load", textPos = (11, 10), attachFn=LoadBtFn)
NewLBt = button((10, 160), -1, 60, 30, "new", textPos = (15, 10), attachFn=NewLBtFn)
DelLBt = button((80, 160), -2, 60, 30, "del", textPos = (15, 10), attachFn=DelLBtFn)

Attelier = template((Window.winX - 300, 50), Window.winX, 250, Window.winY, 600)
Attelier.link_multi(BasicPL, Color_picker, LyrM)
Attelier.components[LyrM.order].link_component(NewLBt)
Attelier.components[LyrM.order].link_component(DelLBt)

Garage = template((50, 50), Window.winX, 300, Window.winY, 600)
Garage_Colors = [[100, 100, 100], [60, 60, 60], [0, 0, 0]]
BucketBt = toolBt((10, 10), 0, 50, 50, Bucket, color_override=Garage_Colors)
BucketBt.loadIcon("Icons\Bucket.png")
PencilBt = toolBt((70, 10), 1, 50, 50, Pencil, color_override=Garage_Colors)
PencilBt.loadIcon("Icons\Pencil.png")
VisBt = button((130, 10), 2, 50, 50, color_override=Garage_Colors, attachFn=VisBtFn)
VisBt.loadIcon("Icons\VISION.png")
AvaBt = button((10, 130), 4, 50, 50, attachFn=AvalanadiaBtFn)
AvaBt.loadIcon("Icons\Avalandia.png")
ReflectBt = popupBt((10, 70), 3, 50, 50, color_override=Garage_Colors)
ReflectBt.loadIcon("Icons\Reflect.png")

Garage.new_component((10, 10), 280, 300)
Garage.components[0].link_multi(BucketBt, PencilBt, VisBt, AvaBt, ReflectBt)
x_o, y_o = pair_sum(ReflectBt.localPos, ReflectBt.master.localPos, ReflectBt.master.master.position)
print(x_o, y_o)
RefSelection = selection((x_o + 60, y_o - 35), Window.winX, Window.winY, [ReflectX, ReflectY], 30, 0)
ReflectBt.SetValues(RefSelection, (100, 100, 200, 200))
Slider = sliderBt((10, 10), 0, 16, 50)
Archetype = slide_panel((10, 320), 1, 280, 270, 280, 600, Slider)
Archetype.link_component(icon((100, 100), 1, 30, 30, "Icons/Python.png"))
Garage.link_component(Archetype)

Polish = template((450, 20), Window.winX, 700, Window.winY, 100)
Polish.new_component((0, 0), 200, 100, [[150, 150, 150]])
Polish.components[0].link_component(SaveBt)
Polish.components[0].link_component(ExitBt)
Polish.components[0].link_component(LoadBt)
OptionsSlide: component = Polish.new_component((500, 0), 200, 100, [[150, 150, 150]])
StngsBt = popupBt((150, 10), 0, 40, 40)
StngsBt.SetValues(Settings_, (150, 60, 770, 400))
StngsBt.loadIcon("Icons\Settings.png")
OptionsSlide.link_component(StngsBt)

Animator = template((40, 720), Window.winX, 1460, Window.winY, 300)
RollBt = rollBt((10, 10), 0, 40, 40)
RollBt.loadIcon("Icons\Go.png")
FrameBt = button((10, 60), 1, 40, 40, attachFn=PlusFrmBtFn)
FrameBt.loadIcon("Icons\Add.png")
Control: component = Animator.new_component((0, 0), 60, 110)
Control.link_component(RollBt)
Control.link_component(FrameBt)

#___Order_tDict_Here___#
SwitchIn_tDict(1, 4)


#___InitStuff___#
Mouse.tool = Pencil
pygame.time.set_timer(AUTOSAVE_EV, Settings.Get("User", "AutoSave"))
bckgrnd = pygame.transform.scale(pygame.image.load("Gallery/background.jpg").convert(), (Window.winX, Window.winY))

#___MAINLOOP___#
while True:
    Mouse.update(tDict)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ExitBtFn()
        if event.type == BUILD:
            build_canvas()
        if event.type == LOAD:
            Canvas.lDict[Mouse.layer_selected].grid = load()
            Canvas.lDict[Mouse.layer_selected].draw()
            LyrM.draw()
        if event.type == AUTOSAVE:
            # Debug Tool || pygame.event.post(BUILD_EV)
            Settings.Set("Project", "Canvas", Canvas.get_raw())
            Settings.save_specified_settings("Project")
        if event.type == NEWLAYER:
            Mouse.layer_selected = Canvas.new_layer()
            LyrM.update()
        if event.type == DELLAYER:
            if len(Canvas.lDict) == 2:
                prompt.error_prompt(None, (-150 + Window.winX // 2, -75 + Window.winY // 2), 300, 150, 
                                    color_rgb(150, 150, 150), color_rgb(70, 70, 70), "cant delete layer")
                continue
            Canvas.del_layer(Mouse.layer_selected)
            LyrM.del_layer()
            LyrM.update()
        if event.type == pygame.MOUSEBUTTONDOWN:
            Mouse.state["isDown"] = True
            Mouse.state["LWR"] = pygame.mouse.get_pressed()
            for Template in tDict.values():
                if not Template.contains(Mouse.position) or not Template.toggle:
                    continue
                Template.onClick()
        if event.type == pygame.MOUSEBUTTONUP:
            Mouse.state["isDown"] = False
            Mouse.state["LWR"] = (False, False, False)
            for Template in tDict.values():
                if not Template.isClicked:
                    continue
                Template.onRelease()
        if event.type == pygame.TEXTINPUT:
            Registry.Write("Char", event.text)


    Window.screen.fill((150, 150, 150))

    if Mouse.state["visualM"]:
        Canvas.draw_with_tool(LyrM, tDict, Window.screen)
    if not Mouse.state["visualM"]:
        Canvas.draw_with_tool(LyrM)

    Window.screen.blit(bckgrnd, (0, 0))

    Canvas.lDict[Mouse.layer_selected].draw()
    for index in range(max(list(tDict.keys())) + 1):
        if not tDict[index].toggle:
            continue
        tDict[index].display(Window.screen)

    Updater.Update()

    pygame.display.update()

    Clock.tick(Window.framerate)