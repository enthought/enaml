#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_image import QtImage

from ..qt.QtCore import QSize
from ..qt.QtGui import QIcon

from ....noncomponents.abstract_icon import AbstractTkIcon


MODE_MAP = {
    'normal': QIcon.Normal,
    'disabled': QIcon.Disabled,
    'active': QIcon.Active,
    'selected': QIcon.Selected,
}


STATE_MAP = {
    'on': QIcon.On,
    'off': QIcon.Off,
}


class QtIcon(AbstractTkIcon):
    """ A Qt4 implementation of AbstractTkIcon.
    
    """
    def __init__(self, qicon=None):
        """ Initialize a QtIcon.

        Parameters
        ----------
        qicon : QIcon instance or None, optional
            A QIcon instance holding the data. If None is passed, then 
            a new QIcon instance will be constructed.

        """
        if qicon is None:
            qicon = QIcon()
        self._qicon = qicon

    #--------------------------------------------------------------------------
    # Abstract API Implementation
    #--------------------------------------------------------------------------
    @classmethod
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
        new_icon = cls(QIcon(path))
        return new_icon

    @classmethod
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
        if not isinstance(image, QtImage):
            msg = 'Image must be an instance of QtImage. Got %s instead.'
            raise TypeError(msg % type(image))
        new_icon = cls()
        new_icon.add_image(image, 'normal', 'on')
        return new_icon

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
        qt_size = QSize(*size)
        qt_mode = MODE_MAP.get(mode, QIcon.Normal)
        qt_state = STATE_MAP.get(state, QIcon.On)
        qpixmap = self._qicon.pixmap(qt_size, qt_mode, qt_state)
        qimage = qpixmap.toImage()
        image = QtImage(qimage)
        return image
    
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
        if not isinstance(image, QtImage):
            msg = 'Image must be an instance of QtImage. Got %s instead.'
            raise TypeError(msg % type(image))
        qpixmap = image.as_QPixmap()
        qt_mode = MODE_MAP.get(mode, QIcon.Normal)
        qt_state = STATE_MAP.get(state, QIcon.On)
        self._qicon.addPixmap(qpixmap, qt_mode, qt_state)

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
        qt_size = QSize(*size)
        qt_mode = MODE_MAP.get(mode, QIcon.Normal)
        qt_state = STATE_MAP.get(state, QIcon.On)
        size = self._qicon.actualSize(qt_size, qt_mode, qt_state)
        return (size.width(), size.height())

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
        qt_mode = MODE_MAP.get(mode, QIcon.Normal)
        qt_state = STATE_MAP.get(state, QIcon.On)
        sizes = self._qicon.availableSizes(qt_mode, qt_state)
        return [(size.width(), size.height()) for size in sizes]
            
    #--------------------------------------------------------------------------
    # Toolkit Specific
    #--------------------------------------------------------------------------
    def as_QIcon(self):
        """ Returns the underlying QIcon instance.

        This is provided as a convenience for qt backend components that
        require the QIcon instance.

        """
        return self._qicon

