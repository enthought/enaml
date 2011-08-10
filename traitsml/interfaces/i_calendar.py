from traits.api import Date, Int, Either, Str

from .i_element import IElement


class ICalendar(IElement):
    """A calendar widget: select day, month, and year."""

    # The currently selected date.
    selection = Either(Date, Str)

    # The selected day
    day = Int

    # The visible month
    month = Int

    # The visible year
    year = Int

