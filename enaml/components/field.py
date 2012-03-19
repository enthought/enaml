#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import (
    Bool, Int, Unicode, Enum, Instance, Any, List, on_trait_change,
)

from .control import Control, AbstractTkControl

from ..core.trait_types import EnamlEvent
from ..guard import guard
from ..validation import AbstractValidator, CoercingValidator


class AbstractTkField(AbstractTkControl):
    """ The abstract toolkit interface for a Field.

    Toolkit implementations of Field are slighly more complicated than
    other controls, given the flexibility required for validation and
    conversion.

    The major deviation from other toolkit controls is that the shell
    object is responsible for updating the toolkit field by calling
    the get_text/set_text methods, as opposed to having the toolkit
    object rely on change notification from the shell. The reason this
    is done this way is so that the majority of the conversion and
    validation logic can be managed by the shell, instead of repeating
    the same logic in every backend. 

    In order for the toolkit object to communicate successfully with
    the shell object, it must call three methods at various points
    in time:
        
        _field_text_edited
            This should be called when the user has edited the text in
            the UI, and that text has validated as either ACCEPTABLE
            or INTERMEDIATE using the shell's validator object. Text
            which validates as INVALID should be rejected. i.e. the
            text should not be allowed to be entered into the field.
            This means that validation must be performed before the
            new text is actually drawn on the screen.
        
        _field_return_pressed
            This should be called when the user presses the return key
            while the field has focus, but only if the text in the
            field validates as ACCEPTABLE. If return is pressed while
            the text is INTERMEDIATE, the 'normalize' method of the 
            shell's validator should be invoked and if the returned
            text validates as ACCEPTABLE, the new text should be used
            and this method called. If the 'normalize' method returns
            INVALID or INTERMEDIATE text, that text should be ignored
            and this method should not be called.
        
        _field_lost_focus
            This method should be called when the field loses focus.
            If the text in the field does not validate as ACCEPTABLE,
            then the 'normalize' method on the shell's validator should
            be invoked. If the returned text validates as ACCEPTABLE,
            it should be substituted. Otherwise, it should be ignored.
            In any cases, this method should always be called when the
            field loses focus.
    
    The shell object provides a 'validator' object with two methods which
    should be used by the toolkit implementation:
        
        validate
            This method accepts the text in the field and returns one
            of three results:
                
                validator.ACCEPTABLE
                    The text is acceptable input for the field.
                
                validator.INTERMEDIATE
                    The text can be made acceptable by the addition of
                    more characters.
                
                validator.INVALID
                    The text is clearly not valid and adding more 
                    characters cannot make it valid.
            
            When the user attempts to input a string which validates as
            INVALID, this input should be silently rejected before the 
            new characters are even drawn to the screen.
        
        normalize
            This method accepts the text in the field and returns a
            new string, which may or may not be different. This method
            allows the programmer a chance to fixup the user's input
            into a potentially acceptable value. The rules for when
            to call this method are described above.

    """
    @abstractmethod
    def get_text(self):
        """ Returns the current unicode text in the field.

        """
        raise NotImplementedError
    
    @abstractmethod
    def set_text(self, text):
        """ Sets the current unicode text in the field.

        """
        raise NotImplementedError
        
    @abstractmethod
    def shell_validator_changed(self, validator):
        """ The change handler for the 'validator' attribute on the 
        shell object.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_max_length_changed(self, max_length):
        """ The change handler for the 'max_length' attribute on the 
        shell object.

        """ 
        raise NotImplementedError

    @abstractmethod
    def shell_read_only_changed(self, read_only):
        """ The change handler for the 'read_only' attribute on the 
        shell object.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_cursor_position_changed(self, cursor_position):
        """ The change handler for the 'cursor_position' attribute on 
        the shell object.

        """
        raise NotImplementedError

    @abstractmethod
    def shell_placeholder_text_changed(self, placeholder_text):
        """ The change handler for the 'placeholder_text' attribute on 
        the shell object.

        """
        raise NotImplementedError
    
    @abstractmethod
    def shell_password_mode_changed(self, mode):
        """ The change handler for the 'password_mode' attribute on the
        shell object.

        """
        raise NotImplementedError

    @abstractmethod
    def set_selection(self, start, end):
        """ Sets the selection to the bounds of start and end.

        If the indices are invalid, no selection will be made, and any
        current selection will be cleared.

        Arguments
        ---------
        start : Int
            The start selection index, zero based.

        end : Int
            The end selection index, zero based.

        """
        raise NotImplementedError

    @abstractmethod
    def select_all(self):
        """ Select all the text in the field.

        If there is no text in the field, the selection will be empty.

        """
        raise NotImplementedError

    @abstractmethod
    def deselect(self):
        """ Deselect any selected text.

        """
        raise NotImplementedError

    @abstractmethod
    def clear(self):
        """ Clear the field of all text.

        """
        raise NotImplementedError

    @abstractmethod
    def backspace(self):
        """ Simple backspace functionality.

        If no text is selected, deletes the character to the left of 
        the cursor. Otherwise, it deletes the selected text.

        """
        raise NotImplementedError

    @abstractmethod
    def delete(self):
        """ Simple delete functionality.

        If no text is selected, deletes the character to the right of 
        the cursor. Otherwise, it deletes the selected text.

        """
        raise NotImplementedError

    @abstractmethod
    def end(self, mark=False):
        """ Moves the cursor to the end of the line.

        Arguments
        ---------
        mark : bool, optional
            If True, select the text from the current position to the 
            end of the field. Defaults to False.

        """
        raise NotImplementedError

    @abstractmethod
    def home(self, mark=False):
        """ Moves the cursor to the beginning of the line.

        Arguments
        ---------
        mark : bool, optional
            If True, select the text from the current position to the 
            beginning of the field. Defaults to False.

        """
        raise NotImplementedError

    @abstractmethod
    def cut(self):
        """ Cuts the selected text from the field.

        Copies the selected text to the clipboard then deletes the 
        selected text from the field.

        """
        raise NotImplementedError

    @abstractmethod
    def copy(self):
        """ Copies the selected text to the clipboard.

        """
        raise NotImplementedError

    @abstractmethod
    def paste(self):
        """ Paste the contents of the clipboard into the field.

        Inserts the contents of the clipboard into the field at the 
        current cursor position, replacing any selected text.

        """
        raise NotImplementedError

    @abstractmethod
    def insert(self, text):
        """ Insert the text into the field.

        Inserts the given text into the field at the current cursor 
        position, replacing any selected text.

        Arguments
        ---------
        text : str
            The text to insert into the field.

        """
        raise NotImplementedError

    @abstractmethod
    def undo(self):
        """ Undoes the last operation.

        """
        raise NotImplementedError

    @abstractmethod
    def redo(self):
        """ Redoes the last operation.

        """
        raise NotImplementedError


class Field(Control):
    """ A single-line editable text widget.

    Among many other attributes, a Field accepts a validator object
    which allows any arbitrary python object to be displayed and edited
    by the Field.

    """
    #: The Python value to display in the field. The default value
    #: is an empty string.
    value = Any(u'')

    #: A validator which manages validation/conversion to and from the
    #: widget's unicode text and the value attribute.
    validator = Instance(AbstractValidator, factory=CoercingValidator)

    #: The maximum length of the field in characters. The default value
    #: is Zero and indicates there is no maximum length.
    max_length = Int

    #: Whether or not the field is read only. Defaults to False.
    read_only = Bool(False)

    #: The position of the cursor in the field. Defaults to Zero.
    cursor_position = Int

    #: The grayed-out text to display if 'value' is empty and the
    #: widget doesn't have focus. Defaults to the empty string.
    placeholder_text = Unicode
    
    #: How to obscure password text in the field.
    password_mode = Enum('normal', 'password', 'silent')

    #: A boolean which is set to True if the user has changed the text
    #: from the ui, False otherwise. This is reset to False if the
    #: value is updated programmatically. This should be considered
    #: read-only and any assignment by the user will be ignored.
    modified = Bool(False)

    #: A unicode attribute that is updated with the text selected in the
    #: field. This should be considered read-only and any assignment by 
    #: the user will be ignored. Use the various selection methods to
    #: programmatically change the selection.
    selected_text = Unicode

    #: A boolean indicating whether or not the text typed by the user 
    #: is acceptable for conversion as indicated by the validator. Note
    #: that this is distinctly different from the 'error' attribute which
    #: indicates an error occured while converting acceptable text to the
    #: Python value. This should be considered read-only and assignment 
    #: by the user will be ignored.
    acceptable = Bool
    def _acceptable_default(self):
        v = self.validator
        return v.validate(v.format(self.value)) == v.ACCEPTABLE

    #: A list of strings which indicates when the text the in the field
    #: should be converted to a Python object representation and stored 
    #: in the 'value' attribute. The default mode triggers submissions 
    #: on lost focus events and return pressed events. Allowable modes 
    #: are 'always', 'lost_focus', and 'return_pressed'. A submission 
    #: can also be manually triggered by calling the 'submit()' method.
    submit_mode = List(
        Enum('lost_focus', 'return_pressed', 'always'),
        value=['lost_focus', 'return_pressed'],
    )

    #: Fired when the text is changed by the user explicitly through
    #: the ui but not programmatically. The event object will contain
    #: the text.
    text_edited = EnamlEvent

    #: Fired when the return/enter key is pressed in the field, provided 
    #: that the text in the field validates as ACCEPTABLE.
    return_pressed = EnamlEvent
    
    #: Fired when the widget has lost input focus.
    lost_focus = EnamlEvent
        
    #: How strongly a component hugs it's contents' width. Fields ignore 
    #: the width hug by default, so they expand freely in width.
    hug_width = 'ignore'

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkField)

    def get_text(self):
        """ Get the current text as a unicode string.

        """
        return self.abstract_obj.get_text()

    def set_text(self, text):
        """ Set the current text without an event notification.

        """
        return self.abstract_obj.set_text(text)

    def set_selection(self, start, end):
        """ Sets the selection to the bounds of start and end.

        If the indices are invalid, no selection will be made, and any
        current selection will be cleared.

        Arguments
        ---------
        start : Int
            The start selection index, zero based.

        end : Int
            The end selection index, zero based.

        """
        self.abstract_obj.set_selection(start, end)

    def select_all(self):
        """ Select all the text in the field.

        If there is no text in the field, the selection will be empty.

        """
        self.abstract_obj.select_all()

    def deselect(self):
        """ Deselect any selected text.

        """
        self.abstract_obj.deselect()

    def clear(self):
        """ Clear the field of all text.

        """
        self.abstract_obj.clear()

    def backspace(self):
        """ Simple backspace functionality.

        If no text is selected, deletes the character to the left of 
        the cursor. Otherwise, it deletes the selected text.

        """
        self.abstract_obj.backspace()

    def delete(self):
        """ Simple delete functionality.

        If no text is selected, deletes the character to the right of
        the cursor. Otherwise, it deletes the selected text.

        """
        self.abstract_obj.delete()

    def end(self, mark=False):
        """ Moves the cursor to the end of the line.

        Arguments
        ---------
        mark : bool, optional
            If True, select the text from the current position to the 
            end of the field. Defaults to False.

        """
        self.abstract_obj.end(mark=mark)

    def home(self, mark=False):
        """ Moves the cursor to the beginning of the line.

        Arguments
        ---------
        mark : bool, optional
            If True, select the text from the current position to the 
            beginning of the field. Defaults to False.

        """
        self.abstract_obj.home(mark=mark)

    def cut(self):
        """ Cuts the selected text from the field.

        Copies the selected text to the clipthen deletes the selected
        text from the field.

        """
        self.abstract_obj.cut()

    def copy(self):
        """ Copies the selected text to the clipboard.

        """
        self.abstract_obj.copy()

    def paste(self):
        """ Paste the contents of the clipboard into the field.

        Inserts the contents of the clipboard into the field at the 
        current cursor position, replacing any selected text.

        """
        self.abstract_obj.paste()

    def insert(self, text):
        """ Insert the text into the field.

        Inserts the given text into the field at the current cursor 
        position, replacing any selected text.

        Arguments
        ---------
        text : str
            The text to insert into the field.

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
    # Submission Machinery
    #--------------------------------------------------------------------------
    def submit(self, format=True):
        """ A method which is called to perform the submission. 

        A submit involves converting the current text in the field into a 
        Python value using the current validator, and storing that value
        in the 'value' attribute. If an error occurs during conversion,
        then the 'invalid', 'error' and 'exception' attributes on the 
        field will be set appropriately.

        If the current text does not validate as ACCEPTABLE then the
        'value' attribute will not be changed. In such case if 'format'
        is True, then the existing value will be formatted and the 
        display text updated.
        
        Parameters
        ----------
        format : bool, optional
            Whether or not to re-format the text after conversion and
            submission. A False value is useful for submitting the value
            without causing the text in the field to be updated. The
            default is True.
        
        Returns
        -------
        result : bool
            True if the submission is successful, or False if the text
            is not valid or the conversion from text to value fails. 

        """
        text = self.get_text()
        v = self.validator
        self.acceptable = acceptable = (v.validate(text) == v.ACCEPTABLE)

        res = False
        if acceptable:
            try:
                value = v.convert(text)
            except ValueError as e:
                self.exception = e
                self.error = True
                return
            else:
                # Setting the value attribute may fire off a model 
                # subscription which has the potential to raise other
                # exceptions. XXX we may want to log this exception
                # at some point in the future.
                try:
                    with guard(self, 'submitting'):
                        self.value = value
                except Exception as e:
                    self.exception = e
                    self.error = True
                    return
                else:
                    res = True
                    self.exception = None
                    self.error = False

        if format:
            text = v.format(self.value)
            self.set_text(text)
            self.acceptable = (v.validate(text) == v.ACCEPTABLE)
        
        return res

    @on_trait_change('value, validator')
    def _update_text_from_value(self):
        """ A change handler which updates the displayed text whenever
        the 'value' or the 'validator' attributes change.

        """
        if not guard.guarded(self, 'submitting'):
            self.modified = False
            v = self.validator
            text = v.format(self.value)
            self.set_text(text)
            self.acceptable = (v.validate(text) == v.ACCEPTABLE)
    
    #--------------------------------------------------------------------------
    # Field Update Methods
    #--------------------------------------------------------------------------
    def _field_text_edited(self):
        """ A method which should be called by the toolkit implementation
        whenever the user edits the text in the ui, but not when the text
        has been updated by a call to set_text(). This method should not
        be called if the user input validates as INVALID as such text
        should be rejected entirely.

        """
        self.modified = True
        if 'always' in self.submit_mode:
            self.submit(format=False)
        else:
            v = self.validator
            self.acceptable = (v.validate(self.get_text()) == v.ACCEPTABLE)
        self.text_edited()
    
    def _field_return_pressed(self):
        """ A method which should be called by the toolkit implementation
        whenever the user presses the return key, but only if the text in 
        the field validates as ACCEPTABLE.

        """
        if 'return_pressed' in self.submit_mode:
            self.submit()
        self.return_pressed()
    
    def _field_lost_focus(self):
        """ A method which should be called by the toolkit implementation 
        whenever the field loses focus.

        """
        if 'lost_focus' in self.submit_mode:
            self.submit()
        self.lost_focus()

