#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Bool, Enum, Property, cached_property

from .constraints_widget import ConstraintsWidget
from .split_item import SplitItem


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
    
    #: A read only property which returns the split items being managed
    #: by the splitter.
    split_items = Property(depends_on='children')

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
        return snap

    def bind(self):
        """ Bind the change handlers for the widget.

        """
        super(Splitter, self).bind()
        self.publish_attributes('orientation', 'live_drag')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_split_items(self):
        """ The getter for the 'split_items' property.

        Returns
        -------
        result : tuple
            The tuple of SplitItem instances defined as children of
            this Splitter.

        """
        isinst = isinstance
        items = (child for child in self.children if isinst(child, SplitItem))
        return tuple(items)

