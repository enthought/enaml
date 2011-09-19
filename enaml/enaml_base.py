#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import HasStrictTraits, Instance, Dict, Str, Set, DelegatesTo, Any

from .expressions import IExpressionDelegate, IExpressionNotifier


class EnamlBase(HasStrictTraits):
    """ The most base class of types used in Enaml source files.

    Attributes
    ----------
    _delegates : Dict(Str, Instance(IExpressionDelegate))
        The expression delegates currently installed on this component.
        This is a protected attribute and is managed internally.
        Manipulate at your own risk.

    _notifiers : Set(Instance(IExpressionNotifier))
        The expression notifiers currently installed on this component.
        This is a protected attribute and is managed internally.
        Manipulate at your own risk.

    Methods
    -------
    set_attribute_delegate(name, delegate)
        Delegates the value of the attribute to the delegate.

    add_attribute_notifier(name, notifier)
        Adds a notifier for the given attribute name.

    """
    _delegates = Dict(Str, Instance(IExpressionDelegate))

    _notifiers = Set(Instance(IExpressionNotifier))

    @classmethod
    def protect(cls, *names):
        protected = set(names)
        parent_cls = cls.mro()[1]
        try:
            parent_protected = parent_cls.__protected__
        except AttributeError:
            parent_protected = ()
        protected.update(parent_protected)
        cls.__protected__ = protected
        return cls

    @classmethod
    def unprotect(cls, *names):
        try:
            protected = cls.__protected__
        except:
            protected = set()
        parent_cls = cls.mro()[1]
        try:
            parent_protected = parent_cls.__protected__
        except AttributeError:
            parent_protected = ()
        protected.update(parent_protected)
        protected.difference_update(names)
        cls.__protected__ = protected
        return cls

    def _set_extended_delegate(self, name, delegate):
        root, attr = name.split('.')
        root_obj = getattr(self, root)
        if isinstance(root_obj, EnamlBase):
            root_obj.set_attribute_delegate(attr, delegate)

    def _set_extended_notifier(self, name, notifier):
        root, attr = name.split('.')
        root_obj = getattr(self, root)
        if isinstance(root_obj, EnamlBase):
            root_obj.add_attribute_notifier(attr, notifier)

    def set_attribute_delegate(self, name, delegate):
        """ Delegates the value of the attribute to the delegate.

        Call this method to intercept the value of the standard trait
        attribute and delegate that value to the given delegate.

        Arguments
        ---------
        name : string
            The name of the attribute to delegate.

        delegate : IExpressionDelegate
            An implementor of the IExpressionDelegate interface.

        """
        if '.' in name:
            self._set_extended_delegate(name, delegate)
            return

        if name in self.__protected__:
            msg = ('The `%s` attribute of the `%s` object is protected and '
                   'cannot be used in left associative Enaml expressions.')
            raise AttributeError(msg % (name, type(self).__name__))

        trait = self.trait(name)
        delegates = self._delegates
        delegate_name = '_%s_enaml_delegate' % name

        if trait is None:
            trait = Any()()

        if delegate_name in delegates:
            msg = 'The `%s` attr on the `%s` object is already associated.'
            raise ValueError(msg % (name, type(self).__name__))
        else:
            delegates[delegate_name] = delegate

        delegate.bind(self, name, trait())

        self.add_trait(delegate_name, delegate)
        self.add_trait(name, DelegatesTo(delegate_name, 'value'))

        # Need to fire trait_added or the delegate
        # listeners don't get hooked up properly.
        self.trait_added = name

    def add_attribute_notifier(self, name, notifier):
        """ Adds a notifier for the given attribute name.

        Call this method to hook up an IExpressionNotifier to the
        given attribute name.

        Arguments
        ---------
        name : string
            The name of the attribute to delegate.

        notifier : IExpressionNotifier
            An implementor of the IExpressionNotifer interface.

        """
        if '.' in name:
            self._set_extended_notifier(name, notifier)
            return

        trait = self.trait(name)
        if trait is None:
            msg = '`%s` is not a proper attribute on the `%s` object.'
            raise AttributeError(msg % (name, type(self).__name__))

        self._notifiers.add(notifier)
        notifier.bind(self, name)


EnamlBase.protect('_delegates', '_notifiers')

