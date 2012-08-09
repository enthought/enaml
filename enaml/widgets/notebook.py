#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Enum, Bool, Property, cached_property

from enaml.core.trait_types import EnamlEvent

from .constraints_widget import ConstraintsWidget
from .page import Page


class Notebook(ConstraintsWidget):
    """ A component which displays its children as tabbed pages.

    """
    #: The position of tabs in the notebook.
    tab_position = Enum('top', 'bottom', 'left', 'right')

    #: The style of the tabs to use in the notebook. This may not
    #: be supported on all platforms. The 'document' style is used
    #: when displaying many pages in an editing context such as in
    #: an IDE. The 'preferences' style is used to display tabs in
    #: a style that is appropriate for a preferences dialog.
    tab_style = Enum('document', 'preferences')

    #: Whether or not the tabs in the notebook should be closable.
    tabs_closable = Bool(True)

    #: Whether or not the tabs in the notebook should be movable.
    tabs_movable = Bool(True)

    #: An event fired when the user closes a tab by clicking on its
    #: close button. The content will be the page object.
    tab_closed = EnamlEvent

    #: A read only property which returns the notebook's Pages.
    pages = Property(depends_on='children[]')

    #: How strongly a component hugs it's contents' width. A TabGroup
    #: ignores its width hug by default, so it expands freely in width.
    hug_width = 'ignore'

    #: How strongly a component hugs it's contents' height. A TabGroup
    #: ignores its height hug by default, so it expands freely in height.
    hug_height = 'ignore'

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the dict of creation attributes for the control.

        """
        snap = super(Notebook, self).snapshot()
        snap['page_ids'] = self._snap_page_ids()
        snap['tab_position'] = self.tab_position
        snap['tab_style'] = self.tab_style
        snap['tabs_closable'] = self.tabs_closable
        snap['tabs_movable'] = self.tabs_movable
        return snap

    def bind(self):
        """ Bind the change handlers for the control.

        """
        super(Notebook, self).bind()
        attrs = ('tab_position', 'tab_style', 'tabs_closable', 'tabs_movable')
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

    def _snap_page_ids(self):
        """ Returns the widget ids of the notebook's pages.

        """
        return [page.widget_id for page in self.pages]

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_tab_closed(self, content):
        """ Handle the 'tab_closed' action from the client widget.

        """
        widget_id = content['widget_id']
        for page in self.pages:
            if page.widget_id == widget_id:
                self.tab_closed(page)
                page.closed()
                return

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def open_tab(self, page):
        """ Open the tab for the given page, if it isn't already open.

        Parameters
        ----------
        page : Page
            The page instance to open. It must be owned by this 
            Notebook.

        """
        if page not in self.pages:
            msg = 'Page is not owned by this Notebook'
            raise ValueError(msg)
        content = {'widget_id': page.widget_id}
        self.send_action('open_tab', content)

    def close_tab(self, page):
        """ Close the tab for the given page, if it isn't already closed.

        Parameters
        ----------
        page : Page
            The page instance to open. It must be owned by this 
            Notebook.

        """
        if page not in self.pages:
            msg = 'Page is not owned by this Notebook'
            raise ValueError(msg)
        content = {'widget_id': page.widget_id}
        self.send_action('close_tab', content)

