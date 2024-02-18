import engine

root = engine.Root('test')

txt = engine.Text(
    position=(100,70),
    text='Test',
    size=100,
    color=(0,0,0)
).add(root,1)

button = engine.Button(
    position=(100,150),
    width=200,
    height=100,
    text='Click Me!',
    size=50,
    action=lambda: button.setPos(button.x+10,button.y)
).add(root,0)

pb = engine.ProgressBar(
    position=(100,400),
    width=200,
    height=25,
    corner_radius=3,
    speed=25
).add(root,0)

pb2 = engine.ProgressBar(
    position=(100,440),
    width=200,
    height=25,
    corner_radius=3,
    speed=0
).add(root,0)

img = engine.Image(
    position=(300,50),
    image_path='src/img.png'
).add(root,1)

def a(_):
    txt.visible = not txt.visible

cb = engine.CheckBox(
    position=(25,200),
    width=50,
    height=50,
    action=a
).add(root)

tb = engine.TextBox(
    position=(100,300),
    width=200,
    height=50,
    size=30,
    action=lambda txt: print(f'\r{txt}',end=' ')
).add(root)

pb.start()

root.show()

a = 0
while engine.update():
    if pb.realProg < 1:
        if a%50==0:
            pb.setProgress(a/4)
            pb2.setProgress(a/4)
        a += 1
