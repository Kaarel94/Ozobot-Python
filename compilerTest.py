import ast
from tkinter import *

from ozopython.compiler import Compiler
from ozopython.colorLanguageTranslator import ColorLanguageTranslator

node = ast.parse('''
x = -10
while x <= 10:
    color(random(-127, 127), random(-127, 127), random(-127, 127))
    wheels(random(-127, 127), random(-127, 127))
    wait(1, 0)
    x = x + 1
terminate(IDLE)
''')

print(ast.dump(node))
# print(type(node))

compiler = Compiler()
code = compiler.compile(node)
print(code)
print(' '.join([hex(x) for x in code]))
print('0 19 93 19 92 64 9c 8a 80 13 97 0 19 92 0 b8 2 9b 19 92 1 85 19 93 ba eb 97 2 ae')

colorcode = ColorLanguageTranslator.translate(code)
print(colorcode)


def load(prog):
    colormap = {
        'K': "#000000",
        'R': "#ff0000",
        'G': "#00ff00",
        'Y': "#ffff00",
        'B': "#0000ff",
        'M': "#ff00ff",
        'C': "#00ffff",
        'W': "#ffffff"
    }

    head, *tail = prog
    canvas.itemconfig(circle, fill=colormap[head])
    prog = tail
    if len(prog) != 0:
        canvas.after(50, lambda: load(prog))


window = Tk()

button = Button(window, text="Load", command=lambda: load(colorcode))
button.pack()

canvas = Canvas(window, height=350, width=350)
circle = canvas.create_oval(25, 25, 325, 325, fill="white")

canvas.pack()

window.mainloop()