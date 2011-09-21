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
        self.set_date(parent.date)
        min_date = parent.minimum_date
        max_date = parent.maximum_date
        if min_date is not None:
            self.set_minimum_date(min_date)
        if max_date is not None:
            self.set_maximum_date(max_date)
        self.connect()

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
    def connect(self):
        """ Connects the signal handlers for the date edit widget. Not 
        meant for public consumption.

        """
        self.widget.dateChanged.connect(self.on_date_changed)
        
    def on_date_changed(self):
        """ The signal handler for the controls's changed event. Not
        meant for public consumption.

        """
        parent = self.parent
        qdate = self.widget.date()
        py_date = qdate_to_python(qdate)
        parent.date = py_date
        parent.activated = py_date
        
    def set_date(self, date):
        """ Sets the date on the widget with the provided value. Not
        meant for public consumption.

        """
        self.widget.setDate(date)

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


        
    
