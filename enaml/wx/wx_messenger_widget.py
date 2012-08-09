#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging
from weakref import ref

from enaml.utils import LoopbackGuard


class WxMessengerWidget(object):
    """ The base class of the Wx widgets wrappers for a Wx Enaml client.

    """
    def __init__(self, parent, widget_id, session):
        """ Initialize a WxMessengerWidget

        Parameters
        ----------
        parent : WxMessengerWidget or None
            The parent widget of this widget, or None if this widget has
            no parent.

        widget_id : str
            The identifier string for this widget.

        session : WxClientSession
            The client session object to use for communicating with the
            server widget.

        """
        self._parent_ref = ref(parent) if parent is not None else lambda: None
        self.widget = None
        self.children = []
        self.children_map = {}
        self.widget_id = widget_id
        self.session = session
        if parent is not None:
            parent.children.append(self)
            parent.children_map[widget_id] = self

    #--------------------------------------------------------------------------
    # Messaging/Session API
    #--------------------------------------------------------------------------
    def handle_action(self, action, content):
        """ Handle an action sent from the server widget

        This is called by the WxClientSession object when the server
        widget sends a message to this widget.

        Parameters
        ----------
        action : str
            The action to be performed by the widget.

        content : ObjectDict
            The content dictionary for the action.

        """
        handler_name = 'on_action_' + action
        handler = getattr(self, handler_name, None)
        if handler is not None:
            handler(content)
        else:
            # XXX show a dialog here?
            msg = "Unhandled action sent to `%s` from server: %s"
            logging.warn(msg % (self.widget_id, action))

    def send_action(self, action, content):
        """ Send an action to the server widget.

        This method can be called to send an unsolicited message of
        type 'widget_action' to the server widget for this widget.

        Parameters
        ----------
        action : str
            The action for the message.

        content : dict
            The content of the message.

        """
        session = self.session
        if session is None:
            msg = 'No Session object for widget %s'
            logging.warn(msg % self.widget_id)
        else:
            session.send_action(self.widget_id, action, content)

    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------
    @property
    def parent(self):
        """ A read-only property which returns the parent of this widget.

        """
        return self._parent_ref()

    @property
    def parent_widget(self):
        """ A read-only property which returns the parent wx widget 
        for this client widget, or None if it has no parent.

        """
        parent = self.parent
        if parent is None:
            return None
        return parent.widget

    @property
    def loopback_guard(self):
        """ Lazily creates and returns a LoopbackGuard for convenient 
        use by subclasses.

        """
        try:
            guard = self._loopback_guard
        except AttributeError:
            guard = self._loopback_guard = LoopbackGuard()
        return guard

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ A method which must be implemented by subclasses.

        This method is called by the create(...) method. It should and
        return the underlying wx widget. Implementations of this method
        should *not* call the superclass version.

        Parameters
        ----------
        parent : wxWindow or None
            The parent wx widget for this control, or None if if the
            control does not have a parent.

        tree : dict
            The dictionary representation of the tree for this object.
            This is provided in the even that the component needs to 
            create a different type of widget based on the information
            in the tree.

        """
        raise NotImplementedError

    def create(self, tree):
        """ A method called by the application when creating the UI.

        The default implementation of this method calls 'create_widget'
        and assigns the results to the 'widget' attribute, so subclasses
        must be sure to call the superclass method as the first order of
        business.

        This method is called by the application in a top-down fashion.

        Parameters
        ----------
        tree : dict
            The dictionary representation of the tree for this object.

        """
        self.widget = self.create_widget(self.parent_widget, tree)

    def post_create(self):
        """ A method that allows widgets to do post creation work.

        This method is called after all widgets in a tree have had
        their 'create' method called. It is useful for doing any
        initialization where a widget must access its child widgets.

        The default implementation of this method is a no-op in order
        to be super() friendly.

        This method is called by the application in a top-down fashion.

        """
        pass

    def init_layout(self):
        """ A method that allows widgets to do layout initialization.

        This method is called after all widgets in a tree have had
        their 'post_create' method called. It is useful for doing any
        initialization related to layout.

        The default implementation of this method is a no-op in order
        to be super() friendly.

        This method is called by the application in a bottom-up order.
        
        """
        pass
        
    def destroy(self):
        """ Destroy this widget by removing all references to it from
        it parent and its children and destroy the underlying Wx widget.

        """
        parent = self.parent
        if parent is not None:
            if self in parent.children:
                parent.children.remove(self)
        self.children = []
        widget = self.widget
        if widget is not None:
            widget.Destroy()
            self.widget = None

