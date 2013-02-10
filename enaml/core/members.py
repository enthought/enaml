#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .catom import CMember


class Member(CMember):
    """ A simple class for defining data members of an atom.

    A plain `Member` provides support for default values and factories,
    but does not perform any type checking or validation. It is useful
    for creating private storage attributes on an atom.

    """
    __slots__ = ('_default', '_factory')

    def __init__(self, default=None, factory=None):
        """ Initialize a Member.

        Parameters
        ----------
        default : object, optional
            The default value for the member. If this is provided, it
            should be an immutable value. The value will will not be
            copied between owner instances.

        factory : callable, optional
            A callable object which is called with zero arguments and
            returns a default value for the member. This will override
            any value given by `default`.

        """
        self.has_default = True
        self._default = default
        self._factory = factory

    def default(self, owner, name):
        """ Get the default value for the member.

        """
        factory = self._factory
        if factory is not None:
            return factory()
        return self._default


class Typed(Member):
    """ A member class wich supports type validation.

    """
    __slots__ = ('_kind',)

    def __init__(self, kind=None, default=None, factory=None):
        """ Initialize a Typed member.

        Parameters
        ----------
        kind : type, optional
            The allowed type of values assigned to the member.

        default : object, optional
            The default value for the member.

        factory : callable, optional
            The default value factory for the member.

        """
        kind = kind or object
        assert isinstance(kind, type), "Kind must be a type"
        super(Typed, self).__init__(default, factory)
        self.has_validate = True
        self._kind = kind

    def validate(self, owner, name, value):
        """ Validate the value being assigned to the member.

        If the value is not valid, a TypeError is raised.

        Parameters
        ----------
        owner : Atom
            The atom object which owns the value being modified.

        name : str
            The member name of the atom being modified.

        value : object
            The value being assigned to the member.

        Returns
        -------
        result : object
            The original value, provided it passes type validation.

        """
        if not isinstance(value, self._kind):
            t = "The '%s' member on the `%s` object requires a value of type "
            t += "`%s`. Got value of type `%s` instead."
            owner_type = type(owner).__name__
            kind_type = self._kind.__name__
            value_type = type(value).__name__
            raise TypeError(t % (name, owner_type, kind_type, value_type))
        return value


class Bool(Typed):
    """ A typed member of type `bool`.

    """
    __slots__ = ()

    def __init__(self, default=False):
        assert isinstance(default, bool)
        super(Bool, self).__init__(bool, default)


class Int(Typed):
    """ A typed member of type `int`.

    """
    __slots__ = ()

    def __init__(self, default=0):
        assert isinstance(default, int)
        super(Int, self).__init__(int, default)


class Long(Typed):
    """ A typed member of type `long`.

    """
    __slots__ = ()

    def __init__(self, default=0L):
        assert isinstance(default, long)
        super(Long, self).__init__(long, default)


class Float(Typed):
    """ A typed member of type `float`.

    """
    __slots__ = ()

    def __init__(self, default=0.0):
        assert isinstance(default, float)
        super(Float, self).__init__(float, default)


class Str(Typed):
    """ A typed member of type `str`.

    """
    __slots__ = ()

    def __init__(self, default=''):
        assert isinstance(default, str)
        super(Str, self).__init__(str, default)


class Unicode(Typed):
    """ A typed member of type `unicode`.

    Regular strings will be promoted to unicode strings.

    """
    __slots__ = ()

    def __init__(self, default=u''):
        assert isinstance(default, unicode)
        super(Unicode, self).__init__(unicode, default)


class Tuple(Typed):
    """ A typed member of type `tuple`.

    """
    __slots__ = ()

    def __init__(self, default=()):
        assert isinstance(default, tuple)
        super(Tuple, self).__init__(tuple, default)


class List(Typed):
    """ A typed member of type `list`.

    """
    __slots__ = ()

    def __init__(self, default=None):
        if default is None:
            factory = list
        else:
            assert isinstance(default, list)
            factory = lambda: default[:]
        super(List, self).__init__(list, factory=factory)


class Dict(Typed):
    """ A typed member of type `dict`.

    """
    __slots__ = ()

    def __init__(self, default=None):
        if default is None:
            factory = dict
        else:
            assert isinstance(default, dict)
            factory = lambda: default.copy()
        super(Dict, self).__init__(dict, factory=factory)

