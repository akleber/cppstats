import clang.cindex, asciitree, sys, os

kInputsDir = os.path.join(os.path.dirname(__file__), 'INPUTS')

index = clang.cindex.Index(clang.cindex.conf.lib.clang_createIndex(False, True))
translation_unit = index.parse(os.path.join(kInputsDir, 'hello.cpp'), ['-x', 'c++'])

print(asciitree.draw_tree(translation_unit.cursor,
  lambda n: n.get_children(),
  lambda n: "%s (%s)" % (n.spelling or n.displayname, str(n.kind).split(".")[1])))

if __name__ == '__main__':
    unittest.main()
