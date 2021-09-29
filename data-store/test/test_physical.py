import os
import tempfile
import unittest

from dbdb.physical import Storage

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.f = tempfile.NamedTemporaryFile()
        self.p = Storage(self.f)

    def tearDown(self):
        self.p.close()

    def _get_superblock_and_data(self, value):
        superblock = value[:Storage.SUPERBLOCK_SIZE]
        data = value[Storage.SUPERBLOCK_SIZE:]
        return superblock, data

    def _get_f_contents(self):
        self.f.flush()
        origin = self.f.tell()
        self.f.seek(0)
        res = self.f.read()
        self.f.seek(origin)
        return res

    def test_init_ensures_superblock(self):
        EMPTY_SUPERBLOCK = b'\x00' * Storage.SUPERBLOCK_SIZE
        self.f.seek(0, os.SEEK_END)
        value = self._get_f_contents()
        self.assertEqual(value, EMPTY_SUPERBLOCK)

    def test_write(self):
        self.p.write(b'ABCDE')
        value = self._get_f_contents()
        superblock, data = self._get_superblock_and_data(value)
        self.assertEqual(data, b'\x00' * 7 + b'\x05ABCDE')

    def test_read(self):
        self.f.seek(Storage.SUPERBLOCK_SIZE)
        self.f.write(b'\x00' * 7 + b'\x0801234567')
        value = self.p.read(Storage.SUPERBLOCK_SIZE)
        self.assertEqual(value, b'01234567')

    def test_commit_root_address(self):
        self.p.commit_root_address(257)
        root_bytes = self._get_f_contents()[:8]
        self.assertEqual(root_bytes, b'\x00' * 6 + b'\x01\x01')

    def test_get_root_address(self):
        self.f.seek(0)
        self.f.write(b'\x00' * 6 + b'\x02\x02')
        root_address = self.p.get_root_address()
        self.assertEqual(root_address, 514)

    def test_workflow(self):
        a1 = self.p.write(b'one')
        a2 = self.p.write(b'two')
        self.p.commit_root_address(a2)
        a3 = self.p.write(b'three')
        self.assertEqual(self.p.get_root_address(), a2)
        a4 = self.p.write(b'four')
        self.p.commit_root_address(a4)
        self.assertEqual(self.p.read(a1), b'one')
        self.assertEqual(self.p.read(a2), b'two')
        self.assertEqual(self.p.read(a3), b'three')
        self.assertEqual(self.p.read(a4), b'four')
        self.assertEqual(self.p.get_root_address(), a4)
