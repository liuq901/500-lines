import pickle
import random
import unittest

from dbdb.binary_tree import BinaryNode, BinaryTree, BinaryNodeRef, ValueRef

class StubStorage(object):
    def __init__(self):
        self.d = [0]
        self.locked = False

    def lock(self):
        if not self.locked:
            self.locked = True
            return True
        else:
            return False

    def unlock(self):
        if self.locked:
            self.locked = False

    def get_root_address(self):
        return 0

    def write(self, string):
        address = len(self.d)
        self.d.append(string)
        return address

    def read(self, address):
        return self.d[address]

class TestBinaryTree(unittest.TestCase):
    def setUp(self):
        self.tree = BinaryTree(StubStorage())

    def test_get_missing_key_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.tree.get('Not A Key In The Tree')

    def test_set_and_get_key(self):
        self.tree.set('a', 'b')
        self.assertEqual(self.tree.get('a'), 'b')

    def test_random_set_and_get_keys(self):
        ten_k = list(range(10000))
        pairs = list(zip(random.sample(ten_k, 10), random.sample(ten_k, 10)))
        for i, (k, v) in enumerate(pairs, start=1):
            self.tree.set(k, v)
            self.assertEqual(len(self.tree), i)
        for k, v in pairs:
            self.assertEqual(self.tree.get(k), v)
        random.shuffle(pairs)
        for i, (k, v) in enumerate(pairs, start=1):
            self.tree.pop(k)
            self.assertEqual(len(self.tree), len(pairs) - i)

    def test_overwrite_and_get_key(self):
        self.tree.set('a', 'b')
        self.tree.set('a', 'c')
        self.assertEqual(self.tree.get('a'), 'c')

    def test_pop_non_existent_key(self):
        with self.assertRaises(KeyError):
            self.tree.pop('Not A Key In The Tree')

    def test_del_leaf_key(self):
        self.tree.set('b', '2')
        self.tree.pop('b')
        with self.assertRaises(KeyError):
            self.tree.get('b')

    def test_del_left_node_key(self):
        self.tree.set('b', '2')
        self.tree.set('a', '1')
        self.tree.pop('b')
        with self.assertRaises(KeyError):
            self.tree.get('b')
        self.tree.get('a')

    def test_del_right_node_key(self):
        self.tree.set('b', '2')
        self.tree.set('c', '3')
        self.tree.pop('b')
        with self.assertRaises(KeyError):
            self.tree.get('b')
        self.tree.get('c')

    def test_del_full_node_key(self):
        self.tree.set('b', '2')
        self.tree.set('a', '1')
        self.tree.set('c', '3')
        self.tree.pop('b')
        with self.assertRaises(KeyError):
            self.tree.get('b')
        self.tree.get('a')
        self.tree.get('c')

class TestBinaryNodeRef(unittest.TestCase):
    def test_to_string_leaf(self):
        n = BinaryNode(BinaryNodeRef(), 'k', ValueRef(address=999), BinaryNodeRef(), 1)
        pickled = BinaryNodeRef.referent_to_string(n)
        d = pickle.loads(pickled)
        self.assertEqual(d['left'], 0)
        self.assertEqual(d['key'], 'k')
        self.assertEqual(d['value'], 999)
        self.assertEqual(d['right'], 0)

    def test_to_string_nonleaf(self):
        left_ref = BinaryNodeRef(address=123)
        right_ref = BinaryNodeRef(address=321)
        n = BinaryNode(left_ref, 'k', ValueRef(address=999), right_ref, 3)
        pickled = BinaryNodeRef.referent_to_string(n)
        d = pickle.loads(pickled)
        self.assertEqual(d['left'], 123)
        self.assertEqual(d['key'], 'k')
        self.assertEqual(d['value'], 999)
        self.assertEqual(d['right'], 321)
