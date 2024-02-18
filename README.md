
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

root = engine.Root('test')

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

### Components List

- Frame       - Literally just a frame
- Text        - Literally just text
- Button      - Text but with a rectangle arround it*
- TextBox     - You can type shit*
- Image       - Just displays an image thats it
- ProgressBar - Fanciest progressbar you've ever seen

(* = has callback)

Please spam ping me on discord so i get motivation to add more

### Root

The root is the actual window that components get added to.

To create the window you must call the .show() method.

The root takes 2 attributes:

- Title   - str
- BgColor - r,g,b

You can set the window title with root.setTitle()

To add components, call the components .add() method
with the root.

(or frame if you're adding a component to a frame)

### Components (detailed)

### Frame

Lets you add other objects into it.

Can be used with .add()

#### Attributes

- Position - x,y
- Width    - int
- Height   - int

### Text

Literally just text

#### Attributes

- Position - x,y
- Text     - str
- Size     - int   (font size)
- Color    - r,g,b (text color)
- Font     - str   (default Roboto)

### Button

A button.

#### Attributes

- position      - x,y
- width         - int
- height        - int
- text          - str
- size          - int (font size)
- action        - Callable
- color         - r,g,b (button color)
- hover_color   - r,g,b
- font_color    - r,g,b
- font          - str (default Roboto)
- corner_radius - int

### TextBox

Box that you can type in. Not really advanced but it works.

Has a callback that gets called
with the current text whenever the text is changed.

- position    - x,y
- width       - int
- height      - int
- size        - int (font size)
- color       - r,g,b
- focus_color - r,g,b (color when in focus)
- hover_color - r,g,b (color when mouse hover)
- font_color  - r,g,b
- font        - str (default roboto)
- text        - str
- on_type     - Callable (called whenever key entered)

### Image

Basic image.

#### Attributes

- position   - x,y
- image_path - str

### ProgressBar

The best progress bar you have and will ever see.

If you want to smooth the movement of the progressbar,
call .start() when you start the operation.

The progressbar will automatically increase based on the speed attribute,
and slow down when its getting far from the last set value.

It will eventually stop.

You should set the speed attribute to a value where the
progressbar doesent stop and its speed
stays somewhat the same

#### Attributes

- position      - x,y
- width         - int
- height        - int
- color         - r,g,b
- border_color  - r,g,b
- border_radius - int
- corner_radius - int
- speed         - int

## Methods (Universal)

Here are all the methods that exist for every single component. (including root)

Basically all methods return self

This is just for convinience reasons.

### comp.add(parent,layer=0)*

Adds a component to a parent and sets layer. (layer is optional)

### comp.setPos(x,y)*

Changes the position of component

(* = Returns self) <!--You're welcome, i love syntax!-->

## Internal methods

Dont use theese!

This is only documented if you want to add custom components

### comp.event(event)

Used internally for events.

### comp.tick(frame)

Called every frame
