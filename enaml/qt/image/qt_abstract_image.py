#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from weakref import WeakKeyDictionary
from enaml.core.signaling import Signal
from ..qt_object import QtObject
from ..qt.QtGui import QImage

class QtAbstractImage(QtObject):
    """ Base class for Qt4 implementation of Image subclasses
    
    This class is not meant to be instantiated.
    
    """
    refreshed = Signal()
    
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the QPixmap
        
        Subclasses should use the snapshot to create other attributes and
        populate the QPixmap.
        
        """
        return QImage()
    
    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------    
    def on_action_refresh(self, content):
        """ Handle the 'refresh' action from the Enaml widget

        """
        self.refresh()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def refresh(self):
        """ Refresh the image
        
        The abstract image just calls the refreshed Signal
        
        """
        self.refreshed.emit()