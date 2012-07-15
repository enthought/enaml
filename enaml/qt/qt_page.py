#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt_container import QtContainer, QContainer


class QtPage(QtContainer):
    """ A Qt4 implementation of an Enaml notebook Page.

    """
    #: Internal storage for a copy of the page title. This is needed by
    #: the parent notebook when re-opening a closed tab.
    _title = u''

    #: Internal storage for a copy of the enabled flag. This is required
    #: for maintaining the enabled state of the page versus the enabled
    #: state of the tab. Qt doesn't keep separate flags for these, so
    #: we need to do it ourselves.
    _enabled = True

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Create the underlying widget.

        """
        # The widget is properly parented by call addTab on the parent
        # QTabWidget, as opposed to parenting the widget like normal.
        self.widget = QContainer()
        self.parent_widget.addTab(self.widget, self.get_title())

    def initialize(self, attrs):
        """ Initialize the attributes of the underlying control.

        """
        super(QtPage, self).initialize(attrs)
        self.set_title(attrs['title'])
        self.set_tool_tip(attrs['tool_tip'])
        self.set_tab_enabled(attrs['tab_enabled'])

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_message_set_title(self, payload):
        """ Handle the 'set-title' action from the Enaml widget.

        """
        self.set_title(payload['title'])

    def on_message_set_tool_tip(self, payload):
        """ Handle the 'set-tool_tip' action from the Enaml widget.

        """
        self.set_tool_tip(payload['tool_tip'])

    def on_message_set_tab_enabled(self, payload):
        """ Handle the 'set-tab_enabled' action from the Enaml widget.

        """
        self.set_tab_enabled(payload['tab_enabled'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def get_title(self):
        """ Return the title in use for this page.

        """
        return self._title

    def set_title(self, title):
        """ Set the title of the tab for this page.

        """
        op = lambda tabw, idx: tabw.setTabText(idx, title)
        self._tab_index_op(op)
        self._title = title

    def set_tool_tip(self, tool_tip):
        """ Set the tooltip of the tab for this page.

        """
        op = lambda tabw, idx: tabw.setTabToolTip(idx, tool_tip)
        self._tab_index_op(op)

    def set_tab_enabled(self, enabled):
        """ Set the enabled state for the tab for this page.

        """
        op = lambda tabw, idx: tabw.setTabEnabled(idx, enabled)
        self._tab_index_op(op)
        # Restore the current flag for the child, since the tab widget
        # doesn't store its own flag and overrides that of the page.
        self.set_enabled(self._enabled)

    def set_enabled(self, enabled):
        """ Overridden method which stores the enabled flag.

        The QTabWidget parent does not keep its own enabled flag for 
        each tab. It reuses that from the child widgets. This means
        enabling a disabled tab will re-enable the child page even 
        if it was previously disabled. Storing this flag allows us
        to restore the enabled state of the page, after changing the
        enabled state of the tab.

        """
        super(QtPage, self).set_enabled(enabled)
        self._enabled = enabled

    def set_visible(self, visible):
        """ Overriden method which disables the setting of visibility
        by the user code.

        The visibility of a page is controlled entirely by the parent
        Notebook.

        """
        pass

    #--------------------------------------------------------------------------
    # Private Api
    #--------------------------------------------------------------------------
    def _tab_index_op(self, op):
        """ Perform an operation on the parent notebook widget which
        requires the tab index.

        The callable will only be called the index of this page can
        be successfully determined.

        Parameters
        ----------
        op : callable
            A callable which accepts two arguments, the QTabWidget
            control, and the integer index of the tab representing
            this page.

        """
        widget = self.widget
        tab_widget = self.parent_widget
        idx = tab_widget.indexOf(widget)
        if idx != -1:
            op(tab_widget, idx)

