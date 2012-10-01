#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, List, Either, Int, Enum, Property, cached_property

from .constraints_widget import ConstraintsWidget
from .container import Container


class Splitter(ConstraintsWidget):
    """ A widget which displays its children in separate resizable 
    compartements that are connected with a resizing bar.
     
    A Splitter can have an arbitrary number of Container children.

    """
    #: The orientation of the Splitter. 'horizontal' means the children 
    #: are laid out left to right, 'vertical' means top to bottom.
    orientation = Enum('horizontal', 'vertical')

    #: Whether the child widgets resize as a splitter is being dragged
    #: (True), or if a simple indicator is drawn until the drag handle
    #: is released (False). The default is True.
    live_drag = Bool(True)
    
    #: A list of preferred sizes for each compartment of the splitter, 
    #: or None if there is no preference for the size.
    preferred_sizes = List(Either(None, Int))
    
    #: A read only property which returns the splitter widgets being
    #: managed by the splitter.
    splitter_widgets = Property(depends_on='children')

    #: How strongly a component hugs it's contents' width. A Splitter
    #: container ignores its width hug by default, so it expands freely
    #: in width.
    hug_width = 'ignore'

    #: How strongly a component hugs it's contents' height. A Splitter
    #: container ignores its height hug by default, so it expands freely
    #: in height.
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the dict of creation attributes for the control.

        """
        snap = super(Splitter, self).snapshot()
        snap['orientation'] = self.orientation
        snap['live_drag'] = self.live_drag
        snap['preferred_sizes'] = self.preferred_sizes
        return snap

    def bind(self):
        """ Bind the change handlers for the widget.

        """
        super(Splitter, self).bind()
        self.publish_attributes('orientation', 'live_drag', 'preferred_sizes')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_splitter_widgets(self):
        """ The getter for the 'splitter_widgets' property.

        Returns
        -------
        result : tuple
            The tuple of Container instances defined as children of 
            this Splitter.

        """
        isinst = isinstance
        pages = (child for child in self.children if isinst(child, Container))
        return tuple(pages)

