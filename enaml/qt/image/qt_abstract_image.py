#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from ..qt_object import QtObject
from ..qt.QtGui import QPixmap

class QtAbstractImage(QtObject):
    """ Base class for Qt4 implementation of Image subclasses
    
    This class is not meant to be instantiated.
    
    """
    
    def create(self, tree):
        """ Create the QPixmap
        
        Subclasses should use the snapshot to create other attributes and
        populate the QPixmap.
        
        """
        self.widget = QPixmap()


    
