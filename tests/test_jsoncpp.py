import os, sys
sys.path.insert(0, os.path.abspath(os.path.join('..', 'cppstats')))
import generate_stats

from clang.cindex import *

json_reader_file = os.path.join(os.path.dirname(__file__), 'jsoncpp', 'include', 'json', 'reader.h')

def test_json_reader():
    index = Index.create()
    assert isinstance(index, Index)
    tu = index.parse(json_reader_file, ["-I/Users/andreaslangs/Shares/NAS/Dev/python/cppstats/tests/jsoncpp/include", "-I/Users/andreaslangs/Shares/NAS/Dev/python/cppstats/tests/jsoncpp/src/lib_json/../../include", "-std=c++11", "-DNDEBUG", "-isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk"])
    assert isinstance(tu, TranslationUnit)

    generate_stats.process_tu(tu)
