#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import weakref

from .qt import QtCore

from ...components.base_widget_component import AbstractTkBaseWidgetComponent


class QtBaseWidgetComponent(AbstractTkBaseWidgetComponent):
    """ A Qt4 implementation of BaseWidgetComponent.

    """
    #: The reference to the shell object. Will be stored as a weakref.
    _shell_obj = lambda self: None

    #: The Qt widget/object created by the component
    widget = None

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

    def create(self, parent):
        """ Creates the underlying Qt object. As necessary, subclasses
        should reimplement this method to create different types of
        widgets.

        """
        self.widget = QtCore.QObject(parent)

    def initialize(self):
        """ Initializes the attributes of the the Qt widget.

        """
        super(QtBaseWidgetComponent, self).initialize()
    
    def bind(self):
        """ Bind any event/signal handlers for the Qt Widget. By default,
        this is a no-op. Subclasses should reimplement this method as
        necessary to bind any widget event handlers or signals.

        """
        super(QtBaseWidgetComponent, self).bind()

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
            if widget.isWidgetType():
                widget.destroy()
        self.widget = None

