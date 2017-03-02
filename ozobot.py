from tkinter import *

START = "CRYCYMCRW"
END = "CMW"
VERSION = [0x01, 0x03]
KILL = [0x00, 0xAE]

program = []

def base7(num):
    numerals = "0123456"
    return ((num == 0) and numerals[0]) or (base7(num // 7).lstrip(numerals[0]) + numerals[num % 7])

# Function for converting a base-7 number(given as a string) to a 3 digit color code:
def base7_to_color_code(num):
    colorDict = {
        '0': 'K',
        '1': 'R',
        '2': 'G',
        '3': 'Y',
        '4': 'B',
        '5': 'M',
        '6': 'C',
    }

    if len(num) == 1:
        num = "00" + num
    elif len(num) == 2:
        num = "0" + num

    chars = list(num)

    return colorDict[chars[0]] + colorDict[chars[1]] + colorDict[chars[2]]

def calc_checksum(array):
    result = 0

    for byte in array:
        result -= byte
        if result < 0:
            result += 256

    return int(hex(result),16)


# TODO: make it possible to have longer than 256 byte programs
def get_length_bytes(array):
    return [219 - len(array), 0x00, len(array)]

def color(red, green, blue):
    if red > 127:
        red = 127
    if green > 127:
        green = 127
    if blue > 127:
        blue = 127

    if red < 0:
        red = 0
    if green < 0:
        green = 0
    if blue < 0:
        blue = 0

    program.extend([int(hex(red), 16), int(hex(green), 16), int(hex(blue), 16), 0xB8])

# TODO: make it possible to set wait timer more precisely
def wait(time):
    if time < 0:
        return
    if time > 127:
        time = 127

    program.extend([time, 0x9B])

def move(distance, speed):
    if distance < 0:
        distance = 0
    if distance > 127:
        distance = 127
    if speed < 0:
        speed = 0
    if speed > 127:
        speed = 127

    program.extend([distance, speed, 0x9E])

def rotate(degree, speed):
    if degree < 0:
        degree = 0
    elif degree > 127:
        degree = 127
    if speed < 0:
        speed = 0
    elif speed > 127:
        speed = 127

    program.extend([degree, speed, 0x98])

def compile():
    program.extend(KILL)

    programByteArray = VERSION + get_length_bytes(program) + program

    checksum = base7_to_color_code(base7(calc_checksum(programByteArray)))

    colorSequence = "".join([base7_to_color_code(base7(int(str(x)))) for x in programByteArray])

    programWithRepetition = START + colorSequence + checksum + END

    endProgram = ""
    for i, c in enumerate(programWithRepetition):
        if i == 0 or programWithRepetition[i - 1] != c or endProgram[i - 1] == 'W':
            endProgram += c
        else:
            endProgram += 'W'

    print(endProgram)

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

    button = Button(window, text="Load", command=lambda: load(endProgram))
    button.pack()

    canvas = Canvas(window, height=350, width=350)
    circle = canvas.create_oval(25, 25, 325, 325, fill="white")

    canvas.pack()

    window.mainloop()