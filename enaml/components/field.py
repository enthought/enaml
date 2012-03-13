#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Bool, Int, Str, Enum, Property, Instance, Any

from .control import Control, AbstractTkControl

from ..converters import Converter, StringConverter
from ..core.trait_types import EnamlEvent


class AbstractTkField(AbstractTkControl):

    @abstractmethod
    def shell_max_length_changed(self, max_length):
        raise NotImplementedError

    @abstractmethod
    def shell_read_only_changed(self, read_only):
        raise NotImplementedError

    @abstractmethod
    def shell_cursor_position_changed(self, cursor_position):
        raise NotImplementedError

    @abstractmethod
    def shell_placeholder_text_changed(self, placeholder_text):
        raise NotImplementedError

    @abstractmethod
    def shell_field_text_changed(self, value):
        raise NotImplementedError

    @abstractmethod
    def shell_password_mode_changed(self, mode):
        raise NotImplementedError

    @abstractmethod
    def set_selection(self, start, end):
        raise NotImplementedError

    @abstractmethod
    def select_all(self):
        raise NotImplementedError

    @abstractmethod
    def deselect(self):
        raise NotImplementedError

    @abstractmethod
    def clear(self):
        raise NotImplementedError

    @abstractmethod
    def backspace(self):
        raise NotImplementedError

    @abstractmethod
    def delete(self):
        raise NotImplementedError

    @abstractmethod
    def end(self, mark=False):
        raise NotImplementedError

    @abstractmethod
    def home(self, mark=False):
        raise NotImplementedError

    @abstractmethod
    def cut(self):
        raise NotImplementedError

    @abstractmethod
    def copy(self):
        raise NotImplementedError

    @abstractmethod
    def paste(self):
        raise NotImplementedError

    @abstractmethod
    def insert(self, text):
        raise NotImplementedError

    @abstractmethod
    def undo(self):
        raise NotImplementedError

    @abstractmethod
    def redo(self):
        raise NotImplementedError


class Field(Control):
    """ A single-line editable text widget.

    Among many other attributes, a Field accepts a converter object
    which allows any arbitrary python object to be displayed and edited
    by the Field.

    """
    #: The maximum length of the field in characters. The default value
    #: is Zero and indicates there is no maximum length.
    max_length = Int

    #: Whether or not the field is read only. Defaults to False.
    read_only = Bool

    #: The position of the cursor in the field. Defaults to Zero.
    cursor_position = Int

    #: A read only property that is set to True if the user has changed
    #: the line edit from the ui, False otherwise. This is reset to
    #: False if the text is programmatically changed.
    modified = Property(Bool, depends_on='_modified')

    #: The grayed-out text to display if 'value' is empty and the
    #: widget doesn't have focus. Defaults to the empty string.
    placeholder_text = Str
    
    #: How to obscure password text in the field.
    password_mode = Enum('normal', 'password', 'silent')

    #: A converter object for converting values to and from the component
    #: The default is basic str(...) conversion.
    converter = Instance(Converter, factory=StringConverter)

    #: The Python value to display in the field. The default value
    #: is an empty string.
    value = Any('')

    #: A read-only property that returns the internal text of the field.
    text = Property(depends_on='_text')

    #: Private internal storage for the 'text' attribute.
    _text = Str

    #: A property which manages the conversion to and from :attr:`value`
    #: and the string for display and editing. Toolkit implementations
    #: should use this attribute for getting/setting the value.
    field_text = Property(depends_on=['value', 'converter'])

    #: A read only property that is updated with the text selected
    #: in the field.
    selected_text = Property(Str, depends_on='_selected_text')

    #: Fired when the text is changed by the user explicitly through
    #: the ui but not programmatically. The event object will contain
    #: the text.
    text_edited = EnamlEvent

    #: Fired when the return/enter key is pressed in the line edit.
    return_pressed = EnamlEvent
    
    #: How strongly a component hugs it's contents' width.
    #: Fields ignore the width hug by default, so they expand freely in width.
    hug_width = 'ignore'

    #: An internal attribute that is used by the implementation object
    #: to update the value of 'modified'.
    _modified = Bool(False)

    #: An internal attribute that is used by the implementation object
    #: to update the value of 'selected_text'.
    _selected_text = Str

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkField)

    def set_selection(self, start, end):
        """ Sets the selection to the bounds of start and end.

        If the indices are invalid, no selection will be made,
        and any current selection will be cleared.

        Arguments
        ---------
        start : Int
            The start selection index, zero based.

        end : Int
            The end selection index, zero based.

        """
        self.abstract_obj.set_selection(start, end)

    def select_all(self):
        """ Select all the text in the line edit.

        If there is no text in the line edit, the selection will be
        empty.

        """
        self.abstract_obj.select_all()

    def deselect(self):
        """ Deselect any selected text.

        """
        self.abstract_obj.deselect()

    def clear(self):
        """ Clear the line edit of all text.

        """
        self.abstract_obj.clear()

    def backspace(self):
        """ Simple backspace functionality.

        If no text is selected, deletes the character to the left
        of the cursor. Otherwise, it deletes the selected text.

        """
        self.abstract_obj.backspace()

    def delete(self):
        """ Simple delete functionality.

        If no text is selected, deletes the character to the right
        of the cursor. Otherwise, it deletes the selected text.

        """
        self.abstract_obj.delete()

    def end(self, mark=False):
        """ Moves the cursor to the end of the line.

        Arguments
        ---------
        mark : bool, optional
            If True, select the text from the current position to
            the end of the line edit. Defaults to False.

        """
        self.abstract_obj.end(mark=mark)

    def home(self, mark=False):
        """ Moves the cursor to the beginning of the line.

        Arguments
        ---------
        mark : bool, optional
            If True, select the text from the current position to
            the beginning of the line edit. Defaults to False.

        """
        self.abstract_obj.home(mark=mark)

    def cut(self):
        """ Cuts the selected text from the line edit.

        Copies the selected text to the clipthen deletes the selected
        text from the line edit.

        """
        self.abstract_obj.cut()

    def copy(self):
        """ Copies the selected text to the clipboard.

        """
        self.abstract_obj.copy()

    def paste(self):
        """ Paste the contents of the clipboard into the line edit.

        Inserts the contents of the clipboard into the line edit at
        the current cursor position, replacing any selected text.

        """
        self.abstract_obj.paste()

    def insert(self, text):
        """ Insert the text into the line edit.

        Inserts the given text at the current cursor position,
        replacing any selected text.

        Arguments
        ---------
        text : str
            The text to insert into the line edit.

        """
        self.abstract_obj.insert(text)

    def undo(self):
        """ Undoes the last operation.

        """
        self.abstract_obj.undo()

    def redo(self):
        """ Redoes the last operation.

        """
        self.abstract_obj.redo()

    #--------------------------------------------------------------------------
    # Property methods 
    #--------------------------------------------------------------------------
    def _get_modified(self):
        """ The property getter for the 'modified' attribute.

        """
        return self._modified

    def _get_selected_text(self):
        """ The property getter for the 'selected' attribute.

        """
        return self._selected_text

    def _get_text(self):
        """ The property getter for the 'text' attribute.

        """
        return self._text

    def _get_field_text(self):
        """ The property getter for :attr:`field_text`. It uses an 
        appropriate exception guard to manage the error state if
        the conversion from value to text fails. If there is an
        error during conversion, this will return None and toolkit
        implementations should not perform an update.

        """
        # Disable the context temporarily since it captures all
        # exceptions, including Trait errors that we may want to 
        # bubble up during initialization.
        #with self.capture_exceptions():
        try:
            res = self.converter.to_component(self.value)
        except (ValueError, TypeError) as e:
            self.exception = e
            self.error = True
            return
        else:
            self.exception = None
            self.error = False
        return res
        
    def _set_field_text(self, text):
        """ The property setter for :attr:`field_text`. It uses an
        appropriate exception guard to manage the error state if
        the conversion from string to value fails.

        """
        self._text = text
        # Disable the context temporarily since it captures all
        # exceptions, including Trait errors that we may want to 
        # bubble up during initialization.
        #with self.capture_notification_exceptions():
        try:
            self.value = self.converter.from_component(text)
        except (ValueError, TypeError) as e:
            self.exception = e
            self.error = True
            return
        else:
            self.exception = None
            self.error = False

