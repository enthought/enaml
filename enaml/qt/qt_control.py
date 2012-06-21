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

      def receive_set_show_focus_rect(self, ctxt):
            """ Message handler for set_show_focus_rect

            """
            show = ctxt.get('value')
            if show is not None:
                  self.set_show_focus_rect(show)

      #--------------------------------------------------------------------------
      # Widget Update Methods
      #--------------------------------------------------------------------------
      def set_error(self, err):
            """ Set whether an exception was raised through user interaction or
            setting a value trait on the Control.
      
            """
            raise NotImplementedError

      def set_show_focus_rect(self, show):
            """ Set whether or not to draw a focus rectangle around a control.
            Support for this may not be implemented on all controls or on all
            platforms or all backends.

            """
            raise NotImplementedError
