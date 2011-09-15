from .qt import QtGui

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
        """ Creates the underlying QtCalendarWidget.

        """
        self.widget = QtGui.QCalendarWidget(self.parent_widget())

    def initialize_widget(self):
        """ Initializes the attributes of the control.

        """
        parent = self.parent
        self.set_date(parent.date)
        min_date = parent.minimum_date
        max_date = parent.maximum_date
        if min_date is not None:
            self.set_minimum_date(min_date)
        if max_date is not None:
            self.set_maximum_date(max_date)
        self.bind()

    def parent_date_changed(self, date):
        """ The change handler for the 'date' attribute. Not meant for
        public consumption.

        """
        self.set_date(date)

    def parent_minimum_date_changed(self, date):
        """ The change handler for the 'minimum_date' attribute. Not 
        meant for public consumption.

        """
        self.set_minimum_date(date)

    def parent_maximum_date_changed(self, date):
        """ The change handler for the 'maximum_date' attribute. Not
        meant for public consumption.

        """
        self.set_maximum_date(date)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def bind(self):
        """ Binds the event handlers for the calendar widget. Not meant
        for public consumption.

        """
        widget = self.widget
        widget.activated.connect(self.on_date_activated)
        widget.selectionChanged.connect(self.on_date_selected)
        
    def on_date_activated(self):
        """ The event handler for the calendar's activation event. Not
        meant for public consumption.

        """
        date = self.widget.selectedDate().toPython()
        self.parent.date = date
        self.parent.activated = date

    def on_date_selected(self):
        """ The event handler for the calendar's selection event. Not
        meant for public consumption.

        """
        date = self.widget.selectedDate().toPython()
        self.parent.selected = date
        
    def set_date(self, date):
        """ Sets the date on the widget with the provided value. Not
        meant for public consumption.

        """
        self.widget.setSelectedDate(date)

    def set_minimum_date(self, date):
        """ Sets the minimum date on the widget with the provided value.
        Not meant for public consumption.

        """
        self.widget.setMinimumDate(date)

    def set_maximum_date(self, date):
        """ Sets the maximum date on the widget with the provided value.
        Not meant for public consumption.

        """
        self.widget.setMaximumDate(date)


        
    
