from ozopython.colorLanguageTranslator import ColorLanguageTranslator
from .ozopython import *
from tkinter import *

def run(filename):
    code = ozopython.compile(filename)
    colorcode = ColorLanguageTranslator.translate(code)

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

