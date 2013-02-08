#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import sys
from contextlib import contextmanager


if sys.maxint > (1 << 32):
    MAX_MEMBER_COUNT = 63
    ATOM_BIT = 64
else:
    MAX_MEMBER_COUNT = 31
    ATOM_BIT = 32


#: A global sentinel representing C null
null = object()


class CAtom(object):
    """ The base CAtom class.

    There is a much higher performance version of this class available
    as a C++ extension. Prefer building Enaml with this extension.

    """
    __slots__ = ('_notifybits', '_c_atom_data')

    def __new__(cls, *args, **kwargs):
        count = getattr(cls, "_atom_member_count")
        if count > MAX_MEMBER_COUNT:
            raise TypeError("too many members %d" % count)
        self = object.__new__(cls)
        self._notifybits = 0L
        self._c_atom_data = [null] * count
        return self

    def _get_notify_bit(self, bit):
        return bool(self._notifybits & (1 << bit))

    def _set_notify_bit(self, bit, enable):
        if enable:
            self._notifybits |= (1 << bit)
        else:
            self._notifybits &= ~(1 << bit)

    def _is_notify_enabled(self):
        return self._get_notify_bit(ATOM_BIT)

    def _set_notify_enabled(self, enable):
        self._set_notify_bit(ATOM_BIT, enable)

    def _is_member_notify_enabled(self, name):
        member = getattr(type(self), name)
        if not isinstance(member, CMember):
            raise TypeError
        return self._get_notify_bit(member._index)

    def _set_member_notify_enabled(self, name, enable):
        member = getattr(type(self), name)
        if not isinstance(member, CMember):
            raise TypeError
        return self._set_notify_bit(member._index, enable)

    def _notify(self, name, old, new):
        """ Implement in a subclass to receive change notification.

        """
        pass


MEMBER_HAS_DEFAULT = 1

MEMBER_HAS_VALIDATE = 2

class CMember(object):
    """ The base CMember class.

    There is a much higher performance version of this class available
    as a C++ extension. Prefer building Enaml with this extension.

    """
    __slots__ = ('_name', '_index', '_flags')

    def __new__(cls, *args, **kwargs):
        self = object.__new__(cls)
        self._name = "<undefined>"
        self._index = 0
        self._flags = 0
        if hasattr(self, 'default'):
            self._flags |= MEMBER_HAS_DEFAULT
        if hasattr(self, 'validate'):
            self._flags |= MEMBER_HAS_VALIDATE
        return self

    def __get__(self, owner, cls):
        if owner is None:
            return self
        if not isinstance(owner, CAtom):
            t = "Expect object of type `CAtom`. "
            t += "Got object of type `%s` instead."
            raise TypeError(t % type(owner).__name__)
        index = self._index
        data = owner._c_atom_data
        if index >= len(data):
            t = "'%s' object has no attribute '%s'"
            typename = type(owner).__name__
            attrname = self._name
            raise AttributeError(t % (typename, attrname))
        value = data[index]
        if value is not null:
            return value
        if self._flags & MEMBER_HAS_DEFAULT:
            value = self.default(owner, self._name)
        else:
            value = None
        data[index] = value
        return value

    def __set__(self, owner, value):
        if not isinstance(owner, CAtom):
            t = "Expect object of type `CAtom`. "
            t += "Got object of type `%s` instead."
            raise TypeError(t % type(owner).__name__)
        index = self._index
        data = owner._c_atom_data
        if index >= len(data):
            t = "'%s' object has no attribute '%s'"
            typename = type(owner).__name__
            attrname = self._name
            raise AttributeError(t % (typename, attrname))
        if self._flags & MEMBER_HAS_VALIDATE:
            print 'here'
            value = self.validate(owner, self._name, value)
        old = data[index]
        data[index] = value
        if owner._get_notify_bit(ATOM_BIT) and owner._get_notify_bit(index):
            owner._notify(self._name, old, value)

    def __delete__(self, owner):
        if not isinstance(owner, CAtom):
            t = "Expect object of type `CAtom`. "
            t += "Got object of type `%s` instead."
            raise TypeError(t % type(owner).__name__)
        index = self._index
        data = owner._c_atom_data
        if index >= len(data):
            t = "'%s' object has no attribute '%s'"
            typename = type(owner).__name__
            attrname = self._name
            raise AttributeError(t % (typename, attrname))
        data[index] = null
        # XXX notify on delete


#: Use the faster C++ versions of CAtom and CMember if available
try:
  from enaml.extensions.catom import CAtom, CMember, MAX_MEMBER_COUNT
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
        members = {}
        for base in cls.__mro__[1:]:
            if base is not CAtom:
                for key, value in base.__dict__.iteritems():
                    if isinstance(value, CMember):
                        members[key] = value
        index = len(members)
        for key, value in dct.iteritems():
            if isinstance(value, CMember):
                value._name = key
                if key in members:
                    value._index = members[key]._index
                else:
                    value._index = index
                    index += 1
                members[key] = value
        if index > MAX_MEMBER_COUNT:
            t = 'A `CAtom` subclass can have at most %d members. '
            t += 'The `%s` class defines %d.'
            raise TypeError(t % (MAX_MEMBER_COUNT, name, index))
        cls._atom_member_count = index
        cls._atom_members = members
        return cls


class Atom(CAtom):
    """ The base class for defining atom objects.

    Atom objects are special Python objects which never allocate an
    instance dictionary unless one is explicitly requested. Instead,
    the storage that is allocated for an atom is computed based on the
    `Member` variables declared on the atom with no over allocation.

    These restrictions make atom objects slightly less flexible than
    normal Python objects, but they are ~10x more memory efficient for
    objects with many attributes. Attribute access on Atom objects is
    also slightly faster than for normal Python objects.

    """
    __metaclass__ = AtomMeta

    @contextmanager
    def suppress_notifications(self, *names):
        """ Disable member notifications within a context.

        Parameters
        ----------
        *names
            The string names of the members to suppress. If not given,
            all members are suppressed.

        Returns
        -------
        result : contextmanager
            A context manager which disables the relevant notifications
            for the duration of the context. When the context exits,
            the notification state is retored to its previous state.

        """
        if len(names) == 0:
            old = self._is_notify_enabled()
            self._set_notify_enabled(False)
        else:
            old = []
            for name in names:
                old.append((name, self._is_member_notify_enabled(name)))
                self._set_member_notify_enabled(name, False)
        yield
        if len(names) == 0:
            self._set_notify_enabled(old)
        else:
            for name, enable in old:
                self._set_member_notify_enabled(name, enable)

