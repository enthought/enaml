#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, cached_property

from .proxy_widget import ProxyWidget
from .widget_component import WidgetComponent
from .container import Container

class ClientPanel(ProxyWidget, WidgetComponent):
    """ A non-Enaml UI widget that is embeds in an Enaml UI
    
    A ClientPanel represents a UI widget that is outside the control of
    Enaml, but which embeds an Enaml UI.
    
    The expected behavior is that the client session object sill implement a
    method with the signature get_proxy_widget(proxy_id, parent), where `parent`
    is None. This method should return a toolkit widget.
    
    It is presumed that the non-Enaml widget will provide layout for all its
    children, including those coming from Enaml.
    
    """
    #: Returns the central widget in use for the Window
    central_widget = Property(depends_on='children[]')

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the snapshot for a Window.

        """
        snap = super(ClientPanel, self).snapshot()
        snap['central_widget_id'] = self._snap_central_widget_id()
        return snap

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_central_widget(self):
        """ The getter for the 'central_widget' property.

        Returns
        -------
        result : Container or None
            The central widget for the Window, or None if not provieded.

        """
        for child in self.children:
            if isinstance(child, Container):
                return child

    def _snap_central_widget_id(self):
        """ Returns the widget id of the central widget or None.

        """
        widget = self.central_widget
        if widget is not None:
            return widget.widget_id

