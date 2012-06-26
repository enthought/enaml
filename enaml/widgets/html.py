#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Str

from .constraints_widget import ConstraintsWidget


class Html(ConstraintsWidget):
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
    # Initialization
    #--------------------------------------------------------------------------
    def bind(self):
        """ A method called after initialization which allows the widget
        to bind any event handlers necessary.

        """
        super(Html, self).bind()
        self.default_send('source')

    def initial_attrs(self):
        """ Return a dictionary which contains all the state necessary to
        initialize a client widget.

        """
        super_attrs = super(Html, self).initial_attrs()
        attrs = {'source' : self.source}
        super_attrs.update(attrs)
        return super_attrs

