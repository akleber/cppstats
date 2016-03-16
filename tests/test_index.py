import clang.cindex
import os
import unittest

kInputsDir = os.path.join(os.path.dirname(__file__), 'INPUTS')

class TestCIndex(unittest.TestCase):

    def test_create(self):
        index = clang.cindex.Index.create()

    def test_parse(self):
        index = clang.cindex.Index.create()
        self.assertTrue(isinstance(index, clang.cindex.Index))
        tu = index.parse(os.path.join(kInputsDir, 'hello.cpp'))
        self.assertTrue(isinstance(tu, clang.cindex.TranslationUnit))

if __name__ == '__main__':
    unittest.main()
