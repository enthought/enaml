#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
#: A global sentinel representing null
null = object()


class CAtom(object):
    """ The base CAtom class.

    There is a much higher performance version of this class available
    as a C++ extension. Prefer building Enaml with this extension.

    """
    __slots__ = ('_c_atom_data',)

    def __new__(cls, *args, **kwargs):
        count = getattr(cls, "_atom_member_count")
        self = object.__new__(cls)
        self._c_atom_data = [null] * count
        return self

    def notify(self, name, old, new):
        """ Implement in a subclass to receive change notification.

        This will be called for members with the `listenable` flag
        set to True.

        """
        pass


class CMember(object):
    """ The base CMember class.

    There is a much higher performance version of this class available
    as a C++ extension. Prefer building Enaml with this extension.

    """
    __slots__ = (
        '_member_name', '_member_index', 'default_func', 'validate_func'
    )

    def __init__(self):
        self._member_name = "<undefined>"
        self._member_index = 0
        self.listenable = False
        self.default_func = None
        self.validate_func = None

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
        if value is not null:
            return value
        default_func = self.default_func
        if default_func is not None:
            value = default_func(owner, self._member_name)
        else:
            value = None
        data[index] = value
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
        validate_func = self.validate_func
        if validate_func is not None:
            value = validate_func(owner, self._member_name, value)
        old = data[index]
        data[index] = value
        if self.listenable:
            owner.notify(self._member_name, old, value)

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
        data[index] = null


#: Use the faster C++ versions of CAtom and CMember if available
try:
  from enaml.extensions.catom import CAtom, CMember
except ImportError:
  pass


class AtomMeta(type):
    """ The metaclass for classes derived from Atom.

    This metaclass computes the layout and count of the members in a
    given class, so that the CAtom class can allocate exactly enough
    space for the object data when it instantiates an object.

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
                    if isinstance(value, CMember):
                        base_members[key] = value
        index = len(base_members)
        for key, value in dct.iteritems():
            if isinstance(value, CMember):
                value._member_name = key
                if key in base_members:
                    value._member_index = base_members[key]._member_index
                else:
                    value._member_index = index
                    index += 1
        cls._atom_member_count = index
        return cls


class Atom(CAtom):
    """ The base class for defining atom objects.

    Atom objects are special Python objects which never allocate an
    instance dictionary unless one is explicitly requested. Instead,
    the storage that is allocated for an atom is computed based on the
    `Member` variables declared on the atom; there is no overage. It
    is not possible to dynamically add attributes to an Atom object,
    unless an instance dict is requested.

    These restrictions make atom objects slightly less flexible than
    normal Python objects, but they are ~10x more memory efficient for
    objects with many attributes. Attribute access on Atom objects is
    also slightly faster than for normal Python objects.

    """
    __metaclass__ = AtomMeta


def _simple_type_checker(kind):
    def validator(owner, name, value):
        if not isinstance(value, kind):
            t = "The `%s` member on a `%s` object must be an instance of "
            t += "`%s`. Got object of type `%s` instead."
            obj_name = type(owner).__name__
            val_name = type(value).__name__
            kind_name = kind.__name__
            raise TypeError(t % (name, obj_name, kind_name, val_name))
        return value
    return validator


class Member(CMember):
    """ The base class for defining atom members.

    A `Member` provides a storage slot for a piece of data on an `Atom`
    object. The member is a descriptor which gets and sets the value in
    the internal data array on the atom object. It also provides the

    A `Member` descriptor can only be used with subclasses of `Atom`.

    """
    __slots__ = ()

    def __init__(self, kind=None, default=None, factory=None, validate=None,
                 listenable=False):
        """ Initialize a Member.

        Parameters
        ----------
        kind : type, optional
            The type of value allowed to be assigned to this member. If
            a value being assigned is not an instance of this type, a
            TypeError will be raised. If neither a default value nor a
            factory are given, the type will be called with no arguments
            to create the default value for the member.

        default : object, optional
            The default value for the member. If this is provided, it
            should be an immutable value since it will not be copied.

        factory : callable, optional
            A callable object which accepts two arguments, the object
            and the member name, and creates the default value for the
            member. This will override any given default value.

        validate : callable, optional
            A callable which can be provided to validate and convert
            a value before it is assigned to a member. If this is
            given, it will override the type checking of `kind`. It
            must accept three arguments: the object, name, and value.

        listenable : bool, optional
            Whether or not the member is listenable. If True, the
            `notify` method on the atom will be invoked when this
            member changes. The default is False.

        """
        super(Member, self).__init__()
        if kind is not None:
            assert isinstance(kind, type)
        if validate is not None:
            self.validate_func = validate
        elif kind is not None:
            self.validate_func = _simple_type_checker(kind)
        if factory is not None:
            self.default_func = factory
        elif default is not None:
            self.default_func = lambda obj, name: default
        elif kind is not None:
            self.default_func = lambda obj, name: kind()
        self.listenable = listenable


class Bool(Member):

    __slots__ = ()

    def __init__(self, default, listenable=False):
        if default is not None:
            default = bool(default)
        super(Bool, self).__init__(bool, default, listenable=listenable)


class Int(Member):

    __slots__ = ()

    def __init__(self, default=None, listenable=False):
        if default is not None:
            default = int(default)
        super(Int, self).__init__(int, default, listenable=listenable)


class Long(Member):

    __slots__ = ()

    def __init__(self, default=None, listenable=False):
        if default is not None:
            default = long(default)
        super(Long, self).__init__(long, default, listenable=listenable)


class Float(Member):

    __slots__ = ()

    def __init__(self, default=None, listenable=False):
        if default is not None:
            default = float(default)
        super(Float, self).__init__(float, default, listenable=listenable)


class Str(Member):

    __slots__ = ()

    def __init__(self, default=None, listenable=False):
        if default is not None:
            default = str(default)
        super(Str, self).__init__(str, default, listenable=listenable)


class Unicode(Member):

    __slots__ = ()

    def __init__(self, default=None, listenable=False):
        if default is not None:
            default = unicode(default)
        super(Unicode, self).__init__(unicode, default, listenable=listenable)

