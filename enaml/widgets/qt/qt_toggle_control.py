from traits.api import implements

from .qt_control import QtControl

from ..toggle_control import IToggleControlImpl


class QtToggleControl(QtControl):
    """ A base class for PySide toggle widgets.

    This class can serve as a base class for widgets that implement
    toggle behavior such as CheckBox and RadioButton. It is not meant
    to be used directly. Subclasses should implement the 'create_widget'
    method.

    See Also
    --------
    IToggleElement

    """
    implements(IToggleControlImpl)

    #---------------------------------------------------------------------------
    # IToggleControlImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying Qt widget.
        
        """
        
    def initialize_widget(self):
        """ Initializes the attributes of the Qt component.

        """
        
    
