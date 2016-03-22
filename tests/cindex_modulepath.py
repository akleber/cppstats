import sys
print(sys.path)
print(sys.version)

import os
print(os.environ['PATH'])

import clang.cindex
print (clang.cindex.__file__)
