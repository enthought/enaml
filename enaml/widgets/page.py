#------------------------------------------------------------------------------
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from traits.api import Unicode, Bool, Str, Property, cached_property

from enaml.core.trait_types import EnamlEvent

from .container import Container
from .widget import Widget


class Page(Widget):
    """ A widget which can be used as a page in a Notebook control.

    A Page is a widget which can be used as a child of a Notebook
    control. It can have at most a single child widget which is an
    instance of Container.

    """
    #: The title to use for the page in the notebook.
    title = Unicode

    #: The source url for the icon to use for the page.
    icon_source = Str

    #: Whether or not this individual page is closable. Note that the
    #: 'tabs_closable' flag on the parent Notebook must be set to True
    #: for this to have any effect.
    closable = Bool(True)

    #: A read only property which returns the page's page widget.
    page_widget = Property(depends_on='children')

    #: An event fired when the user closes the page by clicking on
    #: the tab's close button. This event is fired by the parent
    #: Notebook when the tab is closed. This event has no payload.
    closed = EnamlEvent

    #--------------------------------------------------------------------------
    # Initialization
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the snapshot for the control.

        """
        snap = super(Page, self).snapshot()
        snap['title'] = self.title
        snap['closable'] = self.closable
        snap['icon_source'] = self.icon_source
        return snap

    def bind(self):
        """ Bind the change handlers for the control.

        """
        super(Page, self).bind()
        self.publish_attributes('title', 'closable', 'icon_source')

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    @cached_property
    def _get_page_widget(self):
        """ The getter for the 'page_widget' property.

        Returns
        -------
        result : Container or None
            The page widget for the Page, or None if not provided.

        """
        widget = None
        for child in self.children:
            if isinstance(child, Container):
                widget = child
        return widget

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_closed(self, content):
        """ Handle the 'closed' action from the client widget.

        """
        self.set_guarded(visible=False)
        self.closed()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def open(self):
        """ Open the page in the Notebook.

        Calling this method will also set the page visibility to True.

        """
        self.set_guarded(visible=True)
        self.send_action('open', {})

    def close(self):
        """ Close the page in the Notebook.

        Calling this method will set the page visibility to False.

        """
        self.set_guarded(visible=False)
        self.send_action('close', {})

