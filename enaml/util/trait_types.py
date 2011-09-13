from traits.api import TraitType, Interface


class SubClass(TraitType):

    def __init__(self, cls):
        super(SubClass, self).__init__()
        if issubclass(cls, Interface):
            self.info = (cls, True)
        else:
            self.info = (cls, False)

    def validate(self, obj, name, value):
        cls, interface = self.info
        if interface:
            if issubclass(value.__implements__, cls):
                return value
        else:
            if issubclass(value, cls):
                return value
        if interface:
            msg = 'Class must be and implementor of %s.' % cls
            raise TypeError(msg)
        else:
            msg = 'Class must be a subclass of %s.' % cls
            raise TypeError(msg)


class ReadOnlyConstruct(TraitType):

    def __init__(self, factory):
        super(ReadOnlyConstruct, self).__init__()
        self._factory = factory

    def get(self, obj, name):
        dct = obj.__dict__
        if name in dct:
            res = dct[name]
        else:
            res = dct[name] = self._factory(obj, name)
        return res


class NamedLookup(TraitType):

    def __init__(self, lookup_func_name):
        super(NamedLookup, self).__init__()
        self._lookup_func_name = lookup_func_name
    
    def get(self, obj, name):
        return getattr(obj, self._lookup_func_name)(name)


class ORStr(TraitType):
    """ Allows a space-separated string of any combination of the 
    constituents of the string passed to the constructor.
    
    i.e. StrFlags("foo bar") will validate only the following strings:
        
        "", "foo", "foo bar", "bar", "bar foo"

    """
    default_value = ""

    def __init__(self, allowed):
        self.allowed = set(allowed.strip().split())

    def is_valid(self, val):
        if not isinstance(val, basestring):
            return False
        components = val.strip.split()
        allowed = self.allowed
        return all(component in allowed for component in components)

