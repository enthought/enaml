#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import List

from .declarative import Declarative


class Templated(Declarative):
    """ A declarative which serves as a base class for templated types.

    The `Templated` class serves as a base class for classes such as
    `Looper` and `Conditional` which never create their children, but
    the descriptions of their children as templates for generating new
    objects at runtime.

    """
    #: Private storage for the templates used to create items.
    _templates = List

    #--------------------------------------------------------------------------
    # Lifetime API
    #--------------------------------------------------------------------------
    def post_destroy(self):
        """ A post destroy handler.

        The templated item will release all of its templates after it
        has been destroyed.

        """
        super(Templated, self).post_destroy()
        self._templates = []

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @classmethod
    def _construct(cls, parent, description, identifiers, f_globals):
        """ An overridden parent class constructor.

        A `Templated` object never actually constructs its children.
        Instead, the child descriptions are used as templates by the
        various subclasses to generate objects at runtime. This method
        simply creates the object, initializes the bindings, and stores
        the children information in the templates list.

        """
        # Note: if `cls` is an EnamlDef, it may have its own description
        # which will trigger a population round from another scope.
        self = cls(parent)

        # Add this instance to the identifiers if needed.
        ident = description['identifier']
        if ident:
            identifiers[ident] = self

        # Setup the bindings for the item.
        bindings = description['bindings']
        if len(bindings) > 0:
            self._setup_bindings(bindings, identifiers, f_globals)

        # Store the child descriptions as templates.
        children = description['children']
        if len(children) > 0:
            template = (identifiers, f_globals, children)
            self._templates.append(template)

        return self

    def _populate(self, descriptions):
        """ An overridden parent class populator.

        See the documentation for the `_construct` classmethod. These
        two methods perform a similar task, but `_populate` will only
        be invoked if the object has been subclassed via enamldef.

        """
        for description, f_globals in descriptions:
            # Each description represents an enamldef block. Each block
            # gets its own independent identifier scope.
            identifiers = {}

            # Add this item to the identifier scope.
            ident = description['identifier']
            if ident:
                identifiers[ident] = self

            # Setup the bindings for the item.
            bindings = description['bindings']
            if len(bindings) > 0:
                self._setup_bindings(bindings, identifiers, f_globals)

            # Store the child descriptions as templates.
            children = description['children']
            if len(children) > 0:
                template = (identifiers, f_globals, children)
                self._templates.append(template)

