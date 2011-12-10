#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod


class AbstractLayoutManager(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def initialize(self):
        raise NotImplementedError

    @abstractmethod
    def update_constraints(self):
        raise NotImplementedError
    
    @abstractmethod
    def layout(self):
        raise NotImplementedError


class NullLayoutManager(AbstractLayoutManager):
    """ A LayoutManager that does nothing.

    """

    def initialize(self):
        pass

    def update_constraints(self):
        pass

    def layout(self):
        pass

