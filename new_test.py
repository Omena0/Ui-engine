import engine as ui

root = ui.Root(800,600,'UI engine V2 test')


with ui.LayoutManager(
        x=0,
        y=0,
        width=root.width,
        height=root.height,
        padding=5
    ):

    ui.Image((1,1),'src/img.png',width=0,height=0).add()

    ui.Area((4,3),0,0,(30,40,60)).add()


while ui.update(): ...
