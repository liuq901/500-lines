from . import vmtest

class TestExceptions(vmtest.VmTestCase):
    def test_catching_exceptions(self):
        self.assert_ok('''
            try:
                [][1]
                print('Shouldn\\'t be here...')
            except IndexError:
                print('caught it!')
            try:
                [][1]
                print('Shouldn\\'t be here...')
            except Exception:
                print('caught it!')
            try:
                [][1]
                print('Shouldn\\'t be here...')
            except:
                print('caught it!')
        ''')

    def test_raise_exception(self):
        self.assert_ok('''
            raise Exception('ooops')
        ''', raises=Exception)

    def test_raise_exception_class(self):
        self.assert_ok('''
            raise ValueError
        ''', raises=ValueError)

    def test_raise_exception_from(self):
        self.assert_ok('''
            raise ValueError from NameError
        ''', raises=ValueError)

    def test_raise_and_catch_exception(self):
        self.assert_ok('''
            try:
                raise ValueError('foo')
            except ValueError as e:
                print('Caught: %s' % e)
            print('All done')
        ''')

    def test_raise_and_catch_exception_in_function(self):
        self.assert_ok('''
            def fn():
                raise ValueError('oops')

            try:
                fn()
            except ValueError as e:
                print('Caught: %s' % e)
            print('done')
        ''')

    def test_global_name_error(self):
        self.assert_ok('''
            try:
                fooey
                print('Yes fooey?')
            except NameError:
                print('No fooey')
            fooey
        ''', raises=NameError)

    def test_local_name_error(self):
        self.assert_ok('''
            def fn():
                fooey

            fn()
        ''', raises=NameError)

    def test_catch_local_name_error(self):
        self.assert_ok('''
            def fn():
                try:
                    fooey
                    print('Yes fooey?')
                except NameError:
                    print('No fooey')

            fn()
        ''')

    def test_reraise(self):
        self.assert_ok('''
            def fn():
                try:
                    fooey
                    print('Yes fooey?')
                except NameError:
                    print('No fooey')
                    raise

            fn()
        ''', raises=NameError)

    def test_reraise_explicit_exception(self):
        self.assert_ok('''
            def fn():
                try:
                    raise ValueError('ouch')
                except ValueError as e:
                    print('Caught %s' % e)
                    raise

            fn()
        ''', raises=ValueError)

    def test_finally_while_throwing(self):
        self.assert_ok('''
            def fn():
                try:
                    print('About to..')
                    raise ValueError('ouch')
                finally:
                    print('Finally')

            fn()
            print('Done')
        ''', raises=ValueError)

    def test_finally_order(self):
        self.assert_ok('''
            l = []
            for i in range(3):
                try:
                    l.append(i)
                finally:
                    l.append('f')
                l.append('e')
            l.append('r')
            print(l)
            assert l == [0, 'f', 'e', 1, 'f', 'e', 2, 'f', 'e', 'r']
        ''')
