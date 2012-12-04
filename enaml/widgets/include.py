#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import List, Instance, Bool

from enaml.core.declarative import Declarative
from enaml.core.object import Object, ChildrenEventContext


class Include(Declarative):
    """ An object which dynamically inserts children into its parent.

    The Include object can be used to cleanly and easily insert objects
    into the children of its parent. Object assigned to the `objects`
    list of the Include will be parented by the parent of the Include.
    By default, an Include is not snappable and therefore acts like a
    shadow object with no client widget representation.

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
        self._update_parent(set(), set(self.objects))
        # XXX init nested Includes

    def parent_event(self, event):
        """ Handle a `ParentEvent` for the Include.

        If the object state is `active` the current include objects will
        be reparented to the new parent.

        """
        if self.is_active:
            new = event.new
            if new is None:
                if self.destroy_old:
                    for obj in self.objects:
                        obj.destroy()
                else:
                    for obj in self.objects:
                        obj.set_parent(None)
            else:
                self._update_parent(set(), set(self.objects))

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
                self._update_parent(set(old), set(new))

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
                self._update_parent(set(event.removed), set(event.added))

    def _update_parent(self, remove_set, add_set):
        """ Update the children of the parent.

        Parameters
        ----------
        remove_set : set
            The set of children to remove from the parent. This may
            overlap with `add_set`. Overlapping objects are ignored.

        add_set : set
            The set of children to add to the parent. This may overlap
            with `remove_set`. Overlapping objects are ignored.

        """
        parent = self.parent
        add = add_set - remove_set
        remove = remove_set - add_set
        parent = self.parent
        with ChildrenEventContext(parent):
            if self.destroy_old:
                for obj in remove:
                    obj.destroy()
            else:
                for obj in remove:
                    obj.set_parent(None)
            for obj in add:
                obj.set_parent(parent)
            parent.permute_children(self._permutation())
        # XXX init and activate new children if needed

    def _permutation(self):
        """ Compute the permutation for this Include.

        Returns
        -------
        result : list
            The permutation to apply to the parent so that its children
            appear in the desired order.

        """
        # Compute the current indices
        indices = {}
        children = self.parent.children
        for idx, child in enumerate(children):
            indices[child] = idx

        # Filter the current objects for duplicates
        obj_set = set()
        objects = []
        for obj in self.objects:
            if obj not in obj_set:
                obj_set.add(obj)
                objects.append(obj)

        # Compute the permuted indices
        permutation = []
        for child in children:
            if child is self:
                permutation.append(indices[child])
                for obj in objects:
                    permutation.append(indices[obj])
            elif child not in obj_set:
                permutation.append(indices[child])

        return permutation

