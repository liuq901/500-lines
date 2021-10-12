import importlib
import sys

from byterun import VirtualMachine

def run_python_file(filename):
    old_main_mod = sys.modules['__main__']
    main_mod_spec = importlib.util.spec_from_loader('__main__', loader=None)
    main_mod = importlib.util.module_from_spec(main_mod_spec)
    sys.modules['__main__'] = main_mod
    main_mod.__builtins__ = sys.modules['builtins']

    with open(filename, 'r') as f:
        source = f.read()

    if not source or source[-1] != '\n':
        source += '\n'
    code = compile(source, filename, 'exec')

    vm = VirtualMachine()
    vm.run_code(code, global_names=main_mod.__dict__)

if __name__ == '__main__':
    run_python_file(sys.argv[1])
