#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui, QtCore
from .qt_bounded_date import QtBoundedDate

from ..calendar import AbstractTkCalendar


# Workaround for an incompatibility between PySide and PyQt
try: # pragma: no cover
    qdate_to_python = QtCore.QDate.toPython
except AttributeError: # pragma: no cover
    qdate_to_python = QtCore.QDate.toPyDate


class QtCalendar(QtBoundedDate, AbstractTkCalendar):
    """ A Qt implementation of Calendar.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QtCalendarWidget.

        """
        self.widget = QtGui.QCalendarWidget(self.parent_widget())

    def bind(self):
        """ Binds the event handlers for the calendar widget.

        """
        super(QtCalendar, self).bind()
        widget = self.widget
        widget.activated.connect(self.on_date_activated)
        widget.selectionChanged.connect(self.on_date_selected)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def on_date_activated(self, qdate):
        """ The event handler for the calendar's activation event.

        """
        shell = self.shell_obj
        date = qdate_to_python(qdate)
        shell.date = date
        shell.activated = date

    def on_date_selected(self):
        """ The event handler for the calendar's selection event.

        """
        date = qdate_to_python(self.widget.selectedDate())
        self.shell_obj.selected = date

    def set_date(self, date):
        """ Sets and validates the component date on the widget.

        """
        self.widget.setSelectedDate(date)

    def set_min_date(self, min_date):
        """ Sets the minimum date on the widget with the provided value.

        """
        self.widget.setMinimumDate(min_date)

    def set_max_date(self, max_date):
        """ Sets the maximum date on the widget with the provided value.

        """
        self.widget.setMaximumDate(max_date)

