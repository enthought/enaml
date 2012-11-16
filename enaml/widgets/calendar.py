#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .bounded_date import BoundedDate


class Calendar(BoundedDate):
    """ A bounded date control which edits a Python datetime.date using 
    a widget which resembles a calendar.

    """
    # The BoundedDate interface is sufficient for a Calendar
    pass

