#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import weakref

from .qt import QtGui

from ..component import AbstractTkComponent


class QtComponent(AbstractTkComponent):
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
        """ Creates the underlying Qt widget. As necessary, subclasses
        should reimplement this method to create different types of
        widgets.

        """
        self.widget = QtGui.QFrame(parent)

    def initialize(self):
        """ Initializes the attributes of the the Qt widget.

        """
        super(QtComponent, self).initialize()
        self.set_enabled(self.shell_obj.enabled)
    
    def bind(self):
        """ Bind any event/signal handlers for the Qt Widget. By default,
        this is a no-op. Subclasses should reimplement this method as
        necessary to bind any widget event handlers or signals.

        """
        super(QtComponent, self).bind()

    #--------------------------------------------------------------------------
    # Teardown Methods
    #--------------------------------------------------------------------------
    def destroy(self):
        """ Destroys the underlying Qt widget.

        """
        widget = self.widget
        if widget:
            # On Windows, it's not sufficient to simply destroy the
            # widget. It appears that this only schedules the widget 
            # for destruction at a later time. So, we need to explicitly
            # unparent the widget as well.
            widget.setParent(None)
            widget.destroy()
        self.widget = None

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
        
    def disable_updates(self):
        """ Disable rendering updates for the underlying Qt widget.

        """
        # Freezing updates on a top-level window seems to cause 
        # flicker on OSX the updates are reenabled. In this case, 
        # just freeze the children instead.
        if self.widget.isWindow():
            for child in self.shell_obj.children:
                child.disable_updates()
        else:
            self.widget.setUpdatesEnabled(False)

    def enable_updates(self):
        """ Enable rendering updates for the underlying Wx widget.

        """
        # Freezing updates on a top-level window seems to cause 
        # flicker on OSX the updates are reenabled. In this case, 
        # just freeze the children instead.
        if self.widget.isWindow():
            for child in self.shell_obj.children:
                child.enable_updates()
        self.widget.setUpdatesEnabled(True)

    #--------------------------------------------------------------------------
    # Shell Object Change Handlers 
    #--------------------------------------------------------------------------
    def shell_enabled_changed(self, enabled):
        """ The change handler for the 'enabled' attribute on the shell
        object.

        """
        self.set_enabled(enabled)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_enabled(self, enabled):
        """ Enable or disable the widget.

        """
        self.widget.setEnabled(enabled)

    def set_visible(self, visible):
        """ Show or hide the widget.

        """
        self.widget.setVisible(visible)

