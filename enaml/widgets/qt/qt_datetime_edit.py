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
        self.set_datetime(parent.datetime)
        min_datetime = parent.minimum_datetime
        max_datetime = parent.maximum_datetime
        if min_datetime is not None:
            self.set_minimum_datetime(min_datetime)
        if max_datetime is not None:
            self.set_maximum_datetime(max_datetime)
        self.connect()

    def parent_datetime_changed(self, datetime):
        """ The change handler for the 'date' attribute. Not meant for
        public consumption.

        """
        self.set_datetime(datetime)

    def parent_minimum_datetime_changed(self, datetime):
        """ The change handler for the 'minimum_date' attribute. Not 
        meant for public consumption.

        """
        self.set_minimum_datetime(datetime)

    def parent_maximum_date_changed(self, datetime):
        """ The change handler for the 'maximum_date' attribute. Not
        meant for public consumption.

        """
        self.set_maximum_datetime(datetime)

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
        qdatetime = self.widget.dateTime()
        py_datetime = qdatetime_to_python(qdatetime)
        parent.datetime = py_datetime
        parent.activated = py_datetime
        
    def set_datetime(self, datetime):
        """ Sets the datetime on the widget with the provided value. Not
        meant for public consumption.

        """
        self.widget.setDateTime(datetime)

    def set_minimum_datetime(self, datetime):
        """ Sets the minimum datetime on the widget with the provided value.
        Not meant for public consumption.

        """
        self.widget.setMinimumDateTime(datetime)

    def set_maximum_datetime(self, datetime):
        """ Sets the maximum datetime on the widget with the provided value.
        Not meant for public consumption.

        """
        self.widget.setMaximumDateTime(datetime)

