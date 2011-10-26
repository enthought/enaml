#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Event, Str, Instance

from .bounded_datetime import BoundedDatetime, AbstractTkBoundedDatetime


class AbstractTkDatetimeEdit(AbstractTkBoundedDatetime):

    @abstractmethod
    def shell_datetime_format_changed(self, datetime_format):
        raise NotImplementedError


class DatetimeEdit(BoundedDatetime):
    """ A datetime widget.

    A DatetimeEdit displays a Python datetime.datetime object using an
    appropriate toolkit specific control.

    """
    #: A python date format string to format the datetime. If None is
    #: supplied (or is invalid) the system locale setting is used.
    #: This may not be supported by all backends.
    datetime_format = Str

    #: Triggered whenever the user clicks or changes the control. 
    #: The event payload will be the datetime on the control.
    datetime_changed = Event

    #: Overridden parent class trait
    abstract_obj = Instance(AbstractTkDatetimeEdit)

