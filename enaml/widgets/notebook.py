#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum, Bool, Property, cached_property

from .constraints_widget import ConstraintsWidget
from .page import Page


class Notebook(ConstraintsWidget):
    """ A component which displays its children as tabbed pages.
    
    """
    #: The style of tabs to use in the notebook. Preferences style
    #: tabs are appropriate for configuration dialogs and the like.
    #: Document style tabs are appropriate for multi-page editing
    #: in code editors and the like.
    tab_style = Enum('document', 'preferences')

    #: The position of tabs in the notebook.
    tab_position = Enum('top', 'bottom', 'left', 'right')

    #: Whether or not the tabs in the notebook should be closable.
    tabs_closable = Bool(True)

    #: Whether or not the tabs in the notebook should be movable.
    tabs_movable = Bool(True)

    #: A read only property which returns the notebook's Pages.
    pages = Property(depends_on='children')

    #: How strongly a component hugs it's contents' width. A Notebook
    #: ignores its width hug by default, so it expands freely in width.
    hug_width = 'ignore'

    #: How strongly a component hugs it's contents' height. A Notebook
    #: ignores its height hug by default, so it expands freely in height.
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot for the control.

        """
        snap = super(Notebook, self).snapshot()
        snap['tab_style'] = self.tab_style
        snap['tab_position'] = self.tab_position
        snap['tabs_closable'] = self.tabs_closable
        snap['tabs_movable'] = self.tabs_movable
        return snap

    def bind(self):
        """ Bind the change handlers for the control.

        """
        super(Notebook, self).bind()
        attrs = (
            'tab_style', 'tab_position', 'tabs_closable', 'tabs_movable',
        )
        self.publish_attributes(*attrs)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_pages(self):
        """ The getter for the 'pages' property.

        Returns
        -------
        result : tuple
            The tuple of Page instances defined as children of this
            Notebook.

        """
        isinst = isinstance
        pages = (child for child in self.children if isinst(child, Page))
        return tuple(pages)

