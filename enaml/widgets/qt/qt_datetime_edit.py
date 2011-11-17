#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui, QtCore

from .qt_bounded_datetime import QtBoundedDatetime

from ..datetime_edit import AbstractTkDatetimeEdit


# Workaround for an incompatibility between PySide and PyQt
try:
    qdatetime_to_python = QtCore.QDateTime.toPython
except AttributeError:
    qdatetime_to_python = QtCore.QDateTime.toPyDateTime


class QtDatetimeEdit(QtBoundedDatetime, AbstractTkDatetimeEdit):
    """ A Qt implementation of DateTimeEdit.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Creates the underlying QtCalendarWidget.

        """
        self.widget = QtGui.QDateTimeEdit(self.parent_widget())

    def initialize(self):
        """ Initializes the attributes of the control.

        """
        super(QtDatetimeEdit, self).initialize()
        self.set_format(self.shell_obj.datetime_format)
    
    def bind(self):
        """ Connects the signal handlers for the date edit widget. Not
        meant for public consumption.

        """
        super(QtDatetimeEdit, self).bind()
        self.widget.dateTimeChanged.connect(self.on_datetime_changed)

    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_datetime_format_changed(self, datetime_format):
        """ The change handler for the 'format' attribute.

        """
        self.set_format(datetime_format)

    def on_datetime_changed(self):
        """ The signal handler for the controls's changed event. Not
        meant for public consumption.

        """
        # only emit update the shell object if the widget was 
        # changed via the ui and not programmatically.
        if not self._setting_datetime:
            shell = self.shell_obj
            qdatetime = self.widget.dateTime()
            new_datetime = qdatetime_to_python(qdatetime)
            shell.datetime = new_datetime
            shell.datetime_changed = new_datetime

    #: A boolen flag used to avoid feedback loops when setting the
    #: datetime programmatically.
    _setting_datetime = False

    def set_datetime(self, datetime):
        """ Sets and the datetime on the widget.

        """
        # Calling setDate will trigger the dateChanged signal.
        # We want to avoid that feeback loop since the value is
        # being set programatically.
        self._setting_datetime = True
        self.widget.setDateTime(datetime)
        self._setting_datetime = False

    def set_min_datetime(self, datetime):
        """ Sets the minimum datetime on the widget with the provided 
        value.

        """
        # Calling setMinimumDateTime *may* trigger the dateTimeChanged 
        # signal, if the datetime needs to be clipped. We want to avoid 
        # that feeback  loop since the value is being set programatically 
        # and the new datetime will already have been updated by the shell 
        # object.
        self._setting_datetime = True
        self.widget.setMinimumDateTime(datetime)
        self._setting_datetime = False

    def set_max_datetime(self, datetime):
        """ Sets the maximum datetime on the widget with the provided 
        value.

        """
        # Calling setMaximumDateTime *may* trigger the dateTimeChanged 
        # signal, if the datetime needs to be clipped. We want to avoid 
        # that feeback  loop since the value is being set programatically 
        # and the new datetime will already have been updated by the shell 
        # object.
        self._setting_datetime = True
        self.widget.setMaximumDateTime(datetime)
        self._setting_datetime = False
        
    def set_format(self, datetime_format):
        """ Sets the display format on the widget with the provided 
        value.

        """
        self.widget.setDisplayFormat(datetime_format)

