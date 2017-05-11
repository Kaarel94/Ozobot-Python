from tkinter import ttk

from ozopython.colorLanguageTranslator import ColorLanguageTranslator
from .ozopython import *
from tkinter import *

def run(filename):
    code = ozopython.compile(filename)
    colorcode = ColorLanguageTranslator.translate(code)

    def load(prog, prog_bar):
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
        prog_bar["value"] = len(colorcode) - len(prog)
        if len(prog) != 0:
            canvas.after(50, lambda: load(prog, prog_bar))

    window = Tk()

    progress = ttk.Progressbar(window, orient="horizontal", length='5c', mode="determinate")
    progress["value"] = 0
    progress["maximum"] = len(colorcode)

    button = Button(window, text="Load", command=lambda: load(colorcode, progress))
    button.pack()

    progress.pack()

    canvas = Canvas(window, height='6c', width='6c')
    circle = canvas.create_oval('0.5c', '0.5c', '5.5c', '5.5c', fill="white")

    canvas.pack()

    window.mainloop()

