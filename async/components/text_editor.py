#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Int, Str, Property, Instance

from .control import Control

from ..core.trait_types import EnamlEvent


class TextEditor(Control):
    """ A text editor widget capable of editing plain text with styles.
    
    This is not a general text edit widget with general capabilties for 
    sophistcated formatting or image display.
    
    """
    #: Whether or not the editor is read only.
    read_only = Bool(False)
    
    #: Whether to wrap text in the editor or not. If True, keep words
    #: together if possible.
    wrap_lines = Bool(True)
    
    #: Whether to overwrite or insert text when the user types.
    overwrite = Bool(False)
    
    #: The position of the cursor in the editor.
    cursor_position = Int

    #: The anchor of the selection in the editor.
    anchor_position = Int

    #: A read only property holding the line number of cursor in the
    #: editor.
    cursor_line = Property(Int, depends_on='_cursor_line')

    #: A read only property holding the column number of cursor in the
    #: editor.
    cursor_column = Property(Int, depends_on='_cursor_column')

    #: A read only property that is set to True if the user has changed
    #: the line edit from the ui, False otherwise. This is reset to
    #: False if the text is programmatically changed.
    modified = Property(Bool, depends_on='_modified')

    #: A read only property that is updated with the text selected
    #: in the editor.
    selected_text = Property(Str, depends_on='_selected_text')

    #: Fired when the text is changed programmatically, or by the user
    #: via the ui. The event does not carry a payload. To retrieve the
    #: current text, use the `get_text()` method.
    text_changed = EnamlEvent

    #: Fired when the text is changed by the user explicitly through
    #: the ui and not programmatically. The event does not carry a 
    #: payload. To retrieve the current text, call `get_text()`.
    text_edited = EnamlEvent

    #: Fired when the widget has lost input focus.
    lost_focus = EnamlEvent

    #: How strongly a component hugs it's contents' width. TextEditors 
    #: ignore the width hug by default, so they expand freely in width.
    hug_width = 'ignore'
    
    #: How strongly a component hugs it's contents' height. TextEditors 
    #: ignore the height hug by default, so they expand freely in height.
    hug_height = 'ignore'

    #: An internal attribute that is used by the implementation object
    #: to update the value of 'cursor_line'.
    _cursor_line = Int

    #: An internal attribute that is used by the implementation object
    #: to update the value of 'cursor_column'.
    _cursor_column = Int

    #: An internal attribute that is used by the implementation object
    #: to update the value of 'modified'.
    _modified = Bool(False)

    #: An internal attribute that is used by the implementation object
    #: to update the value of 'selected_text'.
    _selected_text = Str

    #--------------------------------------------------------------------------
    # Toolkit Communication
    #--------------------------------------------------------------------------
    @on_trait_change('anchor_position,cursor_position,overwrite,read_only,'
                     'text,wrap_lines')
    def sync_object_state(self, name, new):
        """ Notify the client component of updates to the object state.

        """
        msg = 'set_' + name
        self.send(msg, {'value': new})

    def initial_attrs(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(Control, self).initial_attrs()
        attrs = {
            'anchor_position' : self.anchor_position,
            'cursor_position' : self.cursor_position,
            'overwrite' : self.overwrite,
            'read_only' : self.read_only
            'text' : self.text,
            'wrap_lines' : self.wrap_lines
            }
        super_attrs.update(attrs)
        return super_attrs

    def receive_lost_focus(self, context):
        """ Callback from the UI when focus is lost.

        """
        self.lost_focus()

    def receive_text_changed(self, context):
        """ Callback from UI when the text changes.

        """
        self.text_changed()

    def receive_text_edited(self, context):
        """ Callback from the UI when the text is edited

        """
        self.text_edited()

    #--------------------------------------------------------------------------
    # Property methods 
    #--------------------------------------------------------------------------
    def _get_cursor_column(self):
        """ The property getter for the 'cursor_column' attribute.

        """
        return self._cursor_column

    def _get_cursor_line(self):
        """ The property getter for the 'cursor_line' attribute.

        """
        return self._cursor_line

    def _get_modified(self):
        """ The property getter for the 'modified' attribute.

        """
        return self._modified

    def _get_selected_text(self):
        """ The property getter for the 'selected' attribute.

        """
        return self._selected_text
    
