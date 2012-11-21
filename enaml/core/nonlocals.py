#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
class Nonlocals(object):
    """ An object which implements implicit attribute scoping starting
    at a given object in the tree. It is used in conjuction with a
    nonlocals() instance to allow for explicit referencing of values
    which would otherwise be implicitly scoped.

    """
    def __init__(self, obj, attr_cb):
        """ Initialize a nonlocal scope.

        Parameters
        ----------
        obj : Declarative
            The Declarative instance which forms the first level of
            the scope.

        attr_cb : callable or None
            A callable which is called when an implicit attribute is
            found and accessed on the object. The arguments passed are
            the object and the attribute name.

        """
        self._nls_obj = obj
        self._nls_attr_cb = attr_cb

    def __repr__(self):
        """ A pretty representation of the NonlocalScope.

        """
        templ = 'NonlocalScope[%s]'
        return templ % self._nls_obj

    def __call__(self, level=0):
        """ Returns a new nonlocal scope object offset the given number
        of levels in the hierarchy.

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

        return NonlocalScope(target, self._nls_attr_cb)

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
        if name in ('_nls_obj', '_nls_attr_cb'):
            super(NonlocalScope, self).__setattr__(name, value)
        else:
            try:
                self.__setitem__(name, value)
            except KeyError:
                msg = "%s has no attribute '%s'" % (self, name)
                raise AttributeError(msg)

    def __getitem__(self, name):
        """ Returns the named item beginning at the current scope object
        and progressing up the tree until the named attribute is found.
        A KeyError is raised if the attribute is not found.

        """
        parent = self._nls_obj
        while parent is not None:
            try:
                res = getattr(parent, name)
            except AttributeError:
                parent = parent.parent
            else:
                cb = self._nls_attr_cb
                if cb is not None:
                    cb(parent, name)
                return res
        raise KeyError(name)

    def __setitem__(self, name, value):
        """ Sets the value of the scope by beginning at the current scope
        object and progressing up the tree until the named attribute is
        found. A KeyError is raise in the attribute is not found.

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
            except UninitializedAttributeError:
                pass
            except AttributeError:
                parent = parent.parent
                continue
            setattr(parent, name, value)
            return
        raise KeyError(name)

    def __contains__(self, name):
        """ Return True if the name is found in the scope, False
        otherwise.

        """
        with swap_attribute(self, '_nls_attr_cb', None):
            if isinstance(name, basestring):
                try:
                    self.__getitem__(name)
                except KeyError:
                    res = False
                else:
                    res = True
            else:
                res = False
        return res
