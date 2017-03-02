import ozobot

def change_color(red, green, blue):
    ozobot.color(red, green, blue)
    ozobot.wait(100)

change_color(127, 0, 0)
ozobot.move(100, 100)
change_color(0, 127, 0)
ozobot.move(100, 100)
ozobot.rotate(90, 100)
change_color(0, 0, 127)
ozobot.move(100, 100)

ozobot.compile()