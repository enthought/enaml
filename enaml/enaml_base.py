#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import weakref

from traits.api import (HasStrictTraits, Instance, Dict, Str, Set, DelegatesTo, 
                        Any, List, Callable)

from .expressions import IExpressionDelegate, IExpressionNotifier


class WeakDelayedBinder(object):

    def __init__(self, obj, *args, **kwargs):
        self.wr_obj = weakref.ref(obj)
        self.args = args
        self.kwargs = kwargs
        
    def __call__(self):
        obj = self.wr_obj()
        if obj is not None:
            obj.bind(*self.args, **self.kwargs)


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

    _binders = List(Callable)

    @classmethod
    def protect(cls, *names):
        protected = set(names)
        try:
            protected.update(cls.__protected__)
        except AttributeError:
            pass
        cls.__protected__ = protected

    def set_attribute_delegate(self, name, delegate):
        """ Delegates the value of the attribute to the delegate.

        Call this method to intercept the value of the standard trait
        attribute and delegate that value to the given delegate.

        Arguments
        ---------
        name : 2-tuple
            The (root, leaf) string name of the attribute to delegate. If 
            Leaf is not None, it's taken to be an extended attribute name.

        delegate : IExpressionDelegate
            An implementor of the IExpressionDelegate interface.

        """
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
            self.remove_trait(delegate_name)
            self.remove_trait(name)

        delegates[delegate_name] = delegate

        self.add_trait(delegate_name, delegate)
        self.add_trait(name, DelegatesTo(delegate_name, 'value'))

        # Need to fire trait_added or the delegate
        # listeners don't get hooked up properly.
        self.trait_added = name
        
        self._binders.append(WeakDelayedBinder(delegate, self, name, trait()))

    def add_attribute_notifier(self, name, notifier):
        """ Adds a notifier for the given attribute name.

        Call this method to hook up an IExpressionNotifier to the
        given attribute name.

        Arguments
        ---------
        name : 2-tuple
            The (root, leaf) string name of the attribute to delegate. If 
            Leaf is not None, it's taken to be an extended attribute name.

        notifier : IExpressionNotifier
            An implementor of the IExpressionNotifer interface.

        """
        trait = self.trait(name)
        if trait is None:
            msg = '`%s` is not a proper attribute on the `%s` object.'
            raise AttributeError(msg % (name, type(self).__name__))

        self._notifiers.add(notifier)
        self._binders.append(WeakDelayedBinder(notifier, self, name))

    def bind_expressions(self):
        for binder in self._binders:
            binder()
        self._binders = []            


EnamlBase.protect('_delegates', '_notifiers')

