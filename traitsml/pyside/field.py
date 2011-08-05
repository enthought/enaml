from enthought.traits.api import DelegatesTo, Instance

from PySide import QtGui

from .line_edit import LineEdit


class Field(LineEdit):
    """ Field is a subclass of LineEdit and handles the coversion
    between value <-> text using the to_string and from_string
    callables provided. The work of updating the editor and
    what not is delegated to the LineEdit through the text trait.

    """
    # Whether or not the from_string callabled raised an
    # exception during conversion. - Bool
    error = DelegatesTo('abstract_obj')

    # The callable to be called to convert the string in the 
    # the text box to the proper python value - Callable
    from_string = DelegatesTo('abstract_obj')
    
    # The callable to be called to convert the python value
    # to a string for display - Callable
    to_string = DelegatesTo('abstract_obj')
        
    # The value to display in the field - Any
    value = DelegatesTo('abstract_obj')

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def init_attributes(self):
        super(Field, self).init_attributes()
        # The order of these calls is important. The text in the 
        # widget must be inited before we check if it's valid.
        self.init_value()
        self.init_error()

    def init_value(self):
        val = self.value
        str_val = self.to_string(val)
        self.text = str_val

    def init_error(self):
        txt = self.text
        try:
            value = self.from_string(txt)
        except (TypeError, ValueError):
            self.error = True
            return
        self.error = False

    #--------------------------------------------------------------------------
    # Change handlers
    #--------------------------------------------------------------------------
    def _value_changed(self):
        py_val = self.value
        str_val = self.to_string(py_val)
        self.text = str_val
    
    def _text_changed(self):
        # XXX - do we really want the text typed in the field
        # to follow text -> from_string -> to_string -> text ?
        super(Field, self)._text_changed() 
        
        # We need to convert the text value to the user
        # value via the provided from_string callable. Since 
        # this sets the value, the value handler is called which
        # will then set the text. So the to_string and from_string
        # need to round-trip for things to function properly.
        try:
            value = self.from_string(self.text)
        except (TypeError, ValueError) as e:
            self.error = True
            return
        self.value = value
        self.error = False


