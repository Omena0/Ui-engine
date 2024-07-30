from types import FunctionType
from easing import get_easing
from threading import Thread
from copy import copy
import time as t
import pygame

pygame.init()
clock = pygame.time.Clock()

# Const
FPS = 60
use_drag_rectangle = True

# Vars
running = True
root = None
manager = None
focus = None
frame = 0
tab = 0
tabCount = 0

eventHooks = []

def nothing(*args, **kwargs):
    """Does nothing"""

class CustomGroup(pygame.sprite.LayeredDirty):
    def draw(self, surface):
        """draw all sprites in the right order onto the passed surface

        LayeredUpdates.draw(surface, special_flags=0): return Rect_list

        """
        spritedict = self.spritedict
        dirty = self.lostsprites

        self.lostsprites = []

        init_rect = self._init_rect

        for sprite in self.sprites():
            rec = spritedict[sprite]
            newrects = sprite.draw()

            if not isinstance(newrects, list):
                newrects = [newrects]

            for newrect in newrects:
                if isinstance(newrect, pygame.Surface):
                    newrect = newrect.get_rect()
                if rec is init_rect:
                    dirty.append(newrect)
                else:
                    if newrect.colliderect(rec):
                        dirty.append(newrect.union(rec))
                    else:
                        dirty.append(newrect)
                        dirty.append(rec)
                spritedict[sprite] = newrect
        return dirty

class BasePositionManager:
    """Base Position manager, used as a context manager where it is able to manage positions of it's children.

       Override the update method to set the positions of the children.
    """
    def __init__(self):
        super().__init__()
        self.children = []

    def update(self):
        """Does nothing by default, override this with a method that sets the positions of self.children.
        """
    
    def addChild(self,child):
        """Add a child to the position manager

        Args:
            child (Component): The child component to add
        """
        self.children.append(child)

    def __enter__(self):
        global manager
        if manager: manager.update()
        self.oldManager = manager
        manager = self
        return self

    def __exit__(self, *_):
        global manager
        manager = self.oldManager
        self.update()

group = CustomGroup()

### COMPONENTS ###

class Component(pygame.sprite.DirtySprite):
    def __init__(self) -> None:
        super().__init__()
        self.hovered: bool = False
        if manager:
            manager.addChild(self)
    
    def checkHover(self) -> bool:
        x, y = pygame.mouse.get_pos()
        self.hovered = x in range(int(self.x),int(self.x+self.width)) and y in range(int(self.y),int(self.y+self.height))
        return self.hovered

    def add(self, layer: int = 0) -> 'Component':
        self._layer = layer
        group.add(self)
        return self

    def setPos(self, x: int, y: int) -> 'Component':
        self.x = x
        self.y = y
        self.pos = x,y
        self.dirty = 1
        self.draw()
        if hasattr(self,'update'): self.update()
        return self

class Text(Component):
    def __init__(
            self,
            position:tuple[int,int],
            text:str,
            size:int,
            color=(255,255,255),
            font='Roboto'
        ):
        super().__init__()
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.text = text
        self.size = size
        self.color = color
        self.font = font

    def draw(self):
        font = pygame.font.SysFont(self.font, self.size)

        return root.disp.blit(
            font.render(self.text, 1, self.color),
            (self.x,self.y)
        )

class Area(Component):
    def __init__(
            self,
            position:tuple[int,int],
            width,
            height,
            color=(255,255,255),
            corner_radius=10
        ):
        super().__init__()
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.color = color
        self.width = width
        self.height = height
        self.corner_radius = corner_radius

    def draw(self):
        return pygame.draw.rect(root.disp,self.color,(self.x,self.y,self.width,self.height),0,self.corner_radius)

class Button(Component):
    def __init__(
            self,
            position:tuple[int,int],
            width,
            height,
            text,
            color=(60,60,60),
            hover_color=(70,70,70),
            text_color=(255,255,255),
            font='Roboto',
            size=30,
            corner_radius=10,
            action = lambda: ...
        ):
        super().__init__()
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.action = action

        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.size = size

        eventHooks.append(self.event)

    def draw(self):
        self.checkHover()
        # Button rect
        rect = pygame.draw.rect(
            root.disp,
            (self.hover_color if self.hovered else self.color),
            (self.x, self.y, self.width, self.height),
            0, self.corner_radius
        )

        # Button Text
        rendered = pygame.font.SysFont(
            self.font, self.size
        ).render(
            self.text, 1, self.text_color
        )
        
        text = root.disp.blit(
            rendered,
            (self.x+self.width//2-rendered.get_width()//2,self.y+self.height//2-rendered.get_height()//2)
        )
        return [rect,text]

    def event(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                self.action()

class Checkbox(Component):
    def __init__(
            self,
            position:tuple[int,int],
            width:int,
            height:int,
            color=(56,56,56),
            hover_color=(70,70,70),
            check_color=(120,120,120),
            corner_radius=3,
            checked:bool=False,
            action:FunctionType=None
        ):
        super().__init__()
        self.action = action

        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        
        # Style
        self.width = width
        self.height = height
        self.color = color
        self.hoverColor = hover_color
        self.checkColor = check_color
        self.corner_radius = corner_radius
        self.checked = checked
        self.hovered = False

        eventHooks.append(self.event)

    def toggle(self):
        self.checked = not self.checked
        if self.action:
            self.action(self.checked)

    def draw(self):
        if not self.changed: return
        color = self.hoverColor if self.hovered else self.color
        
        outer_rect = pygame.draw.rect(
            root.disp,
            color,
            (self.abs_x, self.abs_y, self.width, self.height),
            0,
            self.corner_radius
        )

        if self.checked:
            inner_rect = pygame.draw.rect(
                root.disp,
                self.checkColor,
                (self.abs_x+self.width/8, self.abs_y+self.width/8, self.width-self.width/4+1, self.height-self.width/4+1),
                0,
                self.corner_radius
            )
            return [outer_rect, inner_rect]
        return [outer_rect]

    def event(self, event):
        self.checkHover()
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            event.handled = True
            self.toggle()

class Textbox(Component):
    def __init__(
            self,
            position:tuple[int,int],
            width:int,
            height:int,
            size:int,
            color=(75, 75, 75),
            focus_color=(65,65,65),
            hover_color=(80,80,80),
            font_color =(255,255,255),
            corner_radius=8,
            font="Roboto",
            text="",
            action=None,
        ):
        super().__init__()
        
        self.action = action
        
        # Style
        self.color = color
        self.focusColor = focus_color
        self.hoverColor = hover_color
        self.fontColor  = font_color
        self.corner_radius = corner_radius
        self.size = size
        self.width = width
        self.height = height
        self.font = font
        self.text = text
        self.hovered = False
        
        # Extra
        self.repeat_delay = 200
        self.repeat_interval = 50
        self.repeat_timer = 0
        self.repeating = False
        self.pressed = ''
        self.pressed_old = ''
        
        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]

        eventHooks.append(self.event)

    def draw(self):
        global frame
        self.checkHover()

        # Tick
        if self.pressed: self.repeat_timer += clock.get_time()
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
            
            # Autorepeat calls action :)
            if self.action:
                self.action(self.text)
        
        # Render
        color = self.color if focus == self else self.focusColor
        if self.hovered: color = self.hoverColor

        # Draw base
        base = pygame.draw.rect(
            root.disp,
            color,
            pygame.Rect(
                self.x,
                self.y,
                self.width,
                self.height
            ),
            0,
            self.corner_radius
        )

        if self.text:
            font = pygame.font.SysFont(self.font, self.size)

            # Blinking cursor (i love this lmao)
            a = f'{self.text}|' if focus == self and frame//20 % 2 == 0 else self.text
            text = font.render(a, 1, self.fontColor)

            x = self.x + 5
            y = self.y + (self.height - text.get_height()) // 2
            root.disp.blit(text, (x, y))
            return [base,text]
        return [base]

    def event(self, event):
        global focus

        # Text input
        if event.type == pygame.KEYDOWN and focus == self:
            event.handled = True
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
            if self.action:
                self.action(self.text)

        elif event.type == pygame.KEYUP and focus == self:
            event.handled = True
            self.pressed = ''
            self.repeating = False
            self.repeat_timer = 0

        # Set focus
        if event.type == pygame.MOUSEBUTTONDOWN:
            focus = self if self.hovered else None

class Image(Component):
    def __init__(
            self,
            position,
            image_path,
            width=None,
            height=None
        ):
        super().__init__()

        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.width = width
        self.height = height

        # Image
        self.image_path = image_path
        self.update_image()

        eventHooks.append(self.event)

    def update_image(self):
        self.image = pygame.image.load(self.image_path)
        if not (self.width and self.height): return
        self.image = pygame.transform.smoothscale(self.image,(self.width,self.height))

    def draw(self):
        rect = root.disp.blit(self.image, (self.x, self.y))
        return rect

    def event(self,event):
        if event.type in (pygame.VIDEORESIZE,pygame.WINDOWMAXIMIZED):
            self.update_image()

class Progressbar(Component):
    def __init__(
            self,
            position,
            width,
            height,
            color=(30,85,230),
            border_color=(56,56,56),
            border_radius=4,
            corner_radius=4,
            speed=0
        ):
        super().__init__()
        
        # Style
        self.color = color
        self.borderColor = border_color
        self.borderRadius = border_radius
        self.corner_radius = corner_radius
        
        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.width = width
        self.height = height
        
        # Progress
        self.progress   = 0              # Progressbar state (0-1)
        self.max        = 1              # Max
        self.completed  = 0              # Current progress
        self.speed      = speed/10000    # How much to increase/tick
        self.started    = False          # Should we increase?
        self.halted     = False          # Should we increase? (if set progress < current progress)
        self.shouldHalt = True           # Should halt (option)
        self.realProg   = 0              # The last progress value sent to us
        self.tolerance  = 0.3            # Largest difference between prog (smoothed) and realProg can be before we halt

    def draw(self):
        # Tick
        if self.started and not self.halted:
            # Dynamically adjust the speed of the progress bar depending on
            # how far away we are from the last datapoint (realProg)
            # Im really fucking proud of making a better Progressbar than tkinter lmao
            speed = round(self.speed - max(self.progress-self.realProg,0)/100,5)

            self.progress += speed

        #print(f'Speed: {speed}')
        #print(f'Smooth: {self.progress} Real: {self.realProg}')
        
        # Run this shit to check if we should halt (for next frame)
        self.setProgress(self.completed,self.max)
        
        # Draw
        rect1 = pygame.draw.rect(
            root.disp,
            self.borderColor,
            pygame.Rect(self.abs_x,self.abs_y,self.width,self.height),
            self.borderRadius,
            self.corner_radius
        )
        rect2 = pygame.draw.rect(
            root.disp,
            self.color,
            pygame.Rect(
                self.abs_x+self.borderRadius,
                self.abs_y+self.borderRadius,
                min(max((self.width-self.borderRadius*2)*(self.progress),0),self.width-self.borderRadius*2),
                self.height-self.borderRadius*2
            ),
            0,
            self.corner_radius//2
        )
        
        return [rect1,rect2]
    
    def start(self):
        self.started = True
        
    def stop(self):
        self.started = False
    
    def setProgress(self,completed,max_=100):
        self.max = max_
        self.completed = completed
        
        progress = (self.completed/self.max)

        self.halted = self.progress > progress+self.tolerance and self.shouldHalt
        self.realProg = progress
        
        # only lets you decrease progress if not started.
        self.progress = round(max(self.progress, progress) if self.started else progress,5)

class Slider(Component):
    def __init__(
            self,
            position,
            width,
            height,
            color=(30, 85, 230),
            handle_color=(56, 56, 56),
            handle_radius=8,
            track_color=(200, 200, 200),
            track_height=4,
            action:FunctionType=None
    ):
        super().__init__()

        # Style
        self.color = color
        self.handleColor = handle_color
        self.handleRadius = handle_radius
        self.trackColor = track_color
        self.trackHeight = track_height

        # Position
        self.pos = position
        self.x = position[0]
        self.y = position[1]
        self.width = width
        self.height = height

        # Value
        self.value = 0
        self.pressed = False
        self.action = action
        
        eventHooks.append(self.event)

    def draw(self):
        # Tick
        self.checkHover()

        # Track movement
        if self.pressed:
            x = pygame.mouse.get_pos()[0]
            self.setValue((x-self.abs_x)/self.width)

        # Draw track
        track_y = self.abs_y + (self.height - self.trackHeight) // 2
        track = pygame.draw.rect(
            root.disp,
            self.trackColor,
            pygame.Rect(self.abs_x, track_y, self.width, self.trackHeight)
        )

        # Calculate handle position
        handle_x = self.abs_x + (self.width - self.handleRadius * 2) * ((self.value - 0) / (1 - 0))

        # Draw handle
        handle_y = self.abs_y + (self.height - self.handleRadius * 2) // 2
        handle = pygame.draw.circle(
            root.disp,
            self.handleColor,
            (int(handle_x + self.handleRadius), int(handle_y + self.handleRadius)),
            self.handleRadius
        )

        return [track, handle]

    def setValue(self, value):
        self.value = max(0, min(value, 1))
        if self.action:
            self.action(self.value)

    def event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                event.handled = True
                self.pressed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            event.handled = True
            self.pressed = False

class Line(Component):
    def __init__(
            self,
            from_:tuple[int,int],
            to:tuple[int,int],
            color=(255, 255, 255),
            width=5
        ):
        super().__init__()
        
        # Style
        self.color = color
        self.width = width
        
        # Position
        self.from_ = from_
        self.to    = to
        
        self.x       = from_[0]
        self.y       = from_[1]

    def draw(self):
        if not self.changed: return
        rect = pygame.draw.line(
            root.disp,
            self.color,
            self.from_,
            self.to,
            self.width
        )

        return rect

class Titlebar(Component):
    def __init__(
            self,
            text:str,
            height:int = 25,
            color = (40,40,40),
            border_radius:int = 5,
            size = 25,
            text_position = None
        ):
        super().__init__()

        self.text = text
        self.width = root.disp.get_width()
        self.height = height
        self.color = color
        self.border_radius = border_radius
        
        # Pos
        self.x = 0
        self.y = 0
        self.abs_x = 0
        self.abs_y = 0
        
        if text_position is None:
            text_position = (5,height//2-size//3)
        self.textPos = text_position
        self.dragPoint = (0,0)
        self.dragging = False
        
        # Style
        self.size = size
        self.visible = True
        self.changed = True
        
        # Close button
        self.close = Button(
            (root.disp.get_width()-25,0),
            25,
            25,
            'X',
            25,
            lambda: pygame.quit(),
            color=(40,40,40),
            hover_color=(175,60,60),
            corner_radius=5
        ).add(root,10)

        eventHooks.append(self.event)

    def draw(self):
        # Tick
        self.checkHover()
        if pygame.mouse.get_pressed()[0] and self.dragging:
            pos = root.window.position
            root.window.position = (pos[0] + root.width - self.dragPoint[0]), (pos[1] + root.height - self.dragPoint[1])

        # Bar
        bar = pygame.draw.rect(
            root.disp,
            self.color,
            (0,0,root.disp.get_size()[0],self.height),
            0,
            -1,
            self.border_radius,
            self.border_radius
        )
        
        # Text
        font = pygame.font.SysFont('Roboto',self.size)
        text = font.render(self.text,1,(255,255,255))
        root.disp.blit(text,self.textPos)
        
        # Close button in __init__
        
        return [bar,text]

    def event(self, event):
        global focus
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.dragPoint = event.dict['pos']
            self.dragging = True
            focus = self
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        
        elif event.type in (pygame.VIDEORESIZE,pygame.WINDOWMAXIMIZED):
            self.width = root.disp.get_width()
            self.close.setPos(self.width-27,self.close.y)

class Window(BasePositionManager,Component):
    def __init__(
            self,
            position:tuple[int,int],
            width:int,
            height:int,
            title:str,
            tb_height:int=25,
            corner_radius=5,
            color=(45, 45, 45),
            bg_focused_color=(50, 50, 50),
            font='Roboto',
            on_quit:FunctionType=nothing
        ):
        self.parent = None
        self.children = []
        self.onQuit = on_quit
        
        # Style
        self.title = title
        self.width = width
        self.height = height
        self.tb_height = tb_height
        self.corner_radius = corner_radius
        self.bgColor = color
        self.bgFocusedColor = bg_focused_color
        self.font = font
        self.hovered = False
        
        self.dragPoint = 0,0
        self.dragging = False
        self.nextPos = None
        
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
        self.quit_ = False
        
        # Close button
        self.close = Button(
            (self.width-27,3-self.tb_height),
            25,
            20,
            'X',
            25,
            self.quit,
            color=(40,40,40),
            hover_color=(175,60,60),
            corner_radius=5
        ).add(self,self.layer)

    def quit(self):
        self.parent.children.remove(self)
        root.update_all()
        self.quit_ = True
        self.onQuit()

    def draw(self):
        # Tick
        self.checkHovered()
        if focus == self:
            self.parent.children.remove(self)
            self.parent.children.append(self)
        
        if self.dragging:
            p = self.parent
            px = 0
            py = 0
            while True:
                px += p.x
                py += p.y
                if hasattr(p,'parent'):
                    p = p.parent
                else: break

            self.nextPos = (root.width-self.dragPoint[0]-px,root.height-self.dragPoint[1]-py)
            if not use_drag_rectangle: self.setPos(*self.nextPos)

        # Rendering
        ## Title bar
        color = self.bgFocusedColor if focus == self else self.bgColor

        # Rect
        bar = pygame.draw.rect(
            root.disp,
            (40,40,40),
            (self.abs_x,self.abs_y-self.tb_height,self.width,self.tb_height),
            border_top_left_radius=self.corner_radius,
            border_top_right_radius=self.corner_radius
        )
        # Text
        font:pygame.font.Font = pygame.font.SysFont(self.font,25)
        text = font.render(self.title,1,(255,255,255))
        root.disp.blit(text,(self.abs_x+10,self.abs_y+5-self.tb_height))
        
        ## Window background

        # Rect
        bg = pygame.draw.rect(
            root.disp,
            color,
            (self.abs_x,self.abs_y,self.width,self.height),
            border_bottom_left_radius=self.corner_radius,
            border_bottom_right_radius=self.corner_radius
        )

        # Dragging rectangle
        if self.dragging and use_drag_rectangle:
            rect = pygame.draw.rect(
                root.disp,
                (100,100,100),
                (root.width-self.dragPoint[0],root.height-self.dragPoint[1]-self.tb_height,self.width,self.height+self.tb_height),
                2,
                self.corner_radius
            )
            return [bar,bg,rect]
        return [bar,bg]
    
    def update(self):
        for child in self.children:
            if not hasattr(child,'orig_x'): child.orig_x = child.x
            if not hasattr(child,'orig_y'): child.orig_y = child.y

            child.x += self.x
            child.y += self.y

    def event(self, event):
        global focus

        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            event.handled = True
            self.dragPoint = event.dict['pos'][0]-self.abs_x, event.dict['pos'][1]-self.abs_y
            if self.dragPoint[1] < 0:
                self.dragging = True
            focus = self
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            if self.nextPos:
                self.setPos(*self.nextPos)
                self.update()

class Tab(BasePositionManager,Component):
    def __init__(self):
        super().__init__()

        global tab, tabCount
        self.id = tabCount
        tabCount += 1
        
        # Position
        self.x = 0
        self.y = 0
        self.width = root.width
        self.height = root.height

    def draw(self):
        global tab, tabs
        # Set visibility
        self.visible = (tab == self.id)

        for child in self.children:
            child.visible = self.visible

        return pygame.Rect(0,0,0,0)
    
    def update(self):
        for child in self.children:
            
            if not hasattr(child,'orig_x'): child.orig_x = child.x
            if not hasattr(child,'orig_y'): child.orig_y = child.y

            child.x += self.x
            child.y += self.y

class Frame(BasePositionManager,Component):
    def __init__(self,x,y,width,height):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def draw(self):
        return 0,0,0,0
    
    def update(self):
        for child in self.children:
            
            if not hasattr(child,'orig_x'): child.orig_x = child.x
            if not hasattr(child,'orig_y'): child.orig_y = child.y

            child.x += self.x
            child.y += self.y


class Root:
    def __init__(self,width,height,name='Default Title'):
        global root
        self.disp = pygame.display.set_mode((width,height),pygame.RESIZABLE)
        self.width = width
        self.height = height
        self.name = name

        root = self
    
    def draw(self, surface):
        pygame.display.set_caption(f'{self.name} - FPS: {round(clock.get_fps(),2)}')
        self.disp.fill((0,0,0))
        pygame.display.update(group.draw(surface))


running = True

def update():
    global running, frame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            return False
        elif event.type == pygame.VIDEORESIZE:
            pygame.display.update()
        for hook in eventHooks:
            hook(event)
    
    root.disp.fill((0,0,0))
    root.draw(root.disp)
    
    clock.tick(FPS)
    frame += 1

    return True

### ANIMATIONS ###

class Animation:
    def __init__(
            self,
            component,
            length,
            endPos,
            easing,
            ease_in=True,
            ease_out=True
        ):
        self.component = component
        self.length = length
        self.startPos = copy(component.pos)
        self.endPos = endPos
        self.easing = easing
        self.running = False
        
        self.easer = Easer(self.length,get_easing(easing,ease_in,ease_out))
    
    def start(self):
        Thread(target=self.start_blocking).start()
        return self
    
    def start_blocking(self):
        print(self.startPos,self.endPos)
        self.running = True
        for i in self.easer:
            try: i = next(i)+0.0001
            except StopIteration: break
            


            x = abs(self.startPos[0] - abs(self.endPos[0] - self.startPos[0]) * i)

            y = abs(self.startPos[1] - abs(self.endPos[1] - self.startPos[1]) * i)
                
            self.component.setPos(round(x),round(y))
            if not running: break
            t.sleep(1/120)
        self.running = False

class Easer:
    def __init__(self,length:int,easing_function:FunctionType):
        self.frame = -1
        self.length = length
        self.ease = easing_function
    
    def __len__(self):
        return self.length
    
    def __iter__(self):
        return self
    
    def __next__(self):
        self.frame += 1
        if self.frame > self.length: return
        yield self.ease(self.frame/self.length)

### LAYOUT MANAGER ###

class LayoutManager(BasePositionManager, Component):
    def __init__(self,x,y,width,height,padding):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width - padding
        self.height = height - padding
        self.padding = padding
        self.setPos(x+padding,y+padding)
        self.screen_width = root.width
        self.screen_height = root.height

        # Hook events
        eventHooks.append(self.event)

    def draw(self):
        return 0,0,0,0

    def event(self,event):
        if event.type == pygame.VIDEORESIZE:
            self.width += event.dict['w'] - self.screen_width
            self.height += event.dict['h'] - self.screen_height
            self.width = abs(self.width)
            self.height = abs(self.height)

            self.screen_width = event.dict['w']
            self.screen_height = event.dict['h']
            self.update()

    def setPos(self,x,y):
        self.x = x
        self.y = y
        if hasattr(self,'frame'): self.frame.setPos(x,y)

    def update(self):
        totalX = 0
        largestY = 0
        for i,child in enumerate(self.children):
            if not hasattr(child,'orig_x'): child.orig_x = child.x
            if not hasattr(child,'orig_y'): child.orig_y = child.y
            totalX += child.orig_x
            largestY = max(largestY,child.orig_y)

        x = 0
        y = 0
        for i,child in enumerate(self.children):
            child.width  = abs(self.width  / (totalX / child.orig_x) - self.padding)
            child.height = abs(self.height / (largestY / child.orig_y) - self.padding)

            print(f'{str(child):<50}: {round(x):<4}, {round(y):<4} - {round(child.width):<4}, {round(child.height):<4}')

            child.setPos(abs(round(x+self.x)),abs(round(y+self.y)))
            if isinstance(child,Image): child.update_image()
            x += child.width + self.padding


