import unittest

from map_optimization import Class
from map_optimization import Instance
from map_optimization import OBJECT
from map_optimization import TYPE

class TestMapOptimization(unittest.TestCase):
    def test_isinstance(self):
        class A(object):
            pass

        class B(A):
            pass

        b = B()
        self.assertIsInstance(b, B)
        self.assertIsInstance(b, A)
        self.assertIsInstance(b, object)
        self.assertNotIsInstance(b, type)

        A = Class(name='A', base_class=OBJECT, fields={}, metaclass=TYPE)
        B = Class(name='B', base_class=A, fields={}, metaclass=TYPE)
        b = Instance(B)
        self.assertTrue(b.isinstance(B))
        self.assertTrue(b.isinstance(A))
        self.assertTrue(b.isinstance(OBJECT))
        self.assertFalse(b.isinstance(TYPE))

    def test_read_write_field(self):
        class A(object):
            pass

        obj = A()
        obj.a = 1
        self.assertEqual(obj.a, 1)

        obj.b = 5
        self.assertEqual(obj.a, 1)
        self.assertEqual(obj.b, 5)

        obj.a = 2
        self.assertEqual(obj.a, 2)
        self.assertEqual(obj.b, 5)

        A = Class(name='A', base_class=OBJECT, fields={}, metaclass=TYPE)
        obj = Instance(A)
        obj.write_attr('a', 1)
        self.assertEqual(obj.read_attr('a'), 1)

        obj.write_attr('b', 5)
        self.assertEqual(obj.read_attr('a'), 1)
        self.assertEqual(obj.read_attr('b'), 5)

        obj.write_attr('a', 2)
        self.assertEqual(obj.read_attr('a'), 2)
        self.assertEqual(obj.read_attr('b'), 5)

    def test_read_write_field_class(self):
        class A(object):
            pass

        A.a = 1
        self.assertEqual(A.a, 1)
        A.a = 6
        self.assertEqual(A.a, 6)

        A = Class(name='A', base_class=OBJECT, fields={'a': 1}, metaclass=TYPE)
        self.assertEqual(A.read_attr('a'), 1)
        A.write_attr('a', 5)
        self.assertEqual(A.read_attr('a'), 5)

    def test_callmethod_simple(self):
        class A(object):
            def f(self):
                return self.x + 1

        obj = A()
        obj.x = 1
        self.assertEqual(obj.f(), 2)

        class B(A):
            pass

        obj = B()
        obj.x = 1
        self.assertEqual(obj.f(), 2)

        def f_A(self):
            return self.read_attr('x') + 1

        A = Class(name='A', base_class=OBJECT, fields={'f': f_A}, metaclass=TYPE)
        obj = Instance(A)
        obj.write_attr('x', 1)
        self.assertEqual(obj.callmethod('f'), 2)

        B = Class(name='B', base_class=A, fields={}, metaclass=TYPE)
        obj = Instance(B)
        obj.write_attr('x', 2)
        self.assertEqual(obj.callmethod('f'), 3)

    def test_callmethod_subclass_and_arguments(self):
        class A(object):
            def g(self, arg):
                return self.x + arg

        obj = A()
        obj.x = 1
        self.assertEqual(obj.g(4), 5)

        class B(A):
            def g(self, arg):
                return self.x + arg * 2

        obj = B()
        obj.x = 4
        self.assertEqual(obj.g(4), 12)

        def g_A(self, arg):
            return self.read_attr('x') + arg

        A = Class(name='A', base_class=OBJECT, fields={'g': g_A}, metaclass=TYPE)
        obj = Instance(A)
        obj.write_attr('x', 1)
        self.assertEqual(obj.callmethod('g', 4), 5)

        def g_B(self, arg):
            return self.read_attr('x') + arg * 2

        B = Class(name='B', base_class=A, fields={'g': g_B}, metaclass=TYPE)
        obj = Instance(B)
        obj.write_attr('x', 4)
        self.assertEqual(obj.callmethod('g', 4), 12)

    def test_bound_method(self):
        class A(object):
            def f(self, a):
                return self.x + a + 1

        obj = A()
        obj.x = 2
        m = obj.f
        self.assertEqual(m(4), 7)

        class B(A):
            pass

        obj = B()
        obj.x = 1
        m = obj.f
        self.assertEqual(m(10), 12)

        def f_A(self, a):
            return self.read_attr('x') + a + 1

        A = Class(name='A', base_class=OBJECT, fields={'f': f_A}, metaclass=TYPE)
        obj = Instance(A)
        obj.write_attr('x', 2)
        m = obj.read_attr('f')
        self.assertEqual(m(4), 7)

        B = Class(name='B', base_class=A, fields={}, metaclass=TYPE)
        obj = Instance(B)
        obj.write_attr('x', 1)
        m = obj.read_attr('f')
        self.assertEqual(m(10), 12)

    def test_getattr(self):
        class A(object):
            def __getattr__(self, name):
                if name == 'fahrenheit':
                    return self.celsius * 9.0 / 5.0 + 32
                raise AttributeError(name)

            def __setattr__(self, name, value):
                if name == 'fahrenheit':
                    self.celsius = (value - 32) * 5.0 / 9.0
                else:
                    object.__setattr__(self, name, value)

        obj = A()
        obj.celsius = 30
        self.assertEqual(obj.fahrenheit, 86)
        obj.celsius = 40
        self.assertEqual(obj.fahrenheit, 104)

        obj.fahrenheit = 86
        self.assertEqual(obj.celsius, 30)
        self.assertEqual(obj.fahrenheit, 86)

        def __getattr__(self, name):
            if name == 'fahrenheit':
                return self.read_attr('celsius') * 9.0 / 5.0 + 32
            raise AttributeError(name)

        def __setattr__(self, name, value):
            if name == 'fahrenheit':
                self.write_attr('celsius', (value - 32) * 5.0 / 9.0)
            else:
                OBJECT.read_attr('__setattr__')(self, name, value)

        A = Class(name='A', base_class=OBJECT, fields={'__getattr__': __getattr__, '__setattr__': __setattr__}, metaclass=TYPE)
        obj = Instance(A)
        obj.write_attr('celsius', 30)
        self.assertEqual(obj.read_attr('fahrenheit'), 86)
        obj.write_attr('celsius', 40)
        self.assertEqual(obj.read_attr('fahrenheit'), 104)
        obj.write_attr('fahrenheit', 86)
        self.assertEqual(obj.read_attr('celsius'), 30)
        self.assertEqual(obj.read_attr('fahrenheit'), 86)

    def test_get(self):
        class FahrenheitGetter(object):
            def __get__(self, inst, cls):
                return inst.celsius * 9.0 / 5.0 + 32

        class A(object):
            fahrenheit = FahrenheitGetter()

        obj = A()
        obj.celsius = 30
        self.assertEqual(obj.fahrenheit, 86)

        class FahrenheitGetter(object):
            def __get__(self, inst, cls):
                return inst.read_attr('celsius') * 9.0 / 5.0 + 32

        A = Class(name='A', base_class=OBJECT, fields={'fahrenheit': FahrenheitGetter()}, metaclass=TYPE)
        obj = Instance(A)
        obj.write_attr('celsius', 30)
        self.assertEqual(obj.read_attr('fahrenheit'), 86)

    def test_map(self):
        Point = Class(name='Point', base_class=OBJECT, fields={}, metaclass=TYPE)
        p1 = Instance(Point)
        p1.write_attr('x', 1)
        p1.write_attr('y', 2)
        self.assertEqual(p1.storage, [1, 2])
        self.assertEqual(p1.map.attrs, {'x': 0, 'y': 1})

        p2 = Instance(Point)
        p2.write_attr('x', 5)
        p2.write_attr('y', 6)
        self.assertIs(p1.map, p2.map)
        self.assertEqual(p2.storage, [5, 6])

        p1.write_attr('x', -1)
        p1.write_attr('y', -2)
        self.assertIs(p1.map, p2.map)
        self.assertEqual(p1.storage, [-1, -2])

        p3 = Instance(Point)
        p3.write_attr('x', 100)
        p3.write_attr('z', -343)
        self.assertIsNot(p3.map, p1.map)
        self.assertEqual(p3.map.attrs, {'x': 0, 'z': 1})
