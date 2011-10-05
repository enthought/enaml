#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui, QtCore

from traits.api import implements

from .qt_control import QtControl

from ..calendar import ICalendarImpl


# Workaround for an incompatibility between PySide and PyQt
try:
    qdate_to_python = QtCore.QDate.toPython
except AttributeError:
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
        self.set_and_validate_date()
        self.bind()

    def parent_date_changed(self, date):
        """ The change handler for the 'date' attribute.

        """
        self.set_and_validate_date()

    def parent_minimum_date_changed(self, date):
        """ The change handler for the 'minimum_date' attribute.

        """
        self.set_minimum_date(date)

    def parent_maximum_date_changed(self, date):
        """ The change handler for the 'maximum_date' attribute.

        """
        self.set_maximum_date(date)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def bind(self):
        """ Binds the event handlers for the calendar widget.

        """
        widget = self.widget
        widget.activated.connect(self.on_date_activated)
        widget.selectionChanged.connect(self.on_date_selected)

    def on_date_activated(self):
        """ The event handler for the calendar's activation event.

        """
        parent = self.parent
        widget_date = self.get_date()
        parent.date = widget_date
        parent.activated = widget_date

    def on_date_selected(self):
        """ The event handler for the calendar's selection event.

        """
        parent = self.parent
        widget_date = self.get_date()
        parent.date = widget_date
        parent.selected = parent.date

    def set_and_validate_date(self):
        """ Sets and validates the component date on the widget.

        The method sets the date in the toolkit widget and makes sure that
        if the widget has truncated the enaml component is syncronized
        without firing trait notification events.
        """
        parent = self.parent
        date = parent.date
        self.widget.setSelectedDate(date)
        validated_widget_date = self.get_date()
        if validated_widget_date != date:
            self.parent.trait_setq(date=validated_widget_date)

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
