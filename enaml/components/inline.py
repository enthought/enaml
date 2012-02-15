#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Property, on_trait_change

from ..core.base_component import BaseComponent


class Inline(BaseComponent):
    """ A BaseComponent subclass which allows children to be statically
    inlined into a parent.

    """
    #: A read-only property which returns the toolkit widget for this
    #: component. This call is proxied to the parent and will return
    #: None if the parent does not have a toolkit widget defined. 
    #: It is necessary to proxy the toolkit_widget so that any child
    #: Include components can access the proper toolkit widget to 
    #: pass down to their dynamic components.
    toolkit_widget = Property

    #--------------------------------------------------------------------------
    # Property Getters
    #--------------------------------------------------------------------------
    def _get_toolkit_widget(self):
        """ The property getter for the 'toolkit_widget' attribute.

        """
        try:
            res = self.parent.toolkit_widget
        except AttributeError:
            res = None
        return res

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def get_actual(self):
        """ A reimplemented parent class method which returns the inlined
        subcomponents for this component.

        """
        return sum([c.get_actual() for c in self._subcomponents], [])

    #--------------------------------------------------------------------------
    # Change Handlers
    #--------------------------------------------------------------------------
    @on_trait_change('_subcomponents:_actual_updated')
    def handle_actual_updated(self):
        """ Handles the '_actual_updated' event being fired on any of the
        subcomponents. It proxies this event up to the parent so that it
        can request the new children and relayout if necessary.

        """
        self._actual_updated()

