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

