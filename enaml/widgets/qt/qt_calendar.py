from traits.api import implements

from .qt_control import QtControl

from ..calendar import ICalendarImpl


class QtCalendar(QtControl):
    """ A PySide implementation of Calendar.

    See Also
    --------
    Calendar
    
    """
    implements(ICalendarImpl)

    #---------------------------------------------------------------------------
    # ICalendarImpl interface
    #---------------------------------------------------------------------------

    def create_widget(self):
        """ Creates the underlying Qt widget.
        
        """
        
    def initialize_widget(self):
        """ Initializes the attributes of the Qt component.

        """
        
    
