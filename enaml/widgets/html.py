#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Str, on_trait_change

from .control import Control


class Html(Control):
    """ An extremely simple widget for displaying HTML.
    
    """
    #: The Html source code to be rendered.
    source = Str
    
    #: How strongly a component hugs it's contents' width. Html widgets 
    # ignore the width hug by default, so they expand freely in width.
    hug_width = 'ignore'
    
    #: How strongly a component hugs it's contents' height. Html widgets
    #: ignore the height hug by default, so they expand freely in height.
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Toolkit Communication
    #--------------------------------------------------------------------------
    @on_trait_change('source')
    def sync_object_state(self, name, new):
        """ Notify the client component of updates to the object state.

        """
        msg = 'set_' + name
        self.send(msg, {'value':new})

    def initial_attrs(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(Html, self).initial_attrs()
        attrs = {
            'source' : self.source
        }
        super_attrs.update(attrs)
        return super_attrs

