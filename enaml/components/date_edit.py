#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from abc import abstractmethod

from traits.api import Instance, Str

from .bounded_date import BoundedDate, AbstractTkBoundedDate

from ..core.trait_types import EnamlEvent


class AbstractTkDateEdit(AbstractTkBoundedDate):

    @abstractmethod
    def shell_date_format_changed(self, date_format):
        raise NotImplementedError


class DateEdit(BoundedDate):
    """ A widget to edit a Python datetime.date object.

    A DateEdit displays a Python datetime.date using an appropriate
    toolkit specific control. This is a geometrically smaller control 
    than what is provided by Calendar.

    """
    #: A python date format string to format the date. If none is
    #: supplied (or is invalid) the system locale setting is used.
    #: This may not be supported by all backends.
    date_format = Str

    #: Triggered whenever the user changes the date through the ui
    #: control, but not programmatically. The event payload will be 
    #: the date on the control.
    date_changed = EnamlEvent
    
    #: How strongly a component hugs it's contents' width. DateEdits 
    #: ignore the width hug by default, so they expand freely in width.
    hug_width = 'ignore'

    #: Overridden parent class trait.
    abstract_obj = Instance(AbstractTkDateEdit)

