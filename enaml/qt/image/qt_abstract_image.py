#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from weakref import WeakKeyDictionary
from ..qt_object import QtObject
from ..qt.QtGui import QImage

class QtAbstractImage(QtObject):
    """ Base class for Qt4 implementation of Image subclasses
    
    This class is not meant to be instantiated.
    
    """
    _refresh_callbacks = None
    
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, tree):
        """ Create the QPixmap
        
        Subclasses should use the snapshot to create other attributes and
        populate the QPixmap.
        
        """
        self._widget = QImage()
        self._refresh_callbacks = WeakKeyDictionary()

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------    
    def on_action_refresh(self, content):
        """ Handle the 'refresh' action from the Enaml widget

        """
        self.refresh()

    #--------------------------------------------------------------------------
    # View Handlers
    #--------------------------------------------------------------------------
    def add_view(self, obj, callback_name='refresh_image'):
        """ Add an ImageView or other user of the image
        
        The provided callback name will be resolved and called when the image
        is refreshed.  References to the view are stored in a weak dictionary,
        so Images will not cause their viewers to persist needlessly.
        
        """
        self._refresh_callbacks[obj] = callback_name
    
    def remove_view(self, obj):
        """ Remove an ImageView or other user of the image
        
        """
        del self._refresh_callbacks[obj]
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def refresh(self):
        """ Refresh the image
        
        This notifies all views that the image may have changed.
        
        """
        for obj, callback_name in self._refresh_callbacks.items():
            getattr(obj, callback_name)()
    
