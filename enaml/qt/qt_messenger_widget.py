#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from weakref import ref

from enaml.async.messenger_mixin import MessengerMixin


class QtMessengerWidget(MessengerMixin):
    """ The base class of the Qt widgets wrappers for a Qt Enaml client.

    """
    def __init__(self, parent, target_id, send_pipe, recv_pipe):
        """ Initialize a QtClientWidget

        Parameters
        ----------
        parent : QtClientWidget or None
            The parent client widget of this widget, or None if this
            client widget has no parent.

        target_id : str
            A string which identifies the target Enaml widget with
            which this widget will communicate.

        send_pipe : AsyncSendPipe
            The async send pipe used to send messages to the Enaml
            widget on the other end.

        recv_pipe : AsyncRecvPipe
            The async recv pipe used to recv messages from the Enaml
            widget on the other end.

        """
        if parent is None:
            self.__parent_ref = lambda: None
        else:
            self.__parent_ref = ref(parent)
            parent.children.add(self)
        self.widget = None
        self.children = set()
        self.target_id = target_id
        self.send_pipe = send_pipe
        self.recv_pipe = recv_pipe
        
    #--------------------------------------------------------------------------
    # Properties
    #--------------------------------------------------------------------------
    @property
    def widget_type(self):
        """ A read-only property which provides the name of this widget
        type, which is simply the name of this class.

        """
        return type(self).__name__

    @property
    def parent(self):
        """ A read-only property which returns the parent client widget
        for this client widget, or None if this widget has no parent.

        """
        return self.__parent_ref()

    @property
    def parent_widget(self):
        """ A read-only property which returns the parent qt widget 
        for this client widget, or None if it has no parent.

        """
        parent = self.parent
        if parent is None:
            return None
        return parent.widget

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def create(self):
        """ A method which must be implemented by subclasses. It should
        create the underlying QWidget object.

        """
        raise NotImplementedError

    def initialize(self, init_attrs):
        """ A method called by the builder in order to initialize the
        attributes of the underlying QWidget object.

        """
        pass

    def bind(self):
        """ A method called by the builder in order to bind any required
        signal/event handlers for the underlying QWidget object.

        """
        pass

    def initialize_layout(self):
        """ A method called by the builder after the entire tree has
        been built. Subclasses should implement this method if they
        need to do layout initialization.

        """
        pass

    def init_messaging(self):
        """ A method called by the builder after layout as been inited.
        and which binds the receiving handlers for the pipes.

        """
        # XXX not sure if I like this at the moment.
        self.bind_recv_handlers()
        for child in self.children:
            child.init_messaging()
            
