from abc import ABCMeta, abstractmethod


class AbstractLayoutManager(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def initialize(self):
        raise NotImplementedError

    @abstractmethod
    def update_constraints_if_needed(self):
        raise NotImplementedError
    
    @abstractmethod
    def set_needs_update_constraints(self, needs=True):
        raise NotImplementedError
    
    @abstractmethod
    def update_constraints(self):
        raise NotImplementedError
    
    @abstractmethod
    def layout_if_needed(self):
        raise NotImplementedError
    
    @abstractmethod
    def set_needs_layout(self, needs=True):
        raise NotImplementedError
    
    @abstractmethod
    def layout(self):
        raise NotImplementedError

