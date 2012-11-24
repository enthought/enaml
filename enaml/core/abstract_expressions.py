#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from enaml.signaling import Signal


class AbstractListener(object):
    """ An interface definition for creating attribute listeners.

    Listeners are registered with `Declarative` instances using the
    `bind_listener` method to track changes to their attributes.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def value_changed(self, obj, name, old, new):
        """ Called when the attribute on the object has changed.

        Parameters
        ----------
        obj : Declarative
            The Declarative object which owns the attribute.

        name : str
            The name of the attribute which changed.

        old : object
            The old value of the attribute.

        new : object
            The new value of the attribute.

        """
        raise NotImplementedError


class AbstractExpression(object):
    """ An abstract interface definition for creating expressions.

    Expressions are registered with `Declarative` instances using the
    `bind_expression` method to provide computed attribute values.

    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def eval(self, obj, name):
        """ Evaluate and return the results of the expression.

        Parameters
        ----------
        obj : Declarative
            The declarative object which owns the expression.

        name : str
            The attribute name on `obj` for which this expression is
            providing the value.

        """
        raise NotImplementedError


class AbstractListenableExpression(AbstractExpression):
    """ An abstract interface definition for creating listenable
    expressions.

    Listenable expressions are registered with `Declarative` instances
    using the `bind_expression` method to provide dynamically computed
    attribute values at runtime.

    """
    #: An Enaml Signal emitted by the expression when it becomes invalid.
    #: The payload of the signal will be the name that was passed to the
    #: `eval` method during the last expression evaluation.
    invalidated = Signal()

