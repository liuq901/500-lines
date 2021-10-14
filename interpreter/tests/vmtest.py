import dis
import io
import sys
import textwrap
import types
import unittest

from byterun.byterun import VirtualMachine
from byterun.byterun import VirtualMachineError

def dis_code(code):
    print("")
    print(code)
    dis.dis(code)

class VmTestCase(unittest.TestCase):
    def tearDown(self):
        result = self.defaultTestResult()
        self._feedErrorsToResult(result, self._outcome.errors)
        error = self.list2reason(result.errors)
        failure = self.list2reason(result.failures)
        ok = not error and not failure

        if not ok:
            dis_code(self.code)
            print('-- stdout ----------')
            print(self.output.getvalue())
            print('-- log -------------')
            print(self.log.getvalue())

    def list2reason(self, exc_list):
        if exc_list and exc_list[-1][0] is self:
            return exc_list[-1][1]

    def assert_ok(self, code, raises=None):
        code = textwrap.dedent(code)
        code = compile(code, f'<{self.id()}>', 'exec', 0, 1)

        self.code = code

        real_stdout = sys.stdout

        vm_stdout = io.StringIO()
        sys.stdout = vm_stdout
        vm = VirtualMachine()

        vm_value = vm_exc = None
        try:
            vm_value = vm.run_code(code)
        except VirtualMachineError:
            raise
        except AssertionError:
            raise
        except Exception as e:
            vm_exc = e
        finally:
            self.output = vm_stdout
            self.log = vm.log
            sys.stdout = real_stdout

        py_stdout = io.StringIO()
        sys.stdout = py_stdout

        py_value = py_exc = None
        globs = {}
        try:
            py_value = eval(code, globs, globs)
        except AssertionError:
            raise
        except Exception as e:
            py_exc = e
        finally:
            sys.stdout = real_stdout

        self.assert_same_exception(vm_exc, py_exc)
        self.assertEqual(vm_stdout.getvalue(), py_stdout.getvalue())
        self.assertEqual(vm_value, py_value)
        if raises:
            self.assertIsInstance(vm_exc, raises)
        else:
            self.assertIsNone(vm_exc)

    def assert_same_exception(self, e1, e2):
        self.assertEqual(str(e1), str(e2))
        self.assertIs(type(e1), type(e2))

