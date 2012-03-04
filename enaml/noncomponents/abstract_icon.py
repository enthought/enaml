#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod

from ..utils import abstractclassmethod


class AbstractTkIcon(object):
    """ An abstract base class which represents a toolkit independent 
    abstraction of an icon.
    
    Concrete implemetations of the AbstractTkIcon class allow the user 
    to specify different images for different states of the icon, so that
    a component can select the image which is most appropriate for 
    display in the widget.
    
    The icon can specify modes and states, which toolkit objects may use
    to select which image to use for display. The available modes are:
        
        'normal'
            A control in its normal mode
        
        'disabled'
            A control which is disabled or greyed-out
    
        'active'
            A control which is currently activiated
    
        'selected'
            A control in a selected state
    
    Not every mode is used by every backend. 

    The state of an icon may be either:
        
        'on'
            The normal or checked form of the icon.
        
        'off'
            The unchecked form of the icon.
    
    """
    __metaclass__ = ABCMeta
    
    @abstractclassmethod
    def from_file(cls, path):
        """ Create a new icon from a file on disk.

        Parameters
        ----------
        path : string
            The path to the image to use for the default mode and state.
        
        Returns
        -------
        result : AbstractTkIcon
            An new icon instance.

        """
        raise NotImplementedError

    @abstractclassmethod
    def from_image(cls, image):
        """ Create a new icon from an instance of AbstractTkImage using
        the default 'normal' and 'on' states.
                
        Parameters
        ----------
        image : AbstractTkImage
            An appropriate instance of AbstractTkImage to use for the
            default mode and state.
        
        Returns
        -------
        result : AbstractTkIcon
            An new icon instance.

        """
        raise NotImplementedError

    @abstractmethod
    def get_image(self, size, mode='normal', state='on'):
        """ Get an appropriate image instance for the requested size, 
        mode and state.
        
        Parameters
        ----------
        size : (width, height)
            The size of the requested image. The returned image may
            be smaller, but will never be larger than this size.
            
        mode : string, optional
            The mode of the requested image. The default is 'normal'.
            
        state : string, optional
            The state of the requested image. The default is 'on'.
        
        Returns
        -------
        result : AbstractTkImage
            An appropriate image instance.

        """
        raise NotImplementedError

    @abstractmethod
    def add_image(self, image, mode='normal', state='on'):
        """ Add an image instance for use by the icon with the given 
        mode and state.
        
        Parameters
        ----------
        image : AbstractTkImage
            An appropriate image instance.
            
        mode : string, optional
            The mode of the image. The default is 'normal'.
            
        state : string, optional
            The state of the image. The default is 'on'.
        
        """
        raise NotImplementedError

    @abstractmethod
    def actual_size(self, size, mode='normal', state='on'):
        """ Returns the actual size for the requested size, mode, and
        state.

        The returned size may be smaller but will never be larger.

        Parameters
        ----------
        size : (width, height)
            The size of the requested image. The returned image may
            be smaller, but will never be larger than this size.
            
        mode : string, optional
            The mode of the requested image. The default is 'normal'.
            
        state : string, optional
            The state of the requested image. The default is 'on'.
        
        Returns
        -------
        result : (width, height)
            The actual size for the requested size. If no suitable
            match can be found, the result will be (-1, -1).

        """
        raise NotImplementedError
    
    @abstractmethod
    def available_sizes(self, mode='normal', state='on'):
        """ Returns the available image sizes for the given mode and 
        state.
        
        Sizes other than these may be requested, but the implemetation 
        may scale down the image on the fly to the requested size.
        
        Parameters
        ----------
        mode : string, optional
            The requested image mode. The default is 'normal'.
            
        state : string, optional
            The requested image state. The default is 'on'.
        
        Returns
        -------
        results : [(width, height), ... ]
            The list of available sizes for the given mode and state.
            
        """
        raise NotImplementedError

