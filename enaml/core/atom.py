#------------------------------------------------------------------------------
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from contextlib import contextmanager
import re

from .catom import CAtom, CMember


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
        for base in reversed(cls.__mro__[1:-1]):
            if base is not CAtom and issubclass(base, CAtom):
                members.update(base._atom_members)
        count = len(members)
        for key, value in dct.iteritems():
            if isinstance(value, CMember):
                value._name = key
                if key in members:
                    value._index = members[key]._index
                else:
                    value._index = count
                    count += 1
                members[key] = value
        # The CAtom class expects this class attribute to exist.
        cls._atom_members = members
        return cls


class Atom(CAtom):
    """ The base class for defining atom objects.

    `Atom` objects are special Python objects which never allocate an
    instance dictionary unless one is explicitly requested. The storage
    for an atom is instead computed from the `Member` objects declared
    on the class. Memory is reserved for these members with no over
    allocation.

    This restriction make atom objects a bit less flexible than normal
    Python objects, but they are between 3x-10x more memory efficient
    than normal objects depending on the number of attributes.

    """
    __metaclass__ = AtomMeta

    @classmethod
    def members(cls):
        """ Get the members dictionary for the type.

        Returns
        -------
        result : dict
            The dictionary of members defined on the class. User code
            should not modify the contents of the dict.

        """
        return cls._atom_members

    @contextmanager
    def suppress_notifications(self, name=None, regex=False):
        """ Disable member notifications within in a context.

        Parameters
        ----------
        name : str, optional
            The member name on which to suppress notifications. If not
            given, all notifications will be suppressed. The default is
            None.

        regex : bool, optional
            If True, the `name` is a regex pattern. All members with a
            matching name will be suppressed. The default is False.

        Returns
        -------
        result : contextmanager
            A context manager which disables the relevant notifications
            for the duration of the context. When the context exits,
            the notification state is retored to its previous state.

        """
        if name is None:
            reenable = self.notifications_enabled()
            if reenable:
                self.disable_notifications()
            yield
            if reenable:
                self.enable_notifications()
        else:
            disabled = []
            members = self.members()
            if not regex and name in members:
                if self.notifications_enabled(name):
                    self.disable_notifications(name)
                    disabled.append(name)
            else:
                rgx = re.compile(name)
                for key in members:
                    if rgx.match(key) and self.notifications_enabled(key):
                        self.disable_notifications(key)
                        disabled.append(key)
            yield
            for name in disabled:
                self.enable_notifications(name)

