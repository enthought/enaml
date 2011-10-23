from abc import ABCMeta, abstractmethod


class AbstractLayoutManager(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def initialize(self, container):
        raise NotImplementedError
    
    @abstractmethod
    def layout(self, container):
        raise NotImplementedError
    

