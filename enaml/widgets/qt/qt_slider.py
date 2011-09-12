from PySide import QtGui

from traits.api import implements

from .qt_control import QtControl

from ..slider import ISliderImpl

from ...enums import Orientation, TickPosition


class QtSlider(QtControl):
    """ A PySide implementation of Slider.

    See Also
    --------
    Slider

    """
    implements(ISliderImpl)

	#---------------------------------------------------------------------------
    # ISliderImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying Qt widget.
        
        """
        
    def initialize_widget(self):
        """ Initializes the attributes of the Qt component.

        """
        
    
