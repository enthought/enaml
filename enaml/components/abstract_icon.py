#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from abc import ABCMeta, abstractmethod, abstractproperty

class AbstractTkIcon(object):
    """ Collection of Pixmap instances for display in a component
    
    The Icon class allows the user to specify different images for different
    states of the icon, so that a widget can select the image which is most
    appropriate for display in the widget.
    
    The Icon class can specify modes and states, which toolkit objects may use
    to select which pixmap to use for display.  The available modes are:
        
        normal: for a control in its normal mode
        
        disabled: for a control which is disabled or greyed-out
    
        activated: for a control which is currently activiated
    
        selected: for a control in a selected state
    
    Not every mode is used by every backend.  The state of an icon is either:
        
        on: the normal or checked form of the icon
        
        off: the unchecked form of the icon
    
    """
    __metaclass__ = ABCMeta
    
    PixmapClass = None
    
    @abstractmethod
    def get_pixmap(self, size=(None, None), mode='normal', state='on'):
        """ Get an appropriate Pixmap instance for the requested size, mode and state
        
        Arguments
        ---------
        
        size : tuple of width, height
            The size of the requested pixmap.
            
        mode : str
            The mode of the requested pixmap.
            
        state : str
            The state of the requested pixmap.
        
        """
        raise NotImplemented

    
    @abstractmethod
    def set_pixmap(self, pixmap, mode='normal', state='on'):
        """ Set the appropriate Pixmap instance for the requested size, mode and state
        
        If no images have been set for the corresponding 'normal' and 'on' states
        then this will also set the image as a default for those states as well.
        
        Arguments
        ---------
        
        pixmap : backend AbstractTkPixmap subclass
            The size of the requested pixmap.
            
        mode : str
            The mode of the requested pixmap.
            
        state : str
            The state of the requested pixmap.
        
        """
        raise NotImplemented

    @abstractmethod
    def available_sizes(self, mode='normal', state='on'):
        """ Return the available Pixmap instance sizes for the given mode and state
        
        Other sizes can be requested, but the implemetation may scale the image
        on the fly to the requested size.
        
        Arguments
        ---------
            
        mode : str
            The mode of the requested pixmap.
            
        state : str
            The state of the requested pixmap.
        
        """
        raise NotImplemented
    
    #------------------------------------------------------------------------
    # Constructors
    #------------------------------------------------------------------------

    @classmethod
    def from_pixmap(cls, pixmap):
        """  Create a new Icon from a toolkit Pixmap
        
        Arguments
        ---------
        
        pixmap : backend AbstractTkPixmap subclass
            The pixmap to use for the default mode and state.
        """
        new_icon = cls()
        new_icon.set_pixmap(pixmap, 'normal', 'on')
        return new_icon

    @classmethod
    def from_file(cls, path):
        """  Create a new Icon from a toolkit Pixmap
        
        Arguments
        ---------
        
        path : str
            The path to the pixmap to use for the default mode and state.
            
        """
        return cls.from_pixmap(cls.PixmapClass.from_file(path))
