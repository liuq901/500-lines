from io import StringIO

class Interpreter(object):
    def __init__(self):
        self.stack = []
        self.environment = {}
        self.output = StringIO()

    def LOAD_VALUE(self, number):
        self.stack.append(number)

    def LOAD_NAME(self, name):
        val = self.environment[name]
        self.stack.append(val)

    def STORE_NAME(self, name):
        val = self.stack.pop()
        self.environment[name] = val
    
    def PRINT_ANSWER(self):
        answer = self.stack.pop()
        print(answer)
        self.output.write(str(answer))

    def ADD_TWO_VALUES(self):
        first_num = self.stack.pop()
        second_num = self.stack.pop()
        total = first_num + second_num
        self.stack.append(total)

    def read_output(self):
        output = self.output.getvalue()
        self.output = StringIO()
        return output

    def parse_argument(self, instruction, argument, what_to_execute):
        numbers = ['LOAD_VALUE']
        names = ['LOAD_NAME', 'STORE_NAME']

        if instruction in numbers:
            argument = what_to_execute['numbers'][argument]
        elif instruction in names:
            argument = what_to_execute['names'][argument]

        return argument

    def execute(self, what_to_execute):
        instructions = what_to_execute['instructions']
        for each_step in instructions:
            instruction, argument = each_step
            argument = self.parse_argument(instruction, argument, what_to_execute)
            bytecode_method = getattr(self, instruction)
            if argument is None:
                bytecode_method()
            else:
                bytecode_method(argument)

def test_interpreter():
    interpreter = Interpreter()

    what_to_execute = {
        'instructions': [
            ('LOAD_VALUE', 0),
            ('LOAD_VALUE', 1),
            ('ADD_TWO_VALUES', None),
            ('PRINT_ANSWER', None),
        ],
        'numbers': [7, 5],
    }
    interpreter.execute(what_to_execute)
    assert interpreter.read_output() == '12'

    what_to_execute = {
        'instructions': [
            ('LOAD_VALUE', 0),
            ('LOAD_VALUE', 1),
            ('ADD_TWO_VALUES', None),
            ('LOAD_VALUE', 2),
            ('ADD_TWO_VALUES', None),
            ('PRINT_ANSWER', None),
        ],
        'numbers': [7, 5, 8],
    }
    interpreter.execute(what_to_execute)
    assert interpreter.read_output() == '20'

    what_to_execute = {
        'instructions': [
            ('LOAD_VALUE', 0),
            ('STORE_NAME', 0),
            ('LOAD_VALUE', 1),
            ('STORE_NAME', 1),
            ('LOAD_NAME', 0),
            ('LOAD_NAME', 1),
            ('ADD_TWO_VALUES', None),
            ('PRINT_ANSWER', None),
        ],
        'numbers': [1, 2],
        'names': ['a', 'b'],
    }
    interpreter.execute(what_to_execute)
    assert interpreter.read_output() == '3'

if __name__ == '__main__':
    test_interpreter()
