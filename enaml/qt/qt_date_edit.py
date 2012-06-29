#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QDateEdit
from .qt import QtCore
from .qt_bounded_date import QtBoundedDate

# Workaround for an incompatibility between PySide and PyQt
try: # pragma: no cover
    qdate_to_python = QtCore.QDate.toPython
except AttributeError: # pragma: no cover
    qdate_to_python = QtCore.QDate.toPyDate

class QtDateEdit(QtBoundedDate):
    """ A Qt implementation of a date edit

    """
    def create(self):
        """ Create the underlying widget

        """
        self.widget = QDateEdit(self.parent_widget)

    def initialize(self, init_attrs):
        """ Initialize the widget's attributes

        """
        super(QtDateEdit, self).initialize(init_attrs)
        self.set_date(init_attrs.get('value'))
        self.set_min_date(init_attrs.get('minimum'))
        self.set_max_date(init_attrs.get('maximum'))
        self.set_date_format(init_attrs.get('date_format'))

    def bind(self):
        """ Connect the widgets signals to slots

        """
        self.widget.dateChanged.connect(self.on_date_changed)
        
    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_date_changed(self, date):
        """ Event handler for date_changed

        """
        self.send({'action':'date_changed','date':qdate_to_python(date)})

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_date_format(self, ctxt):
        """ Message handler for set_date_format

        """
        date_format = ctxt.get('date_format')
        if date_format is not None:
            self.set_date_format(date_format)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_date(self, date):
        """ Set the widget's date

        """
        self.widget.setDate(date)

    def set_max_date(self, date):
        """ Set the widget's maximum date

        """
        self.widget.setMaximumDate(date)

    def set_min_date(self, date):
        """ Set the widget's minimum date

        """
        self.widget.setMinimumDate(date)

    def set_date_format(self, date_format):
        """ Set the widget's date format

        """
        self.widget.setDisplayFormat(date_format)
