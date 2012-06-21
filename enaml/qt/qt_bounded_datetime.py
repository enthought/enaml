#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------

from .qt_control import QtControl

class QtBoundedDatetime(QtControl):
    """ A base class for datetime widgets

    """
    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_set_date(self, ctxt):
        """ Message handler for set_datetime
    
        """
        datetime = ctxt.get('value')
        if datetime is not None:
            self.set_datetime(datetime)

    def receive_set_max_date(self, ctxt):
        """ Message handler for set_max_datetime

        """
        datetime = ctxt.get('value')
        if datetime is not None:
            self.set_max_datetime(datetime)

    def receive_set_min_date(self, ctxt):
        """ Message handler for set_min_datetime

        """
        datetime = ctxt.get('value')
        if datetime is not None:
            self.set_min_datetime(datetime)
            
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_datetime(self, datetime):
        """ Set the widget's datetime

        """
        raise NotImplementedError

    def set_max_datetime(self, datetime):
        """ Set the widget's maximum datetime

        """
        raise NotImplementedError

    def set_min_datetime(self, datetime):
        """ Set the widget's minimum datetime

        """
        raise NotImplementedError
