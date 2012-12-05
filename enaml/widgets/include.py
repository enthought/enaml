#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import List, Instance, Bool

from enaml.core.declarative import Declarative
from enaml.core.object import Object, ChildrenEventContext


class Include(Declarative):
    """ An object which dynamically inserts children into its parent.

    The `Include` object is used to cleanly and easily insert objects
    into the children of its parent. `Object` instances assigned to the
    `objects` list of the `Include` will be parented with the parent of
    the `Include`. The parent of an `Include` should be an instance of
    `WidgetBase`; if this condition does not hold, the behavior will be
    undefined.

    """
    #: The list of objects belonging to this Include. Objects in this
    #: list will be automatically parented with the Include's parent.
    objects = List(Instance(Object))

    #: A boolean flag indicating whether to destroy the old objects that
    #: are removed from the parent. The default is True.
    destroy_old = Bool(True)

    def init_objects(self):
        """ A method called by a parent widget to init the Include.

        This method must be called by objects to initialize the objects
        in an Include. It should be called before the parent initializes
        its children. This method should never be called by user code.

        """
        self.parent.insert_children(self, self.objects)

    def parent_event(self, event):
        """ Handle a `ParentEvent` for the Include.

        If the object state is `active` the current include objects will
        be reparented to the new parent.

        """
        if self.is_active:
            old = event.old
            new = event.new
            with ChildrenEventContext(new):
                with ChildrenEventContext(old):
                    if new is None:
                        for obj in self.objects:
                            obj.set_parent(None)
                    else:
                        new.insert_children(self, self.objects)

    def _objects_changed(self, old, new):
        """ A change handler for the `objects` list of the Include.

        If the object state is 'active' objects which are removed will
        be unparented and objects which are added will be reparented.
        Old objects will be destroyed if the `destroy_old` flag is set
        to True.

        """
        if self.is_active:
            parent = self.parent
            if parent is not None:
                with ChildrenEventContext(parent):
                    new_set = set(new)
                    if self.destroy_old:
                        for obj in old:
                            if obj not in new_set:
                                obj.destroy()
                    else:
                        for obj in old:
                            if obj not in new_set:
                                obj.set_parent(None)
                    if new_set:
                        parent.insert_children(self, self.objects)
                        self._activate_objects(new_set)

    def _objects_items_changed(self, event):
        """ Handle the `objects` list changing in-place.

        If the object state is 'active' objects which are removed will
        be unparented and objects which are added will be reparented.
        Old objects will be destroyed if the `destroy_old` flag is set
        to True.

        """
        if self.is_active:
            parent = self.parent
            if parent is not None:
                with ChildrenEventContext(parent):
                    add_set = set(event.added)
                    if self.destroy_old:
                        for obj in event.removed:
                            if obj not in add_set:
                                obj.destroy()
                    else:
                        for obj in event.removed:
                            if obj not in add_set:
                                obj.set_parent(None)
                    if add_set:
                        parent.insert_children(self, self.objects)
                        self._activate_objects(add_set)

    def _activate_objects(self, objects):
        """ Initialize and activate the given objects.

        Parameters
        ----------
        objects : iterable
            An iterable of objects which should be initialized and
            activated. Objects which are already active are ignored.

        """
        for obj in objects:
            if obj.is_inactive:
                obj.initialize()
        session = self.session
        for obj in objects:
            if obj.is_initialized:
                obj.activate(session)

