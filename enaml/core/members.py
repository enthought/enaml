#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .atom import CMember


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
        self._default = default
        self._factory = factory

    def default(self, owner, name):
        """ Get the default value for the member.

        """
        factory = self._factory
        if factory is not None:
            return factory()
        return self._default


class TypedMember(Member):
    """ A member class wich supports type checking validation.

    """
    __slots__ = ('_kind',)

    def __init__(self, kind=None, default=None, factory=None):
        super(TypedMember, self).__init__(default, factory)
        if kind is not None:
            assert isinstance(kind, type), "Kind must be a type"
            self._kind = kind
        else:
            self._kind = object

    def validate(self, owner, name, value):
        if not isinstance(value, self._kind):
            t = "Member '%s' requires object of type `%s`. "
            t += "Got object of type `%s` instead."
            kind_type = self._kind.__name__
            val_type = type(value).__name__
            raise TypeError(t % (name, kind_type, val_type))
        return value


class Bool(TypedMember):

    __slots__ = ()

    def __init__(self, default=False):
        assert isinstance(default, bool)
        super(Bool, self).__init__(bool, default)


class Int(TypedMember):

    __slots__ = ()

    def __init__(self, default=0):
        assert isinstance(default, int)
        super(Int, self).__init__(int, default)


class Long(TypedMember):

    __slots__ = ()

    def __init__(self, default=0L):
        assert isinstance(default, long)
        super(Long, self).__init__(long, default)


class Float(TypedMember):

    __slots__ = ()

    def __init__(self, default=0.0):
        assert isinstance(default, float)
        super(Float, self).__init__(float, default)


class BaseString(TypedMember):

    __slots__ = ()

    def __init__(self, default=''):
        assert isinstance(default, basestring)
        super(Str, self).__init__(basestring, default)


class Str(TypedMember):

    __slots__ = ()

    def __init__(self, default=''):
        assert isinstance(default, str)
        super(Str, self).__init__(str, default)


class Unicode(TypedMember):

    __slots__ = ()

    def __init__(self, default=u''):
        assert isinstance(default, unicode)
        super(Unicode, self).__init__(unicode, default)


class Tuple(TypedMember):

    __slots__ = ()

    def __init__(self, default=()):
        assert isinstance(default, tuple)
        super(Tuple, self).__init__(tuple, default)


class List(TypedMember):

    __slots__ = ()

    @staticmethod
    def list_factory(owner, name):
        return []

    def __init__(self, default=None):
        if default is None:
            factory = self.list_factory
        else:
            assert isinstance(default, list)
            factory = lambda owner, name: default[:]
        super(List, self).__init__(list, factory=factory)


class Dict(TypedMember):

    __slots__ = ()

    @staticmethod
    def dict_factory(owner, name):
        return {}

    def __init__(self, default=None):
        if default is None:
            factory = self.dict_factory
        else:
            assert isinstance(default, dict)
            factory = lambda owner, name: default.copy()
        super(Dict, self).__init__(dict, factory=factory)

