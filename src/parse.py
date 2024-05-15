# This is used to create a gui from a .ui file

import engine as ui
import sys

sys.argv.append('src/test.ui')

with open(sys.argv[1]) as f:
    source = f.read().splitlines()

def getLevel(expr:str) -> int:
    return expr.count('    ',0,expr.rfind('    ')+4)

def getAttrs(line:int) -> dict:
    expr = source[line]
    level = getLevel(expr)
    print(level,expr)

    if expr.strip() == '': return
    if expr.strip().startswith('#'): return

    attr = {}
    key,value = expr.split('=')
    key,value = key.strip(), value.strip()
    value = eval(value)

    attr[key] = value
    if getLevel(source[line+1]) < level:
        return attr
    a = getAttrs(line+1)
    if a is None: return attr
    attr |= a
    return attr

def parseExpr(line:int,parent='root'):
    if line >= len(source): return
    expr = source[line]
    level = getLevel(expr)
    print(level,expr)
    expr = expr.strip()
    
    if expr == '':
        return parseExpr(line+1)

    if expr.startswith('#'):
        attr = getAttrs(line+1)
        if not attr:
            return parseExpr(line+1)
        
        if expr == '#root':
            if 'bg' not in attr.keys():
                attr['bg'] = (100,100,100)

            ui.Root(title=attr['title'],bg=attr['bg'])
            ui.root.width  = attr['size'][0]
            ui.root.height = attr['size'][1]
        
        elif expr.startswith('#'):
            getattr(ui,expr.replace('#','').capitalize())(
                **attr
            ).add(ui.root)
        
    
        return parseExpr(line+len(attr)+1)

    if expr.strip() == '!run':
        ui.root.show()
        ui.mainloop()



parseExpr(0)

