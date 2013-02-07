#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
class CAtom(object):
    """ The base CAtom class.

    There is a much higher performance version of this class available
    as a C++ extension. Prefer building Enaml with this extension.

    """
    __slots__ = ('_c_atom_data',)

    def __new__(cls, *args, **kwargs):
        count = getattr(cls, "_atom_member_count")
        self = object.__new__(cls)
        self._c_atom_data = [NotImplemented] * count
        return self


class Member(object):
    """ The base Member class.

    There is a much higher performance version of this class available
    as a C++ extension. Prefer building Enaml with this extension.

    """
    __slots__ = ("_member_name", "_member_index")

    def __init__(self):
        self._member_name = "<undefined>"
        self._member_index = 0

    def __get__(self, owner, cls):
        if owner is None:
            return self
        if not isinstance(owner, CAtom):
            t = "Expect object of type `CAtom`. "
            t += "Got object of type `%s` instead."
            raise TypeError(t % type(owner).__name__)
        index = self._member_index
        data = owner._c_atom_data
        if index >= len(data):
            t = "'%s' object has no attribute '%s'"
            typename = type(owner).__name__
            attrname = self._member_name
            raise AttributeError(t % (typename, attrname))
        value = data[index]
        if value is NotImplemented:
            value = data[index] = None
        return value

    def __set__(self, owner, value):
        if not isinstance(owner, CAtom):
            t = "Expect object of type `CAtom`. "
            t += "Got object of type `%s` instead."
            raise TypeError(t % type(owner).__name__)
        index = self._member_index
        data = owner._c_atom_data
        if index >= len(data):
            t = "'%s' object has no attribute '%s'"
            typename = type(owner).__name__
            attrname = self._member_name
            raise AttributeError(t % (typename, attrname))
        data[index] = value

    def __delete__(self, owner):
        if not isinstance(owner, CAtom):
            t = "Expect object of type `CAtom`. "
            t += "Got object of type `%s` instead."
            raise TypeError(t % type(owner).__name__)
        index = self._member_index
        data = owner._c_atom_data
        if index >= len(data):
            t = "'%s' object has no attribute '%s'"
            typename = type(owner).__name__
            attrname = self._member_name
            raise AttributeError(t % (typename, attrname))
        data[index] = NotImplemented


#: Use the faster versions of CAtom and Member if available
try:
   from enaml.extensions.catom import CAtom, Member
except ImportError:
   pass


class AtomMeta(type):
    """ The metaclass for classes derived from Atom.

    This metaclass computes the layout and count of the members in a
    given class, so that the CAtom class can allocate exactly enough
    space for the object data when it is instantiated.

    All classes deriving from Atom will be automatically slotted, which
    will prevent the creation of an instance dictionary and also the
    ability of an Atom to be weakly referenceable. If that behavior is
    needed, then a subclasss should declare the appropriate slots.

    """
    def __new__(meta, name, bases, dct):
        if '__slots__' not in dct:
            dct['__slots__'] = ()
        cls = type.__new__(meta, name, bases, dct)
        base_members = {}
        for base in cls.__mro__[1:]:
            if base is not CAtom:
                for key, value in base.__dict__.iteritems():
                    if isinstance(value, Member):
                        base_members[key] = value
        index = len(base_members)
        for key, value in dct.iteritems():
            if isinstance(value, Member):
                value._member_name = key
                if key in base_members:
                    print 'override', key
                    value._member_index = base_members[key]._member_index
                else:
                    print 'set index', value, index
                    value._member_index = index
                    index += 1
        cls._atom_member_count = index
        return cls


class Atom(CAtom):

    __metaclass__ = AtomMeta

