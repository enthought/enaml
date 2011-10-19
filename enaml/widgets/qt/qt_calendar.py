#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui, QtCore

from traits.api import implements

from .qt_control import QtControl

from ..calendar import ICalendarImpl


# Workaround for an incompatibility between PySide and PyQt
try: # pragma: no cover
    qdate_to_python = QtCore.QDate.toPython
except AttributeError: # pragma: no cover
    qdate_to_python = QtCore.QDate.toPyDate


class QtCalendar(QtControl):
    """ A Qt implementation of Calendar.

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
        self.set_minimum_date(parent.minimum_date)
        self.set_maximum_date(parent.maximum_date)
        self.set_date(parent.date)
        self.connect()

    def parent_date_changed(self, date):
        """ The change handler for the 'date' attribute.

        """
        self.set_date(date)

    def parent__minimum_date_changed(self, date):
        """ The change handler for the 'minimum_date' attribute.

        """
        self.set_minimum_date(date)

    def parent__maximum_date_changed(self, date):
        """ The change handler for the 'maximum_date' attribute.

        """
        self.set_maximum_date(date)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def connect(self):
        """ Binds the event handlers for the calendar widget.

        """
        widget = self.widget
        widget.activated.connect(self.on_date_activated)
        widget.selectionChanged.connect(self.on_date_selected)

    def on_date_activated(self, qdate):
        """ The event handler for the calendar's activation event.

        """
        parent = self.parent
        date = qdate_to_python(qdate)
        parent.date = date
        parent.activated = date

    def on_date_selected(self):
        """ The event handler for the calendar's selection event.

        """
        self.parent.selected = self.get_date()

    def set_date(self, date):
        """ Sets and validates the component date on the widget.

        """
        self.widget.setSelectedDate(date)

    def set_minimum_date(self, date):
        """ Sets the minimum date on the widget with the provided value.

        """
        self.widget.setMinimumDate(date)

    def set_maximum_date(self, date):
        """ Sets the maximum date on the widget with the provided value.

        """
        self.widget.setMaximumDate(date)

    def get_date(self):
        """ Get the active widget date.

        """
        qdate = self.widget.selectedDate()
        return qdate_to_python(qdate)
