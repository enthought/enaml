#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui, QtCore

from traits.api import implements

from .qt_control import QtControl

from ..datetime_edit import IDateTimeEditImpl


# Workaround for an incompatibility between PySide and PyQt
try:
    qdatetime_to_python = QtCore.QDateTime.toPython
except AttributeError:
    qdatetime_to_python = QtCore.QDateTime.toPyDateTime


class QtDateTimeEdit(QtControl):
    """ A Qt implementation of DateTimeEdit.

    See Also
    --------
    DateEdit

    """
    implements(IDateTimeEditImpl)

    #---------------------------------------------------------------------------
    # IDateEditImpl interface
    #---------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying QtCalendarWidget.

        """
        self.widget = QtGui.QDateTimeEdit(self.parent_widget())

    def initialize_widget(self):
        """ Initializes the attributes of the control.

        """
        parent = self.parent
        self.set_minimum_datetime(parent.minimum_datetime)
        self.set_maximum_datetime(parent.maximum_datetime)
        self.set_format(parent.format)
        self.set_and_validate_date()
        self.connect()

    def parent_datetime_changed(self, datetime):
        """ The change handler for the 'date' attribute.

        """
        self.set_and_validate_date()

    def parent_minimum_datetime_changed(self, datetime):
        """ The change handler for the 'minimum_date' attribute.

        """
        self.set_minimum_datetime(datetime)

    def parent_maximum_datetime_changed(self, datetime):
        """ The change handler for the 'maximum_date' attribute.

        """
        self.set_maximum_datetime(datetime)

    def parent_format_changed(self, datetime_format):
        """ The change handler for the 'format' attribute.

        """
        self.set_format(datetime_format)


    #---------------------------------------------------------------------------
    # Implementation
    #---------------------------------------------------------------------------
    def connect(self):
        """ Connects the signal handlers for the date edit widget. Not
        meant for public consumption.

        """
        self.widget.dateTimeChanged.connect(self.on_datetime_changed)

    def on_datetime_changed(self):
        """ The signal handler for the controls's changed event. Not
        meant for public consumption.
        """
        parent = self.parent
        new_datetime = self.get_datetime()
        parent.datetime = new_datetime
        parent.datetime_changed = new_datetime

    def set_and_validate_date(self):
        """ Sets and validates the datetime on the widget.

        The method sets the datetime in the toolkit widget and makes sure
        that if the widget has truncated the value,  the enaml component
        is syncronized without firing trait notification events.
        """
        parent = self.parent
        datetime = parent.datetime
        self.widget.setDateTime(datetime)
        validated_widget_datetime = self.get_datetime()
        if validated_widget_datetime != datetime:
            self.parent.trait_setq(datetime=validated_widget_datetime)

    def set_minimum_datetime(self, datetime):
        """ Sets the minimum datetime on the widget with the provided value.

        """
        self.widget.setMinimumDateTime(datetime)

    def set_maximum_datetime(self, datetime):
        """ Sets the maximum datetime on the widget with the provided value.

        """
        self.widget.setMaximumDateTime(datetime)

    def set_format(self, datetime_format):
        """ Sets the display format on the widget with the provided value.

        """
        self.widget.setDisplayFormat(datetime_format)

    def get_datetime(self):
        """ Get the active widget date.

        """
        qdatetime = self.widget.dateTime()
        return qdatetime_to_python(qdatetime)
