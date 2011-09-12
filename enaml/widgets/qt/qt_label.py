from .qt_api import QtGui

from traits.api import implements

from .qt_control import QtControl

from ..label import ILabelImpl


class QtLabel(QtControl):
    """ A Qt implementation of Label.

    A QtLabel displays static text using a QLabel control.

    See Also
    --------
    Label

    """
    implements(ILabelImpl)

    #---------------------------------------------------------------------------
    # ILabelImpl interface 
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying text control.

        """
        self.widget = QtGui.QLabel(self.parent_widget())

    def initialize_widget(self):
        """ Initializes the attributes on the underlying control.

        """
        self.set_label(self.parent.text)

    def parent_text_changed(self, text):
        """ The change handler for the 'text' attribute. Not meant for
        public consumption.

        """
        self.set_label(text)

    #---------------------------------------------------------------------------
    # Widget update
    #---------------------------------------------------------------------------
    def set_label(self, label):
        """ Sets the label on the underlying control. Not meant for
        public consumption.

        """
        self.widget.setText(label)

