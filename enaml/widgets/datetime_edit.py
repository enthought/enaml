#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from datetime import datetime

from traits.api import Event, Instance, Str

from .control import Control, IControlImpl


class IDateTimeEditImpl(IControlImpl):

    def parent_datetime_changed(self, datetime):
        raise NotImplementedError
    
    def parent_minimum_datetime_changed(self, datetime):
        raise NotImplementedError
    
    def parent_maximum_datetime_changed(self, datetime):
        raise NotImplementedError


class DateTimeEdit(Control):
    """ A datetime widget.

    A DatetimeEdit displays a Python datetime.datetime using an 
    appropriate toolkit specific control.
    
    Attributes
    ----------
    datetime : Instance(datetime.datetime)
        The currently selected datetime.

    minimum_datetime : Instance(datetime.datetime)
        The minimum datetime available in the date edit.

    maximum_datetime : Instance(datetime.datetime)
        The maximum datetime available in the date edit.
    
    format : Str
        A python date format string to format the datetime. If none is 
        supplied (or is invalid) the system locale setting is used.
        This may not be supported by all backends.

    selected : Event
        Triggered whenever the user clicks or changes the control. The
        event payload will be the datetime on the control.

    """    
    datetime = Instance(datetime, factory=datetime.now)

    minimum_datetime = Instance(datetime)

    maximum_datetime = Instance(datetime)

    format = Str

    activated = Event

    #---------------------------------------------------------------------------
    # Overridden parent traits
    #---------------------------------------------------------------------------
    toolkit_impl = Instance(IDateTimeEditImpl)


DateTimeEdit.protect('activated')

