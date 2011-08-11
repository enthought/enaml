from traits.api import Date, Int

from .i_element import IElement


class ICalendar(IElement):
    """ A calendar widget.
    
    Attributes
    ----------
    date : A Python datetime.date object.
    
    day : An integer.
    
    month : An integer.
    
    year : An integer
    
    The date attribute is synchronized bi-directionally with the
    day, month, and year attributes.
    
    """    
    date = Date

    day = Int

    month = Int

    year = Int


