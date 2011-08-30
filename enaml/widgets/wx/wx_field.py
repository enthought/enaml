import wx

from traits.api import implements, Bool, Instance, Callable, Any

from .wx_line_edit import WXLineEdit

from ..i_field import IField


class WXField(WXLineEdit):
    """ A wxPython implementation of IField.

    WXField is a subclass of WXLineEdit.

    See Also
    --------
    IField

    """
    implements(IField)

    #===========================================================================
    # IField interface
    #===========================================================================
    error = Bool

    exception = Instance(Exception)

    from_string = Callable
    
    to_string = Callable
      
    value = Any

    #---------------------------------------------------------------------------
    # Initialization
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying wxPython widget.

        This is called by the 'layout' method and is not meant for
        public consumption.

        """
        super(WXField, self).create_widget()
        self.try_set(self.text)

    def init_attributes(self):
        """ Intializes the widget with the attributes of this instance.

        This is called by the 'layout' method and is not meant for
        public consumption.

        """
        super(WXField, self).init_attributes()

    def init_meta_handlers(self):
        """ Initializes any meta handlers for this widget.

        This is called by the 'layout' method and is not meant for
        public consumption.

        """
        pass

    #---------------------------------------------------------------------------
    # Notification
    #---------------------------------------------------------------------------
    def _value_changed(self, value):
        """ The change handler for the 'text' attribute. Not meant for
        public consumption.

        """
        self.try_set(value)

    def _text_changed(self, text):
        super(WXField, self)._text_changed()
        try:
            new_value = self.from_string(text)
        except Exception as e:
            self.exception = e
            self.error = True
        else:
            self.exception = None
            self.error = False
            self.value = new_value

    def try_set(self, value):
        try:
            new_value = self.to_string(value)
        except Exception as e:
            self.exception = e
            self.error = True
        else:
            self.exception = None
            self.error = False
            self.text = new_value