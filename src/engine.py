import pygame
from typing import Callable
pygame.init()
pygame.threads.init(32)

clock = pygame.time.Clock()

window = None
focus  = None

frame = 0

class Frame:
    def __init__(
        self,
        position,
        width,
        height
    ):
        self.children = []
        self.parent = None
        
        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.abs_pos = self.pos
        self.abs_x = self.x
        self.abs_y = self.y
        self.pos2 = width, height
        self.width = width
        self.height = height
        
        # Rendering
        self.layer = 0
        self.visible = True

    def setPos(self, x, y):
        self.pos = x, y
        self.x = x
        self.y = y
        self.abs_x = x + self.parent.abs_x
        self.abs_y = y + self.parent.abs_y
        self.abs_pos = self.abs_x, self.abs_y
        return self

    def event(self, event):
        for child in self.children:
            child.event(event)

    def addChild(self, child):
        x = max(child.x, self.x)
        x = min(child.x, self.x + self.width)
        y = max(child.y, self.y)
        y = min(child.y, self.y + self.height)
        child.setPos(x, y)
        if self.children:
            for i, c in enumerate(self.children):
                if child.layer <= c.layer:
                    self.children.insert(i, child)
                    break
        else:
            self.children.append(child)
        return self

    def render(self):
        if not self.visible: return self
        for child in self.children:
            child.render()
        return self

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

class Text:
    def __init__(self, position, text, size, color=(255, 255, 255), font='Roboto'):
        self.parent = None
        
        # Style
        self.text = text
        self.size = size
        self.color = color
        self.font = font
        
        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.abs_pos = self.pos
        self.abs_x = self.x
        self.abs_y = self.y
        
        # Rendering
        self.layer = 0
        self.visible = True

    def setPos(self, x, y):
        self.pos = x, y
        self.x = x
        self.y = y
        self.abs_x = x + self.parent.abs_x
        self.abs_y = y + self.parent.abs_y
        self.abs_pos = self.abs_x, self.abs_y
        return self

    def render(self):
        if not self.visible: return self
        font = pygame.font.SysFont(self.font, self.size)
        text = font.render(self.text, 1, self.color)
        window.disp.blit(text, (self.abs_x, self.abs_y))
        return self

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

    def event(self, event):
        pass

class Button:
    def __init__(
            self,
            position:tuple[int,int,int],
            width:int,
            height:int,
            text:str,
            size:int,
            action:Callable,
            color=(200, 200, 200),
            hover_color=(150, 150, 150),
            font_color=(255, 255, 255),
            font='Roboto'
        ):
        self.parent = None
        
        # Style
        self.text = text
        self.size = size
        self.width = width
        self.height = height
        self.action = action
        self.color = color
        self.hoverColor = hover_color
        self.font_color = font_color
        self.font = font
        self.hovered = False
        
        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.abs_pos = self.pos
        self.abs_x = self.x
        self.abs_y = self.y
        
        # Rendering
        self.layer = 0
        self.visible = True

    def setPos(self, x, y):
        self.pos = x, y
        self.x = x
        self.y = y
        self.abs_x = x + self.parent.abs_x
        self.abs_y = y + self.parent.abs_y
        self.abs_pos = self.abs_x, self.abs_y
        return self

    def checkHovered(self):
        x, y = pygame.mouse.get_pos()
        self.hovered = (
            x in range(self.abs_x, self.abs_x + self.width)
            and y in range(self.abs_y, self.abs_y + self.height)
        )
        return self.hovered

    def render(self):
        if not self.visible: return self
        self.checkHovered()
        color = self.color if self.hovered else self.hoverColor
        pygame.draw.rect(
            window.disp,
            color,
            (self.abs_x, self.abs_y, self.width, self.height),
        )
        font = pygame.font.SysFont(self.font, self.size)
        text = font.render(self.text, 1, self.font_color)
        x = self.abs_x + (self.width - text.get_width()) // 2
        y = self.abs_y + (self.height - text.get_height()) // 2
        window.disp.blit(text, (x, y))
        return self

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

    def event(self, event):
        self.checkHovered()
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.action()

class TextBox:
    def __init__(
            self,
            position:tuple[int,int],
            width:int,
            height:int,
            size:int,
            color=(200, 200, 200),
            focus_color=(175,175,175),
            hover_color=(150,150,150),
            font_color =(255,255,255),
            font="Roboto",
            text="",
            on_type=None,
        ):
        self.parent = None
        
        # Style
        self.color = color
        self.focusColor = focus_color
        self.hoverColor = hover_color
        self.fontColor  = font_color
        self.size = size
        self.width = width
        self.height = height
        self.font = font
        self.callback = on_type
        self.text = text
        self.hovered = False
        
        # Extra
        self.repeat_delay = 20
        self.repeat_interval = 2
        self.repeat_timer = 0
        self.repeating = False
        self.pressed = ''
        self.pressed_old = ''
        
        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.abs_pos = self.pos
        self.abs_x = self.x
        self.abs_y = self.y
        
        # Rendering
        self.layer = 0
        self.visible = True

    def setPos(self, x, y):
        self.pos = x, y
        self.x = x
        self.y = y
        
        self.abs_x = x + self.parent.abs_x
        self.abs_y = y + self.parent.abs_y
        self.abs_pos = self.abs_x, self.abs_y
        
        return self

    def checkHovered(self):
        x, y = pygame.mouse.get_pos()
        self.hovered = x in range(self.abs_x, self.abs_x + self.width) and y in range(self.abs_y, self.abs_y + self.height)
        return self.hovered

    def render(self):
        global frame
        if not self.visible: return self
        # Render
        self.checkHovered()
        color = self.color if self.hovered else self.hoverColor
        if focus == self: color = self.focusColor

        pygame.draw.rect(window.disp,color,(self.abs_x, self.abs_y, self.width, self.height))
        font = pygame.font.SysFont(self.font, self.size)
        a = f'{self.text}|' if focus == self and frame//20 % 2 == 0 else self.text
        text = font.render(a, 1, self.fontColor)

        x = self.abs_x + 5
        y = self.abs_y + (self.height - text.get_height()) // 2
        window.disp.blit(text, (x, y))

        # Key repeat timer
        if self.pressed: self.repeat_timer += 1
        if not self.repeating and self.repeat_timer > self.repeat_delay:
            self.repeating = True
            self.repeat_timer = 0

        if self.pressed != self.pressed_old:
            self.repeat_timer = 0
            self.pressed_old = self.pressed

        if self.repeating and self.repeat_timer > self.repeat_interval:
            if self.pressed == 'BACKSPACE':
                if pygame.key.get_mods() & pygame.KMOD_CTRL:
                    words = self.text.split()
                    self.text = ' '.join(words[:-1]) if words else ''
                else:
                    self.text = self.text[:-1]
            else:
                self.text += self.pressed
            self.repeat_timer = 0

        return self

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

    def event(self, event):
        global focus
        self.checkHovered()

        # Text input
        if event.type == pygame.KEYDOWN:
            if focus == self:
                if event.key == pygame.K_BACKSPACE:
                    self.pressed = 'BACKSPACE'
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        words = self.text.split()
                        self.text = ' '.join(words[:-1]) if words else ''
                    else:
                        self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                    self.pressed = event.unicode
                if self.callback:
                    self.callback(self.text)

        elif event.type == pygame.KEYUP:
            if focus == self:
                self.pressed = ''
                self.repeating = False
                self.repeat_timer = 0

        # Set focus
        if event.type == pygame.MOUSEBUTTONDOWN:
            focus = self if self.hovered else None

class Image:
    def __init__(
            self,
            position,
            image_path
        ):
        self.parent = None

        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.abs_pos = self.pos
        self.abs_x = self.x
        self.abs_y = self.y

        # Image
        self.image = pygame.image.load(image_path)

        # Rendering
        self.layer = 0
        self.visible = True

    def setPos(self, x, y):
        self.pos = x, y
        self.x = x
        self.y = y
        
        self.abs_x = x + self.parent.abs_x
        self.abs_y = y + self.parent.abs_y
        self.abs_pos = self.abs_x, self.abs_y
        return self

    def render(self):
        if not self.visible: return self
        window.disp.blit(self.image, (self.abs_x, self.abs_y))
        return self

    def add(self, parent, layer=0):
        self.layer = layer
        self.parent = parent
        self.setPos(self.x, self.y)
        parent.addChild(self)
        return self

    def event(self, event):
        pass

class Window:
    def __init__(self, title="", bg=(100, 100, 100)):
        global window
        self.setTitle(title)
        self.res = (600, 500)
        self.children = []
        
        # Style
        self.bgColor = bg
        self.width = self.res[0]
        self.height = self.res[1]
        
        # Position (just so parent.x / parent.abs_x works)
        self.x = 0
        self.y = 0
        self.abs_y = 0
        self.abs_x = 0
        
        window = self

    def setTitle(self, title):
        self.title = title
        return self

    def show(self, resizable=True):
        flags = pygame.SCALED | (pygame.RESIZABLE if resizable else 0)
        self.disp = pygame.display.set_mode(
            self.res, flags=flags, depth=32, vsync=1
        )
        return self

    def addChild(self, child):
        x = max(child.x, self.x)
        x = min(child.x, self.x + self.width)
        y = max(child.y, self.y)
        y = min(child.y, self.y + self.height)
        child.setPos(x, y)
        if self.children:
            for i, c in enumerate(self.children):
                if child.layer <= c.layer:
                    self.children.insert(i, child)
                    break
        else:
            self.children.append(child)

    def render(self):
        global frame
        frame += 1
        pygame.display.set_caption(f'{self.title} | FPS: {clock.get_fps()//1}')
        self.disp.fill(self.bgColor)
        for component in self.children:
            component.render()
        pygame.display.flip()
        return self

    def event(self, event):
        if event.type == pygame.VIDEORESIZE:
            self.res = event.size
            self.disp = pygame.display.set_mode(
                self.res, flags=self.disp.get_flags()
            )
        for i in self.children:
            i.event(event)


def update():
    try:
        window.render()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            window.event(event)
        return window
    except Exception as e:
        print(e)
        return None

def mainloop():
    while True:
        a = update()
        clock.tick(120)
        if not a: break



if __name__ == "__main__":
    import main
