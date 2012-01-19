#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt import QtGui, QtCore
from .qt_bounded_date import QtBoundedDate

from ..date_edit import AbstractTkDateEdit

from ...guard import guard


# Workaround for an incompatibility between PySide and PyQt
try:
    qdate_to_python = QtCore.QDate.toPython
except AttributeError:
    qdate_to_python = QtCore.QDate.toPyDate


class QtDateEdit(QtBoundedDate, AbstractTkDateEdit):
    """ A Qt implementation of DateEdit.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create(self, parent):
        """ Creates the underlying QDateEdit.

        """
        self.widget = QtGui.QDateEdit(parent)

    def initialize(self):
        """ Initializes the attributes of the control.

        """
        super(QtDateEdit, self).initialize()
        self.set_format(self.shell_obj.date_format)
    
    def bind(self):
        """ Connects the signal handlers for the date edit widget.

        """
        super(QtDateEdit, self).bind()
        self.widget.dateChanged.connect(self.on_date_changed)
        
    #--------------------------------------------------------------------------
    # Implementation
    #--------------------------------------------------------------------------
    def shell_date_format_changed(self, date_format):
        """ The change handler for the 'format' attribute.

        """
        self.set_format(date_format)

    def on_date_changed(self):
        """ The signal handler for the controls's changed event.

        """
        # only emit update the shell object if the widget was 
        # changed via the ui and not programmatically.
        if not guard.guarded(self, 'updating'):
            shell = self.shell_obj
            qdate = self.widget.date()
            new_date = qdate_to_python(qdate)
            shell.date = new_date
            shell.date_changed(new_date)

    def set_date(self, date):
        """ Sets the date on the widget.

        """
        # Calling setDate will trigger the dateChanged signal.
        # We want to avoid that feeback loop since the value is
        # being set programatically.
        with guard(self, 'updating'):
            self.widget.setDate(date)

    def set_min_date(self, min_date):
        """ Sets the minimum date on the widget with the provided value.

        """
        # Calling setMinimumDate *may* trigger the dateChanged signal,
        # if the date needs to be clipped. We want to avoid that feeback 
        # loop since the value is being set programatically and the new
        # date will already have been updated by the shell object.
        with guard(self, 'updating'):
            self.widget.setMinimumDate(min_date)

    def set_max_date(self, max_date):
        """ Sets the maximum date on the widget with the provided value.

        """
        # Calling setMaximumDate *may* trigger the dateChanged signal,
        # if the date needs to be clipped. We want to avoid that feeback 
        # loop since the value is being set programatically and the new
        # date will already have been updated by the shell object.
        with guard(self, 'updating'):
            self.widget.setMaximumDate(max_date)
        
    def set_format(self, date_format):
        """ Sets the display format on the widget with the provided value.

        """
        self.widget.setDisplayFormat(date_format)

