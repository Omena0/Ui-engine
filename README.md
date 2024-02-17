
# Ui engine

Easiest ui engine ever???

Fuck compex ass layout managers we have position control :fire:

(tbh might still add them)

## Example

### Result

![Image of the ui created with the bellow code](img/ui.png)

### Code

```python
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
    image_path='pack.png'
).add(root,1)


root.show()

engine.mainloop()
```

## Doc

### Components

- Frame   - Literally just a frame
- Text    - Literally just text
- Button  - Text but with a rectangle arround it*
- TextBox - You can type shit*
- Image   - Just displays an image thats it

(* = has callback)

Please spam ping me on discord so i get motivation to add more

### Methods

#### comp.add(parent,layer=0)*

Adds a component to a parent and sets layer. (layer is optional)

#### comp.setPos(x,y)*

Changes the position of component

(* = Returns self)
