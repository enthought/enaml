#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" A pure Python implementation of the catom.cpp extension module.

This exists to make Enaml usable without a C++ compiler. However, it is
much slower than the extension, and production deployments should use
Enaml with the compiled extension modules for the best performance.

"""
from collections import namedtuple


#: A global sentinel representing C null
null = object()


#: Bit position constants
ATOM_BIT = 0
INDEX_OFFSET = 1


#: Member flag bitfield values
MEMBER_HAS_DEFAULT = 0x01
MEMBER_HAS_VALIDATE = 0x02


#: A namedtuple which holds information about an atom member change.
MemberChange = namedtuple('MemberChange', 'object name old new')


def get_notify_bit(atom, bit):
    return atom._notifybits & (1 << bit)


def set_notify_bit(atom, bit, enable):
    if enable:
        atom._notifybits |= (1 << bit)
    else:
        atom._notifybits &= ~(1 << bit)


class CAtom(object):
    """ The base CAtom class.

    There is a much higher performance version of this class available
    as a C++ extension. Prefer building Enaml with this extension.

    """
    __slots__ = ('_notifybits', '_c_atom_data')

    def __new__(cls, *args, **kwargs):
        self = object.__new__(cls)
        count = len(cls._atom_members)
        self._notifybits = 0
        self._c_atom_data = [null] * count
        return self

    def lookup_member(self, name):
        """ Lookup a member on the object.

        """
        ob_type = type(self)
        member = getattr(ob_type, name, None)
        if not isinstance(member, CMember):
            raise TypeError("object has no member '%s'" % member)
        return member

    def notifications_enabled(self, name=None):
        """ Get whether notifications are enabled for the atom.

        """
        if name is None:
            return bool(get_notify_bit(self, ATOM_BIT))
        member = self.lookup_member(name)
        return bool(get_notify_bit(self, member._index + INDEX_OFFSET))

    def enable_notifications(self, name=None):
        """ Enable notifications for the atom.

        """
        if name is None:
            set_notify_bit(self, ATOM_BIT, True)
        else:
            member = self.lookup_member(name)
            set_notify_bit(self, member._index + INDEX_OFFSET, True)

    def disable_notifications(self, name=None):
        """ Disable notifications for the atom.

        """
        if name is None:
            set_notify_bit(self, ATOM_BIT, False)
        else:
            member = self.lookup_member(name)
            set_notify_bit(self, member._index + INDEX_OFFSET, False)

    def notify(self, change):
        """ Reimplement in a subclass to receive change notification.

        """
        pass


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
        return self

    def has_default():
        def getter(self):
            return self._flags & MEMBER_HAS_DEFAULT
        def setter(self, value):
            if value:
                self._flags |= MEMBER_HAS_DEFAULT
            else:
                self._flags &= ~MEMBER_HAS_DEFAULT
        return getter, setter

    has_default = property(*has_default())

    def has_validate():
        def getter(self):
            return self._flags & MEMBER_HAS_VALIDATE
        def setter(self, value):
            if value:
                self._flags |= MEMBER_HAS_VALIDATE
            else:
                self._flags &= ~MEMBER_HAS_VALIDATE
        return getter, setter

    has_validate = property(*has_validate())

    def __get__(self, owner, cls):
        """ Get the value of the member.

        """
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
        """ Set the value of the member.

        """
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
            value = self.validate(owner, self._name, value)
        old = data[index]
        data[index] = value
        bit = index + INDEX_OFFSET
        if get_notify_bit(owner, ATOM_BIT) and get_notify_bit(owner, bit):
            if old is null:
                old = None
            try:
                changed = old != value
            except Exception:
                changed = True
            if changed:
                change = MemberChange(owner, self._name, old, value)
                owner.notify(change)

    def __delete__(self, owner):
        """ Delete the value of the member.

        """
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
        old = data[index]
        data[index] = null
        bit = index + INDEX_OFFSET
        if get_notify_bit(owner, ATOM_BIT) and get_notify_bit(owner, bit):
            if old is not null:
                change = MemberChange(owner, self._name, old, None)
                owner.notify(change)


#: Use the faster C++ versions if available
try:
    from enaml.extensions.catom import CAtom, CMember, MemberChange
except ImportError:
    pass

