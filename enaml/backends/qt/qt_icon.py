#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from ...components.abstract_icon import AbstractTkIcon
from enaml.widgets.qt.qt import QtGui

from .qt_pixmap import QtPixmap

mode_map = {
    'normal': QtGui.QIcon.Normal,
    'disabled': QtGui.QIcon.Disabled,
    'active': QtGui.QIcon.Active,
    'selected': QtGui.QIcon.Selected,
}

state_map = {
    'on': QtGui.QIcon.On,
    'off': QtGui.QIcon.Off,
}

class QtIcon(AbstractTkIcon):
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
    
    Internally, this uses a QIcon instance to store QPixmaps extracted from the
    underlying QtPixmaps.  This QIcon instance is stored in the qicon attribute
    of the class, which is available for other Qt backend components to use.
    
    Arguments
    ---------
    qicon : QIcon instance or None
        A QIcon instance holding the data.  If None is passed, then a new QIcon
        instance will be constructed.
    
    """
    PixmapClass = QtPixmap

    def __init__(self, qicon=None):
        if qicon is None:
            qicon = QtGui.QIcon()
        self.qicon = qicon
    
    def get_pixmap(self, size=(None, None), mode='normal', state='on'):
        """ Get an appropriate QtPixmap instance for the requested size, mode and state
        
        Arguments
        ---------
        
        size : tuple of width, height
            The size of the requested pixmap.
            
        mode : str
            The mode of the requested pixmap.
            
        state : str
            The state of the requested pixmap.
        
        """
        width, height = size
        qt_mode = mode_map.get(mode, QtGui.QIcon.Normal)
        qt_state = state_map.get(state, QtGui.QIcon.On)
        qpixmap = self.qicon.pixmap(width, height, qt_mode, qt_state)
        qimage = qpixmap.toImage()
        pixmap = QtPixmap(qimage)
        return pixmap
    
    def set_pixmap(self, pixmap, mode='normal', state='on'):
        """ Set the appropriate QtPixmap instance for the requested size, mode and state
        
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
        if not isinstance(pixmap, self.PixmapClass):
            raise ValueError('pixmap argument must be an instance of enaml.backends.qt.qt_pixmap.QtPixmap, ' +
                str(pixmap) + ' provided.')
        qpixmap = pixmap.qpixmap
        qt_mode = mode_map.get(mode, QtGui.QIcon.Normal)
        qt_state = state_map.get(state, QtGui.QIcon.On)
        self.qicon.addPixmap(qpixmap, qt_mode, qt_state)

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
        return self.qicon.availableSizes(mode=mode_map.get(mode, QtGui.QIcon.Normal),
            state=state_map.get(mode, QtGui.QIcon.On))

        
    #------------------------------------------------------------------------
    # Constructors
    #------------------------------------------------------------------------
                        
    @classmethod
    def from_file(cls, path):
        """  Create a new Icon from a toolkit Pixmap
        
        Arguments
        ---------
        
        path : str
            The path to the pixmap to use for the default mode and state.
            
        """
        new_icon = cls(QtGui.QIcon(path))
        return new_icon
