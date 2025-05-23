import pygame
import sys

pygame.init()

from SourceFiles import Canvas
from SourceFiles.Canvas import Pencil, Bucket, Lasso, Taster, Shader
from SourceFiles.Color import color_rgba, color_rgb
from SourceFiles.Tapestry import color_picker, shade_picker, thick_picker, layer_mngr, frame_mngr, AUTOSAVE, AUTOSAVE_EV, \
    selection, load_pallete, load, BUILD, LOAD, file, radar, lookup_mngr
from SourceFiles.Template import template, component, slide_panel, tDict, SwitchIn_tDict
from SourceFiles.Meta import Updater, Registry
from SourceFiles.Mouse import Mouse
from SourceFiles.Window import Window, Clock
from SourceFiles import Settings
from SourceFiles.Button import toolBt, rollBt, button, toggleBt, textBt, text, popupBt, sliderBt, icon
from SourceFiles.ComF import validate_string, pair_sum
from SourceFiles.Prompt import prompt
from SourceFiles.Functions import NEWLAYER, DELLAYER, PLAYANIM, \
    ExitBtFn, SaveStngsBtFn, NewLBtFn, DelLBtFn, VisBtFn, \
    PlusFrmBtFn, SaveAnimBtFn, SetSpeedMetaFn, PlayBtFn, ReflectX, ReflectY, AvalanadiaBtFn
from SourceFiles.BootF import build_canvas

Pallete = load_pallete("Testing")
Pallete.localPos = (10, 10)
Registry.Write("Pallete", Pallete)

Color_picker = color_picker((10, 170), 1, 230, 130, Pallete)
Registry.Write("ColorPicker", Color_picker)

Registry.Write("Char", "")

Settings.Set("Project", "Name", "DefaultName")


#___Radar___#
Radar = radar((Window.winX / 3 - 20, Window.winY / 4 - 30), Window.winX, 50, Window.winY, 25)

#___SETTINGS___#
Settings_ = template((400, 150), Window.winX, 150, Window.winY, 60)
Settings_.toggle = False
Settings_.new_component((0, 0), 150, 60)
Registry.Write("Settings", Settings_)
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
    Canvas.Canvas.rescale((Window.winX / 3 + 50, Window.winY / 4 - 30), Window.winX, 500, Window.winY, 500, dimensions)
def CanvasYBtFn(CanvasYBt: textBt):
    dimensions = Settings.Get("Project", "CanvasMeta")
    if not validate_string(CanvasYBt.stats["txt"]):
        prompt.error_prompt(None, (-150 + Window.winX // 2, -75 + Window.winY // 2), 300, 150, "select valid size")
        return
    dimensions[1] = int(CanvasYBt.stats["txt"])
    Settings.Set("Project", "CanvasMeta", dimensions)
    Canvas.Canvas.rescale((Window.winX / 3 + 50, Window.winY / 4 - 30), Window.winX, 500, Window.winY, 500, dimensions)
CanvasXBt.attach(CanvasXBtFn)
CanvasYBt.attach(CanvasYBtFn)
SaveStngsBt = button((720, 370), 8, 60, 30, "save", (11, 10), attachFn=SaveStngsBtFn)
Settings_.components[0].link_multi(NameBt, NameTxt, SaveDirBt, SaveDirTxt, CanvasXBt, CanvasXBtTxt,
                                   CanvasYBt, CanvasYBtTxt, SaveStngsBt)

#___File___#
File = file((400, 150), Window.winX, 150, Window.winY, 60)
Registry.Write("File", File)

#___CANVAS___#
LyrM = layer_mngr([10, 310], 2, 230, 200)
Registry.Write("LayerManager", LyrM)
FileBt = popupBt((10, 10), 0, 60, 30, 'file', textPos = (11, 10))
FileBt.SetValues(File, (150, 60, 770, 400))
# SaveBt = button((10, 10), 0, 60, 30, "save", textPos = (11, 10), attachFn=SaveBtFn)
ExitBt = button((80, 10), 1, 60, 30, "exit", textPos = (11, 10), attachFn=ExitBtFn)
# LoadBt = button((10, 55), 2, 60, 30, "load", textPos = (11, 10), attachFn=LoadBtFn)
NewLBt = button((10, 160), -1, 60, 30, "new", textPos = (15, 10), attachFn=NewLBtFn)
DelLBt = button((80, 160), -2, 60, 30, "del", textPos = (15, 10), attachFn=DelLBtFn)

Attelier = template((Window.winX - 300, 50), Window.winX, 250, Window.winY, 600)
Attelier.link_multi(Pallete, Color_picker, LyrM)
Attelier.components[LyrM.order].link_component(NewLBt)
Attelier.components[LyrM.order].link_component(DelLBt)

Garage = template((50, 50), Window.winX, 300, Window.winY, 600)
Garage_Colors = [[100, 100, 100], [60, 60, 60], [0, 0, 0]]
BucketBt = toolBt((10, 10), 0, 50, 50, Bucket, color_override=Garage_Colors)
BucketBt.loadIcon("Bucket.png")
PencilBt = toolBt((70, 10), 1, 50, 50, Pencil, color_override=Garage_Colors)
PencilBt.loadIcon("Pencil.png")
VisBt = button((130, 10), 2, 50, 50, color_override=Garage_Colors, attachFn=VisBtFn)
VisBt.loadIcon("VISION.png")
AvaBt = button((10, 130), 4, 50, 50, attachFn=AvalanadiaBtFn)
AvaBt.loadIcon("Avalandia.png")
ReflectBt = popupBt((10, 70), 3, 50, 50, color_override=Garage_Colors)
ReflectBt.loadIcon("Reflect.png")
LassoBt = toolBt((190, 10), 5, 50, 50, Lasso, color_override=Garage_Colors)
LassoBt.loadIcon('Lasso.png')
TasterBt = toolBt((190, 70), 6, 50, 50, Taster, color_override=Garage_Colors)
TasterBt.loadIcon('Taster.png')
ShaderBt = toolBt((130, 70), 7, 50, 50, Shader, color_override=Garage_Colors)
ShaderBt.loadIcon('Shade.png')

Garage.new_component((10, 10), 280, 300)
Garage.components[0].link_multi(BucketBt, PencilBt, VisBt, AvaBt, ReflectBt, LassoBt, TasterBt, ShaderBt)

Thick_picker = thick_picker((10, 320), 1, 280, 50)
Shader_picker = shade_picker((10, 380), 2, 280, 50)
Garage.link_multi(Thick_picker, Shader_picker)

Polish = template((450, 20), Window.winX, 700, Window.winY, 100)
Polish.new_component((0, 0), 200, 100)
#Polish.components[0].link_component(SaveBt)
Polish.components[0].link_component(FileBt)
Polish.components[0].link_component(ExitBt)
#Polish.components[0].link_component(LoadBt)
OptionsSlide: component = Polish.new_component((500, 0), 200, 100)
StngsBt = popupBt((150, 10), 0, 40, 40)
StngsBt.SetValues(Settings_, (150, 60, 770, 400))
StngsBt.loadIcon("Settings.png")
OptionsSlide.link_component(StngsBt)
PltBt = button((100, 10), 1, 40, 40)
PltBt.loadIcon("Pallete.png")
OptionsSlide.link_component(PltBt)

Animator = template((40, 720), Window.winX, 1460, Window.winY, 300)
RollBt = rollBt((10, 10), 0, 40, 40)
RollBt.loadIcon("Go.png")
FrameBt = button((10, 60), 1, 40, 40, attachFn=PlusFrmBtFn)
FrameBt.loadIcon("Add.png")
PlayBt = popupBt((10, 110), 2, 40, 40)
PlayBt.loadIcon("Play.png")
PlayBt.attach(PlayBtFn)
AnimSaveBt = button((10, 160), 3, 40, 40, attachFn=SaveAnimBtFn)
AnimSaveBt.loadIcon("AnimSave.png")
Control: component = Animator.new_component((10, 10), 60, 210)
Control.link_multi(RollBt, FrameBt, PlayBt, AnimSaveBt)
FrmSlider = sliderBt((10, 120), 0, 50, 20, True)
FrmM = frame_mngr((80, 10), 1, 800, 160, 2000, 160, FrmSlider, True)
Registry.Write("FrameManager", FrmM)
Animator.link_component(FrmM)
LkupM = lookup_mngr((890, 10), 2, 300, 160)
Animator.link_component(LkupM)


#___Selections___#
RefSelection = selection(pair_sum(ReflectBt.localPos, ReflectBt.master.localPos, ReflectBt.master.master.position, (60, -15)),
                          Window.winX, Window.winY, [ReflectX, ReflectY], ["Vertical.png", "Horizontal.png"], 30, 0)
ReflectBt.SetValues(RefSelection, (7, 15, RefSelection.stats['w'], RefSelection.stats['h']))
AnimSpeedSlctn = selection(pair_sum(PlayBt.localPos, PlayBt.master.localPos, PlayBt.master.master.position, (60, -355)),
                           Window.winX, Window.winY, [SetSpeedMetaFn(15), SetSpeedMetaFn(20), SetSpeedMetaFn(30), SetSpeedMetaFn(60),
                            SetSpeedMetaFn(120), SetSpeedMetaFn(10), SetSpeedMetaFn(5), SetSpeedMetaFn(2)],
                            ["Play1.png", "Play2.png", "Play3.png", "Play5.png", "Play10.png", "Plays2.png", "Plays3.png", "Plays5.png"],
                            30, 0)
PlayBt.SetValues(AnimSpeedSlctn, (7, 15, AnimSpeedSlctn.stats['w'], AnimSpeedSlctn.stats['h']))

#___Order_tDict_Here___#
# SwitchIn_tDict(1, 4)


#___InitStuff___#
Mouse.tool = Pencil
pygame.time.set_timer(AUTOSAVE_EV, Settings.Get("User", "AutoSave"))
bckgrnd = pygame.transform.scale(pygame.image.load('Icons/background.jpg').convert(), (Window.winX, Window.winY))

#___MAINLOOP___#
while True:
    Mouse.update(tDict)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ExitBtFn()
        if event.type == BUILD:
            if not build_canvas():
                prompt.error_prompt(None, (-150 + Window.winX // 2, -75 + Window.winY // 2), 300, 150, "could not save image")
        if event.type == LOAD:
            load()
            LyrM.draw()
        if event.type == AUTOSAVE:
            Settings.Set("Project", "Canvas", Canvas.Canvas.get_raw())
            Settings.save_specified_setting("Project")
        if event.type == NEWLAYER:
            Mouse.layer_selected = Canvas.Canvas.new_layer()
            LyrM.update()
        if event.type == DELLAYER:
            if len(Canvas.Canvas.lDict) == 2:
                prompt.error_prompt(None, (-150 + Window.winX // 2, -75 + Window.winY // 2), 300, 150, "cant delete layer")
                continue
            Canvas.Canvas.del_layer(Mouse.layer_selected)
            LyrM.del_layer()
            LyrM.update()
        if event.type == PLAYANIM:
            FrmM.play()
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
        Canvas.Canvas.draw_with_tool(LyrM, tDict, Window.screen)
    if not Mouse.state["visualM"]:
        Canvas.Canvas.draw_with_tool(LyrM)

    Window.screen.blit(bckgrnd, (0, 0))

    Canvas.Canvas.lDict[Mouse.layer_selected].draw()
    for index in range(max(list(tDict.keys())) + 1):
        if not tDict[index].toggle:
            continue
        tDict[index].display(Window.screen)

    Updater.Update()

    pygame.display.update()

    Clock.tick(Window.framerate)
