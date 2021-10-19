import unittest

from smalltalk_like import Class
from smalltalk_like import Instance
from smalltalk_like import OBJECT
from smalltalk_like import TYPE

class TestSmalltalkLike(unittest.TestCase):
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
