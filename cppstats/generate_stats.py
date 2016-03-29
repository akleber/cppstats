import clang.cindex
import json
import os
import re
import logging
import multiprocessing

#Stats = namedtuple('Stats', 'classes_count, method_count, member_count')

#logging.basicConfig(filename='example.log',level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

def print_statistics(classes):
    class_count = len(classes)
    public_pethod_count = 0
    private_method_count = 0

    for c in classes:
        for m in c.methods:
            if (m.access == clang.cindex.AccessSpecifier.PUBLIC):
                public_pethod_count += 1
            elif (m.access == clang.cindex.AccessSpecifier.PRIVATE):
                private_method_count += 1

    logging.info('classes        : %i', class_count)
    logging.info('public_methods : %i', public_pethod_count)
    logging.info('private_methods: %i', private_method_count)


def get_annotations(node):
    return [c.displayname for c in node.get_children()
            if c.kind == clang.cindex.CursorKind.ANNOTATE_ATTR]

class Method(object):
    def __init__(self, cursor):
        self.name = cursor.spelling
        self.annotations = get_annotations(cursor)
        self.access = cursor.access_specifier

class Class(object):
    def __init__(self, cursor):
        self.name = cursor.spelling
        self.usr = cursor.get_usr()

        self.methods = []
        #self.annotations = get_annotations(cursor)

        logging.debug('created Class for: %s', cursor.spelling)

        for c in cursor.get_children():
            if (c.kind == clang.cindex.CursorKind.CXX_METHOD): 
                m = Method(c)
                self.methods.append(m)

        #dummy_classes = set()
        #dummy_classes.add(self)
        #print_statistics(dummy_classes)

    def __repr__(self):
        return "%s" % (self.usr, )

    # for set
    def __eq__(self, other):
        return self.usr == other.usr

    def __hash__(self):
        return hash(self.usr)

def collect_classes(cursor, filename):
    classes = set()

    (drive, tail) = os.path.splitdrive(filename)
    if not drive:
        drive = os.sep
    search_path = os.path.abspath(os.path.join(drive, 'Users', 'andreaslangs', 'Shares', 'NAS', 'Dev', 'python', 'cppstats', 'tests', 'jsoncpp'))
    logging.debug('search_path: %s', search_path)

    for c in cursor.get_children():
        if (os.path.abspath(c.location.file.name).startswith(search_path)):
            if (c.kind == clang.cindex.CursorKind.CLASS_DECL
                and c.is_definition()):
                a_class = Class(c)
                classes.add(a_class)
            elif c.kind == clang.cindex.CursorKind.NAMESPACE:
                child_classes = collect_classes(c, filename)
                classes.update(child_classes)

    return classes 

def process_tu(translation_unit):
    tu_filename = os.path.abspath(translation_unit.spelling)
    logging.debug('process_tu: %s', tu_filename)

    cursor = translation_unit.cursor
    classes = collect_classes(cursor, tu_filename)

    #sum_public_methods = sum([len(x.public_methods) for x in classes])
    #sum_private_methods = sum([len(x.private_methods) for x in classes])
    #sum_annotations = sum([len(x.annotations) for x in classes])
    #print("classes: %i, public methods: %i, private methods: %i, annotations count: %i" % (len(classes),sum_public_methods,sum_private_methods,sum_annotations))
    
    #print(*classes, sep='\n')
    return classes


def process_source_file(file, args):
    logging.debug('process_source_file: %s', file)

    # remove outfile
    outfile_regex = re.compile(r"-o \S*", re.IGNORECASE)
    args = outfile_regex.sub('', args)

    #remove sourcefile
    sourcefile_regex = re.compile(r"-c \S*", re.IGNORECASE)
    args = sourcefile_regex.sub('', args)

    args_list = args.split(' ')

    #remove empty entries
    args_list = [x for x in args_list if x]

    index = clang.cindex.Index.create()
    tu = index.parse(file, args_list)

    classes = process_tu(tu)

    print_statistics(classes)

def mp_worker(compile_commands_entry):
    process_source_file(compile_commands_entry["file"], compile_commands_entry["command"])


def process_compile_commands_db(file, disables_multiple_processes=False):
    ''' The compile_commands.json is a list [] of dictionaries {}.
    '''
    logging.debug('process_compile_commands_db: %s', file)

    with open(file) as db_file:    
        data = json.load(db_file)

    if disables_multiple_processes:
        for entry in data:
            process_source_file(entry["file"], entry["command"])
    else:
        logging.info('cpu_count() = %d', multiprocessing.cpu_count())
        p = multiprocessing.Pool()
        p.map(mp_worker, data)


if __name__ == '__main__':
    db_file = os.path.join(os.path.dirname(__file__), '..', 'tests', 'jsoncpp', 'build', 'compile_commands.json')
    process_compile_commands_db(db_file)

    #source_file = os.path.join(os.path.dirname(__file__), '..', 'tests', 'jsoncpp', 'include', 'json', 'writer.h')
    #source_file = os.path.join(os.path.dirname(__file__), '..', 'tests', 'jsoncpp', 'src', 'lib_json', 'json_reader.cpp')
    #process_source_file(source_file, "-I/Users/andreaslangs/Shares/NAS/Dev/python/cppstats/tests/jsoncpp/include -I/Users/andreaslangs/Shares/NAS/Dev/python/cppstats/tests/jsoncpp/src/lib_json/../../include   -std=c++11 -Wall -Wconversion -Wshadow -Werror=conversion -Werror=sign-compare -O3 -DNDEBUG -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk")

