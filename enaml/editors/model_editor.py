#------------------------------------------------------------------------------
# Copyright (c) 2013, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Any

from enaml.core.declarative import Declarative

from .editor_group import EditorGroup


class ModelEditor(Declarative):
    """ A class for conveniently declaring editors for a model.

    A `ModelEditor` works in conjuction with one or more `EditorGroup`
    children to define the editor items available for a given model.

    """
    #: The model object associated with the editor. Subclasses may
    #: redefine this traits to enforce more strict type checking.
    model = Any

    def editor_groups(self):
        """ Get the editor groups defined on this model editor.

        Returns
        -------
        result : generator
            A generator which will yield the children of the model
            editor which are instances of `EditorGroup`.

        """
        for child in self.children:
            if isinstance(child, EditorGroup):
                yield child

