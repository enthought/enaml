#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import (
    Bool, Int, Unicode, Enum, Instance, Any, List, on_trait_change,
)

from .control import Control

from ..core.trait_types import EnamlEvent
from ..guard import guard
from ..validation import AbstractValidator, CoercingValidator


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

    @on_trait_change('max_length, password_mode, placeholder_text, read_only, \
        submit_mode, text, validator')
    def sync_object_state(self, name, new):
        msg = 'set_' + name
        self.send(msg, {'value':new})

    def initial_attrs(self):
        super_attrs = super(Field, self).initial_attrs()
        attrs = {'max_length':self.max_length, 'read_only':self.read_only,
                 'password_mode':self.password_mode, 'text':self.text,
                 'placeholder_text':self.placeholder_text,
                 'submit_mode':self.submit_mode, 'validator':self.validator}
        attrs.update(super_attrs)
        return attrs

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

