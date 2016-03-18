import clang.cindex

#Stats = namedtuple('Stats', 'classes_count, method_count, member_count')

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


