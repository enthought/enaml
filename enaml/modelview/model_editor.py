#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Any

from enaml.core.declarative import Declarative

from .edit_group import EditGroup


class ModelEditor(Declarative):
    """ A class for editing a model using `EditGroup` children.

    """
    #: The model object to edit with this editor. Subclasses may
    #: reimplement this trait.
    model = Any

    def edit_groups(self):
        """ Get the edit groups defined on this model editor.

        Returns
        -------
        result : generator
            A generator which will yield the children of the editor
            which are instances of `EditGroup`.

        """
        for child in self.children:
            if isinstance(child, EditGroup):
                yield child

