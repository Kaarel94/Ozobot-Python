# Python-like language for Ozobot

This is a Python-like language compiler that can be used to program the Ozobot bit robot.
None of this would have been possible without [this](https://github.com/AshleyF/ozobot)

## Language description
Below is a description of the given Python-like language which due to using the Python parser is a subset of Python with some added builtin methods to control the Ozobot bit with.

### Built in constants

8 color constants marking the 8 different colors Ozobot can undestand:
`BLACK`, `WHITE`, `GREEN`, `RED`, `BLUE`, `YELLOW`, `CYAN` and `MAGENTA`

4 direction constants used with the `there_is_way(direction)` and `pick_direction(direction)` functions described under line navigation:
`STRAIGHT`, `LEFT`, `RIGHT` and `BACK`

3 termination constants used by the `terminate(mode)` function:
`OFF`, `FOLLOW` and `IDLE`

### Values, variables and math

Only integer value in the range -127 to 127 and boolean values `True` and `False` are supported

Assigning variables is standard e.g `x = 5`. Multiple variable assignment is also possible e.g `x = y = 5` sets x and y to 5.

5 arithmetic operations are supprted: `+`, `-`, `*`, `/` and `%`

There are also 2 mathematical functions:
`random(low, high)` - generate a random value wihtin the given range
`abs(value)` - absolute value of the given parameter

### Movement

There are 3 built in functions to control the movement of the robot outside of line navigation:

`move(distance, speed)` - move forward by given distance (mm) and speed (mm/s).
`rotate(angle, speed)` - rotate by given angle (degrees) and speed y (mm/s).
`wheels(left, right)` - set the left and right wheel speeds (mm/s).

Stopping the robot is just `wheels(0, 0)`

Reading the surface color below the robot is `get_surface_color()`

### Line navigation

There are 4 built in functions to control the robot on line navigation:

`follow_line_to_intersect_or_end()` - follows a line to intersectsion or line end
`move_straight_until_line(speed)` - move forward at a given speed (mm/s) until a line is found
`there_is_way(direction)` - checks if there is a way(line) in the given direction.
`pick_direction(direction)` - picks a given direction at an intersection.

It is also possible to set and read the line following speed:
`set_line_speed(speed)` - sets the line following speed to the given value
`get_line_speed()` - gets the current line following speed

There is also `get_intersect_or_line_end_color()` which is similar to `get_surface_color()`, but is specifically meant for reading the color of the line the robot is navigating.

### Top LED

`color(red, green, blue)` - sets the top led color by the given red, green and blue values.

Turning the LED off is simply `color(0, 0, 0)`

### Timing and termination

`wait(seconds, centiseconds)` - waits for the given time
`terminate(mode)` - end program excecution on leave leave the robot in one of three modes: off, line following or idle. If this function is not called at the end of the programm a `terminate(OFF)` is implicitly added by the compiler at the end of the program.

### Conditional statements and logic

Standard Python `if` and `else` blocks are supported but the `elif` keyword is not.
Also the standard Python boolean operations `and`, `or` and `not` and comparison operators `<`, `>`, `==`, `<=`, `>=` and `!=` are supported.

### Loops

Only the standard `while` block is supported.

### Functions

It is possible to create functions wihtout parameters and return values with the standard `def` keyword.
Functions do not have their own scope and have to be declared before being called.

## Loading programs

See compilerTest.py or use the Thonny plugin

## Thonny plugin

I also created a thonny plugin which can be found [here](https://bitbucket.org/kaarel94/thonny-ozobot)
