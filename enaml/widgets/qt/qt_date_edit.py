#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui, QtCore
from traits.api import implements

from .qt_control import QtControl
from ..date_edit import IDateEditImpl


# Workaround for an incompatibility between PySide and PyQt
try:
    qdate_to_python = QtCore.QDate.toPython
except AttributeError:
    qdate_to_python = QtCore.QDate.toPyDate


class QtDateEdit(QtControl):
    """ A Qt implementation of DateEdit.

    See Also
    --------
    DateEdit

    """
    implements(IDateEditImpl)

    #---------------------------------------------------------------------------
    # IDateEditImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying QtCalendarWidget.

        """
        self.widget = QtGui.QDateEdit(self.parent_widget())

    def initialize_widget(self):
        """ Initializes the attributes of the control.

        """
        parent = self.parent
        self.set_minimum_date(parent.minimum_date)
        self.set_maximum_date(parent.maximum_date)
        self.set_format(parent.date_format)
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

    def parent_date_format_changed(self, date_format):
        """ The change handler for the 'format' attribute.

        """
        self.set_format(date_format)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------

    def connect(self):
        """ Connects the signal handlers for the date edit widget.

        """
        self.widget.dateChanged.connect(self.on_date_changed)

    def on_date_changed(self, date):
        """ The signal handler for the controls's changed event.

        """
        parent = self.parent
        new_date = self.get_date() # FIXME: Is this necessary? What about 'date'
        parent.date = new_date
        parent.date_changed = new_date

    def set_date(self, date):
        """ Sets the date on the widget.

        """
        self.widget.setDate(date)

    def set_minimum_date(self, date):
        """ Sets the minimum date on the widget with the provided value.
        Not meant for public consumption.

        """
        self.widget.setMinimumDate(date)

    def set_maximum_date(self, date):
        """ Sets the maximum date on the widget with the provided value.

        """
        self.widget.setMaximumDate(date)

    def set_format(self, date_format):
        """ Sets the display format on the widget with the provided value.

        """
        self.widget.setDisplayFormat(date_format)

    def get_date(self):
        """ Get the active widget date.

        """
        qdate = self.widget.date()
        return qdate_to_python(qdate)
