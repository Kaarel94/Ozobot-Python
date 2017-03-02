# This code is largely based on https://github.com/AshleyF/ozobot
#
# An ozobot program is just a sequence of bytes encoded into color codes
# Color codes consist of 8 (7 + white) different colors:
# White, R, G, B, C, M, Y, K (black)
# Each color is a 3-bit value (or a single digit in base-7):
#   base-7  base-2  color
#   0       000     Black
#   1       001     Red
#   2       010     Green
#   3       011     Yellow (R+G)
#   4       100     Blue
#   5       101     Magenta (R+B)
#   6       110     Cyan (G+B)
#
# The eighth color is White(111), but is different from the other colors since it isn't used as a value,
# but rather signifies repetition, since no color can occur twice in a row in an ozobot program.
# For example KWK is just 000
#
#
# Programs are "framed" by:
# CRY CYM CRW ... CMW
# The first three "words" are CRY CYM CRW followed by a sequence of encoded bytes and finally by CMW.
# These framing words starting with cyan (C) decode to values outside of a single byte range
# (hex 130, 140, 12E and 14E). Everything between however seems to always decode to bytes
#
#
# The bytes within frames appear to be in the form:
# VV UU XX YY ZZ ... CK
# Giving a version, length and checksum. Bytes within this "envelope" are program instructions.
#
# VV and UU may be a version number? They have been observed to always be 1 and 3 currently.
#
# It's not fully understood yet, but ZZ (probably combined with YY) appears to be the length of the program instructions
# (up to the checksum). XX is, for some reason that's still a mystery, always 219-length.
# YY has only been observed to be zero, but likely it's the high bits of ZZ when programs longer than 255 (FF) are sent.
#
# CK is a checksum to detect misreading. It is constructed from the whole payload up to the checksum -
# version, length and program bytes.
#
# The checksum has been found to be simply a single-byte (underflowed) running difference between the bytes
# of the envelope, starting with zero. That is, subtract the first byte from zero,
# subtract the second byte from this, the third from that, and so on; keeping a running value.
from tkinter import *


# Function for converting decimal to base-7. This is a slightly modified function taken from
# http://stackoverflow.com/questions/2267362/how-to-convert-an-integer-in-any-base-to-a-string
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

    return hex(result)

start = "CRYCYMCRW"  # Starting color codes which all programs are framed by
end = "CMW"  # Ending color code which all programs are framed by
# version = "KKRKKY"  # 01 and 03 in base 7 color codes described above


# Following two values are based on the program itself
# length = "BKKKKKKYG"  # color coded length(XX YY ZZ) of our static program
# checksum = "BMC"  # color coded checksum(CK) of our static program

# A program itself as a an array of base-16 encoded bytes.
#
# This is a simple program that flashes red green and blue once with a second interval and then stops
# the first five bytes of this program are the version and length bytes described above.
# next four bytes(0x7F, 0x00, 0x00, 0xB8) make up the command to change ozobots LED to red
# More specifically B8 is the command to change the color of the LED and 7F 00 00 are 3 parameters(red, green, blue)
# passed to the command. Next are 2 bytes that tell ozobot to wait for 1 second. 9B is the wait command
# and 64 is the argument passed to it. The wait command waits for argument x 10ms and 64hex = 100dec.
# after that the change LED and wait command are repeated twice more and at the end of the program there are two
# bytes that tell the ozobot to terminate the program and turn ozobot off. AE is the byte command to terminate
# the program and 00 is the parameter to that command that tells ozobot to turn off after the program
# has been terminated. Values between 00 and 7F (0-127 dec) are considered literals and so command arguments
# can be changed within this ranges and the program will continue to work.
programByteArray = [0x01, 0x03, 0xC4, 0x00, 0x14, 0x7F, 0x00, 0x00, 0xB8, 0x64, 0x9B, 0x00, 0x7F,
           0x00, 0xB8, 0x64, 0x9B, 0x00, 0x00, 0x7F, 0xB8, 0x64, 0x9B, 0x00, 0xAE]

# calculate checksum and translate it to a color code
checksum = base7_to_color_code(base7(int(calc_checksum(programByteArray), 16)))

# Convert our byte array to a string of color codes
colorSequence = "".join([base7_to_color_code(base7(int(str(x)))) for x in programByteArray])

# Glue everything together
programWithRepetition = start + colorSequence + checksum + end

# Remove repetition by replacing repeats with white
program = ""
for i, c in enumerate(programWithRepetition):
    if i == 0 or programWithRepetition[i-1] != c or program[i-1] == 'W':
        program += c
    else:
        program += 'W'

print(program)

# Everything related to tkinter
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

button = Button(window, text="Load", command= lambda: load(program))
button.pack()

canvas = Canvas(window, height=350, width=350)
circle = canvas.create_oval(25, 25, 325, 325, fill="white")

canvas.pack()

window.mainloop()