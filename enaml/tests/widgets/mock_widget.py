#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import logging
import re
from types import MethodType

logger = logging.getLogger(__name__)

def make_handler_func(func_name, name, obj):
    func = lambda slf, ctxt: setattr(slf, name, ctxt['value'])
    func.func_name = func_name
    return MethodType(func, obj)


class MockWidget(object):
    """ A mock client UI widget

    """

    _objects = {}

    @classmethod
    def lookup_object(cls, object_id):
        """ A classmethod which finds the object with the given id.

        Parameters
        ----------
        object_id : str
            The identifier for the object to lookup.

        Returns
        -------
        result : QtObject or None
            The QtObject for the given identifier, or None if no object
            is found.

        """
        return cls._objects.get(object_id)

    @classmethod
    def construct(cls, tree, parent, pipe, builder):
        """ Construct the QtObject instance for the given parameters.

        This classmethod is called by the QtBuilder object used by the
        application. When called, it will create a new instance of the
        class by extracting the object id from the snapshot and calling
        the class constructor. It then invokes the `create` method on
        the new instance. This classmethod exists for cases where it is
        necessary to define custom construction behavior. A subclass
        may reimplement this method as required.

        Parameters
        ----------
        tree : dict
            An Enaml snapshot dict representing an object tree from this
            object downward.

        parent : QtObject or None
            The parent QtObject to use for this object, or None if this
            object is top-level.

        pipe : QActionPipe or None
            The QActionPipe to use for sending messages to the Enaml
            object, or None if messaging is not desired.

        builder : QtBuilder
            The QtBuilder instance that is building this object.

        Returns
        -------
        result : QtObject
            The QtObject instance for these parameters.

        Notes
        -----
        This method does *not* construct the children for this object.
        That responsibility lies with the QtBuilder object which calls
        this constructor.

        """
        object_id = tree['object_id']
        self = cls.lookup_object(object_id)
        if self is None:
            self = cls(object_id, parent, pipe, builder)
        self.create(tree)
        return self

    def __new__(cls, object_id, *args, **kwargs):
        """ Create a new QtObject.

        """
        if object_id in cls._objects:
            raise ValueError('Duplicate object id')
        self = super(MockWidget, cls).__new__(cls)
        cls._objects[object_id] = self
        return self

    def __init__(self, object_id, parent, pipe, builder):
        """ Initialize a MockWidget

        Parameters
        ----------
        parent : QtMessengerWidget or None
            The parent widget of this widget, or None if this widget has
            no parent.

        widget_id : str
            The identifier string for this widget.

        session : QtClientSession
            The client session object to use for communicating with the
            server widget.

        """
        self._object_id = object_id
        self._pipe = pipe
        self._builder = builder
        self._parent = parent
        self._children = []
        self._children_map = {}
        self._widget = None
        self._initialized = False

    #--------------------------------------------------------------------------
    # Public API (stolen from the QtMessengerWidget)
    #--------------------------------------------------------------------------
    def parent(self):
        """ Get the parent of this messenger widget.

        Returns
        -------
        result : QtMessengerWidget or None
            The parent of this messenger widget, or None if it has
            no parent.

        """
        return self._parent

    def children(self):
        """ Get the children of this widget.

        Returns
        -------
        result : list
            The list of children of this widget. This list should not
            be modified in place by user code.

        """
        return [MockWidget.lookup_object(child['object_id']) for child in self._children]

    def widget(self):
        """ Get the toolkit widget for this widget.

        Returns
        -------
        result : QWidget
            The toolkit widget for this messenger widget, or None if
            it does not have a toolkit widget.

        """
        return self._widget


    def widget_type(self):
        """ Returns the widget type for this widget.

        Returns
        -------
        result: str
            The widget type (meaning the class name of the server side widget)

        """

        return self._widget['class']


    def widget_id(self):
        """ Get the widget id for the messenger widget.

        Returns
        -------
        result : str
            The widget identifier for this messenger widget.

        """
        return self._object_id

    def create_widget(self, parent, tree):
        """ A method which must be implemented by subclasses.

        This method is called by the create(...) method. It should 
        create and return the underlying Qt widget. Implementations 
        of this method should *not* call the superclass version.

        Parameters
        ----------
        parent : QWidget or None
            The parent Qt widget for this control, or None if if the
            control does not have a parent.

        tree : dict
            The dictionary representation of the tree for this object.
            This is provided in the even that the component needs to 
            create a different type of widget based on the information
            in the tree.

        """
        return tree

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
        parent = self._parent
        parent_widget = parent.widget() if parent else None
        self._widget = self.create_widget(parent_widget, tree)

        # The builder takes care of creating the object. Just keep a reference
        # to tree['children'] 
        self._children = tree['children']

    def init_layout(self):
        """ A method that allows widgets to do layout initialization.

        This method is called after all widgets in a tree have had
        their 'create' method called. It is useful for doing any
        initialization related to layout.

        The default implementation of this method is a no-op in order
        to be super() friendly.

        This method is called by the application in a bottom-up order.

        """
        pass

    def destroy(self):
        """ Destroy this widget.
        """
        pass


    def __getattr__(self, name):
        """ When trying to resolve attributes that are part of the
        widget it self, parse the tree and return the related value if any.
        """

        widget = self.widget()
        if widget is not None and name in widget:
            return widget[name]

        res = re.match('on_action_(.*?)_(.*)', name)
        if res is not None:
            action, attribute = res.groups()
            # Dirty hack to generate the setter in the MockWidget
            if action == 'set':
                def set_attribute(value):
                    self._widget[attribute] = value[attribute]
                return set_attribute

        res = re.match('on_action_(.*?)', name)
        if res is not None:
            action = res.groups()
            def fun(self):
                return True
            self._widget[action] = fun
            return self._widget[action]


    #--------------------------------------------------------------------------
    # Messaging/Session API
    #--------------------------------------------------------------------------
    def handle_action(self, action, content):
        """ Handle an action sent from the server widget

        This is called by the QtClientSession object when the server
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
            logger.error(msg % (self.widget_id(), action))


