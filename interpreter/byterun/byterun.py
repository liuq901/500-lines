import collections
import dis
import functools
import inspect
import io
import operator
import sys
import types

class Cell(object):
    def __init__(self, value):
        self.set(value)

    def get(self):
        return self.value

    def set(self, value):
        self.value = value

class Frame(object):
    def __init__(self, code_obj, global_names, local_names, prev_frame):
        self.code_obj = code_obj
        self.global_names = global_names
        self.local_names = local_names
        self.prev_frame = prev_frame
        self.stack = []
        if prev_frame:
            self.builtin_names = prev_frame.builtin_names
        else:
            self.builtin_names = local_names['__builtins__']
            if hasattr(self.builtin_names, '__dict__'):
                self.builtin_names = self.builtin_names.__dict__

        self.last_instruction = 0
        self.block_stack = []

        if code_obj.co_cellvars:
            self.cells = {}
            if not prev_frame.cells:
                prev_frame.cells = {}
            for var in code_obj.co_cellvars:
                cell = Cell(self.local_names[var])
                prev_frame.cells[var] = self.cells[var] = cell
        else:
            self.cells = None

        if code_obj.co_freevars:
            if not self.cells:
                self.cells = {}
            for var in code_obj.co_freevars:
                self.cells[var] = prev_frame.cells[var]

    def top(self):
        return self.stack[-1]

    def pop(self):
        return self.stack.pop()

    def push(self, *vals):
        self.stack.extend(vals)

    def popn(self, n):
        if n:
            ret = self.stack[-n:]
            self.stack[-n:] = []
            return ret
        else:
            return []

    def rotate(self, n):
        tmp = self.top()
        for i in range(1, n):
            self.stack[-i] = self.stack[-(i + 1)]
        self.stack[-n] = tmp

    def push_block(self, b_type, handler=None):
        stack_height = len(self.stack)
        self.block_stack.append(Block(b_type, handler, stack_height))

    def pop_block(self):
        return self.block_stack.pop()

    def unwind_block(self, block):
        if block.type == 'except-handler':
            offset = 3
        else:
            offset = 0

        while len(self.stack) > block.stack_height + offset:
            self.pop()

        if block.type == 'except-handler':
            traceback, value, exctype = self.popn(3)
            return exctype, value, traceback

Block = collections.namedtuple('Block', ['type', 'handler', 'stack_height'])

class Function(object):
    __slots__ = [
        'func_code', 'func_name', 'func_defaults', 'func_globals',
        'func_locals', 'func_dict', 'func_closure',
        '__name__', '__dict__', '__doc__', '_vm', '_func',
    ]

    def __init__(self, name, code, globs, defaults, closure, vm):
        self._vm = vm
        self.func_code = code
        self.func_name = self.__name__ = name or code.co_name
        self.func_defaults = tuple(defaults)
        self.func_globals = globs
        self.func_locals = self._vm.frame.local_names
        self.__dict__ = {}
        self.func_closure = closure
        self.__doc__ = code.co_consts[0] if code.co_consts else None

        kw = {
            'argdefs': self.func_defaults,
        }
        if closure:
            kw['closure'] = tuple(make_cell(0) for _ in closure)
        self._func = types.FunctionType(code, globs, **kw)

    def __call__(self, *args, **kwargs):
        callargs = inspect.getcallargs(self._func, *args, **kwargs)
        frame = self._vm.make_frame(self.func_code, callargs, self.func_globals, {})
        return self._vm.run_frame(frame)

def make_cell(value):
    fn = (lambda x: lambda: x)(value)
    return fn.__closure__[0]

class VirtualMachineError(Exception):
    pass

class VirtualMachine(object):
    def __init__(self):
        self.frames = []
        self.frame = None
        self.extended_arg = 0
        self.return_value = None
        self.last_exception = None
        self.log = io.StringIO()

    def make_frame(self, code, callargs={}, global_names=None, local_names=None):
        if global_names is not None and local_names is not None:
            local_names = global_names
        elif self.frames:
            global_names = self.frame.global_names
            local_names = {}
        else:
            global_names = local_names = {
                '__builtins__': __builtins__,
                '__name__': '__main__',
                '__doc__': None,
                '__package__': None,
            }
        local_names.update(callargs)
        frame = Frame(code, global_names, local_names, self.frame)
        return frame

    def push_frame(self, frame):
        self.frames.append(frame)
        self.frame = frame

    def pop_frame(self):
        self.frames.pop()
        if self.frames:
            self.frame = self.frames[-1]
        else:
            self.frame = None

    def jump(self, jump):
        self.frame.last_instruction = jump

    def run_code(self, code, global_names=None, local_names=None):
        frame = self.make_frame(code, global_names=global_names, local_names=local_names)

        self.run_frame(frame)

        if self.frames:
            raise VirtualMachineError('Frames left over!')
        if self.frame and self.frame.stack:
            raise VirtualMachineError(f'Data left on stack! {self.frame.stack}')

    def parse_byte_and_args(self):
        f = self.frame
        opoffset = f.last_instruction
        byteCode = f.code_obj.co_code[opoffset]
        f.last_instruction += 2
        byte_name = dis.opname[byteCode]
        arg_val = f.code_obj.co_code[opoffset + 1] + (self.extended_arg << 8)
        self.extended_arg = 0
        if byteCode in dis.hasconst:
            arg = f.code_obj.co_consts[arg_val]
        elif byteCode in dis.hasname:
            arg = f.code_obj.co_names[arg_val]
        elif byteCode in dis.haslocal:
            arg = f.code_obj.co_varnames[arg_val]
        elif byteCode in dis.hasjrel:
            arg = f.last_instruction + arg_val
        elif byteCode in dis.hasfree:
            if arg_val < len(f.code_obj.co_cellvars):
                arg = f.code_obj.co_cellvars[arg_val]
            else:
                idx = arg_val - len(f.code_obj.co_cellvars)
                arg = f.code_obj.co_freevars[idx]
        else:
            arg = arg_val
        argument = [arg]

        return byte_name, argument

    def dispatch(self, byte_name, argument):
        why = None
        try:
            bytecode_fn = getattr(self, f'byte_{byte_name}', None)
            if bytecode_fn is None:
                if byte_name.startswith('UNARY_'):
                    self.unaryOperator(byte_name[6:])
                elif byte_name.startswith('BINARY_'):
                    self.binaryOperator(byte_name[7:])
                elif byte_name.startswith('INPLACE_'):
                    self.binaryOperator(byte_name[8:])
                else:
                    raise VirtualMachineError(f'unsupported bytecode type {byte_name}')
            else:
                why = bytecode_fn(*argument)
        except BaseException:
            self.last_exception = sys.exc_info()[:2] + (None,)
            why = 'exception'

        print(byte_name, argument, self.frame.stack, file=self.log)

        return why

    def manage_block_stack(self, why):
        block = self.frame.block_stack[-1]

        if block.type == 'loop' and why == 'continue':
            self.jump(self.return_value)
            why = None
            return why

        self.frame.pop_block()
        current_exc = self.frame.unwind_block(block)
        if current_exc is not None:
            self.last_exception = current_exc

        if block.type == 'loop' and why == 'break':
            self.jump(block.handler)
            why = None
        elif block.type in ['setup-except', 'finally'] and why == 'exception':
            self.frame.push_block('except-handler')
            exctype, value, tb = self.last_exception
            self.frame.push(tb, value, exctype)
            self.frame.push(tb, value, exctype)
            self.jump(block.handler)
            why = None
        elif block.type == 'finally':
            if why in ('return', 'continue'):
                self.frame.push(self.return_value)
            self.frame.push(why)
            self.jump(block.handler)
            why = None

        return why

    def run_frame(self, frame):
        self.push_frame(frame)

        yield_list = None
        while True:
            byte_name, argument = self.parse_byte_and_args()

            why = self.dispatch(byte_name, argument)

            if why == 'yield':
                if yield_list is None:
                    yield_list = []
                yield_list.append(self.return_value)
                why = None

            while why and frame.block_stack:
                why = self.manage_block_stack(why)

            if why:
                break

        self.pop_frame()

        if why == 'exception':
            exc, val, tb = self.last_exception
            e = exc(val)
            e.__traceback__ = tb
            raise e

        if yield_list is not None:
            self.return_value = yield_list
        return self.return_value

    def check_zero_arg(self, arg, byte_name):
        if arg != 0:
            raise VirtualMachineError(f'{byte_name} has non-zero argument!')

    def byte_NOP(self, arg):
        self.check_zero_arg(arg, 'NOP')

    def byte_LOAD_CONST(self, const):
        self.frame.push(const)

    def byte_POP_TOP(self, arg):
        self.check_zero_arg(arg, 'POP_TOP')
        self.frame.pop()

    def byte_DUP_TOP(self, arg):
        self.check_zero_arg(arg, 'DUP_TOP')
        self.frame.push(self.frame.top())

    def byte_DUP_TOP_TWO(self, arg):
        self.check_zero_arg(arg, 'DUP_TOP_TWO')
        self.frame.push(self.frame.stack[-2])
        self.frame.push(self.frame.stack[-2])

    def byte_ROT_TWO(self, arg):
        self.check_zero_arg(arg, 'ROT_TWO')
        self.frame.rotate(2)

    def byte_ROT_THREE(self, arg):
        self.check_zero_arg(arg, 'ROT_THREE')
        self.frame.rotate(3)

    def byte_ROT_FOUR(self, arg):
        self.check_zero_arg(arg, 'ROT_FOUR')
        self.frame.rotate(4)

    def byte_LOAD_NAME(self, name):
        frame = self.frame
        if name in frame.local_names:
            val = frame.local_names[name]
        elif name in frame.global_names:
            val = frame.global_names[name]
        elif name in frame.builtin_names:
            val = frame.builtin_names[name]
        else:
            raise NameError(f'name \'{name}\' is not defined')
        self.frame.push(val)

    def byte_STORE_NAME(self, name):
        self.frame.local_names[name] = self.frame.pop()

    def byte_DELETE_NAME(self, name):
        del self.frame.local_names[name]

    def byte_LOAD_FAST(self, name):
        if name.startswith('.'):
            name = name.replace('.', 'implicit')
        if name in self.frame.local_names:
            val = self.frame.local_names[name]
        else:
            raise UnboundLocalError(f'local variable \'{name}\' referenced before assignment')
        self.frame.push(val)

    def byte_STORE_FAST(self, name):
        self.frame.local_names[name] = self.frame.pop()

    def byte_DELETE_FAST(self, name):
        del self.frame.local_names[name]

    def byte_LOAD_GLOBAL(self, name):
        f = self.frame
        if name in f.global_names:
            val = f.global_names[name]
        elif name in f.builtin_names:
            val = f.builtin_names[name]
        else:
            raise NameError(f'global name \'{name}\' is not defined')
        f.push(val)

    def byte_STORE_GLOBAL(self, name):
        self.frame.global_names[name] = self.frame.pop()

    def byte_LOAD_DEREF(self, name):
        self.frame.push(self.frame.cells[name].get())

    def byte_STORE_DEREF(self, name):
        self.frame.cells[name].set(self.pop())

    def byte_EXTENDED_ARG(self, ext):
        self.extended_arg = ext + (self.extended_arg << 8)

    UNARY_OPERATORS = {
        'POSITIVE': operator.pos,
        'NEGATIVE': operator.neg,
        'NOT': operator.not_,
        'INVERT': operator.invert,
    }

    def unaryOperator(self, op):
        x = self.frame.pop()
        self.frame.push(self.UNARY_OPERATORS[op](x))

    BINARY_OPERATORS = {
        'POWER': operator.pow,
        'MULTIPLY': operator.mul,
        'FLOOR_DIVIDE': operator.floordiv,
        'TRUE_DIVIDE': operator.truediv,
        'MODULO': operator.mod,
        'ADD': operator.add,
        'SUBTRACT': operator.sub,
        'SUBSCR': operator.getitem,
        'LSHIFT': operator.lshift,
        'RSHIFT': operator.rshift,
        'AND': operator.and_,
        'XOR': operator.xor,
        'OR': operator.or_,
    }

    def binaryOperator(self, op):
        x, y = self.frame.popn(2)
        self.frame.push(self.BINARY_OPERATORS[op](x, y))

    COMPARE_OPERATORS = [
        operator.lt,
        operator.le,
        operator.eq,
        operator.ne,
        operator.gt,
        operator.ge,
    ]

    def byte_COMPARE_OP(self, opnum):
        x, y = self.frame.popn(2)
        self.frame.push(self.COMPARE_OPERATORS[opnum](x, y))

    def byte_IS_OP(self, invert):
        x, y = self.frame.popn(2)
        if invert == 1:
            self.frame.push(x is not y)
        else:
            self.frame.push(x is y)

    def byte_CONTAINS_OP(self, invert):
        x, y = self.frame.popn(2)
        if invert == 1:
            self.frame.push(x not in y)
        else:
            self.frame.push(x in y)

    def byte_LOAD_ATTR(self, attr):
        obj = self.frame.pop()
        val = getattr(obj, attr)
        self.frame.push(val)

    def byte_STORE_ATTR(self, name):
        val, obj = self.frame.popn(2)
        setattr(obj, name, val)

    def byte_DELETE_ATTR(self, name):
        obj = self.frame.pop()
        delattr(obj, name)

    def byte_STORE_SUBSCR(self, arg):
        self.check_zero_arg(arg, 'STORE_SUBSCR')
        val, obj, subscr = self.frame.popn(3)
        obj[subscr] = val

    def byte_DELETE_SUBSCR(self, arg):
        self.check_zero_arg(arg, 'DELETE_SUBSCR')
        obj, subscr = self.frame.popn(2)
        del obj[subscr]

    def byte_BUILD_TUPLE(self, count):
        elts = self.frame.popn(count)
        self.frame.push(tuple(elts))

    def byte_BUILD_LIST(self, count):
        elts = self.frame.popn(count)
        self.frame.push(elts)

    def byte_BUILD_SET(self, count):
        elts = self.frame.popn(count)
        self.frame.push(set(elts))

    def byte_BUILD_MAP(self, count):
        elts = self.frame.popn(count * 2)
        self.frame.push({elts[i]: elts[i + 1] for i in range(0, count * 2, 2)})

    def byte_BUILD_CONST_KEY_MAP(self, count):
        keys = self.frame.pop()
        elts = self.frame.popn(count)
        self.frame.push({keys[i]: elts[i] for i in range(count)})

    def byte_BUILD_STRING(self, count):
        elts = self.frame.popn(count)
        self.frame.push(''.join(elts))

    def byte_LIST_TO_TUPLE(self, arg):
        self.check_zero_arg(arg, 'LIST_TO_TUPLE')
        the_list = self.frame.pop()
        self.frame.push(tuple(the_list))

    def byte_LIST_EXTEND(self, count):
        val = self.frame.pop()
        the_list = self.frame.stack[-count]
        the_list.extend(val)

    def byte_SET_UPDATE(self, count):
        val = self.frame.pop()
        the_set = self.frame.stack[-count]
        the_set.update(val)

    def byte_DICT_UPDATE(self, count):
        val = self.frame.pop()
        the_dict = self.frame.stack[-count]
        the_dict.update(val)

    def byte_DICT_MERGE(self, count):
        val = self.frame.pop()
        the_dict = self.frame.stack[-count]
        the_dict.update(val)

    def byte_STORE_MAP(self, arg):
        self.check_zero_arg(arg, 'STORE_MAP')
        the_map, val, key = self.frame.popn(3)
        the_map[key] = val
        self.frame.push(the_map)

    def byte_UNPACK_SEQUENCE(self, count):
        seq = self.frame.pop()
        for x in reversed(seq):
            self.frame.push(x)

    def byte_BUILD_SLICE(self, count):
        if count == 2:
            x, y = self.frame.popn(2)
            self.frame.push(slice(x, y))
        elif count == 3:
            x, y, z = self.frame.popn(3)
            self.frame.push(slice(x, y, z))
        else:
            raise VirtualMachineError(f'Strange BUILD_SLICE count: {count}')

    def byte_LIST_APPEND(self, count):
        val = self.frame.pop()
        the_list = self.frame.stack[-count]
        the_list.append(val)

    def byte_SET_ADD(self, count):
        val = self.frame.pop()
        the_set = self.frame.stack[-count]
        the_set.add(val)

    def byte_MAP_ADD(self, count):
        key, val = self.frame.popn(2)
        the_map = self.frame.stack[-count]
        the_map[key] = val

    def byte_JUMP_FORWARD(self, jump):
        self.jump(jump)

    def byte_JUMP_ABSOLUTE(self, jump):
        self.jump(jump)

    def byte_POP_JUMP_IF_TRUE(self, jump):
        val = self.frame.pop()
        if val:
            self.jump(jump)

    def byte_POP_JUMP_IF_FALSE(self, jump):
        val = self.frame.pop()
        if not val:
            self.jump(jump)

    def byte_JUMP_IF_TRUE_OR_POP(self, jump):
        val = self.frame.top()
        if val:
            self.jump(jump)
        else:
            self.frame.pop()

    def byte_JUMP_IF_FALSE_OR_POP(self, jump):
        val = self.frame.top()
        if not val:
            self.jump(jump)
        else:
            self.frame.pop()

    def byte_SETUP_LOOP(self, dest):
        self.frame.push_block('loop', dest)

    def byte_GET_ITER(self, arg):
        self.check_zero_arg(arg, 'GET_ITER')
        self.frame.push(iter(self.frame.pop()))

    def byte_FOR_ITER(self, jump):
        iterobj = self.frame.top()
        try:
            v = next(iterobj)
            self.frame.push(v)
        except StopIteration:
            self.frame.pop()
            self.jump(jump)

    def byte_BREAK_LOOP(self, arg):
        self.check_zero_arg(arg, 'BREAK_LOOP')
        return 'break'

    def byte_CONTINUE_LOOP(self, dest):
        self.return_value = dest
        return 'continue'

    def byte_SETUP_EXCEPT(self, dest):
        self.frame.push_block('setup-except', dest)

    def byte_SETUP_FINALLY(self, dest):
        self.frame.push_block('finally', dest)

    def byte_POP_BLOCK(self, arg):
        self.check_zero_arg(arg, 'POP_BLOCK')
        self.frame.pop_block()

    def byte_LOAD_ASSERTION_ERROR(self, arg):
        self.check_zero_arg(arg, 'LOAD_ASSERTION_ERROR')
        self.frame.push(AssertionError())

    def byte_RAISE_VARARGS(self, argc):
        cause = exc = None
        if argc == 2:
            cause = self.frame.pop()
            exc = self.frame.pop()
        elif argc == 1:
            exc = self.frame.pop()
        return self.do_raise(exc, cause)

    def do_raise(self, exc, cause):
        if exc is None:
            exc_type, val, tb = self.last_exception
        elif type(exc) == type:
            exc_type = exc
            val = exc()
        elif isinstance(exc, BaseException):
            exc_type = type(exc)
            val = exc
        else:
            return 'exception'

        self.last_exception = exc_type, val, val.__traceback__
        return 'exception'

    def byte_POP_EXCEPT(self):
        block = self.frame.pop_block()
        if block.type != 'except-handler':
            raise VirtualMachineError('popped block is not an except handler')
        current_exc = self.frame.unwind_block(block)
        if current_exc is not None:
            self.last_exception = current_exc

    def byte_LOAD_METHOD(self, name):
        obj = self.frame.pop()
        method = getattr(obj, name)
        self.frame.push(method)

    def byte_CALL_METHOD(self, arg):
        lenPos = arg
        posargs = self.frame.popn(lenPos)

        func = self.frame.pop()
        retval = func(*posargs)
        self.frame.push(retval)

    def byte_LOAD_CLOSURE(self, name):
        self.frame.push(self.frame.cells[name])

    def byte_MAKE_FUNCTION(self, flag):
        name = self.frame.pop()
        code = self.frame.pop()

        defaults = ()
        closure = ()
        if flag & 0x08:
            closure = self.frame.pop()
        if flag & 0x01:
            defaults = self.frame.pop()

        globs = self.frame.global_names
        fn = Function(name, code, globs, defaults, closure, self)
        self.frame.push(fn)

    def byte_CALL_FUNCTION(self, arg):
        lenPos = arg
        posargs = self.frame.popn(lenPos)

        func = self.frame.pop()
        if func.__name__ == '__build_class__':
            posargs[0] = posargs[0]._func
        retval = func(*posargs)
        self.frame.push(retval)

    def byte_CALL_FUNCTION_KW(self, arg):
        kw = self.frame.pop()
        lenKw = len(kw)
        lenPos = arg - lenKw
        kwargs = self.frame.popn(lenKw)
        posargs = self.frame.popn(lenPos)
        kwargs = {kw[i]: kwargs[i] for i in range(lenKw)}

        func = self.frame.pop()
        retval = func(*posargs, **kwargs)
        self.frame.push(retval)

    def byte_CALL_FUNCTION_EX(self, flag):
        if flag == 1:
            posargs, kwargs = self.frame.popn(2)
        else:
            posargs = []
            kwargs = {}

        func = self.frame.pop()
        retval = func(*posargs, **kwargs)
        self.frame.push(retval)

    def byte_RETURN_VALUE(self, arg):
        self.check_zero_arg(arg, 'RETURN_VALUE')
        self.return_value = self.frame.pop()
        return 'return'

    def byte_YIELD_VALUE(self, arg):
        self.check_zero_arg(arg, 'YIELD_VALUE')
        self.return_value = self.frame.top()
        return 'yield'

    def byte_IMPORT_NAME(self, name):
        level, fromlist = self.frame.popn(2)
        frame = self.frame
        self.frame.push(__import__(name, frame.global_names, frame.local_names, fromlist, level))

    def byte_IMPORT_FROM(self, name):
        mod = self.frame.top()
        self.frame.push(getattr(mod, name))

    def byte_IMPORT_STAR(self, arg):
        self.check_zero_arg(arg, 'IMPORT_STAR')
        mod = self.frame.pop()
        for attr in dir(mod):
            if not attr.startswith('_'):
                self.frame.local_names[attr] = getattr(mod, attr)

    def byte_LOAD_BUILD_CLASS(self, arg):
        self.check_zero_arg(arg, 'LOAD_BUILD_CLASS')
        self.frame.push(__build_class__)

    def byte_STORE_LOCALS(self, arg):
        self.check_zero_arg(arg, 'STORE_LOCALS')
        self.frame.local_names = self.frame.pop()
