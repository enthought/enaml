#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasPrivateTraits, Disallow


class HasPrivateTraits_Patched(HasPrivateTraits):
    """ A HasPrivateTraits subclass which patches some traits bugs and
    adds some useful features.

    """
    #: The HasTraits class defines a class attribute 'set' which is a
    #: deprecated alias for the 'trait_set' method. The problem is that
    #: having that as an attribute interferes with the ability of Enaml
    #: expressions to resolve the builtin 'set', since dynamic scoping
    #: takes precedence over builtins. This resets those ill-effects.
    set = Disallow

    def add_notifier(self, name, notifier):
        """ Add a notifier to a trait on the object.

        This is different from `on_trait_change` in that it allows the
        developer to provide the notifier directly which provides an
        opportunity for more efficient notification patterns.

        """
        self._trait(name, 2)._notifiers(1).append(notifier)

    def trait_set(self, trait_change_notify=True, **traits):
        """ An overridden HasTraits method which keeps track of the
        trait change notify flag.

        The default implementation of `trait_set` has side effects if a
        call to `setattr` recurses into `trait_set`; the notification
        context of the original call will be reset.

        This reimplemented method will make sure that context is reset
        appropriately for each call. This is required for Enaml since
        bound attributes are lazily computed and set quitely on the fly.

        A ticket has been filed against traits trunk:
            https://github.com/enthought/traits/issues/26

        """
        # Don't use standard attribute access here, because the trait
        # lookup becomes irregular and error prone.
        dct = self.__dict__
        key = '_[trait_change_notify_flag]'
        last = dct.get(key, True)
        dct[key] = trait_change_notify
        self._trait_change_notify(trait_change_notify)
        try:
            for name, value in traits.iteritems():
                setattr(self, name, value)
        finally:
            dct[key] = last
            self._trait_change_notify(last)
        return self

