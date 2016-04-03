import clang.cindex
import json
import os
import re
import logging
import multiprocessing
from collections import namedtuple
from functools import partial

#logging.basicConfig(filename='example.log',level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)


class cppclass(namedtuple('cppclass', 'name, usr, public_method_count, protected_method_count, private_method_count')):
    #def __repr__(self):
    #    return "%s" % (self.usr, )

    # for set
    def __eq__(self, other):
        return self.usr == other.usr

    def __hash__(self):
        return hash(self.usr)


def print_statistics(classes):
    logging.info("Summary ----------")

    public_method_count = 0
    protected_method_count = 0
    private_method_count = 0

    for c in classes:
        logging.info('class:: %s', c.name)
        public_method_count += c.public_method_count
        protected_method_count += c.protected_method_count
        private_method_count += c.private_method_count

    logging.info("Summary: %d classes, %d public methods, %d protected methods, %d private methods", len(classes),
        public_method_count, protected_method_count, private_method_count)


def traverse_class(cursor):
    '''TODO: implement subclasses. Thats why we return a set of classes in this function
    '''
    logging.debug('traversing class: %s', cursor.spelling)
    classes = set()

    public_method_count = 0
    protected_method_count = 0
    private_method_count = 0

    for c in cursor.get_children():
        if c.kind == clang.cindex.CursorKind.CXX_METHOD:
            if c.access_specifier == clang.cindex.AccessSpecifier.PUBLIC:
                public_method_count +=1
            elif c.access_specifier == clang.cindex.AccessSpecifier.PROTECTED:
                protected_method_count +=1
            elif (c.access_specifier == clang.cindex.AccessSpecifier.PRIVATE):
                private_method_count +=1
        else:
            logging.debug('ignoring: %s', c.kind)

    current_class = cppclass(cursor.spelling, cursor.get_usr(), public_method_count, protected_method_count, private_method_count)
    classes.add(current_class)

    return classes


def traverse(cursor, search_path):
    classes = set()

    for c in cursor.get_children():
        if os.path.abspath(c.location.file.name).startswith(search_path):
            if c.kind == clang.cindex.CursorKind.CLASS_DECL:
                if c.is_definition:
                    classes.update(traverse_class(c))
                else:
                    logging.debug('ignoring not defined CLASS_DECL: %s', c.name)

            elif c.kind == clang.cindex.CursorKind.NAMESPACE:
                logging.debug('traversing NAMESPACE: %s', c.spelling)
                classes.update(traverse(c, search_path))
            else:
                logging.debug('ignoring top level node kind: %s', c.kind)
                pass

        else:
            #logging.debug('ignoring file: %s', c.location.file.name)
            pass 

    return classes


def process_source_file(file, args, search_path):
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
    translation_unit = index.parse(file, args_list)
    cursor = translation_unit.cursor
    classes = traverse(cursor, search_path)

    return classes


def mp_worker(compile_commands_entry, search_path):
    classes = process_source_file(compile_commands_entry["file"], compile_commands_entry["command"], search_path)
    return classes


def process_compile_commands_db(file, search_path):
    ''' The compile_commands.json is a list [] of dictionaries {}.
    '''
    logging.debug('process_compile_commands_db: %s', file)

    with open(file) as db_file:    
        data = json.load(db_file)

    unique_classes = set()

    enable_multiple_processes = True

    if enable_multiple_processes:
        logging.info('cpu_count() = %d', multiprocessing.cpu_count())
        with multiprocessing.Pool() as p:
            classes_sets = p.map(partial(mp_worker, search_path=search_path), data)

    else:
        for entry in data:
            classes = process_source_file(entry["file"], entry["command"])
            unique_classes.update(classes)

    for classes_set in classes_sets:
        unique_classes.update(classes_set)

    print_statistics(unique_classes)


if __name__ == '__main__':
    search_path = os.path.abspath(os.path.join(os.sep, 'Users', 'andreaslangs', 'Shares', 'NAS', 'Dev', 'python', 'cppstats', 'tests', 'jsoncpp'))
    logging.debug('search_path: %s', search_path)

    db_file = os.path.join(os.path.dirname(__file__), '..', 'tests', 'jsoncpp', 'build', 'compile_commands.json')
    process_compile_commands_db(db_file, search_path)

    #source_file = os.path.join(os.path.dirname(__file__), '..', 'tests', 'jsoncpp', 'include', 'json', 'writer.h')
    #source_file = os.path.join(os.path.dirname(__file__), '..', 'tests', 'jsoncpp', 'src', 'lib_json', 'json_reader.cpp')
    #classes = process_source_file(source_file, "-I/Users/andreaslangs/Shares/NAS/Dev/python/cppstats/tests/jsoncpp/include -I/Users/andreaslangs/Shares/NAS/Dev/python/cppstats/tests/jsoncpp/src/lib_json/../../include   -std=c++11 -Wall -Wconversion -Wshadow -Werror=conversion -Werror=sign-compare -O3 -DNDEBUG -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk", search_path)
    #print_statistics(classes)
