#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod


#------------------------------------------------------------------------------
# Abstract Scope Listener
#------------------------------------------------------------------------------
class AbstractScopeListener(object):
    """ An abstract interface definition for scope listeners.

    A scope listener will be notified when an attribute is accessed via
    dynamic scoping.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def dynamic_load(self, obj, name, value):
        """ Called after the scope dynamically loads an attribute.

        Parameters
        ----------
        obj : object
            The object which owns the attribute.

        name : str
            The name of the attribute loaded.

        value : object
            The value of the loaded attribute.

        """
        raise NotImplementedError


#------------------------------------------------------------------------------
# Dynamic Scope
#------------------------------------------------------------------------------
class DynamicAttributeError(AttributeError):
    """ A custom Attribute error for use with dynamic scoping.

    DynamicScope operates by catching AttributeError and converting it
    into a key error. This DynamicAttributeError can be raised by user
    code in order to escape the trapping and bubble up.

    """
    pass


class DynamicScope(object):
    """ A custom mapping object that implements Enaml's dynamic scope.

    The __getitem__ method of this object is called when LOAD_NAME
    opcode is encountered in a code object which has been transformed
    by the Enaml compiler chain.

    Notes
    -----
    Strong references are kept to all objects passed to the constructor,
    so these scope objects should be created as needed and discarded in
    order to avoid unnecessary reference cycles.

    """
    def __init__(self, obj, identifiers, overrides, listener):
        """ Initialize a DynamicScope.

        Parameters
        ----------
        obj : Declarative
            The Declarative object which owns the executing code.

        identifiers : dict
            The identifiers available to the executing code.

        overrides : dict
            A dict of objects which should have higher precedence than
            the identifiers.

        listener : DynamicScopeListener or None
            A listener which should be notified when a name is loaded
            via dynamic scoping.

        """
        self._obj = obj
        self._identifiers = identifiers
        self._overrides = overrides
        self._listener = listener

    def __getitem__(self, name):
        """ Lookup and return an item from the scope.

        Parameters
        ----------
        name : str
            The name of the item to retrieve from the scope.

        Raises
        ------
        KeyError
            The named item is not contained in the scope.

        """
        dct = self._overrides
        if name in dct:
            return dct[name]
        dct = self._identifiers
        if name in dct:
            return dct[name]
        parent = self._obj
        while parent is not None:
            try:
                value = getattr(parent, name)
            except DynamicAttributeError:
                raise
            except AttributeError:
                parent = parent.parent
            else:
                listener = self._listener
                if listener is not None:
                    listener.dynamic_load(parent, name, value)
                return value
        raise KeyError(name)

    def __setitem__(self, name, value):
        """ Set an item in the scope.

        Parameters
        ----------
        name : str
            The name of the item to set in the scope.

        value : object
            The object to set in the scope.

        """
        # This method is required for pdb to function properly.
        self._overrides[name] = value

    def __contains__(self, name):
        """ Returns True if the name is in scope, False otherwise.

        """
        # This method is required for pdb to function properly.
        if isinstance(name, basestring):
            # Temporarily disable the listener during scope testing.
            listener = self._listener
            self._listener = None
            try:
                self.__getitem__(name)
            except KeyError:
                res = False
            else:
                res = True
            finally:
                self._listener = listener
        else:
            res = False
        return res


#------------------------------------------------------------------------------
# Nonlocals
#------------------------------------------------------------------------------
class Nonlocals(object):
    """ An object which implements userland dynamic scoping.

    An instance of this object is made available with the `nonlocals`
    magic name in the scope of an expression.

    """
    def __init__(self, obj, listener):
        """ Initialize a nonlocal scope.

        Parameters
        ----------
        obj : Declarative
            The Declarative object which owns the executing code.

        listener : DynamicScopeListener or None
            A listener which should be notified when a name is loaded
            via dynamic scoping.

        """
        self._nls_obj = obj
        self._nls_listener = listener

    def __repr__(self):
        """ A pretty representation of the NonlocalScope.

        """
        return 'Nonlocals[%s]' % self._obj

    def __call__(self, level=0):
        """ Get a new nonlocals object for the given offset.

        Parameters
        ----------
        level : int, optional
            The number of levels up the tree to offset. The default is
            zero and indicates no offset. The level must be >= 0.

        """
        if not isinstance(level, int) or level < 0:
            msg = ('The nonlocal scope level must be an int >= 0. '
                   'Got %r instead.')
            raise ValueError(msg % level)
        offset = 0
        target = self._nls_obj
        while target is not None and offset != level:
            target = target.parent
            offset += 1
        if offset != level:
            msg = 'Scope level %s is out of range'
            raise ValueError(msg % level)
        return Nonlocals(target, self._nls_listener)

    def __getattr__(self, name):
        """ A convenience method which allows accessing items in the
        scope via getattr instead of getitem.

        """
        try:
            return self.__getitem__(name)
        except KeyError:
            msg = "%s has no attribute '%s'" % (self, name)
            raise AttributeError(msg)

    def __setattr__(self, name, value):
        """ A convenience method which allows setting items in the
        scope via setattr instead of setitem.

        """
        if name in ('_nls_obj', '_nls_listener'):
            super(Nonlocals, self).__setattr__(name, value)
        else:
            try:
                self.__setitem__(name, value)
            except KeyError:
                msg = "%s has no attribute '%s'" % (self, name)
                raise AttributeError(msg)

    def __getitem__(self, name):
        """ Lookup and return an item from the nonlocals.

        Parameters
        ----------
        name : str
            The name of the item to retrieve from the nonlocals.

        Raises
        ------
        KeyError
            The named item is not contained in the nonlocals.

        """
        parent = self._nls_obj
        while parent is not None:
            try:
                value = getattr(parent, name)
            except DynamicAttributeError:
                raise
            except AttributeError:
                parent = parent.parent
            else:
                listener = self._nls_listener
                if listener is not None:
                    listener.dynamic_load(parent, name, value)
                return value
        raise KeyError(name)

    def __setitem__(self, name, value):
        """ Sets the value of the nonlocal.

        Parameters
        ----------
        name : str
            The name of the item to set in the nonlocals.

        value : object
            The value to set in the nonlocals.

        Raises
        ------
        KeyError
            The named item is not contained in the nonlocals.

        """
        parent = self._nls_obj
        while parent is not None:
            # It's not sufficient to try to do setattr(...) here and
            # catch the AttributeError, because HasStrictTraits raises
            # a TraitError in these cases and it becomes impossible
            # to distinguish that error from a trait typing error
            # without checking the message of the exception.
            try:
                getattr(parent, name)
            except DynamicAttributeError:
                pass # ignore uninitialized attribute errors
            except AttributeError:
                parent = parent.parent
                continue
            setattr(parent, name, value)
            return
        raise KeyError(name)

    def __contains__(self, name):
        """ True if the name is in the nonlocals, False otherwise.

        """
        if isinstance(name, basestring):
            # Temporarily disable the listener during scope testing.
            listener = self._nls_listener
            self._nls_listener = None
            try:
                self.__getitem__(name)
            except KeyError:
                res = False
            else:
                res = True
            finally:
                self._nls_listener = listener
        else:
            res = False
        return res

