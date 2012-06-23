#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QDateTimeEdit
from .qt import QtCore
from .qt_bounded_datetime import QtBoundedDatetime

# Workaround for an incompatibility between PySide and PyQt
try: # pragma: no cover
    qdatetime_to_python = QtCore.QDateTime.toPython
except AttributeError: # pragma: no cover
    qdatetime_to_python = QtCore.QDateTime.toPyDateTime

class QtDatetimeEdit(QtBoundedDatetime):
    """ A Qt implementation of a datetime edit

    """
    def create(self):
        """ Create the underlying widget

        """
        self.widget = QDateTimeEdit(self.parent_widget)

    def initialize(self, init_attrs):
        """ Initialize the widget's attributes

        """
        self.set_datetime(init_attrs.get('datetime'))
        self.set_min_datetime(init_attrs.get('min_datetime'))
        self.set_max_datetime(init_attrs.get('max_datetime'))
        self.set_datetime_format(init_attrs.get('datetime_format'))

    def bind(self):
        """ Connect the widgets signals to slots

        """
        self.widget.dateTimeChanged.connect(self.on_datetime_changed)
        
    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_datetime_changed(self, datetime):
        """ Event handler for datetime_changed

        """
        self.send('datetime_changed', {'value':qdatetime_to_python(datetime)})

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_datetime(self, ctxt):
        """ Message handler for set_datetime

        """
        datetime = ctxt.get('value')
        if datetime is not None:
            self.set_datetime(datetime)

    def receive_set_max_datetime(self, ctxt):
        """ Message handler for set_max_datetime

        """
        datetime = ctxt.get('value')
        if datetime is not None:
            self.set_max_datetime(datetime)

    def receive_set_min_datetime(self, ctxt):
        """ Message handler for set_min_datetime

        """
        datetime = ctxt.get('value')
        if datetime is not None:
            self.set_min_datetime(datetime)

    def receive_set_datetime_format(self, ctxt):
        """ Message handler for set_datetime_format

        """
        datetime = ctxt.get('value')
        if datetime is not None:
            self.set_datetime_format(datetime)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_datetime(self, datetime):
        """ Set the widget's datetime

        """
        self.widget.setDateTime(datetime)

    def set_max_datetime(self, datetime):
        """ Set the widget's maximum datetime

        """
        self.widget.setMaximumDateTime(datetime)

    def set_min_datetime(self, datetime):
        """ Set the widget's minimum datetime

        """
        self.widget.setMinimumDateTime(datetime)

    def set_datetime_format(self, datetime_format):
        """ Set the widget's datetime format

        """
        self.widget.setDisplayFormat(datetime_format)
