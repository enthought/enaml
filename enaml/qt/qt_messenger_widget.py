#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from weakref import ref

from enaml.async.messenger_mixin import MessengerMixin


class QtMessengerWidget(MessengerMixin):
    """ The base class of the Qt widgets wrappers for a Qt Enaml client.

    """
    def __init__(self, parent, target_id, async_pipe):
        """ Initialize a QtClientWidget

        Parameters
        ----------
        parent : QtMessengerWidget or None
            The parent client widget of this widget, or None if this
            client widget has no parent.

        target_id : str
            A string which identifies the target Enaml widget with
            which this widget will communicate.

        async_pipe : AsyncPipe
            The async pipe to use for messaging with the Enaml widget.

        """
        self._parent_ref = ref(parent) if parent is not None else lambda: None
        self.widget = None
        self.children = []
        self.target_id = target_id
        self.async_pipe = async_pipe
        async_pipe.set_message_callback(target_id, self.recv_message)
        async_pipe.set_request_callback(target_id, self.recv_request)
        if parent is not None:
            parent.children.append(self)

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
        """ A method which must be implemented by subclasses. 

        This method should create the underlying QWidget object and 
        assign it to the 'widget' attribute. Implementations of this
        method should *not* call the superclass version.

        """
        raise NotImplementedError

    def initialize(self, attributes):
        """ A method called to initialize the attributes of the 
        underlying widget.

        The default implementation of this method is a no-op in order
        to be super() friendly. Implementations of this method should
        call the superclass version to make sure that all attributes
        get properly initialized.

        This method will be called after all other widgets for the
        creation pass have been created.

        Parameters
        ----------
        attributes : dict
            The dictionary of attributes that was contained in the
            payload of the operation for the 'create' action which
            created this widget.

        """
        pass

    def post_initialize(self):
        """ A method that allows widgets to do post initialization work.

        This method is called after all widgets in a creation pass have
        had their 'initialize' method called. It is useful for e.g.
        layout initialization, which requires that all child widgets
        have their attributes already initialized.

        The default implementation of this method is a no-op in order
        to be super() friendly. Implementations of this method should
        call the superclass version to make sure that all post
        initialization is properly performed.

        """
        pass

    def destroy(self):
        """ Destroy this widget by removing all references to it from
        it parent and its children and destroy the underlying Qt widget.

        """
        parent = self.parent
        if parent is not None:
            if self in parent.children:
                parent.children.remove(self)
        self.children = []
        widget = self.widget
        if widget is not None:
            widget.destroy()
            self.widget = None

