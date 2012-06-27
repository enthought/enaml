#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QCalendarWidget
from .qt import QtCore
from .qt_bounded_date import QtBoundedDate

# Workaround for an incompatibility between PySide and PyQt
try: # pragma: no cover
    qdate_to_python = QtCore.QDate.toPython
except AttributeError: # pragma: no cover
    qdate_to_python = QtCore.QDate.toPyDate

class QtCalendar(QtBoundedDate):
    """ A Qt implementation of a calendar

    """
    def create(self):
        """ Create the underlying widget

        """
        self.widget = QCalendarWidget(self.parent_widget)

    def initialize(self, init_attrs):
        """ Initialize the widget's attributes

        """
        super(QtCalendar, self).initialize(init_attrs)
        self.set_date(init_attrs.get('date'))
        self.set_min_date(init_attrs.get('min_date'))
        self.set_max_date(init_attrs.get('max_date'))

    def bind(self):
        """ Connect the widgets signals to slots

        """
        self.widget.activated.connect(self.on_activated)
        self.widget.selectionChanged.connect(self.on_selected)
        
    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_activated(self, date):
        """ Event handler for date_activated

        """
        self.send('activated', {'value':qdate_to_python(date)})

    def on_selected(self):
        """ Event handler for date_selected

        """
        self.send('selected', {'value':qdate_to_python(
            self.widget.selectedDate())})

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_date(self, ctxt):
        """ Message handler for set_date

        """
        date = ctxt.get('value')
        if date is not None:
            self.set_date(date)

    def receive_set_max_date(self, ctxt):
        """ Message handler for set_max_date

        """
        date = ctxt.get('value')
        if date is not None:
            self.set_max_date(date)

    def receive_set_min_date(self, ctxt):
        """ Message handler for set_min_date

        """
        date = ctxt.get('value')
        if date is not None:
            self.set_min_date(date)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_date(self, date):
        """ Set the widget's date

        """
        self.widget.setSelectedDate(date)

    def set_max_date(self, date):
        """ Set the widget's maximum date

        """
        self.widget.setMaximumDate(date)

    def set_min_date(self, date):
        """ Set the widget's minimum date

        """
        self.widget.setMinimumDate(date)
