#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Instance, Uninitialized

from enaml.utils import LoopbackGuard

from .declarative import Declarative
from .object import Object


class PublishAttributeNotifier(object):
    """ A lightweight trait change notifier used by Messenger.

    """
    def __call__(self, obj, name, old, new):
        """ Called by traits to dispatch the notifier.

        """
        if old is not Uninitialized and name not in obj.loopback_guard:
            obj.send_action('set_' + name, {name: new})

    def equals(self, other):
        """ Compares this notifier against another for equality.

        """
        return False

# Only a single instance of PublishAttributeNotifier is needed.
PublishAttributeNotifier = PublishAttributeNotifier()


class ChildrenChangedTask(object):
    """ A task for posting a children changed event to a client.

    Instances of this class can be posted to the `batch_action_task`
    method of Object to send a 'children_changed' action to a client
    object. This task will ensure that new children are initialized
    and activated using session object of the provided parent.

    """
    def __init__(self, parent, event):
        """ Initialize a ChildrenChangedTask.

        Parameters
        ----------
        parent : Object
            The object to which the children event was posted.

        event : ChildrenEvent
            The children event posted to the parent.

        """
        self._parent = parent
        self._event = event

    def __call__(self):
        """ Create the content dictionary for the task.

        This method will also initialize and activate any new objects
        which were added to the parent.

        """
        event = self._event
        content = {}
        new_set = set(event.new)
        old_set = set(event.old)
        added = new_set - old_set
        removed = old_set - new_set
        for obj in added:
            if obj.is_inactive:
                obj.initialize()
        content['order'] = [
            c.object_id for c in event.new if isinstance(c, Messenger)
        ]
        content['removed'] = [
            c.object_id for c in removed if isinstance(c, Messenger)
        ]
        content['added'] = [
            c.snapshot() for c in added if isinstance(c, Messenger)
        ]
        session = self._parent.session
        for obj in added:
            if obj.is_initialized:
                obj.activate(session)
        return content


class Messenger(Declarative):
    """ A base class for creating messaging enabled Enaml objects.

    This is a Declarative subclass which provides convenient APIs for
    sharing state between a server-side Enaml object and a client-side
    implementation of that object.

    """
    #: A loopback guard which can be used to prevent a notification
    #: cycle when setting attributes from within an action handler.
    loopback_guard = Instance(LoopbackGuard, ())

    #--------------------------------------------------------------------------
    # Lifetime API
    #--------------------------------------------------------------------------
    def post_initialize(self):
        """ A reimplemented post initialization method.

        This method calls the `bind` method after calling the superclass
        class version.

        """
        super(Messenger, self).post_initialize()
        self.bind()

    def bind(self):
        """ Called during initialization pass to bind change handlers.

        This method is called at the end of widget initialization to
        provide a subclass the opportunity to setup any required change
        notification handlers for publishing their state to the client.

        """
        pass

    #--------------------------------------------------------------------------
    # Snapshot API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Get a dictionary representation of the widget tree.

        This method can be called to get a dictionary representation of
        the current state of the widget tree which can be used by client
        side implementation to construct their own implementation tree.

        Returns
        -------
        result : dict
            A serializable dictionary representation of the widget tree
            from this widget down.

        """
        snap = {}
        snap['object_id'] = self.object_id
        snap['name'] = self.name
        snap['class'] = self.class_name()
        snap['bases'] = self.base_names()
        snap['children'] = [c.snapshot() for c in self.snap_children()]
        return snap

    def snap_children(self):
        """ Get an iterable of children to include in the snapshot.

        The default implementation returns the list of children which
        are instances of Messenger. Subclasses may reimplement this
        method if more control is needed.

        Returns
        -------
        result : list
            The list of children which are instances of Messenger.

        """
        return [c for c in self.children if isinstance(c, Messenger)]

    def class_name(self):
        """ Get the name of the class for this instance.

        Returns
        -------
        result : str
            The name of the class of this instance.

        """
        return type(self).__name__

    def base_names(self):
        """ Get the list of base class names for this instance.

        Returns
        -------
        result : list
            The list of string names for the base classes of this
            instance. The list starts with the parent class of this
            instance and terminates with Object.

        """
        names = []
        for base in type(self).mro()[1:]:
            names.append(base.__name__)
            if base is Object:
                break
        return names

    #--------------------------------------------------------------------------
    # Messaging Support
    #--------------------------------------------------------------------------
    def set_guarded(self, **attrs):
        """ Set attribute values from within a loopback guard.

        This is a convenience method provided for subclasses to set the
        values of attributes from within a loopback guard. This prevents
        the change from being published back to client and reduces the
        chances of getting hung in a feedback loop.

        Parameters
        ----------
        **attrs
            The attributes to set on the object from within a loopback
            guard context.

        """
        with self.loopback_guard(*attrs):
            for name, value in attrs.iteritems():
                setattr(self, name, value)

    def publish_attributes(self, *attrs):
        """ A convenience method provided for subclasses to publish
        attribute changes as actions to the client.

        The action name is created by prefixing 'set_' to the name of
        the changed attribute. This method is suitable for most cases
        of simple attribute publishing. More complex cases will need
        to implement their own dispatching handlers. The handler for
        the changes will only send the action message if the attribute
        name is not held by the loopback guard.

        Parameters
        ----------
        *attrs
            The string names of the attributes to publish to the client.
            The values of these attributes should be JSON serializable.
            More complex values should use their own dispatch handlers.

        """
        for attr in attrs:
            self.add_notifier(attr, PublishAttributeNotifier)

    def children_event(self, event):
        """ Handle a `ChildrenEvent` for the widget.

        If the widget state is 'active', a `children_changed` action
        will be sent to the client widget. The action is sent before
        the superclass' handler is called, and will therefore precede
        the trait change notification.

        """
        super(Messenger, self).children_event(event)
        # Children events are fired all the time during initialization,
        # so only batch the children task if the widget is activated.
        # The children may not be fully instantiated when this event is
        # fired, and they may still be executing their constructor. The
        # batched task allows the children to finish initializing before
        # their snapshot is taken.
        if self.is_active:
            task = ChildrenChangedTask(self, event)
            self.batch_action_task('children_changed', task)

