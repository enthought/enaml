""" A registry of view element classes.

"""
class ElementRegistry(object):
    
    @classmethod
    def instance(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._elements = {}
    
    def register(self, cls):
        name = cls.__name__
        if name in self._elements:
            raise ValueError('`%s` element already registered.' % name)
        self._elements[name] = cls

    def lookup(self, name):
        if name not in self._elements:
            raise ValueError('`%s` is not a registered element.' % name)
        return self._elements[name]


def register_element(cls):
    """ A class decorator to register a new element. """
    ElementRegistry.instance().register(cls)
    return cls


def lookup_element(name):
    """ Lookup the element class for the given name. """
    return ElementRegistry.instance().lookup(name)

