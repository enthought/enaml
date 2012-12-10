#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod


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

