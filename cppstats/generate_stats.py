import clang.cindex
import json
import os
import re
import logging

#Stats = namedtuple('Stats', 'classes_count, method_count, member_count')

#logging.basicConfig(filename='example.log',level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

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
        self.public_methods = []
        self.private_methods = []
        self.annotations = get_annotations(cursor)

        if cursor.spelling == "Reader":
            print ("spelling: %s" % (cursor.spelling,))
            print ("get_usr: %s" % (cursor.get_usr(),))
            print ("displayname: %s" % (cursor.displayname,))
            print ("mangled_name: %s" % (cursor.mangled_name,))
            print ("location: %s" % (cursor.location,))
            #print ("extend %s" % (cursor.extent,))


        for c in cursor.get_children():
            if (c.kind == clang.cindex.CursorKind.CXX_METHOD): 
                m = Method(c)
                if (c.access_specifier == clang.cindex.AccessSpecifier.PUBLIC):
                    self.public_methods.append(m)
                elif (c.access_specifier == clang.cindex.AccessSpecifier.PRIVATE):
                    self.private_methods.append(m)

    def __repr__(self):
        return "%s" % (self.name, )

def get_classes(cursor):
    result = []
    for c in cursor.get_children():
        if (c.kind == clang.cindex.CursorKind.CLASS_DECL):
            a_class = Class(c)
            result.append(a_class)
        elif c.kind == clang.cindex.CursorKind.NAMESPACE:
            child_classes = get_classes(c)
            result.extend(child_classes)

    return result 

def process_tu(translation_unit):
    cursor = translation_unit.cursor
    classes = get_classes(cursor)
    #print(classes)

    sum_public_methods = sum([len(x.public_methods) for x in classes])
    sum_private_methods = sum([len(x.private_methods) for x in classes])
    sum_annotations = sum([len(x.annotations) for x in classes])

    print("classes: %i, public methods: %i, private methods: %i, annotations count: %i" % (len(classes),sum_public_methods,sum_private_methods,sum_annotations))

    print(*classes, sep='\n')


def process_source_file(file, args):
    logging.debug('process_source_file: %s' % (file,))

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

    process_tu(tu)


def process_compile_commands_db(file):
    with open(file) as db_file:    
        data = json.load(db_file)

    #for entry in data:
    #    process_source_file(entry["file"], entry["command"])

    process_source_file(data[0]["file"], data[0]["command"])

if __name__ == '__main__':
    db_file = os.path.join(os.path.dirname(__file__), '..', 'tests', 'jsoncpp', 'build', 'compile_commands.json')
    process_compile_commands_db(db_file)


