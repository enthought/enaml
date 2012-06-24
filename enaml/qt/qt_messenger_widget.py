#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from weakref import ref

from enaml.utils import WeakMethodWrapper


class QtMessengerWidget(object):
    """ The base class of the Qt widgets wrappers for a Qt Enaml client.

    """
    def __init__(self, parent, send_pipe, recv_pipe):
        """ Initialize a QtClientWidget

        Parameters
        ----------
        parent : QtClientWidget or None
            The parent client widget of this widget, or None if this
            client widget has no parent.

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
            parent.add_child(self)
        self.send_pipe = send_pipe
        self.recv_pipe = recv_pipe
        self.widget = None
        self.children = []
        callback = WeakMethodWrapper(self.recv)
        self.recv_pipe.set_callback(callback)

    def send(self, msg, ctxt):
        """ Send a message to be handled by the Enaml widget.
        
        The message is placed on the send pipe for later delivery to
        the Enaml widget on the other side. The return value is an 
        asynchronous reply object which can provide notification when 
        the message is finished.

        Parameters
        ----------
        msg : string
            The message to be sent to the Enaml widget.
            
        ctxt : dict
            The argument context for the message.

        Returns
        -------
        result : AsyncReply
            An asynchronous reply object for the given message. When
            the Enaml widget has finished processing the message, this 
            async reply will notify any registered callbacks.

        """
        return self.send_pipe.put(msg, ctxt)

    def recv(self, msg, ctxt):
        """ Handle a message sent by the Enaml widget.
        
        This method is called by the recv pipe when there is a message 
        from the Enaml widget ready to be handled.
        
        This method will dispatch the message to methods defined on a 
        subclass by prefixing the command name with 'receive_'. 

        In order to handle a message named e.g. 'set_label', a sublass 
        should define a method with the name 'receive_set_label' which 
        takes a single argument which is the context dictionary for the 
        message. 

        Exceptions raised in a handler are propagated.
        
        Parameters
        ----------
        msg : string
            The message to be handled by the widget.
            
        ctxt : dict
            The context dictionary for the message.

        Returns
        -------
        result : object or NotImplemented
            The return value of the message handler or NotImplemented
            if this object does not define a handler for the message.

        """
        handler_name = 'receive_' + msg
        handler = getattr(self, handler_name, None)
        if handler is not None:
            return handler(ctxt)
        return NotImplemented

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

    def add_child(self, child):
        """ Add a child to this widget. This is called by a child widget
        when it is parented.

        """
        self.children.append(child)

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self):
        """ A method called by the builder in order to create the 
        underlying QWidget object.

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

