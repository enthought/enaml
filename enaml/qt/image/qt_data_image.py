#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_abstract_image import QtAbstractImage        

class QtDataImage(QtAbstractImage):
    """ A Qt4 implementation of an Enaml DataImage.
    
    """
    _data = None
    
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, tree):
        """ Initializes the data for the image.

        """
        super(QtDataImage, self).create(tree)
        self.set_data(self._pipe.decode_binary(tree['data']))
    
    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_data(self, content):
        """ Handle the 'set_data' action from the Enaml widget

        """
        self.set_data(self._pipe.decode_binary(content['data']))
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_data(self, data):
        """ Set the data on the QPixmap
        
        """
        print data[:10]
        self.widget().loadFromData(data)
        self.refresh()
        self._data = data
        
