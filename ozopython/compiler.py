from ast import *

builtins = [
    'color',
    'wait',
    'move',
    'rotate',
    'wheels',
    'random',
    'get_surface_color',
    'terminate',
    'abs',
    'follow_line_to_intersect_or_end',
    'set_line_speed',
    'pick_direction',
    'move_straight_until_line',
    'there_is_way',
    'get_line_speed',
    'get_intersect_or_line_end_color',
]

colors = {
    'BLACK': 0,
    'RED': 1,
    'GREEN': 2,
    'YELLOW': 3,
    'BLUE': 4,
    'MAGENTA': 5,
    'CYAN': 6,
    'WHITE': 7,
}

directions = {
    'STRAIGHT': 1,
    'LEFT': 2,
    'RIGHT': 4,
    'BACK': 8,
}

terminate = {
    'OFF': 0,
    'FOLLOW': 1,
    'IDLE': 2,
}

VERSION = [0x01, 0x03]
KILL = [0x00, 0xAE]

class CompileException(BaseException):
    def __init__(self, msg, node):
        super(CompileException, self).__init__("{0}:{1}".format(node.lineno - 1, node.col_offset), msg)

class Compiler:
    def __init__(self):
        self.bytecode = []
        self.variable_counter = 0x2a
        self.variables = {}

    def calc_checksum(self):
        result = 0

        for byte in self.bytecode:
            result -= byte
            if result < 0:
                result += 256

        self.bytecode.append(result)

    def get_length_bytes(self):
        return [219 - len(self.bytecode), 0x00, len(self.bytecode)]

    def compile(self, root):
        self.compile_stmt(root)
        if self.bytecode[-1] != 0xae:
            self.bytecode.extend(KILL)
        self.bytecode = VERSION + self.get_length_bytes() + self.bytecode
        self.calc_checksum()

        return self.bytecode

    def compile_stmt(self, node):
        if type(node) == Module:
            for n in node.body:
                self.compile_stmt(n)
        elif type(node) == Expr:
            self.compile_expr(node.value)
        elif type(node) == Assign:
            self.assign(node.targets, node.value)
        elif type(node) == If:
            self.if_stmt(node)
        elif type(node) == While:
            self.while_loop(node)
        else:
            raise CompileException('Unsupported statement type %s.\n%s' % (str(type(node)), str(vars(node))), node)

    def compile_expr(self, node):
        if type(node) == Call:
            self.call(node)
        elif type(node) == Num:
            self.num(node)
        elif type(node) == Name:
            self.get_var(node)
        elif type(node) == NameConstant:
            self.name_constant(node)
        elif type(node) == BoolOp:
            self.bool_op(node)
        elif type(node) == Compare:
            self.compare(node)
        elif type(node) == UnaryOp:
            self.unary_op(node)
        elif type(node) == BinOp:
            self.bin_op(node)
        else:
            raise CompileException('Unsupported expression type %s.\n%s' % (str(type(node)), str(vars(node))), node)

    def assign(self, targets, value):
        for target in targets:
            if type(target) != Name:
                raise CompileException('Values can only be assigned to variables', target)

            if target.id in colors.keys():
                raise CompileException('Variable name cannot be one of the built in colors', target)

            if target.id in directions.keys():
                raise CompileException('Variable name cannot be one of the built in directions', target)

            if target.id in self.variables:
                key = self.variables[target.id]
            else:
                key = self.variable_counter
                self.variables[target.id] = key
                self.variable_counter += 1

            self.compile_expr(value)
            self.bytecode.extend([key, 0x93])

    def call(self, node):
        if node.func.id in builtins:
            getattr(self, node.func.id)(*node.args)
        else:
            raise CompileException("Unknown function call %s" % node.func.id, node)

    def num(self, node):
        value = node.n

        if value > 127:
            raise CompileException("Value %s outside of valid range" % value, node)

        self.push(value)

    def get_var(self, node):
        if node.id in colors.keys():
            self.push(colors[node.id])
        elif node.id in directions.keys():
            self.push(directions[node.id])
        elif node.id in terminate.keys():
            self.push(terminate[node.id])
        else:
            if node.id not in self.variables:
                raise CompileException('Undefined variable %s.' % node.id, node)

            key = self.variables[node.id]

            self.bytecode.extend([key, 0x92])

    def if_stmt(self, node):
        self.compile_expr(node.test)
        self.push(0x80)
        self.push(0)
        index = len(self.bytecode) - 1
        self.push(0x97)

        for n in node.body:
            self.compile_stmt(n)

        self.bytecode[index] = len(self.bytecode[index:]) + 1

        if len(node.orelse) > 0:
            self.bytecode[index] += 3
            self.push(0xba)
            self.push(0)
            index = len(self.bytecode) - 1
            self.push(0x97)

            for n in node.orelse:
                self.compile_stmt(n)

            self.bytecode[index] = len(self.bytecode[index:]) + 1

    def name_constant(self, node):
        if type(node.value) != bool:
            raise CompileException('Only boolean constant type is supported. %s' % type(node.value), node)
        self.push(1 if node.value else 0)

    def bool_op(self, node):
        self.compile_expr(node.values[0])
        for i in range(1, len(node.values)):
            self.compile_expr(node.values[i])
            if type(node.op) == And:
                self.push(0xa2)
            elif type(node.op) == Or:
                self.push(0xa3)
            elif type(node.op) == Not:
                self.push(0x8a)
            else:
                raise CompileException("Unknown operator %s" % type(node.op), node.op)

    def compare(self, node):
        self.compile_expr(node.left)
        for i in range(len(node.ops)):
            self.compile_expr(node.comparators[i])
            self.compare_ops(node.ops[i])

    def compare_ops(self, op):
        if type(op) == Eq:
            self.push(0xa4)
        elif type(op) == NotEq:
            self.push(0xa4)
            self.push(0x8a)
        elif type(op) == Lt:
            self.push(0x9c)
            self.push(0x8a)
        elif type(op) == LtE:
            self.push(0x9d)
            self.push(0x8a)
        elif type(op) == Gt:
            self.push(0x9d)
        elif type(op) == GtE:
            self.push(0x9c)
        else:
            raise CompileException('Unsupported operator', op)

    def unary_op(self, node):
        if type(node.op) == Not:
            self.compile_expr(node.operand)
            self.push(0x8a)
        elif type(node.op) == USub:
            self.compile_expr(node.operand)
            # self.bytecode[-1] -= 1
            self.push(0x8b)
        else:
            raise CompileException('Unsupported operator', node.op)

    def bin_op(self, node):
        self.compile_expr(node.left)
        self.compile_expr(node.right)
        if type(node.op) == Add:
            self.push(0x85)
        elif type(node.op) == Sub:
            self.push(0x86)
        elif type(node.op) == Mult:
            self.push(0x87)
        elif type(node.op) == Div:
            self.push(0x88)
        elif type(node.op) == Mod:
            self.push(0x89)
        else:
            raise CompileException('Unsupported operator', node.op)

    def while_loop(self, node):
        # Infinite loop
        if type(node.test) == NameConstant and node.test.value:
            jump_index = len(self.bytecode)
            for n in node.body:
                self.compile_stmt(n)
            self.push(0xba)
            self.push(256 - len(self.bytecode[jump_index:]) + 1)
            self.push(0x97)
        elif type(node.test) == NameConstant and not node.test.value:
            return
        else:
            jump_back_index = len(self.bytecode)
            self.compile_expr(node.test)
            self.push(0x80)
            self.push(0)
            jump_index = len(self.bytecode) - 1
            self.push(0x97)

            for n in node.body:
                self.compile_stmt(n)

            self.push(0xba)
            self.push(256 - len(self.bytecode[jump_back_index:]) + 1)
            self.push(0x97)

            self.bytecode[jump_index] = len(self.bytecode[jump_index:]) + 1

    def move(self, distance, speed):
        self.compile_expr(distance)
        self.compile_expr(speed)
        self.push(0x9E)

    # S 100 wait 1 - dup 00 > not if -8 97 96 T wait
    def wait(self, seconds, centisec):
        self.compile_expr(seconds)

        if self.bytecode[-1] == 0:
            del self.bytecode[-1]
        else:
            self.bytecode.extend([0x64, 0x9b, 0x1, 0x86, 0x94, 0x0, 0x9d, 0x8a, 0x80, 0xf8, 0x97, 0x96])

        self.compile_expr(centisec)
        self.push(0x9B)

    def color(self, red, green, blue):
        self.compile_expr(red)
        self.compile_expr(green)
        self.compile_expr(blue)
        self.push(0xB8)

    def rotate(self, degree, speed):
        self.compile_expr(degree)
        self.compile_expr(speed)
        self.push(0x98)

    def wheels(self, left, right):
        self.compile_expr(left)
        self.compile_expr(right)
        self.push(0x9f)

    def random(self, low, high):
        self.compile_expr(high)
        self.compile_expr(low)
        self.push(0x8c)

    def get_surface_color(self):
        self.push(0xe)
        self.push(0x92)

    def terminate(self, value):
        self.compile_expr(value)
        self.push(0xae)

    def abs(self, value):
        self.compile_expr(value)
        self.push(0xa8)

    # call 00 09 00 end 01 a0 ac ad 9a 10 = if fd 00 a0 01 25 93 ;
    def follow_line_to_intersect_or_end(self):
        # length = len(self.bytecode)
        # self.bytecode.extend([0x90, 0x00, 0x05, 0x00, 0xae, 0x01, 0xa0, 0xac, 0xad, 0x9a, 0x10, 0xa4, 0x80, 0xfd, 0x00, 0xa0, 0x01, 0x29, 0x93, 0x91])
        # self.bytecode.extend([0x01, 0xa0, 0xac, 0xad, 0x9a, 0x10, 0xa4, 0x80, 0xfd, 0x00, 0xa0, 0x01, 0x29, 0x93])
        self.bytecode.extend([0x01, 0xa0, 0xac, 0xad, 0x9a, 0x10, 0xa4, 0x80, 0xfd, 0x00, 0xa0, 0x01, 0x29, 0x93])

    def set_line_speed(self, speed):
        self.compile_expr(speed)
        self.push(0x18)
        self.push(0x93)

    def move_straight_until_line(self, speed):
        self.compile_expr(speed)
        # S dup dup wheels ac 08 sensor if -8 97 96 00 00 wheels c6 01 a0 ac ad 9a 10 = if -3 97 00 a0 01 25 93
        # dup dup wheels ac 08 get if fa 97 drop 00 00 wheels c6 01 a0 ac ad 9a 10 = if fd 97 00 a0 01 29 set
        self.bytecode.extend([0x94, 0x94, 0x9f, 0xac, 0x08, 0x92, 0x80, 0xfa, 0x97, 0x96, 0x00, 0x00, 0x9f, 0xc6, 0x01, 0xa0, 0xac, 0xad, 0x9a, 0x10, 0xa4, 0x80, 0xfd, 0x97, 0x00, 0xa0, 0x01, 0x29, 0x93])

    def pick_direction(self, direction):
        if type(direction) != Name and direction.id not in directions.keys():
            raise CompileException('Unsupported direction', direction)

        self.compile_expr(direction)
        # dup 10 get 81 not b7 29 get not b7 1f set 01 a0 ad 9a 14 = if fd 00 a0 00 29 set
        self.bytecode.extend([0x94, 0x10, 0x92, 0x81, 0x8a, 0xb7, 0x29, 0x92, 0x8a, 0xb7, 0x1f, 0x93, 0x01, 0xa0, 0xad, 0x9a, 0x14, 0xa4, 0x80, 0xfd, 0x00, 0xa0, 0x00, 0x29, 0x93])

    def there_is_way(self, direction):
        if type(direction) != Name and direction.id not in directions.keys():
            raise CompileException('Unsupported direction', direction)

        self.push(0x10)
        self.push(0x92)
        self.compile_expr(direction)
        self.push(0x81)

    def get_line_speed(self):
        self.push(0x18)
        self.push(0x92)

    def get_intersect_or_line_end_color(self):
        self.push(0x0f)
        self.push(0x92)

    def push(self, byte):
        self.bytecode.append(byte)
