#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Bool, Event, Int, Str, Enum, Property, Instance, Any

from .control import Control, AbstractTkControl


class AbstractTkPlainTextEdit(AbstractTkControl):
    """ A text editor widget capable of editing plain text with styles.
    
    This is not a general text edit widget with general capabilties for sophistcated
    formatting or image display.
    """
    
    @abstractmethod
    def shell_text_changed(self, value):
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
    
    #@abstractmethod
    #def find(self):
    #    raise NotImplementedError

class PlainTextEdit(Control):
    """
    """
    #: Whether or not the editor is read only.
    read_only = Bool
    
    #: The position of the cursor in the field.
    cursor_position = Int

    #: A read only property that is set to True if the user has changed
    #: the line edit from the ui, False otherwise. This is reset to
    #: False if the text is programmatically changed.
    modified = Property(Bool, depends_on='_modified')

    #: The Python value to display in the field.
    text = Str

    #: A read only property that is updated with the text selected
    #: in the field.
    selected_text = Property(Str, depends_on='_selected_text')

    #: Fired when the text is changed programmatically, or by the
    #: user via the ui. The args object will contain the text.
    text_changed = Event

    #: Fired when the text is changed by the user explicitly through
    #: the ui and not programmatically. The args object will contain
    #: the text.
    text_edited = Event
    
    #: Whether to wrap text in the editor, and if so where to break lines
    line_wrap_mode = Enum('none', 'character', 'word')
    
    #: How strongly a component hugs it's contents' width.
    #: Fields ignore the width hug by default, so they expand freely in width.
    hug_width = 'ignore'
    
    #: How strongly a component hugs it's contents' height.
    #: PlainTextEdits ignore the height hug by default, so they expand freely
    #: in height.
    hug_height = 'ignore'

    #: An internal attribute that is used by the implementation object
    #: to update the value of 'modified'.
    _modified = Bool(False)

    #: An internal attribute that is used by the implementation object
    #: to update the value of 'selected_text'.
    _selected_text = Str

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkPlainTextEdit)

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
    
    
