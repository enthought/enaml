#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import List, Instance, Bool

from enaml.core.declarative import Declarative
from enaml.core.object import Object, ChildrenEventContext


def _permutation(target, objects, obj_set, current):
    """ Compute the permutation for an Include.

    Parameters
    ----------
    target : Include
        The include which exists in `current` which is used as the
        key value for inserting `objects` into the permutation.

    objects : list
        The list of Objects which should be inserted after `target`.
        There must be no duplicates in this list.

    obj_set : set
        The set of `objects`.

    current : list
        The current list of objects on which the permutation is
        computed. There must be no duplicates in this list.

    """
    indices = {}
    for idx, curr in enumerate(current):
        indices[curr] = idx
    permutation = []
    for curr in current:
        if curr is target:
            permutation.append(indices[curr])
            for obj in objects:
                permutation.append(indices[obj])
        elif curr not in obj_set:
            permutation.append(indices[curr])
    return permutation


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

    def initialize(self):
        """ A reimplemented initialization method.

        This method ensures that the objects are added to the children
        of the parent and initialized.

        """
        parent = self.parent
        if parent is not None:
            # Update the children from within a child event context
            # to collapse multiple notifications into one.
            with ChildrenEventContext(parent):
                objects = self.objects
                obj_set = set(objects)
                if len(objects) != len(obj_set):
                    raise ValueError('Cannot include duplicate objects')
                # Use the `set_parent` api to ensure child validity. This
                # loop dwarfs the cost of the other operations when the
                # number of children is large.
                for obj in objects:
                    obj.set_parent(parent)
                # Compute and apply the permutation for the children to
                # place them in the correct position. The children are
                # placed immediately after the include.
                perm = _permutation(self, objects, obj_set, parent.children)
                parent.permute_children(perm)
                for obj in objects:
                    obj.initialize()

    # def _parent_changed(self, parent):
    #     """ A change handler for the `parent` of the Include.

    #     This handler will reparent the list of objects provided that
    #     the Include is fully initialized.

    #     """
    #     if self.initialized:
    #         objects = self.objects
    #         if parent is None:
    #             for child in objects:
    #                 child.set_parent(None)
    #         else:
    #             parent.insert_children(self, objects)

    def _objects_changed(self, old, new):
        """ A change handler for the `objects` list of the Include.

        """
        parent = self.parent
        if parent is not None:
            old_set = set(old)
            new_set = set(new)
            if len(new) != len(new_set):
                raise ValueError('Cannot include duplicate objects')
            add = new_set - old_set
            remove = old_set - new_set
            with ChildrenEventContext(parent):
                if self.destroy_old:
                    for obj in remove:
                        obj.destroy()
                else:
                    for obj in remove:
                        obj.set_parent(None)
                for obj in add:
                    obj.set_parent(parent)
                perm = _permutation(self, new, new_set, parent.children)
                parent.permute_children(perm)

    def _objects_items_changed(self, event):
        """ Handle the `objects` list changing in-place.

        This handler will replace the old children with the new children
        in a single atomic operation.

        """
        parent = self.parent
        if parent is not None:
            new = self.objects
            new_set = set(new)
            if len(new) != len(new_set):
                raise ValueError('Cannot include duplicate objects')
            removed_set = set(event.removed)
            added_set = set(event.added)
            add = added_set - removed_set
            remove = removed_set - added_set
            with ChildrenEventContext(parent):
                if self.destroy_old:
                    for obj in remove:
                        obj.destroy()
                else:
                    for obj in remove:
                        obj.set_parent(None)
                for obj in add:
                    obj.set_parent(parent)
                perm = _permutation(self, new, new_set, parent.children)
                parent.permute_children(perm)

