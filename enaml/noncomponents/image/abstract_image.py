#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

class AbstractImage(object):
    """ An abstract api for an image class.
    
    """
    __metaclass__ = ABCMeta
    
    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    @abstractmethod
    def as_dict(self):
        """ Return the image as a JSON-serializable dict

        """
        raise NotImplementedError

    @abstractmethod
    def from_dict(self, image_dict):
        """ Receive a JSON representation of an image and convert it into the
        appropriate Python object

        """
        raise NotImplementedError
    
