from traits.api import Date, Int

from .i_element import IElement


class ICalendar(IElement):
    """ A calendar widget.
    
    Attributes
    ----------
    date : datetime.date
        The currently selected date.
    
    day : Int
        The selected day.
    
    month : Int
        The selected month.
    
    year : Int
        The selected year.
    
    The date attribute is synchronized bi-directionally with the
    day, month, and year attributes.
    
    """    
    date = Date

    day = Int

    month = Int

    year = Int


