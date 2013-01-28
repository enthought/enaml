#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import List

from .declarative import Declarative, setup_bindings


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
    # Declarative API
    #--------------------------------------------------------------------------
    def populate(self, description, identifiers, f_globals):
        """ An overridden parent class populator.

        A `Templated` object never actually constructs its children.
        Instead, the child descriptions are used as templates by the
        various subclasses to generate objects at runtime. This method
        simply creates the object, initializes the bindings, and stores
        the children information in the templates list.

        """
        ident = description['identifier']
        if ident:
            identifiers[ident] = self
        bindings = description['bindings']
        if len(bindings) > 0:
            setup_bindings(self, bindings, identifiers, f_globals)
        children = description['children']
        if len(children) > 0:
            template = (identifiers, f_globals, children)
            self._templates.append(template)

