from collections import defaultdict
import re


ID_RE = re.compile(r'#([a-zA-Z_][a-zA-Z0-9_]*)$')

CLASS_RE = re.compile(r'\*?\.([a-zA-Z_][a-zA-Z0-9_]*)$')

TYPE_RE = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)$')

TYPE_CLASS_RE = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*)$')

ANY_RE = re.compile(r'\*')


class NO_STYLE(object):
    __slots__ = ()
    def __repr__(self):
        return 'NO_STYLE'
    def __str__(self):
        return repr(self)
NO_STYLE = NO_STYLE()


class StyleSheet(object):

    def __init__(self,  sheet_descr):
        parsed = self.parse_descr(sheet_descr)
        ids, classes, types, types_classes, defaults = parsed
        self.ids = ids
        self.classes = classes
        self.types = types
        self.types_classes = types_classes
        self.defaults = defaults

    def parse_descr(self, descr):
        ids = defaultdict(dict)
        classes = defaultdict(dict)
        types = defaultdict(dict)
        types_classes = defaultdict(dict)
        defaults = {}

        for key, style in descr.iteritems():
            match = ID_RE.match(key)
            if match:
                ids[match.group(1)].update(style)
                continue
            match = CLASS_RE.match(key)
            if match:
                classes[match.group(1)].update(style)
                continue
            match = TYPE_RE.match(key)
            if match:
                types[match.group(1)].update(style)
                continue
            match = TYPE_CLASS_RE.match(key)
            if match:
                types_classes[match.group(1)].update(style)
                continue
            match = ANY_RE.match(key)
            if match:
                defaults.update(style)
                continue
            raise ValueError('Invalid style string: `%s`' % key)
        
        return ids, classes, types, types_classes, defaults


    def get_style(self, tag, type=None, cls=None, id=None):
        ids = self.ids
        classes = self.classes
        types = self.types
        types_classes = self.types_classes
        defaults = self.defaults

        if id in ids:
            style = ids[id]
            if tag in style:
                return style[tag]
        
        if cls:
            for scls in cls.split():
                if type:
                    key = '%s.%s' % (type, scls)
                    if key in types_classes:
                        style = types_classes[key]
                        if tag in style:
                            return style[tag]

                if scls in classes:
                    style = classes[scls]
                    if tag in style:
                        return style[tag]

        if type in types:
            style = types[type]
            if tag in style:
                return style[tag]
        
        if tag in defaults:
            return defaults[tag]
        
        return NO_STYLE

