from enthought.traits.api import Bool, DelegatesTo

from PySide import QtCore, QtGui

from ..constants import Align
from .element import Element
from .mixins import GeneralWidgetMixin


class LineEditWidget(GeneralWidgetMixin, QtGui.QLineEdit):
    pass


class LineEdit(Element):

    # The alignment of the text
    alignment = DelegatesTo('abstract_obj')
    
    # The maximum length of the line edit, in characters - Int
    max_length = DelegatesTo('abstract_obj')

    # Whether the line edit is read_only - Bool
    read_only = DelegatesTo('abstract_obj')

    # The text for the line edit - Str
    text = DelegatesTo('abstract_obj')
    
    # The Event emitted when the text is changed
    text_changed = DelegatesTo('abstract_obj')

    # The Event emitted when the text is edited (not programatically changed)
    text_edited = DelegatesTo('abstract_obj')

    #--------------------------------------------------------------------------
    # Creation Handler
    #--------------------------------------------------------------------------
    def create_widget(self):
        return LineEditWidget()
    
    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def init_widget(self):
        super(LineEdit, self).init_widget()
        widget = self.widget
        widget.textChanged.connect(self._on_text_changed)
        widget.textEdited.connect(self._on_text_edited)

    def init_attributes(self):
        super(LineEdit, self).init_attributes()
        self.init_bgcolor()
        self.init_max_length()
        self.init_read_only()
        self.init_text()
       
    def init_max_length(self):
        max_length = self.max_length
        if max_length != -1:
            self.widget.setMaxLength(max_length)

    def init_read_only(self):
        self.widget.setReadOnly(self.read_only)

    def init_text(self):
        self.widget.setText(self.text)

    #--------------------------------------------------------------------------
    # Changed Handlers
    #--------------------------------------------------------------------------
    def _alignment_changed(self):
        pass

    def _max_length_changed(self):
        self.widget.setMaxLength(self.max_length)

    def _read_only_changed(self):
        self.widget.setReadOnly(self.read_only)

    def _text_changed(self):
        # If the text in the widget and the text field match,
        # we don't need to update the control. This helps
        # break update cycles earlier than what would be caught
        # by the traits notification sytem.
        if self.text == self.widget.text():
            pass
        else:
            # Otherwise, we want to update the line edit without
            # changing the cursor position. 
            cursor_pos = self.widget.cursorPosition()
            self.widget.setText(self.text)
            self.widget.setCursorPosition(cursor_pos)

    #--------------------------------------------------------------------------
    # Slots    
    #--------------------------------------------------------------------------
    def _on_text_changed(self):
        # Called when the text is edited by keyboard or set 
        # programatically.
        self.text = self.widget.text()
        self.text_changed = True

    def _on_text_edited(self):
        # Called when the text is edited by keyboard only.
        self.text_edited = True


