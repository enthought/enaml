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
        self.set_format(parent.format)
        self.set_and_validate_date()
        self.connect()

    def parent_date_changed(self, date):
        """ The change handler for the 'date' attribute.

        The method assigns the current component date in the toolkit
        widget. If the widget trancates the value then the components is
        updated to reflect the widget behaviour.

        """
        self.set_and_validate_date()

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

    def parent_format_changed(self, date_format):
        """ The change handler for the 'format' attribute. Not
        meant for public consumption.

        """
        self.set_format(date_format)

    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------

    def connect(self):
        """ Connects the signal handlers for the date edit widget. Not
        meant for public consumption.

        """
        self.widget.dateChanged.connect(self.on_date_changed)

    def on_date_changed(self, date):
        """ The signal handler for the controls's changed event. Not
        meant for public consumption.

        """
        parent = self.parent
        new_date = self.get_date()
        parent.date = new_date
        parent.date_changed = new_date

    def set_and_validate_date(self):
        """ Sets and validates the component date on the widget.

        The method sets the date in the toolkit widget and makes sure that
        if the widget has truncated the enaml component is syncronized
        without firing trait notification events.
        """
        parent = self.parent
        date = parent.date
        self.widget.setDate(date)
        validated_widget_date = self.get_date()
        if validated_widget_date != date:
            self.parent.trait_setq(date=validated_widget_date)

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

