#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import weakref

from .qt import QtGui

from ..base_component import AbstractTkBaseComponent


class QtBaseComponent(AbstractTkBaseComponent):
    """ Base component object for the Qt based backend.

    """
    #: The a reference to the shell object. Will be stored as a weakref.
    _shell_obj = lambda self: None

    #: The Qt widget created by the component
    widget = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------    
    def create(self, parent):
        """ Create the underlying Qt widget.

        """
        self.widget = QtGui.QFrame(parent)

    def initialize(self):
        """ Initialize the attributes of the Qt widget.

        """
        pass
    
    def bind(self):
        """ Bind any event/signal handlers for the Qt Widget.

        """
        pass

    def destroy(self):
        """ Destroy the underlying Qt widget.

        """
        widget = self.widget
        if widget:
            # On Windows, it's not sufficient to simply destroy the
            # widget. It appears that this only schedules the widget 
            # for destruction at a later time. So, we need to explicitly
            # unparent the widget as well.
            widget.setParent(None)
            widget.destroy()

    #--------------------------------------------------------------------------
    # Abstract Implementation
    #--------------------------------------------------------------------------
    @property
    def toolkit_widget(self):
        """ A property that returns the toolkit specific widget for this
        component.

        """
        return self.widget

    def _get_shell_obj(self):
        """ Returns a strong reference to the shell object.

        """
        return self._shell_obj()
    
    def _set_shell_obj(self, obj):
        """ Stores a weak reference to the shell object.

        """
        self._shell_obj = weakref.ref(obj)
    
    #: A property which gets a sets a reference (stored weakly)
    #: to the shell object
    shell_obj = property(_get_shell_obj, _set_shell_obj)

