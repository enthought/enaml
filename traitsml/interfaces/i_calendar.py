from traits.api import Date, Int

from .i_element import IElement


class ICalendar(IElement):
    """A calendar widget: select day, month, and year."""

    # The currently selected day.
    selection = Date

    # The visible month
    month = Int

    # The visible year
    year = Int
