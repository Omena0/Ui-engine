import engine
from RGBRotate import RGBRotate

root = engine.Root('test')
root.res = 600,521

tab1 = engine.Tab().add(root,-10)
tab2 = engine.Tab().add(root,-10)

area1 = engine.Area(
    position=(15,15),
    width=195,
    height=230,
    color=(80,80,80),
    corner_radius=10
).add(tab1,-1)

txt = engine.Text(
    position=(25,25),
    text='Test',
    size=100,
    color=(255,0,0)
).add(root,10)

button = engine.Button(
    position=(25,100),
    width=175,
    height=75,
    text='Click Me!',
    size=50,
    action=lambda: button.setPos(button.x+10,button.y)
).add(tab1,0)

tb = engine.Textbox(
    position=(25,185),
    width=175,
    height=50,
    size=30,
    action=lambda txt: print(f'\r{txt}',end=' ')
).add(tab1)

area2 = engine.Area(
    position=(20,355),
    width=310,
    height=130,
    color=(80,80,80),
    corner_radius=10
).add(tab1,-1)

pb1_txt = engine.Text(
    position=(25,360),
    text='Smoothed Progress',
    size=40
).add(tab1)

pb1 = engine.Progressbar(
    position=(25,390),
    width=200,
    height=25,
    corner_radius=3,
    speed=25
).add(tab1,0)

pb2_txt = engine.Text(
    position=(25,425),
    text='Actual Progress',
    size=40
).add(tab1)

pb2 = engine.Progressbar(
    position=(25,455),
    width=200,
    height=25,
    corner_radius=3,
    speed=0
).add(tab1,0)

def r():
    global a
    pb1.setProgress(0,100)
    pb2.setProgress(0,100)
    pb1.progress = 0
    a = 0

restart = engine.Button(
    position=(250,400),
    width=75,
    height=75,
    text='Restart',
    size=30,
    action=r
).add(tab1)

img = engine.Image(
    position=(0,0), # Pos overridden by slider
    image_path='src/img.png'
).add(tab1,1)

def a(_):
    txt.visible = not txt.visible

area3 = engine.Area(
    position=(418,15),
    width=177,
    height=195,
    color=(80,80,80)
).add(tab1,-1)

cb1_txt = engine.Text(
    position=(425,25),
    text='Hide Component',
    size=30
).add(tab1,1)

cb1 = engine.Checkbox(
    position=(480,50),
    width=50,
    height=50,
    action=a
).add(tab1,1)

cb2_txt = engine.Text(
    position=(445,120),
    text='Switch Tabs',
    size=30
).add(root,1)

cb2 = engine.Checkbox(
    position=(480,145),
    width=50,
    height=50,
    action=lambda x: root.setTab(x)
).add(root,1)

slider_txt = engine.Text(
    position=(55,265),
    text='Sliders',
    size=50
).add(tab1)

area4 = engine.Area(
    position=(15,305),
    width=215,
    height=40,
    color=(80,80,80),
    corner_radius=5
).add(tab1,-1)

slider = engine.Slider(
    position=(25,305),
    width=200,
    height=20,
    action=lambda pos: img.setPos(pos*slider.width*2,25)
).add(tab1)

slider2 = engine.Slider(
    position=(25,325),
    width=200,
    height=20,
    action=lambda pos: slider2.setPos(round(20+pos*(slider2.width/1.3)),slider2.y)
).add(tab1)

slider.setValue(0.5)
slider2.setValue(0.0)

pb1.start()

root.show()

rgb = RGBRotate()
rgb.set_hue_rotation(7)

a:int = 0
while engine.update():
    if txt.visible and a % 5 == 0: txt.color = rgb.apply(*txt.color)
    if pb1.realProg < 1 and a%50==0:
        pb1.setProgress(a/4)
        pb2.setProgress(a/4)
    a += 1