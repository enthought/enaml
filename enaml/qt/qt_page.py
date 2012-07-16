#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtCore import Signal
from .qt_container import QtContainer, QContainer


class QPage(QContainer):
    """ A QContainer subclass which acts as a page in a QNotebook.

    """
    #: A signal emitted when the tab title for this page changes.
    #: The payload is the page itself followed by the new title.
    tabTitleChanged = Signal(object, unicode)

    #: A signal emitted when the tab tool tip for this page changes.
    #: The payload is the page itself followed by the new tool tip.
    tabToolTipChanged = Signal(object, unicode)

    #: A signal emitted when the tab enabled state changes.
    #: The payload is the page itself followed by the new state.
    tabEnabledChanged = Signal(object, bool)

    #: A signal emitted when the closable state changes.
    #: The payload is the page itself followed by the new state.
    tabClosableChanged = Signal(object, bool)

    def __init__(self, *args, **kwargs):
        """ Initialize a QPage.

        Parameters
        ----------
        *args, **kwargs
            The position and keyword arguments required to initialize
            a QContainer.

        """
        super(QPage, self).__init__(*args, **kwargs)
        self._tab_title = u''
        self._tab_tool_tip = u''
        self._tab_enabled = True
        self._tab_closable = True
        self._enabled = self.isEnabled()

    def setEnabled(self, enabled):
        """ An overridden parent class method. 

        This stores a copy of the enabled flag. The parent QNotebook
        doesn't keep a separate flag for the tab enabled state (it just
        uses the flag on the child). So, it must be restored manually 
        when the tab enabled state is changed.

        """
        super(QPage, self).setEnabled(enabled)
        self._enabled = self.isEnabled()

    def restoreEnabled(self):
        """ A method called by the parent QNotebook.

        This method will restore the enabled state of the QPage to
        the previously set value. This is used to overcome the issue
        in QTabWidget, where a separate tab enabled flag is not kept,
        and enabled flag of a child is clobbered whenever the tab
        enabled state is changed.

        """
        self.setEnabled(self._enabled)

    def tabTitle(self):
        """ Returns the tab title for this page.

        Returns
        -------
        result : unicode
            The title string for the page's tab.

        """
        return self._tab_title

    def setTabTitle(self, title):
        """ Set the title for the tab for this page. This will emit the
        'tabTitleChanged' signal.

        Parameters
        ----------
        title : unicode
            The string to use for this page's tab title.

        """
        self._tab_title = title
        self.tabTitleChanged.emit(self, title)

    def tabToolTip(self):
        """ Returns the tool tip for the tab for this page.

        Returns
        -------
        result : unicode
            The tool tip string for the page's tab.

        """
        return self._tab_tool_tip

    def setTabToolTip(self, tool_tip):
        """ Set the tool tip for the tab for this page. This will emit
        the 'tabToolTipChanged' signal.

        Parameters
        ----------
        title : unicode
            The string to use for this page's tab tool tip.

        """
        self._tab_tool_tip = tool_tip
        self.tabToolTipChanged.emit(self, tool_tip)

    def tabEnabled(self):
        """ Return whether or no the tab for this page is enabled.

        Returns
        -------
        result : bool
            True if the tab for this page is enabled, False otherwise.

        """
        return self._tab_enabled

    def setTabEnabled(self, enabled):
        """ Set whether the tab for this page is enabled. This will 
        emit the 'tabEnabledChanged' signal.

        Parameters
        ----------
        enabled : bool
            True if the tab should be enabled, False otherwise.

        """
        self._tab_enabled = enabled
        self.tabEnabledChanged.emit(self, enabled)

    def tabClosable(self):
        """ Returns whether or not the tab for this page is closable.

        Returns
        -------
        result : bool
            True if this page's tab is closable, False otherwise.

        """
        return self._tab_closable

    def setTabClosable(self, closable):
        """ Set whether the tab for this page is closable. This will
        emit the 'tabClosableChanged' signal.

        Parameters
        ----------
        closable : bool
            True if the tab should be closable, False otherwise.

        """
        self._tab_closable = closable
        self.tabClosableChanged.emit(self, closable)


class QtPage(QtContainer):
    """ A Qt4 implementation of an Enaml notebook Page.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create(self):
        """ Create the underlying widget.

        """
        # The parent QtNotebook will come along and add the pages to
        # its notebook in a special way, hence we explicitly do not 
        # parent the QPage widget at this point.
        self.widget = QPage()

    def initialize(self, attrs):
        """ Initialize the attributes of the underlying control.

        """
        super(QtPage, self).initialize(attrs)
        self.set_title(attrs['title'])
        self.set_tool_tip(attrs['tool_tip'])
        self.set_tab_enabled(attrs['tab_enabled'])
        self.set_closable(attrs['closable'])

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

    def on_message_set_closable(self, payload):
        """ Handle the 'set-closable' action from the Enaml widget.

        """
        self.set_closable(payload['closable'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_title(self, title):
        """ Set the title of the tab for this page.

        """
        self.widget.setTabTitle(title)

    def set_closable(self, closable):
        """ Set whether or not this page is closable.

        """
        self.widget.setTabClosable(closable)

    def set_tool_tip(self, tool_tip):
        """ Set the tooltip of the tab for this page.

        """
        self.widget.setTabToolTip(tool_tip)

    def set_tab_enabled(self, enabled):
        """ Set the enabled state for the tab for this page.

        """
        self.widget.setTabEnabled(enabled)

    def set_visible(self, visible):
        """ Overriden method which disables the setting of visibility
        by the user code.

        The visibility of a page is controlled entirely by the parent
        QtNotebook.

        """
        pass

