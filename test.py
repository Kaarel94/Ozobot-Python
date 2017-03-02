import ozobot

def change_color(red, green, blue):
    ozobot.color(red, green, blue)
    ozobot.wait(50)

change_color(127, 127, 0)
change_color(0, 127, 0)
change_color(0, 0, 127)

ozobot.compile()