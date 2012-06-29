#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from .qt_constraints_widget import QtConstraintsWidget

class QtBoundedDate(QtConstraintsWidget):
    """ A base class for date widgets

    """
    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_date(self, ctxt):
        """ Message handler for set_date
    
        """
        date = ctxt.get('date')
        if date is not None:
            self.set_date(date)

    def receive_set_max_date(self, ctxt):
        """ Message handler for set_max_date

        """
        date = ctxt.get('max_date')
        if date is not None:
            self.set_max_date(date)

    def receive_set_min_date(self, ctxt):
        """ Message handler for set_min_date

        """
        date = ctxt.get('min_date')
        if date is not None:
            self.set_min_date(date)
            
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_date(self, date):
        """ Set the widget's date

        """
        raise NotImplementedError

    def set_max_date(self, date):
        """ Set the widget's maximum date

        """
        raise NotImplementedError

    def set_min_date(self, date):
        """ Set the widget's minimum date

        """
        raise NotImplementedError
