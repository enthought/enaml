#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QDateEdit
from .qt.QtCore import QDate
from .qt_bounded_date import QtBoundedDate

class QtDateEdit(QtBoundedDate):
    """ A Qt implementation of a date edit

    """
    def create(self, parent):
        """ Create the underlying widget

        """
        self.widget = QDateEdit(parent)
        self.widget.show()

    def initialize(self, init_attrs):
        """ Initialize the widget's attributes

        """
        self.set_date(init_attrs.get('date'))
        self.set_min_date(init_attrs.get('min_date'))
        self.set_max_date(init_attrs.get('max_date'))
        self.set_date_format(init_attrs.get('date_format'))

    def bind(self):
        """ Connect the widgets signals to slots

        """
        self.widget.dateChanged.connect(self.on_date_changed)
        
    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_date_changed(self):
        """ Event handler for date_changed

        """
        self.send('date_changed', {})

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

    def receive_set_date_format(self, ctxt):
        """ Message handler for set_date_format

        """
        date = ctxt.get('value')
        if date is not None:
            self.set_date_format(date)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_date(self, date):
        """ Set the widget's date

        """
        self.widget.setDate(QDate(date.year, date.month, date.day))

    def set_max_date(self, date):
        """ Set the widget's maximum date

        """
        self.widget.setMaximumDate(QDate(date.year, date.month, date.day))

    def set_min_date(self, date):
        """ Set the widget's minimum date

        """
        self.widget.setMinimumDate(QDate(date.year, date.month, date.day))

    def set_date_format(self, date_format):
        """ Set the widget's date format

        """
        self.widget.setDisplayFormat(date_format)
