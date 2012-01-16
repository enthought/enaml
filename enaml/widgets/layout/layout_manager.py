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

    @abstractmethod
    def get_min_size(self):
        raise NotImplementedError

    @abstractmethod
    def get_max_size(self):
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

    def get_min_size(self):
        return (0, 0)

    def get_max_size(self):
        return (-1, -1)
