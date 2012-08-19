#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
from .qt.QtGui import QDockWidget
from .qt_widget_component import QtWidgetComponent


class QtDockPane(QtWidgetComponent):
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
        return QDockWidget(parent)

    def create(self, tree):
        """ Create and initialize the dock pane control.

        """
        super(QtDockPane, self).create(tree)
        self.set_dock_widget_id(tree['dock_widget_id'])
        self.set_title(tree['title'])
        self.set_title_bar_visible(tree['title_bar_visible'])
        self.set_title_bar_orientation(tree['title_bar_orientation'])
        self.set_closable(tree['closable'])
        self.set_movable(tree['movable'])
        self.set_floatable(tree['floatable'])
        self.set_floating(tree['floating'])
        self.set_dock_area(tree['dock_area'])
        self.set_allowed_dock_areas(tree['allowed_dock_areas'])
    
    def init_layout(self):
        """ Handle the layout initialization for the dock pane.

        """
        super(QtDockPane, self).init_layout()
        child = self.find_child(self._dock_widget_id)
        if child is not None:
            self.widget().setWidget(child.widget())

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_dock_pane_closed(self, event):
        """ The signal handler for the EVT_DOCK_PANE_CLOSED event.

        """
        #self.send_action('closed', {})

    def on_dock_pane_floated(self, event):
        """ The event handler for the EVT_DOCK_PANE_FLOATED event.

        """
        #self.send_action('floated', {})

    def on_dock_pane_docked(self, event):
        """ The event handler for the EVT_DOCK_PANE_AREA event.

        """
        #area = self.widget().GetDockArea()
        #content = {'dock_area': _DOCK_AREA_INV_MAP[area]}
        #self.send_action('docked', content)

    #--------------------------------------------------------------------------
    # Message Handling
    #-------------------------------------------------------------------------- 
    def on_action_set_title(self, content):
        """ Handle the 'set_title' action from the Enaml widget.

        """
        self.set_title(content['title'])

    def on_action_set_title_bar_visible(self, content):
        """ Handle the 'set_title_bar_visible' action from the Enaml
        widget.

        """
        self.set_title_bar_visible(content['title_bar_visible'])

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

    def on_action_open(self, content):
        """ Handle the 'open' action from the Enaml widget.

        """
        #self.widget().Open()

    def on_action_close(self, content):
        """ Handle the 'close' action from the Enaml widget.

        """
        #self.widget().Close()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_visible(self, visible):
        """ An overridden visibility setter which to opens|closes the
        dock pane.

        """
        pass

    def set_dock_widget_id(self, dock_widget_id):
        """ Set the dock widget id for the underlying widget.

        """
        self._dock_widget_id = dock_widget_id

    def set_title(self, title):
        """ Set the title on the underlying widget.

        """
        self.widget().setWindowTitle(title)

    def set_title_bar_visible(self, visible):
        """ Set the title bar visibility of the underlying widget.

        """
        #self.widget().SetTitleBarVisible(visible)

    def set_title_bar_orientation(self, orientation):
        """ Set the title bar orientation of the underyling widget.

        """
        #self.widget().SetTitleBarOrientation(_ORIENTATION_MAP[orientation])

    def set_closable(self, closable):
        """ Set the closable state on the underlying widget.

        """
        #self.widget().SetClosable(closable)

    def set_movable(self, movable):
        """ Set the movable state on the underlying widget.

        """
        #self.widget().SetMovable(movable)

    def set_floatable(self, floatable):
        """ Set the floatable state on the underlying widget.

        """
        #self.widget().SetFloatable(floatable)

    def set_floating(self, floating):
        """ Set the floating staet on the underlying widget.

        """
        #self.widget().SetFloating(floating)

    def set_dock_area(self, dock_area):
        """ Set the dock area on the underyling widget.

        """
        #self.widget().SetDockArea(_DOCK_AREA_MAP[dock_area])

    def set_allowed_dock_areas(self, dock_areas):
        """ Set the allowed dock areas on the underlying widget.

        """
        #wx_areas = 0
        #for area in dock_areas:
        #    wx_areas |= _ALLOWED_AREAS_MAP[area]
        #self.widget().SetAllowedDockAreas(wx_areas)

