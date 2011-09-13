from traits.api import Bool, Event, Int, Str, Property, Instance

from .control import IControlImpl, Control


class ILineEditImpl(IControlImpl):

    def parent_max_length_changed(self, max_length):
        raise NotImplementedError
    
    def parent_read_only_changed(self, read_only):
        raise NotImplementedError
    
    def parent_cursor_position_changed(self, cursor_position):
        raise NotImplementedError
    
    def parent_placeholder_text_changed(self, placeholder_text):
        raise NotImplementedError
    
    def parent_text_changed(self, text):
        raise NotImplementedError
    
    def set_selection(self, start, end):
        raise NotImplementedError

    def select_all(self):
        raise NotImplementedError

    def deselect(self):
        raise NotImplementedError
    
    def clear(self):
        raise NotImplementedError

    def backspace(self):
        raise NotImplementedError
    
    def delete(self):
        raise NotImplementedError

    def end(self, mark=False):
        raise NotImplementedError
    
    def home(self, mark=False):
        raise NotImplementedError
    
    def cut(self):
        raise NotImplementedError
    
    def copy(self):
        raise NotImplementedError

    def paste(self):
        raise NotImplementedError
    
    def insert(self, text):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError
    
    def redo(self):
        raise NotImplementedError


class LineEdit(Control):
    """ A single-line editable text widget.

    Attributes
    ----------
    max_length : Int
        The maximum length of the line edit in characters.
    
    max_length_reached : Event
        An event fired when the max length has been reached.

    read_only : Bool
        Whether or not the line edit is read only.

    cursor_position : Int
        The position of the cursor in the line edit.

    modified : Property(Bool)
        A read only property that is set to True if the user has changed
        the line edit from the ui, False otherwise. This is reset to 
        False if the text is programmatically changed.

    placeholder_text : Str
        The grayed-out text to display if 'text' is empty and the
        widget doesn't have focus.

    text : Str
        The string to use in the line edit.

    selected_text : Property(Str)
        A read only property that is updated with the text selected 
        in the line edit.

    text_changed : Event
        Fired when the text is changed programmatically, or by the
        user via the ui. The args object will contain the text.

    text_edited : Event
        Fired when the text is changed by the user explicitly through
        the ui and not programmatically. The args object will contain
        the text.

    return_pressed : Event
        Fired when the return/enter key is pressed in the line edit.
    
    _modified : Bool
        A protected attribute that is used by the implementation object
        to update the value of modified.
    
    _selected_text : Str
        A protected attribute that is used by the implementation object
        to update the value of selected_text.

    Methods
    -------
    set_selection(start, end)
        Sets the selection to the bounds of start and end.

    select_all()
        Select all the text in the line edit.

    deselect()
        Deselect any selected text.

    clear()
        Clear the line edit of all text.

    backspace()
        If no text is selected, deletes the character to the left
        of the cursor. Otherwise, it deletes the selected text.

    delete()
        If no text is selected, deletes the character to the right
        of the cursor. Otherwise, it deletes the selected text.

    end(mark=False)
        Moves the cursor to the end of the line. If 'mark' is True,
        also selects the text from the current position to the end.

    home(mark=False)
        Moves the cursor to the beginning of the line. If 'mark'
        is True, also selects the text from the current position
        to the beginning.

    cut()
        Copies the selected text to the clipboard, then deletes
        the selected text from the line edit.

    copy()
        Copies the selected text to the clipboard.

    paste()
        Inserts the contents of the clipboard into the line edit,
        replacing any selected text.

    insert(text)
        Inserts the given text at the current cursor position,
        replacing any selected text.

    undo()
        Undoes the last operation.

    redo()
        Redoes the last operation.

    """
    max_length = Int

    max_length_reached = Event

    read_only = Bool

    cursor_position = Int

    modified = Property(Bool, depends_on='_modified')

    placeholder_text = Str

    text = Str

    selected_text = Property(Str, depends_on='_selected_text')

    text_changed = Event

    text_edited = Event

    return_pressed = Event

    _modified = Bool(False)

    _selected_text = Str

    #---------------------------------------------------------------------------
    # Overridden parent class traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(ILineEditImpl)
    
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

        Returns
        -------
        result : None

        """
        self.toolkit_impl.set_selection(start, end)

    def select_all(self):
        """ Select all the text in the line edit.

        If there is no text in the line edit, the selection will be
        empty.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        self.toolkit_impl.select_all()

    def deselect(self):
        """ Deselect any selected text.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        self.toolkit_impl.deselect()
    
    def clear(self):
        """ Clear the line edit of all text.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        self.toolkit_impl.clear()

    def backspace(self):
        """ Simple backspace functionality.

        If no text is selected, deletes the character to the left
        of the cursor. Otherwise, it deletes the selected text.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        self.toolkit_impl.backspace()
    
    def delete(self):
        """ Simple delete functionality.

        If no text is selected, deletes the character to the right
        of the cursor. Otherwise, it deletes the selected text.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        self.toolkit_impl.delete()

    def end(self, mark=False):
        """ Moves the cursor to the end of the line.

        Arguments
        ---------
        mark : bool, optional
            If True, select the text from the current position to
            the end of the line edit. Defaults to False.

        Returns
        -------
        results : None

        """
        self.toolkit_impl.end(mark=mark)
    
    def home(self, mark=False):
        """ Moves the cursor to the beginning of the line.

        Arguments
        ---------
        mark : bool, optional
            If True, select the text from the current position to
            the beginning of the line edit. Defaults to False.

        Returns
        -------
        results : None

        """
        self.toolkit_impl.home(mark=mark)
    
    def cut(self):
        """ Cuts the selected text from the line edit.

        Copies the selected text to the clipthen deletes the selected
        text from the line edit.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        self.toolkit_impl.cut()
    
    def copy(self):
        """ Copies the selected text to the clipboard.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        self.toolkit_impl.copy()

    def paste(self):
        """ Paste the contents of the clipboard into the line edit.

        Inserts the contents of the clipboard into the line edit at
        the current cursor position, replacing any selected text.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        self.toolkit_impl.paste()
    
    def insert(self, text):
        """ Insert the text into the line edit.

        Inserts the given text at the current cursor position,
        replacing any selected text.

        Arguments
        ---------
        text : str
            The text to insert into the line edit.

        Returns
        -------
        result : None

        """
        self.toolkit_impl.insert(text)

    def undo(self):
        """ Undoes the last operation.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        self.toolkit_impl.undo()
    
    def redo(self):
        """ Redoes the last operation.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        """
        self.toolkit_impl.redo()

    def _get_modified(self):
        """ The property getter for the 'modified' attribute.

        """
        return self._modified
    
    def _get_selected_text(self):
        """ The property getter for the 'selected' attribute.

        """
        return self._selected_text


LineEdit.protect('max_length_reached', 'modified', 'selected_text', 
                 'text_changed', 'text_edited', 'return_pressed',
                 '_modified', '_selected_text')

