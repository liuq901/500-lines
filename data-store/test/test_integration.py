import os
import shutil
import subprocess
import tempfile
import unittest

import dbdb
import dbdb.tool

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.new_tempfile_name = os.path.join(self.temp_dir, 'new.db')
        self.tempfile_name = os.path.join(self.temp_dir, 'existing.db')
        open(self.tempfile_name, 'w').close()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_new_database_file(self):
        db = dbdb.connect(self.new_tempfile_name)
        db['a'] = 'eye'
        db.commit()
        db.close()

    def test_persistence(self):
        db = dbdb.connect(self.tempfile_name)
        db['b'] = 'bee'
        db['a'] = 'aye'
        db['c'] = 'see'
        db.commit()
        db['d'] = 'dee'
        self.assertEqual(len(db), 4)
        db.close()
        db = dbdb.connect(self.tempfile_name)
        self.assertEqual(db['a'], 'aye')
        self.assertEqual(db['b'], 'bee')
        self.assertEqual(db['c'], 'see')
        with self.assertRaises(KeyError):
            db['d']
        self.assertEqual(len(db), 3)
        db.close()

class TestTool(unittest.TestCase):
    def setUp(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp_f:
            self.tempfile_name = temp_f.name

    def tearDown(self):
        os.remove(self.tempfile_name)

    def _tool(self, *args):
        return subprocess.check_output(
            ['python', '-m', 'dbdb.tool', self.tempfile_name] + list(args),
            stderr=subprocess.STDOUT,
        )

    def test_get_non_existent(self):
        self._tool('set', 'a', b'b')
        self._tool('delete', 'a')
        with self.assertRaises(subprocess.CalledProcessError) as raised:
            self._tool('get', 'a')
        self.assertEqual(raised.exception.returncode, dbdb.tool.BAD_KEY)

    def test_tool(self):
        expected = b'b'
        self._tool('set', 'a', expected)
        actual = self._tool('get', 'a')
        self.assertEqual(actual, expected)
