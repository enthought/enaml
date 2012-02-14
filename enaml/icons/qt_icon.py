#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from enaml.icons.abstract_icon import AbstractIcon
from enaml.widgets.qt.qt import QtGui

class QtIcon(object, AbstractIcon):
    """ Collection of images for display in a component
    
    The Icon class allows the user to specify different images for different
    states of the icon, so that a widget can select the image which is most
    appropriate for display in the widget.
    """
    def __init__(self, image=None):
        self._qicon = QtGui.QIcon(
    
    @abstractmethod
    def get_image(self, size=(None, None), mode='normal', state='on'):
        """ Get an appropriate image instance for the requested size, mode and state
        """
        raise NotImplemented
    
    @abstractmethod
    def set_image(self, image, mode='normal', state='on'):
        """ Set the appropriate image instance for the requested size, mode and state
        """
        raise NotImplemented

    @abstractmethod
    def available_sizes(self, mode='normal', state='on'):
        """ Return the available image sizes for the given mode and state
        """
        raise NotImplemented
