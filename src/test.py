import engine

root = engine.Window('test')

engine.Text(
    position=(100,100),
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
    action=lambda: button.setPos(button.x+5,button.y)
).add(root,0)

tb = engine.TextBox(
    position=(100,260),
    width=100,
    height=50,
    size=20,
    text='Test'
).add(root,1)

img = engine.Image(
    position=(200,150),
    image_path='img.png'
).add(root,1)


root.show()

engine.mainloop()