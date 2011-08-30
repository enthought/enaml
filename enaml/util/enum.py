import itertools


# A sentinel to differentiate from None
NO_VALUE = object()


class ConstantMeta(type):
    """ The metaclass for Constant which tracks the creation of 
    instances and numbers them so that ordering can be determined 
    at a later time if needed.

    """
    # A counter to count the creations.
    _counter = itertools.count()

    def __call__(meta, *args, **kwargs):
        instance = super(ConstantMeta, meta).__call__(*args, **kwargs)
        instance._n = meta._counter.next()
        return instance


class Constant(object):
    """ A constant object descriptor that can either hold a value
    or provide a unique value that will not compare equal with 
    anything else.

    """
    __metaclass__ = ConstantMeta
    
    # _cls_name and _name are set by EnumMeta and
    # _n is set by ConstantMeta.
    __slots__ = ('_cls_name', '_name', '_n', '_value')
    
    def __init__(self, value=NO_VALUE):
        self._value = value
    
    def __get__(self, obj, cls, no_value=NO_VALUE):
        if obj is not None:
            msg = 'Cannot access constant values through a %s instance'
            raise ValueError(msg % self._cls_name)
        
        # If the user has not provided a value, use ourselves
        # as the value since this instance is unique.
        val = self._value
        if val is no_value:
            val = self

        return val

    def __set__(self, obj, val):
        msg = 'Cannot access constant values through a %s instance'
        raise ValueError(msg % self._cls_name)

    def __delete__(self, obj):
        msg = 'Cannot access constant values through a %s instance'
        raise ValueError(msg % self._cls_name)

    def __repr__(self):
        return '%s.%s' % (self._cls_name, self._name)

    def __str__(self):
        return repr(self)


class EnumMeta(type):
    """ The metaclass for Enum which supplies the class name and 
    attribute name to Constant instances and places them in a dict 
    at __values__. A tuple of names for the constants are placed at 
    __names__ in sorted order. The constants themselves are placed
    in a set at __values_set__.

    """
    def __new__(meta, cls_name, bases, cls_dict):
        values = []
        for key, value in cls_dict.iteritems():
            if isinstance(value, Constant):
                value._cls_name = cls_name
                value._name = key
                values.append(value)
        values.sort(key=lambda val: val._n)
        cls_dict['__values__'] = dict((val._name, val) for val in values)
        cls_dict['__names__'] = tuple(val._name for val in values)
        cls_dict['__values_set__'] = set(values)
        return type.__new__(meta, cls_name, bases, cls_dict)

    def __call__(cls, *args, **kwargs):
        raise RuntimeError('Cannot instantiate an Enum.')
    
    def __setattr__(cls, name, val):
        if name in cls.__values__:
            raise AttributeError('Cannot set a Constant value on an Enum.')

    def __instancecheck__(cls, instance):
        return instance in cls.__values_set__


class Enum(object):
    
    __metaclass__ = EnumMeta

    @classmethod
    def values(cls):
        """ Yields the constants defined on the class in sorted order.

        """
        for name in cls.__names__:
            # We need to getattr so the Constant descriptor is triggered.
            yield getattr(cls, name)
    
