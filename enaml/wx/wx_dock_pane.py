#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
import wx
import wx.aui
import wx.lib.newevent

from .wx_main_window import wxMainWindow
from .wx_single_widget_sizer import wxSingleWidgetSizer
from .wx_widget_component import WxWidgetComponent


#: A mapping from Enaml dock areas to wx aui dock area enums
_DOCK_AREA_MAP = {
    'top': wx.aui.AUI_DOCK_TOP,
    'right': wx.aui.AUI_DOCK_RIGHT,
    'bottom': wx.aui.AUI_DOCK_BOTTOM,
    'left': wx.aui.AUI_DOCK_LEFT,
}

#: A mapping from wx aui dock area enums to Enaml dock areas.
_DOCK_AREA_INV_MAP = dict((v, k) for (k, v) in _DOCK_AREA_MAP.iteritems())

#: A mapping from Enaml allowed dock areas to wx direction enums.
_ALLOWED_AREAS_MAP = {
    'top': wx.TOP,
    'right': wx.RIGHT,
    'bottom': wx.BOTTOM,
    'left': wx.LEFT,
    'all': wx.ALL,
}


#: An event emitted when the floating state of a dock pane changes
#: due to user interaction.
wxDockPaneFloatEvent, EVT_DOCK_PANE_FLOAT = wx.lib.newevent.NewEvent()

#: An event emitted when the dock area of a dock pane changes due
#: to user interaction.
wxDockPaneAreaEvent, EVT_DOCK_PANE_AREA = wx.lib.newevent.NewEvent()


class wxDockPane(wx.Panel):
    """ A subclass of wx.Panel which adds DockPane features.

    """
    def __init__(self, parent, *args, **kwargs):
        """ Initialize a wxDockPane.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a wxPanel.

        """
        super(wxDockPane, self).__init__(parent, *args, **kwargs)
        self._title = u''
        self._closable = True
        self._floatable = True
        self._floating = False
        self._dock_area = wx.aui.AUI_DOCK_LEFT
        self._allowed_dock_areas = wx.ALL
        self._dock_widget = None
        self.SetSizer(wxSingleWidgetSizer())

        # Wx does not provide events to know when the user has changed
        # the floating state or dock position of a dock pane. So, we
        # to craft a horrible hack on the show-event and testing 
        # whether or not our parent has changed.
        self._curr_parent = parent
        self.Bind(wx.EVT_SHOW, self._OnShow)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _FindPaneManager(self):
        """ Find the pane manager for this dock pane.

        Returns
        -------
        result : AuiManager or None
            The AuiManager for this dock pane, or None if not found.

        """
        parent = self.GetParent()
        if isinstance(parent, wxMainWindow):
            return parent.GetPaneManager()
        if isinstance(parent, wx.aui.AuiFloatingFrame):
            return parent.GetOwnerManager()

    def _PaneInfoOperation(self, closure):
        """ A private method which will run the given closure if there 
        is a valid pane info object for this dock pane.

        """
        manager = self._FindPaneManager()
        if manager is not None:
            pane = manager.GetPane(self)
            if pane.IsOk():
                closure(pane)
                manager.Update()

    def _OnShow(self, event):
        """ An event handler for the EVT_SHOW event. 

        This is an attempt to workaround the issue that Wx does not
        provide any events when the user manually floats or changes 
        the position of a dock pane.

        """
        # A change in floating state or dock area is accompanied by a
        # change in the parent of the dock pane. But we don't get events
        # for that in wx either, so... We use the show-event which is
        # triggered when a dock pane changes its floating state. However, 
        # that event is emitted twice per state change, so we manually 
        # check for the parent change (which happens once) and then
        # proceed with our manual checking of state change.
        #
        # I can't believe I actually have to do this...
        event.Skip()
        parent = self.GetParent()
        if parent != self._curr_parent:
            self._curr_parent = parent
            manager = self._FindPaneManager()
            if manager is not None:
                pane = manager.GetPane(self)
                if pane.IsOk():
                    is_floating = pane.IsFloating()
                    if is_floating != self._floating:
                        self._floating = is_floating
                        evt = wxDockPaneFloatEvent(IsFloating=is_floating)
                        wx.PostEvent(self, evt)
                    if not is_floating:
                        area = pane.dock_direction
                        if area != self._dock_area:
                            self._dock_area = area
                            evt = wxDockPaneAreaEvent(DockArea=area)
                            wx.PostEvent(self, evt)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def MakePaneInfo(self):
        """ Create a new AuiPaneInfo object for this dock pane.

        This is called by the wxMainWindow when it adds this dock pane
        for the first time.
        
        Returns
        -------
        result : AuiPaneInfo
            An AuiPaneInfo object for this page.

        """
        info = wx.aui.AuiPaneInfo()

        info.BestSize(self.GetBestSize())
        info.MinSize(self.GetEffectiveMinSize())
        info.Caption(self.GetTitle())
        info.Floatable(self.GetFloatable())
        info.Direction(self.GetDockArea())

        areas = self.GetAllowedDockAreas()
        info.TopDockable(bool(areas & wx.TOP))
        info.RightDockable(bool(areas & wx.RIGHT))
        info.LeftDockable(bool(areas & wx.LEFT))
        info.BottomDockable(bool(areas & wx.BOTTOM))
        
        if self.GetFloating():
            info.Float()
        else:
            info.Dock()

        return info

    def GetDockWidget(self):
        """ Get the dock widget being managed by this pane.

        Returns
        -------
        result : wxWindow or None
            The wx widget being managed by this dock pane, or None
            if no widget is being managed.

        """
        return self._dock_widget

    def SetDockWidget(self, widget):
        """ Set the dock widget to be managed by the pane.

        Any old dock widget will be removed, but not destroyed.

        Parameters
        ----------
        widget : wxWindow
            The wx widget to use as the dock widget for this pane.

        """
        self._dock_widget = widget
        self.GetSizer().Add(widget)

    def GetTitle(self):
        """ Get the title for the dock pane.

        Returns
        -------
        result : unicode
            The title of the dock pane.

        """
        return self._title

    def SetTitle(self, title):
        """ Set the title for the dock pane.

        Parameters
        ----------
        title : unicode
            The title to use for the dock pane.

        """
        if self._title != title:
            self._title = title
            def closure(pane):
                if pane.frame:
                    pane.frame.SetTitle(title)
                pane.Caption(title)
            self._PaneInfoOperation(closure)

    def GetClosable(self):
        """ Get the closable state of the pane.

        Returns
        -------
        result : bool
            Whether or not the pane is closable.

        """
        return self._closable

    def SetClosable(self, closable):
        """ Set the closable state of the pane.

        Parameters
        ----------
        closable : bool
            Whether or not the pane is closable.

        """
        # Setting the CloseButton flag on the pane info object is not
        # reliable. So we always show the button, and the main window
        # handles veto'ing the close event if the pane is not closable.
        self._closable = closable

    def GetFloatable(self):
        """ Get the floatable state of the pane.

        Returns
        -------
        result : bool
            Whether or not the pane is floatable.

        """
        return self._floatable

    def SetFloatable(self, floatable):
        """ Set the floatable state of the pane.

        Parameters
        ----------
        floatable : bool
            Whether or not the pane is floatable.

        """
        if self._floatable != floatable:
            self._floatable = floatable
            def closure(pane):
                pane.Floatable(floatable)
            self._PaneInfoOperation(closure)

    def GetFloating(self):
        """ Get the floating state of the pane.

        Returns
        -------
        result : bool
            Whether or not the pane is floating.

        """
        return self._floating

    def SetFloating(self, floating):
        """ Set the floating state of the pane.

        Parameters
        ----------
        floating : bool
            Whether or not the pane should be floating.

        """
        if self._floating != floating:
            self._floating = floating
            def closure(pane):
                if floating:
                    pane.Float()
                else:
                    pane.Dock()
            self._PaneInfoOperation(closure)

    def GetDockArea(self):
        """ Get the current dock area of the pane.

        Returns
        -------
        result : int
            The current dock area of the pane. One of the wx enums 
            LEFT, RIGHT, TOP, or BOTTOM.

        """
        return self._dock_area

    def SetDockArea(self, dock_area):
        """ Set the dock area for the pane.

        Parameters
        ----------
        dock_area : int
            The dock area for the pane. One of the wx enums LEFT, 
            RIGHT, TOP, or BOTTOM.

        """
        if self._dock_area != dock_area:
            self._dock_area = dock_area
            def closure(pane):
                pane.Direction(dock_area)
            self._PaneInfoOperation(closure)

    def GetAllowedDockAreas(self):
        """ Get the allowed dock areas for the pane.

        Returns
        -------
        result : int
            The allowed dock areas for the pane. One of the wx enums
            LEFT, RIGHT, TOP, BOTTOM, or ALL.

        """
        return self._allowed_dock_areas

    def SetAllowedDockAreas(self, dock_areas):
        """ Set the allowed dock areas for the pane.

        Parameters
        ----------
        dock_areas : int
            The allowed dock areas for the pane. One of the wx enums
            LEFT, RIGHT, TOP, BOTTOM, or ALL.

        """
        if self._allowed_dock_areas != dock_areas:
            self._allowed_dock_areas = dock_areas
            def closure(pane):
                pane.TopDockable(bool(dock_areas & wx.TOP))
                pane.RightDockable(bool(dock_areas & wx.RIGHT))
                pane.LeftDockable(bool(dock_areas & wx.LEFT))
                pane.BottomDockable(bool(dock_areas & wx.BOTTOM))
            self._PaneInfoOperation(closure)


class WxDockPane(WxWidgetComponent):
    """ A Wx implementation of an Enaml DockPane.

    """
    #: Storage for the dock widget id
    _dock_widget_id = None

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying wxDockPane widget.

        """
        return wxDockPane(parent)

    def create(self, tree):
        """ Create and initialize the dock pane control.

        """
        super(WxDockPane, self).create(tree)
        self.set_dock_widget_id(tree['dock_widget_id'])
        self.set_title(tree['title'])
        self.set_title_bar_orientation(tree['title_bar_orientation'])
        self.set_closable(tree['closable'])
        self.set_movable(tree['movable'])
        self.set_floatable(tree['floatable'])
        self.set_floating(tree['floating'])
        self.set_dock_area(tree['dock_area'])
        self.set_allowed_dock_areas(tree['allowed_dock_areas'])
        widget = self.widget()
        widget.Bind(EVT_DOCK_PANE_FLOAT, self.on_dock_pane_float)
        widget.Bind(EVT_DOCK_PANE_AREA, self.on_dock_pane_area)

    def init_layout(self):
        """ Handle the layout initialization for the dock pane.

        """
        super(WxDockPane, self).init_layout()
        child = self.find_child(self._dock_widget_id)
        if child is not None:
            self.widget().SetDockWidget(child.widget())

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_dock_pane_float(self, event):
        """ The event handler for the EVT_DOCK_PANE_FLOAT event.

        """
        content = {'floating': event.IsFloating}
        self.send_action('floating_changed', content)

    def on_dock_pane_area(self, event):
        """ The event handler for the EVT_DOCK_PANE_AREA event.

        """
        content = {'dock_area': _DOCK_AREA_INV_MAP[event.DockArea]}
        self.send_action('dock_area_changed', content)

    #--------------------------------------------------------------------------
    # Message Handling
    #-------------------------------------------------------------------------- 
    def on_action_set_title(self, content):
        """ Handle the 'set_title' action from the Enaml widget.

        """
        self.set_title(content['title'])

    def on_action_set_title_bar_orientation(self, content):
        """ Handle the 'set_title_bar_orientation' action from the
        Enaml widget.

        """
        self.set_title_bar_orientation(content['title_bar_orientation'])

    def on_action_set_closable(self, content):
        """ Handle the 'set_closable' action from the Enaml widget.

        """
        self.set_closable(content['closable'])

    def on_action_set_movable(self, content):
        """ Handle the 'set_movable' action from the Enaml widget.

        """
        self.set_movable(content['movable'])

    def on_action_set_floatable(self, content):
        """ Handle the 'set_floatable' action from the Enaml widget.

        """
        self.set_floatable(content['floatable'])

    def on_action_set_floating(self, content):
        """ Handle the 'set_floating' action from the Enaml widget.

        """
        self.set_floating(content['floating'])

    def on_action_set_dock_area(self, content):
        """ Handle the 'set_dock_area' action from the Enaml widget.

        """
        self.set_dock_area(content['dock_area'])

    def on_action_set_allowed_dock_areas(self, content):
        """ Handle the 'set_allowed_dock_areas' action from the Enaml
        widget.

        """
        self.set_allowed_dock_areas(content['allowed_dock_areas'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_dock_widget_id(self, dock_widget_id):
        """ Set the dock widget id for the underlying widget.

        """
        self._dock_widget_id = dock_widget_id

    def set_title(self, title):
        """ Set the title on the underlying widget.

        """
        self.widget().SetTitle(title)

    def set_title_bar_orientation(self, orientation):
        """ Set the title bar orientation of the underyling widget.

        Wx does not support a title bar orientation in dock panes, so 
        this setting is simply ignored.

        """
        pass

    def set_closable(self, closable):
        """ Set the closable state on the underlying widget.

        """
        self.widget().SetClosable(closable)

    def set_movable(self, movable):
        """ Set the movable state on the underlying widget.

        """
        # XXX Setting movable has no effect. Glancing through the wx
        # C++ code indicates that movable flag on a pane info object
        # is never used. This appears to be dead or not implemented 
        # functionality, so it's just ignored for now.
        pass

    def set_floatable(self, floatable):
        """ Set the floatable state on the underlying widget.

        """
        self.widget().SetFloatable(floatable)

    def set_floating(self, floating):
        """ Set the floating staet on the underlying widget.

        """
        self.widget().SetFloating(floating)

    def set_dock_area(self, dock_area):
        """ Set the dock area on the underyling widget.

        """
        self.widget().SetDockArea(_DOCK_AREA_MAP[dock_area])

    def set_allowed_dock_areas(self, dock_areas):
        """ Set the allowed dock areas on the underlying widget.

        """
        wx_areas = 0
        for area in dock_areas:
            wx_areas |= _ALLOWED_AREAS_MAP[area]
        self.widget().SetAllowedDockAreas(wx_areas)

