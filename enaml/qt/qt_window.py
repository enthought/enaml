#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QWidget
from .qt.QtCore import QSize
from .qt_client_widget import QtClientWidget


class QtWindow(QtClientWidget):
    """ A Qt implementation of a window

    """
    def create(self, parent):
        """ Create the underlying widget

        """
        self.widget = QWidget(parent)
        self.widget.show()

    def initialize(self, init_attrs):
        """ Initialize the widget's attributes

        """
        self.set_title(init_attrs.get('title', ''))
        #self.set_icon(init_attrs.get('icon'))
        #self.set_maximum_size(init_attrs.get('maximum_size'))
        #self.set_minimum_size(init_attrs.get('minimum_size'))
        #self.set_initial_size(init_attrs.get('initial_size'))
        #self.set_initial_size_default(init_attrs.get('initial_size_default'))
        #self.set_minimum_size_default(init_attrs.get('minimum_size_default'))
        #self.set_maximum_size_default(init_attrs.get('maximum_size_default'))

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def receive_maximize(self, ctxt):
        """ Message handler for maximize

        """
        self.maximize()

    def receive_minimize(self, ctxt):
        """ Message handler for minimize

        """
        self.minimize()

    def receive_restore(self, ctxt):
        """ Message handler for restore

        """
        self.restore()

    def receive_set_icon(self, ctxt):
        """ Message handler for set_icon

        """
        # XXX needs to be implemented
        pass

    def receive_set_initial_size(self, ctxt):
        """ Message handler for set_initial_size

        """
        size = ctxt.get('value')
        if size is not None:
            self.set_initial_size(size)

    def receive_set_initial_size_default(self, ctxt):
        """ Message handler for set_initial_size_default

        """
        size = ctxt.get('value')
        if size is not None:
            self.set_initial_default_size(size)
            
    def receive_set_maximum_size(self, ctxt):
        """ Message handler for set_maximum_size

        """
        size = ctxt.get('value')
        if size is not None:
            self.set_maximum_size(size)

    def receive_set_maximum_size_default(self, ctxt):
        """ Message handler for set_maximum_size_default

        """
        size = ctxt.get('value')
        if size is not None:
            self.set_maximum_size_default(size)

    def receive_set_minimum_size(self, ctxt):
        """ Message handler for set_minimum_size

        """
        size = ctxt.get('value')
        if size is not None:
            self.set_minimum_size(size)

    def receive_set_minimum_size_default(self, ctxt):
        """ Message handler for set_minimum_size_default

        """
        size = ctxt.get('value')
        if size is not None:
            self.set_minimum_size_default(size)

    def receive_set_title(self, ctxt):
        """ Message handler for set_title

        """
        title = ctxt.get('value')
        if title is not None:
            self.set_title(title)

    def receive_show(self, ctxt):
        """ Message handler for show

        """
        self.show()
    
    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def maximize(self):
        """ Maximize the window

        """
        self.widget.showMaximized()

    def minimize(self):
        """ Minimize the window

        """
        self.widget.showMinimized()

    def restore(self):
        """ Restore the window after a minimize or maximize

        """
        self.widget.showNormal()

    def set_icon(self, icon):
        """ Set the window icon

        """
        # XXX needs to be implemented
        pass

    def set_initial_size(self, size):
        """ Set the initial window size
        
        """
        self.initial_size = size
        self.widget.resize(QSize(*self._compute_initial_size()))

    def set_initial_size_default(self, size):
        """ Set the initial window size default (used if no other initial
        size could be calculated)

        """
        self.initial_size_default = size
        self.set_initial_size(self._compute_initial_size())

    def set_maximum_size(self, size):
        """ Set the maximum size of the window

        """
        self.maximum_size = size
        self.widget.setMaximumSize(QSize(*self._compute_maximum_size()))

    def set_maximum_size_default(self, size):
        """ Set the maximum window size default

        """
        self.maximum_size_default = size
        self.set_maximum_size(self._compute_maximum_size())

    def set_minimum_size(self, size):
        """ Set the minimum size of the window

        """
        self.minimum_size = size
        self.widget.setMinimumSize(QSize(*self._compute_minimum_size()))

    def set_minimum_size_default(self, size):
        """ Set the minimum size default

        """
        self.minimum_size_default = size
        self.set_minimum_size(self._compute_minimum_size())
    
    def set_title(self, title):
        """ Set the title of the window

        """
        self.widget.setWindowTitle(title)

    def show(self):
        """ Show the window

        """
        self.widget.show()

    #--------------------------------------------------------------------------
    # Size Computation Methods
    #--------------------------------------------------------------------------
    def _compute_initial_size(self):
        """ Computes and returns the initial size of the window without
        regard for minimum or maximum sizes.

        """
        # If the user has supplied an explicit initial size, use that.
        computed_width, computed_height = self.initial_size
        if computed_width != -1 and computed_height != -1:
            return (computed_width, computed_height)
        
        # Otherwise, try to compute a default from the central widget.
        widget = self.widget
        if widget is not None:
            size_hint_width = widget.sizeHint().width()
            size_hint_height = widget.sizeHint().height()
            if computed_width == -1:
                computed_width = size_hint_width
            if computed_height == -1:
                computed_height = size_hint_height

        # We use the last resort values to replace any remaining 
        # -1 values. This ensures the return value will be >= 0 
        # in both width and height.
        if computed_width == -1 or computed_height == -1:
            default_width, default_height = self.initial_size_default
            if computed_width == -1:
                computed_width = default_width
            if computed_height == -1:
                computed_height = default_height

        return (computed_width, computed_height)

    def _compute_minimum_size(self):
        """ Computes and returns the minimum size of the window.

        """
        # If the user has supplied an explicit minimum size, use that.
        computed_width, computed_height = self.minimum_size
        if computed_width != -1 and computed_height != -1:
            return (computed_width, computed_height)

        # XXX needs to be reimplemented
        # Otherwise, try to compute a default from the central widget.
        #widget = self.central_widget
        #if widget is not None:

            # If the central widget is a container, we have it compute
            # the minimum size for us, otherwise, we use the size hint
            # of the widget as the value.
            #if isinstance(widget, Container):
            #    min_width, min_height = widget.compute_min_size()
            #else:
            #    min_width, min_height = widget.size_hint()

            # If the hug and resist clip policies of the widget are
            # weaker than the resize strength of the window, then
            # we ignore its value in that direction.
            #if ((widget.hug_width not in STRONGER_THAN_RESIZE) and
            #    (widget.resist_clip_width not in STRONGER_THAN_RESIZE)):
            #    min_width = -1
            
            #if ((widget.hug_height not in STRONGER_THAN_RESIZE) and
            #    (widget.resist_clip_height not in STRONGER_THAN_RESIZE)):
            #    min_height = -1 

            #if computed_width == -1:
            #    computed_width = min_width

            #if computed_height == -1:
            #    computed_height = min_height
        
        # We use the last resort values to replace any remaining 
        # -1 values. This ensures the return value will be >= 0 
        # in both width and height
        if computed_width == -1 or computed_height == -1:
            default_width, default_height = self.minimum_size_default
            if computed_width == -1:
                computed_width = default_width
            if computed_height == -1:
                computed_height = default_height
        
        return (computed_width, computed_height)

    def _compute_maximum_size(self):
        """ Computes and returns the maximum size of the window.

        """
        # If the user has supplied an explicit maximum size, use that.
        computed_width, computed_height = self.maximum_size
        if computed_width != -1 and computed_height != -1:
            return (computed_width, computed_height)

        # XXX Needs to be reimplemented
        # Otherwise, try to compute a default from the central widget.
        #widget = self.central_widget
        #if widget is not None:

            # If the central widget is a container, we have it compute
            # the maximum size for us, otherwise, we use the size hint
            # of the widget as the value.
            #if isinstance(widget, Container):
            #    max_width, max_height = widget.compute_max_size()
            #else:
            #    max_width, max_height = widget.size_hint()

            # If the hug policy of the widget is weaker than the 
            # resize strength of the window, then we ignore its 
            # value in that direction.
            #if widget.hug_width not in STRONGER_THAN_RESIZE:
            #    max_width = -1
            
            #if widget.hug_height not in STRONGER_THAN_RESIZE:
            #    max_height = -1 

            #if computed_width == -1:
            #    computed_width = max_width

            #if computed_height == -1:
            #    computed_height = max_height

        # We use the last resort values to replace any remaining 
        # -1 values. This ensures the return value will be >= 0 
        # in both width and height.
        if computed_width == -1 or computed_height == -1:
            default_width, default_height = self.maximum_size_default
            if computed_width == -1:
                computed_width = default_width
            if computed_height == -1:
                computed_height = default_height
        
        return (computed_width, computed_height)
