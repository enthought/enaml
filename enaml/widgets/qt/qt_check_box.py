from .qt import QtGui

from traits.api import implements

from .qt_toggle_control import QtToggleControl

from ..check_box import ICheckBoxImpl


class QtCheckBox(QtToggleControl):
    """ A PySide implementation of CheckBox.

    See Also
    --------
    CheckBox

    """
    implements(ICheckBoxImpl)

    #---------------------------------------------------------------------------
    # ICheckBoxImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying QCheckBox widget.

        """
        self.widget = QtGui.QCheckBox(self.parent_widget())
        
    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def bind(self):
        """ Binds the event handlers for the check box. Not meant for
        public consumption.

        """
        widget = self.widget
        widget.toggled.connect(self.on_toggled)
        widget.pressed.connect(self.on_pressed)
        widget.released.connect(self.on_released)
        
