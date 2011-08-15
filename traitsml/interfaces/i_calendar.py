from traits.api import Date, Int

from .i_element import IElement


class ICalendar(IElement):
    """ A calendar widget.

    A Calendar displays a Python datetime.date using an appropriate
    toolkit specific control. The date attribute is synchronized 
    bi-directionally with the day, month, and year attributes.
    
    Attributes
    ----------
    date : Date
        The currently selected date.
    
    day : Int
        The selected day.
    
    month : Int
        The selected month.
    
    year : Int
        The selected year.
    
    """    
    date = Date

    day = Int

    month = Int

    year = Int

