import engine
import random as r
import time as t
from threading import Thread

root = engine.Root('Slot machine')
root.res = 500,450

spinning = False
balance = 5000

title = engine.Text(
    position = (125,50),
    text = f'Balance: {balance}$',
    size = 50
).add(root)

slot1 = engine.Text(
    position = (125,150),
    text = '0',
    size = 150
).add(root)

slot2 = engine.Text(
    position = (225,150),
    text = '0',
    size = 150
).add(root)

slot3 = engine.Text(
    position = (325,150),
    text = '0',
    size = 150
).add(root)

def inc_string(x:str) -> str:
    return str((int(x)+1) % 9)

def spin_slot():
    global slot1, slot2, slot3, spinning, balance, title
    time = 0.00025
    if spinning: return
    spinning = True
    a = r.randint(0,10)+25
    b = r.randint(0,9)+a+19
    c = r.randint(0,9)+b+9
    print(f'Slots: {a}', b, c)
    for i in range(c):
        if i < a:
            slot1.text = inc_string(slot1.text)
        if i < b:
            slot2.text = inc_string(slot2.text)
        if i < c:
            slot3.text = inc_string(slot3.text)
        #engine.update()
        time = time*1.1111
        t.sleep(time+0.025)

    spinning = False

    slots = {slot1.text, slot2.text, slot3.text}
    if len(slots) == 1:
        if slot1.text == '7':
            print('JAKPOT: 7777$')
            balance += 7777
        else:
            print(f'3 OF SAME: {int(slot1.text)*111}$')
            balance += int(slot1.text)*111

    elif len(slots) == 2:
        print('2 OF SAME: 25$')
        balance += 25

    else:
        print('You lost 10$.')
        balance -= 10

    title.text = f'Balance: {balance}$'


button = engine.Button(
    position = (150,300),
    width = 200,
    height = 100,
    text = 'Spin!',
    size = 100,
    action = lambda: Thread(target=spin_slot).start()
).add(root)


root.show()
engine.mainloop()