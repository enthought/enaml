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
        if not self._setting_date:
            date = qdate_to_python(self.widget.selectedDate())
            self.shell_obj.selected = date

    #: A boolen flag used to avoid feedback loops when setting the
    #: date programmatically.
    _setting_date = False

    def set_date(self, date):
        """ Sets and validates the component date on the widget.

        """
        # Calling setSelectedDate will trigger the dateChanged signal.
        # We want to avoid that feeback loop since the value is being 
        # set programatically.
        self._setting_date = True
        self.widget.setSelectedDate(date)
        self._setting_date = False

    def set_min_date(self, min_date):
        """ Sets the minimum date on the widget with the provided value.

        """
        # Calling setMinimumDate *may* trigger the dateChanged signal,
        # if the date needs to be clipped. We want to avoid that feeback 
        # loop since the value is being set programatically and the new
        # date will already have been updated by the shell object.
        self._setting_date = True
        self.widget.setMinimumDate(min_date)
        self._setting_date = False

    def set_max_date(self, max_date):
        """ Sets the maximum date on the widget with the provided value.

        """
        # Calling setMaximumDate *may* trigger the dateChanged signal,
        # if the date needs to be clipped. We want to avoid that feeback 
        # loop since the value is being set programatically and the new
        # date will already have been updated by the shell object.
        self._setting_date = True
        self.widget.setMaximumDate(max_date)
        self._setting_date = False

