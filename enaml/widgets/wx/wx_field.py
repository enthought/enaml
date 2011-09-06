import wx

from traits.api import implements

from .wx_line_edit import WXLineEdit

from ..field import IFieldImpl


class WXField(WXLineEdit):
    """ A wxPython implementation of IField.

    WXField is a subclass of WXLineEdit.

    See Also
    --------
    IField

    """
    implements(IFieldImpl)

    #---------------------------------------------------------------------------
    # IFieldImpl interface
    #---------------------------------------------------------------------------
    def initialize_widget(self):
        super(WXField, self).initialize_widget()
        self.sync_text()

    def parent_from_string_changed(self, from_string):
        self.sync_value()
    
    def parent_to_string_changed(self, to_string):
        self.sync_text()
    
    def parent_value_changed(self, value):
        self.sync_text()
    
    def parent_text_changed(self, text):
        super(WXField, self).parent_text_changed(text)
        self.sync_value()

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def sync_value(self):
        parent = self.parent
        text = parent.text
        from_string = parent.from_string
        try:
            value = from_string(text)
        except Exception as e:
            parent._exception = e
            parent._error = True
        else:
            parent._exception = None
            parent._error = False
            parent.value = value
    
    def sync_text(self):
        parent = self.parent
        value = parent.value
        to_string = parent.to_string
        try:
            text = to_string(value)
        except Exception as e:
            parent._exception = e
            parent._error = True
        else:
            parent._exception = None
            parent._error = False
            parent.text = text

