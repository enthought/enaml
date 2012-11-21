#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod


class AbstractListener(object):
    """ An interface definition for creating attribute listeners.

    Listeners can be regisitered with `Declarative` instances in order
    to track changes to their attributes.

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

    Expressions can be registered with `Declarative` instances in order
    to provide dynamically computed values at runtime.

    """
    __metaclass__ = ABCMeta

    #: An Enaml Signal which should be emitted by the expression when
    #: the the expression is invalidated. If an expression does not
    #: support invalidation, this may be None.
    invalidated = None

    @abstractmethod
    def eval(self, obj):
        """ Evaluate and return the results of the expression.

        Parameters
        ----------
        obj : Declarative
            The declarative object which owns the expression.



        """
        raise NotImplementedError

