#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_client_widget import QtClientWidget

class QtControl(QtClientWidget):
      """ A base class for all Qt controls
      
      """
      #--------------------------------------------------------------------------
      # Message Handlers
      #--------------------------------------------------------------------------
      def receive_set_error(self, ctxt):
            """ Message handler for set_error

            """
            err = ctxt.get('value')
            if err is not None:
                  self.set_error(err)

      #--------------------------------------------------------------------------
      # Widget Update Methods
      #--------------------------------------------------------------------------
      def set_error(self, err):
            """ Set whether an exception was raised through user interaction or
            setting a value trait on the Control.
      
            """
            raise NotImplementedError
