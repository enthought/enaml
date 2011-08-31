from traits.api import Bool, Event, Int, Str, Property

from .i_element import IElement


class ILineEdit(IElement):
    """ A single-line editable text widget.

    Attributes
    ----------
    max_length : Int
        The maximum length of the line edit in characters.

    read_only : Bool
        Whether or not the line edit is read only.

    cursor_position : Int
        The position of the cursor in the line edit.

    modified : Bool
        True if the user has modified the line edit from the ui,
        False otherwise. This is reset to False if the text is
        programmatically changed.

    placeholder_text : Str
        The grayed-out text to display if 'text' is empty and the
        widget doesn't have focus.

    text : Str
        The string to use in the line edit.

    selected_text : Property(Str)
        The text selected in the line edit. This is a read only property
        that is updated whenever the selection changes.

    text_changed : Event
        Fired when the text is changed programmatically, or by the
        user via the ui. The args object will contain the text.

    text_edited : Event
        Fired when the text is changed by the user explicitly through
        the ui and not programmatically. The args object will contain
        the text.

    return_pressed : Event
        Fired when the return/enter key is pressed in the line edit.

    length_invalid : Event
        Fired when the user attempts through the ui to violate maximum number
        of characters in the line edit.


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

    read_only = Bool

    cursor_position = Int

    modified = Bool

    placeholder_text = Str

    text = Str

    selected_text = Property(Str)

    text_changed = Event

    text_edited = Event

    return_pressed = Event

    max_length = Event

    length_invalid = Event

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

        Raises
        ------
        None

        """
        raise NotImplementedError

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

        Raises
        ------
        None

        """
        raise NotImplementedError

    def deselect(self):
        """ Deselect any selected text.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        Raises
        ------
        None

        """
        raise NotImplementedError

    def clear(self):
        """ Clear the line edit of all text.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        Raises
        ------
        None

        """
        raise NotImplementedError

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

        Raises
        ------
        None

        """
        raise NotImplementedError

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

        Raises
        ------
        None

        """
        raise NotImplementedError

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

        Raises
        ------
        None

        """
        raise NotImplementedError

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

        Raises
        ------
        None

        """
        raise NotImplementedError

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

        Raises
        ------
        None

        """
        raise NotImplementedError

    def copy(self):
        """ Copies the selected text to the clipboard.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        Raises
        ------
        None

        """
        raise NotImplementedError

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

        Raises
        ------
        None

        """
        raise NotImplementedError

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

        Raises
        ------
        None

        """
        raise NotImplementedError

    def undo(self):
        """ Undoes the last operation.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        Raises
        ------
        None

        """
        raise NotImplementedError

    def redo(self):
        """ Redoes the last operation.

        Arguments
        ---------
        None

        Returns
        -------
        result : None

        Raises
        ------
        None

        """
        raise NotImplementedError

